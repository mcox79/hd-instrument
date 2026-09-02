"""exp_learned_graph_cls_grow_v1 -- GROW the grounded semantic graph FROM READING by brain-faithful
consolidation, and test whether the grown graph improves SETTLING-WSD on HELD-OUT MODERN text over the
STATIC WordNet++ graph. The WRITE/LEARN side of the meaning graph (north-star follow-on to
promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ).

WHY THIS IS NOT THE NAIVE NEGATIVE. The parent cell's _learn_cooc_edges was a clean NEGATIVE. It failed
on TWO levers this cell fixes, both independently proven elsewhere on disk:
  (1) RAW co-occurrence counts -> use PPMI SURPRISE-WEIGHTING. does_learning_from_reading_deserve_to_
      continue [SOLVED, EXCELLENT] showed PPMI is THE lever (RAW 0.04/0.01/0.23 -> PPMI 0.26/0.13/0.63,
      still climbing); it is the brain's N400 surprise-gated encoding (Rabovsky 2018). We MEASURE its
      transfer to WSD (that SOLVED's own caveat: the PPMI win did NOT transfer to a different scorer).
  (2) MFS (sense-0) disambiguation of the edge endpoints -> CONTEXT-DISAMBIGUATE via the current graph's
      own spreading activation (the settling read feeds the write). The parent located this as the fix.

MECHANISM (brain-faithful; PINNED tags per LEARNED_GRAPH_brain_mechanism_spec.md):
  - CROSS-SITUATIONAL EM (Yu & Smith 2007 [PINNED]): E-step = soft sense responsibilities from the current
    graph's contextual pre-activation (one PPR per SENTENCE = fast contextual priming, not per-token
    deliberation); M-step = accumulate soft synset x synset co-occurrence, PPMI-weight, threshold.
  - PRECISION-GATE (relabelled after fidelity audit): an edge whose endpoints are ALREADY graph neighbours
    (schema-consistent) integrates at full rate; a NOVEL pairing is slow/tentative (needs more confirmations,
    down-weighted). HONEST NOTE: additive PPMI counts are inherently non-forgetting, so this gate's real job
    is NOT CLS anti-interference (there is none to fight) -- it is PRECISION / spurious-edge control, the
    LIFG/pMTG semantic-control function (Jefferies; Thompson-Schill). Tested on/off (ppmi_ctx vs
    ppmi_ctx_nogate) to see whether refusing novel edges HELPS or STARVES useful new structure.
  - Surprise-weighted additive PPMI is read-forever / non-forgetting (the CLS read-forever property, McClelland 1995).

ARMS (each a clean ablation; the twin MUST lose):
  ppmi_ctx  : context-disambiguated soft senses + PPMI + schema-gate         (the faithful arm)
  raw_ctx   : context-disambiguated soft senses + RAW counts                 (isolates the PPMI lever)
  ppmi_mfs  : PPMI but HARD MFS (sense-0) endpoints                          (isolates context-disambig)
  shuffle   : ppmi_ctx edges rewired to random synset nodes (info-free twin) (MUST lose CI-sep)

BAR: grown graph beats STATIC cn_syn CI-separated on held-out WiC-test twin-margin AND/OR Raganato ALL,
the shuffle twin loses, and NO degradation on already-correct items (anti-interference). A rigorous
located NEGATIVE (which lever fails and why) is a full PASS.

Glass-box, LM-FREE at inference, deterministic, ASCII. Reuses the parent cell's proven primitives (does
NOT reimplement PPR/graph/eval). Resumable (every expensive stage checkpointed; skip-on-rerun). Heavy ->
REMOTE (this box kills heavy runs ~250s); smoke runs inline.

# KB_REFERENT: data/corpora/simplewiki/simplewiki_clean_v1.txt
# KB_REFERENT: data/datasets/conceptnet5_en_100k.jsonl
# KB_REFERENT: data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
# KB_REFERENT: data/wsdeval/WSD_Evaluation_Framework/Evaluation_Datasets/ALL/ALL.data.xml
# KB_REFERENT: data/wsdeval/WSD_Evaluation_Framework/Evaluation_Datasets/ALL/ALL.gold.key.txt
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "4")

import argparse
import json
import math
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_grounded_semantic_graph_ladder_wsd_v1 as M
from tools.load_wsd_benchmarks import load_wic

ANCHOR = "learned_graph_cls_grow_v1"
SIMPLEWIKI = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")
RAGANATO = os.path.join(REPO, "data", "wsdeval", "WSD_Evaluation_Framework", "Evaluation_Datasets", "ALL")

# --- growth hyperparameters (OUR-INVENTION-UNDER-TEST unless tagged) ---
MIN_COOC = 3            # cross-situational evidence gate (Yu & Smith): #sentences supporting an edge [PINNED kind]
K_CONFIRM_NOVEL = 6     # a schema-INCONSISTENT (novel) pairing needs this many confirmations (slow cortical rate)
GAMMA_SLOW = 0.5        # down-weight for schema-inconsistent edges (fast/slow rate ratio; magnitude swept)
TOPK_SENSE = 2          # soft responsibilities kept per token (continuous-space, not hard argmax)
PPMI_SMOOTH = 0.75      # Levy/Goldberg context-marginal smoothing
MAX_SENSES = 6          # cap candidate senses per word (bound cost)
COOC_WINDOW = int(os.environ.get("COOC_WINDOW", "4"))  # co-occur only within +/-window positions. SMALL window =
                        # collocational/SYNTACTIC (sense-diagnostic); WHOLE-SENTENCE bag = topic (frequency-biased,
                        # the context_conditioned_sense_selection HARD_FAIL). Research: syntactic/selectional context
                        # is the frequency-INDEPENDENT sense signal (Lin; Wilks). A cheap proxy for it, no parser.
ESTEP_ITERS = int(os.environ.get("ESTEP_ITERS", "6"))  # E-step PPR iters = FAST contextual priming (1-2 hop
                        # feedforward sweep, not full settling). Cheap + faithful; eval keeps full PPR_ITERS.
ESTEP_LAM = float(os.environ.get("ESTEP_LAM", "2.0"))  # Reordered Access (Duffy/Rayner): dominance persists,
                        # context reorders. E-step responsibility = log(dominance) + ESTEP_LAM*log(context).
                        # CONTEXT-DOMINATED (lam=2): the prior_swamps_the_channel REFUTATION showed equal
                        # dominance+context blending SWAMPS subordinate senses -- keep dominance a weak tiebreaker.
_POS_ALL = {"NOUN": "n", "VERB": "v", "ADJ": "a", "ADV": "r"}


# ============================================================================ checkpoint dir
def _ck():
    base = os.environ.get("LADDER_DATA_DIR", os.path.join(REPO, "data"))
    d = os.path.join(base, "exp_" + ANCHOR)
    os.makedirs(d, exist_ok=True)
    return d


def _save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


# ============================================================================ base graph (static floor)
def _base_adjacency(variant, s2i, syns, n, ck):
    """Static base adjacency A (unit weights, symmetric csr). variant='cn_syn' = the strongest static
    graph (the FLOOR the grown graph must beat). Cached (relations+glosses+ConceptNet+SyntagNet)."""
    p = os.path.join(ck, "base_adj_%s.npz" % variant)
    if os.path.exists(p):
        z = np.load(p)
        return sp.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=(n, n))
    parts = variant.split("_")
    rows, cols = M._relation_gloss_edges(syns, s2i, gloss_cap=1)
    if "cn" in parts:
        cr, cc, _ = M._conceptnet_edges(s2i, cn_cap=1); rows += cr; cols += cc
    if "syn" in parts:
        sr, sc, _ = M._syntagnet_edges(s2i); rows += sr; cols += sc
    A = M._symmetrize(rows, cols, n); A.data[:] = 1.0; A = A.tocsr()
    np.savez(p + ".b", data=A.data, indices=A.indices, indptr=A.indptr); os.replace(p + ".b.npz", p)
    return A


# ============================================================================ corpus reader
def _corpus_sentences(path, max_sents):
    """Yield ORDER-PRESERVED content-word lists (lowercase, stopworded, len>=3). Order matters: small-window
    co-occurrence approximates SYNTACTIC/collocational context (sense-diagnostic), not whole-sentence topic."""
    import re
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if len(s) < 12:
                continue
            ws = [w for w in (re.sub(r"[^a-z]", "", t.lower()) for t in s.split())
                  if len(w) >= 3 and w not in M._STOP]
            if len(ws) >= 3:
                out.append(ws)
                if len(out) >= max_sents:
                    break
    return out


# ============================================================================ E-step: soft sense responsibilities
_WS_CACHE = {}      # word -> [(name, idx)] ; WordNet lookups dominate growth time -> cache across sentences


def _word_senses(wn, w, s2i):
    """Candidate (name, idx) senses of w present in the graph, capped. Cached (WordNet access is the bottleneck)."""
    c = _WS_CACHE.get(w)
    if c is not None:
        return c
    out = []
    for s in wn.synsets(w):
        j = s2i.get(s.name())
        if j is not None:
            out.append((s.name(), j))
        if len(out) >= MAX_SENSES:
            break
    _WS_CACHE[w] = out
    return out


_WN_ALL = {}      # word -> ALL (name, idx) senses in the graph; cached (eval wn.synsets lookups dominate)


def _all_senses(wn, w, s2i):
    c = _WN_ALL.get(w)
    if c is not None:
        return c
    out = []
    for gs in wn.synsets(w):
        j = s2i.get(gs.name())
        if j is not None:
            out.append((gs.name(), j))
    _WN_ALL[w] = out
    return out


def _fast_coh(wn, ctxw, s2i, T, n, tn):
    """PPR context coherence over target senses tn -- byte-identical to M._sense_ppr but with wn.synsets
    lookups CACHED (they dominate eval time ~10ms each). Excludes the target's own senses from the seed."""
    tset = set(tn); seed = []
    for w in ctxw:
        for nm, j in _all_senses(wn, w, s2i):
            if nm not in tset:
                seed.append(j)
    seed = sorted(set(seed))
    if not seed:
        return None
    r = M._ppr(seed, T, n)
    return np.array([float(r[s2i[nm]]) if nm in s2i else 0.0 for nm in tn])


