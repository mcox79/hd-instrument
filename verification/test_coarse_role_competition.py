"""WITNESS: the Competition-Model coarse ROLE LABELER (hdlab.graded_role_assigner.coarse_roles), landed 2026-09-12 as the
first build of the upstream math-BF pass (rung 5 of the affected-entity chain; notes/SIGNAL_LOSS_LEDGER_affected_entity_chain.md).
Checks the computation, not a number fitted to this file: (1) the learned validity asset loads and has the documented shape;
(2) the categorical cues fire as designed (copula, by-under-passive, surface preposition, pronoun case); (3) the MAP labels on
canonical constructions (active SVO, passive with by-agent, copular predicate, noun-governed oblique, object-case pronoun);
(4) the posterior is a proper distribution and the configuration-conditioned contrasts are ~0 for an absent cue; (5) a
twin with SHUFFLED strengths does not reproduce the labels (the information is in the learned validities).
Run: python verification/test_coarse_role_competition.py
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import graded_role_assigner as G

PASS = 0; FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  ok   {name}")
    else:
        FAIL += 1; print(f"  FAIL {name} {detail}")


def main():
    tab = G.load_coarse_validities()
    check("asset loads with prior + strength", len(tab["prior"]) == len(G.ROLE_CLASSES) and "config" in tab["strength"])
    check("every cue has a strength table", all(c in tab["strength"] for c in G.COARSE_CUES))

    # 1. passive with by-agent: "The dog was bitten by the man ."
    t = "The dog was bitten by the man .".split(); p = ["DET", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
    h = {1: 2, 2: 4, 3: 4, 4: 0, 5: 7, 6: 7, 7: 4, 8: 4}
    c2 = G.coarse_role_cues(t, p, h, 2); c7 = G.coarse_role_cues(t, p, h, 7)
    check("voice cue: strong passive, pre-verbal", c2["voice_order"] == "passive_strong_pre", c2)
    check("prep cue: by under passive", c7["prep"] == "by_passive", c7)
    r = G.coarse_roles(t, p, h)
    check("passive subject -> nsubj:pass", r.get(2) == "nsubj:pass", r)
    check("by-phrase -> obl:agent", r.get(7) == "obl:agent", r)

    # 2. active SVO with object-case pronoun: "She saw him ."
    t = "She saw him .".split(); p = ["PRON", "VERB", "PRON", "PUNCT"]; h = {1: 2, 2: 0, 3: 2, 4: 2}
    r = G.coarse_roles(t, p, h)
    check("subject-case pronoun -> nsubj", r.get(1) == "nsubj", r)
    check("object-case pronoun -> obj", r.get(3) == "obj", r)
    check("cue: case obj", G.coarse_role_cues(t, p, h, 3)["case"] == "obj")
    # 2b. double object: "She gave him the book ." -> recipient iobj, patient obj (the IOBJ class + frame cue)
    t = "She gave him the book .".split(); p = ["PRON", "VERB", "PRON", "DET", "NOUN", "PUNCT"]; h = {1: 2, 2: 0, 3: 2, 4: 5, 5: 2, 6: 2}
    r = G.coarse_roles(t, p, h)
    check("double object: recipient -> iobj, patient -> obj", r.get(3) == "iobj" and r.get(5) == "obj", r)
    # KNOWN LIMIT (recorded, not asserted): "She saw him yesterday" -- a bare TIME noun after the object looks like a second
    # object by order alone, so the competition may read "him" as a recipient; the fix is a lexical time/measure class cue.
    t = "She saw him yesterday .".split(); p = ["PRON", "VERB", "PRON", "NOUN", "PUNCT"]; h = {1: 2, 2: 0, 3: 2, 4: 2, 5: 2}
    print("  note known-limit 'saw him yesterday':", G.coarse_roles(t, p, h))

    # 3. copular clause: "John is a teacher ." (predicate nominal is the head)
    t = "John is a teacher .".split(); p = ["PROPN", "AUX", "DET", "NOUN", "PUNCT"]; h = {1: 4, 2: 4, 3: 4, 4: 0, 5: 4}
    c = G.coarse_role_cues(t, p, h, 1)
    check("copula cue fires (AUX between nominal and non-verbal predicate)", c["cop"] == "aux_between", c)
    r = G.coarse_roles(t, p, h)
    check("copular subject -> nsubj (v1 filed it OTHER)", r.get(1) == "nsubj", r)
    check("predicate nominal (root) -> dep", r.get(4) == "dep", r)

    # 4. noun-governed oblique with a SURFACE preposition (attached to the noun, not the nominal): "the man in the car"
    t = "the man in the car".split(); p = ["DET", "NOUN", "ADP", "DET", "NOUN"]; h = {1: 2, 2: 0, 3: 5, 4: 5, 5: 2}
    check("surface prep found via span scan", G.coarse_role_cues(t, p, h, 5)["prep"] == "other")
    h_wrong = {1: 2, 2: 0, 3: 2, 4: 5, 5: 2}   # the ADP mis-attached to the head noun (a predicted-head error)
    check("surface prep robust to ADP mis-attachment", G.coarse_role_cues(t, p, h_wrong, 5)["prep"] == "other")
    r = G.coarse_roles(t, p, h)
    check("noun-governed PP nominal -> obl (v1 filed it OTHER)", r.get(5) == "obl", r)

    # 5. posterior is a distribution; an absent-cue contrast is ~0 (configuration-conditioned)
    post = G.coarse_role_posterior(t, p, h, 5)
    check("posterior sums to 1", abs(float(post.sum()) - 1.0) < 1e-9 and (post >= 0).all())
    S = G.coarse_role_supports(t, p, h, 2)   # "man": root head -> every secondary cue is 'na'/'none' within ROOT_root
    contrasts = [float(np.abs(S[c]).max()) for c in ("voice_order", "cop", "post_slot") if c in S]
    check("always-absent cues (voice/cop/post_slot at a root nominal) carry exactly 0 contrast",
          len(contrasts) == 3 and all(x == 0.0 for x in contrasts), contrasts)

    # 6. twin: shuffled strengths must not reproduce the canonical labels
    rng = np.random.default_rng(7)
    twin = {"prior": tab["prior"], "strength": {}}
    for cue, vals in tab["strength"].items():
        twin["strength"][cue] = {k: v[rng.permutation(len(v))] for k, v in vals.items()}
    t = "The dog was bitten by the man .".split(); p = ["DET", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
    h = {1: 2, 2: 4, 3: 4, 4: 0, 5: 7, 6: 7, 7: 4, 8: 4}
    rt = G.coarse_roles(t, p, h, validities=twin)
    check("shuffled-strength twin breaks the passive/agent labels", not (rt.get(2) == "nsubj:pass" and rt.get(7) == "obl:agent"), rt)

    # 7. PLASTICITY (owner 2026-09-12: never frozen): the table carries counts; observing confirmed outcomes moves the belief;
    #    strengths rebuilt from counts reproduce the loaded strengths exactly; save/load round-trips the grown table.
    import copy, os as _os, tempfile
    tab_l = G.load_coarse_validities()
    check("validity asset carries accrual counts", bool(tab_l.get("counts")))
    rebuilt = G.strengths_from_counts(tab_l["counts"])
    same = all(np.allclose(rebuilt["strength"][c][v], tab_l["strength"][c][v]) for c in rebuilt["strength"] for v in rebuilt["strength"][c])
    check("strengths are a pure function of the counts (rebuild == loaded)", same and np.allclose(rebuilt["prior"], tab_l["prior"]))
    tab2 = {"prior": tab_l["prior"].copy(), "strength": tab_l["strength"], "counts": copy.deepcopy(tab_l["counts"]), "lemma_frames": tab_l["lemma_frames"]}
    t = "She saw him .".split(); p = ["PRON", "VERB", "PRON", "PUNCT"]; h = {1: 2, 2: 0, 3: 2, 4: 2}
    ki = G.ROLE_CLASSES.index("IOBJ")
    before = float(G.coarse_role_posterior(t, p, h, 3, tab2)[ki])
    for _ in range(200):
        G.observe_role_outcome(t, p, h, 3, "IOBJ", tab2)
    after = float(G.coarse_role_posterior(t, p, h, 3, tab2)[ki])
    check("online accrual moves the belief toward the observed outcome", after > before + 0.2, (before, after))
    tmp = _os.path.join(tempfile.gettempdir(), "coarse_role_validities_roundtrip.json")
    G.save_coarse_validities(tmp, tab2); tab3 = G.load_coarse_validities(tmp)
    check("save/load round-trip preserves the grown table", abs(float(G.coarse_role_posterior(t, p, h, 3, tab3)[ki]) - after) < 1e-9)
    print(f"\n{PASS}/{PASS + FAIL} checks passed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
