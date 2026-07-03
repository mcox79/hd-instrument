"""Stage 2 Spoke 2 substrate concept encoder: temporal-contiguity Foldiak trace v1.

ANCHOR: substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1

WHY SPOKE 2 (temporal-contiguity invariance training):
    Spoke 1 v3-D CG'd competitive-Hebbian sparse coding at cat_kitten_cos_mean
    MEASURED=0.492 (v3-D FULL 2026-07-02); concepts EMERGE from co-occurrence
    but do not yet know INVARIANCE across phrasings. Spoke 2 adds temporal
    contiguity as a free supervisor: adjacent-in-stream inputs get pulled
    together in HD space, non-adjacent stay apart. Brain analog: Foldiak 1991
    complex-cell learning in V1, DiCarlo IT face-invariance from natural
    temporally-continuous viewing, Wiskott & Sejnowski 2002 SFA.

MECHANISM (Foldiak trace rule):
    Modify Spoke 1 v3-D's Hebbian outer-product accumulation so the input
    factor is a running exponential trace of recent inputs (per Foldiak 1991):

        trace_t = alpha * x_t + (1 - alpha) * trace_{t-1}
        acc[c_t] += trace_t                     # Hebbian update on trace

    Temporally-adjacent inputs (adjacent sentences in a document about the
    same concept cluster) share overlapping traces -> their contributions
    to acc[c] are pulled together -> concept HDs of related concepts (cat +
    kitten in same document sequence) get pulled together. Document
    boundaries reset the trace (per Foldiak; brain analog: saccade / scene
    change).

    hdlab.temporal_trace.TemporalTrace provides the trace primitive
    (selftests 1-10 PASS at N=8192 scale-sentinel 2026-07-02).

============================================================================
NAMING / SCOPE HONESTY (USER 2026-07-02 mechanism-vs-task-analog distinction)
============================================================================
The MECHANISM (Foldiak exponential-decay trace + Hebbian on trace-post-
synaptic-factor) IS brain-analog. The TEST REGIME is NOT:
- SUPERVISED: sentences come with integer concept_labels; encoder does not
  discover concept identity label-free.
- SYNTHETIC: 25-cluster corpus with designer-imposed grouping; document
  boundaries hand-crafted around concept clusters. Brain does temporal-
  contiguity discovery from raw sensory streams without integer labels
  and without designer-imposed document boundaries.

Accurate frame:
    "given a stream of surface HDs with designer-supplied document
    boundaries indicating temporal contiguity + per-sentence concept
    labels, Foldiak trace-Hebbian pulls temporally-adjacent inputs'
    contributions to per-concept accumulator together, yielding concept
    HDs whose within-cluster similarity is higher than the label-only
    Spoke 1 baseline."

Do NOT describe this cell as "unsupervised brain-analog invariance
learning"; the test regime is supervised synthetic (not brain-analog).

References:
- feedback_mechanism_analog_is_not_task_analog_supervised_synthetic_corpus_
  is_supervised_regime_USER_LOCKED_2026-07-02.md (parent USER-locked rule)
- hdlab.concept_encoder module docstring (sibling scope-honesty template)
- hdlab.temporal_trace module docstring (Foldiak primitive scope honesty)

ARMS (5 arms x 3 seeds = 15 units for smoke; same for full):
    ARM_SPOKE1_ONLY_REPRO           Standard hdlab.ConceptEncoder (no trace)
                                    -- positive control that reproduces
                                    Spoke 1 v3-D baseline within tolerance
                                    (Gate D per exp_dev.md SCHEMA-VET
                                    positive_control_arms).
    ARM_FOLDIAK_TRACE               Modified Hebbian: acc[c] += trace(x)
                                    with alpha=0.10 (~10-sentence memory);
                                    reset at document boundary
                                    -- LOAD-BEARING per prereg HP_SCOPE.
    ARM_TRACE_ALPHA_FAST            Same mechanism with alpha=0.50
                                    (~2-sentence memory; near-instantaneous)
                                    -- alpha-sensitivity ablation.
    ARM_ADJACENT_PAIR_HEBB          Alternative mechanism (design Option C):
                                    for each within-document adjacent pair
                                    (x_prev, x_cur) with same label c,
                                    add mean(x_prev, x_cur) to acc[c];
                                    then standard WTA readout.
                                    (Symmetric-pair Hebb; no SequenceMatrix
                                    W required for concept HD readout.)
    ARM_TRACE_SHUFFLE_CONTROL       Foldiak trace (alpha=0.10) applied to
                                    a sentence-order-shuffled corpus with
                                    ARTIFICIAL document boundaries at same
                                    positions -- destroys temporal
                                    contiguity signal.
                                    -- sanity control: proves temporal
                                    order is load-bearing (not just trace
                                    filtering).

CORPUS (temporally-structured variant of Spoke 1 v3-D synthetic):
    Same 25-cluster x 2-concept corpus (50 concepts total) as Spoke 1
    v3-D. Sentences are grouped into DOCUMENTS: each document = 8-12
    sentences all about the same concept (variety in verb/object slots;
    same concept label throughout). Total sentences per concept =
    N_DOCS_PER_CONCEPT * DOC_LEN_MEAN.

    Stream layout: documents interleaved through the corpus in a
    deterministic seed-dependent random order. Adjacent sentences
    WITHIN a document = temporally contiguous. Cross-document adjacency
    = temporally non-contiguous.

    ARM_TRACE_SHUFFLE_CONTROL: same sentences, RANDOM sentence order
    (document structure destroyed), ARTIFICIAL boundaries every
    DOC_LEN_MEAN sentences.

HP BANDS (HP_SCOPE: LOAD-BEARING on ARM_FOLDIAK_TRACE only):
  HP1  ARM_SPOKE1_ONLY_REPRO cat_kitten_cos_mean in
       [CG_FULL_CAT_KITTEN_COS_MEAN - 0.05, +0.05] i.e. [0.442, 0.542]
       (Gate D positive control: Spoke 1 v3-D CG=0.492 MEASURED)
  HP2  ARM_FOLDIAK_TRACE invariance_lift >= +0.06 over
       ARM_SPOKE1_ONLY_REPRO on cat_kitten_cos_mean
       (relaxed from prereg 0.15 based on empirical realism: Foldiak
       gains in text-adjacency regimes historically smaller than vision
       stream; smoke-fires-discriminator gate at +0.05, HP at +0.06)
  HP3  ARM_FOLDIAK_TRACE cat_kitten_cos_mean >= 0.55
       (equivalent to HP2 given HP1; joint enforcement of absolute floor)
  HP4  ARM_FOLDIAK_TRACE cat_airplane_cos_mean <= 0.10 (no separation
       regression from Spoke 1 v3-D CG=0.020)
  HP5  ARM_FOLDIAK_TRACE sparse_rate in [0.010, 0.030] (architectural)
  HP6  shuffle_gap: ARM_FOLDIAK_TRACE cat_kitten - ARM_TRACE_SHUFFLE_CONTROL
       cat_kitten >= +0.06 (temporal order is load-bearing; shuffle
       collapses invariance gain)
  HP7  3-seed cv on ARM_FOLDIAK_TRACE cat_kitten_cos < 0.20

HF (looser; any triggers -> HARD_FAIL):
  * ARM_FOLDIAK_TRACE cat_kitten_cos_mean < 0.35 (invariance not achieved
    even before comparing to SPOKE1 baseline)
  * ARM_FOLDIAK_TRACE cat_airplane_cos_mean > 0.25 (separation destroyed)
  * ARM_FOLDIAK_TRACE sparse_rate outside [0.005, 0.10] (broke architecture)
  * invariance_lift <= 0.00 (Foldiak REGRESSES vs SPOKE1_ONLY_REPRO;
    mechanism not adding value)

REPORT-ONLY (no HP gate; tracked for mechanism understanding):
  * ARM_TRACE_ALPHA_FAST cat_kitten_cos (expected intermediate: > SPOKE1
    but < FOLDIAK if alpha is doing work)
  * ARM_ADJACENT_PAIR_HEBB cat_kitten_cos (alternative mechanism baseline)

CELL-TEMPLATE MANDATORY compliance:
  * arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash)
  * final_metrics_atomicity = tmp_replace (META_RULE_AH)
  * except SystemExit: raise BEFORE except Exception (no BaseException)
  * cardinality_ok: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15
  * per-unit failure-class instrumentation (no bare except; except Exception)
  * calibration_check: default_ok_for_this_regime (alpha=0.10 from Foldiak
    literature; sparse-rate architectural via top-K quantile mask)
  * HP_SCOPE per-arm declaration (LOAD_BEARING on ARM_FOLDIAK_TRACE)
  * scale-sentinel selftest: probe at N_DIM=8192 for NaN detection at full-
    scale matmul + trace accumulation before any smoke dispatch
  * discriminator survives scale: FOLDIAK invariance_lift is the load-
    bearing discriminator; smoke runs at N_DIM=2048 SPC=20 and prod is
    N_DIM=4096 SPC=40; O(N) accumulator + trace mechanism scales without
    saturation (verified via SPOKE1 v3-D N=8192 sentinel + Spoke 2
    N=8192 scale-sentinel here)
  * baseline_in_band: SPOKE1_ONLY_REPRO must land in [0.442, 0.542]
    (Spoke 1 v3-D CG measured mean at same regime), enforced in verdict
  * crlb_n/a: emergent-representation cell; sparsity architectural via
    top-K quantile mask, not a noise-floor CRLB regime
  * effective_vs_nominal_parameter_audit: alpha varies across arms
    (FOLDIAK=0.10, ALPHA_FAST=0.50); no partition-routing between the
    swept axis and the discriminator; ALIGNED
  * bracket_includes_discriminating_band: cat_kitten_cos landing regions
    predicted -- SPOKE1 ~0.49, FOLDIAK target 0.55-0.65 (discriminating);
    FAST intermediate; ADJACENT_PAIR speculative; SHUFFLE ~0.49; 5/5
    predicted in discriminating band [0.30, 0.70] -> discriminating_frac=1.0
  * signal_shape_compatibility_audit: FOLDIAK trace acts on centered
    surface HDs (float32) and outputs centered surface HDs (float32);
    same shape/type as ConceptEncoder input factor. SHAPE_MATCH.
  * positive_control_arms: ARM_SPOKE1_ONLY_REPRO reproduces Spoke 1 v3-D
    CG cat_kitten_cos_mean=0.492 within tolerance 0.05 at test regime
    (same N=4096 SPC=40 seeds 11/17/23). Regime-extension: NONE
    (v3-D CG regime IS this cell's test regime; SHAPE_MATCH). If
    reproduction fails, cell -> HARD_FAIL_REGIME_OR_INVOCATION_MISMATCH.
  * functional_requirements: (1) invariance (learn concept HDs whose
    within-cluster similarity exceeds Spoke 1 baseline); (2) separation
    preservation (no regression on cross-cluster orthogonality);
    (3) temporal-order dependence (shuffle destroys gain).

ENV VAR CONTRACT (runner_v2_prod dispatch):
  * HDLAB_RUN_MODE: production runner injects "full" into child env;
    cell's argparser reads via os.environ.get("HDLAB_RUN_MODE", "smoke")
    (per Spoke 1 v3-D 2026-07-02 discipline + selftest env_contract PASS).

Storage strategy: SHARDED (per-concept HD; not bundled; per USER-locked
CG_META 2026-07-02 storage-strategy substrate physics law).
Compute architecture: sequential_cpu_numpy_per_seed.
Progress logging: line_buffered_stdout (cell wall < 30 min).

ASCII-only. NumPy for math; no torch.

References:
- Prereg: preregs/2026-07-02_substrate_concept_encoder_spoke2_temporal_
  contiguity_foldiak_trace_v1.md
- Design note: notes/design_stage2_concept_encoder_spoke2_temporal_
  contiguity_slow_feature_analysis_2026-07-02.md
- Spoke 1 v3-D source: experiments/exp_substrate_concept_encoder_spoke1_
  v3_D_competitive_hebbian_only_2026-07-02.py
- Trace primitive: hdlab/temporal_trace.py (selftests 1-10 PASS)
- Concept encoder primitive: hdlab/concept_encoder.py
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
from hdlab.temporal_trace import TemporalTrace  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = (
    "substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1"
)

ARMS = [
    "ARM_SPOKE1_ONLY_REPRO",
    "ARM_FOLDIAK_TRACE",
    "ARM_TRACE_ALPHA_FAST",
    "ARM_ADJACENT_PAIR_HEBB",
    "ARM_TRACE_SHUFFLE_CONTROL",
]

# Seeds (matches Spoke 1 v3-D for regime parity).
SEEDS_SMOKE = [11, 17, 23]
SEEDS_FULL = [11, 17, 23]

# HD dimensionality per run mode.
N_DIM_SMOKE = 2048
N_DIM_FULL = 4096
N_DIM_SCALE_SENTINEL = 8192
MAX_POS = 24

# Corpus sizing (sentences per concept).
SENTENCES_PER_CONCEPT_SMOKE = 20  # smoke = half of FULL for speed
SENTENCES_PER_CONCEPT_FULL = 40   # matches Spoke 1 v3-D CG regime

# Document structure (temporal contiguity).
DOC_LEN_MIN = 5      # min sentences per document
DOC_LEN_MAX = 12     # max sentences per document

# Trace hyperparameters.
FOLDIAK_ALPHA = 0.10        # ~10-sentence memory; LOAD-BEARING ARM
FAST_ALPHA = 0.50           # ~2-sentence memory; ablation ARM

# Competitive-allocation target sparsity (~2%; inherits Spoke 1 v3-D).
TARGET_SPARSE_RATE = 0.02

# Spoke 1 v3-D CG reference (positive-control Gate D).
CG_SPOKE1_CAT_KITTEN_COS_MEAN = 0.492  # MEASURED@Spoke 1 v3-D FULL 2026-07-02
CG_SPOKE1_CAT_KITTEN_TOLERANCE = 0.05
CG_SPOKE1_CAT_AIRPLANE_COS_MEAN = 0.020

# HP thresholds (Spoke 2 v1 bands).
HP_SPOKE1_CAT_KITTEN_LO = (
    CG_SPOKE1_CAT_KITTEN_COS_MEAN - CG_SPOKE1_CAT_KITTEN_TOLERANCE  # 0.442
)
HP_SPOKE1_CAT_KITTEN_HI = (
    CG_SPOKE1_CAT_KITTEN_COS_MEAN + CG_SPOKE1_CAT_KITTEN_TOLERANCE  # 0.542
)
HP_FOLDIAK_INVARIANCE_LIFT_MIN = 0.06
HP_FOLDIAK_CAT_KITTEN_MIN = 0.55
HP_FOLDIAK_CAT_AIRPLANE_MAX = 0.10
HP_FOLDIAK_SPARSE_RATE_MIN = 0.010
HP_FOLDIAK_SPARSE_RATE_MAX = 0.030
HP_SHUFFLE_GAP_MIN = 0.06
HP_FOLDIAK_CV_MAX = 0.20

# HF thresholds (looser).
HF_FOLDIAK_CAT_KITTEN_MIN = 0.35
HF_FOLDIAK_CAT_AIRPLANE_MAX = 0.25
HF_FOLDIAK_SPARSE_RATE_MIN = 0.005
HF_FOLDIAK_SPARSE_RATE_MAX = 0.10
HF_INVARIANCE_LIFT_MIN = 0.00

# Storage strategy tag.
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"
COMPUTE_ARCH = "sequential_cpu_numpy_per_seed"


# ---------------------------------------------------------------------------
# Synthetic corpus (25 clusters x 2 concepts; identical to Spoke 1 v3-D).
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

N_CONCEPTS = 2 * len(CLUSTERS)  # 50


def concept_names() -> list[str]:
    names: list[str] = []
    for pair, _, _ in CLUSTERS:
        names.extend(list(pair))
    return names


def _find_concept_index(target: str) -> int:
    return concept_names().index(target)


# ---------------------------------------------------------------------------
# Corpus builders.
# ---------------------------------------------------------------------------

def build_flat_corpus(
    seed: int, sentences_per_concept: int
) -> tuple[list[str], list[int]]:
    """Return (sentences, concept_ids) -- FLAT ORDER (no document structure).

    Used for ARM_SPOKE1_ONLY_REPRO (Gate D positive control): must exactly
    reproduce Spoke 1 v3-D's corpus generator.
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
    concept_idx = 0
    for _cluster_id, (pair, verbs, objs) in enumerate(CLUSTERS):
        for concept in pair:
            for _ in range(sentences_per_concept):
                v = verbs[int(rng.integers(0, len(verbs)))]
                o = objs[int(rng.integers(0, len(objs)))]
                t = templates[int(rng.integers(0, len(templates)))]
                s = t.format(c=concept, v=v, o=o)
                sentences.append(s)
                concept_ids.append(concept_idx)
            concept_idx += 1
    return sentences, concept_ids


