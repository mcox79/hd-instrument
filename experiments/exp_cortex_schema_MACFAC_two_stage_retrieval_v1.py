"""cortex_schema_MACFAC_two_stage_retrieval_v1 -- Gentner-Forbus structural alignment.

Prereg: preregs/2026-06-27_cortex_schema_MACFAC_two_stage_retrieval_v1.md
Drill:  notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md TOP-2
Handoff: notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md ANCHOR 2

COMPARATORS (absolute paths; cited per number-tagging discipline):
  ANCHOR 3 HARD_PASS: d:/AI/hd-instrument/data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json
    EXEMPLAR_BAYES_K20 = MEASURED@0.728 (cv=0.015) -- substrate cosine baseline
    ORACLE              = MEASURED@0.809
  ANCHOR 1 MIDDLE_BAND: d:/AI/hd-instrument/data/exp_cortex_schema_instantiation_context_prior_v1_smoke/metrics.json
    CONTEXT_BOUND_PRIOR = MEASURED@0.731 (lift +0.003 over EXEMPLAR_BAYES -- substrate cosine
    already encodes the schema; top-down prior adds NOTHING orthogonal)

CONCEPT (Gentner-Forbus 1990s MAC/FAC; later mapped to VSA/HRR by Eliasmith):
  Two-stage retrieval for analogical reasoning:
    MAC (Many Are Called):  cheap surface-similarity prefilter; sparse-dotprod
                            over content vectors; picks top-K candidates
    FAC (Few Are Chosen):   expensive structural alignment; per-slot type-matched
                            scoring; re-ranks candidates by structural fit
  Hypothesis: This is an ORTHOGONAL mechanism class to ANCHOR 1's TOP-DOWN PRIOR.
  Where ANCHOR 1 conditions on schema prior P(schema|context), ANCHOR 2 conditions
  on per-slot structural alignment (matching MASKED slot identity to candidate
  slots that fill the SAME slot type).

  Substrate cosine retrieval (ANCHOR 3) treats the query as an unstructured bag --
  observed slots get pooled. MAC+FAC respects per-slot STRUCTURE: a candidate
  exemplar matching well on HABITAT but poorly on DIET should score by alignment
  per slot, not by global cosine.

  Expected: structural alignment provides orthogonal lift if substrate cosine is
  losing per-slot structure in the sum-encoding pool. If substrate cosine ALREADY
  preserves per-slot structure (the ANCHOR 1 result HYPOTHESIZES@this), MAC+FAC
  will not improve over cosine -- the structure is recovered post-hoc by cosine.

DATA (identical to ANCHOR 1+3 for direct comparability per handoff spec):
  8 schemas x 6 typed slots x 20 exemplars per schema = 160 exemplars
  V_SLOT=8 fillers per slot; M_SLOTS=6 slots; FILLER_NOISE=0.20
  Test: novel partial input (3 of 6 slots observed); predict remaining 3.

ARMS (7):
  ARM_NO_SCHEMA_BASELINE        chance: per-slot mode over ALL exemplars (popularity)
  ARM_EXEMPLAR_BAYES_K20        replicate ANCHOR 3 primary (cosine top-K20 softmax vote)
                                COMPARATOR: MEASURED@0.728 on ANCHOR 3
  ARM_MAC_ONLY                  MAC-only: sparse-dotprod top-K20, NO structural rerank;
                                tests whether MAC alone matches exemplar-Bayes
  ARM_MAC_PLUS_FAC              MECHANISM under test: MAC top-K20 -> FAC per-slot
                                structural alignment scoring -> re-rank top-K
                                Predict masked slots from FAC-reranked top exemplars.
  ARM_FAC_ONLY_DENSE            FAC over ALL exemplars (no MAC prefilter); tests
                                whether MAC stage is needed (cost-benefit ablation)
  ARM_ORACLE_TRUE_SCHEMA        know-true-schema upper bound; COMPARATOR MEASURED@0.809
  ARM_RANDOM_STRUCTURAL         FAC with RANDOM alignment scores; control distinguishes
                                "structural alignment per se" from "any rerank"

MAC mechanism (sparse-dotprod surface match):
  For each query: project query and each exemplar to SPARSE sign-vector (top-T% by
  magnitude, +/-1 sign elsewhere zero); dot-product matches surface features.
  Approximates Gentner's "structure-blind surface match". Sparse-dotprod is cheaper
  and computationally distinct from cosine.

FAC mechanism (per-slot structural alignment):
  For each candidate exemplar, score = sum over OBSERVED slots s of
    alignment(query.slot[s], candidate.slot[s])
  where alignment is the cosine of filler-atom vectors (NOT pooled).
  This respects per-slot STRUCTURE -- it knows q.HABITAT goes with c.HABITAT, not
  the sum-pool of all 6 slots.

ENCODING (identical to ANCHOR 3):
  per-slot V_SLOT random L2-normalized N-dim filler atoms
  exemplar_vector = L2(sum over 6 slots of slot_filler_vector) + FILLER_NOISE
  query_vector_observed = L2(sum over OBSERVED slots only)

REGIME:
  N_DIM=2048 (smoke), 8192 (full)  -- matches ANCHOR 3 smoke
  K_SCHEMAS=8 V_SLOT=8 M_SLOTS=6 NEX=20 FILLER_NOISE=0.20 MASK_FRACTION=0.50
  N_QUERIES_PER_SCHEMA_SMOKE=30 -> 240 events; FULL=100 -> 800 events
  BETA_TEMP=8.0 (softmax for K-nearest)
  MAC_SPARSE_FRAC=0.10 (top-10% of N_DIM by magnitude form sparse code)
  FAC_K_AFTER_MAC=20 (rerank top-20 from MAC; K_TOP_FAC=5 used for vote)
  K_TOP_FOR_VOTE=5 (after FAC re-rank, top-5 vote)

PRE-REG BANDS:
  HARD_PASS (orthogonal lift):
    ARM_MAC_PLUS_FAC mean recall@1 >= HYPOTHESIZED@0.80 (above EXEMPLAR_BAYES 0.728 + 0.07)
    AND ARM_MAC_PLUS_FAC - ARM_MAC_ONLY >= 0.05 (FAC step adds value over MAC alone)
    AND ARM_MAC_PLUS_FAC > ARM_EXEMPLAR_BAYES_K20 + 0.05 (orthogonal to cosine)
    AND cv across seeds < 0.10
    AND arms_distinct=True
    AND cardinality_ok=True

  MIDDLE_BAND:
    ARM_MAC_PLUS_FAC in [0.74, 0.80) -- some lift but below HP floor

  HARD_FAIL (substrate cosine already encodes structure):
    ARM_MAC_PLUS_FAC <= ARM_EXEMPLAR_BAYES_K20 + 0.01
      -> CONFIRMS strong "substrate cosine already does it" finding
    OR ARM_FAC_ONLY_DENSE - ARM_MAC_PLUS_FAC <= 0 (MAC stage useless: dense FAC matches/beats)
      [secondary signal; doesn't block HP if MAC+FAC still lifts over cosine]
    OR ARM_ORACLE_TRUE_SCHEMA <= 0.70 (oracle broken; harness broken)
    OR ANY non-oracle arm > 0.95 (FAIRNESS_VIOLATION; regime too easy)
    OR cv >= 0.15
    OR ARM_RANDOM_STRUCTURAL >= ARM_MAC_PLUS_FAC (random alignment matches structural;
      mechanism is degenerate)
    OR cardinality breach

CRLB PRE-VALIDATION (per [[feedback-experiment-bias-master-checklist]] N):
  N=2048, V_SLOT=8 categorical, N_TRIALS=240*3=720 events per arm at smoke.
  var = p(1-p)/n = 0.80*0.20/720 = 2.22e-4; sd = 0.0149
  HP discriminator = +0.072 lift over EXEMPLAR_BAYES; ratio = 0.072 / 0.0149 = 4.8x
  CRLB-REACHABLE. Smoke n_seeds=3 gives between-seed cv estimate.

DISCRIMINATOR_MUST_SURVIVE_SCALE check (per [[feedback-discriminator-must-survive-scale]]):
  Smoke at N=2048 (same N as ANCHOR 1+3 smoke; full at 8192). Strategy A: smoke
  AT-FULL-N for HP threshold. If smoke MAC+FAC == EXEMPLAR_BAYES at N=2048, scaling
  to N=8192 is UNLIKELY to introduce orthogonal lift (cosine kernel only gets MORE
  precise at higher N; if it's already capturing structure at N=2048, FAC adds
  nothing at N=8192). HARD_FAIL at smoke -> no full dispatch (saves CPU).

CARDINALITY_OK:
  EXPECTED_N_UNITS_SMOKE = 7 arms * 3 seeds * 240 queries * 3 masked = 15120 events
  EXPECTED_N_UNITS_FULL  = 7 arms * 5 seeds * 800 queries * 3 masked = 84000 events
  HARD_FAIL_CARDINALITY_BREACH if observed < 0.85 * expected.

ARMS-MUST-DIFFER (META_RULE_AF):
  SHA-256 of per-arm prediction matrices. unique_hashes == len(EXPECTED_ARMS).
  Note: ARM_MAC_ONLY vs ARM_EXEMPLAR_BAYES_K20 use DIFFERENT similarity functions
  (sparse-dotprod vs cosine) -> predictions WILL differ in general.
  Note: ARM_FAC_ONLY_DENSE vs ARM_MAC_PLUS_FAC use DIFFERENT candidate pools
  (all 160 vs MAC-prefiltered 20) -> predictions WILL differ in general.
  Note: ARM_RANDOM_STRUCTURAL uses RANDOM alignment scores -> always differs.

ASCII-only; no emojis; no em-dashes.
Author: exp_dev 2026-06-27 (drill TOP-2 / ANCHOR 2 schema-driven inference).
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

ANCHOR_NAME = "cortex_schema_MACFAC_two_stage_retrieval_v1"

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
HP_MACFAC_FLOOR = 0.80           # HP threshold for MAC+FAC absolute
HP_LIFT_OVER_EXEMPLAR = 0.05     # HP requires >+0.05 over EXEMPLAR_BAYES_K20
HP_LIFT_OVER_MAC_ONLY = 0.05     # HP requires >+0.05 over MAC_ONLY (FAC step value)
HP_CV_MAX = 0.10
HF_FAIRNESS_CEILING = 0.95
HF_ORACLE_FLOOR = 0.70
HF_CV_MAX = 0.15
HF_DEGENERATE_LIFT_OVER_EXEMPLAR = 0.01  # if MAC+FAC <= EXEMPLAR + 0.01 => HF
MIDDLE_MACFAC_LO = 0.74
MIDDLE_MACFAC_HI = 0.80

EXPECTED_ARMS = (
    "ARM_NO_SCHEMA_BASELINE",
    "ARM_EXEMPLAR_BAYES_K20",
    "ARM_MAC_ONLY",
    "ARM_MAC_PLUS_FAC",
    "ARM_FAC_ONLY_DENSE",
    "ARM_ORACLE_TRUE_SCHEMA",
    "ARM_RANDOM_STRUCTURAL",
)
PRIMARY_ARM = "ARM_MAC_PLUS_FAC"

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
    SEEDS = [7, 17, 23]
    BETA_TEMP = 8.0
    MAC_SPARSE_FRAC = 0.10
    FAC_K_AFTER_MAC = 20
    K_TOP_FOR_VOTE = 5
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
    BETA_TEMP = 8.0
    MAC_SPARSE_FRAC = 0.10
    FAC_K_AFTER_MAC = 20
    K_TOP_FOR_VOTE = 5

N_MASKED = int(round(MASK_FRACTION * M_SLOTS))  # 3 of 6
K_EXEMPLAR_BAYES = 20  # match ANCHOR 3 primary

EXPECTED_N_UNITS = (len(EXPECTED_ARMS) * len(SEEDS)
                    * (N_QUERIES_PER_SCHEMA * K_SCHEMAS) * N_MASKED)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,VSLOT=%d,MSLOTS=%d,KSCH=%d,NEX=%d,FN=%.2f,MF=%.2f,"
    "NQPS=%d,SEEDS=%s,BETA=%.1f,N_MASKED=%d,MAC_SPARSE=%.2f,FAC_K=%d,KTOP=%d,"
    "K_EXEMPLAR=%d,HP_floor=%.2f,HP_lift_ex>=%.2f,HP_lift_mac>=%.2f,HP_cv<%.2f,"
    "RUN_MODE=%s,hardening=L1early+L2perarm+L4importsentinel+CARDINALITY_OK"
    "+ARMS_DIFFER_SHA256+ATOMIC_REPLACE+SMOKE_FIRES_DISCRIMINATOR"
) % (
    ANCHOR_NAME, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS, N_EXEMPLARS_PER_SCHEMA,
    FILLER_NOISE, MASK_FRACTION, N_QUERIES_PER_SCHEMA, SEEDS,
    BETA_TEMP, N_MASKED, MAC_SPARSE_FRAC, FAC_K_AFTER_MAC, K_TOP_FOR_VOTE,
    K_EXEMPLAR_BAYES,
    HP_MACFAC_FLOOR, HP_LIFT_OVER_EXEMPLAR, HP_LIFT_OVER_MAC_ONLY, HP_CV_MAX,
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
            "_hardening_marker": "v1_MACFAC_two_stage_orthogonal_mechanism",
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
            "_hardening_marker": "v1_MACFAC_import_crash",
        }
        _atomic_write_metrics(out_dir, sentinel)
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- data generation (identical to ANCHOR 3) --------------------------

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
    out = rng.integers(0, V_SLOT, size=(K_SCHEMAS, M_SLOTS), dtype=np.int64)
    return out


def make_exemplar_bank(seed: int, schema_defaults: np.ndarray,
                       filler_atoms: np.ndarray
                       ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same exemplar generation as ANCHOR 3 (direct comparability)."""
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
    """Same query generation as ANCHOR 3."""
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

