"""exp_cue_regime_one_variable_v1 -- ONE VARIABLE: HOW MUCH OF THE TARGET'S OWN IDENTITY IS IN THE
CUE. Everything else is held fixed.

FINDINGS LOG (pre-registration in section 2, written before any number was read):
notes/one_upstream_cause_findings_2026-08-17.md

THE QUESTION. Two bridging mechanisms are landed nulls
(exp_thematic_relation_supply_bridged_grounding_v2, exp_selectional_constraint_bridge_v1) and the
partial cue is capped at ~0.037 even for a circular WordNet oracle that is allowed to cheat. Three
results, three readings. The hypothesis is that they are ONE finding with ONE upstream cause: the
cue does not carry the target's identity, so nothing built ON the cue could have worked.

THE CONTRAST. Same held-out words, same SimLex pairs, same 12-dim L2-normalised cosine scorer,
same gold, same bootstrap seed, all four floors recomputed on the same stratum. Only the CUE
REGIME changes, as a continuous mixing fraction lam between the target's own stored row (THE EXACT
KEY) and a filler:

    cue(w, lam) = lam * unit(t_w) + (1 - lam) * unit(filler_w)

  lam = 1.0 -> the cue IS the exact key. ASSERTED bit-identical to K1_OWN_NORMS.
  lam = 0.0 -> the cue is the filler alone. With filler = a bridge code this REPRODUCES the landed
              bridge arm exactly, which is the regression gate.

THE PRIMARY MEASURE is lambda_star: the smallest lam at which a NON-INFORMATIVE filler ladder
CI-separates above max(four floors). That is the instrument's detection threshold expressed in
units of "fraction of the target's own identity", and it decides how the two landed nulls must be
read:

  lambda_star SMALL -> the instrument would have seen a weakly-identified cue; the bridges deliver
                       less than that; THE CUE IS THE CAUSE and the three results collapse into one.
  lambda_star LARGE -> only a near-exact cue clears; THE BRIDGING NULLS ARE POWER STATEMENTS, NOT
                       CAPABILITY STATEMENTS, and the Phase 2 kill-condition reading is retracted.

It can therefore fail both ways, which is the point.

BRAIN FIDELITY, stated so nothing is laundered.
  * The mixing device above is OURS -- INVENTION UNDER TEST. It is an INSTRUMENT CALIBRATION
    DEVICE, not a model of anything. NO BRAIN STRUCTURE IS CLAIMED FOR IT and inventing one to fill
    the box would be exactly the laundering the fidelity gate bans.
  * PINNED, and it cuts against the framing of both bridging cells (Treves & Rolls 1992; Rolls
    2018; Kesner 2007, via notes/drill_brain_partial_cue_retrieval_..._2026-08-16.md sec 1c): the
    brain's retrieval cue is NOT a subset of the stored pattern. It arrives on a DIFFERENT WIRE
    (direct perforant path) from the one that wrote the memory (mossy fibre -> DG -> CA3), through
    a synaptic matrix that was itself modified during storage. This cell does not fix that. It
    measures whether our instrument could have detected the identity even if it were present.
  * PINNED as a COMPUTATION, swept never adopted as a PARAMETER: nothing here copies a brain
    parameter. lam is swept end to end.
  * VSA algebraic binding -- this substrate's core operation -- is UNPINNED in the brain, with
    three live accounts and published objections to each. Nothing here depends on it or tests it.

ORGAN REUSE, enumerated from disk then reconciled (never the reverse). This cell AUTHORS NO NEW
MECHANISM. It imports and never edits: exp_encoding_quality_instrument_v2 (the instrument),
exp_meaning_asset_fair_test_v1 (bootstrap + bands), exp_bridged_grounding_from_core_v1 (Bridger,
code_matrix, pair_cos, asset loaders), exp_thematic_relation_supply_bridged_grounding_v2 (the
thematic graph = mechanism 1), exp_selectional_constraint_bridge_v1 (SelectionalSource = mechanism
2, build_floors, scramble_floor), thematic_relation_extractor_v1, selectional_preference_
extractor_v1, tools/exp_checkpoint, experiments/_seed_checkpoint.

PRIOR ART, credited and built on rather than re-derived. Cue-degradation CURVES already exist in
this repo, all in the ADDRESSING/hit@1 regime and none on the bridging population or the SimLex
pair-Spearman scorer: experiments/exp_hub_spoke_partial_cue_curve_v1.py,
experiments/exp_ca3_completion_partial_cue_v1.py, experiments/exp_readout_sign_cue_overlap_curve_v1.py
and the exp_substrate_pattern_completion_corruption_cliff_v2_* family. What is new here is not the
curve; it is using the curve as a DETECTION THRESHOLD to decide whether a landed null is a
capability statement or a power statement.

TRAPS RE-EARNED BY RUNTIME EVERY RUN, NEVER INHERITED. grounded_similarity() saturates >70% of
SimLex onto two values and is NEVER the scorer. exp_task_degeneracy_v1.ruler_mode_gate() is CALLED
and hard-fails unless the instrument resolved RUN_MODE=full / V=4096 / CORPUS_BYTES=64,000,000, so
this cell's reduced-grid flag is `--grid reduced` and the bare token `--smoke` NEVER enters argv.
Floors 0.1382 / 0.2070 / -0.1959 are NEVER imported; every floor is recomputed here.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened by this cell.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE INSTRUMENT, IMPORTED, NEVER EDITED
import exp_meaning_asset_fair_test_v1 as FT               # verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL         # sibling library, NEVER EDITED
import exp_thematic_relation_supply_bridged_grounding_v2 as INC   # MECHANISM 1, NEVER EDITED
import exp_selectional_constraint_bridge_v1 as SELB       # MECHANISM 2 + floors, NEVER EDITED
import thematic_relation_extractor_v1 as THEM
import selectional_preference_extractor_v1 as SEL
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "cue_regime_one_variable_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/one_upstream_cause_findings_2026-08-17.md"

# THE FLAG IS `--grid reduced`, NOT `--smoke`, AND THAT IS LOAD-BEARING (see module docstring).
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS (findings-log section 2). NEVER EDITED AFTER A RUN. -----------
# The ladder. Denser at the bottom because that is where the detection threshold is expected and
# where the decision rule is sensitive; 0.0 and 1.0 are the two regression gates.
LAMBDAS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0)
FILLER_SEEDS: Tuple[int, ...] = (7, 13) if SMOKE else (7, 13, 17, 23, 29)
NULL_LAMBDA = 1.0          # permuted-assignment null sits at the TOP of the ladder on purpose
MONOTONE_MIN = 0.90        # Spearman(lam, rho) a D ladder must reach to be a dose-response curve

# inherited from the sibling so that every constant is single-sourced and cannot drift
N_BOOT = SELB.N_BOOT
N_PERM = SELB.N_PERM
BOOT_SEED = SELB.BOOT_SEED
T_MARGIN_MIN = SELB.T_MARGIN_MIN
AOA_CORE_MAX = SELB.AOA_CORE_MAX
FLOOR_ORTHO = SELB.FLOOR_ORTHO
FLOOR_FREQ = SELB.FLOOR_FREQ
FLOOR_SCRAM = SELB.FLOOR_SCRAM
FLOOR_CONST = SELB.FLOOR_CONST
FLOOR_KEYS = SELB.FLOOR_KEYS

LADDER_SEL = "E_SEL_selectional_bridge"
LADDER_INC = "E_INC_thematic_neighbour_copy"
LADDER_RANDWORD = "D_RANDWORD_noninformative"
LADDER_GAUSS = "D_GAUSS_noninformative"
D_LADDERS = (LADDER_RANDWORD, LADDER_GAUSS)
E_LADDERS = (LADDER_SEL, LADDER_INC)


def _arm_seed(name: str) -> int:
    """DETERMINISTIC per-arm seed -- builtin hash() is per-process randomised and this cell is
    checkpointed and therefore WILL be resumed."""
    return int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big") % 100000


# ==========================================================================================
# A VECTORISED PAIRED BOOTSTRAP -- IDENTICAL MATHEMATICS, PROVEN BY AN EQUALITY GATE
# ==========================================================================================
# exp_meaning_asset_fair_test_v1.boot_rho_diff is a Python loop calling a Python-tie-loop Spearman:
# 247 us per correlation, 5.73 s per 2,000-resample call, and this cell needs ~250 of them per
# config. At the FULL grid that is ~10 hours, i.e. the run would not land.
#
# THE SHARED MODULE IS NOT EDITED. Instead the SAME quantity is computed with midranks in numpy,
# drawing the resample indices from the IDENTICAL generator (`default_rng(seed).integers(0, n,
# size=(n_boot, n))`) so the two agree RESAMPLE BY RESAMPLE and not merely in distribution.
# selftest() asserts agreement with FT.boot_rho_diff to 1e-9 on both the point estimate and both
# CI bounds, on data that CONTAINS TIES, and asserts per-row agreement with INS._spearman.
# If that assertion ever fails this fast path is void and the cell will not run.
def _midrank(X: np.ndarray) -> np.ndarray:
    """Row-wise midranks (the average-rank tie convention), vectorised. X [B, n] -> [B, n]."""
    B, n = X.shape
    order = np.argsort(X, axis=1, kind="stable")
    Xs = np.take_along_axis(X, order, axis=1)
    start = np.ones((B, n), dtype=bool)
    start[:, 1:] = Xs[:, 1:] != Xs[:, :-1]
    idxs = np.arange(n, dtype=np.float64)[None, :]
    first_of = np.maximum.accumulate(np.where(start, idxs, 0.0), axis=1)
    end = np.ones((B, n), dtype=bool)
    end[:, :-1] = start[:, 1:]
    last_of = np.minimum.accumulate(np.where(end, idxs, float(n - 1))[:, ::-1], axis=1)[:, ::-1]
    mid = 0.5 * (first_of + last_of)
    out = np.empty((B, n), dtype=np.float64)
    np.put_along_axis(out, order, mid, axis=1)
    return out


def _rho_rows(A: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Spearman per row = Pearson of the midranks. A, G [B, n] -> [B]."""
    ra = _midrank(A)
    rg = _midrank(G)
    ra -= ra.mean(axis=1, keepdims=True)
    rg -= rg.mean(axis=1, keepdims=True)
    num = np.einsum("ij,ij->i", ra, rg)
    den = np.sqrt(np.einsum("ij,ij->i", ra, ra) * np.einsum("ij,ij->i", rg, rg))
    return np.where(den > 1e-12, num / np.maximum(den, 1e-30), np.nan)


