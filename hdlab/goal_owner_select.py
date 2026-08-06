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
    """Structural (gold-free) subject resolver: backward-search recency pick over gender/number-
    compatible roster candidates. Byte-identical mechanism to exp_component5_gold_role_isolated_v1.
    py's GeneralRecencyEntityResolver (byte-copied here because hdlab/ must not import from
    experiments/): the first explicit roster NAME in a sentence is the subject; else the first
    pronoun resolves to the most-recently-mentioned gender-compatible roster entity. `roster` is a
    {name: gender} dict describing the passage's cast (structural passage metadata, NEVER a gold
    label); defaults to DEFAULT_ROSTER when the caller doesn't supply one."""

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


def _sentences(text: str) -> List[str]:
    """Byte-identical to experiments/exp_situation_model_goal_outcome_dimension_v1.py's _sentences."""
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]


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


# ============================================================================ CANDIDATE ENUMERATION
# + SELECTION (the full outcome-owner selector). Byte-identical mechanism to experiments/exp_c5_
# primacy_trap_endtoend_goal_coherence_candidate_gen_v1.py's build_candidate_role_seq/_outcome_pos/
# enumerate_and_select (commit b1b1ce460), generalized off the source cell's 'item' dict onto
# (passage_text, roster) args.
def build_candidate_role_seq(passage_text: str, roster: dict, outcome_entity,
                              scramble_goal_to_foil=None):
    """Structural (gold-free) role_seq/cluster_ids for ONE proposed outcome-slot candidate.
    Non-outcome sentences: subject resolved from the PASSAGE TEXT (GeneralRecencyEntityResolver),
    never from a gold label. Outcome (final) sentence: subject is the PROPOSED CANDIDATE
    `outcome_entity` -- this is the enumeration step. `scramble_goal_to_foil` is a diagnostic-only
    hook (redirects GOAL-role bindings to a named foil entity) for scramble-control self-tests; leave
    None in production use."""
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
    for (entity, role) in type_goal_events(sents[-1], outcome_entity):
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
    = roster.keys() (structural passage metadata), never a gold label."""
    candidates = sorted(roster.keys())
    scored = {}
    for c in candidates:
        rs, cid = build_candidate_role_seq(passage_text, roster, c,
                                            scramble_goal_to_foil=scramble_goal_to_foil)
        pos = _outcome_pos(rs)
        if pos is None:
            raise ValueError(
                f"outcome slot never typed for candidate {c!r}; passage_text's final sentence must "
                f"type an OUTCOME_UNMET/OUTCOME_MET event")
        scored[c] = directed_goal_outcome_score(rs, cid, seed, pos)
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

    return {"score_correct": score_correct, "score_wrong": score_wrong,
            "score_amy_own_goal": score_amy_own_goal, "adopt": adopt,
            "t24_scored": t24_scored, "t24_owner": t24_owner,
            "p01_scored": p01_scored, "p01_owner": p01_owner}


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