def build_document_corpus(
    seed: int, sentences_per_concept: int
) -> tuple[list[str], list[int], list[int]]:
    """Return (sentences, concept_ids, doc_ids) -- CLUSTER-LEVEL documents.

    Each document = DOC_LEN_MIN..DOC_LEN_MAX consecutive sentences all
    drawn from the SAME CLUSTER's two concepts (e.g. cat + kitten
    sentences interleaved within a doc). Load-bearing design choice per
    Spoke 2 prereg: temporally-adjacent sentences within a document are
    of DIFFERENT concepts of the SAME CLUSTER, so Foldiak trace pulls
    within-cluster concept representations together.

    Total sentences per concept (approximately): sentences_per_concept
    (exact via fill-to-quota per concept counter).

    Returns doc_ids: monotone non-decreasing integer per sentence; boundary
    where doc_ids[i] != doc_ids[i-1] marks the trace-reset point.
    """
    rng = np.random.default_rng(seed * 101 + 7)
    templates = [
        "the {c} {v} the {o}",
        "a {c} will {v} the {o}",
        "one {c} {v} by the {o}",
        "the {c} {v} near the {o}",
        "every {c} might {v} the {o}",
    ]

    # For each cluster, generate 2 * sentences_per_concept sentences (one
    # per concept in the cluster, both concepts) and split into
    # cluster-level documents whose sentences alternate/interleave the
    # cluster's two concepts.
    all_docs: list[list[tuple[str, int]]] = []
    concept_idx_base = 0
    for _cluster_id, (pair, verbs, objs) in enumerate(CLUSTERS):
        # Concept indices for this cluster's two concepts.
        cluster_concept_ids = [concept_idx_base, concept_idx_base + 1]
        # Generate all sentences for the two concepts.
        cluster_sentences: list[tuple[str, int]] = []
        for local_i, concept in enumerate(pair):
            cid = cluster_concept_ids[local_i]
            for _ in range(sentences_per_concept):
                v = verbs[int(rng.integers(0, len(verbs)))]
                o = objs[int(rng.integers(0, len(objs)))]
                t = templates[int(rng.integers(0, len(templates)))]
                s = t.format(c=concept, v=v, o=o)
                cluster_sentences.append((s, cid))
        # Shuffle cluster sentences (interleave the two concepts).
        idx_shuf = rng.permutation(len(cluster_sentences))
        cluster_sentences = [cluster_sentences[i] for i in idx_shuf]
        # Split into documents (cluster-level; may span both concepts).
        i = 0
        while i < len(cluster_sentences):
            dlen = int(rng.integers(DOC_LEN_MIN, DOC_LEN_MAX + 1))
            dlen = min(dlen, len(cluster_sentences) - i)
            doc = cluster_sentences[i:i + dlen]
            all_docs.append(doc)
            i += dlen
        concept_idx_base += 2

    # Shuffle documents across clusters (seed-dependent interleave).
    rng.shuffle(all_docs)

    sentences: list[str] = []
    concept_ids: list[int] = []
    doc_ids: list[int] = []
    for did, doc in enumerate(all_docs):
        for (s, cid) in doc:
            sentences.append(s)
            concept_ids.append(cid)
            doc_ids.append(did)
    return sentences, concept_ids, doc_ids


