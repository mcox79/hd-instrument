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

================================================================================================
USAGE (for solvers -- this is the shared a_s INSTRUMENT the meaning-channel projects measure on)
================================================================================================
The organ scores CANDIDATE SENSES given CONTEXT; you feed it VECTORS. To pick a word's sense in context:

    from hdlab.diagnostic_context_wsd import pick_sense, diagnostic_context_scores
    # vec_lookup: str -> unit np.ndarray or None  (YOUR embedding space -- w2v gestalt / hub / your encoder)
    # context_words: the target's sentence, content words, target REMOVED
    # candidate_gloss_words: for each candidate WordNet synset, its gloss+example+lemma words (a word list)
    idx = pick_sense(context_words, candidate_gloss_words, vec_lookup)   # -> index of the picked synset (or None)

Or drive the pure mechanism yourself: build `context_vecs` (S? no -- (W,D) unit rows, one per in-vocab context
word) and `sense_gloss_vecs` ((S,D) unit rows, the MEAN gloss-word vector per candidate synset; a missing-gloss
sense = a ZERO row), then `tn[int(argmax(diagnostic_context_scores(context_vecs, sense_gloss_vecs)))]`.

WHAT A PROJECT VARIES: your knowledge/encoder change swaps the VECTORS fed in (better gloss signatures from
consolidated knowledge; a context-shaped target/context vector from a contextual encoder) -- the biased-competition
READOUT stays FIXED (that is the point: the readout is solved, the input is the lever). The a_s BAR is strict
document-disjoint SemCor, subordinate senses, subject-weighted accuracy, with a shuffled-context/diagnosticity twin
LOSING. REFERENCE HARNESS (build recs + embeddings + the a_s eval -- do NOT re-implement the loader/scorer):
`experiments/exp_sg_lite_diagnostic_context_readout_v1` (the DIAGCTX arm) + `exp_sg_lite_sense_gestalt_v1._gloss_vec`
(the per-synset gloss-vector builder) + its strict-disjoint SemCor a_s split. Witness: `test_diagnostic_context_wsd_organ.py`.
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
                     shuffle_rng: Optional[np.random.Generator] = None,
                     gamma: float = 1.0, topk: Optional[int] = None) -> np.ndarray:
    """The DIAGNOSTIC-weighted context query (unit). Falls back to the FLAT context mean when no context word is
    diagnostic (weight sum ~0). shuffle_rng permutes the weights onto the WRONG words -> the info-free twin
    (which must LOSE). VERBATIM to the cell's diag_q.

    PRECISION-WEIGHTING (P9 `build_the_atl_hub_and_spoke_meaning_channel...`, owner-DONE; Friston 2010 selective
    gain / Feldman-Friston -- precision is a MULTIPLICATIVE gain letting a high-precision subordinate cue overturn
    the dominant prior): `topk` keeps only the top-k most-diagnostic context words (hard selective gain); `gamma`
    is the sharpening exponent on the per-word diagnosticity. DEFAULT gamma=1.0, topk=None -> BYTE-IDENTICAL to
    the pre-P9 flat diagnostic query (both branches guarded off). On strict document-disjoint SemCor subordinate
    senses this lifts a_s 0.313 -> 0.336 (+0.023 CI-sep, shuffled-diagnosticity twin loses, NO MFS regression);
    it does NOT reach the ~0.35 static-distributional ceiling (that is the frozen sense-conflated input, not the
    readout). VERBATIM to exp_atl_hubspoke_query_side_readout_v1.readout_pick."""
    diag = diagnosticity(context_vecs, sense_gloss_vecs)
    if shuffle_rng is not None:
        diag = diag[shuffle_rng.permutation(len(diag))]
    if topk is not None and topk < len(diag):          # hard selective gain: keep only the top-k diagnostic words
        thr = np.sort(diag)[-topk]
        diag = np.where(diag >= thr, diag, 0.0)
    if gamma != 1.0:                                   # multiplicative precision sharpening (guarded -> byte-identical at 1.0)
        diag = diag ** gamma
    if float(diag.sum()) <= _EPS:
        return _unit(context_vecs.mean(axis=0))
    return _unit((diag[:, None] * context_vecs).sum(axis=0))


