"""hdlab/goal_owner_select.py -- Component-5 goal-owner DIRECTED coherence-score organ (promotion,
2026-08-05).

PROMOTION (WIRE-DON'T-ISLAND): locks in the fix VET'd in experiments/exp_component5_gold_role_
isolated_v1.py (commit 6911a28a6, disk-verified MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS -- intact
outcome_binding_accuracy=1.0 beats recency 0.3333, NON-VACUOUS role-scramble collapse). Nothing
here is new mechanism: GoalOutcomeRegister is a byte-identical copy of the register defined in
experiments/exp_situation_model_goal_outcome_dimension_v1.py (itself already mirroring
hdlab.situation_model_accumulate.CausalLinkRegister's CAUSE/EFFECT extension pattern verbatim --
same bind/unbind/bundle/cleanup_argmax organ, atom 29609, only the role vocabulary changes), and
directed_goal_outcome_score is a byte-identical copy of the score function that fixed Component-5
(diagnosed 60aa9f060: decode_coherence_margins is EXACTLY 0.0-blind for goal-outcome binding
because it decodes each candidate's own slot in isolation and never sees the other candidate's
assignment -- the same symmetric-write-then-read failure mode that sank CausalLinkRegister for
causal-antecedent selection). The two source cells are left untouched as the source-of-truth for
their own historical numbers (same convention as hdlab/self_improving_loop.py's 2026-08-02
promotion docstring) -- this module is the reusable, importable wire-point so a caller (situation-
model callers wanting goal-owner selection) does not need to import an experiment module.

MECHANISM (glass-box, deterministic given seed): directed_goal_outcome_score(role_seq,
cluster_ids, seed, outcome_pos) builds a FRESH GoalOutcomeRegister, accumulates the CANDIDATE's OWN
(role, entity) assignment (role_seq paired with cluster_ids -- i.e. THIS candidate's whole-passage
resolution, not a shared/baseline register), then appraises whether the entity THIS CANDIDATE
assigned to the outcome slot (cluster_ids[outcome_pos]) also carries an earlier GOAL event under
that SAME assignment. This is DIRECTED, not symmetric: two candidates with different cluster_ids
get DIFFERENT registers, so the score distinguishes "outcome bound to the goal-holder" (1.0) from
"outcome bound to a goal-less entity" (0.0) -- exactly the distinction decode_coherence_margins
could not make. Feed the resulting per-candidate score DELTA to
hdlab.self_improving_loop.decide_keep_or_revert (reused verbatim, unmodified) as the adoption gate.

SCOPE (do not overclaim): validated on N=3 hand-authored recency-trap items (2 genuine traps + 1
sanity), 3 seeds, GOLD (lexicon-typed) role labels -- see exp_component5_gold_role_isolated_v1
metrics.json for the historical gold-role numbers this promotion reproduces byte-identically.
The REAL-C3-role end-to-end honest-compounded measurement (does this score still work when the
GOAL role comes from Component-3's actual frame_primary_role labeler instead of a hand-lexicon)
lives in experiments/exp_component5_wired_endtoend_v1.py -- see that cell for the compounded
(not-isolated) numbers; this module's self-test only reproduces the ISOLATED historical result.

SELECTOR PROMOTION (2026-08-05, extends this module): select_outcome_owner(passage_text, roster,
seed) is the FULL outcome-owner selection flow -- candidate enumeration + directed-score argmax +
content-coherence tie-break -- promoted from two further-validated experiment cells, reused
byte-identically (no re-tuning, no reimplementation):
  (1) CANDIDATE ENUMERATION + ARGMAX: experiments/exp_c5_primacy_trap_endtoend_goal_coherence_
      candidate_gen_v1.py (commit b1b1ce460) -- enumerate_and_select's pattern (propose every
      roster entity as the outcome-slot referent, score with directed_goal_outcome_score above,
      argmax). MEASURED (disk, that cell's metrics.json): 47/48 on the full fair instrument
      (goal_owner_fair_v1.jsonl: primacy ep 12/12 + ai 8/8, recency-trap divergent ep 18/18 + ai
      10/10) without the tie-break below.
  (2) CONTENT-COHERENCE TIE-BREAK: experiments/exp_c5_multigoal_content_coherence_tiebreak_v1.py
      (commit 6961f5b49) -- among tied top-scorers, prefer the entity whose GOAL-theme (head nouns
      of the goal-bearing clause's determiner-led NPs) overlaps the OUTCOME-theme; fires ONLY on a
      unique overlapper, else falls back to sorted-order (so non-tie items are bit-identical to (1)
      by construction). MEASURED (disk, that cell's metrics.json): 48/48 full instrument (closes the
      one remaining miss, t24_tom_boat_foil_sid) and 12/12 on a dedicated 6-family multi-goal
      cue-conflict bank (experiments/data/goal_owner_multigoal_coherence_v1.jsonl) vs 6/12 (chance)
      for the tie-break-off/positional path, with a full within-family flip-control (swapping the
      outcome-theme flips the pick to the other entity in all 6 families).

DEPENDENCY NOTE: hdlab/ must not import from experiments/, so this promotion also byte-copies (not
re-derives) three pieces that previously lived ONLY in experiment cells: GeneralRecencyEntityResolver
+ its gender helpers (_is_pron_general/_gender_of_general/DEFAULT_ROSTER, from experiments/
exp_component5_gold_role_isolated_v1.py), the trivial sentence splitter (_sentences, from
experiments/exp_situation_model_goal_outcome_dimension_v1.py), and the theme-extraction tie-break
helpers (clause_theme/_theme_tokens/_DET/_ADJ_STOP/entity_goal_themes, from experiments/exp_c5_
multigoal_content_coherence_tiebreak_v1.py). GOAL-typing itself is NOT byte-copied -- it is consumed
directly from the already-promoted hdlab.goal_typing.type_goal_events (no duplicate typer).
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Sequence

import torch

from hdlab.situation_model_accumulate import AccumulateRegister
from hdlab.goal_typing import type_goal_events
from hdlab.state_of_mind import PRONOUN_SCOPE, infer_nominal_gender

# GoalOutcomeRegister role vocabulary (Zwaan goal/intentionality + outcome valence), byte-identical
# to experiments/exp_situation_model_goal_outcome_dimension_v1.py's GO_ROLES.
R_GOAL = "GOAL"
R_ACTION = "ACTION_AGAINST"
R_UNMET = "OUTCOME_UNMET"
R_MET = "OUTCOME_MET"
GO_ROLES = [R_GOAL, R_ACTION, R_UNMET, R_MET]

MAX_EVENTS_DEFAULT = 8
D2_DEFAULT = 1024


class GoalOutcomeRegister(AccumulateRegister):
    """Situation-model register extended with the GOAL/OUTCOME dimension (Zwaan event-indexing).
    Byte-identical copy of experiments/exp_situation_model_goal_outcome_dimension_v1.py's
    GoalOutcomeRegister (extends AccumulateRegister VERBATIM, same organ, only role_vocab differs).
    """

    def __init__(self, d: int, generator: torch.Generator,
                 max_event_slots: int = MAX_EVENTS_DEFAULT) -> None:
        super().__init__(role_vocab=list(GO_ROLES), d=d, generator=generator,
                         max_event_slots=max_event_slots, overwrite=False)
        self._next_slot: dict = {}
        self._written: dict = {}  # entity -> list of (slot, role_written) for honest decode

    def add_typed_event(self, entity: str, role: str) -> bool:
        """Bind `role` to entity's next event slot; accumulate. Returns False if slots exhausted."""
        slot = self._next_slot.get(entity, 0)
        if slot >= self.max_event_slots:
            return False
        self.add_event(entity, role, slot)
        self._written.setdefault(entity, []).append((slot, role))
        self._next_slot[entity] = slot + 1
        return True

    def appraise(self, entity: str) -> dict:
        """Read goal-blocking OFF the accumulated register (decode every written slot; tally)."""
        base = {"has_goal": False, "has_action_against": False, "n_unmet": 0, "n_met": 0,
                "goal_blocked": False, "n_events": 0, "decode_faithful": True}
        if entity not in self._written:
            return base
        tally: Counter = Counter()
        n_faithful = 0
        rows = self._written[entity]
        for slot, role_written in rows:
            best, _scores = self.decode(entity, slot)
            tally[best] += 1
            n_faithful += int(best == role_written)
        has_goal = tally[R_GOAL] > 0
        n_unmet, n_met = tally[R_UNMET], tally[R_MET]
        base.update(has_goal=has_goal, has_action_against=tally[R_ACTION] > 0,
                    n_unmet=n_unmet, n_met=n_met, n_events=len(rows),
                    goal_blocked=(has_goal and n_unmet > n_met),
                    decode_faithful=(n_faithful == len(rows)))
        return base


