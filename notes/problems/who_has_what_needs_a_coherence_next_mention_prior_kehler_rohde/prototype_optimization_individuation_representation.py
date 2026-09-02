"""PROTOTYPE THE OPTIMIZATION to the root component (the entity-INDIVIDUATION representation). The grounded cue
(12-dim mean event vec) holds the answer on 68% of recoverable errors but is the weakest standalone (0.516) --
too coarse to individuate two people. Build SHARPER glass-box, no-LLM entity representations and test whether the
individuation cue's standalone accuracy rises AND the integrator breaks past 0.677 toward the 0.905 oracle:
  ENR1  TF-IDF content cosine  -- down-weight common words -> rare, entity-SPECIFIC words individuate (sharper lexical)
  ENR2  full grounded PROFILE  -- mean grounded vec of ALL the entity's content words (not just gov_verb/obj_head event)
  ENR3  discriminative metric  -- learn (on DEV) a weighting over the enriched semantic features (a conjunctive
        individuation code, research DELTA 6) that maximizes candidate discrimination.
Report each enriched cue's STANDALONE accuracy vs the base cues, and the integrator accuracy with the enriched cues."""
import os, sys, math, numpy as np
sys.path.insert(0, os.path.abspath("."))
import experiments.exp_coref_faithful_integrator_deltas_v1 as F
import experiments.exp_coref_coherence_prior_on_chain_bucket_v1 as M
from experiments.exp_litbank_activation_binder_v1 import PRONOUNS
from hdlab.coref import infer_nominal_gender
from collections import defaultdict, Counter

streams, all_docs, chain, sdmap, by_doc, goldh, person = F._prep(None)
dev, test = set(all_docs[0::2]), set(all_docs[1::2])
cache = {}

# ---- corpus IDF over mention-sentence content (each sentence a 'document') ----
df = Counter(); ndoc = 0
for doc in all_docs:
    for s in range(len(M.P.sents(doc))):
        cw = F._content(cache, doc, s)
        if cw:
            ndoc += 1
            for w in cw:
                df[w] += 1
idf = {w: math.log(ndoc / c) for w, c in df.items()}


def gvecw(w):
    return M.P.gvec(w)


def _z(a):
    a = np.array(a, float); s = a.std(); return (a - a.mean()) / s if s > 1e-9 else a * 0.0


def enriched_feats(docs):
    """base 4 cues + ENR1 tfidf-content + ENR2 full-grounded-profile, per candidate."""
    out = []
    for doc in sorted(docs):
        for r in chain[doc]:
            if not r["sd"]:
                continue
            gold = r["inst"]["gold_cid"]
            ids = [c for c in r["inst"]["cand_ids"] if person[doc].get(c) or c == gold]
            if gold not in ids or len(ids) < 2:
                continue
            inst = {**r["inst"], "cand_ids": ids, "prior": {c: r["inst"]["prior"][c] for c in ids}}
            net, gi, _i, _s = M.graded_net(inst, F.W, F.D)
            _dd, ps, pst = r["mkey"]; ck = (ps, pst if pst is not None else -1)
            gv = ob = ev = None
            for t in goldh[doc].get(gold, []):
                if (t[0], t[1] if t[1] is not None else -1) == ck:
                    gv, ob, ev = t[2], t[3], t[4]; break
            cur_cw = F._content(cache, doc, ps)
            cur_tfidf = {w: idf.get(w, 0.0) for w in cur_cw}
            cur_g = [gvecw(w) for w in cur_cw if gvecw(w) is not None]
            cur_gprofile = np.mean(np.stack(cur_g), 0) if cur_g else None
            cont, grnd, exa, tfidf, gprof = [], [], [], [], []
            for c in ids:
                past = [t for t in goldh[doc].get(c, []) if (t[0], t[1] if t[1] is not None else -1) < ck]
                cb = set(); pv = []; psents = set()
                for t in past:
                    psents.add(t[0])
                    if t[4] is not None:
                        pv.append(t[4])
                for s2 in psents:
                    cb |= F._content(cache, doc, s2)
                cont.append(len(cur_cw & cb) / len(cur_cw | cb) if (cur_cw and cb) else 0.0)
                grnd.append(max([M.P.cos(ev, v) for v in pv] or [0.0]) if ev is not None else 0.0)
                exa.append(float(sum(1 for t in past if (gv and t[2] == gv) or (ob and t[3] == ob))))
                # ENR1: tf-idf weighted content cosine
                ent_tfidf = defaultdict(float)
                for s2 in psents:
                    for w in F._content(cache, doc, s2):
                        ent_tfidf[w] += idf.get(w, 0.0)
                num = sum(cur_tfidf.get(w, 0.0) * ent_tfidf.get(w, 0.0) for w in cur_tfidf)
                na = math.sqrt(sum(v * v for v in cur_tfidf.values())); nb = math.sqrt(sum(v * v for v in ent_tfidf.values()))
                tfidf.append(num / (na * nb) if na > 0 and nb > 0 else 0.0)
                # ENR2: full grounded profile (mean grounded vec of ALL the entity's content words)
                gw = [gvecw(w) for s2 in psents for w in F._content(cache, doc, s2) if gvecw(w) is not None]
                ent_gprof = np.mean(np.stack(gw), 0) if gw else None
                gprof.append(M.P.cos(cur_gprofile, ent_gprof) if (cur_gprofile is not None and ent_gprof is not None) else 0.0)
            X = np.stack([_z(net), _z(cont), _z(grnd), _z(exa), _z(tfidf), _z(gprof)], 1)
            out.append((X, gi, doc, (np.array(net), np.array(cont), np.array(grnd), np.array(exa), np.array(tfidf), np.array(gprof))))
    return out


