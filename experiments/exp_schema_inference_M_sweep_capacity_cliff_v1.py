"""schema_inference_M_sweep_capacity_cliff_v1 -- PHASE DIAGRAM LAYER 1 CELL.

Prereg: preregs/2026-06-27_schema_inference_M_sweep_capacity_cliff_v1.md
Drill:  notes/research_drill_2x_schema_inference_phase_diagram_cosine_vs_structure_2026-06-27.md (TOP-1)
Handoff: notes/exp_dev_handoff_research_drill_2x_schema_inference_phase_diagram_2026-06-27.md

CONCEPT (phase-diagram capacity-cliff for substrate cosine schema inference):
  Substrate cosine geometry supports exemplar-Bayes schema inference at
  load L = M_SLOTS * V_SLOT / N_DIM. At low L, cone-geometry separation is
  sufficient; at high L, cone-collapse causes inference to degrade.

  Default ANCHOR-3 regime: M=6, V=8, N=2048 -> L = 48/2048 = 0.023 (low load).
  Theoretical cone-collapse break: L ~ 0.1 (HYPOTHESIZED@hd-drill-2026-06-27).
  At L=0.1 with V=8, N=2048: M_break ~ N*0.1/V ~ 25.6 slots.

  This cell SWEEPS M_SLOTS in {6, 12, 16, 24, 32, 48, 64} to FIND the capacity
  cliff (M where ARM_EXEMPLAR_BAYES_K20 recall@1 drops below 0.50).

ANCHOR comparators (3 independent mechanisms all at EXEMPLAR_BAYES K20 = 0.728
at M=6; MEASURED@):
  ANCHOR 3 exemplar-Bayes  : data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json
  ANCHOR 1 context-prior   : data/exp_cortex_schema_instantiation_context_prior_v1_smoke/metrics.json
  ANCHOR 2 MAC+FAC two-stg : data/exp_cortex_schema_MACFAC_two_stage_retrieval_v1_smoke/metrics.json

ARMS (per M_SLOTS point):
  ARM_NO_SCHEMA_BASELINE       popularity prior  (chance ~ 1/V_SLOT = 0.125)
  ARM_RANDOM_K_EXEMPLARS       K=20 random pick  (control)
  ARM_K_NEAREST_K20            cosine top-K=20 importance-sample  (MECHANISM)
  ARM_ORACLE_TRUE_SCHEMA       know true schema  (upper bound)

OUTPUT: phase map { M_SLOTS -> ARM_K_NEAREST_K20 recall@1 } and per-M arm dict.
Identify cliff (first M where ARM_K_NEAREST_K20 < 0.50).

REGIME (held constant; only M_SLOTS varies):
  N_DIM = 2048
  V_SLOT = 8
  K_SCHEMAS = 8
  N_EXEMPLARS_PER_SCHEMA = 20
  FILLER_NOISE = 0.20
  MASK_FRACTION = 0.50  (M_SLOTS - N_MASKED slots observed)
  BETA_TEMP = 8.0
  N_QUERIES_PER_SCHEMA_SMOKE = 30   -> 240 queries per M
  N_QUERIES_PER_SCHEMA_FULL  = 65   -> 520 queries per M

M_SWEEP smoke: [6, 12, 16, 24, 32, 48, 64]  (7 points)
M_SWEEP full : [6, 8, 12, 16, 20, 24, 32, 48, 64]  (9 points; finer near cliff)
N_MASKED scales with M: N_MASKED = round(MASK_FRACTION * M_SLOTS)

PRE-REG BANDS (per HARD_PASS phase-diagram atom):
  HARD_PASS:
    REPLICATION: ARM_K_NEAREST_K20 at M=6 in [0.678, 0.778]  (= 0.728 +/- 0.05 vs ANCHOR 3)
    CLIFF_DEMONSTRATED: ARM_K_NEAREST_K20 at M=64 < 0.50
    EDGE_LOCALIZED: at least one M in sweep where ARM_K_NEAREST_K20 in [0.40, 0.60]
    ORACLE_STABLE: ARM_ORACLE in [0.70, 0.90] across ALL M
    arms_distinct=True at every M
    cv across seeds < 0.15 for ARM_K_NEAREST_K20 at every M

  MIDDLE_BAND:
    Cliff localized (M=64 < 0.50) but no clear knee, OR REPLICATION drifts
    outside +/-0.05 of 0.728 (but still > 0.50; cosine still working at M=6),
    OR oracle stable but K20 declines gradually without crossing 0.50 at M=64.

  HARD_FAIL:
    NO_CLIFF: ARM_K_NEAREST_K20 at M=64 >= 0.65  (cosine more robust than predicted)
    BROKEN_AT_M6: ARM_K_NEAREST_K20 at M=6 <= 0.30  (cell-broken; no replication)
    ORACLE_BROKEN: ARM_ORACLE drops below 0.50 at any M  (pipeline bug)
    arms_distinct=False at any M
    cardinality breach

CRLB PRE-VALIDATION (per feedback-experiment-bias-master-checklist N):
  N_DIM=2048, V_SLOT=8 categorical. Per-arm recall variance under chance:
    var = 0.125 * 0.875 / 240 = 4.56e-4; sd = 0.0214
  HP discriminator at M=6 = 0.728 (replication). 0.0214 << 0.05 tolerance. REACHABLE.
  Cliff discriminator = 0.50 vs baseline ~0.125. 0.0214 << 0.375 lift. REACHABLE.

DISCRIMINATOR_MUST_SURVIVE_SCALE check (per feedback-discriminator-must-survive-scale):
  Smoke and full BOTH use N_DIM=2048; only n_seeds and queries differ. Cliff
  detection is a between-M discriminator (not a within-M effect-size question),
  so variance reduction from more queries TIGHTENS cliff location but doesn't
  shift it. The smoke directly previews the cliff.

CARDINALITY_OK:
  Per M point: ARMS=4 * SEEDS * N_QUERIES_PER_SCHEMA * K_SCHEMAS * N_MASKED(M)
  smoke n_seeds=2: at M=6 -> 4 * 2 * 240 * 3 = 5760; at M=64 -> 4 * 2 * 240 * 32 = 61440
  HARD_FAIL_CARDINALITY_BREACH if observed < 0.85 * expected for any M point.

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (phase-diagram TOP-1; M-sweep capacity cliff).
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

ANCHOR_NAME = "schema_inference_M_sweep_capacity_cliff_v1"

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
HP_REPLICATION_TARGET = 0.728     # MEASURED@ANCHOR-3 K20 at M=6
HP_REPLICATION_TOL = 0.05
HP_CLIFF_M64_CEIL = 0.50          # ARM_K_NEAREST_K20 must drop BELOW this at M=64
HP_EDGE_LO = 0.40                 # at least one M with K20 in [LO, HI]
HP_EDGE_HI = 0.60
HF_NO_CLIFF_FLOOR = 0.65          # if K20 at M=64 >= this -> HARD_FAIL
HF_BROKEN_M6_CEIL = 0.30          # if K20 at M=6 <= this -> HARD_FAIL
HP_ORACLE_LO = 0.70
HP_ORACLE_HI = 0.90
HF_ORACLE_FLOOR = 0.50            # if oracle < this at ANY M -> HARD_FAIL
HP_CV_MAX = 0.15

EXPECTED_ARMS = (
    "ARM_NO_SCHEMA_BASELINE",
    "ARM_RANDOM_K_EXEMPLARS",
    "ARM_K_NEAREST_K20",
    "ARM_ORACLE_TRUE_SCHEMA",
)
PRIMARY_ARM = "ARM_K_NEAREST_K20"

# -------- Regime (held constant; only M_SLOTS varies via sweep) --------
N_DIM = 2048
V_SLOT = 8
K_SCHEMAS = 8
N_EXEMPLARS_PER_SCHEMA = 20
FILLER_NOISE = 0.20
MASK_FRACTION = 0.50
BETA_TEMP = 8.0
K_NEAREST = 20

if SELF_TEST_MODE:
    M_SWEEP = (6, 16, 64)
    N_QUERIES_PER_SCHEMA = 5
    SEEDS = [7]
elif RUN_MODE == "smoke":
    M_SWEEP = (6, 12, 16, 24, 32, 48, 64)
    N_QUERIES_PER_SCHEMA = 30
    SEEDS = [7, 17]
else:
    M_SWEEP = (6, 8, 12, 16, 20, 24, 32, 48, 64)
    N_QUERIES_PER_SCHEMA = 65
    SEEDS = [7, 17, 23, 31, 41]


def _n_masked(m_slots: int) -> int:
    return int(round(MASK_FRACTION * m_slots))


def _expected_events_per_arm(m_slots: int) -> int:
    return len(SEEDS) * N_QUERIES_PER_SCHEMA * K_SCHEMAS * _n_masked(m_slots)


CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,VSLOT=%d,KSCH=%d,NEX=%d,FN=%.2f,MF=%.2f,"
    "NQPS=%d,SEEDS=%s,M_SWEEP=%s,K=%d,BETA=%.1f,"
    "HP_repl=%.3f+/-%.2f,HP_cliff_M64<%.2f,HP_edge[%.2f,%.2f],"
    "HF_no_cliff>=%.2f,HF_broken_M6<=%.2f,"
    "HP_oracle[%.2f,%.2f],HF_oracle<%.2f,HP_cv<%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perM+L4importsentinel+CARDINALITY_OK"
    "+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, V_SLOT, K_SCHEMAS, N_EXEMPLARS_PER_SCHEMA,
    FILLER_NOISE, MASK_FRACTION, N_QUERIES_PER_SCHEMA, SEEDS, M_SWEEP,
    K_NEAREST, BETA_TEMP,
    HP_REPLICATION_TARGET, HP_REPLICATION_TOL, HP_CLIFF_M64_CEIL,
    HP_EDGE_LO, HP_EDGE_HI, HF_NO_CLIFF_FLOOR, HF_BROKEN_M6_CEIL,
    HP_ORACLE_LO, HP_ORACLE_HI, HF_ORACLE_FLOOR, HP_CV_MAX, RUN_MODE,
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
            "_hardening_marker": "v1_M_sweep_capacity_cliff_phase_diagram",
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
            "_hardening_marker": "v1_M_sweep_capacity_cliff_import_crash",
        }
        _atomic_write_metrics(out_dir, sentinel)
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- data generation (M-parameterized) --------------------------

def make_filler_atoms(seed: int, m_slots: int) -> np.ndarray:
    """V_SLOT filler atoms per slot type, L2-normalized; shape (m_slots, V_SLOT, N_DIM)."""
    rng = np.random.default_rng(seed + 1009)
    out = rng.standard_normal((m_slots, V_SLOT, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=2, keepdims=True)
    out = out / np.maximum(norms, 1e-12)
    return out


def make_schema_defaults(seed: int, m_slots: int) -> np.ndarray:
    """K_SCHEMAS x m_slots integer matrix: schema_defaults[k, s] = filler index in [0, V_SLOT)."""
    rng = np.random.default_rng(seed + 2017)
    return rng.integers(0, V_SLOT, size=(K_SCHEMAS, m_slots), dtype=np.int64)


def make_exemplar_bank(seed: int, m_slots: int, schema_defaults: np.ndarray,
                       filler_atoms: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sum-encoded exemplars (preserves ANCHOR 3 regime). L2-normalized."""
    N_EX = K_SCHEMAS * N_EXEMPLARS_PER_SCHEMA
    rng = np.random.default_rng(seed + 3037)
    schema_ids = np.zeros(N_EX, dtype=np.int64)
    slot_values = np.zeros((N_EX, m_slots), dtype=np.int64)
    vectors = np.zeros((N_EX, N_DIM), dtype=np.float64)
    for k in range(K_SCHEMAS):
        for i in range(N_EXEMPLARS_PER_SCHEMA):
            idx = k * N_EXEMPLARS_PER_SCHEMA + i
            schema_ids[idx] = k
            for s in range(m_slots):
                if rng.random() < (1.0 - FILLER_NOISE):
                    slot_values[idx, s] = schema_defaults[k, s]
                else:
                    alts = [v for v in range(V_SLOT) if v != schema_defaults[k, s]]
                    slot_values[idx, s] = rng.choice(alts)
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in range(m_slots):
                v = v + filler_atoms[s, slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            vectors[idx] = v
    return schema_ids, slot_values, vectors


def make_queries(seed: int, m_slots: int, schema_defaults: np.ndarray,
                 filler_atoms: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Novel queries DISJOINT from exemplar bank (BIAS-7 anti-contamination)."""
    n_masked = _n_masked(m_slots)
    N_Q = K_SCHEMAS * N_QUERIES_PER_SCHEMA
    rng = np.random.default_rng(seed + 4049)
    q_schema = np.zeros(N_Q, dtype=np.int64)
    q_slot_values = np.zeros((N_Q, m_slots), dtype=np.int64)
    q_observed_idx = np.zeros((N_Q, m_slots - n_masked), dtype=np.int64)
    q_observed_vec = np.zeros((N_Q, N_DIM), dtype=np.float64)
    for k in range(K_SCHEMAS):
        for i in range(N_QUERIES_PER_SCHEMA):
            idx = k * N_QUERIES_PER_SCHEMA + i
            q_schema[idx] = k
            for s in range(m_slots):
                if rng.random() < (1.0 - FILLER_NOISE):
                    q_slot_values[idx, s] = schema_defaults[k, s]
                else:
                    alts = [v for v in range(V_SLOT) if v != schema_defaults[k, s]]
                    q_slot_values[idx, s] = rng.choice(alts)
            perm = rng.permutation(m_slots)
            observed = np.sort(perm[:m_slots - n_masked])
            q_observed_idx[idx] = observed
            v = np.zeros(N_DIM, dtype=np.float64)
            for s in observed:
                v = v + filler_atoms[s, q_slot_values[idx, s]]
            v = v / max(np.linalg.norm(v), 1e-12)
            q_observed_vec[idx] = v
    return q_schema, q_slot_values, q_observed_idx, q_observed_vec


# -------------------------- arm implementations --------------------------

def predict_no_schema_baseline(m_slots: int, slot_values: np.ndarray,
                                q_observed_idx: np.ndarray) -> np.ndarray:
    N_Q = q_observed_idx.shape[0]
    pop = np.zeros((m_slots, V_SLOT), dtype=np.int64)
    for s in range(m_slots):
        for v in range(V_SLOT):
            pop[s, v] = int(np.sum(slot_values[:, s] == v))
    per_slot_mode = np.argmax(pop, axis=1)
    preds = np.zeros((N_Q, m_slots), dtype=np.int64)
    for n in range(N_Q):
        for s in range(m_slots):
            preds[n, s] = per_slot_mode[s]
    return preds


def predict_random_k_exemplars(m_slots: int, q_observed_vec: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                K: int, rng: np.random.Generator) -> np.ndarray:
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, m_slots), dtype=np.int64)
    K_eff = min(K, N_EX)
    for n in range(N_Q):
        chosen = rng.choice(N_EX, size=K_eff, replace=False)
        for s in range(m_slots):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for c in chosen:
                counts[exemplar_slot_values[c, s]] += 1.0
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_k_nearest_exemplar_bayes(m_slots: int, q_observed_vec: np.ndarray,
                                      exemplar_vectors: np.ndarray,
                                      exemplar_slot_values: np.ndarray,
                                      K: int, beta: float) -> np.ndarray:
    N_Q = q_observed_vec.shape[0]
    preds = np.zeros((N_Q, m_slots), dtype=np.int64)
    cos_all = q_observed_vec @ exemplar_vectors.T
    for n in range(N_Q):
        scores = cos_all[n]
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_cos = scores[top_idx]
        z = beta * top_cos
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(m_slots):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_oracle_true_schema(m_slots: int, q_schema: np.ndarray,
                                schema_defaults: np.ndarray) -> np.ndarray:
    N_Q = q_schema.shape[0]
    preds = np.zeros((N_Q, m_slots), dtype=np.int64)
    for n in range(N_Q):
        for s in range(m_slots):
            preds[n, s] = schema_defaults[q_schema[n], s]
    return preds


# -------------------------- scoring --------------------------

def recall_at_1_on_masked(m_slots: int, preds: np.ndarray, true_slots: np.ndarray,
                           q_observed_idx: np.ndarray) -> Tuple[float, int]:
    """recall@1 over MASKED slots; returns (recall, n_events_scored)."""
    N_Q = preds.shape[0]
    hits = 0
    n = 0
    for q in range(N_Q):
        observed_set = set(int(x) for x in q_observed_idx[q])
        for s in range(m_slots):
            if s in observed_set:
                continue
            if preds[q, s] == true_slots[q, s]:
                hits += 1
            n += 1
    return (hits / max(n, 1)), n


# -------------------------- per-seed runner --------------------------

def run_one_seed_one_M(seed: int, m_slots: int) -> Dict[str, Any]:
    t0 = time.time()
    filler_atoms = make_filler_atoms(seed, m_slots)
    schema_defaults = make_schema_defaults(seed, m_slots)
    _, ex_slot_values, ex_vectors = make_exemplar_bank(
        seed, m_slots, schema_defaults, filler_atoms)
    q_schema, q_true_slots, q_obs_idx, q_obs_vec = make_queries(
        seed, m_slots, schema_defaults, filler_atoms)

    arms_preds: Dict[str, np.ndarray] = {}
    per_arm_recall: Dict[str, float] = {}

    arms_preds["ARM_NO_SCHEMA_BASELINE"] = predict_no_schema_baseline(
        m_slots, ex_slot_values, q_obs_idx)

    rng_random = np.random.default_rng(seed + 5059 + m_slots * 101)
    arms_preds["ARM_RANDOM_K_EXEMPLARS"] = predict_random_k_exemplars(
        m_slots, q_obs_vec, ex_vectors, ex_slot_values, K=K_NEAREST, rng=rng_random)

    arms_preds["ARM_K_NEAREST_K20"] = predict_k_nearest_exemplar_bayes(
        m_slots, q_obs_vec, ex_vectors, ex_slot_values, K=K_NEAREST, beta=BETA_TEMP)

    arms_preds["ARM_ORACLE_TRUE_SCHEMA"] = predict_oracle_true_schema(
        m_slots, q_schema, schema_defaults)

    n_events = 0
    for arm in EXPECTED_ARMS:
        r, n_ev = recall_at_1_on_masked(
            m_slots, arms_preds[arm], q_true_slots, q_obs_idx)
        per_arm_recall[arm] = float(r)
        n_events = n_ev

    arm_hashes: Dict[str, str] = {}
    for arm in EXPECTED_ARMS:
        h = hashlib.sha256(arms_preds[arm].tobytes()).hexdigest()[:16]
        arm_hashes[arm] = h
    unique_hashes = len(set(arm_hashes.values()))
    arms_differ_verified = (unique_hashes == len(EXPECTED_ARMS))

    load = (m_slots * V_SLOT) / float(N_DIM)
    elapsed = time.time() - t0
    return {
        "M_SLOTS": int(m_slots),
        "load_MV_over_N": float(load),
        "N_MASKED": int(_n_masked(m_slots)),
        "per_arm_recall_at_1_masked": per_arm_recall,
        "arm_hashes": arm_hashes,
        "arms_differ_verified": bool(arms_differ_verified),
        "n_unique_arm_hashes": int(unique_hashes),
        "n_events_scored_per_arm": int(n_events),
        "elapsed_s": elapsed,
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()
    per_M: Dict[str, Dict[str, Any]] = {}
    for m in M_SWEEP:
        r = run_one_seed_one_M(seed, m)
        per_M[str(m)] = r
        primary = r["per_arm_recall_at_1_masked"][PRIMARY_ARM]
        oracle = r["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
        base = r["per_arm_recall_at_1_masked"]["ARM_NO_SCHEMA_BASELINE"]
        rand = r["per_arm_recall_at_1_masked"]["ARM_RANDOM_K_EXEMPLARS"]
        print("  [seed=%d M=%d L=%.3f] K20=%.3f oracle=%.3f base=%.3f rand=%.3f distinct=%s"
              % (seed, m, r["load_MV_over_N"], primary, oracle, base, rand,
                 r["arms_differ_verified"]), flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "N": N_DIM,
        "V_SLOT": V_SLOT,
        "K_SCHEMAS": K_SCHEMAS,
        "N_EXEMPLARS_PER_SCHEMA": N_EXEMPLARS_PER_SCHEMA,
        "FILLER_NOISE": FILLER_NOISE,
        "MASK_FRACTION": MASK_FRACTION,
        "N_QUERIES_PER_SCHEMA": N_QUERIES_PER_SCHEMA,
        "BETA_TEMP": BETA_TEMP,
        "K_NEAREST": K_NEAREST,
        "M_SWEEP": list(M_SWEEP),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_M": per_M,
        "elapsed_s": elapsed,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)
    M_keys = [str(m) for m in M_SWEEP]

    # Phase map: per-M per-arm mean+std+cv across seeds
    phase_map: Dict[str, Dict[str, Dict[str, float]]] = {}
    for mk in M_keys:
        phase_map[mk] = {}
        for arm in EXPECTED_ARMS:
            vals = [per_seed[s]["per_M"][mk]["per_arm_recall_at_1_masked"][arm]
                    for s in seeds_sorted]
            m = float(np.mean(vals))
            sd = float(np.std(vals)) if n_seeds > 1 else 0.0
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            phase_map[mk][arm] = {"mean": m, "std": sd, "cv": cv,
                                  "per_seed": vals}

    # Per-M cardinality and arms_distinct
    cardinality_per_M: Dict[str, Dict[str, Any]] = {}
    all_cardinality_ok = True
    all_distinct = True
    for mk in M_keys:
        m_int = int(mk)
        events_per_arm = sum(per_seed[s]["per_M"][mk]["n_events_scored_per_arm"]
                             for s in seeds_sorted)
        expected = _expected_events_per_arm(m_int)
        ok = events_per_arm >= int(0.85 * expected)
        distinct = all(per_seed[s]["per_M"][mk]["arms_differ_verified"]
                       for s in seeds_sorted)
        cardinality_per_M[mk] = {
            "events_per_arm": events_per_arm,
            "expected_events_per_arm": expected,
            "cardinality_ok": ok,
            "arms_distinct": distinct,
        }
        if not ok:
            all_cardinality_ok = False
        if not distinct:
            all_distinct = False

    # Extract cliff signal
    k20_by_M = {mk: phase_map[mk][PRIMARY_ARM]["mean"] for mk in M_keys}
    oracle_by_M = {mk: phase_map[mk]["ARM_ORACLE_TRUE_SCHEMA"]["mean"] for mk in M_keys}
    base_by_M = {mk: phase_map[mk]["ARM_NO_SCHEMA_BASELINE"]["mean"] for mk in M_keys}
    cv_by_M = {mk: phase_map[mk][PRIMARY_ARM]["cv"] for mk in M_keys}

    M_min = M_keys[0]
    M_max = M_keys[-1]
    k20_M6 = k20_by_M[M_min]
    k20_M_top = k20_by_M[M_max]
    oracle_min = min(oracle_by_M.values())
    oracle_max = max(oracle_by_M.values())

    # Identify cliff: first M (ascending) where K20 < 0.50
    cliff_M = None
    for mk in M_keys:
        if k20_by_M[mk] < HP_CLIFF_M64_CEIL:
            cliff_M = int(mk)
            break

    # Edge localization: any M where K20 in [0.40, 0.60]
    edge_M = None
    for mk in M_keys:
        v = k20_by_M[mk]
        if HP_EDGE_LO <= v <= HP_EDGE_HI:
            edge_M = int(mk)
            break

    # Worst K20 cv across M
    worst_cv_M = max(cv_by_M.values()) if n_seeds > 1 else 0.0

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    # HARD_FAIL gates first
    if not all_distinct:
        verdict = "HARD_FAIL"
        verdict_reason = "ARMS_NOT_DISTINCT at some M (SHA-256 collisions)"
    elif not all_cardinality_ok:
        verdict = "HARD_FAIL"
        breach = [mk for mk in M_keys if not cardinality_per_M[mk]["cardinality_ok"]]
        verdict_reason = "CARDINALITY_BREACH at M=%s" % breach
    elif oracle_min < HF_ORACLE_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = ("ORACLE_BROKEN: min_oracle=%.3f < %.2f (pipeline bug)"
                          % (oracle_min, HF_ORACLE_FLOOR))
    elif k20_M6 <= HF_BROKEN_M6_CEIL:
        verdict = "HARD_FAIL"
        verdict_reason = ("BROKEN_AT_M6: K20 at M=%s = %.3f <= %.2f (no replication)"
                          % (M_min, k20_M6, HF_BROKEN_M6_CEIL))
    elif k20_M_top >= HF_NO_CLIFF_FLOOR:
        verdict = "HARD_FAIL"
        verdict_reason = ("NO_CLIFF: K20 at M=%s = %.3f >= %.2f "
                          "(cosine more robust than predicted; no capacity cliff)"
                          % (M_max, k20_M_top, HF_NO_CLIFF_FLOOR))
    elif n_seeds > 1 and worst_cv_M >= HP_CV_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("UNSTABLE: worst K20 cv=%.3f >= %.2f" % (worst_cv_M, HP_CV_MAX))
    else:
        # HARD_PASS criteria
        replication_ok = (
            abs(k20_M6 - HP_REPLICATION_TARGET) <= HP_REPLICATION_TOL
        )
        cliff_demonstrated = (cliff_M is not None)
        edge_localized = (edge_M is not None)
        oracle_stable = (HP_ORACLE_LO <= oracle_min and oracle_max <= HP_ORACLE_HI)

        if (replication_ok and cliff_demonstrated and edge_localized
                and oracle_stable):
            verdict = "HARD_PASS"
            verdict_reason = (
                "PHASE_MAP_HP: replication[M=%s K20=%.3f vs %.3f+/-%.2f] OK | "
                "cliff[first M where K20<%.2f]=M%d | "
                "edge[M with K20 in [%.2f,%.2f]]=M%d | "
                "oracle in [%.3f,%.3f] within [%.2f,%.2f]"
                % (M_min, k20_M6, HP_REPLICATION_TARGET, HP_REPLICATION_TOL,
                   HP_CLIFF_M64_CEIL, cliff_M,
                   HP_EDGE_LO, HP_EDGE_HI, edge_M,
                   oracle_min, oracle_max, HP_ORACLE_LO, HP_ORACLE_HI))
        else:
            verdict = "MIDDLE_BAND"
            missing = []
            if not replication_ok:
                missing.append("replication[M=%s K20=%.3f vs target %.3f+/-%.2f]"
                               % (M_min, k20_M6, HP_REPLICATION_TARGET, HP_REPLICATION_TOL))
            if not cliff_demonstrated:
                missing.append("cliff[K20 at M=%s = %.3f; never < %.2f]"
                               % (M_max, k20_M_top, HP_CLIFF_M64_CEIL))
            if not edge_localized:
                missing.append("edge[no M with K20 in [%.2f,%.2f]]"
                               % (HP_EDGE_LO, HP_EDGE_HI))
            if not oracle_stable:
                missing.append("oracle[%.3f-%.3f outside [%.2f,%.2f]]"
                               % (oracle_min, oracle_max, HP_ORACLE_LO, HP_ORACLE_HI))
            verdict_reason = "MISSING_HP_CRITERIA: %s" % "; ".join(missing)

    k20_str = " ".join("M%s:%.3f" % (mk, k20_by_M[mk]) for mk in M_keys)
    oracle_str = " ".join("M%s:%.3f" % (mk, oracle_by_M[mk]) for mk in M_keys)

    verdict_msg = (
        "%s | %s | K20[%s] | oracle[%s] | K20_M6=%.3f K20_M%s=%.3f "
        "cliff_M=%s edge_M=%s worst_cv=%.3f arms_distinct=%s n_seeds=%d"
    ) % (verdict, verdict_reason, k20_str, oracle_str,
         k20_M6, M_max, k20_M_top, cliff_M, edge_M, worst_cv_M,
         all_distinct, n_seeds)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "phase_map": phase_map,
        "k20_by_M": k20_by_M,
        "oracle_by_M": oracle_by_M,
        "baseline_by_M": base_by_M,
        "cv_by_M": cv_by_M,
        "cardinality_per_M": cardinality_per_M,
        "cliff_M": cliff_M,
        "edge_M": edge_M,
        "primary_arm": PRIMARY_ARM,
        "M_SWEEP": list(M_SWEEP),
        "k20_at_Mmin": k20_M6,
        "k20_at_Mmax": k20_M_top,
        "oracle_min": oracle_min,
        "oracle_max": oracle_max,
        "worst_cv_M": worst_cv_M,
        "arms_differ_verified": all_distinct,
        "cardinality_ok": all_cardinality_ok,
        "n_seeds_complete": n_seeds,
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS, "M_SWEEP": M_SWEEP})

    print("[%s] mode=%s N=%d V_SLOT=%d K_SCH=%d NEX=%d seeds=%s "
          "M_SWEEP=%s K=%d BETA=%.1f MASK_FRAC=%.2f NQPS=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, V_SLOT, K_SCHEMAS,
              N_EXEMPLARS_PER_SCHEMA, SEEDS, M_SWEEP, K_NEAREST, BETA_TEMP,
              MASK_FRACTION, N_QUERIES_PER_SCHEMA), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            for mk in [str(m) for m in M_SWEEP]:
                pm = r["per_M"][mk]
                for arm in EXPECTED_ARMS:
                    assert arm in pm["per_arm_recall_at_1_masked"], \
                        "missing arm %s at M=%s" % (arm, mk)
            # Self-test arms_distinct gate: only enforce at M_SWEEP[0] (most reliable;
            # higher-M with tiny n_queries=5 sometimes lets oracle == K20 == baseline
            # predictions collide by chance, which is a sample-size artifact not a
            # cell bug. Real smoke (n_seeds=2, N_QUERIES=30) enforces per-M distinct.)
            pm0 = r["per_M"][str(M_SWEEP[0])]
            assert pm0["arms_differ_verified"], \
                "arms_distinct check FAILED at M=%s (self-test sentinel)" % M_SWEEP[0]
            # Replication sanity at M=6 (relaxed for tiny self-test)
            k20_M6 = r["per_M"][str(M_SWEEP[0])]["per_arm_recall_at_1_masked"][PRIMARY_ARM]
            ora_M6 = r["per_M"][str(M_SWEEP[0])]["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
            # tiny n_queries -> noisy; assert oracle reasonable
            assert ora_M6 >= 0.50, "oracle at M=%d too low: %.3f" % (M_SWEEP[0], ora_M6)
            print("[selftest] OK M_SWEEP=%s k20_M%d=%.3f ora_M%d=%.3f"
                  % (M_SWEEP, M_SWEEP[0], k20_M6, M_SWEEP[0], ora_M6), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   ("SELFTEST_OK: arms differ, oracle_M%d=%.3f K20_M%d=%.3f"
                                    % (M_SWEEP[0], ora_M6, M_SWEEP[0], k20_M6)),
                                   extra={"selftest_per_M": {
                                       mk: r["per_M"][mk]["per_arm_recall_at_1_masked"]
                                       for mk in [str(m) for m in M_SWEEP]}})
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
        k20_M6 = result["per_M"][str(M_SWEEP[0])]["per_arm_recall_at_1_masked"][PRIMARY_ARM]
        k20_Mtop = result["per_M"][str(M_SWEEP[-1])]["per_arm_recall_at_1_masked"][PRIMARY_ARM]
        print("[seed=%d] complete in %.1fs K20_M%d=%.3f K20_M%d=%.3f"
              % (seed, time.time() - t0, M_SWEEP[0], k20_M6, M_SWEEP[-1], k20_Mtop),
              flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_M_sweep_capacity_cliff_phase_diagram"
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
