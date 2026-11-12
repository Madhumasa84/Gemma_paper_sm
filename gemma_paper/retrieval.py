import os
import ast
import math
import re
from collections import Counter
from typing import Dict, Any, List

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())

def extract_entities_from_file(file_path: str, repo_base: str) -> List[Dict[str, Any]]:
    entities = []
    rel_path = os.path.relpath(file_path, repo_base)
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
            lines = code.splitlines(keepends=True)
    except Exception:
        return []

    # Whole file entity
    entities.append({
        "type": "file",
        "file_path": rel_path,
        "name": rel_path,
        "start_line": 1,
        "end_line": len(lines),
        "content": code
    })

    try:
        tree = ast.parse(code)
    except Exception:
        return entities

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            s_line = getattr(node, "lineno", 1)
            e_line = getattr(node, "end_lineno", s_line)
            entity_content = "".join(lines[s_line - 1 : e_line])
            
            # Extract docstring if present
            docstring = ast.get_docstring(node) or ""
            
            entities.append({
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "file_path": rel_path,
                "name": node.name,
                "start_line": s_line,
                "end_line": e_line,
                "content": entity_content,
                "docstring": docstring
            })

    return entities

def build_and_cache_task_ranking(task_id: str, repo_dir: str, problem_statement: str) -> Dict[str, Any]:
    all_entities = []
    indexed_files = 0

    for root, _, files in os.walk(repo_dir):
        # Skip git, tests, docs
        rel = os.path.relpath(root, repo_dir)
        if ".git" in rel.split(os.sep) or "tests" in rel.split(os.sep) or "docs" in rel.split(os.sep):
            continue
        for f in files:
            if f.endswith(".py"):
                f_path = os.path.join(root, f)
                all_entities.extend(extract_entities_from_file(f_path, repo_dir))
                indexed_files += 1

    # BM25 Lexical Ranking against problem_statement
    q_tokens = tokenize(problem_statement)
    q_counts = Counter(q_tokens)
    N = len(all_entities)
    
    doc_tokens = [tokenize(e["content"]) for e in all_entities]
    doc_lens = [len(t) for t in doc_tokens]
    avg_dl = sum(doc_lens) / max(N, 1)

    df = Counter()
    for t_list in doc_tokens:
        for w in set(t_list):
            df[w] += 1

    k1 = 1.5
    b = 0.75
    scored = []
    for idx, e in enumerate(all_entities):
        tokens = doc_tokens[idx]
        tf = Counter(tokens)
        score = 0.0
        for q in q_counts:
            if df[q] > 0:
                idf = math.log((N - df[q] + 0.5) / (df[q] + 0.5) + 1.0)
                denom = tf[q] + k1 * (1.0 - b + b * (doc_lens[idx] / avg_dl))
                score += idf * ((tf[q] * (k1 + 1.0)) / denom)
        scored.append((score, e))

    # Tie-breaking: score desc, length asc, name asc
    scored.sort(key=lambda x: (-x[0], len(x[1]["content"]), x[1]["name"]))

    ranked_entities = [item[1] for item in scored]
    return {
        "task_id": task_id,
        "indexed_file_count": indexed_files,
        "ranked_entities_count": len(ranked_entities),
        "ranked_entities": ranked_entities
    }
