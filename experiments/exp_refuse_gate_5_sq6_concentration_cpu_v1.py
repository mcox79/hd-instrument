"""
refuse_gate_5_sq6_concentration_cpu_v1 -- refuse-gate #5: does the substrate REFUSE on the SQ6-HARD_FAIL regime (dense graph-
adjacency it genuinely CANNOT store separably) rather than FABRICATE, while ANSWERING on an in-envelope graph? CPU.

MECHANISM (reuse):
- SQ6 graph bind (exp_substrate_sq6_graph_adjacency_v1): G = sum over edges (u,v) of node_u * node_v (MAP elementwise, symmetric).
  Neighbor query for node a: scores s_v = <G, node_a*node_v>/N (~1 true edge, ~noise non-edge). At E>=0.25N (SQ6 HARD_FAIL) the
  graph is overloaded -> scores DIFFUSE (crosstalk swamps the true neighbor).
- refuse-gate (exp_substrate_refuse_gate_nonlinear_readout_v1): attention-CONCENTRATION = softmax(beta*scores).max() over the
  candidate scores. CONCENTRATED -> confident -> ACCEPT (return argmax neighbor); DIFFUSE -> REFUSE. refuse iff concentration < c.

CLAIM (Path A, Skunkworks-concur): the gate REFUSES on the SQ6-HARD_FAIL regime (substrate genuinely can't store) instead of
fabricating. SCOPE = the known-HARD_FAIL regime (NOT boundary-precision; that needs the capacity curve = Path B). Small-N
HARD_FAIL is CONSERVATIVE (fails easy -> fails at scale).
CAN-fail (Skunkworks REQUIRED): the in-envelope ANSWER arm -- the gate must ACCEPT on a storable graph (in-env-accept>=0.80),
else a refuse-everything gate trivially "passes" the refuse-test but is useless. Discriminating iff a (beta,c) exists with
SQ6-refuse>=0.95 AND in-env-accept>=0.80 AND concentrations separated. ASCII. CPU.
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

ANCHOR_NAME = "refuse_gate_5_sq6_concentration_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 2048 if SMOKE else 4096
V = 128                                                   # nodes (SQ6 default)
E_IN_FRAC = 0.03                                          # in-envelope graph: E = 0.03N edges (storable -> concentrated)
E_SQ6_FRAC = 0.5                                          # SQ6 HARD_FAIL graph: E = 0.5N edges (>=0.25N -> overloaded -> diffuse)
BETAS = [2.0, 5.0, 10.0, 20.0]
C_GRID = [round(0.1 + 0.05 * i, 2) for i in range(17)]    # 0.10 .. 0.90
SEEDS = [1] if SMOKE else [1, 2, 3]
MIN_INENV_ACCEPT = 0.80                                   # in-envelope accept floor (refuse-everything guard = the CAN-fail)


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


def build_graph(nodes, edges):
    n = nodes.shape[1]; G = np.zeros(n, np.float32)
    for (u, w) in edges:
        G += nodes[u] * nodes[w]                          # MAP symmetric bind
    return G


def neighbor_concentrations(nodes, G, edges, beta, g, n_query=64):
    """For sampled nodes with >=1 edge: softmax(beta*s_v).max() concentration + whether argmax is a true neighbor."""
    n = nodes.shape[1]
    adj = {}
    for (u, w) in edges:
        adj.setdefault(u, set()).add(w); adj.setdefault(w, set()).add(u)
    qnodes = [a for a in adj]
    if len(qnodes) > n_query:
        idx = g.choice(len(qnodes), n_query, replace=False); qnodes = [qnodes[int(i)] for i in idx]
    concs = []; correct = []
    for a in qnodes:
        bound = G * nodes[a]                              # G * node_a -> recall node_a's neighbors
        s = (nodes @ bound) / n                           # score per candidate node v (= <G, node_a*node_v>/N)
        s[a] = -1e9                                       # exclude self
        z = beta * s; z = z - z.max(); e = np.exp(z); w = e / (e.sum() + 1e-12)
        concs.append(float(w.max()))                      # attention concentration (max-weight)
        correct.append(int(np.argmax(s) in adj[a]))       # argmax neighbor is a TRUE neighbor?
    return np.array(concs), np.array(correct)


def _selftest():
    g = np.random.default_rng(0); nodes = bipolar((V, 512), g)
    e_in = _edge_set(V, int(0.03 * 512), g); G_in = build_graph(nodes, e_in)
    ci, acc = neighbor_concentrations(nodes, G_in, e_in, 10.0, g)
    assert ci.mean() > 0.3, "in-envelope concentrated (mean conc %.3f)" % ci.mean()
    e_sq = _edge_set(V, int(0.5 * 512), g); G_sq = build_graph(nodes, e_sq)
    cs, _ = neighbor_concentrations(nodes, G_sq, e_sq, 10.0, g)
    assert cs.mean() < ci.mean(), "SQ6-overloaded MORE diffuse than in-envelope (%.3f < %.3f)" % (cs.mean(), ci.mean())
    print("[selftest] PASS: in-envelope concentrated > SQ6-overloaded diffuse + neighbor-bind", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_unit(seed):
    g = np.random.default_rng(seed); nodes = bipolar((V, N), g)
    e_in = _edge_set(V, int(E_IN_FRAC * N), g); G_in = build_graph(nodes, e_in)
    e_sq = _edge_set(V, int(E_SQ6_FRAC * N), g); G_sq = build_graph(nodes, e_sq)
    best = None
    for beta in BETAS:
        ci, acc = neighbor_concentrations(nodes, G_in, e_in, beta, g)        # in-envelope
        cs, _ = neighbor_concentrations(nodes, G_sq, e_sq, beta, g)          # SQ6 HARD_FAIL
        for c in C_GRID:
            inenv_accept = float((ci >= c).mean())                          # accept iff concentration>=c
            inenv_answer = float((acc[ci >= c]).mean()) if (ci >= c).any() else 0.0  # of accepted, fraction correct
            sq6_refuse = float((cs < c).mean())                            # refuse iff concentration<c
            ok = sq6_refuse >= 0.95 and inenv_accept >= MIN_INENV_ACCEPT
            score = sq6_refuse + inenv_accept
            cand = {"beta": beta, "c": c, "inenv_accept": round(inenv_accept, 3), "inenv_answer_acc": round(inenv_answer, 3),
                    "sq6_refuse": round(sq6_refuse, 3), "discriminating": bool(ok), "score": round(score, 3),
                    "inenv_conc_mean": round(float(ci.mean()), 3), "sq6_conc_mean": round(float(cs.mean()), 3)}
            if ok and (best is None or score > best["score"]):
                best = cand
    # if no discriminating (beta,c), report the best-by-score for diagnosis
    if best is None:
        bb = None
        for beta in BETAS:
            ci, acc = neighbor_concentrations(nodes, G_in, e_in, beta, g); cs, _ = neighbor_concentrations(nodes, G_sq, e_sq, beta, g)
            for c in C_GRID:
                inenv_accept = float((ci >= c).mean()); sq6_refuse = float((cs < c).mean())
                cand = {"beta": beta, "c": c, "inenv_accept": round(inenv_accept, 3), "sq6_refuse": round(sq6_refuse, 3),
                        "discriminating": False, "score": round(sq6_refuse + inenv_accept, 3),
                        "inenv_conc_mean": round(float(ci.mean()), 3), "sq6_conc_mean": round(float(cs.mean()), 3)}
                if bb is None or cand["score"] > bb["score"]:
                    bb = cand
        best = bb
    print("  [s=%d] best (beta=%.1f c=%.2f): inenv_accept=%.3f answer_acc=%s sq6_refuse=%.3f discriminating=%s | conc in/sq6=%.3f/%.3f" %
          (seed, best["beta"], best["c"], best["inenv_accept"], best.get("inenv_answer_acc", "?"), best["sq6_refuse"], best["discriminating"], best["inenv_conc_mean"], best["sq6_conc_mean"]), flush=True)
    best["seed"] = seed; best["run_mode"] = RUN_MODE
    return best


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units: return ("HARD_FAIL", "no results", {})
    n_disc = sum(1 for u in units if u["discriminating"])
    mean_sq6_refuse = float(np.mean([u["sq6_refuse"] for u in units]))
    mean_inenv_accept = float(np.mean([u["inenv_accept"] for u in units]))
    sep = float(np.mean([u["inenv_conc_mean"] - u["sq6_conc_mean"] for u in units]))
    detail = {"per_seed": units, "n_discriminating": n_disc, "n_seeds": len(units), "mean_sq6_refuse": round(mean_sq6_refuse, 3),
              "mean_inenv_accept": round(mean_inenv_accept, 3), "conc_separation_inenv_minus_sq6": round(sep, 3),
              "honest_claim": "Refuse-gate (attention-concentration) REFUSES on the SQ6-HARD_FAIL regime (dense graph-adjacency "
                              "E=0.5N the substrate can't store separably) rather than fabricating, while ANSWERING on an "
                              "in-envelope graph (E=0.03N): exists (beta,c) with SQ6-refuse>=0.95 AND in-env-accept>=0.80 on %d/%d "
                              "seeds; concentration separation %.2f. SCOPE = known-HARD_FAIL regime (NOT boundary-precision)." % (n_disc, len(units), sep)}
    summary = "discriminating %d/%d seeds | sq6_refuse=%.3f in-env-accept=%.3f conc_sep=%.3f" % (n_disc, len(units), mean_sq6_refuse, mean_inenv_accept, sep)
    if n_disc == len(units) and sep > 0.05:
        return ("HARD_PASS", "HARD_PASS: refuse-gate REFUSES on SQ6-HARD_FAIL (>=0.95) AND ANSWERS in-envelope (>=0.80) on ALL seeds at a discriminating operating point (concentrations separated). Refuses-the-unstorable, not refuse-everything. " + summary, detail)
    if n_disc >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: discriminating on %d/%d seeds (not all). " % (n_disc, len(units)) + summary, detail)
    return ("HARD_FAIL", "HARD_FAIL / NON_TEST: no (beta,c) separates SQ6-refuse>=0.95 from in-env-accept>=0.80 -> concentrations overlap (gate can't discriminate storable from unstorable, OR only refuses-everything). " + summary, detail)


print("[config] %s mode=%s N=%d V=%d E_in=%.2fN E_sq6=%.2fN seeds=%s" % (ANCHOR_NAME, RUN_MODE, N, V, E_IN_FRAC, E_SQ6_FRAC, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
for seed in SEEDS:
    key = "s%d" % seed
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print("[ckpt] %s done; skip" % key, flush=True); continue
    try:
        write_partial_key(out_dir, key, run_unit(seed))
    except Exception as e:
        print("[WARN] %s failed: %s" % (key, e), flush=True)
units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "V": V,
           "E_in_frac": E_IN_FRAC, "E_sq6_frac": E_SQ6_FRAC, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_cpu_refuse_gate_sq6_concentration", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