def predict_no_schema_baseline(slot_values: np.ndarray, q_observed_idx: np.ndarray,
                                q_true_slot_values: np.ndarray) -> np.ndarray:
    """Per-slot mode over ALL exemplars (popularity prior). Identical to ANCHOR 3 baseline."""
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
    """ANCHOR 3 primary: top-K cosine, softmax-weighted slot vote."""
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
    """MAC sparse code: top-sparse_frac*N entries by |value| -> sign(value); rest -> 0.

    Distinct from cosine: keeps only the largest-magnitude dimensions. Approximates
    Gentner's "surface match" -- gross structural signature, not full geometry.
    Returns shape same as vectors (sparse representation in dense storage).
    """
    n_keep = max(1, int(round(sparse_frac * vectors.shape[1])))
    abs_v = np.abs(vectors)
    # Per row: indices of top-n_keep by magnitude
    idx_sorted = np.argpartition(-abs_v, n_keep - 1, axis=1)[:, :n_keep]
    out = np.zeros_like(vectors)
    rows = np.arange(vectors.shape[0])[:, None]
    out[rows, idx_sorted] = np.sign(vectors[rows, idx_sorted])
    return out


def predict_mac_only(q_observed_vec: np.ndarray, exemplar_vectors: np.ndarray,
                     exemplar_slot_values: np.ndarray,
                     K: int, beta: float, sparse_frac: float) -> np.ndarray:
    """MAC-only: sparse-dotprod top-K, softmax vote (NO structural rerank).

    Compare to ARM_EXEMPLAR_BAYES_K20: same vote mechanism, DIFFERENT similarity
    function (sparse-dotprod vs cosine). Tests whether sparse surface match alone
    matches dense cosine.
    """
    N_Q = q_observed_vec.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    q_sparse = _build_sparse_codes(q_observed_vec, sparse_frac)
    ex_sparse = _build_sparse_codes(exemplar_vectors, sparse_frac)
    # Sparse-dotprod (not cosine -- sparse codes aren't unit norm)
    dot_all = q_sparse @ ex_sparse.T
    # Normalize by max per row for stable softmax temperature
    for n in range(N_Q):
        scores = dot_all[n]
        top_idx = np.argpartition(-scores, min(K, len(scores) - 1))[:K]
        top_scores = scores[top_idx]
        max_score = max(np.max(np.abs(top_scores)), 1e-12)
        z = beta * (top_scores / max_score)  # rescale so beta stays meaningful
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def _fac_align_scores(q_slot_values: np.ndarray, q_observed_idx: np.ndarray,
                       candidate_indices: np.ndarray,
                       exemplar_slot_values: np.ndarray,
                       filler_atoms: np.ndarray) -> np.ndarray:
    """Per-slot STRUCTURAL alignment between query observed slots and candidate slots.

    For each (query, candidate) pair:
      score = sum over OBSERVED slots s of cos(q.slot_filler[s], cand.slot_filler[s])
    Filler atoms are L2-normalized, so cos = dot.
    Per-slot type-matched: q.slot_HABITAT compared ONLY to cand.slot_HABITAT.

    Returns: (N_Q, len(candidate_indices)) score matrix per query.
    Only fills entries for candidates passed in; caller dispatches per-query.
    """
    # Vectorized: filler_atoms[s, idx] is (N_DIM,)
    # For each query n and candidate c in q's candidate_indices[n]:
    #   score = sum_{s in observed} dot(filler_atoms[s, q_slot_values[n,s]],
    #                                    filler_atoms[s, exemplar_slot_values[c,s]])
    # Since filler atoms are pre-normalized random, dot of distinct atoms ~ 0;
    # dot of same atom = 1; so score ~ # of slot-matches on observed slots.
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
    """MAC+FAC mechanism (the test arm).

    Step 1 (MAC): sparse-dotprod top-mac_K candidates per query.
    Step 2 (FAC): per-slot structural alignment scoring on the mac_K candidates.
    Step 3: top-fac_K_top by FAC score, softmax-weighted slot vote.

    THIS is the orthogonal-mechanism arm. If substrate cosine already encodes
    per-slot structure (ANCHOR 1 finding), MAC+FAC will not lift over ANCHOR 3.
    """
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)

    # Step 1: MAC over all exemplars (sparse-dotprod)
    q_sparse = _build_sparse_codes(q_observed_vec, sparse_frac)
    ex_sparse = _build_sparse_codes(exemplar_vectors, sparse_frac)
    dot_all = q_sparse @ ex_sparse.T  # (N_Q, N_EX)

    K_mac = min(mac_K, N_EX)
    mac_candidates = np.zeros((N_Q, K_mac), dtype=np.int64)
    for n in range(N_Q):
        scores = dot_all[n]
        mac_candidates[n] = np.argpartition(-scores, K_mac - 1)[:K_mac]

    # Step 2: FAC structural alignment on the K_mac candidates
    fac_scores = _fac_align_scores(q_slot_values, q_observed_idx, mac_candidates,
                                    exemplar_slot_values, filler_atoms)

    # Step 3: top-fac_K_top by FAC, softmax-weighted vote
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


