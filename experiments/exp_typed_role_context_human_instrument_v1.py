"""exp_typed_role_context_human_instrument_v1 -- SCORE THE TYPED-CONTEXT ARMS ON THE **HUMAN**
INSTRUMENT. THE TWO FACTS FROM notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md SEC 6.39 MEET HERE.

=================================================================================================
BOUND BY A PRE-COMMITMENT WRITTEN BEFORE THIS FILE EXISTED. `notes/PLAN_ORGAN_STEP_LADDERS_
2026-08-17.md` sec 6.39, committed at `fa5da1d2c` BEFORE this cell was dispatched, fixes the
readings (A)/(B)/(C) below. THIS FILE DOES NOT RENEGOTIATE THEM AND PROPOSES NO BAND CHANGE.
Quoted verbatim from 6.39 (the strings are also emitted into metrics.json so a reader never has to
trust this docstring):

  (A) "`U1` CLEARS 0.5943 CI-SEPARATED -> the typed-context result holds on two independently built
      instruments. That would be this programme's first genuine cross-instrument capability win, and
      it must still be reported with `STOPIF3` attached -- clearing the bar does NOT retire the
      finding that role-only ties it."
  (B) "`U1` LANDS AT OR BELOW CHANCE ON HUMAN JUDGEMENT -> the 0.6669 was WORDNET-SPECIFIC, and rho
      0.9034 was carried by agreement about the POOR arms while the instruments DISAGREE at the top
      of the range -- which is where it matters. THIS IS THE INFORMATIVE CASE. IT MUST NOT BE
      REPORTED AS 'MIXED', AND IT PARTIALLY RE-OPENS 6.24 for the only region of the scale anyone
      cares about."
  (C) "ABOVE CHANCE BUT NOT CI-SEPARATED FROM 0.5943 -> POWER_INSUFFICIENT, FULL STOP. n=65 against
      n=242 is a 3.7x smaller sample and the human CI half-widths in v4 run ~0.10 -- wide enough to
      swallow the entire 0.6669-vs-0.5943 margin before any capability question is asked. DO NOT
      READ THIS AS A CEILING."
  MANDATORY REGARDLESS OF BRANCH: "report the CI half-width and the null p95 at n=65 beside every
      margin, and score `U3_ROLE_ONLY` in the same run -- if `U1` ties `U3` on the human instrument
      too, the which-kind-of-slot reading is confirmed on BOTH sticks and stops being a
      one-instrument caveat."

A FOURTH ARITHMETIC OUTCOME EXISTS AND IS NOT ONE OF THE THREE, so it is labelled as such rather
than silently folded into the nearest band: AUC strictly ABOVE chance yet CI-separated BELOW 0.5943
(ci_hi < bar). That is not (A), not (B) ("at or below chance"), and not literally (C) ("not
CI-separated from 0.5943"). If it fires this file reports `D_ABOVE_CHANCE_BUT_CI_SEPARATED_BELOW_
BAR` and says so plainly; the Director adjudicates. No band is moved here.

=================================================================================================
WHY THIS CELL. `exp_typed_role_context_write_rule_dissociation_v1` (`5170c7751`) read
U1_TYPED_CONTEXT 0.6669 [0.6184, 0.7136] on the WORDNET instrument (DSI, n=242/cell, bar 0.5431 =
F_CONSTANT_PROTOTYPE), CI-separated above its bar with U1_COVERAGE_MATCHED unmoved at 0.6669 -- the
first arm in the programme to clear a bar with its coverage control intact. It landed AFTER
`exp_dissociation_score_instrument_human_v4` (`75e093747`) had already built its 24-arm harvest, so
U1 IS NOT AMONG THOSE 24 AND HAS NEVER BEEN SCORED AGAINST HUMAN JUDGEMENT.

=================================================================================================
ARM-NAME COLLISION, DISCLOSED LOUDLY BECAUSE IT IS A REAL TRAP (emitted as
`NAME_COLLISION_DISCLOSURE` in metrics.json). TWO DIFFERENT CELLS OWN AN ARM CALLED
`T2_UNTYPED_SAME_COVERAGE`, AND ONE CALLED `T1_TYPED_ROLE` LOOKS LIKE `U1` BUT IS NOT:

  * v4's `T1_TYPED_ROLE` / `T2_UNTYPED_SAME_COVERAGE` (WordNet AUC 0.5802 / 0.5900) are the
    SIMPLEWIKI cell `exp_typed_role_selectional_asset_writerule_v1`'s arms, built by
    `TR.build_typed_role_matrix` / `TR.collapse_roles` + `TR.ppmi_svd` from the 737,488-slot
    PERSISTED SELECTIONAL ASSET. THEY ARE NOT SCORED HERE AND NOT TOUCHED HERE.
  * THIS cell's `U1_TYPED_CONTEXT` / `U3_ROLE_ONLY` / `T2_UNTYPED_SAME_COVERAGE` are the CONTEXT
    cell `exp_typed_role_context_write_rule_dissociation_v1`'s arms, built by ONE function,
    `URC.store_from_arc_events(arc_events, words, mode="typed"|"role_only"|"neighbour_only")`, over
    arcs re-extracted from THIS project's own 34,169-sentence corpus with the real dependency
    front-end. Different corpus, different construction, different cell.
  Every arm this file reports carries an `ARM_PROVENANCE` entry naming its source cell, source
  function and mode. The two families are never compared as if they were the same arm.

=================================================================================================
METHOD -- NO CONSTRUCTION IS REIMPLEMENTED (hard requirement).
  * Population: v3's own human population, loaded VERBATIM from v3's checkpoint through v4's own
    `V4.v3_regression_gate()`. Zero matching code, zero caliper code, zero binning code here.
  * Arms: `URC.build_occurrence_data` (the context cell's own occurrence builder, real
    `SPE._load_frontend()` parser) then `URC.flatten_arc_events` then `URC.store_from_arc_events`,
    all called VERBATIM. Scored with `DSI.dense_scores_from_dict_store` + `DSI.auc_bootstrap`, the
    same scorer both instruments use. The S1/N1/N2/N3/N6 arms of the context cell are NOT rebuilt
    here (out of this dispatch's scope; stated, not silently dropped).
  * Context arm A0_INCUMBENT_HUMAN = v3's OWN cached RAW_COUNT_FULL_ACCUM score arrays on this
    identical population, reused bit-for-bit, never rebuilt -- so the paired U1-vs-A0 margin uses
    one population and one pair ordering.
  * BOTH regression gates v4 runs are re-run through v4's own functions, unmodified:
      GATE A: DSI's 8 cached checks recomputed from DSI's checkpoint, tol 0.0005.
      GATE B: v3's floors recomputed from v3's checkpoint, tol 0.0005, and n_match == 65.
    Either failure -> SystemExit before a single arm is built (an unlicensed instrument scores
    nothing).
  * EVERY FLOOR IS RECOMPUTED ON THIS POPULATION. No floor value is imported from the WordNet
    population. The bar is DERIVED here as max(four floors recomputed on the human population) and
    then cross-checked against 6.39's stated 0.5943 as a known answer; if the derivation disagreed
    with the pre-registered number, the derived value would be reported and the run marked, not
    quietly reconciled.
  * Reported beside EVERY margin: the bootstrap CI, its HALF-WIDTH, and the PERMUTATION NULL p95 at
    this n. A width is not an effect.
  * `U1` vs `U3` is read from the PAIRED-DIFFERENCE bootstrap CI (`PCWG.auc_margin_paired`, same
    resampled indices feeding both arms), NEVER from whether two individual CIs overlap. The two
    tests disagree and the overlap test is the wrong one.

PRIOR-WORK CHECK. `tools/substrate_query.sh` is NON-FUNCTIONAL (zero bytes, exit 0) and was NOT
used; its silence is not evidence. `os.walk` over `data/` is forbidden (157 GB, stalled two lanes).
Method actually used: name-level enumeration `ls experiments/ | grep -i -E "dissoc|typed|instrument"`
-> 19 files, every one inspected by name and the four candidates read: the human instrument is
v1/v2/v3/v4 (v4 is the harvest and is imported here rather than duplicated); the typed-role family
is `exp_typed_role_selectional_asset_writerule_v1` (SimpleWiki, already in v4's 24) and
`exp_typed_role_context_write_rule_dissociation_v1` (this cell's source, NOT in v4's 24, verified by
reading v4's own `HARVESTED_WORDNET_AUC` dict and its EXISTING_SEVEN list -- neither contains
`U1_TYPED_CONTEXT`). No sibling scores any context-cell arm on the human population. This cell is a
directly-commissioned follow-on, not an independently-conceived direction.

CELL-TEMPLATE MANDATORY (per .claude/agents/exp_dev.md):
# - arms_differ_verified: sha256 over every arm's per-pair score vector, asserted >1 distinct digest
# - final_metrics_atomicity: tmp_replace (experiments._seed_checkpoint.write_metrics, Path not str)
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint: OCC per word (URC's own unit keys, in THIS cell's own data dir) + MAIN
# - discriminator survives scale: FULL is the real n=65 population. The branch selector is a
#   deterministic function of (auc, ci95, bar) and is exercised end-to-end in --grid reduced, but
#   reduced (12 pairs/cell) CANNOT be powered -- that is the entire content of pre-committed branch
#   (C), which exists because n=65 itself may not be powered either. Smoke proves the machinery and
#   the branch emission; it does not and cannot pre-empt the reading.
# - calibration_check: default_ok_for_this_regime (v3's instrument reused unmodified; only the arms
#   under test are new)
# - progress_logging: print_flush_true (every phase prints a flushed line, Sec 17)
# - baseline_in_band: n/a -- licensing-gate + dissociation-AUC instrument, declared explicitly
# - crlb_floor_computed: n/a -- an AUC dissociation measurement is not a capacity sweep
# - tie conventions: DSI's AUC scorer is Mann-Whitney rank-sum with ties at 0.5 (auc_of uses
#   scipy rankdata's average-rank convention, ONE convention project-wide); ties are reported both
#   ways via TIE_DIAGNOSTICS (exact-tie count per arm) since zero-vector rows produce genuine ties.

ASCII-only. NO LLM anywhere in this runtime path. CPU only, pinned single-threaded. `hdlab/` is not
modified. `preregs/**` is not touched. `data/foundation/**` is never opened. Writes only under
data/exp_typed_role_context_human_instrument_v1[_reduced]/.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy import.
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

print("[imports] starting (numpy + DSI/PCWG/INFO/SPE/URC/V4 read-only -- flushed so a slow import "
      "is never mistaken for a hang)", flush=True)

import argparse
import hashlib
import json
import sys
import time
import traceback
from typing import Dict, List, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO, os.path.join(REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import experiments.exp_dissociation_score_instrument_v1 as DSI                         # noqa: E402  READ ONLY
import experiments.exp_predictive_coding_write_gate_dissociation_v1 as PCWG            # noqa: E402  READ ONLY
import experiments.exp_cue_information_audit_v1 as INFO                                # noqa: E402  READ ONLY
import experiments.selectional_preference_extractor_v1 as SPE                          # noqa: E402  READ ONLY
import experiments.exp_typed_role_context_write_rule_dissociation_v1 as URC            # noqa: E402  READ ONLY
import experiments.exp_dissociation_score_instrument_human_v4 as V4                    # noqa: E402  READ ONLY
from experiments._seed_checkpoint import get_output_dir, write_metrics                 # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units    # noqa: E402

print("[imports] done", flush=True)

ANCHOR_NAME = "typed_role_context_human_instrument_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/typed_role_context_human_instrument_v1_2026-08-18.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

MASTER_SEED = URC.MASTER_SEED
N_BOOT = 1500 if SMOKE else 10000
N_PERM = 2000 if SMOKE else 20000
N_SMOKE_PAIRS = 12

# The pre-registered bar, quoted from 6.39 for the KNOWN-ANSWER cross-check ONLY. The bar this cell
# actually uses is DERIVED below from floors recomputed on this population (never imported).
PREREG_BAR_6_39 = 0.5943
BAR_KNOWN_ANSWER_TOL = 0.0005
FLOOR_NAMES = ["F_ORTHOGRAPHIC", "F_FREQUENCY", "F_SCRAMBLE", "F_CONSTANT_PROTOTYPE"]
CHANCE = 0.5

BRANCH_TEXT_6_39 = {
    "A": ("(A) U1 CLEARS 0.5943 CI-SEPARATED -> the typed-context result holds on two independently "
          "built instruments. That would be this programme's first genuine cross-instrument "
          "capability win, and it must still be reported with STOPIF3 attached -- clearing the bar "
          "does NOT retire the finding that role-only ties it."),
    "B": ("(B) U1 LANDS AT OR BELOW CHANCE ON HUMAN JUDGEMENT -> the 0.6669 was WORDNET-SPECIFIC, "
          "and rho 0.9034 was carried by agreement about the POOR arms while the instruments "
          "DISAGREE at the top of the range -- which is where it matters. THIS IS THE INFORMATIVE "
          "CASE. IT MUST NOT BE REPORTED AS 'MIXED', AND IT PARTIALLY RE-OPENS 6.24 for the only "
          "region of the scale anyone cares about."),
    "C": ("(C) ABOVE CHANCE BUT NOT CI-SEPARATED FROM 0.5943 -> POWER_INSUFFICIENT, FULL STOP. n=65 "
          "against n=242 is a 3.7x smaller sample and the human CI half-widths in v4 run ~0.10 -- "
          "wide enough to swallow the entire 0.6669-vs-0.5943 margin before any capability question "
          "is asked. DO NOT READ THIS AS A CEILING."),
    "D_NOT_PRECOMMITTED": ("NOT ONE OF 6.39's THREE BRANCHES: AUC strictly above chance yet the CI "
                           "is separated BELOW the bar (ci_hi < bar). Reported as-is, unadjudicated; "
                           "no band was moved to accommodate it."),
}

ARM_PROVENANCE = {
    "U1_TYPED_CONTEXT": {
        "source_cell": "experiments/exp_typed_role_context_write_rule_dissociation_v1.py",
        "source_commit_when_landed": "5170c7751",
        "construction": "URC.store_from_arc_events(mode='typed')  # (neighbour, relation, direction)",
        "corpus": "exp_cue_information_audit_v1.load_corpus_and_buckets (34,169 sentences)"},
    "U3_ROLE_ONLY": {
        "source_cell": "experiments/exp_typed_role_context_write_rule_dissociation_v1.py",
        "source_commit_when_landed": "5170c7751",
        "construction": "URC.store_from_arc_events(mode='role_only')  # (relation, direction) only",
        "corpus": "exp_cue_information_audit_v1.load_corpus_and_buckets (34,169 sentences)"},
    "T2_UNTYPED_SAME_COVERAGE": {
        "source_cell": "experiments/exp_typed_role_context_write_rule_dissociation_v1.py",
        "source_commit_when_landed": "5170c7751",
        "construction": "URC.store_from_arc_events(mode='neighbour_only')  # label STRIPPED",
        "corpus": "exp_cue_information_audit_v1.load_corpus_and_buckets (34,169 sentences)",
        "NOT_THE_SAME_ARM_AS": ("v4/exp_typed_role_selectional_asset_writerule_v1's "
                                "T2_UNTYPED_SAME_COVERAGE (TR.collapse_roles + TR.ppmi_svd over the "
                                "SimpleWiki selectional asset, WordNet AUC 0.5900) -- different cell, "
                                "different corpus, different construction, same name")},
    "A0_INCUMBENT_HUMAN": {
        "source_cell": "experiments/exp_dissociation_score_instrument_human_v3.py (cached scores)",
        "construction": "REUSED BIT-FOR-BIT from v3's SCORES_EXPENSIVE checkpoint, arm "
                        "RAW_COUNT_FULL_ACCUM -- never rebuilt here",
        "corpus": "same 34,169-sentence corpus, plain bag-of-words raw-count store"},
}

NAME_COLLISION_DISCLOSURE = (
    "TWO CELLS OWN AN ARM NAMED T2_UNTYPED_SAME_COVERAGE. This cell scores the CONTEXT cell's "
    "(exp_typed_role_context_write_rule_dissociation_v1, URC.store_from_arc_events mode="
    "'neighbour_only'). v4's 24-arm table contains the SIMPLEWIKI cell's "
    "(exp_typed_role_selectional_asset_writerule_v1, TR.collapse_roles) with WordNet AUC 0.5900, and "
    "v4's T1_TYPED_ROLE (WordNet AUC 0.5802) is that same SimpleWiki cell -- it is NOT "
    "U1_TYPED_CONTEXT (WordNet AUC 0.6669). The two families are kept distinct by construction here: "
    "this file imports only URC for arm construction and never calls TR.")


def _digest(v) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# NULLS AND MARGIN REPORTING -- a width is not an effect (6.39 mandatory clause).
# =================================================================================================
def perm_null_auc(sp: np.ndarray, ss: np.ndarray, n_perm: int, seed: int) -> Dict:
    """Label-permutation null for a single arm's AUC at THIS n: pool the arm's own P and S scores,
    reassign the P/S labels at random n_perm times, recompute AUC. Preserves the arm's own score
    distribution and its own tie structure exactly -- the null is about the LABELS, not the values."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    n_p, n_s = sp.size, ss.size
    pool = np.concatenate([sp, ss])
    obs = DSI.auc_of(sp, ss)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_perm, dtype=np.float64)
    for b in range(n_perm):
        perm = rng.permutation(pool)
        draws[b] = DSI.auc_of(perm[:n_p], perm[n_p:n_p + n_s])
    p95 = float(np.percentile(draws, 95.0))
    p99 = float(np.percentile(draws, 99.0))
    p_one = float(np.mean(draws >= obs - 1e-12))
    return {"null_p50": round(float(np.percentile(draws, 50.0)), 4),
            "null_p95_at_this_n": round(p95, 4), "null_p99_at_this_n": round(p99, 4),
            "null_sd": round(float(np.std(draws)), 4),
            "observed_auc": round(obs, 4), "p_one_sided_vs_null": round(p_one, 4),
            "observed_exceeds_null_p95": bool(obs > p95), "n_perm": int(n_perm),
            "n_pairs_P": int(n_p), "n_pairs_S": int(n_s)}


