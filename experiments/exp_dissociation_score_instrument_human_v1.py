"""exp_dissociation_score_instrument_human_v1 -- SAME QUESTION, WORDNET-FREE LABELS.

THIS CELL EXISTS TO TEST WHETHER PLAN SEC 6.23'S CONCLUSION IS ABOUT OUR STORE OR ABOUT WORDNET.

Verified off disk (`exp_dissociation_score_instrument_v1.py:304,312,674`): `SET_P` is built by
`build_wordnet_synonym_candidates()` from `wn.synsets()`; `SET_S` explicitly excludes any WordNet
pair even at high co-occurrence; the known-answer arm is WordNet path similarity. WordNet defines
BOTH sides of the licensed instrument's labels (plan sec 6.24). Every number in plan 6.12-6.23 is
therefore really "agreement with WordNet's notion of synonymy". This cell reruns the SAME 7 arms on
a SECOND, INDEPENDENT construction whose labels come from HUMAN SIMILARITY JUDGEMENTS
(SimLex-999 + SimVerb-3500) instead of WordNet, and reports the rank correlation between the two
instruments' arm orderings. Full spec: notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.24 (commit
21c9b3e19), pre-reg preregs/2026-08-18_dissociation_score_instrument_human_v1.md.

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
STOP-IF (evaluated in this order):
  (i)   any floor's 95% CI excludes 0.5 -> INSTRUMENT_LICENSED=False, publish no arm numbers.
  (ii)  known-answer AUC < 0.999 -> label/score plumbing bug (it is tautological by design).
  (iii) achieved n / CI half-widths too wide to resolve the arm ordering -> POWER_INSUFFICIENT,
        report the achieved half-width, not a ranking.
  (iv)  the two instruments' arm orderings AGREE (rank correlation excludes 0, positive) -> plan
        6.23's conclusion is about OUR STORE and survives.
  (v)   the orderings DISAGREE -> 6.23 was substantially about WordNet; redirect the programme.
  (vi)  any arm reads CI-separated ABOVE 0.5 on the human instrument -> report loudly, every control,
        the coverage.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: POPULATION_HUMAN, SCORES_HUMAN, POSITIVE_CONTROL as separate
#   tools.exp_checkpoint units; MAIN wraps the whole run() result
# - discriminator survives scale: n/a -- licensing-gate instrument re-score, not a mechanism sweep;
#   the real scale risk is COVERAGE, addressed by the explicit POWER_INSUFFICIENT stop-if
# - calibration_check: default_ok_for_this_regime (reuses landed, regression-gated caches unmodified)
# - progress_logging: print_flush_true (every phase prints a flushed line)
# - baseline_in_band: n/a -- licensing-gate instrument, same declaration as DSI
# - crlb_floor_computed: n/a -- AUC dissociation measurement, not a capacity sweep

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. No store is
rebuilt; data/foundation/** is never opened. Writes only under
data/exp_dissociation_score_instrument_human_v1[_reduced]/.
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

ANCHOR_NAME = "dissociation_score_instrument_human_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/dissociation_score_instrument_human_2026-08-18.md"

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
    if n_match < 20:
        raise SystemExit("INSTRUMENT_UNBUILDABLE_AT_THIS_N -- only %d matched pairs per cell; too "
                         "few for a meaningful AUC. diag=%r" % (n_match, pop_diag))
    # re-surface the WN audit at top level too (post-checkpoint-resume path needs it explicitly)
    rep.setdefault("WORDNET_INDEPENDENCE_AUDIT_MATCHED_SET_P", pop_diag.get("wordnet_independence_audit_matched"))

    words_needed = sorted(set(w for w1, w2, _ in matchedP + matchedS for w in (w1, w2)))
    print("[scores] %d distinct words needed across both matched cells" % len(words_needed), flush=True)

    def score_of_pair(pairs: List[Tuple[str, str, str]]) -> np.ndarray:
        out = np.zeros(len(pairs), dtype=np.float64)
        for i, (w1, w2, _p) in enumerate(pairs):
            out[i] = pair_score_of.get(tuple(sorted((w1, w2))), np.nan)
        return out

    # =============================== SCORES_HUMAN (checkpointed unit) ================================
    scores_key = unit_key("SCORES_HUMAN", CODE_VERSION, grid)
    prior_scores = load_units(out_dir_ckpt).get(scores_key)
    if prior_scores is not None:
        print("[scores] RESUMED FROM CHECKPOINT", flush=True)
        arm_scores = {k: {"P": np.array(v["P"]), "S": np.array(v["S"])} for k, v in prior_scores.items()}
    else:
        wid = {w: pos_idx[w] for w in words_needed}
        Mn_incumbent = l2n(mat)
        t0s = time.time()

        store_incumbent = {w: Mn_incumbent[wid[w]] for w in words_needed}

        rng_rand = np.random.default_rng(MASTER_SEED + 9091)
        rand_full = l2n(rng_rand.standard_normal((n_anchors, mat.shape[1])).astype(np.float32))
        store_random = {w: rand_full[wid[w]] for w in words_needed}

        scrambled = l2n(FB.scramble_null(mat, MASTER_SEED + 4433))
        store_scramble = {w: scrambled[wid[w]] for w in words_needed}

        Tn = l2n(t_mat)
        store_ortho = {w: Tn[wid[w]] for w in words_needed}

        proto = FB.constant_prototype_floor(mat, mat_ok)
        proto_of_words = {w: float(proto[wid[w]]) for w in words_needed}
        freq_of_words = {w: fq_log.get(w, 0.0) for w in words_needed}

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

        print("[scores] all arms built, elapsed=%.1fs" % (time.time() - t0s), flush=True)

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

        arm_scores_raw: Dict[str, Tuple[np.ndarray, np.ndarray]] = {
            "F_ORTHOGRAPHIC": pair_dense(store_ortho),
            "F_FREQUENCY": pair_scalar_max(freq_of_words),
            "F_SCRAMBLE": pair_dense(store_scramble),
            "F_CONSTANT_PROTOTYPE": pair_scalar_mean(proto_of_words),
            "KNOWN_ANSWER_HUMAN_RATING": (score_of_pair(matchedP), score_of_pair(matchedS)),
            "RANDOM_VECTOR_STORE": pair_dense(store_random),
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

    # =============================== ARMS-MUST-DIFFER (META_RULE_AF) ================================
    digests = {k: DSI._digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores.items()}
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests

    # =============================== AUC PER ARM ======================================================
    FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
    boot_seed_base = MASTER_SEED + 8383
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(arm_scores.items()):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, boot_seed_base + i)
        auc_results[name] = res
        print("[auc] %-30s AUC=%.4f CI=%r band=%s" % (name, res["auc"], res["ci95"], res["band"]),
             flush=True)
    rep["AUC_PER_ARM"] = auc_results

    # =============================== LICENSING (STOP-IF i, ii) =======================================
    floor_licensing_ok = all(auc_results[f]["band"] == "NOT_SEPARATED_FROM_CHANCE" for f in FLOOR_NAMES)
    floor_failures = [f for f in FLOOR_NAMES if auc_results[f]["band"] != "NOT_SEPARATED_FROM_CHANCE"]
    known_answer_auc = auc_results["KNOWN_ANSWER_HUMAN_RATING"]["auc"]
    known_answer_ok = known_answer_auc >= KNOWN_ANSWER_MIN_AUC
    random_store_ok = auc_results["RANDOM_VECTOR_STORE"]["band"] == "NOT_SEPARATED_FROM_CHANCE"
    instrument_licensed = bool(floor_licensing_ok and known_answer_ok)
    rep["LICENSING"] = {
        "STOP_IF_i_floors_at_chance": {"PASS": floor_licensing_ok, "floor_failures": floor_failures},
        "STOP_IF_ii_known_answer_near_1": {"PASS": known_answer_ok, "measured_auc": known_answer_auc,
                                          "gate": KNOWN_ANSWER_MIN_AUC},
        "random_vector_store_at_chance": {"PASS": random_store_ok},
        "INSTRUMENT_LICENSED": instrument_licensed,
    }
    if not instrument_licensed:
        print("[LICENSING] INSTRUMENT UNLICENSED -- store-arm numbers are WRITTEN below for the "
             "record but MUST NOT be interpreted as a finding. floor_failures=%r known_answer=%.4f"
             % (floor_failures, known_answer_auc), flush=True)

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

    # =============================== INTERPRETATION (STOP-IF iii/iv/v/vi) ============================
    if not instrument_licensed:
        interp = "INSTRUMENT_UNLICENSED_NO_INTERPRETATION_PERMITTED"
    elif power_insufficient:
        interp = "POWER_INSUFFICIENT__n=%d__max_ci_halfwidth=%.4f" % (n_match, max_halfwidth)
    else:
        rho_val = rank_corr_diag.get("spearman_rho")
        boot_ci = rank_corr_diag.get("bootstrap_of_arms_ci95", [None, None])
        any_above_half = any(auc_results[a]["band"] == "ABOVE_0.5_SUBSTITUTABILITY" for a in SEVEN_ARMS)
        if rho_val is not None and boot_ci[0] is not None and boot_ci[0] > 0:
            interp = "STOP_IF_iv_ORDERINGS_AGREE__6_23_IS_ABOUT_OUR_STORE__rho=%.4f" % rho_val
        elif rho_val is not None and boot_ci[1] is not None and boot_ci[1] < 0:
            interp = "STOP_IF_v_ORDERINGS_DISAGREE__6_23_WAS_ABOUT_WORDNET__rho=%.4f" % rho_val
        else:
            interp = "RANK_CORRELATION_CI_INCLUDES_ZERO__INCONCLUSIVE_AT_THIS_N__rho=%r" % rho_val
        if any_above_half:
            interp += "__STOP_IF_vi_ARM_ABOVE_0.5_ON_HUMAN_INSTRUMENT"
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
