# Reference-Code Visibility and Patch Applicability in Budgeted Code Repair

**A Gemma Pilot Study · Madhusudhanan G**

Research code, archived experimental evidence, and analysis accompanying the paper **“Reference-Code Visibility and Patch Applicability in Budgeted Code Repair: A Gemma Pilot Study.”**

**[Read the paper](paper_v2/main.pdf)** · [Manuscript source](paper_v2/main.tex) · [Reproduction guide](docs/REPRODUCIBILITY.md) · [Evidence ledger](paper_v2/evidence_ledger.csv) · [Citation](CITATION.cff)

## Research question

Under a fixed **4,000-token evidence budget**, which reference-modified code remains visible to a repair model, and where do the observed repair attempts fail?

The study audits frozen `google/gemma-4-E4B-it` runs on the **SWE-bench Lite development split**, comparing four deterministic ways to package retrieved Python source:

| Policy | Evidence representation |
| --- | --- |
| W | Whole files; skip files that exceed the remaining budget |
| A | Complete functions and classes with source line ranges |
| B | Signatures, bounded docstrings, and 14-line opening excerpts |
| C | One complete primary entity with 9-line supporting excerpts |

Reference patches are used **only for the offline evaluator diagnostic**. They are not supplied to the repair model or used to select its evidence.

## Results at a glance

| Cohort | Completed / planned | Applicable patches | Tested | Demonstrated resolutions |
| --- | ---: | ---: | ---: | ---: |
| Development pilot | 12 / 12 | 7 recount-assisted | 7 | 0 |
| Fresh comparison, interim | 22 / 40 | 2 strict; 10 recount-assisted total | 10 | 0 |

Across the 40 frozen fresh packets, whole-file packaging omits 8 of 10 reference files. Compact policies B and C expose all 10 reference files, but miss the edit site in 8 and 9 tasks respectively. Policy A exposes edit lines in 3 of 10 tasks. These observations describe visibility and application failure boundaries; the sample does not establish a winning repair policy.

The unfinished 18 fresh attempts are **17 unstarted and 1 reported interrupted**, not observed failures. Five tasks have complete four-policy generation sets. Only six of ten native evaluation tasks have fully verified controls under the manuscript's stricter audit. See the [limitations](docs/REPRODUCIBILITY.md#limitations-and-interpretation).

## Quick start: reproduce the analysis

Requires Python 3.10 or 3.11, `make`, and internet access for one small pinned dataset download. No GPU, model weights, or API key is needed.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make reproduce
```

This verifies archived input hashes, downloads and authenticates the pinned development dataset, then regenerates reference coverage, tables, the evidence ledger, and figures. The paper's principal counts are checked again after rebuilding. Generated CSV/LaTeX results are retained in `paper_v2/`; the dataset download is ignored by Git.

To verify the included evidence without installing analysis dependencies or downloading data:

```bash
python3 scripts/verify_artifacts.py
```

To compile the manuscript with a TeX Live installation containing `latexmk` and the packages used in `main.tex`:

```bash
make paper
```

## Repository guide

| Path | Purpose |
| --- | --- |
| [`paper_v2/`](paper_v2/) | Submission manuscript, bibliography, PDF, analysis scripts, tables, figures, and audited results |
| [`gemma_paper/`](gemma_paper/) | Original retrieval, BM25 ranking, evidence packaging, prompting, and generation modules recovered from the pilot handoff |
| [`evaluator/`](evaluator/) | Original pilot evaluator helpers |
| [`paper_v1/evidence/`](paper_v1/evidence/) | Frozen evidence archive: fresh runs, native test logs, instrumented case, pilot notebooks, and original execution scripts |
| [`paper_v1/data/required_tests.json`](paper_v1/data/required_tests.json) | Required benchmark test identifiers used by the current audit |
| [`evaluation_three_task/`](evaluation_three_task/) | Pilot prediction processing code and source checkpoints |
| [`evaluation/`](evaluation/) and [`pilot_audit/`](pilot_audit/) | Historical evaluation and audit scripts |
| [`logs/`](logs/) | Pilot harness reports and test output referenced by the evidence ledger |
| [`scripts/`](scripts/) | Portable dataset download and artifact verification |
| [`docs/`](docs/) | Reproduction details, provenance, and rights information |

`paper_v1` is retained as an **evidence path**, because manifests and ledger records refer to it. The submission manuscript is `paper_v2/main.tex`.

## Reproduction scope

The supported local workflow rebuilds the analysis from recorded evidence. Original GPU and native/Docker execution scripts are included for inspection and adaptation; their Colab/Drive paths and historical dependencies require the environments described in the [reproduction guide](docs/REPRODUCIBILITY.md#original-generation-and-evaluation). Running them creates a new experiment and is not required to reproduce the submitted analysis.

## Citation and reuse

Use the repository's **Cite this repository** metadata or cite the accompanying manuscript. No publication venue, DOI, or acceptance status is claimed.

The author's original code is released under the [MIT License](LICENSE). Third-party code, benchmark excerpts, and archived evidence retain their applicable terms; see [rights and third-party notices](docs/RIGHTS_AND_NOTICES.md).
