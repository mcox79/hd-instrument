"""exp_atl_hubspoke_knowledge_integration_v1 -- OPTIMIZE the diagnostic-word identification by INTEGRATING all the
substrate's sense-linked knowledge into a structured MEMBERSHIP clincher-identifier, instead of a dilutive topical
cosine over one centroid.

PROBLEM: build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader

The located loss: the clincher context word EXISTS in the frozen context 87% of the time (ORACLE_single 0.868), but
averaging cosine over all context words dilutes it to 0.336. The brain doesn't average -- controlled retrieval finds
the decisive cue. STRUCTURED, sense-linked knowledge identifies it: a context word literally in the gold sense's
SyntagNet/example/ConceptNet neighbors is a clincher (and correct signal, so -- unlike the anti-dominant prior-shift --
it can pass the MFS guard).

MECHANISM (glass-box, knowledge-integration; the "three-tier multi-source" prior):
  per candidate sense s, SIGNATURE SET Sig(s) = gloss+examples+lemmas+hypernyms (WordNet) U SyntagNet[s] (curated,
    sense-linked) U ConceptNet neighbors of the seeds U gold-LOO-W top associates (leave-one-doc-out; the sense-
    discriminative corpus signal). Multi-source, sense-linked, mostly non-Zipf (curated + structural).
  IDF (diagnosticity by structured specificity): idf(c) = 1 / (1 + #candidate-senses whose Sig contains c). A context
    word in FEW candidates' signatures is the clincher.
  overlap(s) = sum_{c in context} idf(c) * [c in Sig(s)]   -- structured-membership score (NOT topical cosine)
  ARMS: overlap alone; overlap FUSED with the w2v precision cosine (two orthogonal channels, dev-tuned mix);
        winner-take-all (the highest-idf context word in exactly one candidate's Sig picks that sense).
  MFS no-regression guard (full pop); shuffled-signature twin; toward ORACLE 0.63-0.87.

Glass-box, frozen w2v for the cosine channel, NO external LLM/transformer/training. Core-capped. ASCII. Own dir.
# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/_sglite_cache/sglite_syntagnet.pkl
# KB_REFERENT: data/_sglite_cache/kg_conceptnet_lemma_map.pkl
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import json
import time
import pickle
import argparse
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BF

_CACHE = G1._CACHE
OUT_DIR = os.path.join(_REPO, "data", "exp_atl_hubspoke_knowledge_integration_v1")


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _z(x):
    x = np.asarray(x, float); s = x.std()
    return (x - x.mean()) / (s + 1e-9) if s > 1e-9 else x - x.mean()


def run(smoke=False):
    t0 = time.time()
    os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    cn = pickle.load(open(os.path.join(_CACHE, "kg_conceptnet_lemma_map.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_sub = list(np.where((doc % 2 == 0) & sub)[0]); dev_all = list(np.where(doc % 2 == 0)[0])
    test_sub = list(np.where((doc % 2 == 1) & sub)[0]); test_all = list(np.where(doc % 2 == 1)[0])
    if smoke:
        dev_sub, dev_all, test_sub, test_all = dev_sub[:300], dev_all[:600], test_sub[:400], test_all[:800]
    cand = set()
    for i in dev_sub + dev_all + test_sub + test_all:
        cand.update(recs[i]["tn"])
    cand = sorted(cand)
    rich_sig = {s: G1._sigvec(mat, w2i, BF.rich_atom_words(s, w2i, 3)) for s in cand}

    # TWO gold sense->associate W sources, to expose the transductive-leakage artifact explicitly:
    #  - EVEN-ONLY (strictly inductive; disjoint from every ODD test doc -- the clean parent-2 protocol)
    #  - LOO-ALL (leave-one-DOCUMENT-out; uses OTHER odd test docs' gold => TRANSDUCTIVE LEAK on the test population)
    g_even = defaultdict(Counter); g_all = defaultdict(Counter); d_all = defaultdict(lambda: defaultdict(Counter))
    for i in range(len(recs)):
        r = recs[i]; s = r["gold"]; dd = r["doc_id"]
        toks = set(x for x in r["ctx"] if x in w2i)
        for x in toks:
            g_all[s][x] += 1; d_all[dd][s][x] += 1
            if dd % 2 == 0:
                g_even[s][x] += 1
    W_MODE = os.environ.get("W_MODE", "even")     # 'even' = clean inductive (default); 'loo' = transductive control

    def w_assoc(s, dd, k=15):
        if W_MODE == "loo":
            c = Counter()
            for x, n in g_all.get(s, {}).items():
                v = n - d_all[dd].get(s, {}).get(x, 0)
                if v > 0:
                    c[x] = v
            return set(x for x, _ in c.most_common(k))
        return set(x for x, _ in Counter(g_even.get(s, {})).most_common(k))

    # STRUCTURED SIGNATURE SET per sense (knowledge integration), context-independent part cached
    def base_sig(s):
        words = set(BF.rich_atom_words(s, w2i, 1))                 # gloss+ex+lemma+hyp+WN-relations (in-vocab)
        for x in syntag.get(s, []):
            words.add(x.lower().split("_")[0])                    # SyntagNet (curated, sense-linked)
        seeds = list(G1._seed_words(s, w2i))[:6]
        for sd in seeds:
            for x in cn.get(sd, [])[:8]:
                words.add(x)                                       # ConceptNet relational neighbors
        return words
    base_sig_cache = {s: base_sig(s) for s in cand}
    print("[setup] signatures built for %d senses (%.0fs)" % (len(cand), time.time() - t0), flush=True)

    def parts(r):
        tn = r["tn"]; ctxw = [x for x in r["ctx"] if x in w2i]
        if not ctxw:
            return None
        C = np.stack([_unit(mat[w2i[x]]) for x in ctxw])
        G = np.stack([rich_sig[s] if (rich_sig[s] is not None and np.any(rich_sig[s])) else np.zeros(G1.EMB_DIM, np.float32) for s in tn])
        if not np.any(G):
            return None
        # signature set per candidate = base U gold-LOO-W associates
        sig = [base_sig_cache[s] | w_assoc(s, r["doc_id"]) for s in tn]
        # IDF over candidates: a context word in FEW candidate signatures is diagnostic
        idf = {}
        for c in set(ctxw):
            df = sum(1 for S in sig if c in S)
            idf[c] = 0.0 if df == 0 else 1.0 / df
        overlap = np.array([sum(idf[c] for c in ctxw if c in sig[si]) for si in range(len(tn))])
        # precision cosine
        sim = C @ G.T; diag = np.clip(sim.max(1) - sim.mean(1), 0, None)
        thr = np.sort(diag)[-5] if len(diag) > 5 else diag.min()
        wq = np.where(diag >= thr, diag, 0.0) ** 3.0
        qp = _unit((wq[:, None] * C).sum(0)) if wq.sum() > 1e-9 else _unit(C.mean(0))
        prec = G @ qp
        return tn, overlap, prec, tn.index(r["gold"]), ctxw, sig, idf

    def pick(r, lam, mode="fuse", shuffle=False):
        p = parts(r)
        if p is None:
            return None
        tn, overlap, prec, gi, ctxw, sig, idf = p
        ov = overlap
        if shuffle:
            rng = np.random.default_rng((hash(r["lemma"]) & 0xffff) + 3); ov = overlap[rng.permutation(len(overlap))]
        if mode == "overlap":
            sc = ov
        elif mode == "wta":
            # highest-idf context word that is in exactly ONE candidate signature -> that candidate
            best_c, best_idf, best_s = None, -1.0, None
            for c in ctxw:
                mem = [si for si in range(len(tn)) if c in sig[si]]
                if len(mem) == 1 and idf[c] > best_idf:
                    best_idf, best_s = idf[c], mem[0]
            if best_s is not None:
                return int(best_s == gi)
            sc = _z(prec)                                          # fallback to precision
        else:  # fuse
            sc = _z(prec) + lam * _z(ov) if np.any(ov) else _z(prec)
        return int(int(np.argmax(sc)) == gi)

    def acc(idxs, lam, mode="fuse", shuffle=False):
        return np.asarray([v for i in idxs if (v := pick(recs[i], lam, mode, shuffle)) is not None], float)

    prec_dev_all = acc(dev_all, 0.0, "fuse").mean()
    # tune lam on dev subordinate s.t. all-pop no MFS regression
    best_lam, best_dev = 0.0, acc(dev_sub, 0.0, "fuse").mean()
    for lam in [0.25, 0.5, 1.0, 1.5, 2.0]:
        s = acc(dev_sub, lam, "fuse").mean(); a = acc(dev_all, lam, "fuse").mean()
        if a >= prec_dev_all - 0.003 and s > best_dev:
            best_dev, best_lam = float(s), lam
    print("[tune] best_lam=%.2f dev_sub=%.4f (%.0fs)" % (best_lam, best_dev, time.time() - t0), flush=True)

    fuse = acc(test_sub, best_lam, "fuse"); prec = acc(test_sub, 0.0, "fuse")
    ovl = acc(test_sub, 1.0, "overlap"); wta = acc(test_sub, 0.0, "wta")
    twin = acc(test_sub, best_lam, "fuse", shuffle=True)
    mfs_f = acc(test_all, best_lam, "fuse"); mfs_p = acc(test_all, 0.0, "fuse")

    def m(x):
        return round(float(x.mean()), 4) if len(x) else None

    def pair(a, b, seed):
        n = min(len(a), len(b)); return G1._paired(a[:n], b[:n], seed)

    res = {
        "n_test_sub": len(test_sub), "best_lam": best_lam,
        "a_s": {"fuse": m(fuse), "precision": m(prec), "overlap_alone": m(ovl), "wta": m(wta), "twin": m(twin)},
        "fuse_vs_precision": pair(fuse, prec, 891), "fuse_vs_twin": pair(fuse, twin, 892),
        "mfs_guard": {"fuse_all": m(mfs_f), "precision_all": m(mfs_p), "delta": round(float(mfs_f.mean() - mfs_p.mean()), 4),
                      "no_regression": bool(mfs_f.mean() >= mfs_p.mean() - 0.005)},
        "crosses_0.35": bool((m(fuse) or 0) >= 0.35),
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["BAR_PASS"] = bool(res["crosses_0.35"] and res["fuse_vs_precision"]["sep"] and res["fuse_vs_twin"]["sep"]
                           and res["mfs_guard"]["no_regression"])
    res["headline"] = ("KNOWLEDGE INTEGRATION | lam=%.2f | fuse=%.4f precision=%.4f overlap=%.4f wta=%.4f twin=%.4f | "
                       "vs precision sep=%s ci=%s | vs twin sep=%s | MFS %.4f->%.4f no-regr=%s | crosses0.35=%s BAR_PASS=%s"
                       % (best_lam, res["a_s"]["fuse"], res["a_s"]["precision"], res["a_s"]["overlap_alone"],
                          res["a_s"]["wta"], res["a_s"]["twin"], res["fuse_vs_precision"]["sep"],
                          res["fuse_vs_precision"]["ci"], res["fuse_vs_twin"]["sep"], res["mfs_guard"]["precision_all"],
                          res["mfs_guard"]["fuse_all"], res["mfs_guard"]["no_regression"], res["crosses_0.35"],
                          res["BAR_PASS"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "atl_hubspoke_knowledge_integration_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    print("SELFTEST PASS (knowledge-integration cell imports)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke and not args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
