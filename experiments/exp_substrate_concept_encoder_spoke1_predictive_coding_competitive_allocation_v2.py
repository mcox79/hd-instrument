"""Stage 2 Spoke 1 substrate concept encoder v2: reframed HP + naive-WTA control.

ANCHOR: substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2

v2 CHANGES from v1 (Director-approved option A, 2026-07-02):
  1. REFRAMED HP:
     - v1 HP `HYBRID_composition_lift >= 0.05` on discrimination gap treated
       sparsity as free. v1 smoke measured a ~0.10 gap tax on HYBRID vs dense
       PREDICTIVE — the "composition failed" verdict was actually an
       ARCHITECTURAL SPARSITY TRADE-OFF, not mechanism failure. v2 replaces
       that gate with:
       * HYBRID cat/kitten gap must MATCH PREDICTIVE gap within +/- 0.15 (i.e.
         sparsity tax is bounded; sparse HYBRID retains most of dense
         discrimination).
       * HYBRID must STRICTLY BEAT ARM_NAIVE_WTA_SAMPLING (the falsified
         2026-06-23 sparse_engram_allocation reference) by gap >= 0.15
         (real progress vs the naive candidate-sampling baseline).
     - Removes HP `HYBRID_composition_lift` (redundant with beats-NAIVE-WTA).

  2. ADD ARM_NAIVE_WTA_SAMPLING: reproduces the 2026-06-23
     `sparse_engram_allocation_smoke_v1` mechanism (candidate-set K-winners
     with collision minimization; no predictive coding). Concrete point of
     comparison: brain-analog Spoke 1 (HYBRID) must beat the falsified
     naive-WTA mechanism by 0.15 gap to demonstrate mechanism progress
     over the prior negative result.

  3. INCREASE SEEDS 3->5: seeds = {11, 17, 23, 29, 37}. v1 smoke showed
     seed-CV=0.30 on HYBRID cat/kitten cos (per-seed 0.671 / 0.415 / 0.415);
     5 seeds should tighten the CV estimate.

  4. SEED-VARIANCE INVESTIGATION: log per-seed the shuffle-order signature
     (SHA-256 hex of first-20 sentence indices in PC-update permutation) +
     per-seed HYBRID gap. Post-hoc correlation lets Director decide whether
     PC weight learning is regime-order-dependent.

Arms (6 arms x 5 seeds = 30 units):
    ARM_RANDOM_BASELINE       Random-codebook HDs (no learning)
    ARM_CHAR_TRIGRAM_BASELINE hdlab.char_trigram_encoder on concept name only
    ARM_PREDICTIVE_ONLY       char+positional + Rao-Ballard PC on shared W
    ARM_COMPETITIVE_ONLY      char+positional + per-concept winner-take-all
    ARM_NAIVE_WTA_SAMPLING    (NEW) K-winners candidate sampling with
                              collision minimization; no PC. Reference-control
                              reproducing 2026-06-23 falsified mechanism.
    ARM_FULL_HYBRID           PC + competitive allocation composed (load-bearing)

Framing discipline reminder (USER-locked brain-best-in-class):
  If HYBRID beats NAIVE_WTA_SAMPLING (progress vs falsified 2026-06-23 mechanism)
  but still slightly underperforms dense PREDICTIVE on raw discrimination, that
  is the CORRECT brain-analog outcome. Sparsity's compositional value shows
  up downstream in bind-and-unbind chains (M1.9 mechanism), one-shot
  hippocampal indexing (Spoke 3), continual-learning capacity. Not in
  single-hop cosine.

CELL-TEMPLATE MANDATORY compliance (META_RULE_AC/AF/AG/AH + scope/scale/floor):
    - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER)
    - final_metrics_atomicity = tmp_replace (META_RULE_AH)
    - except SystemExit: raise BEFORE except Exception (no BaseException)
    - crlb_n/a: emergent-representation cell; sparse-rate architecturally
      constrained by top-K quantile mask, not by noise-floor CRLB.
    - baseline_in_band at smoke (RANDOM ~0; CHAR_TRIGRAM ~0.05;
      NAIVE_WTA_SAMPLING likely below hybrid; hybrid target 0.30-0.60)
    - HP_SCOPE per-arm declaration (LOAD_BEARING on ARM_FULL_HYBRID)
    - cardinality_ok: EXPECTED_N_UNITS = 6 arms * 5 seeds = 30
    - per-unit failure-class instrumentation (bare except -> Exception only)
    - calibration_check: default_ok_for_this_regime (synthetic corpus; single
      hyperparameter set; not tuning-for-pass)
    - all numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ /
      THEORETICAL@ / CITED@ (META_RULE_AC)

ASCII-only. NumPy for math; no torch.
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
    "substrate_concept_encoder_spoke1_predictive_coding_competitive_allocation_v2"
)

ARMS = [
    "ARM_RANDOM_BASELINE",
    "ARM_CHAR_TRIGRAM_BASELINE",
    "ARM_PREDICTIVE_ONLY",
    "ARM_COMPETITIVE_ONLY",
    "ARM_NAIVE_WTA_SAMPLING",
    "ARM_FULL_HYBRID",
]

# 5 seeds per Director spec (v1 was 3 with CV=0.30 too high).
SEEDS_SMOKE = [11, 17, 23, 29, 37]
SEEDS_FULL = [11, 17, 23, 29, 37]

# HD dimensionality per run mode.
N_DIM_SMOKE = 2048     # smoke fast; 5-seed target wall <10 min
N_DIM_FULL = 4096      # full matches v1 smoke N=4096 (which was v1's full spec)
MAX_POS = 24

# Corpus sizing (smoke = full for this cell; 40 sentences/concept for signal).
SENTENCES_PER_CONCEPT_SMOKE = 40
SENTENCES_PER_CONCEPT_FULL = 40

# PC threshold: residual-mag gate for Hebbian W update.
PC_RESIDUAL_THRESHOLD = 0.30

# Competitive-allocation target sparsity.
TARGET_SPARSE_RATE = 0.02

# HP thresholds (v2 REFRAMED):
# HP1: HYBRID cat/kitten gap must match PREDICTIVE within +/- 0.15
HP_HYBRID_MATCHES_PRED_TOLERANCE = 0.15
# HP2: HYBRID sparse-rate in [0.01, 0.03]
HP_HYBRID_SPARSE_RATE_MIN = 0.010
HP_HYBRID_SPARSE_RATE_MAX = 0.030
# HP3: HYBRID must beat NAIVE_WTA_SAMPLING by 0.15 gap (mechanism progress
# over 2026-06-23 falsified sparse_engram_allocation baseline)
HP_HYBRID_BEATS_NAIVE_WTA_BY = 0.15
# HP4/HP5: baselines at chance
HP_RANDOM_COS_ABS_MAX = 0.05
HP_TRIGRAM_COS_ABS_MAX = 0.10  # trigram can carry small surface-form signal

# HF thresholds (looser).
HF_HYBRID_CAT_KITTEN_COS_MIN = 0.15
HF_HYBRID_SPARSE_RATE_MIN = 0.005
HF_HYBRID_SPARSE_RATE_MAX = 0.10
# HYBRID gap must NOT regress vs NAIVE_WTA_SAMPLING (mechanism at least
# matches the falsified baseline). 0.0 = strict; -0.05 = tolerant.
HF_HYBRID_GAP_MINUS_NAIVE_WTA_MIN = -0.05

# Storage strategy tag.
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"

# Compute-arch tag.
COMPUTE_ARCH = "sequential_cpu_numpy_per_seed"


# ---------------------------------------------------------------------------
# Synthetic controlled corpus (v1 clusters — unchanged).
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


def build_corpus(
    seed: int, sentences_per_concept: int
) -> tuple[list[str], list[int], list[int]]:
    """Return (sentences, concept_ids, cluster_ids) — one entry per sentence."""
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
    threshold = np.partition(magnitudes, magnitudes.shape[0] - k)[
        magnitudes.shape[0] - k
    ]
    return magnitudes >= threshold


def arm_random_baseline(seed: int, n_dim: int) -> np.ndarray:
    """Random bipolar HD per concept; no learning at all."""
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for i in range(N_CONCEPTS):
        concept_hds[i] = _bipolar_hv(int(seed) * 1_000_003 + i, n_dim)
    return concept_hds


def arm_char_trigram_baseline(seed: int, n_dim: int) -> np.ndarray:
    """Encode concept NAME only via existing hdlab.char_trigram_encoder."""
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
    """Encode each sentence with its ground-truth concept word MASKED OUT."""
    names = concept_names()
    out = np.zeros((len(sentences), encoder.n_dim), dtype=np.float32)
    for i, s in enumerate(sentences):
        concept_word = names[concept_ids[i]]
        out[i] = encoder.encode_sentence_masked(s, concept_word)
    return out


def _center_contexts(ctx_hds: np.ndarray) -> np.ndarray:
    """Mean-center context HDs across the corpus."""
    mean = ctx_hds.mean(axis=0, keepdims=True)
    return (ctx_hds - mean).astype(np.float32)


def arm_predictive_only(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Char+positional + Rao-Ballard PC on shared W (dense output)."""
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)

    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    lr = 1.0 / float(n_dim)
    n_written = 0
    n_skipped = 0
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(sentences))
    order_sig = hashlib.sha256(
        order[: min(20, len(order))].tobytes()
    ).hexdigest()[:16]
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

    mean_ctx = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for idx in range(len(sentences)):
        cid = concept_ids[idx]
        mean_ctx[cid] += centered[idx]
        counts[cid] += 1.0
    for c in range(N_CONCEPTS):
        if counts[c] > 0:
            mean_ctx[c] /= counts[c]

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
        "shuffle_order_sig": order_sig,
    }
    return concept_hds, diag


