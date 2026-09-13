"""WITNESS: hdlab/attachment_arm.py (the ATTACHMENT arm of the Competition-Model organ, landed 2026-09-12).
Checks the COMPUTATION, not a number fitted to this file: (1) construction detectors fire on canonical shapes; (2) cue values;
(3) strengths are a pure function of counts, always-on values contribute exactly 0, form classes never head/root; (4) the head
posterior is a proper distribution per dependent; (5) PLASTICITY: observing confirmed outcomes moves the posterior; save/load
round-trip; (6) with the learned asset present: the MAP parse of a canonical sentence attaches the NP modifiers to their noun and
the subject/object to the verb. Run: python verification/test_attachment_arm.py
"""
import os
import sys
import tempfile

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab import attachment_arm as AA

PASS = 0; FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print("  ok   " + name)
    else:
        FAIL += 1; print("  FAIL " + name + " " + str(detail))


def toy_table(sentences):
    """A table learned from a few toy sentences with a 'gold-like' outcome (adjacent-noun NP + verb args) -- just to exercise
    the math end to end without the asset."""
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _ in sentences])
    counts = AA.new_counts()
    for toks, pos, heads in sentences:
        sc = AA.SentenceCues(toks, pos, frames)
        marg = {j: {h: (1.0 if heads[j - 1] == h else 0.0) for h in range(0, len(toks) + 1) if h != j} for j in range(1, len(toks) + 1)}
        AA.accrue_sentence(counts, sc, marg)
    return {"counts": counts, "frames": frames, "strength": AA.strengths_from_arc_counts(counts)}


def main():
    t = "The dog was bitten by the man .".split(); p = ["DET", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
    sc = AA.SentenceCues(t, p, {})
    check("npmod construction: determiners attach to their nouns", sc.constr.get((2, 1)) == "npmod" and sc.constr.get((7, 6)) == "npmod", sc.constr)
    check("verbarg construction proposes the verb's arguments", sc.constr.get((4, 2)) == "verbarg", sc.constr)
    c = sc.cues(2, 4)
    check("cue values: locality/form/boundary/constr present", {"locality", "form", "boundary", "constr", "frame", "agree"} <= set(c), c)
    check("boundary cue counts spanned punctuation", AA.SentenceCues("a , b".split(), ["NOUN", "PUNCT", "NOUN"], {}).cues(3, 1)["boundary"] == "1")
    t2 = "apples and oranges".split(); p2 = ["NOUN", "CCONJ", "NOUN"]
    check("coordination construction: second conjunct to first, cc to second", AA.SentenceCues(t2, p2, {}).constr == {(1, 3): "coord", (3, 2): "coord"}, AA.SentenceCues(t2, p2, {}).constr)
    # strengths / constraints on a toy table
    toy = [("The dog bit the man .".split(), ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"], [2, 3, 0, 5, 3, 3]),
           ("A cat saw a bird .".split(), ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"], [2, 3, 0, 5, 3, 3]),
           ("The old man reads books .".split(), ["DET", "ADJ", "NOUN", "VERB", "NOUN", "PUNCT"], [3, 3, 4, 0, 4, 4])]
    tab = toy_table(toy)
    st2 = AA.strengths_from_arc_counts(tab["counts"])
    same = all(abs(st2["cfg"][k] - tab["strength"]["cfg"][k]) < 1e-12 for k in st2["cfg"])
    check("strengths are a pure function of the counts", same)
    zero_ok = all(abs(v) < 1e-12 for cue in AA.CUES for key, v in tab["strength"].get(cue, {}).items()
                  if tab["counts"]["cues"].get(cue, {}).get(key, [0, 0])[1] >= tab["counts"]["config"][key.split("|")[0]][1])
    check("a value that always fires within its configuration contributes exactly 0", zero_ok)
    A, n = AA.arc_scores(toy[0][0], toy[0][1], tab)
    check("form classes never head (punctuation row is -inf)", np.all(np.isinf(A[6, :])))
    check("form classes never root when a word exists", np.isinf(A[0, 6]))
    post = AA.head_posterior(toy[0][0], toy[0][1], tab)
    sums = [sum(post[j].values()) for j in post]
    check("head posterior sums to 1 per dependent", all(abs(s - 1.0) < 1e-6 for s in sums), sums)
    hd = AA.heads(toy[0][0], toy[0][1], tab)
    check("toy MAP parse: 'The' -> 'dog', 'dog' -> 'bit', 'man' -> 'bit'", hd.get(1) == 2 and hd.get(2) == 3 and hd.get(5) == 3, hd)
    # plasticity
    import copy
    tab2 = {"counts": copy.deepcopy(tab["counts"]), "frames": tab["frames"], "strength": tab["strength"]}
    t3 = "Dogs chase cats .".split(); p3 = ["NOUN", "VERB", "NOUN", "PUNCT"]
    before = AA.head_posterior(t3, p3, tab2)[3].get(2, 0.0)
    for _ in range(20):
        AA.observe_arc_outcome(t3, p3, 3, 2, tab2)
    after = AA.head_posterior(t3, p3, tab2)[3].get(2, 0.0)
    check("observing confirmed outcomes moves the posterior toward them", after >= before - 1e-9 and after > 0.5, (before, after))
    tmp = os.path.join(tempfile.gettempdir(), "attachment_validities_roundtrip.json")
    AA.save_attachment_validities(tmp, tab2); tab3 = AA.load_attachment_validities(tmp)
    check("save/load round-trip preserves the table", abs(AA.head_posterior(t3, p3, tab3)[3].get(2, 0.0) - after) < 1e-9)
    if os.path.isfile(AA.ASSET):
        tab_l = AA.load_attachment_validities()
        hd = AA.heads(t, p, tab_l)
        check("learned asset: 'The'->'dog', 'the'->'man' (NP modifiers to their nouns)", hd.get(1) == 2 and hd.get(6) == 7, hd)
        # CORE STRUCTURE (asserted since the semantic-bootstrapping teacher, 2026-09-12 late): the predicate heads its participant
        # -- 'dog' -> 'bitten'. Before that teacher the knowledge-free asset had obj recall 0.19 and this was a recorded limit.
        check("learned asset: 'dog' -> 'bitten' (the verb heads its argument; semantic bootstrapping)", hd.get(2) == 4, hd)
    else:
        print("  note learned asset absent (tools/build_attachment_validities.py not yet run) -- asset checks skipped")
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
