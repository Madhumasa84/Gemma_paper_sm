# Recovery Status Report: Gemma 4 Code Representation & Issue Repair Study

**Date/Time:** 2026-11-08 17:23:57Z  
**Recovery Agent:** Antigravity Pair Programmer  
**Environment:** Google Colab Linux Container (`d40457f6fd7c` x86_64, CPU runtime)

## 1. Executive Summary

- **Total Planned Generations:** 40 (10 tasks × 4 conditions: W, A, B, C)
- **Actual Recovered Completed Generations:** **22 / 40** (55.0%)
- **Interrupted In-Flight Generation:** **1** (`pydicom__pydicom-1413__C`)
- **Unstarted Pairs:** **17**
- **GPU Status:** Expired / Unavailable in current container session (CPU fallback strictly barred)
- **Google Drive Status:** **Verified & Mounted** at `/content/drive/MyDrive/gemma_paper/`
- **Pilot Study (3 tasks, 12 runs):** 100% Preserved & Isolated (0/12 resolved, 7 applicable)
- **Development Preflight (`marshmallow-1359__A`):** 100% Preserved & Isolated (707 tokens, INT8 layers 592)

## 2. Counts by Evidence Representation Condition

| Condition | Description | Completed / 10 | Applicable Patches | Resolved / Evaluated |
|:---:|:---|:---:|:---:|:---:|
| **W** | Complete whole files | 5/10 | 2 | 0 / 2 |
| **A** | Complete functions/classes | 6/10 | 4 | 0 / 4 |
| **B** | Compact signatures/docstrings/excerpts | 6/10 | 1 | 0 / 1 |
| **C** | Full main + compact supporting | 5/10 | 3 | 0 / 3 |
| **Total** | | **22/40** | **10** | **0 / 10** |

## 3. Inventory of All 40 Task/Condition Pairs

### A. Completed Pairs (22 / 40)

| Task ID | Cond | Ev. Tokens | In Tokens | Out Tokens | Finish Reason | Strict Apply | Recount Apply | Prompt SHA-256 Valid |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `pvlib__pvlib-python-1154` | **W** | 3980 | 4345 | 257 | `eos` | True | True | True |
| `pvlib__pvlib-python-1154` | **A** | 3978 | 4343 | 1640 | `eos` | False | True | True |
| `pvlib__pvlib-python-1154` | **B** | 3990 | 4355 | 1856 | `eos` | False | False | True |
| `pvlib__pvlib-python-1154` | **C** | 3994 | 4359 | 797 | `eos` | False | True | True |
| `pvlib__pvlib-python-1606` | **W** | 3993 | 6364 | 234 | `eos` | False | False | True |
| `pvlib__pvlib-python-1606` | **A** | 3996 | 6367 | 289 | `eos` | True | True | True |
| `pvlib__pvlib-python-1606` | **B** | 4000 | 6371 | 554 | `eos` | False | False | True |
| `pvlib__pvlib-python-1606` | **C** | 3970 | 6341 | 216 | `eos` | False | False | True |
| `pvlib__pvlib-python-1707` | **W** | 3998 | 4365 | 1510 | `eos` | False | False | True |
| `pvlib__pvlib-python-1707` | **A** | 3983 | 4350 | 147 | `eos` | False | True | True |
| `pvlib__pvlib-python-1707` | **B** | 3999 | 4366 | 112 | `eos` | False | False | True |
| `pvlib__pvlib-python-1707` | **C** | 3978 | 4345 | 139 | `eos` | False | True | True |
| `pvlib__pvlib-python-1854` | **W** | 3999 | 4762 | 192 | `eos` | False | False | True |
| `pvlib__pvlib-python-1854` | **A** | 4000 | 4763 | 240 | `eos` | False | True | True |
| `pvlib__pvlib-python-1854` | **B** | 4000 | 4763 | 127 | `eos` | False | False | True |
| `pvlib__pvlib-python-1854` | **C** | 3991 | 4754 | 186 | `eos` | False | True | True |
| `pydicom__pydicom-1256` | **W** | 3997 | 4531 | 1651 | `eos` | False | True | True |
| `pydicom__pydicom-1256` | **A** | 3988 | 4522 | 2048 | `token_limit` | False | False | True |
| `pydicom__pydicom-1256` | **B** | 3988 | 4522 | 120 | `eos` | False | True | True |
| `pydicom__pydicom-1256` | **C** | 3995 | 4529 | 2048 | `token_limit` | False | False | True |
| `pydicom__pydicom-1413` | **A** | 3960 | 4392 | 2048 | `token_limit` | False | False | True |
| `pydicom__pydicom-1413` | **B** | 3974 | 4406 | 2048 | `token_limit` | False | False | True |

### B. Interrupted Pair (1 / 40)

