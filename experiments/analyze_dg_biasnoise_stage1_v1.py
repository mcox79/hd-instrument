"""STAGE-1 bias-vs-noise co-failure concentration check on the DG_XFIT self-grounding negative.

The 5x negative-drill (notes/research_dg_selfgrounding_5x_remaining_internal_angles_2026-07-09.md)
closes four internal-revival angles and rests its exogenous-required conclusion on ONE testable claim:
the residual corr(failmask)=0.377 measured by exp_selfplay_dg_pattern_separation_xfit_v1 is a shared-BIAS
signature (the SAME referents recur as hard across independent training seeds), not a NOISE/VARIANCE
signature (which referents fail reshuffles randomly seed-to-seed). If NOISE, an internal
variance-reduction fix (bagging/replay) might still work and the exogenous pivot is premature; if BIAS,
exogenous ground-truth is the only known lever -> proceed to B1+EXOG.

WHY A RE-RUN (not a pure read of metrics.json): the landed FULL metrics.json persists only per-(seed,arm)
AGGREGATE rates + a mask sha256 DIGEST -- NOT the per-referent speaker_correct/listener_correct boolean
arrays the concentration/Jaccard check needs. The eval set is DETERMINISTIC (built from
SUBGRAPH_BASE_SEED+999, independent of the training seed), so the SAME referents are scored in every seed;
re-running the DG_XFIT arm at the EXACT FULL config regenerates the per-referent masks faithfully to the
0.377 result. This script re-runs DG_XFIT ONLY (not B0/B1) for the 5 FULL seeds.

METHOD (per the drill's "cheap decisive test", Stage 1):
  co_fail[seed][r] = (speaker wrong AND listener wrong) on referent r  (the joint co-failure event)
  co_fail_rate[r] = mean over seeds of co_fail[seed][r]
  CONCENTRATION: rank referents by co_fail_rate; ratio = mean(top-decile co_fail_rate) / population-avg,
    with a PERMUTATION NULL (shuffle co-failure within each seed, preserving per-seed count) giving the
    z-score of the observed ratio above the noise floor.
  CROSS-SEED CO-FAILURE CORRELATION: mean pairwise phi-correlation of the co-failure indicator across
    seeds -- the DIRECT analog of the program's own failmask_corr, but across independent training seeds.
    Under NOISE the same-referent co-failures are independent -> ~0; under BIAS the same referents recur
    -> positive. This is the PRIMARY instrument (no discrete-tie / set-size artifact).
  Also reports the both-wrong co-failure-SET Jaccard (interpretable) and a per-seed top-decile-set Jaccard
    (DIAGNOSTIC ONLY -- inflated-noise artifact: per-seed hardness is discrete 0/1/2 so "top decile" is
    decided by random tie-break among the many co-failers; do NOT gate on it).

BANDS (principled, mirroring the program's independence bar; the drill's fixed Jaccard=0.40/0.15 numbers
  were mis-specified for the discrete-ties reality, so the valid phi-corr instrument replaces them):
  BIAS  (confirms exogenous is correctly aimed): concentration ratio z >= 3.0 AND cross-seed cofail corr >= 0.15
  NOISE (would reopen an internal angle):        concentration ratio z <  1.0 OR  cross-seed cofail corr <  0.05
  AMBIGUOUS: anything between.

ASCII-only. No emojis. No em dashes. Reuses DG cell functions VERBATIM (no re-implementation of the game).
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402
from experiments.exp_selfplay_dg_pattern_separation_xfit_v1 import (  # noqa: E402
    SUBGRAPH_BASE_SEED, FULL_CFG, SMOKE_CFG,
    build_dg_features, train_arm, eval_masks, neighborhood_augment, build_candidate_sets,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    load_cn_subgraph, char_trigram_features, build_adjlist,
)

ANCHOR_NAME = "analyze_dg_biasnoise_stage1_v1"

# Bands (principled; phi-corr replaces the drill's tie-fragile Jaccard number)
CONC_Z_BIAS = 3.0        # observed concentration ratio must be >=3 SD above the permutation noise null
CONC_Z_NOISE = 1.0
COFAIL_CORR_BIAS = 0.15  # cross-seed co-failure phi-corr (analog of the program's independence bar ~0.20)
COFAIL_CORR_NOISE = 0.05
TOP_DECILE = 0.10
N_PERM = 400             # permutation-null replicates for the concentration-ratio z-score


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _pairwise_mean_jaccard(sets):
    """Mean Jaccard over all unordered pairs of index-sets."""
    vals = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            a, b = sets[i], sets[j]
            u = len(a | b)
            vals.append((len(a & b) / u) if u > 0 else 0.0)
    return float(np.mean(vals)) if vals else float("nan")


def _mean_pairwise_phi(mat):
    """Mean pairwise Pearson (phi for 0/1) correlation across rows of mat [n_seeds, n_items].
    Degenerate rows (constant) contribute 0 (no information)."""
    n = mat.shape[0]
    vals = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = mat[i], mat[j]
            if a.std() < 1e-9 or b.std() < 1e-9:
                vals.append(0.0)
            else:
                vals.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(vals)) if vals else float("nan")


def _concentration_ratio(co_fail_mat, k_dec):
    """top-decile mean cross-seed co-failure rate / population-average rate."""
    rate = co_fail_mat.mean(axis=0)
    pop = float(rate.mean())
    top = float(np.sort(rate)[::-1][:k_dec].mean())
    return (top / pop) if pop > 1e-12 else float("nan"), top, pop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=["full", "smoke"], default="full",
                    help="full = faithful to the 0.377 landed result (default); smoke = fast proxy")
    args, _ = ap.parse_known_args()
    cfg = FULL_CFG if args.config == "full" else SMOKE_CFG
    t0 = time.perf_counter()
    out_dir = get_output_dir(ANCHOR_NAME)          # Path (write_metrics needs Path)
    out_dir_s = str(out_dir)

    _log("loading ConceptNet subgraph (target n_nodes=%d, config=%s)..." % (cfg["n_nodes"], args.config))
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    Xn = neighborhood_augment(X, adj, cfg["neighbor_weight"])
    _log("subgraph: %s" % meta)

    # Deterministic eval set -- IDENTICAL construction to the DG cell main() (matches the landed run).
    eval_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 999)
    has_nb = np.nonzero(np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool))[0]
    n_eval = int(min(cfg["n_eval"], has_nb.shape[0]))
    eval_idx = np.sort(eval_rng.choice(has_nb, size=n_eval, replace=False))
    cand_idx = build_candidate_sets(eval_idx, n_nodes, cfg["n_dist"], eval_rng)
    _log("eval referents=%d candidate_set_size=%d" % (n_eval, 1 + cfg["n_dist"]))

    seeds = cfg["seeds"]
    co_fail = np.zeros((len(seeds), n_eval), dtype=np.float64)   # both-wrong indicator per (seed, referent)
    n_wrong = np.zeros((len(seeds), n_eval), dtype=np.float64)   # halves-wrong count (0/1/2) per (seed, ref)
    per_seed_diag = []
    for si, seed in enumerate(seeds):
        _log("DG_XFIT re-run seed=%d ..." % seed)
        Xn_dg, X_dg, dg_diag = build_dg_features(X, Xn, cfg, seed)
        enc_s, enc_l, chan = train_arm("DG_XFIT", cfg, X_dg, Xn_dg, adj, seed, n_nodes, out_dir_s, tag="DG_XFIT")
        ev = eval_masks(enc_s, enc_l, chan, Xn_dg, X_dg, eval_idx, cand_idx, cfg["K"])
        sc = ev["speaker_correct"].astype(bool)
        lc = ev["listener_correct"].astype(bool)
        cf = (~sc) & (~lc)
        co_fail[si] = cf.astype(np.float64)
        n_wrong[si] = (~sc).astype(np.float64) + (~lc).astype(np.float64)
        per_seed_diag.append(dict(seed=int(seed), grounding_acc=float(ev["grounding_acc"]),
                                  speaker_fail_rate=float((~sc).mean()),
                                  listener_fail_rate=float((~lc).mean()),
                                  cofail_rate=float(cf.mean())))
        _log("  seed=%d cofail_rate=%.4f ground=%.3f spk_fail=%.3f lis_fail=%.3f" % (
            seed, cf.mean(), ev["grounding_acc"], (~sc).mean(), (~lc).mean()))

    # ---- CONCENTRATION (observed) + permutation null z-score ----
    k_dec = max(1, int(round(TOP_DECILE * n_eval)))
    conc_ratio, top_decile_rate, pop_avg = _concentration_ratio(co_fail, k_dec)
    perm_rng = np.random.default_rng(20260709)
    counts = co_fail.sum(axis=1).astype(int)                     # per-seed co-failure count (preserved)
    null_ratios = np.empty(N_PERM, dtype=np.float64)
    for p in range(N_PERM):
        shuf = np.zeros_like(co_fail)
        for si in range(len(seeds)):
            idx = perm_rng.choice(n_eval, size=counts[si], replace=False)
            shuf[si, idx] = 1.0
        null_ratios[p], _, _ = _concentration_ratio(shuf, k_dec)
    null_mu = float(np.nanmean(null_ratios))
    null_sd = float(np.nanstd(null_ratios))
    conc_z = float((conc_ratio - null_mu) / null_sd) if null_sd > 1e-9 else float("nan")

    # ---- PRIMARY: cross-seed co-failure phi-correlation (analog of failmask_corr, across seeds) ----
    cross_seed_cofail_corr = _mean_pairwise_phi(co_fail)

    # ---- secondary/diagnostic Jaccards ----
    jac_rng = np.random.default_rng(424242)
    top_sets, cofail_sets = [], []
    for si in range(len(seeds)):
        tie = jac_rng.random(n_eval) * 1e-6
        top_sets.append(set(np.argsort(-(n_wrong[si] + tie))[:k_dec].tolist()))
        cofail_sets.append(set(np.nonzero(co_fail[si] > 0.5)[0].tolist()))
    jaccard_topdecile_diag = _pairwise_mean_jaccard(top_sets)    # tie-inflated: DIAGNOSTIC ONLY
    jaccard_cofailset = _pairwise_mean_jaccard(cofail_sets)

    # ---- verdict ----
    is_bias = (conc_z >= CONC_Z_BIAS) and (cross_seed_cofail_corr >= COFAIL_CORR_BIAS)
    is_noise = (conc_z < CONC_Z_NOISE) or (cross_seed_cofail_corr < COFAIL_CORR_NOISE)
    if is_bias:
        verdict = "BIAS_CONFIRMED_EXOGENOUS_CORRECTLY_AIMED"
    elif is_noise:
        verdict = "NOISE_INTERNAL_ANGLE_REOPENS"
    else:
        verdict = "AMBIGUOUS_MIDDLE"

    verdict_msg = (
        "%s | config=%s seeds=%s n_eval=%d | cross-seed cofail phi-corr=%.3f | concentration ratio=%.3f "
        "(z=%.2f vs null %.3f+-%.3f; top-decile rate=%.4f pop-avg=%.4f) | Jaccard cofail-set=%.3f "
        "topdecile(diag)=%.3f | bands: BIAS(z>=%.1f AND corr>=%.2f) NOISE(z<%.1f OR corr<%.2f)" % (
            verdict, args.config, seeds, n_eval, cross_seed_cofail_corr, conc_ratio, conc_z,
            null_mu, null_sd, top_decile_rate, pop_avg, jaccard_cofailset, jaccard_topdecile_diag,
            CONC_Z_BIAS, COFAIL_CORR_BIAS, CONC_Z_NOISE, COFAIL_CORR_NOISE))
    _log("VERDICT: %s" % verdict_msg)

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=args.config, elapsed_s=time.perf_counter() - t0,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        seeds=list(seeds), n_eval=int(n_eval),
        cross_seed_cofail_corr=cross_seed_cofail_corr,
        concentration_ratio=conc_ratio, concentration_z=conc_z,
        null_ratio_mean=null_mu, null_ratio_std=null_sd, n_perm=N_PERM,
        top_decile_cofail_rate=top_decile_rate, population_avg_cofail_rate=pop_avg,
        jaccard_cofailset=jaccard_cofailset, jaccard_topdecile_diag=jaccard_topdecile_diag,
        bands=dict(CONC_Z_BIAS=CONC_Z_BIAS, CONC_Z_NOISE=CONC_Z_NOISE,
                   COFAIL_CORR_BIAS=COFAIL_CORR_BIAS, COFAIL_CORR_NOISE=COFAIL_CORR_NOISE,
                   TOP_DECILE=TOP_DECILE),
        per_seed=per_seed_diag, subgraph_meta=meta,
    )
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("done (%.1fs) -> %s/metrics.json" % (time.perf_counter() - t0, out_dir_s))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    main()
