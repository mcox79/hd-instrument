#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_narrative_referent_recurrence_structural_v1

LEVER-2 PROBE (director task, following INC-2 commit 9c4439e92 / bank 1b0e62139). INC-2 measured
that hdlab.goal_typing's CLASS_REGISTRY-based grounded/class-relation channels are STARVED on
modern narrative vocabulary (owned_verdict fires 3/20 test, 0/3 correct; class_relation="none" on
29/30 train), BUT one channel carried signal WITHOUT any grounding lexicon:
hdlab.goal_typing.congruence_referent_recurrence_windowed's referent_recur_verdict fired 6/30 train
at accuracy-when-fired 5/6=0.833 (purity 0.8 on 5 MET-fires, 1.0 on 1 UNMET-fire) -- see
data/exp_narrative_goal_outcome_achievement_comparison_learnable_grounded_v1/metrics.json
family_signal_train.referent_recur_verdict. That channel, however, is NOT itself lexicon-free: its
_referent_recurrence_matches falls through to hdlab.lexical_similarity shared-feature cosine and a
small NOUN_CONCEPT_CLASSES register when literal match fails.

THIS CELL builds a version of the referent-recurrence idea that uses ONLY literal token match +
pronoun-coreference (hdlab.coreference_resolver, a structural/grammatical primitive, not a semantic
concept lexicon) + explicit closed-class negation/abandonment markers + one orthographic
(capitalization) cue for proper-noun destination replacement -- NO hdlab.lexical_similarity
CONCEPT_FEATURES, NO CLASS_REGISTRY, NO verb_lexical_similarity. Question: how far does
LITERAL/STRUCTURAL referent-resolution alone crack modern narrative goal-outcome MET/UNMET, past
the 0.60 surface plateau, with ZERO generalizable-grounding dependency?

