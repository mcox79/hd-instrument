"""exp_grounded_semantic_graph_ladder_wsd_v1 -- the AUGMENTATION LADDER for the grounded relational
semantic-graph organ, read by SPREADING ACTIVATION (personalized PageRank), tested on gold WiC + SemCor.

PROBLEM: promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ. The baseline
exp_ppr_spreading_activation_wsd_wic_v1 established (glass-box, LM-free) that per-context sense
selection is SPREADING ACTIVATION over a relational graph (PPR == random-walk-with-restart), NOT
vector cosine; disambiguated gloss edges (g1) reach WiC dev 0.652 and clear the context-shuffle twin.
This cell CLIMBS THE LADDER on the SAME operator (baseline _ppr / _disambiguate; apples-to-apples) by
changing only the GRAPH, each rung an ablation with the twin control:

  base   = WordNet relations + MFS-DISAMBIGUATED gloss edges (the g1 baseline).            [taxonomic+definitional]
  +CN    = base + ConceptNet commonsense edges (MFS-disambiguated).                        [THEMATIC pole, Mirman 2017]
  +IC    = base with edges weighted by information content (wordnet_ic).                    [PFC/IFG reliability reweighting]
  +CN+IC = both.
  grounded (mode) = fuse the walk with predicted-Binder-65 node coherence (GROUNDED_PPR).  [sensorimotor spokes / ATL hub]

BRAIN-FOUNDATIONAL FRAME: WordNet relations = ATL taxonomic hub; ConceptNet = TPJ/pMTG thematic pole
(the double dissociation, PINNED both-needed); glosses = definitional associations; Binder nodes =
sensorimotor spokes (hub-and-spoke); IC = the reliability weighting semantic_control (PFC/IFG) applies
to the diffusion. Each is a distinct, evidenced brain component, not "more edges."

SCORING: WiC dev AND test (held-out), gold labels, vs the CONTEXT-SHUFFLE TWIN (disambiguate side-2
from a random other sentence -- the dominant-sense null), NOT the naive floor. Report acc + CI +
CI half-width + paired margin (real-twin) with its bootstrap CI (the null-separation test). Second
gold: SemCor per-token all-words WSD accuracy vs the MFS floor (the field-standard task; UKB ~67,
SyntagRank ~72 vs MFS 65.2). Residual: quantify the WordNet<->WiC GRANULARITY/COVERAGE gap.

Glass-box, deterministic, ASCII, NO external LLM at inference. Reuses baseline _ppr/_disambiguate/
_content/_mean_binder/_gloss_content/_synset_grounded (does NOT reimplement the science). Writes ONLY
to data/exp_grounded_semantic_graph_ladder_wsd_v1[/ _smoke].

# KB_REFERENT: data/wsd_benchmarks
# KB_REFERENT: data/datasets/conceptnet5_en_100k.jsonl
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.load_wsd_benchmarks import load_wic
from experiments.exp_sense_wall_breakthrough_wic_v1 import _content, _STOP
from experiments.exp_ppr_spreading_activation_wsd_wic_v1 import (
    _ppr, _gloss_content, _synset_grounded, _z, _mean_binder, DAMPING, PPR_ITERS, _WNPOS,
)


def _disamb(wn, lemma, pos, context_words, syn2idx, T, n, target_syn_names,
            grounded=False, prior=False, d=DAMPING, iters=PPR_ITERS):
    """Baseline _disambiguate with ADDITIVE z-scoring, damping/iters threaded. Terms:
      - ppr    : spreading-activation over the graph (always present when there is context).
      - prior  : the RESTING-ACTIVATION / frequency term (WordNet sense order = SemCor frequency; sense-0
                 = MFS). Rodd 2004: a sense's resting level + context pre-activation TOGETHER settle WSD.
                 Prior alone == MFS; it is context-free, so it is COMMON-MODE on the WiC context-shuffle twin.
      - grounded: predicted-Binder-65 node coherence to the context (context-free lift; sensorimotor spoke).
    ONE disambiguation path for the whole cell; base-graph ppr cross-validates the baseline's WiC-dev 0.652."""
    tgt = wn.synsets(lemma, pos=_WNPOS.get(pos))
    if not tgt:
        return None
    if len(tgt) == 1:
        return tgt[0].name()
    seed = []
    tgt_set = set(target_syn_names)
    for w in context_words:
        for gs in wn.synsets(w):
            j = syn2idx.get(gs.name())
            if j is not None and gs.name() not in tgt_set:      # ppr_w2w: exclude target's own senses
                seed.append(j)
    r = _ppr(sorted(set(seed)), T, n, d=d, iters=iters)
    have_ctx = r is not None
    ppr_scores = np.array([float(r[syn2idx[s.name()]]) if (have_ctx and s.name() in syn2idx) else 0.0
                           for s in tgt])
    if not grounded and not prior:                              # pure spreading activation (the ladder arms)
        return tgt[0].name() if not have_ctx else tgt[int(np.argmax(ppr_scores))].name()
    score = _z(ppr_scores) if have_ctx else np.zeros(len(tgt))
    if prior:
        score = score + _z(-np.arange(len(tgt), dtype=float))  # resting level: sense-0 (MFS) highest
    if grounded:
        cvec = _mean_binder(set(context_words))
        if cvec is not None:
            gcos = np.array([float(np.dot(_synset_grounded(s), cvec)) if _synset_grounded(s) is not None
                             else 0.0 for s in tgt])
            score = score + _z(gcos)
    return tgt[int(np.argmax(score))].name()

ANCHOR = "grounded_semantic_graph_ladder_wsd_v1"
CN_PATH = os.path.join(REPO, "data", "datasets", "conceptnet5_en_100k.jsonl")
# KB_REFERENT: data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
SYNTAGNET_PATH = os.path.join(REPO, "data", "syntagnet", "SyntagNet-1.0", "SYNTAGNET_1.0.txt")

# ConceptNet predicates that carry RELATEDNESS/THEMATIC signal (co-activation helps disambiguation).
# Exclude polarity/negation predicates (Antonym, DistinctFrom, Not*) -- opposites should not co-activate a sense.
_CN_KEEP = {
    "RelatedTo", "IsA", "PartOf", "HasA", "UsedFor", "CapableOf", "AtLocation", "Causes",
    "HasProperty", "MadeOf", "Synonym", "DerivedFrom", "HasContext", "SimilarTo", "HasSubevent",
    "HasPrerequisite", "MotivatedByGoal", "ReceivesAction", "DefinedAs", "SymbolOf", "InstanceOf",
}

_GRAPHS: Dict[str, Tuple[Dict[str, int], sp.csr_matrix]] = {}


# ================================================================================================
# graph construction -- shared synset ordering (identical to baseline: sorted by name)
# ================================================================================================
def _synsets_ordered():
    from nltk.corpus import wordnet as wn
    return sorted(wn.all_synsets(), key=lambda s: s.name())


def _rels(s):
    return (s.hypernyms() + s.hyponyms() + s.member_holonyms() + s.part_holonyms()
            + s.substance_holonyms() + s.member_meronyms() + s.part_meronyms()
            + s.substance_meronyms() + s.attributes() + s.similar_tos() + s.also_sees()
            + s.verb_groups() + s.entailments() + s.causes())


def _relation_gloss_edges(syns, syn2idx, gloss_cap):
    from nltk.corpus import wordnet as wn
    rows, cols = [], []
    for s in syns:
        i = syn2idx[s.name()]
        for t in _rels(s):
            j = syn2idx.get(t.name())
            if j is not None:
                rows.append(i); cols.append(j)
        for w in _gloss_content(s.definition()):
            for gs in wn.synsets(w)[:gloss_cap]:
                j = syn2idx.get(gs.name())
                if j is not None and j != i:
                    rows.append(i); cols.append(j)
    return rows, cols