_TGT_CACHE = {}      # (lemma, wnpos) -> (tgt, tn, prior); target wn.synsets + _sense_prior are eval-time hot spots


def _target_senses(wn, lemma, wnpos):
    key = (lemma, wnpos)
    c = _TGT_CACHE.get(key)
    if c is not None:
        return c
    tgt = wn.synsets(lemma, pos=wnpos)
    if wnpos == "a":
        tgt = tgt + wn.synsets(lemma, pos="s")
    tn = [x.name() for x in tgt]
    prior = M._sense_prior(lemma, tgt)
    _TGT_CACHE[key] = (tgt, tn, prior)
    return tgt, tn, prior


def _sentence_resp(wn, words, s2i, T, n, disambig, topk=TOPK_SENSE):
    """Return {word -> [(syn_idx, weight)]}: soft sense responsibilities.
    disambig='ctx': ONE PPR per sentence seeded on ALL candidate senses = contextual pre-activation; read
                    out each word's senses' settled mass, keep top-k, normalize (context-disambiguated).
    disambig='mfs': hard sense-0 (the parent's naive endpoint; the ablation)."""
    wsen = {}
    seed = []
    for w in words:
        sv = _word_senses(wn, w, s2i)
        if sv:
            wsen[w] = sv
            seed += [j for _, j in sv]
    if not wsen:
        return {}
    if disambig == "mfs":
        return {w: [(sv[0][1], 1.0)] for w, sv in wsen.items()}
    r = M._ppr(sorted(set(seed)), T, n, iters=ESTEP_ITERS) if seed else None
    resp = {}
    for w, sv in wsen.items():
        dom = np.array([1.0 / (1.0 + k) for k in range(len(sv))])   # dominance = WordNet freq-ranked resting level
        if r is not None:
            pp = np.array([float(r[j]) for _, j in sv], dtype=np.float64)
        else:
            pp = np.zeros(len(sv))
        s = pp.sum()
        if s > 0:
            pp = pp / s                                       # Reordered Access: dominance persists + context reorders
            logsc = np.log(dom) + ESTEP_LAM * np.log(pp + 1e-6)
            vals = np.exp(logsc - logsc.max())
        else:
            vals = dom                                        # no context signal -> pure dominance
        order = np.argsort(vals)[::-1][:topk]
        sel = [(sv[o][1], float(vals[o])) for o in order]
        tot = sum(v for _, v in sel) or 1.0
        resp[w] = [(j, v / tot) for j, v in sel]
    return resp


# ============================================================================ M-step: accumulate + PPMI
def _accumulate(sentences, wn, s2i, T, n, disambig, window=COOC_WINDOW, log_every=2000, t0=None):
    """Accumulate soft synset x synset co-occurrence within +/-window positions (collocational/syntactic
    locality, not whole-sentence topic). cooc = soft mass, supp = #co-occurrences (cross-situational gate),
    marg = co-occurrence marginal (row sums, standard PPMI). One PPR per sentence for disambig='ctx'."""
    cooc = defaultdict(float)
    supp = defaultdict(int)
    for si, words in enumerate(sentences):
        resp = _sentence_resp(wn, words, s2i, T, n, disambig)
        L = len(words)
        for i_pos in range(L):
            ra = resp.get(words[i_pos])
            if not ra:
                continue
            for j_pos in range(i_pos + 1, min(i_pos + 1 + window, L)):     # windowed = local/syntactic
                rb = resp.get(words[j_pos])
                if not rb:
                    continue
                for ia, va in ra:
                    for ib, vb in rb:
                        if ia == ib:
                            continue
                        key = (ia, ib) if ia < ib else (ib, ia)
                        cooc[key] += va * vb
                        supp[key] += 1
        if t0 is not None and (si % log_every == 0):
            print("[grow:%s] sent %d/%d  pairs=%d  (%.0fs)" % (disambig, si, len(sentences), len(cooc),
                  time.time() - t0), flush=True)
    marg = defaultdict(float)                                              # co-occurrence marginal (row sums)
    for (i, j), c in cooc.items():
        marg[i] += c; marg[j] += c
    return cooc, supp, marg


def _ppmi_edges(cooc, supp, marg, weighting, A_base, schema_gate):
    """Turn accumulated co-occurrence into learned WEIGHTED edges.
      weighting='ppmi' : positive PMI with Levy/Goldberg 0.75 context smoothing (the surprise lever).
      weighting='raw'  : edge weight = raw support count (the RAW ablation -- no surprise weighting).
    Cross-situational gate: supp >= MIN_COOC. Schema-gate: schema-inconsistent (non-neighbour) pairs need
    supp >= K_CONFIRM_NOVEL and are down-weighted by GAMMA_SLOW (slow cortical rate)."""
    Npair = sum(cooc.values()) or 1.0
    Nmarg = sum(marg.values()) or 1.0
    marg_sm = {i: (m ** PPMI_SMOOTH) for i, m in marg.items()}
    Nmarg_sm = sum(marg_sm.values()) or 1.0
    mbar = (Nmarg / len(marg)) if marg else 1.0               # mean activity (BCM homeostatic reference)
    rows, cols, wts = [], [], []
    n_novel = 0; n_consistent = 0
    for (i, j), c in cooc.items():
        if supp[(i, j)] < MIN_COOC:
            continue
        consistent = (A_base[i, j] != 0)
        if schema_gate and not consistent:
            if supp[(i, j)] < K_CONFIRM_NOVEL:
                continue
        if weighting in ("ppmi", "bcm"):
            pij = c / Npair
            pi = marg.get(i, 0.0) / Nmarg
            pj = marg_sm.get(j, 0.0) / Nmarg_sm
            if pij <= 0 or pi <= 0 or pj <= 0:
                continue
            w = math.log(pij / (pi * pj))
            if w <= 0:                                        # positive PMI only
                continue
            if weighting == "bcm":
                # HOMEOSTATIC (BCM sliding threshold / synaptic scaling): depress edges to HIGH-activity
                # (frequent) synsets, so growth strengthens LOW-activity (subordinate) senses' edges instead
                # of rich-get-richer. h(x) = mbar/(activity(x)+mbar) in (0,1]; low activity -> ~1, high -> small.
                w *= (mbar / (marg.get(i, 0.0) + mbar)) * (mbar / (marg.get(j, 0.0) + mbar))
        else:                                                 # raw
            w = float(supp[(i, j)])
        if schema_gate and not consistent:
            w *= GAMMA_SLOW; n_novel += 1
        else:
            n_consistent += 1
        rows.append(i); cols.append(j); wts.append(w)
    return rows, cols, wts, {"n_consistent": n_consistent, "n_novel": n_novel}


def _shuffle_edges(rows, cols, wts, seed=13):
    """Info-free twin: rewire the SAME #edges + SAME weights to random nodes drawn from the SAME node set."""
    rng = np.random.default_rng(seed)
    nodes = np.array(sorted(set(rows + cols))) if rows else np.array([0])
    sr = list(rng.choice(nodes, size=len(rows)))
    sc = list(rng.choice(nodes, size=len(cols)))
    return sr, sc, list(wts)


def _grown_T(A_base, rows, cols, wts, edge_scale, n):
    """Row-stochastic T from base (unit) + learned (weighted*scale) edges, symmetric. Duplicates summed."""
    if rows:
        lr = np.array(rows + cols, np.int64); lc = np.array(cols + rows, np.int64)
        lw = np.array(list(wts) + list(wts), np.float64) * edge_scale
        L = sp.csr_matrix((lw, (lr, lc)), shape=(n, n))
        A = (A_base + L).tocsr()
    else:
        A = A_base.tocsr()
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1.0
    return A.multiply(1.0 / deg[:, None]).tocsr()


# ============================================================================ Raganato ALL eval
def _key_to_syn(wn, k):
    try:
        return wn.lemma_from_key(k).synset().name()
    except Exception:
        return None


