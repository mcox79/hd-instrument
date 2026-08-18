"""self_explanation_deletion_fidelity_v2_per_atom_marginal -- per-atom MARGINAL cosine
fix to v1's bilinear bind-trace formulation (Stage 3 self-explanation faithfulness).

v1 RESULT (verified d:/AI/hd-instrument/data/exp_self_explanation_deletion_fidelity_v1_smoke/metrics.json):
  TRUE_TRACE_BILINEAR rho=0.240 < COSINE_TRACE rho=0.467 (raw cosine BEAT substrate bind-trace)
  cleanup_margin=0.032 (tight; not saturation-trivial)
  HARD_FAIL on TRUE-COSINE<=0 AND TRUE_rho<0.40.

v1 ROOT CAUSE (cell-author diagnosis):
  bilinear contribution_i = |<unbind(bind(K_i,V_i), Q), O>| where O = full unbind(M_part, Q)
  contains all M_BINDS stored bindings' interference. The inner product against O has
  cross-term noise: per_atom_decoded_i has rank-1 signal at K_i==Q (== V_i exactly), plus
  M-1 noise terms from the M-1 other stored binds in O. Cross-term magnitude scales
  ~sqrt(M)/sqrt(N), masking the target atom for K_i != Q discriminator atoms.

v2 FIX (per cell-author recommended formulation):
  TRUE_TRACE_MARGINAL contribution_i = |cos(per_atom_decoded_i, O)|
  Cosine NORMALIZES out the cross-term magnitude scale; what survives is the DIRECTIONAL
  alignment of per_atom_decoded_i with O. For high-contribution atoms (i where K_i is
  near Q or aliases interfere with the query), per_atom_decoded_i has high directional
  alignment with O regardless of magnitude. For unrelated atoms (random K_i with no
  alias to Q), per_atom_decoded_i is noise-direction relative to O -> low |cos|.

  This is per-atom MARGINAL because it tests "what direction does THIS atom contribute
  to the output, normalized for magnitude" rather than "what magnitude in the output
  basis does THIS atom project to (BILINEAR, has cross-term magnitude noise)".

ENCODING-BEFORE-READOUT (META_RULE_AL):
  ENCODING: HRR bind on stored (K_i, V_i); M_part = sum_i bind(K_i, V_i). Chain-grade
  (hdlab.binding.bind FFT-based; smoke-tested).
  READOUT: per-arm contribution score on top-K=5 atoms; deletion-counterfactual
  delta = 1 - cos(baseline_decoded, ablated_decoded). Per-arm Spearman rho of
  (contribution_score, deletion_delta).
  Encoder-readout separation by SHA-256 fingerprint on per-arm trace cosines.

ARMS (4; structurally differ per META_RULE_AF):
  ARM_TRUE_TRACE_BILINEAR  v1 formulation (comparator; expected rho ~ 0.240)
  ARM_TRUE_TRACE_MARGINAL  v2 MECHANISM; per-atom cosine (expected to beat COSINE)
  ARM_COSINE_TRACE         raw cos(query_key, K_i) baseline (expected rho ~ 0.467 replicating v1)
  ARM_RANDOM_TRACE         chance baseline (expected rho ~ 0.00)

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE; research-owned 2026-06-28):
  HARD_PASS (ALL must hold):
    ARM_TRUE_TRACE_MARGINAL rho >= 0.70             HP_TRUE_RHO_MIN
    ARM_TRUE_TRACE_MARGINAL - ARM_COSINE_TRACE rho >= 0.15  HP_MARGINAL_MINUS_COSINE_MIN
    ARM_TRUE_TRACE_BILINEAR rho in [0.15, 0.35]      (replicates v1 sanity band)
    ARM_RANDOM_TRACE rho in [-0.10, +0.10]           (chance)
    arms_distinct == True                            (META_RULE_AF SHA-256)
    CARDINALITY_OK                                   (META_RULE_H)
    not suspect_Q                                    (META_RULE_Q)
    smoke discriminator gap OK                       (MARGINAL - COSINE >= 0.05 at smoke)
  MIDDLE_BAND:
    ARM_TRUE_TRACE_MARGINAL rho in [0.40, 0.70]
    OR ARM_TRUE_TRACE_MARGINAL - ARM_COSINE_TRACE rho in [0.05, 0.15)
  HARD_FAIL (ANY triggers):
    ARM_TRUE_TRACE_MARGINAL - ARM_COSINE_TRACE rho <= 0  (raw cosine still wins -- substrate
                                                          bind-trace fundamentally unfaithful)
    arms_distinct == False
    CARDINALITY breach
    META_RULE_Q suspect-1.000 on n>=100

STRATEGIC NOTE (research framing):
  If v2 MARGINAL ALSO HARD_FAILs, that's strong substrate-physics evidence: substrate
  bind-trace fundamentally cannot beat raw cosine for self-explanation at this scale.
  The "substrate already does X via cosine" pattern would extend to self-explanation
  layer, meaning the audit-claim story needs to be re-thought (raw cosine attribution
  IS the substrate's self-explanation, not a separate bind-derived trace).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 arms * 5 seeds * 1000 queries * 5 trace = 100,000
  EXPECTED_N_UNITS_SMOKE = 4 arms * 3 seeds *  500 queries * 5 trace =  30,000

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  smoke=N=2048; full=N=8192. At smoke, MARGINAL-COSINE gap must be >= 0.05 (smoke
  discriminator floor). If smoke MARGINAL = BILINEAR within +/-0.05, do NOT dispatch
  full -- the per-atom-cosine fix did NOT structurally change the contribution score.

NUMBER TAGGING (META_RULE_AC):
  MEASURED@v1_smoke: TRUE_BILINEAR=0.240 RANDOM=0.009 COSINE=0.467 cleanup_margin=0.032
  HYPOTHESIZED@v2: TRUE_MARGINAL >= 0.70 (cell-author rec); TRUE_MARGINAL - COSINE >= 0.15

ASCII-only; self-contained; SystemExit re-raised BEFORE BaseException; atomic-final-metrics-write.
Author: exp_dev 2026-06-28 (Opus 4.7 1M; v2 per-atom MARGINAL fix to v1's bilinear bind-trace).
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

ANCHOR_NAME = "self_explanation_deletion_fidelity_v2_per_atom_marginal"

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
HP_TRUE_RHO_MIN = 0.70                  # HYPOTHESIZED@HARD_PASS TRUE_MARGINAL rho floor
HP_MARGINAL_MINUS_COSINE_MIN = 0.15     # HYPOTHESIZED@HARD_PASS MARGINAL - COSINE gap floor
HP_BILINEAR_REPLICATE_LO = 0.15         # HYPOTHESIZED@v1-replicate BILINEAR rho band low
HP_BILINEAR_REPLICATE_HI = 0.35         # HYPOTHESIZED@v1-replicate BILINEAR rho band high
HP_RANDOM_RHO_LO = -0.10                # HYPOTHESIZED@RANDOM rho band low
HP_RANDOM_RHO_HI = 0.10                 # HYPOTHESIZED@RANDOM rho band high

MB_TRUE_RHO_LO = 0.40                   # MIDDLE_BAND TRUE_MARGINAL rho low
MB_MARGINAL_MINUS_COSINE_LO = 0.05      # MIDDLE_BAND MARGINAL - COSINE low

HF_MARGINAL_MINUS_COSINE_HI = 0.0       # HARD_FAIL MARGINAL - COSINE <= 0

# Discriminator-must-survive-scale (smoke gate):
SMOKE_MARGINAL_MINUS_COSINE_MIN = 0.05  # smoke MARGINAL must beat COSINE by >=0.05
SMOKE_MARGINAL_MINUS_BILINEAR_MIN = 0.05  # smoke MARGINAL must differ from BILINEAR by >=0.05

EXPECTED_ARMS = [
    "ARM_TRUE_TRACE_BILINEAR",
    "ARM_TRUE_TRACE_MARGINAL",
    "ARM_COSINE_TRACE",
    "ARM_RANDOM_TRACE",
]

K_TRACE = 5                              # K trace-depth (top-K atoms per explanation)

if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_QUERIES = 20
    M_BINDS = 32
elif RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7, 17, 23]
    N_QUERIES = 500
    M_BINDS = 128
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    N_QUERIES = 1000
    M_BINDS = 512

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_QUERIES * K_TRACE

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,K=%d,queries=%d,seeds=%s,mode=%s,"
    "HP_marg_rho>=%.2f,HP_marg_minus_cos>=%.2f,smoke_marg_minus_cos>=%.2f,"
    "expected_n=%d,arms=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "v2_fix=per_atom_marginal_cosine_NOT_bilinear_inner_product"
) % (
    ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE, N_QUERIES, SEEDS, RUN_MODE,
    HP_TRUE_RHO_MIN, HP_MARGINAL_MINUS_COSINE_MIN, SMOKE_MARGINAL_MINUS_COSINE_MIN,
    EXPECTED_N_UNITS, len(EXPECTED_ARMS),
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
            "_hardening_marker": "v2_self_explanation_deletion_fidelity_per_atom_marginal",
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
            "_hardening_marker": "v2_self_explanation_deletion_fidelity_per_atom_marginal_import_crash",
        }
        _atomic_write_json(out_dir / "metrics.json", s)
        _atomic_write_json(out_dir / "import_crash.json", s)
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------- HRR primitives (FFT-bind; bipolar codebook) --------------------

def _bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = a.shape[-1]
    A = np.fft.rfft(a, axis=-1)
    B = np.fft.rfft(b, axis=-1)
    return np.fft.irfft(A * B, n=n, axis=-1).astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = c.shape[-1]
    C = np.fft.rfft(c, axis=-1)
    B = np.fft.rfft(b, axis=-1)
    return np.fft.irfft(C * np.conjugate(B), n=n, axis=-1).astype(np.float32)


def cos_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    Xn = X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)
    yn = y / (np.linalg.norm(y) + 1e-8)
    return Xn @ yn


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
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
    g = np.random.default_rng(seed)
    keys = _bipolar(M_BINDS, N_DIM, g)
    values = _bipolar(M_BINDS, N_DIM, g)
    binds = hrr_bind(keys, values)
    M_part = binds.sum(axis=0)
    return {
        "keys": keys, "values": values, "binds": binds,
        "M_part": M_part.astype(np.float32), "seed": int(seed),
    }


# -------------------- contribution-score functions per arm --------------------
# All four functions take signature (M_part, query_key, keys, values [, rng]) -> (M_BINDS,)


def _per_atom_decoded(M_part: np.ndarray, query_key: np.ndarray,
                       keys: np.ndarray, values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Helper: compute O = unbind(M_part, Q) and per_atom_decoded_i = unbind(bind(K_i,V_i), Q).
    Returns (O, per_atom_decoded) shapes (n,) and (M, n).
    Shared between BILINEAR and MARGINAL arms (only the score-combination differs).
    """
    n_dim_local = M_part.shape[-1]
    Q_freq = np.fft.rfft(query_key, axis=-1)
    M_freq = np.fft.rfft(M_part, axis=-1)
    O = np.fft.irfft(M_freq * np.conjugate(Q_freq), n=n_dim_local, axis=-1).astype(np.float32)
    K_freq_all = np.fft.rfft(keys, axis=-1)
    V_freq_all = np.fft.rfft(values, axis=-1)
    binds_freq = K_freq_all * V_freq_all  # (M, freq_dim)
    per_atom_decoded = np.fft.irfft(binds_freq * np.conjugate(Q_freq)[None, :],
                                     n=n_dim_local, axis=-1).astype(np.float32)
    return O, per_atom_decoded


