"""exp_consolidation_gate_v1 -- the CONTROLLED knowledge-growth / CONSOLIDATION GATE for the learner.

PROBLEM: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner

WHAT WE ARE TESTING. Knowledge growth is the biggest lever on rare-sense selection (gloss->rich a_s +0.081
CI-sep, parent build_sg_lite...), BUT growing it the naive way REGRESSES the score: on the winning
biased-competition diagnostic readout the parent measured gloss 0.239 -> +raw-organic-w2v-NN 0.301 (-0.022,
reproduced first-hand this session), the same as the graph organ's raw learn_from_text co-occurrence
(0.274->0.267). Only CONSOLIDATED (SyntagNet-quality) knowledge helps (+SyntagNet 0.310). So the learner can
grow this knowledge from reading ONLY through a consolidation/quality gate. THIS cell builds that gate and proves
CONSOLIDATED reading-derived associations RAISE a_s over gloss-only while the RAW-ungated twin LOSES (regresses).

HOW THE BRAIN DOES THIS (each gate component is a replicated neural operation; PINNED unless marked):
  1. HIPPOCAMPAL PATTERN SEPARATION (DG/CA3): reading episodes stored SEPARABLY, not superposed -> we keep a
     SEPARABLE per-seed co-occurrence store (the ROUTE-B _ctx_counts design; here rebuilt offline from the same
     text the reader read, simplewiki, so the counts are not blurred).                                  [PINNED]
  2. NEOCORTICAL SLOW CONSOLIDATION (Complementary Learning Systems; McClelland/McNaughton/O'Reilly 1995) +
     CROSS-SITUATIONAL STATISTICAL LEARNING (Yu & Smith 2007): keep only regularities that RECUR across many
     situations; discard one-off co-occurrences -> RECURRENCE gate (co-occurs with a seed across >= K sentences)
     and MULTI-SEED CONVERGENCE (the associate recurs across >= M of the sense's own defining words, so it is a
     property of the SENSE-cluster, not one ambiguous word -- cross-situational sense attribution).      [PINNED]
  3. SCHEMA-GATED CONSOLIDATION (Tse et al. 2007): information CONSISTENT with an existing schema consolidates
     and integrates; inconsistent noise does not -> the sense's WordNet gloss/hypernym IS its schema; admit an
     associate only if it DISCRIMINATES the sense from its lexical competitors (biased competition at
     consolidation time: cos(assoc, sense-schema) - max cos(assoc, sibling-schema) > margin).            [PINNED]
  4. RELIABILITY/PRECISION WEIGHTING (Ernst & Banks 2002; Feldman & Friston 2010; Competition Model cue validity
     = availability x reliability): downweight unreliable, globally-frequent cues -> PPMI confidence gate.  [PINNED]
  5. SYNAPTIC DOWNSCALING / SHY (Tononi & Cirelli): sleep prunes weak traces, preserves the strong -> admission
     threshold + dedup + per-sense cap.                                                                   [PINNED]
  The exact thresholds (K, M, PPMI, margin, cap) are OUR-INVENTION-under-test -- swept ON THE DEV SPLIT (even
  docs), frozen, then reported on the TEST split (odd docs). Never adopted from a constraint we do not share.

WHERE WE DIFFER FROM THE BRAIN (named, not hidden):
  * OFFLINE BATCH vs ONLINE REPLAY: the brain consolidates online during sleep replay; we run one offline pass
    over the accumulated store (admissible: an offline static consolidation asset is allowed). Same computation.
  * NO GROUNDING: brain associations are sensorimotor-grounded (ATL hub spokes); ours are text-distributional
    only -- the known ceiling deviation (parent: residual to human is grounding+inference).
  * SENSE ATTRIBUTION: the brain has the referent present (situated reference) to bind an episode to a sense; we
    INFER the sense from textual context via the schema gate -- the central fidelity gap vs human-disambiguated
    SyntagNet, quantified here as the residual to the SyntagNet ceiling.

READOUT: scored through the WIRED biased-competition organ hdlab.diagnostic_context_wsd (the parent's promoted
a_s instrument). Strict document-disjoint SemCor. DEV = even docs & subordinate (tune the gate); TEST = odd docs
& subordinate (report; n~2676, the parent's population). RAW-ungated twin + shuffled-sense twin must LOSE.
Glass-box, frozen w2v, NO external LLM, NO gold used to build knowledge. ASCII-only. Own data dir.
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

from hdlab.diagnostic_context_wsd import diagnostic_context_scores, diagnostic_query  # WIRED a_s readout

# KB_REFERENT: data/_sglite_cache/sglite_w2v_full.pkl
# KB_REFERENT: data/_sglite_cache/sglite_semcorrole_f30.pkl
# KB_REFERENT: data/_sglite_cache/sglite_syntagnet.pkl
# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
_CACHE = os.path.join(_REPO, "data", "_sglite_cache")
SIMPLEWIKI = os.path.join(_REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
OUT_DIR = os.path.join(_REPO, "data", "exp_consolidation_gate_v1")

EMB_DIM = 200
_ZERO = np.zeros(EMB_DIM, np.float32)
_STOP = set(
    "a an the this that these those of to in on at by for with from into over under and or but if then else "
    "is are was were be been being am do does did done has have had having will would shall should can could "
    "may might must not no nor as so than too very it its he she they them his her their him you your i me my "
    "we us our who whom which what when where why how all any both each few more most other some such only own "
    "same up down out off again further here there also one two first new used many make made like get".split())


# -------------------------------------------------------------------------------------------------
# stats: paired bootstrap CI (verbatim from exp_topdown_situation_sense_selector_v1._boot) + sign-flip null p95
# -------------------------------------------------------------------------------------------------
def _boot(a, b, seed, reps=2000):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b
    if len(d) < 20:
        return float(d.mean()), float("nan"), float("nan"), float("nan")
    idx = np.random.default_rng(seed).integers(0, len(d), size=(reps, len(d)))
    m = d[idx].mean(1)
    lo = float(np.percentile(m, 2.5)); hi = float(np.percentile(m, 97.5))
    return float(d.mean()), lo, hi, float((hi - lo) / 2.0)


def _null_p95(a, b, seed, reps=2000):
    """Sign-flip permutation null: 95th pct of |mean(+/-d)| when the pairing carries no signal."""
    d = np.asarray(a, float) - np.asarray(b, float)
    if len(d) < 20:
        return float("nan")
    rng = np.random.default_rng(seed + 1)
    signs = rng.integers(0, 2, size=(reps, len(d))) * 2 - 1
    return float(np.percentile(np.abs((signs * d).mean(1)), 95))


def _paired(a, b, seed=7):
    d, lo, hi, hw = _boot(a, b, seed)
    p95 = _null_p95(a, b, seed)
    return {"delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)],
            "ci_hw": None if hw != hw else round(hw, 4), "null_p95": None if p95 != p95 else round(p95, 4),
            "a": round(float(np.mean(a)), 4), "b": round(float(np.mean(b)), 4), "n": int(len(a)),
            "sep": bool(lo > 0), "beats_null": bool(d > p95) if p95 == p95 else None}


# -------------------------------------------------------------------------------------------------
# WordNet schema (seeds) + lexical competitors
# -------------------------------------------------------------------------------------------------
def _toks(s):
    out = []
    for tok in s.replace(";", " ").replace(",", " ").split():
        t = "".join(c for c in tok.lower() if c.isalpha())
        if len(t) >= 3 and t not in _STOP:
            out.append(t)
    return out


_SEEDCACHE = {}


def _seed_words(syn_name, w2i):
    if syn_name in _SEEDCACHE:
        return _SEEDCACHE[syn_name]
    from nltk.corpus import wordnet as wn
    w = []
    try:
        s = wn.synset(syn_name)
        w += _toks(s.definition())
        for ex in s.examples():
            w += _toks(ex)
        for ln in s.lemma_names():
            w.append(ln.lower().split("_")[0])
        for h in s.hypernyms():
            for ln in h.lemma_names():
                w.append(ln.lower().split("_")[0])
    except Exception:
        pass
    seen, out = set(), []
    for x in w:
        if len(x) >= 3 and x not in _STOP and x in w2i and x not in seen:
            seen.add(x); out.append(x)
    _SEEDCACHE[syn_name] = out
    return out


def _siblings(syn_name):
    from nltk.corpus import wordnet as wn
    try:
        s = wn.synset(syn_name)
        lemma = s.lemmas()[0].name(); pos = s.pos()
        return [t.name() for t in wn.synsets(lemma, pos=pos) if t.name() != syn_name]
    except Exception:
        return []


def _unit(v):
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else v


def _sigvec(mat, w2i, words):
    vs = [mat[w2i[x]] for x in words if x in w2i]
    return _unit(np.mean(vs, 0)) if vs else None


# -------------------------------------------------------------------------------------------------
# the reader's own reading: separable first-order syntagmatic co-occurrence over simplewiki
# -------------------------------------------------------------------------------------------------
def build_cooc(seed_set, max_sents, w2i):
    key = "%d_%d" % (max_sents, (hash(frozenset(seed_set)) & 0xffffffff))
    cache = os.path.join(_CACHE, "consol_cooc_%s.pkl" % key)
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)
    cooc = defaultdict(Counter); uni = Counter(); nS = 0; t0 = time.time()
    with open(SIMPLEWIKI, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            toks = [w for w in "".join(c.lower() if (c.isalpha() or c == " ") else " " for c in line).split()
                    if len(w) >= 3 and w not in _STOP and w in w2i]
            if len(toks) < 3:
                continue
            cs = set(toks)
            for x in cs:
                uni[x] += 1
            for s in (cs & seed_set):
                cooc[s].update(cs - {s})
            nS += 1
            if max_sents and nS >= max_sents:
                break
            if nS % 1000000 == 0:
                print("[cooc] %d sents, %d seeds (%.0fs)" % (nS, len(cooc), time.time() - t0), flush=True)
    out = {"cooc": {k: dict(v) for k, v in cooc.items()}, "uni": dict(uni), "n_sents": nS}
    with open(cache, "wb") as f:
        pickle.dump(out, f)
    print("[cooc] DONE %d sents, %d seeds, %.0fs" % (nS, len(cooc), time.time() - t0), flush=True)
    return out


def _ppmi(cnt_sw, uni_s, uni_w, N):
    if cnt_sw <= 0 or uni_s <= 0 or uni_w <= 0:
        return 0.0
    v = np.log((cnt_sw / N) / ((uni_s / N) * (uni_w / N)))
    return float(v) if v > 0 else 0.0


def candidate_assocs(seeds, store):
    """Aggregate reading-derived candidate associates across a sense's seed words.
    Returns {w: (support=#seeds, recur=max sentence-count, ppmi=max PPMI)}."""
    cooc = store["cooc"]; uni = store["uni"]; N = store["n_sents"]
    agg = {}; seedset = set(seeds)
    for s in seeds:
        nbrs = cooc.get(s)
        if not nbrs:
            continue
        us = uni.get(s, 0)
        for w, c in nbrs.items():
            if w in seedset:
                continue
            pm = _ppmi(c, us, uni.get(w, 0), N)
            if w in agg:
                sup, rc, pp = agg[w]; agg[w] = (sup + 1, max(rc, c), max(pp, pm))
            else:
                agg[w] = (1, c, pm)
    return agg


def consolidate(agg, mat, w2i, sig_self, sib_sigs, cfg):
    """Full gate (vectorized schema step). cfg: K recur, M multiseed, P ppmi, margin schema, cap; drop=set()."""
    drop = cfg.get("drop", set())
    K, M, P, margin, cap = cfg["K"], cfg["M"], cfg["P"], cfg["margin"], cfg["cap"]
    words, scores = [], []
    for w, (sup, rc, pp) in agg.items():
        if w not in w2i:
            continue
        if "recur" not in drop and rc < K:
            continue
        if "multiseed" not in drop and sup < M:
            continue
        if "ppmi" not in drop and pp < P:
            continue
        words.append(w); scores.append(pp * (1.0 + sup))
    if not words:
        return []
    if "schema" not in drop and sig_self is not None:
        V = mat[[w2i[w] for w in words]]
        V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-9)
        self_s = V @ sig_self
        if sib_sigs:
            S = np.stack(sib_sigs)
            sib_s = (V @ S.T).max(axis=1)
        else:
            sib_s = np.full(len(words), -1.0)
        keep = (self_s - sib_s) >= margin
        words = [w for w, k in zip(words, keep) if k]
        scores = [sc for sc, k in zip(scores, keep) if k]
        if not words:
            return []
    order = np.argsort(-np.asarray(scores))[:cap]
    return [words[i] for i in order]


def raw_assocs(agg, cap):
    """RAW-ungated twin: top-cap by raw recurrence count only (no ppmi/multiseed/schema)."""
    return [w for w, _ in sorted(agg.items(), key=lambda kv: -kv[1][1])[:cap]]


# -------------------------------------------------------------------------------------------------
# readout + scoring (context matrices precomputed once, reused across arms)
# -------------------------------------------------------------------------------------------------
def precompute_ctx(recs, idxs, mat, w2i):
    Ctx = {}
    for i in idxs:
        rows = [_unit(mat[w2i[x]]) for x in recs[i]["ctx"] if x in w2i]
        Ctx[i] = np.stack(rows) if rows else None
    return Ctx


def score(recs, idxs, sig_by_syn, Ctx):
    ok = []
    for i in idxs:
        C = Ctx[i]
        if C is None:
            continue
        tn = recs[i]["tn"]
        G = np.stack([sig_by_syn.get(s) if sig_by_syn.get(s) is not None else _ZERO for s in tn])
        if not np.any(G):
            continue
        sc = diagnostic_context_scores(C, G)
        ok.append(int(tn[int(np.argmax(sc))] == recs[i]["gold"]))
    return np.array(ok, float)


def sigs_for(cand, seeds_by_syn, assoc_by_syn, mat, w2i):
    return {s: _sigvec(mat, w2i, list(seeds_by_syn[s]) + list(assoc_by_syn.get(s, []))) for s in cand}


def score_topk(recs, idxs, sigwords_by_syn, mean_sig_by_syn, Ctx, mat, w2i, k=3):
    """EXEMPLAR / best-match key readout (brain-faithful biased competition, not prototype-averaging): the query
    is still the diagnostic-weighted context, but a sense is scored by the mean of its TOP-K best-matching
    INDIVIDUAL signature words (gloss + admitted associates) -- so a clean associate can WIN for its
    discriminative context without a mean-pool diluting it, and a noise word rarely becomes a top-k match.
    The parent measured top-k key > mean-pool key (+0.031); this makes admitted knowledge non-diluting."""
    ok = []
    for i in idxs:
        C = Ctx[i]
        if C is None:
            continue
        tn = recs[i]["tn"]
        Gm = np.stack([mean_sig_by_syn.get(s) if mean_sig_by_syn.get(s) is not None else _ZERO for s in tn])
        if not np.any(Gm):
            continue
        q = diagnostic_query(C, Gm)
        sc = []
        for s in tn:
            iw = [w2i[w] for w in sigwords_by_syn.get(s, ()) if w in w2i]
            if not iw:
                sc.append(-9.0); continue
            W = mat[iw]; W = W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-9)
            sims = W @ q
            kk = min(k, len(sims))
            sc.append(float(np.sort(sims)[-kk:].mean()))
        ok.append(int(tn[int(np.argmax(sc))] == recs[i]["gold"]))
    return np.array(ok, float)


