"""Independent official base/reference validation for one dataset task."""
import argparse
import hashlib
import importlib.metadata
import json
import sys
import traceback
from pathlib import Path, PurePosixPath

import docker
from swebench.harness.constants import DOCKER_WORKDIR, RUN_EVALUATION_LOG_DIR
from swebench.harness.docker_build import build_container, close_logger, setup_logger
from swebench.harness.docker_utils import cleanup_container, copy_to_container, exec_run_with_timeout
from swebench.harness.grading import get_eval_report, get_logs_eval, test_passed
from swebench.harness.run_evaluation import run_instance
from swebench.harness.test_spec.test_spec import make_test_spec

ROOT = Path(__file__).resolve().parent


def main(task):
    assert importlib.metadata.version('swebench') == '4.1.0'
    private = ROOT / 'evaluator_only' / task
    row = json.loads((private / 'instance.json').read_text())
    info = json.loads((ROOT / 'dataset_metadata.json').read_text())['instances'][task]
    spec = make_test_spec(row, namespace='swebench', instance_image_tag=info.get('instance_image_tag', 'latest'))
    client = docker.from_env(timeout=1800)
    image = client.images.get(spec.instance_image_key)
    (private / 'image_metadata.json').write_text(json.dumps(image.attrs, indent=2))
    image_hash = image.id.split(':')[-1][:12]
    base_id = 'pilot2_base_' + task + '_' + row['base_commit'][:12] + '_env' + image_hash
    base_dir = RUN_EVALUATION_LOG_DIR / base_id / 'unmodified_base' / task
    base_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger(task, base_dir / 'run_instance.log')
    container = None
    outcome = {'instance_id': task, 'base_commit': row['base_commit'], 'image': spec.instance_image_key,
               'image_id': image.id, 'base_run_id': base_id, 'base_log_dir': str(base_dir), 'passed': False,
               'command': [sys.executable, *sys.argv]}
    try:
        try:
            container = build_container(spec, client, base_id, logger, False, False)
            container.start()

            def git(command):
                value = container.exec_run('git ' + command, workdir=DOCKER_WORKDIR)
                logger.info('git %s: exit=%s\n%s', command, value.exit_code, value.output.decode(errors='replace'))
                assert value.exit_code == 0, value.output
                return value.output.decode().strip()

            head = git('rev-parse HEAD')
            base_tree = git('rev-parse ' + row['base_commit'] + '^{tree}')
            head_tree = git('rev-parse HEAD^{tree}')
            assert base_tree == head_tree, 'Image tree differs from expected base'
            assert not git('status --porcelain'), 'Dirty image checkout'
            verification = dict(image_head=head, expected_base_commit=row['base_commit'],
                                base_tree=base_tree, head_tree=head_tree, tracked_tree_identical=True, clean_worktree=True)
            (base_dir / 'base_verification.json').write_text(json.dumps(verification, indent=2))
            deps = container.exec_run(['/bin/bash', '-c', 'source /opt/miniconda3/bin/activate && conda activate testbed && python --version && python -m pip freeze'])
            (private / 'container_dependencies.txt').write_bytes(deps.output)
            eval_file = base_dir / 'eval.sh'
            eval_file.write_text(spec.eval_script)
            logger.info('Applying no model patch; executing exact official script /bin/bash /eval.sh')
            copy_to_container(container, eval_file, PurePosixPath('/eval.sh'))
            output, timed_out, runtime = exec_run_with_timeout(container, '/bin/bash /eval.sh', 1800)
            (base_dir / 'test_output.txt').write_text(output)
            logger.info('Tests finished: timed_out=%s runtime=%s', timed_out, runtime)
            assert not timed_out, 'BASE_TEST_TIMEOUT'
            pred = dict(instance_id=task, model_name_or_path='unmodified_base', model_patch='')
            report = get_eval_report(spec, pred, base_dir / 'test_output.txt', include_tests_status=True)
            report[task]['baseline_no_model_patch'] = True
            (base_dir / 'report.json').write_text(json.dumps(report, indent=2))
            statuses, markers = get_logs_eval(spec, base_dir / 'test_output.txt')
            (base_dir / 'parsed_test_status.json').write_text(json.dumps(statuses, indent=2))
            assert markers and all(statuses.get(t) == 'FAILED' for t in spec.FAIL_TO_PASS), {t: statuses.get(t) for t in spec.FAIL_TO_PASS}
            assert all(test_passed(t, statuses) for t in spec.PASS_TO_PASS), {t: statuses.get(t) for t in spec.PASS_TO_PASS if not test_passed(t, statuses)}
            outcome['base_regressions_failed'] = True
            print(task, 'BASE VALIDATED', flush=True)
        except Exception:
            logger.error(traceback.format_exc())
            raise
        finally:
            cleanup_container(client, container, logger)
            close_logger(logger)

        gold_id = 'pilot2_reference_' + task + '_' + hashlib.sha256(row['patch'].encode()).hexdigest()[:12] + '_env' + image_hash
        pred = dict(instance_id=task, model_name_or_path='reference_evaluator_only', model_patch=row['patch'])
        gold_dir = RUN_EVALUATION_LOG_DIR / gold_id / pred['model_name_or_path'] / task
        outcome.update(reference_run_id=gold_id, reference_log_dir=str(gold_dir))
        run_instance(spec, pred, False, False, client, gold_id, timeout=1800)
        assert (gold_dir / 'report.json').exists(), 'Reference produced no report; see run_instance.log'
        report = json.loads((gold_dir / 'report.json').read_text())
        statuses, markers = get_logs_eval(spec, gold_dir / 'test_output.txt')
        (gold_dir / 'parsed_test_status.json').write_text(json.dumps(statuses, indent=2))
        assert report[task]['resolved'] is True and markers, report
        assert all(test_passed(t, statuses) for t in spec.FAIL_TO_PASS + spec.PASS_TO_PASS), statuses
        assert (base_dir / 'eval.sh').read_bytes() == (gold_dir / 'eval.sh').read_bytes() == spec.eval_script.encode()
        outcome.update(reference_resolved=True, same_eval_script=True, passed=True)
        print(task, 'REFERENCE VALIDATED', flush=True)
    except Exception:
        outcome['error'] = traceback.format_exc()
        raise
    finally:
        (private / 'preflight_outcome.json').write_text(json.dumps(outcome, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('instance_id', choices=('pvlib__pvlib-python-1072', 'pydicom__pydicom-1139'))
    main(parser.parse_args().instance_id)
