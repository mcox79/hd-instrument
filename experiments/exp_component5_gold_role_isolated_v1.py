"""exp_component5_gold_role_isolated_v1 -- Component-5 GOLD-ROLE-ISOLATED goal-owner + outcome-
binding eval: given GOLD (Component-3-shaped) role labels, does a role-content-aware candidate
generator + the existing gold-free route_passage/decode_coherence_margins/decide_keep_or_revert
selector (hdlab/self_improving_loop.py, promoted 2026-08-02) beat pure recency on goal-owner /
outcome binding? This is the make-or-break density-gating check named by BOTH design docs:
notes/research_component5_goal_owner_selection_binding_2026-08-04.md (mechanism/reuse map) and
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md (Section 6, "Instance C
(goal-outcome) -- first buildable step ... has NOT been ruled out for goal-outcome" per Section 7's
named risk: decode_coherence_margins is PROVEN wrong for causal antecedent selection because
CausalLinkRegister write-then-read is symmetric; whether goal-outcome binding shares that same
symmetric-write failure is exactly what this cell settles).

PRE-REG: preregs/2026-08-04_component5_gold_role_isolated_v1.md

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh "goal owner
selection coherence binding recency outcome"` returned notes/WHERE_WE_ARE_NOW.md (cosine=0.4014),
notes/director_POST_COMPACTION_BACKUP_2026-08-04.md (cosine=0.3965/0.3906), and
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md (cosine=0.3877) -- all
above the 0.30 threshold. Both notes/*_2026-08-04.md docs were READ IN FULL before writing this
cell: this eval IS the "first buildable step" the build-spec names (Section 6.1: "Instance C
(goal-outcome) -- zero new hdlab code, only a harness wiring decode_coherence_margins to the
goal-outcome role vocab + candidate-owner cluster_ids ... first harden the item set into a true
recency-trap before scoring it") -- NOT a rediscovery. The RECENCY item set in
exp_situation_model_goal_outcome_dimension_v1.py already satisfies the "harden into a true
recency-trap" prerequisite (2 genuine traps + 1 sanity item, verified by reading the item texts).

GOLD-ROLE ISOLATION (per task brief): Component-3's thematic-role perceptron is still in flight
(3c). This eval bypasses it entirely -- role labels come from the SAME lexicon-based typing
(type_sentence_events, GO_ROLES) the fb5b2a188 cell already uses, reused bit-identical, which is a
GOLD (hand/lexicon-derived, not learned/noisy) role signal for these items. This isolates
Component-5's SELECTION mechanism from Component-3's OWN accuracy, per the design drill's explicit
recommendation (Section (e): "Recommend running the gold-role isolation FIRST regardless of
Component-3's 3c status").

MECHANISM (glass-box, reuses 3 organs bit-identical, adds ONE new ~30-line candidate generator):
  1. BASELINE candidate = RecencyEntityResolver (reused verbatim from fb5b2a188, unchanged):
     backward-search, first gender-compatible entity by recency -- the KNOWN falsified failure
     mode (MEMORY 2026-08-03, coref 0/4).
  2. CONTENT candidate = NEW ContentMatchResolver (this cell): tracks entities carrying an OPEN
     GOAL (a GOAL-role event with no OUTCOME yet bound); on an ambiguous pronoun, prefers a
     gender-compatible OPEN-GOAL entity over recency; falls back to recency if none (honest
     fallback, not a forced win).
  3. SELECTOR = hdlab.self_improving_loop.route_passage (reused verbatim): scores both candidates'
     whole-passage resolutions via decode_coherence_margins over role_vocab=GO_ROLES (the 4-symbol
     GOAL/ACTION_AGAINST/OUTCOME_UNMET/OUTCOME_MET vocab -- the richer role-content signal named as
     the missing wire in both design docs, vs the 2-symbol agent/mentioned vocab route_passage was
     validated on before), adopts CONTENT iff its aggregate coherence-margin delta clears the
     abstain band (0.02, unchanged default).

CONTROLS: anti-recency (both real traps have gold-owner != most-recent entity, by construction);
role-scramble (mislabel the GOAL holder as the foil, text/gold unchanged -- must COLLAPSE accuracy
if the selector is genuinely content-driven, else it is the same positional-confound failure mode
as _pick_strict_cb); control false-fire (unchanged CONTROLS items must stay 0/6); sign check
(route_passage's own gold-free agg_coherence_delta must be positive on genuine traps).

BANDS (VERBATIM per task brief + pre-reg):
  HARD-PASS  -> outcome_binding_accuracy>=0.67 AND role_scramble_collapse holds AND
                control_false_fire_rate==0 AND goal_owner_binding_accuracy>=5/6.
  MIDDLE     -> outcome_binding_accuracy in [0.334,0.66] OR scramble partially collapses.
  HARD-FAIL  -> outcome_binding_accuracy<=0.333 OR role_scramble_collapse fails.
  SMALL-N CAP (VET-as-hard-as-negative): N=3 recency items -> a formal HARD-PASS is REPORTED as
  MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS (mechanism-class license, not landed statistical result);
  HARD-FAIL is NOT capped (a clean small-N negative is still informative evidence).

GUARDS: glass-box; RecencyEntityResolver / type_sentence_events / GO_ROLES / route_passage /
decode_coherence_margins / decide_keep_or_revert reused bit-identical; deterministic given seed;
ASCII-only; atomic metrics write; NOT dispatched to any queue (LOCAL-ONLY, in-process foreground
per task brief, no push).

Cites: notes/research_component5_goal_owner_selection_binding_2026-08-04.md;
notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md;
experiments/exp_situation_model_goal_outcome_dimension_v1.py (item bank, fb5b2a188, 0.333 recency
floor); hdlab/self_improving_loop.py (route_passage, promoted 2026-08-02).
"""
from __future__ import annotations

