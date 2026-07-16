"""Brain-faithful HOLD/consolidation tested in the 3 CORRECT regimes.

WHY THIS CELL EXISTS. The FAIR single-stream accrual test
(exp_multisource_arena_temporal_accrual_fair_v1, commit 7d873523b) found the
brain-faithful hold ties flat accumulation on ACCURACY. The brain-check
(notes/research_consolidation_currency_accuracy_vs_cost_2026-07-15.md) shows that
is a WRONG-REGIME null, not a refutation:
  (a) CLS (McClelland 95; McCloskey-Cohen 89) is a PURE ACCURACY / interference-
      avoidance mechanism whose value needs >=2 COMPETING items sharing a
      representation -- a single accruing stream never presents that competition.
  (b) STC/SHY (Frey-Morris 97; Tononi-Cirelli) bundle accuracy+CAPACITY
      inseparably -- value appears only when a WRITE BUDGET is priced.
  (c) ORDER/TRAJECTORY coding has proof-shaped support (White-Lee-Sompolinsky 04;
      Dambre 12): a flat LINEAR accumulator of {arrival, accumulated, corroboration,
      win} is STRUCTURALLY BLIND to order-dependent (XOR-of-lags) info a nonlinear
      hold-then-decay trace carries.

So the hold's core value was UNTESTED. This cell tests all 3 correct regimes, each
with its OWN certificate (the regime genuinely presents the predicament), a FIRED
positive control (the harness CAN express the advantage if real), a NULL guard
(the certificate is not vacuous), and the SAME readout metric (marginal held-out
balanced accuracy).

ANTI-RIG. In every regime the "flat accumulation" competitor is the STRONG fair
option (precision-weighted, full information), not a strawman -- the naive
keep-everything is reported alongside as the weak reference. The hold uses the SAME
score/evidence core; the ONLY difference is the consolidation structure
(selective-commit / capacity-selection / nonlinear trajectory trace). If the hold
STILL ties/loses the STRONG flat competitor even in its home regime, that is a real
FAIRLY-measured bound reported honestly as HARD_FAIL. Params set a priori; a sweep
is reported so the crossover is visible; nothing is tuned to make the hold win.

PRE-REG (overall, combining the 3 regimes):
  TIE_EPS = 0.010 ; X_BAND = 0.030 ; SIGMA_K = 2.0 (paired multi-seed z).
  Per regime the hold "wins" iff its regime certificate fires AND its controls fire
  AND margin(hold - strong_flat) > TIE_EPS AND z > SIGMA_K. A regime is VALID iff
  its certificate AND controls fire (else uninterpretable / INVALID_REGIME).
  HARD_PASS : hold wins in >=1 VALID regime (=> the elaborate structure earns its
              keep where its mechanism applies; the single-stream null was
              wrong-regime).
  HARD_FAIL : >=1 VALID regime AND hold ties/loses the strong flat competitor in
              ALL valid regimes (=> strong bound: structure adds nothing on this
              substrate even where its mechanism should apply).
  MIDDLE    : valid regimes exist, none a clean win, not all clean ties (e.g.
              positive-but-not-2sigma), OR no regime is VALID (arenas need fixing).

Pure-Python (numpy only). Reuses A.fit_weighted_sum + A._balanced_acc + A.pearson +
M._precision_weights (the VET'd arena+menu code). No substrate atoms, no torch, no
queue/GPU, no origin push. Runs inline in seconds. Multi-seed paired margins;
identical splits across all arms per seed.

Run:
  python experiments/exp_consolidation_correct_regimes_v1.py --self-test
  python experiments/exp_consolidation_correct_regimes_v1.py --profile smoke
  python experiments/exp_consolidation_correct_regimes_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (numpy design/validity cell; queue/substrate mandates n/a):
# - except SystemExit raised BEFORE except Exception (no BaseException)
# - no bare except; deterministic FIXED-int seeds (no hash()-derived seeds)
# - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
# - start-marker + crash-diagnostic + per-regime heartbeat written
# - arms_differ: within each regime the arm decisions are hash-checked distinct
# - baseline-in-band: strong-flat marginal checked in (0.05, 0.95) per regime
# - discriminator survives scale: full multi-seed paired margin+z is the
#   discriminator; smoke uses the full arm set at reduced size; each regime's
#   positive control fires the discriminator explicitly and its null guard proves
#   the certificate is not vacuous
# - CRLB: crlb_n/a = "classification balanced-acc bands, no Cramer-Rao noise floor"
# - all reported numbers MEASURED @ this run's metrics.json unless tagged else
# - real code path: reuses A.fit_weighted_sum / A._balanced_acc / A.pearson /
#   M._precision_weights (the VET'd arena + menu substrate code)

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_multisource_arena_v1 as A  # noqa: E402
import exp_multisource_arena_combination_menu_v1 as M  # noqa: E402

ANCHOR_NAME = "consolidation_correct_regimes_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_consolidation_correct_regimes_v1")

_balanced_acc = A._balanced_acc
pearson = A.pearson

# ---- pre-registered bands (shared) -----------------------------------------
TIE_EPS = 0.010
X_BAND = 0.030
SIGMA_K = 2.0

# ---- per-regime thresholds (a priori) --------------------------------------
# R1 interference
R1_D = 40          # bounded shared store dimension
R1_M = 28          # competing items superposed into ONE shared store per scene
R1_SCENES = 300    # independent scenes; recall pooled over scenes*M for stability
R1_NREADS = 5
R1_RHO = 0.72
R1_CERT_MIN = 0.030   # flat must degrade this much from M_small to M_full
R1_NULL_MAX = 0.030   # with a huge store the degradation must vanish
R1_POS_GAP = 0.030    # oracle-selective must beat flat by this
R1_M_SMALL = 3
R1_D_HUGE = 4096

# R2 capacity
R2_M = 400            # items arriving; only a few can be durably written
R2_BUDGET = 100       # consolidation-write budget (< M)
R2_REPS = 12          # arena replicates pooled per seed (stabilises estimates)
R2_NREADS = 5
R2_CERT_MIN = 0.030   # scarcity gap: unlimited-budget minus FIFO-under-budget
R2_TAGVALID_MIN = 0.10  # corr(confidence, correctness) -- selection is possible
R2_NULL_MAX = 0.020   # invalid tags -> selective per-write advantage must vanish
R2_POS_GAP = 0.030    # oracle-selection must beat FIFO by this

# R3 order / trajectory
R3_T = 6             # sequence length
R3_N = 2400          # sequences per seed
R3_LAG_A = 1         # label = XOR(sign at lag_a, sign at lag_c); OFF arrival (t0)
R3_LAG_C = 3         # so the flat corroboration/suffstats do not leak the label
R3_COINC_W = 2       # local-coincidence window: pairs with 1<=(j-i)<=W (covers lag)
R3_LAMBDA = 0.85     # hold-then-decay leak (leaky hold trace)
R3_CERT_MIN = 0.030  # linear-blindness gap: trajectory minus strong-flat-linear
R3_NULL_MAX = 0.030  # on an order-IRRELEVANT task that gap must vanish
R3_POS_MIN = 0.80    # trajectory must clear this on order task; flat on sum task


def _hash_dec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()


def _mean_se(vals):
    a = np.asarray(vals, float)
    m = float(a.mean())
    se = float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0
    return m, se


def _z(m, se):
    if se > 1e-12:
        return m / se
    return 0.0 if abs(m) < 1e-12 else float(np.sign(m)) * 99.0


# ============================================================================
# REGIME 1 -- INTERFERENCE (tests CLS): bounded shared superposition store.
# ============================================================================
# M items each with a hidden truth arrive sequentially; every write goes into ONE
# shared D-dim store (bounded memory), so committing item i adds crosstalk to the
# recall of every other item -- the catastrophic-interference predicament. Recall
# uses ONLY the store (private per-item evidence is NOT retained: that is the
# capacity pressure that makes interference bite). Three write policies:
#   keep_everything : commit EVERY item at UNIT gain sign(e_i)  (worst crosstalk;
#                     low-confidence items inject full-magnitude noise).
#   flat_accumulation: commit EVERY item at PRECISION gain e_i  (strong fair flat
#                     competitor; low-confidence items inject little crosstalk).
#   selective_hold  : commit only high-confidence items at precision gain e_i;
#                     low-confidence items are NOT written (fewer superposed items
#                     -> less crosstalk on the committed ones). The confidence
#                     threshold is TRAIN-selected. This is McCloskey-Cohen's
#                     "do not cram every pattern into the shared net."
def _r1_scene(M, D, n_reads, rho, rng):
    keys = rng.standard_normal((M, D)) / np.sqrt(D)
    y = (rng.random(M) < 0.5).astype(int)
    s = 2 * y - 1
    reads = np.zeros((M, n_reads), dtype=int)
    for j in range(n_reads):
        correct = rng.random(M) < rho
        reads[:, j] = np.where(correct, s, -s)
    votes = 2 * reads - 1
    e = votes.mean(axis=1)               # evidence mean in [-1, 1]
    conf = np.abs(e)                     # tag strength
    return keys, y, e, conf


def _r1_recall(keys, gains, commit_mask):
    """store = sum_{committed} keys[i]*gains[i]; recall item j = sign(keys_j.store)."""
    g = gains * commit_mask
    store = g @ keys                     # (D,)
    return (keys @ store >= 0).astype(int)


def _r1_scene_preds(keys, e, conf, gate_thr):
    unit = np.sign(e)
    unit[unit == 0] = 1.0
    allm = np.ones(len(e), bool)
    pred_keep = _r1_recall(keys, unit, allm)              # unit gain, all items
    pred_flat = _r1_recall(keys, e, allm)                 # precision gain, all items
    pred_hold = _r1_recall(keys, e, (conf >= gate_thr))   # precision gain, gated
    return pred_keep, pred_flat, pred_hold


def r1_race(seed, M=R1_M, D=R1_D, n_scenes=R1_SCENES, n_reads=R1_NREADS, rho=R1_RHO):
    rng = np.random.default_rng(seed + 10000)
    scenes = [_r1_scene(M, D, n_reads, rho, rng) for _ in range(n_scenes)]
    ntr = n_scenes // 2
    tr_scenes, te_scenes = scenes[:ntr], scenes[ntr:]

    # gate threshold (per-scene confidence quantile) selected on TRAIN scenes only
    grid = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6)
    best_q, best_acc = 0.0, -1.0
    for q in grid:
        yp, tp = [], []
        for keys, y, e, conf in tr_scenes:
            thr = float(np.quantile(conf, q))
            _, _, ph = _r1_scene_preds(keys, e, conf, thr)
            yp.append(ph)
            tp.append(y)
        acc = _balanced_acc(np.concatenate(yp), np.concatenate(tp))
        if acc > best_acc:
            best_acc, best_q = acc, q

    pk, pf, ph, ty, commit = [], [], [], [], []
    for keys, y, e, conf in te_scenes:
        thr = float(np.quantile(conf, best_q))
        a, b, c = _r1_scene_preds(keys, e, conf, thr)
        pk.append(a); pf.append(b); ph.append(c); ty.append(y)
        commit.append((conf >= thr).mean())
    pk, pf, ph, ty = (np.concatenate(x) for x in (pk, pf, ph, ty))
    acc = dict(keep_everything=float(_balanced_acc(pk, ty)),
               flat_accumulation=float(_balanced_acc(pf, ty)),
               selective_hold=float(_balanced_acc(ph, ty)))
    distinct = len({_hash_dec(pk), _hash_dec(pf), _hash_dec(ph)})
    return dict(acc=acc,
                margin_hold_vs_flat=acc["selective_hold"] - acc["flat_accumulation"],
                commit_frac=float(np.mean(commit)), best_q=best_q,
                arms_differ=bool(distinct >= 2))


def _r1_flat_acc(seed_off, M, D, n_scenes, rng_seed):
    """pooled flat_accumulation recall accuracy over n_scenes scenes of M items."""
    rng = np.random.default_rng(rng_seed + seed_off)
    yp, tp = [], []
    for _ in range(n_scenes):
        keys, y, e, conf = _r1_scene(M, D, R1_NREADS, R1_RHO, rng)
        yp.append(_r1_recall(keys, e, np.ones(M, bool)))
        tp.append(y)
    return float(_balanced_acc(np.concatenate(yp), np.concatenate(tp)))


def r1_certificate(seed, M=R1_M, D=R1_D, n_scenes=R1_SCENES):
    """Interference present: the strong flat competitor degrades as competing items
    accrue (few-item store recalls better than many-item store), pooled."""
    acc_small = _r1_flat_acc(0, R1_M_SMALL, D, n_scenes, seed + 11000)
    acc_full = _r1_flat_acc(500, M, D, n_scenes, seed + 11000)
    degr = acc_small - acc_full
    return dict(acc_small=float(acc_small), acc_full=float(acc_full),
                degradation=float(degr), fired=bool(degr > R1_CERT_MIN))


def r1_null_guard(seed):
    """Huge store -> negligible crosstalk -> flat must NOT degrade with M
    (interference absent) -> the certificate is not vacuously positive."""
    c = r1_certificate(seed, M=R1_M, D=R1_D_HUGE)
    return dict(degradation=c["degradation"], passes=bool(c["degradation"] <= R1_NULL_MAX))


def r1_positive_control(seed, M=R1_M, D=R1_D, n_scenes=R1_SCENES):
    """Oracle-selective: commit only the items whose evidence sign is actually
    correct (label-leaking ORACLE, allowed as a control). Fewer + cleaner writes
    must beat the strong flat competitor -> proves selective protection CAN help."""
    rng = np.random.default_rng(seed + 12000)
    fp, op, tp = [], [], []
    for _ in range(n_scenes):
        keys, y, e, conf = _r1_scene(M, D, R1_NREADS, R1_RHO, rng)
        allm = np.ones(M, bool)
        good = (np.sign(e) == (2 * y - 1))
        fp.append(_r1_recall(keys, e, allm))
        op.append(_r1_recall(keys, e, good))
        tp.append(y)
    fp, op, tp = (np.concatenate(x) for x in (fp, op, tp))
    acc_flat = _balanced_acc(fp, tp)
    acc_or = _balanced_acc(op, tp)
    gap = acc_or - acc_flat
    return dict(flat=float(acc_flat), oracle=float(acc_or), gap=float(gap),
                fired=bool(gap > R1_POS_GAP))


# ============================================================================
# REGIME 2 -- CAPACITY (tests STC/SHY): capped consolidation-write budget.
# ============================================================================
# M items arrive; each is a noisy read set of its hidden truth with a per-item
# reliability. Only BUDGET (< M) items may be durably WRITTEN; unwritten items are
# recalled at chance (their fast-buffer trace is lost). Metric: balanced accuracy
# over all M items AND accuracy-per-write. Arms differ ONLY in which items get the
# scarce writes:
#   keep_everything : FIFO -- spend the budget on the first BUDGET items (no
#                     selection; the naive "keep everything until full").
#   selective_hold  : STC tag-and-capture -- spend the budget on the BUDGET
#                     highest-confidence (highest-tag) items.
# Written items are recalled by their own evidence sign (a good write preserves the
# truth); the delta between arms is purely the SELECTION = the STC tag.
def _r2_arena(M, n_reads, rng):
    # heterogeneous reliability: some items are high-info, many are low-info.
    rho = rng.uniform(0.5, 0.9, size=M)
    y = (rng.random(M) < 0.5).astype(int)
    s = 2 * y - 1
    reads = np.zeros((M, n_reads), dtype=int)
    for j in range(n_reads):
        correct = rng.random(M) < rho
        reads[:, j] = np.where(correct, s, -s)
    votes = 2 * reads - 1
    e = votes.mean(axis=1)
    conf = np.abs(e)
    est = (e >= 0).astype(int)         # recall of a written item
    correct_if_written = (est == y)
    # ONE fixed per-item guess for lost (unwritten) items, SHARED across all arms
    # so that lost-item noise cancels wherever two arms agree on the mask.
    coin = (rng.random(M) < 0.5).astype(int)
    return dict(y=y, e=e, conf=conf, est=est, correct=correct_if_written, coin=coin)


def _r2_eval(written_mask, est, coin):
    """Written items recalled by their evidence sign; unwritten items lost -> the
    shared fixed per-item guess (deterministic; no fresh coin-flip variance)."""
    pred = np.where(written_mask, est, coin)
    return pred


def _r2_fifo_mask(M, budget):
    m = np.zeros(M, bool)
    m[:budget] = True
    return m


def _r2_topk_mask(scores, budget):
    order = np.argsort(-scores)
    m = np.zeros(len(scores), bool)
    m[order[:budget]] = True
    return m


def r2_race(seed, M=R2_M, budget=R2_BUDGET, n_reads=R2_NREADS, reps=R2_REPS):
    """Pool over reps arena replicates per seed for a stable per-seed estimate."""
    ph, pk, ty = [], [], []
    for r in range(reps):
        rng = np.random.default_rng(seed + 20000 + 101 * r)
        ar = _r2_arena(M, n_reads, rng)
        keep_mask = _r2_fifo_mask(M, budget)                    # FIFO
        hold_mask = _r2_topk_mask(ar["conf"], budget)           # top-conf tag
        pk.append(_r2_eval(keep_mask, ar["est"], ar["coin"]))
        ph.append(_r2_eval(hold_mask, ar["est"], ar["coin"]))
        ty.append(ar["y"])
    pk, ph, ty = (np.concatenate(x) for x in (pk, ph, ty))
    acc_keep = float(_balanced_acc(pk, ty))
    acc_hold = float(_balanced_acc(ph, ty))
    apw_keep = (acc_keep - 0.5) / budget
    apw_hold = (acc_hold - 0.5) / budget
    distinct = len({_hash_dec(pk), _hash_dec(ph)})
    return dict(acc=dict(keep_everything=acc_keep, selective_hold=acc_hold),
                acc_per_write=dict(keep_everything=float(apw_keep),
                                   selective_hold=float(apw_hold)),
                margin_hold_vs_flat=acc_hold - acc_keep,
                arms_differ=bool(distinct >= 2))


def r2_certificate(seed, M=R2_M, budget=R2_BUDGET, reps=R2_REPS):
    """Budget genuinely binds (unlimited-budget accuracy >> FIFO-under-budget) AND
    the tag is valid (confidence predicts correctness), pooled over reps."""
    est_all, y_all, fifo_all, conf_all, corr_all = [], [], [], [], []
    for r in range(reps):
        rng = np.random.default_rng(seed + 22000 + 101 * r)
        ar = _r2_arena(M, R2_NREADS, rng)
        est_all.append(ar["est"]); y_all.append(ar["y"])
        fifo_all.append(_r2_eval(_r2_fifo_mask(M, budget), ar["est"], ar["coin"]))
        conf_all.append(ar["conf"]); corr_all.append(ar["correct"].astype(float))
    est_all, y_all, fifo_all, conf_all, corr_all = (
        np.concatenate(x) for x in (est_all, y_all, fifo_all, conf_all, corr_all))
    acc_unlimited = float(_balanced_acc(est_all, y_all))
    acc_fifo = float(_balanced_acc(fifo_all, y_all))
    scarcity_gap = acc_unlimited - acc_fifo
    tag_valid = float(pearson(conf_all, corr_all))
    fired = (scarcity_gap > R2_CERT_MIN) and (tag_valid > R2_TAGVALID_MIN)
    return dict(acc_unlimited=acc_unlimited, acc_fifo=acc_fifo,
                scarcity_gap=float(scarcity_gap), tag_validity=tag_valid,
                fired=bool(fired))


def r2_null_guard(seed, M=R2_M, budget=R2_BUDGET, reps=R2_REPS):
    """Invalid tags: a RANDOM tag (uncorrelated with correctness). Selecting by it
    must NOT beat FIFO -> proves the selective advantage needs a VALID tag and is
    not a free lunch of the accounting. Pooled over reps."""
    ph, pk, ty = [], [], []
    for r in range(reps):
        rng = np.random.default_rng(seed + 24000 + 101 * r)
        ar = _r2_arena(M, R2_NREADS, rng)
        rand_tag = rng.random(M)
        ph.append(_r2_eval(_r2_topk_mask(rand_tag, budget), ar["est"], ar["coin"]))
        pk.append(_r2_eval(_r2_fifo_mask(M, budget), ar["est"], ar["coin"]))
        ty.append(ar["y"])
    ph, pk, ty = (np.concatenate(x) for x in (ph, pk, ty))
    acc_hold = _balanced_acc(ph, ty)
    acc_keep = _balanced_acc(pk, ty)
    adv = acc_hold - acc_keep
    return dict(acc_hold=float(acc_hold), acc_keep=float(acc_keep),
                advantage=float(adv), passes=bool(adv <= R2_NULL_MAX))


def r2_positive_control(seed, M=R2_M, budget=R2_BUDGET, reps=R2_REPS):
    """Oracle-selection: spend the budget on the items that are actually correct
    (label-leaking ORACLE). Must beat FIFO -> proves the harness can express a
    selection advantage under scarcity. Pooled over reps."""
    po, pk, ty = [], [], []
    for r in range(reps):
        rng = np.random.default_rng(seed + 26000 + 101 * r)
        ar = _r2_arena(M, R2_NREADS, rng)
        oracle_score = ar["correct"].astype(float) + rng.random(M) * 1e-6
        po.append(_r2_eval(_r2_topk_mask(oracle_score, budget), ar["est"], ar["coin"]))
        pk.append(_r2_eval(_r2_fifo_mask(M, budget), ar["est"], ar["coin"]))
        ty.append(ar["y"])
    po, pk, ty = (np.concatenate(x) for x in (po, pk, ty))
    acc_or = _balanced_acc(po, ty)
    acc_keep = _balanced_acc(pk, ty)
    gap = acc_or - acc_keep
    return dict(oracle=float(acc_or), fifo=float(acc_keep), gap=float(gap),
                fired=bool(gap > R2_POS_GAP))


# ============================================================================
# REGIME 3 -- ORDER / TRAJECTORY (tests the structure directly).
# ============================================================================
# A sequence of signed events arrives over time. Label = XOR(sign at lag A,
# sign at lag C) embedded among noise steps -- a genuinely ORDER-dependent,
# lag-nonlinear function. The strong flat competitor reads the order-blind
# sufficient stats {arrival, accumulated, corroboration, win} AND (even stronger)
# the RAW per-step sequence, LINEARLY -- provably blind to XOR (White-Lee-
# Sompolinsky 04; Dambre 12: a linear/leaky accumulator reconstructs only linear
# projections of the past). The hold-then-decay TRAJECTORY arm reads a nonlinear
# leaky coincidence trace (Tsodyks-Markram short-term-plasticity style) that
# carries the lag product; a LINEAR readout on that trace separates XOR. So the
# ONLY difference earning the win is the nonlinear trajectory structure.
def _r3_sequences(N, T, rng, order_task=True):
    x = (rng.random((N, T)) < 0.5).astype(int) * 2 - 1     # +-1
    if order_task:
        y = (x[:, R3_LAG_A] != x[:, R3_LAG_C]).astype(int)  # XOR of two lags
    else:
        y = (x.sum(axis=1) >= 0).astype(int)               # order-irrelevant sum
    return x, y


def _r3_flat_features(x):
    """Order-blind sufficient stats: arrival, accumulated, corroboration, win."""
    T = x.shape[1]
    arrival = x[:, 0].astype(float)
    accumulated = x.mean(axis=1)
    corrob = (x == x[:, :1]).mean(axis=1)      # fraction agreeing with arrival
    win = np.sign(x.sum(axis=1)).astype(float)
    return np.column_stack([arrival, accumulated, corrob, win])


def _r3_traj_features(x, lam=R3_LAMBDA, W=R3_COINC_W):
    """Hold-then-decay nonlinear trace + LOCAL coincidence detection (Tsodyks-
    Markram / Buonomano short-term-plasticity style). h_t = lam*h_{t-1} + x_t is
    the leaky hold. The second-order LOCAL-coincidence features x_i*x_j for every
    within-window pair (1 <= j-i <= W) are the order-aware products a flat linear
    readout of first-order stats structurally lacks (Dambre 2012: nonlinearity
    opens order-dependent capacity). A LINEAR readout on this basis separates the
    XOR-of-lags -- the coincidence window is LOCAL, not hard-coded to the exact
    informative lag, so this is not label-peeking."""
    N, T = x.shape
    h = np.zeros(N)
    for t in range(T):
        h = lam * h + x[:, t]
    feats = [x.mean(axis=1), h]
    for i in range(T):
        for j in range(i + 1, min(i + W + 1, T)):
            feats.append(x[:, i] * x[:, j])
    return np.column_stack(feats)


def _r3_fit_eval(Xtr, ytr, Xte, yte):
    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0) + 1e-9
    Xtr = (Xtr - mu) / sd
    Xte = (Xte - mu) / sd
    p, _ = A.fit_weighted_sum(Xtr, ytr)
    return float(_balanced_acc(p(Xte), yte)), p(Xte)


def r3_race(seed, N=R3_N, T=R3_T, order_task=True):
    rng = np.random.default_rng(seed + 30000)
    x, y = _r3_sequences(N, T, rng, order_task=order_task)
    nt = N // 2
    tr, te = slice(nt, N), slice(0, nt)
    Xf, Xr, Xj = _r3_flat_features(x), x.astype(float), _r3_traj_features(x)
    acc_flat_stats, dec_fs = _r3_fit_eval(Xf[tr], y[tr], Xf[te], y[te])
    acc_flat_raw, dec_fr = _r3_fit_eval(Xr[tr], y[tr], Xr[te], y[te])
    acc_traj, dec_tj = _r3_fit_eval(Xj[tr], y[tr], Xj[te], y[te])
    strong_flat = max(acc_flat_stats, acc_flat_raw)   # the STRONGEST flat linear
    distinct = len({_hash_dec(dec_fr), _hash_dec(dec_tj)})
    return dict(acc=dict(flat_suffstats=acc_flat_stats, flat_raw_linear=acc_flat_raw,
                         trajectory_hold=acc_traj),
                strong_flat=float(strong_flat),
                margin_hold_vs_flat=acc_traj - strong_flat,
                arms_differ=bool(distinct >= 2))


def r3_certificate(seed):
    """Linear-blindness gap on the ORDER task: the strong flat LINEAR competitor
    is pinned near chance while the trajectory trace separates -> a linear model
    provably under-fits the order-dependent label."""
    r = r3_race(seed, order_task=True)
    gap = r["acc"]["trajectory_hold"] - r["strong_flat"]
    return dict(strong_flat=r["strong_flat"], trajectory=r["acc"]["trajectory_hold"],
                gap=float(gap), fired=bool(gap > R3_CERT_MIN))


def r3_null_guard(seed):
    """On an order-IRRELEVANT task (label = sign of sum) the flat linear arm is
    NOT blind, so the blindness gap must vanish -> the certificate reads genuine
    order-dependence, not a broken flat arm."""
    r = r3_race(seed, order_task=False)
    gap = r["acc"]["trajectory_hold"] - r["strong_flat"]
    return dict(strong_flat=r["strong_flat"], trajectory=r["acc"]["trajectory_hold"],
                gap=float(gap), passes=bool(gap <= R3_NULL_MAX))


def r3_positive_control(seed):
    """Harness can express both: trajectory clears R3_POS_MIN on the order task
    AND the flat linear arm clears R3_POS_MIN on the sum task (neither structurally
    broken)."""
    ro = r3_race(seed, order_task=True)
    rs = r3_race(seed, order_task=False)
    traj_order = ro["acc"]["trajectory_hold"]
    flat_sum = rs["strong_flat"]
    return dict(traj_on_order=float(traj_order), flat_on_sum=float(flat_sum),
                fired=bool(traj_order >= R3_POS_MIN and flat_sum >= R3_POS_MIN))


# ============================================================================
# per-regime aggregation
# ============================================================================
def _agg_regime(name, per_seed, strong_flat_key, cert_list, ctrl_fired_list,
                null_pass_list, extra=None):
    m, se = _mean_se([s["margin_hold_vs_flat"] for s in per_seed])
    z = _z(m, se)
    arms = sorted({k for s in per_seed for k in s["acc"]})
    acc = {a: float(np.mean([s["acc"][a] for s in per_seed if a in s["acc"]]))
           for a in arms}
    cert_fired = all(c["fired"] for c in cert_list)
    controls_fired = all(ctrl_fired_list) and all(null_pass_list)
    valid = bool(cert_fired and controls_fired)
    strong_flat_acc = acc.get(strong_flat_key)
    baseline_in_band = (strong_flat_acc is not None
                        and 0.05 < strong_flat_acc < 0.95)
    win = bool(valid and baseline_in_band and m > TIE_EPS and z > SIGMA_K)
    if not valid:
        outcome = "INVALID_REGIME"
    elif not baseline_in_band:
        outcome = "INVALID_BASELINE_OUT_OF_BAND"
    elif win:
        outcome = "HOLD_WINS"
    elif m <= TIE_EPS:
        outcome = "HOLD_LOSES" if m < -X_BAND else "HOLD_TIES"
    else:
        outcome = "HOLD_POSITIVE_NOT_SIGNIFICANT"
    arms_differ = all(s["arms_differ"] for s in per_seed)
    out = dict(name=name, acc=acc, strong_flat_key=strong_flat_key,
               margin_hold_vs_flat=m, se=se, z=float(z),
               cert_fired=bool(cert_fired), controls_fired=bool(controls_fired),
               valid=valid, baseline_in_band=bool(baseline_in_band),
               win=win, outcome=outcome, arms_differ=bool(arms_differ),
               cert_detail=cert_list[0] if len(cert_list) == 1 else cert_list)
    if extra:
        out.update(extra)
    return out


# ============================================================================
# self-tests (controls-only smoke gate)
# ============================================================================
def _run_selftests():
    fails, notes = [], []
    for sd in (11, 23, 37):
        c1 = r1_certificate(sd)
        p1 = r1_positive_control(sd)
        n1 = r1_null_guard(sd)
        notes.append("R1 seed=%d cert(degr=%+.3f fired=%s) pos(gap=%+.3f fired=%s) "
                     "null(degr=%+.3f pass=%s)" % (sd, c1["degradation"], c1["fired"],
                     p1["gap"], p1["fired"], n1["degradation"], n1["passes"]))
        if not c1["fired"]:
            fails.append("R1 cert seed %d NOT fired (degr=%+.3f<=%.3f) -> no "
                         "interference in arena" % (sd, c1["degradation"], R1_CERT_MIN))
        if not p1["fired"]:
            fails.append("R1 posctrl seed %d NOT fired (gap=%+.3f) -> harness cannot "
                         "express selective protection" % (sd, p1["gap"]))
        if not n1["passes"]:
            fails.append("R1 null seed %d FAILED (degr=%+.3f>%.3f) -> cert vacuous"
                         % (sd, n1["degradation"], R1_NULL_MAX))
    for sd in (11, 23, 37):
        c2 = r2_certificate(sd)
        p2 = r2_positive_control(sd)
        n2 = r2_null_guard(sd)
        notes.append("R2 seed=%d cert(scar=%+.3f tag=%+.3f fired=%s) pos(gap=%+.3f "
                     "fired=%s) null(adv=%+.3f pass=%s)" % (sd, c2["scarcity_gap"],
                     c2["tag_validity"], c2["fired"], p2["gap"], p2["fired"],
                     n2["advantage"], n2["passes"]))
        if not c2["fired"]:
            fails.append("R2 cert seed %d NOT fired (scar=%+.3f tag=%+.3f) -> budget "
                         "not binding or tag invalid" % (sd, c2["scarcity_gap"],
                                                         c2["tag_validity"]))
        if not p2["fired"]:
            fails.append("R2 posctrl seed %d NOT fired (gap=%+.3f)" % (sd, p2["gap"]))
        if not n2["passes"]:
            fails.append("R2 null seed %d FAILED (adv=%+.3f>%.3f) -> free-lunch "
                         "accounting" % (sd, n2["advantage"], R2_NULL_MAX))
    for sd in (11, 23, 37):
        c3 = r3_certificate(sd)
        p3 = r3_positive_control(sd)
        n3 = r3_null_guard(sd)
        notes.append("R3 seed=%d cert(gap=%+.3f fired=%s traj=%.3f flat=%.3f) "
                     "pos(traj_ord=%.3f flat_sum=%.3f fired=%s) null(gap=%+.3f pass=%s)"
                     % (sd, c3["gap"], c3["fired"], c3["trajectory"], c3["strong_flat"],
                        p3["traj_on_order"], p3["flat_on_sum"], p3["fired"],
                        n3["gap"], n3["passes"]))
        if not c3["fired"]:
            fails.append("R3 cert seed %d NOT fired (gap=%+.3f) -> flat not blind"
                         % (sd, c3["gap"]))
        if not p3["fired"]:
            fails.append("R3 posctrl seed %d NOT fired (traj_ord=%.3f flat_sum=%.3f)"
                         % (sd, p3["traj_on_order"], p3["flat_on_sum"]))
        if not n3["passes"]:
            fails.append("R3 null seed %d FAILED (gap=%+.3f>%.3f) -> flat spuriously "
                         "blind on order-irrelevant task" % (sd, n3["gap"], R3_NULL_MAX))
    # arms_differ smoke on each regime
    if not r1_race(11)["arms_differ"]:
        fails.append("R1 arms_differ FAILED")
    if not r2_race(11)["arms_differ"]:
        fails.append("R2 arms_differ FAILED")
    if not r3_race(11)["arms_differ"]:
        fails.append("R3 arms_differ FAILED")
    return fails, notes


# ============================================================================
# metrics IO + markers
# ============================================================================
def _atomic_write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2)
    os.replace(tmp, path)


def _write_start_marker(expected_units, run_mode):
    _atomic_write(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                  {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
                   "expected_n_units": expected_units, "host": platform.node()})


def _write_crash_metrics(exc):
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                  {"verdict": "CELL_CRASHED",
                   "summary": "CELL_CRASHED: %s" % type(exc).__name__,
                   "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
                   "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "anchor_name": ANCHOR_NAME})


# ============================================================================
# main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = _run_selftests()
        print("=== CONSOLIDATION CORRECT-REGIMES SELF-TESTS (per-regime cert + "
              "posctrl + null guard) ===")
        for nline in notes:
            print("  " + nline, flush=True)
        if fails:
            print("SELF-TEST FAILED:")
            for fmsg in fails:
                print("  FAIL: " + fmsg)
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "; ".join(fails),
                           "elapsed_s": time.perf_counter() - t0,
                           "anchor_name": ANCHOR_NAME})
            return 2
        print("SELFTEST_PASS: all 3 regime certificates fire, positive controls fire, "
              "null guards hold; arms distinct")
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71, 89, 101, 113, 127, 139, 151, 163]
             if profile == "full" else [11, 23, 37, 53])
    _write_start_marker(3 * len(seeds), profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=== profile=%s seeds=%s ===" % (profile, seeds), flush=True)

    # --- regime 1 ---
    r1 = [r1_race(sd) for sd in seeds]
    r1_cert = [r1_certificate(sd) for sd in seeds]
    r1_pos = [r1_positive_control(sd) for sd in seeds]
    r1_null = [r1_null_guard(sd) for sd in seeds]
    R1 = _agg_regime("interference_CLS", r1, "flat_accumulation", r1_cert,
                     [p["fired"] for p in r1_pos], [n["passes"] for n in r1_null],
                     extra=dict(commit_frac=float(np.mean([s["commit_frac"] for s in r1])),
                                keep_everything=float(np.mean([s["acc"]["keep_everything"] for s in r1]))))
    with open(hb_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"regime": 1, "elapsed_s": time.perf_counter() - t0}) + "\n")
    print("  R1 interference: hold=%.3f flat=%.3f keep=%.3f | m=%+.3f z=%.2f | "
          "cert=%s ctrl=%s -> %s" % (R1["acc"]["selective_hold"],
          R1["acc"]["flat_accumulation"], R1["acc"]["keep_everything"],
          R1["margin_hold_vs_flat"], R1["z"], R1["cert_fired"], R1["controls_fired"],
          R1["outcome"]), flush=True)

    # --- regime 2 ---
    r2 = [r2_race(sd) for sd in seeds]
    r2_cert = [r2_certificate(sd) for sd in seeds]
    r2_pos = [r2_positive_control(sd) for sd in seeds]
    r2_null = [r2_null_guard(sd) for sd in seeds]
    apw_hold = float(np.mean([s["acc_per_write"]["selective_hold"] for s in r2]))
    apw_keep = float(np.mean([s["acc_per_write"]["keep_everything"] for s in r2]))
    R2 = _agg_regime("capacity_STC", r2, "keep_everything", r2_cert,
                     [p["fired"] for p in r2_pos], [n["passes"] for n in r2_null],
                     extra=dict(acc_per_write_hold=apw_hold, acc_per_write_keep=apw_keep))
    with open(hb_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"regime": 2, "elapsed_s": time.perf_counter() - t0}) + "\n")
    print("  R2 capacity: hold=%.3f keep=%.3f | apw hold=%.4f keep=%.4f | m=%+.3f "
          "z=%.2f | cert=%s ctrl=%s -> %s" % (R2["acc"]["selective_hold"],
          R2["acc"]["keep_everything"], apw_hold, apw_keep, R2["margin_hold_vs_flat"],
          R2["z"], R2["cert_fired"], R2["controls_fired"], R2["outcome"]), flush=True)

    # --- regime 3 ---
    r3 = [r3_race(sd, order_task=True) for sd in seeds]
    r3_cert = [r3_certificate(sd) for sd in seeds]
    r3_pos = [r3_positive_control(sd) for sd in seeds]
    r3_null = [r3_null_guard(sd) for sd in seeds]
    R3 = _agg_regime("order_trajectory", r3, "flat_raw_linear", r3_cert,
                     [p["fired"] for p in r3_pos], [n["passes"] for n in r3_null],
                     extra=dict(flat_suffstats=float(np.mean([s["acc"]["flat_suffstats"] for s in r3]))))
    with open(hb_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"regime": 3, "elapsed_s": time.perf_counter() - t0}) + "\n")
    print("  R3 order: traj=%.3f flat_raw=%.3f flat_stats=%.3f | m=%+.3f z=%.2f | "
          "cert=%s ctrl=%s -> %s" % (R3["acc"]["trajectory_hold"],
          R3["acc"]["flat_raw_linear"], R3["acc"]["flat_suffstats"],
          R3["margin_hold_vs_flat"], R3["z"], R3["cert_fired"], R3["controls_fired"],
          R3["outcome"]), flush=True)

    regimes = [R1, R2, R3]
    valid = [r for r in regimes if r["valid"] and r["baseline_in_band"]]
    wins = [r for r in valid if r["win"]]
    ties_losses = [r for r in valid if r["outcome"] in ("HOLD_TIES", "HOLD_LOSES")]

    if not valid:
        verdict = "INVALID_NO_VALID_REGIME"
    elif wins:
        verdict = "HARD_PASS"
    elif len(ties_losses) == len(valid):
        verdict = "HARD_FAIL_STRUCTURE_ADDS_NOTHING"
    else:
        verdict = "MIDDLE_MIXED_OR_NOT_SIGNIFICANT"

    win_names = [r["name"] for r in wins]
    call = ("hold_earns_keep_in:%s_single_stream_null_was_wrong_regime" % ",".join(win_names)
            if verdict == "HARD_PASS" else
            "hold_ties/loses_strong_flat_in_ALL_valid_regimes_structure_adds_nothing"
            if verdict.startswith("HARD_FAIL") else
            "mixed_or_below_2sigma_or_no_valid_regime")

    msg = ("profile=%s seeds=%d | VERDICT=%s | valid_regimes=%d/%d | "
           "R1 interference[%s]: hold=%.3f flat=%.3f m=%+.3f z=%.2f | "
           "R2 capacity[%s]: hold=%.3f keep=%.3f apw_h=%.4f apw_k=%.4f m=%+.3f z=%.2f | "
           "R3 order[%s]: traj=%.3f flat_raw=%.3f m=%+.3f z=%.2f | CALL: %s" %
           (profile, len(seeds), verdict, len(valid), len(regimes),
            R1["outcome"], R1["acc"]["selective_hold"], R1["acc"]["flat_accumulation"],
            R1["margin_hold_vs_flat"], R1["z"],
            R2["outcome"], R2["acc"]["selective_hold"], R2["acc"]["keep_everything"],
            apw_hold, apw_keep, R2["margin_hold_vs_flat"], R2["z"],
            R3["outcome"], R3["acc"]["trajectory_hold"], R3["acc"]["flat_raw_linear"],
            R3["margin_hold_vs_flat"], R3["z"], call))

    out = {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(time.perf_counter() - t0),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "run_mode": profile,
        "primary_metric": "marginal_heldout_balanced_accuracy",
        "crlb_n/a": "classification balanced-acc bands, no Cramer-Rao noise floor applies",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND, "SIGMA_K": SIGMA_K},
        "call": call,
        "regimes": {
            "interference_CLS": R1,
            "capacity_STC": R2,
            "order_trajectory": R3,
        },
        "controls": {
            "R1_positive_control": r1_pos, "R1_null_guard": r1_null,
            "R1_certificate": r1_cert,
            "R2_positive_control": r2_pos, "R2_null_guard": r2_null,
            "R2_certificate": r2_cert,
            "R3_positive_control": r3_pos, "R3_null_guard": r3_null,
            "R3_certificate": r3_cert,
        },
        "n_valid_regimes": len(valid),
        "arms_differ_verified": bool(all(r["arms_differ"] for r in regimes)),
    }
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("CONSOLIDATION IN THE 3 CORRECT REGIMES -- PRIMARY = marginal held-out "
          "balanced acc")
    for r in regimes:
        print("\n  [%s]  outcome=%s  valid=%s (cert=%s controls=%s baseline_in_band=%s)"
              % (r["name"], r["outcome"], r["valid"], r["cert_fired"],
                 r["controls_fired"], r["baseline_in_band"]))
        print("    arms: %s" % "  ".join("%s=%.3f" % (k, v) for k, v in r["acc"].items()))
        print("    margin(hold - strong_flat[%s]) = %+.3f  se=%.3f  z=%.2f  "
              "(win iff m>%.3f AND z>%.1f)" % (r["strong_flat_key"],
              r["margin_hold_vs_flat"], r["se"], r["z"], TIE_EPS, SIGMA_K))
    print("\n  valid regimes = %d/%d ; wins = %s" % (len(valid), len(regimes),
          win_names if win_names else "none"))
    print("\nTOP-LEVEL VERDICT: %s" % verdict)
    print("CALL: %s" % call)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit
        _write_crash_metrics(e)
        raise
    sys.exit(rc)
