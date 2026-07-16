"""Combination-rule MENU re-race in a CONJUNCTION-TRUTH arena.

COMPANION to experiments/exp_multisource_arena_combination_menu_v1.py (commit
6741d9e1f), which raced the 9-form menu on the VET'd ADDITIVE-truth arena and
found the brain-faithful MULTIPLICATIVE gate LOSES (mult=0.851 vs additive-
logistic=0.863, gap -0.012) -- because that arena's truth is additive-linear by
construction, so a single linear boundary is the right form and the AND-gate
form is mismatched.

THIS cell asks the mirror question: when the regime's TRUTH is genuinely
INTERACTION-structured (an AND-gate world), does the multiplicative gate WIN and
REVERSE the additive arena's ordering? The gate-race self-test already hinted it
(mult 0.904 vs logistic 0.814 on a synthetic AND control); this establishes it
properly inside the full validity-disciplined arena.

REUSE (no new arena machinery, no new gate forms):
  - exp_multisource_arena_v1 (A): build_arena + the 4 signal functions + copy
    detector + validity harness (conditional_mi, copying_stress_test, pearson,
    within_cell_bal_acc) + fit_weighted_sum / fit_route / fit_best_single. The
    ONLY change is ArenaConfig.truth_mode = "conjunction" (a backward-compatible
    knob added to A; the additive default is byte-identical to the VET'd v1 and
    the conjunction branch draws NO rng, so v1 + menu_v1 reproducibility is
    untouched -- reconfirmed by re-running both after the edit).
  - exp_multisource_arena_combination_menu_v1 (M): the 6 brain-faithful + 3
    engineering fit functions, raced VERBATIM on identical splits/seeds.

CONJUNCTION TRUTH (A._truth_logit "conjunction" branch): a dominant 4-way soft-
AND g(Ls)*g(Lo)*g(Lt)*g(Li), g(L)=sigmoid(gain*L) -- truth is likely only when
ALL four latents are high (matches the multiplicative-gate functional form; a
single linear boundary cannot express "need all four") -- plus a WEAK linear
main-effect so each signal keeps a marginal foothold (base-rate + conditional-MI
health). The four latents are the SAME four independent generative processes;
only their COMBINATION into truth changed from sum to product.

STAGING (VET discipline; report in order):
  A) generator self-tests (A.run_self_tests reused) at the conjunction truth.
  B) ARENA-VALIDITY precondition FIRST -- recomputed for the CONJUNCTION truth
     (it does NOT inherit the additive VET): pairwise |r| decorrelation,
     conditional-MI per signal | other three, copying stress-test, base-rate,
     AND a NON-ADDITIVITY certification (a linear-in-latents logistic must
     UNDER-fit vs an interaction-augmented logistic on held-out truth -- proves
     the arena is genuinely conjunction-structured, not additive in disguise).
     The gate race is NOT trusted unless the arena is BOTH valid AND certified
     conjunctive.
  C) only if arena valid + conjunctive: the 9-form MARGINAL held-out race.

DECISIVE metric (PRIMARY): MARGINAL held-out balanced accuracy. gap =
multiplicative_gate - additive_logistic.
PRE-REG BANDS: TIE_EPS = 0.010, X_BAND = 0.030 (balanced-acc).
  HARD-PASS : gap >= X_BAND  (multiplicative decisively BEATS logistic ->
              its advantage IS conjunction-structure; ordering reversed).
  HARD-FAIL : gap <= TIE_EPS (mult ties/loses EVEN on genuinely-conjunctive
              truth -> its advantage is NOT conjunction-structure; drill +
              brain-check).
  MIDDLE    : TIE_EPS < gap < X_BAND.
  NON-ADDITIVITY gate: mean latent-space (interaction - linear) held-out gap
  must be >= 0.03 or the arena is NOT_CONJUNCTIVE and the question is void.

Pure-Python (numpy only). No atoms, no torch, no queue, no push. Runs inline in
seconds. Multi-seed (identical splits across all forms).

Run:
  python experiments/exp_multisource_arena_conjunction_menu_v1.py --self-test
  python experiments/exp_multisource_arena_conjunction_menu_v1.py --profile smoke
  python experiments/exp_multisource_arena_conjunction_menu_v1.py --profile full
"""