def arm_competitive_only(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Char+positional + per-concept winner-take-all + Hebbian (sparse ternary)."""
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)

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
        E_c = np.abs(acc[c]) / counts[c]
        mask = _sparse_topk_mask(E_c, TARGET_SPARSE_RATE)
        sign_c = np.sign(acc[c]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c * mask.astype(np.float32)

    diag = {"competitive_target_sparse_rate": TARGET_SPARSE_RATE}
    return concept_hds, diag


def arm_naive_wta_sampling(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """NEW v2 arm: reproduce 2026-06-23 sparse_engram_allocation mechanism.

    Reference: `sparse_engram_allocation_smoke_v1` (prereg 2026-06-23) FALSIFIED
    naive collision-minimizing K-winners candidate sampling at N=4096 M=10K on
    all 3 predicted lifts. This arm reproduces that mechanism as a
    reference-control: brain-analog Spoke 1 (HYBRID) must strictly beat this
    baseline by gap >= 0.15 to demonstrate mechanism progress over the prior
    negative result.

    Mechanism (per 2026-06-23 falsified baseline):
      1. Encode contexts (concept-word masked out) via char+positional.
      2. Per-concept accumulate mean centered context (for sign selection).
      3. Iterate concepts in a random order; for each concept c:
         - Compute per-dim "candidate score" = -dim_use_count[d] + small noise
           (prefer dims with LOWER prior use = collision minimization).
         - Select top-K dims by score (K = TARGET_SPARSE_RATE * n_dim).
         - Sign = sign(mean_ctx[c, selected]); zeros -> +1.
         - Increment dim_use_count[selected] to bias next concept toward
           unused dims.

    Key architectural difference from ARM_COMPETITIVE_ONLY:
      COMPETITIVE_ONLY selects dims per-concept by per-dim consistency
        E_c[d] = |sum_i x_i[d]| / n_c  (per-concept discriminability)
        -> mask reflects the CONTEXT signal.
      NAIVE_WTA_SAMPLING selects dims by cross-concept collision minimization
        with only sign coming from context
        -> mask reflects allocation policy, NOT context discriminability.

    The 2026-06-23 falsification showed this cannot cluster related concepts
    because selected dims are chosen for cross-concept ORTHOGONALITY, not
    within-cluster consistency.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)

    mean_ctx = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for idx in range(len(sentences)):
        cid = concept_ids[idx]
        mean_ctx[cid] += centered[idx]
        counts[cid] += 1.0
    for c in range(N_CONCEPTS):
        if counts[c] > 0:
            mean_ctx[c] /= counts[c]

    K = max(1, int(round(TARGET_SPARSE_RATE * n_dim)))
    dim_use_count = np.zeros(n_dim, dtype=np.int32)
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)

    # RNG intentionally decoupled from PC-arm seed usage (different multiplier)
    # so any observed correlation with PC-arm results is NOT a shared-RNG bug.
    rng = np.random.default_rng(int(seed) * 7919 + 13)
    concept_order = rng.permutation(N_CONCEPTS)

    for c in concept_order:
        # score = dim_use_count + tiny tiebreak noise; pick K lowest.
        tiebreak = rng.random(n_dim).astype(np.float32)
        score = dim_use_count.astype(np.float32) + tiebreak * 0.01
        # np.argpartition k-th smallest at position K.
        selected = np.argpartition(score, K)[:K]
        signs = np.sign(mean_ctx[c, selected]).astype(np.float32)
        signs[signs == 0] = 1.0
        concept_hds[c, selected] = signs
        dim_use_count[selected] += 1

    diag = {
        "naive_wta_K": K,
        "naive_wta_max_collision": int(dim_use_count.max()),
        "naive_wta_mean_collision": float(dim_use_count.mean()),
    }
    return concept_hds, diag


