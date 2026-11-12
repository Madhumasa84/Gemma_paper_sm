#!/usr/bin/env python3
"""Render publication figures for paper_v2 from frozen experimental records.
Adheres strictly to the scientific-figure-making house style from figures4papers:
- Minimalist, high-contrast publication design
- Clean sans-serif typography (Arial/Helvetica/DejaVu Sans)
- TrueType/Type 42 vector font embedding (pdf.fonttype = 42)
- Minimal spines (top and right off, linewidth = 1.6-2.0)
- Frameless legends (frameon = False)
- Canonical PALETTE semantic colors with sharp black bar edges
- 300 DPI print-ready vector PDF and high-res PNG export
Usage: python3 paper_v2/build_plots.py
"""
import os
import sys
import json
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# ── figures4papers Style Configuration ─────────────────────────────────────
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "sans-serif"]
matplotlib.rcParams["font.size"] = 10.5
matplotlib.rcParams["axes.labelsize"] = 11
matplotlib.rcParams["axes.titlesize"] = 12
matplotlib.rcParams["xtick.labelsize"] = 9.5
matplotlib.rcParams["ytick.labelsize"] = 9.5
matplotlib.rcParams["legend.fontsize"] = 9
matplotlib.rcParams["axes.spines.top"] = False
matplotlib.rcParams["axes.spines.right"] = False
matplotlib.rcParams["axes.linewidth"] = 1.6
matplotlib.rcParams["legend.frameon"] = False
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["svg.fonttype"] = "none"

# Canonical figures4papers PALETTE
PALETTE = {
    "blue_main": "#0F4D92",       # Key method / Primary result (e.g. Strict clean, Policy A)
    "blue_secondary": "#3775BA",  # Supporting blue / Prompt wrapper
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",         # Positive / Recount-assisted / Verified
    "red_1": "#F6CFCB",
    "red_2": "#E9A6A1",
    "red_strong": "#B64342",      # Baseline / Failures / Budget ceiling / Contrast
    "neutral": "#CFCECE",         # Background / Unstarted / Gap
    "neutral_dark": "#4D4D4D",
    "highlight": "#FFD700",       # Accent / Interrupted / Callout
    "teal": "#42949E",            # Secondary category
    "violet": "#9A4D8E",          # Truncation / No block
}

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RESULT_DATA = SCRIPT_DIR / "data"
V2_DATA = SCRIPT_DIR / "data"
FIG_DIR = SCRIPT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Load Verified Data ─────────────────────────────────────────────────────
with open(V2_DATA / "reference_coverage.csv", "r", encoding="utf-8") as f:
    cov_rows = list(csv.DictReader(f))

with open(RESULT_DATA / "fresh_rows.csv", "r", encoding="utf-8") as f:
    fresh_rows = list(csv.DictReader(f))

with open(RESULT_DATA / "pilot_rows.csv", "r", encoding="utf-8") as f:
    pilot_rows = list(csv.DictReader(f))

with open(RESULT_DATA / "native_controls.csv", "r", encoding="utf-8") as f:
    ctrl_rows = list(csv.DictReader(f))

tasks = sorted(list(set(r["instance_id"] for r in fresh_rows)))
short_tasks = [t.split("__")[1].replace("pvlib-python-", "pvlib-").replace("pydicom-", "pydicom-").replace("astroid-", "astroid-") for t in tasks]
conds = ["W", "A", "B", "C"]


