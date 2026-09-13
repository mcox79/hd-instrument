"""DIAGNOSTIC (strategy 2026-09-13): whole-sentence tree search vs INCREMENTAL commitment on the attachment arm's cue activations.
usage: python experiments/_diag_decode_incremental.py [cap] [configs]   configs = comma list of map1 | incr:<beam>:<hold>[:<mode expect|const>[:<norm sum|local>]]
Same sentences, same arc activations (gold categories, UD-EWT test), same convention layer; UAS over all tokens + per-relation recall
+ the incremental arm's incomplete-word rate (words still waiting at the end, attached by repair) + seconds per config."""
import os, sys, json, time
from collections import Counter
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.attachment_arm as AA
from tools.build_attachment_validities import sentences, TEST
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 700
cfgs = (sys.argv[2] if len(sys.argv) > 2 else "map1,incr:8:0:expect:local,incr:1:0,incr:4:0,incr:8:0,incr:32:0,incr:8:-1,incr:8:1,incr:8:0:const").split(",")
RELS = ("root", "nsubj", "obj", "obl", "nmod", "ccomp", "xcomp", "advcl", "conj", "punct", "amod", "det", "case")
test = sentences(TEST, cap=cap, maxlen=10**6); tab = AA.load_attachment_validities()
arcs = [AA.arc_scores(toks, pos, tab) for toks, pos, _, _ in test]
for cfg in cfgs:
    parts = cfg.split(":"); AA.DECODE = parts[0]
    if parts[0] == "incr":
        AA.INCR_BEAM = int(parts[1]); AA.INCR_HOLD = float(parts[2]); AA.INCR_HOLD_MODE = parts[3] if len(parts) > 3 else "expect"; AA.INCR_NORM = parts[4] if len(parts) > 4 else "sum"
    for k in AA.INCR_STATS: AA.INCR_STATS[k] = 0
    tot = ok = 0; rt = Counter(); rk = Counter(); t0 = time.time()
    for (toks, pos, heads_g, rels), (A, n) in zip(test, arcs):
        hd, _ = AA.decode(toks, pos, A, n)
        for i, (g, r) in enumerate(zip(heads_g, rels), start=1):
            tot += 1; hit = hd.get(i, -1) == g; ok += hit
            if r in RELS:
                rt[r] += 1; rk[r] += hit
    st = AA.INCR_STATS
    print(json.dumps({"cfg": cfg, "n_sent": len(test), "tokens": tot, "UAS": round(ok / max(1, tot), 4),
                      "rel": {r: round(rk[r] / max(1, rt[r]), 3) for r in RELS},
                      "incomplete_rate": round(st["incomplete_words"] / max(1, st["words"]), 4) if st["words"] else None,
                      "sec": round(time.time() - t0, 1)}))
