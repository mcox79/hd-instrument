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
gender_number_for/gn_compatible, already-production primitives, reused unmodified; Tier-2 (2026-08-06
upgrade, see TIER-2 UPGRADE section below): shared-feature cosine similarity, hdlab.lexical_
similarity, the lifted exp_n11c ATL-hub organ); same-referent + same/entailing class -> MET; same-referent +
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

TIER-2 UPGRADE (2026-08-06, WIRE-DONT-ISLAND): the original NARROW hand-authored SYNONYM_GROUPS
register (one group, {ferry, vessel, boat, ship}) is REPLACED by the shared-feature-similarity
organ proved in experiments/exp_n11c_shared_feature_lexical_similarity_v1.py (commit 7d0a574b4,
HARD_PASS: ordered_frac=0.9655 vs WINDOW=0.3793/HASH_RANDOM=0.1034, SCRAMBLED_FEATURES collapse
confirms earned-not-artifact), lifted into hdlab/lexical_similarity.py (clean copy of the
McRae-style feature lexicon + FHRR bundle-cosine encoder, both hdlab-only -- no experiments/
import). Two referents link at Tier-2 iff BOTH are present in
hdlab.lexical_similarity.CONCEPT_FEATURES AND their shared-feature cosine clears
SIMILARITY_LINK_THRESHOLD=0.50 (MEASURED@this promotion: sim(vessel,ferry)=0.634 links;
sim(sister,rival)=0.398 and sim(vessel,dock)=0.279 do NOT -- see
preregs/2026-08-06_wire_shared_feature_similarity_outcome_valence_v1.md). OOV-of-lexicon falls
through to no-link (never crashes, never over-links by default).

SCOPE (do not overclaim): Tier-1 pronoun-referent linking is GENERAL (the production coreference
primitives, not bank-specific). Tier-2 shared-feature linking is scoped to
hdlab.lexical_similarity.CONCEPT_FEATURES's 89 concepts (the 86 exp_n11c concepts + 3 SUPPLY
additions for this bank's referent-stress items); general open-vocabulary synonym/hypernym
resolution (inducing features for arbitrary words) remains a separate, missing-LEARNING follow-up,
not claimed here. Validated on a N=26 hand-authored bank
(experiments/data/outcome_valence_congruence_v2.jsonl) -- production-safe as a strict ADD (zero
regression on every existing call site), but broad real-data coverage beyond this bank remains the
open follow-up, same caveat the source cells' own verdict already carries.

Cites (outcome-valence section): experiments/exp_outcome_valence_goal_congruence_v1.py (mechanism
origin, commit 63c71935d); experiments/exp_outcome_valence_goal_congruence_v2.py (discourse-entity
referent resolution + expanded RESULT_VERB_CLASS register + 26-item bank, commit 3ed374148);
experiments/exp_n11c_shared_feature_lexical_similarity_v1.py (Tier-2 shared-feature-similarity
organ, commit 7d0a574b4, HARD_PASS); hdlab/lexical_similarity.py (the lifted production organ,
this promotion); hdlab.coreference_resolver (is_pronoun_mention/gender_number_for/gn_compatible,
PROMOTED, consumed directly); hdlab.thematic_role_labeler.lemma_verb; hdlab.goal_owner_select.py
(backward-compat consumer, unaffected by this promotion, verified not merely asserted).
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
from hdlab.lexical_similarity import (
    concept_similarity as _lexsim_concept_similarity,
    in_lexicon as _lexsim_in_lexicon,
    SIMILARITY_LINK_THRESHOLD,
)
from hdlab import verb_lexical_similarity as _verblex

# TIER-2 OPEN-VOCAB VERB-CLASS UPGRADE (2026-08-06). Per
# notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md (formalize drill) +
# preregs/2026-08-06_verb_class_openvocab_similarity_v1.md: extends CLASS_REGISTRY /
# V2_OUTCOME_MET/_UNMET / DESIDERATIVE_PASS-ASPECTUAL_STOP membership from exact `lemma in members`
# to concept_similarity(verb, class_seed_exemplars) via hdlab.verb_lexical_similarity (the verb-
# feature-tagged sibling of hdlab.lexical_similarity's ATL-hub-style organ). Thresholds MEASURED@
# preregs/2026-08-06_verb_class_openvocab_similarity_v1.md (held-out non-circular classification,
# both pools well above floor with wide margins; see that pre-reg for the exact numbers this
# threshold choice is based on). Strict ADD in all three integration points below: Tier-1 exact
# literal membership always wins; Tier-2 only fires on OOV-of-Tier-1; abstain (None/{}/False) is
# IDENTICAL to today's OOV behavior in every case, so this can never regress a caller that
# currently gets no class/no polarity/no skip.
VERB_CLASS_SIM_FLOOR = 0.35
VERB_CLASS_MARGIN = 0.15

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

# TIER-2 (2026-08-06): open-vocab 2-way MET/UNMET fallback for tokens OOV of the flat V2 lexicon
# above. Seed pools = the verb-like subset of V2_OUTCOME_MET/_UNMET's own lemmas (their non-verb
# members -- "sorry"/"late"/"never"/"down"/"unwarned"/"unprotected"/"calamity" -- are adjectives/
# adverbs/a noun and stay Tier-1-only, unaffected). This is the mechanism that directly targets the
# OUTCOME_NEVER_TYPED bottleneck (disk-verified 6/10 on real prose, commit f496caa51): outcome-
# typeability for owner-selection is gated entirely by has_unmet/has_met below, not by
# CLASS_REGISTRY -- see preregs/2026-08-06_verb_class_openvocab_similarity_v1.md.
_V2_POLARITY_SEED_POS = ("reach", "win", "escape", "arrive", "enjoy")
_V2_POLARITY_SEED_NEG = ("fall", "sink", "lose", "fail", "miss", "wail")