# ── Figure 1: Evidence Budget & Input Tokens across 40 Packets ─────────────
def plot_fig1_tokens():
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    y_positions = []
    y_labels = []
    cur_y = 0

    for t, st in zip(tasks, short_tasks):
        t_rows = [r for r in fresh_rows if r["instance_id"] == t]
        for cond in conds:
            cr = [r for r in t_rows if r["condition"] == cond]
            if cr:
                r = cr[0]
                ev = int(r["evidence_tokens"])
                inp = int(r["input_tokens"]) if r["input_tokens"] else ev + 350
                # Bar for evidence tokens
                ax.barh(cur_y, ev, height=0.72, color=PALETTE["blue_main"], edgecolor="black", linewidth=0.7, zorder=3)
                # Bar for prompt wrapper
                ax.barh(cur_y, inp - ev, left=ev, height=0.72, color=PALETTE["blue_secondary"], alpha=0.55, edgecolor="black", linewidth=0.7, zorder=3)
                y_positions.append(cur_y)
                y_labels.append(f"{st} {cond}")
                cur_y += 1
        cur_y += 0.5  # gap between tasks

    ax.axvline(x=4000, color=PALETTE["red_strong"], linestyle="--", linewidth=1.6, zorder=4, label="Evidence Ceiling (4,000 tokens)")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=7.2)
    ax.tick_params(axis="x", direction="out", length=4, width=1.2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Tokens (Gemma 4 Tokenizer)", fontsize=10.5, fontweight="semibold")
    ax.set_title("Evidence Budget & Total Input Tokens across 40 Frozen Packets", fontsize=11.5, pad=12, fontweight="bold")
    ax.set_xlim(0, 6800)
    ax.invert_yaxis()

    ev_patch = mpatches.Patch(facecolor=PALETTE["blue_main"], edgecolor="black", linewidth=0.7, label="Evidence tokens (<= 4,000)")
    wrap_patch = mpatches.Patch(facecolor=PALETTE["blue_secondary"], alpha=0.55, edgecolor="black", linewidth=0.7, label="Prompt wrapper & issue text")
    ceil_line = plt.Line2D([0], [0], color=PALETTE["red_strong"], linestyle="--", linewidth=1.6, label="4,000-token evidence ceiling")
    ax.legend(handles=[ev_patch, wrap_patch, ceil_line], loc="lower right", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_tokens.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_tokens.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_tokens")


# ── Figure 2: Reference Code Visibility under 4,000-Token Budget ───────────
def plot_fig2_reference_coverage():
    fig, ax = plt.subplots(figsize=(6.8, 4.2))

    file_overlap_pcts = []
    entity_overlap_pcts = []
    line_cov_pcts = []

    for c in conds:
        c_rows = [r for r in cov_rows if r["condition"] == c]
        n = len(c_rows)
        file_overlap_pcts.append(sum(1 for r in c_rows if r["any_file_overlap"] == "True") / n * 100)
        entity_overlap_pcts.append(sum(1 for r in c_rows if r["any_entity_overlap"] == "True") / n * 100)
        line_cov_pcts.append(sum(float(r["edit_site_coverage_pct"]) for r in c_rows) / n)

    x = np.arange(len(conds))
    width = 0.26

    rects1 = ax.bar(x - width, file_overlap_pcts, width, label="Reference File Visible (%)",
                    color=PALETTE["blue_main"], edgecolor="black", linewidth=1.2, zorder=3)
    rects2 = ax.bar(x, entity_overlap_pcts, width, label="Reference Entity Visible (%)",
                    color=PALETTE["green_3"], edgecolor="black", linewidth=1.2, zorder=3)
    rects3 = ax.bar(x + width, line_cov_pcts, width, label="Mean Edit Lines Visible (%)",
                    color=PALETTE["teal"], edgecolor="black", linewidth=1.2, zorder=3)

    # In-place bold annotations
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.0f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.5, fontweight="semibold")
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.0f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.5, fontweight="semibold")
    for rect in rects3:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.5, fontweight="bold", color=PALETTE["neutral_dark"])

    ax.set_ylabel("Percentage (%)", fontsize=11, fontweight="semibold")
    ax.set_title("Reference Code Visibility under 4,000-Token Evidence Budget (N=10 Tasks)",
                 fontsize=11.5, pad=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["W\n(Whole Files)", "A\n(Entities)", "B\n(Compact)", "C\n(Hybrid)"],
                       fontsize=9.5, fontweight="semibold")
    ax.tick_params(axis="y", direction="out", length=4, width=1.2)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 120)
    ax.yaxis.grid(True, linestyle=":", alpha=0.5, color=PALETTE["neutral"])
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_reference_coverage.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_reference_coverage.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_reference_coverage")