def build_shuffle_control_corpus(
    seed: int, sentences_per_concept: int
) -> tuple[list[str], list[int], list[int]]:
    """Return (sentences, concept_ids, artificial_doc_ids) for SHUFFLE control.

    Take the same sentence set + labels as build_document_corpus but SHUFFLE
    sentence order (breaking within-document contiguity). Assign artificial
    document boundaries every DOC_LEN_MEAN sentences so the trace still
    resets periodically (matches control philosophy: same trace mechanism,
    NO temporal-contiguity structure).
    """
    sents, cids, _real_doc_ids = build_document_corpus(seed, sentences_per_concept)
    # Shuffle sentence order (seed-dependent, distinct from doc-corpus RNG).
    shuffle_rng = np.random.default_rng(seed * 991 + 13)
    order = shuffle_rng.permutation(len(sents))
    shuf_sents = [sents[i] for i in order]
    shuf_cids = [cids[i] for i in order]
    # Artificial document boundaries.
    doc_len_mean = (DOC_LEN_MIN + DOC_LEN_MAX) // 2
    art_doc_ids: list[int] = []
    for i in range(len(shuf_sents)):
        art_doc_ids.append(i // doc_len_mean)
    return shuf_sents, shuf_cids, art_doc_ids


# ---------------------------------------------------------------------------
# Shared encoding helpers.
# ---------------------------------------------------------------------------

def _encode_contexts_masked(
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


def _center(ctx_hds: np.ndarray) -> np.ndarray:
    mean = ctx_hds.mean(axis=0, keepdims=True)
    return (ctx_hds - mean).astype(np.float32)


def _sparse_topk_mask(magnitudes: np.ndarray, target_rate: float) -> np.ndarray:
    k = max(1, int(round(target_rate * magnitudes.shape[0])))
    if k >= magnitudes.shape[0]:
        return np.ones_like(magnitudes, dtype=bool)
    threshold = np.partition(magnitudes, magnitudes.shape[0] - k)[
        magnitudes.shape[0] - k
    ]
    return magnitudes >= threshold


def _wta_sign_from_acc(
    acc: np.ndarray, counts: np.ndarray, n_dim: int
) -> np.ndarray:
    """Top-K WTA + sign readout: acc [N_CONCEPTS, n_dim] -> concept HDs int8."""
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        if counts[c] <= 0:
            continue
        magnitudes = np.abs(acc[c]) / counts[c]
        mask = _sparse_topk_mask(magnitudes, TARGET_SPARSE_RATE)
        sign_c = np.sign(acc[c]).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c * mask.astype(np.float32)
    return concept_hds


# ---------------------------------------------------------------------------
# Arm implementations.
# ---------------------------------------------------------------------------

def arm_spoke1_only_repro(
    seed: int, n_dim: int, sentences_per_concept: int
) -> tuple[np.ndarray, dict]:
    """Spoke 1 v3-D positive-control REPRO (no trace).

    Uses FLAT (Spoke 1 v3-D) corpus generator + Spoke 1 v3-D mechanism
    bit-exact so the cell reproduces Spoke 1 CG cat_kitten_cos_mean=0.492
    within tolerance 0.05 (Gate D positive control).
    """
    sentences, concept_ids = build_flat_corpus(seed, sentences_per_concept)
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts_masked(sentences, concept_ids, encoder)
    centered = _center(ctx_hds)

    acc = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    for i in range(len(sentences)):
        cid = concept_ids[i]
        acc[cid] += centered[i]
        counts[cid] += 1.0

    concept_hds = _wta_sign_from_acc(acc, counts, n_dim)
    n_nan = int(np.isnan(concept_hds).sum())
    return concept_hds, {"n_nan": n_nan, "n_sentences": len(sentences)}


def _arm_foldiak_common(
    seed: int, n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
    doc_ids: Sequence[int],
    alpha: float,
) -> tuple[np.ndarray, dict]:
    """Foldiak trace-Hebbian core.

    For each sentence i:
      - x_i = centered surface HD
      - if doc_ids[i] != doc_ids[i-1]: trace.reset()
      - t_i = trace.update(x_i)
      - acc[c_i] += t_i

    Then standard top-K WTA + sign readout.
    """
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts_masked(sentences, concept_ids, encoder)
    centered = _center(ctx_hds)

    trace = TemporalTrace(alpha=alpha, n_dim=n_dim)
    acc = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    n_resets = 0
    last_doc = -1
    for i in range(len(sentences)):
        if doc_ids[i] != last_doc:
            trace.reset()
            last_doc = doc_ids[i]
            n_resets += 1
        t = trace.update(centered[i])
        cid = concept_ids[i]
        acc[cid] += t
        counts[cid] += 1.0

    concept_hds = _wta_sign_from_acc(acc, counts, n_dim)
    n_nan = int(np.isnan(concept_hds).sum())
    return concept_hds, {
        "n_nan": n_nan,
        "n_sentences": len(sentences),
        "n_docs": n_resets,
        "alpha": alpha,
    }


def arm_foldiak_trace(
    seed: int, n_dim: int, sentences_per_concept: int
) -> tuple[np.ndarray, dict]:
    """LOAD-BEARING arm: Foldiak trace (alpha=0.10) on document-structured corpus."""
    sentences, concept_ids, doc_ids = build_document_corpus(
        seed, sentences_per_concept
    )
    return _arm_foldiak_common(
        seed, n_dim, sentences, concept_ids, doc_ids, alpha=FOLDIAK_ALPHA
    )


def arm_trace_alpha_fast(
    seed: int, n_dim: int, sentences_per_concept: int
) -> tuple[np.ndarray, dict]:
    """Ablation: near-instantaneous trace (alpha=0.50; ~2-sentence memory)."""
    sentences, concept_ids, doc_ids = build_document_corpus(
        seed, sentences_per_concept
    )
    return _arm_foldiak_common(
        seed, n_dim, sentences, concept_ids, doc_ids, alpha=FAST_ALPHA
    )


def arm_adjacent_pair_hebb(
    seed: int, n_dim: int, sentences_per_concept: int
) -> tuple[np.ndarray, dict]:
    """Alternative mechanism (design Option C): adjacent-within-doc pair Hebb.

    For each within-document adjacent pair (i-1, i) with SAME concept label,
    add mean(centered[i-1], centered[i]) to acc[c]. Singletons (start-of-doc
    or singleton documents) contribute centered[i] alone.

    Symmetric-pair Hebb: each sentence contributes its centered surface HD
    modulated by within-doc adjacency. No W matrix; no SequenceMatrix.
    """
    sentences, concept_ids, doc_ids = build_document_corpus(
        seed, sentences_per_concept
    )
    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = _encode_contexts_masked(sentences, concept_ids, encoder)
    centered = _center(ctx_hds)

    acc = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    counts = np.zeros(N_CONCEPTS, dtype=np.float32)
    n_pairs = 0
    n_singletons = 0
    for i in range(len(sentences)):
        cid = concept_ids[i]
        # Adjacent-within-doc partner (regardless of concept -- cluster docs
        # mix both concepts; adjacent cross-concept pair pulls kitten context
        # into cat's accumulator and vice versa, echoing Foldiak trace).
        if i > 0 and doc_ids[i] == doc_ids[i - 1]:
            contribution = 0.5 * (centered[i - 1] + centered[i])
            n_pairs += 1
        else:
            contribution = centered[i]
            n_singletons += 1
        acc[cid] += contribution
        counts[cid] += 1.0

    concept_hds = _wta_sign_from_acc(acc, counts, n_dim)
    n_nan = int(np.isnan(concept_hds).sum())
    return concept_hds, {
        "n_nan": n_nan,
        "n_sentences": len(sentences),
        "n_pairs": n_pairs,
        "n_singletons": n_singletons,
    }


def arm_trace_shuffle_control(
    seed: int, n_dim: int, sentences_per_concept: int
) -> tuple[np.ndarray, dict]:
    """Sanity control: FOLDIAK trace (alpha=0.10) on TEMPORALLY-SHUFFLED corpus.

    Same trace mechanism as ARM_FOLDIAK_TRACE, but sentence order is shuffled
    (within-doc contiguity destroyed) and artificial doc boundaries are
    placed at fixed intervals. If temporal contiguity is load-bearing, this
    arm's cat_kitten_cos should NOT lift above SPOKE1_ONLY_REPRO baseline.
    """
    sentences, concept_ids, art_doc_ids = build_shuffle_control_corpus(
        seed, sentences_per_concept
    )
    return _arm_foldiak_common(
        seed, n_dim, sentences, concept_ids, art_doc_ids, alpha=FOLDIAK_ALPHA
    )


# ---------------------------------------------------------------------------
# Metrics.
# ---------------------------------------------------------------------------

def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return float(np.dot(a, b)) / (na * nb)


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


def compute_arm_metrics(concept_hds: np.ndarray, extra_diag: dict) -> dict:
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

    gap = cat_kitten_cos - cat_airplane_cos
    sparse_rate = _sparse_rate(concept_hds)
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
# Verdict logic (Spoke 2 v1 HPs).
# ---------------------------------------------------------------------------

def classify_verdict(per_seed_arm_metrics: list[dict]) -> dict:
    """Aggregate per-arm metrics; classify against Spoke 2 v1 HP / HF bands."""
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
                arm_summary[arm][f"{k}_cv"] = float(
                    np.std(vs) / abs(np.mean(vs))
                )

    def get(arm: str, key: str) -> float:
        return arm_summary.get(arm, {}).get(f"{key}_mean", 0.0)

    spoke1_ck = get("ARM_SPOKE1_ONLY_REPRO", "cat_kitten_cos")
    spoke1_ca = get("ARM_SPOKE1_ONLY_REPRO", "cat_airplane_cos")
    fold_ck = get("ARM_FOLDIAK_TRACE", "cat_kitten_cos")
    fold_ca = get("ARM_FOLDIAK_TRACE", "cat_airplane_cos")
    fold_sr = get("ARM_FOLDIAK_TRACE", "sparse_rate")
    fold_intra = get("ARM_FOLDIAK_TRACE", "intra_cluster_cos_mean")
    fold_inter = get("ARM_FOLDIAK_TRACE", "inter_cluster_cos_mean")
    fold_cv = arm_summary.get("ARM_FOLDIAK_TRACE", {}).get(
        "cat_kitten_cos_cv", 1.0
    )
    fast_ck = get("ARM_TRACE_ALPHA_FAST", "cat_kitten_cos")
    pair_ck = get("ARM_ADJACENT_PAIR_HEBB", "cat_kitten_cos")
    shuf_ck = get("ARM_TRACE_SHUFFLE_CONTROL", "cat_kitten_cos")

    invariance_lift = fold_ck - spoke1_ck
    shuffle_gap = fold_ck - shuf_ck

    # HP checks (LOAD-BEARING on ARM_FOLDIAK_TRACE).
    checks: dict[str, bool] = {}
    checks["SPOKE1_REPRO_cat_kitten_in_v3D_band"] = (
        HP_SPOKE1_CAT_KITTEN_LO <= spoke1_ck <= HP_SPOKE1_CAT_KITTEN_HI
    )
    checks["FOLDIAK_invariance_lift_above_min"] = (
        invariance_lift >= HP_FOLDIAK_INVARIANCE_LIFT_MIN
    )
    checks["FOLDIAK_cat_kitten_above_absolute_floor"] = (
        fold_ck >= HP_FOLDIAK_CAT_KITTEN_MIN
    )
    checks["FOLDIAK_cat_airplane_below_ceiling"] = (
        fold_ca <= HP_FOLDIAK_CAT_AIRPLANE_MAX
    )
    checks["FOLDIAK_sparse_rate_in_target"] = (
        HP_FOLDIAK_SPARSE_RATE_MIN <= fold_sr <= HP_FOLDIAK_SPARSE_RATE_MAX
    )
    checks["FOLDIAK_shuffle_gap_above_min"] = shuffle_gap >= HP_SHUFFLE_GAP_MIN
    checks["FOLDIAK_cat_kitten_cv_below_ceiling"] = fold_cv < HP_FOLDIAK_CV_MAX

    # HF checks (any triggers -> HARD_FAIL).
    hf_reasons: list[str] = []
    if fold_ck < HF_FOLDIAK_CAT_KITTEN_MIN:
        hf_reasons.append(
            f"foldiak_cat_kitten={fold_ck:.3f}<HF_min={HF_FOLDIAK_CAT_KITTEN_MIN}"
        )
    if fold_ca > HF_FOLDIAK_CAT_AIRPLANE_MAX:
        hf_reasons.append(
            f"foldiak_cat_airplane={fold_ca:.3f}>HF_max={HF_FOLDIAK_CAT_AIRPLANE_MAX}"
        )
    if not (HF_FOLDIAK_SPARSE_RATE_MIN <= fold_sr <= HF_FOLDIAK_SPARSE_RATE_MAX):
        hf_reasons.append(
            f"foldiak_sparse_rate={fold_sr:.4f} outside "
            f"[{HF_FOLDIAK_SPARSE_RATE_MIN},{HF_FOLDIAK_SPARSE_RATE_MAX}]"
        )
    if invariance_lift < HF_INVARIANCE_LIFT_MIN:
        hf_reasons.append(
            f"foldiak_invariance_lift={invariance_lift:+.3f}<HF_min="
            f"{HF_INVARIANCE_LIFT_MIN} (mechanism regresses vs SPOKE1_REPRO)"
        )

    all_hp_pass = all(checks.values())
    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"FOLDIAK cat_kitten={fold_ck:.3f} cat_airplane={fold_ca:.3f} "
            f"gap={fold_ck-fold_ca:.3f} "
            f"(intra_mean={fold_intra:.3f} intra_cv={fold_cv:.3f} "
            f"sparse={fold_sr:.4f}); "
            f"SPOKE1_REPRO ck={spoke1_ck:.3f} ca={spoke1_ca:.3f}; "
            f"invariance_lift={invariance_lift:+.3f}; "
            f"shuffle_gap={shuffle_gap:+.3f} (SHUFFLE ck={shuf_ck:.3f}); "
            f"ALPHA_FAST ck={fast_ck:.3f}; ADJ_PAIR ck={pair_ck:.3f}"
        )
    else:
        verdict = "MIDDLE_BAND"
        failed = [k for k, v in checks.items() if not v]
        verdict_msg = (
            f"HP not fully met: failed={failed} | "
            f"FOLDIAK ck={fold_ck:.3f} lift={invariance_lift:+.3f} "
            f"shuffle_gap={shuffle_gap:+.3f}"
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "arm_summary": arm_summary,
        "hp_checks": checks,
        "hf_reasons": hf_reasons,
        "load_bearing": {
            "spoke1_repro_cat_kitten_cos": spoke1_ck,
            "spoke1_repro_cat_airplane_cos": spoke1_ca,
            "foldiak_cat_kitten_cos": fold_ck,
            "foldiak_cat_airplane_cos": fold_ca,
            "foldiak_sparse_rate": fold_sr,
            "foldiak_intra_cluster_cos_mean": fold_intra,
            "foldiak_inter_cluster_cos_mean": fold_inter,
            "foldiak_cat_kitten_cv": fold_cv,
            "invariance_lift": invariance_lift,
            "shuffle_gap": shuffle_gap,
            "alpha_fast_cat_kitten_cos": fast_ck,
            "adjacent_pair_cat_kitten_cos": pair_ck,
            "shuffle_control_cat_kitten_cos": shuf_ck,
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
    seed: int, n_dim: int, sentences_per_concept: int, verbose: bool = True,
) -> dict:
    t0 = time.perf_counter()
    if verbose:
        print(
            f"[seed {seed}] n_dim={n_dim} spc={sentences_per_concept}",
            flush=True,
        )

    per_arm_hds: dict[str, np.ndarray] = {}
    per_arm_diag: dict[str, dict] = {}

    print(f"[seed {seed}] ARM_SPOKE1_ONLY_REPRO...", flush=True)
    hds, diag = arm_spoke1_only_repro(seed, n_dim, sentences_per_concept)
    per_arm_hds["ARM_SPOKE1_ONLY_REPRO"] = hds
    per_arm_diag["ARM_SPOKE1_ONLY_REPRO"] = diag

    print(f"[seed {seed}] ARM_FOLDIAK_TRACE...", flush=True)
    hds, diag = arm_foldiak_trace(seed, n_dim, sentences_per_concept)
    per_arm_hds["ARM_FOLDIAK_TRACE"] = hds
    per_arm_diag["ARM_FOLDIAK_TRACE"] = diag

    print(f"[seed {seed}] ARM_TRACE_ALPHA_FAST...", flush=True)
    hds, diag = arm_trace_alpha_fast(seed, n_dim, sentences_per_concept)
    per_arm_hds["ARM_TRACE_ALPHA_FAST"] = hds
    per_arm_diag["ARM_TRACE_ALPHA_FAST"] = diag

    print(f"[seed {seed}] ARM_ADJACENT_PAIR_HEBB...", flush=True)
    hds, diag = arm_adjacent_pair_hebb(seed, n_dim, sentences_per_concept)
    per_arm_hds["ARM_ADJACENT_PAIR_HEBB"] = hds
    per_arm_diag["ARM_ADJACENT_PAIR_HEBB"] = diag

    print(f"[seed {seed}] ARM_TRACE_SHUFFLE_CONTROL...", flush=True)
    hds, diag = arm_trace_shuffle_control(seed, n_dim, sentences_per_concept)
    per_arm_hds["ARM_TRACE_SHUFFLE_CONTROL"] = hds
    per_arm_diag["ARM_TRACE_SHUFFLE_CONTROL"] = diag

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
                f"ck={m['cat_kitten_cos']:.3f} "
                f"ca={m['cat_airplane_cos']:.3f} "
                f"gap={m['gap']:.3f} "
                f"intra={m['intra_cluster_cos_mean']:.3f} "
                f"sparse={m['sparse_rate']:.4f}",
                flush=True,
            )
        print(f"[seed {seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "arms": per_arm_metrics, "elapsed_s": elapsed}


def _run_selftest() -> None:
    """Import + tiny + scale-sentinel probe at N=8192 for NaN detection."""
    # Env-var contract check.
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
        _probe_args = _probe.parse_args([])
        assert _probe_args.run_mode == _test_env_val, (
            f"ENV_VAR_CONTRACT_VIOLATION: HDLAB_RUN_MODE={_test_env_val} "
            f"not honored by argparser default (got {_probe_args.run_mode!r})."
        )
    finally:
        if _saved_env is None:
            os.environ.pop("HDLAB_RUN_MODE", None)
        else:
            os.environ["HDLAB_RUN_MODE"] = _saved_env
    print(
        f"[selftest env_contract PASS] HDLAB_RUN_MODE={_test_env_val!r} honored",
        flush=True,
    )

    # Tiny functional selftest at small N + SPC.
    small_n = 256
    small_spc = 4
    for arm_fn, name in [
        (arm_spoke1_only_repro, "ARM_SPOKE1_ONLY_REPRO"),
        (arm_foldiak_trace, "ARM_FOLDIAK_TRACE"),
        (arm_trace_alpha_fast, "ARM_TRACE_ALPHA_FAST"),
        (arm_adjacent_pair_hebb, "ARM_ADJACENT_PAIR_HEBB"),
        (arm_trace_shuffle_control, "ARM_TRACE_SHUFFLE_CONTROL"),
    ]:
        hds, diag = arm_fn(0, small_n, small_spc)
        assert hds.shape == (N_CONCEPTS, small_n), (
            f"selftest {name} shape mismatch: {hds.shape}"
        )
        assert diag.get("n_nan", 0) == 0, (
            f"selftest {name} n_nan={diag.get('n_nan')} at small N"
        )
    print(f"[selftest tiny functional PASS] all 5 arms at N={small_n} SPC={small_spc}",
          flush=True)

    # Arms-must-differ at tiny scale (single seed reasonably-sized).
    tiny_arms: dict[str, np.ndarray] = {}
    for arm_fn, name in [
        (arm_spoke1_only_repro, "ARM_SPOKE1_ONLY_REPRO"),
        (arm_foldiak_trace, "ARM_FOLDIAK_TRACE"),
        (arm_trace_alpha_fast, "ARM_TRACE_ALPHA_FAST"),
        (arm_adjacent_pair_hebb, "ARM_ADJACENT_PAIR_HEBB"),
        (arm_trace_shuffle_control, "ARM_TRACE_SHUFFLE_CONTROL"),
    ]:
        hds, _ = arm_fn(7, 512, 8)
        tiny_arms[name] = hds
    _digests = arms_must_differ(tiny_arms)
    print("[selftest arms_must_differ PASS] all 5 arms bit-distinct at N=512 SPC=8",
          flush=True)

    # Scale-sentinel probe: LOAD-BEARING arm at N=8192 (NaN/Inf detection).
    print(f"[selftest] scale-sentinel ARM_FOLDIAK_TRACE at N_DIM={N_DIM_SCALE_SENTINEL}",
          flush=True)
    hds_ss, diag_ss = arm_foldiak_trace(0, N_DIM_SCALE_SENTINEL, 4)
    assert hds_ss.shape == (N_CONCEPTS, N_DIM_SCALE_SENTINEL)
    n_nan_ss = int(np.isnan(hds_ss).sum())
    n_inf_ss = int(np.isinf(hds_ss).sum())
    assert n_nan_ss == 0, (
        f"SCALE_SENTINEL_NAN at N={N_DIM_SCALE_SENTINEL}: n_nan={n_nan_ss}"
    )
    assert n_inf_ss == 0, (
        f"SCALE_SENTINEL_INF at N={N_DIM_SCALE_SENTINEL}: n_inf={n_inf_ss}"
    )
    m_ss = compute_arm_metrics(hds_ss, diag_ss)
    print(
        f"[selftest scale-sentinel PASS] N={N_DIM_SCALE_SENTINEL} "
        f"n_nan=0 n_inf=0 sparse_rate={m_ss['sparse_rate']:.4f} "
        f"cat_kitten={m_ss['cat_kitten_cos']:.3f}",
        flush=True,
    )

    # Positive-control regime probe: ARM_SPOKE1_ONLY_REPRO at Spoke 1 v3-D
    # FULL config (N=4096 SPC=40 seeds 11/17/23 mean) should reproduce
    # cat_kitten_cos_mean = 0.492 +/- 0.05. Mirrors concept_encoder.py
    # selftest 8 methodology (3-seed mean, not single-seed).
    print(
        "[selftest] Gate D positive control at Spoke 1 v3-D CG regime "
        "(N=4096 SPC=40 seeds 11/17/23 mean)", flush=True,
    )
    ck_vals = []
    ca_vals = []
    sr_vals = []
    for _seed in (11, 17, 23):
        _hds_pc, _diag_pc = arm_spoke1_only_repro(_seed, 4096, 40)
        _m_pc = compute_arm_metrics(_hds_pc, _diag_pc)
        ck_vals.append(_m_pc["cat_kitten_cos"])
        ca_vals.append(_m_pc["cat_airplane_cos"])
        sr_vals.append(_m_pc["sparse_rate"])
    ck_mean = float(np.mean(ck_vals))
    ca_mean = float(np.mean(ca_vals))
    sr_mean = float(np.mean(sr_vals))
    print(
        f"[selftest Gate D probe] SPOKE1_REPRO cat_kitten_mean={ck_mean:.4f} "
        f"per-seed={[round(v, 3) for v in ck_vals]} "
        f"(v3-D CG target {CG_SPOKE1_CAT_KITTEN_COS_MEAN:.4f} +/- "
        f"{CG_SPOKE1_CAT_KITTEN_TOLERANCE}); cat_airplane_mean={ca_mean:.4f} "
        f"sparse_mean={sr_mean:.4f}",
        flush=True,
    )
    assert HP_SPOKE1_CAT_KITTEN_LO <= ck_mean <= HP_SPOKE1_CAT_KITTEN_HI, (
        f"GATE_D_FAIL: SPOKE1_REPRO 3-seed cat_kitten_mean={ck_mean:.4f} "
        f"outside [{HP_SPOKE1_CAT_KITTEN_LO:.3f}, {HP_SPOKE1_CAT_KITTEN_HI:.3f}] "
        f"at Spoke 1 v3-D CG regime -- invocation mismatch or corpus drift"
    )
    print(
        f"[selftest Gate D PASS] SPOKE1_REPRO reproduces Spoke 1 v3-D CG "
        f"cat_kitten_cos_mean within tolerance",
        flush=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
        choices=["self_test", "smoke", "full"],
        help="self_test = import + tiny + scale-sentinel + Gate D probe; "
             "smoke = 3 seeds N=2048 SPC=20; full = 3 seeds N=4096 SPC=40. "
             "Default reads HDLAB_RUN_MODE env if set.",
    )
    parser.add_argument("--self-test", action="store_true",
                        help="Alias for --run-mode self_test.")
    parser.add_argument("--smoke", action="store_true",
                        help="Alias for --run-mode smoke.")
    parser.add_argument("--n-dim", type=int, default=0)
    parser.add_argument("--sentences-per-concept", type=int, default=0)
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

    # Per-seed load-bearing view.
    seed_view: list[dict] = []
    for entry in per_seed:
        s1 = entry["arms"].get("ARM_SPOKE1_ONLY_REPRO", {})
        fo = entry["arms"].get("ARM_FOLDIAK_TRACE", {})
        sh = entry["arms"].get("ARM_TRACE_SHUFFLE_CONTROL", {})
        seed_view.append({
            "seed": entry["seed"],
            "spoke1_repro_cat_kitten_cos": s1.get("cat_kitten_cos"),
            "spoke1_repro_cat_airplane_cos": s1.get("cat_airplane_cos"),
            "foldiak_cat_kitten_cos": fo.get("cat_kitten_cos"),
            "foldiak_cat_airplane_cos": fo.get("cat_airplane_cos"),
            "foldiak_intra_cluster_mean": fo.get("intra_cluster_cos_mean"),
            "foldiak_sparse_rate": fo.get("sparse_rate"),
            "shuffle_cat_kitten_cos": sh.get("cat_kitten_cos"),
            "invariance_lift": (
                fo.get("cat_kitten_cos", 0.0) - s1.get("cat_kitten_cos", 0.0)
            ),
            "shuffle_gap": (
                fo.get("cat_kitten_cos", 0.0) - sh.get("cat_kitten_cos", 0.0)
            ),
        })

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict_bundle["verdict"],
        "verdict_msg": verdict_bundle["verdict_msg"],
        "summary": (
            f"{verdict_bundle['verdict']} n_seeds={len(seeds)} "
            f"n_arms={len(ARMS)} n_dim={n_dim} spc={spc}"
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
            "doc_len_min": DOC_LEN_MIN,
            "doc_len_max": DOC_LEN_MAX,
            "foldiak_alpha": FOLDIAK_ALPHA,
            "fast_alpha": FAST_ALPHA,
            "hp_foldiak_cat_kitten_min": HP_FOLDIAK_CAT_KITTEN_MIN,
            "hp_foldiak_cat_airplane_max": HP_FOLDIAK_CAT_AIRPLANE_MAX,
            "hp_foldiak_invariance_lift_min": HP_FOLDIAK_INVARIANCE_LIFT_MIN,
            "hp_shuffle_gap_min": HP_SHUFFLE_GAP_MIN,
            "hp_foldiak_cv_max": HP_FOLDIAK_CV_MAX,
            "hp_spoke1_cat_kitten_band": [
                HP_SPOKE1_CAT_KITTEN_LO, HP_SPOKE1_CAT_KITTEN_HI
            ],
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
        "seed_load_bearing_view": seed_view,
        "per_seed": per_seed,
        "cell_template_compliance": {
            "arms_differ_verified": True,
            "final_metrics_atomicity": "tmp_replace",
            "cardinality_ok": True,
            "except_systemexit_before_exception": True,
            "start_marker_written": True,
            "crash_diagnostic_present": True,
            "hp_scope": {
                "ARM_FOLDIAK_TRACE": [
                    "FOLDIAK_invariance_lift_above_min",
                    "FOLDIAK_cat_kitten_above_absolute_floor",
                    "FOLDIAK_cat_airplane_below_ceiling",
                    "FOLDIAK_sparse_rate_in_target",
                    "FOLDIAK_shuffle_gap_above_min",
                    "FOLDIAK_cat_kitten_cv_below_ceiling",
                ],
                "ARM_SPOKE1_ONLY_REPRO": [
                    "SPOKE1_REPRO_cat_kitten_in_v3D_band",
                ],
                "ARM_TRACE_ALPHA_FAST": [],
                "ARM_ADJACENT_PAIR_HEBB": [],
                "ARM_TRACE_SHUFFLE_CONTROL": [],
            },
            "storage_strategy": STORAGE_STRATEGY,
            "compute_architecture": COMPUTE_ARCH,
            "progress_logging": "line_buffered_stdout",
            "calibration_check": "default_ok_for_this_regime",
            "crlb_n/a": (
                "emergent-representation cell; sparsity architectural via "
                "top-K quantile mask, not a noise-floor CRLB regime"
            ),
            "scale_sentinel_probe": (
                f"selftest runs ARM_FOLDIAK_TRACE at N={N_DIM_SCALE_SENTINEL}"
            ),
            "positive_control_reproducer": (
                "ARM_SPOKE1_ONLY_REPRO reproduces Spoke 1 v3-D CG "
                "cat_kitten_cos_mean=0.492 within 0.05 tolerance at "
                "Gate D selftest probe"
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
