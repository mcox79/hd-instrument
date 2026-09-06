"""hdlab/underspecified_sense_reader.py -- the upgraded meaning-channel sense reader, PROMOTED (2026-09-06) from
experiments/exp_underspecified_sense_reader_v1.py (owner-DONE
select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub, SOLVED section 10e, Q111).
The SOLVED headline is a LOCATED NEGATIVE -- do NOT decorrelate/whiten the sense hub (provably argmax-neutral +
brain-unfaithful; NOTHING lands on the hub here). This module carries the problem's PROVEN POSITIVE: committing the
COARSE (shared-core) sense by default (a_s +0.169 CI-separated over the coarse-MFS floor + a context-shuffle twin).

THE FOUR UPGRADES (each measured in the problem's cells; see the SOLVED writeup):
  (1) UNDERSPECIFICATION-BY-DEFAULT (Frisson 2009 good-enough; Rodd 2002 shared-core). COMPETE FINE, COMMIT COARSE:
      the reader returns the shared-core cluster (WordNet lexname/supersense) as its default sense, retaining the
      fine synset for on-demand elaboration. Measured: this form beats merge-then-compete (+0.0425 CI-sep) AND the
      coarse-MFS floor (+0.169 CI-sep, witness U2) AND a context-shuffle twin (+0.120 CI-sep).
  (2) CLUSTER-FIRST COMPUTE MODE: mode="cluster_first" competes among shared-core cluster centroids -> ~56-60% fewer
      candidates at a ~0.043 accuracy cost (a brain-plausible accuracy/compute knob for constrained callers).
  (3) BIND (multiplicative) > BUNDLE (additive) joint-expectation composition (Lenci 2011 ECU; CI-sep in the
      problem): the `compose_joint` utility for the situation model's predictive role-composition component.
  (4) THE WIRE: source signatures from the curated hdlab.meaning_foundation hub and run the landed
      hdlab.diagnostic_context_wsd biased-competition readout WITH its precision (gamma/topk) + Bayesian log-prior
      (sense_prior/prior_weight) knobs -- the proven curated stack (beats the live PPR select_sense +0.0633 on WiC).

Glass-box, CPU numpy, NO external LLM at inference, ASCII. Imports ONLY hdlab.meaning_foundation +
hdlab.diagnostic_context_wsd + wordnet (+ a caller-supplied vec_lookup). `default_vec_lookup()` supplies the live
path's context vec_lookup (the sglite-w2v space the curated signatures live in) as a lazy static-asset loader that
DEGRADES GRACEFULLY (returns None on OOV / absent asset -> select_sense abstains, never raises).
"""
from __future__ import annotations
import os
import pickle
from typing import Callable, List, Optional, Sequence

import numpy as np