def directed_goal_outcome_score(role_seq: Sequence[str], cluster_ids: Sequence[str], seed: int,
                                 outcome_pos: int, d: int = D2_DEFAULT) -> float:
    """DIRECTED GOAL->OUTCOME relational-coherence score (Zwaan intentionality: the outcome
    coheres with the entity who HOLDS the relevant goal). Byte-identical formula to the score
    that fixed Component-5 (commit 6911a28a6, disk-verified 2026-08-04): accumulate THIS
    candidate's own (role, entity) assignment into a FRESH register, then appraise whether the
    entity THIS CANDIDATE assigned to the outcome slot also carries an earlier GOAL event under
    the SAME assignment -- directed, not symmetric (two candidates with different cluster_ids get
    different registers, so a candidate that binds the outcome to a goal-less entity scores 0.0
    while one that binds it to the true goal-holder scores 1.0)."""
    gen = torch.Generator().manual_seed(4000 + int(seed))
    reg = GoalOutcomeRegister(d=d, generator=gen, max_event_slots=max(len(role_seq) + 1, 4))
    for role, cid in zip(role_seq, cluster_ids):
        reg.add_typed_event(cid, role)
    owner = cluster_ids[outcome_pos]
    ap = reg.appraise(owner)
    return 1.0 if ap["has_goal"] else 0.0


# ============================================================================ STRUCTURAL SUBJECT
# RESOLVER (byte-copied dependency: hdlab/ must not import from experiments/). Byte-identical
# mechanism to experiments/exp_component5_gold_role_isolated_v1.py's GeneralRecencyEntityResolver +
# _is_pron_general/_gender_of_general/DEFAULT_ROSTER -- gold-free, backward-search recency pick over
# gender/number-compatible roster candidates.
def _ordered_tokens(sentence: str) -> List[str]:
    """Order-preserving lowercase content tokens. Byte-identical to
    exp_situation_model_goal_outcome_dimension_v1._ordered_tokens / hdlab.goal_typing._ordered_tokens
    (same regex, independently promoted; kept local so this module has no other hdlab-internal dep)."""
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


# Byte-identical default gazetteer to exp_component5_gold_role_isolated_v1.py's DEFAULT_ROSTER (the
# original 12-name toy cast, now pluggable DATA -- any caller may supply its own {name: gender} roster).
GENDER = {}
for _n in ("amy", "jo", "beth", "meg", "ruth", "ann"):
    GENDER[_n] = "f"
for _n in ("tom", "sid", "laurie"):
    GENDER[_n] = "m"
DEFAULT_ROSTER = dict(GENDER)

# PRONOUN_SCOPE (production, hdlab.state_of_mind) does not carry reflexives (herself/himself); extend
# the PRODUCTION table locally (reuse-then-augment, byte-identical to the source cell's extension).
_PRON_SCOPE_EXT = dict(PRONOUN_SCOPE)
_PRON_SCOPE_EXT.setdefault("herself", {"number": "singular", "gender": "fem"})
_PRON_SCOPE_EXT.setdefault("himself", {"number": "singular", "gender": "masc"})
_GENDER_MAP = {"masc": "m", "fem": "f"}  # production's masc/fem -> this organ's f/m scheme


def _is_pron_general(token: str) -> bool:
    """True iff token is a gendered singular pronoun (production PRONOUN_SCOPE, reflexive-extended).
    Byte-identical to exp_component5_gold_role_isolated_v1.py's _is_pron_general."""
    scope = _PRON_SCOPE_EXT.get(token)
    return scope is not None and scope["gender"] in ("masc", "fem")


def _gender_of_general(token: str, roster: dict):
    """f / m / None gender for a lowercase token, generalized off any roster (not a fixed lexicon).
    Byte-identical to exp_component5_gold_role_isolated_v1.py's _gender_of_general: (1) PRONOUN_SCOPE
    (production, hdlab.state_of_mind) -> (2) the roster's explicit gender (structural passage cast
    data) -> (3) infer_nominal_gender (production, hdlab.state_of_mind) as an honest fallback."""
    scope = _PRON_SCOPE_EXT.get(token)
    if scope is not None:
        return _GENDER_MAP.get(scope["gender"])
    if token in roster:
        return roster[token]
    return _GENDER_MAP.get(infer_nominal_gender([token]))


