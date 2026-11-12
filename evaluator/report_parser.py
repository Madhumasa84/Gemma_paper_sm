import json
import os
from typing import Dict, Any

def join_evaluator_report_to_configuration(eval_report_path: str, config_hash: str) -> Dict[str, Any]:
    """Merges SWE-bench official test report with configuration metadata."""
    if not os.path.exists(eval_report_path):
        return {
            "eval_report_found": False,
            "status": "PENDING_EVALUATION",
            "config_hash": config_hash
        }
    with open(eval_report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["joined_config_hash"] = config_hash
    return data
