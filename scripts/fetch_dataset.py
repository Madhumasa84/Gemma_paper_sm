#!/usr/bin/env python3
"""Download and authenticate the evaluator-only, pinned SWE-bench Lite dev split."""
import hashlib
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
REVISION = "6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2"
URL = f"https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite/resolve/{REVISION}/data/dev-00000-of-00001.parquet"
SHA256 = "8312f321838051849d2fa7c6ca071244733a3e90bb517ff6ca8186f722199b5c"
TARGET = ROOT / "data" / "swebench_lite_dev.parquet"


def main():
    if TARGET.exists():
        data = TARGET.read_bytes()
    else:
        with urlopen(URL, timeout=60) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise SystemExit("Dataset SHA-256 mismatch; refusing to use these bytes.")
    if not TARGET.exists():
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_bytes(data)
    print(f"Verified pinned development split: {TARGET}")


if __name__ == "__main__":
    main()