def _outcome_polarity_tier2(lemma: str):
    """2-way POS/NEG classification via hdlab.verb_lexical_similarity. Returns "MET", "UNMET", or
    None (abstain -- OOV, below floor, or margin too thin)."""
    verdict = _verblex.classify_2way(lemma, _V2_POLARITY_SEED_POS, _V2_POLARITY_SEED_NEG,
                                      "outcome", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
    if verdict == "POS":
        return "MET"
    if verdict == "NEG":
        return "UNMET"
    return None


def _tier2_outcome_polarity_scan(sentence: str):
    """Scan every ordered token of `sentence` that is OOV of the literal V2_OUTCOME_UNMET/_MET
    sets; lemmatize + Tier-2 classify each. Returns (has_unmet_t2, has_met_t2) -- either or both may
    fire (mirrors the existing Tier-1 has_unmet/has_met independence, which callers already
    disambiguate, e.g. lexicon_predict's AMBIGUOUS branch)."""
    has_unmet_t2 = False
    has_met_t2 = False
    for tok in _ordered_tokens(sentence):
        if tok in V2_OUTCOME_UNMET or tok in V2_OUTCOME_MET:
            continue
        lemma = lemma_verb(tok)
        verdict = _outcome_polarity_tier2(lemma)
        if verdict == "UNMET":
            has_unmet_t2 = True
        elif verdict == "MET":
            has_met_t2 = True
    return has_unmet_t2, has_met_t2


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
    -- identical to the conservative wire in hdlab/situation_reader.py) labels subj=EXPERIENCER,
    AND that EXPERIENCER token is not itself NEGATED. Based on
    experiments/exp_component5_wired_endtoend_v1.py::c3_has_desire; NO LONGER byte-identical --
    extended 2026-08-06 with the same do-support/modal/"never" negation-scope guard the construction
    path uses (_verb_negated_before), so a NEGATED desire state ("he did NOT like to VP") is not
    read as an active desire (that source cell keeps its own copy untouched as its historical
    source-of-truth). A non-negated EXPERIENCER fire ("he was WANTING attention") is unchanged."""
    toks = _ordered_tokens(sentence)
    for k, tok in enumerate(toks):
        lemma = lemma_verb(tok)
        role = frame_primary_role(lemma, [], 0, None, "subj")
        if role == "EXPERIENCER" and not _verb_negated_before(toks, k):
            return True
    return False


def type_sentence_events_c3(sentence: str, subject) -> List[Tuple[object, str]]:
    """Based on experiments/exp_component5_wired_endtoend_v1.py::type_sentence_events_c3
    (has_desire computed via the real Component-3 mechanism, c3_has_desire); OUTCOME_UNMET/
    OUTCOME_MET stay PRIMARILY lexicon-typed (Tier-1, unchanged) with a TIER-2 open-vocab
    similarity fallback added 2026-08-06 (_tier2_outcome_polarity_scan) for tokens OOV of the flat
    V2_OUTCOME_UNMET/_MET lexicon -- strict ADD, Tier-1 exact membership always wins."""
    t = _tokset(sentence)
    events: List[Tuple[object, str]] = []
    has_desire = c3_has_desire(sentence)
    has_unmet_t2, has_met_t2 = _tier2_outcome_polarity_scan(sentence)
    has_unmet = bool(t & V2_OUTCOME_UNMET) or has_unmet_t2
    has_met = bool(t & V2_OUTCOME_MET) or has_met_t2
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
    "hope", "hopes", "hoped", "hoping", "want", "wants", "wanted", "wanting",
    "wish", "wishes", "wished", "wishing", "mean", "means", "meant", "meaning",
    "plan", "plans", "planned", "planning", "intend", "intends", "intended", "intending",
    "aim", "aims", "aimed", "aiming", "long", "longs", "longed", "longing",
    "yearn", "yearns", "yearned", "yearning", "desire", "desires", "desired", "desiring",
    # BOULETIC-PREFERENCE extension (2026-08-06 coverage expansion): like/love are the same
    # world-to-mind DESIRE class as want/wish/hope (Searle 1983 Intentionality), NOT a new
    # category. base + 3sg + past + gerund, matching the desiderative inflection convention.
    "like", "likes", "liked", "liking", "love", "loves", "loved", "loving",
}
# CONATIVE / ATTEMPT class (2026-08-06 coverage expansion): "try to VP" recognizes the goal via
# Talmy (1988) force-dynamics AGONIST-exertion -- the goal is recognized EVEN WHEN THE ATTEMPT
# FAILS ("tried to X but couldn't" -> X is still the goal). Moved OUT of ASPECTUAL_STOP: an
# attempt is NOT aspectual marking of a prior action, it IS the effortful reaching toward a goal.
CONATIVE_PASS = {"try", "tries", "tried", "trying"}
# INTENTION / DECISION / COMMITMENT class (2026-08-06 coverage expansion): "decide/determine to
# VP" -- Bratman (1987) intention-vs-desire; deciding FORMS an intention and the decided-upon
# action becomes the goal regardless of whether it is later acted out. decide* moved OUT of
# OTHER_STOP_UNCHANGED; determine* was previously in NO set (a genuine unclassified gap).
INTENTION_PASS = {
    "decide", "decides", "decided", "deciding",
    "determine", "determines", "determined", "determining",
}
# ASPECTUAL/IMPLICATIVE verbs -- NOT goal-signaling ("X began/failed to VP" is not a goal
# ownership signal); STAYS in the stop set. (try* REMOVED 2026-08-06 -> CONATIVE_PASS: it was
# miscategorized -- an attempt is a goal signal, not aspectual marking.)
ASPECTUAL_STOP = {
    "begin", "begins", "began", "start", "starts", "started",
    "fail", "fails", "failed",
    "manage", "manages", "managed", "happen", "happens", "happened",
    "cease", "ceases", "ceased", "stop", "stops", "stopped",
    "continue", "continues", "continued",
}
# Remaining unclassified / precision-safe stop-set verbs. (decide* REMOVED 2026-08-06 ->
# INTENTION_PASS: it was an acknowledged placeholder, not a considered exclusion.)
OTHER_STOP_UNCHANGED = {
    "need", "needs", "needed", "seem", "seems", "seemed",
    "get", "gets", "got", "choose", "chooses", "chose",
}
PARTITIONED_STOP = ASPECTUAL_STOP | OTHER_STOP_UNCHANGED
# GOAL_GOVERNING_PASS: the UNION of the three intentional-state pass-classes (bouletic DESIRE +
# conative ATTEMPT + intention DECISION -- Bratman 1987's three-way split). BOTH consumers below
# (find_desired_state's dv_idx gate and _control_verb_is_aspectual_like's Tier-1 check) test THIS
# union, not DESIDERATIVE_PASS alone -- the union coverage at both call sites is load-bearing.
GOAL_GOVERNING_PASS = DESIDERATIVE_PASS | CONATIVE_PASS | INTENTION_PASS
# Load-bearing invariant: the removal-half (try*/decide* out of the stop sets) and the addition-half
# (CONATIVE_PASS/INTENTION_PASS) MUST land together or this assert AssertionErrors at import.
assert GOAL_GOVERNING_PASS.isdisjoint(PARTITIONED_STOP), "goal-governing pass-set must be disjoint from the stop set"
assert DESIDERATIVE_PASS.isdisjoint(CONATIVE_PASS) and DESIDERATIVE_PASS.isdisjoint(INTENTION_PASS) \
    and CONATIVE_PASS.isdisjoint(INTENTION_PASS), "the three pass-classes must be mutually disjoint"


# ============================================================================ NEGATION-SCOPE GUARD
# (2026-08-06). Closes the pre-existing negation gap that the goal-recognition coverage expansion
# (commit 051f6d0ef) widened: a GOAL_GOVERNING_PASS verb that is itself NEGATED ("did not try",
# "never decided", "did not mean", "did not like") signals a NEGATED/ABSENT goal and must NOT be
# recognized as an active goal (abstain). LOAD-BEARING PRECISION GUARD: the negator must scope the
# GOVERNING VERB ITSELF (precede it, via do-support / modal / "never" adjacency), NOT the "to VP"
# COMPLEMENT -- "He tried NOT to cry" / "She decided NOT to go" are AVOIDANCE goals (the goal-holder
# still HAS a goal) and MUST still fire. That is why only tokens PRECEDING the governing verb are
# consulted (a complement negator sits AFTER the governing verb, so it can never suppress). Brain-
# grounding: FrameNet Negation frame (EVOKED_BY never.adv, HAS_FE Negated_proposition) -- the top
# substrate-KB hit for this concept.
#
# SCOPE / known edges (reported honestly, "scope out conservatively"): (a) double-negation via a
# lexical negative-implicative ("did not FAIL to arrive", "never NEGLECTED to help") is semantically
# POSITIVE; those never reach this guard because fail/neglect/arrive are not GOAL_GOVERNING_PASS
# verbs (dv_idx is None -> already abstained), so no false-suppression. (b) Litotes "not without ...
# hopes" is NOT suppressed because the negator is not adjacent to the (noun) "hopes" -- a content
# word breaks the window. (c) A double negation directly adjacent to a governing verb ("not not
# want") and a fronted negation ("Never did she want to VP") are out of scope, left as known edges
# (the conservative direction is to NOT suppress, favoring recall over false-suppression).
NEGATORS = {"not", "never", "no", "none", "cannot"}
# Degree/focus adverbs that can sit between a do-support/modal negator and the verb ("did not REALLY
# want", "would not EVER decide") -- transparent to the backward negator scan. A content word,
# preposition, determiner, or clause boundary is NOT transparent and stops the scan (this is what
# keeps litotes "not without her own secret HOPES" un-suppressed: "secret" stops the scan short).
_NEG_TRANSPARENT_ADVERBS = {"really", "ever", "always", "just", "simply", "even", "quite", "only",
                            "truly", "actually", "once", "also", "still"}
_NEG_MAX_SKIP = 2


def _is_negator(tok: str) -> bool:
    """True for an explicit clausal negator token: a NEGATORS-set word or an n't-contraction
    ("didn't"/"won't"/"can't"/... -- the [a-z']+ tokenizer keeps "n't" joined to its host)."""
    return tok in NEGATORS or tok.endswith("n't")


def _verb_negated_before(toks: List[str], v_idx: int) -> bool:
    """True iff a negator scopes the verb at toks[v_idx] via do-support / modal / "never" adjacency:
    scan LEFT from v_idx-1, skipping up to _NEG_MAX_SKIP transparent degree adverbs; an explicit
    negator within that window -> negated; a content word / clause boundary / sentence start ->
    NOT negated. Only tokens PRECEDING the verb are consulted, so a negator on the "to VP" complement
    ("tried NOT to cry") never suppresses -- that negator sits AFTER the governing verb."""
    steps = 0
    j = v_idx - 1
    while j >= 0 and steps <= _NEG_MAX_SKIP:
        tok = toks[j]
        if _is_negator(tok):
            return True
        if tok in _NEG_TRANSPARENT_ADVERBS:
            j -= 1
            steps += 1
            continue
        return False
    return False


# TIER-2 (2026-08-06): open-vocab control-verb classification for action_frame_feats's PARTITIONED
# exclusion below. Seed pools = the lemma forms already in ASPECTUAL_STOP / DESIDERATIVE_PASS.
# ("try" REMOVED from the aspect seed pool 2026-08-06: it is now CONATIVE, and leaving it here
# would bias OOV siblings attempt/endeavor/strive toward the wrong (aspectual-suppress) pool.)
_GOAL_ASPECT_SEED_LEMMAS = ("begin", "start", "fail", "manage", "happen", "cease", "stop",
                            "continue")
_GOAL_DESID_SEED_LEMMAS = ("want", "hope", "wish", "mean", "plan", "intend", "aim", "long",
                           "yearn", "desire")


def _control_verb_is_aspectual_like(preceding: str) -> bool:
    """True iff `preceding` should be treated as an aspectual/implicative control verb (i.e. the
    purpose-infinitival construction should be SUPPRESSED). Tier-1: literal PARTITIONED_STOP /
    DESIDERATIVE_PASS membership (unchanged, always wins). Tier-2 (NEW): for a preceding word OOV
    of BOTH literal sets, classify via hdlab.verb_lexical_similarity; only a confident
    ASPECTUAL-pool verdict flips the (permissive) default to suppress -- abstain or a
    DESIDERATIVE-pool verdict preserves today's default behavior (fire purpose_to_no_det), so this
    can only ever ADD precision (catch more true aspectual-like OOV governing verbs), never regress
    an already-firing case."""
    if preceding in PARTITIONED_STOP:
        return True
    if preceding in GOAL_GOVERNING_PASS:  # desiderative | conative | intention (2026-08-06 union)
        return False
    lemma = lemma_verb(preceding)
    verdict = _verblex.classify_2way(lemma, _GOAL_ASPECT_SEED_LEMMAS, _GOAL_DESID_SEED_LEMMAS,
                                      "goal", VERB_CLASS_SIM_FLOOR, VERB_CLASS_MARGIN)
    return verdict == "POS"  # "POS" pool == first arg == the aspectual pool here


def action_frame_feats(sentence: str) -> List[str]:
    """Structural purpose-infinitival detector (verb-lemma-independent 'to VP' vs 'to NP'), with the
    PARTITIONED control-verb exclusion. Based on
    exp_c5_desiderative_aspectual_partition_goal_typing_v1.action_frame_feats_partitioned, extended
    2026-08-06 with a Tier-2 open-vocab control-verb classifier (_control_verb_is_aspectual_like)."""
    toks = _ordered_tokens(sentence)
    feats = []
    has_purpose_inf = False
    for i in range(len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        preceding = toks[i - 1] if i > 0 else None
        if preceding is not None and _control_verb_is_aspectual_like(preceding):
            continue
        # NEGATION-SCOPE GUARD (2026-08-06): suppress when the GOVERNING verb of this purpose-
        # infinitival is itself negated. The governing verb is toks[i-1]; if THAT token is itself a
        # negator, the negation scopes the COMPLEMENT ("tried NOT to cry" = avoidance goal, still a
        # goal) and must still fire -- so the verb-negation guard is consulted only when toks[i-1] is
        # not a negator. (Same _verb_negated_before adjacency logic find_desired_state uses.)
        if preceding is not None and not _is_negator(preceding) and _verb_negated_before(toks, i - 1):
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

# TIER-3 ACQUIRED-POLE SENTINEL (2026-08-06, grounded-word-acquisition increment 1b, Risk #1 fix;
# preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md Section 3). A Tier-3-acquired outcome
# verb (resolvable ONLY through verb_lexical_similarity.ACQUIRED_OUTCOME_VERB_FEATURES, which carries
# the polarity POLE tags but NO EVENT_DOMAIN tag) cannot be placed into one of the 12 domain-keyed
# CLASS_REGISTRY classes by the Tier-2 argmax (near-tied across same-pole classes -> margin gate fails
# -> set()), so find_actual_state_candidates' `if classes:` filter would silently drop it. The fix
# gives such a lemma a one-element POLE sentinel ({"ACQUIRED_REALIZED"} / {"ACQUIRED_BLOCKED"}) so it
# survives as a candidate, and adds ONE pole-comparison branch to _class_relation below. POS_POLE /
# NEG_POLE are a re-derivation of the ALREADY-EXISTING OPPOSED_PAIRS (first element of each pair is the
# realized/POS pole, second the blocked/NEG pole -- matches verb_lexical_similarity.OUTCOME_SEED_POS vs
# _NEG exactly), ZERO new taxonomy. All strict ADD: the overlay is EMPTY at import, so these constants
# and branches never fire for any Tier-1/Tier-2 verb -> cert/production behavior byte-identical.
POS_POLE_CLASSES = {a for a, _ in OPPOSED_PAIRS}
NEG_POLE_CLASSES = {b for _, b in OPPOSED_PAIRS}
ACQUIRED_POLE_SENTINELS = {"ACQUIRED_REALIZED", "ACQUIRED_BLOCKED"}

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
    """Tier-1: exact CLASS_REGISTRY membership (unchanged, always wins -- zero regression). Tier-2
    (2026-08-06): open-vocab fallback via shared-feature similarity, OOV-of-Tier-1 only. Tier-3
    (2026-08-06 increment 1b, Risk #1 fix): a lemma resolvable ONLY through the acquired overlay
    (Tier-1 and Tier-2 both returned nothing) gets a one-element pole sentinel so it survives
    find_actual_state_candidates' `if classes:` filter. The overlay is EMPTY at import, so this branch
    never fires for any Tier-1/Tier-2 verb -> byte-identical to before for every existing caller."""
    literal = {name for name, members in CLASS_REGISTRY.items() if lemma in members}
    if literal:
        return literal
    sim = _verb_classes_similarity(lemma)
    if sim:
        return sim
    return _acquired_pole_sentinel(lemma)


def _acquired_pole_sentinel(lemma: str) -> set:
    """Tier-3 pole sentinel for an outcome verb resolvable ONLY through
    verb_lexical_similarity.ACQUIRED_OUTCOME_VERB_FEATURES (increment 1b Risk #1). Returns
    {"ACQUIRED_REALIZED"} for an acquired POS-pole word, {"ACQUIRED_BLOCKED"} for NEG, or set() if the
    lemma is not in the acquired overlay. Never touches Tier-1/Tier-2 resolution."""
    feats = _verblex.ACQUIRED_OUTCOME_VERB_FEATURES.get(lemma)
    if feats is None:
        return set()
    if "AGONIST_REALIZED" in feats:
        return {"ACQUIRED_REALIZED"}
    if "AGONIST_BLOCKED" in feats:
        return {"ACQUIRED_BLOCKED"}
    return set()


def _pole_of(classes: set) -> Optional[str]:
    """POS/NEG/None pole for a class-set, unifying CLASS_REGISTRY poles (OPPOSED_PAIRS) and the Tier-3
    ACQUIRED_* sentinels. None if the set carries no pole or mixes both poles (ambiguous)."""
    pos = bool(classes & POS_POLE_CLASSES) or ("ACQUIRED_REALIZED" in classes)
    neg = bool(classes & NEG_POLE_CLASSES) or ("ACQUIRED_BLOCKED" in classes)
    if pos and not neg:
        return "POS"
    if neg and not pos:
        return "NEG"
    return None


def _class_relation(desired_classes: set, actual_classes: set) -> Optional[str]:
    """'same' / 'opposed' / None between a desired class-set and an actual class-set. Tier-1/Tier-2
    literal class intersection first (BYTE-IDENTICAL to the pre-1b `same`/`opposed` computation, same
    'same wins' precedence). Tier-3 (increment 1b) ADD: a single pole-comparison branch that fires
    ONLY when at least one side carries an ACQUIRED_* sentinel -- so two pure CLASS_REGISTRY sets can
    never reach it (a non-sentinel unrelated pair still returns None -> NA, exactly as before)."""
    same = bool(desired_classes & actual_classes)
    opposed = bool(_opposed_of(desired_classes) & actual_classes)
    if same or opposed:
        return "same" if same else "opposed"
    if (actual_classes & ACQUIRED_POLE_SENTINELS) or (desired_classes & ACQUIRED_POLE_SENTINELS):
        dp, ap = _pole_of(desired_classes), _pole_of(actual_classes)
        if dp is not None and ap is not None:
            return "same" if dp == ap else "opposed"
    return None


def _verb_classes_similarity(lemma: str) -> set:
    """Tier-2: argmax over CLASS_REGISTRY seed-exemplar-mean shared-feature similarity
    (hdlab.verb_lexical_similarity), thresholded + margin-gated. Returns {} (abstain) if `lemma` is
    OOV of the verb-feature lexicon, or if the best class doesn't clear the floor, or if the top-2
    classes are too close to call -- {} is IDENTICAL to today's OOV behavior, so this can never
    regress a caller that currently gets no class."""
    if not _verblex.in_lexicon(lemma, "outcome"):
        return set()
    sims = {}
    for cls, members in CLASS_REGISTRY.items():
        seed_words = [m for m in members if _verblex.in_lexicon(m, "outcome")]
        if not seed_words:
            continue
        sim = _verblex.mean_similarity_to_seeds(lemma, seed_words, "outcome")
        if sim is not None:
            sims[cls] = sim
    if not sims:
        return set()
    ranked = sorted(sims.items(), key=lambda kv: -kv[1])
    best_cls, best_sim = ranked[0]
    second_sim = ranked[1][1] if len(ranked) > 1 else -1.0
    if best_sim >= VERB_CLASS_SIM_FLOOR and (best_sim - second_sim) >= VERB_CLASS_MARGIN:
        return {best_cls}
    return set()


def _opposed_of(classes: set) -> set:
    out = set()
    for c in classes:
        out |= OPPOSED_OF.get(c, set())
    return out


# Discourse-entity referent linking (v2's coverage-wall fix). TIER 2 (2026-08-06 WIRE-DONT-ISLAND
# upgrade): shared-feature cosine similarity over hdlab.lexical_similarity.CONCEPT_FEATURES (the
# lifted exp_n11c ATL-hub organ), REPLACING the prior narrow hand-authored SYNONYM_GROUPS
# set-membership register -- see module docstring TIER-2 UPGRADE section and
# preregs/2026-08-06_wire_shared_feature_similarity_outcome_valence_v1.md.

LINK_TIERS = {"literal", "pronoun_coref", "shared_feature"}  # tiers that count as a genuine referent link


def _referent_links(desired_ref, actual_ref):
    """Discourse-entity-level referent match. Returns (linked: bool, tier: str). TIER 0 (literal):
    exact surface match. TIER 1 (pronoun_coref) fires ONLY when `actual_ref` is a bare pronoun
    surface (`is_pronoun_mention`, owned hdlab.coreference_resolver primitive) AND its gender/number
    is agreement-compatible (`gn_compatible`, same owned primitive the production pronoun resolvers
    use) with the goal referent's inferred gender/number (`gender_number_for`, nominal-cue path).
    TIER 2 (shared_feature) fires ONLY when BOTH referents are present in
    hdlab.lexical_similarity.CONCEPT_FEATURES AND their shared-feature cosine
    (hdlab.lexical_similarity.concept_similarity, the lifted exp_n11c ATL-hub organ) clears
    SIMILARITY_LINK_THRESHOLD -- either referent being OOV of that lexicon falls straight through
    to no-link (never crashes, never over-links by default). Two distinct common nouns with neither
    a pronoun-agreement nor a clears-threshold shared-feature relationship (e.g. "sister"/"rival" at
    sim=0.398 < 0.50, "workshop"/"shed" both OOV of the lexicon) NEVER link -- there is no
    unconditional generic-similarity fallback, by design (the over-link guard). Byte-identical
    referent-extraction logic to experiments/exp_outcome_valence_goal_congruence_v2.py::
    _referent_links; the Tier-2 MECHANISM itself is the 2026-08-06 upgrade (that source cell keeps
    its own SYNONYM_GROUPS copy, untouched, as the source-of-truth for its own historical numbers)."""
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
    if _lexsim_in_lexicon(desired_ref) and _lexsim_in_lexicon(actual_ref):
        sim = _lexsim_concept_similarity(desired_ref, actual_ref)
        if sim is not None and sim >= SIMILARITY_LINK_THRESHOLD:
            return True, "shared_feature"
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


# SENTENCE-SPLITTER FIX (2026-08-06, real-text generalization diagnostic, commit d52aa7669 traced
# root cause) -- kept byte-identical to hdlab.goal_owner_select._SENT_SPLIT_RE / _sentences; see that
# module for the full rationale. Summary: `[.!?]` alone split each terminal-punctuation char
# individually, so a dialogue-final passage (`...boy, Henry."`) produced a spurious bare-quote final
# fragment that survived the `if s.strip()` filter (strip() doesn't remove quote chars) and became
# `sents[-1]` -- the sentence congruence_outcome_valence/lexicon_predict treat as THE outcome
# sentence, so real dialogue-final outcomes silently went untyped. Consuming an optional
# immediately-following closing quote as part of the delimiter fixes this without changing any
# non-dialogue split point (the optional group simply never matches when no quote follows).
_SENT_SPLIT_RE = re.compile(r'[.!?]+[\'"’”]?')


def _sentences(text: str) -> List[str]:
    """Trivial sentence splitter. Byte-copied (not imported) from
    hdlab.goal_owner_select._sentences so this module has no dependency on hdlab.goal_owner_select,
    which imports type_goal_events FROM this module -- a reverse import would be circular. NO LONGER
    byte-identical to experiments/exp_situation_model_goal_outcome_dimension_v1.py's _sentences --
    that experiment cell is left untouched per the source-of-truth convention; this fix is
    PRODUCTION-only (see _SENT_SPLIT_RE comment above for the dialogue/quote-final bug this closes)."""
    return [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]


def find_desired_state(sentence: str):
    """Locate a goal-governing (desiderative | conative | intention) purpose-infinitival "to VERB"
    and extract {referent, classes, verb_lemma, pattern}. Returns None if no GOAL_GOVERNING_PASS
    verb is found. Scan logic byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::find_desired_state; the governing-verb
    gate widened 2026-08-06 from DESIDERATIVE_PASS alone to the GOAL_GOVERNING_PASS union (adds
    try/decide/determine/like/love + gerund forms)."""
    toks = _tokens(sentence)
    # NEGATION-SCOPE GUARD (2026-08-06): iterate governing-verb occurrences and SKIP one whose verb
    # is itself negated (do-support / modal / "never" adjacency, _verb_negated_before) -- a negated
    # goal is ABSENT, not active -- recognizing from the first NON-negated governing verb instead.
    # When no governing verb is negated this is behaviourally identical to the prior first-match
    # next(...) logic (first GOAL_GOVERNING_PASS token == first non-negated one), so no non-negated
    # coverage item changes.
    dv_idx = next((k for k, t in enumerate(toks)
                   if t in GOAL_GOVERNING_PASS and not _verb_negated_before(toks, k)), None)
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
        related = _class_relation(desired["classes"], cand["classes"]) is not None
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

    # Tier-1/Tier-2 literal class intersection OR (increment 1b) a Tier-3 pole comparison when the
    # actual/desired carries an ACQUIRED_* sentinel -- _class_relation is byte-identical to the prior
    # `same`/`opposed` computation for every non-sentinel pair.
    relation = _class_relation(desired["classes"], actual["classes"])
    if relation is None:
        return "NA", {"reason": "verb_class_unrelated", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if desired["referent"] is None or actual["referent"] is None:
        return "NA", {"reason": "referent_extraction_failed", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if link_tier not in LINK_TIERS:
        return "UNMET", {"reason": "referent_mismatch", "desired": desired, "actual": actual,
                         "link_tier": link_tier}
    if relation == "same":
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
    type_sentence_events_c3 above), PLUS the same TIER-2 open-vocab similarity fallback
    (_tier2_outcome_polarity_scan, 2026-08-06) for tokens OOV of the literal lexicon. Based on
    experiments/exp_outcome_valence_goal_congruence_v1.py::lexicon_predict."""
    t = normalize_tokens(outcome_sentence)
    has_unmet_t2, has_met_t2 = _tier2_outcome_polarity_scan(outcome_sentence)
    has_unmet = bool(t & V2_OUTCOME_UNMET) or has_unmet_t2
    has_met = bool(t & V2_OUTCOME_MET) or has_met_t2
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


# ============================================================================ CHANNEL B ADAPTER
# goal_congruence_appraisal_type (2026-08-06, online grounded-word-acquisition increment 1,
# preregs/2026-08-06_grounded_word_acquisition_increment1_v1.md). STRICT ADD: this function is
# consulted ONLY by hdlab.word_acquisition_loop's Channel B; NO existing call site changes behavior.
# It maps an outcome clause's GOAL-CONGRUENCE STRUCTURE onto one of the reward-simulation appraisal
# types RECIPROCITY (goal-completing) / BLOCK_HIGH (goal-thwarting) / None (insufficient or ambiguous
# structure -> abstain), using ONLY argument structure + animacy (+ an antecedent desiderative goal's
# referent when present) -- NEVER the target verb's own lexical identity and NEVER any text
# co-occurrence statistic of the target word. The VALENCE of the returned type is NOT decided here;
# the acquisition loop reads it downstream from the FROZEN reward-trained appraisal theta
# (context_grounded_valence.score_item's situation_type path -> Q(harm@coherent)-Q(help@coherent)).
# The completing/thwarting DECISION follows Talmy (1988) force dynamics, the SAME AGONIST_REALIZED-vs-
# AGONIST_BLOCKED axis hdlab.verb_lexical_similarity.OUTCOME_VERB_FEATURES tags its poles by (so this
# adapter is consistent with the module's own polarity typology, not an ad-hoc heuristic).
_CB_NOMINATIVE_PRONOUNS = {"i", "he", "she", "we", "they", "you", "who"}
_CB_INANIMATE_PRONOUNS = {"it", "this", "that", "these", "those"}
_CB_OBJECT_PRONOUNS = {"me", "him", "her", "us", "them", "myself", "himself", "herself",
                       "themselves", "itself", "ourselves", "yourself"}
_CB_RESULT_PARTICLES = {"up", "down", "off", "out", "away", "back"}
_CB_BE_AUX = {"is", "are", "was", "were", "be", "been", "being", "am", "get", "got", "gets"}
_CB_PREPS = {"to", "at", "on", "in", "of", "for", "with", "by", "from", "into", "onto", "upon",
             "over", "under", "through", "toward", "towards", "about", "after", "before", "against"}
_CB_CLAUSE_BOUNDARY = {"and", "but", "or", "nor", "yet", "so", "while", "when", "because", "if",
                       "though", "although", "as", "until", "till"}
# closed-class function words that never head a direct-object NP (used to reject non-noun tokens).
_CB_FUNCTION_WORDS = (_DET | _CB_PREPS | _CB_CLAUSE_BOUNDARY | _CB_BE_AUX | _CB_NOMINATIVE_PRONOUNS
                      | _CB_INANIMATE_PRONOUNS | _CB_RESULT_PARTICLES
                      | {"not", "very", "so", "then", "there", "here", "no", "nor", "too", "also",
                         "just", "only", "even", "still", "more", "most", "much", "well", "how",
                         "why", "where", "again", "ever", "never", "almost", "quite", "the"})

# OPTIONAL enrichment-atom vocabulary (increment 1b Section 4, behind the `enrich` flag threaded
# through _cb_analyze_outcome_clause / goal_congruence_appraisal_type below -- default OFF, so every
# existing caller and cert path is byte-identical). Beavers 2011 scalar affectedness (a quantized DO
# marks a telic, fully-affected result) + Kehler 2002 / Hobbs 1979 discourse-coherence pole cues.
_CB_QUANTIFIERS = {"some", "many", "much", "all", "every", "each", "no", "two", "three", "four",
                   "five", "six", "seven", "eight", "nine", "ten", "several", "few", "most", "both",
                   "another", "one"}
_CB_CONTRAST_CUES = {"but", "yet", "though", "although", "however"}
_CB_RESULT_CUES = {"and", "so", "then", "for"}


def _cb_discourse_pole_cue(toks, start, v_idx):
    """Discourse-coherence pole cue for the target clause (Kehler 2002, Hobbs 1979). A CONTRAST
    connective opening the clause (or 'however' inside it) votes REVERSAL relative to the clause-local
    force-dynamic trajectory; a RESULT/continuation connective votes continuation. Returns
    'CONTRAST' / 'CONTINUATION' / None."""
    if start > 0 and toks[start - 1] in _CB_CONTRAST_CUES:
        return "CONTRAST"
    if "however" in toks[start:v_idx]:
        return "CONTRAST"
    if start > 0 and toks[start - 1] in _CB_RESULT_CUES:
        return "CONTINUATION"
    return None


def _cb_token_is_animate_agent(tok_lower: str, tok_raw: str, idx: int) -> bool:
    """Surface animacy for a candidate subject token: nominative pronoun -> animate; inanimate
    pronoun -> inanimate; animacy_lexicon animate+agent_capable -> animate; non-sentence-initial
    capitalized token (proper noun) -> animate; else inanimate. Never consults the target verb."""
    if tok_lower in _CB_NOMINATIVE_PRONOUNS:
        return True
    if tok_lower in _CB_INANIMATE_PRONOUNS:
        return False
    from hdlab.animacy_lexicon import lookup_animacy
    info = lookup_animacy(tok_lower)
    if info is not None:
        return info.get("animacy") == "animate" and bool(info.get("agent_capable", False))
    if idx > 0 and tok_raw[:1].isupper():
        return True
    return False


def _cb_analyze_outcome_clause(outcome_sentence: str, target_lemma: str, enrich: bool = False):
    """Extract the target verb's local clause structure (subject animacy, direct-object presence,
    passive voice, result particle) around the FIRST token whose lemma == target_lemma. Returns None
    if the target verb is not found in the sentence. Glass-box surface parse, no external parser, no
    lemma-as-feature. `enrich` (increment 1b, default OFF -> byte-identical return dict) ADDS two
    optional keys -- `direct_object_is_quantized` and `discourse_pole_cue` -- consumed only by the
    enriched branch of goal_congruence_appraisal_type; the ablation runs both configs from this path."""
    toks = _tokens(outcome_sentence)
    raw = re.findall(r"[A-Za-z']+", outcome_sentence)
    if len(raw) != len(toks):
        raw = list(toks)
    v_idx = next((i for i, t in enumerate(toks) if lemma_verb(t) == target_lemma), None)
    if v_idx is None:
        return None
    start = 0
    for j in range(v_idx - 1, -1, -1):
        if toks[j] in _CB_CLAUSE_BOUNDARY:
            start = j + 1
            break
    subj_idxs = list(range(start, v_idx))
    animate_agent = any(
        _cb_token_is_animate_agent(toks[j], raw[j] if j < len(raw) else toks[j], j)
        for j in subj_idxs)
    subject_present = len(subj_idxs) > 0
    passive = any(toks[j] in _CB_BE_AUX for j in range(max(0, v_idx - 2), v_idx))
    result_particle = any(toks[k] in _CB_RESULT_PARTICLES
                          for k in range(v_idx + 1, min(len(toks), v_idx + 3)))
    # Direct object := the FIRST NP head after the verb (skipping determiners) is a bare accusative
    # NP, NOT introduced by a preposition. A preposition (or infinitival "to") ANYWHERE earlier in the
    # post-verb span makes the remaining constituent oblique (a PP), so "stood by the wooden gate" /
    # "walked to the well" have NO direct object while "caught the mousie" / "earned money" do. Glass-
    # box surface approximation (no chunker); may over-count a post-verbal adjective as an NP head.
    has_direct_object = False
    do_quantized = False
    saw_prep = False
    det_before = False
    for k in range(v_idx + 1, len(toks)):
        w = toks[k]
        if w in _CB_CLAUSE_BOUNDARY:
            break
        if w in _CB_PREPS or w == "to":
            saw_prep = True
            det_before = False
            continue
        if w in _DET or w in _CB_QUANTIFIERS:
            det_before = True
            continue
        if not saw_prep and (w in _CB_OBJECT_PRONOUNS
                             or (w not in _CB_FUNCTION_WORDS and len(w) >= 2)):
            has_direct_object = True
            do_quantized = (det_before or (k < len(raw) and raw[k][:1].isupper())
                            or w in _CB_OBJECT_PRONOUNS)
            break
        det_before = False
    result = {"v_idx": v_idx, "animate_agent": animate_agent, "subject_present": subject_present,
              "passive": passive, "result_particle": result_particle,
              "has_direct_object": has_direct_object}
    if enrich:
        result["direct_object_is_quantized"] = has_direct_object and do_quantized
        result["discourse_pole_cue"] = _cb_discourse_pole_cue(toks, start, v_idx)
    return result


def _cb_antecedent_goal_type(goal_sentences, clause):
    """If the goal_sentences carry an explicit desiderative goal whose referent LINKS to a
    class-related verb in the outcome clause, return RECIPROCITY (same-class completion) or BLOCK_HIGH
    (opposed-class thwarting). Reuses find_desired_state + _referent_links + the SUBJECT/OBJECT-is-
    referent class sets already in this module. Returns None when no explicit goal is present (the
    common case for bare corpus acquisition sentences)."""
    if not goal_sentences:
        return None
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    if desired is None or not desired.get("classes"):
        return None
    # A class-related outcome-clause verb whose referent links to the goal theme -> congruent.
    for cand in find_actual_state_candidates(clause):
        same = bool(desired["classes"] & cand["classes"])
        opposed = bool(_opposed_of(desired["classes"]) & cand["classes"])
        if not (same or opposed):
            continue
        linked, tier = _referent_links(desired["referent"], cand["referent"])
        if linked and tier in LINK_TIERS:
            return "RECIPROCITY" if same else "BLOCK_HIGH"
    return None


def goal_congruence_appraisal_type(goal_sentences, outcome_sentence: str, target_word: str,
                                   enrich: bool = False):
    """Channel B / 1b structural situation-typer. Returns "RECIPROCITY" (goal-completing), "BLOCK_HIGH"
    (goal-thwarting), or None (abstain). PURE STRUCTURE -- no target-verb identity, no target-word
    co-occurrence, and (unlike increment 1's downstream caller) NO reward-theta lookup: the caller maps
    RECIPROCITY->POS / BLOCK_HIGH->NEG directly (increment 1b, Section 1: the reward-theta was a fixed
    2-value sign constant, dropped as proven-redundant, not a capability loss). `goal_sentences` may be
    an empty list (bare-clause acquisition). `enrich` (default OFF -> byte-identical to increment 1's
    behavior) adds the Beavers-2011 quantized-DO realization atom + the Kehler/Hobbs CONTRAST pole flip.
    """
    target_lemma = lemma_verb(target_word)
    clause = _cb_analyze_outcome_clause(outcome_sentence, target_lemma, enrich=enrich)
    if clause is None:
        return None
    # (1) explicit antecedent-goal congruence, when the passage supplies a desiderative goal.
    g = _cb_antecedent_goal_type(goal_sentences, outcome_sentence)
    if g is not None:
        return g
    # (2) implicit force-dynamics reading of the outcome clause alone (Talmy agonist realized/blocked).
    agonist_realized = ((clause["animate_agent"] and clause["has_direct_object"])
                        or clause["passive"] or clause["result_particle"])
    if enrich and clause.get("direct_object_is_quantized"):
        agonist_realized = True   # a bounded/quantized DO independently marks a telic realized result
    agonist_blocked = (clause["subject_present"] and not clause["has_direct_object"]
                       and not clause["passive"] and not clause["result_particle"]
                       and not clause["animate_agent"])
    stype = None
    if agonist_realized and not agonist_blocked:
        stype = "RECIPROCITY"
    elif agonist_blocked and not agonist_realized:
        stype = "BLOCK_HIGH"
    if enrich and stype is not None and clause.get("discourse_pole_cue") == "CONTRAST":
        stype = "BLOCK_HIGH" if stype == "RECIPROCITY" else "RECIPROCITY"
    return stype


# ============================================================================ self-test
def self_test() -> dict:
    """Reproduces decisive cases from the source cells with THIS module's promoted (copied) organ,
    proving the promotion is byte-identical, not just similarly-shaped."""
    # (1) partition is disjoint by construction (all three goal-governing pass-classes vs the stop
    # set, and the pass-classes mutually -- 2026-08-06 coverage expansion invariant)
    assert DESIDERATIVE_PASS.isdisjoint(ASPECTUAL_STOP) and DESIDERATIVE_PASS.isdisjoint(OTHER_STOP_UNCHANGED)
    assert GOAL_GOVERNING_PASS.isdisjoint(PARTITIONED_STOP), "goal-governing union must be disjoint from stop set"
    assert DESIDERATIVE_PASS.isdisjoint(CONATIVE_PASS) and DESIDERATIVE_PASS.isdisjoint(INTENTION_PASS) \
        and CONATIVE_PASS.isdisjoint(INTENTION_PASS), "the three pass-classes must be mutually disjoint"

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

    # (5b) DECISIVE CASE (2026-08-06 coverage expansion): a CONATIVE "tried to VP" fires GOAL, and
    # the goal is recognized EVEN THOUGH THE ATTEMPT MAY FAIL (Talmy 1988 force-dynamics) -- goal
    # recognition is NOT outcome-typing. Precision guard: a bare-transitive "tried NP" (no
    # infinitival complement) must NOT fire.
    goal_tried = has_goal("Tom tried to steal sugar under his aunt's nose.", "tom")
    assert goal_tried is True, "conative 'tried to VP' must fire GOAL"
    tried_bare = has_goal("She tried the cake before dinner.", "she")
    assert tried_bare is False, "bare-transitive 'tried NP' (no infinitival) must NOT fire GOAL"
    assert find_desired_state("She tried the cake before dinner.") is None, (
        "bare-transitive 'tried the cake' must yield no desired-state (no 'to VP')")
    tried_state = find_desired_state("Tom tried to steal sugar under his aunt's nose.")
    assert tried_state is not None and tried_state["verb_lemma"] == "steal", (
        f"conative 'tried to steal' must recognize the goal-content verb 'steal', got {tried_state}")

    # (5c) DECISIVE CASE (2026-08-06 coverage expansion): an INTENTION "decided to VP" fires GOAL
    # (Bratman 1987 intention-vs-desire). Precision guard: a bare-transitive "decided NP" must NOT.
    goal_decided = has_goal("He decided to leave the village at once.", "he")
    assert goal_decided is True, "intention 'decided to VP' must fire GOAL"
    decided_bare = has_goal("He decided the matter without delay.", "he")
    assert decided_bare is False, "bare-transitive 'decided NP' (no infinitival) must NOT fire GOAL"

    # (5d) NEGATION-SCOPE GUARD (2026-08-06): a goal-governing verb that is itself NEGATED (do-
    # support / modal / "never" adjacency) signals a NEGATED/ABSENT goal -> abstain. Both the gated
    # goal-CONTENT recognizer (find_desired_state) and has_goal must decline.
    for _neg_sent, _neg_subj in [("She did not try to escape from the tower.", "she"),
                                 ("He never decided to leave the village.", "he"),
                                 ("She did not mean to intoxicate Diana.", "she"),
                                 ("He did not like to disturb her.", "he"),
                                 ("She didn't try to escape.", "she")]:
        assert find_desired_state(_neg_sent) is None, (
            f"negated goal-governing verb must abstain in find_desired_state: {_neg_sent!r}")
        assert has_goal(_neg_sent, _neg_subj) is False, (
            f"negated goal-governing verb must abstain in has_goal: {_neg_sent!r}")
    # PRECISION GUARD: negation on the COMPLEMENT ("tried NOT to cry") is an AVOIDANCE goal -- the
    # goal-holder still HAS a goal -- and MUST still fire (only the governing-verb negation suppresses).
    for _cn_sent, _cn_subj in [("He tried not to cry.", "he"), ("She decided not to go.", "she")]:
        assert find_desired_state(_cn_sent) is not None, (
            f"complement negation (avoidance goal) must still fire in find_desired_state: {_cn_sent!r}")
        assert has_goal(_cn_sent, _cn_subj) is True, (
            f"complement negation (avoidance goal) must still fire in has_goal: {_cn_sent!r}")
    # LITOTES: "not without ... hopes" is a positive goal (the negator is not adjacent to the
    # governing noun/verb) -- must NOT be over-suppressed.
    assert find_desired_state("she was not without secret hopes, and wanted to win") is not None, (
        "litotes 'not without ... hopes' must not be over-suppressed")

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

    # (9b) DECISIVE (2026-08-06 TIER-2 UPGRADE): shared-feature-similarity MET -- "ferry" resolves
    # to "vessel" via hdlab.lexical_similarity.concept_similarity (the lifted exp_n11c ATL-hub
    # organ, sim(vessel,ferry)=0.634 >= SIMILARITY_LINK_THRESHOLD=0.50), NOT a literal string match
    # and NOT the old hand-authored SYNONYM_GROUPS register (which this promotion removes).
    synfeat_met, synfeat_detail = congruence_decision(
        ["Grace wanted the ferry to sink so the insurers would pay out"], "The vessel sank")
    assert synfeat_met == "MET" and synfeat_detail["link_tier"] == "shared_feature", (
        f"goal=sink(ferry), outcome=sank(vessel) must be MET via shared_feature linking "
        f"(sim(vessel,ferry)=0.634 >= threshold), got {synfeat_met} ({synfeat_detail})")

    # (10) DECISIVE: over-link guard, genuinely-different-referent UNMET -- an ECM goal ("wanted his
    # SISTER to win") must NOT be satisfied by a different entity's same-class outcome ("his RIVAL
    # won"); sister and rival are BOTH in hdlab.lexical_similarity.CONCEPT_FEATURES (this is a
    # genuine sub-threshold measurement, sim(sister,rival)=0.398 < 0.50, not an OOV-fallthrough) and
    # still correctly do NOT link.
    diff_ref, diff_detail = congruence_decision(
        ["Owen wanted his sister to win the race before the whistle blew"], "His rival won the race")
    assert diff_ref == "UNMET" and diff_detail["reason"] == "referent_mismatch", (
        f"goal=win(sister) [ECM], outcome=won(rival) must be UNMET (over-link guard: sister!=rival, "
        f"sub-threshold shared-feature similarity), got {diff_ref} ({diff_detail})")
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
        "goal_tried_to_steal": goal_tried,
        "goal_tried_bare_transitive": tried_bare,
        "goal_decided_to_leave": goal_decided,
        "goal_decided_bare_transitive": decided_bare,
        "goal_action_frame_telos": goal_action_frame,
        "c3_only_misses_hoped": not any(r == R_GOAL for (_e, r) in c3_only_events),
        "outcome_valence": {
            "flip_unmet": flip_unmet, "flip_met": flip_met, "pronoun_referent_met": pron_met,
            "shared_feature_synonym_met": synfeat_met,
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