def _load_raganato(wn):
    gold = {}
    for line in open(os.path.join(RAGANATO, "ALL.gold.key.txt"), encoding="utf-8"):
        p = line.split()
        if len(p) >= 2:
            gold[p[0]] = set(filter(None, (_key_to_syn(wn, k) for k in p[1:])))
    items = []
    tree = ET.parse(os.path.join(RAGANATO, "ALL.data.xml"))
    for sent in tree.getroot().iter("sentence"):
        toks = list(sent)
        ctx = []
        for el in toks:
            lem = (el.get("lemma") or "").lower()
            w = "".join(c for c in lem if c.isalpha())
            if len(w) >= 3 and w not in M._STOP:
                ctx.append(w)
        for el in toks:
            if el.tag != "instance":
                continue
            iid = el.get("id"); lemma = (el.get("lemma") or "").lower()
            wnpos = _POS_ALL.get(el.get("pos"))
            g = gold.get(iid, set())
            if wnpos and g:
                items.append((iid, lemma, wnpos, ctx, g))
    return items


def eval_raganato(items, s2i, T, n, lam=1.0, touched=None):
    """Per-instance: blend log P_freq + lam*log PPR over candidate senses; accuracy vs MFS. Returns
    ok, mfs (per-item correct arrays, for retention) + touched mask (item's target has a learned edge)."""
    from nltk.corpus import wordnet as wn
    ok = np.zeros(len(items), np.int32); mfs = np.zeros(len(items), np.int32)
    tmask = np.zeros(len(items), bool)
    for k, (iid, lemma, wnpos, ctx, g) in enumerate(items):
        tgt, tn, prior = _target_senses(wn, lemma, wnpos)
        if not tn:
            continue
        mfs[k] = int(tn[0] in g)
        ctxw = [w for w in ctx if w != lemma]
        ppr = _fast_coh(wn, ctxw, s2i, T, n, tn)
        j = M._blend_pick(ppr, prior, lam)
        ok[k] = int(tn[j] in g)
        if touched:
            tmask[k] = any(s2i.get(nm) in touched for nm in tn)
    return ok, mfs, tmask


# ============================================================================ BRAIN-FOUNDATIONAL readout:
# reordered-access (freq prior + graph context coherence) + SEMANTIC CONTROL (LIFG conflict-gated suppression
# of the dominant sense). semantic_control is the LANDED, VALIDATED organ from context_override_of_the_
# frequency_prior (AUC 0.79 trigger). We do NOT rebuild it -- we test whether the GROWN graph gives it a
# BETTER context-coherence signal for SUBORDINATE-sense recovery than the static graph (its own docstring:
# "a genuinely new orthogonal directional signal is the forward lever"). Deep syntax is a KNOWN NEGATIVE
# (+0.007, context_override) -- local collocation (our windowed edges) is the lever.
def eval_raganato_control(items, s2i, T, n, lam=1.0, gamma=1.0, quantile=0.80):
    """Reordered-access + semantic-control read; coherence = THIS graph's PPR context activation. Returns
    (ok, mfs, n_fired). theta calibrated GOLD-BLIND to the 80th pct of the conflict distribution."""
    from nltk.corpus import wordnet as wn
    from hdlab.semantic_control import SemanticControl, conflict as _conflict
    recs = []; conflicts = []
    ok = np.zeros(len(items), np.int32); mfs = np.zeros(len(items), np.int32)
    for k, (iid, lemma, wnpos, ctx, g) in enumerate(items):
        tgt = wn.synsets(lemma, pos=wnpos)
        if wnpos == "a":
            tgt = tgt + wn.synsets(lemma, pos="s")
        tn = [x.name() for x in tgt]
        if not tn:
            recs.append(None); continue
        mfs[k] = int(tn[0] in g)
        prior = M._sense_prior(lemma, tgt); prior_idx = int(np.argmax(prior))
        if len(tn) < 2:
            recs.append(("mono", tn, g, prior_idx, None, None, None)); continue
        ctxw = [w for w in ctx if w != lemma]
        coh = M._sense_ppr(wn, lemma, wnpos, ctxw, s2i, T, n, tgt, tn)
        if coh is None:
            recs.append(("nocoh", tn, g, prior_idx, None, None, None)); continue
        coh = np.asarray(coh, float); cs = coh.sum(); cohn = coh / cs if cs > 0 else coh
        scores = np.log(prior + 0.1) + lam * np.log(cohn + 1e-6)     # reordered access
        cfl = _conflict(cohn, prior_idx); conflicts.append(cfl)
        recs.append(("full", tn, g, prior_idx, scores, cohn, cfl))
    sc = SemanticControl(gamma=gamma).calibrate(conflicts, quantile)
    fired = 0
    for k, r in enumerate(recs):
        if r is None:
            continue
        typ, tn, g, pidx, scores, cohn, cfl = r
        if typ in ("mono", "nocoh"):
            ok[k] = int(tn[pidx] in g); continue
        idx, _ = sc.resolve(scores, cohn, pidx); ok[k] = int(tn[idx] in g)
        fired += int(sc.fires(cfl))
    return ok, mfs, fired


def _load_ctx_edges(ck, A_base, max_sents, schema_gate=True, weighting="ppmi"):
    """Rebuild learned edges from the cached accumulation (cheap; the PPR accumulation is the expensive
    stage and it is checkpointed). weighting in {ppmi, bcm (homeostatic), raw}."""
    accp = os.path.join(ck, "acc_ctx_%d.npz" % max_sents)
    z = np.load(accp, allow_pickle=True)
    cooc = dict(zip((tuple(int(x) for x in k) for k in z["ck"]), z["cv"].tolist()))
    supp = dict(zip((tuple(int(x) for x in k) for k in z["ck"]), z["sv"].tolist()))
    marg = dict(zip(z["mk"].tolist(), z["mv"].tolist()))
    return _ppmi_edges(cooc, supp, marg, weighting, A_base, schema_gate)


def run_inhibitory(cache_dir, max_sents, base_variant, n_rag, lam, gamma):
    """THE brain-foundational readout test: does the GROWN graph's context-coherence let semantic_control
    recover MORE subordinate senses than the STATIC graph? Reuses the cached ppmi_ctx accumulation."""
    from nltk.corpus import wordnet as wn
    t0 = time.time(); ck = _ck()
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    A_base = _base_adjacency(base_variant, s2i, syns, n, ck)
    T_static = M._row_stochastic(A_base.copy())
    rr, cc, ww, estat = _load_ctx_edges(ck, A_base, max_sents)
    T_grown = _grown_T(A_base, rr, cc, ww, 2.0, n)
    print("[inhib] static + grown(%d edges) built (%.0fs)" % (len(rr), time.time() - t0), flush=True)
    rag = _load_raganato(wn)
    if n_rag and len(rag) > n_rag:
        idx = np.random.default_rng(0).permutation(len(rag))[:n_rag]; rag = [rag[i] for i in sorted(idx)]
    out = {"n_raganato": len(rag), "edge_stat": estat, "lam": lam, "gamma": gamma, "max_sents": max_sents}
    # argmax (no control) vs semantic-control, static vs grown coherence
    ok_sa, mfs, _ = eval_raganato(rag, s2i, T_static, n)          # static, no control (reordered-access argmax)
    ok_ga, _, _ = eval_raganato(rag, s2i, T_grown, n)             # grown,  no control
    ok_sc, _, f_s = eval_raganato_control(rag, s2i, T_static, n, lam, gamma)   # static + control
    ok_gc, _, f_g = eval_raganato_control(rag, s2i, T_grown, n, lam, gamma)    # grown  + control
    hard = (mfs == 0); nh = int(hard.sum())
    def blk(ok):
        return {"acc": round(float(ok.mean()), 4), "subordinate_acc": round(float(ok[hard].mean()), 4) if nh else None}
    out["n_subordinate"] = nh
    out["static_argmax"] = blk(ok_sa); out["grown_argmax"] = blk(ok_ga)
    out["static_control"] = dict(blk(ok_sc), fired=f_s); out["grown_control"] = dict(blk(ok_gc), fired=f_g)
    # the decisive contrasts on the SUBORDINATE population (where MFS=0, prior_swamps' wall)
    if nh:
        for name, a, b in [("control_vs_argmax_static", ok_sc, ok_sa),
                           ("control_vs_argmax_grown", ok_gc, ok_ga),
                           ("grown_vs_static_control", ok_gc, ok_sc)]:
            d, lo, hi = _boot_margin(a[hard], b[hard], 21)
            out[name] = {"delta_subordinate": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "beats": bool(lo > 0)}
    out["headline"] = ("SUBORDINATE (n=%d): static-argmax %s -> +control %s; grown-argmax %s -> +control %s. "
                       "grown-vs-static (control): %s" % (
                       nh, out["static_argmax"]["subordinate_acc"], out["static_control"]["subordinate_acc"],
                       out["grown_argmax"]["subordinate_acc"], out["grown_control"]["subordinate_acc"],
                       out.get("grown_vs_static_control", {}).get("delta_subordinate")))
    out["elapsed_s"] = round(time.time() - t0, 2)
    _save_json(os.path.join(ck, "result_inhibitory_%s_%d.json" % (base_variant, max_sents)), out)
    return out


def _boot_margin(a, b, seed):
    d = (a.astype(float) - b.astype(float))
    idx = np.random.default_rng(seed).integers(0, len(d), size=(2000, len(d)))
    m = d[idx].mean(1)
    return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


