"""schema_inference_cross_schema_overlap_sweep_v1 -- PHASE DIAGRAM TOP-2.

Sweeps the cross-schema slot-overlap fraction to find the regime where
MAC+FAC structural rerank starts beating substrate-cosine EXEMPLAR_BAYES.
At 0% overlap, schemas have disjoint random fillers per slot -> within-schema
cosine dominates -> EXEMPLAR_BAYES wins (ANCHOR 3 MEASURED@0.728). As overlap
grows, schemas SHARE slot fillers (e.g. BIRD.feathers and DRAGON.scales both
bind to a shared 'outer_covering' filler atom) -> cross-schema cosine
inflates -> K-NN routes to wrong schema -> EXEMPLAR_BAYES degrades.
MAC+FAC respects per-slot STRUCTURE so it should be more robust.

Prereg:  preregs/2026-06-27_schema_inference_cross_schema_overlap_sweep_v1.md
Drill:   d:/AI/hd-instrument/notes/research_drill_2x_schema_inference_phase_diagram_cosine_vs_structure_2026-06-27.md (TOP-2)
Handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_drill_2x_schema_inference_phase_diagram_2026-06-27.md (ANCHOR B)

COMPARATORS (absolute paths; cited per META_RULE_AC number-tagging):
  ANCHOR 3 HARD_PASS @ 0% overlap:
    d:/AI/hd-instrument/data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json
    EXEMPLAR_BAYES_K20 = MEASURED@0.728 (cv=0.015)
    ORACLE             = MEASURED@0.809
  ANCHOR 2 HARD_FAIL @ 0% overlap:
    d:/AI/hd-instrument/data/exp_cortex_schema_MACFAC_two_stage_retrieval_v1_smoke/metrics.json
    MAC_PLUS_FAC       = MEASURED@0.665
  M-sweep TOP-1 (no-cliff up to M=1024) MEASURED@same regime: substrate cosine
  more robust on M_SLOTS axis than predicted; TOP-2 tests ORTHOGONAL axis.

CONCEPT:
  ANCHOR 3 used DISJOINT per-slot filler atoms across schemas (each schema
  picks defaults independently from V_SLOT options; with 8 schemas and
  V_SLOT=8 the EXPECTED accidental overlap is ~1/8 of slot-value pairs).
  TOP-2 introduces controlled cross-schema OVERLAP by forcing pairs of
  schemas to share a fraction of (slot, value) defaults. At overlap=0% we
  reproduce ANCHOR 3; at overlap=100% all schemas have identical defaults
  (degenerate -- distinguishable only via exemplar noise).

MECHANISM (cross-schema overlap encoding):
  overlap_frac controls the fraction of (schema, slot) pairs that share
  a default with the previous schema. Implementation:
    For schema k in [1..K-1], for slot s in [0..M-1]:
      if rng.random() < overlap_frac:
        schema_defaults[k, s] = schema_defaults[k-1, s]  # SHARE
      else:
        schema_defaults[k, s] = rng.integers(0, V_SLOT)  # FRESH
  Schema 0 is always fresh. Average shared slots per schema-pair = overlap_frac
  * M_SLOTS. At overlap=0.5 with M=6, each schema shares ~3 slots with its
  neighbor in the chain.

  EXEMPLAR_BAYES degrades because: shared (slot, value) pairs across schemas
  cause cosine similarity to confuse schema membership.
  MAC+FAC is HYPOTHESIZED to stay flatter because: per-slot structural
  alignment respects WHICH slot the match comes from, so a query observation
  on slot HABITAT matching candidate slot HABITAT (regardless of which schema
  the candidate came from) is fundamentally the same signal -- and the
  candidates after FAC re-rank tend to be the ones with most slot-matches
  on observed slots, which is the actual structural signature.

ARMS (5):
  ARM_NO_SCHEMA_BASELINE          chance: per-slot mode over ALL exemplars (popularity)
  ARM_EXEMPLAR_BAYES_K20          ANCHOR 3 primary; expected to DEGRADE with overlap
  ARM_MAC_PLUS_FAC                MECHANISM under test; expected to stay flatter
  ARM_ORACLE_TRUE_SCHEMA          know-true-schema upper bound
  ARM_RANDOM_STRUCTURAL           MAC + random rerank; control distinguishing
                                  structural alignment from any rerank stage

REGIME (hold constant; preserve ANCHOR 3 regime at 0% baseline per prompt):
  N_DIM=2048 (both smoke and full per prompt design)
  K_SCHEMAS=8 V_SLOT=8 M_SLOTS=6 NEX=20 FILLER_NOISE=0.20 MASK_FRACTION=0.50
  BETA_TEMP=8.0 MAC_SPARSE_FRAC=0.10 FAC_K_AFTER_MAC=20 K_TOP_FOR_VOTE=5
  SMOKE: overlap_grid=[0.00, 0.10, 0.25, 0.50, 0.75, 0.90]
         n_queries_per_schema=30 -> 240 events per overlap point
         n_seeds=2 -> ~30-60s smoke wall (per prompt)
  FULL:  overlap_grid=[0.00, 0.10, 0.25, 0.50, 0.67, 0.75, 0.85, 0.90, 0.95]
         n_queries_per_schema=62 -> 496 events per overlap point (~500 target)
         n_seeds=5 -> ~2-3 min wall

PRE-REG BANDS (per prompt spec):
  HARD_PASS (crossing demonstrated):
    At 0% overlap: ARM_EXEMPLAR in [0.678, 0.778] (reproduces ANCHOR 3 0.728 +/- 0.05)
    AND for SOME overlap >= 0.50: ARM_MAC_PLUS_FAC >= ARM_EXEMPLAR
    AND ARM_ORACLE_TRUE_SCHEMA in [0.65, 0.85] across ALL overlaps (pipeline sound)
    AND arms_distinct=True at every overlap point
    AND cv across seeds < 0.15 for primary

  HARD_FAIL:
    EITHER ARM_EXEMPLAR stays > 0.65 at 90% overlap
      (cosine still robust at extreme overlap; structural alignment NEVER helps)
    OR ARM_MAC_PLUS_FAC stays below EXEMPLAR at ALL overlaps (no crossing)
    OR ARM_ORACLE drops below 0.50 at ANY overlap (pipeline broken)
    OR ARM_RANDOM_STRUCTURAL >= ARM_MAC_PLUS_FAC at the crossing overlap
      (FAC mechanism degenerate; rerank is doing the work, not alignment)
    OR cardinality breach
    OR ANY non-oracle arm > 0.95 (FAIRNESS_VIOLATION; regime degenerate)

  MIDDLE_BAND: crossing exists ONLY at extreme 90%+ overlap (substrate cosine
    very hard to break) OR ANCHOR 3 reproduction wider than +/-0.05 but oracle
    sound.

STRATEGIC NOTE: if MAC+FAC crosses EXEMPLAR at any overlap, structural
mechanisms ARE useful at the right phase -- this would justify a Layer-2
phase-operation: 'if overlap > X%, switch from cosine cleanup to structural
rerank.'

CRLB PRE-VALIDATION (per [[feedback-experiment-bias-master-checklist]] N):
  Per overlap point: 240 events * 3 masked = 720 events per arm at smoke.
  var = p(1-p)/n at p=0.70 = 0.21/720 = 2.92e-4; sd = 0.017.
  Crossing-detection requires |MAC_PLUS_FAC - EXEMPLAR| > 2*sd_pooled = 0.048.
  n_seeds=2 reduces this further. CRLB-REACHABLE.

DISCRIMINATOR_MUST_SURVIVE_SCALE check (per [[feedback-discriminator-must-survive-scale]]):
  Smoke uses the SAME N_DIM=2048 as full (Strategy A: smoke-AT-FULL-N).
  Only n_seeds differs (2 vs 5). Crossing signal at 75-90% overlap is
  characteristic of the cosine-cone collapse boundary -- if it appears at
  N=2048 smoke, it will appear at N=2048 full. No scaling risk.

CARDINALITY_OK:
  SMOKE: 6 overlap * 5 arms * 2 seeds * 240 queries * 3 masked = 43200 events
  FULL:  9 overlap * 5 arms * 5 seeds * 496 queries * 3 masked = 334800 events
  HARD_FAIL_CARDINALITY_BREACH if observed < 0.85 * expected.

ARMS-MUST-DIFFER (META_RULE_AF):
  SHA-256 of per-arm prediction matrices PER OVERLAP POINT. unique_hashes
  == len(EXPECTED_ARMS) required at every overlap.

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (drill TOP-2 phase-diagram cross-schema overlap).
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

ANCHOR_NAME = "schema_inference_cross_schema_overlap_sweep_v1"

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
HP_ANCHOR3_REPRO_LO = 0.678         # EXEMPLAR at 0% must be in [0.728 +/- 0.05]
HP_ANCHOR3_REPRO_HI = 0.778
HP_CROSSING_OVERLAP_MIN = 0.50      # crossing required at SOME overlap >= 0.50
HP_ORACLE_LO = 0.65                 # ORACLE in [0.65, 0.85] across all overlaps
HP_ORACLE_HI = 0.85
HP_CV_MAX = 0.15
HF_FAIRNESS_CEILING = 0.95
HF_ORACLE_FLOOR = 0.50              # any overlap with oracle < 0.50 -> harness broken
HF_NO_CROSSING_EXEMPLAR_AT_90 = 0.65  # if EXEMPLAR > 0.65 at 90% overlap -> HF (cosine robust)

EXPECTED_ARMS = (
    "ARM_NO_SCHEMA_BASELINE",
    "ARM_EXEMPLAR_BAYES_K20",
    "ARM_MAC_PLUS_FAC",
    "ARM_ORACLE_TRUE_SCHEMA",
    "ARM_RANDOM_STRUCTURAL",
)
PRIMARY_ARM = "ARM_MAC_PLUS_FAC"
BASELINE_ARM = "ARM_EXEMPLAR_BAYES_K20"

# -------- Regime --------
if SELF_TEST_MODE:
    N_DIM = 512
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 5
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 4
    SEEDS = [7]
    OVERLAP_GRID = [0.0, 0.50, 0.90]  # 3 points for self-test
    BETA_TEMP = 8.0
    MAC_SPARSE_FRAC = 0.10
    FAC_K_AFTER_MAC = 20
    K_TOP_FOR_VOTE = 5
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 20
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 30
    SEEDS = [7, 17]
    OVERLAP_GRID = [0.0, 0.10, 0.25, 0.50, 0.75, 0.90]
    BETA_TEMP = 8.0
    MAC_SPARSE_FRAC = 0.10
    FAC_K_AFTER_MAC = 20
    K_TOP_FOR_VOTE = 5
else:
    N_DIM = 2048
    V_SLOT = 8
    M_SLOTS = 6
    K_SCHEMAS = 8
    N_EXEMPLARS_PER_SCHEMA = 20
    FILLER_NOISE = 0.20
    MASK_FRACTION = 0.50
    N_QUERIES_PER_SCHEMA = 62  # ~500 events per overlap
    SEEDS = [7, 17, 23, 31, 41]
    OVERLAP_GRID = [0.0, 0.10, 0.25, 0.50, 0.67, 0.75, 0.85, 0.90, 0.95]
    BETA_TEMP = 8.0
    MAC_SPARSE_FRAC = 0.10
    FAC_K_AFTER_MAC = 20
    K_TOP_FOR_VOTE = 5

N_MASKED = int(round(MASK_FRACTION * M_SLOTS))
K_EXEMPLAR_BAYES = 20

EXPECTED_N_UNITS = (len(EXPECTED_ARMS) * len(SEEDS) * len(OVERLAP_GRID)
                    * (N_QUERIES_PER_SCHEMA * K_SCHEMAS) * N_MASKED)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,VSLOT=%d,MSLOTS=%d,KSCH=%d,NEX=%d,FN=%.2f,MF=%.2f,"
    "NQPS=%d,SEEDS=%s,OVERLAP_GRID=%s,BETA=%.1f,N_MASKED=%d,"
    "MAC_SPARSE=%.2f,FAC_K=%d,KTOP=%d,K_EXEMPLAR=%d,"
    "HP_anchor3_repro=[%.3f,%.3f],HP_crossing_overlap_min=%.2f,"
    "HP_oracle=[%.2f,%.2f],HP_cv<%.2f,HF_no_crossing_ex_at_90=%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK"
    "+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS, N_EXEMPLARS_PER_SCHEMA,
    FILLER_NOISE, MASK_FRACTION, N_QUERIES_PER_SCHEMA, SEEDS, OVERLAP_GRID,
    BETA_TEMP, N_MASKED, MAC_SPARSE_FRAC, FAC_K_AFTER_MAC, K_TOP_FOR_VOTE,
    K_EXEMPLAR_BAYES,
    HP_ANCHOR3_REPRO_LO, HP_ANCHOR3_REPRO_HI, HP_CROSSING_OVERLAP_MIN,
    HP_ORACLE_LO, HP_ORACLE_HI, HP_CV_MAX, HF_NO_CROSSING_EXEMPLAR_AT_90,
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
            "_hardening_marker": "v1_cross_schema_overlap_phase_diagram",
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
            "_hardening_marker": "v1_cross_schema_overlap_import_crash",
        }
        _atomic_write_metrics(out_dir, sentinel)
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- data generation with cross-schema overlap --------------------------

def make_filler_atoms(seed: int) -> np.ndarray:
    """V_SLOT filler atoms per slot type, L2-normalized; shape (M_SLOTS, V_SLOT, N_DIM)."""
    rng = np.random.default_rng(seed + 1009)
    out = rng.standard_normal((M_SLOTS, V_SLOT, N_DIM)).astype(np.float64)
    norms = np.linalg.norm(out, axis=2, keepdims=True)
    out = out / np.maximum(norms, 1e-12)
    return out


def make_schema_defaults_with_overlap(seed: int, overlap_frac: float) -> np.ndarray:
    """K_SCHEMAS x M_SLOTS defaults with controlled cross-schema overlap.

    Schema 0 fully random. For k >= 1, each slot has overlap_frac chance of
    inheriting from schema k-1 (chain). At overlap=0 -> ANCHOR 3 regime
    (independent randoms). At overlap=1.0 -> all schemas identical defaults.
    """
    rng = np.random.default_rng(seed + 2017 + int(round(overlap_frac * 10000)))
    out = np.zeros((K_SCHEMAS, M_SLOTS), dtype=np.int64)
    out[0] = rng.integers(0, V_SLOT, size=M_SLOTS, dtype=np.int64)
    for k in range(1, K_SCHEMAS):
        for s in range(M_SLOTS):
            if rng.random() < overlap_frac:
                out[k, s] = out[k - 1, s]  # SHARE with previous
            else:
                out[k, s] = int(rng.integers(0, V_SLOT))  # FRESH
    return out


def measure_observed_overlap(schema_defaults: np.ndarray) -> float:
    """Measure actual overlap fraction (slot-value pairs shared across schemas).

    Returns fraction of (slot, value) cells that appear in >1 schema.
    Used to verify overlap mechanism matches the requested overlap_frac.
    """
    M = schema_defaults.shape[1]
    n_shared_pairs = 0
    n_total_pairs = 0
    for s in range(M):
        # Count unique values across schemas at this slot
        vals = schema_defaults[:, s]
        unique_vals, counts = np.unique(vals, return_counts=True)
        # A value is "shared" if it appears in >1 schema
        shared_vals = unique_vals[counts > 1]
        n_shared_pairs += int(np.sum(counts[counts > 1]))
        n_total_pairs += int(len(vals))
    return n_shared_pairs / max(n_total_pairs, 1)


def make_exemplar_bank(seed: int, overlap_frac: float, schema_defaults: np.ndarray,
                       filler_atoms: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build exemplar bank with FILLER_NOISE perturbation."""
    N_EX = K_SCHEMAS * N_EXEMPLARS_PER_SCHEMA
    rng = np.random.default_rng(seed + 3037 + int(round(overlap_frac * 10000)))
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