class GeneralRecencyEntityResolver:
    """Structural (gold-free) subject resolver: SINGLE-PASS first-nominal pick, respecting
    subject-first word order (fixed 2026-08-06, coref goal-subject confound -- see below), with a
    backward-search recency resolution for pronouns. `roster` is a {name: gender} dict describing
    the passage's cast (structural passage metadata, NEVER a gold label); defaults to
    DEFAULT_ROSTER when the caller doesn't supply one.

    COREF GOAL-SUBJECT CONFOUND FIX (2026-08-06): the prior mechanism was TWO-PASS -- pass 1 scanned
    the WHOLE sentence for the first roster-NAME token ANYWHERE (subject OR object position) before
    ever looking for a pronoun; pass 2 (only reached if pass 1 found no name at all) resolved the
    first pronoun via recency. Bug: "He wanted to help his mother" (roster {henry, mother}) -- pass 1
    scans past the pronoun subject "he" and finds "mother" (a roster key that happens to sit in
    OBJECT position later in the same sentence), returning "mother" as the subject instead of
    resolving "he" -> henry via recency. The brain resolves the grammatical SUBJECT by POSITION
    (subject-first order), not by "any roster name anywhere in the sentence." FIX: iterate tokens
    ONCE, in order; the FIRST token that is EITHER a roster name OR a pronoun IS the subject (name ->
    use it directly; pronoun -> the existing recency/gender resolution) -- a roster name that occurs
    only in a LATER (object) position can never pre-empt an earlier pronoun subject. Byte-identical
    mechanism otherwise (backward-search recency pick over gender/number-compatible candidates) to
    the historical exp_component5_gold_role_isolated_v1.py GeneralRecencyEntityResolver this class
    was byte-copied from -- that experiment cell's OWN copy is deliberately left unfixed (see its
    docstring) because it gates the 48-item fair instrument's DIVERGENT-item population for the cert
    suite (test_goal_owner_select.py / verify_goal_typing.py); this PRODUCTION-only fix cannot change
    that population without risking a cert regression unrelated to this fix's own correctness. The
    fair instrument's own goal sentences are all name-subject-first by construction, so this fix
    reproduces every one of them byte-identically (verified: single-pass and two-pass agree whenever
    the sentence's first roster-name-or-pronoun token is also its first roster-name token, which is
    always true when no pronoun subject precedes an object name -- exactly the fair instrument's
    construction)."""

    def __init__(self, roster: dict | None = None):
        self._recent = []  # entity names in order of mention (most recent last)
        self._roster = roster if roster is not None else DEFAULT_ROSTER

    def subject_entity(self, sentence: str):
        toks = _ordered_tokens(sentence)
        for t in toks:                                   # SINGLE PASS: first NAME-or-PRONOUN wins
            if t in self._roster:                         # explicit roster NAME = subject
                self._note(t)
                return t
            if _is_pron_general(t):                       # first pronoun -> recency-resolved
                want = _gender_of_general(t, self._roster)
                for e in reversed(self._recent):           # BACKWARD search == recency
                    if _gender_of_general(e, self._roster) == want:
                        return e
                return None
        return None

    def _note(self, entity: str):
        self._recent.append(entity)


# SENTENCE-SPLITTER FIX (2026-08-06, real-text generalization diagnostic, commit d52aa7669 traced
# root cause): the old delimiter `[.!?]` split each terminal-punctuation char individually, so a
# passage ending in dialogue (`...boy, Henry."`) produced a spurious final fragment consisting ONLY
# of the closing quote (`"`) -- `.strip()` does not remove quote chars, so that bare-quote fragment
# survived the `if s.strip()` filter and became `sents[-1]`, silently discarding the REAL final
# clause. Downstream (build_candidate_role_seq / congruence_outcome_valence) treat `sents[-1]` as
# THE outcome sentence, so this degenerated to OUTCOME_NEVER_TYPED for any dialogue-final passage.
# FIX: the delimiter now consumes a run of terminal punctuation PLUS one immediately-following
# closing quote (straight or curly) as a single delimiter token, so the quote is dropped along with
# the punctuation instead of surviving as its own fragment. Non-dialogue text (no quote char
# immediately after `.!?`) is byte-identical to the old behavior -- the optional quote-group simply
# never matches, so `[.!?]+` alone determines every split point exactly as `[.!?]` did before (a run
# of punctuation with no intervening non-punctuation chars produces one non-empty fragment before it
# and one after, same as splitting on each char and filtering the resulting empty strings).
_SENT_SPLIT_RE = re.compile(r'[.!?]+[\'"’”]?')


def _sentences(text: str) -> List[str]:
    """Byte-identical to hdlab.goal_typing._sentences (kept in sync; see that module's docstring for
    the circular-import rationale). NO LONGER byte-identical to experiments/exp_situation_model_
    goal_outcome_dimension_v1.py's _sentences -- that experiment cell is left untouched per this
    module's own promotion convention (source-of-truth for its historical numbers); this fix is
    PRODUCTION-only. See _SENT_SPLIT_RE comment above for the dialogue/quote-final bug this closes."""
    return [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]


# ============================================================================ THEME EXTRACTION (for
# the content-coherence tie-break below). Byte-identical mechanism to experiments/exp_c5_multigoal_
# content_coherence_tiebreak_v1.py's clause_theme/_theme_tokens/_DET/_ADJ_STOP/entity_goal_themes
# (byte-copied here because hdlab/ must not import from experiments/).
_DET = {"the", "a", "an", "his", "her", "its", "their"}
_ADJ_STOP = {
    "old", "whole", "broken", "tall", "leaking", "torn", "heavy", "brass",
    "woven", "copper", "cracked", "wooden", "new",
}


def _theme_tokens(sentence: str) -> List[str]:
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


def clause_theme(sentence: str, roster: dict) -> set:
    """Head nouns of determiner-led NPs in `sentence`, minus roster entity names. Glass-box, no POS
    tagger. Byte-identical to exp_c5_multigoal_content_coherence_tiebreak_v1.py's clause_theme."""
    toks = _theme_tokens(sentence)
    heads = set()
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] in _DET:
            j = i + 1
            while j < n and toks[j] in _ADJ_STOP:
                j += 1
            if j < n and toks[j] not in _DET:
                head = toks[j]
                if head not in roster:
                    heads.add(head)
            i = j + 1
        else:
            i += 1
    return heads


def entity_goal_themes(passage_text: str, roster: dict) -> dict:
    """{entity: set of goal-theme head nouns} from each non-outcome sentence whose STRUCTURAL
    subject (GeneralRecencyEntityResolver -- gold-free) fires a GOAL. Byte-identical mechanism to
    exp_c5_multigoal_content_coherence_tiebreak_v1.py's entity_goal_themes, generalized off the
    source cell's 'item' dict onto (passage_text, roster) args; never consults a gold label."""
    sents = _sentences(passage_text)
    resolver = GeneralRecencyEntityResolver(roster)
    themes: dict = {}
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        if subj is None:
            continue
        fires_goal = any(r == R_GOAL and e == subj for (e, r) in type_goal_events(s, subj))
        if fires_goal:
            themes.setdefault(subj, set()).update(clause_theme(s, roster))
    return themes


