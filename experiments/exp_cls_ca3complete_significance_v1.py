"""
exp_cls_ca3complete_significance_v1 -- firm the CA3-completion sub-claim to a real verdict.

CONTEXT. The parent cell exp_cls_ca3complete_consolidation_v1 (commit 92e01cf3f) landed the CLS
consolidation MAIN claim (integrate-new-without-forgetting) as CHAIN_GRADE at 3 seeds [7,17,23].
Its CA3-completion SUB-CLAIM (does the CA3 pattern-completion step during replay measurably lift
OLD-item retention over the SAME loop WITHOUT the completion step) came in MM_TENTATIVE: the lift
(CONSOLIDATE_FULL old_retention - CONSOLIDATE_NO_CLEANUP old_retention) was real-but-small,
per-seed {0.08, 0.04, 0.04}, mean ~0.053, directionally consistent 3/3, but did NOT clean-clear
significance at n=3 (sign-test p=0.125; paired-t t~4.0 df=2 p~0.06). Recorded revival criterion:
rerun at >=5 seeds to establish (or refute) significance before any CG claim on CA3-completion.

THIS CELL does exactly that: re-runs the IDENTICAL consolidation loop (same regime, same arms, same
old/new item sets, same discrete fixed budget, same CA3 params) at 8 seeds [7,17,23,29,31,37,41,43]
-- the original 3 are INCLUDED so the run composes/reproduces them -- and makes the PRIMARY metric
the CA3-completion lift and its CROSS-SEED SIGNIFICANCE (sign-test + paired-t) at the larger n.
The MAIN claim (parent cell + its metrics.json) is NOT touched; this ONLY firms the CA3 sub-claim.

PRIMARY DISCRIMINATOR (this cell): the paired lift d_i = FULL_old_i - NO_CLEANUP_old_i and whether
it is (a) positive and (b) significant at n=8.
  HARD_PASS  (sub-claim promotes toward CG-eligible): mean(d) > 0 AND paired-t two-sided p < 0.05
             AND sign-test two-sided p < 0.05.
  HARD_FAIL  (sub-claim refuted): mean(d) <= 0 -- the CA3 completion provides no lift (or hurts).
  MIDDLE_BAND(sub-claim = small MM refinement): mean(d) > 0 but NOT both tests clear p<0.05
             (directionally consistent but marginal/non-significant; NO_CLEANUP already retains
             ~0.88 so CA3 is a marginal refinement, not load-bearing).
Either outcome is a clean result. See preregs/2026-07-08_cls_ca3complete_significance_v1.md.

CONTRACT. assert_discriminator_fires (NAIVE catastrophic-forgetting positive control must STILL fire
= the store CAN learn recent items, so its ~0.02 OLD-retention is a genuine forgetting readout, not a
dead store). Telemetry-sensitivity self-test. Pausable/restartable per-seed checkpoint. Atomic metric
writes (tmp+os.replace). except SystemExit: raise BEFORE except Exception (no BaseException).
numpy-only + scipy.stats for the two pre-declared significance tests. CPU-only. ASCII-only.

Compute: recency-decayed matrix recurrence is inherently sequential (F_t depends on F_{t-1});
~2.6s/seed at D=1024,T=600 measured (parent FULL 3 seeds = 7.8s) -> 8 seeds ~ 21s. sequential-CPU
justified (per-seed wall << 10s; no GPU benefit; matmuls are tiny D x D). Storage: no_composition
(single-hop argmax readout of an associative matrix; not a chained-retrieval store).
"""
from __future__ import annotations
import sys, os, argparse, time, json, platform, traceback, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List
import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    assert_discriminator_fires, record_gate,
)
from hdlab.iterative_attractor import iterative_cleanup

ANCHOR_NAME = "cls_ca3complete_significance_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ---- CA3 completion parameters (brain-canonical alpha=0.5 perforant-path re-injection) ----
# IDENTICAL to parent cell exp_cls_ca3complete_consolidation_v1 (do not drift).
CA3_TEMP = 4.0
CA3_MAX_STEPS = 6
CA3_ALPHA = 0.5

