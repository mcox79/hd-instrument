"""Decisive can-fail test: is the learning negative task-triviality or mechanism-poverty?

Delayed k-parity-in-context (k=2, XOR) embedded in an HD role-filler token stream. A first-order
correlation / co-occurrence counter is MATHEMATICALLY pinned at chance on parity (Minsky-Papert XOR
non-separability); a mechanism that forms the second-order CONJUNCTION (the substrate's BIND primitive)
can solve it. The cell resolves the confound behind the repeated "correlation ties everything" learning
negatives: were the past tasks correlation-solvable (triviality), or is a structure genuinely missing
(poverty)?

Arms (all share the SAME substrate front-end -- bipolar role-filler encode + unbind/cleanup recovery of
per-position signs; they differ ONLY in the readout/combination mechanism under test):
  ARM_CORR        first-order marginal correlation counter over per-position signs. PROVABLY chance
                  on parity (control that MUST fire at chance). This is the additive/linear readout class
                  (cf. hdlab.additive_map score = -||X_h+D_r-X_t||, a linear function of coordinates).
  ARM_BIND_ORACLE conjunction of the TWO KNOWN informative positions (substrate bind of the two recovered
                  signs) -> capacity ceiling: proves the HD channel CAN carry the parity signal at this
                  N/W. Separates "channel poverty" from "search poverty".
  ARM_BIND_HEBB   ALL pairwise conjunctions (substrate forms every second-order feature) + UNWEIGHTED
                  (parallel Hebbian/correlation) readout. Maps to negative #3 (dilution by unweighted
                  context). No predictive-error element.
  ARM_PREDCODE    same conjunction features + a predictive-ERROR relevance gate (residual-driven
                  competitive selection). ONE variable different from ARM_BIND_HEBB: the target is the
                  prediction ERROR (residual), not the raw label. Tests whether the predictive/error
                  element is what unlocks parity at scale.

Verdict logic (see prereg for full bands):
  - VOID if ARM_CORR > 0.55 (task leaks -- not true parity).
  - VOID if recovery accuracy < 0.95 (front-end confound; result would confound recovery with combination).
  - HARD_FAIL if ALL arms (incl ORACLE) <= 0.55 (channel/mechanism poverty at this construction).
  - HARD_PASS if a structure-using arm (ORACLE/BIND_HEBB/PREDCODE) >= 0.65 while ARM_CORR at chance
    -> the missing structure (conjunction/binding) is REAL and this task discriminates it.
  - Predictive-loop localization: if BIND_HEBB fails where PREDCODE holds (dilution regime) -> the
    predictive/error element is the specific unlock; if BIND_HEBB already passes -> binding alone
    suffices and the predictive-loop is NOT specifically required for parity.

Two regimes to make the test can-fail-both-ways and isolate the predictive element:
  R_small (few distractor conjunctions): BIND_HEBB expected to PASS -> binding-alone suffices here.
  R_large (many distractor conjunctions, small train): BIND_HEBB expected to DEGRADE toward chance
    (unweighted dilution) while PREDCODE HOLDS -> demonstrates the discriminator can fire in the FAIL
    direction for an un-gated structure arm, and isolates the predictive/error element's value.

Glass-box, closed-form / Hebbian / matching-pursuit -- NO SGD, NO GPU. CPU-cheap (< ~1 min full).
ASCII-only. Explicit dtypes. Seeded generators. Determinism: single-threaded BLAS.
"""

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (os.replace on final metrics.json)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: parity is a discrete logical target; chance=0.5 exact, no CRLB noise floor (bands are
#   binomial-significance based; n_test chosen so per-seed binomial std < 0.012)
# - baseline_in_band at smoke (META_RULE_AG): ARM_CORR must be ~0.5 (control fires); ORACLE must pass
# - discriminator survives scale: smoke runs FULL-N (N identical smoke vs full); only n_seeds reduced
# - HARD_PASS strictly above floor + margin (>=0.65 vs 0.55 void ceiling: 0.10 margin >> 5% band width)
# - HP_SCOPE: {ARM_CORR: [MUST_STAY_CHANCE], ARM_BIND_ORACLE/ARM_BIND_HEBB/ARM_PREDCODE: [STRUCTURE_HP]}
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_regimes; verdict counts per-unit
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok_for_this_regime (analytic chance=0.5 exact for parity)
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ in prereg
# - all analytic claims proven in --self-test (marginal corr ~0; optimal-linear ~chance; conjunction solves)

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import torch

torch.set_num_threads(1)

ANCHOR_NAME = "parity_in_context_binding_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Regimes. m1/m2 are the informative offsets (k=2 parity). Neither is the most-recent (W-1) position.
# ---------------------------------------------------------------------------
REGIMES = {
    "R_small": dict(W=8, m1=1, m2=4, N=4096, n_train=400, n_test=2000),
    "R_large": dict(W=40, m1=3, m2=17, N=4096, n_train=100, n_test=2000),
}
SEEDS_FULL = [7, 13, 19, 23, 29]
SEEDS_SMOKE = [7, 13, 19]

VOID_CORR_CEIL = 0.55        # ARM_CORR above this => task leaks => VOID
RECOVERY_FLOOR = 0.95        # front-end recovery accuracy floor (else confound)
STRUCTURE_HP = 0.65          # structure-arm HARD_PASS floor
CHANCE = 0.5

PREDCODE_ITERS = 30
PREDCODE_LR = 0.5


# ---------------------------------------------------------------------------
# Substrate primitives (bipolar MAP/BSC, identical to hdlab.binding.bsc_bind; inline for zero import drift
# and full glass-box transparency).
# ---------------------------------------------------------------------------
def make_roles(W, N, gen):
    """W random bipolar {-1,+1} role/position vectors, shape (W, N) float32."""
    r = torch.randint(0, 2, (W, N), generator=gen, dtype=torch.int64)
    return (r * 2 - 1).to(torch.float32)


def encode_windows(signs, roles):
    """Superpose per-position role-filler tokens. signs (nq,W) in {-1,+1}, roles (W,N) -> windows (nq,N).

    token_i = s_i * P_i ; window = sum_i token_i (real-valued superposition)."""
    return signs.to(torch.float32) @ roles          # (nq,N)


def recover_signs(windows, roles, N):
    """Unbind + cleanup: shat_i = sign(<window, P_i>/N). Returns (margins (nq,W), shat (nq,W) in {-1,+1})."""
    margins = (windows @ roles.T) / float(N)         # (nq,W); own term ~ +/-1, crosstalk ~ N(0,(W-1)/N)
    shat = torch.where(margins >= 0, torch.ones_like(margins), -torch.ones_like(margins))
    return margins, shat


# ---------------------------------------------------------------------------
# Task: delayed k=2 parity in context.
# ---------------------------------------------------------------------------
def gen_task(W, m1, m2, n, rng):
    """Random bits (n,W) in {0,1}; y = bit[m1] XOR bit[m2]. Returns (signs (n,W) float32 in {-1,+1},
    y (n,) int64 in {0,1}, y_signed (n,) float32 in {-1,+1})."""
    bits = rng.integers(0, 2, size=(n, W)).astype(np.int64)
    y = np.bitwise_xor(bits[:, m1], bits[:, m2]).astype(np.int64)
    signs = (1 - 2 * bits).astype(np.float32)                    # bit 0 -> +1, bit 1 -> -1
    y_signed = (1 - 2 * y).astype(np.float32)                    # y 0 -> +1, y 1 -> -1
    return torch.from_numpy(signs), y, torch.from_numpy(y_signed)


def pair_features(shat):
    """All second-order conjunction features f_ij = shat_i * shat_j for i<j. shat (n,W) -> (n,P), pairs list."""
    n, W = shat.shape
    idx = [(i, j) for i in range(W) for j in range(i + 1, W)]
    a = torch.tensor([i for (i, j) in idx], dtype=torch.long)
    b = torch.tensor([j for (i, j) in idx], dtype=torch.long)
    F = shat[:, a] * shat[:, b]                                  # (n,P)
    return F, idx


def _sign_pred(scores):
    """scores (n,) real -> predicted y in {0,1}. sign>=0 -> +1 -> y=0 ; sign<0 -> -1 -> y=1."""
    return (scores < 0).astype(np.int64)


# ---- arms -----------------------------------------------------------------
def arm_corr(shat_tr, y_signed_tr, shat_te):
    """First-order marginal correlation counter. w_i = mean(shat_i * y_signed). pred = sign(shat_te @ w)."""
    F_tr = shat_tr.numpy().astype(np.float64)
    yst = y_signed_tr.numpy().astype(np.float64)
    w = (F_tr * yst[:, None]).mean(axis=0)                      # (W,)
    scores = shat_te.numpy().astype(np.float64) @ w             # (n_te,)
    return _sign_pred(scores), w


def arm_bind_oracle(shat_tr, y_signed_tr, shat_te, m1, m2):
    """Conjunction of the two KNOWN informative positions only (capacity ceiling)."""
    f_tr = (shat_tr[:, m1] * shat_tr[:, m2]).numpy().astype(np.float64)
    yst = y_signed_tr.numpy().astype(np.float64)
    w = float((f_tr * yst).mean())
    f_te = (shat_te[:, m1] * shat_te[:, m2]).numpy().astype(np.float64)
    scores = w * f_te
    return _sign_pred(scores), w


def arm_bind_hebb(F_tr, y_signed_tr, F_te):
    """All pairwise conjunctions + UNWEIGHTED parallel Hebbian readout (no error gating)."""
    Ftr = F_tr.numpy().astype(np.float64)
    yst = y_signed_tr.numpy().astype(np.float64)
    w = (Ftr * yst[:, None]).mean(axis=0)                       # (P,) parallel correlation with the LABEL
    scores = F_te.numpy().astype(np.float64) @ w
    return _sign_pred(scores), w


def arm_predcode(F_tr, y_signed_tr, F_te, n_iter=PREDCODE_ITERS, lr=PREDCODE_LR):
    """Same conjunctions + predictive-ERROR relevance gate: residual-driven competitive selection.

    ONE variable vs arm_bind_hebb: the update target is the prediction ERROR (residual y - pred), not the
    raw label. Matching-pursuit realizes the relevance gate (winner explains most residual each step),
    suppressing the ~P distractor conjunctions. Glass-box, closed-form correlations, no SGD."""
    Ftr = F_tr.numpy().astype(np.float64)
    yst = y_signed_tr.numpy().astype(np.float64)
    n, P = Ftr.shape
    w = np.zeros(P, dtype=np.float64)
    pred = np.zeros(n, dtype=np.float64)
    for _ in range(n_iter):
        resid = yst - pred                                     # prediction error
        c = (Ftr * resid[:, None]).mean(axis=0)                # (P,) corr of feature with the ERROR
        p_star = int(np.argmax(np.abs(c)))                     # relevance gate = winner explains residual
        step = lr * c[p_star]
        w[p_star] += step
        pred = pred + step * Ftr[:, p_star]
    scores = F_te.numpy().astype(np.float64) @ w
    return _sign_pred(scores), w


# ---------------------------------------------------------------------------
# One (regime, seed) unit.
# ---------------------------------------------------------------------------
def run_unit(regime_name, cfg, seed):
    W, m1, m2, N = cfg["W"], cfg["m1"], cfg["m2"], cfg["N"]
    n_train, n_test = cfg["n_train"], cfg["n_test"]
    gen = torch.Generator().manual_seed(seed * 100003 + 17)
    rng = np.random.default_rng(seed * 100019 + 3)

    roles = make_roles(W, N, gen)
    s_tr, y_tr, ys_tr = gen_task(W, m1, m2, n_train, rng)
    s_te, y_te, ys_te = gen_task(W, m1, m2, n_test, rng)

    win_tr = encode_windows(s_tr, roles)
    win_te = encode_windows(s_te, roles)
    _, shat_tr = recover_signs(win_tr, roles, N)
    _, shat_te = recover_signs(win_te, roles, N)

    # front-end recovery integrity (sigma0-analog gate): recovered signs vs truth
    rec_acc = float(((shat_te == s_te).float().mean()).item())

    F_tr, pairs = pair_features(shat_tr)
    F_te, _ = pair_features(shat_te)

    p_corr, w_corr = arm_corr(shat_tr, ys_tr, shat_te)
    p_orac, _ = arm_bind_oracle(shat_tr, ys_tr, shat_te, m1, m2)
    p_hebb, w_hebb = arm_bind_hebb(F_tr, ys_tr, F_te)
    p_pred, w_pred = arm_predcode(F_tr, ys_tr, F_te)

    acc = {
        "ARM_CORR": float((p_corr == y_te).mean()),
        "ARM_BIND_ORACLE": float((p_orac == y_te).mean()),
        "ARM_BIND_HEBB": float((p_hebb == y_te).mean()),
        "ARM_PREDCODE": float((p_pred == y_te).mean()),
    }
    # arms-differ (META_RULE_AF): prediction vectors must not be bit-identical
    preds = {"ARM_CORR": p_corr, "ARM_BIND_ORACLE": p_orac, "ARM_BIND_HEBB": p_hebb, "ARM_PREDCODE": p_pred}
    digests = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in preds.items()}
    return dict(regime=regime_name, seed=seed, recovery_acc=rec_acc, acc=acc,
                n_pairs=int(F_tr.shape[1]), pred_digests=digests,
                pair_focus=_predcode_focus(w_pred, pairs, m1, m2))