from hdlab import meaning_foundation as MF
from hdlab.diagnostic_context_wsd import diagnostic_context_scores

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The sglite-w2v space the curated meaning_foundation signatures live in (the DEFAULT context vec source for the
# live meaning stage). Static offline asset, on-disk per the project's data-asset convention (data/ is gitignored).
_W2V_ASSET = os.path.join(_REPO, "data", "_sglite_cache", "sglite_w2v_full.pkl")
_W2V = None            # lazy (w2i, mat float64) singleton
_EPS = 1e-9


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > _EPS else v


def _unit_rows(M: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(M, axis=1, keepdims=True)
    return M / np.where(n > _EPS, n, 1.0)


def coarse_cluster(synset_name: str) -> str:
    """The shared-core cluster of a synset = its WordNet lexicographer file (supersense). This is the brain's
    graded-shared-core grain (Rodd 2002); over-split fine synsets collapse to the sense the brain distinguishes.
    (A finer OntoNotes/CoarseWSD grouping can be dropped in here later; lexname is the always-available default.)"""
    from nltk.corpus import wordnet as wn
    try:
        return wn.synset(synset_name).lexname()
    except Exception:
        return synset_name


def _context_matrix(context_words: Sequence[str], vec_lookup: Callable[[str], Optional[np.ndarray]]) -> Optional[np.ndarray]:
    rows = []
    for w in context_words:
        v = vec_lookup(w)
        if v is not None:
            rows.append(np.asarray(v, dtype=np.float64).reshape(-1))
    return _unit_rows(np.stack(rows)) if rows else None


def select_sense(context_words: Sequence[str], vec_lookup: Callable[[str], Optional[np.ndarray]],
                 lemma: Optional[str] = None, pos: str = "n",
                 candidate_synsets: Optional[List[str]] = None, *,
                 mode: str = "underspecified",
                 gamma: float = 1.0, topk: Optional[int] = None,
                 sense_prior: Optional[np.ndarray] = None, prior_weight: float = 0.0) -> Optional[dict]:
    """The upgraded meaning-channel sense reader.

    context_words : the target's sentence content words (target removed).
    vec_lookup    : word -> unit vector or None (the substrate's sglite-w2v space; the live path injects it).
    lemma/pos     : the target (used to enumerate candidate synsets) -- OR pass candidate_synsets directly.
    mode          : "underspecified" (UPGRADE 1: compete FINE over the curated hub, COMMIT the coarse cluster) |
                    "cluster_first" (UPGRADE 2: compete among shared-core cluster centroids -- fewer candidates) |
                    "fine" (return the fine synset only -- the pre-upgrade behaviour, for A/B).
    gamma/topk/sense_prior/prior_weight : the landed diagnostic_context_wsd knobs (UPGRADE 4), default = byte-identical.

    Returns None if the target is out of vocabulary / has no covered signature, else:
      {"coarse": <lexname>, "fine": <synset or None>, "confidence": <top1-top2 margin>,
       "n_fine": <#fine candidates>, "n_coarse": <#clusters>, "distribution": {label: prob}}
    The DEFAULT committed sense is `coarse` (underspecified); `fine` is retained for on-demand elaboration.
    """
    from nltk.corpus import wordnet as wn
    if candidate_synsets is None:
        if lemma is None:
            raise ValueError("select_sense needs candidate_synsets or lemma")
        candidate_synsets = [s.name() for s in wn.synsets(lemma, pos=pos)]
    tn = list(candidate_synsets)
    if len(tn) < 1:
        return None
    C = _context_matrix(context_words, vec_lookup)
    G = MF.sense_signatures(tn)                                   # curated hub (UPGRADE 4)
    if C is None or not np.any(G):
        # abstain to the MFS cluster (first candidate) -- underspecified, context-free fallback
        return {"coarse": coarse_cluster(tn[0]), "fine": tn[0], "confidence": 0.0,
                "n_fine": len(tn), "n_coarse": len(set(coarse_cluster(s) for s in tn)), "distribution": {}}
    clusters = {}
    for k, s in enumerate(tn):
        if np.linalg.norm(G[k]) > _EPS:
            clusters.setdefault(coarse_cluster(s), []).append(k)
    n_coarse = len(clusters)

    if mode == "cluster_first":
        # UPGRADE 2: compete among shared-core cluster CENTROIDS (fewer candidates)
        lex = list(clusters.keys())
        Gc = np.stack([_unit(G[idx].mean(axis=0)) for idx in clusters.values()])
        sc = diagnostic_context_scores(C, Gc, gamma=gamma, topk=topk)
        order = np.argsort(-sc); win = int(order[0])
        margin = float(sc[order[0]] - sc[order[1]]) if len(sc) > 1 else 1.0
        # fine synset = best fine member of the winning cluster (for on-demand elaboration)
        members = clusters[lex[win]]
        fsc = diagnostic_context_scores(C, G[members], gamma=gamma, topk=topk)
        fine = tn[members[int(np.argmax(fsc))]]
        dist = _distribution(sc, lex)
        return {"coarse": lex[win], "fine": fine, "confidence": margin,
                "n_fine": len(tn), "n_coarse": n_coarse, "distribution": dist}

    # UPGRADE 1 (default): compete FINE over the curated hub with the landed knobs, COMMIT the coarse cluster.
    sc = diagnostic_context_scores(C, G, gamma=gamma, topk=topk, sense_prior=sense_prior, prior_weight=prior_weight)
    order = np.argsort(-sc)
    fine = tn[int(order[0])]
    margin = float(sc[order[0]] - sc[order[1]]) if len(sc) > 1 else 1.0
    if mode == "fine":
        return {"coarse": coarse_cluster(fine), "fine": fine, "confidence": margin,
                "n_fine": len(tn), "n_coarse": n_coarse, "distribution": _distribution(sc, tn)}
    # aggregate the fine distribution to clusters (the committed, underspecified read)
    return {"coarse": coarse_cluster(fine), "fine": fine, "confidence": margin,
            "n_fine": len(tn), "n_coarse": n_coarse,
            "distribution": _cluster_distribution(sc, tn)}


def _distribution(scores: np.ndarray, labels: Sequence[str]) -> dict:
    s = np.asarray(scores, float); s = s - s.max(); e = np.exp(3.0 * s); p = e / (e.sum() + _EPS)
    return {labels[i]: round(float(p[i]), 4) for i in range(len(labels))}


def _cluster_distribution(scores: np.ndarray, synsets: Sequence[str]) -> dict:
    s = np.asarray(scores, float); s = s - s.max(); e = np.exp(3.0 * s); p = e / (e.sum() + _EPS)
    out = {}
    for i, syn in enumerate(synsets):
        c = coarse_cluster(syn); out[c] = out.get(c, 0.0) + float(p[i])
    return {k: round(v, 4) for k, v in sorted(out.items(), key=lambda kv: -kv[1])}


# ---- UPGRADE 3: BIND (multiplicative) joint-expectation composition (Lenci 2011 ECU; bind > bundle CI-sep) ----
def compose_joint(base_scores: Sequence[float], filler_scores: Sequence[float], mode: str = "bind") -> np.ndarray:
    """Compose a role expectation with an already-filled sibling role's compatibility. BIND = multiplicative
    (softmax product = Bayesian-AND / feature intersection; the CI-sep winner + the substrate's structure-preserving
    composition); BUNDLE = additive (z-sum / superposition). Use BIND wherever the situation model composes multiple
    role-fillers into a JOINT expectation. Returns a score array; argmax = the jointly-most-expected candidate."""
    b = np.asarray(base_scores, float); f = np.asarray(filler_scores, float)
    if mode == "bundle":
        def _z(a):
            sd = a.std(); return (a - a.mean()) / sd if sd > 1e-12 else np.zeros(len(a))
        return _z(b) + _z(f)
    def _sm(a):
        a = a - a.max(); e = np.exp(3.0 * a); return e / (e.sum() + _EPS)
    return _sm(b) * _sm(f)


def default_vec_lookup() -> Callable[[str], Optional[np.ndarray]]:
    """The live meaning stage's DEFAULT context vec_lookup: the sglite-w2v space the curated meaning_foundation
    signatures live in (data/_sglite_cache/sglite_w2v_full.pkl). Returns a closure word -> UNIT float64 vector or
    None (OOV). Byte-faithful to the reference/witness lookup (float64 cast then unit-normalize). Lazy singleton
    (a reader that never invokes sm.select_sense pays nothing). DEGRADES GRACEFULLY -- if the gitignored asset is
    absent, returns a lookup that always yields None (select_sense then abstains, never raises), mirroring
    hdlab.meaning_foundation / hdlab.bridging_inference. NO external LLM."""
    global _W2V
    if _W2V is None:
        try:
            with open(_W2V_ASSET, "rb") as fh:
                emb = pickle.load(fh)
            _W2V = (emb["w2i"], np.asarray(emb["mat"], dtype=np.float64))
        except Exception:
            _W2V = ({}, None)
    w2i, mat = _W2V

    def _vl(word: str) -> Optional[np.ndarray]:
        i = w2i.get(word)
        if i is None or mat is None:
            return None
        return _unit(np.asarray(mat[i], dtype=np.float64))
    return _vl
