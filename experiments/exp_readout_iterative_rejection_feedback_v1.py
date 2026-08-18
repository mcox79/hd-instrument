"""exp_readout_iterative_rejection_feedback_v1 -- THE DECIDER FOR THE WHOLE READ-OUT ROAD. Does making
generate-and-test ITERATIVE, with rejection FEEDING BACK into the next proposal, buy anything that a
budget-matched one-shot shortlist+rejector does not?

WHY THIS CELL, AND WHY NOW. Seven read-out interventions have landed on this instrument (write-rule
payload, write-rule selection, cue binarisation, shortlist+verifier, and three independent rejector
signals: data/exp_readout_shortlist_verifier_v1/metrics.json,
data/exp_readout_independent_verifier_signals_v1/metrics.json) and EVERY ONE buys roughly +0.01 while
none buys +0.10. THE MEASURED SITUATION this cell exists to break, verified off disk before a line of
this cell was written: partial-cue shortlist hit rate 0.02228 / 0.08838 / 0.14171 / 0.22183 / 0.37581
at k=1/5/10/20/50 (RSV G1_SHORTLIST_ORACLE, PARTIAL_CUE_curve). RECOVERY FRACTION of the best real
rejector (the fraction of gold-in-shortlist items it actually picks) falls from S2_TYPE_VIOLATION_k5
0.37054 to S2_TYPE_VIOLATION_k50 0.11093, against N1_RANDOM_REJECTOR_k5 0.17847 falling to
N1_RANDOM_REJECTOR_k50 0.03931 (data/exp_readout_independent_verifier_signals_v1/metrics.json
.RECOVERY_FRACTION). A SHORT list is one the rejector can handle but usually does not contain the
answer; a LONG list usually contains the answer but the rejector cannot discriminate across it. The two
nearly cancel, which is why every one-shot arm on this instrument lands near 0.02-0.04 regardless of
list length or rejector design.

THE OWNER'S MECHANISM, and the part never built. BOARD Q8, verbatim: "wrong candidates definitely come
up and get rejected. It's often ITERATIVE - if I cant bring up the word at the beginning - I either can
figure it out through thinking it through, or I have to ask someone. I often have a sense of what the
first letter is, but that could just be me." Q12, verbatim: "If I can't remember the word, i'll give up
basically because it's not worth it... Also, if I'm trying to hard to think of a word, it typically
works against me. If I stop thinking about it, often it will come to me later for some reason."
EVERYTHING BUILT SO FAR ON THIS INSTRUMENT IS ONE SHOT. The owner describes ROUNDS, an EXIT CONDITION,
and the observation that PUSHING HARDER MAKES IT WORSE. The scientific content of this cell is whether
REJECTING A CANDIDATE CHANGES THE NEXT PROPOSAL. If round 2 is merely round 1's list with the top item
deleted, that is not iteration -- it is a longer list read in pieces, and it cannot beat the k=50
one-shot arm (the two are the SAME SET examined by the SAME selection rule; this is asserted, not
merely argued, at I1's construction below).

THE COMPUTATION BEING COPIED (problem-derived, not parameter-derived): iterative generate-and-test with
REJECTION FEEDBACK INTO THE NEXT PROPOSAL. THE FEEDBACK, STATED PRECISELY. A prior, interrupted attempt
at this cell (nothing written to disk) proposed Gram-Schmidt cue deflation: when a candidate is
rejected, subtract its direction from the cue before the next round's proposal --
`cue -= (cue . anchor_hat) * anchor_hat`, where `anchor_hat` is the store's own L2-normalised row for
the rejected candidate. This cell adopts that feedback exactly. Concretely, per round r (1-indexed),
for item i with current cue state `cue_{r-1}[i]`:
  1. PROPOSE: score every not-yet-examined eligible anchor by cos(anchor, cue_{r-1}[i]); take the top
     K_PER_ROUND=5 as this round's fresh candidates (`shortlist_mask`, REUSED VERBATIM from RSV,
     restricted to the shrinking "remaining" pool so a candidate is examined at most once).
  2. TEST: score those 5 with the REAL, non-oracle rejector -- R1_ATTESTATION (coordination-pattern
     count over raw sentence text, REUSED VERBATIM from RSV.attestation_scores_for_shortlist; the
     SAME signal RSV and the follow-on cell measured to be independent of the proposer's own cosine at
     r~0.11 and the one signal that beat both G0 and a random pick CI-separated on this instrument).
     The round's WINNER is the attestation argmax within the fresh 5 (I2/I3) or a uniform-random pick
     within the fresh 5 (N1_RANDOM_ITERATIVE, isolating whether a VALIDLY CHOSEN rejection target
     matters or whether cue drift alone would do).
  3. REJECT AND FEED BACK: deflate `cue_{r-1}[i]` by the round winner's direction, producing
     `cue_r[i]`, which is what round r+1 proposes from. The winner is not discarded from the record --
     it becomes part of the CUMULATIVE examined set, and the process's CURRENT BEST GUESS after R
     rounds is always the cumulative attestation-argmax over every candidate examined so far (the same
     tie-corrected scorer, `tools/floor_battery.hit_at_1_both_tie_conventions`, used for every other
     arm on this instrument) -- so a later round CAN displace an earlier correct find if a spurious
     candidate scores higher, which is exactly the mechanism a "pushing harder makes it worse" finding
     would look like if it is real.

ARMS (exact names used as metrics.json / hits_exp keys):
  I0_ONESHOT_BEST_k{K}        the best landed one-shot configuration: RSV's own R1_ATTESTATION_REJECTOR
                               mechanism (shortlist_mask + attestation_scores_for_shortlist, verbatim),
                               evaluated at every K in {5,10,...,50} so every round checkpoint below has
                               a budget-matched one-shot comparator. REGRESSION-GATED against RSV's own
                               landed accuracy at k=5/10/20/50 (0.03056/0.03423/0.03749/0.04093);
                               SystemExit if it does not reproduce.
  I1_ITERATIVE_DELETE_round{R} rounds where a rejected candidate is simply removed (remaining pool
                               shrinks) and the next-best proposer-ranked candidates are taken -- NO cue
                               modification. THE TRIVIAL VERSION. PRE-REGISTERED PREDICTION, written
                               before this run: I1 at round R examines the SAME top-5R proposer-ranked
                               set as I0_ONESHOT_BEST_k(5R) and, using the identical cumulative
                               tie-corrected argmax selection rule, produces a BIT-IDENTICAL result.
                               Checked empirically (not merely asserted) via `np.array_equal` on the
                               winner-index arrays; reported loudly, not fatally, if it fails.
  I2_ITERATIVE_FEEDBACK_round{R} THE ARM THIS CELL EXISTS FOR: I1's loop plus the Gram-Schmidt cue
                               deflation described above, so each round's proposal set genuinely depends
                               on what was rejected before it.
  I3_STOPPING_RULE_round{R}   I2 plus an exit condition. The owner's Q12 describes giving up because
                               continuing "is not worth it", not because of exhaustion -- modelled here
                               as a CONFIDENCE-BASED stop: an item's search FREEZES (stops examining new
                               candidates, cue stops updating) the first time its round-LOCAL best
                               attestation evidence is exactly zero (structurally blind -- no
                               coordination-pattern evidence for ANY of that round's 5 fresh candidates)
                               for GIVEUP_STREAK=2 CONSECUTIVE rounds. I3(R) for R past an item's own
                               stop round is I2's cumulative winner AT the stop round, carried forward --
                               the "gave up, went with the best guess so far" reading of Q12. TOTAL
                               CANDIDATES EXAMINED is therefore VARIABLE PER ITEM; the mean is reported
                               and used to pick I3's own budget-matched I0 comparator (nearest {5..50}
                               grid point to 5*mean_stop_round), per the explicit budget-matching rule
                               below.
  N1_RANDOM_ITERATIVE_round{R} THE FLOOR THAT MATTERS MOST: I2's identical loop (proposal, cue
                               deflation, cumulative attestation-argmax finalisation) but the ROUND
                               WINNER used to choose the deflation direction is picked UNIFORMLY AT
                               RANDOM from the round's fresh 5, not by the rejector. Isolates whether a
                               VALIDLY CHOSEN rejection target matters, independent of cue drift itself.
  G1_SHORTLIST_ORACLE_PARTIAL_k{K} CEILING DIAGNOSTIC ONLY, never a headline: the standard static-list
                               oracle (RCD.hit_at_k_curve, REUSED VERBATIM), reported at every K in
                               {5,10,...,50} to match the round grid.
  K1_KNOWN_ANSWER              BINDING gate: KA_SELF_ADDRESS on the store (exact-key argmax recovers the
                               item's own row), >= 0.95, hard SystemExit before any treatment number, per
                               STOP-IF (v). MUST PASS OR PUBLISH NO QUALITY NUMBER.
  F_ORTHOGRAPHIC / F_FREQUENCY / F_SCRAMBLE / F_CONSTANT_PROTOTYPE
                               all four floors, recomputed on THIS cell's own population, on the PARTIAL
                               cue (F_SCRAMBLE uses Q_part_T; the other three are cue-invariant by
                               construction). Never imported. hit_exp is primary; hit_opt/hit_cons (both
                               tie conventions) also carried per floor.
  SEQ_COVERAGE_I2 / SEQ_COVERAGE_N1_ITER  diagnostic, not an arm: does gold ever enter the CUMULATIVE
                               examined set by round R, for I2's and N1's OWN (feedback-modified)
                               candidate trajectories -- the direct empirical test of whether rejection
                               changes what gets examined at all, compared against the STATIC
                               G1_SHORTLIST_ORACLE_PARTIAL_k(5R) curve.

TOTAL CANDIDATES EXAMINED PER ARM, stated once so no comparison below is void: I0_k(K) examines exactly
K. I1(R) and I2(R) and N1(R) each examine EXACTLY K_PER_ROUND*R = 5R by round R (fixed, no early exit).
I3(R) examines 5*min(stop_round_i, R) PER ITEM (variable); its own mean and the matched-I0-k it implies
are computed and reported explicitly. THE PRIMARY COMPARISON (I2 vs I0) is always made AT THE SAME R,
i.e. I2_round(R) vs I0_ONESHOT_BEST_k(5R) -- an iterative scheme examining 50 candidates over 10 rounds
is compared against a one-shot scheme examining 50, never 5. This is the single easiest way for this
cell to false-positive and is guarded explicitly in STOP_IF below (the "matched_budget" field on every
I2/I3 margin names the exact K it was compared against).

STOP-IF, pre-registered verbatim from the dispatch:
  (i)   I2 clears max(four floors) CI-separated AND beats N1_RANDOM_ITERATIVE CI-separated AND beats
        I0 at MATCHED BUDGET CI-separated -> the first genuine read-out win this programme has had;
        report the level as prominently as the margin, state every control.
  (ii)  I2 ties I1 (NOT_SEPARATED) -> the feedback does nothing and iteration is just a longer list;
        say so plainly.
  (iii) I2 ties I0 at matched budget (NOT_SEPARATED) -> ITERATION IS NOT THE MISSING STRUCTURE, and
        combined with the seven landed interventions the honest reading is that THE READ-OUT DEFICIT IS
        DISTRIBUTED ACROSS THE REPRESENTATION RATHER THAN A SINGLE MISSING COMPONENT. Stated in those
        words verbatim in `verdict_msg` when this fires -- pre-committed, not softened.
  (iv)  accuracy declines with rounds (a peak round < the final round, with the drop not explainable by
        CI noise at that n) -> report the owner's introspection as a measured effect.
  (v)   K1 fails -> INSTRUMENT_STILL_LOOSE, publish nothing (hard SystemExit before any treatment
        number, matching every sibling cell's convention).

MATCH THE BUDGET OR THE COMPARISON IS VOID -- restated as an assertion, not merely a docstring claim:
every I2/I3 margin dict below carries `matched_budget_k`, and `run()` asserts that value equals the R
(or, for I3, the mean-stop-round-derived K) actually used, so a future edit cannot silently compare
across mismatched K without the assertion firing.

BRAIN FIDELITY.
(a) STRUCTURE PER COMPONENT. Generate-then-test with a rejector, iterated with rejection feeding back
    into the next proposal, is PINNED as a control structure by the same literature RSV and the
    follow-on cell cite: tip-of-the-tongue transmission-deficit accounts with REPEATED retrieval
    attempts (Burke & MacKay 1991; Brown & McNeill 1966), and propose-but-verify word learning with
    ITERATIVE refinement (Medina 2011 PNAS; Trueswell 2013). The STOPPING RULE (give up when continuing
    "is not worth it") matches diminishing-returns/cost-of-search accounts of TOT resolution -- searchers
    abandon retrieval attempts as expected utility falls, not on exhaustion (Schwartz & Metcalfe 2011 TOT
    review). The REJECTOR'S CONTENT (R1_ATTESTATION) remains UNPINNED, same standing finding as both
    prior cells: an engineering heuristic standing in for the owner's unbuilt register/feeling channel.
    GRAM-SCHMIDT CUE DEFLATION AS THE FEEDBACK MECHANISM IS OURS, invention under test -- there is no
    claim that the brain performs an orthogonal projection; it is the simplest operation that makes
    "reject this direction" a directional edit to the search cue rather than a list-index bookkeeping
    trick, and it is reported as such, not as biologically pinned. VSA algebraic binding, the
    substrate's core operation, remains UNPINNED in the brain (three live accounts, published
    objections to each; MEMORY.md 2026-08-16 drill); nothing here depends on it.
(b) ORGAN REUSE, enumerated from disk (ls experiments/ filtered on readout/rerank/shortlist/verifier/
    reject/propose/attest/iterative/rounds/feedback/deflat* -- no existing cell operates an iterative
    propose-reject loop with cue feedback on this instrument), then reconciled, verified by RUNTIME
    (sys.modules, recorded in metrics, never grep): experiments.exp_readout_shortlist_verifier_v1
    (shortlist_mask, top1_index, build_attestation_index, attestation_scores_for_shortlist, arm_digest,
    REGRESSION_* constants -- NONE edited), experiments.exp_readout_ceiling_diagnosis_v1
    (build_population, hit_at_k_curve, random_ranking_hit_at_k, install_grounded_similarity_tripwire,
    _halfwidth), experiments.exp_cue_to_store_translation_v1 (cache/aux loaders, ruler gate, MASTER_SEED),
    experiments.exp_cue_binarised_readout_transfer_v1 (pearson_ci_bootstrap),
    experiments.exp_definitional_grounding_v5 (load_corpus_v5), tools.floor_battery (floors, scorer,
    bootstrap), hdlab.reading_grounding_loop (normalize_lemma), tools.exp_checkpoint. NONE edited.
(c) PINNED vs OURS: stated per component in (a).
(d) SHELVE / REVIVAL, BRAIN-FRAMED. If I2 does not win, the revival criterion is NOT "the loop did not
    score" -- the REJECTOR CONTENT (R1_ATTESTATION) is still the same unbuilt-register-channel proxy
    both prior cells named; an iterative loop around a weak rejector inherits the rejector's weakness.
    Revive the ITERATIVE STRUCTURE specifically once a genuine register/feeling rejector signal exists
    (the standing revival criterion from both prior cells), and separately revive GRAM-SCHMIDT FEEDBACK
    specifically only if SEQ_COVERAGE_I2 measurably exceeds the static G1_SHORTLIST_ORACLE_PARTIAL
    curve (i.e. deflation genuinely surfaces candidates a static ranked list would not) -- if it does
    not, the feedback mechanism itself, not just the rejector, is the thing to redesign.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network. The store is NEVER
rebuilt. data/foundation/** is never opened. Writes only under
data/exp_readout_iterative_rejection_feedback_v1{_REDUCED}/. THIS CELL DOES NOT WIRE ANYTHING INTO
hdlab/ EVEN IF IT WINS -- the Director owns the wire-or-shelve call.
"""
from __future__ import annotations

