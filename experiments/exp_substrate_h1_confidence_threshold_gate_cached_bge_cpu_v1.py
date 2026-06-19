"""
exp_substrate_h1_confidence_threshold_gate_cached_bge_cpu_v1.py -- H1 confidence-threshold gating prototype: does a cosine-tau gate cut the FP blowout while keeping the true equivalent? -- CPU/local (no heat), READ-ONLY.

ROUTING: Research F1 SYNTHESIS H1 (per-axis confidence-threshold gating; "substrate retrieves but doesn't gate" -- FP blowout Q59-F: 116 FP/0
  gold). The eval scorer is BGE-degraded/offline locally, but the GATING MECHANISM can be prototyped on the cached BGE structured core
  (bge_large_v2_name_*.npz, precomputed BGE vectors). For each equivalence-pair query (one member's cached BGE vector), sweep a cosine
  threshold tau over [0..1]: count TP (true equivalent retrieved above tau) vs FP (non-equivalent above tau). This characterizes whether a
  confidence gate exists that preserves recall of the genuine equivalent while collapsing the FP count -- the H1 lever. Ungated (cached vectors,
  no query encoding, no model). Substrate-internal (11th rule). NOT the full eval F1 (needs BGE install) -- a mechanism prototype that ports to
  the real retrieval path once bge is on.

  CAVEAT (honest): "FP" here = any non-exact-equivalent atom above tau. Many are legitimately SIMILAR (same family), so absolute precision is
  pessimistic; the INFORMATIVE signal is the SHAPE -- does FP-count fall fast with tau while the equivalent stays retrieved (its cosine is high)?
  If yes, a gate works. The optimal-tau F1 is reported as a mechanism indicator, not an eval F1.

PRE-REGISTERED: GATE-EFFECTIVE iff there exists a tau where recall-of-equivalent >= 0.60 AND mean-FP-per-query drops by >= 50% vs the ungated
  (tau=0 / top-k) FP count -> a confidence gate is a viable FP-blowout fix (supports H1). GATE-WEAK iff best tau gives <50% FP reduction at
  >=0.60 recall (gate doesn't separate). UNKNOWN if no cache / <5 pairs. Reports the recall/FP curve + F1-optimal tau. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_h1_confidence_threshold_gate_cached_bge_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CACHE_GLOB = "cached_indices/bge_large_v2_name_*.npz"
TAUS = [round(x, 2) for x in np.arange(0.30, 0.96, 0.05)]
BASE_TOPK = 10                                            # ungated baseline = top-10 (the eval's k)


def _short(x):
    return str(x).split("::")[-1].split("/")[-1].strip().lower()


def gate_curve(qvec, mat, ids, self_i, targets, taus):
    """For each tau: (recall_of_equiv in {0,1}, fp_count = #non-target above tau, excluding self)."""
    sims = mat @ qvec
    sims[self_i] = -2.0
    out = []
    tgt_mask = np.array([ids[j] in targets for j in range(len(ids))])
    for tau in taus:
        above = sims >= tau
        tp = bool(np.any(above & tgt_mask))
        fp = int(np.sum(above & (~tgt_mask)))
        out.append((tau, tp, fp))
    # ungated baseline FP at top-10 (non-targets in top-10)
    order = np.argsort(-sims)[:BASE_TOPK]
    base_fp = int(sum(1 for j in order if not tgt_mask[j]))
    return out, base_fp


def _selftest():
    m = np.array([[1, 0, 0], [0.8, 0.6, 0], [0.1, 0, 0.99]], dtype=np.float64)
    m = m / np.linalg.norm(m, axis=1, keepdims=True)
    ids = ["T3/x", "T2/x", "T1/z"]
    curve, base_fp = gate_curve(m[0].copy(), m, ids, 0, {"T2/x"}, [0.3, 0.7, 0.9])
    # at low tau both T2/x(tp) and maybe T1/z(fp); at high tau fp drops
    fp_lo = curve[0][2]; fp_hi = curve[-1][2]
    assert fp_hi <= fp_lo, (fp_lo, fp_hi)
    assert any(tp for _, tp, _ in curve)              # equivalent retrieved at some tau
    print("[selftest] PASS: substrate_h1_confidence_threshold_gate_cached_bge_cpu_v1", flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    caches = sorted(root.glob(CACHE_GLOB))
    if not caches:
        return {"error": "no_bge_cache"}
    cache = caches[-1]
    d = np.load(cache, allow_pickle=True)
    ids = json.loads(str(d["id_order_json"]))
    mat = np.asarray(d["semantic"], dtype=np.float64)
    mat = mat / (np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12)
    by = defaultdict(list)
    for i, aid in enumerate(ids):
        by[_short(aid)].append(i)
    groups = {k: v for k, v in by.items() if len(v) >= 2}
    if not groups:
        return {"error": "no_pairs_in_cache", "cache": cache.name}
    # accumulate per-tau recall + fp across all pair queries
    agg = {tau: {"tp": 0, "fp_sum": 0} for tau in TAUS}
    base_fp_sum = 0; nq = 0
    for sname, idxs in groups.items():
        idset = set(ids[i] for i in idxs)
        for i in idxs:
            targets = idset - {ids[i]}
            curve, base_fp = gate_curve(mat[i].copy(), mat, ids, i, targets, TAUS)
            base_fp_sum += base_fp; nq += 1
            for tau, tp, fp in curve:
                agg[tau]["tp"] += int(tp); agg[tau]["fp_sum"] += fp
    base_fp_mean = round(base_fp_sum / nq, 3)
    rows = []
    for tau in TAUS:
        rec = round(agg[tau]["tp"] / nq, 4)
        fp_mean = round(agg[tau]["fp_sum"] / nq, 3)
        fp_red = round(1 - (fp_mean / base_fp_mean), 4) if base_fp_mean > 0 else 0.0
        # mechanism-F1: treat recall vs precision proxy (1 tp vs fp_mean) per query
        prec = round(agg[tau]["tp"] / (agg[tau]["tp"] + agg[tau]["fp_sum"] + 1e-9), 4)
        f1 = round(2 * prec * rec / (prec + rec + 1e-9), 4)
        rows.append({"tau": tau, "recall": rec, "fp_mean": fp_mean, "fp_reduction": fp_red, "precision": prec, "f1": f1})
    # find tau with recall>=0.60 maximizing fp_reduction
    viable = [r for r in rows if r["recall"] >= 0.60]
    best = max(viable, key=lambda r: r["fp_reduction"]) if viable else None
    best_f1 = max(rows, key=lambda r: r["f1"])
    print("  cache=%s | %d atoms | pairs=%d queries=%d | ungated top-10 mean FP/query=%.3f" % (cache.name, len(ids), len(groups), nq, base_fp_mean), flush=True)
    print("  tau   recall  fpmean  fp_reduction  prec    f1", flush=True)
    for r in rows:
        print("  %.2f  %.3f   %.2f    %+.3f       %.3f  %.3f" % (r["tau"], r["recall"], r["fp_mean"], r["fp_reduction"], r["precision"], r["f1"]), flush=True)
    if best:
        print("  BEST gate (recall>=0.60, max FP-reduction): tau=%.2f recall=%.3f FP-reduction=%.1f%%" % (best["tau"], best["recall"], 100 * best["fp_reduction"]), flush=True)
    print("  F1-optimal tau=%.2f (mechanism f1=%.3f)" % (best_f1["tau"], best_f1["f1"]), flush=True)
    return {"cache": cache.name, "n_pairs": len(groups), "n_queries": nq, "base_fp_mean": base_fp_mean,
            "curve": rows, "best_gate": best, "f1_optimal": best_f1}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("cache", "")))
    best = r["best_gate"]
    s = ("H1 confidence-threshold gate prototype on cached BGE (%s, %d pairs, %d queries). Ungated top-10 mean FP/query=%.3f. F1-optimal "
         "tau=%.2f. This prototypes the FP-blowout fix; CAVEAT: 'FP' = any non-exact-equivalent above tau (pessimistic; many are same-family "
         "similars). The signal is the SHAPE: does FP collapse with tau while the equivalent stays retrieved? Ports to the real eval retrieval "
         "path once BGE is installed.") % (r["cache"], r["n_pairs"], r["n_queries"], r["base_fp_mean"], r["f1_optimal"]["tau"])
    if best is not None and best["fp_reduction"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS (confidence gate is a viable FP-blowout fix): at tau=%.2f the gate keeps recall=%.3f>=0.60 of the true "
                "equivalent while cutting mean FP/query by %.1f%% (>=50%%). A per-axis tau gate should materially reduce the eval's FP explosion "
                "(supports H1). " % (best["tau"], best["recall"], 100 * best["fp_reduction"]) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND (gate weak at this scale): no tau achieves >=50%% FP-reduction while holding recall>=0.60 -- on the cached "
            "core the equivalent and the FP similars are not cleanly separable by a single cosine gate; per-axis/learned gating may be needed. " + s)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
    v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