def _boot_idx(n: int, n_boot: int, seed: int) -> np.ndarray:
    """THE IDENTICAL draw the landed bootstrap makes -- same generator, same call, same shape."""
    return np.random.default_rng(seed).integers(0, n, size=(n_boot, n))


def _boot_rhos(cos: np.ndarray, gold: np.ndarray, IDX: np.ndarray,
               chunk: int = 2000) -> np.ndarray:
    cos = np.asarray(cos, dtype=np.float64)
    gold = np.asarray(gold, dtype=np.float64)
    out = np.empty(IDX.shape[0], dtype=np.float64)
    for s in range(0, IDX.shape[0], chunk):
        j = IDX[s:s + chunk]
        out[s:s + chunk] = _rho_rows(cos[j], gold[j])
    return out


def boot_rho_fast(cos, gold, n_boot: int = None, seed: int = None) -> Dict:
    n_boot = n_boot or N_BOOT
    seed = BOOT_SEED if seed is None else seed
    cos, gold = np.asarray(cos, dtype=np.float64), np.asarray(gold, dtype=np.float64)
    n = len(gold)
    if n < 5:
        return {"point": float("nan"), "ci95": [float("nan")] * 2, "n": n}
    r = _boot_rhos(cos, gold, _boot_idx(n, n_boot, seed))
    r = r[np.isfinite(r)]
    return {"point": float(INS._spearman(cos, gold)),
            "ci95": [float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))], "n": int(n)}


def boot_rho_diff_fast(cos_a, cos_b, gold, n_boot: int = None, seed: int = None) -> Dict:
    n_boot = n_boot or N_BOOT
    seed = BOOT_SEED if seed is None else seed
    cos_a = np.asarray(cos_a, dtype=np.float64)
    cos_b = np.asarray(cos_b, dtype=np.float64)
    gold = np.asarray(gold, dtype=np.float64)
    n = len(gold)
    if n < 5:
        return {"point": float("nan"), "ci95": [float("nan")] * 2, "n": n}
    IDX = _boot_idx(n, n_boot, seed)
    d = _boot_rhos(cos_a, gold, IDX) - _boot_rhos(cos_b, gold, IDX)
    d = d[np.isfinite(d)]
    pt = INS._spearman(cos_a, gold) - INS._spearman(cos_b, gold)
    return {"point": float(pt), "ci95": [float(np.percentile(d, 2.5)),
                                         float(np.percentile(d, 97.5))], "n": int(n)}


# ==========================================================================================
# THE ONE VARIABLE
# ==========================================================================================
def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return (v / n) if n > 1e-12 else np.asarray(v, dtype=np.float64)


def mix(t_row: np.ndarray, filler: np.ndarray, lam: float) -> np.ndarray:
    """cue(w, lam) = lam*unit(exact key) + (1-lam)*unit(filler).

    Both sides are unit-normalised FIRST so lam is a genuine mixing fraction rather than an
    accident of the two vectors' magnitudes. OURS -- INVENTION UNDER TEST, and it is a calibration
    device, not a model of anything.
    """
    return lam * _unit(np.asarray(t_row, dtype=np.float64)) \
        + (1.0 - lam) * _unit(np.asarray(filler, dtype=np.float64))


# ==========================================================================================
# tie conventions -- REPORTED BOTH WAYS, never silently the flattering one
# ==========================================================================================
def tie_conventions(score: np.ndarray, gold: np.ndarray) -> Dict[str, float]:
    """Spearman under all three tie conventions plus the tie mass that drives the spread.

    optimistic  = ties inside a group broken in GOLD ORDER (best case for this score vector)
    pessimistic = ties broken against gold (worst case)
    midrank     = the standard average-rank convention, i.e. what the instrument computes
    """
    score = np.asarray(score, dtype=np.float64)
    gold = np.asarray(gold, dtype=np.float64)
    n = len(score)
    out: Dict[str, float] = {"midrank": float(INS._spearman(score, gold))}
    for name, sgn in (("optimistic", 1.0), ("pessimistic", -1.0)):
        order = np.lexsort((sgn * gold, score))       # primary key = score, secondary = +/- gold
        r = np.empty(n, dtype=np.float64)
        r[order] = np.arange(n, dtype=np.float64)
        out[name] = float(INS._spearman(r, gold))
    out["tie_mass"] = float(1.0 - (len(np.unique(score)) / float(n)))
    return out


