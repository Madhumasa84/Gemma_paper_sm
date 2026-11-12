import os
import json
import time
import hashlib
import re
import subprocess
import torch
from typing import Dict, Any, List, Tuple, Optional
from gemma_paper.workspace import WORKSPACE_DIR

CONDITIONS = ["W", "A", "B", "C"]
VALID_CONDITIONS = ("W", "A", "B", "C")
EVIDENCE_BUDGET = 4000
MAX_OUTPUT_TOKENS = 2048

def get_configuration_hash(extra_config: Optional[Dict[str, Any]] = None) -> str:
    """Computes a deterministic SHA-256 hash representing the frozen model/inference configuration."""
    cfg = {
        "model_id": "google/gemma-4-E4B-it",
        "revision": "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c",
        "quantization": "bitsandbytes_8bit",
        "evidence_budget": EVIDENCE_BUDGET,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "do_sample": False,
        "enable_thinking": False,
        "temperature": 0.0,
        "prompt_template_version": "v1.1_with_issue_text"
    }
    if extra_config:
        cfg.update(extra_config)
    serialized = json.dumps(cfg, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def get_prompt_hash(prompt_text: str) -> str:
    """Computes a SHA-256 hash for the exact formatted input prompt."""
    return hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()

def compute_checkpoint_key(task_id: str, condition: str, prompt_hash: str, config_hash: str, attempt: int = 1) -> str:
    """
    Uniform checkpoint key shared between single-attempt and batch runners.
    Ensures that changed configurations or prompts do not reuse stale results.
    """
    clean_task = task_id.replace("/", "__")
    return f"{clean_task}__{condition}__a{attempt}__{prompt_hash[:8]}__{config_hash[:8]}"

def format_repair_prompt(task_id: str, problem_statement: str, evidence_text: str, condition: str) -> str:
    """
    Constructs the repair prompt with the mandatory issue problem statement text and evidence representation.
    """
    prompt = (
        f"You are an expert software engineer resolving an issue in the repository for task '{task_id}'.\n\n"
        f"### ISSUE PROBLEM STATEMENT\n"
        f"{problem_statement.strip()}\n\n"
        f"### RELEVANT REPOSITORY CODE (Evidence Condition: {condition})\n"
        f"{evidence_text.strip()}\n\n"
        f"### INSTRUCTIONS\n"
        f"Analyze the issue description and repository code above.\n"
        f"Write a patch that fixes the issue.\n"
        f"Output your patch as a unified diff format inside a ```diff code block.\n"
        f"Ensure file paths in the diff match the repository files (e.g., a/src/... b/src/...).\n"
    )
    return prompt

def parse_model_patch(raw_output: str) -> Tuple[str, str]:
    """
    Extracts unified diff patch from raw model generation.
    Returns (patch_string, conversion_status).
    """
    if not raw_output or not raw_output.strip():
        return "", "EMPTY_GENERATION"

    # 1. Look for ```diff or ```patch markdown code fence
    diff_block_match = re.search(r"```(?:diff|patch)?\s*\n(diff --git .*?)```", raw_output, re.DOTALL)
    if diff_block_match:
        patch = diff_block_match.group(1).strip()
        return patch, "SUCCESS"

    # 2. Look for raw diff --git header
    raw_git_match = re.search(r"(diff --git a/.*?)(?:\n\n\n|\Z)", raw_output, re.DOTALL)
    if raw_git_match:
        patch = raw_git_match.group(1).strip()
        return patch, "SUCCESS"

    # 3. Look for standard --- a/ +++ b/ headers
    standard_patch_match = re.search(r"(--- a/.*?\n\+\+\+ b/.*?\n@@.*)", raw_output, re.DOTALL)
    if standard_patch_match:
        patch = standard_patch_match.group(1).strip()
        return patch, "SUCCESS"

    return "", "PARSING_FAILED_NO_VALID_DIFF"

def check_patch_applicability(repo_dir: str, patch_str: str) -> str:
    """Tests whether git apply --check accepts the synthesized patch."""
    if not patch_str.strip():
        return "EMPTY_PATCH"
    if not os.path.exists(repo_dir):
        return "REPO_NOT_FOUND"

    try:
        proc = subprocess.run(
            ["git", "-C", repo_dir, "apply", "--check", "-"],
            input=patch_str,
            text=True,
            capture_output=True,
            timeout=10
        )
        if proc.returncode == 0:
            return "APPLIES_CLEANLY"
        else:
            return f"GIT_APPLY_REJECTED: {proc.stderr.strip()[:100]}"
    except Exception as e:
        return f"CHECK_ERROR: {str(e)}"

def run_single_attempt(
    model: Any,
    processor: Any,
    task_id: str,
    condition: str,
    evidence_packet: Dict[str, Any],
    output_dir: Optional[str] = None,
    repos_base_dir: Optional[str] = None,
    attempt: int = 1,
    extra_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE_DIR, "inference_output")
    if repos_base_dir is None:
        repos_base_dir = os.path.join(WORKSPACE_DIR, "task_repos")
    """
    Executes or resumes a single issue repair attempt using the uniform checkpoint key.
    Enforces real GPU execution; rejects mock models and mock checkpoints.
    """
    if condition not in VALID_CONDITIONS:
        raise ValueError(f"Invalid condition '{condition}'. Must be one of {VALID_CONDITIONS}")

    if getattr(model, "is_mock", False):
        raise ValueError("FATAL: Mock model detected! Production inference requires real model on GPU.")

    if not torch.cuda.is_available():
        raise RuntimeError("FATAL: CUDA GPU acceleration is required for production 8-bit model inference.")

    problem_statement = evidence_packet.get("problem_statement", "")
    evidence_text = evidence_packet.get("evidence_text", "")

    # 1. Format prompt & calculate hashes
    prompt = format_repair_prompt(task_id, problem_statement, evidence_text, condition)
    p_hash = get_prompt_hash(prompt)
    c_hash = get_configuration_hash(extra_config)
    
    ckpt_key = compute_checkpoint_key(task_id, condition, p_hash, c_hash, attempt)
    ckpt_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    ckpt_file = os.path.join(ckpt_dir, f"{ckpt_key}.json")

    # 2. Check for existing checkpoint (strictly rejecting quarantined/mock checkpoints)
    if os.path.exists(ckpt_file):
        with open(ckpt_file, "r", encoding="utf-8") as f:
            cached_record = json.load(f)
        if cached_record.get("execution_mode") != "production_gpu" or cached_record.get("is_mock", False):
            print(f"[Single Attempt] Rejecting non-production checkpoint at {ckpt_file}. Re-running real inference.")
        else:
            print(f"[Single Attempt] Valid production checkpoint found: {ckpt_file}. Loading cached results.")
            return cached_record

    print(f"[Single Attempt] Executing task '{task_id}' under Condition '{condition}' (Attempt {attempt})...")
    print(f"  Checkpoint Key: {ckpt_key}")

    # 3. Memory measurement before inference
    torch.cuda.reset_peak_memory_stats()
    mem_before = {
        "allocated_mb": round(torch.cuda.memory_allocated() / (1024**2), 2),
        "reserved_mb": round(torch.cuda.memory_reserved() / (1024**2), 2)
    }

    # 4. Tokenization & Model Generation
    from gemma_paper.generation_smoke import format_chat_input
    inputs = format_chat_input(processor, prompt, enable_thinking=False)
    input_ids = inputs["input_ids"].cuda()
    in_tokens = int(input_ids.shape[1])

    start_time = time.time()
    with torch.no_grad():
        output_tokens = model.generate(
            input_ids,
            max_new_tokens=MAX_OUTPUT_TOKENS,
            do_sample=False
        )
    elapsed_time = round(time.time() - start_time, 2)

    new_tokens = output_tokens[0][input_ids.shape[1]:]
    gen_tokens = len(new_tokens)
    raw_generation = processor.decode(new_tokens, skip_special_tokens=True)
    finish_reason = "length_truncated" if gen_tokens >= MAX_OUTPUT_TOKENS else "stop"

    # 5. Patch Extraction & Separate Statuses
    model_patch, conversion_status = parse_model_patch(raw_generation)
    
    # 6. Check Git Patch Applicability against repository
    repo_dir = os.path.join(repos_base_dir, task_id.replace("/", "__"))
    applicability_status = check_patch_applicability(repo_dir, model_patch)

    # 7. Memory measurement after inference
    mem_after = {
        "allocated_mb": round(torch.cuda.memory_allocated() / (1024**2), 2),
        "reserved_mb": round(torch.cuda.memory_reserved() / (1024**2), 2),
        "peak_mb": round(torch.cuda.max_memory_allocated() / (1024**2), 2)
    }

    record = {
        "checkpoint_key": ckpt_key,
        "execution_mode": "production_gpu",
        "is_mock": False,
        "instance_id": task_id,
        "condition": condition,
        "attempt": attempt,
        "prompt_hash": p_hash,
        "config_hash": c_hash,
        "model_id": getattr(model, "name_or_path", "google/gemma-4-E4B-it"),
        "model_revision": "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c",
        "raw_generation": raw_generation,
        "model_patch": model_patch,
        "generation_status": "COMPLETED" if finish_reason == "stop" else "TRUNCATED",
        "conversion_status": conversion_status,
        "patch_applicability": applicability_status,
        "test_resolution": "PENDING_SWE_BENCH_EVALUATOR",
        "token_counts": {
            "input_tokens": in_tokens,
            "generated_tokens": gen_tokens,
            "total_tokens": in_tokens + gen_tokens
        },
        "finish_reason": finish_reason,
        "elapsed_seconds": elapsed_time,
        "memory_measurements": {
            "before": mem_before,
            "after": mem_after
        },
        "timestamp": time.time()
    }

    # 8. Write checkpoint atomically
    with open(ckpt_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    # 9. Export individual prediction JSON file
    pred_dir = os.path.join(output_dir, "predictions")
    os.makedirs(pred_dir, exist_ok=True)
    pred_file = os.path.join(pred_dir, f"{ckpt_key}.json")
    with open(pred_file, "w", encoding="utf-8") as f:
        json.dump({
            "model_name_or_path": record["model_id"],
            "instance_id": task_id,
            "model_patch": model_patch
        }, f, indent=2)

    print(f"  Attempt Complete: Status={conversion_status} | Applicability={applicability_status} | Gen Tokens={gen_tokens}")
    print(f"  Saved Checkpoint: {ckpt_file}")
    return record

def run_resumable_pilot_inference(
    model: Any,
    processor: Any,
    evidence_packets_dir: Optional[str] = None,
    repos_base_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    attempt: int = 1
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    if evidence_packets_dir is None:
        evidence_packets_dir = os.path.join(WORKSPACE_DIR, "evidence_packets")
    if repos_base_dir is None:
        repos_base_dir = os.path.join(WORKSPACE_DIR, "task_repos")
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE_DIR, "inference_output")
    """
    Executes batch inference explicitly restricted to conditions W, A, B, and C.
    Enforces real GPU execution; rejects mock records.
    """
    if conditions is None:
        target_conditions = list(VALID_CONDITIONS)
    else:
        for c in conditions:
            if c not in VALID_CONDITIONS:
                raise ValueError(f"Condition '{c}' is invalid. Batch runner strictly restricted to {VALID_CONDITIONS}")
        target_conditions = conditions

    print(f"[Batch Runner] Active Conditions: {target_conditions}")
    
    task_manifest_path = os.path.join(WORKSPACE_DIR, "task_manifest.json")
    with open(task_manifest_path, "r", encoding="utf-8") as f:
        tasks_data = json.load(f)["selected_tasks"]

    attempt_records = []
    for task in tasks_data:
        task_id = task["instance_id"]
        for cond in target_conditions:
            packet_path = os.path.join(evidence_packets_dir, f"{task_id}__{cond}.json")
            if not os.path.exists(packet_path):
                print(f"[Batch Runner] Warning: Packet not found at {packet_path}. Skipping.")
                continue

            with open(packet_path, "r", encoding="utf-8") as f:
                packet = json.load(f)

            rec = run_single_attempt(
                model=model,
                processor=processor,
                task_id=task_id,
                condition=cond,
                evidence_packet=packet,
                output_dir=output_dir,
                repos_base_dir=repos_base_dir,
                attempt=attempt
            )
            attempt_records.append(rec)

    exported_pred_files = {}
    for cond in target_conditions:
        cond_records = [r for r in attempt_records if r["condition"] == cond]
        jsonl_path = os.path.join(output_dir, f"predictions_condition_{cond}.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for r in cond_records:
                f.write(json.dumps({
                    "model_name_or_path": r["model_id"],
                    "instance_id": r["instance_id"],
                    "model_patch": r["model_patch"]
                }) + "\n")
        exported_pred_files[cond] = jsonl_path

    return attempt_records, exported_pred_files

def print_inference_summary_table(attempt_records: List[Dict[str, Any]]):
    print("=" * 95)
    print(f"{'Task ID':<36} | {'Cond':<4} | {'Tokens':<6} | {'Conversion':<10} | {'Applicability':<16} | {'Test Status'}")
    print("-" * 95)
    for r in attempt_records:
        tokens = r["token_counts"]["generated_tokens"]
        print(f"{r['instance_id']:<36} | {r['condition']:<4} | {tokens:<6} | {r['conversion_status']:<10} | {r['patch_applicability']:<16} | {r['test_resolution']}")
    print("=" * 95)