# ---- regime (IDENTICAL to parent; smoke == full-scale params, discriminator-survives-scale opt A) ----
D = 1024
T_STREAM = 600      # total stream items
N_EPOCH = 12        # consolidation phases
DECAY = 0.94        # fast-buffer recency decay (early items decay out -> genuine forgetting)
V = 64              # clean concept codebook size
BUDGET_B = 50       # fixed per-phase consolidation budget
CUE_RHO = 0.70      # partial replay cue: cue = rho*key + sqrt(1-rho^2)*random (SWR partial reactivation)

# >=5 seed requirement: 8 seeds, original 3 [7,17,23] INCLUDED so the run composes/reproduces them.
FULL_SEEDS = [7, 17, 23, 29, 31, 37, 41, 43]
# Smoke exercises the FULL significance pipeline at the ORIGINAL 3 seeds (reproduces MM_TENTATIVE
# state at n=3 -> MIDDLE_BAND expected) at IDENTICAL full-scale params. ~8s local, discriminating.
SMOKE_SEEDS = [7, 17, 23]
SEEDS = FULL_SEEDS if RUN_MODE == "full" else SMOKE_SEEDS
EXPECTED_N_UNITS = len(SEEDS)

# ---- pre-reg bands (this cell's discriminator = the paired CA3-completion lift significance) ----
ALPHA_SIG = 0.05             # significance threshold (two-sided) for both tests
# consolidation-regime sanity floors (IDENTICAL to parent; the sub-claim test is meaningless if the
# main consolidation loop itself broke). Reported in detail; a broken regime -> CONTEXT_INVALID.
HP_OLD_FLOOR = 0.80          # CONSOLIDATE_FULL must still retain OLD
NAIVE_FORGET_CEIL = 0.55     # NAIVE must still forget OLD (interference exercised)

ARMS = ["NAIVE_NO_CONSOLIDATION", "CONSOLIDATE_FULL", "CONSOLIDATE_NO_CLEANUP"]

CONFIG_VERSION = (
    "ANCHOR=%s, D=%d T=%d E=%d DECAY=%.2f V=%d BUDGET_B=%d CUE_RHO=%.2f "
    "ca3_temp=%.1f ca3_alpha=%.2f ca3_steps=%d n_seeds=%d seeds=%s mode=%s alpha_sig=%.2f"
) % (ANCHOR_NAME, D, T_STREAM, N_EPOCH, DECAY, V, BUDGET_B, CUE_RHO, CA3_TEMP, CA3_ALPHA,
     CA3_MAX_STEPS, len(SEEDS), SEEDS, RUN_MODE, ALPHA_SIG)


def _l2n(X, eps=1e-12):
    if X.ndim == 1:
        return (X / (np.linalg.norm(X) + eps)).astype(np.float32)
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)).astype(np.float32)


def _build_stream(seed, d, t_stream, v):
    g = np.random.default_rng(seed)
    VB = _l2n(g.standard_normal((v, d)).astype(np.float32))        # (V, d) clean concept attractors
    K = _l2n(g.standard_normal((t_stream, d)).astype(np.float32))  # (T, d) per-item keys
    val = g.integers(0, v, size=t_stream)                          # concept per item
    return g, VB, K, val


def _readout_acc(store, keys, val_idx, VB):
    """Single-step argmax readout (identical across arms). Returns top-1 accuracy."""
    R = keys.astype(np.float32) @ store.T
    pred = np.argmax(R @ VB.T, axis=1)
    return float(np.mean(pred == val_idx))


def _ca3_complete(vecs, VB):
    out = iterative_cleanup(vecs.astype(np.float32), VB, temp=CA3_TEMP,
                            max_steps=CA3_MAX_STEPS, alpha=CA3_ALPHA)
    return out["state"].astype(np.float32)


def _partial_cue(keys, rng, rho):
    """SWR partial reactivation: cue = rho*key + sqrt(1-rho^2)*random_unit (renormalized)."""
    rnd = _l2n(rng.standard_normal(keys.shape).astype(np.float32))
    return _l2n(rho * keys + math.sqrt(max(1e-6, 1.0 - rho * rho)) * rnd)