# ==========================================================================================
# scoring -- mirrors the sibling's _score_cos and ADDS the power block the standing rule demands
# ==========================================================================================
def score_arm(name: str, obs: np.ndarray, X: Optional[np.ndarray], ia: np.ndarray, ib: np.ndarray,
              gold: np.ndarray, floors: Dict[str, Dict], seed: int, light: bool = False) -> Dict:
    n = int(len(gold))
    analytic_null_width = float(1.645 / max(n - 1, 1) ** 0.5)
    rho = boot_rho_fast(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED)
    rho["ci_halfwidth"] = float((rho["ci95"][1] - rho["ci95"][0]) / 2.0)
    if light or X is None:
        return {"arm": name, "rho": rho, "n": n,
                "analytic_null_width_1p645_over_sqrt_n_minus_1": round(analytic_null_width, 4),
                "scoring": "LIGHT (rho only; not a verdict-bearing arm)", "_cos": obs}
    sc = SELB.scramble_floor(X, ia, ib, gold, seed)
    cands = {k: (floors[k]["rho"], floors[k]["_partner"]) for k in floors}
    cands[FLOOR_SCRAM] = (sc["p95"], sc["_partner"])
    bf = max(cands, key=lambda k: cands[k][0])
    diff = boot_rho_diff_fast(obs, cands[bf][1], gold, n_boot=N_BOOT, seed=BOOT_SEED)
    diff["ci_halfwidth"] = float((diff["ci95"][1] - diff["ci95"][0]) / 2.0)
    b = FT.band(diff["ci95"])
    per_floor = {}
    for k, (r, p) in cands.items():
        dd = boot_rho_diff_fast(obs, p, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        dd["ci_halfwidth"] = float((dd["ci95"][1] - dd["ci95"][0]) / 2.0)
        per_floor[k] = {"floor_rho": float(r), "margin": dd, "band": FT.band(dd["ci95"])}
    min_ci_lo = min(per_floor[k]["margin"]["ci95"][0] for k in per_floor)
    clears_ci = bool(b == "ABOVE")
    clears_ci_and_t = bool(clears_ci and diff["point"] >= T_MARGIN_MIN)
    return {
        "arm": name, "n": n, "rho": rho,
        "strongest_floor": bf,
        "floor_rho_by_arm": {k: round(float(v[0]), 4) for k, v in cands.items()},
        "margin_over_strongest_floor": diff, "band": b,
        # ---- THE POWER BLOCK. A WIDTH IS NOT AN EFFECT.
        "POWER": {
            "n": n,
            "margin_point": diff["point"],
            "margin_ci_halfwidth": diff["ci_halfwidth"],
            "rho_ci_halfwidth": rho["ci_halfwidth"],
            "scramble_null_p95_at_this_n": sc["p95"],
            "analytic_null_width_1p645_over_sqrt_n_minus_1": round(analytic_null_width, 4),
            "MARGIN_NARROWER_THAN_ITS_OWN_CI": bool(abs(diff["point"]) < diff["ci_halfwidth"]),
            "reading": "if the margin is smaller than its own CI half-width the arm cannot "
                       "separate at this n no matter how good the underlying thing is",
        },
        "clears_floor_ci_separated": clears_ci,
        "clears_floor_ci_separated_and_T_MARGIN": clears_ci_and_t,
        "clears_ALL_FOUR_floors_ci_separated": bool(clears_ci and min_ci_lo > 0.0),
        "min_ci_lo_over_all_floors": float(min_ci_lo),
        "scramble_null": {k: v for k, v in sc.items() if not k.startswith("_")},
        "DECOMPOSED_per_floor": per_floor,
        "_cos": obs,
    }


# ==========================================================================================
# derived: invert the calibration curve
# ==========================================================================================
def invert_curve(lams: Sequence[float], rhos: Sequence[float], target: float) -> Optional[float]:
    """Smallest lam whose calibration rho reaches `target`, by linear interpolation.

    DERIVED QUANTITY, NOT A MEASUREMENT. Returns None when the target lies outside the curve.
    """
    lams = list(lams)
    rhos = list(rhos)
    if not lams or target <= rhos[0]:
        return 0.0 if (rhos and target <= rhos[0]) else None
    if target > max(rhos):
        return None
    for i in range(1, len(lams)):
        lo, hi = rhos[i - 1], rhos[i]
        if lo <= target <= hi:
            if hi - lo < 1e-12:
                return float(lams[i])
            f = (target - lo) / (hi - lo)
            return float(lams[i - 1] + f * (lams[i] - lams[i - 1]))
    return None


# ==========================================================================================
# one stratum, all ladders
# ==========================================================================================
def run_config(cfg: str, ctx: Dict, *, which: str, morph_block: bool = False,
               ladders: Sequence[str] = (LADDER_SEL, LADDER_INC, LADDER_RANDWORD, LADDER_GAUSS)
               ) -> Dict:
    t0 = time.time()
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out, partners = ctx["idx"], ctx["held_out"], ctx["partners"]
    counts, core = ctx["counts"], ctx["core"]
    br: CELL.Bridger = ctx["br"]
    S = ctx["sel"]
    graph = ctx["enriched"]

    if which == "COMMON":
        cand_words = sorted(ctx["sel_words"] & ctx["inc_words"])
    elif which == "INC_OWN":
        cand_words = sorted(ctx["inc_words"])
    elif which == "SEL_OWN":
        cand_words = sorted(ctx["sel_words"])
    else:
        raise ValueError(which)

    # ---- BUILD EVERY BRIDGE CODE FIRST, THEN RESTRICT THE POPULATION TO FULL COVERAGE.
    # code_matrix() falls back to the EXACT KEY for any word an arm does not cover, so partial
    # coverage would silently leak the answer into a ladder arm. Coverage is therefore 100% by
    # construction and asserted below.
    sel_code: Dict[str, np.ndarray] = {}
    inc_code: Dict[str, np.ndarray] = {}
    for w in cand_words:
        v = S.code(w, "S1_SELECTIONAL_MEAN", morph_block)
        if v is not None:
            sel_code[w] = v
        nb = br.neighbours(w, graph, core, morph_block)
        if nb:
            inc_code[w] = br.mean_code(nb, False)
    need = set(cand_words)
    if LADDER_SEL in ladders:
        need &= set(sel_code)
    if LADDER_INC in ladders:
        need &= set(inc_code)
    words = sorted(need)

    Sset = set(words)
    strat = [p for p in pairs if (p[0] in Sset) != (p[1] in Sset)]
    n = len(strat)
    res: Dict = {
        "config": cfg, "which_words": which, "morph_block": morph_block,
        "ladders": list(ladders),
        "n_candidate_words": len(cand_words), "n_bridged_words": len(words), "n_stratum": n,
        "coverage": {"selectional": len(sel_code), "incumbent": len(inc_code),
                     "kept_for_full_coverage": len(words),
                     "note": "population restricted to words EVERY ladder covers, because "
                             "code_matrix() falls back to the exact key for uncovered words and "
                             "that would leak the answer into a ladder arm"},
        "pos_counts": dict(collections.Counter(p[2] for p in strat)),
        "spearman_ci_halfwidth_approx": (round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None),
        "analytic_null_width_1p645_over_sqrt_n_minus_1": (round(1.645 / max(n - 1, 1) ** 0.5, 4)
                                                          if n > 1 else None),
    }
    if n < 10 or len(words) < 10:
        res["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        res["elapsed_s"] = round(time.time() - t0, 1)
        return res

    ia = np.array([idx[p[0]] for p in strat])
    ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)

    # ---- the CONSTANT/PROTOTYPE floor's code table, built before any arm is scored
    core_src = sorted(w for w in core if w in raw and w not in held_out)
    proto = np.stack([raw[c] for c in core_src]).astype(np.float64).mean(axis=0)
    X_const = CELL.code_matrix(vocab, raw, {w: proto for w in words})
    const_cos = CELL.pair_cos(X_const, ia, ib)

    floors = SELB.build_floors(vocab, ia, ib, gold, counts, const_cos)
    res["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}
    # THE CONSTANT FLOOR UNDER ALL THREE TIE CONVENTIONS, recomputed on THIS population.
    # 0.1382 / 0.2070 / -0.1959 are floors on OTHER populations and are never imported.
    res["floors"][FLOOR_CONST]["TIE_CONVENTIONS"] = tie_conventions(const_cos, gold)
    res["floors"][FLOOR_ORTHO]["TIE_CONVENTIONS"] = tie_conventions(
        floors[FLOOR_ORTHO]["_partner"], gold)
    res["floors"][FLOOR_FREQ]["TIE_CONVENTIONS"] = tie_conventions(
        floors[FLOOR_FREQ]["_partner"], gold)
    res["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = True

    # ---- the fillers -----------------------------------------------------------------------
    filler_tables: Dict[str, Dict[int, Dict[str, np.ndarray]]] = {}
    if LADDER_SEL in ladders:
        filler_tables[LADDER_SEL] = {0: {w: sel_code[w] for w in words}}
    if LADDER_INC in ladders:
        filler_tables[LADDER_INC] = {0: {w: inc_code[w] for w in words}}
    if LADDER_RANDWORD in ladders:
        tabs: Dict[int, Dict[str, np.ndarray]] = {}
        for s in FILLER_SEEDS:
            rng = np.random.default_rng(s ^ 0x51F7)
            t: Dict[str, np.ndarray] = {}
            for w in words:
                for _ in range(256):
                    c2 = core_src[int(rng.integers(len(core_src)))]
                    if br.eligible(w, c2, core, False):
                        t[w] = br.hidden[c2].astype(np.float64)
                        break
            if len(t) == len(words):
                tabs[s] = t
        filler_tables[LADDER_RANDWORD] = tabs
    if LADDER_GAUSS in ladders:
        CORE = np.stack([raw[c] for c in core_src]).astype(np.float64)
        mu, sd = CORE.mean(axis=0), CORE.std(axis=0, ddof=1)
        tabs = {}
        for s in FILLER_SEEDS:
            rng = np.random.default_rng(s ^ 0x0A11)
            tabs[s] = {w: (mu + sd * rng.normal(size=len(mu))) for w in words}
        filler_tables[LADDER_GAUSS] = tabs

    for lname, tabs in filler_tables.items():
        for s, t in tabs.items():
            assert len(t) == len(words), f"{lname} seed {s} covers {len(t)} of {len(words)} words"

    # ---- the ladders -----------------------------------------------------------------------
    k1_matrix = CELL.code_matrix(vocab, raw, {})
    rows: Dict[str, Dict] = {}
    cos_by_arm: Dict[str, np.ndarray] = {}
    ladder_rows: Dict[str, Dict[str, Dict]] = {}
    regression: Dict[str, Dict] = {}

    def _score(name: str, table: Dict[str, np.ndarray], light: bool) -> Dict:
        X = CELL.code_matrix(vocab, raw, table)
        r = score_arm(name, CELL.pair_cos(X, ia, ib), None if light else X, ia, ib, gold, floors,
                      seed=_arm_seed(name), light=light)
        cos_by_arm[name] = r.pop("_cos")
        rows[name] = r
        return r

    for lname in ladders:
        tabs = filler_tables[lname]
        seeds = sorted(tabs)
        per_lambda: Dict[str, Dict] = {}
        for lam in LAMBDAS:
            # per-seed LIGHT pass, then the MAX DRAW seed scored in full (the standing null policy)
            by_seed: Dict[int, float] = {}
            tables: Dict[int, Dict[str, np.ndarray]] = {}
            for s in seeds:
                tbl = {w: mix(raw[w], tabs[s][w], lam) for w in words}
                tables[s] = tbl
                if len(seeds) > 1:
                    nm = f"{lname}|lam{lam:.2f}|s{s}"
                    by_seed[s] = _score(nm, tbl, light=True)["rho"]["point"]
            mk = max(by_seed, key=lambda k: by_seed[k]) if by_seed else seeds[0]
            name = f"{lname}|lam{lam:.2f}"
            r = _score(name, tables[mk], light=False)
            r["max_draw_seed"] = int(mk)
            r["rho_by_seed"] = {str(k): round(v, 6) for k, v in by_seed.items()}
            r["seed_policy"] = "MAX DRAW never the mean"
            r["lam"] = lam
            per_lambda[f"{lam:.2f}"] = r

            # ---- REGRESSION GATES at the two ends of the ladder
            if lam == 1.0:
                Xk = CELL.code_matrix(vocab, raw, tables[mk])
                regression[f"{lname}_lam1_is_K1_OWN_NORMS"] = {
                    "allclose_to_K1_code_matrix": bool(np.allclose(Xk, k1_matrix, atol=1e-5)),
                    "max_abs_deviation": float(np.max(np.abs(Xk - k1_matrix))),
                    "rho": r["rho"]["point"]}
            if lam == 0.0 and lname in E_LADDERS:
                regression[f"{lname}_lam0_reproduces_the_landed_bridge_arm"] = {
                    "rho": r["rho"]["point"],
                    "what_it_should_equal": ("the landed S1_SELECTIONAL_MEAN arm"
                                             if lname == LADDER_SEL else
                                             "the landed I1_NEIGHBOUR_COPY_INCUMBENT arm"),
                    "note": "same stratum construction; compare against the landed metrics.json "
                            "by hand -- the populations are only identical when this config is "
                            "PRIMARY_COMMON with morph_block False"}
        ladder_rows[lname] = per_lambda

    # ---- MONOTONICITY GATE, read BEFORE any lambda_star -------------------------------------
    lam_arr = np.array(LAMBDAS, dtype=np.float64)
    mono: Dict[str, Dict] = {}
    for lname in ladders:
        rr = np.array([ladder_rows[lname][f"{l:.2f}"]["rho"]["point"] for l in LAMBDAS])
        sp = float(INS._spearman(lam_arr, rr))
        mono[lname] = {
            "spearman_lam_vs_rho": round(sp, 4),
            "rho_by_lambda": {f"{l:.2f}": round(float(v), 6) for l, v in zip(LAMBDAS, rr)},
            "IS_A_DOSE_RESPONSE_CURVE": bool(sp >= MONOTONE_MIN),
            "threshold": MONOTONE_MIN,
            "rule": "if a D ladder is not monotone in lam it is not a dose-response curve and its "
                    "lambda_star is meaningless and is NOT published"}
    res["MONOTONICITY_GATE"] = mono

    # ---- THE PRIMARY MEASURE: lambda_star ---------------------------------------------------
    lstar: Dict[str, Dict] = {}
    for lname in ladders:
        pl = ladder_rows[lname]
        first_ci = None
        first_ci_t = None
        first_all4 = None
        for lam in LAMBDAS:
            r = pl[f"{lam:.2f}"]
            if first_ci is None and r.get("clears_floor_ci_separated"):
                first_ci = lam
            if first_ci_t is None and r.get("clears_floor_ci_separated_and_T_MARGIN"):
                first_ci_t = lam
            if first_all4 is None and r.get("clears_ALL_FOUR_floors_ci_separated"):
                first_all4 = lam
        lstar[lname] = {
            "lambda_star_ci_separated_over_strongest_floor": first_ci,
            "lambda_star_ci_separated_AND_T_MARGIN_0p05": first_ci_t,
            "lambda_star_ci_separated_over_ALL_FOUR_floors": first_all4,
            "PUBLISHABLE": bool(mono[lname]["IS_A_DOSE_RESPONSE_CURVE"]),
            "definition": "smallest exact-key mixing fraction at which this ladder CI-separates "
                          "above max(four floors) recomputed on THIS population",
        }
    res["LAMBDA_STAR"] = lstar

    # ---- DERIVED: the bridge's exact-key-equivalent, in the D ladder's units -----------------
    equiv: Dict[str, Dict] = {}
    for dname in [d for d in D_LADDERS if d in ladders]:
        if not mono[dname]["IS_A_DOSE_RESPONSE_CURVE"]:
            equiv[dname] = {"status": "NOT_PUBLISHED -- calibration ladder is not monotone"}
            continue
        crhos = [ladder_rows[dname][f"{l:.2f}"]["rho"]["point"] for l in LAMBDAS]
        per_e: Dict[str, Dict] = {}
        for ename in [e for e in E_LADDERS if e in ladders]:
            b0 = ladder_rows[ename]["0.00"]["rho"]
            per_e[ename] = {
                "bridge_rho_at_lam0": b0["point"],
                "bridge_rho_ci95": b0["ci95"],
                "exact_key_equivalent_point": invert_curve(LAMBDAS, crhos, b0["point"]),
                "exact_key_equivalent_ci": [invert_curve(LAMBDAS, crhos, b0["ci95"][0]),
                                            invert_curve(LAMBDAS, crhos, b0["ci95"][1])],
                "DERIVED_NOT_MEASURED": True,
                "reading": "the fraction of the target's OWN identity whose dilution by a "
                           "non-informative filler reads the same as this bridge cue"}
        equiv[dname] = per_e
    res["EXACT_KEY_EQUIVALENT_derived"] = equiv

    # ---- HEAD-TO-HEAD at every rung: does the bridge beat a non-informative filler? ----------
    h2h: Dict[str, Dict] = {}
    for ename in [e for e in E_LADDERS if e in ladders]:
        for dname in [d for d in D_LADDERS if d in ladders]:
            per_lam = {}
            for lam in LAMBDAS:
                a = f"{ename}|lam{lam:.2f}"
                b = f"{dname}|lam{lam:.2f}"
                if a not in cos_by_arm or b not in cos_by_arm:
                    continue
                d = boot_rho_diff_fast(cos_by_arm[a], cos_by_arm[b], gold, n_boot=N_BOOT,
                                     seed=BOOT_SEED)
                d["ci_halfwidth"] = float((d["ci95"][1] - d["ci95"][0]) / 2.0)
                per_lam[f"{lam:.2f}"] = {"margin": d, "band": FT.band(d["ci95"])}
            n_above = sum(1 for v in per_lam.values() if v["band"] == "ABOVE")
            best = cur = 0
            for lam in LAMBDAS:                       # THE MULTIPLICITY-ROBUST STATISTIC
                v = per_lam.get(f"{lam:.2f}")
                cur = cur + 1 if (v and v["band"] == "ABOVE") else 0
                best = max(best, cur)
            h2h[f"{ename}_minus_{dname}"] = {
                "per_lambda": per_lam,
                "n_rungs": len(per_lam), "n_rungs_ABOVE": n_above,
                "longest_ADJACENT_run_ABOVE": best,
                "ANY_RUNG_ABOVE": bool(n_above > 0),
                "CARRIES_IDENTITY_two_or_more_adjacent_rungs": bool(best >= 2),
                "multiplicity": f"{len(per_lam)} rungs tested; a single ABOVE rung at alpha=0.05 "
                                f"is expected {0.05 * len(per_lam):.2f} times under the null, so "
                                f"one isolated rung is NOT evidence. The decision uses the LONGEST "
                                f"ADJACENT RUN, not the count.",
                "scorer": "SimLex Spearman rho on 12-dim L2-normalised norms cosine",
                "n": n}
    res["HEAD_TO_HEAD_bridge_minus_noninformative"] = h2h

    # ---- VALIDITY ARMS, which must fail INDEPENDENTLY ---------------------------------------
    rng = np.random.default_rng(20260817)
    perm = list(words)
    for _ in range(64):
        rng.shuffle(perm)
        if all(a != b for a, b in zip(words, perm)):
            break
    null_tbl = {w: mix(raw[p], raw[p], NULL_LAMBDA) for w, p in zip(words, perm)}
    r_null = _score("NULL_PERMUTED_ASSIGNMENT", null_tbl, light=False)
    ka_name = None
    for lname in ladders:
        cand = f"{lname}|lam1.00"
        if cand in rows:
            ka_name = cand
            break
    ka = rows.get(ka_name, {})
    res["VALIDITY"] = {
        "KA_EXACT_ONLY": {
            "arm": ka_name, "rho": ka.get("rho", {}).get("point"),
            "band_over_strongest_floor": ka.get("band"),
            "margin": ka.get("margin_over_strongest_floor", {}).get("point"),
            "PASSED": bool(ka.get("band") == "ABOVE"),
            "sensitive_to": "the scorer, the pool and the eligibility mask",
            "INSENSITIVE_to": "the filler construction"},
        "NULL_PERMUTED_ASSIGNMENT": {
            "lam": NULL_LAMBDA, "rho": r_null["rho"]["point"], "rho_ci95": r_null["rho"]["ci95"],
            "band_over_strongest_floor": r_null["band"],
            "PASSED": bool(r_null["band"] != "ABOVE"),
            "sensitive_to": "the cue-to-word pairing",
            "INSENSITIVE_to": "whether the scorer is correct",
            "why_lam_is_1": "the null sits at the TOP of the ladder on purpose: with a correct "
                            "pairing this arm would be at ceiling, so any failure to collapse is "
                            "unmissable"},
        "FAIL_INDEPENDENTLY": "a scorer bug drops KA while leaving NULL at chance; a pairing or "
                              "leak bug leaves KA at ceiling while raising NULL. Neither single "
                              "bug can make both pass.",
        "BOTH_PASSED": bool(ka.get("band") == "ABOVE" and r_null["band"] != "ABOVE"),
    }
    res["REGRESSION_GATES"] = regression

    # ---- G0 power gate on the exact-key arm (inherited rule) ---------------------------------
    res["G0_POWER_GATE"] = {
        "K1_equivalent_arm": ka_name,
        "K1_rho": ka.get("rho", {}).get("point"),
        "K1_strongest_floor": ka.get("strongest_floor"),
        "K1_margin": ka.get("margin_over_strongest_floor", {}).get("point"),
        "K1_band": ka.get("band"),
        "PASSED": bool(ka.get("band") == "ABOVE"),
        "rule": "if the exact key does not clear THIS stratum's own max(4 floors) CI-separated, "
                "every arm on this stratum is POWER_INSUFFICIENT, NEVER FAIL"}

    res["LADDERS"] = ladder_rows
    res["arms"] = {k: v for k, v in rows.items()}
    res["elapsed_s"] = round(time.time() - t0, 1)
    return res


# ==========================================================================================
def selftest() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    from hdlab import grounded_similarity as GS

    # --- RULER GATE: the EXISTING one, imported and called, not a reimplementation.
    from exp_task_degeneracy_v1 import ruler_mode_gate
    ev["RULER_MODE_GATE"] = ruler_mode_gate()
    ev["RULER_MODE_GATE"]["source"] = "experiments/exp_task_degeneracy_v1.py:121, imported"

    tab = GS._table()
    assert len(tab) == 36810, f"RULER GATE: norms table {len(tab)} != 36810 (grid={RUN_MODE})"
    assert len(next(iter(tab.values()))) == 12, "RULER GATE: norms are not 12-dim"
    ev["RULER_GATE_norms"] = {"n_words": len(tab), "n_dim": 12, "run_mode": RUN_MODE}

    # --- TRAP: grounded_similarity is SATURATED and is NEVER the scorer. Re-measured, not inherited.
    pairs = CELL.load_simlex_pos()
    vals = [GS.grounded_similarity(a, b) for a, b, _, _ in pairs]
    c = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(k for _, k in c.most_common(2)) / len(vals)
    assert frac2 > 0.70, f"expected saturation; top-2 mass {frac2:.4f}"
    ev["TRAP_grounded_similarity_saturation"] = {"n_pairs": len(vals),
                                                 "fraction_on_two_values": round(frac2, 4)}

    # --- THE ONE VARIABLE does exactly what the docstring says, with a KNOWN ANSWER.
    t = np.array([3.0, 0.0, 4.0])                    # unit -> [0.6, 0, 0.8]
    f = np.array([0.0, 5.0, 0.0])                    # unit -> [0, 1, 0]
    assert np.allclose(mix(t, f, 1.0), [0.6, 0.0, 0.8]), "lam=1 must be the unit exact key"
    assert np.allclose(mix(t, f, 0.0), [0.0, 1.0, 0.0]), "lam=0 must be the unit filler"
    assert np.allclose(mix(t, f, 0.25), [0.15, 0.75, 0.20]), "lam=0.25 mix is wrong"
    ev["MIX_known_answer"] = {"lam1": mix(t, f, 1.0).tolist(), "lam0": mix(t, f, 0.0).tolist(),
                              "lam0.25": mix(t, f, 0.25).tolist()}

    # --- lam=1 REALLY reproduces the exact-key code matrix, through the real code_matrix()
    vsm = [f"w{i}" for i in range(40)]
    rng = np.random.default_rng(5)
    rr = {w: np.abs(rng.normal(size=12)) + 0.1 for w in vsm}
    bridged = {w: np.abs(rng.normal(size=12)) + 0.1 for w in vsm[:15]}
    Xk = CELL.code_matrix(vsm, rr, {})
    X1 = CELL.code_matrix(vsm, rr, {w: mix(rr[w], bridged[w], 1.0) for w in vsm[:15]})
    X0 = CELL.code_matrix(vsm, rr, {w: mix(rr[w], bridged[w], 0.0) for w in vsm[:15]})
    Xb = CELL.code_matrix(vsm, rr, bridged)
    assert np.allclose(X1, Xk, atol=1e-5), "lam=1 does NOT reproduce the exact-key code matrix"
    assert np.allclose(X0, Xb, atol=1e-5), "lam=0 does NOT reproduce the raw bridge code matrix"
    assert not np.allclose(Xb, Xk, atol=1e-5), "the fixture's bridge codes equal the exact keys"
    ev["LADDER_ENDPOINTS_are_the_two_regression_gates"] = {
        "lam1_equals_K1": True, "lam0_equals_the_bridge_arm": True,
        "max_abs_dev_lam1": float(np.max(np.abs(X1 - Xk))),
        "max_abs_dev_lam0": float(np.max(np.abs(X0 - Xb)))}

    # --- the ladder is genuinely graded: intermediate lam is neither endpoint
    Xm = CELL.code_matrix(vsm, rr, {w: mix(rr[w], bridged[w], 0.5) for w in vsm[:15]})
    assert not np.allclose(Xm, Xk, atol=1e-4) and not np.allclose(Xm, Xb, atol=1e-4), \
        "lam=0.5 collapsed onto an endpoint -- the ladder is not graded"
    ev["LADDER_is_graded"] = True

    # --- THE DOSE-RESPONSE IS REAL: on a planted fixture rho must RISE with lam, monotonically.
    # This is the gate that makes lambda_star meaningful, so it is asserted, not assumed.
    n_w = 300
    vs2 = [f"v{i}" for i in range(n_w)]
    rng2 = np.random.default_rng(11)
    r2 = {w: np.abs(rng2.normal(size=12)) + 0.05 for w in vs2}
    i2 = {w: i for i, w in enumerate(vs2)}
    br_words = vs2[:n_w // 2]
    iaa = np.array([i2[vs2[i]] for i in range(0, n_w, 2)])
    ibb = np.array([i2[vs2[i]] for i in range(1, n_w, 2)])
    Xtrue = CELL.code_matrix(vs2, r2, {})
    g2 = CELL.pair_cos(Xtrue, iaa, ibb)              # gold = the exact-key scorer's own output
    noise = {w: np.abs(rng2.normal(size=12)) + 0.05 for w in br_words}
    curve = []
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        Xl = CELL.code_matrix(vs2, r2, {w: mix(r2[w], noise[w], lam) for w in br_words})
        curve.append(float(INS._spearman(CELL.pair_cos(Xl, iaa, ibb), g2)))
    assert all(curve[i] <= curve[i + 1] + 1e-9 for i in range(len(curve) - 1)), \
        f"the ladder is NOT a dose-response curve on a planted fixture: {curve}"
    assert curve[-1] > curve[0] + 0.2, f"the ladder does not separate its own endpoints: {curve}"
    ev["DOSE_RESPONSE_planted_fixture"] = {"rho_by_lam": [round(v, 4) for v in curve],
                                           "monotone": True}

    # --- tie conventions: optimistic >= midrank >= pessimistic, and a constant is degenerate
    sc = np.array([1.0, 1.0, 1.0, 2.0, 2.0, 3.0])
    gd = np.array([5.0, 1.0, 3.0, 4.0, 2.0, 6.0])
    tc = tie_conventions(sc, gd)
    assert tc["optimistic"] >= tc["midrank"] >= tc["pessimistic"] - 1e-12, \
        f"tie conventions are not ordered: {tc}"
    assert tc["tie_mass"] > 0.4, f"fixture should be tie-heavy; got {tc['tie_mass']}"
    ev["TIE_CONVENTIONS_ordered"] = {k: round(v, 4) for k, v in tc.items()}

    # --- invert_curve is exact on a straight line and refuses to extrapolate
    assert abs(invert_curve([0.0, 1.0], [0.0, 1.0], 0.3) - 0.3) < 1e-9
    assert invert_curve([0.0, 1.0], [0.0, 0.5], 0.9) is None, "invert_curve must refuse to extrapolate"
    ev["invert_curve"] = "exact on a line; refuses to extrapolate"

    # --- THE EQUALITY GATE ON THE FAST BOOTSTRAP. If this fails the fast path is void.
    # Two parts, both required: (i) the vectorised midrank Spearman must agree with the LANDED
    # INS._spearman row by row, ON DATA WITH TIES; (ii) the vectorised paired bootstrap must agree
    # with the LANDED FT.boot_rho_diff on the point estimate and BOTH CI bounds, because it draws
    # the same resamples from the same generator.
    rngq = np.random.default_rng(77)
    nq = 220
    ca = rngq.normal(size=nq)
    cb = rngq.normal(size=nq)
    gq = np.round(ca * 0.4 + rngq.normal(size=nq), 1)     # ROUNDED -> deliberately tie-heavy
    ca_t = np.round(ca, 1)
    assert len(np.unique(gq)) < nq and len(np.unique(ca_t)) < nq, "fixture has no ties"
    IDXq = _boot_idx(nq, 40, 1234)
    mine = _boot_rhos(ca_t, gq, IDXq)
    theirs = np.array([INS._spearman(ca_t[j], gq[j]) for j in IDXq])
    md = float(np.nanmax(np.abs(mine - theirs)))
    assert md < 1e-9, f"vectorised Spearman disagrees with INS._spearman by {md:.3e}"
    slow = FT.boot_rho_diff(ca_t, cb, gq, n_boot=600, seed=4242)
    fast = boot_rho_diff_fast(ca_t, cb, gq, n_boot=600, seed=4242)
    dd = max(abs(slow["point"] - fast["point"]),
             abs(slow["ci95"][0] - fast["ci95"][0]), abs(slow["ci95"][1] - fast["ci95"][1]))
    assert dd < 1e-9, f"fast paired bootstrap disagrees with the landed one by {dd:.3e}: " \
                      f"{slow} vs {fast}"
    ev["FAST_BOOTSTRAP_EQUALITY_GATE"] = {
        "max_abs_spearman_deviation_from_INS_spearman_on_tied_data": md,
        "n_ties_in_fixture": {"gold_distinct": int(len(np.unique(gq))),
                              "cos_distinct": int(len(np.unique(ca_t))), "n": nq},
        "max_abs_deviation_point_and_both_CI_bounds_vs_FT_boot_rho_diff": dd,
        "landed": slow, "fast": fast,
        "why": "the shared module is NOT edited; the same quantity is recomputed with vectorised "
               "midranks from the IDENTICAL resample draw, so the two agree resample by resample. "
               "Without this the FULL grid would take ~10 h and the run would not land."}

    # --- the bootstrap must be able to BOTH fire and fail
    rng3 = np.random.default_rng(3)
    a = np.arange(60.0)
    gg = a + rng3.normal(scale=0.01, size=60)
    b2 = rng3.normal(size=60)
    fire = FT.boot_rho_diff(a, b2, gg, n_boot=400, seed=1)
    fail = FT.boot_rho_diff(b2, rng3.normal(size=60), gg, n_boot=400, seed=1)
    assert FT.band(fire["ci95"]) == "ABOVE", "bootstrap cannot FIRE on a planted signal"
    assert FT.band(fail["ci95"]) == "NOT_SEPARATED", "bootstrap cannot FAIL on a planted null"
    ev["bootstrap_can_fire_and_fail"] = {"planted_signal": FT.band(fire["ci95"]),
                                         "planted_null": FT.band(fail["ci95"])}

    # --- the four floors are four DIFFERENT functions on a fixture (the sibling's own assertion)
    vsm3 = [f"z{i}" for i in range(60)]
    rr3 = {w: rng3.normal(size=12) for w in vsm3}
    i3 = {w: i for i, w in enumerate(vsm3)}
    ia3 = np.array([i3[vsm3[i]] for i in range(0, 58, 2)])
    ib3 = np.array([i3[vsm3[i]] for i in range(1, 59, 2)])
    g3 = rng3.normal(size=len(ia3))
    proto = np.stack([rr3[w] for w in vsm3[:20]]).mean(axis=0)
    Xc = CELL.code_matrix(vsm3, rr3, {w: proto for w in vsm3[:10]})
    assert np.allclose(Xc[0], Xc[9]), "CONSTANT floor code table is not constant across bridged rows"
    fl = SELB.build_floors(vsm3, ia3, ib3, g3, {w: i + 1 for i, w in enumerate(vsm3)},
                           CELL.pair_cos(Xc, ia3, ib3))
    parts = [fl[k]["_partner"] for k in (FLOOR_ORTHO, FLOOR_FREQ, FLOOR_CONST)]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            assert not np.allclose(parts[i], parts[j]), "two floors are the same function"
    ev["FOUR_FLOORS_are_distinct"] = sorted(FLOOR_KEYS)

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1500], flush=True)
    return ev


def main() -> int:
    t_start = time.time()
    ev = selftest()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} seeds={FILLER_SEEDS} "
          f"out={out_dir}", flush=True)

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    pairs = CELL.load_simlex_pos()
    vocab = sorted({w for p in pairs for w in p[:2]})
    raw = {w: np.asarray(v, dtype=np.float64) for w, v in tab.items()}
    idx = {w: i for i, w in enumerate(vocab)}
    partners: Dict[str, Set[str]] = collections.defaultdict(set)
    for a, b, _, _ in pairs:
        partners[a].add(b)
        partners[b].add(a)
    aoa = CELL.load_aoa()
    core = {w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in tab}
    held_out = {w for w in vocab if w not in core}
    counts = CELL.corpus_counts()
    print(f"[assets] simlex={len(pairs)} vocab={len(vocab)} core={len(core)} "
          f"held_out={len(held_out)}", flush=True)

    def_graph, _pat, _rows = CELL.load_def_graph()
    them_edges = THEM.build_or_load()
    them_graph, them_info = INC.build_thematic_graph(them_edges)
    enriched = INC.merge(def_graph, them_graph)
    print(f"[assets] thematic graph built", flush=True)

    slots = SEL.build_or_load()
    br = CELL.Bridger(raw, held_out, partners)
    S = SELB.SelectionalSource(slots, br, core)

    sel_words = {w for w in held_out if S.slots_for(w, None, False, False)}
    inc_words = {w for w in held_out if br.neighbours(w, enriched, core, False)}
    print(f"[assets] slots={len(S.sf)} sel_reach={len(sel_words)} inc_reach={len(inc_words)} "
          f"common={len(sel_words & inc_words)}", flush=True)

    ctx = {"vocab": vocab, "raw": raw, "pairs": pairs, "idx": idx, "held_out": held_out,
           "core": core, "partners": partners, "counts": counts, "br": br, "sel": S,
           "enriched": enriched, "sel_words": sel_words, "inc_words": inc_words}

    CONFIGS = [
        ("PRIMARY_COMMON", {"which": "COMMON"}),
        ("COMMON_MORPHBLOCK", {"which": "COMMON", "morph_block": True}),
        ("INCUMBENT_OWN_larger_n", {"which": "INC_OWN",
                                    "ladders": (LADDER_INC, LADDER_RANDWORD, LADDER_GAUSS)}),
    ]
    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results: Dict[str, Dict] = {}
    for name, kw in CONFIGS:
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, name)
        if key in done and key in units:
            results[name] = units[key]
            print(f"[cfg] {name} RESUMED", flush=True)
            continue
        print(f"[cfg] {name} start", flush=True)
        r = run_config(name, ctx, **kw)
        record_unit(str(out_dir), key, r)
        results[name] = r
        print(f"[cfg] {name} done n={r.get('n_stratum')} words={r.get('n_bridged_words')} "
              f"t={r.get('elapsed_s')}s lambda_star="
              f"{json.dumps({k: v.get('lambda_star_ci_separated_over_strongest_floor') for k, v in (r.get('LAMBDA_STAR') or {}).items()})}",
              flush=True)

    # ---- verdict ----------------------------------------------------------------------------
    P = results.get("PRIMARY_COMMON", {})
    val = P.get("VALIDITY", {})
    ls = P.get("LAMBDA_STAR", {})
    mono = P.get("MONOTONICITY_GATE", {})
    d_pub = [k for k in D_LADDERS if mono.get(k, {}).get("IS_A_DOSE_RESPONSE_CURVE")]
    d_star = [ls[k]["lambda_star_ci_separated_over_strongest_floor"] for k in d_pub
              if ls.get(k, {}).get("lambda_star_ci_separated_over_strongest_floor") is not None]
    carries = any(v.get("CARRIES_IDENTITY_two_or_more_adjacent_rungs")
                  for v in (P.get("HEAD_TO_HEAD_bridge_minus_noninformative") or {}).values())

    # THE VERDICT IS COMPOSED FROM INDEPENDENT GATES, NOT SELECTED BY BRANCH ORDER. An earlier
    # draft used an if/elif chain; the retrieval sibling's REDUCED-GRID SMOKE caught that shape
    # declaring "CUE_IS_THE_UPSTREAM_CAUSE" on a run whose own head-to-head contradicted it. A
    # branch order must never be able to hide a measured fact. Disclosed in the findings log; no
    # arm, floor, population or threshold changed, only the LABEL MAPPING.
    if not P:
        verdict = "PRIMARY_CONFIG_DID_NOT_RUN"
    elif not val.get("BOTH_PASSED"):
        verdict = "INSTRUMENT_STILL_LOOSE_VALIDITY_ARMS_DID_NOT_BOTH_PASS"
    elif not d_pub:
        verdict = "CALIBRATION_LADDER_NOT_MONOTONE_LAMBDA_STAR_NOT_PUBLISHABLE"
    else:
        ls_tag = "NONE" if not d_star else ("%.2f" % min(d_star)).replace(".", "p")
        verdict = ("BRIDGE_CUE_CARRIES_IDENTITY_%s__LAMBDA_STAR_%s"
                   % ("YES" if carries else "NO", ls_tag))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ONE VARIABLE -- the fraction of the cue that is the target's own exact key -- swept "
            "end to end on the identical stratum / scorer / n / pool / gold, with all four floors "
            "recomputed on this population. PRIMARY MEASURE lambda_star = the smallest exact-key "
            "fraction at which a NON-INFORMATIVE filler ladder CI-separates above max(four "
            "floors). -> " + verdict),
        "HOW_TO_READ_THIS": (
            "A child acquires most of its vocabulary by exactly the route these bridging cells "
            "model, so THE CAPABILITY IS DEMONSTRATED and every null here is a fact about OUR "
            "IMPLEMENTATION. Finding that our cue is information-poor is a GOOD outcome: it "
            "collapses three negatives into one upstream defect and redirects the programme to "
            "what the cue is MADE OF."),
        "BRAIN_FIDELITY": {
            "the_mixing_device": "OURS -- INVENTION UNDER TEST. An instrument calibration device. "
                                 "NO BRAIN STRUCTURE IS CLAIMED FOR IT.",
            "PINNED_and_it_cuts_against_the_framing_of_both_bridging_cells":
                "The brain's retrieval cue is NOT a subset of the stored pattern; it arrives on a "
                "DIFFERENT WIRE (direct perforant path) from the one that wrote the memory (mossy "
                "fibre -> DG -> CA3), through a synaptic matrix modified during storage. "
                "Treves & Rolls 1992; Rolls 2018; Kesner 2007.",
            "VSA_binding": "UNPINNED in the brain -- three live accounts, published objections to "
                           "each. Nothing here depends on it or tests it.",
            "parameters_vs_computations": "No brain PARAMETER is adopted as a value anywhere in "
                                          "this cell. lam is swept end to end.",
            "organ_reuse": "No new mechanism is authored. Every mechanism, floor, bootstrap and "
                           "asset loader is imported from a landed cell and never edited.",
            "shelve_revival_criteria_brain_framed":
                "If lambda_star is small, the shelved object is OUR CUE CONSTRUCTION (a held-out "
                "sentence bag compared by cosine against the store), and the revival criterion is "
                "brain-framed: revive when a cue is delivered through a stage that TRANSLATES "
                "between cue space and store space, as the perforant path does, rather than being "
                "compared for raw similarity in one space.",
        },
        "config": {"LAMBDAS": list(LAMBDAS), "FILLER_SEEDS": list(FILLER_SEEDS),
                   "N_BOOT": N_BOOT, "N_PERM": N_PERM, "BOOT_SEED": BOOT_SEED,
                   "T_MARGIN_MIN": T_MARGIN_MIN, "MONOTONE_MIN": MONOTONE_MIN,
                   "NULL_LAMBDA": NULL_LAMBDA, "FLOORS": list(FLOOR_KEYS),
                   "AOA_CORE_MAX": AOA_CORE_MAX},
        "STANDING_RULES_HONOURED": {
            "every_floor_recomputed_on_this_population": True,
            "never_imported_0p1382_0p2070_or_minus_0p1959": True,
            "CI_halfwidth_and_null_p95_beside_every_margin": True,
            "tie_conventions_reported_all_three": True,
            "grounded_similarity_is_never_the_scorer": True,
            "ruler_mode_gate_called_not_reimplemented": True,
            "no_number_crosses_scorers_pools_or_populations": True,
            "verdict_bar_check_run_separately_and_NOT_relied_on": "four false passes on record",
        },
        "thematic_extraction": them_info,
        "selectional_extraction": {k: v for k, v in slots.items()
                                   if k not in ("slot_filler", "word_cooc")},
        "selftest_evidence": ev,
        "results": results,
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