def perm_null_paired_diff(aP, aS, bP, bS, n_perm: int, seed: int) -> Dict:
    """Exchangeability null for AUC(a) - AUC(b) at THIS n: for each matched-pair index independently,
    swap arm a's and arm b's score for that pair with prob 0.5, then recompute the difference. Under
    'the two arms carry the same information about this pair' the swap is uninformative. Reports the
    p95 of the ABSOLUTE difference -- the width a real difference has to beat."""
    aP, aS = np.asarray(aP, dtype=np.float64), np.asarray(aS, dtype=np.float64)
    bP, bS = np.asarray(bP, dtype=np.float64), np.asarray(bS, dtype=np.float64)
    obs = DSI.auc_of(aP, aS) - DSI.auc_of(bP, bS)
    rng = np.random.default_rng(seed)
    draws = np.empty(n_perm, dtype=np.float64)
    for k in range(n_perm):
        mp = rng.random(aP.size) < 0.5
        ms = rng.random(aS.size) < 0.5
        a_p, b_p = np.where(mp, bP, aP), np.where(mp, aP, bP)
        a_s, b_s = np.where(ms, bS, aS), np.where(ms, aS, bS)
        draws[k] = DSI.auc_of(a_p, a_s) - DSI.auc_of(b_p, b_s)
    p95_abs = float(np.percentile(np.abs(draws), 95.0))
    return {"observed_diff": round(obs, 4), "null_p95_abs_diff_at_this_n": round(p95_abs, 4),
            "null_sd": round(float(np.std(draws)), 4),
            "p_two_sided_vs_null": round(float(np.mean(np.abs(draws) >= abs(obs) - 1e-12)), 4),
            "observed_exceeds_null_p95": bool(abs(obs) > p95_abs), "n_perm": int(n_perm)}


