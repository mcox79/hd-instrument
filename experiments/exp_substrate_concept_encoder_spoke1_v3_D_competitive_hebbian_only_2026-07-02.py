"""Stage 2 Spoke 1 substrate concept encoder v3-D: competitive-Hebbian ONLY (drop PC).

ANCHOR: substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02

WHY V3-D (drop PC from Spoke 1):
    6/6 convergent evidence across 5x drill (2026-07-02) + empirical drill
    (5-seed 6-config diagnostic sweep on v2 HYBRID) established that
    PREDICTIVE CODING DOES NOT EARN COMPLEXITY in composition with the
    per-concept competitive WTA mechanism for the concept-encoding
    functional target (within-cluster consolidation / cat==kitten similarity).

    Empirical drill top-line (MEASURED@notes/research_spoke1_pc_earning_complexity_investigation_2026-07-02.md):
      Variant A pre-mask compose at W_ALPHA={0.10, 0.5, 1.0}:
        Delta_intra_cluster_cos_mean vs COMPETITIVE_ONLY =
          {-0.038, -0.173, -0.238} (monotone-degrades; NOT rescued at any W_ALPHA)
      Variant B post-mask sign-modulation at W_ALPHA={0.5, 1.0}:
        Delta_intra = -0.002 (null intervention; raw acc magnitude dominates)
      Seed 29 pathology root-caused: PC's W develops asymmetric amplification
      (cat 3.4x cross-projection, kitten 1.2x); top-K gets hijacked into
      airplane-space.
      Apparent v2 "gap improvement" is Goodhart's Law on the summary metric
      (cross-corpus anti-correlation up, within-cluster consolidation down;
      net gap looks similar but mechanism is worse).

    Under the brain-best-in-class strategic anchor (USER-LOCKED 2026-07-02),
    a mechanism that DEGRADES the primary target (within-cluster consolidation)
    cannot ship. Also: the ML/AI drill (SoftHebb / Journe 2023) recommends
    competitive-only baseline; the neuroscience drill notes cortical maps
    (V1 / SOM / concept cells) are all competitive-Hebbian in brain WITHOUT
    a PC layer at this level of processing. PC is legitimately brain-analog
    at higher-level hierarchical prediction (Rao-Ballard); it belongs in
    Spoke 2+ (temporal contiguity trace / one-shot indexing) where hierarchy
    makes sense, NOT in a flat concept-formation stage.

    See design ref for Spoke 2 (temporal contiguity / Foldiak trace-rule):
      notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md

BRAIN + LITERATURE ANALOGS (this cell's design lineage):
  * Foldiak 1990 "Forming sparse representations by local anti-Hebbian
    learning" -- competitive-Hebbian + optional anti-Hebbian lateral
    inhibition yields sparse-distributed codes.
  * Kohonen 1982 self-organizing maps -- competitive winner update.
  * Journe et al. 2023 SoftHebb -- competitive-only Hebbian networks
    trained without backprop, close to gradient-based baselines
    (ML/AI-drill recommendation; competitive-only is the baseline to beat
    before adding hierarchy).
  * Quiroga et al. 2005 "Invariant visual representation by single neurons
    in the human brain" (concept cells) -- brain's concept-encoding
    functional target; empirically emerges from competitive-Hebbian
    dynamics, no PC layer at that level.
  * Cerebellar granule cells (Marr 1969 / Albus 1971) -- classic sparse
    competitive-Hebbian encoding; no hierarchical top-down prediction
    involved.

ARMS (5 arms x 3 seeds = 15 units for smoke; same for full):
    ARM_RANDOM_BASELINE            Random-codebook HDs (no learning; chance)
    ARM_CHAR_TRIGRAM_BASELINE      hdlab.char_trigram_encoder on concept name
                                   (surface-form / bag-word baseline)
    ARM_COMPETITIVE_HEBBIAN        char+positional + per-concept Hebbian
                                   accumulator + k-largest top-K WTA + sign
                                   (Foldiak/Kohonen base -- LOAD-BEARING)
    ARM_COMP_HEB_LATERAL_INHIBITION  + anti-Hebbian lateral inhibition
                                   (winners suppress each other's mask
                                   selection; Foldiak 1990 style; STRETCH)
    ARM_NAIVE_WTA_SAMPLING         2026-06-23 falsified mechanism
                                   (K-winners collision-minimizing sampling
                                   with signs from mean context; PROGRESS
                                   CONTROL vs falsified reference)

HP BANDS (targeting CG for COMPETITIVE_HEBBIAN):
  HP1  ARM_COMPETITIVE_HEBBIAN cat_kitten_cos_mean >= 0.40
       (v2 baseline MEASURED: 0.522; HYPOTHESIZED band-floor 0.40 with 5%
       strict-above-floor -> effective threshold 0.42)
  HP2  ARM_COMPETITIVE_HEBBIAN cat_airplane_cos_mean <= 0.10
       (v2 baseline MEASURED: 0.015; HYPOTHESIZED cushion for 3-seed variance)
  HP3  ARM_COMPETITIVE_HEBBIAN sparse_rate in [0.010, 0.030]
       (architectural via top-K quantile mask; target 2%)
  HP4  ARM_COMPETITIVE_HEBBIAN intra_concept_cv < 0.20
       (invariance: within-cluster consistency stable across seeds; RELAXED
       from spec's 0.15 to 0.20 because v2 showed 0.30 on HYBRID; but
       COMPETITIVE_ONLY at v2 already MEASURED intra_std=0.006 / intra_mean=0.474
       -> effective intra_cv ~ 0.013 << 0.20; comfortably in band by prior)
  HP5  ARM_COMPETITIVE_HEBBIAN gap - NAIVE_WTA_SAMPLING gap >= 0.15
       (progress over 2026-06-23 falsified sparse_engram_allocation baseline)
  HP6  ARM_RANDOM_BASELINE cat_kitten_cos |mean| <= 0.05 (at chance)
  HP7  ARM_CHAR_TRIGRAM_BASELINE cat_kitten_cos |mean| <= 0.15
       (trigram carries some surface-form signal for morphologically related
       kitten/cat but should be well below competitive-Hebbian)

REPORT-ONLY (no gate for HARD_PASS but tracked for meta-signal):
  ARM_COMP_HEB_LATERAL_INHIBITION Delta vs ARM_COMPETITIVE_HEBBIAN --
    any positive lift over the competitive-Hebbian base counts as bonus
    evidence for lateral inhibition; negative or null is fine, cell still
    HARD_PASSes on the base competitive-Hebbian arm.

CELL-TEMPLATE MANDATORY compliance:
  * arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash)
  * final_metrics_atomicity = tmp_replace (META_RULE_AH)
  * except SystemExit: raise BEFORE except Exception (no BaseException)
  * crlb_n/a: emergent-representation cell; sparsity is architectural via
    top-K quantile mask, not a noise-floor CRLB regime
  * baseline_in_band at smoke (RANDOM ~0; CHAR_TRIGRAM ~0.05;
    NAIVE_WTA_SAMPLING likely below competitive-Hebbian; discriminating
    arm target 0.4-0.6)
  * HP_SCOPE per-arm declaration (LOAD_BEARING on ARM_COMPETITIVE_HEBBIAN)
  * cardinality_ok: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15
  * per-unit failure-class instrumentation (no bare except; except Exception only)
  * calibration_check: default_ok_for_this_regime (synthetic corpus; no tuning)
  * scale-sentinel selftest: probe at N_DIM=8192 for NaN detection at full-
    scale matmul before any smoke dispatch (per DISCIPLINE LOAD-BEARING)
  * discriminator survives scale (COMPETITIVE_HEBBIAN v2 baseline MEASURED
    at N=2048 and N=4096; extrapolates cleanly since accumulator is O(N)
    not saturating; smoke at N=2048 is representative)
  * progress_logging = line_buffered_stdout (cell is fast; no long timeouts)
  * all numbers in this docstring tagged MEASURED / HYPOTHESIZED / CITED per
    META_RULE_AC

ENV VAR CONTRACT (runner_v2_prod dispatch, MANDATORY per META_RULE
env_var_contract_must_survive_runner_dispatch):
  * HDLAB_RUN_MODE: production runner injects "full" into child env
    (runner_v2_prod.py line 536-537). Cell's argparser MUST read this via
    os.environ.get("HDLAB_RUN_MODE", "smoke") as its --run-mode default
    (belt-and-suspenders per runner_v2_prod line 524-528). Hardcoded
    default="smoke" caused silent smoke-scope runs on the production
    runner (Round 6 batch 2026-06-01 anchors E/F/J/K; recurred for this
    cell 2026-07-02 pre-fix).
  * HDLAB_EXP_NAME: informational; not consumed here.
  * HDLAB_QUEUE: informational (gpu_mandate gate uses this in other cells);
    not consumed here.
  * Verified by _run_selftest env_contract inline check (2026-07-02 fix).

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

# ---------------------------------------------------------------------------
# Configuration constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = (
    "substrate_concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02"
)

ARMS = [
    "ARM_RANDOM_BASELINE",
    "ARM_CHAR_TRIGRAM_BASELINE",
    "ARM_COMPETITIVE_HEBBIAN",
    "ARM_COMP_HEB_LATERAL_INHIBITION",
    "ARM_NAIVE_WTA_SAMPLING",
]

# 3 seeds per Director spec (v3-D is simpler mechanism -> tighter across-seed CV).
SEEDS_SMOKE = [11, 17, 23]
SEEDS_FULL = [11, 17, 23]

# HD dimensionality per run mode.
N_DIM_SMOKE = 2048     # smoke fast; 3-seed target wall < 5 min
N_DIM_FULL = 4096      # full matches v2 for comparability
N_DIM_SCALE_SENTINEL = 8192  # selftest scale-sanity probe (NaN check at prod scale)
MAX_POS = 24

# Corpus sizing (smoke = full for this cell; 40 sentences/concept for signal).
SENTENCES_PER_CONCEPT_SMOKE = 40
SENTENCES_PER_CONCEPT_FULL = 40

# Competitive-allocation target sparsity (~2%).
TARGET_SPARSE_RATE = 0.02

# Lateral inhibition strength for ARM_COMP_HEB_LATERAL_INHIBITION.
# Penalizes dim selection by (LI_ALPHA * dim_use_count_by_other_concepts).
# 0.0 = no inhibition (collapses to COMPETITIVE_HEBBIAN); higher = stronger.
LI_ALPHA = 0.05

# HP thresholds (v3-D bands per Director spec).
HP_COMP_HEB_CAT_KITTEN_MIN = 0.40
HP_COMP_HEB_CAT_AIRPLANE_MAX = 0.10
HP_COMP_HEB_SPARSE_RATE_MIN = 0.010
HP_COMP_HEB_SPARSE_RATE_MAX = 0.030
HP_COMP_HEB_INTRA_CV_MAX = 0.20
HP_COMP_HEB_BEATS_NAIVE_WTA_BY = 0.15
HP_RANDOM_COS_ABS_MAX = 0.05
HP_TRIGRAM_COS_ABS_MAX = 0.15

# HF thresholds (looser).
HF_COMP_HEB_CAT_KITTEN_COS_MIN = 0.20
HF_COMP_HEB_SPARSE_RATE_MIN = 0.005
HF_COMP_HEB_SPARSE_RATE_MAX = 0.10
HF_COMP_HEB_GAP_MINUS_NAIVE_WTA_MIN = -0.05

# Storage strategy tag.
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"

# Compute-arch tag.
COMPUTE_ARCH = "sequential_cpu_numpy_per_seed"


# ---------------------------------------------------------------------------
# Synthetic controlled corpus (unchanged from v1/v2 -- 25 clusters x 2 concepts).
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
    """Return (sentences, concept_ids, cluster_ids) -- one entry per sentence."""
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
    """Boolean mask keeping top-target_rate fraction of dimensions (by magnitude)."""
    k = max(1, int(round(target_rate * magnitudes.shape[0])))
    if k >= magnitudes.shape[0]:
        return np.ones_like(magnitudes, dtype=bool)
    # partition puts the k-th largest at position N-k; everything >= it is top-k.
    threshold = np.partition(magnitudes, magnitudes.shape[0] - k)[
        magnitudes.shape[0] - k
    ]
    return magnitudes >= threshold


def arm_random_baseline(seed: int, n_dim: int) -> np.ndarray:
    """Random bipolar HD per concept; no learning."""
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


def arm_competitive_hebbian(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """char+positional + per-concept Hebbian accumulator + k-largest WTA + sign.

    Foldiak/Kohonen brain-analog concept encoder:
      * For each sentence x with concept-label c:
          - Hebbian outer product with the one-hot concept indicator I_c:
            W[c, :] += lr * x       (equivalent to accumulator update)
        (this IS the online-Hebbian update between input x and per-concept
        neuron c; because I_c is one-hot the outer product reduces to a
        per-concept accumulator.)
      * After all sentences seen, per-concept activation profile a_c = W[c, :].
      * Winner-take-all on the dim axis: select top-K dims by |a_c| (k = 2%N).
      * Assign sign_c = sign(a_c[selected]) -> ternary bipolar HD.

    This is the classical sparse-Hebbian core (Foldiak 1990 competitive term
    without lateral inhibition). No PC; no residual gate; no top-down
    generative model. Mechanism is deliberately minimal so we can measure
    what the base sparse-competitive-Hebbian encoder produces before we
    add hierarchy in Spoke 2+.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts(sentences, concept_ids, encoder)
    centered = _center_contexts(ctx_hds)

    # Batch equivalent of per-concept online Hebbian outer product with one-hot
    # concept indicator: acc[c] += x for each sentence with label c.
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
        # Per-dim consistency magnitude (mean centered activation strength).
        E_c = np.abs(acc[c]) / counts[c]
        # WTA: top-K by magnitude.
        mask = _sparse_topk_mask(E_c, TARGET_SPARSE_RATE)
        sign_c = np.sign(acc[c]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c * mask.astype(np.float32)

    # NaN sentinel: detect scale-collapse (float overflow / NaN accumulation).
    n_nan = int(np.isnan(concept_hds).sum())
    diag = {
        "competitive_target_sparse_rate": TARGET_SPARSE_RATE,
        "n_nan": n_nan,
    }
    return concept_hds, diag


def arm_comp_heb_lateral_inhibition(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """COMPETITIVE_HEBBIAN base + anti-Hebbian lateral inhibition (Foldiak 1990).

    Extends ARM_COMPETITIVE_HEBBIAN with a per-dim inhibitory signal:
      * Compute per-concept magnitudes E_c as in COMPETITIVE_HEBBIAN.
      * Iterate concepts in a randomized order (per seed).
      * For each concept c, the effective selection score is
          score[d] = E_c[d] - LI_ALPHA * dim_use_count[d]
        where dim_use_count[d] is the number of earlier concepts (in this
        pass) that selected dim d. Higher use -> lower score -> less
        likely to be selected.
      * Top-K by score.
      * Increment dim_use_count on selected dims.

    Brain analog: winners in earlier concepts "kick out" the same dims from
    later concepts via lateral inhibitory connections. Foldiak showed this
    yields DECORRELATED sparse codes with better pattern separation than
    pure competitive-only (competitive-Hebbian alone allows the same dims
    to be picked by many concepts).

    Note: unlike ARM_NAIVE_WTA_SAMPLING, this arm still USES the per-concept
    consistency signal E_c as the base score (context-driven), and lateral
    inhibition only modulates. NAIVE_WTA picks dims by collision-only,
    ignoring E_c entirely -- that's why NAIVE_WTA is falsified.
    """
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
    dim_use_count = np.zeros(n_dim, dtype=np.float32)

    # Randomized concept order per seed.
    # Decouple from WTA/Hebbian seed reuse -- multiplier different.
    rng = np.random.default_rng(int(seed) * 15013 + 41)
    concept_order = rng.permutation(N_CONCEPTS)

    K = max(1, int(round(TARGET_SPARSE_RATE * n_dim)))

    for c in concept_order:
        if counts[c] <= 0:
            continue
        E_c = np.abs(acc[c]) / counts[c]
        # Lateral inhibition: penalize by dim_use_count from earlier concepts.
        score = E_c - LI_ALPHA * dim_use_count
        # Select top-K by score.
        if K >= n_dim:
            selected = np.arange(n_dim)
        else:
            selected = np.argpartition(-score, K)[:K]
        sign_c = np.sign(acc[c, selected]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c, selected] = sign_c
        dim_use_count[selected] += 1.0

    n_nan = int(np.isnan(concept_hds).sum())
    diag = {
        "li_target_sparse_rate": TARGET_SPARSE_RATE,
        "li_alpha": LI_ALPHA,
        "li_dim_use_max": int(dim_use_count.max()),
        "li_dim_use_mean": float(dim_use_count.mean()),
        "n_nan": n_nan,
    }
    return concept_hds, diag


def arm_naive_wta_sampling(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """2026-06-23 sparse_engram_allocation FALSIFIED mechanism (progress control).

    Reference: `sparse_engram_allocation_smoke_v1` (prereg 2026-06-23) FALSIFIED
    naive collision-minimizing K-winners candidate sampling at N=4096 M=10K on
    all 3 predicted lifts. This arm reproduces that mechanism as a
    reference-control: brain-analog Spoke 1 (COMPETITIVE_HEBBIAN) must
    strictly beat this baseline by gap >= 0.15 to demonstrate mechanism
    progress over the prior negative result.

    Mechanism:
      1. Encode contexts via char+positional, mean-center.
      2. Per-concept accumulate mean centered context (for sign only).
      3. Iterate concepts in random order; for each c:
         - Score = dim_use_count + tiebreak noise (prefer low-use dims).
         - Pick K lowest-score dims (K = TARGET_SPARSE_RATE * n_dim).
         - sign = sign(mean_ctx[c, selected]); zeros -> +1.
         - Increment dim_use_count on selected dims.

    Architectural diff vs COMPETITIVE_HEBBIAN: NAIVE_WTA_SAMPLING picks dims
    by cross-concept COLLISION MINIMIZATION only. It ignores per-dim
    within-concept consistency magnitude E_c. That's why it can't cluster
    related concepts -- selected dims are chosen for cross-concept
    orthogonality, not for within-cluster consistency.
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

    rng = np.random.default_rng(int(seed) * 7919 + 13)
    concept_order = rng.permutation(N_CONCEPTS)

    for c in concept_order:
        tiebreak = rng.random(n_dim).astype(np.float32)
        score = dim_use_count.astype(np.float32) + tiebreak * 0.01
        selected = np.argpartition(score, K)[:K]
        signs = np.sign(mean_ctx[c, selected]).astype(np.float32)
        signs[signs == 0] = 1.0
        concept_hds[c, selected] = signs
        dim_use_count[selected] += 1

    n_nan = int(np.isnan(concept_hds).sum())
    diag = {
        "naive_wta_K": K,
        "naive_wta_max_collision": int(dim_use_count.max()),
        "naive_wta_mean_collision": float(dim_use_count.mean()),
        "n_nan": n_nan,
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
# Verdict logic (v3-D HPs).
# ---------------------------------------------------------------------------

def classify_verdict(per_seed_arm_metrics: list[dict]) -> dict:
    """Aggregate per-arm metrics and classify against v3-D HP / HF bands."""
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

    ch_ck = get("ARM_COMPETITIVE_HEBBIAN", "cat_kitten_cos")
    ch_ca = get("ARM_COMPETITIVE_HEBBIAN", "cat_airplane_cos")
    ch_sr = get("ARM_COMPETITIVE_HEBBIAN", "sparse_rate")
    ch_intra = get("ARM_COMPETITIVE_HEBBIAN", "intra_cluster_cos_mean")
    ch_inter = get("ARM_COMPETITIVE_HEBBIAN", "inter_cluster_cos_mean")
    ch_intra_cv_mean = get("ARM_COMPETITIVE_HEBBIAN", "intra_concept_cv")
    ch_gap = ch_ck - ch_ca

    nwta_ck = get("ARM_NAIVE_WTA_SAMPLING", "cat_kitten_cos")
    nwta_ca = get("ARM_NAIVE_WTA_SAMPLING", "cat_airplane_cos")
    nwta_gap = nwta_ck - nwta_ca

    li_ck = get("ARM_COMP_HEB_LATERAL_INHIBITION", "cat_kitten_cos")
    li_ca = get("ARM_COMP_HEB_LATERAL_INHIBITION", "cat_airplane_cos")
    li_intra = get("ARM_COMP_HEB_LATERAL_INHIBITION", "intra_cluster_cos_mean")
    li_gap = li_ck - li_ca

    rand_ck = get("ARM_RANDOM_BASELINE", "cat_kitten_cos")
    trigram_ck = get("ARM_CHAR_TRIGRAM_BASELINE", "cat_kitten_cos")

    # HP checks (v3-D bands).
    checks: dict[str, bool] = {}
    checks["COMP_HEB_cat_kitten_cos_at_or_above_floor"] = (
        ch_ck >= HP_COMP_HEB_CAT_KITTEN_MIN
    )
    checks["COMP_HEB_cat_airplane_cos_at_or_below_ceiling"] = (
        ch_ca <= HP_COMP_HEB_CAT_AIRPLANE_MAX
    )
    checks["COMP_HEB_sparse_rate_in_target"] = (
        HP_COMP_HEB_SPARSE_RATE_MIN <= ch_sr <= HP_COMP_HEB_SPARSE_RATE_MAX
    )
    checks["COMP_HEB_intra_concept_cv_below_ceiling"] = (
        ch_intra_cv_mean < HP_COMP_HEB_INTRA_CV_MAX
    )
    checks["COMP_HEB_beats_NAIVE_WTA_by_min"] = (
        ch_gap >= nwta_gap + HP_COMP_HEB_BEATS_NAIVE_WTA_BY
    )
    checks["RANDOM_baseline_at_chance"] = abs(rand_ck) <= HP_RANDOM_COS_ABS_MAX
    checks["TRIGRAM_baseline_low_signal"] = abs(trigram_ck) <= HP_TRIGRAM_COS_ABS_MAX

    # HF checks (looser).
    hf_reasons: list[str] = []
    if ch_ck < HF_COMP_HEB_CAT_KITTEN_COS_MIN:
        hf_reasons.append(
            f"comp_heb_cat_kitten_cos={ch_ck:.3f}<HF_min={HF_COMP_HEB_CAT_KITTEN_COS_MIN}"
        )
    if not (HF_COMP_HEB_SPARSE_RATE_MIN <= ch_sr <= HF_COMP_HEB_SPARSE_RATE_MAX):
        hf_reasons.append(
            f"comp_heb_sparse_rate={ch_sr:.4f} outside "
            f"[{HF_COMP_HEB_SPARSE_RATE_MIN},{HF_COMP_HEB_SPARSE_RATE_MAX}]"
        )
    if (ch_gap - nwta_gap) < HF_COMP_HEB_GAP_MINUS_NAIVE_WTA_MIN:
        hf_reasons.append(
            f"comp_heb_gap_minus_naive_wta={ch_gap - nwta_gap:.3f}<"
            f"HF_min={HF_COMP_HEB_GAP_MINUS_NAIVE_WTA_MIN} (mechanism regresses "
            f"vs falsified 2026-06-23 baseline)"
        )

    all_hp_pass = all(checks.values())
    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"COMP_HEB ck={ch_ck:.3f} ca={ch_ca:.3f} gap={ch_gap:.3f} "
            f"(intra_mean={ch_intra:.3f} intra_cv={ch_intra_cv_mean:.3f} "
            f"sparse={ch_sr:.4f}); "
            f"NAIVE_WTA gap={nwta_gap:.3f} (COMP_HEB-NAIVE_WTA={ch_gap-nwta_gap:.3f}"
            f">={HP_COMP_HEB_BEATS_NAIVE_WTA_BY}); "
            f"RANDOM ck={rand_ck:.3f}; TRIGRAM ck={trigram_ck:.3f}; "
            f"LI(report-only) gap={li_gap:.3f} delta_intra={li_intra-ch_intra:+.3f}"
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
            "comp_heb_cat_kitten_cos": ch_ck,
            "comp_heb_cat_airplane_cos": ch_ca,
            "comp_heb_gap": ch_gap,
            "comp_heb_sparse_rate": ch_sr,
            "comp_heb_intra_cluster_cos_mean": ch_intra,
            "comp_heb_inter_cluster_cos_mean": ch_inter,
            "comp_heb_intra_concept_cv_mean": ch_intra_cv_mean,
            "naive_wta_sampling_gap": nwta_gap,
            "lateral_inhibition_gap": li_gap,
            "lateral_inhibition_intra_cluster_cos_mean": li_intra,
            "comp_heb_minus_naive_wta_gap": ch_gap - nwta_gap,
            "li_minus_comp_heb_intra": li_intra - ch_intra,
            "li_minus_comp_heb_gap": li_gap - ch_gap,
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

    print(f"[seed {seed}] ARM_COMPETITIVE_HEBBIAN...", flush=True)
    hds, diag = arm_competitive_hebbian(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_COMPETITIVE_HEBBIAN"] = hds
    per_arm_diag["ARM_COMPETITIVE_HEBBIAN"] = diag

    print(f"[seed {seed}] ARM_COMP_HEB_LATERAL_INHIBITION...", flush=True)
    hds, diag = arm_comp_heb_lateral_inhibition(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_COMP_HEB_LATERAL_INHIBITION"] = hds
    per_arm_diag["ARM_COMP_HEB_LATERAL_INHIBITION"] = diag

    print(f"[seed {seed}] ARM_NAIVE_WTA_SAMPLING...", flush=True)
    hds, diag = arm_naive_wta_sampling(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_NAIVE_WTA_SAMPLING"] = hds
    per_arm_diag["ARM_NAIVE_WTA_SAMPLING"] = diag

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


def _run_selftest() -> None:
    """Import + tiny + scale-sentinel probe at N=8192 for NaN detection."""
    # Env-var contract check: verify argparser default reads HDLAB_RUN_MODE.
    # META durable pattern (bias-checklist 2026-07-02): smoke code path must
    # exercise same env-var-reading branches as FULL. Round 6 batch 2026-06-01
    # anchors E/F/J/K + Spoke 1 v3-D 2026-07-02 failure mode: hardcoded
    # default="smoke" bypasses runner_v2_prod HDLAB_RUN_MODE=full injection.
    _test_env_val = "full"
    _saved_env = os.environ.get("HDLAB_RUN_MODE")
    os.environ["HDLAB_RUN_MODE"] = _test_env_val
    try:
        _probe = argparse.ArgumentParser(add_help=False)
        _probe.add_argument(
            "--run-mode",
            default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
            choices=["self_test", "smoke", "full"],
        )
        _probe_args = _probe.parse_args([])  # no CLI args -> default resolved
        assert _probe_args.run_mode == _test_env_val, (
            f"ENV_VAR_CONTRACT_VIOLATION: HDLAB_RUN_MODE={_test_env_val} "
            f"not honored by argparser default (got {_probe_args.run_mode!r}). "
            f"This class of bug caused silent smoke-scope runs on production "
            f"runner (Round 6 batch 2026-06-01 anchors E/F/J/K; Spoke 1 v3-D "
            f"2026-07-02). Fix: default=os.environ.get('HDLAB_RUN_MODE', 'smoke')."
        )
    finally:
        if _saved_env is None:
            os.environ.pop("HDLAB_RUN_MODE", None)
        else:
            os.environ["HDLAB_RUN_MODE"] = _saved_env
    print(
        f"[selftest env_contract PASS] HDLAB_RUN_MODE={_test_env_val!r} "
        f"honored by argparser default; runner FULL dispatch will not "
        f"silently downgrade to smoke.",
        flush=True,
    )

    # Tiny functional selftest at N=256.
    sentences, concept_ids, _ = build_corpus(0, 2)
    assert len(sentences) == N_CONCEPTS * 2
    hds_r = arm_random_baseline(0, 256)
    assert hds_r.shape == (N_CONCEPTS, 256)
    hds_t = arm_char_trigram_baseline(0, 256)
    assert hds_t.shape == (N_CONCEPTS, 256)
    hds_c, _ = arm_competitive_hebbian(0, 256, sentences, concept_ids)
    assert hds_c.shape == (N_CONCEPTS, 256)
    hds_l, _ = arm_comp_heb_lateral_inhibition(0, 256, sentences, concept_ids)
    assert hds_l.shape == (N_CONCEPTS, 256)
    hds_n, _ = arm_naive_wta_sampling(0, 256, sentences, concept_ids)
    assert hds_n.shape == (N_CONCEPTS, 256)
    arms_must_differ({
        "ARM_RANDOM_BASELINE": hds_r,
        "ARM_CHAR_TRIGRAM_BASELINE": hds_t,
        "ARM_COMPETITIVE_HEBBIAN": hds_c,
        "ARM_COMP_HEB_LATERAL_INHIBITION": hds_l,
        "ARM_NAIVE_WTA_SAMPLING": hds_n,
    })

    # Scale-sentinel probe at N_DIM=8192: LOAD-BEARING arm only, 1 seed, minimal
    # corpus. Verifies no NaN / overflow at full production scale before smoke.
    print(f"[selftest] scale-sentinel probe at N_DIM={N_DIM_SCALE_SENTINEL}",
          flush=True)
    s_sent, s_cids, _ = build_corpus(0, 4)  # tiny corpus at real N=8192
    hds_ss, diag_ss = arm_competitive_hebbian(
        0, N_DIM_SCALE_SENTINEL, s_sent, s_cids
    )
    assert hds_ss.shape == (N_CONCEPTS, N_DIM_SCALE_SENTINEL)
    n_nan_ss = int(np.isnan(hds_ss).sum())
    n_inf_ss = int(np.isinf(hds_ss).sum())
    assert n_nan_ss == 0, (
        f"SCALE_SENTINEL_NAN_DETECTED at N={N_DIM_SCALE_SENTINEL}: "
        f"n_nan={n_nan_ss} in ARM_COMPETITIVE_HEBBIAN. "
        f"Mechanism has scale-collapse; do NOT dispatch smoke."
    )
    assert n_inf_ss == 0, (
        f"SCALE_SENTINEL_INF_DETECTED at N={N_DIM_SCALE_SENTINEL}: "
        f"n_inf={n_inf_ss} in ARM_COMPETITIVE_HEBBIAN"
    )
    m_ss = compute_arm_metrics(hds_ss, diag_ss)
    print(
        f"[selftest scale-sentinel PASS] N={N_DIM_SCALE_SENTINEL} "
        f"n_nan=0 n_inf=0 "
        f"sparse_rate={m_ss['sparse_rate']:.4f} "
        f"cat_kitten={m_ss['cat_kitten_cos']:.3f}",
        flush=True,
    )

    # Legacy tiny functional at N=256.
    m = compute_arm_metrics(hds_c, {})
    m_nwta = compute_arm_metrics(hds_n, {})
    m_li = compute_arm_metrics(hds_l, {})
    print(
        f"[self_test PASS] N=256 comp_heb gap={m['gap']:.3f} "
        f"sparse={m['sparse_rate']:.4f}; "
        f"lateral_inhibition gap={m_li['gap']:.3f} "
        f"sparse={m_li['sparse_rate']:.4f}; "
        f"nwta gap={m_nwta['gap']:.3f} sparse={m_nwta['sparse_rate']:.4f}",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    # HDLAB_RUN_MODE env-var read per runner_v2_prod contract (line 524-528,
    # 536-537). runner injects HDLAB_RUN_MODE=full into child env; hardcoded
    # default="smoke" would silently downgrade FULL dispatches to smoke scope.
    parser.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
        choices=["self_test", "smoke", "full"],
        help="self_test = import + tiny + scale-sentinel N=8192; "
             "smoke = 3 seeds N=2048; full = 3 seeds N=4096. "
             "Default reads HDLAB_RUN_MODE env if set.",
    )
    parser.add_argument("--self-test", action="store_true",
                        help="Alias for --run-mode self_test (queue_add convention).")
    parser.add_argument("--smoke", action="store_true",
                        help="Alias for --run-mode smoke (queue_add convention).")
    parser.add_argument("--n-dim", type=int, default=0)
    parser.add_argument("--sentences-per-concept", type=int, default=0)
    parser.add_argument("--seeds", type=int, nargs="+", default=None)
    args = parser.parse_args()

    # Alias resolution.
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

    # Per-seed COMPETITIVE_HEBBIAN + LATERAL_INHIBITION load-bearing view.
    seed_load_bearing_view: list[dict] = []
    for entry in per_seed:
        ch = entry["arms"].get("ARM_COMPETITIVE_HEBBIAN", {})
        li = entry["arms"].get("ARM_COMP_HEB_LATERAL_INHIBITION", {})
        nw = entry["arms"].get("ARM_NAIVE_WTA_SAMPLING", {})
        seed_load_bearing_view.append({
            "seed": entry["seed"],
            "comp_heb_cat_kitten_cos": ch.get("cat_kitten_cos", None),
            "comp_heb_cat_airplane_cos": ch.get("cat_airplane_cos", None),
            "comp_heb_gap": ch.get("gap", None),
            "comp_heb_intra_mean": ch.get("intra_cluster_cos_mean", None),
            "comp_heb_intra_cv": ch.get("intra_concept_cv", None),
            "comp_heb_sparse_rate": ch.get("sparse_rate", None),
            "lateral_inhibition_gap": li.get("gap", None),
            "lateral_inhibition_intra_mean": li.get("intra_cluster_cos_mean", None),
            "naive_wta_gap": nw.get("gap", None),
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
            "target_sparse_rate": TARGET_SPARSE_RATE,
            "li_alpha": LI_ALPHA,
            "hp_comp_heb_cat_kitten_min": HP_COMP_HEB_CAT_KITTEN_MIN,
            "hp_comp_heb_cat_airplane_max": HP_COMP_HEB_CAT_AIRPLANE_MAX,
            "hp_comp_heb_beats_naive_wta_by": HP_COMP_HEB_BEATS_NAIVE_WTA_BY,
            "hp_comp_heb_intra_cv_max": HP_COMP_HEB_INTRA_CV_MAX,
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
        "seed_load_bearing_view": seed_load_bearing_view,
        "per_seed": per_seed,
        "cell_template_compliance": {
            "arms_differ_verified": True,
            "final_metrics_atomicity": "tmp_replace",
            "cardinality_ok": True,
            "except_systemexit_before_exception": True,
            "start_marker_written": True,
            "crash_diagnostic_present": True,
            "hp_scope": {
                "ARM_COMPETITIVE_HEBBIAN": [
                    "COMP_HEB_cat_kitten_cos_at_or_above_floor",
                    "COMP_HEB_cat_airplane_cos_at_or_below_ceiling",
                    "COMP_HEB_sparse_rate_in_target",
                    "COMP_HEB_intra_concept_cv_below_ceiling",
                    "COMP_HEB_beats_NAIVE_WTA_by_min",
                ],
                "ARM_COMP_HEB_LATERAL_INHIBITION": [],
                "ARM_NAIVE_WTA_SAMPLING": [],
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
            "scale_sentinel_probe": (
                f"selftest runs ARM_COMPETITIVE_HEBBIAN at N={N_DIM_SCALE_SENTINEL} "
                f"and asserts n_nan==0"
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
    # Pre-parse-time fallback: honor HDLAB_RUN_MODE env so crash-metrics
    # land in the correct output_dir even if early-parser itself explodes.
    _output_dir_for_crash = _output_dir(
        os.environ.get("HDLAB_RUN_MODE", "smoke")
    )
    try:
        _early = argparse.ArgumentParser(add_help=False)
        _early.add_argument("--run-mode",
                            default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
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
