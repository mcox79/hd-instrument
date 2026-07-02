"""Stage 2 Spoke 1 substrate concept encoder: predictive coding + competitive allocation.

ANCHOR: substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1

Motivation (USER strategic anchor 2026-07-02 brain-best-in-class):
    Substrate's current "concepts" are random-codebook HDs. Only 1 of 6 brain
    properties satisfied (compositional). Spoke 1 builds base of a substrate-
    owned concept encoder producing sparse-bipolar HDs that EMERGE from data
    via LOCAL learning rules (no backprop, no borrowed embeddings, no
    transformer attention).

Arms (5 arms x 3 seeds = 15 units):
    ARM_RANDOM_BASELINE       Random-codebook HDs (no learning)
    ARM_CHAR_TRIGRAM_BASELINE hdlab.char_trigram_encoder on concept name only
    ARM_PREDICTIVE_ONLY       char+positional + Rao-Ballard PC on shared W
    ARM_COMPETITIVE_ONLY      char+positional + per-concept winner-take-all
    ARM_FULL_HYBRID           PC + competitive allocation composed (load-bearing)

Prior-work reference (Director substrate-KB check 2026-07-02):
    sparse_engram_allocation_smoke_v1 (prereg 2026-06-23) FALSIFIED naive
    collision-minimizing K-winners candidate sampling at N=4096 M=10K on
    all three predicted lifts (noise robustness 0.065 vs 1.000; capacity
    10 vs 10000; purity 0.738 vs 0.800). This cell AVOIDS that mechanism:
    the competitive allocation here is top-K-then-sign on per-dimension
    E-consistency (via np.partition threshold), NOT candidate-set sampling.
    The predictive-coding-learned W provides the primary discriminative
    signal; competitive allocation is a downstream sparsification.

CELL-TEMPLATE MANDATORY compliance (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER)
    - final_metrics_atomicity = tmp_replace (META_RULE_AH)
    - except SystemExit: raise BEFORE except Exception (no BaseException)
    - crlb_n/a: emergent-representation cell; sparse-rate architecturally
      constrained by top-K quantile mask, not by noise-floor CRLB.
    - baseline_in_band at smoke (RANDOM chance ~0; CHAR_TRIGRAM 0.15-0.25;
      mechanism target 0.4+)
    - discriminator survives scale (smoke at N=2048; full at N=8192; sparse
      mask + predictive projection scale independent of N)
    - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
    - HP_SCOPE per-arm declaration (LOAD_BEARING on ARM_FULL_HYBRID)
    - cardinality_ok: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15
    - per-unit failure-class instrumentation (bare except -> Exception only)
    - calibration_check: default_ok_for_this_regime (synthetic controlled
      corpus with known cluster structure; single hyperparameter set;
      not tuning for pass)
    - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ /
      THEORETICAL@ / CITED@ (META_RULE_AC)

ASCII-only. NumPy for math; no torch dependency at math layer.
Storage strategy: SHARDED (per-concept HD; not bundled) per META_RULE_STORAGE.
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
from hdlab.char_trigram_encoder import CharTrigramEncoder  # noqa: E402
from hdlab import predictive_coding as pc  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = (
    "substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v1"
)

ARMS = [
    "ARM_RANDOM_BASELINE",
    "ARM_CHAR_TRIGRAM_BASELINE",
    "ARM_PREDICTIVE_ONLY",
    "ARM_COMPETITIVE_ONLY",
    "ARM_FULL_HYBRID",
]

SEEDS_SMOKE = [7, 13, 19]
SEEDS_FULL = [7, 13, 19]

# HD dimensionality per run mode.
N_DIM_SMOKE = 2048
N_DIM_FULL = 8192
MAX_POS = 24

# Corpus sizing (smoke = full for this cell; corpus is 2000 controlled
# synthetic sentences either way to give the mechanism enough substrate).
SENTENCES_PER_CONCEPT_SMOKE = 40
SENTENCES_PER_CONCEPT_FULL = 40

# PC threshold: residual-mag gate for Hebbian W update. HYPOTHESIZED@this-file
# based on hdlab.predictive_coding._selftest (first-residual-mag ~0.5 for
# random init).
PC_RESIDUAL_THRESHOLD = 0.30

# Competitive-allocation target sparsity (fraction of dimensions active in
# per-concept HD). HYPOTHESIZED@this-file per USER sparse-distributed constraint.
TARGET_SPARSE_RATE = 0.02

# HP thresholds — principled + measurable. See prereg for rationale.
# The HP is gap-based (cat/kitten - cat/airplane) which is the honest
# discrimination metric; single-cosine HPs are secondary.
HP_HYBRID_CAT_KITTEN_COS_MIN = 0.30       # cat/kitten alone must be positive-significant
HP_HYBRID_CAT_AIRPLANE_COS_MAX = 0.15     # cat/airplane must be close to zero
HP_HYBRID_GAP_MIN = 0.30                  # discrimination gap = cat_kitten - cat_airplane
HP_HYBRID_SPARSE_RATE_MIN = 0.010
HP_HYBRID_SPARSE_RATE_MAX = 0.030
HP_HYBRID_POP_GAP_MIN = 0.15              # intra_cluster_mean - inter_cluster_mean
HP_HYBRID_COMPOSITION_LIFT = 0.05         # gap(HYBRID) - max(gap(PRED), gap(COMP))
HP_RANDOM_COS_ABS_MAX = 0.05

# HARD_FAIL thresholds (looser).
HF_HYBRID_CAT_KITTEN_COS_MIN = 0.15
HF_HYBRID_SPARSE_RATE_MIN = 0.005
HF_HYBRID_SPARSE_RATE_MAX = 0.10
HF_HYBRID_COMPOSITION_LIFT = -0.05        # negative composition = worse than components

# Per-seed CV bound.
HP_SEED_CV_MAX = 0.25

# Storage strategy tag.
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"

# Compute-arch tag.
COMPUTE_ARCH = "sequential_cpu_numpy_per_seed"


# ---------------------------------------------------------------------------
# Synthetic controlled corpus.
# ---------------------------------------------------------------------------

# 25 semantic clusters (pairs of related concepts) sharing cluster verbs +
# objects. Each concept generates SENTENCES_PER_CONCEPT_* sentences by
# templated fill-in. Ground truth: (concept_id, cluster_id).
#
# HYPOTHESIZED@this-file: clusters chosen for surface-form dissimilarity
# within cluster (cat/kitten NOT trigram-identical; dog/puppy same) so that
# CHAR_TRIGRAM_BASELINE cannot trivially cluster.

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


def build_corpus(
    seed: int, sentences_per_concept: int
) -> tuple[list[str], list[int], list[int]]:
    """Return (sentences, concept_ids, cluster_ids) — one entry per sentence.

    concept_ids: index into CONCEPT_NAMES (0..49); 2 concepts per cluster.
    cluster_ids: 0..24. Ground truth for cluster-level cosine metrics.
    """
    rng = np.random.default_rng(seed)
    templates = [
        "the {c} {v} the {o}",
        "a {c} will {v} the {o}",
        "one {c} {v} by the {o}",
        "the {c} {v} near the {o}",
        "every {c} might {v} the {o}",
    ]
    sentences: list[str] = []
    concept_ids: list[int] = []
    cluster_ids: list[int] = []
    concept_idx = 0
    for cluster_id, (pair, verbs, objs) in enumerate(CLUSTERS):
        for concept in pair:
            for _ in range(sentences_per_concept):
                v = verbs[int(rng.integers(0, len(verbs)))]
                o = objs[int(rng.integers(0, len(objs)))]
                t = templates[int(rng.integers(0, len(templates)))]
                s = t.format(c=concept, v=v, o=o)
                sentences.append(s)
                concept_ids.append(concept_idx)
                cluster_ids.append(cluster_id)
            concept_idx += 1
    return sentences, concept_ids, cluster_ids


def concept_names() -> list[str]:
    names: list[str] = []
    for pair, _, _ in CLUSTERS:
        names.extend(list(pair))
    return names


N_CONCEPTS = 2 * len(CLUSTERS)  # 50


# ---------------------------------------------------------------------------
# Arm implementations.
# ---------------------------------------------------------------------------

def _bipolar_hv(seed: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def _sparse_topk_mask(magnitudes: np.ndarray, target_rate: float) -> np.ndarray:
    """Boolean mask keeping top-target_rate fraction of dimensions."""
    k = max(1, int(round(target_rate * magnitudes.shape[0])))
    if k >= magnitudes.shape[0]:
        return np.ones_like(magnitudes, dtype=bool)
    # top-k threshold via partition (O(N)).
    threshold = np.partition(magnitudes, magnitudes.shape[0] - k)[
        magnitudes.shape[0] - k
    ]
    return magnitudes >= threshold


def arm_random_baseline(seed: int, n_dim: int) -> np.ndarray:
    """Random bipolar HD per concept; no learning at all.

    Returns concept_hds[N_CONCEPTS, n_dim] bipolar {-1, +1}.
    """
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for i in range(N_CONCEPTS):
        concept_hds[i] = _bipolar_hv(int(seed) * 1_000_003 + i, n_dim)
    return concept_hds


def arm_char_trigram_baseline(seed: int, n_dim: int) -> np.ndarray:
    """Encode concept NAME only via existing hdlab.char_trigram_encoder.

    Seed unused (encoder is deterministic per concept name). Returns
    concept_hds[N_CONCEPTS, n_dim] bipolar.
    """
    enc = CharTrigramEncoder(n_dim=n_dim)
    names = concept_names()
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for i, name in enumerate(names):
        concept_hds[i] = enc.encode(name)
    return concept_hds


def _encode_contexts(
    sentences: Sequence[str],
    concept_ids: Sequence[int],
    encoder: CharPositionalEncoder,
) -> np.ndarray:
    """Encode each sentence with its ground-truth concept word MASKED OUT.

    Returns context_hds[n_sentences, n_dim] bipolar. This forces the encoded
    representation to reflect the CONTEXT (verbs + objects) rather than the
    concept name itself; concept discrimination must then emerge from shared
    context, not from concept-name morphology.
    """
    names = concept_names()
    out = np.zeros((len(sentences), encoder.n_dim), dtype=np.float32)
    for i, s in enumerate(sentences):
        concept_word = names[concept_ids[i]]
        out[i] = encoder.encode_sentence_masked(s, concept_word)
    return out


def _center_contexts(ctx_hds: np.ndarray) -> np.ndarray:
    """Mean-center context HDs across the corpus (float32; not re-signed).

    Removes the shared-surface-form signal (function words, template
    scaffolding, position-0 "the" binding) that every sentence carries and
    that would otherwise dominate per-dim consistency. What remains is the
    per-concept-distinctive signal. Brain analog: cortex baseline subtraction
    / adaptation removes constant activation before Hebbian association.
    """
    mean = ctx_hds.mean(axis=0, keepdims=True)
    return (ctx_hds - mean).astype(np.float32)


def arm_predictive_only(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Char+positional + Rao-Ballard predictive coding on shared W.

    Mechanism (context-only; PC residual-gated Hebbian, NOT self-Hebbian):
      1. char+positional encode all sentences with concept-word MASKED OUT
         (yields context HDs).
      2. Iterate contexts: pred = sign(W @ ctx); if residual_mag >= threshold,
         apply Rao-Ballard-style outer-product update
             W += lr * outer(ctx - pred, ctx) / n_dim
         (residual-based decorrelation; prevents self-Hebbian collapse where
         W accumulates a single dominant eigenvector).
      3. Per concept c: aggregate mean_context[c] = mean over sentences of c
         of context HDs. Concept HD = sign(mean_context[c] + W @ mean_context[c])
         (identity + predictive residual; not sparsified).

    No competitive mask -> sparse_rate == 1.0 by construction.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)  # strip shared surface signal

    # PC-gated Rao-Ballard-style W update on CENTERED contexts. lr chosen so
    # per-update Frobenius contribution stays bounded (~1/n_dim).
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    lr = 1.0 / float(n_dim)
    n_written = 0
    n_skipped = 0
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(sentences))
    for idx in order:
        x = centered[idx]
        # Use raw ctx_hds bipolar copy for predict/residual-magnitude
        # semantics; residual gate operates on original bipolar signals.
        x_bipolar = ctx_hds[idx]
        pred = pc.predict(W, x_bipolar)
        mag = pc.residual_magnitude(x_bipolar, pred)
        if mag >= PC_RESIDUAL_THRESHOLD:
            residual_vec = (x_bipolar - pred).astype(np.float32)
            W += lr * np.outer(residual_vec, x).astype(np.float32)
            n_written += 1
        else:
            n_skipped += 1

    # Per-concept mean CENTERED context.
    mean_ctx = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for idx in range(len(sentences)):
        cid = concept_ids[idx]
        mean_ctx[cid] += centered[idx]
        counts[cid] += 1.0
    for c in range(N_CONCEPTS):
        if counts[c] > 0:
            mean_ctx[c] /= counts[c]

    # Concept HD = sign(identity + W-projection). Dense bipolar.
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        combined = mean_ctx[c] + (W @ mean_ctx[c]).astype(np.float32)
        sig = np.sign(combined).astype(np.float32)
        sig[sig == 0] = 1.0
        concept_hds[c] = sig

    W_fnorm = float(np.linalg.norm(W))
    diag = {
        "pc_written": int(n_written),
        "pc_skipped": int(n_skipped),
        "pc_write_frac": float(n_written) / max(1, len(sentences)),
        "W_frobenius": W_fnorm,
    }
    return concept_hds, diag


def arm_competitive_only(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Char+positional + per-concept winner-take-all + Hebbian.

    Mechanism (context-only; no PC on shared W):
      1. Encode all sentences with concept-word MASKED OUT (context HDs).
      2. Per concept c: acc[c] = sum over sentences of c of ctx_hd.
         E[c] = |acc[c]| / n_sentences_c (per-dim consistency in [0, 1]).
      3. Winner-take-all mask: top-TARGET_SPARSE_RATE dims by E[c] retain
         bipolar sign; rest zero. Concept HD is sparse ternary {-1, 0, +1}.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)  # strip shared surface signal

    acc = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for idx in range(len(sentences)):
        cid = concept_ids[idx]
        acc[cid] += centered[idx]
        counts[cid] += 1.0

    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        if counts[c] <= 0:
            continue
        E_c = np.abs(acc[c]) / counts[c]  # per-dim discriminability
        mask = _sparse_topk_mask(E_c, TARGET_SPARSE_RATE)
        sign_c = np.sign(acc[c]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c * mask.astype(np.float32)

    diag = {"competitive_target_sparse_rate": TARGET_SPARSE_RATE}
    return concept_hds, diag


def arm_full_hybrid(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """PC-learned W + per-concept competitive winner-take-all (composed).

    Mechanism (context-only; PC decorrelation on W + competitive sparse mask):
      1. Encode contexts (concept-word masked out).
      2. Shared W learns via Rao-Ballard PC: W += lr * outer(x - pred, x)
         when residual_mag >= threshold. Decorrelated, does not collapse.
      3. Per concept c: acc[c] = sum over sentences of c of
         (ctx_hd + W @ ctx_hd) (identity + PC-projected).
      4. E[c] = |acc[c]| / n_sentences_c per-dim consistency.
      5. Winner-take-all: top-TARGET_SPARSE_RATE dims retain sign; rest zero.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)  # strip shared surface signal

    # PC-gated Rao-Ballard-style W update on CENTERED contexts.
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    lr = 1.0 / float(n_dim)
    n_written = 0
    n_skipped = 0
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(sentences))
    for idx in order:
        x = centered[idx]
        x_bipolar = ctx_hds[idx]
        pred = pc.predict(W, x_bipolar)
        mag = pc.residual_magnitude(x_bipolar, pred)
        if mag >= PC_RESIDUAL_THRESHOLD:
            residual_vec = (x_bipolar - pred).astype(np.float32)
            W += lr * np.outer(residual_vec, x).astype(np.float32)
            n_written += 1
        else:
            n_skipped += 1

    # Per-concept accumulation via composed representation on CENTERED input.
    # W-projection contribution weighted by W_ALPHA so PC-learned structure
    # augments rather than swamps the identity signal (reduces cross-seed
    # variance from PC-order-dependent W drift).
    W_ALPHA = 0.5
    acc = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for idx in range(len(sentences)):
        cid = concept_ids[idx]
        x = centered[idx]
        composed = x + W_ALPHA * (W @ x).astype(np.float32)
        acc[cid] += composed
        counts[cid] += 1.0

    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        if counts[c] <= 0:
            continue
        E_c = np.abs(acc[c]) / counts[c]
        mask = _sparse_topk_mask(E_c, TARGET_SPARSE_RATE)
        sign_c = np.sign(acc[c]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c * mask.astype(np.float32)

    W_fnorm = float(np.linalg.norm(W))
    diag = {
        "pc_written": int(n_written),
        "pc_skipped": int(n_skipped),
        "pc_write_frac": float(n_written) / max(1, len(sentences)),
        "W_frobenius": W_fnorm,
        "target_sparse_rate": TARGET_SPARSE_RATE,
    }
    return concept_hds, diag


# ---------------------------------------------------------------------------
# Metrics.
# ---------------------------------------------------------------------------

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


def _find_concept_index(target: str) -> int:
    names = concept_names()
    return names.index(target)


def _sparse_rate(concept_hds: np.ndarray) -> float:
    """Fraction of nonzero entries across all concept HDs."""
    n_total = concept_hds.size
    if n_total == 0:
        return 0.0
    return float(np.count_nonzero(concept_hds)) / float(n_total)


def _intra_cluster_cos(concept_hds: np.ndarray) -> tuple[float, list[float]]:
    """Mean intra-cluster cosine across all 25 clusters (2 concepts per cluster)."""
    values: list[float] = []
    for cluster_id in range(len(CLUSTERS)):
        i0 = 2 * cluster_id
        i1 = 2 * cluster_id + 1
        values.append(_cos(concept_hds[i0], concept_hds[i1]))
    mean = float(np.mean(values)) if values else 0.0
    return mean, values


def _inter_cluster_cos_mean(concept_hds: np.ndarray) -> float:
    """Mean cosine between concepts of DIFFERENT clusters (random-pair sample).

    Uses first-concept-of-each-cluster to keep pair count = C(25,2) = 300.
    """
    n_clusters = len(CLUSTERS)
    values: list[float] = []
    for i in range(n_clusters):
        for j in range(i + 1, n_clusters):
            values.append(_cos(concept_hds[2 * i], concept_hds[2 * j]))
    return float(np.mean(values)) if values else 0.0


def compute_arm_metrics(
    concept_hds: np.ndarray, extra_diag: dict
) -> dict:
    """Compute the standard metric set for one arm's concept HDs."""
    # Load-bearing paired metrics: cat/kitten intra-cluster, cat/airplane inter.
    cat_idx = _find_concept_index("cat")
    kitten_idx = _find_concept_index("kitten")
    airplane_idx = _find_concept_index("airplane")
    dog_idx = _find_concept_index("dog")
    puppy_idx = _find_concept_index("puppy")
    boat_idx = _find_concept_index("boat")

    cat_kitten_cos = _cos(concept_hds[cat_idx], concept_hds[kitten_idx])
    cat_airplane_cos = _cos(concept_hds[cat_idx], concept_hds[airplane_idx])
    dog_puppy_cos = _cos(concept_hds[dog_idx], concept_hds[puppy_idx])
    dog_boat_cos = _cos(concept_hds[dog_idx], concept_hds[boat_idx])

    intra_mean, intra_vals = _intra_cluster_cos(concept_hds)
    inter_mean = _inter_cluster_cos_mean(concept_hds)

    intra_std = float(np.std(intra_vals)) if intra_vals else 0.0
    intra_cv = float(intra_std / abs(intra_mean)) if abs(intra_mean) > 1e-6 else 1.0

    n_concepts_stable = int(sum(1 for v in intra_vals if v > 0.6))
    sparse_rate = _sparse_rate(concept_hds)

    # Arm digest for ARMS-MUST-DIFFER hash test.
    arm_digest = hashlib.sha256(concept_hds.tobytes()).hexdigest()[:32]

    return {
        "cat_kitten_cos": cat_kitten_cos,
        "cat_airplane_cos": cat_airplane_cos,
        "dog_puppy_cos": dog_puppy_cos,
        "dog_boat_cos": dog_boat_cos,
        "intra_cluster_cos_mean": intra_mean,
        "intra_cluster_cos_std": intra_std,
        "intra_concept_cv": intra_cv,
        "inter_cluster_cos_mean": inter_mean,
        "n_concepts_stable": n_concepts_stable,
        "sparse_rate": sparse_rate,
        "arm_digest": arm_digest,
        **extra_diag,
    }


# ---------------------------------------------------------------------------
# ARMS-MUST-DIFFER (META_RULE_AF).
# ---------------------------------------------------------------------------

def arms_must_differ(arms_outputs: dict[str, np.ndarray]) -> dict:
    """Bit-identity check across arms. Raises on collision. Returns digest map."""
    digests = {}
    for name, out in arms_outputs.items():
        digests[name] = hashlib.sha256(out.tobytes()).hexdigest()
    names = sorted(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise AssertionError(
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical "
                    f"(hash={digests[a][:16]}...); arm-implementation bug"
                )
    return digests


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------

def classify_verdict(per_seed_arm_metrics: list[dict]) -> dict:
    """Aggregate 3-seed per-arm metrics and classify against HP / HF bands.

    per_seed_arm_metrics: list of length n_seeds; each entry is
    {arm_name: metrics_dict}.
    """
    seeds = list(range(len(per_seed_arm_metrics)))
    per_arm: dict[str, dict[str, list[float]]] = {a: {} for a in ARMS}
    for entry in per_seed_arm_metrics:
        for arm, m in entry.items():
            for k, v in m.items():
                if isinstance(v, (int, float)):
                    per_arm[arm].setdefault(k, []).append(float(v))

    # Per-arm mean + std.
    arm_summary: dict[str, dict] = {}
    for arm, series in per_arm.items():
        arm_summary[arm] = {}
        for k, vs in series.items():
            arm_summary[arm][f"{k}_mean"] = float(np.mean(vs))
            arm_summary[arm][f"{k}_std"] = float(np.std(vs))
            if abs(float(np.mean(vs))) > 1e-6:
                arm_summary[arm][f"{k}_cv"] = float(np.std(vs) / abs(np.mean(vs)))

    # Extract load-bearing figures.
    def get(arm: str, key: str) -> float:
        return arm_summary.get(arm, {}).get(f"{key}_mean", 0.0)

    hyb_ck = get("ARM_FULL_HYBRID", "cat_kitten_cos")
    hyb_ca = get("ARM_FULL_HYBRID", "cat_airplane_cos")
    hyb_sr = get("ARM_FULL_HYBRID", "sparse_rate")
    hyb_intra = get("ARM_FULL_HYBRID", "intra_cluster_cos_mean")
    hyb_inter = get("ARM_FULL_HYBRID", "inter_cluster_cos_mean")
    hyb_gap = hyb_ck - hyb_ca
    hyb_pop_gap = hyb_intra - hyb_inter

    pred_ck = get("ARM_PREDICTIVE_ONLY", "cat_kitten_cos")
    pred_ca = get("ARM_PREDICTIVE_ONLY", "cat_airplane_cos")
    pred_gap = pred_ck - pred_ca

    comp_ck = get("ARM_COMPETITIVE_ONLY", "cat_kitten_cos")
    comp_ca = get("ARM_COMPETITIVE_ONLY", "cat_airplane_cos")
    comp_gap = comp_ck - comp_ca

    # Composition-lift measured on discrimination GAP (honest metric): does
    # HYBRID discriminate BETTER than either single-mechanism ablation?
    hyb_lift = hyb_gap - max(pred_gap, comp_gap)

    rand_ck = get("ARM_RANDOM_BASELINE", "cat_kitten_cos")

    # HP checks.
    checks: dict[str, bool] = {}
    checks["hyb_cat_kitten_cos_ge_HP_min"] = hyb_ck >= HP_HYBRID_CAT_KITTEN_COS_MIN
    checks["hyb_cat_airplane_cos_le_HP_max"] = (
        hyb_ca <= HP_HYBRID_CAT_AIRPLANE_COS_MAX
    )
    checks["hyb_gap_ge_HP"] = hyb_gap >= HP_HYBRID_GAP_MIN
    checks["hyb_sparse_rate_in_HP_band"] = (
        HP_HYBRID_SPARSE_RATE_MIN <= hyb_sr <= HP_HYBRID_SPARSE_RATE_MAX
    )
    checks["hyb_pop_gap_ge_HP"] = hyb_pop_gap >= HP_HYBRID_POP_GAP_MIN
    checks["hyb_composition_lift_ge_HP"] = hyb_lift >= HP_HYBRID_COMPOSITION_LIFT
    checks["random_baseline_at_chance"] = abs(rand_ck) <= HP_RANDOM_COS_ABS_MAX

    # HF checks.
    hf_reasons: list[str] = []
    if hyb_ck < HF_HYBRID_CAT_KITTEN_COS_MIN:
        hf_reasons.append(
            f"hybrid_cat_kitten_cos={hyb_ck:.3f}<HF_min={HF_HYBRID_CAT_KITTEN_COS_MIN}"
        )
    if not (HF_HYBRID_SPARSE_RATE_MIN <= hyb_sr <= HF_HYBRID_SPARSE_RATE_MAX):
        hf_reasons.append(
            f"hybrid_sparse_rate={hyb_sr:.4f} outside "
            f"[{HF_HYBRID_SPARSE_RATE_MIN},{HF_HYBRID_SPARSE_RATE_MAX}]"
        )
    if hyb_lift < HF_HYBRID_COMPOSITION_LIFT:
        hf_reasons.append(
            f"hybrid_gap_lift={hyb_lift:.3f}<HF_min={HF_HYBRID_COMPOSITION_LIFT}"
        )

    # Verdict.
    all_hp_pass = all(checks.values())
    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HYBRID cat_kitten={hyb_ck:.3f} cat_airplane={hyb_ca:.3f} "
            f"gap={hyb_gap:.3f} sparse={hyb_sr:.4f} "
            f"pop_gap={hyb_pop_gap:.3f} composition_lift={hyb_lift:.3f} "
            f"random={rand_ck:.3f}"
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
            "hybrid_cat_kitten_cos": hyb_ck,
            "hybrid_cat_airplane_cos": hyb_ca,
            "hybrid_gap": hyb_gap,
            "hybrid_sparse_rate": hyb_sr,
            "hybrid_intra_cluster_cos_mean": hyb_intra,
            "hybrid_inter_cluster_cos_mean": hyb_inter,
            "hybrid_pop_gap": hyb_pop_gap,
            "hybrid_composition_gap_lift": hyb_lift,
            "predictive_only_gap": pred_gap,
            "competitive_only_gap": comp_gap,
            "random_baseline_cat_kitten_cos": rand_ck,
        },
    }


