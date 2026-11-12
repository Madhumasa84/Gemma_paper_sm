# Combined three-task Gemma pilot evaluation

All 12 task/condition pairs are retained. **0/12 resolved**, 7/12 patches applicable, 7 patches tested.
Overall application rate: **7/12 (58.3%)**. Resolution among tested patches: **0/7 (0.0%)**.

| Task | Condition | Generation / truncated | Application outcome | Tests executed | F2P passed | P2P passed | Resolved | Infrastructure error |
|---|---|---|---|---|---|---|---|---|
| marshmallow-code__marshmallow-1343 | W | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/1 | 24/24 | No | None |
| marshmallow-code__marshmallow-1343 | A | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/1 | 24/24 | No | None |
| marshmallow-code__marshmallow-1343 | B | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/1 | 24/24 | No | None |
| marshmallow-code__marshmallow-1343 | C | COMPLETED / No | PATCH_NOT_APPLICABLE | No | Not executed | Not executed | Not evaluated | None |
| pvlib__pvlib-python-1072 | W | COMPLETED / No | PATCH_NOT_APPLICABLE | No | Not executed | Not executed | Not evaluated | None |
| pvlib__pvlib-python-1072 | A | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/1 | 18/18 | No | None |
| pvlib__pvlib-python-1072 | B | COMPLETED / No | PATCH_NOT_APPLICABLE | No | Not executed | Not executed | Not evaluated | None |
| pvlib__pvlib-python-1072 | C | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/1 | 18/18 | No | None |
| pydicom__pydicom-1139 | W | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/3 | 38/38 | No | None |
| pydicom__pydicom-1139 | A | COMPLETED / No | PATCH_NOT_APPLICABLE | No | Not executed | Not executed | Not evaluated | None |
| pydicom__pydicom-1139 | B | COMPLETED / No | APPLIED_NORMALIZED | Yes | 0/3 | 38/38 | No | None |
| pydicom__pydicom-1139 | C | COMPLETED / No | PATCH_NOT_APPLICABLE | No | Not executed | Not executed | Not evaluated | None |

F2P/P2P counts are passed/required. Application failures were never submitted for testing and are not executed test failures. A null resolved value means not evaluated, while the task remains in the overall denominator.

| Condition | Tasks resolved / THREE | Application rate | Tested patches | Resolution among tested | Infrastructure errors |
|---|---|---|---|---|---|
| W | 0/3 | 2/3 (66.7%) | 2 | 0/2 (0.0%) | 0 |
| A | 0/3 | 2/3 (66.7%) | 2 | 0/2 (0.0%) | 0 |
| B | 0/3 | 2/3 (66.7%) | 2 | 0/2 (0.0%) | 0 |
| C | 0/3 | 1/3 (33.3%) | 1 | 0/1 (0.0%) | 0 |

Three tasks support descriptive pilot results only; no statistical significance is claimed.

## Evaluator validation

Marshmallow results were reused only after all four checkpoints matched byte-for-byte. Its completed reports, raw logs, scripts and outputs remain unchanged and are archived in [marshmallow_completed.zip](archives/marshmallow_completed.zip), with [SHA-256 manifest](archives/marshmallow_completed_manifest.json).

