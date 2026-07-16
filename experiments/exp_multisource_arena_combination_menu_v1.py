"""Combination-rule MENU race inside the VET-cleared multi-source arena.

REUSES experiments/exp_multisource_arena_v1.py (commit e943e0854) VERBATIM as the
arena (build_arena + 4 signal functions + copy detector + validity harness). This
cell adds NO new arena -- it races the 5-FORM combination-rule menu from
notes/research_combination_rule_menu_and_route_calibration_2026-07-16.md in the
arena's pluggable gate slot, on identical splits/seeds.

PRIMARY METRIC (VET-mandated): MARGINAL held-out balanced accuracy. Truth in this
arena is an INDEPENDENT noisy sigmoid (19.7% label noise, no circularity), so the
marginal held-out metric is the honest one. Within-cell (stratified) balanced
accuracy is reported as a SECONDARY, narrower residual test -- clearly labeled,
NOT treated as "the honest one."

THE 5-FORM MENU (each labeled brain-faithful [BF] vs engineering-baseline [ENG]):
  F1  BRANCH/ROUTE with CALIBRATED thresholds [BF] -- 3 calibration methods:
        F1a route_np    : Neyman-Pearson tau* = f(C_FP,C_FN,base-rate)
        F1b route_ewma  : SDT/DDM leaky-EWMA online base-rate -> threshold
        F1c route_stn   : NP tau* + STN conflict-triggered threshold-raise
      (all three share a precision-graded score core + reliability-gate branch +
       salience bypass; they differ ONLY in the final decision threshold, which
       isolates whether threshold-calibration is the lever.)
  F2  precision_fusion  [BF]  -- Ernst-Banks inverse-variance / LLR summation
                                 (diagonal-LDA; weights DERIVED from class-
                                 conditional precisions, NOT MLE-learned).
  F3  additive_logistic [ENG] -- learned weights (== arena's weighted_sum). The
                                 current marginal winner (0.866) to match/beat.
  F4  multiplicative_gate [BF-form] -- product of per-signal calibrated probs
                                 (naive-Bayes AND / Friston precision-gating form).
  F5  race_2accumulator [BF]  -- leaky competing accumulators (Usher-McClelland
                                 LCA): evidence-for vs evidence-against race to a
                                 boundary; time-to-threshold = confidence readout.
  Reference arms: route_uncal_grid [ENG] (arena's fit_route, the -20% under-
  performer being fixed) + best_single [ENG] (floor).

DECISIVE QUESTION: does a BRAIN-FAITHFUL form, once properly calibrated, MATCH or
BEAT the learned logistic (0.866) on the honest MARGINAL metric? And WHY does the
uncalibrated route fail -- threshold, the branch structure, or the form itself?

SELF-TEST (guards a vacuous race, real code path):
  ST-A linear-additive control  : precision_fusion, race, calibrated-route MUST
        recover logistic-level accuracy (a correctly-built linear/route form CAN
        express a linear separator; if it can't, the impl is broken).
  ST-B interaction (AND) control: multiplicative_gate MUST beat additive_logistic
        (a correctly-built multiplicative form expresses a conjunction a single
        linear boundary cannot; guards F4 is not vacuous).

PRE-REG BANDS (marginal, brain-faithful vs learned logistic):
  TIE_EPS = 0.010 balanced-acc ; X_BAND = 0.030 balanced-acc
  HARD-PASS : best brain-faithful form marginal >= logistic - TIE_EPS (tie-or-beat)
  HARD-FAIL : best brain-faithful form marginal <  logistic - X_BAND (>3pts below
              even after calibration => learned weights genuinely needed; honest
              informative negative)
  MIDDLE    : otherwise.

Pure-Python (numpy only), reuses arena. No atoms, no torch, no queue, no push.
Runs inline in seconds. Multi-seed (identical splits across all forms).

Run:
  python experiments/exp_multisource_arena_combination_menu_v1.py --self-test
  python experiments/exp_multisource_arena_combination_menu_v1.py --profile smoke
  python experiments/exp_multisource_arena_combination_menu_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (numpy design cell):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - no bare except; no hash()-derived seeds; sorted(set()) ordering only
# - final metrics via tmp + os.replace (atomic; META_RULE_AH)
# - start-marker + crash-diagnostic + per-seed heartbeat
# - arms_differ: forms produce distinct decisions (hash-checked)
# - all reported numbers MEASURED @ this run's metrics.json unless tagged else
# - baseline-in-band: logistic marginal checked in (0.05, 0.95)

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

# --- reuse the arena verbatim ------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_multisource_arena_v1 as A  # noqa: E402

ANCHOR_NAME = "multisource_arena_combination_menu_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_combination_menu_v1")

sigmoid = A.sigmoid
_balanced_acc = A._balanced_acc

# pre-registered bands
TIE_EPS = 0.010
X_BAND = 0.030

BRAIN_FAITHFUL = ["route_np", "route_ewma", "route_stn", "precision_fusion",
                  "multiplicative_gate", "race_2accumulator"]
ENGINEERING = ["additive_logistic", "route_uncal_grid", "best_single"]


# ============================================================================
# small fitters shared by the forms
# ============================================================================
def _uni_logistic(x, y, steps=300, lr=0.5, l2=1e-3):
    """1-feature logistic (a*x + b) via deterministic GD -> (a, b)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    a, b = 0.0, 0.0
    for _ in range(steps):
        p = sigmoid(a * x + b)
        ga = (x * (p - y)).mean() + l2 * a
        gb = (p - y).mean()
        a -= lr * ga
        b -= lr * gb
    return float(a), float(b)


