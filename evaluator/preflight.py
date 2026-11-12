import os
import json
import shutil
import subprocess
from typing import Dict, Any, Tuple, Optional

def get_workspace_dir() -> str:
    if "WORKSPACE_DIR" in os.environ:
        return os.environ["WORKSPACE_DIR"]
    if os.path.exists("/kaggle/working"):
        return "/kaggle/working"
    if os.path.exists("/content"):
        return "/content"
    return os.getcwd()

WORKSPACE_DIR = get_workspace_dir()

def check_docker_available() -> bool:
    """Checks if Docker daemon is running and accessible."""
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        return res.returncode == 0
    except Exception:
        return False

def generate_preflight_prediction_files(output_dir: Optional[str] = None) -> Tuple[str, str]:
    """Generates baseline prediction files: empty patch (base sanity) and reference gold patch."""
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE_DIR, "evaluator", "preflight_preds")
    os.makedirs(output_dir, exist_ok=True)
    empty_pred_path = os.path.join(output_dir, "preflight_empty_patch.jsonl")
    gold_pred_path = os.path.join(output_dir, "preflight_gold_patch.jsonl")

    # Empty patch baseline
    with open(empty_pred_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "model_name_or_path": "baseline_empty",
            "instance_id": "marshmallow-code__marshmallow-1343",
            "model_patch": ""
        }) + "\n")

    # Reference test patch baseline
    with open(gold_pred_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "model_name_or_path": "reference_gold",
            "instance_id": "marshmallow-code__marshmallow-1343",
            "model_patch": (
                "diff --git a/src/marshmallow/schema.py b/src/marshmallow/schema.py\n"
                "--- a/src/marshmallow/schema.py\n"
                "+++ b/src/marshmallow/schema.py\n"
                "@@ -892,3 +892,5 @@ def _invoke_field_validators(self, unmarshal, data, many):\n"
                "         for field_name, field_obj in self.fields.items():\n"
                "+            if data is None:\n"
                "+                continue\n"
                "             value = data[field_obj.attribute or field_name]\n"
            )
        }) + "\n")

    print(f"Generated Preflight Empty Prediction: {empty_pred_path}")
    print(f"Generated Preflight Gold Prediction : {gold_pred_path}")
    return empty_pred_path, gold_pred_path

def check_preflight_results(log_dir: Optional[str] = None) -> Dict[str, Any]:
    if log_dir is None:
        log_dir = os.path.join(WORKSPACE_DIR, "logs", "evaluation")
    """
    Audits whether the containerized evaluation harness has executed base and reference preflight.
    Marks preflight clearly PENDING if Docker has not run.
    """
    docker_up = check_docker_available()
    has_logs = os.path.exists(log_dir) and len(os.listdir(log_dir)) > 0 if os.path.exists(log_dir) else False

    if not docker_up or not has_logs:
        return {
            "preflight_status": "PENDING_DOCKER_EXECUTION",
            "is_pending": True,
            "docker_available": docker_up,
            "has_execution_logs": has_logs,
            "message": (
                "Evaluator base/reference-patch preflight is PENDING. "
                "Docker runner has not executed containerized tests (standard in Google Colab). "
                "Evaluation harness should be executed on WSL2/Linux with Docker."
            )
        }

    return {
        "preflight_status": "COMPLETED",
        "is_pending": False,
        "docker_available": True,
        "has_execution_logs": True,
        "message": "Evaluator preflight checks completed in Docker environment."
    }
