"""
exp_substrate_sr3_foundational_vs_frequency_curated_tools_cpu_v1.py -- USER-craftsman test: foundational(TOOL) != frequency(citation) -- CPU/local (no heat, read-only).

ROUTING: Research SR-1 RATIFICATION (notes/research_to_exp_dev_SR1_RATIFICATION_curated_TOOLS_list_33_atoms...). Definitive run of drill
  cell #3 (foundational != frequency) using the Research-RATIFIED 33-atom curated TOOLS list (replaces my auto-name-match LOWER BOUND, which
  undercounted because the code implements tools under generic identifiers like np.dot). Verifies the USER craftsman intuition verbatim:
  "a book might be cited 1M times but might just be the FIRST book on topic; addition is extraordinarily foundational; different worlds."

  TEST: do the substrate's load-bearing TOOLS (Axis 2) coincide with the most-CITED atoms (DEPENDS_ON in-degree)? If foundational(tool) ==
  frequency, tools would dominate the top-cited. The USER claim is they DECORRELATE: machinery primitives are often LOW-citation (you do not
  re-derive fhrr_unbind; it just IS the machinery), while many high-citation atoms are MATERIALS the substrate reasons ABOUT, not WITH.
  NO LLM; relation in-degree over the ratified list; numpy-free; no heat. READ-ONLY.

PRE-REGISTERED: HARD-PASS (foundational != frequency CONFIRMED) iff median(TOOL in-degree) < 0.5 * median(top-K-cited in-degree) AND
  >= 30% of TOOLS are NOT in the top-K cited (citation does not track tool-ness). MIDDLE iff one of the two holds. HARD-FAIL iff tools ARE
  essentially the most-cited (median ratio >= 0.8 AND < 15% tools outside top-K) -> foundational == frequency, USER intuition refuted here.
  UNKNOWN if no index / tools absent. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, statistics
from collections import Counter
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_sr3_foundational_vs_frequency_curated_tools_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
TOP_K = 100
# Research-RATIFIED 33-atom curated TOOLS list (A 18 + B 15; generic-name FPs removed). The substrate's "workshop floor".
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())


def _short(aid):
    return str(aid).split("::")[-1].split("/")[-1].strip().lower()


def _selftest():
    # foundational != frequency: tools mostly low-cited, top-cited full of non-tools
    indeg = {"tool_a": 1, "tool_b": 0, "tool_c": 300, "mat_x": 50, "mat_y": 40, "mat_z": 30}
    tools = {"tool_a", "tool_b", "tool_c"}
    topk = [s for s, _ in Counter(indeg).most_common(3)]              # tool_c, mat_x, mat_y
    med_tool = statistics.median([indeg[t] for t in tools])          # median(1,0,300)=1
    med_top = statistics.median([indeg[s] for s in topk])            # median(300,50,40)=50
    out = [t for t in tools if t not in topk]                        # tool_a, tool_b
    assert med_tool < 0.5 * med_top and len(out) / len(tools) >= 0.3
    assert 33 == len(CURATED_TOOLS), len(CURATED_TOOLS)
    print("[selftest] PASS: substrate_sr3_foundational_vs_frequency_curated_tools_cpu_v1 (33 tools; foundational!=frequency logic)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    present = {_short(a.id) for a in PartitionedStore(root).all_atoms()}
    indeg = Counter()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() == "DEPENDS_ON":
                indeg[_short(r.get("tgt_id", ""))] += 1
    tools = sorted(t for t in CURATED_TOOLS if t in present)
    missing = sorted(CURATED_TOOLS - present)
    if len(tools) < 10:
        return {"error": "too_few_curated_tools_present", "present": len(tools), "missing": missing}
    topk = [s for s, _ in indeg.most_common(TOP_K)]
    topk_set = set(topk)
    tool_deg = {t: indeg[t] for t in tools}
    med_tool = float(statistics.median(list(tool_deg.values())))
    med_top = float(statistics.median([indeg[s] for s in topk])) if topk else 0.0
    tools_in_top = [t for t in tools if t in topk_set]
    tools_out_top = [t for t in tools if t not in topk_set]
    frac_out = round(len(tools_out_top) / len(tools), 4)
    ratio = round(med_tool / (med_top + 1e-9), 4)
    nontool_top = [s for s in topk if s not in CURATED_TOOLS][:15]
    print("  curated tools present=%d/33 (missing=%s)" % (len(tools), missing), flush=True)
    print("  median TOOL in-degree=%.1f vs median top-%d in-degree=%.1f (ratio=%.3f)" % (med_tool, TOP_K, med_top, ratio), flush=True)
    print("  TOOLS in top-%d cited=%d/%d | TOOLS OUTSIDE top-%d (load-bearing but low-citation)=%d (%.0f%%): %s" % (
        TOP_K, len(tools_in_top), len(tools), TOP_K, len(tools_out_top), frac_out * 100, tools_out_top[:12]), flush=True)
    print("  highly-cited NON-tools (frequency != foundational): %s" % nontool_top, flush=True)
    return {"n_tools_present": len(tools), "missing": missing, "median_tool_indeg": med_tool, "median_topk_indeg": med_top,
            "median_ratio": ratio, "tools_in_topk": len(tools_in_top), "tools_out_topk": len(tools_out_top),
            "frac_tools_outside_topk": frac_out, "low_citation_tools": tools_out_top, "highly_cited_nontools": nontool_top,
            "tool_indegrees": dict(sorted(tool_deg.items(), key=lambda kv: -kv[1]))}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("missing", "")))
    ratio = r["median_ratio"]; frac_out = r["frac_tools_outside_topk"]
    s = ("ratified TOOLS present=%d/33; median TOOL citation=%.1f vs median top-%d citation=%.1f (ratio=%.3f); %d/%d tools (%.0f%%) are "
         "OUTSIDE the top-%d cited (load-bearing but rarely cited: %s); highly-cited NON-tools (materials): %s.") % (
        r["n_tools_present"], r["median_tool_indeg"], TOP_K, r["median_topk_indeg"], ratio, r["tools_out_topk"],
        r["n_tools_present"], frac_out * 100, TOP_K, r["low_citation_tools"][:8], r["highly_cited_nontools"][:8])
    hp = (ratio < 0.5 and frac_out >= 0.30)
    fail = (ratio >= 0.8 and frac_out < 0.15)
    if hp:
        return ("HARD_PASS", "HARD_PASS (USER craftsman intuition CONFIRMED -- foundational != frequency): the substrate's load-bearing TOOLS are CITATION-DECORRELATED -- median tool citation %.1f is far below median top-%d citation %.1f (ratio %.3f<0.5) AND %.0f%% of tools sit OUTSIDE the most-cited (you do not re-derive the machinery; it just IS the machinery), while the most-cited are dominated by MATERIALS the substrate reasons ABOUT. Axis 2 (load-bearing) is genuinely orthogonal to citation-frequency -- 'cited a lot' != 'foundational tool'. " % (r["median_tool_indeg"], TOP_K, r["median_topk_indeg"], ratio, frac_out * 100) + s)
    if fail:
        return ("HARD_FAIL", "HARD_FAIL: tools ARE essentially the most-cited (ratio %.3f, only %.0f%% outside top-K) -- foundational == frequency here; USER intuition not borne out on this corpus. " % (ratio, frac_out * 100) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: partial decorrelation (median ratio %.3f, %.0f%% tools outside top-K) -- tool-ness and citation are partly but not cleanly decoupled. " % (ratio, frac_out * 100) + s)


print("[config] anchor=%s mode=%s top_k=%d curated_tools=%d" % (ANCHOR_NAME, RUN_MODE, TOP_K, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
