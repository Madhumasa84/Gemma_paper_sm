# Independent Gemma pilot evaluation

Task: `marshmallow-code__marshmallow-1343`. Dataset: `princeton-nlp/SWE-bench_Lite`, split `dev`.
Base commit verified: `2be2d83a1a9a6d3d9b85804f3ab545cecc409bb0`.

| Condition | Patch applied | Tests executed | Resolved | Fail-to-pass results | Pass-to-pass results | Error category |
|---|---|---|---|---|---|---|
| BASE | No | Yes | No | 0/1 passed | 24/24 passed | None |
| REFERENCE | Yes | Yes | Yes | 1/1 passed | 24/24 passed | None |
| W | Yes | Yes | No | 0/1 passed | 24/24 passed | UNRESOLVED |
| A | Yes | Yes | No | 0/1 passed | 24/24 passed | UNRESOLVED |
| B | Yes | Yes | No | 0/1 passed | 24/24 passed | UNRESOLVED |
| C | No | No | Not evaluated | Not executed | Not executed | PATCH_NOT_APPLICABLE |

Base regression failure is expected and validates the evaluator. C has no applicable patch and was never submitted to the harness; it is not a tested baseline or a model test failure.

## Evaluator validation

Preflight passed: **True**. The base run verified the requested base tree and a clean worktree, applied no model patch, and directly executed the exact official evaluation script. The reference run used the dataset reference patch. Both used the same image and identical evaluation script; every saved prediction used that script too.

The official image adds an empty SWE-bench setup commit (`d4f98233971ee3e73bba47026cd77b4ba69a25bb`) whose parent is the expected base. Both commits have identical tree `a38157586804d01a22947322408a8a2a09b39bce`. An initial strict HEAD check stopped before testing; this was investigated and corrected to verify tree equivalence. Evidence: [image setup](evaluation/logs/image-base-investigation.txt), [base comparison](evaluation/logs/base-equivalence.log), [initial check](evaluation/logs/preflight-initial-head-check.log). The baseline grader's `patch_successfully_applied` field indicates test log markers; `baseline_no_model_patch=true` explicitly records that no model patch was applied.

Reference patch and tests are stored in `evaluation/evaluator_only/`, separate from the preserved solver outputs. No model was loaded and no prediction was regenerated or edited.

## Versions and provenance

5.0.1 installs, but is incompatible with this dataset schema: make_test_spec raises KeyError: 'image'; official 4.1.0 used in separate isolated environment.

Python: 3.10.16; architecture: x86_64. Dataset revision: `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2`; dev fingerprint: `8dd9ba440fb35178`; 23 rows. Prediction runs loaded this verified cache in offline mode.

The ZIP passed CRC/path/symlink checks and was extracted separately into `evaluation/archive_verified/`. All 21 archived files match the supplied directory. All original files remain byte-for-byte unchanged.

Environment: [resources](evaluation/logs/environment.txt), [Docker version](evaluation/logs/docker-version.txt), [Docker daemon](evaluation/logs/docker-info.txt).
Dependencies: [5.0.1](evaluation/logs/dependencies.txt), [4.1.0](evaluation/logs/dependencies-legacy.txt). Both isolated environments passed `pip check`.
Test container dependencies: [Python and pip freeze](evaluation/logs/container-dependencies.txt). Image and immutable digest: [image inspection](evaluation/logs/image-inspect.json).
The 4.1.0 harness writes run summaries in the working directory despite accepting `--report_dir`; the actual summary paths are linked below.
Harness help: [5.0.1](evaluation/logs/harness-help.txt), [4.1.0](evaluation/logs/harness-help-legacy.txt).
Official documentation: https://www.swebench.com/SWE-bench/guides/evaluation/ (saved at `evaluation/logs/official-evaluation-docs.html`).
Hashes: [prediction and original files](evaluation/input_inventory.json), [ZIP and archive comparisons](evaluation/archive_audit.json).

| Condition | Prediction file SHA-256 |
|---|---|
| W | `de99f2cb2f6c47e61d03511ae7474054e6f4b52a67325102a7d3cddb76eaf978` |
| A | `585e64ea6b265e8672377dabb9c6ca475eff059afb613b1572105ca840588bbe` |
| B | `242a56b1fdf5ea5328a6cbf9c60ace89e61c60af4f9aa2a71d63b4a384f71b9d` |
| C | `94fcb04a73372a3dde6b72eaa6fe287a2d969d1e277a57a4418fd45a962e15e7` |

## Commands

Run from `/home/masa84/gemma-pilot-evaluation`.

