"""grounding_selfplay_fair_test_difficulty_partial_v1 -- FAIR-TEST of the self-play failmask-correlation
~0.38 "wall": is it a REAL residual substrate coupling, or a BROKEN MEASUREMENT forced by shared per-item
difficulty (the grounding analog of the reader multihop fair-test that just dissolved barrier #1)?

FINDING (grounding fairness audit, off-disk): failmask_corr conflates intrinsic shared-item-difficulty with
mechanism-coupling. Analytically, for two binary fail masks whose per-item fail probability is a shared
intrinsic difficulty d_i, phi(fail_s, fail_l) ~= Var_i(d_i)/[p(1-p)] -- a floor forced by items DIFFERING in
intrinsic difficulty, INVARIANT to any encoder/anchor/active mechanism. Two decisive tells (MEASURED, prior
cells) put the substrate AT this shared-difficulty floor: A1_wide (8x channel capacity) RAISES corr
0.386->0.509 (a real bottleneck would DROP); A5_cap1 (zero channel info) drives corr->0.012 while grounding
-> chance (correlation carried BY the shared signal, not a residual coupling). Cross-fit already removed the
shared-ENCODER coupling (mirror 0.79 -> crossfit 0.38, separate encoders / disjoint folds), so the residual
0.38 is the shared-TASK floor -- a representation-invariant difficulty artifact -- OR a genuine coupling.
THIS CELL decides between those two by CONTROLLING difficulty.

THE FAIR TEST (fair scorings on an ENSEMBLE of independent B1_crossfit self-plays):
  1. TASK-DIFFICULTY-CONTROLLED corr (PRIMARY; attenuation-free): the residual after removing TASK-LEVEL
     shared item difficulty via a CROSS-MODEL co-failure decomposition. Two competences from DIFFERENT
     independent models can only co-fail via an item's INTRINSIC, mechanism-invariant difficulty (the exact
     analog of partialling the reader's intrinsic branching-factor k_sr). So:
       within(raw)   = mean_m phi(fail_s^m, fail_l^m)           (the within-model failmask correlation ~0.38)
       task_floor    = mean_{a!=b} phi(fail_s^a, fail_l^b)      (task-level shared item difficulty)
       residual      = within - task_floor                      (difficulty-CONTROLLED coupling)
     A per-model leave-model-out LINEAR partial correlation is ALSO reported (SECONDARY) but is attenuation-
     prone at the single-model binary level (a noisy per-item difficulty estimate under-removes) -- the
     cross-model floor is the honest, apples-to-apples control.
  2. WITHIN-DIFFICULTY-BIN corr (SECONDARY): bin items by ensemble difficulty d_i quantile, report the pooled
     within-bin corr (residualize on bin one-hot = demean within bin) + per-bin phi -- removes the between-bin
     difficulty variance that inflates the raw phi. Must AGREE with the primary residual for a hard verdict.
  3. DETERMINACY-FRACTION (DIAGNOSTIC): fraction of eval items whose target is UNIQUELY feature-separable from
     its distractors (no distractor collides with the target in trigram space above tau) -- the analog of the
     reader's unique-successor fraction. If most items are NOT uniquely separable, the task is underdetermined.
     A structural target-vs-distractor trigram-collision difficulty proxy is also reported (SECONDARY control).

POSITIVE CONTROL (real-data must-fire; SATURATION-VACUOUS discipline): a MIRROR arm (tied encoder, both halves
share the SAME representation) has a GENUINE coupling beyond difficulty (raw ~0.77-0.79). Its partial corr MUST
STAY high after difficulty-partialling. If the partialling procedure ALSO nukes the mirror, the estimator is
over-removing (broken) and every reading is void. This proves the partialling removes shared difficulty WITHOUT
destroying a known genuine coupling.

PRE-REGISTERED BANDS (BOTH; LOCKED PROSPECTIVE; primary = cross-model task-difficulty residual):
  HARD_PASS_FAIRNESS_ARTIFACT: CROSSFIT residual <= 0.15 AND within_bin_corr <= 0.15 (BOTH collapse toward
    ~0; the task-difficulty floor accounts for the raw) WHILE within(raw) reproduces ~0.38 (in [0.28,0.50]) AND
    the MIRROR positive control STAYS (residual_mirror >= 0.40, raw_mirror >= raw_crossfit + 0.20). => the
    grounding "wall" is a BROKEN MEASUREMENT (task-level shared item difficulty); the whole self-play arc is a
    fairness artifact; the substrate is fine.
  HARD_FAIL_REAL_BOUND: CROSSFIT residual >= 0.25 AND within_bin_corr >= 0.25 (BOTH stay materially >0 after
    controlling task difficulty), MIRROR control valid. => 0.38 is a GENUINE residual coupling that survives
    task-difficulty control (mechanism-specific, not reproducible across independent models); grounding HFs STAND.
  MIDDLE_BAND_PARTIAL_COLLAPSE: partial movement -- one measure collapses but not the other, or values land in
    (0.15, 0.25). => partial artifact; sweep before concluding.
  Void states: ANCHOR_NOT_REPRODUCED_VOID (raw_crossfit out of [0.28,0.50]); DIFFICULTY_DEGENERATE_VOID
    (Var(d_i) ~ 0 or too few varying bins -> partialling vacuous); MIRROR_CONTROL_FAILED_VOID (mirror partial
    does not stay high -> estimator over-removes / screen cannot preserve a real coupling); BASELINE_OUT_OF_BAND
    (crossfit fail rates outside 0.05..0.95); MACHINERY_SELFTEST_FAILED (partial-corr estimator not telemetry-
    sensitive).

SELF-TEST (controlled cases where the answer is KNOWN; machinery must-fire; ALWAYS runs): (case 1) inject PURE
shared-difficulty with CONDITIONALLY-INDEPENDENT failures (fail_s, fail_l ~ Bernoulli(d_true) independent given
a shared d_true; difficulty estimated from a matched-noise synthetic ensemble sized to FULL's leave-model-out
size E=7) -> raw corr > 0 but partial AND within-bin corr MUST land in the collapse band (<=COLLAPSE_MAX=0.15;
the finite-ensemble attenuation floor sits below this). (case 2) inject a REAL coupling beyond difficulty
(fail_l == fail_s on half the items) -> partial AND within-bin corr MUST land in the stays band
(>=REAL_MIN=0.25), and case-2 MUST exceed case-1 by >=0.15 (clean separation). This proves the pre-registered
bands sit on the correct sides of the estimator's behavior; if it cannot distinguish these two known cases,
the cell is void.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (AF): every ensemble/mirror model's (spk,lis) mask-pair hashed; all
#   must differ (distinct seeds -> distinct masks). Bit-identical => train/eval build bug.
# - final_metrics_atomicity: tmp_replace (write_metrics -> os.replace; crash-diag atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb_n/a: the discriminator is a partial CORRELATION vs a within-cell MIRROR must-stay control + a two-case
#   synthetic self-test, not a closed-form noise floor. Reachability by construction: case-1 synthetic collapses
#   to ~0 and mirror stays >=0.40 at the same ensemble size; the [<=0.15 collapse] / [>=0.25 stays] bands sit
#   strictly inside; a two-case self-test proves the partial-corr estimator is telemetry-sensitive.
# - baseline_in_band (AG): CROSSFIT speaker_fail + listener_fail rates must be in 0.05..0.95 at smoke.
# - discriminator survives scale: smoke = FULL branches at smaller n_nodes/epochs/K/ensemble, SAME cross-fit +
#   mirror machinery + SAME difficulty-partial + within-bin estimators. SMOKE must show: raw_crossfit in band,
#   difficulty non-degenerate, mirror control valid, self-test passes, masks differ. The COLLAPSE-vs-STAYS
#   DECISION is a multi-seed FULL call (per HOLD-mechanism-story discipline: smoke reports VERDICT-vs-BANDS only).
# - multi-seed: ensemble members ARE independent seeds; verdict aggregates over ensemble target models (LOMO).
# - HARD_PASS strictly two-sided: BOTH partial and within-bin <= 0.15 (collapse) with mirror-stays; HARD_FAIL
#   BOTH >= 0.25 (stays). No single-measure pass.
# - HP_SCOPE: anchor-reproduce -> {CROSSFIT raw}; baseline-in-band -> {CROSSFIT}; mirror-stays control ->
#   {MIRROR}; collapse/stays decision -> {CROSSFIT partial + within-bin}. determinacy = reported diagnostic.
# - cardinality_ok: EXPECTED_N_UNITS = N_ens + N_mir self-play trainings; verdict counts per_model records.
# - per-unit failure-class instrumentation (no bare except; per-(role,seed) failure_class).
# - calibration_check: adaptive_with_discriminator_gate (K / bins / ensemble size fixed per profile; difficulty
#   non-degeneracy floor + mirror-stays control + anchor-in-band + two-case machinery self-test all gate).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in this docstring / the pre-reg.
# - PERSISTS per-item failure masks + difficulty to a sidecar per_item_masks.npz (fixes the self-play cells'
#   no_storage gap -> the result is re-auditable off-disk). Not a PartitionedStore write.

Compute architecture: (c) mixed sequential-CPU with justification. Self-play training loops are sequential over
epochs (genuine dependency); nets are shallow ProjHeads (code_dim<=192) + a K x code channel matrix; per-step
ops are batched matmuls / gumbel-softmax / candidate scoring. N_ens+N_mir independent trainings (11 at FULL);
not GPU-batching-mandatory (small nets, loop sequential-dependent). Storage: no_substrate_store; persists a
per_item_masks.npz sidecar (re-auditability, not a store write). progress_logging: print_flush_true (line-
buffered stdout + flush=True progress + per-(role,seed) heartbeat; FULL timeout_s >= 1800).

Reuses VERBATIM (calibration continuity, NO drift): the B1_crossfit + A4_mirror self-play machinery
(train_arm, eval_masks, Channel, ARM_MODE, _arm_K, forward_game) from
experiments/exp_selfplay_message_channel_ablation_v1.py; failure_mask_corr, neighborhood_augment,
build_candidate_sets from experiments/exp_selfplay_dg_pattern_separation_xfit_v1.py; load_cn_subgraph,
char_trigram_features, build_adjlist, _l2norm from
experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py. NEW (additive): leave-model-out ensemble
difficulty, the difficulty-partialled + within-difficulty-bin correlation estimators, the determinacy-fraction,
the mirror must-stay control, the two-case machinery self-test, per-item persistence, the fairness verdict.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir,
    write_metrics,
    write_partial,
)
from experiments.exp_selfplay_dg_pattern_separation_xfit_v1 import (  # noqa: E402
    failure_mask_corr,
    neighborhood_augment,
    build_candidate_sets,
)
from experiments.exp_teacher_free_relational_encoder_cn_subgraph_v1 import (  # noqa: E402
    load_cn_subgraph,
    char_trigram_features,
    build_adjlist,
)
from experiments.exp_selfplay_message_channel_ablation_v1 import (  # noqa: E402
    train_arm as sp_train_arm,
    eval_masks as sp_eval_masks,
    ARM_MODE,
    _arm_K,
)

ANCHOR_NAME = "grounding_selfplay_fair_test_difficulty_partial_v1"
SUBGRAPH_BASE_SEED = 1234

CROSSFIT_ARM = "A0_shared"   # == B1_crossfit (separate Enc_S/Enc_L, disjoint folds, shared discrete channel)
MIRROR_ARM = "A4_mirror"     # tied encoder positive control (genuine coupling; partial must STAY high)

_T0 = time.time()
RUN_MODE_GLOBAL = "full"

# ---------------------------------------------------------------------------
# Config profiles (SMOKE exercises the SAME branches as FULL; scale + ensemble parity)
# ---------------------------------------------------------------------------
SELFTEST_CFG = dict(
    n_nodes=300, ens_seeds=[7, 13, 19], mir_seeds=[101], epochs=12, batch=128,
    code_dim=32, feat_dim=512,
    lr=0.01, lambda_ent=0.1, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=8, K_wide=64, n_dist=5, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=150,
    n_bins=5,
)
SMOKE_CFG = dict(
    n_nodes=1500, ens_seeds=[7, 13, 17, 23], mir_seeds=[101, 103], epochs=80, batch=256,
    code_dim=96, feat_dim=4096,
    lr=0.01, lambda_ent=0.1, temp=0.15, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=12, K_wide=96, n_dist=7, gumbel_tau=2.0, gumbel_tau_end=0.5, neighbor_weight=0.5, n_eval=700,
    n_bins=8,
)
FULL_CFG = dict(
    n_nodes=8000, ens_seeds=[7, 13, 17, 23, 29, 31, 37, 41], mir_seeds=[101, 103, 107], epochs=220, batch=512,
    code_dim=192, feat_dim=8192,
    lr=0.008, lambda_ent=0.1, temp=0.12, lambda_cov=1.0, lambda_var=1.0, lambda_rel=0.05,
    K=24, K_wide=192, n_dist=9, gumbel_tau=2.0, gumbel_tau_end=0.4, neighbor_weight=0.5, n_eval=3000,
    n_bins=10,
)

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED; PROSPECTIVE)
# ---------------------------------------------------------------------------
ANCHOR_LO = 0.28              # CROSSFIT raw corr must reproduce the ~0.38 cross-fit floor
ANCHOR_HI = 0.50
COLLAPSE_MAX = 0.15           # HARD_PASS (fairness artifact): partial AND within-bin <= this
REAL_MIN = 0.25               # HARD_FAIL (real bound): partial AND within-bin >= this
MIRROR_STAY_MIN = 0.40        # positive control: mirror partial corr must STAY >= this
MIRROR_RAW_MARGIN = 0.20      # positive control: mirror raw corr must exceed crossfit raw by >= this
FAILRATE_LO = 0.05            # baseline-in-band lower edge (both halves)
FAILRATE_HI = 0.95            # baseline-in-band upper edge (both halves)
DIFF_VAR_MIN = 1e-3           # difficulty non-degeneracy: Var(d_i) must exceed this
DIFF_MIN_VARYING_BINS = 3     # difficulty non-degeneracy: >= this many quantile bins with within-bin variance
# machinery self-test thresholds (BAND-TIED: a known-artifact must land in the collapse band, a known
# genuine coupling in the stays band, with a clear separation gap -> validates the bands are on the right
# side of the estimator's finite-ensemble attenuation floor)
ST_CASE1_COLLAPSE = COLLAPSE_MAX  # 0.15: case-1 (pure shared difficulty) partial/within-bin must be <= this
ST_CASE1_RAW_MIN = 0.05       # case-1 raw corr must be > this (there IS a shared-difficulty signal to remove)
ST_CASE2_STAY = REAL_MIN      # 0.25: case-2 (real coupling) partial/within-bin must be >= this
ST_SEPARATION = 0.15          # case-2 partial/within-bin must exceed case-1 by >= this (clean separation)
# determinacy diagnostic
DETERMINACY_TAUS = [0.3, 0.5, 0.7]
DETERMINACY_PRIMARY_TAU = 0.5

CONFIG_VERSION = (
    "ANCHOR=%s,xarm=%s,marm=%s,anchor=[%.2f,%.2f],collapse<=%.2f,real>=%.2f,mirStay>=%.2f,mirRaw>=%.2f,"
    "failband=[%.2f,%.2f],diffVar>=%g,stC1<=%.2f,stC2>=%.2f,detTau=%.2f"
) % (ANCHOR_NAME, CROSSFIT_ARM, MIRROR_ARM, ANCHOR_LO, ANCHOR_HI, COLLAPSE_MAX, REAL_MIN,
     MIRROR_STAY_MIN, MIRROR_RAW_MARGIN, FAILRATE_LO, FAILRATE_HI, DIFF_VAR_MIN,
     ST_CASE1_COLLAPSE, ST_CASE2_STAY, DETERMINACY_PRIMARY_TAU)


# ---------------------------------------------------------------------------
# Defensive error-checking scaffolding (SCHEMA-VET section 13)
# ---------------------------------------------------------------------------
def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED",
                verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__),
                elapsed_s=round(time.time() - _T0, 1), traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME, run_mode=RUN_MODE_GLOBAL, config_version=CONFIG_VERSION)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir, unit_idx, total, note=""):
    try:
        row = dict(ts_iso=datetime.now(timezone.utc).isoformat(), unit_idx=unit_idx,
                   total_units=total, elapsed_s=round(time.time() - _T0, 1), note=note)
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Correlation / partial-correlation estimators (the fair-scoring core)
# ---------------------------------------------------------------------------
def _pearson(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.std() < 1e-12 or y.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _residualize(y, Z):
    """Return residuals of y regressed on design Z (least squares)."""
    y = np.asarray(y, dtype=np.float64)
    beta, _res, _rank, _sv = np.linalg.lstsq(Z, y, rcond=None)
    return y - Z @ beta


def _partial_corr(fa_s, fa_l, Z):
    """Pearson correlation of fa_s and fa_l AFTER residualizing both on the column space of Z."""
    rs = _residualize(fa_s, Z)
    rl = _residualize(fa_l, Z)
    return _pearson(rs, rl)


def _lin_design(d):
    """Design matrix [1, dz, dz^2] with standardized d (linear + quadratic difficulty control)."""
    d = np.asarray(d, dtype=np.float64)
    sd = d.std()
    dz = (d - d.mean()) / (sd if sd > 1e-12 else 1.0)
    return np.column_stack([np.ones_like(dz), dz, dz * dz])


def _quantile_bins(d, Q):
    """Assign each item to one of Q equal-count quantile bins of d. Returns (binid [n], Q_effective)."""
    d = np.asarray(d, dtype=np.float64)
    n = d.shape[0]
    ranks = np.argsort(np.argsort(d))
    binid = np.minimum((ranks * Q) // max(n, 1), Q - 1).astype(np.int64)
    return binid, Q


def _bin_design(binid, Q):
    """One-hot bin design. Residualizing on it == demeaning within bins (pooled within-bin correlation)."""
    n = binid.shape[0]
    Z = np.zeros((n, Q), dtype=np.float64)
    Z[np.arange(n), binid] = 1.0
    # drop all-empty columns (keeps lstsq well-conditioned)
    keep = Z.sum(axis=0) > 0
    return Z[:, keep]


def _per_bin_phi(fa_s, fa_l, binid, Q, min_bin=10):
    """Per-bin phi(fail_s, fail_l). Returns (list of phi-or-nan, n_varying_bins)."""
    out = []
    n_varying = 0
    for b in range(Q):
        sel = (binid == b)
        if sel.sum() >= min_bin:
            phi = _pearson(fa_s[sel], fa_l[sel])
            out.append(phi if phi == phi else None)
            if phi == phi:
                n_varying += 1
        else:
            out.append(None)
    return out, n_varying


def fair_scores(fa_s, fa_l, d, Q):
    """Raw, difficulty-partialled (linear), and within-difficulty-bin correlations of two fail masks.
    fa_s, fa_l: float {0,1} arrays [n]. d: continuous difficulty [n]. Q: n quantile bins.
    (SECONDARY / per-model view; attenuation-prone at the single-model binary level.)"""
    raw = _pearson(fa_s, fa_l)
    part_lin = _partial_corr(fa_s, fa_l, _lin_design(d))
    binid, Qe = _quantile_bins(d, Q)
    within_bin = _partial_corr(fa_s, fa_l, _bin_design(binid, Qe))
    per_bin, n_varying = _per_bin_phi(fa_s, fa_l, binid, Qe)
    return dict(raw=raw, partial_linear=part_lin, within_bin=within_bin,
                per_bin_phi=per_bin, n_varying_bins=int(n_varying))


def cross_model_decomp(fs_stack, fl_stack):
    """PRIMARY difficulty control (attenuation-free). fs_stack, fl_stack: [K, M] fail masks over K models.
    within  = mean_m phi(fail_s^m, fail_l^m)                 -- the within-model failmask correlation (raw).
    floor   = mean_{a!=b} phi(fail_s^a, fail_l^b)            -- two competences from DIFFERENT models can only
              co-fail via TASK-LEVEL shared item difficulty (mechanism-invariant, reproducible-across-models).
              This is the exact analog of partialling the reader's intrinsic branching-factor k_sr.
    residual = within - floor                                -- the DIFFICULTY-CONTROLLED coupling: the part of
              the within-model correlation NOT explained by task-level shared item difficulty."""
    K = fs_stack.shape[0]
    within = [_pearson(fs_stack[m], fl_stack[m]) for m in range(K)]
    cross = [_pearson(fs_stack[a], fl_stack[b]) for a in range(K) for b in range(K) if a != b]
    within_m = _mean(within)
    cross_m = _mean(cross)
    # same-role cross-model floor (spk^a vs spk^b) as an additional task-difficulty read
    cross_ss = [_pearson(fs_stack[a], fs_stack[b]) for a in range(K) for b in range(K) if a < b]
    return dict(within=within_m, cross_floor=cross_m, residual=within_m - cross_m,
                cross_floor_samerole=_mean(cross_ss), per_model_within=within)


# ---------------------------------------------------------------------------
# Structural determinacy + collision difficulty (encoder-free; trigram feature space)
# ---------------------------------------------------------------------------
def collision_stats(X, cand_idx, taus):
    """X [n, feat] L2-normalized rows. cand_idx [M, 1+ND] (col0=target). Returns per-item:
    max distractor-target cosine (collision difficulty proxy), and determinate flag per tau."""
    tgt = cand_idx[:, 0]
    dist = cand_idx[:, 1:]
    Xt = X[tgt].astype(np.float64)                        # [M, feat]
    Xd = X[dist].astype(np.float64)                       # [M, ND, feat]
    sims = np.einsum("mf,mkf->mk", Xt, Xd)                # cosine (unit rows) [M, ND]
    max_sim = sims.max(axis=1)                            # [M]
    determinate = {}
    n_coll = {}
    for tau in taus:
        nc = (sims >= tau).sum(axis=1)
        n_coll["%.2f" % tau] = nc.astype(np.int64)
        determinate["%.2f" % tau] = float((nc == 0).mean())
    return max_sim.astype(np.float64), n_coll, determinate


# ---------------------------------------------------------------------------
# Machinery self-test: two controlled cases with KNOWN answers (telemetry-sensitivity of the estimator)
# ---------------------------------------------------------------------------
def machinery_selftest():
    """Validates the PRIMARY (cross-model residual) AND SECONDARY (within-bin) estimators on two synthetic
    ensembles with KNOWN answers. case 1 = pure TASK-LEVEL shared difficulty (the SAME per-item difficulty
    drives every model's speaker + listener, conditionally independent) -> the cross-model floor equals the
    within-model correlation, so residual MUST collapse (<=COLLAPSE_MAX), and within-bin (binned by the
    ensemble-mean difficulty, which captures the shared d) MUST collapse. case 2 = MODEL-SPECIFIC coupling
    (each model has its own hard items + a direct within-model speaker==listener coupling) -> cross-model floor
    ~0, residual == within (stays >=REAL_MIN), and within-bin binned by ensemble-mean (which washes out the
    per-model structure) stays high. Proves the decomposition separates task-difficulty from mechanism-specific
    coupling; if it cannot, the cell is void."""
    rng = np.random.default_rng(0)
    n = 4000
    E = 8                       # synthetic ensemble size (matches FULL N_ens)
    Q = 10
    p_ctr = 0.5

    def _spread_d(gen):
        return np.clip(p_ctr + 0.47 * (2.0 * gen.random(n) - 1.0), 0.02, 0.98)   # within ~0.29 by construction

    # CASE 1: TASK-LEVEL shared difficulty (same d_shared across ALL models; halves conditionally independent)
    d_shared = _spread_d(rng)
    fs1 = np.zeros((E, n)); fl1 = np.zeros((E, n))
    for m in range(E):
        fs1[m] = (rng.random(n) < d_shared).astype(np.float64)
        fl1[m] = (rng.random(n) < d_shared).astype(np.float64)
    dc1 = cross_model_decomp(fs1, fl1)
    d_hat1 = np.vstack([fs1, fl1]).mean(axis=0)                # ensemble-mean difficulty (captures d_shared)
    wb1 = _mean([fair_scores(fs1[m], fl1[m], d_hat1, Q)["within_bin"] for m in range(E)])

    # CASE 2: MODEL-SPECIFIC difficulty + direct within-model coupling (speaker==listener on a fraction)
    fs2 = np.zeros((E, n)); fl2 = np.zeros((E, n))
    for m in range(E):
        d_m = _spread_d(rng)                                  # each model its OWN hard items
        fs2[m] = (rng.random(n) < d_m).astype(np.float64)
        base = (rng.random(n) < d_m).astype(np.float64)
        couple = rng.random(n) < 0.4                          # 40% direct speaker==listener coupling
        fl2[m] = np.where(couple, fs2[m], base)
    dc2 = cross_model_decomp(fs2, fl2)
    d_hat2 = np.vstack([fs2, fl2]).mean(axis=0)               # washes out per-model structure (~constant)
    wb2 = _mean([fair_scores(fs2[m], fl2[m], d_hat2, Q)["within_bin"] for m in range(E)])

    case1_collapses = bool(dc1["within"] > ST_CASE1_RAW_MIN
                           and dc1["residual"] <= ST_CASE1_COLLAPSE and abs(wb1) <= ST_CASE1_COLLAPSE)
    case2_stays = bool(dc2["residual"] >= ST_CASE2_STAY and wb2 >= ST_CASE2_STAY)
    separation = bool((dc2["residual"] - dc1["residual"]) >= ST_SEPARATION)
    ok = bool(case1_collapses and case2_stays and separation)
    return ok, dict(
        case1_within=round(dc1["within"], 4), case1_floor=round(dc1["cross_floor"], 4),
        case1_residual=round(dc1["residual"], 4), case1_within_bin=round(wb1, 4),
        case1_collapses=case1_collapses,
        case2_within=round(dc2["within"], 4), case2_floor=round(dc2["cross_floor"], 4),
        case2_residual=round(dc2["residual"], 4), case2_within_bin=round(wb2, 4),
        case2_stays=case2_stays, separation=separation, E=E,
    )


# ---------------------------------------------------------------------------
# Train one self-play model + eval per-item masks on the FIXED eval set
# ---------------------------------------------------------------------------
def run_model(arm, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx, out_dir, tag):
    mode = ARM_MODE[arm]
    K = _arm_K(mode, cfg)
    enc_s, enc_l, chan = sp_train_arm(arm, cfg, X, Xn, adj, seed, n_nodes, out_dir, tag=tag)
    tau_final = cfg.get("gumbel_tau_end", cfg["gumbel_tau"])
    ev = sp_eval_masks(enc_s, enc_l, chan, Xn, X, eval_idx, cand_idx, K, tau_final)
    spk = np.asarray(ev["speaker_correct"], dtype=bool)
    lis = np.asarray(ev["listener_correct"], dtype=bool)
    dig = hashlib.sha256(np.concatenate([spk, lis]).tobytes()).hexdigest()
    return dict(arm=arm, seed=seed, mode=mode, K=int(K),
                speaker_correct=spk, listener_correct=lis,
                grounding_acc=float(lis.mean()),
                speaker_fail_rate=float((~spk).mean()), listener_fail_rate=float((~lis).mean()),
                symbol_entropy_bits=float(ev["symbol_entropy_bits"]), n_symbols_used=int(ev["n_symbols_used"]),
                mask_digest=dig)


def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


# ---------------------------------------------------------------------------
# Aggregate + fairness verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(ens_models, mir_models, d_collision, determinacy, n_coll_primary,
                          cfg, subgraph_meta, run_mode, st_res):
    Q = cfg["n_bins"]
    n_ens = len(ens_models)
    M = ens_models[0]["speaker_correct"].shape[0]

    # ---- fail-mask stacks + ensemble difficulty (competence matrix rows 2m=spk-fail, 2m+1=lis-fail) ----
    xf_fs = np.stack([(~m["speaker_correct"]).astype(np.float64) for m in ens_models])   # [n_ens, M]
    xf_fl = np.stack([(~m["listener_correct"]).astype(np.float64) for m in ens_models])
    comp_fail = np.zeros((2 * n_ens, M), dtype=np.float64)
    comp_fail[0::2] = xf_fs
    comp_fail[1::2] = xf_fl
    d_full = comp_fail.mean(axis=0)                       # ensemble difficulty (used for mirror + within-bin)
    diff_var = float(np.var(d_full))
    ds_hat = xf_fs.mean(axis=0)
    dl_hat = xf_fl.mean(axis=0)
    shared_diff_corr = _pearson(ds_hat, dl_hat)           # diagnostic (ensemble-avg speaker vs listener diff)

    # ---- PRIMARY: cross-model co-failure decomposition (attenuation-free task-difficulty control) ----
    xf_dc = cross_model_decomp(xf_fs, xf_fl)
    raw_xf = xf_dc["within"]
    floor_xf = xf_dc["cross_floor"]
    residual_xf = xf_dc["residual"]

    # ---- SECONDARY (reported): per-model within-difficulty-bin + LOMO linear partial (attenuation-prone) ----
    xf_bin, xf_part, xf_part_coll, xf_nvary = [], [], [], []
    per_model = []
    for m, mm in enumerate(ens_models):
        keep = np.ones(2 * n_ens, dtype=bool)
        keep[2 * m] = False
        keep[2 * m + 1] = False
        d_lomo = comp_fail[keep].mean(axis=0)
        fa_s = xf_fs[m]; fa_l = xf_fl[m]
        sc = fair_scores(fa_s, fa_l, d_lomo, Q)
        sc_coll = fair_scores(fa_s, fa_l, d_collision, Q)
        xf_bin.append(sc["within_bin"]); xf_part.append(sc["partial_linear"])
        xf_part_coll.append(sc_coll["partial_linear"]); xf_nvary.append(sc["n_varying_bins"])
        per_model.append(dict(
            role="crossfit", arm=mm["arm"], seed=mm["seed"], K=mm["K"],
            grounding_acc=mm["grounding_acc"], speaker_fail_rate=mm["speaker_fail_rate"],
            listener_fail_rate=mm["listener_fail_rate"], symbol_entropy_bits=mm["symbol_entropy_bits"],
            n_symbols_used=mm["n_symbols_used"], within_model_corr=xf_dc["per_model_within"][m],
            within_bin_ens=sc["within_bin"], partial_lomo=sc["partial_linear"],
            partial_collision=sc_coll["partial_linear"], n_varying_bins=sc["n_varying_bins"]))
    within_bin_xf = _mean(xf_bin)
    partial_xf = _mean(xf_part)
    partial_xf_coll = _mean(xf_part_coll)
    spk_fail_xf = _mean([mm["speaker_fail_rate"] for mm in ens_models])
    lis_fail_xf = _mean([mm["listener_fail_rate"] for mm in ens_models])
    ground_xf = _mean([mm["grounding_acc"] for mm in ens_models])

    # ---- MIRROR positive control: same cross-model decomposition (residual must STAY high) ----
    mir_fs = np.stack([(~m["speaker_correct"]).astype(np.float64) for m in mir_models])
    mir_fl = np.stack([(~m["listener_correct"]).astype(np.float64) for m in mir_models])
    mir_dc = cross_model_decomp(mir_fs, mir_fl)
    raw_mir = mir_dc["within"]
    floor_mir = mir_dc["cross_floor"]
    residual_mir = mir_dc["residual"]
    mir_bin = []
    for m, mm in enumerate(mir_models):
        sc = fair_scores(mir_fs[m], mir_fl[m], d_full, Q)   # bin by crossfit-ensemble difficulty
        mir_bin.append(sc["within_bin"])
        per_model.append(dict(
            role="mirror", arm=mm["arm"], seed=mm["seed"], K=mm["K"],
            grounding_acc=mm["grounding_acc"], speaker_fail_rate=mm["speaker_fail_rate"],
            listener_fail_rate=mm["listener_fail_rate"], within_model_corr=mir_dc["per_model_within"][m],
            within_bin_ens=sc["within_bin"]))
    within_bin_mir = _mean(mir_bin)

    # ---- gate evaluation ----
    n_varying = int(_mean(xf_nvary)) if xf_nvary else 0
    difficulty_ok = bool(diff_var >= DIFF_VAR_MIN and n_varying >= DIFF_MIN_VARYING_BINS)
    anchor_ok = bool(raw_xf == raw_xf and ANCHOR_LO <= raw_xf <= ANCHOR_HI)
    baseline_in_band = bool(FAILRATE_LO < spk_fail_xf < FAILRATE_HI and FAILRATE_LO < lis_fail_xf < FAILRATE_HI)
    mirror_valid = bool(raw_mir == raw_mir and residual_mir == residual_mir
                        and (raw_mir - raw_xf) >= MIRROR_RAW_MARGIN
                        and residual_mir >= MIRROR_STAY_MIN)
    st_ok = bool(st_res.get("case1_collapses") and st_res.get("case2_stays") and st_res.get("separation"))

    # PRIMARY = cross-model residual; SECONDARY = within-difficulty-bin. BOTH must agree for a hard verdict.
    collapses = bool(residual_xf == residual_xf and within_bin_xf == within_bin_xf
                     and residual_xf <= COLLAPSE_MAX and within_bin_xf <= COLLAPSE_MAX)
    stays = bool(residual_xf == residual_xf and within_bin_xf == within_bin_xf
                 and residual_xf >= REAL_MIN and within_bin_xf >= REAL_MIN)

    if not st_ok:
        verdict = "MACHINERY_SELFTEST_FAILED"
    elif not baseline_in_band:
        verdict = "BASELINE_OUT_OF_BAND"
    elif not anchor_ok:
        verdict = "ANCHOR_NOT_REPRODUCED_VOID"
    elif not difficulty_ok:
        verdict = "DIFFICULTY_DEGENERATE_VOID"
    elif not mirror_valid:
        verdict = "MIRROR_CONTROL_FAILED_VOID"
    elif collapses:
        verdict = "HARD_PASS_FAIRNESS_ARTIFACT"
    elif stays:
        verdict = "HARD_FAIL_REAL_BOUND"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_COLLAPSE"

    det_primary = determinacy.get("%.2f" % DETERMINACY_PRIMARY_TAU, float("nan"))
    verdict_msg = (
        "%s | mode=%s | CROSSFIT within(raw)=%.3f (anchor=%s) task_diff_floor=%.3f residual=%.3f "
        "within_bin=%.3f partial_lomo=%.3f partial_coll=%.3f (spk_fail=%.3f lis_fail=%.3f ground=%.3f "
        "in_band=%s) | MIRROR within=%.3f floor=%.3f residual=%.3f within_bin=%.3f (rise=%+.3f valid=%s) | "
        "diff_var=%.4f n_varying_bins=%d ok=%s shared_diff_corr=%.3f | determinacy@%.2f=%.3f (all=%s "
        "mean_ncoll=%.2f) | selftest c1_resid=%.3f c1_bin=%.3f c2_resid=%.3f c2_bin=%.3f ok=%s | "
        "bands: collapse<=%.2f real>=%.2f mirStay>=%.2f | n_ens=%d n_mir=%d n_eval=%d nodes=%d E=%d run=%s" % (
            verdict, run_mode, raw_xf, anchor_ok, floor_xf, residual_xf, within_bin_xf, partial_xf,
            partial_xf_coll, spk_fail_xf, lis_fail_xf, ground_xf, baseline_in_band,
            raw_mir, floor_mir, residual_mir, within_bin_mir, raw_mir - raw_xf, mirror_valid,
            diff_var, n_varying, difficulty_ok, shared_diff_corr,
            DETERMINACY_PRIMARY_TAU, det_primary, determinacy, float(np.mean(n_coll_primary)),
            st_res.get("case1_residual", float("nan")), st_res.get("case1_within_bin", float("nan")),
            st_res.get("case2_residual", float("nan")), st_res.get("case2_within_bin", float("nan")), st_ok,
            COLLAPSE_MAX, REAL_MIN, MIRROR_STAY_MIN,
            len(ens_models), len(mir_models), M, subgraph_meta.get("n_nodes", -1),
            subgraph_meta.get("n_edges", -1), run_mode))

    gates = dict(
        verdict=verdict,
        crossfit=dict(raw_within_model=raw_xf, task_diff_floor=floor_xf, residual=residual_xf,
                      cross_floor_samerole=xf_dc["cross_floor_samerole"], within_bin_ens=within_bin_xf,
                      partial_lomo=partial_xf, partial_collision=partial_xf_coll,
                      speaker_fail_rate=spk_fail_xf, listener_fail_rate=lis_fail_xf, grounding_acc=ground_xf,
                      per_model_within=xf_dc["per_model_within"], per_seed_within_bin=xf_bin),
        mirror=dict(raw_within_model=raw_mir, task_diff_floor=floor_mir, residual=residual_mir,
                    within_bin_ens=within_bin_mir, rise_over_crossfit=raw_mir - raw_xf),
        difficulty=dict(diff_var=diff_var, n_varying_bins=n_varying, shared_diff_corr=shared_diff_corr,
                        difficulty_ok=difficulty_ok),
        determinacy=dict(by_tau=determinacy, primary_tau=DETERMINACY_PRIMARY_TAU, primary=det_primary,
                         mean_ncoll_primary=float(np.mean(n_coll_primary))),
        anchor_ok=anchor_ok, baseline_in_band=baseline_in_band, mirror_valid=mirror_valid,
        machinery_selftest_ok=st_ok, collapses=collapses, stays=stays,
        bands=dict(ANCHOR_LO=ANCHOR_LO, ANCHOR_HI=ANCHOR_HI, COLLAPSE_MAX=COLLAPSE_MAX, REAL_MIN=REAL_MIN,
                   MIRROR_STAY_MIN=MIRROR_STAY_MIN, MIRROR_RAW_MARGIN=MIRROR_RAW_MARGIN,
                   FAILRATE_LO=FAILRATE_LO, FAILRATE_HI=FAILRATE_HI, DIFF_VAR_MIN=DIFF_VAR_MIN),
    )
    return verdict, verdict_msg, gates, per_model, d_full, ds_hat, dl_hat


# ---------------------------------------------------------------------------
# Persist per-item masks + difficulty (fixes the self-play no_storage gap; re-auditable off-disk)
# ---------------------------------------------------------------------------
def persist_per_item(out_dir, ens_models, mir_models, eval_idx, cand_idx, d_full, ds_hat, dl_hat,
                     d_collision, n_coll_primary):
    M = eval_idx.shape[0]
    ens_spk = np.stack([m["speaker_correct"] for m in ens_models]).astype(bool)
    ens_lis = np.stack([m["listener_correct"] for m in ens_models]).astype(bool)
    payload = dict(
        eval_idx=eval_idx.astype(np.int64), cand_idx=cand_idx.astype(np.int64),
        ens_seeds=np.array([m["seed"] for m in ens_models], dtype=np.int64),
        ens_speaker_correct=ens_spk, ens_listener_correct=ens_lis,
        d_ensemble_full=d_full.astype(np.float64), ds_hat=ds_hat.astype(np.float64),
        dl_hat=dl_hat.astype(np.float64), d_collision=d_collision.astype(np.float64),
        n_collisions_primary=n_coll_primary.astype(np.int64),
    )
    if mir_models:
        payload["mir_seeds"] = np.array([m["seed"] for m in mir_models], dtype=np.int64)
        payload["mir_speaker_correct"] = np.stack([m["speaker_correct"] for m in mir_models]).astype(bool)
        payload["mir_listener_correct"] = np.stack([m["listener_correct"] for m in mir_models]).astype(bool)
    path = os.path.join(out_dir, "per_item_masks.npz")
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, **payload)
    os.replace(tmp, path)
    return path, int(M)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global RUN_MODE_GLOBAL
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args, _unknown = ap.parse_known_args()
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = args.run_mode
    if "_smoke" in os.environ.get("HDLAB_EXP_NAME", "").lower():
        run_mode = "smoke"
    RUN_MODE_GLOBAL = run_mode

    import torch
    output_dir = str(get_output_dir(ANCHOR_NAME))
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["ens_seeds"]) + len(cfg["mir_seeds"])
    _write_start_marker(output_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    st_ok, st_res = machinery_selftest()
    _log("machinery_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="MACHINERY_SELFTEST_FAILED", run_mode=run_mode,
            verdict_msg="MACHINERY_SELFTEST_FAILED (partial-corr estimator not telemetry-sensitive): %s" % st_res,
            summary="machinery selftest failed", elapsed_s=time.perf_counter() - t_start,
            machinery_selftest=st_res, config_version=CONFIG_VERSION))
        raise SystemExit(1)

    _log("loading ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, meta = load_cn_subgraph(cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    n_nodes = len(node_ids)
    _log("subgraph: %s" % meta)
    X = char_trigram_features(node_words, cfg["feat_dim"])
    adj = build_adjlist(edges, n_nodes)
    Xn = neighborhood_augment(X, adj, cfg["neighbor_weight"])

    eval_rng = np.random.default_rng(SUBGRAPH_BASE_SEED + 999)
    has_nb = np.nonzero(np.array([len(adj[i]) > 0 for i in range(n_nodes)], dtype=bool))[0]
    n_eval = int(min(cfg["n_eval"], has_nb.shape[0]))
    eval_idx = np.sort(eval_rng.choice(has_nb, size=n_eval, replace=False))
    cand_idx = build_candidate_sets(eval_idx, n_nodes, cfg["n_dist"], eval_rng)
    _log("eval referents=%d candidate_set_size=%d" % (n_eval, 1 + cfg["n_dist"]))

    # structural determinacy + collision difficulty (encoder-free)
    d_collision, n_coll, determinacy = collision_stats(X, cand_idx, DETERMINACY_TAUS)
    n_coll_primary = n_coll["%.2f" % DETERMINACY_PRIMARY_TAU]
    _log("determinacy=%s mean_max_sim=%.3f" % (determinacy, float(np.mean(d_collision))))

    if run_mode == "self_test":
        write_metrics(get_output_dir(ANCHOR_NAME), dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS machinery telemetry-sensitive (case1 collapses, case2 stays) + pipeline "
                        "exercised (subgraph + eval set + determinacy)",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start,
            machinery_selftest=st_res, determinacy=determinacy, subgraph_meta=meta,
            config_version=CONFIG_VERSION))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    out_dir_path = get_output_dir(ANCHOR_NAME)
    ens_models = []
    mir_models = []
    unit_failures = []
    total_units = expected_n_units
    u = 0
    for seed in cfg["ens_seeds"]:
        u += 1
        try:
            r = run_model(CROSSFIT_ARM, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx,
                          out_dir_path, tag="XF_s%d" % seed)
            ens_models.append(r)
            write_partial(out_dir_path, "crossfit_seed%d" % seed,
                          dict(seed=seed, role="crossfit", grounding_acc=r["grounding_acc"],
                               speaker_fail_rate=r["speaker_fail_rate"],
                               listener_fail_rate=r["listener_fail_rate"]))
            _log("[%d/%d] CROSSFIT seed=%d ground=%.3f spk_fail=%.3f lis_fail=%.3f ent=%.2f nsym=%d" % (
                u, total_units, seed, r["grounding_acc"], r["speaker_fail_rate"],
                r["listener_fail_rate"], r["symbol_entropy_bits"], r["n_symbols_used"]))
            _heartbeat(out_dir_path, u, total_units, note="crossfit seed=%d" % seed)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            unit_failures.append(dict(role="crossfit", seed=seed, failure_class=type(e).__name__,
                                      msg=str(e)[:300]))
            _log("UNIT_FAILED crossfit seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))
    for seed in cfg["mir_seeds"]:
        u += 1
        try:
            r = run_model(MIRROR_ARM, cfg, X, Xn, adj, seed, n_nodes, eval_idx, cand_idx,
                          out_dir_path, tag="MIR_s%d" % seed)
            mir_models.append(r)
            write_partial(out_dir_path, "mirror_seed%d" % seed,
                          dict(seed=seed, role="mirror", grounding_acc=r["grounding_acc"],
                               speaker_fail_rate=r["speaker_fail_rate"],
                               listener_fail_rate=r["listener_fail_rate"]))
            _log("[%d/%d] MIRROR seed=%d ground=%.3f spk_fail=%.3f lis_fail=%.3f" % (
                u, total_units, seed, r["grounding_acc"], r["speaker_fail_rate"], r["listener_fail_rate"]))
            _heartbeat(out_dir_path, u, total_units, note="mirror seed=%d" % seed)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            unit_failures.append(dict(role="mirror", seed=seed, failure_class=type(e).__name__,
                                      msg=str(e)[:300]))
            _log("UNIT_FAILED mirror seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(ens_models) < len(cfg["ens_seeds"]) or len(mir_models) < len(cfg["mir_seeds"]):
        write_metrics(out_dir_path, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d crossfit + %d mirror, got %d + %d (failures=%s)" % (
                len(cfg["ens_seeds"]), len(cfg["mir_seeds"]), len(ens_models), len(mir_models),
                unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, subgraph_meta=meta, config_version=CONFIG_VERSION))
        raise SystemExit(1)

    # ARMS-MUST-DIFFER (META_RULE_AF): all model mask-pairs must differ
    digs = {}
    for m in ens_models + mir_models:
        key = "%s_%d" % (m["arm"], m["seed"])
        digs[key] = m["mask_digest"]
    keys = list(digs.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            assert digs[keys[i]] != digs[keys[j]], (
                "META_RULE_AF VIOLATION: models %s and %s bit-identical" % (keys[i], keys[j]))

    subgraph_meta = dict(n_nodes=meta.get("n_nodes", n_nodes), n_edges=meta.get("n_edges", len(edges)),
                         median_degree=meta.get("median_degree", -1))
    verdict, verdict_msg, gates, per_model, d_full, ds_hat, dl_hat = aggregate_and_verdict(
        ens_models, mir_models, d_collision, determinacy, n_coll_primary, cfg, subgraph_meta, run_mode, st_res)

    sidecar_path, M = persist_per_item(out_dir_path, ens_models, mir_models, eval_idx, cand_idx,
                                       d_full, ds_hat, dl_hat, d_collision, n_coll_primary)
    _log("persisted per-item masks + difficulty -> %s (M=%d items)" % (sidecar_path, M))

    metrics = dict(
        verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200],
        run_mode=run_mode, elapsed_s=time.perf_counter() - t_start,
        anchor_name=ANCHOR_NAME, ts_iso=datetime.now(timezone.utc).isoformat(),
        n_ens=len(ens_models), n_mir=len(mir_models), ens_seeds=cfg["ens_seeds"], mir_seeds=cfg["mir_seeds"],
        config=cfg, config_version=CONFIG_VERSION, subgraph_meta=subgraph_meta, gates=gates,
        per_model=per_model, determinacy=determinacy, machinery_selftest=st_res,
        unit_failures=unit_failures, per_item_sidecar=os.path.basename(sidecar_path), n_eval_items=M,
    )
    write_metrics(out_dir_path, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
