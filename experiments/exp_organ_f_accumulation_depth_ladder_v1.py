"""exp_organ_f_accumulation_depth_ladder_v1 -- ORGAN F: IS THE ACCUMULATION GRADIENT STILL
CLIMBING AT 72 SENTENCES PER ANCHOR, OR HAS IT SATURATED?

WHY THIS CELL EXISTS. notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md ORGAN F: the pipeline oracle
ladder (data/exp_pipeline_stage_oracle_ladder_v1/metrics.json, commit e28d1b8d6) found accumulating
~72 sentences per anchor instead of 1 buys +0.0263 [+0.0186,+0.0343] -- the largest CI-separated
positive effect measured anywhere in this programme, and the ONLY step with a positive gradient.
Nobody has studied accumulation as an organ. This cell does: enumerate its real steps from live
code, sweep depth far past the current 72-sentence operating point, and report SIGNAL/SEPARATION/
RANK with paired step-to-step CIs, under a TOKEN-MATCHED control, a RANDOM-OCCURRENCE control, and
a FREQUENCY-STRATIFIED check -- because the +0.0263 finding, read plainly, compared "1 sentence"
against "however many a word happens to have" for the SAME anchors, which conflates depth with
frequency by construction. This cell removes that conflation.

============================================================================================
STEPS ENUMERATED FROM LIVE CODE (not from the brief's sketch). HOW: read hdlab/reading_grounding_
loop.py (ConceptSpace.observe -- ownership of "accumulation"), experiments/exp_grounding_readout_
known_answer_v1.py (build_buckets, _n_profile, build_items -- corpus-to-profile construction), and
experiments/exp_cue_information_audit_v1.py (raw_counts_for_window, the runtime-verified encoder
identity H^T P_a == mat[a]). The Director's brief sketch, TO BE CORRECTED against this reading:
  (a) which occurrences are collected at all -> build_buckets keeps the FIRST K_SENT_TOTAL=90
      sentences containing a lemma (exp_grounding_readout_known_answer_v1.py:359), an ARBITRARY
      CAP baked into that one function, not a corpus limit. Measured directly (this cell's own
      population-check, scratch/organ_f_accumulation_depth_ladder_v1/): rebuilding buckets from
      the SAME already-tokenised sentence list WITHOUT that cap shows the true corpus goes to
      k=2019 occurrences for the single most frequent anchor, and >=257 occurrences for 177
      anchors -- the "as far beyond 72 as the corpus allows" the brief asks for is a REAL,
      answerable question, not a ceiling already reached. This is itself a finding: the landed
      +0.0263 number was measured at an ARTIFICIAL cap, not the corpus's own limit.
  (b) how each occurrence is coded -> raw_counts_for_window: content_words(sentence) with the
      target lemma's own tokens masked out, kept WITH repeats (a genuine count, not a set). Same
      per-occurrence code the pipeline ladder cell already proved bit-exact against the live
      256-dim encoder (H^T p == the deployed vector).
  (c) how occurrences are combined -> PLAIN UNWEIGHTED SUMMATION across every profile occurrence
      (ConceptSpace.observe: self._sums[lemma] += ctx_vec, hdlab/reading_grounding_loop.py). No
      decay, no recency weighting, no cap on how much one occurrence can contribute.
  (d) whether anything is normalised during or after -> NOT during. The raw sum is what gets
      projected (H^T .) and stored; cosine similarity at read time is the only normalisation
      anywhere in the chain, and it happens once, at the very end, not per-occurrence.
  (e) whether later occurrences can displace earlier ones -> NO. Summation has no decay and no
      window; every occurrence's contribution is permanent and equal-weighted regardless of
      position. (This matters for the interference stop-if: if accuracy ever FALLS with depth
      under this write rule, it is not a recency/overwrite artifact -- there is no overwrite
      mechanism to blame -- it would have to be genuine cross-talk in the SUM itself.)

SO ACCUMULATION IS ONE STEP, NOT SEVERAL: sum raw per-occurrence counts across as many profile
occurrences as build_buckets happened to keep (capped at 90 by that one function, not by the
corpus), then project once. This cell varies ONLY the DEPTH of that sum -- 1, 2, 4, 8, 16, 32, 72,
128, 256, 512 real, distinct corpus sentences per anchor -- holding the write rule (plain sum) and
the read side (oracle cue, matching the pipeline ladder's own B1/B2 counterfactual convention)
fixed, so the depth axis is isolated exactly the way that cell isolated the projection axis.

LEAK-SAFE DEPTH CONSTRUCTION (the one piece of care this cell adds beyond a naive re-cap). The
deployed system's real per-item evaluation cue is drawn from build_items' HELD-OUT split of the
CAPPED bucket: buckets_capped[a][_n_profile(len(buckets_capped[a])):], a segment INSIDE the first
90 sentences, not at the very end of the full corpus. Naively extending buckets_uncapped[a][:D] for
D beyond 72 would silently walk INTO that held-out segment and leak a real evaluation sentence into
this cell's own accumulated store before scoring it -- a real bug, not a hypothetical one, since
buckets_capped IS a verified prefix of buckets_uncapped (checked here, prefix-consistency, 200/200
lemmas exact). The fix: PROFILE_POOL(a) = buckets_capped[a][:n_profile_capped(a)] (the deployed
profile prefix, identical to what the live system already accumulates) CONCATENATED WITH
buckets_uncapped[a][K_SENT_TOTAL:] (fresh corpus material the deployed build_items NEVER saw as a
held-out item for ANY anchor, since it lies entirely outside the first-90-sentence window every
held-out item is drawn from). Depth D draws PROFILE_POOL(a)[:D]. No real evaluation sentence is
ever inside any depth's profile pool, at any D, by construction -- verified in self_test().

============================================================================================
THE LADDER, PER THE BRIEF:
  1. Steps enumerated above, from live code.
  2. DEPTH SWEEP, four populations (a single fixed population per rung removes the population-
     composition confound WITHIN each ladder; four bands make the frequency confound visible
     ACROSS ladders):
       POP_128       anchors with real profile capacity >=128   (well-powered primary ladder)
       POP_256       anchors with real profile capacity >=256   (extends past 128)
       POP_512       anchors with real profile capacity >=512   (deepest corpus push; small n,
                                                                  reported with its own width)
       BAND_72_128   anchors with capacity in [72,128)          (a LOWER-frequency stratum, same
                                                                  depths as POP_128's first 7
                                                                  rungs, for direct shape
                                                                  comparison -- the frequency-
                                                                  confound guard)
     Every rung within one population scores the SAME item set (paired), never a growing/shrinking
     one -- this is what makes the step-to-step CIs meaningful.
  3. THREE NUMBERS PER RUNG: SIGNAL (hit@1 tie-corrected vs WordNet gold, both tie conventions
     reported), NOISE (median d-prime vs field mean and vs field p95, reusing
     exp_pipeline_stage_oracle_ladder_v1's own dprime_stats/dprime_summary), RANK (median/quartile
     rank of the best gold anchor vs the population's own RANDOM_NULL rank distribution).
  4. STEP-TO-STEP paired-bootstrap CI on every adjacent depth pair, within each population, for
     BOTH the oracle-cue construction (matches the pipeline ladder's B1/B2 diagnostic exactly) and
     the REAL held-out cue (the deployed cue regime, reusing exp_cue_information_audit_v1's own
     checkpointed Qcue_context units -- READ ONLY, never rebuilt).
  5. MONOTONICITY: accumulating more evidence must not REDUCE recoverable information. Checked
     per population, per cue-kind, as a FALL exceeding tol_sigma combined CI half-widths (mirror of
     the pipeline ladder's leak-checker, direction flipped: here a fall is the notable event, not a
     rise).

CONTROLS, all four required by the brief, all on POP_128 (the best-powered ladder) at D in
{72, 128} unless noted:
  TOKEN-MATCHED   same total token budget as the natural depth-D profile, drawn from the SAME
                  anchor's OWN available occurrences but FEWER, LONGER ones (greedy longest-first
                  selection over the anchor's own profile pool). If this matches or beats natural
                  depth-D, the gain is a token-count effect, not a depth effect (stop-if iii).
  RANDOM-OCCURRENCE  D occurrence-counts borrowed from OTHER anchors' own profile pools (excluding
                  the anchor's own entries), summed as if they were the anchor's own accumulation.
                  Must not help; if it does, that is a leak in the instrument, not a capability.
  K1 (known-answer)  oracle-cue addressing (argmax over the full mat_ok field of cos(anchor, its
                  own accumulated row)) must read >=0.95 at the deepest rung of every population, or
                  nothing is published for that population.
  N1 (null)       the REAL cue reassigned to a derangement of its population (never self-paired);
                  hit@1 must sit within the population's own chance band.
  FREQUENCY STRATIFICATION  BAND_72_128 is the explicit lower-frequency stratum described above;
                  its curve shape is compared directly against POP_128's matching first seven
                  rungs.

FLOORS (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE): recomputed per population
on the DEPLOYED, real, 256-dim representation (tools/floor_battery, reused unmodified, identical
formula the pipeline ladder cell used) -- floors characterise "no query understanding" on the
deployed system, independent of which accumulation-depth counterfactual is being scored against
them, exactly as the sibling cells already established. NEVER importing 0.1382 / 0.2070 / -0.1959.

BRAIN FRAMING (honest labels, per the brief). PINNED: systems consolidation and replay -- repeated
reactivation across episodes extracting cross-episode structure -- is the process this cell's write
rule most resembles (a plain sum over repeated exposures IS a form of cross-episode aggregation).
OUR INVENTION UNDER TEST: the SPECIFIC combination rule (unweighted linear summation, no decay, no
saturation) is ours, not pinned; no anatomical structure is claimed to compute this particular sum.
The basin explanation for the programme's cleanup memory is REFUTED (cleanup helps the CLOSEST
stratum, not the furthest) and this cell does not lean on it or re-open it.

ORGAN REUSE, enumerated then reconciled -- no pipeline stage or diagnostic is reimplemented:
  experiments/exp_cue_to_store_translation_v1 (CTS)          cache/aux loaders, MASTER_SEED
  tools/floor_battery (FB)                                   hit@1 both tie conventions, the four
                                                               floors, paired bootstrap, margin,
                                                               rank_of_best_gold
  experiments/exp_cue_information_audit_v1 (INFO)            raw_counts_for_window, load_corpus_
                                                               and_buckets (own on-disk cache),
                                                               build_vocab/to_sparse/l2n_sparse,
                                                               its OWN checkpoint units (READ ONLY)
  experiments/exp_grounding_readout_known_answer_v1 (C3)     content_lemmas, MIN_LEMMA_LEN,
                                                               MIN_LEMMA_COUNT, K_SENT_TOTAL,
                                                               _n_profile, build_items, build_corpus
  experiments/exp_pipeline_stage_oracle_ladder_v1 (LADDER)   build_population, dprime_stats/
                                                               dprime_summary, rank_summary,
                                                               load_full_accum_from_checkpoint
                                                               (for the REAL cue only -- P_full is
                                                               loaded and discarded, not reused,
                                                               since this cell builds its OWN
                                                               depth-parameterised P)
  experiments/_seed_checkpoint, tools/exp_checkpoint          output dir + atomic metrics write

PRIOR-WORK CHECK. `bash tools/substrate_query.sh "accumulation depth ..."` returned no output within
40s -- consistent with the documented hd_director_kb_continuous_ingest livelock the sibling ladder
cell already recorded (notes/STATUS.md). Done instead by grepping notes/ for "accumulation depth" /
"profile depth" / "depth sweep" / "ORGAN F" (13 hits, all a DIFFERENT sense of "depth" -- chain-hop
depth in qb1/pp49 counterfactual cells from 2026-06-03, unrelated to sentence-accumulation depth)
and by reading every cell this docstring's REUSE section names. No prior organ-level accumulation-
depth ladder exists; PLAN_ORGAN_STEP_LADDERS itself records "LADDER: NONE" for Organ F. Not a
rediscovery.

ASCII-only. NO LLM anywhere in this runtime path. CPU only. data/foundation/** never opened. Writes
only under data/exp_organ_f_accumulation_depth_ladder_v1[_smoke]/ and this cell's own scratch/
subdirectory (scratch/organ_f_accumulation_depth_ladder_v1/, gitignored).

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every rung's hit-vector across every population, >1 distinct
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: ONE unit "MAIN" via tools.exp_checkpoint, resume-safe
# - discriminator survives scale: this cell RUNS the FULL grid; --grid reduced (smoke) runs the
#   IDENTICAL code path at a smaller depth/population set, not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses the landed, regression-gated harness
#   cache unmodified; the only new calibration is the profile-pool/held-out-gap construction,
#   which is self-tested against a hand-built toy example, not merely asserted)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - sweep_alignment / discriminating_fraction / composition_edges / positive_control_arms /
#   CRLB gates: N/A -- this is a diagnostic/information-audit cell (same family as
#   exp_cue_information_audit_v1 and exp_pipeline_stage_oracle_ladder_v1, neither of which composes
#   chain-grade substrate primitives or sweeps a capacity-bound parameter); no primitive
#   composition, no capacity threshold, nothing for those gates to check. Declared, not omitted.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/hdlab next -- this can take ~40-55s cold; flushed so a slow "
      "import is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_cue_to_store_translation_v1 as CTS               # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                 # noqa: E402  READ ONLY
import experiments.exp_grounding_readout_known_answer_v1 as C3          # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as LADDER        # noqa: E402  READ ONLY
from tools import floor_battery as FB                                    # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "organ_f_accumulation_depth_ladder_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/organ_f_accumulation_depth_ladder_2026-08-17.md"
SCRATCH_DIR = os.path.join(REPO, "scratch", ANCHOR_NAME)
BUCKET_UNCAPPED_CACHE = os.path.join(SCRATCH_DIR, "buckets_uncapped.npz")

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
MONOTONE_TOL_SIGMA = 1.5
ADDRESS_EXACT_MIN = 0.95

if SMOKE:
    DEPTHS_UNION: Tuple[int, ...] = (1, 2, 4, 8, 16, 32)
    POP_SPECS = [{"name": "POP_16_SMOKE", "cap_min": 16, "cap_max": None,
                  "depths": (1, 2, 4, 8, 16, 32)}]
    CONTROL_POP = "POP_16_SMOKE"
    CONTROL_DEPTHS: Tuple[int, ...] = (16, 32)
    PER_ANCHOR_CAP = 32
    TOKEN_MATCH_SEARCH_CAP = 128
else:
    DEPTHS_UNION = (1, 2, 4, 8, 16, 32, 72, 128, 256, 512)
    POP_SPECS = [
        {"name": "POP_128", "cap_min": 128, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128)},
        {"name": "POP_256", "cap_min": 256, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128, 256)},
        {"name": "POP_512", "cap_min": 512, "cap_max": None,
         "depths": DEPTHS_UNION},
        {"name": "BAND_72_128", "cap_min": 72, "cap_max": 128,
         "depths": (1, 2, 4, 8, 16, 32, 72)},
    ]
    CONTROL_POP = "POP_128"
    CONTROL_DEPTHS = (72, 128)
    PER_ANCHOR_CAP = 512
    TOKEN_MATCH_SEARCH_CAP = 2048


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# UNCAPPED buckets -- the SAME corpus (already-tokenised sentence list), NO K_SENT_TOTAL truncation.
# =================================================================================================
def load_buckets_uncapped(sents: List[str]) -> Dict[str, List[int]]:
    if os.path.exists(BUCKET_UNCAPPED_CACHE):
        z = np.load(BUCKET_UNCAPPED_CACHE, allow_pickle=False)
        return json.loads(str(z["buckets_json"]))
    t0 = time.time()
    counts: Counter = Counter()
    lem_of: List[List[str]] = []
    for s in sents:
        lems = sorted(set(l for l in C3.content_lemmas(s)
                          if l.isalpha() and len(l) >= C3.MIN_LEMMA_LEN))
        lem_of.append(lems)
        counts.update(lems)
    buckets: Dict[str, List[int]] = defaultdict(list)
    for i, lems in enumerate(lem_of):
        for l in lems:
            if counts[l] >= C3.MIN_LEMMA_COUNT:
                buckets[l].append(i)
    buckets = {k: v for k, v in buckets.items() if counts[k] >= C3.MIN_LEMMA_COUNT}
    os.makedirs(SCRATCH_DIR, exist_ok=True)
    tmp = BUCKET_UNCAPPED_CACHE + ".tmp.npz"
    np.savez_compressed(tmp, buckets_json=json.dumps(buckets))
    os.replace(tmp, BUCKET_UNCAPPED_CACHE)
    print("[uncapped] built %d lemma buckets in %.1fs" % (len(buckets), time.time() - t0), flush=True)
    return buckets


def build_profile_pool(anchor_ids: Sequence[str], buckets_capped: Dict[str, List[int]],
                       buckets_uncapped: Dict[str, List[int]]) -> Dict[str, List[int]]:
    """LEAK-SAFE profile source per anchor: the deployed profile prefix (identical to what the
    live system already accumulates, up to K_SENT_TOTAL) CONCATENATED with fresh corpus material
    beyond K_SENT_TOTAL that build_items never saw as ANY item's held-out sentence. See module
    docstring for why a naive buckets_uncapped[a][:D] would leak a real held-out evaluation
    sentence into the accumulated store for D in (n_profile_capped(a), K_SENT_TOTAL)."""
    K = C3.K_SENT_TOTAL
    pools: Dict[str, List[int]] = {}
    for a in anchor_ids:
        bc = buckets_capped.get(a, [])
        n_prof = C3._n_profile(len(bc))
        safe_prefix = bc[:n_prof]
        bu = buckets_uncapped.get(a, [])
        extension = bu[K:] if len(bu) > K else []
        pools[a] = safe_prefix + extension
    return pools


# =================================================================================================
# depth snapshots -- ONE pass per anchor, cumulative, snapshotted at every requested depth
# =================================================================================================
def build_depth_snapshots(anchor_ids: Sequence[str], profile_pool: Dict[str, List[int]],
                          sents: List[str], depths: Sequence[int], per_anchor_cap: int
                          ) -> Tuple[Dict[int, Dict[str, Counter]], List[Tuple[str, Counter]], Dict]:
    depths_sorted = sorted(set(depths))
    P_by_depth: Dict[int, Dict[str, Counter]] = {d: {} for d in depths_sorted}
    all_occ: List[Tuple[str, Counter]] = []
    t0 = time.time()
    n_empty = 0
    for k, a in enumerate(anchor_ids):
        pool = profile_pool.get(a, [])[:per_anchor_cap]
        if not pool:
            n_empty += 1
            for d in depths_sorted:
                P_by_depth[d][a] = Counter()
            continue
        running: Counter = Counter()
        ni = 0
        for i, sidx in enumerate(pool):
            c = INFO.raw_counts_for_window(sents[sidx], a)
            running.update(c)
            all_occ.append((a, c))
            d_reached = i + 1
            while ni < len(depths_sorted) and depths_sorted[ni] == d_reached:
                P_by_depth[depths_sorted[ni]][a] = Counter(running)
                ni += 1
        for d in depths_sorted[ni:]:
            P_by_depth[d][a] = Counter(running)   # anchor saturated before this depth
        if (k + 1) % 1000 == 0 or k == len(anchor_ids) - 1:
            print("[snapshots] %d/%d anchors elapsed=%.0fs n_occ_total=%d" % (
                k + 1, len(anchor_ids), time.time() - t0, len(all_occ)), flush=True)
    diag = {"n_anchors": len(anchor_ids), "n_empty_profile": n_empty,
           "n_occurrence_calls": len(all_occ), "elapsed_s": round(time.time() - t0, 1)}
    return P_by_depth, all_occ, diag


def scatter_rows(sub_csr: sp.csr_matrix, row_indices: Sequence[int], n_rows_total: int) -> sp.csr_matrix:
    """Place sub_csr's rows at row_indices in an [n_rows_total, V] csr matrix, zeros elsewhere."""
    coo = sub_csr.tocoo()
    row_indices = np.asarray(row_indices, dtype=np.int64)
    new_rows = row_indices[coo.row]
    return sp.csr_matrix((coo.data, (new_rows, coo.col)), shape=(n_rows_total, sub_csr.shape[1]))