- `marshmallow-code__marshmallow-1343`: preflight **PASSED** (verified prior evaluation reused).
- `pvlib__pvlib-python-1072`: preflight **PASSED**.
  [base_log_dir/report.json](logs/run_evaluation/pilot2_base_pvlib__pvlib-python-1072_04a523fafbd6_enve6a6a28ecea3/unmodified_base/pvlib__pvlib-python-1072/report.json)
  [base_log_dir/test_output.txt](logs/run_evaluation/pilot2_base_pvlib__pvlib-python-1072_04a523fafbd6_enve6a6a28ecea3/unmodified_base/pvlib__pvlib-python-1072/test_output.txt)
  [base_log_dir/run_instance.log](logs/run_evaluation/pilot2_base_pvlib__pvlib-python-1072_04a523fafbd6_enve6a6a28ecea3/unmodified_base/pvlib__pvlib-python-1072/run_instance.log)
  [base_log_dir/eval.sh](logs/run_evaluation/pilot2_base_pvlib__pvlib-python-1072_04a523fafbd6_enve6a6a28ecea3/unmodified_base/pvlib__pvlib-python-1072/eval.sh)
  [reference_log_dir/report.json](logs/run_evaluation/pilot2_reference_pvlib__pvlib-python-1072_d18c3f997994_enve6a6a28ecea3/reference_evaluator_only/pvlib__pvlib-python-1072/report.json)
  [reference_log_dir/test_output.txt](logs/run_evaluation/pilot2_reference_pvlib__pvlib-python-1072_d18c3f997994_enve6a6a28ecea3/reference_evaluator_only/pvlib__pvlib-python-1072/test_output.txt)
  [reference_log_dir/run_instance.log](logs/run_evaluation/pilot2_reference_pvlib__pvlib-python-1072_d18c3f997994_enve6a6a28ecea3/reference_evaluator_only/pvlib__pvlib-python-1072/run_instance.log)
  [reference_log_dir/eval.sh](logs/run_evaluation/pilot2_reference_pvlib__pvlib-python-1072_d18c3f997994_enve6a6a28ecea3/reference_evaluator_only/pvlib__pvlib-python-1072/eval.sh)
- `pydicom__pydicom-1139`: preflight **PASSED**.
  [base_log_dir/report.json](logs/run_evaluation/pilot2_base_pydicom__pydicom-1139_b9fb05c177b6_enva24eb46eb81d/unmodified_base/pydicom__pydicom-1139/report.json)
  [base_log_dir/test_output.txt](logs/run_evaluation/pilot2_base_pydicom__pydicom-1139_b9fb05c177b6_enva24eb46eb81d/unmodified_base/pydicom__pydicom-1139/test_output.txt)
  [base_log_dir/run_instance.log](logs/run_evaluation/pilot2_base_pydicom__pydicom-1139_b9fb05c177b6_enva24eb46eb81d/unmodified_base/pydicom__pydicom-1139/run_instance.log)
  [base_log_dir/eval.sh](logs/run_evaluation/pilot2_base_pydicom__pydicom-1139_b9fb05c177b6_enva24eb46eb81d/unmodified_base/pydicom__pydicom-1139/eval.sh)
  [reference_log_dir/report.json](logs/run_evaluation/pilot2_reference_pydicom__pydicom-1139_061145e48f90_enva24eb46eb81d/reference_evaluator_only/pydicom__pydicom-1139/report.json)
  [reference_log_dir/test_output.txt](logs/run_evaluation/pilot2_reference_pydicom__pydicom-1139_061145e48f90_enva24eb46eb81d/reference_evaluator_only/pydicom__pydicom-1139/test_output.txt)
  [reference_log_dir/run_instance.log](logs/run_evaluation/pilot2_reference_pydicom__pydicom-1139_061145e48f90_enva24eb46eb81d/reference_evaluator_only/pydicom__pydicom-1139/run_instance.log)
  [reference_log_dir/eval.sh](logs/run_evaluation/pilot2_reference_pydicom__pydicom-1139_061145e48f90_enva24eb46eb81d/reference_evaluator_only/pydicom__pydicom-1139/eval.sh)

Base controls execute the exact official evaluation script without a model patch; an empty skipped prediction is never used as baseline. Every base verifies a clean tree identical to the dataset base. Reference controls must resolve all F2P tests and preserve all P2P tests before any model prediction for that task is interpreted. Gold patches/tests are stored only under evaluator-only directories.

## Infrastructure incidents

Initial controls exposed two historical dependency incompatibilities. These attempts are infrastructure failures, not model failures. Their original logs/reports remain preserved. Final per-pair infrastructure fields describe the validated evaluation attempts.