def margin_with_width(name: str, aP, aS, bP, bS, seed_off: int) -> Dict:
    """Paired-bootstrap margin (PCWG.auc_margin_paired verbatim) + its CI HALF-WIDTH + its own
    permutation null p95 at this n. Read a margin from THIS, never from two overlapping CIs."""
    m = PCWG.auc_margin_paired(aP, aS, bP, bS, N_BOOT, MASTER_SEED + seed_off)
    lo, hi = m["ci95_diff"]
    m["ci_halfwidth_diff"] = round((hi - lo) / 2.0, 4)
    m["NULL"] = perm_null_paired_diff(aP, aS, bP, bS, N_PERM, MASTER_SEED + 3000 + seed_off)
    m["comparison"] = name
    m["READ_FROM"] = "paired-difference CI (same resampled indices both arms), NOT CI overlap"
    return m


def tie_diagnostics(sp: np.ndarray, ss: np.ndarray) -> Dict:
    """Ties are real here: a word with no arc events gets a zero row, so its pair scores 0.0 exactly.
    DSI.auc_of scores a tie at 0.5. Reported BOTH ways (ties-as-0.5 = the project convention, plus
    the pessimistic ties-as-loss and optimistic ties-as-win bounds) so the convention is visible."""
    sp = np.asarray(sp, dtype=np.float64)
    ss = np.asarray(ss, dtype=np.float64)
    gt = float(np.mean(sp[:, None] > ss[None, :]))
    eq = float(np.mean(sp[:, None] == ss[None, :]))
    return {"auc_ties_half": round(gt + 0.5 * eq, 4), "auc_ties_as_loss": round(gt, 4),
            "auc_ties_as_win": round(gt + eq, 4), "frac_tied_comparisons": round(eq, 4),
            "n_zero_scores_P": int(np.sum(sp == 0.0)), "n_zero_scores_S": int(np.sum(ss == 0.0))}