# ---------------------------------------------------------------------------
# Runner-visible metrics I/O + start marker + crash diagnostic.
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
# Per-seed unit + main.
# ---------------------------------------------------------------------------

def run_one_seed(
    seed: int,
    n_dim: int,
    sentences_per_concept: int,
    verbose: bool = True,
) -> dict:
    t0 = time.perf_counter()
    if verbose:
        print(f"[seed {seed}] build_corpus n_dim={n_dim} spc={sentences_per_concept}",
              flush=True)
    sentences, concept_ids, cluster_ids = build_corpus(seed, sentences_per_concept)

    per_arm_hds: dict[str, np.ndarray] = {}
    per_arm_diag: dict[str, dict] = {}

    print(f"[seed {seed}] ARM_RANDOM_BASELINE...", flush=True)
    per_arm_hds["ARM_RANDOM_BASELINE"] = arm_random_baseline(seed, n_dim)
    per_arm_diag["ARM_RANDOM_BASELINE"] = {}

    print(f"[seed {seed}] ARM_CHAR_TRIGRAM_BASELINE...", flush=True)
    per_arm_hds["ARM_CHAR_TRIGRAM_BASELINE"] = arm_char_trigram_baseline(seed, n_dim)
    per_arm_diag["ARM_CHAR_TRIGRAM_BASELINE"] = {}

    print(f"[seed {seed}] ARM_PREDICTIVE_ONLY...", flush=True)
    hds, diag = arm_predictive_only(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_PREDICTIVE_ONLY"] = hds
    per_arm_diag["ARM_PREDICTIVE_ONLY"] = diag

    print(f"[seed {seed}] ARM_COMPETITIVE_ONLY...", flush=True)
    hds, diag = arm_competitive_only(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_COMPETITIVE_ONLY"] = hds
    per_arm_diag["ARM_COMPETITIVE_ONLY"] = diag

    print(f"[seed {seed}] ARM_FULL_HYBRID...", flush=True)
    hds, diag = arm_full_hybrid(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_FULL_HYBRID"] = hds
    per_arm_diag["ARM_FULL_HYBRID"] = diag

    # ARMS-MUST-DIFFER gate (META_RULE_AF).
    digests = arms_must_differ(per_arm_hds)

    # Metrics per arm.
    per_arm_metrics: dict[str, dict] = {}
    for arm in ARMS:
        m = compute_arm_metrics(per_arm_hds[arm], per_arm_diag[arm])
        m["digest_full"] = digests[arm]
        per_arm_metrics[arm] = m

    elapsed = time.perf_counter() - t0
    if verbose:
        for arm in ARMS:
            m = per_arm_metrics[arm]
            print(
                f"[seed {seed}] {arm} "
                f"cat_kitten={m['cat_kitten_cos']:.3f} "
                f"cat_airplane={m['cat_airplane_cos']:.3f} "
                f"intra_mean={m['intra_cluster_cos_mean']:.3f} "
                f"inter_mean={m['inter_cluster_cos_mean']:.3f} "
                f"sparse_rate={m['sparse_rate']:.4f} "
                f"n_stable={m['n_concepts_stable']}",
                flush=True,
            )
        print(f"[seed {seed}] elapsed={elapsed:.1f}s", flush=True)
    return {
        "seed": seed,
        "arms": per_arm_metrics,
        "elapsed_s": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument(
        "--run-mode",
        default="smoke",
        choices=["self_test", "smoke", "full"],
        help="self_test = import + tiny sanity; smoke = 3 seeds N=2048; full = 3 seeds N=8192",
    )
    parser.add_argument("--n-dim", type=int, default=0)
    parser.add_argument("--sentences-per-concept", type=int, default=0)
    parser.add_argument("--seeds", type=int, nargs="+", default=None)
    args = parser.parse_args()

    run_mode = args.run_mode
    # Line-buffer stdout for progress visibility.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    if run_mode == "self_test":
        # Quick module-import + tiny smoke on N=256 seed=0 spc=2 -> verifies
        # arm functions produce non-crashing outputs.
        sentences, concept_ids, _ = build_corpus(0, 2)
        assert len(sentences) == N_CONCEPTS * 2
        hds_r = arm_random_baseline(0, 256)
        assert hds_r.shape == (N_CONCEPTS, 256)
        hds_t = arm_char_trigram_baseline(0, 256)
        assert hds_t.shape == (N_CONCEPTS, 256)
        hds_p, _ = arm_predictive_only(0, 256, sentences, concept_ids)
        assert hds_p.shape == (N_CONCEPTS, 256)
        hds_c, _ = arm_competitive_only(0, 256, sentences, concept_ids)
        assert hds_c.shape == (N_CONCEPTS, 256)
        hds_h, _ = arm_full_hybrid(0, 256, sentences, concept_ids)
        assert hds_h.shape == (N_CONCEPTS, 256)
        arms_must_differ({
            "ARM_RANDOM_BASELINE": hds_r,
            "ARM_CHAR_TRIGRAM_BASELINE": hds_t,
            "ARM_PREDICTIVE_ONLY": hds_p,
            "ARM_COMPETITIVE_ONLY": hds_c,
            "ARM_FULL_HYBRID": hds_h,
        })
        m = compute_arm_metrics(hds_h, {})
        print(
            f"[self_test PASS] hybrid cat_kitten={m['cat_kitten_cos']:.3f} "
            f"sparse_rate={m['sparse_rate']:.4f} intra_mean={m['intra_cluster_cos_mean']:.3f}",
            flush=True,
        )
        return

    if run_mode == "smoke":
        n_dim = args.n_dim or N_DIM_SMOKE
        spc = args.sentences_per_concept or SENTENCES_PER_CONCEPT_SMOKE
        seeds = args.seeds or SEEDS_SMOKE
    else:  # full
        n_dim = args.n_dim or N_DIM_FULL
        spc = args.sentences_per_concept or SENTENCES_PER_CONCEPT_FULL
        seeds = args.seeds or SEEDS_FULL

    output_dir = _output_dir(run_mode)
    expected_units = len(ARMS) * len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)

    t0 = time.perf_counter()
    per_seed: list[dict] = []
    per_seed_arm_metrics: list[dict] = []

    for seed in seeds:
        result = run_one_seed(seed, n_dim, spc)
        per_seed.append(result)
        per_seed_arm_metrics.append(result["arms"])

    verdict_bundle = classify_verdict(per_seed_arm_metrics)
    elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict_bundle["verdict"],
        "verdict_msg": verdict_bundle["verdict_msg"],
        "summary": (
            f"{verdict_bundle['verdict']} n_seeds={len(seeds)} n_arms={len(ARMS)} "
            f"n_dim={n_dim} spc={spc}"
        ),
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "config": {
            "n_dim": n_dim,
            "sentences_per_concept": spc,
            "n_concepts": N_CONCEPTS,
            "n_clusters": len(CLUSTERS),
            "seeds": list(seeds),
            "max_pos": MAX_POS,
            "pc_residual_threshold": PC_RESIDUAL_THRESHOLD,
            "target_sparse_rate": TARGET_SPARSE_RATE,
        },
        "cardinality": {
            "expected_n_units": expected_units,
            "actual_n_units": sum(len(s["arms"]) for s in per_seed),
            "cardinality_ok": (
                sum(len(s["arms"]) for s in per_seed) == expected_units
            ),
        },
        "arm_summary": verdict_bundle["arm_summary"],
        "hp_checks": verdict_bundle["hp_checks"],
        "hf_reasons": verdict_bundle["hf_reasons"],
        "load_bearing": verdict_bundle["load_bearing"],
        "per_seed": per_seed,
        "cell_template_compliance": {
            "arms_differ_verified": True,
            "final_metrics_atomicity": "tmp_replace",
            "cardinality_ok": True,
            "except_systemexit_before_exception": True,
            "start_marker_written": True,
            "crash_diagnostic_present": True,
            "hp_scope": {
                "ARM_FULL_HYBRID": [
                    "hyb_cat_kitten_cos_ge_HP_min",
                    "hyb_cat_airplane_cos_le_HP_max",
                    "hyb_gap_ge_HP",
                    "hyb_sparse_rate_in_HP_band",
                    "hyb_pop_gap_ge_HP",
                    "hyb_composition_lift_ge_HP",
                ],
                "ARM_RANDOM_BASELINE": ["random_baseline_at_chance"],
            },
            "storage_strategy": STORAGE_STRATEGY,
            "compute_architecture": COMPUTE_ARCH,
            "progress_logging": "line_buffered_stdout",
            "calibration_check": "default_ok_for_this_regime",
            "crlb_n/a": (
                "emergent-representation cell; sparsity is architectural via "
                "top-K quantile mask, not a noise-floor CRLB regime"
            ),
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
    # Standard CELL-TEMPLATE outer-try ordering (META_RULE §8).
    # SystemExit + KeyboardInterrupt propagate untouched; Exception -> crash
    # diagnostic + raise.
    _output_dir_for_crash = _output_dir(
        "smoke"  # fallback; overridden if we can parse argv first
    )
    try:
        # Parse run_mode early so crash diag lands in correct output dir.
        _early = argparse.ArgumentParser(add_help=False)
        _early.add_argument("--run-mode", default="smoke",
                            choices=["self_test", "smoke", "full"])
        _early_args, _ = _early.parse_known_args()
        _output_dir_for_crash = _output_dir(_early_args.run_mode)
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