def diagnostic_context_scores(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray,
                              shuffle_rng: Optional[np.random.Generator] = None,
                              gamma: float = 1.0, topk: Optional[int] = None,
                              sense_prior: Optional[np.ndarray] = None,
                              prior_weight: float = 0.0) -> np.ndarray:
    """Biased-competition sense scores = cos(diagnostic-weighted query, each candidate sense gloss). Returns (S,);
    argmax = the picked sense. The wired a_s fix (DIAGCTX arm of the validated cell). All inputs UNIT vectors;
    a missing-gloss sense is a zero row (scores 0). Pass shuffle_rng to get the info-free twin's scores.
    gamma/topk = the P9 precision-weighting (default gamma=1.0, topk=None = byte-identical; see diagnostic_query).
    sense_prior/prior_weight = the BAYESIAN frequency-modulated competition (owner-DONE rare-sense readout
    `grow_broad_coverage_correctly_resolved_rare_sense_experience...`, 2026-09-04): frequency enters as a log-prior
    RESTING BIAS while STRONG context decides (MacDonald 1994 / McRae competition-integration, linearized), NOT as an
    additive dominant-forcing vote. `sense_prior` = a per-candidate frequency prior (SAME order as the gloss rows);
    `prior_weight` scales it. DEFAULT prior_weight=0.0 (or sense_prior=None) -> BYTE-IDENTICAL to the pure biased-
    competition scores. When active, returns prior_weight*log(prior) + zscore(context_score) -- the rare tail rises
    +0.065 CI-sep (SemCor, generalizes 6/6 frozen-weight), a strict PARETO win over the context-only readout; dev-
    select prior_weight on a held-out split (do NOT test-tune). Its only substrate consumer (consolidation_gate /
    learner) is default-off, so this is an OFF-by-default tuning knob (like gamma/topk), on for the day the meaning
    channel turns on (the owner's input-representation decision)."""
    q = diagnostic_query(context_vecs, sense_gloss_vecs, shuffle_rng, gamma=gamma, topk=topk)
    sc = sense_gloss_vecs @ q
    if sense_prior is not None and prior_weight:
        pr = np.asarray(sense_prior, dtype=np.float64).reshape(-1)
        z = (sc - sc.mean()) / (sc.std() + 1e-9)              # scale-free context; frequency = log resting bias
        sc = prior_weight * np.log(pr + 1e-6) + z
    return sc


def flat_context_scores(context_vecs: np.ndarray, sense_gloss_vecs: np.ndarray) -> np.ndarray:
    """The TOPIC-AVERAGE baseline (flat context mean x gloss) the diagnostic query beats +0.0389 CI-sep. Provided
    so a consumer can measure the biased-competition lift on its own population before defaulting it on."""
    q = _unit(context_vecs.mean(axis=0))
    return sense_gloss_vecs @ q


# ── convenience entry points (build the vectors from words + a lookup, then run the mechanism) ────────────────
def _stack_word_vecs(words, vec_lookup):
    """Unit rows for the in-vocab words (vec_lookup: word -> vector or None). Returns (K, D) float64 or None."""
    rows = []
    for w in words:
        v = vec_lookup(w)
        if v is not None:
            rows.append(_unit(np.asarray(v, dtype=np.float64).reshape(-1)))
    return np.stack(rows) if rows else None


def sense_gloss_vec(gloss_words, vec_lookup):
    """Per-synset gloss signature = the unit MEAN of its in-vocab gloss/example/lemma word vectors (the same
    construction as exp_sg_lite_sense_gestalt_v1._gloss_vec). Returns a unit (D,) vector, or None if no gloss
    word is in-vocab (the caller should pass a ZERO row for such a sense so it scores 0)."""
    M = _stack_word_vecs(gloss_words, vec_lookup)
    return None if M is None else _unit(M.mean(axis=0))


def pick_sense(context_words, candidate_gloss_words, vec_lookup, shuffle_rng=None,
               gamma: float = 1.0, topk: Optional[int] = None,
               sense_prior: Optional[np.ndarray] = None, prior_weight: float = 0.0):
    """Direct solver entry point: pick which candidate SENSE the context supports, by biased competition.
    context_words: the target's sentence content words (target REMOVED). candidate_gloss_words: a list (one per
    candidate synset, IN ORDER) of that synset's gloss+example+lemma words. vec_lookup: word -> vector or None
    (YOUR embedding space). Returns the INDEX of the picked candidate synset, or None if the context or every
    gloss is out-of-vocab (the caller keeps its own fallback -- e.g. the MFS/first synset). Pass shuffle_rng for
    the info-free twin. gamma/topk = the P9 precision-weighting (default = byte-identical; see diagnostic_query).
    Builds the vectors then calls diagnostic_context_scores (missing-gloss senses = zero rows)."""
    C = _stack_word_vecs(context_words, vec_lookup)
    if C is None or not candidate_gloss_words:
        return None
    gvs = [sense_gloss_vec(g, vec_lookup) for g in candidate_gloss_words]
    if all(g is None for g in gvs):
        return None
    D = C.shape[1]
    G = np.stack([g if g is not None else np.zeros(D, dtype=np.float64) for g in gvs])
    return int(np.argmax(diagnostic_context_scores(C, G, shuffle_rng, gamma=gamma, topk=topk,
                                                    sense_prior=sense_prior, prior_weight=prior_weight)))
