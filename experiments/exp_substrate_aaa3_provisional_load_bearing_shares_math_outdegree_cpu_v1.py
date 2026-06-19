"""
exp_substrate_aaa3_provisional_load_bearing_shares_math_outdegree_cpu_v1.py -- CELL-AAA-3 (PROVISIONAL): do TOOLS have higher SHARES_MATH out-degree than MATERIALS? -- CPU/local (no heat, read-only).

ROUTING: Research ALTERNATIVES-DRILL Reservation C falsifier (notes/..._ALTERNATIVES_DRILL_VERDICT...). The substrate-load-bearing axis
  (Axis 2, tools-vs-materials, USER craftsman) has NO direct prior-art parallel -> "either genuinely substrate-novel OR category error".
  Pre-reg falsifier (CELL-AAA-3): TOOLS atoms predicted to have HIGHER SHARES_MATH out-degree than MATERIALS (tools are mechanism-class,
  generalize across capabilities). HARD-PASS ratio >= 1.4x; HARD-FAIL ratio < 1.1x (axis collapses to noise -> reconsider C per 7th rule).

  GATE: canonical SHARES_MATH edges = 0 (Testbed authoring pending). This is a PROVISIONAL EARLY READ on the SHARES_MATH AUTO-DISCOVERY
  CANDIDATE edges (exp_substrate_shares_math_auto_discovery..., bench_reports/shares_math_auto_discovery_candidates.json) -- structural
  signals (shared capability/USES) ORTHOGONAL to load-bearing, so the comparison is fair. KP P6 has shipped (Research's post-P6 deferral
  condition met); this de-risks Axis 2 before Testbed canonicalizes. NOT a substitute for the canonical run -- clearly labeled provisional.
  NO LLM; candidate-edge degree counting; numpy-free; no heat. READ-ONLY.

PRE-REGISTERED (Research CELL-AAA-3 bands, applied PROVISIONALLY): PROVISIONAL-SUPPORT ratio >= 1.4x (Reservation C supported -- axis real).
  PROVISIONAL-LEAN ratio in [1.1, 1.4) (axis NOT noise but below the bar; canonical edges may clear it). PROVISIONAL-REFUTE ratio < 1.1x
  (axis collapses to noise even provisionally -> strong reconsider-C signal). UNKNOWN if candidate file absent / too few tools present.
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
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
ANCHOR_NAME = "substrate_aaa3_provisional_load_bearing_shares_math_outdegree_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CAND = REPO / "data" / "substrate_index" / "bench_reports" / "shares_math_auto_discovery_candidates.json"
CURATED_TOOLS = set("""
fhrr_bind fhrr_unbind circular_convolution cleanup cosine_similarity superposition bundling discriminative_perceptron metric_space
spectral_gap theta_gamma_binding tracy_widom_distribution kappa_4_free mp_bulk_kl vsa_family unit_modulus vector_space gradient
inner_product role_filler_binding algebraic_binding context_binding cleanup_retrieval cosine_cleanup permutation_indexed_binding
resonator_network_decoder modern_hopfield_ramsauer hopfield_family superposition_aggregation unbinders ghrr_noncommutative_bind
theta_gamma_to_hrr qubit_to_fhrr_phasor
""".split())


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def degree_ratio(edges, tools):
    deg = Counter()
    for e in edges:
        a = _short(e["a"]); b = _short(e["b"]); deg[a] += 1; deg[b] += 1
    nodes = set(deg)
    td = [deg[n] for n in nodes if n in tools]
    md = [deg[n] for n in nodes if n not in tools]
    mt = statistics.mean(td) if td else 0.0
    mm = statistics.mean(md) if md else 0.0
    return mt, mm, (mt / mm if mm else 0.0), len(td), len(md)


def _selftest():
    # tools wired to more SHARES_MATH neighbors than materials
    edges = [{"a": "t1", "b": "t2"}, {"a": "t1", "b": "t3"}, {"a": "t2", "b": "t3"}, {"a": "t1", "b": "m1"}]
    mt, mm, ratio, nt, nm = degree_ratio(edges, {"t1", "t2", "t3"})   # tools form a triangle (deg 3,2,2=2.33) vs material m1 (deg 1)
    assert mt > mm and ratio > 1.4, (mt, mm, ratio)
    print("[selftest] PASS: substrate_aaa3_provisional_load_bearing_shares_math_outdegree_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not CAND.exists():
        return {"error": "no_candidate_file", "note": str(CAND)}
    d = json.load(open(CAND, encoding="utf-8"))
    edges = d.get("candidate_edges", [])
    if len(edges) < 10:
        return {"error": "too_few_candidate_edges", "n": len(edges)}
    mt, mm, ratio, n_tools, n_mats = degree_ratio(edges, CURATED_TOOLS)
    if n_tools < 5:
        return {"error": "too_few_tools_in_candidate_graph", "n_tools": n_tools}
    ratio = round(ratio, 3)
    print("  PROVISIONAL (auto-discovered SHARES_MATH candidate edges; canonical edges still 0):", flush=True)
    print("  %d candidate edges | TOOLS in graph=%d/33 | mean SHARES_MATH out-degree: TOOLS=%.2f MATERIALS=%.2f -> ratio=%.2fx" % (
        len(edges), n_tools, mt, mm, ratio), flush=True)
    return {"n_candidate_edges": len(edges), "tools_in_graph": n_tools, "materials_in_graph": n_mats,
            "tool_mean_outdeg": round(mt, 3), "material_mean_outdeg": round(mm, 3), "ratio": ratio}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("note", r.get("n", r.get("n_tools", "")))))
    ratio = r["ratio"]
    s = ("PROVISIONAL on %d auto-discovered SHARES_MATH candidate edges (canonical=0): TOOLS mean out-degree=%.2f (n=%d/33 in graph) vs "
         "MATERIALS=%.2f (n=%d) -> ratio=%.2fx. NOT canonical -- structural-candidate proxy; re-run on Testbed-authored SHARES_MATH for the definitive CELL-AAA-3.") % (
        r["n_candidate_edges"], r["tool_mean_outdeg"], r["tools_in_graph"], r["material_mean_outdeg"], r["materials_in_graph"], ratio)
    if ratio >= 1.4:
        return ("PROVISIONAL_SUPPORT", "PROVISIONAL-SUPPORT (Reservation C leaning REAL): TOOLS have >=1.4x the SHARES_MATH out-degree of MATERIALS even on candidate edges -- the load-bearing axis is mechanism-class (tools generalize across capabilities), NOT a category error. Confirm on canonical SHARES_MATH. " + s)
    if ratio >= 1.1:
        return ("PROVISIONAL_LEAN", "PROVISIONAL-LEAN (axis is NOT noise; below the 1.4x bar): ratio %.2fx in [1.1,1.4) -- TOOLS do share more math than MATERIALS (well above the 1.1x HARD-FAIL floor), so Axis 2 is NOT collapsing to noise, but does not clear 1.4x on candidate edges. Canonical (richer) SHARES_MATH authoring may push it over. Reservation C leans supported, pending canonical run. " % ratio + s)
    return ("PROVISIONAL_REFUTE", "PROVISIONAL-REFUTE (reconsider C): ratio %.2fx < 1.1x even provisionally -- the load-bearing axis may collapse to noise; flag for reconsideration per 7th USER-LOCKED rule (pending canonical SHARES_MATH confirmation). " % ratio + s)


print("[config] anchor=%s mode=%s curated_tools=%d" % (ANCHOR_NAME, RUN_MODE, len(CURATED_TOOLS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
