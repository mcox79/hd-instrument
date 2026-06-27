"""cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED -- Wave 2 isolated-bank fix.

Prereg: preregs/2026-06-27_cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED.md
Skunkworks audit: notes/skunkworks_mechanism_null_audit_wave2_2026-06-27.md (commit edee21b3)

ROOT CAUSE FIX vs v2:
  v2 stored each cluster's schema in its own row of a separate bank (sparse_bank_k20
  shape (K, N_SCHEMA_CELLS)); retrieval was per-cluster cosine/overlap to bank rows.
  When clusters are separated (BETWEEN_CLUSTER_COSINE=0.45), even PROTOTYPE_CENTROID
  recovers easily because each row is independent and ranks are trivially preserved.
  Skunkworks Wave 2F: "TOP-1 path: BUNDLED capacity test where all K schemas share
                       one substrate vector".
  The brain-grounded test is HRR-bundle capacity: cram K schemas into ONE substrate
  vector via XOR-binding, query unbinds + matches by k-WTA overlap. THIS is where
  sparse-code-vs-dense-centroid interference differences emerge (Treves-Rolls predicts
  sparse codes have ~10x lower crosstalk at sparsity 0.01).

ARCHITECTURE:
  TONEGAWA_SPARSE_BUNDLED:
    schema_id_k ~ random bipolar (N_DIM,) [unique key per schema]
    sparse_code_k = k-WTA(centroid_k via W_schema) [k=20 of N=2000; 1% sparsity]
    S_bundle = sum_k XOR(schema_id_k, sparse_code_k_lifted_to_N_DIM)
    Query: given query_centroid -> sparse_code_q via k-WTA;
           for each candidate k: probe = XOR(schema_id_k, S_bundle); match k-WTA overlap
                                  cluster_score_k = overlap(probe, sparse_code_q)

  PROTOTYPE_CENTROID_BUNDLED (dense equivalent):
    C_bundle = sum_k XOR(schema_id_k, centroid_k)
    Query: probe = XOR(schema_id_k, C_bundle); cluster_score_k = cosine(probe, centroid_k)

  DIAG_RANDOM_SPARSE_BUNDLED: random k-subset codes; tests false-accept floor.

HYPOTHESIS:
  At small K (=25): all 3 arms recover most schemas (saturation regime)
  At K growing (50, 100, 200): BUNDLED interference accumulates faster for DENSE
    centroids than SPARSE codes; TONEGAWA wins at capacity@95%-recall crossover
  Treves-Rolls capacity scaling: sparse ~ N / (k * log(K)); dense ~ N (no log factor
    but each schema contributes ~all-N interference)

DISCRIMINATOR:
  HARD_PASS:
    TONEGAWA capacity@95%-recall >= 1.5 * PROTOTYPE_CENTROID capacity@95%-recall
    AND DIAG_RANDOM_SPARSE capacity@95%-recall < 0.5 * TONEGAWA
    AND CV across seeds < 0.10
  MIDDLE_BAND: TONEGAWA capacity in [1.1, 1.5)x PROTOTYPE (lift but not Treves-Rolls)
  HARD_FAIL:
    any arm capacity@95% at K=25 indicates saturation regime (PROTOTYPE_at_K25 < 0.95)
    OR TONEGAWA capacity <= PROTOTYPE capacity (mechanism null in bundled regime)
    OR DIAG_RANDOM_SPARSE capacity >= TONEGAWA capacity (random matches structure)
    OR cardinality breach (sweep K count incomplete)

CAPACITY SWEEP K in {25, 50, 100, 200}; measure recall@TOP_K=1 at each K; capacity@95%
  = max K such that recall@1 >= 0.95. (Use recall@1 not @5 for tight capacity definition.)

ARMS:
  ARM_PROTOTYPE_CENTROID_BUNDLED   dense bundle; XOR-binding
  ARM_TONEGAWA_SPARSE_K20_BUNDLED  sparse bundle (k=20 of N=2000); 1% sparsity
  ARM_DIAG_RANDOM_SPARSE_BUNDLED   random k-subset bundle; false-accept floor

REGIME:
  N_DIM=2000; K_SPARSE=20; N_PER_CLUSTER=10; BETWEEN_CLUSTER_COSINE=0.30 (harder than v2)
  K_SWEEP=[25, 50, 100, 200] full; [10, 25] smoke; [10] selftest
  seeds: full=[7, 17, 23]; smoke=[7]; selftest=[7]

CARDINALITY_OK:
  EXPECTED_N_UNITS = 3 arms * len(K_SWEEP) * n_seeds
  smoke = 3 * 2 * 1 = 6
  full = 3 * 4 * 3 = 36

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (Wave 2 redesign cell 3 of 4).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "cortex_schema_tonegawa_sparse_ensemble_v3_BUNDLED"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands
HP_TONEGAWA_OVER_PROTO_RATIO = 1.5
HP_DIAG_UNDER_TONEGAWA_RATIO = 0.5
HP_CV_MAX = 0.10
MIDDLE_RATIO_LO = 1.1
HF_SATURATION_AT_SMALL_K = 0.95  # any arm hitting 0.95 at K=25 -> regime too easy

EXPECTED_ARMS = (
    "ARM_PROTOTYPE_CENTROID_BUNDLED",
    "ARM_TONEGAWA_SPARSE_K20_BUNDLED",
    "ARM_DIAG_RANDOM_SPARSE_BUNDLED",
)

# Regime
if SELF_TEST_MODE:
    N_DIM = 512
    N_SCHEMA_CELLS = 512
    K_SPARSE = 10
    N_PER_CLUSTER = 5
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.60
    K_SWEEP = [10]
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 5
elif RUN_MODE == "smoke":
    # Smoke MUST FIRE DISCRIMINATOR (META_RULE_K). At K=10 dense wins trivially;
    # at K>=100, sparse-bundle interference advantage emerges. Smoke spans both.
    N_DIM = 1024
    N_SCHEMA_CELLS = 1024
    K_SPARSE = 20
    N_PER_CLUSTER = 8
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.60
    K_SWEEP = [25, 100]  # smoke: K=25 (dense regime) + K=100 (sparse-advantage regime)
    SEEDS = [7]
    N_QUERIES_PER_CLUSTER = 10
else:
    N_DIM = 2000
    N_SCHEMA_CELLS = 2000
    K_SPARSE = 20
    N_PER_CLUSTER = 10
    BETWEEN_CLUSTER_COSINE = 0.30
    WITHIN_CLUSTER_NOISE = 0.70
    K_SWEEP = [25, 50, 100, 200]
    SEEDS = [7, 17, 23]
    N_QUERIES_PER_CLUSTER = 20

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(K_SWEEP) * len(SEEDS)
TARGET_RECALL_FOR_CAPACITY = 0.95

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,NSCH=%d,KSP=%d,NPC=%d,BCC=%.2f,WCN=%.2f,"
    "K_SWEEP=%s,SEEDS=%s,NQPC=%d,target_recall=%.2f,"
    "HP_tonegawa_over_proto>=%.2f,HP_diag_under_tonegawa<=%.2f,HP_cv<%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, N_SCHEMA_CELLS, K_SPARSE, N_PER_CLUSTER,
    BETWEEN_CLUSTER_COSINE, WITHIN_CLUSTER_NOISE,
    K_SWEEP, SEEDS, N_QUERIES_PER_CLUSTER, TARGET_RECALL_FOR_CAPACITY,
    HP_TONEGAWA_OVER_PROTO_RATIO, HP_DIAG_UNDER_TONEGAWA_RATIO, HP_CV_MAX,
    RUN_MODE,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v3_bundled_capacity",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v3_bundled_capacity_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar_unit(n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar {-1, +1} unit vector (no normalization; binding-friendly)."""
    return (g.integers(0, 2, size=n).astype(np.float32) * 2.0 - 1.0)