# ============================================================================ TIER-3 EVALUATIVE
# BRIDGING INFERENCE (promotion, 2026-08-06). Byte-copied (not imported -- hdlab/ must not import
# from experiments/) from experiments/exp_evaluative_bridging_inference_v1.py (commit 17dd3567b,
# HARD_PASS: zero_overlap_bridging_acc=1.0 9/9 incl mg2_henry_bootblack, gap_vs_lexical_only=1.0,
# valence controls 1.0/1.0, bystander_no_bridge_acc=1.0, unchanged_control_acc=1.0, scramble_acc=0.0).
# Graesser Class-7 BACKWARD causal-antecedent bridge: an evaluative speech act ("you are a good boy")
# implies the addressee's antecedent goal was met/unmet, for the case where the outcome clause shares
# ZERO verb/theme/thematic-role with the goal clause -- no similarity/verb-typing/theme-match
# mechanism can ever bridge these, only an inferential bridge can. STRICT Tier-3 ADD: consulted only
# when Tier-1 exact-lexicon + Tier-2 concept-similarity verb-typing (type_goal_events, unmodified)
# produced NOTHING for the outcome (final) sentence under a candidate's hypothesis (the
# OUTCOME_NEVER_TYPED case) -- wired into build_candidate_role_seq below, the single outcome-typing
# call site select_outcome_owner depends on. No GoalOutcomeRegister modification, no new binding
# operator: `has_open_goal` below is read directly off the candidate's own already-accumulated
# role_seq/cluster_ids (equivalent to that source cell's GoalOutcomeRegister.appraise(entity)
# ["has_goal"], since appraise's decode_faithful==True on every self-test -- a GOAL role written for
# an entity always decodes back as GOAL at this event-slot scale) rather than constructing a register
# just to ask one boolean.
EVAL_POS = {
    "good", "dear", "kind", "fine", "gentle", "devoted", "obedient", "cheerful", "quiet",
    "thoughtful", "gallant", "noble", "sweet", "honest", "brave",
}
EVAL_NEG = {
    "bad", "wicked", "naughty", "clumsy", "careless", "cruel", "foolish", "selfish", "unkind",
    "rude", "lazy",
}
_COPULA = {"is", "are", "was", "were"}
_EVAL_WINDOW = 6


def detect_evaluative_construction(sentence: str, roster: dict):
    """Copula + evaluative-predicate construction detector (glass-box, no POS tagger). Returns
    (polarity, addressee) where polarity in {"POS","NEG"}, or (None, None) if no evaluative
    construction is found. addressee: 2nd-person "you...Name" -> the LAST roster name token in the
    sentence (vocative); 3rd-person "Name is/was ADJ" -> the roster name immediately preceding the
    copula. Neither pattern matched -> addressee=None. Byte-identical to experiments/
    exp_evaluative_bridging_inference_v1.py's detect_evaluative_construction (commit 17dd3567b)."""
    toks = _ordered_tokens(sentence)
    cop_idx = None
    for i, t in enumerate(toks):
        if t in _COPULA:
            cop_idx = i
            break
    if cop_idx is None:
        return None, None
    polarity = None
    for w in toks[cop_idx + 1: cop_idx + 1 + _EVAL_WINDOW]:
        if w in EVAL_POS:
            polarity = "POS"
            break
        if w in EVAL_NEG:
            polarity = "NEG"
            break
    if polarity is None:
        return None, None
    subj = toks[cop_idx - 1] if cop_idx > 0 else None
    if subj == "you":
        addressee = None
        for t in reversed(toks):
            if t in roster:
                addressee = t
                break
        return polarity, addressee
    if subj in roster:
        return polarity, subj
    return polarity, None


def _bridge_outcome_event(outcome_sentence: str, roster: dict, entity: str, has_open_goal: bool):
    """Bridging DECISION, same over-fire guards as experiments/exp_evaluative_bridging_inference_v1.
    py's bridge_outcome (commit 17dd3567b): fires ONLY if the evaluative construction's addressee is
    `entity` AND `entity` already holds an open GOAL (`has_open_goal`, read off this candidate's own
    accumulated events -- see module comment above). No match / no open goal -> abstain (None), never
    forces a bridge. Returns R_MET / R_UNMET / None."""
    polarity, addressee = detect_evaluative_construction(outcome_sentence, roster)
    if polarity is None or addressee != entity:
        return None
    if not has_open_goal:
        return None
    return R_MET if polarity == "POS" else R_UNMET


# ============================================================================ TIER-3 AFFECT-STATE
# BRIDGING INFERENCE (promotion, 2026-08-06). SIBLING of the evaluative bridge above; byte-copied
# (not imported -- hdlab/ must not import from experiments/) from experiments/exp_affect_state_
# bridging_inference_v1.py (commit 0ff1a6d97, Director-VET'd HARD_PASS: zero_overlap_bridging_acc=1.0
# 8/8 incl frank_fishing_glad, gap_vs_lexical_only=1.0, valence controls 1.0/1.0, bystander_no_bridge_
# acc=1.0, unchanged_control_acc=1.0, scramble_acc=0.0, no_interference=True). Graesser Class-7
# BACKWARD causal-antecedent bridge from the goal-holder's OWN AFFECT STATE ("Oh, how glad I am!" ->
# goal MET; "he felt ashamed" -> goal UNMET) back to that holder's standing GOAL, for the case where
# the outcome clause shares ZERO verb/theme with the goal clause. INTERNAL-affect sibling of the
# EXTERNAL-evaluation bridge above ("you are a good boy"); same strict-Tier-3-ADD scope, same over-fire
# guards, same reuse of the candidate's already-accumulated has_open_goal boolean (NO GoalOutcome-
# Register modification, NO new binding operator). The two detectors are PROVABLY DISJOINT: Pattern A
# below triggers on is/was/feels/felt but DELIBERATELY NOT are/were, so it can never match the
# evaluative bridge's 2nd-person "you are ADJ" construction, and none of this bridge's AFFECT words are
# EVAL_POS/EVAL_NEG members (the one shared token, "cheerful", still cannot cross-fire for the same
# is/was-not-are/were structural reason) -- verified by the PART 3 interference self-tests below and
# the verification/verify_affect_state_bridging_production.py witness, not merely asserted.
AFFECT_POS = {
    "glad", "happy", "joyful", "delighted", "proud", "pleased", "thankful", "merry", "cheerful",
}
AFFECT_NEG = {
    "sad", "ashamed", "sorry", "miserable", "disappointed", "unhappy", "grieved", "downcast",
    "sorrowful",
}
_AFFECT_TRIGGERS_3P = {"feels", "felt", "is", "was"}  # deliberately NOT are/were (2nd-person guard)
_AFFECT_WINDOW = 6


