"""hdlab/semantic_hub.py -- the ATL CONVERGENCE HUB: one amodal graded-meaning code per lemma, consolidated from the substrate's five
graded spokes (distributional phi, grounded-distinctive, valence, DINOv2 visual referent, per-lemma w2v aggregate).

Landed 2026-09-12 (strategy) from the owner-DONE pri-13 problem `consolidate_the_graded_lexical_semantic_stores_into_one_learned_
convergence_hub_with_task_readouts` (status PARTIAL by its own pre-registered test; reverified 14/14 first-hand).
BRAIN COMPUTATION (PINNED at the computational level): the anterior-temporal convergence hub (Rogers & McClelland 2004; Patterson,
Nestor & Rogers 2007; Jackson, Rogers & Lambon Ralph 2021): all modality-specific spokes pass through ONE shared nonlinear layer,
h = tanh(W.s + b), shaped by error-driven consolidation to reconstruct every spoke from every other (denoising, spoke dropout) and to
match the gold-free cross-spoke CONSENSUS similarity, precision-weighted (Ma & Pouget inverse variance; Cox et al. 2024
representational-similarity learning). MODEL: the autoencoder realisation and its width/dropout/sim weight (swept, not adopted).
MEASURED (solver, reverified): the one hub ties/beats EACH spoke on its own task (MEN 0.628 > concat 0.601 > best single 0.595;
twin -0.0005); precision weighting beats equal weighting (0.628 vs 0.615); the ONLINE (CLS slow-system, interleaved replay) path
reaches ~the batch equilibrium (0.577 vs 0.628). PRE-REGISTERED LIVE TEST FAILED: as the grounding DECISION the hub trails the
landed separate-pool precision fusion (0.2304 vs 0.2945, CI-sep) and as a 4th pool it TIES (0.3006) -- the read-time decision keeps
its separate pools (the semantic-dementia x amnesia double dissociation). SO: this organ is the REPRESENTATION store for graded
relatedness reads (one store instead of per-store islands), NOT a replacement for `reading_grounding_loop.FusedSenseRanker`.
WHAT IS LIVE HERE: numpy-only inference over the consolidated codes (`data/frontend_assets/semantic_hub_vectors_v1.npz`, built by
tools/build_semantic_hub_asset.py from the fitted weights). Re-consolidation (batch or online) = experiments/exp_semantic_hub_
convergence_v1.ConsensusHub (torch; the slow path), then rebuild the asset. No reader is repointed to this store yet: repointing is
per consumer, measured (byte-identical where the read is unchanged) -- recorded as follow-ons in INTEGRATION_LEDGER.
Glass-box; NO LLM / NO spaCy at inference.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import numpy as np

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = ("2026-09-12 strategy landing of owner-DONE pri-13 (PARTIAL; reverified 14/14): ATL convergence hub = one nonlinear shared "
                   "layer over the graded spokes, consolidated by denoising reconstruction + precision-weighted consensus RSA (Rogers-McClelland; "
                   "Ma-Pouget; Cox 2024); the read-time grounding decision stays with the separate-pool fusion (pre-registered test)")
__bf_note__ = "representation store only; the autoencoder realisation + width/dropout are MODEL; online CLS re-consolidation lives in the experiment class"

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET = os.path.join(_REPO, "data", "frontend_assets", "semantic_hub_vectors_v1.npz")


class SemanticHub:
    def __init__(self, vocab, vectors, n_spokes=None, spoke_names=None, hub_width=None, weights_source=""):
        self.vocab: List[str] = [str(w) for w in vocab]
        self.vectors: np.ndarray = np.asarray(vectors, dtype=np.float32)
        self.index: Dict[str, int] = {w: i for i, w in enumerate(self.vocab)}
        self.n_spokes = None if n_spokes is None else np.asarray(n_spokes)
        self.spoke_names = list(spoke_names) if spoke_names is not None else []
        self.hub_width = int(hub_width) if hub_width is not None else int(self.vectors.shape[1])
        self.weights_source = str(weights_source)

    @classmethod
    def load(cls, path: str = ASSET) -> "SemanticHub":
        z = np.load(path, allow_pickle=True)
        return cls(z["vocab"], z["vectors"], z.get("n_spokes"), z.get("spoke_names"), z.get("hub_width"), z.get("weights_source", ""))

    def _key(self, word: str) -> Optional[str]:
        w = word.lower().strip()
        if w in self.index:
            return w
        try:
            from hdlab.thematic_role_labeler import lemma_word   # glass-box morphology (hdlab.morphology)
            l = lemma_word(w)
            if l in self.index:
                return l
        except Exception:
            pass
        return None

    def covers(self, word: str) -> bool:
        return self._key(word) is not None

    def hub_vector(self, word: str) -> Optional[np.ndarray]:
        """Unit amodal convergence code for the word's lemma, or None if no spoke covers it."""
        k = self._key(word)
        return None if k is None else self.vectors[self.index[k]]

    def similarity(self, a: str, b: str) -> Optional[float]:
        """Graded relatedness = cosine of the two hub codes (None if either is uncovered)."""
        va, vb = self.hub_vector(a), self.hub_vector(b)
        if va is None or vb is None:
            return None
        return float(np.dot(va, vb))

    def neighbors(self, word: str, k: int = 10) -> List[Tuple[str, float]]:
        v = self.hub_vector(word)
        if v is None:
            return []
        s = self.vectors @ v
        order = np.argsort(-s)
        out = []
        for i in order:
            if self.vocab[i] == self._key(word):
                continue
            out.append((self.vocab[i], float(s[i])))
            if len(out) >= k:
                break
        return out


_INST: Optional[SemanticHub] = None


def get() -> SemanticHub:
    global _INST
    if _INST is None:
        _INST = SemanticHub.load()
    return _INST


def similarity(a: str, b: str) -> Optional[float]:
    return get().similarity(a, b)


def hub_vector(word: str) -> Optional[np.ndarray]:
    return get().hub_vector(word)


def covers(word: str) -> bool:
    return get().covers(word)


__all__ = ["SemanticHub", "get", "similarity", "hub_vector", "covers", "ASSET"]

if __name__ == "__main__":
    h = get()
    print("semantic hub: %d lemmas x %d-d (spokes %s; weights %s)" % (len(h.vocab), h.hub_width, h.spoke_names, h.weights_source))
    for a, b in [("dog", "cat"), ("dog", "democracy"), ("happy", "joyful"), ("car", "truck")]:
        print("  sim(%s, %s) = %s" % (a, b, h.similarity(a, b)))
    print("  neighbors(dog):", h.neighbors("dog", 6))