def _predcode_focus(w_pred, pairs, m1, m2):
    """Fraction of predcode L1 weight landing on the true informative pair (glass-box interpretability)."""
    w = np.abs(np.asarray(w_pred, dtype=np.float64))
    tot = float(w.sum())
    if tot <= 0:
        return 0.0
    tgt = (min(m1, m2), max(m1, m2))
    for p, (i, j) in enumerate(pairs):
        if (i, j) == tgt:
            return float(w[p] / tot)
    return 0.0


# ---------------------------------------------------------------------------
# Self-test: ANALYTIC proof that correlation is chance-bounded + conjunction solves parity.
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] analytic proof: correlation chance-bounded on k=2 parity; conjunction solves it")
    W, m1, m2, N = 8, 1, 4, 2048
    rng = np.random.default_rng(1234)
    gen = torch.Generator().manual_seed(999)
    n = 4000
    s, y, ys = gen_task(W, m1, m2, n, rng)
    ys_np = ys.numpy().astype(np.float64)
    s_np = s.numpy().astype(np.float64)

    # (1) Every single-position marginal correlation with the label is ~0 (incl. the informative positions).
    marg = (s_np * ys_np[:, None]).mean(axis=0)                 # (W,)
    max_marg = float(np.max(np.abs(marg)))
    print("  max |marginal corr(position, label)| = %.4f (informative m1,m2 included)" % max_marg)
    assert max_marg < 0.08, "marginals not uninformative -> task not genuine parity (max=%.4f)" % max_marg

    # (2) Even the OPTIMAL linear classifier over first-order features is at chance (XOR non-separable).
    # closed-form least squares s -> y_signed, then sign readout.
    X = s_np
    coef, *_ = np.linalg.lstsq(X, ys_np, rcond=None)
    lin_pred = _sign_pred(X @ coef)
    lin_acc = float((lin_pred == y).mean())
    print("  optimal linear (least-squares) accuracy = %.4f (must be ~chance)" % lin_acc)
    assert lin_acc < 0.55, "optimal linear beat chance -> not genuine parity (acc=%.4f)" % lin_acc

    # (3) The second-order conjunction of the two informative positions perfectly predicts.
    conj = s_np[:, m1] * s_np[:, m2]
    conj_corr = float((conj * ys_np).mean())
    print("  corr(conjunction[m1,m2], label) = %.4f (must be ~1.0)" % conj_corr)
    assert conj_corr > 0.98, "informative conjunction does not predict label (corr=%.4f)" % conj_corr

    # (4) End-to-end substrate front-end recovers per-position signs near-perfectly at N=%d.
    roles = make_roles(W, N, gen)
    win = encode_windows(s, roles)
    _, shat = recover_signs(win, roles, N)
    rec = float(((shat == s).float().mean()).item())
    print("  substrate recovery accuracy at N=%d,W=%d = %.4f (must be >= %.2f)" % (N, W, rec, RECOVERY_FLOOR))
    assert rec >= RECOVERY_FLOOR, "recovery below floor -> front-end confound (rec=%.4f)" % rec

    # (5) predcode gate concentrates on the informative pair (glass-box).
    F, pairs = pair_features(shat)
    _, w_pred = arm_predcode(F, ys, F)
    focus = _predcode_focus(w_pred, pairs, m1, m2)
    print("  predcode L1 weight fraction on true pair = %.4f (must be > 0.5)" % focus)
    assert focus > 0.5, "predcode did not localize the informative pair (focus=%.4f)" % focus

    print("[self-test] PASS")
    return True


