import os
import json
from typing import Dict, Any, List, Tuple, Optional
from gemma_paper.workspace import WORKSPACE_DIR
from gemma_paper.dataset_prep import load_and_select_tasks, prepare_repository_at_base_commit
from gemma_paper.retrieval import build_and_cache_task_ranking

EVIDENCE_BUDGET = 4000
CONDITIONS = ["W", "A", "B", "C"]

def pack_evidence_for_condition(
    condition: str,
    ranking: Dict[str, Any],
    processor: Any,
    budget: int = EVIDENCE_BUDGET
) -> Tuple[str, int, Dict[str, Any]]:
    """Packs ranked entities into representation format respecting token ceiling."""
    tokenizer = getattr(processor, "tokenizer", processor)
    
    packed_pieces = []
    total_tokens = 0
    entities_included = 0
    
    if condition == "W":
        # Whole files only in rank order; skip oversized files
        file_entities = [e for e in ranking["ranked_entities"] if e["type"] == "file"]
        seen_files = set()
        for e in file_entities:
            if e["file_path"] in seen_files:
                continue
            seen_files.add(e["file_path"])
            text_block = f"### File: {e['file_path']}\n```python\n{e['content']}\n```\n"
            tok_count = len(tokenizer.encode(text_block, add_special_tokens=False))
            if tok_count > budget:
                # Oversized file skipped without silent truncation
                continue
            if total_tokens + tok_count <= budget:
                packed_pieces.append(text_block)
                total_tokens += tok_count
                entities_included += 1

    elif condition == "A":
        # Complete code-entity bodies
        func_class = [e for e in ranking["ranked_entities"] if e["type"] in ("function", "class")]
        for e in func_class:
            text_block = f"### Entity: {e['name']} ({e['file_path']}:{e['start_line']}-{e['end_line']})\n```python\n{e['content']}\n```\n"
            tok_count = len(tokenizer.encode(text_block, add_special_tokens=False))
            if total_tokens + tok_count <= budget:
                packed_pieces.append(text_block)
                total_tokens += tok_count
                entities_included += 1

    elif condition == "B":
        # Exact signatures, bounded docstrings (<=8 lines), and selected excerpts
        func_class = [e for e in ranking["ranked_entities"] if e["type"] in ("function", "class")]
        for e in func_class:
            lines = e["content"].splitlines()
            sig_line = lines[0] if lines else e["name"]
            doc_lines = e.get("docstring", "").splitlines()[:8]
            doc_text = "\n".join(doc_lines)
            body_excerpt = "\n".join(lines[1:15]) if len(lines) > 1 else ""
            compact_repr = f"### {e['name']} ({e['file_path']}:{e['start_line']})\nSignature: {sig_line}\nDocstring: {doc_text}\nExcerpt:\n{body_excerpt}\n"
            tok_count = len(tokenizer.encode(compact_repr, add_special_tokens=False))
            if total_tokens + tok_count <= budget:
                packed_pieces.append(compact_repr)
                total_tokens += tok_count
                entities_included += 1

    elif condition == "C":
        # Condition C: Rank 1 entity rendered in full (Condition A); Rank 2+ entities rendered compact (Condition B)
        func_class = [e for e in ranking["ranked_entities"] if e["type"] in ("function", "class")]
        for idx, e in enumerate(func_class):
            if idx == 0:
                # Full body
                text_block = f"### [PRIMARY] {e['name']} ({e['file_path']}:{e['start_line']}-{e['end_line']})\n```python\n{e['content']}\n```\n"
            else:
                # Compact supporting
                lines = e["content"].splitlines()
                sig_line = lines[0] if lines else e["name"]
                excerpt = "\n".join(lines[1:10]) if len(lines) > 1 else ""
                text_block = f"### [SUPPORTING] {e['name']} ({e['file_path']}:{e['start_line']})\n{sig_line}\nExcerpt:\n{excerpt}\n"
            
            tok_count = len(tokenizer.encode(text_block, add_special_tokens=False))
            if total_tokens + tok_count <= budget:
                packed_pieces.append(text_block)
                total_tokens += tok_count
                entities_included += 1

    packed_text = "\n".join(packed_pieces)
    verification = {
        "budget_limit": budget,
        "token_count": total_tokens,
        "under_ceiling": total_tokens <= budget,
        "entities_included": entities_included,
        "all_passed": total_tokens <= budget
    }
    return packed_text, total_tokens, verification

def generate_all_12_evidence_packets(
    processor: Any,
    output_dir: Optional[str] = None,
    repos_base_dir: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if output_dir is None:
        output_dir = os.path.join(WORKSPACE_DIR, "evidence_packets")
    if repos_base_dir is None:
        repos_base_dir = os.path.join(WORKSPACE_DIR, "task_repos")
    os.makedirs(output_dir, exist_ok=True)
    selected_tasks, _ = load_and_select_tasks()

    all_packets = []
    summary_rows = []

    for task in selected_tasks:
        task_id = task["instance_id"]
        repo = task["repo"]
        base_commit = task["base_commit"]
        prob_statement = task["problem_statement"]

        repo_dir = os.path.join(repos_base_dir, task_id.replace("/", "__"))
        prepare_repository_at_base_commit(repo, base_commit, repo_dir)

        ranking = build_and_cache_task_ranking(task_id, repo_dir, prob_statement)

        for cond in CONDITIONS:
            packed_text, token_count, verif = pack_evidence_for_condition(
                condition=cond,
                ranking=ranking,
                processor=processor,
                budget=EVIDENCE_BUDGET
            )

            packet_obj = {
                "packet_id": f"{task_id}__{cond}",
                "instance_id": task_id,
                "repo": repo,
                "base_commit": base_commit,
                "condition": cond,
                "problem_statement": prob_statement,
                "evidence_text": packed_text,
                "token_count": token_count,
                "model_revision": "4ecc2ba63bcac23ba4a767fc87025b1450f84c9c",
                "qa_verification": verif
            }

            file_path = os.path.join(output_dir, f"{task_id}__{cond}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(packet_obj, f, indent=2)

            all_packets.append(packet_obj)
            summary_rows.append({
                "packet_id": packet_obj["packet_id"],
                "condition": cond,
                "tokens": token_count,
                "passed": verif["all_passed"],
                "file": file_path
            })

    return all_packets, summary_rows

def print_packet_summary_table(summary_rows: List[Dict[str, Any]]):
    print("=" * 80)
    print(f"{'Packet ID':<46} | {'Cond':<4} | {'Tokens':<6} | {'QA Status'}")
    print("-" * 80)
    for r in summary_rows:
        status_str = "PASS" if r["passed"] else "FAIL"
        print(f"{r['packet_id']:<46} | {r['condition']:<4} | {r['tokens']:<6} | {status_str}")
    print("=" * 80)