def predict_fac_only_dense(q_slot_values: np.ndarray, q_observed_idx: np.ndarray,
                            exemplar_slot_values: np.ndarray,
                            filler_atoms: np.ndarray,
                            fac_K_top: int, beta: float) -> np.ndarray:
    """FAC over ALL exemplars (no MAC prefilter); rerank top-K_top by FAC, vote.

    Tests whether MAC stage is needed. If FAC_ONLY_DENSE matches MAC_PLUS_FAC,
    MAC is wasted computation. If FAC_ONLY_DENSE >> MAC_PLUS_FAC, MAC is
    *removing* relevant candidates.
    """
    N_Q = q_slot_values.shape[0]
    N_EX = exemplar_slot_values.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    # FAC over ALL exemplars: candidate_indices is N_Q copies of arange(N_EX)
    all_cand = np.tile(np.arange(N_EX, dtype=np.int64), (N_Q, 1))
    fac_scores = _fac_align_scores(q_slot_values, q_observed_idx, all_cand,
                                    exemplar_slot_values, filler_atoms)
    K_top = min(fac_K_top, N_EX)
    for n in range(N_Q):
        s_n = fac_scores[n]
        top_idx = np.argpartition(-s_n, K_top - 1)[:K_top]
        top_scores = s_n[top_idx]
        z = beta * top_scores
        z = z - np.max(z)
        w = np.exp(z)
        w = w / max(np.sum(w), 1e-12)
        for s in range(M_SLOTS):
            counts = np.zeros(V_SLOT, dtype=np.float64)
            for ii, ex_idx in enumerate(top_idx):
                counts[exemplar_slot_values[ex_idx, s]] += w[ii]
            preds[n, s] = int(np.argmax(counts))
    return preds