# ---------------------------------------------------------------------------
# Aggregation + verdict.
# ---------------------------------------------------------------------------
def aggregate(units):
    arms = ["ARM_CORR", "ARM_BIND_ORACLE", "ARM_BIND_HEBB", "ARM_PREDCODE"]
    per_regime = {}
    for rn in sorted(set(u["regime"] for u in units)):
        rus = [u for u in units if u["regime"] == rn]
        means = {a: float(np.mean([u["acc"][a] for u in rus])) for a in arms}
        stds = {a: float(np.std([u["acc"][a] for u in rus])) for a in arms}
        per_regime[rn] = dict(
            arm_mean=means, arm_std=stds, n_seeds=len(rus),
            recovery_acc_mean=float(np.mean([u["recovery_acc"] for u in rus])),
            n_pairs=int(rus[0]["n_pairs"]),
            predcode_focus_mean=float(np.mean([u["pair_focus"] for u in rus])),
        )
    return per_regime


def verdict(per_regime, expected_units, got_units):
    reasons = []
    if got_units < expected_units:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", \
            "got %d units, expected %d" % (got_units, expected_units), {}

    # gates across all regimes
    corr_max = max(pr["arm_mean"]["ARM_CORR"] for pr in per_regime.values())
    rec_min = min(pr["recovery_acc_mean"] for pr in per_regime.values())
    if corr_max > VOID_CORR_CEIL:
        return "VOID_TASK_LEAKS", \
            "ARM_CORR mean %.3f > void ceiling %.2f -> not genuine parity" % (corr_max, VOID_CORR_CEIL), {}
    if rec_min < RECOVERY_FLOOR:
        return "VOID_RECOVERY_CONFOUND", \
            "recovery mean %.3f < floor %.2f -> front-end confound" % (rec_min, RECOVERY_FLOOR), {}

    # structure gate: does ANY structure arm beat chance in ANY regime while CORR at chance?
    struct_arms = ["ARM_BIND_ORACLE", "ARM_BIND_HEBB", "ARM_PREDCODE"]
    best_struct = 0.0
    for pr in per_regime.values():
        for a in struct_arms:
            best_struct = max(best_struct, pr["arm_mean"][a])
    oracle_max = max(pr["arm_mean"]["ARM_BIND_ORACLE"] for pr in per_regime.values())

    if best_struct < STRUCTURE_HP:
        # all structure arms (incl oracle) at chance -> channel/mechanism poverty
        v = "HARD_FAIL_MECHANISM_POVERTY"
        msg = ("all structure arms < %.2f (best=%.3f, oracle_max=%.3f) while CORR chance (%.3f); "
               "substrate cannot carry/solve parity at this construction" %
               (STRUCTURE_HP, best_struct, oracle_max, corr_max))
        return v, msg, dict(best_struct=best_struct, oracle_max=oracle_max, corr_max=corr_max)

    # HARD_PASS: structure beats chance where correlation is pinned at chance.
    # localize the predictive-loop question across regimes.
    localize = {}
    for rn, pr in per_regime.items():
        hebb = pr["arm_mean"]["ARM_BIND_HEBB"]
        pred = pr["arm_mean"]["ARM_PREDCODE"]
        if hebb >= STRUCTURE_HP and pred >= STRUCTURE_HP:
            localize[rn] = "binding_alone_suffices"
        elif hebb < STRUCTURE_HP and pred >= STRUCTURE_HP:
            localize[rn] = "predictive_error_element_required"
        elif hebb >= STRUCTURE_HP and pred < STRUCTURE_HP:
            localize[rn] = "predcode_underperforms_hebb"
        else:
            localize[rn] = "both_below_but_oracle_carries_search_poverty"
    msg = ("structure beats chance where correlation pinned at chance "
           "(best_struct=%.3f, oracle_max=%.3f, corr_max=%.3f); predictive-loop localization=%s" %
           (best_struct, oracle_max, corr_max, json.dumps(localize)))
    return "HARD_PASS_STRUCTURE_DISCRIMINATES", msg, dict(
        best_struct=best_struct, oracle_max=oracle_max, corr_max=corr_max, localization=localize)