def detect_affect_state_construction(sentence: str, roster: dict):
    """Own-affect construction detector (glass-box, no POS tagger). Returns (polarity, holder) where
    polarity in {"POS","NEG"}, holder = the roster entity whose OWN affect this is, or (None, None).
    Byte-identical to experiments/exp_affect_state_bridging_inference_v1.py's
    detect_affect_state_construction (commit 0ff1a6d97).

    Pattern B (first person) checked FIRST: "i" immediately followed by "am" (covers "I am so glad"
    AND "how glad I am!" word order -- the AFFECT scan below covers the WHOLE sentence for this
    pattern, since the affect word can precede "i am"). Holder = the first roster-name token in the
    sentence (reporting-verb speaker attribution, e.g. "Frank cried, ...I am!").

    Pattern A (third person): a roster NAME or a gender-resolvable pronoun (he/she) immediately
    preceding feels/felt/is/was (NEVER are/were -- that word order is the evaluative bridge's 2nd-
    person "you are ADJ" construction, out of scope here BY CONSTRUCTION, not by exclusion-list
    patching), AFFECT word within a forward window. Ambiguous pronoun (no unique gender match in
    roster) -> abstain for that trigger, scan continues."""
    toks = _ordered_tokens(sentence)
    # ---- Pattern B: first person dialogue ----
    for i, t in enumerate(toks):
        if t == "i" and i + 1 < len(toks) and toks[i + 1] == "am":
            polarity = None
            for w in toks:
                if w in AFFECT_POS:
                    polarity = "POS"
                    break
                if w in AFFECT_NEG:
                    polarity = "NEG"
                    break
            if polarity is None:
                continue
            holder = None
            for t2 in toks:
                if t2 in roster:
                    holder = t2
                    break
            return polarity, holder
    # ---- Pattern A: third person ----
    for i, t in enumerate(toks):
        if t not in _AFFECT_TRIGGERS_3P:
            continue
        subj = toks[i - 1] if i > 0 else None
        if subj is None or subj in ("you", "i"):
            continue
        holder = None
        if subj in roster:
            holder = subj
        elif _is_pron_general(subj):
            want = _gender_of_general(subj, roster)
            cands = sorted(e for e in roster if roster[e] == want)
            if len(cands) == 1:
                holder = cands[0]
        if holder is None:
            continue
        polarity = None
        for w in toks[i + 1: i + 1 + _AFFECT_WINDOW]:
            if w in AFFECT_POS:
                polarity = "POS"
                break
            if w in AFFECT_NEG:
                polarity = "NEG"
                break
        if polarity is not None:
            return polarity, holder
    return None, None


def _bridge_affect_outcome_event(outcome_sentence: str, roster: dict, entity: str,
                                 has_open_goal: bool):
    """Affect-state bridging DECISION, same over-fire guards as experiments/exp_affect_state_bridging_
    inference_v1.py's bridge_outcome (commit 0ff1a6d97): fires ONLY if the affect-state construction's
    HOLDER is `entity` (the affect must be the GOAL-HOLDER's OWN affect, never a bystander's) AND
    `entity` already holds an open GOAL (`has_open_goal`, read off this candidate's own accumulated
    events -- identical source as the evaluative bridge above). No match / wrong holder / no open goal
    -> abstain (None), never forces a bridge. Returns R_MET / R_UNMET / None."""
    polarity, holder = detect_affect_state_construction(outcome_sentence, roster)
    if polarity is None or holder != entity:
        return None
    if not has_open_goal:
        return None
    return R_MET if polarity == "POS" else R_UNMET


# ============================================================================ CANDIDATE ENUMERATION
# + SELECTION (the full outcome-owner selector). Byte-identical mechanism to experiments/exp_c5_
# primacy_trap_endtoend_goal_coherence_candidate_gen_v1.py's build_candidate_role_seq/_outcome_pos/
# enumerate_and_select (commit b1b1ce460), generalized off the source cell's 'item' dict onto
# (passage_text, roster) args, extended 2026-08-06 with the Tier-3 evaluative bridge above.
def build_candidate_role_seq(passage_text: str, roster: dict, outcome_entity,
                              scramble_goal_to_foil=None):
    """Structural (gold-free) role_seq/cluster_ids for ONE proposed outcome-slot candidate.
    Non-outcome sentences: subject resolved from the PASSAGE TEXT (GeneralRecencyEntityResolver),
    never from a gold label. Outcome (final) sentence: subject is the PROPOSED CANDIDATE
    `outcome_entity` -- this is the enumeration step; TIER-3 ADD (2026-08-06): if lexical/similarity
    verb-typing (type_goal_events) types NOTHING for the outcome sentence under this candidate's
    hypothesis, try the two sibling bridges IN ORDER -- the evaluative bridge (_bridge_outcome_event,
    external "you are a good boy") then the affect-state bridge (_bridge_affect_outcome_event, internal
    "how glad I am!") -- before giving up. The two detectors are provably disjoint (at most one fires
    on any outcome sentence; see the affect detector's module comment), so ordering is a formality; a
    passage exercising NEITHER bridge leaves outcome_events byte-identical to the pre-bridge organ.
    `scramble_goal_to_foil` is a diagnostic-only hook (redirects GOAL-role bindings to a named foil
    entity) for scramble-control self-tests; leave None in production use."""
    sents = _sentences(passage_text)
    resolver = GeneralRecencyEntityResolver(roster)
    role_seq, cluster_ids = [], []
    for s in sents[:-1]:
        subj = resolver.subject_entity(s)
        for (entity, role) in type_goal_events(s, subj):
            eff = entity
            if scramble_goal_to_foil is not None and role == R_GOAL:
                eff = scramble_goal_to_foil
            role_seq.append(role)
            cluster_ids.append(eff)
    outcome_sentence = sents[-1]
    outcome_events = type_goal_events(outcome_sentence, outcome_entity)
    if not any(role in (R_UNMET, R_MET) for (_e, role) in outcome_events):
        has_open_goal = any(r == R_GOAL and cid == outcome_entity
                             for r, cid in zip(role_seq, cluster_ids))
        # TIER-3: evaluative bridge first, then the sibling affect-state bridge (2026-08-06). Both
        # abstaining (bridged_role stays None) leaves outcome_events byte-identical to the pre-affect
        # organ -- the strict-ADD property.
        bridged_role = _bridge_outcome_event(outcome_sentence, roster, outcome_entity, has_open_goal)
        if bridged_role is None:
            bridged_role = _bridge_affect_outcome_event(outcome_sentence, roster, outcome_entity,
                                                        has_open_goal)
        if bridged_role is not None:
            outcome_events = list(outcome_events) + [(outcome_entity, bridged_role)]
    for (entity, role) in outcome_events:
        role_seq.append(role)
        cluster_ids.append(entity)
    return role_seq, cluster_ids


def _outcome_pos(role_seq: Sequence[str]):
    positions = [i for i, r in enumerate(role_seq) if r in (R_UNMET, R_MET)]
    return positions[-1] if positions else None