# CELL-TEMPLATE MANDATORY (numpy design/validity cell):
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - no bare except; no hash()-derived seeds; FIXED integer seeds only
# - final metrics via tmp + os.replace (atomic; META_RULE_AH tmp_replace)
# - start-marker + crash-diagnostic + per-seed heartbeat
# - arms_differ: menu forms produce distinct decisions (hash-checked)
# - baseline-in-band: additive_logistic marginal checked in (0.05, 0.95)
# - discriminator (mult-vs-logistic gap) verified present at smoke before full
# - all reported numbers MEASURED @ this run's metrics.json unless tagged else

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

# --- reuse the arena + the menu forms verbatim ------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp_multisource_arena_v1 as A  # noqa: E402
import exp_multisource_arena_combination_menu_v1 as M  # noqa: E402

ANCHOR_NAME = "multisource_arena_conjunction_menu_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO, "data", "exp_multisource_arena_conjunction_menu_v1")

_balanced_acc = A._balanced_acc

# pre-registered bands
TIE_EPS = 0.010
X_BAND = 0.030
NONADD_MARGIN = 0.030   # latent-space (interaction - linear) held-out gap floor

BRAIN_FAITHFUL = M.BRAIN_FAITHFUL
FORMS = ["route_np", "route_ewma", "route_stn", "precision_fusion",
         "additive_logistic", "multiplicative_gate", "race_2accumulator",
         "route_uncal_grid", "best_single"]


# conjunction-truth params (pinned here so the cell is self-contained + fully
# reproducible independent of A.ArenaConfig defaults). Tuned in-cell for a
# genuinely-conjunctive-yet-VALID arena: dominant 4-way AND, base-rate above the
# reused ST7 floor (0.20), signals still decorrelated + conditionally informative.
CONJ_GAIN = 5.0
CONJ_SHIFT = 0.0
CONJ_W_AND = 7.0
CONJ_W_MAIN = 0.10
CONJ_W_BIAS = 0.10


def conjunction_cfg(profile, seed):
    """ArenaConfig with the CONJUNCTION truth mode + pinned conjunction params."""
    cfg = A.ArenaConfig(profile=profile, seed=seed)
    cfg.truth_mode = "conjunction"
    cfg.conj_gain = CONJ_GAIN
    cfg.conj_shift = CONJ_SHIFT
    cfg.conj_w_and = CONJ_W_AND
    cfg.conj_w_main = CONJ_W_MAIN
    cfg.conj_w_bias = CONJ_W_BIAS
    return cfg


# ============================================================================
# NON-ADDITIVITY certification (latent space; certifies the truth STRUCTURE
# independently of any gate form). A linear-in-latents logistic must UNDER-fit
# vs an interaction-augmented logistic on HELD-OUT truth.
# ============================================================================
def certify_nonadditive(arena, truth, train_idx, test_idx):
    Ls, Lo = arena["L_schema"], arena["L_source"]
    Lt, Li = arena["L_temporal"], arena["L_importance"]
    lat = [Ls, Lo, Lt, Li]
    lin = np.column_stack(lat)
    inter_cols = list(lat)
    for a in range(4):
        for b in range(a + 1, 4):
            inter_cols.append(lat[a] * lat[b])       # 6 pairwise products
    inter_cols.append(Ls * Lo * Lt * Li)             # the 4-way product
    inter = np.column_stack(inter_cols)

    def std_fit_acc(F):
        mu = F[train_idx].mean(axis=0)
        sd = F[train_idx].std(axis=0) + 1e-9
        Fz = (F - mu) / sd
        pred, _ = A.fit_weighted_sum(Fz[train_idx], truth[train_idx])
        return float(_balanced_acc(pred(Fz[test_idx]), truth[test_idx]))

    lin_acc = std_fit_acc(lin)
    int_acc = std_fit_acc(inter)
    return {"lin_acc": lin_acc, "int_acc": int_acc,
            "gap": float(int_acc - lin_acc)}


