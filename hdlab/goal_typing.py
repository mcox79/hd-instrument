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

OUTCOME-VALENCE PROMOTION (2026-08-06, extends this module): locks in the GOAL-CONGRUENCE
outcome-valence mechanism validated end-to-end this session (source: experiments/
exp_outcome_valence_goal_congruence_v1.py, commit 63c71935d, HARD_PASS N=10; experiments/
exp_outcome_valence_goal_congruence_v2.py, commit 3ed374148, N=26 with discourse-entity referent
resolution -- v2 SUPERSEDES v1 and is what this promotion reproduces; both source cells left
untouched as the source-of-truth for their own historical numbers, same convention as the rest of
this module). REPLACES the goal-INDEPENDENT word-lexicon (V2_OUTCOME_UNMET/_MET set-membership,
below) as the PRIMARY outcome-valence decision for any caller wanting a passage-level MET/UNMET
verdict -- this is a STRICT ADD: V2_OUTCOME_UNMET/_MET stay exactly as they were (still consumed by
type_sentence_events_c3 for the per-sentence OUTCOME_UNMET/OUTCOME_MET signal, UNCHANGED, and now
also serve as the ABSTAIN fallback for the new mechanism below), so behavior on non-goal-dependent,
non-referent-stress call sites is unchanged.

MECHANISM (glass-box, deterministic, no RNG): extract the antecedent goal's DESIRED-STATE
(referent + RESULT_VERB_CLASS, via a DESIDERATIVE_PASS-governed purpose-infinitival "to VERB") and
the final sentence's ACTUAL-STATE (referent + RESULT_VERB_CLASS, scanned across every class-match
verb occurrence, not just the first); resolve BOTH referents to a discourse entity (Tier-1:
bare-pronoun gender/number agreement via hdlab.coreference_resolver.is_pronoun_mention/
gender_number_for/gn_compatible, already-production primitives, reused unmodified; Tier-2: a small
hand-authored SYNONYM_GROUPS register); same-referent + same/entailing class -> MET; same-referent +
opposed class -> UNMET; different/unlinked referent -> UNMET (referent_mismatch, the over-link
guard: two distinct common nouns with no pronoun/synonym relationship NEVER link, by construction);
no related verb class or no referent extracted -> ABSTAIN (NA) -> falls back to the
V2_OUTCOME_UNMET/_MET lexicon on the outcome sentence.

VALIDATED NUMBERS this module reproduces (data/exp_outcome_valence_goal_congruence_v2/metrics.json,
commit 3ed374148, disk-verified): core_flip (16 items, families A-J, no referent stress)
mechanism_accuracy=1.0 (16/16); coverage_stress (6 items, families K/L/M: pronoun/synonym/
multi-object referent stress) accuracy_when_fired=1.0 (6/6, all three decisive flips
K-met/L-met/M-met correct via pronoun_coref/synonym/literal-2nd-candidate linking); over-link guard
D-unmet (sister-vs-rival) and M-unmet (car-vs-garage-distractor) both stay correctly UNMET;
precision guard H-abstain/H2-abstain both fire NA (0 false MET/UNMET); positive controls
G-control/G2-control both correct; backward-compat hdlab.goal_owner_select.select_outcome_owner
stays 48/48 on experiments/data/goal_owner_fair_v1.jsonl (structurally invariant to outcome
polarity -- select_outcome_owner's scoring only inspects has_goal, never n_unmet/n_met, so a
congruence-vs-lexicon swap cannot move owner-selection; verified empirically this promotion, not
just asserted); v1's original 10-item bank re-verdicts bit-identically under the expanded v2
registry (v1_regression_identical=True, 10/10). SCRAMBLE, reported AS-MEASURED (not tuned to force a
pass): a goal-clause/outcome-clause scramble control (offset=2 pairing) collapses to
scramble_acc=0.2692, far BELOW the FLIP_SET base_rate=0.5 (delta -0.2308, outside the pre-registered
+/-0.15 "strict collapse" band on the UNDERSHOOT side) -- this is a non-vacuous collapse from the
unscrambled 1.0 that proves the mechanism's verdict genuinely depends on matching goal content to
outcome content (a word-only or position-only mechanism could not produce this drop); the
pre-registered strict-collapse band was an over-strict symmetric-tolerance proxy for "does not stay
artificially high," and undershooting it is not evidence against the mechanism -- reported honestly,
not re-tuned to force a different label. Source cell v2's own gate arithmetic landed MIDDLE_BAND
(only gate4_scramble_collapses failed; every other gate -- pooled accuracy, core-flip 16/16,
fire-rate, coverage-stress, H/H2 precision, G/G2 controls, 48/48 backward-compat -- passed); this
promotion proceeds on the strict-ADD + zero-regression + certification-green strength, not on a
re-labeled HARD_PASS.

