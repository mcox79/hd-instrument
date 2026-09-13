"""WITNESS: hdlab/lexical_categories.py (the CATEGORY organ's count-based generative model + forward-backward posterior; landed
2026-09-12 from the owner-DONE pri-12 solver's prototype). Checks the COMPUTATION: (1) the posterior is a distribution per token;
(2) the point readout is the argmax of the posterior; (3) accuracy on a UD-EWT test slice is above the majority-class floor and
within the measured band (>= 0.88; full test 0.9120 vs the perceptron 0.9445); (4) unknown words are categorised by the suffix cue
('barked' -> VERB); (5) PLASTICITY: observing a confirmed categorisation moves the posterior; (6) save/load round-trip preserves
the posterior; (7) the reader's live tag path uses the organ by default (HDLAB_TAG_SOURCE unset -> counts).
Run: python verification/test_lexical_categories.py
"""
import os
import sys
import tempfile

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

PASS = 0; FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print("  ok   " + name)
    else:
        FAIL += 1; print("  FAIL " + name + " " + str(detail))


def main():
    import hdlab.lexical_categories as LC
    from tools.build_attachment_validities import sentences, TEST
    m = LC.get()
    toks = "The dog was bitten by the man because it barked .".split()
    post = m.posterior(toks)
    check("posterior is a distribution per token", np.allclose(post.sum(axis=1), 1.0), post.sum(axis=1))
    tags = m.tag(toks)
    check("point readout = argmax of the posterior", tags == [m.tags[int(i)] for i in post.argmax(axis=1)])
    check("unknown word by suffix cue: 'barked' -> VERB", "barked" not in m.vocab and tags[9] == "VERB", (tags[9], "barked" in m.vocab))
    te = sentences(TEST, cap=400, maxlen=10**6)
    a = n = 0
    maj = {}
    for t, g, _, _ in te:
        for x, y in zip(m.tag(t), g):
            a += int(x == y); n += 1; maj[y] = maj.get(y, 0) + 1
    acc = a / n; floor = max(maj.values()) / n
    check("accuracy on 400 UD-EWT test sentences >= 0.88 and above the majority floor", acc >= 0.88 and acc > floor + 0.3, (round(acc, 4), round(floor, 4)))
    # plasticity: a made-up word observed as ADJ moves its posterior
    import copy
    m2 = LC.LexicalCategories(lam=m.lam, suf_len=m.suf_len)
    m2.emit = copy.deepcopy(m.emit); m2.tag_count = copy.deepcopy(m.tag_count); m2.trans = copy.deepcopy(m.trans)
    m2.suf = copy.deepcopy(m.suf); m2.suf_tot = copy.deepcopy(m.suf_tot); m2.vocab = set(m.vocab); m2.finalize()
    w = "zorply"; s2 = ["the", w, "dog", "."]
    before = float(m2.posterior(s2)[1, m2.tag_idx["ADJ"]])
    for _ in range(5):
        m2.observe(s2, ["DET", "ADJ", "NOUN", "PUNCT"])
    after = float(m2.posterior(s2)[1, m2.tag_idx["ADJ"]])
    check("plasticity: observing confirmed categorisations moves the posterior", after > before and after > 0.5, (round(before, 3), round(after, 3)))
    tmp = os.path.join(tempfile.gettempdir(), "lexical_categories_roundtrip.json")
    m2.save(tmp); m3 = LC.LexicalCategories.load(tmp)
    check("save/load round-trip preserves the posterior", abs(float(m3.posterior(s2)[1, m3.tag_idx["ADJ"]]) - after) < 1e-9)
    import hdlab.situation_reader as SR
    check("the reader's live tag path defaults to the category organ", SR._TAG_SOURCE == "counts" or os.environ.get("HDLAB_TAG_SOURCE") == "perceptron", SR._TAG_SOURCE)
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
