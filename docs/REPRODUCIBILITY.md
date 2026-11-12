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

1. `scripts/verify_artifacts.py` checks the original 311-entry archive manifest, the additional release input manifest, and the main paper counts.
2. `scripts/fetch_dataset.py` downloads the pinned development Parquet file from Hugging Face and checks its SHA-256. A cached file must pass the same check. The file is evaluator-only and ignored by Git. For offline work, copy that exact file to `data/swebench_lite_dev.parquet` beforehand.
3. `paper_v2/build_reference_coverage.py` compares the 40 archived evidence packets to developer reference edits. It writes `reference_coverage.csv` and the coverage table. Target entity identities/ranges are manually recorded in the script; line visibility is computed from packet rendering and reference diffs.
4. `paper_v2/build_tables.py` audits required test IDs in raw logs and rebuilds cohort/condition/control tables, result CSVs, `summary.json`, and the evidence ledger.
5. `paper_v2/build_plots.py` renders PDF/PNG figures from the current `paper_v2/data` outputs.
6. The verifier checks the resulting principal counts and coverage totals again.

The retrieval-rank and oracle-fit table in `build_tables.py` contains manually transcribed diagnostic values. That table is rendered from those values rather than independently recomputed by this workflow. The archive preserves the corresponding top-ten ranking records. Do not interpret rendering that table as a new tokenization or ranking experiment.

The CPU dependency versions are those used to validate the release locally on Python 3.10.16. GitHub Actions is configured for Python 3.11. They are separate from historical inference environments; installing them does not recreate the original GPU stack. Figure/PDF bytes can vary with fonts, plotting libraries, TeX versions, and timestamps. The expected scientific result is agreement of the numeric records and evidence hashes, not byte-identical rebuilt PDFs.

## Building the manuscript

```bash
make paper
```

This runs `latexmk` in `paper_v2/`. The existing PDF, figures, and generated tables are included so the manuscript can also be read or compiled without rerunning the analysis. Building requires the LaTeX packages declared in `main.tex`, including `geometry`, `booktabs`, `enumitem`, `multirow`, `hyperref`, and `microtype`.

## Original generation and evaluation

The archive contains the original workflow code and environment records:

- `gemma_paper/retrieval.py` and `packet_runner.py`: original BM25/AST retrieval and W/A/B/C packaging implementation, extracted from `04_prior_three_task_pilot/gemma_paper_handoff.zip` without editing.
- `paper_v1/evidence/01_comparison_study/`: packet builder, frozen prompts, comparison runner, 22 completed checkpoints, all 40 packets, raw outputs, predictions, and resumption notebook/script.
- `paper_v1/evidence/02_native_evaluation/`: native evaluation runners, dependency audits, reference/base controls, and model test logs.
- `paper_v1/evidence/03_development_run_marshmallow_1359/`: instrumented notebook and saved package/device/tensor provenance for a development case excluded from comparison denominators.
- `paper_v1/evidence/04_prior_three_task_pilot/`: pilot notebooks and original handoff bundles.
- `evaluation_three_task/`, `evaluation/`, `pilot_audit/`, and `logs/`: historical processing, Docker evaluation, and audit records used by the pilot analysis.

These files are historical execution artifacts, not a portable one-command GPU runner. They use paths such as `/content/comparison_study` and mounted Google Drive directories. Inspect their notebook setup cells and environment records before adapting them to a fresh CUDA runtime. Model access may require accepting Google's model terms and authenticating through platform secrets. No model weights or credentials are included.

The original scripts prepare or reset task checkouts. Use disposable benchmark workspaces. Keep evaluator-only reference patches and test data out of model inputs. To extend the experiment, write new outputs separately and retain the submitted snapshot; the resumption script explicitly schedules the remaining 18 pairs.

The pilot used SWE-bench 4.1.0 with Docker and task-specific compatibility images recorded in `combined_results.json`. Fresh evaluation used isolated native Python 3.9 environments. These environments are not asserted to be equivalent.

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

The archived `paper_v1/evidence/README.md` and protocol are preserved verbatim for hash integrity. Where they describe all ten native controls as verified, an interruption cause as established, or compact excerpt lengths differently, the audited `paper_v2` manuscript and current result CSVs take precedence.