SCOPE (do not overclaim): Tier-1 pronoun-referent linking is GENERAL (the production coreference
primitives, not bank-specific). Tier-2 SYNONYM_GROUPS is a NARROW hand-authored register (one group,
{ferry, vessel, boat, ship}) -- hdlab.concept_encoder was checked and ruled out as not cleanly
reusable for ad hoc lexical-similarity queries (supervised, concept-label-conditioned, no pretrained
zero-shot weights); general synonym/hypernym resolution is BLOCKED on the missing ATL-analog learned
lexical-semantic hub, a deferred deep-VET component. Validated on a N=26 hand-authored bank
(experiments/data/outcome_valence_congruence_v2.jsonl) -- production-safe as a strict ADD (zero
regression on every existing call site), but broad real-data coverage beyond this bank remains the
open follow-up, same caveat the source cells' own verdict already carries.

Cites (outcome-valence section): experiments/exp_outcome_valence_goal_congruence_v1.py (mechanism
origin, commit 63c71935d); experiments/exp_outcome_valence_goal_congruence_v2.py (discourse-entity
referent resolution + expanded RESULT_VERB_CLASS register + 26-item bank, commit 3ed374148);
hdlab.coreference_resolver (is_pronoun_mention/gender_number_for/gn_compatible, PROMOTED, consumed
directly); hdlab.thematic_role_labeler.lemma_verb; hdlab.goal_owner_select.py (backward-compat
consumer, unaffected by this promotion, verified not merely asserted).
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from hdlab.coreference_resolver import (
    normalize_tokens, is_pronoun_mention, gender_number_for, gn_compatible,
)
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


# ============================================================================ OUTCOME-VALENCE:
# GOAL-CONGRUENCE (promotion, 2026-08-06). Hand-authored, innate-core physical/social result-state
# verb typology (SUPPLY, not induce -- same scope/pattern as DESIDERATIVE_PASS/ASPECTUAL_STOP above).
# Byte-identical to experiments/exp_outcome_valence_goal_congruence_v2.py's CLASS_REGISTRY (v2's
# 8-class register is a superset of v1's original 4 classes; v1's items re-verdict bit-identically
# under this expanded registry -- see self_test).
REPAIR_PRESERVE = {"mend", "fix", "repair", "save", "rescue", "protect", "build", "restore"}
DAMAGE_LOSE = {"sink", "break", "fall", "collapse", "lose", "fail", "destroy", "damage", "wreck",
               "crash", "drown", "flood"}
ARRIVE_SUCCEED = {"reach", "escape", "arrive", "win", "succeed"}
FAIL_LOSE = {"lose", "fail", "miss"}
# v2 SUPPLY fix: lemma_verb("collapsed") -> "collaps" (silent-e truncation, a
# hdlab.thematic_role_labeler production limitation; v1's own bank never hit this because
# "collapse" only appeared unconjugated there). Documented workaround, not a mechanism change: add
# the mis-lemmatized surface form as an explicit class member so find_actual_state_candidates below
# can still see this candidate at all.
DAMAGE_LOSE.add("collaps")

OPEN_CLASS = {"open", "unlock", "unseal", "unbar", "unbolt"}
CLOSE_CLASS = {"shut", "lock", "seal", "bar", "bolt"}
FILL_CLASS = {"fill", "fil", "load", "stock"}  # "fil": lemma_verb("filled") double-consonant bug
EMPTY_CLASS = {"empty", "drain", "unload"}
GATHER_CLASS = {"gather", "collect"}
SCATTER_CLASS = {"scatter"}
HEAL_CLASS = {"heal"}
HARM_CLASS = {"worsen", "fester"}

