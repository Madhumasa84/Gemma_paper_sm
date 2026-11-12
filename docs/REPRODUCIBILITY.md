# Reproducing the submitted analysis

## Frozen study identifiers

| Item | Identifier |
| --- | --- |
| Submission manuscript | `paper_v2/main.tex` |
| Model | `google/gemma-4-E4B-it` |
| Model revision | `4ecc2ba63bcac23ba4a767fc87025b1450f84c9c` |
| Dataset | `princeton-nlp/SWE-bench_Lite`, `dev` |
| Dataset revision | `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2` |
| Evidence / output budget | 4,000 / 2,048 tokens |
| Fresh protocol | Greedy decoding; batch size 1; thinking disabled; 8-bit weights |
| Evidence snapshot label | 2026-11-08 17:38:23 UTC; internal files extend to 17:46 UTC |

## CPU analysis workflow

Run commands from the repository root using Python 3.10 or 3.11 and `requirements.txt`:

```bash
make reproduce
```

The steps are ordered because tables depend on reference coverage and figures depend on the newly rebuilt tables/data:

1. `scripts/verify_artifacts.py` checks the 247 retained evidence files against `evidence/manifest.json`, validates current ledger source hashes, and checks the main paper counts.
2. `scripts/fetch_dataset.py` downloads the pinned development Parquet file from Hugging Face and checks its SHA-256. A cached file must pass the same check. The file is evaluator-only and ignored by Git. For offline work, copy that exact file to `data/swebench_lite_dev.parquet` beforehand.
3. `paper_v2/build_reference_coverage.py` compares the 40 archived evidence packets to developer reference edits. It writes `reference_coverage.csv` and the coverage table. Target entity identities/ranges are manually recorded in the script; line visibility is computed from packet rendering and reference diffs.
4. `paper_v2/build_tables.py` audits required test IDs in raw logs and rebuilds cohort/condition/control tables, result CSVs, `summary.json`, and the evidence ledger.
5. `paper_v2/build_plots.py` renders PDF/PNG figures from the current `paper_v2/data` outputs.
6. The verifier checks the resulting principal counts and coverage totals again.

The retrieval-rank and oracle-fit table in `build_tables.py` contains manually transcribed diagnostic values. That table is rendered from those values rather than independently recomputed by this workflow. The `evidence/fresh/packets/` directory preserves the corresponding top-ten ranking records. Do not interpret rendering that table as a new tokenization or ranking experiment.

The CPU dependency versions are those used to validate the release locally on Python 3.10.16. GitHub Actions is configured for Python 3.11. They are separate from historical inference environments; installing them does not recreate the original GPU stack. Figure/PDF bytes can vary with fonts, plotting libraries, TeX versions, and timestamps. The expected scientific result is agreement of the numeric records and evidence hashes, not byte-identical rebuilt PDFs.

## Building the manuscript

```bash
make paper
```

This runs `latexmk` in `paper_v2/`. The existing PDF, figures, and generated tables are included so the manuscript can also be read or compiled without rerunning the analysis. Building requires the LaTeX packages declared in `main.tex`, including `geometry`, `booktabs`, `enumitem`, `multirow`, `hyperref`, and `microtype`.

## Research source and retained evidence

The repository exposes one supported analysis workflow: `make reproduce`. Historical transfer scripts, repeated evaluation runners, ZIP bundles, and resumption notebooks are excluded.

- `gemma_paper/`: original retrieval, AST/BM25 ranking, packaging, dataset preparation, model-loading, and repair modules. These preserve the study implementation; GPU-specific modules require the historical CUDA/inference stack and are not invoked by the CPU workflow.
- `evidence/fresh/`: all 40 frozen packets, top-ten rankings, 22 completed checkpoints, model outputs and predictions, task selection manifest, and completion inventory.
- `evidence/native/`: required test IDs, native evaluation records, dependency audits, and raw base/reference/model test logs.
- `evidence/pilot/`: one copy of the pilot checkpoints, processing audits, available test output, shared harness reports, and 12 evidence packets. `attempts.json` maps each task/condition to its canonical sources; identical report bytes are stored once.
- `evidence/development/`: instrumented marshmallow-1359 generation inputs, output tensors, package/device records, prompt and configuration provenance. This case is excluded from comparison denominators.
- `evidence/provenance/`: original archive manifest and handoff-reconciliation note. These describe the original archive, not the number of files retained in this cleaned repository.

`evidence/manifest.json` records each retained input's size, SHA-256, and original source paths. The pilot index is a derived path mapping; outcomes are unchanged. The verifier also checks every source path/digest in the rebuilt evidence ledger.

Model access may require accepting Google's model terms and authenticating through platform secrets. Model weights and credentials are excluded. Keep evaluator-only reference information out of solver inputs. Any future generation or benchmark rerun must use a separate output location to preserve the submitted snapshot.

The pilot used SWE-bench 4.1.0 with Docker and task-specific compatibility images. Fresh evaluation used isolated native Python 3.9 environments. These environments are not asserted to be equivalent.

## Limitations and interpretation

- Fresh completion is 22/40, with five complete four-condition task sets. The other 18 outcomes are unknown.
- Strict application succeeds in 2/22 completions. Recount-assisted application succeeds in 10/22 total, including those two strict successes.
- No issue resolution is demonstrated in either comparison cohort. This does not justify ranking policies on benchmark resolution.
- A resolution requires every required regression and preservation test to be confirmed passed, with verified controls. Missing, skipped, errored, or unmatched required tests cannot establish success.
- Six of ten native tasks have fully verified controls. Known problems include missing preservation test confirmations for pvlib-1154, errors for pvlib-1707 and pvlib-1854, and reference preservation failures for pydicom-1413.
- Original pilot prompt variants and complete pilot generation configuration were not recovered. Fresh per-attempt effective configuration/device audits were not separately preserved for every comparison run.
- The interruption's technical cause cannot be established from preserved telemetry. Historical archive prose describing lease expiration is not independent evidence of that cause.
- The internal manifest authenticates byte consistency, not external provenance. No independent outer-archive signature was supplied.
- Entity coverage uses manually identified reference entities; this is a diagnostic, not a learned or oracle-assisted retrieval policy. Oracle information must not feed back into solver inputs.

The original archive is preserved in the author’s research workspace. This repository retains the evidence required for the submitted analysis; the audited `paper_v2` manuscript and current result CSVs govern interpretation.