def band_vs_bar(ci: Sequence[float], bar: float) -> str:
    return URC.band_vs_bar(0.0, list(ci), bar)


# =================================================================================================
# self-test -- reuses the source cell's OWN self-test wholesale (proves every construction entry
# point) and then exercises THIS FILE'S OWN glue (nulls, margins, branch selector, tie diagnostics)
# on known answers plus a tiny REAL slice of v3's own checkpoint.
# =================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    ev["URC_selftest_evidence_keys"] = sorted(URC.self_test().keys())
    print("[selftest] source-cell (URC) self-test PASS", flush=True)

    # --- perm_null_auc known answers ---------------------------------------------------------------
    # (1) a perfectly separated arm must sit far above its own null p95;
    # (2) two IDENTICAL distributions must give an observed AUC of 0.5 that does NOT beat null p95.
    sep = perm_null_auc(np.arange(20.0) + 100.0, np.arange(20.0), 500, 11)
    assert sep["observed_auc"] == 1.0, "perfectly separated arm must read AUC 1.0: %r" % sep
    assert sep["observed_exceeds_null_p95"], "AUC 1.0 must exceed its own null p95: %r" % sep
    same = perm_null_auc(np.arange(20.0), np.arange(20.0), 500, 12)
    assert abs(same["observed_auc"] - 0.5) < 1e-9, "identical vectors must read AUC 0.5: %r" % same
    assert not same["observed_exceeds_null_p95"], "AUC 0.5 must NOT beat its own null p95: %r" % same
    assert same["null_p95_at_this_n"] > 0.5, "a null p95 at finite n must exceed 0.5: %r" % same
    ev["perm_null_known_answers"] = {"separated": sep["observed_auc"], "identical": same["observed_auc"],
                                     "null_p95_identical": same["null_p95_at_this_n"]}

    # --- paired-difference null known answer: two arms with IDENTICAL scores must have observed
    # diff exactly 0 and must not exceed the null width -----------------------------------------------
    a = np.array([0.9, 0.8, 0.7, 0.6]); b = np.array([0.1, 0.2, 0.3, 0.4])
    d_same = perm_null_paired_diff(a, b, a.copy(), b.copy(), 300, 13)
    assert abs(d_same["observed_diff"]) < 1e-12, "identical arms must give diff 0: %r" % d_same
    assert not d_same["observed_exceeds_null_p95"], "diff 0 cannot beat a null width: %r" % d_same
    ev["paired_null_known_answer"] = d_same

    # --- tie diagnostics known answer: all-zero scores => every comparison tied, 0.5 by convention,
    # 0.0 pessimistic, 1.0 optimistic ----------------------------------------------------------------
    z = tie_diagnostics(np.zeros(5), np.zeros(5))
    assert (z["auc_ties_half"], z["auc_ties_as_loss"], z["auc_ties_as_win"]) == (0.5, 0.0, 1.0), \
        "all-tied fixture must read 0.5/0.0/1.0: %r" % z
    assert z["frac_tied_comparisons"] == 1.0
    ev["tie_diagnostics_known_answer"] = z

    # --- branch selector known answers (the pre-committed readings, exercised as a pure function) ----
    assert select_branch(0.70, [0.62, 0.78], 0.5943)[0] == "A"
    assert select_branch(0.48, [0.40, 0.56], 0.5943)[0] == "B"       # at or below chance
    assert select_branch(0.50, [0.42, 0.58], 0.5943)[0] == "B"       # exactly chance counts as B
    assert select_branch(0.62, [0.55, 0.69], 0.5943)[0] == "C"       # above chance, straddles bar
    assert select_branch(0.55, [0.51, 0.58], 0.5943)[0] == "D_NOT_PRECOMMITTED"
    ev["branch_selector_known_answers"] = True

    # --- REAL code path on a tiny slice of v3's own checkpoint: build the three arms end to end -----
    gate_b = V4.v3_regression_gate()
    mP = gate_b["matchedP"][:3]
    mS = gate_b["matchedS"][:3]
    words_tiny = sorted(set(w for w1, w2, _p in mP + mS for w in (w1, w2)))
    sents, buckets, _c, _prov = INFO.load_corpus_and_buckets()
    tg, lb, pr = SPE._load_frontend()
    scratch_dir = os.path.join(REPO, "data", "%s_selftest_scratch_%d_%d" % (
        ANCHOR_NAME, os.getpid(), time.time_ns()))
    occ = URC.build_occurrence_data(words_tiny, buckets, sents, tg, pr, lb, scratch_dir, "selftest")
    arc = URC.flatten_arc_events(occ, words_tiny)
    stores = {}
    for arm, mode in (("U1_TYPED_CONTEXT", "typed"), ("U3_ROLE_ONLY", "role_only"),
                      ("T2_UNTYPED_SAME_COVERAGE", "neighbour_only")):
        st, dg = URC.store_from_arc_events(arc, words_tiny, mode=mode)
        stores[arm] = (st, dg)
    sc = {arm: (DSI.dense_scores_from_dict_store(st, mP), DSI.dense_scores_from_dict_store(st, mS))
          for arm, (st, dg) in stores.items()}
    for arm, (p_, s_) in sc.items():
        assert len(p_) == len(mP) and len(s_) == len(mS), "score length mismatch for %s" % arm
        assert not np.any(np.isnan(p_)) and not np.any(np.isnan(s_)), \
            "%s produced NaN on the real human slice (word missing from store)" % arm
    ev["real_code_path_three_arms"] = {
        "n_words_tiny": len(words_tiny), "n_arc_events": len(arc),
        "vocab": {arm: dg["vocab_size"] for arm, (st, dg) in stores.items()},
        "aucs_tiny_NOT_A_RESULT": {arm: round(DSI.auc_of(p_, s_), 4) for arm, (p_, s_) in sc.items()}}

    # --- U3 must have the SMALLEST vocab (roles only), U1 the LARGEST (neighbour x role x direction);
    # T2 in between. This is the structural claim that makes U1-vs-U3 and U1-vs-T2 different questions.
    v_u1 = stores["U1_TYPED_CONTEXT"][1]["vocab_size"]
    v_u3 = stores["U3_ROLE_ONLY"][1]["vocab_size"]
    v_t2 = stores["T2_UNTYPED_SAME_COVERAGE"][1]["vocab_size"]
    assert v_u3 <= v_t2 <= v_u1, "vocab ordering must be U3 <= T2 <= U1: %r" % [v_u3, v_t2, v_u1]
    ev["vocab_ordering_known_answer"] = {"U3": v_u3, "T2": v_t2, "U1": v_u1}

    # --- name-collision guard, checked mechanically rather than asserted in prose: the SimpleWiki
    # typed-role cell (whose OWN arm is also called T2_UNTYPED_SAME_COVERAGE) is never imported here,
    # so no arm in this file can possibly be built by TR.collapse_roles / TR.build_typed_role_matrix.
    # (v4 imports TR transitively for ITS harvest, so sys.modules is not the right check -- the right
    # check is that no TR module object is reachable from THIS module's namespace.)
    tr_name = "experiments.exp_typed_role_selectional_asset_writerule_v1"
    bound = sorted(k for k, v in globals().items()
                   if getattr(v, "__name__", None) in (tr_name, tr_name.split(".")[-1]))
    assert not bound, "SimpleWiki typed-role module must not be bound in this module: %r" % bound
    assert "TR" not in globals(), "no TR alias may exist in this module"
    ev["name_collision_guard"] = {"TR_module_bound_here": bound,
                                  "arms_built_only_by": "URC.store_from_arc_events"}

    print("[selftest] ALL PASS", flush=True)
    return ev


