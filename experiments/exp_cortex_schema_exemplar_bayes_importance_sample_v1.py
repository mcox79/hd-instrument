"""cortex_schema_exemplar_bayes_importance_sample_v1 -- CHEAP FALSIFIER.

Prereg: preregs/2026-06-27_cortex_schema_exemplar_bayes_importance_sample_v1.md
Drill:  notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md TOP-3
Handoff: notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md ANCHOR 3

CONCEPT (Shi-Griffiths-Feldman 2010):
  Exemplar memory IS importance sampling. Bayesian posterior over slot-fillers:
    P(slot_value | observed) approx sum_i w_i delta(slot_value, exemplar_i.slot)
    w_i = sim(observed, exemplar_i) / sum_j sim(observed, exemplar_j)
  Substrate cosine kernel = the kernel. Tests whether substrate's cosine geometry
  is RICH ENOUGH to support posterior-style slot inference.

  HARD_FAIL => substrate cone-geometry confound; ANCHOR 1+2 (richer mechanisms)
              unlikely to pass at richer-mechanism work.
  HARD_PASS => substrate cosine supports posterior; ANCHOR 1+2 likely to pass at
              HIGHER accuracy (this is upper-bound lower-bound).

DATA (synthetic concept hierarchy):
  8 schemas (BIRD/FISH/MAMMAL/REPTILE/INSECT/TREE/FLOWER/FUNGUS)
  6 typed slots per schema (HABITAT/DIET/SIZE/COVERING/MOVEMENT/REPRO)
  V_SLOT = 8 fillers per slot type (categorical; each schema picks one per slot
           as its DEFAULT; exemplars are NOISY perturbations of the schema default)
  20 exemplars per schema = 160 total atoms in exemplar bank
  N_DIM=2048 substrate (per drill recommendation; cone-geometry honest)

INFERENCE TASK:
  Given a NOVEL partial input with M=6 slots, 3 are OBSERVED (revealed) and 3 are
  MASKED. Predict the value of each masked slot.
  Per drill: 50% slot mask (3 of 6).

ARMS (5):
  ARM_NO_SCHEMA_BASELINE       popularity prior; predict per-slot mode over ALL exemplars
                                regardless of observed; expected ~ 1/V_SLOT = 0.125
  ARM_RANDOM_K_EXEMPLARS       cosine-irrelevant; pick K=20 RANDOM exemplars; weight uniform
                                control: distinguishes "cosine signal" from "K averaging"
                                expected ~ 1/V_SLOT (random doesn't condition on schema)
  ARM_K_NEAREST_EXEMPLAR_BAYES top-K=20 cosine-nearest exemplars; softmax-weighted vote
                                MECHANISM under test. expected HARD_PASS recall@1 >= 0.50
  ARM_ORACLE_TRUE_SCHEMA       know the true schema; predict slot = schema_default[slot]
                                upper bound; if exemplars are noisy, oracle < 1.0
  DIAG_K_SWEEP arm folded as variant per K in [5, 20, 50] (K-sensitivity sub-arms)
    encoded as separate arm names ARM_K_NEAREST_K5 / K20 / K50

ARM NAMES (final; SHA-256 distinguishability self-test enforced):
  ARM_NO_SCHEMA_BASELINE
  ARM_RANDOM_K_EXEMPLARS
  ARM_K_NEAREST_K5
  ARM_K_NEAREST_K20
  ARM_K_NEAREST_K50
  ARM_ORACLE_TRUE_SCHEMA

PRIMITIVES (CHAIN_GRADE):
  cosine cleanup; refuse-gate (post-hoc check only, not blocking arm-recall metric)
  HRR bind/unbind: NOT used in this cell (this is pure exemplar-Bayes; richer mechanisms
  reside in ANCHOR 1 / ANCHOR 2).

ENCODING:
  per slot s, V_SLOT random L2-normalized N-dim vectors (filler atoms)
  exemplar_vector(i) = average over 6 slots of slot_filler_vector + noise
                        (this is a sum-encoding; concrete realization of the "novel
                         input" embedding for cosine retrieval)
  observed encoding for query = sum over OBSERVED slots only

REGIME / DISCRIMINATORS:
  N_DIM=2048
  V_SLOT=8 fillers per slot
  M_SLOTS=6 typed slots
  K_SCHEMAS=8
  N_EXEMPLARS_PER_SCHEMA=20
  FILLER_NOISE=0.20  (per-exemplar slot-vector perturbation; non-trivial within-schema variance)
  MASK_FRACTION=0.50 (3 of 6 slots masked)
  N_QUERIES_PER_SCHEMA_SMOKE=30 -> 240 inference events smoke
  N_QUERIES_PER_SCHEMA_FULL=100 -> 800 inference events full

PRE-REG BANDS:
  HARD_PASS:
    ARM_K_NEAREST_K20 mean recall@1 >= 0.50 AND
    ARM_K_NEAREST_K20 - ARM_NO_SCHEMA_BASELINE >= 0.30 (cosine signal is the lever) AND
    ARM_K_NEAREST_K20 - ARM_RANDOM_K_EXEMPLARS >= 0.30 (cosine signal not K averaging) AND
    cv across seeds < 0.15 (n=3 smoke; n=5 full) AND
    arms_distinct=True AND
    cardinality_ok=True

  MIDDLE_BAND:
    ARM_K_NEAREST_K20 mean recall@1 in [0.20, 0.50] with cv<0.15
    (real signal but bounded; cone-geometry partial pass)

  HARD_FAIL:
    ARM_K_NEAREST_K20 <= ARM_NO_SCHEMA_BASELINE + 0.05 (cosine kernel doesn't support inference) OR
    ARM_K_NEAREST_K20 < ARM_RANDOM_K_EXEMPLARS (random equals signal -- substrate broken) OR
    ARM_ORACLE_TRUE_SCHEMA <= 0.70 (oracle pipeline broken; cell harness broken) OR
    ANY arm > 0.95 absolute (FAIRNESS_VIOLATION; regime too easy) OR
    cv >= 0.15 OR
    cardinality breach

CRLB PRE-VALIDATION (per [[feedback-experiment-bias-master-checklist]] N):
  N=2048, V_SLOT=8 categorical. Per-slot accuracy variance under chance (1/8=0.125):
    var = p(1-p)/n_trials = 0.125*0.875/240 = 4.56e-4; sd = 0.0214
  HP discriminator = +0.30 lift over baseline. CRLB noise floor 0.02 << 0.30 by 15x.
  Discriminator REACHABLE.

DISCRIMINATOR_MUST_SURVIVE_SCALE check (per [[feedback-discriminator-must-survive-scale]]):
  Smoke at N=2048 (full-N preview = strategy A). Smoke and full use SAME N_DIM; only
  n_seeds and queries differ. So smoke result directly predicts full result modulo
  variance reduction. Cone-geometry confounds visible at smoke.

CARDINALITY_OK:
  EXPECTED_N_UNITS_SMOKE = 6 arms * 3 seeds * 240 queries * 3 masked-slots = 12960 events
  EXPECTED_N_UNITS_FULL  = 6 arms * 5 seeds * 800 queries * 3 masked-slots = 72000 events
  HARD_FAIL_CARDINALITY_BREACH if observed < 0.85 * expected.

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (drill TOP-3 / ANCHOR 3 cheap falsifier).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import inspect
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

ANCHOR_NAME = "cortex_schema_exemplar_bayes_importance_sample_v1"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# -------- Pre-reg bands --------
HP_K_NEAREST_FLOOR = 0.50
HP_LIFT_OVER_BASELINE = 0.30
HP_LIFT_OVER_RANDOM_K = 0.30
HP_CV_MAX = 0.15
HF_FAIRNESS_CEILING = 0.95
HF_ORACLE_FLOOR = 0.70
MIDDLE_K_NEAREST_LO = 0.20
MIDDLE_K_NEAREST_HI = 0.50

EXPECTED_ARMS = (
    "ARM_NO_SCHEMA_BASELINE",
    "ARM_RANDOM_K_EXEMPLARS",
    "ARM_K_NEAREST_K5",
    "ARM_K_NEAREST_K20",
    "ARM_K_NEAREST_K50",
    "ARM_ORACLE_TRUE_SCHEMA",
)
PRIMARY_ARM = "ARM_K_NEAREST_K20"

# -------- Regime --------
if SELF_TEST_MODE:
    N_DIM = 512
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 5
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 5
    SEEDS = [7]
    K_NEAREST_VARIANTS = (5, 20, 50)
    BETA_TEMP = 8.0
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 20
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 30
    SEEDS = [7, 17, 23]
    K_NEAREST_VARIANTS = (5, 20, 50)
    BETA_TEMP = 8.0
else:
    N_DIM = 2048
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 20
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 100
    SEEDS = [7, 17, 23, 31, 41]
    K_NEAREST_VARIANTS = (5, 20, 50)
    BETA_TEMP = 8.0

# arms_distinct check: K=5, K=20, K=50 must produce DIFFERENT predictions
# (else smoke discriminator-fails per [[feedback-three-smoke-disciplines]])
N_MASKED = int(round(MASK_FRACTION * M_SLOTS))  # 3 of 6

EXPECTED_N_UNITS = (len(EXPECTED_ARMS) * len(SEEDS)
                    * (N_QUERIES_PER_SCHEMA * K_SCHEMAS) * N_MASKED)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,VSLOT=%d,MSLOTS=%d,KSCH=%d,NEX=%d,FN=%.2f,MF=%.2f,"
    "NQPS=%d,SEEDS=%s,K_VARIANTS=%s,BETA=%.1f,N_MASKED=%d,"
    "HP_floor=%.2f,HP_lift_base>=%.2f,HP_lift_rand>=%.2f,HP_cv<%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK"
    "+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS, N_EXEMPLARS_PER_SCHEMA,
    FILLER_NOISE, MASK_FRACTION, N_QUERIES_PER_SCHEMA, SEEDS,
    K_NEAREST_VARIANTS, BETA_TEMP, N_MASKED,
    HP_K_NEAREST_FLOOR, HP_LIFT_OVER_BASELINE, HP_LIFT_OVER_RANDOM_K, HP_CV_MAX,
    RUN_MODE,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _atomic_write_metrics(out_dir: Path, metrics_dict: Dict[str, Any]) -> None:
    """ATOMIC-FINAL-METRICS-WRITE per META_RULE_AH: tmp + os.replace."""
    out_dir.mkdir(parents=True, exist_ok=True)
    final = out_dir / "metrics.json"
    tmp = out_dir / ("metrics.json.tmp." + str(os.getpid()))
    payload = json.dumps(metrics_dict, indent=2)
    tmp.write_text(payload, encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
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
            "_hardening_marker": "v1_exemplar_bayes_cheap_falsifier",
        }
        if extra:
            metrics.update(extra)
        _atomic_write_metrics(out_dir, metrics)
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_exemplar_bayes_import_crash",
        }
        _atomic_write_metrics(out_dir, sentinel)
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- data generation --------------------------

def make_filler_atoms(seed: int) -> np.ndarray:
    """V_SLOT filler atoms per slot type, L2-normalized; shape (M_SLOTS, V_SLOT, N_DIM)."""
    rng = np.random.default_rng(seed + 1009)
    out = rng.standard_normal((M_SLOTS, V_SLOT, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=2, keepdims=True)
    out = out / np.maximum(norms, 1e-12)
    return out


def make_schema_defaults(seed: int) -> np.ndarray:
    """K_SCHEMAS x M_SLOTS integer matrix: schema_defaults[k, s] = filler index in [0, V_SLOT)."""
    rng = np.random.default_rng(seed + 2017)
    # NOT all unique fillers per slot; allow shared defaults (some schemas share HABITAT)
    out = rng.integers(0, V_SLOT, size=(K_SCHEMAS, M_SLOTS), dtype=np.int64)
    return out


def make_exemplar_bank(seed: int, schema_defaults: np.ndarray,
                       filler_atoms: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build exemplar bank.

    Each exemplar: schema_id, slot_values (per-slot filler index), vector (sum of
    slot_filler_vectors + noise; L2 normalized).

    Returns:
      schema_ids:  shape (N_EX,) int
      slot_values: shape (N_EX, M_SLOTS) int (filler index per slot)
      vectors:     shape (N_EX, N_DIM) float64 L2-normalized
    """
    N_EX = K_SCHEMAS * N_EXEMPLARS_PER_SCHEMA
    rng = np.random.default_rng(seed + 3037)
    schema_ids = np.zeros(N_EX, dtype=np.int64)
    slot_values = np.zeros((N_EX, M_SLOTS), dtype=np.int64)
    vectors = np.zeros((N_EX, N_DIM), dtype=np.float64)
    for k in range(K_SCHEMAS):
        for i in range(N_EXEMPLARS_PER_SCHEMA):
            idx = k * N_EXEMPLARS_PER_SCHEMA + i
            schema_ids[idx] = k
            for s in range(M_SLOTS):
                # 80% follow schema default; 20% perturb to a random filler
                if rng.random() < (1.0 - FILLER_NOISE):
                    slot_values[idx, s] = schema_defaults[k, s]
                else:
                    # pick a DIFFERENT filler index to avoid collapsing to default
                    alts = [v for v in range(V_SLOT) if v != schema_defaults[k, s]]
                    slot_values[idx, s] = rng.choice(alts)
            # Build vector as sum of slot filler atoms (sum-encoding)
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in range(M_SLOTS):
                v = v + filler_atoms[s, slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            vectors[idx] = v
    return schema_ids, slot_values, vectors


def make_queries(seed: int, schema_defaults: np.ndarray, filler_atoms: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build novel test queries DISJOINT from training exemplars (BIAS-7 anti-contamination).

    Returns:
      q_schema:        (N_Q,) int true schema
      q_slot_values:   (N_Q, M_SLOTS) int ground-truth slot values
      q_observed_idx:  (N_Q, M_SLOTS - N_MASKED) int -- which slots are revealed
      q_observed_vec:  (N_Q, N_DIM) float64 L2-normalized -- query embedding using
                       only OBSERVED slots
    """
    N_Q = K_SCHEMAS * N_QUERIES_PER_SCHEMA
    rng = np.random.default_rng(seed + 4049)  # NOTE: disjoint seed from exemplar bank
    q_schema = np.zeros(N_Q, dtype=np.int64)
    q_slot_values = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    q_observed_idx = np.zeros((N_Q, M_SLOTS - N_MASKED), dtype=np.int64)
    q_observed_vec = np.zeros((N_Q, N_DIM), dtype=np.float64)
    for k in range(K_SCHEMAS):
        for i in range(N_QUERIES_PER_SCHEMA):
            idx = k * N_QUERIES_PER_SCHEMA + i
            q_schema[idx] = k
            for s in range(M_SLOTS):
                if rng.random() < (1.0 - FILLER_NOISE):
                    q_slot_values[idx, s] = schema_defaults[k, s]
                else:
                    alts = [v for v in range(V_SLOT) if v != schema_defaults[k, s]]
                    q_slot_values[idx, s] = rng.choice(alts)
            # Choose OBSERVED slots: random subset of size (M_SLOTS - N_MASKED)
            perm = rng.permutation(M_SLOTS)
            observed = np.sort(perm[:M_SLOTS - N_MASKED])
            q_observed_idx[idx] = observed
            # Build query vector from OBSERVED slots only
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in observed:
                v = v + filler_atoms[s, q_slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            q_observed_vec[idx] = v
    return q_schema, q_slot_values, q_observed_idx, q_observed_vec


# -------------------------- arm implementations --------------------------

def predict_no_schema_baseline(slot_values: np.ndarray, q_observed_idx: np.ndarray,
                                q_true_slot_values: np.ndarray) -> np.ndarray:
    """Predict masked slots as the per-slot MODE over ALL exemplars (popularity prior).

    Returns predictions shape (N_Q, M_SLOTS) -- only masked positions are meaningful.
    For observed positions, fills with the truth (we never score those).
    """
    N_Q = q_observed_idx.shape[0]
    # Popularity per (slot, filler)
    pop = np.zeros((M_SLOTS, V_SLOT), dtype=np.int64)
    for s in range(M_SLOTS):
        for v in range(V_SLOT):
            pop[s, v] = int(np.sum(slot_values[:, s] == v))
    per_slot_mode = np.argmax(pop, axis=1)  # (M_SLOTS,)
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    for n in range(N_Q):
        for s in range(M_SLOTS):
            preds[n, s] = per_slot_mode[s]
    return preds


def predict_random_k_exemplars(q_observed_vec: np.ndarray, q_observed_idx: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                K: int, rng: np.random.Generator) -> np.ndarray:
    """Pick K RANDOM exemplars (NOT nearest); uniform vote per masked slot.

    Control: distinguishes "cosine signal" from "K averaging".
    """
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    K_eff = min(K, N_EX)
    for n in range(N_Q):
        chosen = rng.choice(N_EX, size=K_eff, replace=False)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for c in chosen:
                counts[exemplar_slot_values[c, s]] += 1.0
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_k_nearest_exemplar_bayes(q_observed_vec: np.ndarray,
                                      exemplar_vectors: np.ndarray,
                                      exemplar_slot_values: np.ndarray,
                                      K: int, beta: float) -> np.ndarray:
    """K-nearest exemplar importance-sampled posterior.

    For each query:
      cosine_i = cos(q, exemplar_i)
      take top-K by cosine
      w_i = softmax(beta * cosine_i) over top-K
      For each slot s: P(v) = sum_{i in topK, slot_value_i[s]==v} w_i
      pred[s] = argmax_v P(v)
    """
    N_Q = q_observed_vec.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    # All exemplars assumed pre-normalized (L2=1); query also normalized.
    # cos_matrix shape (N_Q, N_EX)
    cos_all = q_observed_vec @ exemplar_vectors.T  # (N_Q, N_EX)
    for n in range(N_Q):
        scores = cos_all[n]  # (N_EX,)
        # top-K indices by cosine
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_cos = scores[top_idx]
        # softmax weights at temperature beta
        z = beta * top_cos
        z = z - np.max(z)  # numerical stability
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_oracle_true_schema(q_schema: np.ndarray, schema_defaults: np.ndarray
                                ) -> np.ndarray:
    """Oracle: know the true schema; predict slot = schema_default[slot]."""
    N_Q = q_schema.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    for n in range(N_Q):
        for s in range(M_SLOTS):
            preds[n, s] = schema_defaults[q_schema[n], s]
    return preds


# -------------------------- scoring --------------------------

def recall_at_1_on_masked(preds: np.ndarray, true_slots: np.ndarray,
                           q_observed_idx: np.ndarray) -> float:
    """recall@1 over MASKED slots only. Per-query: 3 masked slots; one event each."""
    N_Q = preds.shape[0]
    hits = 0
    n = 0
    for q in range(N_Q):
        observed_set = set(int(x) for x in q_observed_idx[q])
        for s in range(M_SLOTS):
            if s in observed_set:
                continue
            if preds[q, s] == true_slots[q, s]:
                hits += 1
            n += 1
    return hits / max(n, 1)


# -------------------------- per-seed runner --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    filler_atoms = make_filler_atoms(seed)
    schema_defaults = make_schema_defaults(seed)
    ex_schema_ids, ex_slot_values, ex_vectors = make_exemplar_bank(
        seed, schema_defaults, filler_atoms)
    q_schema, q_true_slots, q_obs_idx, q_obs_vec = make_queries(
        seed, schema_defaults, filler_atoms)

    arms_preds: Dict[str, np.ndarray] = {}
    per_arm_recall: Dict[str, float] = {}

    # NO_SCHEMA_BASELINE
    arms_preds["ARM_NO_SCHEMA_BASELINE"] = predict_no_schema_baseline(
        ex_slot_values, q_obs_idx, q_true_slots)

    # RANDOM_K_EXEMPLARS (use K=20 for parity with primary)
    rng_random = np.random.default_rng(seed + 5059)
    arms_preds["ARM_RANDOM_K_EXEMPLARS"] = predict_random_k_exemplars(
        q_obs_vec, q_obs_idx, ex_vectors, ex_slot_values, K=20, rng=rng_random)

    # K-nearest variants
    for K in K_NEAREST_VARIANTS:
        arm = "ARM_K_NEAREST_K%d" % K
        arms_preds[arm] = predict_k_nearest_exemplar_bayes(
            q_obs_vec, ex_vectors, ex_slot_values, K=K, beta=BETA_TEMP)

    # ORACLE
    arms_preds["ARM_ORACLE_TRUE_SCHEMA"] = predict_oracle_true_schema(
        q_schema, schema_defaults)

    # Score each arm
    for arm in EXPECTED_ARMS:
        r = recall_at_1_on_masked(arms_preds[arm], q_true_slots, q_obs_idx)
        per_arm_recall[arm] = float(r)
        print("  [seed=%d %s] recall@1=%.3f" % (seed, arm, r), flush=True)

    # ARMS-MUST-DIFFER SHA-256 self-test on prediction MATRICES (META_RULE_AF)
    arm_hashes: Dict[str, str] = {}
    for arm in EXPECTED_ARMS:
        h = hashlib.sha256(arms_preds[arm].tobytes()).hexdigest()[:16]
        arm_hashes[arm] = h
    unique_hashes = len(set(arm_hashes.values()))
    arms_differ_verified = (unique_hashes == len(EXPECTED_ARMS))

    # Count cardinality (events scored)
    n_events_per_arm = q_obs_vec.shape[0] * N_MASKED
    events_total = n_events_per_arm * len(EXPECTED_ARMS)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "V_SLOT": V_SLOT,
        "M_SLOTS": M_SLOTS,
        "K_SCHEMAS": K_SCHEMAS,
        "N_EXEMPLARS_PER_SCHEMA": N_EXEMPLARS_PER_SCHEMA,
        "FILLER_NOISE": FILLER_NOISE,
        "MASK_FRACTION": MASK_FRACTION,
        "N_MASKED": N_MASKED,
        "N_QUERIES_PER_SCHEMA": N_QUERIES_PER_SCHEMA,
        "BETA_TEMP": BETA_TEMP,
        "K_NEAREST_VARIANTS": list(K_NEAREST_VARIANTS),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm_recall_at_1_masked": per_arm_recall,
        "arm_hashes": arm_hashes,
        "arms_differ_verified": bool(arms_differ_verified),
        "n_unique_arm_hashes": int(unique_hashes),
        "n_events_scored_per_arm": int(n_events_per_arm),
        "n_events_scored_total": int(events_total),
        "elapsed_s": elapsed,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    per_arm_recall_summary: Dict[str, Dict[str, float]] = {}
    for arm in EXPECTED_ARMS:
        vals = [per_seed[s]["per_arm_recall_at_1_masked"][arm] for s in seeds_sorted]
        m = float(np.mean(vals))
        sd = float(np.std(vals)) if n_seeds > 1 else 0.0
        cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
        per_arm_recall_summary[arm] = {
            "mean": m, "std": sd, "cv": cv, "per_seed": vals}

    # Verify arms_differ across all seeds
    all_distinct = all(per_seed[s]["arms_differ_verified"] for s in seeds_sorted)

    # Cardinality
    events_total = sum(per_seed[s]["n_events_scored_per_arm"] for s in seeds_sorted)
    expected_events_per_arm = len(SEEDS) * N_QUERIES_PER_SCHEMA * K_SCHEMAS * N_MASKED
    cardinality_ok = events_total >= int(0.85 * expected_events_per_arm)

    base = per_arm_recall_summary["ARM_NO_SCHEMA_BASELINE"]["mean"]
    rand = per_arm_recall_summary["ARM_RANDOM_K_EXEMPLARS"]["mean"]
    primary = per_arm_recall_summary[PRIMARY_ARM]["mean"]
    primary_cv = per_arm_recall_summary[PRIMARY_ARM]["cv"]
    oracle = per_arm_recall_summary["ARM_ORACLE_TRUE_SCHEMA"]["mean"]
    k5 = per_arm_recall_summary["ARM_K_NEAREST_K5"]["mean"]
    k50 = per_arm_recall_summary["ARM_K_NEAREST_K50"]["mean"]

    # Fairness ceiling
    max_arm = max(per_arm_recall_summary[arm]["mean"] for arm in EXPECTED_ARMS
                  if arm != "ARM_ORACLE_TRUE_SCHEMA")
    # Oracle is allowed to be high; non-oracle arms must NOT saturate

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not all_distinct:
        verdict = "HARD_FAIL"
        verdict_reason = "ARMS_NOT_DISTINCT: SHA-256 collisions across arm predictions"
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = ("CARDINALITY_BREACH: events_per_arm=%d < 0.85 * expected=%d"
                          % (events_total, expected_events_per_arm))
    elif oracle <= HF_ORACLE_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = ("ORACLE_BROKEN: oracle_recall=%.3f <= %.2f (cell harness broken)"
                          % (oracle, HF_ORACLE_FLOOR))
    elif max_arm > HF_FAIRNESS_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = ("FAIRNESS_VIOLATION: non-oracle arm max=%.3f > %.2f "
                          "(regime too easy)" % (max_arm, HF_FAIRNESS_CEILING))
    elif primary <= base + 0.05:
        verdict = "HARD_FAIL"
        verdict_reason = ("COSINE_KERNEL_NULL: primary=%.3f <= baseline=%.3f + 0.05 "
                          "(substrate cosine doesn't support schema inference)"
                          % (primary, base))
    elif primary < rand:
        verdict = "HARD_FAIL"
        verdict_reason = ("SIGNAL_LT_RANDOM: primary=%.3f < random_K=%.3f "
                          "(substrate broken)" % (primary, rand))
    elif n_seeds > 1 and primary_cv >= HP_CV_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("UNSTABLE: primary cv=%.3f >= %.2f" % (primary_cv, HP_CV_MAX))
    elif (primary >= HP_K_NEAREST_FLOOR
          and (primary - base) >= HP_LIFT_OVER_BASELINE
          and (primary - rand) >= HP_LIFT_OVER_RANDOM_K
          and (n_seeds == 1 or primary_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "EXEMPLAR_BAYES_SUPPORTED: primary=%.3f (>=%.2f) | "
            "lift_over_base=+%.3f (>=%.2f) | lift_over_rand=+%.3f (>=%.2f)"
            % (primary, HP_K_NEAREST_FLOOR,
               primary - base, HP_LIFT_OVER_BASELINE,
               primary - rand, HP_LIFT_OVER_RANDOM_K))
    elif MIDDLE_K_NEAREST_LO <= primary < MIDDLE_K_NEAREST_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("PARTIAL_SIGNAL: primary=%.3f in [%.2f, %.2f); "
                          "cosine signal present but bounded"
                          % (primary, MIDDLE_K_NEAREST_LO, MIDDLE_K_NEAREST_HI))
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("BOUNDARY: primary=%.3f base=%.3f rand=%.3f"
                          % (primary, base, rand))

    verdict_msg = (
        "%s | %s | primary[%s]=%.3f base=%.3f rand=%.3f oracle=%.3f "
        "K5=%.3f K20=%.3f K50=%.3f cv_primary=%.3f arms_distinct=%s n_seeds=%d"
    ) % (verdict, verdict_reason, PRIMARY_ARM, primary, base, rand, oracle,
         k5, primary, k50, primary_cv, all_distinct, n_seeds)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_recall_summary": per_arm_recall_summary,
        "primary_arm": PRIMARY_ARM,
        "primary_recall": primary,
        "baseline_recall": base,
        "random_k_recall": rand,
        "oracle_recall": oracle,
        "lift_over_baseline": primary - base,
        "lift_over_random_k": primary - rand,
        "primary_cv": primary_cv,
        "arms_differ_verified": all_distinct,
        "cardinality_ok": cardinality_ok,
        "events_per_arm_total": events_total,
        "expected_events_per_arm": expected_events_per_arm,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "K_variants": K_NEAREST_VARIANTS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_SLOT=%d M_SLOTS=%d K_SCH=%d NEX=%d seeds=%s "
          "K_NEAREST_VARIANTS=%s BETA=%.1f MASK_FRAC=%.2f" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS,
              N_EXEMPLARS_PER_SCHEMA, SEEDS, K_NEAREST_VARIANTS, BETA_TEMP,
              MASK_FRACTION), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            # Assert all expected arms produced predictions
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_recall_at_1_masked"], "missing arm %s" % arm
            # Oracle should be HIGH (mostly correct since 80% follow defaults)
            ora = r["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
            base = r["per_arm_recall_at_1_masked"]["ARM_NO_SCHEMA_BASELINE"]
            primary = r["per_arm_recall_at_1_masked"][PRIMARY_ARM]
            rand = r["per_arm_recall_at_1_masked"]["ARM_RANDOM_K_EXEMPLARS"]
            assert r["arms_differ_verified"], "arms_distinct check FAILED"
            # Oracle should be >> chance; self-test at tiny N relaxed
            assert ora >= 0.50, "oracle recall %.3f too low" % ora
            print("[selftest] OK primary=%.3f base=%.3f rand=%.3f oracle=%.3f "
                  "arms_distinct=%s n_unique=%d/%d" % (
                      primary, base, rand, ora, r["arms_differ_verified"],
                      r["n_unique_arm_hashes"], len(EXPECTED_ARMS)), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   ("SELFTEST_OK: arms differ, oracle=%.3f base=%.3f "
                                    "rand=%.3f primary=%.3f"
                                    % (ora, base, rand, primary)),
                                   extra={"selftest_per_arm": r["per_arm_recall_at_1_masked"],
                                          "selftest_arms_distinct": r["arms_differ_verified"]})
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
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        per_seed_results[str(seed)] = result
        print("[seed=%d] complete in %.1fs primary[%s]=%.3f arms_distinct=%s" % (
            seed, time.time() - t0, PRIMARY_ARM,
            result["per_arm_recall_at_1_masked"][PRIMARY_ARM],
            result["arms_differ_verified"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_exemplar_bayes_cheap_falsifier"
    _atomic_write_metrics(out_dir, final)
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
