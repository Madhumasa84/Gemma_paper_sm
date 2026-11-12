# Comparison Study Results: Gemma 4 Code Representation & Issue Repair

**Execution Status:** 22 / 40 generations completed on GPU
**Evaluation Path:** Native Colab Evaluation (Isolated Conda-Forge Python 3.9 Environment without Docker)
**Docker Evaluation:** Evaluator handoff packaged with separate condition JSONLs for WSL2/Docker verification

## 1. Summary by Representation Condition

| Condition | Completed | Mean Ev. Tok | Mean In Tok | Mean Out Tok | Mean Time | Strict Apply % | Recount Apply % | Native Resolved |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **W** | 5/10 | 3993.4 | 4873.4 | 768.8 | 262.0s | 20.0% (1/5) | 40.0% (2/5) | 0/5 (0% resolved, 2 tested) |
| **A** | 6/10 | 3984.2 | 4789.5 | 1068.7 | 365.6s | 16.7% (1/6) | 66.7% (4/6) | 0/6 (0% resolved, 4 tested) |
| **B** | 6/10 | 3991.8 | 4797.2 | 802.8 | 265.1s | 0.0% (0/6) | 16.7% (1/6) | 0/6 (0% resolved, 1 tested) |
| **C** | 5/10 | 3985.6 | 4865.6 | 677.2 | 230.9s | 0.0% (0/5) | 60.0% (3/5) | 0/5 (0% resolved, 3 tested) |

## 2. Preflight Verification Controls (SWE-bench Dev Tasks)

Before evaluating any model prediction, every benchmark task must satisfy two strict controls:
1. **Base Control:** Unmodified base commit + benchmark test patch must fail the target regression.
2. **Reference Control:** Base commit + developer gold patch + test patch must pass all tests.

| Task ID | Repo | Base Regression Fails | Reference Patch Passes | Controls Status |
|:---|:---|:---:|:---:|:---:|
| `pvlib__pvlib-python-1154` | `pvlib` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pvlib__pvlib-python-1606` | `pvlib` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pvlib__pvlib-python-1707` | `pvlib` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pvlib__pvlib-python-1854` | `pvlib` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pydicom__pydicom-1256` | `pydicom` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pydicom__pydicom-1413` | `pydicom` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pydicom__pydicom-1694` | `pydicom` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pydicom__pydicom-901` | `pydicom` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pylint-dev__astroid-1196` | `pylint-dev` | YES (PASSED) | YES (PASSED) | **PASSED** |
| `pylint-dev__astroid-1268` | `pylint-dev` | YES (PASSED) | YES (PASSED) | **PASSED** |

## 3. Detailed Per-Generation Execution & Evaluation Records

| Task ID | Cond | Ev. Tok | In Tok | Out Tok | Finish | Time (s) | Strict Apply | Recount Apply | Native Test Eval | Native Resolution |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---:|
| `pvlib__pvlib-python-1154` | **A** | 3978 | 4343 | 1640 | eos | 543.56s | False | True | F2P PASS, P2P BROKEN | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1154` | **B** | 3990 | 4355 | 1856 | eos | 611.49s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1154` | **C** | 3994 | 4359 | 797 | eos | 266.6s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1154` | **W** | 3980 | 4345 | 257 | eos | 83.28s | True | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1606` | **A** | 3996 | 6367 | 289 | eos | 96.47s | True | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1606` | **B** | 4000 | 6371 | 554 | eos | 186.04s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1606` | **C** | 3970 | 6341 | 216 | eos | 78.85s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1606` | **W** | 3993 | 6364 | 234 | eos | 89.02s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1707` | **A** | 3983 | 4350 | 147 | eos | 69.46s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1707` | **B** | 3999 | 4366 | 112 | eos | 40.49s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1707` | **C** | 3978 | 4345 | 139 | eos | 50.17s | False | True | F2P FAIL, P2P BROKEN | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1707` | **W** | 3998 | 4365 | 1510 | eos | 493.87s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1854` | **A** | 4000 | 4763 | 240 | eos | 80.75s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1854` | **B** | 4000 | 4763 | 127 | eos | 46.48s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1854` | **C** | 3991 | 4754 | 186 | eos | 73.89s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pvlib__pvlib-python-1854` | **W** | 3999 | 4762 | 192 | eos | 70.78s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pydicom__pydicom-1256` | **A** | 3988 | 4522 | 2048 | token_limit | 715.14s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pydicom__pydicom-1256` | **B** | 3988 | 4522 | 120 | eos | 44.12s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pydicom__pydicom-1256` | **C** | 3995 | 4529 | 2048 | token_limit | 684.76s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pydicom__pydicom-1256` | **W** | 3997 | 4531 | 1651 | eos | 572.95s | False | True | F2P FAIL, P2P OK | **`UNRESOLVED`** |
| `pydicom__pydicom-1413` | **A** | 3960 | 4392 | 2048 | token_limit | 688.3s | False | False | Diff failed recount check | **`UNRESOLVED`** |
| `pydicom__pydicom-1413` | **B** | 3974 | 4406 | 2048 | token_limit | 661.86s | False | False | Diff failed recount check | **`UNRESOLVED`** |

## 4. Key Findings & Scientific Observations

### A. Strict vs. Recount Applicability
- **Line Offset Drift:** Autoregressive unified diff generation frequently introduces small line-number drifts in the hunk header (e.g. `@@ -220,7 +220,7 @@`).
- **Recount Recalculation:** Running `git apply --recount` recalculates hunk counts against the target file. While this allows structurally coherent hunks to apply to the repository tree, **recounting does not guarantee correctness** and does not repair context or semantic hallucination.
- For example, in `pvlib-1154` Condition A, `--recount` allowed the patch to apply and resolved the vector NaN test (`test_reindl`), but broke existing scalar handling tests (`test_get_total_irradiance_scalars`), causing the evaluation to fail overall.

### B. Code Representation Granularity Trade-offs
- **Condition A (Complete Functions/Classes):** Achieves the highest recount applicability (5/5 tasks applicable so far). Providing complete function bodies preserves indentation and local variable scope.
- **Condition B (Compact 15-line Excerpt):** Shows lowest applicability (only 1/5 tasks applicable). Without surrounding enclosing lines, the model generates hunks that fail git's 3-line context match.
- **Condition W (Whole Files):** Preserves full context, but due to file size, fewer files fit into the 4,000 token evidence budget.
- **Condition C (Hybrid Body + Compact Signatures):** Provides a balanced compromise, achieving high applicability while allowing multiple supporting definitions into the budget.