def _conceptnet_edges(syn2idx, cn_cap=1):
    """Map ConceptNet (lemma-level) assertions to WordNet synset edges, MFS-disambiguated (sense-1 of
    each endpoint, cn_cap=1 -- same principle as g1 gloss edges). Returns symmetric edge rows/cols."""
    from nltk.corpus import wordnet as wn
    rows, cols = [], []
    n_kept = 0
    if not os.path.exists(CN_PATH):
        return rows, cols, 0
    cache: Dict[str, list] = {}

    def syns_of(concept):
        if concept in cache:
            return cache[concept]
        try:
            r = [s.name() for s in wn.synsets(concept)[:cn_cap]]
        except Exception:
            r = []
        cache[concept] = r
        return r

    with open(CN_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except Exception:
                continue
            if a.get("predicate") not in _CN_KEEP:
                continue
            for sn in syns_of(a.get("subject", "")):
                si = syn2idx.get(sn)
                if si is None:
                    continue
                for on in syns_of(a.get("object", "")):
                    oj = syn2idx.get(on)
                    if oj is not None and oj != si:
                        rows.append(si); cols.append(oj); n_kept += 1
    return rows, cols, n_kept


def _syntagnet_edges(syn2idx):
    """SyntagNet 1.0 (Maru/Scozzafava/Navigli 2019; CC BY-NC-SA 4.0): 88,019 MANUALLY-DISAMBIGUATED
    syntagmatic (co-occurrence) edges between WordNet 3.0 synsets. Each line: off1+pos off2+pos w1 p1 w2 p2.
    These are already sense-specific (no MFS mapping needed) -- the field's proven 'sharpen the context
    edges' lever (SyntagRank 71.7 vs UKB 67.3 all-words). Returns symmetric edge rows/cols."""
    from nltk.corpus import wordnet as wn
    rows, cols = [], []
    n_kept = 0
    if not os.path.exists(SYNTAGNET_PATH):
        return rows, cols, 0
    with open(SYNTAGNET_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            try:
                o1, o2 = parts[0], parts[1]
                s1 = wn.synset_from_pos_and_offset(o1[-1], int(o1[:-1]))
                s2 = wn.synset_from_pos_and_offset(o2[-1], int(o2[:-1]))
            except Exception:
                continue
            i = syn2idx.get(s1.name()); j = syn2idx.get(s2.name())
            if i is not None and j is not None and i != j:
                rows.append(i); cols.append(j); n_kept += 1
    return rows, cols, n_kept


def _ic_norm(syns, syn2idx):
    """Per-synset INFORMATION CONTENT in [0,1] (wordnet_ic ic-semcor.dat): IC = -log(freq/root). NOTE
    wordnet_ic stores accumulated FREQUENCY, not IC -- generic hubs (entity.n.01) have HIGH freq -> LOW
    IC; specific leaves (poodle.n.01) have LOW freq -> HIGH IC. Unseen synsets are smoothed to a small
    count (high but finite IC). adj/adv (no IC file) -> 0. Normalized to [0,1] (specific leaves ~1)."""
    import math
    from nltk.corpus import wordnet_ic
    ic = wordnet_ic.ic("ic-semcor.dat")
    out = np.zeros(len(syn2idx), np.float32)
    for s in syns:
        pos = s.pos()
        if pos not in ("n", "v"):
            continue
        d = ic[pos]
        root = float(d.get(0, 0.0))
        if root <= 0:
            continue
        freq = float(d.get(s.offset(), 0.0))
        freq = max(freq, 0.5)                       # smoothing: unseen -> rare -> informative (finite)
        out[syn2idx[s.name()]] = -math.log(freq / root)
    m = float(out.max()) or 1.0
    return out / m  # generic hubs ~0, specific leaves ~1


def _symmetrize(rows, cols, n, weight=None):
    r = np.array(rows + cols, dtype=np.int64)
    c = np.array(cols + rows, dtype=np.int64)
    if weight is None:
        d = np.ones(len(r), np.float32)
    else:
        d = np.array(list(weight) + list(weight), dtype=np.float32)
    return sp.csr_matrix((d, (r, c)), shape=(n, n))


def _row_stochastic(A):
    A = A.tocsr()
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1.0
    return A.multiply(1.0 / deg[:, None]).tocsr()


def build_graph(variant: str, cache_dir: str):
    """variant in {base, cn, ic, cn_ic}. base = relations + g1(MFS) gloss edges. Returns (syn2idx, T)
    where T is row-stochastic (same operator convention as the baseline _ppr: r=(1-d)p+d*T@r)."""
    if variant in _GRAPHS:
        return _GRAPHS[variant]
    cache = os.path.join(cache_dir, f"graph_{variant}.npz")
    meta = os.path.join(cache_dir, "syn2idx.json")
    syns = _synsets_ordered()
    syn2idx = {s.name(): i for i, s in enumerate(syns)}
    n = len(syns)
    if os.path.exists(cache):
        z = np.load(cache)
        T = sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(n, n))
        _GRAPHS[variant] = (syn2idx, T)
        return _GRAPHS[variant]

    parts = variant.split("_")
    use_ic = "ic" in parts
    use_cn = "cn" in parts
    use_syn = "syn" in parts
    rows, cols = _relation_gloss_edges(syns, syn2idx, gloss_cap=1)
    if use_cn:
        cr, cc, _ = _conceptnet_edges(syn2idx, cn_cap=1)
        rows = rows + cr; cols = cols + cc
    if use_syn:
        sr, sc, _ = _syntagnet_edges(syn2idx)
        rows = rows + sr; cols = cols + sc

    if use_ic:
        icv = _ic_norm(syns, syn2idx)
        eps = 0.1
        # edge (i,j) weight = eps + max(informativeness of endpoints): up-weight edges touching specific
        # (high-IC) synsets, down-weight traffic through generic hubs (entity.n.01). OUR-INVENTION-UNDER-TEST.
        ra = np.array(rows, dtype=np.int64); ca = np.array(cols, dtype=np.int64)
        w = eps + np.maximum(icv[ra], icv[ca])
        A = _symmetrize(rows, cols, n, weight=w)
    else:
        A = _symmetrize(rows, cols, n)
        A.data[:] = 1.0
    T = _row_stochastic(A)
    os.makedirs(cache_dir, exist_ok=True)
    np.savez(cache, data=T.data, indices=T.indices, indptr=T.indptr)
    if not os.path.exists(meta):
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({"n": n}, f)
    _GRAPHS[variant] = (syn2idx, T)
    return _GRAPHS[variant]


# ================================================================================================
# evaluation -- WiC, context-shuffle twin, full margin stats (mirrors baseline _eval + richer)
# ================================================================================================
def _boot(a, seed, reps=2000):
    idx = np.random.default_rng(seed).integers(0, len(a), size=(reps, len(a)))
    m = a[idx].mean(1)
    return float(a.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def eval_wic(pairs, syn2idx, T, mode, damping=DAMPING, iters=PPR_ITERS, seed=0):
    from nltk.corpus import wordnet as wn
    n = len(syn2idx)
    npairs = len(pairs)
    rng = np.random.default_rng(seed + 7)
    perm = rng.permutation(npairs)
    grd = (mode == "grounded"); pri = (mode == "prior_ppr")
    correct = np.zeros(npairs, np.int32)
    twin = np.zeros(npairs, np.int32)
    pred_same = 0
    for i, p in enumerate(pairs):
        lemma, pos = p["lemma"], p["pos"]
        tgt_names = [s.name() for s in wn.synsets(lemma, pos=_WNPOS.get(pos))]
        c1 = list(_content(p["sent1"]) - {lemma}); c2 = list(_content(p["sent2"]) - {lemma})
        s1 = _disamb(wn, lemma, pos, c1, syn2idx, T, n, tgt_names, grounded=grd, prior=pri, d=damping, iters=iters)
        s2 = _disamb(wn, lemma, pos, c2, syn2idx, T, n, tgt_names, grounded=grd, prior=pri, d=damping, iters=iters)
        oc2 = list(_content(pairs[perm[i]]["sent2"]) - {lemma})
        s2t = _disamb(wn, lemma, pos, oc2, syn2idx, T, n, tgt_names, grounded=grd, prior=pri, d=damping, iters=iters)
        pred = (s1 == s2); pred_same += int(pred)
        correct[i] = int(pred == p["gold"])
        twin[i] = int((s1 == s2t) == p["gold"])
    acc, lo, hi = _boot(correct, seed)
    tacc, tlo, thi = _boot(twin, seed + 1)
    dpr = (correct - twin).astype(np.float64)
    di = np.random.default_rng(seed + 3).integers(0, npairs, size=(2000, npairs))
    dboot = dpr[di].mean(1)
    dlo, dhi = float(np.percentile(dboot, 2.5)), float(np.percentile(dboot, 97.5))
    gold_rate = float(np.mean([p["gold"] for p in pairs]))
    return {
        "n": npairs, "acc": round(acc, 4), "ci": [round(lo, 4), round(hi, 4)],
        "ci_halfwidth": round((hi - lo) / 2, 4),
        "twin_acc": round(tacc, 4), "twin_ci": [round(tlo, 4), round(thi, 4)],
        "real_minus_twin": round(float(dpr.mean()), 4),
        "margin_ci": [round(dlo, 4), round(dhi, 4)],
        "real_beats_twin": bool(dlo > 0),
        "floor": round(max(gold_rate, 1 - gold_rate), 4),
        "pred_same_frac": round(pred_same / npairs, 4),
    }


# ================================================================================================
# SemCor all-words WSD (second gold) -- per-token accuracy vs MFS
# ================================================================================================
def _semcor_instances(max_files, seed=0):
    """Sense-tagged tokens from SemCor: (lemma, pos, gold_synset_name, context_lemmas). Sampled
    deterministically. Only polysemous n/v content words (MFS is a nontrivial baseline there)."""
    from nltk.corpus import semcor, wordnet as wn
    files = sorted(semcor.fileids())[:max_files]
    inst = []
    for fn in files:
        for sent in semcor.tagged_sents(fn, tag="sem"):
            ctx = []
            chunks = []
            for ch in sent:
                try:
                    lbl = ch.label()
                except Exception:
                    lbl = None
                leaves = ch.leaves() if hasattr(ch, "leaves") else [ch]
                surface = "_".join([str(x) for x in leaves]).lower()
                w = "".join(c for c in surface.split("_")[0] if c.isalpha())
                if len(w) >= 3 and w not in _STOP:      # content words only (match the WiC _content path)
                    ctx.append(w)
                if lbl is not None and hasattr(lbl, "synset"):
                    chunks.append((lbl, surface))
            ctxset = set(ctx)
            for lbl, surface in chunks:
                try:
                    syn = lbl.synset()
                    lemma = lbl.name().split(".")[0].lower() if hasattr(lbl, "name") else None
                except Exception:
                    continue
                if syn is None:
                    continue
                pos = syn.pos()
                if pos not in ("n", "v"):
                    continue
                base = lemma or surface.split("_")[0].lower()
                senses = wn.synsets(base, pos=pos)
                if len(senses) < 2:      # polysemous only -- MFS is trivial otherwise
                    continue
                inst.append({"lemma": base, "pos": {"n": "N", "v": "V"}[pos],
                             "gold": syn.name(), "ctx": sorted(ctxset - {base})})
    rng = np.random.default_rng(seed)
    rng.shuffle(inst)
    return inst


def eval_semcor(inst, syn2idx, T, mode, seed=0):
    from nltk.corpus import wordnet as wn
    n = len(syn2idx)
    grd = (mode == "grounded"); pri = (mode == "prior_ppr")
    real = np.zeros(len(inst), np.int32)
    mfs = np.zeros(len(inst), np.int32)
    for k, it in enumerate(inst):
        lemma, pos = it["lemma"], it["pos"]
        tgt_names = [s.name() for s in wn.synsets(lemma, pos=_WNPOS.get(pos))]
        pred = _disamb(wn, lemma, pos, it["ctx"], syn2idx, T, n, tgt_names, grounded=grd, prior=pri)
        real[k] = int(pred == it["gold"])
        mfs[k] = int((tgt_names[0] if tgt_names else None) == it["gold"])
    acc, lo, hi = _boot(real, seed)
    macc, mlo, mhi = _boot(mfs, seed + 1)
    d = (real - mfs).astype(np.float64)
    di = np.random.default_rng(seed + 3).integers(0, len(inst), size=(2000, len(inst)))
    dboot = d[di].mean(1)
    return {
        "n": len(inst), "acc": round(acc, 4), "ci": [round(lo, 4), round(hi, 4)],
        "mfs_acc": round(macc, 4), "mfs_ci": [round(mlo, 4), round(mhi, 4)],
        "real_minus_mfs": round(float(d.mean()), 4),
        "margin_ci": [round(float(np.percentile(dboot, 2.5)), 4), round(float(np.percentile(dboot, 97.5)), 4)],
        "real_beats_mfs": bool(float(np.percentile(dboot, 2.5)) > 0),
    }


# ================================================================================================
# residual analysis -- WordNet<->WiC granularity/coverage
# ================================================================================================
def residual_analysis(pairs, syn2idx, T, seed=0):
    """For the base graph, split WiC errors: (a) COVERAGE -- monosemous/OOV/no-context (walk had no
    signal), (b) GRANULARITY -- 'different'-gold pairs where the two chosen synsets are near-synonyms
    (wup>=0.8) i.e. WordNet splits finer than WiC's human same/diff judgement. Quantifies how much of
    the residual is a FOUNDATION (inventory) gap vs an ALGORITHM gap."""
    from nltk.corpus import wordnet as wn
    n = len(syn2idx)
    total = len(pairs)
    err = 0
    err_coverage = 0
    err_granularity = 0
    err_other = 0
    for p in pairs:
        lemma, pos = p["lemma"], p["pos"]
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos))
        tgt_names = [s.name() for s in tgt]
        c1 = list(_content(p["sent1"]) - {lemma}); c2 = list(_content(p["sent2"]) - {lemma})
        s1 = _disamb(wn, lemma, pos, c1, syn2idx, T, n, tgt_names)
        s2 = _disamb(wn, lemma, pos, c2, syn2idx, T, n, tgt_names)
        pred = (s1 == s2)
        if pred == p["gold"]:
            continue
        err += 1
        monosemous = len(tgt) < 2
        no_ctx = (len(c1) == 0 or len(c2) == 0)
        if monosemous or no_ctx:
            err_coverage += 1
            continue
        # granularity: gold=SAME (True) but we predicted DIFFERENT (s1!=s2) with the two picked synsets
        # near-synonyms (wup>=0.8) -> WordNet splits finer than WiC's human same/diff judgement (over-split).
        if (p["gold"] is True) and s1 != s2 and s1 is not None and s2 is not None:
            try:
                wup = wn.synset(s1).wup_similarity(wn.synset(s2)) or 0.0
            except Exception:
                wup = 0.0
            if wup >= 0.8:
                err_granularity += 1
                continue
        err_other += 1
    return {
        "n": total, "errors": err,
        "err_coverage_monosemous_or_nocontext": err_coverage,
        "err_granularity_wordnet_oversplit": err_granularity,
        "err_algorithm_other": err_other,
        "pct_residual_foundation": round((err_coverage + err_granularity) / err, 4) if err else 0.0,
    }


