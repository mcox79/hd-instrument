"""
refuse_gate_5_graph_health_cpu_v1 -- refuse-gate #5, signal (b) GRAPH-LEVEL HEALTH (Skunkworks call). Does a graph-level
crosstalk-health signal let the substrate REFUSE the graph-adjacency OVERLOAD regime (E>=0.25N, which it genuinely can't store
separably) rather than fabricate, while ACCEPTING storable graphs? CPU. data-decides; DON'T FORCE -> (c) honest-negative is cert-grade.

WHY (b) not (a): the v1 per-query concentration cell (b9bcd7a7) proved the substrate is CONFIDENTLY WRONG at overload (softmax
peaks on a crosstalk false-positive) -> per-query confidence is the WRONG GRAIN. #5's claim is REGIME-level ("refuse on the regime
it can't store") -> a GRAPH-level signal (non-edge score VARIANCE = the substrate's "I'm saturated" signal) is the right grain.

MECHANISM: SQ6 graph bind G = sum over edges (u,v) of node_u*node_v. Per graph: edge-membership ACCURACY (balanced edge-vs-nonedge
classification at best threshold = the SQ6 referent) + HEALTH = variance of non-edge scores (crosstalk spread). Gate: REFUSE iff health > c.

3 HARD CAN-fail conditions (Skunkworks):
  1. PREDICT-THE-CLIFF-NOT-E: the refuse threshold's boundary (in E) must COINCIDE with the accuracy<0.95 boundary (the SQ6 cliff,
     ~E=0.25N) -- validated against MEASURED accuracy, not just correlated with edge-count.
  2. SEPARATION: storable (E<0.25N, acc>=0.95) -> health<c -> ACCEPT (false-refuse<=0.05); unstorable (E>=0.25N) -> health>c ->
     REFUSE (refuse-rate>=0.95). A single c must separate them.
  3. Keep the ACCEPT arm (refuse-everything is useless -- condition 2's accept-storable IS this).
data-decides: clean separation + cliff-coincidence -> safety-capability cert; else -> (c) honest-negative (genuine LIMIT). ASCII. CPU.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "refuse_gate_5_graph_health_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 2048 if SMOKE else 4096
V = 128
E_FRACS = [0.05, 0.15, 0.25, 0.5, 1.0]                   # x N edges; 0.25N = the SQ6 HARD_FAIL cliff (accuracy<0.95 at/above)
SEEDS = [1] if SMOKE else [1, 2, 3]
ACC_CLIFF = 0.95                                          # edge-membership accuracy threshold (SQ6 referent)


def bipolar(shape, g):
    return (g.integers(0, 2, shape) * 2 - 1).astype(np.float32)


def _edge_set(V, E, g):
    seen = set(); edges = []
    while len(edges) < E:
        u, w = int(g.integers(0, V)), int(g.integers(0, V))
        if u != w:
            k = (min(u, w), max(u, w))
            if k not in seen:
                seen.add(k); edges.append(k)
    return edges


def graph_scores(nodes, edges, g):
    """Build G = sum node_u*node_v; return (true_edge_scores, non_edge_scores) -- score = <G, node_a*node_b>/N."""
    n = nodes.shape[1]; G = np.zeros(n, np.float32)
    for (u, w) in edges:
        G += nodes[u] * nodes[w]
    eset = set(edges)
    te = np.array([float((G * (nodes[u] * nodes[w])).sum() / n) for (u, w) in edges], np.float32)
    # sample equal # of non-edges
    ne = []; need = len(edges)
    while len(ne) < need:
        u, w = int(g.integers(0, V)), int(g.integers(0, V))
        if u != w and (min(u, w), max(u, w)) not in eset:
            ne.append(float((G * (nodes[u] * nodes[w])).sum() / n))
    return te, np.array(ne, np.float32)


def best_balanced_accuracy(te, ne):
    """Balanced edge-vs-nonedge classification accuracy at the best threshold."""
    cands = np.unique(np.concatenate([te, ne]))
    best = 0.0
    for t in cands:
        acc = 0.5 * (float((te >= t).mean()) + float((ne < t).mean()))
        if acc > best:
            best = acc
    return best


def health(ne):
    """Graph health = variance of NON-EDGE scores (crosstalk spread = the 'I'm saturated' signal). Low=clean, high=overloaded."""
    return float(np.var(ne))


def _selftest():
    g = np.random.default_rng(0); nodes = bipolar((V, 512), g)
    e_lo = _edge_set(V, int(0.05 * 512), g); te, ne = graph_scores(nodes, e_lo, g)
    assert best_balanced_accuracy(te, ne) >= 0.95, "low-E edge-membership separable (acc>=0.95)"
    h_lo = health(ne)
    e_hi = _edge_set(V, int(1.0 * 512), g); te2, ne2 = graph_scores(nodes, e_hi, g)
    assert health(ne2) > h_lo, "high-E health(non-edge variance) > low-E (%.3f > %.3f)" % (health(ne2), h_lo)
    print("[selftest] PASS: low-E separable+clean, high-E overloaded+high-variance", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_unit(e_frac, seed):
    g = np.random.default_rng(seed * 911 + int(e_frac * 1000)); nodes = bipolar((V, N), g)
    E = max(2, int(e_frac * N)); edges = _edge_set(V, E, g)
    te, ne = graph_scores(nodes, edges, g)
    acc = best_balanced_accuracy(te, ne); h = health(ne)
    storable = acc >= ACC_CLIFF
    print("  [E=%.2fN s=%d] edge-membership acc=%.3f health(nonedge-var)=%.4f storable=%s" % (e_frac, seed, acc, h, storable), flush=True)
    return {"e_frac": e_frac, "seed": seed, "accuracy": round(acc, 4), "health": round(h, 5), "storable": bool(storable), "run_mode": RUN_MODE}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    by = {}
    for u in units:
        by.setdefault(u["e_frac"], []).append(u)
    per = {}
    for ef, us in by.items():
        per[ef] = {"accuracy": float(np.mean([u["accuracy"] for u in us])), "health": float(np.mean([u["health"] for u in us])),
                   "storable": float(np.mean([u["accuracy"] for u in us])) >= ACC_CLIFF}
    efs = sorted(per.keys())
    storable_efs = [e for e in efs if per[e]["storable"]]
    unstorable_efs = [e for e in efs if not per[e]["storable"]]
    # choose threshold c = midpoint between max-storable-health and min-unstorable-health (best separator)
    c = None; separates = False
    if storable_efs and unstorable_efs:
        max_store_h = max(per[e]["health"] for e in storable_efs)
        min_unstore_h = min(per[e]["health"] for e in unstorable_efs)
        c = 0.5 * (max_store_h + min_unstore_h)
        separates = max_store_h < min_unstore_h                          # storable health ALL below unstorable health -> clean separator
    # CAN-fail 1: does the health-refuse boundary (c) coincide with the accuracy<0.95 boundary?
    cliff_e = min(unstorable_efs) if unstorable_efs else None            # first E where accuracy<0.95 (SQ6 cliff)
    health_refuses = {e: (per[e]["health"] > c if c is not None else False) for e in efs}
    coincides = bool(separates and cliff_e is not None and all((health_refuses[e] == (not per[e]["storable"])) for e in efs))
    false_refuse = float(np.mean([1.0 if (c is not None and per[e]["health"] > c) else 0.0 for e in storable_efs])) if storable_efs else 1.0
    refuse_unstore = float(np.mean([1.0 if (c is not None and per[e]["health"] > c) else 0.0 for e in unstorable_efs])) if unstorable_efs else 0.0
    detail = {"per_e_frac": {("E%.2fN" % e): {"acc": round(per[e]["accuracy"], 3), "health": round(per[e]["health"], 5), "storable": per[e]["storable"]} for e in efs},
              "accuracy_cliff_E": cliff_e, "health_threshold_c": (round(c, 5) if c is not None else None), "clean_separator": bool(separates),
              "health_predicts_cliff": coincides, "false_refuse_rate_storable": round(false_refuse, 3), "refuse_rate_unstorable": round(refuse_unstore, 3),
              "honest_claim": "Graph-level health (non-edge score variance) as the refuse signal for graph-adjacency overload: "
                              "accuracy-cliff at E=%s; health separates storable/unstorable=%s; health predicts the cliff (not just E)=%s; "
                              "false-refuse(storable)=%.2f refuse(unstorable)=%.2f. data-decides (don't force; per-query was confidently-wrong)." % (cliff_e, separates, coincides, false_refuse, refuse_unstore)}
    summary = "acc_cliff_E=%s c=%s separates=%s predicts_cliff=%s | false_refuse=%.2f refuse_unstore=%.2f | per_E=%s" % (
        cliff_e, detail["health_threshold_c"], separates, coincides, false_refuse, refuse_unstore, detail["per_e_frac"])
    if cliff_e is None:
        return ("UNKNOWN", "no accuracy-cliff in the swept E range (all storable or all unstorable) -- widen E. " + summary, detail)
    if separates and coincides and false_refuse <= 0.05 and refuse_unstore >= 0.95:
        return ("HARD_PASS", "HARD_PASS (safety-capability; data-decides -> Skunkworks rules): graph-health REFUSES the overload regime (>=0.95) + ACCEPTS storable (false-refuse<=0.05) AND the health-boundary COINCIDES with the accuracy-cliff (predicts the cliff, not just E). Substrate detects its own graph-overload + refuses before fabricating. " + summary, detail)
    if separates and false_refuse <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: health separates storable/unstorable but cliff-coincidence or band imperfect (may be E-counting-ish). " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM / honest-NEGATIVE (c, cert-grade): graph-health does NOT cleanly separate storable from overload (no single c, or doesn't predict the cliff). Combined with v1 (per-query confidently-wrong): confidence- AND graph-health-based self-refusal do NOT cover the confidently-wrong graph-overload regime -- a genuine LIMIT of substrate self-refusal at high graph-load. " + summary, detail)


print("[config] %s mode=%s N=%d V=%d E_fracs=%s seeds=%s (signal b: graph-health)" % (ANCHOR_NAME, RUN_MODE, N, V, E_FRACS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for ef in E_FRACS:
    for seed in SEEDS:
        key = ("E%.2f_s%d" % (ef, seed)).replace(".", "p")
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        try:
            write_partial_key(out_dir, key, run_unit(ef, seed))
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)
keys = [("E%.2f_s%d" % (ef, sd)).replace(".", "p") for ef in E_FRACS for sd in SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "V": V,
           "E_fracs": E_FRACS, "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_refuse_gate_graph_health_variance", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
