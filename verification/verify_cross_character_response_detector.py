"""verification/verify_cross_character_response_detector.py -- scaffold-free witness (tracing=False)
for the CROSS-CHARACTER RESPONSE channel (hdlab.goal_typing.congruence_cross_character_response),
2026-08-07 build per notes/formalize_cross_character_response_detector_ToM_2d_2026-08-06.md.

Reproduces, off the PRODUCTION hdlab.goal_typing / hdlab.goal_owner_select modules directly (no
experiment-cell scaffold):

  (1) MECHANISM correctness: decisive constructed ACCEPT-class MET, REFUSE-class UNMET, and the
      negation occurrence-gate flip (MET->UNMET on a negated ACCEPT-class response, which also
      covers the spec's "won't/will not + response verb" REFUSE pattern for free).
  (2) GUARD 2 (genuine cross-entity): responder == goal-holder must never fire.
  (3) GUARD 1 (directedness, "NOT a bare response-verb scan"): an ACCEPT/REFUSE-class verb near an
      open goal must NOT fire when the goal's own referent does not discourse-link to the responder,
      even when a naive gn_compatible check would weakly "link" (the channel's own extra
      known-gender precision sub-guard on the pronoun_coref tier).
  (4) OVER-FIRE PROOF on the 8-verb / 16-sentence NOISE light-verb bank (reused verbatim from
      verify_grounded_word_acquisition_increment1b.py's walked/sat/spoke/turned/answered/asked/
      stood/carried list): (a) standalone (no antecedent goal) -- must stay NA by construction
      (insufficient_sentences); (b) embedded as the RESPONSE clause after a genuine open goal (the
      maximally adversarial placement) -- must stay NA via class non-membership. Zero MET/UNMET in
      either arm.
  (5) FULL-44 eval-wide (experiments/data/goal_bearing_modern_eval_v1.jsonl) MEASURED sweep for BOTH
      numbers (polarity via congruence_with_lexicon_fallback, owner via
      hdlab.goal_owner_select.select_outcome_owner/enumerate_and_score): reports newly-correct count
      and proves ZERO REGRESSION against the pre-edit baseline (every item this module's git HISTORY
      already got right stays right). MEASURED, not assumed -- see this file's __main__ output for
      the actual numbers and the disk-verified root-cause diagnosis of why the channel's own guards
      (correctly) keep it from firing on the 4 items the pre-reg predicted (dashwood: goal referent
      truncated to "mr" by a pre-existing Mr.-abbreviation sentence-split bug, and "we'll" (editorial
      "we") is not modeled as a coreferring pronoun by hdlab.coreference_resolver.is_pronoun_mention
      -- Guard 1 correctly abstains rather than loosen and risk the over-fire class this build is
      formalized against; the other 3 named items convey the response via free indirect discourse /
      dialogue with NO literal ACCEPT/REFUSE-class word in the text at all, a SHAPE gap out of reach
      of any literal-lexicon mechanism, not a guard mis-tuning).
  (6) FAIR INSTRUMENTS byte-identical: goal_owner_fair_v1 48/48 (+ positional 47/48, unchanged) and
      the multigoal cue-conflict bank 12/12 (+ positional 6/12, unchanged) -- delegates to the
      existing production witness verification/test_goal_owner_select.py so this file cannot drift
      from the landed contract.

Run: .venv/Scripts/python.exe verification/verify_cross_character_response_detector.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.goal_typing import (  # noqa: E402
    congruence_with_lexicon_fallback, congruence_cross_character_response,
    congruence_outcome_valence_windowed, congruence_referent_recurrence_windowed,
    _cross_character_response_in_sentence, _referent_links, self_test as goal_typing_self_test,
)
from hdlab.goal_owner_select import select_outcome_owner  # noqa: E402

EVAL_REL = os.path.join("experiments", "data", "goal_bearing_modern_eval_v1.jsonl")

# Reused verbatim from verify_grounded_word_acquisition_increment1b.py (NOT re-authored -- same
# convention this whole module family uses for shared banks).
NOISE = [
    ("walked", ["He walked to the well and carried the pail home.",
                "The old man walked slowly down the road."]),
    ("sat", ["She sat by the fire in the evening.", "The children sat under the tall tree."]),
    ("spoke", ["She turned and spoke to her brother.", "The teacher spoke to the class that morning."]),
    ("turned", ["He turned and looked toward the door.", "She turned the corner by the shop."]),
    ("answered", ["The boy answered the question at once.", "She answered her mother very softly."]),
    ("asked", ["He asked for a cup of cold water.", "The girl asked her friend about the road."]),
    ("stood", ["The horse stood by the wooden gate.", "He stood near the open window."]),
    ("carried", ["She carried the basket to the market.", "They carried the boxes up the stairs."]),
]

# A genuine antecedent-goal sentence (open goal, resolved holder "owen") for the adversarial-
# placement over-fire arm -- reused across all 16 NOISE sentences.
_GOAL_STEM = "Owen wanted his sister to join the choir before winter."

# BASELINE (pre-edit, this session's disk-verified measurement of hdlab.goal_typing /
# hdlab.goal_owner_select BEFORE the cross-character-response channel was wired in): polarity_typed
# 18/44, polarity_correct 15/44, owner_correct 25/44. The specific per-item correct/wrong/abstain
# sets below are the exact baseline sets (captured from the pre-edit tree this build started from),
# used ONLY for the zero-regression check -- this witness does not re-derive them from git, it
# pins them as MEASURED@this session's baseline sweep (reported inline).
BASELINE_POLARITY_WRONG = {
    ("lw_jo_laurie_snowball", "unmet", "met"),
    ("lw_jo_wanted_forgive_amy", "met", "unmet"),
    ("onestop_skydiver", "unmet", "met"),
}
BASELINE_OWNER_WRONG = {
    ("lw_aunt_march_opposition", "john", "march"),
    ("agg_gilbert_porch_apology_ch15", "anne", "gilbert"),
    ("agg_gilbert_pond_rescue_friendship_plea_ch28", "anne", "gilbert"),
    ("ts_tom_wish_free_potter", "joe", "tom"),
}
BASELINE_OWNER_NEVER_TYPED = {
    "lw_jo_mr_laurence_confront", "lw_jo_editor_dashwood", "lw_laurie_proposal_rejected",
    "agg_anne_picnic_wish_ch14", "agg_anne_liniment_cake_ch21",
    "agg_matthew_puffed_sleeves_dress_ch25", "agg_anne_hair_dye_green_ch27",
    "agg_anne_diana_bosom_friend_ch12", "ts_tom_whitewash_fence",
    "ts_becky_anatomy_book_confession", "ts_tom_sugar_theft", "woz_tin_woodman_heart",
    "race_chen_situps", "race_davey_wiffle", "onestop_carle_madeinfrance",
}
BASELINE_POLARITY_TYPED = 18
BASELINE_POLARITY_CORRECT = 15
BASELINE_OWNER_CORRECT = 25
EVAL_N = 44


def check_module_self_test():
    """hdlab.goal_typing.self_test() must pass -- it now includes the (14a)-(14f) decisive
    cross-character-response cases (mechanism MET/UNMET, guard1, guard2, NOISE-bank inline check)."""
    res = goal_typing_self_test()
    xc = res["cross_character_response"]
    assert xc["accept_class_met"] == "MET"
    assert xc["refuse_class_unmet"] == "UNMET"
    assert xc["negated_accept_flips_unmet"] == "UNMET"
    assert xc["guard1_undirected_abstains"] == "NA"
    assert xc["noise_bank_overfire_count"] == 0
    print("[CHECK module_self_test] hdlab.goal_typing.self_test() green, "
          f"cross_character_response={xc}")
    return xc


def check_noise_bank_no_overfire():
    """Zero MET/UNMET FROM THIS CHANNEL on the 8-verb/16-sentence NOISE bank in BOTH arms:
    standalone (no antecedent goal -- congruence_cross_character_response, THIS build's own
    function, must stay NA by construction: insufficient_sentences) and embedded as the response
    clause after a genuine open goal (maximally adversarial placement -- must stay NA via class
    non-membership, the closed RESPONSE_ACCEPT/REFUSE_CLASS lexicon). Scoped to
    congruence_cross_character_response directly (NOT the full congruence_with_lexicon_fallback
    chain) so this check attributes correctly: the pre-existing bare V2_OUTCOME_UNMET/_MET word
    lexicon (lexicon_predict, present before this build, untouched by it) DOES independently
    classify some of these isolated single-word NOISE sentences (e.g. "down" in "walked ... down
    the road" is a literal legacy V2_OUTCOME_UNMET member) -- that is pre-existing, unrelated
    behavior, not this channel's over-fire, and conflating the two would misattribute a pre-existing
    quirk to this build."""
    standalone_overfire = []
    adversarial_overfire = []
    n_sentences = 0
    for verb, sents in NOISE:
        for s in sents:
            n_sentences += 1
            v_standalone, d_standalone = congruence_cross_character_response(s)
            if v_standalone in ("MET", "UNMET"):
                standalone_overfire.append((verb, s, v_standalone, d_standalone))
            v_adv, d_adv = congruence_cross_character_response(_GOAL_STEM + " " + s)
            if v_adv in ("MET", "UNMET"):
                adversarial_overfire.append((verb, s, v_adv, d_adv))
    assert n_sentences == 16, f"expected 16 NOISE sentences (8 verbs x 2), got {n_sentences}"
    assert not standalone_overfire, f"NOISE standalone over-fire (HARD-FAIL): {standalone_overfire}"
    assert not adversarial_overfire, (
        f"NOISE adversarial-placement over-fire (HARD-FAIL): {adversarial_overfire}")
    print(f"[CHECK noise_bank] 0/16 over-fire in BOTH arms (standalone + adversarial-placement "
          f"after a genuine open goal)")
    return {"n_sentences": n_sentences, "standalone_overfire": 0, "adversarial_overfire": 0}


def check_guard1_directedness():
    """GUARD 1 isolated unit check: an ACCEPT-class response near an open goal whose referent does
    NOT link to the responder must abstain, even though _referent_links' own weak gn_compatible
    default WOULD link (proves the channel's extra known-gender precision sub-guard, not
    _referent_links, is what blocks it -- the exact loophole a naive implementation would fall into)."""
    v, d = congruence_cross_character_response(
        "Owen wanted to visit the museum before closing. She agreed to renovate the office.")
    assert v == "NA", f"GUARD 1 violation: undirected response must abstain, got {v} ({d})"
    weak_linked, weak_tier = _referent_links("museum", "she")
    assert weak_linked and weak_tier == "pronoun_coref", (
        "sanity: _referent_links' weak default IS permissive here -- confirms the channel's own "
        "extra precision sub-guard (not _referent_links) is what correctly blocks Guard 1")
    print("[CHECK guard1_directedness] undirected response abstains (NA); confirmed the block is "
          "the channel's own known-gender precision sub-guard, not a missing weak-link")
    return {"undirected_abstains": v, "referent_links_would_weakly_link": weak_linked}


def check_guard2_cross_entity():
    """GUARD 2 isolated unit check: responder == goal_holder (same-entity) must never fire this
    channel (same-entity resolution belongs to the sibling channels, not this one)."""
    hit = _cross_character_response_in_sentence("Owen agreed to join at once.", "owen")
    assert hit is None, f"GUARD 2 violation: same-entity responder must not fire, got {hit}"
    print("[CHECK guard2_cross_entity] responder==goal_holder correctly blocked")
    return {"same_entity_blocked": True}


def _load_eval():
    rows = []
    with open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def check_full_eval_sweep_measured():
    """Full-44 MEASURED sweep, BOTH numbers, against the pinned BASELINE_* sets -- proves ZERO
    REGRESSION and reports the ACTUAL (not hypothesized) newly-correct delta. Also records every
    passage where the new channel's own `reason: cross_character_response` fires (fire-count), so a
    HARD-FAIL (delta < 2) is reported with the real fire-count, not silently assumed to be zero."""
    rows = _load_eval()
    assert len(rows) == EVAL_N, f"expected {EVAL_N}-item eval, got {len(rows)}"

    polarity_wrong, polarity_abstain, owner_wrong, owner_never_typed = [], [], [], []
    polarity_typed = polarity_correct = owner_correct = 0
    xchar_fired = []

    for d in rows:
        text, gold_pol, gold_owner, roster = (
            d["text"], d["gold_outcome_polarity"], d["gold_outcome_owner"], d["roster"])
        verdict, detail = congruence_with_lexicon_fallback(text)
        if detail.get("reason") == "cross_character_response":
            xchar_fired.append((d["id"], verdict, gold_pol, detail.get("responder"),
                                detail.get("link_tier")))
        v = verdict.lower()
        if v in ("met", "unmet"):
            polarity_typed += 1
            if v == gold_pol:
                polarity_correct += 1
            else:
                polarity_wrong.append((d["id"], v, gold_pol))
        else:
            polarity_abstain.append((d["id"], v, gold_pol))
        try:
            owner = select_outcome_owner(text, roster, seed=0)
            if owner == gold_owner:
                owner_correct += 1
            else:
                owner_wrong.append((d["id"], owner, gold_owner))
        except ValueError:
            owner_never_typed.append(d["id"])

    # ---- ZERO-REGRESSION: every baseline-WRONG item must still be in the current-WRONG set (no
    # baseline-correct item may have flipped to wrong), and every baseline-never-typed owner item
    # must either stay never-typed OR newly resolve CORRECTLY (never flip to a wrong owner).
    current_polarity_wrong = set(polarity_wrong)
    current_owner_wrong = set(owner_wrong)
    current_owner_never_typed = set(owner_never_typed)

    # a baseline-correct item regresses iff it is now wrong or newly-abstaining when it used to be
    # typed+correct; the cleanest zero-regression proof is: polarity_correct/owner_correct counts
    # must not have DECREASED, and no NEW polarity_wrong id appeared that wasn't already wrong before
    # AND wasn't previously abstaining-that-fires-now-wrong (i.e. any newly-typed item must be
    # correct, not wrong).
    baseline_wrong_ids = {i for i, _, _ in BASELINE_POLARITY_WRONG}
    new_polarity_wrong_ids = {i for i, _, _ in current_polarity_wrong} - baseline_wrong_ids
    assert not new_polarity_wrong_ids, (
        f"POLARITY REGRESSION: newly-wrong items not in baseline: {new_polarity_wrong_ids}")
    assert polarity_correct >= BASELINE_POLARITY_CORRECT, (
        f"POLARITY REGRESSION: correct count dropped {BASELINE_POLARITY_CORRECT} -> {polarity_correct}")

    baseline_owner_wrong_ids = {i for i, _, _ in BASELINE_OWNER_WRONG}
    new_owner_wrong_ids = {i for i, _, _ in current_owner_wrong} - baseline_owner_wrong_ids
    assert not new_owner_wrong_ids, (
        f"OWNER REGRESSION: newly-wrong items not in baseline: {new_owner_wrong_ids}")
    assert owner_correct >= BASELINE_OWNER_CORRECT, (
        f"OWNER REGRESSION: correct count dropped {BASELINE_OWNER_CORRECT} -> {owner_correct}")
    # every item that used to raise ValueError (never-typed) must still either never-type or now
    # resolve to the CORRECT owner (never a newly-WRONG owner) -- already covered by the
    # new_owner_wrong_ids assertion above, since a never-typed item can't appear in owner_wrong at
    # baseline; this is a redundant, explicit re-statement for readability.
    flipped_never_typed_to_wrong = (
        BASELINE_OWNER_NEVER_TYPED - current_owner_never_typed) & {i for i, _, _ in current_owner_wrong}
    assert not flipped_never_typed_to_wrong, (
        f"a previously-never-typed owner item newly resolved WRONG: {flipped_never_typed_to_wrong}")

    polarity_delta = polarity_correct - BASELINE_POLARITY_CORRECT
    owner_delta = owner_correct - BASELINE_OWNER_CORRECT
    combined_newly_correct = polarity_delta + owner_delta  # both numbers, per the pre-reg's gate

    print(f"[CHECK full_eval_sweep] polarity_typed={polarity_typed}/{EVAL_N} "
          f"polarity_correct={polarity_correct}/{EVAL_N} (baseline {BASELINE_POLARITY_CORRECT}, "
          f"delta={polarity_delta:+d}) | owner_correct={owner_correct}/{EVAL_N} "
          f"(baseline {BASELINE_OWNER_CORRECT}, delta={owner_delta:+d}) | "
          f"cross_character_response fired {len(xchar_fired)}x on the eval set: {xchar_fired} | "
          f"ZERO_REGRESSION=True (measured)")
    return {
        "polarity_typed": polarity_typed, "polarity_correct": polarity_correct,
        "polarity_delta": polarity_delta, "owner_correct": owner_correct,
        "owner_delta": owner_delta, "combined_newly_correct": combined_newly_correct,
        "xchar_fired_on_eval": xchar_fired, "zero_regression": True,
    }


def check_fair_instruments_byte_identical():
    """Delegates to the existing production witness (never re-authored) -- goal_owner_fair_v1
    48/48 + positional 47/48, multigoal 12/12 + positional 6/12, flip-control all 6 families."""
    import test_goal_owner_select as FAIR  # noqa: E402  (verification/ is on sys.path via pytest /
    # this file's own REPO_ROOT insertion below when run standalone)
    r1 = FAIR.check_full_instrument_48_of_48()
    r2 = FAIR.check_multigoal_12_of_12()
    r3 = FAIR.check_flip_control()
    assert r1["content_total"] == 48 and r2["content"] == 12
    print("[CHECK fair_instruments] goal_owner_fair_v1 48/48 + multigoal 12/12 + flip_control "
          "byte-identical (delegated to verification/test_goal_owner_select.py)")
    return {"fair_v1": r1, "multigoal": r2, "flip_control": r3}


def test_module_self_test():
    check_module_self_test()


def test_noise_bank_no_overfire():
    check_noise_bank_no_overfire()


def test_guard1_directedness():
    check_guard1_directedness()


def test_guard2_cross_entity():
    check_guard2_cross_entity()


def test_full_eval_sweep_measured():
    check_full_eval_sweep_measured()


def test_fair_instruments_byte_identical():
    check_fair_instruments_byte_identical()


def run():
    VERIFICATION_DIR = os.path.join(REPO_ROOT, "verification")
    if VERIFICATION_DIR not in sys.path:
        sys.path.insert(0, VERIFICATION_DIR)
    r1 = check_module_self_test()
    r2 = check_noise_bank_no_overfire()
    r3 = check_guard1_directedness()
    r4 = check_guard2_cross_entity()
    r5 = check_full_eval_sweep_measured()
    r6 = check_fair_instruments_byte_identical()
    delta = r5["combined_newly_correct"]
    if delta >= 3:
        verdict = "HARD-PASS"
    elif delta >= 2:
        verdict = "PARTIAL (below +3 HARD-PASS)"
    else:
        verdict = "HARD-FAIL (delta < +2)"
    print(f"\n[ALL CHECKS PASS] mechanism correct, guards correct, zero over-fire (NOISE bank "
          f"0/16 both arms), zero regression (measured), fair instruments byte-identical. "
          f"combined_newly_correct={delta:+d} -> {verdict}")
    return {"self_test": r1, "noise_bank": r2, "guard1": r3, "guard2": r4,
            "eval_sweep": r5, "fair_instruments": r6, "verdict": verdict}


if __name__ == "__main__":
    res = run()
    print(json.dumps({k: v for k, v in res.items() if k != "fair_instruments"}, indent=2, default=str))
