import re
import time
from typing import Tuple

def generate_unique_run_id(model_tag: str, condition: str, budget: int = 4000, attempt: int = 1) -> str:
    """Generates deterministic collision-free run identifier."""
    ts = int(time.time())
    return f"run__{model_tag}__cond{condition}__b{budget}__att{attempt}__{ts}"

def validate_patch_syntax(patch_str: str) -> Tuple[bool, str]:
    """Validates unified diff patch syntax."""
    if not patch_str or not patch_str.strip():
        return False, "EMPTY_PATCH"

    lines = patch_str.strip().splitlines()
    has_diff_header = any(line.startswith("diff --git") or line.startswith("--- ") for line in lines)
    has_hunk_header = any(line.startswith("@@ ") for line in lines)
    has_modifications = any(line.startswith("+") or line.startswith("-") for line in lines)

    if not has_diff_header:
        return False, "MISSING_DIFF_OR_FILE_HEADER"
    if not has_hunk_header:
        return False, "MISSING_HUNK_HEADER"
    if not has_modifications:
        return False, "NO_DIFF_CHANGES"

    return True, "VALID_UNIFIED_DIFF"