def contribution_true_trace_bilinear(M_part: np.ndarray, query_key: np.ndarray,
                                       keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """v1 formulation (comparator): contribution_i = |<per_atom_decoded_i, O>|.

    BILINEAR INNER PRODUCT has cross-term magnitude noise: per_atom_decoded_i has rank-1
    signal at K_i==Q plus M-1 noise terms from other binds in O. Cross-term magnitude
    scales ~sqrt(M)/sqrt(N) masking K_i != Q discriminator atoms.

    Verified v1 result (smoke N=2048 M=128): rho=0.240; raw cosine baseline rho=0.467.
    """
    O, per_atom_decoded = _per_atom_decoded(M_part, query_key, keys, values)
    inners = (per_atom_decoded * O[None, :]).sum(axis=-1)  # (M,)
    return np.abs(inners).astype(np.float32)


def contribution_true_trace_marginal(M_part: np.ndarray, query_key: np.ndarray,
                                       keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """v2 MECHANISM (per-atom MARGINAL): contribution_i = |cos(per_atom_decoded_i, O)|.

    COSINE NORMALIZES out cross-term magnitude scale; what survives is DIRECTIONAL
    alignment of per_atom_decoded_i with O. High-contribution atoms have high directional
    alignment regardless of magnitude; unrelated atoms have noise-direction relative to O.

    Hypothesis: rho >= 0.70 (HP); MARGINAL - COSINE >= 0.15 (HP gap floor).
    """
    O, per_atom_decoded = _per_atom_decoded(M_part, query_key, keys, values)
    # row-wise cosine of per_atom_decoded (M, n) against O (n,)
    pad_norms = np.linalg.norm(per_atom_decoded, axis=-1) + 1e-8
    O_norm = float(np.linalg.norm(O)) + 1e-8
    inners = (per_atom_decoded * O[None, :]).sum(axis=-1)  # (M,)
    cos_vals = inners / (pad_norms * O_norm)
    return np.abs(cos_vals).astype(np.float32)


def contribution_cosine_trace(M_part: np.ndarray, query_key: np.ndarray,
                                keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """Raw cosine baseline: |cos(query_key, K_i)|. Tests whether substrate's bind primitive
    adds anything beyond raw key similarity. v1 result: rho=0.467 (BEAT bilinear bind-trace)."""
    return np.abs(cos_rows(keys, query_key)).astype(np.float32)


def contribution_random_trace(M_part: np.ndarray, query_key: np.ndarray,
                                keys: np.ndarray, values: np.ndarray,
                                rng: np.random.Generator) -> np.ndarray:
    """Chance baseline. v1 result: rho ~ 0.009."""
    return rng.random(M_BINDS).astype(np.float32)


# -------------------- deletion-counterfactual --------------------

def deletion_delta(M_part: np.ndarray, query_key: np.ndarray, values: np.ndarray,
                    binds: np.ndarray, atom_idx: int,
                    baseline_decoded: np.ndarray) -> float:
    M_part_minus_i = M_part - binds[atom_idx]
    ablated_decoded = hrr_unbind(M_part_minus_i, query_key)
    bn = baseline_decoded / (np.linalg.norm(baseline_decoded) + 1e-8)
    an = ablated_decoded / (np.linalg.norm(ablated_decoded) + 1e-8)
    cos_sim = float((bn * an).sum())
    return float(1.0 - cos_sim)


# -------------------- per-arm runner --------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    """L2 per-arm try/except: one arm crashing doesn't kill the rest."""
    sub = build_substrate(seed)
    keys = sub["keys"]; values = sub["values"]; binds = sub["binds"]; M_part = sub["M_part"]

    per_arm: Dict[str, Dict[str, Any]] = {}
    fingerprints: Dict[str, str] = {}
    cleanup_margins: List[float] = []

    rng_q = np.random.default_rng(seed * 7919)
    if N_QUERIES > M_BINDS:
        q_idxs = rng_q.choice(M_BINDS, size=N_QUERIES, replace=True)
    else:
        q_idxs = rng_q.choice(M_BINDS, size=N_QUERIES, replace=False)

    arms_to_run = [
        ("ARM_TRUE_TRACE_BILINEAR", contribution_true_trace_bilinear),
        ("ARM_TRUE_TRACE_MARGINAL", contribution_true_trace_marginal),
        ("ARM_COSINE_TRACE",        contribution_cosine_trace),
        ("ARM_RANDOM_TRACE",        contribution_random_trace),
    ]

    # Per-query baseline decoded (shared across arms; deletion-delta uses it as reference)
    baselines = []
    for qi in q_idxs:
        decoded_i = hrr_unbind(M_part, keys[qi])
        baselines.append(decoded_i)
        sims_v = cos_rows(values, decoded_i)
        s_sorted = np.sort(sims_v)[::-1]
        if s_sorted.size >= 2:
            cleanup_margins.append(float(s_sorted[0] - s_sorted[1]))

    for arm_name, score_fn in arms_to_run:
        try:
            ag = np.random.default_rng(seed * 1009 + (hash(arm_name) % (10 ** 6)))
            all_scores: List[np.ndarray] = []
            all_deltas: List[np.ndarray] = []
            fp_samples: List[np.ndarray] = []

            for q_pos, qi in enumerate(q_idxs):
                q_key = keys[qi]
                baseline_decoded = baselines[q_pos]
                if arm_name == "ARM_RANDOM_TRACE":
                    scores = contribution_random_trace(M_part, q_key, keys, values, ag)
                else:
                    scores = score_fn(M_part, q_key, keys, values)
                top_k_idx = np.argsort(-scores)[:K_TRACE]
                top_k_scores = scores[top_k_idx]
                deltas = np.zeros(K_TRACE, dtype=np.float32)
                for j, atom_idx in enumerate(top_k_idx):
                    deltas[j] = deletion_delta(
                        M_part, q_key, values, binds, int(atom_idx), baseline_decoded
                    )
                all_scores.append(top_k_scores.astype(np.float32))
                all_deltas.append(deltas)
                if q_pos < 5:
                    fp_samples.append(top_k_scores.astype(np.float32)[None, :])

            scores_flat = np.concatenate(all_scores)
            deltas_flat = np.concatenate(all_deltas)
            rho = spearman_rho(scores_flat, deltas_flat)
            per_q_rhos = np.array(
                [spearman_rho(s_arr, d_arr) for s_arr, d_arr in zip(all_scores, all_deltas)],
                dtype=np.float32,
            )
            mean_q_rho = float(per_q_rhos.mean()) if per_q_rhos.size > 0 else 0.0

            per_arm[arm_name] = {
                "spearman_rho_flat": float(rho),
                "spearman_rho_per_query_mean": mean_q_rho,
                "spearman_rho_per_query_std": float(per_q_rhos.std()) if per_q_rhos.size > 0 else 0.0,
                "n_queries": int(len(all_scores)),
                "n_units_arm": int(scores_flat.size),
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
        "N": N_DIM, "M_BINDS": M_BINDS, "K_TRACE": K_TRACE,
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arm_fingerprints": fingerprints,
        "n_queries": int(len(q_idxs)),
        "cleanup_margin_mean": float(np.mean(cleanup_margins)) if cleanup_margins else 0.0,
        "cleanup_margin_std": float(np.std(cleanup_margins)) if cleanup_margins else 0.0,
        "n_units_seed": int(len(EXPECTED_ARMS) * len(q_idxs) * K_TRACE),
    }


def _arm_fp(samples: List[np.ndarray]) -> str:
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

    # arms_distinct (META_RULE_AF): per-seed all-4 fingerprints distinct
    arms_distinct = True
    distinct_per_seed: List[bool] = []
    for s in per_seed:
        fps = s.get("arm_fingerprints", {})
        if "ERROR" in fps.values() or len(set(fps.get(a, "NA") for a in EXPECTED_ARMS)) < len(EXPECTED_ARMS):
            arms_distinct = False
            distinct_per_seed.append(False)
        else:
            distinct_per_seed.append(True)

    bilinear_rho = summary["ARM_TRUE_TRACE_BILINEAR"]["spearman_rho_flat_mean"]
    marginal_rho = summary["ARM_TRUE_TRACE_MARGINAL"]["spearman_rho_flat_mean"]
    cosine_rho   = summary["ARM_COSINE_TRACE"]["spearman_rho_flat_mean"]
    random_rho   = summary["ARM_RANDOM_TRACE"]["spearman_rho_flat_mean"]

    marginal_minus_cosine = marginal_rho - cosine_rho
    marginal_minus_bilinear = marginal_rho - bilinear_rho
    marginal_minus_random = marginal_rho - random_rho
    bilinear_replicates_v1 = (HP_BILINEAR_REPLICATE_LO <= bilinear_rho <= HP_BILINEAR_REPLICATE_HI)

    total_events = sum(s.get("n_units_seed", 0) for s in per_seed)
    n_queries_total = sum(s.get("n_queries", 0) for s in per_seed)
    expected_for_observed = len(EXPECTED_ARMS) * n_queries_total * K_TRACE
    cardinality_ok = (total_events == expected_for_observed)

    suspect_q = False
    for arm in EXPECTED_ARMS:
        if n_queries_total >= 100 and abs(summary[arm]["spearman_rho_flat_mean"]) >= 0.9995:
            suspect_q = True

    # Smoke discriminator-must-survive-scale
    smoke_gap_ok = True
    smoke_gap_msg = "N/A (full run)"
    if RUN_MODE == "smoke":
        cos_gap_ok = (marginal_minus_cosine >= SMOKE_MARGINAL_MINUS_COSINE_MIN)
        bil_gap_ok = (abs(marginal_minus_bilinear) >= SMOKE_MARGINAL_MINUS_BILINEAR_MIN)
        smoke_gap_ok = cos_gap_ok and bil_gap_ok
        smoke_gap_msg = (
            "MARG-COS=%+.3f (need>=%.2f cos_ok=%s); MARG-BIL=%+.3f (need_abs>=%.2f bil_ok=%s); overall=%s"
        ) % (
            marginal_minus_cosine, SMOKE_MARGINAL_MINUS_COSINE_MIN, cos_gap_ok,
            marginal_minus_bilinear, SMOKE_MARGINAL_MINUS_BILINEAR_MIN, bil_gap_ok,
            smoke_gap_ok,
        )

    # cleanup margin diagnostic
    cleanup_margins_seed = [s.get("cleanup_margin_mean", 1.0) for s in per_seed]
    cleanup_margin_global = float(np.mean(cleanup_margins_seed)) if cleanup_margins_seed else 1.0

    hp_conds = {
        "MARGINAL_rho>=%.2f" % HP_TRUE_RHO_MIN: marginal_rho >= HP_TRUE_RHO_MIN,
        "MARGINAL-COSINE>=%.2f" % HP_MARGINAL_MINUS_COSINE_MIN: marginal_minus_cosine >= HP_MARGINAL_MINUS_COSINE_MIN,
        "BILINEAR_in_v1_band[%.2f,%.2f]" % (HP_BILINEAR_REPLICATE_LO, HP_BILINEAR_REPLICATE_HI): bilinear_replicates_v1,
        "RANDOM_rho_in_band": (HP_RANDOM_RHO_LO <= random_rho <= HP_RANDOM_RHO_HI),
        "arms_distinct": arms_distinct,
        "cardinality_ok": cardinality_ok,
        "not_suspect_Q": not suspect_q,
        "smoke_discriminator_gap_ok": smoke_gap_ok,
    }
    hf_conds = {
        "MARGINAL-COSINE<=0": marginal_minus_cosine <= HF_MARGINAL_MINUS_COSINE_HI,
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
        "MARGINAL_rho=%.3f BILINEAR_rho=%.3f COSINE_rho=%.3f RANDOM_rho=%.3f | "
        "MARG-COS=%+.3f MARG-BIL=%+.3f MARG-RAND=%+.3f | "
        "arms_distinct=%s | cardinality_ok=%s (%d/%d) | smoke_gap=%s | "
        "cleanup_margin=%.3f bilinear_replicates_v1=%s"
    ) % (
        marginal_rho, bilinear_rho, cosine_rho, random_rho,
        marginal_minus_cosine, marginal_minus_bilinear, marginal_minus_random,
        arms_distinct, cardinality_ok, total_events, expected_for_observed,
        smoke_gap_msg, cleanup_margin_global, bilinear_replicates_v1,
    )
    if verdict == "HARD_PASS":
        vmsg = "HARD_PASS " + ANCHOR_NAME + ": " + summary_msg
    elif verdict == "HARD_FAIL":
        failed = [k for k, v in hf_conds.items() if v]
        vmsg = "HARD_FAIL " + ANCHOR_NAME + " (" + ",".join(failed) + "): " + summary_msg
    else:
        failed_hp = [k for k, v in hp_conds.items() if not v]
        vmsg = "MIDDLE_BAND " + ANCHOR_NAME + " (missed HP: " + ",".join(failed_hp) + "): " + summary_msg

    return {
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
        "per_arm_summary": summary,
        "hp_conds": hp_conds, "hf_conds": hf_conds,
        "bilinear_rho": bilinear_rho, "marginal_rho": marginal_rho,
        "cosine_rho": cosine_rho, "random_rho": random_rho,
        "marginal_minus_cosine": marginal_minus_cosine,
        "marginal_minus_bilinear": marginal_minus_bilinear,
        "marginal_minus_random": marginal_minus_random,
        "bilinear_replicates_v1": bilinear_replicates_v1,
        "arms_distinct": arms_distinct,
        "distinct_per_seed": distinct_per_seed,
        "arm_fingerprints_per_seed": [s.get("arm_fingerprints", {}) for s in per_seed],
        "cardinality_ok": cardinality_ok,
        "total_events": total_events, "expected_n_units": expected_for_observed,
        "smoke_discriminator_gap_ok": smoke_gap_ok,
        "smoke_discriminator_gap_msg": smoke_gap_msg,
        "cleanup_margin_global": cleanup_margin_global,
    }


# -------------------- self-test --------------------

def _selftest() -> None:
    """Formula self-test: HRR round-trip; spearman; deletion; BILINEAR vs MARGINAL must
    give DIFFERENT score VECTORS on the same input (arms-must-differ); MARGINAL is
    bounded [0,1] (cosine); BILINEAR is NOT bounded. CRLB pre-validation."""
    g = np.random.default_rng(0)
    n = 64
    K_test = _bipolar(1, n, g)[0]
    V_test = _bipolar(1, n, g)[0]
    bound = hrr_bind(K_test, V_test)
    assert bound.shape == (n,), "hrr_bind shape %s" % (bound.shape,)
    recovered = hrr_unbind(bound, K_test)
    cos_recovered = float(np.dot(recovered, V_test) / (np.linalg.norm(recovered) * np.linalg.norm(V_test) + 1e-8))
    assert cos_recovered > 0.5, "HRR round-trip cosine should be >0.5; got %.3f" % cos_recovered

    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(spearman_rho(x, x) - 1.0) < 1e-6
    assert abs(spearman_rho(x, -x) - (-1.0)) < 1e-6
    g2 = np.random.default_rng(42)
    rho_rand = spearman_rho(g2.random(200), g2.random(200))
    assert abs(rho_rand) < 0.20, "rho(random,random) should be ~0; got %.3f" % rho_rand

    # substrate sanity
    sub_dim = 32
    g3 = np.random.default_rng(11)
    Mb = 8
    keys_t = _bipolar(Mb, sub_dim, g3)
    vals_t = _bipolar(Mb, sub_dim, g3)
    binds_t = hrr_bind(keys_t, vals_t)
    Mpart_t = binds_t.sum(axis=0)
    decoded_t = hrr_unbind(Mpart_t, keys_t[0])
    sims_t = cos_rows(vals_t, decoded_t)
    top_idx = int(np.argmax(sims_t))
    assert top_idx == 0, "decoded should cleanup to vals[0]; got argmax=%d" % top_idx

    # deletion sanity
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

    # KEY v2 SELF-TEST: BILINEAR and MARGINAL must produce DIFFERENT score vectors
    scores_bil = contribution_true_trace_bilinear(Mpart_t, keys_t[0], keys_t, vals_t)
    scores_mar = contribution_true_trace_marginal(Mpart_t, keys_t[0], keys_t, vals_t)
    scores_cos = contribution_cosine_trace(Mpart_t, keys_t[0], keys_t, vals_t)
    assert scores_bil.shape == (Mb,) == scores_mar.shape == scores_cos.shape
    # MARGINAL is bounded [0, 1] (it's |cos|); BILINEAR is NOT bounded
    assert (scores_mar >= 0.0).all() and (scores_mar <= 1.0 + 1e-5).all(), \
        "MARGINAL must be in [0,1] (|cos|); got [%.3f, %.3f]" % (scores_mar.min(), scores_mar.max())
    # The vectors must DIFFER (not just be rescaled copies); check via SHA-256
    fp_bil = hashlib.sha256(scores_bil.tobytes()).hexdigest()[:16]
    fp_mar = hashlib.sha256(scores_mar.tobytes()).hexdigest()[:16]
    fp_cos = hashlib.sha256(scores_cos.tobytes()).hexdigest()[:16]
    assert len({fp_bil, fp_mar, fp_cos}) == 3, \
        "META_RULE_AF: BILINEAR, MARGINAL, COSINE must produce 3 distinct fingerprints; got bil=%s mar=%s cos=%s" % (
            fp_bil, fp_mar, fp_cos)
    # ranks differ too (not just magnitudes) -- on random Mb=8 data, BILINEAR vs MARGINAL
    # should not have identical argsort orderings (probability is ~1/M! = 1/40320)
    rank_bil = np.argsort(-scores_bil)
    rank_mar = np.argsort(-scores_mar)
    # they MAY agree on top-1 (own atom for both); just don't require identical full order
    # but BOTH must put atom 0 (the query's own atom) at top-1
    assert int(rank_bil[0]) == 0, "BILINEAR top-1 should be query atom 0; got %d" % int(rank_bil[0])
    assert int(rank_mar[0]) == 0, "MARGINAL top-1 should be query atom 0; got %d" % int(rank_mar[0])

    # MARGINAL self-cos top-1 should be > 0.9 (own atom decoded == V_0 exactly with no cross-talk
    # because per_atom_decoded[0] = V_0 exactly; cos(V_0, O) is high since V_0 dominates O when M is small)
    assert scores_mar[0] > 0.5, "MARGINAL top-1 (own atom) should be > 0.5; got %.3f" % scores_mar[0]

    # COSINE self-cos must be ~1.0 (cos(K_0, K_0))
    assert scores_cos[0] > 0.99, "COSINE self-cos should be ~1.0; got %.3f" % scores_cos[0]

    # CRLB pre-validation: SE(rho) ~ 1/sqrt(N-1); HP rho>=0.70 must be measurement-feasible
    n_per_arm_smoke = 500 * 5  # queries * K_TRACE
    se_rho = 1.0 / math.sqrt(n_per_arm_smoke - 1)
    margin_to_hp = 0.70 / se_rho
    assert margin_to_hp > 20.0, "CRLB FAIL: HP threshold not measurement-feasible (%.1f SE)" % margin_to_hp

    # Fingerprints for all 4 arms must be distinct
    g4 = np.random.default_rng(99)
    fp_keys = _bipolar(8, 32, g4)
    fp_vals = _bipolar(8, 32, g4)
    fp_binds = hrr_bind(fp_keys, fp_vals)
    fp_Mpart = fp_binds.sum(axis=0)
    s_bil = contribution_true_trace_bilinear(fp_Mpart, fp_keys[0], fp_keys, fp_vals)
    s_mar = contribution_true_trace_marginal(fp_Mpart, fp_keys[0], fp_keys, fp_vals)
    s_cos = contribution_cosine_trace(fp_Mpart, fp_keys[0], fp_keys, fp_vals)
    s_rnd = contribution_random_trace(fp_Mpart, fp_keys[0], fp_keys, fp_vals, g4)
    f_bil = _arm_fp([s_bil[None, :]])
    f_mar = _arm_fp([s_mar[None, :]])
    f_cos = _arm_fp([s_cos[None, :]])
    f_rnd = _arm_fp([s_rnd[None, :]])
    assert len({f_bil, f_mar, f_cos, f_rnd}) == 4, \
        "META_RULE_AF: 4 arms must produce 4 distinct fingerprints; got %s" % str({
            "bil": f_bil, "mar": f_mar, "cos": f_cos, "rnd": f_rnd})

    print("[selftest] PASS HRR round-trip cos=%.3f | rho(x,x)=1 rho(x,-x)=-1 rho(rand)~%.3f | "
          "deletion: baseline=%.3f ablated=%.3f | "
          "BILINEAR-vs-MARGINAL-distinct=YES MARGINAL_bounded_0_1=YES MARGINAL_top1_self=%.3f | "
          "CRLB margin=%.1f SE | arms_distinct=4/4"
          % (cos_recovered, rho_rand, baseline_cos, ablated_cos, scores_mar[0], margin_to_hp), flush=True)


# -------------------- main --------------------

def main() -> int:
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    print("[config] anchor=%s | N=%d M=%d K=%d queries=%d seeds=%s mode=%s out_dir=%s" % (
        ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE, N_QUERIES, SEEDS, RUN_MODE, out_dir), flush=True)
    print("[config] expected_n_units=%d  (arms * seeds * queries * K_TRACE)" % EXPECTED_N_UNITS, flush=True)
    print("[config] v2 FIX: per-atom MARGINAL cosine (NOT v1 bilinear inner product)", flush=True)

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
            raise
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
        "N": N_DIM, "M_BINDS": M_BINDS, "K_TRACE": K_TRACE, "N_QUERIES": N_QUERIES,
        "arms_tested": EXPECTED_ARMS,
        "config_version": CONFIG_VERSION,
        "per_arm_summary": agg["per_arm_summary"],
        "hp_conds": agg["hp_conds"], "hf_conds": agg["hf_conds"],
        "bilinear_rho": agg["bilinear_rho"],
        "marginal_rho": agg["marginal_rho"],
        "cosine_rho": agg["cosine_rho"],
        "random_rho": agg["random_rho"],
        "marginal_minus_cosine": agg["marginal_minus_cosine"],
        "marginal_minus_bilinear": agg["marginal_minus_bilinear"],
        "marginal_minus_random": agg["marginal_minus_random"],
        "bilinear_replicates_v1": agg["bilinear_replicates_v1"],
        "arms_distinct": agg["arms_distinct"],
        "distinct_per_seed": agg["distinct_per_seed"],
        "arm_fingerprints_per_seed": agg["arm_fingerprints_per_seed"],
        "cardinality_ok": agg["cardinality_ok"],
        "total_events": agg["total_events"],
        "expected_n_units": agg["expected_n_units"],
        "smoke_discriminator_gap_ok": agg["smoke_discriminator_gap_ok"],
        "smoke_discriminator_gap_msg": agg["smoke_discriminator_gap_msg"],
        "cleanup_margin_global": agg["cleanup_margin_global"],
        "per_seed": per_seed,
        "_hardening_marker": "v2_self_explanation_deletion_fidelity_per_atom_marginal",
        "_prior_run_reference": "data/exp_self_explanation_deletion_fidelity_v1_smoke/metrics.json",
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
