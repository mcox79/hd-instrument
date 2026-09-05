"""exp_knowledge_factory_meaning_store_v1 -- THE FIRST VERTICAL SLICE of the knowledge-import factory:
BUILD -> TRIM -> FREEZE -> RELOAD -> VALIDATE the MEANING store (per-sense signature vectors) as a static
offline asset, and prove the FROZEN asset delivers the proven +0.0665 meaning lift THROUGH the live
`hdlab.diagnostic_context_wsd` readout (with the P9 precision-weighting), the info-free twin LOSING and NO
MFS regression.

PROBLEM: build_and_freeze_the_clean_curated_knowledge_foundation_the_proven_meaning_lift

WHY THIS SLICE FIRST. It is the proven anchor (+0.0665 CI-sep, measured in exp_brain_faithful_reader_v1) and it
exercises the WHOLE factory end-to-end (adapter -> learner-consolidation/trim -> freeze -> reload -> validate ->
wire). Once green, the other typed stores (typed selectional preference; affect/frame lexicons) are added as
adapters + consumers to this working spine.

HOW THE BRAIN DOES THIS (PINNED). Word meaning is a CONSOLIDATED neocortical semantic store (ATL hub; CLS
consolidation, McClelland-McNaughton-O'Reilly 1995) CONSULTED at comprehension via biased-competition controlled
retrieval (LIFG/pMTG; Jefferies 2013; Lambon-Ralph 2017) -- NOT re-derived per read, and NOT a raw dictionary
dump. So the foundation is BUILT by the consolidation machinery (curated source admitted + schema-gated/pruned)
and FROZEN, exactly the store the online reading-experience learner later extends.

  * ADAPTER (curated source -> per-sense word bag): reuse rich_atom_words (gloss+examples+lemmas+hypernyms +
    WordNet relations + curated SyntagNet + ConceptNet) = the admissible offline foundation.
  * TRIM / OPTIMIZE (the learner's schema-gating = synaptic pruning): keep only associate words that
    DISCRIMINATE this sense from its sibling senses by a margin (the consolidation gate's schema step,
    generalized from reading co-occurrence to curated knowledge). Tuned on DEV, locked, reported on TEST.
  * SIGNATURE (mean-w2v unit vector per synset) -> FREEZE (npz: names + float32 unit matrix) -> the live readout
    loads THIS instead of recomputing gloss vectors.

Strict document-disjoint SemCor subordinate, DEV=even docs (tune), TEST=odd docs (report), n_test~2675.
Glass-box, NO external LLM, NO training. Pure numpy. ASCII.
Run: .venv/Scripts/python.exe experiments/exp_knowledge_factory_meaning_store_v1.py --self-test
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import sys
import json
import time
import pickle
import argparse

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_consolidation_gate_v1 as G1
import experiments.exp_brain_faithful_reader_v1 as BFR
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

_CACHE = G1._CACHE
EMB_DIM = G1.EMB_DIM
OUT_DIR = os.path.join(_REPO, "data", "exp_knowledge_factory_meaning_store_v1")
_ZERO = np.zeros(EMB_DIM, np.float32)


# ---------------------------------------------------------------------------------------------------
# ADAPTER: curated source -> per-sense word bag (seeds = gloss floor; associates = the curated knowledge)
# ---------------------------------------------------------------------------------------------------
def _srt_syn(lst):
    return sorted(lst, key=lambda x: x.name())


def sense_word_bag(syn, w2i, level):
    """DETERMINISTIC curated word bag for a synset. level 0=gloss floor; 1=+WordNet relations; 2=+SyntagNet;
    3=+ConceptNet. Mirrors exp_brain_faithful_reader_v1.rich_atom_words BUT sorts each relation set by synset
    name BEFORE the cap -- rich_atom_words did `s.hyponyms()[:8]` and NLTK returns relations in HASH-RANDOMISED
    order, so the cap picked a DIFFERENT 8 hyponyms every PYTHONHASHSEED (a frozen asset must be byte-reproducible;
    this also means the parent's landed 0.3178 was itself hash-seed-dependent). Sorted-then-capped = deterministic."""
    from nltk.corpus import wordnet as wn
    w = list(G1._seed_words(syn, w2i))
    try:
        s = wn.synset(syn)
        if level >= 1:
            rels = (_srt_syn(s.hyponyms())[:8] + _srt_syn(s.part_meronyms())[:4]
                    + _srt_syn(s.member_holonyms())[:4] + _srt_syn(s.similar_tos())
                    + _srt_syn(s.also_sees())[:4] + _srt_syn(s.verb_groups()))
            for h in rels:
                for ln in h.lemma_names():
                    w.append(ln.lower().split("_")[0])
                w += G1._toks(h.definition())
        if level >= 2:
            w += [x.lower().split("_")[0] for x in BFR._syntag().get(syn, [])]
        if level >= 3:
            cn = BFR._cn()
            for seed in list(dict.fromkeys(G1._seed_words(syn, w2i)))[:8]:
                w += cn.get(seed, [])
    except Exception:
        pass
    return [x for x in w if x in w2i]


def seeds_and_associates(syn, w2i, level):
    """Split the bag into SEEDS (the gloss-floor L0 words -- always kept) and ASSOCIATES (the curated knowledge
    added at levels>=1 -- the words the trimmer may prune). Order-preserving, de-duped."""
    seeds = list(dict.fromkeys(G1._seed_words(syn, w2i)))
    seedset = set(seeds)
    assoc = [w for w in sense_word_bag(syn, w2i, level) if w not in seedset]
    return seeds, list(dict.fromkeys(assoc))


# ---------------------------------------------------------------------------------------------------
# THE TRIMMING / OPTIMIZATION TOOL (learner schema-gating = discriminative synaptic pruning)
# ---------------------------------------------------------------------------------------------------
def _sib_sigs(syn, seed_sig_by_syn):
    """Sibling-sense signatures (competitors that share a lemma) -- the schema competitors to discriminate from."""
    sibs = []
    for t in G1._siblings(syn):
        v = seed_sig_by_syn.get(t)
        if v is not None:
            sibs.append(v)
    return sibs


def trim_associates(assoc, mat, w2i, sig_self, sib_sigs, margin):
    """Keep only associate words that DISCRIMINATE this sense from its siblings: (w.self - max_sib w.sib) >= margin.
    margin=None or <=-1 -> no trimming (keep all). This is the consolidation gate's schema step (byte-equivalent to
    the discriminative keep in G1.consolidate) applied to CURATED associates instead of reading co-occurrence."""
    if margin is None or margin <= -1.0 or not assoc or sig_self is None:
        return list(assoc)
    idx = [w2i[w] for w in assoc if w in w2i]
    kept_words = [w for w in assoc if w in w2i]
    if not idx:
        return list(assoc)
    V = mat[idx]
    V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
    self_s = V @ sig_self
    if sib_sigs:
        S = np.stack(sib_sigs)
        sib_s = (V @ S.T).max(axis=1)
    else:
        sib_s = np.full(len(kept_words), -1.0)
    keep = (self_s - sib_s) >= margin
    return [w for w, k in zip(kept_words, keep) if k]


# ---------------------------------------------------------------------------------------------------
# SIGNATURE BUILD + FREEZE/RELOAD (the static offline asset)
# ---------------------------------------------------------------------------------------------------
def prep_bags(synsets, mat, w2i, level):
    """Gather the EXPENSIVE per-synset material ONCE (WordNet/SyntagNet/ConceptNet lookups): seed words, associate
    words, seed signature, sibling signatures. A margin sweep then only re-trims + re-means (cheap)."""
    syns = list(synsets)
    seed_words = {s: list(dict.fromkeys(G1._seed_words(s, w2i))) for s in syns}
    seed_sig = {s: G1._sigvec(mat, w2i, seed_words[s]) for s in syns}
    assoc = {s: seeds_and_associates(s, w2i, level)[1] for s in syns}
    sib = {s: _sib_sigs(s, seed_sig) for s in syns}
    return {"syns": syns, "seed_words": seed_words, "seed_sig": seed_sig, "assoc": assoc, "sib": sib}


def sigs_at(prep, mat, w2i, margin, shuffle_rng=None):
    """Build per-synset signatures from a prep at a given trim margin. shuffle_rng => the INFO-FREE twin (permute
    the ASSOCIATE bags onto the WRONG synsets; seeds kept correct)."""
    syns = prep["syns"]; assoc = prep["assoc"]
    if shuffle_rng is not None:
        perm = shuffle_rng.permutation(len(syns))
        assoc = {syns[i]: prep["assoc"][syns[perm[i]]] for i in range(len(syns))}
    sig = {}
    for s in syns:
        a = trim_associates(assoc[s], mat, w2i, prep["seed_sig"][s], prep["sib"][s], margin)
        sig[s] = G1._sigvec(mat, w2i, prep["seed_words"][s] + a)
    return sig


def build_sense_signatures(synsets, mat, w2i, level, margin=None, shuffle_rng=None):
    """Per-synset unit signature (mean-w2v of seeds+trimmed-associates). Thin wrapper over prep_bags+sigs_at."""
    return sigs_at(prep_bags(synsets, mat, w2i, level), mat, w2i, margin, shuffle_rng=shuffle_rng)


def freeze(sig_by_syn, path, meta):
    """Serialize the meaning store: names[] + float32 unit matrix (missing sig -> zero row). Deterministic."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    names = sorted(sig_by_syn.keys())
    M = np.zeros((len(names), EMB_DIM), np.float32)
    for i, n in enumerate(names):
        v = sig_by_syn.get(n)
        if v is not None:
            M[i] = v.astype(np.float32)
    np.savez_compressed(path, names=np.array(names), vecs=M, meta=json.dumps(meta))
    return path


def build_and_freeze_full(level=3, dtype="float16", smoke=False, out_path=None):
    """BUILD + FREEZE the BROAD-COVERAGE foundation: one signature for EVERY WordNet synset with >=1 in-vocab
    gloss/associate word. The static offline asset the live reader loads. Streaming (does not hold all bags in
    memory); margin=None (the proven keep-all config -- trimming curated knowledge only removes coverage).
    Fast format: sorted names + a contiguous unit matrix (dtype); synset->row rebuilt O(1) at load; mmap-friendly."""
    from nltk.corpus import wordnet as wn
    t0 = time.time()
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb")); w2i, mat = emb["w2i"], emb["mat"]
    syns = sorted(s.name() for s in wn.all_synsets())
    if smoke:
        syns = syns[:3000]
    names, rows = [], []
    for j, s in enumerate(syns):
        seeds, assoc = seeds_and_associates(s, w2i, level)
        v = G1._sigvec(mat, w2i, seeds + assoc)
        if v is None:
            continue
        names.append(s); rows.append(v)
        if j % 20000 == 0:
            print("[freeze-full] %d/%d synsets, %d kept (%.0fs)" % (j, len(syns), len(names), time.time() - t0), flush=True)
    M = np.stack(rows).astype(dtype)
    if out_path is None:
        out_path = os.path.join(OUT_DIR, "meaning_sense_signatures_wordnet_%s.npz" % ("smoke" if smoke else "full"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    meta = {"level": level, "margin": None, "dim": EMB_DIM, "n": len(names), "dtype": dtype,
            "coverage": "all_wordnet_synsets_with_invocab_words", "source": "wordnet+syntagnet+conceptnet",
            "builder": "exp_knowledge_factory_meaning_store_v1.build_and_freeze_full"}
    np.savez_compressed(out_path, names=np.array(names), vecs=M, meta=json.dumps(meta))
    sz = os.path.getsize(out_path) / 1e6
    print("[freeze-full] WROTE %d synsets x %d dim (%s) -> %s  %.1f MB  (%.0fs)"
          % (len(names), EMB_DIM, dtype, out_path, sz, time.time() - t0), flush=True)
    return {"path": out_path, "n": len(names), "mb": round(sz, 1), "dtype": dtype, "elapsed_s": round(time.time() - t0, 1)}


def load_frozen(path):
    """Reload the frozen store -> {synset_name: unit vec (or None for a zero row)}."""
    z = np.load(path, allow_pickle=True)
    names = list(z["names"]); M = z["vecs"]
    out = {}
    for i, n in enumerate(names):
        v = M[i]
        out[str(n)] = v if float(np.linalg.norm(v)) > 1e-9 else None
    return out


# ---------------------------------------------------------------------------------------------------
# VALIDATE: a_s through the LIVE hdlab readout (with P9 precision-weighting gamma/topk)
# ---------------------------------------------------------------------------------------------------
def a_s(recs, idxs, sig_by_syn, Ctx, gamma=1.0, topk=None):
    ok = []
    for i in idxs:
        C = Ctx[i]
        if C is None:
            continue
        tn = recs[i]["tn"]
        G = np.stack([sig_by_syn.get(s) if sig_by_syn.get(s) is not None else _ZERO for s in tn])
        if not np.any(G):
            continue
        sc = diagnostic_context_scores(C, G, gamma=gamma, topk=topk)
        ok.append(int(tn[int(np.argmax(sc))] == recs[i]["gold"]))
    return np.array(ok, float)


def _load_eval():
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev = list(np.where((doc % 2 == 0) & sub)[0]); test = list(np.where((doc % 2 == 1) & sub)[0])
    test_all = list(np.where(doc % 2 == 1)[0])   # ALL senses (dominant+subordinate) -- the MFS-guard population
    return w2i, mat, recs, dev, test, test_all


def run(level=3, smoke=False, margin=None, gamma=1.0, topk=None, do_freeze=True):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = _load_eval()
    if smoke:
        dev = dev[:250]; test = test[:250]; test_all = test_all[:500]
    cand = set()
    for i in dev + test + test_all:
        cand.update(recs[i]["tn"])
    Ctx_test = G1.precompute_ctx(recs, test, mat, w2i)
    print("[run] dev=%d test=%d cand=%d (%.0fs)" % (len(dev), len(test), len(cand), time.time() - t0), flush=True)

    # BUILD gloss floor (L0) + rich (level), on-the-fly
    sig_gloss = build_sense_signatures(cand, mat, w2i, 0, margin=None)
    sig_rich = build_sense_signatures(cand, mat, w2i, level, margin=margin)
    sig_shuf = build_sense_signatures(cand, mat, w2i, level, margin=margin,
                                      shuffle_rng=np.random.default_rng(1234))

    # FREEZE the rich store + RELOAD (freeze-fidelity)
    frozen_path = None; sig_frozen = sig_rich
    if do_freeze:
        frozen_path = os.path.join(OUT_DIR, "meaning_sense_signatures_%s.npz" % ("smoke" if smoke else "full"))
        freeze(sig_rich, frozen_path, {"level": level, "margin": margin, "dim": EMB_DIM,
                                       "n": len(sig_rich), "source": "wordnet+syntagnet+conceptnet",
                                       "builder": "exp_knowledge_factory_meaning_store_v1"})
        sig_frozen = load_frozen(frozen_path)

    ok_gloss = a_s(recs, test, sig_gloss, Ctx_test, gamma=1.0, topk=None)
    ok_rich = a_s(recs, test, sig_rich, Ctx_test, gamma=gamma, topk=topk)
    ok_frozen = a_s(recs, test, sig_frozen, Ctx_test, gamma=gamma, topk=topk)
    ok_shuf = a_s(recs, test, sig_shuf, Ctx_test, gamma=gamma, topk=topk)

    n = min(len(ok_gloss), len(ok_rich), len(ok_frozen), len(ok_shuf))
    res = {"n_test": int(n), "level": level, "margin": margin, "gamma": gamma, "topk": topk,
           "a_s": {"gloss": round(float(ok_gloss.mean()), 4), "rich_onfly": round(float(ok_rich.mean()), 4),
                   "rich_FROZEN": round(float(ok_frozen.mean()), 4), "shuffled_twin": round(float(ok_shuf.mean()), 4)},
           "FROZEN_vs_gloss": G1._paired(ok_frozen[:n], ok_gloss[:n], 950),
           "FROZEN_vs_shuffled": G1._paired(ok_frozen[:n], ok_shuf[:n], 951),
           "freeze_fidelity_delta": round(float(ok_frozen.mean() - ok_rich.mean()), 5),
           "frozen_path": frozen_path}

    # MFS no-regression guard: blended readout (freq prior + diagnostic) on the FULL (all-sense) test
    # population, where MFS is a REAL floor -- subordinate-only makes MFS trivially 0 (the parent's guard
    # was 0.695 blended >= 0.683 MFS on all senses).
    Ctx_all = G1.precompute_ctx(recs, test_all, mat, w2i)
    ok_bl_g, mfs = G1.blended_overall(recs, test_all, sig_gloss, Ctx_all, mat, w2i, lam=1.0, T=0.5)
    ok_bl_f, _ = G1.blended_overall(recs, test_all, sig_frozen, Ctx_all, mat, w2i, lam=1.0, T=0.5)
    res["MFS_guard"] = {"population": "all_senses_odd_docs", "n": int(len(test_all)),
                        "mfs": round(float(mfs.mean()), 4),
                        "blended_gloss": round(float(ok_bl_g.mean()), 4),
                        "blended_frozen": round(float(ok_bl_f.mean()), 4),
                        "no_regression_vs_mfs": bool(ok_bl_f.mean() >= mfs.mean()),
                        "no_regression_vs_gloss": bool(ok_bl_f.mean() >= ok_bl_g.mean() - 0.005)}
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["headline"] = ("MEANING STORE frozen a_s=%.4f vs gloss %.4f (sep=%s ci=%s) | shuffled-twin %.4f (loses=%s) "
                       "| freeze-fidelity d=%.5f | MFS no-regress=%s"
                       % (res["a_s"]["rich_FROZEN"], res["a_s"]["gloss"], res["FROZEN_vs_gloss"]["sep"],
                          res["FROZEN_vs_gloss"]["ci"], res["a_s"]["shuffled_twin"],
                          res["FROZEN_vs_shuffled"]["sep"], res["freeze_fidelity_delta"],
                          res["MFS_guard"]["no_regression_vs_mfs"]))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % ("smoke" if smoke else "full")), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_meaning_store_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def optimize(level=3, smoke=False,
             margins=(None, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2),
             gammas=(1.0, 1.5, 2.0), topks=(None, 5, 10)):
    """THE TRIMMING / OPTIMIZATION TOOL. Tune the discriminative trim margin + the P9 precision-weighting
    (gamma/topk) on the DEV split (even docs), LOCK the best config, report on the held-out TEST split (odd docs)
    with the frozen asset, the shuffled-knowledge twin, and the MFS guard. Honest held-out tuning: TEST is never
    used to choose the config."""
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    w2i, mat, recs, dev, test, test_all = _load_eval()
    if smoke:
        dev = dev[:400]; test = test[:400]; test_all = test_all[:800]
        margins = (None, 0.0, 0.1); gammas = (1.0, 2.0); topks = (None, 10)
    cand = set()
    for i in dev + test + test_all:
        cand.update(recs[i]["tn"])
    Ctx_dev = G1.precompute_ctx(recs, dev, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test, mat, w2i)
    prep = prep_bags(cand, mat, w2i, level)
    prep0 = prep_bags(cand, mat, w2i, 0)
    sig_gloss = sigs_at(prep0, mat, w2i, None)
    ok_gloss_dev = a_s(recs, dev, sig_gloss, Ctx_dev)
    print("[opt] dev=%d test=%d cand=%d gloss_dev=%.4f (%.0fs)"
          % (len(dev), len(test), len(cand), ok_gloss_dev.mean(), time.time() - t0), flush=True)

    # 1) sweep MARGIN on DEV at gamma=1, topk=None
    sigs_by_margin = {}; dev_by_margin = {}
    for m in margins:
        sig = sigs_at(prep, mat, w2i, m); sigs_by_margin[m] = sig
        d = float(a_s(recs, dev, sig, Ctx_dev).mean()); dev_by_margin[m] = d
        print("[opt] margin=%-5s dev_a_s=%.4f (%.0fs)" % (str(m), d, time.time() - t0), flush=True)
    best_m = max(margins, key=lambda m: dev_by_margin[m])

    # 2) sweep P9 (gamma, topk) on DEV at best margin
    p9 = {}
    for g in gammas:
        for k in topks:
            d = float(a_s(recs, dev, sigs_by_margin[best_m], Ctx_dev, gamma=g, topk=k).mean())
            p9[(g, k)] = d
    best_g, best_k = max(p9, key=lambda gk: p9[gk])
    print("[opt] LOCKED on DEV: margin=%s gamma=%s topk=%s (dev_a_s=%.4f)"
          % (str(best_m), best_g, best_k, p9[(best_g, best_k)]), flush=True)

    # 3) report on TEST with the locked config (freeze the locked asset + reload)
    sig_lock = sigs_by_margin[best_m]
    frozen_path = os.path.join(OUT_DIR, "meaning_sense_signatures_optimized_%s.npz" % ("smoke" if smoke else "full"))
    freeze(sig_lock, frozen_path, {"level": level, "margin": best_m, "gamma": best_g, "topk": best_k,
                                   "dim": EMB_DIM, "n": len(sig_lock), "tuned_on": "dev_even_docs",
                                   "source": "wordnet+syntagnet+conceptnet",
                                   "builder": "exp_knowledge_factory_meaning_store_v1.optimize"})
    sig_frozen = load_frozen(frozen_path)
    sig_shuf = sigs_at(prep, mat, w2i, best_m, shuffle_rng=np.random.default_rng(1234))
    ok_gloss = a_s(recs, test, sig_gloss, Ctx_test)
    ok_frozen = a_s(recs, test, sig_frozen, Ctx_test, gamma=best_g, topk=best_k)
    ok_shuf = a_s(recs, test, sig_shuf, Ctx_test, gamma=best_g, topk=best_k)
    # a nontrivial baseline: the UNTUNED store (margin=None, gamma=1) also on TEST, to show tuning's marginal value
    ok_untuned = a_s(recs, test, sigs_by_margin[None], Ctx_test)
    n = min(len(ok_gloss), len(ok_frozen), len(ok_shuf), len(ok_untuned))
    # asset size: mean associates kept
    kept = np.mean([len(trim_associates(prep["assoc"][s], mat, w2i, prep["seed_sig"][s], prep["sib"][s], best_m))
                    for s in list(prep["syns"])[:2000]])
    kept_all = np.mean([len(prep["assoc"][s]) for s in list(prep["syns"])[:2000]])

    # MFS guard on all-sense TEST at the locked config
    Ctx_all = G1.precompute_ctx(recs, test_all, mat, w2i)
    ok_bl_f, mfs = G1.blended_overall(recs, test_all, sig_frozen, Ctx_all, mat, w2i, lam=1.0, T=0.5)

    res = {"level": level, "n_test": int(n), "locked": {"margin": best_m, "gamma": best_g, "topk": best_k},
           "dev_by_margin": {str(k): round(v, 4) for k, v in dev_by_margin.items()},
           "dev_p9": {"%s_%s" % (g, k): round(v, 4) for (g, k), v in p9.items()},
           "test_a_s": {"gloss": round(float(ok_gloss.mean()), 4),
                        "untuned_richNone": round(float(ok_untuned.mean()), 4),
                        "OPTIMIZED_frozen": round(float(ok_frozen.mean()), 4),
                        "shuffled_twin": round(float(ok_shuf.mean()), 4)},
           "OPT_vs_gloss": G1._paired(ok_frozen[:n], ok_gloss[:n], 950),
           "OPT_vs_untuned": G1._paired(ok_frozen[:n], ok_untuned[:n], 952),
           "OPT_vs_shuffled": G1._paired(ok_frozen[:n], ok_shuf[:n], 951),
           "asset_associates_kept": round(float(kept), 1), "asset_associates_all": round(float(kept_all), 1),
           "trim_ratio": round(float(kept / max(1e-9, kept_all)), 3),
           "MFS_guard": {"population": "all_senses_odd_docs", "n": int(len(test_all)),
                         "mfs": round(float(mfs.mean()), 4), "blended_frozen": round(float(ok_bl_f.mean()), 4),
                         "no_regression_vs_mfs": bool(ok_bl_f.mean() >= mfs.mean())},
           "frozen_path": frozen_path, "elapsed_s": round(time.time() - t0, 1)}
    res["headline"] = ("OPTIMIZED meaning store (dev-locked margin=%s gamma=%s topk=%s) test a_s=%.4f vs gloss "
                       "%.4f (+%.4f sep=%s) | vs untuned %.4f (d=%+.4f sep=%s) | shuffled %.4f loses=%s | keep "
                       "%.0f/%.0f assoc (%.0f%%) | MFS no-regress=%s"
                       % (str(best_m), best_g, best_k, res["test_a_s"]["OPTIMIZED_frozen"],
                          res["test_a_s"]["gloss"], res["OPT_vs_gloss"]["delta"], res["OPT_vs_gloss"]["sep"],
                          res["test_a_s"]["untuned_richNone"], res["OPT_vs_untuned"]["delta"],
                          res["OPT_vs_untuned"]["sep"], res["test_a_s"]["shuffled_twin"],
                          res["OPT_vs_shuffled"]["sep"], res["asset_associates_kept"],
                          res["asset_associates_all"], 100 * res["trim_ratio"],
                          res["MFS_guard"]["no_regression_vs_mfs"]))
    with open(os.path.join(OUT_DIR, "metrics_optimize_%s.json" % ("smoke" if smoke else "full")), "w",
              encoding="ascii") as f:
        json.dump({"anchor_name": "knowledge_factory_meaning_store_optimize_v1", "verdict": "MEASURED",
                   "result": res}, f, indent=2, default=str)
    print("[opt] " + res["headline"], flush=True)
    return res


def self_test():
    # trimming keeps a discriminative associate and drops an anti-discriminative one; freeze/reload round-trips.
    rng = np.random.default_rng(0)
    mat = rng.standard_normal((5, EMB_DIM)).astype(np.float32)
    w2i = {"self": 0, "disc": 1, "anti": 2, "sib": 3, "x": 4}
    sig_self = G1._unit(mat[0]); sib = G1._unit(mat[3])
    # make 'disc' align with self, 'anti' align with sib
    mat[1] = mat[0] + 0.01 * rng.standard_normal(EMB_DIM); mat[2] = mat[3] + 0.01 * rng.standard_normal(EMB_DIM)
    kept = trim_associates(["disc", "anti"], mat, w2i, sig_self, [sib], margin=0.05)
    assert "disc" in kept and "anti" not in kept, "trim keeps discriminative, drops anti: %s" % kept
    # freeze/reload
    p = os.path.join(OUT_DIR, "selftest.npz")
    freeze({"a.n.01": sig_self, "b.n.01": None}, p, {"t": 1})
    r = load_frozen(p)
    assert r["b.n.01"] is None and r["a.n.01"] is not None and abs(float(np.linalg.norm(r["a.n.01"])) - 1.0) < 1e-4
    os.remove(p)
    print("SELFTEST PASS (trim discriminative-keep + freeze/reload round-trip)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--level", type=int, default=3)
    ap.add_argument("--margin", type=float, default=None)   # trimming margin; None = no trim
    ap.add_argument("--gamma", type=float, default=1.0)     # P9 precision sharpening
    ap.add_argument("--topk", type=int, default=None)       # P9 hard selective gain
    ap.add_argument("--no-freeze", action="store_true")
    ap.add_argument("--optimize", action="store_true", help="dev-tune trim margin + P9 precision, report on test")
    ap.add_argument("--freeze-full", action="store_true", help="build+freeze the broad-coverage WordNet asset")
    ap.add_argument("--dtype", default="float16")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    if args.freeze_full:
        build_and_freeze_full(level=args.level, dtype=args.dtype, smoke=args.smoke)
        return 0
    if args.optimize:
        optimize(level=args.level, smoke=args.smoke)
        return 0
    run(level=args.level, smoke=args.smoke, margin=args.margin, gamma=args.gamma, topk=args.topk,
        do_freeze=not args.no_freeze)
    return 0


if __name__ == "__main__":
    sys.exit(main())