- `pvlib__pvlib-python-1072`: NumPy 2.0 removed np.Inf, preventing historical pvlib import. Repair: NumPy 1.26.4 and pandas 1.5.3 in a separate image. Revalidated: **True**.
  [Initial failing test log](logs/run_evaluation/pilot2_base_pvlib__pvlib-python-1072_04a523fafbd6/unmodified_base/pvlib__pvlib-python-1072/test_output.txt), [initial outcome](evaluation_three_task/evaluator_only/pvlib__pvlib-python-1072/preflight_outcome.json.initial-infrastructure-attempt), [Dockerfile](evaluation_three_task/infrastructure/pvlib/Dockerfile), [build log](evaluation_three_task/logs/pvlib-compat-image-build.log).
- `pydicom__pydicom-1139`: pytest 8 removed nose-style setup hooks; two preservation tests had no self.tag fixture. Repair: pytest 7.4.4 in a separate image. Revalidated: **True**.
  [Initial failing test log](logs/run_evaluation/pilot2_base_pydicom__pydicom-1139_b9fb05c177b6/unmodified_base/pydicom__pydicom-1139/test_output.txt), [initial outcome](evaluation_three_task/evaluator_only/pydicom__pydicom-1139/preflight_outcome.json.initial-infrastructure-attempt), [Dockerfile](evaluation_three_task/infrastructure/pydicom/Dockerfile), [build log](evaluation_three_task/logs/pydicom-compat-image-build.log).

## Processing and provenance

Dataset: `princeton-nlp/SWE-bench_Lite`, split `dev`, revision `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2`, fingerprint `8dd9ba440fb35178`. SWE-bench **4.1.0**, existing isolated environment `evaluation/.venv-legacy`.
Model: `google/gemma-4-E4B-it`, revision `4ecc2ba63bcac23ba4a767fc87025b1450f84c9c`. Shared recorded configuration hash: `0d94c473014df36032494da359ab2f34ef2335b996e7928d743d8afde70dc30e`. All generations reported `stop` below the 2,048 output-token cap; no model was loaded or response regenerated.

The supplied archive contains recorded hashes rather than the complete generation configuration or prompt text. Shared hashes and revisions were verified; the prior experiment settings were not changed or reconstructed.

The last explicitly labelled `diff`/`patch` fenced block was selected; whitespace was preserved and a final newline ensured. `git apply --recount --check` followed by `git apply --recount` ran in an isolated temporary checkout at the task base. The canonical staged Git diff was exported; added/removed lines were verified unchanged. No source context, missing lines or patch logic were repaired, and no patch was selected using test performance.

[Input archive audit and source hashes](evaluation_three_task/input_manifest.json), [processing manifest](evaluation_three_task/processing_manifest.json), [exact Marshmallow extraction equivalence](evaluation_three_task/marshmallow_processing_equivalence.json), [dataset bases](evaluation_three_task/dataset_metadata.json).

## Per-pair artifacts and hashes

### marshmallow-code__marshmallow-1343 / W