def predict_random_structural(q_observed_vec: np.ndarray,
                                q_observed_idx: np.ndarray,
                                exemplar_vectors: np.ndarray,
                                exemplar_slot_values: np.ndarray,
                                mac_K: int, sparse_frac: float, fac_K_top: int,
                                beta: float, rng: np.random.Generator) -> np.ndarray:
    """MAC + RANDOM 'structural' scores (control).

    Same pipeline as MAC+FAC, but FAC scores are random Uniform[0,1] not real
    per-slot alignment. Distinguishes "structural alignment per se" from
    "any rerank stage" -- if RANDOM_STRUCTURAL >= MAC_PLUS_FAC, the FAC mechanism
    is degenerate and the lift (if any) came from MAC stage alone.
    """
    N_Q = q_observed_vec.shape[0]
    N_EX = exemplar_vectors.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)

    # Step 1: MAC (identical)
    q_sparse = _build_sparse_codes(q_observed_vec, sparse_frac)
    ex_sparse = _build_sparse_codes(exemplar_vectors, sparse_frac)
    dot_all = q_sparse @ ex_sparse.T

    K_mac = min(mac_K, N_EX)
    mac_candidates = np.zeros((N_Q, K_mac), dtype=np.int64)
    for n in range(N_Q):
        scores = dot_all[n]
        mac_candidates[n] = np.argpartition(-scores, K_mac - 1)[:K_mac]

    # Step 2: RANDOM "structural" scores per (query, candidate)
    fac_scores = rng.random(size=(N_Q, K_mac))

    # Step 3: top-fac_K_top by RANDOM rerank
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
    """Identical to ANCHOR 3 oracle."""
    N_Q = q_schema.shape[0]
    preds = np.zeros((N_Q, M_SLOTS), dtype=np.int64)
    for n in range(N_Q):
        for s in range(M_SLOTS):
            preds[n, s] = schema_defaults[q_schema[n], s]
    return preds


