"""Scaffold-free witness for the online grounded-word-acquisition loop, increment 1 (2026-08-06).

Reproduces (tracing=False, no experiment-cell scaffold, hdlab organs only):
  (1) the held-out result -- fall-through baseline 0/7, and the COMBINED-arm acquisition writes back
      exactly {earn:POS, gain:POS}, so held-out accuracy = 2/7 via the PRODUCTION lexicon_predict;
  (2) the earned-theta sign relation VALENCE(RECIPROCITY) < 0 < VALENCE(BLOCK_HIGH), read from the
      frozen reward-trained appraisal theta through score_item's situation_type path (a random theta
      gives ~0 -- so this is genuinely earned, not supplied);
  (3) the anti-drift leak is REAL and reported, not hidden -- the two valence-neutral transitive noise
      verbs {answer, carry} consolidate POS (noise_consolidated_count = 2 on this pair), the measured
      HARD-FAIL cause;
  (4) the STRICT-ADD no-regression property -- with an empty Tier-3 overlay every base Tier-2 word
      classifies byte-identically; a Tier-3 write for an OOV word never changes any base word's
      classification (base lexicon always wins in _features_for); clearing restores the fall-through.

Run: .venv/Scripts/python.exe verification/verify_grounded_word_acquisition_increment1.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.word_acquisition_loop as L
import hdlab.verb_lexical_similarity as vls
from hdlab.goal_typing import lexicon_predict
from hdlab.thematic_role_labeler import lemma_verb

_CORPUS_REL = [
    "data/corpora/mcguffey_graded/g1_first.txt", "data/corpora/mcguffey_graded/g2_second.txt",
    "data/corpora/mcguffey_graded/g3_third.txt", "data/corpora/mcguffey_graded/g4_fourth.txt",
    "data/corpora/mcguffey_graded/g5_fifth.txt", "data/corpora/mcguffey_graded/g6_sixth.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_first_reader.clean.txt",
    "data/corpora/graded_readers_grade1/cleaned/mcguffey_primer.clean.txt",
]
CORPORA = [os.path.join(REPO_ROOT, p) for p in _CORPUS_REL]

HELDOUT = [
    ("caught", "POS",
     ["Four soft paws had little kitty, and they caught the little mousie, Long time ago.",
      "Papa and Mamma caught at him to save him, and before we knew it we were all in the water."],
     "The rat stole out, and she jumped at it and caught it."),
    ("obtained", "POS",
     ["Harry, at length, obtained permission for the little dog to remain as a sort of outdoor pensioner.",
      "Reverse the process, and repeat as before until the lowest pitch is obtained."],
     "Having on several days obtained sight of some of them, he gave chase; but they baffled all pursuit."),
    ("gained", "POS",
     ["A distinct articulation can only be gained by constant and careful practice of the elementary sounds.",
      "His writings in poetry and prose are well known, and he also gained distinction in his profession as a sculptor."],
     "suggestions and criticisms gained from their daily work in the schoolroom."),
    ("earned", "POS",
     ["He earned almost enough to support his mother and his little sister.",
      "In a few years, while still a small boy, he earned money enough to support his father."],
     "You have earned the orange, my boy; and she gave it to him with a smile."),
    ("deserted", "NEG",
     ["But sleep seemed to have deserted the pillow of poor Tom.",
      "Frank started up in great consternation, and, from that time, almost entirely deserted the library."],
     "They both consequently deserted the little family circle every evening after tea."),
    ("wasted", "NEG",
     ["His wasted form, his aching head, And all that now remains of him, Lies, shuddering, on a felon's bed.",
      "But his bodily energies wasted and declined under incessant toil."],
     "With fire and sword, the country round Was wasted, far and wide."),
    ("faded", "NEG",
     ["I can see her as she stood there in front of the store, in her old hood and faded dress.",
      "looking up at a faded picture of an old gentleman."],
     "The fair, meek blossom that grew up And faded by my side."),
]
NOISE_LEAK = [
    ("answered", ["The boy answered the question at once.", "She answered her mother very softly."]),
    ("carried", ["She carried the basket to the market.", "They carried the boxes up the stairs."]),
]

# base Tier-2 words used for the strict-ADD no-regression checks (a POS and a NEG seed + held-out tags)
_BASE_POS_SEEDS = ("reach", "win", "escape", "arrive", "enjoy")
_BASE_NEG_SEEDS = ("fall", "sink", "lose", "fail", "miss", "wail")
_BASE_PROBE = ["praise", "punish", "reach", "fall", "recover", "perish"]  # all Tier-1/Tier-2 members


def _occ(dataset):
    out = []
    for word, _g, acq, _ho in dataset:
        for s in acq:
            out.append({"word": word, "goal_sentences": [], "sentence": s})
    return out


def _classify(word):
    return vls.classify_2way(word, _BASE_POS_SEEDS, _BASE_NEG_SEEDS, "outcome", 0.35, 0.15)


def check_held_out_result():
    vls.clear_acquired_outcome()
    # (a) fall-through baseline = 0/7 (all OOV -> lexicon_predict abstains to NONE)
    for word, _g, _acq, _ho in HELDOUT:
        assert not vls.in_lexicon(lemma_verb(word), "outcome"), f"{word} not OOV (circularity breach)"
    fall = sum(1 for w, g, _a, ho in HELDOUT
               if lexicon_predict(ho) == ("MET" if g == "POS" else "UNMET"))
    assert fall == 0, f"fall-through baseline must be 0/7, got {fall}/7"

    # (b) earned-theta sign relation (read from the frozen reward theta via score_item)
    vt = L.channel_b_valence_table()
    assert vt["RECIPROCITY"] < 0.0 < vt["BLOCK_HIGH"], f"earned-theta sign violation: {vt}"

    # (c) COMBINED acquisition writes back exactly {earn:POS, gain:POS}
    cn, hyp, ne = L.train_channel_a(CORPORA, max_per_seed=6, seed_shuffle=0)
    acquired, _tr = L.run_acquisition(_occ(HELDOUT), cn, hyp, vt, arm="combined")
    got = {k: v["polarity"] for k, v in acquired.items()}
    assert got == {"earn": "POS", "gain": "POS"}, f"combined acquired mismatch: {got}"

    # (d) held-out accuracy via PRODUCTION lexicon_predict with the overlay live = 2/7
    vls.clear_acquired_outcome()
    for lemma, info in acquired.items():
        vls.register_acquired_outcome(lemma, info["polarity"])
    correct = sum(1 for w, g, _a, ho in HELDOUT
                  if lexicon_predict(ho) == ("MET" if g == "POS" else "UNMET"))
    assert correct == 2, f"held-out accuracy must be 2/7, got {correct}/7"
    vls.clear_acquired_outcome()
    print(f"[CHECK held_out] fall-through=0/7 earned_theta_signs=OK "
          f"combined_acquired={got} held_out_accuracy={correct}/7")
    return {"fallthrough": fall, "valence_table": {k: round(v, 4) for k, v in vt.items()},
            "combined_acquired": got, "held_out_accuracy": correct, "channel_a_episodes": ne}


def check_anti_drift_leak_is_real():
    """The measured HARD-FAIL cause, reproduced and reported (not hidden): the two valence-neutral
    transitive noise verbs consolidate POS under the COMBINED (strict-agreement) arm."""
    vt = L.channel_b_valence_table()
    cn, hyp, _ne = L.train_channel_a(CORPORA, max_per_seed=6, seed_shuffle=0)
    occ = []
    for word, sents in NOISE_LEAK:
        for s in sents:
            occ.append({"word": word, "goal_sentences": [], "sentence": s})
    leaked, _tr = L.run_acquisition(occ, cn, hyp, vt, arm="combined")
    got = {k: v["polarity"] for k, v in leaked.items()}
    assert got == {"answer": "POS", "carry": "POS"}, f"expected the measured leak, got {got}"
    vls.clear_acquired_outcome()
    print(f"[CHECK anti_drift_leak] the real HARD-FAIL cause reproduces: neutral transitives "
          f"leak POS -> {got}")
    return {"noise_leak": got}


def check_strict_add_no_regression():
    """Tier-3 is empty by default and NEVER regresses a base Tier-1/Tier-2 classification. Base words
    classify byte-identically whether or not the overlay holds acquired OOV entries; base always wins."""
    vls.clear_acquired_outcome()
    baseline = {w: _classify(w) for w in _BASE_PROBE}
    assert vls.ACQUIRED_OUTCOME_VERB_FEATURES == {}, "overlay must start empty"
    # base words already resolve today (non-None) -> the property under test is that they do not change
    assert baseline["praise"] == "POS" and baseline["punish"] == "NEG", (
        f"base Tier-2 sanity failed: {baseline}")

    # register OOV acquired entries (opposite polarities) and confirm NO base word changes
    vls.register_acquired_outcome("catch", "POS")
    vls.register_acquired_outcome("wast", "NEG")
    after = {w: _classify(w) for w in _BASE_PROBE}
    assert after == baseline, f"STRICT-ADD VIOLATION: base classifications changed: {baseline} -> {after}"
    # the acquired OOV words now classify to their registered polarity (added coverage)
    assert _classify("catch") == "POS" and _classify("wast") == "NEG", "acquired OOV entries not live"
    # a base word is NEVER shadowed even by an overlay entry of the SAME key (base wins in _features_for)
    assert "praise" in vls.OUTCOME_VERB_FEATURES, "expected 'praise' to be a base Tier-2 member"
    vls.register_acquired_outcome("praise", "NEG")   # force a conflicting overlay entry for a base key
    assert _classify("praise") == "POS", "base lexicon must win over an overlay entry of the same key"

    vls.clear_acquired_outcome()
    restored = {w: _classify(w) for w in _BASE_PROBE}
    assert restored == baseline, "clear_acquired_outcome must restore base behavior"
    assert not vls.in_lexicon("catch", "outcome"), "clear must remove acquired OOV entries"
    print("[CHECK strict_add] base Tier-1/Tier-2 classifications unchanged by Tier-3 writes; base "
          "wins over overlay; clear restores fall-through (no-regression proven)")
    return {"baseline": baseline, "after_acquire": after, "restored": restored}


def run():
    r1 = check_held_out_result()
    r2 = check_anti_drift_leak_is_real()
    r3 = check_strict_add_no_regression()
    print("[ALL CHECKS PASS] grounded-word-acquisition increment 1: held-out result reproduced "
          "(fall-through 0/7 -> combined 2/7, earned-theta signs), anti-drift leak (HARD-FAIL cause) "
          "reproduced honestly, strict-ADD no-regression proven. Measured verdict: HARD_FAIL.")
    return {"held_out": r1, "anti_drift_leak": r2, "strict_add": r3}


if __name__ == "__main__":
    run()
