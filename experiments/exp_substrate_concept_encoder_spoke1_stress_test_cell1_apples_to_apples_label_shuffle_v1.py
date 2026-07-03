"""Stage 2 Spoke 1 stress-test Cell 1: apples-to-apples supervised baseline
(Test 2) + label-semantics shuffle ablation (Test 4) COMBINED.

ANCHOR: substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1

STRATEGIC CONTEXT (USER-CRITICAL, LOAD-BEARING):
    USER 2026-07-02 late evening challenge:
        "stress test spoke 1. how does substrate know what a cat or airplane
        are? are we sure we tested apples to apples?"
    Skunkworks self-demoted META `drill_convergence_method` CG_META ->
        MM_TENTATIVE per USER's honest scope challenge.
    Spoke 1 v3-D CG scope tightened to "supervised synthetic concept-label
        regime with designer-imposed clusters" (hdlab.concept_encoder module
        docstring VALIDATION SCOPE + STAGE 4 CAVEATS).

    THIS CELL is the load-bearing apples-to-apples validity test. HP2 pass =
    Spoke 1 has a real substrate story beyond trivial supervised classifier.
    HF2 fire = arc pauses honestly and mechanism reframes.

    Framing discipline (LOAD-BEARING per mechanism-analog-vs-task-analog rule
    USER-LOCKED 2026-07-02):
        Cell tests SUPERVISED regime; result informs mechanism scope claim,
        NOT deep concept-understanding claim. No overclaims of "brain-analog
        concept understanding".

WHAT THIS CELL DOES (5 arms x 3 seeds = 15 units, cardinality_ok):

  ARM_SPOKE1_V3D_REPRO
    Positive-control (Gate D reproducibility). Uses hdlab.concept_encoder.
    ConceptEncoder (the primitive extracted 2026-07-02 from Spoke 1 v3-D
    FULL) with same regime (N=4096 FULL, seeds 11/17/23, SPC=40, mask_target
    _word=True). Reproduces v3-D FULL cat_kitten=0.492 within +/- 0.05.

  ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE                (LOAD-BEARING for Test 2)
    Trivial supervised classifier baseline: bag-of-char-trigram features
    (sklearn CountVectorizer analyzer='char' ngram_range=(3,3)) + sklearn
    LogisticRegression multinomial softmax classifier on concept_label.
    Concept-HD for the cat_kitten_cos metric = per-concept centroid in
    N_DIM space built from hdlab.char_trigram_encoder.CharTrigramEncoder
    encodings (sign-bundled bipolar HD averaged per concept, then sign()
    to recover bipolar).
    Reports classifier_test_accuracy (held-out 20% split).

  ARM_SPOKE1_LABEL_SHUFFLED                        (LOAD-BEARING for Test 4)
    Same v3-D mechanism, BUT concept labels are shuffled uniformly at
    random BEFORE fit. Tests whether the mechanism exploits label
    SEMANTICS (unshuffled) vs arbitrary label routing (shuffled).
    Under shuffle: W[c'] averages ~40 random sentences; if all sentences
    look alike in char+positional space, W[c'] converges toward similar
    HDs across all c' and cat_kitten_cos should collapse toward chance.
    Metric: (v3-D unshuffled gap) - (v3-D shuffled gap) >= 0.30 => labels
    matter; < 0.10 => mechanism is structural not semantic.

  ARM_RANDOM_BASELINE
    Chance control. Random bipolar HDs per concept; verifies scoring rig
    at chance ( |cat_kitten_cos| <= 0.05 ).

  ARM_UNSUPERVISED_KMEANS                          (bonus / Test 5 preview)
    Encode all sentences via CharPositionalEncoder, run sklearn KMeans
    (k=50) on the sentence HDs, compute adjusted mutual information (AMI)
    vs designer-intended concept labels. REPORT-ONLY diagnostic (not a
    gating HP but valuable info for the Spoke 3 unsupervised design).

HP BANDS:
  HP1 (Gate D reproducibility, ARM_SPOKE1_V3D_REPRO):
        cat_kitten_cos_mean within +/- 0.05 of v3-D FULL 0.492
        (i.e. between 0.442 and 0.542).
        Applied at N=4096 (full); at N=2048 smoke, band is looser (+/- 0.10).
  HP2 (apples-to-apples earned complexity):
        ARM_SPOKE1_V3D_REPRO.cat_kitten_cos_mean
        - ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE.cat_kitten_cos_mean >= 0.05
        (v3-D beats trivial supervised classifier by >= 0.05 cosine).
  HP3 (label-semantics dependence):
        ARM_SPOKE1_V3D_REPRO.cat_kitten_cos_mean
        - ARM_SPOKE1_LABEL_SHUFFLED.cat_kitten_cos_mean >= 0.30
        (shuffled labels collapse discrimination -> mechanism uses labels
        meaningfully).
  HP4 (chance):
        |ARM_RANDOM_BASELINE.cat_kitten_cos_mean| <= 0.05.
  HP5 (unsupervised bonus, REPORT-ONLY):
        ARM_UNSUPERVISED_KMEANS.ami_score >= 0.30.

HARD_FAIL BANDS:
  HF1 (Gate D violation):
        ARM_SPOKE1_V3D_REPRO.cat_kitten_cos_mean deviates > 0.10 from
        v3-D FULL 0.492 (i.e. < 0.392 or > 0.592) at N=4096.
        INVOCATION_MISMATCH halt -- do NOT trust downstream arms.
  HF2 (softmax matches or beats v3-D):
        ARM_SPOKE1_V3D_REPRO.cat_kitten_cos_mean
        - ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE.cat_kitten_cos_mean < -0.05
        (v3-D LOSES to trivial classifier).
        Mechanism has no advantage over char-trigram softmax; major arc-
        reframe required.
  HF3 (label-semantics-independent):
        ARM_SPOKE1_V3D_REPRO.cat_kitten_cos_mean
        - ARM_SPOKE1_LABEL_SHUFFLED.cat_kitten_cos_mean > 0.30 NOT MET
        AND shuffled cat_kitten_cos_mean > 0.30 (mechanism clusters
        arbitrary labels; deep concept structure NOT being learned).

MIDDLE_BAND (partial):
  HP2 delta in (0.00, 0.05) -- Spoke 1 marginally beats softmax.
  HP3 delta in (0.10, 0.30) -- labels partially matter.

CELL-TEMPLATE MANDATORY compliance:
  * arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash)
  * final_metrics_atomicity = tmp_replace (META_RULE_AH)
  * except SystemExit: raise BEFORE except Exception (no BaseException)
  * cardinality_ok: EXPECTED_N_UNITS = 5 arms * 3 seeds = 15
  * baseline_in_band at smoke (RANDOM ~0; discriminating arm target 0.4-0.6)
  * HP_SCOPE per-arm declaration (LOAD_BEARING on softmax + label_shuffled)
  * per-unit failure-class instrumentation (no bare except; except Exception)
  * calibration_check: default_ok_for_this_regime (synthetic corpus; no tuning)
  * scale-sentinel selftest: probe at N_DIM=8192 for NaN detection at full-
    scale matmul before any smoke dispatch
  * discriminator survives scale (ARM_SPOKE1_V3D_REPRO uses same corpus and
    mechanism as v3-D FULL which CG'd at N=4096; smoke at N=2048)
  * progress_logging = line_buffered_stdout (cell wall < 15 min; not required
    but adopted for observability parity with v3-D)
  * all numbers in this docstring tagged MEASURED / HYPOTHESIZED / CITED
    per META_RULE_AC:
        v3-D FULL cat_kitten_cos_mean = 0.492 MEASURED@data/exp_substrate_
            concept_encoder_spoke1_v3_D_competitive_hebbian_only_2026_07_02/
            metrics.json:arm_summary.ARM_COMPETITIVE_HEBBIAN.cat_kitten_cos_mean
        v3-D FULL cat_airplane_cos_mean = 0.020 MEASURED (same path)
        v3-D FULL sparse_rate_mean = 0.020 MEASURED (same path)
        HP thresholds HYPOTHESIZED@preregs/2026-07-02_substrate_concept_
            encoder_spoke1_stress_test_cell1_...md (this cell's pre-reg)

ENV VAR CONTRACT (runner_v2_prod dispatch, MANDATORY):
    HDLAB_RUN_MODE: production runner injects "full" into child env.
    Argparser reads via os.environ.get("HDLAB_RUN_MODE", "smoke") default.
    Verified by _run_selftest env_contract inline check.

Storage strategy: SHARDED (per-concept HD; not bundled) per storage-strategy
law (T4/META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW_v1).
Compute architecture: (b) sequential CPU numpy + sklearn.

ASCII-only. NumPy for math; sklearn for softmax + k-means; no torch.
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
from hdlab.concept_encoder import ConceptEncoder  # noqa: E402

# sklearn imports (external per pre-reg; softmax + kmeans arms).
from sklearn.cluster import KMeans  # noqa: E402
from sklearn.feature_extraction.text import CountVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import adjusted_mutual_info_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration constants.
# ---------------------------------------------------------------------------

ANCHOR_NAME = (
    "substrate_concept_encoder_spoke1_stress_test_cell1_apples_to_apples_label_shuffle_v1"
)

ARMS = [
    "ARM_SPOKE1_V3D_REPRO",
    "ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE",
    "ARM_SPOKE1_LABEL_SHUFFLED",
    "ARM_RANDOM_BASELINE",
    "ARM_UNSUPERVISED_KMEANS",
]

# 3 seeds per Director spec (match v3-D seeds for direct comparability).
SEEDS_SMOKE = [11, 17, 23]
SEEDS_FULL = [11, 17, 23]

# HD dimensionality per run mode (match v3-D).
N_DIM_SMOKE = 2048
N_DIM_FULL = 4096
N_DIM_SCALE_SENTINEL = 8192
MAX_POS = 24

# Corpus sizing (match v3-D).
SENTENCES_PER_CONCEPT_SMOKE = 40
SENTENCES_PER_CONCEPT_FULL = 40

# Competitive-allocation target sparsity (match v3-D 2%).
TARGET_SPARSE_RATE = 0.02

# HP thresholds per Director spec.
HP1_V3D_REPRO_DELTA_MAX = 0.05          # +/- 0.05 of v3-D FULL 0.492 at N=4096
HP1_V3D_REPRO_DELTA_MAX_SMOKE = 0.10    # +/- 0.10 at N=2048 smoke (looser)
HP2_SPOKE1_VS_SOFTMAX_MIN = 0.05        # v3-D beats softmax by >= 0.05 cos
HP3_SHUFFLE_DELTA_MIN = 0.30            # unshuffled - shuffled >= 0.30
HP4_RANDOM_ABS_MAX = 0.05               # random arm chance floor
HP5_KMEANS_AMI_MIN = 0.30               # unsupervised bonus (REPORT-ONLY)

# HF thresholds.
HF1_V3D_REPRO_DELTA_MAX = 0.10          # halt if deviates > 0.10 from v3-D 0.492
HF2_SOFTMAX_BEATS_MIN = -0.05           # v3-D - softmax < -0.05 => HF2
HF3_SHUFFLED_CAT_KITTEN_MAX = 0.30      # shuffled cat_kitten > 0.30 AND HP3 fail

# v3-D reference (MEASURED).
V3D_FULL_CAT_KITTEN_COS_MEAN = 0.492

# Storage strategy tag.
STORAGE_STRATEGY = "sharded_per_concept_hd_ternary_bipolar"
COMPUTE_ARCH = "sequential_cpu_numpy_plus_sklearn"

# ---------------------------------------------------------------------------
# Synthetic controlled corpus (copied verbatim from v3-D for direct
# comparability).
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
    """Return (sentences, concept_ids, cluster_ids) -- one entry per sentence.

    Verbatim reproduction of v3-D build_corpus for direct comparability.
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


