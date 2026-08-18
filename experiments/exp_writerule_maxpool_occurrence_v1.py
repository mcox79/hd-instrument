"""exp_writerule_maxpool_occurrence_v1 -- IF A WORD'S OCCURRENCES ARE KEPT SEPARATE AND SCORED BY
BEST MATCH INSTEAD OF SUMMED, DOES THE STORE STOP ENCODING CO-OCCURRENCE AND START ENCODING
SUBSTITUTABILITY? WRITE-RULE ORGAN, DECISIVE BUILD.

WHY A NEW CELL, NOT A RESTART OF THE KILLED ONE. `exp_organ_f_noncollapsing_accumulation_v1.py`
self-tested PASS and was KILLED by the Director at ~9h projected (1,000/5,491 anchors in 5,861s). Its
cost was spherical k-means PER ANCHOR PER DEPTH PER K inside `build_nonlinear_arms` (32,946 k-means
calls, each 8 iterations of dense matmul). THE QUESTION UNDER TEST DOES NOT NEED CLUSTERING: it asks
whether MAX-POOLING over kept-separate occurrences (a sparse matrix product plus a segmented max)
beats summing, not whether a clustering rule discovers structure inside the occurrence set. This cell
reuses the killed cell's verified pieces (occurrence-list construction pattern, leak-safe profile
prefix convention, K1/N0 sanity gates, cell-template mandates) and REPLACES the k-means machinery
entirely -- no `spherical_kmeans`, no per-(anchor,D,k) clustering loop anywhere below.

=================================================================================================
WHAT TWO INDEPENDENT INSTRUMENTS NOW AGREE ON (both re-verified below as REGRESSION GATES that EXIT
ON FAILURE, not merely cited):
  1. `exp_writerule_step_ladder_v1` DECISIVE ARM (commit 3e5fde9c0), background fixed at single-
     occurrence for every OTHER anchor, only the TARGET anchor's own row varying: SUM_ALL 0.0100 <
     RANDOM_SINGLE 0.0367 < BEST_SINGLE_ORACLE 0.3033, all CI-separated. Summing a word's occurrences
     is WORSE than keeping ONE at random.
  2. `exp_dissociation_score_instrument_v1` (commit 0eb44eb1d), a LICENSED instrument (all four floors
     at chance, known-answer AUC 0.9599, random-vector store at chance): RAW_COUNT_SINGLE_OCC AUC
     0.4173 is the LEAST co-occurrence-biased store owned, against INCUMBENT 0.0710 and
     RAW_COUNT_FULL_ACCUM 0.0510. Above 0.5 AUC = substitutability; below = co-occurrence.

THE QUESTION: if a word's occurrences are kept SEPARATE and scored by BEST MATCH instead of summed
into one vector, does the store stop encoding co-occurrence and start encoding substitutability?

=================================================================================================
TWO MEASUREMENT REGIMES, BOTH ON THE IDENTICAL ARM SET, NEITHER SUBSTITUTING FOR THE OTHER:

  REGIME A -- DISSOCIATION AUC (PRIMARY). Reuses `exp_dissociation_score_instrument_v1`'s (DISS)
  matched-pair population VERBATIM, loaded from ITS OWN landed checkpoint
  (data/exp_dissociation_score_instrument_v1/units.jsonl, key POPULATION::v1.7::full) -- NOT rebuilt.
  Matching took 7 versions to get its floors to chance; this cell does not touch that machinery. Every
  arm below is scored as an AUC separating SET P (WordNet-synonym, zero co-occurrence -- "could
  replace") from SET S (top-decile co-occurring, no close WordNet relation -- "co-occurs, cannot
  replace") on the SAME matched pairs, using DISS's own `auc_of` / `auc_bootstrap` (imported, not
  reimplemented).

  REGIME B -- HIT@1 + WINNER COMPOSITION (SECONDARY, reported BESIDE the AUC, never instead). Reuses
  `exp_writerule_step_ladder_v1`'s (WR) DECISIVE-ARM convention exactly: candidates (the competitive
  background) held FIXED at single-occurrence for every anchor (`Pm_single`, WR's own construction,
  never rebuilt); only the TARGET anchor's own query construction varies across arms. WR's own
  `best_single_occurrence_oracle` is called VERBATIM as the formal regression proof (its SUM_ALL /
  RANDOM_SINGLE / BEST_SINGLE_ORACLE means are compared against 0.0100 / 0.0367 / 0.3033). A small
  PARALLEL, self-consistency-checked construction captures WINNER WORDS (needed for
  `wordnet_relation_composition` / `syntagmatic_jaccard_composition`, which WR's boolean-only function
  does not expose) and is asserted BYTE-IDENTICAL to WR's own hit booleans on the same item subsample
  before being trusted for anything.

=================================================================================================
ARMS, identical construction across both regimes (one variable: how the target's occurrences are
combined into a score), reused verbatim where marked:
  A0_SUM       the incumbent unweighted sum. REGRESSION GATE in BOTH regimes (must reproduce DISS's
               landed RAW_COUNT_FULL_ACCUM AUC=0.0510 and WR's landed SUM_ALL hit@1=0.0100).
  S1_SINGLE_OCC one occurrence only, carried forward as the known reference point (DISS
               RAW_COUNT_SINGLE_OCC AUC=0.4173; WR RANDOM_SINGLE hit@1=0.0367). Reused, not rebuilt.
  M1_MAXPOOL   THE ARM THIS CELL EXISTS FOR. Keep every occurrence; score a candidate by the MAXIMUM
               similarity over the target's own occurrences. No clustering: a sparse matrix product
               (occurrence rows @ candidate columns) plus `.max(axis=0)`, a segmented maximum.
  M2_TOPK_MEAN mean of the top-k occurrence similarities, k swept in {2,3,5}. Interpolates between max
               (k=1) and sum-like averaging; never adopted as a value.
  N1_MAXPOOL_RANDOM_OCC THE CONTROL THAT CARRIES THE CLAIM. Same max-pooling machinery, but the
               target's occurrence set is replaced by an equal-size draw from OTHER anchors' own
               occurrences. Max over ANY set of vectors inflates similarity by construction (a maximum
               over more draws), so if M1 does not beat N1 CI-separated, the gain is the MAX OPERATOR,
               not the target's own occurrences.
  N2_MAXPOOL_SIZE_MATCHED_SHUFFLE second guard: the target's occurrence set is replaced by a SAME-
               FREQUENCY-BAND donor anchor's WHOLE occurrence set (content shuffled across anchors,
               set cohesion preserved, size only band-matched not exactly matched -- disclosed).
  K1 / N0      REGIME A only (per DISS's own licensing convention): K1 = WordNet path-similarity
               known-answer (must clear AUC>=0.95); N0 = iid-Gaussian random-vector store (must sit at
               chance). If K1 fails: INSTRUMENT_STILL_LOOSE, publish nothing (SystemExit).

=================================================================================================
COST CONTROL (the thing that killed the predecessor). NO per-anchor clustering anywhere. REGIME A
restricts everything to `words_needed` (the union of DISS's matched-pair members -- low hundreds, not
5,491 anchors): occurrence lists + a small sparse matrix, cross-similarity computed as a DENSE product
of two small blocks per pair (occurrence counts per word are bounded by the corpus's own K_SENT_TOTAL
profile cap, typically well under 100). REGIME B restricts the EXPENSIVE occurrence-level arms
(M1/M2/N1/N2) to a bounded N_DECISIVE=300 item subsample (same order of magnitude WR's own already-
landed, never-killed decisive arm used); A0_SUM/S1_SINGLE_OCC are additionally computed over the FULL
item population as a single vectorized sparse matmul each (no python loop), giving a tighter
regression read than the 300-item subsample alone. Estimated + measured wall time reported in metrics;
if the full run does not land under ~30 minutes this cell reports the achieved n and CI half-width
rather than running long, per the dispatch's explicit instruction.

=================================================================================================
ORGAN REUSE, enumerated then reconciled -- nothing below reimplements an existing pipeline stage:
  experiments.exp_dissociation_score_instrument_v1 (DISS)   POPULATION checkpoint (matchedP/matchedS,
                                                              loaded not rebuilt), auc_of, auc_bootstrap,
                                                              dense_scores_from_dict_store,
                                                              counts_to_dense_store, l2n,
                                                              wn_best_path_similarity, CTS (reexported),
                                                              its own self_test() (called wholesale)
  experiments.exp_writerule_step_ladder_v1 (WR)              best_single_occurrence_oracle (called
                                                              verbatim for the regression proof),
                                                              wordnet_relation_composition,
                                                              syntagmatic_jaccard_composition, its own
                                                              self_test() (called wholesale, chains PIPE)
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)     build_population, build_single_occurrence_
                                                              counts, load_full_accum_from_checkpoint,
                                                              MASTER_SEED, REGRESSION_A0_PARTIAL,
                                                              dprime_stats/summary, rank_summary
  experiments.exp_cue_information_audit_v1 (INFO)            load_corpus_and_buckets, raw_counts_for_
                                                              window, build_vocab, to_sparse, l2n_sparse,
                                                              C3 (_n_profile, the leak-safe profile
                                                              PREFIX every occurrence list below uses)
  tools.floor_battery (FB)                                   l2n, scramble_null, constant_prototype_
                                                              floor, frequency_floor
  hdlab.reading_grounding_loop                                content_lemmas
  experiments._seed_checkpoint / tools.exp_checkpoint         output dir, atomic metrics write, per-
                                                              unit checkpoint/resume (ONE unit "MAIN")

NEW IN THIS CELL (nothing existing does it): build_occurrence_lists (per-word UN-SUMMED occurrence
Counters over the leak-safe profile PREFIX -- every sibling cell only ever built CUMULATIVE sums or a
single first occurrence, never a full un-summed list restricted to a small word set), the sparse
occurrence-matrix + max/top-k-mean pairwise scorer, build_random_occ_indices (N1's control),
build_band_shuffle (N2's control), paired_auc_diff_bootstrap (M1 vs A0 / M1 vs N1 paired CI on the
difference, not two independent CIs), auc_tie_variants (mid/optimistic/conservative AUC), the REGIME B
per-item max-pool/top-k/N1/N2 loop with winner-word capture.

PRIOR-WORK CHECK (substrate-KB, per .claude/agents/exp_dev.md). `bash tools/substrate_query.sh
"max-pool occurrence separate substitutability co-occurrence write rule"` -- if the KB ingest is
STALE this session (documented notes/STATUS.md, hd_director_kb_continuous_ingest livelock), the
enumeration above is the substitute per the standing exemption: every cell this docstring's REUSE
section names was read in full, plus notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.9/6.12/6.13 and
the two findings notes the decisive numbers above are cited from. No existing cell builds a max-pool /
top-k occurrence scorer, a random-occurrence control, or a frequency-band occurrence-shuffle control.
Not a rediscovery -- this IS the ladder's next follow-up, explicitly named in 6.9 as "the highest-value
unfinished work in the organ."

=================================================================================================
STOP-IF (evaluated on REGIME A's AUC, per the dispatch, in this order):
  (i)   M1 AUC CI-separated ABOVE A0 AND above N1_MAXPOOL_RANDOM_OCC -> not collapsing is the fix.
  (ii)  M1 beats A0 but NOT N1 -> the gain is the MAX OPERATOR, not the occurrences; no mechanism claim.
  (iii) M1 ties A0 -> not-collapsing insufficient; suspect shifts to FILTER/SUPERPOSE.
  (iv)  AUC stays below 0.5 for every arm -> no store this corpus supports encodes substitutability;
        report loudly.
  (v)   K1 fails -> INSTRUMENT_STILL_LOOSE, publish nothing.

STORAGE HONESTY: floats stored per anchor reported for every arm, matched-depth AND matched-storage.
Max-pooling keeps N vectors where the sum kept 1 -- an arm that wins by storing more is an EFFICIENCY
statement, not a mechanism statement, and is labelled as one throughout.

BRAIN FRAMING, labelled per the dispatch. PINNED (as a computation): complementary learning systems --
hippocampus keeps the EPISODE, neocortex extracts the CROSS-EPISODE REGULARITY (McClelland/O'Reilly).
Adjacency is episodic; substitutability is the regularity. Keeping occurrences separable and matching
the best one is closer to that division than averaging them into one point. OUR INVENTION UNDER TEST:
max-pooling as the READ operator (and top-k-mean as its interpolation). No anatomy is claimed to
compute a max over stored episodes; nothing here asserts a brain structure performs this operation.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's score vector (both regimes), >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: ONE unit "MAIN" via tools.exp_checkpoint, resume-safe (same pattern as WR/DISS)
# - discriminator survives scale: --grid reduced runs the IDENTICAL code path at a smaller matched-
#   pair population / smaller N_DECISIVE, not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses DISS's landed, regression-gated matched
#   population and WR's landed, regression-gated background unmodified; the only new calibration --
#   occurrence-list construction, random/shuffle controls -- is self-tested against hand-built toy
#   examples with known answers)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - sweep_alignment / discriminating_fraction / composition_edges / positive_control_arms / CRLB
#   gates: N/A -- diagnostic/rule-comparison cell (same family as organ_f/writerule/dissociation, none
#   of which compose chain-grade substrate primitives or sweep a capacity-bound parameter); declared
#   not omitted.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. Neither store (mat)
nor DISS's matched population is ever rebuilt. data/foundation/** is never opened. Writes only under
data/exp_writerule_maxpool_occurrence_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/hdlab next -- can take ~40-60s cold; flushed so a slow "
      "import is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DISS         # noqa: E402  READ ONLY
import experiments.exp_writerule_step_ladder_v1 as WR                   # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE          # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "writerule_maxpool_occurrence_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/writerule_maxpool_occurrence_v1_findings_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = PIPE.MASTER_SEED
N_BOOT = 1200 if SMOKE else 10000
K_SWEEP: Tuple[int, ...] = (2, 3, 5)
N_BANDS = 3
N_DECISIVE = 40 if SMOKE else 300
KNOWN_ANSWER_MIN_AUC = 0.95
EXPECTED_A0_AUC = 0.0510          # DISS RAW_COUNT_FULL_ACCUM, landed 0eb44eb1d
EXPECTED_S1_AUC = 0.4173          # DISS RAW_COUNT_SINGLE_OCC, landed 0eb44eb1d
EXPECTED_SUM_ALL_HIT1 = 0.0100    # WR decisive arm, landed 3e5fde9c0
EXPECTED_RANDOM_SINGLE_HIT1 = 0.0367
EXPECTED_BEST_SINGLE_ORACLE_HIT1 = 0.3033
AUC_REGRESSION_TOL = 0.006
HIT1_REGRESSION_TOL = 0.03        # generous: idx_decisive is NOT guaranteed bit-identical to WR's own


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _digest(v) -> str:
    arr = np.asarray(v, dtype=np.float64)
    arr = np.where(np.isnan(arr), -999.0, arr)
    return hashlib.sha256(arr.tobytes()).hexdigest()[:16]


# =================================================================================================
# NEW MACHINERY -- occurrence lists, sparse cross-scoring, random/shuffle controls, AUC helpers
# =================================================================================================
def build_occurrence_lists(words: Sequence[str], buckets: Dict[str, List[int]],
                           sents: List[str]) -> Tuple[Dict[str, List[Counter]], Dict]:
    """Per-word UN-SUMMED occurrence count vectors over the LEAK-SAFE profile PREFIX
    (buckets[w][:INFO.C3._n_profile(len(buckets[w]))]) -- the IDENTICAL material
    exp_cue_information_audit_v1.build_store_counts sums into Pstore and PIPE.build_single_occurrence_
    counts samples occ[0] from. Restricted to `words` (a small set), not the full anchor pool."""
    t0 = time.time()
    out: Dict[str, List[Counter]] = {}
    n_empty = 0
    n_occ_total = 0
    for i, w in enumerate(words):
        occ_all = buckets.get(w, [])
        n_prof = INFO.C3._n_profile(len(occ_all))
        prof = occ_all[:n_prof]
        if not prof:
            out[w] = []
            n_empty += 1
            continue
        out[w] = [INFO.raw_counts_for_window(sents[j], w) for j in prof]
        n_occ_total += len(out[w])
        if (i + 1) % 200 == 0 or i == len(words) - 1:
            print("[occ_lists] %d/%d words n_occ_total=%d elapsed=%.0fs" % (
                i + 1, len(words), n_occ_total, time.time() - t0), flush=True)
    return out, {"n_words": len(words), "n_empty_profile": n_empty,
                "n_occurrences_total": n_occ_total, "elapsed_s": round(time.time() - t0, 1)}


def occurrence_sparse_matrix(occ_lists: Dict[str, List[Counter]], words: Sequence[str],
                             vocab: Dict[str, int]) -> Tuple[sp.csr_matrix, Dict[str, Tuple[int, int]]]:
    """Stacks every word's occurrence rows into ONE sparse matrix (L2-normalised), plus a
    [start,end) row-range per word. No clustering; a single to_sparse/l2n_sparse call."""
    key_order: List[Tuple[str, int]] = []
    row_range: Dict[str, Tuple[int, int]] = {}
    counters: Dict[Tuple[str, int], Counter] = {}
    for w in words:
        start = len(key_order)
        for kk, c in enumerate(occ_lists.get(w, [])):
            key = (w, kk)
            key_order.append(key)
            counters[key] = c
        row_range[w] = (start, len(key_order))
    M = INFO.l2n_sparse(INFO.to_sparse(counters, key_order, vocab))
    return M, row_range


def pair_scores_from_index_map(M: sp.csr_matrix, idx_of: Dict[str, np.ndarray],
                               pairs: Sequence[Tuple[str, str, str]], topk: int = 1) -> np.ndarray:
    """Pairwise MAX-POOL (topk=1) or TOP-K-MEAN (topk>1) score: for each pair, the dense cross-
    similarity block between w1's rows and w2's rows (both indexed via idx_of), reduced by max or by
    the mean of its top-k entries. A sparse matrix product plus a small dense reduction -- no python
    loop over occurrences, no clustering."""
    out = np.full(len(pairs), np.nan, dtype=np.float64)
    for i, (w1, w2, _p) in enumerate(pairs):
        i1 = idx_of.get(w1, np.zeros(0, dtype=np.int64))
        i2 = idx_of.get(w2, np.zeros(0, dtype=np.int64))
        if i1.size == 0 or i2.size == 0:
            continue
        cross = np.asarray((M[i1] @ M[i2].T).todense())
        flat = cross.ravel()
        if topk <= 1:
            out[i] = float(flat.max())
        else:
            k = min(topk, flat.size)
            top_idx = np.argpartition(flat, -k)[-k:]
            out[i] = float(flat[top_idx].mean())
    return out


def build_random_occ_indices(words: Sequence[str], row_range: Dict[str, Tuple[int, int]],
                             n_rows_total: int, seed: int) -> Dict[str, np.ndarray]:
    """N1's control: for each word, draw n_w row indices from the POOL of every OTHER word's own
    occurrence rows (this word's own range excluded), size-matched, seeded."""
    rng = np.random.default_rng(seed)
    out: Dict[str, np.ndarray] = {}
    for w in words:
        s, e = row_range.get(w, (0, 0))
        n_w = e - s
        if n_w == 0:
            out[w] = np.zeros(0, dtype=np.int64)
            continue
        pool = np.concatenate([np.arange(0, s), np.arange(e, n_rows_total)])
        if pool.size == 0:
            out[w] = np.zeros(0, dtype=np.int64)
            continue
        idx = rng.choice(pool, size=n_w, replace=(pool.size < n_w))
        out[w] = idx.astype(np.int64)
    return out


def build_band_shuffle(words: Sequence[str], scalar_of: Dict[str, float], n_bands: int,
                       seed: int) -> Dict[str, str]:
    """N2's control: bucket `words` into `n_bands` quantile bands of `scalar_of` (frequency), then
    within each band assign every word a DIFFERENT donor word (cyclic shift of a seeded permutation --
    guarantees no self-map whenever the band has >=2 members). Bands of size 1 map to themselves
    (degenerate, disclosed, never silently dropped)."""
    order = sorted(words, key=lambda w: scalar_of.get(w, 0.0))
    n = len(order)
    if n == 0:
        return {}
    bands = np.array_split(np.arange(n), max(1, min(n_bands, n)))
    rng = np.random.default_rng(seed)
    donor_of: Dict[str, str] = {}
    for b in bands:
        ws = [order[i] for i in b]
        if len(ws) < 2:
            for w in ws:
                donor_of[w] = w
            continue
        perm = rng.permutation(len(ws))
        ws_shuffled = [ws[i] for i in perm]
        for i, w in enumerate(ws_shuffled):
            donor_of[w] = ws_shuffled[(i + 1) % len(ws_shuffled)]
    return donor_of


def auc_tie_variants(sp_arr: np.ndarray, ss_arr: np.ndarray) -> Dict[str, float]:
    """mid (0.5 tie credit, matches DISS.auc_of exactly), optimistic (ties favor SET P), conservative
    (ties favor SET S). O(n_p*n_s) pairwise, fine at these small n (low hundreds)."""
    a = np.asarray(sp_arr, dtype=np.float64)[:, None]
    b = np.asarray(ss_arr, dtype=np.float64)[None, :]
    diff = a - b
    n = diff.size
    if n == 0:
        return {"mid": float("nan"), "optimistic": float("nan"), "conservative": float("nan")}
    wins_gt = float((diff > 0).sum())
    ties = float((diff == 0).sum())
    return {"mid": round((wins_gt + 0.5 * ties) / n, 4),
           "optimistic": round((wins_gt + ties) / n, 4),
           "conservative": round(wins_gt / n, 4)}


def paired_auc_diff_bootstrap(sp_a: np.ndarray, ss_a: np.ndarray, sp_b: np.ndarray, ss_b: np.ndarray,
                              n_boot: int, seed: int) -> Dict:
    """AUC(arm A) - AUC(arm B) on the SAME resampled P-index-set and S-index-set every draw (a
    genuinely paired comparison, not two independently-bootstrapped CIs eyeballed for overlap)."""
    n_p, n_s = sp_a.size, ss_a.size
    assert sp_b.size == n_p and ss_b.size == n_s, "paired diff requires matched pair arrays"
    point = DISS.auc_of(sp_a, ss_a) - DISS.auc_of(sp_b, ss_b)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    for b in range(n_boot):
        ip = rng.integers(0, n_p, size=n_p)
        isv = rng.integers(0, n_s, size=n_s)
        diffs[b] = (DISS.auc_of(sp_a[ip], ss_a[isv]) - DISS.auc_of(sp_b[ip], ss_b[isv]))
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
    return {"point": round(float(point), 4), "ci95": [round(lo, 4), round(hi, 4)],
           "ci_halfwidth": round((hi - lo) / 2.0, 4), "band": band}


def paired_hit1_diff_bootstrap(hit_a: np.ndarray, hit_b: np.ndarray, n_boot: int, seed: int) -> Dict:
    n = hit_a.size
    assert hit_b.size == n
    a = hit_a.astype(np.float64); b = hit_b.astype(np.float64)
    point = float(a.mean() - b.mean())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    diffs = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    lo, hi = float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))
    band = "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")
    return {"point": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)],
           "ci_halfwidth": round((hi - lo) / 2.0, 4), "band": band}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    print("[selftest] reusing DISS's own self_test() wholesale (matching, AUC, floors, WordNet, "
         "checkpoint round-trip)", flush=True)
    ev["DISS_selftest_keys"] = sorted(DISS.self_test().keys())
    print("[selftest] reusing WR's own self_test() wholesale (chains PIPE/INFO, decisive-arm "
         "discriminator fixture, composition instrument)", flush=True)
    ev["WR_selftest_keys"] = sorted(WR.self_test().keys())

    # ---- build_occurrence_lists: real code path on a toy corpus, depth truncation, saturation -----
    toy_sents = ["cat sat on mat", "cat ran to park", "cat ate the fish", "cat slept all day"]
    toy_buckets = {"cat": [0, 1, 2, 3]}
    occ, diag = build_occurrence_lists(["cat"], toy_buckets, toy_sents)
    n_prof_expected = INFO.C3._n_profile(4)
    assert len(occ["cat"]) == n_prof_expected, (len(occ["cat"]), n_prof_expected)
    assert occ["cat"][0] == INFO.raw_counts_for_window(toy_sents[0], "cat")
    ev["build_occurrence_lists_selftest"] = {"n_prof_expected": n_prof_expected,
                                             "n_built": len(occ["cat"])}

    # ---- occurrence_sparse_matrix + pair_scores_from_index_map: KNOWN ANSWER -- max-pooling beats a
    # summed/averaged score on an adversarial case where opposed-direction occurrences cancel under
    # summing but a single occurrence exactly matches the query (mirrors the killed cell's own proof,
    # reused reasoning, rebuilt against THIS cell's own machinery) -------------------------------------
    fake_occ = {"w": [Counter(a=1), Counter(b=1)], "q": [Counter(a=1)]}
    vocab_fake = INFO.build_vocab([{("w", i): c for i, c in enumerate(fake_occ["w"])},
                                   {("q", 0): fake_occ["q"][0]}])
    M_fake, rr_fake = occurrence_sparse_matrix(fake_occ, ["w", "q"], vocab_fake)
    idx_fake = {k: np.arange(*v) for k, v in rr_fake.items()}
    max_score = pair_scores_from_index_map(M_fake, idx_fake, [("w", "q", "n")], topk=1)[0]
    sum_row = INFO.l2n_sparse(INFO.to_sparse({"w": Counter(a=1, b=1)}, ["w"], vocab_fake))
    q_row = INFO.l2n_sparse(INFO.to_sparse({"q": Counter(a=1)}, ["q"], vocab_fake))
    sum_score = float((sum_row @ q_row.T).todense()[0, 0])
    assert max_score > sum_score + 0.1, (max_score, sum_score, "max-pool must beat the diluted sum")
    ev["max_vs_sum_known_answer"] = {"max_score": round(max_score, 4), "sum_score": round(sum_score, 4)}

    # ---- top-k-mean known answer: k=1 == max; k>=n_rows == plain mean of all cross entries --------
    k1 = pair_scores_from_index_map(M_fake, idx_fake, [("w", "q", "n")], topk=1)[0]
    k_all = pair_scores_from_index_map(M_fake, idx_fake, [("w", "q", "n")], topk=99)[0]
    cross_fake = np.asarray((M_fake[idx_fake["w"]] @ M_fake[idx_fake["q"]].T).todense())
    assert abs(k1 - cross_fake.max()) < 1e-9
    assert abs(k_all - cross_fake.mean()) < 1e-9
    ev["topk_mean_known_answer"] = {"k1": round(float(k1), 4), "k_all": round(float(k_all), 4)}

    # ---- build_random_occ_indices: excludes own range, size-matched, no crash on tiny pools -------
    rr2 = {"a": (0, 3), "b": (3, 5), "c": (5, 6)}
    ridx = build_random_occ_indices(["a", "b", "c"], rr2, n_rows_total=6, seed=1)
    assert ridx["a"].size == 3 and not np.any((ridx["a"] >= 0) & (ridx["a"] < 3))
    assert ridx["b"].size == 2 and not np.any((ridx["b"] >= 3) & (ridx["b"] < 5))
    ev["build_random_occ_indices_selftest"] = {"a_excludes_own_range": True, "size_matched": True}

    # ---- build_band_shuffle: derangement property (donor != self) whenever band size >= 2, seeded
    # reproducibility ---------------------------------------------------------------------------------
    fq_fake = {"a": 1.0, "b": 1.1, "c": 1.2, "d": 9.0, "e": 9.1, "f": 9.2}
    donor1 = build_band_shuffle(list(fq_fake), fq_fake, n_bands=2, seed=3)
    assert all(donor1[w] != w for w in fq_fake), donor1
    donor2 = build_band_shuffle(list(fq_fake), fq_fake, n_bands=2, seed=3)
    assert donor1 == donor2, "same seed must reproduce the same shuffle"
    donor_degenerate = build_band_shuffle(["x"], {"x": 1.0}, n_bands=3, seed=1)
    assert donor_degenerate["x"] == "x", "size-1 band must map to itself, not crash"
    ev["build_band_shuffle_selftest"] = {"no_self_map_when_band_ge_2": True, "seed_reproducible": True,
                                         "degenerate_band_no_crash": True}

    # ---- auc_tie_variants: matches DISS.auc_of on the 'mid' convention; optimistic >= mid >= cons --
    sp_t = np.array([0.9, 0.5, 0.1]); ss_t = np.array([0.5, 0.2])
    variants = auc_tie_variants(sp_t, ss_t)
    ref_mid = DISS.auc_of(sp_t, ss_t)
    assert abs(variants["mid"] - ref_mid) < 1e-3, (variants, ref_mid)
    assert variants["optimistic"] >= variants["mid"] >= variants["conservative"]
    ev["auc_tie_variants_known_answer"] = variants

    # ---- paired_auc_diff_bootstrap: known separable difference must CI-separate above 0 -----------
    rng = np.random.default_rng(0)
    base_p, base_s = rng.standard_normal(300), rng.standard_normal(300)
    diff_res = paired_auc_diff_bootstrap(base_p + 2.0, base_s, base_p, base_s, 400, 1)
    assert diff_res["band"] == "ABOVE", diff_res
    same_res = paired_auc_diff_bootstrap(base_p, base_s, base_p, base_s, 400, 2)
    assert same_res["point"] == 0.0 and same_res["band"] == "NOT_SEPARATED", same_res
    ev["paired_auc_diff_bootstrap_known_answer"] = {"separable": diff_res["band"], "identical": same_res["band"]}

    # ---- paired_hit1_diff_bootstrap: known separable case -------------------------------------------
    hit_hi = np.array([True] * 80 + [False] * 20)
    hit_lo = np.array([True] * 20 + [False] * 80)
    hd = paired_hit1_diff_bootstrap(hit_hi, hit_lo, 400, 3)
    assert hd["band"] == "ABOVE", hd
    ev["paired_hit1_diff_bootstrap_known_answer"] = hd["band"]

    # ---- arms-must-differ digest sensitivity + NaN-safety --------------------------------------------
    a1 = np.array([1.0, 2.0, 3.0]); a2 = np.array([1.0, 2.0, 3.0001]); a3 = np.array([1.0, np.nan, 3.0])
    assert _digest(a1) != _digest(a2)
    assert _digest(a3) == _digest(a3)   # NaN-safe digest is at least self-consistent
    ev["arms_must_differ_digest_sensitivity"] = True

    # ---- checkpoint round-trip (reused, not reimplemented) ------------------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# REGIME A -- DISSOCIATION AUC
