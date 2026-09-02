"""grounded_semantic_graph_organ -- the INTEGRATION-READY reference organ for the grounded relational
semantic graph, read by SPREADING ACTIVATION. Proven in exp_grounded_semantic_graph_ladder_wsd_v1.py +
verification/test_grounded_semantic_graph_ladder.py (5/5, cn clears the WiC context-shuffle twin held-out).

WHY THIS FILE EXISTS: it packages the proven mechanism behind ONE clean API so the strategy session can
promote it to hdlab/grounded_semantic_graph.py nearly verbatim (Q111 -- strategy is the sole hdlab writer).
On promotion, inline the ~8 primitives imported below (they live in the experiment cell today).

IT ANSWERS THE TWO INTEGRATION QUESTIONS CONCRETELY:
  * READY TO INTEGRATE -- yes: a stable API (build / select_sense / select_sense_blended); the wire is a
    default-off diff (new organ + reframe reading_grounding_loop.canonicalize), spec in SOLVED.md.
  * CAN BE ADDED TO   -- yes: add_edges() augments the graph; DEMONSTRATED with ConceptNet + SyntagNet
    (static offline foundation edges), each a clean ablation.
  * CAN LEARN         -- yes: learn_from_text() GROWS syntagmatic edges from reading (co-occurrence; the
    north-star mechanism in miniature -- a learned version of SyntagNet), can-fail vs an info-free twin.

Glass-box, LM-FREE at inference, deterministic. NO external LLM (the invariant).
"""
from __future__ import annotations

import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments.exp_grounded_semantic_graph_ladder_wsd_v1 import (
    _synsets_ordered, _relation_gloss_edges, _conceptnet_edges, _syntagnet_edges,
    _symmetrize, _row_stochastic, _sense_ppr, _sense_prior, _blend_pick, _learn_cooc_edges, _WNPOS,
)

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