# ============================================================================
# per-seed: build conjunction arena -> validity -> race (identical split)
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

    # ---- (B) arena validity, RECOMPUTED for the conjunction truth ----
    pairs = [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]
    rvals = {"%s|%s" % (a, b): abs(A.pearson(raw[a], raw[b])) for a, b in pairs}
    max_abs_r = max(rvals.values())
    cmi = {}
    for n in names:
        others = [raw[o] for o in names if o != n]
        s = -raw[n] if n == "unexpectedness" else raw[n]
        cmi[n] = A.conditional_mi(s, truth, others)
    n_informative = int(sum(v > 1e-3 for v in cmi.values()))
    # copying stress uses a SEPARATE rng stream so it does not perturb the split
    stress = A.copying_stress_test(cfg, np.random.default_rng(seed + 7919), clusters)
    base_rate = float(truth.mean())

    # ---- identical split + standardization (rng AFTER build, as in v1/menu) ----
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

    # ---- non-additivity certification on the SAME held-out split ----
    nonadd = certify_nonadditive(arena, truth, train_idx, test_idx)

    # ---- (C) race every form on the SAME train ----
    preds, infos = {}, {}
    f, i = M.fit_route_calibrated(Xtr, ytr, cols, method="np")
    preds["route_np"], infos["route_np"] = f(Xte), i
    f, i = M.fit_route_calibrated(Xtr, ytr, cols, method="ewma")
    preds["route_ewma"], infos["route_ewma"] = f(Xte), i
    f, i = M.fit_route_calibrated(Xtr, ytr, cols, method="stn")
    preds["route_stn"], infos["route_stn"] = f(Xte), i
    f, i = M.fit_precision_fusion(Xtr, ytr, cols)
    preds["precision_fusion"], infos["precision_fusion"] = f(Xte), i
    f, i = A.fit_weighted_sum(Xtr, ytr)
    preds["additive_logistic"], infos["additive_logistic"] = f(Xte), i
    f, i = M.fit_multiplicative_gate(Xtr, ytr, cols)
    preds["multiplicative_gate"], infos["multiplicative_gate"] = f(Xte), i
    f, i = M.fit_race_accumulator(Xtr, ytr, cols)
    preds["race_2accumulator"], infos["race_2accumulator"] = f(Xte), i
    f, i = A.fit_route(Xtr, ytr, cols)
    preds["route_uncal_grid"], infos["route_uncal_grid"] = f(Xte), i
    f, i = A.fit_best_single(Xtr, ytr, cols)
    preds["best_single"], infos["best_single"] = f(Xte), i
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

    distinct = len({_hash_dec(preds[k]) for k in
                    ["route_np", "precision_fusion", "additive_logistic",
                     "multiplicative_gate", "race_2accumulator"]})
    arms_differ = distinct >= 3

    return dict(gen_self_test_fails=gen_fails, best_single_signal=best_single_name,
                marginal=marginal, within_cell=within, arms_differ=bool(arms_differ),
                pairwise_abs_r=rvals, max_abs_r=float(max_abs_r),
                conditional_mi=cmi, n_informative=n_informative,
                copying=stress, base_rate=base_rate, nonadditivity=nonadd,
                n_test=int(n_test))


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
    def mean_over(metric, key):
        return float(np.mean([s[metric][key] for s in per_seed]))

    marg = {k: mean_over("marginal", k) for k in FORMS}
    within = {k: mean_over("within_cell", k) for k in FORMS}
    logistic = marg["additive_logistic"]
    mult = marg["multiplicative_gate"]
    gap = mult - logistic                       # DECISIVE quantity

    # arena validity aggregates (conjunction truth)
    max_abs_r = float(np.max([s["max_abs_r"] for s in per_seed]))
    min_info = int(np.min([s["n_informative"] for s in per_seed]))
    mean_ratio = float(np.mean([s["copying"]["corr_ratio"] for s in per_seed]))
    worst_p = float(np.max([s["copying"]["corr_pvalue"] for s in per_seed]))
    base_rates = [s["base_rate"] for s in per_seed]
    base_rate_ok = all(0.20 <= b <= 0.80 for b in base_rates)
    mean_nonadd = float(np.mean([s["nonadditivity"]["gap"] for s in per_seed]))
    mean_lin = float(np.mean([s["nonadditivity"]["lin_acc"] for s in per_seed]))
    mean_int = float(np.mean([s["nonadditivity"]["int_acc"] for s in per_seed]))
    pair_keys = list(per_seed[0]["pairwise_abs_r"].keys())
    mean_pair_r = {k: float(np.mean([s["pairwise_abs_r"][k] for s in per_seed]))
                   for k in pair_keys}
    mean_cmi = {n: float(np.mean([s["conditional_mi"][n] for s in per_seed]))
                for n in ["unexpectedness", "schema_fit", "recurrence", "importance"]}

    baseline_in_band = 0.05 < logistic < 0.95
    arms_differ_all = all(s["arms_differ"] for s in per_seed)

    # arena verdict (must be valid AND certified conjunctive before gate trusted)
    arena_structurally_valid = (max_abs_r < 0.30 and mean_ratio >= 1.5
                                and worst_p < 0.05 and min_info >= 3
                                and base_rate_ok and baseline_in_band)
    arena_conjunctive = mean_nonadd >= NONADD_MARGIN
    if not arena_structurally_valid:
        arena_verdict = "ARENA_INVALID"
    elif not arena_conjunctive:
        arena_verdict = "ARENA_NOT_CONJUNCTIVE"
    else:
        arena_verdict = "ARENA_VALID_CONJUNCTIVE"

    # decisive gate (only trusted if arena valid + conjunctive)
    if arena_verdict != "ARENA_VALID_CONJUNCTIVE":
        decisive = "GATE_NOT_TRUSTED"
    elif gap >= X_BAND:
        decisive = "MULTIPLICATIVE_WINS"
    elif gap <= TIE_EPS:
        decisive = "MULTIPLICATIVE_TIES_OR_LOSES"
    else:
        decisive = "MULTIPLICATIVE_MIDDLE"

    # top-level verdict
    if arena_verdict == "ARENA_INVALID":
        verdict = "HARD_FAIL_ARENA_INVALID"
    elif arena_verdict == "ARENA_NOT_CONJUNCTIVE":
        verdict = "HARD_FAIL_ARENA_NOT_CONJUNCTIVE"
    elif decisive == "MULTIPLICATIVE_WINS":
        verdict = "HARD_PASS"
    elif decisive == "MULTIPLICATIVE_TIES_OR_LOSES":
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"

    # multiplicative rank among all forms on marginal (1 = best)
    order_by_marg = sorted(FORMS, key=lambda k: -marg[k])
    mult_rank = order_by_marg.index("multiplicative_gate") + 1
    best_form = order_by_marg[0]

    msg = ("profile=%s seeds=%d | %s | ARENA %s (max|r|=%.3f copy=%.2fx p<=%.4f "
           "cMI=%d/4 base=%.2f nonadd_gap=%.3f[lin=%.3f int=%.3f]) | DECISIVE "
           "mult=%.3f vs logistic=%.3f gap=%+.3f (%s) | mult_rank=%d/9 best=%s | "
           "menu-marg: fusion=%.3f route_np=%.3f race=%.3f uncal=%.3f single[%s]=%.3f"
           % (profile, len(seeds), verdict, arena_verdict, max_abs_r, mean_ratio,
              worst_p, min_info, float(np.mean(base_rates)), mean_nonadd, mean_lin,
              mean_int, mult, logistic, gap, decisive, mult_rank, best_form,
              marg["precision_fusion"], marg["route_np"], marg["race_2accumulator"],
              marg["route_uncal_grid"], per_seed[0]["best_single_signal"],
              marg["best_single"]))

    return {
        "verdict": verdict, "summary": verdict, "verdict_msg": msg,
        "elapsed_s": float(elapsed), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "profile": profile, "seeds": list(seeds),
        "primary_metric": "marginal_heldout_balanced_accuracy",
        "bands": {"TIE_EPS": TIE_EPS, "X_BAND": X_BAND, "NONADD_MARGIN": NONADD_MARGIN},
        "arena_validity": {
            "verdict": arena_verdict,
            "structurally_valid": bool(arena_structurally_valid),
            "certified_conjunctive": bool(arena_conjunctive),
            "max_abs_r": max_abs_r, "mean_pairwise_abs_r": mean_pair_r,
            "copying_ratio_mean": mean_ratio, "copying_worst_pvalue": worst_p,
            "mean_conditional_mi": mean_cmi, "min_informative_signals_of_4": min_info,
            "base_rates": base_rates, "base_rate_in_band": bool(base_rate_ok),
            "nonadditivity_gap_mean": mean_nonadd,
            "nonadditivity_lin_acc_mean": mean_lin,
            "nonadditivity_int_acc_mean": mean_int,
        },
        "decisive": {
            "verdict": decisive,
            "multiplicative_marginal": mult, "logistic_marginal": logistic,
            "gap_mult_minus_logistic": float(gap),
            "multiplicative_rank_of_9": int(mult_rank), "best_form": best_form,
        },
        "marginal_bal_acc": marg,
        "within_cell_bal_acc_secondary": within,
        "baseline_in_band": bool(baseline_in_band),
        "arms_differ_verified": bool(arms_differ_all),
        "best_single_signal": per_seed[0]["best_single_signal"],
        "per_seed": per_seed,
    }


