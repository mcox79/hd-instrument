"""hdlab/diagnostic_context_wsd.py -- the BIASED-COMPETITION diagnostic-context sense readout, promoted VERBATIM
(2026-09-03) from experiments/exp_sg_lite_diagnostic_context_readout_v1._readout (the owner-DONE north-star
build_sg_lite_self_supervised_scale_generative_sense_predictor).

WHAT THIS ORGAN IS. Picking a word's SPECIFIC (often rare/subordinate) sense in context. The naive readout forms
the query as a FLAT AVERAGE of the context words and scores each candidate sense by cos(query, gloss); that query
is a TOPIC-level blur (flat-context x gloss ~= the model's mean ~0.28) that cannot separate a rare sense from its
dominant twin sharing the topic. The brain does NOT average context -- it does BIASED COMPETITION / controlled
semantic cognition (LIFG/pMTG; Jefferies 2013; Lambon-Ralph 2017; word-level precision-weighting, Feldman-Friston):
AMPLIFY the context features that DISCRIMINATE the competing senses, SUPPRESS the shared (topic) ones.

MECHANISM (glass-box, CPU numpy, NO external LLM, GOLD-BLIND -- all candidate senses symmetric, no label):
for a target word with candidate-sense gloss vectors g_1..g_S and context-word vectors c_1..c_W (all unit), weight
each context word by its DIAGNOSTICITY = how much its cosine to the candidate gloss vectors VARIES across senses
(max - mean, clipped at 0): a word equally similar to all senses -> ~0 (non-diagnostic); a word much closer to one
sense -> high. The query is the diagnostic-weighted context mean; score sense s = cos(query, g_s); argmax = pick.

MEASURED (build_sg_lite, strict document-disjoint SemCor, subordinate senses, subject-weighted, n=2676): a_s
flat-context 0.268 -> DIAGNOSTIC 0.307 (+0.0389 CI-sep [+0.019,+0.059]) on 41M-token w2v, and 0.283 -> 0.326
(APEX, +0.0430 CI-sep) on 277M-token w2v (the fix STACKS with richer embeddings). The SHUFFLED-DIAGNOSTICITY twin
(the same weight distribution permuted onto the WRONG context words) LOSES CI-separated (real-vs-shuffled +0.0381)
-- so it is the CORRECT diagnostic words carrying the signal, not the weighting shape. It beats the top-k key-side
gloss variant (0.296) while running on the smaller gestalt, is the most brain-faithful arm, and is gestalt-
INDEPENDENT (needs only context-word + gloss vectors). >> the located-negative NB 0.198 and nearest-centroid 0.22.

ASSET-INDEPENDENT: the caller supplies the vectors from ANY embedding space (the north-star ships a w2v gestalt;
the WSD path could supply grounded/hub vectors). The residual ceiling (~0.35 glass-box) is the CONTEXT-INPUT
ENCODING (one sense-conflated vector per surface form), a separate contextual-encoder fork -- NOT this readout.
Glass-box, NO LLM. This is the a_s lever the meaning channel's controlled-knowledge growth feeds.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

_EPS = 1e-9


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > _EPS else v


def diagnosticity(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray) -> np.ndarray:
    """Per-context-word DIAGNOSTICITY = spread (max - mean) of its cosine to the candidate sense gloss vectors,
    clipped at 0. context_vecs (W, D) unit; sense_gloss_vecs (S, D) unit (missing-gloss senses = a zero row).
    Returns (W,) >= 0 -- high = the word discriminates the senses (biased competition), ~0 = topic-generic.
    VERBATIM to the validated cell: sim = C @ G.T ; diag = sim.max(1) - sim.mean(1) ; clip>=0."""
    sim = context_vecs @ sense_gloss_vecs.T                       # (W, S) cos(context word, sense gloss)
    d = sim.max(axis=1) - sim.mean(axis=1)
    return np.clip(d, 0.0, None)


def diagnostic_query(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray,
                     shuffle_rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """The DIAGNOSTIC-weighted context query (unit). Falls back to the FLAT context mean when no context word is
    diagnostic (weight sum ~0). shuffle_rng permutes the weights onto the WRONG words -> the info-free twin
    (which must LOSE). VERBATIM to the cell's diag_q."""
    diag = diagnosticity(context_vecs, sense_gloss_vecs)
    if shuffle_rng is not None:
        diag = diag[shuffle_rng.permutation(len(diag))]
    if float(diag.sum()) <= _EPS:
        return _unit(context_vecs.mean(axis=0))
    return _unit((diag[:, None] * context_vecs).sum(axis=0))


def diagnostic_context_scores(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray,
                              shuffle_rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Biased-competition sense scores = cos(diagnostic-weighted query, each candidate sense gloss). Returns (S,);
    argmax = the picked sense. The wired a_s fix (DIAGCTX arm of the validated cell). All inputs UNIT vectors;
    a missing-gloss sense is a zero row (scores 0). Pass shuffle_rng to get the info-free twin's scores."""
    q = diagnostic_query(context_vecs, sense_gloss_vecs, shuffle_rng)
    return sense_gloss_vecs @ q


def flat_context_scores(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray) -> np.ndarray:
    """The TOPIC-AVERAGE baseline (flat context mean x gloss) the diagnostic query beats +0.0389 CI-sep. Provided
    so a consumer can measure the biased-competition lift on its own population before defaulting it on."""
    q = _unit(context_vecs.mean(axis=0))
    return sense_gloss_vecs @ q
