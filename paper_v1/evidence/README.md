# Gemma Code-Repair Evidence Archive (`gemma_paper_evidence`)

**Archive Generation Timestamp:** 2026-11-08 17:38:23Z  
**Target Paper:** Code Representation Granularity and Automated Issue Repair with Frozen Gemma 4  
**Primary Model:** `google/gemma-4-E4B-it` (Revision: `4ecc2ba63bcac23ba4a767fc87025b1450f84c9c`)  
**Quantization:** BitsandBytes 8-bit (`BitsAndBytesConfig(load_in_8bit=True)`)  
**Decoded Policy:** Greedy decoding (`do_sample=False`, `num_beams=1`, `enable_thinking=False`)  
**Token Budgets:** Evidence ceiling = 4,000 tokens; Output generation cap = 2,048 tokens  

---

## 1. Executive Summary & Archive Contents

This archive consolidates all recoverable experimental artifacts, checkpoints, raw outputs, evaluator logs, test harness scripts, and provenance manifests for the Gemma code-repair research study. 

The archive covers four distinct experimental phases:
1. **Fresh 10-Task Comparison Study (`01_comparison_study/`):** 10 fresh SWE-bench Lite development tasks × 4 conditions (W, A, B, C) = 40 planned generations. Exactly 22 completed generations were recovered, 1 pair was interrupted mid-generation during an Internet outage/GPU lease expiration, and 17 pairs remain unstarted.
2. **Native Evaluation Run (`02_native_evaluation/`):** Native Colab evaluation of the completed comparison study predictions under Python 3.9 conda environments. Preflight base and reference controls verified for all 10 tasks. 10 recount-applicable patches evaluated against benchmark test suites (0/10 resolved).
3. **Instrumented Development Run (`03_development_run_marshmallow_1359/`):** Protocol v2 preflight execution on `marshmallow-code__marshmallow-1359` Condition A. Contains the executed notebook, complete environment records, INT8 layer distribution, and PyTorch tensor checkpoints (`.pt` files).
4. **Prior Three-Task Pilot Study (`04_prior_three_task_pilot/`):** Completed and evaluated 3-task pilot (`marshmallow-1343`, `pvlib-1072`, `pydicom-1139`) across conditions W, A, B, C (12 generations). Result: 0/12 resolved, with 7 applicable patches. All 12 pilot evidence packets and evaluations are preserved.
5. **Old Protocol Colab Rerun (`05_old_protocol_colab_rerun/`):** Earlier Colab rerun artifacts for `marshmallow-code__marshmallow-1343` Condition W.
6. **WSL Evaluator Handoff (`06_wsl_handoff/`):** Containerized SWE-bench Docker handoff bundle with isolated condition prediction files (`predictions_W.jsonl`, `predictions_A.jsonl`, `predictions_B.jsonl`, `predictions_C.jsonl`) and execution script `run_evaluator_wsl.sh`.

---

## 2. Directory Structure & How to Read This Archive

```
.
├── README.md                                  # This document
├── inventory.csv                              # 40-row inventory tracking every planned pair
├── manifest.json                              # Internal manifest with file paths, sizes, SHA-256
├── SHA256SUMS.txt                             # Text checksum list for standard sha256sum verification
├── 01_comparison_study/                       # Fresh 10-task comparison experiment
│   ├── protocol.md                            # Frozen study protocol and prompt template
│   ├── task_manifest.json                     # Deterministic selection manifest (10 tasks)
│   ├── build_comparison_packets.py           # BM25 evidence packet builder
│   ├── comparison_runner.py                   # GPU inference and patch extractor runner
│   ├── resume_comparison_study.py             # Script to resume remaining 18 pairs
│   ├── resume_comparison_study.ipynb          # Interactive Colab notebook for GPU resumption
│   ├── results.csv / results.json / results.md# Summary tables and scientific findings
│   ├── checkpoints/                           # 22 verified generation checkpoint JSONs
│   ├── raw_outputs/                           # 22 raw model completion texts
│   ├── predictions/                           # 22 SWE-bench format prediction JSONs
│   ├── extracted_patches/                     # Raw and canonical unified diff files
│   ├── evidence_packets/                      # All 40 evidence packets + 10 BM25 rankings
│   ├── evaluator_handoff_drive/               # Final handoff from Drive (22 predictions)
│   ├── evaluator_handoff_bundle/              # Earlier handoff from bundle (21 predictions)
│   └── evaluator_handoff_discrepancy.md       # Note detailing the discrepancy between handoff copies
├── 02_native_evaluation/                      # Colab native evaluation framework
│   ├── run_native_evaluation.py               # Evaluator runner for base/ref/model diffs
│   ├── evaluate_and_compile.py                # Result compilation and Markdown table generator
│   ├── native_evaluation_results.json         # Complete machine-readable test results
│   ├── env_audits/                            # Environment dependency audits for tasks
│   └── logs/                                  # 28 raw pytest/test logs (base, ref, model)
├── 03_development_run_marshmallow_1359/        # Preflight instrumented development run
│   ├── gemma_development_20261108T142140Z_07484dcb.zip # Original execution ZIP
│   ├── gemma_fresh_development_instrumented_colab_v2.ipynb # Executed notebook
│   └── unpacked_execution_bundle/             # Unpacked files including:
│       ├── actual_generation_inputs.pt        # Generation inputs tensor
│       ├── processor_inputs.pt                # Processor outputs tensor
│       ├── output_sequences.pt                # Detached output token tensor
│       ├── chat_template.jinja                # Pinned Gemma 4 chat template
│       ├── package_versions.json              # Exact installed package pins
│       └── checkpoint.json                    # Execution checkpoint (707 tokens)
├── 04_prior_three_task_pilot/                 # 3-task pilot baseline
│   ├── three_task_pilot_generations.zip       # Original pilot generation ZIP
│   ├── unpacked_pilot_generations/            # Checkpoints, predictions, and audit files
│   ├── combined_results.json / combined_results.md # Combined pilot evaluation report
│   ├── gemma_paper_handoff.zip                # 12 pilot evidence packets and scripts
│   ├── gemma_evidence_pilot.ipynb             # Pilot Colab notebook
│   └── kaggle_gemma_pilot.ipynb              # Pilot Kaggle notebook
├── 05_old_protocol_colab_rerun/               # Colab rerun under earlier protocol
│   ├── checkpoints/                           # marshmallow-1343 Condition W checkpoint
│   └── predictions/                           # marshmallow-1343 Condition W prediction
└── 06_wsl_handoff/                            # SWE-bench Docker harness handoff
    ├── comparison_evaluator_handoff.tar.gz    # Original handoff tarball
    └── unpacked_handoff/                      # Prediction JSONLs and run_evaluator_wsl.sh
```

