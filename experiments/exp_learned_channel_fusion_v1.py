"""exp_learned_channel_fusion_v1 -- BAR #3: does the LEARNED dependency-typed channel NET-IMPROVE
the p1-updated meaning read-out (grounded feature spoke + WordNet-conceptual spoke)?

WHY (notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/
DESIGN_brain_analysis.md sec 8 + 10): BAR #1 already PASSED -- the dependency-typed distributional
learner (DEP_TYPED) beats the incumbent window baseline on the SIMILARITY axis (SimLex/SimVerb),
CI-separated, twins lose (exp_structured_context_learner_v1.py). But the p1-updated substrate
already has TWO supplied/supervised similarity spokes on that same axis: the grounded feature spoke
(hdlab.grounded_similarity.distinctive_grounded_similarity, sensorimotor+concreteness, whitened) and
the conceptual/definitional spoke (hdlab.conceptual_meaning.ConceptualChannel, WordNet-IDF). DEP_TYPED
is UNSUPERVISED (grown from reading); the other two are SUPERVISED (external norms / WordNet). The
open question this cell answers: does the learned channel add NON-REDUNDANT signal on top of what the
supplied spokes already carry, or is it redundant with (dominated by) WordNet conceptual structure?

ONE VARIABLE: which extra channel joins the (grounded + conceptual) fusion pool. Equal-weight
z-score fusion (the incumbent MeaningFusion pattern), reusing the baseline's PPMI+SVD math VERBATIM
for DEP_TYPED (no re-derivation of BAR #1).

ARMS (fuse = z-score each spoke over the SAME common-coverage pairs, then average):
  CONTROL    = fuse(GROUNDED, CONCEPTUAL)                  the supplied/supervised read-out (p1)
  TREATMENT  = fuse(GROUNDED, CONCEPTUAL, DEP_TYPED)        + the learned channel
  NOISE_CTL  = fuse(GROUNDED, CONCEPTUAL, RANDOM)           info-free channel -- must NOT beat CONTROL
  SHUF_CTL   = fuse(GROUNDED, CONCEPTUAL, DEP_LABELSHUF)    info-free structured twin -- must NOT beat CONTROL
Also scored ALONE for context: GROUNDED, CONCEPTUAL, DEP_TYPED, SELPREF.

GATE (paired-difference bootstrap Delta-rho on the SAME common pairs, reusing
exp_structured_context_learner_v1.paired_delta -- the correct, higher-power test for a matched-
population margin): TREATMENT beats CONTROL CI-separated (separated_above) on >=1 of {SimLex,
SimVerb} AND NOISE_CTL, SHUF_CTL do NOT beat CONTROL CI-separated on ANY benchmark.

Parse cache + DEP_TYPED/SELPREF/DEP_LABELSHUF construction, vocab build, PPMI/SVD math, and the
three human-rating benchmarks are ALL REUSED VERBATIM from exp_structured_context_learner_v1.py and
exp_learn_from_reading_strong_arm_v1.py (BAR #1's own baseline) -- no re-derivation. This cell only
ADDS the fusion machinery and the two substrate spokes. ASCII-only. Writes only to
data/exp_learned_channel_fusion_v1/. Does not modify hdlab/, data/foundation/, the baseline cell, or
exp_structured_context_learner_v1.py.
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

import numpy as np
from scipy.stats import spearmanr

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# REUSE VERBATIM: baseline PPMI+SVD math, scorer, benchmarks (BAR #1's own foundation)
from experiments.exp_learn_from_reading_strong_arm_v1 import (
    ppmi_matrix, svd_vectors, dense_vec_cosine_fn, random_vec_cosine_fn,
    build_vocab, benchmark_vocab, load_simlex, load_simverb, load_wordsim,
    score_arm, covered_pairs, build_cooc, PPMI_ALPHA, SVD_K, SVD_P,
)
# REUSE VERBATIM: the dependency-typed context builders + parse cache + paired-delta gate (BAR #1)
from experiments.exp_structured_context_learner_v1 import (
    load_parsed, token_sents, build_typed_cooc, build_selpref_cooc, build_labelshuffle_cooc,
    paired_delta, parse_and_cache, CACHE_DIR as STRUCT_CACHE_DIR,
)

# the p1-updated substrate spokes (grounded feature + conceptual/WordNet) -- READ-ONLY imports
from hdlab.grounded_similarity import distinctive_grounded_similarity
from hdlab.conceptual_meaning import ConceptualChannel

ANCHOR = "learned_channel_fusion_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR)
SEED = 13
VALID_POS = ("N", "V", "A")


# --------------------------------------------------------------------------- spoke sim_fns
def grounded_sim_fn():
    """GROUNDED spoke: whitened sensorimotor+concreteness cosine (None if either word OOV)."""
    def sim(w1, w2):
        return distinctive_grounded_similarity(w1, w2)
    return sim


def conceptual_sim_fn(bench_rows, ch):
    """CONCEPTUAL spoke for ONE benchmark: POS looked up per-pair from the benchmark's own rows
    (SimLex/SimVerb carry POS; WordSim rows carry 'NA' -> default 'N', per pre-reg)."""
    pos_of = {}
    for (w1, w2, _g, pos, _rel) in bench_rows:
        p = pos if pos in VALID_POS else "N"
        pos_of[(w1, w2)] = p

    def sim(w1, w2):
        pos = pos_of.get((w1, w2), "N")
        return ch.similarity(w1, pos, w2, pos)
    return sim


# --------------------------------------------------------------------------- fusion
def fuse(sim_fns, pairs):
    """Equal-weight z-score fusion (the incumbent MeaningFusion pattern): z-score each spoke's
    similarity over `pairs` ([(w1,w2), ...] -- the SAME common-coverage population every arm is
    scored on), then average the z-scores. Returns None for a query pair if ANY spoke returns None
    (keeps every arm restricted to genuinely-covered pairs; matches restrict_pairs=common at scoring
    time). z-score stats (mean/std) are fit on `pairs`, not on the query pair itself -- glass-box,
    no leakage beyond "this arm's fusion pool was calibrated on the population being scored", which
    is the same convention the baseline's own score_fusion() uses."""
    raws = []
    for fn in sim_fns:
        vals = np.array([fn(w1, w2) for (w1, w2) in pairs], dtype=np.float64)
        raws.append(vals)
    means = [float(np.nanmean(v)) if v.size else 0.0 for v in raws]
    stds = [float(np.nanstd(v)) or 1.0 for v in raws]

    def sim(w1, w2):
        zs = []
        for fn, mu, sd in zip(sim_fns, means, stds):
            s = fn(w1, w2)
            if s is None:
                return None
            zs.append((s - mu) / sd)
        return float(np.mean(zs))
    return sim


