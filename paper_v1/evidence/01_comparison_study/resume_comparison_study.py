#!/usr/bin/env python3
"""
Gemma 4 Code Evidence Representation Study - Resumption Script
Restores frozen environment and resumes only unfinished pairs (1 interrupted + 17 unstarted).
Reuses 22 verified completed checkpoints without re-generating.
"""

import os, sys, json, time, re, hashlib, subprocess, shutil
from pathlib import Path
import torch

WORKSPACE = Path("/content/comparison_study")
DRIVE_WORKSPACE = Path("/content/drive/MyDrive/gemma_paper/comparison_study")

CHECKPOINT_DIR = WORKSPACE / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_CHECKPOINT_DIR = DRIVE_WORKSPACE / "checkpoints"
DRIVE_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

PRED_DIR = WORKSPACE / "predictions"
PRED_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_PRED_DIR = DRIVE_WORKSPACE / "predictions"
DRIVE_PRED_DIR.mkdir(parents=True, exist_ok=True)

RAW_DIR = WORKSPACE / "raw_outputs"
RAW_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_RAW_DIR = DRIVE_WORKSPACE / "raw_outputs"
DRIVE_RAW_DIR.mkdir(parents=True, exist_ok=True)

PATCH_DIR = WORKSPACE / "extracted_patches"
PATCH_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_PATCH_DIR = DRIVE_WORKSPACE / "extracted_patches"
DRIVE_PATCH_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ID = "google/gemma-4-E4B-it"
REVISION = "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"

def extract_patch(raw_text: str) -> str:
    blocks = re.findall(r"```diff\s*\n(.*?)\n```", raw_text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```patch\s*\n(.*?)\n```", raw_text, re.DOTALL)
    if not blocks:
        return ""
    patch = blocks[-1]
    if not patch.endswith("\n"):
        patch += "\n"
    return patch

def test_and_apply_patch(repo_dir: Path, patch_text: str) -> dict:
    if not patch_text.strip():
        return {
            "strict_applicable": False,
            "recount_applicable": False,
            "canonical_patch": "",
            "apply_error": "No patch block found"
        }
    
    if not repo_dir.exists():
        return {
            "strict_applicable": False,
            "recount_applicable": False,
            "canonical_patch": "",
            "apply_error": f"Repo dir {repo_dir} does not exist"
        }
    
    subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
    
    patch_file = repo_dir / "_temp_model_patch.diff"
    patch_file.write_text(patch_text, encoding="utf-8")
    
    strict_res = subprocess.run(["git", "apply", "--check", str(patch_file)], cwd=repo_dir, capture_output=True, text=True)
    strict_applicable = (strict_res.returncode == 0)
    
    recount_res = subprocess.run(["git", "apply", "--recount", "--check", str(patch_file)], cwd=repo_dir, capture_output=True, text=True)
    recount_applicable = (recount_res.returncode == 0)
    
    canonical_patch = ""
    apply_error = ""
    if recount_applicable:
        apply_res = subprocess.run(["git", "apply", "--recount", str(patch_file)], cwd=repo_dir, capture_output=True, text=True)
        if apply_res.returncode == 0:
            canonical_patch = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True).stdout
        else:
            apply_error = apply_res.stderr.strip()
    else:
        apply_error = recount_res.stderr.strip() or strict_res.stderr.strip()
        
    if patch_file.exists():
        patch_file.unlink()
    subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
    
    return {
        "strict_applicable": strict_applicable,
        "recount_applicable": recount_applicable,
        "canonical_patch": canonical_patch,
        "apply_error": apply_error
    }

def export_summary_tables(results):
    import pandas as pd
    rows = []
    for r in results:
        rows.append({
            "instance_id": r["instance_id"],
            "condition": r["condition"],
            "evidence_tokens": r.get("evidence_tokens", 0),
            "input_tokens": r.get("input_tokens", 0),
            "generated_tokens": r.get("generated_tokens", 0),
            "finish_reason": r.get("finish_reason", ""),
            "elapsed_seconds": round(r.get("elapsed_seconds", 0), 2),
            "strict_applicable": r.get("strict_applicable", False),
            "recount_applicable": r.get("recount_applicable", False),
            "test_resolution": r.get("test_resolution", "PENDING_DOCKER_EXECUTION")
        })
    df = pd.DataFrame(rows)
    df.to_csv(WORKSPACE / "results.csv", index=False)
    df.to_csv(DRIVE_WORKSPACE / "results.csv", index=False)
    (WORKSPACE / "results.json").write_text(json.dumps(results, indent=2))
    (DRIVE_WORKSPACE / "results.json").write_text(json.dumps(results, indent=2))