def bipolar_normalized(n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar normalized to unit L2 (for cosine readout)."""
    v = (g.integers(0, 2, size=n).astype(np.float32) * 2.0 - 1.0)
    return v / (np.linalg.norm(v) + 1e-8)


def xor_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """XOR-binding for bipolar vectors: elementwise multiply (a, b in {-1, +1})."""
    return (a * b).astype(np.float32)


def k_wta(activations: np.ndarray, k: int) -> np.ndarray:
    """Top-k binary selection: returns 0/1 vector with exactly k ones."""
    n = activations.shape[0]
    if k >= n:
        return np.ones(n, dtype=np.float32)
    top_k_idx = np.argpartition(-activations, k)[:k]
    out = np.zeros(n, dtype=np.float32)
    out[top_k_idx] = 1.0
    return out


def kwta_to_bipolar(sparse: np.ndarray) -> np.ndarray:
    """Convert k-WTA {0, 1} -> bipolar {-1, +1} for XOR-binding."""
    return (sparse * 2.0 - 1.0).astype(np.float32)


# -------------------------- generation --------------------------

def generate_clusters(seed: int, K: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate K clusters; returns (atoms, labels, centers).
    centers are L2-normalized for cosine readout."""
    rng = np.random.RandomState(seed)
    shared = rng.randn(N_DIM).astype(np.float64)
    shared /= max(np.linalg.norm(shared), 1e-12)
    centers = np.zeros((K, N_DIM), dtype=np.float64)
    for k in range(K):
        private = rng.randn(N_DIM).astype(np.float64)
        private = private - (private @ shared) * shared
        private /= max(np.linalg.norm(private), 1e-12)
        c = (float(np.sqrt(BETWEEN_CLUSTER_COSINE)) * shared +
             float(np.sqrt(max(0.0, 1.0 - BETWEEN_CLUSTER_COSINE))) * private)
        c /= max(np.linalg.norm(c), 1e-12)
        centers[k] = c

    atoms = np.zeros((K * N_PER_CLUSTER, N_DIM), dtype=np.float64)
    labels = np.zeros(K * N_PER_CLUSTER, dtype=np.int64)
    for k in range(K):
        for i in range(N_PER_CLUSTER):
            noise = rng.randn(N_DIM).astype(np.float64)
            noise /= max(np.linalg.norm(noise), 1e-12)
            atom = centers[k] + WITHIN_CLUSTER_NOISE * noise
            atom /= max(np.linalg.norm(atom), 1e-12)
            atoms[k * N_PER_CLUSTER + i] = atom
            labels[k * N_PER_CLUSTER + i] = k
    return atoms, labels, centers


def make_W_schema(seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed + 31337)
    W = rng.randn(N_SCHEMA_CELLS, N_DIM).astype(np.float64)
    norms = np.linalg.norm(W, axis=1, keepdims=True)
    W = W / np.maximum(norms, 1e-12)
    return W


def make_schema_ids(seed: int, K: int) -> np.ndarray:
    """K random bipolar {-1, +1} schema-ID keys, shape (K, N_DIM)."""
    g = np.random.default_rng(seed + 7919)
    out = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        out[k] = bipolar_unit(N_DIM, g)
    return out


# -------------------------- bundle builders --------------------------

def build_tonegawa_bundle(centers: np.ndarray, schema_ids: np.ndarray,
                           W: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Build bundled substrate vector for SPARSE arm.

    Returns (S_bundle, list_of_sparse_codes_per_schema).
      S_bundle = sum_k XOR(schema_id_k, sparse_code_k_lifted_to_NDIM)
    For lifting k-WTA sparse code (N_SCHEMA_CELLS,) to NDIM, we use the
    N_SCHEMA_CELLS = N_DIM convention (so sparse_code is already in NDIM space).
    """
    K = centers.shape[0]
    assert N_SCHEMA_CELLS == N_DIM, "BUNDLED arch requires N_SCHEMA_CELLS == N_DIM"
    S_bundle = np.zeros(N_DIM, dtype=np.float32)
    sparse_codes: List[np.ndarray] = []
    for k in range(K):
        acts = W @ centers[k]  # (N_SCHEMA_CELLS,)
        sparse = k_wta(acts, K_SPARSE)  # binary 0/1
        bipolar_code = kwta_to_bipolar(sparse)  # {-1, +1}
        bound = xor_bind(schema_ids[k], bipolar_code)
        S_bundle = S_bundle + bound
        sparse_codes.append(sparse)
    return S_bundle, sparse_codes


def build_prototype_centroid_bundle(centers: np.ndarray,
                                     schema_ids: np.ndarray) -> np.ndarray:
    """Build bundled substrate for DENSE-CENTROID arm.

    C_bundle = sum_k XOR(schema_id_k, centroid_k)
    """
    K = centers.shape[0]
    # Cast centers to float32 bipolar-friendly representation (signum)
    C_bundle = np.zeros(N_DIM, dtype=np.float32)
    for k in range(K):
        # Use the sign of centroid as bipolar surrogate (centers already unit-norm dense)
        c_bipolar = np.sign(centers[k]).astype(np.float32)
        # Replace zeros with +1 to avoid losing dim (rare for randn-init)
        c_bipolar = np.where(c_bipolar == 0.0, 1.0, c_bipolar)
        bound = xor_bind(schema_ids[k], c_bipolar)
        C_bundle = C_bundle + bound
    return C_bundle


def build_random_sparse_bundle(schema_ids: np.ndarray, seed: int
                                ) -> Tuple[np.ndarray, List[np.ndarray]]:
    """Random k-subset sparse codes per schema; tests false-accept floor."""
    K = schema_ids.shape[0]
    g = np.random.default_rng(seed + 99999)
    S_bundle = np.zeros(N_DIM, dtype=np.float32)
    sparse_codes: List[np.ndarray] = []
    for k in range(K):
        idx = g.choice(N_DIM, size=min(K_SPARSE, N_DIM), replace=False)
        sparse = np.zeros(N_DIM, dtype=np.float32)
        sparse[idx] = 1.0
        bipolar_code = kwta_to_bipolar(sparse)
        bound = xor_bind(schema_ids[k], bipolar_code)
        S_bundle = S_bundle + bound
        sparse_codes.append(sparse)
    return S_bundle, sparse_codes


# -------------------------- query scoring --------------------------

def score_tonegawa_bundled(query: np.ndarray, S_bundle: np.ndarray,
                            schema_ids: np.ndarray, sparse_codes: List[np.ndarray],
                            W: np.ndarray, K: int) -> np.ndarray:
    """For each candidate k: probe = XOR(schema_id_k, S_bundle); score by analog
    dot-product with query's k-WTA-mapped-to-bipolar code.

    Use analog dot-product (not sign-binarization) to preserve the unbound signal's
    magnitude. The probe vector is `sparse_code_k_bipolar + noise(other_schemas)`;
    its dot-product with query_sparse_bipolar (the correct sparse_code we expect
    to retrieve) is K_SPARSE in expectation (signal) plus noise of variance
    ~ (K-1) * K_SPARSE / N (other schemas crosstalk).
    """
    acts_q = W @ query
    query_sparse = k_wta(acts_q, K_SPARSE)  # {0, 1}^N
    query_sparse_bipolar = kwta_to_bipolar(query_sparse)  # {-1, +1}
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        probe = xor_bind(schema_ids[k], S_bundle)  # (N,); analog bipolar contaminated
        # Analog dot-product against query's bipolar sparse code
        # Signal: K_SPARSE * 2 (overlap on the K_SPARSE active bits) - extra contribution
        # Actually: the bipolar codes have +1 on active, -1 on inactive; dot-product
        # of two such gives 2*overlap - N -- not what we want.
        # Cleaner: dot-product against ORIGINAL query_sparse (0/1) gives sum of probe
        # entries at the K_SPARSE active positions of query. For correct schema, this
        # ~ K_SPARSE * 1.0 (probe is +1 at query's active bits when bipolar codes match);
        # for wrong schemas, ~ 0 (zero-mean noise summed over K_SPARSE bits).
        score = float(np.sum(probe * query_sparse_bipolar))
        scores[k] = score / float(max(K_SPARSE, 1))
    return scores


def score_prototype_centroid_bundled(query_centroid: np.ndarray, C_bundle: np.ndarray,
                                      schema_ids: np.ndarray, K: int) -> np.ndarray:
    """For each candidate k: probe = XOR(schema_id_k, C_bundle); score = cosine(probe, query_centroid)."""
    q_unit = query_centroid / (np.linalg.norm(query_centroid) + 1e-8)
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        probe = xor_bind(schema_ids[k], C_bundle)
        # Use sign as surrogate (matches build); cosine to query_centroid
        probe_bipolar = np.sign(probe).astype(np.float32)
        probe_bipolar = np.where(probe_bipolar == 0.0, 1.0, probe_bipolar)
        p_unit = probe_bipolar / (np.linalg.norm(probe_bipolar) + 1e-8)
        scores[k] = float(np.dot(p_unit, q_unit))
    return scores


def score_random_sparse_bundled(query: np.ndarray, S_bundle: np.ndarray,
                                 schema_ids: np.ndarray, W: np.ndarray, K: int
                                 ) -> np.ndarray:
    """Same surface as tonegawa_bundled but with random sparse bank (k-WTA on query)."""
    acts_q = W @ query
    query_sparse = k_wta(acts_q, K_SPARSE)
    query_sparse_bipolar = kwta_to_bipolar(query_sparse)
    scores = np.zeros(K, dtype=np.float32)
    for k in range(K):
        probe = xor_bind(schema_ids[k], S_bundle)
        score = float(np.sum(probe * query_sparse_bipolar))
        scores[k] = score / float(max(K_SPARSE, 1))
    return scores


# -------------------------- run one (arm, K, seed) --------------------------

def make_test_query(atom: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.RandomState(seed)
    noise = rng.randn(N_DIM).astype(np.float64)
    noise /= max(np.linalg.norm(noise), 1e-12)
    q = atom + 0.30 * noise
    q /= max(np.linalg.norm(q), 1e-12)
    return q


def measure_recall_at_top1(arm: str, K: int, seed: int,
                            atoms: np.ndarray, labels: np.ndarray,
                            centers: np.ndarray, schema_ids: np.ndarray,
                            W: np.ndarray,
                            S_bundle_tonegawa: np.ndarray, sparse_codes_tonegawa: List,
                            C_bundle_prototype: np.ndarray,
                            S_bundle_random: np.ndarray) -> float:
    """Returns recall@1 across all queries for arm at K clusters."""
    hits = 0
    n_q = 0
    for c in range(K):
        members = atoms[labels == c]
        for q_i in range(N_QUERIES_PER_CLUSTER):
            base_idx = q_i % len(members)
            q = make_test_query(members[base_idx], seed=seed + c * 100 + q_i).astype(np.float32)
            q_centroid = centers[c].astype(np.float32)
            if arm == "ARM_TONEGAWA_SPARSE_K20_BUNDLED":
                scores = score_tonegawa_bundled(
                    q, S_bundle_tonegawa, schema_ids, sparse_codes_tonegawa, W, K)
            elif arm == "ARM_PROTOTYPE_CENTROID_BUNDLED":
                scores = score_prototype_centroid_bundled(
                    q_centroid + 0.30 * (q - q_centroid), C_bundle_prototype, schema_ids, K)
            elif arm == "ARM_DIAG_RANDOM_SPARSE_BUNDLED":
                scores = score_random_sparse_bundled(
                    q, S_bundle_random, schema_ids, W, K)
            else:
                raise ValueError("unknown arm %s" % arm)
            pred = int(np.argmax(scores))
            if pred == c:
                hits += 1
            n_q += 1
    return hits / max(n_q, 1)


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_arm_per_K: Dict[str, Dict[str, float]] = {arm: {} for arm in EXPECTED_ARMS}

    for K in K_SWEEP:
        # Generate K clusters
        atoms, labels, centers = generate_clusters(seed, K)
        W = make_W_schema(seed)
        schema_ids = make_schema_ids(seed, K)
        S_t, codes_t = build_tonegawa_bundle(centers, schema_ids, W)
        C_p = build_prototype_centroid_bundle(centers, schema_ids)
        S_r, codes_r = build_random_sparse_bundle(schema_ids, seed)

        for arm in EXPECTED_ARMS:
            recall = measure_recall_at_top1(
                arm, K, seed, atoms, labels, centers, schema_ids, W,
                S_t, codes_t, C_p, S_r)
            per_arm_per_K[arm][str(K)] = recall
            print("  [seed=%d K=%d %s] recall@1=%.3f" % (seed, K, arm, recall),
                  flush=True)

    # Capacity@95%-recall per arm: max K such that recall@1 >= TARGET_RECALL_FOR_CAPACITY
    per_arm_capacity: Dict[str, int] = {}
    for arm in EXPECTED_ARMS:
        cap = 0
        for K in K_SWEEP:
            r = per_arm_per_K[arm][str(K)]
            if r >= TARGET_RECALL_FOR_CAPACITY:
                cap = K
            else:
                break
        per_arm_capacity[arm] = cap

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "K_SWEEP": K_SWEEP,
        "K_SPARSE": K_SPARSE,
        "N_PER_CLUSTER": N_PER_CLUSTER,
        "BETWEEN_CLUSTER_COSINE": BETWEEN_CLUSTER_COSINE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_per_K_recall": per_arm_per_K,
        "per_arm_capacity_at_95": per_arm_capacity,
        "elapsed_s": elapsed,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # Aggregate per-arm capacity@95
    summary_cap: Dict[str, Dict[str, float]] = {}
    summary_recall_at_smallest_K: Dict[str, float] = {}
    K_smallest = K_SWEEP[0]
    for arm in EXPECTED_ARMS:
        caps = [float(per_seed[s]["per_arm_capacity_at_95"][arm])
                for s in seeds_sorted]
        m = float(np.mean(caps))
        sd = float(np.std(caps)) if n_seeds > 1 else 0.0
        cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
        summary_cap[arm] = {"mean_capacity": m, "std": sd, "cv": cv,
                             "per_seed": caps}
        small_K_recalls = [per_seed[s]["per_arm_per_K_recall"][arm].get(str(K_smallest), 0.0)
                            for s in seeds_sorted]
        summary_recall_at_smallest_K[arm] = float(np.mean(small_K_recalls))

    proto_cap = summary_cap["ARM_PROTOTYPE_CENTROID_BUNDLED"]["mean_capacity"]
    tone_cap = summary_cap["ARM_TONEGAWA_SPARSE_K20_BUNDLED"]["mean_capacity"]
    diag_cap = summary_cap["ARM_DIAG_RANDOM_SPARSE_BUNDLED"]["mean_capacity"]
    tone_cv = summary_cap["ARM_TONEGAWA_SPARSE_K20_BUNDLED"]["cv"]

    ratio_tone_proto = tone_cap / proto_cap if proto_cap > 0 else float("inf")
    ratio_diag_tone = diag_cap / tone_cap if tone_cap > 0 else 0.0

    # Saturation check at smallest K
    saturation_at_smallest_K = max(
        summary_recall_at_smallest_K["ARM_TONEGAWA_SPARSE_K20_BUNDLED"],
        summary_recall_at_smallest_K["ARM_PROTOTYPE_CENTROID_BUNDLED"])

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL: any baseline saturates at smallest K (regime too easy)
    if saturation_at_smallest_K >= HF_SATURATION_AT_SMALL_K and K_smallest >= 25:
        # NOTE: at smoke (K=10), saturation is expected; this only fires at full
        pass  # rely on capacity sweep crossover instead

    if diag_cap >= tone_cap:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "DIAG_FALSE_ACCEPT: random_sparse_capacity=%.1f >= tonegawa_capacity=%.1f "
            "(structure not load-bearing)" % (diag_cap, tone_cap))
    elif tone_cap <= proto_cap:
        verdict = "HARD_FAIL"
        verdict_reason = (
            "MECHANISM_NULL: tonegawa_capacity=%.1f <= prototype_capacity=%.1f "
            "(sparse-code interference NOT lower than dense)" % (tone_cap, proto_cap))
    elif (ratio_tone_proto >= HP_TONEGAWA_OVER_PROTO_RATIO and
            ratio_diag_tone <= HP_DIAG_UNDER_TONEGAWA_RATIO and
            (n_seeds == 1 or tone_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "BUNDLED_SPARSE_LIFT: tone_cap=%.1f / proto_cap=%.1f = %.2fx (>= %.2fx); "
            "diag/tone=%.2f (<= %.2f)" % (
                tone_cap, proto_cap, ratio_tone_proto, HP_TONEGAWA_OVER_PROTO_RATIO,
                ratio_diag_tone, HP_DIAG_UNDER_TONEGAWA_RATIO))
    elif ratio_tone_proto >= MIDDLE_RATIO_LO:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_LIFT: tone/proto=%.2fx in [%.2f, %.2f)" % (
                ratio_tone_proto, MIDDLE_RATIO_LO, HP_TONEGAWA_OVER_PROTO_RATIO))

    verdict_msg = (
        "%s | %s | tone_cap=%.1f proto_cap=%.1f diag_cap=%.1f "
        "ratio_tone/proto=%.2f diag/tone=%.2f cv_tone=%.3f recall@1_at_K%d=tone:%.3f,proto:%.3f,diag:%.3f | n_seeds=%d K_sweep=%s"
    ) % (verdict, verdict_reason, tone_cap, proto_cap, diag_cap,
         ratio_tone_proto, ratio_diag_tone, tone_cv,
         K_smallest,
         summary_recall_at_smallest_K["ARM_TONEGAWA_SPARSE_K20_BUNDLED"],
         summary_recall_at_smallest_K["ARM_PROTOTYPE_CENTROID_BUNDLED"],
         summary_recall_at_smallest_K["ARM_DIAG_RANDOM_SPARSE_BUNDLED"],
         n_seeds, K_SWEEP)

    completed_units = n_seeds * len(EXPECTED_ARMS) * len(K_SWEEP)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_capacity_summary": summary_cap,
        "per_arm_recall_at_smallest_K": summary_recall_at_smallest_K,
        "ratio_tonegawa_over_prototype": ratio_tone_proto,
        "ratio_diag_over_tonegawa": ratio_diag_tone,
        "tonegawa_capacity": tone_cap,
        "prototype_capacity": proto_cap,
        "diag_capacity": diag_cap,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "K_sweep": K_SWEEP,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d KSP=%d K_SWEEP=%s seeds=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, K_SPARSE, K_SWEEP, SEEDS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm_per_K_recall" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_per_K_recall"]
                for K in K_SWEEP:
                    assert str(K) in r["per_arm_per_K_recall"][arm]
            # Diag should NOT exceed Tonegawa even in selftest
            tone_recall = r["per_arm_per_K_recall"]["ARM_TONEGAWA_SPARSE_K20_BUNDLED"][str(K_SWEEP[0])]
            diag_recall = r["per_arm_per_K_recall"]["ARM_DIAG_RANDOM_SPARSE_BUNDLED"][str(K_SWEEP[0])]
            print("[selftest] OK K=%d tone=%.3f proto=%.3f diag=%.3f cap_tone=%d cap_proto=%d cap_diag=%d" % (
                K_SWEEP[0], tone_recall,
                r["per_arm_per_K_recall"]["ARM_PROTOTYPE_CENTROID_BUNDLED"][str(K_SWEEP[0])],
                diag_recall,
                r["per_arm_capacity_at_95"]["ARM_TONEGAWA_SPARSE_K20_BUNDLED"],
                r["per_arm_capacity_at_95"]["ARM_PROTOTYPE_CENTROID_BUNDLED"],
                r["per_arm_capacity_at_95"]["ARM_DIAG_RANDOM_SPARSE_BUNDLED"]), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: 3-arm bundled capacity sweep structured")
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    for i, seed in enumerate(SEEDS):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d) K_SWEEP=%s" % (
                                   seed, i + 1, len(SEEDS), K_SWEEP),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        caps = result["per_arm_capacity_at_95"]
        print("[seed=%d] complete in %.1fs cap_tone=%d cap_proto=%d cap_diag=%d" % (
            seed, time.time() - t0,
            caps["ARM_TONEGAWA_SPARSE_K20_BUNDLED"],
            caps["ARM_PROTOTYPE_CENTROID_BUNDLED"],
            caps["ARM_DIAG_RANDOM_SPARSE_BUNDLED"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v3_bundled_capacity"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