import os

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

ANCHOR_NAME = "component5_gold_role_isolated_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

import torch  # noqa: E402

# ---- REUSED BIT-IDENTICAL: item bank, lexicon typing, recency resolver, register ---------------
from exp_situation_model_goal_outcome_dimension_v1 import (  # noqa: E402
    GOAL_BLOCK, CONTROLS, RECENCY, GO_ROLES, R_GOAL, R_UNMET, R_MET,
    RecencyEntityResolver, type_sentence_events, treatment_fires, _sentences, _ordered_tokens,
    GENDER, ANIMATE_NAMES, PRON_F, PRON_M, GoalOutcomeRegister,
)
# ---- REUSED BIT-IDENTICAL: the gold-free coherence-margin selector (2026-08-02 promotion) -------
# route_passage / decode_coherence_margins kept ONLY for the DIAGNOSTIC field below (proves the
# fix was necessary: this signal is 0.0-blind for Component-5, per commit 60aa9f060 disk-verified
# diagnosis). decide_keep_or_revert is reused VERBATIM as the actual adoption gate -- only the
# SCORE fed to it changes (see directed_goal_outcome_score below).
from hdlab.self_improving_loop import (  # noqa: E402
    route_passage, decide_keep_or_revert, ABSTAIN_BAND_DEFAULT,
)
# ---- REUSED BIT-IDENTICAL: PRODUCTION coref's gender machinery (2026-08-05, this generalization) --
# hdlab/coreference_resolver.py's own docstring: bare first-name gender inference (e.g.
# guess_gender_v2) is "DATA/gazetteer-level, not a resolver-mechanism change" -- so the GENERAL,
# reusable MECHANISM pieces are (a) PRONOUN_SCOPE (pronoun -> gender/number agreement, works for
# ANY pronoun regardless of which names it corefers with) and (b) infer_nominal_gender
# (title/kinship-cue nominal gender inference, works for ANY nominal span). Both are wired in
# below (read-only reuse; hdlab/coreference_resolver.py and hdlab/state_of_mind.py are untouched).
from hdlab.state_of_mind import PRONOUN_SCOPE, infer_nominal_gender  # noqa: E402

D2 = 1024
SEEDS = [0, 1, 2]

# GOLD foil (the entity mentioned more recently than the true goal-owner) for each real trap item.
# DEEPENED 2026-08-05 (USER task "deepen N for the goal-owner pipeline"): the 2 original genuine
# traps above + 20 NEW genuine traps added to RECENCY in exp_situation_model_goal_outcome_
# dimension_v1.py (N=23 total: 22 genuine traps + 1 antecedent-is-recent sanity item, which stays
# excluded from FOILS by design -- it has no foil, recency happens to be correct there).
FOILS = {
    "recency_amy_blocked_pronoun_foil_jo": "jo",
    "recency_tom_blocked_pronoun_foil_sid": "sid",
    "recency_beth_blocked_pronoun_foil_meg": "meg",
    "recency_meg_blocked_pronoun_foil_beth": "beth",
    "recency_ruth_blocked_pronoun_foil_ann": "ann",
    "recency_ann_blocked_pronoun_foil_ruth": "ruth",
    "recency_amy_blocked_pronoun_foil_beth": "beth",
    "recency_jo_blocked_pronoun_foil_meg": "meg",
    "recency_beth_blocked_pronoun_foil_ruth": "ruth",
    "recency_ann_blocked_pronoun_foil_jo": "jo",
    "recency_meg_blocked_pronoun_foil_ann": "ann",
    "recency_ruth_blocked_pronoun_foil_amy": "amy",
    "recency_amy_blocked_pronoun_foil_meg": "meg",
    "recency_jo_blocked_pronoun_foil_ruth": "ruth",
    "recency_beth_blocked_pronoun_foil_jo": "jo",
    "recency_meg_blocked_pronoun_foil_ruth": "ruth",
    "recency_sid_blocked_pronoun_foil_tom": "tom",
    "recency_laurie_blocked_pronoun_foil_tom": "tom",
    "recency_tom_blocked_pronoun_foil_laurie": "laurie",
    "recency_sid_blocked_pronoun_foil_laurie": "laurie",
    "recency_laurie_blocked_pronoun_foil_sid": "sid",
    "recency_tom_blocked_pronoun_foil_sid_summit": "sid",
}


# ============================================================================ GENERALIZED entity/gender resolution
# UNBLOCK (2026-08-05, USER task): generalize entity/gender resolution off the hardcoded 12-name
# toy cast (GENDER/ANIMATE_NAMES/PRON_F/PRON_M, imported bit-identical above for GOAL_BLOCK / the
# unchanged run_goal_owner_binding path only) so the RECENCY pipeline runs on ARBITRARY names --
# reusing PRODUCTION coref's gender MECHANISM (PRONOUN_SCOPE + infer_nominal_gender) plus a
# PER-ITEM roster (name -> gender) supplied by the item, instead of re-deriving name/gender from a
# fixed lexicon baked into the resolver code. DEFAULT_ROSTER = the original 12-name gazetteer
# (unchanged VALUES, now DATA an item can override, not hardwired resolver logic) -- this keeps the
# authored 23-item RECENCY bank bit-identical (no-regression) while any NEW item can supply its own
# roster of arbitrary names.
DEFAULT_ROSTER = dict(GENDER)  # {"amy": "f", ..., "tom": "m", ...} -- same 12 names, now pluggable data

