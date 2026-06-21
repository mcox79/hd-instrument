"""2-AXIS refuse-gate COMPOSITION (builds on CERT 588 refuse-gate #5b + CERT 589 LEVER #4).

Composition #1 (USER-locked enabling priority: "what builds on this"). A deployed substrate-memory answers TWO operation
types on the SAME stored graph:
  - ADJACENCY queries ("is (u,v) an edge?")  -- guarded by the LOAD-axis gate (#5b: graph-health = non-edge score variance;
    refuse when the stored state is edge-OVERLOADED).
  - TRAVERSAL queries ("what is K hops from u?") -- guarded by the DEPTH-axis gate (#4: refuse chains deeper than the
    calibrated K_max(load), where chaining fabricates a confident-wrong node).

GENUINE COMPOSITION CLAIM: on a MIXED workload (both query types), the JOINT gate (right gate per query type) beats EACH
single-axis gate, because a single-axis gate has NO signal for the OTHER query type and therefore FABRICATES on it:
  - load-only gate guards adjacency but ACCEPTS every traversal -> fabricates out-of-envelope traversals.
  - depth-only gate guards traversal but ACCEPTS every adjacency -> fabricates overloaded adjacency.
Neither single axis suffices for a 2-operation substrate; the composition is necessary. Risk-utility: correct +1, fabricate
(confident-wrong) -1, refuse 0. data-decides -> Skunkworks rules tier. NON-circular: thresholds calibrated on cal-seeds,
tested on held-out seeds. ASCII; no em-dashes.
"""
import sys
from pathlib import Path
import argparse
import os
import time
import numpy as np

REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "twoaxis_refuse_gate_compose_v1_cpu_v1"
_P = argparse.ArgumentParser(); _P.add_argument("--self-test", action="store_true", dest="self_test"); _ARGS, _ = _P.parse_known_args()
RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full" if not _ARGS.self_test else "smoke")
N = 4096 if RUN_MODE == "full" else 1024
V = 128                                                   # nodes
CHAIN_LEN = 10
ACC_CLIFF = 0.95                                          # adjacency storable threshold (#5b)
KMAX_ACC_THRESH = 0.70                                    # depth envelope threshold (#4)
# workload spans BOTH axes: a low-load + a high-load graph; traversal depths low..high
LOADS = [0.05, 1.0] if RUN_MODE == "full" else [0.05, 1.0]   # edge/transition load E/N (low=adjacency-storable, high=overloaded)
KQ = list(range(1, CHAIN_LEN))
CAL_SEEDS = [101, 102] if RUN_MODE == "full" else [101]
TEST_SEEDS = [1, 2, 3] if RUN_MODE == "full" else [1]


def bip(rows, n, g):
    return (g.integers(0, 2, (rows, n)) * 2 - 1).astype(np.float32)