Source checkpoint SHA-256: `c8b38c20eaf3fb7e1aca0be9cdaa02fa9340573c68badd1cac8598f162ba5e9c`.
Raw generation SHA-256: `4d171bfa05b7c0d560b4578c1efaa117b6bb1ee7a931bf2defe3ac6b58f7935d`.
Normalized prediction SHA-256: `de99f2cb2f6c47e61d03511ae7474054e6f4b52a67325102a7d3cddb76eaf978`.
Normalized patch SHA-256: `dd58c6e798efb7023fd40d634fdb9bee85131823efa6b8b8418f31a522578430`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/marshmallow-code__marshmallow-1343__W__a1__aa52258f__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/marshmallow-code__marshmallow-1343__W__a1__aa52258f__0d94c473.json), [normalized prediction](marshmallow_evaluation_bundle/predictions_W.jsonl), [processing audit](marshmallow_evaluation_bundle/original_results/processing_audit_v3/W.json).
[report](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json)
[test_output](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt)
[harness_log](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log)
[evaluation_script](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh)
[run_summary](google__gemma-4-E4B-it.gemma_pilot_W_de99f2cb2f6c47e6.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_W.jsonl --run_id gemma_pilot_W_de99f2cb2f6c47e6 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
```

### marshmallow-code__marshmallow-1343 / A

Source checkpoint SHA-256: `89e56540ce51cff561d787285487cd6d8a834d7907f92825cb54bbe004df05b1`.
Raw generation SHA-256: `ee516f07165a1694da944d0875c61f25cbfb54bb50bead3449afacdf020793aa`.
Normalized prediction SHA-256: `585e64ea6b265e8672377dabb9c6ca475eff059afb613b1572105ca840588bbe`.
Normalized patch SHA-256: `825bfcdface79474e1d06e398b86abe1f14f4e77bd691d71ef5ecbeddbe95bff`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/marshmallow-code__marshmallow-1343__A__a1__25e8db93__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/marshmallow-code__marshmallow-1343__A__a1__25e8db93__0d94c473.json), [normalized prediction](marshmallow_evaluation_bundle/predictions_A.jsonl), [processing audit](marshmallow_evaluation_bundle/original_results/processing_audit_v3/A.json).
[report](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json)
[test_output](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt)
[harness_log](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log)
[evaluation_script](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh)
[run_summary](google__gemma-4-E4B-it.gemma_pilot_A_585e64ea6b265e86.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_A.jsonl --run_id gemma_pilot_A_585e64ea6b265e86 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
```

### marshmallow-code__marshmallow-1343 / B

Source checkpoint SHA-256: `d77b4d6c1c8d0d619b7616991b083aae8c6a2fd74cf7c88d6dd29eeb1ac5c195`.
Raw generation SHA-256: `3ffddef4a84b56d53cb91ab5b59efdc96249480aff6b43d9c57ea78be192ecfa`.
Normalized prediction SHA-256: `242a56b1fdf5ea5328a6cbf9c60ace89e61c60af4f9aa2a71d63b4a384f71b9d`.
Normalized patch SHA-256: `4f1ed52390aa283c673cd2fde8487f8e7b0923c16f98351dc5603f1b6ab78ee2`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/marshmallow-code__marshmallow-1343__B__a1__3f933535__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/marshmallow-code__marshmallow-1343__B__a1__3f933535__0d94c473.json), [normalized prediction](marshmallow_evaluation_bundle/predictions_B.jsonl), [processing audit](marshmallow_evaluation_bundle/original_results/processing_audit_v3/B.json).
[report](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json)
[test_output](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt)
[harness_log](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log)
[evaluation_script](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh)
[run_summary](google__gemma-4-E4B-it.gemma_pilot_B_242a56b1fdf5ea53.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_B.jsonl --run_id gemma_pilot_B_242a56b1fdf5ea53 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
```

### marshmallow-code__marshmallow-1343 / C

Source checkpoint SHA-256: `336b3a4b2511b4a7167261e869366d47d402d28563de56cc36a3c3c3cde28e47`.
Raw generation SHA-256: `262ed7eaed830a047f5685ee28929df2513c52e78d72deeef0de818273c77eaa`.
Normalized prediction SHA-256: `94fcb04a73372a3dde6b72eaa6fe287a2d969d1e277a57a4418fd45a962e15e7`.
Normalized patch SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/marshmallow-code__marshmallow-1343__C__a1__fe45737d__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/marshmallow-code__marshmallow-1343__C__a1__fe45737d__0d94c473.json), [normalized prediction](marshmallow_evaluation_bundle/predictions_C.jsonl), [processing audit](marshmallow_evaluation_bundle/original_results/processing_audit_v3/C.json).

```text
error: patch failed: src/marshmallow/schema.py:887
error: src/marshmallow/schema.py: patch does not apply
```

### pvlib__pvlib-python-1072 / W

Source checkpoint SHA-256: `a38681ad04043293f74848ec48d38a7605d0c6af7fa4987bf25537ad2dc09628`.
Raw generation SHA-256: `fd2816076f8617e4fac85cc09308c6966f39e88696886efb0bb0e4dc6fa0029d`.
Normalized prediction SHA-256: `84f9993fb812aac06af945d0f54f22b2b53d7946ad4a2297e2b258b9146f149c`.
Normalized patch SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pvlib__pvlib-python-1072__W__a1__eb5e55b8__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pvlib__pvlib-python-1072__W__a1__eb5e55b8__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pvlib__pvlib-python-1072/W/predictions.jsonl), [processing audit](evaluation_three_task/processed/pvlib__pvlib-python-1072/W/audit.json).

```text
error: patch failed: pvlib/temperature.py:579
error: pvlib/temperature.py: patch does not apply
```
[Exact processing commands](evaluation_three_task/processed/pvlib__pvlib-python-1072/W/processing_commands.json).

### pvlib__pvlib-python-1072 / A

Source checkpoint SHA-256: `890a416f2c36adb4ac8294ae23dea7eb7b4839e1976c31684a82946d7f8e340d`.
Raw generation SHA-256: `655d302989b1fc09754120d01763a79d930c3d9bba7c46036f744a2e3770424c`.
Normalized prediction SHA-256: `2699eb2d01d06d3502c5b9182625704c604ec2e5fd9ef53202c287a7bda7ead1`.
Normalized patch SHA-256: `face3b050edd2b12d5569b1e3388f4776a905b3bf2c1aa1947b744713ff3bb4d`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pvlib__pvlib-python-1072__A__a1__7d8940ea__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pvlib__pvlib-python-1072__A__a1__7d8940ea__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pvlib__pvlib-python-1072/A/predictions.jsonl), [processing audit](evaluation_three_task/processed/pvlib__pvlib-python-1072/A/audit.json).
[Exact processing commands](evaluation_three_task/processed/pvlib__pvlib-python-1072/A/processing_commands.json).
[report](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/report.json)
[test_output](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/test_output.txt)
[harness_log](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/run_instance.log)
[eval_script](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/eval.sh)
[applied_patch](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/patch.diff)
[console_log](evaluation_three_task/logs/pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3.log)
[run_summary](google__gemma-4-E4B-it.pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids pvlib__pvlib-python-1072 --max_workers 1 --predictions_path evaluation_three_task/processed/pvlib__pvlib-python-1072/A/predictions.jsonl --run_id pilot2_pvlib__pvlib-python-1072_A_2699eb2d01d06d35_enve6a6a28ecea3 --cache_level instance --timeout 1800 --instance_image_tag pilot-compat-np126-pd15
```

### pvlib__pvlib-python-1072 / B

Source checkpoint SHA-256: `9294fce657c0ec4576b1006afb933c7eb3af5cebf16eec3ceb2ba9c931a80e17`.
Raw generation SHA-256: `2c6b909d4edf428fdf9472f6abb0854d7e2ac73a145e8e8d75cd101391857256`.
Normalized prediction SHA-256: `84f9993fb812aac06af945d0f54f22b2b53d7946ad4a2297e2b258b9146f149c`.
Normalized patch SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pvlib__pvlib-python-1072__B__a1__4a106365__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pvlib__pvlib-python-1072__B__a1__4a106365__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pvlib__pvlib-python-1072/B/predictions.jsonl), [processing audit](evaluation_three_task/processed/pvlib__pvlib-python-1072/B/audit.json).