# ── Figure 3: Execution & Application Status Grid across 40 Pairs ──────────
def plot_fig3_status():
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    grid = np.zeros((len(tasks), 4))

    for i, t in enumerate(tasks):
        for j, c in enumerate(conds):
            r = [x for x in fresh_rows if x["instance_id"] == t and x["condition"] == c][0]
            if r["completed"] == "True":
                if r["strict_applicable"] == "True":
                    grid[i, j] = 4
                elif r["recount_applicable"] == "True":
                    grid[i, j] = 3
                else:
                    grid[i, j] = 2
            else:
                if r["generation_status"] == "INTERRUPTED":
                    grid[i, j] = 1
                else:
                    grid[i, j] = 0

    cmap = {
        0: (PALETTE["neutral"], "? Unstarted (unknown outcome)"),
        1: (PALETTE["highlight"], "I Interrupted in-flight"),
        2: (PALETTE["red_strong"], "F Application failed"),
        3: (PALETTE["green_3"], "R Applied with recount"),
        4: (PALETTE["blue_main"], "S Strict clean application")
    }

    for i in range(len(tasks)):
        for j in range(4):
            val = int(grid[i, j])
            col, _ = cmap[val]
            ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=col, edgecolor="white", linewidth=2.0))
            txt = "?" if val == 0 else "I" if val == 1 else "F" if val == 2 else "R" if val == 3 else "S"
            txt_col = "white" if val in (2, 4) else "#222222"
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", color=txt_col, fontweight="bold", fontsize=10.5)

    ax.set_xlim(0, 4)
    ax.set_ylim(0, len(tasks))
    ax.set_xticks([0.5, 1.5, 2.5, 3.5])
    ax.set_xticklabels(["Policy W\n(Whole)", "Policy A\n(Entities)", "Policy B\n(Compact)", "Policy C\n(Hybrid)"],
                       fontsize=9.5, fontweight="semibold")
    ax.set_yticks(np.arange(len(tasks)) + 0.5)
    ax.set_yticklabels(short_tasks, fontsize=9)
    ax.tick_params(length=0)
    ax.invert_yaxis()
    ax.set_title("Execution & Application Status across 40 Fresh Attempts", fontsize=11.5, pad=12, fontweight="bold")

    legend_patches = [mpatches.Patch(facecolor=c[0], edgecolor="black", linewidth=0.8, label=c[1])
                      for c in [cmap[4], cmap[3], cmap[2], cmap[1], cmap[0]]]
    ax.legend(handles=legend_patches, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_status.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_status.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_status")


# ── Figure 4: Matched Tasks Application (Denominator = 5) ──────────────────
def plot_fig4_matched_application():
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    complete_tasks = ["pvlib__pvlib-python-1154", "pvlib__pvlib-python-1606", "pvlib__pvlib-python-1707", "pvlib__pvlib-python-1854", "pydicom__pydicom-1256"]
    matched_rows = [r for r in fresh_rows if r["instance_id"] in complete_tasks]

    strict_counts = []
    recount_counts = []
    for c in conds:
        c_m = [r for r in matched_rows if r["condition"] == c]
        strict_counts.append(sum(1 for r in c_m if r["strict_applicable"] == "True"))
        recount_counts.append(sum(1 for r in c_m if r["recount_applicable"] == "True"))

    x = np.arange(len(conds))
    width = 0.32

    rects1 = ax.bar(x - width/2, strict_counts, width, label="Strict Application (as emitted)",
                    color=PALETTE["blue_main"], edgecolor="black", linewidth=1.2, zorder=3)
    rects2 = ax.bar(x + width/2, recount_counts, width, label="Recount-Assisted Application",
                    color=PALETTE["green_3"], edgecolor="black", linewidth=1.2, zorder=3)

    for i in range(len(conds)):
        ax.annotate(f"{strict_counts[i]}/5", xy=(x[i] - width/2, strict_counts[i]),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9, fontweight="semibold")
        ax.annotate(f"{recount_counts[i]}/5", xy=(x[i] + width/2, recount_counts[i]),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9, fontweight="bold")

    ax.set_ylabel("Applicable Patches (out of 5 tasks)", fontsize=10.5, fontweight="semibold")
    ax.set_title("Application Success on 5 Complete Task Sets (Denominator = 5)",
                 fontsize=11.5, pad=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["W: Whole", "A: Entities", "B: Excerpts", "C: Hybrid"], fontsize=9.5, fontweight="semibold")
    ax.tick_params(axis="y", direction="out", length=4, width=1.2)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 5.8)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.yaxis.grid(True, linestyle=":", alpha=0.5, color=PALETTE["neutral"])
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_matched_application.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_matched_application.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_matched_application")


