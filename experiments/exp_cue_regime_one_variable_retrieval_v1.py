"""exp_cue_regime_one_variable_retrieval_v1 -- THE SAME ONE VARIABLE, ON THE RETRIEVAL SIDE.

FINDINGS LOG: notes/one_upstream_cause_findings_2026-08-17.md
SIBLING (bridging side, same design): experiments/exp_cue_regime_one_variable_v1.py

WHY THIS EXISTS. The sibling sweeps the exact-key fraction of a BRIDGING cue and reads off a
DETECTION THRESHOLD lambda_star -- the smallest fraction of the target's own identity that the
instrument can resolve when the rest of the cue is non-informative. That number only settles the
one-upstream-cause question if the SAME quantity is measured on the RETRIEVAL side, because the
whole claim is that the two nulls and the partial-cue cap are ONE finding. This cell supplies the
second half of the common currency.

THE ONE VARIABLE, identical in form to the sibling:

    cue(i, lam) = lam * l2n(Q_exact[i]) + (1 - lam) * l2n(filler_i)

  lam = 1.0 -> the cue IS the exact key. Addressing must read ~1.0000 (the landed value).
  lam = 0.0 with filler = Q_part -> the landed partial-cue read-out. REGRESSION-GATED against
           0.0223 tie-corrected on the full landed open pool, the sibling cell's own gate.

LADDERS
  E_PARTIAL_CUE     filler = the item's REAL held-out-sentence cue. The operating point.
  D_OTHER_PARTIAL   filler = ANOTHER item's partial cue (derangement, per seed, MAX DRAW).
                    Carries the same marginal statistics and ZERO information about this item.
  D_GAUSS           filler = Gaussian matched to Q_part's per-dimension mean and sd, per seed.

TWO MEASURES, NEVER AVERAGED TOGETHER
  M1 ADDRESSING  argmax_a cos(cue_i, store_a) == the query word's OWN anchor. Chance 1/n_anchors.
                 This is the direct identity question and it needs no WordNet gold at all.
  M2 hit@1       the landed open-pool read-out against WordNet gold, tie-corrected, with the
                 optimistic and conservative conventions published beside it.

BRAIN FIDELITY. The mixing device is OURS -- INVENTION UNDER TEST, an instrument calibration
device, and NO BRAIN STRUCTURE IS CLAIMED FOR IT. The PINNED fact that bears on it, and it cuts
against this cell's own framing: the brain's retrieval cue is NOT a subset of the stored pattern
and arrives on a DIFFERENT WIRE (direct perforant path) from the one that wrote the memory (mossy
fibre -> DG -> CA3), through a synaptic matrix modified during storage (Treves & Rolls 1992; Rolls
2018; Kesner 2007). Measuring how much identity our cue carries does not make our cue the right
KIND of cue. VSA algebraic binding is UNPINNED in the brain and nothing here depends on it.

ORGAN REUSE, enumerated then reconciled. No new mechanism is authored. Imported and never edited:
tools/floor_battery (hit@1 both tie conventions, the four floor constructions, the paired
bootstrap, the pool oracle check), experiments/exp_cue_to_store_translation_v1 (the cache loaders,
the ruler gate, the landed regression constant), experiments/_seed_checkpoint, tools/exp_checkpoint.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened. The store is NEVER rebuilt -- rebuilding it would break the
identical-instrument invariant every arm depends on.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_cue_to_store_translation_v1 as CTS            # cache loaders + ruler gate, NEVER EDITED
from tools import floor_battery as FB                    # floors + scorer + bootstrap, NEVER EDITED
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "cue_regime_one_variable_retrieval_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/one_upstream_cause_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. NEVER EDITED AFTER A RUN. ------------------------------------
LAMBDAS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0)
FILLER_SEEDS: Tuple[int, ...] = (7, 13) if SMOKE else (7, 13, 17)
N_BOOT = 2000 if SMOKE else 10000
MASTER_SEED = CTS.MASTER_SEED
REGRESSION_A0_PARTIAL = CTS.REGRESSION_A0_PARTIAL      # 0.0223, the landed partial-cue read-out
REGRESSION_TOL = CTS.REGRESSION_TOL
ADDRESS_EXACT_MIN = 0.95      # exact-key addressing below this -> INSTRUMENT_STILL_LOOSE

LADDER_E = "E_PARTIAL_CUE"
LADDER_D_OTHER = "D_OTHER_PARTIAL_noninformative"
LADDER_D_GAUSS = "D_GAUSS_noninformative"
D_LADDERS = (LADDER_D_OTHER, LADDER_D_GAUSS)
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
MONOTONE_MIN = 0.90


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def mix(exact: np.ndarray, filler: np.ndarray, lam: float) -> np.ndarray:
    """cue = lam*unit(exact key) + (1-lam)*unit(filler), row-wise. OURS -- INVENTION UNDER TEST."""
    return (lam * l2n(exact) + (1.0 - lam) * l2n(filler)).astype(np.float32)


def spearman(a: Sequence[float], b: Sequence[float]) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ra = np.argsort(np.argsort(a)).astype(np.float64)
    rb = np.argsort(np.argsort(b)).astype(np.float64)
    ra -= ra.mean()
    rb -= rb.mean()
    den = float(np.linalg.norm(ra) * np.linalg.norm(rb))
    return float(ra @ rb / den) if den > 1e-12 else 0.0


def invert_curve(lams: Sequence[float], vals: Sequence[float], target: float) -> Optional[float]:
    """Smallest lam whose calibration value reaches `target`. DERIVED, NOT MEASURED."""
    lams, vals = list(lams), list(vals)
    if not lams:
        return None
    if target <= vals[0]:
        return 0.0
    if target > max(vals):
        return None
    for i in range(1, len(lams)):
        lo, hi = vals[i - 1], vals[i]
        if lo <= target <= hi:
            if hi - lo < 1e-12:
                return float(lams[i])
            return float(lams[i - 1] + (target - lo) / (hi - lo) * (lams[i] - lams[i - 1]))
    return None


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())

    # --- THE ONE VARIABLE, known answer
    e = np.array([[3.0, 0.0, 4.0]], dtype=np.float32)
    f = np.array([[0.0, 5.0, 0.0]], dtype=np.float32)
    assert np.allclose(mix(e, f, 1.0), [[0.6, 0.0, 0.8]], atol=1e-6)
    assert np.allclose(mix(e, f, 0.0), [[0.0, 1.0, 0.0]], atol=1e-6)
    assert np.allclose(mix(e, f, 0.25), [[0.15, 0.75, 0.20]], atol=1e-6)
    ev["MIX_known_answer"] = {"lam1": mix(e, f, 1.0).tolist(), "lam0": mix(e, f, 0.0).tolist(),
                              "lam0.25": mix(e, f, 0.25).tolist()}

    # --- DOSE RESPONSE IS REAL on a planted store: addressing must RISE monotonically with lam
    rng = np.random.default_rng(17)
    n_a, d, n_i = 400, 64, 300
    M = rng.standard_normal((n_a, d)).astype(np.float32)
    q = rng.permutation(n_a)[:n_i]
    Qe = M[q].copy()
    Qp = rng.standard_normal((n_i, d)).astype(np.float32)          # a cue carrying NOTHING
    curve = []
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        addr = np.argmax(l2n(mix(Qe, Qp, lam)) @ l2n(M).T, axis=1)
        curve.append(float(np.mean(addr == q)))
    assert all(curve[i] <= curve[i + 1] + 1e-9 for i in range(len(curve) - 1)), \
        f"the ladder is NOT a dose-response curve on a planted store: {curve}"
    assert curve[0] < 0.05 and curve[-1] > 0.99, f"the ladder endpoints are wrong: {curve}"
    ev["DOSE_RESPONSE_planted_store"] = {"addressing_by_lam": curve}

    # --- the scorer can BOTH fire and fail
    E = np.ones((n_a, n_i), dtype=bool)
    G = np.zeros((n_a, n_i), dtype=bool)
    G[q, np.arange(n_i)] = True
    h_good = FB.hit_at_1_both_tie_conventions(l2n(M) @ l2n(Qe).T, E, G)
    h_bad = FB.hit_at_1_both_tie_conventions(l2n(M) @ l2n(Qp).T, E, G)
    assert h_good["hit_exp"].mean() > 0.99, "scorer cannot FIRE on a planted exact key"
    assert h_bad["hit_exp"].mean() < 0.05, "scorer cannot FAIL on a planted null"
    ev["scorer_can_fire_and_fail"] = {"planted_exact_key": round(float(h_good["hit_exp"].mean()), 4),
                                      "planted_null": round(float(h_bad["hit_exp"].mean()), 4)}

    # --- invert_curve
    assert abs(invert_curve([0.0, 1.0], [0.0, 1.0], 0.3) - 0.3) < 1e-9
    assert invert_curve([0.0, 1.0], [0.0, 0.5], 0.9) is None
    ev["invert_curve"] = "exact on a line; refuses to extrapolate"

    # --- a derangement really deranges
    rng2 = np.random.default_rng(1)
    p = np.arange(50)
    for _ in range(64):
        p = rng2.permutation(50)
        if np.all(p != np.arange(50)):
            break
    assert np.all(p != np.arange(50)), "derangement failed"
    ev["derangement"] = True

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1200], flush=True)
    return ev


# =================================================================================================
def build_population() -> Dict:
    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items_all = len(anchors), len(C["L_words"])
    qidx = np.array([C["pos"].get(w, -1) for w in C["L_words"]], dtype=np.int64)

    GOLD_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    E_ALL = np.zeros((n_anchors, n_items_all), dtype=bool)
    for i in range(n_items_all):
        if not keep[i]:
            continue
        E_ALL[:, i] = mat_ok
        if len(C["excl"][i]):
            E_ALL[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD_ALL[gi, i] = True
    GOLD_ALL &= E_ALL
    keep_ALL = keep & GOLD_ALL.any(axis=0)
    return {"C": C, "aux": aux, "anchors": anchors, "mat": mat, "mat_ok": mat_ok,
            "n_anchors": n_anchors, "qidx": qidx, "GOLD": GOLD_ALL, "E": E_ALL,
            "keep": keep_ALL}


def run(grid: str) -> Dict:
    t0 = time.time()
    P = build_population()
    C, mat, mat_ok = P["C"], P["mat"], P["mat_ok"]
    n_anchors, qidx = P["n_anchors"], P["qidx"]
    GOLD, E, keep_ALL = P["GOLD"], P["E"], P["keep"]

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    Q_part = C["Q_part"][T]
    MATn = l2n(mat)
    print(f"[load] n_anchors={n_anchors} n_items={n_items} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": CTS.ruler_mode_gate(),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "population": {"n_anchors": n_anchors, "n_items_scored": n_items,
                       "pool": "the LANDED OPEN pool (mat_ok minus per-item exclusions); no "
                               "matched or balanced pool is used because eligB is on record as "
                               "admitting a constant at 0.1715 against chance 0.0101",
                       "chance_addressing": round(1.0 / n_anchors, 8)},
    }

    # ---- REGRESSION GATE on the FULL landed population -----------------------------------------
    S_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E, GOLD)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGRESSION_GATE"] = {
        "what": "lam=0 of the E ladder IS the landed partial-cue read-out; it must reproduce the "
                "landed value on the FULL landed open pool.",
        "A0_partial_tie_corrected_FULL_POP": round(a0_full, 4),
        "expected": REGRESSION_A0_PARTIAL, "tol": REGRESSION_TOL,
        "PASS": bool(abs(a0_full - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL),
        "n_scored": int(m_full.sum())}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r"
                         % rep["REGRESSION_GATE"])
    print("[regression] A0_partial_FULL=%.4f (expected %.4f) PASS"
          % (a0_full, REGRESSION_A0_PARTIAL), flush=True)
    del S_full, h_full

    # ---- FLOORS, all recomputed on THIS population ----------------------------------------------
    aux = P["aux"]
    floors_S: Dict[str, np.ndarray] = {}
    try:
        Tq = aux["Tq"][T]
        floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(Tq).T).astype(np.float32)
    except Exception as exc:                                       # pragma: no cover - reported
        rep.setdefault("FLOOR_NOTES", {})["F_ORTHOGRAPHIC"] = f"UNAVAILABLE: {exc!r}"
    try:
        floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
            FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    except Exception as exc:                                       # pragma: no cover - reported
        rep.setdefault("FLOOR_NOTES", {})["F_FREQUENCY"] = f"UNAVAILABLE: {exc!r}"
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 91))
                              @ l2n(Q_part).T).astype(np.float32)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(
        FB.constant_prototype_floor(mat, mat_ok), n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i])
                                              for i in range(n_items)]), n_items)

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    scored_all = np.ones(n_items, dtype=bool)
    tie_of: Dict[str, float] = {}

    def add_arm(name: str, S: np.ndarray) -> None:
        nonlocal scored_all
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        hits_exp[name] = h["hit_exp"]
        hits_opt[name] = h["hit_opt"]
        hits_cons[name] = h["hit_cons"]
        tie_of[name] = float(h["tie_mass"].mean())
        scored_all = scored_all & h["scored"]

    for k, S in floors_S.items():
        add_arm(k, S)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959",
                             "every floor above is recomputed on this population's own n"]

    # ---- the fillers -----------------------------------------------------------------------------
    rng = np.random.default_rng(MASTER_SEED + 41)
    filler: Dict[str, Dict[int, np.ndarray]] = {LADDER_E: {0: Q_part}}
    tabs: Dict[int, np.ndarray] = {}
    for s in FILLER_SEEDS:
        r = np.random.default_rng(s ^ 0x5EED)
        p = np.arange(n_items)
        for _ in range(64):
            p = r.permutation(n_items)
            if np.all(p != np.arange(n_items)):
                break
        tabs[s] = Q_part[p]
    filler[LADDER_D_OTHER] = tabs
    mu = Q_part.mean(axis=0)
    sd = Q_part.std(axis=0, ddof=1)
    tabs = {}
    for s in FILLER_SEEDS:
        r = np.random.default_rng(s ^ 0x0A11)
        tabs[s] = (mu[None, :] + sd[None, :] * r.standard_normal(Q_part.shape)).astype(np.float32)
    filler[LADDER_D_GAUSS] = tabs

    # ---- the ladders ------------------------------------------------------------------------------
    addressing: Dict[str, Dict[str, Dict]] = {}
    ladder_arm_names: Dict[str, Dict[str, str]] = {}
    for lname, tabs in filler.items():
        seeds = sorted(tabs)
        per_lam: Dict[str, Dict] = {}
        names: Dict[str, str] = {}
        for lam in LAMBDAS:
            best = None
            for s in seeds:
                cue = mix(Q_exact, tabs[s], lam)
                S = (MATn @ l2n(cue).T).astype(np.float32)
                addr = np.argmax(S, axis=0)
                ok = qidx_T >= 0
                acc = float(np.mean(addr[ok] == qidx_T[ok]))
                if best is None or acc > best[0]:
                    best = (acc, s, S, int(np.unique(addr[ok]).size), int(ok.sum()))
                else:
                    del S
            acc, s, S, n_distinct, n_ok = best
            nm = f"{lname}|lam{lam:.2f}"
            add_arm(nm, S)
            del S
            names[f"{lam:.2f}"] = nm
            per_lam[f"{lam:.2f}"] = {
                "lam": lam, "max_draw_seed": int(s), "seed_policy": "MAX DRAW never the mean",
                "addressed_item_IS_the_query_word": round(acc, 6),
                "n_items_with_an_own_anchor": n_ok,
                "n_distinct_items_addressed": n_distinct,
                "chance": round(1.0 / n_anchors, 8),
                "binom_ci95_halfwidth": round(float(1.96 * (max(acc * (1 - acc), 1e-12)
                                                            / max(n_ok, 1)) ** 0.5), 6)}
            print(f"[{lname}] lam={lam:.2f} addressing={acc:.4f} seed={s}", flush=True)
        addressing[lname] = per_lam
        ladder_arm_names[lname] = names

    # ---- bootstrap over the COMMON scored items ---------------------------------------------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_opt = FB.paired_bootstrap_ci(hits_opt, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_cons = FB.paired_bootstrap_ci(hits_cons, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    rep["M2_hit_at_1"] = {
        "n_common_scored": pb["n_common"],
        "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED",
        "tie_corrected": {k: round(v, 4) for k, v in acc.items()},
        "optimistic_tie": {k: round(v, 4) for k, v in pb_opt["acc"].items()},
        "conservative_tie": {k: round(v, 4) for k, v in pb_cons["acc"].items()},
        "mean_tie_mass": {k: round(v, 4) for k, v in tie_of.items()},
        "BINDING_FLOOR": binding,
        "BINDING_FLOOR_VALUE": round(acc[binding], 4) if binding else None,
        "ORACLE_CONSTANT_not_a_floor":
            round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 4),
        "POOL_ORACLE_CHECK": {
            "what": "the fitted ceiling of the constant family on THIS pool. The open pool is not "
                    "a de-biased pool and is not claimed to be; the number is published so nobody "
                    "reads a margin over it as a margin over chance.",
            "oracle_constant_hit_exp":
                round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 4),
            "note": "tools/floor_battery.pool_admits_a_winning_constant applies to per-item "
                    "CANDIDATE SETS; this is the OPEN pool, so the equivalent quantity is the "
                    "oracle constant's hit rate on the open pool, reported here."},
    }
    if binding:
        rep["M2_hit_at_1"]["MARGIN_vs_binding_floor_TIE_CORRECTED"] = {
            k: FB.margin(boot, k, binding) for k in acc if k != binding}
        rep["M2_hit_at_1"]["MARGIN_vs_binding_floor_CONSERVATIVE"] = {
            k: FB.margin(pb_cons["boot"], k, binding) for k in acc if k != binding}
        rep["M2_hit_at_1"]["MARGIN_vs_binding_floor_OPTIMISTIC"] = {
            k: FB.margin(pb_opt["boot"], k, binding) for k in acc if k != binding}
        rep["M2_hit_at_1"]["ARM_BY_ARM_vs_EACH_FLOOR"] = {
            k: {f: FB.margin(boot, k, f) for f in present}
            for k in acc if k not in present and not k.startswith("ORACLE")}

    # ---- POWER BLOCK. A width is not an effect. ---------------------------------------------------
    nc = pb["n_common"]
    rep["POWER"] = {
        "n_common_scored": nc,
        "hit_at_1_binom_ci_halfwidth_at_binding_floor":
            round(float(1.96 * (max(acc[binding] * (1 - acc[binding]), 1e-12) / max(nc, 1)) ** 0.5),
                  6) if binding else None,
        "addressing_chance": round(1.0 / n_anchors, 8),
        "per_arm_margin_ci_halfwidth": (
            {k: round((v["ci95"][1] - v["ci95"][0]) / 2.0, 5)
             for k, v in rep["M2_hit_at_1"].get("MARGIN_vs_binding_floor_TIE_CORRECTED", {}).items()}
            if binding else {}),
        "reading": "if a margin is smaller than its own CI half-width the arm cannot separate at "
                   "this n no matter how good the underlying thing is",
    }

    # ---- MONOTONICITY GATE, read BEFORE any lambda_star -------------------------------------------
    mono: Dict[str, Dict] = {}
    for lname in filler:
        a_curve = [addressing[lname][f"{l:.2f}"]["addressed_item_IS_the_query_word"]
                   for l in LAMBDAS]
        h_curve = [acc[ladder_arm_names[lname][f"{l:.2f}"]] for l in LAMBDAS]
        mono[lname] = {
            "M1_addressing": {"spearman_lam_vs_value": round(spearman(LAMBDAS, a_curve), 4),
                              "by_lambda": {f"{l:.2f}": v for l, v in zip(LAMBDAS, a_curve)},
                              "IS_A_DOSE_RESPONSE_CURVE":
                                  bool(spearman(LAMBDAS, a_curve) >= MONOTONE_MIN)},
            "M2_hit_at_1": {"spearman_lam_vs_value": round(spearman(LAMBDAS, h_curve), 4),
                            "by_lambda": {f"{l:.2f}": round(v, 4)
                                          for l, v in zip(LAMBDAS, h_curve)},
                            "IS_A_DOSE_RESPONSE_CURVE":
                                bool(spearman(LAMBDAS, h_curve) >= MONOTONE_MIN)},
        }
    rep["MONOTONICITY_GATE"] = mono

    # ---- THE PRIMARY MEASURE: lambda_star ---------------------------------------------------------
    lstar: Dict[str, Dict] = {}
    chance_addr = 1.0 / n_anchors
    for lname in filler:
        first_addr = None
        for lam in LAMBDAS:
            r = addressing[lname][f"{lam:.2f}"]
            lo = r["addressed_item_IS_the_query_word"] - r["binom_ci95_halfwidth"]
            if first_addr is None and lo > chance_addr:
                first_addr = lam
        first_hit = None
        if binding:
            for lam in LAMBDAS:
                nm = ladder_arm_names[lname][f"{lam:.2f}"]
                m = FB.margin(boot, nm, binding)
                if first_hit is None and m["band"] == "ABOVE":
                    first_hit = lam
        lstar[lname] = {
            "M1_lambda_star_addressing_CI_above_chance": first_addr,
            "M2_lambda_star_hit_at_1_CI_above_binding_floor": first_hit,
            "M1_PUBLISHABLE": bool(mono[lname]["M1_addressing"]["IS_A_DOSE_RESPONSE_CURVE"]),
            "M2_PUBLISHABLE": bool(mono[lname]["M2_hit_at_1"]["IS_A_DOSE_RESPONSE_CURVE"]),
            "definition": "smallest exact-key mixing fraction at which this ladder CI-separates "
                          "above its floor, on THIS population",
        }
    rep["LAMBDA_STAR"] = lstar

    # ---- DERIVED: the real partial cue's exact-key-equivalent -- THE COMMON CURRENCY --------------
    equiv: Dict[str, Dict] = {}
    for dname in D_LADDERS:
        a_curve = [addressing[dname][f"{l:.2f}"]["addressed_item_IS_the_query_word"]
                   for l in LAMBDAS]
        h_curve = [acc[ladder_arm_names[dname][f"{l:.2f}"]] for l in LAMBDAS]
        equiv[dname] = {
            "M1_addressing": {
                "partial_cue_value": addressing[LADDER_E]["0.00"]["addressed_item_IS_the_query_word"],
                "exact_key_equivalent": invert_curve(
                    LAMBDAS, a_curve,
                    addressing[LADDER_E]["0.00"]["addressed_item_IS_the_query_word"])},
            "M2_hit_at_1": {
                "partial_cue_value": round(acc[ladder_arm_names[LADDER_E]["0.00"]], 4),
                "exact_key_equivalent": invert_curve(
                    LAMBDAS, h_curve, acc[ladder_arm_names[LADDER_E]["0.00"]])},
            "DERIVED_NOT_MEASURED": True,
            "reading": "the fraction of the target's OWN identity whose dilution by a "
                       "non-informative filler reads the same as the REAL partial cue",
        }
    rep["EXACT_KEY_EQUIVALENT_derived"] = equiv

    # ---- HEAD-TO-HEAD: does the real partial cue beat a non-informative filler at any rung? -------
    h2h: Dict[str, Dict] = {}
    for dname in D_LADDERS:
        per_lam = {}
        for lam in LAMBDAS:
            a = ladder_arm_names[LADDER_E][f"{lam:.2f}"]
            b = ladder_arm_names[dname][f"{lam:.2f}"]
            m = FB.margin(boot, a, b)
            ra = addressing[LADDER_E][f"{lam:.2f}"]
            rb = addressing[dname][f"{lam:.2f}"]
            d_addr = ra["addressed_item_IS_the_query_word"] - rb["addressed_item_IS_the_query_word"]
            hw = float((ra["binom_ci95_halfwidth"] ** 2 + rb["binom_ci95_halfwidth"] ** 2) ** 0.5)
            per_lam[f"{lam:.2f}"] = {
                "M2_hit_at_1_margin": m,
                "M1_addressing_delta": round(d_addr, 6),
                "M1_addressing_delta_ci_halfwidth_unpaired": round(hw, 6),
                "M1_band": ("ABOVE" if d_addr - hw > 0 else
                            ("BELOW" if d_addr + hw < 0 else "NOT_SEPARATED"))}
        n_above_h = sum(1 for v in per_lam.values() if v["M2_hit_at_1_margin"]["band"] == "ABOVE")
        n_above_a = sum(1 for v in per_lam.values() if v["M1_band"] == "ABOVE")

        def _longest_run(key: str, want: str) -> int:
            best = cur = 0
            for lam in LAMBDAS:
                v = per_lam[f"{lam:.2f}"]
                b = v["M1_band"] if key == "M1" else v["M2_hit_at_1_margin"]["band"]
                cur = cur + 1 if b == want else 0
                best = max(best, cur)
            return best

        run_h, run_a = _longest_run("M2", "ABOVE"), _longest_run("M1", "ABOVE")
        h2h[f"{LADDER_E}_minus_{dname}"] = {
            "per_lambda": per_lam,
            "n_rungs": len(per_lam), "n_rungs_M2_ABOVE": n_above_h, "n_rungs_M1_ABOVE": n_above_a,
            "longest_ADJACENT_run_M2_ABOVE": run_h, "longest_ADJACENT_run_M1_ABOVE": run_a,
            "ANY_RUNG_ABOVE": bool(n_above_h > 0 or n_above_a > 0),
            # THE MULTIPLICITY-ROBUST STATISTIC. One isolated rung is noise; a RUN is not.
            "CARRIES_IDENTITY_two_or_more_adjacent_rungs": bool(run_h >= 2 or run_a >= 2),
            "multiplicity": f"{len(per_lam)} rungs; one isolated ABOVE rung is expected "
                            f"{0.05 * len(per_lam):.2f} times under the null and is NOT evidence. "
                            f"The decision uses the LONGEST ADJACENT RUN, not the count."}
    rep["HEAD_TO_HEAD_real_partial_cue_minus_noninformative"] = h2h

    # ---- VALIDITY, failing independently -----------------------------------------------------------
    exact_addr = addressing[LADDER_D_OTHER]["1.00"]["addressed_item_IS_the_query_word"]
    null_addr = addressing[LADDER_D_OTHER]["0.00"]["addressed_item_IS_the_query_word"]
    rep["VALIDITY"] = {
        "KA_EXACT_KEY_addressing": {
            "value": exact_addr, "gate": ADDRESS_EXACT_MIN,
            "PASSED": bool(exact_addr >= ADDRESS_EXACT_MIN),
            "sensitive_to": "the scorer and the store", "INSENSITIVE_to": "the filler"},
        "NULL_NONINFORMATIVE_FILLER_ONLY_addressing": {
            "value": null_addr, "chance": round(chance_addr, 8),
            "PASSED": bool(null_addr < max(0.02, 20.0 * chance_addr)),
            "sensitive_to": "the cue-to-item pairing", "INSENSITIVE_to": "the scorer"},
        "FAIL_INDEPENDENTLY": "a scorer/store bug drops KA while leaving NULL at chance; a pairing "
                              "or leak bug leaves KA at ceiling while raising NULL",
        "BOTH_PASSED": bool(exact_addr >= ADDRESS_EXACT_MIN
                            and null_addr < max(0.02, 20.0 * chance_addr)),
    }
    # ---- THE EXACT-KEY READ-OUT BLOCK. Surfaced on its own because branch ordering must never
    # be able to hide it: if the EXACT KEY does not clear the binding floor on the read-out, the
    # cue is EXONERATED on that metric and the blocker is downstream of the address.
    ek_arm = ladder_arm_names[LADDER_D_OTHER]["1.00"]
    ek = {"arm": ek_arm, "hit_at_1_tie_corrected": round(acc[ek_arm], 4),
          "addressing": addressing[LADDER_D_OTHER]["1.00"]["addressed_item_IS_the_query_word"],
          "binding_floor": binding,
          "binding_floor_value": round(acc[binding], 4) if binding else None,
          "margin_vs_binding_floor": FB.margin(boot, ek_arm, binding) if binding else None}
    ek["EXACT_KEY_CLEARS_THE_READOUT_FLOOR"] = bool(
        binding and ek["margin_vs_binding_floor"]["band"] == "ABOVE")
    ek["reading"] = (
        "the cue is PERFECT here by construction. If addressing is ~1.0 and hit@1 is still below "
        "the binding floor, then on the READ-OUT metric the cue is not the blocker at all and the "
        "defect is downstream of the address -- in what the store's neighbourhood encodes.")
    rep["EXACT_KEY_READOUT"] = ek

    rep["M1_ADDRESSING"] = addressing
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} seeds={FILLER_SEEDS} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    val = rep.get("VALIDITY", {})
    ls = rep.get("LAMBDA_STAR", {})
    mono = rep.get("MONOTONICITY_GATE", {})
    d_ok = [k for k in D_LADDERS if mono.get(k, {}).get("M1_addressing", {}).get(
        "IS_A_DOSE_RESPONSE_CURVE")]
    d_star = [ls[k]["M1_lambda_star_addressing_CI_above_chance"] for k in d_ok
              if ls.get(k, {}).get("M1_lambda_star_addressing_CI_above_chance") is not None]
    carries = any(v.get("CARRIES_IDENTITY_two_or_more_adjacent_rungs") for v in
                  (rep.get("HEAD_TO_HEAD_real_partial_cue_minus_noninformative") or {}).values())
    ek_clears = bool((rep.get("EXACT_KEY_READOUT") or {}).get("EXACT_KEY_CLEARS_THE_READOUT_FLOOR"))

    # THE VERDICT IS COMPOSED FROM THREE INDEPENDENT GATES, NOT SELECTED BY BRANCH ORDER.
    # An earlier draft used an if/elif chain and the REDUCED-GRID SMOKE caught it declaring
    # "CUE_IS_THE_UPSTREAM_CAUSE" on a run whose own head-to-head showed the partial cue beating a
    # matched non-informative filler at 7 of 10 rungs. A branch order must never be able to hide a
    # measured fact. The correction is disclosed in the findings log; no arm, floor, population or
    # threshold changed, only the LABEL MAPPING, and it changed AGAINST the hypothesis being tested.
    if not val.get("BOTH_PASSED"):
        verdict = "INSTRUMENT_STILL_LOOSE_VALIDITY_ARMS_DID_NOT_BOTH_PASS"
    elif not d_ok:
        verdict = "CALIBRATION_LADDER_NOT_MONOTONE_LAMBDA_STAR_NOT_PUBLISHABLE"
    else:
        ls_tag = ("NONE" if not d_star else
                  ("%.2f" % min(d_star)).replace(".", "p"))
        verdict = ("EXACTKEY_READOUT_%s__CUE_CARRIES_IDENTITY_%s__LAMBDA_STAR_%s"
                   % ("CLEARS" if ek_clears else "BELOW_FLOOR",
                      "YES" if carries else "NO", ls_tag))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ONE VARIABLE -- the fraction of the RETRIEVAL cue that is the item's own exact key -- "
            "swept end to end on the identical store / pool / gold / scorer. PRIMARY MEASURE "
            "lambda_star = the smallest exact-key fraction at which a NON-INFORMATIVE filler "
            "ladder CI-separates above its floor. Paired with the bridging-side sibling this gives "
            "the exact-key-equivalent of BOTH cues in the SAME units. -> " + verdict),
        "HOW_TO_READ_THIS": (
            "The capability is DEMONSTRATED -- people retrieve from degraded cues constantly. Any "
            "null here is a fact about OUR IMPLEMENTATION. Finding that our cue is "
            "information-poor is a GOOD outcome: it relocates the blocker upstream, to what we "
            "WRITE, instead of leaving us building retrieval machinery on a cue that cannot "
            "support any of it."),
        "BRAIN_FIDELITY": {
            "the_mixing_device": "OURS -- INVENTION UNDER TEST. Calibration instrument. NO BRAIN "
                                 "STRUCTURE IS CLAIMED FOR IT.",
            "PINNED": "the brain's retrieval cue is NOT a subset of the stored pattern and arrives "
                      "on a DIFFERENT WIRE (direct perforant path) from the one that wrote the "
                      "memory, through a synaptic matrix modified during storage "
                      "(Treves & Rolls 1992; Rolls 2018; Kesner 2007). Measuring how much identity "
                      "our cue carries does not make it the right KIND of cue.",
            "VSA_binding": "UNPINNED in the brain; nothing here depends on it.",
            "shelve_revival_criteria_brain_framed":
                "If the partial cue's exact-key-equivalent is near zero, the shelved object is our "
                "CUE CONSTRUCTION, and the revival criterion is that a cue be delivered through a "
                "TRANSLATION stage between cue space and store space, as the perforant path is, "
                "rather than compared by raw cosine in one space.",
        },
        "config": {"LAMBDAS": list(LAMBDAS), "FILLER_SEEDS": list(FILLER_SEEDS),
                   "N_BOOT": N_BOOT, "MASTER_SEED": MASTER_SEED,
                   "ADDRESS_EXACT_MIN": ADDRESS_EXACT_MIN, "MONOTONE_MIN": MONOTONE_MIN},
        "selftest_evidence": ev,
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(3)
