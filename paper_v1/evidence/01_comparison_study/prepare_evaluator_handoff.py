import os, json, hashlib, shutil
from pathlib import Path

WORKSPACE = Path("/content/comparison_study")
HANDOFF_DIR = WORKSPACE / "evaluator_handoff"
HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
DRIVE_HANDOFF_DIR = Path("/content/drive/MyDrive/gemma_paper/comparison_study/evaluator_handoff")
DRIVE_HANDOFF_DIR.mkdir(parents=True, exist_ok=True)

def prepare_handoff():
    pred_dir = WORKSPACE / "predictions"
    pred_files = sorted(pred_dir.glob("*__*__pred.json"))
    
    all_preds = []
    by_cond = {"W": [], "A": [], "B": [], "C": []}
    
    for pf in pred_files:
        with open(pf) as f:
            data = json.load(f)
            rec = {
                "model_name_or_path": data.get("model_name_or_path", "google/gemma-4-E4B-it_int8"),
                "instance_id": data["instance_id"],
                "model_patch": data.get("model_patch", "")
            }
            all_preds.append(rec)
            cond = data.get("condition")
            if cond in by_cond:
                by_cond[cond].append(rec)
                
    # Write JSONLs
    all_jsonl = HANDOFF_DIR / "all_predictions.jsonl"
    with open(all_jsonl, "w", encoding="utf-8") as f:
        for r in all_preds:
            f.write(json.dumps(r) + "\n")
            
    for cond, records in by_cond.items():
        cond_file = HANDOFF_DIR / f"predictions_{cond}.jsonl"
        with open(cond_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
                
    # Runner script
    script = """#!/usr/bin/env bash
# SWE-bench 4.1.0 Evaluation Runner for WSL2 / Linux (Requires Docker)
set -euo pipefail

echo "=== Verifying Docker daemon ==="
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker is not installed. Please install Docker Engine / Docker Desktop."
    exit 1
fi
if ! docker ps &> /dev/null; then
    echo "ERROR: Docker daemon is not running or accessible without sudo."
    exit 1
fi
echo "Docker daemon verified."

echo "=== Checking SWE-bench installation ==="
python3 -c "import swebench; print('SWE-bench version:', swebench.__version__)" || pip install swebench==4.1.0

echo "=== Running Official SWE-bench Lite Evaluation ==="
# Evaluates applicable and baseline predictions with max_workers=1
python3 -m swebench.harness.run_evaluation \\
    --dataset_name princeton-nlp/SWE-bench_Lite \\
    --split dev \\
    --predictions_path ./all_predictions.jsonl \\
    --max_workers 1 \\
    --run_id gemma4_rep_eval_$(date +%Y%m%d_%H%M%S)

echo "Evaluation run finished. Logs and reports generated in logs/run_evaluation/"
"""
    (HANDOFF_DIR / "run_evaluator_wsl.sh").write_text(script, encoding="utf-8")
    os.chmod(HANDOFF_DIR / "run_evaluator_wsl.sh", 0o755)
    
    # Manifest
    files_to_hash = [p for p in sorted(HANDOFF_DIR.glob("*")) if p.is_file() and p.name != "evaluator_manifest.json"]
    manifest = []
    for p in files_to_hash:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest.append({"file": p.name, "sha256": h, "bytes": p.stat().st_size})
        
    (HANDOFF_DIR / "evaluator_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    
    # Mirror to Drive
    for p in HANDOFF_DIR.glob("*"):
        if p.is_file():
            shutil.copy2(p, DRIVE_HANDOFF_DIR / p.name)
            
    # Tarball
    tar_path = WORKSPACE / "comparison_evaluator_handoff.tar.gz"
    shutil.make_archive(str(WORKSPACE / "comparison_evaluator_handoff"), "gztar", root_dir=HANDOFF_DIR)
    if (WORKSPACE / "comparison_evaluator_handoff.tar.gz").exists():
        shutil.copy2(WORKSPACE / "comparison_evaluator_handoff.tar.gz", Path("/content/drive/MyDrive/gemma_paper/comparison_evaluator_handoff.tar.gz"))
    print(f"Evaluator handoff packaged: {len(all_preds)} predictions ready.")

if __name__ == "__main__":
    prepare_handoff()