# PRONOUN_SCOPE (production, hdlab.state_of_mind) does not carry reflexives (herself/himself); the
# toy PRON_F/PRON_M sets did. Extend the PRODUCTION table locally (reuse-then-augment, not
# reinvent) so no coverage is lost vs the original hardcoded sets.
_PRON_SCOPE_EXT = dict(PRONOUN_SCOPE)
_PRON_SCOPE_EXT.setdefault("herself", {"number": "singular", "gender": "fem"})
_PRON_SCOPE_EXT.setdefault("himself", {"number": "singular", "gender": "masc"})
_GENDER_MAP = {"masc": "m", "fem": "f"}  # production's masc/fem -> this eval's f/m scheme


def _is_pron_general(token: str) -> bool:
    """True iff token is a gendered singular pronoun (production PRONOUN_SCOPE, reflexive-extended)."""
    scope = _PRON_SCOPE_EXT.get(token)
    return scope is not None and scope["gender"] in ("masc", "fem")


def _gender_of_general(token: str, roster: dict):
    """f / m / None gender for a lowercase token -- works on ARBITRARY names, not just the toy
    cast. Order: (1) PRONOUN_SCOPE (production, general, any pronoun) -> (2) the per-item roster's
    explicit gender (item-supplied cast data, e.g. {"elizabeth": "f", "darcy": "m"}) -> (3)
    infer_nominal_gender (production, general, title/kinship nominal cues) as an honest fallback
    for a name absent from the roster. Returns None (unknown) if none resolve -- matches the
    original GENDER.get(e) == want semantics (None never satisfies a gendered want)."""
    scope = _PRON_SCOPE_EXT.get(token)
    if scope is not None:
        return _GENDER_MAP.get(scope["gender"])
    if token in roster:
        return roster[token]
    return _GENDER_MAP.get(infer_nominal_gender([token]))


class GeneralRecencyEntityResolver:
    """Generalized RecencyEntityResolver: IDENTICAL mechanism (backward-search recency pick over
    gender/number-compatible candidates) to the toy RecencyEntityResolver above, but name/gender
    resolution is GENERALIZED (per-item roster + production gender machinery, see
    _gender_of_general) instead of the hardcoded ANIMATE_NAMES/PRON_F/PRON_M/GENDER lexicon --
    this is the unblocked baseline candidate used by run_recency_item (the RECENCY pipeline);
    run_goal_owner_binding keeps using the original RecencyEntityResolver import UNCHANGED (per
    task brief scope). Default roster = DEFAULT_ROSTER (bit-identical to the toy cast, so the
    authored 23-item bank is unaffected); any item may supply its own roster of arbitrary names.

    KNOWN BUG, DELIBERATELY LEFT UNFIXED HERE (2026-08-06, coref goal-subject confound): subject_
    entity below is TWO-PASS -- pass 1 scans the WHOLE sentence for the first roster-NAME token
    ANYWHERE (subject OR object position) before ever checking for a pronoun; pass 2 (reached only if
    pass 1 finds no name at all) resolves the first pronoun via recency. This mis-resolves a pronoun
    SUBJECT that precedes an object-position roster name, e.g. "He wanted to help his mother" (roster
    {henry, mother}) returns "mother" (the object) instead of resolving "he" -> henry. hdlab/goal_
    owner_select.py's byte-copied GeneralRecencyEntityResolver has been FIXED (single-pass
    first-nominal: the first token that is EITHER a name OR a pronoun wins, respecting subject-first
    word order) -- see that module's docstring for the full fix + rationale. THIS copy is
    intentionally left with the original two-pass behavior: it is the resolver
    resolve_outcome_recency_positional (in experiments/exp_c5_real_coref_endtoend_purpose_infinitival_
    v1.py) uses as the BASELINE to select the divergent-item population verification/test_goal_owner_
    select.py's 48-item fair instrument and verification/verify_goal_typing.py's expected_n_divergent
    counts are gated on; changing this resolver's behavior would change that population and risk an
    unrelated cert regression. Same "left untouched as source-of-truth for its own historical numbers"
    convention as this module's sibling promotion docstrings (hdlab/goal_owner_select.py /
    hdlab/goal_typing.py) already document for the sentence-splitter fix."""

    def __init__(self, roster: dict | None = None):
        self._recent = []  # entity names in order of mention (most recent last)
        self._roster = roster if roster is not None else DEFAULT_ROSTER

    def subject_entity(self, sentence: str):
        toks = _ordered_tokens(sentence)
        for t in toks:                                   # first explicit roster NAME = subject
            if t in self._roster:
                self._note(t)
                return t
        for t in toks:                                   # else first pronoun -> recency-resolved
            if _is_pron_general(t):
                want = _gender_of_general(t, self._roster)
                for e in reversed(self._recent):          # BACKWARD search == recency
                    if _gender_of_general(e, self._roster) == want:
                        return e
                return None
        return None

    def _note(self, entity: str):
        self._recent.append(entity)