# ============================================================================
# self-test (staging A): conjunction generator + non-additivity + menu guards
# ============================================================================
def run_conjunction_self_tests():
    """(1) generator self-tests pass at the conjunction truth; (2) truth is
    genuinely NON-additive (interaction logistic beats linear on held-out truth);
    (3) reuse M's menu guards (linear + AND controls) to confirm the fit
    functions are non-vacuous."""
    fails, notes = [], []

    cfg = conjunction_cfg("smoke", 11)
    cfg.n_claims = 600
    cfg.n_schema_entities = 120
    rng = np.random.default_rng(11)
    arena = A.build_arena(cfg, rng)
    gen_fails, gen_notes, _ = A.run_self_tests(arena)
    for nline in gen_notes:
        notes.append("  gen: " + nline)
    fails.extend(["conj-gen " + f for f in gen_fails])

    truth = arena["truth"].astype(int)
    K = cfg.n_claims
    idx = rng.permutation(K)
    nt = int(cfg.test_frac * K)
    test_idx, train_idx = idx[:nt], idx[nt:]
    na = certify_nonadditive(arena, truth, train_idx, test_idx)
    notes.append("NONADD: lin_acc=%.3f int_acc=%.3f gap=%+.3f (must be >= %.3f)"
                 % (na["lin_acc"], na["int_acc"], na["gap"], NONADD_MARGIN))
    if na["gap"] < NONADD_MARGIN:
        fails.append("NONADD: truth is not genuinely conjunctive (interaction "
                     "logistic gap=%.3f < %.3f); a linear model does NOT under-fit "
                     "-> arena would be additive-in-disguise" % (na["gap"], NONADD_MARGIN))
    br = float(truth.mean())
    notes.append("base-rate=%.3f (must be in [0.20, 0.80])" % br)
    if not 0.20 <= br <= 0.80:
        fails.append("base-rate degenerate at conjunction truth (%.3f)" % br)

    # reuse M's menu self-tests (linear-recovery + AND-beats-additive guards)
    m_fails, m_notes = M.run_menu_self_tests()
    for nline in m_notes:
        notes.append("  menu: " + nline)
    fails.extend(["menu " + f for f in m_fails])
    return fails, notes