def _precision_weights(Xtr, ytr):
    """Ernst-Banks inverse-variance weights DERIVED from class-conditional stats.
    w_c = (mu1_c - mu0_c) / pooled_within_var_c. Sign encodes orientation, so no
    separate polarity step is needed. Returns (w, mu1, mu0)."""
    y = ytr.astype(int)
    d = Xtr.shape[1]
    w = np.zeros(d)
    mu1 = np.zeros(d)
    mu0 = np.zeros(d)
    for c in range(d):
        x1 = Xtr[y == 1, c]
        x0 = Xtr[y == 0, c]
        m1 = float(x1.mean()) if len(x1) else 0.0
        m0 = float(x0.mean()) if len(x0) else 0.0
        v = 0.5 * (float(x1.var()) + float(x0.var())) + 1e-9
        w[c] = (m1 - m0) / v
        mu1[c] = m1
        mu0[c] = m0
    return w, mu1, mu0


# ---- F2: precision-weighted Bayesian fusion (diagonal LDA / LLR sum) --------
def fit_precision_fusion(Xtr, ytr, cols, cost_fp=1.0, cost_fn=1.0):
    """BF. score = sum_c w_c x_c ; threshold from NP tau* + base-rate + costs.
    weights are precision-DERIVED (not learned) -- the key contrast with F3."""
    w, mu1, mu0 = _precision_weights(Xtr, ytr)
    base = float(np.clip(ytr.mean(), 1e-3, 1 - 1e-3))
    mid = 0.5 * float(np.dot(w, mu1 + mu0))
    thr = mid - np.log(base / (1 - base)) - np.log(cost_fn / cost_fp)

    def predict(Xte):
        return (Xte @ w >= thr).astype(int)
    return predict, dict(w=w.tolist(), thr=float(thr), base=base)


