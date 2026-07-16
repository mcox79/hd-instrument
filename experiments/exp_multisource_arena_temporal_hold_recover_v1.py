"""TEMPORAL hold-then-recover extension of the multi-source arena + menu re-race.

EXTENDS experiments/exp_multisource_arena_v1.py (VET-cleared arena, commit
e943e0854) and experiments/exp_multisource_arena_combination_menu_v1.py (5-form
menu, commit 6741d9e1f) with a GENUINE temporal dimension: claims arrive as a
STREAM over discrete time and the CORROBORATION (recurrence) signal is not
available at arrival -- it ACCRUES as later source reports arrive within a hold
window. The other three signals (surprise, schema-fit, importance) ARE available
at arrival. A claim can be HELD PROVISIONALLY (n=1) at arrival and RECOVERED if
corroboration accrues within the window, or DISCARDED if it decays unsupported --
the synaptic-tagging-and-capture / CLS fast-vs-slow structure the route/branch is
built for (notes/research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md,
notes/research_multisource_memory_assimilation_arena_2026-07-16.md).

DECISIVE QUESTION (contract): on this TEMPORAL regime, does the brain-faithful
ROUTE/branch (reliability-gate + provisional-hold + one-shot salience bypass) BEAT
the strong static competitors AND the accumulator race -- whereas it only TIED on
the static arena?

THIS IS A CAN-FAIL TEST, NOT AN ENGINEERED ROUTE-WIN (coordinator correction
2026-07-16). Three disciplines encode that:
 (1) The arena is NOT tuned until the route helps. build_arena params are inherited
     verbatim; the temporal schedule (window/delay) is set A PRIORI, not swept to
     favour the window. The route can add ~0.000 and that is a real result.
 (2) The honest PRIMARY null is the FULL-feature flat competitors: static_full_
     logistic + precision_fusion + race all SEE the windowed recurrence too. Route
     wins ONLY if the hold-recover STRUCTURE extracts value a flat readout of the
     SAME information cannot. Since arena truth is a linear noisy-sigmoid, a flat
     logistic is near-Bayes-optimal -> route TYING/LOSING is the expected, valid,
     informative HARD-FAIL (route's value is then NOT temporal-hold).
 (3) FIRED POSITIVE CONTROL (ST-B analog): a synthetic temporal regime where
     arrival features are pure noise and truth = (within-window corroboration >= 2).
     A hold/oracle policy PROVABLY beats any decide-at-arrival single-shot decision
     there; static_arrival is pinned at chance. This proves the harness CAN express
     a temporal advantage IF it is real -- without it, a route tie is uninterpretable.
     ST-A linear guard additionally proves the flat competitors are STRONG (so a
     route win could never be a flat-competitor-is-broken artifact).

Also reported for localization: static_arrival_logistic (decide-at-arrival, no
windowed recurrence) and temporal_info_gain = static_full - static_arrival, which
says whether the window carries truth-info AT ALL, independent of the route.

PRE-REG BANDS (marginal held-out balanced accuracy; marginal is the honest metric
per the menu VET -- truth is an INDEPENDENT noisy sigmoid, no circularity):
  TIE_EPS = 0.010 ; X_BAND = 0.030
  competitor = max(static_full_logistic, precision_fusion, multiplicative_gate,
                   race_2accumulator)   # strong flat-wait + race, all with window info
  margin = route_hold_recover - competitor
  HARD-PASS : arena valid + positive control FIRED + margin > TIE_EPS
              (route beats the strong competitors WITH the time axis -> value IS
               the temporal-hold branch structure).
  HARD-FAIL : arena valid + positive control FIRED + margin <= TIE_EPS
              (route only ties [-> _TIES] or loses [< -X_BAND -> _LOSES] even WITH
               a genuine time axis -> route's value is NOT temporal-hold; drill the
               mechanism + brain-check).
  INVALID   : arena invalid OR positive control did not fire (uninterpretable).
  MIDDLE    : arena-middle validity band with control fired.

Pure-Python (numpy only). Reuses arena + menu modules. No substrate atoms, no
torch, no queue/GPU, no origin push. Runs inline in seconds. Multi-seed (identical
splits across all forms; discriminator = marginal balanced-acc race).

Run:
  python experiments/exp_multisource_arena_temporal_hold_recover_v1.py --self-test
  python experiments/exp_multisource_arena_temporal_hold_recover_v1.py --profile smoke
  python experiments/exp_multisource_arena_temporal_hold_recover_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (numpy design/validity cell; queue/substrate mandates n/a):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - no bare except; deterministic FIXED-int seeds (no hash()-derived seeds); no list(set())
# - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
# - start-marker + crash-diagnostic + per-seed heartbeat written
# - arms_differ: route vs static_full vs race vs fusion decisions hash-checked distinct
# - baseline-in-band: static_full_logistic marginal checked in (0.05, 0.95)
# - discriminator survives scale: full-N marginal race is the discriminator; smoke uses
#   full menu at reduced-N; positive control fires the temporal discriminator explicitly
# - CRLB: crlb_n/a = "classification balanced-acc bands, no Cramer-Rao noise floor applies"
# - all reported numbers MEASURED@ this run's metrics.json unless tagged else
# - real code path: exercises A.build_arena + A/M fit forms (the real reused substrate-arena code)

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

# --- reuse the arena + menu verbatim ----------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_multisource_arena_v1 as A  # noqa: E402
import exp_multisource_arena_combination_menu_v1 as M  # noqa: E402

ANCHOR_NAME = "multisource_arena_temporal_hold_recover_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_temporal_hold_recover_v1")

sigmoid = A.sigmoid
_balanced_acc = A._balanced_acc
pearson = A.pearson

# pre-registered bands
TIE_EPS = 0.010
X_BAND = 0.030
# positive control must show hold/oracle beat decide-at-arrival by at least this,
# with static_arrival pinned below POSCTRL_ARR_MAX (near chance).
POSCTRL_MIN_GAP = 0.15
POSCTRL_ARR_MAX = 0.62

# TEMPORAL schedule -- set A PRIORI (STC finite-capture-window shape), NOT swept to
# favour the window. delay in {1..D_MAX}; a corroboration COUNTS if delay <= WINDOW.
# The primary competitor (static_full_logistic) sees the SAME windowed recurrence
# as the route, so WINDOW affects both equally and cannot rig the route contrast.
WINDOW = 4
D_MAX = 8

NAMES = ["unexpectedness", "schema_fit", "importance", "recurrence"]
ARRIVAL_SIGNALS = ["unexpectedness", "schema_fit", "importance"]  # available at t0
# recurrence is the WINDOW signal (accrues); its two versions:
#   recurrence_arrival = corroboration visible at t0 (initiator only ~ n=1)
#   recurrence_window  = corroboration accrued within [t0, t0+WINDOW]

FLAT_FULL_COMPETITORS = ["static_full_logistic", "precision_fusion",
                         "multiplicative_gate"]
BRAIN_FAITHFUL = ["route_hold_recover", "precision_fusion", "multiplicative_gate",
                  "race_2accumulator"]


# ============================================================================
# temporal overlay on the reused arena
# ============================================================================
def _corrected_count(asserts_mask, clusters, K):
    """Copy-corrected corroboration = # distinct DETECTED independent source
    clusters among the masked asserting-true sources. asserts_mask: (K,S) bool."""
    out = np.zeros(K)
    for c in range(K):
        srcs = np.where(asserts_mask[c])[0]
        if len(srcs):
            out[c] = len(set(int(clusters[s]) for s in srcs))
    return out


def build_temporal(cfg, rng, window=WINDOW, d_max=D_MAX):
    """Reuse A.build_arena verbatim, then overlay a TEMPORAL report-arrival
    schedule. Returns (arena, extras) where extras carries the arrival-vs-window
    recurrence split. Delays are drawn INDEPENDENTLY of truth (self-test ST-D
    verifies) so the temporal schedule cannot leak the label."""
    arena = A.build_arena(cfg, rng)
    K, S = arena["reports"].shape
    clusters = A.detect_dependence(arena["value"], cfg.reliabilities, cfg)

    # per (claim, source) report delay: initiator (first asserting source, by index)
    # reports at delay 0; every other asserting source at a truth-independent
    # uniform delay in [1, d_max].
    delay = np.full((K, S), -1, dtype=int)
    initiator = np.full(K, -1, dtype=int)
    for c in range(K):
        asserting = np.where(arena["reports"][c])[0]
        if len(asserting) == 0:
            continue
        init = int(asserting[0])
        initiator[c] = init
        delay[c, init] = 0
        for s in asserting:
            if s == init:
                continue
            delay[c, s] = int(rng.integers(1, d_max + 1))

    asserts_true = arena["asserts_true"]
    within = (delay >= 0) & (delay <= window)
    at_arrival = (delay == 0)
    asserts_true_window = asserts_true & within
    asserts_true_arrival = asserts_true & at_arrival

    rec_window = _corrected_count(asserts_true_window, clusters, K)
    rec_arrival = _corrected_count(asserts_true_arrival, clusters, K)

    # arrival signals (all available at t0)
    surprise = A.signal_unexpectedness(arena)
    schema = A.signal_schema_fit(arena)
    importance = A.signal_importance(arena)

    extras = dict(clusters=clusters, delay=delay, initiator=initiator,
                  rec_window=rec_window, rec_arrival=rec_arrival,
                  surprise=surprise, schema=schema, importance=importance,
                  within=within)
    return arena, extras


# ============================================================================
# route_hold_recover -- the brain-faithful temporal cascade (novel form)
# ============================================================================
def fit_route_hold_recover(X_arr_tr, X_full_tr, ytr, cols):
    """Brain-faithful CLS provisional-hold-then-recover cascade, built on the SAME
    precision-weighted score core as precision_fusion (M._precision_weights + NP
    threshold) so the ONLY thing that distinguishes this arm from the flat fusion
    competitor is the TEMPORAL BRANCH STRUCTURE -- not a weaker classifier core. A
    route tie therefore means the branch/hold adds nothing; a route loss cannot be
    blamed on a crippled core.

    Per claim, using the shared precision weights w and NP threshold tau:
      s_arr = X_arr @ w   (decision available AT ARRIVAL, n=1: arrival recurrence)
      s_win = X_full @ w  (decision after HOLDING the window: accrued recurrence)
      1. salience one-shot bypass : very-high importance -> assimilate (1)
      2. provisional decision at arrival : prov = (s_arr >= tau)
      3. HOLD + RECOVER : a provisionally-DISCARDED claim whose within-window
         corroboration contribution crosses a recover-threshold is CONSOLIDATED (1);
         a provisionally-KEPT claim whose window corroboration collapses below a
         decay-threshold DECAYS unsupported -> DISCARD (0).
      4. reliability gate : arrival evidence very low AND not salient -> DISCARD (0).
    Branch knobs (recover/decay percentiles, bypass on/off, gate on/off) are
    TRAIN-SELECTED (max train balanced-acc); the score core + tau stay principled.
    X_arr and X_full differ ONLY in the recurrence column (arrival vs windowed) --
    the temporal-hold axis. Returns diagnostics incl. n_recovered / n_decayed (how
    many claims the hold actually revised)."""
    w, mu1, mu0 = M._precision_weights(X_full_tr, ytr)
    base = float(np.clip(ytr.mean(), 1e-3, 1 - 1e-3))
    mid = 0.5 * float(np.dot(w, mu1 + mu0))
    tau = mid - np.log(base / (1 - base))

    im, rc = cols["importance"], cols["recurrence"]
    s_arr_tr = X_arr_tr @ w
    rec_contr_tr = w[rc] * X_full_tr[:, rc]     # windowed corroboration contribution
    imp_contr_tr = w[im] * X_full_tr[:, im]

    def make(rec_q, decay_q, use_bypass, byp_q, use_gate, gate_q):
        rec_hi = float(np.quantile(rec_contr_tr, rec_q))
        rec_lo = float(np.quantile(rec_contr_tr, decay_q))
        byp_th = float(np.quantile(imp_contr_tr, byp_q))
        gate_th = float(np.quantile(s_arr_tr, gate_q))

        def decide(X_arr, X_full, want_diag=False):
            s_arr = X_arr @ w
            rec_c = w[rc] * X_full[:, rc]
            imp_c = w[im] * X_full[:, im]
            prov = (s_arr >= tau).astype(int)
            dec = prov.copy()
            recovered = (prov == 0) & (rec_c >= rec_hi)      # window capture
            dec[recovered] = 1
            decayed = (prov == 1) & (rec_c <= rec_lo)        # unsupported decay
            dec[decayed] = 0
            if use_gate:
                dec[(s_arr < gate_th) & (imp_c < byp_th)] = 0
            if use_bypass:
                dec[imp_c >= byp_th] = 1                      # salience one-shot bypass
            if want_diag:
                return dec.astype(int), int(recovered.sum()), int(decayed.sum())
            return dec.astype(int)
        return decide

    best_cfg, best_acc = None, -1.0
    for rec_q in (0.60, 0.75, 0.90):
        for decay_q in (0.10, 0.25):
            for ub in (False, True):
                for ug in (False, True):
                    dec = make(rec_q, decay_q, ub, 0.90, ug, 0.15)
                    acc = _balanced_acc(dec(X_arr_tr, X_full_tr), ytr)
                    if acc > best_acc:
                        best_acc, best_cfg = acc, (rec_q, decay_q, ub, 0.90, ug, 0.15)
    decider = make(*best_cfg)
    _, n_rec, n_dec = decider(X_arr_tr, X_full_tr, want_diag=True)
    return decider, dict(cfg=dict(rec_q=best_cfg[0], decay_q=best_cfg[1],
                                  bypass=best_cfg[2], gate=best_cfg[4]),
                         train_bal_acc=float(best_acc),
                         n_recovered_train=int(n_rec), n_decayed_train=int(n_dec))


# ============================================================================
# self-tests (guard a vacuous / rigged race; exercise real reused fit code)
# ============================================================================
def _synth_cols():
    return {n: i for i, n in enumerate(NAMES)}


def _standardize_on_train(X, tr):
    mu = X[tr].mean(axis=0)
    sd = X[tr].std(axis=0) + 1e-9
    return (X - mu) / sd


def st_a_linear_guard(seed):
    """ST-A: on a linear-additive truth with ALL features at arrival, the FLAT
    competitors (logistic + precision_fusion) MUST recover a strong separator.
    Guards the anti-rig: a route 'win' can never be a flat-competitor-is-broken
    artifact."""
    rng = np.random.default_rng(seed + 80000)
    n = 3000
    X = rng.normal(size=(n, 4))
    w = np.array([1.0, 1.0, 1.0, 1.0])
    truth = ((X @ w + 0.6 * rng.normal(size=n)) > 0).astype(int)
    tr, te = slice(0, n // 2), slice(n // 2, n)
    cols = _synth_cols()
    log_pred, _ = A.fit_weighted_sum(X[tr], truth[tr])
    la = _balanced_acc(log_pred(X[te]), truth[te])
    fus_pred, _ = M.fit_precision_fusion(X[tr], truth[tr], cols)
    fa = _balanced_acc(fus_pred(X[te]), truth[te])
    fired = (fa >= la - 0.03) and (la > 0.75)
    return dict(logistic=float(la), fusion=float(fa), fired=bool(fired))


def positive_control(seed):
    """ST-B analog (temporal). Arrival features = pure noise; truth is decided by
    WITHIN-WINDOW corroboration (>=2). A hold/oracle policy PROVABLY beats any
    decide-at-arrival single-shot decision; static_arrival is pinned near chance.
    Fires iff route AND oracle beat static_arrival by >= POSCTRL_MIN_GAP and
    static_arrival stays < POSCTRL_ARR_MAX. Proves the harness can express the
    temporal advantage IF it is real."""
    rng = np.random.default_rng(seed + 90000)
    n = 1400
    corrob = rng.integers(0, 5, size=n).astype(float)      # 0..4 within-window
    flip = (rng.random(n) < 0.05).astype(int)              # 5% label noise
    truth = ((corrob >= 2).astype(int)) ^ flip
    su = rng.normal(size=n)
    sf = rng.normal(size=n)
    im = rng.normal(size=n)
    rec_arrival = np.zeros(n)                              # nothing accrued at t0
    rec_window = corrob + 0.30 * rng.normal(size=n)        # noisy windowed readout
    cols = _synth_cols()
    Xarr = np.column_stack([su, sf, im, rec_arrival])
    Xfull = np.column_stack([su, sf, im, rec_window])
    tr, te = slice(0, n // 2), slice(n // 2, n)
    Xarrz = _standardize_on_train(Xarr, tr)
    Xfullz = _standardize_on_train(Xfull, tr)
    ytr, yte = truth[tr], truth[te]

    pa, _ = A.fit_weighted_sum(Xarrz[tr], ytr)
    acc_arr = _balanced_acc(pa(Xarrz[te]), yte)
    pf, _ = A.fit_weighted_sum(Xfullz[tr], ytr)
    acc_full = _balanced_acc(pf(Xfullz[te]), yte)
    rdec, _ = fit_route_hold_recover(Xarrz[tr], Xfullz[tr], ytr, cols)
    acc_route = _balanced_acc(rdec(Xarrz[te], Xfullz[te]), yte)
    # hand-built oracle: threshold the RAW windowed corroboration at the true cut
    acc_oracle = _balanced_acc((rec_window[te] >= 2.0).astype(int), yte)

    fired = (acc_route - acc_arr >= POSCTRL_MIN_GAP
             and acc_oracle - acc_arr >= POSCTRL_MIN_GAP
             and acc_arr < POSCTRL_ARR_MAX)
    return dict(static_arrival=float(acc_arr), static_full=float(acc_full),
                route=float(acc_route), oracle=float(acc_oracle),
                route_minus_arrival=float(acc_route - acc_arr),
                oracle_minus_arrival=float(acc_oracle - acc_arr),
                fired=bool(fired))


def st_d_delay_independence(cfg, extras, truth):
    """ST-D: report-delay schedule is truth-independent (no leakage). mean delay
    per claim over its later reports vs truth -> |r| must be small."""
    delay = extras["delay"]
    K = delay.shape[0]
    mean_delay = np.zeros(K)
    for c in range(K):
        later = delay[c][delay[c] > 0]
        mean_delay[c] = later.mean() if len(later) else 0.0
    r = pearson(mean_delay, truth.astype(float))
    return dict(delay_truth_abs_r=float(abs(r)), ok=bool(abs(r) < 0.15))


# ============================================================================
# per-seed temporal race (identical split across all forms)
# ============================================================================
def _hash_dec(a):
    return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()


def race_one_seed(cfg, seed, window=WINDOW, d_max=D_MAX):
    rng = np.random.default_rng(seed)
    arena, extras = build_temporal(cfg, rng, window, d_max)
    gen_fails, _, _ = A.run_self_tests(arena)
    truth = arena["truth"].astype(int)
    clusters = extras["clusters"]

    raw_full = {"unexpectedness": extras["surprise"], "schema_fit": extras["schema"],
                "importance": extras["importance"], "recurrence": extras["rec_window"]}
    raw_arr = {"unexpectedness": extras["surprise"], "schema_fit": extras["schema"],
               "importance": extras["importance"], "recurrence": extras["rec_arrival"]}

    # ---- arena-validity precondition (on the TEMPORAL signal set) ----
    pairs = [(a, b) for i, a in enumerate(NAMES) for b in NAMES[i + 1:]]
    rvals = {f"{a}|{b}": abs(pearson(raw_full[a], raw_full[b])) for a, b in pairs}
    max_abs_r = max(rvals.values())
    cmi = {}
    for n in NAMES:
        others = [raw_full[o] for o in NAMES if o != n]
        s = -raw_full[n] if n == "unexpectedness" else raw_full[n]
        cmi[n] = A.conditional_mi(s, truth, others)
    n_informative = int(sum(v > 1e-3 for v in cmi.values()))
    stress = A.copying_stress_test(cfg, rng, clusters)
    delay_ind = st_d_delay_independence(cfg, extras, truth)

    # ---- identical split + standardization for every form ----
    K = cfg.n_claims
    idx = rng.permutation(K)
    n_test = int(cfg.test_frac * K)
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    cols = _synth_cols()

    def build_X(raw):
        mu = np.array([raw[n][train_idx].mean() for n in NAMES])
        sd = np.array([raw[n][train_idx].std() + 1e-9 for n in NAMES])
        X = np.column_stack([raw[n] for n in NAMES])
        return (X - mu) / sd

    Xz_full = build_X(raw_full)
    Xz_arr = build_X(raw_arr)
    Xtr_f, Xte_f = Xz_full[train_idx], Xz_full[test_idx]
    Xtr_a, Xte_a = Xz_arr[train_idx], Xz_arr[test_idx]
    ytr, yte = truth[train_idx], truth[test_idx]

    preds = {}
    # decide-at-arrival static baseline (NO windowed recurrence)
    p, _ = A.fit_weighted_sum(Xtr_a, ytr)
    preds["static_arrival_logistic"] = p(Xte_a)
    # strong flat-wait competitors (full features incl. windowed recurrence)
    p, _ = A.fit_weighted_sum(Xtr_f, ytr)
    preds["static_full_logistic"] = p(Xte_f)
    p, _ = M.fit_precision_fusion(Xtr_f, ytr, cols)
    preds["precision_fusion"] = p(Xte_f)
    p, _ = M.fit_multiplicative_gate(Xtr_f, ytr, cols)
    preds["multiplicative_gate"] = p(Xte_f)
    p, _ = M.fit_race_accumulator(Xtr_f, ytr, cols)
    preds["race_2accumulator"] = p(Xte_f)
    p, _ = A.fit_best_single(Xtr_f, ytr, cols)
    preds["best_single"] = p(Xte_f)
    best_single_name = A.fit_best_single(Xtr_f, ytr, cols)[1]["signal"]
    # THE brain-faithful temporal cascade
    dec, rinfo = fit_route_hold_recover(Xtr_a, Xtr_f, ytr, cols)
    preds["route_hold_recover"] = dec(Xte_a, Xte_f)

    marginal = {k: float(_balanced_acc(v, yte)) for k, v in preds.items()}

    # arms-must-differ across the key contrast set
    distinct = len({_hash_dec(preds[k]) for k in
                    ["route_hold_recover", "static_full_logistic",
                     "precision_fusion", "race_2accumulator"]})
    arms_differ = distinct >= 3

    return dict(gen_self_test_fails=gen_fails, best_single_signal=best_single_name,
                marginal=marginal, arms_differ=bool(arms_differ),
                max_abs_r=float(max_abs_r), pairwise_abs_r=rvals,
                conditional_mi=cmi, n_informative=n_informative,
                copying=stress, delay_independence=delay_ind,
                route_cfg=rinfo["cfg"], n_test=int(n_test),
                truth_base_rate=float(truth.mean()))


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
def aggregate_and_verdict(profile, seeds, per_seed, posctrls, st_a, elapsed):
    forms = ["route_hold_recover", "static_arrival_logistic", "static_full_logistic",
             "precision_fusion", "multiplicative_gate", "race_2accumulator",
             "best_single"]

    def mean_over(metric, key):
        return float(np.mean([s[metric][key] for s in per_seed]))

    marg = {k: mean_over("marginal", k) for k in forms}
    route = marg["route_hold_recover"]
    # Competitor set = EVERY non-route form except the floor. CRITICAL: this INCLUDES
    # static_arrival_logistic (decide-at-arrival) -- the strongest static logistic and
    # the one a genuine temporal-hold policy must beat. Excluding it flatters the route
    # whenever the windowed feature is noise (the flat-full forms then dip below the
    # arrival baseline and the route "wins" without any temporal-hold advantage).
    competitor_forms = (["static_arrival_logistic"] + FLAT_FULL_COMPETITORS
                        + ["race_2accumulator"])
    competitor = max(marg[k] for k in competitor_forms)
    competitor_name = max(competitor_forms, key=lambda k: marg[k])
    margin = route - competitor
    temporal_info_gain = marg["static_full_logistic"] - marg["static_arrival_logistic"]
    route_over_arrival = route - marg["static_arrival_logistic"]

    # arena validity (aggregate; reuse arena bands)
    max_abs_r = float(np.max([s["max_abs_r"] for s in per_seed]))
    mean_ratio = float(np.mean([s["copying"]["corr_ratio"] for s in per_seed]))
    worst_p = float(np.max([s["copying"]["corr_pvalue"] for s in per_seed]))
    min_info = int(np.min([s["n_informative"] for s in per_seed]))
    delay_ok = all(s["delay_independence"]["ok"] for s in per_seed)
    pair_keys = list(per_seed[0]["pairwise_abs_r"].keys())
    mean_pair_r = {k: float(np.mean([s["pairwise_abs_r"][k] for s in per_seed]))
                   for k in pair_keys}
    mean_cmi = {n: float(np.mean([s["conditional_mi"][n] for s in per_seed]))
                for n in NAMES}
    arena_valid = (max_abs_r < 0.30 and mean_ratio >= 1.5 and worst_p < 0.05
                   and min_info >= 3 and delay_ok)
    arena_invalid = (max_abs_r > 0.60 or mean_ratio < 1.05 or worst_p >= 0.05
                     or not delay_ok)
    arena_middle = not (arena_valid or arena_invalid)
    arena_verdict = ("ARENA_VALID" if arena_valid else
                     "ARENA_INVALID" if arena_invalid else "ARENA_MIDDLE")

    # positive control + ST-A guard (must fire on ALL seeds)
    posctrl_fired = all(p["fired"] for p in posctrls)
    st_a_fired = st_a["fired"]
    control_ok = posctrl_fired and st_a_fired

    baseline_in_band = 0.05 < marg["static_full_logistic"] < 0.95
    arms_differ_all = all(s["arms_differ"] for s in per_seed)

    # ---- verdict ----
    if not control_ok:
        verdict = "INVALID_CONTROL_DID_NOT_FIRE"
    elif arena_invalid:
        verdict = "INVALID_ARENA"
    elif not baseline_in_band:
        verdict = "INVALID_BASELINE_OUT_OF_BAND"
    elif arena_middle:
        verdict = "MIDDLE_ARENA_VALIDITY"
    elif margin > TIE_EPS and temporal_info_gain > TIE_EPS:
        # route beats the BEST baseline (incl. decide-at-arrival) AND the window
        # genuinely carried incremental truth-info -> the win IS temporal-hold.
        verdict = "HARD_PASS"
    elif margin > TIE_EPS:
        # route is the best form but the window carried no info (temporal_info_gain
        # <= TIE_EPS) -> the edge is NOT temporal-hold; do not over-claim.
        verdict = "MIDDLE_STRUCTURE_EDGE_NOT_TEMPORAL"
    elif margin < -X_BAND:
        verdict = "HARD_FAIL_ROUTE_LOSES"
    else:
        verdict = "HARD_FAIL_ROUTE_TIES"

    route_value_localization = (
        "route_temporal_hold_beats_best_baseline_with_genuine_window_info"
        if verdict == "HARD_PASS"
        else "route_is_best_form_but_no_window_info_edge_is_not_temporal_hold"
        if verdict == "MIDDLE_STRUCTURE_EDGE_NOT_TEMPORAL"
        else "temporal_info_present_but_route_ties_flat_readout_of_it"
        if (verdict.startswith("HARD_FAIL") and temporal_info_gain > TIE_EPS)
        else "no_temporal_info_to_exploit_route_ties_decide_at_arrival"
        if verdict.startswith("HARD_FAIL") else "n/a")

    pc = {k: float(np.mean([p[k] for p in posctrls]))
          for k in ["static_arrival", "route", "oracle", "route_minus_arrival",
                    "oracle_minus_arrival"]}

    msg = ("profile=%s seeds=%d | %s | MARGINAL: route=%.3f vs competitor[%s]=%.3f "
           "(margin=%+.3f TIE_EPS=%.3f) | static_arrival=%.3f static_full=%.3f "
           "fusion=%.3f mult=%.3f race=%.3f best_single[%s]=%.3f | "
           "temporal_info_gain(full-arrival)=%+.3f route_over_arrival=%+.3f | "
           "ARENA %s (max|r|=%.3f copy=%.2fx cMI=%d/4 delay_ok=%s) | "
           "POSCTRL fired=%s (route=%.3f oracle=%.3f arrival=%.3f) ST-A fired=%s | %s" %
           (profile, len(seeds), verdict, route, competitor_name, competitor, margin,
            TIE_EPS, marg["static_arrival_logistic"], marg["static_full_logistic"],
            marg["precision_fusion"], marg["multiplicative_gate"],
            marg["race_2accumulator"], per_seed[0]["best_single_signal"],
            marg["best_single"], temporal_info_gain, route_over_arrival,
            arena_verdict, max_abs_r, mean_ratio, min_info, delay_ok,
            posctrl_fired, pc["route"], pc["oracle"], pc["static_arrival"],
            st_a_fired, route_value_localization))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "run_mode": profile,
        "primary_metric": "marginal_heldout_balanced_accuracy",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND,
                  "POSCTRL_MIN_GAP": POSCTRL_MIN_GAP},
        "temporal_schedule": {"window": WINDOW, "d_max": D_MAX,
                              "note": "a_priori_not_swept"},
        "marginal_bal_acc": marg,
        "contract": {
            "route_hold_recover": route,
            "competitor_best": competitor, "competitor_name": competitor_name,
            "margin": float(margin),
            "temporal_info_gain_full_minus_arrival": float(temporal_info_gain),
            "route_over_static_arrival": float(route_over_arrival),
            "route_value_localization": route_value_localization,
        },
        "arena_validity": {
            "verdict": arena_verdict, "max_abs_r": max_abs_r,
            "mean_pairwise_abs_r": mean_pair_r, "copying_ratio_mean": mean_ratio,
            "copying_worst_pvalue": worst_p, "mean_conditional_mi": mean_cmi,
            "min_informative_signals_of_4": min_info, "delay_independence_ok": delay_ok,
        },
        "controls": {
            "positive_control_fired_all_seeds": posctrl_fired,
            "positive_control_per_seed": posctrls,
            "positive_control_mean": pc,
            "st_a_linear_guard": st_a,
        },
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ_all),
        "best_single_signal": per_seed[0]["best_single_signal"],
        "per_seed": per_seed,
    }


# ============================================================================
# main
# ============================================================================
def _run_selftests():
    fails, notes = [], []
    st_a = st_a_linear_guard(11)
    notes.append("ST-A linear guard: logistic=%.3f fusion=%.3f fired=%s"
                 % (st_a["logistic"], st_a["fusion"], st_a["fired"]))
    if not st_a["fired"]:
        fails.append("ST-A: flat competitors do NOT recover linear separator "
                     "(fusion=%.3f logistic=%.3f) -> flat-competitor impl weak/broken"
                     % (st_a["fusion"], st_a["logistic"]))
    for sd in (11, 23, 37):
        pc = positive_control(sd)
        notes.append("ST-B posctrl seed=%d: static_arrival=%.3f route=%.3f oracle=%.3f "
                     "(route-arr=%+.3f oracle-arr=%+.3f) fired=%s"
                     % (sd, pc["static_arrival"], pc["route"], pc["oracle"],
                        pc["route_minus_arrival"], pc["oracle_minus_arrival"], pc["fired"]))
        if not pc["fired"]:
            fails.append("ST-B seed %d: temporal positive control did NOT fire "
                         "(route-arr=%+.3f oracle-arr=%+.3f arrival=%.3f) -> harness "
                         "cannot express temporal advantage; a route tie would be "
                         "uninterpretable" % (sd, pc["route_minus_arrival"],
                                              pc["oracle_minus_arrival"], pc["static_arrival"]))
    # ST-D on a tiny real temporal arena (delay-truth independence)
    cfg = A.ArenaConfig(profile="smoke", seed=11)
    cfg.n_claims = 420
    cfg.n_schema_entities = 100
    rng = np.random.default_rng(11)
    arena, extras = build_temporal(cfg, rng)
    d = st_d_delay_independence(cfg, extras, arena["truth"])
    notes.append("ST-D delay-truth |r|=%.3f ok=%s" % (d["delay_truth_abs_r"], d["ok"]))
    if not d["ok"]:
        fails.append("ST-D: report delay correlates with truth (|r|=%.3f) -> temporal "
                     "schedule leaks the label" % d["delay_truth_abs_r"])
    # ST-generator: reuse arena's own generator self-tests
    gfails, _, _ = A.run_self_tests(arena)
    notes.append("ST-gen arena self-tests: %d fail(s)" % len(gfails))
    fails.extend("ST-gen: " + f for f in gfails)
    return fails, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="controls-only: ST-A linear guard + ST-B temporal posctrl + "
                         "ST-D delay-independence + arena generator self-tests")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = _run_selftests()
        print("=== TEMPORAL CELL SELF-TESTS (controls guard vacuous/rigged race) ===")
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
        print("SELFTEST_PASS: ST-A guard + ST-B temporal positive control fire; "
              "delay-independence + arena generator self-tests pass")
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71] if profile == "full" else [11, 23, 37])
    _write_start_marker(len(seeds), profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # controls first (interpretability gate)
    st_a = st_a_linear_guard(11)
    posctrls = [positive_control(sd) for sd in seeds]

    per_seed = []
    print("=== profile=%s seeds=%s window=%d d_max=%d ===" % (profile, seeds, WINDOW, D_MAX))
    print("  ST-A linear guard fired=%s | POSCTRL fired(all)=%s"
          % (st_a["fired"], all(p["fired"] for p in posctrls)), flush=True)
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
        print("  seed %d MARGINAL: route=%.3f static_arr=%.3f static_full=%.3f "
              "fusion=%.3f mult=%.3f race=%.3f | max|r|=%.3f cMI=%d/4" %
              (sd, m["route_hold_recover"], m["static_arrival_logistic"],
               m["static_full_logistic"], m["precision_fusion"],
               m["multiplicative_gate"], m["race_2accumulator"],
               res["max_abs_r"], res["n_informative"]), flush=True)

    out = aggregate_and_verdict(profile, seeds, per_seed, posctrls, st_a,
                                time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78)
    print("TEMPORAL HOLD-THEN-RECOVER RACE -- PRIMARY = MARGINAL held-out balanced acc")
    mg = out["marginal_bal_acc"]
    order = ["route_hold_recover", "static_arrival_logistic", "static_full_logistic",
             "precision_fusion", "multiplicative_gate", "race_2accumulator",
             "best_single"]
    label = {"route_hold_recover": "route_hold_recover  [BF, temporal cascade]",
             "static_arrival_logistic": "static_arrival_log  [ENG, decide-at-arrival]",
             "static_full_logistic": "static_full_logistic[ENG, flat-wait ceiling]",
             "precision_fusion": "precision_fusion    [BF, flat-wait]",
             "multiplicative_gate": "multiplicative_gate [BF, flat-wait]",
             "race_2accumulator": "race_2accumulator   [BF, temporal race]",
             "best_single": "best_single         [ENG, floor]"}
    print("  %-42s %8s" % ("form", "MARGINAL"))
    for k in order:
        print("  %-42s %8.3f" % (label[k], mg[k]))
    ct = out["contract"]
    print("\n  CONTRACT: route=%.3f vs competitor[%s]=%.3f  margin=%+.3f (TIE_EPS=%.3f)"
          % (ct["route_hold_recover"], ct["competitor_name"], ct["competitor_best"],
             ct["margin"], TIE_EPS))
    print("  temporal_info_gain (static_full - static_arrival) = %+.3f"
          % ct["temporal_info_gain_full_minus_arrival"])
    print("  route_over_static_arrival = %+.3f" % ct["route_over_static_arrival"])
    print("  localization: %s" % ct["route_value_localization"])
    av = out["arena_validity"]
    print("\n  ARENA VALIDITY: %s (max|r|=%.3f copy=%.2fx cMI=%d/4 delay_ok=%s)"
          % (av["verdict"], av["max_abs_r"], av["copying_ratio_mean"],
             av["min_informative_signals_of_4"], av["delay_independence_ok"]))
    pcm = out["controls"]["positive_control_mean"]
    print("  POSITIVE CONTROL fired(all seeds)=%s: route=%.3f oracle=%.3f "
          "static_arrival=%.3f (route-arr=%+.3f oracle-arr=%+.3f)"
          % (out["controls"]["positive_control_fired_all_seeds"], pcm["route"],
             pcm["oracle"], pcm["static_arrival"], pcm["route_minus_arrival"],
             pcm["oracle_minus_arrival"]))
    print("  ST-A linear guard fired=%s (logistic=%.3f fusion=%.3f)"
          % (st_a["fired"], st_a["logistic"], st_a["fusion"]))
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
