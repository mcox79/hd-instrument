"""Scaffold-free witness for the online grounded-word-acquisition loop, increment 1b (2026-08-06).

Reproduces (tracing=False, no experiment-cell scaffold -- hdlab organs + an inline compact corpus
loader only), for preregs/2026-08-06_grounded_word_acquisition_increment1b_v1.md:

  (1) PRIMARY NUMBER: on the 36 OOV-outcome items of goal_bearing_modern_eval_v1.jsonl, the
      single-channel structural acquisition (structural_vote -> MIN_CONFIRM=2 consolidate -> Tier-3
      write-back), scored through the LIVE production congruence_with_lexicon_fallback with the Risk-#1
      pole-sentinel fix live, yields primary_accuracy = 16/36 = 0.4444 (met_recall 14/23, unmet_recall
      2/13) and the SHAPE-fix's key gate-5 claim is FALSIFIED: eligible subset 7/18 < fallback 9/18.
  (2) TIER-3 POLE SENTINEL (Risk #1 fix) end-to-end: an acquired POS word gets a one-element pole
      sentinel from _verb_classes and types MET (same pole) / UNMET (opposed pole) through the
      congruence organ -- the wiring gap increment 1 could never exercise is closed.
  (3) ANTI-DRIFT LEAK is REAL and reported, not hidden: two valence-neutral transitive activity verbs
      {answered, carried} consolidate POS under the single channel (noise_consolidated_count = 2/8),
      one of the measured HARD-FAIL causes -- the dropped two-channel AND-gate had masked this.
  (4) STRICT-ADD no-regression: with an EMPTY Tier-3 overlay every existing goal_typing decisive case
      classifies byte-identically (goal_typing.self_test passes); the new POS_POLE/sentinel/pole-branch
      never fires for a non-acquired verb; a Tier-3 write for an OOV word changes no base verdict;
      clearing restores.

Run: .venv/Scripts/python.exe verification/verify_grounded_word_acquisition_increment1b.py
"""
import glob
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.word_acquisition_loop as L
import hdlab.verb_lexical_similarity as vls
import hdlab.goal_typing as G
from hdlab.goal_typing import congruence_with_lexicon_fallback, congruence_decision, _verb_classes

DESIDERATIVE_LEMMAS = {"want", "hope", "wish", "mean", "plan", "intend", "aim", "long", "yearn",
                       "desire"}
NOVEL_RELS = [
    "little_women/cleaned/little_women.clean.txt",
    "anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt",
    "tom_sawyer/cleaned/tom_sawyer.clean.txt",
    "wizard_of_oz/cleaned/wizard_of_oz.clean.txt",
    "alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt",
]
RACE_RELS = ["race/middle_test.jsonl", "race/high_test.jsonl"]
ONESTOP_LEVELS = ["Ele", "Int", "Adv"]
EVAL_REL = "experiments/data/goal_bearing_modern_eval_v1.jsonl"
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


def _split_sents(text):
    parts = re.split(r'[.!?]+["\'’”)]?', text)
    return [s.strip() for s in parts if len(s.strip()) > 3]