```text
error: patch failed: pvlib/temperature.py:599
error: pvlib/temperature.py: patch does not apply
```
[Exact processing commands](evaluation_three_task/processed/pvlib__pvlib-python-1072/B/processing_commands.json).

### pvlib__pvlib-python-1072 / C

Source checkpoint SHA-256: `03ce3132f0907edad042c64113b7a8508c7125f52b54ef633fcb1155d0962056`.
Raw generation SHA-256: `b9a8652cf5dc74ebd83c5a9ffdedd9b98042450ea32f55095ea2f1bdeb3db23a`.
Normalized prediction SHA-256: `5f2f5b655335b57f44b59abedd2663675cf762e9660bc30f5e54d1b29e2db7a6`.
Normalized patch SHA-256: `21bce54cfd3f1a4332203527edafd1fcf1085ffe4e50f939b36be05b57aea030`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pvlib__pvlib-python-1072__C__a1__00e324d9__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pvlib__pvlib-python-1072__C__a1__00e324d9__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pvlib__pvlib-python-1072/C/predictions.jsonl), [processing audit](evaluation_three_task/processed/pvlib__pvlib-python-1072/C/audit.json).
[Exact processing commands](evaluation_three_task/processed/pvlib__pvlib-python-1072/C/processing_commands.json).
[report](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/report.json)
[test_output](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/test_output.txt)
[harness_log](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/run_instance.log)
[eval_script](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/eval.sh)
[applied_patch](logs/run_evaluation/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3/google__gemma-4-E4B-it/pvlib__pvlib-python-1072/patch.diff)
[console_log](evaluation_three_task/logs/pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3.log)
[run_summary](google__gemma-4-E4B-it.pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids pvlib__pvlib-python-1072 --max_workers 1 --predictions_path evaluation_three_task/processed/pvlib__pvlib-python-1072/C/predictions.jsonl --run_id pilot2_pvlib__pvlib-python-1072_C_5f2f5b655335b57f_enve6a6a28ecea3 --cache_level instance --timeout 1800 --instance_image_tag pilot-compat-np126-pd15
```

### pydicom__pydicom-1139 / W

Source checkpoint SHA-256: `bb2676eb8da7619d6bfca2235c69304dbaac62ce74e80e9e2a38fdd5b45d2a6c`.
Raw generation SHA-256: `9ee93ad51faa906a8ded6b10873f7cbc3b0c5492c66115a1545836808d94fe77`.
Normalized prediction SHA-256: `24233f43636f3dd09216e0de5d29404e297545bc6c6ad895963d1bdeea04c859`.
Normalized patch SHA-256: `3048a66ff8bd50d7013a34fe09107e38cf08eaa836b66cf07a7eab22c2375da9`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pydicom__pydicom-1139__W__a1__47d8388e__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pydicom__pydicom-1139__W__a1__47d8388e__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pydicom__pydicom-1139/W/predictions.jsonl), [processing audit](evaluation_three_task/processed/pydicom__pydicom-1139/W/audit.json).
[Exact processing commands](evaluation_three_task/processed/pydicom__pydicom-1139/W/processing_commands.json).
[report](logs/run_evaluation/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/report.json)
[test_output](logs/run_evaluation/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/test_output.txt)
[harness_log](logs/run_evaluation/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/run_instance.log)
[eval_script](logs/run_evaluation/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/eval.sh)
[applied_patch](logs/run_evaluation/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/patch.diff)
[console_log](evaluation_three_task/logs/pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d.log)
[run_summary](google__gemma-4-E4B-it.pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids pydicom__pydicom-1139 --max_workers 1 --predictions_path evaluation_three_task/processed/pydicom__pydicom-1139/W/predictions.jsonl --run_id pilot2_pydicom__pydicom-1139_W_24233f43636f3dd0_enva24eb46eb81d --cache_level instance --timeout 1800 --instance_image_tag pilot-compat-pytest744
```

### pydicom__pydicom-1139 / A

Source checkpoint SHA-256: `cd4f1e45fc8e3343ada915c440ef95e2563bb05701e7868d709a0e71b8e52604`.
Raw generation SHA-256: `169988a4c8404a8e70d9ccec2b5c1c4a2c0d042d3a676aca1b4bf88133e8d521`.
Normalized prediction SHA-256: `004c89beba71a2dd0c04c7638fbf80f08b12ff2ff2fdc66cc2ad2439775e16fd`.
Normalized patch SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pydicom__pydicom-1139__A__a1__e2c04977__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pydicom__pydicom-1139__A__a1__e2c04977__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pydicom__pydicom-1139/A/predictions.jsonl), [processing audit](evaluation_three_task/processed/pydicom__pydicom-1139/A/audit.json).

