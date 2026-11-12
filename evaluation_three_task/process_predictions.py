"""Extract last labelled block and recount only, with no semantic/context repair."""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
BLOCK = re.compile(r'^```(?:diff|patch)[ \t]*\r?\n(.*?)^```[ \t]*\r?$', re.MULTILINE | re.DOTALL)


def extract(raw):
    blocks = BLOCK.findall(raw)
    if not blocks:
        return None, 0
    patch = blocks[-1]
    return patch if patch.endswith('\n') else patch + '\n', len(blocks)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((ROOT / 'input_manifest.json').read_text())
    metadata = json.loads((ROOT / 'dataset_metadata.json').read_text())
    # Exact extraction proof against all four archived Marshmallow audits.
    proofs = []
    for cp in manifest['checkpoints']:
        if cp['instance_id'] != 'marshmallow-code__marshmallow-1343':
            continue
        row = json.loads((WORKSPACE / cp['source_checkpoint']).read_text())
        audit = json.loads((WORKSPACE / 'marshmallow_evaluation_bundle/original_results/processing_audit_v3' / (cp['condition'] + '.json')).read_text())
        patch, count = extract(row['raw_generation'])
        assert patch == audit['extracted_patch'] and count == audit['diff_blocks_found']
        proofs.append({'condition': cp['condition'], 'exact_extraction_match': True, 'extracted_sha256': sha(patch.encode()), 'block_count': count})
    (ROOT / 'marshmallow_processing_equivalence.json').write_text(json.dumps(proofs, indent=2))
    env = os.environ.copy()
    env.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_TERMINAL_PROMPT='0')
    results = []
    for task, info in metadata['instances'].items():
        with tempfile.TemporaryDirectory(prefix=task + '-') as checkout:
            git_commands = []

            def git(*args):
                command = ['git', '-C', checkout, *args]
                value = subprocess.run(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                git_commands.append({'argv': command, 'exit_code': value.returncode,
                                     'stdout': value.stdout.decode(errors='replace'), 'stderr': value.stderr.decode(errors='replace')})
                return value

            assert git('init', '--quiet').returncode == 0
            value = git('fetch', '--depth', '1', 'https://github.com/' + info['repo'] + '.git', info['base_commit'])
            if value.returncode:
                (ROOT / 'logs' / (task + '-fetch.json')).write_text(json.dumps(git_commands, indent=2))
                raise RuntimeError(f'Infrastructure: git fetch {task}: {value.stderr.decode()}')
            assert git('checkout', '--detach', '--quiet', 'FETCH_HEAD').returncode == 0
            assert git('rev-parse', 'HEAD').stdout.decode().strip() == info['base_commit']
            for cp in sorted((c for c in manifest['checkpoints'] if c['instance_id'] == task), key=lambda c: 'WABC'.index(c['condition'])):
                assert git('reset', '--hard', info['base_commit']).returncode == 0
                assert git('clean', '-fdx').returncode == 0
                assert not git('status', '--porcelain').stdout
                source = WORKSPACE / cp['source_checkpoint']
                assert sha(source.read_bytes()) == cp['source_checkpoint_sha256']
                row = json.loads(source.read_text())
                out = ROOT / 'processed' / task / cp['condition']
                out.mkdir(parents=True, exist_ok=True)
                patch, count = extract(row['raw_generation'])
                audit = dict(cp, base_commit=info['base_commit'], processing_rule='last_labelled_diff_block_plus_recount_v3',
                             diff_blocks_found=count, extracted_patch_sha256=None, normalized_patch_sha256=None,
                             application_outcome=None, extraction_outcome='SUCCESS' if patch is not None else 'NO_LABELLED_DIFF_BLOCK',
                             normalized_prediction_path=None, normalized_prediction_sha256=None)
                canonical = b''
                start = len(git_commands)
                if patch is None:
                    audit['application_outcome'] = 'NOT_ATTEMPTED_EXTRACTION_FAILED'
                else:
                    extracted = out / 'extracted.diff'
                    extracted.write_bytes(patch.encode())
                    audit['extracted_patch_sha256'] = sha(extracted.read_bytes())
                    check = git('apply', '--recount', '--check', str(extracted))
                    audit['recount_check_passed'] = check.returncode == 0
                    if check.returncode:
                        audit['application_outcome'] = 'PATCH_NOT_APPLICABLE'
                        audit['application_error'] = check.stderr.decode(errors='replace')
                    else:
                        applied = git('apply', '--recount', str(extracted))
                        assert applied.returncode == 0, applied.stderr
                        assert git('add', '--all').returncode == 0
                        diff = git('-c', 'core.abbrev=8', 'diff', '--cached', '--binary', '--no-ext-diff', '--no-color', '--no-renames')
                        assert diff.returncode == 0
                        canonical = diff.stdout
                        audit['application_outcome'] = 'APPLIED_NORMALIZED' if canonical else 'APPLIED_EMPTY_DIFF'
                (out / 'normalized.diff').write_bytes(canonical)
                audit['normalized_patch_sha256'] = sha(canonical)
                prediction = {'instance_id': task, 'model_name_or_path': cp['model_id'], 'model_patch': canonical.decode()}
                prediction_path = out / 'predictions.jsonl'
                prediction_path.write_text(json.dumps(prediction, ensure_ascii=False) + '\n')
                audit['normalized_prediction_path'] = str(prediction_path.relative_to(WORKSPACE))
                audit['normalized_prediction_sha256'] = sha(prediction_path.read_bytes())
                audit['processing_log_path'] = str((out / 'processing_commands.json').relative_to(WORKSPACE))
                (out / 'processing_commands.json').write_text(json.dumps(git_commands[start:], indent=2))
                (out / 'audit.json').write_text(json.dumps(audit, indent=2))
                results.append(audit)
                (ROOT / 'processing_manifest.json').write_text(json.dumps(results, indent=2))
                print(task, cp['condition'], audit['application_outcome'], audit.get('application_error', '').strip(), flush=True)
            (ROOT / 'logs' / (task + '-checkout-commands.json')).write_text(json.dumps(git_commands, indent=2))


if __name__ == '__main__':
    main()