# ============================================================================ growth driver (one arm)
def grow_arm(arm, sentences, wn, s2i, T_static, n, A_base, ck, edge_scale, schema_gate, t0):
    """Produce learned edges for an arm, checkpointed. ctx arms share one accumulation pass."""
    disambig = "mfs" if arm == "ppmi_mfs" else "ctx"
    accp = os.path.join(ck, "acc_%s_%d.npz" % (disambig, len(sentences)))
    if os.path.exists(accp):
        z = np.load(accp, allow_pickle=True)
        cooc = dict(zip(map(tuple, z["ck"]), z["cv"])); supp = dict(zip(map(tuple, z["ck"]), z["sv"]))
        marg = dict(zip(z["mk"].tolist(), z["mv"].tolist()))
        print("[grow:%s] accumulation loaded (%d pairs) (%.0fs)" % (disambig, len(cooc), time.time() - t0), flush=True)
    else:
        cooc, supp, marg = _accumulate(sentences, wn, s2i, T_static, n, disambig, t0=t0)
        ck_keys = np.array(list(cooc.keys()), np.int64) if cooc else np.zeros((0, 2), np.int64)
        np.savez(accp + ".b", ck=ck_keys, cv=np.array(list(cooc.values())),
                 sv=np.array([supp[k] for k in cooc.keys()]),
                 mk=np.array(list(marg.keys()), np.int64), mv=np.array(list(marg.values())))
        os.replace(accp + ".b.npz", accp)
        print("[grow:%s] accumulated %d pairs (%.0fs)" % (disambig, len(cooc), time.time() - t0), flush=True)
    weighting = "raw" if arm == "raw_ctx" else "ppmi"
    rows, cols, wts, stat = _ppmi_edges(cooc, supp, marg, weighting, A_base, schema_gate)
    return rows, cols, wts, stat


# ============================================================================ modes
def run_smoke_or_full(mode, cache_dir, arms, edge_scale, schema_gate, eval_which, max_sents, n_wic, n_rag,
                      base_variant="cn_syn"):
    from nltk.corpus import wordnet as wn
    t0 = time.time()
    ck = _ck()
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    A_base = _base_adjacency(base_variant, s2i, syns, n, ck)
    T_static = M._row_stochastic(A_base.copy())
    print("[grow] base %s: %d nodes, %d nnz (%.0fs)" % (base_variant, n, A_base.nnz, time.time() - t0), flush=True)
    sentences = _corpus_sentences(SIMPLEWIKI, max_sents)
    print("[grow] corpus: %d sentences (max=%d) (%.0fs)" % (len(sentences), max_sents, time.time() - t0), flush=True)

    dev = M._prep(load_wic("dev"))[:n_wic]; test = M._prep(load_wic("test"))
    if mode == "smoke":
        test = test[:n_wic]
    rag = _load_raganato(wn) if eval_which in ("wsd_all", "both") else []
    if n_rag and len(rag) > n_rag:
        idx = np.random.default_rng(0).permutation(len(rag))[:n_rag]; rag = [rag[i] for i in sorted(idx)]

    out = {"mode": mode, "base_variant": base_variant, "edge_scale": edge_scale,
           "schema_gate": schema_gate, "max_sents": len(sentences),
           "n_wic_dev": len(dev), "n_wic_test": len(test), "n_raganato": len(rag),
           "params": {"MIN_COOC": MIN_COOC, "K_CONFIRM_NOVEL": K_CONFIRM_NOVEL, "GAMMA_SLOW": GAMMA_SLOW,
                      "TOPK_SENSE": TOPK_SENSE, "PPMI_SMOOTH": PPMI_SMOOTH}, "arms": {}}

    # STATIC baseline (the floor) -- cached (resumable) -------------------------------------------
    stat_p = os.path.join(ck, "static_%s_d%d_t%d_r%d.json" % (base_variant, len(dev), len(test), len(rag)))
    rag_static_ok = None
    rag_mfs_arr = None
    if os.path.exists(stat_p):
        sd = json.load(open(stat_p))
        for kk in ("static_wic_dev", "static_wic_test", "static_raganato"):
            if kk in sd:
                out[kk] = sd[kk]
        if sd.get("rag_static_ok") is not None:
            rag_static_ok = np.array(sd["rag_static_ok"], np.int32)
        if sd.get("rag_mfs") is not None:
            rag_mfs_arr = np.array(sd["rag_mfs"], np.int32)
        print("[grow] STATIC loaded from cache (%.0fs)" % (time.time() - t0), flush=True)
    else:
        sd = {}
        w_static = M.eval_wic(dev, s2i, T_static, "ppr")
        out["static_wic_dev"] = sd["static_wic_dev"] = {
            "acc": w_static["acc"], "real_minus_twin": w_static["real_minus_twin"],
            "margin_ci": w_static["margin_ci"], "beats_twin": w_static["real_beats_twin"]}
        if test:
            w_static_t = M.eval_wic(test, s2i, T_static, "ppr")
            out["static_wic_test"] = sd["static_wic_test"] = {
                "acc": w_static_t["acc"], "real_minus_twin": w_static_t["real_minus_twin"],
                "margin_ci": w_static_t["margin_ci"], "beats_twin": w_static_t["real_beats_twin"]}
        if rag:
            rag_static_ok, rag_mfs, _ = eval_raganato(rag, s2i, T_static, n)
            rag_mfs_arr = rag_mfs
            rs, rlo, rhi = _boot_margin(rag_static_ok, rag_mfs, 11)
            out["static_raganato"] = sd["static_raganato"] = {
                "acc": round(float(rag_static_ok.mean()), 4), "mfs": round(float(rag_mfs.mean()), 4),
                "acc_minus_mfs": round(rs, 4), "margin_ci": [round(rlo, 4), round(rhi, 4)]}
            sd["rag_static_ok"] = rag_static_ok.tolist()
            sd["rag_mfs"] = rag_mfs.tolist()
        _save_json(stat_p, sd)
        print("[grow] STATIC computed (%.0fs)" % (time.time() - t0), flush=True)

    # GROWN arms -- edges recomputed cheaply each run; EVAL cached per arm (resumable) ------------
    ctx_edges = None
    for arm in arms:
        if arm == "shuffle":
            if ctx_edges is None:
                continue
            rr, cc, ww = _shuffle_edges(*ctx_edges); stat = {"twin": True}
        else:
            arm_gate = schema_gate and not arm.endswith("_nogate")   # precision-gate on/off per arm
            base_arm = arm[:-7] if arm.endswith("_nogate") else arm
            rr, cc, ww, stat = grow_arm(base_arm, sentences, wn, s2i, T_static, n, A_base, ck, edge_scale, arm_gate, t0)
            if arm == "ppmi_ctx":
                ctx_edges = (rr, cc, ww)
        arm_p = os.path.join(ck, "armrec_%s_%s_%d.json" % (arm, base_variant, len(sentences)))
        if os.path.exists(arm_p):
            out["arms"][arm] = json.load(open(arm_p))
            print("[grow] ARM %-13s cached (edges=%d) (%.0fs)" % (arm, len(rr), time.time() - t0), flush=True)
            continue
        T_g = _grown_T(A_base, rr, cc, ww, edge_scale, n)
        rec = {"n_edges": len(rr), "edge_stat": stat}
        w_g = M.eval_wic(dev, s2i, T_g, "ppr")
        rec["wic_dev"] = {"acc": w_g["acc"], "real_minus_twin": w_g["real_minus_twin"],
                          "margin_ci": w_g["margin_ci"], "beats_twin": w_g["real_beats_twin"]}
        if test and arm in ("ppmi_ctx", "ppmi_ctx_nogate", "shuffle"):
            w_gt = M.eval_wic(test, s2i, T_g, "ppr")
            rec["wic_test"] = {"acc": w_gt["acc"], "real_minus_twin": w_gt["real_minus_twin"],
                               "margin_ci": w_gt["margin_ci"], "beats_twin": w_gt["real_beats_twin"]}
        if rag and rag_static_ok is not None:
            touched = set(int(x) for x in (rr + cc))
            rag_g_ok, _, tmask = eval_raganato(rag, s2i, T_g, n, touched=touched)
            gs, glo, ghi = _boot_margin(rag_g_ok, rag_static_ok, 12)     # grown vs STATIC (paired)
            retain = float(((rag_g_ok == 1) & (rag_static_ok == 1)).sum()) / max(1, int(rag_static_ok.sum()))
            rec["raganato"] = {"acc": round(float(rag_g_ok.mean()), 4),
                               "acc_minus_static": round(gs, 4), "margin_ci_vs_static": [round(glo, 4), round(ghi, 4)],
                               "beats_static": bool(glo > 0), "retention_of_static_correct": round(retain, 4)}
            if tmask.any():                                   # isolate the effect where it CAN exist (target touched)
                ts, tlo, thi = _boot_margin(rag_g_ok[tmask], rag_static_ok[tmask], 14)
                rec["raganato_touched"] = {"n_touched": int(tmask.sum()),
                                           "grown_acc": round(float(rag_g_ok[tmask].mean()), 4),
                                           "static_acc": round(float(rag_static_ok[tmask].mean()), 4),
                                           "acc_minus_static": round(ts, 4), "margin_ci": [round(tlo, 4), round(thi, 4)],
                                           "beats_static": bool(tlo > 0)}
            if rag_mfs_arr is not None:
                # MFS-WRONG = subordinate-sense items = THE FAIR TEST: the prior fails here, so ONLY context/
                # growth can help. the_prior_swamps_the_channel predicts a structural wall (no gold-blind
                # detector) -- if grown also fails here, it is that SAME understood wall, not a new failure.
                hard = (rag_mfs_arr == 0)
                if int(hard.sum()) > 0:
                    hs, hlo, hhi = _boot_margin(rag_g_ok[hard], rag_static_ok[hard], 15)
                    rec["raganato_mfs_wrong"] = {"n_hard": int(hard.sum()),
                                                 "grown_acc": round(float(rag_g_ok[hard].mean()), 4),
                                                 "static_acc": round(float(rag_static_ok[hard].mean()), 4),
                                                 "acc_minus_static": round(hs, 4), "margin_ci": [round(hlo, 4), round(hhi, 4)],
                                                 "beats_static": bool(hlo > 0)}
        _save_json(arm_p, rec)
        out["arms"][arm] = rec
        print("[grow] ARM %-13s edges=%d WiC dev r-t=%s | Raganato %s (vs static %s) touched=%s (%.0fs)" % (
            arm, len(rr), w_g["real_minus_twin"], rec.get("raganato", {}).get("acc"),
            rec.get("raganato", {}).get("acc_minus_static"),
            rec.get("raganato_touched", {}).get("acc_minus_static"), time.time() - t0), flush=True)

    # verdict ------------------------------------------------------------------------------------
    faithful = out["arms"].get("ppmi_ctx", {})
    twin = out["arms"].get("shuffle", {})
    out["headline"] = _headline(out, faithful, twin)
    out["elapsed_s"] = round(time.time() - t0, 2)
    _save_json(os.path.join(ck, "result_%s_%s.json" % (mode, base_variant)), out)
    return out