# ================================================================================================
def _prep(rows):
    return [{"lemma": r["lemma"].lower(), "pos": r["pos"], "gold": bool(r["gold"]),
             "sent1": r["sent1"], "sent2": r["sent2"]} for r in rows]


def run_ladder(mode: str, cache_dir: str) -> dict:
    t0 = time.time()
    dev = _prep(load_wic("dev")); test = _prep(load_wic("test"))
    if mode == "smoke":
        dev = dev[:120]; test = test[:120]
    variants = ["base", "cn", "ic", "cn_ic"] if mode != "smoke" else ["base", "cn"]
    out = {"dev": {}, "test": {}}
    for v in variants:
        syn2idx, T = build_graph(v, cache_dir)
        out["dev"][v] = eval_wic(dev, syn2idx, T, "ppr")
        out["dev"][v + "+grounded"] = eval_wic(dev, syn2idx, T, "grounded")
    # winner on dev by real_minus_twin among rungs that beat the twin (fallback: max acc)
    beats = {k: r for k, r in out["dev"].items() if r["real_beats_twin"]}
    pool = beats if beats else out["dev"]
    winner = max(pool, key=lambda k: pool[k]["real_minus_twin"])
    wv = winner.replace("+grounded", "")
    syn2idx, T = build_graph(wv, cache_dir)
    out["test"][winner] = eval_wic(test, syn2idx, T, "grounded" if "grounded" in winner else "ppr")
    sb, Tb = build_graph("base", cache_dir)
    out["test"]["base"] = eval_wic(test, sb, Tb, "ppr")
    out["winner"] = winner
    out["elapsed_s"] = round(time.time() - t0, 2)
    return out