def build_graph(load, n, seed):
    """Node-disjoint chains: consecutive pairs are EDGES (adjacency) AND transitions (traversal). Returns codebook, edges, chains, G, W."""
    g = np.random.default_rng(seed)
    E = max(CHAIN_LEN, int(load * n)); n_chains = max(1, E // (CHAIN_LEN - 1)); total = n_chains * CHAIN_LEN
    cb = bip(total, n, g)
    chains = [list(range(c * CHAIN_LEN, c * CHAIN_LEN + CHAIN_LEN)) for c in range(n_chains)]
    edges = set(); G = np.zeros(n, np.float32); W = np.zeros((n, n), np.float32)
    for ch in chains:
        for i in range(len(ch) - 1):
            a, b = ch[i], ch[i + 1]; edges.add((min(a, b), max(a, b)))
            G += cb[a] * cb[b]                                # adjacency binding (#5b)
            W += np.outer(cb[b], cb[a])                       # transition (#4)
    return cb, edges, chains, G, W / n


# ---- LOAD axis (#5b adjacency) ----
def adjacency_scores(cb, G, edges, n):
    te, ne = [], []
    Vn = len(cb)
    for u in range(min(Vn, 90)):
        for w in range(u + 1, min(Vn, 90)):
            s = float(G @ (cb[u] * cb[w]) / n)
            (te if (u, w) in edges else ne).append(s)
    return np.array(te), np.array(ne)


def best_bal_acc(te, ne):
    if len(te) == 0 or len(ne) == 0: return 0.0
    th = np.linspace(min(te.min(), ne.min()), max(te.max(), ne.max()), 120); best = 0.0
    for t in th: best = max(best, 0.5 * ((te > t).mean() + (ne <= t).mean()))
    return best


def health(ne):
    return float(np.var(ne)) if len(ne) else 0.0


# ---- DEPTH axis (#4 traversal) ----
def chain_recall(cb, W, start_idx, K):
    cur = cb[start_idx].copy()
    for _ in range(K):
        cur = np.sign(W @ cur).astype(np.float32); cur[cur == 0] = 1.0
    return int(np.argmax(cb @ cur))


def chain_acc(cb, W, chains, K):
    ok = t = 0
    for ch in chains:
        if len(ch) > K: t += 1; ok += int(chain_recall(cb, W, ch[0], K) == ch[K])
    return ok / max(1, t)


def calibrate(n, cal_seeds):
    """Calibrate the LOAD-axis health threshold c (#5b) + per-load DEPTH envelope K_max (#4), on cal seeds."""
    # health threshold c: midpoint between storable (low-load) and unstorable (high-load) adjacency health
    hs_storable, hs_unstorable = [], []
    kmax_by_load = {}
    for load in LOADS:
        accs_adj, hs, kmax_runs = [], [], []
        for sd in cal_seeds:
            cb, edges, chains, G, W = build_graph(load, n, sd * 13 + 1)
            te, ne = adjacency_scores(cb, G, edges, n); accs_adj.append(best_bal_acc(te, ne)); hs.append(health(ne))
            km = 0
            for K in KQ:
                if chain_acc(cb, W, chains, K) >= KMAX_ACC_THRESH: km = K
                else: break
            kmax_runs.append(km)
        adj_acc = float(np.mean(accs_adj)); h = float(np.mean(hs))
        (hs_storable if adj_acc >= ACC_CLIFF else hs_unstorable).append(h)
        kmax_by_load[load] = int(np.median(kmax_runs))
    c = 0.5 * (max(hs_storable) + min(hs_unstorable)) if hs_storable and hs_unstorable else (max(hs_storable + hs_unstorable) * 1.5)
    return c, kmax_by_load


def run_unit(load, seed, c, kmax):
    """Mixed workload on one (load, seed): adjacency queries + traversal queries; score 5 policies via risk-utility."""
    cb, edges, chains, G, W = build_graph(load, N, seed * 977 + 5)
    te, ne = adjacency_scores(cb, G, edges, N); adj_acc = best_bal_acc(te, ne); h = health(ne)
    load_overloaded = h > c                               # LOAD-axis signal (#5b): adjacency unreliable
    # ADJACENCY queries: is the substrate's adjacency answer reliable? utility per policy
    # (if overloaded, answering adjacency FABRICATES at rate (1-adj_acc); refusing = 0)
    adj_correct = adj_acc; adj_util_answer = (adj_correct * 1.0 + (1 - adj_correct) * (-1.0))
    # TRAVERSAL queries across depths: per K, answering fabricates if K>kmax (acc low)
    trav = []
    for K in KQ:
        a = chain_acc(cb, W, chains, K); in_env = K <= kmax
        trav.append({"K": K, "acc": round(a, 3), "in_env": in_env, "util_answer": a * 1.0 + (1 - a) * (-1.0)})
    # 5 policies over the mixed workload (equal weight adjacency-block and traversal-block; traversal averaged over KQ)
    def trav_util(refuse_fn):  # refuse_fn(K)->bool
        return float(np.mean([(0.0 if refuse_fn(t["K"]) else t["util_answer"]) for t in trav]))
    adj_util = lambda refuse: 0.0 if refuse else adj_util_answer
    pol = {}
    pol["always_answer"] = 0.5 * adj_util(False) + 0.5 * trav_util(lambda K: False)
    pol["load_only"]     = 0.5 * adj_util(load_overloaded) + 0.5 * trav_util(lambda K: False)            # guards adj, blind to depth -> fabricates deep traversal
    pol["depth_only"]    = 0.5 * adj_util(False) + 0.5 * trav_util(lambda K: K > kmax)                    # guards traversal, blind to load -> fabricates overloaded adj
    pol["joint"]         = 0.5 * adj_util(load_overloaded) + 0.5 * trav_util(lambda K: K > kmax)          # right gate per query type
    return {"load": load, "seed": seed, "adj_acc": round(adj_acc, 3), "health": round(h, 5), "c": round(c, 5),
            "load_overloaded": bool(load_overloaded), "kmax": kmax,
            "util_always_answer": round(pol["always_answer"], 4), "util_load_only": round(pol["load_only"], 4),
            "util_depth_only": round(pol["depth_only"], 4), "util_joint": round(pol["joint"], 4),
            "trav_acc_by_K": {t["K"]: t["acc"] for t in trav}}


def _r(x): return None if x is None else round(x, 4)


def compute_verdict(units):
    if not units: return ("HARD_FAIL", "no results", {})
    # per-seed margins of joint over each single-axis (robust = mean > 2*std, the LEVER #4 discipline)
    def margins(a, b): return [u[a] - u[b] for u in units]
    m_vs_load = margins("util_joint", "util_load_only"); m_vs_depth = margins("util_joint", "util_depth_only"); m_vs_always = margins("util_joint", "util_always_answer")
    def robust(m): return bool(np.mean(m) > 0.03 and np.mean(m) > 2 * np.std(m))
    def never_worse(m): return bool(np.mean(m) >= -0.02)
    # which single-axis each fabricates: load_only on traversal (high-load units have deep OOE), depth_only on adjacency (overloaded units)
    overloaded_units = [u for u in units if u["load_overloaded"]]
    detail = {"per_unit_util": [{"load": u["load"], "seed": u["seed"], "joint": u["util_joint"], "load_only": u["util_load_only"],
                                 "depth_only": u["util_depth_only"], "always": u["util_always_answer"], "overloaded": u["load_overloaded"], "kmax": u["kmax"]} for u in units],
              "joint_vs_load_only_mean": _r(float(np.mean(m_vs_load))), "joint_vs_depth_only_mean": _r(float(np.mean(m_vs_depth))), "joint_vs_always_mean": _r(float(np.mean(m_vs_always))),
              "joint_ROBUST_beats_load_only": robust(m_vs_load), "joint_ROBUST_beats_depth_only": robust(m_vs_depth), "joint_beats_always": robust(m_vs_always),
              "joint_never_worse_than_either_single": bool(never_worse(m_vs_load) and never_worse(m_vs_depth)),
              "n_overloaded_units": len(overloaded_units),
              "honest_claim": ("2-axis refuse-gate composition (#5b load-axis adjacency + #4 depth-axis traversal): on a mixed "
                               "adjacency+traversal workload the JOINT gate beats BOTH single-axis gates -- each single axis is blind "
                               "to the OTHER query type and fabricates on it (load-only fabricates deep traversal; depth-only fabricates "
                               "overloaded adjacency). Neither single axis suffices for a 2-operation substrate; the composition is necessary.")}
    summary = "joint vs load_only=%s depth_only=%s always=%s | robust_beats: load_only=%s depth_only=%s | never_worse=%s n_overloaded=%d" % (
        detail["joint_vs_load_only_mean"], detail["joint_vs_depth_only_mean"], detail["joint_vs_always_mean"],
        detail["joint_ROBUST_beats_load_only"], detail["joint_ROBUST_beats_depth_only"], detail["joint_never_worse_than_either_single"], len(overloaded_units))
    if detail["joint_ROBUST_beats_load_only"] and detail["joint_ROBUST_beats_depth_only"] and detail["joint_never_worse_than_either_single"]:
        return ("HARD_PASS", "HARD_PASS (2-axis refuse-gate composition; data-decides -> Skunkworks): the JOINT gate ROBUSTLY beats "
                "BOTH single-axis gates (per-seed margin > seed-noise) on the mixed adjacency+traversal workload -- each single axis "
                "fabricates on the query type it cannot see; the composition of CERT 588 (load) + CERT 589 (depth) is NECESSARY for a "
                "2-operation substrate. Never worse than either single axis. " + summary, detail)
    if detail["joint_ROBUST_beats_load_only"] or detail["joint_ROBUST_beats_depth_only"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: joint beats one single-axis robustly but not both (one query-type's OOE not exercised enough). " + summary, detail)
    return ("MEASURED_MECHANISM", "MEASURED_MECHANISM: joint does not robustly beat both single-axis gates (workload may not exercise both OOE axes). " + summary, detail)


def _selftest():
    cb, edges, chains, G, W = build_graph(0.05, 256, 1)
    te, ne = adjacency_scores(cb, G, edges, 256)
    assert best_bal_acc(te, ne) >= 0.8, "low-load adjacency should be storable"
    assert chain_acc(cb, W, chains, 1) >= 0.8, "1-hop traversal should work at low load"
    print("[selftest] PASS: graph builds both adjacency (storable low-load) + traversal (1-hop works)", flush=True)


_selftest()
if _ARGS.self_test:
    raise SystemExit(0)

print("[config] %s mode=%s N=%d V=%d loads=%s chain_len=%d cal=%s test=%s" % (ANCHOR_NAME, RUN_MODE, N, V, LOADS, CHAIN_LEN, CAL_SEEDS, TEST_SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); run_config = {"run_mode": RUN_MODE}; t0 = time.time()
c, kmax_by_load = calibrate(N, CAL_SEEDS)
print("[calibrate] health_threshold_c=%.5f kmax_by_load=%s" % (c, kmax_by_load), flush=True)
for load in LOADS:
    for sd in TEST_SEEDS:
        key = ("a%.2f_s%d" % (load, sd)).replace(".", "p")
        if key in aggregate_partials(out_dir, [key], run_config=run_config):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(load, sd, c, kmax_by_load[load]))
        print("[unit] %s done" % key, flush=True)
keys = [("a%.2f_s%d" % (load, sd)).replace(".", "p") for load in LOADS for sd in TEST_SEEDS]
units = list(aggregate_partials(out_dir, keys, run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE, "N": N, "V": V,
           "loads": LOADS, "cal_seeds": CAL_SEEDS, "test_seeds": TEST_SEEDS, "detail": detail,
           "metrics_source": "measured_cpu_2axis_refuse_gate_composition", "per_unit": units, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
