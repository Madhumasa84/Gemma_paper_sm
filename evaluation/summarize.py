import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path

from swebench.harness.grading import get_logs_eval
from swebench.harness.constants import RUN_EVALUATION_LOG_DIR
from swebench.harness.test_spec.test_spec import make_test_spec

root = Path(__file__).resolve().parent
workspace = root.parent
inventory = json.loads((root / 'input_inventory.json').read_text())
dataset = json.loads((root / 'dataset_metadata.json').read_text())
instance = json.loads((root / 'evaluator_only/instance.json').read_text())
spec = make_test_spec(instance, namespace='swebench')
commands = json.loads((root / 'commands.json').read_text()) if (root / 'commands.json').exists() else []

def summarize_log(directory, condition, baseline=False):
    directory = Path(directory)
    paths = {key: str(directory / filename) for key, filename in {
        'report': 'report.json', 'test_output': 'test_output.txt',
        'harness_log': 'run_instance.log', 'evaluation_script': 'eval.sh'
    }.items()}
    report_path = workspace / paths['report']
    log_path = workspace / paths['harness_log']
    text = log_path.read_text() if log_path.exists() else ''
    row = dict(condition=condition, patch_applied=False if baseline else None,
               tests_executed=False, resolved=None, fail_to_pass=None,
               pass_to_pass=None, error_category=None,
               paths={k: v if (workspace / v).exists() else None for k, v in paths.items()})
    if '>>>>> Applied Patch' in text or 'Applied Patch' in text:
        row['patch_applied'] = not baseline
    if report_path.exists():
        report = json.loads(report_path.read_text())[instance['instance_id']]
        row['resolved'] = report['resolved']
        if not baseline:
            row['patch_applied'] = report.get('patch_successfully_applied', False)
        statuses, markers = get_logs_eval(spec, workspace / paths['test_output'])
        row['tests_executed'] = markers and bool(statuses)
        row['observed_regression_status'] = {t: statuses.get(t, 'NOT_OBSERVED') for t in spec.FAIL_TO_PASS}
        for key, field in [('FAIL_TO_PASS', 'fail_to_pass'), ('PASS_TO_PASS', 'pass_to_pass')]:
            value = report.get('tests_status', {}).get(key)
            if value is not None:
                row[field] = dict(passed=len(value['success']), failed=len(value['failure']),
                                  total=len(value['success']) + len(value['failure']), **value)
        if not row['tests_executed']:
            row['error_category'] = 'TEST_INFRASTRUCTURE_ERROR'
            row['resolved'] = None
        elif not row['resolved']:
            row['error_category'] = 'UNRESOLVED'
    elif 'timed out' in text.lower():
        row['error_category'] = 'TIMEOUT'
    elif 'patch apply failed' in text.lower() or 'applied patch failed' in text.lower():
        row['error_category'] = 'PATCH_APPLY_ERROR'
    else:
        row['error_category'] = 'DOCKER_OR_HARNESS_ERROR'
    return row

preflight_file = root / 'preflight_passed.json'
preflight = json.loads(preflight_file.read_text()) if preflight_file.exists() else {}
preflight_results = []
if preflight:
    preflight_results = [summarize_log(preflight['base_log_dir'], 'BASE', baseline=True),
                         summarize_log(preflight['reference_log_dir'], 'REFERENCE')]
    preflight_results[0]['error_category'] = None  # Expected failure of target regression.
conditions = []
for condition in 'WABC':
    command = next((c for c in commands if c['condition'] == condition), None)
    if command:
        model = inventory['predictions'][condition]['model_name_or_path'].replace('/', '__')
        directory = RUN_EVALUATION_LOG_DIR / command['run_id'] / model / instance['instance_id']
        result = summarize_log(directory, condition)
        summary_path = workspace / f'{model}.{command["run_id"]}.json'
        if summary_path.exists():
            result['paths']['run_summary'] = str(summary_path.relative_to(workspace))
            result['run_summary'] = json.loads(summary_path.read_text())
        result['command'] = command
        if result['paths']['evaluation_script']:
            actual = (workspace / result['paths']['evaluation_script']).read_bytes()
            assert actual == spec.eval_script.encode(), condition
        if result['patch_applied']:
            actual = (workspace / directory / 'patch.diff').read_bytes()
            assert hashlib.sha256(actual).hexdigest() == inventory['predictions'][condition]['patch_sha256']
    else:
        result = dict(condition=condition, patch_applied=False if condition == 'C' else None,
                      tests_executed=False, resolved=None, fail_to_pass=None, pass_to_pass=None,
                      error_category='PATCH_NOT_APPLICABLE' if condition == 'C' else 'NOT_EXECUTED', paths={})
    result['prediction'] = inventory['predictions'][condition]
    conditions.append(result)

