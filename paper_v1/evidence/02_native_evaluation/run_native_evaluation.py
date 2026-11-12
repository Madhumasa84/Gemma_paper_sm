import os, sys, json, time, re, hashlib, subprocess, shutil
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

PYTHON_EXE = "/content/py39_eval_env/bin/python3"
PYTEST_EXE = "/content/py39_eval_env/bin/pytest"

DEV_PARQUET = "/root/.cache/huggingface/hub/datasets--princeton-nlp--SWE-bench_Lite/snapshots/6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2/data/dev-00000-of-00001.parquet"

def parse_pytest_output(stdout: str, f2p_list: list, p2p_list: list) -> dict:
    # Look for PASSED / FAILED test lines in pytest -rA output
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
            # Check prefix/suffix matching
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

def run_evaluation_for_task(iid: str, df: pd.DataFrame):
    row = df[df["instance_id"] == iid].iloc[0]
    repo_name = row["repo"]
    base_commit = row["base_commit"]
    gold_patch = row["patch"]
    test_patch = row["test_patch"]
    
    f2p = json.loads(row["FAIL_TO_PASS"]) if isinstance(row["FAIL_TO_PASS"], str) else row["FAIL_TO_PASS"]
    p2p = json.loads(row["PASS_TO_PASS"]) if isinstance(row["PASS_TO_PASS"], str) else row["PASS_TO_PASS"]
    
    print(f"\n=======================================================")
    print(f"NATIVE EVALUATION: {iid} ({repo_name} @ {base_commit[:10]})")
    print(f"=======================================================")
    
    # 1. Environment Audit
    env_audit = {
        "instance_id": iid,
        "repo": repo_name,
        "docker_spec": {"python": "3.9", "test_cmd": "pytest -rA"},
        "native_colab_env": {
            "python": subprocess.run([PYTHON_EXE, "--version"], capture_output=True, text=True).stdout.strip(),
            "pytest": subprocess.run([PYTEST_EXE, "--version"], capture_output=True, text=True).stdout.strip()
        },
        "env_differences": [
            "Native environment uses isolated conda-forge Python 3.9 virtual environment",
            "Installed numpy==1.26.4 (NumPy 1.x) to preserve legacy API compatibility",
            "pytest 8.4.1"
        ]
    }
    
    # Base checkout
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
        
    # Install package into eval env if not installed
    install_res = subprocess.run([PYTHON_EXE, "-m", "pip", "install", "--no-build-isolation", "-e", str(repo_dir)], capture_output=True, text=True)
    if install_res.returncode != 0:
        env_audit["status"] = "NATIVE_EVALUATION_BLOCKED"
        env_audit["error"] = install_res.stderr.strip()
        (AUDIT_DIR / f"{iid}__audit.json").write_text(json.dumps(env_audit, indent=2))
        print(f"ERROR: Native evaluation blocked for {iid}: {install_res.stderr[:200]}")
        return {"instance_id": iid, "status": "NATIVE_EVALUATION_BLOCKED", "error": install_res.stderr.strip()}
    
    env_audit["status"] = "ENVIRONMENT_VERIFIED"
    (AUDIT_DIR / f"{iid}__audit.json").write_text(json.dumps(env_audit, indent=2))
    
    # Extract test targets from f2p
    test_files = sorted({t.split("::")[0] for t in f2p})
    
    # 2. Base Control Verification
    print("Running Base Control (unmodified base + benchmark test patch)...")
    subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
    
    tp_file = Path(f"/tmp/{iid}_eval_test_patch.diff")
    tp_file.write_text(test_patch, encoding="utf-8")
    subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
    
    base_test_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
    (LOGS_DIR / f"{iid}__base_control.log").write_text(base_test_res.stdout + "\n" + base_test_res.stderr, encoding="utf-8")
    
    base_parsed = parse_pytest_output(base_test_res.stdout, f2p, p2p)
    base_regression_failed = base_parsed["f2p_all_failed"] or (base_test_res.returncode != 0 and base_parsed["failed_count"] > 0)
    print(f"  Base Control Result: returncode={base_test_res.returncode}, target test failed={base_regression_failed}")
    
    # 3. Reference Control Verification
    print("Running Reference Control (base + developer gold patch + test patch)...")
    subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
    subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
    
    gp_file = Path(f"/tmp/{iid}_eval_gold_patch.diff")
    gp_file.write_text(gold_patch, encoding="utf-8")
    subprocess.run(["git", "apply", str(gp_file)], cwd=repo_dir, check=True)
    subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
    
    ref_test_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
    (LOGS_DIR / f"{iid}__ref_control.log").write_text(ref_test_res.stdout + "\n" + ref_test_res.stderr, encoding="utf-8")
    
    ref_parsed = parse_pytest_output(ref_test_res.stdout, f2p, p2p)
    ref_passed = (ref_test_res.returncode == 0) or ref_parsed["f2p_all_passed"]
    print(f"  Reference Control Result: returncode={ref_test_res.returncode}, target test passed={ref_passed}")
    
    control_passed = base_regression_failed and ref_passed
    print(f"  Controls Preflight Status: {'PASSED' if control_passed else 'FAILED'}")
    
    # 4. Evaluate Available Conditions (W, A, B, C)
    checkpoints_dir = Path("/content/comparison_study/checkpoints")
    patches_dir = Path("/content/comparison_study/extracted_patches")
    
    conditions = ["W", "A", "B", "C"]
    condition_outcomes = {}
    
    for c in conditions:
        ckpt_path = checkpoints_dir / f"{iid}__{c}__checkpoint.json"
        if not ckpt_path.exists():
            condition_outcomes[c] = {"status": "GENERATION_PENDING"}
            continue
            
        with open(ckpt_path) as f:
            ckpt = json.load(f)
            
        recount_app = ckpt.get("recount_applicable", False)
        if not recount_app:
            condition_outcomes[c] = {
                "status": "NOT_APPLICABLE",
                "resolution": "UNRESOLVED",
                "details": "Model patch failed git apply --recount check"
            }
            continue
            
        # Patch is applicable! Test it!
        canon_diff = patches_dir / f"{iid}__{c}__canonical.diff"
        raw_diff = patches_dir / f"{iid}__{c}.diff"
        patch_to_use = canon_diff if canon_diff.exists() else raw_diff
        
        print(f"Evaluating Condition {c} ({patch_to_use.name})...")
        subprocess.run(["git", "checkout", "--", "."], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_dir, capture_output=True)
        
        apply_res = subprocess.run(["git", "apply", "--recount", str(patch_to_use)], cwd=repo_dir, capture_output=True, text=True)
        if apply_res.returncode != 0:
            condition_outcomes[c] = {
                "status": "APPLY_ERROR_ON_EVAL_BASE",
                "resolution": "UNRESOLVED",
                "error": apply_res.stderr.strip()
            }
            continue
            
        # Apply test patch
        subprocess.run(["git", "apply", str(tp_file)], cwd=repo_dir, check=True)
        
        # Run tests
        cond_test_res = subprocess.run([PYTEST_EXE, "-rA", *test_files], cwd=repo_dir, capture_output=True, text=True)
        (LOGS_DIR / f"{iid}__{c}__eval.log").write_text(cond_test_res.stdout + "\n" + cond_test_res.stderr, encoding="utf-8")
        
        cond_parsed = parse_pytest_output(cond_test_res.stdout, f2p, p2p)
        
        # Check resolution: ALL F2P pass, and NO P2P failed
        f2p_ok = cond_parsed["f2p_all_passed"]
        p2p_ok = not cond_parsed["p2p_any_failed"]
        
        resolved = (cond_test_res.returncode == 0) and f2p_ok and p2p_ok
        resolution_label = "RESOLVED" if resolved else "UNRESOLVED"
        
        condition_outcomes[c] = {
            "status": "EVALUATED",
            "resolution": resolution_label,
            "exit_code": cond_test_res.returncode,
            "f2p_all_passed": f2p_ok,
            "p2p_any_failed": cond_parsed["p2p_any_failed"],
            "passed_test_count": cond_parsed["passed_count"],
            "failed_test_count": cond_parsed["failed_count"],
            "f2p_details": cond_parsed["f2p_status"]
        }
        print(f"  Condition {c} Result: {resolution_label} (f2p passed: {f2p_ok}, p2p failure: {cond_parsed['p2p_any_failed']})")
        
    return {
        "instance_id": iid,
        "control_passed": control_passed,
        "base_regression_failed": base_regression_failed,
        "ref_passed": ref_passed,
        "conditions": condition_outcomes
    }

def run_all_evaluations():
    df = pd.read_parquet(DEV_PARQUET)
    with open("/content/comparison_study/task_manifest.json") as f:
        manifest = json.load(f)
        
    all_results = []
    for task in manifest["tasks"]:
        iid = task["instance_id"]
        res = run_evaluation_for_task(iid, df)
        all_results.append(res)
        
    (EVAL_BASE / "native_evaluation_results.json").write_text(json.dumps(all_results, indent=2))
    (DRIVE_EVAL_BASE / "native_evaluation_results.json").write_text(json.dumps(all_results, indent=2))
    
    # Mirror logs
    for log_file in LOGS_DIR.glob("*.log"):
        shutil.copy2(log_file, DRIVE_EVAL_BASE / log_file.name)
        
    print(f"\nNative evaluation complete for {len(all_results)} tasks!")

if __name__ == "__main__":
    run_all_evaluations()