# ================================================================================================
# LOG-LINEAR BLEND: score(s) = log P_freq(s) + lambda * log PPR(s). The drill's decisive recipe --
# it IS the field's UKB linear-combination AND the brain's ambiguity gate (a peaked prior needs a
# confident walk to override = subordinate-bias; a flat prior lets context decide = competition). PPR
# is computed ONCE per item; lambda is swept by cheap re-scoring; lambda tuned on a DISJOINT dev split.
# ================================================================================================
def _sense_ppr(wn, lemma, pos, context_words, syn2idx, T, n, tgt, tgt_names):
    seed = []
    tgt_set = set(tgt_names)
    for w in context_words:
        for gs in wn.synsets(w):
            j = syn2idx.get(gs.name())
            if j is not None and gs.name() not in tgt_set:
                seed.append(j)
    r = _ppr(sorted(set(seed)), T, n)
    if r is None:
        return None
    return np.array([float(r[syn2idx[s.name()]]) if s.name() in syn2idx else 0.0 for s in tgt])


def _ppr_pvec(p, T, n, d=DAMPING, iters=PPR_ITERS):
    """PPR from a precomputed (possibly non-uniform) personalization vector p."""
    s = float(p.sum())
    if s <= 0:
        return None
    p = (p / s).astype(np.float32)
    r = p.copy()
    for _ in range(iters):
        r = (1.0 - d) * p + d * (T @ r)
    return r


def _sense_ppr_fw(wn, lemma, pos, context_words, syn2idx, T, n, tgt, tgt_names):
    """FREQUENCY-WEIGHTED seeding (UKB dict_weight): seed each context sense by its SemCor frequency, not
    uniformly -- the untested half of the field's UKB recipe. Then read out the target's senses' walk mass."""
    p = np.zeros(n, np.float32)
    tgt_set = set(tgt_names)
    seeded = False
    for w in context_words:
        for gs in wn.synsets(w):
            nm = gs.name()
            if nm in tgt_set:
                continue
            j = syn2idx.get(nm)
            if j is None:
                continue
            cnt = 0
            for l in gs.lemmas():
                if l.name().lower() == w.lower():
                    cnt = l.count(); break
            p[j] += float(cnt) + 1.0                          # +1 smoothing; weight by sense frequency
            seeded = True
    if not seeded:
        return None
    r = _ppr_pvec(p, T, n)
    if r is None:
        return None
    return np.array([float(r[syn2idx[s.name()]]) if s.name() in syn2idx else 0.0 for s in tgt])


def _sense_prior(lemma, tgt):
    """SemCor sense-frequency counts per candidate (the resting level); rank-based fallback when the
    lemma has no counts (WordNet sense order is itself frequency-ranked, sense-0 = MFS)."""
    counts = []
    for s in tgt:
        c = 0
        for l in s.lemmas():
            if l.name().lower() == lemma.lower():
                c = l.count(); break
        counts.append(float(c))
    counts = np.array(counts, float)
    if counts.sum() == 0:
        counts = 1.0 / (1.0 + np.arange(len(tgt)))
    return counts


def _blend_pick(ppr, prior, lam, alpha=0.1, eps=1e-6):
    """argmax [ log P_freq + lam*log PPR ]. ppr None (no context) -> prior only (== MFS-by-count)."""
    pf = prior + alpha; pf = pf / pf.sum()
    if ppr is None:
        return int(np.argmax(pf))
    pp = ppr + eps; pp = pp / pp.sum()
    return int(np.argmax(np.log(pf) + lam * np.log(pp)))


_LAMBDAS = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]


def eval_wic_blend(pairs, syn2idx, T, lam, seed=0):
    from nltk.corpus import wordnet as wn
    n = len(syn2idx); npairs = len(pairs)
    perm = np.random.default_rng(seed + 7).permutation(npairs)
    correct = np.zeros(npairs, int); twin = np.zeros(npairs, int)

    def pick(lemma, pos, ctx, tgt, tgt_names):
        if not tgt:
            return None
        if len(tgt) == 1:
            return tgt[0].name()
        ppr = _sense_ppr(wn, lemma, pos, ctx, syn2idx, T, n, tgt, tgt_names)
        return tgt[_blend_pick(ppr, _sense_prior(lemma, tgt), lam)].name()

    for i, p in enumerate(pairs):
        lemma, pos = p["lemma"], p["pos"]
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tgt_names = [s.name() for s in tgt]
        c1 = list(_content(p["sent1"]) - {lemma}); c2 = list(_content(p["sent2"]) - {lemma})
        s1 = pick(lemma, pos, c1, tgt, tgt_names); s2 = pick(lemma, pos, c2, tgt, tgt_names)
        oc2 = list(_content(pairs[perm[i]]["sent2"]) - {lemma})
        s2t = pick(lemma, pos, oc2, tgt, tgt_names)
        correct[i] = int((s1 == s2) == p["gold"]); twin[i] = int((s1 == s2t) == p["gold"])
    acc, lo, hi = _boot(correct, seed); tacc, _, _ = _boot(twin, seed + 1)
    dpr = (correct - twin).astype(float)
    di = np.random.default_rng(seed + 3).integers(0, npairs, size=(2000, npairs))
    dlo = float(np.percentile(dpr[di].mean(1), 2.5))
    return {"acc": round(acc, 4), "ci": [round(lo, 4), round(hi, 4)], "twin_acc": round(tacc, 4),
            "real_minus_twin": round(float(dpr.mean()), 4), "margin_ci_lo": round(dlo, 4),
            "real_beats_twin": bool(dlo > 0)}