# ---- F1: calibrated BRANCH/ROUTE (3 threshold-calibration methods) ----------
def fit_route_calibrated(Xtr, ytr, cols, method="np", cost_fp=1.0, cost_fn=1.0,
                         ewma_lambda=0.05):
    """BF. Precision-graded score core (STC accumulation) + reliability-gate
    branch (CLS route) + one-shot salience bypass (arousal). The three methods
    fix the decision threshold on the score by a distinct calibration knob:
      np   : Neyman-Pearson tau* = mid - logit(base) - log(C_FN/C_FP)
      ewma : SDT/DDM leaky-EWMA online base-rate -> logit(p_hat)
      stn  : np + STN conflict-triggered raise on narrow-margin (high-conflict)
             claims (raise threshold before committing).
    OPTIMIZE-TO-FRONTIER (USER 07-16): the branch STRENGTH (reliability-gate
    percentile, incl. 0.0 = branch OFF), the one-shot salience bypass (on/off),
    and the STN raise magnitude/band are TRAIN-SELECTED (max train balanced-acc)
    per method -- so each calibration method is reported at its best config, not
    a naive first guess. The threshold tau stays at the method's PRINCIPLED value
    (that is the calibration contrast under test); only the branch is tuned."""
    w, mu1, mu0 = _precision_weights(Xtr, ytr)
    base = float(np.clip(ytr.mean(), 1e-3, 1 - 1e-3))
    mid = 0.5 * float(np.dot(w, mu1 + mu0))
    tau_np = mid - np.log(base / (1 - base)) - np.log(cost_fn / cost_fp)

    # leaky-EWMA online base-rate over the train stream (order as given)
    p = base
    for yt in ytr:
        p = (1 - ewma_lambda) * p + ewma_lambda * float(yt)
    p = float(np.clip(p, 1e-3, 1 - 1e-3))
    tau_ewma = mid - np.log(p / (1 - p)) - np.log(cost_fn / cost_fp)
    tau = {"np": tau_np, "ewma": tau_ewma, "stn": tau_np}[method]

    rc, im = cols["recurrence"], cols["importance"]
    contr_rc_tr = w[rc] * Xtr[:, rc]
    contr_im_tr = w[im] * Xtr[:, im]
    s_tr = Xtr @ w
    sd_s = float(np.std(s_tr)) + 1e-9

    def make_decider(gate_q, use_bypass, conf_q, raise_frac):
        rc_lo = float(np.quantile(contr_rc_tr, gate_q)) if gate_q > 0 else -np.inf
        im_lo = float(np.quantile(contr_im_tr, gate_q)) if gate_q > 0 else -np.inf
        im_hi = float(np.quantile(contr_im_tr, 0.90))
        conf_band = float(np.quantile(np.abs(s_tr - tau), conf_q))
        raise_delta = raise_frac * sd_s

        def decide(X):
            s = X @ w
            dec = (s >= tau).astype(int)
            if method == "stn" and raise_delta > 0:
                conflict = np.abs(s - tau) < conf_band
                dec = np.where(conflict, (s >= tau + raise_delta).astype(int), dec)
            if gate_q > 0:
                cr = w[rc] * X[:, rc]
                ci = w[im] * X[:, im]
                bypass = (ci >= im_hi) if use_bypass else np.zeros(len(X), bool)
                rel_fail = (cr < rc_lo) & (ci < im_lo) & (~bypass)
                dec = np.where(rel_fail, 0, dec)
                if use_bypass:
                    dec = np.where(bypass, 1, dec)
            return dec.astype(int)
        return decide

    # train-search the branch/raise config (frontier); tau stays principled.
    gate_grid = (0.0, 0.10, 0.25)
    bypass_grid = (False, True)
    if method == "stn":
        conf_grid, raise_grid = (0.10, 0.25), (0.0, 0.15, 0.30)
    else:
        conf_grid, raise_grid = (0.25,), (0.0,)
    best_cfg, best_acc = None, -1.0
    for gq in gate_grid:
        for bp in bypass_grid:
            for cq in conf_grid:
                for rf in raise_grid:
                    dec = make_decider(gq, bp, cq, rf)
                    acc = _balanced_acc(dec(Xtr), ytr)
                    if acc > best_acc:
                        best_acc, best_cfg = acc, (gq, bp, cq, rf)
    decider = make_decider(*best_cfg)
    return decider, dict(method=method, tau_np=float(tau_np),
                         tau_ewma=float(tau_ewma), p_ewma=p, base=base,
                         cfg=dict(gate_q=best_cfg[0], bypass=best_cfg[1],
                                  conf_q=best_cfg[2], raise_frac=best_cfg[3]),
                         train_bal_acc=float(best_acc))