def make_queries(seed: int, overlap_frac: float, schema_defaults: np.ndarray,
                 filler_atoms: np.ndarray
                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate test queries with masked slots."""
    N_Q = K_SCHEMAS * N_QUERIES_PER_SCHEMA
    rng = np.random.default_rng(seed + 4049 + int(round(overlap_frac * 10000)))
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


# -------------------------- arm implementations (ported from ANCHOR 2/3) --------------------------

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


def predict_exemplar_bayes_k20(q_observed_vec: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                K: int, beta: float) -> np.ndarray:
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


def _build_sparse_codes(vectors: np.ndarray, sparse_frac: float) -> np.ndarray:
    n_keep = max(1, int(round(sparse_frac * vectors.shape[1])))
    abs_v = np.abs(vectors)
    idx_sorted = np.argpartition(-abs_v, n_keep - 1, axis=1)[:, :n_keep]
    out = np.zeros_like(vectors)
    rows = np.arange(vectors.shape[0])[:, None]
    out[rows, idx_sorted] = np.sign(vectors[rows, idx_sorted])
    return out


def _fac_align_scores(q_slot_values: np.ndarray, q_observed_idx: np.ndarray,
                       candidate_indices: np.ndarray,
                       exemplar_slot_values: np.ndarray,
                       filler_atoms: np.ndarray) -> np.ndarray:
    N_Q = q_slot_values.shape[0]
    K_cand = candidate_indices.shape[1]
    scores = np.zeros((N_Q, K_cand), dtype=np.float64)
    for n in range(N_Q):
        observed = q_observed_idx[n]
        cand_idx_n = candidate_indices[n]
        for j, c in enumerate(cand_idx_n):
            s_score = 0.0
            for s in observed:
                qv = filler_atoms[s, q_slot_values[n, s]]
                cv = filler_atoms[s, exemplar_slot_values[c, s]]
                s_score += float(np.dot(qv, cv))
            scores[n, j] = s_score
    return scores


def predict_mac_plus_fac(q_observed_vec: np.ndarray, q_slot_values: np.ndarray,
                          q_observed_idx: np.ndarray,
                          exemplar_vectors: np.ndarray,
                          exemplar_slot_values: np.ndarray,
                          filler_atoms: np.ndarray,
                          mac_K: int, sparse_frac: float, fac_K_top: int,
                          beta: float) -> np.ndarray:
    """MAC+FAC: sparse-dotprod prefilter -> per-slot structural rerank -> vote."""
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)

    q_sparse = _build_sparse_codes(q_observed_vec, sparse_frac)
    ex_sparse = _build_sparse_codes(exemplar_vectors, sparse_frac)
    dot_all = q_sparse @ ex_sparse.T

    K_mac = min(mac_K, N_EX)
    mac_candidates = np.zeros((N_Q, K_mac), dtype=np.int64)
    for n in range(N_Q):
        scores = dot_all[n]
        mac_candidates[n] = np.argpartition(-scores, K_mac - 1)[:K_mac]

    fac_scores = _fac_align_scores(q_slot_values, q_observed_idx, mac_candidates,
                                    exemplar_slot_values, filler_atoms)

    K_top = min(fac_K_top, K_mac)
    for n in range(N_Q):
        s_n = fac_scores[n]
        top_local_idx = np.argpartition(-s_n, K_top - 1)[:K_top]
        top_global_idx = mac_candidates[n, top_local_idx]
        top_fac_scores = s_n[top_local_idx]
        z = beta * top_fac_scores
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_global_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_random_structural(q_observed_vec: np.ndarray,
                                q_observed_idx: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                mac_K: int, sparse_frac: float, fac_K_top: int,
                                beta: float, rng: np.random.Generator) -> np.ndarray:
    """MAC + RANDOM rerank control (distinguishes structural alignment from any rerank)."""
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)

    q_sparse = _build_sparse_codes(q_observed_vec, sparse_frac)
    ex_sparse = _build_sparse_codes(exemplar_vectors, sparse_frac)
    dot_all = q_sparse @ ex_sparse.T

    K_mac = min(mac_K, N_EX)
    mac_candidates = np.zeros((N_Q, K_mac), dtype=np.int64)
    for n in range(N_Q):
        scores = dot_all[n]
        mac_candidates[n] = np.argpartition(-scores, K_mac - 1)[:K_mac]

    fac_scores = rng.random(size=(N_Q, K_mac))

    K_top = min(fac_K_top, K_mac)
    for n in range(N_Q):
        s_n = fac_scores[n]
        top_local_idx = np.argpartition(-s_n, K_top - 1)[:K_top]
        top_global_idx = mac_candidates[n, top_local_idx]
        top_scores = s_n[top_local_idx]
        z = beta * top_scores
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_global_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
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


# -------------------------- per-(seed, overlap) runner --------------------------

def run_one_seed_one_overlap(seed: int, overlap_frac: float) -> Dict[str, Any]:
    t0 = time.time()
    filler_atoms = make_filler_atoms(seed)
    schema_defaults = make_schema_defaults_with_overlap(seed, overlap_frac)
    observed_overlap = measure_observed_overlap(schema_defaults)
    ex_schema_ids, ex_slot_values, ex_vectors = make_exemplar_bank(
        seed, overlap_frac, schema_defaults, filler_atoms)
    q_schema, q_true_slots, q_obs_idx, q_obs_vec = make_queries(
        seed, overlap_frac, schema_defaults, filler_atoms)

    arms_preds: Dict[str, np.ndarray] = {}
    per_arm_recall: Dict[str, float] = {}

    arms_preds["ARM_NO_SCHEMA_BASELINE"] = predict_no_schema_baseline(
        ex_slot_values, q_obs_idx)

    arms_preds["ARM_EXEMPLAR_BAYES_K20"] = predict_exemplar_bayes_k20(
        q_obs_vec, ex_vectors, ex_slot_values, K=K_EXEMPLAR_BAYES, beta=BETA_TEMP)

    arms_preds["ARM_MAC_PLUS_FAC"] = predict_mac_plus_fac(
        q_obs_vec, q_true_slots, q_obs_idx, ex_vectors, ex_slot_values,
        filler_atoms, mac_K=FAC_K_AFTER_MAC, sparse_frac=MAC_SPARSE_FRAC,
        fac_K_top=K_TOP_FOR_VOTE, beta=BETA_TEMP)

    arms_preds["ARM_ORACLE_TRUE_SCHEMA"] = predict_oracle_true_schema(
        q_schema, schema_defaults)

    rng_rand_struct = np.random.default_rng(seed + 6071
                                             + int(round(overlap_frac * 10000)))
    arms_preds["ARM_RANDOM_STRUCTURAL"] = predict_random_structural(
        q_obs_vec, q_obs_idx, ex_vectors, ex_slot_values,
        mac_K=FAC_K_AFTER_MAC, sparse_frac=MAC_SPARSE_FRAC,
        fac_K_top=K_TOP_FOR_VOTE, beta=BETA_TEMP, rng=rng_rand_struct)

    for arm in EXPECTED_ARMS:
        r = recall_at_1_on_masked(arms_preds[arm], q_true_slots, q_obs_idx)
        per_arm_recall[arm] = float(r)

    arm_hashes: Dict[str, str] = {}
    for arm in EXPECTED_ARMS:
        h = hashlib.sha256(arms_preds[arm].tobytes()).hexdigest()[:16]
        arm_hashes[arm] = h
    unique_hashes = len(set(arm_hashes.values()))
    arms_differ_verified = (unique_hashes == len(EXPECTED_ARMS))

    n_events_per_arm = q_obs_vec.shape[0] * N_MASKED
    elapsed = time.time() - t0
    print("  [seed=%d overlap=%.2f obs_overlap=%.3f] EX=%.3f MACFAC=%.3f "
          "ORA=%.3f BASE=%.3f RAND=%.3f arms_distinct=%s (%.1fs)" % (
              seed, overlap_frac, observed_overlap,
              per_arm_recall["ARM_EXEMPLAR_BAYES_K20"],
              per_arm_recall["ARM_MAC_PLUS_FAC"],
              per_arm_recall["ARM_ORACLE_TRUE_SCHEMA"],
              per_arm_recall["ARM_NO_SCHEMA_BASELINE"],
              per_arm_recall["ARM_RANDOM_STRUCTURAL"],
              arms_differ_verified, elapsed), flush=True)

    return {
        "seed": int(seed),
        "overlap_frac": float(overlap_frac),
        "observed_overlap": float(observed_overlap),
        "per_arm_recall_at_1_masked": per_arm_recall,
        "arm_hashes": arm_hashes,
        "arms_differ_verified": bool(arms_differ_verified),
        "n_unique_arm_hashes": int(unique_hashes),
        "n_events_scored_per_arm": int(n_events_per_arm),
        "elapsed_s": elapsed,
    }


def run_one_seed(seed: int) -> Dict[str, Any]:
    """Sweep overlap grid for a single seed."""
    t0 = time.time()
    per_overlap: Dict[str, Dict[str, Any]] = {}
    for ov in OVERLAP_GRID:
        result = run_one_seed_one_overlap(seed, ov)
        per_overlap["%.2f" % ov] = result
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
        "MAC_SPARSE_FRAC": MAC_SPARSE_FRAC,
        "FAC_K_AFTER_MAC": FAC_K_AFTER_MAC,
        "K_TOP_FOR_VOTE": K_TOP_FOR_VOTE,
        "K_EXEMPLAR_BAYES": K_EXEMPLAR_BAYES,
        "OVERLAP_GRID": list(OVERLAP_GRID),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_overlap": per_overlap,
        "elapsed_s": elapsed,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)
    overlap_keys = ["%.2f" % ov for ov in OVERLAP_GRID]

    # Build per-overlap, per-arm summary across seeds
    per_overlap_summary: Dict[str, Dict[str, Dict[str, float]]] = {}
    for ovk in overlap_keys:
        per_arm_summary: Dict[str, Dict[str, float]] = {}
        for arm in EXPECTED_ARMS:
            vals = [per_seed[s]["per_overlap"][ovk]["per_arm_recall_at_1_masked"][arm]
                    for s in seeds_sorted]
            m = float(np.mean(vals))
            sd = float(np.std(vals)) if n_seeds > 1 else 0.0
            cv = sd / abs(m) if abs(m) > 1e-6 else 0.0
            per_arm_summary[arm] = {"mean": m, "std": sd, "cv": cv, "per_seed": vals}
        per_overlap_summary[ovk] = per_arm_summary

    # ARMS-DIFFER check across all (seed, overlap) cells
    all_distinct = all(
        per_seed[s]["per_overlap"][ovk]["arms_differ_verified"]
        for s in seeds_sorted for ovk in overlap_keys
    )

    # Cardinality
    events_per_arm_per_cell = (N_QUERIES_PER_SCHEMA * K_SCHEMAS * N_MASKED)
    total_events_observed = sum(
        per_seed[s]["per_overlap"][ovk]["n_events_scored_per_arm"]
        for s in seeds_sorted for ovk in overlap_keys
    )
    expected_total = len(SEEDS) * len(OVERLAP_GRID) * events_per_arm_per_cell
    cardinality_ok = total_events_observed >= int(0.85 * expected_total)

    # ANCHOR 3 reproduction check (overlap=0.00)
    ov0_key = "%.2f" % OVERLAP_GRID[0]
    exemplar_at_0 = per_overlap_summary[ov0_key]["ARM_EXEMPLAR_BAYES_K20"]["mean"]
    anchor3_repro_ok = (HP_ANCHOR3_REPRO_LO <= exemplar_at_0 <= HP_ANCHOR3_REPRO_HI)

    # Oracle stability across overlaps
    oracle_means = [per_overlap_summary[ovk]["ARM_ORACLE_TRUE_SCHEMA"]["mean"]
                    for ovk in overlap_keys]
    oracle_min = float(np.min(oracle_means))
    oracle_max = float(np.max(oracle_means))
    oracle_pipeline_sound = (oracle_min >= HP_ORACLE_LO and oracle_max <= HP_ORACLE_HI)
    oracle_broken = (oracle_min < HF_ORACLE_FLOOR)

    # Crossing detection: find smallest overlap where MAC_PLUS_FAC >= EXEMPLAR
    crossing_overlap: float = -1.0
    for ovk in overlap_keys:
        macfac = per_overlap_summary[ovk]["ARM_MAC_PLUS_FAC"]["mean"]
        ex = per_overlap_summary[ovk]["ARM_EXEMPLAR_BAYES_K20"]["mean"]
        if macfac >= ex:
            crossing_overlap = float(ovk)
            break

    # HF rails
    fairness_violated = False
    for ovk in overlap_keys:
        for arm in EXPECTED_ARMS:
            if arm == "ARM_ORACLE_TRUE_SCHEMA":
                continue
            if per_overlap_summary[ovk][arm]["mean"] > HF_FAIRNESS_CEILING:
                fairness_violated = True
                break

    rand_struct_beats_primary = False
    for ovk in overlap_keys:
        rs = per_overlap_summary[ovk]["ARM_RANDOM_STRUCTURAL"]["mean"]
        mf = per_overlap_summary[ovk]["ARM_MAC_PLUS_FAC"]["mean"]
        if rs >= mf and mf > per_overlap_summary[ovk]["ARM_NO_SCHEMA_BASELINE"]["mean"]:
            # Only flag if BOTH match AND both are above baseline (otherwise
            # both at chance is not meaningful)
            rand_struct_beats_primary = True
            break

    # CV check on primary arm (worst-case across overlap)
    primary_max_cv = max(per_overlap_summary[ovk]["ARM_MAC_PLUS_FAC"]["cv"]
                         for ovk in overlap_keys)

    # Exemplar at 90% overlap (for HF-no-crossing rail)
    ovk_90 = "%.2f" % 0.90
    exemplar_at_90 = (per_overlap_summary[ovk_90]["ARM_EXEMPLAR_BAYES_K20"]["mean"]
                       if ovk_90 in per_overlap_summary else None)

    # MAC+FAC ever crosses EXEMPLAR?
    macfac_ever_crosses = (crossing_overlap >= 0.0)
    crossing_meets_hp_threshold = (crossing_overlap >= HP_CROSSING_OVERLAP_MIN
                                    if macfac_ever_crosses else False)

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not all_distinct:
        verdict = "HARD_FAIL"
        verdict_reason = "ARMS_NOT_DISTINCT: SHA-256 collisions in some (seed, overlap)"
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_reason = ("CARDINALITY_BREACH: %d < 0.85 * %d"
                          % (total_events_observed, expected_total))
    elif oracle_broken:
        verdict = "HARD_FAIL"
        verdict_reason = ("ORACLE_BROKEN: oracle_min=%.3f < %.2f (pipeline broken)"
                          % (oracle_min, HF_ORACLE_FLOOR))
    elif fairness_violated:
        verdict = "HARD_FAIL"
        verdict_reason = ("FAIRNESS_VIOLATION: non-oracle arm > %.2f at some overlap "
                          "(regime degenerate)" % HF_FAIRNESS_CEILING)
    elif rand_struct_beats_primary:
        verdict = "HARD_FAIL"
        verdict_reason = ("DEGENERATE_FAC: random_structural >= primary at some overlap "
                          "(structural alignment per se adds no signal beyond MAC stage)")
    elif (exemplar_at_90 is not None
          and exemplar_at_90 > HF_NO_CROSSING_EXEMPLAR_AT_90
          and not macfac_ever_crosses):
        verdict = "HARD_FAIL"
        verdict_reason = ("NO_CROSSING_AT_EXTREME: EXEMPLAR at 90%% overlap = %.3f > %.2f "
                          "AND MAC+FAC never crosses (cosine fully robust; structural alignment "
                          "NEVER helps in measured regime)"
                          % (exemplar_at_90, HF_NO_CROSSING_EXEMPLAR_AT_90))
    elif n_seeds > 1 and primary_max_cv >= HP_CV_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("UNSTABLE: primary max cv across overlaps = %.3f >= %.2f"
                          % (primary_max_cv, HP_CV_MAX))
    elif (anchor3_repro_ok and oracle_pipeline_sound
          and crossing_meets_hp_threshold
          and (n_seeds == 1 or primary_max_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "PHASE_DIAGRAM_CROSSING: anchor3_repro OK (EX@0=%.3f in [%.3f,%.3f]) | "
            "oracle stable [%.3f,%.3f] in [%.2f,%.2f] | crossing at overlap=%.2f (>=%.2f) | "
            "max_cv=%.3f (<%.2f) | structural rerank IS useful at high cross-schema overlap"
            % (exemplar_at_0, HP_ANCHOR3_REPRO_LO, HP_ANCHOR3_REPRO_HI,
               oracle_min, oracle_max, HP_ORACLE_LO, HP_ORACLE_HI,
               crossing_overlap, HP_CROSSING_OVERLAP_MIN, primary_max_cv, HP_CV_MAX))
    elif macfac_ever_crosses and crossing_overlap < HP_CROSSING_OVERLAP_MIN:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "EARLY_CROSSING: MAC+FAC crosses EXEMPLAR at overlap=%.2f < HP_min=%.2f "
            "(crossing exists but at lower-than-expected overlap; refine in v2)"
            % (crossing_overlap, HP_CROSSING_OVERLAP_MIN))
    elif macfac_ever_crosses and crossing_overlap >= HP_CROSSING_OVERLAP_MIN and not anchor3_repro_ok:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "CROSSING_OK_REPRO_OFF: crossing at overlap=%.2f (>=%.2f) but EXEMPLAR@0=%.3f "
            "outside ANCHOR3 repro band [%.3f,%.3f]"
            % (crossing_overlap, HP_CROSSING_OVERLAP_MIN, exemplar_at_0,
               HP_ANCHOR3_REPRO_LO, HP_ANCHOR3_REPRO_HI))
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "BOUNDARY: anchor3_repro=%s oracle_sound=%s crossing_overlap=%.2f "
            "ex@90=%s max_cv=%.3f"
            % (anchor3_repro_ok, oracle_pipeline_sound, crossing_overlap,
               ("%.3f" % exemplar_at_90 if exemplar_at_90 is not None else "NA"),
               primary_max_cv))

    # Compact summary table (per overlap)
    table_lines = []
    for ovk in overlap_keys:
        s = per_overlap_summary[ovk]
        table_lines.append(
            "ov=%s EX=%.3f MACFAC=%.3f ORA=%.3f BASE=%.3f RAND=%.3f"
            % (ovk, s["ARM_EXEMPLAR_BAYES_K20"]["mean"],
               s["ARM_MAC_PLUS_FAC"]["mean"], s["ARM_ORACLE_TRUE_SCHEMA"]["mean"],
               s["ARM_NO_SCHEMA_BASELINE"]["mean"],
               s["ARM_RANDOM_STRUCTURAL"]["mean"]))
    table_str = " || ".join(table_lines)

    verdict_msg = (
        "%s | %s | %s | crossing_overlap=%.2f anchor3_repro=%s oracle=[%.3f,%.3f] "
        "max_cv_primary=%.3f arms_distinct=%s n_seeds=%d"
    ) % (verdict, verdict_reason, table_str, crossing_overlap, anchor3_repro_ok,
         oracle_min, oracle_max, primary_max_cv, all_distinct, n_seeds)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_overlap_per_arm_summary": per_overlap_summary,
        "crossing_overlap": crossing_overlap,
        "macfac_ever_crosses": macfac_ever_crosses,
        "anchor3_reproduction_ok": anchor3_repro_ok,
        "exemplar_at_0_overlap": exemplar_at_0,
        "exemplar_at_90_overlap": exemplar_at_90,
        "oracle_min_across_overlaps": oracle_min,
        "oracle_max_across_overlaps": oracle_max,
        "oracle_pipeline_sound": oracle_pipeline_sound,
        "primary_max_cv_across_overlaps": primary_max_cv,
        "arms_differ_verified": all_distinct,
        "cardinality_ok": cardinality_ok,
        "events_observed_total": total_events_observed,
        "events_expected_total": expected_total,
        "n_seeds_complete": n_seeds,
        "n_overlap_points": len(OVERLAP_GRID),
        "overlap_grid": list(OVERLAP_GRID),
        "expected_n_units": EXPECTED_N_UNITS,
        "comparator_anchor_3_exemplar_bayes_MEASURED": 0.728,
        "comparator_anchor_3_oracle_MEASURED": 0.809,
        "comparator_anchor_2_mac_plus_fac_MEASURED": 0.665,
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
                                  "overlap_grid": list(OVERLAP_GRID),
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V_SLOT=%d M_SLOTS=%d K_SCH=%d NEX=%d seeds=%s "
          "OVERLAPS=%s BETA=%.1f MAC_SPARSE=%.2f FAC_K=%d KTOP=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS,
              N_EXEMPLARS_PER_SCHEMA, SEEDS, OVERLAP_GRID, BETA_TEMP,
              MAC_SPARSE_FRAC, FAC_K_AFTER_MAC, K_TOP_FOR_VOTE), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            # Verify per-overlap structure
            for ovk in ("%.2f" % ov for ov in OVERLAP_GRID):
                assert ovk in r["per_overlap"], "missing overlap %s" % ovk
                cell = r["per_overlap"][ovk]
                for arm in EXPECTED_ARMS:
                    assert arm in cell["per_arm_recall_at_1_masked"], (
                        "missing arm %s at overlap %s" % (arm, ovk))
                assert cell["arms_differ_verified"], (
                    "arms_distinct FAILED at overlap %s" % ovk)
                ora = cell["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
                assert ora >= 0.40, "oracle recall %.3f too low at overlap %s" % (ora, ovk)
            # Verify overlap mechanism: observed_overlap at 0.0 should be small,
            # at 0.90 should be much larger
            ov0_obs = r["per_overlap"]["0.00"]["observed_overlap"]
            ov90_obs = r["per_overlap"]["0.90"]["observed_overlap"]
            assert ov90_obs > ov0_obs, (
                "overlap mechanism broken: obs@0=%.3f obs@90=%.3f (expect monotone)"
                % (ov0_obs, ov90_obs))
            print("[selftest] OK overlaps verified obs@0=%.3f obs@90=%.3f" % (
                ov0_obs, ov90_obs), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: %d overlaps OK obs@0=%.3f obs@90=%.3f"
                                   % (len(OVERLAP_GRID), ov0_obs, ov90_obs),
                                   extra={"selftest_per_overlap": {
                                       ovk: r["per_overlap"][ovk]["per_arm_recall_at_1_masked"]
                                       for ovk in r["per_overlap"]
                                   }})
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
        # Build per-seed summary line
        per_ov_pairs = []
        for ovk in ("%.2f" % ov for ov in OVERLAP_GRID):
            cell = result["per_overlap"][ovk]
            per_ov_pairs.append("%s:EX=%.3f/MF=%.3f" % (
                ovk,
                cell["per_arm_recall_at_1_masked"]["ARM_EXEMPLAR_BAYES_K20"],
                cell["per_arm_recall_at_1_masked"]["ARM_MAC_PLUS_FAC"]))
        print("[seed=%d] complete in %.1fs | %s" % (
            seed, time.time() - t0, " | ".join(per_ov_pairs)), flush=True)

    final = aggregate_and_verdict(per_seed_results)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_cross_schema_overlap_phase_diagram"
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