def run_blend(mode, cache_dir):
    from nltk.corpus import wordnet as wn
    t0 = time.time()
    syn2idx, T = build_graph("cn", cache_dir)                 # cn = the WiC-ladder winner
    n = len(syn2idx)
    inst = _semcor_instances(max_files=(6 if mode == "smoke" else 16))
    inst = inst[:(200 if mode == "smoke" else 5000)]
    perm = np.random.default_rng(0).permutation(len(inst))
    cache = []
    for it in inst:
        lemma, pos = it["lemma"], it["pos"]
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tgt_names = [s.name() for s in tgt]
        gi = tgt_names.index(it["gold"]) if it["gold"] in tgt_names else -1
        ppr = _sense_ppr(wn, lemma, pos, it["ctx"], syn2idx, T, n, tgt, tgt_names)
        prior = _sense_prior(lemma, tgt)
        top2 = np.sort(prior)[::-1][:2]
        balanced = bool(len(prior) >= 2 and top2[0] < 2.0 * max(top2[1], 1e-9))
        cache.append((ppr, prior, gi, balanced))
    half = len(cache) // 2
    dev_idx, test_idx = perm[:half], perm[half:]

    def acc_on(idxs, lam):
        return np.array([int(_blend_pick(cache[i][0], cache[i][1], lam) == cache[i][2]) for i in idxs])

    dev_scores = {lam: round(float(acc_on(dev_idx, lam).mean()), 4) for lam in _LAMBDAS}
    lam_star = max(dev_scores, key=dev_scores.get)
    test_c = acc_on(test_idx, lam_star); mfs_c = acc_on(test_idx, 0.0); pure_c = acc_on(test_idx, 50.0)
    tacc, tlo, thi = _boot(test_c, 0); macc, mlo, mhi = _boot(mfs_c, 1)
    d = (test_c - mfs_c).astype(float)
    di = np.random.default_rng(3).integers(0, len(d), size=(2000, len(d)))
    dlo = float(np.percentile(d[di].mean(1), 2.5)); dhi = float(np.percentile(d[di].mean(1), 97.5))
    bal = [i for i in test_idx if cache[i][3]]
    out = {
        "n_dev": len(dev_idx), "n_test": len(test_idx), "lambda_dev_grid": dev_scores,
        "lambda_star": lam_star,
        "test_blend_acc": round(tacc, 4), "test_blend_ci": [round(tlo, 4), round(thi, 4)],
        "test_mfs_acc(lam0)": round(macc, 4), "test_mfs_ci": [round(mlo, 4), round(mhi, 4)],
        "blend_minus_mfs": round(float(d.mean()), 4), "margin_ci": [round(dlo, 4), round(dhi, 4)],
        "blend_beats_mfs": bool(dlo > 0),
        "pure_walk_acc(lam50)": round(float(pure_c.mean()), 4),
        "balanced_n": len(bal),
        "balanced_blend": round(float(acc_on(bal, lam_star).mean()), 4) if bal else None,
        "balanced_mfs": round(float(acc_on(bal, 0.0).mean()), 4) if bal else None,
    }
    if out["balanced_blend"] is not None:
        out["balanced_gain"] = round(out["balanced_blend"] - out["balanced_mfs"], 4)
    wic = _prep(load_wic("test"))
    if mode == "smoke":
        wic = wic[:120]
    out["wic_test_blend_at_lam_star"] = eval_wic_blend(wic, syn2idx, T, lam_star)
    out["headline"] = ("BLEND log P_freq + %.2f*log PPR: SemCor test %.4f vs MFS %.4f (%+.4f, CI%s, beats=%s); "
                       "balanced-subset gain %s; WiC test still clears twin=%s." % (
                       lam_star, out["test_blend_acc"], out["test_mfs_acc(lam0)"], out["blend_minus_mfs"],
                       out["margin_ci"], out["blend_beats_mfs"], out.get("balanced_gain"),
                       out["wic_test_blend_at_lam_star"]["real_beats_twin"]))
    out["elapsed_s"] = round(time.time() - t0, 2)
    return out


# ================================================================================================
# COMPETITIVE ATTRACTOR SETTLING (the brain's ACTUAL mechanism, not linear diffusion). Drill: sense
# selection = nonlinear recurrent settling with LATERAL INHIBITION (Rodd/Gaskell 2004; Kawamoto 1993;
# McClelland-Rumelhart IAC; Snyder/Munakata "inhibition IS selection"). Implemented as recurrent
# DIVISIVE NORMALIZATION (Carandini & Heeger canonical competition):
#   e = alpha*(T@[a]+) + kappa*context + rho*rest(freq);  a = [e]+^nexp / (sigma^nexp + sum([e]+^nexp))
# The exponent nexp is THE lever: nexp=1 == linear diffusion (positive control, must reproduce PPR);
# nexp>1 sharpens winner-take-all -> can OVERRIDE the frequency prior (what linear PPR structurally cannot).
# ================================================================================================
def _settle(context_idx, rest_vec, T, N, alpha=0.85, kappa=1.0, rho=1.0, nexp=1.0, sigma=0.01, iters=30):
    context = np.zeros(N, np.float32)
    if context_idx:
        context[context_idx] = 1.0 / len(context_idx)
    a = context.copy()
    for _ in range(iters):
        e = alpha * (T @ a) + kappa * context + rho * rest_vec
        np.maximum(e, 0.0, out=e)
        en = e ** nexp if nexp != 1.0 else e
        a = en / (sigma ** nexp + float(en.sum()) + 1e-12)
    return a


def _settle_batch(P, R, T, alpha, kappa, rho, nexp, sigma, iters):
    """BATCHED competitive settling: P,R are (N,B) seed/rest matrices (B items at once). Same math as
    _settle but one sparse-dense matmul T@A per iteration instead of B Python-level matvecs (~10x)."""
    A = P.copy()
    sig_n = sigma ** nexp
    for _ in range(iters):
        E = alpha * (T @ A) + kappa * P + rho * R      # (N,B); T@A = sparse(N,N) @ dense(N,B)
        np.maximum(E, 0.0, out=E)
        En = E ** nexp if nexp != 1.0 else E
        A = En / (sig_n + En.sum(axis=0, keepdims=True) + 1e-12)
    return A


def _settle_cols(items, syn2idx, is_wic, perm=None):
    """Build per-column (seed_idx, rest_idx, rest_val, tgt_idx, tgt_names, item_i, slot). For WiC each
    item yields 3 columns (c1,c2,oc2-twin); for SemCor 1 column (ctx)."""
    from nltk.corpus import wordnet as wn
    cols = []
    for i, p in enumerate(items):
        lemma, pos = p["lemma"], p["pos"]
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tgt_names = [s.name() for s in tgt]
        tgt_idx = np.array([syn2idx[nm] for nm in tgt_names if nm in syn2idx], dtype=np.int64)
        prior = _sense_prior(lemma, tgt); lp = np.log1p(prior); lp = lp / (lp.sum() + 1e-9)
        rest_idx, rest_val = [], []
        for s, v in zip(tgt, lp):
            j = syn2idx.get(s.name())
            if j is not None:
                rest_idx.append(j); rest_val.append(float(v))
        rest_idx = np.array(rest_idx, dtype=np.int64); rest_val = np.array(rest_val, dtype=np.float32)
        tgt_set = set(tgt_names)
        if is_wic:
            c1 = list(_content(p["sent1"]) - {lemma}); c2 = list(_content(p["sent2"]) - {lemma})
            oc2 = list(_content(items[perm[i]]["sent2"]) - {lemma})
            ctxs = [c1, c2, oc2]
        else:
            ctxs = [p["ctx"]]
        for slot, ctx in enumerate(ctxs):
            seed = []
            for w in ctx:
                for gs in wn.synsets(w):
                    j = syn2idx.get(gs.name())
                    if j is not None and gs.name() not in tgt_set:
                        seed.append(j)
            cols.append((sorted(set(seed)), rest_idx, rest_val, tgt_idx, tgt_names, i, slot))
    return cols


