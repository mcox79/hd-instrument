"""hdlab/meaning_fusion.py -- the GENERAL word-meaning read-out: COMPLEMENTARY FUSION of a
reading spoke and a grounded spoke (equal-weight z-fusion), NOT distillation.

WHAT THIS ORGAN IS (owner-accepted resolved mechanism, 2026-08-25). Word meaning in this substrate
is produced by INTEGRATING two partially-independent modality spokes, each a weak-but-real signal:

  * READING SPOKE  -- a PPMI+SVD distributional embedding built OFFLINE from the reader's separable
    co-occurrence store (hdlab.reading_grounding_loop.ConceptSpace, ROUTE B:
    track_context_counts / observe_context_counts / all_context_counts). Its phi is the SAME
    PPMI+SVD consolidation the substitutability organ uses -- this module reuses
    distributional_meaning_channel.ppmi_svd / _count_matrix byte-for-byte. WordSim-353 Spearman
    rho ~0.34-0.36 alone.
  * GROUNDED SPOKE -- hdlab.grounded_similarity.grounded_vector: a static, fully-built external
    asset (12-dim Lancaster sensorimotor + Brysbaert concreteness, z-scored). WordSim-353 rho
    ~0.38-0.41 alone.

The read-out is EQUAL-WEIGHT Z-FUSION: z(cos_reading) + z(cos_grounded), higher == more related.
On WordSim-353 this scores ~0.44-0.45 and beats BOTH spokes; the FUSION_EQUAL - GROUNDED delta is
CI-separated for 2/3 readers, and an information-free twin (the grounded assignment permuted across
words) LOSES CI-separated -- so the lift is grounding, not arithmetic
(experiments/exp_reader_meaning_integration_diag_v1.py; data/exp_reader_meaning_integration_diag_v1/
metrics.json, FROZEN: RAW 0.3567 / GROUNDED 0.3801 / FUSION_EQUAL 0.4455, delta-over-GROUNDED
+0.0654 CI [0.0094, 0.1236], FUSION_EQUAL - FUSION_SHUFFLE +0.19 CI [0.0639, 0.3141]).

NOT DISTILLATION. Making the reading spoke MIMIC the grounded spoke (the "SUBSTITUTIVE" arm) scores
rho -0.24 on WordSim-353 -- BELOW raw reading -- because substitutability and general relatedness
are near-opposite here. The already-landed hdlab/distributional_meaning_channel.py is a
SUBSTITUTABILITY specialist (its own docstring says so) and MUST NOT be used as the general
read-out. THIS organ is the general one; it reuses the other's PPMI+SVD math but fuses the two
spokes complementarily instead of collapsing one into the other.

------------------------------------------------------------------------------------------------
OPT-IN CONCEPTUAL IDENTITY CHANNEL (wired 2026-08-30; DEFAULT-OFF -- owner-directed).
------------------------------------------------------------------------------------------------
The reading+grounded fusion above is a RELATEDNESS read-out (what a word goes WITH; validated on
WordSim-353). The brain has a SECOND, dissociable meaning system: the ATL amodal hub that reads
IDENTITY / TAXONOMIC SIMILARITY (what a word IS; validated on SimLex-999 / SimVerb by
hdlab/conceptual_meaning.ConceptualChannel -- rho 0.521 vs a steelmanned GloVe 0.371, CI-separated;
a DOUBLE DISSOCIATION holds: conceptual->similarity, associative->relatedness). Until now that hub
was an ISLAND -- imported by no live read-out. This organ now COMPOSES it in, DEMAND-ROUTED, so the
reader has both systems:

  * demand='relatedness' (THE DEFAULT) -> the reading+grounded z-fusion, UNCHANGED. With the
    conceptual channel OFF (the default build), the object is byte-identical to before and every
    existing method / self-test / witness number is preserved. This is the wire-don't-break invariant.
  * demand='similarity'  -> the ATL conceptual hub (hdlab.conceptual_meaning). GRADABLE-ADJECTIVE
    pairs route instead to the scalar-magnitude "ruler" via hdlab.meaning_operation_router (the
    validated word-class router; magnitude is a "how much" op, NOT a similarity op, so it is added
    for gradable adjectives, never used on nouns/verbs). The magnitude channel is INJECTED (it needs
    heavy external norm assets); absent one, gradable-adjective pairs fall back to the conceptual op
    with an HONEST recorded label, not silently.
  * demand='rating'      -> decontextualised graded RATING with NO known demand: FUSE (not switch)
    the conceptual and relatedness signals (z-combined over the batch), per the organ's validated
    "fusion ties/beats routing for rating" finding.

ROUTING, NOT POOLING (preserve the double dissociation): the channels are kept separate and one is
SELECTED by the demand + word class; the similarity signal is never averaged into the relatedness
pool (that would destroy both -- magnitude-on-nouns 0.066 vs gloss 0.599). Enable via
build(..., enable_conceptual=True) or by passing a ConceptualChannel/router explicitly.

------------------------------------------------------------------------------------------------
BRAIN-FOUNDATIONAL LABELLING (which structure, and are we replicating it or substituting?)
------------------------------------------------------------------------------------------------
PINNED-BY-EVIDENCE (a described neural operation):
  * HUB-AND-SPOKE COMPLEMENTARY INTEGRATION (Patterson 2007; Lambon Ralph 2017). The anterior
    temporal-lobe amodal hub integrates modality spokes so the integrated code is >= either spoke
    alone; here a distributional/linguistic spoke and a sensorimotor/affective spoke are integrated
    complementarily, and the integrated read-out beats each spoke -- the defining signature.
  * DISTRIBUTIONAL SEMANTICS for the reading spoke (Firth 1957; PPMI+SVD is a standard model of
    slow neocortical extraction of co-occurrence structure). Run OFFLINE (consolidation is slow),
    never at inference.
  * SUPPLIED GROUNDED ASSET == the FOUNDATION pivot (USER 2026-07-14): the grounded norms are a
    static, external, fully-built asset used as foundation, not learned at inference. NO LLM.

OUR-INVENTION-UNDER-TEST (we chose this; not pinned to a recording):
  * EQUAL-WEIGHT Z-FUSION as the software FORM of hub integration. The brain's actual cross-modal
    combination rule is not recorded at this resolution. Equal-weight z-fusion is validated as
    SUFFICIENT (it beats both spokes, CI-separated over the stronger, with an info-free twin that
    loses) -- NOT as OPTIMAL. The diagnostic alpha-sweep shows a tuned weight near alpha=0.5-0.6 is
    marginally better, but equal weight is the untuned, label-free, honest default and is what is
    validated. Sweeping the weight is a licensed future refinement, not a claim made here.
  * THE Z-SCORING REFERENCE POPULATION (below) is a design choice; documented, not pinned.

------------------------------------------------------------------------------------------------
Z-SCORING AND THE READ-OUT SURFACE (the design point this organ had to resolve, resolved honestly).
------------------------------------------------------------------------------------------------
Fusion adds two cosines that live on DIFFERENT scales, so each is z-standardized first (label-free
-- z uses only the cosine distribution, never the gold scores). The Spearman of the fused ranking
depends on the RATIO of the two spokes' z-scales, hence on the population the z-statistics are
computed over. The diagnostic cell z-scores over the presented eval batch. This organ exposes both
faithful surfaces, mirroring hdlab.distributional_meaning_channel's batch/single split:

  * similarity_batch(pairs) -- THE FAITHFUL READ-OUT. z-standardizes each spoke's cosine over the
    in-vocabulary subset of the PRESENTED batch (label-free) and fuses. This reproduces the
    diagnostic cell's FUSION_EQUAL exactly. Use it whenever a batch of candidate pairs is available.
  * similarity(a, b, reference_pairs=None) -- single-pair convenience. With reference_pairs it
    routes through similarity_batch (faithful). WITHOUT one it z-scores against a DOCUMENTED,
    build-time REFERENCE POPULATION (N_REF_PAIRS random in-both-vocabulary pairs, fixed seed) whose
    per-spoke (mean, sd) are frozen at build() time. This is a fully inductive single-pair read-out;
    it agrees closely with the batch form when the reference population is representative, and any
    residual difference is reported by the witness, not hidden.

OOV POLICY (documented and honest). A word may be missing from one spoke or both.
  * both spokes cover the pair  -> fuse: 0.5*z(cos_reading) + 0.5*z(cos_grounded).
  * only the reading spoke      -> fall back to z(cos_reading) alone.
  * only the grounded spoke     -> fall back to z(cos_grounded) alone.
  * neither spoke covers a word -> None ("cannot judge").
The clean, validated instrument is the BOTH-COVERED population (what the diagnostic measures and
what the witness scores). Ranking single-spoke fallbacks against both-covered fused scores in ONE
ordering is only APPROXIMATELY comparable (a fused sum and a lone z have different spread); the
fallback exists to EXTEND coverage honestly, not to assert the two are on an identical scale.

Glass-box, CPU-only, single-threaded pins at top, deterministic (fixed seeds), NO LLM. ASCII-only.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from collections import Counter
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

# Reuse the substitutability organ's PPMI+SVD consolidation byte-for-byte (wire-don't-island): the
# reading spoke's phi IS the same consolidated distributional space.
from hdlab.distributional_meaning_channel import _count_matrix, l2n, ppmi_svd
from hdlab.grounded_similarity import grounded_vector

SVD_K = 100                 # == distributional_meaning_channel.SVD_K / build_phi SVD_K
MASTER_SEED = 20260824      # == distributional_meaning_channel.MASTER_SEED (ppmi_svd determinism)
N_REF_PAIRS = 5000          # size of the documented build-time z-reference population
REF_SEED = 8112025          # fixed seed for the reference-pair sample (deterministic)
_EPS = 1e-12


def _z_vals(x: np.ndarray) -> np.ndarray:
    """z-standardize a 1-D array (== the diagnostic cell's _z: (x - mean) / (std + eps))."""
    return (x - x.mean()) / (x.std() + _EPS)


def _grounded_unit(word: str, grounded_fn: Callable[[str], Optional[object]]
                   ) -> Optional[np.ndarray]:
    """L2-normalized grounded vector for `word`, or None if the grounded spoke is OOV. Matches the
    diagnostic cell's gv_u: np.asarray(grounded_vector(w).tolist()) then divide by its norm."""
    v = grounded_fn(word)
    if v is None:
        return None
    a = np.asarray(v.tolist() if hasattr(v, "tolist") else v, dtype=np.float64)
    n = float(np.linalg.norm(a))
    if n < _EPS:
        return None
    return a / n


class MeaningFusion:
    """Reading-spoke distributional embedding + grounded-spoke accessor + a frozen z-reference.

    THE faithful read-out is similarity_batch(pairs). Single-pair similarity(a, b) uses a
    build-time reference population to z-score, or a caller-supplied reference batch (see the module
    Z-SCORING note)."""

    def __init__(self, words: List[str], row_idx: Dict[str, int], phi: np.ndarray,
                 grounded_fn: Callable[[str], Optional[object]],
                 ref_stats: Dict[str, float], weights: Tuple[float, float] = (0.5, 0.5),
                 ref_n_pairs: int = 0,
                 conceptual: Optional[object] = None,
                 router_fn: Optional[Callable[[str, Optional[str]], str]] = None,
                 magnitude_fn: Optional[Callable[[str, str], Optional[float]]] = None) -> None:
        self.words = words
        self.row_idx = row_idx
        self.phi = phi                       # l2-normalized reading rows [n_words, k]
        self.grounded_fn = grounded_fn
        self.ref_stats = dict(ref_stats)     # mu_r, sd_r, mu_g, sd_g over the reference population
        self.w_read, self.w_grnd = float(weights[0]), float(weights[1])
        self.ref_n_pairs = int(ref_n_pairs)
        self.n_words = len(words)
        self.n_dim = int(phi.shape[1]) if phi.size else 0
        self._grnd_cache: Dict[str, Optional[np.ndarray]] = {}
        # OPT-IN identity channel (default OFF -> pure relatedness read-out, byte-identical to before):
        self.conceptual = conceptual          # a ConceptualChannel-like object with .similarity(w1,pos1,w2,pos2)
        self.router_fn = router_fn            # meaning_operation_router.route(word,pos) -> 'magnitude'|'conceptual'
        self.magnitude_fn = magnitude_fn      # optional injected pair->score for gradable-adjective magnitude

    # ---- spoke cosines -------------------------------------------------------------------------
    def _reading_index(self, word: str) -> Optional[int]:
        i = self.row_idx.get(word)
        if i is None:
            i = self.row_idx.get(word.lower())
        return i

    def _reading_cos(self, a: str, b: str) -> Optional[float]:
        ia, ib = self._reading_index(a), self._reading_index(b)
        if ia is None or ib is None:
            return None
        # phi rows are already unit-norm (ppmi_svd L2-normalizes), so dot == cosine.
        return float(np.dot(self.phi[ia], self.phi[ib]))

    def _grounded_vec(self, word: str) -> Optional[np.ndarray]:
        key = word.lower()
        if key in self._grnd_cache:
            return self._grnd_cache[key]
        u = _grounded_unit(word, self.grounded_fn)
        self._grnd_cache[key] = u
        return u

    def _grounded_cos(self, a: str, b: str) -> Optional[float]:
        ua, ub = self._grounded_vec(a), self._grounded_vec(b)
        if ua is None or ub is None:
            return None
        return float(np.dot(ua, ub))

    def coverage(self, word: str) -> Tuple[bool, bool]:
        """(in_reading_spoke, in_grounded_spoke) for `word`."""
        return (self._reading_index(word) is not None, self._grounded_vec(word) is not None)

    # ---- THE faithful read-out: batch z-fusion over the presented pairs ------------------------
    def similarity_batch(self, pairs: Sequence[Tuple[str, str]]) -> List[Optional[float]]:
        """General meaning read-out over a batch. Higher == more related. Returns one score per
        input pair (None where NEITHER spoke covers a word). z-standardizes each spoke over the
        subset of `pairs` that spoke covers (label-free), then fuses 0.5*z_read + 0.5*z_grnd where
        both cover, else the single covered spoke's z. Reproduces the diagnostic cell when `pairs`
        is the WordSim-353 both-covered set."""
        n = len(pairs)
        cr: List[Optional[float]] = [None] * n
        cg: List[Optional[float]] = [None] * n
        for k, (a, b) in enumerate(pairs):
            cr[k] = self._reading_cos(a, b)
            cg[k] = self._grounded_cos(a, b)
        r_idx = [k for k in range(n) if cr[k] is not None]
        g_idx = [k for k in range(n) if cg[k] is not None]
        zr: Dict[int, float] = {}
        zg: Dict[int, float] = {}
        if r_idx:
            zvals = _z_vals(np.array([cr[k] for k in r_idx], dtype=np.float64))
            zr = {k: float(zvals[j]) for j, k in enumerate(r_idx)}
        if g_idx:
            zvals = _z_vals(np.array([cg[k] for k in g_idx], dtype=np.float64))
            zg = {k: float(zvals[j]) for j, k in enumerate(g_idx)}
        out: List[Optional[float]] = [None] * n
        for k in range(n):
            hr, hg = k in zr, k in zg
            if hr and hg:
                out[k] = self.w_read * zr[k] + self.w_grnd * zg[k]
            elif hr:
                out[k] = zr[k]
            elif hg:
                out[k] = zg[k]
            else:
                out[k] = None
        return out

    # ---- single-pair convenience ---------------------------------------------------------------
    def similarity(self, word_a: str, word_b: str,
                   reference_pairs: Optional[Sequence[Tuple[str, str]]] = None) -> Optional[float]:
        """Single-pair meaning read-out. Higher == more related. None if NEITHER spoke covers a
        word. With `reference_pairs` (a representative batch the query is drawn from) it routes
        through similarity_batch and is faithful. WITHOUT one it z-scores each spoke against the
        DOCUMENTED build-time reference population (see the module Z-SCORING note)."""
        if reference_pairs is not None:
            scored = self.similarity_batch(list(reference_pairs) + [(word_a, word_b)])
            return scored[-1]
        cr = self._reading_cos(word_a, word_b)
        cg = self._grounded_cos(word_a, word_b)
        zr = ((cr - self.ref_stats["mu_r"]) / (self.ref_stats["sd_r"] + _EPS)
              if cr is not None else None)
        zg = ((cg - self.ref_stats["mu_g"]) / (self.ref_stats["sd_g"] + _EPS)
              if cg is not None else None)
        if zr is not None and zg is not None:
            return self.w_read * zr + self.w_grnd * zg
        if zr is not None:
            return zr
        if zg is not None:
            return zg
        return None

    # ---- OPT-IN routed read-out: relatedness (default) | similarity (ATL) | rating (fuse) --------
    def route_pair(self, word_a: str, pos_a: Optional[str], word_b: str, pos_b: Optional[str],
                   demand: str) -> str:
        """Transparent dispatch decision for a meaning pair (glass-box). Returns the CHANNEL label:
          'relatedness'  -> reading+grounded z-fusion (the default associative read-out)
          'conceptual'   -> the ATL identity/similarity hub
          'magnitude'    -> the scalar 'ruler' (BOTH words gradable adjectives AND a magnitude_fn present)
          'magnitude_unavailable' -> both gradable but no magnitude_fn injected (falls back to conceptual, recorded)
          'rating'       -> fuse conceptual + relatedness (decontextualised graded rating)
        With NO conceptual channel wired (the default object), ALWAYS 'relatedness' -- the organ simply
        has no identity system yet, reported honestly (never a silent similarity degrade)."""
        if self.conceptual is None or demand == "relatedness":
            return "relatedness"
        both_gradable = (self.router_fn is not None
                         and self.router_fn(word_a, pos_a) == "magnitude"
                         and self.router_fn(word_b, pos_b) == "magnitude")
        if both_gradable:
            return "magnitude" if self.magnitude_fn is not None else "magnitude_unavailable"
        if demand == "rating":
            return "rating"
        return "conceptual"

    def _conceptual_cos(self, word_a: str, pos_a: Optional[str], word_b: str,
                        pos_b: Optional[str]) -> Optional[float]:
        if self.conceptual is None:
            return None
        return self.conceptual.similarity(word_a, pos_a or "N", word_b, pos_b or "N")

    def meaning(self, word_a: str, word_b: str, *, pos_a: Optional[str] = "N",
                pos_b: Optional[str] = "N", demand: str = "relatedness",
                reference_pairs: Optional[Sequence[Tuple[str, str]]] = None) -> Optional[float]:
        """Routed single-pair meaning read-out. `demand` in {'relatedness','similarity','rating'}.
        Higher == more related/similar. None where the routed channel cannot judge the pair.
        DEFAULT demand='relatedness' with no conceptual channel == self.similarity(...) exactly."""
        label = self.route_pair(word_a, pos_a, word_b, pos_b, demand)
        if label == "relatedness":
            return self.similarity(word_a, word_b, reference_pairs)
        if label == "magnitude":
            return self.magnitude_fn(word_a, word_b)  # type: ignore[misc]
        if label in ("conceptual", "magnitude_unavailable"):
            return self._conceptual_cos(word_a, pos_a, word_b, pos_b)
        # label == 'rating': fuse a single pair via the frozen reference z-stats + the conceptual cos.
        rel = self.similarity(word_a, word_b, reference_pairs)
        con = self._conceptual_cos(word_a, pos_a, word_b, pos_b)
        if rel is not None and con is not None:
            return 0.5 * rel + 0.5 * con
        return rel if rel is not None else con

    def meaning_batch(self, items: Sequence[Tuple[str, Optional[str], str, Optional[str]]],
                      demand: str = "relatedness") -> List[Optional[float]]:
        """Routed batch read-out over (word_a, pos_a, word_b, pos_b) tuples. THE faithful surface.
          relatedness -> similarity_batch (z over the batch), UNCHANGED.
          similarity  -> per-item conceptual cosine (already comparable in [0,1]); gradable-adj pairs
                         route to magnitude_fn if present, else the conceptual op (recorded label).
          rating      -> z-standardize BOTH the relatedness fusion and the conceptual cosine over the
                         items each covers (label-free), then average where both are present."""
        if self.conceptual is None or demand == "relatedness":
            return self.similarity_batch([(a, b) for (a, _pa, b, _pb) in items])
        n = len(items)
        con: List[Optional[float]] = [None] * n
        for k, (a, pa, b, pb) in enumerate(items):
            label = self.route_pair(a, pa, b, pb, demand if demand != "rating" else "similarity")
            if label == "magnitude":
                con[k] = self.magnitude_fn(a, b)  # type: ignore[misc]
            else:
                con[k] = self._conceptual_cos(a, pa, b, pb)
        if demand == "similarity":
            return con
        # rating: fuse z(relatedness) + z(conceptual) over covered items.
        rel = self.similarity_batch([(a, b) for (a, _pa, b, _pb) in items])
        r_idx = [k for k in range(n) if rel[k] is not None]
        c_idx = [k for k in range(n) if con[k] is not None]
        zr: Dict[int, float] = {}
        zc: Dict[int, float] = {}
        if r_idx:
            zvals = _z_vals(np.array([rel[k] for k in r_idx], dtype=np.float64))
            zr = {k: float(zvals[j]) for j, k in enumerate(r_idx)}
        if c_idx:
            zvals = _z_vals(np.array([con[k] for k in c_idx], dtype=np.float64))
            zc = {k: float(zvals[j]) for j, k in enumerate(c_idx)}
        out: List[Optional[float]] = [None] * n
        for k in range(n):
            hr, hc = k in zr, k in zc
            if hr and hc:
                out[k] = 0.5 * zr[k] + 0.5 * zc[k]
            elif hr:
                out[k] = zr[k]
            elif hc:
                out[k] = zc[k]
        return out


def _reference_stats(words: List[str], phi: np.ndarray, row_idx: Dict[str, int],
                     grounded_fn: Callable[[str], Optional[object]],
                     n_pairs: int, seed: int) -> Tuple[Dict[str, float], int]:
    """Build-time z-reference: sample `n_pairs` random pairs (fixed seed) from lemmas covered by
    BOTH spokes, return per-spoke (mean, sd) of their cosines. Documented, label-free (uses only
    cosine distributions, never gold scores)."""
    both = sorted(w for w in words if _grounded_unit(w, grounded_fn) is not None)
    stats = {"mu_r": 0.0, "sd_r": 1.0, "mu_g": 0.0, "sd_g": 1.0}
    if len(both) < 2:
        return stats, 0
    gunit = {w: _grounded_unit(w, grounded_fn) for w in both}
    rng = np.random.default_rng(seed)
    ii = rng.integers(0, len(both), (n_pairs, 2))
    ii = ii[ii[:, 0] != ii[:, 1]]
    cr = np.empty(len(ii), dtype=np.float64)
    cg = np.empty(len(ii), dtype=np.float64)
    for t, (i, j) in enumerate(ii):
        a, b = both[int(i)], both[int(j)]
        cr[t] = float(np.dot(phi[row_idx[a]], phi[row_idx[b]]))
        cg[t] = float(np.dot(gunit[a], gunit[b]))
    stats = {"mu_r": float(cr.mean()), "sd_r": float(cr.std() + _EPS),
             "mu_g": float(cg.mean()), "sd_g": float(cg.std() + _EPS)}
    return stats, int(len(ii))


def build(context_counts: Dict[str, "Counter[str]"], *,
          grounded_fn: Callable[[str], Optional[object]] = grounded_vector,
          svd_k: int = SVD_K, seed: int = MASTER_SEED,
          n_ref_pairs: int = N_REF_PAIRS, ref_seed: int = REF_SEED,
          weights: Tuple[float, float] = (0.5, 0.5),
          enable_conceptual: bool = False,
          conceptual: Optional[object] = None,
          router_fn: Optional[Callable[[str, Optional[str]], str]] = None,
          magnitude_fn: Optional[Callable[[str, str], Optional[float]]] = None) -> MeaningFusion:
    """OFFLINE build of the general meaning read-out from the reading loop's separable
    co-occurrence store.

    context_counts : Dict[lemma -> Counter(context_lemma -> count)] == ConceptSpace.all_context_counts().
    grounded_fn    : the grounded spoke accessor (default hdlab.grounded_similarity.grounded_vector).
    Steps: (1) count matrix over the store's lemmas (reuses _count_matrix), (2) PPMI+SVD -> phi
    (reuses ppmi_svd; L2-normalized rows), (3) freeze the documented z-reference population.
    Deterministic (fixed seeds). NO distillation, NO LLM.

    OPT-IN identity channel (DEFAULT-OFF): with enable_conceptual=True (or an explicit `conceptual`
    object), the returned read-out also serves demand='similarity'/'rating' by DEMAND-ROUTING to the
    ATL conceptual hub (hdlab.conceptual_meaning) + the word-class router (hdlab.meaning_operation_
    router). Imports are LAZY -- the default build touches neither module, so import-time behaviour and
    every existing number are byte-identical. `magnitude_fn` optionally injects the scalar-magnitude op
    for gradable-adjective pairs (it needs heavy external norm assets, so it is not built here)."""
    words = list(context_counts.keys())
    if not words:
        raise ValueError("empty context_counts: nothing to consolidate")
    vocab: Dict[str, int] = {}
    for w in words:
        for c in context_counts[w]:
            vocab.setdefault(c, len(vocab))
    if not vocab:
        raise ValueError("context_counts has no context columns: cannot build a reading spoke")
    M = _count_matrix(words, context_counts, vocab)
    k = min(int(svd_k), min(M.shape) - 1)
    if k < 2:
        raise ValueError("count matrix too small for SVD (min(shape)=%d)" % min(M.shape))
    phi = ppmi_svd(M, svd_k=k, seed=seed)          # l2n unit rows [n_words, k]
    row_idx = {w: i for i, w in enumerate(words)}
    ref_stats, ref_n = _reference_stats(words, phi, row_idx, grounded_fn, n_ref_pairs, ref_seed)
    if enable_conceptual and conceptual is None:
        from hdlab.conceptual_meaning import ConceptualChannel     # lazy: only when opted in
        conceptual = ConceptualChannel()
    if conceptual is not None and router_fn is None:
        from hdlab.meaning_operation_router import route as _mor_route   # lazy
        router_fn = _mor_route
    return MeaningFusion(words, row_idx, phi, grounded_fn, ref_stats, weights, ref_n,
                         conceptual=conceptual, router_fn=router_fn, magnitude_fn=magnitude_fn)


# ================================================================================================
# self-test -- DATA-FREE formula + policy checks (no store, no CSVs). End-to-end validation against
# the diagnostic numbers lives in the witness (drives the live ConceptSpace store).
# ================================================================================================
def self_test() -> Dict:
    ev: Dict[str, object] = {}
    rng = np.random.default_rng(20260825)

    # (1) KNOWN-ANSWER discriminator (== the diagnostic cell's self-test): two channels each carrying
    # HALF the true signal under independent noise -> equal-weight z-fusion must beat the better
    # single channel; an info-free (shuffled) channel fused with reading must NOT beat reading.
    n = 600
    true = rng.standard_normal(n)
    cos_r = true + 1.4 * rng.standard_normal(n)
    cos_g = true + 1.4 * rng.standard_normal(n)
    cos_shuf = rng.standard_normal(n)                     # info-free
    from scipy.stats import spearmanr
    fe = 0.5 * _z_vals(cos_r) + 0.5 * _z_vals(cos_g)
    fsh = 0.5 * _z_vals(cos_r) + 0.5 * _z_vals(cos_shuf)
    r_r = float(spearmanr(cos_r, true)[0])
    r_g = float(spearmanr(cos_g, true)[0])
    r_fe = float(spearmanr(fe, true)[0])
    r_fsh = float(spearmanr(fsh, true)[0])
    assert r_fe > r_r and r_fe > r_g, "discriminator did NOT fire: fusion must beat both spokes"
    assert r_fsh <= max(r_r, r_g) + 1e-9, "info-free twin beat a real spoke (arithmetic artifact)"
    ev["toy_fusion_beats_spokes"] = {"raw": round(r_r, 4), "grnd": round(r_g, 4),
                                     "fusion": round(r_fe, 4), "shuffle": round(r_fsh, 4)}

    # (2) build a tiny MeaningFusion by hand (no CSVs): 4 reading words with distinct unit rows, a
    # dict-based grounded spoke that covers only some of them, and a documented reference stat.
    words = ["alpha", "beta", "gamma", "delta"]
    phi = l2n(rng.standard_normal((4, 6)))
    row_idx = {w: i for i, w in enumerate(words)}
    gtable = {"alpha": np.array([1.0, 0.0, 0.0]), "beta": np.array([0.9, 0.1, 0.0]),
              "gamma": np.array([0.0, 1.0, 0.0])}         # delta grounded-OOV; "omega" reading-OOV
    gfn = lambda w: gtable.get(w.lower())
    ref = {"mu_r": 0.0, "sd_r": 0.5, "mu_g": 0.0, "sd_g": 0.5}
    mf = MeaningFusion(words, row_idx, phi, gfn, ref, weights=(0.5, 0.5))

    # (3) OOV policy (single-pair, build-reference path):
    assert mf.similarity("alpha", "beta") is not None, "both-covered pair must score"
    assert mf.similarity("alpha", "delta") is not None, "reading-only pair must fall back, not None"
    assert mf.similarity("gamma", "delta") is not None, "reading-only pair must fall back, not None"
    # "omega" is OOV of reading; but grounded-OOV too (not in gtable) -> None on both spokes.
    assert mf.similarity("omega", "zzz") is None, "pair OOV of BOTH spokes must be None"
    # a grounded-only pair: neither in reading vocab, but both grounded -> grounded fallback.
    gtable["omega"] = np.array([0.0, 0.0, 1.0]); gtable["psi"] = np.array([0.2, 0.0, 0.9])
    mf2 = MeaningFusion(words, row_idx, phi, lambda w: gtable.get(w.lower()), ref, (0.5, 0.5))
    assert mf2.similarity("omega", "psi") is not None, "grounded-only pair must fall back, not None"
    ev["oov_policy_ok"] = True

    # (4) determinism: same pair twice -> bit-identical.
    assert mf.similarity("alpha", "beta") == mf.similarity("alpha", "beta"), "nondeterministic"
    ev["determinism_ok"] = True

    # (5) batch read-out matches the diagnostic z-fusion arithmetic on a both-covered batch.
    pairs = [("alpha", "beta"), ("alpha", "gamma"), ("beta", "gamma")]
    got = mf.similarity_batch(pairs)
    crv = np.array([mf._reading_cos(a, b) for a, b in pairs])
    cgv = np.array([mf._grounded_cos(a, b) for a, b in pairs])
    want = 0.5 * _z_vals(crv) + 0.5 * _z_vals(cgv)
    assert all(g is not None for g in got) and np.allclose(np.array(got), want, atol=1e-12), \
        "similarity_batch must equal 0.5*z(reading)+0.5*z(grounded) over the batch"
    ev["batch_matches_zfusion_formula"] = True

    # (6) OPT-IN routing logic (DATA-FREE: inject a FAKE conceptual channel + FAKE router, no WordNet).
    # (6a) DEFAULT object (no conceptual) is a pure relatedness read-out: any demand -> 'relatedness',
    #      and meaning(demand='relatedness') == similarity(...) EXACTLY (the byte-identical invariant).
    assert mf.route_pair("alpha", "N", "beta", "N", "similarity") == "relatedness", \
        "no conceptual channel -> must honestly stay relatedness, never a silent similarity degrade"
    assert mf.meaning("alpha", "beta", demand="relatedness") == mf.similarity("alpha", "beta"), \
        "default routed read-out must equal the unchanged relatedness path"

    class _FakeConc:                                        # a stand-in ConceptualChannel
        def similarity(self, w1, p1, w2, p2):
            return 0.99 if w1 == w2 else 0.11
    fake_router = lambda w, p: "magnitude" if w in ("big", "small") else "conceptual"  # noqa: E731
    mfc = MeaningFusion(words, row_idx, phi, gfn, ref, (0.5, 0.5),
                        conceptual=_FakeConc(), router_fn=fake_router,
                        magnitude_fn=lambda a, b: 0.77)
    # (6b) demand routing: relatedness->fusion, similarity(noun)->conceptual, similarity(2 gradable adj)->magnitude.
    assert mfc.route_pair("dog", "N", "cat", "N", "relatedness") == "relatedness"
    assert mfc.route_pair("dog", "N", "cat", "N", "similarity") == "conceptual"
    assert mfc.route_pair("big", "A", "small", "A", "similarity") == "magnitude"
    assert mfc.route_pair("big", "A", "cat", "N", "similarity") == "conceptual", \
        "only BOTH-gradable pairs take the magnitude ruler"
    # (6c) routed values dispatch to the chosen channel.
    assert mfc.meaning("big", "small", pos_a="A", pos_b="A", demand="similarity") == 0.77, "magnitude route"
    assert mfc.meaning("dog", "dog", pos_a="N", pos_b="N", demand="similarity") == 0.99, "conceptual identity"
    assert mfc.meaning("dog", "cat", pos_a="N", pos_b="N", demand="similarity") == 0.11, "conceptual route"
    # (6d) magnitude-unavailable is HONEST: no magnitude_fn -> gradable pair falls back to conceptual, labelled.
    mfc2 = MeaningFusion(words, row_idx, phi, gfn, ref, (0.5, 0.5),
                         conceptual=_FakeConc(), router_fn=fake_router, magnitude_fn=None)
    assert mfc2.route_pair("big", "small", "A", "A", "similarity") == "magnitude_unavailable" \
        or mfc2.route_pair("big", "A", "small", "A", "similarity") == "magnitude_unavailable"
    assert mfc2.meaning("big", "small", pos_a="A", pos_b="A", demand="similarity") == 0.11, \
        "no magnitude channel -> gradable pair falls back to the conceptual op (recorded, not silent)"
    # (6e) similarity batch routes per item.
    sb = mfc.meaning_batch([("dog", "N", "dog", "N"), ("dog", "N", "cat", "N"), ("big", "A", "small", "A")],
                           demand="similarity")
    assert sb == [0.99, 0.11, 0.77], "meaning_batch(similarity) must route each item to its channel"
    ev["routing_logic_ok"] = True
    return ev


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2, default=str))
    print("ALL SELF-TESTS PASSED")