def _headline(out, faithful, twin):
    parts = []
    if "raganato" in faithful:
        parts.append("Raganato grown %s vs static %s: %+.4f CI%s beats_static=%s retention=%s" % (
            faithful["raganato"]["acc"], out.get("static_raganato", {}).get("acc"),
            faithful["raganato"]["acc_minus_static"], faithful["raganato"]["margin_ci_vs_static"],
            faithful["raganato"]["beats_static"], faithful["raganato"]["retention_of_static_correct"]))
    if "wic_test" in faithful:
        parts.append("WiC-test grown r-t=%s (static %s)" % (
            faithful["wic_test"]["real_minus_twin"], out.get("static_wic_test", {}).get("real_minus_twin")))
    if "raganato" in twin:
        parts.append("shuffle-twin Raganato %+.4f (must be < faithful)" % twin["raganato"]["acc_minus_static"])
    return " | ".join(parts) or "no eval ran"


# ============================================================================ self-test
# ============================================================================ INTEGRATED FULL STACK
# The owner's thesis: brain-foundational aspects that fail IN ISOLATION may synergize when PAIRED. Here:
#   SYNTACTIC edges (frequency-INDEPENDENT signal; a +0.007 isolated negative in context_override) +
#   local-collocation edges grown from reading -> sharper, better-SEPARATED basins -> COMPETITIVE SETTLING
#   (lateral inhibition; formally == argmax ONLY when basins are un-separated) now bites -> SEMANTIC CONTROL
#   suppression recovers subordinate senses. Plus E-M REPLAY (re-disambiguate with the improved graph).
def _resp_for_token(wn, w, ctx_words, s2i, T, n, topk=TOPK_SENSE):
    """Reordered-access soft responsibilities for ONE token given an EXPLICIT context word list (e.g. its
    syntactic neighbours = the frequency-independent signal). log(dominance) + ESTEP_LAM*log(context)."""
    sv = _word_senses(wn, w, s2i)
    if not sv:
        return None
    dom = np.array([1.0 / (1.0 + k) for k in range(len(sv))])
    seed = []
    for c in ctx_words:
        for _, j in _word_senses(wn, c, s2i):
            seed.append(j)
    if seed:
        r = M._ppr(sorted(set(seed)), T, n, iters=ESTEP_ITERS)
        pp = np.array([float(r[j]) for _, j in sv]); s = pp.sum()
        if s > 0:
            pp = pp / s
            logsc = np.log(dom) + ESTEP_LAM * np.log(pp + 1e-6)
            vals = np.exp(logsc - logsc.max())
        else:
            vals = dom
    else:
        vals = dom
    order = np.argsort(vals)[::-1][:topk]
    sel = [(sv[o][1], float(vals[o])) for o in order]
    tot = sum(v for _, v in sel) or 1.0
    return [(j, v / tot) for j, v in sel]


def _parse_corpus_syntactic(path, max_sents, ck):
    """spaCy dependency parse -> per sentence (content-lemma list, dependency pairs among content tokens).
    Cached JSONL (LOCAL only -- remote has no spaCy). The dependency pairs are the frequency-INDEPENDENT,
    sense-diagnostic structure (verb-argument, head-modifier)."""
    cache = os.path.join(ck, "synparse_%d.jsonl" % max_sents)
    if os.path.exists(cache):
        out = []
        for line in open(cache, encoding="utf-8"):
            r = json.loads(line); out.append((r["t"], r["d"]))
        return out
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    out = []
    buf = []
    tmp = cache + ".tmp"
    fw = open(tmp, "w", encoding="utf-8")

    def flush(sents):
        for doc in nlp.pipe(sents):
            idxmap = {}; toks = []
            for t in doc:
                if t.is_alpha and not t.is_stop and len(t.lemma_) >= 3:
                    idxmap[t.i] = len(toks); toks.append(t.lemma_.lower())
            deps = []
            for t in doc:
                if t.i in idxmap and t.head.i in idxmap and t.head.i != t.i:
                    deps.append([idxmap[t.head.i], idxmap[t.i]])
            if len(toks) >= 3:
                out.append((toks, deps)); fw.write(json.dumps({"t": toks, "d": deps}) + "\n")

    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if len(s) < 12:
                continue
            buf.append(s)
            if len(buf) >= 2000:
                flush(buf); buf = []
                if len(out) >= max_sents:
                    break
        if buf and len(out) < max_sents:
            flush(buf)
    fw.close()
    os.replace(tmp, cache)
    return out[:max_sents]


def _accumulate_syntactic(parsed, wn, s2i, T, n, per_token=False, t0=None, log_every=2000):
    """Accumulate soft synset co-occurrence over DEPENDENCY PAIRS (the sense-diagnostic syntactic EDGE
    structure). Disambiguation: per_token=True -> each token by its syntactic NEIGHBOURS (most faithful,
    one PPR/token, SLOW); per_token=False (default) -> per-SENTENCE (one PPR/sentence, ~5x faster) -- the
    syntactic value here is the edge STRUCTURE (which pairs), wired with the sentence-context senses."""
    cooc = defaultdict(float); supp = defaultdict(int)
    for si, (toks, deps) in enumerate(parsed):
        if per_token:
            neigh = defaultdict(list)
            for gi, di in deps:
                if 0 <= gi < len(toks) and 0 <= di < len(toks):
                    neigh[gi].append(di); neigh[di].append(gi)
            resp_i = {}
            for i, w in enumerate(toks):
                r = _resp_for_token(wn, w, [toks[j] for j in neigh.get(i, [])], s2i, T, n)
                if r:
                    resp_i[i] = r
            get = lambda idx: resp_i.get(idx)
        else:
            resp_w = _sentence_resp(wn, toks, s2i, T, n, "ctx")     # ONE PPR per sentence (fast)
            get = lambda idx: resp_w.get(toks[idx]) if 0 <= idx < len(toks) else None
        for gi, di in deps:
            ra = get(gi); rb = get(di)
            if not ra or not rb:
                continue
            for ia, va in ra:
                for ib, vb in rb:
                    if ia == ib:
                        continue
                    key = (ia, ib) if ia < ib else (ib, ia)
                    cooc[key] += va * vb; supp[key] += 1
        if t0 is not None and (si % log_every == 0):
            print("[grow:syn] sent %d/%d pairs=%d (%.0fs)" % (si, len(parsed), len(cooc), time.time() - t0), flush=True)
    marg = defaultdict(float)
    for (i, j), c in cooc.items():
        marg[i] += c; marg[j] += c
    return cooc, supp, marg


def _merge_cooc(a, b):
    """Merge two (cooc,supp,marg) accumulations (window + syntactic)."""
    cooc, supp = defaultdict(float), defaultdict(int)
    for (co, su, _) in (a, b):
        for k, v in co.items():
            cooc[k] += v
        for k, v in su.items():
            supp[k] += v
    marg = defaultdict(float)
    for (i, j), c in cooc.items():
        marg[i] += c; marg[j] += c
    return cooc, supp, marg


def _settle_coherence(wn, lemma, wnpos, ctxw, s2i, T, n, tn, nexp=2.0, iters=20):
    """Context coherence over the target's senses from COMPETITIVE ATTRACTOR SETTLING (lateral inhibition,
    divisive normalization; M._settle). nexp>1 = competition. Suppresses competitors where basins separate."""
    tset = set(tn); seed = []
    for w in ctxw:
        for nm, j in _all_senses(wn, w, s2i):
            if nm not in tset:
                seed.append(j)
    if not seed:
        return None
    a = M._settle(sorted(set(seed)), np.zeros(n, np.float32), T, n, nexp=nexp, iters=iters)
    return np.array([float(a[s2i[nm]]) if nm in s2i else 0.0 for nm in tn])


