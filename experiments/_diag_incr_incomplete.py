"""DIAGNOSTIC (2026-09-13): anatomy of the incremental arm's WRAP-UP words (held to the end, attached by repair): by category, with
the gold head's side and whether the repair got it right. usage: python experiments/_diag_incr_incomplete.py [cap] [beam] [hold]"""
import os, sys, json
from collections import Counter
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 300
AA.DECODE = "incr"; AA.INCR_BEAM = int(sys.argv[2]) if len(sys.argv) > 2 else 8; AA.INCR_HOLD = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
tab = AA.load_attachment_validities(); test = sentences(TEST, cap=cap, maxlen=10**6)
by_cat = Counter(); ok_cat = Counter(); gold_side = Counter(); tot = 0; wrong_examples = []
for toks, pos, hg, rels in test:
    A, n = AA.arc_scores(toks, pos, tab); hd, _ = AA.decode(toks, pos, A, n)
    for j in AA.INCR_STATS["last_incomplete"]:
        tot += 1; c = pos[j - 1]; g = hg[j - 1]; by_cat[c] += 1
        ok = hd.get(j) == g; ok_cat[c] += ok
        gold_side[("root" if g == 0 else ("L" if g < j else "R"))] += 1
        if not ok and len(wrong_examples) < 10:
            wrong_examples.append({"w": toks[j - 1], "cat": c, "gold": toks[g - 1] if g else "ROOT", "pred": toks[hd[j] - 1] if hd.get(j) else "ROOT", "rel": rels[j - 1]})
print(json.dumps({"wrapup_words": tot, "by_cat": {c: [by_cat[c], round(ok_cat[c] / by_cat[c], 2)] for c, _ in by_cat.most_common(10)},
                  "gold_head_side": dict(gold_side)}))
for e in wrong_examples: print(json.dumps(e, ensure_ascii=False))
