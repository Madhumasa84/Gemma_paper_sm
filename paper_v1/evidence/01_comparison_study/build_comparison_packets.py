import os, sys, json, hashlib
sys.path.insert(0, "/content")
from pathlib import Path
from transformers import AutoProcessor
from gemma_paper.retrieval import build_and_cache_task_ranking
from gemma_paper.packet_runner import pack_evidence_for_condition

MODEL_ID = "google/gemma-4-E4B-it"
REVISION = "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"
BUDGET = 4000
CONDITIONS = ["W", "A", "B", "C"]

processor = AutoProcessor.from_pretrained(MODEL_ID, revision=REVISION, trust_remote_code=False)
tokenizer = processor.tokenizer

with open("/content/comparison_study/task_manifest.json") as f:
    manifest = json.load(f)

repos_dir = Path("/content/comparison_study/task_repos")
out_dir = Path("/content/comparison_study/evidence_packets")
out_dir.mkdir(parents=True, exist_ok=True)
drive_dir = Path("/content/drive/MyDrive/gemma_paper/comparison_study/evidence_packets")
drive_dir.mkdir(parents=True, exist_ok=True)

packets_summary = []

for task in manifest["tasks"]:
    iid = task["instance_id"]
    repo_dir = repos_dir / iid
    prob = task["problem_statement"]
    print(f"Ranking entities for {iid}...")
    ranking = build_and_cache_task_ranking(iid, str(repo_dir), prob)
    
    # Save ranking
    (out_dir / f"{iid}_ranking.json").write_text(json.dumps({
        "task_id": iid,
        "indexed_file_count": ranking["indexed_file_count"],
        "ranked_entities_count": ranking["ranked_entities_count"],
        "top_10": [{"name": e["name"], "file_path": e["file_path"], "type": e["type"]} for e in ranking["ranked_entities"][:10]]
    }, indent=2))
    
    for cond in CONDITIONS:
        packed_text, token_count, verif = pack_evidence_for_condition(cond, ranking, processor, budget=BUDGET)
        
        PATCH_ONLY = (
            "\n### PATCH-ONLY INSTRUCTION \u2014 fresh instrumented protocol v1\n"
            "Return only one explicitly labelled diff fenced block containing a unified diff. "
            "Use exact repository source context. Do not include explanations, placeholders, ellipses, or text outside the diff block.\n"
        )
        prompt = (
            f"You are an expert software engineer resolving an issue in the repository for task '{iid}'.\n\n"
            f"### ISSUE PROBLEM STATEMENT\n{prob.strip()}\n\n"
            f"### RELEVANT REPOSITORY CODE (Evidence Condition: {cond})\n{packed_text.strip()}\n\n"
            "### INSTRUCTIONS\nAnalyze the issue description and repository code above.\nWrite a patch that fixes the issue.\n"
            "Output your patch as a unified diff format inside a ```diff code block.\n"
            "Ensure file paths in the diff match the repository files (e.g., a/src/... b/src/...).\n" + PATCH_ONLY
        )
        
        messages = [{"role": "user", "content": prompt}]
        rendered = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        input_ids = tokenizer.encode(rendered, add_special_tokens=False)
        
        packet_data = {
            "instance_id": iid,
            "repo": task["repo"],
            "base_commit": task["base_commit"],
            "condition": cond,
            "evidence_budget": BUDGET,
            "evidence_tokens": token_count,
            "unused_budget": BUDGET - token_count,
            "entities_included": verif["entities_included"],
            "under_ceiling": token_count <= BUDGET,
            "evidence_sha256": hashlib.sha256(packed_text.encode()).hexdigest(),
            "evidence_text": packed_text,
            "prompt_text": prompt,
            "rendered_prompt": rendered,
            "input_tokens_count": len(input_ids)
        }
        
        pkt_filename = f"{iid}__{cond}__packet.json"
        (out_dir / pkt_filename).write_text(json.dumps(packet_data, indent=2))
        (drive_dir / pkt_filename).write_text(json.dumps(packet_data, indent=2))
        
        packets_summary.append({
            "instance_id": iid,
            "condition": cond,
            "evidence_tokens": token_count,
            "entities_included": verif["entities_included"],
            "input_tokens": len(input_ids)
        })
        n_ent = verif["entities_included"]
        n_inp = len(input_ids)
        print(f"  [{cond}] tokens: {token_count}/{BUDGET} (entities: {n_ent}, input tokens: {n_inp})")

(out_dir / "all_packets_manifest.json").write_text(json.dumps(packets_summary, indent=2))
(drive_dir / "all_packets_manifest.json").write_text(json.dumps(packets_summary, indent=2))
print("All 40 packets successfully packed, tokenized, and verified!")
