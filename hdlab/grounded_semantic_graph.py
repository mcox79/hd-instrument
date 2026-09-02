"""grounded_semantic_graph -- a grounded relational semantic graph (WordNet++ synset nodes) read by
SPREADING ACTIVATION (personalized PageRank), augmentable (add_edges) and learnable (learn_from_text).

PROMOTED VERBATIM (2026-09-01, Q111 -- strategy is the sole hdlab writer) from two experiment files:
  * class GroundedSemanticGraph + _SOURCE_EDGES + _demo -> experiments/grounded_semantic_graph_organ.py
  * the ~11 graph primitives (_synsets_ordered, _relation_gloss_edges, _conceptnet_edges,
    _syntagnet_edges, _symmetrize, _row_stochastic, _sense_ppr, _sense_prior, _blend_pick,
    _learn_cooc_edges, _WNPOS) + their transitive helpers/constants (_rels, _ppr, _gloss_content,
    DAMPING, PPR_ITERS, CN_PATH, SYNTAGNET_PATH, _CN_KEEP, LITBANK_DIR, MIN_COOC, _STOP)
    -> experiments/exp_grounded_semantic_graph_ladder_wsd_v1.py (primitives) and
       experiments/exp_ppr_spreading_activation_wsd_wic_v1.py (_ppr/_gloss_content/_WNPOS/DAMPING/PPR_ITERS)
       and experiments/exp_sense_wall_breakthrough_wic_v1.py (_STOP).
The primitive BODIES are byte-for-byte copies. The ONLY edit made during inlining: _gloss_content dropped
its inner `from experiments... import _STOP` line and now reads the module-level _STOP inlined below
(the _STOP set itself is copied verbatim) -- this is required to make the file self-contained (no
`from experiments...` imports). Behavior is unchanged.

Proven in exp_grounded_semantic_graph_ladder_wsd_v1.py + verification/test_grounded_semantic_graph_ladder.py
(5/5; ConceptNet thematic edges clear the WiC context-shuffle twin held-out).

Glass-box, LM-FREE at inference, deterministic. NO external LLM (the invariant).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
from typing import Dict, List

import numpy as np
import scipy.sparse as sp

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


# ================================================================================================
# CONSTANTS (inlined verbatim from the source experiment cells)
# ================================================================================================
# -- from exp_ppr_spreading_activation_wsd_wic_v1.py --
DAMPING = 0.85
PPR_ITERS = 30
_WNPOS = {"N": "n", "V": "v"}

# -- from exp_grounded_semantic_graph_ladder_wsd_v1.py --
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

LITBANK_DIR = os.path.join(REPO, "data", "litbank", "original")
MIN_COOC = 3

# -- from exp_sense_wall_breakthrough_wic_v1.py (used by _gloss_content and _learn_cooc_edges) --
_STOP = set(
    "a an the this that these those of to in on at by for with from into over under and or but if then "
    "is are was were be been being am do does did done has have had having will would shall should can "
    "could may might must not no nor as so than too very s t it its it's he she they them his her their "
    "him you your i me my we us our who whom which what when where why how all any both each few more most "
    "other some such only own same up down out off again further here there both".split())


# ================================================================================================
# HELPERS (inlined verbatim)
# ================================================================================================
# -- from exp_ppr_spreading_activation_wsd_wic_v1.py --
def _gloss_content(defn: str):
    out = []
    for tok in defn.replace(";", " ").split():
        t = "".join(c for c in tok.lower() if c.isalpha())
        if len(t) >= 3 and t not in _STOP:
            out.append(t)
    return out


def _ppr(seed_idx: List[int], Tt: sp.csr_matrix, n: int, d: float = DAMPING, iters: int = PPR_ITERS):
    """stationary spreading-activation vector: r = (1-d)*p + d*T^T r, p uniform over seed synsets."""
    if not seed_idx:
        return None
    p = np.zeros(n, np.float32)
    p[seed_idx] = 1.0 / len(seed_idx)
    r = p.copy()
    for _ in range(iters):
        r = (1.0 - d) * p + d * (Tt @ r)
    return r


# -- from exp_grounded_semantic_graph_ladder_wsd_v1.py --
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


# ================================================================================================
# THE ORGAN (promoted verbatim from experiments/grounded_semantic_graph_organ.py)
# ================================================================================================
_SOURCE_EDGES = {
    "relations_glosses": lambda syns, s2i: _relation_gloss_edges(syns, s2i, gloss_cap=1),
    "conceptnet": lambda syns, s2i: _conceptnet_edges(s2i, cn_cap=1)[:2],
    "syntagnet": lambda syns, s2i: _syntagnet_edges(s2i)[:2],
}


class GroundedSemanticGraph:
    """A grounded relational semantic graph (WordNet++ synset nodes) read by personalized-PageRank
    spreading activation. Augmentable (add_edges) and learnable (learn_from_text)."""

    def __init__(self, sources=("relations_glosses", "conceptnet", "syntagnet")):
        self.sources = tuple(sources)
        self.syn2idx = None
        self.T = None
        self._base_rows = []
        self._base_cols = []
        self._extra_rows = []
        self._extra_cols = []

    # ---- BUILD (static foundation) -------------------------------------------------------------
    def build(self):
        syns = _synsets_ordered()
        self.syn2idx = {s.name(): i for i, s in enumerate(syns)}
        rows, cols = [], []
        for src in self.sources:
            r, c = _SOURCE_EDGES[src](syns, self.syn2idx)
            rows = rows + list(r); cols = cols + list(c)
        self._base_rows, self._base_cols = rows, cols
        self._rebuild()
        return self

    def _rebuild(self):
        n = len(self.syn2idx)
        A = _symmetrize(self._base_rows + self._extra_rows, self._base_cols + self._extra_cols, n)
        A.data[:] = 1.0
        self.T = _row_stochastic(A)

    @property
    def n_edges(self):
        return len(self._base_rows) + len(self._extra_rows)

    # ---- AUGMENT (can be added to) -------------------------------------------------------------
    def add_edges(self, rows, cols):
        """Add arbitrary synset-index edges (e.g., a new static source, or externally learned edges)."""
        self._extra_rows += list(rows); self._extra_cols += list(cols)
        self._rebuild()
        return self

    # ---- LEARN (grows from reading) ------------------------------------------------------------
    def learn_from_text(self, max_sents=10000):
        """GROW syntagmatic edges from reading (LitBank co-occurrence; cross-situational gate). Returns the
        number of learned edges added. Brain-faithful direction: Hebbian/cross-situational (Yu & Smith);
        the full CLS + schema-gate + sense split/merge spec is in LEARNED_GRAPH_brain_mechanism_spec.md."""
        r, c, ne = _learn_cooc_edges(self.syn2idx, max_sents)
        self.add_edges(r, c)
        return ne

    # ---- READ (spreading activation) -----------------------------------------------------------
    def select_sense(self, lemma, pos, context_words):
        """Pick the target's WordNet synset with max settled spreading activation seeded by the context
        (ppr_w2w). pos in {'N','V'}. Returns a synset name (or None if the word is unknown)."""
        from nltk.corpus import wordnet as wn
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tn = [s.name() for s in tgt]
        if not tgt:
            return None
        if len(tgt) == 1:
            return tn[0]
        ppr = _sense_ppr(wn, lemma, pos, list(context_words), self.syn2idx, self.T, len(self.syn2idx), tgt, tn)
        return tn[0] if ppr is None else tn[int(np.argmax(ppr))]

    def select_sense_blended(self, lemma, pos, context_words, lam=0.5):
        """Read + the frequency resting-level prior via the log-linear blend (log P_freq + lam*log PPR) --
        the brain's ambiguity gate == the field's UKB combination. Best for all-words WSD where the prior matters."""
        from nltk.corpus import wordnet as wn
        tgt = wn.synsets(lemma, pos=_WNPOS.get(pos)); tn = [s.name() for s in tgt]
        if not tgt:
            return None
        if len(tgt) == 1:
            return tn[0]
        ppr = _sense_ppr(wn, lemma, pos, list(context_words), self.syn2idx, self.T, len(self.syn2idx), tgt, tn)
        return tn[_blend_pick(ppr, _sense_prior(lemma, tgt), lam)]


def _demo():
    """Live demo of the three capabilities (build -> read -> augment -> learn)."""
    import time
    t0 = time.time()
    g = GroundedSemanticGraph(sources=("relations_glosses", "conceptnet", "syntagnet")).build()
    print("BUILT: %d synset nodes, %d edges (relations+glosses+ConceptNet+SyntagNet) (%.0fs)"
          % (len(g.syn2idx), g.n_edges, time.time() - t0))
    # READ: disambiguate 'bank' in two contexts
    river = g.select_sense("bank", "N", ["river", "water", "flow", "shore"])
    money = g.select_sense("bank", "N", ["money", "loan", "account", "deposit"])
    print("READ  select_sense('bank' | river-context) -> %s" % river)
    print("READ  select_sense('bank' | money-context) -> %s" % money)
    print("READ  differentiates by context: %s" % (river != money))
    # AUGMENT: add a couple of hand edges
    before = g.n_edges
    g.add_edges([0], [1])
    print("AUGMENT add_edges: %d -> %d edges" % (before, g.n_edges))
    # LEARN: grow from reading
    before = g.n_edges
    ne = g.learn_from_text(max_sents=1500)
    print("LEARN  learn_from_text(1500 sents): +%d learned edges, %d -> %d total (%.0fs)"
          % (ne, before, g.n_edges, time.time() - t0))
    print("READY: build / select_sense / select_sense_blended / add_edges / learn_from_text all live.")


if __name__ == "__main__":
    _demo()
