"""exp_dissociation_score_instrument_human_v2 -- SAME QUESTION, WORDNET-FREE LABELS. SUPERSEDES v1.

THIS CELL EXISTS TO TEST WHETHER PLAN SEC 6.23'S CONCLUSION IS ABOUT OUR STORE OR ABOUT WORDNET.

**SUPERSEDES `experiments/exp_dissociation_score_instrument_human_v1.py` (commit `3f498cf52`,
committed AS THE PERMANENT RECORD OF A NULL -- left UNMODIFIED, do not edit that file).** v1's FULL
run halted with `SystemExit` at `n_match=7` per cell (< its own `n_match<20` floor), writing NO
metrics.json (`notes/human_judgement_instrument_power_failure_2026-08-18.md`). v1's population
construction (`combine_benchmark_pairs(anchor_set)` over the FULL 5,491-anchor set) was already
NOT restricted to the WordNet-licensed instrument's own (much smaller) matched-pair population --
verified off v1's own checkpoint, `data/exp_dissociation_score_instrument_human_v1/units.jsonl`,
unit `POPULATION_HUMAN|v1.0|full`. The MEASURED cause of n=7 is in that same checkpoint's
`matching.pre_match_smd.mean_log_freq = -1.8396` and `matching.per_pos_stratum`: SET_P_HUMAN
(human-rated similar, zero-cooccurring) pairs are structurally far rarer than SET_S_HUMAN (highly
co-occurring) pairs, and the REUSED caliper (tightened to 0.02 on the frequency covariates
specifically for the WordNet-labelled population's own 4-round matching repair,
`exp_dissociation_score_instrument_v1.DEFAULT_CALIPER_SQ_PER_DIM`) caliper-drops 429 of 436
candidates (98.4%) -- adjective and noun POS strata drop to ZERO matches, verb yields the 7 that
survive. This is a NEW, deliberate finding from the same underlying frequency-structure asymmetry,
not a restriction bug this file needs to fix by loosening anything (the dispatch brief is explicit:
NEVER loosen the caliper to buy n). **What v2 actually fixes is PROCESS, not population or caliper:**
v1's uninformative `SystemExit`-with-no-metrics-file at n<20 is replaced with an honest
`POWER_INSUFFICIENT` verdict WRITTEN to metrics.json (with the full funnel) at a RAISED threshold
n<`POWER_INSUFFICIENT_MIN_N`=60 per the dispatch brief; the LICENSE GATE (four floors + known-answer
+ random-store, all CHEAP) is now built and checked BEFORE any of the 7 expensive re-scored arms, so
an unlicensed population never pays for a PPMI+SVD rebuild; and `max(four floors)` is reported as the
real bar (0.5431 on the WordNet instrument, not 0.5), read fresh off disk, never hardcoded. See
"CODE_VERSION v2.0 AMENDMENT" further down for the full account, kept from the original authoring
pass. **The decisive statistic remains a RANK CORRELATION over ARM ORDERINGS, which needs no shared
ITEMS between the two instruments** -- that design was already correct in v1 and is unchanged here.

Verified off disk (`exp_dissociation_score_instrument_v1.py:304,312,674`): `SET_P` is built by
`build_wordnet_synonym_candidates()` from `wn.synsets()`; `SET_S` explicitly excludes any WordNet
pair even at high co-occurrence; the known-answer arm is WordNet path similarity. WordNet defines
BOTH sides of the licensed instrument's labels (plan sec 6.24). Every number in plan 6.12-6.23 is
therefore really "agreement with WordNet's notion of synonymy". This cell reruns the SAME 7 arms on
a SECOND, INDEPENDENT construction whose labels come from HUMAN SIMILARITY JUDGEMENTS
(SimLex-999 + SimVerb-3500) instead of WordNet, and reports the rank correlation between the two
instruments' arm orderings. Full spec: notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.24 (commit
21c9b3e19), pre-reg preregs/2026-08-18_dissociation_score_instrument_human_v1.md (amendment section
added for v2).

=================================================================================================
PRIOR-WORK CHECK (mandatory per .claude/agents/exp_dev.md). `bash tools/substrate_query.sh` was
run before authoring with the query "human similarity judgement dissociation instrument SimLex
SimVerb independent circularity WordNet substitutability"; it returned EMPTY output (0 bytes) after
completing in the background -- the query tool is documented elsewhere in this repo
(`exp_tuned_count_unsupervised_dissociation_v1.py` docstring) as running very slowly under
concurrent agent load on 2026-08-18, and here it produced no readable result at all rather than a
slow-but-valid one. Backstop: `find experiments -iname "*human*dissoc*" -o -iname "*simlex*" -o
-iname "*simverb*"` and `find notes -iname "*human*substitut*" -o -iname "*simlex*"` both return
NOTHING. This cell is also a direct, explicitly-named follow-on to plan sec 6.24 itself (landed
`21c9b3e19`), which names the exact gap ("a second, INDEPENDENT operationalisation of
substitutability... candidate independent targets... human substitution judgements") -- not an
independently-conceived direction, so the prior-work risk this gate guards against is structurally
low regardless of the query's failure. Disclosed rather than silently proceeding as if the query had
answered cleanly.

=================================================================================================
LABEL SOURCE, WORDNET-FREE END TO END (data/encoder_eval_benchmarks/, gitignored deliberately, read
from -- NEVER `git add -f`, NEVER edit .gitignore):
  simlex999.txt     999 pairs, human similarity ratings 0-10, POS in {A,N,V}. Hill, Reichart &
                    Korhonen (2015).
  simverb3500.txt   3500 verb pairs, human similarity ratings mapped to the SAME 0-10 scale, POS
                    always V. Gerz, Vulic, Hill, Reichart & Korhonen (2016).
The published 0-10 SCORE is a crowd-sourced human judgement in both benchmarks -- not a WordNet
computation. (CITED, not independently re-verified by live literature search in this exp_dev role:
SimLex-999's published methodology describes pair CANDIDATE generation as drawn from multiple
sources including free-association norms and WordNet-adjacent pairs; that may make WordNet a
partial influence on which pairs were PUT UP for rating, but not on the SCORE itself, which is what
this cell thresholds on -- unlike the licensed instrument, where the label is a DETERMINISTIC
function of `wn.synsets()`.) The measured overlap fraction below is what actually decides whether
this test is independent enough to answer the question.

=================================================================================================
CONSTRUCTION (mirrors the licensed instrument's machinery so the comparison is fair; deviations
disclosed inline, not silently taken):
  SET_P_HUMAN   Benchmark pairs (SimLex + SimVerb combined, SimLex takes precedence on a duplicate
                unordered pair) with published score >= T_HIGH=6.0, restricted to pairs where BOTH
                members are valid corpus anchors, AND zero corpus co-occurrence (EXPLICIT design
                choice, not verbatim in the brief -- added so this arm cannot pass merely by
                encoding co-occurrence; disclosed in the pre-reg's Construction section).
  SET_S_HUMAN   Same benchmark pool, score <= T_LOW=4.0, AND corpus co-occurrence count >= the 90th
                percentile of the FULL anchor-pair co-occurrence distribution (recomputed fresh,
                mirrors DSI.TOP_DECILE_Q=0.90 exactly). Replaces DSI's WordNet-relation exclusion
                step with the low-human-rating requirement -- that substitution is the entire point.
  MATCHING      `DSI.match_cells` reused VERBATIM (5-covariate per-dimension caliper), except POS
                stratification uses the BENCHMARK's own POS column (not `DSI.wn_dominant_pos`, which
                is WordNet-derived) -- keeps the human construction WordNet-free in the matching
                step too, not just the P/S label definition.

=================================================================================================
WORDNET-INDEPENDENCE AUDIT (mandatory, reported before any arm): fraction of the FINAL MATCHED
SET_P_HUMAN pairs that are ALSO a WordNet same-synset pair (contamination measure), and the looser
WordNet-"close" (path_sim >= 0.25) fraction, both computed off disk via `DSI`'s own WordNet helpers.

=================================================================================================
KNOWN-ANSWER ARM: the published human similarity score itself. Disclosed as MORE tautological than
the licensed instrument's WordNet-path-similarity known-answer (which read 0.9599, not exactly 1.0,
because path similarity is a DIFFERENT quantity from the WordNet-synset label): here the
known-answer score IS the literal quantity SET_P_HUMAN/SET_S_HUMAN were thresholded on, so AUC=1.0
EXACTLY by construction. Reported as a sanity check on the labelling/AUC machinery, never as
evidence about the store. See pre-reg for why a genuinely held-out annotator-split known-answer
(available for SimVerb only, not SimLex) was considered and rejected.

=================================================================================================
ARMS (7, re-scoring the SAME stores/constructions the licensed instrument's siblings already built,
on this NEW population):
  INCUMBENT_LIVE_STORE, RAW_COUNT_FULL_ACCUM, RAW_COUNT_SINGLE_OCC, PRESENCE_ABSENCE_BINARIZED,
  PARADIGMATIC_PROFILE_WRITE  -- byte-identical constructions to `DSI`'s own arms, restricted to
                                 `words_needed`, reused via `DSI`/`INFO`/`PIPE`/`WRP` verbatim.
  T0_VANILLA_PPMI_SVD          `CAP.ppmi_of` + SVD k=50 (the landed winning config,
                                T0_BEST_K="50" in data/exp_corpus_capacity_ppmi_svd_ceiling_v1).
  T2_SHIFTED_PPMI_K15          `TC.ppmi_tuned(alpha=1.0, k_shift=15, subsample_t=None)` + SVD k=50
                                p=0.5 (the landed winning config, T2_SHIFTED_PPMI.SELECTED_CONFIG in
                                data/exp_tuned_count_unsupervised_dissociation_v1).
For T0/T2 the co-occurrence matrix M is rebuilt over the FULL valid-anchor population exactly as the
landed cells built it (`CAP.build_matrix`), and a POSITIVE-CONTROL regression check re-scores the
SAME two configs on the ORIGINAL licensed (WordNet) population BEFORE trusting them on the human
population -- must reproduce 0.0519 (T0) / 0.1144 (T2) within the landed cells' own 0.0005
tolerance. This is SCHEMA-VET item 15.D (`reproduce_prior_chain_grade_result_as_positive_control`)
applied to a SAME-regime reconstruction (identical formula/config/seed over the identical matrix) --
exact reproduction is the expected result; a miss means a reconstruction bug, not that the primitive
fails to extend.

=================================================================================================
CODE_VERSION v2.0 AMENDMENT (2026-08-18, after v1.0's FULL run halted at matching with n=7/cell,
recorded in notes/human_judgement_instrument_power_failure_2026-08-18.md and plan sec 6.27/6.29).
Verified off disk (this cell's own prior checkpoint, data/exp_dissociation_score_instrument_human_v1/
units.jsonl, unit_key POPULATION_HUMAN|v1.0|full): the collapse to n=7 is NOT caused by any
restriction to the WordNet-licensed instrument's population -- combine_benchmark_pairs() below is
called with the FULL 5,491-anchor anchor_set both in v1.0 and here, unchanged, and the population
funnel (2,233 benchmark pairs -> 436 SET_P_HUMAN raw -> 122 SET_S_HUMAN raw) is IDENTICAL in this
version because that construction is untouched. The MEASURED cause, from the same checkpoint's
`matching.per_pos_stratum` and `matching.pre_match_smd`: `mean_log_freq` pre-match SMD=-1.8396
(SET_P_HUMAN pairs are structurally far rarer than SET_S_HUMAN pairs -- rare words are more likely
to be human-rated similar AND never co-occur; frequent words co-occur a lot), and the reused caliper
(mean_log_freq/abs_freq_diff capped at 0.02, i.e. |z-diff|<=0.14 SD, tightened specifically for the
WordNet-labelled population in exp_dissociation_score_instrument_v1's own 4-round matching repair)
caliper-drops 429 of 436 candidates (98.4%); by POS stratum, adjective (19P/3S) and noun (47P/27S)
strata drop to ZERO matches, verb (370P/92S) yields the 7 that survive. Per the standing rule (this
cell's own pre-reg and the dispatch brief): NEVER loosen the caliper to buy n -- a bigger sample of
an unlicensed instrument is worse than no sample. So v2.0 changes PROCESS, not the population or the
caliper: (a) the crash-with-no-metrics.json at n<20 (v1.0's `SystemExit`) is replaced with an
explicit `POWER_INSUFFICIENT` verdict WRITTEN to metrics.json with the full funnel, at a raised
threshold n<`POWER_INSUFFICIENT_MIN_N`=60 (per the dispatch brief: "if n per cell is still under ~60,
report POWER_INSUFFICIENT and stop -- do not proceed to arms"); (b) the LICENSE GATE (four floors +
known-answer + random-store, all CHEAP -- no matrix rebuild needed) is now built and checked BEFORE
any of the 7 expensive re-scored arms (INCUMBENT/RAW_COUNT/PARADIGMATIC/T0/T2), so an unlicensed
population never pays for a PPMI+SVD rebuild; (c) `max(four floors)` is computed explicitly and
reported as the REAL bar (not 0.5), per plan sec 6.29(1)'s correction that the WordNet instrument's
own recomputed max-floor read 0.5431, not 0.5 -- verified fresh off
`data/exp_dissociation_score_instrument_v1/metrics.json` at run time (never hardcoded).

=================================================================================================
STOP-IF (evaluated in this order):
  (0)   n_match < POWER_INSUFFICIENT_MIN_N (60) -> POWER_INSUFFICIENT, report the achieved n and the
        funnel, do NOT build or interpret any arm (including floors).
  (i)   any floor's 95% CI excludes 0.5 -> INSTRUMENT_LICENSED=False, publish no expensive-arm
        numbers (floor + known-answer + random-store numbers ARE written, for the record).
  (ii)  known-answer AUC < 0.999 -> label/score plumbing bug (it is tautological by design).
  (iii) achieved n / CI half-widths too wide to resolve the arm ordering -> POWER_INSUFFICIENT,
        report the achieved half-width, not a ranking.
  (iv)  the two instruments' arm orderings AGREE (rank correlation excludes 0, positive) -> plan
        6.23's conclusion is about OUR STORE and survives.
  (v)   the orderings DISAGREE -> 6.23 was substantially about WordNet; redirect the programme.
  (vi)  any arm reads CI-separated ABOVE the recomputed max(four floors) on the human instrument ->
        report loudly, every control, the coverage, the margin against BOTH max(four floors) and 0.5.

NOTE ON COMPARABILITY (stated once, applies whenever the licensed path is reached): this
instrument's population and the WordNet instrument's population are DIFFERENT, non-overlapping-by-
construction pools (different label source, different n, different difficulty) -- so absolute AUC
values are NEVER compared side by side across the two instruments. Only the ARM ORDERING (the rank
correlation below) is a valid cross-instrument comparison.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
#   (cheap-only digest set if unlicensed; all 13 if licensed -- both paths assert len(set)>1)
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: POPULATION_HUMAN, SCORES_CHEAP, SCORES_EXPENSIVE, POSITIVE_CONTROL as
#   separate tools.exp_checkpoint units (v2.0: SCORES_HUMAN split into CHEAP/EXPENSIVE so the
#   license gate can run, and be checked, BEFORE the expensive unit is ever built); MAIN wraps the
#   whole run() result
# - discriminator survives scale: n/a -- licensing-gate instrument re-score, not a mechanism sweep;
#   the real scale risk is COVERAGE, addressed by the explicit POWER_INSUFFICIENT stop-if (v2.0:
#   now a WRITTEN metrics.json branch, not a SystemExit with no output)
# - calibration_check: default_ok_for_this_regime (reuses landed, regression-gated caches unmodified)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - baseline_in_band: n/a -- licensing-gate instrument, same declaration as DSI
# - crlb_floor_computed: n/a -- AUC dissociation measurement, not a capacity sweep

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. No store is
rebuilt; data/foundation/** is never opened. v1's own output dir
(data/exp_dissociation_score_instrument_human_v1/) is READ-ONLY reference (its checkpoint diag was
read for the "CODE_VERSION v2.0 AMENDMENT" note above; never written to). This cell writes only
under data/exp_dissociation_score_instrument_human_v2[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy/scipy/nltk/DSI/CAP/TC next -- flushed so a slow import is never "
      "mistaken for a hang)", flush=True)

import argparse
import csv
import sys
import time
import traceback
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import spearmanr

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from nltk.corpus import wordnet as wn                                          # noqa: E402

import experiments.exp_dissociation_score_instrument_v1 as DSI                 # noqa: E402  READ ONLY
import experiments.exp_cue_to_store_translation_v1 as CTS                      # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                       # noqa: E402  READ ONLY
import experiments.exp_pipeline_stage_oracle_ladder_v1 as PIPE                 # noqa: E402  READ ONLY
import experiments.exp_readout_writerule_paradigmatic_v1 as WRP                # noqa: E402  READ ONLY
import experiments.exp_corpus_capacity_ppmi_svd_ceiling_v1 as CAP              # noqa: E402  READ ONLY
import experiments.exp_tuned_count_unsupervised_dissociation_v1 as TC          # noqa: E402  READ ONLY
from tools import floor_battery as FB                                          # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics         # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "dissociation_score_instrument_human_v2"  # DISTINCT from v1's anchor name/output dir
                       # (data/exp_dissociation_score_instrument_human_v2/) -- v1's own output dir
                       # and committed source are the permanent null record and are never touched or
                       # resumed-from by this file.
CODE_VERSION = "v2.0"  # v1.0's FULL run halted with SystemExit at n_match=7<20, no metrics.json
                       # written (notes/human_judgement_instrument_power_failure_2026-08-18.md).
                       # v2.0 changes PROCESS only (see module docstring "SUPERSEDES v1" +
                       # "CODE_VERSION v2.0 AMENDMENT" above): population/matching construction is
                       # BYTE-IDENTICAL to v1.0 (same combine_benchmark_pairs(anchor_set) call over
                       # the FULL 5,491 anchors, same caliper) -- carried into a fresh file+anchor
                       # name (not just a version bump) so v1's checkpoint/metrics/commit stay the
                       # permanent, reproducible record of the n=7 null.
FINDINGS = "notes/dissociation_score_instrument_human_v2_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = CTS.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
T_HIGH = 6.0
T_LOW = 4.0
TOP_DECILE_Q = 0.90
KNOWN_ANSWER_MIN_AUC = 0.999   # tautological by design; anything short of ~1.0 is a plumbing bug
POS_FIX = {"N": "n", "V": "v", "A": "a"}
SIMLEX_PATH = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simlex999.txt")
SIMVERB_PATH = os.path.join(REPO, "data", "encoder_eval_benchmarks", "simverb3500.txt")

# Landed WordNet-instrument AUCs for the SAME 7 arms, MEASURED@ the cited metrics.json paths --
# read fresh at run() time (never hardcoded into the interpretation), these module-level constants
# exist only as the DECLARED SOURCE for the self-test's "real code path" check.
DSI_METRICS_PATH = os.path.join(REPO, "data", "exp_dissociation_score_instrument_v1", "metrics.json")
CAP_METRICS_PATH = os.path.join(REPO, "data", "exp_corpus_capacity_ppmi_svd_ceiling_v1", "metrics.json")
TC_METRICS_PATH = os.path.join(REPO, "data", "exp_tuned_count_unsupervised_dissociation_v1",
                               "metrics.json")

SEVEN_ARMS = ["INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM", "RAW_COUNT_SINGLE_OCC",
             "PRESENCE_ABSENCE_BINARIZED", "PARADIGMATIC_PROFILE_WRITE",
             "T0_VANILLA_PPMI_SVD", "T2_SHIFTED_PPMI_K15"]

# v2.0: population-size stop-if, and the CHEAP/EXPENSIVE arm partition that makes "license gate
# BEFORE any arm" possible (dispatch brief, "LICENCE GATE FIRST, before any arm"). CHEAP arms need
# only the already-cached mat/t_mat/proto/freq (milliseconds); EXPENSIVE arms need a fresh M-matrix
# build + 2 SVDs (the only genuinely slow part of this cell) and are built ONLY if the license gate
# (floors at chance + known-answer near-1) passes on the CHEAP arms.
POWER_INSUFFICIENT_MIN_N = 60  # dispatch brief: "if n per cell is still under ~60, report
                               # POWER_INSUFFICIENT and stop -- do not proceed to arms"
FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
CHEAP_ARM_NAMES = FLOOR_NAMES + ["KNOWN_ANSWER_HUMAN_RATING", "RANDOM_VECTOR_STORE"]
EXPENSIVE_ARM_NAMES = list(SEVEN_ARMS)
assert not (set(CHEAP_ARM_NAMES) & set(EXPENSIVE_ARM_NAMES)), "CHEAP/EXPENSIVE arm names must not overlap"


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


# =================================================================================================
# BENCHMARK LOADERS
# =================================================================================================
def load_simlex(path: str) -> List[Tuple[str, str, str, float]]:
    """(w1, w2, pos, score) -- HAS a header line (skipped)."""
    out: List[Tuple[str, str, str, float]] = []
    with open(path, encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        next(r)  # header
        for row in r:
            w1, w2, pos, score = row[0].lower(), row[1].lower(), row[2], float(row[3])
            out.append((w1, w2, POS_FIX.get(pos, pos.lower()), score))
    return out


def load_simverb(path: str) -> List[Tuple[str, str, str, float]]:
    """(w1, w2, pos, score) -- NO header line. Columns: word1 word2 POS score relation."""
    out: List[Tuple[str, str, str, float]] = []
    with open(path, encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t")
        for row in r:
            w1, w2, pos, score = row[0].lower(), row[1].lower(), row[2], float(row[3])
            out.append((w1, w2, POS_FIX.get(pos, pos.lower()), score))
    return out


def combine_benchmark_pairs(anchor_set: Sequence[str], simlex_rows=None, simverb_rows=None
                            ) -> Dict[Tuple[str, str], Tuple[str, str, str, float]]:
    """Combine SimLex + SimVerb, SimLex takes precedence on a duplicate unordered pair, restricted
    to pairs where BOTH members are valid corpus anchors and w1 != w2. Returns
    {sorted_pair_key: (w1, w2, pos, score)}."""
    aset = set(anchor_set)
    simlex_rows = load_simlex(SIMLEX_PATH) if simlex_rows is None else simlex_rows
    simverb_rows = load_simverb(SIMVERB_PATH) if simverb_rows is None else simverb_rows
    by_key: Dict[Tuple[str, str], Tuple[str, str, str, float]] = {}
    for w1, w2, pos, score in simlex_rows + simverb_rows:
        key = tuple(sorted((w1, w2)))
        if key not in by_key:
            by_key[key] = (w1, w2, pos, score)
    return {k: v for k, v in by_key.items()
           if v[0] in aset and v[1] in aset and v[0] != v[1]}


# =================================================================================================
# SET_P_HUMAN / SET_S_HUMAN CANDIDATE CONSTRUCTION
# =================================================================================================
def build_setP_human(bench: Dict[Tuple[str, str], Tuple[str, str, str, float]], pair_counts,
                     t_high: float) -> List[Tuple[str, str, str]]:
    out = []
    for (w1, w2, pos, score) in bench.values():
        if score >= t_high and pair_counts.get((w1, w2), pair_counts.get((w2, w1), 0)) == 0:
            out.append((w1, w2, pos))
    return sorted(out)


def build_setS_human(bench: Dict[Tuple[str, str], Tuple[str, str, str, float]], pair_counts,
                     t_low: float, decile_thresh: float) -> List[Tuple[str, str, str]]:
    out = []
    for (w1, w2, pos, score) in bench.values():
        c = pair_counts.get((w1, w2), pair_counts.get((w2, w1), 0))
        if score <= t_low and c >= decile_thresh:
            out.append((w1, w2, pos))
    return sorted(out)


def wn_overlap_stats(pairs: List[Tuple[str, str, str]]) -> Dict:
    """Fraction of `pairs` that are ALSO a WordNet same-synset pair, and the looser
    path_sim>=WN_CLOSE_THRESHOLD fraction. The direct WordNet-independence contamination measure."""
    if not pairs:
        return {"n": 0, "n_exact_synonym": 0, "n_close": 0, "frac_exact_synonym": None,
               "frac_close": None}
    n_exact = n_close = 0
    for w1, w2, _p in pairs:
        syns1 = wn.synsets(w1)[:DSI.SYNSET_CAP]
        names1 = set()
        for s in syns1:
            names1 |= set(l.replace("_", " ") for l in s.lemma_names())
        if w2 in names1:
            n_exact += 1
        if DSI.wn_best_path_similarity(w1, w2) >= DSI.WN_CLOSE_THRESHOLD:
            n_close += 1
    return {"n": len(pairs), "n_exact_synonym": n_exact, "n_close": n_close,
           "frac_exact_synonym": round(n_exact / len(pairs), 4),
           "frac_close": round(n_close / len(pairs), 4)}


# =================================================================================================
# self-test -- exercises the REAL loader/construction functions above on tiny real+synthetic
# fixtures (META_RULE F.1), plus reuses DSI's own self-test wholesale to prove every REUSED
# entrypoint (match_cells, auc_of, auc_bootstrap, checkpoint) still self-validates.
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- real WordNet path: reuse DSI's own self-test wholesale (proves every reused entrypoint) --
    ev["DSI_selftest"] = DSI.self_test()

    # --- benchmark loaders on tiny REAL-format synthetic files (real code path: csv.reader, real
    # column layout, real header-skip behaviour) --------------------------------------------------
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        simlex_fixture = os.path.join(td, "simlex_fixture.txt")
        with open(simlex_fixture, "w", encoding="utf-8") as f:
            f.write("word1\tword2\tPOS\tSimLex999\tconc(w1)\tconc(w2)\tconcQ\tAssoc(USF)\t"
                   "SimAssoc333\tSD(SimLex)\n")
            f.write("smart\tintelligent\tA\t9.2\t1.75\t2.46\t1\t7.11\t1\t0.67\n")
            f.write("old\tnew\tA\t1.58\t2.72\t2.81\t2\t7.25\t1\t0.41\n")
        simverb_fixture = os.path.join(td, "simverb_fixture.txt")
        with open(simverb_fixture, "w", encoding="utf-8") as f:
            f.write("take\tremove\tV\t6.81\tSYNONYMS\n")
            f.write("feed\tstarve\tV\t1.49\tANTONYMS\n")
        rows_sl = load_simlex(simlex_fixture)
        rows_sv = load_simverb(simverb_fixture)
        assert rows_sl == [("smart", "intelligent", "a", 9.2), ("old", "new", "a", 1.58)], rows_sl
        assert rows_sv == [("take", "remove", "v", 6.81), ("feed", "starve", "v", 1.49)], rows_sv
        ev["benchmark_loaders_real_code_path"] = {"simlex": rows_sl, "simverb": rows_sv}

        # combine_benchmark_pairs: SimLex precedence on duplicate pair, anchor restriction ---------
        rows_sl2 = rows_sl + [("dup", "pair", "n", 5.0)]
        rows_sv2 = rows_sv + [("dup", "pair", "n", 0.5)]  # same pair, different score -> SimLex wins
        anchor_set = {"smart", "intelligent", "old", "new", "take", "remove", "dup", "pair"}
        bench = combine_benchmark_pairs(anchor_set, simlex_rows=rows_sl2, simverb_rows=rows_sv2)
        key = tuple(sorted(("dup", "pair")))
        assert bench[key][3] == 5.0, "SimLex must take precedence on a duplicate pair: %r" % (bench[key],)
        # feed/starve excluded: 'starve' not in this tiny anchor_set
        assert tuple(sorted(("feed", "starve"))) not in bench, \
            "pair with a member outside the anchor set must be excluded: %r" % bench
        ev["combine_benchmark_pairs_precedence_and_anchor_restriction"] = {
            "dup_pair_score": bench[key][3], "n_combined": len(bench)}

    # --- build_setP_human / build_setS_human filtering logic on synthetic co-occurrence counts ----
    bench2 = {("a", "b"): ("a", "b", "n", 8.0),   # high score, zero cooc -> SET_P candidate
             ("c", "d"): ("c", "d", "n", 8.0),    # high score, NONZERO cooc -> excluded from SET_P
             ("e", "f"): ("e", "f", "n", 1.0),    # low score, high cooc -> SET_S candidate
             ("g", "h"): ("g", "h", "n", 1.0)}    # low score, cooc BELOW decile -> excluded from SET_S
    pair_counts_fake = {("c", "d"): 3, ("e", "f"): 10, ("g", "h"): 1}
    setP = build_setP_human(bench2, pair_counts_fake, t_high=6.0)
    setS = build_setS_human(bench2, pair_counts_fake, t_low=4.0, decile_thresh=5)
    assert setP == [("a", "b", "n")], "only the zero-cooc high-score pair belongs in SET_P: %r" % setP
    assert setS == [("e", "f", "n")], "only the >=decile-thresh low-score pair belongs in SET_S: %r" % setS
    ev["setP_setS_construction_known_answer"] = {"setP": setP, "setS": setS}

    # --- wn_overlap_stats: car/auto (exact synonym) vs car/pepper (unrelated) on REAL WordNet -----
    stats_syn = wn_overlap_stats([("car", "auto", "n")])
    stats_unrel = wn_overlap_stats([("car", "pepper", "n")])
    assert stats_syn["n_exact_synonym"] == 1, "car/auto must be flagged an exact WordNet synonym: %r" % stats_syn
    assert stats_unrel["n_exact_synonym"] == 0 and stats_unrel["n_close"] == 0, \
        "car/pepper must NOT be flagged WordNet-related: %r" % stats_unrel
    ev["wn_overlap_stats_known_answer"] = {"synonym_pair": stats_syn, "unrelated_pair": stats_unrel}

    # --- CAP/TC entrypoints bind against their LIVE signature (F.2, cheap, no object built) -------
    import inspect
    sig_checks = []
    for callable_obj, kwargs in [
        (CAP.build_matrix, {"anchor_words": []}),
        (CAP.ppmi_of, {"M": None}),
        (TC.ppmi_tuned, {"M": None, "alpha": 1.0, "k_shift": 1.0, "subsample_t": None}),
        (TC.svd_vectors_p, {"Mppmi": None, "k": 1, "p": 0.5, "svd_seed": 0}),
        (TC._seed_for, {"tag": "x"}),
        (CAP.pair_cosine_from_dense_rows, {"rows": None, "row_idx": {}, "pairs": []}),
        (TC.score_pairs, {"vecs": None, "row_idx": {}, "pairsP": [], "pairsS": [], "boot_seed": 0}),
        (CAP.regression_gate, {}),
    ]:
        sig = inspect.signature(callable_obj)
        for k in kwargs:
            assert k in sig.parameters, "%s missing expected kwarg %r (signature drift): %r" % (
                callable_obj.__name__, k, sig)
        sig_checks.append(callable_obj.__name__)
    ev["substrate_signature_checks_passed"] = sig_checks

    # --- v2.0: CHEAP/EXPENSIVE arm partition is exhaustive and disjoint over the 13 total arms ------
    all_13 = set(CHEAP_ARM_NAMES) | set(EXPENSIVE_ARM_NAMES)
    assert set(EXPENSIVE_ARM_NAMES) == set(SEVEN_ARMS), \
        "EXPENSIVE_ARM_NAMES must be exactly the 7 arms compared against the WordNet instrument"
    assert len(all_13) == len(CHEAP_ARM_NAMES) + len(EXPENSIVE_ARM_NAMES) == 13, \
        "CHEAP + EXPENSIVE arm partition must be disjoint and total 13: %r" % all_13
    assert set(FLOOR_NAMES) <= set(CHEAP_ARM_NAMES), "all 4 floors must be CHEAP (license-gate-first)"
    ev["arm_partition_known_answer"] = {"cheap": CHEAP_ARM_NAMES, "expensive": EXPENSIVE_ARM_NAMES}

    # --- v2.0: POWER_INSUFFICIENT_MIN_N threshold is a real gate, not decorative -------------------
    assert POWER_INSUFFICIENT_MIN_N == 60, \
        "dispatch brief pins the threshold at ~60: %r" % POWER_INSUFFICIENT_MIN_N
    assert 7 < POWER_INSUFFICIENT_MIN_N, \
        "v1's own measured collapse (n=7) must fall BELOW the threshold, or this gate is vacuous"
    ev["power_insufficient_threshold_known_answer"] = {
        "POWER_INSUFFICIENT_MIN_N": POWER_INSUFFICIENT_MIN_N,
        "v1_measured_n_match": 7, "v1_would_stop_here": bool(7 < POWER_INSUFFICIENT_MIN_N)}

    # --- v2.0: max(four floors) margin arithmetic, on synthetic AUC results (real function, no I/O) -
    fake_auc = {"F_ORTHOGRAPHIC": {"auc": 0.51}, "F_FREQUENCY": {"auc": 0.49},
               "F_SCRAMBLE": {"auc": 0.47}, "F_CONSTANT_PROTOTYPE": {"auc": 0.54}}
    max_floor_fake = round(max(fake_auc[f]["auc"] for f in FLOOR_NAMES), 4)
    assert max_floor_fake == 0.54, "max(four floors) must pick the largest floor point-AUC: %r" % max_floor_fake
    arm_auc_fake = 0.60
    margin_vs_max_floor = round(arm_auc_fake - max_floor_fake, 4)
    margin_vs_half = round(arm_auc_fake - 0.5, 4)
    assert abs(margin_vs_max_floor - 0.06) < 1e-9 and abs(margin_vs_half - 0.10) < 1e-9, \
        "the two margins must differ when max_floor != 0.5: %r %r" % (margin_vs_max_floor, margin_vs_half)
    ev["max_floor_margin_known_answer"] = {"max_floor_fake": max_floor_fake,
                                           "margin_vs_max_floor": margin_vs_max_floor,
                                           "margin_vs_0.5": margin_vs_half}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))

    C = CTS.load_cache()
    aux = CTS.load_aux()
    anchors: List[str] = C["anchors"]
    mat_ok = np.asarray(C["mat_ok"], dtype=bool)
    mat = np.asarray(C["mat"], dtype=np.float32)
    n_anchors = len(anchors)
    anchor_set = set(a for a, ok in zip(anchors, mat_ok) if ok)
    fq_log = {a: float(v) for a, v, ok in zip(anchors, aux["fq"], mat_ok) if ok}
    t_mat = np.asarray(aux["t_mat"], dtype=np.float32)
    pos_idx: Dict[str, int] = C["pos"]
    print("[load] n_anchors=%d n_valid=%d t=%.1fs" % (n_anchors, len(anchor_set), time.time() - t0),
         flush=True)

    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                "T_HIGH": T_HIGH, "T_LOW": T_LOW}

    rep["REGRESSION_GATE"] = {"n_anchors": n_anchors, "mat_shape": list(mat.shape),
                              "PASS": bool(n_anchors == mat.shape[0] == t_mat.shape[0])}
    if not rep["REGRESSION_GATE"]["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- cache shapes disagree: %r" % rep["REGRESSION_GATE"])

    # =============================== POPULATION_HUMAN (checkpointed unit) ============================
    pop_key = unit_key("POPULATION_HUMAN", CODE_VERSION, grid)
    prior_pop = load_units(out_dir_ckpt).get(pop_key)
    if prior_pop is not None:
        print("[population] RESUMED FROM CHECKPOINT", flush=True)
        matchedP = [tuple(x) for x in prior_pop["matchedP"]]
        matchedS = [tuple(x) for x in prior_pop["matchedS"]]
        pop_diag = prior_pop["diag"]
        pair_score_of = {tuple(k.split("|")): v for k, v in prior_pop["pair_score_of"].items()}
    else:
        bench = combine_benchmark_pairs(anchor_set)
        pair_score_of = {k: v[3] for k, v in bench.items()}
        print("[population] combined benchmark pairs restricted to anchor set: %d" % len(bench),
             flush=True)

        sents, buckets, counts, corpus_prov = INFO.load_corpus_and_buckets()
        rep["corpus_provenance"] = corpus_prov
        pair_counts = DSI.build_cooccurrence_paircounts(sents, anchor_set)
        vals = np.array([c for c in pair_counts.values()], dtype=np.float64)
        decile_thresh = float(np.percentile(vals, TOP_DECILE_Q * 100)) if vals.size else 0.0
        print("[population] decile90_threshold=%.2f (over %d distinct cooccurring anchor pairs)" %
             (decile_thresh, len(pair_counts)), flush=True)

        cellP_raw = build_setP_human(bench, pair_counts, T_HIGH)
        cellS_raw = build_setS_human(bench, pair_counts, T_LOW, decile_thresh)
        print("[population] SET_P_HUMAN raw candidates (zero-cooc, score>=%.1f): %d" %
             (T_HIGH, len(cellP_raw)), flush=True)
        print("[population] SET_S_HUMAN raw candidates (>=decile90 cooc, score<=%.1f): %d" %
             (T_LOW, len(cellS_raw)), flush=True)

        wn_audit_raw = wn_overlap_stats(cellP_raw)
        rep["WORDNET_INDEPENDENCE_AUDIT_RAW_CANDIDATES"] = wn_audit_raw

        if grid == "reduced":
            cellP_raw = cellP_raw[:120]
            cellS_raw = cellS_raw[:120]

        tri_all = l2n(t_mat)
        proto_all = FB.constant_prototype_floor(mat, mat_ok)
        cand_words = set(w for w1, w2, _p in cellP_raw + cellS_raw for w in (w1, w2))
        tri_of = {w: tri_all[pos_idx[w]] for w in cand_words if w in pos_idx}
        proto_of = {w: float(proto_all[pos_idx[w]]) for w in cand_words if w in pos_idx}
        matchedP, matchedS, match_diag = DSI.match_cells(
            cellP_raw, cellS_raw, fq_log, seed=MASTER_SEED + 7011, tri_of=tri_of, proto_of=proto_of)
        print("[population] MATCHED n_P=%d n_S=%d" % (len(matchedP), len(matchedS)), flush=True)

        wn_audit_matched = wn_overlap_stats(matchedP)
        rep["WORDNET_INDEPENDENCE_AUDIT_MATCHED_SET_P"] = wn_audit_matched

        pop_diag = {"n_combined_benchmark_pairs_anchor_restricted": len(bench),
                   "decile90_threshold": decile_thresh,
                   "n_distinct_cooccurring_anchor_pairs": len(pair_counts),
                   "n_setP_raw": len(cellP_raw), "n_setS_raw": len(cellS_raw),
                   "matching": match_diag,
                   "wordnet_independence_audit_raw": wn_audit_raw,
                   "wordnet_independence_audit_matched": wn_audit_matched}
        record_unit(out_dir_ckpt, pop_key,
                   {"matchedP": matchedP, "matchedS": matchedS, "diag": pop_diag,
                    "pair_score_of": {"|".join(k): v for k, v in pair_score_of.items()}})

    rep["POPULATION"] = pop_diag
    n_match = len(matchedP)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_match
    # re-surface the WN audit at top level too (post-checkpoint-resume path needs it explicitly)
    rep.setdefault("WORDNET_INDEPENDENCE_AUDIT_MATCHED_SET_P", pop_diag.get("wordnet_independence_audit_matched"))

    # =============================== STOP-IF (0): POPULATION UNDERPOWERED ============================
    # v2.0: WRITE an honest POWER_INSUFFICIENT metrics.json here instead of v1.0's SystemExit-with-no-
    # metrics-file. Per the dispatch brief: "if n per cell is still under ~60, report
    # POWER_INSUFFICIENT and stop -- do not proceed to arms." No floor, known-answer, or store arm is
    # built or scored past this point -- an AUC/CI at n<60 (let alone n=7) is not a meaningful
    # measurement of anything, including the floors themselves.
    if n_match < POWER_INSUFFICIENT_MIN_N:
        print("[STOP-IF-0] n_match=%d < POWER_INSUFFICIENT_MIN_N=%d -- stopping before any arm is "
             "built" % (n_match, POWER_INSUFFICIENT_MIN_N), flush=True)
        rep["LICENSING"] = {"SKIPPED": True, "INSTRUMENT_LICENSED": False,
                            "reason": "population n_match=%d < POWER_INSUFFICIENT_MIN_N=%d; per "
                                     "pre-reg STOP-IF (0), no floor is scored at this n" %
                                     (n_match, POWER_INSUFFICIENT_MIN_N)}
        rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match,
                              "POWER_INSUFFICIENT_MIN_N": POWER_INSUFFICIENT_MIN_N,
                              "POWER_INSUFFICIENT": True,
                              "reason": "matched population below the pre-registered minimum n; no "
                                       "arm (including floors) is scored"}
        rep["AUC_PER_ARM"] = {}
        rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = {}
        rep["arms_differ_exempted"] = ["ALL_ARMS: population POWER_INSUFFICIENT at n=%d (<%d), no "
                                       "arm was scored, so the arms-must-differ hash-test does not "
                                       "apply (there is nothing to hash)" %
                                       (n_match, POWER_INSUFFICIENT_MIN_N)]
        rep["RANK_CORRELATION"] = {"SKIPPED": "no arms scored on this population"}
        # Context only, never interpreted as a finding on THIS population: the WordNet-licensed
        # instrument's own recomputed max(four floors) bar, read fresh (never hardcoded) so a
        # reader of this metrics.json knows what any FUTURE licensed run here would need to clear.
        try:
            import json as _json
            with open(DSI_METRICS_PATH, encoding="utf-8") as f:
                _dsi = _json.load(f)
            _dsi_floor_aucs = {k: _dsi["report"]["AUC_PER_ARM"][k]["auc"] for k in FLOOR_NAMES}
            rep["WORDNET_INSTRUMENT_CONTEXT_MAX_FLOOR_AUC"] = {
                "source": DSI_METRICS_PATH, "per_floor_auc": _dsi_floor_aucs,
                "max_floor_auc": round(max(_dsi_floor_aucs.values()), 4),
                "note": "the bar for ANY future arm on a licensed run is max(four floors), NOT 0.5 "
                        "-- this is the WordNet instrument's OWN recomputed value, cited for context "
                        "only; this cell's own floors were never scored (population underpowered)"}
        except Exception as e:  # non-fatal side-channel, never blocks the POWER_INSUFFICIENT report
            rep["WORDNET_INSTRUMENT_CONTEXT_MAX_FLOOR_AUC"] = {"ERROR": "%s: %s" % (
                type(e).__name__, str(e)[:300])}
        rep["INTERPRETATION"] = ("POWER_INSUFFICIENT__n_match=%d__min_required=%d__"
                                 "STOPPED_BEFORE_ANY_ARM" % (n_match, POWER_INSUFFICIENT_MIN_N))
        rep["elapsed_s"] = round(time.time() - t0, 1)
        return rep

    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    print("[scores] %d distinct words needed across both matched cells" % len(words_needed), flush=True)

    def score_of_pair(pairs: List[Tuple[str, str, str]]) -> np.ndarray:
        out = np.zeros(len(pairs), dtype=np.float64)
        for i, (w1, w2, _p) in enumerate(pairs):
            out[i] = pair_score_of.get(tuple(sorted((w1, w2))), np.nan)
        return out

    def pair_dense(store: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        return (DSI.dense_scores_from_dict_store(store, matchedP),
                DSI.dense_scores_from_dict_store(store, matchedS))

    def pair_scalar_mean(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        fp = lambda pairs: np.array([0.5 * (scalar_of.get(w1, 0.0) + scalar_of.get(w2, 0.0))
                                    for w1, w2, _p in pairs])
        return fp(matchedP), fp(matchedS)

    def pair_scalar_max(scalar_of: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
        fp = lambda pairs: np.array([max(scalar_of.get(w1, 0.0), scalar_of.get(w2, 0.0))
                                    for w1, w2, _p in pairs])
        return fp(matchedP), fp(matchedS)

    wid = {w: pos_idx[w] for w in words_needed}

    # =============================== SCORES_CHEAP (checkpointed unit) -- LICENSE GATE FIRST ===========
    # v2.0: the 4 floors + known-answer + random-store need only the ALREADY-CACHED mat/t_mat/proto/
    # freq (milliseconds) -- built and AUC-scored BEFORE any of the 7 expensive re-scored arms, so an
    # unlicensed population never pays for the M-matrix rebuild + 2 SVDs below (dispatch brief:
    # "LICENCE GATE FIRST, before any arm").
    cheap_key = unit_key("SCORES_CHEAP", CODE_VERSION, grid)
    prior_cheap = load_units(out_dir_ckpt).get(cheap_key)
    if prior_cheap is not None:
        print("[scores-cheap] RESUMED FROM CHECKPOINT", flush=True)
        cheap_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_cheap.items()}
    else:
        Tn = l2n(t_mat)
        store_ortho = {w: Tn[wid[w]] for w in words_needed}
        proto = FB.constant_prototype_floor(mat, mat_ok)
        proto_of_words = {w: float(proto[wid[w]]) for w in words_needed}
        freq_of_words = {w: fq_log.get(w, 0.0) for w in words_needed}
        scrambled = l2n(FB.scramble_null(mat, MASTER_SEED + 4433))
        store_scramble = {w: scrambled[wid[w]] for w in words_needed}
        rng_rand = np.random.default_rng(MASTER_SEED + 9091)
        rand_full = l2n(rng_rand.standard_normal((n_anchors, mat.shape[1])).astype(np.float32))
        store_random = {w: rand_full[wid[w]] for w in words_needed}

        cheap_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "F_ORTHOGRAPHIC": pair_dense(store_ortho),
            "F_FREQUENCY": pair_scalar_max(freq_of_words),
            "F_SCRAMBLE": pair_dense(store_scramble),
            "F_CONSTANT_PROTOTYPE": pair_scalar_mean(proto_of_words),
            "KNOWN_ANSWER_HUMAN_RATING": (score_of_pair(matchedP), score_of_pair(matchedS)),
            "RANDOM_VECTOR_STORE": pair_dense(store_random),
        }
        cheap_scores = {k: {"P": v[0], "S": v[1]} for k, v in cheap_raw.items()}
        record_unit(out_dir_ckpt, cheap_key,
                   {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in cheap_scores.items()})
    print("[scores-cheap] 4 floors + known-answer + random-store built", flush=True)

    boot_seed_base = MASTER_SEED + 8383
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(cheap_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + i)
        auc_results[name] = res
        print("[auc] %-30s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)

    # =============================== LICENSING (STOP-IF i, ii) -- gate BEFORE expensive arms ==========
    floor_licensing_ok = all(auc_results[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in FLOOR_NAMES)
    floor_failures = [f for f in FLOOR_NAMES if auc_results[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    known_answer_auc = auc_results["KNOWN_ANSWER_HUMAN_RATING"]["auc"]
    known_answer_ok = known_answer_auc >= KNOWN_ANSWER_MIN_AUC
    random_store_ok = auc_results["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    instrument_licensed = bool(floor_licensing_ok and known_answer_ok)
    max_floor_auc_this_population = round(max(auc_results[f]["auc"] for f in FLOOR_NAMES), 4)
    rep["LICENSING"] = {
        "STOP_IF_i_floors_at_chance": {"PASS": floor_licensing_ok, "floor_failures": floor_failures},
        "STOP_IF_ii_known_answer_near_1": {"PASS": known_answer_ok, "measured_auc": known_answer_auc,
                                          "gate": KNOWN_ANSWER_MIN_AUC},
        "random_vector_store_at_chance": {"PASS": random_store_ok},
        "INSTRUMENT_LICENSED": instrument_licensed,
        "max_floor_auc_this_population": max_floor_auc_this_population,
        "BAR_NOTE": "the bar for any arm reading 'above chance' is max(four floors)=%.4f on THIS "
                   "population, NOT 0.5 -- report margins against both, separately, per plan sec "
                   "6.29(1)'s correction" % max_floor_auc_this_population,
    }
    rep["AUC_PER_ARM"] = dict(auc_results)  # cheap arms only so far; expensive merged in below if licensed
    if not instrument_licensed:
        print("[LICENSING] INSTRUMENT UNLICENSED -- floor/known-answer/random-store numbers are "
             "WRITTEN above for the record but MUST NOT be interpreted as a finding. No expensive "
             "arm is built (INCUMBENT/RAW_COUNT/PARADIGMATIC/T0/T2 all skipped). floor_failures=%r "
             "known_answer=%.4f" % (floor_failures, known_answer_auc), flush=True)
        rep["EXPENSIVE_ARMS_SKIPPED"] = ("instrument not licensed on this population -- per pre-reg "
                                         "STOP-IF (i)/(ii), no expensive arm is built or interpreted")
        rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = {k: DSI._digest(np.concatenate([v["P"], v["S"]]))
                                               for k, v in cheap_scores.items()}
        assert len(set(rep["ARM_DIGESTS_ARMS_MUST_DIFFER"].values())) > 1, \
            "all cheap arms produced IDENTICAL score vectors -- construction bug"
        rep["RANK_CORRELATION"] = {"SKIPPED": "instrument not licensed; no expensive arms scored"}
        rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match, "SKIPPED": "instrument not licensed"}
        rep["INTERPRETATION"] = "INSTRUMENT_UNLICENSED_NO_INTERPRETATION_PERMITTED"
        rep["elapsed_s"] = round(time.time() - t0, 1)
        return rep

    # =============================== SCORES_EXPENSIVE (checkpointed unit) -- ONLY IF LICENSED =========
    scores_key = unit_key("SCORES_EXPENSIVE", CODE_VERSION, grid)
    prior_scores = load_units(out_dir_ckpt).get(scores_key)
    if prior_scores is not None:
        print("[scores-expensive] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_scores.items()}
    else:
        Mn_incumbent = l2n(mat)
        t0s = time.time()

        store_incumbent = {w: Mn_incumbent[wid[w]] for w in words_needed}

        units_info = load_units(os.path.join(REPO, "data", "exp_cue_information_audit_v1"))
        counts_full: Dict[str, "collections.Counter"] = {}
        missing_p = []
        for w in words_needed:
            rec = units_info.get(unit_key("Pstore", w))
            if rec is None:
                missing_p.append(w)
                continue
            from collections import Counter
            counts_full[w] = Counter(rec["counts"])
        if missing_p:
            raise SystemExit("CHECKPOINT REUSE INCOMPLETE -- exp_cue_information_audit_v1's own "
                             "units.jsonl is missing Pstore for: %r" % missing_p[:20])
        store_raw_full = DSI.counts_to_dense_store(counts_full, words_needed, binarize=False)
        store_binarized = DSI.counts_to_dense_store(counts_full, words_needed, binarize=True)

        sents, buckets, counts, _prov = INFO.load_corpus_and_buckets()
        P_single, single_diag = PIPE.build_single_occurrence_counts(words_needed, buckets, sents)
        rep["single_occurrence_build_diag"] = single_diag
        store_single = DSI.counts_to_dense_store(P_single, words_needed, binarize=False)

        mat0n = WRP.l2n_rows64(mat)
        d_dim = mat.shape[1]
        cw_cache: Dict[int, List[str]] = {}
        t_w1 = time.time()
        mat_w1, _part = WRP.build_arm(words_needed, buckets, cw_cache, sents, mat0n, pos_idx,
                                      d_dim, "PROFILE")
        print("[scores] PARADIGMATIC_PROFILE_WRITE built for %d words in %.1fs" % (
            len(words_needed), time.time() - t_w1), flush=True)
        w1n = l2n(mat_w1)
        store_paradigmatic = {w: w1n[i] for i, w in enumerate(words_needed)}

        # ---- T0 / T2: rebuild M over the FULL valid-anchor population, exactly as the landed
        # cells built it. In reduced grid, mirror TC's own reduced-grid convention (restrict to a
        # slice of anchors unioned with the words this arm actually needs) so smoke stays fast.
        anchor_words_full = sorted(anchor_set)
        if grid == "reduced":
            anchor_words_full = sorted(set(anchor_words_full[:1200]) | set(words_needed))
        t0m = time.time()
        M, row_idx, matrix_diag = CAP.build_matrix(anchor_words_full)
        rep["MATRIX"] = matrix_diag
        print("[scores] M built shape=%r t=%.1fs" % (M.shape, time.time() - t0m), flush=True)

        Mppmi_vanilla = CAP.ppmi_of(M)
        vecs_t0 = TC.svd_vectors_p(Mppmi_vanilla, 50, 0.5, MASTER_SEED + 7000 + 50)
        Mppmi_t2 = TC.ppmi_tuned(M, alpha=1.0, k_shift=15, subsample_t=None)
        vecs_t2 = TC.svd_vectors_p(Mppmi_t2, 50, 0.5, TC._seed_for("T2:ks15_k50:svd"))
        if vecs_t0 is None or vecs_t2 is None:
            raise SystemExit("SVD_RANK_CEILING -- k=50 exceeded the matrix's rank ceiling "
                             "(shape=%r); cannot build T0/T2 arms." % (M.shape,))
        store_t0 = {w: vecs_t0[row_idx[w]] for w in words_needed if w in row_idx}
        store_t2 = {w: vecs_t2[row_idx[w]] for w in words_needed if w in row_idx}

        # ---- POSITIVE_CONTROL (checkpointed unit): reproduce T0=0.0519 / T2=0.1144 on the
        # ORIGINAL WordNet population, using the landed cells' OWN exact seed conventions ---------
        pc_key = unit_key("POSITIVE_CONTROL", CODE_VERSION, grid)
        prior_pc = load_units(out_dir_ckpt).get(pc_key)
        if prior_pc is not None:
            print("[positive_control] RESUMED FROM CHECKPOINT", flush=True)
            pos_control = prior_pc
        else:
            gate = CAP.regression_gate()
            origP, origS = gate["matchedP"], gate["matchedS"]
            t0_orig = TC.score_pairs(vecs_t0, row_idx, origP, origS, MASTER_SEED + 9300 + 50)
            t2_orig = TC.score_pairs(vecs_t2, row_idx, origP, origS, TC._seed_for("T2:ks15_k50:ev"))
            t0_delta = round(t0_orig["auc"] - 0.0519, 6)
            t2_delta = round(t2_orig["auc"] - 0.1144, 6)
            pos_control = {
                "T0_orig_population_auc": t0_orig, "T0_expected": 0.0519, "T0_delta": t0_delta,
                "T0_PASS": bool(abs(t0_delta) <= 0.0005),
                "T2_orig_population_auc": t2_orig, "T2_expected": 0.1144, "T2_delta": t2_delta,
                "T2_PASS": bool(abs(t2_delta) <= 0.0005),
            }
            record_unit(out_dir_ckpt, pc_key, pos_control)
        rep["POSITIVE_CONTROL"] = pos_control
        if grid == "full" and not (pos_control["T0_PASS"] and pos_control["T2_PASS"]):
            raise SystemExit("POSITIVE_CONTROL_FAILED -- T0/T2 reconstruction does not reproduce "
                             "the landed cells' own numbers on the ORIGINAL population: %r" %
                             pos_control)

        print("[scores] all expensive arms built, elapsed=%.1fs" % (time.time() - t0s), flush=True)

        arm_scores_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "INCUMBENT_LIVE_STORE": pair_dense(store_incumbent),
            "RAW_COUNT_FULL_ACCUM": pair_dense(store_raw_full),
            "RAW_COUNT_SINGLE_OCC": pair_dense(store_single),
            "PRESENCE_ABSENCE_BINARIZED": pair_dense(store_binarized),
            "PARADIGMATIC_PROFILE_WRITE": pair_dense(store_paradigmatic),
            "T0_VANILLA_PPMI_SVD": pair_dense(store_t0),
            "T2_SHIFTED_PPMI_K15": pair_dense(store_t2),
        }
        arm_scores = {k: {"P": v[0], "S": v[1]} for k, v in arm_scores_raw.items()}
        record_unit(out_dir_ckpt, scores_key,
                   {k: {"P": v["P"].tolist(), "S": v["S"].tolist()} for k, v in arm_scores.items()})
        # ensure POSITIVE_CONTROL is surfaced even on a fresh (non-resumed) run
        rep.setdefault("POSITIVE_CONTROL", pos_control)

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) -- ALL 13 arms ===================
    all_scores = dict(cheap_scores)
    all_scores.update(arm_scores)
    digests = {k: DSI._digest(np.concatenate([v["P"], v["S"]])) for k, v in all_scores.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC PER ARM (expensive arms) ====================================
    for i, (name, sc) in enumerate(arm_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + 100 + i)
        auc_results[name] = res
        margin_vs_max_floor = round(res["auc"] - max_floor_auc_this_population, 4)
        margin_vs_half = round(res["auc"] - 0.5, 4)
        res["margin_vs_max_floor_this_population"] = margin_vs_max_floor
        res["margin_vs_0.5"] = margin_vs_half
        print("[auc] %-30s AUC=%.4f CI=%r band=%s margin_vs_max_floor=%+.4f margin_vs_0.5=%+.4f" % (
            name, res["auc"], res["ci95"], res["band"], margin_vs_max_floor, margin_vs_half),
             flush=True)
    rep["AUC_PER_ARM"] = auc_results

    # =============================== POWER CHECK (coverage) ==========================================
    seven_ci = {a: auc_results[a]["ci95"] for a in SEVEN_ARMS}
    los = [seven_ci[a][0] for a in SEVEN_ARMS]
    his = [seven_ci[a][1] for a in SEVEN_ARMS]
    any_pairwise_separated = False
    for i in range(len(SEVEN_ARMS)):
        for j in range(i + 1, len(SEVEN_ARMS)):
            ai, aj = SEVEN_ARMS[i], SEVEN_ARMS[j]
            if seven_ci[ai][1] < seven_ci[aj][0] or seven_ci[aj][1] < seven_ci[ai][0]:
                any_pairwise_separated = True
    max_halfwidth = max(auc_results[a]["ci_halfwidth"] for a in SEVEN_ARMS)
    power_insufficient = not any_pairwise_separated
    rep["POWER_CHECK"] = {"n_matched_pairs_per_cell": n_match,
                          "max_ci_halfwidth_across_seven_arms": max_halfwidth,
                          "any_pairwise_CI_separated_among_seven_arms": any_pairwise_separated,
                          "POWER_INSUFFICIENT": power_insufficient}

    # =============================== RANK CORRELATION (the decisive comparison) ======================
    wordnet_aucs: Dict[str, Optional[float]] = {}
    rank_corr_diag: Dict = {"source_paths": {"DSI": DSI_METRICS_PATH, "CAP": CAP_METRICS_PATH,
                                             "TC": TC_METRICS_PATH}}
    try:
        import json
        with open(DSI_METRICS_PATH, encoding="utf-8") as f:
            dsi_m = json.load(f)
        dsi_auc = dsi_m["report"]["AUC_PER_ARM"]
        for a in ["INCUMBENT_LIVE_STORE", "RAW_COUNT_FULL_ACCUM", "RAW_COUNT_SINGLE_OCC",
                 "PRESENCE_ABSENCE_BINARIZED", "PARADIGMATIC_PROFILE_WRITE"]:
            wordnet_aucs[a] = dsi_auc[a]["auc"]
        with open(TC_METRICS_PATH, encoding="utf-8") as f:
            tc_m = json.load(f)
        wordnet_aucs["T0_VANILLA_PPMI_SVD"] = tc_m["report"]["T0_VANILLA_PPMI_SVD"]["sweep"]["50"]["auc"]
        wordnet_aucs["T2_SHIFTED_PPMI_K15"] = \
            tc_m["report"]["T2_SHIFTED_PPMI"]["RESULT_held_out_selected_eval_AUC"]["auc"]
        rank_corr_diag["wordnet_instrument_aucs"] = wordnet_aucs
        human_aucs = {a: auc_results[a]["auc"] for a in SEVEN_ARMS}
        rank_corr_diag["human_instrument_aucs"] = human_aucs
        wn_vec = np.array([wordnet_aucs[a] for a in SEVEN_ARMS])
        hu_vec = np.array([human_aucs[a] for a in SEVEN_ARMS])
        rho, _p_asymp = spearmanr(wn_vec, hu_vec)
        # exact permutation test (7! = 5040 permutations, small enough to enumerate)
        import itertools
        n7 = len(SEVEN_ARMS)
        perm_rhos = []
        for perm in itertools.permutations(range(n7)):
            r, _ = spearmanr(wn_vec, hu_vec[list(perm)])
            perm_rhos.append(r if not np.isnan(r) else 0.0)
        perm_rhos = np.array(perm_rhos)
        exact_p_two_sided = float(np.mean(np.abs(perm_rhos) >= abs(rho) - 1e-9))
        # bootstrap-of-arms 95% CI (informal, disclosed low-n)
        rng_bs = np.random.default_rng(MASTER_SEED + 6060)
        boot_rhos = []
        for _ in range(10000):
            idx = rng_bs.integers(0, n7, size=n7)
            r, _ = spearmanr(wn_vec[idx], hu_vec[idx])
            if not np.isnan(r):
                boot_rhos.append(r)
        boot_rhos = np.array(boot_rhos) if boot_rhos else np.array([np.nan])
        rank_corr_diag.update({
            "n_arms": n7, "spearman_rho": None if np.isnan(rho) else round(float(rho), 4),
            "exact_permutation_two_sided_p": round(exact_p_two_sided, 4),
            "bootstrap_of_arms_ci95": [round(float(np.nanpercentile(boot_rhos, 2.5)), 4),
                                      round(float(np.nanpercentile(boot_rhos, 97.5)), 4)],
            "DISCLOSURE": "n=7 arms is a very small sample for a rank correlation; the bootstrap CI "
                          "and exact permutation p-value are both reported so the reader can judge "
                          "resolution directly rather than trust a single point estimate.",
        })
    except Exception as e:  # NOT BaseException; this is a reporting side-channel, never fatal to
                            # the licensed arm numbers already computed above -- record and continue
        rank_corr_diag["ERROR"] = "%s: %s" % (type(e).__name__, str(e)[:500])
    rep["RANK_CORRELATION"] = rank_corr_diag
    rep["POPULATIONS_NOT_COMPARABLE"] = (
        "this instrument's matched population and the WordNet instrument's are DIFFERENT, "
        "non-overlapping-by-construction pools (different label source, different n, different "
        "difficulty) -- absolute AUC values are NEVER compared side by side across the two "
        "instruments; only RANK_CORRELATION (the arm ORDERING) is a valid cross-instrument statement")

    # =============================== INTERPRETATION (STOP-IF iii/iv/v/vi) ============================
    # NOTE: instrument_licensed is always True by this point -- the UNLICENSED branch returns early
    # above, before any expensive arm is built (v2.0's license-gate-first fix). Kept as an explicit
    # guard rather than assumed, in case a future refactor removes the early return.
    if not instrument_licensed:
        interp = "INSTRUMENT_UNLICENSED_NO_INTERPRETATION_PERMITTED"
    elif power_insufficient:
        interp = "POWER_INSUFFICIENT__n=%d__max_ci_halfwidth=%.4f" % (n_match, max_halfwidth)
    else:
        rho_val = rank_corr_diag.get("spearman_rho")
        boot_ci = rank_corr_diag.get("bootstrap_of_arms_ci95", [None, None])
        # STOP-IF (vi): the real bar is max(four floors) on THIS population, not 0.5. An arm whose CI
        # sits above 0.5 but not above max_floor_auc_this_population is NOT "above chance" by this
        # instrument's own bar -- report both margins (already attached per-arm above) but gate the
        # headline flag on the STRICTER bar.
        any_above_max_floor = any(
            auc_results[a]["ci95"][0] > max_floor_auc_this_population for a in SEVEN_ARMS)
        any_above_half = any(auc_results[a]["band"] == "ABOVE_0.5_SUBSTITUTABILITY" for a in SEVEN_ARMS)
        if rho_val is not None and boot_ci[0] is not None and boot_ci[0] > 0:
            interp = "STOP_IF_iv_ORDERINGS_AGREE__6_23_IS_ABOUT_OUR_STORE__rho=%.4f" % rho_val
        elif rho_val is not None and boot_ci[1] is not None and boot_ci[1] < 0:
            interp = "STOP_IF_v_ORDERINGS_DISAGREE__6_23_WAS_ABOUT_WORDNET__rho=%.4f" % rho_val
        else:
            interp = "RANK_CORRELATION_CI_INCLUDES_ZERO__INCONCLUSIVE_AT_THIS_N__rho=%r" % rho_val
        if any_above_max_floor:
            interp += "__STOP_IF_vi_ARM_CI_SEPARATED_ABOVE_MAX_FLOOR_%.4f" % max_floor_auc_this_population
        elif any_above_half:
            interp += "__ARM_ABOVE_0.5_BUT_NOT_ABOVE_MAX_FLOOR_%.4f__NOT_STOP_IF_vi" % max_floor_auc_this_population
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

    licensed = rep.get("LICENSING", {}).get("INSTRUMENT_LICENSED", False)
    interp = rep.get("INTERPRETATION", "UNKNOWN")
    verdict = "DISSOCIATION_INSTRUMENT_HUMAN_%s__%s" % ("LICENSED" if licensed else "UNLICENSED", interp)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": ("Human-label (SimLex-999 + SimVerb-3500) dissociation-score instrument: "
                       "does agreement with human similarity judgements rank the same 7 arms the "
                       "same way the WordNet-labelled instrument does? -> " + verdict),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "T_HIGH": T_HIGH, "T_LOW": T_LOW,
                  "TOP_DECILE_Q": TOP_DECILE_Q, "KNOWN_ANSWER_MIN_AUC": KNOWN_ANSWER_MIN_AUC},
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
