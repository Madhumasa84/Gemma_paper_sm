"""Combine all twelve checkpoints with observed evaluator reports and provenance."""
import hashlib
import importlib.metadata
import json
from datetime import datetime, timezone
from pathlib import Path

from swebench.harness.constants import RUN_EVALUATION_LOG_DIR
from swebench.harness.grading import get_logs_eval
from swebench.harness.test_spec.test_spec import make_test_spec

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
MARSHMALLOW = 'marshmallow-code__marshmallow-1343'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def relative(path):
    return str(Path(path).relative_to(WORKSPACE))


def counts(report):
    return {key: dict(passed=len(value['success']), failed=len(value['failure']),
                      total=len(value['success']) + len(value['failure']), **value)
            for key, value in report.get('tests_status', {}).items() if key in ('FAIL_TO_PASS', 'PASS_TO_PASS')}


def main():
    assert importlib.metadata.version('swebench') == '4.1.0'
    inputs = read(ROOT / 'input_manifest.json')
    assert all(c['byte_identical'] for c in inputs['marshmallow_comparisons'])
    frozen = read(WORKSPACE / 'archives/marshmallow_completed_manifest.json')
    for filename, expected in frozen['files'].items():
        assert sha(WORKSPACE / filename) == expected, f'Completed artifact changed: {filename}'
    for member in inputs['members']:
        assert sha(WORKSPACE / member['path']) == member['sha256']
    old = read(WORKSPACE / 'results.json')
    metadata = read(ROOT / 'dataset_metadata.json')
    processing = read(ROOT / 'processing_manifest.json')
    commands = read(ROOT / 'commands.json') if (ROOT / 'commands.json').exists() else []
    preflights = {MARSHMALLOW: {'passed': old['preflight_passed'], 'reused': True, 'controls': old['preflight'],
                              'base_verification': old['base_verification']}}
    incidents = []
    for task in metadata['instances']:
        path = ROOT / 'evaluator_only' / task / 'preflight_outcome.json'
        outcome = read(path) if path.exists() else {'passed': False, 'error': 'Preflight not executed'}
        outcome['outcome_path'] = relative(path) if path.exists() else None
        for key in ('base_log_dir', 'reference_log_dir'):
            if outcome.get(key):
                report = WORKSPACE / outcome[key] / 'report.json'
                if report.exists():
                    outcome[key + '_counts'] = counts(read(report)[task])
        preflights[task] = outcome
        initial_path = ROOT / 'evaluator_only' / task / 'preflight_outcome.json.initial-infrastructure-attempt'
        if initial_path.exists():
            initial = read(initial_path)
            pvlib = task.startswith('pvlib')
            incidents.append(dict(instance_id=task, phase='initial_base_preflight',
                initial_outcome_path=relative(initial_path), failing_command=initial['command'],
                error=initial.get('error'), initial_test_output=str(Path(initial['base_log_dir']) / 'test_output.txt'),
                cause='NumPy 2.0 removed np.Inf, preventing historical pvlib import' if pvlib else 'pytest 8 removed nose-style setup hooks; two preservation tests had no self.tag fixture',
                repair='NumPy 1.26.4 and pandas 1.5.3 in a separate image' if pvlib else 'pytest 7.4.4 in a separate image',
                dockerfile=f'evaluation_three_task/infrastructure/{"pvlib" if pvlib else "pydicom"}/Dockerfile',
                build_log=f'evaluation_three_task/logs/{"pvlib" if pvlib else "pydicom"}-compat-image-build.log',
                repaired_and_preflight_validated=outcome['passed']))

    rows = []
    for cp in sorted(inputs['checkpoints'], key=lambda c: (list((MARSHMALLOW, *metadata['instances'])).index(c['instance_id']), 'WABC'.index(c['condition']))):
        task, condition = cp['instance_id'], cp['condition']
        checkpoint = read(WORKSPACE / cp['source_checkpoint'])
        generated = cp['token_counts']['generated_tokens']
        truncated = cp['finish_reason'] in ('length', 'max_tokens') or generated >= 2048
        source_prediction = ROOT / 'source_archive/predictions' / Path(cp['source_checkpoint']).name
        item = dict(cp, source_prediction_path=relative(source_prediction), source_prediction_sha256=sha(source_prediction),
                    truncation_status='TOKEN_LIMIT_REACHED' if truncated else 'STOP_BEFORE_TOKEN_LIMIT', truncated=truncated,
                    tested=False, resolved=None, resolution_status='NOT_EVALUATED', infrastructure_error=None,
                    error_category=None, F2P=None, P2P=None, paths={}, evaluation_reused=task == MARSHMALLOW)
        if task == MARSHMALLOW:
            previous = next(c for c in old['conditions'] if c['condition'] == condition)
            audit_path = WORKSPACE / 'marshmallow_evaluation_bundle/original_results/processing_audit_v3' / (condition + '.json')
            audit = read(audit_path)
            prediction = WORKSPACE / previous['prediction']['file']
            item.update(base_commit=old['dataset']['base_commit'],
                        extraction_outcome='SUCCESS', application_outcome='APPLIED_NORMALIZED' if audit['recount_check_passed'] else 'PATCH_NOT_APPLICABLE',
                        extraction_block_count=audit['diff_blocks_found'], application_error=audit['git_stderr'] or None,
                        processing_audit_path=relative(audit_path), normalized_prediction_path=relative(prediction),
                        normalized_prediction_sha256=sha(prediction), normalized_patch_sha256=previous['prediction']['patch_sha256'],
                        tested=previous['tests_executed'], resolved=previous['resolved'],
                        F2P=previous['fail_to_pass'], P2P=previous['pass_to_pass'],
                        error_category=previous['error_category'], paths=previous['paths'],
                        resolution_status='UNRESOLVED' if previous['tests_executed'] else 'PATCH_NOT_APPLICABLE')
            item['extracted_patch_sha256'] = hashlib.sha256(audit['extracted_patch'].encode()).hexdigest()
            item['expected_F2P'] = len(json.loads(old['dataset']['fail_to_pass']))
            item['expected_P2P'] = len(json.loads(old['dataset']['pass_to_pass']))
            item['evaluation_command'] = previous.get('command')
        else:
            processed = next(p for p in processing if p['instance_id'] == task and p['condition'] == condition)
            prediction = WORKSPACE / processed['normalized_prediction_path']
            for key in ('base_commit', 'extraction_outcome', 'application_outcome', 'normalized_prediction_path',
                        'normalized_prediction_sha256', 'normalized_patch_sha256', 'extracted_patch_sha256'):
                item[key] = processed[key]
            item['application_error'] = processed.get('application_error')
            item['extraction_block_count'] = processed['diff_blocks_found']
            item['processing_audit_path'] = relative(prediction.parent / 'audit.json')
            item['processing_commands_path'] = processed['processing_log_path']
            item['expected_F2P'] = len(metadata['instances'][task]['FAIL_TO_PASS'])
            item['expected_P2P'] = len(metadata['instances'][task]['PASS_TO_PASS'])
            assert sha(prediction) == item['normalized_prediction_sha256']
            if processed['application_outcome'] != 'APPLIED_NORMALIZED':
                item['resolution_status'] = processed['application_outcome']
                item['error_category'] = processed['application_outcome']
            elif not preflights[task]['passed']:
                item['resolution_status'] = 'BLOCKED_PREFLIGHT'
                item['infrastructure_error'] = preflights[task].get('error', 'Preflight failed')
                item['error_category'] = 'PREFLIGHT_ERROR'
            else:
                command = next((c for c in commands if c.get('phase') == 'prediction' and c['instance_id'] == task and c['condition'] == condition), None)
                item['evaluation_command'] = command
                if not command:
                    item['resolution_status'] = 'NOT_EXECUTED'
                    item['infrastructure_error'] = 'Applicable prediction has no harness invocation'
                else:
                    model = cp['model_id'].replace('/', '__')
                    folder = RUN_EVALUATION_LOG_DIR / command['run_id'] / model / task
                    for key, filename in (('report', 'report.json'), ('test_output', 'test_output.txt'), ('harness_log', 'run_instance.log'), ('eval_script', 'eval.sh'), ('applied_patch', 'patch.diff')):
                        path = WORKSPACE / folder / filename
                        item['paths'][key] = relative(path) if path.exists() else None
                    item['paths']['console_log'] = command['console_log']
                    summary = WORKSPACE / f'{model}.{command["run_id"]}.json'
                    if summary.exists():
                        item['paths']['run_summary'] = relative(summary)
                    report_path = WORKSPACE / folder / 'report.json'
                    if not report_path.exists():
                        log = WORKSPACE / folder / 'run_instance.log'
                        error = log.read_text() if log.exists() else (WORKSPACE / command['console_log']).read_text()
                        item.update(resolution_status='EXECUTION_ERROR', error_category='HARNESS_OR_DOCKER_ERROR', infrastructure_error=error)
                    else:
                        reference = read(ROOT / 'evaluator_only' / task / 'instance.json')
                        spec = make_test_spec(reference, namespace='swebench')
                        assert (WORKSPACE / folder / 'eval.sh').read_bytes() == spec.eval_script.encode()
                        assert sha(WORKSPACE / folder / 'patch.diff') == item['normalized_patch_sha256']
                        statuses, markers = get_logs_eval(spec, WORKSPACE / folder / 'test_output.txt')
                        report = read(report_path)[task]
                        item['tested'] = bool(markers and statuses)
                        item['observed_F2P'] = {t: statuses.get(t, 'NOT_OBSERVED') for t in spec.FAIL_TO_PASS}
                        item['observed_P2P'] = {t: statuses.get(t, 'NOT_OBSERVED') for t in spec.PASS_TO_PASS}
                        if not markers or any(t not in statuses for t in spec.FAIL_TO_PASS + spec.PASS_TO_PASS):
                            item.update(resolution_status='TEST_EXECUTION_ERROR_REQUIRES_REVIEW',
                                        error_category='MISSING_EXPECTED_TEST_RESULTS', infrastructure_error='Inspect test output for missing required tests')
                        else:
                            measured = counts(report)
                            item.update(resolved=report['resolved'], F2P=measured['FAIL_TO_PASS'], P2P=measured['PASS_TO_PASS'],
                                        resolution_status='RESOLVED' if report['resolved'] else 'UNRESOLVED',
                                        error_category=None if report['resolved'] else 'UNRESOLVED')
        item['patch_applied_in_processing'] = item['application_outcome'] == 'APPLIED_NORMALIZED'
        item['harness_patch_applied'] = item['tested']
        rows.append(item)
    assert len(rows) == 12 and len({(r['instance_id'], r['condition']) for r in rows}) == 12
    aggregates = {}
    for condition in 'WABC':
        group = [r for r in rows if r['condition'] == condition]
        tested = sum(r['tested'] for r in group)
        applied = sum(r['patch_applied_in_processing'] for r in group)
        resolved = sum(r['resolved'] is True for r in group)
        aggregates[condition] = dict(resolved=resolved, total_tasks=3, resolved_fraction=resolved / 3,
                                     applied=applied, application_rate=applied / 3,
                                     tested=tested, resolved_among_tested=resolved / tested if tested else None,
                                     infrastructure_errors=sum(r['infrastructure_error'] is not None for r in group))
    tested = sum(r['tested'] for r in rows)
    applied = sum(r['patch_applied_in_processing'] for r in rows)
    resolved = sum(r['resolved'] is True for r in rows)
    result = dict(created_at=datetime.now(timezone.utc).isoformat(), dataset=metadata,
                  harness_version=importlib.metadata.version('swebench'), shared_config_hash=inputs['shared_config_hash'],
                  model_id=rows[0]['model_id'], model_revision=rows[0]['model_revision'],
                  input_manifest='evaluation_three_task/input_manifest.json',
                  processing_rule='last_labelled_diff_block_plus_recount_v3',
                  processing_equivalence='evaluation_three_task/marshmallow_processing_equivalence.json',
                  original_snapshot=inputs['original_snapshot'], original_files_preserved=True,
                  marshmallow_reuse_verified=True, preflights=preflights, rows=rows, per_condition=aggregates,
                  infrastructure_incidents=incidents,
                  overall=dict(total_pairs=12, applied=applied, application_rate=applied / 12,
                               tested=tested, resolved=resolved, resolved_among_tested=resolved / tested if tested else None,
                               infrastructure_errors=sum(r['infrastructure_error'] is not None for r in rows)),
                  generation_config_provenance='Shared recorded configuration hash; all twelve checkpoints use the same model/revision. Full original configuration is not included in the archive.',
                  commands=commands, limitations='Three tasks are a descriptive pilot; no statistical significance is claimed.')
    (WORKSPACE / 'combined_results.json').write_text(json.dumps(result, indent=2))

    def rate(a, b):
        return f'{a}/{b} ({100*a/b:.1f}%)' if b else 'N/A (no tested patches)'

    def count(value):
        return f"{value['passed']}/{value['total']}" if value else 'Not executed'

    lines = ['# Combined three-task Gemma pilot evaluation', '',
             f'All 12 task/condition pairs are retained. **{resolved}/12 resolved**, {applied}/12 patches applicable, {tested} patches tested.',
             f'Overall application rate: **{rate(applied, 12)}**. Resolution among tested patches: **{rate(resolved, tested)}**.', '',
             '| Task | Condition | Generation / truncated | Application outcome | Tests executed | F2P passed | P2P passed | Resolved | Infrastructure error |',
             '|---|---|---|---|---|---|---|---|---|']
    for row in rows:
        status = 'Yes' if row['resolved'] else ('No' if row['tested'] else 'Not evaluated')
        lines.append(f"| {row['instance_id']} | {row['condition']} | {row['generation_status']} / {'Yes' if row['truncated'] else 'No'} | {row['application_outcome']} | {'Yes' if row['tested'] else 'No'} | {count(row['F2P'])} | {count(row['P2P'])} | {status} | {'Yes: ' + str(row['error_category']) if row['infrastructure_error'] else 'None'} |")
    lines += ['', 'F2P/P2P counts are passed/required. Application failures were never submitted for testing and are not executed test failures. A null resolved value means not evaluated, while the task remains in the overall denominator.', '',
              '| Condition | Tasks resolved / THREE | Application rate | Tested patches | Resolution among tested | Infrastructure errors |',
              '|---|---|---|---|---|---|']
    for condition, a in aggregates.items():
        lines.append(f"| {condition} | {a['resolved']}/3 | {rate(a['applied'], 3)} | {a['tested']} | {rate(a['resolved'], a['tested'])} | {a['infrastructure_errors']} |")
    lines += ['', 'Three tasks support descriptive pilot results only; no statistical significance is claimed.', '',
              '## Evaluator validation', '',
              'Marshmallow results were reused only after all four checkpoints matched byte-for-byte. Its completed reports, raw logs, scripts and outputs remain unchanged and are archived in [marshmallow_completed.zip](archives/marshmallow_completed.zip), with [SHA-256 manifest](archives/marshmallow_completed_manifest.json).', '']
    for task, outcome in preflights.items():
        lines.append(f"- `{task}`: preflight **{'PASSED' if outcome['passed'] else 'FAILED / BLOCKED'}**" + (' (verified prior evaluation reused).' if task == MARSHMALLOW else '.'))
        if task != MARSHMALLOW:
            for key in ('base_log_dir', 'reference_log_dir'):
                if outcome.get(key):
                    for filename in ('report.json', 'test_output.txt', 'run_instance.log', 'eval.sh'):
                        path = Path(outcome[key]) / filename
                        if (WORKSPACE / path).exists():
                            lines.append(f'  [{key}/{filename}]({path})')
            if outcome.get('error'):
                lines += ['', '```text', outcome['error'], '```', '']
    lines += ['', 'Base controls execute the exact official evaluation script without a model patch; an empty skipped prediction is never used as baseline. Every base verifies a clean tree identical to the dataset base. Reference controls must resolve all F2P tests and preserve all P2P tests before any model prediction for that task is interpreted. Gold patches/tests are stored only under evaluator-only directories.', '',
              '## Infrastructure incidents', '',
              'Initial controls exposed two historical dependency incompatibilities. These attempts are infrastructure failures, not model failures. Their original logs/reports remain preserved. Final per-pair infrastructure fields describe the validated evaluation attempts.', '']
    for incident in incidents:
        lines += [f"- `{incident['instance_id']}`: {incident['cause']}. Repair: {incident['repair']}. Revalidated: **{incident['repaired_and_preflight_validated']}**.",
                  f"  [Initial failing test log]({incident['initial_test_output']}), [initial outcome]({incident['initial_outcome_path']}), [Dockerfile]({incident['dockerfile']}), [build log]({incident['build_log']})."]
    lines += ['', '## Processing and provenance', '',
              f"Dataset: `{metadata['dataset_name']}`, split `{metadata['split']}`, revision `{metadata['revision']}`, fingerprint `{metadata['fingerprint']}`. SWE-bench **4.1.0**, existing isolated environment `evaluation/.venv-legacy`.",
              f"Model: `{result['model_id']}`, revision `{result['model_revision']}`. Shared recorded configuration hash: `{inputs['shared_config_hash']}`. All generations reported `stop` below the 2,048 output-token cap; no model was loaded or response regenerated.", '',
              'The supplied archive contains recorded hashes rather than the complete generation configuration or prompt text. Shared hashes and revisions were verified; the prior experiment settings were not changed or reconstructed.', '',
              'The last explicitly labelled `diff`/`patch` fenced block was selected; whitespace was preserved and a final newline ensured. `git apply --recount --check` followed by `git apply --recount` ran in an isolated temporary checkout at the task base. The canonical staged Git diff was exported; added/removed lines were verified unchanged. No source context, missing lines or patch logic were repaired, and no patch was selected using test performance.', '',
              '[Input archive audit and source hashes](evaluation_three_task/input_manifest.json), [processing manifest](evaluation_three_task/processing_manifest.json), [exact Marshmallow extraction equivalence](evaluation_three_task/marshmallow_processing_equivalence.json), [dataset bases](evaluation_three_task/dataset_metadata.json).', '',
              '## Per-pair artifacts and hashes', '']
    for row in rows:
        lines += [f"### {row['instance_id']} / {row['condition']}", '',
                  f"Source checkpoint SHA-256: `{row['source_checkpoint_sha256']}`.",
                  f"Raw generation SHA-256: `{row['raw_generation_sha256']}`.",
                  f"Normalized prediction SHA-256: `{row['normalized_prediction_sha256']}`.",
                  f"Normalized patch SHA-256: `{row['normalized_patch_sha256']}`.",
                  f"[Source checkpoint]({row['source_checkpoint']}), [original prediction JSON]({row['source_prediction_path']}), [normalized prediction]({row['normalized_prediction_path']}), [processing audit]({row['processing_audit_path']})."]
        if row.get('application_error'):
            lines += ['', '```text', row['application_error'].rstrip(), '```']
        if row.get('processing_commands_path'):
            lines.append(f"[Exact processing commands]({row['processing_commands_path']}).")
        for key, path in row['paths'].items():
            if path:
                lines.append(f'[{key}]({path})')
        if row.get('evaluation_command'):
            command = row['evaluation_command']
            lines += ['', '```bash', command['command'], '```']
        lines.append('')
    lines += ['## Commands and evidence', '',
              'All new harness invocations use `--max_workers 1`, distinct task/condition/prediction-hash run IDs, the requested dataset/dev split and the verified offline cache. Their exact arguments, environment, exit codes and console paths are recorded in [commands.json](evaluation_three_task/commands.json). Process exit status alone is never treated as resolution.', '',
              'Setup: [archive preparation](evaluation_three_task/logs/prepare.log), [dataset verification](evaluation_three_task/logs/dataset.log), [processing log](evaluation_three_task/logs/processing.log), [pvlib image download](evaluation_three_task/logs/pull-pvlib.log), [pydicom image download](evaluation_three_task/logs/pull-pydicom.log).', '',
              'Entrypoints: [prepare.py](evaluation_three_task/prepare.py), [process_predictions.py](evaluation_three_task/process_predictions.py), [preflight.py](evaluation_three_task/preflight.py), [run_evaluations.py](evaluation_three_task/run_evaluations.py), [combine_results.py](evaluation_three_task/combine_results.py).', '',
              'Full structured records, generation/truncation details, per-test names, source/normalized hashes and preflight outcomes are in [combined_results.json](combined_results.json). [evaluation_evidence.zip](evaluation_evidence.zip) contains reports, raw logs, evaluation/processing scripts, predictions and manifests; virtual environments, Docker images, model weights, caches and credentials are excluded.', '']
    (WORKSPACE / 'combined_results.md').write_text('\n'.join(lines))
    print(json.dumps({'overall': result['overall'], 'per_condition': aggregates}, indent=2))


if __name__ == '__main__':
    main()