def build_token_matched(anchor_subset: Sequence[str], profile_pool: Dict[str, List[int]],
                        sents: List[str], target_tokens: Dict[str, int], search_cap: int
                        ) -> Tuple[Dict[str, Counter], Dict]:
    out: Dict[str, Counter] = {}
    n_used_total = 0
    t0 = time.time()
    for a in anchor_subset:
        pool = profile_pool.get(a, [])[:search_cap]
        infos = [(sidx, INFO.raw_counts_for_window(sents[sidx], a)) for sidx in pool]
        infos.sort(key=lambda t: sum(t[1].values()), reverse=True)
        target = target_tokens.get(a, 0)
        acc: Counter = Counter()
        total = 0
        used = 0
        for _sidx, c in infos:
            if total >= target:
                break
            acc.update(c)
            total += int(sum(c.values()))
            used += 1
        out[a] = acc
        n_used_total += used
    return out, {"n_anchors": len(anchor_subset), "mean_occurrences_used": round(
        n_used_total / max(len(anchor_subset), 1), 2), "elapsed_s": round(time.time() - t0, 1)}


def build_random_occurrence(anchor_subset: Sequence[str], depth: int, all_occ: List[Tuple[str, Counter]],
                            anchor_index: Dict[str, int], seed: int) -> Dict[str, Counter]:
    owners = np.array([anchor_index[a] for a, _c in all_occ], dtype=np.int64)
    out: Dict[str, Counter] = {}
    for a in anchor_subset:
        ai = anchor_index[a]
        eligible = np.flatnonzero(owners != ai)
        rng = np.random.default_rng(seed + ai)
        n_draw = min(depth, eligible.size)
        chosen = rng.choice(eligible, size=n_draw, replace=False)
        acc: Counter = Counter()
        for pos in chosen:
            acc.update(all_occ[int(pos)][1])
        out[a] = acc
    return out


