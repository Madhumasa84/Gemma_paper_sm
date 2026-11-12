import os, sys, json, time, re, hashlib, subprocess, shutil, zipfile
from pathlib import Path
import pandas as pd

EVAL_BASE = Path("/content/native_evaluation")
EVAL_BASE.mkdir(parents=True, exist_ok=True)
DRIVE_EVAL_BASE = Path("/content/drive/MyDrive/gemma_paper/native_evaluation")
DRIVE_EVAL_BASE.mkdir(parents=True, exist_ok=True)

REPOS_DIR = EVAL_BASE / "eval_repos"
REPOS_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = EVAL_BASE / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_DIR = EVAL_BASE / "env_audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

WORKSPACE = Path("/content/comparison_study")
DRIVE_WORKSPACE = Path("/content/drive/MyDrive/gemma_paper/comparison_study")
CHECKPOINTS_DIR = WORKSPACE / "checkpoints"
PATCHES_DIR = WORKSPACE / "extracted_patches"

PYTHON_EXE = "/content/py39_eval_env/bin/python3"
PYTEST_EXE = "/content/py39_eval_env/bin/pytest"
DEV_PARQUET = "/root/.cache/huggingface/hub/datasets--princeton-nlp--SWE-bench_Lite/snapshots/6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2/data/dev-00000-of-00001.parquet"

def parse_pytest_output(stdout: str, f2p_list: list, p2p_list: list) -> dict:
    passed_tests = set()
    failed_tests = set()
    
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("PASSED "):
            test_id = line[len("PASSED "):].split()[0]
            passed_tests.add(test_id)
        elif line.startswith("FAILED "):
            test_id = line[len("FAILED "):].split()[0]
            failed_tests.add(test_id)
            
    f2p_status = {}
    for t in f2p_list:
        if t in passed_tests:
            f2p_status[t] = "PASSED"
        elif t in failed_tests:
            f2p_status[t] = "FAILED"
        else:
            matched = False
            for pt in passed_tests:
                if t in pt or pt in t:
                    f2p_status[t] = "PASSED"
                    matched = True
                    break
            if not matched:
                for ft in failed_tests:
                    if t in ft or ft in t:
                        f2p_status[t] = "FAILED"
                        matched = True
                        break
            if not matched:
                f2p_status[t] = "NOT_RUN"
                
    p2p_status = {}
    for t in p2p_list:
        if t in passed_tests:
            p2p_status[t] = "PASSED"
        elif t in failed_tests:
            p2p_status[t] = "FAILED"
        else:
            matched = False
            for pt in passed_tests:
                if t in pt or pt in t:
                    p2p_status[t] = "PASSED"
                    matched = True
                    break
            if not matched:
                for ft in failed_tests:
                    if t in ft or ft in t:
                        f2p_status[t] = "FAILED"
                        matched = True
                        break
            if not matched:
                p2p_status[t] = "NOT_RUN"
                
    f2p_all_passed = all(status == "PASSED" for status in f2p_status.values()) if f2p_status else False
    f2p_all_failed = all(status == "FAILED" for status in f2p_status.values()) if f2p_status else False
    p2p_any_failed = any(status == "FAILED" for status in p2p_status.values())
    
    return {
        "passed_count": len(passed_tests),
        "failed_count": len(failed_tests),
        "f2p_status": f2p_status,
        "p2p_status": p2p_status,
        "f2p_all_passed": f2p_all_passed,
        "f2p_all_failed": f2p_all_failed,
        "p2p_any_failed": p2p_any_failed
    }

def ensure_repo_setup(iid: str, repo_name: str, base_commit: str) -> Path:
    repo_dir = REPOS_DIR / iid
    if not repo_dir.exists():
        src_dir = Path("/content/comparison_study/task_repos") / iid
        if src_dir.exists():
            shutil.copytree(src_dir, repo_dir)
            subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
            subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
            subprocess.run(["git", "checkout", "--detach", base_commit], cwd=repo_dir, capture_output=True)
        else:
            repo_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "init", "--quiet"], cwd=repo_dir, check=True)
            subprocess.run(["git", "fetch", "--depth", "1", f"https://github.com/{repo_name}.git", base_commit], cwd=repo_dir, check=True)
            subprocess.run(["git", "checkout", "--detach", "--quiet", "FETCH_HEAD"], cwd=repo_dir, check=True)
            
    subprocess.run([PYTHON_EXE, "-m", "pip", "install", "--no-build-isolation", "-e", str(repo_dir)], capture_output=True, text=True)
    return repo_dir

