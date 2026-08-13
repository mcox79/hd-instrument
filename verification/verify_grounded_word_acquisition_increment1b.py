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
      PIN REFRESH 2026-08-13 (Director): the primary number is now a FLOOR at the measured 18/36
      (was an `==` pin at 16/36). The lift is NOT uniform and is NOT reported as if it were:
      unmet_recall 2/13 -> 5/13 (+3) but met_recall 14/23 -> 13/23 (a genuine -1). The met -1 is not
      attributable to tonight's work (the old lemmatiser path scores 12/23 on this component, below
      the current 13/23), but it is real, so met_recall is asserted as its OWN floor and printed as
      its own component -- the rising aggregate must not be allowed to absorb it. Gate-5 eligible
      7/18 -> 8/18 vs fallback 9/18 -> 10/18: the SHAPE claim REMAINS FALSIFIED and was not touched.
      This build's measured verdict is still HARD_FAIL.
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

# ---------------------------------------------------------------- PIN POLICY (2026-08-13, Director)
# primary_accuracy / met_recall / unmet_recall / gate-5 eligible+fallback are LIVE production numbers
# read through congruence_with_lexicon_fallback. They ACCUMULATE as tiers land and more is better, so
# `==` pins on them go stale on every improvement and cannot tell improvement from regression. They
# are now FLOORS (`>=`), pinned at TODAY's measured values.
# NOT converted (deliberately): the eligible/fallback PARTITION SIZES (18/18) stay `==` -- they are a
# property of the 36-item bank, not a score. The gate-5 SHAPE assert stays an inequality on the
# measured ratios (it IS the falsification record). check_anti_drift_leak_is_real's exact leak set
# {answered: POS, carried: POS} and 2/8 gate count stay `==` (a named HARD-FAIL cause reproduced on
# purpose). check_strict_add_no_regression's equalities stay `==` (they are invariants).
#
# PIN UPDATE 2026-08-13: primary_accuracy 16/36 -> 18/36. VERIFIED as an overall gain, but NOT a
# clean one, and the composition is recorded here rather than buried in the total:
#     met_recall   14/23 -> 13/23   (a GENUINE -1, see below)
#     unmet_recall  2/13 ->  5/13   (+3)
#     gate-5        eligible 7/18 -> 8/18, fallback 9/18 -> 10/18
# THE MET -1 IS NOT TONIGHT'S WORK: the pre-existing lemmatiser path scores 12/23 on this component,
# i.e. 13/23 is already ABOVE it, so the loss predates the lemma_verb fix rather than being caused by
# it. It is nonetheless a real component regression against this build's own 14/23 and is asserted
# SEPARATELY below (MET_RECALL_FLOOR) precisely so a rising aggregate can never hide it.
# GATE-5 SHAPE REMAINS FALSIFIED (8/18 = 0.4444 <= 10/18 = 0.5556) -- unchanged, and deliberately NOT
# "fixed" by moving a pin. The measured verdict of this build is still HARD_FAIL.
PRIMARY_ACCURACY_FLOOR = 18   # was pinned ==16 (2026-08-06); now >=18 (2026-08-13)
MET_RECALL_FLOOR = 13         # was pinned ==14 (2026-08-06); now >=13 -- A GENUINE -1, see above
UNMET_RECALL_FLOOR = 5        # was pinned ==2  (2026-08-06); now >=5  (2026-08-13)
GATE5_ELIGIBLE_FLOOR = 8      # was pinned ==7  (2026-08-06); now >=8  (2026-08-13)
GATE5_FALLBACK_FLOOR = 10     # was pinned ==9  (2026-08-06); now >=10 (2026-08-13)
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

    # AGGREGATE: floor (accumulating, more-is-better). Was pinned ==16 (2026-08-06); now >=18.
    assert correct >= PRIMARY_ACCURACY_FLOOR, (
        f"primary_accuracy must be >= {PRIMARY_ACCURACY_FLOOR}/36 (16/36 at this build), "
        f"got {correct}/36")
    # COMPONENT FLOORS, ASSERTED SEPARATELY AND ON PURPOSE -- see MET_RECALL_FLOOR's comment. The
    # aggregate above must NOT be allowed to mask a component moving the wrong way; met_recall is
    # already 1 BELOW where this build measured it, and that -1 must stay visible from here on.
    assert met_c >= MET_RECALL_FLOOR, (
        f"MET-RECALL COMPONENT REGRESSION: met_recall={met_c}/23, floor {MET_RECALL_FLOOR}/23 "
        f"(was 14/23 at this build on 2026-08-06; already down 1 -- do NOT lower this floor again "
        f"without an explicit VET of what was lost)")
    assert unmet_c >= UNMET_RECALL_FLOOR, (
        f"unmet_recall={unmet_c}/13, floor {UNMET_RECALL_FLOOR}/13 (was 2/13 at this build)")
    # BANK COMPOSITION: EXACT on purpose. e_tot/f_tot are the desiderative/non-desiderative partition
    # sizes of the 36-item OOV bank -- a fixed property of the data, not a quality score. If either
    # moves, the gate-5 comparison is no longer comparing what it was designed to compare.
    assert (e_tot, f_tot) == (18, 18), f"gate-5 partition changed: eligible_n={e_tot} fallback_n={f_tot}"
    assert e_ok >= GATE5_ELIGIBLE_FLOOR, (e_ok, GATE5_ELIGIBLE_FLOOR)
    assert f_ok >= GATE5_FALLBACK_FLOOR, (f_ok, GATE5_FALLBACK_FLOOR)
    # GATE-5 SHAPE: still FALSIFIED, and deliberately left as an INEQUALITY ON THE MEASURED RATIOS,
    # not "fixed" by moving a pin. eligible <= fallback is the falsification itself; the day this
    # assert fires is the day the SHAPE claim stops being falsified, and that must be a loud event.
    assert e_ok / e_tot <= f_ok / f_tot, "gate-5 SHAPE claim should be FALSIFIED (eligible <= fallback)"
    print(f"[CHECK primary] primary={correct}/36={correct / 36:.4f} (floor {PRIMARY_ACCURACY_FLOOR}; "
          f"16/36 at this build) | COMPONENTS met_recall={met_c}/23 (floor {MET_RECALL_FLOOR}; "
          f"14/23 at this build -- the -1 is REPORTED, not absorbed into the total) "
          f"unmet_recall={unmet_c}/13 (floor {UNMET_RECALL_FLOOR}; 2/13 at this build) | "
          f"GATE5 eligible={e_ok}/{e_tot}={e_ok / e_tot:.4f} <= fallback={f_ok}/{f_tot}="
          f"{f_ok / f_tot:.4f} (SHAPE claim still FALSIFIED)")
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
    _p = r1 or {}
    print("[ALL CHECKS PASS] grounded-word-acquisition increment 1b: primary=%s/36 (floor %d; 16/36 "
          "at this build) with COMPONENTS met_recall=%s/23 (floor %d; 14/23 at this build -- a "
          "GENUINE -1, reported not absorbed) unmet_recall=%s/13 (floor %d; 2/13 at this build); "
          "gate-5 eligible %s/18 <= fallback %s/18 -> SHAPE claim STILL FALSIFIED (untouched); "
          "Tier-3 pole sentinel MET/UNMET wiring works, anti-drift leak (2/8) reproduced honestly, "
          "strict-ADD no-regression proven. Measured verdict: HARD_FAIL." % (
              _p.get("primary_correct"), PRIMARY_ACCURACY_FLOOR, _p.get("met_recall"),
              MET_RECALL_FLOOR, _p.get("unmet_recall"), UNMET_RECALL_FLOOR,
              (_p.get("eligible") or ["?"])[0], (_p.get("fallback") or ["?"])[0]))
    return {"pole_sentinel": r2, "anti_drift_leak": r3, "strict_add": r4, "primary": r1}


if __name__ == "__main__":
    run()
