"""Scaffold-free witness for the DID-IT-HAPPEN occurrence-gate + recurrence + window-widening build
AND its 2026-08-06 REFERENT-EXTRACTION REPAIR (GAP-B / GAP-C). tracing=False; hdlab organs + the
in-repo eval JSONL only (no experiment-cell scaffold, no corpora needed -- the eval carries each
passage's text directly).

Pre-reg: preregs/2026-08-06_did_it_happen_occurrence_gate_v1.md
Design:  notes/research_did_it_happen_occurrence_gate_congruence_wiring_2026-08-06.md

HISTORY. The occurrence-gate + recurrence channel + window-widening were built at 7058d026b (strict-ADD,
mechanism-correct on constructed inputs) but landed net-new-correct=0 on the real-prose eval because the
signals were STARVED by two upstream referent-extraction bugs (Director-reproduced): GAP-C (a pre-verbal
negator/do-support cluster poisons the ACTUAL referent -- "the boat did not sink" -> referent="not" ->
the correct occurrence-gate flip is discarded at referent_mismatch) and GAP-B (an OOV control-verb goal
yields desired referent=None -> the recurrence same-referent match dies at referent_extraction_failed).

MEASURED VERDICT AFTER THE REFERENT REPAIR (this witness reproduces it):
  - GAP-C FIXED: for a NEGATED outcome verb the pre-verbal negator/aux cluster is skipped before taking
    the subject NP head, so "the boat did not sink" -> referent="boat" and the occurrence-gate flip
    RESOLVES (save-goal + "did not sink" -> MET). Byte-identical referent extraction for NON-negated
    verbs (precision guard).
  - GAP-B FIXED: an OOV control-verb goal ("wanted to find love") now extracts the object NP theme
    ("love") instead of None, so the recurrence channel can link.
  - RECURRENCE THEME SYMMETRY: a recurrence emits BOTH a subject-referent and an object-referent sibling
    candidate (a recurred transitive action's theme is its object, an intransitive's is its subject; we
    cannot tell them apart without a parser), and congruence_decision Pass-1 links on whichever matches
    the goal's theme.
  - WINDOW-WIDENING WIRED into production (congruence_with_lexicon_fallback now uses
    congruence_outcome_valence_windowed; strict-widen: byte-identical when sents[-1] already has a
    candidate).
  MEASURED lift (disk, this witness): the 15-item did-it-happen subset moved 6/15 -> 7/15
    (net-new +1: onestop_limal_dating, recovered via window-widening + GAP-B object theme + recurrence
    object candidate); the full 36-OOV eval moved 6/36 -> 8/36 (net-new +2: onestop_limal_dating PLUS
    lw_aunt_march_opposition, a recurrence 'marry' that referent-mismatches -> UNMET, matching gold).
    ZERO regressions across the FULL 44-item eval (exactly 2 verdicts move, both NONE->correct);
    cert 220/3 green, fair_v1 48/48, real_text owner 6/10, goal_typing.self_test byte-identical,
    NOISE 0 leaks, numeric-threshold traps not false-MET.

PIN REFRESH 2026-08-13 (Director). `prod_sub` is a LIVE ACCUMULATING production number and was pinned
with `==`, so it was guaranteed to go stale on every real improvement -- it did. Measured today:
prod_sub 7 -> 10, net_new +1 -> +4, GAP-1 recovered 1/5 -> 2/5, full-44 gains 2 -> 9. VERIFIED as
gains-with-zero-regressions: 9 gains, 0 regressions across the full 44, and the FROZEN
_baseline_nonwindowed reference still reproduces EXACTLY 6 on both the 15-subset and the OOV-36, so
every bit of the movement is on the production side. Cause = tiers that landed after this witness
(referent-recurrence, grounded result-class, request-response, Levin last-resort backoff), NOT a
re-scoring of this build. All production-side numbers are now FLOORS (>=); all baseline-side numbers
and all invariants (NOISE==0, no-regression, this build's own attributed recovery) stay exact. See
PIN POLICY below.

HONEST BAND READ (do not overclaim): net-new +1 on the 15-subset is ABOVE the luck baseline and ABOVE
the pre-reg Check-1 HARD-FAIL bar (net==0) but BELOW its +2 HARD-PASS bar -> a PARTIAL/MIDDLE result, not
a HARD-PASS. Check-4 recovered only 1 of the 5 GAP-1 items (onestop_limal_dating). The other 4 have
blockers DEEPER than window-widening + referent extraction, named per-item in check4 below (no-desiderative
-goal, OOV-verb-with-no-object-referent, ECM-copula-referent, distractor-clause) -- these are the natural
next FORMALIZE targets, reported not forced.

Run: .venv/Scripts/python.exe verification/witness_did_it_happen_occurrence_gate_v1.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.goal_typing as G

EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"

SUBSET15 = [
    "lw_meg_currant_jelly", "lw_laurie_flower_table_amy",
    "agg_gilbert_pond_rescue_friendship_plea_ch28", "agg_anne_pudding_sauce_mouse_ch16",
    "agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17", "woz_dorothy_kansas_wish",
    "woz_scarecrow_brains", "woz_tin_woodman_heart", "woz_lion_courage_denied",
    "alice_beautiful_garden", "race_german_dog", "race_davey_wiffle", "onestop_malala",
    "onestop_hunt_crowdfunding", "onestop_limal_dating",
]
GAP1_ITEMS = ["lw_laurie_flower_table_amy", "agg_anne_mrs_barry_forgiveness_currant_wine_ch16_17",
              "woz_dorothy_kansas_wish", "race_davey_wiffle", "onestop_limal_dating"]

# ---------------------------------------------------------------- PIN POLICY (2026-08-13, Director)
# THIS witness was the clearest instance of the design flaw: `prod_sub` is a LIVE ACCUMULATING
# production number (congruence_with_lexicon_fallback scored on the 15-subset), and it was pinned
# with `==`. That is guaranteed to go stale on every genuine improvement to the substrate, and an
# equality assert cannot distinguish an improvement from a regression -- it just fails either way.
# CONVERTED TO FLOORS (`>=`): prod_sub, net_new (prod_sub - base_sub), the GAP-1 recovered count,
# and the check-4 gain set (now a required-SUBSET).
# LEFT AS `==` ON PURPOSE: everything on the BASELINE side. `_baseline_nonwindowed` is the FROZEN
# pre-fix reference (full-36 == 6, 15-subset == 6, congruence-native-correct == 0, base_sub == 6);
# if a baseline number moves, the measured delta is no longer the delta that was recorded and this
# witness SHOULD fail loudly instead of silently re-baselining. Also left exact: the NOISE leak count
# (== 0), the light-verb recurrence block, the numeric-threshold no-false-MET traps, the strict-ADD
# checks, and `assert not regressions` -- those are invariants, not accumulating quality scores.
#
# PIN UPDATE 2026-08-13: prod_sub 7 -> 10 (net_new +1 -> +4); check-4 GAP-1 recovered 1 -> 2
# (woz_dorothy_kansas_wish now also recovers); check-4 full-44 gain set 2 -> 9 members.
# VERIFIED gains-with-zero-regressions: 9 gains, 0 regressions across the full 44, and the frozen
# baseline still reproduces EXACTLY 6 on both the 15-subset and the OOV-36 (so the movement is on the
# production side only). Cause is later-landed tiers this witness predates -- referent-recurrence
# (2026-08-07), grounded result-class (2026-08-07), request-response (2026-08-07), Levin last-resort
# backoff (276674abb). Drift, not regression; this build's own +1 claim is unchanged and still
# attributed to onestop_limal_dating via same_class_same_referent (asserted exactly, below).
EXPECTED_PROD_SUB15_FLOOR = 10   # was pinned ==7 (2026-08-06); now >=10 (2026-08-13)
EXPECTED_NET_NEW_FLOOR = 4       # was pinned ==1 (2026-08-06); now >=4 (2026-08-13)
EXPECTED_GAP1_RECOVERED_FLOOR = 2  # was pinned == ["onestop_limal_dating"] exactly; now >=2 members
BASELINE_SUB15 = 6               # FROZEN baseline, exact -- deliberately NOT a floor
BASELINE_OOV36 = 6               # FROZEN baseline, exact -- deliberately NOT a floor
NOISE = [("walked", "He walked to the well and carried the pail home"),
         ("sat", "She sat by the fire in the evening"),
         ("spoke", "She turned and spoke to her brother"),
         ("turned", "He turned and looked toward the door"),
         ("answered", "The boy answered the question at once"),
         ("asked", "He asked for a cup of cold water"),
         ("stood", "The horse stood by the wooden gate"),
         ("carried", "She carried the basket to the market")]


def _load():
    rows = [json.loads(l) for l in open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8")
            if l.strip()]
    return rows, {r["id"]: r for r in rows}


def _gold(r):
    return "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"


def _baseline_nonwindowed(txt):
    """FROZEN pre-fix baseline: the NON-windowed congruence_outcome_valence primary + V2 lexicon
    fallback (the behavior before window-widening was wired into congruence_with_lexicon_fallback).
    The GAP-B/GAP-C referent fixes only bite via a recurrence in a BACKWARD clause, which this
    non-windowed path never reaches, so this reproduces the exact historical 6/15 + 6/36 baseline."""
    v, det = G.congruence_outcome_valence(txt)
    if v != "NA":
        return v, det
    sents = G._sentences(txt)
    return (G.lexicon_predict(sents[-1]) if sents else "NONE"), {"reason": "abstain_fallback_to_lexicon"}


def check_step0_baseline():
    """Step 0: FROZEN baseline via the non-windowed path -- full-36 + 15-subset + congruence-native."""
    rows, d = _load()
    oov = [r for r in rows if r.get("outcome_in_lexicon") is False]
    assert len(oov) == 36, f"expected 36 OOV, got {len(oov)}"
    full = sum(_baseline_nonwindowed(r["text"])[0] == _gold(r) for r in oov)
    sub = sum(_baseline_nonwindowed(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)
    native_correct = 0
    for i in SUBSET15:
        pred, det = _baseline_nonwindowed(d[i]["text"])
        if pred == _gold(d[i]) and det.get("reason") != "abstain_fallback_to_lexicon":
            native_correct += 1
    # ALL EXACT (`==`) ON PURPOSE -- frozen baseline, not an accumulating production score. See PIN
    # POLICY: a moving baseline invalidates every recorded delta and must fail loudly.
    assert full == BASELINE_OOV36, f"Step-0 full-36 must be 6 (empty-overlay floor), got {full}"
    assert sub == BASELINE_SUB15, f"Step-0 15-subset must be 6, got {sub}"
    assert native_correct == 0, f"Step-0 congruence-native-correct on subset must be 0, got {native_correct}"
    print("[CHECK step0] FROZEN baseline (non-windowed): full-36=6/36=0.1667 | 15-subset=6/15=0.40 | "
          "congruence-native-correct=0 (all 6 are lexicon-fallback luck)")
    return {"full36": full, "sub15": sub, "native_correct": native_correct}


def check_mechanism_fires():
    """The occurrence-gate, recurrence channel (subject + object theme), and window-widening FIRE and
    now RESOLVE correctly on constructed inputs (was the DEFEAT documented at 7058d026b) -- proves the
    GAP-B/GAP-C referent repair, not just that the gate executes."""
    goal = ["The coach wanted Davey to pitch in the final"]
    # subject-recurrence positive (intransitive theme == subject) still MET
    v, det = G.congruence_decision(goal, "Davey pitched all afternoon")
    assert v == "MET" and det["actual"]["referent"] == "davey" \
        and G.RECURRENCE_SENTINEL in det["actual"]["classes"], (v, det)
    # GAP-C: a NEGATED recurrence is no longer referent-poisoned -- referent="davey" (was "not"),
    # occurrence-gate flips same->opposed, verdict UNMET (Davey did NOT pitch -> goal unmet).
    v2, det2 = G.congruence_decision(goal, "Davey did not pitch at all")
    assert det2.get("occurrence_gate_fired") is True and det2["actual"]["referent"] == "davey" \
        and v2 == "UNMET", (v2, det2)
    # object-recurrence positive (transitive theme == object): GAP-B object referent on the goal side
    # links to the recurrence object candidate on the actual side.
    v3, det3 = G.congruence_decision(["Nora wanted to paint a fence in the yard"], "Nora painted a fence")
    assert v3 == "MET" and det3["desired"]["referent"] == "fence" \
        and det3["actual"]["referent"] == "fence", (v3, det3)
    # window-widening steps back past a trailing reaction sentence to the true clause
    p = ("The coach wanted Davey to pitch in the final. Davey pitched all afternoon. "
         "Everyone cheered loudly.")
    assert G.congruence_outcome_valence_windowed(p)[0] == "MET" and \
        G.congruence_outcome_valence(p)[0] == "NA"
    # GAP-C headline repro: save-goal + "The boat did not sink" now RESOLVES to MET (was the poisoned
    # referent_mismatch(UNMET) defeat at 7058d026b) -- occurrence-gate flip reaches a literal referent.
    vp, detp = G.congruence_decision(["Owen wanted to save the boat before the storm hit"],
                                     "The boat did not sink")
    assert detp.get("occurrence_gate_fired") is True and vp == "MET" \
        and detp["reason"] == "same_class_same_referent" \
        and detp["actual"]["referent"] == "boat", (vp, detp)
    print("[CHECK mechanism_fires] GAP-C FIXED: 'the boat did not sink' -> referent='boat', gate flips "
          "-> MET (was referent_mismatch/UNMET defeat). subject-recur->MET(davey); negated-recur "
          "un-poisoned->UNMET(davey); GAP-B object-recur paint/fence->MET; window steps back to true clause")
    return {"gapc_repro": vp, "gate_fired": detp.get("occurrence_gate_fired")}


def check1_occurrence_gate_and_recurrence():
    """Check 1 (production, now WINDOWED primary): net-new-correct on the 15-subset relative to the
    frozen non-windowed baseline + NOISE anti-drift + light-verb recurrence block + numeric-threshold
    no-false-MET."""
    _rows, d = _load()
    base_sub = sum(_baseline_nonwindowed(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)
    prod_sub = sum(G.congruence_with_lexicon_fallback(d[i]["text"])[0] == _gold(d[i]) for i in SUBSET15)
    net_new = prod_sub - base_sub
    # which items newly earned a congruence-native verdict
    newly = []
    for i in SUBSET15:
        pred, det = G.congruence_with_lexicon_fallback(d[i]["text"])
        if pred == _gold(d[i]) and det.get("reason") != "abstain_fallback_to_lexicon":
            newly.append((i, det.get("reason")))
    # NOISE anti-drift: 0 spurious congruence-native MET/UNMET
    leaks = 0
    for v, sent in NOISE:
        for goalp in ["Kim wanted to open the greenhouse before winter came",
                      f"Kim wanted to {v} to the market before noon"]:
            verd, det = G.congruence_decision([goalp], sent)
            if det.get("reason") in ("same_class_same_referent", "opposed_class_same_referent",
                                     "referent_mismatch") and verd in ("MET", "UNMET"):
                leaks += 1
    # light/copula recurrence blocked
    for lv, past in [("be", "was"), ("do", "did"), ("have", "had"), ("say", "said"), ("get", "got")]:
        assert not any(G.RECURRENCE_SENTINEL in c["classes"]
                       for c in G.find_actual_state_candidates(f"He {past} the thing", lv))
    # numeric-threshold: must NOT be flipped to a false MET
    for i in ["race_chen_situps", "onestop_carle_madeinfrance"]:
        assert G.congruence_with_lexicon_fallback(d[i]["text"])[0] != "MET", i
    # base_sub EXACT (frozen baseline); prod_sub / net_new FLOORS (live accumulating). See PIN POLICY.
    assert base_sub == BASELINE_SUB15, f"FROZEN baseline moved: base_sub={base_sub} (must be 6)"
    assert prod_sub >= EXPECTED_PROD_SUB15_FLOOR, (
        f"LIVE prod 15-subset = {prod_sub}, floor {EXPECTED_PROD_SUB15_FLOOR} (7 at this build)")
    assert net_new >= EXPECTED_NET_NEW_FLOOR, (
        f"Check-1 net-new-correct on 15-subset = {net_new}, floor +{EXPECTED_NET_NEW_FLOOR} "
        f"(+1 at this build)")
    assert leaks == 0, f"NOISE anti-drift leaks = {leaks} (HARD-FAIL if > 0)"   # EXACT invariant
    # EXACT: this build's OWN attributed recovery must still be present and still earned by the same
    # mechanism -- a floor here would let the one item this build actually earned silently drop out.
    assert ("onestop_limal_dating", "same_class_same_referent") in newly, newly
    print(f"[CHECK check1] LIVE net-new-correct = +{net_new}/15 ({base_sub}->{prod_sub}, floor "
          f"+{EXPECTED_NET_NEW_FLOOR}); THIS BUILD's own claim unchanged: +1 (6->7; "
          f"onestop_limal_dating, same_class_same_referent), ABOVE luck baseline + HARD-FAIL(0) bar, "
          f"BELOW its +2 HARD-PASS bar (PARTIAL); newly_earned={newly}; NOISE leaks=0; light-verb "
          f"recurrence blocked; numeric-threshold no false MET")
    return {"net_new": net_new, "noise_leaks": leaks, "newly_earned": newly}


def check4_window_widening():
    """Check 4 (windowed production): GAP-1 items recovered + FULL-44 non-regression (every moved
    verdict is a gain)."""
    rows, d = _load()
    recovered = [i for i in GAP1_ITEMS
                 if G.congruence_with_lexicon_fallback(d[i]["text"])[0] == _gold(d[i])]
    # FULL-44 non-regression: compare windowed production against the frozen non-windowed baseline.
    gains, regressions = [], []
    for r in rows:
        base = _baseline_nonwindowed(r["text"])[0]
        prod = G.congruence_with_lexicon_fallback(r["text"])[0]
        if prod == base:
            continue
        bc, pc = base == _gold(r), prod == _gold(r)
        if pc and not bc:
            gains.append(r["id"])
        elif bc and not pc:
            regressions.append((r["id"], base, prod))
    # FLOOR + required-member (was `recovered == ["onestop_limal_dating"]`): GAP-1 recovery is an
    # accumulating count -- more of the 5 recovering is strictly better. This build's own recovered
    # item stays a REQUIRED member (exact), so its loss is still a hard failure.
    assert "onestop_limal_dating" in recovered, f"GAP-1: this build's own recovery lost: {recovered}"
    assert len(recovered) >= EXPECTED_GAP1_RECOVERED_FLOOR, (
        f"GAP-1 recovered = {sorted(recovered)} ({len(recovered)}/5), floor "
        f"{EXPECTED_GAP1_RECOVERED_FLOOR} (1/5 at this build)")
    # EXACT, deliberately NOT loosened: zero regressions is the invariant this check exists for.
    assert not regressions, f"FULL-44 REGRESSIONS: {regressions}"
    # Required-SUBSET (was `==`): the gain set accumulates as later tiers land; this build's own 2
    # must never drop out. The "nothing gets worse" side is guarded exactly, one line above.
    assert {"lw_aunt_march_opposition", "onestop_limal_dating"} <= set(gains), sorted(gains)
    print(f"[CHECK check4] LIVE GAP-1 recovered={len(recovered)}/5 ({sorted(recovered)}; floor "
          f"{EXPECTED_GAP1_RECOVERED_FLOOR}/5); THIS BUILD's own claim unchanged: 1/5 "
          f"(onestop_limal_dating, via window-widening + GAP-B object theme + recurrence object "
          f"candidate). FULL-44: {len(gains)} verdicts move, ALL gains ({sorted(gains)}), ZERO "
          f"regressions. Per-item GAP-1 blockers AS DIAGNOSED AT THIS BUILD (out of GAP-B/GAP-C "
          f"scope): lw_laurie=no_desiderative_goal_found; agg_anne_mrs_barry=OOV verb 'intercede' "
          f"with no object referent; woz_dorothy=ECM copula referent 'is'; race_davey=distractor "
          f"clause 'balls failed', goal 'play' never recurs. NOTE 2026-08-13: woz_dorothy's ECM-copula "
          f"blocker was CLOSED by the later A3 referent-extraction repair (see "
          f"verify_referent_recurrence_did_it_happen.py) -- it now recovers, which is why the GAP-1 "
          f"count is a floor rather than a fixed list.")
    return {"recovered": recovered, "gains": gains, "regressions": regressions}


def check_strict_add():
    """goal_typing.self_test passes (all decisive cases byte-identical) AND legacy find_actual_state_
    candidates (no desired_verb_lemma) never produces a RECURRENCE_SENTINEL (GAP-C referent skip is
    negated-only, so non-negated legacy extraction is byte-identical)."""
    G.self_test()
    assert not any(G.RECURRENCE_SENTINEL in c["classes"]
                   for c in G.find_actual_state_candidates("Davey pitched all afternoon"))
    # GAP-C is NEGATED-only: a non-negated candidate's referent is byte-identical to toks[:idx].
    cands = G.find_actual_state_candidates("The boat sank in the storm")
    assert cands and cands[0]["referent"] == "boat" and cands[0]["negated"] is False
    print("[CHECK strict_add] goal_typing.self_test passes; legacy candidate scan has no recurrence; "
          "non-negated referent extraction byte-identical")
    return True


def run():
    r0 = check_step0_baseline()
    rm = check_mechanism_fires()
    r1 = check1_occurrence_gate_and_recurrence()
    r4 = check4_window_widening()
    rs = check_strict_add()
    print("[ALL CHECKS PASS] did-it-happen occurrence-gate REFERENT REPAIR (GAP-B/GAP-C). THIS "
          "BUILD's measured claim unchanged: 15-subset 6->7 (net-new +1), full-36 6->8 (net-new +2), "
          "GAP-C repro flips to MET, onestop_limal_dating recovered via window-widening; PARTIAL vs "
          "the +2/3-of-5 HARD-PASS bars -- honest. LIVE TODAY (floors; includes later-landed tiers, "
          f"not this build's credit): 15-subset {r1['net_new'] + 6} (net-new +{r1['net_new']}), "
          f"GAP-1 recovered {len(r4['recovered'])}/5, full-44 gains {len(r4['gains'])}. FROZEN "
          "baseline still exactly 6/6. ZERO regressions (cert per run_certification.py, fair 48/48, "
          "self_test byte-identical, NOISE 0 leaks, numeric-threshold not false-MET).")
    return {"step0": r0, "mechanism": rm, "check1": r1, "check4": r4, "strict_add": rs}


if __name__ == "__main__":
    run()
