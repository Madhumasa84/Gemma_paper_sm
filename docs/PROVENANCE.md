# Artifact provenance

The submission manuscript is `paper_v2/main.tex`. This repository contains the working CPU analysis, core research implementation, and one canonical set of supporting evidence. The author's original research workspace is retained separately.

## Evidence ownership

`evidence/manifest.json` is the single integrity manifest for the retained inputs. Each entry records the repository path, byte size, SHA-256, and original source paths. Identical source bytes are stored once, with all retained aliases recorded as provenance. The pilot `attempts.json` index maps task/condition identities to their canonical checkpoints, processing audits, and reports.

The original 311-entry archive manifest is preserved in `evidence/provenance/original_archive_manifest.json` as historical metadata. It describes the original archive, not this curated release. Verification checks the 247 retained inputs and all current ledger source digests. A digest establishes byte consistency, not independent authenticity.

## Cleanup

Repeated ZIP/handoff bundles, duplicate pilot exports, old platform-specific runners, superseded summaries, generated-file copies, and local build/cache artifacts are excluded. Their removal does not alter frozen model outputs, reference inputs, recorded outcomes, or manuscript prose. The core retrieval, packaging, dataset, model-loading, and repair implementation remains in `gemma_paper/`.

Analysis scripts now read the consolidated `evidence/` paths. Reference coverage is written only to `paper_v2/data/reference_coverage.csv`; the evidence ledger is written only to `paper_v2/evidence_ledger.csv`. Rebuilding does not recreate removed duplicates.

## Analysis safeguards

Reference coverage uses a repository-relative pinned dataset and PyArrow directly. Figures read the freshly rebuilt `paper_v2/data` records. Resolution requires confirmed passage of every required regression and preservation test with verified controls; unconfirmed preservation tests cannot establish success.

The historical archive count in the evidence ledger remains 311 because it describes the original archive. The retained-input count is separately reported by the verifier. File locations and ledger hashes change with consolidation; scientific outcomes do not.

## Snapshot policy

Rebuilding analysis does not run inference. Completing missing attempts, changing generation settings, or repeating evaluation creates a new experiment and must use a separate output location.
