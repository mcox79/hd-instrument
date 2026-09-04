"""exp_consolidation_gate_readbind_v1 -- the CONSOLIDATION GATE, built the brain's effective way: READ, then
DISAMBIGUATE-IN-CONTEXT, then BIND the co-occurring context to the SELECTED SENSE (not the lemma), then
cross-situationally CONSOLIDATE. The v1 cell anchored on each sense's definition words (a static proxy for
sense context); THIS cell replicates the brain's actual loop, in which sense-attribution happens ONLINE at
encoding BEFORE storage -- which is why the brain's per-sense knowledge is clean and naive lemma-growth is not.

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

THE BRAIN'S EFFECTIVE MECHANISM (replicated operation-for-operation, all glass-box, pieces we already own):
  1. CONTEXTUAL RETRIEVAL / controlled semantic access (LIFG -> pMTG/ATL; Jefferies 2013, Lambon-Ralph 2017):
     as a word is read, top-down control settles its representation into the CONTEXT-appropriate sense BEFORE
     storage. We replicate this with the WIRED biased-competition readout (hdlab.diagnostic_context_wsd): for
     each occurrence of a target word we pick its sense from the sentence context.                       [PINNED]
  2. HEBBIAN BINDING TO THE SELECTED SENSE (hippocampal DG pattern-separation -> CA3 autoassociation): the
     co-occurring content is bound to the ALREADY-DISAMBIGUATED sense, stored SEPARABLY per sense -- so a rare
     sense's slot never receives the dominant sense's associates. We accumulate cooc[selected_sense][word].  [PINNED]
  3. SLEEP REPLAY -> NEOCORTICAL CONSOLIDATION (CLS; McClelland 1995 + cross-situational SL, Yu & Smith 2007):
     keep associations that RECUR across situations, prune one-offs; PPMI reliability (Ernst&Banks/Friston);
     SHY downscaling = threshold + cap. Cross-situational recurrence SELF-CORRECTS the per-occurrence errors of
     an imperfect online reader -- so a noisy sense-selector still yields clean consolidated knowledge.     [PINNED]
  The exact thresholds (K recurrence, P ppmi, cap) are OUR-INVENTION-under-test -- swept on DEV, frozen on TEST.

WHY THIS BEATS v1 (and the naive baseline): v1 asked "what co-occurs with the sense's DEFINITION words" (indirect,
static). Here we disambiguate the TARGET WORD ITSELF in each context and bind -- the brain's actual solution to
sense-attribution. The RAW-ungated twin (lemma-level growth, no attribution, no consolidation) must still LOSE.

WHERE WE DIFFER FROM THE BRAIN: offline batch (not online replay); text context (no grounded referent -- the
online disambiguation uses distributional context, not a perceived scene); imperfect selector (a_s~0.3 on rare
senses) leaned on cross-situational consolidation to clean. These name the residual to the human-disambiguated
SyntagNet ceiling.

Strict document-disjoint SemCor: DEV = even docs & sub (tune), TEST = odd docs & sub (report, n~2676). Glass-box,
frozen w2v, NO external LLM, NO gold used to build knowledge. ASCII-only. Own data dir.
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
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/_sglite_cache/sglite_syntagnet.pkl
# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
_CACHE = G1._CACHE
SIMPLEWIKI = G1.SIMPLEWIKI
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_gate_readbind_v1")
EMB_DIM = G1.EMB_DIM
_STOP = G1._STOP
_unit = G1._unit
_WNPOS = {"NOUN": "n", "VERB": "v", "N": "n", "V": "v", "n": "n", "v": "v"}


def _read_and_bind(target_senses, gloss_sig, mat, w2i, max_sents, window=0):
    """READ simplewiki; for each occurrence of a target lemma, DISAMBIGUATE in the FULL sentence context
    (biased-competition readout over its candidate-sense gloss vectors) and BIND the co-occurring content words
    to the SELECTED sense. window=0 binds the whole sentence (topical); window>0 binds only the +/-window
    CONTENT-WORD neighbours of the target occurrence (a syntagmatic-tightness proxy for dependency-linked pairs
    -- the SyntagNet-construction ingredient). target_senses: {(lemma,pos_wn):[synsets]}. Cached per window."""
    from nltk.corpus import wordnet as wn
    key = "%d_w%d_%d" % (max_sents, window, (hash(frozenset(target_senses)) & 0xffffffff))
    cache = os.path.join(_CACHE, "consol_readbind_%s.pkl" % key)
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)

    # precompute candidate-sense gloss matrices per (lemma,pos)
    lem_G = {}
    for (lemma, pos), tn in target_senses.items():
        gs = [gloss_sig.get(s) for s in tn]
        if any(g is not None for g in gs):
            G = np.stack([g if g is not None else np.zeros(EMB_DIM, np.float32) for g in gs])
            lem_G[(lemma, pos)] = (tn, G, np.array([g is not None for g in gs]))
    lemmas_by_surface_pos = defaultdict(list)   # lemma string -> list of pos present as target
    for (lemma, pos) in lem_G:
        lemmas_by_surface_pos[lemma].append(pos)
    target_lemma_strings = set(lemmas_by_surface_pos)
    morphy_cache = {}

    def lemmatize(w):
        if w in morphy_cache:
            return morphy_cache[w]
        out = []
        for pos in ("n", "v"):
            try:
                m = wn.morphy(w, pos)
            except Exception:
                m = None
            if m and m in target_lemma_strings and pos in lemmas_by_surface_pos.get(m, ()):
                out.append((m, pos))
        morphy_cache[w] = out
        return out

    cooc = defaultdict(Counter)   # synset -> Counter(context word -> #sentences bound)
    sel = Counter()               # synset -> #sentences it was selected
    uni = Counter(); nS = 0; nbind = 0; t0 = time.time()
    with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            toks = [w for w in "".join(c.lower() if (c.isalpha() or c == " ") else " " for c in line).split()
                    if len(w) >= 3 and w not in _STOP and w in w2i]
            if len(toks) < 4:
                continue
            cs = set(toks)
            for x in cs:
                uni[x] += 1
            # target-lemma occurrences WITH POSITION (for windowed binding)
            targets_here = []
            for j, w in enumerate(toks):
                for (lem, pos) in lemmatize(w):
                    targets_here.append((j, lem, pos))
            for (j, lem, pos) in targets_here:
                tn, G, present = lem_G[(lem, pos)]
                # DISAMBIGUATE with the FULL sentence context (exclude only the target position)
                rows = [_unit(mat[w2i[toks[k]]]) for k in range(len(toks)) if k != j]
                if not rows:
                    continue
                C = np.stack(rows)
                scv = diagnostic_context_scores(C, G)
                scv = np.where(present, scv, -9.0)
                ssyn = tn[int(np.argmax(scv))]
                sel[ssyn] += 1
                # BIND: whole sentence (window=0) or the +/-window content-word neighbours (syntagmatic)
                if window > 0:
                    lo = max(0, j - window); hi = min(len(toks), j + window + 1)
                    bind = set(toks[k] for k in range(lo, hi) if k != j)
                else:
                    bind = set(toks[k] for k in range(len(toks)) if k != j)
                cooc[ssyn].update(bind)
                nbind += 1
            nS += 1
            if max_sents and nS >= max_sents:
                break
            if nS % 500000 == 0:
                print("[readbind] %d sents, %d binds, %d senses (%.0fs)"
                      % (nS, nbind, len(cooc), time.time() - t0), flush=True)
    out = {"cooc": {k: dict(v) for k, v in cooc.items()}, "sel": dict(sel), "uni": dict(uni),
           "n_sents": nS, "n_binds": nbind}
    with open(cache, "wb") as f:
        pickle.dump(out, f)
    print("[readbind] DONE %d sents, %d binds, %d senses, %.0fs" % (nS, nbind, len(cooc), time.time() - t0),
          flush=True)
    return out


def sense_assocs(syn, store):
    """Per-sense candidate associates from the read-and-bind store: {w: (recur=#sentences bound, ppmi)}."""
    cooc = store["cooc"].get(syn, {}); N = store["n_sents"]; uni = store["uni"]
    ns = store["sel"].get(syn, 0)
    agg = {}
    for w, c in cooc.items():
        agg[w] = (1, c, G1._ppmi(c, ns, uni.get(w, 0), N))   # (support placeholder, recur, ppmi)
    return agg


def consolidate_sense(agg, mat, w2i, sig_self, sib_sigs, cfg):
    """recurrence >= K, ppmi >= P, optional schema-discrimination, cap. (Multiseed N/A: attribution is direct.)"""
    drop = cfg.get("drop", set())
    K, P, margin, cap = cfg["K"], cfg["P"], cfg["margin"], cfg["cap"]
    words, scores = [], []
    for w, (sup, rc, pp) in agg.items():
        if w not in w2i:
            continue
        if "recur" not in drop and rc < K:
            continue
        if "ppmi" not in drop and pp < P:
            continue
        words.append(w); scores.append(pp * rc)
    if not words:
        return []
    if "schema" not in drop and sig_self is not None:
        V = mat[[w2i[w] for w in words]]
        V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        self_s = V @ sig_self
        sib_s = (V @ np.stack(sib_sigs).T).max(axis=1) if sib_sigs else np.full(len(words), -1.0)
        keep = (self_s - sib_s) >= margin
        words = [w for w, k in zip(words, keep) if k]; scores = [s for s, k in zip(scores, keep) if k]
        if not words:
            return []
    order = np.argsort(-np.asarray(scores))[:cap]
    return [words[i] for i in order]


def run(max_sents, cap, cfg0, smoke=False, readout="mean", topk=3, window=0):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0])
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    all_test_idx = list(np.where(doc % 2 == 1)[0])
    if smoke:
        dev_idx = dev_idx[:200]; test_idx = test_idx[:200]; all_test_idx = all_test_idx[:400]
    print("[run] dev-sub=%d test-sub=%d all-test=%d (%.0fs)"
          % (len(dev_idx), len(test_idx), len(all_test_idx), time.time() - t0), flush=True)

    cand = set()
    target_senses = {}
    for i in dev_idx + test_idx + all_test_idx:
        r = recs[i]; cand.update(r["tn"])
        pos = _WNPOS.get(r["pos"], "n")
        target_senses[(r["lemma"].lower(), pos)] = r["tn"]
    all_syn = set(cand)
    sib_by_syn = {s: G1._siblings(s) for s in cand}
    for sibs in sib_by_syn.values():
        all_syn.update(sibs)
    seeds_by_syn = {s: G1._seed_words(s, w2i) for s in all_syn}
    gloss_sig = {s: G1._sigvec(mat, w2i, seeds_by_syn[s]) for s in all_syn}

    print("[run] %d cand synsets, %d target (lemma,pos); read-and-bind over <=%d sents ... (%.0fs)"
          % (len(cand), len(target_senses), max_sents, time.time() - t0), flush=True)
    store = _read_and_bind(target_senses, gloss_sig, mat, w2i, max_sents, window=window)
    agg_by_syn = {s: sense_assocs(s, store) for s in cand}

    Ctx_dev = G1.precompute_ctx(recs, dev_idx, mat, w2i)
    Ctx_test = G1.precompute_ctx(recs, test_idx, mat, w2i)
    Ctx_all = G1.precompute_ctx(recs, all_test_idx, mat, w2i)

    def build_assoc(cfg):
        return {s: consolidate_sense(agg_by_syn[s], mat, w2i, gloss_sig[s],
                                     [gloss_sig[x] for x in sib_by_syn[s] if gloss_sig[x] is not None], cfg)
                for s in cand}

    def a_s(idxs, Ctx, assoc):
        mean_sig = G1.sigs_for(cand, seeds_by_syn, assoc, mat, w2i)
        if readout == "topk":
            sw = {s: list(seeds_by_syn[s]) + list(assoc.get(s, [])) for s in cand}
            return G1.score_topk(recs, idxs, sw, mean_sig, Ctx, mat, w2i, k=topk)
        return G1.score(recs, idxs, mean_sig, Ctx)

    gloss_assoc = {s: [] for s in cand}
    gloss_dev = a_s(dev_idx, Ctx_dev, gloss_assoc); gloss_test = a_s(test_idx, Ctx_test, gloss_assoc)

    configs = {
        "recurrence_only":  dict(cfg0, cap=cap, drop={"schema", "ppmi"}),
        "recur+ppmi":       dict(cfg0, cap=cap, drop={"schema"}),
        "recur+schema":     dict(cfg0, cap=cap, drop={"ppmi"}),
        "full_gate":        dict(cfg0, cap=cap, drop=set()),
    }
    sweep = {}
    for name, cfg in configs.items():
        assoc = build_assoc(cfg)
        dv = a_s(dev_idx, Ctx_dev, assoc)
        sweep[name] = {"dev": round(float(dv.mean()), 4),
                       "mean_assoc": round(float(np.mean([len(assoc[s]) for s in cand])), 2)}
        print("[sweep] %-18s dev a_s=%.4f assoc/sense=%.1f (%.0fs)"
              % (name, sweep[name]["dev"], sweep[name]["mean_assoc"], time.time() - t0), flush=True)
    best_name = max(sweep, key=lambda k: sweep[k]["dev"]); best_cfg = configs[best_name]
    print("[sweep] BEST-ON-DEV = %s (%.4f)" % (best_name, sweep[best_name]["dev"]), flush=True)

    cons_assoc = build_assoc(best_cfg)
    cons_test = a_s(test_idx, Ctx_test, cons_assoc)
    # RAW-ungated twin: bind-all, NO consolidation (every associate, cap by raw recurrence count)
    raw_assoc = {s: [w for w, _ in sorted(agg_by_syn[s].items(), key=lambda kv: -kv[1][1])[:cap]] for s in cand}
    raw_test = a_s(test_idx, Ctx_test, raw_assoc)
    syntag_assoc = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    syntag_test = a_s(test_idx, Ctx_test, syntag_assoc)
    rng = np.random.default_rng(1234); cl = sorted(cand); perm = list(cl); rng.shuffle(perm)
    shuf = dict(zip(cl, perm)); shuf_assoc = {s: cons_assoc[shuf[s]] for s in cand}
    shuf_test = a_s(test_idx, Ctx_test, shuf_assoc)

    gl_sig = G1.sigs_for(cand, seeds_by_syn, gloss_assoc, mat, w2i)
    cn_sig = G1.sigs_for(cand, seeds_by_syn, cons_assoc, mat, w2i)
    ov_gloss, mfs = G1.blended_overall(recs, all_test_idx, gl_sig, Ctx_all, mat, w2i, lam=1.0, T=0.1)
    ov_cons, _ = G1.blended_overall(recs, all_test_idx, cn_sig, Ctx_all, mat, w2i, lam=1.0, T=0.1)

    n = min(len(gloss_test), len(cons_test), len(raw_test))
    res = {
        "n_dev_sub": len(dev_idx), "n_test_sub": len(test_idx), "n_all_test": len(all_test_idx),
        "n_sents": store["n_sents"], "n_binds": store["n_binds"], "cap": cap,
        "cfg0": {k: v for k, v in cfg0.items() if k != "drop"}, "best_config_on_dev": best_name, "sweep": sweep,
        "a_s_test": {"gloss": round(float(gloss_test.mean()), 4), "RAW": round(float(raw_test.mean()), 4),
                     "CONSOLIDATED": round(float(cons_test.mean()), 4),
                     "twin_shuffled": round(float(shuf_test.mean()), 4),
                     "CEILING_syntagnet": round(float(syntag_test.mean()), 4)},
        "CONSOLIDATED_vs_gloss": G1._paired(cons_test[:n], gloss_test[:n], 201),
        "RAW_vs_gloss": G1._paired(raw_test[:n], gloss_test[:n], 202),
        "CONSOLIDATED_vs_RAW": G1._paired(cons_test[:n], raw_test[:n], 203),
        "CONSOLIDATED_vs_shuffled": G1._paired(cons_test[:len(shuf_test)], shuf_test, 204),
        "syntagnet_ceiling_gap": G1._paired(syntag_test[:n], cons_test[:n], 206),
        "MFS_guard": {"mfs_floor": round(float(mfs.mean()), 4),
                      "overall_gloss_blend": round(float(ov_gloss.mean()), 4),
                      "overall_CONS_blend": round(float(ov_cons.mean()), 4),
                      "CONS_vs_MFS": G1._paired(ov_cons, mfs, 207),
                      "CONS_vs_gloss_blend": G1._paired(ov_cons, ov_gloss, 208)},
    }
    res["headline"] = (
        "READ-BIND CONSOLIDATION [%s] | gloss=%.3f RAW=%.3f CONS=%.3f | CONS>gloss sep=%s null_p95=%s | "
        "RAW<gloss=%s | CONS>RAW sep=%s | shuf lose=%s | ceiling=%.3f gap=%+.3f | MFS %.3f ovCONS %.3f >=MFS=%s"
        % (best_name, res["a_s_test"]["gloss"], res["a_s_test"]["RAW"], res["a_s_test"]["CONSOLIDATED"],
           res["CONSOLIDATED_vs_gloss"]["sep"], res["CONSOLIDATED_vs_gloss"]["null_p95"],
           (res["RAW_vs_gloss"]["delta"] < 0), res["CONSOLIDATED_vs_RAW"]["sep"],
           res["CONSOLIDATED_vs_shuffled"]["sep"], res["a_s_test"]["CEILING_syntagnet"],
           res["syntagnet_ceiling_gap"]["delta"], res["MFS_guard"]["mfs_floor"],
           res["MFS_guard"]["overall_CONS_blend"], res["MFS_guard"]["CONS_vs_MFS"]["sep"]))
    res["readout"] = readout; res["window"] = window
    res["elapsed_s"] = round(time.time() - t0, 1)
    tag = ("smoke_" if smoke else "") + ("%s_w%d_s%d_cap%d" % (readout, window, store["n_sents"], cap))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_gate_readbind_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    assert _WNPOS.get("NOUN") == "n"
    agg = {"river": (1, 8, 2.4), "the": (1, 300, 0.0)}
    w2i = {"river": 1, "the": 2}
    out = consolidate_sense(agg, None, w2i, None, [], {"K": 3, "P": 0.5, "margin": 0.0, "cap": 5,
                                                       "drop": {"schema"}})
    assert "river" in out and "the" not in out, "ppmi/recur gate must drop the frequent-noise word (ppmi=0)"
    print("SELFTEST PASS", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-sents", type=int, default=0)   # 0 == ALL simplewiki
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--K", type=int, default=3)
    ap.add_argument("--P", type=float, default=0.5)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--readout", default="mean", choices=["mean", "topk"])
    ap.add_argument("--topk", type=int, default=3)
    ap.add_argument("--window", type=int, default=0)   # 0=whole sentence; >0 = +/-window content-word neighbours
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    cfg0 = {"K": args.K, "P": args.P, "margin": args.margin, "cap": args.cap, "drop": set()}
    ms = 60000 if args.smoke else args.max_sents
    run(ms, args.cap, cfg0, smoke=args.smoke, readout=args.readout, topk=args.topk, window=args.window)
    return 0


if __name__ == "__main__":
    sys.exit(main())