for path, expected in inventory['files'].items():
    assert hashlib.sha256((workspace / path).read_bytes()).hexdigest() == expected['sha256'], path
versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
output = dict(created_at=datetime.now(timezone.utc).isoformat(),
              instance_id=instance['instance_id'], dataset=dataset,
              requested_harness_version='5.0.1', actual_harness_version=importlib.metadata.version('swebench'),
              harness_version_discrepancy="5.0.1 installs, but is incompatible with this dataset schema: make_test_spec raises KeyError: 'image'; official 4.1.0 used in separate isolated environment.",
              dependency_versions=versions, archive_audit='evaluation/archive_audit.json',
              input_inventory='evaluation/input_inventory.json', originals_unchanged=True,
              preflight_passed=bool(preflight), preflight=preflight_results,
              conditions=conditions, commands=commands,
              setup_logs={p.name: str(p.relative_to(workspace)) for p in (root / 'logs').iterdir() if p.is_file()})
output['image_metadata'] = json.loads((root / 'logs/image-inspect.json').read_text())
if preflight:
    output['base_verification'] = json.loads((workspace / preflight['base_log_dir'] / 'base_verification.json').read_text())
(workspace / 'results.json').write_text(json.dumps(output, indent=2))

def count(value):
    return f"{value['passed']}/{value['total']} passed" if value else 'Not executed'

def display(value):
    return 'Not evaluated' if value is None else ('Yes' if value else 'No')

lines = ['# Independent Gemma pilot evaluation', '',
         f"Task: `{instance['instance_id']}`. Dataset: `{dataset['dataset_name']}`, split `dev`.",
         f"Base commit verified: `{dataset['base_commit']}`.", '',
         '| Condition | Patch applied | Tests executed | Resolved | Fail-to-pass results | Pass-to-pass results | Error category |',
         '|---|---|---|---|---|---|---|']
for row in preflight_results + conditions:
    lines.append(f"| {row['condition']} | {display(row['patch_applied'])} | {display(row['tests_executed'])} | {display(row['resolved'])} | {count(row['fail_to_pass'])} | {count(row['pass_to_pass'])} | {row['error_category'] or 'None'} |")
lines += ['', 'Base regression failure is expected and validates the evaluator. C has no applicable patch and was never submitted to the harness; it is not a tested baseline or a model test failure.', '',
          '## Evaluator validation', '',
          f"Preflight passed: **{bool(preflight)}**. The base run verified the requested base tree and a clean worktree, applied no model patch, and directly executed the exact official evaluation script. The reference run used the dataset reference patch. Both used the same image and identical evaluation script; every saved prediction used that script too.", '',
          "The official image adds an empty SWE-bench setup commit (`d4f98233971ee3e73bba47026cd77b4ba69a25bb`) whose parent is the expected base. Both commits have identical tree `a38157586804d01a22947322408a8a2a09b39bce`. An initial strict HEAD check stopped before testing; this was investigated and corrected to verify tree equivalence. Evidence: [image setup](evaluation/logs/image-base-investigation.txt), [base comparison](evaluation/logs/base-equivalence.log), [initial check](evaluation/logs/preflight-initial-head-check.log). The baseline grader's `patch_successfully_applied` field indicates test log markers; `baseline_no_model_patch=true` explicitly records that no model patch was applied.", '',
          'Reference patch and tests are stored in `evaluation/evaluator_only/`, separate from the preserved solver outputs. No model was loaded and no prediction was regenerated or edited.', '',
          '## Versions and provenance', '',
          output['harness_version_discrepancy'], '',
          f"Python: {dataset['python']}; architecture: {dataset['architecture']}. Dataset revision: `{dataset['revision']}`; dev fingerprint: `{dataset['fingerprint']}`; {dataset['rows']} rows. Prediction runs loaded this verified cache in offline mode.", '',
          'The ZIP passed CRC/path/symlink checks and was extracted separately into `evaluation/archive_verified/`. All 21 archived files match the supplied directory. All original files remain byte-for-byte unchanged.', '',
          'Environment: [resources](evaluation/logs/environment.txt), [Docker version](evaluation/logs/docker-version.txt), [Docker daemon](evaluation/logs/docker-info.txt).',
          'Dependencies: [5.0.1](evaluation/logs/dependencies.txt), [4.1.0](evaluation/logs/dependencies-legacy.txt). Both isolated environments passed `pip check`.',
          'Test container dependencies: [Python and pip freeze](evaluation/logs/container-dependencies.txt). Image and immutable digest: [image inspection](evaluation/logs/image-inspect.json).',
          'The 4.1.0 harness writes run summaries in the working directory despite accepting `--report_dir`; the actual summary paths are linked below.',
          'Harness help: [5.0.1](evaluation/logs/harness-help.txt), [4.1.0](evaluation/logs/harness-help-legacy.txt).',
          'Official documentation: https://www.swebench.com/SWE-bench/guides/evaluation/ (saved at `evaluation/logs/official-evaluation-docs.html`).',
          'Hashes: [prediction and original files](evaluation/input_inventory.json), [ZIP and archive comparisons](evaluation/archive_audit.json).', '',
          '| Condition | Prediction file SHA-256 |', '|---|---|']
