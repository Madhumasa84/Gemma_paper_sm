import os
import json
import torch
import transformers
from typing import Dict, Any, List

def build_manifest(
    model: Any,
    processor: Any,
    model_id: str,
    revision: str = "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c",
    quantization_type: str = "bitsandbytes_8bit",
    unquantized_dtype: str = "float16",
    enable_thinking: bool = False,
    smoke_test_results: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    manifest = {
        "model_id": model_id,
        "model_revision": revision,
        "quantization_type": quantization_type,
        "unquantized_dtype": unquantized_dtype,
        "enable_thinking": enable_thinking,
        "framework_versions": {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        },
        "smoke_test_results": smoke_test_results or [],
        "evidence_budget_ceiling": 4000,
        "max_output_tokens": 2048,
        "allowed_conditions": ["W", "A", "B", "C"]
    }
    return manifest

def save_manifest(manifest: Dict[str, Any], output_dir: str = "/content/gemma_paper") -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written successfully: {path}")
    return path
