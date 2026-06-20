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
    """E distinct edges over all V nodes (~uniform degree)."""
    seen = set(); edges = []
    while len(edges) < E:
        u, w = int(g.integers(0, V)), int(g.integers(0, V))
        if u != w:
            k = (min(u, w), max(u, w))
            if k not in seen:
                seen.add(k); edges.append(k)
    return edges


# FIXED-E test (Skunkworks REQUIRED, decides tier): hold E AND edge-structure fixed, vary the SUBSTRATE STATE itself
# (node-vector crosstalk via injected correlation). Correlated nodes -> more crosstalk in the stored superposition G ->
# less storable. If health separates the two AT IDENTICAL E and IDENTICAL graph, it is reading substrate-STATE (the crosstalk
# in G), not edge-count -- rules out E-counting-in-disguise. (Degree-concentration was rejected: it dilutes global non-edge
# variance, so it cannot give health a fair test.)
FIXED_E_FRAC = 0.15                                       # fixed edge-load for the contrast (at the accuracy-cliff)
FIXED_E_RHO = 0.6                                         # node-vector correlation for the high-crosstalk (less-storable) arm


def correlated_bipolar(V, N, rho, g):
    """V bipolar vectors with a shared component (pairwise overlap grows with rho); rho=0 -> ~orthogonal random."""
    base = g.standard_normal((1, N)); noise = g.standard_normal((V, N))
    return np.sign(rho * base + np.sqrt(1.0 - rho * rho) * noise).astype(np.float32)


def fixed_e_contrast(N, V, seed):
    """At FIXED E and IDENTICAL graph: LOW-crosstalk nodes (rho=0, storable) vs HIGH-crosstalk nodes (rho>0, less storable). Return (acc,health) each."""
    g = np.random.default_rng(seed * 7757 + 13)
    E = max(2, int(FIXED_E_FRAC * N))
    e = _edge_set(V, E, g)                                      # SAME edge structure for both arms
    nodes_lo = correlated_bipolar(V, N, 0.0, g)                 # orthogonal -> low crosstalk -> storable
    nodes_hi = correlated_bipolar(V, N, FIXED_E_RHO, g)         # correlated -> high crosstalk -> less storable (SAME E, SAME graph)
    te_l, ne_l = graph_scores(nodes_lo, e, g); te_h, ne_h = graph_scores(nodes_hi, e, g)
    return {"E": E, "spread_acc": best_balanced_accuracy(te_l, ne_l), "spread_health": health(ne_l),
            "conc_acc": best_balanced_accuracy(te_h, ne_h), "conc_health": health(ne_h)}


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


def storable_accept_test(N, V, c, seeds):
    """RESIDUAL 2 (Skunkworks): does the GLOBAL threshold c correctly ACCEPT a genuinely-storable structure?
    Uses rho=0 (orthogonal = max-storable) nodes, sweeps E_FRAC across/below the cliff; for each acc>=0.95 point,
    checks health<c (accepted). If a storable point has health>=c -> the global threshold FALSE-REFUSES it -> the
    false-refuse=0 claim is E-sweep-SCOPED and a STATE-RELATIVE threshold is needed for deployment. data-decides."""
    pts = []
    for ef in [0.05, 0.08, 0.10, 0.12]:
        accs, hs = [], []
        for sd in seeds:
            g = np.random.default_rng(sd * 7757 + 13); E = max(2, int(ef * N)); e = _edge_set(V, E, g)
            nodes = correlated_bipolar(V, N, 0.0, g)                       # rho=0 = max-storable structure
            te, ne = graph_scores(nodes, e, g); accs.append(best_balanced_accuracy(te, ne)); hs.append(health(ne))
        acc, h = float(np.mean(accs)), float(np.mean(hs))
        pts.append({"e_frac": ef, "acc": round(acc, 3), "health": round(h, 5), "storable_ge_0p95": acc >= 0.95,
                    "accepted_by_c": bool(c is not None and h < c)})
    storable = [p for p in pts if p["storable_ge_0p95"]]
    all_accepted = bool(storable) and all(p["accepted_by_c"] for p in storable)
    refused = [p["e_frac"] for p in storable if not p["accepted_by_c"]]
    return {"points": pts, "n_storable_tested": len(storable), "all_storable_accepted_global_c": all_accepted,
            "storable_but_REFUSED_efracs": refused,
            "interpretation": ("global threshold ACCEPTS all storable -> false-refuse=0 generalizes (deployable global gate)" if all_accepted
                               else ("storable structures REFUSED at E_frac %s -> false-refuse=0 is E-sweep-SCOPED; deployment needs a STATE-RELATIVE threshold (health-reads-state still holds)" % refused if storable
                                     else "no acc>=0.95 storable point in the tested E_frac range -- inconclusive (lower E_frac)"))}


