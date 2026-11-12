# Artifact provenance

This release is curated from the author's local research workspace. The submission is `paper_v2/main.tex`; previous manuscript drafts, local environments, dataset/model caches, cloned benchmark repositories, and operating-system metadata are excluded.

## Preserved inputs

The complete `paper_v1/evidence/` archive is copied byte-for-byte, including its original manifest and historical scripts/notebooks. All 311 listed entries are checked by `scripts/verify_artifacts.py`.

Pilot source checkpoints, processing audits, and harness reports retain the paths referenced by `combined_results.json` and the generated evidence ledger. `gemma_paper/` and `evaluator/` are extracted from the original pilot handoff ZIP so reviewers can inspect the implementation directly.

`artifact_manifest.json` records SHA-256 and byte size for additional frozen inputs outside the original evidence archive. Rebuildable analysis outputs and release documentation are not part of that input manifest. Git history provides versioning for release code and documentation after publication.

## Release preparation changes

Only the submission copy of the following analysis code is adapted:

- Reference coverage reads the pinned dataset from a repository-relative `data/` path and uses PyArrow directly, removing a local absolute path and an unnecessary pandas conversion.
- Plotting reads the freshly generated `paper_v2/data` results instead of older `paper_v1/data` outputs.
- The resolution audit explicitly requires zero unconfirmed preservation tests, in addition to the existing regression/control checks. This strengthens the documented success invariant and leaves the observed zero-resolution counts unchanged.

Portable setup, dataset authentication, input verification, documentation, citation metadata, and a GitHub Actions CPU reproduction workflow are added. Original model outputs, reference inputs, historical execution scripts, and manuscript prose are not rewritten.

## Snapshot policy

The included PDF is the author's submitted-manuscript candidate. Rebuilding analysis does not run inference. Completing missing attempts, changing generation settings, or repeating evaluation produces a new experiment and should be recorded separately from this frozen release.
