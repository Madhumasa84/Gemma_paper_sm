#!/usr/bin/env python3
"""Offline diagnostic: Compute reference-code visibility across packaging policies.
Evaluator-only analysis. Never modifies retrieval or generates patches.
Usage: python3 paper_v2/build_reference_coverage.py
"""
import os
import sys
import re
import json
import glob
from pathlib import Path

import pyarrow.parquet as pq

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
EVIDENCE_DIR = PROJECT_DIR / "evidence" / "fresh" / "packets"
DATA_DIR = SCRIPT_DIR / "data"
TABLES_DIR = SCRIPT_DIR / "tables"
DATA_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

PARQUET_PATH = PROJECT_DIR / "data" / "swebench_lite_dev.parquet"

def load_dev_split():
    if not PARQUET_PATH.exists():
        raise RuntimeError("Missing pinned dataset. Run python3 scripts/fetch_dataset.py first.")
    return {row["instance_id"]: row for row in pq.read_table(PARQUET_PATH).to_pylist()}

def parse_reference_patch(patch_str: str):
    """Parses a unified diff into per-file modified lines, insertion points, and hunk headers."""
    files = {}
    current_file = None
    old_line = 0

    for line in patch_str.splitlines():
        if line.startswith("--- a/"):
            current_file = line[6:].strip()
            if current_file not in files:
                files[current_file] = {
                    "modified_lines": set(),
                    "insertion_lines": set(),
                    "hunk_headings": []
                }
        elif line.startswith("@@"):
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", line)
            if m:
                old_start = int(m.group(1))
                heading = m.group(5).strip()
                files[current_file]["hunk_headings"].append((old_start, heading))
                old_line = old_start
        elif current_file:
            if line.startswith("-"):
                files[current_file]["modified_lines"].add(old_line)
                old_line += 1
            elif line.startswith("+"):
                # Insertion point at adjacent base line
                files[current_file]["insertion_lines"].add(old_line)
            elif line.startswith(" "):
                old_line += 1

    return files

# Target entity mappings based on ground truth modified entities in SWE-bench Lite base commits
# Each entry is (file_path, entity_name, approx_start_line, approx_end_line)
KNOWN_TARGET_ENTITIES = {
    "pvlib__pvlib-python-1154": [("pvlib/irradiance.py", "reindl", 793, 894)],
    "pvlib__pvlib-python-1606": [("pvlib/tools.py", "_golden_sect_DataFrame", 341, 396)],
    "pvlib__pvlib-python-1707": [("pvlib/iam.py", "physical", 94, 225)],
    "pvlib__pvlib-python-1854": [("pvlib/pvsystem.py", "PVSystem", 69, 450)],
    "pydicom__pydicom-1256": [("pydicom/jsonrep.py", "get_sequence_item", 207, 234)],
    "pydicom__pydicom-1413": [("pydicom/dataelem.py", "value", 433, 460)],
    "pydicom__pydicom-1694": [("pydicom/dataset.py", "to_json_dict", 2480, 2520)],
    "pydicom__pydicom-901": [("pydicom/config.py", "debug", 110, 142)],
    "pylint-dev__astroid-1196": [("astroid/nodes/node_classes.py", "getitem", 2345, 2370)],
    "pylint-dev__astroid-1268": [("astroid/nodes/as_string.py", "AsStringVisitor", 75, 700)],
    "marshmallow-code__marshmallow-1343": [("src/marshmallow/schema.py", "_invoke_field_validators", 877, 900)],
    "pvlib__pvlib-python-1072": [("pvlib/temperature.py", "fuentes", 520, 650)],
    "pydicom__pydicom-1139": [("pydicom/valuerep.py", "PersonName", 710, 775)],
}

