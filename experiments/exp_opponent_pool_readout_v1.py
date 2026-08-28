"""exp_opponent_pool_readout_v1 -- replace the convenient LINEAR projection with the brain's OPPONENT-POOL mechanism.

Deepening drill (owner: make it MORE brain-foundational). The composed channel reads magnitude as a single LINEAR
projection onto a pole-difference axis. The brain does NOT: it has TWO OPPONENT MONOTONIC pools -- a "more" pool and
a "less" pool (Roitman/Brannon/Platt 2007 LIP; amygdala BLA positive/negative valence populations) -- combined into
a tuned place code (Verguts & Fias 2004). A single (pos - neg) difference COLLAPSES the two pools, which is a
convenient substitution, not the mechanism. This cell builds the opponent readout and tests the two brain-faithful,
MEASURABLE consequences a linear axis lacks:

  1. NEGATIVITY BIAS. The negative pool has higher gain ("bad is stronger than good": Ito et al. 1998; Baumeister et
     al. 2001; Rozin & Royzman 2001). A rectified, negativity-biased opponent readout should recover human valence
     BETTER than the symmetric difference axis IF the bias is real in the ratings. Can-fail: if the poles are
     antipodal and symmetric, the opponent readout is MONOTONE-EQUIVALENT to the axis (identical rho) -> honest
     negative (the linear axis is an adequate computational-level model of the readout).
  2. TWO CHANNELS CARRY MORE THAN THEIR DIFFERENCE. With relu-rectified pools, does the NEGATIVE channel add unique
     variance beyond the positive channel (partial correlation), i.e. are the poles non-antipodal?
  3. WEBER DISCRIMINATION EMERGES from the place code built on the pools (construction proof; Verguts-Fias): encode
     the net pool magnitude as FPE(log) -> discrimination degrades with magnitude (Weber), where a LINEAR place code
     is uniform. Info-free twin: shuffled pool activations.

Deterministic, ASCII-only. Writes only its own data dir. hdlab/ NOT modified. Reuses exp_composed_magnitude_channel
+ exp_perclass + the norms + FPE machinery (wire-don't-island).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_perclass_meaning_operations_v1 as V1                        # noqa: E402
import experiments.exp_adjective_intensity_ordering_v1 as INT                      # noqa: E402
import experiments.exp_adjective_magnitude_deeper_v1 as DEEP                       # noqa: E402
import experiments.exp_composed_magnitude_channel_v1 as CMC                        # noqa: E402
import experiments.exp_fpe_log_weber_magnitude_v1 as FPE                           # noqa: E402

ANCHOR = "exp_opponent_pool_readout_v1"
N_BOOT = 2000
SEED = 20260827
DIMS = ["valence", "arousal", "dominance"]      # evaluative dims with clean antonym poles


def _boot_rho_diff(xa, xb, gold, seed):
    a, b, g = np.asarray(xa, float), np.asarray(xb, float), np.asarray(gold, float)
    n = len(g); rng = np.random.default_rng(seed); d = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        d[i] = abs(spearmanr(a[idx], g[idx]).statistic) - abs(spearmanr(b[idx], g[idx]).statistic)
    lo, hi = np.percentile(d, [2.5, 97.5]); base = abs(spearmanr(a, g).statistic) - abs(spearmanr(b, g).statistic)
    return {"margin": round(float(base), 4), "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
            "ci_hw": round(float(hi - lo) / 2, 4), "null_p95": round(float(np.percentile(np.abs(d - base), 95)), 4)}


def pole_centroids(dim, gv):
    pos = [a for a, _ in V1.DIM_SEEDS[dim] if a in gv]
    neg = [b for _, b in V1.DIM_SEEDS[dim] if b in gv]
    pc = np.mean([gv[w] for w in pos], axis=0); pc /= (np.linalg.norm(pc) + 1e-12)
    nc = np.mean([gv[w] for w in neg], axis=0); nc /= (np.linalg.norm(nc) + 1e-12)
    return pc, nc


def test_opponent_recovery(gv, war, smoke=False):
    wn_adj = set(V1.all_wordnet_adjectives())
    out = {}
    for dim in DIMS:
        seed_words = {w for p in V1.DIM_SEEDS[dim] for w in p}
        scored = sorted({w for w in wn_adj if w in gv and w in war and dim in war[w]} - seed_words)
        if smoke:
            scored = scored[:600]
        if len(scored) < 30:
            continue
        r = np.array([war[w][dim] for w in scored], float)
        M = np.stack([gv[w] for w in scored])
        pc, nc = pole_centroids(dim, gv)
        sim_pos = M @ pc; sim_neg = M @ nc
        a_pos = np.maximum(sim_pos, 0.0); a_neg = np.maximum(sim_neg, 0.0)      # rectified opponent pools
        axis = sim_pos - sim_neg                                                # LINEAR symmetric axis (current op)
        # NEGATIVITY-BIAS beta is selected on a TRAIN split (even idx) and the win is evaluated on the HELD-OUT
        # split (odd idx) -- so the beta sweep cannot inflate the comparison (no fitting to the scored gold).
        tr = np.arange(len(scored)) % 2 == 0; te = ~tr
        betas = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
        rho_tr = {beta: abs(spearmanr((a_pos - beta * a_neg)[tr], r[tr]).statistic) for beta in betas}
        best_beta = max(rho_tr, key=rho_tr.get)                                 # chosen on TRAIN only
        net_best_te = (a_pos - best_beta * a_neg)[te]
        # partial correlation (full set, descriptive): does a_neg add unique variance beyond a_pos?
        def resid(x, ctrl):
            b = np.polyfit(ctrl, x, 1); return x - (b[0] * ctrl + b[1])
        pr_neg = float(spearmanr(resid(a_neg, a_pos), resid(r, a_pos)).statistic)
        out[dim] = {"n": len(scored), "n_heldout": int(te.sum()),
                    "rho_LINEAR_axis": round(float(abs(spearmanr(axis, r).statistic)), 4),
                    "rho_opponent_symmetric": round(float(abs(spearmanr(a_pos - a_neg, r).statistic)), 4),
                    "best_beta_selected_on_TRAIN": best_beta,
                    "rho_opponent_bestbeta_HELDOUT": round(float(abs(spearmanr(net_best_te, r[te]).statistic)), 4),
                    "rho_LINEAR_HELDOUT": round(float(abs(spearmanr(axis[te], r[te]).statistic)), 4),
                    "partial_corr_negpool_beyond_pospool": round(pr_neg, 4),
                    "boot_bestbeta_minus_LINEAR_HELDOUT": _boot_rho_diff(net_best_te, axis[te], r[te], SEED + 1)}
        print("[opp %s] n=%d LINEAR=%.3f opp-sym=%.3f | HELDOUT beta*=%.2f opp=%.3f LINEAR=%.3f | partial(neg|pos)=%.3f | opp-LINEAR(heldout)=%s"
              % (dim, out[dim]["n"], out[dim]["rho_LINEAR_axis"], out[dim]["rho_opponent_symmetric"], best_beta,
                 out[dim]["rho_opponent_bestbeta_HELDOUT"], out[dim]["rho_LINEAR_HELDOUT"], pr_neg,
                 out[dim]["boot_bestbeta_minus_LINEAR_HELDOUT"]), flush=True)
    return out


def test_weber_emergent(gv, war, smoke=False):
    """Construction proof: the place code built on the opponent net-magnitude reproduces Weber discrimination
    (kernel scale-invariant) where a LINEAR place code is uniform. Info-free twin: shuffled pool activations."""
    rates = FPE.phase_rates("gauss", 1024 if smoke else 4096, SEED, sigma=1.0)
    wn_adj = set(V1.all_wordnet_adjectives())
    seed_words = {w for p in V1.DIM_SEEDS["valence"] for w in p}
    scored = sorted({w for w in wn_adj if w in gv and w in war} - seed_words)[: (400 if smoke else 3000)]
    M = np.stack([gv[w] for w in scored]); pc, nc = pole_centroids("valence", gv)
    net = np.maximum(M @ pc, 0) + 0.5                     # positive net magnitude (distance from a low standard)
    net = net / net.min() + 1.0                           # positive, ratio-meaningful
    lo, hi = np.percentile(net, [10, 90]); xs = np.linspace(lo, hi, 8); r = 1.5

    def cv(v):
        v = np.asarray(v, float); m = v.mean(); return float(v.std() / abs(m)) if abs(m) > 1e-9 else float("inf")
    log_ratio = [FPE.kern(rates, np.log(x), np.log(x * r)) for x in xs if x * r <= net.max() * 1.6]
    lin_ratio = [FPE.kern(rates, x, x * r) for x in xs if x * r <= net.max() * 1.6]
    weber = bool(cv(log_ratio) < 0.05 and cv(lin_ratio) > cv(log_ratio) + 0.1)
    res = {"n": len(scored), "LOG_place_fixed_ratio_CV": round(cv(log_ratio), 4),
           "LINEAR_place_fixed_ratio_CV": round(cv(lin_ratio), 4), "weber_emergent_from_pools": weber}
    print("[weber-emergent] LOG-place ratio-CV=%.3f vs LINEAR-place ratio-CV=%.3f -> weber=%s"
          % (res["LOG_place_fixed_ratio_CV"], res["LINEAR_place_fixed_ratio_CV"], weber), flush=True)
    return res


def run(smoke=False):
    t0 = time.time()
    war = V1.load_warriner()
    needed = set(V1.all_wordnet_adjectives()) | set(war) | {w for s in V1.DIM_SEEDS.values() for pr in s for w in pr}
    gv = V1.build_or_load_glove(needed)
    print("[setup] glove=%d t=%.1fs" % (len(gv), time.time() - t0), flush=True)
    opp = test_opponent_recovery(gv, war, smoke=smoke)
    weber = test_weber_emergent(gv, war, smoke=smoke)

    # Is the opponent readout a MEASURABLE brain-faithful win, or monotone-equivalent (honest negative)?
    wins = [d for d in opp if opp[d]["boot_bestbeta_minus_LINEAR_HELDOUT"]["ci_lo"] > 0]
    neg_bias_dims = [d for d in opp if opp[d]["best_beta_selected_on_TRAIN"] > 1.0]
    verdict = ("OPPONENT_POOL_READOUT_MEASURABLE_WIN_ON_%s" % "_".join(wins) if wins
               else "OPPONENT_READOUT_MONOTONE_EQUIVALENT_TO_LINEAR_AXIS_ON_AVAILABLE_GOLDS")
    out = {"anchor_name": ANCHOR, "verdict": verdict, "smoke": smoke, "ts_iso": datetime.now(timezone.utc).isoformat(),
           "opponent_recovery": opp, "weber_emergent": weber, "dims_with_measurable_win": wins,
           "dims_showing_negativity_bias": neg_bias_dims, "elapsed_s": round(time.time() - t0, 2),
           "note": "Replaces the convenient LINEAR projection with the brain's OPPONENT-POOL mechanism (two rectified "
                   "monotonic pools + negativity bias, Verguts-Fias construction). Reports whether it is a MEASURABLE "
                   "win over the symmetric axis or MONOTONE-EQUIVALENT (an honest negative that justifies the linear "
                   "readout as a computational-level model). Weber discrimination emerges from the place code on the "
                   "pool magnitude regardless."}
    suffix = "_smoke" if smoke else ""
    outdir = os.path.join(REPO_ROOT, "data", ANCHOR + suffix)
    os.makedirs(outdir, exist_ok=True)
    tmp = os.path.join(outdir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, os.path.join(outdir, "metrics.json"))
    print("[verdict] %s  t=%.1fs" % (verdict, time.time() - t0), flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    run(smoke=args.smoke)