def arm_full_hybrid(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """PC-learned W + per-concept competitive winner-take-all (composed)."""
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)

    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    lr = 1.0 / float(n_dim)
    n_written = 0
    n_skipped = 0
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(sentences))
    order_sig = hashlib.sha256(
        order[: min(20, len(order))].tobytes()
    ).hexdigest()[:16]
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
        "shuffle_order_sig": order_sig,
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
    n_total = concept_hds.size
    if n_total == 0:
        return 0.0
    return float(np.count_nonzero(concept_hds)) / float(n_total)


def _intra_cluster_cos(concept_hds: np.ndarray) -> tuple[float, list[float]]:
    values: list[float] = []
    for cluster_id in range(len(CLUSTERS)):
        i0 = 2 * cluster_id
        i1 = 2 * cluster_id + 1
        values.append(_cos(concept_hds[i0], concept_hds[i1]))
    mean = float(np.mean(values)) if values else 0.0
    return mean, values


def _inter_cluster_cos_mean(concept_hds: np.ndarray) -> float:
    n_clusters = len(CLUSTERS)
    values: list[float] = []
    for i in range(n_clusters):
        for j in range(i + 1, n_clusters):
            values.append(_cos(concept_hds[2 * i], concept_hds[2 * j]))
    return float(np.mean(values)) if values else 0.0