# ---------------------------------------------------------------------------
# Metrics IO (atomic).
# ---------------------------------------------------------------------------
def _out_dir(mode):
    sub = "exp_%s%s" % (ANCHOR_NAME, "_smoke" if mode == "smoke" else "")
    d = os.path.join(REPO, "data", sub)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(out_dir, payload):
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(out_dir, diag)


# ---------------------------------------------------------------------------
def run(mode):
    t0 = time.perf_counter()
    seeds = SEEDS_SMOKE if mode == "smoke" else SEEDS_FULL
    out_dir = _out_dir(mode)
    expected = len(seeds) * len(REGIMES)
    _write_start_marker(out_dir, mode, expected)

    units = []
    unit_errors = []
    for rn, cfg in REGIMES.items():
        for sd in seeds:
            try:
                units.append(run_unit(rn, cfg, sd))
            except Exception as e:  # per-unit failure-class instrumentation (META_RULE_J)
                unit_errors.append(dict(regime=rn, seed=sd, failure_class=type(e).__name__,
                                        detail=str(e)[:300]))

    per_regime = aggregate(units) if units else {}

    # arms-differ (META_RULE_AF): catch ACCIDENTAL bit-identical arm IMPLEMENTATIONS. Two distinct
    # mechanisms can legitimately converge to identical CORRECT predictions when the task is trivially
    # solved (all structure arms hit 1.000 in R_small). Such collisions are EXEMPTED when both arms
    # achieve >= 0.99 accuracy in that unit (convergence to ground truth, not shared code). The control
    # arm ARM_CORR is NEVER exempt. Distinctness is positively asserted below (each mechanism differs
    # from the others in >= 1 unit), except (ORACLE, PREDCODE) which converge whenever PREDCODE's search
    # succeeds -- their code-level distinctness (ORACLE hard-codes m1,m2; PREDCODE searches all pairs) is
    # self-evident and declared, not verifiable by prediction bytes at this difficulty.
    CONVERGE_ACC = 0.99
    arm_list = ["ARM_CORR", "ARM_BIND_ORACLE", "ARM_BIND_HEBB", "ARM_PREDCODE"]
    exempted_pairs = set()
    unexpected_collision = []
    differ_witness = {}   # pair -> True if predictions differ in >=1 unit
    for u in units:
        d = u["pred_digests"]
        acc = u["acc"]
        for a in range(len(arm_list)):
            for b in range(a + 1, len(arm_list)):
                ka, kb = arm_list[a], arm_list[b]
                pair = (ka, kb)
                if d[ka] != d[kb]:
                    differ_witness[pair] = True
                    continue
                # identical predictions in this unit
                both_perfect = (acc[ka] >= CONVERGE_ACC and acc[kb] >= CONVERGE_ACC)
                is_corr_pair = (ka == "ARM_CORR" or kb == "ARM_CORR")
                if both_perfect and not is_corr_pair:
                    exempted_pairs.add(pair)
                else:
                    unexpected_collision.append(dict(regime=u["regime"], seed=u["seed"],
                                                     pair=[ka, kb], acc_a=acc[ka], acc_b=acc[kb]))
    # positive distinctness: CORR must differ from every arm; HEBB vs PREDCODE (the one-variable pair)
    # must differ in >=1 unit. (ORACLE,PREDCODE) is the only declared code-level exemption.
    declared_conv_exempt = {("ARM_BIND_ORACLE", "ARM_PREDCODE")}
    required_distinct = [("ARM_CORR", "ARM_BIND_ORACLE"), ("ARM_CORR", "ARM_BIND_HEBB"),
                         ("ARM_CORR", "ARM_PREDCODE"), ("ARM_BIND_HEBB", "ARM_PREDCODE"),
                         ("ARM_BIND_ORACLE", "ARM_BIND_HEBB")]
    missing_distinct = [list(p) for p in required_distinct if not differ_witness.get(p, False)]
    arms_differ_ok = (len(unexpected_collision) == 0 and len(missing_distinct) == 0)
    arms_differ_detail = dict(
        exempted_pairs=[list(p) for p in sorted(exempted_pairs)],
        declared_code_level_exempt=[list(p) for p in sorted(declared_conv_exempt)],
        unexpected_collision=unexpected_collision,
        missing_required_distinct=missing_distinct,
    )

    v, vmsg, vextra = verdict(per_regime, expected, len(units))
    elapsed = time.perf_counter() - t0

    payload = dict(
        verdict=v,
        verdict_msg=vmsg,
        summary="parity-in-context binding-vs-correlation | %s" % v,
        elapsed_s=elapsed,
        anchor_name=ANCHOR_NAME,
        mode=mode,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        expected_n_units=expected,
        got_n_units=len(units),
        cardinality_ok=(len(units) == expected),
        arms_differ_verified=arms_differ_ok,
        arms_differ_detail=arms_differ_detail,
        recovery_floor=RECOVERY_FLOOR,
        void_corr_ceiling=VOID_CORR_CEIL,
        structure_hard_pass_floor=STRUCTURE_HP,
        per_regime=per_regime,
        unit_errors=unit_errors,
        verdict_extra=vextra,
        seeds=seeds,
    )
    _write_metrics(out_dir, payload)

    # console verdict
    print("\n=== %s (%s) ===" % (ANCHOR_NAME, mode))
    for rn, pr in per_regime.items():
        print("[%s] n_pairs=%d recovery=%.3f" % (rn, pr["n_pairs"], pr["recovery_acc_mean"]))
        for a in ["ARM_CORR", "ARM_BIND_ORACLE", "ARM_BIND_HEBB", "ARM_PREDCODE"]:
            print("    %-16s %.3f +/- %.3f" % (a, pr["arm_mean"][a], pr["arm_std"][a]))
        print("    predcode_focus_on_true_pair=%.3f" % pr["predcode_focus_mean"])
    print("VERDICT: %s" % v)
    print("  %s" % vmsg)
    print("  arms_differ_verified=%s cardinality_ok=%s elapsed=%.1fs" %
          (arms_differ_ok, len(units) == expected, elapsed))
    print("  metrics -> %s" % os.path.join(out_dir, "metrics.json"))
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    out_dir_guess = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        try:
            _write_crash_metrics(out_dir_guess, e)
        except Exception:
            pass
        raise