CLASS_REGISTRY = {
    "REPAIR_PRESERVE": REPAIR_PRESERVE, "DAMAGE_LOSE": DAMAGE_LOSE,
    "ARRIVE_SUCCEED": ARRIVE_SUCCEED, "FAIL_LOSE": FAIL_LOSE,
    "OPEN_CLASS": OPEN_CLASS, "CLOSE_CLASS": CLOSE_CLASS,
    "FILL_CLASS": FILL_CLASS, "EMPTY_CLASS": EMPTY_CLASS,
    "GATHER_CLASS": GATHER_CLASS, "SCATTER_CLASS": SCATTER_CLASS,
    "HEAL_CLASS": HEAL_CLASS, "HARM_CLASS": HARM_CLASS,
}
OPPOSED_PAIRS = [
    ("REPAIR_PRESERVE", "DAMAGE_LOSE"), ("ARRIVE_SUCCEED", "FAIL_LOSE"),
    ("OPEN_CLASS", "CLOSE_CLASS"), ("FILL_CLASS", "EMPTY_CLASS"),
    ("GATHER_CLASS", "SCATTER_CLASS"), ("HEAL_CLASS", "HARM_CLASS"),
]
OPPOSED_OF: dict = {}
for _a, _b in OPPOSED_PAIRS:
    OPPOSED_OF.setdefault(_a, set()).add(_b)
    OPPOSED_OF.setdefault(_b, set()).add(_a)

# Which grammatical position holds the referent for CONTROL-pattern ("X wanted to VP") sentences,
# keyed by the embedded verb's class: achievement verbs (win/reach/...) -- the SUBJECT (agent) is
# who changes state; change-of-state transitives (mend/save/open/fill/...) -- the OBJECT (patient)
# is who changes state, regardless of syntactic transitivity.
SUBJECT_IS_REFERENT_CLASSES = {"ARRIVE_SUCCEED", "FAIL_LOSE"}
OBJECT_IS_REFERENT_CLASSES = {
    "REPAIR_PRESERVE", "DAMAGE_LOSE", "OPEN_CLASS", "CLOSE_CLASS", "FILL_CLASS", "EMPTY_CLASS",
    "GATHER_CLASS", "SCATTER_CLASS", "HEAL_CLASS", "HARM_CLASS",
}


def _verb_classes(lemma: str) -> set:
    return {name for name, members in CLASS_REGISTRY.items() if lemma in members}


def _opposed_of(classes: set) -> set:
    out = set()
    for c in classes:
        out |= OPPOSED_OF.get(c, set())
    return out


# Discourse-entity referent linking (v2's coverage-wall fix). TIER 2 SUPPLY register: SMALL,
# hand-authored, honestly scoped to the source cell's L-family case -- NOT a general synonym/WordNet
# substitute (hdlab.concept_encoder checked and ruled out: supervised, concept-label-conditioned, no
# zero-shot pretrained weights to reuse for an ad hoc "ferry"~"vessel" query -- see module docstring
# SCOPE section).
SYNONYM_GROUPS = [
    {"ferry", "vessel", "boat", "ship"},
]
_SYNONYM_OF: dict = {}
for _grp in SYNONYM_GROUPS:
    for _w in _grp:
        _SYNONYM_OF[_w] = _grp

LINK_TIERS = {"literal", "pronoun_coref", "synonym"}  # tiers that count as a genuine referent link


def _referent_links(desired_ref, actual_ref):
    """Discourse-entity-level referent match. Returns (linked: bool, tier: str). TIER 0 (literal):
    exact surface match. TIER 1 (pronoun_coref) fires ONLY when `actual_ref` is a bare pronoun
    surface (`is_pronoun_mention`, owned hdlab.coreference_resolver primitive) AND its gender/number
    is agreement-compatible (`gn_compatible`, same owned primitive the production pronoun resolvers
    use) with the goal referent's inferred gender/number (`gender_number_for`, nominal-cue path).
    TIER 2 (synonym) fires ONLY when both referents are literal members of the SAME hand-authored
    SYNONYM_GROUPS entry. Two distinct common nouns with neither relationship (e.g. "sister"/"rival",
    "workshop"/"shed") NEVER link -- there is no generic-similarity fallback tier, by design (the
    over-link guard). Byte-identical logic to
    experiments/exp_outcome_valence_goal_congruence_v2.py::_referent_links."""
    if desired_ref is None or actual_ref is None:
        return False, "none"
    if desired_ref == actual_ref:
        return True, "literal"
    if is_pronoun_mention(actual_ref):
        p_gender, p_number = gender_number_for(actual_ref, is_pron=True)
        c_gender, c_number = gender_number_for(desired_ref, is_pron=False)
        if gn_compatible(p_gender, p_number, c_gender, c_number):
            return True, "pronoun_coref"
        return False, "pronoun_incompatible"
    if actual_ref in _SYNONYM_OF.get(desired_ref, ()):
        return True, "synonym"
    return False, "no_link"


