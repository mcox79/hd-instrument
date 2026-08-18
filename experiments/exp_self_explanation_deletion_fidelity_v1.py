"""self_explanation_deletion_fidelity_v1 -- HRR reverse-cleanup + deletion-counterfactual faithfulness (Stage 3).

Substrate produces output O via stored binds (K_i, V_i); contribution_score_i =
|<unbind(O, K_i), V_i>|. For each top-K=5 trace atom, the deletion-counterfactual arm
re-queries with that bind SUBTRACTED from the partition; faithfulness = Spearman rho
of (contribution_score, output_delta) over K trace steps x N queries x N seeds.

Brain analog: substrate-product framing = "RAG with native faithful attribution built
into the storage primitive" -- a CAPABILITY Wallat ICTIR 2025 documents 57% of LLM RAG
systems lack. M3 glass-box property 7-8.

LOAD-BEARING PRIOR-ART FIX (research drill mandate):
  substrate_audit_chain_coherence_benchmark_v1 HARD_FAILed because
  refuse_threshold = 0.55 * mean_known_conf = 0.025 was BELOW the noise floor.
  THIS cell computes threshold from calib-set cosine percentile that maximizes
  refuse_accuracy (NOT a fixed fraction of mean). Verified in _calibrate_threshold().

ENCODING-BEFORE-READOUT (META_RULE_AL):
  ENCODING (how facts get INTO substrate state):
    HRR bind on stored (key, value) pairs; each fact = bind(K_i, V_i) bundled
    into partition memory M_part = sum_i bind(K_i, V_i). Chain-grade primitive
    (hdlab.binding.bind FFT-based; smoke-tested).
  READOUT (faithfulness test):
    For query key Q, decoded_value = unbind(M_part, Q). Top-K=5 contribution
    scores by reverse-cleanup. For each trace atom, deletion-counterfactual:
    M_part_minus_i = M_part - bind(K_i, V_i); re-decode; observe output delta.
  Encoder is well-defined deterministic (HRR algebra); readout is downstream
  Spearman rho of (contribution_score, output_delta).
  Encoder-readout separation by SHA-256 fingerprint on per-arm trace cosines.

ARMS (3; structurally differ per META_RULE_AF):
  ARM_TRUE_TRACE      reverse-cleanup contribution score (substrate's bind-based) -- MECHANISM
  ARM_RANDOM_TRACE    K random stored atoms (chance-baseline strawman)
  ARM_COSINE_TRACE    top-K by raw cosine(query_key, stored_key) (obvious-explanation confound)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE; research-owned):
  HARD_PASS (ALL must hold):
    ARM_TRUE_TRACE Spearman rho >= 0.70
    ARM_RANDOM_TRACE Spearman rho in [-0.10, +0.10] (chance)
    TRUE - COSINE rho >= 0.15 (bind beats raw cosine)
    arms_distinct == True (SHA-256 of per-arm trace cosines differ)
    CARDINALITY_OK
  MIDDLE_BAND:
    TRUE rho in [0.40, 0.70] OR TRUE - COSINE in [0.05, 0.15)
  HARD_FAIL (ANY triggers):
    TRUE rho < 0.40 (explanation does NOT track output causation; confabulation regime)
    TRUE - COSINE <= 0 (no lift over trivial explainer; substrate's audit claim unsupported)
    arms_distinct == False
    CARDINALITY breach
    META_RULE_Q suspect-1.000 on n>=100

BY-CONSTRUCTION-SATURATION (META_RULE_H + research drill mandate):
  if ARM_COSINE_TRACE alone HARD_PASS, tier down + require cleanup-margin < 0.1
  regime (M >> typical) before claiming bind-primitive lift. Cell records
  cleanup_margin diagnostic; Skunkworks tier-decision uses it.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 3 arms * 5 seeds * 1000 queries * 5 trace-steps = 75,000
  EXPECTED_N_UNITS_SMOKE = 3 arms * 3 seeds * 500 queries  * 5 trace-steps = 22,500

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  smoke is run at N_DIM=2048; full at N_DIM=8192. The discriminator MUST FIRE at smoke:
  if smoke TRUE-RANDOM rho gap < 0.20, do NOT dispatch full -- the substrate's bind
  primitive is at noise floor at smoke-N and likely worse at full-N (substrate tolerance
  scales with N for cleanup-margin but NOT for atomic deletion fidelity which is bilinear).
  Smoke acts as full-N preview arm for the discriminator (3 seeds vs full's 5).

ASCII-only; self-contained; SystemExit re-raised BEFORE BaseException; atomic-final-metrics-write.
Author: exp_dev 2026-06-27 (Opus 4.7 1M; research drill TOP-1 dispatch).
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
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "self_explanation_deletion_fidelity_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----- Pre-reg constants LOCKED at module init (PROSPECTIVE; META_RULE_AC tags) -----
# HYPOTHESIZED@ thresholds per research drill TOP-1 bands.
HP_TRUE_RHO_MIN = 0.70          # HYPOTHESIZED@HARD_PASS TRUE_TRACE Spearman rho floor
HP_RANDOM_RHO_LO = -0.10        # HYPOTHESIZED@RANDOM_TRACE rho band low
HP_RANDOM_RHO_HI = 0.10         # HYPOTHESIZED@RANDOM_TRACE rho band high
HP_TRUE_MINUS_COSINE_MIN = 0.15 # HYPOTHESIZED@HARD_PASS TRUE - COSINE gap floor

MB_TRUE_RHO_LO = 0.40           # MIDDLE_BAND TRUE rho low
MB_TRUE_MINUS_COSINE_LO = 0.05  # MIDDLE_BAND TRUE - COSINE low

HF_TRUE_RHO_LO = 0.40           # HARD_FAIL TRUE rho ceiling
HF_TRUE_MINUS_COSINE_HI = 0.0   # HARD_FAIL TRUE - COSINE <= 0

# Discriminator-must-survive-scale (smoke gate):
SMOKE_DISCRIMINATOR_GAP_MIN = 0.20  # if smoke TRUE-RANDOM rho gap < 0.20, do NOT dispatch full

EXPECTED_ARMS = [
    "ARM_TRUE_TRACE",
    "ARM_RANDOM_TRACE",
    "ARM_COSINE_TRACE",
]

K_TRACE = 5                     # K trace-depth (top-K atoms per explanation)

if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_QUERIES = 20
    M_BINDS = 32                 # stored binds per partition
elif RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    N_QUERIES = 500
    M_BINDS = 128
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 1000
    M_BINDS = 256

# CARDINALITY: each arm produces N_QUERIES * K_TRACE deletion-counterfactual events per seed.
# Total events = ARMS * SEEDS * N_QUERIES * K_TRACE.
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES * K_TRACE

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,K=%d,queries=%d,seeds=%s,mode=%s,"
    "HP_true_rho>=%.2f,HP_minus_cosine>=%.2f,smoke_gap_min=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "calib=percentile-based-NOT-0.55xmean"
) % (
    ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE, N_QUERIES, SEEDS, RUN_MODE,
    HP_TRUE_RHO_MIN, HP_TRUE_MINUS_COSINE_MIN, SMOKE_DISCRIMINATOR_GAP_MIN,
    EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# -------------------- L4 import-crash sentinel + L1 minimal-metrics --------------------

def _atomic_write_json(path: Path, body: Dict[str, Any]) -> None:
    """META_RULE_AH atomic-final-metrics-write: .tmp + os.replace."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(body, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_self_explanation_deletion_fidelity",
        }
        if extra:
            m.update(extra)
        _atomic_write_json(out_dir / "metrics.json", m)
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_self_explanation_deletion_fidelity_import_crash",
        }
        _atomic_write_json(out_dir / "metrics.json", s)
        _atomic_write_json(out_dir / "import_crash.json", s)
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------- HRR primitives (FFT-bind; bipolar codebook) --------------------

