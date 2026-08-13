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
    _SPEECH_VERBS as _COREF_SPEECH_VERBS,
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


def _tier2_outcome_polarity_scan(sentence: str, exclude_idxs=None):
    """Scan every ordered token of `sentence` that is OOV of the literal V2_OUTCOME_UNMET/_MET
    sets; lemmatize + Tier-2 classify each. Returns (has_unmet_t2, has_met_t2) -- either or both may
    fire (mirrors the existing Tier-1 has_unmet/has_met independence, which callers already
    disambiguate, e.g. lexicon_predict's AMBIGUOUS branch). `exclude_idxs` (ordered-token indices,
    default None) are skipped -- type_sentence_events_c3 passes a GOAL clause's own infinitival
    complement verb index here so the goal verb is not mis-read as an achieved outcome (2026-08-06
    bystander mis-bind fix, _goal_complement_verb_indices). None -> byte-identical to the pre-fix
    scan, so lexicon_predict (which passes no exclusion) is unchanged."""
    has_unmet_t2 = False
    has_met_t2 = False
    for idx, tok in enumerate(_ordered_tokens(sentence)):
        if exclude_idxs is not None and idx in exclude_idxs:
            continue
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
def c3_has_desire(sentence: str, exclude_idxs=None) -> bool:
    """True iff ANY token in `sentence` lemmatizes (hdlab.thematic_role_labeler.lemma_verb) to a
    verb that frame_primary_role (Component-3, production config: chosen_name=None, hypothesis=None
    -- identical to the conservative wire in hdlab/situation_reader.py) labels subj=EXPERIENCER,
    AND that EXPERIENCER token is not itself NEGATED. Based on
    experiments/exp_component5_wired_endtoend_v1.py::c3_has_desire; NO LONGER byte-identical --
    extended 2026-08-06 with the same do-support/modal/"never" negation-scope guard the construction
    path uses (_verb_negated_before), so a NEGATED desire state ("he did NOT like to VP") is not
    read as an active desire (that source cell keeps its own copy untouched as its historical
    source-of-truth). A non-negated EXPERIENCER fire ("he was WANTING attention") is unchanged.

    `exclude_idxs` (ordered-token indices, default None) are skipped -- type_sentence_events_c3
    passes the indices of tokens already CONSUMED as OUTCOME evidence here, so an outcome word is
    not ALSO read as a desire state (2026-08-13 self-satisfying-GOAL fix,
    _outcome_evidence_token_indices). None -> byte-identical to the pre-fix scan, so every other
    caller is unchanged. Exact mirror of _tier2_outcome_polarity_scan's own `exclude_idxs`
    parameter, which the 2026-08-06 bystander mis-bind fix added for the opposite direction."""
    toks = _ordered_tokens(sentence)
    for k, tok in enumerate(toks):
        if exclude_idxs is not None and k in exclude_idxs:
            continue
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
    V2_OUTCOME_UNMET/_MET lexicon -- strict ADD, Tier-1 exact membership always wins.

    GOAL-COMPLEMENT OUTCOME EXCLUSION (2026-08-06 bystander mis-bind fix): a GOAL clause's OWN
    purpose-infinitival complement verb ("X wanted to FIX...", "X longed to WIN...") IS the goal
    (find_desired_state's desired-state verb), never an achieved outcome, so its token is excluded
    from OUTCOME typing in BOTH tiers (Tier-2 skips the index; Tier-1 subtracts the surface form only
    when it occurs SOLELY at goal-complement positions -- a later recurrence elsewhere stays typed).
    See _goal_complement_verb_indices below.

    OUTCOME-EVIDENCE GOAL EXCLUSION (2026-08-13 self-satisfying-GOAL fix): the exact MIRROR of the
    above -- a token already CONSUMED as OUTCOME evidence must not ALSO mint GOAL evidence for the
    same clause, so those token indices are excluded from the EXPERIENCER (has_desire) scan. See
    _outcome_evidence_token_indices below."""
    events: List[Tuple[object, str]] = []
    excl = _goal_complement_verb_indices(sentence)
    has_desire = c3_has_desire(
        sentence, exclude_idxs=_outcome_evidence_token_indices(sentence, excl))
    has_unmet_t2, has_met_t2 = _tier2_outcome_polarity_scan(sentence, exclude_idxs=excl)
    t = _tokset(sentence) - _goal_complement_only_outcome_surface(sentence, excl)
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


# ============================================================================ GOAL-COMPLEMENT
# OUTCOME-TYPING EXCLUSION (2026-08-06 bystander mis-bind fix). BUG (flagged in the affect-bridge
# wiring, commit f99d1024f): a GOAL clause's OWN infinitival complement verb ("Jack wanted to FIX
# the fence", "Ruth longed to WIN the prize") was being read as an achieved OUTCOME_MET/UNMET by the
# outcome scans (Tier-1 lexicon set-membership and the Tier-2 open-vocab polarity scan), fabricating
# a spurious outcome event bound to the goal-holder. In the owner-selection path (hdlab.goal_owner_
# select.build_candidate_role_seq -> type_goal_events -> type_sentence_events_c3 here) that spurious
# outcome let a BYSTANDER passage -- whose real outcome belongs to NOBODY (the affect/praise is a
# bystander's, so both Tier-3 bridges correctly abstain) -- mis-bind an owner via the goal-clause
# verb instead of abstaining (OUTCOME_NEVER_TYPED). FIX (strict SUBTRACT, never adds an event): the
# "to VERB" complement of a GOAL_GOVERNING_PASS verb IS the goal (exactly find_desired_state's
# desired-state verb), never an outcome, so its token is excluded from outcome typing. PRECISION
# GUARD (load-bearing, do NOT over-exclude): only the goal-clause-INTERNAL complement token index is
# excluded; a LATER recurrence of the same verb elsewhere ("wanted to WIN" ... then "she WON the
# prize") is a genuine outcome and stays typed -- Tier-2 skips only the excluded index, Tier-1
# subtracts a surface form only when it occurs SOLELY at goal-complement positions.
def _goal_complement_verb_indices(sentence: str) -> set:
    """Ordered-token indices (_ordered_tokens) of the verb heading a GOAL_GOVERNING_PASS-governed
    purpose-infinitival 'to VP' -- the goal's OWN desired-state verb, which outcome-typing must not
    read as an achieved OUTCOME. Mirrors find_desired_state's non-negated-governing-verb + first
    'to VERB' scan (same [a-z']+ tokenization), collected for EVERY non-negated governing verb in the
    sentence (a slight superset of find_desired_state's single first-match, so a two-goal sentence is
    covered). A negated governing verb ('did not want to VP') is skipped exactly as find_desired_state
    skips it -- there is no active goal to protect there."""
    toks = _ordered_tokens(sentence)
    idxs: set = set()
    for k, t in enumerate(toks):
        if t not in GOAL_GOVERNING_PASS or _verb_negated_before(toks, k):
            continue
        for i in range(k + 1, len(toks) - 1):
            if toks[i] != "to" or toks[i + 1] in DET_STOP:
                continue
            idxs.add(i + 1)
            break
    return idxs


def _goal_complement_only_outcome_surface(sentence: str, excl: set) -> set:
    """V2-lexicon outcome surface forms that occur ONLY at a goal-complement index in `sentence` (so
    subtracting them from the Tier-1 token SET suppresses the spurious goal-complement outcome
    WITHOUT suppressing a genuine recurrence of the same surface elsewhere -- the precision guard for
    the set-based Tier-1 path, which cannot otherwise tell two occurrences of one surface apart). A
    surface that also appears at a non-excluded index is retained (returned NOT here)."""
    if not excl:
        return set()
    ordered = _ordered_tokens(sentence)
    non_excluded = {tok for k, tok in enumerate(ordered) if k not in excl}
    excluded_surface = {ordered[i] for i in excl if i < len(ordered)}
    return {s for s in (excluded_surface - non_excluded)
            if s in V2_OUTCOME_UNMET or s in V2_OUTCOME_MET}


# ============================================================================ OUTCOME-EVIDENCE
# GOAL-TYPING EXCLUSION (2026-08-13 self-satisfying-GOAL fix). The exact MIRROR IMAGE of the
# 2026-08-06 goal-complement guard directly above: that guard stops a GOAL clause's own complement
# verb from being read as an OUTCOME; this one stops an OUTCOME clause's own verb from being read as
# a GOAL. BUG: `miss`/`enjoy` sit in BOTH the EXPERIENCER psych frame (hdlab.thematic_role_labeler.
# PSYCH_VERBS -> frame_primary_role subj=EXPERIENCER) AND the outcome lexicon (V2_OUTCOME_UNMET /
# V2_OUTCOME_MET, and their Tier-2 similarity pools), so ONE token was consumed simultaneously as
# OUTCOME evidence and as GOAL evidence for the same clause. In the owner-selection path that
# fabricated GOAL is bound to whatever entity the CALLER hypothesizes for the outcome sentence, so
# hdlab.goal_owner_select.directed_goal_outcome_score's "does the outcome-slot entity also carry a
# GOAL" test is satisfied BY CONSTRUCTION for EVERY candidate (all score 1.0, delta 0.0, the
# adoption gate abstains and silently keeps the recency baseline). A discriminator whose evidence
# the candidate under test can mint is not a discriminator. FIX (strict SUBTRACT, never adds an
# event, symmetric in shape to _goal_complement_verb_indices): collect the ordered-token indices
# consumed as OUTCOME evidence and skip exactly those indices in the EXPERIENCER scan
# (c3_has_desire's `exclude_idxs`, the mirror of _tier2_outcome_polarity_scan's `exclude_idxs`).
# PRECISION GUARD (load-bearing, do NOT over-exclude), mirroring the goal-complement guard's
# "a later recurrence elsewhere stays typed": exclusion is BY INDEX, so a DIFFERENT, non-outcome
# EXPERIENCER token in the same clause ("she LOVED the fair, but she MISSED her turn") still mints
# GOAL normally -- only the dual-consumed token itself is silenced. NOT a lexicon edit: `miss` and
# `enjoy` stay in PSYCH_VERBS (they genuinely are psych verbs in their other sense); the rule is
# structural and fires for any current or future dual-listed token, Tier-1 or Tier-2.
def _outcome_evidence_token_indices(sentence: str, goal_complement_excl: set) -> set:
    """Ordered-token indices (_ordered_tokens) of the tokens CONSUMED as OUTCOME evidence by
    type_sentence_events_c3's has_unmet/has_met computation -- Tier-1 literal V2_OUTCOME_UNMET/_MET
    membership, plus Tier-2 open-vocab polarity (_outcome_polarity_tier2) for tokens OOV of Tier-1,
    exactly the two scans has_unmet/has_met are built from. `goal_complement_excl`
    (_goal_complement_verb_indices) is subtracted FIRST, in the same precedence the outcome scans
    themselves use: a goal clause's own complement verb is NOT outcome evidence there, so it must
    not be silenced as goal evidence here either (the two guards compose, they do not fight)."""
    toks = _ordered_tokens(sentence)
    idxs: set = set()
    for i, tok in enumerate(toks):
        if i in goal_complement_excl:
            continue
        if tok in V2_OUTCOME_UNMET or tok in V2_OUTCOME_MET:
            idxs.add(i)
            continue
        if _outcome_polarity_tier2(lemma_verb(tok)) is not None:
            idxs.add(i)
    return idxs


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

# ============================================================================ GOAL-VERB-RECURRENCE
# CHANNEL (2026-08-06, did-it-happen occurrence-gate build; preregs/
# 2026-08-06_did_it_happen_occurrence_gate_v1.md Check 1). A CLASS_REGISTRY-OOV outcome verb that is
# LEMMA-IDENTICAL to the antecedent goal's OWN desired verb ("the campaign MADE 400,000 pounds"
# recurring "wanted to MAKE a fund") is direct discourse evidence the desired action OCCURRED. Such an
# OOV verb otherwise gets no class and is silently dropped by find_actual_state_candidates' `if
# classes:` filter; the fix gives it a one-element RECURRENCE_SENTINEL so it survives as a candidate,
# and _class_relation reads a recurrence as "same" (the occurrence-gate in congruence_decision flips
# it to "opposed" iff that recurrence is itself negated). Structurally identical IN KIND to the
# ACQUIRED_* pole sentinels above -- it never fires unless the specific condition holds (outcome lemma
# == desired lemma, a content verb of len>3 not in the light/copula stop-list). Pure strict ADD:
# every existing caller passes desired_verb_lemma=None so the channel never fires -> byte-identical.
RECURRENCE_SENTINEL = "RECURRENCE_MATCH"
# Light/copula verbs that must NOT drive the recurrence channel (a coincidental recurrence of
# "was"/"had"/"said"/"got" is not evidence a contentful goal recurred). Reuses the aspectual seed
# lemmas (_GOAL_ASPECT_SEED_LEMMAS, defined above) plus the copula/light-verb closed set the design
# note names (be/do/have/say/get at minimum). NOTE: "make" is deliberately NOT excluded -- it is a
# genuine creation verb (onestop_hunt_crowdfunding's goal recurrence) and clears the len>3 gate; the
# stop-list was chosen from these principled classes, NOT tuned against eval-passage text (Check 5).
_RECURRENCE_LIGHT_VERB_STOP = set(_GOAL_ASPECT_SEED_LEMMAS) | {"be", "do", "have", "say", "get"}


def _is_recurrence(lemma: str, desired_verb_lemma: Optional[str]) -> bool:
    """True iff `lemma` should fire the goal-verb-recurrence channel against `desired_verb_lemma`:
    lemma-identical to the goal's OWN desired verb, a content verb (len>3), and not a light/copula
    verb. desired_verb_lemma=None (every legacy caller) -> always False -> byte-identical behavior."""
    return (desired_verb_lemma is not None and lemma == desired_verb_lemma
            and len(desired_verb_lemma) > 3
            and desired_verb_lemma not in _RECURRENCE_LIGHT_VERB_STOP)

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
    # RECURRENCE channel (2026-08-06 did-it-happen build): a RECURRENCE_SENTINEL means the actual
    # outcome verb is lemma-identical to the desired goal verb (a CLASS_REGISTRY-OOV recurrence) -> the
    # desired action recurred -> "same" by construction (the occurrence-gate in congruence_decision
    # then flips it to "opposed" iff the recurrence is itself negated). RECURRENCE_SENTINEL is never a
    # CLASS_REGISTRY member, so two pure-registry sets can never reach this branch.
    if RECURRENCE_SENTINEL in actual_classes or RECURRENCE_SENTINEL in desired_classes:
        return "same"
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

# QUOTE-ATTRIBUTION BOUNDARY (2026-08-07, referent-extraction repair for dialogue-final passages).
# _object_referent_after's forward object-NP scan previously stopped ONLY at _STOP_BOUNDARY / "to",
# so a trailing quotative-attribution tag with no intervening preposition ("...a heart," said the
# Tin Woodman) was NOT a stop point -- the scan ran past the true object NP and grabbed the speaker
# tag instead ("woodman" instead of "heart"). FIX: reuse hdlab.coreference_resolver's OWN quotative-
# attribution vocabulary (_SPEECH_VERBS, already the production primitive for "said/replied/asked
# NAME" detection) as an ADDITIONAL boundary set, rather than hand-authoring a second copy.
_QUOTE_ATTRIBUTION_VERBS = frozenset(_COREF_SPEECH_VERBS.split("|"))
_QUOTE_BOUNDARY = _STOP_BOUNDARY | _QUOTE_ATTRIBUTION_VERBS


def _tokens(sentence: str):
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


# DEICTIC NON-NOMINAL GUARD (2026-08-07, referent-recurrence regression fix): a bare deictic locative/
# temporal adverb ("here"/"there"/"now"/...) is grammatically NOT a noun phrase head -- it can only
# reach _np_last_content via an object-scan running past the true (pronoun/absent) object into an
# adjunct ("want to come HERE for" -> "here"). Disk-probed regression: ts_potter_failed_escape's
# desired referent extracted as "here" (from "wanted to come here"), which then falsely
# referent-recurred against a later "here" -> false MET (gold UNMET). General fix, not tuned to this
# one item: _np_last_content must never return a deictic adverb as an NP head.
_DEICTIC_NON_NOMINAL = {"here", "there", "now", "then", "today", "tomorrow", "yesterday"}


def _np_last_content(span):
    """Rightmost content token of an NP span, after stripping ONE leading determiner-equivalent (a
    closed DET set, or any token ending "'s" -- handles both "the old oak tree" (-> tree) and
    possessive "Owen's rival" (-> rival, not owen)). Returns None (not a real NP head) for a bare
    deictic locative/temporal adverb (_DEICTIC_NON_NOMINAL)."""
    toks = list(span)
    if toks and (toks[0] in _DET or toks[0].endswith("'s")):
        toks = toks[1:]
    if not toks:
        return None
    last = toks[-1]
    return None if last in _DEICTIC_NON_NOMINAL else last


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


# ============================================================================ REFERENT-EXTRACTION
# REPAIR (2026-08-06, did-it-happen occurrence-gate unblock; preregs/
# 2026-08-06_did_it_happen_occurrence_gate_v1.md). The occurrence-gate + recurrence channel (built at
# 7058d026b, strict-ADD, mechanism-correct) landed net-new-correct=0 on the real-prose eval because
# the signals were STARVED by two upstream referent-extraction gaps -- fixed here, still strict-ADD:
#
#   GAP-C (actual side): find_actual_state_candidates reads the pre-verb NP head as the referent via
#     _np_last_content(toks[:idx]). For a NEGATED outcome verb the do-support/negator/modal cluster
#     ("the boat DID NOT sink", "he DIDN'T come back") sits between the true subject and the verb, so
#     the rightmost pre-verb token is the negator/aux -> referent poisoned to "not"/"did" ->
#     congruence_decision discards the (correct) occurrence-gate flip at referent_mismatch. FIX: for a
#     negated verb, skip the contiguous pre-verbal negator/aux/transparent-adverb cluster before
#     taking the NP head. NON-negated extraction is BYTE-IDENTICAL (toks[:idx]) -- a genuinely
#     different referent still mismatches (precision guard).
#
#   GAP-B (desired side): an OOV control-verb goal ("wanted to FIND love") has no CLASS_REGISTRY
#     class, so neither SUBJECT_IS_REFERENT nor OBJECT_IS_REFERENT applied and the referent was left
#     None -> the recurrence "same-referent" match died at referent_extraction_failed even when the
#     outcome recurred the goal verb. FIX: extract the object NP after the embedded verb (the goal's
#     THEME) for the OOV control case -- symmetric with the recurrence channel's actual-side object
#     theme below. Conservative: only fills a slot that was None; never overrides an existing referent.
_PREVERBAL_AUX = {
    "did", "do", "does", "will", "would", "shall", "should", "can", "could", "may", "might",
    "must", "have", "has", "had", "is", "are", "was", "were", "be", "been", "being", "am",
}


def _subject_span_skipping_preverbal_aux(toks: List[str], v_idx: int) -> List[str]:
    """Pre-verb subject-NP span for a NEGATED verb (GAP-C): step left from v_idx-1 over the
    contiguous pre-verbal negator / do-support-modal-copula auxiliary / transparent-adverb cluster
    and return toks up to (and excluding) that cluster, so "the boat did not sink" -> ["the","boat"].
    Only called when _verb_negated_before(toks, v_idx) is True; non-negated extraction stays
    byte-identical (the caller passes toks[:v_idx] in that case)."""
    j = v_idx - 1
    while j >= 0 and (_is_negator(toks[j]) or toks[j] in _PREVERBAL_AUX
                      or toks[j] in _NEG_TRANSPARENT_ADVERBS):
        j -= 1
    return toks[:j + 1]


def _object_referent_after(toks: List[str], v_idx: int) -> Optional[str]:
    """Head of the direct-object NP immediately after toks[v_idx] (walk forward to the first
    _QUOTE_BOUNDARY token, "to", or _PREVERBAL_AUX token), or None when there is no such NP ("tried to
    intercede FOR anne" -> None). Same span logic find_desired_state already uses for
    OBJECT_IS_REFERENT_CLASSES, factored here so both the GAP-B desired side and the recurrence-channel
    actual side compare the same THEME (object) of the recurred action. Boundary widened 2026-08-07
    from _STOP_BOUNDARY to _QUOTE_BOUNDARY (adds quotative-attribution verbs) so a dialogue-final NP
    doesn't run on into "...," said X -- see _QUOTE_BOUNDARY docstring above. FINITE-CLAUSE GUARD
    (2026-08-07, referent-recurrence regression fix): also stop at a _PREVERBAL_AUX token (modal/aux/
    copula -- the SAME closed set _subject_span_skipping_preverbal_aux already reuses) -- a modal/
    copula inside the span marks the start of a SEPARATE finite clause (a comparative/adverbial, e.g.
    "cover it just as much as COULD be, Diana"), not a continuation of the direct-object NP; without
    this guard the scan ran past the true (pronoun) object into a trailing vocative and returned the
    vocative name as the "referent" (disk-probed regression: agg_anne_pudding_sauce_mouse_ch16's
    desired referent was extracted as "diana", a vocative address, not a real goal target -- false
    MET once referent-recurrence found "Diana" mentioned again downstream). Byte-identical for every
    span that doesn't reach a speech verb or preverbal-aux token (the only NEW stop points)."""
    j = v_idx + 1
    while j < len(toks) and toks[j] not in _QUOTE_BOUNDARY and toks[j] != "to" \
            and toks[j] not in _PREVERBAL_AUX:
        j += 1
    return _np_last_content(toks[v_idx + 1:j])


# ============================================================================ REFERENT-EXTRACTION
# REPAIR PART 2 (2026-08-07, referent-recurrence unblock; extends the 2026-08-06 GAP-B/GAP-C repair
# above). Two more find_desired_state referent bugs, both real-prose-probed:
#
#   ECM-DITRANSITIVE-THEME: "I want HIM to give me a heart" -- the ECM subject ("him") is NOT who
#     changes state for a transfer-of-possession embedded verb; the THEME being transferred ("heart")
#     is the did-it-happen-relevant referent. SUBJECT_IS_REFERENT_CLASSES/OBJECT_IS_REFERENT_CLASSES
#     already encode this subject-vs-object distinction for CONTROL, but ECM's `between` span is
#     ALWAYS read as the referent today regardless of the embedded verb's argument structure -- wrong
#     specifically for a small closed class of transfer verbs (give/hand/bring/...). SUPPLY register
#     (hand-authored, same convention as CLASS_REGISTRY -- NOT induced/tuned against eval text).
TRANSFER_CLASS = {"give", "hand", "bring", "send", "offer", "grant", "pay", "pass", "return",
                   "award", "present", "deliver", "donate"}

#   ECM-COPULA: "My greatest WISH now ... IS to get back to Kansas" -- "wish" here is a NOUN (subject
#     of a copular predicate), not a verb governing an ECM-subject infinitival. The naive `between`
#     span ("now Dorothy added is") spans an entire intervening clause and ends at the copula itself,
#     so _np_last_content(between) grabs "is" -- not a referent at all. FIX: when `between`'s last
#     token is a copula form, this is NOT a true ECM embedding; treat it like CONTROL (referent comes
#     from the embedded verb's own complement, not from `between`).
_ECM_COPULA_FORMS = {"is", "are", "was", "were", "be", "been", "being", "am"}
# Motion particles a destination PP can follow ("get BACK TO Kansas") -- the "to" there heads a
# destination PP, not a new infinitival clause, so the object-NP scan must not stop at it. Reuses
# DIRECTIONAL_PP (already-existing constant) plus "back" (not in DIRECTIONAL_PP, common in this
# construction); scoped to its own local set so the shared DIRECTIONAL_PP / _object_referent_after
# semantics used elsewhere (action_frame_feats's has_directional_pp feature) are untouched.
_PP_CONTINUATION_PARTICLES = DIRECTIONAL_PP | {"back"}


def _object_referent_after_pp_aware(toks: List[str], v_idx: int) -> Optional[str]:
    """Variant of _object_referent_after that does not stop at a "to" immediately preceded by a
    _PP_CONTINUATION_PARTICLES word -- that "to" heads a destination PP ("get BACK TO Kansas"), not a
    new infinitival clause, so the scan must continue through it to reach the real destination NP.
    Used ONLY by the ECM-copula referent fallback below (narrow, additive; the shared
    _object_referent_after stays byte-identical for every existing caller)."""
    j = v_idx + 1
    while j < len(toks) and toks[j] not in _QUOTE_BOUNDARY:
        if toks[j] == "to" and not (j > v_idx + 1 and toks[j - 1] in _PP_CONTINUATION_PARTICLES):
            break
        j += 1
    return _np_last_content(toks[v_idx + 1:j])


# ============================================================================ DIALOGUE-GOAL
# CONSTRUCTIONS (2026-08-07). find_desired_state's scan above requires a GOAL_GOVERNING_PASS verb
# followed by an infinitival "to VP" -- but dialogue expresses a goal through two other constructions
# that shape never covers:
#
#   HEDGED-MODAL WISH: "I wish I might open the gate" / "I wish we could get him out" -- a FINITE
#     modal complement ("wish [SUBJ] might/could/would VP"), not an infinitival. "wish" is already
#     GOAL_GOVERNING_PASS (DESIDERATIVE_PASS), so dv_idx above finds it, but the existing for-loop
#     only looks for "to" and finds none here -> falls through to the original `return None`.
#
#   REQUEST: "let me/us VP", "may/might/can I VP", "will you (not) VP", "please VP" -- an
#     illocutionary request IS the requester's goal (Searle 1969 directive speech acts: a request
#     expresses the speaker's desire that the addressee bring about VP). No GOAL_GOVERNING_PASS verb
#     governs this shape at all ("let"/"may"/"will"/"please" are not in that set), so dv_idx is None
#     and the ORIGINAL scan never even starts.
#
# Both are wired as ADDITIONAL fallback passes tried only after the existing GOAL_GOVERNING_PASS +
# "to VP" scan has already returned nothing (see find_desired_state below) -- a pure strict ADD: any
# sentence the existing scan already resolves is untouched (these passes are never consulted), so
# every already-passing coverage/recall/precision number stays exactly as measured.
#
# OVER-FIRE GUARDS (load-bearing -- requests/wishes are common; not every one is the protagonist's
# own goal):
#   - HEDGED_MODAL_WISH fires only for a FIRST-PERSON embedded subject ("i"/"we") -- "I wish YOU
#     would stop" is a wish about someone ELSE's behavior, not the speaker's own action-goal.
#   - REQUEST fires only on first-/second-person forms that request something FOR the speaker:
#     a light/discourse-filler verb immediately governed by the request ("let me THINK", "may I
#     SAY", "let me TELL you") is a conversational aside, not a real-world action goal
#     (_REQUEST_DISCOURSE_STOP, SUPPLY -- the closed cognition/speech-act class, not tuned to one
#     item); a request whose object is the 2nd-person addressee ("may I help YOU", "let me help
#     you") is an OFFER to the addressee, not the speaker's own goal
#     (_request_object_is_addressee); "will you (not) VP" additionally requires VP's own object to
#     be "me"/"us" (the request explicitly names something the SPEAKER receives), which is what
#     excludes rhetorical/command uses with no such object ("will you be quiet", "will you stop
#     that").
_HEDGE_MODALS = {"might", "could", "would"}
_HEDGE_SUBJ_MAX_SPAN = 6
_WISH_FORMS = {"wish", "wishes", "wished", "wishing"}
assert _WISH_FORMS <= DESIDERATIVE_PASS, "wish forms must stay a subset of DESIDERATIVE_PASS"

_REQUEST_ME_PRONOUNS = {"me", "us"}
_REQUEST_MODALS_1P = {"may", "might", "can"}
# Cognition/speech-act light verbs that read as a conversational filler ("let me THINK", "may I
# SAY", "let me TELL you") rather than a real-world action goal when directly governed by a
# REQUEST construction. SUPPLY, hand-authored closed class (same convention as CLASS_REGISTRY /
# DESIDERATIVE_PASS) -- deliberately NOT the recurrence channel's _RECURRENCE_LIGHT_VERB_STOP (that
# set includes "get", which is a genuine content verb in a request -- "let me GET my coat" -- and
# must NOT be suppressed here).
_REQUEST_DISCOURSE_STOP = {"think", "tell", "say", "know", "ask", "see", "explain", "mention",
                           "guess", "wonder"}


def _request_object_is_addressee(toks: List[str], verb_idx: int) -> bool:
    """True iff the embedded verb's direct object is the 2nd-person addressee ("you") -- an OFFER
    ("may I help YOU", "let me help you"), not a request for something the SPEAKER wants. Reuses the
    existing object-NP scan (_object_referent_after) rather than a second hand-rolled one."""
    return _object_referent_after(toks, verb_idx) == "you"


def _find_hedged_modal_wish(toks: List[str]):
    """HEDGED-MODAL WISH: "wish [i/we] might/could/would VP" -- see section docstring above. Returns
    the same {referent, classes, verb_lemma, pattern} contract as find_desired_state, or None.
    Referent extraction reuses the SAME SUBJECT_IS_REFERENT_CLASSES / OBJECT_IS_REFERENT_CLASSES
    branching find_desired_state's CONTROL pattern already uses (the embedded verb's own class
    decides subject-changes-state vs object-changes-state); OOV embedded verbs default to the
    object-NP scan, exactly the GAP-B fallback convention used elsewhere in this module."""
    for k, t in enumerate(toks):
        if t not in _WISH_FORMS or _verb_negated_before(toks, k):
            continue
        j = k + 1
        while (j < len(toks) and toks[j] not in _HEDGE_MODALS
               and toks[j] not in _STOP_BOUNDARY and (j - k) <= _HEDGE_SUBJ_MAX_SPAN):
            j += 1
        if j >= len(toks) or toks[j] not in _HEDGE_MODALS:
            continue
        subj_span = toks[k + 1:j]
        if subj_span not in (["i"], ["we"]):   # first-person-only over-fire guard
            continue
        v_idx = j + 1
        if v_idx >= len(toks):
            continue
        embedded_lemma = lemma_verb(toks[v_idx])
        classes = _verb_classes(embedded_lemma)
        if classes & SUBJECT_IS_REFERENT_CLASSES:
            referent = _np_last_content(subj_span)
        else:
            referent = _object_referent_after(toks, v_idx)
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": "HEDGED_MODAL_WISH"}
    return None


def _find_request_goal(toks: List[str]):
    """REQUEST constructions -- see section docstring above. Returns the same
    {referent, classes, verb_lemma, pattern} contract as find_desired_state, or None. Tries, in
    order: "let me/us VP", "may/might/can I VP", "will you (not) VP" (gated to a VP whose own object
    is "me"/"us"), "please VP"."""
    n = len(toks)
    for k, t in enumerate(toks):
        if t != "let" or k + 2 >= n or toks[k + 1] not in _REQUEST_ME_PRONOUNS:
            continue
        v_idx = k + 2
        if toks[v_idx] in _REQUEST_DISCOURSE_STOP or _request_object_is_addressee(toks, v_idx):
            continue
        embedded_lemma = lemma_verb(toks[v_idx])
        classes = _verb_classes(embedded_lemma)
        requester = toks[k + 1]
        referent = requester if classes & SUBJECT_IS_REFERENT_CLASSES \
            else _object_referent_after(toks, v_idx)
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": "REQUEST_LET"}
    for k, t in enumerate(toks):
        if t not in _REQUEST_MODALS_1P or k + 2 >= n or toks[k + 1] != "i":
            continue
        v_idx = k + 2
        if toks[v_idx] in _REQUEST_DISCOURSE_STOP or _request_object_is_addressee(toks, v_idx):
            continue
        embedded_lemma = lemma_verb(toks[v_idx])
        classes = _verb_classes(embedded_lemma)
        referent = "i" if classes & SUBJECT_IS_REFERENT_CLASSES \
            else _object_referent_after(toks, v_idx)
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": "REQUEST_MODAL_1P"}
    for k, t in enumerate(toks):
        if t != "will" or k + 1 >= n or toks[k + 1] != "you":
            continue
        v_idx = k + 2
        if v_idx < n and toks[v_idx] in NEGATORS:   # "will you NOT VP" -- still a positive request
            v_idx += 1
        if v_idx >= n or toks[v_idx] in _REQUEST_DISCOURSE_STOP:
            continue
        obj = _object_referent_after(toks, v_idx)
        if obj not in _REQUEST_ME_PRONOUNS:   # excludes "will you be quiet" / "will you stop that"
            continue
        embedded_lemma = lemma_verb(toks[v_idx])
        classes = _verb_classes(embedded_lemma)
        return {"referent": obj, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": "REQUEST_WILL_YOU"}
    for k, t in enumerate(toks):
        if t != "please" or k + 1 >= n:
            continue
        v_idx = k + 1
        if toks[v_idx] in _REQUEST_DISCOURSE_STOP or _request_object_is_addressee(toks, v_idx):
            continue
        embedded_lemma = lemma_verb(toks[v_idx])
        classes = _verb_classes(embedded_lemma)
        referent = "i" if classes & SUBJECT_IS_REFERENT_CLASSES \
            else _object_referent_after(toks, v_idx)
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": "REQUEST_PLEASE"}
    return None


def _find_purpose_infinitival(toks: List[str], dv_idx: int):
    """The original GOAL_GOVERNING_PASS + infinitival "to VERB" scan, unchanged (extracted verbatim
    out of find_desired_state below so the 2026-08-07 dialogue-goal fallback passes can be tried when
    this one finds nothing, without touching a single byte of this scan's own logic)."""
    for i in range(dv_idx + 1, len(toks) - 1):
        if toks[i] != "to" or toks[i + 1] in DET_STOP:
            continue
        embedded_lemma = lemma_verb(toks[i + 1])
        classes = _verb_classes(embedded_lemma)
        between = toks[dv_idx + 1:i]
        between_is_copula_predicate = bool(between) and between[-1] in _ECM_COPULA_FORMS
        if between and not between_is_copula_predicate:
            pattern = "ECM"
            candidate_referent = _np_last_content(between)
            # INVALID-ECM-REFERENT GUARD (2026-08-07): a dropped numeric token ("decided IN [2013] to
            # see") can strand a bare preposition/function word as the "between" NP head -- not a real
            # referent (candidate_referent in _STOP_BOUNDARY). DITRANSITIVE-TRANSFER GUARD: for a
            # transfer-of-possession embedded verb, the referent that matters is the THEME being
            # transferred (the embedded verb's own direct object), not the ECM subject in `between`.
            if (candidate_referent is None or candidate_referent in _STOP_BOUNDARY
                    or embedded_lemma in TRANSFER_CLASS):
                referent = _object_referent_after(toks, i + 1)
            else:
                referent = candidate_referent
        else:
            # ECM-COPULA (2026-08-07): between_is_copula_predicate -- a copular predicate ("wish ...
            # IS to VP"), not a true ECM embedding; fall through to the embedded verb's own complement
            # exactly like CONTROL, with a PP-aware object scan (get BACK TO Kansas) as the final
            # fallback. between empty -> ordinary CONTROL, byte-identical to before.
            pattern = "ECM_COPULA" if between_is_copula_predicate else "CONTROL"
            if classes & SUBJECT_IS_REFERENT_CLASSES:
                referent = _np_last_content(toks[:dv_idx])
            elif classes & OBJECT_IS_REFERENT_CLASSES:
                j = i + 2
                while j < len(toks) and toks[j] not in _STOP_BOUNDARY and toks[j] != "to":
                    j += 1
                referent = _np_last_content(toks[i + 2:j])
            elif between_is_copula_predicate:
                referent = _object_referent_after_pp_aware(toks, i + 1)
            else:
                # GAP-B (2026-08-06): OOV control verb (no CLASS_REGISTRY class) -- extract the object
                # NP theme ("wanted to FIND love" -> "love") so the goal-verb-recurrence channel can
                # link, instead of leaving the referent None. None-safe (stays None when no object NP).
                referent = _object_referent_after(toks, i + 1)
        return {"referent": referent, "classes": classes, "verb_lemma": embedded_lemma,
                "pattern": pattern}
    return None


def find_desired_state(sentence: str):
    """Locate a goal-bearing construction and extract {referent, classes, verb_lemma, pattern}, or
    None if no goal is found. Tries, in order: (1) the original GOAL_GOVERNING_PASS (desiderative |
    conative | intention) purpose-infinitival "to VERB" scan (_find_purpose_infinitival, byte-
    identical to experiments/exp_outcome_valence_goal_congruence_v1.py::find_desired_state; the
    governing-verb gate widened 2026-08-06 from DESIDERATIVE_PASS alone to the GOAL_GOVERNING_PASS
    union -- adds try/decide/determine/like/love + gerund forms; referent extraction extended
    2026-08-07 with the ECM-ditransitive-theme, ECM-copula, and invalid-function-word-referent
    repairs above); then, ONLY when that finds nothing, (2) the HEDGED-MODAL WISH construction
    ("wish [i/we] might/could/would VP") and (3) the REQUEST construction ("let me/us VP",
    "may/might/can I VP", "will you (not) VP", "please VP") -- both added 2026-08-07, see the
    DIALOGUE-GOAL CONSTRUCTIONS section above _find_hedged_modal_wish for the full rationale and
    over-fire guards. Strict ADD: any sentence (1) already resolves is returned unchanged from (1),
    so every existing coverage/recall/precision number this module reproduces is untouched."""
    toks = _tokens(sentence)
    # NEGATION-SCOPE GUARD (2026-08-06): iterate governing-verb occurrences and SKIP one whose verb
    # is itself negated (do-support / modal / "never" adjacency, _verb_negated_before) -- a negated
    # goal is ABSENT, not active -- recognizing from the first NON-negated governing verb instead.
    # When no governing verb is negated this is behaviourally identical to the prior first-match
    # next(...) logic (first GOAL_GOVERNING_PASS token == first non-negated one), so no non-negated
    # coverage item changes.
    dv_idx = next((k for k, t in enumerate(toks)
                   if t in GOAL_GOVERNING_PASS and not _verb_negated_before(toks, k)), None)
    if dv_idx is not None:
        purpose_inf = _find_purpose_infinitival(toks, dv_idx)
        if purpose_inf is not None:
            return purpose_inf
    hedged = _find_hedged_modal_wish(toks)
    if hedged is not None:
        return hedged
    return _find_request_goal(toks)


def find_actual_state_candidates(sentence: str, desired_verb_lemma: Optional[str] = None):
    """ALL class-match verb occurrences in `sentence`, left-to-right (not just the first -- needed so
    congruence_decision below can prefer a LATER goal-relevant clause over an EARLIER same-class
    DISTRACTOR clause, e.g. "The workshop flooded and the shed collapsed." must not resolve to
    'workshop' just because 'flooded' is scanned first). Extended 2026-08-06 (did-it-happen build,
    strict ADD): every candidate carries a `negated` key (_verb_negated_before reused verbatim, the
    SAME do-support/modal/"never" adjacency scanner already used on the GOAL side) so
    congruence_decision's occurrence-gate can flip same<->opposed when the outcome verb is negated;
    and a CLASS_REGISTRY-OOV token lemma-identical to `desired_verb_lemma` (the recurrence channel,
    _is_recurrence guard) becomes a candidate via a RECURRENCE_SENTINEL. desired_verb_lemma=None
    (every legacy caller: find_actual_state, _cb_antecedent_goal_type) -> no recurrence candidate ever
    added; the `negated` key is purely additive -> byte-identical candidate SET for legacy callers.
    Base scan otherwise byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v2.py::find_actual_state_candidates."""
    toks = _tokens(sentence)
    out = []
    for idx, t in enumerate(toks):
        lemma = lemma_verb(t)
        classes = _verb_classes(lemma)
        is_recur = False
        if not classes and _is_recurrence(lemma, desired_verb_lemma):
            classes = {RECURRENCE_SENTINEL}
            is_recur = True
        if classes:
            negated = _verb_negated_before(toks, idx)
            # GAP-C (2026-08-06): for a NEGATED verb, skip the pre-verbal negator/aux cluster so the
            # subject NP head is read (not "not"/"did"); byte-identical span toks[:idx] otherwise.
            subj_span = _subject_span_skipping_preverbal_aux(toks, idx) if negated else toks[:idx]
            subj_ref = _np_last_content(subj_span)
            out.append({"referent": subj_ref, "classes": classes, "verb_lemma": lemma,
                        "verb_idx": idx, "negated": negated})
            # RECURRENCE THEME SYMMETRY (2026-08-06): a recurred TRANSITIVE action's theme is its
            # OBJECT ("found LOVE" recurring "find LOVE"); a recurred INTRANSITIVE action's theme is
            # its SUBJECT ("Davey PITCHED"). Robustly telling the two apart needs a parser we do not
            # have, so emit BOTH referents as sibling recurrence candidates (subject first, preserving
            # legacy order + the intransitive case; then the object theme) and let congruence_decision
            # Pass-1 link on whichever matches the goal's theme. Strict-ADD: recurrence candidates
            # exist only when desired_verb_lemma is threaded (never for legacy callers), so no
            # class-candidate set changes and every legacy candidate SET is byte-identical.
            if is_recur:
                obj_ref = _object_referent_after(toks, idx)
                if obj_ref is not None and obj_ref != subj_ref:
                    out.append({"referent": obj_ref, "classes": classes, "verb_lemma": lemma,
                                "verb_idx": idx, "negated": negated})
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
    # Thread the goal's OWN desired verb lemma so the recurrence channel (did-it-happen build) can
    # admit a CLASS_REGISTRY-OOV outcome verb that recurs the goal verb; None-safe for OOV desired.
    candidates = find_actual_state_candidates(outcome_sentence, desired.get("verb_lemma"))
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
    # OCCURRENCE-GATE (2026-08-06 did-it-happen build): a NEGATED actual outcome verb inverts the
    # occurrence polarity -- the wanted THING lexically appears but did NOT actually happen. Pure XOR
    # flip of same<->opposed; fires ONLY when relation is already not None, so it can never create a
    # MET/UNMET out of a class-unrelated candidate (the NA/abstain path is untouched). Uses the SAME
    # negation-scope readout (_verb_negated_before, recorded per candidate as `negated`) the goal side
    # already uses -- distinct discourse-occurrence readout, not a lexical-pole fact.
    occurrence_gate_fired = False
    if relation is not None and actual.get("negated"):
        relation = "opposed" if relation == "same" else "same"
        occurrence_gate_fired = True
    if relation is None:
        return "NA", {"reason": "verb_class_unrelated", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if desired["referent"] is None or actual["referent"] is None:
        return "NA", {"reason": "referent_extraction_failed", "desired": desired, "actual": actual,
                      "link_tier": link_tier}
    if link_tier not in LINK_TIERS:
        return "UNMET", {"reason": "referent_mismatch", "desired": desired, "actual": actual,
                         "link_tier": link_tier, "occurrence_gate_fired": occurrence_gate_fired}
    if relation == "same":
        return "MET", {"reason": "same_class_same_referent", "desired": desired, "actual": actual,
                       "link_tier": link_tier, "occurrence_gate_fired": occurrence_gate_fired}
    return "UNMET", {"reason": "opposed_class_same_referent", "desired": desired, "actual": actual,
                     "link_tier": link_tier, "occurrence_gate_fired": occurrence_gate_fired}


def congruence_outcome_valence(passage_text: str):
    """Top-level entry: split `passage_text` into sentences (this module's own _sentences), goal-
    sentences = all but the last, outcome-sentence = the last. Byte-identical to
    experiments/exp_outcome_valence_goal_congruence_v1.py::congruence_outcome_valence."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    return congruence_decision(sents[:-1], sents[-1])


def congruence_outcome_valence_windowed(passage_text: str, max_window: int = 4):
    """WINDOW-WIDENING companion (2026-08-06 did-it-happen build; preregs/
    2026-08-06_did_it_happen_occurrence_gate_v1.md Check 4). Same contract as
    congruence_outcome_valence, but the outcome sentence is chosen by a candidate-nonempty BACKWARD
    scan instead of the unconditional sents[-1]: step from the nearest-to-end sentence backward (up to
    max_window) and use the FIRST one that yields >=1 outcome candidate. This closes GAP-1 -- real
    narrative resolution clauses are frequently followed by a trailing reaction/dialogue sentence, so
    sents[-1] often has no outcome verb at all and congruence_outcome_valence abstains no matter how
    good the occurrence-gate is.

    STRICT-WIDEN / byte-identical-fallback property: the candidate-nonempty gate is threaded with the
    goal's OWN desired verb lemma (so a recurrence-only true clause is detected, not skipped -- the
    onestop_limal 'found'==goal 'find' case), and when sents[-1] already yields >=1 candidate the loop
    returns at k=1 immediately, i.e. congruence_decision(goal_sentences, sents[-1]) -- byte-identical
    to congruence_outcome_valence for every already-typed passage. The loop only steps backward when
    the closest-to-end sentence is candidate-EMPTY. Named risk (measured eval-wide, Check 4): stepping
    backward could pick an earlier, coincidentally-class-related clause; the non-regression sweep is
    over the FULL 44-item eval, not just the OOV subset."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    goal_sentences = sents[:-1]
    # Resolve the antecedent goal ONCE so the candidate-nonempty gate can admit a recurrence-only
    # clause (find_actual_state_candidates with the goal's desired verb lemma). None-safe.
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    dvl = desired.get("verb_lemma") if desired is not None else None
    for k in range(1, min(max_window, len(sents) - 1) + 1):
        outcome_sentence = sents[-k]
        if find_actual_state_candidates(outcome_sentence, dvl):
            return congruence_decision(goal_sentences, outcome_sentence)
    return congruence_decision(goal_sentences, sents[-1])   # byte-identical fallback


# ============================================================================ REFERENT-RECURRENCE
# CHANNEL (2026-08-07, did-it-happen build, sibling of the GOAL-VERB-RECURRENCE channel above). The
# verb-recurrence channel (RECURRENCE_SENTINEL) types MET/UNMET when the OUTCOME reuses the goal's own
# VERB. Several real-prose items never recur the verb at all (goal "give a heart", outcome "put the
# heart in") -- the goal's REFERENT (its TARGET noun, now correctly extracted per the 2026-08-07 A3
# repair above) recurs instead. This channel is deliberately built as a SEPARATE top-level pass (NOT
# spliced into find_actual_state_candidates/congruence_decision) so it can be added as a pure
# ADDITIONAL fallback tier with zero risk to the existing verb-class Pass-1/occurrence-gate/
# verb-recurrence machinery (fully isolated new code path; congruence_decision, find_actual_state_
# candidates, and _referent_links are UNTOUCHED by this section).
#
# SUPPLY, innate-core noun-concept register (2026-08-07) -- same "hand-authored, not induced/tuned
# against eval text" convention as CLASS_REGISTRY, extended to a small common-sense NOUN class the
# existing 89-concept hdlab.lexical_similarity.CONCEPT_FEATURES lexicon does not cover. Generalizes to
# any money/funding passage, not specific to one eval item's wording.
MONEY_CLASS = {"money", "funding", "fund", "funds", "cash", "pound", "pounds", "dollar", "dollars",
               "euro", "euros"}
NOUN_CONCEPT_CLASSES = {"MONEY_CLASS": MONEY_CLASS}

# OVER-FIRE GUARD: light/vague/pronoun/gerund referents must never drive this channel (a coincidental
# recurrence of "it"/"something"/"one" is not evidence the goal's target recurred). Reuses
# _RECURRENCE_LIGHT_VERB_STOP (already-defined light-verb-adjacent closed set) plus a small explicit
# vague-pronoun set; the gerund-suffix + is_pronoun_mention checks are GENERAL (not a hand list).
_REFERENT_RECURRENCE_STOP = _RECURRENCE_LIGHT_VERB_STOP | {
    "something", "someone", "somebody", "anything", "anybody", "everything", "everybody",
    "nothing", "one", "it",
}
_REFERENT_RECURRENCE_MIN_LEN = 3


def _referent_recurrence_eligible(referent: Optional[str]) -> bool:
    """True iff `referent` is specific enough to drive the referent-recurrence channel: not None, not
    too short, not a light/vague-pronoun noun (_REFERENT_RECURRENCE_STOP), not gerund-shaped (a
    generic morphological guard against gerund referents that are almost always an extraction
    artifact, not a real target), and not a bare pronoun (is_pronoun_mention, the same production
    coreference primitive _referent_links already reuses)."""
    if not referent or len(referent) < _REFERENT_RECURRENCE_MIN_LEN:
        return False
    if referent in _REFERENT_RECURRENCE_STOP:
        return False
    if referent.endswith("ing"):
        return False
    if is_pronoun_mention(referent):
        return False
    return True


def _noun_class_of(word: str) -> set:
    return {name for name, members in NOUN_CONCEPT_CLASSES.items() if word in members}


def _referent_recurrence_matches(desired_ref: str, tok: str) -> bool:
    """Does outcome-sentence token `tok` recur the goal's target referent `desired_ref`? LITERAL
    (exact match) first; then SHARED_FEATURE (hdlab.lexical_similarity.concept_similarity, the SAME
    organ _referent_links already uses, reused unmodified); then NOUN_CONCEPT_CLASSES (the small SUPPLY
    register above, for common-sense noun concepts the 89-concept shared-feature lexicon doesn't
    cover, e.g. money/funding/pounds)."""
    if desired_ref == tok:
        return True
    if _lexsim_in_lexicon(desired_ref) and _lexsim_in_lexicon(tok):
        sim = _lexsim_concept_similarity(desired_ref, tok)
        if sim is not None and sim >= SIMILARITY_LINK_THRESHOLD:
            return True
    return bool(_noun_class_of(desired_ref) & _noun_class_of(tok))


def _referent_recurrence_in_sentence(sentence: str, desired_ref: str):
    """First token in `sentence` that recurs `desired_ref` (_referent_recurrence_matches), plus an
    OCCURRENCE-GATE read: scan LEFT from the match to the nearest _STOP_BOUNDARY token or sentence
    start (the same clause-scoping convention _object_referent_after/_STOP_BOUNDARY already use
    elsewhere in this module) and check for an explicit negator (_is_negator -- the SAME primitive the
    verb-side occurrence-gate uses) in that span: negated -> UNMET (the target recurred but under
    negation, "the money never came"), else MET (occurrence confirmed). Returns (verdict, detail) or
    None (no recurrence found in this sentence)."""
    toks = _tokens(sentence)
    for idx, tok in enumerate(toks):
        if _referent_recurrence_matches(desired_ref, tok):
            j = idx - 1
            while j >= 0 and toks[j] not in _STOP_BOUNDARY:
                j -= 1
            clause = toks[j + 1:idx]
            negated = any(_is_negator(t) for t in clause)
            verdict = "UNMET" if negated else "MET"
            return verdict, {"reason": "referent_recurrence", "referent": desired_ref,
                             "matched_token": tok, "negated": negated,
                             "occurrence_gate_fired": negated}
    return None


def congruence_referent_recurrence_windowed(passage_text: str, max_window: int = 2):
    """Referent-recurrence fallback tier (sibling of congruence_outcome_valence_windowed, same
    backward-window convention). Fires ONLY when: (a) an antecedent goal is found
    (find_desired_state), (b) its referent is _referent_recurrence_eligible, and (c) that referent
    recurs (literal / shared-feature / noun-concept-class) in one of the trailing `max_window`
    sentences. NA (abstain) otherwise -- never a forced verdict; the closest-to-end matching sentence
    wins (consistent with congruence_outcome_valence_windowed's own backward-scan convention).

    max_window=2 (narrower than the verb-class channel's max_window=4): a bare-noun recurrence is a
    WEAKER signal than a class-matched verb (no result-state semantics at all, just co-reference), so
    it is given a tighter reach. MEASURED reason (2026-08-07, disk-probed): at max_window=4 the scan
    can reach back INTO the goal-adjacent region and match a goal RESTATEMENT rather than a genuine
    post-goal outcome -- e.g. a passage where the goal sentence is followed 1 sentence later by a
    rhetorical repeat of the same target noun (agg_anne_diana_bosom_friend_ch12: the goal is "hoped to
    be your bosom friend"; two sentences later Anne asks Diana "...enough to be my bosom FRIEND?" --
    literal 'friend' recurs, but this is the SAME request restated, not evidence Diana agreed; the
    real signal there is enablement/granting ('Diana laughed...I guess so'), a different, harder,
    out-of-scope mechanism). max_window=2 keeps every measured genuine recovery (all three land at
    k=1: woz_tin_woodman_heart/woz_dorothy_kansas_wish/onestop_hunt_crowdfunding) while dropping that
    one coincidental/lucky match -- reported honestly, not silently kept."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    goal_sentences = sents[:-1]
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    if desired is None:
        return "NA", {"reason": "no_desiderative_goal_found"}
    referent = desired.get("referent")
    if not _referent_recurrence_eligible(referent):
        return "NA", {"reason": "referent_recurrence_ineligible", "referent": referent}
    for k in range(1, min(max_window, len(sents) - 1) + 1):
        hit = _referent_recurrence_in_sentence(sents[-k], referent)
        if hit is not None:
            verdict, detail = hit
            detail["desired"] = desired
            detail["window_k"] = k
            return verdict, detail
    return "NA", {"reason": "no_referent_recurrence", "referent": referent}


# ============================================================================ GROUNDED RESULT-CLASS
# TIER (2026-08-07, ~6yo-grounded-foundation SUPPLY build; last-resort congruence tier). USER-
# authorized as Director-LEAN option A from the grounding fork: "supply the grounded result-
# semantics a 6yo has" is DATA (a small hand-authored result-valence lexicon), not text-induction
# (the closed VERB-VALENCE GROUNDING arc) and not raw lexical valence in isolation (a 6yo doesn't
# just grade the WORD "spoil"/"punish" as bad -- they COMBINE it with "did this happen to something/
# someone connected to what I wanted", i.e. a recognized goal). This tier is that combination: it
# fires ONLY when (1) find_desired_state has already recognized a goal (this module's existing
# goal-recognition, unchanged) AND (2)-(4) the outcome region carries a small closed-class RESULT
# verb whose grounded valence (NEGATIVE_RESULT/POSITIVE_RESULT below) is common-sense-obvious to a
# young child, subject-linked to a person (not a bystander/inanimate event) and occurrence-gated the
# SAME way every other channel in this module is (_verb_negated_before).
#
# NOT referent-linked (unlike the verb-class Pass-1 channel and the referent-recurrence channel
# above) -- ts_tom_sugar_theft is why: the goal's referent extracts as "nose" (a known GAP-C artifact
# of the "steal sugar UNDER his aunt's very NOSE" PP-attachment span; "under" is not in
# _STOP_BOUNDARY so the object-scan overruns past the true theme "sugar") but the punishment lands on
# "his KNUCKLES" -- a different noun with no lexical or shared-feature relationship to either. The
# only thing connecting the punishment to the goal is that it happens TO the goal-holder (not a
# stranger), which is exactly guard (2)/_grounded_result_subject_linked below, not a referent match.
#
# STRICT LAST-RESORT ORDERING (never touches an item any earlier tier already resolves): consulted
# by congruence_with_lexicon_fallback ONLY after BOTH congruence_outcome_valence_windowed (the
# verb-class + occurrence-gate + goal-verb-recurrence did-it-happen channel) AND
# congruence_referent_recurrence_windowed have abstained (NA) -- see congruence_with_lexicon_fallback
# below. Pure additive fallback, isolated new code path: does not modify congruence_decision /
# find_actual_state_candidates / congruence_referent_recurrence_windowed.
NEGATIVE_RESULT = {"spoil", "ruin", "punish", "scold", "damage", "damag", "harm", "wreck", "rap"}
POSITIVE_RESULT = {"reward", "praise", "prais", "succeed", "succe", "achieve", "achiev", "mend",
                    "fix"}
# "damag"/"prais"/"succe"/"achiev": hdlab.thematic_role_labeler.lemma_verb double-consonant/silent-e
# stemmer quirks (MEASURED@this build: lemma_verb("damaged")=="damag" but lemma_verb("damage")==
# "damage"; lemma_verb("praised")=="prais"; lemma_verb("succeed")=="succe" but lemma_verb
# ("succeeded")=="succeed"; lemma_verb("achieved")=="achiev") -- same documented workaround pattern
# as DAMAGE_LOSE.add("collaps") / FILL_CLASS's "fil" above, not a mechanism change. TWO words from
# the Director pre-reg's example list are DELIBERATELY EXCLUDED, both MEASURED@this build (a
# real-eval regression sweep, not a hypothetical):
#   "break" -- already a CLASS_REGISTRY/DAMAGE_LOSE member (reachable via the earlier, referent-
#     linked windowed-primary tier when a link exists) AND it carries a common positive idiom this
#     coarse lemma-membership scan cannot safely tell apart ("broke the RECORD" / "broke new GROUND"
#     = achieved, not damaged).
#   "fail" -- MEASURED@this build's own full-44 regression sweep: onestop_malala ("They thought the
#     bullet would silence us. But they FAILED," she said...) mis-typed UNMET (gold MET) because the
#     ANTAGONIST's own failure is GOOD news for the goal-holder -- guard (2) confirms the clause is
#     about a person ("they" is a legitimate pronoun) but has no way to tell that person is the
#     antagonist, not the goal-holder (find_desired_state itself has no entity attribution -- a
#     pre-existing, out-of-scope limitation this tier is not positioned to fix). Removing "fail"
#     costs nothing (not load-bearing for either measured gain below) and eliminates the miss.
# Both exclusions are scope-narrowing safety choices, not oversights.

# SENSE-DISAMBIGUATION EXCEPTIONS (narrow, principled, not eval-tuned): a couple of the remaining
# words have a genuinely different, non-negative/non-positive common sense a literal
# lemma-membership scan cannot otherwise tell apart. "rapped ON/AT the door" = knocked (neutral), not
# "rapped SOMEONE'S KNUCKLES" = struck/punished; "spoil HIM/HER/THEM/a CHILD" = indulge/pamper
# (positive-adjacent), not "spoil the CAKE/MILK/FOOD" = ruin.
_GROUNDED_RESULT_SKIP_IF_NEXT = {"rap": {"on", "at"}}
_GROUNDED_RESULT_SKIP_IF_NEXT_PERSON = {"spoil": {"him", "her", "them", "me", "us", "kid", "kids",
                                                   "child", "children"}}


def _grounded_result_subject_linked(toks: List[str], v_idx: int) -> bool:
    """Guard (2), the 'responder/subject = goal-holder or the goal's target' constraint: scan LEFT
    from the result verb to the nearest _STOP_BOUNDARY / sentence start (same clause-scoping
    convention _referent_recurrence_in_sentence above already uses) and require the clause to be
    ABOUT a person -- an elliptical/imperative clause with no subject at all ('Punish me...'), a
    pronoun (is_pronoun_mention, which already covers possessives like 'his'/'her' -- 'got HIS
    knuckles rapped' links via the possessive), or an explicit animate noun
    (hdlab.animacy_lexicon.lookup_animacy, the SAME primitive Channel B's _cb_token_is_animate_agent
    above already uses) all pass. An explicit new INANIMATE subject with none of these cues ('the
    STORM broke') fails the guard -- this is what keeps the tier from crediting/blaming the
    goal-holder for a bystander event."""
    j = v_idx - 1
    span = []
    while j >= 0 and toks[j] not in _STOP_BOUNDARY:
        span.append(toks[j])
        j -= 1
    if not span:
        return True
    from hdlab.animacy_lexicon import lookup_animacy
    for t in span:
        if is_pronoun_mention(t):
            return True
        info = lookup_animacy(t)
        if info is not None and info.get("animacy") == "animate":
            return True
    return False


def _grounded_result_class_in_sentence(sentence: str):
    """First eligible NEGATIVE_RESULT/POSITIVE_RESULT verb occurrence in `sentence`: lemma_verb
    membership, sense-disambiguation exceptions, guard (2) (_grounded_result_subject_linked), then
    occurrence-gated (_verb_negated_before, reused verbatim -- the SAME primitive every other channel
    in this module uses) with a same<->opposed XOR flip on negation ('he was NOT rewarded' -> the
    good thing did not happen -> UNMET; 'no HARM done' -- 'no' is itself a NEGATORS-set negator, so
    this already flips NEGATIVE_RESULT 'harm' to MET via the same gate, no special-case needed).
    Returns (verdict, detail) or None (no eligible match in this sentence)."""
    toks = _tokens(sentence)
    for idx, tok in enumerate(toks):
        lemma = lemma_verb(tok)
        if lemma in NEGATIVE_RESULT:
            base_verdict = "UNMET"
        elif lemma in POSITIVE_RESULT:
            base_verdict = "MET"
        else:
            continue
        skip_next = _GROUNDED_RESULT_SKIP_IF_NEXT.get(lemma)
        if skip_next and idx + 1 < len(toks) and toks[idx + 1] in skip_next:
            continue
        skip_next_person = _GROUNDED_RESULT_SKIP_IF_NEXT_PERSON.get(lemma)
        if skip_next_person and idx + 1 < len(toks) and toks[idx + 1] in skip_next_person:
            continue
        if not _grounded_result_subject_linked(toks, idx):
            continue
        negated = _verb_negated_before(toks, idx)
        verdict = ("MET" if base_verdict == "UNMET" else "UNMET") if negated else base_verdict
        return verdict, {"reason": "grounded_result_class", "verb_lemma": lemma,
                          "base_verdict": base_verdict, "negated": negated,
                          "occurrence_gate_fired": negated}
    return None


def congruence_grounded_result_class(passage_text: str, max_window: int = 2):
    """LAST-RESORT congruence tier (sibling of congruence_referent_recurrence_windowed, same
    backward-window convention, max_window=2 for the same reason -- reaching further back risks
    picking up a goal-adjacent restatement rather than genuine outcome). Fires ONLY when (1) an
    antecedent goal is found (find_desired_state fires -- guard 1: 'a recognized positive goal'), and
    (2)-(4) a NEGATIVE_RESULT/POSITIVE_RESULT verb passes the subject-linkage guard and
    occurrence-gate in one of the trailing `max_window` sentences (_grounded_result_class_in_sentence
    above). NA (abstain) otherwise.

    GOAL-SEARCH SCOPE (extends the sents[:-1] convention every sibling tier uses): if no goal is
    found among sents[:-1], ALSO try find_desired_state on sents[-1] itself before abstaining -- a
    coordinated single-sentence goal+result construction ('Tom TRIED to steal sugar under his aunt's
    nose, and got his knuckles RAPPED for it.') states the goal and its immediate result in ONE
    sentence joined by a coordinator, so the ordinary goal_sentences=sents[:-1] split (which treats
    the goal-bearing sentence as the LAST sentence, hence unavailable to the goal-search) never finds
    it. This is a general narrative-construction pattern (X tried to VP, and/but RESULT), not tuned
    to one item; it only ever ADDS a goal-search candidate (never removes desired=None -> NA when
    both scans fail), so no existing NA outcome elsewhere in this module changes."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    goal_sentences = sents[:-1]
    desired = None
    for gs in goal_sentences:
        desired = find_desired_state(gs)
        if desired is not None:
            break
    if desired is None:
        desired = find_desired_state(sents[-1])
    if desired is None:
        return "NA", {"reason": "no_desiderative_goal_found"}
    for k in range(1, min(max_window, len(sents) - 1) + 1):
        hit = _grounded_result_class_in_sentence(sents[-k])
        if hit is not None:
            verdict, detail = hit
            detail["desired"] = desired
            detail["window_k"] = k
            return verdict, detail
    return "NA", {"reason": "no_grounded_result_verb_found"}


# ============================================================================ REQUEST-RESPONSE
# OUTCOME-TYPING TIER (2026-08-07, dialogue-goal companion build). The 2026-08-07 dialogue-goal-
# recognition build (commit 2747fac9a) taught find_desired_state to recognize an illocutionary
# REQUEST/hedged-request as the requester's own goal (HEDGED_MODAL_WISH / REQUEST_LET /
# REQUEST_MODAL_1P / REQUEST_WILL_YOU / REQUEST_PLEASE -- collectively _DIALOGUE_REQUEST_PATTERNS
# below), but left the OUTCOME of that goal untyped: the standard recurrence channel
# (find_actual_state_candidates) requires a class-bearing verb, so it structurally cannot type a
# request refused via "will not LET you in" (no CLASS_REGISTRY class at all -- "let" is a light verb
# with no matching class) or granted via a verb with no lexical relationship to the request's own verb
# ("invited...to come in" shares no verb-class with "open the gate"). A request's outcome is not "did
# the SAME event happen again" (the recurrence channel's question) -- it is "did the ADDRESSEE respond
# to the request", a distinct illocutionary-uptake construction (Searle 1969 direct/indirect speech
# acts; Austin 1962 perlocutionary effect) that needs its own scan of the dialogue turn FOLLOWING the
# request, not the request's own clause.
#
# MECHANISM: fires ONLY when a request goal was found (_find_dialogue_request_goal, scanning
# sents[:-1] left-to-right for the FIRST sentence whose find_desired_state result carries a
# _DIALOGUE_REQUEST_PATTERNS pattern) -- never touches a passage with no recognized request. Then
# scans the sentence(s) immediately FOLLOWING the request (max_window_forward, default 1 -- the
# request's very next line of dialogue) for one of two response signals, earliest-token-index wins if
# both appear in the same sentence:
#
#   (a) GRANT-VERB (_request_grant_verb_match): a small closed-class affirmative-response verb
#       (_REQUEST_GRANT_VERBS: invite/allow/admit/permit/grant) whose own direct object is a PERSON
#       pronoun (is_pronoun_mention guard -- blocks an unrelated sense with no person object at all,
#       e.g. "invited PROPOSALS for the new park") -> MET (base_verdict), occurrence-gated
#       (_verb_negated_before) same as every other channel in this module ("did not allow him in" ->
#       negation flips MET -> UNMET).
#   (b) REQUEST-ECHO (_request_echo_match): the request's OWN verb-or-particle surface recurs in the
#       response, occurrence-gated the same way. REQUEST_LET's embedded "verb" is frequently an
#       elided participle/particle rather than a real verb ("let me IN" -- lemma_verb("in") == "in"
#       itself, not a conjugated form), so a bare lemma match on a word as common as "in" would be a
#       serious over-fire risk (any unrelated "in"-containing sentence in the response window). THE
#       DEIXIS-SHIFT GUARD (over-fire guard, load-bearing): for REQUEST_LET specifically, require the
#       echoed "let" be immediately followed by "you" -- the request's own surface has the requester
#       as "me"/"us" (1st person, from the requester's own utterance); a genuine response addresses
#       that SAME entity as "you" (2nd person, from the responder's turn) -- "I will not let YOU in" /
#       "I will let YOU in". This blocks a coincidental unrelated "let X in" about a different entity
#       in the response window (e.g. "the cat let ITSELF in") without needing a full
#       speaker-attribution / cross-turn coreference primitive this module does not have.
#       For every OTHER _DIALOGUE_REQUEST_PATTERNS pattern the verb_lemma is a genuine content verb
#       (find_desired_state only reaches those patterns for a real embedded verb) -- REFERENT-LINK
#       GUARD (over-fire guard, load-bearing, disk-probed): a bare lemma_verb match on that content
#       verb ANYWHERE in the response is still not enough -- "May I OPEN the shop early?" ... "she
#       OPENED the report" shares the verb lemma but is about a different object entirely. Reuse the
#       SAME class-directed referent extraction find_desired_state itself uses (SUBJECT_IS_REFERENT_
#       CLASSES / OBJECT_IS_REFERENT_CLASSES) to read the echoed token's own referent, then require it
#       to _referent_links (literal / pronoun-coref / shared-feature -- the SAME discourse-entity
#       linker congruence_decision's Pass-1 already uses) back to the request's own referent. A
#       coincidentally-lemma-matching but referentially-unrelated echo never qualifies.
#
# OVER-FIRE GUARDS (matches the spawn-prompt's own checklist): (1) fires ONLY for a recognized
# _DIALOGUE_REQUEST_PATTERNS goal (never a bare verb-class goal already handled by the earlier tiers);
# (2) the response is scanned starting at the sentence AFTER the request sentence, never the request's
# own sentence (rules out the requester's own repeated "let me in; let me in" from being read as its
# own response); (3) both response channels are occurrence-gated (_verb_negated_before, the SAME
# primitive every sibling channel in this module already uses); (4) STRICT LAST-RESORT ORDERING --
# consulted by congruence_with_lexicon_fallback ONLY after congruence_outcome_valence_windowed,
# congruence_referent_recurrence_windowed, AND congruence_grounded_result_class have all abstained
# (NA); a passage any earlier tier already resolves is untouched. max_window_forward defaults to 1
# (the request's immediate next line) rather than a wider window like the sibling tiers use --
# MEASURED (this build): both pre-reg target items resolve at forward-window 1, and narrowing the
# reach is a direct over-fire mitigation (a request/response pair that is not adjacent dialogue is
# exactly the kind of narrative distance where a coincidental unrelated echo becomes likely).
_DIALOGUE_REQUEST_PATTERNS = {"REQUEST_LET", "REQUEST_MODAL_1P", "REQUEST_WILL_YOU",
                              "REQUEST_PLEASE", "HEDGED_MODAL_WISH"}
_REQUEST_GRANT_VERBS = {"invite", "invit", "allow", "admit", "permit", "grant"}
_REQUEST_ECHO_MAX_SPAN = 3
_REQUEST_RESPONSE_MAX_WINDOW_FORWARD = 1


def _request_grant_verb_match(toks: List[str]):
    """First _REQUEST_GRANT_VERBS occurrence whose own direct object is a person pronoun (guards
    against an unrelated sense of the same verb with no person object, e.g. "invited proposals").
    Returns (idx, negated, kind, base_verdict) or None."""
    for idx, tok in enumerate(toks):
        lemma = lemma_verb(tok)
        if lemma not in _REQUEST_GRANT_VERBS:
            continue
        obj = _object_referent_after(toks, idx)
        if obj is None or not is_pronoun_mention(obj):
            continue
        return idx, _verb_negated_before(toks, idx), "grant_verb", "MET"
    return None


def _request_echo_match(toks: List[str], request: dict):
    """First echo of `request`'s own verb-or-particle surface. Returns (idx, negated, kind,
    base_verdict) or None. See section docstring above for the REQUEST_LET deixis-shift guard and the
    referent-link guard used for every other pattern."""
    verb_lemma = request.get("verb_lemma")
    if not verb_lemma:
        return None
    if request.get("pattern") == "REQUEST_LET":
        for idx, tok in enumerate(toks):
            if tok != "let" or idx + 1 >= len(toks) or toks[idx + 1] != "you":
                continue
            span_end = min(len(toks), idx + 2 + _REQUEST_ECHO_MAX_SPAN)
            if any(toks[k] == verb_lemma for k in range(idx + 2, span_end)):
                return idx, _verb_negated_before(toks, idx), "let_echo", "MET"
        return None
    for idx, tok in enumerate(toks):
        if lemma_verb(tok) != verb_lemma:
            continue
        classes = _verb_classes(verb_lemma)
        candidate_ref = (_np_last_content(toks[:idx]) if classes & SUBJECT_IS_REFERENT_CLASSES
                         else _object_referent_after(toks, idx))
        linked, _tier = _referent_links(request.get("referent"), candidate_ref)
        if not linked:
            continue
        return idx, _verb_negated_before(toks, idx), "verb_echo", "MET"
    return None


def _request_response_in_sentence(sentence: str, request: dict):
    """Earliest-token-index response signal in `sentence` (grant-verb or request-echo, see section
    docstring), occurrence-gated with a same<->opposed XOR flip on negation. Returns (verdict, detail)
    or None (no response signal in this sentence)."""
    toks = _tokens(sentence)
    candidates = [c for c in (_request_grant_verb_match(toks), _request_echo_match(toks, request))
                  if c is not None]
    if not candidates:
        return None
    idx, negated, kind, base_verdict = min(candidates, key=lambda c: c[0])
    verdict = ("UNMET" if base_verdict == "MET" else "MET") if negated else base_verdict
    return verdict, {"reason": f"request_response_{kind}", "match_idx": idx, "negated": negated,
                      "occurrence_gate_fired": negated}


def _find_dialogue_request_goal(sents: List[str]):
    """First sentence (left-to-right) whose find_desired_state result carries a
    _DIALOGUE_REQUEST_PATTERNS pattern, paired with its index in `sents`. Returns (request, idx) or
    (None, None)."""
    for i, s in enumerate(sents):
        d = find_desired_state(s)
        if d is not None and d.get("pattern") in _DIALOGUE_REQUEST_PATTERNS:
            return d, i
    return None, None


def congruence_request_response(passage_text: str,
                                 max_window_forward: int = _REQUEST_RESPONSE_MAX_WINDOW_FORWARD):
    """REQUEST-RESPONSE outcome-typing tier (sibling of congruence_grounded_result_class, same
    last-resort-fallback convention). Fires ONLY when (1) a _DIALOGUE_REQUEST_PATTERNS goal is found
    among sents[:-1] (_find_dialogue_request_goal), and (2) one of the trailing `max_window_forward`
    sentences AFTER the request sentence carries a grant-verb or request-echo response signal
    (_request_response_in_sentence). NA (abstain) otherwise -- never a forced verdict. See section
    docstring above for the full mechanism + over-fire guards."""
    sents = _sentences(passage_text)
    if len(sents) < 2:
        return "NA", {"reason": "insufficient_sentences"}
    request, req_idx = _find_dialogue_request_goal(sents[:-1])
    if request is None:
        return "NA", {"reason": "no_request_goal_found"}
    for j in range(req_idx + 1, min(req_idx + 1 + max_window_forward, len(sents))):
        hit = _request_response_in_sentence(sents[j], request)
        if hit is not None:
            verdict, detail = hit
            detail["desired"] = request
            detail["response_sentence_idx"] = j
            return verdict, detail
    return "NA", {"reason": "no_response_found", "desired": request}


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


# ============================================================================ LEVIN VERB-CLASS
# LAST-RESORT BACKOFF (2026-08-07, WIRE-DONT-ISLAND promotion from experiments/
# exp_verbclass_backoff_coverage_v2.py, commit 276674abb, PARTIAL: coverage_gain=+1
# (ts_tom_wish_free_potter, NA->CORRECT), regressions=0, na_to_wrong=0, no_overfire=True,
# restoration_ok=True on the full-44 goal_bearing_modern_eval_v1.jsonl bank; held-out generalization
# 4/8, below the 6/8 bar -- a separate, already-traced referent-extraction gap (see the source cell's
# docstring), not a defect of this tier's placement. v1 (commit 883e1b7ba, HARD_FAIL) patched
# _verb_classes GLOBALLY, so the FIRST cascade tier saw the backoff and pre-empted later,
# more-reliable tiers that were correctly answering via referent matching -- net -2. v2's fix (this
# promotion): consult the SAME Levin backoff table ONLY as the ABSOLUTE LAST RESORT, after the entire
# unpatched cascade (verb-class-windowed / referent-recurrence / grounded-result / request-response /
# bare-lexicon, ALL unchanged by this promotion) has abstained -- see the `_levin_retry` parameter on
# congruence_with_lexicon_fallback below, which re-runs the SAME cascade function exactly once more
# with this table installed, then restores. STRICT-ADD (load-bearing, MEASURED not just argued): an
# item whose unpatched cascade already returns a non-abstain verdict (correct OR wrong) never even
# attempts the retry, so it is IMPOSSIBLE for this tier to touch (let alone flip) an already-decided
# item.
#
# CLASS DESIGN (SUPPLY DATA, hand-authored from Levin 1993's class inventory, same convention as
# CLASS_REGISTRY above -- NOT induced/tuned against any eval's text). "do" is DELIBERATELY EXCLUDED:
# Levin/VerbNet do not define a dedicated "do" class -- it is the paradigm semantically-bleached
# light-verb/pro-verb (Jespersen 1949); forcing a class onto it would be a precision risk (over-fire),
# not a genuine backoff.
LEVIN_CLASS_MEMBERS = {
    "LEVIN_POSSESSION": [  # Levin 13.5.1 "Obtain verbs" + have-class possession-state verbs
        ("get",     ["get", "gets", "getting", "got"],                    True),
        ("have",    ["have", "has", "had", "having"],                     True),
        ("find",    ["find", "finds", "finding", "found"],                True),
        ("take",    ["take", "takes", "taking", "took", "taken"],         True),
        ("obtain",  ["obtain", "obtains", "obtaining", "obtained"],       True),
        ("gain",    ["gain", "gains", "gaining", "gained"],               True),
        ("procure", ["procure", "procures", "procuring", "procured"],     False),
        ("secure",  ["secure", "secures", "securing", "secured"],         False),
    ],
    "LEVIN_TRANSFER": [  # Levin 13.1 "Verbs of Future Having" / dative-alternation give-class
        ("give",    ["give", "gives", "giving", "gave", "given"],         True),
        ("hand",    ["hand", "hands", "handing", "handed"],               True),
        ("offer",   ["offer", "offers", "offering", "offered"],           True),
        ("provide", ["provide", "provides", "providing", "provided"],     True),
        ("present", ["present", "presents", "presenting", "presented"],   True),
        ("award",   ["award", "awards", "awarding", "awarded"],           True),
        ("grant",   ["grant", "grants", "granting", "granted"],           False),
        ("deliver", ["deliver", "delivers", "delivering", "delivered"],   False),
    ],
    "LEVIN_CREATION": [  # Levin 26.1/26.4 "Build verbs" / "Create verbs"
        ("make",     ["make", "makes", "making", "made"],                 True),
        ("build",    ["build", "builds", "building", "built"],            True),
        ("create",   ["create", "creates", "creating", "created"],        True),
        ("form",     ["form", "forms", "forming", "formed"],              True),
        ("produce",  ["produce", "produces", "producing", "produced"],    True),
        ("craft",    ["craft", "crafts", "crafting", "crafted"],          True),
        ("construct", ["construct", "constructs", "constructing", "constructed"], False),
        ("forge",    ["forge", "forges", "forging", "forged"],            False),
    ],
    "LEVIN_PERCEPTION": [  # Levin 30.1 "Verbs of Perception"
        ("see",      ["see", "sees", "seeing", "saw", "seen"],            True),
        ("notice",   ["notice", "notices", "noticing", "noticed"],        True),
        ("observe",  ["observe", "observes", "observing", "observed"],    True),
        ("spot",     ["spot", "spots", "spotting", "spotted"],            True),
        ("glimpse",  ["glimpse", "glimpses", "glimpsing", "glimpsed"],    True),
        ("witness",  ["witness", "witnesses", "witnessing", "witnessed"], False),
        ("perceive", ["perceive", "perceives", "perceiving", "perceived"], False),
    ],
}
LEVIN_ADVERSARIAL_EXCLUDED_LIGHT_VERB = "do"  # deliberately unclassed -- see class-design note above
_LEVIN_NEGATIVE_ACHIEVEMENT_CLASSES = {"FAIL_LOSE", "DAMAGE_LOSE"}  # existing CLASS_REGISTRY neg poles
_LEVIN_ABSTAIN = ("NA", "NONE", "AMBIGUOUS")

_levin_backoff_table_cache: Optional[dict] = None


def _levin_backoff_table() -> dict:
    """Lazily-built lemma -> frozenset({class_tag}) table, built from lemma_verb (the real production
    lemmatizer, never hand-guessed) so truncation quirks (collaps/fil/mak/giv/tak) are handled
    identically to every other tier. Cached after first build (deterministic, no RNG, no I/O)."""
    global _levin_backoff_table_cache
    if _levin_backoff_table_cache is None:
        table = {}
        for class_tag, members in LEVIN_CLASS_MEMBERS.items():
            for _concept, surfaces, _is_core in members:
                for surf in surfaces:
                    table[lemma_verb(surf)] = frozenset({class_tag})
        _levin_backoff_table_cache = table
    return _levin_backoff_table_cache


def _install_levin_backoff_patch():
    """Runtime-only reassignment of the module-globals _verb_classes / _class_relation to STRICT-ADD
    wrappers (never overrides an existing non-empty classification/relation). Returns the two ORIGINAL
    function objects so the caller restores them exactly. Same monkeypatch mechanics validated in
    experiments/exp_verbclass_backoff_coverage_v1.py::_install_patch (reused by v2) -- promoted
    in-module here (this module IS the target, so no cross-process patching is needed)."""
    global _verb_classes, _class_relation
    orig_verb_classes = _verb_classes
    orig_class_relation = _class_relation
    backoff_table = _levin_backoff_table()

    def _patched_verb_classes(lemma):
        classes = orig_verb_classes(lemma)
        if classes:
            return classes  # STRICT ADD: never override an existing classification
        return set(backoff_table.get(lemma, set()))

    def _patched_class_relation(desired_classes, actual_classes):
        rel = orig_class_relation(desired_classes, actual_classes)
        if rel is not None:
            return rel  # STRICT ADD: never override an existing relation decision
        levin_d = {c for c in desired_classes if c in LEVIN_CLASS_MEMBERS}
        levin_a = {c for c in actual_classes if c in LEVIN_CLASS_MEMBERS}
        if levin_d and levin_d & levin_a:
            return "same"
        if levin_d and (actual_classes & _LEVIN_NEGATIVE_ACHIEVEMENT_CLASSES):
            return "opposed"
        if levin_a and (desired_classes & _LEVIN_NEGATIVE_ACHIEVEMENT_CLASSES):
            return "opposed"
        return None

    _verb_classes = _patched_verb_classes
    _class_relation = _patched_class_relation
    return orig_verb_classes, orig_class_relation


def _restore_levin_backoff_patch(orig_verb_classes, orig_class_relation):
    global _verb_classes, _class_relation
    _verb_classes = orig_verb_classes
    _class_relation = orig_class_relation


def congruence_with_lexicon_fallback(passage_text: str, _levin_retry: bool = False):
    """PRODUCTION entry point: goal-congruence PRIMARY, V2_OUTCOME_UNMET/_MET lexicon as the ABSTAIN
    fallback (strict ADD -- non-goal-dependent / non-referent-stress behavior is unchanged from the
    pre-promotion lexicon-only path). WINDOW-WIDENING WIRED (2026-08-06 did-it-happen build, Check 4):
    the PRIMARY is now congruence_outcome_valence_windowed (was congruence_outcome_valence) so a true
    resolving clause followed by a trailing reaction/dialogue sentence is still reached. Strict-widen
    property (see congruence_outcome_valence_windowed): when sents[-1] already yields >=1 outcome
    candidate the windowed primary returns k=1 == congruence_outcome_valence, i.e. BYTE-IDENTICAL to
    the pre-wire behavior for every already-typed passage; it only steps backward when the
    closest-to-end sentence is candidate-empty. FULL-44 eval-wide non-regression verified (Check 4):
    every verdict that moves is NONE/NA -> a correct verdict, none correct -> wrong. Was byte-identical
    to experiments/exp_outcome_valence_goal_congruence_v1.py::congruence_with_lexicon_fallback before
    this wire (that source cell keeps its own copy untouched). REFERENT-RECURRENCE WIRED (2026-08-07,
    did-it-happen sibling build): when the verb-class windowed primary abstains (NA), try
    congruence_referent_recurrence_windowed BEFORE falling all the way to the bare lexicon -- a
    goal-relative referent-grounded signal is preferred over a goal-independent word-lexicon guess.
    Strict-ADD: only consulted on NA from the primary, and itself abstains (NA) unless a genuine
    referent recurrence is found, so a passage with no antecedent goal or no eligible referent falls
    through to the lexicon exactly as before. GROUNDED RESULT-CLASS TIER WIRED (2026-08-07, ~6yo-
    grounded-foundation SUPPLY build): when BOTH the verb-class windowed primary AND
    referent-recurrence abstain (NA), try congruence_grounded_result_class BEFORE falling all the way
    to the bare lexicon -- a goal-relational grounded-result-verb signal (SUPPLY, not raw lexical
    valence: it only ever fires when a goal is already recognized) is preferred over a
    goal-independent word-lexicon guess. Strict-ADD: only consulted on NA from both prior tiers, and
    itself abstains (NA) unless an eligible grounded-result verb is found, so a passage with no
    antecedent goal or no eligible result verb falls through to the lexicon exactly as before.
    REQUEST-RESPONSE TIER WIRED (2026-08-07, dialogue-goal companion build): a request's outcome is
    typed by whether the addressee's NEXT dialogue turn grants or refuses it (see
    congruence_request_response's own section docstring for the full mechanism), which fires ONLY
    when find_desired_state recognized the antecedent goal as a REQUEST/hedged-request construction
    (never a bare verb-class goal already handled by the earlier tiers). ORDERING (load-bearing,
    MEASURED@this build): a plain last-resort append (consulted only when ALL THREE prior tiers
    abstain) is NOT sufficient on its own -- the three prior tiers each independently call
    find_desired_state too, and now that it recognizes REQUEST_*/HEDGED_MODAL_WISH goals (2026-08-07
    dialogue-goal-recognition build), those tiers can produce a non-NA verdict FROM a request-type
    antecedent even though they were never designed/validated for illocutionary request/response
    resolution -- MEASURED regression case: mg3_frank_garden_invited's windowed verb-class primary
    (congruence_outcome_valence_windowed) coincidentally classifies "invited" into the SAME
    Tier-2-open-vocab-similarity class as the wish's "open" (both OPEN_CLASS), then fails the
    referent link (the subject-scan picks up the stray adverb "kindly", not "the gardener") ->
    "referent_mismatch" -> a confident but WRONG UNMET (gold MET), which a plain last-resort ordering
    would never get a chance to override. FIX: each of the three prior tiers' verdicts is trusted
    UNLESS it was computed from a _DIALOGUE_REQUEST_PATTERNS antecedent (detail["desired"]["pattern"]
    -- present on every non-NA verdict all three tiers return), in which case
    congruence_request_response gets the first attempt instead; if congruence_request_response ALSO
    abstains, the original tier's verdict is used exactly as it would have been anyway (so this can
    never produce a WORSE answer than before, only a chance to supply a better one). Strict-scoped:
    for any passage whose antecedent is NOT a dialogue-request construction (every existing 44-item /
    real_text / fair-instrument regression item outside the 2 new targets), `pattern` is never in
    _DIALOGUE_REQUEST_PATTERNS, so the very first non-NA tier returns exactly as before -- BYTE-
    IDENTICAL for every already-typed non-dialogue-request passage.
    LEVIN VERB-CLASS LAST-RESORT BACKOFF WIRED (2026-08-07, promoted from experiments/
    exp_verbclass_backoff_coverage_v2.py, commit 276674abb -- see the section comment above this
    function for the full mechanism + provenance): when ALL of the above (the 4 tiers AND the bare
    lexicon) abstain, the LEVIN_CLASS_MEMBERS table (get/have/find/take/obtain/gain,
    give/hand/offer/provide/present/award, make/build/create/form/produce/craft,
    see/notice/observe/spot/glimpse -- "do" excluded) is installed via `_install_levin_backoff_patch`
    and the SAME cascade is retried exactly once (`_levin_retry=True` on the internal recursive call
    prevents this block from firing again inside the retry, capping recursion at depth 1). Strict-ADD:
    fires ONLY on total abstain, so it is structurally impossible to flip an already-decided verdict
    -- MEASURED zero regression, +1 coverage gain on goal_bearing_modern_eval_v1.jsonl (see
    verification/verify_levin_lastresort_backoff.py)."""
    verdict, detail = congruence_outcome_valence_windowed(passage_text)
    if verdict != "NA" and detail.get("desired", {}).get("pattern") not in _DIALOGUE_REQUEST_PATTERNS:
        return verdict, detail
    verdict2, detail2 = congruence_referent_recurrence_windowed(passage_text)
    if verdict2 != "NA" and detail2.get("desired", {}).get("pattern") not in _DIALOGUE_REQUEST_PATTERNS:
        return verdict2, detail2
    verdict3, detail3 = congruence_grounded_result_class(passage_text)
    if verdict3 != "NA" and detail3.get("desired", {}).get("pattern") not in _DIALOGUE_REQUEST_PATTERNS:
        return verdict3, detail3
    verdict4, detail4 = congruence_request_response(passage_text)
    if verdict4 != "NA":
        return verdict4, detail4
    # congruence_request_response itself abstained -- fall back to whichever prior tier had a
    # (request-antecedent) non-NA verdict, in the ORIGINAL priority order, so a passage that reaches
    # this point is typed EXACTLY as it would have been before this build.
    if verdict != "NA":
        return verdict, detail
    if verdict2 != "NA":
        return verdict2, detail2
    if verdict3 != "NA":
        return verdict3, detail3
    sents = _sentences(passage_text)
    lex = lexicon_predict(sents[-1]) if sents else "NONE"
    if lex.upper() not in _LEVIN_ABSTAIN or _levin_retry:
        return lex, {"reason": "abstain_fallback_to_lexicon", "lexicon_raw": lex}
    # LEVIN VERB-CLASS LAST-RESORT BACKOFF (2026-08-07 promotion; see section comment above this
    # function). The entire unpatched cascade (all 4 prior tiers + bare lexicon) has abstained --
    # install the Levin backoff table and retry the SAME cascade exactly once. `_levin_retry=True` on
    # the recursive call below prevents this block from firing again inside the retry itself, so
    # recursion depth is capped at 1. An item that already reached a non-abstain verdict above never
    # enters this block, so it is structurally impossible for the backoff to touch (let alone flip) an
    # already-decided item.
    orig_verb_classes, orig_class_relation = _install_levin_backoff_patch()
    try:
        verdict5, detail5 = congruence_with_lexicon_fallback(passage_text, _levin_retry=True)
    finally:
        _restore_levin_backoff_patch(orig_verb_classes, orig_class_relation)
    if verdict5.upper() not in _LEVIN_ABSTAIN:
        detail5 = dict(detail5)
        detail5["levin_last_resort_backoff_applied"] = True
        return verdict5, detail5
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

    # (7b) GOAL-COMPLEMENT OUTCOME-TYPING EXCLUSION (2026-08-06 bystander mis-bind fix) -----------
    # CAN-FAIL (a): a GOAL clause's OWN infinitival complement verb must NOT be typed as an achieved
    # outcome. Pre-fix, "wanted to FIX"/"longed to WIN" (Tier-2) and "wanted to SINK" (Tier-1) fired
    # a spurious (subject, OUTCOME_MET/UNMET) that mis-bound a bystander owner downstream; GOAL must
    # still fire (the exclusion is strict SUBTRACT of outcome typing only, never touches has_desire).
    for _gs, _gsubj in [("Jack wanted to fix the old fence before the storm came.", "jack"),
                        ("Ruth longed to win the reading prize this year.", "ruth"),
                        ("Owen wanted to sink the raft before dawn.", "owen")]:
        _ev = type_sentence_events_c3(_gs, _gsubj)
        assert (_gsubj, R_GOAL) in _ev, f"goal must still fire after the exclusion: {_gs!r} -> {_ev}"
        assert not any(r in (R_UNMET, R_MET) for (_e, r) in _ev), (
            f"goal-clause complement verb must NOT be typed as an outcome: {_gs!r} -> {_ev}")
    # PRECISION GUARD (b): only the goal-clause-INTERNAL complement token is excluded; a LATER
    # genuine recurrence of the SAME verb surface elsewhere in the sentence must STILL type an
    # outcome (index-scoped, not a blanket surface suppression). Both tiers exercised on the SAME
    # surface: Tier-2 (base "win" recurs) and Tier-1 ("sink", a V2_OUTCOME_UNMET surface, recurs).
    _recur_t2 = type_sentence_events_c3("Sam wanted to win, and in the end did win the race.", "sam")
    assert ("sam", R_GOAL) in _recur_t2 and any(r == R_MET for (_e, r) in _recur_t2), (
        f"Tier-2: later recurrence of goal verb 'win' must still type OUTCOME_MET: {_recur_t2}")
    _recur_t1 = type_sentence_events_c3("Owen wanted to sink the raft, so he did sink it.", "owen")
    assert ("owen", R_GOAL) in _recur_t1 and any(r == R_UNMET for (_e, r) in _recur_t1), (
        f"Tier-1: later recurrence of goal verb 'sink' must still type OUTCOME_UNMET: {_recur_t1}")

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

    # (13) DID-IT-HAPPEN occurrence-gate + goal-verb-recurrence channel (2026-08-06 build; preregs/
    # 2026-08-06_did_it_happen_occurrence_gate_v1.md). These pin the MECHANISM (fires correctly on
    # constructed inputs) + the strict-ADD guards; the eval-wide LIFT is measured separately in
    # verification/witness_did_it_happen_occurrence_gate_v1.py (MEASURED HARD-FAIL on real prose --
    # blocked by referent-extraction gaps documented there, NOT by a mechanism bug).
    # (13a) recurrence-only MET: a CLASS_REGISTRY-OOV outcome verb lemma-identical to the goal's own
    # desired verb ("pitch") recurs -> MET via the RECURRENCE_SENTINEL (referent 'davey' links).
    rec_met, rec_det = congruence_decision(
        ["The coach wanted Davey to pitch in the final"], "Davey pitched all afternoon")
    assert rec_met == "MET" and rec_det["reason"] == "same_class_same_referent" and \
        RECURRENCE_SENTINEL in rec_det["actual"]["classes"], (
        f"recurrence channel must type MET via RECURRENCE_SENTINEL, got {rec_met} ({rec_det})")
    # (13b) occurrence-gate EXECUTES on a negated recurrence (flips same<->opposed). The referent is
    # poisoned by the pre-verbal negator here (a documented real-prose gap), so the final verdict is
    # referent_mismatch -- what is asserted is that the gate FIRED, not the (poison-defeated) verdict.
    _neg_v, neg_det = congruence_decision(
        ["The coach wanted Davey to pitch in the final"], "Davey did not pitch at all")
    assert neg_det.get("occurrence_gate_fired") is True, (
        f"occurrence-gate must fire on a negated class-related/recurrence outcome: {neg_det}")
    # (13c) every candidate carries a correct `negated` key (reused _verb_negated_before verbatim).
    assert find_actual_state_candidates("The boat did not sink")[0]["negated"] is True
    assert find_actual_state_candidates("The boat sank")[0]["negated"] is False
    # (13d) recurrence guard: a content verb (len>3, not light) fires; a light/copula verb is blocked.
    assert any(RECURRENCE_SENTINEL in c["classes"]
               for c in find_actual_state_candidates("Davey pitched hard", "pitch"))
    assert not any(RECURRENCE_SENTINEL in c["classes"]
                   for c in find_actual_state_candidates("He got the prize", "get")), (
        "light/copula verb 'get' must NOT drive the recurrence channel")
    # (13e) STRICT-ADD: a legacy call (no desired_verb_lemma) never produces a RECURRENCE_SENTINEL.
    assert not any(RECURRENCE_SENTINEL in c["classes"]
                   for c in find_actual_state_candidates("Davey pitched hard"))
    # (13f) the occurrence-gate can NEVER fabricate a MET/UNMET from a class-UNRELATED candidate: an
    # unrelated (OPEN vs ARRIVE) negated outcome still abstains NA, gate does not fire.
    ung_v, ung_det = congruence_decision(
        ["Owen wanted to open the greenhouse before winter came"],
        "The gardener did not reach the market")
    assert ung_v == "NA" and ung_det["reason"] == "verb_class_unrelated" and \
        not ung_det.get("occurrence_gate_fired"), (
        f"class-unrelated negated outcome must stay NA (gate cannot fabricate): {ung_v} ({ung_det})")
    # (13g) window-widening: byte-identical to congruence_outcome_valence when sents[-1] already has a
    # candidate (k=1 wins); steps back to the true clause when sents[-1] is a candidate-empty trailing
    # reaction sentence.
    _wp1 = "Owen wanted to sink the raft before dawn. The raft sank."
    assert congruence_outcome_valence_windowed(_wp1) == congruence_outcome_valence(_wp1), (
        "windowed must be byte-identical when sents[-1] already yields a candidate")
    _wp2 = ("The coach wanted Davey to pitch in the final. Davey pitched all afternoon. "
            "Everyone cheered loudly.")
    _ww, _wwd = congruence_outcome_valence_windowed(_wp2)
    assert _ww == "MET" and congruence_outcome_valence(_wp2)[0] == "NA", (
        f"windowed must step back past a trailing reaction sentence to the true clause: {_ww} ({_wwd})")

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
        "goal_complement_exclusion": {
            "jack_fix_no_outcome": not any(
                r in (R_UNMET, R_MET) for (_e, r) in
                type_sentence_events_c3("Jack wanted to fix the old fence before the storm came.", "jack")),
            "win_recurrence_still_met": any(r == R_MET for (_e, r) in _recur_t2),
            "sink_recurrence_still_unmet": any(r == R_UNMET for (_e, r) in _recur_t1),
        },
        "outcome_valence": {
            "flip_unmet": flip_unmet, "flip_met": flip_met, "pronoun_referent_met": pron_met,
            "shared_feature_synonym_met": synfeat_met,
            "over_link_guard_unmet": diff_ref, "theme_mismatch_abstain": theme_mismatch,
            "abstain_fallback_verdict": fallback_verdict, "v1_bank_checked": len(v1_rows) if
            os.path.exists(_v1_bank_path) else 0, "v1_regression_mismatches": v1_mismatches,
        },
        "did_it_happen": {
            "recurrence_met": rec_met, "occurrence_gate_fired_on_negated": neg_det.get(
                "occurrence_gate_fired"), "unrelated_negated_stays_na": ung_v,
            "windowed_steps_back_to_true_clause": _ww,
        },
    }


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
