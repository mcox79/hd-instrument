"""exp_organ_f_deep_reading_partialcue_ladder_v1 -- ORGAN F, REVISED ORDER-OF-WORK ITEM 3
(notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.4): RAISE THE ARBITRARY DEPTH CAP AND RE-MEASURE
END TO END ON THE REAL PARTIAL CUE, WITH NESTED POPULATIONS SO A DEEP-VS-SHALLOW COMPARISON IS PAIRED.

WHY THIS CELL EXISTS. `exp_organ_f_accumulation_depth_ladder_v1` (commit 379c42833) found the
accumulation gradient still CI-separated CLIMBING at 72->128 sentences/anchor (+0.0503
[+0.0139,+0.0861]), but (a) its headline was the ORACLE cue (query = the item's own accumulated
store row), not the REAL PARTIAL CUE the deployed system actually uses at inference; (b) its four
populations were defined independently by capacity band, so a "72 vs 512" comparison crossed
different anchor sets and the frequency confound was only checked QUALITATIVELY (BAND_72_128's shape
by eye), never as a formal same-item paired margin; (c) it stopped at 512 (n=43) without checking
whether the corpus supports a still-deeper, still-resolvable rung; (d) it never measured winner
COMPOSITION (WordNet relation / co-occurrence) as a function of depth, so "depth buys accuracy" and
"depth buys ranking-not-meaning" were never distinguished. This cell fixes all four, reusing the
leak-safe machinery verbatim rather than re-deriving it.

============================================================================================
LEAK-SAFETY, REUSED VERBATIM, NOT RE-DERIVED. `experiments.exp_organ_f_accumulation_depth_ladder_v1`
(OLD below) already found and fixed a real leak: the deployed held-out cue sentence sits INSIDE the
first-90-sentence collection window, not at the corpus end, so naively extending buckets_uncapped[a]
[:D] for D>90 would pull a real evaluation sentence into the accumulated store before scoring it. OLD
built `build_profile_pool` to skip that gap (deployed profile prefix + fresh material strictly beyond
K_SENT_TOTAL=90) and self-tested it against a hand-built toy example with a real gap. This cell calls
OLD.build_profile_pool, OLD.load_buckets_uncapped, OLD.build_depth_snapshots, OLD.scatter_rows,
OLD.build_token_matched, OLD.build_random_occurrence, OLD.check_monotone_nondecreasing,
OLD.build_capacity UNCHANGED -- reused as a library, per the brief's explicit instruction. This
cell's own self_test() re-runs OLD's leak-safety fixture (not re-asserted differently) plus the NEW
constructions this cell adds (nested-population monotonicity, cross-population restriction margin,
composition reuse). Leak-safety is therefore verified by construction (identical code path) AND by
self-test, at every rung including the new 768 rung.

============================================================================================
WHAT'S NEW VS THE SIBLING (four changes, each answering one gap above):

1. NESTED POPULATIONS, not independent capacity bands. POP_72 (cap>=72, the incumbent operating
   point) contains POP_128 (cap>=128) contains POP_256 (cap>=256) contains POP_512 (cap>=512)
   contains POP_768 (cap>=768, the corpus's practical edge -- measured directly below). Because
   nesting is via a capacity THRESHOLD on the item's own query anchor, every deeper population's item
   set is a TRUE SUBSET of every shallower one's -- verified in self_test(). This lets a single global
   score computed once per depth (over the FULL open pool, not re-scored per population) be sliced by
   ANY population's boolean mask for reporting, so a "72 vs 768, same items" comparison is a genuine
   PAIRED bootstrap margin on IDENTICAL items differing only in accumulation depth, not a comparison
   across different anchor sets. This is the fix for gap (b): CROSS_POPULATION_RESTRICTION_TABLE
   below reports, for every deep population, (i) the SPAN margin baseline-depth-72 -> its own deepest
   depth, PAIRED on that population's own items (the valid deep-vs-shallow comparison the brief
   requires), and (ii) the UNPAIRED composition check -- POP_72's full-population D=72 accuracy
   (n=694) side by side with the SAME D=72 arm restricted to the deep population's own subset (n as
   small as 17) -- explicitly labelled UNPAIRED (different item counts) so it is never read as a
   paired test.

2. DEEPEST LEAK-SAFE, RESOLVABLE RUNG MEASURED DIRECTLY, NOT ASSUMED. Capacity counted directly off
   the SAME leak-safe profile pool OLD built (scratch/organ_f_accumulation_depth_ladder_v1/
   buckets_uncapped.npz, reused unmodified): item-level population sizes at cap>=768 / 1024 / 1536 /
   2048 are 17 / 9 / 4 / 0 (measured once during authoring, reproduced by this cell's own
   CAPACITY_DISTRIBUTION report). 512 is real-answerable (n=43, as OLD found); 768 is the corpus's
   absolute edge with anything worth calling a population (n=17, explicitly UNDERPOWERED, reported
   with full CI half-width, never called saturated); 1024+ is too small (n<10) to report as anything
   but a capacity fact. POP_768 is included as a headline rung SO THIS IS STATED WITH EVIDENCE, not
   asserted from the sibling's percentile table.

3. THE REAL PARTIAL CUE IS THE PRIMARY MEASURE, oracle reported BESIDE it, never instead of it. Both
   cue kinds are scored at every depth for every population (matching OLD's own convention of scoring
   both), but every headline number, the floor-clearing check, and the verdict string are keyed off
   REAL_CUE the deployed regime is Qcue_context, reused READ-ONLY from
   `exp_cue_information_audit_v1`'s own checkpoint via LADDER.load_full_accum_from_checkpoint, exactly
   as OLD does -- never rebuilt.

4. WINNER COMPOSITION AT EVERY DEPTH, on the REAL cue. `exp_writerule_step_ladder_v1`
   (WR below) already built and self-tested `wordnet_relation_composition` and
   `syntagmatic_jaccard_composition` (its own C1/C2-style instruments) and measured them at 5 FIXED
   write-rule steps; this cell calls those SAME functions, reused verbatim, but sweeps them across
   the accumulation-DEPTH axis instead, on POP_72 (baseline scale, n=694, for direct comparability to
   WR's own reported baselines: 79.3% no-relation, 66.0%->94.4% co-occurrence share) and POP_512 (deep
   scale, n=43) so a composition trend is visible at both a well-powered and a maximally-deep
   population.

ORGAN REUSE, enumerated then reconciled -- nothing above is reimplemented:
  experiments.exp_organ_f_accumulation_depth_ladder_v1 (OLD)   load_buckets_uncapped,
    build_profile_pool, build_depth_snapshots, scatter_rows, build_token_matched,
    build_random_occurrence, check_monotone_nondecreasing, build_capacity, BUCKET_UNCAPPED_CACHE
  experiments.exp_writerule_step_ladder_v1 (WR)   wordnet_relation_composition,
    syntagmatic_jaccard_composition
  experiments.exp_cue_information_audit_v1 (INFO)   raw_counts_for_window, load_corpus_and_buckets,
    build_vocab, to_sparse, l2n_sparse, _ShimSpace, self_test
  experiments.exp_grounding_readout_known_answer_v1 (via INFO.C3)   content_lemmas, MIN_LEMMA_LEN,
    MIN_LEMMA_COUNT, K_SENT_TOTAL, _n_profile, build_items, MAX_ITEMS
  experiments.exp_pipeline_stage_oracle_ladder_v1 (LADDER)   build_population, dprime_stats,
    dprime_summary, rank_summary, load_full_accum_from_checkpoint, self_test, CTS
  hdlab.reading_grounding_loop   content_lemmas, normalize_lemma (for the co-occurrence index "where")
  tools.floor_battery (FB)   hit_at_1_both_tie_conventions, the four floors, paired_bootstrap_ci,
    margin, as_constant_matrix, l2n, self_test
  experiments._seed_checkpoint, tools.exp_checkpoint   output dir + atomic metrics write + resume

ANOTHER AGENT IS RUNNING experiments/exp_organ_f_noncollapsing_accumulation_v1.py CONCURRENTLY (per
the coordinator's brief). This cell uses a DISTINCT filename, writes only to
data/exp_organ_f_deep_reading_partialcue_ladder_v1[_smoke]/ and its own
scratch/organ_f_deep_reading_partialcue_ladder_v1/ subdirectory, and does not import or edit that
sibling cell's file.

PRIOR-WORK CHECK. `bash tools/substrate_query.sh "accumulation depth real partial cue nested
population winner composition"` returned no output within 45s -- the same documented
hd_director_kb_continuous_ingest livelock OLD and its own sibling ladder already recorded (see
notes/STATUS.md). Read PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.4 (the routing brief for this
exact cell), OLD's full source + its findings note, and WR's full source + its findings note (all
four read end-to-end before authoring). No prior cell sweeps accumulation depth past 512 on the real
partial cue with nested populations; not a rediscovery.

BRAIN FRAMING (unchanged from OLD, restated so this cell states its own labels rather than
inheriting them silently). PINNED: systems consolidation and replay -- repeated reactivation across
episodes extracting cross-episode structure -- is the process a plain sum over repeated exposures
most resembles. OUR INVENTION UNDER TEST: the specific unweighted-linear-summation combination rule,
no decay, no saturation; no anatomical structure is claimed to compute this particular sum. The
basin explanation for the programme's cleanup memory is REFUTED elsewhere and not leaned on here.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. data/foundation/
never opened. Writes only under data/exp_organ_f_deep_reading_partialcue_ladder_v1[_smoke]/ and this
cell's own scratch/ subdirectory (gitignored).

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every depth/cue-kind/floor hit-vector, >1 distinct, asserted
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: outer "MAIN" unit wraps run() (tools.exp_checkpoint), plus PER-(population,
#   depth) composition sub-checkpoints inside run() (same two-tier pattern as
#   exp_writerule_step_ladder_v1), since composition (nltk WordNet lookups) is the most interruption-
#   prone phase
# - discriminator survives scale: this cell RUNS the FULL grid; --grid reduced (smoke) runs the
#   IDENTICAL code path at a smaller depth/population set (POP_16_SMOKE), not a synthetic stand-in
# - calibration_check: default_ok_for_this_regime (reuses OLD's leak-safe pool + INFO's landed cache
#   unmodified; the only new calibration is the nested-population construction and the cross-
#   population restriction table, both self-tested on hand-built fixtures, not merely asserted)
# - progress_logging: print_flush_true (every phase prints a flushed line; this cell is long enough
#   under --grid full that a silent multi-minute gap would look like a hang without this)
# - sweep_alignment / discriminating_fraction / composition_edges / positive_control_arms / CRLB
#   gates: N/A -- same family as OLD and exp_pipeline_stage_oracle_ladder_v1 (diagnostic/information-
#   audit cell over a fixed store; no primitive composition, no capacity-bound sweep). Declared, not
#   omitted.
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
from hdlab.reading_grounding_loop import content_lemmas                  # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics   # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "organ_f_deep_reading_partialcue_ladder_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/organ_f_deep_reading_partialcue_ladder_2026-08-17.md"
SCRATCH_DIR = os.path.join(REPO, "scratch", ANCHOR_NAME)

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = LADDER.CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
MONOTONE_TOL_SIGMA = 1.5
ADDRESS_EXACT_MIN = 0.95
MIN_ITEMS_HARD = 8            # below this, a population is not scored at all
MIN_ITEMS_SOFT = 30           # below this, scored but flagged UNDERPOWERED, never "saturated"

if SMOKE:
    DEPTHS_UNION: Tuple[int, ...] = (1, 2, 4, 8, 16, 32)
    POP_SPECS = [{"name": "POP_16_SMOKE", "cap_min": 16, "cap_max": None,
                  "depths": (1, 2, 4, 8, 16, 32), "is_band": False}]
    BAND_SPEC = None
    CONTROL_POP = "POP_16_SMOKE"
    CONTROL_DEPTHS: Tuple[int, ...] = (16, 32)
    PER_ANCHOR_CAP = 32
    TOKEN_MATCH_SEARCH_CAP = 128
    N_PROBE_COMPOSITION_BASE = 40
    N_PROBE_COMPOSITION_DEEP = 12
else:
    DEPTHS_UNION = (1, 2, 4, 8, 16, 32, 72, 128, 256, 512, 768)
    POP_SPECS = [
        {"name": "POP_72", "cap_min": 72, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72), "is_band": False},
        {"name": "POP_128", "cap_min": 128, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128), "is_band": False},
        {"name": "POP_256", "cap_min": 256, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128, 256), "is_band": False},
        {"name": "POP_512", "cap_min": 512, "cap_max": None,
         "depths": (1, 2, 4, 8, 16, 32, 72, 128, 256, 512), "is_band": False},
        {"name": "POP_768", "cap_min": 768, "cap_max": None,
         "depths": DEPTHS_UNION, "is_band": False},
    ]
    BAND_SPEC = {"name": "BAND_LOW_FREQ_72_256", "cap_min": 72, "cap_max": 256,
                 "depths": (1, 2, 4, 8, 16, 32, 72), "is_band": True}
    CONTROL_POP = "POP_512"
    CONTROL_DEPTHS = (72, 512)
    PER_ANCHOR_CAP = 768
    TOKEN_MATCH_SEARCH_CAP = 2048
    N_PROBE_COMPOSITION_BASE = 500     # on POP_72 (n=694) -- comparable scale to WR's own N=700
    N_PROBE_COMPOSITION_DEEP = 43      # on POP_512 (n=43) -- every item probed

BASELINE_DEPTH = 72
NEVER_IMPORTED_COMPOSITION_BASELINES = {
    "no_relation_fraction_R2_single_occ": 0.8400,  # WR's own FILTERED_SINGLE_OCC, cited not imported
    "no_relation_fraction_R3_full_accum": 0.7971,  # WR's own FILTERED_FULL_ACCUM, cited not imported
    "winner_cooccur_R2": 0.660, "winner_cooccur_R3": 0.944,   # WR sec 5, cited not imported into calc
}


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    print("[selftest] reusing OLD's own self_test() wholesale (leak-safety fixture, depth-snapshot "
          "cumulative-sum real-code-path, saturation, scatter_rows, monotonicity checker, random-"
          "occurrence self-exclusion; chains INFO/FB/LADDER self-tests inside it)", flush=True)
    ev["OLD_selftest_keys"] = sorted(OLD.self_test().keys())

    print("[selftest] reusing WR's composition instruments' own self-test fixtures directly here "
          "(known WordNet relation classes, known Jaccard co-occurrence)", flush=True)
    qw_ = ["dog", "dog", "dog"]
    ww_ = ["canine", "carburetor", "dog"]
    ig_ = np.array([False, False, True])
    idxp = np.array([0, 1, 2])
    comp = WR.wordnet_relation_composition(qw_, ww_, ig_, idxp)
    assert comp["n_probed"] == 3 and comp["counts"].get("IN_THE_GENEROUS_GOLD", 0) == 1, comp
    ev["wordnet_relation_composition_reused_known_answer"] = comp["counts"]
    where_ = {"a": {0, 1}, "b": {0, 1}, "c": {5}, "d": set()}
    comp2 = WR.syntagmatic_jaccard_composition(["a", "a"], ["b", "c"], ["b", None], where_,
                                               np.array([0, 1]))
    assert comp2["TOP1_WINNER"]["n"] == 2 and abs(comp2["TOP1_WINNER"]["mean"] - 0.5) < 1e-9, comp2
    ev["syntagmatic_jaccard_reused_known_answer"] = comp2["TOP1_WINNER"]

    # ---- NESTED-POPULATION construction: a deeper capacity threshold's item set is a TRUE SUBSET
    # of every shallower one's, on a hand-built toy capacity array -------------------------------
    toy_item_cap = np.array([5, 72, 128, 256, 512, 768, 1000, 40, 90])
    masks = {}
    for cmin in (72, 128, 256, 512, 768):
        masks[cmin] = toy_item_cap >= cmin
    for a, b in [(128, 72), (256, 128), (512, 256), (768, 512)]:
        idx_a = set(np.flatnonzero(masks[a]).tolist())
        idx_b = set(np.flatnonzero(masks[b]).tolist())
        assert idx_a.issubset(idx_b), "deeper population is NOT a subset of the shallower one: " \
                                      f"cap>={a} not subset of cap>={b}: {idx_a} vs {idx_b}"
    ev["nested_population_subset_property"] = {"PASS": True, "toy_capacities": toy_item_cap.tolist()}

    # ---- global-score-once-slice-by-mask gives the IDENTICAL number as scoring the subset directly,
    # on a hand-built toy store: proves the "compute once, slice per population" refactor is not
    # silently changing which items are compared against which competitors ---------------------------
    rng = np.random.default_rng(3)
    n_anc_t, n_it_t = 12, 9
    mat_t = rng.standard_normal((n_anc_t, 6)).astype(np.float32)
    q_t = rng.standard_normal((n_it_t, 6)).astype(np.float32)
    qidx_t = rng.integers(0, n_anc_t, size=n_it_t)
    S_full = FB.l2n(mat_t) @ FB.l2n(q_t).T          # [n_anc_t, n_it_t] -- scored against ALL anchors
    pop_mask = np.array([True, False, True, True, False, True, False, True, True])
    E_t = np.ones((n_anc_t, n_it_t), dtype=bool)
    GOLD_t = np.zeros((n_anc_t, n_it_t), dtype=bool)
    GOLD_t[qidx_t, np.arange(n_it_t)] = True
    h_full = FB.hit_at_1_both_tie_conventions(S_full, E_t, GOLD_t)
    acc_sliced = float(h_full["hit_exp"][pop_mask].mean())
    # rescoring the SAME items directly (as a population-restricted run would) must match exactly
    sub_idx = np.flatnonzero(pop_mask)
    S_direct = FB.l2n(mat_t) @ FB.l2n(q_t[sub_idx]).T
    h_direct = FB.hit_at_1_both_tie_conventions(S_direct, E_t[:, sub_idx], GOLD_t[:, sub_idx])
    acc_direct = float(h_direct["hit_exp"].mean())
    assert abs(acc_sliced - acc_direct) < 1e-9, (acc_sliced, acc_direct)
    ev["global_score_slice_equals_direct_rescoring"] = {"PASS": True, "acc": round(acc_sliced, 6)}

    # ---- cross-population restriction margin: constructed case where a deep subset's baseline-
    # depth accuracy DIFFERS from the full population's, proving the UNPAIRED composition check can
    # actually detect a real difference (not a vacuous always-equal comparison) ---------------------
    hit_baseline = np.array([1, 1, 0, 0, 1, 1, 0, 1, 1, 0], dtype=np.float64)   # full pop, acc=0.6
    deep_mask = np.array([True, True, False, False, False, False, False, False, False, False])
    acc_full = float(hit_baseline.mean())
    acc_restricted = float(hit_baseline[deep_mask].mean())
    assert abs(acc_full - 0.6) < 1e-9 and abs(acc_restricted - 1.0) < 1e-9, (acc_full, acc_restricted)
    ev["restriction_check_detects_a_real_difference"] = {"PASS": True, "acc_full": acc_full,
                                                          "acc_restricted": acc_restricted}

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

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "RULER_MODE_GATE": LADDER.CTS.ruler_mode_gate(),
        "PRIMARY_CUE": "REAL_PARTIAL_CUE (deployed Qcue_context, oracle reported beside it, never "
                       "instead of it)",
    }

    # ---- corpus, capped buckets (cached), uncapped buckets (OLD's cache, reused unmodified) --------
    sents, buckets_capped, counts_capped, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    buckets_uncapped = OLD.load_buckets_uncapped(sents)
    profile_pool = OLD.build_profile_pool(anchors, buckets_capped, buckets_uncapped)
    capacity = OLD.build_capacity(anchors, profile_pool)
    rep["CAPACITY_DISTRIBUTION"] = {
        "percentiles": {str(p): int(np.percentile(capacity, p)) for p in (50, 75, 90, 95, 99, 100)},
        "max_capacity_anchor": anchors[int(np.argmax(capacity))], "max_capacity": int(capacity.max()),
        "n_anchors_by_threshold": {str(d): int((capacity >= d).sum())
                                   for d in (72, 128, 256, 512, 768, 1024, 1536, 2048)},
        "note": "measured directly off the leak-safe pool; 1024/1536/2048 item-pop counts reported "
                "below in PER_POPULATION-adjacent CAPACITY_ITEM_COUNTS to justify stopping at 768"}
    item_capacity = capacity[qidx_T]
    rep["CAPACITY_ITEM_COUNTS"] = {str(d): int((item_capacity >= d).sum())
                                   for d in (72, 128, 256, 512, 768, 1024, 1536, 2048)}
    print("[capacity] " + json.dumps(rep["CAPACITY_ITEM_COUNTS"]), flush=True)

    # ---- real-cue (Qcue_context), reused READ ONLY from exp_cue_information_audit_v1's checkpoint --
    shim = INFO._ShimSpace(C["anchors"], C["pos"], mat)
    all_items_meta, _item_diag = INFO.C3.build_items(shim, buckets_capped, counts_capped, INFO.C3.MAX_ITEMS)
    assert len(all_items_meta) == len(C["L_words"]), "rebuilt item metadata misaligned with cache"
    item_id_of_idx = [it["item_id"] for it in all_items_meta]
    item_ids_T = [item_id_of_idx[int(i)] for i in T]
    info_out_dir = os.path.join(REPO, "data", "exp_cue_information_audit_v1")
    print("[real_cue] reusing exp_cue_information_audit_v1's landed checkpoint (READ ONLY)", flush=True)
    _P_full_unused, Q_ctx_full, reuse_diag = LADDER.load_full_accum_from_checkpoint(
        info_out_dir, anchors, item_ids_T)
    rep["real_cue_checkpoint_reuse"] = reuse_diag
    del _P_full_unused

    # ---- depth snapshots, ONE pass over the union of every depth this cell tests -------------------
    P_by_depth, all_occ, snap_diag = OLD.build_depth_snapshots(
        anchors, profile_pool, sents, DEPTHS_UNION, PER_ANCHOR_CAP)
    rep["DEPTH_SNAPSHOT_BUILD"] = snap_diag

    # ---- controls (token-matched, random-occurrence) built on CONTROL_POP's own anchors -----------
    ctrl_spec = next((s for s in POP_SPECS if s["name"] == CONTROL_POP), None)
    if ctrl_spec is None:
        ctrl_spec = POP_SPECS[-1]
    ctrl_mask_items = (item_capacity >= ctrl_spec["cap_min"]) & (
        item_capacity < ctrl_spec["cap_max"] if ctrl_spec["cap_max"] is not None else True)
    ctrl_anchor_idx = sorted(set(int(qidx_T[i]) for i in np.flatnonzero(ctrl_mask_items)))
    ctrl_anchors = [anchors[i] for i in ctrl_anchor_idx]
    print(f"[controls] population={CONTROL_POP} n_anchors={len(ctrl_anchors)} "
         f"n_items={int(ctrl_mask_items.sum())} depths={CONTROL_DEPTHS}", flush=True)
    token_matched: Dict[int, Dict[str, Counter]] = {}
    token_matched_diag: Dict[int, Dict] = {}
    random_occ: Dict[int, Dict[str, Counter]] = {}
    for D in CONTROL_DEPTHS:
        target_tokens = {a: int(sum(P_by_depth[D][a].values())) for a in ctrl_anchors}
        tm, tm_diag = OLD.build_token_matched(ctrl_anchors, profile_pool, sents, target_tokens,
                                              TOKEN_MATCH_SEARCH_CAP)
        token_matched[D] = tm
        token_matched_diag[D] = tm_diag
        random_occ[D] = OLD.build_random_occurrence(ctrl_anchors, D, all_occ,
                                                     {a: i for i, a in enumerate(anchors)},
                                                     MASTER_SEED + 6000 + D)
    rep["CONTROLS_BUILD"] = {"token_matched": token_matched_diag, "control_population": CONTROL_POP,
                             "control_depths": list(CONTROL_DEPTHS)}

    # ---- vocab, shared across every arm ---------------------------------------------------------
    vocab_groups = [P_by_depth[d] for d in DEPTHS_UNION] + [Q_ctx_full] + \
        [token_matched[D] for D in CONTROL_DEPTHS] + [random_occ[D] for D in CONTROL_DEPTHS]
    vocab = INFO.build_vocab(vocab_groups)
    rep["vocab_n_distinct_content_words"] = len(vocab)
    print(f"[vocab] {len(vocab)} distinct content words t={time.time() - t0:.0f}s", flush=True)

    Qm_ctx = INFO.l2n_sparse(INFO.to_sparse(Q_ctx_full, item_ids_T, vocab))   # [n_items_T, V]

    # =============================== GLOBAL SCORE, ONCE PER DEPTH, SLICED BY POPULATION MASK LATER ==
    # See self_test()'s "global_score_slice_equals_direct_rescoring" -- this is provably identical to
    # scoring each population's own item subset directly, and lets a shallow-vs-deep comparison at
    # the SAME depth be a genuine paired margin on the SAME underlying hit array.
    hits_exp: Dict[str, np.ndarray] = {}
    hits_opt: Dict[str, np.ndarray] = {}
    hits_cons: Dict[str, np.ndarray] = {}
    noise_of: Dict[str, Dict] = {}
    rank_of: Dict[str, Dict] = {}
    addressing_of: Dict[str, float] = {}
    winner_idx_of: Dict[str, np.ndarray] = {}   # for composition: argmax anchor per item

    def add_arm(name: str, S: np.ndarray, addressing_target: Optional[np.ndarray] = None,
               keep_winner: bool = False) -> None:
        h = FB.hit_at_1_both_tie_conventions(S, E_T, GOLD_T)
        hits_exp[name] = h["hit_exp"]; hits_opt[name] = h["hit_opt"]; hits_cons[name] = h["hit_cons"]
        noise_of[name] = LADDER.dprime_summary(LADDER.dprime_stats(S, E_T, GOLD_T))
        rs, _ro, _rc = LADDER.rank_summary(S, E_T, GOLD_T)
        rank_of[name] = rs
        if addressing_target is not None:
            Sm = np.where(mat_ok[:, None], S, -np.inf)
            addr = np.argmax(Sm, axis=0)
            ok = addressing_target >= 0
            addressing_of[name] = round(float(np.mean(addr[ok] == addressing_target[ok])), 6)
        if keep_winner:
            Sm2 = np.where(E_T, S, -np.inf)
            winner_idx_of[name] = np.argmax(Sm2, axis=0)

    for D in DEPTHS_UNION:
        Pm_D = INFO.l2n_sparse(INFO.to_sparse(P_by_depth[D], anchors, vocab))
        S_oracle = np.asarray((Pm_D @ Pm_D[qidx_T].T).todense(), dtype=np.float32)
        add_arm(f"D{D}_ORACLE", S_oracle, addressing_target=qidx_T, keep_winner=True)
        del S_oracle
        S_real = np.asarray((Pm_D @ Qm_ctx.T).todense(), dtype=np.float32)
        add_arm(f"D{D}_REAL", S_real, keep_winner=True)
        del S_real
        print(f"[score] D={D} ORACLE_hit={hits_exp[f'D{D}_ORACLE'].mean():.4f} "
             f"REAL_hit={hits_exp[f'D{D}_REAL'].mean():.4f} t={time.time() - t0:.0f}s", flush=True)
        del Pm_D

    # ---- floors, computed ONCE over the full T, sliced per population like every depth arm --------
    S_orth = (FB.l2n(aux["t_mat"]) @ FB.l2n(Tq).T).astype(np.float32)
    S_freq = FB.as_constant_matrix(FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items_T)
    S_scr = (FB.l2n(FB.scramble_null(mat, MASTER_SEED + 191)) @ FB.l2n(C["Q_part"][T]).T).astype(np.float32)
    S_const = FB.as_constant_matrix(FB.constant_prototype_floor(mat, mat_ok), n_items_T)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items_T)]),
        n_items_T)
    for fname, S in (("F_ORTHOGRAPHIC", S_orth), ("F_FREQUENCY", S_freq), ("F_SCRAMBLE", S_scr),
                    ("F_CONSTANT_PROTOTYPE", S_const),
                    ("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S)):
        add_arm(fname, S)
    del S_orth, S_freq, S_scr, S_const, oracle_S

    # ---- token-matched / random-occurrence control arms, on CONTROL_POP's anchors -----------------
    keep_mask_ctrl = np.ones(n_anchors, dtype=np.float32)
    for i in ctrl_anchor_idx:
        keep_mask_ctrl[i] = 0.0
    for D in CONTROL_DEPTHS:
        Pm_D = INFO.l2n_sparse(INFO.to_sparse(P_by_depth[D], anchors, vocab))
        base = Pm_D.multiply(keep_mask_ctrl[:, None]).tocsr()
        tm_sub = INFO.to_sparse(token_matched[D], ctrl_anchors, vocab)
        ro_sub = INFO.to_sparse(random_occ[D], ctrl_anchors, vocab)
        Pm_tm = INFO.l2n_sparse((base + OLD.scatter_rows(tm_sub, ctrl_anchor_idx, n_anchors)).tocsr())
        Pm_ro = INFO.l2n_sparse((base + OLD.scatter_rows(ro_sub, ctrl_anchor_idx, n_anchors)).tocsr())
        S_tm = np.asarray((Pm_tm @ Pm_tm[qidx_T].T).todense(), dtype=np.float32)
        add_arm(f"CTRL_TOKEN_MATCHED_D{D}", S_tm, addressing_target=qidx_T)
        S_ro = np.asarray((Pm_ro @ Pm_ro[qidx_T].T).todense(), dtype=np.float32)
        add_arm(f"CTRL_RANDOM_OCC_D{D}", S_ro, addressing_target=qidx_T)
        del Pm_D, base, Pm_tm, Pm_ro, S_tm, S_ro

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: _digest(v) for k, v in hits_exp.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL hit vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_distinct"] = len(set(digests.values()))
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER_n_total"] = len(digests)

    # =============================== PER-POPULATION PROCESSING (nested) =============================
    per_population: Dict[str, Dict] = {}
    step_table: List[Dict] = []
    monotonicity: Dict[str, Dict] = {}
    sanity: Dict[str, Dict] = {}
    pop_masks: Dict[str, np.ndarray] = {}
    all_specs = list(POP_SPECS) + ([BAND_SPEC] if BAND_SPEC else [])

    for spec in all_specs:
        name = spec["name"]
        cap_min, cap_max, depths = spec["cap_min"], spec["cap_max"], spec["depths"]
        mask = (item_capacity >= cap_min) & (item_capacity < cap_max if cap_max is not None else True)
        pop_masks[name] = mask
        n_items_pop = int(mask.sum())
        n_anchors_pop = len(set(qidx_T[mask].tolist()))
        if n_items_pop < MIN_ITEMS_HARD:
            per_population[name] = {"SKIPPED_TOO_SMALL": True, "n_items": n_items_pop,
                                    "min_items_hard": MIN_ITEMS_HARD}
            print(f"[{name}] SKIPPED -- n_items={n_items_pop} < MIN_ITEMS_HARD={MIN_ITEMS_HARD}",
                 flush=True)
            continue
        underpowered = n_items_pop < MIN_ITEMS_SOFT

        # ---- RANDOM_NULL: real cue deranged within this population, deepest-depth store -----------
        deepest = max(depths)
        idx_pop = np.flatnonzero(mask)
        rng_n = np.random.default_rng(MASTER_SEED + 4141 + cap_min)
        perm_local = np.arange(idx_pop.size)
        for _ in range(64):
            perm_local = rng_n.permutation(idx_pop.size)
            if idx_pop.size < 2 or np.all(perm_local != np.arange(idx_pop.size)):
                break
        Pm_deep = INFO.l2n_sparse(INFO.to_sparse(P_by_depth[deepest], anchors, vocab))
        Q_pop = Qm_ctx[idx_pop]
        S_null_local = np.asarray((Pm_deep @ Q_pop[perm_local].T).todense(), dtype=np.float32)
        h_null = FB.hit_at_1_both_tie_conventions(S_null_local, E_T[:, idx_pop], GOLD_T[:, idx_pop])
        null_name = f"{name}_RANDOM_NULL"
        hits_exp[null_name] = np.full(n_items_T, np.nan)
        hits_exp[null_name][idx_pop] = h_null["hit_exp"]
        Sm_null_full = np.where(mat_ok[:, None], S_null_local, -np.inf)
        addr_null_local = np.argmax(Sm_null_full, axis=0)
        addr_null = float(np.mean(addr_null_local == qidx_T[idx_pop]))
        del Pm_deep, S_null_local, Sm_null_full

        arm_names = [f"D{d}_ORACLE" for d in depths] + [f"D{d}_REAL" for d in depths] + \
            ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE",
             "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"]
        pop_hits = {a: hits_exp[a] for a in arm_names}
        pb = FB.paired_bootstrap_ci(pop_hits, mask, N_BOOT, MASTER_SEED + 101 + cap_min)
        acc, boot = pb["acc"], pb["boot"]
        ci_hw = {k: round((float(np.percentile(v, 97.5)) - float(np.percentile(v, 2.5))) / 2.0, 5)
                for k, v in boot.items()}
        analytic_null_hw = round(float(1.645 / np.sqrt(max(pb["n_common"] - 1, 1))), 5)

        floor_names = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
        binding = max(floor_names, key=lambda f: acc[f])

        per_rung = {}
        for a in arm_names:
            per_rung[a] = {
                "SIGNAL_hit_at_1_tie_corrected": round(acc[a], 4),
                "ci95": [round(float(np.percentile(boot[a], 2.5)), 4),
                        round(float(np.percentile(boot[a], 97.5)), 4)],
                "ci_halfwidth": ci_hw[a], "analytic_null_halfwidth": analytic_null_hw,
                "NOISE_dprime": noise_of[a], "RANK": rank_of[a],
                "addressing_accuracy": addressing_of.get(a),
                "margin_vs_binding_floor": FB.margin(boot, a, binding) if a != binding else None}

        for cue_kind in ("ORACLE", "REAL"):
            chain = [f"D{d}_{cue_kind}" for d in depths]
            for i in range(1, len(chain)):
                m = FB.margin(boot, chain[i], chain[i - 1])
                step_table.append({"population": name, "cue_kind": cue_kind,
                                  "from_depth": depths[i - 1], "to_depth": depths[i],
                                  "gain_point": m["point"], "gain_ci95": m["ci95"],
                                  "gain_ci_halfwidth": round((m["ci95"][1] - m["ci95"][0]) / 2.0, 4),
                                  "band": m["band"]})
            # ---- SPAN margin: deepest vs the BASELINE_DEPTH (72), PAIRED on this population's own
            # items -- the valid deep-vs-shallow comparison the brief requires, not adjacent-step only
            if BASELINE_DEPTH in depths and deepest != BASELINE_DEPTH:
                span = FB.margin(boot, f"D{deepest}_{cue_kind}", f"D{BASELINE_DEPTH}_{cue_kind}")
                step_table.append({"population": name, "cue_kind": cue_kind,
                                  "from_depth": BASELINE_DEPTH, "to_depth": deepest,
                                  "gain_point": span["point"], "gain_ci95": span["ci95"],
                                  "gain_ci_halfwidth": round((span["ci95"][1] - span["ci95"][0]) / 2.0, 4),
                                  "band": span["band"], "SPAN_BASELINE_TO_DEEPEST": True})
            chain_vals = [acc[n_] for n_ in chain]
            chain_hw = [ci_hw[n_] / 2.0 for n_ in chain]
            mono = OLD.check_monotone_nondecreasing(chain_vals, chain_hw, MONOTONE_TOL_SIGMA)
            monotonicity[f"{name}_{cue_kind}"] = dict(mono, chain=chain,
                                                      values=[round(v, 4) for v in chain_vals])

        addr_known = addressing_of.get(f"D{deepest}_ORACLE")
        addr_known = 0.0 if addr_known is None else addr_known
        chance = 1.0 / max(n_anchors_pop, 1)
        sanity[name] = {
            "K1_known_answer": {"addressing_at_deepest": addr_known, "gate": ADDRESS_EXACT_MIN,
                               "PASSED": bool(addr_known >= ADDRESS_EXACT_MIN)},
            "N1_random_null": {"addressing_RANDOM_NULL": round(addr_null, 6),
                              "hit_at_1_RANDOM_NULL_mean": round(float(h_null["hit_exp"].mean()), 4),
                              "chance_addressing_approx": round(chance, 6),
                              "PASSED": bool(addr_null < max(0.05, 20.0 * chance))}}
        publishable = sanity[name]["K1_known_answer"]["PASSED"] and sanity[name]["N1_random_null"]["PASSED"]
        if not publishable:
            print(f"[{name}] SANITY FAILED -- this population's numbers are NOT PUBLISHABLE: "
                 f"{sanity[name]!r}", flush=True)

        per_population[name] = {
            "n_items": n_items_pop, "n_anchors": n_anchors_pop, "depths": list(depths),
            "cap_min": cap_min, "cap_max": cap_max, "is_band": spec.get("is_band", False),
            "UNDERPOWERED": underpowered, "PUBLISHABLE": publishable,
            "PER_RUNG": per_rung, "BINDING_FLOOR": binding, "BINDING_FLOOR_VALUE": round(acc[binding], 4),
            "POWER": {"n_common_scored": pb["n_common"], "analytic_null_halfwidth": analytic_null_hw},
        }
        print(f"[{name}] n_items={n_items_pop} n_anchors={n_anchors_pop} UNDERPOWERED={underpowered} "
             f"binding_floor={binding}={acc[binding]:.4f} "
             f"deepest_REAL={acc[f'D{deepest}_REAL']:.4f} deepest_ORACLE={acc[f'D{deepest}_ORACLE']:.4f}",
             flush=True)

    rep["PER_POPULATION"] = per_population
    rep["STEP_TABLE"] = step_table
    rep["MONOTONICITY"] = monotonicity
    rep["SANITY"] = sanity

    # =============================== CROSS-POPULATION RESTRICTION TABLE =============================
    # For each deep population, the UNPAIRED composition check: POP_72's FULL D=72 accuracy (n=694)
    # beside the SAME D=72 arm restricted to the deep population's own (smaller, nested) item subset.
    # Explicitly labelled UNPAIRED -- different item counts, not a formal paired test. The PAIRED
    # comparison (SPAN_BASELINE_TO_DEEPEST above, same items, different depth) is the valid one.
    restriction_table = []
    if "POP_72" in per_population and not per_population["POP_72"].get("SKIPPED_TOO_SMALL"):
        base_acc = per_population["POP_72"]["PER_RUNG"][f"D{BASELINE_DEPTH}_REAL"]["SIGNAL_hit_at_1_tie_corrected"]
        base_ci = per_population["POP_72"]["PER_RUNG"][f"D{BASELINE_DEPTH}_REAL"]["ci95"]
        for spec in POP_SPECS:
            name = spec["name"]
            if name == "POP_72" or name not in per_population or per_population[name].get("SKIPPED_TOO_SMALL"):
                continue
            pr = per_population[name]["PER_RUNG"]
            restricted = pr.get(f"D{BASELINE_DEPTH}_REAL")
            deepest_d = max(per_population[name]["depths"])
            deep_entry = pr.get(f"D{deepest_d}_REAL")
            restriction_table.append({
                "deep_population": name, "n_items_deep": per_population[name]["n_items"],
                "D72_on_FULL_POP_72_n694": {"acc": base_acc, "ci95": base_ci},
                "D72_RESTRICTED_to_deep_subset": {"acc": restricted["SIGNAL_hit_at_1_tie_corrected"],
                                                  "ci95": restricted["ci95"]} if restricted else None,
                "deepest_depth": deepest_d,
                "deepest_RESTRICTED_to_deep_subset": {"acc": deep_entry["SIGNAL_hit_at_1_tie_corrected"],
                                                       "ci95": deep_entry["ci95"]} if deep_entry else None,
                "NOTE": "the two D72 numbers are UNPAIRED (different item counts, though nested); the "
                        "PAIRED comparison is STEP_TABLE's SPAN_BASELINE_TO_DEEPEST row for this "
                        "population, same items throughout"})
    rep["CROSS_POPULATION_RESTRICTION_TABLE"] = restriction_table

    # =============================== FREQUENCY-STRATIFIED CHECK (BAND vs POP_256, matching depths) ==
    freq_compare = None
    if BAND_SPEC and BAND_SPEC["name"] in per_population and "POP_256" in per_population and \
            not per_population[BAND_SPEC["name"]].get("SKIPPED_TOO_SMALL"):
        band_depths = per_population[BAND_SPEC["name"]]["depths"]
        freq_compare = {
            "BAND_LOW_FREQ_values_REAL": [per_population[BAND_SPEC["name"]]["PER_RUNG"][f"D{d}_REAL"][
                "SIGNAL_hit_at_1_tie_corrected"] for d in band_depths],
            "POP_256_values_REAL_matching_depths": [per_population["POP_256"]["PER_RUNG"][f"D{d}_REAL"][
                "SIGNAL_hit_at_1_tie_corrected"] for d in band_depths],
            "depths_compared": list(band_depths),
            "band_n_items": per_population[BAND_SPEC["name"]]["n_items"],
            "pop256_n_items": per_population["POP_256"]["n_items"]}
    rep["FREQUENCY_STRATIFIED_COMPARISON"] = freq_compare

    # =============================== CONTROL MARGINS ================================================
    control_margins = []
    ctrl_arm_names = [f"D{D}_ORACLE" for D in CONTROL_DEPTHS] + \
        [f"CTRL_TOKEN_MATCHED_D{D}" for D in CONTROL_DEPTHS] + \
        [f"CTRL_RANDOM_OCC_D{D}" for D in CONTROL_DEPTHS]
    ctrl_hits = {a: hits_exp[a] for a in ctrl_arm_names}
    pb_ctrl = FB.paired_bootstrap_ci(ctrl_hits, ctrl_mask_items, N_BOOT, MASTER_SEED + 999)
    for D in CONTROL_DEPTHS:
        nat = f"D{D}_ORACLE"
        for kind in ("TOKEN_MATCHED", "RANDOM_OCC"):
            ctrl = f"CTRL_{kind}_D{D}"
            m = FB.margin(pb_ctrl["boot"], nat, ctrl)
            control_margins.append({"depth": D, "control": kind, "natural_arm": nat,
                                   "control_arm": ctrl, "natural_minus_control_point": m["point"],
                                   "ci95": m["ci95"], "band": m["band"]})
    rep["CONTROL_MARGINS"] = control_margins

    # =============================== WINNER COMPOSITION AT EVERY DEPTH (REAL cue) ====================
    print("[composition] building sentence co-occurrence index (content_lemmas over %d sentences, "
         "REUSED corpus, store never rebuilt)" % len(sents), flush=True)
    where: Dict[str, set] = {}
    for si, s in enumerate(sents):
        for w in content_lemmas(s):
            where.setdefault(w, set()).add(si)
    query_words = [C["L_words"][int(t)] for t in T]

    has_gold = (GOLD_T & E_T).any(axis=0)
    gtop = np.argmax(np.where(GOLD_T & E_T, 1.0, -np.inf), axis=0)
    gold_words_all: List[Optional[str]] = [anchors[int(gtop[i])] if has_gold[i] else None
                                           for i in range(n_items_T)]

    composition_by_population: Dict[str, Dict] = {}
    for pop_name, n_probe_target in (("POP_72", N_PROBE_COMPOSITION_BASE),
                                     ("POP_512", N_PROBE_COMPOSITION_DEEP),
                                     ("POP_768", N_PROBE_COMPOSITION_DEEP)):
        if pop_name not in per_population or per_population[pop_name].get("SKIPPED_TOO_SMALL"):
            continue
        mask = pop_masks[pop_name]
        idx_pool = np.flatnonzero(mask)
        rng_probe = np.random.default_rng(MASTER_SEED + 909 + hash(pop_name) % 1000)
        n_probe = min(n_probe_target, idx_pool.size)
        idx_probe = np.sort(rng_probe.choice(idx_pool, size=n_probe, replace=False))
        depths_here = per_population[pop_name]["depths"]
        per_depth: Dict[str, Dict] = {}
        for D in depths_here:
            arm = f"D{D}_REAL"
            ck_key = unit_key("COMPOSITION", CODE_VERSION, grid, pop_name, str(D))
            prior = load_units(out_dir).get(ck_key)
            if prior is not None:
                per_depth[str(D)] = prior
                print(f"[composition] {pop_name} D={D} RESUMED FROM CHECKPOINT", flush=True)
                continue
            top1 = winner_idx_of[arm]
            winner_words = [anchors[int(w)] for w in top1]
            in_gold = np.array([bool(GOLD_T[int(top1[i]), i]) for i in range(n_items_T)])
            wn_comp = WR.wordnet_relation_composition(query_words, winner_words, in_gold, idx_probe)
            jac_comp = WR.syntagmatic_jaccard_composition(query_words, winner_words, gold_words_all,
                                                           where, idx_probe)
            rec = {"depth": D, "n_probe": int(idx_probe.size), "wordnet": wn_comp,
                  "syntagmatic": jac_comp}
            per_depth[str(D)] = rec
            record_unit(out_dir, ck_key, rec)
            print(f"[composition] {pop_name} D={D} no_relation={wn_comp['fraction_no_close_relation']} "
                 f"winner_cooc={jac_comp['TOP1_WINNER']['mean']} "
                 f"gold_cooc={jac_comp['BEST_GOLD_SYNONYM']['mean']}", flush=True)
        composition_by_population[pop_name] = {"n_probe_target": n_probe_target,
                                               "n_probe_actual": int(idx_probe.size),
                                               "PER_DEPTH": per_depth}
    rep["WINNER_COMPOSITION"] = composition_by_population

    # ---- composition trend flag: does no-relation / co-occurrence move from shallowest to deepest
    # measured depth on the population that reaches furthest (paired bootstrap on the SAME idx_probe,
    # reusing the no_relation_bool arrays each rung already returned) --------------------------------
    composition_trend = {}
    for pop_name in ("POP_72", "POP_512", "POP_768"):
        cp = composition_by_population.get(pop_name)
        if not cp or len(cp["PER_DEPTH"]) < 2:
            continue
        depths_sorted = sorted((int(d) for d in cp["PER_DEPTH"].keys()))
        shallow, deep = depths_sorted[0], depths_sorted[-1]
        wn_shallow = np.array(cp["PER_DEPTH"][str(shallow)]["wordnet"]["no_relation_bool"], dtype=bool)
        wn_deep = np.array(cp["PER_DEPTH"][str(deep)]["wordnet"]["no_relation_bool"], dtype=bool)
        n_pr = wn_shallow.size
        rng_cb = np.random.default_rng(MASTER_SEED + 5151 + hash(pop_name) % 1000)
        boot_idx = rng_cb.integers(0, n_pr, size=(2000, n_pr))
        d_no_rel = wn_deep.astype(np.float64)[boot_idx].mean(axis=1) - \
            wn_shallow.astype(np.float64)[boot_idx].mean(axis=1)
        lo, hi = float(np.percentile(d_no_rel, 2.5)), float(np.percentile(d_no_rel, 97.5))
        acc_shallow = per_population[pop_name]["PER_RUNG"][f"D{shallow}_REAL"]["SIGNAL_hit_at_1_tie_corrected"]
        acc_deep = per_population[pop_name]["PER_RUNG"][f"D{deep}_REAL"]["SIGNAL_hit_at_1_tie_corrected"]
        accuracy_rose = acc_deep > acc_shallow
        no_relation_worsened = lo > 0   # CI-separated increase in no-relation fraction = worse
        composition_trend[pop_name] = {
            "shallow_depth": shallow, "deep_depth": deep,
            "no_relation_delta_point": round(float(np.mean(d_no_rel)), 4),
            "no_relation_delta_ci95": [round(lo, 4), round(hi, 4)],
            "accuracy_rose": bool(accuracy_rose), "no_relation_worsened_CI_separated": bool(no_relation_worsened),
            "DEPTH_BUYS_RANKING_NOT_MEANING": bool(accuracy_rose and no_relation_worsened)}
    rep["COMPOSITION_TREND"] = composition_trend

    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = True
    rep["NEVER_IMPORTED"] = ["0.1382", "0.2070", "-0.1959", "0.1390", "0.0873"]
    rep["CITED_NOT_IMPORTED_BASELINES_FROM_WR"] = NEVER_IMPORTED_COMPOSITION_BASELINES
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

    # ---- mechanical verdict classification, keyed on the REAL cue (primary measure) ----------------
    def find_span(pop: str, cue: str) -> Optional[Dict]:
        for s in rep["STEP_TABLE"]:
            if s["population"] == pop and s["cue_kind"] == cue and s.get("SPAN_BASELINE_TO_DEEPEST"):
                return s
        return None

    prize_cleared_populations = []
    for pop_name, pop_rep in rep["PER_POPULATION"].items():
        if pop_rep.get("SKIPPED_TOO_SMALL") or not pop_rep.get("PUBLISHABLE", False):
            continue
        deepest_d = max(pop_rep["depths"])
        arm = f"D{deepest_d}_REAL"
        entry = pop_rep["PER_RUNG"].get(arm)
        if entry and entry.get("margin_vs_binding_floor") and \
                entry["margin_vs_binding_floor"]["band"] == "ABOVE":
            prize_cleared_populations.append({"population": pop_name, "depth": deepest_d,
                                             "margin": entry["margin_vs_binding_floor"]})

    climbing_populations = []
    underpowered_populations = []
    for pop_name in ("POP_128", "POP_256", "POP_512", "POP_768"):
        pop_rep = rep["PER_POPULATION"].get(pop_name, {})
        if pop_rep.get("SKIPPED_TOO_SMALL"):
            continue
        if pop_rep.get("UNDERPOWERED"):
            underpowered_populations.append(pop_name)
        span = find_span(pop_name, "REAL")
        if span and span["band"] == "ABOVE":
            climbing_populations.append(pop_name)

    ranking_not_meaning = [p for p, v in rep.get("COMPOSITION_TREND", {}).items()
                           if v.get("DEPTH_BUYS_RANKING_NOT_MEANING")]

    sanity_all_pass = all(
        v.get("K1_known_answer", {}).get("PASSED", False) and
        v.get("N1_random_null", {}).get("PASSED", False)
        for v in rep["SANITY"].values())

    if not sanity_all_pass:
        verdict = "ORGAN_F_DEEP__INSTRUMENT_STILL_LOOSE__K1_OR_N1_FAILED_SOMEWHERE"
    else:
        verdict = "ORGAN_F_DEEP__PRIZE_%s__CLIMBING_%s__UNDERPOWERED_%s__RANKING_NOT_MEANING_%s" % (
            "CLEARED" if prize_cleared_populations else "NOT_CLEARED",
            "_".join(climbing_populations) if climbing_populations else "NONE",
            "_".join(underpowered_populations) if underpowered_populations else "NONE",
            "_".join(ranking_not_meaning) if ranking_not_meaning else "NONE")

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "ORGAN F, deep nested depth ladder on the REAL PARTIAL CUE. Nested populations "
            "(POP_72/128/256/512/768) so every deep-vs-shallow comparison is paired on identical "
            "items; winner composition (WordNet relation + co-occurrence) measured at every depth; "
            "token-matched, random-occurrence and frequency-stratified controls. -> " + verdict),
        "config": {"DEPTHS_UNION": list(DEPTHS_UNION), "POP_SPECS": [
            {"name": s["name"], "cap_min": s["cap_min"], "cap_max": s["cap_max"],
             "depths": list(s["depths"])} for s in POP_SPECS],
                  "BAND_SPEC": BAND_SPEC, "CONTROL_POP": CONTROL_POP,
                  "CONTROL_DEPTHS": list(CONTROL_DEPTHS), "N_BOOT": N_BOOT, "MASTER_SEED": MASTER_SEED,
                  "MIN_ITEMS_HARD": MIN_ITEMS_HARD, "MIN_ITEMS_SOFT": MIN_ITEMS_SOFT},
        "selftest_evidence_keys": sorted(ev.keys()),
        "prize_cleared_populations": prize_cleared_populations,
        "report": rep,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    # write_metrics expects a Path (it calls .mkdir); out_dir is str for the
    # checkpoint helpers, which want a plain path string. Convert at the boundary.
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