# ── Figure 5: Application Outcome Categories for 22 Completions ────────────
def plot_fig5_error_cats():
    fig, ax = plt.subplots(figsize=(5.4, 4.0))
    completed = [r for r in fresh_rows if r["completed"] == "True"]
    n_comp = len(completed)

    n_strict = sum(1 for r in completed if r["strict_applicable"] == "True")
    n_recount = sum(1 for r in completed if r["strict_applicable"] == "False" and r["recount_applicable"] == "True")
    n_mismatch = sum(1 for r in completed if r["recount_applicable"] == "False" and "patch does not apply" in r["apply_error"])
    n_no_patch = sum(1 for r in completed if "No patch block found" in r["apply_error"])
    n_corrupt = sum(1 for r in completed if "corrupt" in r["apply_error"])

    cats = [
        f"Strict clean (n={n_strict})",
        f"Recount only (n={n_recount})",
        f"Source mismatch (n={n_mismatch})",
        f"No block found (n={n_no_patch})",
        f"Corrupt header (n={n_corrupt})"
    ]
    counts = [n_strict, n_recount, n_mismatch, n_no_patch, n_corrupt]
    colors = [PALETTE["blue_main"], PALETTE["green_3"], PALETTE["red_strong"], PALETTE["violet"], PALETTE["red_2"]]

    wedges, texts, autotexts = ax.pie(
        counts, labels=cats,
        autopct=lambda p: f"{p:.0f}%",
        pctdistance=0.72,
        startangle=140,
        colors=colors,
        wedgeprops=dict(edgecolor="black", linewidth=1.2, width=0.45), # Donut style
        textprops={"fontsize": 8.5, "fontweight": "semibold"}
    )
    for at in autotexts:
        at.set_fontsize(9.5)
        at.set_fontweight("bold")
        at.set_color("white")

    # Center label in donut hole
    ax.text(0, 0, f"N = {n_comp}\nTotal", ha="center", va="center", fontsize=11, fontweight="bold", color=PALETTE["neutral_dark"])
    ax.set_title("Application Outcomes for 22 Recovered Completions", fontsize=11.5, pad=12, fontweight="bold")

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_error_cats.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_error_cats.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_error_cats")