import os

# THREAD PINS -- must precede the numpy import.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_readout_shortlist_verifier_v1 as RSV           # THE LIBRARY, NEVER EDITED
import exp_cue_to_store_translation_v1 as CTS              # cache/aux loaders + ruler gate, NEVER EDITED
import exp_readout_ceiling_diagnosis_v1 as RCD              # build_population/hit_at_k_curve, NEVER EDITED
from tools import floor_battery as FB                       # floors + scorer + bootstrap, NEVER EDITED
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key

ANCHOR_NAME = "exp_readout_iterative_rejection_feedback_v1"
CODE_VERSION = "v1.0"
FINDINGS = "notes/readout_iterative_rejection_feedback_findings_2026-08-17.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. NEVER EDITED AFTER A RUN. --------------------------------------------
MASTER_SEED = RSV.MASTER_SEED
N_BOOT = 2000 if SMOKE else 10000
REGRESSION_TOL = RSV.REGRESSION_TOL
KA_MIN = RSV.KA_MIN
FLOOR_NAMES = RSV.FLOOR_NAMES

K_PER_ROUND = 5                        # candidates proposed per round, matches RSV's own K grid unit
ROUNDS_MAX = 10                        # cumulative budget 5..50, matches RSV's established k=5/10/20/50
ROUND_GRID: Tuple[int, ...] = tuple(range(1, ROUNDS_MAX + 1))
K_GRID: Tuple[int, ...] = tuple(K_PER_ROUND * r for r in ROUND_GRID)     # (5,10,...,50)
GIVEUP_STREAK = 2                      # consecutive zero-evidence rounds -> I3 freezes (Q12 "not worth it")

# ---- REGRESSION-CHECK constants (I0_ONESHOT_BEST must reproduce RSV's own landed R1_ATTESTATION
# ---- numbers; VERIFIED off disk against data/exp_readout_shortlist_verifier_v1/metrics.json .MARGINS
# ---- acc_a fields BEFORE this cell was authored) -----------------------------------------------------
REG_A0_PARTIAL = RSV.REGRESSION_A0_PARTIAL
REG_A1_EXACT_K1 = RSV.REGRESSION_A1_EXACT_K1
REG_A1_EXACT_K5 = RSV.REGRESSION_A1_EXACT_K5
REG_A1_EXACT_K10 = RSV.REGRESSION_A1_EXACT_K10
REG_ADDR_EXACT = RSV.REGRESSION_ADDR_EXACT
REG_FCONST_K1 = RSV.REGRESSION_FCONST_K1
REG_I0_AT_K = {5: 0.03056, 10: 0.03423, 20: 0.03749, 50: 0.04093}    # RSV R1_ATTESTATION_REJECTOR acc_a


def l2n(A: np.ndarray) -> np.ndarray:
    return FB.l2n(A)


def _out_dir() -> str:
    suffix = "" if RUN_MODE == "full" else "_REDUCED"
    return os.path.join(REPO_ROOT, "data", ANCHOR_NAME + suffix)


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1, default=str).encode("utf-8"))
    os.replace(tmp, path)


def _halfwidth(p: float, n: int) -> float:
    return RCD._halfwidth(p, n)


# =======================================================================================================
# NEW PRIMITIVES OWNED BY THIS CELL
# =======================================================================================================
def deflate_cue(cue: np.ndarray, anchor_hat: np.ndarray) -> np.ndarray:
    """Gram-Schmidt deflation, per row: cue -= (cue . anchor_hat) * anchor_hat.

    `cue` [n_items, D], `anchor_hat` [n_items, D] -- ALREADY L2-normalised rows of the store (MATn is
    l2n(mat), so a row gathered from it is unit-norm by construction; not re-normalised here). Returns
    a NEW array; `cue` is never mutated in place, matching the read-out family's standing convention
    that a scoring primitive never mutates its inputs.
    """
    cue = np.asarray(cue, dtype=np.float64)
    ah = np.asarray(anchor_hat, dtype=np.float64)
    dot = np.sum(cue * ah, axis=1, keepdims=True)
    return cue - dot * ah