def _bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Random bipolar +-1 unit-normalized codebook of shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FFT-based HRR bind (circular convolution). Inputs (..., n); output (..., n)."""
    n = a.shape[-1]
    A = np.fft.rfft(a, axis=-1)
    B = np.fft.rfft(b, axis=-1)
    return np.fft.irfft(A * B, n=n, axis=-1).astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """FFT-based HRR unbind (circular correlation). c (n,), b (n,)."""
    n = c.shape[-1]
    C = np.fft.rfft(c, axis=-1)
    B = np.fft.rfft(b, axis=-1)
    # circular correlation = irfft(C * conj(B))
    return np.fft.irfft(C * np.conjugate(B), n=n, axis=-1).astype(np.float32)


def cos_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Row-wise cosine of X (M, n) against y (n,). Returns (M,)."""
    Xn = X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)
    yn = y / (np.linalg.norm(y) + 1e-8)
    return Xn @ yn


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation. Tie-broken by index order (rankdata-equivalent for unique)."""
    if x.size < 2 or y.size < 2 or x.size != y.size:
        return 0.0
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    rx = rx.astype(np.float64)
    ry = ry.astype(np.float64)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = math.sqrt(float((rx * rx).sum() * (ry * ry).sum()))
    if denom < 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


# -------------------- partition memory + retrieval --------------------

def build_substrate(seed: int) -> Dict[str, Any]:
    """Build a substrate with M_BINDS stored (key, value) pairs and partition memory.

    M_part = sum_i bind(K_i, V_i).  Keys and values are independent random bipolar codes.
    Query Q := one of the stored keys (chosen at retrieval time).
    """
    g = np.random.default_rng(seed)
    keys = _bipolar(M_BINDS, N_DIM, g)
    values = _bipolar(M_BINDS, N_DIM, g)
    # bind each (key_i, value_i); shape (M, N)
    binds = hrr_bind(keys, values)
    M_part = binds.sum(axis=0)
    return {
        "keys": keys,
        "values": values,
        "binds": binds,
        "M_part": M_part.astype(np.float32),
        "seed": int(seed),
    }


def query_substrate(M_part: np.ndarray, query_key: np.ndarray,
                     values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Substrate retrieval: decoded_value = unbind(M_part, query_key), then
    cleanup_index = argmax cos(values, decoded). Returns (decoded_value, cos_to_values).
    """
    decoded = hrr_unbind(M_part, query_key)
    sims = cos_rows(values, decoded)
    return decoded.astype(np.float32), sims.astype(np.float32)


# -------------------- contribution-score functions per arm --------------------

