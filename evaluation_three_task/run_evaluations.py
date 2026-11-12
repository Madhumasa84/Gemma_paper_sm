"""Evaluate applicable immutable predictions, independently gated per task."""
import hashlib
import argparse
import importlib.metadata
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from datasets import load_dataset

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent


def main(tasks=None):
    os.chdir(WORKSPACE)
    assert importlib.metadata.version('swebench') == '4.1.0'
    metadata = json.loads((ROOT / 'dataset_metadata.json').read_text())
    dataset = load_dataset(metadata['dataset_name'], split=metadata['split'])
    assert dataset._fingerprint == metadata['fingerprint']
    records = json.loads((ROOT / 'processing_manifest.json').read_text())
    assert len(records) == 8
    commands = json.loads((ROOT / 'commands.json').read_text()) if (ROOT / 'commands.json').exists() else []

    def run(argv, path, **fields):
        record = dict(fields, argv=argv, command=shlex.join(argv), console_log=str(path.relative_to(WORKSPACE)),
                      environment={k: os.environ.get(k) for k in ('HF_HOME', 'HF_HUB_OFFLINE', 'HF_DATASETS_OFFLINE')})
        commands.append(record)
        (ROOT / 'commands.json').write_text(json.dumps(commands, indent=2))
        print('RUN:', record['command'], flush=True)
        with path.open('w') as log:
            result = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
        record['process_exit_code'] = result.returncode
        (ROOT / 'commands.json').write_text(json.dumps(commands, indent=2))
        print('FINISHED:', fields, 'exit=', result.returncode, flush=True)
        return result.returncode

    for task in tasks or metadata['instances']:
        preflight = [sys.executable, 'evaluation_three_task/preflight.py', task]
        tag = metadata['instances'][task].get('instance_image_tag', 'latest')
        code = run(preflight, ROOT / 'logs' / (task + '-' + tag + '-preflight.log'), instance_id=task, phase='preflight')
        path = ROOT / 'evaluator_only' / task / 'preflight_outcome.json'
        if code or not path.exists() or not json.loads(path.read_text())['passed']:
            print('PREFLIGHT BLOCKED:', task, '; no predictions interpreted for this task', flush=True)
            continue
        for item in [r for r in records if r['instance_id'] == task]:
            if item['application_outcome'] != 'APPLIED_NORMALIZED':
                print('NO TEST RUN:', task, item['condition'], item['application_outcome'], flush=True)
                continue
            prediction = WORKSPACE / item['normalized_prediction_path']
            assert hashlib.sha256(prediction.read_bytes()).hexdigest() == item['normalized_prediction_sha256']
            source = WORKSPACE / item['source_checkpoint']
            assert hashlib.sha256(source.read_bytes()).hexdigest() == item['source_checkpoint_sha256']
            run_id = f'pilot2_{task}_{item["condition"]}_{item["normalized_prediction_sha256"][:16]}'
            run_id += '_env' + json.loads(path.read_text())['image_id'].split(':')[-1][:12]
            command = [sys.executable, '-m', 'swebench.harness.run_evaluation',
                       '--dataset_name', metadata['dataset_name'], '--split', metadata['split'],
                       '--instance_ids', task, '--max_workers', '1',
                       '--predictions_path', item['normalized_prediction_path'],
                       '--run_id', run_id, '--cache_level', 'instance', '--timeout', '1800']
            if tag != 'latest':
                command.extend(['--instance_image_tag', tag])
            run(command, ROOT / 'logs' / (run_id + '.log'), instance_id=task,
                condition=item['condition'], phase='prediction', run_id=run_id,
                normalized_prediction_sha256=item['normalized_prediction_sha256'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tasks', nargs='*', choices=('pvlib__pvlib-python-1072', 'pydicom__pydicom-1139'))
    main(parser.parse_args().tasks)