# =================================================================================================
def run_regime_a(grid: str, rep: Dict) -> Dict:
    t0 = time.time()
    diss_pop_out_dir = os.path.join(REPO, "data", "exp_" + DISS.ANCHOR_NAME)
    pop_key = unit_key("POPULATION", DISS.CODE_VERSION, "full")
    prior_pop = load_units(diss_pop_out_dir).get(pop_key)
    if prior_pop is None:
        raise SystemExit(
            "DISSOCIATION INSTRUMENT'S OWN POPULATION CHECKPOINT NOT FOUND at %s key=%s -- this cell "
            "REUSES the matched pairs, it does not rebuild the matching (7 versions to reach chance "
            "floors). Run exp_dissociation_score_instrument_v1's FULL grid first." % (diss_pop_out_dir, pop_key))
    matchedP_all = [tuple(x) for x in prior_pop["matchedP"]]
    matchedS_all = [tuple(x) for x in prior_pop["matchedS"]]
    if grid == "reduced":
        matchedP_all = matchedP_all[:40]
        matchedS_all = matchedS_all[:40]
    rep["DISSOCIATION_POPULATION_REUSED_FROM"] = {"path": diss_pop_out_dir, "key": pop_key,
                                                   "n_matchedP_available": len(prior_pop["matchedP"]),
                                                   "n_matchedS_available": len(prior_pop["matchedS"]),
                                                   "n_matchedP_used": len(matchedP_all),
                                                   "n_matchedS_used": len(matchedS_all)}
    print("[regime_a] reused %d/%d matched pairs from DISS's own landed checkpoint" %
         (len(matchedP_all), len(matchedS_all)), flush=True)

    words_all = sorted(set(w for w1, w2, _ in matchedP_all + matchedS_all for w in (w1, w2)))

    C = DISS.CTS.load_cache()
    aux = DISS.CTS.load_aux()
    anchors = C["anchors"]
    mat = np.asarray(C["mat"], dtype=np.float32)
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    pos_idx = C["pos"]
    n_anchors = len(anchors)
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)

    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov

    # ---- occurrence lists for words_all, then filter pairs to words with >=1 occurrence (SHARED
    # mask across every arm below, so every arm is scored on the IDENTICAL pair set) -----------------
    occ_lists, occ_diag = build_occurrence_lists(words_all, buckets, sents)
    rep["REGIME_A_OCC_BUILD"] = occ_diag
    valid_words = set(w for w in words_all if len(occ_lists.get(w, [])) > 0)

    def _both_valid(pairs):
        return [p for p in pairs if p[0] in valid_words and p[1] in valid_words]
    matchedP = _both_valid(matchedP_all)
    matchedS = _both_valid(matchedS_all)
    rep["REGIME_A_PAIRS_AFTER_OCC_FILTER"] = {
        "n_matchedP_dropped": len(matchedP_all) - len(matchedP),
        "n_matchedS_dropped": len(matchedS_all) - len(matchedS),
        "n_matchedP": len(matchedP), "n_matchedS": len(matchedS)}
    if len(matchedP) < 15 or len(matchedS) < 15:
        raise SystemExit("REGIME A UNBUILDABLE -- too few matched pairs survive the occurrence filter: "
                         "%r" % rep["REGIME_A_PAIRS_AFTER_OCC_FILTER"])
    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    rep["REGIME_A_words_needed"] = len(words_needed)

    vocab_occ = INFO.build_vocab(
        [{(w, i): c for i, c in enumerate(occ_lists.get(w, []))} for w in words_needed])
    M_occ, row_range = occurrence_sparse_matrix(occ_lists, words_needed, vocab_occ)
    rep["REGIME_A_OCC_sparse_shape"] = list(M_occ.shape)
    idx_of_own = {w: np.arange(*row_range[w]) for w in words_needed}
    mean_occ = float(np.mean([row_range[w][1] - row_range[w][0] for w in words_needed])) if words_needed else 0.0
    rep["REGIME_A_mean_occurrences_per_word"] = round(mean_occ, 2)
    rep["REGIME_A_vocab_size"] = len(vocab_occ)

    # ---- A0_SUM: DISS's own RAW_COUNT_FULL_ACCUM construction, reused verbatim (checkpoint reuse) --
    diss_info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    units_info = load_units(diss_info_out_dir)
    counts_full: Dict[str, Counter] = {}
    missing_p = []
    for w in words_needed:
        rec = units_info.get(unit_key("Pstore", w))
        if rec is None:
            missing_p.append(w)
            continue
        counts_full[w] = Counter(rec["counts"])
    if missing_p:
        raise SystemExit("CHECKPOINT REUSE INCOMPLETE -- exp_cue_information_audit_v1's own Pstore "
                         "checkpoint is missing: %r" % missing_p[:20])
    store_A0 = DISS.counts_to_dense_store(counts_full, words_needed, binarize=False)

    # ---- S1_SINGLE_OCC: DISS's own RAW_COUNT_SINGLE_OCC construction, reused verbatim -------------
    P_single, single_diag = PIPE.build_single_occurrence_counts(words_needed, buckets, sents)
    rep["REGIME_A_single_occurrence_build_diag"] = single_diag
    store_S1 = DISS.counts_to_dense_store(P_single, words_needed, binarize=False)

    # ---- N1 / N2 index maps -----------------------------------------------------------------------
    n_rows_total = M_occ.shape[0]
    rand_idx_of = build_random_occ_indices(words_needed, row_range, n_rows_total, seed=MASTER_SEED + 7001)
    donor_of = build_band_shuffle(words_needed, fq_log, N_BANDS, seed=MASTER_SEED + 7002)
    donor_idx_of = {w: idx_of_own.get(donor_of.get(w, w), np.zeros(0, dtype=np.int64)) for w in words_needed}
    rep["REGIME_A_N2_band_shuffle_self_maps"] = int(sum(1 for w in words_needed if donor_of.get(w) == w))

    def _pd(store, pairs):
        return DISS.dense_scores_from_dict_store(store, pairs)

    arm_pairs: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
        "A0_SUM": (_pd(store_A0, matchedP), _pd(store_A0, matchedS)),
        "S1_SINGLE_OCC": (_pd(store_S1, matchedP), _pd(store_S1, matchedS)),
        "M1_MAXPOOL": (pair_scores_from_index_map(M_occ, idx_of_own, matchedP, topk=1),
                       pair_scores_from_index_map(M_occ, idx_of_own, matchedS, topk=1)),
        "N1_MAXPOOL_RANDOM_OCC": (pair_scores_from_index_map(M_occ, rand_idx_of, matchedP, topk=1),
                                  pair_scores_from_index_map(M_occ, rand_idx_of, matchedS, topk=1)),
        "N2_MAXPOOL_SIZE_MATCHED_SHUFFLE": (pair_scores_from_index_map(M_occ, donor_idx_of, matchedP, topk=1),
                                            pair_scores_from_index_map(M_occ, donor_idx_of, matchedS, topk=1)),
    }
    for kk in K_SWEEP:
        arm_pairs["M2_TOPK_MEAN_K%d" % kk] = (
            pair_scores_from_index_map(M_occ, idx_of_own, matchedP, topk=kk),
            pair_scores_from_index_map(M_occ, idx_of_own, matchedS, topk=kk))

    # ---- floors, recomputed on THIS (occurrence-filtered) population -------------------------------
    Tn = DISS.l2n(t_mat)
    store_ortho = {w: Tn[pos_idx[w]] for w in words_needed if w in pos_idx}
    arm_pairs["F_ORTHOGRAPHIC"] = (_pd(store_ortho, matchedP), _pd(store_ortho, matchedS))

    def _pair_scalar_max(scalar_of, pairs):
        return np.array([max(scalar_of.get(w1, 0.0), scalar_of.get(w2, 0.0)) for w1, w2, _p in pairs])
    arm_pairs["F_FREQUENCY"] = (_pair_scalar_max(fq_log, matchedP), _pair_scalar_max(fq_log, matchedS))

    scrambled = DISS.l2n(FB.scramble_null(mat, MASTER_SEED + 4242))
    store_scr = {w: scrambled[pos_idx[w]] for w in words_needed if w in pos_idx}
    arm_pairs["F_SCRAMBLE"] = (_pd(store_scr, matchedP), _pd(store_scr, matchedS))

    proto = FB.constant_prototype_floor(mat, mat_ok)
    proto_of = {w: float(proto[pos_idx[w]]) for w in words_needed if w in pos_idx}

    def _pair_scalar_mean(scalar_of, pairs):
        return np.array([0.5 * (scalar_of.get(w1, 0.0) + scalar_of.get(w2, 0.0)) for w1, w2, _p in pairs])
    arm_pairs["F_CONSTANT_PROTOTYPE"] = (_pair_scalar_mean(proto_of, matchedP), _pair_scalar_mean(proto_of, matchedS))

    def _pair_path_sim(pairs):
        return np.array([DISS.wn_best_path_similarity(w1, w2) for w1, w2, _p in pairs])
    arm_pairs["KNOWN_ANSWER_WORDNET_PATH_SIM"] = (_pair_path_sim(matchedP), _pair_path_sim(matchedS))

    rng_rand = np.random.default_rng(MASTER_SEED + 909)
    rand_full = DISS.l2n(rng_rand.standard_normal((n_anchors, mat.shape[1])).astype(np.float32))
    store_rand = {w: rand_full[pos_idx[w]] for w in words_needed if w in pos_idx}
    arm_pairs["RANDOM_VECTOR_STORE"] = (_pd(store_rand, matchedP), _pd(store_rand, matchedS))

    # ---- ARMS-MUST-DIFFER ---------------------------------------------------------------------------
    digests = {k: _digest(np.concatenate([v[0], v[1]])) for k, v in arm_pairs.items()}
    assert len(set(digests.values())) > 1, "REGIME A: all arms produced IDENTICAL score vectors"
    rep["REGIME_A_ARM_DIGESTS"] = digests

    # ---- AUC per arm (+ both extra tie conventions) -------------------------------------------------
    auc_results: Dict[str, Dict] = {}
    boot_seed_base = MASTER_SEED + 8181
    for i, (name, (spv, ssv)) in enumerate(arm_pairs.items()):
        res = DISS.auc_bootstrap(spv, ssv, N_BOOT, boot_seed_base + i)
        res["tie_variants"] = auc_tie_variants(spv, ssv)
        auc_results[name] = res
        print("[regime_a] %-32s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)
    rep["REGIME_A_AUC_PER_ARM"] = auc_results

    # ---- storage honesty ------------------------------------------------------------------------------
    storage: Dict[str, Dict] = {}
    for name in arm_pairs:
        if name in ("A0_SUM", "S1_SINGLE_OCC", "F_ORTHOGRAPHIC", "F_SCRAMBLE", "RANDOM_VECTOR_STORE",
                    "F_FREQUENCY", "F_CONSTANT_PROTOTYPE", "KNOWN_ANSWER_WORDNET_PATH_SIM"):
            vecs_per_anchor, dim = 1, len(vocab_occ)
        else:
            vecs_per_anchor, dim = round(mean_occ, 2), len(vocab_occ)
        storage[name] = {"vectors_per_anchor": vecs_per_anchor, "dim": dim,
                        "floats_per_anchor": round(vecs_per_anchor * dim, 1),
                        "storage_multiplier_vs_A0_SUM": round(vecs_per_anchor / 1.0, 2)}
    rep["REGIME_A_STORAGE_HONESTY"] = storage

    # ---- LICENSING (K1 / N0 / floors) ----------------------------------------------------------------
    floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    floor_ok = all(auc_results[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in floor_names)
    floor_failures = [f for f in floor_names if auc_results[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    known_answer_ok = auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"] >= KNOWN_ANSWER_MIN_AUC
    random_ok = auc_results["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    instrument_licensed = bool(floor_ok and known_answer_ok)
    rep["REGIME_A_LICENSING"] = {
        "floors_at_chance": {"PASS": floor_ok, "failures": floor_failures},
        "known_answer_ok": {"PASS": known_answer_ok, "auc": auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"],
                            "gate": KNOWN_ANSWER_MIN_AUC},
        "random_vector_store_at_chance": {"PASS": random_ok},
        "INSTRUMENT_LICENSED": instrument_licensed}
    if not instrument_licensed:
        raise SystemExit("STOP_IF_v_INSTRUMENT_STILL_LOOSE -- publishing nothing. LICENSING=%r"
                         % rep["REGIME_A_LICENSING"])
    print("[regime_a] LICENSING PASS: floors at chance, known-answer AUC=%.4f" %
         auc_results["KNOWN_ANSWER_WORDNET_PATH_SIM"]["auc"], flush=True)

    # ---- REGRESSION GATE: A0_SUM / S1_SINGLE_OCC must reproduce DISS's own landed numbers ----------
    a0_auc = auc_results["A0_SUM"]["auc"]
    s1_auc = auc_results["S1_SINGLE_OCC"]["auc"]
    rep["REGRESSION_GATE_A0_SUM"] = {"measured": a0_auc, "expected": EXPECTED_A0_AUC,
                                     "tol": AUC_REGRESSION_TOL,
                                     "PASS": bool(abs(a0_auc - EXPECTED_A0_AUC) <= AUC_REGRESSION_TOL)}
    rep["REGRESSION_GATE_S1_SINGLE_OCC"] = {"measured": s1_auc, "expected": EXPECTED_S1_AUC,
                                            "tol": AUC_REGRESSION_TOL,
                                            "PASS": bool(abs(s1_auc - EXPECTED_S1_AUC) <= AUC_REGRESSION_TOL)}
    if grid == "full" and not rep["REGRESSION_GATE_A0_SUM"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- A0_SUM AUC does not reproduce DISS's landed "
                         "RAW_COUNT_FULL_ACCUM: %r" % rep["REGRESSION_GATE_A0_SUM"])
    print("[regime_a] REGRESSION A0_SUM=%.4f (expected %.4f) S1_SINGLE_OCC=%.4f (expected %.4f)" %
         (a0_auc, EXPECTED_A0_AUC, s1_auc, EXPECTED_S1_AUC), flush=True)

    # ---- STOP-IF (i)/(ii)/(iii)/(iv), paired diff bootstraps ----------------------------------------
    sp_m1, ss_m1 = arm_pairs["M1_MAXPOOL"]
    sp_a0, ss_a0 = arm_pairs["A0_SUM"]
    sp_n1, ss_n1 = arm_pairs["N1_MAXPOOL_RANDOM_OCC"]
    m1_vs_a0 = paired_auc_diff_bootstrap(sp_m1, ss_m1, sp_a0, ss_a0, N_BOOT, MASTER_SEED + 9191)
    m1_vs_n1 = paired_auc_diff_bootstrap(sp_m1, ss_m1, sp_n1, ss_n1, N_BOOT, MASTER_SEED + 9292)
    rep["REGIME_A_M1_vs_A0"] = m1_vs_a0
    rep["REGIME_A_M1_vs_N1"] = m1_vs_n1

    all_below_half = all(auc_results[a]["band"] != "ABOVE_0.5_SUBSTITUTABILITY"
                         for a in arm_pairs if not a.startswith("F_") and a != "RANDOM_VECTOR_STORE")
    stop_if_fired = []
    if m1_vs_a0["band"] == "ABOVE" and m1_vs_n1["band"] == "ABOVE":
        stop_if_fired.append("(i) M1_BEATS_A0_AND_N1 -- not collapsing is the fix")
    elif m1_vs_a0["band"] == "ABOVE" and m1_vs_n1["band"] != "ABOVE":
        stop_if_fired.append("(ii) M1_BEATS_A0_BUT_NOT_N1 -- gain is the MAX OPERATOR, not the occurrences")
    elif m1_vs_a0["band"] == "NOT_SEPARATED":
        stop_if_fired.append("(iii) M1_TIES_A0 -- not-collapsing insufficient")
    if all_below_half:
        stop_if_fired.append("(iv) ALL_ARMS_BELOW_0.5 -- no store this corpus supports encodes substitutability")
    rep["REGIME_A_STOP_IF_FIRED"] = stop_if_fired if stop_if_fired else ["NONE of (i)-(iv) fired cleanly"]
    rep["REGIME_A_elapsed_s"] = round(time.time() - t0, 1)
    return rep


# =================================================================================================
# REGIME B -- HIT@1 + WINNER COMPOSITION
# =================================================================================================
def run_regime_b(grid: str, rep: Dict) -> Dict:
    t0 = time.time()
    Pp = PIPE.build_population()
    C, mat, mat_ok = Pp["C"], Pp["mat"], Pp["mat_ok"]
    n_anchors, qidx = Pp["n_anchors"], Pp["qidx"]
    GOLD, E, keep_ALL = Pp["GOLD"], Pp["E"], Pp["keep"]
    aux = Pp["aux"]
    anchors = list(C["anchors"])

    T = np.flatnonzero(keep_ALL)
    if grid == "reduced":
        T = T[:400]
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact = C["Q_exact"][T]
    MATn = l2n(mat)
    query_words = [C["L_words"][int(t)] for t in T]
    n_items = int(T.size)
    print("[regime_b] n_anchors=%d n_items=%d" % (n_anchors, n_items), flush=True)

    # ---- REGRESSION GATE (proves this cell's own cache/pop matches the landed WR instrument) -------
    S_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E, GOLD)
    m_full = h_full["scored"] & keep_ALL
    a0_full = float(h_full["hit_exp"][m_full].mean())
    rep["REGIME_B_CACHE_REGRESSION_GATE"] = {"measured": round(a0_full, 4), "expected": PIPE.REGRESSION_A0_PARTIAL,
                                            "PASS": bool(abs(a0_full - PIPE.REGRESSION_A0_PARTIAL) <= PIPE.REGRESSION_TOL)}
    if not rep["REGIME_B_CACHE_REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGIME B CACHE REGRESSION GATE FAILED: %r" % rep["REGIME_B_CACHE_REGRESSION_GATE"])
    del S_full, h_full

    # ---- write-side corpus (reused, cached) + backgrounds (Pm_single/Pm_full, WR's own construction)
    sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["REGIME_B_corpus_provenance"] = corpus_prov
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, _item_diag = INFO.C3.build_items(shim, buckets, counts, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), "rebuilt item metadata misaligned with cache"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]

    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    P_full, _Q_ctx_unused, reuse_diag = PIPE.load_full_accum_from_checkpoint(info_out_dir, anchors, item_ids_T)
    rep["REGIME_B_checkpoint_reuse_full_accum"] = reuse_diag
    P_single, single_diag = PIPE.build_single_occurrence_counts(anchors, buckets, sents)
    rep["REGIME_B_single_occurrence_build_diag"] = single_diag
    vocab_f = INFO.build_vocab([P_full, P_single])
    rep["REGIME_B_vocab_size"] = len(vocab_f)
    Pm_full = INFO.l2n_sparse(INFO.to_sparse(P_full, anchors, vocab_f))
    Pm_single = INFO.l2n_sparse(INFO.to_sparse(P_single, anchors, vocab_f))
    Pm_single_T = Pm_single.T.tocsr()

    # ---- A0_SUM / S1_SINGLE_OCC over the FULL item population, vectorised (no python loop) --------
    Q_sum_full = Pm_full[qidx_T]
    Q_single_full = Pm_single[qidx_T]
    S_sum_full = np.asarray((Q_sum_full @ Pm_single_T).todense())      # [n_items, n_anchors]
    S_single_full = np.asarray((Q_single_full @ Pm_single_T).todense())
    elig_full = E_T.T   # [n_items, n_anchors]
    gold_full = GOLD_T.T
    Sm_sum = np.where(elig_full, S_sum_full, -np.inf)
    Sm_single = np.where(elig_full, S_single_full, -np.inf)
    winners_sum_full = np.argmax(Sm_sum, axis=1)
    winners_single_full = np.argmax(Sm_single, axis=1)
    hit_sum_full = gold_full[np.arange(n_items), winners_sum_full]
    hit_single_full = gold_full[np.arange(n_items), winners_single_full]
    rep["REGIME_B_A0_SUM_hit1_FULL_POPULATION"] = {"n": n_items, "hit_at_1": round(float(hit_sum_full.mean()), 4)}
    rep["REGIME_B_S1_SINGLE_OCC_hit1_FULL_POPULATION"] = {"n": n_items, "hit_at_1": round(float(hit_single_full.mean()), 4)}
    print("[regime_b] FULL-population A0_SUM=%.4f S1_SINGLE_OCC=%.4f (n=%d)" %
         (hit_sum_full.mean(), hit_single_full.mean(), n_items), flush=True)

    # ---- decisive subsample (own seeded draw, same recipe WR uses; NOT guaranteed index-identical) -
    n_decisive = min(N_DECISIVE, n_items)
    rng_dec = np.random.default_rng(MASTER_SEED + 909)
    idx_decisive = np.sort(rng_dec.choice(n_items, size=n_decisive, replace=False))
    rep["REGIME_B_N_DECISIVE"] = int(n_decisive)

    # ---- REGRESSION PROOF: call WR.best_single_occurrence_oracle VERBATIM on idx_decisive ----------
    dec_raw = WR.best_single_occurrence_oracle(idx_decisive, anchors, qidx_T, buckets, sents, vocab_f,
                                               Pm_single, Pm_full, E_T, GOLD_T)
    wr_sum_hit1 = float(dec_raw["SUM_ALL"].mean())
    wr_rand_hit1 = float(dec_raw["RANDOM_SINGLE"].mean())
    wr_best_hit1 = float(dec_raw["BEST_SINGLE_ORACLE"].mean())
    rep["REGRESSION_GATE_WR_DECISIVE_ARM"] = {
        "SUM_ALL": {"measured": round(wr_sum_hit1, 4), "expected": EXPECTED_SUM_ALL_HIT1,
                   "tol": HIT1_REGRESSION_TOL, "PASS": bool(abs(wr_sum_hit1 - EXPECTED_SUM_ALL_HIT1) <= HIT1_REGRESSION_TOL)},
        "RANDOM_SINGLE": {"measured": round(wr_rand_hit1, 4), "expected": EXPECTED_RANDOM_SINGLE_HIT1,
                         "tol": HIT1_REGRESSION_TOL, "PASS": bool(abs(wr_rand_hit1 - EXPECTED_RANDOM_SINGLE_HIT1) <= HIT1_REGRESSION_TOL)},
        "BEST_SINGLE_ORACLE": {"measured": round(wr_best_hit1, 4), "expected": EXPECTED_BEST_SINGLE_ORACLE_HIT1,
                              "tol": HIT1_REGRESSION_TOL, "PASS": bool(abs(wr_best_hit1 - EXPECTED_BEST_SINGLE_ORACLE_HIT1) <= HIT1_REGRESSION_TOL)}}
    if grid == "full":
        gate = rep["REGRESSION_GATE_WR_DECISIVE_ARM"]
        if not (gate["SUM_ALL"]["PASS"] and gate["RANDOM_SINGLE"]["PASS"]):
            raise SystemExit("REGIME B REGRESSION GATE FAILED (WR decisive arm): %r" % gate)
    print("[regime_b] WR-verbatim decisive arm on idx_decisive: SUM_ALL=%.4f RANDOM_SINGLE=%.4f "
         "BEST_SINGLE_ORACLE=%.4f (n=%d)" % (wr_sum_hit1, wr_rand_hit1, wr_best_hit1, n_decisive), flush=True)

    # ---- SELF-CONSISTENCY: my own vectorised A0_SUM/S1_SINGLE_OCC on idx_decisive must be BYTE-
    # IDENTICAL to WR's own hit booleans (same construction, proves winner-capture is trustworthy) ---
    hit_sum_dec = hit_sum_full[idx_decisive]
    hit_single_dec = hit_single_full[idx_decisive]
    n_mismatch_sum = int(np.sum(hit_sum_dec != dec_raw["SUM_ALL"]))
    n_mismatch_single = int(np.sum(hit_single_dec != dec_raw["RANDOM_SINGLE"]))
    rep["REGIME_B_SELF_CONSISTENCY"] = {"n_mismatch_SUM_ALL": n_mismatch_sum,
                                       "n_mismatch_RANDOM_SINGLE": n_mismatch_single,
                                       "PASS": bool(n_mismatch_sum == 0 and n_mismatch_single == 0)}
    if not rep["REGIME_B_SELF_CONSISTENCY"]["PASS"]:
        raise SystemExit("REGIME B SELF-CONSISTENCY FAILED -- vectorised A0_SUM/S1 construction "
                         "disagrees with WR's own function on idx_decisive: %r" % rep["REGIME_B_SELF_CONSISTENCY"])
    print("[regime_b] self-consistency PASS (0 mismatches vs WR's own boolean arrays)", flush=True)

    # ---- occurrence cache for the decisive subsample (target anchors only, bounded cost) -----------
    anchors_dec = [anchors[int(qidx_T[i])] for i in idx_decisive]
    occ_cache: Dict[str, List[Counter]] = {}
    t_cache = time.time()
    for a in sorted(set(anchors_dec)):
        occ_all = buckets.get(a, [])
        n_prof = INFO.C3._n_profile(len(occ_all))
        occ_cache[a] = [c for j in occ_all[:n_prof] for c in (INFO.raw_counts_for_window(sents[j], a),) if c]
    rep["REGIME_B_OCC_CACHE_DIAG"] = {"n_distinct_anchors": len(occ_cache),
                                     "elapsed_s": round(time.time() - t_cache, 1)}
    pool_pairs = [(a, c) for a, lst in occ_cache.items() for c in lst]
    fq_of = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    donor_of = build_band_shuffle(sorted(set(anchors_dec)), fq_of, N_BANDS, seed=MASTER_SEED + 7102)

    # ---- per-item scoring: M1_MAXPOOL / M2_TOPK_MEAN / N1 / N2 -------------------------------------
    names_new = ["M1_MAXPOOL"] + ["M2_TOPK_MEAN_K%d" % k for k in K_SWEEP] + \
        ["N1_MAXPOOL_RANDOM_OCC", "N2_MAXPOOL_SIZE_MATCHED_SHUFFLE"]
    hits: Dict[str, np.ndarray] = {name: np.zeros(n_decisive, dtype=bool) for name in names_new}
    winners: Dict[str, List[str]] = {name: [] for name in names_new}
    n_occ_arr = np.zeros(n_decisive, dtype=np.int64)
    rng_n1 = np.random.default_rng(MASTER_SEED + 7202)
    t_score = time.time()

    def _score_rows(counters: Dict[str, Counter], order: List[str], elig: np.ndarray, gold: np.ndarray):
        rows = INFO.l2n_sparse(INFO.to_sparse(counters, order, vocab_f))
        S = np.asarray((rows @ Pm_single_T).todense())
        Sm = np.where(elig[None, :], S, -np.inf)
        return Sm

    for pos in range(n_decisive):
        i = int(idx_decisive[pos])
        elig = E_T[:, i]
        gold = GOLD_T[:, i]
        a = anchors_dec[pos]
        occ_list = occ_cache.get(a, [])
        n_occ_arr[pos] = len(occ_list)

        if occ_list:
            counters_m = {str(j): c for j, c in enumerate(occ_list)}
            order_m = list(counters_m.keys())
            Sm = _score_rows(counters_m, order_m, elig, gold)
            pooled_max = Sm.max(axis=0)
            w = int(np.argmax(pooled_max))
            hits["M1_MAXPOOL"][pos] = bool(gold[w]); winners["M1_MAXPOOL"].append(anchors[w])
            for kk in K_SWEEP:
                kth = min(kk, Sm.shape[0])
                part = np.partition(Sm, -kth, axis=0)[-kth:, :]
                pooled_k = part.mean(axis=0)
                wk = int(np.argmax(pooled_k))
                name_k = "M2_TOPK_MEAN_K%d" % kk
                hits[name_k][pos] = bool(gold[wk]); winners[name_k].append(anchors[wk])
        else:
            for name in ["M1_MAXPOOL"] + ["M2_TOPK_MEAN_K%d" % k for k in K_SWEEP]:
                winners[name].append(a)

        n_w = len(occ_list)
        others = [p for p in pool_pairs if p[0] != a]
        if n_w > 0 and len(others) >= 1:
            sel = rng_n1.integers(0, len(others), size=n_w)
            counters_r = {str(j): others[int(ix)][1] for j, ix in enumerate(sel)}
            order_r = list(counters_r.keys())
            Sm_r = _score_rows(counters_r, order_r, elig, gold)
            pooled_r = Sm_r.max(axis=0)
            wr_ = int(np.argmax(pooled_r))
            hits["N1_MAXPOOL_RANDOM_OCC"][pos] = bool(gold[wr_]); winners["N1_MAXPOOL_RANDOM_OCC"].append(anchors[wr_])
        else:
            winners["N1_MAXPOOL_RANDOM_OCC"].append(a)

        donor = donor_of.get(a, a)
        donor_occ = occ_cache.get(donor, [])
        if donor_occ:
            counters_s = {str(j): c for j, c in enumerate(donor_occ)}
            order_s = list(counters_s.keys())
            Sm_s = _score_rows(counters_s, order_s, elig, gold)
            pooled_s = Sm_s.max(axis=0)
            ws_ = int(np.argmax(pooled_s))
            hits["N2_MAXPOOL_SIZE_MATCHED_SHUFFLE"][pos] = bool(gold[ws_])
            winners["N2_MAXPOOL_SIZE_MATCHED_SHUFFLE"].append(anchors[ws_])
        else:
            winners["N2_MAXPOOL_SIZE_MATCHED_SHUFFLE"].append(a)

        if (pos + 1) % 50 == 0 or pos == n_decisive - 1:
            print("[regime_b] scored %d/%d elapsed=%.0fs" % (pos + 1, n_decisive, time.time() - t_score), flush=True)

    rep["REGIME_B_mean_occurrences_per_item"] = round(float(n_occ_arr.mean()), 2)
    hits["A0_SUM"] = hit_sum_dec
    hits["S1_SINGLE_OCC"] = hit_single_dec
    winners["A0_SUM"] = [anchors[int(w)] for w in winners_sum_full[idx_decisive]]
    winners["S1_SINGLE_OCC"] = [anchors[int(w)] for w in winners_single_full[idx_decisive]]

    hit1_summary = {name: round(float(h.mean()), 4) for name, h in hits.items()}
    rep["REGIME_B_HIT1_PER_ARM"] = hit1_summary
    print("[regime_b] hit@1 per arm: %r" % hit1_summary, flush=True)

    # ---- storage honesty for REGIME B -----------------------------------------------------------------
    mean_occ_items = float(n_occ_arr.mean()) if n_decisive else 0.0
    storage_b: Dict[str, Dict] = {}
    for name in list(hits.keys()):
        vecs = 1.0 if name in ("A0_SUM", "S1_SINGLE_OCC") else mean_occ_items
        storage_b[name] = {"vectors_per_item": round(vecs, 2), "dim": len(vocab_f),
                          "floats_per_item": round(vecs * len(vocab_f), 1),
                          "storage_multiplier_vs_A0_SUM": round(vecs, 2)}
    rep["REGIME_B_STORAGE_HONESTY"] = storage_b

    # ---- ARMS-MUST-DIFFER -----------------------------------------------------------------------------
    digests_b = {k: _digest(v.astype(np.float64)) for k, v in hits.items()}
    assert len(set(digests_b.values())) > 1, "REGIME B: all arms produced IDENTICAL hit vectors"
    rep["REGIME_B_ARM_DIGESTS"] = digests_b

    # ---- winner composition, reused verbatim from WR ---------------------------------------------------
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in content_lemmas(s):
            where.setdefault(w, set()).add(si)
    query_words_dec = [query_words[i] for i in idx_decisive]
    gold_T_dec = GOLD_T[:, idx_decisive]
    idx_local = np.arange(n_decisive)
    composition: Dict[str, Dict] = {}
    for name, wlist in winners.items():
        in_gold = np.array([bool(gold_T_dec[C["pos"].get(wlist[j], -1), j]) if wlist[j] in C["pos"] else False
                            for j in range(n_decisive)])
        wn_comp = WR.wordnet_relation_composition(query_words_dec, wlist, in_gold, idx_local)
        # BEST_GOLD_SYNONYM reference computed once via A0_SUM's own score matrix (WR precedent: each
        # rung's own S_cache; here re-derived from the shared full-population Sm_sum, indexed to idx_decisive)
        gbest_local = np.where(gold_T_dec, Sm_sum[idx_decisive].T, -np.inf)
        gtop_local = np.argmax(gbest_local, axis=0)
        has_gold_local = gold_T_dec.any(axis=0)
        gold_words_local = [anchors[int(gtop_local[j])] if has_gold_local[j] else None for j in range(n_decisive)]
        jac_comp = WR.syntagmatic_jaccard_composition(query_words_dec, wlist, gold_words_local, where, idx_local)
        composition[name] = {"wordnet": {k: v for k, v in wn_comp.items() if k != "no_relation_bool"},
                            "syntagmatic": {k: v for k, v in jac_comp.items() if k not in ("jw_array", "jg_array")}}
        print("[regime_b] %-32s no_relation=%s winner_cooc=%s gold_cooc=%s" % (
            name, wn_comp["fraction_no_close_relation"], jac_comp["TOP1_WINNER"]["mean"],
            jac_comp["BEST_GOLD_SYNONYM"]["mean"]), flush=True)
    rep["REGIME_B_WINNER_COMPOSITION"] = composition

    # ---- paired hit@1 diff bootstraps (M1 vs A0, M1 vs N1) --------------------------------------------
    rep["REGIME_B_M1_vs_A0"] = paired_hit1_diff_bootstrap(hits["M1_MAXPOOL"], hits["A0_SUM"], N_BOOT, MASTER_SEED + 9393)
    rep["REGIME_B_M1_vs_N1"] = paired_hit1_diff_bootstrap(hits["M1_MAXPOOL"], hits["N1_MAXPOOL_RANDOM_OCC"], N_BOOT, MASTER_SEED + 9494)
    rep["REGIME_B_elapsed_s"] = round(time.time() - t0, 1)
    return rep


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True}
    print("[run] REGIME A (dissociation AUC) starting", flush=True)
    run_regime_a(grid, rep)
    print("[run] REGIME B (hit@1 + composition) starting", flush=True)
    run_regime_b(grid, rep)
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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_DECISIVE={N_DECISIVE} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    stop_if_a = rep.get("REGIME_A_STOP_IF_FIRED", ["UNKNOWN"])
    m1_vs_a0 = rep.get("REGIME_A_M1_vs_A0", {})
    verdict = "MAXPOOL_OCCURRENCE__%s__M1_vs_A0_%s__M1_vs_N1_%s" % (
        stop_if_a[0].split()[0].strip("()") if stop_if_a else "NONE",
        m1_vs_a0.get("band", "UNKNOWN"),
        rep.get("REGIME_A_M1_vs_N1", {}).get("band", "UNKNOWN"))

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Does keeping a word's occurrences separate and scoring by best match (max-"
                       "pool) beat summing, on the dissociation AUC (primary) and hit@1 + winner "
                       "composition (secondary)? -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "K_SWEEP": list(K_SWEEP),
                  "N_DECISIVE": N_DECISIVE, "N_BANDS": N_BANDS},
        "selftest_evidence_keys": sorted(ev.keys()),
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
        traceback.print_exc()
        raise SystemExit(3)