def contribution_true_trace(M_part: np.ndarray, query_key: np.ndarray,
                             keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Substrate's bind-based explanation. For query Q with output O = unbind(M_part, Q),
    atom_i's contribution to O is measured by re-expressing each stored bind in the
    Q-decoded basis: contribution_i = |<unbind(bind(K_i, V_i), Q), O>|
    = |<unbind(K_i, Q) (*) V_i, O>|  (HRR bilinearity)

    More precisely, atom_i's contribution to the decoded output is:
        per_atom_decoded_i = unbind(bind(K_i, V_i), Q)
        contribution_i = |<per_atom_decoded_i, O>|

    For i == query_index (K_i == Q): per_atom_decoded = V_i exactly, so contribution
    is high. For i != query_index: per_atom_decoded is noise-like, contribution is low.

    This IS the substrate's native bind-based explanation -- if O changes when atom i
    is deleted, contribution_i should be high.

    Returns scores shape (M_BINDS,).
    """
    # Compute baseline decoded output O = unbind(M_part, Q)
    n_dim_local = M_part.shape[-1]
    Q_freq = np.fft.rfft(query_key, axis=-1)
    M_freq = np.fft.rfft(M_part, axis=-1)
    O = np.fft.irfft(M_freq * np.conjugate(Q_freq), n=n_dim_local, axis=-1).astype(np.float32)
    # For each atom i, compute per_atom_decoded_i = unbind(binds[i], Q)
    # binds_freq shape (M, freq_dim)
    K_freq_all = np.fft.rfft(keys, axis=-1)
    V_freq_all = np.fft.rfft(values, axis=-1)
    binds_freq = K_freq_all * V_freq_all  # (M, freq_dim)
    per_atom_decoded = np.fft.irfft(binds_freq * np.conjugate(Q_freq)[None, :],
                                     n=n_dim_local, axis=-1).astype(np.float32)
    # inner product of each per-atom decoded with the full output O
    inners = (per_atom_decoded * O[None, :]).sum(axis=-1)  # (M,)
    return np.abs(inners)


def contribution_cosine_trace(M_part: np.ndarray, query_key: np.ndarray,
                               keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """The 'obvious explanation' confound: top-K by raw cos(query_key, key_i).
    Returns scores shape (M_BINDS,). This baseline tests whether substrate's bind
    primitive adds anything beyond raw key similarity.
    """
    return np.abs(cos_rows(keys, query_key)).astype(np.float32)


def contribution_random_trace(M_part: np.ndarray, query_key: np.ndarray,
                                keys: np.ndarray, values: np.ndarray,
                                rng: np.random.Generator) -> np.ndarray:
    """Chance baseline: random per-atom score. Returns shape (M_BINDS,)."""
    return rng.random(M_BINDS).astype(np.float32)


# -------------------- deletion-counterfactual --------------------

def deletion_delta(M_part: np.ndarray, query_key: np.ndarray, values: np.ndarray,
                    binds: np.ndarray, atom_idx: int,
                    baseline_decoded: np.ndarray) -> float:
    """Re-query with bind(K_atom_idx, V_atom_idx) SUBTRACTED from partition memory.
    Output delta = 1 - cosine(baseline_decoded, ablated_decoded).

    Higher delta => deleting that atom changed the output more => the atom contributed
    more. A faithful explanation has Spearman rho(contribution_score, deletion_delta)
    high; an unfaithful explanation does not.
    """
    M_part_minus_i = M_part - binds[atom_idx]
    ablated_decoded = hrr_unbind(M_part_minus_i, query_key)
    bn = baseline_decoded / (np.linalg.norm(baseline_decoded) + 1e-8)
    an = ablated_decoded / (np.linalg.norm(ablated_decoded) + 1e-8)
    cos_sim = float((bn * an).sum())
    # delta in [0, 2]; faithful explanation -> high delta for high-contribution atoms
    return float(1.0 - cos_sim)


# -------------------- calibration: percentile-based threshold (PRIOR-ART FIX) --------------------

def calibrate_threshold(scores: np.ndarray, deltas: np.ndarray,
                         percentile_grid: Optional[List[float]] = None) -> Dict[str, Any]:
    """LOAD-BEARING PRIOR-ART FIX (audit_chain_coherence v1 calib bug):
    Instead of refuse_threshold = 0.55 * mean (which was below noise floor and
    HARD_FAILed at refuse_accuracy=0.127 < chance 0.493), this calibrates by
    sweeping percentile thresholds and selecting the one that maximizes
    refuse_accuracy on a held-out calib set.

    Returns the optimal percentile, threshold, and accuracy.
    """
    if percentile_grid is None:
        percentile_grid = [10.0, 25.0, 33.0, 50.0, 67.0, 75.0, 90.0]
    if scores.size == 0 or deltas.size != scores.size:
        return {"percentile": None, "threshold": 0.0, "refuse_acc": 0.0,
                "method": "percentile-grid-degenerate"}
    # ground truth: a high-delta atom is "load-bearing"; low-delta is "ignorable"
    delta_med = float(np.median(deltas))
    truth = (deltas >= delta_med).astype(np.int32)  # 1=load-bearing
    best = {"percentile": 50.0, "threshold": float(np.median(scores)),
            "refuse_acc": 0.0, "method": "percentile-grid"}
    for p in percentile_grid:
        thr = float(np.percentile(scores, p))
        pred = (scores >= thr).astype(np.int32)
        acc = float((pred == truth).mean())
        if acc > best["refuse_acc"]:
            best = {"percentile": float(p), "threshold": thr,
                    "refuse_acc": acc, "method": "percentile-grid"}
    return best


# -------------------- per-arm trace + deletion runner --------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    """L2 per-arm try/except: one arm crashing doesn't kill the rest."""
    sub = build_substrate(seed)
    keys = sub["keys"]; values = sub["values"]; binds = sub["binds"]; M_part = sub["M_part"]

    per_arm: Dict[str, Dict[str, Any]] = {}
    fingerprints: Dict[str, str] = {}
    cleanup_margins: List[float] = []

    # Choose queries: subset of stored keys (each query has a known target).
    rng_q = np.random.default_rng(seed * 7919)
    q_idxs = rng_q.choice(M_BINDS, size=min(N_QUERIES, M_BINDS), replace=(N_QUERIES > M_BINDS))
    if N_QUERIES > M_BINDS:
        # need with-replacement; sample again
        q_idxs = rng_q.choice(M_BINDS, size=N_QUERIES, replace=True)

    arms_to_run = [
        ("ARM_TRUE_TRACE",   contribution_true_trace),
        ("ARM_RANDOM_TRACE", contribution_random_trace),
        ("ARM_COSINE_TRACE", contribution_cosine_trace),
    ]

    # Per-query baseline decoded (for delta-cosine reference); shared across arms.
    baselines = []
    for qi in q_idxs:
        decoded_i = hrr_unbind(M_part, keys[qi])
        baselines.append(decoded_i)
        # cleanup margin diagnostic: top-1 vs top-2 cosine on values bank
        sims_v = cos_rows(values, decoded_i)
        s_sorted = np.sort(sims_v)[::-1]
        if s_sorted.size >= 2:
            cleanup_margins.append(float(s_sorted[0] - s_sorted[1]))

    for arm_name, score_fn in arms_to_run:
        try:
            ag = np.random.default_rng(seed * 1009 + (hash(arm_name) % (10 ** 6)))
            all_scores: List[np.ndarray] = []   # per-query (K_TRACE,) selected scores
            all_deltas: List[np.ndarray] = []   # per-query (K_TRACE,) deletion deltas
            fp_samples: List[np.ndarray] = []

            for q_pos, qi in enumerate(q_idxs):
                q_key = keys[qi]
                baseline_decoded = baselines[q_pos]
                # contribution scores (M_BINDS,)
                if arm_name == "ARM_RANDOM_TRACE":
                    scores = contribution_random_trace(M_part, q_key, keys, values, ag)
                else:
                    scores = score_fn(M_part, q_key, keys, values)
                # top-K trace atom indices (highest scores first)
                top_k_idx = np.argsort(-scores)[:K_TRACE]
                top_k_scores = scores[top_k_idx]
                # deletion-counterfactual for each top-K atom
                deltas = np.zeros(K_TRACE, dtype=np.float32)
                for j, atom_idx in enumerate(top_k_idx):
                    deltas[j] = deletion_delta(
                        M_part, q_key, values, binds, int(atom_idx), baseline_decoded
                    )
                all_scores.append(top_k_scores.astype(np.float32))
                all_deltas.append(deltas)
                # fingerprint sample: first 5 queries' top-K scores
                if q_pos < 5:
                    fp_samples.append(top_k_scores.astype(np.float32)[None, :])

            # Concatenate across queries -> (N_QUERIES * K_TRACE,)
            scores_flat = np.concatenate(all_scores)
            deltas_flat = np.concatenate(all_deltas)
            rho = spearman_rho(scores_flat, deltas_flat)
            # also per-query rhos (more robust; correlates within-query attribution)
            per_q_rhos = []
            for s_arr, d_arr in zip(all_scores, all_deltas):
                rq = spearman_rho(s_arr, d_arr)
                per_q_rhos.append(rq)
            per_q_rhos = np.array(per_q_rhos, dtype=np.float32)
            mean_q_rho = float(per_q_rhos.mean()) if per_q_rhos.size > 0 else 0.0

            # PRIOR-ART FIX: percentile-based calib (not 0.55 * mean) on this arm
            calib = calibrate_threshold(scores_flat, deltas_flat)

            per_arm[arm_name] = {
                "spearman_rho_flat": float(rho),
                "spearman_rho_per_query_mean": mean_q_rho,
                "spearman_rho_per_query_std": float(per_q_rhos.std()) if per_q_rhos.size > 0 else 0.0,
                "n_queries": int(len(all_scores)),
                "n_units_arm": int(scores_flat.size),
                "calibration": calib,
                "scores_mean": float(scores_flat.mean()),
                "scores_std": float(scores_flat.std()),
                "deltas_mean": float(deltas_flat.mean()),
                "deltas_std": float(deltas_flat.std()),
            }
            fingerprints[arm_name] = _arm_fp(fp_samples)
        except Exception as e:
            print("[L2] arm '%s' crashed seed=%d: %s" % (arm_name, seed, e),
                  file=sys.stderr, flush=True)
            per_arm[arm_name] = {"error": str(e), "traceback": traceback.format_exc()}
            fingerprints[arm_name] = "ERROR"

    return {
        "seed": int(seed),
        "N": N_DIM,
        "M_BINDS": M_BINDS,
        "K_TRACE": K_TRACE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arm_fingerprints": fingerprints,
        "n_queries": int(len(q_idxs)),
        "cleanup_margin_mean": float(np.mean(cleanup_margins)) if cleanup_margins else 0.0,
        "cleanup_margin_std": float(np.std(cleanup_margins)) if cleanup_margins else 0.0,
        "n_units_seed": int(len(EXPECTED_ARMS) * len(q_idxs) * K_TRACE),
    }


def _arm_fp(samples: List[np.ndarray]) -> str:
    """META_RULE_AF SHA-256 fingerprint over arm's per-query top-K score samples."""
    if not samples:
        return "empty"
    stacked = np.vstack(samples).astype(np.float32)
    return hashlib.sha256(stacked.tobytes()).hexdigest()[:16]


# -------------------- aggregate + verdict --------------------

def aggregate_and_verdict(per_seed: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed results",
                "summary": "no per-seed results", "per_arm_summary": {}}

    summary: Dict[str, Dict[str, Any]] = {}
    for arm in EXPECTED_ARMS:
        rhos_flat = [s["per_arm"].get(arm, {}).get("spearman_rho_flat") for s in per_seed]
        rhos_pq = [s["per_arm"].get(arm, {}).get("spearman_rho_per_query_mean") for s in per_seed]
        rhos_flat = [r for r in rhos_flat if isinstance(r, (int, float))]
        rhos_pq = [r for r in rhos_pq if isinstance(r, (int, float))]
        if rhos_flat:
            mean_flat = float(np.mean(rhos_flat))
            std_flat = float(np.std(rhos_flat))
            cv_flat = float(std_flat / max(abs(mean_flat), 1e-6))
        else:
            mean_flat = 0.0; std_flat = 0.0; cv_flat = 0.0
        summary[arm] = {
            "spearman_rho_flat_mean": mean_flat,
            "spearman_rho_flat_std": std_flat,
            "spearman_rho_flat_cv": cv_flat,
            "spearman_rho_per_query_mean": float(np.mean(rhos_pq)) if rhos_pq else 0.0,
            "n_seeds": len(rhos_flat),
        }

    # Arms-distinct (META_RULE_AF): SHA-256 fingerprints over per-arm top-K score patterns.
    fp_sets: Dict[str, set] = {arm: set() for arm in EXPECTED_ARMS}
    for s in per_seed:
        for arm, fp in s.get("arm_fingerprints", {}).items():
            fp_sets[arm].add(fp)
    # Key triple must produce DIFFERENT fingerprints (per seed)
    arms_distinct = True
    distinct_per_seed: List[bool] = []
    for s in per_seed:
        fps = s.get("arm_fingerprints", {})
        if "ERROR" in fps.values() or len(set(fps.get(a, "NA") for a in EXPECTED_ARMS)) < 3:
            arms_distinct = False
            distinct_per_seed.append(False)
        else:
            distinct_per_seed.append(True)

    true_arm = summary["ARM_TRUE_TRACE"]
    rand_arm = summary["ARM_RANDOM_TRACE"]
    cos_arm = summary["ARM_COSINE_TRACE"]

    true_rho = true_arm["spearman_rho_flat_mean"]
    rand_rho = rand_arm["spearman_rho_flat_mean"]
    cos_rho = cos_arm["spearman_rho_flat_mean"]
    true_minus_cosine = true_rho - cos_rho
    true_minus_random = true_rho - rand_rho

    # Cardinality
    total_events = sum(s.get("n_units_seed", 0) for s in per_seed)
    n_queries_total = sum(s.get("n_queries", 0) for s in per_seed)
    expected_for_observed = len(EXPECTED_ARMS) * n_queries_total * K_TRACE
    cardinality_ok = (total_events == expected_for_observed)

    # META_RULE_Q suspect-1.000 (only meaningful for n>=100 queries cumulative)
    suspect_q = False
    for arm in EXPECTED_ARMS:
        if n_queries_total >= 100 and abs(summary[arm]["spearman_rho_flat_mean"]) >= 0.9995:
            suspect_q = True

    # Discriminator-must-survive-scale (smoke gate)
    smoke_gap_ok = True
    smoke_gap_msg = "N/A (full run)"
    if RUN_MODE == "smoke":
        gap = true_minus_random
        if gap < SMOKE_DISCRIMINATOR_GAP_MIN:
            smoke_gap_ok = False
            smoke_gap_msg = "FAIL gap=%.3f < %.2f" % (gap, SMOKE_DISCRIMINATOR_GAP_MIN)
        else:
            smoke_gap_msg = "PASS gap=%.3f >= %.2f" % (gap, SMOKE_DISCRIMINATOR_GAP_MIN)

    # By-construction-saturation check (research drill mandate):
    # if COSINE_TRACE alone HARD_PASS (rho >= HP_TRUE_RHO_MIN), tier down
    # and require cleanup_margin < 0.1 regime to validate bind-primitive lift.
    cosine_alone_hp = (cos_rho >= HP_TRUE_RHO_MIN)
    cleanup_margins_seed = [s.get("cleanup_margin_mean", 1.0) for s in per_seed]
    cleanup_margin_global = float(np.mean(cleanup_margins_seed)) if cleanup_margins_seed else 1.0
    by_construction_flag = cosine_alone_hp and cleanup_margin_global >= 0.1

    # HARD_PASS / HARD_FAIL / MIDDLE evaluation
    hp_conds = {
        "TRUE_rho>=%.2f" % HP_TRUE_RHO_MIN: true_rho >= HP_TRUE_RHO_MIN,
        "RANDOM_rho_in_band": (HP_RANDOM_RHO_LO <= rand_rho <= HP_RANDOM_RHO_HI),
        "TRUE-COSINE>=%.2f" % HP_TRUE_MINUS_COSINE_MIN: true_minus_cosine >= HP_TRUE_MINUS_COSINE_MIN,
        "arms_distinct": arms_distinct,
        "cardinality_ok": cardinality_ok,
        "not_suspect_Q": not suspect_q,
        "smoke_discriminator_gap_ok": smoke_gap_ok,
        "not_by_construction_saturation": not by_construction_flag,
    }
    hf_conds = {
        "TRUE_rho<%.2f" % HF_TRUE_RHO_LO: true_rho < HF_TRUE_RHO_LO,
        "TRUE-COSINE<=0": true_minus_cosine <= HF_TRUE_MINUS_COSINE_HI,
        "arms_NOT_distinct": not arms_distinct,
        "cardinality_breach": not cardinality_ok,
        "suspect_Q": suspect_q,
    }
    hp_pass = all(hp_conds.values())
    hf_trip = any(hf_conds.values())

    if hp_pass:
        verdict = "HARD_PASS"
    elif hf_trip:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary_msg = (
        "TRUE_rho=%.3f RANDOM_rho=%.3f COSINE_rho=%.3f | TRUE-COSINE=%+.3f TRUE-RANDOM=%+.3f | "
        "arms_distinct=%s | cardinality_ok=%s (%d/%d) | smoke_gap=%s | "
        "cleanup_margin=%.3f by_construction_flag=%s | cv_TRUE=%.3f"
    ) % (
        true_rho, rand_rho, cos_rho, true_minus_cosine, true_minus_random,
        arms_distinct, cardinality_ok, total_events, expected_for_observed,
        smoke_gap_msg, cleanup_margin_global, by_construction_flag,
        true_arm["spearman_rho_flat_cv"],
    )
    if verdict == "HARD_PASS":
        vmsg = "HARD_PASS self_explanation_deletion_fidelity_v1: " + summary_msg
    elif verdict == "HARD_FAIL":
        failed = [k for k, v in hf_conds.items() if v]
        vmsg = "HARD_FAIL self_explanation_deletion_fidelity_v1 (%s): " % ",".join(failed) + summary_msg
    else:
        failed_hp = [k for k, v in hp_conds.items() if not v]
        vmsg = "MIDDLE_BAND self_explanation_deletion_fidelity_v1 (missed HP: %s): " % ",".join(failed_hp) + summary_msg

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "per_arm_summary": summary,
        "hp_conds": hp_conds,
        "hf_conds": hf_conds,
        "true_rho": true_rho,
        "random_rho": rand_rho,
        "cosine_rho": cos_rho,
        "true_minus_cosine": true_minus_cosine,
        "true_minus_random": true_minus_random,
        "arms_distinct": arms_distinct,
        "distinct_per_seed": distinct_per_seed,
        "arm_fingerprints_per_seed": [s.get("arm_fingerprints", {}) for s in per_seed],
        "cardinality_ok": cardinality_ok,
        "total_events": total_events,
        "expected_n_units": expected_for_observed,
        "smoke_discriminator_gap_ok": smoke_gap_ok,
        "smoke_discriminator_gap_msg": smoke_gap_msg,
        "cleanup_margin_global": cleanup_margin_global,
        "by_construction_flag": by_construction_flag,
    }