# ---- F4: multiplicative / gated AND (naive-Bayes product of calib probs) ----
def fit_multiplicative_gate(Xtr, ytr, cols, grid_q=np.linspace(0.10, 0.90, 17)):
    """BF-form. Each signal -> per-signal P(true) via univariate logistic; the
    joint gate = product of those probs (strict AND / precision-gating). A single
    strong signal cannot open the gate alone -> genuinely different from additive.
    Decision threshold grid-searched on train (product is monotone but nonlinear
    in z, so it needs its own cut)."""
    y = ytr.astype(float)
    d = Xtr.shape[1]
    params = [_uni_logistic(Xtr[:, c], y) for c in range(d)]

    def probs(X):
        P = np.ones(len(X))
        for c in range(d):
            a, b = params[c]
            P = P * sigmoid(a * X[:, c] + b)
        return P

    Ptr = probs(Xtr)
    best_thr, best_acc = None, -1.0
    for thr in np.quantile(Ptr, grid_q):
        acc = _balanced_acc((Ptr >= thr).astype(int), ytr)
        if acc > best_acc:
            best_acc, best_thr = acc, float(thr)

    def predict(Xte):
        return (probs(Xte) >= best_thr).astype(int)
    return predict, dict(thr=float(best_thr), train_bal_acc=float(best_acc))


# ---- F5: two-accumulator leaky competing race (LCA) -------------------------
def _lca_race(drift_for, drift_against, k=0.2, beta=0.3, dt=0.1, theta=1.0,
              max_t=250):
    """Deterministic leaky competing accumulators. Returns (decision, time).
    aF/aS accumulate evidence-for/-against with leak k and mutual inhibition beta;
    first to cross theta wins; time-to-threshold is the confidence/urgency readout."""
    n = len(drift_for)
    aF = np.zeros(n)
    aS = np.zeros(n)
    dec = np.zeros(n, dtype=int)
    tvec = np.full(n, float(max_t))
    decided = np.zeros(n, dtype=bool)
    for t in range(max_t):
        aF = np.maximum(0.0, aF + dt * (drift_for - k * aF - beta * aS))
        aS = np.maximum(0.0, aS + dt * (drift_against - k * aS - beta * aF))
        newF = (~decided) & (aF >= theta)
        newS = (~decided) & (aS >= theta) & (~newF)
        dec[newF] = 1
        dec[newS] = 0
        both = newF | newS
        tvec[both] = t + 1
        decided |= both
        if decided.all():
            break
    und = ~decided
    dec[und] = (aF[und] >= aS[und]).astype(int)
    return dec.astype(int), tvec


def fit_race_accumulator(Xtr, ytr, cols):
    """BF. drift_for = precision-weighted POSITIVE evidence; drift_against =
    precision-weighted NEGATIVE evidence + a base-rate bias (grid-set on train,
    one scalar, like a route threshold). Returns predictor + a time-readout probe."""
    w, mu1, mu0 = _precision_weights(Xtr, ytr)
    scale = 1.0 / (np.abs(w).sum() + 1e-9)

    def drifts(X, bias):
        contr = (X * w) * scale               # per-signal signed evidence
        df = np.maximum(0.0, contr).sum(axis=1)
        ds = np.maximum(0.0, -contr).sum(axis=1) + bias
        return df, ds

    # calibrate the single base-rate bias scalar on train balanced-acc
    best_bias, best_acc = 0.0, -1.0
    for bias in np.linspace(-0.4, 0.4, 17):
        df, ds = drifts(Xtr, bias)
        dec, _ = _lca_race(df, ds)
        acc = _balanced_acc(dec, ytr)
        if acc > best_acc:
            best_acc, best_bias = acc, float(bias)

    def predict(Xte):
        df, ds = drifts(Xte, best_bias)
        dec, _ = _lca_race(df, ds)
        return dec

    def time_probe(Xte):
        df, ds = drifts(Xte, best_bias)
        dec, tvec = _lca_race(df, ds)
        return dec, tvec
    return predict, dict(bias=float(best_bias), train_bal_acc=float(best_acc),
                         time_probe=time_probe)


