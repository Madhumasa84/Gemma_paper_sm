import os
import json
import subprocess
from typing import List, Dict, Any, Tuple, Optional

from gemma_paper.workspace import WORKSPACE_DIR

def load_and_select_tasks() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Loads SWE-bench Lite dev split and selects the first instance from first 3 lexicographical repos."""
    import datasets

    ds = datasets.load_dataset("princeton-nlp/SWE-bench_Lite", split="dev")
    repos = sorted(list(set(row["repo"] for row in ds)))
    selected_repos = repos[:3]

    selected_tasks = []
    for repo in selected_repos:
        repo_tasks = sorted([row for row in ds if row["repo"] == repo], key=lambda x: x["instance_id"])
        selected_tasks.append(repo_tasks[0])

    manifest_meta = {
        "dataset_name": "princeton-nlp/SWE-bench_Lite",
        "split": "dev",
        "selection_rule": "Lexicographical repo ordering, first 3 distinct repos, lowest instance ID per repo",
        "selected_tasks": [
            {
                "instance_id": t["instance_id"],
                "repo": t["repo"],
                "base_commit": t["base_commit"],
                "problem_statement": t["problem_statement"]
            }
            for t in selected_tasks
        ]
    }
    return selected_tasks, manifest_meta

def save_task_manifest(manifest_meta: Dict[str, Any], output_path: Optional[str] = None) -> str:
    if output_path is None:
        output_path = os.path.join(WORKSPACE_DIR, "task_manifest.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest_meta, f, indent=2)
    return output_path

def prepare_repository_at_base_commit(repo_name: str, base_commit: str, target_dir: str):
    """Clones repo if not present and checks out base commit."""
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    if not os.path.exists(target_dir):
        clone_url = f"https://github.com/{repo_name}.git"
        print(f"Cloning {clone_url} -> {target_dir}...")
        subprocess.check_call(["git", "clone", clone_url, target_dir])
    
    print(f"Checking out base commit {base_commit} in {target_dir}...")
    subprocess.check_call(["git", "-C", target_dir, "checkout", base_commit])
