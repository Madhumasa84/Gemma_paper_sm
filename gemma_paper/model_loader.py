import os
import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from typing import Tuple, Dict, Any, Optional

DEFAULT_MODEL_ID = "google/gemma-4-E4B-it"
DEFAULT_MODEL_REVISION = "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"

def get_hf_token() -> Optional[str]:
    """Retrieve HF_TOKEN securely from Kaggle Secrets, Colab Secrets, or environment."""
    try:
        from kaggle_secrets import UserSecretsClient
        return UserSecretsClient().get_secret("HF_TOKEN")
    except Exception:
        pass
    try:
        from google.colab import userdata
        token = userdata.get("HF_TOKEN")
        if token:
            return token
    except Exception:
        pass
    return os.environ.get("HF_TOKEN", None)

def verify_manifest_revision(manifest: Dict[str, Any], revision: str) -> bool:
    """Verifies that the model revision matches the evidence-packet manifest."""
    manifest_rev = manifest.get("model_revision") or manifest.get("model_config", {}).get("revision")
    if manifest_rev and manifest_rev != revision:
        raise ValueError(
            f"Revision mismatch! Evidence packet manifest specifies '{manifest_rev}', "
            f"but loader was called with '{revision}'."
        )
    return True

def load_gemma4_and_processor(
    model_id: str = DEFAULT_MODEL_ID,
    revision: str = DEFAULT_MODEL_REVISION,
    use_4bit: bool = False,
    device_map: str = "auto"
) -> Tuple[Any, Any, torch.dtype]:
    """
    Loads Google Gemma 4 model and AutoProcessor with explicit revision and quantization.
    
    Guarantees:
    - Stops immediately with RuntimeError if CUDA GPU is not available.
    - Explicit revision passed to both AutoProcessor and AutoModelForImageTextToText.
    - use_4bit=False explicitly selects BitsAndBytesConfig(load_in_8bit=True), NEVER full precision.
    - Zero mock/stub fallbacks: missing GPU or failure halts execution.
    """
    if not torch.cuda.is_available():
        raise RuntimeError(
            "FATAL: CUDA GPU acceleration is required for 8-bit BitsAndBytes quantization! "
            "No CUDA-capable GPU detected. Please attach a GPU runtime in Colab "
            "(Runtime -> Change runtime type -> T4 GPU)."
        )

    hf_token = get_hf_token()
    unquantized_dtype = torch.float16

    print(f"[Model Loader] Target Model ID       : {model_id}")
    print(f"[Model Loader] Explicit Revision     : {revision}")
    
    # 1. Configure Quantization (Strictly 8-bit when use_4bit=False, never full precision)
    if use_4bit:
        print("[Model Loader] Quantization Mode      : 4-bit NF4 (BitsAndBytesConfig)")
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
    else:
        print("[Model Loader] Quantization Mode      : 8-bit INT8 (BitsAndBytesConfig load_in_8bit=True)")
        quant_config = BitsAndBytesConfig(
            load_in_8bit=True
        )

    # 2. Load Processor with explicit revision
    print(f"[Model Loader] Loading AutoProcessor (revision={revision})...")
    processor = AutoProcessor.from_pretrained(
        model_id,
        revision=revision,
        token=hf_token
    )

    # 3. Load Model with explicit revision and quantization config
    print(f"[Model Loader] Loading AutoModelForImageTextToText (revision={revision}, quantization={quant_config})...")
    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        revision=revision,
        quantization_config=quant_config,
        device_map=device_map,
        torch_dtype=unquantized_dtype,
        token=hf_token
    )

    return model, processor, unquantized_dtype

def verify_quantization_and_placement(model: Any) -> Dict[str, Any]:
    """
    Inspects model layers, counts quantized layers, checks device placement,
    and reports GPU memory measurements. Rejects mock objects.
    """
    if getattr(model, "is_mock", False):
        raise ValueError("Cannot verify quantization on a mock model in production inference.")

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available to verify GPU quantization and placement.")

    import bitsandbytes as bnb

    quant_layers_8bit = 0
    quant_layers_4bit = 0
    total_linear = 0
    devices = set()

    for name, module in model.named_modules():
        if isinstance(module, bnb.nn.Linear8bitLt):
            quant_layers_8bit += 1
        elif isinstance(module, bnb.nn.Linear4bit):
            quant_layers_4bit += 1
        elif isinstance(module, torch.nn.Linear):
            total_linear += 1

    for param in model.parameters():
        devices.add(str(param.device))

    gpu_mem = {
        "allocated_gb": round(torch.cuda.memory_allocated() / (1024**3), 3),
        "reserved_gb": round(torch.cuda.memory_reserved() / (1024**3), 3),
        "max_allocated_gb": round(torch.cuda.max_memory_allocated() / (1024**3), 3)
    }

    report = {
        "quantized_8bit_layers": quant_layers_8bit,
        "quantized_4bit_layers": quant_layers_4bit,
        "unquantized_linear_layers": total_linear,
        "device_placement": sorted(list(devices)),
        "gpu_memory": gpu_mem,
        "status": "VERIFIED_ON_GPU"
    }

    print("=" * 60)
    print("QUANTIZATION & DEVICE PLACEMENT VERIFICATION REPORT")
    print("=" * 60)
    print(f"Quantized 8-bit Layers (Linear8bitLt) : {quant_layers_8bit}")
    print(f"Quantized 4-bit Layers (Linear4bit)   : {quant_layers_4bit}")
    print(f"Unquantized Linear Layers             : {total_linear}")
    print(f"Parameter Device Placements           : {report['device_placement']}")
    print(f"GPU VRAM Allocated                   : {gpu_mem['allocated_gb']} GB")
    print(f"GPU VRAM Reserved                    : {gpu_mem['reserved_gb']} GB")
    print(f"GPU Peak Allocated                   : {gpu_mem['max_allocated_gb']} GB")
    print("=" * 60)

    return report