# -------------------------- scoring --------------------------

def recall_at_1_on_masked(preds: np.ndarray, true_slots: np.ndarray,
                           q_observed_idx: np.ndarray) -> float:
    """recall@1 over MASKED slots only (identical to ANCHOR 3)."""
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

    arms_preds["ARM_NO_SCHEMA_BASELINE"] = predict_no_schema_baseline(
        ex_slot_values, q_obs_idx, q_true_slots)

    arms_preds["ARM_EXEMPLAR_BAYES_K20"] = predict_exemplar_bayes_k20(
        q_obs_vec, ex_vectors, ex_slot_values, K=K_EXEMPLAR_BAYES, beta=BETA_TEMP)

    arms_preds["ARM_MAC_ONLY"] = predict_mac_only(
        q_obs_vec, ex_vectors, ex_slot_values,
        K=K_EXEMPLAR_BAYES, beta=BETA_TEMP, sparse_frac=MAC_SPARSE_FRAC)

    arms_preds["ARM_MAC_PLUS_FAC"] = predict_mac_plus_fac(
        q_obs_vec, q_true_slots, q_obs_idx, ex_vectors, ex_slot_values,
        filler_atoms, mac_K=FAC_K_AFTER_MAC, sparse_frac=MAC_SPARSE_FRAC,
        fac_K_top=K_TOP_FOR_VOTE, beta=BETA_TEMP)

    arms_preds["ARM_FAC_ONLY_DENSE"] = predict_fac_only_dense(
        q_true_slots, q_obs_idx, ex_slot_values, filler_atoms,
        fac_K_top=K_TOP_FOR_VOTE, beta=BETA_TEMP)

    arms_preds["ARM_ORACLE_TRUE_SCHEMA"] = predict_oracle_true_schema(
        q_schema, schema_defaults)

    rng_rand_struct = np.random.default_rng(seed + 6071)
    arms_preds["ARM_RANDOM_STRUCTURAL"] = predict_random_structural(
        q_obs_vec, q_obs_idx, ex_vectors, ex_slot_values,
        mac_K=FAC_K_AFTER_MAC, sparse_frac=MAC_SPARSE_FRAC,
        fac_K_top=K_TOP_FOR_VOTE, beta=BETA_TEMP, rng=rng_rand_struct)

    for arm in EXPECTED_ARMS:
        r = recall_at_1_on_masked(arms_preds[arm], q_true_slots, q_obs_idx)
        per_arm_recall[arm] = float(r)
        print("  [seed=%d %s] recall@1=%.3f" % (seed, arm, r), flush=True)

    # ARMS-MUST-DIFFER SHA-256
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
        "MAC_SPARSE_FRAC": MAC_SPARSE_FRAC,
        "FAC_K_AFTER_MAC": FAC_K_AFTER_MAC,
        "K_TOP_FOR_VOTE": K_TOP_FOR_VOTE,
        "K_EXEMPLAR_BAYES": K_EXEMPLAR_BAYES,
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
    exemplar = per_arm_recall_summary["ARM_EXEMPLAR_BAYES_K20"]["mean"]
    mac_only = per_arm_recall_summary["ARM_MAC_ONLY"]["mean"]
    primary = per_arm_recall_summary[PRIMARY_ARM]["mean"]  # MAC_PLUS_FAC
    primary_cv = per_arm_recall_summary[PRIMARY_ARM]["cv"]
    fac_dense = per_arm_recall_summary["ARM_FAC_ONLY_DENSE"]["mean"]
    oracle = per_arm_recall_summary["ARM_ORACLE_TRUE_SCHEMA"]["mean"]
    rand_struct = per_arm_recall_summary["ARM_RANDOM_STRUCTURAL"]["mean"]

    max_non_oracle = max(per_arm_recall_summary[arm]["mean"] for arm in EXPECTED_ARMS
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
        verdict_reason = ("ORACLE_BROKEN: oracle_recall=%.3f <= %.2f (cell harness broken)"
                          % (oracle, HF_ORACLE_FLOOR))
    elif max_non_oracle > HF_FAIRNESS_CEILING:
        verdict = "HARD_FAIL"
        verdict_reason = ("FAIRNESS_VIOLATION: non-oracle arm max=%.3f > %.2f "
                          "(regime too easy)" % (max_non_oracle, HF_FAIRNESS_CEILING))
    elif rand_struct >= primary:
        verdict = "HARD_FAIL"
        verdict_reason = ("DEGENERATE_FAC: random_structural=%.3f >= primary=%.3f "
                          "(structural alignment per se adds no signal)"
                          % (rand_struct, primary))
    elif n_seeds > 1 and primary_cv >= HF_CV_MAX:
        verdict = "HARD_FAIL"
        verdict_reason = ("UNSTABLE: primary cv=%.3f >= %.2f" % (primary_cv, HF_CV_MAX))
    elif primary <= exemplar + HF_DEGENERATE_LIFT_OVER_EXEMPLAR:
        verdict = "HARD_FAIL"
        verdict_reason = ("NO_ORTHOGONAL_LIFT: primary=%.3f <= EXEMPLAR_BAYES=%.3f + %.2f "
                          "(substrate cosine ALREADY encodes schema structure; "
                          "MAC+FAC adds no orthogonal value)"
                          % (primary, exemplar, HF_DEGENERATE_LIFT_OVER_EXEMPLAR))
    elif (primary >= HP_MACFAC_FLOOR
          and (primary - exemplar) >= HP_LIFT_OVER_EXEMPLAR
          and (primary - mac_only) >= HP_LIFT_OVER_MAC_ONLY
          and (n_seeds == 1 or primary_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "MACFAC_ORTHOGONAL_LIFT: primary=%.3f (>=%.2f) | "
            "lift_over_exemplar=+%.3f (>=%.2f) | lift_over_mac_only=+%.3f (>=%.2f) | "
            "cv=%.3f (<%.2f) | structural-alignment IS orthogonal to substrate cosine"
            % (primary, HP_MACFAC_FLOOR,
               primary - exemplar, HP_LIFT_OVER_EXEMPLAR,
               primary - mac_only, HP_LIFT_OVER_MAC_ONLY,
               primary_cv, HP_CV_MAX))
    elif MIDDLE_MACFAC_LO <= primary < MIDDLE_MACFAC_HI:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("PARTIAL_ORTHOGONAL_LIFT: primary=%.3f in [%.2f, %.2f); "
                          "some structural signal but below HP floor"
                          % (primary, MIDDLE_MACFAC_LO, MIDDLE_MACFAC_HI))
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = ("BOUNDARY: primary=%.3f exemplar=%.3f mac_only=%.3f "
                          "fac_dense=%.3f" % (primary, exemplar, mac_only, fac_dense))

    verdict_msg = (
        "%s | %s | primary[%s]=%.3f exemplar=%.3f mac_only=%.3f fac_dense=%.3f "
        "rand_struct=%.3f oracle=%.3f base=%.3f cv_primary=%.3f arms_distinct=%s n_seeds=%d"
    ) % (verdict, verdict_reason, PRIMARY_ARM, primary, exemplar, mac_only,
         fac_dense, rand_struct, oracle, base, primary_cv, all_distinct, n_seeds)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "per_arm_recall_summary": per_arm_recall_summary,
        "primary_arm": PRIMARY_ARM,
        "primary_recall": primary,
        "exemplar_bayes_recall": exemplar,
        "mac_only_recall": mac_only,
        "fac_only_dense_recall": fac_dense,
        "random_structural_recall": rand_struct,
        "oracle_recall": oracle,
        "baseline_recall": base,
        "lift_over_exemplar": primary - exemplar,
        "lift_over_mac_only": primary - mac_only,
        "lift_over_fac_dense": primary - fac_dense,
        "primary_cv": primary_cv,
        "arms_differ_verified": all_distinct,
        "cardinality_ok": cardinality_ok,
        "events_per_arm_total": events_total,
        "expected_events_per_arm": expected_events_per_arm,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
        "comparator_anchor_3_exemplar_bayes_MEASURED": 0.728,
        "comparator_anchor_3_oracle_MEASURED": 0.809,
        "comparator_anchor_1_context_prior_MEASURED": 0.731,
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
          "BETA=%.1f MASK_FRAC=%.2f MAC_SPARSE=%.2f FAC_K=%d KTOP=%d" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, V_SLOT, M_SLOTS, K_SCHEMAS,
              N_EXEMPLARS_PER_SCHEMA, SEEDS, BETA_TEMP, MASK_FRACTION,
              MAC_SPARSE_FRAC, FAC_K_AFTER_MAC, K_TOP_FOR_VOTE), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm_recall_at_1_masked"], "missing arm %s" % arm
            ora = r["per_arm_recall_at_1_masked"]["ARM_ORACLE_TRUE_SCHEMA"]
            base = r["per_arm_recall_at_1_masked"]["ARM_NO_SCHEMA_BASELINE"]
            primary = r["per_arm_recall_at_1_masked"][PRIMARY_ARM]
            exemplar = r["per_arm_recall_at_1_masked"]["ARM_EXEMPLAR_BAYES_K20"]
            assert r["arms_differ_verified"], "arms_distinct check FAILED"
            assert ora >= 0.50, "oracle recall %.3f too low" % ora
            print("[selftest] OK primary=%.3f exemplar=%.3f base=%.3f oracle=%.3f "
                  "arms_distinct=%s n_unique=%d/%d" % (
                      primary, exemplar, base, ora, r["arms_differ_verified"],
                      r["n_unique_arm_hashes"], len(EXPECTED_ARMS)), flush=True)
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   ("SELFTEST_OK: arms differ, oracle=%.3f base=%.3f "
                                    "exemplar=%.3f primary=%.3f"
                                    % (ora, base, exemplar, primary)),
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
    final["_hardening_marker"] = "v1_MACFAC_two_stage_orthogonal_mechanism"
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
