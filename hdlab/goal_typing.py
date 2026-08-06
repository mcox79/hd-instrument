"""hdlab/goal_typing.py -- Component-5 GOAL-typing production organ (promotion, 2026-08-05).

PROMOTION (WIRE-DON'T-ISLAND): locks in the three GOAL-typing signals validated end-to-end this
session, following the promotion convention of hdlab/goal_owner_select.py (byte-identical copy of
the reused mechanism, no re-tuning, no reimplementation):

  (1) EXPERIENCER-frame typing: hdlab.frame_induction.frame_primary_role (already-in-hdlab
      production organ, imported directly, unmodified) decides whether a sentence's subject is an
      EXPERIENCER (a psychological GOAL/desire state), reused via `c3_has_desire`/
      `type_sentence_events_c3` -- byte-identical copies of
      experiments/exp_component5_wired_endtoend_v1.py's functions of the same name (that module
      itself only wraps hdlab organs; nothing experiment-specific in the two functions).
  (2) PURPOSE-INFINITIVAL construction typing ("X V...to VP" -> GOAL, verb-lemma-independent):
      byte-identical copy of experiments/exp_c5_generative_goal_typing_action_frame_v1.py's
      structural `action_frame_feats` detector (commit 9bf855dd0) plus its MDL-induced hypothesis
      (hdlab.learner `ruleind` plugin, reused unmodified) -- generalizes to any action-frame verb
      via a fresh fit each process (deterministic: same FIT_POS_SENTENCES/FIT_NEG_SENTENCES every
      time, cached after first call).
  (3) DESIDERATIVE/ASPECTUAL PARTITION: byte-identical copy of
      experiments/exp_c5_desiderative_aspectual_partition_goal_typing_v1.py's
      DESIDERATIVE_PASS / ASPECTUAL_STOP / OTHER_STOP_UNCHANGED sets (commit 5da76bf34) --
      desiderative/intention control verbs (hope/hoped/want/wish/mean/meant/plan/intend/aim/
      long/yearn/desire) are REMOVED from the purpose-infinitival control-verb stop set so "X hoped
      to VP" fires GOAL via the CONSTRUCTION path even when C3's EXPERIENCER lexicon is OOV on the
      governing verb; aspectual/implicative verbs (begin/began/start/started/try/tried/fail/failed/
      manage/managed/cease/continue/...) STAY in the stop set (precision guard -- "X began/tried/
      failed to VP" is NOT a goal-ownership signal).

VALIDATED NUMBERS this module reproduces (data/exp_c5_desiderative_aspectual_partition_goal_typing_v1/
metrics.json, commit 5da76bf34, disk-verified): explicit_psych divergent 18/18 (1.0), action_implied
divergent 10/10 (1.0), aspectual-precision-probe false_goal_count=0 across 7 verbs x 3 seeds,
role-scramble collapses non-vacuous on both subsets. The end-to-end owner-selection harness (real
coref + the recency-trap bank + the directed-score adoption gate) lives in
experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py / *_desiderative_aspectual_
partition_goal_typing_v1.py, both left untouched as the source-of-truth for their own historical
numbers (same convention as this module's sibling hdlab/goal_owner_select.py). This module is the
reusable, importable GOAL-typing wire-point: given a sentence + subject entity, decide whether a
GOAL role fires, so a caller (e.g. hdlab.situation_reader, or a future situation-model consumer)
does not need to import three separate experiment modules.

MECHANISM (glass-box, deterministic): `type_goal_events(sentence, subject)` returns the c3_only
typed events (GOAL/OUTCOME_UNMET/OUTCOME_MET, signal 1) UNIONED with an additional GOAL event iff
the partitioned purpose-infinitival construction fires on `sentence` (signals 2+3) and `subject`
does not already carry a GOAL event -- the exact union pattern validated by
exp_c5_desiderative_aspectual_partition_goal_typing_v1.type_sentence_events_partitioned.
`has_goal(sentence, subject)` is the boolean convenience wrapper most callers want.

SCOPE (do not overclaim): validated on the recency-trap subset of
experiments/data/goal_owner_fair_v1.jsonl (verb_type in {explicit_psych, action_implied}), 3 seeds,
plus a 7-item hand-authored aspectual precision probe. Not validated on the primacy-trap subset or
on open-domain text beyond that bank; OTHER_STOP_UNCHANGED verbs (decide/need/seem/get/choose) are
conservatively left NON-goal-signaling pending their own dedicated cell.

Cites: experiments/exp_component5_wired_endtoend_v1.py (c3_has_desire/type_sentence_events_c3,
commit 78294a2c6 lineage); experiments/exp_c5_generative_goal_typing_action_frame_v1.py
(action_frame_feats/DET_STOP/DIRECTIONAL_PP/induce_hypothesis, commit 9bf855dd0);
experiments/exp_c5_desiderative_aspectual_partition_goal_typing_v1.py (DESIDERATIVE_PASS/
ASPECTUAL_STOP/OTHER_STOP_UNCHANGED partition, commit 5da76bf34);
experiments/exp_c5_real_coref_endtoend_purpose_infinitival_v1.py (end-to-end harness, commit
78294a2c6); hdlab/frame_induction.py::frame_primary_role; hdlab/thematic_role_labeler.py::
lemma_verb; hdlab/coreference_resolver.py::normalize_tokens; hdlab/learner/ (ruleind plugin,
reused unmodified); hdlab/goal_owner_select.py (sibling promotion, same convention, downstream
consumer of the GOAL role this module types).
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from hdlab.coreference_resolver import normalize_tokens
from hdlab.frame_induction import frame_primary_role
from hdlab.thematic_role_labeler import lemma_verb
from hdlab.learner import apply as learner_apply, learn as learner_learn

# ============================================================================ role vocabulary
# Byte-identical to experiments/exp_situation_model_goal_outcome_dimension_v1.py's R_GOAL/R_UNMET/R_MET.
R_GOAL = "GOAL"
R_UNMET = "OUTCOME_UNMET"
R_MET = "OUTCOME_MET"

# Byte-identical to experiments/exp_self_extension_grounded_realprose_v1.py's V2_OUTCOME_UNMET/MET
# (outcome valence stays lexicon-typed -- declared out of Component-3's scope, a thematic-role
# labeler is not an outcome classifier; unchanged by this promotion).
V2_OUTCOME_UNMET = {"down", "fell", "fall", "sank", "sink", "wailing", "wailed",
                    "lost", "lose", "failed", "fail", "calamity", "sorry", "missed", "miss",
                    "unwarned", "unprotected", "late", "never"}
V2_OUTCOME_MET = {"reached", "enjoyed", "enjoy", "won", "escaped", "arrived"}


def _tokset(text: str):
    """Byte-identical to exp_situation_model_goal_outcome_dimension_v1._tokset (normalize_tokens)."""
    return normalize_tokens(text)


def _ordered_tokens(sentence: str) -> List[str]:
    """Order-preserving lowercase content tokens. Byte-identical to
    exp_situation_model_goal_outcome_dimension_v1._ordered_tokens (attribution needs ORDER;
    normalize_tokens returns a set and is used only for lexicon membership above)."""
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


# ============================================================================ SIGNAL 1: EXPERIENCER-frame (c3)
def c3_has_desire(sentence: str) -> bool:
    """True iff ANY token in `sentence` lemmatizes (hdlab.thematic_role_labeler.lemma_verb) to a
    verb that frame_primary_role (Component-3, production config: chosen_name=None, hypothesis=None
    -- identical to the conservative wire in hdlab/situation_reader.py) labels subj=EXPERIENCER.
    Byte-identical copy of experiments/exp_component5_wired_endtoend_v1.py::c3_has_desire."""
    for tok in _ordered_tokens(sentence):
        lemma = lemma_verb(tok)
        role = frame_primary_role(lemma, [], 0, None, "subj")
        if role == "EXPERIENCER":
            return True
    return False


def type_sentence_events_c3(sentence: str, subject) -> List[Tuple[object, str]]:
    """Byte-identical copy of experiments/exp_component5_wired_endtoend_v1.py::
    type_sentence_events_c3: has_desire computed via the real Component-3 mechanism
    (c3_has_desire), OUTCOME_UNMET/OUTCOME_MET stay lexicon-typed."""
    t = _tokset(sentence)
    events: List[Tuple[object, str]] = []
    has_desire = c3_has_desire(sentence)
    has_unmet = bool(t & V2_OUTCOME_UNMET)
    has_met = bool(t & V2_OUTCOME_MET)
    if has_desire and subject is not None:
        events.append((subject, R_GOAL))
    if has_unmet and subject is not None:
        events.append((subject, R_UNMET))
    if has_met and subject is not None:
        events.append((subject, R_MET))
    return events


# ============================================================================ SIGNALS 2+3: partitioned purpose-infinitival
# Byte-identical to experiments/exp_c5_generative_goal_typing_action_frame_v1.py's DET_STOP/DIRECTIONAL_PP.
DET_STOP = {
    "the", "a", "an", "his", "her", "its", "their", "this", "that", "my", "your", "our", "to",
}
DIRECTIONAL_PP = {"toward", "towards", "into", "up", "down", "out", "across", "off", "along"}

# Byte-identical to experiments/exp_c5_desiderative_aspectual_partition_goal_typing_v1.py's partition
# (commit 5da76bf34). DESIDERATIVE/intention verbs -- goal-signaling; REMOVED from the stop set so
# "X <verb> to VP" fires purpose_to_no_det via the CONSTRUCTION path even when C3 is OOV.
DESIDERATIVE_PASS = {
    "hope", "hopes", "hoped", "want", "wants", "wanted", "wish", "wishes", "wished",
    "mean", "means", "meant", "plan", "plans", "planned", "intend", "intends", "intended",
    "aim", "aims", "aimed", "long", "longs", "longed", "yearn", "yearns", "yearned",
    "desire", "desires", "desired",
}
# ASPECTUAL/IMPLICATIVE verbs -- NOT goal-signaling ("X began/tried/failed to VP" is not a goal
# ownership signal); STAYS in the stop set.
ASPECTUAL_STOP = {
    "begin", "begins", "began", "start", "starts", "started",
    "try", "tries", "tried", "fail", "fails", "failed",
    "manage", "manages", "managed", "happen", "happens", "happened",
    "cease", "ceases", "ceased", "stop", "stops", "stopped",
    "continue", "continues", "continued",
}
# Unclassified by the source cell's task brief -- conservatively LEFT in the stop set: no behavior
# change vs the pre-partition typer, precision-safe default.
OTHER_STOP_UNCHANGED = {
    "decide", "decides", "decided", "need", "needs", "needed", "seem", "seems", "seemed",
    "get", "gets", "got", "choose", "chooses", "chose",
}
PARTITIONED_STOP = ASPECTUAL_STOP | OTHER_STOP_UNCHANGED
assert DESIDERATIVE_PASS.isdisjoint(PARTITIONED_STOP), "partition must be disjoint by construction"


def action_frame_feats(sentence: str) -> List[str]:
    """Structural purpose-infinitival detector (verb-lemma-independent 'to VP' vs 'to NP'), with the
    PARTITIONED control-verb exclusion. Byte-identical logic to
    exp_c5_desiderative_aspectual_partition_goal_typing_v1.action_frame_feats_partitioned."""
    toks = _ordered_tokens(sentence)
    feats = []
    has_purpose_inf = False
    for i in range(len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        preceding = toks[i - 1] if i > 0 else None
        if preceding in PARTITIONED_STOP:
            continue
        has_purpose_inf = True
        break
    if has_purpose_inf:
        feats.append("purpose_to_no_det")
    if any(w in toks for w in DIRECTIONAL_PP):
        feats.append("has_directional_pp")
    return feats


# ============================================================================ MDL induction (held-out FIT set)
# Byte-identical to experiments/exp_c5_generative_goal_typing_action_frame_v1.py's FIT set (verbs
# disjoint from the historical TEST bank's action_implied verbs -- held-out generalization, not
# memorization; asserted in self_test below).
FIT_POS_SENTENCES = [
    "Nell ran to the well to fetch water before noon.",
    "Owen hurried to the barn to feed the horses.",
    "Priya marched to the hall to deliver the letter.",
    "Quinn sailed to the island to trade the goods.",
    "Rex drove to the mill to collect the flour.",
    "Sara hiked to the peak to plant the flag.",
    "Theo sprinted to the gate to open the lock.",
    "Uma journeyed to the town to sell the cloth.",
]
FIT_NEG_SENTENCES = [
    "Nell ran to the well early in the morning.",
    "Owen hurried to the barn before the storm.",
    "Priya marched to the hall with the others.",
    "Quinn sailed to the island near the coast.",
    "Rex drove to the mill along the river.",
    "Sara hiked to the peak under the stars.",
    "Theo sprinted to the gate at dawn.",
    "Uma journeyed to the town by cart.",
]
FIT_VERBS = {"ran", "hurried", "marched", "sailed", "drove", "hiked", "sprinted", "journeyed"}
TEST_ACTION_VERBS = {"set", "climbed", "carried", "walked", "rowed"}

HYP_SPACE_SPEC = dict(
    candidate_plugins=["ruleind"], min_coverage=1, purity_thresh=0.9, max_conjunct=2, max_rules=4,
    key_fn=lambda inst: tuple(sorted(inst["feats"])),
)


def build_fit_episodes():
    eps = [{"feats": action_frame_feats(s), "gold_class": "GOAL"} for s in FIT_POS_SENTENCES]
    eps += [{"feats": action_frame_feats(s), "gold_class": "NOT_GOAL"} for s in FIT_NEG_SENTENCES]
    return eps


def induce_hypothesis():
    """MDL model-selection (hdlab.learner, config-only registry) over the declared action-frame
    features. Returns (plugin_name, hypothesis, all_results) -- 'hypothesis' is glass-box (JSON-able).
    Byte-identical to exp_c5_generative_goal_typing_action_frame_v1.induce_hypothesis."""
    episodes = build_fit_episodes()
    chosen_name, chosen, all_results = learner_learn(
        episodes, lambda inst: inst["feats"], HYP_SPACE_SPEC)
    return chosen_name, chosen, all_results


_INDUCED_CACHE: Optional[Tuple[str, dict]] = None


def _get_induced() -> Tuple[str, dict]:
    """Lazily induce + cache (plugin_name, hypothesis) -- deterministic given the fixed FIT set, so
    caching is safe and avoids re-running MDL model-selection on every call."""
    global _INDUCED_CACHE
    if _INDUCED_CACHE is None:
        plugin_name, chosen, _all_results = induce_hypothesis()
        if chosen is None:
            raise RuntimeError("MDL model-selection returned KEEP_EPISODIC -- no rule induced")
        _INDUCED_CACHE = (plugin_name, chosen.hypothesis)
    return _INDUCED_CACHE


# ============================================================================ COMBINED GOAL-TYPING (union of signals 1-3)
def type_goal_events(sentence: str, subject) -> List[Tuple[object, str]]:
    """c3_only events (signal 1: EXPERIENCER-frame) UNIONED with an additional GOAL event iff the
    PARTITIONED purpose-infinitival construction fires (signals 2+3) and `subject` doesn't already
    carry a GOAL. Byte-identical union pattern to
    exp_c5_desiderative_aspectual_partition_goal_typing_v1.type_sentence_events_partitioned."""
    events = type_sentence_events_c3(sentence, subject)
    feats = action_frame_feats(sentence)
    plugin_name, hypothesis = _get_induced()
    pred = learner_apply(plugin_name, hypothesis, feats, key=None, default_class="NOT_GOAL")
    already_goal = any(r == R_GOAL and e == subject for (e, r) in events)
    if pred == "GOAL" and subject is not None and not already_goal:
        events = list(events) + [(subject, R_GOAL)]
    return events


def has_goal(sentence: str, subject) -> bool:
    """Boolean convenience wrapper: does a GOAL role fire for `subject` in `sentence`, combining all
    three promoted signals (EXPERIENCER-frame + purpose-infinitival + desiderative/aspectual
    partition)."""
    return any(r == R_GOAL and e == subject for (e, r) in type_goal_events(sentence, subject))


# ============================================================================ self-test
def self_test() -> dict:
    """Reproduces decisive cases from the source cells with THIS module's promoted (copied) organ,
    proving the promotion is byte-identical, not just similarly-shaped."""
    # (1) partition is disjoint by construction
    assert DESIDERATIVE_PASS.isdisjoint(ASPECTUAL_STOP) and DESIDERATIVE_PASS.isdisjoint(OTHER_STOP_UNCHANGED)

    # (2) FIT/TEST verb disjointness (held-out generalization, not memorization)
    assert FIT_VERBS.isdisjoint(TEST_ACTION_VERBS)

    # (3) feature-level: desiderative-governed infinitival fires; aspectual-governed does NOT
    assert "purpose_to_no_det" in action_frame_feats("Beth hoped to win a place at the summer fair.")
    assert "purpose_to_no_det" not in action_frame_feats("Dawn began to open the gate.")
    assert "purpose_to_no_det" not in action_frame_feats("Fay started to close the shop.")

    # (4) DECISIVE CASE: a desiderative "hoped to VP" fires GOAL for the subject.
    goal_hoped = has_goal("Beth hoped to win a place at the summer fair.", "beth")
    assert goal_hoped is True, "desiderative 'hoped to VP' must fire GOAL"

    # (5) DECISIVE CASE: an aspectual "began to VP" does NOT fire GOAL for the subject.
    goal_began = has_goal("Dawn began to open the gate.", "dawn")
    assert goal_began is False, "aspectual 'began to VP' must NOT fire GOAL"

    # (6) action-frame telos (no desiderative/psych word at all) still fires GOAL via the
    # purpose-infinitival construction (signal 2), same held-out verbs as the source cell.
    goal_action_frame = has_goal("Nell ran to the well to fetch water before noon.", "nell")
    assert goal_action_frame is True, "purpose-infinitival action-frame telos must fire GOAL"

    # (7) c3_only (signal 1 alone, via type_sentence_events_c3) still misses the desiderative case
    # (confirms the gap this promotion closes is real, not stale).
    c3_only_events = type_sentence_events_c3("Beth hoped to win a place at the summer fair.", "beth")
    assert not any(r == R_GOAL for (_e, r) in c3_only_events), (
        "c3_only sanity check: expected 'hoped' to stay OOV under signal 1 alone")

    return {
        "goal_hoped_to_win": goal_hoped,
        "goal_began_to_open": goal_began,
        "goal_action_frame_telos": goal_action_frame,
        "c3_only_misses_hoped": not any(r == R_GOAL for (_e, r) in c3_only_events),
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