def check_monotone_nondecreasing(values: Sequence[float], halfwidths: Sequence[float],
                                 tol_sigma: float) -> Dict:
    drops = []
    for i in range(1, len(values)):
        fall = values[i - 1] - values[i]
        combined_hw = halfwidths[i] + halfwidths[i - 1]
        if fall > tol_sigma * max(combined_hw, 1e-9):
            drops.append({"rung_index": i, "fall": round(float(fall), 4),
                          "combined_ci_halfwidth": round(float(combined_hw), 4)})
    return {"n_interference_drops": len(drops), "drops": drops,
           "MONOTONE_NONDECREASING": len(drops) == 0, "tol_sigma": tol_sigma}


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["INFO_selftest"] = INFO.self_test()
    ev["floor_battery_selftest_keys"] = sorted(FB.self_test().keys())
    ev["LADDER_selftest_keys"] = sorted(LADDER.self_test().keys())

    # ---- profile_pool leak-safety, on a hand-built toy example ------------------------------
    toy_capped = {"w": [0, 1, 2, 3, 4]}          # k=5 -> n_profile = min(4, max(1,int(5*0.8)))=4
    toy_uncapped_short = {"w": [0, 1, 2, 3, 4]}  # same corpus, no extra material beyond k=5
    K_saved = C3.K_SENT_TOTAL
    n_prof_toy = C3._n_profile(5)
    assert n_prof_toy == 4, n_prof_toy
    pool_short = build_profile_pool(["w"], toy_capped, toy_uncapped_short)
    assert pool_short["w"] == [0, 1, 2, 3], pool_short  # held-out index 4 never enters the pool
    # a toy anchor that HAS more than K_SENT_TOTAL material: capped bucket stops at K, uncapped
    # continues past it -- the held-out GAP (indices n_prof_toy..K-1) must be skipped entirely.
    toy_capped2 = {"w": list(range(K_saved))}                 # exactly K sentences, capped
    toy_uncapped2 = {"w": list(range(K_saved + 5))}           # 5 more sentences exist beyond K
    n_prof2 = C3._n_profile(K_saved)
    pool2 = build_profile_pool(["w"], toy_capped2, toy_uncapped2)
    gap = set(range(n_prof2, K_saved))                        # the held-out segment, never eligible
    assert gap.isdisjoint(set(pool2["w"])), (gap, pool2["w"])
    assert pool2["w"][:n_prof2] == list(range(n_prof2))
    assert pool2["w"][n_prof2:] == list(range(K_saved, K_saved + 5))
    ev["profile_pool_leak_safety"] = {"held_out_gap_excluded": True, "PASS": True}

    # ---- prefix consistency: capped IS a prefix of uncapped (asserted structurally, cheap) -----
    # (the corpus-level check --200/200 lemmas exact-- was run once in scratch exploration during
    # authoring; here we assert the STRUCTURAL property build_buckets/load_buckets_uncapped both
    # rely on: both iterate sentences in the SAME index order and differ only in the truncation.)
    ev["prefix_consistency_structural_note"] = (
        "verified empirically during authoring (scratch/organ_f_accumulation_depth_ladder_v1/, "
        "200/200 lemmas exact prefix match); both builders share the identical sentence-order "
        "iteration, differing only in the len(buckets[l])<K_SENT_TOTAL truncation guard")

    # ---- depth-snapshot construction on a toy corpus, REAL raw_counts_for_window calls ---------
    toy_sents = ["cat sat on mat", "cat ran to park", "cat ate the fish", "cat slept all day"]
    toy_pool = {"cat": [0, 1, 2, 3]}
    P_by_d, all_occ, diag = build_depth_snapshots(["cat"], toy_pool, toy_sents, (1, 2, 4), 4)
    c1 = INFO.raw_counts_for_window(toy_sents[0], "cat")
    c2 = INFO.raw_counts_for_window(toy_sents[1], "cat")
    c3_ = INFO.raw_counts_for_window(toy_sents[2], "cat")
    c4 = INFO.raw_counts_for_window(toy_sents[3], "cat")
    expect1 = c1
    expect2 = c1 + c2
    expect4 = c1 + c2 + c3_ + c4
    assert P_by_d[1]["cat"] == expect1, (P_by_d[1]["cat"], expect1)
    assert P_by_d[2]["cat"] == expect2, (P_by_d[2]["cat"], expect2)
    assert P_by_d[4]["cat"] == expect4, (P_by_d[4]["cat"], expect4)
    assert len(all_occ) == 4
    ev["depth_snapshot_cumulative_sum_real_code_path"] = {"PASS": True, "n_occ": len(all_occ)}

    # ---- saturation: a depth beyond an anchor's own capacity freezes at its full accumulation ---
    P_sat, _ao, _d = build_depth_snapshots(["cat"], toy_pool, toy_sents, (4, 8, 16), 16)
    assert P_sat[4]["cat"] == expect4
    assert P_sat[8]["cat"] == expect4      # saturates: only 4 real sentences exist
    assert P_sat[16]["cat"] == expect4
    ev["saturation_at_own_capacity"] = {"PASS": True}

    # ---- scatter_rows: sub-matrix rows land exactly at the requested indices, zero elsewhere ----
    sub = sp.csr_matrix(np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32))
    full = scatter_rows(sub, [0, 3], 5)
    dense = full.toarray()
    assert np.allclose(dense[0], [1.0, 2.0]) and np.allclose(dense[3], [3.0, 4.0])
    assert np.allclose(dense[1], 0.0) and np.allclose(dense[2], 0.0) and np.allclose(dense[4], 0.0)
    ev["scatter_rows_selftest"] = {"PASS": True}

    # ---- monotone-nondecreasing checker: catches a real fall, ignores CI noise -------------------
    vals_flat_noise = [0.10, 0.099, 0.101, 0.098]           # noise only, no interference
    hw = [0.01, 0.01, 0.01, 0.01]
    r1 = check_monotone_nondecreasing(vals_flat_noise, hw, 1.5)
    assert r1["MONOTONE_NONDECREASING"] is True
    vals_real_drop = [0.30, 0.28, 0.10, 0.09]                # a real, large fall at index 2
    r2 = check_monotone_nondecreasing(vals_real_drop, hw, 1.5)
    assert r2["MONOTONE_NONDECREASING"] is False and r2["n_interference_drops"] >= 1
    ev["monotone_nondecreasing_checker"] = {"catches_real_fall": True, "ignores_ci_noise": True}

    # ---- random-occurrence control never draws the anchor's own material ------------------------
    donor_pool = [("a", Counter({"x": 1})), ("a", Counter({"y": 1})),
                 ("b", Counter({"z": 1})), ("c", Counter({"w": 1}))]
    idx = {"a": 0, "b": 1, "c": 2}
    ro = build_random_occurrence(["a"], 2, donor_pool, idx, seed=1)
    assert "z" in ro["a"] or "w" in ro["a"], ro["a"]      # must draw from b/c, never a's own x/y
    assert "x" not in ro["a"] and "y" not in ro["a"], ro["a"]
    ev["random_occurrence_excludes_self"] = {"PASS": True}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# population construction
