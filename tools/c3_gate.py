#!/usr/bin/env python
"""The C3 grounding-quality gate, as an EXECUTABLE PREDICATE rather than prose.

Why this file exists. The C3 gate used to be one sentence in a document -- ">=10% MEANINGFUL
against a recorded floor, tautologies <10%" -- and on 2026-08-14 a pure character-trigram control
carrying NO MEANING AT ALL scored hit@1 0.10275 on that read-out and cleared it
(data/exp_meaning_supply_separation_v1/metrics.json, arm A5_STRINGCTRL at w=1.00, commit c0e6ec0da).
A prose gate gets re-interpreted by whoever quotes it. A gate that is a function does not.

Two jobs:
  1. `string_form_profile` / `string_control_scores` -- the MANDATORY zero-meaning control arm,
     supplied here so no future cell has an excuse to skip it. Identical construction to the arm
     that caught the defect (sha256-hashed character trigrams with ^ $ boundaries, L2-normalized).
  2. `evaluate` / `--score` -- the four-condition gate. It returns NOT_EVALUABLE, never PASS, when
     the string control arm is absent. That is the guard, and `--self-test` proves it.

Usage:
    python tools/c3_gate.py --self-test
    python tools/c3_gate.py --score data/exp_meaning_supply_separation_v1/metrics.json
    python tools/c3_gate.py --score <metrics.json> --arm A4_BOTH --base-arm A1_BASE

Exit codes: 0 = at least one arm PASSes (or self-test passed), 1 = nothing passes, 2 = bad input.

Doc coupling (CLAUDE.md "a doc parsed by code is coupled to it"): the authoritative prose statement
of this gate lives in notes/SUBSTRATE_STRATEGY.md PART 1, under the C3 row. That prose must name
this file; this file names that section. Changing one without the other is the defect.
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import re
import sys
from typing import Dict, List, Optional, Sequence

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ gate constants
HIT_AT_1_FLOOR = 0.10          # the historical magnitude clause, unchanged
TAUTOLOGY_CEILING = 0.10       # the historical tautology clause, unchanged
STRING_CONTROL_DIM = 512       # matches experiments/exp_meaning_supply_separation_v1.TRIGRAM_DIM

# Every arm name ever used, across cells, for a floor CONTROL rather than a treatment. HG1's
# "recorded floor" is defined (notes/SUBSTRATE_STRATEGY.md PART 1, MEMORY.md "A GATE IS A
# CI-SEPARATED MARGIN...") as max(orthographic, frequency, scramble) -- never scramble alone.
# 2026-08-15: found stale -- score_metrics() only ever chased scramble-shaped delta keys
# (d_A1_BASE_minus_F_SCRAMBLE / d_*_minus_B6_OPEN_SCRAMBLE / d_B5_minus_B6) even on cells that
# recorded a DIRECT arm-vs-orthographic and arm-vs-frequency delta in the same bootstrap block
# (data/exp_graded_path_vs_orthographic_floor_v1/metrics.json has
# d_A1_GRADED_ON_minus_A5_STRINGCTRL and d_A1_GRADED_ON_minus_F_FREQUENCY sitting unread next to
# the scramble delta it did use). Widened below.
# 2026-08-16 (second widening): the CONSTANT/PROTOTYPE floor became MANDATORY when a
# query-ignoring constant ranking (cosine to the mean anchor direction) beat the spelling floor
# CI-separated on the open-vocabulary read-out. tools/floor_battery.FLOOR_SET_REQUIRED had
# carried four members since that morning; this list and REQUIRED_FLOOR_ROLES below still
# carried three. Names ENUMERATED from disk (scratch/cf_enumerate.py over 7,787 metrics.json),
# not guessed.
FLOOR_ARM_NAMES = (
    "F_SCRAMBLE", "F_SCRAMBLE_ON", "F_SCRAMBLE_OFF", "B6_OPEN_SCRAMBLE",
    "F_FREQUENCY", "F_FREQ", "A5_STRINGCTRL", "A6_TRIGRAM_ONLY", "A7_PREFIX_ONLY",
    "A8_MAXORTHO",
    "F_CONSTANT_PROTOTYPE", "F4_CONSTANT_PROTOTYPE", "F5_CONSTANT_PROTOTYPE",
    "F5_CONSTANT_PROTOTYPE_zero_query_information",
)

PASS, FAIL, NOT_EVALUABLE = "PASS", "FAIL", "NOT_EVALUABLE"

# ------------------------------------------------------------------ arm ROLE classification
# Added 2026-08-16 for tools/verdict_bar_check.py. It lives HERE, not in the checker, for the
# same reason FLOOR_ARM_NAMES does: a second opinion about "which arms are floors" is a second
# gate, and a second gate is the defect class this file exists to prevent.
#
# The three roles that make up the standing bar's max(orthographic, frequency, scramble) are
# REQUIRED_FLOOR_ROLES. `random_chance` is deliberately NOT one of them: a chance baseline is not
# an orthographic, frequency or scramble floor, and counting it as one is precisely how a bare
# threshold gets dressed up as a floor comparison.
_ROLE_PATTERNS = (
    ("orthographic", r"orthograph|stringctrl|string_ctrl|trigram|prefix_only|char_?ngram|"
                     r"spelling|maxortho|surface_form|edit_?dist"),
    ("frequency",    r"\bfreq\b|frequenc|_freq_|freq_min|freq_sum|unigram_?count|zipf"),
    ("scramble",     r"scrambl|shuffl|permut|derange|_perm_null|permutation_null"),
    ("random_chance", r"random_chance|\bchance\b|random_baseline|uniform_baseline|coin_flip"),
    # KNOWN-ANSWER / PLANTED-ANSWER / ORACLE. Widened 2026-08-16 after a PER-PIPELINE validity
    # arm named `S_INPLACE_d256_f0.020__KA` was selected as the CLAIM-CARRYING ARM by
    # tools/verdict_bar_check.py and produced a false MEETS_BAR at min ci_lo +0.9044 on a cell
    # whose every genuine arm is negative. The additions were ENUMERATED from disk, not guessed:
    # every dict key sitting in an arm-shaped position across all 7,772 banked metrics.json was
    # collected and bucketed (scratch/fp_enumerate_names.py), which is why `ka`, `planted`,
    # `query_is_gold` and the `gt` shape are here and why `identity` / `sanity` / `ceiling` /
    # `leak` are NOT (they live in _SCAFFOLD_RE below, where over-firing costs nothing).
    #   * `(^|_)ka(_|$)`  covers `__KA`, `_KA`, `KA_QUERY_IS_GOLD_VECTOR`, `KA_PLANTED_SEMANTIC`.
    #     Bounded on both sides deliberately: it must NOT fire on `kappa`, `kalman`, `weka`.
    ("known_answer", r"known_answer|known_?ans|oracle|positive_control|pos_?ctrl|"
                     r"pretrained_positive|glove|ceiling_ref|upper_bound_ref|gold_oracle|"
                     r"sanity_arm|(^|_)ka(_|$)|planted|query_?is_?gold|gold_?vector|"
                     r"ground_?truth|(^|_)gt(_|$)"),
    # THE FOURTH FLOOR, added 2026-08-16. A CONSTANT ranking -- the same answer to every
    # question, e.g. cosine to the mean anchor direction -- uses ZERO query information and beat
    # the spelling floor CI-separated on the open-vocabulary read-out. tools/floor_battery.py
    # computes it and has listed it in FLOOR_SET_REQUIRED since that morning; it was never wired
    # into this classifier, so evaluate_standing_bar could not include it in the max.
    #
    # POSITION IS LOAD-BEARING, in BOTH directions:
    #   * AFTER `frequency`, so `F3_FREQUENCY_ONLY_constant` (the frequency floor, whose name
    #     says "constant column") keeps reading as FREQUENCY -- 386 occurrences on disk.
    #   * AFTER `known_answer`, so `ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor` (192),
    #     `B_ORACLE_CONSTANT_GOLD_DEGREE_not_a_floor` (61) and `ORACLE_CONSTANT_never_a_floor`
    #     (29) keep reading as ORACLE. Those are fitted on the gold labels: they are the CEILING
    #     of the constant family, never a floor, and promoting one to a required floor would
    #     hand a cell a floor it is supposed to be unable to reach.
    # The pattern requires the two tokens ADJACENT so it does not fire on the 20+ genuine
    # treatment arms carrying `PROTOTYPE` or `CENTROID` alone (ARM_HRR_BUNDLE_PROTOTYPE,
    # C_ISO_GLOBAL_CENTROID_beta0.50, memorize_prototype, FAMILY_PROTOTYPE_BASED), nor on
    # `v4_constants` / `v2_metric_constants` / `S5_balanced_pool_kills_constant_rankings`.
    ("constant_prototype",
     r"constant_?prototype|prototype_?constant|const_?proto(type)?(_|$)|constant_?column|"
     r"constant_?ranking_?floor|zero_query_information|mean_anchor_direction"),
    ("null_control", r"null_arm|null_control|negative_control|randinit|rand_init|noise_arm|"
                     r"untrained|no_signal|_null\b|null_"),
)
_ROLE_RE = tuple((role, re.compile(pat, re.IGNORECASE)) for role, pat in _ROLE_PATTERNS)

# THE STANDING BAR'S FLOOR SET. Four roles since 2026-08-16, matching
# tools/floor_battery.FLOOR_SET_REQUIRED exactly -- the two lists are the same rule and a drift
# between them is what this fix repairs. `random_chance` is still deliberately NOT one of them.
CONSTANT_FLOOR_ROLE = "constant_prototype"
REQUIRED_FLOOR_ROLES = ("orthographic", "frequency", "scramble", CONSTANT_FLOOR_ROLE)
BAR_MEETS, BAR_FAILS, BAR_NO_EVIDENCE = "MEETS_BAR", "FAILS_BAR", "NO_EVIDENCE"
# Reported when a cell's CLAIM ARM has no CI-bearing margin against the constant floor. This is
# a NAMED, reportable condition rather than a silent pass: for every gate evaluation before this
# date the max was formed from three floors, and the fourth was the strongest one measured.
CONSTANT_FLOOR_COMPARED, NO_CONSTANT_FLOOR = "CONSTANT_FLOOR_COMPARED", "NO_CONSTANT_FLOOR"


def classify_arm_role(name: str) -> Optional[str]:
    """Role of an arm/floor/delta NAME, or None if it looks like a treatment arm.

    Name-shape only -- deliberately. The alternative is a hand-maintained list of arm names,
    which is what went stale in FLOOR_ARM_NAMES between June and 2026-08-15 (see that constant's
    comment). Precedence is the tuple order above: `null_control` is checked LAST so that
    `F_SCRAMBLE_NULL_P95` reads as a scramble floor rather than as a null arm.
    """
    s = str(name)
    for role, rx in _ROLE_RE:
        if rx.search(s):
            return role
    return None


# ------------------------------------------------------------------ CLAIM-ARM ELIGIBILITY
# Added 2026-08-16. A KNOWN-ANSWER / planted-answer / oracle / control arm may NEVER be selected
# as the arm that carries a cell's claim. It is VALIDITY SCAFFOLDING: near ceiling BY
# CONSTRUCTION, so its margin over a floor is arithmetic, not evidence.
#
# WHY THIS IS A SEPARATE PREDICATE FROM classify_arm_role. Role classification feeds the bar's
# bookkeeping (does this cell HAVE a known-answer arm? which floors did it record?), where a
# false positive would wrongly credit a cell with evidence it lacks -- so it is kept tight.
# Eligibility only ever REMOVES an arm from consideration, so over-firing costs a NO_EVIDENCE,
# never a false pass. The two therefore get different tolerances on purpose, and the looser
# lexicon lives here where it is safe.
#
# ANTI-CORRELATION WITH RIGOUR is the reason this exists at all: a cell that ships a known-answer
# and a null for EVERY pipeline -- the MORE rigorous design -- was MORE likely to be falsely
# passed than a sloppy one, because it published more planted-answer arms for the selector to
# find. Any rule here must not re-create that inversion.
#
# PINNED vs OURS (brain-fidelity block c, and this whole file is INSTRUMENTATION -- no brain
# claim): "a planted-answer arm is not evidence" is PINNED by the standing bar. The lexicon
# below and the two structural tells are OUR-INVENTION, freely revisable, and falsifiable by
# the self-test and by verification/test_verdict_bar_checker.py.
CLAIM_ARM_ELIGIBLE = "ELIGIBLE"
CLAIM_ARM_CONTROL = "CONTROL_ARM"
CLAIM_ARM_SCAFFOLD = "VALIDITY_SCAFFOLD"
CLAIM_ARM_CEILING = "CEILING_BY_CONSTRUCTION"

CONTROL_ROLES = ("orthographic", "frequency", "scramble", CONSTANT_FLOOR_ROLE, "random_chance",
                 "null_control", "known_answer")
# `constant_prototype` joined this list 2026-08-16 for a reason worth stating: before the role
# existed, `classify_arm_role("F5_CONSTANT_PROTOTYPE_zero_query_information")` returned None, so
# the constant FLOOR was ELIGIBLE TO CARRY A CELL'S CLAIM -- a zero-query-information ranking
# could have been selected as the arm a cell's result rests on. Measured, not hypothesised:
# claim_arm_eligibility(["F5_CONSTANT_PROTOTYPE"]) returned {"eligible": True} before this edit.

# The LOOSER lexicon: tokens that mark an arm as scaffolding/diagnostic rather than a result.
# Enumerated from disk (see the known_answer comment above), NOT guessed. Each token below was
# observed as a real arm-position key in data/**/metrics.json.
_SCAFFOLD_RE = re.compile(
    r"(^|_)ka(_|$)|planted|query_?is_?gold|gold_?vector|known_?ans|oracle|"
    r"(^|_)sanity(_|$)|sanity_|_sanity|(^|_)ceil(ing)?(_|$)|ceiling_|_ceiling|"
    r"(^|_)identity(_|$)|self_?retriev|(^|_)gt(_|$)|ground_?truth|"
    r"leak_control|leakage_control|_direct_leak|leak_probe|leak_audit|leakage_audit|"
    r"positive_control|pos_?ctrl|posctrl|upper_?bound|skyline|topline|cheat",
    re.IGNORECASE)

# Bounded PERFORMANCE scores only -- the keys whose ceiling of 1.0 means "answered everything
# correctly". Deliberately NARROWER than tools/verdict_bar_check._SCORE_KEY, which answers a
# different question (which key is a cell's HEADLINE metric for the saturation-across-arms
# shape). `margin`, `separation` and `agreement` are excluded: a margin of 1.0 is not a ceiling.
#
# `frac` / `fraction` / `rate` / `ratio` are excluded too, and that exclusion is MEASURED, not
# cautious drafting. With them in, the first cut of this detector excluded `INC_SIMHASH` -- the
# legitimate INCUMBENT arm of exp_meaning_lift_population_code_v1 -- as "at ceiling", because a
# SimHash is a sign function so its `active_frac_realised` is 1.0 by definition. A realised
# configuration fraction is not a score, and over-exclusion here silently deletes real arms from
# consideration, which is the opposite failure to the one this whole change is fixing.
CEILING_SCORE_KEY = re.compile(
    r"(^|_)(acc|accuracy|hit|hits|recall|precision|f1|auc|success|coverage|mrr|ndcg)($|_)|"
    r"hit_?at_?\d+|top_?\d+", re.IGNORECASE)
_CEIL_TOL = 1e-9


def _is_ceiling_value(x: float) -> bool:
    return abs(float(x) - 1.0) <= _CEIL_TOL


def arm_ceiling_shape(node: Optional[dict]) -> Optional[dict]:
    """STRUCTURAL, name-free tell that an arm sits at the instrument ceiling BY CONSTRUCTION.

    Returns evidence, or None. Two tells, reported separately because they catch different arms:

      S1 DEGENERATE_CI_AT_CEILING -- a bounded score has a confidence interval of ZERO WIDTH at
         1.0, e.g. `hit_at_1: 1.0` beside `hit_at_1_ci95: [1.0, 1.0]`. An arm that answers every
         item correctly on every bootstrap draw is not measuring anything; it is proving the
         pipeline can reach ceiling. This is the tell that catches the arm behind the false pass.
      S2 ALL_SCORES_AT_CEILING -- every bounded score on the node is exactly 1.0.

    LIMIT, stated rather than buried: this CANNOT see a planted-answer arm that FAILS. The two
    degenerate `f=0.002/0.005` known-answer arms in the cell that produced the false pass read
    hit@1 0.4056 (k=1 active unit of 256, so anchors collide) and are structurally
    indistinguishable from a mediocre treatment arm. Those are caught by NAME only. Anyone
    reading this must not treat the structural tell as sufficient.
    """
    if not isinstance(node, dict):
        return None
    scores = []
    for k, v in node.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        if CEILING_SCORE_KEY.search(str(k)):
            scores.append((str(k), float(v)))
    for k, v in node.items():
        if (isinstance(v, (list, tuple)) and len(v) == 2
                and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)
                and abs(float(v[0]) - float(v[1])) <= _CEIL_TOL
                and _is_ceiling_value(v[0])):
            return {"tell": "DEGENERATE_CI_AT_CEILING", "key": str(k), "value": [v[0], v[1]],
                    "scores_at_ceiling": [s for s in scores if _is_ceiling_value(s[1])][:6]}
    if scores and all(_is_ceiling_value(v) for _, v in scores):
        return {"tell": "ALL_SCORES_AT_CEILING", "key": None, "value": None,
                "scores_at_ceiling": scores[:6]}
    return None


def claim_arm_eligibility(name_segments: Sequence[str],
                          node: Optional[dict] = None) -> dict:
    """May this arm carry the cell's CLAIM? FAIL-CLOSED: when in doubt, NOT eligible.

    `name_segments` is EVERY path segment that could name the arm -- not just the last one. That
    is load-bearing: the false pass on 2026-08-16 selected `020__KA::MARGIN_per_floor`, and the
    old check classified only the tail `MARGIN_per_floor` (a CONTAINER), so nine `__NULL` arms
    that the classifier ALREADY recognised correctly were scored as treatment arms anyway. Any
    segment matching disqualifies the whole arm.

    `node` is the arm's own metrics dict when the caller can supply it, for the structural tell.

    Returns {"eligible": bool, "reason": <CLAIM_ARM_*>, "detail": ..., "evidence": ...}.
    """
    segs = [str(s) for s in name_segments if s not in (None, "", "[]")]
    for s in segs:
        role = classify_arm_role(s)
        if role in CONTROL_ROLES:
            return {"eligible": False, "reason": CLAIM_ARM_CONTROL,
                    "detail": f"segment {s!r} classifies as role {role!r}", "evidence": None}
    for s in segs:
        mt = _SCAFFOLD_RE.search(s)
        if mt:
            return {"eligible": False, "reason": CLAIM_ARM_SCAFFOLD,
                    "detail": f"segment {s!r} matches validity-scaffold token {mt.group(0)!r}",
                    "evidence": None}
    shape = arm_ceiling_shape(node)
    if shape:
        return {"eligible": False, "reason": CLAIM_ARM_CEILING,
                "detail": f"structural: {shape['tell']}", "evidence": shape}
    return {"eligible": True, "reason": CLAIM_ARM_ELIGIBLE, "detail": None, "evidence": None}


def min_ci_lo(candidates: Sequence[tuple]) -> tuple:
    """THE conservative rule, in ONE place: take the MIN ci_lo and NAME its source.

    `candidates` is a sequence of (ci_lo, source_name). Returns (ci_lo, source) or (None, None).

    Why MIN and not "the floor with the highest point estimate": the standing bar is a margin
    above max(orthographic, frequency, scramble), and under a PAIRED bootstrap the floor with the
    highest point value is NOT always the hardest to separate from -- the arm and the floor
    channel are correlated, so a lower-point floor can produce the tighter bound. Measured on
    2026-08-16 in data/exp_meaning_asset_calibrated_floor_verdict_v1: arm d512|ASSET_RETRAIN_CTX
    separates from the scramble floor (highest point, 0.0932) at ci_lo +0.0704 but does NOT
    separate from the frequency floor (lower point, 0.0797) at ci_lo -0.0156. Picking by point
    value passed that arm; MIN over ci_lo fails it, which is the correct reading.
    """
    vals = [(v, s) for v, s in candidates if v is not None]
    if not vals:
        return None, None
    return min(vals, key=lambda t: t[0])


def evaluate_standing_bar(*,
                          floor_ci_pairs: Sequence[tuple],
                          floor_roles_present: Sequence[str],
                          floor_roles_with_ci: Sequence[str],
                          has_known_answer_arm: Optional[bool] = None,
                          has_null_arm: Optional[bool] = None,
                          arm_name: str = "ARM") -> dict:
    """The STANDING BAR as an executable predicate, for any cell -- not just C3-shaped ones.

    The bar (notes/LONG_TERM_PLAN.md sec 5, MEMORY.md "A GATE IS A CI-SEPARATED MARGIN"):
      a CI-SEPARATED margin over max(orthographic, frequency, scramble) on the IDENTICAL
      scorer / n / pool / gold -- never a bare absolute number -- PLUS a KNOWN-ANSWER arm
      licensing the instrument and a NULL arm licensing the effect, which fail INDEPENDENTLY.

    Independence is structural here: each of the five conditions is computed from its own
    evidence and reported separately, so "no floor" never masquerades as "not separated" and a
    missing known-answer arm never silently downgrades a real separation.

    `floor_ci_pairs` is [(ci_lo, floor_source_name), ...] -- one entry per floor the cell
    actually recorded a CI-bearing margin against. This function does NOT invent one.

    Returns a dict; `status` is MEETS_BAR / FAILS_BAR / NO_EVIDENCE. It is never a bare bool,
    because "we cannot tell" and "it fails" are different findings and this project has paid for
    conflating them (17 corrections-of-a-correction from premature demotion).
    """
    roles_present = sorted(set(floor_roles_present))
    roles_with_ci = sorted(set(floor_roles_with_ci))
    required_present = [r for r in REQUIRED_FLOOR_ROLES if r in roles_present]
    ci_lo, ci_src = min_ci_lo(floor_ci_pairs)

    c: Dict[str, dict] = {}
    c["FLOOR_PRESENT"] = {
        "ok": bool(required_present),
        "roles_present": roles_present,
        "required_roles_present": required_present,
        "required_roles_absent": [r for r in REQUIRED_FLOOR_ROLES if r not in roles_present],
    }
    c["CI_PRESENT"] = {"ok": bool(floor_ci_pairs), "n_floor_margins_with_ci": len(floor_ci_pairs)}
    if not floor_ci_pairs or not required_present:
        c["MARGIN_CI_SEPARATED"] = {"ok": None, "min_ci_lo": ci_lo, "binding_floor": ci_src}
    else:
        c["MARGIN_CI_SEPARATED"] = {"ok": bool(ci_lo > 0.0), "min_ci_lo": ci_lo,
                                    "binding_floor": ci_src}
    # The bar is a margin over max(orthographic, frequency, scramble). If a cell never PAIRED
    # against one of the three, we cannot know it cleared the max -- so this is None (unknown),
    # never False. "Not measured" and "refuted" are different findings and conflating them is
    # what produces premature demotions. This condition is what stops
    # "cleared its strongest floor" from being read as "cleared THE floor": the calibrated-floor
    # cell picked its strongest floor by POINT value and the paired test against a
    # lower-pointed floor is the one that failed.
    _all_compared = set(REQUIRED_FLOOR_ROLES).issubset(set(roles_with_ci))
    c["ALL_REQUIRED_FLOORS_COMPARED"] = {
        "ok": True if _all_compared else None,
        "compared": roles_with_ci,
        "not_compared": [r for r in REQUIRED_FLOOR_ROLES if r not in roles_with_ci],
    }
    # THE FOURTH FLOOR, REPORTED BY NAME. It is already inside ALL_REQUIRED_FLOORS_COMPARED, but
    # it gets its own condition because its absence has a specific, actionable meaning that a
    # generic "one of the four is missing" hides: every bar decision computed before 2026-08-16
    # was taken against max(orthographic, frequency, scramble) while the CONSTANT floor -- the
    # strongest member on the instrument where it was measured -- sat uncomputed. A reader
    # scanning old verdicts needs to see WHICH floor was missing, not merely that one was.
    # `ok` is None, never False: not-measured and refuted are different findings.
    _const_compared = CONSTANT_FLOOR_ROLE in roles_with_ci
    c["CONSTANT_FLOOR_COMPARED"] = {
        "ok": True if _const_compared else None,
        "role": CONSTANT_FLOOR_ROLE,
        "present_in_cell": CONSTANT_FLOOR_ROLE in roles_present,
        "status": CONSTANT_FLOOR_COMPARED if _const_compared else NO_CONSTANT_FLOOR,
        "why_it_matters": (
            "a query-ignoring CONSTANT ranking beat the spelling floor CI-separated on the "
            "open-vocabulary read-out (tools/floor_battery.constant_prototype_floor). A max "
            "formed without it is not the standing bar's max."),
    }
    c["KNOWN_ANSWER_ARM"] = {"ok": has_known_answer_arm}
    c["NULL_ARM"] = {"ok": has_null_arm}

    # Coverage is reported, never silently folded into the verdict: a cell can separate from
    # every floor it MEASURED while never having measured one of the three. That is a real and
    # different defect from failing to separate, and the operator decides what to do about it.
    missing_ci = [r for r in required_present if r not in roles_with_ci]
    evidence_complete = bool(
        not missing_ci
        and sorted(required_present) == sorted(REQUIRED_FLOOR_ROLES)
        and has_known_answer_arm and has_null_arm)

    failed = [k for k, v in c.items() if v["ok"] is False]
    unknown = [k for k, v in c.items() if v["ok"] is None]
    if failed:
        status = BAR_FAILS
    elif unknown:
        status = BAR_NO_EVIDENCE
    else:
        status = BAR_MEETS
    return {
        "arm": arm_name, "status": status, "conditions": c,
        "min_ci_lo": ci_lo, "binding_floor": ci_src,
        "floor_roles_present": roles_present, "floor_roles_with_margin_ci": roles_with_ci,
        "required_floor_roles_without_margin_ci": missing_ci,
        "bar_evidence_complete": evidence_complete,
        "constant_floor_status": c["CONSTANT_FLOOR_COMPARED"]["status"],
        "failed_conditions": sorted(failed), "unknown_conditions": sorted(unknown),
    }

# Set False only by --_disable_guard, to prove in the self-test that the guard is load-bearing.
GUARD_ENABLED = True


# ------------------------------------------------------------------ the mandatory control arm
def string_form_profile(words: Sequence[str], dim: int = STRING_CONTROL_DIM) -> np.ndarray:
    """Hashed character-trigram profile per word, rows L2-normalized. Shape [len(words), dim].

    Pure SURFACE STRING content: no meaning, no corpus, no training. Cosine between two rows is a
    morphology/spelling similarity. Uses hashlib, never the built-in hash(), so the arm is
    reproducible across processes (PROT-023 determinism).
    """
    mat = np.zeros((len(words), dim), dtype=np.float64)
    for i, w in enumerate(words):
        s = "^" + str(w) + "$"
        for k in range(len(s) - 2):
            j = int.from_bytes(hashlib.sha256(s[k:k + 3].encode("utf-8")).digest()[:4], "big") % dim
            mat[i, j] += 1.0
        nrm = float(np.linalg.norm(mat[i]))
        if nrm >= 1e-9:
            mat[i] /= nrm
    return mat


def string_control_scores(query: str, candidates: Sequence[str],
                          dim: int = STRING_CONTROL_DIM) -> np.ndarray:
    """Zero-meaning auxiliary similarity of `query` against each candidate. Shape [len(candidates)].

    Drop-in for whatever aux similarity the treatment arm blends: score the control arm with the
    IDENTICAL blend mechanism and the IDENTICAL weight, so the only difference between the arms is
    whether the auxiliary signal carries meaning.
    """
    prof = string_form_profile([query] + list(candidates), dim=dim)
    return prof[1:] @ prof[0]


# ------------------------------------------------------------------ the gate
def _get(d: Optional[dict], *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur


def _margin(arm: Optional[dict]) -> Optional[float]:
    """Separation margin, preferring the RESTANDARDIZED form when a cell reports it.

    `separation_margin_z` as emitted by exp_meaning_supply_separation_v1 is measured in sd units of
    the item's candidate pool but on a blended score z(base)+w*sum(z(aux)) that is NOT itself
    restandardized, so an arm carrying more aux weight has a mechanically larger |margin|. New cells
    must report `separation_margin_z.restandardized`; this reader uses it when present.
    """
    r = _get(arm, "separation_margin_z", "restandardized")
    if r is None:
        r = _get(arm, "separation_margin_z", "mean")
    if r is None:
        r = _get(arm, "separation_margin")
    return None if r is None else float(r)


def evaluate(arm: dict,
             base: dict,
             stringctrl: Optional[dict],
             *,
             arm_minus_floor_ci_lo: Optional[float] = None,
             arm_minus_stringctrl_ci_lo: Optional[float] = None,
             tautology_rate: Optional[float] = None,
             arm_name: str = "ARM",
             floor_source: Optional[str] = None) -> dict:
    """Score one candidate arm against the hardened four-condition C3 gate.

    HG1 MAGNITUDE_WITH_FLOOR       hit@1 >= 0.10, CI on (arm - recorded floor) excludes 0,
                                   tautology rate < 0.10.
    HG2 DISTRIBUTION_MOVED         median target rank strictly improves AND frac-gold-in-top-50
                                   strictly improves, vs the SAME cell's base arm on the SAME items.
    HG3 SEPARATION_NOT_DEGRADED    separation margin does not fall below the base arm's.
    HG4 STRING_CONTROL_BEATEN      a zero-meaning string-form arm was RUN, and the CI on
                                   (arm - string control) excludes 0.

    Returns {"status": PASS|FAIL|NOT_EVALUABLE, "conditions": {...}, "reasons": [...]}.
    Missing evidence is NOT_EVALUABLE. It is never PASS.
    """
    cond: Dict[str, dict] = {}
    missing: List[str] = []

    def need(val, label):
        if val is None:
            missing.append(label)
        return val

    # ---- HG1 magnitude, against a recorded floor
    h = need(_get(arm, "hit_at_1"), f"{arm_name}.hit_at_1")
    taut = tautology_rate if tautology_rate is not None else _get(arm, "tautology_rate")
    hg1_parts = {
        "hit_at_1": h,
        "threshold": HIT_AT_1_FLOOR,
        "arm_minus_floor_ci_lo": arm_minus_floor_ci_lo,
        # NAMES which control supplied the floor this arm was measured against (standing rule:
        # a floor is max(orthographic, frequency, scramble), never a bare number) -- e.g.
        # "A5_STRINGCTRL" (orthographic), "F_FREQUENCY", or a scramble arm. The scramble arms
        # themselves are donor-rule dependent -- F_SCRAMBLE in exp_meaning_supply_separation_v1
        # is a conflict-avoiding derangement (0.0080); F_SCRAMBLE_ON/OFF in
        # exp_graded_path_vs_orthographic_floor_v1 is a plain permutation (0.01375), the looser,
        # more conservative construction. floor_source makes that provenance explicit per-arm
        # rather than leaving "the floor" ambiguous.
        "floor_source": floor_source,
        "tautology_rate": taut,
        "tautology_ceiling": TAUTOLOGY_CEILING,
    }
    if h is None or arm_minus_floor_ci_lo is None or taut is None:
        if arm_minus_floor_ci_lo is None:
            missing.append(f"{arm_name}-minus-floor CI")
        if taut is None:
            missing.append(f"{arm_name}.tautology_rate")
        cond["HG1_MAGNITUDE_WITH_FLOOR"] = {"ok": None, **hg1_parts}
    else:
        cond["HG1_MAGNITUDE_WITH_FLOOR"] = {
            "ok": bool(h >= HIT_AT_1_FLOOR and arm_minus_floor_ci_lo > 0
                       and taut < TAUTOLOGY_CEILING),
            **hg1_parts,
        }

    # ---- HG2 the whole distribution moved, not just the argmax
    ar, br = _get(arm, "median_rank"), _get(base, "median_rank")
    at, bt = _get(arm, "frac_gold_in_top50"), _get(base, "frac_gold_in_top50")
    for v, lbl in ((ar, f"{arm_name}.median_rank"), (br, "base.median_rank"),
                   (at, f"{arm_name}.frac_gold_in_top50"), (bt, "base.frac_gold_in_top50")):
        need(v, lbl)
    if None in (ar, br, at, bt):
        cond["HG2_DISTRIBUTION_MOVED"] = {"ok": None, "median_rank": [br, ar],
                                          "frac_gold_in_top50": [bt, at]}
    else:
        cond["HG2_DISTRIBUTION_MOVED"] = {
            "ok": bool(ar < br and at > bt),
            "median_rank": [br, ar], "frac_gold_in_top50": [bt, at],
        }

    # ---- HG3 within-neighbourhood separation did not degrade
    am, bm = _margin(arm), _margin(base)
    for v, lbl in ((am, f"{arm_name}.separation_margin"), (bm, "base.separation_margin")):
        need(v, lbl)
    if None in (am, bm):
        cond["HG3_SEPARATION_NOT_DEGRADED"] = {"ok": None, "separation_margin": [bm, am]}
    else:
        cond["HG3_SEPARATION_NOT_DEGRADED"] = {"ok": bool(am >= bm),
                                               "separation_margin": [bm, am]}

    # ---- HG4 THE GUARD: the zero-meaning string arm must exist and must be beaten
    if GUARD_ENABLED and stringctrl is None:
        missing.append("string-form control ARM (mandatory; see tools/c3_gate.string_control_scores)")
        cond["HG4_STRING_CONTROL_BEATEN"] = {"ok": None, "stringctrl_arm_present": False}
    else:
        present = stringctrl is not None
        ch = _get(stringctrl, "hit_at_1")
        if arm_minus_stringctrl_ci_lo is None:
            missing.append(f"{arm_name}-minus-stringctrl paired CI")
            cond["HG4_STRING_CONTROL_BEATEN"] = {"ok": None, "stringctrl_arm_present": present,
                                                 "stringctrl_hit_at_1": ch,
                                                 "ci_lo": None}
        else:
            cond["HG4_STRING_CONTROL_BEATEN"] = {
                "ok": bool(arm_minus_stringctrl_ci_lo > 0),
                "stringctrl_arm_present": present, "stringctrl_hit_at_1": ch,
                "ci_lo": arm_minus_stringctrl_ci_lo,
            }

    failed = [k for k, v in cond.items() if v["ok"] is False]
    unknown = [k for k, v in cond.items() if v["ok"] is None]
    if failed:
        status = FAIL
    elif unknown:
        status = NOT_EVALUABLE
    else:
        status = PASS

    reasons = []
    if failed:
        reasons.append("FAILS: " + ", ".join(sorted(failed)))
    if unknown:
        reasons.append("NOT EVALUABLE on " + ", ".join(sorted(unknown))
                       + " | missing: " + "; ".join(sorted(set(missing))))
    if status == PASS:
        reasons.append("all four conditions hold")
    return {"arm": arm_name, "status": status, "conditions": cond, "reasons": reasons}


def _floor_ci_lo(name: str, deltas: dict, string_arm: str) -> tuple:
    """(arm - floor) CI lower bound, floor = max(orthographic, frequency, scramble).

    Returns (ci_lo, source) -- source NAMES the control that produced the binding floor, so a
    report never has to say "the floor" without saying which one (donor-rule for a scramble
    control is itself a choice: conflict-avoiding derangement vs plain permutation give
    different, both-correct numbers; naming the source arm makes that traceable).

    Two sources for ci_lo, combined by MIN -- the tightest bound governs, because beating the
    HIGHEST floor is what a floor comparison means (the standing rule: a gate is a margin above
    max(...), never above whichever single control happens to be easiest to beat):

      1. DIRECT arm-vs-floor deltas, `d_{name}_minus_{FLOOR_ARM}`, for every floor-shaped arm
         name (see FLOOR_ARM_NAMES) the cell actually recorded a paired delta against. This is
         the path that was missing entirely before 2026-08-15: a cell that ran an orthographic
         or frequency control and recorded `d_{name}_minus_F_FREQUENCY` /
         `d_{name}_minus_A5_STRINGCTRL` etc. had that number sitting unread.
      2. The legacy scramble-only chain through the base arm
         (`d_{name}_minus_BASE` composed with `d_A1_BASE_minus_F_SCRAMBLE` or equivalent),
         kept as a FALLBACK ONLY for cells that predate the orthographic/frequency controls and
         never recorded any direct arm-vs-floor delta at all.
    """
    direct = []
    for cand in set(FLOOR_ARM_NAMES) | {string_arm}:
        if cand == name:
            continue
        v = _get(deltas, f"d_{name}_minus_{cand}", "ci_lo")
        if v is not None:
            direct.append((v, cand))
    if direct:
        # ONE implementation of "take the MIN ci_lo": min_ci_lo(). tools/verdict_bar_check.py
        # calls the SAME function, so the two tools cannot drift apart on the conservative rule.
        return min_ci_lo(direct)
    d_arm_base = _get(deltas, f"d_{name}_minus_BASE", "ci_lo")
    d_base_floor = _get(deltas, "d_A1_BASE_minus_F_SCRAMBLE", "ci_lo")
    floor_src = "F_SCRAMBLE (via BASE chain)"
    if d_base_floor is None:
        d_base_floor = _get(deltas, f"d_{name}_minus_B6_OPEN_SCRAMBLE", "ci_lo")
        floor_src = "B6_OPEN_SCRAMBLE (via BASE chain)"
        if d_base_floor is None:
            d_base_floor = _get(deltas, "d_B5_minus_B6", "ci_lo")
            floor_src = "B5_minus_B6 (via BASE chain)"
        d_arm_base = d_base_floor
    if d_arm_base is not None and d_base_floor is not None:
        return min(d_arm_base, d_base_floor), floor_src
    return None, None


# ------------------------------------------------------------------ scoring a metrics.json
def _open_vocab_pseudo_arms(m: dict) -> Optional[tuple]:
    """Adapter for exp_grounding_readout_known_answer_v1's own layout.

    That cell -- the one the 4.80% C3 headline comes from -- reports ONLY hit@1 and the tautology
    rate for its open-vocabulary arms. It records no median rank, no top-50 fraction and no
    separation margin, so it is structurally unable to answer HG2/HG3, and it ran no string-form
    control at all. Scoring it here makes that visible instead of crashing.
    """
    ov = _get(m, "stage_b", "open_vocabulary_readout")
    if not isinstance(ov, dict) or "hit_at_1" not in ov:
        return None
    per_arm = {k: {"hit_at_1": _get(v, "acc")} for k, v in ov["hit_at_1"].items()}
    boot = {"deltas": {}}
    for name, d in (ov.get("delta") or {}).items():
        boot["deltas"][name] = d
    return ("open_vocab", per_arm, boot)


def score_metrics(path: str, base_arm: str = "A1_BASE", string_arm: str = "A5_STRINGCTRL",
                  only_arm: Optional[str] = None,
                  tautology_rate: Optional[float] = None) -> List[dict]:
    """Re-score every arm of a metrics.json that carries a per_w/per_arm block."""
    with open(path, "r", encoding="utf-8") as fh:
        m = json.load(fh)

    blocks = []
    if isinstance(m.get("per_w"), dict):
        for w, blk in sorted(m["per_w"].items()):
            blocks.append((w, blk.get("per_arm", {}), blk.get("bootstrap", {})))
    elif isinstance(m.get("per_arm"), dict):
        blocks.append(("-", m["per_arm"], m.get("bootstrap", {})))
    else:
        ov = _open_vocab_pseudo_arms(m)
        if ov is None:
            raise SystemExit(f"[c3_gate] {path}: no per_w/per_arm block -- cannot score. "
                             "A C3 claim must report per-arm hit@1, median_rank, "
                             "frac_gold_in_top50 and separation margin.")
        blocks.append(ov)

    # A tautology rate reported once for the cell applies to every arm unless overridden.
    cell_taut = tautology_rate
    if cell_taut is None:
        cell_taut = _get(m, "stage_b", "open_vocabulary_readout", "tautology_rate")
    if cell_taut is None:
        cell_taut = m.get("tautology_rate")

    out = []
    for w, per_arm, boot in blocks:
        base = per_arm.get(base_arm)
        ctrl = per_arm.get(string_arm)
        deltas = boot.get("deltas", {}) if isinstance(boot, dict) else {}
        for name in sorted(per_arm):
            if name == base_arm or (only_arm and name != only_arm):
                continue
            # (arm - floor) CI, floor = max(orthographic, frequency, scramble) -- see
            # _floor_ci_lo's docstring for why this replaced a scramble-only lookup 2026-08-15.
            floor_ci, floor_src = _floor_ci_lo(name, deltas, string_arm)
            d_ctrl = _get(deltas, f"d_{name}_minus_{string_arm}", "ci_lo")
            r = evaluate(per_arm[name], base or {}, ctrl,
                         arm_minus_floor_ci_lo=floor_ci,
                         arm_minus_stringctrl_ci_lo=d_ctrl,
                         tautology_rate=cell_taut,
                         arm_name=name,
                         floor_source=floor_src)
            r["w"] = w
            out.append(r)
    return out


def _fmt(r: dict) -> str:
    c = r["conditions"]

    def mark(k):
        v = c[k]["ok"]
        return "PASS" if v is True else ("FAIL" if v is False else "  ? ")
    floor_src = c.get("HG1_MAGNITUDE_WITH_FLOOR", {}).get("floor_source")
    return ("  %-16s w=%-6s %-14s HG1 %s | HG2 %s | HG3 %s | HG4 %s  floor=%s\n      %s"
            % (r["arm"], r.get("w", "-"), r["status"],
               mark("HG1_MAGNITUDE_WITH_FLOOR"), mark("HG2_DISTRIBUTION_MOVED"),
               mark("HG3_SEPARATION_NOT_DEGRADED"), mark("HG4_STRING_CONTROL_BEATEN"),
               floor_src or "(none)",
               " ".join(r["reasons"])))


# ------------------------------------------------------------------ self-test
def _arm(hit, rank, top50, margin):
    return {"hit_at_1": hit, "median_rank": rank, "frac_gold_in_top50": top50,
            "separation_margin_z": {"mean": margin}}


def self_test() -> int:
    """Prove the guard: a C3 claim with NO string-form control can never come back PASS.

    Five cases, three of them replays of numbers measured on disk 2026-08-14.
    """
    ok = True

    def check(label, got, want):
        nonlocal ok
        if got == want:
            print(f"[self-test] PASS {label} -> {got}")
        else:
            print(f"[self-test] FAIL {label} -> {got}, expected {want}", file=sys.stderr)
            ok = False

    # Measured base arm (exp_meaning_supply_separation_v1 A1_BASE == the 4.80% C3 headline).
    base = _arm(0.0480, 37.0, 0.5565, -2.5422609616204763)

    # CASE 1 -- THE GUARD. An arm that clears every OTHER condition (hit@1, rank, top-50 and
    # separation all good) but ran NO string control. Must be NOT_EVALUABLE, so that the missing
    # control is the ONLY thing deciding the outcome. If this ever returns PASS the gate is back to
    # the state that let a trigram control through on 2026-08-14.
    gamer = _arm(0.1200, 30.0, 0.6000, -2.40)
    r = evaluate(gamer, base, None, arm_minus_floor_ci_lo=0.03, tautology_rate=0.0,
                 arm_name="NO_CONTROL")
    check("no string-control arm is NOT_EVALUABLE, never PASS", r["status"], NOT_EVALUABLE)
    check("  and it names the missing arm",
          "string-form control ARM" in " ".join(r["reasons"]), True)

    # CASE 2 -- MEASURED REPLAY. exp_meaning_supply_separation_v1 A5_STRINGCTRL at w=1.00: hit@1
    # 0.10275 (clears 10%), median rank 31.0 < 37.0, top-50 0.58675 > 0.5565 -- so hit@1 + rank +
    # top-50 ALL pass. Only the separation margin (-5.473 vs -2.542) catches it.
    a5 = _arm(0.10275, 31.0, 0.58675, -5.473060945852469)
    r = evaluate(a5, base, a5, arm_minus_floor_ci_lo=0.04375,
                 arm_minus_stringctrl_ci_lo=0.0, tautology_rate=0.0, arm_name="A5_STRINGCTRL")
    check("measured trigram control at w=1.00 is FAIL", r["status"], FAIL)
    check("  HG1 magnitude alone would have PASSED it",
          r["conditions"]["HG1_MAGNITUDE_WITH_FLOOR"]["ok"], True)
    check("  HG2 rank+top50 alone would ALSO have passed it",
          r["conditions"]["HG2_DISTRIBUTION_MOVED"]["ok"], True)
    check("  HG3 separation is what stops it",
          r["conditions"]["HG3_SEPARATION_NOT_DEGRADED"]["ok"], False)

    # CASE 3 -- the string control REPRODUCES a real arm's gain. Must FAIL on HG4 alone.
    good = _arm(0.1100, 20.0, 0.6600, -2.30)
    r = evaluate(good, base, a5, arm_minus_floor_ci_lo=0.05,
                 arm_minus_stringctrl_ci_lo=-0.004, tautology_rate=0.0, arm_name="REPRODUCED")
    check("string control reproduces the gain -> FAIL", r["status"], FAIL)
    check("  and only HG4 is the failing condition",
          [k for k, v in r["conditions"].items() if v["ok"] is False],
          ["HG4_STRING_CONTROL_BEATEN"])

    # CASE 4 -- NON-VACUITY. A well-formed genuine win must PASS, or the gate is unusable.
    r = evaluate(good, base, a5, arm_minus_floor_ci_lo=0.05,
                 arm_minus_stringctrl_ci_lo=0.006, tautology_rate=0.0, arm_name="GENUINE")
    check("a genuine, string-control-beating arm PASSES (gate is not vacuous)", r["status"], PASS)

    # CASE 5 -- MEASURED REPLAY, the best real arm. A4_BOTH at w=1.00 clears HG1/HG2/HG3 and is
    # NOT_EVALUABLE only because the cell never computed the arm-minus-stringctrl paired CI.
    a4 = _arm(0.1190, 13.0, 0.7040, -2.3670214335543847)
    r = evaluate(a4, base, a5, arm_minus_floor_ci_lo=0.03775, tautology_rate=0.0,
                 arm_name="A4_BOTH")
    check("measured A4_BOTH w=1.00 is NOT_EVALUABLE (no paired CI vs the control)",
          r["status"], NOT_EVALUABLE)
    check("  but it does clear HG3, so the gate is reachable by real meaning",
          r["conditions"]["HG3_SEPARATION_NOT_DEGRADED"]["ok"], True)

    # CASE 6 -- the control constructor itself carries no meaning: morphological relatives score
    # high, synonyms score low. This is why it is the right zero-meaning control.
    s = string_control_scores("abnormality", ["abnormal", "duplication", "chromosomal"])
    check("string control ranks 'abnormal' above 'duplication' for 'abnormality'",
          bool(s[0] > s[1]), True)
    s2 = string_control_scores("sofa", ["couch", "sofas"])
    check("string control ranks 'sofas' above the SYNONYM 'couch' (no meaning in it)",
          bool(s2[1] > s2[0]), True)

    # CASE 7 -- _floor_ci_lo must use the WORST (highest) floor, not merely a scramble floor,
    # replaying the exact shape of exp_graded_path_vs_orthographic_floor_v1's bootstrap block
    # (data/exp_graded_path_vs_orthographic_floor_v1/metrics.json): an arm that clears scramble
    # comfortably but sits BELOW the orthographic control must get a floor_ci_lo that is
    # negative (from the orthographic delta), not the positive one scramble alone would give.
    deltas_mixed = {
        "d_ARM_minus_F_SCRAMBLE_ON": {"ci_lo": 0.02675},   # beats scramble: positive margin
        "d_ARM_minus_A5_STRINGCTRL": {"ci_lo": -0.05},     # loses to orthographic: negative
        "d_ARM_minus_F_FREQUENCY": {"ci_lo": 0.02175},     # beats frequency: positive margin
    }
    fc, fc_src = _floor_ci_lo("ARM", deltas_mixed, "A5_STRINGCTRL")
    check("floor_ci_lo takes the WORST floor (orthographic), not scramble alone",
          fc, -0.05)
    check("  and names its source as the orthographic control",
          fc_src, "A5_STRINGCTRL")

    # and the legacy scramble-only chain still works when no direct floor delta exists at all
    # (pre-orthographic-control cells must not regress to NOT_EVALUABLE).
    deltas_legacy = {
        "d_ARM_minus_BASE": {"ci_lo": 0.02},
        "d_A1_BASE_minus_F_SCRAMBLE": {"ci_lo": 0.01},
    }
    fc2, fc2_src = _floor_ci_lo("ARM", deltas_legacy, "A5_STRINGCTRL")
    check("floor_ci_lo falls back to the legacy scramble-only chain when no direct delta exists",
          fc2, 0.01)
    check("  and names the legacy chain as its source",
          fc2_src, "F_SCRAMBLE (via BASE chain)")

    # CASE 8 -- ARM ROLE CLASSIFICATION (added 2026-08-16 for tools/verdict_bar_check.py).
    # Naming drift is the enemy here: the verdict vocabulary went from 13 strings in June to 444
    # in July, and floor arms are named just as loosely. Classification is by SHAPE, and these
    # cases are the shapes actually found on disk.
    for nm, want in (("A5_STRINGCTRL", "orthographic"), ("A6_TRIGRAM_ONLY", "orthographic"),
                     ("A_ORTHOGRAPHIC", "orthographic"), ("A7_PREFIX_ONLY", "orthographic"),
                     ("HARDENED_FREQUENCY_FREQ_MIN", "frequency"), ("F_FREQUENCY", "frequency"),
                     ("F_SCRAMBLE_ON", "scramble"), ("B6_OPEN_SCRAMBLE", "scramble"),
                     ("SCRAMBLE_NULL_P95", "scramble"),
                     ("random_chance", "random_chance"),
                     ("CTRL_RANDINIT_CTX", "null_control"),
                     ("GLOVE_POSITIVE_CONTROL", "known_answer"),
                     # THE FOURTH FLOOR (2026-08-16). Every name below was enumerated from disk.
                     ("F5_CONSTANT_PROTOTYPE_zero_query_information", "constant_prototype"),
                     ("F4_CONSTANT_PROTOTYPE", "constant_prototype"),
                     ("F_CONSTANT_PROTOTYPE", "constant_prototype"),
                     ("B_vs_OWN_CONSTANT_PROTOTYPE", "constant_prototype"),
                     ("constant_prototype_floor", "constant_prototype"),
                     # ... and the OVER-FIRE guards, which matter more than the hits. The first
                     # two must keep their EXISTING roles or the fourth floor would have stolen
                     # 386 frequency arms and 282 oracle arms; the rest are genuine TREATMENT
                     # arms that merely contain PROTOTYPE / CENTROID / "constants".
                     ("F3_FREQUENCY_ONLY_constant", "frequency"),
                     ("ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor", "known_answer"),
                     ("B_ORACLE_CONSTANT_GOLD_DEGREE_not_a_floor", "known_answer"),
                     ("ARM_HRR_BUNDLE_PROTOTYPE", None),
                     ("C_ISO_GLOBAL_CENTROID_beta0.50", None),
                     ("memorize_prototype", None),
                     ("v4_constants", None),
                     ("S5_balanced_pool_kills_constant_rankings", None),
                     ("A4_BOTH", None), ("d512|ASSET_RETRAIN_CTX", None)):
        check(f"classify_arm_role({nm!r})", classify_arm_role(nm), want)
    check("a chance baseline is NOT one of the required floor roles",
          "random_chance" in REQUIRED_FLOOR_ROLES, False)
    # THE DRIFT THAT CAUSED THIS FIX, asserted so it cannot recur silently: the two lists that
    # state "what the required floor set is" must agree. floor_battery carried four members for
    # a day while this file carried three, and every gate evaluation in that window formed its
    # max without the strongest floor.
    check("REQUIRED_FLOOR_ROLES has four members and names the constant floor",
          (len(REQUIRED_FLOOR_ROLES), CONSTANT_FLOOR_ROLE in REQUIRED_FLOOR_ROLES), (4, True))
    try:
        from tools.floor_battery import FLOOR_SET_REQUIRED as _FB
    except ImportError:                                            # pragma: no cover
        _FB = None
    if _FB is not None:
        check("  and it matches tools/floor_battery.FLOOR_SET_REQUIRED member for member",
              sorted(r.upper().replace("CONSTANT_PROTOTYPE", "CONSTANT_PROTOTYPE")
                     for r in REQUIRED_FLOOR_ROLES),
              sorted(x.upper() for x in _FB))
    else:
        print("[self-test] SKIP floor_battery not importable; the two-list agreement is UNCHECKED")
    # A CONSTANT FLOOR MAY NOT CARRY A CLAIM. Before this fix it could: the role did not exist,
    # so the arm classified as None and claim_arm_eligibility returned eligible=True.
    check("a constant-prototype floor arm is NOT eligible to carry a claim",
          claim_arm_eligibility(["EXACT_KEY", "F5_CONSTANT_PROTOTYPE", "MARGIN_per_floor"])
          ["reason"], CLAIM_ARM_CONTROL)

    # CASE 9 -- min_ci_lo is the ONE conservative rule and it names its source.
    check("min_ci_lo takes the minimum, not the first or the largest",
          min_ci_lo([(0.07, "SCRAMBLE"), (-0.0156, "FREQUENCY"), (0.045, "ORTHO")]),
          (-0.0156, "FREQUENCY"))
    check("min_ci_lo on nothing is (None, None)", min_ci_lo([]), (None, None))

    # CASE 10 -- THE STANDING BAR, replaying the measured shape of
    # data/exp_meaning_asset_calibrated_floor_verdict_v1 row d512|ASSET_RETRAIN_CTX. Its verdict
    # string reads as a clearance; two of its three floors do not separate.
    r = evaluate_standing_bar(
        floor_ci_pairs=[(0.0455, "A_ORTHOGRAPHIC"), (-0.0156, "HARDENED_FREQUENCY_FREQ_MIN"),
                        (0.0704, "SCRAMBLE_NULL_P95")],
        floor_roles_present=["orthographic", "frequency", "scramble"],
        floor_roles_with_ci=["orthographic", "frequency", "scramble"],
        has_known_answer_arm=False, has_null_arm=True, arm_name="d512|ASSET_RETRAIN_CTX")
    check("measured ASSET_RETRAIN_CTX FAILS the standing bar", r["status"], BAR_FAILS)
    check("  and the FREQUENCY floor is named as the binding one",
          r["binding_floor"], "HARDENED_FREQUENCY_FREQ_MIN")
    check("  and picking the highest-POINT floor alone would have passed it",
          r["conditions"]["MARGIN_CI_SEPARATED"]["min_ci_lo"] < 0 < 0.0704, True)

    # CASE 11 -- NON-VACUITY for the standing bar: a fully-evidenced win must MEET it, or the
    # checker built on this predicate flags everything and is worthless. FOUR floors since
    # 2026-08-16.
    _FOUR = ["orthographic", "frequency", "scramble", CONSTANT_FLOOR_ROLE]
    r = evaluate_standing_bar(
        floor_ci_pairs=[(0.0455, "A_ORTHOGRAPHIC"), (0.0210, "F_FREQUENCY"),
                        (0.0704, "F_SCRAMBLE"), (0.0180, "F5_CONSTANT_PROTOTYPE")],
        floor_roles_present=_FOUR, floor_roles_with_ci=_FOUR,
        has_known_answer_arm=True, has_null_arm=True, arm_name="GENUINE")
    check("a fully-evidenced arm MEETS the standing bar (predicate is not vacuous)",
          r["status"], BAR_MEETS)
    check("  and its evidence is marked complete", r["bar_evidence_complete"], True)
    check("  and the constant floor is recorded as COMPARED",
          r["constant_floor_status"], CONSTANT_FLOOR_COMPARED)

    # CASE 11b -- THE NEGATIVE CONTROL FOR THE FOURTH FLOOR, and the whole point of this fix.
    # ONE VARIABLE: the identical arm, the identical three margins, the constant floor simply
    # never run. Before 2026-08-16 this returned MEETS_BAR with bar_evidence_complete=True --
    # a max formed from three floors, presented as the standing bar. It must now withhold.
    r = evaluate_standing_bar(
        floor_ci_pairs=[(0.0455, "A_ORTHOGRAPHIC"), (0.0210, "F_FREQUENCY"),
                        (0.0704, "F_SCRAMBLE")],
        floor_roles_present=["orthographic", "frequency", "scramble"],
        floor_roles_with_ci=["orthographic", "frequency", "scramble"],
        has_known_answer_arm=True, has_null_arm=True, arm_name="THREE_FLOORS_ONLY")
    check("the SAME arm without a constant floor is NO_EVIDENCE, not a pass", r["status"],
          BAR_NO_EVIDENCE)
    check("  and the missing floor is NAMED, not merely counted",
          (r["constant_floor_status"],
           r["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["not_compared"]),
          (NO_CONSTANT_FLOOR, [CONSTANT_FLOOR_ROLE]))
    check("  and its evidence is NOT marked complete", r["bar_evidence_complete"], False)
    # CASE 11c -- and the constant floor must be able to BIND, not merely be present: an arm
    # that clears the old three but LOSES to the constant floor now FAILS. These are the
    # synonym cell's own OPEN-pool / LANDED-criterion numbers
    # (.claude/scan-out/synonym-substitution-metric.json section 3): R0 0.0223 with
    # F5_CONSTANT_PROTOTYPE binding at -0.1167 [-0.1282, -0.1054].
    r = evaluate_standing_bar(
        floor_ci_pairs=[(0.0146, "F1_TRIGRAM"), (0.0038, "F3_FREQUENCY"),
                        (0.0085, "NULL_SCRAMBLED"), (-0.1282, "F5_CONSTANT_PROTOTYPE")],
        floor_roles_present=_FOUR, floor_roles_with_ci=_FOUR,
        has_known_answer_arm=True, has_null_arm=True, arm_name="R0_CTX_DENSE")
    check("an arm that clears the old three but loses to the CONSTANT floor FAILS the bar",
          (r["status"], r["binding_floor"]), (BAR_FAILS, "F5_CONSTANT_PROTOTYPE"))

    # CASE 12 -- the three failure modes are INDEPENDENT: no floor, no CI, and incomplete
    # coverage each produce their own distinct finding rather than collapsing into one.
    r = evaluate_standing_bar(floor_ci_pairs=[], floor_roles_present=[], floor_roles_with_ci=[],
                              has_known_answer_arm=False, has_null_arm=False, arm_name="BARE")
    check("a bare-threshold cell FAILS on FLOOR_PRESENT",
          r["conditions"]["FLOOR_PRESENT"]["ok"], False)
    check("  and its separation is UNKNOWN, not False (no evidence != refuted)",
          r["conditions"]["MARGIN_CI_SEPARATED"]["ok"], None)
    r = evaluate_standing_bar(floor_ci_pairs=[], floor_roles_present=["scramble"],
                              floor_roles_with_ci=[],
                              has_known_answer_arm=True, has_null_arm=True, arm_name="FLOOR_NO_CI")
    check("a floor-without-CI cell FAILS on CI_PRESENT and not on FLOOR_PRESENT",
          (r["conditions"]["FLOOR_PRESENT"]["ok"], r["conditions"]["CI_PRESENT"]["ok"]),
          (True, False))
    r = evaluate_standing_bar(floor_ci_pairs=[(0.20, "SCRAMBLE_NULL_P95")],
                              floor_roles_present=["orthographic", "frequency", "scramble"],
                              floor_roles_with_ci=["scramble"],
                              has_known_answer_arm=True, has_null_arm=True, arm_name="PARTIAL_COV")
    # An arm that separates from the ONE floor it was paired against has not been shown to clear
    # max(ortho, freq, scramble) -- that is NO_EVIDENCE, not a clearance. Measured on disk
    # 2026-08-16: exp_meaning_asset_pretrained_positive_control_v1 and
    # exp_context_conditioned_near_neighbour_v1 both have this shape, and calling either of them
    # MEETS_BAR would reproduce the exact "cleared its strongest floor" error being audited.
    check("separating from only the floor it MEASURED is NO_EVIDENCE, not a clearance",
          (r["status"], r["required_floor_roles_without_margin_ci"], r["bar_evidence_complete"]),
          (BAR_NO_EVIDENCE, ["orthographic", "frequency"], False))
    check("  and the uncompared floors are named",
          r["conditions"]["ALL_REQUIRED_FLOORS_COMPARED"]["not_compared"],
          ["orthographic", "frequency", CONSTANT_FLOOR_ROLE])

    # NEGATIVE CONTROL for the guard: with the guard disabled, CASE 1 must stop being protected.
    global GUARD_ENABLED
    GUARD_ENABLED = False
    try:
        r = evaluate(gamer, base, None, arm_minus_floor_ci_lo=0.03,
                     arm_minus_stringctrl_ci_lo=0.01, tautology_rate=0.0, arm_name="NO_CONTROL")
        check("guard DISABLED: the same no-control arm becomes PASS (guard is load-bearing)",
              r["status"], PASS)
    finally:
        GUARD_ENABLED = True

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--score", metavar="METRICS_JSON", help="re-score a cell's arms under the gate")
    ap.add_argument("--arm", default=None, help="score only this arm")
    ap.add_argument("--base-arm", default="A1_BASE")
    ap.add_argument("--string-arm", default="A5_STRINGCTRL")
    ap.add_argument("--json", action="store_true", help="emit the full per-condition JSON")
    ap.add_argument("--tautology", type=float, default=None,
                    help="tautology rate to apply when the cell inherits it from another cell "
                         "(state the inheritance in the report; do not assume it)")
    ap.add_argument("--self-test", action="store_true", help="prove the mandatory-control guard")
    ap.add_argument("--_disable_guard", action="store_true",
                    help="self-test only: negative control for the guard")
    args = ap.parse_args(argv)

    if args._disable_guard:
        global GUARD_ENABLED
        GUARD_ENABLED = False
        print("[c3_gate] WARNING guard DISABLED (negative control)")

    if args.self_test:
        return self_test()

    if not args.score:
        ap.print_help()
        return 2

    rows = score_metrics(args.score, base_arm=args.base_arm, string_arm=args.string_arm,
                         only_arm=args.arm, tautology_rate=args.tautology)
    if args.json:
        print(json.dumps(rows, indent=1))
    else:
        print(f"[c3_gate] {args.score}")
        for r in rows:
            print(_fmt(r))
    n_pass = sum(1 for r in rows if r["status"] == PASS)
    print(f"[c3_gate] {n_pass} of {len(rows)} arm-by-w cells PASS the hardened C3 gate")
    return 0 if n_pass else 1


if __name__ == "__main__":
    sys.exit(main())
