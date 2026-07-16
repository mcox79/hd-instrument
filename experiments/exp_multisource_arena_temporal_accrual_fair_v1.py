"""FAIR temporal HOLD/recurrence test -- genuine sequential-evidence accrual arena.

WHY THIS CELL EXISTS (fairness audit skunkworks a960675f, fix #3). In the prior
temporal cells (exp_multisource_arena_temporal_hold_recover_v1, commit 2d32312fa;
exp_multisource_arena_phase_boundary_v1, commit e9b815405) the "delay" merely
SPLIT an already-fixed corroboration set built once at arena construction. Truth
was determined at build time and the window/arrival split was a truth-independent
random partition of a static feature, so measured static_full (0.843) was BELOW
static_arrival (0.859): WINDOWING ADDED NOISE, not info -> temporal_info_gain <= 0
BY CONSTRUCTION. The hold "tying/losing decide_at_arrival" there was therefore an
UNINTERPRETABLE non-result: the hold was never given genuine incremental info to
exploit. This cell gives it a fair shot.

WHAT IS DIFFERENT HERE. Evidence for each claim ARRIVES SEQUENTIALLY as independent
noisy reads of a hidden truth. At ARRIVAL (t=0) only a few reads are visible, so
the arrival estimate is genuinely UNDER-informed; more corroborating reads accrue
over the hold window and genuinely sharpen the truth estimate. A tunable fraction
(p_noise) of claims are DISTRACTORS whose arrival report is a CONFIDENT-looking red
herring that later accrual fails to corroborate -- the synaptic-tagging-and-capture
/ CLS structure where a tag set early must be captured by sustained corroboration
or it decays (notes consolidation_gate_signal_mechanism_and_integration_2026-07-16).

CERTIFICATE-FIRST (precondition, analogous to the conjunction non-additivity cert).
temporal_info_gain = keep_everything(static_full) - decide_at_arrival(static_arrival)
MUST be > CERT_MIN by construction: a model that WAITS for the window is genuinely
more accurate than one deciding at arrival. If the certificate does NOT fire, the
arena is still artificial and the hold verdict is not trusted (INVALID_ARENA). A
NULL guard (accrual = pure noise) proves the certificate is not vacuously positive:
there tig must stay <= NULL_MAX even though both arms are well above chance.

CONTROLS (guard a vacuous/rigged race):
  (i)  temporal_info_gain > CERT_MIN certificate  (the precondition)
  (ii) hold-ORACLE positive control: a regime where arrival is pure noise and truth
       = accrual majority; an oracle thresholding accrual PROVABLY beats decide-at-
       arrival (pinned near chance). Proves the harness CAN express a temporal
       advantage IF it is real.
  (iii) NULL/must-fail guard: accrual = pure noise -> certificate must NOT fire.
  (iv) linear guard: clean regime -> flat competitor recovers a strong separator
       (a hold "win" can never be a broken-competitor artifact).

ANTI-RIG. The arena is NOT tuned to make the hold win. The hold uses the SAME
precision-weighted score core as keep_everything (M._precision_weights); the ONLY
difference is the provisional-hold-then-recover/decay BRANCH structure. If the hold
STILL ties/loses decide_at_arrival even WITH certified accruing info, that is a real
FAIRLY-measured bound and is reported honestly as HARD_FAIL. keep_everything (the
strong flat full-window accumulator) is reported alongside: if the hold beats
arrival but only TIES keep_everything, the localization is "hold uses the time axis
but selective consolidation adds nothing a flat accumulation of the same accrued
evidence cannot" -- the honest expected outcome for linearly-separable evidence.

PRE-REG BANDS (marginal held-out balanced accuracy; multi-seed paired margins):
  TIE_EPS = 0.010 ; X_BAND = 0.030 ; SIGMA_K = 2.0
  margin  = hold - decide_at_arrival ; z = mean(margin) / se(margin) over seeds
  HARD_PASS : certificate fires + all controls fire + margin > TIE_EPS AND z > 2
              (the brain-faithful hold beats decide_at_arrival by >2sigma -> the
               hold machinery earns its keep on genuine accruing info).
  HARD_FAIL : certificate fires + controls fire + margin <= TIE_EPS
              (hold ties [_TIES] or loses [< -X_BAND -> _LOSES] even WITH genuine
               accruing info -> the hold adds nothing beyond a simple gate; a real,
               fairly-measured bound -> drill mechanism + brain-check).
  MIDDLE    : certificate + controls fire, margin > TIE_EPS but z <= 2 (positive
              but not >2sigma significant).
  INVALID   : certificate did not fire OR a control did not fire OR baseline
              out-of-band (uninterpretable; the arena is still artificial -- fix it).

Pure-Python (numpy only). Reuses A.fit_weighted_sum + A._balanced_acc + A.pearson +
M._precision_weights (the VET'd arena+menu code). No substrate atoms, no torch, no
queue/GPU, no origin push. Runs inline in seconds. Multi-seed, multi operating-point
sweep (identical splits across all arms per seed/point).

Run:
  python experiments/exp_multisource_arena_temporal_accrual_fair_v1.py --self-test
  python experiments/exp_multisource_arena_temporal_accrual_fair_v1.py --profile smoke
  python experiments/exp_multisource_arena_temporal_accrual_fair_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (numpy design/validity cell; queue/substrate mandates n/a):
# - except SystemExit raised BEFORE except Exception (no BaseException)
# - no bare except; deterministic FIXED-int seeds (no hash()-derived seeds); sorted(set())
# - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
# - start-marker + crash-diagnostic + per-unit heartbeat written
# - arms_differ: hold vs keep_everything vs decide_at_arrival decisions hash-checked distinct
# - baseline-in-band: keep_everything marginal checked in (0.05, 0.95)
# - discriminator survives scale: full-N multi-seed paired margin+z is the discriminator;
#   smoke uses the full arm set at reduced-N; positive control fires the temporal
#   discriminator explicitly and null guard proves the certificate is not vacuous
# - CRLB: crlb_n/a = "classification balanced-acc bands, no Cramer-Rao noise floor applies"
# - all reported numbers MEASURED@ this run's metrics.json unless tagged else
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

# --- reuse the VET'd arena + menu fit code verbatim -------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_multisource_arena_v1 as A  # noqa: E402
import exp_multisource_arena_combination_menu_v1 as M  # noqa: E402

ANCHOR_NAME = "multisource_arena_temporal_accrual_fair_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_temporal_accrual_fair_v1")

_balanced_acc = A._balanced_acc
pearson = A.pearson

# ---- pre-registered bands --------------------------------------------------
TIE_EPS = 0.010
X_BAND = 0.030
SIGMA_K = 2.0
CERT_MIN = 0.030          # temporal_info_gain must exceed this to certify accruing info
NULL_MAX = 0.030          # null-guard tig must stay <= this (certificate not vacuous)
POSCTRL_MIN_GAP = 0.15    # oracle must beat decide-at-arrival by at least this
POSCTRL_ARR_MAX = 0.62    # ... with decide-at-arrival pinned near chance

# ---- evidence schedule (set A PRIORI, not swept to favour the window) ------
# n_arrival reads visible at t0; n_accrual further independent reads accrue within
# the hold window. More reads = lower-variance truth estimate -> keep_everything
# genuinely beats decide_at_arrival by construction (the certificate).
N_ARRIVAL = 3
N_ACCRUAL = 7

# ---- operating-point sweep (crossover region included) ---------------------
# p_noise = fraction of DISTRACTOR claims (confident misleading arrival, no
# corroboration). rho_arr = per-read arrival reliability, rho_acc = per-read
# accrual reliability. The BASE point (crossover) drives the primary verdict.
OPERATING_POINTS = [
    {"name": "clean", "p_noise": 0.00, "rho_arr": 0.75, "rho_acc": 0.70},
    {"name": "low_noise", "p_noise": 0.15, "rho_arr": 0.70, "rho_acc": 0.70},
    {"name": "crossover", "p_noise": 0.30, "rho_arr": 0.65, "rho_acc": 0.70},
    {"name": "high_noise", "p_noise": 0.45, "rho_arr": 0.60, "rho_acc": 0.70},
]
BASE_NAME = "crossover"

FEAT_FULL = ["arr_mean", "acc_mean", "win_mean", "corrob"]


# ============================================================================
# genuine sequential-evidence temporal arena
# ============================================================================
def build_accrual_arena(K, n_arr, n_acc, rho_arr, rho_acc, p_noise, rng,
                        spurious_bias=1):
    """Each claim c: hidden truth y_c ~ Bernoulli(0.5). n_arr arrival reads at t0
    and n_acc accrual reads over the window, each an INDEPENDENT noisy read of y_c.

    GENUINE claims: every read is correct w.p. its reliability (arrival + accrual
    both informative; more reads => sharper estimate).
    DISTRACTOR claims (fraction p_noise): the ARRIVAL reads are a confident RED
    HERRING -- they report `spurious_bias` w.p. rho_arr REGARDLESS of truth, so
    arrival evidence is uninformative-yet-confident; the ACCRUAL reads are honest
    (corroboration materialises over time and corrects the misleading arrival).

    So the arrival estimate is genuinely under-informed and later evidence genuinely
    improves the truth estimate -> temporal_info_gain > 0 by construction. Delays
    carry no label info (reads are exchangeable within arrival/accrual pools)."""
    y = (rng.random(K) < 0.5).astype(int)
    spurious = (rng.random(K) < p_noise)
    arr = np.zeros((K, n_arr), dtype=int)
    for j in range(n_arr):
        correct = rng.random(K) < rho_arr
        genuine_vote = np.where(correct, y, 1 - y)
        conf = rng.random(K) < rho_arr
        spur_vote = np.where(conf, spurious_bias, 1 - spurious_bias)
        arr[:, j] = np.where(spurious, spur_vote, genuine_vote)
    acc = np.zeros((K, n_acc), dtype=int)
    for j in range(n_acc):
        correct = rng.random(K) < rho_acc
        acc[:, j] = np.where(correct, y, 1 - y)
    return dict(y=y, spurious=spurious, arr=arr, acc=acc)


def features(data):
    """Per-claim evidence features (votes in {-1,+1}). arr_mean/arr_absconf are the
    arrival sufficient stats (only info available at t0); acc_mean/win_mean/corrob
    require the accrued window. corrob = does accrual corroborate the arrival lean
    (trajectory signal a flat mean discards)."""
    arr_v = 2 * data["arr"] - 1
    acc_v = 2 * data["acc"] - 1
    arr_mean = arr_v.mean(axis=1)
    acc_mean = acc_v.mean(axis=1)
    win_mean = np.concatenate([arr_v, acc_v], axis=1).mean(axis=1)
    arr_absconf = np.abs(arr_mean)
    arr_sign = np.sign(arr_mean)
    arr_sign[arr_sign == 0] = 1.0
    corrob = arr_sign * acc_mean
    return dict(arr_mean=arr_mean, acc_mean=acc_mean, win_mean=win_mean,
                arr_absconf=arr_absconf, corrob=corrob)


def _std_on(X, tr):
    mu = X[tr].mean(axis=0)
    sd = X[tr].std(axis=0) + 1e-9
    return (X - mu) / sd


# ============================================================================
# hold_recover -- the brain-faithful temporal cascade (novel form)
# ============================================================================
def fit_hold_recover(X_arr_tr, X_full_tr, ytr, cols):
    """Brain-faithful CLS provisional-hold-then-recover cascade, built on the SAME
    precision-weighted score core as keep_everything (M._precision_weights + NP
    threshold) so the ONLY thing distinguishing this arm from the flat full-window
    competitor is the TEMPORAL BRANCH STRUCTURE. X_arr and X_full share columns and
    differ ONLY in the accrued columns (arrival proxies vs windowed values):
      s_arr = X_arr @ w   (provisional decision at ARRIVAL, under-informed)
      s_win = X_full @ w  (decision after HOLDING the window)
      1. provisional at arrival: prov = (s_arr >= tau)
      2. RECOVER: a provisionally-discarded claim whose accrued corroboration
         contribution crosses a recover-threshold is CONSOLIDATED (1).
      3. DECAY: a provisionally-kept claim whose accrued corroboration collapses
         below a decay-threshold DECAYS unsupported -> DISCARD (0).
    Recover/decay percentiles are TRAIN-SELECTED (max train balanced-acc); the score
    core + tau stay principled. Returns n_recovered/n_decayed diagnostics."""
    w, mu1, mu0 = M._precision_weights(X_full_tr, ytr)
    base = float(np.clip(ytr.mean(), 1e-3, 1 - 1e-3))
    mid = 0.5 * float(np.dot(w, mu1 + mu0))
    tau = mid - np.log(base / (1 - base))

    ac, cb = cols["acc_mean"], cols["corrob"]
    rec_contr_tr = w[ac] * X_full_tr[:, ac] + w[cb] * X_full_tr[:, cb]

    def make(rec_q, decay_q):
        rec_hi = float(np.quantile(rec_contr_tr, rec_q))
        rec_lo = float(np.quantile(rec_contr_tr, decay_q))

        def decide(X_arr, X_full, want_diag=False):
            s_arr = X_arr @ w
            rec_c = w[ac] * X_full[:, ac] + w[cb] * X_full[:, cb]
            prov = (s_arr >= tau).astype(int)
            dec = prov.copy()
            recovered = (prov == 0) & (rec_c >= rec_hi)
            dec[recovered] = 1
            decayed = (prov == 1) & (rec_c <= rec_lo)
            dec[decayed] = 0
            if want_diag:
                return dec.astype(int), int(recovered.sum()), int(decayed.sum())
            return dec.astype(int)
        return decide

    best_cfg, best_acc = None, -1.0
    for rec_q in (0.55, 0.70, 0.85):
        for decay_q in (0.15, 0.30):
            dec = make(rec_q, decay_q)
            acc = _balanced_acc(dec(X_arr_tr, X_full_tr), ytr)
            if acc > best_acc:
                best_acc, best_cfg = acc, (rec_q, decay_q)
    decider = make(*best_cfg)
    _, n_rec, n_dec = decider(X_arr_tr, X_full_tr, want_diag=True)
    return decider, dict(rec_q=best_cfg[0], decay_q=best_cfg[1],
                         train_bal_acc=float(best_acc),
                         n_recovered_train=int(n_rec), n_decayed_train=int(n_dec))


# ============================================================================
# per (operating-point, seed) race -- identical split across all arms
# ============================================================================
def _hash_dec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()


def race_point_seed(op, seed, K, n_arr=N_ARRIVAL, n_acc=N_ACCRUAL):
    rng = np.random.default_rng(seed)
    data = build_accrual_arena(K, n_arr, n_acc, op["rho_arr"], op["rho_acc"],
                               op["p_noise"], rng)
    f = features(data)
    y = data["y"]

    idx = rng.permutation(K)
    n_test = K // 2
    test_idx, train_idx = idx[:n_test], idx[n_test:]

    # arrival-only readout (2 arrival sufficient stats)
    Xa_raw = np.column_stack([f["arr_mean"], f["arr_absconf"]])
    Xa = _std_on(Xa_raw, train_idx)
    # full-window readout (all accrued features)
    Xf_raw = np.column_stack([f[n] for n in FEAT_FULL])
    Xf = _std_on(Xf_raw, train_idx)
    cols = {n: i for i, n in enumerate(FEAT_FULL)}
    # hold arrival proxy IN FULL COLUMNS: acc/corrob unknown at t0 (=0), win ~ arr_mean.
    # Standardized with the SAME train stats as Xf so s_arr and s_win share scale.
    Xarr_full_raw = np.column_stack([f["arr_mean"], np.zeros(K),
                                     f["arr_mean"], np.zeros(K)])
    mu = Xf_raw[train_idx].mean(axis=0)
    sd = Xf_raw[train_idx].std(axis=0) + 1e-9
    Xarr_full = (Xarr_full_raw - mu) / sd

    ytr, yte = y[train_idx], y[test_idx]
    preds = {}
    p, _ = A.fit_weighted_sum(Xa[train_idx], ytr)
    preds["decide_at_arrival"] = p(Xa[test_idx])
    p, _ = A.fit_weighted_sum(Xf[train_idx], ytr)
    preds["keep_everything"] = p(Xf[test_idx])
    dec, hinfo = fit_hold_recover(Xarr_full[train_idx], Xf[train_idx], ytr, cols)
    preds["hold_recover"] = dec(Xarr_full[test_idx], Xf[test_idx])

    acc = {k: float(_balanced_acc(v, yte)) for k, v in preds.items()}
    distinct = len({_hash_dec(preds[k]) for k in preds})
    return dict(acc=acc,
                margin_hold_vs_arrival=acc["hold_recover"] - acc["decide_at_arrival"],
                margin_hold_vs_keep=acc["hold_recover"] - acc["keep_everything"],
                temporal_info_gain=acc["keep_everything"] - acc["decide_at_arrival"],
                arms_differ=bool(distinct >= 2),
                spurious_frac=float(data["spurious"].mean()),
                base_rate=float(y.mean()), hold_info=hinfo)


# ============================================================================
# controls (guard a vacuous / rigged race)
# ============================================================================
def positive_control(seed, K=1400):
    """ST-B analog. Arrival = pure noise (rho_arr=0.5); truth recoverable ONLY from
    accrual. An oracle thresholding accrual majority PROVABLY beats decide-at-arrival
    (pinned near chance). Proves the harness can express a temporal advantage."""
    rng = np.random.default_rng(seed + 90000)
    data = build_accrual_arena(K, N_ARRIVAL, N_ACCRUAL, 0.5, 0.75, 0.0, rng)
    f = features(data)
    y = data["y"]
    idx = rng.permutation(K)
    nt = K // 2
    te, tr = idx[:nt], idx[nt:]
    Xa = _std_on(np.column_stack([f["arr_mean"], f["arr_absconf"]]), tr)
    p, _ = A.fit_weighted_sum(Xa[tr], y[tr])
    acc_arr = _balanced_acc(p(Xa[te]), y[te])
    acc_oracle = _balanced_acc((f["acc_mean"][te] >= 0).astype(int), y[te])
    fired = (acc_oracle - acc_arr >= POSCTRL_MIN_GAP) and (acc_arr < POSCTRL_ARR_MAX)
    return dict(arrival=float(acc_arr), oracle=float(acc_oracle),
                gap=float(acc_oracle - acc_arr), fired=bool(fired))


def null_guard(seed, K=1400):
    """Must-fail. Accrual = PURE NOISE (rho_acc=0.5); arrival stays informative.
    The certificate temporal_info_gain must NOT fire (tig <= NULL_MAX) even though
    BOTH arms sit well above chance -> proves the certificate is not vacuously
    positive (it reads the DIFFERENCE, not the level)."""
    rng = np.random.default_rng(seed + 70000)
    data = build_accrual_arena(K, N_ARRIVAL, N_ACCRUAL, 0.65, 0.50, 0.0, rng)
    f = features(data)
    y = data["y"]
    idx = rng.permutation(K)
    nt = K // 2
    te, tr = idx[:nt], idx[nt:]
    Xa = _std_on(np.column_stack([f["arr_mean"], f["arr_absconf"]]), tr)
    Xf = _std_on(np.column_stack([f[n] for n in FEAT_FULL]), tr)
    p, _ = A.fit_weighted_sum(Xa[tr], y[tr])
    acc_arr = _balanced_acc(p(Xa[te]), y[te])
    p, _ = A.fit_weighted_sum(Xf[tr], y[tr])
    acc_full = _balanced_acc(p(Xf[te]), y[te])
    tig = acc_full - acc_arr
    return dict(arrival=float(acc_arr), full=float(acc_full),
                tig_null=float(tig), passes=bool(tig <= NULL_MAX))


def linear_guard(seed, K=1400):
    """Clean regime -> the flat full-window competitor MUST recover a strong
    separator. Guards the anti-rig: a hold 'win' can never be a broken-competitor
    artifact."""
    rng = np.random.default_rng(seed + 80000)
    data = build_accrual_arena(K, N_ARRIVAL, N_ACCRUAL, 0.75, 0.80, 0.0, rng)
    f = features(data)
    y = data["y"]
    idx = rng.permutation(K)
    nt = K // 2
    te, tr = idx[:nt], idx[nt:]
    Xf = _std_on(np.column_stack([f[n] for n in FEAT_FULL]), tr)
    p, _ = A.fit_weighted_sum(Xf[tr], y[tr])
    acc_full = _balanced_acc(p(Xf[te]), y[te])
    return dict(full=float(acc_full), fired=bool(acc_full > 0.75))


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
# self-tests (controls-only smoke gate)
# ============================================================================
def _run_selftests():
    fails, notes = [], []
    lg = linear_guard(11)
    notes.append("linear guard: keep_everything full=%.3f fired=%s"
                 % (lg["full"], lg["fired"]))
    if not lg["fired"]:
        fails.append("linear guard: flat full competitor weak (full=%.3f) -> "
                     "competitor impl broken" % lg["full"])
    for sd in (11, 23, 37):
        pc = positive_control(sd)
        notes.append("POSCTRL seed=%d: arrival=%.3f oracle=%.3f gap=%+.3f fired=%s"
                     % (sd, pc["arrival"], pc["oracle"], pc["gap"], pc["fired"]))
        if not pc["fired"]:
            fails.append("POSCTRL seed %d did NOT fire (gap=%+.3f arrival=%.3f) -> "
                         "harness cannot express temporal advantage" % (sd, pc["gap"],
                                                                        pc["arrival"]))
    for sd in (11, 23, 37):
        ng = null_guard(sd)
        notes.append("NULL guard seed=%d: arrival=%.3f full=%.3f tig_null=%+.3f passes=%s"
                     % (sd, ng["arrival"], ng["full"], ng["tig_null"], ng["passes"]))
        if not ng["passes"]:
            fails.append("NULL guard seed %d FAILED (tig_null=%+.3f > %.3f) -> "
                         "certificate is vacuously positive" % (sd, ng["tig_null"],
                                                                NULL_MAX))
    # tiny real-arena certificate smoke: crossover point must show tig > CERT_MIN
    base = next(o for o in OPERATING_POINTS if o["name"] == BASE_NAME)
    r = race_point_seed(base, 11, 480)
    notes.append("CERT smoke (crossover K=480 seed=11): tig=%+.3f arms_differ=%s "
                 "hold=%.3f keep=%.3f arrival=%.3f"
                 % (r["temporal_info_gain"], r["arms_differ"], r["acc"]["hold_recover"],
                    r["acc"]["keep_everything"], r["acc"]["decide_at_arrival"]))
    if r["temporal_info_gain"] <= CERT_MIN:
        fails.append("CERT smoke: tig=%+.3f <= CERT_MIN=%.3f at base point -> arena "
                     "carries no accruing info" % (r["temporal_info_gain"], CERT_MIN))
    if not r["arms_differ"]:
        fails.append("arms_differ FAILED at base point -> arms not distinct")
    return fails, notes


# ============================================================================
# aggregate + verdict
# ============================================================================
def _mean_se(vals):
    a = np.asarray(vals, float)
    m = float(a.mean())
    se = float(a.std(ddof=1) / np.sqrt(len(a))) if len(a) > 1 else 0.0
    return m, se


def aggregate_and_verdict(profile, seeds, sweep, posctrls, ng_list, lg, elapsed):
    # per operating-point aggregates
    points = {}
    for name, per_seed in sweep.items():
        arms = ["hold_recover", "keep_everything", "decide_at_arrival"]
        acc = {a: float(np.mean([s["acc"][a] for s in per_seed])) for a in arms}
        m_arr, se_arr = _mean_se([s["margin_hold_vs_arrival"] for s in per_seed])
        m_keep, se_keep = _mean_se([s["margin_hold_vs_keep"] for s in per_seed])
        tig = float(np.mean([s["temporal_info_gain"] for s in per_seed]))
        z_arr = (m_arr / se_arr) if se_arr > 1e-12 else (0.0 if abs(m_arr) < 1e-12
                                                         else float(np.sign(m_arr)) * 99.0)
        points[name] = dict(
            acc=acc, margin_hold_vs_arrival=m_arr, se_hold_vs_arrival=se_arr,
            z_hold_vs_arrival=float(z_arr), margin_hold_vs_keep=m_keep,
            se_hold_vs_keep=se_keep, temporal_info_gain=tig,
            spurious_frac=float(np.mean([s["spurious_frac"] for s in per_seed])),
            arms_differ=all(s["arms_differ"] for s in per_seed))

    base = points[BASE_NAME]
    tig_base = base["temporal_info_gain"]
    margin = base["margin_hold_vs_arrival"]
    z = base["z_hold_vs_arrival"]
    margin_keep = base["margin_hold_vs_keep"]

    # controls
    posctrl_fired = all(p["fired"] for p in posctrls)
    null_ok = all(n["passes"] for n in ng_list)
    lg_fired = lg["fired"]
    controls_ok = posctrl_fired and null_ok and lg_fired
    cert_fired = tig_base > CERT_MIN
    baseline_in_band = 0.05 < base["acc"]["keep_everything"] < 0.95
    arms_differ_all = all(points[n]["arms_differ"] for n in points)

    # ---- verdict (base operating point) ----
    if not controls_ok:
        verdict = "INVALID_CONTROL_DID_NOT_FIRE"
    elif not cert_fired:
        verdict = "INVALID_ARENA_NO_ACCRUING_INFO"
    elif not baseline_in_band:
        verdict = "INVALID_BASELINE_OUT_OF_BAND"
    elif margin > TIE_EPS and z > SIGMA_K:
        verdict = "HARD_PASS"
    elif margin <= TIE_EPS:
        verdict = ("HARD_FAIL_HOLD_LOSES" if margin < -X_BAND
                   else "HARD_FAIL_HOLD_TIES")
    else:
        verdict = "MIDDLE_POSITIVE_NOT_SIGNIFICANT"

    localization = (
        "hold_beats_decide_at_arrival_by_>2sigma_with_certified_accruing_info"
        if verdict == "HARD_PASS" else
        "hold_positive_over_arrival_but_below_2sigma"
        if verdict == "MIDDLE_POSITIVE_NOT_SIGNIFICANT" else
        "certified_accruing_info_but_hold_ties/loses_decide_at_arrival_real_fair_bound"
        if verdict.startswith("HARD_FAIL") else
        "uninterpretable_precondition_not_met")
    # secondary localization for the hold-vs-flat-accumulation question
    if verdict in ("HARD_PASS", "MIDDLE_POSITIVE_NOT_SIGNIFICANT"):
        struct = ("hold_ALSO_beats_flat_keep_everything_selective_consolidation_adds_value"
                  if margin_keep > TIE_EPS else
                  "hold_beats_arrival_but_TIES_flat_keep_everything_"
                  "structure_adds_nothing_beyond_flat_accumulation")
    else:
        struct = "n/a_hold_did_not_beat_arrival"

    pc = {k: float(np.mean([p[k] for p in posctrls]))
          for k in ["arrival", "oracle", "gap"]}
    ngm = {k: float(np.mean([n[k] for n in ng_list]))
           for k in ["arrival", "full", "tig_null"]}

    sweep_line = " ; ".join(
        "%s[pn=%.2f]: hold=%.3f keep=%.3f arr=%.3f tig=%+.3f m_arr=%+.3f(z=%.1f) m_keep=%+.3f"
        % (name, next(o["p_noise"] for o in OPERATING_POINTS if o["name"] == name),
           p["acc"]["hold_recover"], p["acc"]["keep_everything"],
           p["acc"]["decide_at_arrival"], p["temporal_info_gain"],
           p["margin_hold_vs_arrival"], p["z_hold_vs_arrival"], p["margin_hold_vs_keep"])
        for name, p in points.items())

    msg = ("profile=%s seeds=%d | %s | BASE=%s: hold=%.3f decide_at_arrival=%.3f "
           "keep_everything=%.3f | CERTIFICATE temporal_info_gain=%+.3f (>%.3f=%s) | "
           "margin hold-arrival=%+.3f se=%.3f z=%.2f (>%.1f) | margin hold-keep=%+.3f | "
           "CONTROLS posctrl=%s(gap=%+.3f arr=%.3f) null=%s(tig_null=%+.3f) linear=%s | "
           "%s | %s || SWEEP: %s" %
           (profile, len(seeds), verdict, BASE_NAME, base["acc"]["hold_recover"],
            base["acc"]["decide_at_arrival"], base["acc"]["keep_everything"],
            tig_base, CERT_MIN, cert_fired, margin, base["se_hold_vs_arrival"], z,
            SIGMA_K, margin_keep, posctrl_fired, pc["gap"], pc["arrival"], null_ok,
            ngm["tig_null"], lg_fired, localization, struct, sweep_line))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "run_mode": profile,
        "primary_metric": "marginal_heldout_balanced_accuracy",
        "crlb_n/a": "classification balanced-acc bands, no Cramer-Rao noise floor applies",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND, "SIGMA_K": SIGMA_K,
                  "CERT_MIN": CERT_MIN, "NULL_MAX": NULL_MAX,
                  "POSCTRL_MIN_GAP": POSCTRL_MIN_GAP},
        "evidence_schedule": {"n_arrival": N_ARRIVAL, "n_accrual": N_ACCRUAL,
                              "note": "a_priori_not_swept"},
        "base_point": BASE_NAME,
        "certificate": {
            "temporal_info_gain_full_minus_arrival": tig_base,
            "fired": bool(cert_fired), "cert_min": CERT_MIN,
        },
        "contract": {
            "hold_recover": base["acc"]["hold_recover"],
            "decide_at_arrival": base["acc"]["decide_at_arrival"],
            "keep_everything": base["acc"]["keep_everything"],
            "margin_hold_vs_arrival": margin,
            "se_hold_vs_arrival": base["se_hold_vs_arrival"],
            "z_hold_vs_arrival": z,
            "margin_hold_vs_keep": margin_keep,
            "localization": localization,
            "structure_localization": struct,
        },
        "sweep": points,
        "controls": {
            "positive_control_fired_all_seeds": posctrl_fired,
            "positive_control_per_seed": posctrls, "positive_control_mean": pc,
            "null_guard_passes_all_seeds": null_ok, "null_guard_per_seed": ng_list,
            "null_guard_mean": ngm, "linear_guard": lg,
        },
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ_all),
    }


# ============================================================================
# main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="controls-only: linear guard + temporal posctrl + null guard "
                         "+ base-point certificate smoke")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = _run_selftests()
        print("=== ACCRUAL CELL SELF-TESTS (controls guard vacuous/rigged race) ===")
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
        print("SELFTEST_PASS: linear guard + temporal positive control fire; null guard "
              "keeps certificate non-vacuous; base-point accruing-info certificate fires")
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71, 89, 101, 113] if profile == "full"
             else [11, 23, 37])
    K = 1600 if profile == "full" else 480
    _write_start_marker(len(seeds), profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # controls first (interpretability gate)
    lg = linear_guard(11)
    posctrls = [positive_control(sd) for sd in seeds]
    ng_list = [null_guard(sd) for sd in seeds]
    print("=== profile=%s seeds=%s K=%d n_arr=%d n_acc=%d ==="
          % (profile, seeds, K, N_ARRIVAL, N_ACCRUAL))
    print("  linear guard fired=%s | POSCTRL fired(all)=%s | NULL guard passes(all)=%s"
          % (lg["fired"], all(p["fired"] for p in posctrls),
             all(n["passes"] for n in ng_list)), flush=True)

    sweep = {op["name"]: [] for op in OPERATING_POINTS}
    total_units = len(OPERATING_POINTS) * len(seeds)
    unit = 0
    for op in OPERATING_POINTS:
        for sd in seeds:
            r = race_point_seed(op, sd, K)
            sweep[op["name"]].append(r)
            unit += 1
            with open(hb_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                     "unit_idx": unit - 1, "total_units": total_units,
                                     "op": op["name"], "seed": sd,
                                     "elapsed_s": time.perf_counter() - t0}) + "\n")
        agg = sweep[op["name"]]
        print("  %-11s pn=%.2f: hold=%.3f keep=%.3f arrival=%.3f | tig=%+.3f "
              "m_arr=%+.3f m_keep=%+.3f" %
              (op["name"], op["p_noise"],
               float(np.mean([s["acc"]["hold_recover"] for s in agg])),
               float(np.mean([s["acc"]["keep_everything"] for s in agg])),
               float(np.mean([s["acc"]["decide_at_arrival"] for s in agg])),
               float(np.mean([s["temporal_info_gain"] for s in agg])),
               float(np.mean([s["margin_hold_vs_arrival"] for s in agg])),
               float(np.mean([s["margin_hold_vs_keep"] for s in agg]))), flush=True)

    out = aggregate_and_verdict(profile, seeds, sweep, posctrls, ng_list, lg,
                                time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("FAIR TEMPORAL ACCRUAL RACE -- PRIMARY = MARGINAL held-out balanced acc")
    print("  base operating point = %s" % BASE_NAME)
    ct = out["contract"]
    cert = out["certificate"]
    print("\n  CERTIFICATE (precondition): temporal_info_gain (keep - arrival) = %+.3f"
          % cert["temporal_info_gain_full_minus_arrival"])
    print("    fired (> %.3f) = %s  [if not fired -> arena still artificial, INVALID]"
          % (cert["cert_min"], cert["fired"]))
    print("\n  BASE ARMS: hold_recover=%.3f  decide_at_arrival=%.3f  keep_everything=%.3f"
          % (ct["hold_recover"], ct["decide_at_arrival"], ct["keep_everything"]))
    print("  margin hold - decide_at_arrival = %+.3f (se=%.3f, z=%.2f; HARD_PASS z>%.1f)"
          % (ct["margin_hold_vs_arrival"], ct["se_hold_vs_arrival"],
             ct["z_hold_vs_arrival"], SIGMA_K))
    print("  margin hold - keep_everything   = %+.3f (structure vs flat accumulation)"
          % ct["margin_hold_vs_keep"])
    print("  localization: %s" % ct["localization"])
    print("  structure   : %s" % ct["structure_localization"])
    cc = out["controls"]
    print("\n  CONTROLS: posctrl fired(all)=%s (oracle gap=%+.3f arrival=%.3f) | "
          "null guard passes(all)=%s (tig_null=%+.3f) | linear guard fired=%s (full=%.3f)"
          % (cc["positive_control_fired_all_seeds"], cc["positive_control_mean"]["gap"],
             cc["positive_control_mean"]["arrival"], cc["null_guard_passes_all_seeds"],
             cc["null_guard_mean"]["tig_null"], cc["linear_guard"]["fired"],
             cc["linear_guard"]["full"]))
    print("\n  SWEEP (crossover region):")
    print("  %-11s %6s %7s %7s %7s %8s %8s %6s %8s"
          % ("point", "p_noise", "hold", "keep", "arrival", "tig", "m_arr", "z", "m_keep"))
    for name, p in out["sweep"].items():
        pn = next(o["p_noise"] for o in OPERATING_POINTS if o["name"] == name)
        print("  %-11s %6.2f %7.3f %7.3f %7.3f %+8.3f %+8.3f %6.1f %+8.3f"
              % (name, pn, p["acc"]["hold_recover"], p["acc"]["keep_everything"],
                 p["acc"]["decide_at_arrival"], p["temporal_info_gain"],
                 p["margin_hold_vs_arrival"], p["z_hold_vs_arrival"],
                 p["margin_hold_vs_keep"]))
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"])
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