# ============================================================================
# self-tests (guard a vacuous race; exercise the REAL fit functions)
# ============================================================================
def _synth_cols():
    return {"unexpectedness": 0, "schema_fit": 1, "recurrence": 2, "importance": 3}


def run_menu_self_tests():
    """ST-A linear-additive: linear/route forms recover logistic-level.
    ST-B interaction(AND): multiplicative_gate beats additive_logistic."""
    fails, notes = [], []
    cols = _synth_cols()
    rng = np.random.default_rng(2027)

    # ---- ST-A: linear-additive, all-informative positive weights ----
    n = 4000
    X = rng.normal(size=(n, 4))
    wtrue = np.array([1.0, 1.0, 1.0, 1.0])
    truth = ((X @ wtrue + 0.6 * rng.normal(size=n)) > 0).astype(int)
    tr = slice(0, n // 2)
    te = slice(n // 2, n)
    Xtr, ytr, Xte, yte = X[tr], truth[tr], X[te], truth[te]
    log_pred, _ = A.fit_weighted_sum(Xtr, ytr)
    log_acc = _balanced_acc(log_pred(Xte), yte)
    fus_pred, _ = fit_precision_fusion(Xtr, ytr, cols)
    fus_acc = _balanced_acc(fus_pred(Xte), yte)
    rt_pred, _ = fit_route_calibrated(Xtr, ytr, cols, method="np")
    rt_acc = _balanced_acc(rt_pred(Xte), yte)
    rc_pred, _ = fit_race_accumulator(Xtr, ytr, cols)
    rc_acc = _balanced_acc(rc_pred(Xte), yte)
    notes.append("ST-A linear: logistic=%.3f fusion=%.3f route_np=%.3f race=%.3f"
                 % (log_acc, fus_acc, rt_acc, rc_acc))
    if fus_acc < log_acc - 0.03:
        fails.append("ST-A: precision_fusion fails to recover linear separator "
                     "(fusion=%.3f logistic=%.3f) -> fusion impl broken" % (fus_acc, log_acc))
    if rt_acc < log_acc - 0.05:
        fails.append("ST-A: calibrated route fails to recover linear separator "
                     "(route=%.3f logistic=%.3f) -> route impl broken, not brain-form"
                     % (rt_acc, log_acc))
    if rc_acc < log_acc - 0.05:
        fails.append("ST-A: race fails to recover linear separator "
                     "(race=%.3f logistic=%.3f) -> race impl broken" % (rc_acc, log_acc))

    # ---- ST-B: interaction (AND) -> multiplicative must beat additive ----
    X2 = rng.normal(size=(n, 4))
    truth2 = ((X2[:, 0] > 0) & (X2[:, 1] > 0)).astype(int)
    Xtr2, ytr2, Xte2, yte2 = X2[tr], truth2[tr], X2[te], truth2[te]
    log2, _ = A.fit_weighted_sum(Xtr2, ytr2)
    log2_acc = _balanced_acc(log2(Xte2), yte2)
    mg2, _ = fit_multiplicative_gate(Xtr2, ytr2, cols)
    mg2_acc = _balanced_acc(mg2(Xte2), yte2)
    notes.append("ST-B AND-interaction: logistic=%.3f multiplicative=%.3f"
                 % (log2_acc, mg2_acc))
    if mg2_acc < log2_acc + 0.03:
        fails.append("ST-B: multiplicative_gate does NOT beat additive on an AND "
                     "control (mult=%.3f logistic=%.3f) -> multiplicative impl vacuous"
                     % (mg2_acc, log2_acc))
    return fails, notes


# ============================================================================
# per-seed race (identical split -> all forms fair)
# ============================================================================
def _hash_dec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()


def race_one_seed(cfg, seed):
    rng = np.random.default_rng(seed)
    arena = A.build_arena(cfg, rng)
    gen_fails, _, clusters = A.run_self_tests(arena)
    sig = A.compute_all_signals(arena, clusters)
    truth = arena["truth"].astype(int)
    names = ["unexpectedness", "schema_fit", "recurrence", "importance"]
    raw = {n: sig[n] for n in names}

    # identical split + standardization as arena's run_one_seed
    K = cfg.n_claims
    idx = rng.permutation(K)
    n_test = int(cfg.test_frac * K)
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    mu = np.array([raw[n][train_idx].mean() for n in names])
    sd = np.array([raw[n][train_idx].std() + 1e-9 for n in names])
    X = np.column_stack([raw[n] for n in names])
    Xz = (X - mu) / sd
    cols = {n: i for i, n in enumerate(names)}
    Xtr, ytr = Xz[train_idx], truth[train_idx]
    Xte, yte = Xz[test_idx], truth[test_idx]

    # --- fit every form on the SAME train ---
    preds = {}
    infos = {}
    f, i = fit_route_calibrated(Xtr, ytr, cols, method="np"); preds["route_np"] = f(Xte); infos["route_np"] = i
    f, i = fit_route_calibrated(Xtr, ytr, cols, method="ewma"); preds["route_ewma"] = f(Xte); infos["route_ewma"] = i
    f, i = fit_route_calibrated(Xtr, ytr, cols, method="stn"); preds["route_stn"] = f(Xte); infos["route_stn"] = i
    f, i = fit_precision_fusion(Xtr, ytr, cols); preds["precision_fusion"] = f(Xte); infos["precision_fusion"] = i
    f, i = A.fit_weighted_sum(Xtr, ytr); preds["additive_logistic"] = f(Xte); infos["additive_logistic"] = i
    f, i = fit_multiplicative_gate(Xtr, ytr, cols); preds["multiplicative_gate"] = f(Xte); infos["multiplicative_gate"] = i
    f, i = fit_race_accumulator(Xtr, ytr, cols); preds["race_2accumulator"] = f(Xte); infos["race_2accumulator"] = i
    f, i = A.fit_route(Xtr, ytr, cols); preds["route_uncal_grid"] = f(Xte); infos["route_uncal_grid"] = i
    f, i = A.fit_best_single(Xtr, ytr, cols); preds["best_single"] = f(Xte); infos["best_single"] = i
    best_single_name = infos["best_single"]["signal"]

    # PRIMARY: marginal held-out balanced accuracy
    marginal = {k: float(_balanced_acc(v, yte)) for k, v in preds.items()}
    # SECONDARY: within-cell stratified balanced accuracy
    strat_th = {n: 0.0 for n in names}
    strat_sig = {n: Xte[:, cols[n]] for n in names}
    within = {}
    for k, v in preds.items():
        acc, _ = A.within_cell_bal_acc(v, yte, strat_sig, cfg, strat_th)
        within[k] = float(acc)

    # race time-to-threshold diagnostic: does confidence (time) track correctness?
    tp = fit_race_accumulator(Xtr, ytr, cols)[1]["time_probe"]
    rdec, rtime = tp(Xte)
    correct = (rdec == yte).astype(float)
    # shorter time == more confident; expect NEGATIVE corr(time, correct)
    if rtime.std() > 1e-9 and correct.std() > 1e-9:
        time_corr = float(np.corrcoef(rtime, correct)[0, 1])
    else:
        time_corr = 0.0

    # arms-must-differ across the menu (brain-faithful forms distinct)
    distinct = len({_hash_dec(preds[k]) for k in
                    ["route_np", "precision_fusion", "additive_logistic",
                     "multiplicative_gate", "race_2accumulator"]})
    arms_differ = distinct >= 3

    return dict(gen_self_test_fails=gen_fails, best_single_signal=best_single_name,
                marginal=marginal, within_cell=within, arms_differ=bool(arms_differ),
                race_time_correct_corr=time_corr, n_test=int(n_test),
                route_cfgs={k: infos[k]["cfg"] for k in
                            ["route_np", "route_ewma", "route_stn"]})


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
# aggregate + verdict
# ============================================================================
def aggregate_and_verdict(profile, seeds, per_seed, elapsed):
    forms = ["route_np", "route_ewma", "route_stn", "precision_fusion",
             "additive_logistic", "multiplicative_gate", "race_2accumulator",
             "route_uncal_grid", "best_single"]

    def mean_over(metric, key):
        return float(np.mean([s[metric][key] for s in per_seed]))

    marg = {k: mean_over("marginal", k) for k in forms}
    within = {k: mean_over("within_cell", k) for k in forms}
    logistic = marg["additive_logistic"]

    # best brain-faithful form on the PRIMARY (marginal) metric
    best_bf = max(BRAIN_FAITHFUL, key=lambda k: marg[k])
    best_bf_marg = marg[best_bf]
    gap = logistic - best_bf_marg

    baseline_in_band = 0.05 < logistic < 0.95
    arms_differ_all = all(s["arms_differ"] for s in per_seed)

    if not baseline_in_band:
        verdict = "INVALID_BASELINE_OUT_OF_BAND"
    elif best_bf_marg >= logistic - TIE_EPS:
        verdict = "HARD_PASS"
    elif best_bf_marg < logistic - X_BAND:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    # route-failure diagnosis (route_uncal_grid is the -20% underperformer)
    route_uncal = marg["route_uncal_grid"]
    route_best_cal = max(marg["route_np"], marg["route_ewma"], marg["route_stn"])
    calibration_gain = route_best_cal - route_uncal            # threshold/form-core fix
    branch_cost = marg["precision_fusion"] - route_best_cal    # what the branch costs vs pure fusion
    cal_methods_spread = max(marg["route_np"], marg["route_ewma"], marg["route_stn"]) - \
        min(marg["route_np"], marg["route_ewma"], marg["route_stn"])
    mean_time_corr = float(np.mean([s["race_time_correct_corr"] for s in per_seed]))

    msg = ("profile=%s seeds=%d | %s | MARGINAL(primary): logistic=%.3f "
           "best_bf=%s@%.3f (gap=%+.3f) | fusion=%.3f route_np=%.3f route_ewma=%.3f "
           "route_stn=%.3f mult=%.3f race=%.3f route_uncal=%.3f best_single[%s]=%.3f "
           "| route-fix: calib_gain=%+.3f branch_cost=%+.3f cal_spread=%.3f "
           "race_time~correct_r=%+.2f" %
           (profile, len(seeds), verdict, logistic, best_bf, best_bf_marg, -gap,
            marg["precision_fusion"], marg["route_np"], marg["route_ewma"],
            marg["route_stn"], marg["multiplicative_gate"], marg["race_2accumulator"],
            route_uncal, per_seed[0]["best_single_signal"], marg["best_single"],
            calibration_gain, branch_cost, cal_methods_spread, mean_time_corr))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "primary_metric": "marginal_heldout_balanced_accuracy",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND},
        "marginal_bal_acc": marg,
        "within_cell_bal_acc_secondary": within,
        "logistic_marginal": logistic,
        "best_brain_faithful": {"form": best_bf, "marginal": best_bf_marg,
                                "gap_vs_logistic": float(-gap)},
        "brain_faithful_vs_learned": ("BRAIN_FAITHFUL_TIES_OR_BEATS"
                                      if best_bf_marg >= logistic - TIE_EPS
                                      else "LEARNED_LOGISTIC_WINS"),
        "route_failure_diagnosis": {
            "route_uncalibrated_grid": route_uncal,
            "route_best_calibrated": route_best_cal,
            "calibration_gain": float(calibration_gain),
            "branch_cost_vs_pure_fusion": float(branch_cost),
            "calibration_method_spread": float(cal_methods_spread),
        },
        "race_time_correct_corr_mean": mean_time_corr,
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ_all),
        "best_single_signal": per_seed[0]["best_single_signal"],
        "per_seed": per_seed,
    }


