import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path

from datasets import load_dataset
from huggingface_hub import HfApi
from swebench.harness.utils import make_test_spec

root = Path(__file__).resolve().parent
name = 'princeton-nlp/SWE-bench_Lite'
revision = HfApi().dataset_info(name).sha
dataset = load_dataset(name, split='dev', revision=revision)
matches = [r for r in dataset if r['instance_id'] == 'marshmallow-code__marshmallow-1343']
assert len(matches) == 1, len(matches)
row = matches[0]
assert row['base_commit'] == '2be2d83a1a9a6d3d9b85804f3ab545cecc409bb0'
private = root / 'evaluator_only'
(private / 'instance.json').write_text(json.dumps(row, indent=2))
(private / 'reference.diff').write_text(row['patch'])
(private / 'test.diff').write_text(row['test_patch'])
metadata = dict(dataset_name=name, split='dev', revision=revision,
                fingerprint=dataset._fingerprint, rows=len(dataset),
                columns=dataset.column_names, base_commit=row['base_commit'],
                reference_sha256=hashlib.sha256(row['patch'].encode()).hexdigest(),
                python=platform.python_version(), architecture=platform.machine(),
                swebench=importlib.metadata.version('swebench'),
                fail_to_pass=row['FAIL_TO_PASS'], pass_to_pass=row['PASS_TO_PASS'])
(root / 'dataset_metadata.json').write_text(json.dumps(metadata, indent=2))
print(json.dumps(metadata, indent=2), flush=True)
spec = make_test_spec(row)
(private / 'eval.sh').write_text(spec.eval_script)
(root / 'test_spec.json').write_text(json.dumps({'image': spec.image, 'eval_script': spec.eval_script}, indent=2))
print('Test spec image:', spec.image, flush=True)
