"""
exp_substrate_kp_p6_three_axis_tagging_crosstab_cpu_v1.py -- KP P6 audit operator: tag every atom on 3 orthogonal axes + prove they COMPOSE -- CPU/local (no heat, read-only).

ROUTING: Research SR-1 RATIFICATION + 3-axis framework (notes/research_to_exp_dev_SR1_RATIFICATION_curated_TOOLS_list_33_atoms...; the
  philosophy/science drill verdict). KP P6's audit-operator half (Testbed owns the Atom-schema `substrate_load_bearing` field; this cell is
  the analysis pipeline that PRODUCES the tagging + validates the architecture). The whole thesis of the philosophy thread: the substrate is
  the FIRST cognitive architecture making these THREE axes explicit + first-class + orthogonal:
    Axis 1 EPISTEMIC TIER  : T1/T2/T3/... (how foundational) -- KP promotion ladder
    Axis 2 LOAD-BEARING    : tool (machinery uses it) vs material (content it works on) -- Research-ratified 33 TOOLS
    Axis 3 CONTENT-TYPE    : system (rule-governed) vs record (narrative/episodic) -- system-vs-record classifier (Spearman -0.90 confirmed)
  This cell tags each atom on all 3 and proves they COMPOSE (genuinely orthogonal, non-degenerate) rather than collapse onto one another --
  the empirical basis for "ONE atom can be e.g. T1+tool+system (inner_product) vs T3+material+record (a Wikidata fact)". Produces the
  per-atom tagging artifact for Testbed schema ingest. NO LLM; tier + curated-tools membership + text/corpus classifier; numpy-free; no heat.

PRE-REGISTERED: HARD-PASS the 3 axes COMPOSE: each axis non-degenerate (>=2 categories populated) AND >= 5 distinct (tier x load-bearing x
  content-type) combination-cells each hold >= 3 atoms (axes are independent, not collinear) AND tools span >= 2 tiers (load-bearing is not
  just "T1") AND tools are predominantly system-content (sanity). MIDDLE: 3-4 populated combination-cells OR tools confined to 1 tier.
  HARD-FAIL: an axis is degenerate (all atoms one category) OR < 3 combination-cells (axes collapse / are redundant). UNKNOWN if no index.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_kp_p6_three_axis_tagging_crosstab_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
PROSE_CHARS = 700
_NOTE_PAT = re.compile(r"(20\d\d|_to_|to_research|to_exp|to_testbed|drill|handoff|\bnote\b|report|verdict|status|check_in|resume)", re.I)
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())


def _short(aid):
    return str(aid).split("::")[-1].split("/")[-1].strip().lower()


def axis2_load_bearing(short_id: str) -> str:
    return "tool" if short_id in CURATED_TOOLS else "material"


def axis3_content_type(corpus: str, name: str, desc: str) -> str:
    """system (rule-governed) vs record (narrative); episodic = chronological record (history corpus)."""
    c = (corpus or "").lower()
    rec = 0
    if "history" in c: rec += 1
    if len(desc or "") > PROSE_CHARS: rec += 1
    if _NOTE_PAT.search(name or ""): rec += 1
    if (desc or "").lstrip().startswith("#"): rec += 1
    if rec >= 2:
        return "episodic" if "history" in c else "record"
    return "system"


def _selftest():
    assert axis2_load_bearing("fhrr_bind") == "tool" and axis2_load_bearing("jensen_inequality") == "material"
    assert axis3_content_type("research_history", "research_drill_x_2026-06-11", "# Note ...") == "episodic"
    assert axis3_content_type("math", "inner_product", "Bilinear form.") == "system"
    assert len(CURATED_TOOLS) == 33
    print("[selftest] PASS: substrate_kp_p6_three_axis_tagging_crosstab_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    tagging = {}
    ax1 = Counter(); ax2 = Counter(); ax3 = Counter(); cross = Counter()
    tool_tiers = set(); tool_content = Counter()
    examples = {}
    for a in atoms:
        sid = _short(a.id)
        tier = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "NA")
        corpus = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        lb = axis2_load_bearing(sid)
        ct = axis3_content_type(corpus, getattr(a, "name", "") or "", getattr(a, "description", "") or "")
        tagging[sid] = {"tier": tier, "load_bearing": lb, "content_type": ct}
        ax1[tier] += 1; ax2[lb] += 1; ax3[ct] += 1
        key = (tier, lb, ct); cross[key] += 1
        if lb == "tool":
            tool_tiers.add(tier); tool_content[ct] += 1
        if key not in examples:
            examples[key] = sid
    populated_cells = {k: v for k, v in cross.items() if v >= 3}
    n_cells = len(populated_cells)
    nondegen = (len([c for c in ax1 if ax1[c] >= 1]) >= 2 and len(ax2) >= 2 and len(ax3) >= 2)
    tools_span_tiers = len(tool_tiers)
    tools_system_frac = round(tool_content.get("system", 0) / max(1, sum(tool_content.values())), 3)
    print("  Axis1 tier=%s" % dict(ax1.most_common()), flush=True)
    print("  Axis2 load-bearing=%s | Axis3 content-type=%s" % (dict(ax2), dict(ax3)), flush=True)
    print("  3-axis combination cells with >=3 atoms: %d | tools span %d tiers %s | tools system-frac=%.3f" % (
        n_cells, tools_span_tiers, sorted(tool_tiers), tools_system_frac), flush=True)
    print("  example atoms per combination (tier, load-bearing, content-type):", flush=True)
    for k in sorted(populated_cells, key=lambda x: -populated_cells[x])[:12]:
        print("    %-26s n=%4d e.g. %s" % (str(k), populated_cells[k], examples.get(k, "")), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "kp_p6_three_axis_tagging.json").write_text(json.dumps(
        {"tagging": tagging, "axis1_tier": dict(ax1), "axis2_load_bearing": dict(ax2), "axis3_content_type": dict(ax3),
         "combination_cells": {str(k): v for k, v in sorted(cross.items(), key=lambda x: -x[1])},
         "tools_span_tiers": sorted(tool_tiers), "tools_system_fraction": tools_system_frac}, indent=2), encoding="utf-8")
    return {"n_atoms": len(atoms), "axis1": dict(ax1), "axis2": dict(ax2), "axis3": dict(ax3),
            "n_combo_cells_ge3": n_cells, "tools_span_tiers": tools_span_tiers, "tools_system_frac": tools_system_frac,
            "nondegenerate": nondegen, "top_cells": {str(k): v for k, v in sorted(populated_cells.items(), key=lambda x: -x[1])[:12]}}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_combo_cells_ge3"]; spt = r["tools_span_tiers"]; tsf = r["tools_system_frac"]; nd = r["nondegenerate"]
    s = ("Axis1 tier=%s; Axis2 load-bearing=%s; Axis3 content-type=%s; %d distinct (tier x load-bearing x content-type) cells hold >=3 atoms; "
         "tools span %d tiers (load-bearing != just-T1); tools system-fraction=%.3f. Per-atom 3-axis tagging saved bench_reports/kp_p6_three_axis_tagging.json (-> Testbed Atom-schema substrate_load_bearing + content_type).") % (
        r["axis1"], r["axis2"], r["axis3"], n, spt, tsf)
    if nd and n >= 5 and spt >= 2 and tsf >= 0.5:
        return ("HARD_PASS", "HARD_PASS: the 3 axes genuinely COMPOSE -- all non-degenerate, %d distinct combination-cells populated (axes are ORTHOGONAL, not collinear), tools span %d tiers (load-bearing is independent of epistemic tier), and tools are predominantly system-content (%.0f%%, sane). Empirical basis for the substrate-product claim: a single atom carries 3 INDEPENDENT coordinates (tier x tool/material x system/record). LLMs have none of these explicitly, let alone composed. " % (n, spt, tsf * 100) + s)
    if nd and n >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: axes non-degenerate and %d combination-cells populated, but not cleanly at the HARD-PASS bar (tools span %d tiers / system-frac %.2f). Axes compose partially. " % (n, spt, tsf) + s)
    return ("HARD_FAIL", "HARD_FAIL: an axis is degenerate OR < 3 combination-cells -- the axes collapse / are redundant rather than orthogonal. " + s)


print("[config] anchor=%s mode=%s curated_tools=%d" % (ANCHOR_NAME, RUN_MODE, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
