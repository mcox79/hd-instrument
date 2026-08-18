"""exp_organ_f_noncollapsing_accumulation_v1 -- DOES A NON-COLLAPSING ACCUMULATION RULE BEAT THE
UNWEIGHTED SUM, AT A DEPTH WHERE MORE EVIDENCE IS STILL BUYING GAINS?

WHY THIS CELL EXISTS. Two findings landed 2026-08-17 on the SAME organ (accumulation) and this cell
composes them:
  1. notes/organ_f_accumulation_depth_ladder_2026-08-17.md (data/exp_organ_f_accumulation_depth_
     ladder_v1/metrics.json, commit 379c42833): on POP_128 (n=360 anchors, real profile capacity
     >=128), 72->128 sentences per anchor buys +0.0503 [+0.0139,+0.0861] hit@1, CI-separated, still
     climbing at the deepest well-powered rung tested.
  2. notes/writerule_step_ladder_v1_findings_2026-08-17.md (data/exp_writerule_step_ladder_v1/
     metrics.json, commit ab3555eb6): of the write rule's four live steps, ACCUMULATE (unweighted
     summation across profile occurrences) is 64% of the total ranked-drop mass, and across that
     single step the fraction of top-1 winners that have EVER co-occurred with the query jumps
     66.0% -> 94.4%. Summation is what converts the store into a record of adjacency.

THE HYPOTHESIS UNDER TEST (stated as a hypothesis, not a conclusion, per the dispatch): more
evidence helps (finding 1), but collapsing it into one unweighted sum throws part of it away and
biases what remains toward co-occurrence (finding 2). The build target this cell tests is therefore
ACCUMULATE WITHOUT COLLAPSING: does a non-collapsing (or less-collapsing) accumulation rule beat the
unweighted sum, on accuracy AND on winner composition, at a depth where more evidence still helps?

============================================================================================
LEAK-SAFE PROFILE POOL -- REUSED VERBATIM, NOT REIMPLEMENTED. Per the dispatch's explicit
instruction, this cell imports and calls experiments.exp_organ_f_accumulation_depth_ladder_v1's
`build_profile_pool` and `load_buckets_uncapped` UNMODIFIED (aliased ORGF below). That construction:
PROFILE_POOL(a) = the deployed profile prefix (buckets_capped[a][:n_profile_capped(a)], identical to
what the live system already accumulates) CONCATENATED WITH buckets_uncapped[a][K_SENT_TOTAL:] (fresh
corpus material beyond the arbitrary K_SENT_TOTAL=90 collection cap, which the deployed system never
saw as ANY item's held-out cue). No depth's profile pool, at any D, ever contains a real held-out
evaluation sentence -- verified in ORGF's own self_test() against a hand-built toy example with a
real gap, reused wholesale below (ORGF.self_test() is called in full in this cell's own self_test()).

============================================================================================
ARMS, one variable at a time (the ACCUMULATION RULE), identical population / scorer / gold / cue
regime, at MATCHED DEPTH (D=72 the incumbent operating point, D=128 the deepest well-powered rung
organ_f established) on POP_128 (cap_min=128, SAME population definition organ_f used: item_capacity
= leak-safe profile pool length per anchor >= 128). The QUERY (cue) construction is held FIXED across
every arm at each depth -- Q_oracle_D = the TRUE anchor's own S0 (plain unweighted sum) row at depth
D, EXACTLY the oracle-cue convention organ_f/pipeline_stage_oracle_ladder/writerule all already use
("cue = the item's own accumulated representation") -- so only the STORE construction varies between
arms, never the cue. A REAL held-out cue (Q_ctx_full, reused READ ONLY from exp_cue_information_
audit_v1's own checkpoint, the SAME real cue organ_f used) is scored BESIDE the oracle cue for every
arm that is cheap to score (everything except S1, which is declared a ceiling diagnostic only).

  S0_UNWEIGHTED_SUM        the incumbent: sum(raw per-occurrence counts) across the depth-D profile
                            pool. REGRESSION-GATED against organ_f's own landed POP_128 D72/D128
                            numbers (0.0917 / 0.1417) to prove this cell reproduces the identical
                            population + leak-safe-pool + accumulation construction.
  S1_BEST_SINGLE_OCC_ORACLE an oracle that, for each anchor, scores by the MAX cosine similarity of
                            any single one of its own depth-D occurrence vectors to the query (never
                            summed). CEILING DIAGNOSTIC ONLY -- reported, never treated as a headline
                            number, per the dispatch's explicit instruction. This is the cleanest
                            separator of "more evidence" from "summing": if it beats S0 badly, the sum
                            is destroying recoverable information rather than the evidence being
                            absent.
  S2_NORMALISED_SUM        each occurrence's raw count vector is L2-normalised BEFORE summing, so one
                            long or frequent sentence cannot dominate the accumulated row.
  S3_IDF_DOWNWEIGHT        tf-idf-style: every context word's contribution is downweighted by
                            log(N_sentences / (1+document_frequency(word))), computed over the SAME
                            34,169-sentence corpus (the "where" sentence-co-occurrence index, reused
                            for both this and the composition instrument), then summed as usual.
                            CAUTION flagged by the dispatch: frequency is one of the four required
                            floors -- if this wins, a frequency-stratified within-tercile check is run
                            (below) to rule out simple reproduction of the frequency floor.
  S4_MULTI_VECTOR          does NOT collapse: the depth-D occurrence set is clustered (spherical
                            k-means, cosine distance, OUR INVENTION UNDER TEST -- see BRAIN FRAMING)
                            into k>1 centroids per anchor, scored by the BEST-matching centroid (max
                            over k). k in {2,3,4}, swept, never adopted as a value. Compared against
                            S0 at MATCHED DEPTH (same D) and, separately, at MATCHED TOTAL STORAGE
                            (see MATCHED_STORAGE_CHECK below) -- the dispatch requires both, since a
                            k-vector store trivially has k times S0's storage and could win "by being
                            bigger" rather than by clustering carrying real structure.
  N1_RANDOM_PARTITION      THE CONTROL THAT MATTERS MOST FOR S4, per the dispatch: identical
                            multi-vector machinery (same D occurrences, same k, same best-matching-
                            component scoring) but occurrences are assigned to the k components AT
                            RANDOM instead of by clustering. If N1 ties S4, the gain (if any) is from
                            having several vectors to match against, not from the clustering carrying
                            anything -- reported as such, no mechanism claimed.
  K1_KNOWN_ANSWER / N0_NULL sanity arms built from S0's own D=128 representation: K1 = addressing
                            (does the anchor's own row win argmax over the full ~5500-anchor pool
                            when queried with its own oracle representation) must read >=0.95;
                            N0_NULL = the oracle query deranged (never-self permutation) must sit at
                            this population's own chance addressing. Both are HARD gates -- if either
                            fails, nothing downstream is published (SystemExit).

MATCHED_STORAGE_CHECK (k=2 only, disclosed scope limit -- k=3/4 matched-storage checks are NOT run,
for the same reason organ_f itself: shrinking sub-populations at higher storage multiples underpower
the check faster than it informs). For (D_from, D_to) in {(72,144), (128,256)}: on the sub-population
of POP_128 anchors whose leak-safe capacity ALSO reaches D_to (a strict, smaller, disclosed-n subset),
compare S4_MULTI_VECTOR(k=2, D=D_from) [k vectors, D_from material each] against S0_UNWEIGHTED_SUM at
D=D_to [1 vector, k*D_from material] -- i.e., "is the same k-vector storage budget better spent on the
SAME material split k ways (non-collapsing) than on k times as much material summed into one vector
(more collapsing, more reading)?" This is a DIFFERENT question from N1 (which holds material AND
storage both fixed and asks only whether the PARTITION is smart); this asks whether non-collapsing
storage is a more efficient use of a fixed storage budget than reading more and collapsing it.

WINNER COMPOSITION, reused wholesale from experiments.exp_writerule_step_ladder_v1 (aliased WR below)
-- `wordnet_relation_composition` and `syntagmatic_jaccard_composition` are top-level, independently
self-tested functions there (not reimplemented here). Measured at D=128 only (the deepest, best-
powered primary rung; D=72 composition is a disclosed scope limit, not run, to bound nltk
path_similarity cost across the full arm list) for every arm: S0, S1, S2, S3, S4 (each k), N1 (each
k) -- ten arms, one shared paired probe (all 360 POP_128 items; n_probe convention elsewhere in this
arc caps at 700, so no subsampling is needed here). The incumbent baselines this cell compares against
(landed, writerule_step_ladder_v1, full-depth R4 rung): 79.3%(ish; the writerule cell's own R4 number
is 0.8000 no-relation, and 90.6% ever-co-occurred at PROJECTED depth) / at the UNPROJECTED matched
FULL-ACCUM rung (R3, the construction closest to this cell's own unprojected S0) the writerule cell
measured 0.7971 no-relation and 94.4% ever-co-occurred -- THIS is the number this cell's own S0_D128
composition is checked against as the closest prior measurement, disclosed as a DIFFERENT cell/run
(informal cross-check, not a formal paired margin).

============================================================================================
BRAIN FRAMING, labelled per the dispatch. PINNED (as a computation, not a parameter): complementary
learning systems -- neocortex extracts CROSS-EPISODE REGULARITIES while hippocampus keeps the
EPISODE (McClelland/O'Reilly). Adjacency is episodic; substitutability is the regularity. A
multi-vector store that keeps several distinguishable episode-clusters and abstracts across each,
rather than averaging every episode into one blurred sum, is structurally closer to that division of
labour than a single collapsed vector. PINNED: repeated reactivation/replay extracting structure
across episodes is the broad process this whole accumulation organ is an instance of (matching
organ_f's own framing, not re-argued here). OUR INVENTION UNDER TEST, explicitly, per the dispatch:
the SPECIFIC clustering rule (spherical k-means, cosine distance), the value of k, and the
best-matching-component scoring rule. No anatomical structure is claimed to compute cosine k-means;
this is an engineering proxy for "several distinguishable episode traces," tested on its OWN merits
against the two controls (N1 random partition; S0 at matched storage), not adopted because it is
brain-labelled.

ORGAN REUSE, enumerated then reconciled -- nothing below is reimplemented that already exists:
  experiments.exp_organ_f_accumulation_depth_ladder_v1 (ORGF)   build_profile_pool (LEAK-SAFE, REUSED
                                                                  VERBATIM per the dispatch's explicit
                                                                  instruction), load_buckets_uncapped
                                                                  (cached), build_capacity, self_test()
  experiments.exp_pipeline_stage_oracle_ladder_v1 (PIPE)        build_population, dprime_stats/
                                                                  summary, rank_summary, spearman,
                                                                  load_full_accum_from_checkpoint,
                                                                  MASTER_SEED, self_test()
  experiments.exp_cue_information_audit_v1 (INFO)               raw_counts_for_window, load_corpus_
                                                                  and_buckets, build_vocab, to_sparse,
                                                                  l2n_sparse, _ShimSpace, C3, self_test()
  experiments.exp_writerule_step_ladder_v1 (WR)                 wordnet_relation_composition,
                                                                  syntagmatic_jaccard_composition,
                                                                  self_test()
  tools.floor_battery (FB)                                      hit_at_1_both_tie_conventions, the
                                                                  four floors, paired_bootstrap_ci,
                                                                  margin, oracle_constant_scores,
                                                                  as_constant_matrix, l2n, self_test()
  hdlab.reading_grounding_loop                                  content_lemmas (the "where" sentence-
                                                                  co-occurrence index, reused for both
                                                                  IDF and composition)
  experiments._seed_checkpoint, tools.exp_checkpoint             output dir + atomic metrics write +
                                                                  per-unit checkpoint/resume

NEW IN THIS CELL (not reused because nothing existing does it): spherical_kmeans (cosine k-means over
sparse rows, self-tested against a hand-built two-cluster toy example), random_partition_groups
(seeded, self-tested for balance and reproducibility), build_occurrence_lists (per-anchor UN-SUMMED
occurrence lists over the REUSED leak-safe pool -- organ_f only ever built CUMULATIVE sums, never
individual occurrence vectors, since its own question never needed to isolate a single occurrence),
build_nonlinear_arms (the per-anchor loop that builds S1/S4/N1's candidate scores against a fixed
oracle+real query set), build_where_index / compute_idf (document-frequency IDF over the shared
corpus).

PRIOR-WORK CHECK. `bash tools/substrate_query.sh "non-collapsing accumulation multi-vector cluster"`
-- if the KB ingest is livelocked (documented this session, notes/STATUS.md), the substitute is the
enumeration above: every cell this docstring's REUSE section names was read in full, plus
notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md (Organ F, "LADDER: NONE" as of this morning, this cell IS
that ladder's first follow-up) and both 2026-08-17 findings notes named at the top of this docstring.
No existing cell builds a multi-vector / non-collapsing accumulation store, an IDF-weighted store, or
a best-single-occurrence oracle on this population. The sibling agent running the depth ladder
(organ-f-accumulation) confirmed, on request, that it has neither a BEST_SINGLE_OCCURRENCE_ORACLE arm
nor any multi-vector/clustering/IDF arm on disk or in flight. Not a rediscovery.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. The deployed store
(mat) is NEVER rebuilt; it is used only for floors. data/foundation/** is never opened. Writes only
under data/exp_organ_f_noncollapsing_accumulation_v1[_reduced]/ and this cell's own scratch/
subdirectory (none needed -- everything read is already cached on disk by the cells this one reuses).

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's hit-vector across the full arm list, >1 distinct
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: ONE unit "MAIN" via tools.exp_checkpoint, resume-safe
# - discriminator survives scale: --grid reduced (smoke) runs the IDENTICAL code path at a smaller
#   population/depth/k-sweep, not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated leak-safe pool
#   and population construction unmodified; the only new calibration -- spherical_kmeans,
#   random_partition_groups, the occurrence-list builder, IDF -- is self-tested against hand-built toy
#   examples with known answers, not merely asserted)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - sweep_alignment / discriminating_fraction / composition_edges / positive_control_arms / CRLB
#   gates: N/A -- this is a diagnostic/rule-comparison cell (same family as organ_f/pipeline_stage/
#   writerule, none of which compose chain-grade substrate primitives or sweep a capacity-bound
#   parameter in the CRLB sense); declared, not omitted.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/hdlab next -- this can take ~40-60s cold; flushed so a "
      "slow import is never mistaken for a hang)", flush=True)

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

import experiments.exp_organ_f_accumulation_depth_ladder_v1 as ORGF     # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE          # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
import experiments.exp_writerule_step_ladder_v1 as WR                   # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "organ_f_noncollapsing_accumulation_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/organ_f_noncollapsing_accumulation_v1_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = PIPE.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
ADDRESS_EXACT_MIN = 0.95
N_KMEANS_ITERS = 8

if SMOKE:
    CAP_MIN = 16
    DEPTHS_SUM: Tuple[int, ...] = (8, 16, 24, 32)
    DEPTHS_PRIMARY: Tuple[int, ...] = (8, 16)
    NONLINEAR_MAX_DEPTH = 16
    K_SWEEP: Tuple[int, ...] = (2,)
    MATCHED_STORAGE_PAIRS: List[Tuple[int, int]] = [(8, 16), (16, 32)]
else:
    CAP_MIN = 128
    DEPTHS_SUM = (72, 128, 144, 256)
    DEPTHS_PRIMARY = (72, 128)
    NONLINEAR_MAX_DEPTH = 128
    K_SWEEP = (2, 3, 4)
    MATCHED_STORAGE_PAIRS = [(72, 144), (128, 256)]

D_MAX_SUM = max(DEPTHS_SUM)

# ---- cross-cell regression: organ_f's own landed POP_128 oracle numbers (FULL grid only) ----------
REGRESSION_ORGANF_POP128 = {72: 0.0917, 128: 0.1417}
REGRESSION_TOL = 1e-3


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# NEW MACHINERY -- spherical k-means, random partition, occurrence lists, IDF
# =================================================================================================
def spherical_kmeans(M: sp.csr_matrix, k: int, seed: int,
                     n_iters: int = N_KMEANS_ITERS) -> Tuple[np.ndarray, np.ndarray]:
    """Cosine k-means over L2-NORMALISED sparse rows of M [D_pts, V]. k_eff = min(k, D_pts) when
    D_pts < k (OUR INVENTION UNDER TEST -- see module docstring BRAIN FRAMING; no anatomy computes
    this particular rule). Returns (centroids [k_eff, V] dense unit rows, assign [D_pts] cluster id).
    Empty clusters are reinitialised to the point with the LOWEST current best-match similarity, so a
    bad init cannot silently collapse to fewer than k_eff active clusters."""
    D_pts = M.shape[0]
    V = M.shape[1]
    if D_pts == 0:
        return np.zeros((0, V), dtype=np.float32), np.zeros(0, dtype=np.int64)
    k_eff = max(1, min(k, D_pts))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(D_pts)
    centroids = np.asarray(M[perm[:k_eff]].todense(), dtype=np.float64)
    assign = np.zeros(D_pts, dtype=np.int64)
    for _it in range(n_iters):
        sim = np.asarray(M @ centroids.T)             # [D_pts, k_eff]
        assign = np.argmax(sim, axis=1)
        new_centroids = np.zeros_like(centroids)
        for c in range(k_eff):
            members = np.flatnonzero(assign == c)
            if members.size == 0:
                worst = int(np.argmin(sim.max(axis=1)))
                new_centroids[c] = np.asarray(M[worst].todense(), dtype=np.float64).ravel()
                assign[worst] = c
                continue
            summed = np.asarray(M[members].sum(axis=0), dtype=np.float64).ravel()
            nrm = np.linalg.norm(summed)
            new_centroids[c] = summed / nrm if nrm > 1e-12 else summed
        centroids = new_centroids
    return centroids.astype(np.float32), assign


def random_partition_groups(n: int, k: int, seed: int) -> List[np.ndarray]:
    """n items assigned to k groups uniformly AT RANDOM (never by similarity) -- the machinery
    N1_RANDOM_PARTITION reuses so it differs from S4_MULTI_VECTOR ONLY in the partition rule."""
    k_eff = max(1, min(k, max(n, 1)))
    if n == 0:
        return [np.zeros(0, dtype=np.int64) for _ in range(k_eff)]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    return [np.asarray(g, dtype=np.int64) for g in np.array_split(perm, k_eff)]


def build_occurrence_lists(anchor_ids: Sequence[str], profile_pool: Dict[str, List[int]],
                           sents: List[str], max_depth: int) -> Tuple[Dict[str, List[Counter]], Dict]:
    """Per-anchor list of UN-SUMMED individual occurrence count-vectors, in the REUSED leak-safe
    PROFILE_POOL order (ORGF.build_profile_pool, called by the caller, never reimplemented here).
    Truncated to max_depth per anchor, saturating at the anchor's own capacity -- same convention
    ORGF.build_depth_snapshots uses for its cumulative sums, applied here to un-summed lists instead."""
    t0 = time.time()
    out: Dict[str, List[Counter]] = {}
    n_empty = 0
    n_occ_total = 0
    for k_i, a in enumerate(anchor_ids):
        pool = profile_pool.get(a, [])[:max_depth]
        if not pool:
            out[a] = []
            n_empty += 1
            continue
        out[a] = [INFO.raw_counts_for_window(sents[sidx], a) for sidx in pool]
        n_occ_total += len(out[a])
        if (k_i + 1) % 1000 == 0 or k_i == len(anchor_ids) - 1:
            print("[occ_lists] %d/%d anchors n_occ_total=%d elapsed=%.0fs" % (
                k_i + 1, len(anchor_ids), n_occ_total, time.time() - t0), flush=True)
    return out, {"n_anchors": len(anchor_ids), "n_empty_profile": n_empty,
                "n_occurrence_calls": n_occ_total, "elapsed_s": round(time.time() - t0, 1)}


def sum_prefix(occ_list: Sequence[Counter], D: int) -> Counter:
    c: Counter = Counter()
    for x in occ_list[:D]:
        c.update(x)
    return c


def normalized_counter(c: Counter) -> Dict[str, float]:
    if not c:
        return {}
    nrm = float(np.sqrt(sum(v * v for v in c.values())))
    if nrm < 1e-12:
        return {}
    return {w: v / nrm for w, v in c.items()}


def sum_normalized_prefix(occ_list: Sequence[Counter], D: int) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for x in occ_list[:D]:
        for w, v in normalized_counter(x).items():
            out[w] = out.get(w, 0.0) + v
    return out


def build_where_index(sents: List[str]) -> Dict[str, set]:
    """Sentence-co-occurrence index: word -> set of sentence indices containing it. REUSED PATTERN
    from exp_writerule_step_ladder_v1's own composition instrument (that cell embeds this inline in
    run(), not as a standalone callable); shared here between IDF (document frequency) and the
    composition Jaccard measurement, so it is built exactly once."""
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in content_lemmas(s):
            where.setdefault(w, set()).add(si)
    return where


def compute_idf(vocab: Dict[str, int], where: Dict[str, set], n_sents: int) -> np.ndarray:
    """idf(w) = log(N_sents / (1+df(w))), aligned to vocab's column order. A HIGH-frequency context
    word (appears in many sentences) gets a LOW (or negative, for very common words) weight."""
    idf = np.zeros(len(vocab), dtype=np.float64)
    for w, ci in vocab.items():
        df = len(where.get(w, ()))
        idf[ci] = np.log(n_sents / (1.0 + df))
    return idf.astype(np.float32)


def build_nonlinear_arms(anchor_ids: Sequence[str], OCC_sparse: sp.csr_matrix,
                         anchor_row_range: Dict[str, Tuple[int, int]],
                         Q_oracle_by_depth: Dict[int, np.ndarray], Q_real: Optional[np.ndarray],
                         depths: Sequence[int], k_sweep: Sequence[int], master_seed: int) -> Dict:
    """ONE pass over every anchor. For each requested depth D: S1 = max cosine to any single one of
    the anchor's own occurrence vectors (oracle only). For each k in k_sweep: S4 = max cosine to any
    of k spherical-k-means centroids (clustered); N1 = the SAME machinery with occurrences assigned
    to the k components at random. Centroids are computed ONCE per (anchor, D, k) and reused for both
    the oracle and the real-cue score, avoiding redundant clustering."""
    n_anchors = len(anchor_ids)
    n_q_oracle = {D: Q_oracle_by_depth[D].shape[0] for D in depths}
    n_q_real = int(Q_real.shape[0]) if Q_real is not None else 0
    S1 = {D: np.zeros((n_anchors, n_q_oracle[D]), dtype=np.float32) for D in depths}
    S4 = {(D, k): np.zeros((n_anchors, n_q_oracle[D]), dtype=np.float32) for D in depths for k in k_sweep}
    N1 = {(D, k): np.zeros((n_anchors, n_q_oracle[D]), dtype=np.float32) for D in depths for k in k_sweep}
    S4r = {(D, k): np.zeros((n_anchors, n_q_real), dtype=np.float32) for D in depths for k in k_sweep} \
        if Q_real is not None else {}
    N1r = {(D, k): np.zeros((n_anchors, n_q_real), dtype=np.float32) for D in depths for k in k_sweep} \
        if Q_real is not None else {}
    k_eff_used: Dict[Tuple[int, int], List[int]] = {(D, k): [] for D in depths for k in k_sweep}
    t0 = time.time()
    for a_idx, a in enumerate(anchor_ids):
        start, end = anchor_row_range.get(a, (0, 0))
        n_rows = end - start
        if n_rows == 0:
            continue
        for D in depths:
            n_take = min(D, n_rows)
            if n_take == 0:
                continue
            M = OCC_sparse[start:start + n_take]
            Qo = Q_oracle_by_depth[D]
            sim_occ = np.asarray(M @ Qo.T)                      # [n_take, n_q_oracle]
            S1[D][a_idx, :] = sim_occ.max(axis=0)
            for k in k_sweep:
                cen, _assign = spherical_kmeans(M, k, master_seed + 97 * D + 13 * k + a_idx)
                k_eff_used[(D, k)].append(int(cen.shape[0]))
                if cen.shape[0]:
                    S4[(D, k)][a_idx, :] = np.asarray(cen @ Qo.T).max(axis=0)
                groups = random_partition_groups(n_take, k, master_seed + 5000 + 97 * D + 13 * k + a_idx)
                cen_r: List[np.ndarray] = []
                for g in groups:
                    if g.size == 0:
                        continue
                    v = np.asarray(M[g].sum(axis=0), dtype=np.float64).ravel()
                    nrm = np.linalg.norm(v)
                    cen_r.append((v / nrm if nrm > 1e-12 else v).astype(np.float32))
                if cen_r:
                    N1[(D, k)][a_idx, :] = (np.stack(cen_r) @ Qo.T).max(axis=0)
                if Q_real is not None:
                    if cen.shape[0]:
                        S4r[(D, k)][a_idx, :] = np.asarray(cen @ Q_real.T).max(axis=0)
                    if cen_r:
                        N1r[(D, k)][a_idx, :] = (np.stack(cen_r) @ Q_real.T).max(axis=0)
        if (a_idx + 1) % 1000 == 0 or a_idx == n_anchors - 1:
            print("[nonlinear] %d/%d anchors elapsed=%.0fs" % (a_idx + 1, n_anchors, time.time() - t0),
                 flush=True)
    diag = {"elapsed_s": round(time.time() - t0, 1),
           "k_eff_mean": {"D%d_K%d" % (D, k): round(float(np.mean(v)), 3) if v else None
                          for (D, k), v in k_eff_used.items()},
           "k_eff_below_requested_rate": {
               "D%d_K%d" % (D, k): round(float(np.mean([1.0 if e < k else 0.0 for e in v])), 4)
               if v else None for (D, k), v in k_eff_used.items()}}
    return {"S1": S1, "S4": S4, "N1": N1, "S4_REAL": S4r, "N1_REAL": N1r, "diag": diag}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    print("[selftest] reusing ORGF's own self_test() wholesale (chains FB+INFO+PIPE self-tests, plus "
         "ORGF's own leak-safety/saturation checks on the REUSED build_profile_pool)", flush=True)
    ev["ORGF_selftest_keys"] = sorted(ORGF.self_test().keys())
    print("[selftest] reusing WR's own self_test() wholesale (chains PIPE again, plus WR's own "
         "FILTER/NORMALISE/composition-instrument checks)", flush=True)
    ev["WR_selftest_keys"] = sorted(WR.self_test().keys())

    # ---- spherical_kmeans: two well-separated toy clusters must separate; k_eff clipping works ----
    rows = [[1.0, 0.0, 0.0], [0.9, 0.1, 0.0], [0.95, 0.05, 0.0],
           [0.0, 1.0, 0.0], [0.1, 0.9, 0.0], [0.05, 0.95, 0.0]]
    M_toy = sp.csr_matrix(l2n(np.array(rows, dtype=np.float32)))
    cen, assign = spherical_kmeans(M_toy, 2, seed=3)
    assert cen.shape == (2, 3), cen.shape
    same_first_three = len(set(assign[:3].tolist())) == 1
    same_last_three = len(set(assign[3:].tolist())) == 1
    diff_groups = assign[0] != assign[3]
    assert same_first_three and same_last_three and diff_groups, (
        "spherical_kmeans did not separate two well-separated toy clusters: %r" % assign)
    cen1, assign1 = spherical_kmeans(M_toy[:1], 3, seed=1)   # D_pts=1 < k=3 -> k_eff clipped to 1
    assert cen1.shape == (1, 3), cen1.shape
    cen0, _a0 = spherical_kmeans(sp.csr_matrix((0, 3)), 2, seed=1)   # D_pts=0 -> empty, no crash
    assert cen0.shape == (0, 3), cen0.shape
    ev["spherical_kmeans_selftest"] = {"separates_toy_clusters": True, "k_eff_clipping": True,
                                       "empty_input_no_crash": True}

    # ---- random_partition_groups: balanced sizes, exact partition, seeded reproducibility ---------
    g = random_partition_groups(10, 3, seed=5)
    assert sorted(np.concatenate(g).tolist()) == list(range(10)), g
    assert max(len(x) for x in g) - min(len(x) for x in g) <= 1, [len(x) for x in g]
    g2 = random_partition_groups(10, 3, seed=5)
    assert all(np.array_equal(a, b) for a, b in zip(g, g2)), "same seed must reproduce the same split"
    g3 = random_partition_groups(2, 5, seed=1)   # n < k -> k_eff clipped
    assert len(g3) == 2 and sorted(np.concatenate(g3).tolist()) == [0, 1], g3
    ev["random_partition_groups_selftest"] = {"exact_partition": True, "balanced": True,
                                              "seed_reproducible": True, "k_eff_clipping": True}

    # ---- normalized_counter: known unit-norm output ------------------------------------------------
    nc = normalized_counter(Counter({"a": 3, "b": 4}))
    assert abs(nc["a"] - 0.6) < 1e-9 and abs(nc["b"] - 0.8) < 1e-9, nc
    assert normalized_counter(Counter()) == {}
    ev["normalized_counter_known_answer"] = nc

    # ---- IDF: a word in every sentence must score LOWER than a word in one sentence ----------------
    toy_where = {"common": {0, 1, 2}, "rare": {0}}
    idf_toy = compute_idf({"common": 0, "rare": 1}, toy_where, n_sents=3)
    assert idf_toy[0] < idf_toy[1], idf_toy
    ev["idf_known_answer"] = {"idf_common": round(float(idf_toy[0]), 4), "idf_rare": round(float(idf_toy[1]), 4)}

    # ---- occurrence-list construction, real code path, on a toy corpus (mirrors ORGF's own toy) ----
    toy_sents = ["cat sat on mat", "cat ran to park", "cat ate the fish", "cat slept all day"]
    toy_pool = {"cat": [0, 1, 2, 3]}
    occ, diag = build_occurrence_lists(["cat"], toy_pool, toy_sents, max_depth=3)
    assert len(occ["cat"]) == 3, occ["cat"]
    assert occ["cat"][0] == INFO.raw_counts_for_window(toy_sents[0], "cat")
    assert occ["cat"][2] == INFO.raw_counts_for_window(toy_sents[2], "cat")
    occ_sat, _d = build_occurrence_lists(["cat"], toy_pool, toy_sents, max_depth=10)
    assert len(occ_sat["cat"]) == 4, "must saturate at the anchor's own capacity, not crash or pad"
    ev["build_occurrence_lists_selftest"] = {"depth_truncation": True, "saturation_no_crash": True}

    # ---- KNOWN ANSWER: max-over-occurrences (S1-style) beats the sum on a constructed adversarial
    # case where summing two opposed-direction occurrences cancels a real match; max-pooling recovers
    # it. This proves the MACHINERY (not real data) correctly implements "best occurrence wins". -----
    V_toy = 4
    occ_a = sp.csr_matrix(l2n(np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)))
    query_toy = l2n(np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32))
    sum_row = l2n(np.array([occ_a.toarray().sum(axis=0)], dtype=np.float32))
    sim_sum = float((sum_row @ query_toy.T)[0, 0])
    sim_max = float(np.asarray(occ_a @ query_toy.T).max())
    assert sim_max > sim_sum + 0.1, (sim_max, sim_sum, "max-pooling must beat the diluted sum here")
    ev["max_vs_sum_known_answer"] = {"sim_max": round(sim_max, 4), "sim_sum": round(sim_sum, 4)}

    # ---- checkpoint round-trip (reused, not reimplemented) ------------------------------------------
    import tools.exp_checkpoint as ECK
    ev["exp_checkpoint_selftest"] = bool(ECK._selftest())

    # ---- arms-must-differ digest sensitivity --------------------------------------------------------
    a1 = np.array([1.0, 2.0, 3.0]); a2 = np.array([1.0, 2.0, 3.0001])
    assert _digest(a1) != _digest(a2)
    ev["arms_must_differ_digest_sensitivity"] = True

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    Pp = PIPE.build_population()
    C, mat, mat_ok = Pp["C"], Pp["mat"], Pp["mat_ok"]
    n_anchors, qidx = Pp["n_anchors"], Pp["qidx"]
    GOLD, E, keep_ALL = Pp["GOLD"], Pp["E"], Pp["keep"]
    aux = Pp["aux"]
    anchors = list(C["anchors"])

    T = np.flatnonzero(keep_ALL)
    qidx_T = qidx[T]
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    Tq = aux["Tq"][T]
    query_words_T = [C["L_words"][int(t)] for t in T]
    print(f"[load] n_anchors={n_anchors} n_items_T={T.size} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": PIPE.CTS.ruler_mode_gate(),
    }

    # ---- corpus, LEAK-SAFE profile pool (REUSED VERBATIM from ORGF) -----------------------------
    sents, buckets_capped, counts_capped, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    buckets_uncapped = ORGF.load_buckets_uncapped(sents)
    profile_pool = ORGF.build_profile_pool(anchors, buckets_capped, buckets_uncapped)
    capacity = ORGF.build_capacity(anchors, profile_pool)
    item_capacity = capacity[qidx_T]

    pop_mask = item_capacity >= CAP_MIN
    pop_items = np.flatnonzero(pop_mask)
    if pop_items.size < 10:
        raise SystemExit(f"POPULATION cap_min={CAP_MIN} has only {pop_items.size} items -- too small "
                         "to publish anything")
    E_pop = E_T[:, pop_items]
    GOLD_pop = GOLD_T[:, pop_items]
    qidx_pop = qidx_T[pop_items]
    query_words_pop = [query_words_T[i] for i in pop_items]
    n_anchors_pop = len(set(qidx_pop.tolist()))
    rep["POPULATION"] = {"cap_min": CAP_MIN, "n_items": int(pop_items.size), "n_anchors": n_anchors_pop,
                         "note": "SAME construction as ORGF's own POP_128 (cap_min=128): item_capacity "
                                 "= leak-safe profile pool length per anchor"}
    print(f"[population] cap_min={CAP_MIN} n_items={pop_items.size} n_anchors={n_anchors_pop}", flush=True)

    # ---- real-cue item metadata + checkpoint reuse (READ ONLY, same pattern as ORGF/PIPE) --------
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, _item_diag = INFO.C3.build_items(shim, buckets_capped, counts_capped, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), "rebuilt item metadata misaligned with cache"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    print("[real_cue] reusing exp_cue_information_audit_v1's landed checkpoint (READ ONLY)", flush=True)
    _P_full_unused, Q_ctx_full, reuse_diag = PIPE.load_full_accum_from_checkpoint(
        info_out_dir, anchors, item_ids_T)
    rep["real_cue_checkpoint_reuse"] = reuse_diag
    del _P_full_unused

    # ---- occurrence lists (NEW: per-anchor, UN-SUMMED, over the REUSED leak-safe pool) ------------
    occ_lists, occ_diag = build_occurrence_lists(anchors, profile_pool, sents, max_depth=D_MAX_SUM)
    rep["OCC_BUILD"] = occ_diag

    # ---- S0 (sum) / S2 (normalised-sum) dicts, per depth -------------------------------------------
    P0 = {D: {a: sum_prefix(occ_lists[a], D) for a in anchors} for D in DEPTHS_SUM}
    P2 = {D: {a: sum_normalized_prefix(occ_lists[a], D) for a in anchors} for D in DEPTHS_PRIMARY}
    print("[P0/P2] built sum + normalised-sum dicts for depths %r / %r t=%.0fs" % (
         DEPTHS_SUM, DEPTHS_PRIMARY, time.time() - t0), flush=True)

    vocab = INFO.build_vocab([P0[D] for D in DEPTHS_SUM] + [Q_ctx_full])
    rep["vocab_n_distinct_content_words"] = len(vocab)
    print(f"[vocab] {len(vocab)} distinct content words t={time.time() - t0:.0f}s", flush=True)

    Pm0 = {D: INFO.l2n_sparse(INFO.to_sparse(P0[D], anchors, vocab)) for D in DEPTHS_SUM}
    Pm2 = {D: INFO.l2n_sparse(INFO.to_sparse(P2[D], anchors, vocab)) for D in DEPTHS_PRIMARY}

    # ---- IDF (S3), from the SAME corpus's sentence-co-occurrence index (also reused for composition)
    where = build_where_index(sents)
    idf_row = compute_idf(vocab, where, len(sents))
    Pm3 = {D: INFO.l2n_sparse(Pm0[D].multiply(idf_row[None, :]).tocsr()) for D in DEPTHS_PRIMARY}
    rep["IDF_DIAG"] = {"idf_min": round(float(idf_row.min()), 4), "idf_max": round(float(idf_row.max()), 4),
                       "idf_mean": round(float(idf_row.mean()), 4)}

    Qm_ctx = INFO.l2n_sparse(INFO.to_sparse(Q_ctx_full, item_ids_T, vocab))   # [n_items_T, V]

    # ---- occurrence-level sparse matrix (individual, L2-normalised rows) for S1/S4/N1 ---------------
    key_order: List[Tuple[str, int]] = []
    anchor_row_range: Dict[str, Tuple[int, int]] = {}
    occ_counters: Dict[Tuple[str, int], Counter] = {}
    for a in anchors:
        n_a = min(len(occ_lists[a]), NONLINEAR_MAX_DEPTH)
        start = len(key_order)
        for kk in range(n_a):
            key = (a, kk)
            key_order.append(key)
            occ_counters[key] = occ_lists[a][kk]
        anchor_row_range[a] = (start, start + n_a)
    OCC_sparse = INFO.l2n_sparse(INFO.to_sparse(occ_counters, key_order, vocab))
    rep["OCC_sparse_shape"] = list(OCC_sparse.shape)
    print(f"[occ_sparse] shape={OCC_sparse.shape} t={time.time() - t0:.0f}s", flush=True)

    # ---- oracle queries (S0's own row, per depth) + real cue, restricted to pop_items ---------------
    Q_oracle_by_depth = {D: np.asarray(Pm0[D][qidx_pop].todense(), dtype=np.float32) for D in DEPTHS_PRIMARY}
    Q_real = np.asarray(Qm_ctx[pop_items].todense(), dtype=np.float32)

    print("[nonlinear] starting per-anchor S1/S4/N1 build", flush=True)
    nonlin = build_nonlinear_arms(anchors, OCC_sparse, anchor_row_range, Q_oracle_by_depth, Q_real,
                                  DEPTHS_PRIMARY, K_SWEEP, MASTER_SEED)
    rep["NONLINEAR_BUILD_DIAG"] = nonlin["diag"]
    print("[nonlinear] done t=%.0fs" % (time.time() - t0), flush=True)

    # =============================== SCORING ==========================================================
    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    tie_of: Dict[str, float] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    S_cache: Dict[str, np.ndarray] = {}

    def add_arm(name: str, S: np.ndarray, target: Optional[np.ndarray] = None,
               cache_for_composition: bool = False) -> None:
        h = FB.hit_at_1_both_tie_conventions(S, E_pop, GOLD_pop)
        hits_exp[name] = h["hit_exp"]; hits_opt[name] = h["hit_opt"]; hits_cons[name] = h["hit_cons"]
        tie_of[name] = float(h["tie_mass"].mean())
        noise_of[name] = PIPE.dprime_summary(PIPE.dprime_stats(S, E_pop, GOLD_pop))
        rs, _ro, _rc = PIPE.rank_summary(S, E_pop, GOLD_pop)
        rank_of[name] = rs
        if target is not None:
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = target >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == target[ok])), 6)
        if cache_for_composition:
            S_cache[name] = S
        print(f"[{name}] hit@1={h['hit_exp'][h['scored']].mean():.4f}", flush=True)

    for D in DEPTHS_PRIMARY:
        Qo = Q_oracle_by_depth[D]
        S0_o = np.asarray((Pm0[D] @ Qo.T), dtype=np.float32)
        add_arm(f"S0_UNWEIGHTED_SUM_D{D}", S0_o, target=qidx_pop, cache_for_composition=(D == max(DEPTHS_PRIMARY)))
        S1_o = nonlin["S1"][D]
        add_arm(f"S1_BEST_SINGLE_OCC_ORACLE_D{D}", S1_o, target=qidx_pop,
               cache_for_composition=(D == max(DEPTHS_PRIMARY)))
        S2_o = np.asarray((Pm2[D] @ Qo.T), dtype=np.float32)
        add_arm(f"S2_NORMALISED_SUM_D{D}", S2_o, target=qidx_pop, cache_for_composition=(D == max(DEPTHS_PRIMARY)))
        S3_o = np.asarray((Pm3[D] @ Qo.T), dtype=np.float32)
        add_arm(f"S3_IDF_DOWNWEIGHT_D{D}", S3_o, target=qidx_pop, cache_for_composition=(D == max(DEPTHS_PRIMARY)))
        for k in K_SWEEP:
            add_arm(f"S4_MULTI_VECTOR_D{D}_K{k}", nonlin["S4"][(D, k)], target=qidx_pop,
                   cache_for_composition=(D == max(DEPTHS_PRIMARY)))
            add_arm(f"N1_RANDOM_PARTITION_D{D}_K{k}", nonlin["N1"][(D, k)], target=qidx_pop,
                   cache_for_composition=(D == max(DEPTHS_PRIMARY)))
        # ---- real cue (beside, never instead) --------------------------------------------------------
        add_arm(f"S0_UNWEIGHTED_SUM_D{D}_REAL", np.asarray((Pm0[D] @ Q_real.T), dtype=np.float32))
        add_arm(f"S2_NORMALISED_SUM_D{D}_REAL", np.asarray((Pm2[D] @ Q_real.T), dtype=np.float32))
        add_arm(f"S3_IDF_DOWNWEIGHT_D{D}_REAL", np.asarray((Pm3[D] @ Q_real.T), dtype=np.float32))
        for k in K_SWEEP:
            add_arm(f"S4_MULTI_VECTOR_D{D}_K{k}_REAL", nonlin["S4_REAL"][(D, k)])
            add_arm(f"N1_RANDOM_PARTITION_D{D}_K{k}_REAL", nonlin["N1_REAL"][(D, k)])

    # =============================== FLOORS, recomputed on THIS population ==========================
    S_orth = (FB.l2n(aux["t_mat"]) @ FB.l2n(Tq[pop_items]).T).astype(np.float32)
    add_arm("F_ORTHOGRAPHIC", S_orth)
    S_freq = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), pop_items.size)
    add_arm("F_FREQUENCY", S_freq)
    Q_part_pop = C["Q_part"][T][pop_items]
    Q_exact_pop = C["Q_exact"][T][pop_items]
    S_scr_part = (FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191)) @ FB.l2n(Q_part_pop).T).astype(np.float32)
    add_arm("F_SCRAMBLE_PARTIAL_CUE", S_scr_part)
    S_scr_exact = (FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191)) @ FB.l2n(Q_exact_pop).T).astype(np.float32)
    add_arm("F_SCRAMBLE_EXACT_KEY", S_scr_exact)
    S_const = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), pop_items.size)
    add_arm("F_CONSTANT_PROTOTYPE", S_const)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_pop[:, i]) for i in range(pop_items.size)]),
        pop_items.size)
    add_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)

    # =============================== K1 / N0_NULL SANITY (using S0's own deepest representation) ------
    D_deep = max(DEPTHS_PRIMARY)
    rng_n = np.random.default_rng(MASTER_SEED + 8181)
    n_pop = pop_items.size
    perm = np.arange(n_pop)
    for _ in range(64):
        perm = rng_n.permutation(n_pop)
        if n_pop < 2 or np.all(perm != np.arange(n_pop)):
            break
    S_null = np.asarray((Pm0[D_deep] @ Q_oracle_by_depth[D_deep][perm].T), dtype=np.float32)
    add_arm("N0_NULL", S_null, target=qidx_pop)

    addr_known = addressing_of.get(f"S0_UNWEIGHTED_SUM_D{D_deep}")
    addr_known = 0.0 if addr_known is None else addr_known
    addr_null = addressing_of.get("N0_NULL")
    addr_null = 1.0 if addr_null is None else addr_null
    chance = 1.0 / max(n_anchors_pop, 1)
    rep["K1_KNOWN_ANSWER"] = {"addressing_at_deepest_D": D_deep, "addressing": addr_known,
                              "gate": ADDRESS_EXACT_MIN, "PASSED": bool(addr_known >= ADDRESS_EXACT_MIN)}
    rep["N0_NULL"] = {"addressing": addr_null, "chance_addressing_approx": round(chance, 6),
                      "hit_at_1": round(hits_exp["N0_NULL"].mean(), 4),
                      "PASSED": bool(addr_null < max(0.05, 20.0 * chance))}
    if not (rep["K1_KNOWN_ANSWER"]["PASSED"] and rep["N0_NULL"]["PASSED"]):
        raise SystemExit("INSTRUMENT_STILL_LOOSE -- K1/N0 sanity failed, publishing nothing: %r / %r"
                         % (rep["K1_KNOWN_ANSWER"], rep["N0_NULL"]))
    print("[gates] K1/N0 PASS", flush=True)

    # =============================== REGRESSION vs organ_f's own landed POP_128 numbers (FULL only) ---
    if grid == "full":
        reg = {}
        for D in (72, 128):
            if D in DEPTHS_PRIMARY:
                measured = float(hits_exp[f"S0_UNWEIGHTED_SUM_D{D}"].mean())
                expected = REGRESSION_ORGANF_POP128[D]
                reg[f"D{D}"] = {"measured": round(measured, 4), "expected": expected,
                               "PASS": bool(abs(measured - expected) <= REGRESSION_TOL)}
        rep["REGRESSION_VS_ORGANF_POP128"] = reg
        if not all(v["PASS"] for v in reg.values()):
            raise SystemExit("REGRESSION FAILED vs organ_f's landed POP_128 numbers -- not the "
                             "identical population/pool/construction: %r" % reg)
        print("[regression] PASS vs organ_f landed numbers %r" % reg, flush=True)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_distinct"] = len(set(digests.values()))
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_total"] = len(digests)

    # =============================== BOOTSTRAP, main arm list =========================================
    pb = FB.paired_bootstrap_ci(hits_exp, np.ones(n_pop, dtype=bool), N_BOOT, MASTER_SEED + 101)
    pb_opt = FB.paired_bootstrap_ci(hits_opt, np.ones(n_pop, dtype=bool), N_BOOT, MASTER_SEED + 101)
    pb_cons = FB.paired_bootstrap_ci(hits_cons, np.ones(n_pop, dtype=bool), N_BOOT, MASTER_SEED + 101)
    acc, boot = pb["acc"], pb["boot"]
    ci_hw = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
            for k, v in boot.items()}
    analytic_null_hw = round(float(1.645 / np.sqrt(max(pb["n_common"] - 1, 1))), 5)
    floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE_PARTIAL_CUE", "F_SCRAMBLE_EXACT_KEY",
                  "F_CONSTANT_PROTOTYPE"]
    binding = max(floor_names, key=lambda f: acc[f])
    rep["POWER"] = {"n_common_scored": pb["n_common"], "analytic_null_halfwidth": analytic_null_hw}
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = floor_names
    rep["NEVER_IMPORTED"] = ["0.1390", "0.0873", "0.1382", "0.2070", "-0.1959"]
    rep["BINDING_FLOOR"] = binding
    rep["BINDING_FLOOR_VALUE"] = round(acc[binding], 4)

    per_arm = {}
    for name in hits_exp:
        per_arm[name] = {
            "SIGNAL_hit_at_1_tie_corrected": round(acc[name], 4),
            "SIGNAL_hit_at_1_optimistic": round(pb_opt["acc"][name], 4),
            "SIGNAL_hit_at_1_conservative": round(pb_cons["acc"][name], 4),
            "ci95": [round(float(np.percentile(boot[name], 2.5)), 4),
                    round(float(np.percentile(boot[name], 97.5)), 4)],
            "ci_halfwidth": ci_hw[name], "analytic_null_halfwidth": analytic_null_hw,
            "mean_tie_mass": round(tie_of.get(name, float("nan")), 4), "NOISE_dprime": noise_of.get(name),
            "RANK": rank_of.get(name), "addressing_accuracy": addressing_of.get(name),
            "margin_vs_binding_floor": FB.margin(boot, name, binding) if name != binding else None}
    rep["PER_ARM"] = per_arm

    # =============================== KEY MARGINS: S4 vs S0, S4 vs N1, S1 vs S0, S2/S3 vs S0 ----------
    margins = []
    for D in DEPTHS_PRIMARY:
        margins.append({"pair": f"S1_vs_S0_D{D}_ceiling_diagnostic",
                        **FB.margin(boot, f"S1_BEST_SINGLE_OCC_ORACLE_D{D}", f"S0_UNWEIGHTED_SUM_D{D}")})
        margins.append({"pair": f"S2_vs_S0_D{D}", **FB.margin(boot, f"S2_NORMALISED_SUM_D{D}", f"S0_UNWEIGHTED_SUM_D{D}")})
        margins.append({"pair": f"S3_vs_S0_D{D}", **FB.margin(boot, f"S3_IDF_DOWNWEIGHT_D{D}", f"S0_UNWEIGHTED_SUM_D{D}")})
        margins.append({"pair": f"S2_vs_S0_D{D}_REAL",
                        **FB.margin(boot, f"S2_NORMALISED_SUM_D{D}_REAL", f"S0_UNWEIGHTED_SUM_D{D}_REAL")})
        margins.append({"pair": f"S3_vs_S0_D{D}_REAL",
                        **FB.margin(boot, f"S3_IDF_DOWNWEIGHT_D{D}_REAL", f"S0_UNWEIGHTED_SUM_D{D}_REAL")})
        for k in K_SWEEP:
            margins.append({"pair": f"S4_vs_S0_D{D}_K{k}",
                           **FB.margin(boot, f"S4_MULTI_VECTOR_D{D}_K{k}", f"S0_UNWEIGHTED_SUM_D{D}")})
            margins.append({"pair": f"S4_vs_N1_D{D}_K{k}",
                           **FB.margin(boot, f"S4_MULTI_VECTOR_D{D}_K{k}", f"N1_RANDOM_PARTITION_D{D}_K{k}")})
            margins.append({"pair": f"N1_vs_S0_D{D}_K{k}",
                           **FB.margin(boot, f"N1_RANDOM_PARTITION_D{D}_K{k}", f"S0_UNWEIGHTED_SUM_D{D}")})
            margins.append({"pair": f"S4_vs_S0_D{D}_K{k}_REAL",
                           **FB.margin(boot, f"S4_MULTI_VECTOR_D{D}_K{k}_REAL", f"S0_UNWEIGHTED_SUM_D{D}_REAL")})
            margins.append({"pair": f"S4_vs_N1_D{D}_K{k}_REAL",
                           **FB.margin(boot, f"S4_MULTI_VECTOR_D{D}_K{k}_REAL", f"N1_RANDOM_PARTITION_D{D}_K{k}_REAL")})
    rep["KEY_MARGINS"] = margins

    # =============================== FREQUENCY-STRATIFIED CHECK for S3 (CAUTION per dispatch) --------
    fq_pop = np.asarray(aux["fq"], dtype=np.float64)[qidx_T[pop_items]]
    D_deep = max(DEPTHS_PRIMARY)
    terc = np.quantile(fq_pop, [1 / 3, 2 / 3])
    strata = {"LOW_FREQ": fq_pop <= terc[0], "MID_FREQ": (fq_pop > terc[0]) & (fq_pop <= terc[1]),
             "HIGH_FREQ": fq_pop > terc[1]}
    freq_strat = {}
    for sname, smask in strata.items():
        if int(smask.sum()) < 10:
            freq_strat[sname] = {"n": int(smask.sum()), "note": "too small to bootstrap"}
            continue
        pb_s = FB.paired_bootstrap_ci(
            {f"S3_IDF_DOWNWEIGHT_D{D_deep}": hits_exp[f"S3_IDF_DOWNWEIGHT_D{D_deep}"],
            f"S0_UNWEIGHTED_SUM_D{D_deep}": hits_exp[f"S0_UNWEIGHTED_SUM_D{D_deep}"]},
            smask, min(N_BOOT, 4000), MASTER_SEED + 3030)
        m = FB.margin(pb_s["boot"], f"S3_IDF_DOWNWEIGHT_D{D_deep}", f"S0_UNWEIGHTED_SUM_D{D_deep}")
        freq_strat[sname] = {"n": int(smask.sum()), **m}
    rep["S3_FREQUENCY_STRATIFIED_CHECK"] = {"depth": D_deep, "strata": freq_strat,
        "reading": "if S3 beats S0 even in the LOW_FREQ stratum (where the frequency floor is "
                   "weakest), the S3 effect is not simply reproducing the frequency floor"}

    # =============================== MATCHED_STORAGE_CHECK (k=2 only) =================================
    matched_storage = []
    for D_from, D_to in MATCHED_STORAGE_PAIRS:
        if 2 not in K_SWEEP:
            continue
        sub_mask_full = item_capacity[pop_items] >= D_to
        sub_items = pop_items[sub_mask_full]
        if sub_items.size < 10:
            matched_storage.append({"D_from": D_from, "D_to": D_to, "n_sub": int(sub_items.size),
                                    "note": "too small to publish"})
            continue
        sub_local = np.flatnonzero(sub_mask_full)     # positions WITHIN pop_items/hit-vector arrays
        E_sub = E_T[:, sub_items]; GOLD_sub = GOLD_T[:, sub_items]; qidx_sub = qidx_T[sub_items]
        Qo_to = np.asarray(Pm0[D_to][qidx_sub].todense(), dtype=np.float32)
        S0_to = np.asarray((Pm0[D_to] @ Qo_to.T), dtype=np.float32)
        h_to = FB.hit_at_1_both_tie_conventions(S0_to, E_sub, GOLD_sub)["hit_exp"]
        h_s4_sub = nonlin["S4"][(D_from, 2)][:, sub_local]      # candidate rows unchanged; query subset
        h_s4 = FB.hit_at_1_both_tie_conventions(h_s4_sub, E_sub, GOLD_sub)["hit_exp"]
        h_s0_from_sub = FB.hit_at_1_both_tie_conventions(
            np.asarray((Pm0[D_from] @ Q_oracle_by_depth[D_from][sub_local].T), dtype=np.float32),
            E_sub, GOLD_sub)["hit_exp"]
        pb_ms = FB.paired_bootstrap_ci(
            {"S0_AT_D_TO": h_to, "S4_K2_AT_D_FROM": h_s4, "S0_AT_D_FROM": h_s0_from_sub},
            np.ones(sub_items.size, dtype=bool), min(N_BOOT, 4000), MASTER_SEED + 4040 + D_from)
        m_s4_vs_s0to = FB.margin(pb_ms["boot"], "S4_K2_AT_D_FROM", "S0_AT_D_TO")
        matched_storage.append({
            "D_from": D_from, "D_to": D_to, "n_sub": int(sub_items.size),
            "S0_AT_D_FROM_acc": round(pb_ms["acc"]["S0_AT_D_FROM"], 4),
            "S4_K2_AT_D_FROM_acc": round(pb_ms["acc"]["S4_K2_AT_D_FROM"], 4),
            "S0_AT_D_TO_acc": round(pb_ms["acc"]["S0_AT_D_TO"], 4),
            "S4_vs_S0_AT_D_TO_margin": m_s4_vs_s0to,
            "reading": ("S4(k=2, D=%d material, 2-vector storage) vs S0(D=%d material, 1-vector "
                       "storage, SAME total storage budget as 2 vectors would need if filled by "
                       "reading twice as much)" % (D_from, D_to))})
    rep["MATCHED_STORAGE_CHECK"] = matched_storage

    # =============================== WINNER COMPOSITION -- D_deep only, all main arms ------------------
    comp_arms = [f"S0_UNWEIGHTED_SUM_D{D_deep}", f"S1_BEST_SINGLE_OCC_ORACLE_D{D_deep}",
                f"S2_NORMALISED_SUM_D{D_deep}", f"S3_IDF_DOWNWEIGHT_D{D_deep}"] + \
               [f"S4_MULTI_VECTOR_D{D_deep}_K{k}" for k in K_SWEEP] + \
               [f"N1_RANDOM_PARTITION_D{D_deep}_K{k}" for k in K_SWEEP]
    composition: Dict[str, Dict] = {}
    idx_probe = np.arange(pop_items.size)
    for name in comp_arms:
        if name not in S_cache:
            continue
        S = S_cache[name]
        Sm = np.where(E_pop, S, -np.inf)
        top1 = np.argmax(Sm, axis=0)
        winner_words = [anchors[int(w)] for w in top1]
        in_gold = np.array([bool(GOLD_pop[int(top1[i]), i]) for i in range(pop_items.size)])
        gbest = np.where(GOLD_pop & E_pop, Sm, -np.inf)
        gtop = np.argmax(gbest, axis=0)
        has_gold = (GOLD_pop & E_pop).any(axis=0)
        gold_words: List[Optional[str]] = [anchors[int(gtop[i])] if has_gold[i] else None
                                           for i in range(pop_items.size)]
        wn_comp = WR.wordnet_relation_composition(query_words_pop, winner_words, in_gold, idx_probe)
        jac_comp = WR.syntagmatic_jaccard_composition(query_words_pop, winner_words, gold_words,
                                                       where, idx_probe)
        composition[name] = {"wordnet": wn_comp, "syntagmatic": jac_comp}
        print("[composition] %s no_relation=%.3f winner_cooc=%s ever_cooc=%s" % (
             name, wn_comp["fraction_no_close_relation"] or -1.0, jac_comp["TOP1_WINNER"]["mean"],
             jac_comp["TOP1_WINNER"]["frac_ever_co_occurring"]), flush=True)
    rep["WINNER_COMPOSITION_D%d" % D_deep] = composition

    # =============================== STANDING RULE 12: floor-clearance correlation checks --------------
    clearance_checks: Dict[str, Dict] = {}
    for name in comp_arms:
        m = per_arm.get(name, {}).get("margin_vs_binding_floor")
        if not m or m.get("band") != "ABOVE":
            continue
        S = S_cache.get(name)
        if S is None:
            continue
        best_gold = np.where(GOLD_pop & E_pop, S, -np.inf).max(axis=0)
        orth_best = np.where(GOLD_pop & E_pop, S_orth, -np.inf).max(axis=0)
        valid = np.isfinite(best_gold) & np.isfinite(orth_best)
        lens = np.array([len(w) for w in query_words_pop])
        clearance_checks[name] = {
            "n": int(valid.sum()),
            "corr_with_word_length": round(PIPE.spearman(best_gold[valid], lens[valid]), 4)
                if valid.sum() > 2 else None,
            "corr_with_orthographic_floor_score": round(PIPE.spearman(best_gold[valid], orth_best[valid]), 4)
                if valid.sum() > 2 else None}
    rep["STANDING_RULE_12_FLOOR_CLEARANCE_CORRELATION"] = clearance_checks

    # =============================== STOP-IF EVALUATION ================================================
    def band_of(pair_tag: str) -> Optional[str]:
        for m in margins:
            if m["pair"] == pair_tag:
                return m["band"]
        return None

    s4_wins = [f"S4_vs_S0_D{D_deep}_K{k}" for k in K_SWEEP if band_of(f"S4_vs_S0_D{D_deep}_K{k}") == "ABOVE"]
    s4_beats_n1 = [f"S4_vs_N1_D{D_deep}_K{k}" for k in K_SWEEP if band_of(f"S4_vs_N1_D{D_deep}_K{k}") == "ABOVE"]
    s4_ties_n1 = [f"S4_vs_N1_D{D_deep}_K{k}" for k in K_SWEEP if band_of(f"S4_vs_N1_D{D_deep}_K{k}") == "NOT_SEPARATED"]
    ms_wins = [ms for ms in matched_storage if ms.get("S4_vs_S0_AT_D_TO_margin", {}).get("band") == "ABOVE"]
    s1_margin_d_deep = FB.margin(boot, f"S1_BEST_SINGLE_OCC_ORACLE_D{D_deep}", f"S0_UNWEIGHTED_SUM_D{D_deep}")
    s1_barely = s1_margin_d_deep["band"] != "ABOVE" or s1_margin_d_deep["point"] < 0.02

    comp_flat_but_acc_moves = []
    for name in comp_arms:
        m = None
        if name.startswith("S4_MULTI_VECTOR"):
            k_ = int(name.split("_K")[-1])
            m = band_of(f"S4_vs_S0_D{D_deep}_K{k_}")
        if m == "ABOVE" and name in composition:
            cooc = composition[name]["syntagmatic"]["TOP1_WINNER"].get("frac_ever_co_occurring")
            base_cooc = composition.get(f"S0_UNWEIGHTED_SUM_D{D_deep}", {}).get(
                "syntagmatic", {}).get("TOP1_WINNER", {}).get("frac_ever_co_occurring")
            if cooc is not None and base_cooc is not None and abs(cooc - base_cooc) < 0.03:
                comp_flat_but_acc_moves.append(name)

    stop_if: List[str] = []
    if s4_wins and s4_beats_n1 and ms_wins:
        stop_if.append("(i) S4 beats S0 (matched depth) AND beats S0-at-matched-storage AND beats "
                       "N1_RANDOM_PARTITION -- NON-COLLAPSING ACCUMULATION IS REAL")
    if s4_ties_n1 and not s4_beats_n1:
        stop_if.append("(ii) S4 ties N1_RANDOM_PARTITION -- the gain (if any) is from having several "
                       "vectors, not from clustering; claim no mechanism")
    if s1_barely:
        stop_if.append("(iii) S1 oracle barely beats S0 -- the sum is NOT destroying much; this "
                       "would retire 'accumulate without collapsing'")
    if comp_flat_but_acc_moves:
        stop_if.append("(iv) accuracy improves while composition stays flat for: %r -- ranking fixed, "
                       "not the relation" % comp_flat_but_acc_moves)
    rep["STOP_IF_FIRED"] = stop_if if stop_if else ["NONE of (i)-(iv) fired cleanly on this run's numbers"]

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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} CAP_MIN={CAP_MIN} DEPTHS_PRIMARY={DEPTHS_PRIMARY} "
         f"K_SWEEP={K_SWEEP} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    stop_if = rep.get("STOP_IF_FIRED", [])
    fired_real = [s for s in stop_if if not s.startswith("NONE")]
    verdict = "NONCOLLAPSE__%s__STOPIF_%s" % (
        "FIRED_" + "_".join(s[:4].replace("(", "").replace(")", "") for s in fired_real) if fired_real
        else "NONE_FIRED",
        "YES" if fired_real else "NO")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "Does a non-collapsing accumulation rule beat the unweighted sum at a depth where more "
            "evidence still helps? S0(sum)/S1(best-occ oracle)/S2(normalised-sum)/S3(idf-downweight)/"
            "S4(multi-vector clustered)/N1(random-partition control), matched depth + matched storage, "
            "oracle and real cue, winner composition at every arm. -> " + verdict),
        "config": {"CAP_MIN": CAP_MIN, "DEPTHS_SUM": list(DEPTHS_SUM), "DEPTHS_PRIMARY": list(DEPTHS_PRIMARY),
                  "NONLINEAR_MAX_DEPTH": NONLINEAR_MAX_DEPTH, "K_SWEEP": list(K_SWEEP),
                  "MATCHED_STORAGE_PAIRS": MATCHED_STORAGE_PAIRS, "N_BOOT": N_BOOT,
                  "MASTER_SEED": MASTER_SEED},
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
    except KeyboardInterrupt:
        raise
    except Exception as _e:
        traceback.print_exc()
        _out = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
        _out.mkdir(parents=True, exist_ok=True)
        _diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(_e).__name__}: {str(_e)[:500]}",
                 "summary": f"CELL_CRASHED: {type(_e).__name__}", "elapsed_s": 0.0,
                 "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _tmp = os.path.join(str(_out), "metrics.json.tmp")
        _final = os.path.join(str(_out), "metrics.json")
        with open(_tmp, "w", encoding="utf-8") as _f:
            json.dump(_diag, _f, indent=2)
        os.replace(_tmp, _final)
        raise SystemExit(1)
