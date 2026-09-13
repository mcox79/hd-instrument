"""WITNESS: hdlab/semantic_hub.py (the ATL convergence hub's live representation store; landed 2026-09-12 from owner-DONE pri-13).
Checks the ORGAN, not the solver's fit (that is verification/test_semantic_hub_convergence.py): (1) the asset loads with unit codes;
(2) graded relatedness orders a related pair above an unrelated one on several anchors; (3) lemma-keyed coverage reaches inflected
forms through the glass-box morphology; (4) neighbours of a concrete noun are semantically near (share the referent's category);
(5) similarity is symmetric and bounded; (6) uncovered words return None (abstain), never a number.
Run: python verification/test_semantic_hub_organ.py
"""
import os
import sys

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
    from hdlab import semantic_hub as SH
    h = SH.get()
    norms = np.linalg.norm(h.vectors[:2000], axis=1)
    check("asset loads; codes are unit vectors", len(h.vocab) > 10000 and np.allclose(norms, 1.0, atol=1e-3), (len(h.vocab), norms.min(), norms.max()))
    pairs = [(("dog", "cat"), ("dog", "democracy")), (("car", "truck"), ("car", "happiness")), (("happy", "joyful"), ("happy", "table")),
             (("king", "queen"), ("king", "spoon"))]
    wins = sum(int((h.similarity(*r) or -9) > (h.similarity(*u) or 9)) for r, u in pairs)
    check("related > unrelated on %d/%d anchor pairs" % (wins, len(pairs)), wins >= 3, [(r, h.similarity(*r), u, h.similarity(*u)) for r, u in pairs])
    check("inflected forms reach the lemma's code (dogs -> dog)", h.covers("dogs") and h.similarity("dogs", "dog") is not None and h.similarity("dogs", "dog") > 0.99, h.similarity("dogs", "dog"))
    nb = [w for w, _ in h.neighbors("dog", 8)]
    check("neighbours of 'dog' are near in kind", sum(int(w in ("puppy", "pet", "cat", "animal", "poodle", "hound", "kitten", "terrier", "donkey", "pig", "horse")) for w in nb) >= 3, nb)
    s1, s2 = h.similarity("car", "truck"), h.similarity("truck", "car")
    check("similarity symmetric and bounded", s1 is not None and abs(s1 - s2) < 1e-6 and -1.0001 <= s1 <= 1.0001, (s1, s2))
    check("uncovered word abstains (None)", h.similarity("xqzvplorth", "dog") is None and not h.covers("xqzvplorth"))
    print("\n%d/%d checks passed" % (PASS, PASS + FAIL))
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
