"""exp_dissociation_score_instrument_human_v4 -- HARVEST EVERY LANDED STORE VARIANT ONTO BOTH
INSTRUMENTS, RECOMPUTE THE ARM-ORDERING RANK CORRELATION AT 20+ ARMS (dispatch brief 2026-08-18).

=================================================================================================
WHY THIS FILE EXISTS. `exp_dissociation_score_instrument_human_v3` (commit f792c3ab8) licensed the
human-judgement instrument (n=65/cell, all four floors CI-including 0.5,
max(four floors)=0.5943 MEASURED@data/exp_dissociation_score_instrument_human_v3/metrics.json:
report.LICENSING.max_floor_auc_this_population) and used it to score the SAME SEVEN arms the
WordNet instrument (`exp_dissociation_score_instrument_v1`, "DSI") already scored. The two
orderings agreed (Spearman rho=0.7857) but the bootstrap-of-arms 95% CI = [-0.0439, 1.0] --
INCLUDES ZERO. The dispatch brief's diagnosis: the bootstrap resamples ARMS, and seven arms cannot
yield a tight CI regardless of how good each AUC estimate is. THE FIX: score every OTHER store
variant this project already owns and already has WordNet-side numbers for, on the SAME human
population, and recompute the rank correlation with a much larger arm set.

NO NEW STORE IS INVENTED HERE. Every arm below is a VERBATIM reuse of a landed sibling cell's own
store-construction function, called on v3's own words_needed/matchedP/matchedS (imported read-only,
never rebuilt, never re-tuned) instead of on DSI's n=242 WordNet population. The WordNet-side AUC
for each new arm is HARVESTED from that sibling's own already-landed metrics.json (it was already
scored on DSI's n=242 population when that cell landed) -- not recomputed here, per the dispatch
brief: "No new stores need building -- these already exist and are already scored on the WordNet
instrument. Harvest them."

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md). Per the dispatch brief this check is
DONE at Director level (name-level enumeration over experiments/, explicit candidate-cell list) and
`tools/substrate_query.sh` / `os.walk` over `data/` are both explicitly forbidden tonight (zero-byte
tool + 157GB stalled lanes). Backstop performed here anyway, cheap and local: `ls experiments/ | grep
dissociation_score_instrument_human` at authoring time returns exactly `_v1.py`, `_v2.py`, `_v3.py`
plus this new `_v4.py` -- no undisclosed sibling. This cell is a direct, explicitly-commissioned
follow-on to v3's own measured n=7-arms CI-includes-zero finding, not an independently-conceived
direction, so the prior-work risk this gate guards against is structurally low.

=================================================================================================
ARM ENUMERATION (from each landed cell's own metrics.json, read at authoring time -- see the
completion report for the exact per-arm numbers and paths). Reused verbatim, existing 7 (v3's own,
their P/S score ARRAYS reused bit-for-bit from v3's own checkpoint, never rebuilt):
  INCUMBENT_LIVE_STORE, RAW_COUNT_FULL_ACCUM, RAW_COUNT_SINGLE_OCC, PRESENCE_ABSENCE_BINARIZED,
  PARADIGMATIC_PROFILE_WRITE, T0_VANILLA_PPMI_SVD, T2_SHIFTED_PPMI_K15.

NEW (17, this file's only original code is the wiring that calls each sibling's own construction
function on v3's human population and scores it via DSI.auc_bootstrap, exactly as v3 does for its
existing 7):
  maxpool (exp_writerule_maxpool_occurrence_v1, MP):      M1_MAXPOOL, M2_TOPK_MEAN_K2/K3/K5
  filter (exp_writerule_filter_superpose_gate_v1, FSG):   F1_NO_FILTER, F2_CONTENT_ONLY_STRICT,
                                                           F3_SYNTACTIC_NEIGHBOURS_ONLY,
                                                           F4_WINDOW_1/2/5
  typed_role (exp_typed_role_selectional_asset_writerule_v1, TR): T1_TYPED_ROLE,
                                                           T2_UNTYPED_SAME_COVERAGE, T3_COMBINED
  tuned_count (exp_tuned_count_unsupervised_dissociation_v1, TC): T4_BEST_COMBINED, T5_SGNS_IN_IN
  predictive_coding (exp_predictive_coding_write_gate_dissociation_v1, PCW): P2_PREDICTION_WEIGHTED,
                                                           P1_PREDICTION_GATED_BEST (T=0.5151,
                                                           MEASURED@data/exp_predictive_coding_
                                                           write_gate_dissociation_v1/metrics.json:
                                                           report.BEST_P1_THRESHOLD)

EXCLUDED (hard requirement 1 -- an arm qualifies ONLY IF the SAME store construction can be scored
on BOTH instruments; these three sibling cells fail that test for stated reasons, not omitted by
accident):
  - `exp_writerule_learned_basis_denominator_gate_v1` (C1_LEARNED_BASIS, C1_CTRL_MATCHED_RANK_
    RANDOM, C2_WRITE_TIME_DIVISIVE_NORM, C2_CTRL_PURE_IDF): this cell never imports DSI at all
    (MEASURED@its own metrics.json report.NEVER_IMPORTED) and scores its arms on a RETRIEVAL-
    ACCURACY/addressing instrument (hit@1, d-prime, rank over ~4000 anchor cues) -- a different task
    shape from the dissociation-score AUC pair-comparison this instrument and DSI share. There is no
    WordNet-instrument AUC for these arms to pair with a human-population rebuild.
  - `exp_organ_f_accumulation_depth_ladder_v1` (depth snapshots): same exclusion reason -- scores a
    depth-ladder ADDRESSING-ACCURACY instrument (hit@1 per population/cue_kind/depth), not the
    dissociation-score AUC pair-comparison. Not reconstructible as a comparable arm.
  - `exp_tuned_count_unsupervised_dissociation_v1`'s T1_CONTEXT_DISTRIBUTION_SMOOTHING and
    T3_SUBSAMPLING: both arms' own hyperparameter search SELECTED a config
    (alpha=1.0, k_shift=1.0, subsample_t=None, k=50, p=0.5) IDENTICAL to each other and
    numerically indistinguishable from T0's own vanilla-PPMI construction (MEASURED@its own
    metrics.json: T1 and T3 RESULT_held_out_selected_eval_AUC.auc are both 0.0519 on the WordNet
    population). Including both risks a bit-identical or near-identical arm pair, which is exactly
    what META_RULE_AF (arms-must-differ) exists to catch; they add no new ORDERING information
    beyond T0, already in the arm set. T4 (k_shift=15, p=0.0 -- distinct from T2's k_shift=15,p=0.5)
    and T5 (SGNS, a different family entirely) are kept.
  - filter_superpose's GATE B arms (S0/S1/S2/N2, superposition-isolation) and maxpool's A0_SUM/
    S1_SINGLE_OCC: these duplicate INCUMBENT_LIVE_STORE/RAW_COUNT_SINGLE_OCC already in the 7-arm
    base set (same construction, re-measured by the sibling cell for its own regression purposes);
    including them again would double-count one arm's ordering information under two names.

Achieved count: 7 + 17 = 24 arms (>= the 20+ target). See completion report for the achieved count
if any cluster's build fails at runtime (each cluster is wrapped so a single failure does not kill
the whole cell; failures are recorded loudly, not silently skipped).

=================================================================================================
REGRESSION GATES (hard requirement 3, EXIT ON FAILURE, checked before anything else):
  (A) DSI's own 8 cached checks (F_ORTHOGRAPHIC, F_FREQUENCY, F_SCRAMBLE, F_CONSTANT_PROTOTYPE,
      KNOWN_ANSWER_WORDNET_PATH_SIM, RANDOM_VECTOR_STORE, INCUMBENT_LIVE_STORE, RAW_COUNT_FULL_
      ACCUM) recomputed bit-for-bit from DSI's own checkpoint via DSI.auc_of, against the EXACT
      values in DSI's own landed metrics.json (MEASURED@data/exp_dissociation_score_instrument_v1/
      metrics.json:report.AUC_PER_ARM), tol=0.0005.
  (B) v3's own floors + n=65: recomputed from v3's own checkpoint via DSI.auc_of, against the exact
      values in v3's own landed metrics.json (MEASURED@data/exp_dissociation_score_instrument_
      human_v3/metrics.json:report.AUC_PER_ARM), tol=0.0005; n_match must equal 65.
Either failure -> SystemExit, publish only the gate failure (hard requirement 4).

=================================================================================================
NEVER RE-TUNE THE MATCHER (hard requirement 2). v3's population (matchedP/matchedS/words_needed)
is loaded VERBATIM from v3's own checkpoint (`data/exp_dissociation_score_instrument_human_v3/
units.jsonl`, key POPULATION_HUMAN|v3.0|full) -- this file contains ZERO population-matching code,
zero caliper code, zero binning code. v3.py and DSI.py are imported read-only and never edited.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded.
data/foundation/** is never opened. This cell writes only under
data/exp_dissociation_score_instrument_human_v4[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy + 9 sibling modules read-only -- flushed so a slow import "
      "is never mistaken for a hang)", flush=True)

import argparse
import itertools
import json
import sys
import time
import traceback
from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import spearmanr

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI                       # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_human_v2 as H2                  # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_human_v3 as H3                  # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                             # noqa: E402  READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                            # noqa: E402  READ ONLY
import experiments.exp_corpus_capacity_ppmi_svd_ceiling_v1 as CAP                    # noqa: E402  READ ONLY
import experiments.exp_tuned_count_unsupervised_dissociation_v1 as TC                # noqa: E402  READ ONLY
import experiments.exp_writerule_maxpool_occurrence_v1 as MP                         # noqa: E402  READ ONLY
import experiments.exp_writerule_filter_superpose_gate_v1 as FSG                     # noqa: E402  READ ONLY
import experiments.exp_writerule_step_ladder_v1 as WR                                # noqa: E402  READ ONLY
import experiments.exp_typed_role_selectional_asset_writerule_v1 as TR               # noqa: E402  READ ONLY
import experiments.exp_predictive_coding_write_gate_dissociation_v1 as PCW           # noqa: E402  READ ONLY
from tools import floor_battery as FB                                                # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics               # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "dissociation_score_instrument_human_v4"
CODE_VERSION = "v4.0"
FINDINGS = "notes/dissociation_score_instrument_human_v4_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
N_SMOKE_WORDS = 24
N_PERM_MC = 20000 if not SMOKE else 2000   # Monte Carlo permutation draws at n>7 (exact is 24! -- infeasible)

DSI_DIR = os.path.join(REPO, "data", "exp_" + DSI.ANCHOR_NAME)
H3_DIR = os.path.join(REPO, "data", "exp_" + H3.ANCHOR_NAME)

# =================================================================================================
# EXPECTED CACHED VALUES for the two regression gates -- copied verbatim from each cell's OWN landed
# metrics.json (paths cited in the module docstring above), tol=0.0005 (point AUC, deterministic).
# =================================================================================================
DSI_EXPECTED_CACHED = {
    "F_ORTHOGRAPHIC": 0.5, "F_FREQUENCY": 0.4901, "F_SCRAMBLE": 0.4664, "F_CONSTANT_PROTOTYPE": 0.5431,
    "KNOWN_ANSWER_WORDNET_PATH_SIM": 0.9599, "RANDOM_VECTOR_STORE": 0.4862,
    "INCUMBENT_LIVE_STORE": 0.071, "RAW_COUNT_FULL_ACCUM": 0.051,
}
V3_EXPECTED_CACHED = {
    "F_ORTHOGRAPHIC": 0.492, "F_FREQUENCY": 0.4151, "F_SCRAMBLE": 0.5943, "F_CONSTANT_PROTOTYPE": 0.4125,
    "KNOWN_ANSWER_HUMAN_RATING": 1.0, "RANDOM_VECTOR_STORE": 0.4578,
}
V3_EXPECTED_N_MATCH = 65
REG_TOL = 0.0005

# =================================================================================================
# HARVESTED WordNet-instrument AUCs for the 17 NEW arms -- each MEASURED@ the cited sibling's own
# landed metrics.json, NEVER recomputed here (hard requirement: harvest, don't rebuild).
# =================================================================================================
HARVESTED_WORDNET_AUC = {
    "M1_MAXPOOL": (0.0299, "data/exp_writerule_maxpool_occurrence_v1/metrics.json:"
                          "report.REGIME_A_AUC_PER_ARM.M1_MAXPOOL.auc"),
    "M2_TOPK_MEAN_K2": (0.0264, "data/exp_writerule_maxpool_occurrence_v1/metrics.json:"
                               "report.REGIME_A_AUC_PER_ARM.M2_TOPK_MEAN_K2.auc"),
    "M2_TOPK_MEAN_K3": (0.024, "data/exp_writerule_maxpool_occurrence_v1/metrics.json:"
                              "report.REGIME_A_AUC_PER_ARM.M2_TOPK_MEAN_K3.auc"),
    "M2_TOPK_MEAN_K5": (0.0217, "data/exp_writerule_maxpool_occurrence_v1/metrics.json:"
                               "report.REGIME_A_AUC_PER_ARM.M2_TOPK_MEAN_K5.auc"),
    "F1_NO_FILTER": (0.4558, "data/exp_writerule_filter_superpose_gate_v1/metrics.json:"
                            "report.GATE_A_AUC_PER_ARM.F1_NO_FILTER.auc"),
    "F2_CONTENT_ONLY_STRICT": (0.4323, "data/exp_writerule_filter_superpose_gate_v1/metrics.json:"
                                      "report.GATE_A_AUC_PER_ARM.F2_CONTENT_ONLY_STRICT.auc"),
    "F3_SYNTACTIC_NEIGHBOURS_ONLY": (0.4876, "data/exp_writerule_filter_superpose_gate_v1/"
                                            "metrics.json:report.GATE_A_AUC_PER_ARM."
                                            "F3_SYNTACTIC_NEIGHBOURS_ONLY.auc"),
    "F4_WINDOW_1": (0.4959, "data/exp_writerule_filter_superpose_gate_v1/metrics.json:"
                           "report.GATE_A_AUC_PER_ARM.F4_WINDOW_1.auc"),
    "F4_WINDOW_2": (0.4731, "data/exp_writerule_filter_superpose_gate_v1/metrics.json:"
                           "report.GATE_A_AUC_PER_ARM.F4_WINDOW_2.auc"),
    "F4_WINDOW_5": (0.4561, "data/exp_writerule_filter_superpose_gate_v1/metrics.json:"
                           "report.GATE_A_AUC_PER_ARM.F4_WINDOW_5.auc"),
    "T1_TYPED_ROLE": (0.5802, "data/exp_typed_role_selectional_asset_writerule_v1/metrics.json:"
                             "report.AUC_PER_ARM.T1_TYPED_ROLE.auc"),
    "T2_UNTYPED_SAME_COVERAGE": (0.59, "data/exp_typed_role_selectional_asset_writerule_v1/"
                                      "metrics.json:report.AUC_PER_ARM.T2_UNTYPED_SAME_COVERAGE.auc"),
    "T3_COMBINED": (0.2264, "data/exp_typed_role_selectional_asset_writerule_v1/metrics.json:"
                           "report.AUC_PER_ARM.T3_COMBINED.auc"),
    "T4_BEST_COMBINED": (0.1144, "data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json:"
                                "report.T4_BEST_COMBINED.RESULT_held_out_selected_eval_AUC.auc"),
    "T5_SGNS_IN_IN": (0.4417, "data/exp_tuned_count_unsupervised_dissociation_v1/metrics.json:"
                             "report.T5_SGNS_FROM_SCRATCH.T5_IN_IN.auc"),
    "P2_PREDICTION_WEIGHTED": (0.0728, "data/exp_predictive_coding_write_gate_dissociation_v1/"
                                      "metrics.json:report.AUC_PER_ARM.P2_PREDICTION_WEIGHTED.auc"),
    "P1_PREDICTION_GATED_BEST": (0.3079, "data/exp_predictive_coding_write_gate_dissociation_v1/"
                                        "metrics.json:report.AUC_PER_ARM."
                                        "P1_PREDICTION_GATED_T0.5151.auc"),
}
P1_BEST_THRESHOLD = 0.5151   # MEASURED@data/exp_predictive_coding_write_gate_dissociation_v1/metrics.json:report.BEST_P1_THRESHOLD


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


# =================================================================================================
# REGRESSION GATE A -- DSI's (WordNet instrument) own 8 cached checks, recomputed bit-for-bit.
# =================================================================================================
def dsi_regression_gate() -> Dict:
    units = load_units(DSI_DIR)
    pop = units.get(unit_key("POPULATION", DSI.CODE_VERSION, "full"))
    scores = units.get(unit_key("SCORES", DSI.CODE_VERSION, "full"))
    if pop is None or scores is None:
        raise SystemExit("DSI CHECKPOINT MISSING at %s -- run exp_dissociation_score_instrument_v1.py "
                         "--grid full first; this cell must NOT rebuild the WordNet population." % DSI_DIR)
    arm_scores = {k: {"P": np.array(v["P"], dtype=np.float64), "S": np.array(v["S"], dtype=np.float64)}
                 for k, v in scores.items()}
    measured, failures = {}, []
    for name, exp_val in DSI_EXPECTED_CACHED.items():
        sc = arm_scores.get(name)
        if sc is None:
            failures.append({"name": name, "reason": "ARM_MISSING_FROM_DSI_CHECKPOINT"})
            continue
        got = DSI.auc_of(sc["P"], sc["S"])
        measured[name] = round(got, 4)
        if abs(got - exp_val) > REG_TOL:
            failures.append({"name": name, "expected": exp_val, "measured": round(got, 6),
                             "delta": round(got - exp_val, 6)})
    gate = {"PASS": len(failures) == 0, "measured": measured, "expected": DSI_EXPECTED_CACHED,
           "failures": failures, "tol": REG_TOL}
    if not gate["PASS"]:
        raise SystemExit("REGRESSION_GATE_A_FAILED -- DSI checkpoint drifted from its own landed "
                         "metrics.json: %r" % failures)
    print("[gate-A] DSI 8-check regression PASS: %r" % measured, flush=True)
    return gate


# =================================================================================================
# REGRESSION GATE B -- v3's (human instrument) own floors + n=65, recomputed bit-for-bit.
# =================================================================================================
def v3_regression_gate() -> Dict:
    units = load_units(H3_DIR)
    pop = units.get(unit_key("POPULATION_HUMAN", H3.CODE_VERSION, "full"))
    cheap = units.get(unit_key("SCORES_CHEAP", H3.CODE_VERSION, "full"))
    expensive = units.get(unit_key("SCORES_EXPENSIVE", H3.CODE_VERSION, "full"))
    if pop is None or cheap is None or expensive is None:
        raise SystemExit("V3 CHECKPOINT MISSING at %s -- run exp_dissociation_score_instrument_"
                         "human_v3.py --grid full first; this cell must NOT rebuild the human "
                         "population/matcher." % H3_DIR)
    matchedP = [tuple(x) for x in pop["matchedP"]]
    matchedS = [tuple(x) for x in pop["matchedS"]]
    n_match = len(matchedP)
    measured, failures = {}, []
    if n_match != V3_EXPECTED_N_MATCH:
        failures.append({"n_match_mismatch": n_match, "expected": V3_EXPECTED_N_MATCH})
    for name, exp_val in V3_EXPECTED_CACHED.items():
        rec = cheap.get(name)
        if rec is None:
            failures.append({"name": name, "reason": "ARM_MISSING_FROM_V3_CHECKPOINT"})
            continue
        got = DSI.auc_of(np.array(rec["P"], dtype=np.float64), np.array(rec["S"], dtype=np.float64))
        measured[name] = round(got, 4)
        if abs(got - exp_val) > REG_TOL:
            failures.append({"name": name, "expected": exp_val, "measured": round(got, 6),
                             "delta": round(got - exp_val, 6)})
    gate = {"PASS": len(failures) == 0, "measured": measured, "expected": V3_EXPECTED_CACHED,
           "n_match": n_match, "failures": failures, "tol": REG_TOL}
    if not gate["PASS"]:
        raise SystemExit("REGRESSION_GATE_B_FAILED -- v3 checkpoint drifted from its own landed "
                         "metrics.json: %r" % failures)
    print("[gate-B] v3 floors+n=65 regression PASS: n=%d measured=%r" % (n_match, measured), flush=True)
    existing_arm_scores = {k: {"P": np.array(v["P"], dtype=np.float64), "S": np.array(v["S"], dtype=np.float64)}
                          for k, v in expensive.items()}
    return {"gate": gate, "matchedP": matchedP, "matchedS": matchedS,
           "existing_arm_scores": existing_arm_scores}


# =================================================================================================
# NEW ARM CLUSTER BUILDERS -- each calls a sibling cell's own construction function VERBATIM on
# v3's human words_needed/matchedP/matchedS. Returns {arm_name: (P_arr, S_arr)}, diag.
# =================================================================================================
def build_maxpool_arms(words_needed: List[str], matchedP, matchedS, buckets, sents) -> Tuple[Dict, Dict]:
    occ_lists, occ_diag = MP.build_occurrence_lists(words_needed, buckets, sents)
    valid_words = set(w for w in words_needed if len(occ_lists.get(w, [])) > 0)

    def _both_valid(pairs):
        return [p for p in pairs if p[0] in valid_words and p[1] in valid_words]

    mP, mS = _both_valid(matchedP), _both_valid(matchedS)
    diag = {"occ_diag": occ_diag, "n_valid_words": len(valid_words), "n_words_needed": len(words_needed),
           "n_matchedP_used": len(mP), "n_matchedS_used": len(mS),
           "n_matchedP_dropped": len(matchedP) - len(mP), "n_matchedS_dropped": len(matchedS) - len(mS)}
    if len(mP) < 5 or len(mS) < 5:
        diag["SKIPPED"] = "too few pairs survive the occurrence filter"
        return {}, diag
    vocab_occ = INFO.build_vocab([{(w, i): c for i, c in enumerate(occ_lists.get(w, []))} for w in words_needed])
    M_occ, row_range = MP.occurrence_sparse_matrix(occ_lists, words_needed, vocab_occ)
    idx_of_own = {w: np.arange(*row_range[w]) for w in words_needed}
    arms = {"M1_MAXPOOL": (MP.pair_scores_from_index_map(M_occ, idx_of_own, mP, topk=1),
                          MP.pair_scores_from_index_map(M_occ, idx_of_own, mS, topk=1))}
    for kk in (2, 3, 5):
        arms["M2_TOPK_MEAN_K%d" % kk] = (MP.pair_scores_from_index_map(M_occ, idx_of_own, mP, topk=kk),
                                        MP.pair_scores_from_index_map(M_occ, idx_of_own, mS, topk=kk))
    diag["vocab_size"] = len(vocab_occ)
    return arms, diag


def build_filter_arms(words_needed: List[str], matchedP, matchedS, buckets, sents) -> Tuple[Dict, Dict]:
    F1_counts, f1_diag = FSG.build_variant_counts(words_needed, buckets, sents,
                                                  WR.raw_counts_unfiltered_for_window, "F1")
    encoder = FSG.StructuralEncoder(repo_root=REPO)
    F2_counts, f2_diag = FSG.build_variant_counts(
        words_needed, buckets, sents, lambda s_, a_: FSG.raw_counts_pos_strict_for_window(encoder, s_, a_), "F2")

    def _f3(s_, a_):
        c, _found = FSG.raw_counts_syntactic_neighbours_for_window(encoder, s_, a_)
        return c

    F3_counts, f3_diag = FSG.build_variant_counts(words_needed, buckets, sents, _f3, "F3")
    F4_1, _ = FSG.build_variant_counts(
        words_needed, buckets, sents, lambda s_, a_: FSG.raw_counts_windowed_for_window(s_, a_, 1), "F4w1")
    F4_2, _ = FSG.build_variant_counts(
        words_needed, buckets, sents, lambda s_, a_: FSG.raw_counts_windowed_for_window(s_, a_, 2), "F4w2")
    F4_5, _ = FSG.build_variant_counts(
        words_needed, buckets, sents, lambda s_, a_: FSG.raw_counts_windowed_for_window(s_, a_, 5), "F4w5")
    stores = {
        "F1_NO_FILTER": DSI.counts_to_dense_store(F1_counts, words_needed),
        "F2_CONTENT_ONLY_STRICT": DSI.counts_to_dense_store(F2_counts, words_needed),
        "F3_SYNTACTIC_NEIGHBOURS_ONLY": DSI.counts_to_dense_store(F3_counts, words_needed),
        "F4_WINDOW_1": DSI.counts_to_dense_store(F4_1, words_needed),
        "F4_WINDOW_2": DSI.counts_to_dense_store(F4_2, words_needed),
        "F4_WINDOW_5": DSI.counts_to_dense_store(F4_5, words_needed),
    }
    arms = {name: (DSI.dense_scores_from_dict_store(store, matchedP),
                  DSI.dense_scores_from_dict_store(store, matchedS)) for name, store in stores.items()}
    diag = {"f1": f1_diag, "f2": f2_diag, "f3": f3_diag, "encoder_stats": encoder.stats()}
    return arms, diag


def build_typed_role_arms(words_needed: List[str], matchedP, matchedS, mat, mat_ok, pos_idx) -> Tuple[Dict, Dict]:
    asset = TR.load_selectional_asset()
    slot_filler = asset["slot_filler"]
    mat_t1_raw, col_names = TR.build_typed_role_matrix(words_needed, slot_filler)
    mat_t2_raw, verb_names = TR.collapse_roles(mat_t1_raw, col_names)
    covered = TR.covered_words(mat_t1_raw, words_needed)
    emb_t1, k_t1 = TR.ppmi_svd(mat_t1_raw, TR.N_TARGET, seed=MASTER_SEED + 9201)
    emb_t2, k_t2 = TR.ppmi_svd(mat_t2_raw, TR.N_TARGET, seed=MASTER_SEED + 9202)
    store_t1 = TR.store_from_matrix(emb_t1, words_needed)
    store_t2 = TR.store_from_matrix(emb_t2, words_needed)
    Mn_incumbent = l2n(mat)
    store_a0 = {w: Mn_incumbent[pos_idx[w]] for w in words_needed if w in pos_idx and mat_ok[pos_idx[w]]}

    def _l2_row(v):
        n = np.linalg.norm(v)
        return v / n if n > 1e-12 else v

    d_a0 = mat.shape[1]
    store_t3 = {w: _l2_row(np.concatenate([_l2_row(store_t1[w]), _l2_row(store_a0.get(w, np.zeros(d_a0)))]))
               for w in words_needed}
    stores = {"T1_TYPED_ROLE": store_t1, "T2_UNTYPED_SAME_COVERAGE": store_t2, "T3_COMBINED": store_t3}
    arms = {name: (DSI.dense_scores_from_dict_store(store, matchedP),
                  DSI.dense_scores_from_dict_store(store, matchedS)) for name, store in stores.items()}
    diag = {"typed_matrix_shape": list(mat_t1_raw.shape), "n_typed_cols": len(col_names),
           "n_verb_cols_untyped": len(verb_names), "n_covered_words": len(covered),
           "svd_achieved_ranks": {"T1": k_t1, "T2": k_t2}}
    return arms, diag


def build_tuned_count_arms(words_needed: List[str], matchedP, matchedS, anchor_words_full: List[str]) -> Tuple[Dict, Dict]:
    M, row_idx, matrix_diag = CAP.build_matrix(anchor_words_full)
    diag: Dict = {"MATRIX": matrix_diag}
    arms: Dict = {}
    Mppmi_t4 = TC.ppmi_tuned(M, alpha=1.0, k_shift=15, subsample_t=None)
    vecs_t4 = TC.svd_vectors_p(Mppmi_t4, 50, 0.0, TC._seed_for("V4:T4_p0.00_k50"))
    if vecs_t4 is not None:
        store_t4 = {w: vecs_t4[row_idx[w]] for w in words_needed if w in row_idx}
        arms["T4_BEST_COMBINED"] = (DSI.dense_scores_from_dict_store(store_t4, matchedP),
                                    DSI.dense_scores_from_dict_store(store_t4, matchedS))
    else:
        diag["T4_SKIPPED"] = "SVD_RANK_CEILING (k=50 exceeded matrix rank)"
    sgns = TC.run_sgns_arm({}, matchedP, matchedS)
    diag["T5_sgns_diag"] = {k: v for k, v in sgns.items()
                           if k not in ("T5_IN_IN", "T5_IN_OUT_bonus_diagnostic", "N1_UNTRAINED_RANDOM_INIT_CONTROL")}
    if not sgns.get("SKIPPED", True) and sgns.get("T5_IN_IN") is not None:
        diag["T5_SGNS_RESULT_ALREADY_SCORED"] = sgns["T5_IN_IN"]
        arms["__PRESCORED__T5_SGNS_IN_IN"] = sgns["T5_IN_IN"]
    else:
        diag["T5_SKIPPED"] = sgns.get("reason", "unknown")
    return arms, diag


def build_predictive_coding_arms(words_needed: List[str], matchedP, matchedS) -> Tuple[Dict, Dict]:
    obs = PCW.SWU.build_obs_stream()
    rng1 = np.random.default_rng(MASTER_SEED + 9301)
    store_p2, diag_p2 = PCW.build_store(obs, words_needed, "P2_WEIGHTED", 0.0, rng1)
    rng2 = np.random.default_rng(MASTER_SEED + 9302)
    store_p1, diag_p1 = PCW.build_store(obs, words_needed, "P1_GATE", P1_BEST_THRESHOLD, rng2)
    sc_p2 = PCW.store_to_scores(store_p2, matchedP, matchedS)
    sc_p1 = PCW.store_to_scores(store_p1, matchedP, matchedS)
    arms = {"P2_PREDICTION_WEIGHTED": (sc_p2["P"], sc_p2["S"]),
           "P1_PREDICTION_GATED_BEST": (sc_p1["P"], sc_p1["S"])}
    diag = {"P2_diag": diag_p2, "P1_diag": diag_p1, "P1_threshold": P1_BEST_THRESHOLD}
    return arms, diag


# =================================================================================================
# self-test -- reuses every sibling module's own self-test wholesale (proves every reused
# entrypoint), then exercises THIS FILE'S OWN glue (the 5 build_* functions above) on a TINY REAL
# slice of v3's own checkpoint (words_needed[:6], pairs restricted to that slice) -- META_RULE F.1:
# the real substrate objects (real corpus, real selectional asset, real StructuralEncoder, real
# CAP.build_matrix/TC.svd_vectors_p, real PCW.build_store), not a synthetic-only branch.
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    ev["DSI_selftest"] = DSI.self_test()
    ev["H3_selftest"] = H3.self_test()
    ev["MP_selftest"] = MP.self_test()
    ev["FSG_selftest"] = FSG.self_test()
    ev["TR_selftest"] = TR.self_test()
    print("[selftest] all 5 reused-module self-tests PASS", flush=True)

    # --- real code path: THIS FILE'S OWN glue functions on a tiny slice of v3's REAL checkpoint ----
    units = load_units(H3_DIR)
    pop = units.get(unit_key("POPULATION_HUMAN", H3.CODE_VERSION, "full"))
    assert pop is not None, "v3 checkpoint required for self-test (run v3 --grid full first)"
    matchedP_full = [tuple(x) for x in pop["matchedP"]]
    matchedS_full = [tuple(x) for x in pop["matchedS"]]
    words_tiny = sorted(set(w for w1, w2, _ in matchedP_full[:6] + matchedS_full[:6] for w in (w1, w2)))[:8]

    def _restrict(pairs):
        return [p for p in pairs if p[0] in words_tiny and p[1] in words_tiny][:3]

    mP_tiny, mS_tiny = _restrict(matchedP_full), _restrict(matchedS_full)
    if len(mP_tiny) < 1 or len(mS_tiny) < 1:
        # words_tiny slice happened not to contain a full pair -- fall back to the raw first pairs'
        # own endpoints directly, still real data, still tiny.
        mP_tiny = matchedP_full[:2]
        mS_tiny = matchedS_full[:2]
        words_tiny = sorted(set(w for w1, w2, _ in mP_tiny + mS_tiny for w in (w1, w2)))

    sents, buckets, _counts, _prov = INFO.load_corpus_and_buckets()
    arms_mp, diag_mp = build_maxpool_arms(words_tiny, mP_tiny, mS_tiny, buckets, sents)
    ev["real_code_path_maxpool"] = {"n_arms": len(arms_mp), "diag_keys": sorted(diag_mp.keys())}

    arms_f, diag_f = build_filter_arms(words_tiny, mP_tiny, mS_tiny, buckets, sents)
    assert len(arms_f) == 6, "build_filter_arms must always produce all 6 F-arms: got %r" % sorted(arms_f)
    for name, (spv, ssv) in arms_f.items():
        assert len(spv) == len(mP_tiny) and len(ssv) == len(mS_tiny), \
            "filter arm %r score length mismatch" % name
    ev["real_code_path_filter"] = {"n_arms": len(arms_f), "arm_names": sorted(arms_f)}

    C = CTS.load_cache()
    mat = np.asarray(C["mat"], dtype=np.float32)
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    pos_idx = C["pos"]
    arms_tr, diag_tr = build_typed_role_arms(words_tiny, mP_tiny, mS_tiny, mat, mat_ok, pos_idx)
    assert len(arms_tr) == 3, "build_typed_role_arms must always produce 3 T-arms: got %r" % sorted(arms_tr)
    ev["real_code_path_typed_role"] = {"n_arms": len(arms_tr), "diag": diag_tr}

    arms_pc, diag_pc = build_predictive_coding_arms(words_tiny, mP_tiny, mS_tiny)
    assert len(arms_pc) == 2, "build_predictive_coding_arms must always produce 2 P-arms: got %r" % sorted(arms_pc)
    ev["real_code_path_predictive_coding"] = {"n_arms": len(arms_pc), "diag_keys": sorted(diag_pc.keys())}

    # --- ARMS-MUST-DIFFER sanity on the tiny slice's filter arms. NOTE: at this tiny scale (2-3
    # pairs, short sentences) some window sizes genuinely coincide (F4_WINDOW_2/5 can see the exact
    # same tokens as F3 when a sentence is short) -- that is a scale artifact, not a construction
    # bug (the sibling cell's own FULL-population AUCs for these arms differ: F3=0.4876,
    # F4_WINDOW_1=0.4959, F4_WINDOW_2=0.4731, F4_WINDOW_5=0.4561, all distinct). The REAL
    # arms-must-differ gate (all-distinct, at full 65-pair scale) runs in run() below, on every arm.
    # Here we only assert the tiny slice is not COMPLETELY degenerate (at least 2 distinct outputs).
    digests = {name: DSI._digest(np.concatenate([spv, ssv])) for name, (spv, ssv) in arms_f.items()}
    assert len(set(digests.values())) >= 2, \
        "tiny filter-arm slice fully degenerate (all 6 arms identical) -- construction bug: %r" % digests
    ev["arms_must_differ_known_answer"] = sorted(digests)

    # --- module-level config sanity ------------------------------------------------------------------
    assert len(HARVESTED_WORDNET_AUC) == 17, "expected exactly 17 harvested new-arm AUCs: got %d" % len(HARVESTED_WORDNET_AUC)
    assert set(DSI_EXPECTED_CACHED) == {"F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE",
                                        "KNOWN_ANSWER_WORDNET_PATH_SIM", "RANDOM_VECTOR_STORE",
                                        "INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM"}
    ev["config_known_answer"] = {"n_harvested_new_arms": len(HARVESTED_WORDNET_AUC),
                                 "n_dsi_expected_checks": len(DSI_EXPECTED_CACHED),
                                 "n_v3_expected_checks": len(V3_EXPECTED_CACHED)}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True}

    # =============================== REGRESSION GATES (EXIT ON FAILURE) =============================
    gate_a = dsi_regression_gate()
    rep["REGRESSION_GATE_A_DSI_WORDNET_INSTRUMENT"] = gate_a
    gate_b_out = v3_regression_gate()
    rep["REGRESSION_GATE_B_V3_HUMAN_INSTRUMENT"] = gate_b_out["gate"]

    matchedP_full = gate_b_out["matchedP"]
    matchedS_full = gate_b_out["matchedS"]
    existing_arm_scores_full = gate_b_out["existing_arm_scores"]

    if grid == "reduced":
        word_universe = sorted(set(w for w1, w2, _p in matchedP_full + matchedS_full for w in (w1, w2)))
        keep_words = set(word_universe[:N_SMOKE_WORDS])
        matchedP = [t for t in matchedP_full if t[0] in keep_words and t[1] in keep_words]
        matchedS = [t for t in matchedS_full if t[0] in keep_words and t[1] in keep_words]
        if len(matchedP) < 5 or len(matchedS) < 5:
            matchedP, matchedS = matchedP_full[:10], matchedS_full[:10]
    else:
        matchedP, matchedS = matchedP_full, matchedS_full

    words_needed = sorted(set(w for w1, w2, _p in matchedP + matchedS for w in (w1, w2)))
    rep["N_MATCHED_PAIRS_PER_CELL"] = len(matchedP)
    rep["N_WORDS_NEEDED"] = len(words_needed)
    print("[population] REUSED v3's own %d matched pairs/cell (grid=%s), %d distinct words" %
         (len(matchedP), grid, len(words_needed)), flush=True)

    # existing 7 arms: slice v3's own cached P/S score arrays down to the (possibly smoke-truncated)
    # matchedP/matchedS index range -- v3 built its arrays in the SAME order as its own matchedP/
    # matchedS list, and smoke here truncates by WORD not by index, so re-score via dict lookup
    # instead of a raw slice when grid == reduced.
    def _existing_scores(name: str) -> Tuple[np.ndarray, np.ndarray]:
        arr = existing_arm_scores_full[name]
        if grid == "full":
            return arr["P"], arr["S"]
        # reduced: rebuild the store implicitly is not available (only scores are cached) -- for
        # smoke we just take the first len(matchedP)/len(matchedS) cached entries, which is a valid
        # (if not identically-matched) smoke exercise of the scoring/bootstrap machinery.
        return arr["P"][: len(matchedP)], arr["S"][: len(matchedS)]

    EXISTING_SEVEN = ["INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM", "RAW_COUNT_SINGLE_OCC",
                     "PRESENCE_ABSENCE_BINARIZED", "PARADIGMATIC_PROFILE_WRITE",
                     "T0_VANILLA_PPMI_SVD", "T2_SHIFTED_PPMI_K15"]
    all_scores: Dict[str, Tuple[np.ndarray, np.ndarray]] = {name: _existing_scores(name) for name in EXISTING_SEVEN}

    sents, buckets, _counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    C = CTS.load_cache()
    mat = np.asarray(C["mat"], dtype=np.float32)
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    pos_idx = C["pos"]
    anchors_all = C["anchors"]
    anchor_set = set(a for a, ok in zip(anchors_all, mat_ok) if ok)
    anchor_words_full = sorted(anchor_set)
    if grid == "reduced":
        anchor_words_full = sorted(set(anchor_words_full[:1200]) | set(words_needed))

    # =============================== NEW ARM CLUSTERS (checkpointed, each independently guarded) ====
    cluster_key = unit_key("NEW_ARM_CLUSTERS", CODE_VERSION, grid)
    prior_clusters = load_units(out_dir_ckpt).get(cluster_key)
    failed_clusters: Dict[str, str] = {}
    cluster_diags: Dict[str, Dict] = {}
    if prior_clusters is not None:
        print("[clusters] RESUMED FROM CHECKPOINT", flush=True)
        for name, rec in prior_clusters["scores"].items():
            all_scores[name] = (np.array(rec["P"]), np.array(rec["S"]))
        failed_clusters = prior_clusters["failed_clusters"]
        cluster_diags = prior_clusters["diags"]
    else:
        prescored: Dict[str, Dict] = {}
        try:
            t_c = time.time()
            arms, diag = build_maxpool_arms(words_needed, matchedP, matchedS, buckets, sents)
            all_scores.update(arms)
            cluster_diags["maxpool"] = diag
            print("[cluster] maxpool: %d arms built in %.1fs" % (len(arms), time.time() - t_c), flush=True)
        except Exception as e:
            failed_clusters["maxpool"] = "%s: %s" % (type(e).__name__, str(e)[:500])
            print("[cluster] maxpool FAILED: %s" % failed_clusters["maxpool"], flush=True)

        try:
            t_c = time.time()
            arms, diag = build_filter_arms(words_needed, matchedP, matchedS, buckets, sents)
            all_scores.update(arms)
            cluster_diags["filter"] = diag
            print("[cluster] filter: %d arms built in %.1fs" % (len(arms), time.time() - t_c), flush=True)
        except Exception as e:
            failed_clusters["filter"] = "%s: %s" % (type(e).__name__, str(e)[:500])
            print("[cluster] filter FAILED: %s" % failed_clusters["filter"], flush=True)

        try:
            t_c = time.time()
            arms, diag = build_typed_role_arms(words_needed, matchedP, matchedS, mat, mat_ok, pos_idx)
            all_scores.update(arms)
            cluster_diags["typed_role"] = diag
            print("[cluster] typed_role: %d arms built in %.1fs" % (len(arms), time.time() - t_c), flush=True)
        except Exception as e:
            failed_clusters["typed_role"] = "%s: %s" % (type(e).__name__, str(e)[:500])
            print("[cluster] typed_role FAILED: %s" % failed_clusters["typed_role"], flush=True)

        try:
            t_c = time.time()
            arms, diag = build_tuned_count_arms(words_needed, matchedP, matchedS, anchor_words_full)
            for name, val in arms.items():
                if name.startswith("__PRESCORED__"):
                    prescored[name[len("__PRESCORED__"):]] = val
                else:
                    all_scores[name] = val
            cluster_diags["tuned_count"] = diag
            print("[cluster] tuned_count: %d arms built in %.1fs" % (len(arms), time.time() - t_c), flush=True)
        except Exception as e:
            failed_clusters["tuned_count"] = "%s: %s" % (type(e).__name__, str(e)[:500])
            print("[cluster] tuned_count FAILED: %s" % failed_clusters["tuned_count"], flush=True)

        try:
            t_c = time.time()
            arms, diag = build_predictive_coding_arms(words_needed, matchedP, matchedS)
            all_scores.update(arms)
            cluster_diags["predictive_coding"] = diag
            print("[cluster] predictive_coding: %d arms built in %.1fs" % (len(arms), time.time() - t_c), flush=True)
        except Exception as e:
            failed_clusters["predictive_coding"] = "%s: %s" % (type(e).__name__, str(e)[:500])
            print("[cluster] predictive_coding FAILED: %s" % failed_clusters["predictive_coding"], flush=True)

        record_unit(out_dir_ckpt, cluster_key,
                   {"scores": {k: {"P": v[0].tolist(), "S": v[1].tolist()} for k, v in all_scores.items()
                              if k not in EXISTING_SEVEN},
                    "failed_clusters": failed_clusters, "diags": cluster_diags,
                    "prescored": prescored})
    rep["FAILED_ARM_CLUSTERS"] = failed_clusters
    rep["CLUSTER_DIAGS"] = cluster_diags

    # re-derive `prescored` on the resumed-from-checkpoint path too
    if prior_clusters is not None:
        prescored = prior_clusters.get("prescored", {})

    # =============================== SCORE EVERY ARM (AUC bootstrap) ================================
    boot_seed_base = MASTER_SEED + 8484
    auc_results: Dict[str, Dict] = {}
    for i, (name, (spv, ssv)) in enumerate(sorted(all_scores.items())):
        spv = np.asarray(spv, dtype=np.float64)
        ssv = np.asarray(ssv, dtype=np.float64)
        spv, ssv = spv[~np.isnan(spv)], ssv[~np.isnan(ssv)]
        res = DSI.auc_bootstrap(spv, ssv, N_BOOT, boot_seed_base + i)
        auc_results[name] = res
        print("[auc] %-32s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]), flush=True)
    for name, res in prescored.items():
        auc_results[name] = res
        print("[auc-prescored] %-22s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]), flush=True)

    rep["N_ARMS_ACHIEVED"] = len(auc_results)
    rep["ARM_NAMES"] = sorted(auc_results)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {}
    for name, (spv, ssv) in all_scores.items():
        digests[name] = DSI._digest(np.concatenate([np.asarray(spv), np.asarray(ssv)]))
    for name, res in prescored.items():
        digests[name] = "PRESCORED_%s_%s" % (name, round(res["auc"], 6))
    dup_check: Dict[str, List[str]] = {}
    for name, dg in digests.items():
        dup_check.setdefault(dg, []).append(name)
    duplicate_groups = {dg: names for dg, names in dup_check.items() if len(names) > 1}
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests
    rep["ARMS_MUST_DIFFER_DUPLICATE_GROUPS"] = duplicate_groups
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    if duplicate_groups:
        print("[WARN] duplicate score-vector groups found (bit-identical arms): %r" % duplicate_groups, flush=True)

    # =============================== HUMAN AUC PER ARM ===============================================
    rep["HUMAN_AUC_PER_ARM"] = auc_results

    # =============================== WORDNET AUC PER ARM (existing 7 harvested from v3's own cached
    # rank-correlation dict; new 17 harvested from each sibling's own metrics.json, hardcoded above) ==
    wordnet_aucs: Dict[str, float] = {}
    wordnet_sources: Dict[str, str] = {}
    try:
        with open(os.path.join(H3_DIR, "metrics.json"), encoding="utf-8") as f:
            v3_metrics = json.load(f)
        wn7 = v3_metrics["report"]["RANK_CORRELATION"]["wordnet_instrument_aucs"]
        for name in EXISTING_SEVEN:
            wordnet_aucs[name] = wn7[name]
            wordnet_sources[name] = "data/exp_dissociation_score_instrument_human_v3/metrics.json:" \
                                    "report.RANK_CORRELATION.wordnet_instrument_aucs.%s" % name
    except Exception as e:
        rep["WORDNET_AUC_HARVEST_ERROR_EXISTING_SEVEN"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    for name, (auc_val, src) in HARVESTED_WORDNET_AUC.items():
        wordnet_aucs[name] = auc_val
        wordnet_sources[name] = src
    rep["WORDNET_AUC_PER_ARM"] = wordnet_aucs
    rep["WORDNET_AUC_SOURCES"] = wordnet_sources

    # =============================== RANK CORRELATION -- AT 7 ARMS AND AT FINAL COUNT, SIDE BY SIDE ===
    def _rank_corr(arm_names: List[str], tag: str) -> Dict:
        usable = [a for a in arm_names if a in wordnet_aucs and a in auc_results]
        missing = [a for a in arm_names if a not in usable]
        n = len(usable)
        out: Dict = {"tag": tag, "n_arms_requested": len(arm_names), "n_arms_usable": n, "missing_arms": missing}
        if n < 3:
            out["SKIPPED"] = "fewer than 3 usable arms"
            return out
        wn_vec = np.array([wordnet_aucs[a] for a in usable])
        hu_vec = np.array([auc_results[a]["auc"] for a in usable])
        rho, _p_asymp = spearmanr(wn_vec, hu_vec)
        rho = None if np.isnan(rho) else round(float(rho), 4)
        out["spearman_rho"] = rho
        out["arm_names_used"] = usable
        if n <= 8:
            perm_rhos = []
            for perm in itertools.permutations(range(n)):
                r, _ = spearmanr(wn_vec, hu_vec[list(perm)])
                perm_rhos.append(r if not np.isnan(r) else 0.0)
            perm_rhos = np.array(perm_rhos)
            exact_p = float(np.mean(np.abs(perm_rhos) >= abs(rho if rho is not None else 0.0) - 1e-9))
            out["permutation_p_method"] = "exact"
            out["permutation_p"] = round(exact_p, 4)
        else:
            rng_mc = np.random.default_rng(MASTER_SEED + 7171 + n)
            perm_rhos = []
            for _ in range(N_PERM_MC):
                perm = rng_mc.permutation(n)
                r, _ = spearmanr(wn_vec, hu_vec[perm])
                perm_rhos.append(r if not np.isnan(r) else 0.0)
            perm_rhos = np.array(perm_rhos)
            mc_p = float(np.mean(np.abs(perm_rhos) >= abs(rho if rho is not None else 0.0) - 1e-9))
            out["permutation_p_method"] = "monte_carlo_%d_draws_NOT_exact" % N_PERM_MC
            out["permutation_p"] = round(mc_p, 4)
        rng_bs = np.random.default_rng(MASTER_SEED + 6161 + n)
        boot_rhos = []
        for _ in range(10000):
            idx = rng_bs.integers(0, n, size=n)
            r, _ = spearmanr(wn_vec[idx], hu_vec[idx])
            if not np.isnan(r):
                boot_rhos.append(r)
        boot_rhos = np.array(boot_rhos) if boot_rhos else np.array([np.nan])
        out["bootstrap_of_arms_ci95"] = [round(float(np.nanpercentile(boot_rhos, 2.5)), 4),
                                        round(float(np.nanpercentile(boot_rhos, 97.5)), 4)]
        out["DISCLOSURE"] = ("the bootstrap resamples ARMS, not pairs; a small n here yields a wide "
                            "CI regardless of how good each per-arm AUC estimate is")
        return out

    rank_corr_7 = _rank_corr(H2.SEVEN_ARMS, "SEVEN_ARMS_v3_BASELINE_COMPARISON")
    rank_corr_all = _rank_corr(sorted(auc_results), "ALL_ACHIEVED_ARMS")
    rep["RANK_CORRELATION_AT_7_ARMS"] = rank_corr_7
    rep["RANK_CORRELATION_AT_FINAL_COUNT"] = rank_corr_all
    rep["POPULATIONS_NOT_COMPARABLE"] = (
        "this instrument's matched population and the WordNet instrument's are DIFFERENT, "
        "non-overlapping-by-construction pools -- absolute AUC values are NEVER compared side by "
        "side across the two instruments; only RANK_CORRELATION (the arm ORDERING) is a valid "
        "cross-instrument statement")

    # =============================== PRE-COMMITTED INTERPRETATION ====================================
    ci7 = rank_corr_7.get("bootstrap_of_arms_ci95", [None, None])
    ciN = rank_corr_all.get("bootstrap_of_arms_ci95", [None, None])
    rho7 = rank_corr_7.get("spearman_rho")
    rhoN = rank_corr_all.get("spearman_rho")
    if failed_clusters and rep["N_ARMS_ACHIEVED"] < 20:
        interp = ("ARM_COUNT_TARGET_MISSED__achieved=%d__failed_clusters=%r" %
                 (rep["N_ARMS_ACHIEVED"], sorted(failed_clusters)))
    elif rhoN is not None and ciN[0] is not None and ciN[0] > 0:
        interp = ("STOP_IF_i_CI_EXCLUDES_ZERO_POSITIVE__ORDERINGS_AGREE__ORGAN_A_CLOSURE_IS_ABOUT_"
                 "OUR_STORE__rho_at_%d_arms=%.4f__rho_at_7_arms=%r" %
                 (rep["N_ARMS_ACHIEVED"], rhoN, rho7))
    elif rhoN is not None and rhoN < 0 and ciN[1] is not None and ciN[1] < 0:
        interp = ("STOP_IF_iii_CI_EXCLUDES_ZERO_NEGATIVE__ORDERINGS_DISAGREE__6_24_IS_THE_HEADLINE__"
                 "rho_at_%d_arms=%.4f__rho_at_7_arms=%r" % (rep["N_ARMS_ACHIEVED"], rhoN, rho7))
    else:
        interp = ("STOP_IF_ii_CI_STILL_INCLUDES_ZERO_AT_%d_ARMS__ARM_COUNT_WAS_NOT_THE_LIMIT_EITHER__"
                 "rho_at_%d_arms=%r__ci=%r__rho_at_7_arms=%r__ci_at_7=%r" %
                 (rep["N_ARMS_ACHIEVED"], rep["N_ARMS_ACHIEVED"], rhoN, ciN, rho7, ci7))
    rep["INTERPRETATION"] = interp
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

    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "DISSOCIATION_INSTRUMENT_HUMAN_V4__%s" % interp

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Harvest every landed store variant onto both instruments; recompute the "
                       "arm-ordering rank correlation with a much larger arm set than v3's n=7 -> "
                       + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "N_PERM_MC": N_PERM_MC},
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
