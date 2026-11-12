#!/usr/bin/env python3
"""Check frozen evidence integrity and the manuscript's principal denominators."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def verify_manifest(root, manifest):
    entries = json.loads(manifest.read_text())
    for entry in entries:
        path = root / entry["path"]
        require(path.is_file(), f"Missing evidence: {path}")
        data = path.read_bytes()
        require(len(data) == entry["bytes"], f"Size mismatch: {path}")
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], f"SHA-256 mismatch: {path}")
    return len(entries)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def main():
    evidence = ROOT / "evidence"
    count = verify_manifest(ROOT, evidence / "manifest.json")
    summary = json.loads((ROOT / "paper_v2/data/summary.json").read_text())
    require(summary["pilot"] == {"completed": 12, "applied": 7, "tested": 7, "resolved": 0}, "Pilot summary changed")
    expected = dict(planned=40, completed=22, strict=2, recount=10, tested=10,
                    verified_resolved=0, complete_task_sets=5, controls_verified=6)
    for key, value in expected.items():
        require(summary["fresh"][key] == value, f"Fresh summary changed: {key}")
    rows = read_csv(ROOT / "paper_v2/data/fresh_rows.csv")
    require(len(rows) == 40 and len({(r['instance_id'], r['condition']) for r in rows}) == 40, "Expected 40 unique fresh pairs")
    completed = [r for r in rows if r["completed"] == "True"]
    require(len(completed) == 22, "Expected 22 completed pairs")
    coverage = read_csv(ROOT / "paper_v2/data/reference_coverage.csv")
    require(len(coverage) == 40, "Expected 40 coverage rows")
    for policy, expected_counts in {"W": (2, 2, 2), "A": (8, 3, 3), "B": (10, 7, 2), "C": (10, 7, 1)}.items():
        subset = [r for r in coverage if r["condition"] == policy]
        counts = tuple(sum(r[key] == "True" for r in subset) for key in
                       ("any_file_overlap", "any_entity_overlap", "any_line_overlap"))
        require(len(subset) == 10 and counts == expected_counts, f"Coverage changed: {policy}: {counts}")
    ledger = read_csv(ROOT / "paper_v2/evidence_ledger.csv")
    for claim in ledger:
        paths = claim["source_paths"].split(";")
        hashes = claim["source_sha256"].split(";")
        require(len(paths) == len(hashes), "Ledger paths/digests differ in length")
        for name, expected_hash in zip(paths, hashes):
            source = ROOT / name
            require(source.is_file(), f"Missing ledger source: {name}")
            require(hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash,
                    f"Ledger source digest changed: {name}")
    print(f"Verified {count} manifest entries; paper denominators and coverage agree.")


if __name__ == "__main__":
    main()