- **Pair:** `pydicom__pydicom-1413__C`
  - **Task:** `pydicom__pydicom-1413` | **Condition:** `C`
  - **Failure Mode:** Process was actively generating `pydicom-1413__C` when network outage and GPU lease expiration occurred; zero bytes persisted to disk.
  - **Evidence Packet Available:** Yes (`pydicom__pydicom-1413__C__packet.json` verified)
  - **Recovery Action:** Queued as the first task in `resume_comparison_study.py` / `resume_comparison_study.ipynb` when GPU becomes available.

### C. Unstarted Pairs (17 / 40)

| Task ID | Condition | Packet Verified |
|:---|:---:|:---:|
| `pydicom__pydicom-1413` | **W** | Yes |
| `pydicom__pydicom-1694` | **W** | Yes |
| `pydicom__pydicom-1694` | **A** | Yes |
| `pydicom__pydicom-1694` | **B** | Yes |
| `pydicom__pydicom-1694` | **C** | Yes |
| `pydicom__pydicom-901` | **W** | Yes |
| `pydicom__pydicom-901` | **A** | Yes |
| `pydicom__pydicom-901` | **B** | Yes |
| `pydicom__pydicom-901` | **C** | Yes |
| `pylint-dev__astroid-1196` | **W** | Yes |
| `pylint-dev__astroid-1196` | **A** | Yes |
| `pylint-dev__astroid-1196` | **B** | Yes |
| `pylint-dev__astroid-1196` | **C** | Yes |
| `pylint-dev__astroid-1268` | **W** | Yes |
| `pylint-dev__astroid-1268` | **A** | Yes |
| `pylint-dev__astroid-1268` | **B** | Yes |
| `pylint-dev__astroid-1268` | **C** | Yes |

## 4. Evaluation Progress & Scientific Findings

- **SWE-bench Dev Controls:** All 10 tasks passed strict base regression failure and reference test passing controls.
- **Applicable Patches Evaluated:** 10 / 22 completed generations produced recount-applicable patches.
- **Test Resolution:** 0 / 10 resolved. Applicable patches failed target regression or introduced regressions on pass-to-pass tests.
- **Format Failure Rate:** 12 / 22 patches were unapplicable (mostly Condition B excerpts lacking context and 2,048 token limit truncations on pydicom-1256 and 1413).

## 5. Provenance & Artifact Integrity

- **Checkpoint Integrity:** All 22 checkpoint JSON files validated with exact schema, model ID (`google/gemma-4-E4B-it`), revision (`4ecc2ba63bcac23ba4a767fc87025b1450f84c9c`), and matching prompt SHA-256 hashes.
- **Raw Outputs:** All 22 raw output text files preserved without modifications.
- **Evaluator Handoff:** Packaged into `comparison_evaluator_handoff.tar.gz` with separate condition JSONLs (`predictions_W.jsonl`, `predictions_A.jsonl`, `predictions_B.jsonl`, `predictions_C.jsonl`).
- **Pilot Results:** 3-task pilot preserved in `pilot_study/three_task_pilot_generations.zip`.
- **Development Run:** `marshmallow-1359__A` preserved in `development_run/gemma_development_20261108T142140Z_07484dcb.zip`.

## 6. Verified Backup Archives & Hashes

| Archive Name | Location | Size | SHA-256 |
|:---|:---|:---:|:---:|
| `comparison_recovery_20261108T172659Z.zip` | `/content/drive/MyDrive/gemma_paper/comparison_recovery_20261108T172659Z.zip` | 669,649 B | `67ecd3582595f54a81c1054b3980708f62499910dd28f22273fe56acf25f9fe7` |
| `comparison_recovery_20261108T172659Z.zip` | `/content/comparison_recovery_20261108T172659Z.zip` | 669,649 B | `67ecd3582595f54a81c1054b3980708f62499910dd28f22273fe56acf25f9fe7` |
| `comparison_study_bundle.zip` | `/content/drive/MyDrive/gemma_paper/comparison_study/comparison_study_bundle.zip` | 504,795 B | `0ad9b988da6bcfc67b3f83d18cdf20d6241f4f1a956051af1ffadbf635f6d1d2` |
| `comparison_evaluator_handoff.tar.gz` | `/content/drive/MyDrive/gemma_paper/comparison_evaluator_handoff.tar.gz` | 9,026 B | `e6cbee4926c6dbcaeba2e478cc90239ba98069125ffef066d2e4cf555b3a3b98` |

## 7. Exact Next Action

1. **Do not attempt GPU generation in this container:** GPU is unavailable and no CPU generation is permitted under Protocol v2.
2. **To resume remaining 18 pairs (when GPU quota is renewed):**
   - Open a fresh Colab session with a T4 or A100 GPU.
   - Open `/content/drive/MyDrive/gemma_paper/comparison_study/resume_comparison_study.ipynb`.
   - Run all cells; it will automatically reuse the 22 completed checkpoints, generate `pydicom-1413/C`, and complete the 17 unstarted pairs.
3. **For Docker-harness evaluation in WSL2:**
   - Use `comparison_evaluator_handoff.tar.gz` with `run_evaluator_wsl.sh` in your SWE-bench 4.1.0 environment.