def parse_packet_visibility(evidence_text: str, condition: str):
    """Extracts visible files, entities, and line number ranges from rendered evidence packet text."""
    visible_files = set()
    visible_entities = set() # (file_path, entity_name)
    visible_lines = {} # file_path -> set of line numbers

    # Split by block header '### '
    blocks = re.split(r"(?m)^###\s+", evidence_text)
    for block in blocks:
        if not block.strip():
            continue
        first_line = block.splitlines()[0].strip()

        # Condition W: File: <path>
        if first_line.startswith("File: "):
            fpath = first_line[6:].strip()
            visible_files.add(fpath)
            # Find code block
            cm = re.search(r"```python\n(.*?)```", block, re.DOTALL)
            line_count = len(cm.group(1).splitlines()) if cm else 0
            if fpath not in visible_lines:
                visible_lines[fpath] = set()
            visible_lines[fpath].update(range(1, line_count + 1))

        # Condition A: Entity: <name> (<path>:<start>-<end>)
        elif first_line.startswith("Entity: "):
            m = re.match(r"Entity:\s+([^\s\(]+)\s+\(([^:]+):(\d+)-(\d+)\)", first_line)
            if m:
                ename, fpath, s, e = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
                visible_files.add(fpath)
                visible_entities.add((fpath, ename))
                if fpath not in visible_lines:
                    visible_lines[fpath] = set()
                visible_lines[fpath].update(range(s, e + 1))

        # Condition C Primary: [PRIMARY] <name> (<path>:<start>-<end>)
        elif first_line.startswith("[PRIMARY] "):
            m = re.match(r"\[PRIMARY\]\s+([^\s\(]+)\s+\(([^:]+):(\d+)-(\d+)\)", first_line)
            if m:
                ename, fpath, s, e = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
                visible_files.add(fpath)
                visible_entities.add((fpath, ename))
                if fpath not in visible_lines:
                    visible_lines[fpath] = set()
                visible_lines[fpath].update(range(s, e + 1))

        # Condition C Supporting: [SUPPORTING] <name> (<path>:<start>)
        elif first_line.startswith("[SUPPORTING] "):
            m = re.match(r"\[SUPPORTING\]\s+([^\s\(]+)\s+\(([^:]+):(\d+)\)", first_line)
            if m:
                ename, fpath, s = m.group(1), m.group(2), int(m.group(3))
                visible_files.add(fpath)
                visible_entities.add((fpath, ename))
                em = re.search(r"Excerpt:\n(.*)", block, re.DOTALL)
                n_exc = len(em.group(1).splitlines()) if em else 0
                if fpath not in visible_lines:
                    visible_lines[fpath] = set()
                # Lines 1 to 9 of entity body (start+1 to start+n_exc)
                visible_lines[fpath].update(range(s + 1, s + 1 + n_exc))

        # Condition B: <name> (<path>:<start>)
        else:
            m = re.match(r"([^\s\(]+)\s+\(([^:]+):(\d+)\)", first_line)
            if m:
                ename, fpath, s = m.group(1), m.group(2), int(m.group(3))
                visible_files.add(fpath)
                visible_entities.add((fpath, ename))
                em = re.search(r"Excerpt:\n(.*)", block, re.DOTALL)
                n_exc = len(em.group(1).splitlines()) if em else 0
                if fpath not in visible_lines:
                    visible_lines[fpath] = set()
                # Lines 1 to 14 of entity body (start+1 to start+n_exc)
                visible_lines[fpath].update(range(s + 1, s + 1 + n_exc))

    return visible_files, visible_entities, visible_lines

