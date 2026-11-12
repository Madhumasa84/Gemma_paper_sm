import os, sys, time, json, subprocess, shutil
from pathlib import Path

WORKSPACE = Path("/content/comparison_study")
CHECKPOINTS_DIR = WORKSPACE / "checkpoints"
EVAL_BASE = Path("/content/native_evaluation")
PYTHON_EXE = "/content/py39_eval_env/bin/python3"
EXPORT_SCRIPT = "/content/comparison_study/export_study_bundle.py"
HANDOFF_SCRIPT = "/content/comparison_study/prepare_evaluator_handoff.py"
EVAL_SCRIPT = "/content/native_evaluation/evaluate_and_compile.py"

def run_cycle():
    print(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ')}] Running evaluation and compilation cycle...")
    res = subprocess.run([PYTHON_EXE, EVAL_SCRIPT], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Eval script error: {res.stderr}")
    else:
        print(res.stdout.strip())
        
    # Re-export study bundle & results.md
    res_exp = subprocess.run(["python3", EXPORT_SCRIPT], cwd=WORKSPACE, capture_output=True, text=True)
    if res_exp.returncode != 0:
        print(f"Export bundle error: {res_exp.stderr}")
        
    # Re-prepare evaluator handoff
    res_hand = subprocess.run(["python3", HANDOFF_SCRIPT], cwd=WORKSPACE, capture_output=True, text=True)
    if res_hand.returncode != 0:
        print(f"Handoff error: {res_hand.stderr}")

if __name__ == "__main__":
    run_cycle()
