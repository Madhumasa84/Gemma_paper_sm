"""Verify completeness, control outcomes, artifacts, and denominator accounting."""
import hashlib
import json
import re
from pathlib import Path

from swebench.harness.grading import get_logs_eval, test_passed
from swebench.harness.test_spec.test_spec import make_test_spec

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent


def main():
    result = json.loads((WORKSPACE / 'combined_results.json').read_text())
    assert result['harness_version'] == '4.1.0'
    assert len(result['rows']) == 12
    assert len({(r['instance_id'], r['condition']) for r in result['rows']}) == 12
    assert len({r['config_hash'] for r in result['rows']}) == 1
    assert all(p['passed'] for p in result['preflights'].values())
    for task, preflight in result['preflights'].items():
        if preflight.get('reused'):
            continue
        instance = json.loads((ROOT / 'evaluator_only' / task / 'instance.json').read_text())
        info = result['dataset']['instances'][task]
        spec = make_test_spec(instance, namespace='swebench', instance_image_tag=info['instance_image_tag'])
        base = WORKSPACE / preflight['base_log_dir']
        reference = WORKSPACE / preflight['reference_log_dir']
        b, bok = get_logs_eval(spec, base / 'test_output.txt')
        g, gok = get_logs_eval(spec, reference / 'test_output.txt')
        assert bok and gok
        assert all(b.get(t) == 'FAILED' for t in spec.FAIL_TO_PASS)
        assert all(test_passed(t, b) for t in spec.PASS_TO_PASS)
        assert all(test_passed(t, g) for t in spec.FAIL_TO_PASS + spec.PASS_TO_PASS)
        assert json.loads((reference / 'report.json').read_text())[task]['resolved']
        assert (base / 'eval.sh').read_bytes() == (reference / 'eval.sh').read_bytes() == spec.eval_script.encode()
        assert json.loads((base / 'base_verification.json').read_text())['tracked_tree_identical']
    for row in result['rows']:
        assert hashlib.sha256((WORKSPACE / row['source_checkpoint']).read_bytes()).hexdigest() == row['source_checkpoint_sha256']
        assert hashlib.sha256((WORKSPACE / row['normalized_prediction_path']).read_bytes()).hexdigest() == row['normalized_prediction_sha256']
        assert not row['infrastructure_error'], row
        assert not row['truncated'] and row['finish_reason'] == 'stop'
        if row['tested']:
            assert row['application_outcome'] == 'APPLIED_NORMALIZED'
            assert row['F2P']['total'] == row['expected_F2P']
            assert row['P2P']['total'] == row['expected_P2P']
            assert row['resolved'] == (row['F2P']['failed'] == row['P2P']['failed'] == 0)
            for key in ('report', 'test_output', 'harness_log'):
                assert row['paths'][key] and (WORKSPACE / row['paths'][key]).is_file()
            report = json.loads((WORKSPACE / row['paths']['report']).read_text())[row['instance_id']]
            assert report['resolved'] == row['resolved']
        else:
            assert row['resolved'] is None and row['F2P'] is None and row['P2P'] is None
            assert row['application_outcome'] == 'PATCH_NOT_APPLICABLE'
            assert not row.get('evaluation_command')
    for condition, values in result['per_condition'].items():
        group = [r for r in result['rows'] if r['condition'] == condition]
        assert len(group) == values['total_tasks'] == 3
        assert values['resolved'] == sum(r['resolved'] is True for r in group)
        assert values['applied'] == sum(r['patch_applied_in_processing'] for r in group)
        assert values['tested'] == sum(r['tested'] for r in group)
    assert all(i['repaired_and_preflight_validated'] for i in result['infrastructure_incidents'])
    for target in re.findall(r'\]\(([^)]+)\)', (WORKSPACE / 'combined_results.md').read_text()):
        if target == 'evaluation_evidence.zip':
            continue  # This verification is included in the package built next.
        assert (WORKSPACE / target).exists(), target
    print(json.dumps({'verified': True, 'overall': result['overall'], 'per_condition': result['per_condition'],
                      'preflights_passed': list(result['preflights']),
                      'resolved_infrastructure_incidents': len(result['infrastructure_incidents'])}, indent=2))


if __name__ == '__main__':
    main()
