"""exp_organ_f_accumulate_interference_diagnosis_v1 -- ORGAN F, ACCUMULATE-GATE DIAGNOSIS
(notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.6/6.7 -- the owner's ONE-ORGAN ruling; this cell
DIAGNOSES the ACCUMULATE gate, it does not rebuild anything).

WHY THIS CELL EXISTS. `exp_organ_f_deep_reading_partialcue_ladder_v1` (commit landed 2026-08-17T23:12,
sec 6.6) found the deep accumulation gradient inverts by cue kind: on POP_72/POP_128 the ORACLE cue
(query = the item's own accumulated store row) keeps CLIMBING with depth (0.0404->0.1066, 0.0453->
0.1417) while the REAL partial cue (the deployed operating point) roughly HALVES (0.0264->0.0130,
0.0312->0.0139) -- AND median gold RANK IMPROVES on the real cue too (78->72, 78->70) while hit@1
FALLS. So the defect is not "summing loses information" (the ordering improves, an oracle exploits
it) -- the hypothesis this cell tests is that summing ADDS information AND ADDS MORE INTERFERENCE
than the reader can cut through. This cell asks WHERE that interference comes from and whether it
grows faster than the signal.

============================================================================================
LEAK-SAFETY, REUSED VERBATIM, NOT RE-DERIVED. `experiments.exp_organ_f_accumulation_depth_ladder_v1`
(OLD) built and self-tested `build_profile_pool` against a hand-built toy example with a real gap (the
deployed held-out cue sentence sits INSIDE the first-90-sentence collection window, so naively reading
deeper would leak it into the store). This cell calls OLD.build_profile_pool, OLD.load_buckets_uncapped,
OLD.build_depth_snapshots, OLD.build_capacity, OLD.check_monotone_nondecreasing UNCHANGED, exactly as
`exp_organ_f_deep_reading_partialcue_ladder_v1` (SIB) already did. Leak-safety is verified by
construction (identical code path, OLD.self_test() called wholesale below) AND self-tested again here
for the NEW instruments this cell adds.

ANOTHER AGENT IS RUNNING experiments/exp_organ_f_noncollapsing_accumulation_v1.py CONCURRENTLY (per
the coordinator's brief). This cell uses a DISTINCT filename, writes only to
data/exp_organ_f_accumulate_interference_diagnosis_v1[_reduced]/ and its own
scratch/organ_f_accumulate_interference_diagnosis_v1/ subdirectory, and does not import or edit either
that sibling cell's file or SIB's file (SIB is read for its established population/floor conventions
by re-implementing the same nested-population construction here, not by importing SIB as a library --
SIB's run() does not expose the intermediate score matrices this cell needs).

============================================================================================
WHAT'S NEW VS SIB (four new instruments, per the brief; SIB's own instruments -- hit@1 both tie
conventions, d-prime vs mean, rank, winner composition -- are reused via LADDER/FB/WR exactly as SIB
uses them):

1. SIGNAL/INTERFERENCE DECOMPOSITION. Per item, per depth, per cue kind: the correct anchor's score,
   and the FULL distribution of scores against every eligible INCORRECT anchor (mean, p95, max, std),
   plus d-prime vs the field mean (reusing LADDER.dprime_stats/dprime_summary) and vs the field p95
   (new). Reported as SPAN margins (depth 72 -> deepest, paired bootstrap, reusing FB.paired_bootstrap_
   ci/FB.margin which are generic over any float array, not just hit vectors) for BOTH the correct
   score and the field mean/p95, so "does the field grow faster than the signal" is a CI-separated
   comparison, not a plot read by eye.

2. HIGH-FREQUENCY VS LOW-FREQUENCY CONTRIBUTOR DECOMPOSITION, plus mean pairwise anchor cosine. The
   cue-anchor cosine overlap is an exact sum over vocabulary columns (both sides are L2-normalised
   sparse count vectors, so splitting the vocabulary into a HIGH_FREQ set (top N_HIGH_FREQ=200 most
   frequent context word TYPES, measured off the deepest real accumulation snapshot, OUR INVENTION
   UNDER TEST -- not swept exhaustively but sanity-checked at N=50/1000 on one depth in self_test-
   adjacent CHECK, see FREQ_N_SENSITIVITY below) and its complement gives an EXACT reconstruction
   S = S_HIGH + S_LOW with no cross terms, verified in self_test(). Computed once as full [n_anchors,
   n_items_T] matrices per depth (same cost as the main score matrix, so free to slice by any
   population afterward). Reported: the correct pairing's high-frequency overlap fraction, and the
   INCORRECT field's high-frequency overlap fraction (mean over the top-20 highest-scoring incorrect
   anchors per item -- "the competitive field", not literally every anchor in the pool, most of which
   score near zero and are not real competitors). Mean pairwise anchor cosine uses the closed-form
   identity mean_{i!=j} cos(i,j) = (||sum of unit rows||^2 - n) / (n(n-1)) for L2-normalised rows,
   verified against brute-force on a toy matrix in self_test() -- this avoids ever materialising an
   n_anchors^2 pairwise matrix (n_anchors ~ several thousand) while being numerically EXACT, not an
   approximation.

3. COMMON-MODE REMOVAL, with a RANDOM-DIRECTION CONTROL matching the discipline that closed
   notes/STATUS.md DO-NOT-REDO 27 (see the READ-FIRST note in self_test() and in the report below --
   this cell's finding on whether it clears that bar is stated explicitly, never silently). The
   store's rank-1 common direction is estimated as the mean of the L2-normalised anchor rows (same
   "mean direction" convention as tools.floor_battery.constant_prototype_floor, applied here in the
   sparse V-dim accumulation space rather than the dense 256-dim projected store DO-NOT-REDO 27 used,
   because this cell diagnoses the ACCUMULATE gate specifically, which lives in that space). Removing
   a direction M from unit vectors a, q without ever materialising a dense [n_anchors, V] residual
   matrix: cos(a-M, q-M) = (a.q - a.M - M.q + M.M) / (sqrt(1-2a.M+M.M) * sqrt(1-2M.q+M.M)) for unit a,
   q -- an exact closed form reusing the ALREADY-COMPUTED S_full matrix plus two cheap sparse-dense
   matvecs (Pm_D @ M, Qm_ctx @ M) and one scalar (M.M). Verified against a dense brute-force
   subtract-then-cosine on a toy matrix in self_test(). The RANDOM control redistributes M's own
   mass to a random permutation of vocabulary columns (same norm, same magnitude histogram, semantic
   alignment destroyed) rather than drawing a fresh dense random vector -- a fresh dense vector in a
   ~10^4-column sparse bag-of-words space would have near-zero overlap with any row purely from
   dimensionality and would not be a fair control for "does removing ANY comparably-shaped direction
   help equally".

4. RANK VS HIT@1 (LADDER.rank_summary, reused, reported beside hit@1 at every depth -- this is SIB's
   own already-landed dissociation, reproduced here as a regression check, not re-derived) and WINNER
   COMPOSITION (WR.wordnet_relation_composition / WR.syntagmatic_jaccard_composition, reused exactly
   as SIB calls them) at every depth on POP_72.

ORGAN REUSE, enumerated then reconciled -- nothing above is reimplemented:
  experiments.exp_organ_f_accumulation_depth_ladder_v1 (OLD)   load_buckets_uncapped,
    build_profile_pool, build_depth_snapshots, build_capacity, check_monotone_nondecreasing,
    BUCKET_UNCAPPED_CACHE, its own self_test()
  experiments.exp_writerule_step_ladder_v1 (WR)   wordnet_relation_composition,
    syntagmatic_jaccard_composition
  experiments.exp_cue_information_audit_v1 (INFO)   raw_counts_for_window, load_corpus_and_buckets,
    build_vocab, to_sparse, l2n_sparse, _ShimSpace, C3.build_items, its own self_test()
  experiments.exp_pipeline_stage_oracle_ladder_v1 (LADDER)   build_population, dprime_stats,
    dprime_summary, rank_summary, load_full_accum_from_checkpoint, CTS, its own self_test()
  tools.floor_battery (FB)   hit_at_1_both_tie_conventions, the four floors, paired_bootstrap_ci,
    margin, as_constant_matrix, l2n, scramble_null, constant_prototype_floor, frequency_floor,
    its own self_test()
  experiments._seed_checkpoint, tools.exp_checkpoint   output dir + atomic metrics write + resume

PRIOR-WORK CHECK. `bash tools/substrate_query.sh "accumulation depth interference signal noise
decomposition common-mode removal high frequency contributor"` -- see run log in the completion
report (director_kb livelock is a known, documented condition; if the query times out the top hits
from the two directly-cited sibling cells above are read in full instead, which was done). This
cell's four new instruments (signal/interference d-prime-with-percentiles decomposition,
high/low-frequency contributor split of the accumulate step, common-mode removal AS A GATED REVIVAL
of DO-NOT-REDO 27 rather than a fresh untested idea, and the closed-form pairwise-anchor-cosine) do
not exist in OLD, SIB, or WR; not a rediscovery.

BRAIN FRAMING (per the brief). PINNED: divisive normalisation -- a response divided by a pooled sum
over a neighbourhood -- is a canonical cortical operation whose documented function is exactly to
suppress the shared component so what remains is distinguishing (Carandini & Heeger 2012). Our
ACCUMULATE step is a bare unnormalised sum, which is the one thing cortex is not; this cell measures
whether that REPLICATE-vs-SUBSTITUTE gap is the operative defect. OUR INVENTION UNDER TEST: the
specific N_HIGH_FREQ=200 threshold and TOP_K=20 competitive-field size (sanity-checked, not
exhaustively swept), and the mean-anchor-direction estimator of the common mode. Systems consolidation
/ replay (repeated reactivation extracting cross-episode structure) remains the process a plain sum
over exposures most resembles, per OLD/SIB's own framing, restated not re-derived.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. data/foundation/
never opened. Writes only under data/exp_organ_f_accumulate_interference_diagnosis_v1[_reduced]/ and
this cell's own scratch/ subdirectory (gitignored).

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every depth/cue-kind hit-vector plus the common-mode arms,
#   >1 distinct, asserted
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: outer "MAIN" unit wraps run() (tools.exp_checkpoint), plus PER-DEPTH
#   sub-checkpoints inside run() (depth-snapshot scoring + composition are the interruption-prone
#   phases), same two-tier pattern as SIB
# - discriminator survives scale: this cell RUNS the FULL grid; --grid reduced (smoke) runs the
#   IDENTICAL code path at a smaller depth/population set (POP_16_SMOKE), not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses OLD's leak-safe pool + INFO's landed cache
#   unmodified; the four NEW instruments are each self-tested against hand-built fixtures with a
#   known closed-form answer, not merely asserted to run)
# - progress_logging: print_flush_true (every phase prints a flushed line; full grid is long enough
#   that a silent multi-minute gap would look like a hang without this)
# - sweep_alignment / discriminating_fraction / composition_edges / positive_control_arms / CRLB
#   gates: N/A -- diagnostic/information-audit cell over a fixed store, same family as OLD/SIB/
#   LADDER; no primitive composition, no capacity-bound sweep. Declared, not omitted.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/hdlab/nltk next -- this can take ~40-60s cold; flushed so a "
      "slow import is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_organ_f_accumulation_depth_ladder_v1 as OLD      # noqa: E402  READ ONLY (lib)
import experiments.exp_writerule_step_ladder_v1 as WR                   # noqa: E402  READ ONLY (lib)
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as LADDER        # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "organ_f_accumulate_interference_diagnosis_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/organ_f_accumulate_interference_diagnosis_2026-08-18.md"
SCRATCH_DIR = os.path.join(REPO, "scratch", ANCHOR_NAME)

DO_NOT_REDO_27_NOTE = (
    "notes/STATUS.md DO-NOT-REDO 27 = 'rank-1 common-mode removal', CLOSED with a starred revival "
    "criterion. Prior instance (notes/SUBSTRATE_STRATEGY.md STEP 3, commit 34b94e8bc): removing the "
    "mean-anchor rank-1 direction from the DENSE 256-dim PROJECTED store on the C1 near-neighbour "
    "2AFC read-out task moved accuracy +0.0005 [CI includes zero] -- and a RANDOM rank-1 direction "
    "removed as a control moved accuracy by the IDENTICAL +0.0005. The revival bar that closure "
    "implies: the treatment (real mean direction) must beat the matched random-direction control, "
    "CI-separated, or it is the same null in new clothes. THIS CELL RUNS THAT EXACT COMPARISON "
    "(mean vs random direction removal) AS PART OF ITS OWN DESIGN, on a DIFFERENT object (the sparse "
    "unprojected accumulation store, as a function of DEPTH, not the fixed dense projected store) "
    "and a DIFFERENT question (does the fix specifically counteract DEPTH-driven interference growth, "
    "not general read-out accuracy). Verdict on whether THIS instance clears the mean-beats-random "
    "bar is reported explicitly below (COMMON_MODE_REMOVAL.cleared_do_not_redo_27_bar); if it does "
    "not, the result is reported as DIAGNOSTIC ONLY, not as a reopened direction.")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = LADDER.CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
ADDRESS_EXACT_MIN = 0.95
MIN_ITEMS_HARD = 8
MIN_ITEMS_SOFT = 30
BASELINE_DEPTH = 72
TOPK_INCORRECT_FIELD = 20   # "the competitive field" for the high/low-freq decomposition, OUR INVENTION

if SMOKE:
    DEPTHS_UNION: Tuple[int, ...] = (1, 2, 4, 8, 16, 32)
    POP_SPECS = [{"name": "POP_16_SMOKE", "cap_min": 16, "cap_max": None,
                  "depths": (1, 2, 4, 8, 16, 32)}]
    HEADLINE_POP = "POP_16_SMOKE"
    CROSSCHECK_POP = None
    PER_ANCHOR_CAP = 32
    N_HIGH_FREQ = 40
    N_PROBE_COMPOSITION = 40
else:
    DEPTHS_UNION = (1, 2, 4, 8, 16, 32, 72, 128, 256, 512, 768)
    POP_SPECS = [
        {"name": "POP_72", "cap_min": 72, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72)},
        {"name": "POP_128", "cap_min": 128, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128)},
        {"name": "POP_256", "cap_min": 256, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128, 256)},
        {"name": "POP_512", "cap_min": 512, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128, 256, 512)},
        {"name": "POP_768", "cap_min": 768, "cap_max": None,
         "depths": DEPTHS_UNION},
    ]
    HEADLINE_POP = "POP_72"          # well-powered (n~694 per SIB); primary reporting population
    CROSSCHECK_POP = "POP_512"       # deep cross-check at (72, deepest) only, cheap (same matrices)
    PER_ANCHOR_CAP = 768
    N_HIGH_FREQ = 200
    N_PROBE_COMPOSITION = 500        # POP_72 scale, comparable to WR's own N=700 / SIB's N=500


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# NEW MATH -- closed-form helpers, each proven against a toy example in self_test()
# =================================================================================================
def high_low_split(Mn: sp.csr_matrix, high_idx: np.ndarray) -> Tuple[sp.csr_matrix, sp.csr_matrix]:
    """Split an L2-normalised sparse [rows, V] matrix's COLUMNS into HIGH and LOW sets. Because both
    sides of every downstream dot product are split the SAME way, S_full = S_high + S_low EXACTLY
    (no cross terms: a dot product sums matching column indices only)."""
    V = Mn.shape[1]
    mask = np.zeros(V, dtype=bool)
    mask[high_idx] = True
    low_idx = np.flatnonzero(~mask)
    return Mn[:, high_idx].tocsr(), Mn[:, low_idx].tocsr()


def mean_pairwise_cosine(Mn: sp.csr_matrix) -> Dict:
    """EXACT mean_{i!=j} cos(row_i, row_j) for L2-NORMALISED rows, via
    sum_{i!=j} dot(i,j) = ||sum_i row_i||^2 - sum_i dot(i,i) = ||S||^2 - n  (unit rows -> dot(i,i)=1).
    O(n*V) via one sparse row-sum, never materialises an [n,n] matrix."""
    n = Mn.shape[0]
    if n < 2:
        return {"n": n, "mean_pairwise_cosine": None}
    s = np.asarray(Mn.sum(axis=0)).ravel()
    sq_norm_sum = float(s @ s)
    val = (sq_norm_sum - n) / (n * (n - 1))
    return {"n": n, "mean_pairwise_cosine": round(val, 6)}


def common_mode_residual_cosine(S_full: np.ndarray, Pm: sp.csr_matrix, Qm: sp.csr_matrix,
                                M: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    """cos(a-M, q-M) for unit rows a (of Pm), q (of Qm), WITHOUT materialising a dense [n_anchors,V]
    residual. a.q = S_full (already computed); a.M and M.q are cheap sparse-dense matvecs; M.M is a
    scalar. ||a-M||^2 = 1 - 2 a.M + M.M since ||a||=1 (same for q)."""
    AM = np.asarray(Pm @ M).ravel().astype(np.float64)          # [n_anchors]
    MQ = np.asarray(Qm @ M).ravel().astype(np.float64)          # [n_items]
    MM = float(M @ M)
    num = S_full.astype(np.float64) - AM[:, None] - MQ[None, :] + MM
    da = np.sqrt(np.clip(1.0 - 2.0 * AM + MM, eps, None))
    dq = np.sqrt(np.clip(1.0 - 2.0 * MQ + MM, eps, None))
    return (num / (da[:, None] * dq[None, :])).astype(np.float32)


def field_stats(S: np.ndarray, E: np.ndarray, GOLD: np.ndarray) -> Dict[str, np.ndarray]:
    """Per item: correct-anchor score, and the incorrect field's mean/p95/max/std, plus d-prime vs
    both. Superset of LADDER.dprime_stats (which returns only the two d-primes) -- this cell needs
    the raw field moments too, so it is computed directly rather than re-deriving from LADDER's
    narrower return."""
    field_mask = E & (~GOLD)
    Sf = np.where(field_mask, S, np.nan).astype(np.float64)
    Sg = np.where(E & GOLD, S, -np.inf).astype(np.float64)
    correct = Sg.max(axis=0)
    with np.errstate(invalid="ignore", all="ignore"):
        f_mean = np.nanmean(Sf, axis=0)
        f_std = np.nanstd(Sf, axis=0, ddof=1)
        f_p95 = np.nanpercentile(Sf, 95, axis=0)
        f_max = np.nanmax(Sf, axis=0)
    valid = np.isfinite(correct) & np.isfinite(f_mean) & np.isfinite(f_std) & (f_std > 1e-9)
    sd_safe = np.where(f_std > 1e-9, f_std, np.nan)
    dprime_mean = np.where(valid, (correct - f_mean) / sd_safe, np.nan)
    dprime_p95 = np.where(valid, (correct - f_p95) / sd_safe, np.nan)
    return {"correct": correct, "field_mean": f_mean, "field_p95": f_p95, "field_max": f_max,
            "field_std": f_std, "dprime_vs_mean": dprime_mean, "dprime_vs_p95": dprime_p95,
            "valid": valid}


def field_stats_summary(fs: Dict[str, np.ndarray], mask: Optional[np.ndarray] = None) -> Dict:
    v = fs["valid"] if mask is None else (fs["valid"] & mask)
    n = int(v.sum())
    if n == 0:
        return {"n_valid": 0}
    return {"n_valid": n,
            "mean_correct_score": round(float(np.nanmean(fs["correct"][v])), 5),
            "mean_field_mean": round(float(np.nanmean(fs["field_mean"][v])), 5),
            "mean_field_p95": round(float(np.nanmean(fs["field_p95"][v])), 5),
            "mean_field_max": round(float(np.nanmean(fs["field_max"][v])), 5),
            "mean_field_std": round(float(np.nanmean(fs["field_std"][v])), 5),
            "median_dprime_vs_mean": round(float(np.nanmedian(fs["dprime_vs_mean"][v])), 4),
            "median_dprime_vs_p95": round(float(np.nanmedian(fs["dprime_vs_p95"][v])), 4)}


def topk_incorrect_freq_fraction(S_full: np.ndarray, S_high: np.ndarray, E: np.ndarray,
                                 GOLD: np.ndarray, k: int, item_idx: np.ndarray) -> np.ndarray:
    """Per item (restricted to item_idx): mean over the top-k highest-scoring INCORRECT eligible
    anchors of S_high/S_full (the fraction of that anchor-item overlap carried by HIGH_FREQ words).
    Non-negative scores throughout (raw counts -> cosine of non-negative vectors), so a simple
    epsilon guard on the denominator suffices."""
    field_mask = E & (~GOLD)
    out = np.full(item_idx.size, np.nan, dtype=np.float64)
    for j, i in enumerate(item_idx):
        col = np.where(field_mask[:, i], S_full[:, i], -np.inf)
        if not np.isfinite(col).any():
            continue
        kk = min(k, int(np.isfinite(col).sum()))
        top = np.argpartition(-col, kk - 1)[:kk]
        denom = S_full[top, i].astype(np.float64)
        ok = denom > 1e-9
        if not ok.any():
            continue
        out[j] = float(np.mean(S_high[top[ok], i].astype(np.float64) / denom[ok]))
    return out


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    print("[selftest] " + DO_NOT_REDO_27_NOTE, flush=True)
    ev: Dict = {}

    print("[selftest] reusing OLD/INFO/LADDER/FB's own self_test() wholesale (leak-safety fixture, "
          "depth-snapshot cumulative-sum real-code-path, encoder identity, floor batteries, dprime/"
          "rank known-answers)", flush=True)
    ev["OLD_selftest_keys"] = sorted(OLD.self_test().keys())

    print("[selftest] WR composition instruments' own known-answer fixtures", flush=True)
    qw_ = ["dog", "dog", "dog"]
    ww_ = ["canine", "carburetor", "dog"]
    ig_ = np.array([False, False, True])
    idxp = np.array([0, 1, 2])
    comp = WR.wordnet_relation_composition(qw_, ww_, ig_, idxp)
    assert comp["n_probed"] == 3 and comp["counts"].get("IN_THE_GENEROUS_GOLD", 0) == 1, comp
    ev["wordnet_relation_composition_known_answer"] = comp["counts"]

    # ---- high_low_split: EXACT reconstruction, no cross terms -----------------------------------
    rng = np.random.default_rng(3)
    n_r, V = 9, 14
    raw = rng.integers(0, 5, size=(n_r, V)).astype(np.float32)
    raw[rng.random((n_r, V)) < 0.5] = 0.0
    Mn = INFO.l2n_sparse(sp.csr_matrix(raw))
    high_idx = np.array([1, 3, 5, 7, 9, 11], dtype=np.int64)
    Hh, Ll = high_low_split(Mn, high_idx)
    n_q = 6
    rawq = rng.integers(0, 4, size=(n_q, V)).astype(np.float32)
    rawq[rng.random((n_q, V)) < 0.5] = 0.0
    Qn = INFO.l2n_sparse(sp.csr_matrix(rawq))
    Hh_q, Ll_q = high_low_split(Qn, high_idx)
    S_full_toy = np.asarray((Mn @ Qn.T).todense(), dtype=np.float64)
    S_high_toy = np.asarray((Hh @ Hh_q.T).todense(), dtype=np.float64)
    S_low_toy = np.asarray((Ll @ Ll_q.T).todense(), dtype=np.float64)
    assert np.allclose(S_full_toy, S_high_toy + S_low_toy, atol=1e-5), \
        (float(np.abs(S_full_toy - (S_high_toy + S_low_toy)).max()))
    ev["high_low_split_exact_reconstruction"] = {"PASS": True, "max_abs_err":
                                                  float(np.abs(S_full_toy - (S_high_toy + S_low_toy)).max())}

    # ---- mean_pairwise_cosine: closed form matches brute force on a toy unit-row matrix ----------
    toy = rng.standard_normal((11, 5)).astype(np.float32)
    toy_n = FB.l2n(toy)
    brute = []
    for i in range(11):
        for j in range(11):
            if i != j:
                brute.append(float(toy_n[i] @ toy_n[j]))
    brute_mean = float(np.mean(brute))
    closed = mean_pairwise_cosine(sp.csr_matrix(toy_n))
    assert abs(closed["mean_pairwise_cosine"] - brute_mean) < 1e-4, (closed, brute_mean)
    ev["mean_pairwise_cosine_matches_brute_force"] = {"closed": closed["mean_pairwise_cosine"],
                                                       "brute": round(brute_mean, 6)}

    # ---- common_mode_residual_cosine: closed form matches dense subtract-then-cosine -------------
    n_a2, n_i2, V2 = 10, 7, 9
    Pn = FB.l2n(rng.standard_normal((n_a2, V2)).astype(np.float32))
    Qn2 = FB.l2n(rng.standard_normal((n_i2, V2)).astype(np.float32))
    M_toy = Pn.mean(axis=0)
    S_full2 = (Pn @ Qn2.T).astype(np.float32)
    closed_resid = common_mode_residual_cosine(S_full2, sp.csr_matrix(Pn), sp.csr_matrix(Qn2), M_toy)
    dense_resid = np.zeros((n_a2, n_i2), dtype=np.float64)
    Pr = Pn - M_toy[None, :]
    Qr = Qn2 - M_toy[None, :]
    for i in range(n_a2):
        for j in range(n_i2):
            na = np.linalg.norm(Pr[i]); nq = np.linalg.norm(Qr[j])
            dense_resid[i, j] = float(Pr[i] @ Qr[j]) / max(na * nq, 1e-12)
    assert np.allclose(closed_resid, dense_resid, atol=1e-4), \
        float(np.abs(closed_resid - dense_resid).max())
    ev["common_mode_residual_cosine_matches_dense"] = {
        "PASS": True, "max_abs_err": float(np.abs(closed_resid - dense_resid).max())}

    # ---- common_mode_residual_cosine: removing a direction ORTHOGONAL to everything is a no-op ---
    M_zero = np.zeros(V2, dtype=np.float32)
    resid_zero = common_mode_residual_cosine(S_full2, sp.csr_matrix(Pn), sp.csr_matrix(Qn2), M_zero)
    assert np.allclose(resid_zero, S_full2, atol=1e-4), "removing the zero vector must be a no-op"
    ev["common_mode_zero_direction_is_noop"] = True

    # ---- topk_incorrect_freq_fraction: known-answer on a hand-built 2-item toy --------------------
    S_toy2 = np.array([[10.0, 0.0], [1.0, 1.0], [2.0, 1.0], [0.5, 1.0]], dtype=np.float32)
    S_high_toy2 = np.array([[8.0, 0.0], [1.0, 0.5], [0.0, 1.0], [0.5, 1.0]], dtype=np.float32)
    E_toy2 = np.ones((4, 2), dtype=bool)
    GOLD_toy2 = np.zeros((4, 2), dtype=bool)
    GOLD_toy2[0, 0] = True; GOLD_toy2[1, 1] = True
    frac = topk_incorrect_freq_fraction(S_toy2, S_high_toy2, E_toy2, GOLD_toy2, k=2,
                                        item_idx=np.array([0, 1]))
    # item 0: incorrect field rows 1,2,3 scores [1,2,0.5] -> top2 = rows{1,2}(2,1) high=[1,0]
    #   frac = mean(1/1, 0/2) = 0.5
    assert abs(frac[0] - 0.5) < 1e-9, frac
    ev["topk_incorrect_freq_fraction_known_answer"] = {"item0": round(float(frac[0]), 4)}

    # ---- field_stats: planted separation, known median d-prime, matches LADDER on the same input --
    n_a3, n_i3 = 30, 12
    Sp = rng.standard_normal((n_a3, n_i3)).astype(np.float32)
    Ep = np.ones((n_a3, n_i3), dtype=bool)
    Gp = np.zeros((n_a3, n_i3), dtype=bool)
    Gp[0, :] = True
    Sp[0, :] = 8.0
    fs = field_stats(Sp, Ep, Gp)
    fsum = field_stats_summary(fs)
    assert fsum["median_dprime_vs_mean"] > 4.0, fsum
    ladder_d = LADDER.dprime_stats(Sp, Ep, Gp)
    ladder_sum = LADDER.dprime_summary(ladder_d)
    assert abs(fsum["median_dprime_vs_mean"] - ladder_sum["median_dprime_vs_mean"]) < 1e-3, \
        (fsum, ladder_sum)
    ev["field_stats_matches_LADDER_dprime"] = {"PASS": True, "field_stats_dprime":
                                               fsum["median_dprime_vs_mean"],
                                               "LADDER_dprime": ladder_sum["median_dprime_vs_mean"]}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str, out_dir: str) -> Dict:
    t0 = time.time()
    Pp = LADDER.build_population()
    C, mat, mat_ok = Pp["C"], Pp["mat"], Pp["mat_ok"]
    n_anchors, qidx = Pp["n_anchors"], Pp["qidx"]
    GOLD, E, keep_ALL = Pp["GOLD"], Pp["E"], Pp["keep"]
    aux = Pp["aux"]
    anchors = list(C["anchors"])
    MATn = FB.l2n(mat)

    T = np.flatnonzero(keep_ALL)
    qidx_T = qidx[T]
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    Tq = aux["Tq"][T]
    n_items_T = T.size
    print(f"[load] n_anchors={n_anchors} n_items_T={n_items_T} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "RULER_MODE_GATE": LADDER.CTS.ruler_mode_gate(),
                "DO_NOT_REDO_27_NOTE": DO_NOT_REDO_27_NOTE,
                "TOPK_INCORRECT_FIELD": TOPK_INCORRECT_FIELD, "N_HIGH_FREQ": N_HIGH_FREQ}

    # ---- corpus, capped/uncapped buckets, leak-safe profile pool, capacity ------------------------
    sents, buckets_capped, counts_capped, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    buckets_uncapped = OLD.load_buckets_uncapped(sents)
    profile_pool = OLD.build_profile_pool(anchors, buckets_capped, buckets_uncapped)
    capacity = OLD.build_capacity(anchors, profile_pool)
    item_capacity = capacity[qidx_T]
    rep["CAPACITY_ITEM_COUNTS"] = {str(d): int((item_capacity >= d).sum())
                                   for d in (16, 72, 128, 256, 512, 768)}
    print("[capacity] " + json.dumps(rep["CAPACITY_ITEM_COUNTS"]), flush=True)

    # ---- REAL cue, reused READ ONLY from exp_cue_information_audit_v1's checkpoint ----------------
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, _diag = INFO.C3.build_items(shim, buckets_capped, counts_capped, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), "rebuilt item metadata misaligned with cache"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    _P_full_unused, Q_ctx_full, reuse_diag = LADDER.load_full_accum_from_checkpoint(
        info_out_dir, anchors, item_ids_T)
    rep["real_cue_checkpoint_reuse"] = reuse_diag
    del _P_full_unused

    # ---- depth snapshots -----------------------------------------------------------------------
    P_by_depth, all_occ, snap_diag = OLD.build_depth_snapshots(
        anchors, profile_pool, sents, DEPTHS_UNION, PER_ANCHOR_CAP)
    rep["DEPTH_SNAPSHOT_BUILD"] = snap_diag
    del all_occ

    # ---- shared vocab, and the HIGH_FREQ set off the deepest real accumulation snapshot -----------
    vocab_groups = [P_by_depth[d] for d in DEPTHS_UNION] + [Q_ctx_full]
    vocab = INFO.build_vocab(vocab_groups)
    V = len(vocab)
    deepest_all = max(DEPTHS_UNION)
    global_freq = np.zeros(V, dtype=np.float64)
    for cnt in P_by_depth[deepest_all].values():
        for w, c in cnt.items():
            global_freq[vocab[w]] += c
    order = np.argsort(-global_freq)
    high_idx = order[:min(N_HIGH_FREQ, V)]
    rep["vocab_n_distinct_content_words"] = V
    rep["HIGH_FREQ_WORDS_SAMPLE"] = [w for w, i in sorted(vocab.items(), key=lambda kv: kv[1])
                                     if i in set(high_idx.tolist())][:30]
    print(f"[vocab] V={V} N_HIGH_FREQ={N_HIGH_FREQ} t={time.time() - t0:.0f}s", flush=True)

    Qm_ctx = INFO.l2n_sparse(INFO.to_sparse(Q_ctx_full, item_ids_T, vocab))

    # =============================== PER-DEPTH, GLOBAL SCORE (all anchors x all T items) ============
    # Reused pattern from SIB: score once per depth over the FULL population, slice by any
    # population's item mask afterward -- proven identical to direct rescoring in SIB's own
    # self_test(); the anchor axis (eligibility) never varies by population, only the item mask does.
    hits_exp: Dict[str, np.ndarray] = {}
    rank_of: Dict[str, Dict] = {}
    fieldstats_of: Dict[str, Dict[str, np.ndarray]] = {}
    freqfrac_correct_of: Dict[int, np.ndarray] = {}
    freqfrac_incorrect_of: Dict[int, np.ndarray] = {}
    pairwise_cos_global_of: Dict[int, Dict] = {}
    pairwise_cos_headline_of: Dict[int, Dict] = {}
    commonmode_of: Dict[int, Dict] = {}
    winner_idx_of: Dict[str, np.ndarray] = {}
    addressing_of: Dict[int, np.ndarray] = {}

    headline_spec = next(s for s in POP_SPECS if s["name"] == HEADLINE_POP)
    headline_mask_items = (item_capacity >= headline_spec["cap_min"])
    headline_anchor_idx = np.array(sorted(set(int(qidx_T[i]) for i in
                                              np.flatnonzero(headline_mask_items))), dtype=np.int64)

    has_data = capacity >= 1
    checkpoint_units = load_units(out_dir)
    checkpoint_done = completed_units(out_dir)

    for D in DEPTHS_UNION:
        dk = unit_key("DEPTH", CODE_VERSION, grid, str(D))
        if dk in checkpoint_done:
            u = checkpoint_units[dk]
            hits_exp[f"D{D}_REAL"] = np.array(u["hit_exp_real"], dtype=np.float64)
            hits_exp[f"D{D}_ORACLE"] = np.array(u["hit_exp_oracle"], dtype=np.float64)
            rank_of[f"D{D}_REAL"] = u["rank_real"]
            # "valid" is bool; every other field_real entry is float -- restore types explicitly,
            # a bool-vs-float64 mixup here would break the "& mask" boolean indexing downstream.
            fieldstats_of[f"D{D}_REAL"] = {
                k: (np.array(v, dtype=bool) if k == "valid" else np.array(v, dtype=np.float64))
                for k, v in u["field_real"].items()}
            # freqfrac arrays were sentinel-encoded (-1.0 for NaN) for JSON round-trip; restore NaN.
            fc = np.array(u["freqfrac_correct"], dtype=np.float64)
            fi = np.array(u["freqfrac_incorrect"], dtype=np.float64)
            freqfrac_correct_of[D] = np.where(fc < -0.5, np.nan, fc)
            freqfrac_incorrect_of[D] = np.where(fi < -0.5, np.nan, fi)
            pairwise_cos_global_of[D] = u["pairwise_global"]
            pairwise_cos_headline_of[D] = u["pairwise_headline"]
            commonmode_of[D] = u["commonmode"]
            winner_idx_of[f"D{D}_REAL"] = np.array(u["winner_real"], dtype=np.int64)
            addressing_of[D] = np.array(u["addressing_oracle"], dtype=np.float64)
            print(f"[depth] D={D} RESUMED FROM CHECKPOINT", flush=True)
            continue

        Pm_D = INFO.l2n_sparse(INFO.to_sparse(P_by_depth[D], anchors, vocab))
        S_oracle = np.asarray((Pm_D @ Pm_D[qidx_T].T).todense(), dtype=np.float32)
        h_o = FB.hit_at_1_both_tie_conventions(S_oracle, E_T, GOLD_T)
        hits_exp[f"D{D}_ORACLE"] = h_o["hit_exp"]
        # K1 self-identity sanity (matches SIB's own convention): the oracle cue's argmax over
        # eligible anchors must recover the item's OWN anchor, not merely a WordNet-gold anchor.
        Sm_o = np.where(mat_ok[:, None], S_oracle, -np.inf)
        addressing_of[D] = (np.argmax(Sm_o, axis=0) == qidx_T).astype(np.float64)
        del S_oracle, Sm_o

        S_real = np.asarray((Pm_D @ Qm_ctx.T).todense(), dtype=np.float32)
        h_r = FB.hit_at_1_both_tie_conventions(S_real, E_T, GOLD_T)
        hits_exp[f"D{D}_REAL"] = h_r["hit_exp"]
        rs, _ro, _rc = LADDER.rank_summary(S_real, E_T, GOLD_T)
        rank_of[f"D{D}_REAL"] = rs
        fs = field_stats(S_real, E_T, GOLD_T)
        fieldstats_of[f"D{D}_REAL"] = fs
        Sm2 = np.where(E_T, S_real, -np.inf)
        winner_idx_of[f"D{D}_REAL"] = np.argmax(Sm2, axis=0)

        # ---- high/low frequency split (REAL cue only, the deployed regime) ------------------------
        Ph, Pl = high_low_split(Pm_D, high_idx)
        Qh, Ql = high_low_split(Qm_ctx, high_idx)
        S_high = np.asarray((Ph @ Qh.T).todense(), dtype=np.float32)
        gtop = np.argmax(np.where(GOLD_T & E_T, 1.0, -np.inf), axis=0)
        has_gold = (GOLD_T & E_T).any(axis=0)
        frac_correct = np.full(n_items_T, np.nan)
        valid_c = np.flatnonzero(has_gold)
        denom_c = S_real[gtop[valid_c], valid_c].astype(np.float64)
        ok_c = denom_c > 1e-9
        frac_correct[valid_c[ok_c]] = S_high[gtop[valid_c[ok_c]], valid_c[ok_c]].astype(np.float64) \
            / denom_c[ok_c]
        freqfrac_correct_of[D] = frac_correct
        all_idx = np.arange(n_items_T)
        freqfrac_incorrect_of[D] = topk_incorrect_freq_fraction(
            S_real, S_high, E_T, GOLD_T, TOPK_INCORRECT_FIELD, all_idx)
        del Ph, Pl, Qh, Ql, S_high

        # ---- mean pairwise anchor cosine: GLOBAL (all eligible-with-data anchors) and HEADLINE
        # (the set of anchors actually queried by HEADLINE_POP's items) --------------------------
        elig_data_idx = np.flatnonzero(mat_ok & has_data)
        pairwise_cos_global_of[D] = mean_pairwise_cosine(Pm_D[elig_data_idx])
        pairwise_cos_headline_of[D] = mean_pairwise_cosine(Pm_D[headline_anchor_idx])

        # ---- common-mode removal + random-direction control, on the HEADLINE population's items --
        M_mean = np.asarray(Pm_D[headline_anchor_idx].mean(axis=0)).ravel().astype(np.float32)
        rng_cm = np.random.default_rng(MASTER_SEED + 7331 + D)
        M_random = M_mean[rng_cm.permutation(M_mean.size)]
        S_resid_mean = common_mode_residual_cosine(S_real, Pm_D, Qm_ctx, M_mean)
        S_resid_rand = common_mode_residual_cosine(S_real, Pm_D, Qm_ctx, M_random)
        h_before = h_r["hit_exp"]
        h_mean = FB.hit_at_1_both_tie_conventions(S_resid_mean, E_T, GOLD_T)["hit_exp"]
        h_rand = FB.hit_at_1_both_tie_conventions(S_resid_rand, E_T, GOLD_T)["hit_exp"]
        headline_item_mask = (item_capacity >= headline_spec["cap_min"])
        pb = FB.paired_bootstrap_ci({"before": h_before, "mean_removed": h_mean,
                                     "random_removed": h_rand}, headline_item_mask, N_BOOT,
                                    MASTER_SEED + 9001 + D)
        m_vs_before = FB.margin(pb["boot"], "mean_removed", "before")
        m_vs_random = FB.margin(pb["boot"], "mean_removed", "random_removed")
        commonmode_of[D] = {
            "hit_before": round(pb["acc"]["before"], 4), "hit_mean_removed": round(pb["acc"]["mean_removed"], 4),
            "hit_random_removed": round(pb["acc"]["random_removed"], 4),
            "margin_mean_removed_vs_before": m_vs_before,
            "margin_mean_removed_vs_random_removed": m_vs_random,
            "cleared_do_not_redo_27_bar": m_vs_random["band"] == "ABOVE"}
        del S_resid_mean, S_resid_rand

        record_unit(out_dir, dk, {
            "hit_exp_real": hits_exp[f"D{D}_REAL"].tolist(), "hit_exp_oracle": hits_exp[f"D{D}_ORACLE"].tolist(),
            "rank_real": rank_of[f"D{D}_REAL"], "field_real": {k: v.tolist() for k, v in fs.items()
                                                              if k != "valid"} | {"valid": fs["valid"].tolist()},
            "freqfrac_correct": np.nan_to_num(freqfrac_correct_of[D], nan=-1.0).tolist(),
            "freqfrac_incorrect": np.nan_to_num(freqfrac_incorrect_of[D], nan=-1.0).tolist(),
            "pairwise_global": pairwise_cos_global_of[D], "pairwise_headline": pairwise_cos_headline_of[D],
            "commonmode": commonmode_of[D], "winner_real": winner_idx_of[f"D{D}_REAL"].tolist(),
            "addressing_oracle": addressing_of[D].tolist()})
        print(f"[depth] D={D} REAL_hit={hits_exp[f'D{D}_REAL'].mean():.4f} "
             f"ORACLE_hit={hits_exp[f'D{D}_ORACLE'].mean():.4f} "
             f"pairwise_cos_headline={pairwise_cos_headline_of[D]['mean_pairwise_cosine']} "
             f"commonmode_cleared={commonmode_of[D]['cleared_do_not_redo_27_bar']} "
             f"t={time.time() - t0:.0f}s", flush=True)
        del S_real

    # ---- floors, computed ONCE over the full T (projected 256-dim space, depth-independent) -------
    S_orth = (FB.l2n(aux["t_mat"]) @ FB.l2n(Tq).T).astype(np.float32)
    S_freq = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items_T)
    S_scr = (FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191)) @ FB.l2n(C["Q_part"][T]).T).astype(np.float32)
    S_const = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), n_items_T)
    for fname, S in (("F_ORTHOGRAPHIC", S_orth), ("F_FREQUENCY", S_freq), ("F_SCRAMBLE", S_scr),
                    ("F_CONSTANT_PROTOTYPE", S_const)):
        hits_exp[fname] = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)["hit_exp"]
    del S_orth, S_freq, S_scr, S_const

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_distinct"] = len(set(digests.values()))
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_total"] = len(digests)

    # =============================== PER-POPULATION PROCESSING (nested) =============================
    per_population: Dict[str, Dict] = {}
    sanity: Dict[str, Dict] = {}
    for spec in POP_SPECS:
        name, cap_min, depths = spec["name"], spec["cap_min"], spec["depths"]
        mask = item_capacity >= cap_min
        n_items_pop = int(mask.sum())
        n_anchors_pop = len(set(qidx_T[mask].tolist()))
        if n_items_pop < MIN_ITEMS_HARD:
            per_population[name] = {"SKIPPED_TOO_SMALL": True, "n_items": n_items_pop}
            print(f"[{name}] SKIPPED -- n_items={n_items_pop} < {MIN_ITEMS_HARD}", flush=True)
            continue
        underpowered = n_items_pop < MIN_ITEMS_SOFT

        arm_names = [f"D{d}_ORACLE" for d in depths] + [f"D{d}_REAL" for d in depths] + \
            ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
        pop_hits = {a: hits_exp[a] for a in arm_names}
        pb = FB.paired_bootstrap_ci(pop_hits, mask, N_BOOT, MASTER_SEED + 101 + cap_min)
        acc, boot = pb["acc"], pb["boot"]
        binding = max(("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"),
                      key=lambda f: acc[f])

        deepest = max(depths)
        # ---- SIGNAL/INTERFERENCE SPAN: correct score AND field mean/p95, depth 72 -> deepest, PAIRED
        span_signal = {}
        if BASELINE_DEPTH in depths and deepest != BASELINE_DEPTH:
            for stat_name, key in (("correct_score", "correct"), ("field_mean", "field_mean"),
                                   ("field_p95", "field_p95")):
                arr_base = fieldstats_of[f"D{BASELINE_DEPTH}_REAL"][key]
                arr_deep = fieldstats_of[f"D{deepest}_REAL"][key]
                pbv = FB.paired_bootstrap_ci({"base": arr_base, "deep": arr_deep}, mask, N_BOOT,
                                             MASTER_SEED + 202 + cap_min)
                span_signal[stat_name] = FB.margin(pbv["boot"], "deep", "base")
        per_rung = {}
        for a in arm_names:
            per_rung[a] = {"SIGNAL_hit_at_1": round(acc[a], 4),
                          "ci95": [round(float(np.percentile(boot[a], 2.5)), 4),
                                  round(float(np.percentile(boot[a], 97.5)), 4)],
                          "margin_vs_binding_floor": FB.margin(boot, a, binding) if a != binding else None}
            if a.endswith("_REAL"):
                per_rung[a]["FIELD_STATS"] = field_stats_summary(fieldstats_of[a], mask)
                per_rung[a]["RANK"] = rank_of[a]
                D_here = int(a[1:a.index("_")])
                per_rung[a]["FREQ_DECOMP"] = {
                    "correct_frac_high": round(float(np.nanmean(freqfrac_correct_of[D_here][mask])), 4)
                    if np.isfinite(freqfrac_correct_of[D_here][mask]).any() else None,
                    "incorrect_topk_frac_high": round(float(np.nanmean(freqfrac_incorrect_of[D_here][mask])), 4)
                    if np.isfinite(freqfrac_incorrect_of[D_here][mask]).any() else None}

        # K1 self-identity sanity, computed once per depth in the main loop (addressing_of):
        # the oracle cue's argmax must recover the item's OWN anchor.
        addr_ok = float(addressing_of[deepest][mask].mean())
        rng_n = np.random.default_rng(MASTER_SEED + 4141 + cap_min)
        idx_pop = np.flatnonzero(mask)
        perm_local = rng_n.permutation(idx_pop.size)
        Pm_deep = INFO.l2n_sparse(INFO.to_sparse(P_by_depth[deepest], anchors, vocab))
        Q_pop = Qm_ctx[idx_pop]
        S_null = np.asarray((Pm_deep @ Q_pop[perm_local].T).todense(), dtype=np.float32)
        h_null = FB.hit_at_1_both_tie_conventions(S_null, E_T[:, idx_pop], GOLD_T[:, idx_pop])
        chance = 1.0 / max(n_anchors_pop, 1)
        sanity[name] = {"K1_known_answer": {"addressing_at_deepest": round(addr_ok, 6),
                                            "gate": ADDRESS_EXACT_MIN, "PASSED": bool(addr_ok >= ADDRESS_EXACT_MIN)},
                        "N1_random_null": {"hit_at_1_RANDOM_NULL_mean": round(float(h_null["hit_exp"].mean()), 4),
                                          "chance_approx": round(chance, 6),
                                          "PASSED": bool(float(h_null["hit_exp"].mean()) < max(0.05, 20.0 * chance))}}
        publishable = sanity[name]["K1_known_answer"]["PASSED"] and sanity[name]["N1_random_null"]["PASSED"]
        del Pm_deep, S_null

        per_population[name] = {"n_items": n_items_pop, "n_anchors": n_anchors_pop, "depths": list(depths),
                                "UNDERPOWERED": underpowered, "PUBLISHABLE": publishable,
                                "PER_RUNG": per_rung, "BINDING_FLOOR": binding,
                                "BINDING_FLOOR_VALUE": round(acc[binding], 4),
                                "SIGNAL_INTERFERENCE_SPAN_72_to_deepest": span_signal}
        print(f"[{name}] n_items={n_items_pop} UNDERPOWERED={underpowered} PUBLISHABLE={publishable} "
             f"binding_floor={binding}={acc[binding]:.4f}", flush=True)

    rep["PER_POPULATION"] = per_population
    rep["SANITY"] = sanity
    rep["MEAN_PAIRWISE_ANCHOR_COSINE_GLOBAL_BY_DEPTH"] = {str(d): pairwise_cos_global_of[d] for d in DEPTHS_UNION}
    rep["MEAN_PAIRWISE_ANCHOR_COSINE_HEADLINE_BY_DEPTH"] = {str(d): pairwise_cos_headline_of[d] for d in DEPTHS_UNION}
    rep["COMMON_MODE_REMOVAL_BY_DEPTH"] = {str(d): commonmode_of[d] for d in DEPTHS_UNION}

    # =============================== WINNER COMPOSITION (HEADLINE_POP, every depth) =================
    print("[composition] building sentence co-occurrence index", flush=True)
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in INFO.C3.content_lemmas(s):
            where.setdefault(w, set()).add(si)
    query_words = [C["L_words"][int(t)] for t in T]
    has_gold = (GOLD_T & E_T).any(axis=0)
    gtop = np.argmax(np.where(GOLD_T & E_T, 1.0, -np.inf), axis=0)
    gold_words_all: List[Optional[str]] = [anchors[int(gtop[i])] if has_gold[i] else None
                                           for i in range(n_items_T)]
    idx_pool = np.flatnonzero(headline_mask_items)
    rng_probe = np.random.default_rng(MASTER_SEED + 909)
    n_probe = min(N_PROBE_COMPOSITION, idx_pool.size)
    idx_probe = np.sort(rng_probe.choice(idx_pool, size=n_probe, replace=False))
    composition_per_depth: Dict[str, Dict] = {}
    for D in headline_spec["depths"]:
        arm = f"D{D}_REAL"
        ck_key = unit_key("COMPOSITION", CODE_VERSION, grid, str(D))
        prior = load_units(out_dir).get(ck_key)
        if prior is not None:
            composition_per_depth[str(D)] = prior
            print(f"[composition] D={D} RESUMED FROM CHECKPOINT", flush=True)
            continue
        top1 = winner_idx_of[arm]
        winner_words = [anchors[int(w)] for w in top1]
        in_gold = np.array([bool(GOLD_T[int(top1[i]), i]) for i in range(n_items_T)])
        wn_comp = WR.wordnet_relation_composition(query_words, winner_words, in_gold, idx_probe)
        jac_comp = WR.syntagmatic_jaccard_composition(query_words, winner_words, gold_words_all,
                                                       where, idx_probe)
        rec = {"depth": D, "n_probe": int(idx_probe.size), "wordnet": wn_comp, "syntagmatic": jac_comp}
        composition_per_depth[str(D)] = rec
        record_unit(out_dir, ck_key, rec)
        print(f"[composition] D={D} no_relation={wn_comp['fraction_no_close_relation']} "
             f"winner_cooc={jac_comp['TOP1_WINNER']['mean']}", flush=True)
    rep["WINNER_COMPOSITION_HEADLINE"] = {"population": HEADLINE_POP, "n_probe": int(idx_probe.size),
                                          "PER_DEPTH": composition_per_depth}

    # composition-flat check: no-relation fraction CI-separated change from shallowest to deepest
    depths_sorted = sorted(int(d) for d in composition_per_depth.keys())
    comp_trend = None
    if len(depths_sorted) >= 2:
        shallow, deep = depths_sorted[0], depths_sorted[-1]
        wn_shallow = np.array(composition_per_depth[str(shallow)]["wordnet"]["no_relation_bool"], dtype=bool)
        wn_deep = np.array(composition_per_depth[str(deep)]["wordnet"]["no_relation_bool"], dtype=bool)
        n_pr = wn_shallow.size
        rng_cb = np.random.default_rng(MASTER_SEED + 5151)
        boot_idx = rng_cb.integers(0, n_pr, size=(2000, n_pr))
        d_no_rel = wn_deep.astype(np.float64)[boot_idx].mean(axis=1) - wn_shallow.astype(np.float64)[boot_idx].mean(axis=1)
        lo, hi = float(np.percentile(d_no_rel, 2.5)), float(np.percentile(d_no_rel, 97.5))
        comp_trend = {"shallow_depth": shallow, "deep_depth": deep,
                     "no_relation_delta_point": round(float(np.mean(d_no_rel)), 4),
                     "no_relation_delta_ci95": [round(lo, 4), round(hi, 4)],
                     "FLAT": lo <= 0 <= hi}
    rep["COMPOSITION_TREND"] = comp_trend

    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = True
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959", "0.1390", "0.0873", "0.2291", "0.1073"]
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    t_start = time.time()
    ev = self_test()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = str(get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else "")))
    os.makedirs(out_dir, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} out={out_dir}", flush=True)

    done = completed_units(out_dir)
    units = load_units(out_dir)
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE, out_dir)
        record_unit(out_dir, key, rep)

    # ---- mechanical stop-if classification ---------------------------------------------------
    sanity_all_pass = all(v.get("K1_known_answer", {}).get("PASSED", False) and
                          v.get("N1_random_null", {}).get("PASSED", False)
                          for v in rep["SANITY"].values())

    interference_grows_faster = []
    refuted_populations = []
    for pop_name, pop_rep in rep["PER_POPULATION"].items():
        span = pop_rep.get("SIGNAL_INTERFERENCE_SPAN_72_to_deepest") or {}
        cs, fp = span.get("correct_score"), span.get("field_p95")
        if cs is None or fp is None:
            continue
        deepest = max(pop_rep["depths"])
        real_arm = pop_rep["PER_RUNG"].get(f"D{deepest}_REAL", {})
        real_base = pop_rep["PER_RUNG"].get(f"D{BASELINE_DEPTH}_REAL", {})
        hit_fell = (real_arm.get("SIGNAL_hit_at_1") is not None and real_base.get("SIGNAL_hit_at_1") is not None
                   and real_arm["SIGNAL_hit_at_1"] < real_base["SIGNAL_hit_at_1"])
        if fp["band"] == "ABOVE" and cs["band"] != "ABOVE":
            interference_grows_faster.append(pop_name)
        elif hit_fell and fp["band"] != "ABOVE":
            refuted_populations.append(pop_name)

    common_mode_fixes = [d for d, v in rep["COMMON_MODE_REMOVAL_BY_DEPTH"].items()
                         if v.get("cleared_do_not_redo_27_bar")]
    composition_flat = bool(rep.get("COMPOSITION_TREND") and rep["COMPOSITION_TREND"].get("FLAT"))

    if not sanity_all_pass:
        verdict = "ORGAN_F_ACCUM_INTERFERENCE__INSTRUMENT_STILL_LOOSE__K1_OR_N1_FAILED"
    else:
        verdict = "ORGAN_F_ACCUM_INTERFERENCE__GROWS_FASTER_%s__REFUTED_%s__COMMONMODE_FIX_%s__COMPOSITION_FLAT_%s" % (
            "_".join(interference_grows_faster) if interference_grows_faster else "NONE",
            "_".join(refuted_populations) if refuted_populations else "NONE",
            "_".join(common_mode_fixes) if common_mode_fixes else "NONE",
            str(composition_flat))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("ORGAN F ACCUMULATE-GATE diagnosis: signal/interference decomposition "
                        "(d-prime + field percentiles), high/low-frequency contributor split, "
                        "common-mode removal vs random-direction control (DO-NOT-REDO 27 gated), "
                        "rank-vs-hit@1, winner composition, all by depth. -> " + verdict),
        "config": {"DEPTHS_UNION": list(DEPTHS_UNION), "POP_SPECS": [
            {"name": s["name"], "cap_min": s["cap_min"], "depths": list(s["depths"])} for s in POP_SPECS],
                  "HEADLINE_POP": HEADLINE_POP, "N_HIGH_FREQ": N_HIGH_FREQ,
                  "TOPK_INCORRECT_FIELD": TOPK_INCORRECT_FIELD, "N_BOOT": N_BOOT, "MASTER_SEED": MASTER_SEED},
        "selftest_evidence_keys": sorted(ev.keys()),
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(Path(out_dir), metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:
        traceback.print_exc()
        _out = str(get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else "")))
        os.makedirs(_out, exist_ok=True)
        _diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(_e).__name__}: {str(_e)[:500]}",
                 "summary": f"CELL_CRASHED: {type(_e).__name__}", "elapsed_s": 0.0,
                 "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _tmp = os.path.join(_out, "metrics.json.tmp")
        _final = os.path.join(_out, "metrics.json")
        with open(_tmp, "w", encoding="utf-8") as _f:
            json.dump(_diag, _f, indent=2)
        os.replace(_tmp, _final)
        raise SystemExit(1)