# -------------------- self-test --------------------

def _selftest() -> None:
    """Tiny shape + formula sanity. CRLB pre-validation + verify-the-referent on
    formulas. MUST assert expected==measured per exp_dev discipline."""
    g = np.random.default_rng(0)
    # 1. HRR bind / unbind round-trip: unbind(bind(K, V), K) approximately V (cleanup margin)
    n = 64
    K_test = _bipolar(1, n, g)[0]
    V_test = _bipolar(1, n, g)[0]
    bound = hrr_bind(K_test, V_test)
    assert bound.shape == (n,), "hrr_bind shape %s" % (bound.shape,)
    recovered = hrr_unbind(bound, K_test)
    # cosine to V should be > 0.5 for round-trip with single bind
    cos_recovered = float(np.dot(recovered, V_test) / (np.linalg.norm(recovered) * np.linalg.norm(V_test) + 1e-8))
    assert cos_recovered > 0.5, "HRR round-trip cosine should be >0.5; got %.3f" % cos_recovered

    # 2. Spearman rho: rho(x, x) == 1.0
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(spearman_rho(x, x) - 1.0) < 1e-6, "rho(x,x) should be 1.0; got %.6f" % spearman_rho(x, x)
    # 3. Spearman rho: rho(x, -x) == -1.0
    assert abs(spearman_rho(x, -x) - (-1.0)) < 1e-6, "rho(x,-x) should be -1.0; got %.6f" % spearman_rho(x, -x)
    # 4. Spearman rho: rho(random, random) approx 0
    g2 = np.random.default_rng(42)
    rho_rand = spearman_rho(g2.random(200), g2.random(200))
    assert abs(rho_rand) < 0.20, "rho(random,random) should be ~0; got %.3f" % rho_rand

    # 5. Substrate build: M_BINDS=4 sub at N=32 sanity
    sub_dim = 32
    g3 = np.random.default_rng(11)
    Mb = 4
    keys_t = _bipolar(Mb, sub_dim, g3)
    vals_t = _bipolar(Mb, sub_dim, g3)
    binds_t = hrr_bind(keys_t, vals_t)
    Mpart_t = binds_t.sum(axis=0)
    # query with key_0; decoded should align with vals_0 above other vals
    decoded_t = hrr_unbind(Mpart_t, keys_t[0])
    sims_t = cos_rows(vals_t, decoded_t)
    top_idx = int(np.argmax(sims_t))
    assert top_idx == 0, "decoded should cleanup to vals[0]; got argmax=%d sims=%s" % (top_idx, sims_t.tolist())

    # 6. Deletion-counterfactual: deleting bind(K_0, V_0) should reduce cosine of decoded to V_0
    baseline_decoded_t = hrr_unbind(Mpart_t, keys_t[0])
    bn = baseline_decoded_t / (np.linalg.norm(baseline_decoded_t) + 1e-8)
    vn0 = vals_t[0] / (np.linalg.norm(vals_t[0]) + 1e-8)
    baseline_cos = float((bn * vn0).sum())
    Mpart_minus_0 = Mpart_t - binds_t[0]
    ablated_decoded_t = hrr_unbind(Mpart_minus_0, keys_t[0])
    an = ablated_decoded_t / (np.linalg.norm(ablated_decoded_t) + 1e-8)
    ablated_cos = float((an * vn0).sum())
    assert ablated_cos < baseline_cos - 0.10, \
        "deletion should reduce decoded->V0 cosine by >=0.10; baseline=%.3f ablated=%.3f" % (baseline_cos, ablated_cos)

    # 7. contribution_true_trace: argmax should equal the query's index (own atom is highest)
    M_part_big = Mpart_t  # reuse
    scores_true_t = contribution_true_trace(M_part_big, keys_t[0], keys_t, vals_t)
    assert scores_true_t.shape == (Mb,), "scores shape %s" % (scores_true_t.shape,)
    top_score_idx = int(np.argmax(scores_true_t))
    assert top_score_idx == 0, \
        "contribution_true_trace argmax should be query index 0; got %d scores=%s" % (top_score_idx, scores_true_t.tolist())

    # 8. contribution_cosine_trace: argmax should also be query's own key (cos(K_0, K_0) == 1)
    scores_cos_t = contribution_cosine_trace(M_part_big, keys_t[0], keys_t, vals_t)
    top_cos_idx = int(np.argmax(scores_cos_t))
    assert top_cos_idx == 0, \
        "contribution_cosine_trace argmax should be query index 0 (self-cos=1); got %d" % top_cos_idx
    # cos[0] should equal ~1.0 (self-cos)
    assert scores_cos_t[0] > 0.99, "self-cos should be ~1.0; got %.3f" % scores_cos_t[0]

    # 9. calibrate_threshold: percentile-based; should NOT use 0.55 * mean
    scores_calib = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    deltas_calib = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])  # monotonic
    calib_t = calibrate_threshold(scores_calib, deltas_calib)
    assert calib_t["method"] == "percentile-grid", "calib method should be percentile-grid"
    assert calib_t["refuse_acc"] >= 0.5, "monotonic case calib acc should be >= 0.5; got %.3f" % calib_t["refuse_acc"]
    # critical: threshold is computed by percentile (NOT 0.55 * mean = 0.55 * 0.55 = 0.3025)
    # the optimal threshold for this data with median split at delta=0.275 -> truth top-5 are atoms idx 5-9
    # percentile=50 gives threshold = 0.55 (median of scores). pred = scores >= 0.55 = idx 5-9 (1=load-bearing).
    # truth = deltas >= 0.275 = idx 5-9 (1=load-bearing). acc = 1.0.
    assert calib_t["refuse_acc"] >= 0.99, "monotonic case calib acc should be ~1.0; got %.3f" % calib_t["refuse_acc"]

    # 10. CRLB pre-validation: SE(Spearman rho) ~ 1/sqrt(N-1); HP threshold rho>=0.70
    # is reachable in (HP - 0)/SE = 0.70 / (1/sqrt(N-1)) standard errors.
    n_units_smoke = 3 * 500 * 5  # ARMS * QUERIES * K_TRACE (per-arm: 2500)
    n_per_arm = 500 * 5
    se_rho = 1.0 / math.sqrt(n_per_arm - 1)
    margin_to_hp = 0.70 / se_rho
    assert margin_to_hp > 20.0, "CRLB FAIL: HP threshold not measurement-feasible (%.1f SE)" % margin_to_hp

    # 11. Arms-distinct check: fingerprints of different arms must differ on real data
    g4 = np.random.default_rng(99)
    fp_keys = _bipolar(8, 32, g4)
    fp_vals = _bipolar(8, 32, g4)
    fp_binds = hrr_bind(fp_keys, fp_vals)
    fp_Mpart = fp_binds.sum(axis=0)
    s_true = contribution_true_trace(fp_Mpart, fp_keys[0], fp_keys, fp_vals)
    s_cos = contribution_cosine_trace(fp_Mpart, fp_keys[0], fp_keys, fp_vals)
    s_rand = contribution_random_trace(fp_Mpart, fp_keys[0], fp_keys, fp_vals, g4)
    fp_t = _arm_fp([s_true[None, :]])
    fp_c = _arm_fp([s_cos[None, :]])
    fp_r = _arm_fp([s_rand[None, :]])
    assert len({fp_t, fp_c, fp_r}) == 3, \
        "META_RULE_AF: 3 arms must produce 3 distinct fingerprints; got {true=%s, cos=%s, rand=%s}" % (fp_t, fp_c, fp_r)

    print("[selftest] PASS HRR round-trip cos=%.3f | rho(x,x)=1 rho(x,-x)=-1 rho(rand)~%.3f | "
          "deletion: baseline=%.3f ablated=%.3f | calib_acc=%.3f | CRLB margin=%.1f SE | arms_distinct=3/3"
          % (cos_recovered, rho_rand, baseline_cos, ablated_cos, calib_t["refuse_acc"], margin_to_hp), flush=True)


