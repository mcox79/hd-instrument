# SCAFFOLD-FREE WITNESS (2026-08-07). Reproduces the REQUEST-RESPONSE OUTCOME-TYPING build off the
# LIVE promoted organ (hdlab/goal_typing.py), no tracing (tracing=False -- this organ takes no
# tracing flag; it is pure string/set membership, same convention as
# verify_grounded_result_class_tier.py / verify_dialogue_goal_recognition.py).
"""verify_request_response_typing.py -- asserts the HARD-PASS floors of the 2026-08-07
REQUEST-RESPONSE outcome-typing build: the downstream companion to the DIALOGUE-GOAL RECOGNITION
build (commit 2747fac9a) that completes the competency end-to-end (recognition -> typing).

hdlab.goal_typing.congruence_request_response is wired inside congruence_with_lexicon_fallback as
the 4th (last-resort) tier, consulted after congruence_outcome_valence_windowed,
congruence_referent_recurrence_windowed, and congruence_grounded_result_class -- PLUS a
DIALOGUE_REQUEST_PATTERNS-gated priority fix: any of those 3 tiers' non-NA verdicts is deferred to
congruence_request_response when that verdict's own antecedent goal is a recognized dialogue-request
construction (those tiers were never designed/validated for illocutionary request/response
resolution and can produce a confident-but-wrong verdict via a coincidental verb-class collision --
see hdlab/goal_typing.py's congruence_with_lexicon_fallback docstring, "ORDERING" paragraph, for the
MEASURED regression case this closes). If congruence_request_response itself abstains, the original
tier's verdict is used exactly as it would have been anyway -- so this reordering can never produce a
worse answer than before this build, only a chance at a better one.

Checks:
  (1) TARGET RECOVERY (both pre-reg targets, via congruence_with_lexicon_fallback on the FULL
      passage, exactly how the real_text_goal_owner_diagnostic_v1 set is scored):
        mg3_boy_at_garden_gate (gold UNMET) -- REFUSED via REQUEST_LET "let me in" echoed negated
          ("I will not let YOU in") in the gardener's next turn.
        mg3_frank_garden_invited (gold MET) -- GRANTED via HEDGED_MODAL_WISH "wish...open the gate"
          answered by a grant-verb ("kindly invited him...to come into the garden") in the very next
          sentence.
      Both must resolve to gold via congruence_with_lexicon_fallback AND via
      hdlab.goal_owner_select.select_outcome_owner (owner-path 2a unification propagation).
  (2) REAL_TEXT SET (10 items, real_text_goal_owner_diagnostic_v1.jsonl): before (3-tier-chain
      replay, i.e. this build's own frozen "before" -- what congruence_with_lexicon_fallback WAS
      before this build) vs after (current organ) -- MUST show +2 net correct (the two targets), ZERO
      regressions elsewhere.
  (3) FULL-44 (goal_bearing_modern_eval_v1.jsonl): before vs after, ZERO regressions (neither target
      item lives in this bank, so no gain is expected here -- this check is a pure non-regression
      gate on the DIALOGUE_REQUEST_PATTERNS-gated reordering, which must be a no-op for every
      non-dialogue-request antecedent).
  (4) FAIR INSTRUMENTS byte-identical: verification/test_goal_owner_select.py's 48/48 full instrument
      + 12/12 multigoal, reproduced via its own run() (imported, not reimplemented).
  (5) ZERO OVER-FIRE: congruence_request_response itself must abstain (NA) on:
        (a) 5 constructed adversarial dialogues (unrelated 3rd-party echo, unrelated grant-verb sense
            with no person object, a delayed-reversal-beyond-window construction, own-turn narration
            with no response signal, a coincidental-verb-echo-unrelated-referent construction);
        (b) the 11-item PRECISION_CONTROLS goal-recognition precision bank (imported from
            verify_goal_recognition_coverage_expansion, wrapped as a 2-sentence passage);
        (c) the 6-item ADVERSARIAL_NON_GOALS dialogue bank (same wrapping).
  (6) NOISE anti-drift: 0 false request-response fires on an 8-verb noise bank crossed with 2 request
      goal-openers (reused convention from verify_grounded_result_class_tier.py).
  (7) hdlab.goal_typing.self_test() stays green (this build did not touch any decisive-case
      assertion).
  (8) `python verification/run_certification.py` == 220 passed / 3 skipped (checked by the caller;
      not reproduced here since it is a separate process, not an importable function).

Run: .venv/Scripts/python.exe verification/verify_request_response_typing.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
VERIFICATION_DIR = os.path.dirname(os.path.abspath(__file__))
if VERIFICATION_DIR not in sys.path:
    sys.path.insert(0, VERIFICATION_DIR)

import hdlab.goal_typing as G  # noqa: E402
from hdlab.goal_owner_select import select_outcome_owner  # noqa: E402
import verify_goal_recognition_coverage_expansion as _coverage_witness  # noqa: E402

EVAL44_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"
REALTEXT_REL = "experiments/data/real_text_goal_owner_diagnostic_v1.jsonl"

TARGET_IDS = ["mg3_boy_at_garden_gate", "mg3_frank_garden_invited"]
EXPECTED_REALTEXT_BEFORE = 4
EXPECTED_REALTEXT_AFTER = 6
EXPECTED_FULL44_BEFORE = 17
EXPECTED_FULL44_AFTER = 17

# ADVERSARIAL DIALOGUES (constructed for this build's over-fire probe, per spawn-prompt mandate).
ADVERSARIAL_DIALOGUES = [
    ("adv1_unrelated_3rd_party_let",
     '"Let me in," the boy pleaded at the gate. Just then, a stray cat let itself in through a gap '
     'in the fence.'),
    ("adv2_unrelated_grant_verb_no_person_object",
     '"May I join the club?" Tom asked. The school proudly invited entries for the science fair.'),
    ("adv3_delayed_reversal_beyond_window",
     '"Let me in," the boy pleaded. The gardener smiled and nodded. But a moment later he shook his '
     'head and said, "Actually, I will not let you in."'),
    ("adv4_own_turn_no_response_signal",
     '"Let me in!" the boy cried. He waited by the gate for a long while.'),
    ("adv5_coincidental_verb_echo_unrelated_referent",
     '"May I open the shop early?" Tom asked the manager. Later, she opened the report and began '
     'reading.'),
]

NOISE = [("walked", "He walked to the well and carried the pail home"),
         ("sat", "She sat by the fire in the evening"),
         ("spoke", "She turned and spoke to her brother"),
         ("turned", "He turned and looked toward the door"),
         ("answered", "The boy answered the question at once"),
         ("asked", "He asked for a cup of cold water"),
         ("stood", "The horse stood by the wooden gate"),
         ("carried", "She carried the basket to the market")]


def _load(rel):
    rows = [json.loads(l) for l in open(os.path.join(REPO_ROOT, rel), encoding="utf-8") if l.strip()]
    return rows, {r["id"]: r for r in rows}


def _gold(r):
    return "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"


def _before_verdict(passage_text):
    """Replays congruence_with_lexicon_fallback's behavior BEFORE this build: the 3 pre-existing
    tiers (verb-class windowed primary / referent-recurrence / grounded-result-class), no
    request-response tier, no DIALOGUE_REQUEST_PATTERNS-gated reordering."""
    v, det = G.congruence_outcome_valence_windowed(passage_text)
    if v != "NA":
        return v, det
    v2, det2 = G.congruence_referent_recurrence_windowed(passage_text)
    if v2 != "NA":
        return v2, det2
    v3, det3 = G.congruence_grounded_result_class(passage_text)
    if v3 != "NA":
        return v3, det3
    sents = G._sentences(passage_text)
    lex = G.lexicon_predict(sents[-1]) if sents else "NONE"
    return lex, {"reason": "abstain_fallback_to_lexicon", "lexicon_raw": lex}


def check_target_items():
    _rows, d = _load(REALTEXT_REL)
    results = {}
    for tid in TARGET_IDS:
        r = d[tid]
        v, det = G.congruence_with_lexicon_fallback(r["text"])
        owner = select_outcome_owner(r["text"], r["roster"], seed=0)
        results[tid] = {"gold_polarity": _gold(r), "got_polarity": v, "reason": det.get("reason"),
                        "gold_owner": r["gold_outcome_owner"], "got_owner": owner}
        print(f"[CHECK target_items] {tid}: gold_polarity={_gold(r)} got_polarity={v} "
              f"reason={det.get('reason')} gold_owner={r['gold_outcome_owner']!r} got_owner={owner!r}")
        assert v == _gold(r), f"{tid}: polarity must recover to gold, got {v} (gold {_gold(r)})"
        assert det.get("reason", "").startswith("request_response_"), (
            f"{tid}: must recover via the request-response tier specifically, got "
            f"reason={det.get('reason')}")
        assert owner == r["gold_outcome_owner"], (
            f"{tid}: owner-path 2a unification must resolve gold owner, got {owner!r} "
            f"(gold {r['gold_outcome_owner']!r})")
    return results


def check_full_eval_and_zero_regression():
    rows, _d = _load(EVAL44_REL)
    before = {r["id"]: _before_verdict(r["text"])[0] for r in rows}
    after = {r["id"]: G.congruence_with_lexicon_fallback(r["text"])[0] for r in rows}
    b44 = sum(before[r["id"]] == _gold(r) for r in rows)
    a44 = sum(after[r["id"]] == _gold(r) for r in rows)
    changed = [r["id"] for r in rows if before[r["id"]] != after[r["id"]]]
    regressions = [rid for rid in changed
                   if before[rid] == _gold({**_d[rid]}) and after[rid] != _gold(_d[rid])]
    assert b44 == EXPECTED_FULL44_BEFORE, (b44, EXPECTED_FULL44_BEFORE)
    assert a44 == EXPECTED_FULL44_AFTER, (a44, EXPECTED_FULL44_AFTER)
    assert not regressions, f"REGRESSION on full-44: {regressions}"
    assert not changed, (
        f"full-44 verdicts changed but should be a pure no-op (no target item lives in this bank): "
        f"{changed}")
    print(f"[CHECK full44_zero_regression] full44={b44}->{a44}/44 (must be equal; no target item "
          f"in this bank), changed={changed} (must be empty), regressions={regressions} "
          "(must be empty)")
    return {"full44_before": b44, "full44_after": a44, "changed": changed}


def check_real_text_set():
    rows, d = _load(REALTEXT_REL)
    before = {r["id"]: _before_verdict(r["text"])[0] for r in rows}
    after = {r["id"]: G.congruence_with_lexicon_fallback(r["text"])[0] for r in rows}
    b = sum(before[r["id"]] == _gold(r) for r in rows)
    a = sum(after[r["id"]] == _gold(r) for r in rows)
    regressions = [r["id"] for r in rows if before[r["id"]] == _gold(r) and after[r["id"]] != _gold(r)]
    gains = [r["id"] for r in rows if before[r["id"]] != _gold(r) and after[r["id"]] == _gold(r)]
    for r in rows:
        print(f"[CHECK real_text] {r['id']}: gold={_gold(r)} before={before[r['id']]} "
              f"after={after[r['id']]}")
    assert b == EXPECTED_REALTEXT_BEFORE, (b, EXPECTED_REALTEXT_BEFORE)
    assert a == EXPECTED_REALTEXT_AFTER, (a, EXPECTED_REALTEXT_AFTER)
    assert not regressions, f"REGRESSION on real_text set: {regressions}"
    assert sorted(gains) == sorted(TARGET_IDS), (sorted(gains), sorted(TARGET_IDS))
    print(f"[CHECK real_text] real_text={b}->{a}/10, gains={sorted(gains)}, "
          f"regressions={regressions} (must be empty)")
    return {"real_text_before": b, "real_text_after": a, "gains": sorted(gains)}


def check_fair_instruments_unchanged():
    import test_goal_owner_select as FAIR  # noqa: E402
    result = FAIR.run()
    assert result["full_instrument"]["content_total"] == 48
    assert result["multigoal"]["content"] == 12
    print("[CHECK fair_instruments_unchanged] 48/48 fair + 12/12 multigoal reproduced via imported "
          "test_goal_owner_select.run() (byte-identical, unaffected by this strict-scoped build)")
    return result


def check_adversarial_overfire():
    failures = []
    for aid, passage in ADVERSARIAL_DIALOGUES:
        v, det = G.congruence_request_response(passage)
        print(f"[CHECK adversarial_overfire] {aid}: tier_verdict={v} reason={det.get('reason')}")
        if v != "NA":
            failures.append((aid, v, det))
    assert not failures, f"ADVERSARIAL OVER-FIRE: {failures}"
    print(f"[CHECK adversarial_overfire] {len(ADVERSARIAL_DIALOGUES)}/{len(ADVERSARIAL_DIALOGUES)} "
          "constructed adversarial dialogues: zero over-fire from congruence_request_response")
    return {"n_adversarial": len(ADVERSARIAL_DIALOGUES), "failures": failures}


def check_precision_and_non_goal_banks():
    pc_fires = []
    for _tag, sent, _sj in _coverage_witness.PRECISION_CONTROLS:
        passage = f"{sent} Nothing else happened."
        v, det = G.congruence_request_response(passage)
        if v != "NA":
            pc_fires.append((sent, v, det))
    assert not pc_fires, f"PRECISION_CONTROLS over-fire: {pc_fires}"

    non_goals = ["Will you be quiet.", "Let me think.", "May I say.", "I wish you would stop.",
                 "Let me tell you.", "May I help you."]
    ng_fires = []
    for sent in non_goals:
        passage = f"{sent} Nothing else happened."
        v, det = G.congruence_request_response(passage)
        if v != "NA":
            ng_fires.append((sent, v, det))
    assert not ng_fires, f"ADVERSARIAL_NON_GOALS over-fire: {ng_fires}"

    print(f"[CHECK precision_and_non_goal_banks] precision_bank_fires=0/"
          f"{len(_coverage_witness.PRECISION_CONTROLS)}, non_goal_fires=0/{len(non_goals)}")
    return {"precision_fires": 0, "non_goal_fires": 0}


def check_noise_anti_drift():
    leaks = []
    for v_, sent in NOISE:
        for goalp in ["Let me open the greenhouse before winter came",
                      f"May I {v_} to the market before noon"]:
            passage = f"{goalp}. {sent}."
            v, det = G.congruence_with_lexicon_fallback(passage)
            if det.get("reason", "").startswith("request_response_"):
                leaks.append((passage, v, det))
    assert not leaks, f"NOISE anti-drift leaks: {leaks}"
    print(f"[CHECK noise_anti_drift] 0 leaks on the 8-verb NOISE bank x 2 request-goal-openers "
          f"({len(NOISE) * 2} passages probed)")
    return {"noise_leaks": len(leaks)}


def check_self_test_green():
    res = G.self_test()
    print("[CHECK self_test_green] hdlab.goal_typing.self_test() passes unmodified "
          "(this build did not touch any decisive-case assertion)")
    return res


def run():
    r_targets = check_target_items()
    r_full44 = check_full_eval_and_zero_regression()
    r_real = check_real_text_set()
    r_fair = check_fair_instruments_unchanged()
    r_adv = check_adversarial_overfire()
    r_precision = check_precision_and_non_goal_banks()
    r_noise = check_noise_anti_drift()
    r_self = check_self_test_green()
    print("[ALL CHECKS PASS] REQUEST-RESPONSE outcome-typing tier: real_text %d->%d/10 (net +%d, "
          "both pre-reg targets recovered via the request-response tier with correct owner), "
          "full44 %d->%d/44 (pure no-op, zero regression), fair instruments 48/48+12/12 unchanged, "
          "adversarial over-fire 0/%d, precision+non-goal banks 0 fires, NOISE 0 leaks, self_test "
          "green. HARD-PASS." % (
              r_real["real_text_before"], r_real["real_text_after"],
              r_real["real_text_after"] - r_real["real_text_before"],
              r_full44["full44_before"], r_full44["full44_after"], r_adv["n_adversarial"]))
    return {"targets": r_targets, "full44": r_full44, "real_text": r_real, "fair": r_fair,
            "adversarial": r_adv, "precision": r_precision, "noise": r_noise, "self_test": r_self}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, default=str))
