"""Package task evidence from explicit local paths, excluding runtime/caches/secrets."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
EXCLUDED = {'.git', '.aws', '.codex', '.agents', '__pycache__', 'hf_cache'}


def main():
    paths = set()
    for folder in ('evaluation', 'evaluation_three_task', 'logs', 'marshmallow_evaluation_bundle', 'archives'):
        for path in (WORKSPACE / folder).rglob('*'):
            relative = path.relative_to(WORKSPACE)
            if any(p in EXCLUDED or p.startswith('.venv') for p in relative.parts):
                continue
            if path.is_file() and not path.is_symlink():
                paths.add(path)
    for filename in ('results.md', 'results.json', 'combined_results.md', 'combined_results.json',
                     'marshmallow_evaluation_bundle.zip', 'three_task_pilot_generations.zip'):
        paths.add(WORKSPACE / filename)
    paths.update(WORKSPACE.glob('google__gemma*.json'))
    files = [{'path': str(p.relative_to(WORKSPACE)), 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(paths)]
    manifest = WORKSPACE / 'evaluation_evidence_manifest.json'
    manifest.write_text(json.dumps({'files': files,
        'excluded': ['virtual environments', 'Docker images', 'model weights', 'Hugging Face caches', 'credentials'],
        'evaluator_only_material': 'Gold patches and tests are included only in clearly separated evaluator_only directories or the completed evaluator snapshot, never supplied to generation or prediction processing.'}, indent=2))
    archive = WORKSPACE / 'evaluation_evidence.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(paths):
            z.write(path, path.relative_to(WORKSPACE))
        z.write(manifest, manifest.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(set(z.namelist()))
        for item in files:
            assert hashlib.sha256(z.read(item['path'])).hexdigest() == item['sha256']
        for name in z.namelist():
            assert not any(p in EXCLUDED or p.startswith('.venv') for p in Path(name).parts)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (WORKSPACE / 'evaluation_evidence.sha256').write_text(digest + '  evaluation_evidence.zip\n')
    print(json.dumps({'archive': archive.name, 'bytes': archive.stat().st_size, 'sha256': digest, 'files': len(files) + 1, 'verified': True}, indent=2))


if __name__ == '__main__':
    main()
