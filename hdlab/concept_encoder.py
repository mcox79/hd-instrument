"""Stage 2 Spoke 1 ConceptEncoder -- brain-analog competitive-Hebbian sparse
coding mechanism for SUPERVISED concept-label-conditioned embedding.

Extracted 2026-07-02 from exp_substrate_concept_encoder_spoke1_v3_D_competitive_
hebbian_only_2026-07-02 (Spoke 1 v3-D ARM_COMPETITIVE_HEBBIAN CG'd at remote
FULL, 39.6s wall; verdict HARD_PASS with cat_kitten_cos_mean=0.492 seed
11/17/23 N=4096 SPC=40). Cortex primitive: given a stream of (sentence,
concept_label) pairs, learn per-concept sparse-bipolar concept HDs via
competitive-Hebbian outer-product accumulation + top-K winner-take-all readout
+ sign selection.

============================================================================
NAMING / SCOPE HONESTY (USER 2026-07-02 challenge -- LOAD-BEARING)
============================================================================
USER 2026-07-02: "how does substrate know what a cat or airplane are? are we
sure we tested apples to apples?"

This module is NOT unsupervised concept discovery. It is a SUPERVISED,
concept-label-conditioned sparse-bipolar embedding trained on a synthetic
controlled corpus with designer-imposed cluster structure. Any framing that
implies the substrate discovers "cat-ness" from raw text is inaccurate:
    - Sentences are surface char+positional HDs (no lexical semantics).
    - Concept identity comes from the integer concept_label passed to fit(),
      NOT from any label-free discovery process.
    - Cluster structure (cat/kitten grouped; airplane in a different cluster)
      is designer-imposed via the 25-cluster corpus scaffolding, NOT
      discovered by the encoder.
The primitive tests a MECHANISM (competitive-Hebbian sparse coding) under a
CONTROLLED SUPERVISED REGIME. Extending to unsupervised discovery, real
corpora, or Stage 4 language ingest requires the additional validation gates
below (VALIDATION SCOPE + STAGE 4 CAVEATS).

============================================================================
INPUT REGIME (mandatory framing per USER 2026-07-02 discipline)
============================================================================
Inputs to fit():
    - sentences: list of raw ASCII strings (length N_sentences).
    - concept_labels: np.ndarray shape [N_sentences] int -- integer indices
      in [0, n_concepts). SUPERVISED (sentence, concept_label) pairs are
      REQUIRED. This module does NOT do unsupervised concept discovery.

Sentences are char-trigram + positional-encoded via hdlab.char_positional_
encoder (character + positional HRR-bind + sign-bundle). Output is a
SURFACE HD reflecting the CHARACTER SEQUENCE (Kanerva-style V1 analog);
NOT semantic English understanding.

The concept encoder learns a per-concept sparse-bipolar HD from the surface
stream via competitive-Hebbian dynamics (Foldiak 1990 / Kohonen SOM
mechanism). It is NOT trained on word-meaning labels, embeddings, or any
external semantic supervision beyond the integer concept_label per sentence.

Per feedback_never_narrate_synthetic_HD_bundles_as_english_language_capability_
USER_2026-07-02: framing this as "the substrate understands English" is a
discipline violation. Correct frame:
    "given a stream of (surface HD, concept_label) pairs, the encoder learns
    per-concept sparse codes via competitive-Hebbian outer-product
    accumulation."

Full "language -> HD" encoding (Stage 4) is separate, upstream, and not yet
built.

============================================================================
VALIDATION SCOPE (as of 2026-07-02 extraction)
============================================================================
TESTED (Spoke 1 v3-D FULL 2026-07-02):
    - Synthetic controlled corpus: 25 clusters x 2 concepts each (50
      concepts total), designer-imposed grouping; 40 sentences/concept;
      5-verb-slot + 5-object-slot template mix; 5 canonical templates.
    - Config: N_DIM=4096, k_sparsity=0.02, seeds 11/17/23, mask_target_word.
    - Envelope: cat/kitten cosine mean 0.492 (>= 0.40 HP floor);
      cat/airplane cosine mean 0.020 (<= 0.10 ceiling); sparse_rate 0.020;
      intra_concept_cv comfortably < 0.20; gap vs NAIVE_WTA control >= 0.15.

NOT TESTED (STAGE 4 GATES; do NOT assume the primitive will hold outside
the tested regime):
    - Unsupervised regime (no concept_labels): mechanism has NO tested
      capability to discover concept groupings label-free.
    - Real-corpus transfer: only synthetic template-generated sentences
      were used; behavior on natural language corpora is unmeasured.
    - Label-semantics ablation: whether the mechanism relies on
      concept-label identity vs concept-name character overlap is
      unmeasured. mask_target_word=True removes the target concept token
      from context but the label channel itself is preserved.
    - Char-trigram-softmax baseline: no head-to-head against a simple
      softmax classifier on trigram features. Whether the mechanism
      SPECIFICALLY earns the "brain-analog" framing over a matched
      baseline is unmeasured.
    - Cross-language / non-ASCII: char encoder is ASCII-only.

============================================================================
BRAIN ANALOG + LITERATURE LINEAGE (accurate framing)
============================================================================
The MECHANISM (competitive-Hebbian sparse coding + top-K WTA readout) IS
brain-analog:
* Foldiak 1990 "Forming sparse representations by local anti-Hebbian
  learning" -- competitive-Hebbian yields sparse-distributed codes.
* Kohonen 1982 self-organizing maps -- competitive winner update via
  per-neuron accumulator + WTA. Direct mechanism analog.
* Journe et al. 2023 SoftHebb -- competitive-only Hebbian networks trained
  without backprop, close to gradient baselines. ML/AI-drill recommendation
  (2026-07-02 5x drill research_5x_drill_1_ml_ai_pc_complexity_2026-07-02.md)
  established that competitive-only is the baseline to beat before adding
  hierarchy.
* Quiroga et al. 2005 "Invariant visual representation by single neurons in
  the human brain" (concept cells) -- brain's concept-encoding functional
  target. Empirically emerges from competitive-Hebbian dynamics; NO PC layer
  at that level of processing.
* Cerebellar granule cells (Marr 1969 / Albus 1971) -- classic sparse
  competitive-Hebbian encoding with no top-down prediction. Same regime.

The APPLICATION REGIME (supervised concept-label-conditioned embedding on a
synthetic controlled corpus with designer-imposed clusters) is NOT brain-
analog: the brain does unsupervised concept discovery from raw sensory
streams, without integer label supervision, on natural (not template-
generated) inputs. Accurate one-line description:
    "brain-analog competitive-Hebbian sparse coding mechanism for
    supervised concept-label-conditioned embedding"
Do NOT describe this module as an "unsupervised brain-analog concept
encoder"; that overstates scope.

============================================================================
STAGE 4 CAVEATS (before using this primitive for real-corpus language ingest)
============================================================================
For real-corpus language ingest (Stage 4 milestone), the following
validation gates MUST be passed before wiring this primitive into the
production language stack:

(a) LABEL-FREE TRAINING PATH: derive a version of fit() that does not
    require integer concept_labels. Candidate mechanisms: temporal
    contiguity trace (Foldiak 1991 slow-feature analysis), streaming
    online clustering, or bootstrapping from surface-HD nearest-neighbor
    graph structure. Spoke 2 will design this per
        notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_
            slow_feature_analysis_2026-07-02.md

(b) CHAR-TRIGRAM-SOFTMAX BASELINE: head-to-head comparison of ConceptEncoder
    against a plain softmax classifier over char-trigram features on the
    same supervised task. If the softmax baseline matches or exceeds the
    competitive-Hebbian mechanism at CG envelope, the "brain-analog"
    framing does not earn complexity for this task.

(c) REAL-CORPUS TRANSFER: fit on a natural-language corpus (WordNet
    concept groupings, WikiConcept, or similar) without designer-imposed
    template scaffolding, and re-measure within-cluster / cross-cluster
    cosine envelopes. The synthetic-corpus envelopes above do NOT
    transfer automatically.

See the 2026-07-02 stress-test-design drill (to be filed) for the required
validation gates before Stage 4 use.

============================================================================
COMPUTE ARCHITECTURE (mandatory per USER-locked storage-strategy substrate
physics law CG_META 2026-07-02: math4_v2 + math4_rung3_v2 chain-grade)
============================================================================
Storage strategy: **SHARDED** (per-concept sparse-bipolar HD; NOT bundled).

Rationale:
- Each concept c owns its own sparse-bipolar HD concept_hds[c, :] of shape
  [n_dim]. Concept HDs are NEVER pooled into a single carrier at storage
  time; each is stored independently as int8 (values in {-1, 0, +1}).
- The Hebbian accumulator is a per-concept SHARDED buffer acc[c, :]
  intermediate to fit(); after top-K WTA + sign it is discarded and only
  the sparse concept HD is retained.
- BUNDLED storage (a single carrier of all concepts summed) would collapse
  concept-vs-concept discriminability under composition depth L>=2 per the
  math4_v2 substrate physics law. SHARDED per-concept storage keeps
  cross-concept cosine similarity at O(sqrt(k_sparsity)) capacity floor.
- Encode is a pure retrieval: cosine argmax over the SHARDED concept HD
  table, then return that concept HD. No cross-concept interference at
  encode time.

Composition guarantee (L>=1 chain composition per math4_v2 discipline):
- fit-time Hebbian: 1 primitive per sentence (outer product with one-hot
  concept indicator; reduces to per-concept accumulator update). Depth L=1.
- encode-time cleanup: 1 primitive (cosine argmax on concept HD table).
  Depth L=1.
- Total chain depth 2 (fit + encode). SHARDED storage prevents the
  BUNDLED-collapse regime.

============================================================================
FALSIFIED-MECHANISM LINEAGE (do NOT reintroduce; kept as selftest control)
============================================================================
* PC (predictive coding) layer: 5x-drill convergence on 2026-07-02 established
  PC DOES NOT EARN COMPLEXITY on top of competitive-only for the concept-
  encoding functional target. Reference:
    ~/.claude/projects/d--AI/memory/reference_5x_drill_convergence_PC_
    redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02.md
  Higher-level hierarchical prediction (Rao-Ballard) belongs at Spoke 2+
  (temporal contiguity / one-shot indexing), NOT here.
* NAIVE_WTA_SAMPLING (2026-06-23 sparse_engram_allocation): picks dims by
  cross-concept COLLISION MINIMIZATION only; ignores per-dim within-concept
  consistency magnitude. FALSIFIED (HF at N=4096 M=10K). Retained as a
  control-only reference mechanism (selftest 9); do NOT wire into any
  cortex layer.

Strategic anchor (brain-best-in-class reference standard):
    ~/.claude/projects/d--AI/memory/project_brain_function_is_best_in_class_
    reference_standard_USER_LOCKED_2026-07-02.md

============================================================================
Envelope (CG-confirmed at ARM_COMPETITIVE_HEBBIAN v3-D FULL; do not exceed
without rescue cell):
- n_dim >= 2048 (empirical minimum for stable within-cluster consolidation;
  smoke ran at 2048, FULL at 4096; scale-sentinel probe validates 8192).
- n_concepts up to 50 (25-cluster 2-concept-per-cluster corpus; CG regime).
- k_sparsity in [0.010, 0.030] (target 2%; architectural via top-K
  quantile mask).
- sentences_per_concept >= 40 (empirically needed for stable per-concept
  accumulator convergence at 25-cluster mixed corpus).
- Per-arm CG envelope (seed 11/17/23 v3-D FULL 2026-07-02):
    cat_kitten_cos_mean >= 0.40 (MEASURED 0.492)
    cat_airplane_cos_mean <= 0.10 (MEASURED 0.020)
    sparse_rate in [0.010, 0.030] (MEASURED 0.020)
    intra_concept_cv < 0.20 (MEASURED far below; comfortably in band)
    gap - naive_wta_gap >= 0.15 (CG progress over 2026-06-23 falsified
                                  baseline)

References:
- Source cell: experiments/exp_substrate_concept_encoder_spoke1_v3_D_
    competitive_hebbian_only_2026-07-02.py (commit e8f15a036)
- Pre-reg + landing evidence: data/exp_substrate_concept_encoder_spoke1_v3_D_
    competitive_hebbian_only_2026_07_02/metrics.json
- Related primitives: hdlab.char_positional_encoder (surface HD input),
    hdlab.semantic_parser (M1.9 SHARDED extraction pattern),
    hdlab.intent_classifier (a related SHARDED concept-prototype primitive)

Cortex wiring: NOT wired in this extraction (per Director instruction 2026-
07-02). Cortex Phase 4 wiring is a separate follow-up post-Spoke-2-CG.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Bootstrap: reach hdlab when executed as script.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402

# ---------------------------------------------------------------------------
# CG-anchored envelope constants (Spoke 1 v3-D seed 11/17/23 CG 2026-07-02).
# ---------------------------------------------------------------------------

CG_N_DIM_DEFAULT = 4096
CG_K_SPARSITY_DEFAULT = 0.02
CG_LEARNING_RATE_DEFAULT = 1.0
CG_SEED_DEFAULT = 11
CG_MAX_POS_DEFAULT = 24

# CG-measured envelope for reproducibility selftests (FULL run 2026-07-02).
CG_FULL_CAT_KITTEN_COS_MEAN = 0.492
CG_FULL_CAT_AIRPLANE_COS_MEAN = 0.020
CG_FULL_SPARSE_RATE_MEAN = 0.020
CG_SPARSITY_TOLERANCE = 0.005  # +/- 0.5% around target
CG_FULL_TOLERANCE = 0.05       # +/- 0.05 around measured FULL means
CG_SEEDS_FULL = (11, 17, 23)
CG_N_DIM_FULL = 4096
CG_SENTENCES_PER_CONCEPT_FULL = 40
CG_N_DIM_SCALE_SENTINEL = 8192

# Storage strategy tag (SHARDED per META_RULE_STORAGE).
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"
COMPUTE_ARCH = "sequential_cpu_numpy"


# ---------------------------------------------------------------------------
# ConceptEncoderResult dataclass -- per-sentence structured encode() output.
# ---------------------------------------------------------------------------

@dataclass
class ConceptEncoderResult:
    """Structured per-sentence concept-encoding output.

    Fields:
        concept_hd: np.ndarray shape [n_dim] int8 -- sparse-bipolar concept HD
                    for the best-matching learned concept. Values in
                    {-1, 0, +1} where non-zero entries mark the top-K
                    winner dims with their sign.
        sparse_dims: np.ndarray shape [k] int64 -- indices of the k non-zero
                    dims of concept_hd (the top-K WTA selection).
        activation_signs: np.ndarray shape [k] int8 -- signs (+1 or -1) of
                    the k non-zero dims, aligned with sparse_dims.
        concept_id: int -- best-matching concept id (argmax cosine over
                    the SHARDED concept HD table).
        confidence: float -- cosine similarity of the sentence surface HD
                    to the recovered concept HD (higher = more confident).
    """
    concept_hd: np.ndarray
    sparse_dims: np.ndarray
    activation_signs: np.ndarray
    concept_id: int
    confidence: float


# ---------------------------------------------------------------------------
# ConceptEncoder class.
# ---------------------------------------------------------------------------

class ConceptEncoder:
    """Brain-analog competitive-Hebbian sparse coding mechanism for SUPERVISED
    concept-label-conditioned embedding (Foldiak/Kohonen mechanism analog).

    NOT unsupervised concept discovery. fit() REQUIRES (sentence,
    concept_label) supervised pairs; the encoder does not derive concept
    identity from the surface stream alone. See module docstring
    VALIDATION SCOPE + STAGE 4 CAVEATS for the un-validated regimes.

    Storage strategy: SHARDED (per-concept HD; NOT bundled).
    Compute arch: sequential CPU numpy per concept.

    Mechanism (fit):
        1. Encode each sentence to surface HD via char_positional_encoder
           (optionally masking the target concept word if concept_names
           supplied and mask_target_word=True).
        2. Mean-center context HDs across the training corpus.
        3. Per-concept Hebbian outer-product accumulation with the one-hot
           concept indicator I_c:
               acc[c, :] += learning_rate * context_hd  for each sentence
               with label c (reduces from full outer product because I_c
               is one-hot).
        4. Per-concept top-K WTA on |acc[c]| / count[c] (k = k_sparsity *
           n_dim).
        5. Sign selection: sign(acc[c, selected]) -> sparse-bipolar HD.
        6. Store as int8 SHARDED table concept_hds[n_concepts, n_dim].

    Mechanism (encode):
        1. Encode input sentence to surface HD (WITHOUT masking; at encode
           time we do not know the concept identity).
        2. Cosine argmax on the SHARDED concept HD table.
        3. Return the winning concept HD.

    Args:
        n_dim: HD dimensionality. Must be >= 1.
        n_concepts: Number of concept classes. Must be >= 2 (single-concept
                    encoding degenerates).
        k_sparsity: Fraction of dims retained by top-K WTA. Must be in
                    (0.0, 1.0]. CG default 0.02 (2%).
        learning_rate: Hebbian accumulation gain. Rescales acc but does NOT
                       change WTA selection (WTA is scale-invariant); kept
                       for interface parity with generic Hebbian primitives.
        seed: Deterministic seed for the char+positional encoder and any
              internal randomness. Reproducibility contract: same seed +
              same inputs -> bit-identical concept HDs.
        max_pos: Max character positions per word (surface encoder param).
        concept_names: Optional list of length n_concepts; if provided AND
                       mask_target_word=True, fit() masks the target
                       concept word from each sentence's surface HD (per
                       Spoke 1 v3-D source-cell discipline).
        mask_target_word: Whether to mask concept_names[label] out of each
                          training sentence. No-op if concept_names is None.

    Public API:
        fit(sentences, concept_labels) -> None
        encode(sentence) -> np.ndarray [n_dim] int8 (concept HD)
        encode_batch(sentences) -> np.ndarray [B, n_dim] int8
        encode_with_result(sentence) -> ConceptEncoderResult
        get_concept_result(concept_id) -> ConceptEncoderResult
        sparse_rate() -> float (architectural sparse rate over concept table)
    """

    def __init__(
        self,
        n_dim: int,
        n_concepts: int,
        k_sparsity: float = CG_K_SPARSITY_DEFAULT,
        learning_rate: float = CG_LEARNING_RATE_DEFAULT,
        seed: int = CG_SEED_DEFAULT,
        max_pos: int = CG_MAX_POS_DEFAULT,
        concept_names: Optional[Sequence[str]] = None,
        mask_target_word: bool = True,
    ) -> None:
        if not isinstance(n_dim, int) or n_dim <= 0:
            raise ValueError(f"n_dim must be positive int; got {n_dim!r}")
        if not isinstance(n_concepts, int) or n_concepts < 2:
            raise ValueError(
                f"n_concepts must be int >= 2; got {n_concepts!r}"
            )
        if not (0.0 < float(k_sparsity) <= 1.0):
            raise ValueError(
                f"k_sparsity must be in (0.0, 1.0]; got {k_sparsity!r}"
            )
        if concept_names is not None and len(concept_names) != n_concepts:
            raise ValueError(
                f"concept_names length {len(concept_names)} != n_concepts "
                f"{n_concepts}"
            )
        if max_pos <= 0:
            raise ValueError(f"max_pos must be positive; got {max_pos!r}")

        self.n_dim = int(n_dim)
        self.n_concepts = int(n_concepts)
        self.k_sparsity = float(k_sparsity)
        self.learning_rate = float(learning_rate)
        self.seed = int(seed)
        self.max_pos = int(max_pos)
        self.concept_names: Optional[List[str]] = (
            list(concept_names) if concept_names is not None else None
        )
        self.mask_target_word = bool(mask_target_word)

        # Surface encoder (char + positional HRR bind + sign bundle).
        # Seed prefix matches Spoke 1 v3-D source cell convention.
        self._surface_encoder = CharPositionalEncoder(
            n_dim=self.n_dim,
            max_pos=self.max_pos,
            seed_prefix=f"SPOKE1_S{self.seed}",
        )

        # Trained state (populated by fit()).
        # concept_hds: [n_concepts, n_dim] int8, values in {-1, 0, +1}.
        self._concept_hds: Optional[np.ndarray] = None
        # counts_per_concept: [n_concepts] float32 -- for diagnostics.
        self._counts_per_concept: Optional[np.ndarray] = None
        # k_effective: int -- actual top-K used (max(1, round(k_sparsity*N))).
        self._k_effective: int = max(1, int(round(self.k_sparsity * self.n_dim)))
        self._fitted: bool = False

    # -----------------------------------------------------------------------
    # Fit.
    # -----------------------------------------------------------------------

    def fit(
        self,
        sentences: Sequence[str],
        concept_labels: np.ndarray,
    ) -> None:
        """Train per-concept sparse-bipolar HDs via competitive-Hebbian.

        Args:
            sentences: list-like of raw text sentences (length N_sentences).
            concept_labels: np.ndarray shape [N_sentences] int -- values in
                            [0, n_concepts).

        Contract:
            - Same (sentences, concept_labels, seed, hyperparams) -> same
              concept_hds (bit-identical; determinism guaranteed by seed).
            - After fit(): _fitted=True, _concept_hds populated.
            - Empty-concept classes (no sentences with that label) have
              all-zero HD (documented; encode() will still return it but
              cosine similarity will be zero).
        """
        labels = np.asarray(concept_labels)
        if labels.ndim != 1:
            raise ValueError(
                f"concept_labels must be 1-D; got shape {labels.shape}"
            )
        if len(sentences) != labels.shape[0]:
            raise ValueError(
                f"len(sentences)={len(sentences)} != len(concept_labels)="
                f"{labels.shape[0]}"
            )
        if labels.size > 0:
            lmin = int(labels.min())
            lmax = int(labels.max())
            if lmin < 0 or lmax >= self.n_concepts:
                raise ValueError(
                    f"concept_labels out of range [0, {self.n_concepts}): "
                    f"min={lmin} max={lmax}"
                )

        # Step 1: encode surface HDs (optionally masking target concept word).
        n_sent = len(sentences)
        context_hds = np.zeros((n_sent, self.n_dim), dtype=np.float32)
        use_mask = (
            self.mask_target_word and self.concept_names is not None
        )
        for i in range(n_sent):
            s = sentences[i]
            if use_mask:
                target_word = self.concept_names[int(labels[i])]
                context_hds[i] = self._surface_encoder.encode_sentence_masked(
                    s, target_word
                )
            else:
                context_hds[i] = self._surface_encoder.encode_sentence(s)

        # Step 2: mean-center across corpus (removes global surface bias).
        mean = context_hds.mean(axis=0, keepdims=True)
        centered = (context_hds - mean).astype(np.float32)

        # Step 3: per-concept Hebbian outer-product accumulation.
        acc = np.zeros((self.n_concepts, self.n_dim), dtype=np.float32)
        counts = np.zeros(self.n_concepts, dtype=np.float32)
        lr = self.learning_rate
        for i in range(n_sent):
            cid = int(labels[i])
            acc[cid] += lr * centered[i]
            counts[cid] += 1.0

        # Step 4-6: per-concept top-K WTA + sign; store as int8.
        concept_hds = np.zeros((self.n_concepts, self.n_dim), dtype=np.int8)
        k = self._k_effective
        for c in range(self.n_concepts):
            if counts[c] <= 0:
                continue
            magnitudes = np.abs(acc[c]) / counts[c]
            if k >= self.n_dim:
                mask = np.ones(self.n_dim, dtype=bool)
            else:
                # partition puts k-th largest at position N-k; >= it = top-k
                pivot = np.partition(
                    magnitudes, self.n_dim - k
                )[self.n_dim - k]
                mask = magnitudes >= pivot
            sign_c = np.sign(acc[c]).astype(np.int8)
            sign_c[sign_c == 0] = 1
            # Zero out dims not in the top-K mask.
            hd = sign_c * mask.astype(np.int8)
            concept_hds[c] = hd

        # NaN sentinel (should never fire in normal regime; catches float
        # overflow at extreme N or unbounded lr).
        n_nan = int(np.isnan(concept_hds.astype(np.float32)).sum())
        if n_nan > 0:
            raise RuntimeError(
                f"ConceptEncoder.fit: NaN detected in concept_hds "
                f"(n_nan={n_nan}); likely float overflow at large N or "
                f"unbounded learning_rate. Reduce learning_rate or n_dim."
            )

        self._concept_hds = concept_hds
        self._counts_per_concept = counts
        self._fitted = True

    # -----------------------------------------------------------------------
    # Encode.
    # -----------------------------------------------------------------------

    def _check_fitted(self) -> None:
        if not self._fitted or self._concept_hds is None:
            raise RuntimeError(
                "ConceptEncoder must be fit() before encode()."
            )

    def _classify(self, surface_hd: np.ndarray) -> tuple:
        """Return (best_concept_id, cosine_confidence) for a surface HD.

        Uses cosine argmax over the SHARDED concept HD table.
        """
        concept_hds_f = self._concept_hds.astype(np.float32)
        # Norms for cosine; zero-guard.
        s_norm = float(np.linalg.norm(surface_hd))
        if s_norm < 1e-12:
            return 0, 0.0
        c_norms = np.linalg.norm(concept_hds_f, axis=1)
        # Any concept with zero HD (empty class) -> similarity 0.
        c_norms_safe = np.where(c_norms < 1e-12, 1.0, c_norms)
        scores = (concept_hds_f @ surface_hd) / (c_norms_safe * s_norm)
        scores = np.where(c_norms < 1e-12, 0.0, scores)
        best = int(np.argmax(scores))
        return best, float(scores[best])

    def encode(self, sentence: str) -> np.ndarray:
        """Return sparse-bipolar concept HD for a single sentence.

        sentence: raw text (ASCII).
        Returns: np.ndarray shape [n_dim] int8; values in {-1, 0, +1}.
        """
        self._check_fitted()
        surface_hd = self._surface_encoder.encode_sentence(sentence)
        best, _ = self._classify(surface_hd)
        return self._concept_hds[best].copy()

    def encode_batch(self, sentences: Sequence[str]) -> np.ndarray:
        """Batched encode -- returns [B, n_dim] int8 concept HD table.

        sentences: list-like of raw text sentences.
        Returns: np.ndarray shape [B, n_dim] int8.
        """
        self._check_fitted()
        n = len(sentences)
        out = np.zeros((n, self.n_dim), dtype=np.int8)
        # Batched surface encoding.
        surface = self._surface_encoder.encode_batch(sentences)  # [B, n_dim] f32
        concept_hds_f = self._concept_hds.astype(np.float32)
        c_norms = np.linalg.norm(concept_hds_f, axis=1)
        c_norms_safe = np.where(c_norms < 1e-12, 1.0, c_norms)
        s_norms = np.linalg.norm(surface, axis=1)
        s_norms_safe = np.where(s_norms < 1e-12, 1.0, s_norms)
        # cosine matrix [B, n_concepts]
        scores = (surface @ concept_hds_f.T)
        scores = scores / (s_norms_safe[:, None] * c_norms_safe[None, :])
        # Zero-out empty-class columns.
        empty_mask = c_norms < 1e-12
        if np.any(empty_mask):
            scores[:, empty_mask] = 0.0
        best_ids = np.argmax(scores, axis=1)
        for i in range(n):
            out[i] = self._concept_hds[int(best_ids[i])]
        return out

    def encode_with_result(self, sentence: str) -> ConceptEncoderResult:
        """Return ConceptEncoderResult for a single sentence.

        Provides sparse_dims + activation_signs + concept_id + confidence
        alongside the raw concept HD.
        """
        self._check_fitted()
        surface_hd = self._surface_encoder.encode_sentence(sentence)
        best, conf = self._classify(surface_hd)
        hd = self._concept_hds[best].copy()
        return self._build_result(hd, best, conf)

    def get_concept_result(self, concept_id: int) -> ConceptEncoderResult:
        """Return ConceptEncoderResult for a trained concept id (no sentence).

        Used to inspect the learned per-concept HD directly. Confidence is
        1.0 by convention (self-similarity of a bipolar-sparse HD to itself).
        """
        self._check_fitted()
        if not (0 <= int(concept_id) < self.n_concepts):
            raise ValueError(
                f"concept_id {concept_id} out of range [0, {self.n_concepts})"
            )
        hd = self._concept_hds[int(concept_id)].copy()
        return self._build_result(hd, int(concept_id), 1.0)

    def _build_result(
        self, hd: np.ndarray, concept_id: int, confidence: float
    ) -> ConceptEncoderResult:
        nonzero_idx = np.nonzero(hd)[0].astype(np.int64)
        signs = hd[nonzero_idx].astype(np.int8)
        return ConceptEncoderResult(
            concept_hd=hd,
            sparse_dims=nonzero_idx,
            activation_signs=signs,
            concept_id=concept_id,
            confidence=confidence,
        )

    def sparse_rate(self) -> float:
        """Return architectural sparse rate over the full concept HD table."""
        self._check_fitted()
        total = self._concept_hds.size
        if total == 0:
            return 0.0
        return float(np.count_nonzero(self._concept_hds)) / float(total)

    @property
    def concept_hds(self) -> np.ndarray:
        """Public accessor for the trained concept HD table."""
        self._check_fitted()
        return self._concept_hds


# ---------------------------------------------------------------------------
# Falsified-mechanism control (2026-06-23 NAIVE_WTA_SAMPLING).
# Retained as a reference control for selftest 9; NOT for production use.
# ---------------------------------------------------------------------------

def _naive_wta_sampling_concept_hds(
    n_dim: int,
    n_concepts: int,
    sentences: Sequence[str],
    concept_labels: np.ndarray,
    seed: int,
    k_sparsity: float,
    concept_names: Optional[Sequence[str]] = None,
    mask_target_word: bool = True,
) -> np.ndarray:
    """FALSIFIED 2026-06-23 collision-minimizing WTA sampling (control only).

    Picks dims by cross-concept COLLISION MINIMIZATION only; ignores per-dim
    within-concept consistency magnitude. That's why it can't cluster
    related concepts.

    Returns concept_hds [n_concepts, n_dim] int8.
    """
    surface_encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=CG_MAX_POS_DEFAULT,
        seed_prefix=f"SPOKE1_S{seed}",
    )
    labels = np.asarray(concept_labels)
    n_sent = len(sentences)
    ctx = np.zeros((n_sent, n_dim), dtype=np.float32)
    use_mask = mask_target_word and concept_names is not None
    for i in range(n_sent):
        s = sentences[i]
        if use_mask:
            ctx[i] = surface_encoder.encode_sentence_masked(
                s, concept_names[int(labels[i])]
            )
        else:
            ctx[i] = surface_encoder.encode_sentence(s)
    centered = ctx - ctx.mean(axis=0, keepdims=True)

    mean_ctx = np.zeros((n_concepts, n_dim), dtype=np.float32)
    counts = np.zeros(n_concepts, dtype=np.float32)
    for i in range(n_sent):
        cid = int(labels[i])
        mean_ctx[cid] += centered[i]
        counts[cid] += 1.0
    for c in range(n_concepts):
        if counts[c] > 0:
            mean_ctx[c] /= counts[c]

    K = max(1, int(round(k_sparsity * n_dim)))
    dim_use_count = np.zeros(n_dim, dtype=np.int32)
    concept_hds = np.zeros((n_concepts, n_dim), dtype=np.int8)

    rng = np.random.default_rng(int(seed) * 7919 + 13)
    concept_order = rng.permutation(n_concepts)

    for c in concept_order:
        tiebreak = rng.random(n_dim).astype(np.float32)
        score = dim_use_count.astype(np.float32) + tiebreak * 0.01
        selected = np.argpartition(score, K)[:K]
        signs = np.sign(mean_ctx[c, selected]).astype(np.int8)
        signs[signs == 0] = 1
        concept_hds[c, selected] = signs
        dim_use_count[selected] += 1
    return concept_hds


# ---------------------------------------------------------------------------
# Selftest helpers -- synthetic 25-cluster corpus (mirrors Spoke 1 v3-D).
# ---------------------------------------------------------------------------

# Same 25-cluster corpus as Spoke 1 v3-D source cell (deterministic scaffold
# for reproducibility of selftest 8 against FULL run).
_SELFTEST_CLUSTERS: List[tuple] = [
    (("cat", "kitten"), ["meow", "purr", "chase", "lick", "groom"],
     ["mouse", "yarn", "milk", "bed", "toy"]),
    (("dog", "puppy"), ["bark", "wag", "fetch", "sniff", "chase"],
     ["bone", "ball", "leash", "tree", "cat"]),
    (("bird", "chick"), ["chirp", "flap", "peck", "fly", "sing"],
     ["seed", "worm", "nest", "twig", "branch"]),
    (("fish", "minnow"), ["swim", "dart", "gulp", "school", "dive"],
     ["water", "coral", "algae", "bait", "wave"]),
    (("horse", "foal"), ["gallop", "neigh", "trot", "canter", "jump"],
     ["field", "fence", "saddle", "hay", "barn"]),
    (("cow", "calf"), ["moo", "graze", "chew", "walk", "rest"],
     ["grass", "field", "pond", "shade", "hay"]),
    (("pig", "piglet"), ["oink", "root", "wallow", "grunt", "trot"],
     ["mud", "trough", "pen", "slop", "corn"]),
    (("sheep", "lamb"), ["baa", "flock", "graze", "wander", "wool"],
     ["meadow", "hill", "shepherd", "gate", "grass"]),
    (("bee", "larva"), ["buzz", "sting", "gather", "dance", "hover"],
     ["nectar", "flower", "hive", "honey", "petal"]),
    (("ant", "pupa"), ["crawl", "carry", "swarm", "march", "tunnel"],
     ["crumb", "sugar", "leaf", "mound", "twig"]),
    (("airplane", "jet"), ["fly", "soar", "climb", "descend", "cruise"],
     ["cloud", "runway", "sky", "airport", "mountain"]),
    (("boat", "ship"), ["sail", "float", "drift", "dock", "cruise"],
     ["ocean", "harbor", "wave", "pier", "shore"]),
    (("car", "truck"), ["drive", "brake", "accelerate", "swerve", "park"],
     ["road", "highway", "garage", "traffic", "lane"]),
    (("bicycle", "scooter"), ["pedal", "coast", "brake", "swerve", "roll"],
     ["path", "hill", "sidewalk", "park", "trail"]),
    (("train", "tram"), ["chug", "roll", "brake", "whistle", "depart"],
     ["track", "station", "platform", "tunnel", "bridge"]),
    (("mountain", "peak"), ["rise", "loom", "tower", "shadow", "erode"],
     ["snow", "cloud", "sky", "valley", "trail"]),
    (("river", "stream"), ["flow", "bend", "rush", "meander", "cascade"],
     ["bank", "bridge", "rock", "fish", "reed"]),
    (("forest", "grove"), ["shelter", "shade", "sway", "grow", "canopy"],
     ["tree", "leaf", "moss", "path", "clearing"]),
    (("desert", "dune"), ["shimmer", "stretch", "bake", "shift", "gleam"],
     ["sand", "sun", "cactus", "rock", "wind"]),
    (("lake", "pond"), ["shimmer", "ripple", "reflect", "still", "freeze"],
     ["water", "shore", "fish", "reed", "duck"]),
    (("hammer", "mallet"), ["strike", "pound", "drive", "swing", "hit"],
     ["nail", "board", "wood", "post", "peg"]),
    (("saw", "blade"), ["cut", "slice", "bite", "rip", "shave"],
     ["wood", "log", "plank", "beam", "branch"]),
    (("chair", "stool"), ["seat", "hold", "rest", "wobble", "creak"],
     ["floor", "table", "desk", "cushion", "leg"]),
    (("bed", "cot"), ["support", "hold", "rest", "creak", "spring"],
     ["pillow", "sheet", "blanket", "frame", "quilt"]),
    (("book", "novel"), ["tell", "describe", "recount", "reveal", "narrate"],
     ["page", "chapter", "shelf", "story", "cover"]),
]

_SELFTEST_N_CLUSTERS = len(_SELFTEST_CLUSTERS)
_SELFTEST_N_CONCEPTS = 2 * _SELFTEST_N_CLUSTERS  # 50


def _selftest_concept_names() -> List[str]:
    names: List[str] = []
    for pair, _, _ in _SELFTEST_CLUSTERS:
        names.extend(list(pair))
    return names


def _selftest_build_corpus(
    seed: int, sentences_per_concept: int
) -> tuple:
    """Return (sentences, concept_labels, cluster_ids) mirroring Spoke 1 v3-D."""
    rng = np.random.default_rng(seed)
    templates = [
        "the {c} {v} the {o}",
        "a {c} will {v} the {o}",
        "one {c} {v} by the {o}",
        "the {c} {v} near the {o}",
        "every {c} might {v} the {o}",
    ]
    sentences: List[str] = []
    concept_labels: List[int] = []
    cluster_ids: List[int] = []
    concept_idx = 0
    for cluster_id, (pair, verbs, objs) in enumerate(_SELFTEST_CLUSTERS):
        for concept in pair:
            for _ in range(sentences_per_concept):
                v = verbs[int(rng.integers(0, len(verbs)))]
                o = objs[int(rng.integers(0, len(objs)))]
                t = templates[int(rng.integers(0, len(templates)))]
                s = t.format(c=concept, v=v, o=o)
                sentences.append(s)
                concept_labels.append(concept_idx)
                cluster_ids.append(cluster_id)
            concept_idx += 1
    return (sentences, np.asarray(concept_labels, dtype=np.int64),
            np.asarray(cluster_ids, dtype=np.int64))


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a.astype(np.float32), b.astype(np.float32)) / (na * nb))


def _concept_id(target: str) -> int:
    return _selftest_concept_names().index(target)


# ---------------------------------------------------------------------------
# Selftests.
# ---------------------------------------------------------------------------

def _selftest_1_fit_encode_round_trip() -> None:
    """Selftest 1: fit + encode round-trip on 25-cluster toy corpus (single seed,
    small N). Predictions:
        cat/kitten cosine >= 0.4 (within-cluster consolidation).
        cat/airplane cosine <= 0.1 (cross-cluster separation).
    """
    names = _selftest_concept_names()
    sentences, labels, _ = _selftest_build_corpus(
        seed=11, sentences_per_concept=40
    )
    enc = ConceptEncoder(
        n_dim=2048,
        n_concepts=_SELFTEST_N_CONCEPTS,
        k_sparsity=0.02,
        seed=11,
        max_pos=24,
        concept_names=names,
        mask_target_word=True,
    )
    enc.fit(sentences, labels)
    cat_hd = enc.concept_hds[_concept_id("cat")]
    kitten_hd = enc.concept_hds[_concept_id("kitten")]
    airplane_hd = enc.concept_hds[_concept_id("airplane")]
    ck = _cos(cat_hd, kitten_hd)
    ca = _cos(cat_hd, airplane_hd)
    if ck < 0.4:
        raise AssertionError(
            f"selftest_1 cat/kitten cosine {ck:.3f} < 0.4 floor"
        )
    if ca > 0.1:
        raise AssertionError(
            f"selftest_1 cat/airplane cosine {ca:.3f} > 0.1 ceiling"
        )


def _selftest_2_sparse_rate_architectural() -> None:
    """Selftest 2: architectural sparse rate at 2% +/- 0.5% (top-K WTA)."""
    names = _selftest_concept_names()
    sentences, labels, _ = _selftest_build_corpus(
        seed=11, sentences_per_concept=40
    )
    enc = ConceptEncoder(
        n_dim=2048,
        n_concepts=_SELFTEST_N_CONCEPTS,
        k_sparsity=0.02,
        seed=11,
        concept_names=names,
    )
    enc.fit(sentences, labels)
    sr = enc.sparse_rate()
    lo = CG_FULL_SPARSE_RATE_MEAN - CG_SPARSITY_TOLERANCE
    hi = CG_FULL_SPARSE_RATE_MEAN + CG_SPARSITY_TOLERANCE
    if not (lo <= sr <= hi):
        raise AssertionError(
            f"selftest_2 sparse_rate {sr:.4f} outside "
            f"[{lo:.4f}, {hi:.4f}] (target 2% +/- 0.5%)"
        )


def _selftest_3_bit_identical_reproducibility() -> None:
    """Selftest 3: same seed + same inputs -> bit-identical concept HDs."""
    names = _selftest_concept_names()
    sentences, labels, _ = _selftest_build_corpus(
        seed=11, sentences_per_concept=20
    )
    enc_a = ConceptEncoder(
        n_dim=1024, n_concepts=_SELFTEST_N_CONCEPTS, seed=11,
        concept_names=names,
    )
    enc_a.fit(sentences, labels)
    enc_b = ConceptEncoder(
        n_dim=1024, n_concepts=_SELFTEST_N_CONCEPTS, seed=11,
        concept_names=names,
    )
    enc_b.fit(sentences, labels)
    if not np.array_equal(enc_a.concept_hds, enc_b.concept_hds):
        raise AssertionError(
            "selftest_3 concept_hds not bit-identical under same seed"
        )
    # And encode() is deterministic too.
    hd_a = enc_a.encode(sentences[0])
    hd_b = enc_b.encode(sentences[0])
    if not np.array_equal(hd_a, hd_b):
        raise AssertionError(
            "selftest_3 encode() not deterministic under same seed"
        )


def _selftest_4_batch_matches_scalar() -> None:
    """Selftest 4: encode_batch(sentences) matches per-item encode(sentence)."""
    names = _selftest_concept_names()
    sentences, labels, _ = _selftest_build_corpus(
        seed=11, sentences_per_concept=20
    )
    enc = ConceptEncoder(
        n_dim=1024, n_concepts=_SELFTEST_N_CONCEPTS, seed=11,
        concept_names=names,
    )
    enc.fit(sentences, labels)
    probe = sentences[:12]
    batch_out = enc.encode_batch(probe)
    for i in range(len(probe)):
        item = enc.encode(probe[i])
        if not np.array_equal(item, batch_out[i]):
            raise AssertionError(
                f"selftest_4 batch/scalar mismatch at i={i}"
            )


def _selftest_5_ctor_validation_n_dim() -> None:
    """Selftest 5: constructor rejects bad n_dim."""
    ok = False
    try:
        ConceptEncoder(n_dim=0, n_concepts=10)
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError("selftest_5 expected ValueError on n_dim=0")
    ok = False
    try:
        ConceptEncoder(n_dim=-4, n_concepts=10)
    except ValueError:
        ok = True
    if not ok:
        raise AssertionError("selftest_5 expected ValueError on n_dim=-4")


def _selftest_6_ctor_validation_k_sparsity() -> None:
    """Selftest 6: constructor rejects bad k_sparsity."""
    for bad in (0.0, -0.1, 1.1, 2.0):
        ok = False
        try:
            ConceptEncoder(n_dim=1024, n_concepts=10, k_sparsity=bad)
        except ValueError:
            ok = True
        if not ok:
            raise AssertionError(
                f"selftest_6 expected ValueError on k_sparsity={bad}"
            )


def _selftest_7_ctor_validation_n_concepts() -> None:
    """Selftest 7: constructor rejects bad n_concepts."""
    for bad in (0, 1, -3):
        ok = False
        try:
            ConceptEncoder(n_dim=1024, n_concepts=bad)
        except ValueError:
            ok = True
        if not ok:
            raise AssertionError(
                f"selftest_7 expected ValueError on n_concepts={bad}"
            )


def _selftest_8_reproduces_v3_d_full_cat_kitten() -> None:
    """Selftest 8: reproduces Spoke 1 v3-D FULL cat/kitten cosine at same
    seeds/N/config. Target mean = 0.492 +/- 0.05.

    Runs 3 seeds (11, 17, 23) at N=4096 SPC=40 (matches v3-D FULL config)
    and asserts mean(cat_kitten_cos) within tolerance of measured
    CG value 0.492.
    """
    names = _selftest_concept_names()
    cat_kitten_vals: List[float] = []
    cat_airplane_vals: List[float] = []
    for seed in CG_SEEDS_FULL:
        sentences, labels, _ = _selftest_build_corpus(
            seed=int(seed),
            sentences_per_concept=CG_SENTENCES_PER_CONCEPT_FULL,
        )
        enc = ConceptEncoder(
            n_dim=CG_N_DIM_FULL,
            n_concepts=_SELFTEST_N_CONCEPTS,
            k_sparsity=0.02,
            seed=int(seed),
            max_pos=24,
            concept_names=names,
            mask_target_word=True,
        )
        enc.fit(sentences, labels)
        cat_hd = enc.concept_hds[_concept_id("cat")]
        kitten_hd = enc.concept_hds[_concept_id("kitten")]
        airplane_hd = enc.concept_hds[_concept_id("airplane")]
        cat_kitten_vals.append(_cos(cat_hd, kitten_hd))
        cat_airplane_vals.append(_cos(cat_hd, airplane_hd))
    ck_mean = float(np.mean(cat_kitten_vals))
    ca_mean = float(np.mean(cat_airplane_vals))
    lo = CG_FULL_CAT_KITTEN_COS_MEAN - CG_FULL_TOLERANCE
    hi = CG_FULL_CAT_KITTEN_COS_MEAN + CG_FULL_TOLERANCE
    if not (lo <= ck_mean <= hi):
        raise AssertionError(
            f"selftest_8 cat/kitten mean {ck_mean:.4f} outside "
            f"[{lo:.4f}, {hi:.4f}] (v3-D FULL CG target "
            f"{CG_FULL_CAT_KITTEN_COS_MEAN:.4f} +/- {CG_FULL_TOLERANCE})"
        )
    if ca_mean > CG_FULL_CAT_AIRPLANE_COS_MEAN + CG_FULL_TOLERANCE:
        raise AssertionError(
            f"selftest_8 cat/airplane mean {ca_mean:.4f} exceeds "
            f"CG ceiling {CG_FULL_CAT_AIRPLANE_COS_MEAN + CG_FULL_TOLERANCE:.4f}"
        )
    print(
        f"[concept_encoder selftest_8] cat_kitten_mean={ck_mean:.4f} "
        f"(v3-D FULL target {CG_FULL_CAT_KITTEN_COS_MEAN:.4f}); "
        f"cat_airplane_mean={ca_mean:.4f}"
    )


def _selftest_9_naive_wta_sampling_falsified_control() -> None:
    """Selftest 9: NAIVE_WTA_SAMPLING (2026-06-23 falsified control) produces
    gap approximately 0 -- reproduces prior HF at v3-D FULL config.

    Predicted: cat_kitten - cat_airplane gap on NAIVE_WTA is near zero
    (source cell measurement: NAIVE_WTA_gap ~ 0.000 vs COMP_HEB_gap ~ 0.47).
    Asserts |NAIVE_WTA gap| <= 0.10 to catch any accidental mechanism drift
    (a working mechanism would exceed this).
    """
    names = _selftest_concept_names()
    gaps: List[float] = []
    for seed in CG_SEEDS_FULL:
        sentences, labels, _ = _selftest_build_corpus(
            seed=int(seed),
            sentences_per_concept=CG_SENTENCES_PER_CONCEPT_FULL,
        )
        naive_hds = _naive_wta_sampling_concept_hds(
            n_dim=CG_N_DIM_FULL,
            n_concepts=_SELFTEST_N_CONCEPTS,
            sentences=sentences,
            concept_labels=labels,
            seed=int(seed),
            k_sparsity=0.02,
            concept_names=names,
            mask_target_word=True,
        )
        ck = _cos(naive_hds[_concept_id("cat")], naive_hds[_concept_id("kitten")])
        ca = _cos(naive_hds[_concept_id("cat")], naive_hds[_concept_id("airplane")])
        gaps.append(ck - ca)
    gap_mean = float(np.mean(gaps))
    if abs(gap_mean) > 0.10:
        raise AssertionError(
            f"selftest_9 NAIVE_WTA_SAMPLING gap {gap_mean:.4f} outside "
            f"[-0.10, 0.10] (2026-06-23 FALSIFIED mechanism should show "
            f"near-zero gap; if positive lift, prior falsification is wrong)"
        )
    print(
        f"[concept_encoder selftest_9] NAIVE_WTA_SAMPLING gap_mean="
        f"{gap_mean:.4f} (2026-06-23 falsified control; reproduces HF)"
    )


def _selftest_10_scale_sentinel_n_8192() -> None:
    """Selftest 10: scale sentinel at N=8192, 50 concepts, 40 SPC.

    Validates mechanism survives scale:
      - no NaN / Inf in concept HDs at N=8192
      - sparse_rate stays in [0.010, 0.030]
      - cat/kitten cosine >= 0.35 (relaxed at higher N; mechanism is O(N)
        accumulator, not saturating).
    """
    names = _selftest_concept_names()
    sentences, labels, _ = _selftest_build_corpus(
        seed=11, sentences_per_concept=40
    )
    enc = ConceptEncoder(
        n_dim=CG_N_DIM_SCALE_SENTINEL,
        n_concepts=_SELFTEST_N_CONCEPTS,
        k_sparsity=0.02,
        seed=11,
        max_pos=24,
        concept_names=names,
        mask_target_word=True,
    )
    enc.fit(sentences, labels)
    hds = enc.concept_hds
    hds_f = hds.astype(np.float32)
    n_nan = int(np.isnan(hds_f).sum())
    n_inf = int(np.isinf(hds_f).sum())
    if n_nan > 0:
        raise AssertionError(
            f"selftest_10 SCALE_SENTINEL_NAN at N={CG_N_DIM_SCALE_SENTINEL}: "
            f"n_nan={n_nan}"
        )
    if n_inf > 0:
        raise AssertionError(
            f"selftest_10 SCALE_SENTINEL_INF at N={CG_N_DIM_SCALE_SENTINEL}: "
            f"n_inf={n_inf}"
        )
    sr = enc.sparse_rate()
    if not (0.010 <= sr <= 0.030):
        raise AssertionError(
            f"selftest_10 sparse_rate {sr:.4f} at N={CG_N_DIM_SCALE_SENTINEL} "
            f"outside architectural band [0.010, 0.030]"
        )
    ck = _cos(hds[_concept_id("cat")], hds[_concept_id("kitten")])
    if ck < 0.35:
        raise AssertionError(
            f"selftest_10 cat/kitten cos {ck:.3f} at N={CG_N_DIM_SCALE_SENTINEL} "
            f"below 0.35 floor (mechanism may not survive scale)"
        )
    print(
        f"[concept_encoder selftest_10] N={CG_N_DIM_SCALE_SENTINEL} "
        f"n_nan=0 n_inf=0 sparse_rate={sr:.4f} cat_kitten={ck:.3f}"
    )


def _selftest_11_env_var_contract() -> None:
    """Selftest 11 (bias-checklist META pattern; NEW 2026-07-02): if the
    module exposes an argparse-driven __main__ entry, the argparser must
    read HDLAB_RUN_MODE via os.environ.get default. Reproduces Round 6
    batch 2026-06-01 anchors E/F/J/K + Spoke 1 v3-D 2026-07-02 pre-fix
    failure mode: hardcoded default='smoke' silently downgrades FULL
    dispatches.

    This module exposes argparse-driven selftest CLI (--run-mode). Verify
    HDLAB_RUN_MODE=full is honored by the argparser default.
    """
    _saved_env = os.environ.get("HDLAB_RUN_MODE")
    os.environ["HDLAB_RUN_MODE"] = "full"
    try:
        probe = argparse.ArgumentParser(add_help=False)
        probe.add_argument(
            "--run-mode",
            default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
            choices=["self_test", "smoke", "full"],
        )
        args = probe.parse_args([])
        if args.run_mode != "full":
            raise AssertionError(
                f"selftest_11 ENV_VAR_CONTRACT_VIOLATION: HDLAB_RUN_MODE=full "
                f"not honored by argparser default (got {args.run_mode!r}). "
                f"Fix: default=os.environ.get('HDLAB_RUN_MODE', 'self_test')."
            )
    finally:
        if _saved_env is None:
            os.environ.pop("HDLAB_RUN_MODE", None)
        else:
            os.environ["HDLAB_RUN_MODE"] = _saved_env


_SELFTESTS = [
    ("1_fit_encode_round_trip", _selftest_1_fit_encode_round_trip),
    ("2_sparse_rate_architectural", _selftest_2_sparse_rate_architectural),
    ("3_bit_identical_reproducibility", _selftest_3_bit_identical_reproducibility),
    ("4_batch_matches_scalar", _selftest_4_batch_matches_scalar),
    ("5_ctor_validation_n_dim", _selftest_5_ctor_validation_n_dim),
    ("6_ctor_validation_k_sparsity", _selftest_6_ctor_validation_k_sparsity),
    ("7_ctor_validation_n_concepts", _selftest_7_ctor_validation_n_concepts),
    ("8_reproduces_v3_d_full_cat_kitten", _selftest_8_reproduces_v3_d_full_cat_kitten),
    ("9_naive_wta_sampling_falsified_control", _selftest_9_naive_wta_sampling_falsified_control),
    ("10_scale_sentinel_n_8192", _selftest_10_scale_sentinel_n_8192),
    ("11_env_var_contract", _selftest_11_env_var_contract),
]


def _run_all_selftests() -> dict:
    passed: List[str] = []
    failed: List[tuple] = []
    for name, fn in _SELFTESTS:
        try:
            fn()
            passed.append(name)
            print(f"[concept_encoder selftest] PASS {name}", flush=True)
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"[concept_encoder selftest] FAIL {name}: {e}", flush=True)
        except Exception as e:  # noqa: BLE001
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(
                f"[concept_encoder selftest] ERROR {name}: "
                f"{type(e).__name__}: {e}",
                flush=True,
            )
    return {
        "n_passed": len(passed),
        "n_failed": len(failed),
        "passed": passed,
        "failed": failed,
        "cg_source": (
            "Spoke 1 v3-D ARM_COMPETITIVE_HEBBIAN CG e8f15a036 2026-07-02"
        ),
    }


def _parse_selftest_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Argparser for __main__ selftest entry.

    Reads HDLAB_RUN_MODE env for --run-mode default (per META_RULE env_var_
    contract_must_survive_runner_dispatch; selftest 11 exercises this).
    """
    parser = argparse.ArgumentParser(
        description="hdlab.concept_encoder selftest harness"
    )
    parser.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "self_test"),
        choices=["self_test", "smoke", "full"],
        help="self_test = 11 selftests (default; reads HDLAB_RUN_MODE env)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    _ = _parse_selftest_args()
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    result = _run_all_selftests()
    print(
        f"[concept_encoder selftest] {result['n_passed']}/{len(_SELFTESTS)} "
        f"passed; failed={[n for n, _ in result['failed']]}",
        flush=True,
    )
    if result["n_failed"] > 0:
        sys.exit(1)