def evaluate_task(iid: str, df: pd.DataFrame) -> dict:
    row = df[df["instance_id"] == iid].iloc[0]
    repo_name = row["repo"]
    base_commit = row["base_commit"]
    gold_patch = row["patch"]
    test_patch = row["test_patch"]
    
    f2p = json.loads(row["FAIL_TO_PASS"]) if isinstance(row["FAIL_TO_PASS"], str) else row["FAIL_TO_PASS"]
    p2p = json.loads(row["PASS_TO_PASS"]) if isinstance(row["PASS_TO_PASS"], str) else row["PASS_TO_PASS"]
    
    test_files = sorted({t.split("::")[0] for t in f2p})
    
    # 1. Base Control Verification
    base_log = LOGS_DIR / f"{iid}__base_control.log"
    repo_dir = None
    if base_log.exists():
        base_out = base_log.read_text(encoding="utf-8")
        base_parsed = parse_pytest_output(base_out, f2p, p2p)
        base_regression_failed = base_parsed["f2p_all_failed"] or (base_parsed["failed_count"] > 0)
    else:
        repo_dir = ensure_repo_setup(iid, repo_name, base_commit)
        subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
        tp_file = Path(f"/tmp/{iid}_eval_test_patch.diff")
        tp_file.write_text(test_patch, encoding="utf-8")
        subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
        base_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
        base_log.write_text(base_res.stdout + "\n" + base_res.stderr, encoding="utf-8")
        base_parsed = parse_pytest_output(base_res.stdout, f2p, p2p)
        base_regression_failed = base_parsed["f2p_all_failed"] or (base_res.returncode != 0 and base_parsed["failed_count"] > 0)

    # 2. Reference Control Verification
    ref_log = LOGS_DIR / f"{iid}__ref_control.log"
    if ref_log.exists():
        ref_out = ref_log.read_text(encoding="utf-8")
        ref_parsed = parse_pytest_output(ref_out, f2p, p2p)
        ref_passed = ref_parsed["f2p_all_passed"] or ("failed" not in ref_out.lower() and "passed" in ref_out.lower())
    else:
        if repo_dir is None:
            repo_dir = ensure_repo_setup(iid, repo_name, base_commit)
        subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
        gp_file = Path(f"/tmp/{iid}_eval_gold_patch.diff")
        gp_file.write_text(gold_patch, encoding="utf-8")
        subprocess.run(["git", "apply", str(gp_file)], cwd=repo_dir, check=True)
        tp_file = Path(f"/tmp/{iid}_eval_test_patch.diff")
        tp_file.write_text(test_patch, encoding="utf-8")
        subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
        ref_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
        ref_log.write_text(ref_res.stdout + "\n" + ref_res.stderr, encoding="utf-8")
        ref_parsed = parse_pytest_output(ref_res.stdout, f2p, p2p)
        ref_passed = (ref_res.returncode == 0) or ref_parsed["f2p_all_passed"]

    control_passed = base_regression_failed and ref_passed
    
    # 3. Evaluate Conditions (W, A, B, C)
    conditions = ["W", "A", "B", "C"]
    cond_results = {}
    
    for c in conditions:
        ckpt_path = CHECKPOINTS_DIR / f"{iid}__{c}__checkpoint.json"
        if not ckpt_path.exists():
            cond_results[c] = {
                "status": "GENERATION_PENDING",
                "resolution": "PENDING_GENERATION"
            }
            continue
            
        with open(ckpt_path) as f:
            ckpt = json.load(f)
            
        recount_app = ckpt.get("recount_applicable", False)
        if not recount_app:
            cond_results[c] = {
                "status": "NOT_APPLICABLE",
                "resolution": "UNRESOLVED",
                "reason": "Failed git apply --recount check",
                "strict_applicable": ckpt.get("strict_applicable", False),
                "recount_applicable": False,
                "generated_tokens": ckpt.get("generated_tokens", 0)
            }
            continue
            
        # Applicable patch: evaluate test outcome
        eval_log = LOGS_DIR / f"{iid}__{c}__eval.log"
        if eval_log.exists():
            cond_out = eval_log.read_text(encoding="utf-8")
            cond_parsed = parse_pytest_output(cond_out, f2p, p2p)
            f2p_ok = cond_parsed["f2p_all_passed"]
            p2p_ok = not cond_parsed["p2p_any_failed"]
            resolved = f2p_ok and p2p_ok
            cond_results[c] = {
                "status": "EVALUATED",
                "resolution": "RESOLVED" if resolved else "UNRESOLVED",
                "f2p_all_passed": f2p_ok,
                "p2p_any_failed": cond_parsed["p2p_any_failed"],
                "strict_applicable": ckpt.get("strict_applicable", False),
                "recount_applicable": True,
                "generated_tokens": ckpt.get("generated_tokens", 0)
            }
        else:
            if repo_dir is None:
                repo_dir = ensure_repo_setup(iid, repo_name, base_commit)
            subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
            subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
            
            canon_diff = PATCHES_DIR / f"{iid}__{c}__canonical.diff"
            raw_diff = PATCHES_DIR / f"{iid}__{c}.diff"
            patch_to_use = canon_diff if canon_diff.exists() else raw_diff
            
            apply_res = subprocess.run(["git", "apply", "--recount", str(patch_to_use)], cwd=repo_dir, capture_output=True, text=True)
            if apply_res.returncode != 0:
                cond_results[c] = {
                    "status": "APPLY_ERROR_ON_EVAL_BASE",
                    "resolution": "UNRESOLVED",
                    "error": apply_res.stderr.strip()
                }
                continue
                
            tp_file = Path(f"/tmp/{iid}_eval_test_patch.diff")
            tp_file.write_text(test_patch, encoding="utf-8")
            subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
            
            test_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
            eval_log.write_text(test_res.stdout + "\n" + test_res.stderr, encoding="utf-8")
            cond_parsed = parse_pytest_output(test_res.stdout, f2p, p2p)
            f2p_ok = cond_parsed["f2p_all_passed"]
            p2p_ok = not cond_parsed["p2p_any_failed"]
            resolved = (test_res.returncode == 0) and f2p_ok and p2p_ok
            cond_results[c] = {
                "status": "EVALUATED",
                "resolution": "RESOLVED" if resolved else "UNRESOLVED",
                "exit_code": test_res.returncode,
                "f2p_all_passed": f2p_ok,
                "p2p_any_failed": cond_parsed["p2p_any_failed"],
                "strict_applicable": ckpt.get("strict_applicable", False),
                "recount_applicable": True,
                "generated_tokens": ckpt.get("generated_tokens", 0)
            }
            
    return {
        "instance_id": iid,
        "repo": repo_name,
        "base_commit": base_commit,
        "control_passed": control_passed,
        "base_regression_failed": base_regression_failed,
        "ref_passed": ref_passed,
        "conditions": cond_results
    }

def run():
    df = pd.read_parquet(DEV_PARQUET)
    with open(WORKSPACE / "task_manifest.json") as f:
        manifest = json.load(f)
        
    study_eval_results = []
    for task in manifest["tasks"]:
        iid = task["instance_id"]
        res = evaluate_task(iid, df)
        study_eval_results.append(res)
        
    # Save native eval results
    summary_path = EVAL_BASE / "native_evaluation_results.json"
    summary_path.write_text(json.dumps(study_eval_results, indent=2))
    shutil.copy2(summary_path, DRIVE_EVAL_BASE / summary_path.name)
    
    # Mirror all logs
    for log_file in LOGS_DIR.glob("*.log"):
        shutil.copy2(log_file, DRIVE_EVAL_BASE / log_file.name)
        
    print(f"Evaluated {len(study_eval_results)} tasks. Summary written to {summary_path}")
    return study_eval_results

if __name__ == "__main__":
    run()
