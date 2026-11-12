#!/usr/bin/env bash
# SWE-bench 4.1.0 Evaluation Runner for WSL2 / Linux (Requires Docker)
set -euo pipefail

echo "=== Verifying Docker daemon ==="
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker is not installed. Please install Docker Engine / Docker Desktop."
    exit 1
fi
if ! docker ps &> /dev/null; then
    echo "ERROR: Docker daemon is not running or accessible without sudo."
    exit 1
fi
echo "Docker daemon verified."

echo "=== Checking SWE-bench installation ==="
python3 -c "import swebench; print('SWE-bench version:', swebench.__version__)" || pip install swebench==4.1.0

echo "=== Running Official SWE-bench Lite Evaluation ==="
# Evaluates applicable and baseline predictions with max_workers=1
python3 -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --split dev \
    --predictions_path ./all_predictions.jsonl \
    --max_workers 1 \
    --run_id gemma4_rep_eval_$(date +%Y%m%d_%H%M%S)

echo "Evaluation run finished. Logs and reports generated in logs/run_evaluation/"