def main():
    dev_map = load_dev_split()
    packet_files = sorted(glob.glob(str(EVIDENCE_DIR / "*__packet.json")))
    print(f"Loaded {len(dev_map)} dev instances, found {len(packet_files)} frozen comparison packets.")

    rows = []

    for p_path in packet_files:
        with open(p_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        iid = data["instance_id"]
        cond = data["condition"]
        ev_tokens = data.get("evidence_tokens", 0)
        ev_text = data.get("evidence_text", "")

        row_data = dev_map[iid]
        patch_str = row_data["patch"]
        patch_files = parse_reference_patch(patch_str)
        ref_files = set(patch_files.keys())

        # Target entities for task
        known_entities = KNOWN_TARGET_ENTITIES.get(iid, [])
        ref_entities = set((fpath, ename) for fpath, ename, _, _ in known_entities)
        if not ref_entities:
            # Fallback to hunk headings
            for fpath, finfo in patch_files.items():
                for _, h in finfo["hunk_headings"]:
                    if h:
                        ref_entities.add((fpath, h.split("(")[0].replace("def ", "").replace("class ", "").strip()))

        # Determine all edit site lines (removed lines + insertion anchor lines)
        all_edit_sites = {} # file -> set of lines
        for fpath, finfo in patch_files.items():
            sites = set(finfo["modified_lines"])
            if not sites:
                sites = set(finfo["insertion_lines"])
            all_edit_sites[fpath] = sites

        vis_files, vis_entities, vis_lines = parse_packet_visibility(ev_text, cond)

        # For Policy W (whole files), enclosing entities in visible files are included
        if cond == "W":
            for fpath, ename, s, e in known_entities:
                if fpath in vis_files and fpath in vis_lines:
                    # Check if entity lines are within visible lines
                    if set(range(s, e + 1)).issubset(vis_lines[fpath]) or len(set(range(s, e + 1)).intersection(vis_lines[fpath])) > 0:
                        vis_entities.add((fpath, ename))

        # 1. File coverage
        files_covered = len(ref_files.intersection(vis_files))
        files_total = len(ref_files)
        file_cov_pct = (files_covered / files_total * 100.0) if files_total > 0 else 0.0

        # 2. Entity coverage
        entities_covered = len(ref_entities.intersection(vis_entities)) if ref_entities else 0
        entities_total = len(ref_entities) if ref_entities else 1
        entity_cov_pct = (entities_covered / entities_total * 100.0) if entities_total > 0 else 0.0

        # 3. Edit-site line coverage
        total_edit_lines = sum(len(lines) for lines in all_edit_sites.values())
        covered_edit_lines = 0
        for fpath, lines in all_edit_sites.items():
            if fpath in vis_lines:
                covered_edit_lines += len(lines.intersection(vis_lines[fpath]))
        line_cov_pct = (covered_edit_lines / total_edit_lines * 100.0) if total_edit_lines > 0 else 0.0

        rows.append({
            "instance_id": iid,
            "condition": cond,
            "evidence_tokens": ev_tokens,
            "ref_files_total": files_total,
            "ref_files_covered": files_covered,
            "file_coverage_pct": round(file_cov_pct, 1),
            "ref_entities_total": entities_total,
            "ref_entities_covered": entities_covered,
            "entity_coverage_pct": round(entity_cov_pct, 1),
            "edit_sites_total": total_edit_lines,
            "edit_sites_covered": covered_edit_lines,
            "edit_site_coverage_pct": round(line_cov_pct, 1),
            "any_file_overlap": files_covered > 0,
            "any_entity_overlap": entities_covered > 0,
            "any_line_overlap": covered_edit_lines > 0,
            "packet_file": Path(p_path).name
        })

    # Output CSVs
    csv_out = DATA_DIR / "reference_coverage.csv"
    with open(csv_out, "w", encoding="utf-8") as f:
        headers = list(rows[0].keys())
        f.write(",".join(headers) + "\n")
        for r in rows:
            f.write(",".join(str(r[h]) for h in headers) + "\n")
    print(f"Wrote {len(rows)} rows to {csv_out}")

    # Generate summary table for LaTeX
    print("\n" + "=" * 80)
    print("REFERENCE COVERAGE SUMMARY ACROSS ALL 40 FRESH PACKETS (10 TASKS)")
    print("=" * 80)
    print(f"{'Cond':<5} | {'Packets':<7} | {'File Overlap':<13} | {'Entity Overlap':<15} | {'Edit-Site Overlap':<18} | {'Mean Line Cov %'}")
    print("-" * 80)

    summary_rows = []
    for cond in ["W", "A", "B", "C"]:
        cond_rows = [r for r in rows if r["condition"] == cond]
        n_pkts = len(cond_rows)
        file_ol = sum(1 for r in cond_rows if r["any_file_overlap"])
        ent_ol = sum(1 for r in cond_rows if r["any_entity_overlap"])
        line_ol = sum(1 for r in cond_rows if r["any_line_overlap"])
        mean_line_cov = sum(r["edit_site_coverage_pct"] for r in cond_rows) / n_pkts

        # Numerators & Denominators for files, entities, lines
        tot_files = sum(r["ref_files_total"] for r in cond_rows)
        cov_files = sum(r["ref_files_covered"] for r in cond_rows)
        tot_ents = sum(r["ref_entities_total"] for r in cond_rows)
        cov_ents = sum(r["ref_entities_covered"] for r in cond_rows)
        tot_lines = sum(r["edit_sites_total"] for r in cond_rows)
        cov_lines = sum(r["edit_sites_covered"] for r in cond_rows)

        print(f"{cond:<5} | {n_pkts:<7} | {file_ol}/10 ({cov_files}/{tot_files}) | {ent_ol}/10 ({cov_ents}/{tot_ents})   | {line_ol}/10 ({cov_lines}/{tot_lines})       | {mean_line_cov:.1f}%")

        summary_rows.append({
            "condition": cond,
            "packets": n_pkts,
            "file_overlap_packets": f"{file_ol}/{n_pkts}",
            "file_counts": f"{cov_files}/{tot_files}",
            "entity_overlap_packets": f"{ent_ol}/{n_pkts}",
            "entity_counts": f"{cov_ents}/{tot_ents}",
            "line_overlap_packets": f"{line_ol}/{n_pkts}",
            "line_counts": f"{cov_lines}/{tot_lines}",
            "mean_line_cov": f"{mean_line_cov:.1f}\\%"
        })

    # Write LaTeX summary table
    tex_path = TABLES_DIR / "coverage_summary.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\\begin{tabular}{lrrrrr}\n\\toprule\n")
        f.write("Policy & File overlap & Files visible & Entity overlap & Edit-site overlap & Edit lines visible \\\\\n\\midrule\n")
        for sr in summary_rows:
            f.write(f"{sr['condition']} & {sr['file_overlap_packets']} & {sr['file_counts']} & {sr['entity_overlap_packets']} & {sr['line_overlap_packets']} & {sr['line_counts']} ({sr['mean_line_cov']}) \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n")
    print(f"Wrote LaTeX table to {tex_path}")

if __name__ == "__main__":
    main()