# tokenization + NP extraction, scoped to the outcome-valence mechanism (distinct from DET_STOP
# above, which includes "to" for the purpose-infinitival scan -- this _DET is the plain determiner
# set used to strip a leading determiner off an extracted NP span). Byte-identical to
# experiments/exp_outcome_valence_goal_congruence_v1.py's _DET/_STOP_BOUNDARY/_tokens/
# _np_last_content.
_DET = {"the", "a", "an", "his", "her", "its", "their", "this", "that", "my", "your", "our"}
_STOP_BOUNDARY = ({"before", "after", "so", "and", "but", "or", "when", "while", "until", "if",
                    "because", "from", "for", "by", "at", "in", "on", "with"} | DIRECTIONAL_PP)


def _tokens(sentence: str):
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


def _np_last_content(span):
    """Rightmost content token of an NP span, after stripping ONE leading determiner-equivalent (a
    closed DET set, or any token ending "'s" -- handles both "the old oak tree" (-> tree) and
    possessive "Owen's rival" (-> rival, not owen))."""
    toks = list(span)
    if toks and (toks[0] in _DET or toks[0].endswith("'s")):
        toks = toks[1:]
    return toks[-1] if toks else None


def _sentences(text: str) -> List[str]:
    """Trivial sentence splitter. Byte-copied (not imported) from
    hdlab.goal_owner_select._sentences (itself byte-copied from experiments/
    exp_situation_model_goal_outcome_dimension_v1.py) so this module has no dependency on
    hdlab.goal_owner_select, which imports type_goal_events FROM this module -- a reverse import
    would be circular."""
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]