def _load_corpus():
    sents = []
    for rel in NOVEL_RELS:
        with open(os.path.join(REPO_ROOT, "data", "corpora", rel), encoding="utf-8",
                  errors="ignore") as f:
            sents += _split_sents(f.read())
    for rel in RACE_RELS:
        seen = set()
        with open(os.path.join(REPO_ROOT, "data", "corpora", rel), encoding="utf-8",
                  errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                art = json.loads(line).get("article", "")
                if not art or art in seen:
                    continue
                seen.add(art)
                sents += _split_sents(art)
    for lvl in ONESTOP_LEVELS:
        pat = os.path.join(REPO_ROOT, "data", "corpora", "onestop",
                           "Texts-SeparatedByReadingLevel", f"{lvl}-Txt", "*.txt")
        for fp in sorted(glob.glob(pat)):
            with open(fp, encoding="utf-8", errors="ignore") as f:
                sents += _split_sents(f.read())
    return sents


def _load_eval():
    rows = []
    with open(os.path.join(REPO_ROOT, EVAL_REL), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows, [r for r in rows if r.get("outcome_in_lexicon") is False]


def _norm(s):
    return " ".join(re.findall(r"[a-z']+", s.lower()))


def check_primary_reproduction():
    """Reproduce the headline HARD_FAIL number from hdlab organs (no cell import). Skips only if the
    corpora are absent (they are present in-repo)."""
    if not os.path.exists(os.path.join(REPO_ROOT, "data", "corpora", NOVEL_RELS[0])):
        print("[SKIP primary_reproduction] corpora not present")
        return None
    corpus = _load_corpus()
    all_rows, oov = _load_eval()
    assert len(oov) == 36, f"expected 36 OOV items, got {len(oov)}"
    blob = " || ".join(_norm(r["text"]) for r in all_rows)

    def exclude(sent):
        n = _norm(sent)
        return len(n) > 0 and n in blob

    target = sorted({r["outcome_verb_lemma"] for r in oov})
    mined = L.mine_target_lemma_sentences(target, corpus, exclude=exclude, max_occ=6)

    vls.clear_acquired_outcome()
    acquired, _ = L.run_acquisition_1b(mined, enrich=False)
    for lemma, info in acquired.items():
        vls.register_acquired_outcome(lemma, info["polarity"])
    correct = met_c = unmet_c = e_ok = e_tot = f_ok = f_tot = 0
    for r in oov:
        gold = "MET" if r["gold_outcome_polarity"] == "met" else "UNMET"
        pred, _d = congruence_with_lexicon_fallback(r["text"])
        ok = (pred == gold)
        correct += ok
        if gold == "MET":
            met_c += ok
        else:
            unmet_c += ok
        if r["goal_verb_lemma"] in DESIDERATIVE_LEMMAS:
            e_tot += 1
            e_ok += ok
        else:
            f_tot += 1
            f_ok += ok
    vls.clear_acquired_outcome()

    assert correct == 16, f"primary_accuracy must reproduce 16/36, got {correct}/36"
    assert met_c == 14 and unmet_c == 2, f"recall mismatch: met={met_c}/23 unmet={unmet_c}/13"
    assert (e_ok, e_tot) == (7, 18) and (f_ok, f_tot) == (9, 18), (
        f"gate-5 subset mismatch: eligible={e_ok}/{e_tot} fallback={f_ok}/{f_tot}")
    assert e_ok / e_tot <= f_ok / f_tot, "gate-5 SHAPE claim should be FALSIFIED (eligible <= fallback)"
    print(f"[CHECK primary] reproduced primary=16/36=0.4444 met_recall=14/23 unmet_recall=2/13 | "
          f"GATE5 eligible=7/18=0.3889 <= fallback=9/18=0.5000 (SHAPE claim FALSIFIED)")
    return {"primary_correct": correct, "met_recall": met_c, "unmet_recall": unmet_c,
            "eligible": [e_ok, e_tot], "fallback": [f_ok, f_tot]}


def check_pole_sentinel_mechanism():
    """Risk #1 fix end-to-end: an acquired POS word survives as a scoring candidate (pole sentinel) and
    types MET (same pole) / UNMET (opposed pole) through congruence_decision."""
    vls.clear_acquired_outcome()
    assert _verb_classes("give") == set(), "empty overlay: OOV verb must have no class"
    vls.register_acquired_outcome("give", "POS")
    assert _verb_classes("give") == {"ACQUIRED_REALIZED"}, "acquired POS must yield the realized sentinel"
    d_met, det_met = congruence_decision(["Owen wanted to win the prize before noon"], "Owen gave a shout")
    assert d_met == "MET" and det_met["reason"] == "same_class_same_referent", (
        f"acquired POS + POS-pole goal + linked referent must be MET, got {d_met} ({det_met})")
    vls.register_acquired_outcome("slump", "NEG")
    d_unmet, det_unmet = congruence_decision(["Owen wanted to win the prize before noon"], "Owen slumped")
    assert d_unmet == "UNMET" and det_unmet["reason"] == "opposed_class_same_referent", (
        f"acquired NEG + POS-pole goal must be UNMET, got {d_unmet} ({det_unmet})")
    vls.clear_acquired_outcome()
    assert _verb_classes("give") == set(), "clear must restore no-class"
    print("[CHECK pole_sentinel] acquired POS->MET, acquired NEG->UNMET via Tier-3 pole comparison; "
          "clear restores (Risk #1 wiring gap closed)")
    return {"acquired_pos_met": d_met, "acquired_neg_unmet": d_unmet}


def check_anti_drift_leak_is_real():
    """The measured HARD-FAIL anti-drift cause, reproduced not hidden: two valence-neutral transitive
    activity verbs consolidate POS under the single structural channel (the dropped AND-gate had
    masked this)."""
    vls.clear_acquired_outcome()
    target = {w: sents for w, sents in NOISE}
    gated = sum(1 for w, sents in NOISE if all(L.structural_vote([], s, w) is None for s in sents))
    acquired, _ = L.run_acquisition_1b(target)
    got = {k: v["polarity"] for k, v in acquired.items()}
    vls.clear_acquired_outcome()
    assert got == {"answered": "POS", "carried": "POS"}, f"expected the measured leak, got {got}"
    assert gated == 2, f"noise_gated should be 2/8 (only sat, spoke), got {gated}/8"
    print(f"[CHECK anti_drift_leak] the real HARD-FAIL cause reproduces: neutral transitives leak POS "
          f"-> noise_consolidated={got} (2/8); noise_gated={gated}/8")
    return {"noise_consolidated": got, "noise_gated": gated}


def check_strict_add_no_regression():
    """Empty overlay => goal_typing's decisive cases classify byte-identically; the Tier-3 sentinel /
    pole branch never fires for a non-acquired verb; a Tier-3 write for an OOV word changes no base
    congruence verdict; clearing restores."""
    vls.clear_acquired_outcome()
    assert vls.ACQUIRED_OUTCOME_VERB_FEATURES == {}, "overlay must start empty"
    # (a) all existing goal_typing decisive cases still pass (strict-ADD, no behavior change)
    G.self_test()
    # (b) a base congruence verdict does not change when an UNRELATED OOV word is acquired
    base_verdict, _ = congruence_decision(["Owen wanted to save the boat before the storm hit"],
                                          "The boat sank")
    assert base_verdict == "UNMET", f"base decisive case must be UNMET, got {base_verdict}"
    vls.register_acquired_outcome("gerfle", "POS")   # OOV nonsense word, unrelated to the passage
    after_verdict, _ = congruence_decision(["Owen wanted to save the boat before the storm hit"],
                                           "The boat sank")
    assert after_verdict == base_verdict, (
        f"STRICT-ADD VIOLATION: a Tier-3 write changed a base verdict {base_verdict} -> {after_verdict}")
    # (c) a non-acquired OOV verb never gets a sentinel (pole branch is acquired-only)
    assert _verb_classes("gerfle") == {"ACQUIRED_REALIZED"}, "acquired sentinel expected for gerfle"
    assert _verb_classes("blorptwig") == set(), "a non-acquired OOV verb must have no class/sentinel"
    vls.clear_acquired_outcome()
    restored, _ = congruence_decision(["Owen wanted to save the boat before the storm hit"],
                                      "The boat sank")
    assert restored == base_verdict, "clear must restore base behavior"
    print("[CHECK strict_add] goal_typing.self_test passes; base verdicts unchanged by Tier-3 writes; "
          "pole branch acquired-only; clear restores (no-regression proven)")
    return {"base_verdict": base_verdict}


def run():
    r2 = check_pole_sentinel_mechanism()
    r3 = check_anti_drift_leak_is_real()
    r4 = check_strict_add_no_regression()
    r1 = check_primary_reproduction()
    print("[ALL CHECKS PASS] grounded-word-acquisition increment 1b: primary reproduced "
          "(16/36=0.4444, eligible 7/18 <= fallback 9/18 -> SHAPE claim FALSIFIED), Tier-3 pole "
          "sentinel MET/UNMET wiring works, anti-drift leak (2/8) reproduced honestly, strict-ADD "
          "no-regression proven. Measured verdict: HARD_FAIL.")
    return {"pole_sentinel": r2, "anti_drift_leak": r3, "strict_add": r4, "primary": r1}


if __name__ == "__main__":
    run()