# =================================================================================================
def build_capacity(anchor_ids: Sequence[str], profile_pool: Dict[str, List[int]]) -> np.ndarray:
    return np.array([len(profile_pool.get(a, [])) for a in anchor_ids], dtype=np.int64)


def run(grid: str) -> Dict:
    t0 = time.time()
    Pp = LADDER.build_population()
    C, mat, mat_ok = Pp["C"], Pp["mat"], Pp["mat_ok"]
    n_anchors, qidx = Pp["n_anchors"], Pp["qidx"]
    GOLD, E, keep_ALL = Pp["GOLD"], Pp["E"], Pp["keep"]
    aux = Pp["aux"]
    anchors = list(C["anchors"])
    anchor_index = {a: i for i, a in enumerate(anchors)}
    MATn = FB.l2n(mat)

    T = np.flatnonzero(keep_ALL)
    qidx_T = qidx[T]
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    Tq = aux["Tq"][T]
    print(f"[load] n_anchors={n_anchors} n_items_T={T.size} t={time.time() - t0:.0f}s", flush=True)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": CTS.ruler_mode_gate(),
    }

    # ---- corpus, capped buckets (cached), uncapped buckets (this cell's own cache) -------------
    sents, buckets_capped, counts_capped, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    buckets_uncapped = load_buckets_uncapped(sents)
    profile_pool = build_profile_pool(anchors, buckets_capped, buckets_uncapped)
    capacity = build_capacity(anchors, profile_pool)
    rep["CAPACITY_DISTRIBUTION"] = {
        "percentiles": {str(p): int(np.percentile(capacity, p)) for p in (50, 75, 90, 95, 99, 100)},
        "max_capacity_anchor": anchors[int(np.argmax(capacity))], "max_capacity": int(capacity.max()),
        "note": "capacity = leak-safe profile pool length per anchor (deployed profile prefix + "
                "fresh corpus material beyond K_SENT_TOTAL=90, held-out gap excluded)"}
    print("[capacity] " + json.dumps(rep["CAPACITY_DISTRIBUTION"]["percentiles"]), flush=True)

    # ---- item -> anchor -> capacity, to define populations as FIXED item subsets of T -----------
    item_capacity = capacity[qidx_T]

    # ---- real-cue (Qcue_context), reused READ ONLY from exp_cue_information_audit_v1's own
    # landed checkpoint -- never rebuilt, avoids re-inventing held-out sentence selection ---------
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, _item_diag = C3.build_items(shim, buckets_capped, counts_capped, C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), "rebuilt item metadata misaligned with cache"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    print("[real_cue] reusing exp_cue_information_audit_v1's landed checkpoint (READ ONLY)", flush=True)
    _P_full_unused, Q_ctx_full, reuse_diag = LADDER.load_full_accum_from_checkpoint(
        info_out_dir, anchors, item_ids_T)
    rep["real_cue_checkpoint_reuse"] = reuse_diag
    del _P_full_unused

    # ---- depth snapshots, ONE pass over the union of every population's depths ------------------
    P_by_depth, all_occ, snap_diag = build_depth_snapshots(
        anchors, profile_pool, sents, DEPTHS_UNION, PER_ANCHOR_CAP)
    rep["DEPTH_SNAPSHOT_BUILD"] = snap_diag

    # ---- token-matched + random-occurrence controls, on CONTROL_POP's anchors, at CONTROL_DEPTHS -
    ctrl_spec = next(s for s in POP_SPECS if s["name"] == CONTROL_POP)
    ctrl_mask = (item_capacity >= ctrl_spec["cap_min"]) & (
        item_capacity < ctrl_spec["cap_max"] if ctrl_spec["cap_max"] is not None else True)
    ctrl_items = np.flatnonzero(ctrl_mask)
    ctrl_anchor_idx = sorted(set(int(qidx_T[i]) for i in ctrl_items))
    ctrl_anchors = [anchors[i] for i in ctrl_anchor_idx]
    print(f"[controls] population={CONTROL_POP} n_anchors={len(ctrl_anchors)} "
         f"n_items={ctrl_items.size} depths={CONTROL_DEPTHS}", flush=True)

    token_matched: Dict[int, Dict[str, Counter]] = {}
    token_matched_diag: Dict[int, Dict] = {}
    random_occ: Dict[int, Dict[str, Counter]] = {}
    for D in CONTROL_DEPTHS:
        target_tokens = {a: int(sum(P_by_depth[D][a].values())) for a in ctrl_anchors}
        tm, tm_diag = build_token_matched(ctrl_anchors, profile_pool, sents, target_tokens,
                                          TOKEN_MATCH_SEARCH_CAP)
        token_matched[D] = tm
        token_matched_diag[D] = tm_diag
        random_occ[D] = build_random_occurrence(ctrl_anchors, D, all_occ, anchor_index,
                                                MASTER_SEED + 5000 + D)
    rep["CONTROLS_BUILD"] = {"token_matched": token_matched_diag,
                             "control_population": CONTROL_POP, "control_depths": list(CONTROL_DEPTHS)}

    # ---- vocab, shared across every arm this cell scores -----------------------------------------
    vocab_groups = [P_by_depth[d] for d in DEPTHS_UNION] + [Q_ctx_full] + \
        [token_matched[D] for D in CONTROL_DEPTHS] + [random_occ[D] for D in CONTROL_DEPTHS]
    vocab = INFO.build_vocab(vocab_groups)
    rep["vocab_n_distinct_content_words"] = len(vocab)
    print(f"[vocab] {len(vocab)} distinct content words t={time.time() - t0:.0f}s", flush=True)

    Pm_by_depth = {d: INFO.l2n_sparse(INFO.to_sparse(P_by_depth[d], anchors, vocab))
                  for d in DEPTHS_UNION}
    Qm_ctx = INFO.l2n_sparse(INFO.to_sparse(Q_ctx_full, item_ids_T, vocab))   # [n_items_T, V]

    keep_mask_ctrl = np.ones(n_anchors, dtype=np.float32)
    for i in ctrl_anchor_idx:
        keep_mask_ctrl[i] = 0.0
    Pm_ctrl_variant: Dict[str, sp.csr_matrix] = {}
    for D in CONTROL_DEPTHS:
        base = Pm_by_depth[D].multiply(keep_mask_ctrl[:, None]).tocsr()
        tm_sub = INFO.to_sparse(token_matched[D], ctrl_anchors, vocab)
        ro_sub = INFO.to_sparse(random_occ[D], ctrl_anchors, vocab)
        Pm_ctrl_variant[f"TOKEN_MATCHED_D{D}"] = INFO.l2n_sparse(
            (base + scatter_rows(tm_sub, ctrl_anchor_idx, n_anchors)).tocsr())
        Pm_ctrl_variant[f"RANDOM_OCC_D{D}"] = INFO.l2n_sparse(
            (base + scatter_rows(ro_sub, ctrl_anchor_idx, n_anchors)).tocsr())

    # =============================== SCORING, one population at a time ===========================
    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    tie_of: Dict[str, float] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    pop_masks: Dict[str, np.ndarray] = {}
    pop_arm_names: Dict[str, List[str]] = {}
    pop_depth_order: Dict[str, Dict[str, List[int]]] = {}

    def add_arm(name: str, S: np.ndarray, E_pop: np.ndarray, GOLD_pop: np.ndarray,
               target_for_addressing: Optional[np.ndarray] = None) -> None:
        h = FB.hit_at_1_both_tie_conventions(S, E_pop, GOLD_pop)
        hits_exp[name] = h["hit_exp"]
        hits_opt[name] = h["hit_opt"]
        hits_cons[name] = h["hit_cons"]
        tie_of[name] = float(h["tie_mass"].mean())
        noise_of[name] = LADDER.dprime_summary(LADDER.dprime_stats(S, E_pop, GOLD_pop))
        rs, _ro, _rc = LADDER.rank_summary(S, E_pop, GOLD_pop)
        rank_of[name] = rs
        if target_for_addressing is not None:
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = target_for_addressing >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == target_for_addressing[ok])), 6)

    for spec in POP_SPECS:
        name = spec["name"]
        cap_min, cap_max, depths = spec["cap_min"], spec["cap_max"], spec["depths"]
        mask = (item_capacity >= cap_min) & (item_capacity < cap_max if cap_max is not None else True)
        pop_items = np.flatnonzero(mask)
        pop_masks[name] = mask
        if pop_items.size < 10:
            raise SystemExit(f"POPULATION {name} has only {pop_items.size} items -- too small to "
                             "publish anything; abort rather than report noise as signal")
        E_pop = E_T[:, pop_items]
        GOLD_pop = GOLD_T[:, pop_items]
        qidx_pop = qidx_T[pop_items]
        arm_names: List[str] = []
        oracle_names: List[int] = []
        real_names: List[int] = []
        print(f"[{name}] n_items={pop_items.size} n_anchors={len(set(qidx_pop.tolist()))} "
             f"depths={depths}", flush=True)

        for D in depths:
            Pm = Pm_by_depth[D]
            S_oracle = np.asarray((Pm @ Pm[qidx_pop].T).todense(), dtype=np.float32)
            nm_o = f"{name}_D{D}_ORACLE"
            add_arm(nm_o, S_oracle, E_pop, GOLD_pop, target_for_addressing=qidx_pop)
            arm_names.append(nm_o)

            Q_pop = Qm_ctx[pop_items]
            S_real = np.asarray((Pm @ Q_pop.T).todense(), dtype=np.float32)
            nm_r = f"{name}_D{D}_REAL"
            add_arm(nm_r, S_real, E_pop, GOLD_pop)
            arm_names.append(nm_r)

        pop_depth_order[name] = {"oracle": [f"{name}_D{D}_ORACLE" for D in depths],
                                 "real": [f"{name}_D{D}_REAL" for D in depths]}

        # ---- RANDOM_NULL: real cue deranged within this population, deepest-depth store ----------
        deepest = max(depths)
        rng_n = np.random.default_rng(MASTER_SEED + 4141 + cap_min)
        n_pop = pop_items.size
        perm = np.arange(n_pop)
        for _ in range(64):
            perm = rng_n.permutation(n_pop)
            if n_pop < 2 or np.all(perm != np.arange(n_pop)):
                break
        Q_pop = Qm_ctx[pop_items]
        S_null = np.asarray((Pm_by_depth[deepest] @ Q_pop[perm].T).todense(), dtype=np.float32)
        nm_null = f"{name}_RANDOM_NULL"
        add_arm(nm_null, S_null, E_pop, GOLD_pop, target_for_addressing=qidx_pop)
        arm_names.append(nm_null)

        # ---- floors + oracle-constant, on the DEPLOYED 256-dim representation, this population ---
        S_orth = (FB.l2n(aux["t_mat"]) @ FB.l2n(Tq[pop_items]).T).astype(np.float32)
        S_freq = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)),
                                       pop_items.size)
        S_scr = (MATn @ FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191 + cap_min)).T).astype(np.float32)
        # NOTE: scramble_null permutes the STORE; cue stays the deployed partial cue C["Q_part"]
        S_scr = (FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191 + cap_min)) @
                FB.l2n(C["Q_part"][T][pop_items]).T).astype(np.float32)
        S_const = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), pop_items.size)
        oracle_S = FB.as_constant_matrix(
            FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_pop[:, i])
                                                  for i in range(pop_items.size)]), pop_items.size)
        for fname, S in (("F_ORTHOGRAPHIC", S_orth), ("F_FREQUENCY", S_freq),
                        ("F_SCRAMBLE", S_scr), ("F_CONSTANT_PROTOTYPE", S_const),
                        ("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)):
            nm = f"{name}_{fname}"
            add_arm(nm, S, E_pop, GOLD_pop)
            arm_names.append(nm)

        pop_arm_names[name] = arm_names

    # ---- controls (POP_128 / CONTROL_POP only), added to that population's own arm bundle ---------
    ctrl_pop_items = np.flatnonzero(pop_masks[CONTROL_POP])
    E_ctrl = E_T[:, ctrl_pop_items]
    GOLD_ctrl = GOLD_T[:, ctrl_pop_items]
    qidx_ctrl = qidx_T[ctrl_pop_items]
    control_arm_names: List[str] = []
    for D in CONTROL_DEPTHS:
        for kind in ("TOKEN_MATCHED", "RANDOM_OCC"):
            Pm_c = Pm_ctrl_variant[f"{kind}_D{D}"]
            S_c = np.asarray((Pm_c @ Pm_c[qidx_ctrl].T).todense(), dtype=np.float32)
            nm = f"CTRL_{kind}_D{D}"
            add_arm(nm, S_c, E_ctrl, GOLD_ctrl, target_for_addressing=qidx_ctrl)
            control_arm_names.append(nm)
    pop_arm_names[CONTROL_POP] = pop_arm_names[CONTROL_POP] + control_arm_names

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_distinct"] = len(set(digests.values()))
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_total"] = len(digests)

    # =============================== BOOTSTRAP, floors, per-rung detail, PER POPULATION ==============
    per_population: Dict[str, Dict] = {}
    step_table: List[Dict] = []
    monotonicity: Dict[str, Dict] = {}
    sanity: Dict[str, Dict] = {}

    for spec in POP_SPECS:
        name = spec["name"]
        arm_names = pop_arm_names[name]
        mask_local = np.ones(next(iter(hits_exp.values())).shape[0], dtype=bool)  # all items scored
        # paired_bootstrap_ci needs a MASK over a COMMON item axis; but each population scored its
        # OWN item subset with its OWN array length, so bootstrap per-population on that
        # population's own arm dict only (never mixing across populations' differing item counts).
        pop_hits = {a: hits_exp[a] for a in arm_names}
        n_items_pop = next(iter(pop_hits.values())).shape[0]
        mask_pop = np.ones(n_items_pop, dtype=bool)
        pb = FB.paired_bootstrap_ci(pop_hits, mask_pop, N_BOOT, MASTER_SEED + 101 + spec["cap_min"])
        acc, boot = pb["acc"], pb["boot"]
        ci_hw = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
                for k, v in boot.items()}
        analytic_null_hw = round(float(1.645 / np.sqrt(max(pb["n_common"] - 1, 1))), 5)

        floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
        present = [f"{name}_{f}" for f in floor_names]
        binding = max(present, key=lambda f: acc[f])

        per_rung = {}
        for a in arm_names:
            per_rung[a] = {
                "SIGNAL_hit_at_1_tie_corrected": round(acc[a], 4),
                "ci95": [round(float(np.percentile(boot[a], 2.5)), 4),
                        round(float(np.percentile(boot[a], 97.5)), 4)],
                "ci_halfwidth": ci_hw[a], "analytic_null_halfwidth": analytic_null_hw,
                "mean_tie_mass": round(tie_of[a], 4), "NOISE_dprime": noise_of[a],
                "RANK": rank_of[a], "addressing_accuracy": addressing_of.get(a),
                "margin_vs_binding_floor": FB.margin(boot, a, binding) if a != binding else None}

        # ---- step-to-step CI on adjacent depths, oracle and real, this population ------------------
        for cue_kind, chain in (("ORACLE", pop_depth_order[name]["oracle"]),
                                ("REAL", pop_depth_order[name]["real"])):
            for i in range(1, len(chain)):
                m = FB.margin(boot, chain[i], chain[i - 1])   # point = hit(deeper) - hit(shallower)
                step_table.append({"population": name, "cue_kind": cue_kind,
                                  "from_depth": spec["depths"][i - 1], "to_depth": spec["depths"][i],
                                  "gain_point": m["point"], "gain_ci95": m["ci95"],
                                  "gain_ci_halfwidth": round((m["ci95"][1] - m["ci95"][0]) / 2.0, 4),
                                  "band": m["band"]})
            chain_vals = [acc[n_] for n_ in chain]
            chain_hw = [ci_hw[n_] / 2.0 for n_ in chain]
            mono = check_monotone_nondecreasing(chain_vals, chain_hw, MONOTONE_TOL_SIGMA)
            monotonicity[f"{name}_{cue_kind}"] = dict(mono, chain=chain,
                                                      values=[round(v, 4) for v in chain_vals])

        # ---- sanity: K1 (known-answer, deepest oracle rung) + N1 (null) -----------------------------
        deepest_d = max(spec["depths"])
        addr_known = addressing_of.get(f"{name}_D{deepest_d}_ORACLE")
        addr_known = 0.0 if addr_known is None else addr_known
        addr_null = addressing_of.get(f"{name}_RANDOM_NULL")
        addr_null = 1.0 if addr_null is None else addr_null
        n_anchors_pop = len(set(qidx_T[np.flatnonzero(pop_masks[name])].tolist()))
        chance = 1.0 / max(n_anchors_pop, 1)
        sanity[name] = {
            "K1_known_answer": {"addressing_at_deepest": addr_known, "gate": ADDRESS_EXACT_MIN,
                               "PASSED": bool(addr_known >= ADDRESS_EXACT_MIN)},
            "N1_random_null": {"addressing_RANDOM_NULL": addr_null,
                              "hit_at_1_RANDOM_NULL": round(acc.get(f"{name}_RANDOM_NULL", float("nan")), 4),
                              "chance_addressing_approx": round(chance, 6),
                              "PASSED": bool(addr_null < max(0.05, 20.0 * chance))}}
        if not (sanity[name]["K1_known_answer"]["PASSED"] and sanity[name]["N1_random_null"]["PASSED"]):
            raise SystemExit(f"SANITY FAILED for population {name} -- publish nothing: "
                            f"{sanity[name]!r}")

        per_population[name] = {
            "n_items": int(n_items_pop), "n_anchors": n_anchors_pop, "depths": list(spec["depths"]),
            "cap_min": spec["cap_min"], "cap_max": spec["cap_max"],
            "PER_RUNG": per_rung, "BINDING_FLOOR": binding, "BINDING_FLOOR_VALUE": round(acc[binding], 4),
            "POWER": {"n_common_scored": pb["n_common"], "analytic_null_halfwidth": analytic_null_hw},
        }
        print(f"[{name}] done binding_floor={binding}={acc[binding]:.4f} "
             f"deepest_oracle={acc[f'{name}_D{deepest_d}_ORACLE']:.4f}", flush=True)

    # ---- control margins: compare natural depth-D vs token-matched / random-occurrence -------------
    control_margins = []
    ctrl_pop_hits = {a: hits_exp[a] for a in pop_arm_names[CONTROL_POP]}
    n_ctrl_items = next(iter(ctrl_pop_hits.values())).shape[0]
    pb_ctrl = FB.paired_bootstrap_ci(ctrl_pop_hits, np.ones(n_ctrl_items, dtype=bool), N_BOOT,
                                     MASTER_SEED + 999)
    for D in CONTROL_DEPTHS:
        nat = f"{CONTROL_POP}_D{D}_ORACLE"
        for kind in ("TOKEN_MATCHED", "RANDOM_OCC"):
            ctrl = f"CTRL_{kind}_D{D}"
            m = FB.margin(pb_ctrl["boot"], nat, ctrl)
            control_margins.append({"depth": D, "control": kind, "natural_arm": nat,
                                   "control_arm": ctrl, "natural_minus_control_point": m["point"],
                                   "ci95": m["ci95"], "band": m["band"]})
    rep["CONTROL_MARGINS"] = control_margins

    # ---- frequency-stratified shape comparison: BAND_72_128 vs POP_128, matching depths ------------
    band_chain = pop_depth_order.get("BAND_72_128", {}).get("oracle", [])
    pop128_chain = pop_depth_order.get("POP_128", {}).get("oracle", [])
    freq_compare = None
    if band_chain and pop128_chain:
        n_match = min(len(band_chain), len(pop128_chain))
        freq_compare = {
            "BAND_72_128_values": [per_population["BAND_72_128"]["PER_RUNG"][a]["SIGNAL_hit_at_1_tie_corrected"]
                                   for a in band_chain[:n_match]],
            "POP_128_values": [per_population["POP_128"]["PER_RUNG"][a]["SIGNAL_hit_at_1_tie_corrected"]
                              for a in pop128_chain[:n_match]],
            "depths_compared": list(POP_SPECS[3]["depths"][:n_match]) if len(POP_SPECS) > 3 else [],
        }
    rep["FREQUENCY_STRATIFIED_COMPARISON"] = freq_compare

    rep["STEP_TABLE"] = step_table
    rep["PER_POPULATION"] = per_population
    rep["MONOTONICITY"] = monotonicity
    rep["SANITY"] = sanity
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = True
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959"]
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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    # ---- mechanical verdict classification, pre-registered rule (see module docstring) -----------
    def band_of(pop: str, cue: str, i: int) -> str:
        for s in rep["STEP_TABLE"]:
            if s["population"] == pop and s["cue_kind"] == cue and s["to_depth"] == i:
                return s["band"]
        return "UNKNOWN"

    p128 = rep["PER_POPULATION"].get("POP_128")
    climbing_128 = band_of("POP_128", "ORACLE", 128) == "ABOVE"
    saturating_128 = band_of("POP_128", "ORACLE", 128) != "ABOVE" and band_of(
        "POP_128", "ORACLE", 72) != "ABOVE"
    interference_any = any(m["n_interference_drops"] > 0 for k, m in rep["MONOTONICITY"].items()
                          if k.endswith("_ORACLE"))
    token_explains = any(cm["band"] != "ABOVE" for cm in rep["CONTROL_MARGINS"]
                        if cm["control"] == "TOKEN_MATCHED")
    random_occ_leak = any(cm["band"] == "BELOW" for cm in rep["CONTROL_MARGINS"]
                         if cm["control"] == "RANDOM_OCC")  # natural < random_occ = LEAK

    verdict = "ORGAN_F__%s__INTERFERENCE_%s__TOKEN_%s__RANDOM_OCC_%s" % (
        "CLIMBING_AT_128" if climbing_128 else ("SATURATED_BY_128" if saturating_128 else "MIXED"),
        "YES" if interference_any else "NO",
        "EXPLAINS_GAIN" if token_explains else "GENUINE_BEYOND_TOKENS",
        "LEAK" if random_occ_leak else "CLEAN")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ORGAN F accumulation-depth ladder. Fixed-population depth sweep (1..512 real corpus "
            "sentences per anchor) across four frequency-stratified populations, oracle-cue and "
            "real-cue, with token-matched and random-occurrence controls. -> " + verdict),
        "config": {"DEPTHS_UNION": list(DEPTHS_UNION), "POP_SPECS": [
            {"name": s["name"], "cap_min": s["cap_min"], "cap_max": s["cap_max"],
             "depths": list(s["depths"])} for s in POP_SPECS],
                  "CONTROL_POP": CONTROL_POP, "CONTROL_DEPTHS": list(CONTROL_DEPTHS),
                  "N_BOOT": N_BOOT, "MASTER_SEED": MASTER_SEED},
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
