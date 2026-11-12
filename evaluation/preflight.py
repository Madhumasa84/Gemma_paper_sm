"""Execute the legacy official eval script on a pristine base, then gold patch."""
import hashlib
import json
import traceback
from pathlib import Path, PurePosixPath

import docker
from swebench.harness.constants import DOCKER_WORKDIR, RUN_EVALUATION_LOG_DIR
from swebench.harness.docker_build import build_container, close_logger, setup_logger
from swebench.harness.docker_utils import cleanup_container, copy_to_container, exec_run_with_timeout
from swebench.harness.grading import get_eval_report, get_logs_eval
from swebench.harness.run_evaluation import run_instance
from swebench.harness.test_spec.test_spec import make_test_spec

root = Path(__file__).resolve().parent
row = json.loads((root / 'evaluator_only/instance.json').read_text())
spec = make_test_spec(row, namespace='swebench')
client = docker.from_env(timeout=1800)
run_id = 'pilot_preflight_base_tree_' + row['base_commit'][:12]
log_dir = Path('logs/evaluation') / run_id / 'unmodified_base' / row['instance_id']
log_dir.mkdir(parents=True, exist_ok=True)
logger = setup_logger(row['instance_id'], log_dir / 'run_instance.log')
container = None
try:
    container = build_container(spec, client, run_id, logger, False, False)
    container.start()
    head = container.exec_run('git rev-parse HEAD', workdir=DOCKER_WORKDIR)
    status = container.exec_run('git status --porcelain', workdir=DOCKER_WORKDIR)
    logger.info('Base HEAD: %s; status: %s', head.output.decode(), status.output.decode())
    assert head.exit_code == 0
    base_tree = container.exec_run('git rev-parse ' + row['base_commit'] + '^{tree}', workdir=DOCKER_WORKDIR)
    head_tree = container.exec_run('git rev-parse HEAD^{tree}', workdir=DOCKER_WORKDIR)
    logger.info('Requested base tree: %s; image HEAD tree: %s', base_tree.output.decode(), head_tree.output.decode())
    assert base_tree.exit_code == head_tree.exit_code == 0
    assert base_tree.output == head_tree.output, 'Image tracked tree differs from requested base'
    (log_dir / 'base_verification.json').write_text(json.dumps({
        'expected_base_commit': row['base_commit'], 'image_head': head.output.decode().strip(),
        'base_tree': base_tree.output.decode().strip(), 'image_tree': head_tree.output.decode().strip(),
        'tracked_tree_identical': True, 'clean_worktree': not status.output.strip()
    }, indent=2))
    assert status.exit_code == 0 and not status.output.strip(), status.output
    eval_file = log_dir / 'eval.sh'
    eval_file.write_text(spec.eval_script)
    (root / 'evaluator_only/eval-legacy.sh').write_text(spec.eval_script)
    (root / 'test_spec-legacy.json').write_text(json.dumps({
        'image': spec.instance_image_key,
        'eval_script_sha256': hashlib.sha256(spec.eval_script.encode()).hexdigest()
    }, indent=2))
    logger.info('No model patch applied; executing exact official eval script')
    copy_to_container(container, eval_file, PurePosixPath('/eval.sh'))
    output, timed_out, runtime = exec_run_with_timeout(container, '/bin/bash /eval.sh', 1800)
    (log_dir / 'test_output.txt').write_text(output)
    assert not timed_out, 'Baseline timed out'
    pred = dict(instance_id=row['instance_id'], model_name_or_path='unmodified_base', model_patch='')
    report = get_eval_report(spec, pred, log_dir / 'test_output.txt', include_tests_status=True)
    # The grader's patch_successfully_applied flag means log markers were found;
    # explicitly record that this run intentionally applied no model patch.
    report[row['instance_id']]['baseline_no_model_patch'] = True
    (log_dir / 'report.json').write_text(json.dumps(report, indent=2))
    statuses, found = get_logs_eval(spec, log_dir / 'test_output.txt')
    (log_dir / 'parsed_test_status.json').write_text(json.dumps(statuses, indent=2))
    assert found and all(statuses.get(t) == 'FAILED' for t in spec.FAIL_TO_PASS), statuses
    assert all(statuses.get(t) == 'PASSED' for t in spec.PASS_TO_PASS), statuses
    print('BASE PREFLIGHT PASSED:', json.dumps(report), flush=True)
except Exception:
    logger.error(traceback.format_exc())
    raise
finally:
    cleanup_container(client, container, logger)
    close_logger(logger)

gold_id = 'pilot_preflight_reference_' + hashlib.sha256(row['patch'].encode()).hexdigest()[:12]
gold = dict(instance_id=row['instance_id'], model_name_or_path='reference_evaluator_only', model_patch=row['patch'])
result = run_instance(spec, gold, False, False, client, gold_id, timeout=1800)
print('Reference runner:', result, flush=True)
gold_dir = RUN_EVALUATION_LOG_DIR / gold_id / gold['model_name_or_path'] / row['instance_id']
report = json.loads((gold_dir / 'report.json').read_text())
statuses, found = get_logs_eval(spec, gold_dir / 'test_output.txt')
(gold_dir / 'parsed_test_status.json').write_text(json.dumps(statuses, indent=2))
assert report[row['instance_id']]['resolved'] is True, report
assert found and all(statuses.get(t) == 'PASSED' for t in spec.FAIL_TO_PASS + spec.PASS_TO_PASS), statuses
assert (gold_dir / 'eval.sh').read_bytes() == (log_dir / 'eval.sh').read_bytes()
(root / 'preflight_passed.json').write_text(json.dumps({
    'base_log_dir': str(log_dir), 'reference_log_dir': str(gold_dir),
    'base_failed_regressions': spec.FAIL_TO_PASS, 'reference_resolved': True,
    'same_eval_script': True, 'image': spec.instance_image_key
}, indent=2))
print('REFERENCE PREFLIGHT PASSED:', json.dumps(report), flush=True)