# -------------------------------------------------------------------------------------------------
# MFS no-regression guard (blended overall readout on ALL test items)
# -------------------------------------------------------------------------------------------------
def blended_overall(recs, idxs, sig_by_syn, Ctx_all, mat, w2i, lam, T):
    """log P_freq + lam*log softmax(diag/T); argmax over candidates. Returns per-item ok vs gold, and MFS ok."""
    ok, mfs = [], []
    for i in idxs:
        r = recs[i]; tn = r["tn"]; prior = np.asarray(r["prior"], float)
        pf = prior + 0.1; pf = pf / pf.sum()
        mfs.append(int(r["gi"] == r["pidx"]))
        C = Ctx_all.get(i)
        if C is None:
            ok.append(int(int(np.argmax(pf)) == r["gi"])); continue
        G = np.stack([sig_by_syn.get(s) if sig_by_syn.get(s) is not None else _ZERO for s in tn])
        sc = diagnostic_context_scores(C, G)
        e = np.exp((sc - sc.max()) / T); pd = e / e.sum()
        fin = np.log(pf) + lam * np.log(pd + 1e-9)
        ok.append(int(int(np.argmax(fin)) == r["gi"]))
    return np.array(ok, float), np.array(mfs, float)


def run(max_sents, cap, cfg0, smoke=False, readout="mean", topk=3):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    emb = pickle.load(open(os.path.join(_CACHE, "sglite_w2v_full.pkl"), "rb"))
    w2i, mat = emb["w2i"], emb["mat"]
    recs = pickle.load(open(os.path.join(_CACHE, "sglite_semcorrole_f30.pkl"), "rb"))
    syntag = pickle.load(open(os.path.join(_CACHE, "sglite_syntagnet.pkl"), "rb"))
    doc = np.array([r["doc_id"] for r in recs]); sub = np.array([r["subordinate"] for r in recs], bool)
    dev_idx = list(np.where((doc % 2 == 0) & sub)[0])
    test_idx = list(np.where((doc % 2 == 1) & sub)[0])
    all_test_idx = list(np.where(doc % 2 == 1)[0])          # for MFS guard (incl dominant)
    if smoke:
        dev_idx = dev_idx[:200]; test_idx = test_idx[:200]; all_test_idx = all_test_idx[:400]
    print("[run] dev-sub=%d  test-sub=%d  all-test=%d  (%.0fs)"
          % (len(dev_idx), len(test_idx), len(all_test_idx), time.time() - t0), flush=True)

    cand = set()
    for i in dev_idx + test_idx + all_test_idx:
        cand.update(recs[i]["tn"])
    seeds_by_syn = {s: _seed_words(s, w2i) for s in cand}
    sib_by_syn = {s: _siblings(s) for s in cand}
    all_syn = set(cand)
    for sibs in sib_by_syn.values():
        all_syn.update(sibs)
    gloss_sig = {s: _sigvec(mat, w2i, _seed_words(s, w2i)) for s in all_syn}

    seed_set = set()
    for s in cand:
        seed_set.update(seeds_by_syn[s])
    print("[run] %d cand synsets, %d seeds; cooc over <=%d sents ... (%.0fs)"
          % (len(cand), len(seed_set), max_sents, time.time() - t0), flush=True)
    store = build_cooc(seed_set, max_sents, w2i)
    agg_by_syn = {s: candidate_assocs(seeds_by_syn[s], store) for s in cand}

    Ctx_dev = precompute_ctx(recs, dev_idx, mat, w2i)
    Ctx_test = precompute_ctx(recs, test_idx, mat, w2i)
    Ctx_all = precompute_ctx(recs, all_test_idx, mat, w2i)

    def build_assoc(cfg):
        return {s: consolidate(agg_by_syn[s], mat, w2i, gloss_sig[s],
                               [gloss_sig[x] for x in sib_by_syn[s] if gloss_sig[x] is not None], cfg)
                for s in cand}

    def a_s(idxs, Ctx, assoc):
        mean_sig = sigs_for(cand, seeds_by_syn, assoc, mat, w2i)
        if readout == "topk":
            sw = {s: list(seeds_by_syn[s]) + list(assoc.get(s, [])) for s in cand}
            return score_topk(recs, idxs, sw, mean_sig, Ctx, mat, w2i, k=topk)
        return score(recs, idxs, mean_sig, Ctx)

    # -------- baselines --------
    gloss_assoc = {s: [] for s in cand}
    gloss_dev = a_s(dev_idx, Ctx_dev, gloss_assoc); gloss_test = a_s(test_idx, Ctx_test, gloss_assoc)

    # -------- CONFIG SWEEP on DEV (freeze, then report on TEST) --------
    configs = {
        "recurrence_only":       dict(cfg0, cap=cap, drop={"schema", "multiseed", "ppmi"}),
        "recur+ppmi":            dict(cfg0, cap=cap, drop={"schema", "multiseed"}),
        "recur+multiseed":       dict(cfg0, cap=cap, drop={"schema", "ppmi"}),
        "recur+ppmi+multiseed":  dict(cfg0, cap=cap, drop={"schema"}),
        "full_gate":             dict(cfg0, cap=cap, drop=set()),
        "recur+schema":          dict(cfg0, cap=cap, drop={"multiseed", "ppmi"}),
    }
    sweep = {}
    for name, cfg in configs.items():
        assoc = build_assoc(cfg)
        dv = a_s(dev_idx, Ctx_dev, assoc)
        sweep[name] = {"dev": round(float(dv.mean()), 4),
                       "mean_assoc": round(float(np.mean([len(assoc[s]) for s in cand])), 2)}
        print("[sweep] %-22s dev a_s=%.4f  assoc/sense=%.1f  (%.0fs)"
              % (name, sweep[name]["dev"], sweep[name]["mean_assoc"], time.time() - t0), flush=True)
    best_name = max(sweep, key=lambda k: sweep[k]["dev"])
    best_cfg = configs[best_name]
    print("[sweep] BEST-ON-DEV = %s (dev a_s=%.4f)" % (best_name, sweep[best_name]["dev"]), flush=True)

    # -------- report the DEV-FROZEN config on TEST + twins --------
    cons_assoc = build_assoc(best_cfg)
    cons_test = a_s(test_idx, Ctx_test, cons_assoc)
    raw_assoc = {s: raw_assocs(agg_by_syn[s], cap) for s in cand}
    raw_test = a_s(test_idx, Ctx_test, raw_assoc)
    syntag_assoc = {s: [w.lower().split("_")[0] for w in syntag.get(s, [])] for s in cand}
    syntag_test = a_s(test_idx, Ctx_test, syntag_assoc)

    rng = np.random.default_rng(1234); cl = sorted(cand); perm = list(cl); rng.shuffle(perm)
    shuf = dict(zip(cl, perm)); shuf_assoc = {s: cons_assoc[shuf[s]] for s in cand}
    shuf_test = a_s(test_idx, Ctx_test, shuf_assoc)

    # -------- MFS no-regression guard (blended overall on all test items) --------
    gl_sig = sigs_for(cand, seeds_by_syn, gloss_assoc, mat, w2i)
    cn_sig = sigs_for(cand, seeds_by_syn, cons_assoc, mat, w2i)
    ov_gloss, mfs = blended_overall(recs, all_test_idx, gl_sig, Ctx_all, mat, w2i, lam=1.0, T=0.1)
    ov_cons, _ = blended_overall(recs, all_test_idx, cn_sig, Ctx_all, mat, w2i, lam=1.0, T=0.1)

    n = min(len(gloss_test), len(cons_test), len(raw_test))
    res = {
        "n_dev_sub": len(dev_idx), "n_test_sub": len(test_idx), "n_all_test": len(all_test_idx),
        "n_sents": store["n_sents"], "cap": cap, "cfg0": {k: v for k, v in cfg0.items() if k != "drop"},
        "best_config_on_dev": best_name, "sweep": sweep,
        "a_s_test": {"gloss": round(float(gloss_test.mean()), 4), "RAW": round(float(raw_test.mean()), 4),
                     "CONSOLIDATED": round(float(cons_test.mean()), 4),
                     "twin_shuffled": round(float(shuf_test.mean()), 4),
                     "CEILING_syntagnet": round(float(syntag_test.mean()), 4)},
        "CONSOLIDATED_vs_gloss": _paired(cons_test[:n], gloss_test[:n], 101),
        "RAW_vs_gloss": _paired(raw_test[:n], gloss_test[:n], 102),
        "CONSOLIDATED_vs_RAW": _paired(cons_test[:n], raw_test[:n], 103),
        "CONSOLIDATED_vs_shuffled": _paired(cons_test[:len(shuf_test)], shuf_test, 104),
        "syntagnet_ceiling_gap": _paired(syntag_test[:n], cons_test[:n], 106),
        "MFS_guard": {"mfs_floor": round(float(mfs.mean()), 4),
                      "overall_gloss_blend": round(float(ov_gloss.mean()), 4),
                      "overall_CONS_blend": round(float(ov_cons.mean()), 4),
                      "CONS_vs_MFS": _paired(ov_cons, mfs, 107),
                      "CONS_vs_gloss_blend": _paired(ov_cons, ov_gloss, 108)},
    }
    res["headline"] = (
        "CONSOLIDATION GATE [%s] | gloss=%.3f RAW=%.3f CONS=%.3f | CONS>gloss sep=%s null_p95=%s | "
        "RAW<gloss(regress)=%s | CONS>RAW sep=%s | shuf lose=%s | ceiling=%.3f gap=%+.3f | "
        "MFS %.3f overallCONS %.3f (>=MFS sep=%s)"
        % (best_name, res["a_s_test"]["gloss"], res["a_s_test"]["RAW"], res["a_s_test"]["CONSOLIDATED"],
           res["CONSOLIDATED_vs_gloss"]["sep"], res["CONSOLIDATED_vs_gloss"]["null_p95"],
           (res["RAW_vs_gloss"]["delta"] < 0), res["CONSOLIDATED_vs_RAW"]["sep"],
           res["CONSOLIDATED_vs_shuffled"]["sep"], res["a_s_test"]["CEILING_syntagnet"],
           res["syntagnet_ceiling_gap"]["delta"], res["MFS_guard"]["mfs_floor"],
           res["MFS_guard"]["overall_CONS_blend"], res["MFS_guard"]["CONS_vs_MFS"]["sep"]))
    res["readout"] = readout
    res["elapsed_s"] = round(time.time() - t0, 1)
    tag = ("smoke_" if smoke else "") + ("%s_s%d_cap%d" % (readout, store["n_sents"], cap))
    with open(os.path.join(OUT_DIR, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "consolidation_gate_v1", "verdict": "MEASURED", "result": res}, f,
                  indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    assert _ppmi(10, 100, 100, 100000) > _ppmi(10, 100, 5000, 100000), "ppmi must downweight frequent w"
    agg = {"river": (3, 20, 2.5), "the": (1, 500, 0.0), "shore": (2, 8, 1.8)}
    assert raw_assocs(agg, 2)[0] == "the", "raw twin ranks by raw count -> frequent noise wins"
    print("SELFTEST PASS", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-sents", type=int, default=0)   # 0 == ALL simplewiki (bare == full)
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--K", type=int, default=3)
    ap.add_argument("--M", type=int, default=2)
    ap.add_argument("--P", type=float, default=1.0)
    ap.add_argument("--margin", type=float, default=0.0)
    ap.add_argument("--readout", default="mean", choices=["mean", "topk"])
    ap.add_argument("--topk", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    cfg0 = {"K": args.K, "M": args.M, "P": args.P, "margin": args.margin, "cap": args.cap, "drop": set()}
    ms = 120000 if args.smoke else args.max_sents
    run(ms, args.cap, cfg0, smoke=args.smoke, readout=args.readout, topk=args.topk)
    return 0


if __name__ == "__main__":
    sys.exit(main())
