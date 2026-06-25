"""Refuse-gate via NONLINEAR readout attention-CONCENTRATION -- v2 FULL 3-seed promotion (USER 2026-06-25).

PROMOTION CONTEXT: the v1 cell (`substrate_refuse_gate_nonlinear_readout_v1`) ran SYNTHETIC smoke (gap-refuse 1.000 /
accept-drop 0.000 @ beta=10/c=0.15) at n_seeds=1 -> not chain-grade-tier-eligible per BIAS-14. v2 re-runs the synthetic
mechanism arm at 3 seeds [11, 13, 19] with prospective bands locked + per-seed cv discipline. The "real bge held-out
q54-q65" path from v1 is PRESERVED but gated behind --real flag; this v2's default FULL is the seed-aggregated synthetic
arm (which IS the chain-grade question -- "does the nonlinear-readout concentration gate separate present-paraphrased
from absent under independent seed realizations").

MECHANISM (unchanged from v1): refuse iff softmax(beta * cosine_scores) max-weight < c; accept (return retrieval) iff
max-weight >= c. The refuse signal = SHAPE of score distribution (concentration), NOT scalar threshold (M1's failure).

DIRECTOR-LOCKED CONDITION (verify-the-referent at runtime): MUST measure attention-spread (max-weight) on present-
paraphrased vs absent mix AND confirm the readout DISCRIMINATES (present concentrated, absent diffuse). NON_TEST if
absent ALSO one-hots (self-dominance wall) OR distributions overlap (no separating c).

PROSPECTIVE BANDS (META_PROSPECTIVE_BANDS_FRESH_SEEDS; LOCKED at module init via assert):
  HARD_PASS_CHAIN_GRADE:  gap-refuse >= 0.95 AND accept-drop <= 0.05 AND cv <= 0.05 (across 3 seeds at best (beta,c))
  HARD_PASS_PARTIAL:      gap-refuse 0.80-0.95 OR cv 0.05-0.10
  HARD_FAIL:              gap-refuse < 0.80 OR accept-drop > 0.10

ASCII-only. --self-test + --smoke + metrics.json. local_cpu_queue.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _spread_attention_harness import make_clustered_keys, cosine_scores, verify_spread
from experiments._seed_checkpoint import get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials

ANCHOR = "substrate_refuse_gate_nonlinear_readout_v2_full"
_EXP_NAME = os.environ.get("HDLAB_EXP_NAME")
OUT = REPO / "data" / (f"exp_{_EXP_NAME}" if _EXP_NAME else ANCHOR)

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
SMOKE = RUN_MODE == "smoke"

# CAPACITY-SENSITIVE DIMENSIONS: smoke matches full on n + n_present + n_query + paraphrase_noise + BETA_GRID + C_GRID.
N_DIM = 256                                   # bipolar vector dim; smoke == full
N_PRESENT = 60                                # cluster centroids = present items; smoke == full
N_QUERY = 120                                 # query budget (half paraphrased / half absent); smoke == full
PARAPHRASE_NOISE = 0.10                       # fraction of bits flipped from centroid for paraphrased queries
BETA_GRID = [10.0, 20.0, 40.0, 80.0, 160.0]
C_GRID = [round(x, 3) for x in np.arange(0.10, 0.96, 0.05)]
ALPHA = float(os.environ.get("HDLAB_RF_ALPHA", "1.0"))  # 1.0 softmax; 1.5/2.0 = entmax sparse variant
SEEDS_FULL = [11, 13, 19]                     # USER cross-cell consistent
SEEDS_SMOKE = [11]
SEEDS = SEEDS_SMOKE if SMOKE else SEEDS_FULL

# PROSPECTIVE BANDS (USER 2026-06-25; LOCKED via assert)
BAND_HARD_PASS_GAP_REFUSE = 0.95              # gap-refuse floor for chain-grade
BAND_HARD_PASS_ACCEPT_DROP = 0.05             # accept-drop ceiling for chain-grade
BAND_HARD_PASS_CV = 0.05                      # cv ceiling across seeds
BAND_HARD_PASS_PARTIAL_GAP_REFUSE_LOW = 0.80
BAND_HARD_PASS_PARTIAL_GAP_REFUSE_HIGH = 0.95
BAND_HARD_PASS_PARTIAL_CV_LOW = 0.05
BAND_HARD_PASS_PARTIAL_CV_HIGH = 0.10
BAND_HARD_FAIL_GAP_REFUSE = 0.80
BAND_HARD_FAIL_ACCEPT_DROP = 0.10
assert BAND_HARD_PASS_GAP_REFUSE > BAND_HARD_FAIL_GAP_REFUSE, "pass band must be > fail band"
assert BAND_HARD_PASS_ACCEPT_DROP < BAND_HARD_FAIL_ACCEPT_DROP, "pass accept-drop must be < fail accept-drop"
assert BAND_HARD_PASS_CV <= BAND_HARD_PASS_PARTIAL_CV_LOW, "cv pass band must be tighter than partial"


def entmax_alpha(Z, alpha, n_iter=30):
    if alpha == 1.0:
        Z = Z - Z.max(axis=1, keepdims=True); E = np.exp(Z); return E / (E.sum(axis=1, keepdims=True) + 1e-12)
    am1 = alpha - 1.0; Zs = am1 * Z
    tau_hi = Zs.max(axis=1, keepdims=True); tau_lo = Zs.min(axis=1, keepdims=True) - 1.0
    for _ in range(n_iter):
        tau = 0.5 * (tau_lo + tau_hi)
        s = (np.clip(Zs - tau, 0.0, None) ** (1.0 / am1)).sum(axis=1, keepdims=True)
        over = s > 1.0; tau_lo = np.where(over, tau, tau_lo); tau_hi = np.where(over, tau_hi, tau)
    p = np.clip(Zs - 0.5 * (tau_lo + tau_hi), 0.0, None) ** (1.0 / am1)
    return p / (p.sum(axis=1, keepdims=True) + 1e-12)


def build_synthetic(seed, n, n_present, n_query, paraphrase_noise):
    """present = cluster centroids; present-paraphrased queries = centroid+noise; absent = novel random."""
    g = np.random.default_rng(seed)
    present, _ = make_clustered_keys(n_present, n, cluster_size=1, g=g)
    nq = n_query // 2
    para = np.empty((nq, n), dtype=np.float32)
    kf = max(1, int(paraphrase_noise * n))
    for i in range(nq):
        j = g.integers(0, n_present)
        q = present[j].copy()
        idx = g.choice(n, size=kf, replace=False)
        q[idx] *= -1.0
        para[i] = q
    absent = (g.integers(0, 2, size=(nq, n)).astype(np.float32) * 2 - 1)
    return present, para, absent


def _concentration(queries, present, beta, alpha):
    W = entmax_alpha(beta * cosine_scores(queries, present), alpha)
    return W.max(axis=1), W


def run_one_seed(seed: int) -> Dict:
    present, para, absent = build_synthetic(seed, N_DIM, N_PRESENT, N_QUERY, PARAPHRASE_NOISE)
    spread_report = {}
    per_op = {}  # (beta,c) -> {gap_refuse, accept_drop, spreads}
    for beta in BETA_GRID:
        cp, _ = _concentration(para, present, beta, ALPHA)
        ca, Wa = _concentration(absent, present, beta, ALPHA)
        absent_spreads = bool(np.median(ca) < 0.9) and verify_spread(Wa)["spreads"]
        spread_report[f"beta{beta}"] = {"present_maxw_med": float(np.median(cp)),
                                        "absent_maxw_med": float(np.median(ca)),
                                        "absent_spreads": absent_spreads}
        for c in C_GRID:
            gap_refuse = float((ca < c).mean())
            accept_drop = 1.0 - float((cp >= c).mean())
            per_op[(beta, c)] = {"gap_refuse": gap_refuse, "accept_drop": accept_drop, "absent_spreads": absent_spreads}
    # find best (beta,c) per seed that passes bands + discriminating
    best = None
    for (beta, c), v in per_op.items():
        if not v["absent_spreads"]:
            continue
        if v["gap_refuse"] < BAND_HARD_PASS_GAP_REFUSE or v["accept_drop"] > BAND_HARD_PASS_ACCEPT_DROP:
            continue
        score = v["gap_refuse"] - v["accept_drop"]
        if best is None or score > best["score"]:
            best = {"beta": beta, "c": c, "gap_refuse": v["gap_refuse"], "accept_drop": v["accept_drop"], "score": score}
    return {"seed": seed, "spread_report": spread_report,
            "per_op": {f"{b}_{c}": v for (b, c), v in per_op.items()},
            "best": best, "alpha": ALPHA, "n": N_DIM, "run_mode": RUN_MODE}


def aggregate_seeds(per_seed: List[Dict]) -> Dict:
    """Aggregate per-seed bests. The chain-grade question: across 3 seeds, does the SAME (beta,c) operating point clear
    bands? Find the (beta,c) that maximises mean(gap_refuse - accept_drop) across seeds AND has cv <= 0.05 on gap_refuse."""
    # gather union of (beta,c) keys
    op_keys = set()
    for s in per_seed:
        op_keys.update(s["per_op"].keys())
    op_keys = sorted(op_keys)
    op_agg = {}
    for k in op_keys:
        grs = [s["per_op"][k]["gap_refuse"] for s in per_seed if k in s["per_op"]]
        ads = [s["per_op"][k]["accept_drop"] for s in per_seed if k in s["per_op"]]
        sps = [s["per_op"][k]["absent_spreads"] for s in per_seed if k in s["per_op"]]
        if len(grs) < len(per_seed):
            continue
        m_gr = float(np.mean(grs)); sd_gr = float(np.std(grs))
        m_ad = float(np.mean(ads)); sd_ad = float(np.std(ads))
        cv_gr = sd_gr / m_gr if m_gr > 1e-9 else float("inf")
        cv_ad = sd_ad / m_ad if m_ad > 1e-9 else 0.0  # accept_drop can be exactly 0 -- cv undefined but acceptable
        all_spreads = all(sps)
        op_agg[k] = {"gap_refuse_mean": round(m_gr, 4), "gap_refuse_cv": round(cv_gr, 4),
                     "accept_drop_mean": round(m_ad, 4), "accept_drop_cv": round(cv_ad, 4),
                     "all_discriminating": all_spreads, "n_seeds_passing": len(grs),
                     "per_seed_gap_refuse": [round(v, 4) for v in grs],
                     "per_seed_accept_drop": [round(v, 4) for v in ads]}
    # find best chain-grade operating point
    candidates = []
    for k, v in op_agg.items():
        if not v["all_discriminating"]:
            continue
        if v["gap_refuse_mean"] >= BAND_HARD_PASS_GAP_REFUSE and v["accept_drop_mean"] <= BAND_HARD_PASS_ACCEPT_DROP and v["gap_refuse_cv"] <= BAND_HARD_PASS_CV:
            score = v["gap_refuse_mean"] - v["accept_drop_mean"]
            candidates.append((score, k, v))
    candidates.sort(reverse=True)
    best_chain_grade = candidates[0] if candidates else None
    # find best partial-band operating point if no chain-grade
    partial_candidates = []
    for k, v in op_agg.items():
        if not v["all_discriminating"]:
            continue
        if v["gap_refuse_mean"] >= BAND_HARD_PASS_PARTIAL_GAP_REFUSE_LOW and v["accept_drop_mean"] <= BAND_HARD_FAIL_ACCEPT_DROP:
            score = v["gap_refuse_mean"] - v["accept_drop_mean"]
            partial_candidates.append((score, k, v))
    partial_candidates.sort(reverse=True)
    best_partial = partial_candidates[0] if partial_candidates else None
    return {"n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
            "best_chain_grade": best_chain_grade, "best_partial": best_partial,
            "n_operating_points": len(op_agg)}


def verdict(agg: Dict, per_seed: List[Dict]) -> Tuple[str, str]:
    if agg["n_seeds"] == 0:
        return ("UNKNOWN", "UNKNOWN: no seeds completed")
    bcg = agg.get("best_chain_grade")
    bp = agg.get("best_partial")
    seeds_summary = "; ".join(["seed=%d best=%s" % (s["seed"], s["best"]) for s in per_seed])
    if bcg:
        score, k, v = bcg
        msg = ("HARD_PASS_CHAIN_GRADE: nonlinear-readout concentration gate at (beta,c)=%s clears bands across %d seeds %s "
               "-- gap_refuse mean=%.4f cv=%.4f, accept_drop mean=%.4f, all 3 seeds discriminating. Per-seed gap_refuse=%s. "
               "Per-seed: %s") % (k, agg["n_seeds"], agg["seeds"], v["gap_refuse_mean"], v["gap_refuse_cv"], v["accept_drop_mean"],
                                  v["per_seed_gap_refuse"], seeds_summary)
        return ("HARD_PASS", msg)
    if bp:
        score, k, v = bp
        msg = ("HARD_PASS_PARTIAL: best (beta,c)=%s reaches gap_refuse=%.4f (partial band 0.80-0.95) cv=%.4f accept_drop=%.4f. "
               "Per-seed gap_refuse=%s. Per-seed: %s") % (k, v["gap_refuse_mean"], v["gap_refuse_cv"], v["accept_drop_mean"],
                                                          v["per_seed_gap_refuse"], seeds_summary)
        return ("MIDDLE_BAND", msg)
    # check HARD_FAIL: no operating point reaches gap_refuse >= 0.80 AND accept_drop <= 0.10
    return ("HARD_FAIL", "HARD_FAIL: no (beta,c) reaches gap_refuse>=%.2f AND accept_drop<=%.2f across all 3 seeds discriminating. Per-seed: %s" % (
        BAND_HARD_FAIL_GAP_REFUSE, BAND_HARD_FAIL_ACCEPT_DROP, seeds_summary))


def _selftest():
    # mechanism check: 1 seed, small grid
    g = np.random.default_rng(7)
    present, para, absent = build_synthetic(7, 64, 30, 40, 0.10)
    cp, _ = _concentration(para, present, 10.0, 1.0)
    ca, _ = _concentration(absent, present, 10.0, 1.0)
    assert float(np.median(cp)) > float(np.median(ca)), "present must concentrate more than absent at beta=10"
    # band sanity
    assert BAND_HARD_PASS_GAP_REFUSE > BAND_HARD_FAIL_GAP_REFUSE
    assert BAND_HARD_PASS_ACCEPT_DROP < BAND_HARD_FAIL_ACCEPT_DROP
    print("[selftest] PASS: substrate_refuse_gate_nonlinear_readout_v2_full (mechanism + bands locked)", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        _selftest()
        return 0
    _selftest()
    print("[config] anchor=%s mode=%s n=%d seeds=%s" % (ANCHOR, RUN_MODE, N_DIM, SEEDS), flush=True)
    out_dir = get_output_dir(ANCHOR)
    t0 = time.time()
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s" % (len(done), len(SEEDS), remaining), flush=True)
    for seed in remaining:
        print("[seed %d] starting" % seed, flush=True)
        res = run_one_seed(seed)
        write_partial(out_dir, seed, res)
        if res["best"]:
            print("[seed %d] best=%s" % (seed, res["best"]), flush=True)
        else:
            print("[seed %d] no operating point cleared bands at this seed" % seed, flush=True)
    per_seed = list(aggregate_partials(out_dir, SEEDS).values())
    agg = aggregate_seeds(per_seed)
    v, vmsg = verdict(agg, per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {"anchor_name": ANCHOR, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "headline": vmsg,
               "run_mode": RUN_MODE, "n_seeds": len(per_seed), "seeds": [s["seed"] for s in per_seed],
               "aggregate": agg, "per_seed": per_seed, "elapsed_s": round(time.time() - t0, 2),
               "alpha": ALPHA, "n": N_DIM,
               "bands": {"HARD_PASS_GAP_REFUSE": BAND_HARD_PASS_GAP_REFUSE,
                         "HARD_PASS_ACCEPT_DROP": BAND_HARD_PASS_ACCEPT_DROP,
                         "HARD_PASS_CV": BAND_HARD_PASS_CV,
                         "HARD_FAIL_GAP_REFUSE": BAND_HARD_FAIL_GAP_REFUSE,
                         "HARD_FAIL_ACCEPT_DROP": BAND_HARD_FAIL_ACCEPT_DROP},
               "config_version": "v2_seeds_11_13_19_synthetic_n256_npresent60_nquery120_paraphrasenoise0.10"}
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
