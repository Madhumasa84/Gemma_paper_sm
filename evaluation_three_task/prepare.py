"""Preserve completed evaluation, safely inspect inputs, and verify provenance."""
import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
TASKS = ('marshmallow-code__marshmallow-1343', 'pvlib__pvlib-python-1072', 'pydicom__pydicom-1139')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive_dir = WORKSPACE / 'archives'
    archive_dir.mkdir(exist_ok=True)
    snapshot = archive_dir / 'marshmallow_completed.zip'
    original_files = []
    for folder in ('evaluation', 'logs', 'marshmallow_evaluation_bundle'):
        for path in (WORKSPACE / folder).rglob('*'):
            relative = path.relative_to(WORKSPACE)
            if path.is_file() and not any(p.startswith('.venv') or p in ('hf_cache', '__pycache__') for p in relative.parts):
                original_files.append(path)
    original_files += [WORKSPACE / f for f in ('results.md', 'results.json', 'marshmallow_evaluation_bundle.zip')]
    original_files += list(WORKSPACE.glob('google__gemma*.json'))
    original_manifest = {str(p.relative_to(WORKSPACE)): sha(p.read_bytes()) for p in sorted(set(original_files))}
    manifest_path = archive_dir / 'marshmallow_completed_manifest.json'
    if snapshot.exists():
        saved = json.loads(manifest_path.read_text())
        assert sha(snapshot.read_bytes()) == saved['archive_sha256']
        for filename, expected in saved['files'].items():
            assert sha((WORKSPACE / filename).read_bytes()) == expected, f'Completed artifact changed: {filename}'
    else:
        with zipfile.ZipFile(snapshot, 'x', compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(set(original_files)):
                z.write(path, path.relative_to(WORKSPACE))
        manifest_path.write_text(json.dumps({'files': original_manifest, 'archive_sha256': sha(snapshot.read_bytes())}, indent=2))

    archive = WORKSPACE / 'three_task_pilot_generations.zip'
    dest = ROOT / 'source_archive'
    members = []
    with zipfile.ZipFile(archive) as z:
        names = [i.filename for i in z.infolist()]
        assert len(names) == len(set(names)), 'Duplicate archive member'
        assert sum(i.file_size for i in z.infolist()) < 100_000_000
        for item in z.infolist():
            name = PurePosixPath(item.filename)
            assert not name.is_absolute() and '..' not in name.parts and '\\' not in item.filename
            assert not stat.S_ISLNK(item.external_attr >> 16)
            assert not item.flag_bits & 1, 'Encrypted member'
        assert z.testzip() is None, 'CRC check failed'
        for item in z.infolist():
            if item.is_dir():
                continue
            data = z.read(item)
            out = dest / item.filename
            out.parent.mkdir(parents=True, exist_ok=True)
            if out.exists():
                assert out.read_bytes() == data
            else:
                out.write_bytes(data)
            members.append({'path': str(out.relative_to(WORKSPACE)), 'bytes': len(data), 'sha256': sha(data)})

    checkpoints = []
    seen = set()
    comparisons = []
    for path in sorted((dest / 'checkpoints').glob('*.json')):
        row = json.loads(path.read_text())
        key = (row['instance_id'], row['condition'])
        assert key not in seen, f'Duplicate task/condition {key}'
        seen.add(key)
        assert row['attempt'] == 1
        assert row['model_id'] == 'google/gemma-4-E4B-it'
        assert row['model_revision'] == '4ecc2ba63bcac23ba4a767fc87025b1450f84c9c'
        record = {k: row.get(k) for k in ('instance_id', 'condition', 'attempt', 'prompt_hash', 'config_hash', 'model_id', 'model_revision', 'generation_status', 'finish_reason', 'token_counts', 'execution_mode', 'is_mock')}
        record.update(source_checkpoint=str(path.relative_to(WORKSPACE)), source_checkpoint_sha256=sha(path.read_bytes()), raw_generation_sha256=sha(row['raw_generation'].encode()))
        checkpoints.append(record)
        if row['instance_id'] == TASKS[0]:
            previous = WORKSPACE / 'marshmallow_evaluation_bundle/original_results/checkpoints' / path.name
            old = json.loads(previous.read_text())
            comparison = dict(condition=row['condition'], old_path=str(previous.relative_to(WORKSPACE)),
                              archive_path=str(path.relative_to(WORKSPACE)), byte_identical=previous.read_bytes() == path.read_bytes(),
                              json_identical=old == row, differing_fields=[k for k in old.keys() | row.keys() if old.get(k) != row.get(k)])
            comparisons.append(comparison)
    expected = {(task, condition) for task in TASKS for condition in 'WABC'}
    assert len(checkpoints) == 12 and seen == expected, seen
    configs = {r['config_hash'] for r in checkpoints}
    assert configs == {'0d94c473014df36032494da359ab2f34ef2335b996e7928d743d8afde70dc30e'}, configs
    report = dict(archive=str(archive.relative_to(WORKSPACE)), archive_sha256=sha(archive.read_bytes()),
                  safe_paths=True, crc_ok=True, unique_task_condition_count=len(seen), shared_config_hash=next(iter(configs)),
                  original_snapshot=str(snapshot.relative_to(WORKSPACE)), members=members,
                  checkpoints=checkpoints, marshmallow_comparisons=comparisons)
    (ROOT / 'input_manifest.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in ('members', 'checkpoints')}, indent=2))
    assert len(comparisons) == 4 and all(c['json_identical'] for c in comparisons), comparisons
    assert all(not c['is_mock'] and c['generation_status'] == 'COMPLETED' for c in checkpoints)


if __name__ == '__main__':
    main()