---

## 3. Evidence Representation Condition Definitions

All conditions share the identical problem statement, chat wrapper, system prompt, and patch-only instruction, varying only the evidence block:

- **Condition W (Whole Files):** Complete source files selected in descending BM25 retrieval order. Files exceeding remaining capacity are skipped without truncation.
- **Condition A (Complete Entities):** Complete top-level functions, methods, and classes selected by BM25 ranking. Each entity includes enclosing definitions and docstrings.
- **Condition B (Compact Excerpts):** Compact entity representations featuring exact signature line, bounded docstring (<=8 lines), and opening excerpt (lines 1-15).
- **Condition C (Hybrid Main + Compact):** The highest-ranked entity is presented in full (as in Condition A); all supporting entities (Rank 2+) are presented in compact excerpt form (as in Condition B).

---

## 4. Status of the 40 Planned Comparison Generations

- **Completed Cleanly (EOS stop token):** 18 pairs (`pvlib-1154` W/A/B/C, `pvlib-1606` W/A/B/C, `pvlib-1707` W/A/B/C, `pvlib-1854` W/A/B/C, `pydicom-1256` W/B).
- **Completed but Truncated (Hit 2,048 Output Token Limit):** 4 pairs (`pydicom-1256` A/C, `pydicom-1413` A/B). These are valid recorded attempts; the model exhausted its token budget generating large diffs or repetitive code blocks.
- **Interrupted In-Flight:** 1 pair (`pydicom-1413` C). The process was actively generating when the GPU runtime expired. Zero bytes were persisted to disk. The evidence packet is verified and ready for resumption.
- **Unstarted Pairs:** 17 pairs (`pydicom-1413` W; all 4 conditions for `pydicom-1694`, `pydicom-901`, `astroid-1196`, `astroid-1268`).

---

## 5. What Was Recovered vs. What Is Missing

| Component | Status | Notes |
|:---|:---:|:---|
| **Pilot Study (3 tasks, 12 runs)** | Recovered | 100% complete in `04_prior_three_task_pilot/` |
| **Dev Preflight (`marshmallow-1359`)** | Recovered | 100% complete in `03_development_run_marshmallow_1359/` (includes tensors) |
| **Comparison Packets (40 pairs)** | Recovered | All 40 packets verified in `01_comparison_study/evidence_packets/` |
| **Comparison Generations (22 pairs)** | Recovered | 22 checkpoints and raw outputs verified in `01_comparison_study/` |
| **Comparison Generations (18 pairs)** | **Missing** | 1 interrupted (`pydicom-1413/C`), 17 unstarted. Resumption script prepared. |
| **Native Evaluation Controls** | Recovered | 10/10 tasks verified (base regressions failed, reference patches passed) |
| **Native Patch Evaluations** | Recovered | All 10 recount-applicable patches evaluated (0/10 resolved) |
| **Evaluator Handoff Discrepancy** | Resolved | Both 21-pair and 22-pair handoffs retained and documented |

---

## 6. How to Resume Unfinished Generations on GPU

When fresh GPU access is acquired in Colab or Kaggle:
1. Mount Google Drive containing this project.
2. Open `01_comparison_study/resume_comparison_study.ipynb` (or execute `resume_comparison_study.py`).
3. The script will:
   - Validate and reuse the 22 completed checkpoints.
   - Execute the interrupted pair `pydicom__pydicom-1413__C`.
   - Complete the remaining 17 unstarted pairs.
   - Automatically compile updated summary tables and evaluator handoffs.