# --------------------------------------------------------------------------- reliability-weighted fusion
def split_half_by_parity(common_idx):
    """Split a set of row-indices into two halves by INDEX parity (A=even idx, B=odd idx). A = the
    reliability-estimation half; B = the fusion+scoring half. No pair is used for both roles."""
    idx_sorted = sorted(common_idx)
    half_a = [k for k in idx_sorted if k % 2 == 0]
    half_b = [k for k in idx_sorted if k % 2 == 1]
    return half_a, half_b


def spearman_reliability(fn, pairs, golds):
    """Brain-faithful cue reliability proxy: max(0, spearman rho of this spoke vs gold) on `pairs`
    (the held-out half A). Clipped at 0 -- an anti-correlated or non-informative spoke gets zero
    fusion weight, never negative weight. Mirrors reliability/precision-weighted cue integration
    (Ernst & Banks 2002) rather than the incumbent's naive equal-weight average."""
    vals, gs = [], []
    for (w1, w2), g in zip(pairs, golds):
        s = fn(w1, w2)
        if s is None:
            continue
        vals.append(s); gs.append(g)
    if len(vals) < 10:
        return 0.0
    r = spearmanr(vals, gs).correlation
    if r is None or np.isnan(r):
        return 0.0
    return max(0.0, float(r))