def resume_generation():
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required to resume model generation. No CPU fallback permitted.")
    
    from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig, GenerationConfig
    
    print("=" * 70)
    print("INITIALIZING FROZEN MODEL AND TOKENIZER")
    print("=" * 70)
    print(f"Model ID: {MODEL_ID}")
    print(f"Revision: {REVISION}")
    print("Quantization: bitsandbytes 8-bit")
    
    bnb_config = BitsAndBytesConfig(load_in_8bit=True)
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=REVISION)
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16
    )
    model.eval()
    
    effective_config = GenerationConfig(
        max_new_tokens=2048,
        do_sample=False,
        num_beams=1,
        pad_token_id=processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id,
        eos_token_id=processor.tokenizer.eos_token_id
    )
    
    packets_dir = WORKSPACE / "evidence_packets"
    packet_files = sorted(packets_dir.glob("*__*__packet.json"))
    repos_dir = WORKSPACE / "task_repos"
    
    print(f"\nTotal planned packets: {len(packet_files)}")
    results = []
    
    for idx, pkt_path in enumerate(packet_files, 1):
        with open(pkt_path) as f:
            packet = json.load(f)
            
        iid = packet["instance_id"]
        cond = packet["condition"]
        checkpoint_key = f"{iid}__{cond}"
        ckpt_file = CHECKPOINT_DIR / f"{checkpoint_key}__checkpoint.json"
        drive_ckpt_file = DRIVE_CHECKPOINT_DIR / f"{checkpoint_key}__checkpoint.json"
        
        # Verify if completed checkpoint already exists
        cached_source = None
        if ckpt_file.exists():
            cached_source = ckpt_file
        elif drive_ckpt_file.exists():
            cached_source = drive_ckpt_file
            shutil.copy2(drive_ckpt_file, ckpt_file)
            
        if cached_source:
            try:
                with open(cached_source) as f:
                    cached = json.load(f)
                expected_sha = hashlib.sha256(packet["prompt_text"].encode()).hexdigest()
                if (cached.get("prompt_sha256") == expected_sha and 
                    cached.get("revision") == REVISION and
                    cached.get("model_id") == MODEL_ID):
                    print(f"[{idx:2d}/{len(packet_files)}] [REUSED] {checkpoint_key} (tokens: {cached.get('generated_tokens')}, recount: {cached.get('recount_applicable')})")
                    results.append(cached)
                    continue
                else:
                    print(f"[{idx:2d}/{len(packet_files)}] Checkpoint hash mismatch for {checkpoint_key}; re-running.")
            except Exception as e:
                print(f"[{idx:2d}/{len(packet_files)}] Checkpoint read error for {checkpoint_key}: {e}; re-running.")
                
        # Interrupted vs Fresh logging
        if checkpoint_key == "pydicom__pydicom-1413__C":
            print(f"\n>>> [{idx:2d}/{len(packet_files)}] [RESUMING INTERRUPTED PAIR] {checkpoint_key} (Condition: {cond}, Evidence tok: {packet['evidence_tokens']}) <<<")
        else:
            print(f"\n[{idx:2d}/{len(packet_files)}] [GENERATING FRESH PAIR] {checkpoint_key} (Condition: {cond}, Evidence tok: {packet['evidence_tokens']})...")
            
        rendered = packet["rendered_prompt"]
        processor_kwargs = {"add_special_tokens": False, "return_tensors": "pt", "return_attention_mask": True, "return_mm_token_type_ids": True}
        inputs = dict(processor(text=[rendered], **processor_kwargs))
        
        input_device = model.get_input_embeddings().weight.device
        generation_inputs = {k: v.to(input_device) for k, v in inputs.items()}
        prefix_len = generation_inputs["input_ids"].shape[1]
        
        torch.cuda.synchronize()
        start_time = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **generation_inputs,
                generation_config=effective_config,
                return_dict_in_generate=True,
                output_scores=False
            )
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start_time
        mem_after = torch.cuda.memory_allocated()
        
        sequences = generated.sequences.detach().cpu()
        new_ids = sequences[0, prefix_len:]
        
        raw_text = processor.decode(new_ids, skip_special_tokens=True)
        eos = effective_config.eos_token_id
        eos_ids = set(eos if isinstance(eos, (list, tuple)) else [eos]) if eos is not None else set()
        ended_eos = bool(len(new_ids) and new_ids[-1].item() in eos_ids)
        hit_limit = len(new_ids) >= 2048
        
        raw_file = RAW_DIR / f"{checkpoint_key}__raw.txt"
        raw_file.write_text(raw_text, encoding="utf-8")
        shutil.copy2(raw_file, DRIVE_RAW_DIR / raw_file.name)
        
        extracted_patch = extract_patch(raw_text)
        task_repo_dir = repos_dir / iid
        patch_audit = test_and_apply_patch(task_repo_dir, extracted_patch)
        
        patch_file = PATCH_DIR / f"{checkpoint_key}.diff"
        patch_file.write_text(extracted_patch, encoding="utf-8")
        shutil.copy2(patch_file, DRIVE_PATCH_DIR / patch_file.name)
        
        if patch_audit["canonical_patch"]:
            canon_file = PATCH_DIR / f"{checkpoint_key}__canonical.diff"
            canon_file.write_text(patch_audit["canonical_patch"], encoding="utf-8")
            shutil.copy2(canon_file, DRIVE_PATCH_DIR / canon_file.name)
            
        pred_record = {
            "model_name_or_path": "google/gemma-4-E4B-it_int8",
            "instance_id": iid,
            "condition": cond,
            "model_patch": patch_audit["canonical_patch"] if patch_audit["recount_applicable"] else extracted_patch
        }
        pred_file = PRED_DIR / f"{checkpoint_key}__pred.json"
        pred_file.write_text(json.dumps(pred_record, indent=2), encoding="utf-8")
        shutil.copy2(pred_file, DRIVE_PRED_DIR / pred_file.name)
        
        checkpoint_data = {
            "record_type": "FRESH_COMPARISON_GPU_EXECUTION",
            "resumption_run": True,
            "instance_id": iid,
            "condition": cond,
            "attempt": 1,
            "model_id": MODEL_ID,
            "revision": REVISION,
            "quantization": "verified_bitsandbytes_8bit",
            "evidence_budget": packet["evidence_budget"],
            "evidence_tokens": packet["evidence_tokens"],
            "unused_budget": packet["unused_budget"],
            "entities_included": packet["entities_included"],
            "input_tokens": prefix_len,
            "generated_tokens": len(new_ids),
            "finish_reason": "token_limit" if hit_limit else ("eos" if ended_eos else "other_stop"),
            "ended_eos": ended_eos,
            "hit_token_cap": hit_limit,
            "elapsed_seconds": elapsed,
            "memory_allocated_bytes": mem_after,
            "strict_applicable": patch_audit["strict_applicable"],
            "recount_applicable": patch_audit["recount_applicable"],
            "has_canonical_patch": bool(patch_audit["canonical_patch"]),
            "apply_error": patch_audit["apply_error"],
            "test_resolution": "PENDING_DOCKER_EXECUTION",
            "prompt_sha256": hashlib.sha256(packet["prompt_text"].encode()).hexdigest(),
            "evidence_sha256": packet["evidence_sha256"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        ckpt_file.write_text(json.dumps(checkpoint_data, indent=2), encoding="utf-8")
        shutil.copy2(ckpt_file, drive_ckpt_file)
        
        results.append(checkpoint_data)
        print(f"  Saved checkpoint: {checkpoint_key} -> {len(new_ids)} tokens in {elapsed:.1f}s | strict: {patch_audit['strict_applicable']} | recount: {patch_audit['recount_applicable']}")
        export_summary_tables(results)
        
    print("\n" + "=" * 70)
    print("RESUMPTION COMPLETE: ALL 40 GENERATIONS RECORDED")
    print("=" * 70)

if __name__ == "__main__":
    resume_generation()
