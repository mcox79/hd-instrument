"""exp_consolidation_gate_syntactic_v1 -- the REAL SyntagNet-construction ingredient: DEPENDENCY-restricted
syntagmatic co-occurrence (not the +/-3 window PROXY). SyntagNet's edges are syntactically-LINKED content-word
pairs (N-N, N-V); ours were whole-sentence topical bags. This cell parses the reading corpus with spaCy (an
OFFLINE static-asset builder -- glass-box, reference-only; the RUNTIME readout never calls spaCy), and for each
occurrence of a target word BINDS only its DEPENDENCY-LINKED content neighbours (head + children) to the
sense selected in context -- the tightest, most syntagmatic (least topical) associations reading can give.

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

This closes the one glass-box lever the signal-loss analysis left open: is reading-derived knowledge's failure to
reach curated quality due to TOPICALITY (fixable by syntactic restriction) or something deeper (grounding /
Zipf-starvation)? If dependency-restricted + disambiguated + discrimination-filtered co-occurrence BEATS gloss
CI-sep, syntactic restriction was the lever (PASS). If not, the located negative is PROVEN, not proxied.

BRAIN MECHANISM: syntagmatic relations are SYNTACTIC dependencies (subject-verb, verb-object, modifier-head) --
the local relational structure the parser recovers; binding to dependency neighbours (not a topic bag) is closer
to how a sentence's relational meaning is encoded. Disambiguate-then-bind (LIFG->pMTG/ATL) + cross-situational
consolidation (Yu & Smith) + biased-competition/MFS-quarantine discrimination, all as before.

Strict doc-disjoint SemCor subordinate (odd test), diagnostic readout, NO external LLM at inference. spaCy is an
OFFLINE asset builder only (admissible). ASCII-only. Own data dir.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

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
import experiments.exp_consolidation_discriminative_rescore_v1 as DR
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
_CACHE = G1._CACHE
SIMPLEWIKI = G1.SIMPLEWIKI
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_gate_syntactic_v1")
EMB_DIM = G1.EMB_DIM
_unit = G1._unit
_CONTENT = {"NOUN", "PROPN", "VERB", "ADJ", "ADV"}
_WNPOS = {"NOUN": "n", "VERB": "v", "n": "n", "v": "v", "N": "n", "V": "v"}


def _parse_and_bind(target_senses, gloss_sig, mat, w2i, max_parse):
    """spaCy-parse simplewiki (sentences containing a target lemma); for each target token disambiguate in the
    sentence context and bind its DEPENDENCY-LINKED content neighbours (head + children) to the selected sense."""
    from nltk.corpus import wordnet as wn
    import spacy
    key = "%d_%d" % (max_parse, (hash(frozenset(target_senses)) & 0xffffffff))
    cache = os.path.join(_CACHE, "consol_syntactic_%s.pkl" % key)
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)

    lem_G = {}
    for (lemma, pos), tn in target_senses.items():
        gs = [gloss_sig.get(s) for s in tn]
        if any(g is not None for g in gs):
            G = np.stack([g if g is not None else np.zeros(EMB_DIM, np.float32) for g in gs])
            lem_G[(lemma, pos)] = (tn, G, np.array([g is not None for g in gs]))
    tgt_lemmas = set(l for (l, p) in lem_G)
    pos_present = defaultdict(set)
    for (l, p) in lem_G:
        pos_present[l].add(p)
    morphy_cache = {}

    def has_target(toks):
        for w in toks:
            if w in morphy_cache:
                hit = morphy_cache[w]
            else:
                hit = False
                for p in ("n", "v"):
                    m = wn.morphy(w, p)
                    if m in tgt_lemmas:
                        hit = True; break
                morphy_cache[w] = hit
            if hit:
                return True
        return False

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    cooc = defaultdict(Counter); sel = Counter(); uni = Counter()
    nS = 0; nparsed = 0; nbind = 0; t0 = time.time()

    def gen():
        nonlocal nS
        with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                toks = [w for w in "".join(c.lower() if (c.isalpha() or c == " ") else " " for c in line).split()
                        if len(w) >= 3 and w in w2i and w not in G1._STOP]
                if len(toks) < 4:
                    continue
                for x in set(toks):
                    uni[x] += 1
                nS += 1
                if has_target(toks):
                    yield line.strip()
                if max_parse and nparsed >= max_parse:
                    break

    for doc in nlp.pipe(gen(), batch_size=256):
        nparsed += 1
        # content-word context for disambiguation (surface forms in vocab)
        ctx_all = [t.text.lower() for t in doc if t.pos_ in _CONTENT and t.is_alpha
                   and t.text.lower() in w2i and t.text.lower() not in G1._STOP]
        if len(ctx_all) < 3:
            if max_parse and nparsed >= max_parse:
                break
            continue
        for t in doc:
            if t.pos_ not in ("NOUN", "VERB"):
                continue
            lem = t.lemma_.lower(); pos = _WNPOS[t.pos_]
            if (lem, pos) not in lem_G or pos not in pos_present.get(lem, ()):
                continue
            tn, G, present = lem_G[(lem, pos)]
            surf = t.text.lower()
            ctx = [x for x in ctx_all if x != surf]
            rows = [_unit(mat[w2i[x]]) for x in ctx]
            if not rows:
                continue
            scv = diagnostic_context_scores(np.stack(rows), G)
            scv = np.where(present, scv, -9.0)
            ssyn = tn[int(np.argmax(scv))]
            # DEPENDENCY-LINKED content neighbours: head + children (the syntagmatic pairs)
            neigh = []
            if t.head is not None and t.head is not t and t.head.pos_ in _CONTENT:
                neigh.append(t.head.text.lower())
            for c in t.children:
                if c.pos_ in _CONTENT:
                    neigh.append(c.text.lower())
            bind = set(w for w in neigh if w in w2i and w not in G1._STOP and w != surf)
            if not bind:
                continue
            sel[ssyn] += 1
            cooc[ssyn].update(bind)
            nbind += 1
        if nparsed % 100000 == 0:
            print("[parse] scanned %d, parsed %d, binds %d, senses %d (%.0fs)"
                  % (nS, nparsed, nbind, len(cooc), time.time() - t0), flush=True)
        if max_parse and nparsed >= max_parse:
            break
    out = {"cooc": {k: dict(v) for k, v in cooc.items()}, "sel": dict(sel), "uni": dict(uni),
           "n_sents": nS, "n_parsed": nparsed, "n_binds": nbind}
    with open(cache, "wb") as f:
        pickle.dump(out, f)
    print("[parse] DONE scanned %d parsed %d binds %d senses %d (%.0fs)"
          % (nS, nparsed, nbind, len(cooc), time.time() - t0), flush=True)
    return out


def run(cap, max_parse, smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0]); test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    all_test = list(np.where(doc % 2 == 1)[0])
    if smoke:
        dev_idx = dev_idx[:200]; test_idx = test_idx[:200]; all_test = all_test[:300]
    cand = set(); target_senses = {}
    for i in dev_idx + test_idx + all_test:
        r = recs[i]; cand.update(r["tn"])
        p = _WNPOS.get(r["pos"])
        if p:
            target_senses[(r["lemma"].lower(), p)] = r["tn"]
    sib_by_syn = {s: G1._siblings(s) for s in cand}
    all_syn = set(cand)
    for sibs in sib_by_syn.values():
        all_syn.update(sibs)
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in all_syn}
    gloss_sig = {s: G1._sigvec(mat, w2i, seeds_by_syn[s]) for s in all_syn}
    print("[run] dev=%d test=%d cand=%d targets=%d; parse-and-bind (max_parse=%d)... (%.0fs)"
          % (len(dev_idx), len(test_idx), len(cand), len(target_senses), max_parse, time.time() - t0), flush=True)
    store = _parse_and_bind(target_senses, gloss_sig, mat, w2i, max_parse)

    Ctx_dev = G1.precompute_ctx(recs, dev_idx, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test_idx, mat, w2i)

    def a_s(idxs, Ctx, assoc):
        return G1.score(recs, idxs, G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i), Ctx)

    gloss = {s: [] for s in cand}
    gtest = a_s(test_idx, Ctx_test, gloss)

    # sweep discriminative (ratio,K) on DEV over the syntactic store, freeze on TEST
    best = None; best_dev = -1; best_assoc = None; sweep = {}
    for ratio in [1.0, 1.5]:
        for K in [2, 3]:
            assoc = {s: DR.discriminative_assocs(s, sib_by_syn[s], store, K, ratio, cap) for s in cand}
            dv = float(a_s(dev_idx, Ctx_dev, assoc).mean())
            na = float(np.mean([len(assoc[s]) for s in cand]))
            sweep["r%.1f_K%d" % (ratio, K)] = {"dev": round(dv, 4), "assoc": round(na, 2)}
            print("[sweep] syntactic+discr ratio=%.1f K=%d dev=%.4f assoc/sense=%.1f (%.0fs)"
                  % (ratio, K, dv, na, time.time() - t0), flush=True)
            if dv > best_dev:
                best_dev = dv; best = (ratio, K); best_assoc = assoc
    # also plain recurrence over the syntactic store
    recur = {s: DR.recurrence_assocs(s, store, best[1], cap) for s in cand}
    disc_test = a_s(test_idx, Ctx_test, best_assoc)
    recur_test = a_s(test_idx, Ctx_test, recur)
    syntag_assoc = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    syntag_test = a_s(test_idx, Ctx_test, syntag_assoc)

    n = min(len(gtest), len(disc_test), len(recur_test))
    res = {"n_dev": len(dev_idx), "n_test": len(test_idx), "cap": cap,
           "n_parsed": store["n_parsed"], "n_binds": store["n_binds"], "best_cfg": {"ratio": best[0], "K": best[1]},
           "sweep": sweep,
           "a_s_test": {"gloss": round(float(gtest.mean()), 4),
                        "syntactic_recurrence": round(float(recur_test.mean()), 4),
                        "syntactic_DISCRIMINATIVE": round(float(disc_test.mean()), 4),
                        "curated_syntagnet": round(float(syntag_test.mean()), 4)},
           "mean_assoc": round(float(np.mean([len(best_assoc[s]) for s in cand])), 2),
           "DISCR_vs_gloss": G1._paired(disc_test[:n], gtest[:n], 501),
           "DISCR_vs_recurrence": G1._paired(disc_test[:n], recur_test[:n], 502),
           "syntagnet_vs_gloss": G1._paired(syntag_test[:n], gtest[:n], 503)}
    res["headline"] = ("SYNTACTIC (dependency-linked) | gloss=%.3f syn_recur=%.3f syn_DISCR=%.3f"
                       "(sep_vs_gloss=%s,null=%s) curated=%.3f | best=%s assoc/sense=%.1f parsed=%d"
                       % (res["a_s_test"]["gloss"], res["a_s_test"]["syntactic_recurrence"],
                          res["a_s_test"]["syntactic_DISCRIMINATIVE"], res["DISCR_vs_gloss"]["sep"],
                          res["DISCR_vs_gloss"]["null_p95"], res["a_s_test"]["curated_syntagnet"],
                          res["best_cfg"], res["mean_assoc"], store["n_parsed"]))
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "p%d" % store["n_parsed"])),
              "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_gate_syntactic_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    d = nlp("The dog chased the red ball across the field.")
    verb = [t for t in d if t.lemma_ == "chase"][0]
    kids = [c.text.lower() for c in verb.children]
    assert "dog" in kids and "ball" in kids, "dependency children of 'chased' must include subj/obj: %s" % kids
    print("SELFTEST PASS (spaCy dependency neighbours = syntagmatic subj/obj)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--max-parse", type=int, default=600000)   # sentences CONTAINING a target lemma to parse
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    mp = 4000 if args.smoke else args.max_parse
    run(args.cap, mp, smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