def _stream_and_consolidate(seed, d, t_stream, n_epoch, decay, v, budget_b, cue_rho):
    """IDENTICAL loop to parent cell: stream through fast buffer; discrete offline consolidation
    phase per epoch for two slow stores (CA3-cleaned and raw)."""
    g, VB, K, val = _build_stream(seed, d, t_stream, v)
    rng_replay = np.random.default_rng(seed * 7919 + 5)
    ipe = t_stream // n_epoch
    old_idx = np.arange(0, ipe)                    # epoch 0 = OLD
    rec_idx = np.arange(t_stream - ipe, t_stream)  # last epoch = RECENT
    F = np.zeros((d, d), dtype=np.float32)
    S_full = np.zeros((d, d), dtype=np.float32)
    S_nc = np.zeros((d, d), dtype=np.float32)
    per_cycle_counts = []
    for e in range(n_epoch):
        lo, hi = e * ipe, (e + 1) * ipe
        for t in range(lo, hi):                    # WAKE: sequential recency-decayed writes to FAST
            F = decay * F + np.outer(VB[val[t]], K[t]).astype(np.float32)
        idx = np.arange(lo, hi)[:budget_b]         # OFFLINE discrete fixed-budget replay of this epoch
        per_cycle_counts.append(len(idx))
        cue = _partial_cue(K[idx], rng_replay, cue_rho)
        r = cue @ F.T                              # noisy FAST readout of the (partial-cued) items
        cleaned = _ca3_complete(r, VB)             # CA3 pattern completion -> clean concept
        S_full += cleaned.T @ K[idx]               # write CLEAN value to the retained (true) key
        raw = _l2n(r)
        S_nc += raw.T @ K[idx]                      # ablation: write RAW noisy readout (no completion)
    return VB, K, val, F, S_full, S_nc, old_idx, rec_idx, per_cycle_counts


def _arms_must_differ(arm_store):
    digests = {}
    for name, W in arm_store.items():
        digests[name] = hashlib.sha256(np.ascontiguousarray(W).tobytes()).hexdigest()
    names = list(digests)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            assert digests[names[a]] != digests[names[b]], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (names[a], names[b]))
    return digests


def run_unit(seed, d=D, t_stream=T_STREAM, n_epoch=N_EPOCH, decay=DECAY, v=V,
             budget_b=BUDGET_B, cue_rho=CUE_RHO):
    VB, K, val, F, S_full, S_nc, old_idx, rec_idx, cyc = _stream_and_consolidate(
        seed, d, t_stream, n_epoch, decay, v, budget_b, cue_rho)

    naive_old = _readout_acc(F, K[old_idx], val[old_idx], VB)
    naive_new = _readout_acc(F, K[rec_idx], val[rec_idx], VB)
    full_old = _readout_acc(S_full, K[old_idx], val[old_idx], VB)
    full_new = _readout_acc(S_full, K[rec_idx], val[rec_idx], VB)
    nc_old = _readout_acc(S_nc, K[old_idx], val[old_idx], VB)
    nc_new = _readout_acc(S_nc, K[rec_idx], val[rec_idx], VB)

    digests = _arms_must_differ({"NAIVE_NO_CONSOLIDATION": F, "CONSOLIDATE_FULL": S_full,
                                 "CONSOLIDATE_NO_CLEANUP": S_nc})
    budget_respected = all(c <= budget_b for c in cyc)

    per_arm = {
        "NAIVE_NO_CONSOLIDATION": {"old_retention": round(naive_old, 4), "new_acquisition": round(naive_new, 4)},
        "CONSOLIDATE_FULL": {"old_retention": round(full_old, 4), "new_acquisition": round(full_new, 4)},
        "CONSOLIDATE_NO_CLEANUP": {"old_retention": round(nc_old, 4), "new_acquisition": round(nc_new, 4)},
    }
    # primary per-seed metric: the CA3-completion lift (paired within-seed).
    ca3_lift = round(full_old - nc_old, 4)
    return {
        "seed": seed, "per_arm": per_arm,
        "ca3_lift_full_minus_nocleanup_old": ca3_lift,
        "budget_respected": bool(budget_respected),
        "n_consolidate_phases": len(cyc), "per_cycle_counts": cyc,
        "arm_digests": digests,
        "D": d, "T": t_stream, "E": n_epoch, "V": v, "DECAY": decay, "CUE_RHO": cue_rho,
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
    }