def rw_fuse(named_fns, weights, calib_pairs):
    """Reliability-weighted z-score fusion: sum_i w_i * zscore_i(over calib_pairs). `weights` are
    pre-estimated on the OTHER half (half A, via spearman_reliability) -- never on calib_pairs itself,
    so no leakage. z-score mean/std are fit on calib_pairs (the population being scored), matching the
    equal-weight fuse() convention above. named_fns: [(name, sim_fn), ...]; weights: {name: w}."""
    names = [nm for nm, _ in named_fns]
    fns = [fn for _, fn in named_fns]
    raws = [np.array([fn(w1, w2) for (w1, w2) in calib_pairs], dtype=np.float64) for fn in fns]
    means = [float(np.nanmean(v)) if v.size else 0.0 for v in raws]
    stds = [float(np.nanstd(v)) or 1.0 for v in raws]
    ws = [weights[nm] for nm in names]

    def sim(w1, w2):
        total = 0.0
        for fn, mu, sd, w in zip(fns, means, stds, ws):
            s = fn(w1, w2)
            if s is None:
                return None
            total += w * ((s - mu) / sd)
        return float(total)
    return sim


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--tokens", type=int, default=None, help="override token budget")
    args = ap.parse_args()

    if args.mode == "smoke":
        max_tokens = args.tokens or 150_000
        vocab_cap, min_count, n_boot, n_null = 15_000, 3, 200, 200
    else:
        max_tokens = args.tokens or 15_000_000
        vocab_cap, min_count, n_boot, n_null = 60_000, 8, 500, 500

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cache_path = os.path.join(STRUCT_CACHE_DIR, "parsed_simplewiki_%dtok.jsonl" % max_tokens)
    rng = np.random.default_rng(SEED)

    t0 = time.time()
    parse_and_cache(max_tokens, cache_path)   # cache-HIT for the caches this run reuses (150k/15M)
    parsed, ntok = load_parsed(cache_path, max_tokens)
    print("[load] %d sentences / %d tokens (%.0fs)" % (len(parsed), ntok, time.time() - t0), flush=True)

    benches = {"simlex": load_simlex(), "simverb": load_simverb(), "wordsim": load_wordsim()}
    force = set().union(*(benchmark_vocab(r) for r in benches.values()))
    toks = token_sents(parsed)
    index = build_vocab(toks, force, vocab_cap, min_count)
    print("[vocab] %d words (cap=%d min_count=%d)" % (len(index), vocab_cap, min_count), flush=True)

    def svd_of(M):
        return dense_vec_cosine_fn(svd_vectors(ppmi_matrix(M), seed=SEED), index)

    print("[build] DEP_TYPED / SELPREF / DEP_LABELSHUF context matrices...", flush=True)
    tb = time.time()
    dep_typed_M, n_typed = build_typed_cooc(parsed, index, typed=True)
    selpref_M, n_sp = build_selpref_cooc(parsed, index)
    labelshuf_M, n_shuf = build_labelshuffle_cooc(parsed, index, np.random.default_rng(SEED + 3))
    print("[build] cols: typed=%d selpref=%d labelshuf=%d (%.0fs)"
          % (n_typed, n_sp, n_shuf, time.time() - tb), flush=True)

    print("[build] SVD vectors...", flush=True)
    ts = time.time()
    DEP_TYPED_fn = svd_of(dep_typed_M)
    SELPREF_fn = svd_of(selpref_M)
    DEP_LABELSHUF_fn = svd_of(labelshuf_M)
    RANDOM_fn = random_vec_cosine_fn(index, seed=SEED)
    GROUNDED_fn = grounded_sim_fn()
    ch = ConceptualChannel()
    print("[build] SVD done (%.0fs)" % (time.time() - ts), flush=True)

    # READING-CHANNEL UPGRADE (part B): WINDOW spoke = PPMI-SVD over the incumbent +/-2 window,
    # built VERBATIM the same way as exp_structured_context_learner_v1's WIN2 arm (reuse build_cooc).
    # This is the OTHER learned/reading-based spoke -- lets us ask whether upgrading the reader's own
    # context shape (window -> dependency) improves the reading-based read-out, with no supervised
    # confound (WINDOW and DEP_TYPED are BOTH unsupervised).
    print("[build] WINDOW (+/-2) context matrix (reading-channel baseline)...", flush=True)
    tw = time.time()
    window_M = build_cooc(toks, index, 2)
    WINDOW_fn = svd_of(window_M)
    print("[build] WINDOW done (%.0fs)" % (time.time() - tw), flush=True)

    metrics_benches = {}
    verdict_bits = {}

    for bn, rows in benches.items():
        tbn = time.time()
        CONCEPTUAL_fn = conceptual_sim_fn(rows, ch)

        core = {"GROUNDED": GROUNDED_fn, "CONCEPTUAL": CONCEPTUAL_fn,
                "DEP_TYPED": DEP_TYPED_fn, "RANDOM": RANDOM_fn, "DEP_LABELSHUF": DEP_LABELSHUF_fn}
        common = None
        for fn in core.values():
            cov = covered_pairs(rows, fn)
            common = cov if common is None else (common & cov)
        common = common or set()
        pairs_list = [(rows[k][0], rows[k][1]) for k in sorted(common)]
        n_common = len(common)
        print("[%s] n_common=%d (intersection of GROUNDED/CONCEPTUAL/DEP_TYPED/RANDOM/DEP_LABELSHUF)"
              % (bn, n_common), flush=True)

        arms = {
            "CONTROL": fuse([GROUNDED_fn, CONCEPTUAL_fn], pairs_list),
            "TREATMENT": fuse([GROUNDED_fn, CONCEPTUAL_fn, DEP_TYPED_fn], pairs_list),
            "NOISE_CTL": fuse([GROUNDED_fn, CONCEPTUAL_fn, RANDOM_fn], pairs_list),
            "SHUF_CTL": fuse([GROUNDED_fn, CONCEPTUAL_fn, DEP_LABELSHUF_fn], pairs_list),
        }
        arm_scores = {nm: score_arm(rows, fn, restrict_pairs=common, n_boot=n_boot, n_null=n_null, seed=SEED)
                      for nm, fn in arms.items()}

        spoke_fns = {"GROUNDED": GROUNDED_fn, "CONCEPTUAL": CONCEPTUAL_fn,
                     "DEP_TYPED": DEP_TYPED_fn, "SELPREF": SELPREF_fn}
        spoke_scores = {nm: {"own": score_arm(rows, fn, restrict_pairs=None, n_boot=n_boot, n_null=n_null, seed=SEED),
                              "common": score_arm(rows, fn, restrict_pairs=common, n_boot=n_boot, n_null=n_null, seed=SEED)}
                         for nm, fn in spoke_fns.items()}

        d_treat = paired_delta(rows, common, arms["TREATMENT"], arms["CONTROL"], n_boot, SEED + 42)
        d_noise = paired_delta(rows, common, arms["NOISE_CTL"], arms["CONTROL"], n_boot, SEED + 42)
        d_shuf = paired_delta(rows, common, arms["SHUF_CTL"], arms["CONTROL"], n_boot, SEED + 42)

        signal_added = bool(d_treat and d_treat["separated_above"])
        noise_clean = not bool(d_noise and d_noise["separated_above"])
        shuf_clean = not bool(d_shuf and d_shuf["separated_above"])

        # ---- (A) RELIABILITY-WEIGHTED FUSION (brain-faithful combiner). Split common pairs by INDEX
        # parity: half A estimates each spoke's reliability (clipped spearman rho vs gold), half B is
        # fused + scored using those pre-estimated weights -- no leakage, weights fixed before B is used.
        half_a_idx, half_b_idx = split_half_by_parity(common)
        pairs_a = [(rows[k][0], rows[k][1]) for k in half_a_idx]
        golds_a = [rows[k][2] for k in half_a_idx]
        pairs_b = [(rows[k][0], rows[k][1]) for k in half_b_idx]
        common_b = set(half_b_idx)

        rel = {
            "GROUNDED": spearman_reliability(GROUNDED_fn, pairs_a, golds_a),
            "CONCEPTUAL": spearman_reliability(CONCEPTUAL_fn, pairs_a, golds_a),
            "DEP_TYPED": spearman_reliability(DEP_TYPED_fn, pairs_a, golds_a),
            "RANDOM": spearman_reliability(RANDOM_fn, pairs_a, golds_a),
        }
        RW_CONTROL_fn = rw_fuse([("GROUNDED", GROUNDED_fn), ("CONCEPTUAL", CONCEPTUAL_fn)], rel, pairs_b)
        RW_TREATMENT_fn = rw_fuse([("GROUNDED", GROUNDED_fn), ("CONCEPTUAL", CONCEPTUAL_fn),
                                    ("DEP_TYPED", DEP_TYPED_fn)], rel, pairs_b)
        RW_NOISE_fn = rw_fuse([("GROUNDED", GROUNDED_fn), ("CONCEPTUAL", CONCEPTUAL_fn),
                                ("RANDOM", RANDOM_fn)], rel, pairs_b)
        rw_arm_scores = {
            "RW_CONTROL": score_arm(rows, RW_CONTROL_fn, restrict_pairs=common_b, n_boot=n_boot, n_null=n_null, seed=SEED),
            "RW_TREATMENT": score_arm(rows, RW_TREATMENT_fn, restrict_pairs=common_b, n_boot=n_boot, n_null=n_null, seed=SEED),
            "RW_NOISE": score_arm(rows, RW_NOISE_fn, restrict_pairs=common_b, n_boot=n_boot, n_null=n_null, seed=SEED),
        }
        d_rw_treat = paired_delta(rows, common_b, RW_TREATMENT_fn, RW_CONTROL_fn, n_boot, SEED + 42)
        d_rw_noise = paired_delta(rows, common_b, RW_NOISE_fn, RW_CONTROL_fn, n_boot, SEED + 42)
        rw_signal_added = bool(d_rw_treat and d_rw_treat["separated_above"])
        rw_noise_clean = not bool(d_rw_noise and d_rw_noise["separated_above"])

        def _rr(nm):
            r = rw_arm_scores[nm]["rho"]
            return "%.4f" % r if r is not None else "NA"
        print("[%s][RW] weights(half-A rho+)=%s | n_halfB=%d | RW_CONTROL=%s RW_TREATMENT=%s RW_NOISE=%s"
              % (bn, {k: round(v, 4) for k, v in rel.items()}, len(common_b),
                 _rr("RW_CONTROL"), _rr("RW_TREATMENT"), _rr("RW_NOISE")), flush=True)
        print("[%s][RW] paired RW_TREATMENT-RW_CONTROL=%s | RW_NOISE-RW_CONTROL=%s | signal_added=%s noise_clean=%s"
              % (bn, d_rw_treat, d_rw_noise, rw_signal_added, rw_noise_clean), flush=True)

        # ---- (B) READING-CHANNEL UPGRADE: WINDOW vs DEP_TYPED as the reading-learned spoke, fused
        # with GROUNDED only (no CONCEPTUAL -- isolates the reading channel's own contribution, no
        # supervised WordNet confound). Compared both equal-weight and reliability-weighted. ----
        core_wd = {"GROUNDED": GROUNDED_fn, "WINDOW": WINDOW_fn, "DEP_TYPED": DEP_TYPED_fn}
        common_wd = None
        for fn in core_wd.values():
            cov = covered_pairs(rows, fn)
            common_wd = cov if common_wd is None else (common_wd & cov)
        common_wd = common_wd or set()
        pairs_wd = [(rows[k][0], rows[k][1]) for k in sorted(common_wd)]

        FUSE_WINDOW_eq = fuse([GROUNDED_fn, WINDOW_fn], pairs_wd)
        FUSE_DEP_eq = fuse([GROUNDED_fn, DEP_TYPED_fn], pairs_wd)
        eq_scores = {
            "FUSE_WINDOW_eq": score_arm(rows, FUSE_WINDOW_eq, restrict_pairs=common_wd, n_boot=n_boot, n_null=n_null, seed=SEED),
            "FUSE_DEP_eq": score_arm(rows, FUSE_DEP_eq, restrict_pairs=common_wd, n_boot=n_boot, n_null=n_null, seed=SEED),
        }
        d_eq = paired_delta(rows, common_wd, FUSE_DEP_eq, FUSE_WINDOW_eq, n_boot, SEED + 42)

        half_a_wd, half_b_wd = split_half_by_parity(common_wd)
        pairs_a_wd = [(rows[k][0], rows[k][1]) for k in half_a_wd]
        golds_a_wd = [rows[k][2] for k in half_a_wd]
        pairs_b_wd = [(rows[k][0], rows[k][1]) for k in half_b_wd]
        common_b_wd = set(half_b_wd)
        rel_wd = {
            "GROUNDED": spearman_reliability(GROUNDED_fn, pairs_a_wd, golds_a_wd),
            "WINDOW": spearman_reliability(WINDOW_fn, pairs_a_wd, golds_a_wd),
            "DEP_TYPED": spearman_reliability(DEP_TYPED_fn, pairs_a_wd, golds_a_wd),
        }
        RW_WINDOW_fn = rw_fuse([("GROUNDED", GROUNDED_fn), ("WINDOW", WINDOW_fn)], rel_wd, pairs_b_wd)
        RW_DEP_fn = rw_fuse([("GROUNDED", GROUNDED_fn), ("DEP_TYPED", DEP_TYPED_fn)], rel_wd, pairs_b_wd)
        rw_scores_wd = {
            "RW_WINDOW": score_arm(rows, RW_WINDOW_fn, restrict_pairs=common_b_wd, n_boot=n_boot, n_null=n_null, seed=SEED),
            "RW_DEP": score_arm(rows, RW_DEP_fn, restrict_pairs=common_b_wd, n_boot=n_boot, n_null=n_null, seed=SEED),
        }
        d_rw_wd = paired_delta(rows, common_b_wd, RW_DEP_fn, RW_WINDOW_fn, n_boot, SEED + 42)

        def _re(nm):
            r = eq_scores[nm]["rho"]
            return "%.4f" % r if r is not None else "NA"
        def _rwd(nm):
            r = rw_scores_wd[nm]["rho"]
            return "%.4f" % r if r is not None else "NA"
        print("[%s][READ] n_common_wd=%d eq: WINDOW=%s DEP=%s delta(DEP-WINDOW)=%s"
              % (bn, len(common_wd), _re("FUSE_WINDOW_eq"), _re("FUSE_DEP_eq"), d_eq), flush=True)
        print("[%s][READ] n_halfB_wd=%d rw(weights=%s): RW_WINDOW=%s RW_DEP=%s delta(RW_DEP-RW_WINDOW)=%s"
              % (bn, len(common_b_wd), {k: round(v, 4) for k, v in rel_wd.items()},
                 _rwd("RW_WINDOW"), _rwd("RW_DEP"), d_rw_wd), flush=True)

        # ---- (C) COVERAGE / UNSUPERVISED VALUE: does DEP_TYPED add signal where WordNet (CONCEPTUAL)
        # is SILENT -- the population a supervised WordNet spoke cannot help on AT ALL. ----
        all_idx = set(range(len(rows)))
        conceptual_covered = covered_pairs(rows, CONCEPTUAL_fn)
        conceptual_missing = all_idx - conceptual_covered
        missing_core = {"DEP_TYPED": DEP_TYPED_fn, "RANDOM": RANDOM_fn, "GROUNDED": GROUNDED_fn}
        missing_common = conceptual_missing
        for fn in missing_core.values():
            missing_common = missing_common & covered_pairs(rows, fn)
        dep_missing_score = score_arm(rows, DEP_TYPED_fn, restrict_pairs=missing_common, n_boot=n_boot, n_null=n_null, seed=SEED)
        d_dep_vs_random_missing = paired_delta(rows, missing_common, DEP_TYPED_fn, RANDOM_fn, n_boot, SEED + 42)
        d_dep_vs_grounded_missing = paired_delta(rows, missing_common, DEP_TYPED_fn, GROUNDED_fn, n_boot, SEED + 42)
        print("[%s][COVERAGE] n_total=%d conceptual_covered=%d conceptual_missing=%d | on MISSING (n_common=%d): "
              "DEP_TYPED_rho=%s delta(DEP-RANDOM)=%s delta(DEP-GROUNDED)=%s"
              % (bn, len(rows), len(conceptual_covered), len(conceptual_missing), len(missing_common),
                 "%.4f" % dep_missing_score["rho"] if dep_missing_score["rho"] is not None else "NA",
                 d_dep_vs_random_missing, d_dep_vs_grounded_missing), flush=True)

        metrics_benches[bn] = {
            "n_common": n_common, "arms": arm_scores, "spokes": spoke_scores,
            "paired_deltas": {"TREATMENT_minus_CONTROL": d_treat, "NOISE_CTL_minus_CONTROL": d_noise,
                              "SHUF_CTL_minus_CONTROL": d_shuf},
            "rw_fusion": {
                "n_halfA": len(half_a_idx), "n_halfB": len(common_b), "reliability_weights_halfA": rel,
                "arms": rw_arm_scores,
                "paired_deltas": {"RW_TREATMENT_minus_RW_CONTROL": d_rw_treat,
                                  "RW_NOISE_minus_RW_CONTROL": d_rw_noise},
                "signal_added": rw_signal_added, "noise_clean": rw_noise_clean,
            },
            "reading_upgrade": {
                "n_common_wd": len(common_wd), "eq_arms": eq_scores,
                "eq_paired_delta_DEP_minus_WINDOW": d_eq,
                "n_halfB_wd": len(common_b_wd), "rw_reliability_weights_halfA": rel_wd,
                "rw_arms": rw_scores_wd, "rw_paired_delta_RWDEP_minus_RWWINDOW": d_rw_wd,
            },
            "coverage_value": {
                "n_total": len(rows), "n_conceptual_covered": len(conceptual_covered),
                "n_conceptual_missing": len(conceptual_missing), "n_missing_common": len(missing_common),
                "DEP_TYPED_rho_on_missing": dep_missing_score,
                "paired_delta_DEP_minus_RANDOM_on_missing": d_dep_vs_random_missing,
                "paired_delta_DEP_minus_GROUNDED_on_missing": d_dep_vs_grounded_missing,
            },
        }
        verdict_bits[bn] = {"signal_added": signal_added, "noise_clean": noise_clean, "shuf_clean": shuf_clean}

        def _rho(nm):
            r = arm_scores[nm]["rho"]
            return "%.4f" % r if r is not None else "NA"
        print("[%s] CONTROL=%s TREATMENT=%s NOISE_CTL=%s SHUF_CTL=%s | spokes: GROUNDED=%s CONCEPTUAL=%s DEP_TYPED=%s SELPREF(own)=%s"
              % (bn, _rho("CONTROL"), _rho("TREATMENT"), _rho("NOISE_CTL"), _rho("SHUF_CTL"),
                 "%.4f" % spoke_scores["GROUNDED"]["common"]["rho"] if spoke_scores["GROUNDED"]["common"]["rho"] is not None else "NA",
                 "%.4f" % spoke_scores["CONCEPTUAL"]["common"]["rho"] if spoke_scores["CONCEPTUAL"]["common"]["rho"] is not None else "NA",
                 "%.4f" % spoke_scores["DEP_TYPED"]["common"]["rho"] if spoke_scores["DEP_TYPED"]["common"]["rho"] is not None else "NA",
                 "%.4f" % spoke_scores["SELPREF"]["own"]["rho"] if spoke_scores["SELPREF"]["own"]["rho"] is not None else "NA"),
              flush=True)
        print("[%s] paired TREATMENT-CONTROL=%s | NOISE_CTL-CONTROL=%s | SHUF_CTL-CONTROL=%s | signal_added=%s noise_clean=%s shuf_clean=%s (%.0fs)"
              % (bn, d_treat, d_noise, d_shuf, signal_added, noise_clean, shuf_clean, time.time() - tbn), flush=True)

    similarity_pass = bool(verdict_bits.get("simlex", {}).get("signal_added") or
                            verdict_bits.get("simverb", {}).get("signal_added"))
    controls_clean_all = all(vb["noise_clean"] and vb["shuf_clean"] for vb in verdict_bits.values())
    if similarity_pass and controls_clean_all:
        verdict = "LEARNED_CHANNEL_NET_IMPROVES_CISEP_TWINS_CLEAN"
    elif similarity_pass and not controls_clean_all:
        verdict = "SIGNAL_PRESENT_BUT_CONTROL_CONTAMINATED_SEE_PAIRED_DELTAS"
    else:
        verdict = "LEARNED_CHANNEL_DOES_NOT_NET_IMPROVE_CISEP__SEE_PAIRED_DELTAS"

    metrics = {
        "anchor_name": ANCHOR, "mode": args.mode, "n_tokens": ntok, "vocab": len(index),
        "context_cols": {"typed": n_typed, "selpref": n_sp, "labelshuf": n_shuf},
        "config": {"ppmi_alpha": PPMI_ALPHA, "svd_k": SVD_K, "svd_p": SVD_P,
                   "vocab_cap": vocab_cap, "min_count": min_count, "n_boot": n_boot, "n_null": n_null,
                   "seed": SEED},
        "benches": metrics_benches, "verdict_bits": verdict_bits, "verdict": verdict,
        "similarity_pass": similarity_pass, "controls_clean_all": controls_clean_all,
        "elapsed_s": round(time.time() - t0, 1),
    }
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[verdict] %s | similarity_pass=%s controls_clean_all=%s | %.0fs"
          % (verdict, similarity_pass, controls_clean_all, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