# =================================================================================================
# PRE-COMMITTED BRANCH SELECTOR (6.39). Pure function of (auc, ci95, bar) -- no free parameter, no
# renegotiation. Order: (A) clears the bar CI-separated; else (B) at or below chance; else (C) above
# chance and NOT CI-separated from the bar; else the fourth, NOT-pre-committed arithmetic case.
# =================================================================================================
def select_branch(auc: float, ci: Sequence[float], bar: float) -> Tuple[str, str]:
    lo, hi = float(ci[0]), float(ci[1])
    if lo > bar:
        return "A", BRANCH_TEXT_6_39["A"]
    if auc <= CHANCE:
        return "B", BRANCH_TEXT_6_39["B"]
    if lo <= bar <= hi:
        return "C", BRANCH_TEXT_6_39["C"]
    return "D_NOT_PRECOMMITTED", BRANCH_TEXT_6_39["D_NOT_PRECOMMITTED"]


# =================================================================================================
# run
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    out_dir_ckpt = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME + ("_reduced" if grid == "reduced" else ""))
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
                 "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
                 "NO_PRETRAINED_TABLE_IMPORTED": True,
                 "PRECOMMITMENT_SOURCE": "notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md sec 6.39 @ fa5da1d2c",
                 "PRECOMMITTED_BRANCH_TEXT": BRANCH_TEXT_6_39,
                 "NAME_COLLISION_DISCLOSURE": NAME_COLLISION_DISCLOSURE,
                 "ARM_PROVENANCE": ARM_PROVENANCE}

    # ======================= BOTH REGRESSION GATES, v4's OWN FUNCTIONS, EXIT ON FAILURE ============
    print("[gate] running v4's DSI 8-check regression gate (tol=%.4f)" % V4.REG_TOL, flush=True)
    gate_a = V4.dsi_regression_gate()
    rep["REGRESSION_GATE_A_DSI_WORDNET_INSTRUMENT"] = gate_a
    print("[gate] running v4's v3 floors+n=65 regression gate (tol=%.4f)" % V4.REG_TOL, flush=True)
    gate_b_out = V4.v3_regression_gate()
    rep["REGRESSION_GATE_B_V3_HUMAN_INSTRUMENT"] = gate_b_out["gate"]
    rep["BOTH_GATES_PASSED"] = True

    matchedP_full = gate_b_out["matchedP"]
    matchedS_full = gate_b_out["matchedS"]
    existing_full = gate_b_out["existing_arm_scores"]
    cheap_full = gate_b_out["gate"]["measured"]
    n_full = len(matchedP_full)

    if grid == "reduced":
        matchedP, matchedS = matchedP_full[:N_SMOKE_PAIRS], matchedS_full[:N_SMOKE_PAIRS]
    else:
        matchedP, matchedS = matchedP_full, matchedS_full
    n_p, n_s = len(matchedP), len(matchedS)
    rep["N_MATCHED_PAIRS_PER_CELL"] = n_p
    rep["N_MATCHED_PAIRS_PER_CELL_FULL_POPULATION"] = n_full
    words_needed = sorted(set(w for w1, w2, _p in matchedP + matchedS for w in (w1, w2)))
    rep["N_WORDS_NEEDED"] = len(words_needed)
    rep["POS_HISTOGRAM_THIS_POPULATION"] = {
        pos: int(sum(1 for t in matchedP + matchedS if t[2] == pos))
        for pos in sorted(set(t[2] for t in matchedP + matchedS))}
    print("[population] v3's own human population REUSED VERBATIM: n=%d pairs/cell, %d distinct words"
          % (n_p, len(words_needed)), flush=True)

    # ======================= FLOORS RECOMPUTED ON *THIS* POPULATION (never imported) ================
    # v3's cached CHEAP score arrays are the floors' own per-pair scores on this identical population.
    # Gate B already recomputed their point AUCs bit-for-bit; here they additionally get a bootstrap CI
    # + half-width + their own permutation null at this n, and the BAR IS DERIVED from them.
    floors: Dict[str, Dict] = {}
    h3_units = load_units(os.path.join(REPO, "data", "exp_" + V4.H3.ANCHOR_NAME))
    cheap = h3_units[unit_key("SCORES_CHEAP", V4.H3.CODE_VERSION, "full")]
    for i, name in enumerate(sorted(cheap)):
        rec = cheap[name]
        fp = np.asarray(rec["P"], dtype=np.float64)
        fs = np.asarray(rec["S"], dtype=np.float64)
        if grid == "reduced":
            fp, fs = fp[:n_p], fs[:n_s]
        res = DSI.auc_bootstrap(fp, fs, N_BOOT, MASTER_SEED + 5100 + i)
        res["NULL"] = perm_null_auc(fp, fs, N_PERM, MASTER_SEED + 5200 + i)
        res["RECOMPUTED_ON"] = "this population (v3 human, n=%d/cell) -- NOT imported" % n_p
        floors[name] = res
        print("[floor] %-30s AUC=%.4f CI=%r halfwidth=%.4f null_p95=%.4f" % (
            name, res["auc"], res["ci95"], res["ci_halfwidth"], res["NULL"]["null_p95_at_this_n"]),
            flush=True)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = floors

    bar = max(floors[f]["auc"] for f in FLOOR_NAMES)
    bar_owner = max(FLOOR_NAMES, key=lambda f: floors[f]["auc"])
    rep["BAR_MAX_FLOOR_AUC_DERIVED_HERE"] = bar
    rep["BAR_OWNING_FLOOR"] = bar_owner
    rep["BAR_KNOWN_ANSWER_CHECK"] = {
        "prereg_6_39_bar": PREREG_BAR_6_39, "derived_bar": bar,
        "delta": round(bar - PREREG_BAR_6_39, 6), "tol": BAR_KNOWN_ANSWER_TOL,
        "AGREES": bool(grid == "full" and abs(bar - PREREG_BAR_6_39) <= BAR_KNOWN_ANSWER_TOL),
        "note": ("reduced grid truncates the population, so the derived bar legitimately differs "
                 "there; the check is only meaningful at grid=full")}
    print("[bar] DERIVED bar = max(4 floors on THIS population) = %.4f (owner=%s); 6.39 states %.4f"
          % (bar, bar_owner, PREREG_BAR_6_39), flush=True)
    if grid == "full" and abs(bar - PREREG_BAR_6_39) > BAR_KNOWN_ANSWER_TOL:
        print("[bar] WARNING: derived bar disagrees with the pre-registered 0.5943 -- REPORTING THE "
              "DERIVED VALUE AND FLAGGING, not reconciling silently", flush=True)

    # ======================= ARM CONSTRUCTION (source cell's own functions, verbatim) ================
    sents, buckets, _counts, corpus_prov = INFO.load_corpus_and_buckets()
    rep["corpus_provenance"] = corpus_prov
    rep["n_corpus_sentences"] = len(sents)
    print("[corpus] n_sentences=%d" % len(sents), flush=True)

    tg, lb, pr = SPE._load_frontend()
    print("[frontend] pos_tagger/arc_parser/arc_labeler loaded (real persisted assets)", flush=True)
    occ_data = URC.build_occurrence_data(words_needed, buckets, sents, tg, pr, lb, out_dir_ckpt, grid)
    n_occ_total = sum(len(v) for v in occ_data.values())
    n_with_slot = sum(1 for recs in occ_data.values() for r in recs if r["slot"] is not None)
    n_words_no_occ = sum(1 for w in words_needed if not occ_data.get(w))
    rep["OCCURRENCE_DATA_STATS"] = {"n_words": len(occ_data), "n_occurrences_total": n_occ_total,
                                    "n_occurrences_with_slot": n_with_slot,
                                    "frac_with_slot": round(n_with_slot / max(1, n_occ_total), 4),
                                    "n_words_with_zero_occurrences": n_words_no_occ}
    print("[occdata] n_occurrences=%d n_with_slot=%d frac=%.4f words_with_zero_occ=%d" % (
        n_occ_total, n_with_slot, rep["OCCURRENCE_DATA_STATS"]["frac_with_slot"], n_words_no_occ),
        flush=True)

    arc_events = URC.flatten_arc_events(occ_data, words_needed)
    rep["N_ARC_EVENTS_TOTAL"] = len(arc_events)
    print("[arcs] n_arc_events=%d" % len(arc_events), flush=True)

    arm_scores: Dict[str, Dict[str, np.ndarray]] = {}
    arm_diags: Dict[str, Dict] = {}
    for arm, mode in (("U1_TYPED_CONTEXT", "typed"), ("U3_ROLE_ONLY", "role_only"),
                      ("T2_UNTYPED_SAME_COVERAGE", "neighbour_only")):
        t_a = time.time()
        store, diag = URC.store_from_arc_events(arc_events, words_needed, mode=mode)
        arm_scores[arm] = {"P": DSI.dense_scores_from_dict_store(store, matchedP),
                           "S": DSI.dense_scores_from_dict_store(store, matchedS)}
        arm_diags[arm] = diag
        n_nan = int(np.sum(np.isnan(arm_scores[arm]["P"])) + np.sum(np.isnan(arm_scores[arm]["S"])))
        assert n_nan == 0, "%s produced %d NaN scores -- a needed word is missing from its store" % (arm, n_nan)
        print("[arm] %-28s built vocab=%d in %.1fs" % (arm, diag["vocab_size"], time.time() - t_a),
              flush=True)

    # A0 context arm: v3's OWN cached RAW_COUNT_FULL_ACCUM on this identical population, reused
    # bit-for-bit (v3 built its score arrays in its own matchedP/matchedS order, so the pairing that
    # the PAIRED margin needs is preserved).
    a0 = existing_full.get("RAW_COUNT_FULL_ACCUM")
    if a0 is not None and len(a0["P"]) == n_full and len(a0["S"]) == n_full:
        arm_scores["A0_INCUMBENT_HUMAN"] = {"P": a0["P"][:n_p], "S": a0["S"][:n_s]}
        arm_diags["A0_INCUMBENT_HUMAN"] = {"reused_from": "v3 SCORES_EXPENSIVE.RAW_COUNT_FULL_ACCUM"}
    else:
        rep["A0_REUSE_SKIPPED"] = "v3 cached RAW_COUNT_FULL_ACCUM absent or wrong length"

    # ======================= ARMS-MUST-DIFFER (META_RULE_AF) ========================================
    digests = {k: _digest(np.concatenate([v["P"], v["S"]])) for k, v in arm_scores.items()}
    dup: Dict[str, List[str]] = {}
    for k, dg in digests.items():
        dup.setdefault(dg, []).append(k)
    duplicate_groups = {dg: names for dg, names in dup.items() if len(names) > 1}
    rep["ARM_DIGESTS_ARMS_MUST_DIFFER"] = digests
    rep["ARMS_MUST_DIFFER_DUPLICATE_GROUPS"] = duplicate_groups
    assert len(set(digests.values())) > 1, "all arms produced IDENTICAL score vectors -- construction bug"
    if duplicate_groups:
        print("[WARN] bit-identical arm groups: %r" % duplicate_groups, flush=True)

    # ======================= AUC + CI HALF-WIDTH + NULL p95, PER ARM =================================
    auc_results: Dict[str, Dict] = {}
    for i, (name, sc) in enumerate(sorted(arm_scores.items())):
        res = DSI.auc_bootstrap(sc["P"], sc["S"], N_BOOT, MASTER_SEED + 8181 + i)
        res["band_vs_bar"] = band_vs_bar(res["ci95"], bar)
        res["margin_vs_bar"] = round(res["auc"] - bar, 4)
        res["margin_vs_chance"] = round(res["auc"] - CHANCE, 4)
        res["NULL"] = perm_null_auc(sc["P"], sc["S"], N_PERM, MASTER_SEED + 9100 + i)
        res["TIES"] = tie_diagnostics(sc["P"], sc["S"])
        auc_results[name] = res
        print("[auc] %-28s AUC=%.4f CI=%r halfwidth=%.4f null_p95=%.4f band_vs_bar=%s" % (
            name, res["auc"], res["ci95"], res["ci_halfwidth"], res["NULL"]["null_p95_at_this_n"],
            res["band_vs_bar"]), flush=True)
    rep["HUMAN_AUC_PER_ARM"] = auc_results
    rep["ARM_DIAGS"] = arm_diags

    # ======================= PAIRED MARGINS (the decisive comparisons) ==============================
    margins: Dict[str, Dict] = {}
    A = arm_scores["U1_TYPED_CONTEXT"]
    B = arm_scores["U3_ROLE_ONLY"]
    T = arm_scores["T2_UNTYPED_SAME_COVERAGE"]
    margins["U1_vs_U3"] = margin_with_width("U1_TYPED_CONTEXT - U3_ROLE_ONLY",
                                            A["P"], A["S"], B["P"], B["S"], 42)
    margins["U1_vs_T2"] = margin_with_width("U1_TYPED_CONTEXT - T2_UNTYPED_SAME_COVERAGE",
                                            A["P"], A["S"], T["P"], T["S"], 46)
    margins["U3_vs_T2"] = margin_with_width("U3_ROLE_ONLY - T2_UNTYPED_SAME_COVERAGE",
                                            B["P"], B["S"], T["P"], T["S"], 47)
    if "A0_INCUMBENT_HUMAN" in arm_scores:
        Z = arm_scores["A0_INCUMBENT_HUMAN"]
        margins["U1_vs_A0"] = margin_with_width("U1_TYPED_CONTEXT - A0_INCUMBENT_HUMAN",
                                                A["P"], A["S"], Z["P"], Z["S"], 43)
        margins["T2_vs_A0"] = margin_with_width("T2_UNTYPED_SAME_COVERAGE - A0_INCUMBENT_HUMAN",
                                                T["P"], T["S"], Z["P"], Z["S"], 48)
    for k, m in margins.items():
        print("[margin] %-10s diff=%+.4f CI=%r halfwidth=%.4f null_p95_abs=%.4f band=%s" % (
            k, m["point_diff"], m["ci95_diff"], m["ci_halfwidth_diff"],
            m["NULL"]["null_p95_abs_diff_at_this_n"], m["band"]), flush=True)
    rep["PAIRED_MARGINS"] = margins

    # ======================= PRE-COMMITTED BRANCH (6.39) ============================================
    u1 = auc_results["U1_TYPED_CONTEXT"]
    branch, branch_text = select_branch(u1["auc"], u1["ci95"], bar)
    rep["PRECOMMITTED_BRANCH"] = branch
    rep["PRECOMMITTED_BRANCH_QUOTED_TEXT"] = branch_text
    rep["BRANCH_INPUTS"] = {"u1_auc": u1["auc"], "u1_ci95": u1["ci95"],
                            "u1_ci_halfwidth": u1["ci_halfwidth"],
                            "u1_null_p95_at_this_n": u1["NULL"]["null_p95_at_this_n"],
                            "bar_derived": bar, "chance": CHANCE,
                            "u1_margin_vs_bar": u1["margin_vs_bar"]}

    # STOPIF3 on THIS instrument -- mandatory clause of 6.39, attached regardless of branch.
    u1_u3 = margins["U1_vs_U3"]
    stopif3_ties = (u1_u3["band"] == "NOT_SEPARATED")
    rep["STOPIF3_ON_HUMAN_INSTRUMENT"] = {
        "U1_ties_U3": bool(stopif3_ties),
        "paired_diff": u1_u3["point_diff"], "ci95_diff": u1_u3["ci95_diff"],
        "ci_halfwidth_diff": u1_u3["ci_halfwidth_diff"],
        "null_p95_abs_diff": u1_u3["NULL"]["null_p95_abs_diff_at_this_n"],
        "READING": ("U1 TIES U3 ON THE HUMAN INSTRUMENT TOO -- the which-kind-of-slot reading is "
                    "confirmed on BOTH sticks and stops being a one-instrument caveat"
                    if stopif3_ties else
                    "U1 and U3 ARE separated on the human instrument (paired-difference CI excludes "
                    "zero) -- this does NOT retire the WordNet-side STOPIF3, it is a second, "
                    "different population"),
        "WORDNET_SIDE_FOR_REFERENCE_NOT_COMPARED_NUMERICALLY": (
            "on the WordNet instrument U1-U3 = +0.0203 [-0.0185, 0.0591] (STOPIF3 FIRED). Different "
            "population and different scorer input; the two numbers are NOT pooled or compared.")}

    # Power disclosure, mandatory under 6.39 regardless of branch.
    rep["POWER_DISCLOSURE"] = {
        "n_per_cell_here": n_p, "n_per_cell_wordnet_instrument": 242,
        "ratio": round(242.0 / max(1, n_p), 2),
        "u1_ci_halfwidth": u1["ci_halfwidth"],
        "bar_minus_chance": round(bar - CHANCE, 4),
        "halfwidth_exceeds_bar_minus_chance": bool(u1["ci_halfwidth"] > (bar - CHANCE)),
        "statement": ("a CI half-width wider than the entire chance-to-bar interval means the "
                      "instrument cannot resolve a bar-clearing effect at this n at all; report the "
                      "width, never convert it into a capability statement in either direction")}

    rep["POPULATIONS_NOT_COMPARABLE"] = (
        "this instrument's matched population (human judgement, n=%d/cell) and the WordNet "
        "instrument's (n=242/cell) are DIFFERENT, non-overlapping-by-construction pools. Absolute "
        "AUCs are NEVER compared across the two instruments; only within-instrument margins against "
        "within-instrument floors are valid statements." % n_p)
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
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} out={out_dir}", flush=True)

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "MAIN")
    if key in done and key in units:
        rep = units[key]
        print("[cfg] MAIN RESUMED FROM CHECKPOINT", flush=True)
    else:
        rep = run(RUN_MODE)
        record_unit(str(out_dir), key, rep)

    branch = rep.get("PRECOMMITTED_BRANCH", "UNKNOWN")
    u1 = rep["HUMAN_AUC_PER_ARM"]["U1_TYPED_CONTEXT"]
    stop3 = "STOPIF3_TIES" if rep["STOPIF3_ON_HUMAN_INSTRUMENT"]["U1_ties_U3"] else "STOPIF3_SEPARATED"
    verdict = "TYPED_CONTEXT_HUMAN_INSTRUMENT__BRANCH_%s__U1=%.4f_CI%r_halfwidth=%.4f__bar=%.4f__%s" % (
        branch, u1["auc"], u1["ci95"], u1["ci_halfwidth"], rep["BAR_MAX_FLOOR_AUC_DERIVED_HERE"], stop3)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "verdict": verdict,
        "verdict_msg": (
            "Score the CONTEXT cell's U1_TYPED_CONTEXT / U3_ROLE_ONLY / T2_UNTYPED_SAME_COVERAGE on "
            "the HUMAN instrument (v3/v4 population, n=%d/cell, bar derived here = %.4f), both v4 "
            "regression gates re-run, every floor recomputed on this population, CI half-width and "
            "permutation-null p95 beside every margin, U1-vs-U3 read from the paired-difference CI. "
            "Pre-committed branch (6.39) -> %s" % (
                rep["N_MATCHED_PAIRS_PER_CELL"], rep["BAR_MAX_FLOOR_AUC_DERIVED_HERE"], branch)),
        "config": {"MASTER_SEED": MASTER_SEED, "N_BOOT": N_BOOT, "N_PERM": N_PERM,
                   "PREREG_BAR_6_39": PREREG_BAR_6_39, "N_SMOKE_PAIRS": N_SMOKE_PAIRS},
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
