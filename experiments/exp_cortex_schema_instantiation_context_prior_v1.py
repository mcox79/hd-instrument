"""cortex_schema_instantiation_context_prior_v1 -- PRIMARY MECHANISM TEST.

Prereg:  d:/AI/hd-instrument/preregs/2026-06-27_cortex_schema_instantiation_context_prior_v1.md
Drill:   d:/AI/hd-instrument/notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md TOP-1
Handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md ANCHOR 1
Greenlight: d:/AI/hd-instrument/data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json
            ANCHOR 3 HARD_PASS K20=MEASURED@0.728 cv=0.015 lift +0.472 over baseline.

CONCEPT (Gilboa-Moscovitch 2017 vmPFC schema-instantiation):
  Schema = structured template with TYPED SLOTS. Given partial instance + context,
  predict missing slots by BIASING retrieval toward schema-consistent candidates.
  vmPFC operationalization = top-down prior over substrate retrieval (not just
  bottom-up pattern match). Implemented as HRR-bound schema prior:
    1. Infer active schema from observed slots (cosine to schema-prototype atoms).
    2. For each masked slot, unbind(schema_atom * slot_role_atom) -> predicted filler.
    3. Cleanup to nearest filler.
  HYBRID arm = additive ensemble of context-prior + exemplar-Bayes.

ARMS (6):
  ARM_NO_SCHEMA_BASELINE       popularity mode; expected ~0.125
  ARM_RANDOM_PRIOR             random filler per slot; CONTROL ~0.125
  ARM_EXEMPLAR_BAYES_K20       replicate ANCHOR 3 K20 (top-K cosine + softmax)
                                EXPECTED@~0.728 (ANCHOR 3 MEASURED@)
  ARM_CONTEXT_BOUND_PRIOR      HRR-derived schema prior; MECHANISM UNDER TEST.
                                PRIMARY ARM. HP HYPOTHESIZED@>=0.80
  ARM_HYBRID_PRIOR_PLUS_EXEMPLAR  alpha=0.5 ensemble; HP HYPOTHESIZED@>=0.85
  ARM_ORACLE_TRUE_SCHEMA       schema_default[slot]; upper bound

PRE-REG (concise):
  HARD_PASS:
    ARM_CONTEXT_BOUND_PRIOR >= 0.80 AND
    ARM_HYBRID >= 0.85 AND
    cv < 0.10 AND arms_distinct=True AND cardinality_ok=True
  MIDDLE_BAND:
    ARM_CONTEXT_BOUND_PRIOR in [0.50, 0.80] with cv<0.15
  HARD_FAIL:
    ARM_CONTEXT_BOUND_PRIOR <= ARM_EXEMPLAR_BAYES_K20 OR
    ORACLE < 0.70 OR RANDOM_PRIOR > 0.25 OR arms_distinct=False OR
    non-oracle arm > 0.95 OR cv >= 0.15

REGIME (same as ANCHOR 3 for direct comparability):
  smoke: N=2048, n_seeds=3, 30 queries/schema (240 total), ~30s wall
  full:  N=8192, n_seeds=5, 100 queries/schema (800 total), ~3-5min wall

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (drill TOP-1 / ANCHOR 1 primary mechanism).
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

ANCHOR_NAME = "cortex_schema_instantiation_context_prior_v1"

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
HP_CONTEXT_PRIOR_FLOOR = 0.80
HP_HYBRID_FLOOR = 0.85
HP_CV_MAX = 0.10
HF_CV_MAX = 0.15
HF_ORACLE_FLOOR = 0.70
HF_RANDOM_CEILING = 0.25
HF_FAIRNESS_CEILING = 0.95
MIDDLE_PRIOR_LO = 0.50
MIDDLE_PRIOR_HI = 0.80
EXEMPLAR_BAYES_REFERENCE = 0.728  # ANCHOR 3 MEASURED@

EXPECTED_ARMS = (
    "ARM_NO_SCHEMA_BASELINE",
    "ARM_RANDOM_PRIOR",
    "ARM_EXEMPLAR_BAYES_K20",
    "ARM_CONTEXT_BOUND_PRIOR",
    "ARM_HYBRID_PRIOR_PLUS_EXEMPLAR",
    "ARM_ORACLE_TRUE_SCHEMA",
)
PRIMARY_ARM = "ARM_CONTEXT_BOUND_PRIOR"

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
    K_EXEMPLAR = 20
    BETA_TEMP = 8.0
    HYBRID_ALPHA = 0.5
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
    K_EXEMPLAR = 20
    BETA_TEMP = 8.0
    HYBRID_ALPHA = 0.5
else:
    N_DIM = 8192
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 20
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 100
    SEEDS = [7, 17, 23, 31, 41]
    K_EXEMPLAR = 20
    BETA_TEMP = 8.0
    HYBRID_ALPHA = 0.5

N_MASKED = int(round(MASK_FRACTION * M_SLOTS))  # 3 of 6

EXPECTED_N_UNITS = (len(EXPECTED_ARMS) * len(SEEDS)
                    * (N_QUERIES_PER_SCHEMA * K_SCHEMAS) * N_MASKED)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,VSLOT=%d,MSLOTS=%d,KSCH=%d,NEX=%d,FN=%.2f,MF=%.2f,"
    "NQPS=%d,SEEDS=%s,K_EX=%d,BETA=%.1f,ALPHA=%.2f,N_MASKED=%d,"
    "HP_prior=%.2f,HP_hybrid=%.2f,HP_cv<%.2f,EX_REF=%.3f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK"
    "+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+HRR_FFT_BIND"
) % (
    ANCHOR_NAME, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS, N_EXEMPLARS_PER_SCHEMA,
    FILLER_NOISE, MASK_FRACTION, N_QUERIES_PER_SCHEMA, SEEDS,
    K_EXEMPLAR, BETA_TEMP, HYBRID_ALPHA, N_MASKED,
    HP_CONTEXT_PRIOR_FLOOR, HP_HYBRID_FLOOR, HP_CV_MAX, EXEMPLAR_BAYES_REFERENCE,
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
            "_hardening_marker": "v1_context_bound_prior_primary_mechanism",
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
            "_hardening_marker": "v1_context_bound_prior_import_crash",
        }
        _atomic_write_metrics(out_dir, sentinel)
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- HRR primitives --------------------------

def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution via FFT. Plate 1995 HRR."""
    return np.real(np.fft.ifft(np.fft.fft(a) * np.fft.fft(b)))


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular correlation via FFT (conjugate of b). Approximate inverse of bind."""
    return np.real(np.fft.ifft(np.fft.fft(c) * np.conj(np.fft.fft(b))))


def l2_normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / max(n, 1e-12)


# -------------------------- data generation (SAME as ANCHOR 3) --------------------------

def make_filler_atoms(seed: int) -> np.ndarray:
    """V_SLOT filler atoms per slot type, L2-normalized; shape (M_SLOTS, V_SLOT, N_DIM)."""
    rng = np.random.default_rng(seed + 1009)
    out = rng.standard_normal((M_SLOTS, V_SLOT, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=2, keepdims=True)
    out = out / np.maximum(norms, 1e-12)
    return out


def make_schema_defaults(seed: int) -> np.ndarray:
    """K_SCHEMAS x M_SLOTS integer matrix."""
    rng = np.random.default_rng(seed + 2017)
    out = rng.integers(0, V_SLOT, size=(K_SCHEMAS, M_SLOTS), dtype=np.int64)
    return out


def make_schema_atoms(seed: int) -> np.ndarray:
    """K_SCHEMAS schema-class atoms, L2-normalized; shape (K_SCHEMAS, N_DIM).
    Distinct seed family from filler atoms to avoid collision."""
    rng = np.random.default_rng(seed + 6067)
    out = rng.standard_normal((K_SCHEMAS, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norms, 1e-12)


def make_slot_role_atoms(seed: int) -> np.ndarray:
    """M_SLOTS slot-role atoms, L2-normalized; shape (M_SLOTS, N_DIM).
    Distinct seed family."""
    rng = np.random.default_rng(seed + 7079)
    out = rng.standard_normal((M_SLOTS, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=1, keepdims=True)
    return out / np.maximum(norms, 1e-12)


def make_schema_memory_traces(schema_atoms: np.ndarray, slot_role_atoms: np.ndarray,
                                schema_defaults: np.ndarray, filler_atoms: np.ndarray
                                ) -> np.ndarray:
    """For each schema k, build HRR-bound memory trace:
        trace_k = sum over slots s of bind(schema_atom_k * slot_role_s, filler_default[k,s])

    NOTE: Use schema_atom * slot_role as KEY for cleanliness (binding two atoms gives a
    distinct lookup key per (schema, slot)). Then bind to filler.
    Returns shape (K_SCHEMAS, N_DIM) -- one trace per schema.
    """
    traces = np.zeros((K_SCHEMAS, N_DIM), dtype=np.float64)
    for k in range(K_SCHEMAS):
        for s in range(M_SLOTS):
            key = hrr_bind(schema_atoms[k], slot_role_atoms[s])
            filler_v = filler_atoms[s, schema_defaults[k, s]]
            traces[k] = traces[k] + hrr_bind(key, filler_v)
        traces[k] = l2_normalize(traces[k])
    return traces


def make_exemplar_bank(seed: int, schema_defaults: np.ndarray,
                       filler_atoms: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same as ANCHOR 3."""
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
                if rng.random() < (1.0 - FILLER_NOISE):
                    slot_values[idx, s] = schema_defaults[k, s]
                else:
                    alts = [v for v in range(V_SLOT) if v != schema_defaults[k, s]]
                    slot_values[idx, s] = rng.choice(alts)
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in range(M_SLOTS):
                v = v + filler_atoms[s, slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            vectors[idx] = v
    return schema_ids, slot_values, vectors


def make_queries(seed: int, schema_defaults: np.ndarray, filler_atoms: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Same as ANCHOR 3 (disjoint seed)."""
    N_Q = K_SCHEMAS * N_QUERIES_PER_SCHEMA
    rng = np.random.default_rng(seed + 4049)
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
            perm = rng.permutation(M_SLOTS)
            observed = np.sort(perm[:M_SLOTS - N_MASKED])
            q_observed_idx[idx] = observed
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in observed:
                v = v + filler_atoms[s, q_slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            q_observed_vec[idx] = v
    return q_schema, q_slot_values, q_observed_idx, q_observed_vec


# -------------------------- arm implementations --------------------------

def predict_no_schema_baseline(slot_values: np.ndarray, q_observed_idx: np.ndarray
                                ) -> np.ndarray:
    N_Q = q_observed_idx.shape[0]
    pop = np.zeros((M_SLOTS, V_SLOT), dtype=np.int64)
    for s in range(M_SLOTS):
        for v in range(V_SLOT):
            pop[s, v] = int(np.sum(slot_values[:, s] == v))
    per_slot_mode = np.argmax(pop, axis=1)
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    for n in range(N_Q):
        for s in range(M_SLOTS):
            preds[n, s] = per_slot_mode[s]
    return preds


def predict_random_prior(q_observed_idx: np.ndarray, rng: np.random.Generator
                          ) -> np.ndarray:
    """Predict each slot as uniformly random filler."""
    N_Q = q_observed_idx.shape[0]
    preds = rng.integers(0, V_SLOT, size=(N_Q, M_SLOTS), dtype=np.int64)
    return preds


def predict_exemplar_bayes_k20(q_observed_vec: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                K: int, beta: float) -> np.ndarray:
    """Replicate ANCHOR 3 K20 mechanism (top-K cosine + softmax weighted vote)."""
    N_Q = q_observed_vec.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    cos_all = q_observed_vec @ exemplar_vectors.T
    for n in range(N_Q):
        scores = cos_all[n]
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_cos = scores[top_idx]
        z = beta * top_cos
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def _schema_posterior_from_observed(q_observed_vec: np.ndarray,
                                     exemplar_vectors: np.ndarray,
                                     exemplar_schema_ids: np.ndarray,
                                     K: int, beta: float) -> np.ndarray:
    """Infer P(schema | observed) via top-K exemplar vote per schema_id.
    Returns shape (N_Q, K_SCHEMAS) probability matrix.
    """
    N_Q = q_observed_vec.shape[0]
    cos_all = q_observed_vec @ exemplar_vectors.T  # (N_Q, N_EX)
    sch_post = np.zeros((N_Q, K_SCHEMAS), dtype=np.float64)
    for n in range(N_Q):
        scores = cos_all[n]
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_cos = scores[top_idx]
        z = beta * top_cos
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for ii, ex_idx in enumerate(top_idx):
            sch_post[n, exemplar_schema_ids[ex_idx]] += w[ii]
    return sch_post


def predict_context_bound_prior(q_observed_vec: np.ndarray,
                                 exemplar_vectors: np.ndarray,
                                 exemplar_schema_ids: np.ndarray,
                                 schema_traces: np.ndarray,
                                 slot_role_atoms: np.ndarray,
                                 filler_atoms: np.ndarray,
                                 K: int, beta: float
                                 ) -> Tuple[np.ndarray, np.ndarray]:
    """HRR-bound context-prior arm (mechanism under test).

    Step 1: Infer schema posterior from observed exemplar cosine vote.
    Step 2: For each query, blend the K_SCHEMAS HRR memory traces weighted by
            schema posterior -> aggregated trace.
    Step 3: For each masked slot s, unbind(aggregated_trace, bind(schema_centroid, slot_role_s))
            to extract predicted filler vector. Use weighted-schema-atom centroid as key.
            Cleanup to nearest filler atom for slot s.

    Returns:
      preds shape (N_Q, M_SLOTS) int
      slot_scores shape (N_Q, M_SLOTS, V_SLOT) float (cosine match to each filler)
    """
    N_Q = q_observed_vec.shape[0]
    sch_post = _schema_posterior_from_observed(
        q_observed_vec, exemplar_vectors, exemplar_schema_ids, K, beta)

    # Build per-query aggregated schema trace = sum_k sch_post[n,k] * schema_traces[k]
    # Also per-query aggregated schema-atom centroid for unbind key.
    schema_atoms = _SCHEMA_ATOMS_CACHE
    agg_traces = sch_post @ schema_traces  # (N_Q, N_DIM)
    agg_schema_atom = sch_post @ schema_atoms  # (N_Q, N_DIM) -- weighted centroid

    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    slot_scores = np.zeros((N_Q, M_SLOTS, V_SLOT), dtype=np.float64)

    # Precompute FFTs to speed up unbind
    for n in range(N_Q):
        trace_n = agg_traces[n]
        sch_n = agg_schema_atom[n]
        for s in range(M_SLOTS):
            # key = bind(schema_centroid, slot_role_s)
            key = hrr_bind(sch_n, slot_role_atoms[s])
            # predicted filler = unbind(trace, key)
            pred_filler = hrr_unbind(trace_n, key)
            pred_filler_n = l2_normalize(pred_filler)
            # Cleanup to nearest filler atom for slot s
            sims = filler_atoms[s] @ pred_filler_n  # (V_SLOT,)
            slot_scores[n, s] = sims
            preds[n, s] = int(np.argmax(sims))
    return preds, slot_scores


def predict_hybrid(q_observed_vec: np.ndarray,
                    exemplar_vectors: np.ndarray,
                    exemplar_schema_ids: np.ndarray,
                    exemplar_slot_values: np.ndarray,
                    context_slot_scores: np.ndarray,
                    K: int, beta: float, alpha: float) -> np.ndarray:
    """Additive ensemble:
      score(v, s) = alpha * P_exemplar(v|s) + (1-alpha) * P_context(v|s)
    where P_exemplar is softmax over exemplar votes per slot/filler, and
    P_context is softmax over cleanup similarities from CONTEXT_BOUND_PRIOR.

    Returns preds shape (N_Q, M_SLOTS) int.
    """
    N_Q = q_observed_vec.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    cos_all = q_observed_vec @ exemplar_vectors.T
    for n in range(N_Q):
        scores = cos_all[n]
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_cos = scores[top_idx]
        z = beta * top_cos
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            # P_exemplar(v|s): vote over filler vals weighted by softmax
            p_ex = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                p_ex[exemplar_slot_values[ex_idx, s]] += w[ii]
            # P_context(v|s): softmax over cleanup similarities
            ctx_z = beta * context_slot_scores[n, s]
            ctx_z = ctx_z - np.max(ctx_z)
            p_ctx = np.exp(ctx_z)
            p_ctx = p_ctx / max(np.sum(p_ctx), 1e-12)
            # Blend
            blended = alpha * p_ex + (1.0 - alpha) * p_ctx
            preds[n, s] = int(np.argmax(blended))
    return preds


def predict_oracle_true_schema(q_schema: np.ndarray, schema_defaults: np.ndarray
                                ) -> np.ndarray:
    N_Q = q_schema.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    for n in range(N_Q):
        for s in range(M_SLOTS):
            preds[n, s] = schema_defaults[q_schema[n], s]
    return preds


# -------------------------- scoring --------------------------

def recall_at_1_on_masked(preds: np.ndarray, true_slots: np.ndarray,
                           q_observed_idx: np.ndarray) -> float:
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

# Module-level cache for schema atoms (needed inside context_bound_prior arm)
_SCHEMA_ATOMS_CACHE = None


def run_one_seed(seed: int) -> Dict[str, Any]:
    global _SCHEMA_ATOMS_CACHE
    t0 = time.time()
    filler_atoms = make_filler_atoms(seed)
    schema_defaults = make_schema_defaults(seed)
    schema_atoms = make_schema_atoms(seed)
    _SCHEMA_ATOMS_CACHE = schema_atoms  # bind for context-prior arm
    slot_role_atoms = make_slot_role_atoms(seed)
    schema_traces = make_schema_memory_traces(
        schema_atoms, slot_role_atoms, schema_defaults, filler_atoms)
    ex_schema_ids, ex_slot_values, ex_vectors = make_exemplar_bank(
        seed, schema_defaults, filler_atoms)
    q_schema, q_true_slots, q_obs_idx, q_obs_vec = make_queries(
        seed, schema_defaults, filler_atoms)

    arms_preds: Dict[str, np.ndarray] = {}
    per_arm_recall: Dict[str, float] = {}

    # ARM_NO_SCHEMA_BASELINE
    arms_preds["ARM_NO_SCHEMA_BASELINE"] = predict_no_schema_baseline(
        ex_slot_values, q_obs_idx)

    # ARM_RANDOM_PRIOR (uniform random; not K-averaging - distinguishes from ANCHOR 3 RANDOM_K)
    rng_random = np.random.default_rng(seed + 5059)
    arms_preds["ARM_RANDOM_PRIOR"] = predict_random_prior(q_obs_idx, rng_random)

    # ARM_EXEMPLAR_BAYES_K20 (replicate ANCHOR 3)
    arms_preds["ARM_EXEMPLAR_BAYES_K20"] = predict_exemplar_bayes_k20(
        q_obs_vec, ex_vectors, ex_slot_values, K=K_EXEMPLAR, beta=BETA_TEMP)

    # ARM_CONTEXT_BOUND_PRIOR (primary mechanism)
    ctx_preds, ctx_slot_scores = predict_context_bound_prior(
        q_obs_vec, ex_vectors, ex_schema_ids, schema_traces,
        slot_role_atoms, filler_atoms, K=K_EXEMPLAR, beta=BETA_TEMP)
    arms_preds["ARM_CONTEXT_BOUND_PRIOR"] = ctx_preds

    # ARM_HYBRID_PRIOR_PLUS_EXEMPLAR (ensemble)
    arms_preds["ARM_HYBRID_PRIOR_PLUS_EXEMPLAR"] = predict_hybrid(
        q_obs_vec, ex_vectors, ex_schema_ids, ex_slot_values,
        ctx_slot_scores, K=K_EXEMPLAR, beta=BETA_TEMP, alpha=HYBRID_ALPHA)

    # ARM_ORACLE_TRUE_SCHEMA
    arms_preds["ARM_ORACLE_TRUE_SCHEMA"] = predict_oracle_true_schema(
        q_schema, schema_defaults)

    # Score each arm
    for arm in EXPECTED_ARMS:
        r = recall_at_1_on_masked(arms_preds[arm], q_true_slots, q_obs_idx)
        per_arm_recall[arm] = float(r)
        print("  [seed=%d %s] recall@1=%.3f" % (seed, arm, r), flush=True)

    # ARMS-MUST-DIFFER SHA-256 (META_RULE_AF)
    arm_hashes: Dict[str, str] = {}
    for arm in EXPECTED_ARMS:
        h = hashlib.sha256(arms_preds[arm].tobytes()).hexdigest()[:16]
        arm_hashes[arm] = h
    unique_hashes = len(set(arm_hashes.values()))
    arms_differ_verified = (unique_hashes == len(EXPECTED_ARMS))

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
        "K_EXEMPLAR": K_EXEMPLAR,
        "HYBRID_ALPHA": HYBRID_ALPHA,
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

    all_distinct = all(per_seed[s]["arms_differ_verified"] for s in seeds_sorted)
    events_total = sum(per_seed[s]["n_events_scored_per_arm"] for s in seeds_sorted)
    expected_events_per_arm = len(SEEDS) * N_QUERIES_PER_SCHEMA * K_SCHEMAS * N_MASKED
    cardinality_ok = events_total >= int(0.85 * expected_events_per_arm)

    base = per_arm_recall_summary["ARM_NO_SCHEMA_BASELINE"]["mean"]
    rand = per_arm_recall_summary["ARM_RANDOM_PRIOR"]["mean"]
    exemplar = per_arm_recall_summary["ARM_EXEMPLAR_BAYES_K20"]["mean"]
    primary = per_arm_recall_summary["ARM_CONTEXT_BOUND_PRIOR"]["mean"]
    primary_cv = per_arm_recall_summary["ARM_CONTEXT_BOUND_PRIOR"]["cv"]
    hybrid = per_arm_recall_summary["ARM_HYBRID_PRIOR_PLUS_EXEMPLAR"]["mean"]
    hybrid_cv = per_arm_recall_summary["ARM_HYBRID_PRIOR_PLUS_EXEMPLAR"]["cv"]
    oracle = per_arm_recall_summary["ARM_ORACLE_TRUE_SCHEMA"]["mean"]

    # Non-oracle max (for fairness ceiling)
    max_nonoracle = max(per_arm_recall_summary[arm]["mean"] for arm in EXPECTED_ARMS
                        if arm != "ARM_ORACLE_TRUE_SCHEMA")

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
        verdict_reason = ("ORACLE_BROKEN: oracle_recall=%.3f <= %.2f"
                          % (oracle, HF_ORACLE_FLOOR))
    elif rand > HF_RANDOM_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = ("RANDOM_TOO_HIGH: rand=%.3f > %.2f (control leak)"
                          % (rand, HF_RANDOM_CEILING))
    elif max_nonoracle > HF_FAIRNESS_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = ("FAIRNESS_VIOLATION: non-oracle arm max=%.3f > %.2f"
                          % (max_nonoracle, HF_FAIRNESS_CEILING))
    elif primary <= exemplar:
        verdict = "HARD_FAIL"
        verdict_reason = ("CONTEXT_PRIOR_NO_LIFT: primary=%.3f <= exemplar=%.3f "
                          "(HRR-bound prior provides no value over ANCHOR 3 cheap mechanism)"
                          % (primary, exemplar))
    elif n_seeds > 1 and primary_cv >= HF_CV_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("UNSTABLE: primary cv=%.3f >= %.2f" % (primary_cv, HF_CV_MAX))
    elif (primary >= HP_CONTEXT_PRIOR_FLOOR
          and hybrid >= HP_HYBRID_FLOOR
          and (n_seeds == 1 or primary_cv < HP_CV_MAX)
          and (n_seeds == 1 or hybrid_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "SCHEMA_INSTANTIATION_SUPPORTED: primary=%.3f (>=%.2f) | hybrid=%.3f (>=%.2f) | "
            "lift_over_exemplar=+%.3f"
            % (primary, HP_CONTEXT_PRIOR_FLOOR, hybrid, HP_HYBRID_FLOOR,
               primary - exemplar))
    elif MIDDLE_PRIOR_LO <= primary < MIDDLE_PRIOR_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("PARTIAL_SIGNAL: primary=%.3f in [%.2f, %.2f); "
                          "HRR prior present but below HP floor"
                          % (primary, MIDDLE_PRIOR_LO, MIDDLE_PRIOR_HI))
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("BOUNDARY: primary=%.3f exemplar=%.3f hybrid=%.3f"
                          % (primary, exemplar, hybrid))

    verdict_msg = (
        "%s | %s | primary[CONTEXT_BOUND_PRIOR]=%.3f hybrid=%.3f exemplar=%.3f "
        "base=%.3f rand=%.3f oracle=%.3f cv_primary=%.3f cv_hybrid=%.3f "
        "arms_distinct=%s n_seeds=%d"
    ) % (verdict, verdict_reason, primary, hybrid, exemplar, base, rand, oracle,
         primary_cv, hybrid_cv, all_distinct, n_seeds)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_recall_summary": per_arm_recall_summary,
        "primary_arm": PRIMARY_ARM,
        "primary_recall": primary,
        "hybrid_recall": hybrid,
        "exemplar_bayes_recall": exemplar,
        "baseline_recall": base,
        "random_recall": rand,
        "oracle_recall": oracle,
        "lift_over_exemplar": primary - exemplar,
        "hybrid_lift_over_primary": hybrid - primary,
        "primary_cv": primary_cv,
        "hybrid_cv": hybrid_cv,
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
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_SLOT=%d M_SLOTS=%d K_SCH=%d NEX=%d seeds=%s "
          "K_EXEMPLAR=%d BETA=%.1f ALPHA=%.2f MASK_FRAC=%.2f" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS,
              N_EXEMPLARS_PER_SCHEMA, SEEDS, K_EXEMPLAR, BETA_TEMP, HYBRID_ALPHA,
              MASK_FRACTION), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_recall_at_1_masked"], "missing arm %s" % arm
            ora = r["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
            base = r["per_arm_recall_at_1_masked"]["ARM_NO_SCHEMA_BASELINE"]
            primary = r["per_arm_recall_at_1_masked"]["ARM_CONTEXT_BOUND_PRIOR"]
            hybrid = r["per_arm_recall_at_1_masked"]["ARM_HYBRID_PRIOR_PLUS_EXEMPLAR"]
            exemplar = r["per_arm_recall_at_1_masked"]["ARM_EXEMPLAR_BAYES_K20"]
            rand = r["per_arm_recall_at_1_masked"]["ARM_RANDOM_PRIOR"]
            assert r["arms_differ_verified"], "arms_distinct check FAILED"
            assert ora >= 0.50, "oracle recall %.3f too low" % ora
            print("[selftest] OK primary=%.3f hybrid=%.3f exemplar=%.3f base=%.3f "
                  "rand=%.3f oracle=%.3f arms_distinct=%s n_unique=%d/%d" % (
                      primary, hybrid, exemplar, base, rand, ora,
                      r["arms_differ_verified"],
                      r["n_unique_arm_hashes"], len(EXPECTED_ARMS)), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   ("SELFTEST_OK: arms differ, oracle=%.3f primary=%.3f "
                                    "hybrid=%.3f exemplar=%.3f"
                                    % (ora, primary, hybrid, exemplar)),
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
        print("[seed=%d] complete in %.1fs primary[CONTEXT]=%.3f hybrid=%.3f "
              "arms_distinct=%s" % (
                  seed, time.time() - t0,
                  result["per_arm_recall_at_1_masked"]["ARM_CONTEXT_BOUND_PRIOR"],
                  result["per_arm_recall_at_1_masked"]["ARM_HYBRID_PRIOR_PLUS_EXEMPLAR"],
                  result["arms_differ_verified"]), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_context_bound_prior_primary_mechanism"
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