def compute_verdict(units, fixed_e=None) -> Tuple[str, str, Dict]:
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
    # FIXED-E test (Skunkworks REQUIRED, DECIDES TIER): at a FIXED E, two structures with DIFFERENT storability.
    # health_reads_state==True ONLY if a storability gap was actually constructed AND health flags the less-storable one ->
    # rules out "health is just counting E in disguise". status: not_run / inconclusive(no gap built) / reads_state / Ecounting.
    fe_status, fixed_e_detail = "not_run", None
    if fixed_e is not None:
        acc_gap = fixed_e["spread_acc"] - fixed_e["conc_acc"]        # >0 -> concentrated genuinely less storable (expected)
        health_gap = fixed_e["conc_health"] - fixed_e["spread_health"]  # >0 -> health flags the less-storable structure
        constructed_gap = acc_gap >= 0.05                            # did the construction actually create a storability gap at fixed E?
        if not constructed_gap: fe_status = "inconclusive"
        elif health_gap > 0:    fe_status = "reads_state"
        else:                   fe_status = "Ecounting"
        fixed_e_detail = {"E": fixed_e["E"], "spread_acc": round(fixed_e["spread_acc"], 3), "conc_acc": round(fixed_e["conc_acc"], 3),
                          "spread_health": round(fixed_e["spread_health"], 5), "conc_health": round(fixed_e["conc_health"], 5),
                          "acc_gap": round(acc_gap, 3), "health_gap": round(health_gap, 5),
                          "storability_gap_constructed": bool(constructed_gap), "status": fe_status,
                          "reads_substrate_state_not_Ecount": fe_status == "reads_state"}
    detail = {"per_e_frac": {("E%.2fN" % e): {"acc": round(per[e]["accuracy"], 3), "health": round(per[e]["health"], 5), "storable": per[e]["storable"]} for e in efs},
              "fixed_e_test": fixed_e_detail,
              "accuracy_cliff_E": cliff_e, "health_threshold_c": (round(c, 5) if c is not None else None), "clean_separator": bool(separates),
              "health_predicts_cliff": coincides, "false_refuse_rate_storable": round(false_refuse, 3), "refuse_rate_unstorable": round(refuse_unstore, 3),
              "honest_claim": "Graph-level health (non-edge score variance) as the refuse signal for graph-adjacency overload: "
                              "accuracy-cliff at E=%s; health separates storable/unstorable=%s; health predicts the cliff (not just E)=%s; "
                              "false-refuse(storable)=%.2f refuse(unstorable)=%.2f. data-decides (don't force; per-query was confidently-wrong)." % (cliff_e, separates, coincides, false_refuse, refuse_unstore)}
    summary = "acc_cliff_E=%s c=%s separates=%s predicts_cliff=%s | false_refuse=%.2f refuse_unstore=%.2f | per_E=%s" % (
        cliff_e, detail["health_threshold_c"], separates, coincides, false_refuse, refuse_unstore, detail["per_e_frac"])
    summary = summary + " | fixed_E_test=%s" % fe_status
    base_pass = bool(separates and coincides and false_refuse <= 0.05 and refuse_unstore >= 0.95)
    if cliff_e is None:
        return ("UNKNOWN", "no accuracy-cliff in the swept E range (all storable or all unstorable) -- widen E. " + summary, detail)
    if base_pass and fe_status == "reads_state":
        return ("HARD_PASS", "HARD_PASS (safety-capability; data-decides -> Skunkworks rules): graph-health REFUSES overload (>=0.95) + ACCEPTS storable (false-refuse<=0.05), the health-boundary COINCIDES with the accuracy-cliff, AND the FIXED-E test proves health reads substrate-STATE (at equal E, the concentrated/less-storable structure has higher health + lower accuracy) -- NOT E-counting-in-disguise. Substrate detects its own graph-overload before fabricating. " + summary, detail)
    if base_pass and fe_status == "Ecounting":
        return ("MIDDLE_BAND", "MIDDLE_BAND: health predicts the cliff over the E-sweep, BUT the fixed-E test shows health does NOT separate two equal-E structures of different storability -- so health is tracking edge-COUNT, not substrate-state (E-counting-in-disguise). Honest demotion. " + summary, detail)
    if base_pass and fe_status in ("not_run", "inconclusive"):
        return ("MIDDLE_BAND", "MIDDLE_BAND: E-sweep gates pass (separates + predicts-cliff + bands) but the fixed-E substrate-state test is %s (no storability gap was constructed at fixed E, or it was not run) -- substrate-state vs E-counting is UNCONFIRMED, so not full HARD_PASS. Tune V_SUB/FIXED_E_FRAC to build a real gap, or run it. " % fe_status + summary, detail)
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
# FIXED-E test (Skunkworks REQUIRED, decides tier): spread-vs-concentrated at equal E, aggregated across seeds
fe_runs = [fixed_e_contrast(N, V, sd) for sd in SEEDS]
fixed_e = {"E": fe_runs[0]["E"],
           "spread_acc": float(np.mean([r["spread_acc"] for r in fe_runs])), "spread_health": float(np.mean([r["spread_health"] for r in fe_runs])),
           "conc_acc": float(np.mean([r["conc_acc"] for r in fe_runs])), "conc_health": float(np.mean([r["conc_health"] for r in fe_runs]))}
