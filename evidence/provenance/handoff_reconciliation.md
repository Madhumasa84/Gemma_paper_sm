# Evaluator Handoff Discrepancy Note

Two copies of `evaluator_handoff/` existed across the session archives:

1. `evaluator_handoff_drive/` (Recovered from `/content/drive/MyDrive/gemma_paper/comparison_study/evaluator_handoff/`):
   - Timestamp: 2026-11-08 16:41 UTC (immediately prior to session disconnection)
   - Predictions Count: 22 records (`predictions_B.jsonl` contains 6 records, including `pydicom-1413` with empty patch)
   - Size of all_predictions.jsonl: 22,503 bytes (SHA-256: d4d61b0cecc2baecc76c3311003f440990a481156a75d944effc7f8f366a7992)

2. `evaluator_handoff_bundle/` (Recovered from `comparison_study_bundle.zip`):
   - Timestamp: 2026-11-08 16:35 UTC (prior to final handoff export)
   - Predictions Count: 21 records (`predictions_B.jsonl` contains 5 records, ending at `pydicom-1256`)
   - Size of all_predictions.jsonl: 22,391 bytes (SHA-256: 49dc4b4d142e4aaac700ea06cfab43cf545bf3cf24990efdddf398c265cb57fd)

**Resolution:** Both copies are preserved. `evaluator_handoff_drive` is the authoritative final handoff reflecting all 22 completed GPU generations.