def _paired_significance(full_old_list, nc_old_list):
    """The two PRE-DECLARED tests on the paired lift d_i = FULL_old_i - NO_CLEANUP_old_i.

    - paired-t (two-sided): scipy.stats.ttest_rel on the paired arrays.
    - sign-test (two-sided binomial): count of positive lifts among non-tied pairs vs Binom(n,0.5).
    Zero-variance edge cases handled explicitly (a deterministic nonzero lift is perfectly
    significant; a deterministic zero lift is not significant).
    """
    fo = np.asarray(full_old_list, dtype=np.float64)
    nc = np.asarray(nc_old_list, dtype=np.float64)
    d = fo - nc
    n = int(len(d))
    mean_lift = float(np.mean(d)) if n > 0 else 0.0
    std_lift = float(np.std(d, ddof=1)) if n > 1 else 0.0

    # paired t-test (two-sided)
    if n < 2:
        t_stat, p_t = 0.0, 1.0
    elif std_lift == 0.0:
        if mean_lift == 0.0:
            t_stat, p_t = 0.0, 1.0            # deterministic zero lift -> no effect
        else:
            t_stat = float("inf") if mean_lift > 0 else float("-inf")
            p_t = 0.0                          # deterministic nonzero lift -> perfectly significant
    else:
        res = stats.ttest_rel(fo, nc)
        t_stat, p_t = float(res.statistic), float(res.pvalue)

    # sign test (two-sided binomial), ties excluded
    n_pos = int(np.sum(d > 0))
    n_neg = int(np.sum(d < 0))
    n_nz = n_pos + n_neg
    if n_nz == 0:
        p_sign = 1.0
    else:
        p_sign = float(stats.binomtest(n_pos, n_nz, 0.5, alternative="two-sided").pvalue)

    return {
        "per_seed_lift": [float(x) for x in d],
        "mean_lift": round(mean_lift, 5),
        "std_lift": round(std_lift, 5),
        "sem_lift": round(std_lift / math.sqrt(n), 5) if n > 0 else 0.0,
        "n": n,
        "paired_t_stat": (round(t_stat, 4) if math.isfinite(t_stat) else t_stat),
        "paired_t_p_two_sided": round(p_t, 6),
        "sign_n_pos": n_pos, "sign_n_neg": n_neg, "sign_n_nonzero": n_nz,
        "sign_test_p_two_sided": round(p_sign, 6),
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {}, [])
    if len(units) < EXPECTED_N_UNITS:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "cardinality breach: got %d units, expected %d" % (len(units), EXPECTED_N_UNITS), {}, [])

    def col(arm, key):
        return [u["per_arm"][arm][key] for u in units]

    full_old_l = col("CONSOLIDATE_FULL", "old_retention")
    nc_old_l = col("CONSOLIDATE_NO_CLEANUP", "old_retention")
    naive_old_l = col("NAIVE_NO_CONSOLIDATION", "old_retention")

    def m(x):
        return float(np.mean(x))

    full_old, nc_old, naive_old = m(full_old_l), m(nc_old_l), m(naive_old_l)
    full_new = m(col("CONSOLIDATE_FULL", "new_acquisition"))
    naive_new = m(col("NAIVE_NO_CONSOLIDATION", "new_acquisition"))
    nc_new = m(col("CONSOLIDATE_NO_CLEANUP", "new_acquisition"))

    sig = _paired_significance(full_old_l, nc_old_l)
    mean_lift = sig["mean_lift"]
    p_t = sig["paired_t_p_two_sided"]
    p_sign = sig["sign_test_p_two_sided"]
    budget_ok = all(u["budget_respected"] for u in units)

    # regime-sanity: the sub-claim test is only meaningful if the consolidation loop itself behaved
    # (NAIVE forgets OLD, CONSOLIDATE_FULL retains OLD) -- guards a silently-drifted regime.
    regime_sane = (naive_old <= NAIVE_FORGET_CEIL) and (full_old >= HP_OLD_FLOOR)

    detail = {
        "PRIMARY_ca3_completion_lift": sig,
        "CONSOLIDATE_FULL": {"old_retention": round(full_old, 4), "new_acquisition": round(full_new, 4)},
        "CONSOLIDATE_NO_CLEANUP": {"old_retention": round(nc_old, 4), "new_acquisition": round(nc_new, 4)},
        "NAIVE_NO_CONSOLIDATION": {"old_retention": round(naive_old, 4), "new_acquisition": round(naive_new, 4)},
        "regime_sane": bool(regime_sane),
        "regime_sane_detail": "naive_old=%.4f<=%.2f AND full_old=%.4f>=%.2f" % (
            naive_old, NAIVE_FORGET_CEIL, full_old, HP_OLD_FLOOR),
        "budget_respected": bool(budget_ok),
        "n_seeds": len(units), "seeds": [u["seed"] for u in units],
        "alpha_sig": ALPHA_SIG, "CONFIG_VERSION": CONFIG_VERSION,
        "note": ("PARENT MAIN claim (exp_cls_ca3complete_consolidation_v1) UNTOUCHED; this cell firms "
                 "ONLY the CA3-completion sub-claim via cross-seed significance of the paired lift."),
        "cites": [
            "exp_cls_ca3complete_consolidation_v1 (commit 92e01cf3f; parent MAIN claim CHAIN_GRADE, 3 seeds)",
            "notes/research_hippocampal_biology_consolidation_loop_brain_first_2026-07-08.md (RANK 1 CA3 completion)",
            "hdlab.iterative_attractor.iterative_cleanup (certified CA3-completion primitive)",
        ],
    }

    gate_claims = [
        record_gate("mean_lift_positive", mean_lift, 0.0, ">",
                    note="CA3-completion lift FULL_old - NO_CLEANUP_old, paired mean across %d seeds" % len(units)),
        record_gate("paired_t_significant", p_t, ALPHA_SIG, "<",
                    note="paired-t two-sided p on the within-seed lift"),
        record_gate("sign_test_significant", p_sign, ALPHA_SIG, "<",
                    note="sign-test two-sided binomial p (%d/%d positive)" % (sig["sign_n_pos"], sig["sign_n_nonzero"])),
        record_gate("regime_sane", 1.0 if regime_sane else 0.0, 1.0, "==",
                    note="consolidation loop behaved (NAIVE forgets, FULL retains) at this run"),
    ]

    summary = ("CA3-lift mean=%.4f (per-seed=%s) | paired-t t=%s p=%.4f | sign-test %d/%d p=%.4f | "
               "n=%d | FULL_old=%.3f NO_CLEANUP_old=%.3f NAIVE_old=%.3f | regime_sane=%s budget_ok=%s") % (
               mean_lift, ["%.3f" % x for x in sig["per_seed_lift"]], str(sig["paired_t_stat"]), p_t,
               sig["sign_n_pos"], sig["sign_n_nonzero"], p_sign, len(units),
               full_old, nc_old, naive_old, regime_sane, budget_ok)

    if not regime_sane:
        return ("MIDDLE_BAND",
                "CONTEXT_INVALID (MIDDLE_BAND): consolidation regime did not behave (NAIVE_old=%.3f, FULL_old=%.3f) "
                "-- the CA3-lift sub-claim test is not interpretable at a broken regime. " % (naive_old, full_old)
                + summary, detail, gate_claims)

    if mean_lift <= 0.0:
        return ("HARD_FAIL",
                "HARD_FAIL: CA3-completion sub-claim REFUTED -- mean lift=%.4f <= 0 at n=%d (the CA3 pattern-completion "
                "step provides no OLD-retention benefit over raw-readout replay). " % (mean_lift, len(units))
                + summary, detail, gate_claims)

    if p_t < ALPHA_SIG and p_sign < ALPHA_SIG:
        return ("HARD_PASS",
                "HARD_PASS: CA3-completion sub-claim FIRMED -- lift stays positive (mean=%.4f) AND clears significance "
                "at n=%d (paired-t p=%.4f < %.2f AND sign-test p=%.4f < %.2f). CA3 pattern-completion during "
                "consolidation-replay measurably lifts OLD-item retention; promotes toward CG-eligible. " % (
                    mean_lift, len(units), p_t, ALPHA_SIG, p_sign, ALPHA_SIG) + summary, detail, gate_claims)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: CA3-completion is a small MM refinement -- lift positive (mean=%.4f) but NOT both tests clear "
            "p<%.2f at n=%d (paired-t p=%.4f, sign-test p=%.4f). NO_CLEANUP already retains ~%.2f so CA3 is marginal, "
            "not load-bearing. " % (mean_lift, ALPHA_SIG, len(units), p_t, p_sign, nc_old) + summary, detail, gate_claims)


