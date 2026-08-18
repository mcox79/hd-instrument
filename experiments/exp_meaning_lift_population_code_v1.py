"""exp_meaning_lift_population_code_v1 -- PHASE 1 item 3: fix the meaning LIFT.

Pre-reg: preregs/exp_meaning_lift_population_code_v1.md (thresholds fixed BEFORE any run).

THE TARGET. Our grounded norms (Lancaster sensorimotor JOIN Brysbaert concreteness, 12 z-scored
dims) read DIRECTLY score SimLex rho = 0.2701 on the instrument's 322 like-for-like pairs. Lifted
into our d-dim bipolar codes by SimHash they score ~0.1970. We destroy roughly a quarter of the
meaning we already have, in our own plumbing, before anything else happens. This cell asks which
brain-motivated lift gets it back, and whether the winner also survives superposition.

THE RULER IS NOT TOUCHED. experiments/exp_encoding_quality_instrument_v2 (542e1fc0d, 21/21 gates,
INSTRUMENT_VALIDATED) is IMPORTED UNMODIFIED and supplies the vocabulary, the golds, the sigma
grid, the seeds, K_DISTRACT, BUNDLE_B, AP_PROBES, N_GATE and every measurement function. This cell
adds ARMS.

THE DIVERGENCE BEING TESTED (prereg section 2). SimHash is `sign(X @ P)`. The random projection
(a) is brain-compatible -- it is the fly's PN -> Kenyon-cell random expansion. The `sign` (b) is
NOT: firing rates are non-negative and graded, so a per-channel +-1 is not a rate at all, and no
structure we could enumerate replaces a graded feature with a per-channel sign. (b) is the build
target. Self-test #3 proves the discard directly: sign(2X) == sign(X) bit-for-bit, so SimHash is
blind to every magnitude; the graded candidates are not.

CANDIDATES, each named against a structure (prereg section 3):
  C1_KCAP_*   Drosophila mushroom-body Kenyon cells + APL global inhibition; cerebellar granule
              layer. Random expansion THEN a global k-cap. FlyHash (Dasgupta, Stevens & Navlakha,
              Science 2017). Binary and GRADED-survivor variants, and a homeostatic-boost variant.
  C2_TUNING_* V1 orientation columns / MEC grid cells: overlapping graded gaussian tuning curves,
              m per norm dimension.
  C3_*        the graded rate code itself plus divisive normalisation (Carandini & Heeger 2012):
              magnitude-preserving expansion, with an exact-isometry variant, a plain-gaussian
              variant, and a retinal ON/OFF rectified-pair variant (rates cannot be negative).
  C4_PHASOR   theta phase coding (O'Keefe & Recce 1993) via our own FHRR-shaped code. Phase coding
              is pinned for POSITION; phase-coding a semantic magnitude is OUR INVENTION.

CREDIT. The mechanism inventory C1 implements is prior work in this repo:
notes/research_drill_brain_5x_angle2_rank_preserving_sparsification_kwta_2026-07-04.md (M1 graded
survivors, M2 global adaptive threshold, M3 expand-then-WTA = LSH, M4 homeostatic boosting), and
preregs/encoder_phase_traversal_graded_sparse_rescue_v1.md swept gradedness on a different task.
Neither measured the norms -> code lift. Prior-work check is recorded in the pre-reg section 0.

TWO AXES REPORTED SEPARATELY AND NEVER AVERAGED. A random encoding is near-optimal on IDENTITY and
at chance on STRUCTURE; a single scalar mixing them is unfalsifiable.

ASCII-only. CPU/numpy. No network. data/foundation/** is never opened. No external LLM anywhere.
GloVe/word2vec/fastText are NOT arms and are not a candidate meaning source.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# THE RULER, imported unmodified.
from experiments import exp_encoding_quality_instrument_v2 as INS
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units
# REUSED, NOT REIMPLEMENTED (WIRE DON'T ISLAND): the production sign convention, so the incumbent
# arm is bit-identical to what the substrate actually ships.
from hdlab.hub_spoke_word import bipolar_quantize
from hdlab import grounded_similarity as GS

ANCHOR_NAME = "meaning_lift_population_code_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = INS.RUN_MODE          # resolved by the ruler from the SAME argv/env
SMOKE = INS.SMOKE

# ---- everything below comes FROM THE RULER; this cell fixes no ruler constant of its own -------
V = INS.V
D_SWEEP = list(INS.D_SWEEP)
SEEDS = list(INS.SEEDS)
SIGMAS = list(INS.SIGMAS)
N_SWEEP = list(INS.N_SWEEP)
N_GATE = INS.N_GATE
BUNDLE_B = INS.BUNDLE_B
K_DISTRACT = INS.K_DISTRACT
AP_PROBES = INS.AP_PROBES
SIGMA_GATE = INS.SIGMA_GATE
HEADLINE_SIGMA = INS.HEADLINE_SIGMA
CORPUS_BYTES = INS.CORPUS_BYTES

# ---- this cell's OWN statistical parameters (precision, not thresholds) ------------------------
N_PERM = 200 if SMOKE else 2000
N_BOOT = 1000 if SMOKE else 10000
BOOT_SEED = 20260816
PERM_P = 95.0

# ---- pre-registered thresholds. FROZEN. Do not edit after a run. -------------------------------
# RG1 tolerance is 5e-3, not 1e-3: Spearman is a RANK statistic on 322 values whose typical gap is
# ~0.006, so a float32-vs-float64 rounding difference of 1e-7 can swap one near-tied pair and move
# rho by ~1/322 = 0.003. A tighter tolerance would make a reproduction gate fail on arithmetic
# noise rather than on a real disagreement. The ISOMETRY claim is gated tightly instead, on the
# per-pair COSINES (KA2), where no rank statistic intervenes.
T_RG1_CEIL_TOL = 5e-3            # CEIL_NORMS12_DIRECT reproduces the landed 0.2701
LANDED_CEIL_RHO = 0.2701227920100438
LANDED_INC_RHO_D256 = 0.19774431011854252   # REPORTED, NOT GATED
T_KA1_PLANTED_RHO_MIN = 0.50
T_KA2_ISOMETRY_TOL = 1e-5        # on the per-pair COSINES, float32 codes
T_KA3_SPEARMAN_TOL = 1e-9
T_NU_ABS_RHO_MAX = 0.10
T_G0_CLOSURE_MIN = 0.50
T_G3_BUNDLE_BITS_MIN = 0.5       # of the log2(N_GATE/B) = 7.000-bit ceiling (parent criterion)

# ---- candidate hyper-parameters (OURS, swept; see prereg section 3) ----------------------------
KCAP_FRACS = (0.02, 0.05, 0.10)
KCAP_MAIN_FRAC = 0.05
TUNING_WIDTHS = (1.0, 0.5)

REF_ARMS = [
    "CEIL_NORMS12_DIRECT",
    "INC_SIMHASH",
    "FLOOR_ORTHOGRAPHIC",
    "NULL_RANDOM_IID",
    "KA_PLANTED_SEMANTIC",
]
CAND_ARMS = [
    "C1_KCAP_BIN_f002",
    "C1_KCAP_BIN_f005",
    "C1_KCAP_BIN_f010",
    "C1_KCAP_GRD_f005",
    "C1_KCAP_GRD_f005_BOOST",
    "C2_TUNING_w1.0",
    "C2_TUNING_w0.5",
    "C3_ORTHONORMAL",
    "C3_GAUSSPROJ",
    "C3_ONOFF",
    "C4_PHASOR",
]
NULL_SCRAM_ARMS = [
    "NULL_SCRAM_SIMHASH",
    "NULL_SCRAM_KCAP_GRD",
    "NULL_SCRAM_TUNING",
    "NULL_SCRAM_ORTHONORMAL",
    "NULL_SCRAM_ONOFF",
    "NULL_SCRAM_PHASOR",
]
ARMS = REF_ARMS + CAND_ARMS + NULL_SCRAM_ARMS
# The NULL_SCRAM arms exist to prove an operator manufactures nothing from permuted content; they
# need the STRUCTURE readout only. Everything else gets the ruler's full battery.
FULL_BATTERY = set(REF_ARMS + CAND_ARMS)

FREQ_CHANNELS = ("FREQ_NEG_ABS_DIFF", "FREQ_SUM", "FREQ_MIN", "FREQ_MIN_OVER_MAX")


# ==================================================================================================
# batched Spearman -- the ONLY new statistical machinery. Asserted EQUAL to INS._spearman (KA3).
# ==================================================================================================
def _avg_ranks(X: np.ndarray) -> np.ndarray:
    """Row-wise average ranks with proper tie handling, vectorised over rows.

    Ties matter: a bootstrap resample draws the same pair repeatedly, so tied values are the norm
    here, not an edge case. Verified bit-equal to INS._spearman's scalar rank routine in
    self-test #1 on data constructed to be heavily tied.
    """
    X = np.asarray(X, dtype=np.float64)
    if X.ndim == 1:
        X = X[None, :]
    b, n = X.shape
    order = np.argsort(X, axis=1, kind="stable")
    Xs = np.take_along_axis(X, order, axis=1)
    newg = np.empty((b, n), dtype=bool)
    newg[:, 0] = True
    if n > 1:
        newg[:, 1:] = Xs[:, 1:] != Xs[:, :-1]
    idx = np.broadcast_to(np.arange(n, dtype=np.float64), (b, n))
    first = np.maximum.accumulate(np.where(newg, idx, -1.0), axis=1)
    endg = np.empty((b, n), dtype=bool)
    endg[:, -1] = True
    if n > 1:
        endg[:, :-1] = newg[:, 1:]
    last_rev = np.minimum.accumulate(np.where(endg, idx, float(n))[:, ::-1], axis=1)[:, ::-1]
    avg = 0.5 * (first + last_rev)
    out = np.empty((b, n), dtype=np.float64)
    np.put_along_axis(out, order, avg, axis=1)
    return out


def _pearson_rows(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    num = np.einsum("ij,ij->i", A, B)
    den = np.sqrt(np.einsum("ij,ij->i", A, A) * np.einsum("ij,ij->i", B, B))
    out = np.full(len(num), np.nan, dtype=np.float64)
    ok = den > 0
    out[ok] = num[ok] / den[ok]
    return out


def spearman_batch(X: np.ndarray, ranked_gold: np.ndarray) -> np.ndarray:
    """Spearman of each row of X against a PRE-RANKED gold matrix of the same shape."""
    return _pearson_rows(_avg_ranks(X), ranked_gold)


def _ci(v: np.ndarray) -> List[float]:
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def _band(lo: float, hi: float) -> str:
    if lo > 0.0:
        return "ABOVE"
    if hi < 0.0:
        return "BELOW"
    return "NOT_SEPARATED"


# ==================================================================================================
# shared inputs -- vocabulary, golds, pairs, norms. All from the ruler except the norms table.
# ==================================================================================================
_SHARED: Dict[str, object] = {}


def shared() -> Dict[str, object]:
    if _SHARED:
        return _SHARED
    words, counts = INS.build_vocab(INS.CORPUS, CORPUS_BYTES, V)
    w2i = {w: i for i, w in enumerate(words)}
    ortho_pool = INS.build_ortho_neighbours(words, K_DISTRACT)
    freq_pool = INS.build_freq_controls(counts, ortho_pool, K_DISTRACT)
    golds = {"GOLD_ORTHO": INS.gold_ortho(words),
             "GOLD_FREQBAND": INS.gold_freqband(counts),
             "GOLD_PLANTED": INS.gold_planted(len(words))}
    all_pairs = INS.load_simlex(INS.SIMLEX)
    pairs = [(a, b, s) for a, b, s in all_pairs if a in w2i and b in w2i]
    ia = np.array([w2i[a] for a, _, _ in pairs], dtype=np.int64)
    ib = np.array([w2i[b] for _, b, _ in pairs], dtype=np.int64)
    gold = np.array([s for _, _, s in pairs], dtype=np.float64)

    # hardened FREQUENCY channels -- per-pair scores, seed-independent
    lc = np.log(counts + 1.0)
    la, lb = lc[ia], lc[ib]
    freq_scores = {
        "FREQ_NEG_ABS_DIFF": -np.abs(la - lb),
        "FREQ_SUM": la + lb,
        "FREQ_MIN": np.minimum(la, lb),
        "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12),
    }

    tab = GS._table()
    n_cov = sum(1 for w in words if w.lower() in tab)

    _SHARED.update(words=words, counts=counts, w2i=w2i, ortho_pool=ortho_pool,
                   freq_pool=freq_pool, golds=golds, all_pairs=all_pairs, pairs=pairs,
                   ia=ia, ib=ib, gold=gold, freq_scores=freq_scores,
                   norms_table=tab, n_vocab_covered_by_norms=n_cov)
    return _SHARED


_NORM_CACHE: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}


def norms_matrix(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """[V, 12] z-scored grounded norms. OOV POLICY (pre-registered): an uncovered word gets a
    deterministic N(0,1) draw in NORM space keyed on (word, seed) and is then lifted through THE
    SAME OPERATOR as every other word -- an honest 'no content yet', uniform across arms. All 322
    scored SimLex pairs are covered, so this cannot touch the structure headline."""
    if seed in _NORM_CACHE:
        return _NORM_CACHE[seed]
    S = shared()
    words = S["words"]
    tab = S["norms_table"]
    X = np.zeros((len(words), 12), dtype=np.float32)
    miss = np.zeros(len(words), dtype=bool)
    for i, w in enumerate(words):
        v = tab.get(w.lower())
        if v is None:
            miss[i] = True
            X[i] = np.random.default_rng(
                INS._hash_seed("oovnorm:" + w, seed)).standard_normal(12)
        else:
            X[i] = np.asarray(v, dtype=np.float32)
    _NORM_CACHE[seed] = (X, miss)
    return X, miss


# ==================================================================================================
# THE LIFT OPERATORS
#
# ONE-VARIABLE DESIGN: every projection-based arm uses THE SAME projection matrix P, drawn with the
# same tag the production SimHash uses ("proj:MEANING"). Arms needing d/2 columns take the first
# d/2 columns of that SAME P, and C3_ORTHONORMAL is the QR-orthonormalisation of that SAME P. So
# INC_SIMHASH vs C3_GAUSSPROJ vs C1_KCAP_* differ ONLY in the nonlinearity, and C3_GAUSSPROJ vs
# C3_ORTHONORMAL differs ONLY in whether the projection is an exact isometry.
# ==================================================================================================
_P_CACHE: Dict[Tuple[int, int], np.ndarray] = {}


def _P(d: int, seed: int) -> np.ndarray:
    key = (d, seed)
    if key not in _P_CACHE:
        _P_CACHE[key] = np.random.default_rng(
            INS._hash_seed("proj:MEANING", seed)).standard_normal((12, d)).astype(np.float32)
    return _P_CACHE[key]


def lift_simhash(X: np.ndarray, d: int, seed: int) -> np.ndarray:
    """THE INCUMBENT. sign() with zeros mapped to +1, via the production bipolar_quantize."""
    return bipolar_quantize(X @ _P(d, seed))


def lift_gaussproj(X: np.ndarray, d: int, seed: int) -> np.ndarray:
    """C3_GAUSSPROJ: the same projection, GRADED, no sign. Prices the projection alone."""
    return (X @ _P(d, seed)).astype(np.float32)


def _frame(d: int, seed: int) -> np.ndarray:
    """A 12 x d orthonormal-ROW frame obtained by orthonormalising THE SAME P. F @ F.T == I_12, so
    (X @ F) @ (X @ F).T == X @ X.T EXACTLY: cosine is preserved bit-for-bit."""
    Q, _ = np.linalg.qr(_P(d, seed).T.astype(np.float64))     # (d, 12), orthonormal columns
    return Q.T


def lift_orthonormal(X: np.ndarray, d: int, seed: int) -> np.ndarray:
    """C3_ORTHONORMAL: exact isometric expansion. Also the KA2 known-answer arm."""
    return (X.astype(np.float64) @ _frame(d, seed)).astype(np.float32)


def lift_kcap(X: np.ndarray, d: int, seed: int, frac: float, graded: bool,
              boost: bool) -> np.ndarray:
    """C1: expansion THEN a GLOBAL k-cap -- the mushroom-body / cerebellar-granule circuit.

    binary  : the surviving units fire, the rest are silent (the fly's tag).
    graded  : survivors keep a rate proportional to drive above the adaptive threshold,
              relu(Z - theta_k) -- biological k-WTA sets a threshold, it does not one-hot.
    boost   : homeostatic per-unit standardisation across the population before the cap, so no
              unit hogs or dies (Turrigiano; the APL/homeostasis pairing).
    """
    Z = (X @ _P(d, seed)).astype(np.float32)
    if boost:
        Z = (Z - Z.mean(axis=0, keepdims=True)) / (Z.std(axis=0, keepdims=True) + 1e-8)
    k = max(1, min(d - 1, int(round(frac * d))))
    theta = np.partition(Z, d - k - 1, axis=1)[:, d - k - 1][:, None]
    if graded:
        return np.maximum(Z - theta, 0.0).astype(np.float32)
    return (Z > theta).astype(np.float32)


def lift_tuning(X: np.ndarray, d: int, seed: int, wmult: float) -> np.ndarray:
    """C2: per norm dimension, m = d // 12 overlapping gaussian tuning curves whose centres span
    the empirical 1st-99th percentile. Graded, non-negative, overlapping -- the textbook cortical
    population code for a scalar (V1 orientation columns; MEC grid cells)."""
    m = max(2, d // 12)
    lo = np.percentile(X, 1.0, axis=0)
    hi = np.percentile(X, 99.0, axis=0)
    out = np.zeros((X.shape[0], 12 * m), dtype=np.float32)
    for i in range(12):
        mu = np.linspace(lo[i], hi[i], m).astype(np.float32)
        spacing = float(hi[i] - lo[i]) / float(max(1, m - 1))
        s = wmult * spacing + 1e-6
        out[:, i * m:(i + 1) * m] = np.exp(-0.5 * ((X[:, i:i + 1] - mu[None, :]) / s) ** 2)
    return out


def lift_onoff(X: np.ndarray, d: int, seed: int) -> np.ndarray:
    """C3_ONOFF: a signed drive carried by a rectified ON/OFF PAIR, because firing rates cannot be
    negative (retinal ON-centre / OFF-centre; cortical push-pull). d_eff == d exactly."""
    h = d // 2
    Z = (X @ _P(d, seed)[:, :h]).astype(np.float32)
    return np.concatenate([np.maximum(Z, 0.0), np.maximum(-Z, 0.0)], axis=1)


_PHASOR_SCALE: Dict[int, float] = {}


def phasor_scale(seed: int) -> float:
    """Pre-registered rule: s * median pairwise Euclidean distance in norm space == 1, with the
    median taken over 4096 RANDOM VOCABULARY pairs at a fixed seed -- never over the gold pairs."""
    if seed not in _PHASOR_SCALE:
        X, _ = norms_matrix(seed)
        rng = np.random.default_rng(BOOT_SEED)
        n = X.shape[0]
        a = rng.integers(0, n, size=4096)
        b = rng.integers(0, n, size=4096)
        dist = np.linalg.norm(X[a].astype(np.float64) - X[b].astype(np.float64), axis=1)
        med = float(np.median(dist))
        _PHASOR_SCALE[seed] = 1.0 / max(med, 1e-9)
    return _PHASOR_SCALE[seed]


def lift_phasor(X: np.ndarray, d: int, seed: int) -> np.ndarray:
    """C4: a unit-modulus phasor code -- phase relative to an ongoing oscillation (theta phase
    coding), and our own FHRR shape. PINNED for position; phase-coding a SEMANTIC magnitude is
    OUR INVENTION BEING TESTED."""
    h = d // 2
    th = phasor_scale(seed) * (X @ _P(d, seed)[:, :h]).astype(np.float64)
    return (np.concatenate([np.cos(th), np.sin(th)], axis=1) / math.sqrt(h)).astype(np.float32)


def _scramble(X: np.ndarray, seed: int) -> np.ndarray:
    return X[np.random.default_rng(INS._hash_seed("scramble:norms", seed)).permutation(X.shape[0])]


def build_codes(arm: str, d: int, seed: int) -> np.ndarray:
    S = shared()
    words = S["words"]
    X, _miss = norms_matrix(seed)

    if arm == "CEIL_NORMS12_DIRECT":
        return X.copy()
    if arm == "INC_SIMHASH":
        return lift_simhash(X, d, seed)
    if arm == "FLOOR_ORTHOGRAPHIC":
        return INS.enc_orthographic(words, d, seed)
    if arm == "NULL_RANDOM_IID":
        return INS.enc_random_iid(words, d, seed)
    if arm == "KA_PLANTED_SEMANTIC":
        return INS.enc_planted_semantic(words, d, seed, S["all_pairs"])

    if arm.startswith("C1_KCAP_"):
        frac = {"f002": 0.02, "f005": 0.05, "f010": 0.10}[arm.split("_")[3]]
        graded = "_GRD_" in arm
        boost = arm.endswith("_BOOST")
        return lift_kcap(X, d, seed, frac, graded, boost)
    if arm.startswith("C2_TUNING_w"):
        return lift_tuning(X, d, seed, float(arm.split("_w")[1]))
    if arm == "C3_ORTHONORMAL":
        return lift_orthonormal(X, d, seed)
    if arm == "C3_GAUSSPROJ":
        return lift_gaussproj(X, d, seed)
    if arm == "C3_ONOFF":
        return lift_onoff(X, d, seed)
    if arm == "C4_PHASOR":
        return lift_phasor(X, d, seed)

    if arm.startswith("NULL_SCRAM_"):
        Xs = _scramble(X, seed)
        kind = arm[len("NULL_SCRAM_"):]
        if kind == "SIMHASH":
            return lift_simhash(Xs, d, seed)
        if kind == "KCAP_GRD":
            return lift_kcap(Xs, d, seed, KCAP_MAIN_FRAC, True, False)
        if kind == "TUNING":
            return lift_tuning(Xs, d, seed, 1.0)
        if kind == "ORTHONORMAL":
            return lift_orthonormal(Xs, d, seed)
        if kind == "ONOFF":
            return lift_onoff(Xs, d, seed)
        if kind == "PHASOR":
            return lift_phasor(Xs, d, seed)
    raise SystemExit("[fatal] unknown arm " + arm)


# ==================================================================================================
# one (arm, d, seed) unit
# ==================================================================================================
def pair_cosines(codes: np.ndarray, ia: np.ndarray, ib: np.ndarray) -> np.ndarray:
    C = INS._l2n(codes).astype(np.float64)
    return np.einsum("ij,ij->i", C[ia], C[ib])


def permutation_null(codes: np.ndarray, arm: str, d: int, seed: int,
                     ia: np.ndarray, ib: np.ndarray,
                     ranked_gold_1: np.ndarray,
                     n_perm: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Row-permutation null: permute the code table ACROSS WORDS, recompute the 322-pair rho,
    N_PERM times. Returns (null_rhos, per_pair_cosines_of_the_permutation_closest_to_p95).

    The p95 of THIS distribution is the scramble floor. NOT a max-of-three-draws scramble: a prior
    agent's floor was a single fluke draw sitting at the 98.6th percentile of exactly this null."""
    n_perm = N_PERM if n_perm is None else n_perm
    C = INS._l2n(codes).astype(np.float32)
    n = C.shape[0]
    rng = np.random.default_rng(INS._hash_seed("perm:" + arm + ":" + str(d), seed))
    PC = np.empty((n_perm, len(ia)), dtype=np.float64)
    for t in range(n_perm):
        p = rng.permutation(n)
        PC[t] = np.einsum("ij,ij->i", C[p[ia]].astype(np.float64), C[p[ib]].astype(np.float64))
    rhos = spearman_batch(PC, np.broadcast_to(ranked_gold_1, PC.shape))
    p95 = float(np.percentile(rhos, PERM_P))
    j = int(np.argmin(np.abs(rhos - p95)))
    return rhos, PC[j]


def run_unit(arm: str, d: int, seed: int) -> Dict:
    t0 = time.time()
    S = shared()
    ia, ib, gold = S["ia"], S["ib"], S["gold"]
    ranked_gold_1 = _avg_ranks(gold[None, :])[0]

    codes = INS._l2n(build_codes(arm, d, seed))
    d_eff = int(codes.shape[1])
    pc = pair_cosines(codes, ia, ib)
    rho = INS._spearman(pc, gold)

    out: Dict = {"arm": arm, "d": d, "seed": seed, "d_eff": d_eff,
                 "simlex_rho": float(rho), "n_pairs": int(len(ia)),
                 "pair_cosines": [float(x) for x in pc]}

    if arm in FULL_BATTERY:
        rhos_null, partner = permutation_null(codes, arm, d, seed, ia, ib, ranked_gold_1)
        out["perm_null"] = {
            "n_permutations": N_PERM,
            "what_is_permuted": "the rows of the [V, d_eff] code table, across words",
            "mean": float(np.mean(rhos_null)), "sd": float(np.std(rhos_null)),
            "p95": float(np.percentile(rhos_null, 95.0)),
            "p99": float(np.percentile(rhos_null, 99.0)),
            "max": float(np.max(rhos_null)),
            "exact_permutation_p_value": float((1.0 + np.sum(rhos_null >= rho))
                                               / (1.0 + len(rhos_null))),
        }
        out["scramble_partner_cosines"] = [float(x) for x in partner]
        out["scramble_partner_rho"] = float(INS._spearman(partner, gold))

        recov = {}
        for n in N_SWEEP:
            if n > V:
                continue
            recov[str(n)] = {f"{s:g}": INS.recoverability(codes, n, s, seed) for s in SIGMAS}
        ng = min(N_GATE, V)
        out["recoverability"] = recov
        out["sigma_half_at_N_GATE"] = INS.sigma_half(recov.get(str(ng), {}), SIGMAS)
        out["discriminability"] = {
            "disc_ortho": {f"{s:g}": INS.discriminability(codes, S["ortho_pool"], s, seed)
                           for s in SIGMAS},
            "disc_freq": {f"{s:g}": INS.discriminability(codes, S["freq_pool"], s, seed)
                          for s in SIGMAS},
        }

        onehot = np.eye(V, dtype=np.float32)
        signed = INS._l2n(np.sign(codes).astype(np.float32))
        stages = [
            ("S0_ORACLE", INS.recoverability_topb(onehot, ng, SIGMA_GATE, seed, BUNDLE_B)),
            ("S1_ENCODE", INS.recoverability_topb(codes, ng, SIGMA_GATE, seed, BUNDLE_B)),
            ("S2_ENCODE_SIGN", INS.recoverability_topb(signed, ng, SIGMA_GATE, seed, BUNDLE_B)),
            ("S3_BUNDLE", INS.bundle_survival(codes, ng, BUNDLE_B, False, seed)),
            ("S4_BUNDLE_SIGN", INS.bundle_survival(codes, ng, BUNDLE_B, True, seed)),
        ]
        chain, prev = [], None
        for name, acc in stages:
            bits = INS.fano_bits_list(acc, ng, BUNDLE_B) if acc == acc else float("nan")
            chain.append({"stage": name, "accuracy": acc, "info_bits_lower_bound": bits,
                          "criterion": "top-%d of %d" % (BUNDLE_B, ng),
                          "destroyed_bits_vs_prev": (None if prev is None else prev - bits)})
            prev = bits
        out["stage_chain"] = chain
        del onehot, signed

        struct = {}
        for gname, lab in S["golds"].items():
            ap, ch, lift, ns = INS.structure_ap(codes, lab, AP_PROBES, seed)
            struct[gname] = {"ap": ap, "chance": ch, "lift": lift, "n_scored": ns}
        out["structure"] = struct

    out["elapsed_s"] = time.time() - t0
    return out


# ==================================================================================================
# aggregate: paired bootstrap with COMMON RANDOM NUMBERS, seed-averaged within each draw
# ==================================================================================================
def boot_indices(n_pairs: int) -> np.ndarray:
    return np.random.default_rng(BOOT_SEED).integers(0, n_pairs, size=(N_BOOT, n_pairs))


def boot_rho_vector(per_seed_scores: Sequence[np.ndarray], IDX: np.ndarray,
                    ranked_gold_boot: np.ndarray) -> np.ndarray:
    """One bootstrap rho vector for an arm/floor: within each draw, rho is averaged over seeds, so
    pair-sampling uncertainty and seed variation are both represented."""
    acc = np.zeros(IDX.shape[0], dtype=np.float64)
    for sc in per_seed_scores:
        acc += spearman_batch(np.asarray(sc, dtype=np.float64)[IDX], ranked_gold_boot)
    return acc / float(len(per_seed_scores))


def diff_block(a: np.ndarray, b: np.ndarray, point_a: float, point_b: float) -> Dict:
    d = a - b
    lo, hi = _ci(d)
    return {"point": float(point_a - point_b), "ci95": [lo, hi], "band": _band(lo, hi),
            "n_boot": int(len(d))}


# ==================================================================================================
# formula self-tests -- run BEFORE any data run, and again at the top of every run
# ==================================================================================================
def selftest() -> None:
    rng = np.random.default_rng(11)

    # 1 / KA3. batched Spearman == INS._spearman, including HEAVY TIES.
    for trial in range(6):
        n = 40 + 7 * trial
        if trial % 2 == 0:
            a = rng.standard_normal(n)
            g = rng.standard_normal(n)
        else:                                  # heavy ties, the bootstrap-resample regime
            a = np.round(rng.standard_normal(n) * 1.2)
            g = np.round(rng.standard_normal(n))
        want = INS._spearman(a, g)
        got = float(spearman_batch(a[None, :], _avg_ranks(g[None, :]))[0])
        assert abs(want - got) <= T_KA3_SPEARMAN_TOL, \
            "KA3 spearman mismatch %.12f vs %.12f" % (want, got)
    # and on a stacked batch with a repeated-index resample
    base = rng.standard_normal(60)
    gg = rng.standard_normal(60)
    idx = rng.integers(0, 60, size=(5, 60))
    rg = _avg_ranks(gg[idx])
    bat = spearman_batch(base[idx], rg)
    for r in range(5):
        assert abs(bat[r] - INS._spearman(base[idx[r]], gg[idx[r]])) <= T_KA3_SPEARMAN_TOL, \
            "KA3 batch/resample mismatch"

    # 2 / KA2. the orthonormal frame is an EXACT isometry: cosine preserved.
    Xs = rng.standard_normal((64, 12)).astype(np.float32)
    F = _frame(128, 7)
    assert np.allclose(F @ F.T, np.eye(12), atol=1e-10), "frame rows not orthonormal"
    Y = (Xs.astype(np.float64) @ F)
    cx = INS._l2n(Xs).astype(np.float64)
    cy = INS._l2n(Y.astype(np.float32)).astype(np.float64)
    assert np.max(np.abs(cx @ cx.T - cy @ cy.T)) < 1e-5, "orthonormal lift is not an isometry"

    # 3. THE DIVERGENCE, PROVEN. sign() is blind to every magnitude; the graded lifts are not.
    A = lift_simhash(Xs, 128, 7)
    B = lift_simhash((2.5 * Xs).astype(np.float32), 128, 7)
    assert np.array_equal(A, B), "sign should be scale-invariant -- self-test is wrong"
    G1 = lift_gaussproj(Xs, 128, 7)
    G2 = lift_gaussproj((2.5 * Xs).astype(np.float32), 128, 7)
    assert not np.allclose(G1, G2), "graded lift must NOT be magnitude-blind"

    # 4. k-cap: exactly k survivors, correct value domain.
    for frac, graded in ((0.05, False), (0.05, True), (0.10, True)):
        K = lift_kcap(Xs, 200, 7, frac, graded, False)
        k = max(1, min(199, int(round(frac * 200))))
        nz = (K > 0).sum(axis=1)
        assert np.all(nz == k), "kcap survivors %r != k=%d" % (np.unique(nz), k)
        assert K.min() >= 0.0, "kcap produced a negative rate"
        if not graded:
            assert set(np.unique(K)).issubset({0.0, 1.0}), "binary kcap not 0/1"
    KB = lift_kcap(Xs, 200, 7, 0.05, True, True)
    assert KB.min() >= 0.0 and (KB > 0).sum(axis=1).max() == 10, "boosted kcap malformed"

    # 5. tuning curves: non-negative, graded, overlapping, and the peak tracks the input.
    T = lift_tuning(Xs, 120, 7, 1.0)
    assert T.min() >= 0.0 and T.max() <= 1.0 + 1e-6, "tuning response outside [0,1]"
    m = 120 // 12
    lo1 = float(np.percentile(Xs[:, 0], 1.0))
    hi1 = float(np.percentile(Xs[:, 0], 99.0))
    mu = np.linspace(lo1, hi1, m)
    for r in (0, 5, 17):
        want = int(np.argmin(np.abs(mu - Xs[r, 0])))
        assert int(np.argmax(T[r, :m])) == want, "tuning peak does not track the input"
    lowv, highv = np.sort(Xs[:, 0])[2], np.sort(Xs[:, 0])[-3]
    two = lift_tuning(np.stack([Xs[0] * 0 + lowv, Xs[0] * 0 + highv]).astype(np.float32),
                      120, 7, 1.0)
    assert float(two[0, :m] @ two[1, :m]) < float(two[0, :m] @ two[0, :m]), \
        "tuning similarity does not fall with distance"

    # 6. ON/OFF rectified pair: non-negative, and ON+OFF reconstructs |z| exactly.
    O = lift_onoff(Xs, 128, 7)
    assert O.min() >= 0.0, "ON/OFF produced a negative rate"
    h = 64
    Z = (Xs @ _P(128, 7)[:, :h])
    assert np.allclose(O[:, :h] + O[:, h:], np.abs(Z), atol=1e-5), "ON/OFF is not a rectified pair"

    # 7. phasor: exactly unit norm per row.
    PH = lift_phasor(Xs, 128, 7)
    assert np.allclose(np.linalg.norm(PH, axis=1), 1.0, atol=1e-5), "phasor rows not unit norm"

    # 8. the permutation null kills a planted signal, and the p95 partner sits where it should.
    gold_s = rng.standard_normal(80)
    Xp = np.zeros((300, 12), dtype=np.float32)
    Xp[:80, 0] = gold_s                       # words 0..79 carry the gold in dim 0
    Xp[:, 1:] = 0.05 * rng.standard_normal((300, 11))
    iap = np.arange(0, 80, 2)
    ibp = np.arange(1, 80, 2)
    gp = np.abs(gold_s[iap] - gold_s[ibp])
    codes_p = INS._l2n(Xp)
    pcp = pair_cosines(codes_p, iap, ibp)
    rho_p = INS._spearman(pcp, gp)
    assert abs(rho_p) > 0.20, "planted probe carries no signal (%.4f)" % rho_p
    rhos, partner = permutation_null(codes_p, "SELFTEST", 12, 7, iap, ibp,
                                     _avg_ranks(gp[None, :])[0], n_perm=200)
    assert abs(float(np.mean(rhos))) < 0.15, "permutation null is not centred near zero"
    assert abs(INS._spearman(partner, gp) - float(np.percentile(rhos, 95.0))) < 0.05, \
        "p95 partner does not sit at p95"

    # 9. the bootstrap machinery: identical arms cannot separate; a perfect arm must.
    npair = 120
    g2 = rng.standard_normal(npair)
    IDX = np.random.default_rng(BOOT_SEED).integers(0, npair, size=(300, npair))
    rgb = _avg_ranks(g2[IDX])
    same = rng.standard_normal(npair)
    bs_a = boot_rho_vector([same], IDX, rgb)
    bs_b = boot_rho_vector([same.copy()], IDX, rgb)
    lo, hi = _ci(bs_a - bs_b)
    assert lo == 0.0 and hi == 0.0, "identical arms produced a non-zero paired difference"
    perfect = g2 + 1e-9 * rng.standard_normal(npair)
    bs_p = boot_rho_vector([perfect], IDX, rgb)
    lo2, hi2 = _ci(bs_p - bs_a)
    assert _band(lo2, hi2) == "ABOVE", "a perfect arm failed to separate from a random one"

    # 10. the ruler still self-tests (regression on every shared function).
    INS.selftest()
    print("[selftest] PASS (10 checks incl. KA2 isometry, KA3 spearman, and the sign-blindness "
          "proof) + the unmodified ruler's own 20", flush=True)


# ==================================================================================================
def main() -> int:
    if _ARGS.self_test:
        selftest()
        return 0
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print("[cfg] mode=%s V=%d D_SWEEP=%s SEEDS=%s SIGMAS=%s N_PERM=%d N_BOOT=%d out=%s"
          % (RUN_MODE, V, D_SWEEP, SEEDS, SIGMAS, N_PERM, N_BOOT, out_dir), flush=True)
    selftest()

    S = shared()
    ia, ib, gold = S["ia"], S["ib"], S["gold"]
    n_pairs = len(ia)
    print("[vocab] %d words; %d covered by the grounded norms; %d SimLex pairs scored"
          % (V, S["n_vocab_covered_by_norms"], n_pairs), flush=True)

    done = completed_units(str(out_dir))
    n_total = len(D_SWEEP) * len(ARMS) * len(SEEDS)
    n_run = 0
    for d in D_SWEEP:
        for arm in ARMS:
            for seed in SEEDS:
                key = unit_key(arm, d, seed, RUN_MODE, V, "perm%d" % N_PERM)
                if key in done:
                    print("[skip] %s" % key, flush=True)
                    n_run += 1
                    continue
                r = run_unit(arm, d, seed)
                record_unit(str(out_dir), key, r)
                n_run += 1
                print("[unit %3d/%3d] %-24s d=%5d seed=%2d d_eff=%5d rho=%+.4f (%.1fs)"
                      % (n_run, n_total, arm, d, seed, r["d_eff"], r["simlex_rho"],
                         r["elapsed_s"]), flush=True)

    units = load_units(str(out_dir))
    rows = [u for u in units.values() if u.get("arm") in ARMS]

    # ---------------- paired bootstrap, COMMON RANDOM NUMBERS across every arm and floor --------
    IDX = boot_indices(n_pairs)
    ranked_gold_boot = _avg_ranks(gold[IDX])
    print("[boot] %d resamples of %d pairs, common random numbers, seed-averaged within draw"
          % (N_BOOT, n_pairs), flush=True)

    def sel(arm, d):
        got = [r for r in rows if r["arm"] == arm and r["d"] == d]
        return sorted(got, key=lambda r: r["seed"])

    freq_rho = {c: INS._spearman(S["freq_scores"][c], gold) for c in FREQ_CHANNELS}
    hardened_channel = max(FREQ_CHANNELS, key=lambda c: freq_rho[c])
    freq_vec = np.asarray(S["freq_scores"][hardened_channel], dtype=np.float64)

    results_by_d: Dict[int, Dict] = {}
    for d in D_SWEEP:
        boot: Dict[str, np.ndarray] = {}
        point: Dict[str, float] = {}
        rho_by_seed: Dict[str, List[float]] = {}
        for arm in ARMS:
            rs = sel(arm, d)
            if not rs:
                continue
            rho_by_seed[arm] = [float(r["simlex_rho"]) for r in rs]
            point[arm] = float(np.mean(rho_by_seed[arm]))
            boot[arm] = boot_rho_vector([np.asarray(r["pair_cosines"]) for r in rs],
                                        IDX, ranked_gold_boot)

        # ---- floors
        floors_boot: Dict[str, np.ndarray] = {}
        floors_point: Dict[str, float] = {}
        floors_boot["A_ORTHOGRAPHIC"] = boot["FLOOR_ORTHOGRAPHIC"]
        floors_point["A_ORTHOGRAPHIC"] = point["FLOOR_ORTHOGRAPHIC"]
        n_seeds_here = max(1, len(sel("FLOOR_ORTHOGRAPHIC", d)))
        floors_boot["HARDENED_FREQUENCY_" + hardened_channel] = boot_rho_vector(
            [freq_vec] * n_seeds_here, IDX, ranked_gold_boot)
        floors_point["HARDENED_FREQUENCY_" + hardened_channel] = float(freq_rho[hardened_channel])
        freq_key = "HARDENED_FREQUENCY_" + hardened_channel

        per_arm: Dict[str, Dict] = {}
        for arm in ARMS:
            rs = sel(arm, d)
            if not rs:
                continue
            lo, hi = _ci(boot[arm])
            entry: Dict = {
                "d_eff": rs[0]["d_eff"],
                "n_seeds": len(rs),
                "STRUCTURE": {
                    "simlex_rho": point[arm],
                    "simlex_rho_ci95": [lo, hi],
                    "simlex_rho_by_seed": rho_by_seed[arm],
                    "n_pairs": n_pairs,
                    "NOTE": ("a RANDOM encoding must sit at rho ~0 here; any real rho IS the "
                             "signal"),
                },
            }
            if arm in FULL_BATTERY:
                # own scramble floor, permutation-calibrated
                p95s = [float(r["perm_null"]["p95"]) for r in rs]
                partner_rhos = [float(r["scramble_partner_rho"]) for r in rs]
                scr_boot = boot_rho_vector(
                    [np.asarray(r["scramble_partner_cosines"]) for r in rs], IDX,
                    ranked_gold_boot)
                scr_point = float(np.mean(partner_rhos))
                fl_boot = dict(floors_boot)
                fl_point = dict(floors_point)
                fl_boot["OWN_SCRAMBLE_PERM_P95"] = scr_boot
                fl_point["OWN_SCRAMBLE_PERM_P95"] = scr_point

                per_floor = {}
                for fname in sorted(fl_boot):
                    per_floor[fname] = diff_block(boot[arm], fl_boot[fname],
                                                  point[arm], fl_point[fname])
                strongest = max(fl_point, key=lambda k: fl_point[k])
                clears_all = all(v["band"] == "ABOVE" for v in per_floor.values())
                entry["THE_BAR"] = {
                    "floors": {k: float(v) for k, v in fl_point.items()},
                    "scramble_floor_policy": (
                        "%dth percentile of a %d-permutation row-permutation null of THIS arm's "
                        "own code table. NOT a max-of-three-draws scramble. Paired-bootstrap "
                        "partner = the permutation whose rho is closest to p95, per seed."
                        % (int(PERM_P), N_PERM)),
                    "scramble_p95_by_seed": p95s,
                    "scramble_partner_rho_by_seed": partner_rhos,
                    "MARGIN_per_floor": per_floor,
                    "strongest_floor_by_point": strongest,
                    "MARGIN_over_strongest_floor": per_floor[strongest],
                    "CLEARS_ALL_THREE_FLOORS_CI_SEPARATED": bool(clears_all),
                    "permutation_p_value_by_seed": [
                        float(r["perm_null"]["exact_permutation_p_value"]) for r in rs],
                }
                entry["IDENTITY"] = {
                    "recoverability_curve_at_N_GATE": rs[0]["recoverability"].get(
                        str(min(N_GATE, V)), {}),
                    "sigma_half": rs[0].get("sigma_half_at_N_GATE"),
                    "disc_ortho_headline": rs[0]["discriminability"]["disc_ortho"].get(
                        "%g" % HEADLINE_SIGMA),
                    "disc_freq_headline": rs[0]["discriminability"]["disc_freq"].get(
                        "%g" % HEADLINE_SIGMA),
                    "NOTE": ("a RANDOM encoding is near-OPTIMAL on this axis by design; scoring "
                             "high here is NOT a win, and this axis is NEVER averaged with "
                             "STRUCTURE"),
                }
                chain_bits = {st["stage"]: float(np.mean(
                    [rr["stage_chain"][i]["info_bits_lower_bound"] for rr in rs]))
                    for i, st in enumerate(rs[0]["stage_chain"])}
                ceil_bits = math.log2(min(N_GATE, V) / float(BUNDLE_B))
                entry["BUNDLING"] = {
                    "criterion": ("pre-registered, carried forward verbatim from the parent: an "
                                  "arm retaining < %.1f bits of the %.3f-bit ceiling after the "
                                  "sum has NOT solved the flat-sum problem"
                                  % (T_G3_BUNDLE_BITS_MIN, ceil_bits)),
                    "ceiling_bits": ceil_bits,
                    "stage_chain_bits": chain_bits,
                    "bits_retained_after_the_sum": chain_bits.get("S3_BUNDLE"),
                    "bits_retained_after_the_sum_then_sign": chain_bits.get("S4_BUNDLE_SIGN"),
                    "SURVIVES_BUNDLING": bool(
                        chain_bits.get("S3_BUNDLE", 0.0) >= T_G3_BUNDLE_BITS_MIN),
                }
                entry["STRUCTURE"]["GOLD_ORTHO_lift"] = float(np.mean(
                    [rr["structure"]["GOLD_ORTHO"]["lift"] for rr in rs]))
                entry["STRUCTURE"]["GOLD_FREQBAND_lift"] = float(np.mean(
                    [rr["structure"]["GOLD_FREQBAND"]["lift"] for rr in rs]))
                entry["STRUCTURE"]["GOLD_PLANTED_lift"] = float(np.mean(
                    [rr["structure"]["GOLD_PLANTED"]["lift"] for rr in rs]))
            per_arm[arm] = entry

        # ---- G0: the lift gap, measured against the incumbent, paired
        r_ceil = point.get("CEIL_NORMS12_DIRECT", float("nan"))
        r_inc = point.get("INC_SIMHASH", float("nan"))
        gap = r_ceil - r_inc
        for arm in ARMS:
            if arm not in per_arm or arm not in CAND_ARMS + ["CEIL_NORMS12_DIRECT"]:
                continue
            vs = diff_block(boot[arm], boot["INC_SIMHASH"], point[arm], r_inc)
            closure = (point[arm] - r_inc) / gap if gap != 0 else float("nan")
            clo_lo = vs["ci95"][0] / gap if gap != 0 else float("nan")
            clo_hi = vs["ci95"][1] / gap if gap != 0 else float("nan")
            per_arm[arm]["THE_TARGET_G0"] = {
                "vs_incumbent_SIMHASH": vs,
                "gap_being_closed": float(gap),
                "closure_fraction_of_the_lift_loss": float(closure),
                "closure_fraction_ci95": [float(min(clo_lo, clo_hi)),
                                          float(max(clo_lo, clo_hi))],
                "CLOSES_THE_LIFT_GAP": bool(vs["band"] == "ABOVE"
                                            and closure == closure
                                            and closure >= T_G0_CLOSURE_MIN),
            }
        results_by_d[d] = {
            "per_arm": per_arm,
            "ceiling_rho": float(r_ceil),
            "incumbent_rho": float(r_inc),
            "lift_gap": float(gap),
            "frequency_channels_rho": {k: float(v) for k, v in freq_rho.items()},
            "hardened_frequency_channel": hardened_channel,
        }
        print("[agg] d=%d ceiling=%.4f incumbent=%.4f gap=%.4f" % (d, r_ceil, r_inc, gap),
              flush=True)

    # ---------------- gates ----------------------------------------------------------------
    d_gate = D_SWEEP[0]
    PA = results_by_d[d_gate]["per_arm"]

    def rho_at(arm, d=d_gate):
        return results_by_d[d]["per_arm"].get(arm, {}).get("STRUCTURE", {}).get(
            "simlex_rho", float("nan"))

    claims: List[Dict] = []

    def gate(gid, fam, claim, val, op, thr):
        ok = (val == val) and ((val <= thr) if op == "<=" else (val >= thr))
        claims.append({"gate_id": gid, "family": fam, "claim": claim,
                       "observed": (None if val != val else float(val)),
                       "op": op, "threshold": thr, "passed": bool(ok)})

    ceil_rho = rho_at("CEIL_NORMS12_DIRECT")
    # AMENDMENT A1 (prereg 4a, made BEFORE any data run): RG1 gates at FULL only. It compares
    # against a number measured on the 322 pairs inside the V=4096 vocabulary; SMOKE resolves
    # V=512 and therefore a different, much smaller pair population, so the comparison is
    # undefined there. Computed and reported at smoke; gated at full. No threshold changed.
    if SMOKE:
        claims.append({"gate_id": "RG1", "family": "REGRESSION_REPORTED_ONLY_AT_SMOKE",
                       "claim": ("CEIL_NORMS12_DIRECT vs the landed 0.2701 -- NOT GATED AT SMOKE "
                                 "(different pair population; prereg amendment A1)"),
                       "observed": float(abs(ceil_rho - LANDED_CEIL_RHO)),
                       "op": ">=", "threshold": 0.0, "passed": True})
    else:
        gate("RG1", "REGRESSION",
             "CEIL_NORMS12_DIRECT reproduces the landed 0.2701 (|delta| <= 5e-3)",
             -abs(ceil_rho - LANDED_CEIL_RHO), ">=", -T_RG1_CEIL_TOL)
    gate("KA1", "KNOWN", "KA_PLANTED_SEMANTIC simlex_rho >= 0.50",
         rho_at("KA_PLANTED_SEMANTIC"), ">=", T_KA1_PLANTED_RHO_MIN)
    # KA2 is gated on the per-pair COSINES, not on rho: an exact isometry must reproduce every
    # pair cosine, and that claim is not exposed to rank-tie sensitivity the way rho is.
    ka2_max = 0.0
    for _s_i, _r_o in enumerate(sel("C3_ORTHONORMAL", d_gate)):
        _r_c = sel("CEIL_NORMS12_DIRECT", d_gate)[_s_i]
        ka2_max = max(ka2_max, float(np.max(np.abs(
            np.asarray(_r_o["pair_cosines"]) - np.asarray(_r_c["pair_cosines"])))))
    gate("KA2", "KNOWN",
         "C3_ORTHONORMAL is an EXACT isometry so every one of the 322 pair cosines must equal the "
         "direct read's (max |delta| <= 1e-5)",
         -ka2_max, ">=", -T_KA2_ISOMETRY_TOL)
    claims[-1]["also_reported_rho_delta"] = float(abs(rho_at("C3_ORTHONORMAL") - ceil_rho))
    gate("KA3", "KNOWN", "batched Spearman == INS._spearman incl. ties (asserted in self-test)",
         1.0, ">=", 1.0)
    gate("NU1", "NULL", "NULL_RANDOM_IID |simlex_rho| <= 0.10",
         abs(rho_at("NULL_RANDOM_IID")), "<=", T_NU_ABS_RHO_MAX)
    worst_null = 0.0
    worst_null_arm = None
    for d in D_SWEEP:
        for a in NULL_SCRAM_ARMS:
            v = abs(rho_at(a, d))
            if v == v and v > worst_null:
                worst_null, worst_null_arm = v, "%s@d%d" % (a, d)
    gate("NU2", "NULL", "every NULL_SCRAM_* arm at every d has |simlex_rho| <= 0.10 (worst: %s)"
         % worst_null_arm, worst_null, "<=", T_NU_ABS_RHO_MAX)

    instrument_ok = all(c["passed"] for c in claims)

    g0_winners, g3_winners, g4_winners = [], [], []
    for d in D_SWEEP:
        for a in CAND_ARMS:
            e = results_by_d[d]["per_arm"].get(a)
            if not e:
                continue
            g0 = bool(e.get("THE_TARGET_G0", {}).get("CLOSES_THE_LIFT_GAP"))
            g3 = bool(e.get("BUNDLING", {}).get("SURVIVES_BUNDLING"))
            tag = "%s@d%d" % (a, d)
            if g0:
                g0_winners.append(tag)
            if g3:
                g3_winners.append(tag)
            if g0 and g3:
                g4_winners.append(tag)
    gate("G0", "TARGET",
         "at least one candidate CI-separated above the incumbent AND closure >= 0.50",
         float(len(g0_winners)), ">=", 1.0)
    gate("G3", "TARGET",
         "at least one candidate retains >= 0.5 bits of the bundling ceiling",
         float(len(g3_winners)), ">=", 1.0)
    gate("G4", "TARGET", "at least one candidate does BOTH (meaning AND bundling survival)",
         float(len(g4_winners)), ">=", 1.0)

    bar_clearers = []
    for d in D_SWEEP:
        for a in CAND_ARMS + ["CEIL_NORMS12_DIRECT", "INC_SIMHASH"]:
            e = results_by_d[d]["per_arm"].get(a)
            if e and e.get("THE_BAR", {}).get("CLEARS_ALL_THREE_FLOORS_CI_SEPARATED"):
                bar_clearers.append("%s@d%d" % (a, d))
    gate("G1", "STANDING_BAR",
         "at least one arm CI-separated above ALL THREE floors (see the scope note: the CEILING "
         "arm itself is known not to clear this on this population)",
         float(len(bar_clearers)), ">=", 1.0)

    if not instrument_ok:
        verdict = "INSTRUMENT_INVALID_GATE_FAILED"
    elif g4_winners:
        verdict = "LIFT_LOSS_CLOSED_AND_SURVIVES_BUNDLING"
    elif g0_winners:
        verdict = "LIFT_LOSS_CLOSED_BUT_DIES_IN_BUNDLING"
    elif g3_winners:
        verdict = "BUNDLING_SURVIVED_BUT_NO_MEANING_GAIN"
    else:
        verdict = "NO_CANDIDATE_CLOSES_THE_LIFT_GAP"

    failed = [c["gate_id"] for c in claims if not c["passed"]]
    msg = ("%s: %d/%d pre-registered gates passed" % (verdict, len(claims) - len(failed),
                                                      len(claims))
           + ("; FAILED=%s" % failed if failed else "")
           + ". IDENTITY and STRUCTURE are reported SEPARATELY and are never averaged.")

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": time.time() - t_start,
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "prereg": "preregs/exp_meaning_lift_population_code_v1.md",
        "ruler": ("experiments/exp_encoding_quality_instrument_v2.py at 542e1fc0d, IMPORTED "
                  "UNMODIFIED. Vocabulary, golds, sigma grid, seeds, K_DISTRACT, BUNDLE_B, "
                  "AP_PROBES, N_GATE and every measurement function come from it."),
        "config": {"V": V, "D_SWEEP": D_SWEEP, "SEEDS": SEEDS, "SIGMAS": SIGMAS,
                   "N_SWEEP": N_SWEEP, "N_GATE": N_GATE, "BUNDLE_B": BUNDLE_B,
                   "K_DISTRACT": K_DISTRACT, "AP_PROBES": AP_PROBES,
                   "CORPUS_BYTES": CORPUS_BYTES, "N_PERM": N_PERM, "N_BOOT": N_BOOT,
                   "BOOT_SEED": BOOT_SEED, "KCAP_FRACS": list(KCAP_FRACS),
                   "TUNING_WIDTHS": list(TUNING_WIDTHS)},
        "gates": claims,
        "G0_winners_close_the_lift_gap": g0_winners,
        "G3_winners_survive_bundling": g3_winners,
        "G4_winners_BOTH": g4_winners,
        "G1_arms_clearing_all_three_floors": bar_clearers,
        "reported_not_gated": {
            "INC_SIMHASH_at_d256_vs_the_landed_hub_spoke_number": {
                "measured": (rho_at("INC_SIMHASH", 256) if 256 in results_by_d else None),
                "landed": LANDED_INC_RHO_D256,
                "note": ("different projection seed/tag draw and a different OOV policy, so a "
                         "mismatch is expected and is NOT a failure"),
            },
        },
        "SCOPE_NOTE_READ_THIS_BEFORE_QUOTING_G1": (
            "G1 is the standing bar (CI-separated above ALL of orthographic, hardened frequency "
            "and the permutation-calibrated scramble p95). It may be unreachable for EVERY arm "
            "here INCLUDING THE CEILING: the direct 12-dim read scores 0.2701 and misses its own "
            "scramble floor by 0.0071 at the lower bound (exp_meaning_asset_permutation_null_v1, "
            "reproduced by exp_meaning_asset_hardened_margins_v2_complete). A lift cannot exceed "
            "what it lifts. A G1 failure is therefore a fact about THE NORMS -- already "
            "established, and Phase 1 item 1's problem -- and is NOT evidence about the lift. The "
            "lift question is G0, which is paired and within-instrument."),
        "axes_note": ("IDENTITY and STRUCTURE are reported separately BY DESIGN. A random "
                      "encoding is near-optimal on IDENTITY and at chance on STRUCTURE, so any "
                      "single scalar mixing them is unfalsifiable. This cell refuses to average "
                      "them."),
        "scope_disclaimer": (
            "CEIL_NORMS12_DIRECT runs at d_eff=12 and is NOT dimension-matched to the other arms "
            "(same disclosure class as A_ORACLE_ONEHOT). C2_TUNING runs at d_eff = 12*(d//12), "
            "near-matched not exact. Fano numbers are LOWER BOUNDS. The only semantic gold is "
            "SimLex-999 pair similarity on the 322 pairs inside the instrument's vocabulary. "
            "KA_PLANTED_SEMANTIC is fitted to that gold BY DESIGN and its rho may never be quoted "
            "as a quality result. OOV words (words with no grounded norms) receive a random "
            "N(0,1) draw in norm space and are lifted through the same operator; all 322 scored "
            "pairs are covered, so this cannot touch the structure headline."),
        "norms_coverage": {"vocab": V, "covered_by_grounded_norms": S["n_vocab_covered_by_norms"],
                           "simlex_pairs_scored": n_pairs},
        "by_d": {str(k): v for k, v in results_by_d.items()},
    }
    write_metrics(out_dir, metrics, results=rows, gate_claims=None)
    print("\n" + msg, flush=True)
    for c in claims:
        print("  [%s] %-5s %-90s observed=%s"
              % ("PASS" if c["passed"] else "FAIL", c["gate_id"], c["claim"][:90],
                 c["observed"]), flush=True)
    for d in D_SWEEP:
        print("\n--- d=%d  ceiling=%.4f  incumbent=%.4f  gap=%.4f ---"
              % (d, results_by_d[d]["ceiling_rho"], results_by_d[d]["incumbent_rho"],
                 results_by_d[d]["lift_gap"]), flush=True)
        for a in ARMS:
            e = results_by_d[d]["per_arm"].get(a)
            if not e:
                continue
            g0 = e.get("THE_TARGET_G0", {})
            bd = e.get("BUNDLING", {})
            print("  %-24s rho=%+.4f [%+.4f,%+.4f]  closure=%s  bundle_bits=%s  %s"
                  % (a, e["STRUCTURE"]["simlex_rho"], e["STRUCTURE"]["simlex_rho_ci95"][0],
                     e["STRUCTURE"]["simlex_rho_ci95"][1],
                     ("%+.3f" % g0["closure_fraction_of_the_lift_loss"]) if g0 else "  n/a",
                     ("%.4f" % bd["bits_retained_after_the_sum"]) if bd else " n/a",
                     g0.get("vs_incumbent_SIMHASH", {}).get("band", "")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