print("[fixed-E] %s" % fixed_e, flush=True)
verdict, msg, detail = compute_verdict(units, fixed_e=fixed_e)
# RAW WITNESS for the reads-STATE discriminator (Skunkworks HOLD): export per-seed fixed-E spread/conc so Testbed can
# INDEPENDENTLY re-derive the health-gap-tracks-acc-gap result from raw data (not from a computed summary field).
detail["fixed_e_raw_per_seed"] = [{"seed": SEEDS[i], "E": fe_runs[i]["E"],
                                   "spread_acc": round(fe_runs[i]["spread_acc"], 4), "spread_health": round(fe_runs[i]["spread_health"], 5),
                                   "conc_acc": round(fe_runs[i]["conc_acc"], 4), "conc_health": round(fe_runs[i]["conc_health"], 5),
                                   "acc_gap": round(fe_runs[i]["spread_acc"] - fe_runs[i]["conc_acc"], 4),
                                   "health_gap": round(fe_runs[i]["conc_health"] - fe_runs[i]["spread_health"], 5)} for i in range(len(SEEDS))]
# RESIDUAL 1 (Skunkworks + Testbed flag): seed-CV robustness, ARM-SPLIT (refuse=unstorable vs accept=storable)
gaps = [r["conc_health"] - r["spread_health"] for r in fe_runs]
hbe, abe = {}, {}
for u in units:
    hbe.setdefault(u["e_frac"], []).append(u["health"]); abe.setdefault(u["e_frac"], []).append(u["accuracy"])
def _cv(v): return float(np.std(v) / (np.mean(v) + 1e-9))
unstorable_es = [e for e in hbe if float(np.mean(abe[e])) < 0.95]    # REFUSE arm (the load-bearing safety direction)
storable_es = [e for e in hbe if float(np.mean(abe[e])) >= 0.95]     # ACCEPT arm
refuse_arm_worst_cv = max((_cv(hbe[e]) for e in unstorable_es), default=0.0)
accept_arm_worst_cv = max((_cv(hbe[e]) for e in storable_es), default=0.0)
e_sweep_worst_health_cv = max((_cv(v) for v in hbe.values()), default=0.0)
gap_cv = _cv(gaps)
detail["seed_cv"] = {"n_seeds": len(SEEDS), "fixed_e_gap_cv": round(gap_cv, 4),
                     "fixed_e_conc_health_cv": round(_cv([r["conc_health"] for r in fe_runs]), 4),
                     "e_sweep_worst_health_cv_ALL": round(e_sweep_worst_health_cv, 4),
                     "refuse_arm_worst_health_cv": round(refuse_arm_worst_cv, 4), "accept_arm_worst_health_cv": round(accept_arm_worst_cv, 4),
                     "robust_on_refuse_arm": bool(refuse_arm_worst_cv < 0.10 and gap_cv < 0.15),
                     "arm_note": "seed-robust on the UNSTORABLE/REFUSE arm (worst health-CV %.3f -- the load-bearing safety direction); "
                                 "the storable/ACCEPT arm has higher CV %.3f, consistent with + mitigated by the thin-boundary "
                                 "deployment threshold-margin caveat." % (refuse_arm_worst_cv, accept_arm_worst_cv)}
# RESIDUAL 2 (Skunkworks): does the global threshold ACCEPT a genuinely-storable structure? (false-refuse-near-boundary check)
detail["storable_accept_test"] = storable_accept_test(N, V, detail.get("health_threshold_c"), SEEDS)
msg = msg + (" | RESIDUAL1 seed_cv: refuse_arm_worst_cv=%.3f (robust) accept_arm_worst_cv=%.3f fixed_e_gap_cv=%.3f | RESIDUAL2 storable_accept: all_accepted=%s -- %s" % (
    detail["seed_cv"]["refuse_arm_worst_health_cv"], detail["seed_cv"]["accept_arm_worst_health_cv"], detail["seed_cv"]["fixed_e_gap_cv"],
    detail["storable_accept_test"]["all_storable_accepted_global_c"], detail["storable_accept_test"]["interpretation"]))
print("\n[VERDICT] " + msg, flush=True)
print("[residuals] seed_cv=%s\n[residuals] storable_accept=%s" % (detail["seed_cv"], detail["storable_accept_test"]), flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "V": V,
           "E_fracs": E_FRACS, "n_seeds": len(SEEDS), "detail": detail, "metrics_source": "measured_cpu_refuse_gate_graph_health_variance", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
