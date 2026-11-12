"""Focused proof that normalization preserves patch edits and original inputs."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent


def edits(text):
    return [line for line in text.splitlines(keepends=True)
            if line.startswith(('+', '-')) and not line.startswith(('--- ', '+++ '))]


def main():
    records = json.loads((ROOT / 'processing_manifest.json').read_text())
    assert len(records) == len({(r['instance_id'], r['condition']) for r in records}) == 8
    for record in records:
        prediction = WORKSPACE / record['normalized_prediction_path']
        value = json.loads(prediction.read_text())
        assert hashlib.sha256(prediction.read_bytes()).hexdigest() == record['normalized_prediction_sha256']
        extracted = prediction.parent / 'extracted.diff'
        canonical = prediction.parent / 'normalized.diff'
        if record['application_outcome'] == 'APPLIED_NORMALIZED':
            assert edits(extracted.read_text()) == edits(canonical.read_text()), (record['instance_id'], record['condition'])
            assert value['model_patch'] == canonical.read_text() and value['model_patch']
        else:
            assert not value['model_patch'] and not canonical.read_bytes()
        commands = json.loads((prediction.parent / 'processing_commands.json').read_text())
        for command in commands:
            if 'apply' in command['argv']:
                assert '--recount' in command['argv']
                assert not any(a.startswith(('--ignore', '--reject', '--3way', '--whitespace=fix')) for a in command['argv'])
    inputs = json.loads((ROOT / 'input_manifest.json').read_text())
    for member in inputs['members']:
        assert hashlib.sha256((WORKSPACE / member['path']).read_bytes()).hexdigest() == member['sha256']
    for filename, expected in json.loads((WORKSPACE / 'archives/marshmallow_completed_manifest.json').read_text())['files'].items():
        assert hashlib.sha256((WORKSPACE / filename).read_bytes()).hexdigest() == expected
    proofs = json.loads((ROOT / 'marshmallow_processing_equivalence.json').read_text())
    assert len(proofs) == 4 and all(p['exact_extraction_match'] for p in proofs)
    print('PASS: eight records; exact Marshmallow extraction equivalence; canonical added/removed lines preserved; recount only; all archived inputs and completed Marshmallow artifacts unchanged.')


if __name__ == '__main__':
    main()