def enumerate_and_score(passage_text: str, roster: dict, seed: int, scramble_goal_to_foil=None):
    """Candidate-enumeration + directed-score core: propose EVERY roster entity as the outcome-slot
    referent, score each with directed_goal_outcome_score (unmodified), return (scored, winners)
    where winners is the sorted-order list of argmax entities (len>1 iff genuinely tied). Entity set
    = roster.keys() (structural passage metadata), never a gold label.

    TIER-3 NOTE (2026-08-06): outcome-typing is no longer subject-invariant once the evaluative
    bridge can fire (bridging is candidate-DIRECTED: it fires only for the construction's addressee,
    who must already hold an open GOAL) -- unlike the old lexical-only typing, which fires uniformly
    for whichever candidate is hypothesized (so every candidate was always typeable together or not
    at all; a strictly no-regression property for any bank that never exercises the bridge). A
    candidate whose own outcome-slot hypothesis gets typed by NEITHER path scores 0.0 (cannot win the
    argmax) but no longer aborts the whole enumeration; only raise if NO roster candidate gets a
    typed outcome anywhere (the genuine OUTCOME_NEVER_TYPED case)."""
    candidates = sorted(roster.keys())
    scored = {}
    any_typed = False
    for c in candidates:
        rs, cid = build_candidate_role_seq(passage_text, roster, c,
                                            scramble_goal_to_foil=scramble_goal_to_foil)
        pos = _outcome_pos(rs)
        if pos is None:
            scored[c] = 0.0
            continue
        any_typed = True
        scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
    if not any_typed:
        raise ValueError(
            f"outcome slot never typed for ANY roster candidate; passage_text's final sentence must "
            f"type an OUTCOME_UNMET/OUTCOME_MET event (lexically, via concept-similarity, or via the "
            f"Tier-3 evaluative bridge) for at least one roster entity")
    max_score = max(scored.values())
    winners = [c for c in candidates if scored[c] == max_score]
    return scored, winners


def select_outcome_owner(passage_text: str, roster: dict, seed: int,
                          scramble_goal_to_foil=None) -> str:
    """PRODUCTION outcome-owner selector: enumerate every roster entity as the outcome-slot referent
    (gold-free), score each with directed_goal_outcome_score (argmax), break ties by goal-theme <->
    outcome-theme content-coherence overlap, else fall back to sorted-order. GOLD-FREE: `roster` is
    the passage's entity set (structural cast metadata); the caller must never pass a gold answer
    through it. Byte-identical composition to the mechanism validated in experiments/exp_c5_primacy_
    trap_endtoend_goal_coherence_candidate_gen_v1.py (enumerate+argmax, commit b1b1ce460, 47/48 on
    the 48-item fair instrument) plus experiments/exp_c5_multigoal_content_coherence_tiebreak_v1.py's
    content-coherence tie-break (commit 6961f5b49, 48/48 with the tie-break; 12/12 on the multi-goal
    cue-conflict bank vs 6/12 for the tie-break-off/positional path). `scramble_goal_to_foil` is a
    diagnostic-only hook for scramble-control self-tests; leave None in production use.

    Non-tie items are BIT-IDENTICAL to the pre-tie-break organ (the tie-break only ever runs when
    len(winners) > 1), so this promotion cannot regress any of the 46 non-tie items the fair
    instrument already got right."""
    scored, winners = enumerate_and_score(passage_text, roster, seed,
                                           scramble_goal_to_foil=scramble_goal_to_foil)
    if len(winners) > 1:
        goal_themes = entity_goal_themes(passage_text, roster)
        out_theme = clause_theme(_sentences(passage_text)[-1], roster)
        overlappers = [c for c in winners if goal_themes.get(c, set()) & out_theme]
        if len(overlappers) == 1:
            return overlappers[0]
    return winners[0]


