"""Run saved, immutable predictions, gated on independently verified preflights."""
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from datasets import load_dataset

root = Path(__file__).resolve().parent
workspace = root.parent
os.chdir(workspace)
assert json.loads((root / 'preflight_passed.json').read_text())['reference_resolved']
metadata = json.loads((root / 'dataset_metadata.json').read_text())
dataset = load_dataset(metadata['dataset_name'], split='dev')
assert dataset._fingerprint == metadata['fingerprint']
inventory = json.loads((root / 'input_inventory.json').read_text())
commands = []
for condition in 'WAB':
    pred = inventory['predictions'][condition]
    path = workspace / pred['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pred['sha256']
    run_id = f'gemma_pilot_{condition}_{pred["sha256"][:16]}'
    command = [sys.executable, '-m', 'swebench.harness.run_evaluation',
               '--dataset_name', metadata['dataset_name'], '--split', 'dev',
               '--instance_ids', 'marshmallow-code__marshmallow-1343',
               '--max_workers', '1', '--predictions_path', pred['file'],
               '--run_id', run_id, '--cache_level', 'instance',
               '--timeout', '1800', '--report_dir', 'evaluation/summary_reports']
    log = root / 'logs' / f'{run_id}.log'
    record = dict(condition=condition, run_id=run_id, argv=command,
                  command=shlex.join(command), stdout_stderr=str(log.relative_to(workspace)))
    commands.append(record)
    (root / 'commands.json').write_text(json.dumps(commands, indent=2))
    print('RUN:', record['command'], flush=True)
    with log.open('w') as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT, env=os.environ.copy())
    record['process_exit_code'] = result.returncode
    (root / 'commands.json').write_text(json.dumps(commands, indent=2))
    print('FINISHED:', condition, 'exit=', result.returncode, 'inspect reports for result', flush=True)
    # A successful process exit alone is never considered a resolved prediction.
    for original, expected in inventory['files'].items():
        assert hashlib.sha256(Path(original).read_bytes()).hexdigest() == expected['sha256'], original