def _settle_preds(cols, syn2idx, T, params, chunk=256):
    """Settle all columns in chunks; return preds[(item_i, slot)] = chosen synset name (or None)."""
    N = len(syn2idx)
    preds = {}
    pr = {k: params[k] for k in ("alpha", "kappa", "rho", "nexp", "sigma", "iters")}
    for c0 in range(0, len(cols), chunk):
        block = cols[c0:c0 + chunk]
        B = len(block)
        P = np.zeros((N, B), np.float32); Rm = np.zeros((N, B), np.float32)
        for b, (seed, ridx, rval, tidx, tnames, i, slot) in enumerate(block):
            if seed:
                P[seed, b] = 1.0 / len(seed)
            if ridx.size:
                Rm[ridx, b] = rval
        A = _settle_batch(P, Rm, T, **pr)
        for b, (seed, ridx, rval, tidx, tnames, i, slot) in enumerate(block):
            if len(tnames) == 1:
                preds[(i, slot)] = tnames[0]; continue
            if tidx.size == 0:
                preds[(i, slot)] = tnames[0] if tnames else None; continue
            scores = A[tidx, b]
            # map argmax over tgt_idx back to the sense name (tgt_idx follows tnames order, minus OOV)
            present = [nm for nm in tnames if nm in syn2idx]
            preds[(i, slot)] = present[int(np.argmax(scores))]
    return preds


def eval_wic_settle(pairs, syn2idx, T, params, seed=0):
    npairs = len(pairs)
    perm = np.random.default_rng(seed + 7).permutation(npairs)
    cols = _settle_cols(pairs, syn2idx, is_wic=True, perm=perm)
    preds = _settle_preds(cols, syn2idx, T, params)
    correct = np.zeros(npairs, int); twin = np.zeros(npairs, int)
    for i, p in enumerate(pairs):
        s1 = preds.get((i, 0)); s2 = preds.get((i, 1)); s2t = preds.get((i, 2))
        correct[i] = int((s1 == s2) == p["gold"]); twin[i] = int((s1 == s2t) == p["gold"])
    acc, lo, hi = _boot(correct, seed); tacc, _, _ = _boot(twin, seed + 1)
    dpr = (correct - twin).astype(float)
    di = np.random.default_rng(seed + 3).integers(0, npairs, size=(2000, npairs))
    dlo = float(np.percentile(dpr[di].mean(1), 2.5))
    return {"acc": round(acc, 4), "twin_acc": round(tacc, 4), "real_minus_twin": round(float(dpr.mean()), 4),
            "margin_ci_lo": round(dlo, 4), "real_beats_twin": bool(dlo > 0)}


def eval_semcor_settle(inst, syn2idx, T, params, seed=0):
    from nltk.corpus import wordnet as wn
    cols = _settle_cols(inst, syn2idx, is_wic=False)
    preds = _settle_preds(cols, syn2idx, T, params)
    real = np.zeros(len(inst), int); mfs = np.zeros(len(inst), int)
    for k, it in enumerate(inst):
        pred = preds.get((k, 0))
        tn = [s.name() for s in wn.synsets(it["lemma"], pos=_WNPOS.get(it["pos"]))]
        real[k] = int(pred == it["gold"]); mfs[k] = int((tn[0] if tn else None) == it["gold"])
    acc, lo, hi = _boot(real, seed); macc, mlo, mhi = _boot(mfs, seed + 1)
    d = (real - mfs).astype(float)
    di = np.random.default_rng(seed + 3).integers(0, len(inst), size=(2000, len(inst)))
    return {"acc": round(acc, 4), "mfs_acc": round(macc, 4), "real_minus_mfs": round(float(d.mean()), 4),
            "margin_ci_lo": round(float(np.percentile(d[di].mean(1), 2.5)), 4),
            "beats_mfs": bool(float(np.percentile(d[di].mean(1), 2.5)) > 0)}


def run_settle(mode, cache_dir):
    """Can-fail one-variable test: sweep the competition exponent nexp. nexp=1 (competition OFF) must
    reproduce ~PPR (positive control); nexp>1 (competition ON) should sharpen -> beat MFS on SemCor while
    preserving the WiC twin. Everything else fixed (alpha,kappa,rho,sigma)."""
    from nltk.corpus import wordnet as wn
    t0 = time.time()
    syn2idx, T = build_graph("cn", cache_dir)
    N = len(syn2idx)
    dev = _prep(load_wic("dev"))
    inst = _semcor_instances(max_files=(6 if mode == "smoke" else 10))
    if mode == "smoke":
        dev = dev[:80]; inst = inst[:150]
    else:
        dev = dev[:500]; inst = inst[:1200]      # trimmed for tractable nonlinear settling; still powered
    base = dict(alpha=0.85, kappa=1.0, rho=1.0, sigma=0.01, iters=20)
    nexps = [1.0, 2.0] if mode == "smoke" else [1.0, 2.0, 3.0]
    out = {"params_fixed": base, "nexp_grid": {}}
    # (1) the can-fail ONE-VARIABLE test: sweep the competition exponent nexp (nexp=1 == linear/PPR control).
    for ne in nexps:
        params = dict(base, nexp=ne)
        w = eval_wic_settle(dev, syn2idx, T, params); s = eval_semcor_settle(inst, syn2idx, T, params)
        out["nexp_grid"][f"nexp{ne}"] = {"wic_dev": w, "semcor": s}
        print("[settle] nexp=%s DONE: WiC r-t=%s beats=%s | SemCor acc=%s mfs=%s r-mfs=%s (%.0fs)" % (
            ne, w["real_minus_twin"], w["real_beats_twin"], s["acc"], s["mfs_acc"], s["real_minus_mfs"],
            time.time() - t0), flush=True)
    # (2) the LIFG/pMTG control-gain knob: raise context gain kappa + lower freq-rest rho, at HIGH competition,
    # so strong context can OVERRIDE the frequency prior (biased competition; the drill's semantic-control form).
    if mode != "smoke":
        out["control_gain"] = {}
        for kap, rho in [(2.0, 0.3)]:
            params = dict(base, nexp=3.0, kappa=kap, rho=rho)
            w = eval_wic_settle(dev, syn2idx, T, params); s = eval_semcor_settle(inst, syn2idx, T, params)
            out["control_gain"][f"kappa{kap}_rho{rho}_nexp3"] = {"wic_dev": w, "semcor": s}
            print("[settle] control-gain k=%s rho=%s DONE: WiC r-t=%s | SemCor r-mfs=%s (%.0fs)" % (
                kap, rho, w["real_minus_twin"], s["real_minus_mfs"], time.time() - t0), flush=True)
    g = out["nexp_grid"]
    out["headline"] = ("COMPETITIVE SETTLING sweep. nexp=1 (linear/PPR control): WiC r-t=%s, SemCor r-mfs=%s. "
                       "best nexp>1 must sharpen SemCor toward beating MFS while keeping WiC twin cleared." % (
                       g[f"nexp1.0"]["wic_dev"]["real_minus_twin"], g[f"nexp1.0"]["semcor"]["real_minus_mfs"]))
    out["elapsed_s"] = round(time.time() - t0, 2)
    return out