```text
error: patch failed: pydicom/dataset.py:101
error: pydicom/dataset.py: patch does not apply
```
[Exact processing commands](evaluation_three_task/processed/pydicom__pydicom-1139/A/processing_commands.json).

### pydicom__pydicom-1139 / B

Source checkpoint SHA-256: `49a320fca62384100d2c0f44cd41945a1893fa5c60a7977b01a4c160513ed171`.
Raw generation SHA-256: `f388ea72a18b8911f4b7608a80307084b6846e8f7240faf80d296d5a33c6d5be`.
Normalized prediction SHA-256: `0edcc03554b22010c45c9dad5094e2b3029154ec73249cf7c62d24706ca92afe`.
Normalized patch SHA-256: `dad3ec7c10e2a08e2e6b5cfd6f54f84f014fcd84b048e6e67eb76bc020d96a3a`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pydicom__pydicom-1139__B__a1__7ba62b02__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pydicom__pydicom-1139__B__a1__7ba62b02__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pydicom__pydicom-1139/B/predictions.jsonl), [processing audit](evaluation_three_task/processed/pydicom__pydicom-1139/B/audit.json).
[Exact processing commands](evaluation_three_task/processed/pydicom__pydicom-1139/B/processing_commands.json).
[report](logs/run_evaluation/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/report.json)
[test_output](logs/run_evaluation/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/test_output.txt)
[harness_log](logs/run_evaluation/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/run_instance.log)
[eval_script](logs/run_evaluation/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/eval.sh)
[applied_patch](logs/run_evaluation/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d/google__gemma-4-E4B-it/pydicom__pydicom-1139/patch.diff)
[console_log](evaluation_three_task/logs/pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d.log)
[run_summary](google__gemma-4-E4B-it.pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d.json)