def eval_raganato_read(items, s2i, T, n, lam=1.0, gamma=1.0, quantile=0.80, coherence="ppr", control=True):
    """Unified brain-foundational readout. coherence in {ppr, settle}; control on/off (semantic_control
    LIFG suppression). Returns (ok, mfs, n_fired). Theta calibrated GOLD-BLIND (80th pct of conflicts)."""
    from nltk.corpus import wordnet as wn
    from hdlab.semantic_control import SemanticControl, conflict as _conflict
    recs = []; conflicts = []
    ok = np.zeros(len(items), np.int32); mfs = np.zeros(len(items), np.int32)
    for k, (iid, lemma, wnpos, ctx, g) in enumerate(items):
        tgt, tn, prior = _target_senses(wn, lemma, wnpos)
        if not tn:
            recs.append(None); continue
        mfs[k] = int(tn[0] in g)
        pidx = int(np.argmax(prior))
        if len(tn) < 2:
            recs.append(("mono", tn, g, pidx, None, None, None)); continue
        ctxw = [w for w in ctx if w != lemma]
        coh = (_settle_coherence(wn, lemma, wnpos, ctxw, s2i, T, n, tn) if coherence == "settle"
               else _fast_coh(wn, ctxw, s2i, T, n, tn))
        if coh is None:
            recs.append(("nocoh", tn, g, pidx, None, None, None)); continue
        coh = np.asarray(coh, float); cs = coh.sum(); cohn = coh / cs if cs > 0 else coh
        scores = np.log(prior + 0.1) + lam * np.log(cohn + 1e-6)
        cfl = _conflict(cohn, pidx); conflicts.append(cfl)
        recs.append(("full", tn, g, pidx, scores, cohn, cfl))
    sc = SemanticControl(gamma=gamma).calibrate(conflicts, quantile) if control else None
    fired = 0
    for k, r in enumerate(recs):
        if r is None:
            continue
        typ, tn, g, pidx, scores, cohn, cfl = r
        if typ in ("mono", "nocoh"):
            ok[k] = int(tn[pidx] in g); continue
        if control and sc is not None:
            idx, _ = sc.resolve(scores, cohn, pidx); fired += int(sc.fires(cfl))
        else:
            idx = int(np.argmax(scores))
        ok[k] = int(tn[idx] in g)
    return ok, mfs, fired


def run_fullstack(cache_dir, max_sents, base_variant, n_rag, lam, gamma, rounds, use_syntactic, t0=None):
    """The INTEGRATED brain-foundational stack: grow (window + SYNTACTIC edges, E-M REPLAY rounds), read
    (reordered-access + COMPETITIVE SETTLING + SEMANTIC CONTROL). Static vs grown on the subordinate pop."""
    from nltk.corpus import wordnet as wn
    t0 = t0 or time.time(); ck = _ck()
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    A_base = _base_adjacency(base_variant, s2i, syns, n, ck)
    T_static = M._row_stochastic(A_base.copy())
    window_sents = _corpus_sentences(SIMPLEWIKI, max_sents)
    parsed = _parse_corpus_syntactic(SIMPLEWIKI, max_sents, ck) if use_syntactic else []
    print("[full] base %s + %d window sents + %d parsed sents (%.0fs)" % (
        base_variant, len(window_sents), len(parsed), time.time() - t0), flush=True)
    # E-M REPLAY: disambiguate with the current graph, grow, rebuild, repeat.
    T_cur = T_static; edges = ([], [], [])
    for rd in range(rounds):
        aw = _accumulate(window_sents, wn, s2i, T_cur, n, "ctx", t0=t0)
        acc = _merge_cooc(aw, _accumulate_syntactic(parsed, wn, s2i, T_cur, n, t0=t0)) if use_syntactic else aw
        rr, cc, ww, estat = _ppmi_edges(acc[0], acc[1], acc[2], "ppmi", A_base, schema_gate=True)
        T_cur = _grown_T(A_base, rr, cc, ww, 2.0, n); edges = (rr, cc, ww)
        print("[full] E-M round %d: %d edges (%s) (%.0fs)" % (rd + 1, len(rr), estat, time.time() - t0), flush=True)
    T_grown = T_cur
    rag = _load_raganato(wn)
    if n_rag and len(rag) > n_rag:
        idx = np.random.default_rng(0).permutation(len(rag))[:n_rag]; rag = [rag[i] for i in sorted(idx)]
    out = {"max_sents": max_sents, "rounds": rounds, "use_syntactic": use_syntactic, "n_edges": len(edges[0]),
           "n_raganato": len(rag), "base_variant": base_variant}
    # the full 2x2x2: {static,grown} x {ppr,settle} x {argmax,control}, on the SUBORDINATE population
    combos = [("static_ppr_argmax", T_static, "ppr", False), ("static_ppr_control", T_static, "ppr", True),
              ("grown_ppr_argmax", T_grown, "ppr", False), ("grown_ppr_control", T_grown, "ppr", True),
              ("grown_settle_argmax", T_grown, "settle", False), ("grown_settle_control", T_grown, "settle", True),
              ("static_settle_control", T_static, "settle", True)]
    res = {}
    mfs_ref = None
    for name, T, coh, ctrl in combos:
        ok, mfs, fired = eval_raganato_read(rag, s2i, T, n, lam, gamma, coherence=coh, control=ctrl)
        if mfs_ref is None:
            mfs_ref = mfs
        res[name] = (ok, fired)
        print("[full] %-22s acc=%.4f fired=%d (%.0fs)" % (name, ok.mean(), fired, time.time() - t0), flush=True)
    hard = (mfs_ref == 0); nh = int(hard.sum())
    out["n_subordinate"] = nh
    out["arms"] = {name: {"acc": round(float(ok.mean()), 4),
                          "subordinate_acc": round(float(ok[hard].mean()), 4) if nh else None, "fired": fired}
                   for name, (ok, fired) in res.items()}
    # decisive contrasts on the subordinate population (the integrated stack vs the pieces)
    def contrast(a, b):
        d, lo, hi = _boot_margin(res[a][0][hard], res[b][0][hard], 31)
        return {"delta_subordinate": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "beats": bool(lo > 0)}
    if nh:
        out["contrasts"] = {
            "control_helps_static": contrast("static_ppr_control", "static_ppr_argmax"),
            "growth_helps_control": contrast("grown_ppr_control", "static_ppr_control"),
            "settle_helps_grown": contrast("grown_settle_control", "grown_ppr_control"),
            "FULL_STACK_vs_static_baseline": contrast("grown_settle_control", "static_ppr_argmax"),
        }
    out["headline"] = ("FULL STACK subordinate (n=%d): static-argmax %s -> full-stack(grown+settle+control) %s | "
                       "full-vs-baseline %s" % (nh, out["arms"]["static_ppr_argmax"]["subordinate_acc"],
                       out["arms"]["grown_settle_control"]["subordinate_acc"],
                       out.get("contrasts", {}).get("FULL_STACK_vs_static_baseline", {}).get("delta_subordinate")))
    out["elapsed_s"] = round(time.time() - t0, 2)
    _save_json(os.path.join(ck, "result_fullstack_%s_%d.json" % (base_variant, max_sents)), out)
    return out