for condition in 'WABC':
    lines.append(f"| {condition} | `{inventory['predictions'][condition]['sha256']}` |")
lines += ['', '## Commands', '', 'Run from `/home/masa84/gemma-pilot-evaluation`.', '', '```bash',
          'python3 -m venv evaluation/.venv',
          'evaluation/.venv/bin/python -m pip index versions swebench',
          'evaluation/.venv/bin/python -m pip install swebench==5.0.1',
          'evaluation/.venv/bin/python -m swebench.harness.run_evaluation --help',
          'HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv/bin/python evaluation/prepare.py',
          "# Above command records the dataset, then fails with KeyError: 'image' under 5.0.1.",
          'python3 -m venv --system-site-packages evaluation/.venv-legacy',
          "sed -i 's/include-system-site-packages = true/include-system-site-packages = false/' evaluation/.venv-legacy/pyvenv.cfg",
          '# Installation was repeated after disabling system packages to populate all isolated dependencies.',
          'evaluation/.venv-legacy/bin/python -m pip install swebench==4.1.0',
          'evaluation/.venv-legacy/bin/python -m pip check',
          'evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --help',
          'docker pull swebench/sweb.eval.x86_64.marshmallow-code_1776_marshmallow-1343:latest',
          'HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv-legacy/bin/python evaluation/preflight.py',
          '# preflight.py calls the official base eval script directly, then run_instance for reference.',
          'HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv-legacy/bin/python evaluation/verify_preflight.py',
          '# Original verification retried after locating 4.1.0 logs under logs/run_evaluation.',
          'export HF_HOME="$PWD/evaluation/hf_cache" HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1']
lines.extend(c['command'] for c in commands)
lines += ['```', '', 'The complete argument arrays, process exit codes, test identities, dependency versions, and artifact paths are in [results.json](results.json). Resolution is taken from reports and observed test outcomes, never process exit codes.', '', '## Reports and logs', '']
for row in preflight_results + conditions:
    lines.append(f"- **{row['condition']}**: " + (', '.join(f'[{key}]({path})' for key, path in row['paths'].items() if path) or 'No execution artifacts.'))
    if row.get('command'):
        lines.append(f"  Console: [{row['command']['stdout_stderr']}]({row['command']['stdout_stderr']}).")
lines += ['', 'Setup/preflight: [installation](evaluation/logs/install.log), [legacy installation](evaluation/logs/install-legacy.log), [5.0.1 incompatibility](evaluation/logs/prepare.log), [image pull](evaluation/logs/image-pull.log), [preflight console](evaluation/logs/preflight.log), [final preflight verification](evaluation/logs/preflight-verify.log).', '',
          'The first post-reference log lookup used the newer harness log directory and raised FileNotFoundError after reference tests had completed successfully. The path was corrected to `logs/run_evaluation`; the final verification independently parsed both existing test logs and checked their reports and identical scripts. No model result was inferred from that orchestration error.', '']
(workspace / 'results.md').write_text('\n'.join(lines))
print(json.dumps({'preflight_passed': bool(preflight), 'conditions': conditions}, indent=2))