# ============================================================================
# main
# ============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true",
                    help="staging A: conjunction generator + non-additivity + menu guards")
    ap.add_argument("--profile", choices=["smoke", "full"], default="full")
    args = ap.parse_args()
    t0 = time.perf_counter()

    if args.self_test:
        _write_start_marker(1, "self_test")
        fails, notes = run_conjunction_self_tests()
        print("=== STAGING A: CONJUNCTION GENERATOR + NON-ADDITIVITY SELF-TESTS ===",
              flush=True)
        for nline in notes:
            print("  " + nline, flush=True)
        if fails:
            print("SELF-TEST FAILED:", flush=True)
            for fmsg in fails:
                print("  FAIL: " + fmsg, flush=True)
            _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"),
                          {"verdict": "SELFTEST_FAIL", "summary": "SELFTEST_FAIL",
                           "verdict_msg": "; ".join(fails),
                           "elapsed_s": time.perf_counter() - t0,
                           "anchor_name": ANCHOR_NAME})
            return 2
        print("SELFTEST_PASS: conjunction truth certified non-additive; "
              "generator + menu guards pass", flush=True)
        return 0

    profile = args.profile
    seeds = ([11, 23, 37, 53, 71] if profile == "full" else [11, 23, 37])
    _write_start_marker(len(seeds), profile)
    hb_path = os.path.join(OUTPUT_DIR, "_heartbeat.jsonl")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    per_seed = []
    print("=== profile=%s seeds=%s (CONJUNCTION truth) ===" % (profile, seeds),
          flush=True)
    for si, sd in enumerate(seeds):
        cfg = conjunction_cfg(profile, sd)
        res = race_one_seed(cfg, sd)
        if res["gen_self_test_fails"]:
            print("SEED %d ARENA SELF-TEST FAIL: %s" % (sd, res["gen_self_test_fails"]),
                  flush=True)
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
        print("  seed %d: base=%.2f nonadd=%+.3f max|r|=%.3f cMI=%d/4 | MARGINAL "
              "mult=%.3f logistic=%.3f gap=%+.3f fusion=%.3f race=%.3f single=%.3f"
              % (sd, res["base_rate"], res["nonadditivity"]["gap"], res["max_abs_r"],
                 res["n_informative"], m["multiplicative_gate"], m["additive_logistic"],
                 m["multiplicative_gate"] - m["additive_logistic"],
                 m["precision_fusion"], m["race_2accumulator"], m["best_single"]),
              flush=True)

    out = aggregate_and_verdict(profile, seeds, per_seed, time.perf_counter() - t0)
    _atomic_write(os.path.join(OUTPUT_DIR, "metrics.json"), out)

    print("\n" + "=" * 78, flush=True)
    print("CONJUNCTION-TRUTH MENU RE-RACE -- PRIMARY = MARGINAL held-out bal-acc",
          flush=True)
    av = out["arena_validity"]
    print("STAGING B -- ARENA VALIDITY (conjunction truth): %s" % av["verdict"],
          flush=True)
    print("  max pairwise |r| = %.3f (< 0.30)   base-rate in band = %s" %
          (av["max_abs_r"], av["base_rate_in_band"]), flush=True)
    print("  copying stress   = %.2fx worst-p=%.4f   cMI informative = %d/4" %
          (av["copying_ratio_mean"], av["copying_worst_pvalue"],
           av["min_informative_signals_of_4"]), flush=True)
    print("  NON-ADDITIVITY   : lin_acc=%.3f int_acc=%.3f gap=%+.3f (>= %.3f = conjunctive)"
          % (av["nonadditivity_lin_acc_mean"], av["nonadditivity_int_acc_mean"],
             av["nonadditivity_gap_mean"], NONADD_MARGIN), flush=True)
    print("  conditional-MI | other 3: " +
          ", ".join("%s=%.4f" % (k, v) for k, v in av["mean_conditional_mi"].items()),
          flush=True)

    mg = out["marginal_bal_acc"]
    wc = out["within_cell_bal_acc_secondary"]
    order = ["multiplicative_gate", "additive_logistic", "precision_fusion",
             "route_np", "route_ewma", "route_stn", "race_2accumulator",
             "route_uncal_grid", "best_single"]
    label = {"multiplicative_gate": "F4 multiplicative     [BF-form] *",
             "additive_logistic": "F3 additive_logistic  [ENG,learned]",
             "precision_fusion": "F2 precision_fusion   [BF]",
             "route_np": "F1a route_np          [BF]",
             "route_ewma": "F1b route_ewma        [BF]",
             "route_stn": "F1c route_stn         [BF]",
             "race_2accumulator": "F5 race_2accumulator  [BF]",
             "route_uncal_grid": "-- route_uncal_grid   [ENG]",
             "best_single": "-- best_single        [ENG,floor]"}
    print("\nSTAGING C -- MENU RACE (marginal, sorted):", flush=True)
    print("  %-40s %8s %8s" % ("form", "MARGINAL", "within"), flush=True)
    for k in order:
        print("  %-40s %8.3f %8.3f" % (label[k], mg[k], wc[k]), flush=True)
    d = out["decisive"]
    print("\n  DECISIVE: multiplicative=%.3f vs additive_logistic=%.3f gap=%+.3f -> %s"
          % (d["multiplicative_marginal"], d["logistic_marginal"],
             d["gap_mult_minus_logistic"], d["verdict"]), flush=True)
    print("            (HARD-PASS gap>=%.3f; HARD-FAIL gap<=%.3f; mult_rank=%d/9 best=%s)"
          % (X_BAND, TIE_EPS, d["multiplicative_rank_of_9"], d["best_form"]), flush=True)
    print("\nTOP-LEVEL VERDICT: %s" % out["verdict"], flush=True)
    print("  " + out["verdict_msg"], flush=True)
    print("=" * 78, flush=True)
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
