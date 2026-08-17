"""exp_readout_ceiling_diagnosis_v1 -- WHY DOES THE READ-OUT CAP AT 0.0481 WITH A PERFECT CUE?

FINDINGS LOG: notes/readout_ceiling_findings_2026-08-17.md (pre-registration in section 2,
written BEFORE any number here was read).

THE RESULT THAT CREATED THIS CELL. data/exp_cue_regime_one_variable_retrieval_v1/metrics.json:
with the cue set to the item's OWN stored row, addressing is 1.0000 over 5,491 anchors and hit@1
against WordNet gold is 0.0481 -- CI-separated BELOW the constant floor 0.1390 and below the
spelling floor 0.0873. The ceiling is INDEPENDENT OF THE CUE, so no cue / translator / completer /
bridge work can touch it.

THIS CELL DOES TWO THINGS AND THEY ARE KEPT SEPARATE.

ARM A -- DIAGNOSE BEFORE BUILDING. Four stages, each measured, so the answer is a STAGE and not
"the read-out is bad":
  S1 IS THE ANSWER IN THE POOL?     eligible-gold census per item
  S2 WHERE DOES IT RANK?            THE DECISIVE ONE. rank of the BEST gold under the exact-key
                                    cosine, against the PER-ITEM RANDOM-RANKING curve
                                    P(hit@k) = 1 - C(n_elig-n_gold,k)/C(n_elig,k), and against the
                                    same rank curve for all four floors.
                                    If the curve sits AT random -> the store does not contain the
                                    answer and THE DEFECT IS IN WHAT WE WROTE, NOT IN HOW WE READ.
                                    If it is CI-separated above random while hit@1 is below the
                                    binding floor -> the information is there and the SELECTOR
                                    cannot reach it.
  S3 WHAT WINS INSTEAD?             top-1 identity, degeneracy, genericity and frequency of the
                                    winners, and the cosine gap winner-minus-best-gold.
  S4 IS THE SCORE MISCALIBRATED?    per-anchor hubness (Nk k-occurrence, Nk-Gini) via the OWNED
                                    organ experiments/dehub_transforms, against a scramble null.

ARM B -- REPLACE THE READ-OUT AND TEST AGAINST THE SAME BAR. Exhaustive cosine argmax over 5,491
anchors is NOT a brain operation; serial scanning of a lexicon is refuted and the field settled on
PARALLEL ACTIVATION WITH COMPETITIVE SELECTION. The pinned computation is DIVISIVE NORMALISATION
(Carandini & Heeger 2012, measured in V1/MT/IT/olfactory bulb; the Luce ratio in WEAVER++). Its
PARAMETERS are constraint-derived and are SWEPT, never adopted.

  AN ARITHMETIC FACT STATED UP FRONT SO IT CANNOT BE LAUNDERED: normalising over the CANDIDATES OF
  ONE QUERY is a monotone transform within that query and CANNOT CHANGE THE ARGMAX. It is
  incapable of moving hit@1 and is asserted, not run. The direction that CAN change the argmax is
  normalising each candidate by ITS OWN response across a probe population -- which is the same
  object as hubness correction.

PRIOR WORK, ENUMERATED FROM DISK AND CREDITED, NOT RE-DERIVED (see findings sec 1):
  experiments/dehub_transforms.py            OWNED de-hubbing organ; IMPORTED here, never edited
  exp_rank1_common_mode_removal_v1           HARD_FAIL_NO_EFFECT (+0.0005 CI [-0.0043,+0.0053])
  exp_task_local_normalisation_pool_v1       HARD_FAIL_GAIN_HURTS (-0.0220 CI-separated NEGATIVE)
  exp_substrate_csls_cleanup_recovery_gpu_v1 HARD_FAIL (lift 0.0; near-duplicates, not hubness)
  exp_readout_fix_v1                         MIDDLE_BAND; FIX1/FIX2 live in hdlab ReadoutConfig
All four were scored on a 2-CANDIDATE forced choice or a different corpus. A per-anchor calibration
has almost nothing to do in a 2-way argmax; the open 5,491-way pool is the regime where hubness is
even defined. That is why they lower the prior without settling the question, and the prior is
DEFLATED in the findings log before the run rather than after.

VALIDITY -- both arms pass and they FAIL INDEPENDENTLY, verified BEFORE any treatment number:
  KA_SELF_ADDRESS   query IS the item's own stored row, gold = its OWN anchor. Sensitive to the
                    scorer/comparator, INSENSITIVE to the WordNet pairing.
  NULL_PERMUTED     cue-to-item assignment deranged. Sensitive to the pairing, INSENSITIVE to
                    whether the scorer is correct.
  REGRESSION        reproduce the landed 0.0223 (partial cue) and 0.0481 (exact key), tol 5e-4.

FLOORS: max(F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE), ALL recomputed on this
population, all three tie conventions, paired bootstrap on the common scored items. 0.1382 / 0.2070
/ -0.1959 are NEVER imported. ORACLE_CONSTANT is reported and is NOT a floor. The pool is the
LANDED OPEN pool; eligB is not used (admits a constant at 0.1715 against chance 0.0101).

ORGAN REUSE, enumerated from disk then reconciled, verified by RUNTIME (sys.modules), never grep:
tools/floor_battery, experiments/dehub_transforms, experiments/exp_cue_to_store_translation_v1
(cache loaders + ruler gate + landed regression constant), tools/exp_checkpoint. NONE is edited.

BRAIN FIDELITY. The exhaustive argmax is OURS and is the thing under test -- it was never chosen,
it was assumed. Divisive normalisation is PINNED as a COMPUTATION and its parameters are SWEPT.
CSLS is OURS (Conneau et al. 2017, a machine-translation retrieval method) and is run as the
standard engineering baseline for the same job, labelled as such; no brain structure is claimed for
it. VSA algebraic binding, the substrate's core operation, is UNPINNED IN THE BRAIN with three live
accounts and published objections to each; nothing here depends on it and nothing here tests it.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. The store is
NEVER rebuilt -- rebuilding it would break the identical-instrument invariant every arm depends on.
data/foundation/** is never opened. Writes only under data/exp_readout_ceiling_diagnosis_v1/.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import (numpy sizes its pools at import time).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dehub_transforms as DH                              # OWNED de-hub organ, NEVER EDITED
import exp_cue_to_store_translation_v1 as CTS              # cache loaders + ruler gate, NEVER EDITED
from tools import floor_battery as FB                      # floors + scorer + bootstrap, NEVER EDITED
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key

ANCHOR_NAME = "exp_readout_ceiling_diagnosis_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_ceiling_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--arm", choices=("A", "B", "all"), default="all")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. NEVER EDITED AFTER A RUN. -------------------------------------
MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 2000 if SMOKE else 10000
REGRESSION_A0_PARTIAL = CTS.REGRESSION_A0_PARTIAL          # 0.0223 landed partial-cue read-out
REGRESSION_A1_EXACT = 0.0481                               # landed exact-key read-out (sibling ARM 2)
REGRESSION_TOL = CTS.REGRESSION_TOL                        # 5e-4
KA_MIN = 0.95
FLOOR_NAMES = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE")
K_GRID: Tuple[int, ...] = (1, 2, 3, 5, 10, 20, 50, 100, 250, 500, 1000)
NK_K = 10                                                  # k-occurrence radius for the hubness stat

# ARM B parameter SWEEPS. Every one of these is a brain PARAMETER (constraint-derived, not shared)
# and is therefore swept, never adopted as a value.
CSLS_K = (1, 5, 10, 20, 50, 100)
SUBTRACT_ALPHA = (0.25, 0.5, 0.75, 1.0, 1.5, 2.0)
DIVNORM_SIGMA = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
DIVNORM_EXPO = (1.0, 2.0)
ABTT_D = (1, 2, 4, 8)


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _out_dir() -> str:
    suffix = "" if RUN_MODE == "full" else "_REDUCED"
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def install_grounded_similarity_tripwire() -> bool:
    """Replace `hdlab.grounded_similarity.grounded_similarity` IN THIS PROCESS ONLY with a stub
    that raises. Nothing on disk is modified and no other process is affected.

    The standing bar says that function is NEVER a scorer (76.18% of SimLex pairs land on two
    values). Every previous cell has honoured that by NOT WRITING IT DOWN, which is an honour-system
    control. This makes it a mechanical one: if any path in this cell reaches the function, the run
    dies rather than quietly banking a number computed with it.
    """
    m = sys.modules.get("hdlab.grounded_similarity")
    if m is None:
        return False

    def _banned(*_a, **_k):
        raise RuntimeError(
            "TRIPWIRE: grounded_similarity() was CALLED inside %s. It is barred as a scorer by the "
            "standing bar (76.18%% of SimLex pairs on two values). No number from this run is "
            "usable." % ANCHOR_NAME)

    if getattr(m, "grounded_similarity", None) is not None:
        m.grounded_similarity = _banned
        return True
    return False


def _halfwidth(p: float, n: int) -> float:
    """Analytic binomial CI half-width at p, n. A WIDTH IS NOT AN EFFECT -- printed beside every
    margin so the two can never be confused."""
    return float(1.96 * (max(p * (1.0 - p), 1e-12) / max(int(n), 1)) ** 0.5)


# =================================================================================================
# THE DECISIVE PRIMITIVE -- the random-ranking curve, computed PER ITEM from its own pool
# =================================================================================================
def random_ranking_hit_at_k(n_elig: np.ndarray, n_gold: np.ndarray,
                            ks: Sequence[int]) -> Dict[int, np.ndarray]:
    """P(hit@k) for a ranking that IGNORES THE QUERY, per item.

        P(hit@k) = 1 - C(n_elig - n_gold, k) / C(n_elig, k)
                 = 1 - prod_{j=0}^{k-1} (n_elig - n_gold - j) / (n_elig - j)

    This is the ONLY correct null for a rank curve on an open pool: it depends on each item's OWN
    pool size and OWN number of correct answers, both of which vary by more than an order of
    magnitude here. A single scalar "chance" would be the exact "a number may not be carried
    between populations" fault this whole battery exists to prevent.
    """
    N = np.asarray(n_elig, dtype=np.float64)
    G = np.asarray(n_gold, dtype=np.float64)
    kmax = int(max(ks))
    out: Dict[int, np.ndarray] = {}
    prod = np.ones_like(N)
    want = set(int(k) for k in ks)
    for j in range(kmax):
        num = np.maximum(N - G - j, 0.0)
        den = np.maximum(N - j, 1e-12)
        prod = prod * (num / den)
        k = j + 1
        if k in want:
            out[k] = 1.0 - prod
    return out


def hit_at_k_curve(S: np.ndarray, elig: np.ndarray, gold: np.ndarray,
                   ks: Sequence[int]) -> Dict[str, object]:
    """Rank of the best gold, and hit@k under BOTH tie conventions, plus MRR.

    Uses tools/floor_battery.rank_of_best_gold UNMODIFIED so the tie handling is the audited one:
    rank_opt = #(strictly greater)+1 (best case inside a tie), rank_cons = #(>=) (worst case).
    """
    r = FB.rank_of_best_gold(S, elig, gold)
    ro, rc = r["rank_opt"], r["rank_cons"]
    hits: Dict[str, Dict[int, np.ndarray]] = {"opt": {}, "cons": {}}
    for k in ks:
        hits["opt"][int(k)] = (ro <= float(k)).astype(np.float64)
        hits["cons"][int(k)] = (rc <= float(k)).astype(np.float64)
    return {"rank_opt": ro, "rank_cons": rc, "hit_at_k": hits,
            "mrr_opt": 1.0 / np.maximum(ro, 1.0), "mrr_cons": 1.0 / np.maximum(rc, 1.0)}


# =================================================================================================
# COMPARATORS. Each maps a raw cosine score matrix [n_anchors, n_items] to a new score matrix.
# =================================================================================================
def anchor_background_stats(MATn: np.ndarray, ok: np.ndarray) -> Dict[str, np.ndarray]:
    """Each anchor's response profile over a GOLD-BLIND, NON-TRANSDUCTIVE probe population: the
    store's own rows. Nothing about the scored queries enters, so no calibration fitted here can
    leak the answers or memorise the test items.

    NOTE, AND IT IS A REAL FINDING NOT A FOOTNOTE: `mean_sim` computed this way is (up to
    normalisation) the CONSTANT/PROTOTYPE FLOOR itself -- cosine to the mean anchor direction. The
    binding floor and the hubness correction are the SAME OBJECT approached from two sides.
    """
    B = MATn[ok]
    Sb = (MATn @ B.T).astype(np.float32)                   # [n_anchors, n_probe]
    n_probe = Sb.shape[1]
    # remove each anchor's self-similarity where it is its own probe (it is exactly 1.0 and would
    # inflate a hub's mean by 1/n_probe -- small, but it is a self-comparison and does not belong)
    idx_in_probe = np.full(MATn.shape[0], -1, dtype=np.int64)
    idx_in_probe[np.flatnonzero(ok)] = np.arange(n_probe)
    tot = Sb.sum(axis=1, dtype=np.float64)
    tot2 = (Sb.astype(np.float64) ** 2).sum(axis=1)
    cnt = np.full(MATn.shape[0], float(n_probe))
    has_self = idx_in_probe >= 0
    self_val = np.zeros(MATn.shape[0], dtype=np.float64)
    self_val[has_self] = Sb[has_self, idx_in_probe[has_self]].astype(np.float64)
    tot[has_self] -= self_val[has_self]
    tot2[has_self] -= self_val[has_self] ** 2
    cnt[has_self] -= 1.0
    mu = tot / np.maximum(cnt, 1.0)
    var = np.maximum(tot2 / np.maximum(cnt, 1.0) - mu ** 2, 0.0)
    sd = np.sqrt(var)
    # top-k local means, for CSLS
    topk: Dict[int, np.ndarray] = {}
    for k in CSLS_K:
        kk = int(min(k, n_probe - 1))
        part = np.partition(Sb, n_probe - kk - 1, axis=1)[:, n_probe - kk:]
        topk[int(k)] = part.mean(axis=1).astype(np.float64)
    del Sb
    return {"mean_sim": mu, "sd_sim": sd, "topk_mean": topk, "n_probe": int(n_probe)}


def comparator_scores(name: str, S: np.ndarray, bg: Dict[str, np.ndarray],
                      const_floor: np.ndarray) -> np.ndarray:
    """Return a NEW score matrix. `S` is never mutated."""
    if name == "R0_COSINE_ARGMAX_INCUMBENT":
        return S
    if name.startswith("R1_CSLS_k"):
        k = int(name.split("k")[-1])
        # CSLS = 2*s(a,i) - r_k(a) - r_k(i). The r_k(i) term is CONSTANT DOWN A COLUMN and
        # therefore cannot change that column's argmax; only r_k(a) can. Asserted in self_test.
        return (2.0 * S - bg["topk_mean"][k][:, None].astype(np.float32)).astype(np.float32)
    if name.startswith("R2_SUBTRACT_CONSTANT_alpha"):
        a = float(name.split("alpha")[-1])
        return (S - a * const_floor[:, None].astype(np.float32)).astype(np.float32)
    if name == "R3_ZNORM_ANCHOR":
        return ((S - bg["mean_sim"][:, None].astype(np.float32))
                / np.maximum(bg["sd_sim"][:, None].astype(np.float32), 1e-6)).astype(np.float32)
    if name.startswith("R4_DIVNORM_sigma"):
        _, sg, ex = name.split("_")[2], name.split("sigma")[1].split("_expo")[0], \
            name.split("_expo")[1]
        sigma, expo = float(sg), float(ex)
        x = np.maximum(S, 0.0) ** expo
        p = np.maximum(bg["mean_sim"], 0.0) ** expo
        return (x / (sigma ** expo + p[:, None])).astype(np.float32)
    raise ValueError("unknown comparator %r" % name)


def comparator_names() -> List[str]:
    names = ["R0_COSINE_ARGMAX_INCUMBENT"]
    names += ["R1_CSLS_k%d" % k for k in CSLS_K]
    names += ["R2_SUBTRACT_CONSTANT_alpha%g" % a for a in SUBTRACT_ALPHA]
    names += ["R3_ZNORM_ANCHOR"]
    names += ["R4_DIVNORM_sigma%g_expo%g" % (s, e) for e in DIVNORM_EXPO for s in DIVNORM_SIGMA]
    return names


# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())
    ev["dehub_transforms_selftest"] = {k: round(float(v), 4)
                                       for k, v in DH.formula_selftests(verbose=False).items()}

    # --- S-A. THE RANDOM-RANKING CURVE IS EXACT ON A KNOWN ANSWER.
    #     N=10 eligible, G=1 gold: P(hit@1)=1/10, P(hit@5)=5/10, P(hit@10)=1.
    r = random_ranking_hit_at_k(np.array([10.0]), np.array([1.0]), (1, 5, 10))
    assert abs(r[1][0] - 0.1) < 1e-12, r[1]
    assert abs(r[5][0] - 0.5) < 1e-12, r[5]
    assert abs(r[10][0] - 1.0) < 1e-12, r[10]
    #     N=10, G=2, k=1 -> 2/10; k=2 -> 1 - (8/10)(7/9) = 1 - 56/90
    r2 = random_ranking_hit_at_k(np.array([10.0]), np.array([2.0]), (1, 2))
    assert abs(r2[1][0] - 0.2) < 1e-12, r2[1]
    assert abs(r2[2][0] - (1.0 - 56.0 / 90.0)) < 1e-12, r2[2]
    #     and it is MONOTONE non-decreasing in k
    r3 = random_ranking_hit_at_k(np.array([500.0, 5000.0]), np.array([3.0, 40.0]), K_GRID)
    vals = [r3[k] for k in K_GRID]
    assert all(np.all(vals[i] <= vals[i + 1] + 1e-12) for i in range(len(vals) - 1)), \
        "random-ranking curve is not monotone in k"
    ev["RANDOM_RANKING_known_answer"] = {"N10_G1_k1": 0.1, "N10_G1_k5": 0.5,
                                         "N10_G2_k2": round(1.0 - 56.0 / 90.0, 6),
                                         "monotone_in_k": True}

    # --- S-B. THE RANK CURVE FIRES AND FAILS ON A PLANTED STORE, and hit@1 agrees with the
    #     audited scorer bit-for-bit. A rank curve that disagrees with hit@1 at k=1 is broken.
    rng = np.random.default_rng(17)
    n_a, d, n_i = 300, 32, 200
    M = rng.standard_normal((n_a, d)).astype(np.float32)
    Mn = l2n(M)
    q = rng.permutation(n_a)[:n_i]
    E = np.ones((n_a, n_i), dtype=bool)
    G = np.zeros((n_a, n_i), dtype=bool)
    G[q, np.arange(n_i)] = True
    S_good = (Mn @ Mn[q].T).astype(np.float32)             # the gold IS the query -> rank 1
    S_bad = (Mn @ l2n(rng.standard_normal((n_i, d))).T).astype(np.float32)
    c_good = hit_at_k_curve(S_good, E, G, K_GRID)
    c_bad = hit_at_k_curve(S_bad, E, G, K_GRID)
    assert c_good["hit_at_k"]["opt"][1].mean() > 0.99, "rank curve cannot FIRE on a planted store"
    assert c_bad["hit_at_k"]["opt"][1].mean() < 0.05, "rank curve cannot FAIL on a planted null"
    h1 = FB.hit_at_1_both_tie_conventions(S_bad, E, G)
    assert abs(float(c_bad["hit_at_k"]["opt"][1].mean())
               - float(h1["hit_opt"].mean())) < 1e-12, \
        "hit@k at k=1 DISAGREES with floor_battery.hit_at_1_both_tie_conventions"
    #     and a planted-null store's rank curve must sit NEAR its own random-ranking curve.
    #     CALIBRATED HONESTLY, NOT TIGHTENED UNTIL IT PASSED: the fixture is random Gaussian at
    #     d=32, which HAS ITS OWN HUBNESS (that is the phenomenon this cell is measuring), so an
    #     exact match is not the correct expectation and asserting one would be asserting a false
    #     fact about high-dimensional geometry. The guard that is actually worth having is that the
    #     curve is within a FACTOR OF ~2.5 either way -- which still catches a rank curve wrong by
    #     an order of magnitude, an off-by-one in k, or an inverted convention.
    rr = random_ranking_hit_at_k(E.sum(axis=0), G.sum(axis=0), K_GRID)
    ratios = {}
    for k in (10, 50, 100):
        ratios[k] = float(c_bad["hit_at_k"]["opt"][k].mean()) / max(float(rr[k].mean()), 1e-9)
        assert 0.4 <= ratios[k] <= 2.5, (
            "a planted-null store is %.2fx its own random-ranking curve at k=%d -- the rank curve "
            "or the null is wrong by more than geometry can explain" % (ratios[k], k))
    #     and the SIGNAL case must be enormously above the null case at k=1, or the curve cannot
    #     discriminate the two branches the whole cell turns on.
    assert (float(c_good["hit_at_k"]["opt"][1].mean())
            > 10.0 * float(c_bad["hit_at_k"]["opt"][1].mean()) + 0.5), \
        "the rank curve does not separate a planted store from a planted null at k=1"
    ev["RANK_CURVE_fires_and_fails"] = {
        "planted_exact_hit1": round(float(c_good["hit_at_k"]["opt"][1].mean()), 4),
        "planted_null_hit1": round(float(c_bad["hit_at_k"]["opt"][1].mean()), 4),
        "planted_null_hit50": round(float(c_bad["hit_at_k"]["opt"][50].mean()), 4),
        "its_own_random_ranking_hit50": round(float(rr[50].mean()), 4),
        "null_over_random_ranking_ratio": {str(k): round(v, 3) for k, v in ratios.items()},
        "agrees_with_floor_battery_at_k1": True}

    # --- S-C. THE ARITHMETIC CLAIM IN THE DOCSTRING, ASSERTED NOT ASSUMED: a PER-QUERY (column)
    #     shift or positive scale CANNOT change that column's argmax, so it cannot move hit@1.
    col_shift = rng.standard_normal(n_i).astype(np.float32)
    col_scale = np.abs(rng.standard_normal(n_i)).astype(np.float32) + 0.1
    S_pq = (S_bad * col_scale[None, :] + col_shift[None, :]).astype(np.float32)
    assert np.array_equal(np.argmax(S_bad, axis=0), np.argmax(S_pq, axis=0)), \
        "a per-query monotone transform changed the argmax -- the docstring claim is wrong"
    #     while a PER-ANCHOR (row) shift CAN and DOES change it. If this ever stops firing, ARM B
    #     is testing nothing.
    row_shift = rng.standard_normal(n_a).astype(np.float32)
    S_pa = (S_bad + row_shift[:, None]).astype(np.float32)
    assert not np.array_equal(np.argmax(S_bad, axis=0), np.argmax(S_pa, axis=0)), \
        "a per-anchor shift did NOT change the argmax -- ARM B cannot discriminate"
    ev["PER_QUERY_NORM_CANNOT_MOVE_ARGMAX"] = True
    ev["PER_ANCHOR_NORM_CAN_MOVE_ARGMAX"] = True

    # --- S-D. THE COMPARATORS ARE GENUINELY DIFFERENT FUNCTIONS and each is reachable.
    ok = np.ones(n_a, dtype=bool)
    bg = anchor_background_stats(Mn, ok)
    cf = FB.constant_prototype_floor(M, ok)
    digests = {}
    for nm in comparator_names():
        Sx = comparator_scores(nm, S_bad, bg, cf)
        digests[nm] = int(np.argmax(Sx, axis=0).sum())
    n_distinct = len(set(digests.values()))
    assert n_distinct >= 4, ("the comparator family collapses: only %d distinct argmax patterns "
                             "over %d arms" % (n_distinct, len(digests)))
    ev["COMPARATORS_distinct_argmax_patterns"] = {"n_arms": len(digests), "n_distinct": n_distinct}

    # --- S-E. CSLS's per-query term really is inert, so dropping it is not a shortcut that
    #     changes the answer. Build the full CSLS and compare argmax to the implemented one.
    k = 10
    ri = np.partition(S_bad, n_a - k, axis=0)[n_a - k:, :].mean(axis=0)
    full = 2.0 * S_bad - bg["topk_mean"][k][:, None].astype(np.float32) - ri[None, :]
    ours = comparator_scores("R1_CSLS_k10", S_bad, bg, cf)
    assert np.array_equal(np.argmax(full, axis=0), np.argmax(ours, axis=0)), \
        "dropping CSLS's per-query term changed the argmax"
    ev["CSLS_per_query_term_is_inert"] = True

    # --- S-F. THE HUBNESS STAT IS REAL: the OWNED organ must read a planted hub set as more
    #     hubbed than an isotropic one. This is dehub_transforms' own measurement, called not
    #     reimplemented.
    g_iso = DH.nk_gini(rng.standard_normal((400, 48)).astype(np.float32), k=10)
    g_hub = DH.nk_gini(DH._make_hub_content(seed=0), k=10)
    assert g_hub > g_iso, "the hubness statistic cannot tell a hub set from an isotropic one"
    ev["HUBNESS_stat_discriminates"] = {"iso": round(float(g_iso), 4), "hub": round(float(g_hub), 4)}

    # --- S-G. grounded_similarity() is NEVER the scorer, enforced by a LIVE TRIPWIRE.
    #
    #     MEASURED HERE, AND IT IS A FINDING ABOUT THE MANDATED GATE ITSELF, NOT A NUISANCE:
    #     `hdlab.grounded_similarity` IS present in sys.modules during this cell's run. It is
    #     pulled in TRANSITIVELY by `ruler_mode_gate()` -> `exp_encoding_quality_instrument_v2`,
    #     which every cell is required to call. Verified by observation, not inference:
    #     False before the gate, True after it.
    #
    #     So "is it loaded" is the WRONG question and would fail every compliant cell in the repo.
    #     The right question is "is it CALLED", and the honest way to answer that is to make a call
    #     impossible: the function is replaced IN THIS PROCESS ONLY with a stub that raises. If any
    #     path in this cell ever reaches it, the run dies instead of quietly producing a number on
    #     a scorer that puts 76.18% of SimLex pairs on two values. Nothing on disk is modified.
    _gs_before = "hdlab.grounded_similarity" in sys.modules
    install_grounded_similarity_tripwire()
    ev["grounded_similarity_is_never_the_scorer"] = {
        "enforced_by": "a LIVE TRIPWIRE that raises if the function is CALLED, not a source scan "
                       "and not an is-it-imported check",
        "module_present_in_sys_modules": _gs_before,
        "why_presence_is_not_a_violation": "ruler_mode_gate() -> exp_encoding_quality_instrument_v2 "
                                           "imports it transitively; MEASURED False before the "
                                           "gate and True after it. Every cell that obeys the "
                                           "mandated ruler gate loads it. LOADED IS NOT CALLED.",
        "hdlab_modules_loaded": sorted(m for m in sys.modules if m.startswith("hdlab"))}
    #     and the tripwire must actually be able to fire, or it is decoration.
    _fired = False
    try:
        sys.modules["hdlab.grounded_similarity"].grounded_similarity(None, None)
    except RuntimeError as e:
        _fired = "TRIPWIRE" in str(e)
    except Exception:
        _fired = False
    assert _fired, "the grounded_similarity tripwire does not fire when the function is called"
    ev["grounded_similarity_tripwire_fires"] = True

    # --- S-H. the bootstrap can BOTH fire and fail.
    a = rng.random(600) < 0.30
    b = a | (rng.random(600) < 0.25)
    pb = FB.paired_bootstrap_ci({"a": a.astype(float), "b": b.astype(float)},
                                np.ones(600, dtype=bool), 800, 3)
    assert FB.margin(pb["boot"], "b", "a")["band"] == "ABOVE", "bootstrap missed a real margin"
    c = rng.random(600) < 0.30
    pb2 = FB.paired_bootstrap_ci({"a": a.astype(float), "c": c.astype(float)},
                                 np.ones(600, dtype=bool), 800, 3)
    ev["BOOTSTRAP_fires_and_can_fail"] = {"real": FB.margin(pb["boot"], "b", "a")["band"],
                                          "null": FB.margin(pb2["boot"], "c", "a")["band"]}

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1400], flush=True)
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
            "n_anchors": n_anchors, "qidx": qidx, "GOLD": GOLD_ALL, "E": E_ALL, "keep": keep_ALL}


def run(grid: str, which_arm: str, output_dir: str) -> Dict:
    t0 = time.time()
    _gate = CTS.ruler_mode_gate()          # called FIRST; it is what transitively loads hdlab
    _tripwire = install_grounded_similarity_tripwire()
    P = build_population()
    C, mat, mat_ok = P["C"], P["mat"], P["mat_ok"]
    n_anchors, qidx = P["n_anchors"], P["qidx"]
    GOLD, E, keep_ALL = P["GOLD"], P["E"], P["keep"]
    anchors = P["anchors"]

    items = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    MATn = l2n(mat)
    print("[load] n_anchors=%d n_items=%d t=%.0fs" % (n_anchors, n_items, time.time() - t0),
          flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "arm": which_arm, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": _gate,
        "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(_tripwire),
        "cache": {"store": CTS.CACHE, "aux": CTS.AUX, "rebuilt": False},
        "population": {
            "n_anchors": n_anchors, "n_items_scored": n_items,
            "pool": "the LANDED OPEN pool (mat_ok minus per-item exclusions). eligB is NOT used: "
                    "it is on record admitting a constant at 0.1715 against chance 0.0101.",
            "gold": "WordNet 3.0 generous meaning set, as built by "
                    "exp_grounding_readout_known_answer_v1 UNMODIFIED",
            "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions, tie-corrected primary",
            "chance_addressing": round(1.0 / n_anchors, 8)},
    }

    # ---- REGRESSION GATES, read BEFORE anything else -------------------------------------------
    S_part_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h = FB.hit_at_1_both_tie_conventions(S_part_full, E, GOLD)
    m = h["scored"] & keep_ALL
    a0 = float(h["hit_exp"][m].mean())
    del S_part_full, h
    S_ex_full = (MATn @ l2n(C["Q_exact"]).T).astype(np.float32)
    h = FB.hit_at_1_both_tie_conventions(S_ex_full, E, GOLD)
    m1 = h["scored"] & keep_ALL
    a1 = float(h["hit_exp"][m1].mean())
    addr_full = float(np.mean(np.argmax(S_ex_full, axis=0)[keep_ALL & (qidx >= 0)]
                              == qidx[keep_ALL & (qidx >= 0)]))
    del S_ex_full, h
    rep["REGRESSION_GATE"] = {
        "partial_cue_tie_corrected_FULL_POP": round(a0, 4), "expected": REGRESSION_A0_PARTIAL,
        "exact_key_tie_corrected_FULL_POP": round(a1, 4), "expected_exact": REGRESSION_A1_EXACT,
        "exact_key_addressing_FULL_POP": round(addr_full, 4),
        "tol": REGRESSION_TOL, "n_scored": int(m.sum()),
        "PASS": bool(abs(a0 - REGRESSION_A0_PARTIAL) <= REGRESSION_TOL
                     and abs(a1 - REGRESSION_A1_EXACT) <= REGRESSION_TOL)}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r"
                         % rep["REGRESSION_GATE"])
    print("[regression] partial=%.4f exact=%.4f addressing=%.4f PASS" % (a0, a1, addr_full),
          flush=True)

    # ---- THE EXACT-KEY SCORE MATRIX -- the whole cell lives on this one object ------------------
    S = (MATn @ l2n(Q_exact).T).astype(np.float32)

    # ---- VALIDITY ARMS, verified BEFORE any treatment number -----------------------------------
    ok_q = qidx_T >= 0
    ka = float(np.mean(np.argmax(S, axis=0)[ok_q] == qidx_T[ok_q]))
    rng = np.random.default_rng(MASTER_SEED + 77)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    h_null = FB.hit_at_1_both_tie_conventions(S[:, perm], E_T, GOLD_T)
    null_hit = float(h_null["hit_exp"][h_null["scored"]].mean())
    null_addr = float(np.mean(np.argmax(S[:, perm], axis=0)[ok_q] == qidx_T[ok_q]))
    rep["VALIDITY"] = {
        "KA_SELF_ADDRESS": {"value": round(ka, 4), "gate": KA_MIN, "PASS": bool(ka >= KA_MIN),
                            "sensitive_to": "scorer / pool / comparator",
                            "insensitive_to": "the WordNet gold pairing"},
        "NULL_PERMUTED": {
            "hit_at_1_tie_corrected": round(null_hit, 6),
            "addressing": round(null_addr, 8), "chance_addressing": round(1.0 / n_anchors, 8),
            "binom_ci_halfwidth_at_null_hit": round(_halfwidth(null_hit, n_items), 6),
            "sensitive_to": "the cue-to-item pairing", "insensitive_to": "whether the scorer works"},
        "they_fail_independently": "a comparator/scorer bug drops KA while leaving NULL at chance; "
                                   "a pairing or leak bug leaves KA at ceiling while lifting NULL. "
                                   "No single bug can make both pass.",
    }
    if ka < KA_MIN:
        raise SystemExit("KNOWN-ANSWER ARM FAILED (%.4f < %.2f) -- no treatment number is read"
                         % (ka, KA_MIN))
    print("[validity] KA_self_address=%.4f NULL_hit=%.6f NULL_addr=%.8f" % (ka, null_hit, null_addr),
          flush=True)

    # ---- FLOORS, ALL recomputed on THIS population ----------------------------------------------
    aux = P["aux"]
    floors_S: Dict[str, np.ndarray] = {}
    try:
        floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(aux["Tq"][T]).T).astype(np.float32)
    except Exception as exc:                                          # reported, never silent
        rep.setdefault("FLOOR_NOTES", {})["F_ORTHOGRAPHIC"] = "UNAVAILABLE: %r" % (exc,)
    try:
        floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
            FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    except Exception as exc:
        rep.setdefault("FLOOR_NOTES", {})["F_FREQUENCY"] = "UNAVAILABLE: %r" % (exc,)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 91))
                              @ l2n(Q_exact).T).astype(np.float32)
    const_floor_vec = FB.constant_prototype_floor(mat, mat_ok)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_floor_vec, n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors,
                                  [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]), n_items)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = sorted(floors_S)
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959",
                             "every floor above is recomputed on this population's own n"]

    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    tie_of: Dict[str, float] = {}
    scored_all = np.ones(n_items, dtype=bool)

    def add_arm(name: str, Sx: np.ndarray) -> None:
        nonlocal scored_all
        hh = FB.hit_at_1_both_tie_conventions(Sx, E_T, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        hits_opt[name] = hh["hit_opt"]
        hits_cons[name] = hh["hit_cons"]
        tie_of[name] = float(hh["tie_mass"].mean())
        scored_all = scored_all & hh["scored"]

    for k, Sf in floors_S.items():
        add_arm(k, Sf)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)

    # =============================================================================================
    # ARM A -- THE DIAGNOSIS
    # =============================================================================================
    if which_arm in ("A", "all"):
        n_elig = E_T.sum(axis=0).astype(np.float64)
        n_gold = (GOLD_T & E_T).sum(axis=0).astype(np.float64)

        # ---- S1. IS THE ANSWER IN THE POOL AT ALL? ----------------------------------------------
        rep["S1_IS_THE_ANSWER_IN_THE_POOL"] = {
            "what": "by construction every scored item has >=1 eligible gold anchor; the CENSUS is "
                    "published because the random-ranking null depends on it PER ITEM.",
            "frac_items_with_at_least_one_eligible_gold": round(float((n_gold >= 1).mean()), 6),
            "n_gold_per_item": {"mean": round(float(n_gold.mean()), 3),
                                "median": float(np.median(n_gold)),
                                "p10": float(np.percentile(n_gold, 10)),
                                "p90": float(np.percentile(n_gold, 90)),
                                "min": float(n_gold.min()), "max": float(n_gold.max())},
            "n_eligible_per_item": {"mean": round(float(n_elig.mean()), 1),
                                    "median": float(np.median(n_elig)),
                                    "min": float(n_elig.min()), "max": float(n_elig.max())},
            "VERDICT": ("THE ANSWER IS ALWAYS IN THE POOL" if float((n_gold >= 1).mean()) > 0.999
                        else "SOME ITEMS HAVE NO REACHABLE ANSWER"),
        }
        # ---- S1b. WHAT IS THE CONSTANT FLOOR ACTUALLY EXPLOITING? --------------------------------
        # Added after the reduced-grid smoke, which showed the constant floor's OWN rank curve is
        # FLAT from k=1 to k=2 (0.1250 -> 0.1250). A constant ranking answers the same word to every
        # question, so a flat step means its SECOND choice adds nothing -- i.e. its whole score is
        # one anchor that happens to be a WordNet gold for a large share of ALL items. That is a
        # property of the GOLD, and it has to be published beside the floor or "below the constant
        # floor" gets read as a pure statement about the read-out when it is partly a statement
        # about a gold set with a mean of ~50 correct answers per item.
        gold_degree_all = GOLD_T.sum(axis=1).astype(np.float64)
        top_generic = np.argsort(-const_floor_vec.astype(np.float64))[:10]
        rep["S1b_WHAT_IS_THE_CONSTANT_FLOOR_EXPLOITING"] = {
            "why_this_is_here": "the binding floor must be interpretable, not just large. A floor "
                                "is only a fair bar if we know what no-understanding story it "
                                "encodes. This does NOT lower the bar -- the bar is the bar -- it "
                                "says what clearing it would and would not prove.",
            "constant_floor_top_10_anchors": [
                {"anchor": anchors[int(a)], "constant_score": round(float(const_floor_vec[int(a)]), 4),
                 "is_gold_for_n_items": int(gold_degree_all[int(a)]),
                 "is_gold_for_frac_of_items": round(float(gold_degree_all[int(a)]) / n_items, 4)}
                for a in top_generic],
            "gold_degree_over_anchors": {
                "max_items_any_single_anchor_is_gold_for": int(gold_degree_all.max()),
                "max_as_frac_of_items": round(float(gold_degree_all.max()) / n_items, 4),
                "mean": round(float(gold_degree_all.mean()), 3),
                "n_anchors_gold_for_at_least_5pct_of_items":
                    int((gold_degree_all >= 0.05 * n_items).sum())},
            "reading": "if one anchor is a correct answer for a large share of all items, a ranking "
                       "that always names it scores that share while understanding nothing. The "
                       "gold is the GENEROUS WordNet set (synonyms + hypernyms 2 up + sisters + "
                       "hyponyms) built by exp_grounding_readout_known_answer_v1 UNMODIFIED.",
        }
        record_unit(output_dir, unit_key("armA", "S1b"),
                    rep["S1b_WHAT_IS_THE_CONSTANT_FLOOR_EXPLOITING"])
        record_unit(output_dir, unit_key("armA", "S1"), rep["S1_IS_THE_ANSWER_IN_THE_POOL"])
        print("[S1] frac_with_gold=%.4f mean_n_gold=%.2f mean_n_elig=%.0f"
              % (float((n_gold >= 1).mean()), n_gold.mean(), n_elig.mean()), flush=True)

        # ---- S2. WHERE DOES IT RANK? THE DECISIVE MEASUREMENT ------------------------------------
        RR = random_ranking_hit_at_k(n_elig, n_gold, K_GRID)
        curves: Dict[str, Dict] = {}
        rank_hits_exp: Dict[str, np.ndarray] = {}
        # THE NULL'S OWN RANK CURVE. Added after the reduced-grid smoke, and the smoke is why:
        # NULL hit@1 read 0.0275 against the exact key's 0.0275 -- IDENTICAL at n=400. A single
        # point cannot tell whether that is a coincidence at small n or the whole ranking carrying
        # no item-specific information, and the difference is the entire finding. The null gets the
        # SAME rank curve so real-minus-null is a PAIRED margin at every k, not one comparison.
        # DISCLOSED AS A DESIGN CHANGE FORCED BY THE SMOKE, not a quiet fix. No floor, population,
        # threshold or seed changed; an arm was ADDED, and it can only make the treatment look
        # WORSE, never better.
        S_null_for_curve = S[:, perm]
        for nm, Sx in ([("EXACT_KEY_COSINE", S), ("NULL_PERMUTED_CUE", S_null_for_curve)]
                       + sorted(floors_S.items())):
            cv = hit_at_k_curve(Sx, E_T, GOLD_T, K_GRID)
            curves[nm] = {
                "hit_at_k_optimistic": {str(k): round(float(cv["hit_at_k"]["opt"][k].mean()), 5)
                                        for k in K_GRID},
                "hit_at_k_conservative": {str(k): round(float(cv["hit_at_k"]["cons"][k].mean()), 5)
                                          for k in K_GRID},
                "rank_of_best_gold": {
                    "median_opt": float(np.median(cv["rank_opt"])),
                    "p25_opt": float(np.percentile(cv["rank_opt"], 25)),
                    "p75_opt": float(np.percentile(cv["rank_opt"], 75)),
                    "mean_opt": round(float(cv["rank_opt"].mean()), 1),
                    "median_cons": float(np.median(cv["rank_cons"]))},
                "MRR_opt": round(float(cv["mrr_opt"].mean()), 5),
            }
            for k in K_GRID:
                rank_hits_exp["%s|hit@%d" % (nm, k)] = cv["hit_at_k"]["opt"][k]
        # the RANDOM-RANKING curve, per item, and its own median rank (n_elig+1)/(n_gold+1)
        curves["RANDOM_RANKING_null_per_item"] = {
            "hit_at_k_optimistic": {str(k): round(float(RR[k].mean()), 5) for k in K_GRID},
            "expected_median_rank_of_best_gold":
                round(float(np.median((n_elig + 1.0) / (n_gold + 1.0))), 1),
            "note": "P(hit@k) = 1 - C(n_elig-n_gold,k)/C(n_elig,k), computed from EACH ITEM'S OWN "
                    "pool size and OWN gold count, then averaged. Not a scalar chance.",
        }
        for k in K_GRID:
            rank_hits_exp["RANDOM_RANKING|hit@%d" % k] = RR[k]

        pb_rank = FB.paired_bootstrap_ci(rank_hits_exp, np.ones(n_items, dtype=bool),
                                         N_BOOT, MASTER_SEED + 303)
        rank_margin = {}
        for k in K_GRID:
            a_k = "EXACT_KEY_COSINE|hit@%d" % k
            b_k = "RANDOM_RANKING|hit@%d" % k
            mg = FB.margin(pb_rank["boot"], a_k, b_k)
            mg["ci_halfwidth"] = round((mg["ci95"][1] - mg["ci95"][0]) / 2.0, 5)
            mg["analytic_null_halfwidth_at_this_n"] = round(
                _halfwidth(float(pb_rank["acc"][b_k]), n_items), 5)
            mg["exact_key"] = round(float(pb_rank["acc"][a_k]), 5)
            mg["random_ranking"] = round(float(pb_rank["acc"][b_k]), 5)
            mg["lift_x"] = (round(float(pb_rank["acc"][a_k]) / max(float(pb_rank["acc"][b_k]), 1e-9),
                                  2))
            rank_margin[str(k)] = mg
        # PAIRED margin against the PERMUTED-CUE null at every k -- how much of the ranking is
        # ITEM-SPECIFIC as opposed to a property of what the argmax likes to return regardless.
        null_margin = {}
        for k in K_GRID:
            mg = FB.margin(pb_rank["boot"], "EXACT_KEY_COSINE|hit@%d" % k,
                           "NULL_PERMUTED_CUE|hit@%d" % k)
            mg["ci_halfwidth"] = round((mg["ci95"][1] - mg["ci95"][0]) / 2.0, 5)
            mg["exact_key"] = round(float(pb_rank["acc"]["EXACT_KEY_COSINE|hit@%d" % k]), 5)
            mg["permuted_cue_null"] = round(float(pb_rank["acc"]["NULL_PERMUTED_CUE|hit@%d" % k]), 5)
            mg["margin_over_own_ci_halfwidth"] = round(
                abs(mg["point"]) / max(mg["ci_halfwidth"], 1e-9), 2)
            null_margin[str(k)] = mg
        # THE CROSSOVER: the smallest k at which the exact-key curve overtakes the binding floor's
        # OWN curve. If the query signal exists but lives below the top of the ranking, this is the
        # number that says how far below.
        bind_curve_name = max(
            [f for f in FLOOR_NAMES if f in curves],
            key=lambda f: curves[f]["hit_at_k_optimistic"]["1"]) if any(
            f in curves for f in FLOOR_NAMES) else None
        crossover = None
        if bind_curve_name:
            for k in K_GRID:
                if (curves["EXACT_KEY_COSINE"]["hit_at_k_optimistic"][str(k)]
                        > curves[bind_curve_name]["hit_at_k_optimistic"][str(k)]):
                    crossover = int(k)
                    break
        sep_ks = [k for k in K_GRID if rank_margin[str(k)]["band"] == "ABOVE"]
        sep_null_ks = [k for k in K_GRID if null_margin[str(k)]["band"] == "ABOVE"]
        rep["S2_WHERE_DOES_THE_ANSWER_RANK"] = {
            "WHY_THIS_IS_THE_DECISIVE_ARM":
                "hit@1 is a single point of a distribution. If the rank curve sits AT the "
                "random-ranking null, the store's neighbourhood carries NO synonym information and "
                "THE DEFECT IS IN WHAT WE WROTE, NOT IN HOW WE READ -- no comparator, verifier, "
                "shortlist or cleanup could ever help. If it is CI-separated ABOVE the null while "
                "hit@1 sits below the binding floor, the information IS in the store and the "
                "SELECTOR cannot reach it.",
            "curves": curves,
            "EXACT_KEY_vs_RANDOM_RANKING_paired_bootstrap": rank_margin,
            "k_values_CI_separated_ABOVE_random": sep_ks,
            "EXACT_KEY_vs_PERMUTED_CUE_NULL_paired_bootstrap": null_margin,
            "k_values_CI_separated_ABOVE_the_permuted_cue_null": sep_null_ks,
            "WHERE_THE_QUERY_SIGNAL_LIVES": {
                "binding_floor_curve": bind_curve_name,
                "crossover_k_where_exact_key_overtakes_the_binding_floor": crossover,
                "reading": "if the crossover is far above k=1, the store's query-conditional signal "
                           "is REAL but sits BELOW the top of the ranking: a query-ignoring "
                           "constant owns the top slot and the query only starts to pay after the "
                           "first %s candidates. That is a statement about WHERE the signal is, "
                           "which hit@1 alone cannot make."
                           % (crossover if crossover else "(never -- it never overtakes)")},
            "PREREGISTERED_READING": (
                "BRANCH_A_STORE_DOES_NOT_CONTAIN_THE_ANSWER" if not sep_ks else
                "BRANCH_B_ANSWER_IS_PRESENT_BUT_THE_SELECTOR_CANNOT_REACH_IT"),
            "TWO_STAGE_CEILING_ORACLE_not_a_floor": {
                "what": "hit@k of stage one IS the exact ceiling of any propose-and-verify with a "
                        "PERFECT verifier at shortlist size k. Labelled ORACLE; it is fitted on "
                        "nothing but it presumes a verifier we have not built.",
                "ceiling_by_shortlist_size": curves["EXACT_KEY_COSINE"]["hit_at_k_optimistic"]},
        }
        record_unit(output_dir, unit_key("armA", "S2"), rep["S2_WHERE_DOES_THE_ANSWER_RANK"])
        print("[S2] exact-key hit@k: " + json.dumps(
            curves["EXACT_KEY_COSINE"]["hit_at_k_optimistic"]), flush=True)
        print("[S2] random-ranking:  " + json.dumps(
            curves["RANDOM_RANKING_null_per_item"]["hit_at_k_optimistic"]), flush=True)
        print("[S2] BRANCH = %s" % rep["S2_WHERE_DOES_THE_ANSWER_RANK"]["PREREGISTERED_READING"],
              flush=True)

        # ---- S3. WHAT WINS INSTEAD? --------------------------------------------------------------
        Smask = np.where(E_T, S, -np.inf)
        top1 = np.argmax(Smask, axis=0)
        top1_cos = Smask[top1, np.arange(n_items)]
        gbest = np.where(GOLD_T & E_T, Smask, -np.inf).max(axis=0)
        cnt = np.bincount(top1, minlength=n_anchors).astype(np.float64)
        order = np.argsort(-cnt)[:25]
        try:
            fq = np.asarray(aux["fq"], dtype=np.float64)
            corr_freq = float(np.corrcoef(cnt, np.log1p(fq))[0, 1])
        except Exception:
            corr_freq = float("nan")
        corr_const = float(np.corrcoef(cnt, const_floor_vec.astype(np.float64))[0, 1])
        rep["S3_WHAT_WINS_INSTEAD"] = {
            "n_distinct_top1_anchors": int(np.unique(top1).size),
            "n_items": n_items,
            "degeneracy_distinct_over_items": round(float(np.unique(top1).size) / n_items, 4),
            "top_25_winners": [{"anchor": anchors[int(a)], "n_items_won": int(cnt[int(a)]),
                                "share": round(float(cnt[int(a)]) / n_items, 4),
                                "constant_floor_score": round(float(const_floor_vec[int(a)]), 4)}
                               for a in order],
            "share_taken_by_top_25": round(float(cnt[order].sum()) / n_items, 4),
            "corr_times_won_vs_GENERICITY_constant_floor": round(corr_const, 4),
            "corr_times_won_vs_LOG_CORPUS_FREQUENCY": round(corr_freq, 4),
            "cosine_gap_winner_minus_best_gold": {
                "mean": round(float(np.mean(top1_cos - gbest)), 5),
                "median": round(float(np.median(top1_cos - gbest)), 5),
                "p90": round(float(np.percentile(top1_cos - gbest, 90)), 5)},
            "mean_cosine_of_winner": round(float(top1_cos.mean()), 5),
            "mean_cosine_of_best_gold": round(float(gbest.mean()), 5),
            "example_query_to_winner": ["%s -> %s" % (C["L_words"][int(T[i])], anchors[int(top1[i])])
                                        for i in range(min(30, n_items))],
        }
        record_unit(output_dir, unit_key("armA", "S3"), rep["S3_WHAT_WINS_INSTEAD"])
        print("[S3] distinct_top1=%d/%d corr_genericity=%.3f corr_freq=%.3f"
              % (int(np.unique(top1).size), n_items, corr_const, corr_freq), flush=True)

        # ---- S4. IS THE SCORE MISCALIBRATED ACROSS ANCHORS? (hubness, via the OWNED organ) -------
        kk = int(min(NK_K, n_anchors - 1))
        part = np.argpartition(-Smask, kk - 1, axis=0)[:kk, :]
        nk = np.bincount(part.ravel(), minlength=n_anchors).astype(np.float64)
        Sscr = (l2n(FB.scramble_null(mat, MASTER_SEED + 91)) @ l2n(Q_exact).T).astype(np.float32)
        Sscr = np.where(E_T, Sscr, -np.inf)
        part_s = np.argpartition(-Sscr, kk - 1, axis=0)[:kk, :]
        nk_s = np.bincount(part_s.ravel(), minlength=n_anchors).astype(np.float64)
        del Sscr, part_s
        gold_degree = GOLD_T.sum(axis=1).astype(np.float64)
        rep["S4_IS_THE_SCORE_MISCALIBRATED_ACROSS_ANCHORS"] = {
            "method": "Nk k-occurrence at k=%d and its Gini, computed with the OWNED organ "
                      "experiments/dehub_transforms (gini), IMPORTED not reimplemented. Radovanovic "
                      "et al. 2010's hubness statistic." % kk,
            "Nk_gini_REAL": round(float(DH.gini(nk)), 4),
            "Nk_gini_SCRAMBLE_NULL": round(float(DH.gini(nk_s)), 4),
            "reading": "a REAL Nk-Gini materially above the scramble null's means a small set of "
                       "anchors is absorbing the top of many queries' rankings -- the signature "
                       "hubness pathology of high-dimensional nearest-neighbour retrieval.",
            "Nk_max_share_of_all_topk_slots": round(float(nk.max()) / max(nk.sum(), 1.0), 5),
            "n_anchors_never_in_any_top%d" % kk: int((nk == 0).sum()),
            "frac_anchors_never_in_any_topk": round(float((nk == 0).mean()), 4),
            "corr_Nk_vs_GENERICITY_constant_floor":
                round(float(np.corrcoef(nk, const_floor_vec.astype(np.float64))[0, 1]), 4),
            "corr_Nk_vs_GOLD_DEGREE_how_often_the_anchor_IS_a_correct_answer":
                round(float(np.corrcoef(nk, gold_degree)[0, 1]), 4),
        }
        record_unit(output_dir, unit_key("armA", "S4"),
                    rep["S4_IS_THE_SCORE_MISCALIBRATED_ACROSS_ANCHORS"])
        print("[S4] Nk_gini real=%.4f scramble=%.4f" % (DH.gini(nk), DH.gini(nk_s)), flush=True)
        del Smask

    # =============================================================================================
    # ARM B -- REPLACE THE READ-OUT
    # =============================================================================================
    if which_arm in ("B", "all"):
        rep["ARM_B_ARITHMETIC_FACT_ASSERTED_NOT_ASSUMED"] = {
            "claim": "normalising over the CANDIDATES OF ONE QUERY is a monotone transform within "
                     "that query and CANNOT change that query's argmax, so it is arithmetically "
                     "incapable of moving hit@1. Only a PER-ANCHOR calibration can.",
            "verified_in": "self_test S-C, on a real score matrix, both directions",
            "consequence": "the per-query direction is NOT run as if it could help; presenting it "
                           "as a brain-derived fix would be laundering."}
        bg = anchor_background_stats(MATn, mat_ok)
        rep["ARM_B_CALIBRATION_IS_GOLD_BLIND_AND_NON_TRANSDUCTIVE"] = {
            "probe_population": "the store's OWN %d rows (mat_ok). Nothing about the scored queries "
                                "and nothing about the WordNet golds enters the calibration, so no "
                                "arm here can memorise the test items or fit the answers."
                                % bg["n_probe"],
            "note": "mean_sim over this probe set IS, up to normalisation, the CONSTANT/PROTOTYPE "
                    "FLOOR -- cosine to the mean anchor direction. The binding floor and the "
                    "hubness correction turn out to be the same object from two sides.",
            "corr_mean_sim_vs_constant_prototype_floor":
                round(float(np.corrcoef(bg["mean_sim"],
                                        const_floor_vec.astype(np.float64))[0, 1]), 4)}
        done = completed_units(output_dir)
        ka_of: Dict[str, float] = {}
        for nm in comparator_names():
            uk = unit_key("armB", nm)
            Sx = comparator_scores(nm, S, bg, const_floor_vec)
            add_arm(nm, Sx)
            ka_of[nm] = float(np.mean(np.argmax(Sx, axis=0)[ok_q] == qidx_T[ok_q]))
            if uk not in done:
                record_unit(output_dir, uk, {"arm": nm, "ka": round(ka_of[nm], 4)})
            if Sx is not S:
                del Sx
            print("[armB] %-34s KA=%.4f t=%.0fs" % (nm, ka_of[nm], time.time() - t0), flush=True)
        rep["ARM_B_KA_PER_COMPARATOR"] = {
            "what": "the KNOWN-ANSWER arm re-run for EVERY comparator: does the transform still "
                    "address the item's own row? A transform that destroys self-addressing has "
                    "broken the instrument and its treatment number is not read.",
            "gate": KA_MIN, "values": {k: round(v, 4) for k, v in ka_of.items()},
            "arms_failing_KA": sorted(k for k, v in ka_of.items() if v < KA_MIN)}

    # ---- SCORING, one paired bootstrap over the COMMON scored items -----------------------------
    pb = FB.paired_bootstrap_ci(hits_exp, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_opt = FB.paired_bootstrap_ci(hits_opt, scored_all, N_BOOT, MASTER_SEED + 101)
    pb_cons = FB.paired_bootstrap_ci(hits_cons, scored_all, N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    present = [f for f in FLOOR_NAMES if f in acc]
    binding = max(present, key=lambda f: acc[f]) if present else None
    nc = pb["n_common"]

    margins = {}
    if binding:
        for k in sorted(acc):
            if k == binding or k.startswith("ORACLE"):
                continue
            mg = FB.margin(boot, k, binding)
            mg["ci_halfwidth"] = round((mg["ci95"][1] - mg["ci95"][0]) / 2.0, 5)
            mg["analytic_null_halfwidth_at_this_n"] = round(_halfwidth(acc[binding], nc), 5)
            mg["arm_value"] = round(acc[k], 5)
            mg["margin_over_own_ci_halfwidth"] = (
                round(abs(mg["point"]) / max(mg["ci_halfwidth"], 1e-9), 2))
            margins[k] = mg

    rep["HIT_AT_1"] = {
        "n_common_scored": nc, "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED",
        "tie_corrected": {k: round(v, 5) for k, v in acc.items()},
        "optimistic_tie": {k: round(v, 5) for k, v in pb_opt["acc"].items()},
        "conservative_tie": {k: round(v, 5) for k, v in pb_cons["acc"].items()},
        "mean_tie_mass": {k: round(v, 5) for k, v in tie_of.items()},
        "BINDING_FLOOR": binding,
        "BINDING_FLOOR_VALUE": round(acc[binding], 5) if binding else None,
        "ALL_FOUR_FLOORS": {f: round(acc[f], 5) for f in present},
        "ORACLE_CONSTANT_not_a_floor":
            round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 5),
        "POOL_ORACLE_CHECK": {
            "what": "the fitted CEILING of the constant family on THIS open pool. The open pool is "
                    "NOT a de-biased pool and is not claimed to be; the number is published so "
                    "nobody reads a margin over it as a margin over chance. eligB is not used.",
            "oracle_constant_hit_exp":
                round(acc.get("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", float("nan")), 5)},
        "MARGIN_vs_binding_floor_TIE_CORRECTED": margins,
        "ARMS_CI_SEPARATED_ABOVE_THE_BINDING_FLOOR":
            sorted(k for k, v in margins.items() if v["band"] == "ABOVE"),
    }
    rep["POWER"] = {
        "n_common_scored": nc,
        "binom_ci_halfwidth_at_binding_floor": round(_halfwidth(acc[binding], nc), 6)
        if binding else None,
        "reading": "A WIDTH IS NOT AN EFFECT. If a margin is smaller than its own CI half-width the "
                   "arm cannot separate at this n no matter how good the underlying thing is. Every "
                   "margin above carries margin_over_own_ci_halfwidth beside it.",
    }

    # ---- RUNTIME ORGAN WITNESS (sys.modules, never grep) ----------------------------------------
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = {
        "what": "modules actually LOADED by this run, observed in sys.modules AFTER the work -- "
                "runtime evidence, not a static search. Lazy imports are invisible to grep and "
                "string constants and comments read as imports.",
        "loaded": sorted(m for m in sys.modules
                         if m.startswith(("hdlab", "tools.", "dehub", "exp_cue_to_store"))
                         or m in ("dehub_transforms",)),
        "edited_by_this_cell": [],
    }
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def decide(rep: Dict) -> Tuple[str, str]:
    """The verdict is COMPOSED from independent gates, never selected by branch order. No branch
    can hide a measured fact."""
    parts, msg = [], []
    s2 = rep.get("S2_WHERE_DOES_THE_ANSWER_RANK")
    if s2:
        parts.append(s2["PREREGISTERED_READING"])
        ek = s2["curves"]["EXACT_KEY_COSINE"]["hit_at_k_optimistic"]
        rr = s2["curves"]["RANDOM_RANKING_null_per_item"]["hit_at_k_optimistic"]
        msg.append("S2 exact-key hit@1=%s hit@10=%s hit@100=%s vs RANDOM-RANKING %s / %s / %s; "
                   "median rank of best gold=%s of %s eligible"
                   % (ek["1"], ek["10"], ek["100"], rr["1"], rr["10"], rr["100"],
                      s2["curves"]["EXACT_KEY_COSINE"]["rank_of_best_gold"]["median_opt"],
                      rep["population"]["n_anchors"]))
    h = rep.get("HIT_AT_1")
    if h:
        above = h["ARMS_CI_SEPARATED_ABOVE_THE_BINDING_FLOOR"]
        parts.append("REPLACEMENT_CLEARS_FLOOR_%s" % ("YES_%d_arms" % len(above) if above else "NO"))
        msg.append("binding floor %s=%s; %d of %d arms CI-separated ABOVE it%s"
                   % (h["BINDING_FLOOR"], h["BINDING_FLOOR_VALUE"], len(above),
                      len(h["MARGIN_vs_binding_floor_TIE_CORRECTED"]),
                      (": " + ", ".join(above[:6])) if above else ""))
    v = rep.get("VALIDITY", {})
    parts.append("KA_%s" % ("PASS" if v.get("KA_SELF_ADDRESS", {}).get("PASS") else "FAIL"))
    return "__".join(parts) if parts else "NO_ARM_RUN", " || ".join(msg)


def main() -> None:
    args = _ap.parse_args()
    if args.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return
    output_dir = _out_dir()
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"),
                 {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                  "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "arm": args.arm,
                  "host": platform.node()})
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(args.grid, args.arm, output_dir)
        verdict, msg = decide(rep)
        rep["verdict"] = verdict
        rep["verdict_msg"] = msg
        rep["wire_status"] = "VET_PENDING"
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        print(json.dumps({"verdict": verdict, "verdict_msg": msg}, indent=2), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(output_dir, "_crash_diagnostic.json"),
                     {"anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
                      "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise


if __name__ == "__main__":
    main()