# ── Figure 6: Generated Length & Output Cap (N=22 Completions) ─────────────
def plot_fig6_outputs():
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    comp_rows = [r for r in fresh_rows if r["completed"] == "True"]

    xs = np.arange(len(comp_rows))
    gen_tokens = [int(r["generated_tokens"]) for r in comp_rows]
    colors_out = [PALETTE["blue_main"] if r["recount_applicable"] == "True" else PALETTE["red_strong"] for r in comp_rows]
    markers_out = ["s" if r["hit_token_cap"] == "True" else "o" for r in comp_rows]
    labels_out = [f"{r['instance_id'].split('__')[1].replace('pvlib-python-', 'pv-').replace('pydicom-', 'pd-')}/{r['condition']}" for r in comp_rows]

    for i, (gt, c, m) in enumerate(zip(gen_tokens, colors_out, markers_out)):
        sz = 75 if m == "s" else 60
        ax.scatter(i, gt, color=c, marker=m, s=sz, zorder=3, edgecolors="black", linewidth=1.1)

    ax.axhline(y=2048, color=PALETTE["red_strong"], linestyle="--", linewidth=1.5, zorder=2, label="Output token cap (2,048)")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels_out, rotation=70, ha="right", fontsize=8)
    ax.tick_params(axis="y", direction="out", length=4, width=1.2)
    ax.tick_params(axis="x", length=3)
    ax.set_ylabel("Generated Tokens", fontsize=10.5, fontweight="semibold")
    ax.set_title("Generated Tokens and Stopping Condition (N=22 Completions)", fontsize=11.5, pad=10, fontweight="bold")
    ax.yaxis.grid(True, linestyle=":", alpha=0.5, color=PALETTE["neutral"])
    ax.set_axisbelow(True)

    cap_patch = plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=PALETTE["red_strong"], markeredgecolor="black", markersize=8, label="Token cap reached (4 attempts, failed)")
    app_patch = plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE["blue_main"], markeredgecolor="black", markersize=8, label="Applicable patch (10 attempts)")
    fail_patch = plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE["red_strong"], markeredgecolor="black", markersize=8, label="Failed patch (12 attempts)")
    ax.legend(handles=[cap_patch, app_patch, fail_patch], loc="upper left", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_outputs.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_outputs.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_outputs")


# ── Figure 7: Control Verification (6 of 10 Tasks Verified) ────────────────
def plot_fig7_controls():
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ctrl_tasks = [r["instance_id"].split("__")[1].replace("pvlib-python-", "pvlib-").replace("pydicom-", "pydicom-").replace("astroid-", "astroid-") for r in ctrl_rows]
    p2p_passed = [int(r["reference_preservation_passed"]) for r in ctrl_rows]
    p2p_total = [int(r["required_preservation"]) for r in ctrl_rows]
    verified_status = [r["verified"] == "True" for r in ctrl_rows]

    y = np.arange(len(ctrl_tasks))
    bar_colors = [PALETTE["blue_main"] if v else PALETTE["highlight"] for v in verified_status]

    ax.barh(y, p2p_passed, height=0.62, color=bar_colors, edgecolor="black", linewidth=0.9, zorder=3)
    gap = [tot - pass_c for tot, pass_c in zip(p2p_total, p2p_passed)]
    ax.barh(y, gap, height=0.62, left=p2p_passed, color=PALETTE["neutral"], edgecolor="black", linewidth=0.9, zorder=3)

    for i, (p, t) in enumerate(zip(p2p_passed, p2p_total)):
        if t > 0:
            ax.text(t + 2, i, f"{p}/{t}", va="center", fontsize=8.5, fontweight="semibold")
        else:
            ax.text(2, i, "0/0 (no P2P required)", va="center", fontsize=8, fontstyle="italic")

    ax.set_yticks(y)
    ax.set_yticklabels(ctrl_tasks, fontsize=9)
    ax.tick_params(axis="x", direction="out", length=4, width=1.2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Required Preservation Tests (P2P)", fontsize=10.5, fontweight="semibold")
    ax.set_title("Native Evaluation Control Verification (6 of 10 Tasks Verified)", fontsize=11.5, pad=12, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, max(p2p_total) + 12)
    ax.xaxis.grid(True, linestyle=":", alpha=0.5, color=PALETTE["neutral"])
    ax.set_axisbelow(True)

    v_patch = mpatches.Patch(facecolor=PALETTE["blue_main"], edgecolor="black", linewidth=0.9, label="Fully verified reference control (6 tasks)")
    nv_patch = mpatches.Patch(facecolor=PALETTE["highlight"], edgecolor="black", linewidth=0.9, label="Incomplete reference verification (4 tasks)")
    gap_patch = mpatches.Patch(facecolor=PALETTE["neutral"], edgecolor="black", linewidth=0.9, label="Unconfirmed / errored / failed P2P tests")
    ax.legend(handles=[v_patch, nv_patch, gap_patch], loc="lower right", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_controls.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_controls.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_controls")


# ── Figure 8: Test Outcomes for 10 Tested Fresh Patches ─────────────────────
def plot_fig8_test_outcomes():
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    tested_rows = [r for r in fresh_rows if r["tested"] == "True"]
    tested_rows.sort(key=lambda r: (r["instance_id"], r["condition"]))

    t_labels = [f"{r['instance_id'].split('__')[1].replace('pvlib-python-', 'pv-').replace('pydicom-', 'pd-')}/{r['condition']}" for r in tested_rows]
    f2p_pass = [int(r["required_regression_passed"]) for r in tested_rows]
    f2p_fail = [int(r["required_regression_failed"]) for r in tested_rows]

    y = np.arange(len(t_labels))
    h = 0.55

    ax.barh(y, f2p_pass, height=h, color=PALETTE["blue_main"], edgecolor="black", linewidth=0.9, label="F2P passed (target fix)", zorder=3)
    ax.barh(y, f2p_fail, height=h, left=f2p_pass, color=PALETTE["red_strong"], edgecolor="black", linewidth=0.9, label="F2P failed (bug remains)", zorder=3)

    for i, (p, f) in enumerate(zip(f2p_pass, f2p_fail)):
        if p > 0:
            ax.text(p + f + 0.06, i, "F2P: PASS, P2P: 2 FAIL (pvlib-1154/A)", va="center", fontsize=8, fontweight="bold", color=PALETTE["red_strong"])
        else:
            ax.text(f + 0.06, i, "F2P: FAIL", va="center", fontsize=8, color=PALETTE["neutral_dark"])

    ax.set_yticks(y)
    ax.set_yticklabels(t_labels, fontsize=8.5)
    ax.tick_params(axis="x", direction="out", length=4, width=1.2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Target Regression Tests (FAIL_TO_PASS)", fontsize=10.5, fontweight="semibold")
    ax.set_title("Test Outcomes for 10 Tested Fresh Patches (0 Resolved)", fontsize=11.5, pad=12, fontweight="bold")
    ax.set_xlim(0, 3.8)
    ax.set_xticks([0, 1, 2, 3])
    ax.invert_yaxis()
    ax.xaxis.grid(True, linestyle=":", alpha=0.5, color=PALETTE["neutral"])
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", fontsize=8.5, frameon=False)

    fig.tight_layout(pad=1.5)
    fig.savefig(FIG_DIR / "fig_test_outcomes.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig_test_outcomes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("✓ fig_test_outcomes")


def main():
    plot_fig1_tokens()
    plot_fig2_reference_coverage()
    plot_fig3_status()
    plot_fig4_matched_application()
    plot_fig5_error_cats()
    plot_fig6_outputs()
    plot_fig7_controls()
    plot_fig8_test_outcomes()
    print("\nAll 8 publication figures regenerated with figures4papers style in paper_v2/figures/.")


if __name__ == "__main__":
    main()