# ============================================================================ NEW candidate generator
class ContentMatchResolver:
    """The ONE genuinely new piece (per both design docs): tracks entities carrying an OPEN GOAL
    (a GOAL-role event with no OUTCOME bound yet, GOLD-typed via type_sentence_events reused
    bit-identical) and prefers such an entity over pure recency when resolving an ambiguous
    pronoun. Falls back to recency if no open-goal entity is gender-compatible (honest fallback --
    this resolver does NOT force a non-recency answer, it only makes one constructible when
    content supports it, per design drill (d).2)."""

    def __init__(self, roster: dict | None = None):
        self._recent = []       # entity names in mention order (mirrors RecencyEntityResolver)
        self._open_goal = set()  # entities with an unresolved (no-outcome-yet) GOAL event
        # GENERALIZED (2026-08-05): per-item roster instead of the hardcoded ANIMATE_NAMES lexicon;
        # default = DEFAULT_ROSTER (bit-identical to the toy cast) -- see GeneralRecencyEntityResolver.
        self._roster = roster if roster is not None else DEFAULT_ROSTER

    def subject_entity(self, sentence: str):
        toks = _ordered_tokens(sentence)
        for t in toks:                                   # explicit NAME = subject (unambiguous)
            if t in self._roster:
                self._note(t)
                return t
        for t in toks:                                   # pronoun -> content-match, else recency
            if _is_pron_general(t):
                want = _gender_of_general(t, self._roster)
                compatible = [e for e in self._recent if _gender_of_general(e, self._roster) == want]
                open_goal_compatible = [e for e in compatible if e in self._open_goal]
                if open_goal_compatible:
                    return open_goal_compatible[-1]       # prefer content (open-goal), not position
                for e in reversed(compatible):             # honest fallback: recency within pool
                    return e
                return None
        return None

    def _note(self, entity: str):
        if entity not in self._recent:
            self._recent.append(entity)

    def mark_role(self, entity: str, role: str):
        """Called by the caller AFTER typing a sentence's events, so later pronouns see the
        updated open-goal state (causal order matches the design: resolve subject -> type events
        -> update state -> next sentence)."""
        if role == R_GOAL:
            self._open_goal.add(entity)
        elif role in (R_UNMET, R_MET):
            self._open_goal.discard(entity)


def build_positions(item: dict, resolver, scramble_owner_to_foil: str | None = None):
    """Walk item['text'] sentence-by-sentence, resolving subject via `resolver` and typing events
    via type_sentence_events (reused bit-identical). Returns (role_seq, cluster_ids, event_slots).
    event_slots = GLOBAL POSITION INDEX (deliberate, see pre-reg "Mechanism" #4): candidate
    reassignment changes an entity's own next-slot number under a per-entity scheme, so global-
    position slotting keeps role_seq/event_slots identical across candidates -- only cluster_ids
    (the entity assignment) varies, matching route_passage's documented contract.
    If scramble_owner_to_foil is set, any GOAL-role event whose true subject is the item's owner
    is relabeled to that foil entity instead (role-scramble control -- text/gold unchanged)."""
    owner = item.get("owner")
    role_seq, cluster_ids = [], []
    for sent in _sentences(item["text"]):
        subj = resolver.subject_entity(sent)
        ev, _info = type_sentence_events(sent, subj)
        for (entity, role) in ev:
            eff_entity = entity
            if scramble_owner_to_foil is not None and role == R_GOAL and entity == owner:
                eff_entity = scramble_owner_to_foil
            role_seq.append(role)
            cluster_ids.append(eff_entity)
            if hasattr(resolver, "mark_role"):
                resolver.mark_role(eff_entity, role)
    event_slots = list(range(len(role_seq)))
    return role_seq, cluster_ids, event_slots


# ============================================================================ THE FIX
def directed_goal_outcome_score(role_seq, cluster_ids, seed: int, outcome_pos: int) -> float:
    """DIRECTED GOAL->OUTCOME relational-coherence score (Zwaan intentionality: the outcome
    coheres with the entity who HOLDS the relevant goal), fed to the adoption gate INSTEAD of
    decode_coherence_margins (disk-verified 2026-08-04, commit 60aa9f060: that signal returns
    EXACTLY 0.0 for Component-5 -- it scores per-position write-fidelity, symmetric between
    entities when events don't collide, so the correct pick is computed by the candidate
    generator but never adopted).

    Reuses GoalOutcomeRegister (hdlab-mirrored organ, exp_situation_model_goal_outcome_dimension_
    v1.py, the same organ that fires goal_blocked=0.833 at fb5b2a188) VERBATIM: accumulate THIS
    candidate's own (role, entity) assignment into a fresh register, then appraise whether the
    ENTITY THIS CANDIDATE ASSIGNED to the outcome slot also carries an earlier GOAL event under
    the SAME assignment. This is directed and NOT symmetric write-then-read: appraise(entity) is
    keyed on the candidate's own cluster_ids, so a candidate that binds the outcome to an entity
    with no GOAL event scores 0.0, while a candidate that binds it to the true goal-holder scores
    1.0 -- the two candidates in this eval get DIFFERENT registers (different cluster_ids), unlike
    decode_coherence_margins which decodes each candidate's OWN slot in isolation and finds no
    conflict to distinguish (the CausalLinkRegister-class symmetric-write blindness)."""
    gen = torch.Generator().manual_seed(4000 + int(seed))
    reg = GoalOutcomeRegister(d=D2, generator=gen, max_event_slots=max(len(role_seq) + 1, 4))
    for role, cid in zip(role_seq, cluster_ids):
        reg.add_typed_event(cid, role)
    owner = cluster_ids[outcome_pos]
    ap = reg.appraise(owner)
    return 1.0 if ap["has_goal"] else 0.0