# -------------------- defensive error-checking (canonical exp_dev.md sec 13) --------------------
def _write_start_marker(output_dir, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp"); final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# -------------------- self-test (mechanism + telemetry + CA3-denoise + significance-fns + discriminator-fires) --------------------
def _selftest():
    # (1) fast reduced-regime mechanism check (must still forget for the discriminator gate).
    d, t, e, dec, v, bud, rho = 384, 240, 8, 0.90, 48, 30, 0.70
    u = run_unit(7, d=d, t_stream=t, n_epoch=e, decay=dec, v=v, budget_b=bud, cue_rho=rho)
    assert set(u["per_arm"].keys()) == set(ARMS), "arm set mismatch"

    # (2) SIGNIFICANCE FUNCTIONS unit-tested against known values (the primary discriminator machinery).
    # 8/8 positive, near-constant lift -> sign p = 2*0.5^8 = 0.0078125; paired-t p tiny.
    s8 = _paired_significance([0.96, 0.92, 0.92, 0.94, 0.90, 0.94, 0.92, 0.90], [0.88] * 8)
    assert s8["sign_n_pos"] == 8 and s8["sign_n_nonzero"] == 8, "sig: sign count"
    assert abs(s8["sign_test_p_two_sided"] - (2.0 * 0.5 ** 8)) < 1e-6, "sig: sign p=%.6f" % s8["sign_test_p_two_sided"]
    assert s8["paired_t_p_two_sided"] < 0.05 and s8["mean_lift"] > 0, "sig: 8-seed should clear"
    # n=3 original {0.08,0.04,0.04} reproduces MM_TENTATIVE: sign p=0.25, paired-t p~0.057 (NOT <0.05).
    s3 = _paired_significance([0.96, 0.92, 0.92], [0.88, 0.88, 0.88])
    assert s3["sign_test_p_two_sided"] > 0.05, "sig: n=3 sign should NOT clear (%.4f)" % s3["sign_test_p_two_sided"]
    assert s3["paired_t_p_two_sided"] > 0.05, "sig: n=3 paired-t should NOT clear (%.4f)" % s3["paired_t_p_two_sided"]
    # cross-check paired-t against scipy ttest_rel independently (no drift).
    xt = stats.ttest_rel(np.array([0.96, 0.92, 0.92]), np.array([0.88, 0.88, 0.88]))
    assert abs(s3["paired_t_p_two_sided"] - float(xt.pvalue)) < 1e-6, "sig: ttest_rel drift"
    # reversed lift -> HARD_FAIL side (mean<=0).
    sneg = _paired_significance([0.80, 0.82], [0.88, 0.90])
    assert sneg["mean_lift"] < 0, "sig: negative lift detect"
    # zero-variance nonzero lift -> perfectly significant.
    szv = _paired_significance([0.93, 0.93, 0.93, 0.93], [0.88, 0.88, 0.88, 0.88])
    assert szv["paired_t_p_two_sided"] == 0.0 and szv["mean_lift"] > 0, "sig: zero-var nonzero lift"

    # (3) verdict pipeline end-to-end at reduced-regime 3-seed smoke (proves compute_verdict + gates).
    units = [run_unit(sd, d=d, t_stream=t, n_epoch=e, decay=dec, v=v, budget_b=bud, cue_rho=rho)
             for sd in SMOKE_SEEDS]
    # temporarily assert cardinality against the smoke set (EXPECTED_N_UNITS is smoke=3 under --self-test).
    vv, msg, det, claims = compute_verdict(units)
    assert vv in ("HARD_PASS", "MIDDLE_BAND", "HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"), "verdict %s" % vv
    assert "PRIMARY_ca3_completion_lift" in det, "detail missing primary metric"
    assert len(claims) == 4, "expected 4 structured gate claims"

    # (4) TELEMETRY-SENSITIVITY: the metric reads store state, is NOT analytically pinned.
    g, VB, K, val = _build_stream(7, d, t, v)
    S = (VB[val[:60]].T @ K[:60]).astype(np.float32)
    acc_full = _readout_acc(S, K[:60], val[:60], VB)
    acc_zero = _readout_acc(np.zeros_like(S), K[:60], val[:60], VB)
    acc_corrupt = _readout_acc(S + 5.0 * g.standard_normal(S.shape).astype(np.float32), K[:60], val[:60], VB)
    assert acc_full > 0.7, "T-tel: clean store should retain, got %.3f" % acc_full
    assert acc_zero < acc_full - 0.3, "T-tel: zeroed store must drop, got %.3f" % acc_zero
    assert acc_corrupt < acc_full - 0.1, "T-tel: corrupted store must drop, got %.3f" % acc_corrupt

    # (5) CA3 completion denoises a partial-cued noisy readout (positive-control at test regime, Gate D).
    F = np.zeros((d, d), dtype=np.float32)
    for tt in range(60):
        F = dec * F + np.outer(VB[val[tt]], K[tt]).astype(np.float32)
    idx = np.arange(50, 60)
    cue = _partial_cue(K[idx], np.random.default_rng(1), rho)
    r = cue @ F.T
    cleaned = _ca3_complete(r, VB)
    tgt = VB[val[idx]]
    cos_raw = float(np.mean(np.sum(_l2n(r) * tgt, axis=1)))
    cos_cln = float(np.mean(np.sum(_l2n(cleaned) * tgt, axis=1)))
    assert cos_cln > cos_raw, "T-ca3: completion did not denoise (raw=%.3f cleaned=%.3f)" % (cos_raw, cos_cln)

    # (6) budget respected.
    assert u["budget_respected"], "budget not respected"

    pa = u["per_arm"]
    print("[selftest] reduced-regime arms: naive_old=%.3f naive_new=%.3f full_old=%.3f nc_old=%.3f lift=%.3f"
          % (pa["NAIVE_NO_CONSOLIDATION"]["old_retention"], pa["NAIVE_NO_CONSOLIDATION"]["new_acquisition"],
             pa["CONSOLIDATE_FULL"]["old_retention"], pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"],
             u["ca3_lift_full_minus_nocleanup_old"]), flush=True)

    # (7) DISCRIMINATOR-FIRES (contract): NAIVE catastrophic-forgetting control MUST forget OLD at smoke,
    # AND the store must be able to learn (NAIVE new_acquisition high) -> the ~0.02 OLD is genuine forgetting.
    assert pa["NAIVE_NO_CONSOLIDATION"]["new_acquisition"] > 0.70, (
        "discriminator: store must LEARN recent items (naive_new=%.3f) so low naive_old is genuine forgetting"
        % pa["NAIVE_NO_CONSOLIDATION"]["new_acquisition"])
    assert_discriminator_fires(
        pa["NAIVE_NO_CONSOLIDATION"]["old_retention"] >= HP_OLD_FLOOR,
        control_name="NAIVE_NO_CONSOLIDATION", headline_name="old_retention>=%.2f" % HP_OLD_FLOOR,
        run_mode="smoke", extra="no-consolidation control must forget OLD (store learns recent, forgets old).")
    print("[selftest] PASS: mechanism + significance-fns + verdict-pipeline + telemetry + CA3-denoise + "
          "budget + discriminator-fires (store-learns-yet-forgets-old)", flush=True)


def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, EXPECTED_N_UNITS)
    print("[config] %s" % CONFIG_VERSION, flush=True)
    t0 = time.time()
    run_cfg = {"run_mode": RUN_MODE, "N": D, "anchor": ANCHOR_NAME}
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        r = run_unit(seed)
        pa = r["per_arm"]
        print("  [seed=%d] naive old=%.3f new=%.3f | full old=%.3f new=%.3f | nc old=%.3f new=%.3f | ca3_lift=%.3f"
              % (seed, pa["NAIVE_NO_CONSOLIDATION"]["old_retention"], pa["NAIVE_NO_CONSOLIDATION"]["new_acquisition"],
                 pa["CONSOLIDATE_FULL"]["old_retention"], pa["CONSOLIDATE_FULL"]["new_acquisition"],
                 pa["CONSOLIDATE_NO_CLEANUP"]["old_retention"], pa["CONSOLIDATE_NO_CLEANUP"]["new_acquisition"],
                 r["ca3_lift_full_minus_nocleanup_old"]), flush=True)
        write_partial_key(out_dir, key, r)
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail, gate_claims = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
        "D": D, "T": T_STREAM, "E": N_EPOCH, "V": V, "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": (len(units) == EXPECTED_N_UNITS),
        "detail": detail, "per_unit": units,
        "metrics_source": "measured_cpu_cls_ca3complete_significance_v1",
        "elapsed_s": time.time() - t0, "summary": msg,
        "substrate_only_decode_gate": "TRUE (HD substrate-native store + cleanup; no encoder)",
        "config_version": CONFIG_VERSION,
    }
    write_metrics(out_dir, metrics, units, gate_claims=gate_claims)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    _out = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out, e)
        raise