def simulate_iterative_loop(mode: str, Q_part_T: np.ndarray, MATn: np.ndarray, E_T: np.ndarray,
                            GOLD_T: np.ndarray, Lwords_T_lemma: Sequence[str],
                            anchors_lemma: Sequence[str], pair_counts: Dict[Tuple[str, str], int],
                            rounds_max: int, k_per_round: int, rng_seed: int) -> Dict:
    """The propose/test/reject-and-feed-back loop, shared by I1 (mode="I1", no cue update), I2
    (mode="I2", attestation-guided deflation) and N1_RANDOM_ITERATIVE (mode="N1", random deflation
    target). Every round: propose K_PER_ROUND fresh candidates from the REMAINING eligible pool under
    the CURRENT cue, score them with the REAL attestation rejector (reused verbatim from RSV), merge
    into the cumulative examined set, and (for I2/N1) deflate the cue by the round's winner direction.

    Returns per-round dicts keyed by round number (1..rounds_max):
      hit_exp[r]               [n_items] tie-corrected hit, CUMULATIVE (examined set through round r)
      winner_idx[r]             [n_items] cumulative attestation-argmax winner index through round r
      round_local_best_score[r] [n_items] max attestation score among round r's OWN fresh candidates
                                 (0.0 where no eligible candidate this round) -- the I3 stop signal
      seq_coverage[r]           [n_items] float 0/1, whether gold is in the CUMULATIVE examined set
      n_examined_total[r]       int, k_per_round * r (fixed; identical for every item under this loop)
    """
    if mode not in ("I1", "I2", "N1"):
        raise ValueError("unknown mode %r" % mode)
    n_anchors, n_items = MATn.shape[0], Q_part_T.shape[0]
    remaining = E_T.copy()
    cumulative_shortlist = np.zeros((n_anchors, n_items), dtype=bool)
    cumulative_score = np.zeros((n_anchors, n_items), dtype=np.float32)
    cue_state = np.asarray(Q_part_T, dtype=np.float64).copy()
    rng = np.random.default_rng(rng_seed)

    out: Dict[str, Dict[int, np.ndarray]] = {"hit_exp": {}, "winner_idx": {},
                                              "round_local_best_score": {}, "seq_coverage": {},
                                              "n_examined_total": {}}
    for r in range(1, rounds_max + 1):
        cue_n = l2n(cue_state.astype(np.float32))
        S_r = (MATn @ cue_n.T).astype(np.float32)
        shortlist_r = RSV.shortlist_mask(S_r, remaining, k_per_round)
        remaining = remaining & (~shortlist_r)

        R1_r = RSV.attestation_scores_for_shortlist(shortlist_r, Lwords_T_lemma, anchors_lemma,
                                                     pair_counts)
        local_best = np.where(shortlist_r, R1_r, -np.inf).max(axis=0)
        local_best = np.where(np.isfinite(local_best), local_best, 0.0)
        out["round_local_best_score"][r] = local_best.astype(np.float64)

        cumulative_shortlist |= shortlist_r
        cumulative_score = np.where(shortlist_r, R1_r, cumulative_score)

        if mode in ("I2", "N1"):
            if mode == "I2":
                round_winner = RSV.top1_index(R1_r, shortlist_r)
            else:                                        # N1: uniform-random pick among the fresh 5
                rnd_scores = rng.random((n_anchors, n_items)).astype(np.float32)
                round_winner = RSV.top1_index(rnd_scores, shortlist_r)
            anchor_hat = MATn[round_winner]               # [n_items, D], unit rows by construction
            cue_state = deflate_cue(cue_state, anchor_hat)
        # mode == "I1": no deflation, cue_state never changes -> round r+1 proposes from the SAME
        # static ranking, just excluding what "remaining" has already removed.

        hh = FB.hit_at_1_both_tie_conventions(cumulative_score, cumulative_shortlist, GOLD_T)
        out["hit_exp"][r] = hh["hit_exp"]
        out["winner_idx"][r] = RSV.top1_index(cumulative_score, cumulative_shortlist)
        out["seq_coverage"][r] = (GOLD_T & cumulative_shortlist).any(axis=0).astype(np.float64)
        out["n_examined_total"][r] = k_per_round * r
    return out


def compute_stop_round(round_local_best_score: Dict[int, np.ndarray], rounds_max: int,
                       giveup_streak: int) -> np.ndarray:
    """Per item: the first round r (2<=r<=rounds_max) such that round_local_best_score[r] and every one
    of the giveup_streak-1 rounds before it are exactly 0.0 (no attested evidence at all for that
    round's fresh candidates). rounds_max if the streak never occurs (the item never "gives up")."""
    n_items = round_local_best_score[1].shape[0]
    zero = np.zeros((rounds_max, n_items), dtype=bool)
    for r in range(1, rounds_max + 1):
        zero[r - 1] = round_local_best_score[r] <= 0.0
    stop = np.full(n_items, rounds_max, dtype=np.int64)
    for r in range(giveup_streak, rounds_max + 1):
        streak_ok = np.all(zero[r - giveup_streak:r], axis=0)
        not_yet_stopped = stop == rounds_max
        newly = streak_ok & not_yet_stopped
        stop[newly] = r
    return stop


def i3_answer_at_round(winner_idx: Dict[int, np.ndarray], stop_round: np.ndarray, R: int,
                       n_items: int) -> np.ndarray:
    """I3's cumulative winner at round min(stop_round, R), per item -- I2's own trajectory frozen at
    whichever comes first: the requested checkpoint R, or the item's own give-up round."""
    eff = np.minimum(stop_round, R)
    W = np.stack([winner_idx[r] for r in range(1, int(eff.max()) + 1)], axis=0)  # [max_eff, n_items]
    return W[eff - 1, np.arange(n_items)]


# =======================================================================================================
def self_test() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    ev["RULER_MODE_GATE"] = CTS.ruler_mode_gate()
    ev["tripwire_installed"] = bool(RCD.install_grounded_similarity_tripwire())
    print("[selftest] reusing RSV.self_test() wholesale -- validates every reused primitive "
         "(shortlist_mask, N2-style reduction pattern, attestation index/lookup, pearson_ci_bootstrap, "
         "arm_digest, RCD/RSO self-tests it wraps) ...", flush=True)
    ev["RSV_self_test"] = RSV.self_test()

    # --- deflate_cue: KNOWN ANSWER. Deflating a cue by its OWN direction (unit vector) leaves ZERO;
    # deflating by an ORTHOGONAL direction leaves the cue UNCHANGED; the result is always orthogonal to
    # the anchor it was deflated against. ---------------------------------------------------------------
    rng = np.random.default_rng(5)
    cue = rng.standard_normal((6, 8)).astype(np.float64)
    unit_self = FB.l2n(cue.astype(np.float32)).astype(np.float64)
    out_self = deflate_cue(cue, unit_self)
    assert np.allclose(out_self, 0.0, atol=1e-6), "deflating a cue by its own direction must zero it"
    orth = np.zeros_like(cue)
    orth[:, 0] = 1.0
    cue2 = np.zeros_like(cue)
    cue2[:, 1] = 3.0
    out_orth = deflate_cue(cue2, orth)
    assert np.allclose(out_orth, cue2, atol=1e-9), "deflating by an orthogonal direction must not change the cue"
    cue3 = rng.standard_normal((6, 8)).astype(np.float64)
    ah3 = FB.l2n(rng.standard_normal((6, 8)).astype(np.float32)).astype(np.float64)
    out3 = deflate_cue(cue3, ah3)
    resid_dot = np.sum(out3 * ah3, axis=1)
    assert np.allclose(resid_dot, 0.0, atol=1e-6), "deflated cue must be orthogonal to the deflation direction"
    ev["deflate_cue_known_answer"] = "PASS (self->zero, orthogonal->unchanged, result always orthogonal)"

    # --- simulate_iterative_loop mode I1: KNOWN ANSWER that the incremental union reduces to a single
    # static shortlist call at k=k_per_round*rounds, i.e. I1 must equal I0 bit-for-bit on synthetic data
    # with a real (non-degenerate) proposer score and a real attestation index. ---------------------------
    n_anchors_syn, n_items_syn, D_syn = 40, 12, 5
    rng2 = np.random.default_rng(9)
    mat_syn = rng2.standard_normal((n_anchors_syn, D_syn)).astype(np.float32)
    MATn_syn = FB.l2n(mat_syn)
    Q_syn = rng2.standard_normal((n_items_syn, D_syn)).astype(np.float32)
    E_syn = np.ones((n_anchors_syn, n_items_syn), dtype=bool)
    GOLD_syn = np.zeros((n_anchors_syn, n_items_syn), dtype=bool)
    GOLD_syn[rng2.integers(0, n_anchors_syn, size=n_items_syn), np.arange(n_items_syn)] = True
    anchors_lemma_syn = ["a%d" % i for i in range(n_anchors_syn)]
    Lwords_syn = ["q%d" % i for i in range(n_items_syn)]
    sents_syn = ["a0 and a1 talk", "a2 or a3 argue", "q0 and a5 meet"]
    vocab_syn = set(anchors_lemma_syn) | set(Lwords_syn)
    pc_syn = RSV.build_attestation_index(sents_syn, vocab_syn, lambda w: w, window=4)
    loop_i1 = simulate_iterative_loop("I1", Q_syn, MATn_syn, E_syn, GOLD_syn, Lwords_syn,
                                      anchors_lemma_syn, pc_syn, rounds_max=4, k_per_round=3,
                                      rng_seed=1)
    for r in (1, 2, 3, 4):
        k_here = 3 * r
        sl_static = RSV.shortlist_mask((MATn_syn @ FB.l2n(Q_syn).T).astype(np.float32), E_syn, k_here)
        R1_static = RSV.attestation_scores_for_shortlist(sl_static, Lwords_syn, anchors_lemma_syn, pc_syn)
        h_static = FB.hit_at_1_both_tie_conventions(R1_static, sl_static, GOLD_syn)
        assert np.array_equal(loop_i1["hit_exp"][r], h_static["hit_exp"]), (
            "I1's cumulative loop did NOT reduce to a single static shortlist at k=%d on synthetic "
            "data -- the incremental-union identity does not hold as implemented" % k_here)
    ev["I1_reduces_to_static_shortlist_known_answer"] = "PASS (rounds 1..4, k=3,6,9,12)"

    # --- simulate_iterative_loop mode I2: KNOWN ANSWER that deflation actually CHANGES which candidate
    # is examined in a later round, on a case constructed so it must. Two anchors, b0 and b1, are BOTH
    # highly similar to the cue's dominant direction; b0 is examined round 1 (proposer's top pick).
    # Deflating the cue by b0's own direction must remove b0's contribution to the score of everything
    # ELSE that shares that direction, in particular reordering who is proposed next relative to the
    # UNDEFLATED (I1) ranking. -----------------------------------------------------------------------
    # D=3. cue=(1,0,c), b0=(1,0,0) [round-1 winner, unambiguous], b1=(1,0,d) with d=3c [near-collinear
    # with b0, wins round 2 under the STATIC (I1) cue], b2=(0,1,1) [orthogonal-ish, loses round 2
    # under the static cue but WINS under the cue deflated by b0's direction, because the deflated
    # residual is pure e2 and b2 has a much larger e2 component than b1 does]. Values chosen and
    # verified algebraically (see docstring derivation) so round 1 is unambiguous and round 2 flips.
    c, d = 0.1, 0.3
    cue_kn = np.array([[1.0, 0.0, c]], dtype=np.float32)
    b0 = np.array([1.0, 0.0, 0.0])
    b1 = np.array([1.0, 0.0, d])
    b2 = np.array([0.0, 1.0, 1.0])
    mat_kn = np.stack([b0, b1, b2]).astype(np.float32)
    MATn_kn = FB.l2n(mat_kn)
    E_kn = np.ones((3, 1), dtype=bool)
    GOLD_kn = np.zeros((3, 1), dtype=bool)
    GOLD_kn[2, 0] = True                              # b2 is gold
    anchors_kn = ["b0", "b1", "b2"]
    Lwords_kn = ["query0"]
    # b0 carries NO attestation evidence with query0 (absent from the dict -> scores exactly 0, same
    # "structurally blind" convention as the real rejector); b1 and b2 BOTH carry positive evidence, so
    # whichever of them is PROPOSED in round 2 becomes the cumulative winner over b0's 0 -- this makes
    # winner_idx at round 2 report the ROUND-2 PROPOSAL identity cleanly, without a tie at 0 masking it.
    pc_kn = {("b1", "query0"): 5, ("b2", "query0"): 5}
    loop_i2_kn = simulate_iterative_loop("I2", cue_kn, MATn_kn, E_kn, GOLD_kn, Lwords_kn, anchors_kn,
                                         pc_kn, rounds_max=2, k_per_round=1, rng_seed=2)
    loop_i1_kn = simulate_iterative_loop("I1", cue_kn, MATn_kn, E_kn, GOLD_kn, Lwords_kn, anchors_kn,
                                         pc_kn, rounds_max=2, k_per_round=1, rng_seed=2)
    r1_i1, r2_i1 = int(loop_i1_kn["winner_idx"][1][0]), int(loop_i1_kn["winner_idx"][2][0])
    r1_i2, r2_i2 = int(loop_i2_kn["winner_idx"][1][0]), int(loop_i2_kn["winner_idx"][2][0])
    assert r1_i1 == 0 and r1_i2 == 0, (
        "round-1 winner must be b0 (unambiguous top cosine) in both modes: I1=%d I2=%d" % (r1_i1, r1_i2))
    # I1 (static, no deflation): round 2 examines {b1,b2} under the UNCHANGED cue -> picks b1 (the
    # near-collinear-with-b0 candidate), same as a plain top-2 read of the original ranking.
    assert r2_i1 == 1, "I1 round-2 winner must be b1 (static ranking, no feedback): got %d" % r2_i1
    # I2 (Gram-Schmidt feedback): after b0 is rejected and deflated out, the residual cue is pure e2 --
    # b1's e2 component is small (d=0.3) but b2's is large (1.0), so REJECTING b0 changes who looks
    # best next: b2 overtakes b1. This is the mechanism claim made numerically checkable.
    assert r2_i2 == 2, ("I2 round-2 winner must be b2 (feedback changed the proposal): got %d -- "
                        "KNOWN-ANSWER CONSTRUCTION FAILED TO DEMONSTRATE A DIFFERENCE" % r2_i2)
    ev["I2_deflation_changes_next_proposal_known_answer"] = {
        "round1_winner_both_modes": r1_i1, "I1_round2_static_pick": r2_i1, "I2_round2_deflated_pick": r2_i2,
        "PASS": "deflation demonstrably changes the next round's proposal, from the wrong candidate "
               "(I1) to the gold candidate (I2), on a constructed case"}

    # --- compute_stop_round: KNOWN ANSWER on a hand-built zero/nonzero evidence trace. ------------------
    trace = {1: np.array([1.0, 0.0, 5.0]), 2: np.array([0.0, 0.0, 0.0]),
             3: np.array([2.0, 0.0, 0.0]), 4: np.array([0.0, 0.0, 3.0])}
    stop = compute_stop_round(trace, rounds_max=4, giveup_streak=2)
    # item0: evidence at r1, zero r2, evidence r3, zero r4 -- never TWO consecutive zeros -> never stops (=4)
    # item1: zero at every round from r1 -- first 2-consecutive-zero window ends at r2 -> stops at 2
    # item2: evidence r1, zero r2, zero r3, evidence r4 -- 2-consecutive-zero (r2,r3) ends at r3 -> stops at 3
    assert list(stop) == [4, 2, 3], "compute_stop_round wrong: got %r, expected [4, 2, 3]" % list(stop)
    ev["compute_stop_round_known_answer"] = {"stop_rounds": [int(x) for x in stop], "PASS": True}

    # --- i3_answer_at_round: KNOWN ANSWER that frozen items carry their stop-round winner forward. ------
    widx = {1: np.array([9, 9, 9]), 2: np.array([1, 8, 8]), 3: np.array([1, 8, 7]),
            4: np.array([1, 8, 7])}
    stop2 = np.array([4, 2, 3])
    a_r2 = i3_answer_at_round(widx, stop2, 2, 3)
    a_r4 = i3_answer_at_round(widx, stop2, 4, 3)
    # at R=2: item0 (stop=4, still ACTIVE) shows round2's CURRENT cumulative winner (1), not a stale
    # round-1 value; item1 (stop=2) is frozen exactly at round2 (8); item2 (stop=3, still active at
    # R=2) also shows round2's current winner (8).
    assert list(a_r2) == [1, 8, 8], "i3_answer_at_round wrong at R=2: %r" % list(a_r2)
    assert list(a_r4) == [1, 8, 7], "i3_answer_at_round wrong at R=4: %r" % list(a_r4)
    assert a_r4[1] == a_r2[1] == 8, "item1 (stop_round=2) must carry the SAME winner forward to R=4"
    ev["i3_answer_at_round_known_answer"] = "PASS (frozen items carry forward, active items keep updating)"

    print("[selftest] ALL PASS", flush=True)
    return ev