def run_signatures(cache_dir, max_sents, base_variant):
    """P5: EMERGENT brain-faithfulness signatures that must fall out UNBID (not hand-coded):
      (A) FREQUENCY-DOMINANCE (Rodd: basin depth ~ frequency): high-SemCor-frequency senses accumulate
          MORE learned edges. Spearman(log freq, learned degree) > 0; shuffled-frequency null ~ 0.
      (B) SEMANTIC COHERENCE (learns structure, not noise): learned edges connect senses that are more
          WordNet-RELATED than random node pairs. Mean path-similarity(learned endpoints) >> random.
    Cheap (edge stats only, no PPR). Reuses the cached ppmi_ctx edges."""
    from nltk.corpus import wordnet as wn, wordnet_ic
    from scipy.stats import spearmanr
    t0 = time.time(); ck = _ck()
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    i2s = {i: s.name() for s, i in zip(syns, range(n))}
    A_base = _base_adjacency(base_variant, s2i, syns, n, ck)
    rr, cc, ww, estat = _load_ctx_edges(ck, A_base, max_sents)
    deg = defaultdict(float)
    for i, j in zip(rr, cc):
        deg[i] += 1.0; deg[j] += 1.0
    # (A) frequency-dominance
    ic = wordnet_ic.ic("ic-semcor.dat")
    fr, dg = [], []
    for idx, d in deg.items():
        s = wn.synset(i2s[idx]); pos = s.pos()
        if pos not in ("n", "v"):
            continue
        f = float(ic[pos].get(s.offset(), 0.0))
        fr.append(math.log1p(f)); dg.append(d)
    fr = np.array(fr); dg = np.array(dg)
    rho, p = spearmanr(fr, dg) if len(fr) > 10 else (float("nan"), 1.0)
    perm = np.random.default_rng(7).permutation(len(fr))
    rho_null, _ = spearmanr(fr[perm], dg) if len(fr) > 10 else (0.0, 1.0)
    # (B) semantic coherence: learned endpoints vs random pairs from the SAME node set
    rng = np.random.default_rng(3)
    nodes = np.array(sorted(deg.keys()))
    m = min(3000, len(rr))
    pick = rng.permutation(len(rr))[:m]

    def _pathsim(a_idx, b_idx):
        try:
            v = wn.synset(i2s[int(a_idx)]).path_similarity(wn.synset(i2s[int(b_idx)]))
            return float(v) if v is not None else 0.0
        except Exception:
            return 0.0
    learned_sim = np.array([_pathsim(rr[k], cc[k]) for k in pick])
    ra = rng.choice(nodes, size=m); rb = rng.choice(nodes, size=m)
    rand_sim = np.array([_pathsim(ra[k], rb[k]) for k in range(m)])
    d, lo, hi = _boot_margin(learned_sim, rand_sim, 51)
    out = {"base_variant": base_variant, "max_sents": max_sents, "n_grown_edges": len(rr), "edge_stat": estat,
           "frequency_dominance": {"spearman_logfreq_vs_degree": round(float(rho), 4), "p": round(float(p), 6),
                                   "shuffled_freq_null": round(float(rho_null), 4), "n": len(fr),
                                   "emergent": bool(rho > 0 and p < 0.05 and rho > abs(rho_null))},
           "semantic_coherence": {"learned_pathsim": round(float(learned_sim.mean()), 4),
                                  "random_pathsim": round(float(rand_sim.mean()), 4),
                                  "delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "emergent": bool(lo > 0)}}
    out["headline"] = ("EMERGENT signatures: frequency-dominance rho=%.3f (null %.3f, emergent=%s); learned edges "
                       "connect related senses %.3f vs random %.3f (emergent=%s)" % (
                       rho, rho_null, out["frequency_dominance"]["emergent"],
                       out["semantic_coherence"]["learned_pathsim"], out["semantic_coherence"]["random_pathsim"],
                       out["semantic_coherence"]["emergent"]))
    out["elapsed_s"] = round(time.time() - t0, 2)
    _save_json(os.path.join(ck, "result_signatures_%s.json" % base_variant), out)
    return out


def run_subordinate(cache_dir, max_sents, base_variant, max_files, lam, gamma):
    """POWERED subordinate-override test (P1/P2/P3): large SemCor subordinate-congruent population (gold
    count STRICTLY below the top sense = MFS wrong by construction, per context_override), reporting the
    subordinate lift AND the dominant see-saw COST, with a SHUFFLED-CONTEXT null. Static vs grown coherence,
    argmax vs semantic-control. Reuses the cached ppmi_ctx edges. Per-arm npz checkpoints (resumable)."""
    from nltk.corpus import wordnet as wn
    t0 = time.time(); ck = _ck()
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    A_base = _base_adjacency(base_variant, s2i, syns, n, ck); T_static = M._row_stochastic(A_base.copy())
    rr, cc, ww, estat = _load_ctx_edges(ck, A_base, max_sents); T_grown = _grown_T(A_base, rr, cc, ww, 2.0, n)
    br, bc, bw, bstat = _load_ctx_edges(ck, A_base, max_sents, weighting="bcm"); T_bcm = _grown_T(A_base, br, bc, bw, 2.0, n)
    print("[sub] graphs built: %d ppmi edges, %d bcm edges (%.0fs)" % (len(rr), len(br), time.time() - t0), flush=True)
    inst = M._semcor_instances(max_files=max_files)
    items = []; sub = []
    for it in inst:
        wnpos = M._WNPOS.get(it["pos"])
        tgt = wn.synsets(it["lemma"], pos=wnpos); tn = [s.name() for s in tgt]
        if len(tn) < 2 or it["gold"] not in tn:
            continue
        counts = M._sense_prior(it["lemma"], tgt); gi = tn.index(it["gold"])
        items.append((len(items), it["lemma"], wnpos, it["ctx"], {it["gold"]}))
        sub.append(bool(counts[gi] < counts.max() - 1e-9))          # subordinate = gold strictly rarer than top
    sub = np.array(sub); nS = int(sub.sum()); nD = int((~sub).sum())
    print("[sub] %d polysemous items: %d subordinate, %d dominant (%.0fs)" % (len(items), nS, nD, time.time() - t0), flush=True)

    def cached_eval(name, T, coh, ctrl, shuffle=False):
        p = os.path.join(ck, "subok_%s_%s_%df_%d%s.npz" % (name, base_variant, max_files, max_sents, "_sh" if shuffle else ""))
        if os.path.exists(p):
            return np.load(p)["ok"]
        ev = items
        if shuffle:                                                 # info-free null: context from a RANDOM other item
            perm = np.random.default_rng(19).permutation(len(items))
            ev = [(items[i][0], items[i][1], items[i][2], items[perm[i]][3], items[i][4]) for i in range(len(items))]
        ok, _, _ = eval_raganato_read(ev, s2i, T, n, lam, gamma, coherence=coh, control=ctrl)
        np.savez(p + ".b", ok=ok); os.replace(p + ".b.npz", p)
        print("[sub] %s%s acc=%.4f (%.0fs)" % (name, "_shuf" if shuffle else "", ok.mean(), time.time() - t0), flush=True)
        return ok

    arms = {"static_argmax": cached_eval("static_argmax", T_static, "ppr", False),
            "static_control": cached_eval("static_control", T_static, "ppr", True),
            "grown_argmax": cached_eval("grown_argmax", T_grown, "ppr", False),
            "grown_control": cached_eval("grown_control", T_grown, "ppr", True),
            "bcm_argmax": cached_eval("bcm_argmax", T_bcm, "ppr", False),      # HOMEOSTATIC growth (anti-freq-dominance)
            "bcm_control": cached_eval("bcm_control", T_bcm, "ppr", True)}
    twin = cached_eval("grown_control", T_grown, "ppr", True, shuffle=True)   # shuffled-context null

    def stats(ok):
        return {"acc": round(float(ok.mean()), 4),
                "subordinate": round(float(ok[sub].mean()), 4) if nS else None,
                "dominant": round(float(ok[~sub].mean()), 4) if nD else None}

    def contrast(a, b, mask, seed):
        d, lo, hi = _boot_margin(arms[a][mask], arms[b][mask], seed)
        return {"delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "beats": bool(lo > 0)}

    out = {"n_items": len(items), "n_subordinate": nS, "n_dominant": nD, "n_ppmi_edges": len(rr), "n_bcm_edges": len(br),
           "edge_stat": estat, "max_files": max_files, "max_sents": max_sents, "base_variant": base_variant}
    out["arms"] = {k: stats(v) for k, v in arms.items()}
    out["shuffled_context_twin_grown_control"] = stats(twin)
    out["subordinate_contrasts"] = {
        "control_helps_static": contrast("static_control", "static_argmax", sub, 41),
        "growth_helps_control": contrast("grown_control", "static_control", sub, 42),
        "grown_control_vs_static_argmax": contrast("grown_control", "static_argmax", sub, 43),
        "BCM_helps_control": contrast("bcm_control", "static_control", sub, 47),        # homeostatic lever
        "BCM_vs_ppmi_control": contrast("bcm_control", "grown_control", sub, 48)}
    out["dominant_seesaw_cost"] = {                                  # P2: the honest see-saw cost on dominant items
        "control_cost_static": contrast("static_control", "static_argmax", ~sub, 44),
        "growth_effect": contrast("grown_control", "static_control", ~sub, 45),
        "bcm_effect": contrast("bcm_control", "static_control", ~sub, 49)}
    d, lo, hi = _boot_margin(arms["grown_control"][sub], twin[sub], 46)   # P3: real vs shuffled-context null
    out["grown_control_vs_shuffled_null_subordinate"] = {"delta": round(d, 4), "ci": [round(lo, 4), round(hi, 4)], "beats": bool(lo > 0)}
    out["headline"] = ("SUBORDINATE n=%d: static-argmax %.4f -> +control %.4f | ppmi-growth+control %.4f (helps=%s) | "
                       "BCM-growth+control %.4f (helps=%s, vs-ppmi %s) | dominant see-saw cost %s" % (
                       nS, out["arms"]["static_argmax"]["subordinate"], out["arms"]["static_control"]["subordinate"],
                       out["arms"]["grown_control"]["subordinate"], out["subordinate_contrasts"]["growth_helps_control"]["beats"],
                       out["arms"]["bcm_control"]["subordinate"], out["subordinate_contrasts"]["BCM_helps_control"]["beats"],
                       out["subordinate_contrasts"]["BCM_vs_ppmi_control"]["delta"],
                       out["dominant_seesaw_cost"]["control_cost_static"]["delta"]))
    out["elapsed_s"] = round(time.time() - t0, 2)
    _save_json(os.path.join(ck, "result_subordinate_%s.json" % base_variant), out)
    return out


def self_test():
    from nltk.corpus import wordnet as wn
    ev = {}
    # PPMI surprise: a rare-marginal pair that co-occurs gets HIGHER weight than a frequent-marginal pair
    # with the same co-occurrence -> surprise up-weights informative neighbours.
    cooc = {(0, 1): 5.0, (0, 2): 5.0}
    supp = {(0, 1): 5, (0, 2): 5}
    marg = {0: 100.0, 1: 5.0, 2: 100.0}       # node1 rare, node2 frequent
    A = sp.csr_matrix((np.ones(4), ([0, 1, 0, 2], [1, 0, 2, 0])), shape=(3, 3))  # both pairs are neighbours
    rows, cols, wts, _ = _ppmi_edges(cooc, supp, marg, "ppmi", A, schema_gate=True)
    d = {(r, c): w for r, c, w in zip(rows, cols, wts)}
    assert d[(0, 1)] > d[(0, 2)], "PPMI must up-weight the pair with the rarer (more surprising) neighbour"
    ev["ppmi_surprise_upweights_rare"] = [round(d[(0, 1)], 3), round(d[(0, 2)], 3)]
    # BCM homeostatic: shifts weight toward the LOW-activity (subordinate) node vs high-activity (frequent) one
    rb, cb, wb, _ = _ppmi_edges(cooc, supp, marg, "bcm", A, schema_gate=True)
    db = {(r, c): w for r, c, w in zip(rb, cb, wb)}
    assert db[(0, 1)] / db[(0, 2)] > d[(0, 1)] / d[(0, 2)], "BCM must shift weight toward the low-activity (subordinate) node"
    ev["bcm_favours_low_activity"] = True
    # cross-situational gate: below MIN_COOC support is dropped
    rows2, _, _, _ = _ppmi_edges({(0, 1): 1.0}, {(0, 1): 1}, {0: 2.0, 1: 2.0}, "ppmi", A, True)
    assert len(rows2) == 0, "support < MIN_COOC must be gated out (cross-situational)"
    ev["cross_situational_gate"] = True
    # schema-gate: a NOVEL (non-neighbour) pair with < K_CONFIRM_NOVEL support is refused; a schema-
    # consistent (neighbour) pair at the same support is kept -> the fast/slow cortical rate.
    Anb = sp.csr_matrix((np.ones(2), ([0, 1], [1, 0])), shape=(4, 4))   # only (0,1) are neighbours
    novel = {(2, 3): 10.0}; nsupp = {(2, 3): MIN_COOC + 1}          # >=MIN_COOC but < K_CONFIRM_NOVEL
    r_gate, _, _, _ = _ppmi_edges(novel, nsupp, {2: 5.0, 3: 5.0}, "ppmi", Anb, schema_gate=True)
    r_nogate, _, _, _ = _ppmi_edges(novel, nsupp, {2: 5.0, 3: 5.0}, "ppmi", Anb, schema_gate=False)
    assert len(r_gate) == 0 and len(r_nogate) == 1, "schema-gate must slow novel (non-neighbour) pairs"
    ev["schema_gate_slows_novel"] = True
    # grown T is row-stochastic
    Ab = M._symmetrize([0, 1], [1, 2], 4); Ab.data[:] = 1.0; Ab = Ab.tocsr()
    Tg = _grown_T(Ab, [0], [3], [2.0], edge_scale=1.0, n=4)
    assert abs(float(Tg.sum(1).max()) - 1.0) < 1e-6, "grown T rows must sum to 1"
    ev["grown_row_stochastic"] = True
    # shuffle twin preserves count + weights but destroys endpoints
    sr, sc, sw = _shuffle_edges([0, 1], [2, 3], [1.0, 2.0], seed=1)
    assert len(sr) == 2 and sorted(sw) == [1.0, 2.0], "shuffle keeps #edges and weight multiset"
    ev["shuffle_twin_ok"] = True
    # E-step soft responsibilities sum to 1 per word and are context-disambiguated (top-k)
    syns = M._synsets_ordered(); s2i = {s.name(): i for i, s in enumerate(syns)}; n = len(syns)
    # semantic control: when coherence favours the subordinate sense, conflict-gated suppression of the
    # dominant (prior) flips the argmax to the context-appropriate competitor (the LIFG override).
    from hdlab.semantic_control import SemanticControl, conflict as _conflict
    prior = np.array([10.0, 1.0]); coh = np.array([0.1, 0.9]); pidx = 0
    scores = np.log(prior + 0.1) + 1.0 * np.log(coh + 1e-6)
    assert int(np.argmax(scores)) == 0, "without control, the frequency prior wins (dominant)"
    sc = SemanticControl(gamma=5.0); sc.theta = 0.0            # fire on any positive conflict
    idx, _ = sc.resolve(scores, coh, pidx)
    assert idx == 1, "semantic control must flip to the context-favoured subordinate sense"
    ev["semantic_control_flips_subordinate"] = True
    # merge cooc (window + syntactic accumulations sum their evidence)
    m = _merge_cooc(({(0, 1): 2.0}, {(0, 1): 2}, {}), ({(0, 1): 3.0, (1, 2): 1.0}, {(0, 1): 3, (1, 2): 1}, {}))
    assert m[0][(0, 1)] == 5.0 and m[1][(0, 1)] == 5 and m[0][(1, 2)] == 1.0, "merge sums cooc + supp"
    ev["merge_cooc_ok"] = True
    ev["self_test"] = "PASS"
    return ev


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    ap.add_argument("--self-test", dest="selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--arms", default="ppmi_ctx,ppmi_ctx_nogate,raw_ctx,ppmi_mfs,shuffle")
    ap.add_argument("--edge-scale", type=float, default=2.0)
    ap.add_argument("--no-schema-gate", action="store_true")
    ap.add_argument("--base-variant", default="cn_syn", choices=["base", "cn", "cn_syn"],
                    help="static floor graph. Discriminator: cn_syn (has 88k manual SyntagNet edges) vs base "
                         "(no SyntagNet) -- if growth helps base but not cn_syn, reading RE-DERIVES SyntagNet.")
    ap.add_argument("--eval", dest="eval_which", choices=["wic", "wsd_all", "both"], default="both")
    ap.add_argument("--max-sents", type=int, default=0, help="0 -> mode default")
    ap.add_argument("--inhibitory", action="store_true",
                    help="brain-foundational readout test: reordered-access + semantic_control suppression, "
                         "grown vs static coherence, on the SUBORDINATE (MFS-wrong) population. Reuses cached edges.")
    ap.add_argument("--lam", type=float, default=1.0, help="context weight in the reordered-access read")
    ap.add_argument("--gamma", type=float, default=1.0, help="semantic-control suppression strength")
    ap.add_argument("--fullstack", action="store_true",
                    help="INTEGRATED stack: window+SYNTACTIC edges, E-M replay rounds, COMPETITIVE SETTLING + "
                         "SEMANTIC CONTROL. Tests brain-foundational aspects PAIRED (synergy), on the subordinate pop.")
    ap.add_argument("--rounds", type=int, default=2, help="E-M replay rounds (re-disambiguate with the grown graph)")
    ap.add_argument("--no-syntactic", action="store_true", help="ablate the syntactic edges (window-only)")
    ap.add_argument("--subordinate", action="store_true",
                    help="POWERED subordinate-override test on large SemCor (subordinate + dominant see-saw + null)")
    ap.add_argument("--max-files", type=int, default=200, help="SemCor files for the subordinate population")
    ap.add_argument("--signatures", action="store_true",
                    help="P5: emergent brain-faithfulness signatures (frequency-dominance + semantic coherence)")
    args = ap.parse_args(argv)
    if args.selftest:
        args.mode = "self-test"
    elif args.smoke:
        args.mode = "smoke"

    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2)); print("SELF-TEST PASSED"); return 0

    st = self_test()
    if args.signatures:
        max_sents = args.max_sents or 40000
        out = run_signatures(_ck(), max_sents, args.base_variant)
        out["selftest"] = st
        print(json.dumps(out, indent=2, default=str)); print("HEADLINE:", out["headline"]); print("DONE")
        return 0
    if args.subordinate:
        max_sents = args.max_sents or 40000
        out = run_subordinate(_ck(), max_sents, args.base_variant, args.max_files, args.lam, args.gamma)
        out["selftest"] = st
        print(json.dumps(out, indent=2, default=str)); print("HEADLINE:", out["headline"]); print("DONE")
        return 0
    if args.fullstack:
        max_sents = args.max_sents or 15000
        out = run_fullstack(_ck(), max_sents, args.base_variant, 2500, args.lam, args.gamma,
                            args.rounds, not args.no_syntactic)
        out["selftest"] = st
        print(json.dumps(out, indent=2, default=str)); print("HEADLINE:", out["headline"]); print("DONE")
        return 0
    if args.inhibitory:
        max_sents = args.max_sents or 40000
        out = run_inhibitory(_ck(), max_sents, args.base_variant, 2500, args.lam, args.gamma)
        out["selftest"] = st
        print(json.dumps(out, indent=2, default=str)); print("HEADLINE:", out["headline"]); print("DONE")
        return 0
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    if args.mode == "smoke":
        max_sents = args.max_sents or 600
        n_wic, n_rag = 150, 300
    else:
        max_sents = args.max_sents or 40000
        n_wic, n_rag = 100000, 2500                           # full WiC dev+test; Raganato sampled 2500 (powered + tractable)
    out = run_smoke_or_full(args.mode, os.path.join(_ck()), arms, args.edge_scale,
                            not args.no_schema_gate, args.eval_which, max_sents, n_wic, n_rag, args.base_variant)
    out["selftest"] = st
    print(json.dumps(out, indent=2, default=str))
    print("HEADLINE:", out["headline"])
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