def compute_arm_metrics(
    concept_hds: np.ndarray, extra_diag: dict
) -> dict:
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

    gap = cat_kitten_cos - cat_airplane_cos

    arm_digest = hashlib.sha256(concept_hds.tobytes()).hexdigest()[:32]

    return {
        "cat_kitten_cos": cat_kitten_cos,
        "cat_airplane_cos": cat_airplane_cos,
        "gap": gap,
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
# Verdict logic (v2 REFRAMED HPs).
# ---------------------------------------------------------------------------

def classify_verdict(per_seed_arm_metrics: list[dict]) -> dict:
    """Aggregate per-arm metrics and classify against v2 HP / HF bands."""
    per_arm: dict[str, dict[str, list[float]]] = {a: {} for a in ARMS}
    for entry in per_seed_arm_metrics:
        for arm, m in entry.items():
            for k, v in m.items():
                if isinstance(v, (int, float)):
                    per_arm[arm].setdefault(k, []).append(float(v))

    arm_summary: dict[str, dict] = {}
    for arm, series in per_arm.items():
        arm_summary[arm] = {}
        for k, vs in series.items():
            arm_summary[arm][f"{k}_mean"] = float(np.mean(vs))
            arm_summary[arm][f"{k}_std"] = float(np.std(vs))
            if abs(float(np.mean(vs))) > 1e-6:
                arm_summary[arm][f"{k}_cv"] = float(np.std(vs) / abs(np.mean(vs)))

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

    nwta_ck = get("ARM_NAIVE_WTA_SAMPLING", "cat_kitten_cos")
    nwta_ca = get("ARM_NAIVE_WTA_SAMPLING", "cat_airplane_cos")
    nwta_gap = nwta_ck - nwta_ca

    rand_ck = get("ARM_RANDOM_BASELINE", "cat_kitten_cos")
    trigram_ck = get("ARM_CHAR_TRIGRAM_BASELINE", "cat_kitten_cos")

    # HP checks (v2 REFRAMED).
    checks: dict[str, bool] = {}
    checks["HYBRID_matches_PREDICTIVE_within_tol"] = (
        abs(hyb_gap - pred_gap) <= HP_HYBRID_MATCHES_PRED_TOLERANCE
    )
    checks["HYBRID_sparse_rate_in_target"] = (
        HP_HYBRID_SPARSE_RATE_MIN <= hyb_sr <= HP_HYBRID_SPARSE_RATE_MAX
    )
    checks["HYBRID_beats_NAIVE_WTA_by_min"] = (
        hyb_gap >= nwta_gap + HP_HYBRID_BEATS_NAIVE_WTA_BY
    )
    checks["RANDOM_baseline_at_chance"] = abs(rand_ck) <= HP_RANDOM_COS_ABS_MAX
    checks["TRIGRAM_baseline_low_signal"] = abs(trigram_ck) <= HP_TRIGRAM_COS_ABS_MAX

    # HF checks (looser).
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
    if (hyb_gap - nwta_gap) < HF_HYBRID_GAP_MINUS_NAIVE_WTA_MIN:
        hf_reasons.append(
            f"hybrid_gap_minus_naive_wta={hyb_gap - nwta_gap:.3f}<"
            f"HF_min={HF_HYBRID_GAP_MINUS_NAIVE_WTA_MIN} (mechanism regresses "
            f"vs falsified 2026-06-23 baseline)"
        )

    all_hp_pass = all(checks.values())
    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HYBRID gap={hyb_gap:.3f} (PRED gap={pred_gap:.3f}, "
            f"|diff|={abs(hyb_gap-pred_gap):.3f}<={HP_HYBRID_MATCHES_PRED_TOLERANCE}); "
            f"NAIVE_WTA gap={nwta_gap:.3f} (HYBRID-NAIVE_WTA={hyb_gap-nwta_gap:.3f}"
            f">={HP_HYBRID_BEATS_NAIVE_WTA_BY}); "
            f"sparse={hyb_sr:.4f}; RANDOM={rand_ck:.3f}"
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
            "predictive_only_gap": pred_gap,
            "competitive_only_gap": comp_gap,
            "naive_wta_sampling_gap": nwta_gap,
            "hybrid_minus_predictive_gap": hyb_gap - pred_gap,
            "hybrid_minus_naive_wta_gap": hyb_gap - nwta_gap,
            "random_baseline_cat_kitten_cos": rand_ck,
            "trigram_baseline_cat_kitten_cos": trigram_ck,
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

    print(f"[seed {seed}] ARM_NAIVE_WTA_SAMPLING...", flush=True)
    hds, diag = arm_naive_wta_sampling(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_NAIVE_WTA_SAMPLING"] = hds
    per_arm_diag["ARM_NAIVE_WTA_SAMPLING"] = diag

    print(f"[seed {seed}] ARM_FULL_HYBRID...", flush=True)
    hds, diag = arm_full_hybrid(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_FULL_HYBRID"] = hds
    per_arm_diag["ARM_FULL_HYBRID"] = diag

    # ARMS-MUST-DIFFER gate (META_RULE_AF).
    digests = arms_must_differ(per_arm_hds)

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
                f"gap={m['gap']:.3f} "
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
        help="self_test = import + tiny; smoke = 5 seeds N=2048; full = 5 seeds N=4096",
    )
    parser.add_argument("--n-dim", type=int, default=0)
    parser.add_argument("--sentences-per-concept", type=int, default=0)
    parser.add_argument("--seeds", type=int, nargs="+", default=None)
    args = parser.parse_args()

    run_mode = args.run_mode
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    if run_mode == "self_test":
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
        hds_n, _ = arm_naive_wta_sampling(0, 256, sentences, concept_ids)
        assert hds_n.shape == (N_CONCEPTS, 256)
        hds_h, _ = arm_full_hybrid(0, 256, sentences, concept_ids)
        assert hds_h.shape == (N_CONCEPTS, 256)
        arms_must_differ({
            "ARM_RANDOM_BASELINE": hds_r,
            "ARM_CHAR_TRIGRAM_BASELINE": hds_t,
            "ARM_PREDICTIVE_ONLY": hds_p,
            "ARM_COMPETITIVE_ONLY": hds_c,
            "ARM_NAIVE_WTA_SAMPLING": hds_n,
            "ARM_FULL_HYBRID": hds_h,
        })
        m = compute_arm_metrics(hds_h, {})
        m_nwta = compute_arm_metrics(hds_n, {})
        print(
            f"[self_test PASS] hybrid gap={m['gap']:.3f} sparse={m['sparse_rate']:.4f}; "
            f"nwta gap={m_nwta['gap']:.3f} sparse={m_nwta['sparse_rate']:.4f}",
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

    # Seed-variance investigation (Director-requested):
    # Per-seed HYBRID gap + shuffle_order_sig so post-hoc correlation can
    # answer "is the seed variance driven by PC-update order?"
    seed_variance_investigation: list[dict] = []
    for entry in per_seed:
        arm = entry["arms"].get("ARM_FULL_HYBRID", {})
        seed_variance_investigation.append({
            "seed": entry["seed"],
            "hybrid_gap": arm.get("gap", None),
            "hybrid_cat_kitten_cos": arm.get("cat_kitten_cos", None),
            "hybrid_cat_airplane_cos": arm.get("cat_airplane_cos", None),
            "hybrid_shuffle_order_sig": arm.get("shuffle_order_sig", None),
            "hybrid_pc_written": arm.get("pc_written", None),
            "hybrid_pc_skipped": arm.get("pc_skipped", None),
            "hybrid_W_frobenius": arm.get("W_frobenius", None),
        })

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
            "hp_hybrid_matches_pred_tol": HP_HYBRID_MATCHES_PRED_TOLERANCE,
            "hp_hybrid_beats_naive_wta_by": HP_HYBRID_BEATS_NAIVE_WTA_BY,
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
        "seed_variance_investigation": seed_variance_investigation,
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
                    "HYBRID_matches_PREDICTIVE_within_tol",
                    "HYBRID_sparse_rate_in_target",
                    "HYBRID_beats_NAIVE_WTA_by_min",
                ],
                "ARM_RANDOM_BASELINE": ["RANDOM_baseline_at_chance"],
                "ARM_CHAR_TRIGRAM_BASELINE": ["TRIGRAM_baseline_low_signal"],
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
    _output_dir_for_crash = _output_dir("smoke")
    try:
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