# ============================================================================
# main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="menu self-tests (linear + AND controls), no arena race")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = run_menu_self_tests()
        print("=== MENU SELF-TESTS (guard vacuous race) ===")
        for nline in notes:
            print("  " + nline)
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
        print("SELFTEST_PASS: forms recover their matched structure (guard passed)")
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71] if profile == "full" else [11, 23, 37])
    _write_start_marker(len(seeds), profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    per_seed = []
    print("=== profile=%s seeds=%s ===" % (profile, seeds))
    for si, sd in enumerate(seeds):
        cfg = A.ArenaConfig(profile=profile, seed=sd)
        res = race_one_seed(cfg, sd)
        if res["gen_self_test_fails"]:
            print("SEED %d ARENA SELF-TEST FAIL: %s" % (sd, res["gen_self_test_fails"]))
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "seed %d arena: %s" % (sd, res["gen_self_test_fails"]),
                           "elapsed_s": time.perf_counter() - t0,
                           "anchor_name": ANCHOR_NAME})
            return 2
        per_seed.append(res)
        with open(hb_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                 "unit_idx": si, "total_units": len(seeds),
                                 "elapsed_s": time.perf_counter() - t0}) + "\n")
        m = res["marginal"]
        print("  seed %d MARGINAL: logistic=%.3f fusion=%.3f route_np=%.3f "
              "mult=%.3f race=%.3f uncal=%.3f single=%.3f" %
              (sd, m["additive_logistic"], m["precision_fusion"], m["route_np"],
               m["multiplicative_gate"], m["race_2accumulator"],
               m["route_uncal_grid"], m["best_single"]))

    out = aggregate_and_verdict(profile, seeds, per_seed, time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("COMBINATION-RULE MENU RACE -- PRIMARY = MARGINAL held-out balanced acc")
    mg = out["marginal_bal_acc"]
    wc = out["within_cell_bal_acc_secondary"]
    order = ["additive_logistic", "precision_fusion", "route_np", "route_ewma",
             "route_stn", "multiplicative_gate", "race_2accumulator",
             "route_uncal_grid", "best_single"]
    label = {"additive_logistic": "F3 additive_logistic [ENG,learned]",
             "precision_fusion": "F2 precision_fusion   [BF]",
             "route_np": "F1a route_np          [BF]",
             "route_ewma": "F1b route_ewma        [BF]",
             "route_stn": "F1c route_stn         [BF]",
             "multiplicative_gate": "F4 multiplicative     [BF-form]",
             "race_2accumulator": "F5 race_2accumulator  [BF]",
             "route_uncal_grid": "-- route_uncal_grid   [ENG,underperformer]",
             "best_single": "-- best_single        [ENG,floor]"}
    print("  %-42s %8s %8s" % ("form", "MARGINAL", "within"))
    for k in order:
        print("  %-42s %8.3f %8.3f" % (label[k], mg[k], wc[k]))
    print("\n  brain-faithful vs learned : %s" % out["brain_faithful_vs_learned"])
    bbf = out["best_brain_faithful"]
    print("  best brain-faithful       : %s @ %.3f (gap vs logistic %+.3f; "
          "TIE_EPS=%.3f X_BAND=%.3f)" % (bbf["form"], bbf["marginal"],
                                          bbf["gap_vs_logistic"], TIE_EPS, X_BAND))
    rd = out["route_failure_diagnosis"]
    print("  route-failure diagnosis   : uncal=%.3f -> best-calibrated=%.3f "
          "(calibration_gain=%+.3f)" % (rd["route_uncalibrated_grid"],
                                         rd["route_best_calibrated"], rd["calibration_gain"]))
    print("                              branch_cost_vs_pure_fusion=%+.3f  "
          "calibration_method_spread=%.3f" % (rd["branch_cost_vs_pure_fusion"],
                                               rd["calibration_method_spread"]))
    print("  race time~correct corr    : %+.2f (negative = shorter-time-more-correct)"
          % out["race_time_correct_corr_mean"])
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"])
    print("  " + out["verdict_msg"])
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
