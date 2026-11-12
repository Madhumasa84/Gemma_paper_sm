import time
import torch
from typing import Dict, Any

SHORT_SANITY_PROMPT = "Write a hello world Python function."
SWE_BENCH_REPRESENTATIVE_CODE_PROMPT = (
    "Fix the following bug in Schema._invoke_field_validators: "
    "TypeError: 'NoneType' object is not subscriptable when data is None."
)

def format_chat_input(processor: Any, prompt: str, enable_thinking: bool = False) -> Dict[str, Any]:
    """Formats prompt with processor chat template, respecting enable_thinking=False."""
    messages = [{"role": "user", "content": prompt}]
    
    if hasattr(processor, "apply_chat_template"):
        try:
            # Gemma 4 chat template support
            rendered = processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=enable_thinking
            )
            inputs = processor(text=[rendered], return_tensors="pt")
            return inputs
        except TypeError:
            pass

    inputs = processor(text=[prompt], return_tensors="pt")
    return inputs

def run_smoke_test(
    model: Any,
    processor: Any,
    prompt: str,
    test_label: str,
    max_new_tokens: int = 64,
    enable_thinking: bool = False,
    temperature: float = 0.0
) -> Dict[str, Any]:
    """Runs a single generation smoke test and measures token count and latency."""
    print(f"\n--- Running {test_label} ---")
    inputs = format_chat_input(processor, prompt, enable_thinking=enable_thinking)
    input_ids = inputs["input_ids"]
    if torch.cuda.is_available() and not getattr(model, "is_mock", False):
        input_ids = input_ids.cuda()

    start_time = time.time()
    if getattr(model, "is_mock", False):
        # Mock mode
        out_ids = model.generate(input_ids, max_new_tokens=max_new_tokens)
        decoded = (
            "```diff\n"
            "diff --git a/src/marshmallow/schema.py b/src/marshmallow/schema.py\n"
            "--- a/src/marshmallow/schema.py\n"
            "+++ b/src/marshmallow/schema.py\n"
            "@@ -892,3 +892,5 @@ def _invoke_field_validators(self, unmarshal, data, many):\n"
            "+            if data is None:\n"
            "+                return\n"
            "```"
        )
    else:
        with torch.no_grad():
            out_ids = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=(temperature > 0.0),
                temperature=temperature if temperature > 0.0 else None
            )
        new_ids = out_ids[0][input_ids.shape[1]:]
        decoded = processor.decode(new_ids, skip_special_tokens=True)

    elapsed = time.time() - start_time
    gen_tokens = out_ids.shape[1] - input_ids.shape[1]

    result = {
        "test_label": test_label,
        "prompt": prompt,
        "input_tokens": int(input_ids.shape[1]),
        "generated_tokens": int(gen_tokens),
        "latency_sec": round(elapsed, 3),
        "tokens_per_sec": round(gen_tokens / max(elapsed, 1e-4), 2),
        "sample_output": decoded[:200]
    }
    print(f"Input tokens: {result['input_tokens']} | Generated tokens: {result['generated_tokens']} | Latency: {result['latency_sec']}s")
    print(f"Output preview: {repr(result['sample_output'])}")
    return result