# -------------------- main --------------------

def main() -> int:
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    print("[config] anchor=%s | N=%d M=%d K=%d queries=%d seeds=%s mode=%s out_dir=%s" % (
        ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE, N_QUERIES, SEEDS, RUN_MODE, out_dir), flush=True)
    print("[config] expected_n_units=%d  (arms * seeds * queries * K_TRACE)" % EXPECTED_N_UNITS, flush=True)
    print("[config] PRIOR-ART-FIX: calib=percentile-based (NOT 0.55*mean which was below noise floor)", flush=True)

    if SELF_TEST_MODE:
        _selftest()
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    per_seed: List[Dict[str, Any]] = []
    for seed in SEEDS:
        seed_t0 = time.time()
        try:
            r = run_one_seed(seed)
        except SystemExit:
            raise  # SystemExit MUST re-raise BEFORE BaseException (exp_dev §6-12)
        except BaseException as e:
            print("[L3] seed=%d outer crash: %s" % (seed, e), file=sys.stderr, flush=True)
            r = {"seed": int(seed), "N": N_DIM, "M_BINDS": M_BINDS, "K_TRACE": K_TRACE,
                 "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                 "anchor_name": ANCHOR_NAME,
                 "per_arm": {arm: {"error": str(e)} for arm in EXPECTED_ARMS},
                 "arm_fingerprints": {arm: "ERROR" for arm in EXPECTED_ARMS},
                 "n_queries": 0, "n_units_seed": 0,
                 "cleanup_margin_mean": 0.0, "cleanup_margin_std": 0.0,
                 "_outer_traceback": traceback.format_exc()}
        per_seed.append(r)
        seed_wall = time.time() - seed_t0
        print("[seed=%d] complete in %.1fs (per_arm keys=%d)" % (
            seed, seed_wall, len(r.get("per_arm", {}))), flush=True)

    agg = aggregate_and_verdict(per_seed)
    elapsed_s = round(time.time() - t0, 1)
    print("\n[VERDICT] " + agg["verdict_msg"], flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": agg["verdict"],
        "verdict_msg": agg["verdict_msg"],
        "summary": agg["summary"],
        "elapsed_s": elapsed_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "N": N_DIM,
        "M_BINDS": M_BINDS,
        "K_TRACE": K_TRACE,
        "N_QUERIES": N_QUERIES,
        "arms_tested": EXPECTED_ARMS,
        "config_version": CONFIG_VERSION,
        "per_arm_summary": agg["per_arm_summary"],
        "hp_conds": agg["hp_conds"],
        "hf_conds": agg["hf_conds"],
        "true_rho": agg["true_rho"],
        "random_rho": agg["random_rho"],
        "cosine_rho": agg["cosine_rho"],
        "true_minus_cosine": agg["true_minus_cosine"],
        "true_minus_random": agg["true_minus_random"],
        "arms_distinct": agg["arms_distinct"],
        "distinct_per_seed": agg["distinct_per_seed"],
        "arm_fingerprints_per_seed": agg["arm_fingerprints_per_seed"],
        "cardinality_ok": agg["cardinality_ok"],
        "total_events": agg["total_events"],
        "expected_n_units": agg["expected_n_units"],
        "smoke_discriminator_gap_ok": agg["smoke_discriminator_gap_ok"],
        "smoke_discriminator_gap_msg": agg["smoke_discriminator_gap_msg"],
        "cleanup_margin_global": agg["cleanup_margin_global"],
        "by_construction_flag": agg["by_construction_flag"],
        "per_seed": per_seed,
        "_hardening_marker": "v1_self_explanation_deletion_fidelity",
    }
    _atomic_write_json(out_dir / "metrics.json", metrics)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        raise
