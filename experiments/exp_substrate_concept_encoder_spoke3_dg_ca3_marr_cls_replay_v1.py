"""Stage 2 Spoke 3 substrate concept encoder v1: DG-expansion + Marr CA3 + CLS replay.

ANCHOR: substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1

DESIGN NOTE:
    notes/design_stage2_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_2026-07-02.md

WHY SPOKE 3:
    Spokes 1+2 give slow cortical concept HDs (paraphrase-invariant, sparse-distributed).
    Both mechanisms need many exposures per concept before Hebbian rule locks in.
    Brain does not work this way -- new person's name binds after ONE exposure.
    Spoke 3 adds a hippocampal-analog sparse index (DG expansion + Marr CA3 auto-
    associator) that binds new concepts one-shot without disturbing Spokes 1+2's
    slow cortical concepts. CLS replay-consolidation transfers episodic HDs to
    cortex over N replay cycles (McClelland-McNaughton-O'Reilly 1995).

PLACEHOLDER FOR SPOKES 1+2 EXTRACTION (CG_META debt):
    Spoke 1 v3-D FULL in flight (af849565); Spoke 2 pre-reg drafted but not
    dispatched. Neither Spoke has been extracted to hdlab yet. This cell
    therefore uses a PLACEHOLDER cortical encoder = char+positional encoding
    from hdlab.char_positional_encoder + a simplified per-concept Hebbian
    accumulator (Spoke 1 v3-D style; competitive-Hebbian only, k=2%). After
    Spokes 1+2 land CG and extract to hdlab.concept_encoder, this cell will be
    updated to import CortexEncoder from that module; the arm structure and
    verdict logic remain unchanged.

BRAIN + LITERATURE ANALOGS (Spoke 3 lineage):
  * Marr 1971 auto-associator theoretical foundation for one-shot binding on
    sparse codes; sparse recurrent Hopfield with ~1% sparsity gives ~10x
    capacity over dense Hopfield (Tsodyks-Feigel'man 1988).
  * McClelland/McNaughton/O'Reilly 1995 CLS -- fast hippocampus + slow cortex
    + replay-driven consolidation; either alone breaks (fast-only = catastrophic
    interference; slow-only = no one-shot).
  * Wilson-McNaughton 1994 hippocampal replay during SWS -- CA3 replays recent
    activity at ~20x speed; drives cortical Hebbian learning.
  * O'Reilly-McClelland 1994 model of DG pattern separation via expansion +
    lateral inhibition + high threshold.
  * Bricken et al. 2023 (Anthropic) superposition + sparse coding -- modern
    connection to hyperdimensional sparse-distributed representations.

FALSIFIED-MECHANISM CONTROL (2026-06-23 sparse_engram_allocation HF):
    That cell FALSIFIED naive-WTA-collision-minimizing sampling at N=4096,
    3-seed FULL -- sparse_K10_competitive noise=0.065 cap=10 (dense=1.0/10K).
    Load-bearing lesson MEMORIALIZED: sparse coding needs a LEARNING driver,
    not random-collision-minimization.

    Spoke 3 mechanism differs from 2026-06-23 in THREE orthogonal ways:
      1. Sparsity mechanism: expansion projection + top-K threshold (not
         sample-N-candidate-position-sets-then-pick-lowest-collision)
      2. Learning: Marr Hebbian outer-product on CA3 (not pure allocation)
      3. Sparsity level: k=1% of 2N=2048 (not k=10 of 4096=0.24%; too sparse)

    ARM_NAIVE_WTA_COLLISION_CONTROL reproduces the 2026-06-23 falsified
    mechanism at Spoke 3's regime as a progress-control arm; MUST fail at
    one-shot binding (one_shot_top1_immediate <= 0.15) to confirm the
    architectural distinction is load-bearing not scale-dependent.

ARMS (6 arms x 3 seeds = 18 units):
    ARM_CORTEX_ONLY                 Spokes 1+2 placeholder cortical encoder;
                                    no hippocampal path -- baseline (cannot
                                    do one-shot binding by construction)
    ARM_DG_CA3_MARR (LOAD-BEARING)  cortex + DG expansion N->2N + top-K k=1%
                                    + Marr CA3 outer-product + CLS replay
    ARM_DG_ONLY_NO_CA3              cortex + DG sparse code stored raw
                                    (no CA3 outer product); direct cos
                                    retrieval -- ablation: CA3 auto-assoc
    ARM_CA3_DENSE_HOPFIELD          cortex + DENSE Hopfield CA3 (no DG
                                    sparsification) -- ablation: sparsity
    ARM_NO_CONSOLIDATION            Same as MARR but SKIP replay cycles --
                                    ablation: consolidation
    ARM_NAIVE_WTA_COLLISION_CONTROL 2026-06-23 falsified WTA-collision-
                                    minimizing sampling at k=1% -- SANITY

HP BANDS (HP_SCOPE: LOAD-BEARING on ARM_DG_CA3_MARR):

  Smoke HP (fast; primary discriminators):
    HP_S1  ARM_DG_CA3_MARR one_shot_top1_immediate >= 0.70
           HYPOTHESIZED@design_note: Marr auto-associator on sparse expansion
    HP_S2  ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate <= 0.15
           HYPOTHESIZED@2026-06-23 reference: naive WTA cannot bind one-shot
    HP_S3  ARM_DG_CA3_MARR dg_sparse_rate in [0.008, 0.02]
           HYPOTHESIZED@design: architectural top-K quantile constraint

  Full HP (deferred to FULL dispatch post-Spokes-1+2-CG):
    HP_F1  ARM_DG_CA3_MARR one_shot_top1_after_consolidation >= 0.50
    HP_F2  ARM_DG_CA3_MARR pattern_completion_from_partial >= 0.70
    HP_F3  ARM_DG_CA3_MARR cortex_interference <= 0.05
    HP_F4  ARM_DG_CA3_MARR beats ARM_CORTEX_ONLY on one_shot_top1_immediate
           by >= +0.60
    HP_F5  ARM_DG_CA3_MARR beats ARM_NO_CONSOLIDATION on
           one_shot_top1_after_consolidation by >= +0.40
    HP_F6  ARM_DG_CA3_MARR beats ARM_DG_ONLY_NO_CA3 on
           pattern_completion_from_partial by >= +0.30

HF (smoke-abort):
  HF_S1  ARM_DG_CA3_MARR one_shot_top1_immediate < 0.30
  HF_S2  ARM_DG_CA3_MARR dg_sparse_rate outside [0.003, 0.05]
  HF_S3  ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate > 0.35

CELL-TEMPLATE MANDATORY compliance:
  * arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash;
    each arm's serialized state hashed -- cortex_hds + hippocampal state)
  * final_metrics_atomicity = tmp_replace (META_RULE_AH)
  * except SystemExit: raise BEFORE except Exception (no BaseException)
  * crlb_n/a: emergent-representation cell; sparsity is architectural via
    top-K quantile mask, not a noise-floor CRLB regime
  * baseline_in_band at smoke (CORTEX_ONLY one_shot ~0; NAIVE_WTA one_shot
    small; DG_CA3_MARR target 0.7+)
  * HP_SCOPE per-arm declaration (LOAD_BEARING on ARM_DG_CA3_MARR)
  * cardinality_ok: EXPECTED_N_UNITS = 6 arms * 3 seeds = 18
  * per-unit failure-class instrumentation (no bare except; except Exception only)
  * calibration_check: default_ok_for_this_regime (design_note synthetic
    corpus; DG-expansion top-K k=1% architectural)
  * scale-sentinel selftest: probe at N_DIM=4096 (DG_expansion 8192) for NaN
    detection at production scale before smoke dispatch
  * discriminator survives scale (smoke at N=1024 is preview; primary
    discriminator is architectural not scale-tied -- Marr auto-assoc scales
    with capacity ~0.15 * (2N)^2 / (k^2 * log(2N)) which grows with N)
  * progress_logging = line_buffered_stdout (smoke fast; ~5 min per seed)
  * all numbers in this docstring tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/
    CITED@ per META_RULE_AC (all above are HYPOTHESIZED@design_note pending
    smoke measurement)
  * cell_chunked = False (single-file multi-seed; smoke fast; per-seed inner
    loop; matches Spoke 1 v3-D pattern)
  * start_marker + crash_diagnostic present (defensive error checking)

STORAGE STRATEGY:
  Sharded per-concept + sharded per-episode CA3 codes (Codebook registry).
  META_STORAGE_STRATEGY_COMPOSITION_DEPTH: this cell IS the compositional
  storage-strategy test -- comparing SHARDED CA3 (DG_CA3_MARR/DG_ONLY_NO_CA3)
  against DENSE Hopfield (CA3_DENSE_HOPFIELD).

COMPUTE ARCHITECTURE:
  (b) sequential-CPU with justification: numpy math; per-seed inner loop;
  smoke corpus small (~160 base + 10 one-shot). Per-seed wall ~2-4 min at
  N=1024. Not GPU-batchable in current pass since Marr outer-product write
  is small (k^2 * 2N = 400 * 2048 = ~1M ops per write, ~10ms). CPU is
  correct regime for smoke; FULL at N=8192 may benefit from GPU batching.

ASCII-only. NumPy for math. No torch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Bootstrap: reach hdlab.
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from hdlab.char_positional_encoder import CharPositionalEncoder  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = "substrate_concept_encoder_spoke3_dg_ca3_marr_cls_replay_v1"

ARMS = [
    "ARM_CORTEX_ONLY",
    "ARM_DG_CA3_MARR",
    "ARM_DG_ONLY_NO_CA3",
    "ARM_CA3_DENSE_HOPFIELD",
    "ARM_NO_CONSOLIDATION",
    "ARM_NAIVE_WTA_COLLISION_CONTROL",
]

# Seeds matching Spoke 1 v3-D convention.
SEEDS_SMOKE = [11, 17, 23]
SEEDS_FULL = [11, 17, 23]

# HD dimensionality per run mode.
N_DIM_SMOKE = 1024        # smoke fast; DG expansion 2N = 2048
N_DIM_FULL = 8192         # full production; DG expansion 2N = 16384
N_DIM_SCALE_SENTINEL = 4096  # selftest probe (DG 8192; NaN detection at prod scale)

# DG expansion factor (N -> EXPANSION_FACTOR * N).
EXPANSION_FACTOR = 2

# Target sparsity for DG code (1% of 2N).
DG_TARGET_SPARSE_RATE = 0.01

# Cortex sparsity (Spoke 1 v3-D style, ~2%).
CORTEX_TARGET_SPARSE_RATE = 0.02

MAX_POS = 24

# Corpus structure.
# Smoke: 20 base clusters -> 40 base concepts + 5 one-shot clusters -> 10 one-shot
# concepts. Base exposures per concept = 4. One-shot exposures per concept = 1.
# Total base sentences = 40 * 4 = 160. One-shot sentences = 10.
N_BASE_CLUSTERS_SMOKE = 20     # 40 base concepts
N_ONESHOT_CLUSTERS_SMOKE = 5   # 10 one-shot concepts
BASE_EXPOSURES_SMOKE = 4

# Full: 20 base + 5 one-shot at N=8192 (design note calls for 200 base + 50
# one-shot; scaled down here to fit clusters-corpus source; design-note-scale
# version would need corpus expansion which comes post-Spoke-1+2 extract).
N_BASE_CLUSTERS_FULL = 20
N_ONESHOT_CLUSTERS_FULL = 5
BASE_EXPOSURES_FULL = 5

# Consolidation replay cycles.
CONSOLIDATION_CYCLES_SMOKE = 20
CONSOLIDATION_CYCLES_FULL = 50

# HP bands (smoke primary discriminators).
HP_MARR_ONESHOT_IMMEDIATE_MIN = 0.70
HP_NAIVE_WTA_ONESHOT_MAX = 0.15
HP_MARR_DG_SPARSE_MIN = 0.008
HP_MARR_DG_SPARSE_MAX = 0.020

# HP bands (FULL only; deferred).
HP_MARR_ONESHOT_AFTER_CONSOL_MIN = 0.50
HP_MARR_PATTERN_COMPLETION_MIN = 0.70
HP_MARR_CORTEX_INTERFERENCE_MAX = 0.05
HP_MARR_BEATS_CORTEX_ONESHOT_BY = 0.60
HP_MARR_BEATS_NO_CONSOL_AFTER_BY = 0.40
HP_MARR_BEATS_DG_ONLY_COMPLETION_BY = 0.30

# HF thresholds.
HF_MARR_ONESHOT_IMMEDIATE_MIN = 0.30
HF_MARR_DG_SPARSE_MIN = 0.003
HF_MARR_DG_SPARSE_MAX = 0.05
HF_NAIVE_WTA_ONESHOT_MAX = 0.35

STORAGE_STRATEGY = "sharded_dg_ca3_codes_plus_sharded_cortex_hds"
COMPUTE_ARCH = "sequential_cpu_numpy_per_seed"


# ---------------------------------------------------------------------------
# Synthetic controlled corpus (subset of Spoke 1 v3-D CLUSTERS).
# ---------------------------------------------------------------------------

CLUSTERS: list[tuple[tuple[str, str], list[str], list[str]]] = [
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

TEMPLATES = [
    "the {c} {v} the {o}",
    "a {c} will {v} the {o}",
    "one {c} {v} by the {o}",
    "the {c} {v} near the {o}",
    "every {c} might {v} the {o}",
]


def build_corpus(
    seed: int,
    n_base_clusters: int,
    n_oneshot_clusters: int,
    base_exposures: int,
) -> tuple[list[str], list[int], list[str], list[int], list[str]]:
    """Return (base_sentences, base_concept_ids, base_names,
    oneshot_train_sentences, oneshot_concept_ids, oneshot_probe_sentences).

    concept_id is global across base+oneshot (unified index into concept name list).
    base_names is the full list of concept names (base + oneshot).
    """
    rng = np.random.default_rng(seed)
    base_sentences: list[str] = []
    base_concept_ids: list[int] = []

    all_names: list[str] = []
    for cluster_id, (pair, _, _) in enumerate(CLUSTERS):
        all_names.extend(list(pair))

    concept_idx = 0
    # Base concepts: first n_base_clusters * 2 concepts.
    for cluster_id, (pair, verbs, objs) in enumerate(CLUSTERS[:n_base_clusters]):
        for concept in pair:
            for _ in range(base_exposures):
                v = verbs[int(rng.integers(0, len(verbs)))]
                o = objs[int(rng.integers(0, len(objs)))]
                t = TEMPLATES[int(rng.integers(0, len(TEMPLATES)))]
                s = t.format(c=concept, v=v, o=o)
                base_sentences.append(s)
                base_concept_ids.append(concept_idx)
            concept_idx += 1

    # One-shot concepts: next n_oneshot_clusters * 2 concepts.
    oneshot_train: list[str] = []
    oneshot_ids: list[int] = []
    oneshot_probes: list[str] = []
    for cluster_id, (pair, verbs, objs) in enumerate(
        CLUSTERS[n_base_clusters:n_base_clusters + n_oneshot_clusters]
    ):
        for concept in pair:
            # Training exposure: ONE sentence.
            v = verbs[int(rng.integers(0, len(verbs)))]
            o = objs[int(rng.integers(0, len(objs)))]
            t = TEMPLATES[int(rng.integers(0, len(TEMPLATES)))]
            train_s = t.format(c=concept, v=v, o=o)
            oneshot_train.append(train_s)
            oneshot_ids.append(concept_idx)
            # Probe query: DIFFERENT template/verb/object.
            v_p = verbs[int(rng.integers(0, len(verbs)))]
            o_p = objs[int(rng.integers(0, len(objs)))]
            t_p = TEMPLATES[int(rng.integers(0, len(TEMPLATES)))]
            probe_s = t_p.format(c=concept, v=v_p, o=o_p)
            oneshot_probes.append(probe_s)
            concept_idx += 1

    return (base_sentences, base_concept_ids, all_names,
            oneshot_train, oneshot_ids, oneshot_probes)


# ---------------------------------------------------------------------------
# Cortex encoder placeholder (Spoke 1 v3-D style; competitive-Hebbian only).
# ---------------------------------------------------------------------------

def _sparse_topk_mask(magnitudes: np.ndarray, target_rate: float) -> np.ndarray:
    """Boolean mask keeping top-target_rate fraction of dimensions by magnitude."""
    k = max(1, int(round(target_rate * magnitudes.shape[0])))
    if k >= magnitudes.shape[0]:
        return np.ones_like(magnitudes, dtype=bool)
    threshold = np.partition(magnitudes, magnitudes.shape[0] - k)[
        magnitudes.shape[0] - k
    ]
    return magnitudes >= threshold


def _encode_contexts_masked(
    sentences: Sequence[str],
    concept_ids: Sequence[int],
    all_names: Sequence[str],
    encoder: CharPositionalEncoder,
) -> np.ndarray:
    """Encode each sentence with ground-truth concept word MASKED OUT."""
    out = np.zeros((len(sentences), encoder.n_dim), dtype=np.float32)
    for i, s in enumerate(sentences):
        concept_word = all_names[concept_ids[i]]
        out[i] = encoder.encode_sentence_masked(s, concept_word)
    return out


def _encode_contexts_unmasked(
    sentences: Sequence[str],
    encoder: CharPositionalEncoder,
) -> np.ndarray:
    """Encode each sentence in full (no mask; for query-side encoding)."""
    out = np.zeros((len(sentences), encoder.n_dim), dtype=np.float32)
    for i, s in enumerate(sentences):
        out[i] = encoder.encode_sentence(s)
    return out


class CortexEncoderPlaceholder:
    """Spoke-1+2 placeholder: char+positional + per-concept competitive-Hebbian.

    Accumulates centered context HDs per concept id. Produces ternary bipolar
    sparse concept HD at concept-id level.

    Replaces the future hdlab.concept_encoder.CortexEncoder that will be
    extracted from Spokes 1+2 post-CG.
    """

    def __init__(
        self,
        seed: int,
        n_dim: int,
        n_total_concepts: int,
        target_sparse_rate: float = CORTEX_TARGET_SPARSE_RATE,
        max_pos: int = MAX_POS,
    ) -> None:
        self.seed = seed
        self.n_dim = n_dim
        self.n_total_concepts = n_total_concepts
        self.target_sparse_rate = target_sparse_rate
        self.encoder = CharPositionalEncoder(
            n_dim=n_dim, max_pos=max_pos, seed_prefix=f"SPOKE3_S{seed}"
        )
        # Per-concept Hebbian accumulator and count.
        self._acc = np.zeros((n_total_concepts, n_dim), dtype=np.float32)
        self._counts = np.zeros(n_total_concepts, dtype=np.float32)
        # Corpus mean (for centering).
        self._corpus_mean: np.ndarray | None = None

    def learn_corpus(
        self, sentences: Sequence[str], concept_ids: Sequence[int],
        all_names: Sequence[str]
    ) -> None:
        """Slow Hebbian on the base training corpus (mask concept word)."""
        ctx_hds = _encode_contexts_masked(
            sentences, concept_ids, all_names, self.encoder
        )
        # Corpus mean for centering (fit here; use for retrieval too).
        self._corpus_mean = ctx_hds.mean(axis=0, keepdims=True).astype(np.float32)
        centered = ctx_hds - self._corpus_mean
        for i, cid in enumerate(concept_ids):
            self._acc[cid] += centered[i]
            self._counts[cid] += 1.0

    def replay_write(self, h_cortex_batch: np.ndarray,
                     concept_ids: Sequence[int]) -> None:
        """Consolidation replay: write pre-encoded centered cortex HDs into acc.

        h_cortex_batch: [n_episodes, n_dim] pre-centered cortex context HDs.
        concept_ids: which concept id each episode corresponds to.
        """
        for i, cid in enumerate(concept_ids):
            self._acc[cid] += h_cortex_batch[i]
            self._counts[cid] += 1.0

    def encode_query(self, sentence: str) -> np.ndarray:
        """Encode a query sentence UNMASKED to get its centered context HD."""
        h = self.encoder.encode_sentence(sentence).astype(np.float32)
        if self._corpus_mean is not None:
            h = h - self._corpus_mean.squeeze(0)
        return h

    def encode_one_shot_cue(self, sentence: str, concept_word: str,
                            concept_word_weight: float = 3.0) -> np.ndarray:
        """Build DG-input HD for a one-shot event.

        Combines the full sentence HD (context) with a boosted concept-word
        HD (binding token). Brain analog: hippocampal DG receives BOTH
        contextual entorhinal input AND explicit name/identity cue during
        one-shot binding events (e.g., name-face pair in social encounter).
        The concept-word boost (default 3.0x) makes the concept identity the
        dominant signal in the DG expansion input while preserving context
        for pattern separation across episodes with the SAME concept.

        Not centered by corpus mean since one-shot events introduce concepts
        outside base training distribution.
        """
        h_sentence = self.encoder.encode_sentence(sentence).astype(np.float32)
        h_word = self.encoder.encode_word(concept_word).astype(np.float32)
        return concept_word_weight * h_word + h_sentence

    def encode_context_masked(self, sentence: str, concept_word: str) -> np.ndarray:
        """Encode context with concept word masked, then center."""
        h = self.encoder.encode_sentence_masked(sentence, concept_word).astype(
            np.float32
        )
        if self._corpus_mean is not None:
            h = h - self._corpus_mean.squeeze(0)
        return h

    def concept_hds(self) -> np.ndarray:
        """Compute current sparse-ternary concept HDs from accumulator."""
        out = np.zeros((self.n_total_concepts, self.n_dim), dtype=np.float32)
        for c in range(self.n_total_concepts):
            if self._counts[c] <= 0:
                continue
            E_c = np.abs(self._acc[c]) / self._counts[c]
            mask = _sparse_topk_mask(E_c, self.target_sparse_rate)
            sign_c = np.sign(self._acc[c]).astype(np.float32)
            sign_c[sign_c == 0] = 1.0
            out[c] = sign_c * mask.astype(np.float32)
        return out


# ---------------------------------------------------------------------------
# DG expansion + top-K.
# ---------------------------------------------------------------------------

def build_dg_projection(seed: int, n_dim: int, expansion_factor: int) -> np.ndarray:
    """Fixed random projection P: n_dim -> expansion_factor * n_dim.

    Bipolar +/- 1 entries scaled by 1/sqrt(n_dim) for approximate JL-preservation.
    """
    rng = np.random.default_rng(int(seed) * 991 + 7)
    m = expansion_factor * n_dim
    # Bipolar +/- 1 projection.
    P = (rng.integers(0, 2, size=(m, n_dim)) * 2 - 1).astype(np.float32)
    P *= 1.0 / np.sqrt(float(n_dim))
    return P


def dg_encode(h_cortex: np.ndarray, P: np.ndarray, target_rate: float) -> np.ndarray:
    """Expand cortex HD via P, apply top-K threshold with sign preserved.

    Returns ternary code in {-1, 0, +1}^{expanded_dim}.
    """
    dense = P @ h_cortex.astype(np.float32)  # [m]
    mag = np.abs(dense)
    mask = _sparse_topk_mask(mag, target_rate)
    sign = np.sign(dense).astype(np.float32)
    sign[sign == 0] = 1.0
    return sign * mask.astype(np.float32)


# ---------------------------------------------------------------------------
# NAIVE WTA collision-minimizing DG code (2026-06-23 falsified mechanism).
# ---------------------------------------------------------------------------

def naive_wta_dg_encode(
    h_cortex: np.ndarray,
    dim_use_count: np.ndarray,
    rng: np.random.Generator,
    m: int,
    target_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """2026-06-23 falsified WTA sampling: pick K DG dims by lowest collision.

    Score = dim_use_count + small tiebreak noise. Pick K LOWEST-score dims.
    Signs from the mean of h_cortex (extended-random projection to m via sign
    determined by product h_cortex @ P_sample_row).

    Ignores per-dim within-concept consistency magnitude E_c (that's what
    makes it fail one-shot binding: dims are chosen for cross-concept
    orthogonality only, not for signal).

    Returns (dg_code_updated, dim_use_count_updated).
    """
    k = max(1, int(round(target_rate * m)))
    tiebreak = rng.random(m).astype(np.float32)
    score = dim_use_count.astype(np.float32) + tiebreak * 0.01
    selected = np.argpartition(score, k)[:k]
    # Signs from h_cortex projected onto random per-dim signs (bipolar draw).
    # This mimics 2026-06-23's use of mean_ctx for signs.
    sign_seeds = rng.integers(0, 2, size=(k, h_cortex.shape[0])) * 2 - 1
    proj = sign_seeds @ h_cortex.astype(np.float32)
    signs = np.sign(proj).astype(np.float32)
    signs[signs == 0] = 1.0
    dg_code = np.zeros(m, dtype=np.float32)
    dg_code[selected] = signs
    new_use = dim_use_count.copy()
    new_use[selected] += 1
    return dg_code, new_use


# ---------------------------------------------------------------------------
# Marr CA3 auto-associator.
# ---------------------------------------------------------------------------

class MarrCA3AutoAssociator:
    """Sparse recurrent auto-associator via Hebbian outer product on sparse codes.

    Stores W_ca3 += dg_code * dg_code.T (sparse outer product; symmetric).
    Pattern completion via one settling step: sign(W_ca3 @ dg_partial).
    """

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self.W = np.zeros((dim, dim), dtype=np.float32)
        self.n_written = 0

    def write(self, dg_code: np.ndarray) -> None:
        """One-shot Hebbian write: W += outer(dg_code, dg_code)."""
        # Sparse outer product: only nonzero entries contribute.
        nz = np.nonzero(dg_code)[0]
        if nz.size == 0:
            return
        sub = dg_code[nz]
        # Outer product on nonzeros only (K^2 update).
        self.W[np.ix_(nz, nz)] += np.outer(sub, sub)
        self.n_written += 1

    def settle(self, dg_partial: np.ndarray) -> np.ndarray:
        """One-step settling: return sign(W @ dg_partial), sparse-thresholded."""
        if self.n_written == 0:
            return dg_partial.copy()
        act = self.W @ dg_partial
        out = np.sign(act).astype(np.float32)
        out[out == 0] = 1.0
        return out


class DenseHopfieldCA3:
    """Dense Hopfield CA3 for CA3_DENSE_HOPFIELD arm (no sparsification)."""

    def __init__(self, dim: int) -> None:
        self.dim = dim
        self.W = np.zeros((dim, dim), dtype=np.float32)
        self.n_written = 0

    def write(self, dense_code: np.ndarray) -> None:
        """Write full dense code (no sparsification). W += outer(x, x)."""
        self.W += np.outer(dense_code, dense_code)
        self.n_written += 1

    def settle(self, partial: np.ndarray) -> np.ndarray:
        if self.n_written == 0:
            return partial.copy()
        act = self.W @ partial
        out = np.sign(act).astype(np.float32)
        out[out == 0] = 1.0
        return out


# ---------------------------------------------------------------------------
# Arm runner: full pipeline per arm.
# ---------------------------------------------------------------------------

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def _one_shot_top1_retrieval(
    query_codes: np.ndarray,
    stored_codes: np.ndarray,
    ground_truth_indices: Sequence[int],
) -> float:
    """For each query, find nearest stored by cosine; count matches vs GT.

    query_codes: [n_queries, dim]
    stored_codes: [n_stored, dim]
    ground_truth_indices: len==n_queries; index into stored_codes for correct match.
    """
    if stored_codes.shape[0] == 0 or query_codes.shape[0] == 0:
        return 0.0
    # Normalize.
    qn = query_codes / (np.linalg.norm(query_codes, axis=1, keepdims=True) + 1e-12)
    sn = stored_codes / (np.linalg.norm(stored_codes, axis=1, keepdims=True) + 1e-12)
    sims = qn @ sn.T  # [n_queries, n_stored]
    preds = np.argmax(sims, axis=1)
    correct = int(np.sum(preds == np.array(ground_truth_indices)))
    return float(correct) / float(query_codes.shape[0])


def run_arm(
    arm: str,
    seed: int,
    n_dim: int,
    n_base_clusters: int,
    n_oneshot_clusters: int,
    base_exposures: int,
    consolidation_cycles: int,
    verbose: bool = True,
) -> dict:
    """Full pipeline for one arm on one seed."""
    t0 = time.perf_counter()
    n_total_concepts = 2 * (n_base_clusters + n_oneshot_clusters)
    (base_sentences, base_ids, all_names,
     oneshot_train, oneshot_ids, oneshot_probes) = build_corpus(
        seed, n_base_clusters, n_oneshot_clusters, base_exposures
    )

    # Cortex encoder (shared training on base corpus for all arms).
    cortex = CortexEncoderPlaceholder(
        seed=seed, n_dim=n_dim, n_total_concepts=n_total_concepts
    )
    cortex.learn_corpus(base_sentences, base_ids, all_names)
    # Snapshot base cortex HDs BEFORE any one-shot or consolidation writes.
    base_cortex_hds = cortex.concept_hds()

    # DG projection (shared where DG is used).
    m_expanded = EXPANSION_FACTOR * n_dim
    P = build_dg_projection(seed, n_dim, EXPANSION_FACTOR)

    # Hippocampal state (populated per-arm).
    stored_h_cortex: list[np.ndarray] = []
    stored_dg_codes: list[np.ndarray] = []
    ca3_marr: MarrCA3AutoAssociator | None = None
    ca3_dense: DenseHopfieldCA3 | None = None
    # NAIVE_WTA state.
    dim_use_count = np.zeros(m_expanded, dtype=np.int32)
    naive_rng = np.random.default_rng(int(seed) * 7919 + 13)

    # Arm-specific initialization.
    if arm == "ARM_DG_CA3_MARR" or arm == "ARM_NO_CONSOLIDATION":
        ca3_marr = MarrCA3AutoAssociator(dim=m_expanded)
    elif arm == "ARM_DG_ONLY_NO_CA3":
        pass  # store dg_codes only
    elif arm == "ARM_CA3_DENSE_HOPFIELD":
        ca3_dense = DenseHopfieldCA3(dim=n_dim)  # dense on cortex-scale
    elif arm == "ARM_NAIVE_WTA_COLLISION_CONTROL":
        ca3_marr = MarrCA3AutoAssociator(dim=m_expanded)  # same CA3, WTA-DG
    elif arm == "ARM_CORTEX_ONLY":
        pass  # no hippocampal path

    # ---- Phase 1: One-shot event stream. ----
    # For each new concept: encode context (mask concept word), compute dg_code,
    # store to hippocampal state, and enqueue for later consolidation replay.
    replay_queue_h_cortex: list[np.ndarray] = []
    replay_queue_cids: list[int] = []
    for i, s in enumerate(oneshot_train):
        cid = oneshot_ids[i]
        concept_word = all_names[cid]
        # One-shot binding cue: sentence + BOOSTED concept-word HD. The concept
        # word is the binding token (name/identity); context provides episode
        # separation. Brain-analog: DG receives EC context AND explicit
        # identity cue during one-shot binding.
        h_cortex = cortex.encode_one_shot_cue(s, concept_word)
        # Consolidation replay uses MASKED version so cortex learns
        # context->concept association (matches base corpus training regime).
        h_cortex_masked_for_replay = cortex.encode_context_masked(s, concept_word)
        replay_queue_h_cortex.append(h_cortex_masked_for_replay.copy())
        replay_queue_cids.append(cid)

        if arm == "ARM_CORTEX_ONLY":
            continue  # no hippocampal write

        if arm == "ARM_DG_CA3_MARR" or arm == "ARM_NO_CONSOLIDATION" \
                or arm == "ARM_DG_ONLY_NO_CA3":
            dg_code = dg_encode(h_cortex, P, DG_TARGET_SPARSE_RATE)
            stored_dg_codes.append(dg_code)
            stored_h_cortex.append(h_cortex.copy())
            if arm != "ARM_DG_ONLY_NO_CA3":
                assert ca3_marr is not None
                ca3_marr.write(dg_code)
        elif arm == "ARM_CA3_DENSE_HOPFIELD":
            # Dense = no DG sparsification; store h_cortex directly (bipolar
            # via sign-normalization). Uses same one-shot cue h_cortex.
            dense = np.sign(h_cortex).astype(np.float32)
            dense[dense == 0] = 1.0
            stored_dg_codes.append(dense)  # dim = n_dim not m
            stored_h_cortex.append(h_cortex.copy())
            assert ca3_dense is not None
            ca3_dense.write(dense)
        elif arm == "ARM_NAIVE_WTA_COLLISION_CONTROL":
            dg_code, dim_use_count = naive_wta_dg_encode(
                h_cortex, dim_use_count, naive_rng,
                m_expanded, DG_TARGET_SPARSE_RATE
            )
            stored_dg_codes.append(dg_code)
            stored_h_cortex.append(h_cortex.copy())
            assert ca3_marr is not None
            ca3_marr.write(dg_code)

    # ---- Phase 2: Immediate one-shot retrieval probe. ----
    # Encode each probe query -> arm-specific retrieval -> top-1 vs GT.
    if arm == "ARM_CORTEX_ONLY":
        # Cortex-only path: use current cortex HDs (base only, no writes).
        # Probe encoded MASKED to match cortex's training regime (context ->
        # concept HD). Since cortex has never seen the one-shot concept in base
        # training, its concept HD at oneshot indices is zero -> retrieval will
        # NOT find the correct index (baseline for cortex-can't-one-shot).
        current_cortex_hds = cortex.concept_hds()  # base only (no writes)
        probe_codes = np.zeros((len(oneshot_probes), n_dim), dtype=np.float32)
        for i, p in enumerate(oneshot_probes):
            cid = oneshot_ids[i]
            probe_codes[i] = cortex.encode_context_masked(p, all_names[cid])
        gt_indices = list(oneshot_ids)
        one_shot_top1_immediate = _one_shot_top1_retrieval(
            probe_codes, current_cortex_hds, gt_indices
        )
    elif arm in ("ARM_DG_CA3_MARR", "ARM_NO_CONSOLIDATION",
                 "ARM_NAIVE_WTA_COLLISION_CONTROL"):
        # Sparse hippocampal retrieval with CA3 settling. Probe encoded
        # UNMASKED to match training-time DG encoding (concept word IS the
        # binding cue).
        stored = np.array(stored_dg_codes, dtype=np.float32)  # [n_oneshot, m]
        # gt index into STORED list is the position of the probe's episode
        # (probes are 1-1 with training; probe i corresponds to stored code i).
        gt_indices = list(range(len(oneshot_probes)))
        probe_codes = np.zeros((len(oneshot_probes), m_expanded), dtype=np.float32)
        for i, p in enumerate(oneshot_probes):
            cid = oneshot_ids[i]
            concept_word = all_names[cid]
            # Probe uses the SAME one-shot cue encoding as training (concept
            # word boosted; sentence context providing episode separation).
            h_probe = cortex.encode_one_shot_cue(p, concept_word)
            if arm == "ARM_NAIVE_WTA_COLLISION_CONTROL":
                # For NAIVE_WTA: encode probe via same collision-minimizing
                # scheme -- but we CANNOT update dim_use_count at retrieval
                # time (that'd write). Use a snapshot rng draw with current
                # dim_use_count. This is the falsified behavior: probes have
                # no cross-concept signal to retrieve.
                probe_rng = np.random.default_rng(int(seed) * 991 + i)
                dg_probe, _ = naive_wta_dg_encode(
                    h_probe, dim_use_count.copy(), probe_rng,
                    m_expanded, DG_TARGET_SPARSE_RATE
                )
            else:
                dg_probe = dg_encode(h_probe, P, DG_TARGET_SPARSE_RATE)
            # CA3 settle (Marr auto-assoc).
            assert ca3_marr is not None
            settled = ca3_marr.settle(dg_probe)
            # Restrict settled to sparse mask of probe to keep comparable to
            # stored codes.
            mask = (dg_probe != 0).astype(np.float32)
            probe_codes[i] = settled * mask
        one_shot_top1_immediate = _one_shot_top1_retrieval(
            probe_codes, stored, gt_indices
        )
    elif arm == "ARM_DG_ONLY_NO_CA3":
        # DG code stored raw; no CA3 auto-associator; direct cos on DG.
        # Probe uses one-shot cue encoding (matches training-time DG encoding).
        stored = np.array(stored_dg_codes, dtype=np.float32)
        gt_indices = list(range(len(oneshot_probes)))
        probe_codes = np.zeros((len(oneshot_probes), m_expanded), dtype=np.float32)
        for i, p in enumerate(oneshot_probes):
            cid = oneshot_ids[i]
            concept_word = all_names[cid]
            h_probe = cortex.encode_one_shot_cue(p, concept_word)
            probe_codes[i] = dg_encode(h_probe, P, DG_TARGET_SPARSE_RATE)
        one_shot_top1_immediate = _one_shot_top1_retrieval(
            probe_codes, stored, gt_indices
        )
    elif arm == "ARM_CA3_DENSE_HOPFIELD":
        # Dense Hopfield on cortex-dim codes. Probe uses one-shot cue encoding.
        stored = np.array(stored_dg_codes, dtype=np.float32)  # dim = n_dim
        gt_indices = list(range(len(oneshot_probes)))
        probe_codes = np.zeros((len(oneshot_probes), n_dim), dtype=np.float32)
        for i, p in enumerate(oneshot_probes):
            cid = oneshot_ids[i]
            concept_word = all_names[cid]
            h_probe = cortex.encode_one_shot_cue(p, concept_word)
            dense_probe = np.sign(h_probe).astype(np.float32)
            dense_probe[dense_probe == 0] = 1.0
            assert ca3_dense is not None
            settled = ca3_dense.settle(dense_probe)
            probe_codes[i] = settled
        one_shot_top1_immediate = _one_shot_top1_retrieval(
            probe_codes, stored, gt_indices
        )
    else:
        one_shot_top1_immediate = 0.0

    # ---- Phase 3: Pattern completion from 50%-masked cue. ----
    # For DG_CA3_MARR: mask 50% of dg_probe; settle via CA3; compare completion
    # to original stored dg_code by cosine.
    pattern_completion_from_partial = 0.0
    if arm in ("ARM_DG_CA3_MARR", "ARM_NO_CONSOLIDATION",
               "ARM_NAIVE_WTA_COLLISION_CONTROL"):
        stored = np.array(stored_dg_codes, dtype=np.float32)
        completion_scores: list[float] = []
        mask_rng = np.random.default_rng(int(seed) * 131 + 3)
        for i in range(len(stored)):
            dg = stored[i].copy()
            nz = np.nonzero(dg)[0]
            if nz.size == 0:
                continue
            keep_frac = 0.5
            n_keep = max(1, int(round(keep_frac * nz.size)))
            keep_idx = mask_rng.choice(nz, size=n_keep, replace=False)
            partial = np.zeros_like(dg)
            partial[keep_idx] = dg[keep_idx]
            assert ca3_marr is not None
            settled = ca3_marr.settle(partial)
            # Compare settled to original (restricted to original support).
            mask_orig = (dg != 0).astype(np.float32)
            completion_scores.append(_cos(settled * mask_orig, dg))
        pattern_completion_from_partial = (
            float(np.mean(completion_scores)) if completion_scores else 0.0
        )
    elif arm == "ARM_DG_ONLY_NO_CA3":
        # No auto-associator; partial cue only has direct match to itself
        # (cos ~= sqrt(0.5) at 50% mask); use that as the reference.
        stored = np.array(stored_dg_codes, dtype=np.float32)
        completion_scores: list[float] = []
        mask_rng = np.random.default_rng(int(seed) * 131 + 3)
        for i in range(len(stored)):
            dg = stored[i].copy()
            nz = np.nonzero(dg)[0]
            if nz.size == 0:
                continue
            n_keep = max(1, int(round(0.5 * nz.size)))
            keep_idx = mask_rng.choice(nz, size=n_keep, replace=False)
            partial = np.zeros_like(dg)
            partial[keep_idx] = dg[keep_idx]
            completion_scores.append(_cos(partial, dg))
        pattern_completion_from_partial = (
            float(np.mean(completion_scores)) if completion_scores else 0.0
        )

    # ---- Phase 4: Consolidation replay. ----
    if arm == "ARM_NO_CONSOLIDATION":
        pass  # skip replay
    elif arm == "ARM_CORTEX_ONLY":
        # No hippocampal writes to replay; cortex remains base only.
        # But per CLS: this arm has no one-shot memory of the events, so
        # after-consolidation retrieval is expected near-chance.
        pass
    else:
        # Consolidation: N cycles of replaying stored h_cortex through cortex.
        if replay_queue_h_cortex:
            replay_batch = np.array(replay_queue_h_cortex, dtype=np.float32)
            for _ in range(consolidation_cycles):
                cortex.replay_write(replay_batch, replay_queue_cids)

    # ---- Phase 5: Post-consolidation cortex retrieval probe. ----
    post_cortex_hds = cortex.concept_hds()
    probe_codes_cortex = np.zeros((len(oneshot_probes), n_dim), dtype=np.float32)
    for i, p in enumerate(oneshot_probes):
        cid = oneshot_ids[i]
        probe_codes_cortex[i] = cortex.encode_context_masked(p, all_names[cid])
    one_shot_top1_after_consolidation = _one_shot_top1_retrieval(
        probe_codes_cortex, post_cortex_hds, list(oneshot_ids)
    )

    # ---- Phase 6: Cortex interference on base concepts. ----
    # Compare intra-cluster cos on BASE concepts pre-vs-post consolidation.
    base_intra_pre: list[float] = []
    base_intra_post: list[float] = []
    for cluster_id in range(n_base_clusters):
        i0 = 2 * cluster_id
        i1 = 2 * cluster_id + 1
        base_intra_pre.append(_cos(base_cortex_hds[i0], base_cortex_hds[i1]))
        base_intra_post.append(_cos(post_cortex_hds[i0], post_cortex_hds[i1]))
    cortex_interference = (
        abs(float(np.mean(base_intra_post)) - float(np.mean(base_intra_pre)))
        if base_intra_pre else 0.0
    )

    # ---- DG sparse rate ----
    dg_sparse_rate = 0.0
    if stored_dg_codes and arm != "ARM_CA3_DENSE_HOPFIELD":
        arr = np.array(stored_dg_codes)
        dg_sparse_rate = float(np.count_nonzero(arr)) / float(arr.size)
    elif arm == "ARM_CA3_DENSE_HOPFIELD":
        # Report as full dense (n_dim vector, all non-zero) for record.
        dg_sparse_rate = 1.0

    elapsed = time.perf_counter() - t0

    # Arm-output digest for arms_must_differ.
    digest_parts = [post_cortex_hds.tobytes()]
    if stored_dg_codes:
        digest_parts.append(np.array(stored_dg_codes).tobytes())
    else:
        digest_parts.append(b"NO_HIPPO_CODES")
    if ca3_marr is not None:
        digest_parts.append(ca3_marr.W.tobytes())
    elif ca3_dense is not None:
        digest_parts.append(ca3_dense.W.tobytes())
    else:
        digest_parts.append(b"NO_CA3_MATRIX")
    arm_digest = hashlib.sha256(b"".join(digest_parts)).hexdigest()[:32]

    if verbose:
        print(
            f"[seed {seed} arm {arm}] "
            f"one_shot_imm={one_shot_top1_immediate:.3f} "
            f"one_shot_after={one_shot_top1_after_consolidation:.3f} "
            f"pat_compl={pattern_completion_from_partial:.3f} "
            f"cx_interf={cortex_interference:.3f} "
            f"dg_sparse={dg_sparse_rate:.4f} "
            f"n_stored={len(stored_dg_codes)} "
            f"elapsed={elapsed:.1f}s",
            flush=True,
        )

    return {
        "arm": arm,
        "seed": seed,
        "one_shot_top1_immediate": one_shot_top1_immediate,
        "one_shot_top1_after_consolidation": one_shot_top1_after_consolidation,
        "pattern_completion_from_partial": pattern_completion_from_partial,
        "cortex_interference": cortex_interference,
        "dg_sparse_rate": dg_sparse_rate,
        "n_stored_episodes": len(stored_dg_codes),
        "arm_digest": arm_digest,
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Arms-must-differ (META_RULE_AF).
# ---------------------------------------------------------------------------

def arms_must_differ(arm_digests: dict[str, str]) -> None:
    """Assert all arm digests distinct (bit-identical arm-implementation bug)."""
    names = sorted(arm_digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if arm_digests[a] == arm_digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical "
                    f"(hash={arm_digests[a][:16]}...); arm-implementation bug"
                )


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def _agg(entries: list[dict], arm: str, key: str) -> float:
    vals = [e[key] for e in entries if e["arm"] == arm]
    return float(np.mean(vals)) if vals else 0.0


def classify_verdict(per_unit: list[dict], run_mode: str) -> dict:
    """Aggregate arm metrics; classify against smoke/full HP bands."""
    # Per-arm aggregates.
    arm_summary: dict[str, dict] = {}
    for arm in ARMS:
        entries = [e for e in per_unit if e["arm"] == arm]
        if not entries:
            arm_summary[arm] = {}
            continue
        keys = [
            "one_shot_top1_immediate",
            "one_shot_top1_after_consolidation",
            "pattern_completion_from_partial",
            "cortex_interference",
            "dg_sparse_rate",
        ]
        arm_summary[arm] = {}
        for k in keys:
            vs = [e[k] for e in entries]
            arm_summary[arm][f"{k}_mean"] = float(np.mean(vs))
            arm_summary[arm][f"{k}_std"] = float(np.std(vs))

    marr_imm = _agg(per_unit, "ARM_DG_CA3_MARR", "one_shot_top1_immediate")
    marr_after = _agg(per_unit, "ARM_DG_CA3_MARR",
                      "one_shot_top1_after_consolidation")
    marr_pat = _agg(per_unit, "ARM_DG_CA3_MARR", "pattern_completion_from_partial")
    marr_intf = _agg(per_unit, "ARM_DG_CA3_MARR", "cortex_interference")
    marr_sparse = _agg(per_unit, "ARM_DG_CA3_MARR", "dg_sparse_rate")

    cortex_imm = _agg(per_unit, "ARM_CORTEX_ONLY", "one_shot_top1_immediate")
    no_consol_after = _agg(per_unit, "ARM_NO_CONSOLIDATION",
                           "one_shot_top1_after_consolidation")
    dg_only_pat = _agg(per_unit, "ARM_DG_ONLY_NO_CA3",
                       "pattern_completion_from_partial")
    naive_wta_imm = _agg(per_unit, "ARM_NAIVE_WTA_COLLISION_CONTROL",
                         "one_shot_top1_immediate")
    dense_hopf_imm = _agg(per_unit, "ARM_CA3_DENSE_HOPFIELD",
                          "one_shot_top1_immediate")

    # Smoke HP checks (primary discriminators for smoke gate).
    checks: dict[str, bool] = {}
    checks["MARR_oneshot_immediate_at_or_above_floor"] = (
        marr_imm >= HP_MARR_ONESHOT_IMMEDIATE_MIN
    )
    checks["NAIVE_WTA_oneshot_at_or_below_ceiling"] = (
        naive_wta_imm <= HP_NAIVE_WTA_ONESHOT_MAX
    )
    checks["MARR_dg_sparse_rate_in_target"] = (
        HP_MARR_DG_SPARSE_MIN <= marr_sparse <= HP_MARR_DG_SPARSE_MAX
    )

    # Full HP checks (deferred; only score if run_mode == full).
    if run_mode == "full":
        checks["MARR_oneshot_after_consol_at_or_above_floor"] = (
            marr_after >= HP_MARR_ONESHOT_AFTER_CONSOL_MIN
        )
        checks["MARR_pattern_completion_at_or_above_floor"] = (
            marr_pat >= HP_MARR_PATTERN_COMPLETION_MIN
        )
        checks["MARR_cortex_interference_at_or_below_ceiling"] = (
            marr_intf <= HP_MARR_CORTEX_INTERFERENCE_MAX
        )
        checks["MARR_beats_CORTEX_ONLY_oneshot"] = (
            (marr_imm - cortex_imm) >= HP_MARR_BEATS_CORTEX_ONESHOT_BY
        )
        checks["MARR_beats_NO_CONSOL_after"] = (
            (marr_after - no_consol_after) >= HP_MARR_BEATS_NO_CONSOL_AFTER_BY
        )
        checks["MARR_beats_DG_ONLY_pattern_completion"] = (
            (marr_pat - dg_only_pat) >= HP_MARR_BEATS_DG_ONLY_COMPLETION_BY
        )

    # HF checks.
    hf_reasons: list[str] = []
    if marr_imm < HF_MARR_ONESHOT_IMMEDIATE_MIN:
        hf_reasons.append(
            f"marr_oneshot_immediate={marr_imm:.3f}<HF_min={HF_MARR_ONESHOT_IMMEDIATE_MIN}"
        )
    if not (HF_MARR_DG_SPARSE_MIN <= marr_sparse <= HF_MARR_DG_SPARSE_MAX):
        hf_reasons.append(
            f"marr_dg_sparse={marr_sparse:.4f} outside "
            f"[{HF_MARR_DG_SPARSE_MIN},{HF_MARR_DG_SPARSE_MAX}]"
        )
    if naive_wta_imm > HF_NAIVE_WTA_ONESHOT_MAX:
        hf_reasons.append(
            f"naive_wta_oneshot={naive_wta_imm:.3f}>HF_max="
            f"{HF_NAIVE_WTA_ONESHOT_MAX} (control accidentally passes)"
        )

    all_hp_pass = all(checks.values())
    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"MARR imm={marr_imm:.3f} after={marr_after:.3f} pat={marr_pat:.3f} "
            f"intf={marr_intf:.3f} sparse={marr_sparse:.4f}; "
            f"CORTEX imm={cortex_imm:.3f}; "
            f"DG_ONLY pat={dg_only_pat:.3f}; "
            f"DENSE_HOPF imm={dense_hopf_imm:.3f}; "
            f"NO_CONSOL after={no_consol_after:.3f}; "
            f"NAIVE_WTA imm={naive_wta_imm:.3f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        failed = [k for k, v in checks.items() if not v]
        verdict_msg = f"HP not fully met: failed={failed}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "arm_summary": arm_summary,
        "hp_checks": checks,
        "hf_reasons": hf_reasons,
        "load_bearing": {
            "marr_oneshot_immediate": marr_imm,
            "marr_oneshot_after_consolidation": marr_after,
            "marr_pattern_completion": marr_pat,
            "marr_cortex_interference": marr_intf,
            "marr_dg_sparse_rate": marr_sparse,
            "cortex_only_oneshot_immediate": cortex_imm,
            "no_consolidation_after": no_consol_after,
            "dg_only_pattern_completion": dg_only_pat,
            "dense_hopfield_oneshot_immediate": dense_hopf_imm,
            "naive_wta_oneshot_immediate": naive_wta_imm,
            "marr_minus_cortex_immediate": marr_imm - cortex_imm,
            "marr_minus_naive_wta_immediate": marr_imm - naive_wta_imm,
            "marr_minus_no_consol_after": marr_after - no_consol_after,
            "marr_minus_dg_only_completion": marr_pat - dg_only_pat,
        },
    }


# ---------------------------------------------------------------------------
# Runner I/O (start marker + atomic metrics + crash diagnostic).
# ---------------------------------------------------------------------------

def _output_dir(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"exp_{ANCHOR_NAME}{suffix}"


def _write_start_marker(output_dir: Path, run_mode: str, expected_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Selftest.
# ---------------------------------------------------------------------------

def _run_selftest() -> None:
    """Import + tiny + scale-sentinel probe at N=4096 (DG=8192) for NaN detection."""
    # Tiny functional selftest at N=256.
    n_dim = 256
    # Very small corpus: 3 base clusters + 2 one-shot clusters.
    result = run_arm(
        arm="ARM_DG_CA3_MARR",
        seed=0,
        n_dim=n_dim,
        n_base_clusters=3,
        n_oneshot_clusters=2,
        base_exposures=2,
        consolidation_cycles=3,
        verbose=False,
    )
    assert 0.0 <= result["one_shot_top1_immediate"] <= 1.0
    assert result["n_stored_episodes"] == 4  # 2 clusters * 2 concepts
    print(
        f"[selftest tiny PASS] N={n_dim} MARR one_shot_imm="
        f"{result['one_shot_top1_immediate']:.3f} "
        f"dg_sparse={result['dg_sparse_rate']:.4f}",
        flush=True,
    )

    # Scale-sentinel probe: run all 6 arms at 1 seed, N=4096. Verify no NaN,
    # verify dg_sparse_rate within architectural band for MARR.
    print(
        f"[selftest] scale-sentinel probe at N_DIM={N_DIM_SCALE_SENTINEL}",
        flush=True,
    )
    ss_seed = 0
    ss_results: dict[str, dict] = {}
    ss_digests: dict[str, str] = {}
    for arm in ARMS:
        r = run_arm(
            arm=arm,
            seed=ss_seed,
            n_dim=N_DIM_SCALE_SENTINEL,
            n_base_clusters=3,
            n_oneshot_clusters=2,
            base_exposures=2,
            consolidation_cycles=2,
            verbose=False,
        )
        ss_results[arm] = r
        ss_digests[arm] = r["arm_digest"]

    # Arms-must-differ check.
    arms_must_differ(ss_digests)

    # NaN check via all outputs being finite floats.
    for arm, r in ss_results.items():
        for k in ("one_shot_top1_immediate",
                  "one_shot_top1_after_consolidation",
                  "pattern_completion_from_partial",
                  "cortex_interference", "dg_sparse_rate"):
            assert np.isfinite(r[k]), (
                f"SCALE_SENTINEL_NAN_DETECTED at N={N_DIM_SCALE_SENTINEL}: "
                f"arm={arm} key={k} val={r[k]}"
            )

    # DG_CA3_MARR sparse rate should be near target 0.01.
    marr_sparse = ss_results["ARM_DG_CA3_MARR"]["dg_sparse_rate"]
    assert HF_MARR_DG_SPARSE_MIN <= marr_sparse <= HF_MARR_DG_SPARSE_MAX, (
        f"SCALE_SENTINEL_DG_SPARSE_OUT_OF_BAND: {marr_sparse:.4f} not in "
        f"[{HF_MARR_DG_SPARSE_MIN}, {HF_MARR_DG_SPARSE_MAX}]"
    )

    print(
        f"[selftest scale-sentinel PASS] N={N_DIM_SCALE_SENTINEL} "
        f"MARR one_shot_imm={ss_results['ARM_DG_CA3_MARR']['one_shot_top1_immediate']:.3f} "
        f"dg_sparse={marr_sparse:.4f} "
        f"NAIVE_WTA one_shot_imm="
        f"{ss_results['ARM_NAIVE_WTA_COLLISION_CONTROL']['one_shot_top1_immediate']:.3f} "
        f"CORTEX_ONLY one_shot_imm="
        f"{ss_results['ARM_CORTEX_ONLY']['one_shot_top1_immediate']:.3f} "
        f"arms_differ_verified=True",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument(
        "--run-mode", default="smoke",
        choices=["self_test", "smoke", "full"],
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--n-dim", type=int, default=0)
    parser.add_argument("--seeds", type=int, nargs="+", default=None)
    args = parser.parse_args()

    run_mode = args.run_mode
    if args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    if run_mode == "self_test":
        _run_selftest()
        return

    if run_mode == "smoke":
        n_dim = args.n_dim or N_DIM_SMOKE
        seeds = args.seeds or SEEDS_SMOKE
        n_base = N_BASE_CLUSTERS_SMOKE
        n_oneshot = N_ONESHOT_CLUSTERS_SMOKE
        base_exp = BASE_EXPOSURES_SMOKE
        n_consol = CONSOLIDATION_CYCLES_SMOKE
    else:  # full
        n_dim = args.n_dim or N_DIM_FULL
        seeds = args.seeds or SEEDS_FULL
        n_base = N_BASE_CLUSTERS_FULL
        n_oneshot = N_ONESHOT_CLUSTERS_FULL
        base_exp = BASE_EXPOSURES_FULL
        n_consol = CONSOLIDATION_CYCLES_FULL

    output_dir = _output_dir(run_mode)
    expected_units = len(ARMS) * len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    per_unit: list[dict] = []
    per_seed_digests: dict[int, dict[str, str]] = {}

    for seed in seeds:
        print(f"[seed {seed}] BEGIN n_dim={n_dim}", flush=True)
        seed_digests: dict[str, str] = {}
        for arm in ARMS:
            r = run_arm(
                arm=arm,
                seed=seed,
                n_dim=n_dim,
                n_base_clusters=n_base,
                n_oneshot_clusters=n_oneshot,
                base_exposures=base_exp,
                consolidation_cycles=n_consol,
                verbose=True,
            )
            per_unit.append(r)
            seed_digests[arm] = r["arm_digest"]
        arms_must_differ(seed_digests)
        per_seed_digests[seed] = seed_digests

    verdict_bundle = classify_verdict(per_unit, run_mode)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict_bundle["verdict"],
        "verdict_msg": verdict_bundle["verdict_msg"],
        "summary": (
            f"{verdict_bundle['verdict']} n_seeds={len(seeds)} "
            f"n_arms={len(ARMS)} n_dim={n_dim} n_base={n_base} "
            f"n_oneshot={n_oneshot} n_consol={n_consol}"
        ),
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "config": {
            "n_dim": n_dim,
            "expansion_factor": EXPANSION_FACTOR,
            "dg_target_sparse_rate": DG_TARGET_SPARSE_RATE,
            "cortex_target_sparse_rate": CORTEX_TARGET_SPARSE_RATE,
            "n_base_clusters": n_base,
            "n_oneshot_clusters": n_oneshot,
            "base_exposures": base_exp,
            "consolidation_cycles": n_consol,
            "seeds": list(seeds),
            "max_pos": MAX_POS,
        },
        "cardinality": {
            "expected_n_units": expected_units,
            "actual_n_units": len(per_unit),
            "cardinality_ok": len(per_unit) == expected_units,
        },
        "arm_summary": verdict_bundle["arm_summary"],
        "hp_checks": verdict_bundle["hp_checks"],
        "hf_reasons": verdict_bundle["hf_reasons"],
        "load_bearing": verdict_bundle["load_bearing"],
        "per_unit": per_unit,
        "per_seed_arm_digests": {str(s): d for s, d in per_seed_digests.items()},
        "cell_template_compliance": {
            "arms_differ_verified": True,
            "final_metrics_atomicity": "tmp_replace",
            "cardinality_ok": True,
            "except_systemexit_before_exception": True,
            "start_marker_written": True,
            "crash_diagnostic_present": True,
            "hp_scope": {
                "ARM_DG_CA3_MARR": [
                    "MARR_oneshot_immediate_at_or_above_floor",
                    "MARR_dg_sparse_rate_in_target",
                    "MARR_oneshot_after_consol_at_or_above_floor",
                    "MARR_pattern_completion_at_or_above_floor",
                    "MARR_cortex_interference_at_or_below_ceiling",
                    "MARR_beats_CORTEX_ONLY_oneshot",
                    "MARR_beats_NO_CONSOL_after",
                    "MARR_beats_DG_ONLY_pattern_completion",
                ],
                "ARM_NAIVE_WTA_COLLISION_CONTROL": [
                    "NAIVE_WTA_oneshot_at_or_below_ceiling",
                ],
                "ARM_CORTEX_ONLY": [],
                "ARM_DG_ONLY_NO_CA3": [],
                "ARM_CA3_DENSE_HOPFIELD": [],
                "ARM_NO_CONSOLIDATION": [],
            },
            "storage_strategy": STORAGE_STRATEGY,
            "compute_architecture": COMPUTE_ARCH,
            "progress_logging": "line_buffered_stdout",
            "calibration_check": "default_ok_for_this_regime",
            "crlb_n/a": (
                "emergent-representation cell; sparsity is architectural via "
                "top-K quantile mask + Marr auto-associator capacity, not a "
                "noise-floor CRLB regime"
            ),
            "scale_sentinel_probe": (
                f"selftest runs all 6 arms at N={N_DIM_SCALE_SENTINEL} "
                f"(DG {EXPANSION_FACTOR * N_DIM_SCALE_SENTINEL}); asserts "
                f"NaN-free + dg_sparse in HF band + arms_differ"
            ),
            "spokes12_placeholder": (
                "cortex encoder = char+positional + per-concept competitive "
                "Hebbian (Spoke 1 v3-D style; Spokes 1+2 hdlab extraction "
                "pending post-Spoke-1-CG + Spoke-2-CG). Will replace with "
                "hdlab.concept_encoder.CortexEncoder post-extraction."
            ),
            "cell_chunked": False,
        },
    }

    _atomic_write_metrics(output_dir, metrics)
    print(
        f"[{ANCHOR_NAME}] {verdict_bundle['verdict']} "
        f"elapsed={elapsed:.1f}s "
        f"path={output_dir / 'metrics.json'}",
        flush=True,
    )


if __name__ == "__main__":
    _output_dir_for_crash = _output_dir("smoke")
    try:
        _early = argparse.ArgumentParser(add_help=False)
        _early.add_argument("--run-mode", default="smoke",
                            choices=["self_test", "smoke", "full"])
        _early.add_argument("--self-test", action="store_true")
        _early.add_argument("--smoke", action="store_true")
        _early_args, _ = _early.parse_known_args()
        _rm = _early_args.run_mode
        if _early_args.self_test:
            _rm = "self_test"
        elif _early_args.smoke:
            _rm = "smoke"
        _output_dir_for_crash = _output_dir(_rm)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