# =======================================================================================================
def run(grid: str, output_dir: str) -> Dict:
    t0 = time.time()
    _gate = CTS.ruler_mode_gate()
    _tripwire = RCD.install_grounded_similarity_tripwire()
    P = RCD.build_population()
    C, mat, mat_ok = P["C"], P["mat"], P["mat_ok"]
    n_anchors, qidx = P["n_anchors"], P["qidx"]
    GOLD, E, keep_ALL = P["GOLD"], P["E"], P["keep"]
    anchors = P["anchors"]
    MATn = l2n(mat)

    rep: Dict = {
        "anchor_name": ANCHOR_NAME, "grid": grid, "code_version": CODE_VERSION,
        "findings_log": FINDINGS, "NO_LLM_IN_OPERATIONAL_FLOW": True,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
        "RULER_MODE_GATE": _gate, "GROUNDED_SIMILARITY_TRIPWIRE_INSTALLED": bool(_tripwire),
        "feedback_definition": {
            "what_is_fed_back": "Gram-Schmidt cue deflation: cue -= (cue . anchor_hat) * anchor_hat, "
                                "where anchor_hat is the store's own L2-normalised row for the round's "
                                "REJECTED candidate (the attestation-rejector's argmax within that "
                                "round's fresh K_PER_ROUND=5 proposer-ranked candidates for I2/I3, or "
                                "a uniform-random pick among them for N1_RANDOM_ITERATIVE). I1 applies "
                                "no cue update at all.",
            "K_PER_ROUND": K_PER_ROUND, "ROUNDS_MAX": ROUNDS_MAX, "K_GRID": list(K_GRID),
            "GIVEUP_STREAK": GIVEUP_STREAK},
    }

    # =====================================================================================================
    # REGRESSION GATES -- ALWAYS on the FULL population, regardless of --grid. Reuses RSV's own constants.
    # =====================================================================================================
    T_full = np.flatnonzero(keep_ALL)
    S_part_full = (MATn @ l2n(C["Q_part"]).T).astype(np.float32)
    h0 = FB.hit_at_1_both_tie_conventions(S_part_full, E, GOLD)
    m0 = h0["scored"] & keep_ALL
    a0 = float(h0["hit_exp"][m0].mean())
    del h0
    S_ex_full = (MATn @ l2n(C["Q_exact"]).T).astype(np.float32)
    curve_full = RCD.hit_at_k_curve(S_ex_full, E, GOLD, (1, 5, 10))
    opt_full = curve_full["hit_at_k"]["opt"]
    a1_k1 = float(opt_full[1][T_full].mean())
    a1_k5 = float(opt_full[5][T_full].mean())
    a1_k10 = float(opt_full[10][T_full].mean())
    addr_full = float(np.mean(np.argmax(S_ex_full, axis=0)[keep_ALL & (qidx >= 0)]
                              == qidx[keep_ALL & (qidx >= 0)]))
    const_vec_full = FB.constant_prototype_floor(mat, mat_ok)
    Sconst_full = FB.as_constant_matrix(const_vec_full, C["Q_exact"].shape[0])
    hconst = FB.hit_at_1_both_tie_conventions(Sconst_full, E, GOLD)
    fconst_k1 = float(hconst["hit_exp"][T_full].mean())
    del curve_full, opt_full, hconst, Sconst_full

    reg = {
        "partial_cue_hit1_FULL_POP": round(a0, 5), "expected": REG_A0_PARTIAL,
        "exact_key_hit1_FULL_POP": round(a1_k1, 5), "expected_k1": REG_A1_EXACT_K1,
        "exact_key_hit5_FULL_POP": round(a1_k5, 5), "expected_k5": REG_A1_EXACT_K5,
        "exact_key_hit10_FULL_POP": round(a1_k10, 5), "expected_k10": REG_A1_EXACT_K10,
        "exact_key_addressing_FULL_POP": round(addr_full, 5), "expected_addr": REG_ADDR_EXACT,
        "F_CONSTANT_PROTOTYPE_hit1_FULL_POP": round(fconst_k1, 5), "expected_fconst": REG_FCONST_K1,
        "tol": REGRESSION_TOL, "n_full": int(T_full.size),
        "source": "VERIFIED against data/exp_readout_shortlist_verifier_v1/metrics.json BEFORE this "
                  "cell was authored; regression constants imported from RSV's own module.",
    }
    reg["PASS"] = bool(
        abs(a0 - REG_A0_PARTIAL) <= REGRESSION_TOL and abs(a1_k1 - REG_A1_EXACT_K1) <= REGRESSION_TOL
        and abs(a1_k5 - REG_A1_EXACT_K5) <= REGRESSION_TOL
        and abs(a1_k10 - REG_A1_EXACT_K10) <= REGRESSION_TOL
        and abs(addr_full - REG_ADDR_EXACT) <= REGRESSION_TOL
        and abs(fconst_k1 - REG_FCONST_K1) <= REGRESSION_TOL)
    rep["REGRESSION_GATE"] = reg
    if not reg["PASS"]:
        raise SystemExit("REGRESSION GATE FAILED -- not the landed instrument: %r" % reg)
    print("[regression] partial=%.5f exact1=%.5f exact5=%.5f exact10=%.5f addr=%.5f fconst=%.5f "
         "ALL PASS t=%.0fs" % (a0, a1_k1, a1_k5, a1_k10, addr_full, fconst_k1, time.time() - t0),
         flush=True)
    del S_part_full, S_ex_full

    # =====================================================================================================
    # POPULATION FOR THE SWEEP -- T is reduced to 400 items under --grid reduced (smoke)
    # =====================================================================================================
    items = T_full.copy()
    if grid == "reduced":
        items = items[:400]
    T = items
    n_items = int(T.size)
    GOLD_T = GOLD[:, T].copy()
    E_T = E[:, T].copy()
    qidx_T = qidx[T]
    Q_exact_T = C["Q_exact"][T]
    Q_part_T = C["Q_part"][T]
    L_words_T = [C["L_words"][int(t)] for t in T]
    rep["population"] = {
        "n_anchors": n_anchors, "n_items_scored": n_items,
        "pool": "the LANDED OPEN pool, identical to RSV/the follow-on cell",
        "gold": "WordNet 3.0 generous meaning set, exp_grounding_readout_known_answer_v1 UNMODIFIED",
        "scorer": "tools/floor_battery.hit_at_1_both_tie_conventions, tie-corrected primary",
        "cue_regime_primary": "PARTIAL CUE (the real regime) for every proposal in every round",
    }
    S_ex_T = (MATn @ l2n(Q_exact_T).T).astype(np.float32)
    S_part_T = (MATn @ l2n(Q_part_T).T).astype(np.float32)
    print("[load] n_anchors=%d n_items=%d t=%.0fs" % (n_anchors, n_items, time.time() - t0), flush=True)

    # ---- K1_KNOWN_ANSWER -- BINDING GATE. Must pass or publish no quality number (STOP-IF v). -----------
    ok_q = qidx_T >= 0
    ka = float(np.mean(np.argmax(S_ex_T, axis=0)[ok_q] == qidx_T[ok_q]))
    rng_perm = np.random.default_rng(MASTER_SEED + 2201)
    perm = np.arange(n_items)
    for _ in range(64):
        perm = rng_perm.permutation(n_items)
        if np.all(perm != np.arange(n_items)):
            break
    h_null = FB.hit_at_1_both_tie_conventions(S_ex_T[:, perm], E_T, GOLD_T)
    null_hit = float(h_null["hit_exp"][h_null["scored"]].mean())
    null_addr = float(np.mean(np.argmax(S_ex_T[:, perm], axis=0)[ok_q] == qidx_T[ok_q]))
    rep["VALIDITY"] = {
        "KA_SELF_ADDRESS": {"value": round(ka, 4), "gate": KA_MIN, "PASS": bool(ka >= KA_MIN)},
        "NULL_PERMUTED": {"hit_at_1_tie_corrected": round(null_hit, 6), "addressing": round(null_addr, 8),
                          "chance_addressing": round(1.0 / n_anchors, 8),
                          "binom_ci_halfwidth_at_null_hit": round(_halfwidth(null_hit, n_items), 6)},
    }
    rep["K1_KNOWN_ANSWER"] = {"BINDING_GATE": "KA_SELF_ADDRESS on the store (>= %.2f): %.4f" % (KA_MIN, ka),
                              "PASS": bool(ka >= KA_MIN)}
    if ka < KA_MIN:
        rep["verdict"] = "STOPIF_V__INSTRUMENT_STILL_LOOSE__K1_KNOWN_ANSWER_FAILED"
        rep["verdict_msg"] = "KA_SELF_ADDRESS=%.4f < %.2f -- no treatment number is read/published." % (
            ka, KA_MIN)
        rep["summary"] = rep["verdict"]
        rep["elapsed_s"] = round(time.time() - t0, 1)
        rep["run_mode"] = "full" if grid == "full" else "smoke"
        _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
        raise SystemExit("K1 KNOWN-ANSWER ARM FAILED (%.4f < %.2f) -- INSTRUMENT_STILL_LOOSE, "
                         "publishing no quality number" % (ka, KA_MIN))
    print("[validity] KA_self_address=%.4f NULL_hit=%.6f NULL_addr=%.8f" % (ka, null_hit, null_addr),
         flush=True)

    # =====================================================================================================
    # FLOORS -- recomputed on THIS population, on the PARTIAL cue. Both tie conventions carried.
    # =====================================================================================================
    aux = P["aux"]
    floors_S: Dict[str, np.ndarray] = {}
    try:
        floors_S["F_ORTHOGRAPHIC"] = (l2n(aux["t_mat"]) @ l2n(aux["Tq"][T]).T).astype(np.float32)
    except Exception as exc:
        rep.setdefault("FLOOR_NOTES", {})["F_ORTHOGRAPHIC"] = "UNAVAILABLE: %r" % (exc,)
    try:
        floors_S["F_FREQUENCY"] = FB.as_constant_matrix(
            FB.frequency_floor(np.asarray(aux["fq"], dtype=np.float64)), n_items)
    except Exception as exc:
        rep.setdefault("FLOOR_NOTES", {})["F_FREQUENCY"] = "UNAVAILABLE: %r" % (exc,)
    floors_S["F_SCRAMBLE"] = (l2n(FB.scramble_null(mat, MASTER_SEED + 2211)) @ l2n(Q_part_T).T
                              ).astype(np.float32)
    const_floor_vec = FB.constant_prototype_floor(mat, mat_ok)
    floors_S["F_CONSTANT_PROTOTYPE"] = FB.as_constant_matrix(const_floor_vec, n_items)
    oracle_S = FB.as_constant_matrix(
        FB.oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD_T[:, i]) for i in range(n_items)]),
        n_items)

    hits_exp: Dict[str, np.ndarray] = {}
    winner_idx_final: Dict[str, np.ndarray] = {}   # for ARMS_MUST_DIFFER, selection identity

    def add_score_matrix_arm(name: str, Sx: np.ndarray, elig: np.ndarray, track_winner: bool = False
                             ) -> Dict:
        hh = FB.hit_at_1_both_tie_conventions(Sx, elig, GOLD_T)
        hits_exp[name] = hh["hit_exp"]
        if track_winner:
            winner_idx_final[name] = RSV.top1_index(Sx, elig)
        return hh

    floor_detail: Dict[str, Dict] = {}
    for f_name, Sf in floors_S.items():
        hh = add_score_matrix_arm(f_name, Sf, E_T)
        floor_detail[f_name] = {"hit_exp": round(float(hh["hit_exp"].mean()), 5),
                                "hit_opt": round(float(hh["hit_opt"].mean()), 5),
                                "hit_cons": round(float(hh["hit_cons"].mean()), 5)}
    add_score_matrix_arm("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", oracle_S, E_T)
    rep["FLOORS_RECOMPUTED_ON_THIS_POPULATION"] = {
        "cue": "PARTIAL", "detail_both_tie_conventions": floor_detail,
        "never_imported": ["0.1390", "0.1715", "0.2604", "0.3758", "0.0873", "0.1382", "0.2070",
                          "-0.1959"]}
    print("[floors] " + json.dumps({k: v["hit_exp"] for k, v in floor_detail.items()}), flush=True)

    # =====================================================================================================
    # THE ATTESTATION INDEX -- built once, cue-independent (word identity + raw corpus text only).
    # =====================================================================================================
    from experiments.exp_definitional_grounding_v5 import load_corpus_v5
    from hdlab.reading_grounding_loop import normalize_lemma
    t_att0 = time.time()
    sents = [s for _seg, s in load_corpus_v5(None, lineaware=True)]
    anchors_lemma = [normalize_lemma(a) for a in anchors]
    Lwords_T_lemma = [normalize_lemma(w) for w in L_words_T]
    vocab_set = set(anchors_lemma) | set(Lwords_T_lemma)
    pair_counts = RSV.build_attestation_index(sents, vocab_set, normalize_lemma, window=RSV.COORD_WINDOW)
    rep["ATTESTATION_INDEX"] = {"n_sentences": len(sents), "n_vocab": len(vocab_set),
                                "n_pairs_attested": len(pair_counts), "window_tokens": RSV.COORD_WINDOW,
                                "build_t_s": round(time.time() - t_att0, 1)}
    print("[attestation] %d sentences -> %d attested coordination pairs t=%.0fs"
         % (len(sents), len(pair_counts), time.time() - t_att0), flush=True)
    del sents

    # =====================================================================================================
    # G1_SHORTLIST_ORACLE_PARTIAL -- CEILING DIAGNOSTIC ONLY, at every K in K_GRID.
    # =====================================================================================================
    n_elig = E_T.sum(axis=0).astype(np.float64)
    n_gold = (GOLD_T & E_T).sum(axis=0).astype(np.float64)
    rr = RCD.random_ranking_hit_at_k(n_elig, n_gold, K_GRID)
    curve_partial = RCD.hit_at_k_curve(S_part_T, E_T, GOLD_T, K_GRID)
    g1_partial: Dict[int, float] = {}
    for k in K_GRID:
        arr = curve_partial["hit_at_k"]["opt"][k].astype(np.float64)
        hits_exp["G1_SHORTLIST_ORACLE_PARTIAL_k%d" % k] = arr
        hits_exp["RANDOM_RANKING_NULL_PARTIAL_k%d" % k] = rr[k]
        g1_partial[k] = float(arr.mean())
    rep["G1_SHORTLIST_ORACLE_PARTIAL_CEILING"] = {str(k): round(v, 5) for k, v in g1_partial.items()}
    print("[G1] PARTIAL k=%s" % {k: round(v, 4) for k, v in g1_partial.items()}, flush=True)

    # =====================================================================================================
    # I0_ONESHOT_BEST -- RSV's own R1_ATTESTATION_REJECTOR mechanism, at every K in K_GRID. REGRESSION-
    # CHECKED against RSV's own landed numbers.
    # =====================================================================================================
    i0_acc: Dict[int, float] = {}
    for k in K_GRID:
        sl = RSV.shortlist_mask(S_part_T, E_T, k)
        R1_k = RSV.attestation_scores_for_shortlist(sl, Lwords_T_lemma, anchors_lemma, pair_counts)
        hh = add_score_matrix_arm("I0_ONESHOT_BEST_k%d" % k, R1_k, sl, track_winner=True)
        i0_acc[k] = float(hh["hit_exp"].mean())
        record_unit(output_dir, unit_key("I0", k), {"acc": round(i0_acc[k], 5)})
    i0_regcheck = {k: {"got": round(i0_acc[k], 5), "expected": v, "delta": round(i0_acc[k] - v, 5)}
                  for k, v in REG_I0_AT_K.items()}
    i0_reg_pass = all(abs(v["delta"]) <= REGRESSION_TOL for v in i0_regcheck.values())
    rep["I0_ONESHOT_BEST_REGRESSION_CHECK"] = {
        "detail": i0_regcheck, "PASS": i0_reg_pass, "enforced": grid == "full",
        "source": "RSV MARGINS acc_a for R1_ATTESTATION_REJECTOR_k{5,10,20,50}, verified off disk "
                  "before this cell was authored. Only ENFORCED (SystemExit on fail) on --grid full: "
                  "RSV's own numbers were computed on the FULL n=3994 population, so a --grid reduced "
                  "(n=400) run cannot be expected to reproduce them and this check is informational "
                  "there, matching how the population-level REGRESSION_GATE above is itself always "
                  "computed on the full population regardless of --grid."}
    if grid == "full" and not i0_reg_pass:
        raise SystemExit("I0_ONESHOT_BEST does not reproduce RSV's own landed R1_ATTESTATION_REJECTOR "
                         "numbers -- not the landed instrument: %r" % i0_regcheck)
    print("[I0] acc=%s ALL REGRESSION CHECKS PASS t=%.0fs"
         % ({k: round(v, 4) for k, v in i0_acc.items()}, time.time() - t0), flush=True)

    # =====================================================================================================
    # THE THREE SIMULATED LOOPS: I1 (trivial/no feedback), I2 (Gram-Schmidt feedback), N1_RANDOM_ITERATIVE
    # (feedback with a random rejection target). Each produces per-round cumulative curves.
    # =====================================================================================================
    t_loop0 = time.time()
    loop_I1 = simulate_iterative_loop("I1", Q_part_T, MATn, E_T, GOLD_T, Lwords_T_lemma, anchors_lemma,
                                      pair_counts, ROUNDS_MAX, K_PER_ROUND, MASTER_SEED + 2301)
    print("[loop I1] done t=%.0fs" % (time.time() - t_loop0), flush=True)
    t_loop1 = time.time()
    loop_I2 = simulate_iterative_loop("I2", Q_part_T, MATn, E_T, GOLD_T, Lwords_T_lemma, anchors_lemma,
                                      pair_counts, ROUNDS_MAX, K_PER_ROUND, MASTER_SEED + 2311)
    print("[loop I2] done t=%.0fs" % (time.time() - t_loop1), flush=True)
    t_loop2 = time.time()
    loop_N1 = simulate_iterative_loop("N1", Q_part_T, MATn, E_T, GOLD_T, Lwords_T_lemma, anchors_lemma,
                                      pair_counts, ROUNDS_MAX, K_PER_ROUND, MASTER_SEED + 2321)
    print("[loop N1] done t=%.0fs" % (time.time() - t_loop2), flush=True)

    i1_i0_equal: Dict[int, bool] = {}
    per_round_curves: Dict[str, Dict[int, float]] = {"I1_ITERATIVE_DELETE": {}, "I2_ITERATIVE_FEEDBACK": {},
                                                      "N1_RANDOM_ITERATIVE": {}}
    seq_coverage_curves: Dict[str, Dict[int, float]] = {"I2_ITERATIVE_FEEDBACK": {},
                                                         "N1_RANDOM_ITERATIVE": {}}
    recovery_curves: Dict[str, Dict[int, Optional[float]]] = {"I1_ITERATIVE_DELETE": {},
                                                               "I2_ITERATIVE_FEEDBACK": {},
                                                               "N1_RANDOM_ITERATIVE": {}}
    for r in ROUND_GRID:
        k_here = K_PER_ROUND * r
        name_i1 = "I1_ITERATIVE_DELETE_round%d" % r
        name_i2 = "I2_ITERATIVE_FEEDBACK_round%d" % r
        name_n1 = "N1_RANDOM_ITERATIVE_round%d" % r
        hits_exp[name_i1] = loop_I1["hit_exp"][r]
        hits_exp[name_i2] = loop_I2["hit_exp"][r]
        hits_exp[name_n1] = loop_N1["hit_exp"][r]
        winner_idx_final[name_i1] = loop_I1["winner_idx"][r]
        winner_idx_final[name_i2] = loop_I2["winner_idx"][r]
        winner_idx_final[name_n1] = loop_N1["winner_idx"][r]

        i1_i0_equal[r] = bool(np.array_equal(loop_I1["winner_idx"][r], winner_idx_final["I0_ONESHOT_BEST_k%d" % k_here]))
        per_round_curves["I1_ITERATIVE_DELETE"][r] = round(float(loop_I1["hit_exp"][r].mean()), 5)
        per_round_curves["I2_ITERATIVE_FEEDBACK"][r] = round(float(loop_I2["hit_exp"][r].mean()), 5)
        per_round_curves["N1_RANDOM_ITERATIVE"][r] = round(float(loop_N1["hit_exp"][r].mean()), 5)
        seq_coverage_curves["I2_ITERATIVE_FEEDBACK"][r] = round(float(loop_I2["seq_coverage"][r].mean()), 5)
        seq_coverage_curves["N1_RANDOM_ITERATIVE"][r] = round(float(loop_N1["seq_coverage"][r].mean()), 5)
        ceiling = g1_partial[k_here]
        recovery_curves["I1_ITERATIVE_DELETE"][r] = round(per_round_curves["I1_ITERATIVE_DELETE"][r]
                                                           / ceiling, 5) if ceiling > 0 else None
        recovery_curves["I2_ITERATIVE_FEEDBACK"][r] = round(per_round_curves["I2_ITERATIVE_FEEDBACK"][r]
                                                             / ceiling, 5) if ceiling > 0 else None
        recovery_curves["N1_RANDOM_ITERATIVE"][r] = round(per_round_curves["N1_RANDOM_ITERATIVE"][r]
                                                           / ceiling, 5) if ceiling > 0 else None
        record_unit(output_dir, unit_key("LOOP", r), {
            "I1": per_round_curves["I1_ITERATIVE_DELETE"][r], "I2": per_round_curves["I2_ITERATIVE_FEEDBACK"][r],
            "N1": per_round_curves["N1_RANDOM_ITERATIVE"][r], "I1_eq_I0": i1_i0_equal[r]})
        print("[round %d, budget=%d] I0=%.4f I1=%.4f(eqI0=%s) I2=%.4f N1=%.4f seqcov_I2=%.4f "
             "seqcov_N1=%.4f G1ceiling=%.4f t=%.0fs"
             % (r, k_here, i0_acc[k_here], per_round_curves["I1_ITERATIVE_DELETE"][r], i1_i0_equal[r],
                per_round_curves["I2_ITERATIVE_FEEDBACK"][r], per_round_curves["N1_RANDOM_ITERATIVE"][r],
                seq_coverage_curves["I2_ITERATIVE_FEEDBACK"][r], seq_coverage_curves["N1_RANDOM_ITERATIVE"][r],
                ceiling, time.time() - t0), flush=True)

    rep["I1_EQUALS_I0_AT_MATCHED_BUDGET"] = {
        "per_round": i1_i0_equal, "ALL_EQUAL": bool(all(i1_i0_equal.values())),
        "prediction": "I1 at round R examines the identical top-(5R) proposer-ranked set as "
                     "I0_ONESHOT_BEST_k(5R) and, using the same cumulative tie-corrected argmax "
                     "selection rule, must produce a bit-identical winner. Checked via np.array_equal, "
                     "reported (not fatal) if it fails.",
    }
    if not rep["I1_EQUALS_I0_AT_MATCHED_BUDGET"]["ALL_EQUAL"]:
        print("[LOUD] I1 DOES NOT EQUAL I0 at matched budget for rounds: %r"
             % [r for r, ok in i1_i0_equal.items() if not ok], flush=True)

    rep["PER_ROUND_ACCURACY_CURVES"] = per_round_curves
    rep["PER_ROUND_RECOVERY_FRACTION_CURVES"] = recovery_curves
    rep["PER_ROUND_SEQUENCE_COVERAGE_CURVES"] = seq_coverage_curves
    rep["I0_ONESHOT_BEST_ACCURACY_BY_K"] = {str(k): round(v, 5) for k, v in i0_acc.items()}
    rep["TOTAL_CANDIDATES_EXAMINED"] = {
        "I0_ONESHOT_BEST_k{K}": "exactly K", "I1_ITERATIVE_DELETE_round{R}": "exactly 5*R",
        "I2_ITERATIVE_FEEDBACK_round{R}": "exactly 5*R", "N1_RANDOM_ITERATIVE_round{R}": "exactly 5*R",
        "I3_STOPPING_RULE": "VARIABLE per item, 5*stop_round_i -- see I3_STOPPING_RULE section below"}

    # =====================================================================================================
    # ACCURACY-DECLINE CHECK (STOP-IF iv), on I2's and N1's own curves.
    # =====================================================================================================
    def decline_check(curve: Dict[int, float], n_items_here: int) -> Dict:
        rounds_sorted = sorted(curve)
        vals = [curve[r] for r in rounds_sorted]
        peak_r = rounds_sorted[int(np.argmax(vals))]
        peak_v = max(vals)
        final_v = curve[rounds_sorted[-1]]
        hw = _halfwidth(peak_v, n_items_here)
        declined = bool(peak_r < rounds_sorted[-1] and (peak_v - final_v) > hw)
        return {"peak_round": peak_r, "peak_value": round(peak_v, 5), "final_value": round(final_v, 5),
               "drop": round(peak_v - final_v, 5), "ci_halfwidth_at_peak": round(hw, 5),
               "DECLINE_DETECTED": declined}
    decline_I2 = decline_check(per_round_curves["I2_ITERATIVE_FEEDBACK"], n_items)
    decline_N1 = decline_check(per_round_curves["N1_RANDOM_ITERATIVE"], n_items)
    decline_I1 = decline_check(per_round_curves["I1_ITERATIVE_DELETE"], n_items)
    rep["ACCURACY_DECLINE_CHECK"] = {"I2_ITERATIVE_FEEDBACK": decline_I2, "N1_RANDOM_ITERATIVE": decline_N1,
                                     "I1_ITERATIVE_DELETE": decline_I1}
    print("[decline] I2 peak@r%d=%.4f final=%.4f DECLINE=%s | N1 peak@r%d=%.4f final=%.4f DECLINE=%s"
         % (decline_I2["peak_round"], decline_I2["peak_value"], decline_I2["final_value"],
            decline_I2["DECLINE_DETECTED"], decline_N1["peak_round"], decline_N1["peak_value"],
            decline_N1["final_value"], decline_N1["DECLINE_DETECTED"]), flush=True)

    # =====================================================================================================
    # I3_STOPPING_RULE -- I2 + a confidence-based give-up condition (GIVEUP_STREAK consecutive rounds of
    # zero attested evidence). Frozen items carry their stop-round winner forward.
    # =====================================================================================================
    stop_round = compute_stop_round(loop_I2["round_local_best_score"], ROUNDS_MAX, GIVEUP_STREAK)
    per_round_curves["I3_STOPPING_RULE"] = {}
    recovery_curves["I3_STOPPING_RULE"] = {}
    for r in ROUND_GRID:
        ans_r = i3_answer_at_round(loop_I2["winner_idx"], stop_round, r, n_items)
        hit_r = GOLD_T[ans_r, np.arange(n_items)].astype(np.float64)
        name_i3 = "I3_STOPPING_RULE_round%d" % r
        hits_exp[name_i3] = hit_r
        winner_idx_final[name_i3] = ans_r
        per_round_curves["I3_STOPPING_RULE"][r] = round(float(hit_r.mean()), 5)
        ceiling = g1_partial[K_PER_ROUND * r]
        recovery_curves["I3_STOPPING_RULE"][r] = round(per_round_curves["I3_STOPPING_RULE"][r] / ceiling,
                                                        5) if ceiling > 0 else None
        record_unit(output_dir, unit_key("I3", r), {"acc": per_round_curves["I3_STOPPING_RULE"][r]})

    mean_stop_round = float(stop_round.mean())
    mean_total_examined = K_PER_ROUND * mean_stop_round
    matched_k_for_i3 = min(K_GRID, key=lambda k: abs(k - mean_total_examined))
    i3_final_acc = per_round_curves["I3_STOPPING_RULE"][ROUNDS_MAX]
    rep["I3_STOPPING_RULE"] = {
        "stop_round_distribution": {str(r): int((stop_round == r).sum()) for r in ROUND_GRID},
        "mean_stop_round": round(mean_stop_round, 3), "median_stop_round": float(np.median(stop_round)),
        "mean_total_candidates_examined": round(mean_total_examined, 2),
        "matched_I0_k_nearest_grid_point": matched_k_for_i3,
        "I0_at_matched_k": round(i0_acc[matched_k_for_i3], 5),
        "I3_final_accuracy_at_round%d" % ROUNDS_MAX: round(i3_final_acc, 5),
        "per_round_curve": per_round_curves["I3_STOPPING_RULE"],
        "recovery_fraction_curve": recovery_curves["I3_STOPPING_RULE"],
    }
    print("[I3] mean_stop_round=%.2f mean_total_examined=%.1f matched_I0_k=%d I0@matched=%.4f "
         "I3_final=%.4f t=%.0fs" % (mean_stop_round, mean_total_examined, matched_k_for_i3,
                                     i0_acc[matched_k_for_i3], i3_final_acc, time.time() - t0), flush=True)

    # =====================================================================================================
    # ARMS_MUST_DIFFER (META_RULE_AF) -- checked on winner_idx (selection identity), restricted to the
    # arms that are genuinely INDEPENDENT MECHANISMS at a given budget: {I0, I1, I2, N1}. I3 is
    # DELIBERATELY EXCLUDED from this pairwise-difference requirement -- by construction
    # (`i3_answer_at_round`) I3(R) = I2(min(stop_round,R)) per item, so I3 is EXPECTED to often equal
    # I2, and I3(Ra) is EXPECTED to often equal I3(Rb) once the population's cumulative winners have
    # stopped moving (whether via the give-up streak firing OR simply because no later round's fresh
    # candidate outscored the existing best under sparse attestation evidence -- both are legitimate,
    # not a bug). I3's relationship to I2 is measured directly instead, below
    # (I3_STOPPING_RULE_BINDING_FRACTION: the fraction of items where the stopping rule actually
    # changed the answer relative to unconstrained I2 at the same round) -- a continuous diagnostic is
    # more informative here than a binary must-differ gate on a derived arm.
    #
    # TWO classes of EXPECTED equivalence remain, both structural, not silently exempted:
    #   (a) I1_ITERATIVE_DELETE_round{R} vs I0_ONESHOT_BEST_k(5R) -- the prediction under test.
    #   (b) ROUND 1, four-way among {I0,I1,I2,N1}: deflation and random-pick selection both only
    #       affect which candidate is CHOSEN for deflation, and round 1 has no prior round to deflate
    #       by -- every mode examines the identical single shortlist under the identical undeflated
    #       cue, so the round-1 cumulative winner (an attestation argmax over that one shared
    #       shortlist) must be bit-identical across I0/I1/I2/N1 regardless of mode. This was VERIFIED
    #       empirically (not merely argued) on the smoke run before being declared here. (I3 also
    #       joins this at round 1 by the same logic, but stays excluded from the CHECK per the
    #       paragraph above, not from the semantic claim.)
    # =====================================================================================================
    core_arms = {name: arr for name, arr in winner_idx_final.items()
                if not name.startswith("I3_STOPPING_RULE")}
    digests = {name: RSV.arm_digest(arr) for name, arr in core_arms.items()}
    expected_equiv_pairs = set()
    for r in ROUND_GRID:
        expected_equiv_pairs.add(frozenset(["I1_ITERATIVE_DELETE_round%d" % r, "I0_ONESHOT_BEST_k%d"
                                            % (K_PER_ROUND * r)]))
    round1_class = frozenset(["I0_ONESHOT_BEST_k%d" % K_PER_ROUND, "I1_ITERATIVE_DELETE_round1",
                              "I2_ITERATIVE_FEEDBACK_round1", "N1_RANDOM_ITERATIVE_round1"])

    def _explained(a: str, b: str) -> bool:
        if frozenset([a, b]) in expected_equiv_pairs:
            return True
        if a in round1_class and b in round1_class:
            return True
        return False

    names_sorted = sorted(digests)
    collisions = []
    for i, a in enumerate(names_sorted):
        for b in names_sorted[i + 1:]:
            if digests[a] == digests[b] and not _explained(a, b):
                collisions.append((a, b))
    rep["ARMS_MUST_DIFFER"] = {
        "n_arms_checked": len(digests), "checked_on": "winner_idx (selection identity), I0/I1/I2/N1 only",
        "I3_excluded_rationale": "I3 is a DERIVED (frozen) view of I2, expected to often coincide with "
                                 "it and with itself across rounds; measured via "
                                 "I3_STOPPING_RULE_BINDING_FRACTION instead of a must-differ gate",
        "expected_equivalence_pairs_I1_eq_I0": [sorted(p) for p in expected_equiv_pairs],
        "expected_equivalence_round1_four_way": sorted(round1_class),
        "unexplained_collisions": collisions, "PASS": bool(len(collisions) == 0)}
    if collisions:
        print("[LOUD] ARMS_MUST_DIFFER: unexplained bit-identical selections: %r" % collisions, flush=True)
    print("[arms_differ] %d selection arms checked (I3 excluded, measured separately), %d unexplained "
         "collisions" % (len(digests), len(collisions)), flush=True)

    # I3's relationship to I2, measured directly: per round, the fraction of items where the give-up
    # streak actually changed the answer relative to unconstrained I2 at the SAME round.
    i3_binding = {}
    for r in ROUND_GRID:
        differs = (winner_idx_final["I3_STOPPING_RULE_round%d" % r]
                  != winner_idx_final["I2_ITERATIVE_FEEDBACK_round%d" % r])
        i3_binding[r] = round(float(differs.mean()), 5)
    rep["I3_STOPPING_RULE_BINDING_FRACTION"] = {
        "definition": "fraction of items where I3(R) != I2(R) -- 0.0 means the give-up rule never "
                      "changed the outcome at that round (I2's own cumulative winner had already "
                      "stabilised), not that the check is broken", "by_round": i3_binding}
    print("[I3 binding] fraction of items where stopping changed the answer, by round: %s"
         % i3_binding, flush=True)

    # =====================================================================================================
    # BOOTSTRAP -- all arms share ONE set of draws.
    # =====================================================================================================
    scored_mask = np.ones(n_items, dtype=bool)
    for arr in hits_exp.values():
        scored_mask &= np.isfinite(arr)
    boot = FB.paired_bootstrap_ci(hits_exp, scored_mask, N_BOOT, MASTER_SEED + 2501)
    rep["N_BOOT"] = N_BOOT
    rep["n_common_scored"] = boot["n_common"]

    floor_acc = {f: boot["acc"][f] for f in FLOOR_NAMES}
    binding_floor_name = max(floor_acc, key=floor_acc.get)
    binding_floor_value = floor_acc[binding_floor_name]
    rep["BINDING_FLOOR"] = {"per_floor_acc": {f: round(v, 5) for f, v in floor_acc.items()},
                            "binding_floor_name": binding_floor_name,
                            "binding_floor_value": round(binding_floor_value, 5)}

    def marg(a: str, b: str) -> Dict:
        m = FB.margin(boot["boot"], a, b)
        m["ci_halfwidth"] = round((m["ci95"][1] - m["ci95"][0]) / 2.0, 5)
        m["analytic_null_halfwidth_a"] = round(_halfwidth(boot["acc"][a], boot["n_common"]), 5)
        m["acc_a"] = round(boot["acc"][a], 5)
        m["acc_b"] = round(boot["acc"][b], 5)
        return m

    # PRIMARY (budget-matched) margins for I2 and I3, at every round.
    margins: Dict[str, Dict] = {}
    for r in ROUND_GRID:
        k_here = K_PER_ROUND * r
        name_i2 = "I2_ITERATIVE_FEEDBACK_round%d" % r
        name_i1 = "I1_ITERATIVE_DELETE_round%d" % r
        name_n1 = "N1_RANDOM_ITERATIVE_round%d" % r
        name_i0 = "I0_ONESHOT_BEST_k%d" % k_here
        m_floor = marg(name_i2, binding_floor_name)
        m_floor["matched_budget_k"] = k_here
        margins["%s__vs__FLOOR(%s)" % (name_i2, binding_floor_name)] = m_floor
        m_i0 = marg(name_i2, name_i0)
        assert k_here == int(name_i0.rsplit("_k", 1)[1]), "BUDGET MISMATCH -- comparison would be VOID"
        m_i0["matched_budget_k"] = k_here
        margins["%s__vs__%s(MATCHED_BUDGET)" % (name_i2, name_i0)] = m_i0
        m_i1 = marg(name_i2, name_i1)
        m_i1["matched_budget_k"] = k_here
        margins["%s__vs__%s" % (name_i2, name_i1)] = m_i1
        m_n1 = marg(name_i2, name_n1)
        m_n1["matched_budget_k"] = k_here
        margins["%s__vs__%s" % (name_i2, name_n1)] = m_n1
        margins["%s__vs__FLOOR(%s)" % (name_n1, binding_floor_name)] = marg(name_n1, binding_floor_name)
        margins["%s__vs__FLOOR(%s)" % (name_i0, binding_floor_name)] = marg(name_i0, binding_floor_name)

    # I3 at its OWN matched budget (nearest K_GRID point to its mean total candidates examined).
    name_i0_i3 = "I0_ONESHOT_BEST_k%d" % matched_k_for_i3
    name_i3_final = "I3_STOPPING_RULE_round%d" % ROUNDS_MAX
    m_i3_i0 = marg(name_i3_final, name_i0_i3)
    m_i3_i0["matched_budget_k"] = matched_k_for_i3
    m_i3_i0["note"] = "I3 examines a VARIABLE budget per item (mean %.2f candidates); matched against " \
                      "the nearest I0 grid point, %d." % (mean_total_examined, matched_k_for_i3)
    margins["%s__vs__%s(MATCHED_BUDGET_MEAN)" % (name_i3_final, name_i0_i3)] = m_i3_i0
    margins["%s__vs__FLOOR(%s)" % (name_i3_final, binding_floor_name)] = marg(name_i3_final, binding_floor_name)
    margins["%s__vs__N1_RANDOM_ITERATIVE_round%d" % (name_i3_final, ROUNDS_MAX)] = marg(
        name_i3_final, "N1_RANDOM_ITERATIVE_round%d" % ROUNDS_MAX)
    rep["MARGINS"] = margins

    # =====================================================================================================
    # STOP-IF EVALUATION -- headline round = ROUNDS_MAX (the full 50-candidate matched budget).
    # =====================================================================================================
    R_HEAD = ROUNDS_MAX
    K_HEAD = K_PER_ROUND * R_HEAD
    name_i2_head = "I2_ITERATIVE_FEEDBACK_round%d" % R_HEAD
    name_i1_head = "I1_ITERATIVE_DELETE_round%d" % R_HEAD
    name_n1_head = "N1_RANDOM_ITERATIVE_round%d" % R_HEAD
    name_i0_head = "I0_ONESHOT_BEST_k%d" % K_HEAD

    beats_floor = margins["%s__vs__FLOOR(%s)" % (name_i2_head, binding_floor_name)]["band"] == "ABOVE"
    beats_n1 = margins["%s__vs__%s" % (name_i2_head, name_n1_head)]["band"] == "ABOVE"
    beats_i0 = margins["%s__vs__%s(MATCHED_BUDGET)" % (name_i2_head, name_i0_head)]["band"] == "ABOVE"
    ties_i1 = margins["%s__vs__%s" % (name_i2_head, name_i1_head)]["band"] == "NOT_SEPARATED"
    ties_i0 = margins["%s__vs__%s(MATCHED_BUDGET)" % (name_i2_head, name_i0_head)]["band"] == "NOT_SEPARATED"

    # rule 12 -- orthographic + word-length correlation, on I2 (and I3, N1 if either separately clears).
    Sortho_T = floors_S.get("F_ORTHOGRAPHIC")
    word_len = np.array([len(a) for a in anchors], dtype=np.float64)
    from experiments.exp_cue_binarised_readout_transfer_v1 import pearson_ci_bootstrap
    rule12: Dict[str, Dict] = {}
    clearing_for_rule12 = [name_i2_head]
    if margins["%s__vs__FLOOR(%s)" % (name_n1_head, binding_floor_name)]["band"] == "ABOVE":
        clearing_for_rule12.append(name_n1_head)
    if margins["%s__vs__FLOOR(%s)" % (name_i0_head, binding_floor_name)]["band"] == "ABOVE":
        clearing_for_rule12.append(name_i0_head)
    if margins["%s__vs__%s(MATCHED_BUDGET_MEAN)" % (name_i3_final, name_i0_i3)]["band"] == "ABOVE" or \
       margins["%s__vs__FLOOR(%s)" % (name_i3_final, binding_floor_name)]["band"] == "ABOVE":
        clearing_for_rule12.append(name_i3_final)
    for arm in clearing_for_rule12:
        top1 = winner_idx_final[arm]
        winner_len = word_len[top1]
        gain = hits_exp[arm] - hits_exp[name_i0_head]
        best_gold_ortho = np.where(GOLD_T & E_T, Sortho_T, -np.inf).max(axis=0) \
            if Sortho_T is not None else np.full(n_items, np.nan)
        ortho_corr = pearson_ci_bootstrap(gain, best_gold_ortho, seed=MASTER_SEED + 2601, n_boot=2000)
        len_corr = pearson_ci_bootstrap(gain, winner_len, seed=MASTER_SEED + 2611, n_boot=2000)
        rule12[arm] = {"ortho_gain_corr": ortho_corr, "word_length_gain_corr": len_corr}
    rule12_fail = [arm for arm, v in rule12.items()
                  if v["ortho_gain_corr"].get("band") == "ABOVE"
                  or v["word_length_gain_corr"].get("band") == "ABOVE"]

    decline_fired = decline_I2["DECLINE_DETECTED"] or decline_N1["DECLINE_DETECTED"] \
        or decline_I1["DECLINE_DETECTED"]

    rep["STOP_IF"] = {
        "headline_round": R_HEAD, "headline_budget_K": K_HEAD,
        "i_real_win": bool(beats_floor and beats_n1 and beats_i0),
        "ii_i2_ties_i1": ties_i1, "iii_i2_ties_i0_matched_budget": ties_i0,
        "iv_accuracy_declines": decline_fired, "v_k1_fail": False,   # would have SystemExit'd already
        "rule12_fail_arms": rule12_fail, "rule12_detail": rule12,
        "beats_floor": beats_floor, "beats_n1": beats_n1, "beats_i0_matched_budget": beats_i0,
    }

    if rep["STOP_IF"]["i_real_win"]:
        verdict = "STOPIF_I__REAL_ITERATIVE_WIN__I2_ITERATIVE_FEEDBACK_round%d" % R_HEAD
    elif rule12_fail:
        verdict = "STOPIF_RULE12_LEAKAGE__" + "_".join(rule12_fail[:2])
    elif ties_i1:
        verdict = "STOPIF_II__FEEDBACK_DOES_NOTHING__ITERATION_IS_JUST_A_LONGER_LIST"
    elif ties_i0:
        verdict = "STOPIF_III__ITERATION_NOT_THE_MISSING_STRUCTURE__DEFICIT_DISTRIBUTED"
    elif decline_fired:
        verdict = "STOPIF_IV__ACCURACY_DECLINES_WITH_ROUNDS__PUSHING_HARDER_MEASURED"
    else:
        verdict = "NO_STOPIF_FIRED__I2_NEITHER_WINS_NOR_TIES_CLEANLY__SEE_MARGINS"

    verdict_msg_parts = [
        "HEADLINE round=%d (budget=%d candidates). BindingFloor=%s@%.5f." % (
            R_HEAD, K_HEAD, binding_floor_name, binding_floor_value),
        "I0=%.5f I1=%.5f(eqI0=%s) I2=%.5f I3final=%.5f(meanN=%.1f,matchedK=%d) N1=%.5f." % (
            i0_acc[K_HEAD], per_round_curves["I1_ITERATIVE_DELETE"][R_HEAD], i1_i0_equal[R_HEAD],
            per_round_curves["I2_ITERATIVE_FEEDBACK"][R_HEAD], i3_final_acc, mean_total_examined,
            matched_k_for_i3, per_round_curves["N1_RANDOM_ITERATIVE"][R_HEAD]),
        "I2 beats_floor=%s beats_N1=%s beats_I0_matched=%s ties_I1=%s ties_I0_matched=%s." % (
            beats_floor, beats_n1, beats_i0, ties_i1, ties_i0),
        "DECLINE_DETECTED I1=%s I2=%s N1=%s. RULE12_FAIL=%r." % (
            decline_I1["DECLINE_DETECTED"], decline_I2["DECLINE_DETECTED"], decline_N1["DECLINE_DETECTED"],
            rule12_fail),
    ]
    if verdict.startswith("STOPIF_III"):
        verdict_msg_parts.append(
            "ITERATION IS NOT THE MISSING STRUCTURE, and combined with the seven landed interventions "
            "the honest reading is that THE READ-OUT DEFICIT IS DISTRIBUTED ACROSS THE REPRESENTATION "
            "RATHER THAN A SINGLE MISSING COMPONENT.")
    rep["verdict"] = verdict
    rep["verdict_msg"] = " ".join(verdict_msg_parts)
    rep["summary"] = verdict
    rep["elapsed_s"] = round(time.time() - t0, 1)
    rep["run_mode"] = "full" if grid == "full" else "smoke"
    rep["ORGAN_REUSE_RUNTIME_WITNESS"] = sorted(
        m for m in sys.modules
        if any(s in m for s in ("exp_readout_shortlist_verifier_v1", "exp_readout_ceiling_diagnosis_v1",
                                "exp_cue_to_store_translation_v1", "floor_battery",
                                "exp_cue_binarised_readout_transfer_v1", "exp_definitional_grounding_v5",
                                "reading_grounding_loop", "exp_checkpoint")))
    print("[verdict] %s  t=%.0fs" % (verdict, time.time() - t0), flush=True)
    return rep


# =======================================================================================================
def decide(rep: Dict) -> Tuple[str, str]:
    return rep["verdict"], rep["verdict_msg"]


def main() -> None:
    output_dir = _out_dir()
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "argv": list(sys.argv),
             "host": platform.node()}
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)

    if _ARGS.self_test:
        ev = self_test()
        _atomic_json(os.path.join(output_dir, "selftest_result.json"), ev)
        print("[main] SELF-TEST ALL PASS", flush=True)
        return

    rep = run(_ARGS.grid, output_dir)
    _atomic_json(os.path.join(output_dir, "metrics.json"), rep)
    print("[main] wrote %s" % os.path.join(output_dir, "metrics.json"), flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:                      # NOT BaseException; preserves SystemExit/KeyboardInterrupt
        out_dir = _out_dir()
        os.makedirs(out_dir, exist_ok=True)
        diag = {
            "verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(e).__name__, str(e)[:500]),
            "summary": "CELL_CRASHED: %s" % type(e).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME,
        }
        tmp_path = os.path.join(out_dir, "metrics.json.tmp")
        final_path = os.path.join(out_dir, "metrics.json")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(diag, f, indent=2)
        os.replace(tmp_path, final_path)
        raise
