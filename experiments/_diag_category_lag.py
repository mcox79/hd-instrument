"""DIAGNOSTIC (strategy 2026-09-13): the cost of INCREMENTALITY at the categories rung. The category organ's belief about word i
using only words up to i + lag (lag 0 = the running belief at arrival; k = revision within k words; inf = whole-sentence smoothing).
usage: python experiments/_diag_category_lag.py [cap_sentences] [lags comma list, 'inf' allowed]   (UD-EWT test, UPOS, live asset)"""
import os, sys, json, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, REPO)
import hdlab.lexical_categories as LC
cap = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
lags = (sys.argv[2] if len(sys.argv) > 2 else "0,1,2,3,5,inf").split(",")
TEST = os.path.join(REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
sents, cur = [], []
with open(TEST, encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line:
            if cur: sents.append(cur); cur = []
            continue
        if line.startswith("#"): continue
        c = line.split("\t")
        if "-" in c[0] or "." in c[0]: continue
        cur.append((c[1], c[3]))
if cur: sents.append(cur)
sents = sents[:cap]
m = LC.get(); known = set(m.vocab) if hasattr(m, "vocab") else set()
for lg in lags:
    lag = None if lg == "inf" else int(lg)
    tot = ok = unk = unk_ok = 0; t0 = time.time()
    for s in sents:
        words = [w for w, _ in s]; gold = [g for _, g in s]
        post = m.posterior(words, lag=lag); pred = [m.tags[int(i)] for i in post.argmax(axis=1)]
        for w, g, p in zip(words, gold, pred):
            tot += 1; hit = (g == p); ok += hit
            if known and w.lower() not in known:
                unk += 1; unk_ok += hit
    print(json.dumps({"lag": lg, "n_sent": len(sents), "tokens": tot, "acc": round(ok / max(1, tot), 4),
                      "unknown_acc": round(unk_ok / max(1, unk), 4) if unk else None, "sec": round(time.time() - t0, 1)}))