MECHANISM (reuses owned referent organs, wire-don't-island; all imported unmodified from
hdlab.goal_typing / hdlab.coreference_resolver / hdlab.thematic_role_labeler):
  GOAL REFERENT: for each goal_text sentence (hdlab.goal_typing._sentences, production convention:
    first sentence that yields an ELIGIBLE referent wins -- hdlab.goal_typing.find_desired_state for
    the base extraction, hdlab.goal_typing._referent_recurrence_eligible as the specificity/pronoun/
    vague-noun gate, both reused unmodified). ADDITIONAL destination-PP fallback (new, this cell):
    find_desired_state's object-only scan returns None/empty for a bare motion verb immediately
    followed by "to <NP>" ("wanted to travel TO Africa" -- the object scan stops AT "to" by design,
    see hdlab.goal_typing._object_referent_after's docstring). _destination_after_verb extracts the
    NP after that "to" instead, ACCEPTED ONLY if the NP head is capitalized in the original
    (un-lowercased) sentence -- an orthographic proper-noun proxy, not a semantic lexicon, so
    "wanted to get a ticket" (lowercase "ticket") is never mistaken for a destination slot.
  OUTCOME MATCH: scan outcome_text tokens; hdlab.goal_typing._referent_links(desired, tok) decides
    LITERAL or PRONOUN_COREF linkage (reused unmodified; its SHARED_FEATURE tier is explicitly
    REJECTED here -- that tier is the grounding-lexicon fallback this probe is testing the absence
    of). A match's local clause (same _STOP_BOUNDARY backward-scan convention goal_typing already
    uses everywhere) is checked for an explicit negator (hdlab.goal_typing._is_negator, closed
    function-word class: not/never/no/none/cannot/n't) OR a closed ABANDON_LEMMAS set
    (cancel/quit/abandon, + a "give ... up" phrasal scan) -- MET iff recurs and neither fires;
    UNMET iff recurs and either fires. A recurrence nested behind a second "of"-PP within the clause
    (e.g. "vomited from the taste OF the donuts") is deliberately NOT read as MET or UNMET --
    reported as NA (referent_recurs_nested_ambiguous): a bare token co-occurrence two PPs deep is a
    real structural ambiguity (could be "the joy of X" or "the taste of X [that sickened him]"),
    not a case literal recurrence can honestly resolve without word-meaning.
  REPLACED (destination slot only): if the goal referent was extracted via the destination-PP
    fallback and does NOT recur, scan outcome_text for its OWN bare "to <capitalized NP>" pattern;
    a DIFFERENT capitalized head there ("went to Europe" vs goal "Africa") -> UNMET
    (referent_replaced). Scoped narrowly to the destination slot -- generic object replacement
    (e.g. a wrong medal color) is NOT attempted; reported as an honest scope limit, not a ceiling.

DATA / SPLIT: experiments/data/narrative_goal_outcome_rocstories_relabeled_v1.jsonl (50 items,
25 MET/25 UNMET). SAME stratified split as the generality/INC-2 cells -- imported directly
(load_items/stratified_split from exp_narrative_goal_outcome_role_sharded_generality_v1, NOT
reimplemented) so n_train=30/n_test=20, byte-identical membership, numbers directly comparable to
the cited 0.60 plateau (naive_flat_mean_acc=0.6100, majority_acc=0.5000).

ARMS (measured on the SAME held-out 20):
  HAND-RULE: the structural referent-recurrence typer above (deterministic, no RNG, no learning).
  LEARNER: hdlab.learner (ruleind plugin, byte-identical HYP_SPACE_SPEC convention to
    hdlab.goal_typing.induce_hypothesis) fit on TRAIN over 4 booleans (recurs/negated/replaced/
    realized -- realized = recurs and not negated and not nested), applied to TEST. Tests whether a
    learned combination of these same lexicon-independent features beats the fixed hand rule.
  BASELINES: 0.60 surface plateau (CITED, not recomputed, see module docstring above); owned
    hdlab.goal_typing.congruence_outcome_valence_windowed (expect near-total abstention, INC-2's own
    measured owned_fire_rate=0.15/owned_acc_when_fired=0.0 on this exact test split); owned
    hdlab.goal_typing.congruence_referent_recurrence_windowed (the EXISTING lexicon-using
    referent-recurrence channel, run on the SAME test split for a direct side-by-side against this
    cell's lexicon-free version); majority (recomputed, must equal 0.5000 by split construction).
  SCRAMBLE: offset=1 cyclic rotation of outcome_text against goal_text within the TEST set (fixed,
    deterministic, no RNG needed -- guarantees a derangement for n=20) -- goal and outcome no longer
    share discourse referents, so a genuine referent-matching mechanism should lose almost all of
    its fire-rate/accuracy; a word-count or position-only mechanism would not.

GATE (pre-registered; anti-premature-HARD_FAIL; brain=existence-proof):
  HARD-PASS: HAND-RULE (or +LEARNER) held-out FORCED acc (NA -> majority fallback) > 0.60 AND > 0.50
    majority, non-constant, scramble collapses (scramble forced-acc drops toward/below majority
    and/or fire-rate collapses) -> structural referent-resolution cracks narrative met/unmet
    LEXICON-INDEPENDENTLY, a real crack in the grounding wall.
  PARTIAL/NULL: ~0.60 or below, OR the channel simply doesn't fire enough to move the forced-acc
    needle -> report accuracy-WHEN-FIRED + coverage (the INC-2-style purity framing) instead, and
    the literal-crackable vs semantic-needs-grounding split (Section: DIAGNOSIS in the printed
    report) -- NOT a ceiling, a measured BOUND on how far lexicon-free structure alone reaches.

COMPUTE: n=50 items, closed-form glass-box feature extraction, no VSA fit / no gradient loop for the
hand rule; hdlab.learner's ruleind plugin is closed-form counting/search. Single blocking run,
sub-second wall time. Deterministic: no RNG anywhere in this cell (scramble is a fixed cyclic
rotation, not a random shuffle).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "narrative_referent_recurrence_structural_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- reuse, not reimplement: the generality cell's own split ----
from experiments.exp_narrative_goal_outcome_role_sharded_generality_v1 import (  # noqa: E402
    load_items, stratified_split, majority_class, accuracy,
)

# ---- reuse, not reimplement: owned referent-resolution organs ----
from hdlab.goal_typing import (  # noqa: E402
    find_desired_state, _sentences, _tokens, _np_last_content, _is_negator, _STOP_BOUNDARY,
    _referent_recurrence_eligible, _referent_links, _NEG_TRANSPARENT_ADVERBS,
    congruence_outcome_valence_windowed, congruence_referent_recurrence_windowed,
)
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.learner import apply as learner_apply, learn as learner_learn  # noqa: E402
from hdlab.state_of_mind import infer_nominal_gender  # noqa: E402

# Small closed-class relative-pronoun set (function words, not eval-tuned) -- a trailing relative
# clause ("his friends, WHO were also skaters") can strand a relative pronoun as the rightmost token
# of _np_last_content's forward NP scan (a known limitation of that rightmost-content-word heuristic,
# shared with the production find_desired_state machinery); such a token is never a real referent.
_RELATIVE_JUNK = {"who", "whom", "whose", "which", "that"}

# ============================================================================================
# CITED baselines (NOT recomputed -- disk-verified sources, see module docstring)
# ============================================================================================
SURFACE_PLATEAU_CITATION = {
    "source": "data/exp_narrative_goal_outcome_role_sharded_generality_v1/metrics.json",
    "naive_flat_mean_acc": 0.6100,
    "role_shard_weighted_mean_acc": 0.6000,
    "majority_acc": 0.5000,
}
SURFACE_PLATEAU = 0.60
INC2_CITATION = {
    "source": "data/exp_narrative_goal_outcome_achievement_comparison_learnable_grounded_v1/metrics.json",
    "commit": "9c4439e92",
    "owned_acc": 0.45, "owned_fire_rate": 0.15, "owned_acc_when_fired": 0.0, "owned_n_fired": 3,
    "referent_recur_verdict_train_fire": "6/30",
    "referent_recur_verdict_train_purity": {"MET": [4, 5, 0.8], "UNMET": [1, 1, 1.0]},
}

# ============================================================================================
# GOAL-REFERENT extraction (destination-PP fallback, orthographic proper-noun proxy)
# ============================================================================================
def _is_capitalized_in_source(orig_text, token_lower):
    """True iff `token_lower`'s first case-insensitive whole-word occurrence in the ORIGINAL
    (un-lowercased) source text is capitalized -- a cheap orthographic proper-noun proxy (place/
    person names), NOT a semantic content lexicon."""
    if not token_lower:
        return False
    m = re.search(r"\b" + re.escape(token_lower) + r"\b", orig_text, flags=re.IGNORECASE)
    return bool(m) and m.group(0)[0:1].isupper()


def _destination_after_verb(toks, vlemma, orig_sentence):
    """When the embedded verb (first surface token lemmatizing to `vlemma`) is IMMEDIATELY followed
    by a bare 'to' (no direct object -- find_desired_state's own object scan, _object_referent_after,
    stops dead at that 'to' by design), extract the NP after it as a DESTINATION referent, but ONLY
    if its head is capitalized in `orig_sentence` (proper-noun proxy). Returns None otherwise --
    never overrides a genuine direct-object referent (caller only consults this as a fallback)."""
    v_idx = next((i for i, t in enumerate(toks) if lemma_verb(t) == vlemma), None)
    if v_idx is None:
        return None
    j = v_idx + 1
    if j >= len(toks) or toks[j] != "to":
        return None
    k = j + 1
    while k < len(toks) and toks[k] not in _STOP_BOUNDARY and toks[k] != "to":
        k += 1
    head = _np_last_content(toks[j + 1:k])
    if head is not None and _is_capitalized_in_source(orig_sentence, head):
        return head
    return None


def extract_goal_referent(goal_text):
    """Scan goal_text sentences in order (production find_desired_state convention: first
    goal-bearing sentence wins); for EACH, prefer the destination-PP fallback over
    find_desired_state's own object-only referent when the destination fallback fires (a strict
    upgrade -- the object scan returns None/junk for a bare motion-to-destination pattern); accept
    the first referent that clears _referent_recurrence_eligible (owned specificity/pronoun/vague-
    noun gate). Returns (referent_or_None, meta_dict)."""
    for gs in _sentences(goal_text):
        d = find_desired_state(gs)
        if d is None:
            continue
        toks = _tokens(gs)
        cand = d.get("referent")
        vlemma = d.get("verb_lemma")
        is_destination = False
        if vlemma:
            dest = _destination_after_verb(toks, vlemma, gs)
            if dest is not None:
                cand = dest
                is_destination = True
        if (cand is not None and cand not in _NEG_TRANSPARENT_ADVERBS and cand not in _RELATIVE_JUNK
                and _referent_recurrence_eligible(cand)):
            return cand, {"sentence": gs, "pattern": d.get("pattern"), "verb_lemma": vlemma,
                          "is_destination": is_destination}
    return None, {"reason": "no_eligible_goal_referent"}


# ============================================================================================
# OUTCOME match: literal / pronoun-coref recurrence + negation/abandonment + nesting guard
# ============================================================================================
_ABANDON_LEMMAS = {"cancel", "quit", "abandon"}


def _clause_span_before(toks, idx):
    """Backward scan to the nearest _STOP_BOUNDARY token or sentence start -- the SAME clause-
    scoping convention hdlab.goal_typing uses throughout (_object_referent_after,
    _referent_recurrence_in_sentence)."""
    j = idx - 1
    while j >= 0 and toks[j] not in _STOP_BOUNDARY:
        j -= 1
    return j + 1, toks[j + 1:idx]


def _clause_negated(toks, span_start, idx, full_toks):
    span = toks[span_start:idx]
    if any(_is_negator(t) for t in span):
        return True, "explicit_negator"
    if any(lemma_verb(t) in _ABANDON_LEMMAS for t in span):
        return True, "abandonment_verb"
    for k in range(len(full_toks) - 1):
        if lemma_verb(full_toks[k]) == "give" and full_toks[k + 1] == "up":
            return True, "give_up_phrasal"
    return False, None


def _destination_candidates(toks, orig_text):
    """All bare 'to <capitalized-NP>' heads in `toks` (orthographic proper-noun proxy, same as the
    goal-side fallback) -- candidate REPLACEMENT destinations."""
    cands = []
    for j, t in enumerate(toks):
        if t != "to":
            continue
        k = j + 1
        while k < len(toks) and toks[k] not in _STOP_BOUNDARY and toks[k] != "to":
            k += 1
        head = _np_last_content(toks[j + 1:k])
        if head is not None and _is_capitalized_in_source(orig_text, head):
            cands.append(head)
    return cands


def _accept_link(referent, tok):
    """Wraps hdlab.goal_typing._referent_links with ONE additional guard: gn_compatible (the
    pronoun-coref tier's agreement check) is documented as "compatible unless a KNOWN attribute
    conflicts" -- i.e. an UNKNOWN gender is treated as a wildcard. MEASURED this build: almost every
    referent this probe extracts (place names, activities, objects: "africa"/"anyway"/"fun"/"bike")
    gets infer_nominal_gender==None (no MASC_CUES/FEM_CUES hit), so gn_compatible vacuously accepts
    ANY personal pronoun in the outcome sentence ("her"/"his"/"it"/"who") as a coreferent -- a
    systematic false-link bug for this use case (production _referent_links is designed for a
    controlled discourse-entity antecedent set, not an arbitrary extracted string vs. every outcome
    token). FIX: only trust pronoun_coref when the GOAL referent itself carries a KNOWN
    (non-wildcard) inferred gender (a real gendered common noun like "sister"/"mother") -- never for
    an unknown-gender referent, where the tier would be vacuous. LITERAL tier is unaffected (never
    gated)."""
    linked, tier = _referent_links(referent, tok)
    if not linked or tier not in ("literal", "pronoun_coref"):
        return False, tier
    if tier == "pronoun_coref" and infer_nominal_gender(referent.split()) is None:
        return False, "pronoun_coref_vacuous_gender_rejected"
    return True, tier


def type_item(goal_text, outcome_text):
    """The lexicon-independent referent-recurrence typer. Returns (verdict, detail) where verdict in
    {"MET", "UNMET", "NA"}."""
    referent, gmeta = extract_goal_referent(goal_text)
    if referent is None:
        return "NA", {"reason": "no_eligible_goal_referent", "goal_meta": gmeta}

    out_toks = _tokens(outcome_text)
    for idx, tok in enumerate(out_toks):
        linked, tier = _accept_link(referent, tok)
        if not linked:
            continue
        span_start, span = _clause_span_before(out_toks, idx)
        negated, neg_reason = _clause_negated(out_toks, span_start, idx, out_toks)
        nested = "of" in span
        base = {"referent": referent, "goal_meta": gmeta, "matched_token": tok, "tier": tier,
                "clause": span, "negated": negated, "neg_reason": neg_reason, "nested_of": nested}
        if negated:
            return "UNMET", {**base, "reason": "referent_recurs_negated"}
        if nested:
            return "NA", {**base, "reason": "referent_recurs_nested_ambiguous"}
        return "MET", {**base, "reason": "referent_recurs_realized"}

    if gmeta.get("is_destination"):
        rivals = [r for r in _destination_candidates(out_toks, outcome_text) if r != referent]
        if rivals:
            return "UNMET", {"referent": referent, "goal_meta": gmeta, "reason": "referent_replaced",
                             "replacement": rivals[0]}
    return "NA", {"referent": referent, "goal_meta": gmeta, "reason": "no_recurrence_no_replacement"}


def item_features(item):
    """4 booleans for the LEARNER arm: recurs / negated / replaced / realized. 'realized' = recurs
    and neither negated nor nested -- the MET-signaling combination."""
    verdict, detail = type_item(item["goal_text"], item["outcome_text"])
    reason = detail.get("reason")
    recurs = reason in ("referent_recurs_negated", "referent_recurs_nested_ambiguous",
                        "referent_recurs_realized")
    negated = reason == "referent_recurs_negated"
    replaced = reason == "referent_replaced"
    realized = reason == "referent_recurs_realized"
    feats = []
    if recurs:
        feats.append("recurs=True")
    if negated:
        feats.append("negated=True")
    if replaced:
        feats.append("replaced=True")
    if realized:
        feats.append("realized=True")
    return verdict, detail, feats


# ============================================================================================
# main
# ============================================================================================
HYP_SPACE_SPEC = dict(
    candidate_plugins=["ruleind"], min_coverage=1, purity_thresh=0.9, max_conjunct=2, max_rules=4,
    key_fn=lambda inst: tuple(sorted(inst["feats"])),
)


def _digest(seq):
    return hashlib.sha256(json.dumps(list(seq)).encode()).hexdigest()[:16]


def forced_predict(verdict, majority_cls):
    return verdict if verdict in ("MET", "UNMET") else majority_cls


def run_arm_hand_rule(items, majority_cls):
    preds_forced, gold, fired_preds, fired_gold, debug = [], [], [], [], []
    for it in items:
        verdict, detail, feats = item_features(it)
        gold.append(it["gold"])
        preds_forced.append(forced_predict(verdict, majority_cls))
        if verdict in ("MET", "UNMET"):
            fired_preds.append(verdict)
            fired_gold.append(it["gold"])
        debug.append({"id": it["id"], "gold": it["gold"], "verdict": verdict,
                      "referent": detail.get("referent"), "reason": detail.get("reason"),
                      "matched_token": detail.get("matched_token"),
                      "negated": detail.get("negated"), "nested_of": detail.get("nested_of"),
                      "replacement": detail.get("replacement"), "feats": feats})
    return {
        "forced_acc": accuracy(preds_forced, gold),
        "fire_rate": len(fired_preds) / len(items) if items else 0.0,
        "n_fired": len(fired_preds),
        "acc_when_fired": accuracy(fired_preds, fired_gold) if fired_preds else None,
        "n_distinct_preds": len(set(preds_forced)),
        "digest": _digest(preds_forced),
        "debug": debug,
    }


def run_arm_learner(train_items, test_items, majority_cls):
    train_eps = []
    for it in train_items:
        _, _, feats = item_features(it)
        train_eps.append({"feats": feats, "gold_class": it["gold"]})
    chosen_name, chosen, all_results = learner_learn(
        train_eps, lambda inst: inst["feats"], HYP_SPACE_SPEC)
    preds = []
    for it in test_items:
        _, _, feats = item_features(it)
        if chosen is None:
            preds.append(majority_cls)
        else:
            preds.append(learner_apply(chosen_name, chosen.hypothesis, feats, key=None,
                                       default_class=majority_cls))
    gold = [it["gold"] for it in test_items]
    return {
        "chosen_plugin": chosen_name, "non_episodic": chosen is not None,
        "hypothesis": (chosen.hypothesis if chosen is not None else None),
        "acc": accuracy(preds, gold), "n_distinct_preds": len(set(preds)), "digest": _digest(preds),
        "preds": preds,
    }


def run_arm_owned(items, majority_cls, fn):
    preds_forced, gold, fired_preds, fired_gold = [], [], [], []
    for it in items:
        verdict, _detail = fn(it["text"])
        gold.append(it["gold"])
        preds_forced.append(forced_predict(verdict, majority_cls))
        if verdict in ("MET", "UNMET"):
            fired_preds.append(verdict)
            fired_gold.append(it["gold"])
    return {
        "forced_acc": accuracy(preds_forced, gold),
        "fire_rate": len(fired_preds) / len(items) if items else 0.0,
        "n_fired": len(fired_preds),
        "acc_when_fired": accuracy(fired_preds, fired_gold) if fired_preds else None,
    }


def scramble_items(test_items, offset=1):
    """Deterministic offset-cyclic rotation of outcome_text against goal_text -- guarantees a
    derangement for n>1 with zero RNG. goal_text/id/gold stay with the original item; outcome_text
    (and outcome_text-derived 'text') come from the item `offset` positions ahead."""
    n = len(test_items)
    out = []
    for i, it in enumerate(test_items):
        donor = test_items[(i + offset) % n]
        new_it = dict(it)
        new_it["outcome_text"] = donor["outcome_text"]
        new_it["text"] = it["goal_text"] + " " + donor["outcome_text"]
        out.append(new_it)
    return out


def self_test(items, split_result, hand_all, hand_test, learn_res, scramble_res, owned_res,
              owned_rr_res, majority_acc_val):
    ok = True
    msgs = []
    train, test = split_result
    if not (len(items) == 50 and len(train) == 30 and len(test) == 20):
        ok = False
        msgs.append("split size mismatch: n=%d n_train=%d n_test=%d" % (len(items), len(train), len(test)))
    if abs(majority_acc_val - 0.5000) > 1e-9:
        ok = False
        msgs.append("majority_acc != 0.5000 (%.4f) -- split not byte-identical to generality cell" % majority_acc_val)
    if hand_test["n_distinct_preds"] < 2:
        ok = False
        msgs.append("hand-rule TEST predictions constant (n_distinct_preds=%d)" % hand_test["n_distinct_preds"])
    # spot-check two hand-derived items (independently reasoned through in the design phase, not
    # tuned against this run's output)
    by_id = {d["id"]: d for d in hand_all["debug"]}
    spot = {
        "rocs_bernice_africa_trip_unmet": ("UNMET", "referent_replaced"),
        "rocs_ryan_bike_led_unmet": ("UNMET", "referent_recurs_negated"),
        "rocs_ryan_bike_led_met": ("MET", "referent_recurs_realized"),
    }
    for iid, (exp_v, exp_r) in spot.items():
        d = by_id.get(iid)
        if d is None:
            ok = False
            msgs.append("spot item missing: %s" % iid)
            continue
        if d["verdict"] != exp_v or d["reason"] != exp_r:
            ok = False
            msgs.append("spot-check MISS %s: got verdict=%s reason=%s, expected %s/%s"
                        % (iid, d["verdict"], d["reason"], exp_v, exp_r))
    # determinism: rerun hand-rule twice, predictions must match bit-for-bit
    preds_a = [forced_predict(type_item(it["goal_text"], it["outcome_text"])[0], "UNMET") for it in test]
    preds_b = [forced_predict(type_item(it["goal_text"], it["outcome_text"])[0], "UNMET") for it in test]
    if preds_a != preds_b:
        ok = False
        msgs.append("hand-rule NOT deterministic across two runs")
    if scramble_res["fire_rate"] >= hand_test["fire_rate"] and hand_test["fire_rate"] > 0:
        msgs.append("NOTE: scramble fire_rate (%.3f) did not drop below unscrambled (%.3f)"
                    % (scramble_res["fire_rate"], hand_test["fire_rate"]))
    return ok, msgs


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    items = load_items()
    train, test = stratified_split(items)
    majority_cls = majority_class(test)
    majority_acc_val = accuracy([majority_cls] * len(test), [it["gold"] for it in test])

    hand_all = run_arm_hand_rule(items, majority_cls)          # full 50, for spot-checks/diagnosis
    hand_train = run_arm_hand_rule(train, majority_cls)
    hand_test = run_arm_hand_rule(test, majority_cls)
    learn_res = run_arm_learner(train, test, majority_cls)
    owned_res = run_arm_owned(test, majority_cls, congruence_outcome_valence_windowed)
    owned_rr_res = run_arm_owned(test, majority_cls, congruence_referent_recurrence_windowed)

    scrambled_test = scramble_items(test, offset=1)
    scramble_res = run_arm_hand_rule(scrambled_test, majority_cls)

    # ---- DIAGNOSIS: literal-crackable vs semantic-needs-grounding split (full 50) ----
    fired_ids = {d["id"] for d in hand_all["debug"] if d["verdict"] in ("MET", "UNMET")}
    correct_fired = {d["id"] for d in hand_all["debug"]
                     if d["verdict"] in ("MET", "UNMET") and d["verdict"] == d["gold"]}
    literal_crackable_frac = len(correct_fired) / len(items)
    semantic_needs_grounding_frac = 1.0 - (len(fired_ids) / len(items))

    ok, self_test_msgs = self_test(items, (train, test), hand_all, hand_test, learn_res,
                                    scramble_res, owned_res, owned_rr_res, majority_acc_val)

    best_arm_name = "HAND-RULE" if hand_test["forced_acc"] >= learn_res["acc"] else "LEARNER"
    best_acc = max(hand_test["forced_acc"], learn_res["acc"])
    beats_plateau = best_acc > SURFACE_PLATEAU
    beats_majority = best_acc > majority_acc_val
    non_constant = hand_test["n_distinct_preds"] > 1 and learn_res["n_distinct_preds"] > 1
    scramble_collapses = (scramble_res["forced_acc"] <= majority_acc_val + 0.05
                          or scramble_res["fire_rate"] <= hand_test["fire_rate"] * 0.5 + 1e-9)

    if beats_plateau and beats_majority and non_constant and scramble_collapses:
        verdict = "HARD_PASS"
        verdict_msg = ("%s held-out forced_acc=%.4f beats SURFACE_PLATEAU=%.2f AND majority=%.4f, "
                       "non-constant, scramble collapses (forced_acc=%.4f, fire_rate %.3f->%.3f) -- "
                       "structural referent-resolution cracks narrative met/unmet LEXICON-"
                       "INDEPENDENTLY." % (best_arm_name, best_acc, SURFACE_PLATEAU, majority_acc_val,
                                           scramble_res["forced_acc"], hand_test["fire_rate"],
                                           scramble_res["fire_rate"]))
    else:
        verdict = "PARTIAL"
        verdict_msg = (
            "%s held-out forced_acc=%.4f (vs SURFACE_PLATEAU=%.2f, majority=%.4f); HAND-RULE fires "
            "on %d/%d test items (fire_rate=%.3f) at acc_when_fired=%s; full-50 diagnosis: "
            "literal-crackable(correct-fired)/50=%.3f, semantic-needs-grounding(never-fired)/50=%.3f. "
            "Gate flags: beats_plateau=%s beats_majority=%s non_constant=%s scramble_collapses=%s."
            % (best_arm_name, best_acc, SURFACE_PLATEAU, majority_acc_val, hand_test["n_fired"],
               len(test), hand_test["fire_rate"],
               ("%.4f" % hand_test["acc_when_fired"]) if hand_test["acc_when_fired"] is not None else "NA",
               literal_crackable_frac, semantic_needs_grounding_frac,
               beats_plateau, beats_majority, non_constant, scramble_collapses))
    if not ok:
        verdict = "SELFTEST_FAIL"
        verdict_msg = "SELF-TEST FAILED: " + " | ".join(self_test_msgs) + " || " + verdict_msg

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "self_test_ok": ok,
        "self_test_msgs": self_test_msgs,
        "elapsed_s": round(time.time() - t0, 3), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "n_items": len(items), "n_train": len(train), "n_test": len(test),
        "majority_class": majority_cls, "majority_acc": majority_acc_val,
        "surface_plateau_citation": SURFACE_PLATEAU_CITATION, "surface_plateau": SURFACE_PLATEAU,
        "inc2_citation": INC2_CITATION,
        "hand_rule": {"full50": {k: v for k, v in hand_all.items() if k != "debug"},
                     "train": {k: v for k, v in hand_train.items() if k != "debug"},
                     "test": {k: v for k, v in hand_test.items() if k != "debug"}},
        "learner": learn_res,
        "owned_congruence_outcome_valence_windowed_test": owned_res,
        "owned_congruence_referent_recurrence_windowed_test": owned_rr_res,
        "scramble_test": {k: v for k, v in scramble_res.items() if k != "debug"},
        "diagnosis": {
            "literal_crackable_correct_fired_over_50": literal_crackable_frac,
            "semantic_needs_grounding_never_fired_over_50": semantic_needs_grounding_frac,
            "n_fired_over_50": len(fired_ids), "n_correct_fired_over_50": len(correct_fired),
        },
        "best_arm_name": best_arm_name, "best_acc": best_acc,
        "beats_plateau": beats_plateau, "beats_majority": beats_majority,
        "non_constant": non_constant, "scramble_collapses": scramble_collapses,
        "glass_box_full50": hand_all["debug"],
        "glass_box_test20": hand_test["debug"],
        "glass_box_scrambled_test20": scramble_res["debug"],
    }
    out_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=True)

    print("=" * 100)
    print("VERDICT:", verdict)
    print(verdict_msg)
    print("SELF-TEST:", "PASS" if ok else "FAIL", self_test_msgs)
    print("-" * 100)
    print("n_items=%d n_train=%d n_test=%d majority_class=%s majority_acc=%.4f"
         % (len(items), len(train), len(test), majority_cls, majority_acc_val))
    print("SURFACE_PLATEAU (cited)=%.2f  INC2 owned_acc(test)=%.2f owned_fire_rate=%.2f "
         "owned_acc_when_fired=%.2f" % (SURFACE_PLATEAU, INC2_CITATION["owned_acc"],
                                        INC2_CITATION["owned_fire_rate"], INC2_CITATION["owned_acc_when_fired"]))
    print("-" * 100)
    print("HAND-RULE  test forced_acc=%.4f  fire_rate=%.3f (%d/%d)  acc_when_fired=%s  n_distinct=%d  digest=%s"
         % (hand_test["forced_acc"], hand_test["fire_rate"], hand_test["n_fired"], len(test),
            ("%.4f" % hand_test["acc_when_fired"]) if hand_test["acc_when_fired"] is not None else "NA",
            hand_test["n_distinct_preds"], hand_test["digest"]))
    print("LEARNER    test acc=%.4f  chosen_plugin=%s  non_episodic=%s  n_distinct=%d  digest=%s"
         % (learn_res["acc"], learn_res["chosen_plugin"], learn_res["non_episodic"],
            learn_res["n_distinct_preds"], learn_res["digest"]))
    print("OWNED congruence_outcome_valence_windowed  test forced_acc=%.4f fire_rate=%.3f acc_when_fired=%s"
         % (owned_res["forced_acc"], owned_res["fire_rate"],
            ("%.4f" % owned_res["acc_when_fired"]) if owned_res["acc_when_fired"] is not None else "NA"))
    print("OWNED congruence_referent_recurrence_windowed (LEXICON-USING) test forced_acc=%.4f fire_rate=%.3f acc_when_fired=%s"
         % (owned_rr_res["forced_acc"], owned_rr_res["fire_rate"],
            ("%.4f" % owned_rr_res["acc_when_fired"]) if owned_rr_res["acc_when_fired"] is not None else "NA"))
    print("SCRAMBLE   test forced_acc=%.4f  fire_rate=%.3f (unscrambled fire_rate=%.3f)"
         % (scramble_res["forced_acc"], scramble_res["fire_rate"], hand_test["fire_rate"]))
    print("-" * 100)
    print("DIAGNOSIS (full 50): literal-crackable(correct-fired)/50=%.3f (%d/50)  "
         "semantic-needs-grounding(never-fired)/50=%.3f (%d/50)"
         % (literal_crackable_frac, len(correct_fired), semantic_needs_grounding_frac,
            50 - len(fired_ids)))
    print("-" * 100)
    print("GLASS-BOX (test 20, id | gold | verdict | referent | reason):")
    for d in hand_test["debug"]:
        print("  %-42s gold=%-6s verdict=%-6s referent=%-14s reason=%s"
             % (d["id"], d["gold"], d["verdict"], d["referent"], d["reason"]))
    print("=" * 100)
    print("metrics written to", out_path)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