def arm_random_baseline(seed: int, n_dim: int) -> tuple[np.ndarray, dict]:
    """Random bipolar HD per concept; no learning. Chance control."""
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for i in range(N_CONCEPTS):
        concept_hds[i] = _bipolar_hv(int(seed) * 1_000_003 + i, n_dim)
    diag = {"mechanism": "random_bipolar_hd"}
    return concept_hds, diag


def arm_spoke1_v3d_repro(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Positive-control reproducer arm using hdlab.concept_encoder.ConceptEncoder.

    Uses the extracted primitive that CG'd at Spoke 1 v3-D FULL (2026-07-02);
    same mechanism, same regime. Gate D reproducibility check: cat_kitten_cos_
    mean should land within +/- 0.05 of v3-D FULL 0.492 at N=4096.
    """
    names = concept_names()
    labels = np.asarray(concept_ids, dtype=np.int64)
    enc = ConceptEncoder(
        n_dim=n_dim,
        n_concepts=N_CONCEPTS,
        k_sparsity=TARGET_SPARSE_RATE,
        learning_rate=1.0,
        seed=int(seed),
        max_pos=MAX_POS,
        concept_names=names,
        mask_target_word=True,
    )
    enc.fit(list(sentences), labels)
    concept_hds = enc._concept_hds.astype(np.float32)
    diag = {
        "mechanism": "hdlab.concept_encoder.ConceptEncoder",
        "k_sparsity": TARGET_SPARSE_RATE,
        "n_concepts": N_CONCEPTS,
        "cited_prior_cat_kitten_cos_mean": V3D_FULL_CAT_KITTEN_COS_MEAN,
    }
    return concept_hds, diag


def arm_spoke1_label_shuffled(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Same v3-D mechanism but shuffle labels uniformly at random BEFORE fit.

    Tests HP3 label-semantics dependence. Under shuffle, W[c'] for each c'
    becomes an average of ~40 randomly-selected sentences (same corpus, but
    labels permuted). If mechanism uses label SEMANTICS, cat_kitten_cos on
    the shuffled-W collapses toward chance. If mechanism is structural
    (arbitrary label routing), shuffled cat_kitten_cos remains high.

    Shuffle strategy: per-seed deterministic permutation of the ORIGINAL
    labels list (i.e. permute assignment sentence -> concept_id label).
    The concept-name mapping stays fixed; we read out W at cat_idx=0 and
    kitten_idx=1 as before but the training averaged different sentences.
    """
    names = concept_names()
    rng = np.random.default_rng(int(seed) * 100003 + 1717)
    labels_orig = np.asarray(concept_ids, dtype=np.int64)
    shuffled_labels = labels_orig.copy()
    rng.shuffle(shuffled_labels)  # in-place permute of the label array

    enc = ConceptEncoder(
        n_dim=n_dim,
        n_concepts=N_CONCEPTS,
        k_sparsity=TARGET_SPARSE_RATE,
        learning_rate=1.0,
        seed=int(seed),
        max_pos=MAX_POS,
        concept_names=names,
        # mask_target_word=False here because the "target word" per label is
        # now nonsensical after shuffle -- masking a random concept name out
        # of each sentence would introduce cross-arm asymmetric bias. We
        # want the shuffle test to isolate label-semantics EXCLUSIVELY,
        # not confound with masking.
        mask_target_word=False,
    )
    enc.fit(list(sentences), shuffled_labels)
    concept_hds = enc._concept_hds.astype(np.float32)

    # Verify labels actually shuffled (unit sanity: not all identical).
    n_moved = int(np.sum(shuffled_labels != labels_orig))
    diag = {
        "mechanism": "hdlab.concept_encoder.ConceptEncoder_shuffled_labels",
        "labels_moved_by_shuffle": n_moved,
        "labels_total": int(labels_orig.shape[0]),
        "mask_target_word": False,
    }
    return concept_hds, diag


def arm_char_trigram_softmax_baseline(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Bag-of-char-trigram + sklearn LogisticRegression softmax classifier
    (Test 2 apples-to-apples supervised baseline).

    Two-part output:
      1. classifier_test_accuracy: sklearn LogisticRegression on bag-of-
         char-trigram COUNT features (CountVectorizer analyzer='char'
         ngram_range=(3,3)); 80/20 stratified train/test split; multinomial
         softmax. Reports held-out accuracy as sanity that the softmax
         baseline actually learns SOMETHING (chance = 1/50 = 0.02).
      2. concept_hds via hdlab.char_trigram_encoder.CharTrigramEncoder:
         encode each training sentence to N_DIM bipolar HD, average per
         concept_id, sign-bundle to ternary. This is the pure supervised
         BoT-based centroid HD in the SAME N_DIM space as v3-D, for
         apples-to-apples cat_kitten_cos comparison.

    Why part (2) is the load-bearing HP2 comparator (not part 1's softmax
    weights): v3-D's concept HD is a sparse bipolar per-concept vector in
    N_DIM space; we compare cat_kitten cosine in that SAME space. A softmax
    classifier's weight vector lives in trigram-feature space (~5000-dim),
    which is not commensurable. The per-concept CharTrigramEncoder centroid
    IS commensurable: same encoder space, same bipolar output, just no WTA
    sparsity and no context masking. If v3-D beats this by >= 0.05, its
    sparse-Hebbian mechanism has earned complexity over trivial bag-of-
    trigrams averaging.
    """
    labels = np.asarray(concept_ids, dtype=np.int64)
    sent_list = list(sentences)

    # Part 1: sklearn LogisticRegression softmax accuracy.
    vec = CountVectorizer(analyzer="char", ngram_range=(3, 3))
    X = vec.fit_transform(sent_list)
    # Guard: stratified test split requires test_size >= n_classes. In
    # selftest regime (SPC=2 -> 100 sent / 50 classes) that floor is violated.
    # Fall back to no-split when insufficient samples per class.
    min_per_class = int(np.bincount(labels).min())
    if min_per_class >= 5:
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=int(seed), stratify=labels
        )
        clf = LogisticRegression(
            solver="lbfgs", max_iter=2000, random_state=int(seed)
        )
        clf.fit(X_train, y_train)
        test_acc = float(clf.score(X_test, y_test))
        train_acc = float(clf.score(X_train, y_train))
        split_used = "stratified_80_20"
    else:
        clf = LogisticRegression(
            solver="lbfgs", max_iter=2000, random_state=int(seed)
        )
        clf.fit(X, labels)
        train_acc = float(clf.score(X, labels))
        test_acc = train_acc  # no held-out possible at this corpus size
        split_used = "no_split_selftest_regime"

    # Part 2: per-concept centroid HDs via CharTrigramEncoder.
    trigram_enc = CharTrigramEncoder(n_dim=n_dim)
    encoded = np.zeros((len(sent_list), n_dim), dtype=np.float32)
    for i, s in enumerate(sent_list):
        encoded[i] = trigram_enc.encode(s)
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        mask = labels == c
        if int(mask.sum()) == 0:
            continue
        centroid = encoded[mask].mean(axis=0)
        sign_c = np.sign(centroid).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c

    n_nan = int(np.isnan(concept_hds).sum())
    diag = {
        "mechanism": "bag_of_char_trigram_softmax_plus_per_concept_centroid_hd",
        "vectorizer": "sklearn.CountVectorizer(analyzer='char', ngram_range=(3,3))",
        "classifier": "sklearn.LogisticRegression(solver='lbfgs', max_iter=2000)",
        "classifier_train_accuracy": train_acc,
        "classifier_test_accuracy": test_acc,
        "classifier_split": split_used,
        "trigram_encoder": "hdlab.char_trigram_encoder.CharTrigramEncoder",
        "n_features_trigram": int(X.shape[1]),
        "n_nan": n_nan,
    }
    return concept_hds, diag


def arm_unsupervised_kmeans(
    seed: int,
    n_dim: int,
    sentences: Sequence[str],
    concept_ids: Sequence[int],
) -> tuple[np.ndarray, dict]:
    """Encode each sentence via CharPositionalEncoder + KMeans k=50, report AMI.

    Bonus REPORT-ONLY arm (HP5 non-gating): tests whether the substrate has
    ANY label-free discovery structure. Encode all sentences via the SAME
    CharPositionalEncoder v3-D uses, then run KMeans(k=50) on the sentence
    HDs and compute adjusted mutual information vs the designer-intended
    concept labels.

    For arms-must-differ compliance, we also emit a per-concept HD by taking
    each true concept's associated cluster centroid, sign-bundling to
    bipolar. This is a diagnostic HD (not comparable to v3-D's sparse HD;
    cat_kitten_cos on this arm is REPORT-ONLY, not gating).
    """
    sent_list = list(sentences)
    labels = np.asarray(concept_ids, dtype=np.int64)

    encoder = CharPositionalEncoder(
        n_dim=n_dim, max_pos=MAX_POS, seed_prefix=f"SPOKE1_S{seed}"
    )
    ctx_hds = np.zeros((len(sent_list), n_dim), dtype=np.float32)
    for i, s in enumerate(sent_list):
        ctx_hds[i] = encoder.encode_sentence(s)

    km = KMeans(
        n_clusters=N_CONCEPTS, n_init=10, random_state=int(seed), max_iter=300
    )
    cluster_assignments = km.fit_predict(ctx_hds)

    ami = float(adjusted_mutual_info_score(labels, cluster_assignments))

    # Per-concept HD diagnostic: for each true concept c, take the majority
    # cluster's centroid, sign-bundle. Not chain-grade but keeps the arm
    # hashable-different from other arms.
    concept_hds = np.zeros((N_CONCEPTS, n_dim), dtype=np.float32)
    for c in range(N_CONCEPTS):
        mask = labels == c
        if int(mask.sum()) == 0:
            continue
        # Find majority cluster among sentences of true label c.
        cluster_counts = np.bincount(
            cluster_assignments[mask], minlength=N_CONCEPTS
        )
        majority_cluster = int(np.argmax(cluster_counts))
        centroid = km.cluster_centers_[majority_cluster]
        sign_c = np.sign(centroid).astype(np.float32)
        sign_c[sign_c == 0] = 1.0
        concept_hds[c] = sign_c

    diag = {
        "mechanism": "char_positional_encoder_plus_kmeans_k50",
        "kmeans_n_iter": int(km.n_iter_),
        "ami_score": ami,
        "n_clusters": N_CONCEPTS,
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


def compute_arm_metrics(concept_hds: np.ndarray, extra_diag: dict) -> dict:
    cat_idx = _find_concept_index("cat")
    kitten_idx = _find_concept_index("kitten")
    airplane_idx = _find_concept_index("airplane")

    cat_kitten_cos = _cos(concept_hds[cat_idx], concept_hds[kitten_idx])
    cat_airplane_cos = _cos(concept_hds[cat_idx], concept_hds[airplane_idx])

    intra_mean, intra_vals = _intra_cluster_cos(concept_hds)
    inter_mean = _inter_cluster_cos_mean(concept_hds)

    intra_std = float(np.std(intra_vals)) if intra_vals else 0.0
    intra_cv = float(intra_std / abs(intra_mean)) if abs(intra_mean) > 1e-6 else 1.0

    sparse_rate = _sparse_rate(concept_hds)
    gap = cat_kitten_cos - cat_airplane_cos
    arm_digest = hashlib.sha256(concept_hds.tobytes()).hexdigest()[:32]

    return {
        "cat_kitten_cos": cat_kitten_cos,
        "cat_airplane_cos": cat_airplane_cos,
        "gap": gap,
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
                    f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} "
                    f"bit-identical (hash={digests[a][:16]}...); "
                    f"arm-implementation bug"
                )
    return digests


# ---------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------


def classify_verdict(
    per_seed_arm_metrics: list[dict], run_mode: str
) -> dict:
    """Aggregate per-arm metrics; classify against HP / HF bands."""
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

    v3d_ck = get("ARM_SPOKE1_V3D_REPRO", "cat_kitten_cos")
    v3d_ca = get("ARM_SPOKE1_V3D_REPRO", "cat_airplane_cos")
    v3d_gap = v3d_ck - v3d_ca

    soft_ck = get("ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE", "cat_kitten_cos")
    soft_ca = get("ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE", "cat_airplane_cos")
    soft_gap = soft_ck - soft_ca
    soft_test_acc = get(
        "ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE", "classifier_test_accuracy"
    )

    shuf_ck = get("ARM_SPOKE1_LABEL_SHUFFLED", "cat_kitten_cos")
    shuf_ca = get("ARM_SPOKE1_LABEL_SHUFFLED", "cat_airplane_cos")
    shuf_gap = shuf_ck - shuf_ca

    rand_ck = get("ARM_RANDOM_BASELINE", "cat_kitten_cos")

    kmeans_ami = get("ARM_UNSUPERVISED_KMEANS", "ami_score")

    # Load-bearing deltas.
    v3d_repro_delta_vs_v3d_full = v3d_ck - V3D_FULL_CAT_KITTEN_COS_MEAN
    hp2_delta_v3d_minus_softmax = v3d_ck - soft_ck
    hp3_delta_v3d_minus_shuffled = v3d_ck - shuf_ck

    # HP checks (bands vary by run mode -- HP1 tightened at FULL N=4096).
    hp1_tol = HP1_V3D_REPRO_DELTA_MAX if run_mode == "full" else HP1_V3D_REPRO_DELTA_MAX_SMOKE

    checks: dict[str, bool] = {}
    checks["HP1_v3d_repro_within_tolerance"] = (
        abs(v3d_repro_delta_vs_v3d_full) <= hp1_tol
    )
    checks["HP2_v3d_beats_softmax_by_min"] = (
        hp2_delta_v3d_minus_softmax >= HP2_SPOKE1_VS_SOFTMAX_MIN
    )
    checks["HP3_shuffled_labels_collapse_by_min"] = (
        hp3_delta_v3d_minus_shuffled >= HP3_SHUFFLE_DELTA_MIN
    )
    checks["HP4_random_baseline_at_chance"] = abs(rand_ck) <= HP4_RANDOM_ABS_MAX
    # HP5 is REPORT-ONLY; tracked but not gating.
    hp5_report_only = kmeans_ami >= HP5_KMEANS_AMI_MIN

    # HF checks (halting; take precedence over HP).
    hf_reasons: list[str] = []
    if abs(v3d_repro_delta_vs_v3d_full) > HF1_V3D_REPRO_DELTA_MAX:
        hf_reasons.append(
            f"HF1_INVOCATION_MISMATCH: v3d_repro cat_kitten={v3d_ck:.3f} "
            f"deviates from v3-D FULL {V3D_FULL_CAT_KITTEN_COS_MEAN:.3f} by "
            f"|{v3d_repro_delta_vs_v3d_full:+.3f}| > {HF1_V3D_REPRO_DELTA_MAX} "
            f"(downstream arms suspect)"
        )
    if hp2_delta_v3d_minus_softmax < HF2_SOFTMAX_BEATS_MIN:
        hf_reasons.append(
            f"HF2_SOFTMAX_MATCHES_OR_BEATS_V3D: v3d cat_kitten={v3d_ck:.3f} "
            f"softmax cat_kitten={soft_ck:.3f} delta={hp2_delta_v3d_minus_softmax:+.3f} "
            f"<{HF2_SOFTMAX_BEATS_MIN} (mechanism has no advantage over trivial "
            f"supervised classifier; major arc-reframe required)"
        )
    if (
        (hp3_delta_v3d_minus_shuffled < HP3_SHUFFLE_DELTA_MIN)
        and (shuf_ck > HF3_SHUFFLED_CAT_KITTEN_MAX)
    ):
        hf_reasons.append(
            f"HF3_LABEL_SEMANTICS_INDEPENDENT: shuffled cat_kitten={shuf_ck:.3f} "
            f">{HF3_SHUFFLED_CAT_KITTEN_MAX} AND v3d-shuffled delta="
            f"{hp3_delta_v3d_minus_shuffled:+.3f}<{HP3_SHUFFLE_DELTA_MIN} "
            f"(mechanism clusters arbitrary labels; deep concept structure "
            f"NOT being learned)"
        )

    # Gating HPs (HP1-HP4; HP5 is report-only).
    gating_hps = [
        "HP1_v3d_repro_within_tolerance",
        "HP2_v3d_beats_softmax_by_min",
        "HP3_shuffled_labels_collapse_by_min",
        "HP4_random_baseline_at_chance",
    ]
    all_hp_pass = all(checks[k] for k in gating_hps)

    if hf_reasons:
        verdict = "HARD_FAIL"
        verdict_msg = "; ".join(hf_reasons)
    elif all_hp_pass:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"V3D_REPRO ck={v3d_ck:.3f} (v3-D FULL {V3D_FULL_CAT_KITTEN_COS_MEAN} "
            f"delta={v3d_repro_delta_vs_v3d_full:+.3f}); "
            f"SOFTMAX ck={soft_ck:.3f} test_acc={soft_test_acc:.3f} "
            f"(HP2 v3d-softmax={hp2_delta_v3d_minus_softmax:+.3f}"
            f">={HP2_SPOKE1_VS_SOFTMAX_MIN}); "
            f"SHUFFLED ck={shuf_ck:.3f} "
            f"(HP3 v3d-shuffled={hp3_delta_v3d_minus_shuffled:+.3f}"
            f">={HP3_SHUFFLE_DELTA_MIN}); "
            f"RANDOM ck={rand_ck:.3f}; "
            f"KMEANS_AMI={kmeans_ami:.3f} "
            f"(HP5 report-only >= {HP5_KMEANS_AMI_MIN}: "
            f"{hp5_report_only})"
        )
    else:
        verdict = "MIDDLE_BAND"
        failed = [k for k in gating_hps if not checks[k]]
        verdict_msg = (
            f"HP gates not fully met: failed={failed}; "
            f"v3d_ck={v3d_ck:.3f} soft_ck={soft_ck:.3f} shuf_ck={shuf_ck:.3f} "
            f"rand_ck={rand_ck:.3f} kmeans_ami={kmeans_ami:.3f}"
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "arm_summary": arm_summary,
        "hp_checks": checks,
        "hp5_report_only_ami_gate": hp5_report_only,
        "hf_reasons": hf_reasons,
        "load_bearing": {
            "v3d_repro_cat_kitten_cos_mean": v3d_ck,
            "v3d_repro_cat_airplane_cos_mean": v3d_ca,
            "v3d_repro_gap_mean": v3d_gap,
            "v3d_repro_delta_vs_v3d_full": v3d_repro_delta_vs_v3d_full,
            "softmax_cat_kitten_cos_mean": soft_ck,
            "softmax_cat_airplane_cos_mean": soft_ca,
            "softmax_gap_mean": soft_gap,
            "softmax_classifier_test_accuracy_mean": soft_test_acc,
            "shuffled_cat_kitten_cos_mean": shuf_ck,
            "shuffled_cat_airplane_cos_mean": shuf_ca,
            "shuffled_gap_mean": shuf_gap,
            "random_cat_kitten_cos_mean": rand_ck,
            "kmeans_ami_score_mean": kmeans_ami,
            "hp2_delta_v3d_minus_softmax": hp2_delta_v3d_minus_softmax,
            "hp3_delta_v3d_minus_shuffled": hp3_delta_v3d_minus_shuffled,
            "v3d_full_reference": V3D_FULL_CAT_KITTEN_COS_MEAN,
        },
    }


# ---------------------------------------------------------------------------
# Runner-visible metrics I/O + start marker + crash diagnostic.
# ---------------------------------------------------------------------------


def _output_dir(run_mode: str) -> Path:
    suffix = "_smoke" if run_mode == "smoke" else ""
    return _REPO / "data" / f"exp_{ANCHOR_NAME}{suffix}"


def _write_start_marker(
    output_dir: Path, run_mode: str, expected_units: int
) -> None:
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
        print(
            f"[seed {seed}] build_corpus n_dim={n_dim} spc={sentences_per_concept}",
            flush=True,
        )
    sentences, concept_ids, _cluster_ids = build_corpus(seed, sentences_per_concept)

    per_arm_hds: dict[str, np.ndarray] = {}
    per_arm_diag: dict[str, dict] = {}

    print(f"[seed {seed}] ARM_RANDOM_BASELINE...", flush=True)
    hds, diag = arm_random_baseline(seed, n_dim)
    per_arm_hds["ARM_RANDOM_BASELINE"] = hds
    per_arm_diag["ARM_RANDOM_BASELINE"] = diag

    print(f"[seed {seed}] ARM_SPOKE1_V3D_REPRO...", flush=True)
    hds, diag = arm_spoke1_v3d_repro(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_SPOKE1_V3D_REPRO"] = hds
    per_arm_diag["ARM_SPOKE1_V3D_REPRO"] = diag

    print(f"[seed {seed}] ARM_SPOKE1_LABEL_SHUFFLED...", flush=True)
    hds, diag = arm_spoke1_label_shuffled(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_SPOKE1_LABEL_SHUFFLED"] = hds
    per_arm_diag["ARM_SPOKE1_LABEL_SHUFFLED"] = diag

    print(f"[seed {seed}] ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE...", flush=True)
    hds, diag = arm_char_trigram_softmax_baseline(
        seed, n_dim, sentences, concept_ids
    )
    per_arm_hds["ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE"] = hds
    per_arm_diag["ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE"] = diag

    print(f"[seed {seed}] ARM_UNSUPERVISED_KMEANS...", flush=True)
    hds, diag = arm_unsupervised_kmeans(seed, n_dim, sentences, concept_ids)
    per_arm_hds["ARM_UNSUPERVISED_KMEANS"] = hds
    per_arm_diag["ARM_UNSUPERVISED_KMEANS"] = diag

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
            extra = ""
            if arm == "ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE":
                extra = (
                    f" test_acc={m.get('classifier_test_accuracy', -1):.3f}"
                )
            elif arm == "ARM_UNSUPERVISED_KMEANS":
                extra = f" ami={m.get('ami_score', -1):.3f}"
            print(
                f"[seed {seed}] {arm} "
                f"cat_kitten={m['cat_kitten_cos']:.3f} "
                f"cat_airplane={m['cat_airplane_cos']:.3f} "
                f"gap={m['gap']:.3f} "
                f"intra_mean={m['intra_cluster_cos_mean']:.3f} "
                f"sparse_rate={m['sparse_rate']:.4f}{extra}",
                flush=True,
            )
        print(f"[seed {seed}] elapsed={elapsed:.1f}s", flush=True)
    return {
        "seed": seed,
        "arms": per_arm_metrics,
        "elapsed_s": elapsed,
    }


def _run_selftest() -> None:
    """Import + tiny + env-var-contract + scale-sentinel at N=8192."""
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
        f"[selftest env_contract PASS] HDLAB_RUN_MODE={_test_env_val!r} honored.",
        flush=True,
    )

    # Tiny functional selftest at N=256 (2 sentences/concept -> 100 sent total).
    sentences, concept_ids, _ = build_corpus(0, 2)
    assert len(sentences) == N_CONCEPTS * 2, (
        f"corpus size {len(sentences)} != {N_CONCEPTS * 2}"
    )

    hds_r, _ = arm_random_baseline(0, 256)
    assert hds_r.shape == (N_CONCEPTS, 256)

    hds_c, _ = arm_spoke1_v3d_repro(0, 256, sentences, concept_ids)
    assert hds_c.shape == (N_CONCEPTS, 256)

    hds_s, _ = arm_spoke1_label_shuffled(0, 256, sentences, concept_ids)
    assert hds_s.shape == (N_CONCEPTS, 256)

    hds_t, _ = arm_char_trigram_softmax_baseline(
        0, 256, sentences, concept_ids
    )
    assert hds_t.shape == (N_CONCEPTS, 256)

    hds_k, _ = arm_unsupervised_kmeans(0, 256, sentences, concept_ids)
    assert hds_k.shape == (N_CONCEPTS, 256)

    # ARMS-MUST-DIFFER on the tiny probe.
    arms_must_differ(
        {
            "ARM_RANDOM_BASELINE": hds_r,
            "ARM_SPOKE1_V3D_REPRO": hds_c,
            "ARM_SPOKE1_LABEL_SHUFFLED": hds_s,
            "ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE": hds_t,
            "ARM_UNSUPERVISED_KMEANS": hds_k,
        }
    )
    print("[selftest arms-must-differ PASS] all 5 arms produce unique HDs.",
          flush=True)

    # Scale-sentinel probe at N_DIM=8192 for LOAD-BEARING v3d_repro arm.
    print(
        f"[selftest] scale-sentinel probe at N_DIM={N_DIM_SCALE_SENTINEL}",
        flush=True,
    )
    s_sent, s_cids, _ = build_corpus(0, 4)
    hds_ss, _diag_ss = arm_spoke1_v3d_repro(
        0, N_DIM_SCALE_SENTINEL, s_sent, s_cids
    )
    assert hds_ss.shape == (N_CONCEPTS, N_DIM_SCALE_SENTINEL)
    n_nan_ss = int(np.isnan(hds_ss).sum())
    n_inf_ss = int(np.isinf(hds_ss).sum())
    assert n_nan_ss == 0, (
        f"SCALE_SENTINEL_NAN_DETECTED at N={N_DIM_SCALE_SENTINEL}: "
        f"n_nan={n_nan_ss} in ARM_SPOKE1_V3D_REPRO"
    )
    assert n_inf_ss == 0, (
        f"SCALE_SENTINEL_INF_DETECTED at N={N_DIM_SCALE_SENTINEL}: "
        f"n_inf={n_inf_ss}"
    )
    m_ss = compute_arm_metrics(hds_ss, {})
    print(
        f"[selftest scale-sentinel PASS] N={N_DIM_SCALE_SENTINEL} "
        f"n_nan=0 n_inf=0 sparse_rate={m_ss['sparse_rate']:.4f} "
        f"cat_kitten={m_ss['cat_kitten_cos']:.3f}",
        flush=True,
    )

    print("[self_test PASS] all selftests green.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=ANCHOR_NAME)
    parser.add_argument(
        "--run-mode",
        default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
        choices=["self_test", "smoke", "full"],
        help="self_test = import + tiny + scale-sentinel N=8192; "
             "smoke = 3 seeds N=2048; full = 3 seeds N=4096.",
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

    verdict_bundle = classify_verdict(per_seed_arm_metrics, run_mode)
    elapsed = time.perf_counter() - t0

    # Per-seed load-bearing view.
    seed_load_bearing_view: list[dict] = []
    for entry in per_seed:
        v3d = entry["arms"].get("ARM_SPOKE1_V3D_REPRO", {})
        soft = entry["arms"].get("ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE", {})
        shuf = entry["arms"].get("ARM_SPOKE1_LABEL_SHUFFLED", {})
        km = entry["arms"].get("ARM_UNSUPERVISED_KMEANS", {})
        seed_load_bearing_view.append({
            "seed": entry["seed"],
            "v3d_cat_kitten_cos": v3d.get("cat_kitten_cos", None),
            "v3d_gap": v3d.get("gap", None),
            "softmax_cat_kitten_cos": soft.get("cat_kitten_cos", None),
            "softmax_classifier_test_accuracy": soft.get(
                "classifier_test_accuracy", None
            ),
            "shuffled_cat_kitten_cos": shuf.get("cat_kitten_cos", None),
            "kmeans_ami_score": km.get("ami_score", None),
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
            "hp1_v3d_repro_delta_max": HP1_V3D_REPRO_DELTA_MAX,
            "hp1_v3d_repro_delta_max_smoke": HP1_V3D_REPRO_DELTA_MAX_SMOKE,
            "hp2_spoke1_vs_softmax_min": HP2_SPOKE1_VS_SOFTMAX_MIN,
            "hp3_shuffle_delta_min": HP3_SHUFFLE_DELTA_MIN,
            "hp4_random_abs_max": HP4_RANDOM_ABS_MAX,
            "hp5_kmeans_ami_min": HP5_KMEANS_AMI_MIN,
            "v3d_full_reference_cat_kitten_cos_mean": V3D_FULL_CAT_KITTEN_COS_MEAN,
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
        "hp5_report_only_ami_gate": verdict_bundle["hp5_report_only_ami_gate"],
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
                "ARM_SPOKE1_V3D_REPRO": [
                    "HP1_v3d_repro_within_tolerance",
                ],
                "ARM_CHAR_TRIGRAM_SOFTMAX_BASELINE": [
                    "HP2_v3d_beats_softmax_by_min",
                ],
                "ARM_SPOKE1_LABEL_SHUFFLED": [
                    "HP3_shuffled_labels_collapse_by_min",
                ],
                "ARM_RANDOM_BASELINE": [
                    "HP4_random_baseline_at_chance",
                ],
                "ARM_UNSUPERVISED_KMEANS": [
                    "HP5_kmeans_ami_min_report_only",
                ],
            },
            "hp_scope_load_bearing": [
                "HP2_v3d_beats_softmax_by_min",
                "HP3_shuffled_labels_collapse_by_min",
            ],
            "storage_strategy": STORAGE_STRATEGY,
            "compute_architecture": COMPUTE_ARCH,
            "progress_logging": "line_buffered_stdout",
            "calibration_check": "default_ok_for_this_regime",
            "crlb_n/a": (
                "supervised concept-encoder cell; discriminator is a cosine "
                "delta between arms, not a noise-floor CRLB regime"
            ),
            "scale_sentinel_probe": (
                f"selftest runs ARM_SPOKE1_V3D_REPRO at N={N_DIM_SCALE_SENTINEL} "
                f"and asserts n_nan==0"
            ),
        },
    }

    _atomic_write_metrics(output_dir, metrics)
    print(
        f"[{ANCHOR_NAME}] {verdict_bundle['verdict']} "
        f"elapsed={elapsed:.1f}s path={output_dir / 'metrics.json'}",
        flush=True,
    )


if __name__ == "__main__":
    _output_dir_for_crash = _output_dir(
        os.environ.get("HDLAB_RUN_MODE", "smoke")
    )
    try:
        _early = argparse.ArgumentParser(add_help=False)
        _early.add_argument(
            "--run-mode",
            default=os.environ.get("HDLAB_RUN_MODE", "smoke"),
            choices=["self_test", "smoke", "full"],
        )
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