def find_desired_state(sentence: str):
    """Locate a desiderative-governed purpose-infinitival "to VERB" and extract
    {referent, classes, verb_lemma, pattern}. Returns None if no DESIDERATIVE_PASS verb is found.
    Byte-identical logic to
    experiments/exp_outcome_valence_goal_congruence_v1.py::find_desired_state (reuses this module's
    own DESIDERATIVE_PASS/DET_STOP, unchanged)."""
    toks = _tokens(sentence)
    dv_idx = next((i for i, t in enumerate(toks) if t in DESIDERATIVE_PASS), None)
    if dv_idx is None:
        return None
    for i in range(dv_idx + 1, len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        embedded_lemma = lemma_verb(toks[i + 1])
        classes = _verb_classes(embedded_lemma)
        between = toks[dv_idx + 1:i]
        if between:
            referent = _np_last_content(between)
            pattern = "ECM"
        else:
            pattern = "CONTROL"
            if classes & SUBJECT_IS_REFERENT_CLASSES:
                referent = _np_last_content(toks[:dv_idx])
            elif classes & OBJECT_IS_REFERENT_CLASSES:
                j = i + 2
                while j < len(toks) and toks[j] not in _STOP_BOUNDARY and toks[j] != "to":
                    j += 1
                referent = _np_last_content(toks[i + 2:j])
            else:
                referent = None
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": pattern}
    return None


def find_actual_state_candidates(sentence: str):
    """ALL class-match verb occurrences in `sentence`, left-to-right (not just the first -- needed so
    congruence_decision below can prefer a LATER goal-relevant clause over an EARLIER same-class
    DISTRACTOR clause, e.g. "The workshop flooded and the shed collapsed." must not resolve to
    'workshop' just because 'flooded' is scanned first). Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v2.py::find_actual_state_candidates."""
    toks = _tokens(sentence)
    out = []
    for idx, t in enumerate(toks):
        lemma = lemma_verb(t)
        classes = _verb_classes(lemma)
        if classes:
            referent = _np_last_content(toks[:idx])
            out.append({"referent": referent, "classes": classes, "verb_lemma": lemma, "verb_idx": idx})
    return out


def find_actual_state(sentence: str):
    """Backward-compat single-candidate accessor (first match only). Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::find_actual_state. Not used by
    congruence_decision below (which uses find_actual_state_candidates directly)."""
    cands = find_actual_state_candidates(sentence)
    return cands[0] if cands else None


def congruence_decision(goal_sentences, outcome_sentence: str):
    """The 3-way MET/UNMET/NA goal-congruence decision, resolving the outcome's referent to a
    DISCOURSE ENTITY (via _referent_links: literal / pronoun-coref / synonym) before matching against
    the goal's theme, searched across every class-related candidate verb occurrence in the outcome
    sentence. Byte-identical logic to
    experiments/exp_outcome_valence_goal_congruence_v2.py::congruence_decision (v2's discourse-entity
    upgrade of v1's plain string-equality match)."""
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    if desired is None:
        return "NA", {"reason": "no_desiderative_goal_found"}
    candidates = find_actual_state_candidates(outcome_sentence)
    if not candidates:
        return "NA", {"reason": "actual_verb_class_unknown", "desired": desired}

    # Pass 1: among candidates whose verb-class RELATES to the desired class (same or opposed),
    # prefer the first one (left-to-right) whose referent LINKS to the desired referent (literal /
    # pronoun-coref / synonym).
    actual, link_tier = None, None
    for cand in candidates:
        related = bool((desired["classes"] & cand["classes"])
                       or (_opposed_of(desired["classes"]) & cand["classes"]))
        if not related:
            continue
        linked, tier = _referent_links(desired["referent"], cand["referent"])
        if linked:
            actual, link_tier = cand, tier
            break
    if actual is None:
        # No candidate's referent resolves to the goal theme -- preserve the original first-match
        # fallback (backward-compat with the precision guards: D-unmet/H2 must still correctly fall
        # through to referent_mismatch/verb_class_unrelated, never a forced link).
        actual = candidates[0]
        _, link_tier = _referent_links(desired["referent"], actual["referent"])

    same = desired["classes"] & actual["classes"]
    opposed = _opposed_of(desired["classes"]) & actual["classes"]
    if not same and not opposed:
        return "NA", {"reason": "verb_class_unrelated", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if desired["referent"] is None or actual["referent"] is None:
        return "NA", {"reason": "referent_extraction_failed", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if link_tier not in LINK_TIERS:
        return "UNMET", {"reason": "referent_mismatch", "desired": desired, "actual": actual,
                         "link_tier": link_tier}
    if same:
        return "MET", {"reason": "same_class_same_referent", "desired": desired, "actual": actual,
                       "link_tier": link_tier}
    return "UNMET", {"reason": "opposed_class_same_referent", "desired": desired, "actual": actual,
                     "link_tier": link_tier}


def congruence_outcome_valence(passage_text: str):
    """Top-level entry: split `passage_text` into sentences (this module's own _sentences), goal-
    sentences = all but the last, outcome-sentence = the last. Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::congruence_outcome_valence."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    return congruence_decision(sents[:-1], sents[-1])


def lexicon_predict(outcome_sentence: str):
    """The mechanism this promotion supplements (not deletes): V2_OUTCOME_UNMET/_MET set-membership
    on the outcome sentence alone (same sets, same tokenization convention as
    type_sentence_events_c3 above). Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::lexicon_predict."""
    t = normalize_tokens(outcome_sentence)
    has_unmet = bool(t & V2_OUTCOME_UNMET)
    has_met = bool(t & V2_OUTCOME_MET)
    if has_unmet and has_met:
        return "AMBIGUOUS"
    if has_unmet:
        return "UNMET"
    if has_met:
        return "MET"
    return "NONE"


def congruence_with_lexicon_fallback(passage_text: str):
    """PRODUCTION entry point: goal-congruence PRIMARY, V2_OUTCOME_UNMET/_MET lexicon as the ABSTAIN
    fallback (strict ADD -- non-goal-dependent / non-referent-stress behavior is unchanged from the
    pre-promotion lexicon-only path). Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::congruence_with_lexicon_fallback."""
    verdict, detail = congruence_outcome_valence(passage_text)
    if verdict != "NA":
        return verdict, detail
    sents = _sentences(passage_text)
    lex = lexicon_predict(sents[-1]) if sents else "NONE"
    return lex, {"reason": "abstain_fallback_to_lexicon", "lexicon_raw": lex}


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

    # ---- OUTCOME-VALENCE GOAL-CONGRUENCE (promotion, 2026-08-06) -------------------------------
    # (8) DECISIVE: a goal-dependent flip in BOTH directions on the SAME outcome word ("sank") --
    # the lexicon (goal-independent) cannot do this by construction; the congruence mechanism must.
    flip_unmet, flip_unmet_detail = congruence_decision(
        ["Owen wanted to save the boat before the storm hit"], "The boat sank")
    assert flip_unmet == "UNMET" and flip_unmet_detail["reason"] == "opposed_class_same_referent", (
        f"goal=save(boat), outcome=sank(boat) must be UNMET (opposed class), got {flip_unmet} "
        f"({flip_unmet_detail})")
    flip_met, flip_met_detail = congruence_decision(
        ["Owen wanted to sink the raft before dawn"], "The raft sank")
    assert flip_met == "MET" and flip_met_detail["reason"] == "same_class_same_referent", (
        f"goal=sink(raft), outcome=sank(raft) must be MET (same class, SAME 'sank' word as the UNMET "
        f"case above -- the flip), got {flip_met} ({flip_met_detail})")

    # (9) DECISIVE: pronoun-referent MET (Tier-1 coref link) -- "it" resolves to "canoe" via
    # gender/number agreement (hdlab.coreference_resolver primitives), not a literal string match.
    pron_met, pron_detail = congruence_decision(
        ["Owen wanted to save the canoe before the flood came"], "It mended quickly")
    assert pron_met == "MET" and pron_detail["link_tier"] == "pronoun_coref", (
        f"goal=save(canoe), outcome=mended(it) must be MET via pronoun_coref linking, got {pron_met} "
        f"({pron_detail})")

    # (10) DECISIVE: over-link guard, genuinely-different-referent UNMET -- an ECM goal ("wanted his
    # SISTER to win") must NOT be satisfied by a different entity's same-class outcome ("his RIVAL
    # won"); sister and rival share no pronoun/synonym relationship, so they must never link.
    diff_ref, diff_detail = congruence_decision(
        ["Owen wanted his sister to win the race before the whistle blew"], "His rival won the race")
    assert diff_ref == "UNMET" and diff_detail["reason"] == "referent_mismatch", (
        f"goal=win(sister) [ECM], outcome=won(rival) must be UNMET (over-link guard: sister!=rival, "
        f"no pronoun/synonym relationship), got {diff_ref} ({diff_detail})")
    assert diff_detail["link_tier"] == "no_link", "over-link guard must not fabricate a link tier"

    # (11) DECISIVE: theme-mismatch ABSTAIN -> lexicon fallback -- the goal's verb class (OPEN_CLASS)
    # is unrelated to the outcome's verb class (ARRIVE_SUCCEED), so the mechanism must abstain (NA);
    # the PRODUCTION wrapper then falls back to the V2_OUTCOME_UNMET/_MET lexicon, which correctly
    # reads "reached" as MET -- proving the strict-ADD fallback contract actually fires end-to-end.
    theme_mismatch, theme_detail = congruence_decision(
        ["Owen wanted to open the greenhouse before winter came"], "The gardener reached the market")
    assert theme_mismatch == "NA" and theme_detail["reason"] == "verb_class_unrelated", (
        f"goal=open(greenhouse), outcome=reached(gardener/market) must ABSTAIN (unrelated verb "
        f"classes), got {theme_mismatch} ({theme_detail})")
    fallback_verdict, fallback_detail = congruence_with_lexicon_fallback(
        "Owen wanted to open the greenhouse before winter came. The gardener reached the market.")
    assert fallback_verdict == "MET" and fallback_detail["reason"] == "abstain_fallback_to_lexicon", (
        f"ABSTAIN must fall back to the lexicon (which reads 'reached' as MET), "
        f"got {fallback_verdict} ({fallback_detail})")

    # (12) v1 regression: v1's original 10-item bank re-verdicts bit-identically under this module's
    # expanded registry (proves the CLASS_REGISTRY expansion did not silently change v1 behavior).
    import json
    import os
    _v1_bank_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "experiments", "data", "outcome_valence_congruence_v1.jsonl")
    v1_mismatches = []
    if os.path.exists(_v1_bank_path):
        with open(_v1_bank_path, "r", encoding="utf-8") as f:
            v1_rows = [json.loads(line) for line in f if line.strip()]
        for row in v1_rows:
            sents = _sentences(row["text"])
            verdict, _detail = congruence_decision(sents[:-1], sents[-1])
            if verdict != row["gold"]:
                v1_mismatches.append((row["id"], verdict, row["gold"]))
        assert not v1_mismatches, f"v1 bank regression under expanded registry: {v1_mismatches}"

    return {
        "goal_hoped_to_win": goal_hoped,
        "goal_began_to_open": goal_began,
        "goal_action_frame_telos": goal_action_frame,
        "c3_only_misses_hoped": not any(r == R_GOAL for (_e, r) in c3_only_events),
        "outcome_valence": {
            "flip_unmet": flip_unmet, "flip_met": flip_met, "pronoun_referent_met": pron_met,
            "over_link_guard_unmet": diff_ref, "theme_mismatch_abstain": theme_mismatch,
            "abstain_fallback_verdict": fallback_verdict, "v1_bank_checked": len(v1_rows) if
            os.path.exists(_v1_bank_path) else 0, "v1_regression_mismatches": v1_mismatches,
        },
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
