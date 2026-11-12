# Research Study Protocol: Gemma 4 Code Representation & Issue Repair

## 1. Research Question
For a frozen Gemma model under a fixed evidence-token ceiling (4,000 tokens), how do different repository-code representations affect:
1. Issue resolution (pass/fail on benchmark tests);
2. Patch applicability (syntactic validity, clean application, recount tolerance);
3. Relevant-source coverage (overlap with developer reference modifications);
4. Input/output tokens and runtime efficiency?

## 2. Model & Generation Configuration
- **Model:** `google/gemma-4-E4B-it`
- **Revision:** `4ecc2ba63bcac23ba4a767fc87025b1450f84c9c`
- **Quantization:** `bitsandbytes` explicit 8-bit (`BitsAndBytesConfig(load_in_8bit=True)`)
- **Dtype:** `torch.float16` for non-quantized layers
- **Evidence Ceiling:** 4,000 tokens
- **Output Token Cap:** 2,048 tokens
- **Batch Size:** 1
- **Decoding:** Greedy, `do_sample=False`, `num_beams=1`
- **Thinking Mode:** Explicitly disabled via chat template (`enable_thinking=False`)
- **Generation Attempts:** Exactly 1 generation per task/condition (40 total)
- **Model Steering / LoRA / Training:** None (Zero fine-tuning)

## 3. Representation Conditions
- **Condition W (Whole Files):**
  Complete whole files ordered by BM25 retrieval ranking against the problem statement. Oversized files exceeding the budget are skipped without silent truncation.
- **Condition A (Complete Entities):**
  Complete functions, classes, and top-level code entities ordered by BM25 ranking. Each entity includes full body and line-range metadata (`start_line`-`end_line`). Oversized entities exceeding remaining budget are skipped.
- **Condition B (Compact Signatures & Excerpts):**
  Compact entity representation containing exact signature line, bounded docstring (<=8 lines), and opening excerpt (lines 1-15).
- **Condition C (Full Main + Compact Supporting):**
  Hybrid representation where Rank 1 primary entity is provided in full (as in Condition A), and supporting entities (Rank 2+) are provided in compact form (as in Condition B).

## 4. Benchmark & Deterministic Task Selection
- **Benchmark:** `princeton-nlp/SWE-bench_Lite` (dev split)
- **Pinned Revision:** `6ec7bb89b9342f664a54a6e0a6ea6501d3437cc2`
- **Excluded Tasks (Development Cases):**
  1. `marshmallow-code__marshmallow-1343` (pilot)
  2. `pvlib__pvlib-python-1072` (pilot)
  3. `pydicom__pydicom-1139` (pilot)
  4. `marshmallow-code__marshmallow-1359` (development preflight)
- **Selection Rule:** First 10 remaining instances in strict lexicographic order:
  1. `pvlib__pvlib-python-1154`
  2. `pvlib__pvlib-python-1606`
  3. `pvlib__pvlib-python-1707`
  4. `pvlib__pvlib-python-1854`
  5. `pydicom__pydicom-1256`
  6. `pydicom__pydicom-1413`
  7. `pydicom__pydicom-1694`
  8. `pydicom__pydicom-901`
  9. `pylint-dev__astroid-1196`
  10. `pylint-dev__astroid-1268`
- Total fresh comparison generations: 10 tasks * 4 conditions = 40 generations.

## 5. Frozen Prompt Specification
All conditions share the identical canonical prompt structure, altering only the evidence block and condition metadata:

```
You are an expert software engineer resolving an issue in the repository for task '{task_id}'.

### ISSUE PROBLEM STATEMENT
{problem_statement}

### RELEVANT REPOSITORY CODE (Evidence Condition: {condition})
{evidence_text}

### INSTRUCTIONS
Analyze the issue description and repository code above.
Write a patch that fixes the issue.
Output your patch as a unified diff format inside a ```diff code block.
Ensure file paths in the diff match the repository files (e.g., a/src/... b/src/...).

### PATCH-ONLY INSTRUCTION — fresh instrumented protocol v1
Return only one explicitly labelled diff fenced block containing a unified diff. Use exact repository source context. Do not include explanations, placeholders, ellipses, or text outside the diff block.
```

## 6. Patch Processing Rule
1. Select the last explicitly labelled diff/patch fenced block (````diff` or ````patch`).
2. Preserve exact patch whitespace and ensure trailing newline.
3. Check and apply using `git apply --recount` in an isolated base checkout.
4. Record strict applicability (without recount) and normalized applicability (with recount) separately.
5. Export canonical unified diff from git tree.

## 7. Independent Evaluation
- Evaluation harness: containerized SWE-bench Docker runner (WSL2/Linux).
- In Colab environment where Docker daemon is inaccessible, export complete evaluation bundle and declare results `PENDING_DOCKER_EXECUTION`.