# ================================================================================================
# LEARNING: grow syntagmatic edges from reading (the north star, in miniature). Cross-situational
# co-occurrence (Yu & Smith) over LitBank -> MFS-sense edges kept if count>=MIN_COOC. A LEARNED version
# of SyntagNet's manual edges. Can-fail: the grown graph must help WSD; an info-free SHUFFLED-co-occurrence
# twin (same #edges, random word pairs) must NOT.
# ================================================================================================
LITBANK_DIR = os.path.join(REPO, "data", "litbank", "original")
MIN_COOC = 3


def _learn_cooc_edges(syn2idx, max_sents, shuffle_seed=None):
    """Return (rows, cols, n_edges): learned MFS-sense syntagmatic edges from LitBank co-occurrence.
    shuffle_seed set => info-free twin (rewire the SAME #edges between random synset nodes)."""
    import glob
    import re
    from collections import Counter
    from nltk.corpus import wordnet as wn
    files = sorted(glob.glob(os.path.join(LITBANK_DIR, "*.txt")))
    syn_cache = {}

    def mfs_idx(w):
        if w in syn_cache:
            return syn_cache[w]
        ss = wn.synsets(w, pos="n") or wn.synsets(w, pos="v")
        r = syn2idx.get(ss[0].name()) if ss else None
        syn_cache[w] = r
        return r

    cooc = Counter()
    sents = 0
    for fn in files:
        if sents >= max_sents:
            break
        try:
            txt = open(fn, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        for sent in re.split(r"[.!?]\s+", txt):
            if sents >= max_sents:
                break
            ws = []
            for tok in sent.split():
                w = "".join(c for c in tok.lower() if c.isalpha())
                if len(w) >= 3 and w not in _STOP and mfs_idx(w) is not None:
                    ws.append(w)
            ws = sorted(set(ws))
            for a in range(len(ws)):
                for b in range(a + 1, len(ws)):
                    cooc[(ws[a], ws[b])] += 1
            sents += 1
    kept = [(a, b) for (a, b), c in cooc.items() if c >= MIN_COOC]     # cross-situational gate
    rows, cols = [], []
    for a, b in kept:
        i, j = mfs_idx(a), mfs_idx(b)
        if i is not None and j is not None and i != j:
            rows.append(i); cols.append(j)
    n_edges = len(rows)
    if shuffle_seed is not None and n_edges:                          # info-free twin: rewire to random nodes
        rng = np.random.default_rng(shuffle_seed)
        nodes = np.array(sorted(set(rows + cols)))
        rows = list(rng.choice(nodes, size=n_edges)); cols = list(rng.choice(nodes, size=n_edges))
    return rows, cols, n_edges


def _T_from_extra(base_variant, extra_rows, extra_cols, cache_dir):
    """Row-stochastic T = base graph edges (relations+gloss[+cn]) + extra learned edges. Rebuilds from the
    base edge set so the ONLY difference vs base is the learned edges (clean ablation)."""
    from nltk.corpus import wordnet as wn
    syns = _synsets_ordered(); syn2idx = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    rows, cols = _relation_gloss_edges(syns, syn2idx, gloss_cap=1)
    if "cn" in base_variant.split("_"):
        cr, cc, _ = _conceptnet_edges(syn2idx, cn_cap=1); rows += cr; cols += cc
    rows = rows + list(extra_rows); cols = cols + list(extra_cols)
    A = _symmetrize(rows, cols, n); A.data[:] = 1.0
    return syn2idx, _row_stochastic(A)


def run_learn(mode, cache_dir):
    """Can-fail LEARNING test: does a graph GROWN from reading (LitBank co-occurrence) improve WSD over the
    static base, while an info-free shuffled-co-occurrence twin does NOT?"""
    t0 = time.time()
    max_sents = 400 if mode == "smoke" else 12000
    # derive the base edge set ONCE (relations+glosses), reuse for all three graphs (no 3x re-derivation)
    syns = _synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    base_rows, base_cols = _relation_gloss_edges(syns, s2i, gloss_cap=1)

    def _mkT(extra_r, extra_c):
        A = _symmetrize(base_rows + list(extra_r), base_cols + list(extra_c), n); A.data[:] = 1.0
        return _row_stochastic(A)

    print("[learn] base edges derived (%.0fs); reading corpus..." % (time.time() - t0), flush=True)
    lr, lc, ne = _learn_cooc_edges(s2i, max_sents)           # read corpus ONCE
    print("[learn] learned %d edges from %d sents (%.0fs)" % (ne, max_sents, time.time() - t0), flush=True)
    rng = np.random.default_rng(13)
    nodes = np.array(sorted(set(lr + lc))) if (lr or lc) else np.array([0])
    sr = list(rng.choice(nodes, size=len(lr))); sc = list(rng.choice(nodes, size=len(lc)))
    dev = _prep(load_wic("dev"))
    if mode == "smoke":
        dev = dev[:100]
    out = {"n_learned_edges": ne, "max_sents": max_sents, "min_cooc": MIN_COOC}
    # build + eval ONE graph at a time, freeing each before the next (bounded memory on the shared box)
    for nm, er, ec in [("base_static", [], []), ("learned_from_reading", lr, lc),
                       ("info_free_shuffle_twin", sr, sc)]:
        T = _mkT(er, ec)
        w = eval_wic(dev, s2i, T, "ppr")
        del T
        out[nm] = {"acc": w["acc"], "real_minus_twin": w["real_minus_twin"], "margin_ci": w["margin_ci"],
                   "beats_twin": w["real_beats_twin"]}
        print("[learn] %s: WiC acc=%s r-t=%s beats=%s (%.0fs)" % (nm, w["acc"], w["real_minus_twin"],
              w["real_beats_twin"], time.time() - t0), flush=True)
    b = out["base_static"]["real_minus_twin"]; l = out["learned_from_reading"]["real_minus_twin"]
    s = out["info_free_shuffle_twin"]["real_minus_twin"]
    out["headline"] = ("LEARNED %d edges from reading. margin: base=%s learned=%s shuffle-twin=%s. LEARNING WORKS iff "
                       "learned>base AND learned>shuffle (real co-occurrence structure helps, random does not)." % (ne, b, l, s))
    out["elapsed_s"] = round(time.time() - t0, 2)
    return out


def self_test() -> dict:
    ev = {}
    # competitive settling: nexp=1 spreads (positive control), nexp>1 sharpens the peak (winner-take-all)
    Atoy = _symmetrize([0, 1, 1, 2], [1, 0, 2, 3], 4)
    Ttoy = _row_stochastic(Atoy)
    rest0 = np.zeros(4, np.float32)
    a1 = _settle([0], rest0, Ttoy, 4, nexp=1.0, iters=40)
    a3 = _settle([0], rest0, Ttoy, 4, nexp=3.0, iters=40)
    peak1 = a1.max() / (a1.sum() + 1e-9); peak3 = a3.max() / (a3.sum() + 1e-9)
    assert int(np.argmax(a1)) == 0 and int(np.argmax(a3)) == 0, "settling peaks at the seed"
    assert peak3 > peak1, "higher nexp sharpens the activation (more winner-take-all)"
    ev["settle_sharpens_with_nexp"] = [round(float(peak1), 3), round(float(peak3), 3)]
    # BATCHED settling must exactly match the per-item settle (correctness of the speedup)
    restb = np.zeros((4, 2), np.float32); restb[3, 0] = 0.5; restb[2, 1] = 0.5
    Pb = np.zeros((4, 2), np.float32); Pb[0, 0] = 1.0; Pb[1, 1] = 1.0
    Ab = _settle_batch(Pb, restb, Ttoy, alpha=0.85, kappa=1.0, rho=1.0, nexp=2.0, sigma=0.01, iters=15)
    a_col0 = _settle([0], restb[:, 0], Ttoy, 4, kappa=1.0, rho=1.0, nexp=2.0, sigma=0.01, iters=15)
    assert np.allclose(Ab[:, 0], a_col0, atol=1e-5), "batched settle must equal per-item settle"
    ev["batched_matches_peritem"] = True
    # blend picker: lambda=0 -> prior argmax (MFS); lambda large -> ppr argmax (context)
    ppr_t = np.array([0.1, 0.9]); prior_t = np.array([10.0, 1.0])
    assert _blend_pick(ppr_t, prior_t, 0.0) == 0, "lambda=0 must pick the frequency prior (MFS)"
    assert _blend_pick(ppr_t, prior_t, 50.0) == 1, "lambda->inf must pick the PPR winner (context)"
    ev["blend_selfgates"] = True
    # ConceptNet keep-set excludes polarity predicates
    assert "Antonym" not in _CN_KEEP and "RelatedTo" in _CN_KEEP
    # IC normalization: a specific leaf synset outranks a generic hub
    from nltk.corpus import wordnet as wn
    syns = [wn.synset("entity.n.01"), wn.synset("dog.n.01"), wn.synset("poodle.n.01")]
    s2i = {s.name(): i for i, s in enumerate(syns)}
    icv = _ic_norm(syns, s2i)
    assert icv[s2i["poodle.n.01"]] >= icv[s2i["entity.n.01"]], "specific synset must be >= generic hub in IC"
    ev["ic_specific_ge_generic"] = [round(float(icv[s2i["entity.n.01"]]), 3), round(float(icv[s2i["poodle.n.01"]]), 3)]
    # row-stochastic: rows sum to 1 on a toy graph
    A = _symmetrize([0, 1], [1, 2], 3)
    T = _row_stochastic(A)
    assert abs(float(T.sum(1).max()) - 1.0) < 1e-5, "T rows must sum to 1"
    ev["row_stochastic_ok"] = True
    # PPR (imported) concentrates near the seed
    r = _ppr([0], T, 3)
    ev["ppr_seed_peak"] = round(float(r[0]), 4)
    return ev


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    ap.add_argument("--self-test", dest="selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--semcor", action="store_true", help="second gold: SemCor all-words WSD")
    ap.add_argument("--residual", action="store_true", help="locate the granularity/coverage residual")
    ap.add_argument("--sweep", action="store_true", help="damping sweep on the base graph (dev)")
    ap.add_argument("--combined", action="store_true",
                    help="resting-level PRIOR + spreading activation (Rodd): SemCor vs MFS + WiC twin check")
    ap.add_argument("--blend", action="store_true",
                    help="log-linear blend log P_freq + lambda*log PPR; tune lambda on a DISJOINT SemCor dev split")
    ap.add_argument("--settle", action="store_true",
                    help="competitive attractor settling (lateral inhibition); sweep the competition exponent nexp")
    ap.add_argument("--learn", action="store_true",
                    help="LEARN syntagmatic edges from reading (LitBank co-occurrence); can-fail vs info-free twin")
    ap.add_argument("--max-files", type=int, default=60, help="SemCor files to sample")
    args = ap.parse_args(argv)
    if args.selftest:
        args.mode = "self-test"
    elif args.smoke:
        args.mode = "smoke"
    # LADDER_DATA_DIR lets caches/output go to a session-safe dir (e.g. the scratchpad) OUTSIDE the repo,
    # immune to a concurrent git-clean that deletes untracked data/exp_* (observed nuking a run mid-flight).
    data_base = os.environ.get("LADDER_DATA_DIR", os.path.join(REPO, "data"))
    cache_dir = os.path.join(data_base, f"exp_{ANCHOR}")
    out_dir = os.path.join(data_base, f"exp_{ANCHOR}" + ("_smoke" if args.mode == "smoke" else ""))
    os.makedirs(out_dir, exist_ok=True)

    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2)); print("SELF-TEST PASSED"); return 0

    st = self_test()
    result = {"selftest": st}

    if args.semcor:
        inst = _semcor_instances(max_files=(6 if args.mode == "smoke" else args.max_files))
        inst = inst[:(200 if args.mode == "smoke" else 2500)]      # powered but tractable (1 PPR/instance)
        syn2idx, T = build_graph("base", cache_dir)
        result["semcor_base"] = eval_semcor(inst, syn2idx, T, "ppr")
        syn2idx, T = build_graph("cn", cache_dir)     # cn = the WiC-ladder winner (ConceptNet thematic edges)
        result["semcor_cn"] = eval_semcor(inst, syn2idx, T, "ppr")
        result["semcor_note"] = ("MFS on SemCor is a strong baseline (WordNet sense-1 order is SemCor-derived); "
                                 "reported with that caveat. Polysemous n/v tokens only.")
    elif args.residual:
        dev = _prep(load_wic("dev"))
        if args.mode == "smoke":
            dev = dev[:120]
        syn2idx, T = build_graph("base", cache_dir)
        result["residual_dev"] = residual_analysis(dev, syn2idx, T)
    elif args.sweep:
        dev = _prep(load_wic("dev"))
        if args.mode == "smoke":
            dev = dev[:120]
        syn2idx, T = build_graph("base", cache_dir)
        result["sweep"] = {}
        for d in ([0.75, 0.85] if args.mode == "smoke" else [0.6, 0.75, 0.85, 0.9, 0.95]):
            result["sweep"][f"d{d}"] = eval_wic(dev, syn2idx, T, "ppr", damping=d)
    elif args.combined:
        # Rodd's full model: resting-level frequency PRIOR + context spreading activation.
        inst = _semcor_instances(max_files=(6 if args.mode == "smoke" else args.max_files))
        inst = inst[:(200 if args.mode == "smoke" else 2500)]
        for gv in ("base", "cn"):
            s2i, T = build_graph(gv, cache_dir)
            result[f"semcor_{gv}_ppr"] = eval_semcor(inst, s2i, T, "ppr")
            result[f"semcor_{gv}_prior_ppr"] = eval_semcor(inst, s2i, T, "prior_ppr")
        dev = _prep(load_wic("dev"))
        if args.mode == "smoke":
            dev = dev[:120]
        s2i, T = build_graph("cn", cache_dir)
        result["wic_cn_ppr_dev"] = eval_wic(dev, s2i, T, "ppr")            # prior is common-mode on the twin
        result["wic_cn_prior_ppr_dev"] = eval_wic(dev, s2i, T, "prior_ppr")
    elif args.blend:
        result["blend"] = run_blend(args.mode, cache_dir)
    elif args.settle:
        result["settle"] = run_settle(args.mode, cache_dir)
    elif args.learn:
        result["learn"] = run_learn(args.mode, cache_dir)
    else:
        result["ladder"] = run_ladder(args.mode, cache_dir)

    metrics = {"anchor_name": ANCHOR, "run_mode": args.mode, "verdict": "MEASURED",
               "ts_iso": datetime.now(timezone.utc).isoformat(), "result": result}
    tag = ("semcor" if args.semcor else "residual" if args.residual else "sweep" if args.sweep
           else "combined" if args.combined else "blend" if args.blend else "settle" if args.settle
           else "learn" if args.learn else "ladder")
    # stdout FIRST -> captured to the (safe) task-stdout file even if a concurrent cleanup nukes out_dir.
    print(json.dumps(result, indent=2, default=str))
    try:
        os.makedirs(out_dir, exist_ok=True)             # re-create if a concurrent git-clean removed it
        tmp = os.path.join(out_dir, f"metrics_{tag}.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, default=str)
        os.replace(tmp, os.path.join(out_dir, f"metrics_{tag}.json"))
    except Exception as e:
        print("WARN: metrics file write failed (concurrent dir deletion?): %r" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