```bash
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids pydicom__pydicom-1139 --max_workers 1 --predictions_path evaluation_three_task/processed/pydicom__pydicom-1139/B/predictions.jsonl --run_id pilot2_pydicom__pydicom-1139_B_0edcc03554b22010_enva24eb46eb81d --cache_level instance --timeout 1800 --instance_image_tag pilot-compat-pytest744
```

### pydicom__pydicom-1139 / C

Source checkpoint SHA-256: `10d98928db278c8310f47f2f47adc5ad252c5d91260c1cfdc4713ee666bb0b1d`.
Raw generation SHA-256: `b35b293c6275b693b7615f5c66651fba40cfe3aa3bd91ac4a0f8b0d6de97447c`.
Normalized prediction SHA-256: `004c89beba71a2dd0c04c7638fbf80f08b12ff2ff2fdc66cc2ad2439775e16fd`.
Normalized patch SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
[Source checkpoint](evaluation_three_task/source_archive/checkpoints/pydicom__pydicom-1139__C__a1__77c52864__0d94c473.json), [original prediction JSON](evaluation_three_task/source_archive/predictions/pydicom__pydicom-1139__C__a1__77c52864__0d94c473.json), [normalized prediction](evaluation_three_task/processed/pydicom__pydicom-1139/C/predictions.jsonl), [processing audit](evaluation_three_task/processed/pydicom__pydicom-1139/C/audit.json).

```text
error: patch failed: pydicom/dataelem.py:154
error: pydicom/dataelem.py: patch does not apply
```
[Exact processing commands](evaluation_three_task/processed/pydicom__pydicom-1139/C/processing_commands.json).

## Commands and evidence

All new harness invocations use `--max_workers 1`, distinct task/condition/prediction-hash run IDs, the requested dataset/dev split and the verified offline cache. Their exact arguments, environment, exit codes and console paths are recorded in [commands.json](evaluation_three_task/commands.json). Process exit status alone is never treated as resolution.

Setup: [archive preparation](evaluation_three_task/logs/prepare.log), [dataset verification](evaluation_three_task/logs/dataset.log), [processing log](evaluation_three_task/logs/processing.log), [pvlib image download](evaluation_three_task/logs/pull-pvlib.log), [pydicom image download](evaluation_three_task/logs/pull-pydicom.log).

Entrypoints: [prepare.py](evaluation_three_task/prepare.py), [process_predictions.py](evaluation_three_task/process_predictions.py), [preflight.py](evaluation_three_task/preflight.py), [run_evaluations.py](evaluation_three_task/run_evaluations.py), [combine_results.py](evaluation_three_task/combine_results.py).

Full structured records, generation/truncation details, per-test names, source/normalized hashes and preflight outcomes are in [combined_results.json](combined_results.json). [evaluation_evidence.zip](evaluation_evidence.zip) contains reports, raw logs, evaluation/processing scripts, predictions and manifests; virtual environments, Docker images, model weights, caches and credentials are excluded.
