#!/usr/bin/env python
"""Graded brain-fidelity score: a FALSIFIABLE number, or no number at all.

WHAT THIS MEASURES, AND WHAT IT DOES NOT
========================================
This scores RESEMBLANCE TO A BIOLOGICAL SPECIFICATION. It does NOT measure capability,
and it is not a predictor of whether a component will win.

Read that twice, because the whole value of the score depends on nobody substituting it for
a measurement. From our own retrodiction (`--retrodict`), off disk:

  * hub-and-spoke role addressing scores 100% and DID NOT BEAT the flat bag it was
    compared against (`data/exp_hub_spoke_partial_cue_curve_v1/metrics.json`).
  * the flat bag scores 25% and BEATS the conjunctive arm, which also scores 25%
    (`data/exp_perirhinal_conjunctive_readout_c3_v1/metrics.json`).
  * the CA3 completer scores 62.5% and was REFUTED at full scale
    (`data/exp_ca3_completion_partial_cue_v1/metrics.json`, PAIRING_HYPOTHESIS_REFUTED).

So: a high-fidelity component can lose, and a low-fidelity one can win. That is EXACTLY why
the floor-and-CI bar (PLAN R1: a CI-separated margin above max(orthographic, frequency,
scramble) on the identical scorer/n/pool/gold) stays a SEPARATE, INDEPENDENT gate. This
score can never clear that bar, soften it, or stand in for it. A component with a fidelity
score of 12/12 and no floored result has measured NOTHING.

What the score IS for: deciding WHAT TO BUILD and WHY A NEGATIVE HAPPENED. When a
brain-motivated component loses, the score says which axis we diverged on, so the answer can
be "we built the wrong regime" instead of "the brain's way does not work here".

WHAT IT COMPOSES WITH (it replaces nothing)
===========================================
  * the QUALITATIVE gate at 3e70c3ba4 -- `tools/dispatch_batch.py::BRAIN_FIDELITY_RULE` in
    every brief, and `brain_structure` + `fidelity_basis` required on registry rows. That
    gate asks "did you state it?". This asks "how far off is it?". Both are needed: a row
    can state all four clauses perfectly and describe a component that matches nothing.
  * `notes/ORGAN_MAP.md`'s 5-way per-organ classification (SAME / RIGHT-OP-WRONG-METRIC /
    RIGHT-OP-WRONG-PLACE / WRONG-OP / MISSING) and its honesty rule 1: "an organ whose brain
    math is UNPINNED cannot be scored for fidelity and is marked UNSCORABLE". D2 below is a
    strict refinement of that vocabulary, not a competitor to it.
  * PLAN R13 (which brain structure), R14 (exact-key does not transfer to partial-cue) and
    R1 (the floor).

THE HONESTY GATE IS PASS/FAIL AND IT VOIDS, IT DOES NOT DEDUCT
==============================================================
Invention is fully authorised and costs nothing. Presenting an invention as established
biology VOIDS THE WHOLE SCORE -- the tool emits no number at all. Failing this is not a low
score, it is NO score. Three clauses, each mechanically checked:

  H1  every claim carries a basis in {pinned, invention, contested, unpinned}.
  H2  a `pinned` claim must cite LITERATURE or an in-repo LITERATURE AUDIT. A pinned claim
      whose evidence is our own module, our own docstring, or our own experiment is a
      SELF-CITATION AS BIOLOGY and voids the score. This clause exists because
      `hdlab/iterative_attractor.py` documents `alpha = 0.5` as "brain-canonical" while
      `notes/ORGAN_MAP.md` D2 records that "the update rule is not stated in the biology --
      Hopfield sign-update and modern-Hopfield softmax are OUR imports". That is an
      invention wearing a pinned label, and it shipped.
  H3  a claim may not be both `pinned` and `invention`.

EVERY DIMENSION CITES ITS EVIDENCE. NO DEFAULT MIDDLE VALUE.
============================================================
A dimension with no citable basis scores 0. Never 1, never "probably fine". The one
exception is NOT an exception to that rule, it is a different state -- see UNPINNED below.

THE SIX DIMENSIONS (and where this differs from the starting proposal)
=====================================================================
D1 STRUCTURE SPECIFICITY -- is a NEURAL SYSTEM named?
   2 a specific neural system, named anatomically, whose relevant computation is documented.
   1 a specific neural system named, but the functional attribution to it is CONTESTED or
     our mapping onto it is loose.
   0 a cognitive-theory label ("working memory", "attention"), a computational model name
     ("random indexing", "modern Hopfield"), or nothing.
   CHANGED FROM THE PROPOSAL: the proposal's "1" bundled two opposite situations -- "we were
   sloppy" and "neuroscience has not answered". Those must not share a score. Whether the
   computation is documented now decides SCORABILITY of D2 (below), not the value of D1.

D2 OPERATION MATCH -- SHAPE, POSITION, METRIC, scored SEPARATELY then combined.
   Count how many of the three match: 3 -> 2, 2 -> 1, <=1 -> 0. Any of the three whose brain
   fact is UNPINNED is dropped from the count AND from the denominator.
   CHANGED: the proposal collapsed three questions into one 0-2 scale. ORGAN_MAP's own tally
   shows they come apart -- 13/38 organs are RIGHT-OP-WRONG-METRIC and 3/38 are
   RIGHT-OP-WRONG-PLACE, different populations. Collapsing them destroys information this
   project has already paid to produce. This form reproduces ORGAN_MAP's categories exactly:
   RIGHT-OP-WRONG-METRIC is D2=1 with metric=False.

D3 REGIME MATCH -- sparse/dense, PARTIAL-CUE/exact-key, graded/binary, timescale.
   Fraction of the APPLICABLE regime axes matched: >=0.9 -> 2, >=0.5 -> 1, else 0.
   UNCHANGED IN SUBSTANCE and it is load-bearing. The conjunctive organ failed precisely
   here: built and validated at an exact key, deployed against partial cues.

D4 ORGAN REUSE -- REPORTED, NOT SCORED BY DEFAULT.
   CHANGED, and this is the sharpest disagreement with the proposal. Whether WE reused OUR
   module is a fact about our codebase, not about whether our thing resembles the brain. A
   parallel build that matches the brain's operation is MORE faithful than a reuse of an
   unfaithful owned organ. This is not hypothetical: the CA3 completer scores 2 on D4 for
   reusing `hdlab/iterative_attractor.py` bit-identically, and that module's update rule is
   one ORGAN_MAP names as OUR import. So D4-as-a-scored-dimension REWARDS substituting
   something convenient, which is the exact move the gate exists to stop. Islanding is real
   and already has an owner: the WIRE-or-SHELVE registry gate. Pass --count-d4 to include it
   and see for yourself; `--retrodict --count-d4` shows it lifting the refuted CA3 arm.

D5 PAIRING COMPLETENESS -- is the matched partner organ PRESENT and REACHED?
   2 named partner, present, and reached at runtime. 1 named and present but NOT reached.
   0 absent, or no partner named at all.
   UNCHANGED. Dentate-gyrus separation with no CA3 completion is half an organ and we
   shipped exactly that.

D6 FAILURE-MODE MATCH -- does it degrade the way biological systems degrade?
   2 tracks or beats a matched reference across the degradation curve. 1 degrades faster but
   not CI-separated. 0 a cliff, CI-separated below the reference.
   CHANGED IN STATUS, not in content: D6 IS NOT SCORABLE AT DESIGN TIME. It needs a measured
   degradation curve, which by definition does not exist before the run. In `design_time`
   mode it is N/A. Scoring it in `post_hoc` mode is legitimate and useful, but a `post_hoc`
   score is a DESCRIPTION of a result, not a prediction of one -- see the retrodiction, where
   D6 supplies most of the apparent separating power and supplies it by leaking the outcome.

UNPINNED IS "NOT APPLICABLE", NOT ZERO -- and it must be EARNED
==============================================================
This is the single most important correction to the starting proposal, and it is a
correction the project has already made once and lost. The proposal's honesty gate says
invention "must NOT cost points"; its requirement 2 says a dimension with no citable basis
scores 0. Where the LITERATURE does not pin the brain fact (14 of 38 organs on today's
ORGAN_MAP), those two collide: an honest, well-motivated invention has no citable brain
basis, scores 0, and invention has cost 2 points on the heaviest dimension. That is the
exact fault `notes/ORGAN_MAP.md` sec 7 point 2 identified when it superseded
`notes/component_brain_fidelity_ledger.md` -- "it scored fidelity where the brain math is
UNPINNED".

Resolution: three outcomes per dimension, not two.
  * 0/1/2   the brain fact IS pinned and we match it to that degree, OR the brain fact is
            pinned and we diverged, OR no evidence was offered at all.
  * N/A     the brain fact is DOCUMENTED AS UNPINNED. Removed from numerator AND denominator.
  * 0       everything else, including "the author asserted N/A without a source".

N/A is not a free pass: claiming it requires citing the source that says the brain fact is
unpinned (a literature scan, or ORGAN_MAP's own UNPINNED marking, which is a lit-derived
audit). No source -> the claim is coerced to 0 and the coercion is RECORDED in the output.
So there is still no default middle value, and honest invention still costs nothing.

Consequence for reading the number: the score is a PERCENTAGE OF APPLICABLE POINTS and it is
meaningless without its COVERAGE. 6/6 over three scorable dimensions is NOT 12/12 over six.
The tool always prints both and refuses to print one alone.

CLI
===
  python tools/brain_fidelity_score.py --self-test
  python tools/brain_fidelity_score.py --retrodict [--count-d4] [--json]
  python tools/brain_fidelity_score.py --score-json <claims.json> [--mode design_time|post_hoc]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DIMENSIONS = ("D1", "D2", "D3", "D4", "D5", "D6")
SCORED_BY_DEFAULT = ("D1", "D2", "D3", "D5", "D6")   # D4 reported, not scored -- see docstring
DESIGN_TIME_DIMENSIONS = ("D1", "D2", "D3", "D5")     # D6 needs a measured degradation curve

VALID_BASIS = ("pinned", "invention", "contested", "unpinned")

# Evidence kinds. The split that matters is whether the evidence is ABOUT BIOLOGY or ABOUT US.
EVIDENCE_KINDS = (
    "literature",        # a primary source or review
    "in_repo_audit",     # a lit-derived audit in this repo (ORGAN_MAP, a lit_scan note)
    "measurement",       # one of our own metrics.json files
    "authors_own_claim", # a docstring, a prereg assertion, a module comment
    "none",
)
# Only these may support a `pinned` claim. `measurement` is excluded ON PURPOSE: our own
# experiment can establish what OUR system does, never what the BRAIN does.
BIOLOGY_EVIDENCE_KINDS = ("literature", "in_repo_audit")

# H2 is a POSITIVE requirement, not a blacklist. A pinned claim must carry a TRACEABLE
# BIOLOGICAL SOURCE: either an author-year citation, or the name of a lit-derived audit in
# this repo. A blacklist of repo paths was tried first and was wrong in both directions -- it
# voided a claim citing "preregs/... Marr 1971, Nakazawa et al. 2002" (which is a perfectly
# good citation that happens to name where it lives) and it would have passed any pinned
# claim that simply mentioned no path at all. A positive requirement cannot be evaded by
# deleting a filename.
_LIT_MARKER = r"(?<![-\d/])(1[89]|20)\d{2}(?![-\d/])"   # a bare year; ISO dates 2026-08-16 excluded
_AUDIT_MARKERS = ("organ_map", "lit_scan", "research_", "component_brain_fidelity_ledger")
# Named only to produce the SHARPER message on the incident's own shape.
_SELF_CITATION_TOKENS = (
    "hdlab/", "experiments/", "data/exp_", "verification/", "scratch/",
    "module docstring", "the cell's own",
)


def _has_biological_source(ev: str) -> bool:
    import re
    low = ev.lower()
    if "et al" in low:
        return True
    if any(m in low for m in _AUDIT_MARKERS):
        return True
    return bool(re.search(_LIT_MARKER, ev))


class HonestyGateVoid(Exception):
    """The score is VOID. Not low -- absent. Raised, never returned as a number."""


def _s(x) -> str:
    return (x or "").strip() if isinstance(x, str) else ""


def check_honesty_gate(claims: list[dict]) -> dict:
    """PASS/FAIL. Returns {'passed': bool, 'violations': [...]}. Never a score."""
    violations = []
    for c in claims:
        dim = _s(c.get("dimension")) or "?"
        basis = _s(c.get("basis"))
        kind = _s(c.get("evidence_kind"))
        ev = _s(c.get("evidence"))

        # H1 -- a basis must be declared and must be one of the four.
        if basis not in VALID_BASIS:
            violations.append({
                "clause": "H1", "dimension": dim, "basis": basis,
                "reason": f"basis must be one of {list(VALID_BASIS)}; got {basis!r}. An "
                          f"undeclared basis is how an invention becomes biology by default."})
            continue

        # H3 -- mutually exclusive labels (guards a claim dict carrying both).
        if basis == "pinned" and bool(c.get("is_invention")):
            violations.append({
                "clause": "H3", "dimension": dim,
                "reason": "claim is marked BOTH pinned and invention"})

        # H2 -- a pinned claim needs biology evidence, and may not cite ourselves.
        if basis == "pinned":
            if kind not in BIOLOGY_EVIDENCE_KINDS:
                violations.append({
                    "clause": "H2", "dimension": dim, "evidence_kind": kind,
                    "reason": f"a PINNED claim must cite {list(BIOLOGY_EVIDENCE_KINDS)}; got "
                              f"{kind!r}. Our own measurement establishes what OUR system "
                              f"does, never what the BRAIN does."})
            if not ev:
                violations.append({
                    "clause": "H2", "dimension": dim,
                    "reason": "PINNED claim with an EMPTY evidence string"})
            elif not _has_biological_source(ev):
                low = ev.lower()
                hit = next((t for t in _SELF_CITATION_TOKENS if t in low), None)
                violations.append({
                    "clause": "H2", "dimension": dim, "evidence": ev[:180],
                    "matched_self_citation_token": hit,
                    "reason": (
                        "PINNED claim with NO TRACEABLE BIOLOGICAL SOURCE -- no author-year "
                        "citation and no lit-derived audit named"
                        + (f"; it cites OUR OWN artifact ({hit}) instead, which is "
                           "SELF-CITATION AS BIOLOGY. The incident: "
                           "hdlab/iterative_attractor.py documents alpha=0.5 as "
                           "'brain-canonical' while ORGAN_MAP D2 records that the update rule "
                           "is not stated in the biology -- an invention wearing a pinned "
                           "label, and it shipped." if hit else
                           ". Point at the literature, or declare the claim as invention -- "
                           "invention costs nothing."))})

    return {"passed": not violations, "violations": violations,
            "meaning": ("PASS/FAIL, not a scored dimension. A FAIL emits NO SCORE AT ALL -- "
                        "presenting invention as established biology voids the whole thing. "
                        "Invention itself is fully authorised and costs zero points.")}


def _resolve_claim(c: dict) -> dict:
    """Apply the no-default-middle and earned-N/A rules to ONE claim. Records coercions."""
    dim = _s(c.get("dimension"))
    basis = _s(c.get("basis"))
    ev = _s(c.get("evidence"))
    kind = _s(c.get("evidence_kind"))
    raw = c.get("verdict")
    coercions = []

    is_na = (isinstance(raw, str) and raw.upper() in ("NA", "N/A", "UNSCORABLE"))

    if is_na:
        # N/A must be EARNED: the brain fact must be DOCUMENTED as unpinned, with a source.
        if basis != "unpinned" or kind not in BIOLOGY_EVIDENCE_KINDS or not ev:
            coercions.append(
                "N/A CLAIMED BUT NOT EARNED -> coerced to 0. Marking a dimension unscorable "
                "requires basis='unpinned' AND a literature / in-repo-audit citation saying "
                "the brain fact is unpinned. Without that, 'unpinned' is indistinguishable "
                "from 'we did not look'.")
            return {"dimension": dim, "verdict": 0, "applicable": True,
                    "basis": basis, "evidence": ev, "evidence_kind": kind,
                    "blindness": _s(c.get("blindness")) or "unstated",
                    "detail": c.get("detail"), "coercions": coercions}
        return {"dimension": dim, "verdict": None, "applicable": False,
                "basis": basis, "evidence": ev, "evidence_kind": kind,
                "blindness": _s(c.get("blindness")) or "unstated",
                "detail": c.get("detail"), "coercions": coercions}

    try:
        v = int(raw)
    except (TypeError, ValueError):
        coercions.append(f"verdict {raw!r} is not 0/1/2/NA -> coerced to 0")
        v = 0
    if v not in (0, 1, 2):
        coercions.append(f"verdict {v} out of range -> coerced to 0")
        v = 0

    # NO DEFAULT MIDDLE VALUE: a positive score with no citable basis is not a score.
    if v > 0 and (not ev or kind == "none"):
        coercions.append(
            f"verdict {v} with no citable evidence -> coerced to 0. A dimension with no "
            f"citable basis scores 0, NEVER a default middle value.")
        v = 0

    return {"dimension": dim, "verdict": v, "applicable": True,
            "basis": basis, "evidence": ev, "evidence_kind": kind,
            "blindness": _s(c.get("blindness")) or "unstated",
            "detail": c.get("detail"), "coercions": coercions}


def score(component: str, claims: list[dict], *, mode: str = "post_hoc",
          count_d4: bool = False) -> dict:
    """Score one component. Raises HonestyGateVoid if the honesty gate fails.

    mode='design_time' drops D6 (no measured degradation curve exists before the run).
    """
    if mode not in ("design_time", "post_hoc"):
        raise ValueError("mode must be 'design_time' or 'post_hoc'")

    gate = check_honesty_gate(claims)
    if not gate["passed"]:
        raise HonestyGateVoid(json.dumps(
            {"component": component, "score": None, "honesty_gate": gate,
             "statement": "SCORE VOID -- no number is emitted. This is not a low score."},
            indent=2))

    counted = set(DESIGN_TIME_DIMENSIONS) if mode == "design_time" else set(SCORED_BY_DEFAULT)
    if count_d4:
        counted.add("D4")

    resolved = [_resolve_claim(c) for c in claims]
    by_dim = {r["dimension"]: r for r in resolved}

    missing = [d for d in counted if d not in by_dim]
    for d in missing:
        # A dimension nobody wrote a claim for is a 0, not an omission. Silence is not N/A.
        by_dim[d] = {"dimension": d, "verdict": 0, "applicable": True, "basis": "",
                     "evidence": "", "evidence_kind": "none", "blindness": "unstated",
                     "detail": "NO CLAIM SUBMITTED",
                     "coercions": ["no claim submitted for this dimension -> 0, never N/A"]}

    scorable = [by_dim[d] for d in sorted(counted) if by_dim[d]["applicable"]]
    not_applicable = [by_dim[d] for d in sorted(counted) if not by_dim[d]["applicable"]]

    points = sum(r["verdict"] for r in scorable)
    max_points = 2 * len(scorable)
    pct = (points / max_points) if max_points else None

    # The binding-constraint flag. HYPOTHESIS GENERATED BY THE 2026-08-16 RETRODICTION,
    # NOT A VALIDATED RULE -- see --retrodict output and notes/PLAN.md sec 5.
    d3 = by_dim.get("D3"); d5 = by_dim.get("D5")
    rp_zero = bool((d3 and d3["applicable"] and d3["verdict"] == 0)
                   or (d5 and d5["applicable"] and d5["verdict"] == 0))

    blindness = sorted({r["blindness"] for r in scorable})
    coercions = [{"dimension": r["dimension"], "coercions": r["coercions"]}
                 for r in resolved + list(by_dim.values()) if r["coercions"]]
    # de-dup (resolved and by_dim overlap)
    seen, uniq = set(), []
    for c in coercions:
        k = (c["dimension"], tuple(c["coercions"]))
        if k not in seen:
            seen.add(k); uniq.append(c)

    return {
        "component": component,
        "mode": mode,
        "honesty_gate": "PASS",
        "points": points,
        "max_points": max_points,
        "pct": pct,
        "n_scorable": len(scorable),
        "n_not_applicable": len(not_applicable),
        "COVERAGE_WARNING": (
            "This number is a PERCENTAGE OF APPLICABLE POINTS. It is meaningless without "
            f"n_scorable ({len(scorable)} of {len(counted)} counted dimensions). "
            "Never quote pct alone."),
        "dimensions": {d: {"verdict": by_dim[d]["verdict"],
                           "applicable": by_dim[d]["applicable"],
                           "basis": by_dim[d]["basis"],
                           "evidence_kind": by_dim[d]["evidence_kind"],
                           "evidence": by_dim[d]["evidence"],
                           "blindness": by_dim[d]["blindness"],
                           "detail": by_dim[d].get("detail")}
                       for d in sorted((set(DIMENSIONS) & (counted | {"D4"})) & set(by_dim))},
        "d4_reported_not_scored": (not count_d4) and ("D4" in by_dim),
        "regime_or_pairing_zero": rp_zero,
        "regime_or_pairing_zero_status": (
            "HYPOTHESIS, NOT A VALIDATED RULE. Generated post-hoc from six banked results on "
            "2026-08-16; it fired on 4 of 5 failures and stayed silent on the one hold, and "
            "missed the CA3 completer. Its pre-registered test: any future component with a "
            "0 on D3 or D5 fails its floor. Do not treat it as established."),
        "coercions": uniq,
        "blindness_of_scored_dimensions": blindness,
        "WHAT_THIS_CANNOT_DO": (
            "Measures fidelity, NOT capability. A high-fidelity component can lose and a "
            "low-fidelity one can win -- both are in our own retrodiction. It can never "
            "clear, soften or substitute for the floor-and-CI bar (PLAN R1)."),
    }


# ---------------------------------------------------------------------------
# THE RETRODICTION FIXTURE -- six banked results, every claim carrying its citation.
#
# HOW BLIND THIS IS, STATED HONESTLY AND UP FRONT. I scored these knowing every outcome;
# genuine blindness was not available. What was available: for (a), (b) and (c) the
# pre-registration documents were written and dated BEFORE the runs, so every D1/D2/D3/D5
# claim below is sourced to a PRE-RUN document and is tagged blindness="pre_run". D6 is
# sourced to the measured degradation curve and is tagged "post_hoc" without exception. The
# `design_time` mode exists so the blind and non-blind readings can be compared directly,
# and they are, in the --retrodict output.
# ---------------------------------------------------------------------------

RETRODICTION = [
    {
        "component": "a_conjunctive_perirhinal_coding",
        "outcome": "FAILED -- CI-separated below flat (-0.0165 [-0.0235,-0.0095]); all three "
                   "arms failed their own known-answer gate (0.6823/0.6990/0.6622 vs 0.70)",
        "outcome_source": "data/exp_perirhinal_conjunctive_readout_c3_v1/metrics.json",
        "claims": [
            {"dimension": "D1", "verdict": 1, "basis": "contested", "evidence_kind": "in_repo_audit",
             "evidence": "notes/PLAN.md sec 5 row 'avoiding interference': perirhinal cortex is "
                         "named anatomically, and the feature-ambiguity ATTRIBUTION is recorded "
                         "as CONTESTED with real failed replications.",
             "blindness": "pre_run",
             "detail": "anatomical system named; documented computation is contested, so 1 not 2"},
            {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "authors_own_claim",
             "evidence": "preregs/2026-08-15_exp_perirhinal_conjunctive_readout_c3_v1.md sec 2 "
                         "and the module docstring: SHAPE conjunctions-not-features matches; "
                         "POSITION applied as a metric swap on the live cortical bag rather than "
                         "as an MTL stage; METRIC (elementwise product over unordered content-word "
                         "pairs) is declared OUR INVENTION.",
             "blindness": "pre_run",
             "detail": "shape MATCH, position MISMATCH, metric UNPINNED-and-dropped -> 1 of 2"},
            {"dimension": "D3", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "MTL sparse coding is PINNED at ~0.2% of neurons per percept, "
                          "each firing to ~50-150 concepts (Waydo, Kraskov, Quian "
                          "Quiroga, Fried & Koch 2006 J Neurosci 26:10232, via "
                          "notes/ORGAN_MAP.md D1). CA3 completes from a DEGRADED cue "
                          "(Nakazawa et al. 2002 Science). PLAN R14 and PLAN sec 5 anchor "
                          "SPARSE-not-dense.",
             "blindness": "pre_run",
             "detail": "sparse MISMATCH (the scored arms are dense; the k-WTA arm was a "
                       "two-variable diagnostic); exact-key-vs-partial-cue MISMATCH (validated "
                       "in an isolation cell where the query IS the stored key, deployed on "
                       "never-seen contexts); graded MATCH. 1 of 3 -> 0"},
            {"dimension": "D4", "verdict": 1, "basis": "invention", "evidence_kind": "measurement",
             "evidence": ".claude/scan-out/wall2-wire-perirhinal.json: a NEW module "
                         "hdlab/perirhinal_conjunctive.py, reaching the reader only through the "
                         "pre-existing default-off port and reusing the live codebook.",
             "blindness": "pre_run", "detail": "new organ, existing port and codebook"},
            {"dimension": "D5", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Separation and completion are a MATCHED PAIR: DG decorrelates "
                          "by sparse expansion (Waydo et al. 2006 J Neurosci 26:10232) "
                          "and CA3 output stays closer to the STORED pattern than its "
                          "degraded DG input (Neunuebel & Knierim 2014 Neuron "
                          "81:416-427), via notes/ORGAN_MAP.md D1/D2 and PLAN R13. No "
                          "completer existed when this ran.",
             "blindness": "pre_run", "detail": "partner organ ABSENT at run time"},
            {"dimension": "D6", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Biological systems complete from degraded cues (Nakazawa et al. 2002 "
                         "via notes/research_schema_fit_derivability_signal_upgrade_2026-07-16.md). "
                         "Measured cliff: 20%-overlap cosine 0.2023 -> 0.0194, ~10x, while the "
                         "flat bag did not move.",
             "blindness": "post_hoc", "detail": "CLIFF, CI-separated below the flat reference"},
        ],
    },
    {
        "component": "b_hub_and_spoke_per_spoke_role_addressing",
        "outcome": "HELD under partial cue (ADDRESSED vs FLAT at 20% overlap: -0.0007, "
                   "CI [-0.0160,+0.0147], a tie) and DID NOT BEAT the flat bag",
        "outcome_source": "data/exp_hub_spoke_partial_cue_curve_v1/metrics.json",
        "claims": [
            {"dimension": "D1", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Anterior temporal hub + modality spokes, with the DOUBLE "
                          "DISSOCIATION as the documented computation a single blended "
                          "store cannot predict (Rogers, Lambon Ralph, Garrard, Bozeat, "
                          "McClelland, Hodges & Patterson 2004 Psychol Rev 111:205-235, "
                          "via notes/ORGAN_MAP.md B2; PLAN sec 5 anchor 2).",
             "blindness": "pre_run", "detail": "named anatomically, computation documented"},
            {"dimension": "D2", "verdict": 2, "basis": "invention", "evidence_kind": "authors_own_claim",
             "evidence": "preregs/2026-08-16_exp_hub_spoke_partial_cue_curve_v1.md: SHAPE "
                         "separately-addressed per-modality stores MATCH; POSITION word-level "
                         "codec where the hub sits MATCH; METRIC unbind-by-role-key declared "
                         "OUR-INVENTION and ORGAN_MAP records the brain's binding operation as "
                         "contested three ways, so the metric axis is dropped.",
             "blindness": "pre_run", "detail": "shape MATCH, position MATCH, metric dropped -> 2 of 2"},
            {"dimension": "D3", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "The semantic hub is pinned DENSE AND GRADED -- first ~4 group "
                          "PCs define the shared space (Huth 2012 Neuron 76:1210), "
                          "~two-thirds of temporal-pole electrodes active per exemplar "
                          "(Tiesinga 2023), and sparse ~0.2% coding is the MTL regime, a "
                          "DIFFERENT system (Waydo et al. 2006) -- via notes/ORGAN_MAP.md "
                          "B4. Ours is dense and graded, so this MATCHES. PLAN R14: the "
                          "partial-cue regime is the real one, and this cell measured "
                          "across a cue-overlap curve rather than at an exact key.",
             "blindness": "pre_run", "detail": "dense MATCH (correct for a hub), partial-cue "
                                               "MATCH, graded MATCH -> 3 of 3"},
            {"dimension": "D4", "verdict": 2, "basis": "invention", "evidence_kind": "measurement",
             "evidence": ".claude/scan-out/wall1-hubspoke-full.json: reused hdlab/hub_spoke_word.py "
                         "and the parent cell's build_arm; the new cell adds NO hdlab module.",
             "blindness": "pre_run", "detail": "reuse, no parallel build"},
            {"dimension": "D5", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "The matched pair here is HUB + SPOKES, pinned by the double "
                          "dissociation (Rogers et al. 2004 Psychol Rev 111:205-235). "
                          "Both are present and both are reached: facet recovery 1.0000 "
                          "at full cue, and gate G2 extension-without-invalidation holds "
                          "on all 6 configs.",
             "blindness": "pre_run", "detail": "both halves present AND reached"},
            {"dimension": "D6", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Graceful degradation is the biological signature -- CA3 output "
                          "stays close to the stored pattern as its input degrades "
                          "(Neunuebel & Knierim 2014 Neuron 81:416-427). Measured: at 20% "
                          "content overlap ADDRESSED 0.2147 against FLAT 0.2162, paired "
                          "delta -0.0007 CI [-0.0160,+0.0147] straddling zero, in the "
                          "SAME run where the instrument detects the conjunctive collapse "
                          "CI-separated.",
             "blindness": "post_hoc", "detail": "tracks the reference; positive control fired"},
        ],
    },
    {
        "component": "c_ca3_completion_as_built",
        "outcome": "REFUTED at full scale, 0/5 gates. C_ADDRESSED_CA3 0.0013 vs B_ADDRESSED "
                   "0.0355 at 20% overlap; G2b settling delta +0.0010 CI covers zero",
        "outcome_source": "data/exp_ca3_completion_partial_cue_v1/metrics.json "
                          "(PAIRING_HYPOTHESIS_REFUTED, run_mode=full)",
        "claims": [
            {"dimension": "D1", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "preregs/2026-08-16_exp_ca3_completion_partial_cue_v1.md sec 3a: "
                         "hippocampal CA3, dense recurrent collaterals forming an "
                         "auto-associator, citing Marr 1971, Treves & Rolls, and Nakazawa et al. "
                         "2002 (CA3-NMDAR knockouts fail SPECIFICALLY on completion from "
                         "degraded cues).",
             "blindness": "pre_run", "detail": "named anatomically, computation documented"},
            {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "authors_own_claim",
             "evidence": "Same prereg sec 3a(c): SHAPE recurrent settling to a stored pattern "
                         "MATCH; POSITION routing completion THROUGH THE ADDRESS, per spoke, "
                         "against that spoke's codebook is declared OUR-INVENTION (CA3 completes "
                         "one hippocampal pattern, not per-modality fragments); METRIC the "
                         "softmax update rule is recorded by ORGAN_MAP D2 as OUR import, so the "
                         "metric axis is dropped.",
             "blindness": "pre_run", "detail": "shape MATCH, position INVENTION, metric dropped -> 1 of 2"},
            {"dimension": "D3", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Partial cue swept explicitly (Nakazawa et al. 2002 Science: "
                          "CA3-NMDAR knockouts fail SPECIFICALLY on completion from "
                          "degraded cues) MATCH; graded settle MATCH; MAX_STEPS=4 "
                          "brain-motivated cap MATCH; SPARSE MISMATCH -- CA3 operates on "
                          "a sparse code (~0.2%, Waydo et al. 2006 J Neurosci 26:10232) "
                          "and our store is dense per-word codes, with prereg sec 5.2c "
                          "recording that running dentate-gyrus separation in front was "
                          "the one brain-motivated variant DELIBERATELY NOT BUILT.",
             "blindness": "pre_run", "detail": "3 of 4 axes -> 1"},
            {"dimension": "D4", "verdict": 2, "basis": "invention", "evidence_kind": "measurement",
             "evidence": "Prereg sec 4 and gate IV6: hdlab/ca3_completer.py DELEGATES to "
                         "hdlab/iterative_attractor.py and IV6 asserts bit-identity. No parallel "
                         "attractor was built.",
             "blindness": "pre_run",
             "detail": "REUSE -- and this is the case that argues D4 out of the score: the "
                       "reused organ's update rule is one ORGAN_MAP names as OUR import, so "
                       "reuse here scores 2 while importing an unfaithful operation"},
            {"dimension": "D5", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "CA3's matched partner is the dentate gyrus: DG decorrelates "
                          "before CA3 stores, and CA3 output stays closer to the stored "
                          "pattern than its degraded DG input (Neunuebel & Knierim 2014 "
                          "Neuron 81:416-427; Treves & Rolls 1992/1994), via "
                          "notes/ORGAN_MAP.md D1/D2. dg_pattern_separation EXISTS and "
                          "ORGAN_MAP rates its fidelity SAME, but it has ZERO IMPORTERS "
                          "and prereg sec 5.2c states it was not run in front of the "
                          "completer.",
             "blindness": "pre_run", "detail": "partner PRESENT, NOT REACHED -> 1"},
            {"dimension": "D6", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Nakazawa et al. 2002 Science and Neunuebel & Knierim 2014: "
                          "intact CA3 completes gracefully from a degraded cue. Measured "
                          "cliff: SLOTTED_CA3 0.3571 at 50% overlap against SLOTTED "
                          "0.9974, and C 0.0013 against B 0.0355 at 20%.",
             "blindness": "post_hoc", "detail": "CLIFF, CI-separated below the un-completed arm"},
        ],
    },
    {
        "component": "d_the_flat_bag_incumbent",
        "outcome": "INCUMBENT, BEATEN BY A SPELLING FLOOR: open-vocab hit@1 0.0480 "
                   "[0.0413,0.0548] vs spelling-alone 0.0870 [0.0783,0.0960], CI-separated",
        "outcome_source": "data/exp_orthographic_floor_vet_v1/metrics.json (58a125c88)",
        "claims": [
            {"dimension": "D1", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "PLAN sec 5 row 'combining one encounter' names CORTICAL "
                          "POOLING with a graded rate code, i.e. canonical divisive "
                          "normalisation (Carandini & Heeger 2012 Nat Rev Neurosci "
                          "13:51-62). That is cortex, so not a bare cognitive label -- "
                          "but no specific cortical field is named, and the STORE half "
                          "has no structure claim on record at all (PLAN sec 2 item 5: "
                          "the shipped store applies NO KEY AT ALL).",
             "blindness": "pre_run", "detail": "a system gestured at, mapping loose -> 1"},
            {"dimension": "D2", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "notes/PLAN.md sec 5 same row: divisive normalisation with a "
                         "POOL-SHARED denominator is PINNED (Carandini & Heeger 2012). SHAPE "
                         "MISMATCH -- brain graded rate code, ours sign() of a sum, i.e. binary. "
                         "POSITION MATCH -- pooling sits where pooling should. METRIC MISMATCH "
                         "-- ours is a per-component sign, not a pool-shared denominator.",
             "blindness": "pre_run", "detail": "1 of 3 -> 0"},
            {"dimension": "D3", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Hub regime dense MATCH (first ~4 group PCs define the shared "
                          "space, Huth 2012 Neuron 76:1210; explicitly NOT sparse, via "
                          "ORGAN_MAP B4); partial-cue MATCH -- it is queried with "
                          "never-seen contexts and handles them; graded-vs-binary "
                          "MISMATCH -- the brain is graded (Carandini & Heeger 2012 Nat "
                          "Rev Neurosci 13:51-62) and the terminal sign() is binary.",
             "blindness": "pre_run", "detail": "2 of 3 -> 1"},
            {"dimension": "D4", "verdict": 2, "basis": "invention", "evidence_kind": "measurement",
             "evidence": "It IS the incumbent live path (hdlab/grounding_acquisition_loop.py); "
                         "nothing was built in parallel to it.",
             "blindness": "pre_run", "detail": "incumbent"},
            {"dimension": "D5", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "The store's matched partner is the hippocampal INDEX -- a sparse "
                         "pointer into distributed neocortical activity (Teyler & Rudy 2007; "
                         "one-shot Hebbian write on the sparse code, Marr 1971), via "
                         "notes/ORGAN_MAP.md D3. PLAN sec 2 item 5, verified by runtime "
                         "reconstruction: what accumulates is acc += symbol_vector(w). This is "
                         "NOT a degraded address, it is an ABSENT one.",
             "blindness": "pre_run", "detail": "partner ABSENT -> 0"},
            {"dimension": "D6", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Graceful degradation under a degraded cue is the biological "
                          "signature (Neunuebel & Knierim 2014 Neuron 81:416-427). "
                          "Measured: the flat bag is the reference every other operator "
                          "degrades against and it does not fall off a cliff -- 0.2162 at "
                          "20% content overlap, the best of the bundled operators.",
             "blindness": "post_hoc",
             "detail": "GRACEFUL. Note plainly: this is the LOWEST-fidelity arm on D2/D5 and it "
                       "degrades the most gracefully. Fidelity and robustness are not the same "
                       "axis and this row proves it inside our own evidence"},
        ],
    },
    {
        "component": "e_sha256_hash_word_encoder",
        "outcome": "THE STRUCTURE-AXIS NULL BY CONSTRUCTION: spelling-gold lift 0.99, SimLex "
                   "-0.0019 at d=256. Not near the null, it IS the null",
        "outcome_source": "notes/PLAN.md sec 2 item 2; "
                          "data/exp_encoding_quality_instrument_v2/metrics.json",
        "claims": [
            {"dimension": "D1", "verdict": 0, "basis": "unpinned", "evidence_kind": "none",
             "evidence": "",
             "blindness": "pre_run",
             "detail": "NO neural system is named anywhere. hdlab/grounding_acquisition_loop.py"
                       "::context_vector cites 'Kanerva random-indexing / BEAGLE-style' -- those "
                       "are COMPUTATIONAL MODELS, not neural systems. Scores 0, and note the "
                       "N/A escape is unavailable: it was claimed with no source, so the tool "
                       "coerces it to 0 rather than dropping the dimension"},
            {"dimension": "D2", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "The brain fact here IS pinned, which is what makes this a 0 and not an "
                         "N/A: notes/PLAN.md sec 5 row '1. word form' -- VWFA open-bigram, "
                         "position-tolerant letter-feature detectors (Dehaene et al. 2005; "
                         "Grainger & Whitney). Ours is a sha256-seeded random bipolar draw, "
                         "which matches none of SHAPE, POSITION or METRIC.",
             "blindness": "pre_run", "detail": "0 of 3, against a PINNED operation -> 0"},
            {"dimension": "D3", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "The brain's word-form regime is graded and position-TOLERANT "
                         "(Dehaene et al. 2005; Grainger & Whitney, via notes/ORGAN_MAP.md A1). "
                         "PLAN sec 2 item 2: a hash destroys relationships by design, so it is "
                         "not merely meaning-blind, it is SPELLING-blind too -- cos(water, "
                         "waters) and cos(water, river) are statistically identical. No regime "
                         "axis is matched, including the form regime it is supposed to occupy.",
             "blindness": "pre_run", "detail": "0 of 3 -> 0"},
            {"dimension": "D4", "verdict": 0, "basis": "invention", "evidence_kind": "in_repo_audit",
             "evidence": "notes/PLAN.md sec 2 item 2: six inlined lines inside "
                         "grounding_acquisition_loop.py::context_vector, while "
                         "hdlab/char_trigram_encoder.py, hdlab/vwfa.py and "
                         "hdlab/char_positional_encoder.py are all built and all off the live "
                         "path. THERE IS NO REGISTRY ROW FOR IT AT ALL.",
             "blindness": "pre_run", "detail": "inlined parallel implementation, three owned "
                                               "organs bypassed"},
            {"dimension": "D5", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Word FORM and word MEANING are separate brain systems -- VWFA "
                          "produces a form code (Dehaene et al. 2005) and meaning lives "
                          "in a temporal hub (Rogers et al. 2004 Psychol Rev "
                          "111:205-235), via ORGAN_MAP A1/B2 and PLAN sec 5 anchor 1. No "
                          "partner organ is named by this component, and the meaning half "
                          "(learned encoder, grounding norms, hand lexicon) is measured "
                          "ABSENT from the live 40-module import closure.",
             "blindness": "pre_run", "detail": "no partner named -> 0"},
            {"dimension": "D6", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "Derivable a priori rather than measured, and flagged as such: a "
                         "cryptographic hash changes its entire output when one input letter "
                         "changes, so degradation is maximally discontinuous. Biological form "
                         "codes are position-tolerant and degrade gracefully (Dehaene et al. "
                         "2005 via PLAN sec 5).",
             "blindness": "pre_run",
             "detail": "MAXIMAL CLIFF BY CONSTRUCTION. This is the one D6 that is NOT post-hoc"},
        ],
    },
    {
        "component": "f_cue_clamp_at_its_measured_regime",
        "outcome": "INERT AT THE LIVE OPERATING POINT: alpha default 0.0, live read-out "
                   "BIT-IDENTICAL with alpha forced to 0.5 on all 12 calls; worth 0.069 -> "
                   "0.470 only at eff_beta=4, and every landed caller sits at the inert end",
        "outcome_source": ".claude/scan-out/alpha-blast-radius.json (runtime A/B, 216-regime "
                          "sweep); data/exp_substrate_iterative_cleanup_cue_clamped_production_v1/"
                          "metrics.json (SANITY_FAIL, never adjudicated)",
        "claims": [
            {"dimension": "D1", "verdict": 2, "basis": "pinned", "evidence_kind": "literature",
             "evidence": "Hippocampal CA3 recurrent collaterals with entorhinal perforant-path "
                         "input persisting during settling: Treves and Rolls 1992/1994 (CA3 "
                         "auto-association); Hasselmo 2002 (cholinergic modulation of the "
                         "entorhinal-vs-recurrent balance); Neunuebel and Knierim 2014 Neuron "
                         "81:416-427.",
             "blindness": "pre_run", "detail": "named anatomically, computation documented"},
            {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "in_repo_audit",
             "evidence": "notes/ORGAN_MAP.md D2: 'the update rule is not stated in the biology -- "
                         "Hopfield sign-update and modern-Hopfield softmax are OUR imports', so "
                         "the METRIC axis is dropped. SHAPE MISMATCH AS DEPLOYED: the pinned "
                         "shape is recurrent settling WITH concurrent external drive, and the "
                         "live default alpha=0.0 WITHDRAWS that drive. POSITION MATCH: ORGAN_MAP "
                         "rates the familiarity/gap signal fidelity SAME.",
             "blindness": "pre_run",
             "detail": "scored AS DEPLOYED, not as documented -- shape MISMATCH, position MATCH, "
                       "metric dropped -> 1 of 2"},
            {"dimension": "D3", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": ".claude/scan-out/alpha-blast-radius.json step3: at the live "
                         "gap-detector temp=8.0 (eff_beta ~181) argmax disagreement is 0.005 and "
                         "the organ is 'operating as a one-shot lookup with extra steps'; "
                         "ORGAN_MAP D2 records every completion implementation terminating in "
                         "sign(); the store is dense where CA3 is sparse. Only the partial-cue "
                         "axis matches.",
             "blindness": "post_hoc",
             "detail": "1 of 4 -> 0. Tagged post_hoc: the effective-temperature regime was "
                       "established by the 216-regime sweep, not known in advance"},
            {"dimension": "D4", "verdict": 2, "basis": "invention", "evidence_kind": "measurement",
             "evidence": ".claude/scan-out/alpha-blast-radius.json: the clamp is a parameter on "
                         "the OWNED hdlab/iterative_attractor.py; no second attractor exists.",
             "blindness": "pre_run", "detail": "reuse"},
            {"dimension": "D5", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
             "evidence": "CA3's matched partner is the dentate gyrus. "
                         "hdlab/dg_pattern_separation.py is present, is rated fidelity SAME by "
                         "ORGAN_MAP, and has ZERO IMPORTERS.",
             "blindness": "pre_run", "detail": "partner PRESENT, NOT REACHED -> 1"},
            {"dimension": "D6", "verdict": "NA", "basis": "unpinned", "evidence_kind": "in_repo_audit",
             "evidence": "No degradation curve exists for the clamp AS DEPLOYED. "
                         ".claude/scan-out/alpha-blast-radius.json states plainly that the clamp "
                         "is UNADJUDICATED: its only supporting gate clears its own band 46.5% "
                         "of the time by construction, and the production follow-up aborted on a "
                         "sanity rail without ever scoring it.",
             "blindness": "post_hoc",
             "detail": "genuinely UNMEASURED. Dropped from numerator AND denominator rather than "
                       "scored 0, because 'we never measured it' is not 'it degrades badly'"},
        ],
    },
]


# ---------------------------------------------------------------------------
# THE CURRENT COMPONENT TABLE (notes/PLAN.md sec 3), scored.
#
# TWO OF THE SIX ARE NOT SCORED, AND THAT IS THE FINDING, NOT AN OMISSION. The absence claim
# is made by ENUMERATION, not by search (MEMORY.md: an absence claim requires an enumeration).
# notes/PLAN.md sec 5, the brain-fidelity ledger, has exactly TEN rows and here they all are:
#   word form | word meaning | combining one encounter | combining many encounters |
#   storage/addressing | avoiding interference | retrieval | selection |
#   settling/pattern completion | foraging
# Component #3 (reading / extraction) and component #6 (foundation, end to end) appear in the
# COMPONENT table and in NO row of the brain-fidelity ledger. No neural system is named for
# either anywhere in that document. They are therefore NOT SCORED rather than scored 0 --
# scoring them would require me to name a structure nobody has named, which is the fabrication
# the honesty gate exists to prevent. Naming them is a task for a person with the biology in
# hand, and it is the highest-value gap this exercise found in the plan.
# ---------------------------------------------------------------------------

COMPONENT_TABLE = [
    {"component": "1_word_and_concept_encoding",
     "plan_status": "identity fine; the live word code IS the structure-axis null",
     "same_as": "e_sha256_hash_word_encoder -- the live component IS that encoder"},
    {"component": "2_storage",
     "plan_status": "unmeasured in isolation; no key is applied at write time",
     "same_as": "d_the_flat_bag_incumbent"},
    {"component": "3_reading_extraction",
     "plan_status": "~0.22-0.25 precision against independent gold",
     "NOT_SCORED": "NO ROW in the notes/PLAN.md sec 5 brain-fidelity ledger. All ten rows "
                   "enumerated above; none is extraction. No neural system has been named for "
                   "this component, so there is nothing to score against. Scoring it would "
                   "mean inventing an anatomy."},
    {"component": "4_retrieval", "plan_status": "FINE -- top-50 55.65% vs spelling 54.55%",
     "claims": [
         {"dimension": "D1", "verdict": 1, "basis": "contested", "evidence_kind": "in_repo_audit",
          "evidence": "notes/PLAN.md sec 5 row 4 names 'cue-driven cortical reinstatement' and "
                      "immediately concedes 'there is no cosine anywhere in the brain'; "
                      "notes/ORGAN_MAP.md carries no specific cortical field for it. Cortex is "
                      "gestured at; no system is pinned.",
          "blindness": "pre_run", "detail": "a system gestured at, mapping loose -> 1"},
         {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "in_repo_audit",
          "evidence": "notes/ORGAN_MAP.md: the honest brain analogue is a recurrent settling "
                      "trajectory. SHAPE MISMATCH -- ours is a single-shot cosine over a "
                      "stacked matrix. POSITION MATCH. METRIC UNPINNED and dropped (PLAN sec 5 "
                      "row 4 states the metric is unpinned).",
          "blindness": "pre_run", "detail": "1 of 2"},
         {"dimension": "D3", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
          "evidence": "Partial-cue MATCH (it is queried with real never-seen cues); graded "
                      "MATCH (cosine is graded); SPARSE MISMATCH -- ours is dense where the "
                      "medial-temporal index is ~0.2% sparse (Waydo et al. 2006 J Neurosci "
                      "26:10232, via notes/ORGAN_MAP.md D1/B4).",
          "blindness": "pre_run", "detail": "2 of 3 -> 1"},
         {"dimension": "D5", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
          "evidence": "Retrieval's matched partner is the completer that turns a reinstated "
                      "neighbourhood into a settled pattern (Treves & Rolls 1992/1994; "
                      "Neunuebel & Knierim 2014 Neuron 81:416-427, via notes/ORGAN_MAP.md D2). "
                      "It IS present and IS reached -- the live chain calls the attractor 4x "
                      "per sentence, measured at runtime in "
                      ".claude/scan-out/alpha-blast-radius.json.",
          "blindness": "pre_run",
          "detail": "present AND reached -> 2. Recorded and NOT double-counted here: the same "
                    "audit measures that completer to be INERT at the live temperature. That "
                    "is a REGIME fault and it is already charged on D3; charging it twice "
                    "would make one defect look like two"}]},
    {"component": "5_selection", "plan_status": "FAILS -- 8.63% vs spelling 15.95%, separated",
     "claims": [
         {"dimension": "D1", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
          "evidence": "notes/PLAN.md sec 5 row 5: basal-ganglia Go/NoGo disinhibition -- an "
                      "anatomical system with a documented computation (via "
                      "notes/ORGAN_MAP.md D4).",
          "blindness": "pre_run", "detail": "named anatomically, computation documented"},
         {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "in_repo_audit",
          "evidence": "SHAPE MISMATCH -- the brain's competition is graded and implemented BY "
                      "the normalisation pool; ours is a hard argmax. PLAN sec 5 row 5 argues "
                      "argmax is the deterministic limit of a softmax and so cannot change a "
                      "TWO-CHOICE score, which is correct on that metric and is not a shape "
                      "match. POSITION MATCH. METRIC UNPINNED -- notes/ORGAN_MAP.md lists D4 "
                      "selection under 'core operation UNPINNED' -- and dropped.",
          "blindness": "pre_run", "detail": "1 of 2"},
         {"dimension": "D3", "verdict": 1, "basis": "pinned", "evidence_kind": "in_repo_audit",
          "evidence": "Graded-vs-binary MISMATCH (hard argmax where the brain is graded, "
                      "Carandini & Heeger 2012 Nat Rev Neurosci 13:51-62); partial-cue MATCH. "
                      "Sparsity is not an applicable axis for a selection stage and is dropped "
                      "rather than counted as a match.",
          "blindness": "pre_run", "detail": "1 of 2 -> 1"},
         {"dimension": "D5", "verdict": 0, "basis": "pinned", "evidence_kind": "in_repo_audit",
          "evidence": "Selection's matched partner is the NORMALISATION POOL that implements "
                      "the competition -- divisive normalisation with a pool-shared denominator "
                      "(Carandini & Heeger 2012 Nat Rev Neurosci 13:51-62). notes/PLAN.md sec 5 "
                      "row 'combining one encounter': ours is a per-component sign, and "
                      "divisive normalisation measured NULL (+0.00175, CI includes zero). The "
                      "partner organ is ABSENT, so the argmax has no graded pool to be the "
                      "limit OF.",
          "blindness": "pre_run", "detail": "partner ABSENT -> 0"}]},
    {"component": "6_foundation_end_to_end",
     "plan_status": "~49% correct (precision 0.4867, CI 0.408-0.566)",
     "NOT_SCORED": "NO ROW in the notes/PLAN.md sec 5 brain-fidelity ledger, by the same "
                   "ten-row enumeration. It is also the wrong UNIT: PLAN sec 4 states the "
                   "end-to-end number is JOINT and cannot be attributed to a component, and a "
                   "fidelity score is a per-organ measure. An assembled system does not have "
                   "one brain structure."},
]


def run_component_table(count_d4: bool = False) -> dict:
    rows = []
    by_retro = {c["component"]: c for c in RETRODICTION}
    for comp in COMPONENT_TABLE:
        if "NOT_SCORED" in comp:
            rows.append({"component": comp["component"], "plan_status": comp["plan_status"],
                         "score": None, "NOT_SCORED": comp["NOT_SCORED"]})
            continue
        claims = comp.get("claims") or by_retro[comp["same_as"].split(" -- ")[0]]["claims"]
        blind = score(comp["component"], claims, mode="design_time", count_d4=count_d4)
        rows.append({"component": comp["component"], "plan_status": comp["plan_status"],
                     "scored_via": comp.get("same_as", "own claim set"),
                     "points": blind["points"], "max_points": blind["max_points"],
                     "pct": blind["pct"],
                     "regime_or_pairing_zero": blind["regime_or_pairing_zero"],
                     "dimensions": {d: blind["dimensions"][d]["verdict"]
                                    for d in sorted(blind["dimensions"])}})
    return {"rows": rows,
            "n_scored": sum(1 for r in rows if r.get("score", 0) is not None),
            "UNSCORED_IS_THE_FINDING": (
                "2 of the 6 components in notes/PLAN.md sec 3 have NO ROW in the same "
                "document's own brain-fidelity ledger (sec 5), established by enumerating all "
                "ten of its rows. Reading/extraction and the end-to-end foundation have no "
                "neural system named anywhere in it. They are reported UNSCORED rather than "
                "scored 0, because scoring them would require inventing an anatomy -- which is "
                "the move the honesty gate voids.")}


def run_retrodiction(count_d4: bool = False) -> dict:
    rows = []
    for case in RETRODICTION:
        blind = score(case["component"], case["claims"], mode="design_time", count_d4=count_d4)
        full = score(case["component"], case["claims"], mode="post_hoc", count_d4=count_d4)
        rows.append({
            "component": case["component"],
            "outcome": case["outcome"],
            "outcome_source": case["outcome_source"],
            "design_time_blind": {"points": blind["points"], "max": blind["max_points"],
                                  "pct": blind["pct"], "n_scorable": blind["n_scorable"]},
            "post_hoc_with_D6": {"points": full["points"], "max": full["max_points"],
                                 "pct": full["pct"], "n_scorable": full["n_scorable"]},
            "regime_or_pairing_zero": blind["regime_or_pairing_zero"],
            "dimensions_blind": {d: blind["dimensions"][d]["verdict"]
                                 for d in sorted(blind["dimensions"])},
        })
    held = [r for r in rows if r["outcome"].startswith("HELD")]
    failed = [r for r in rows if not r["outcome"].startswith("HELD")]
    return {
        "counted_d4": count_d4,
        "rows": sorted(rows, key=lambda r: -(r["design_time_blind"]["pct"] or 0)),
        "n_held": len(held), "n_failed_or_null": len(failed),
        "VALIDATION_VERDICT": (
            "UNVALIDATED AS A PREDICTOR. Six points with exactly ONE positive-class member "
            "cannot support a separation claim: any monotone score that happens to rank the "
            "single hold first does so with probability 1/6 (p ~ 0.17) under a null of random "
            "ranking. The score DID rank the one hold alone at the top and DID put the "
            "construction-null alone at the bottom, and it DID fail twice in ways worth "
            "naming: the refuted CA3 completer scores well above the incumbent flat bag that "
            "beats it, and the flat bag ties the conjunctive arm it beats. Report the weak "
            "ordering; do not report a validated instrument."),
        "WAS_ANYTHING_TUNED": (
            "No weight was tuned. The aggregate was computed as proposed, found weak, and "
            "reported weak. The D3/D5-zero observation was made AFTER seeing the six scores "
            "and is labelled a HYPOTHESIS with a pre-registered forward test, not a result. "
            "Stating the temptation because the instruction required it: fitting six free "
            "dimensions to six points would be curve-fitting and would prove nothing."),
    }


# ---------------------------------------------------------------------------


def _self_test() -> int:
    ok = True

    def check(cond, label):
        nonlocal ok
        if not cond:
            ok = False
            print(f"[selftest] FAIL: {label}")

    good = [
        {"dimension": "D1", "verdict": 2, "basis": "pinned", "evidence_kind": "literature",
         "evidence": "Marr 1971; Treves and Rolls 1994", "blindness": "pre_run"},
        {"dimension": "D2", "verdict": 1, "basis": "invention", "evidence_kind": "authors_own_claim",
         "evidence": "prereg sec 3", "blindness": "pre_run"},
        {"dimension": "D3", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
         "evidence": "ORGAN_MAP sec 4", "blindness": "pre_run"},
        {"dimension": "D5", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
         "evidence": "ORGAN_MAP sec 4", "blindness": "pre_run"},
        {"dimension": "D6", "verdict": 2, "basis": "pinned", "evidence_kind": "in_repo_audit",
         "evidence": "ORGAN_MAP sec 4", "blindness": "post_hoc"},
    ]
    r = score("clean", good)
    check(r["honesty_gate"] == "PASS", "a clean claim set passes the honesty gate")
    check(r["points"] == 9 and r["max_points"] == 10, f"clean set scores 9/10 (got {r['points']}/{r['max_points']})")
    check(r["n_scorable"] == 5, "all five default dimensions scorable")
    check(not r["coercions"], f"clean set triggers NO coercion (got {r['coercions']})")

    # H2 clause A: a pinned claim citing a MEASUREMENT is not biology evidence.
    bad = [dict(good[0], evidence_kind="measurement", evidence="data/exp_foo/metrics.json")] + good[1:]
    try:
        score("h2a", bad); check(False, "H2 must VOID a pinned claim citing a measurement")
    except HonestyGateVoid as e:
        check("H2" in str(e), "H2 void names the clause")

    # H2 clause B: THE INCIDENT -- a pinned claim citing our own module as biology.
    bad2 = [dict(good[0], evidence="hdlab/iterative_attractor.py docstring: brain-canonical = 0.5")] + good[1:]
    try:
        score("h2b", bad2); check(False, "H2 must VOID self-citation as biology (the alpha incident)")
    except HonestyGateVoid as e:
        check("self-citation" in str(e).lower(), "H2 void names self-citation")

    # H1: undeclared basis.
    bad3 = [dict(good[0], basis="")] + good[1:]
    try:
        score("h1", bad3); check(False, "H1 must VOID an undeclared basis")
    except HonestyGateVoid as e:
        check("H1" in str(e), "H1 void names the clause")

    # H3: pinned AND invention.
    bad4 = [dict(good[0], is_invention=True)] + good[1:]
    try:
        score("h3", bad4); check(False, "H3 must VOID pinned+invention")
    except HonestyGateVoid as e:
        check("H3" in str(e), "H3 void names the clause")

    # INVENTION COSTS NOTHING: flip every basis to invention, keep the verdicts, same score.
    inv = [dict(c, basis="invention",
                evidence_kind=("authors_own_claim" if c["basis"] == "pinned" else c["evidence_kind"]))
           for c in good]
    ri = score("invention", inv)
    check(ri["honesty_gate"] == "PASS" and ri["points"] == r["points"],
          f"declared INVENTION scores identically to pinned ({ri['points']} vs {r['points']})")

    # NO DEFAULT MIDDLE VALUE: a positive verdict with no evidence is coerced to 0.
    # (basis=invention here on purpose: a PINNED claim with no evidence is harsher still --
    # it VOIDS under H2 rather than scoring 0, which the H2 cases above already prove.)
    noev = [dict(good[0], basis="invention", evidence="", evidence_kind="none")] + good[1:]
    rn = score("noev", noev)
    check(rn["dimensions"]["D1"]["verdict"] == 0, "a positive verdict with no evidence -> 0")
    check(any("NEVER a default middle value" in x for c in rn["coercions"] for x in c["coercions"]),
          "the coercion is RECORDED, not silent")

    # N/A MUST BE EARNED: unsourced N/A becomes 0, sourced N/A leaves the denominator.
    na_bad = [dict(good[0], verdict="NA", basis="unpinned", evidence_kind="none", evidence="")] + good[1:]
    rb = score("na_bad", na_bad)
    check(rb["dimensions"]["D1"]["verdict"] == 0 and rb["dimensions"]["D1"]["applicable"],
          "UNSOURCED N/A is coerced to 0 and stays in the denominator")
    check(rb["max_points"] == 10, f"unsourced N/A does not shrink the denominator (got {rb['max_points']})")

    na_good = [dict(good[0], verdict="NA", basis="unpinned", evidence_kind="in_repo_audit",
                    evidence="ORGAN_MAP honesty rule 1: brain math UNPINNED -> UNSCORABLE")] + good[1:]
    rg = score("na_good", na_good)
    check(not rg["dimensions"]["D1"]["applicable"], "SOURCED N/A is not applicable")
    check(rg["max_points"] == 8 and rg["n_scorable"] == 4,
          f"SOURCED N/A leaves numerator AND denominator (got {rg['points']}/{rg['max_points']})")
    check(rg["pct"] == 7 / 8, f"pct is over APPLICABLE points (got {rg['pct']})")

    # SILENCE IS NOT N/A: a dimension with no claim at all scores 0 and stays in the denominator.
    sil = [c for c in good if c["dimension"] != "D3"]
    rs = score("silent", sil)
    check(rs["dimensions"]["D3"]["verdict"] == 0 and rs["max_points"] == 10,
          "a dimension with NO CLAIM scores 0 and stays in the denominator")

    # design_time mode drops D6 entirely.
    rd = score("design", good, mode="design_time")
    check(rd["max_points"] == 8 and "D6" not in rd["dimensions"],
          f"design_time drops D6 (got max {rd['max_points']})")

    # D4 is reported, not scored, unless asked for.
    with_d4 = good + [{"dimension": "D4", "verdict": 0, "basis": "invention",
                       "evidence_kind": "measurement", "evidence": "registry", "blindness": "pre_run"}]
    r_no = score("d4off", with_d4)
    r_yes = score("d4on", with_d4, count_d4=True)
    check(r_no["max_points"] == 10 and r_yes["max_points"] == 12,
          "D4 enters the denominator only with --count-d4")
    check(r_no["points"] == r_yes["points"], "D4=0 does not change the numerator either way")

    # The binding-constraint flag fires on a D3 zero and on a D5 zero, and not otherwise.
    z3 = [dict(c, verdict=0) if c["dimension"] == "D3" else c for c in good]
    z5 = [dict(c, verdict=0) if c["dimension"] == "D5" else c for c in good]
    check(score("z3", z3)["regime_or_pairing_zero"], "flag fires on a D3 zero")
    check(score("z5", z5)["regime_or_pairing_zero"], "flag fires on a D5 zero")
    check(not r["regime_or_pairing_zero"], "flag stays silent when neither is zero")

    # The retrodiction fixture must itself pass the honesty gate and reproduce its numbers.
    rt = run_retrodiction()
    check(len(rt["rows"]) == 6, "retrodiction covers all six banked cases")
    by = {x["component"]: x for x in rt["rows"]}
    check(abs(by["b_hub_and_spoke_per_spoke_role_addressing"]["design_time_blind"]["pct"] - 1.0) < 1e-9,
          "hub-and-spoke (the one that HELD) scores 8/8 blind")
    check(by["e_sha256_hash_word_encoder"]["design_time_blind"]["points"] == 0,
          "the sha256 encoder (the construction null) scores 0 blind")
    check(by["c_ca3_completion_as_built"]["design_time_blind"]["points"] == 5,
          f"CA3 scores 5/8 blind (got {by['c_ca3_completion_as_built']['design_time_blind']['points']})")
    check(by["d_the_flat_bag_incumbent"]["design_time_blind"]["points"]
          == by["a_conjunctive_perirhinal_coding"]["design_time_blind"]["points"],
          "the flat bag TIES the conjunctive arm it beats -- the score's own counter-example")
    check(by["f_cue_clamp_at_its_measured_regime"]["post_hoc_with_D6"]["max"] == 8,
          "the clamp's SOURCED N/A on D6 shrinks its denominator to 8 even in post_hoc mode")

    print(f"[selftest] brain_fidelity_score: {'OK' if ok else 'FAIL'} "
          f"(honesty-gate void x4 incl. the alpha self-citation incident; invention-is-free; "
          f"no-default-middle; earned-N/A both ways; silence-is-not-N/A; design_time; D4 opt-in; "
          f"binding flag both ways; retrodiction fixture)")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--retrodict", action="store_true",
                    help="score the six banked 2026-08-15/16 results and report separation")
    ap.add_argument("--score-components", action="store_true",
                    help="score notes/PLAN.md sec 3's component table")
    ap.add_argument("--count-d4", action="store_true",
                    help="include D4 organ-reuse in the score (default: reported, not scored)")
    ap.add_argument("--score-json", type=Path,
                    help="JSON file: {'component': str, 'claims': [...]}")
    ap.add_argument("--mode", default="post_hoc", choices=("design_time", "post_hoc"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.self_test:
        return _self_test()

    if a.retrodict:
        out = run_retrodiction(count_d4=a.count_d4)
        if a.json:
            print(json.dumps(out, indent=2))
            return 0
        print("=" * 78)
        print("RETRODICTION -- six banked results, scored against their own pre-run documents")
        print("=" * 78)
        print(f"{'component':<44} {'blind':>10} {'post-hoc':>10}  D3/D5=0")
        for r in out["rows"]:
            b = r["design_time_blind"]; p = r["post_hoc_with_D6"]
            print(f"{r['component']:<44} {b['points']:>3}/{b['max']:<2}{b['pct']*100:>5.0f}% "
                  f"{p['points']:>3}/{p['max']:<2}{p['pct']*100:>4.0f}%   "
                  f"{'YES' if r['regime_or_pairing_zero'] else '-'}")
            print(f"    outcome: {r['outcome']}")
        print("-" * 78)
        print("VALIDATION: " + out["VALIDATION_VERDICT"])
        print("-" * 78)
        print("TUNING: " + out["WAS_ANYTHING_TUNED"])
        return 0

    if a.score_components:
        out = run_component_table(count_d4=a.count_d4)
        if a.json:
            print(json.dumps(out, indent=2))
            return 0
        print("=" * 78)
        print("COMPONENT TABLE (notes/PLAN.md sec 3), scored blind (design_time: D1 D2 D3 D5)")
        print("=" * 78)
        for r in out["rows"]:
            if r.get("NOT_SCORED"):
                print(f"{r['component']:<34} NOT SCORED")
                print(f"    {r['NOT_SCORED']}")
            else:
                print(f"{r['component']:<34} {r['points']:>2}/{r['max_points']:<2} "
                      f"{r['pct']*100:>4.0f}%   D3/D5=0: "
                      f"{'YES' if r['regime_or_pairing_zero'] else '-'}   {r['dimensions']}")
            print(f"    plan status: {r['plan_status']}")
        print("-" * 78)
        print(out["UNSCORED_IS_THE_FINDING"])
        return 0

    if a.score_json:
        payload = json.loads(a.score_json.read_text(encoding="utf-8"))
        try:
            out = score(payload["component"], payload["claims"], mode=a.mode,
                        count_d4=a.count_d4)
        except HonestyGateVoid as e:
            print(str(e))
            return 2
        print(json.dumps(out, indent=2))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