DEV = enriched_feats(dev)
TEST = enriched_feats(test)
NAMES = ["net", "content(jac)", "grounded(event)", "exact", "ENR1 tfidf-content", "ENR2 grounded-profile"]
n = len(TEST)
print("standalone cue accuracy on the bucket (n=%d):" % n)
for j in range(6):
    acc = np.mean([int(np.argmax(raw[j]) == gi) for (X, gi, doc, raw) in TEST])
    print("  %-24s %.3f" % (NAMES[j], acc))


def fit(data, cols, lam=0.3, lr=0.3, it=400):
    b = np.zeros(len(cols))
    for _ in range(it):
        gr = -2 * lam * b
        for (X, gi, *_r) in data:
            Xu = X[:, cols]; s = Xu @ b; p = np.exp(s - s.max()); p /= p.sum() + 1e-12; gr += Xu[gi] - p @ Xu
        b += lr / len(data) * gr
    return b


def accdoc(data, b, cols):
    ok = defaultdict(lambda: [0, 0])
    for (X, gi, doc, *_r) in data:
        ok[doc][0] += int(np.argmax(X[:, cols] @ b) == gi); ok[doc][1] += 1
    return ok


floor = defaultdict(lambda: [0, 0])
for (X, gi, doc, raw) in TEST:
    floor[doc][0] += int(np.argmax(raw[0]) == gi); floor[doc][1] += 1
print("\nINTEGRATOR accuracy (vs floor 0.6139, base-4 0.677, oracle-of-6-cues below):")
for label, cols in [("base 4 cues", [0, 1, 2, 3]), ("+ENR1 tfidf", [0, 1, 2, 3, 4]),
                    ("REPLACE content w/ ENR1", [0, 4, 2, 3]), ("net+ENR1+grounded", [0, 4, 2]),
                    ("net+ENR1 only", [0, 4]), ("+ENR1+ENR2 (enriched)", [0, 1, 2, 3, 4, 5])]:
    b = fit([(X, gi, d) for (X, gi, d, _r) in DEV], cols)
    ok = accdoc(TEST, b, cols)
    print("  %-24s %.4f   %s" % (label, sum(v[0] for v in ok.values()) / sum(v[1] for v in ok.values()), F._paired(ok, floor, 5)))
orc6 = np.mean([int(any(int(np.argmax(raw[j]) == gi) for j in range(6))) for (X, gi, doc, raw) in TEST])
print("  ORACLE (any of 6 cues right)  %.4f" % orc6)