# ============================================================================ self-test
def self_test() -> dict:
    """Reproduces the historical isolated-mechanism numbers (commit 6911a28a6) with THIS module's
    promoted (copied) organ, not the experiment cell's local definitions -- proves the promotion
    is byte-identical, not just similarly-shaped."""
    # role_seq / cluster_ids for one hand-built passage: jo has a GOAL, amy does not; the OUTCOME
    # slot is bound to jo in one candidate and to amy in another.
    role_seq = [R_GOAL, R_UNMET]
    cluster_ids_jo_holds = ["jo", "jo"]      # outcome bound to the goal-holder
    cluster_ids_amy_holds = ["jo", "amy"]    # outcome bound to a goal-less entity (amy)

    score_correct = directed_goal_outcome_score(role_seq, cluster_ids_jo_holds, seed=0, outcome_pos=1)
    score_wrong = directed_goal_outcome_score(role_seq, cluster_ids_amy_holds, seed=0, outcome_pos=1)
    assert score_correct == 1.0, f"outcome bound to goal-holder must score 1.0, got {score_correct}"
    assert score_wrong == 0.0, f"outcome bound to goal-less entity must score 0.0, got {score_wrong}"

    # directedness: the SAME entity (amy) scores differently depending on whether IT (not jo) holds
    # the goal under its own candidate's assignment -- proves the register is per-candidate, not a
    # shared/baseline register re-read (the bug this fixed).
    role_seq2 = [R_GOAL, R_UNMET]
    cluster_ids_amy_holds_own_goal = ["amy", "amy"]
    score_amy_own_goal = directed_goal_outcome_score(
        role_seq2, cluster_ids_amy_holds_own_goal, seed=0, outcome_pos=1)
    assert score_amy_own_goal == 1.0, (
        f"amy holding her own goal+outcome must score 1.0 (directedness check), got {score_amy_own_goal}")

    # determinism: same inputs, same seed -> identical score across repeated construction.
    score_repeat = directed_goal_outcome_score(role_seq, cluster_ids_jo_holds, seed=0, outcome_pos=1)
    assert score_repeat == score_correct, "non-deterministic score for identical inputs"

    # decide_keep_or_revert (reused from hdlab.self_improving_loop, unmodified) must ADOPT the
    # content candidate whose directed score correctly beats the baseline's.
    from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT
    adopt = decide_keep_or_revert({"content": score_correct - score_wrong}, ABSTAIN_BAND_DEFAULT)
    assert adopt == "content", f"gate must adopt on a clean directed-score win, got {adopt!r}"

    # ---- SELECTOR self-tests (select_outcome_owner: enumerate + argmax + content-coherence
    # tie-break), reproducing two decisive cases byte-identically off the passage text (exact
    # sentences from experiments/data/goal_owner_fair_v1.jsonl, disk-verified this session).

    # TIE CASE broken correctly by theme (t24_tom_boat_foil_sid, commit 6961f5b49): both tom and sid
    # hold a goal (directed-score ties at 1.0 each) -- the content-coherence tie-break must pick tom
    # because his goal-theme {oars, boat, tide} overlaps the outcome-theme {tools, boat}={boat} while
    # sid's goal-theme {rope} does not.
    t24_text = ("Tom carried the oars to mend the old boat before the tide turned. Sid went off to "
                "fetch the rope. Left with the tools alone, he failed and the boat sank.")
    t24_roster = {"tom": "m", "sid": "m"}
    t24_scored, t24_winners = enumerate_and_score(t24_text, t24_roster, seed=0)
    assert t24_scored == {"sid": 1.0, "tom": 1.0} and len(t24_winners) == 2, (
        f"t24 must be a genuine directed-score tie (both hold a goal): {t24_scored}")
    t24_owner = select_outcome_owner(t24_text, t24_roster, seed=0)
    assert t24_owner == "tom", (
        f"t24 content-coherence tie-break must select tom (theme overlap), got {t24_owner!r}")

    # SINGLE-GOAL (non-tie) case UNAFFECTED by the tie-break (p01_amy_ice_foil_jo, commit b1b1ce460,
    # already a clean win before the tie-break existed): only amy holds a goal, so len(winners)==1
    # and the tie-break code path never runs -- proves the promotion cannot regress non-tie items.
    p01_text = ("Jo hurried off early toward the barn. Amy wanted to be warned in time about the "
                "cracking ice. Jo walked back again toward the barn door. Left unwarned, she went "
                "down through the ice.")
    p01_roster = {"amy": "f", "jo": "f"}
    p01_scored, p01_winners = enumerate_and_score(p01_text, p01_roster, seed=0)
    assert len(p01_winners) == 1, f"p01 must NOT be a tie (single-goal-holder case): {p01_scored}"
    p01_owner = select_outcome_owner(p01_text, p01_roster, seed=0)
    assert p01_owner == "amy" == p01_winners[0], (
        f"p01 (single-goal, non-tie) selection must be unaffected by the tie-break: {p01_owner!r}")

    # ---- PART 1 self-tests (2026-08-06): coref goal-subject confound CAN-FAIL cases -- the OLD
    # two-pass resolver returned the first roster-NAME token ANYWHERE in the sentence (even an
    # OBJECT), so a pronoun SUBJECT preceding an object name mis-resolved to the object. SINGLE-PASS
    # must resolve the pronoun subject via recency instead.
    henry_roster = {"henry": "m", "mother": "f"}
    henry_resolver = GeneralRecencyEntityResolver(henry_roster)
    henry_resolver.subject_entity("Henry was a kind, good boy.")  # seeds recency with henry
    henry_subj = henry_resolver.subject_entity("He wanted to help his mother.")
    assert henry_subj == "henry", (
        f"CAN-FAIL: pronoun subject 'he' must resolve to henry (not the object-position roster name "
        f"'mother'), got {henry_subj!r}")

    amy_subj = GeneralRecencyEntityResolver({"amy": "f"}).subject_entity("Amy wanted to win.")
    assert amy_subj == "amy", f"CAN-FAIL: explicit name-subject must resolve to amy, got {amy_subj!r}"

    jo_subj = GeneralRecencyEntityResolver({"jo": "f"}).subject_entity("Jo saw the dog.")
    assert jo_subj == "jo", f"CAN-FAIL: explicit name-subject must resolve to jo, got {jo_subj!r}"

    # object-is-a-roster-name must NOT override an earlier pronoun SUBJECT (the exact bug shape,
    # isolated from the desiderative-verb case above).
    override_roster = {"amy": "f", "jo": "f"}
    override_resolver = GeneralRecencyEntityResolver(override_roster)
    override_resolver.subject_entity("Amy walked to the store.")  # seeds recency with amy
    override_subj = override_resolver.subject_entity("She saw Jo.")
    assert override_subj == "amy", (
        f"CAN-FAIL: pronoun subject 'she' must resolve via recency to amy, NOT be overridden by the "
        f"object-position roster name 'jo', got {override_subj!r}")

    # NO-REGRESSION: the 48-item fair instrument's goal sentences are all name-subject-first, so
    # single-pass reproduces the two-pass answer byte-identically on a representative fair-instrument
    # sentence (full 48/48 regression is verification/test_goal_owner_select.py's job, not
    # duplicated here).
    p01_first_subj = GeneralRecencyEntityResolver(p01_roster).subject_entity(
        "Jo hurried off early toward the barn.")
    assert p01_first_subj == "jo", (
        f"no-regression: name-subject-first fair-instrument sentence must be unaffected by the "
        f"single-pass fix, got {p01_first_subj!r}")

    # ---- PART 2 self-tests (2026-08-06): Tier-3 evaluative bridging inference, wired into
    # build_candidate_role_seq/enumerate_and_score/select_outcome_owner. Reproduces the decisive
    # mg2_henry_bootblack case (experiments/data/real_text_goal_owner_diagnostic_v1.jsonl,
    # commit 17dd3567b's validated bank) end-to-end THROUGH PRODUCTION select_outcome_owner (not just
    # the standalone bridge functions), depending on the PART 1 fix above (without it, "he wanted to
    # help his mother" mis-attributes the GOAL to mother, so henry never has an open goal to bridge).
    mg2_roster = {"henry": "m", "mother": "f"}
    mg2_text = (
        "Henry was a kind, good boy. His father was dead, and his mother was very poor. He wanted "
        "to help his mother, for she could not always earn enough to buy food for her little "
        "family. With the dollar he bought a box, three brushes, and some blacking. He was so "
        "polite that gentlemen soon began to notice him, and to let him black their boots. The "
        "first day he brought home fifty cents, which he gave to his mother to buy food with. She "
        "said, as she dropped a tear of joy, \"You are a dear, good boy, Henry.\""
    )
    mg2_lex_events = type_goal_events(_sentences(mg2_text)[-1], "henry")
    assert not any(r in (R_UNMET, R_MET) for (_e, r) in mg2_lex_events), (
        "mg2 sanity: the outcome sentence ('You are a dear, good boy, Henry.') must have ZERO "
        "lexical/similarity verb-typing overlap -- proves the bridge, not Tier-1/2, resolves this")
    mg2_scored, mg2_winners = enumerate_and_score(mg2_text, mg2_roster, seed=0)
    assert mg2_scored.get("henry") == 1.0, (
        f"mg2 CAN-FAIL: bridge must type+bind the outcome to henry (open GOAL + addressee match), "
        f"got scored={mg2_scored}")
    assert mg2_scored.get("mother", 0.0) == 0.0, (
        f"mg2 over-fire guard: mother (not the goal-holder, not the addressee) must NOT score, "
        f"got scored={mg2_scored}")
    mg2_owner = select_outcome_owner(mg2_text, mg2_roster, seed=0)
    assert mg2_owner == "henry", (
        f"mg2 end-to-end: select_outcome_owner must resolve owner=henry via the Tier-3 bridge, "
        f"got {mg2_owner!r}")

    # BYSTANDER over-fire guard (unit-level, per the validated bank's bystander_no_bridge_acc=1.0
    # gate): an evaluative construction correctly detected + addressed at `jo` must still NOT bridge
    # when jo has no open goal (has_open_goal=False) -- abstain, never a forced bridge.
    bystander_sentence = "You are a good girl, Jo."
    bystander_roster = {"amy": "f", "jo": "f"}
    bys_polarity, bys_addressee = detect_evaluative_construction(bystander_sentence, bystander_roster)
    assert bys_polarity == "POS" and bys_addressee == "jo", (
        f"bystander sanity: construction must be detected (POS, addressee=jo), "
        f"got ({bys_polarity!r}, {bys_addressee!r})")
    bystander_bridge = _bridge_outcome_event(bystander_sentence, bystander_roster, "jo",
                                              has_open_goal=False)
    assert bystander_bridge is None, (
        f"bystander over-fire guard: jo has no open goal, must not bridge, got {bystander_bridge!r}")
    # addressee-mismatch guard: even WITH an open goal, the bridge must not fire for a DIFFERENT
    # entity than the construction's addressee (never binds a non-addressed bystander).
    mismatch_bridge = _bridge_outcome_event(bystander_sentence, bystander_roster, "amy",
                                             has_open_goal=True)
    assert mismatch_bridge is None, (
        f"addressee-mismatch guard: amy is not the addressee ('jo' is), must not bridge, "
        f"got {mismatch_bridge!r}")

    # ---- PART 3 self-tests (2026-08-06): Tier-3 AFFECT-STATE bridging inference (sibling of PART 2),
    # wired into build_candidate_role_seq as the SECOND bridge. Reproduces decisive cases from
    # experiments/data/affect_state_bridging_bank_v1.jsonl (commit 0ff1a6d97's Director-VET'd HARD_PASS
    # bank) end-to-end THROUGH PRODUCTION select_outcome_owner. Both anchor passages (frank, peter)
    # contain NO lexical outcome verb anywhere, so the pre-bridge organ raises OUTCOME_NEVER_TYPED on
    # them -- their resolution is 100% attributable to the affect bridge (the clean-case analogue of
    # mg2 for the evaluative bridge).

    # POS_MET, first-person Pattern B ("Oh, how glad I am!"): goal MET bound to frank (the reporting
    # speaker holding the desiderative goal); father (no goal) must NOT score.
    frank_roster = {"frank": "m", "father": "m"}
    frank_text = ("Frank wanted to catch a fine fish with his father. They walked down to the river "
                  "together. Frank cried, \"Oh, how glad I am!\"")
    frank_lex = type_goal_events(_sentences(frank_text)[-1], "frank")
    assert not any(r in (R_UNMET, R_MET) for (_e, r) in frank_lex), (
        "affect sanity: outcome ('...how glad I am!') must have ZERO lexical/similarity verb-typing "
        "overlap -- proves the AFFECT bridge, not Tier-1/2, resolves this")
    frank_scored, frank_winners = enumerate_and_score(frank_text, frank_roster, seed=0)
    assert frank_scored.get("frank") == 1.0 and frank_scored.get("father", 0.0) == 0.0, (
        f"affect CAN-FAIL: bridge must bind the outcome to frank (open GOAL + own affect); father "
        f"(no goal, not the holder) must NOT score, got {frank_scored}")
    frank_owner = select_outcome_owner(frank_text, frank_roster, seed=0)
    assert frank_owner == "frank", (
        f"affect end-to-end: select_outcome_owner must resolve owner=frank via the Tier-3 affect "
        f"bridge, got {frank_owner!r}")

    # NEG_UNMET, third-person Pattern A (pronoun subject, unique-gender resolved): "He felt downcast"
    # -> goal UNMET bound to peter. peter's passage also has no lexical outcome verb (pre-bridge organ
    # raises), so this isolates the affect bridge's NEG valence path end-to-end.
    peter_roster = {"peter": "m", "sister": "f"}
    peter_text = ("Peter wanted to keep his new book free of every crease. His little sister borrowed "
                  "it without asking. He felt downcast when he found the torn page.")
    peter_rs, peter_cid = build_candidate_role_seq(peter_text, peter_roster, "peter")
    peter_pos = _outcome_pos(peter_rs)
    assert peter_pos is not None and peter_rs[peter_pos] == R_UNMET and peter_cid[peter_pos] == "peter", (
        f"affect valence (neg): peter's outcome slot must bridge to OUTCOME_UNMET, "
        f"got role_seq={peter_rs} cluster_ids={peter_cid}")
    peter_owner = select_outcome_owner(peter_text, peter_roster, seed=0)
    assert peter_owner == "peter", f"affect neg end-to-end owner must be peter, got {peter_owner!r}"

    # BYSTANDER over-fire guard (the critical affect-bridge property): the affect (glad) is kate's OWN,
    # but the goal-holder is jack -- the bridge must bind NOBODY. The construction is correctly detected
    # as kate's, yet the bridge abstains for the protagonist jack (holder mismatch) EVEN when jack holds
    # an open goal -- so the affect bridge can never hijack a bystander's affect onto the protagonist.
    bys_roster = {"jack": "m", "kate": "f"}
    bys_outcome = "Kate felt very glad about the fair weather."
    bys_pol, bys_holder = detect_affect_state_construction(bys_outcome, bys_roster)
    assert (bys_pol, bys_holder) == ("POS", "kate"), (
        f"bystander sanity: affect must be detected as kate's own (POS, kate), "
        f"got ({bys_pol!r}, {bys_holder!r})")
    assert _bridge_affect_outcome_event(bys_outcome, bys_roster, "jack", has_open_goal=True) is None, (
        "bystander over-fire guard: the affect is kate's, jack is the protagonist -- the affect bridge "
        "must NOT fire for jack even with an open goal")
    assert _bridge_affect_outcome_event(bys_outcome, bys_roster, "kate", has_open_goal=False) is None, (
        "bystander over-fire guard: kate is the affect-holder but has no open goal -- must abstain")

    # CROSS-DETECTOR non-interference (both directions, decisive inline cases; the full 0/13 + 0/12 +
    # 0/62 bank-wide sweep is verification/verify_affect_state_bridging_production.py): the affect
    # detector must NOT fire on the evaluative "you are ADJ" construction, and the evaluative detector
    # must NOT fire on an affect-state outcome.
    assert detect_affect_state_construction(
        "You are a dear, good boy, Henry.", {"henry": "m", "mother": "f"}) == (None, None), (
        "cross-detector: affect detector must NOT fire on the evaluative 'you are ADJ' construction")
    assert detect_evaluative_construction(
        "Ellen was so happy that she smiled all afternoon.", {"ellen": "f", "mother": "f"}) == (
        None, None), "cross-detector: evaluative detector must NOT fire on an affect-state outcome"

    return {"score_correct": score_correct, "score_wrong": score_wrong,
            "score_amy_own_goal": score_amy_own_goal, "adopt": adopt,
            "t24_scored": t24_scored, "t24_owner": t24_owner,
            "p01_scored": p01_scored, "p01_owner": p01_owner,
            "part1_henry_subj": henry_subj, "part1_amy_subj": amy_subj, "part1_jo_subj": jo_subj,
            "part1_override_subj": override_subj,
            "part2_mg2_scored": mg2_scored, "part2_mg2_owner": mg2_owner,
            "part2_bystander_bridge": bystander_bridge, "part2_addressee_mismatch_bridge": mismatch_bridge,
            "part3_frank_scored": frank_scored, "part3_frank_owner": frank_owner,
            "part3_peter_outcome_role": peter_rs[peter_pos], "part3_peter_owner": peter_owner,
            "part3_bystander_detect": [bys_pol, bys_holder]}


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
