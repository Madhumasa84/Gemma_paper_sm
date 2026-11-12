"""Verify existing control test logs without rerunning or trusting exit codes."""
import json
from pathlib import Path
from swebench.harness.grading import get_logs_eval
from swebench.harness.test_spec.test_spec import make_test_spec

row = json.load(open('evaluation/evaluator_only/instance.json'))
spec = make_test_spec(row, namespace='swebench')
base = Path('logs/evaluation/pilot_preflight_base_tree_2be2d83a1a9a/unmodified_base') / row['instance_id']
gold = Path('logs/run_evaluation/pilot_preflight_reference_fb93d3650801/reference_evaluator_only') / row['instance_id']
b, ok = get_logs_eval(spec, base / 'test_output.txt')
g, gok = get_logs_eval(spec, gold / 'test_output.txt')
assert ok and gok
assert all(b.get(t) == 'FAILED' for t in spec.FAIL_TO_PASS)
assert all(b.get(t) == 'PASSED' for t in spec.PASS_TO_PASS)
assert all(g.get(t) == 'PASSED' for t in spec.FAIL_TO_PASS + spec.PASS_TO_PASS)
assert json.load(open(gold / 'report.json'))[row['instance_id']]['resolved'] is True
assert (gold / 'eval.sh').read_bytes() == (base / 'eval.sh').read_bytes() == spec.eval_script.encode()
assert json.load(open(base / 'base_verification.json'))['tracked_tree_identical']
Path('evaluation/preflight_passed.json').write_text(json.dumps(dict(
    base_log_dir=str(base), reference_log_dir=str(gold),
    base_failed_regressions=spec.FAIL_TO_PASS, reference_resolved=True,
    same_eval_script=True, image=spec.instance_image_key), indent=2))
print('BASE AND REFERENCE PREFLIGHT VERIFIED: base F2P 0/1, P2P 24/24; reference F2P 1/1, P2P 24/24.')