```bash
python3 -m venv evaluation/.venv
evaluation/.venv/bin/python -m pip index versions swebench
evaluation/.venv/bin/python -m pip install swebench==5.0.1
evaluation/.venv/bin/python -m swebench.harness.run_evaluation --help
HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv/bin/python evaluation/prepare.py
# Above command records the dataset, then fails with KeyError: 'image' under 5.0.1.
python3 -m venv --system-site-packages evaluation/.venv-legacy
sed -i 's/include-system-site-packages = true/include-system-site-packages = false/' evaluation/.venv-legacy/pyvenv.cfg
# Installation was repeated after disabling system packages to populate all isolated dependencies.
evaluation/.venv-legacy/bin/python -m pip install swebench==4.1.0
evaluation/.venv-legacy/bin/python -m pip check
evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --help
docker pull swebench/sweb.eval.x86_64.marshmallow-code_1776_marshmallow-1343:latest
HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv-legacy/bin/python evaluation/preflight.py
# preflight.py calls the official base eval script directly, then run_instance for reference.
HF_HOME="$PWD/evaluation/hf_cache" evaluation/.venv-legacy/bin/python evaluation/verify_preflight.py
# Original verification retried after locating 4.1.0 logs under logs/run_evaluation.
export HF_HOME="$PWD/evaluation/hf_cache" HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_W.jsonl --run_id gemma_pilot_W_de99f2cb2f6c47e6 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_A.jsonl --run_id gemma_pilot_A_585e64ea6b265e86 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
/home/masa84/gemma-pilot-evaluation/evaluation/.venv-legacy/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Lite --split dev --instance_ids marshmallow-code__marshmallow-1343 --max_workers 1 --predictions_path marshmallow_evaluation_bundle/predictions_B.jsonl --run_id gemma_pilot_B_242a56b1fdf5ea53 --cache_level instance --timeout 1800 --report_dir evaluation/summary_reports
```

The complete argument arrays, process exit codes, test identities, dependency versions, and artifact paths are in [results.json](results.json). Resolution is taken from reports and observed test outcomes, never process exit codes.

## Reports and logs

- **BASE**: [report](logs/evaluation/pilot_preflight_base_tree_2be2d83a1a9a/unmodified_base/marshmallow-code__marshmallow-1343/report.json), [test_output](logs/evaluation/pilot_preflight_base_tree_2be2d83a1a9a/unmodified_base/marshmallow-code__marshmallow-1343/test_output.txt), [harness_log](logs/evaluation/pilot_preflight_base_tree_2be2d83a1a9a/unmodified_base/marshmallow-code__marshmallow-1343/run_instance.log), [evaluation_script](logs/evaluation/pilot_preflight_base_tree_2be2d83a1a9a/unmodified_base/marshmallow-code__marshmallow-1343/eval.sh)
- **REFERENCE**: [report](logs/run_evaluation/pilot_preflight_reference_fb93d3650801/reference_evaluator_only/marshmallow-code__marshmallow-1343/report.json), [test_output](logs/run_evaluation/pilot_preflight_reference_fb93d3650801/reference_evaluator_only/marshmallow-code__marshmallow-1343/test_output.txt), [harness_log](logs/run_evaluation/pilot_preflight_reference_fb93d3650801/reference_evaluator_only/marshmallow-code__marshmallow-1343/run_instance.log), [evaluation_script](logs/run_evaluation/pilot_preflight_reference_fb93d3650801/reference_evaluator_only/marshmallow-code__marshmallow-1343/eval.sh)
- **W**: [report](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json), [test_output](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt), [harness_log](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log), [evaluation_script](logs/run_evaluation/gemma_pilot_W_de99f2cb2f6c47e6/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh), [run_summary](google__gemma-4-E4B-it.gemma_pilot_W_de99f2cb2f6c47e6.json)
  Console: [evaluation/logs/gemma_pilot_W_de99f2cb2f6c47e6.log](evaluation/logs/gemma_pilot_W_de99f2cb2f6c47e6.log).
- **A**: [report](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json), [test_output](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt), [harness_log](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log), [evaluation_script](logs/run_evaluation/gemma_pilot_A_585e64ea6b265e86/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh), [run_summary](google__gemma-4-E4B-it.gemma_pilot_A_585e64ea6b265e86.json)
  Console: [evaluation/logs/gemma_pilot_A_585e64ea6b265e86.log](evaluation/logs/gemma_pilot_A_585e64ea6b265e86.log).
- **B**: [report](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/report.json), [test_output](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/test_output.txt), [harness_log](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/run_instance.log), [evaluation_script](logs/run_evaluation/gemma_pilot_B_242a56b1fdf5ea53/google__gemma-4-E4B-it/marshmallow-code__marshmallow-1343/eval.sh), [run_summary](google__gemma-4-E4B-it.gemma_pilot_B_242a56b1fdf5ea53.json)
  Console: [evaluation/logs/gemma_pilot_B_242a56b1fdf5ea53.log](evaluation/logs/gemma_pilot_B_242a56b1fdf5ea53.log).
- **C**: No execution artifacts.

Setup/preflight: [installation](evaluation/logs/install.log), [legacy installation](evaluation/logs/install-legacy.log), [5.0.1 incompatibility](evaluation/logs/prepare.log), [image pull](evaluation/logs/image-pull.log), [preflight console](evaluation/logs/preflight.log), [final preflight verification](evaluation/logs/preflight-verify.log).

The first post-reference log lookup used the newer harness log directory and raised FileNotFoundError after reference tests had completed successfully. The path was corrected to `logs/run_evaluation`; the final verification independently parsed both existing test logs and checked their reports and identical scripts. No model result was inferred from that orchestration error.