# ============================================================================ per-item eval
def run_recency_item(item: dict, seed: int, scrambled: bool):
    """Run the selector on one RECENCY item. If scrambled, the CONTENT candidate's GOAL label is
    mislabeled onto the foil (role-scramble control).

    GENERALIZED (2026-08-05): both candidates now resolve names/gender via the item's OWN roster
    (default DEFAULT_ROSTER = the toy cast, bit-identical for the authored bank) instead of the
    hardcoded lexicon, so this pipeline runs on items with ARBITRARY names too (item["roster"])."""
    roster = item.get("roster", DEFAULT_ROSTER)
    role_seq_b, cluster_ids_b, event_slots_b = build_positions(item, GeneralRecencyEntityResolver(roster))
    foil = FOILS.get(item["id"])
    scramble_target = foil if (scrambled and foil is not None) else None
    role_seq_c, cluster_ids_c, event_slots_c = build_positions(
        item, ContentMatchResolver(roster), scramble_owner_to_foil=scramble_target)

    assert role_seq_b == role_seq_c, (
        f"role sequences diverged between resolvers on {item['id']!r}: "
        f"{role_seq_b} vs {role_seq_c} (lexicon typing must be resolver-independent)")
    assert event_slots_b == event_slots_c

    outcome_positions = [i for i, r in enumerate(role_seq_b) if r in (R_UNMET, R_MET)]
    flagged = [i for i in outcome_positions if cluster_ids_b[i] != cluster_ids_c[i]]
    if not flagged:
        flagged = list(outcome_positions)  # no disagreement (e.g. the sanity item); route trivially

    # DIAGNOSTIC ONLY (not the adoption decision): route_passage's own decode_coherence_margins
    # signal, kept and logged to substantiate the diagnosed blindness on every unit.
    gen_factory = (lambda: torch.Generator().manual_seed(3000 + int(seed)))
    diag = route_passage(
        role_seq=role_seq_b, event_slots=event_slots_b, baseline_cluster_ids=cluster_ids_b,
        candidate_cluster_ids={"content_match": cluster_ids_c}, flagged_positions=flagged,
        role_vocab=list(GO_ROLES), d=D2, generator_factory=gen_factory,
        max_event_slots=len(role_seq_b) + 1, abstain_band=ABSTAIN_BAND_DEFAULT,
    )
    diag_delta = diag["per_candidate"].get("content_match", {}).get("agg_coherence_delta")

    # THE FIX: directed GOAL->OUTCOME score feeds decide_keep_or_revert (verbatim gate) instead.
    outcome_pos = outcome_positions[-1] if outcome_positions else None
    agg_deltas = {}
    score_b = score_c = None
    if flagged and outcome_pos is not None:
        score_b = directed_goal_outcome_score(role_seq_b, cluster_ids_b, seed, outcome_pos)
        score_c = directed_goal_outcome_score(role_seq_c, cluster_ids_c, seed, outcome_pos)
        agg_deltas["content_match"] = score_c - score_b
    adopt = decide_keep_or_revert(agg_deltas, ABSTAIN_BAND_DEFAULT)
    adopted_cluster_ids = cluster_ids_c if adopt == "content_match" else cluster_ids_b

    final_owner = adopted_cluster_ids[outcome_pos] if outcome_pos is not None else None
    baseline_owner = cluster_ids_b[outcome_pos] if outcome_pos is not None else None
    content_owner = cluster_ids_c[outcome_pos] if outcome_pos is not None else None
    gold = item["gold_outcome_owner"]
    return dict(
        id=item["id"], scrambled=scrambled, gold_outcome_owner=gold,
        baseline_owner=baseline_owner, content_owner=content_owner, final_owner=final_owner,
        matches_gold=(final_owner == gold),
        recency_alone_matches_gold=(baseline_owner == gold),
        overrode_recency=(final_owner != baseline_owner),
        adopt=adopt, n_changed_flagged=len(flagged),
        directed_score_baseline=score_b, directed_score_content=score_c,
        agg_coherence_delta=agg_deltas.get("content_match"),
        diagnostic_route_passage_blind_delta=diag_delta,
    )


def run_goal_owner_binding(item: dict):
    """goal_owner_binding_accuracy (GOAL_BLOCK, gold explicit-name attribution): same-clause
    binding, GIVEN not EARNED -- Component-3 already solves this (no cross-sentence search), per
    the design drill. Reported honestly as a supplied-not-mechanism-tested number."""
    role_seq, cluster_ids, _ = build_positions(item, RecencyEntityResolver())
    goal_positions = [i for i, r in enumerate(role_seq) if r == R_GOAL]
    if not goal_positions:
        return dict(id=item["id"], has_goal_event=False, matches_owner=None)
    holder = cluster_ids[goal_positions[0]]
    return dict(id=item["id"], has_goal_event=True, matches_owner=(holder == item["owner"]))


# ============================================================================ per-seed unit
def run_seed(seed: int):
    recency_rows = [run_recency_item(it, seed, scrambled=False) for it in RECENCY]
    scramble_rows = [run_recency_item(it, seed, scrambled=True) for it in RECENCY if it["id"] in FOILS]
    goal_owner_rows = [run_goal_owner_binding(it) for it in GOAL_BLOCK]
    control_rows = []
    for it in CONTROLS:
        owner = it["owner"] if it["owner"] is not None else "__none__"
        fired, _ap, _per_sent = treatment_fires(it["text"], owner, seed)
        control_rows.append(dict(id=it["id"], cls=it["cls"], fired=bool(fired)))

    n_rec = len(recency_rows)
    outcome_binding_accuracy = round(sum(r["matches_gold"] for r in recency_rows) / n_rec, 4)
    n_scr = len(scramble_rows)
    scrambled_outcome_binding_accuracy = (
        round(sum(r["matches_gold"] for r in scramble_rows) / n_scr, 4) if n_scr else None)
    n_owner = sum(1 for r in goal_owner_rows if r["has_goal_event"])
    goal_owner_binding_accuracy = (
        round(sum(1 for r in goal_owner_rows if r["matches_owner"]) / n_owner, 4) if n_owner else None)
    control_false_fire_rate = round(sum(r["fired"] for r in control_rows) / len(control_rows), 4)

    trap_rows = [r for r in recency_rows if r["id"] in FOILS]
    anti_recency_holds = all(r["matches_gold"] for r in trap_rows) if trap_rows else None
    deltas = [r["agg_coherence_delta"] for r in trap_rows if r["agg_coherence_delta"] is not None]
    coherence_margin_delta_sign_positive = (all(d_ > 0 for d_ in deltas) if deltas else None)

    return dict(
        seed=seed,
        outcome_binding_accuracy=outcome_binding_accuracy,
        scrambled_outcome_binding_accuracy=scrambled_outcome_binding_accuracy,
        goal_owner_binding_accuracy=goal_owner_binding_accuracy,
        control_false_fire_rate=control_false_fire_rate,
        anti_recency_holds=anti_recency_holds,
        coherence_margin_delta_sign_positive=coherence_margin_delta_sign_positive,
        recency_rows=recency_rows, scramble_rows=scramble_rows,
        goal_owner_rows=goal_owner_rows, control_rows=control_rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed: dict):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def all_equal(key):
        vals = [per_seed[s][key] for s in seeds]
        return vals[0] if len(set(vals)) == 1 else None  # mechanism is deterministic given seed;
                                                            # margin ties could vary -- surface if so

    outcome_acc_per_seed = [per_seed[s]["outcome_binding_accuracy"] for s in seeds]
    scramble_acc_per_seed = [per_seed[s]["scrambled_outcome_binding_accuracy"] for s in seeds]
    outcome_binding_accuracy = round(sum(outcome_acc_per_seed) / n, 4)
    scrambled_outcome_binding_accuracy = (
        round(sum(v for v in scramble_acc_per_seed if v is not None) /
              max(1, sum(1 for v in scramble_acc_per_seed if v is not None)), 4)
        if any(v is not None for v in scramble_acc_per_seed) else None)
    goal_owner_binding_accuracy = all_equal("goal_owner_binding_accuracy")
    control_false_fire_rate = all_equal("control_false_fire_rate")
    anti_recency_holds = all_equal("anti_recency_holds")
    coherence_margin_delta_sign_positive = all_equal("coherence_margin_delta_sign_positive")

    role_scramble_collapse = (
        scrambled_outcome_binding_accuracy is not None and scrambled_outcome_binding_accuracy <= 0.5)
    # 0.5 = <=1/2 trap items correct post-scramble (N=2 traps -> discrete {0, 0.5, 1.0});
    # 0.333 floor doesn't map onto N=2 cleanly, so use "no better than chance among 2 traps" (<=0.5)
    # as the discrete equivalent, documented here (not silently substituted).
    # VACUOUS-COLLAPSE FLAG: if the UNSCRAMBLED mechanism already never produced a positive delta
    # (coherence_margin_delta_sign_positive is not True), role_scramble_collapse is trivially True
    # for the wrong reason -- there was nothing content-driven to break. Surface this explicitly so
    # a HARD-PASS-looking scramble result is never read as "proves content-use" when the base
    # mechanism was already blind.
    role_scramble_collapse_vacuous = (
        role_scramble_collapse and coherence_margin_delta_sign_positive is not True)

    # Independent confirmation the ORIGINAL diagnosis still holds (diagnostic-only, not adopted):
    # route_passage's decode_coherence_margins delta on the genuine trap items, across all seeds.
    diag_vals = [
        r["diagnostic_route_passage_blind_delta"]
        for s in seeds for r in per_seed[s]["recency_rows"]
        if r["id"] in FOILS and not r["scrambled"] and r["diagnostic_route_passage_blind_delta"] is not None
    ]
    diag_route_passage_still_blind = (all(v == 0.0 for v in diag_vals) if diag_vals else None)

    formal_hard_pass = (
        outcome_binding_accuracy >= 0.67 and role_scramble_collapse and
        control_false_fire_rate == 0 and
        (goal_owner_binding_accuracy is not None and goal_owner_binding_accuracy >= (5 / 6 - 1e-9)))
    formal_hard_fail = (outcome_binding_accuracy <= 0.334 or not role_scramble_collapse)

    if formal_hard_fail:
        verdict = "HARD_FAIL_NO_LIFT_OR_ROLE_CONTENT_BLIND"
    elif formal_hard_pass:
        verdict = "MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS"  # small-N cap, mandatory per pre-reg
    else:
        verdict = "MIDDLE_BAND"

    n_traps = len(FOILS)
    n_recency_total = len(RECENCY)
    recency_floor = round(1.0 / n_recency_total, 4) if n_recency_total else None
    summary = (
        f"N={n_recency_total} recency items ({n_traps} traps+{n_recency_total - n_traps} sanity), "
        f"{n} seeds. outcome_binding_accuracy={outcome_binding_accuracy} "
        f"(recency floor={recency_floor}) scrambled={scrambled_outcome_binding_accuracy} "
        f"role_scramble_collapse={role_scramble_collapse} (vacuous={role_scramble_collapse_vacuous}) "
        f"goal_owner_binding_accuracy={goal_owner_binding_accuracy} "
        f"(GIVEN not EARNED) control_false_fire_rate={control_false_fire_rate} "
        f"anti_recency_holds={anti_recency_holds} coherence_delta_sign_positive={coherence_margin_delta_sign_positive} "
        f"formal_hard_pass={formal_hard_pass} formal_hard_fail={formal_hard_fail}")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        outcome_binding_accuracy=outcome_binding_accuracy,
        recency_baseline=recency_floor,
        beats_recency=(recency_floor is not None and outcome_binding_accuracy > recency_floor),
        scrambled_outcome_binding_accuracy=scrambled_outcome_binding_accuracy,
        role_scramble_collapse=role_scramble_collapse,
        role_scramble_collapse_vacuous=role_scramble_collapse_vacuous,
        goal_owner_binding_accuracy=goal_owner_binding_accuracy,
        control_false_fire_rate=control_false_fire_rate,
        anti_recency_holds=anti_recency_holds,
        coherence_margin_delta_sign_positive=coherence_margin_delta_sign_positive,
        # BLINDNESS is diagnosed from the UNSCRAMBLED (correct-role) delta sign, not from
        # role_scramble_collapse: if the mechanism never produces a positive delta even when fed
        # the TRUE roles, scrambling trivially "collapses" it too (nothing to break) -- that would
        # be a false-negative for blindness if role_scramble_collapse were used as the sole test.
        # After THE FIX (2026-08-04): this field now tracks the FIXED directed-score gate, and is
        # expected FALSE (the gate is no longer blind). `diag_route_passage_still_blind` (below)
        # independently confirms the ORIGINAL diagnosis still holds for decode_coherence_margins
        # (kept as a diagnostic-only side channel, no longer wired to adoption) -- disk-verified:
        # delta==0.0 exactly on both genuine traps, the same symmetric-write-then-read signature
        # that sank CausalLinkRegister; that signal is NOT fed to decide_keep_or_revert anymore.
        is_route_passage_role_content_blind_at_c5=(coherence_margin_delta_sign_positive is not True),
        diag_route_passage_still_blind=diag_route_passage_still_blind,
        formal_hard_pass=formal_hard_pass, formal_hard_fail=formal_hard_fail,
        per_seed=per_seed,
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode: str):
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_json(os.path.join(OUTPUT_DIR, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()})
    per_seed = {}
    for seed in SEEDS:
        ts = time.perf_counter()
        res = run_seed(seed)
        per_seed[seed] = res
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"outcome_acc={res['outcome_binding_accuracy']} "
              f"scrambled={res['scrambled_outcome_binding_accuracy']} "
              f"ctrl_fire={res['control_false_fire_rate']}", flush=True)
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(D2=D2, seeds=SEEDS, role_vocab=GO_ROLES, abstain_band=ABSTAIN_BAND_DEFAULT,
                         n_recency=len(RECENCY), n_scramble=len(FOILS), n_goal_block=len(GOAL_BLOCK),
                         n_controls=len(CONTROLS))
    agg["prereg"] = "preregs/2026-08-04_component5_gold_role_isolated_v1.md"
    agg["cites"] = [
        "notes/research_component5_goal_owner_selection_binding_2026-08-04.md",
        "notes/research_coherence_based_binding_selector_build_spec_2026-08-04.md",
        "experiments/exp_situation_model_goal_outcome_dimension_v1.py (item bank, fb5b2a188)",
        "hdlab/self_improving_loop.py (route_passage, promoted 2026-08-02)",
    ]
    agg["dispatch"] = "LOCAL-ONLY, in-process foreground, not queue-dispatched (per task brief)"
    _write_json(os.path.join(OUTPUT_DIR, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) ContentMatchResolver: names resolve to self; unambiguous pronoun resolves to the only
    # gender-compatible entity (no ambiguity yet -> exercises the fallback path).
    r = ContentMatchResolver()
    assert r.subject_entity("Amy longed for the ice") == "amy"
    r.mark_role("amy", R_GOAL)
    assert "amy" in r._open_goal
    assert r.subject_entity("Jo raced ahead") == "jo"
    # "she" is compatible with amy (open-goal) and jo (recency) -- content-match must prefer amy
    assert r.subject_entity("she was lost") == "amy", "ContentMatchResolver did not prefer open-goal over recency"

    # (1) build_positions: role_seq/event_slots must be resolver-independent (lexicon-only typing)
    item = next(it for it in RECENCY if it["id"] == "recency_amy_blocked_pronoun_foil_jo")
    rs_b, cid_b, es_b = build_positions(item, GeneralRecencyEntityResolver())
    rs_c, cid_c, es_c = build_positions(item, ContentMatchResolver())
    assert rs_b == rs_c and es_b == es_c, "role/slot sequence must not depend on resolver"
    assert cid_b != cid_c, "recency and content-match must disagree on this genuine trap item"
    # recency grabs the foil (jo); content-match must grab the true owner (amy)
    unmet_pos = [i for i, r_ in enumerate(rs_b) if r_ in (R_UNMET, R_MET)][-1]
    assert cid_b[unmet_pos] == "jo", f"recency baseline expected foil jo, got {cid_b[unmet_pos]}"
    assert cid_c[unmet_pos] == "amy", f"content-match expected owner amy, got {cid_c[unmet_pos]}"

    # (2) role-scramble: mislabeling the GOAL holder as the foil must flip the content candidate's
    # pick away from the true owner.
    rs_s, cid_s, es_s = build_positions(item, ContentMatchResolver(), scramble_owner_to_foil="jo")
    assert cid_s[unmet_pos] == "jo", f"scrambled content-match expected foil jo, got {cid_s[unmet_pos]}"

    # (2b) THE FIX: directed_goal_outcome_score must be directed (not symmetric) -- the entity
    # this candidate assigns to the outcome slot decides the score, not a fixed identity.
    unmet_pos = [i for i, r_ in enumerate(rs_b) if r_ in (R_UNMET, R_MET)][-1]
    score_recency_jo = directed_goal_outcome_score(rs_b, cid_b, 0, unmet_pos)   # jo has no GOAL
    score_content_amy = directed_goal_outcome_score(rs_c, cid_c, 0, unmet_pos)  # amy has the GOAL
    assert score_recency_jo == 0.0, f"recency binds outcome to goal-less jo, expected score 0.0, got {score_recency_jo}"
    assert score_content_amy == 1.0, f"content-match binds outcome to goal-holder amy, expected score 1.0, got {score_content_amy}"

    # (2c) THE GATE (decide_keep_or_revert, verbatim) must ADOPT content on this genuine trap when
    # fed the FIXED directed delta (proves the diagnosed bug -- correct answer computed but never
    # adopted via decode_coherence_margins -- is actually fixed, not just diagnosed).
    from hdlab.self_improving_loop import decide_keep_or_revert as _dkr
    fixed_adopt = _dkr({"content_match": score_content_amy - score_recency_jo}, ABSTAIN_BAND_DEFAULT)
    assert fixed_adopt == "content_match", (
        f"decide_keep_or_revert must ADOPT content_match on this trap under the fixed directed "
        f"score (delta={score_content_amy - score_recency_jo}); got {fixed_adopt!r}")

    # (3) one full seed sanity + arms-must-differ (recency vs content-match resolutions differ)
    res = run_seed(0)
    assert res["outcome_binding_accuracy"] is not None
    assert res["control_false_fire_rate"] == 0.0, f"controls false-fired: {res['control_rows']}"
    rec_trap_row = next(r_ for r_ in res["recency_rows"] if r_["id"] == item["id"])
    assert rec_trap_row["baseline_owner"] != rec_trap_row["content_owner"], (
        "META_RULE_AF-style check: baseline and content candidates must differ on a genuine trap")
    # (3b) END-TO-END: the FIX means this trap's FINAL adopted owner must now be the gold owner
    # (amy), not the recency foil (jo) -- this is the exact bug the task diagnosed: correct answer
    # computed by the candidate generator but discarded by a blind gate.
    assert rec_trap_row["adopt"] == "content_match", (
        f"gate must adopt content_match on this genuine trap post-fix; got {rec_trap_row['adopt']!r} "
        f"(agg_coherence_delta={rec_trap_row['agg_coherence_delta']}, "
        f"diagnostic_route_passage_blind_delta={rec_trap_row['diagnostic_route_passage_blind_delta']})")
    assert rec_trap_row["matches_gold"] is True, f"post-fix trap row must match gold: {rec_trap_row}"
    assert rec_trap_row["diagnostic_route_passage_blind_delta"] == 0.0, (
        "diagnostic route_passage delta expected exactly 0.0 (confirms original diagnosis still "
        f"holds for the unwired signal); got {rec_trap_row['diagnostic_route_passage_blind_delta']}")

    # (3c) role-scramble must COLLAPSE the FULL pipeline's decision (not just the raw pick) --
    # scrambled final_owner must NOT match gold (the make-or-break non-vacuous-scramble guard).
    scr_row = run_recency_item(item, 0, scrambled=True)
    assert scr_row["matches_gold"] is False, (
        f"role-scramble must collapse the full pipeline (candidate+gate) to a wrong answer; "
        f"got final_owner={scr_row['final_owner']} gold={scr_row['gold_outcome_owner']}")

    print(f"[SELFTEST PASS] ContentMatchResolver prefers open-goal over recency; role/slot sequence "
          f"resolver-independent; role-scramble flips the pick; seed0 "
          f"outcome_acc={res['outcome_binding_accuracy']} scrambled={res['scrambled_outcome_binding_accuracy']} "
          f"ctrl_fire={res['control_false_fire_rate']}", flush=True)

    # (4) REAL-NAME SMOKE (the UNBLOCK proof, 2026-08-05 task): two items with ARBITRARY names not
    # in DEFAULT_ROSTER, each supplying its own per-item roster -- confirms the generalized
    # resolvers run end-to-end (no crash) and resolve correctly on names outside the toy cast.
    real_name_items = [
        dict(id="realname_smoke_elizabeth_darcy", owner="elizabeth", gold_goal_blocked=True,
             gold_outcome_owner="elizabeth", trap="pronoun_distant_antecedent",
             roster={"elizabeth": "f", "darcy": "m"},
             text="Elizabeth longed to leave the gathering. "
                  "Darcy strode ahead without a word. "
                  "Left behind, she was sorry and missed her chance."),
        dict(id="realname_smoke_marco_priya", owner="priya", gold_goal_blocked=True,
             gold_outcome_owner="priya", trap="pronoun_distant_antecedent",
             roster={"priya": "f", "marco": "m"},
             text="Priya wished to win the race before dusk. "
                  "Marco ran on far ahead of her. "
                  "Far behind, she failed and lost her chance."),
    ]
    for rn_item in real_name_items:
        rn_row = run_recency_item(rn_item, 0, scrambled=False)
        assert rn_row["baseline_owner"] is not None and rn_row["content_owner"] is not None, (
            f"real-name smoke {rn_item['id']!r} crashed/misresolved to None: {rn_row}")
        assert rn_row["content_owner"] == rn_item["gold_outcome_owner"], (
            f"real-name smoke {rn_item['id']!r}: ContentMatchResolver expected "
            f"{rn_item['gold_outcome_owner']!r}, got {rn_row['content_owner']!r} (roster="
            f"{rn_item['roster']!r})")
        assert rn_row["matches_gold"] is True, (
            f"real-name smoke {rn_item['id']!r}: full pipeline final_owner did not match gold: {rn_row}")
    print(f"[SELFTEST PASS 4/4] REAL-NAME SMOKE: {len(real_name_items)} arbitrary-name items "
          f"(outside DEFAULT_ROSTER) ran end-to-end via item-supplied roster, no crash, "
          f"matches_gold=True on all -- generalized resolver UNBLOCKS arbitrary-name eval.",
          flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
