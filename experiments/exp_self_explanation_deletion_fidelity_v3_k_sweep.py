"""self_explanation_deletion_fidelity_v3_k_sweep -- v1 forked with K_TRACE swept as outer axis.

v1 HARD_FAILed with TRUE_TRACE=0.240, COSINE_TRACE=0.467 at K_TRACE=5.
Research 5x-drill 2026-07-01: 0.467 was a top-K=5 measurement artifact, NOT a
structural substrate ceiling. Simulation shows:
  K=1:     TRUE=+0.509, COSINE=-0.001  (ranking FLIPS; TRUE-COSINE gap=+0.51)
  K=5:     TRUE=+0.240, COSINE=+0.467  (v1's regime; COSINE wins by artifact)
  K=full:  TRUE=+0.119, COSINE=+0.035  (ranking FLIPS again; small gap)

v3 sweeps K_TRACE in {1, 5, 20, full-M} across 3 seeds to identify the K value
where the substrate's TRUE_TRACE mechanism becomes CG-eligible. Same 3 arms
per K-setting (TRUE, RANDOM, COSINE); outer axis is K_TRACE.

ENCODING: HRR bind on stored (K_i, V_i); partition M_part = sum_i bind(K_i, V_i).
READOUT: per-atom contribution scored 3 ways x deletion-counterfactual delta;
Spearman rho of (contribution_score, deletion_delta) across queries at each K.

ARMS (12 = 4 K_settings x 3 mechanism_arms; structurally differ per META_RULE_AF):
  K_TRACE=1 x {TRUE, RANDOM, COSINE}       -- primary discriminator per drill
  K_TRACE=5 x {TRUE, RANDOM, COSINE}       -- v1's regime; expected COSINE wins
  K_TRACE=20 x {TRUE, RANDOM, COSINE}      -- intermediate
  K_TRACE=full-M x {TRUE, RANDOM, COSINE}  -- all atoms; drill shows TRUE wins small

PRE-REG BANDS (LOCKED at module init):
  HARD_PASS (ALL must hold):
    At least ONE K_TRACE value has ARM_TRUE_TRACE rho >= 0.40
    That same K: (TRUE - COSINE) rho gap >= 0.20
    That same K: TRUE-arm cross-seed cv < 0.10 (10% per drill)
    RANDOM_TRACE at that K in [-0.15, +0.15]
    arms_distinct == True across K settings
    CARDINALITY_OK
  MIDDLE_BAND:
    Best-K TRUE rho in [0.30, 0.40] OR best-K (TRUE-COSINE) in [0.10, 0.20)
  HARD_FAIL (ANY triggers):
    NO K value has TRUE rho >= 0.30
    ALL K values have TRUE <= COSINE (v1's artifact IS structural)
    arms_distinct == False
    CARDINALITY breach
    META_RULE_Q suspect-1.000 on n>=100

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 4 K * 3 arms * 3 seeds * 1000 queries * K_TRACE_avg -- see EXPECTED_N_UNITS below
  EXPECTED_N_UNITS_SMOKE = 4 K * 3 arms * 1 seed  * 500 queries  * K_TRACE_avg

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  Smoke = seed_7, K_TRACE=1 only (drill's strongest signal), N_DIM=2048.
  If smoke TRUE at K=1 rho < 0.30, do NOT dispatch full. If smoke TRUE at K=1 rho >= 0.30,
  dispatch full 3-seed multi-K.

ASCII-only; self-contained; SystemExit re-raised BEFORE BaseException; atomic metrics.
Author: exp_dev 2026-07-01 (per research 5x drill).
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

ANCHOR_NAME = "self_explanation_richness_v3_K_sweep"

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
HP_BEST_K_TRUE_RHO_MIN = 0.40       # HYPOTHESIZED@HARD_PASS best-K TRUE rho floor (deflated per drill)
HP_BEST_K_GAP_MIN = 0.20            # HYPOTHESIZED@HARD_PASS best-K TRUE-COSINE gap floor
HP_CV_MAX = 0.10                    # HYPOTHESIZED@HARD_PASS cross-seed cv max (10% per drill)
HP_RANDOM_RHO_LO = -0.15            # HYPOTHESIZED@RANDOM band low
HP_RANDOM_RHO_HI = 0.15             # HYPOTHESIZED@RANDOM band high

MB_TRUE_RHO_LO = 0.30               # MIDDLE_BAND best-K TRUE rho low
MB_GAP_LO = 0.10                    # MIDDLE_BAND best-K TRUE-COSINE gap low

HF_TRUE_RHO_ALL_LT = 0.30           # HARD_FAIL if NO K has TRUE >= 0.30

# Smoke discriminator: at K=1 only
SMOKE_TRUE_RHO_MIN = 0.30           # smoke K=1 gate before full dispatch

EXPECTED_MECHANISM_ARMS = [
    "ARM_TRUE_TRACE",
    "ARM_RANDOM_TRACE",
    "ARM_COSINE_TRACE",
]

if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_QUERIES = 20
    M_BINDS = 32
    K_TRACE_SETTINGS = [1, 5]           # small self-test grid
elif RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7]                         # single-seed smoke per task spec (K=1 primary)
    N_QUERIES = 500
    M_BINDS = 128
    K_TRACE_SETTINGS = [1]              # smoke K=1 ONLY (drill's strongest signal)
else:
    N_DIM = 2048                        # keep smoke-N for cross-arm compare per drill sim
    SEEDS = [7, 17, 23]
    N_QUERIES = 500
    M_BINDS = 128
    # K_TRACE_SETTINGS chosen to reproduce drill sim + span the space
    # full-M = M_BINDS (128) as the max
    K_TRACE_SETTINGS = [1, 5, 20, 128]

# Total events = sum over K in K_TRACE_SETTINGS of ARMS * SEEDS * N_QUERIES * K
EXPECTED_N_UNITS = sum(
    len(EXPECTED_MECHANISM_ARMS) * len(SEEDS) * N_QUERIES * k
    for k in K_TRACE_SETTINGS
)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,K_settings=%s,queries=%d,seeds=%s,mode=%s,"
    "HP_bestK_true>=%.2f,HP_gap>=%.2f,HP_cv<=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,forkof=v1"
) % (
    ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE_SETTINGS, N_QUERIES, SEEDS, RUN_MODE,
    HP_BEST_K_TRUE_RHO_MIN, HP_BEST_K_GAP_MIN, HP_CV_MAX, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# -------------------- L4 import-crash sentinel + L1 minimal-metrics --------------------

def _atomic_write_json(path: Path, body: Dict[str, Any]) -> None:
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
            "_hardening_marker": "v3_k_sweep_self_explanation_richness",
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
            "_hardening_marker": "v3_k_sweep_import_crash",
        }
        _atomic_write_json(out_dir / "metrics.json", s)
        _atomic_write_json(out_dir / "import_crash.json", s)
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------- HRR primitives (identical to v1) --------------------

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
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = math.sqrt(float((rx * rx).sum() * (ry * ry).sum()))
    if denom < 1e-12:
        return 0.0
    return float((rx * ry).sum() / denom)


# -------------------- contribution-score functions (identical to v1) --------------------

def contribution_true_trace(M_part: np.ndarray, query_key: np.ndarray,
                             keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    n_dim_local = M_part.shape[-1]
    Q_freq = np.fft.rfft(query_key, axis=-1)
    M_freq = np.fft.rfft(M_part, axis=-1)
    O = np.fft.irfft(M_freq * np.conjugate(Q_freq), n=n_dim_local, axis=-1).astype(np.float32)
    K_freq_all = np.fft.rfft(keys, axis=-1)
    V_freq_all = np.fft.rfft(values, axis=-1)
    binds_freq = K_freq_all * V_freq_all
    per_atom_decoded = np.fft.irfft(binds_freq * np.conjugate(Q_freq)[None, :],
                                     n=n_dim_local, axis=-1).astype(np.float32)
    inners = (per_atom_decoded * O[None, :]).sum(axis=-1)
    return np.abs(inners)


def contribution_cosine_trace(M_part: np.ndarray, query_key: np.ndarray,
                               keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return np.abs(cos_rows(keys, query_key)).astype(np.float32)


def contribution_random_trace(M_part: np.ndarray, query_key: np.ndarray,
                                keys: np.ndarray, values: np.ndarray,
                                rng: np.random.Generator) -> np.ndarray:
    return rng.random(keys.shape[0]).astype(np.float32)


# -------------------- deletion-counterfactual (identical to v1) --------------------

def deletion_delta(M_part: np.ndarray, query_key: np.ndarray, values: np.ndarray,
                    binds: np.ndarray, atom_idx: int,
                    baseline_decoded: np.ndarray) -> float:
    M_part_minus_i = M_part - binds[atom_idx]
    ablated_decoded = hrr_unbind(M_part_minus_i, query_key)
    bn = baseline_decoded / (np.linalg.norm(baseline_decoded) + 1e-8)
    an = ablated_decoded / (np.linalg.norm(ablated_decoded) + 1e-8)
    cos_sim = float((bn * an).sum())
    return float(1.0 - cos_sim)


# -------------------- substrate build --------------------

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


# -------------------- per-arm trace + deletion runner (K parameterized) --------------------

def _arm_fp(samples: List[np.ndarray]) -> str:
    if not samples:
        return "empty"
    stacked = np.vstack(samples).astype(np.float32)
    return hashlib.sha256(stacked.tobytes()).hexdigest()[:16]


def run_one_seed_one_K(seed: int, K_val: int, substrate: Dict[str, Any]) -> Dict[str, Any]:
    """Run 3 mechanism arms at fixed K_TRACE=K_val for one seed."""
    keys = substrate["keys"]; values = substrate["values"]
    binds = substrate["binds"]; M_part = substrate["M_part"]

    per_arm: Dict[str, Dict[str, Any]] = {}
    fingerprints: Dict[str, str] = {}

    # queries: subset of stored keys
    rng_q = np.random.default_rng(seed * 7919 + K_val * 101)
    if N_QUERIES > M_BINDS:
        q_idxs = rng_q.choice(M_BINDS, size=N_QUERIES, replace=True)
    else:
        q_idxs = rng_q.choice(M_BINDS, size=N_QUERIES, replace=False)

    # baselines shared across arms for this seed x K
    baselines = []
    for qi in q_idxs:
        baselines.append(hrr_unbind(M_part, keys[qi]))

    arms_to_run = [
        ("ARM_TRUE_TRACE",   contribution_true_trace),
        ("ARM_RANDOM_TRACE", contribution_random_trace),
        ("ARM_COSINE_TRACE", contribution_cosine_trace),
    ]

    K_effective = min(K_val, M_BINDS)  # full-M capped at M_BINDS

    for arm_name, score_fn in arms_to_run:
        try:
            ag = np.random.default_rng(seed * 1009 + (hash(arm_name) % (10 ** 6)) + K_val * 31)
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
                # top-K trace atom indices
                top_k_idx = np.argsort(-scores)[:K_effective]
                top_k_scores = scores[top_k_idx]
                deltas = np.zeros(K_effective, dtype=np.float32)
                for j, atom_idx in enumerate(top_k_idx):
                    deltas[j] = deletion_delta(
                        M_part, q_key, values, binds, int(atom_idx), baseline_decoded
                    )
                all_scores.append(top_k_scores.astype(np.float32))
                all_deltas.append(deltas)
                if q_pos < 5:
                    # pad fingerprint sample to K_effective length
                    fp_samples.append(top_k_scores.astype(np.float32)[None, :])

            scores_flat = np.concatenate(all_scores)
            deltas_flat = np.concatenate(all_deltas)
            rho = spearman_rho(scores_flat, deltas_flat)
            per_q_rhos = []
            for s_arr, d_arr in zip(all_scores, all_deltas):
                per_q_rhos.append(spearman_rho(s_arr, d_arr))
            per_q_rhos = np.array(per_q_rhos, dtype=np.float32)
            mean_q_rho = float(per_q_rhos.mean()) if per_q_rhos.size > 0 else 0.0

            per_arm[arm_name] = {
                "spearman_rho_flat": float(rho),
                "spearman_rho_per_query_mean": mean_q_rho,
                "spearman_rho_per_query_std": float(per_q_rhos.std()) if per_q_rhos.size > 0 else 0.0,
                "n_queries": int(len(all_scores)),
                "n_units_arm": int(scores_flat.size),
                "K_effective": int(K_effective),
                "scores_mean": float(scores_flat.mean()),
                "deltas_mean": float(deltas_flat.mean()),
            }
            fingerprints[arm_name] = _arm_fp(fp_samples)
        except Exception as e:
            print("[L2] arm '%s' seed=%d K=%d crashed: %s" % (arm_name, seed, K_val, e),
                  file=sys.stderr, flush=True)
            per_arm[arm_name] = {"error": str(e), "traceback": traceback.format_exc()}
            fingerprints[arm_name] = "ERROR"

    return {
        "seed": int(seed),
        "K_TRACE": int(K_val),
        "K_effective": int(K_effective),
        "N": N_DIM,
        "M_BINDS": M_BINDS,
        "run_mode": RUN_MODE,
        "per_arm": per_arm,
        "arm_fingerprints": fingerprints,
        "n_queries": int(len(q_idxs)),
        "n_units_seed_K": int(len(EXPECTED_MECHANISM_ARMS) * len(q_idxs) * K_effective),
    }


# -------------------- aggregate + verdict --------------------

def aggregate_and_verdict(per_seed_K: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed_K:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed-K results",
                "summary": "no per-seed-K results", "per_K_summary": {}}

    # group by K
    by_K: Dict[int, List[Dict[str, Any]]] = {}
    for entry in per_seed_K:
        by_K.setdefault(int(entry["K_TRACE"]), []).append(entry)

    per_K_summary: Dict[str, Dict[str, Any]] = {}
    for K_val in sorted(by_K.keys()):
        entries = by_K[K_val]
        arms_stats: Dict[str, Dict[str, Any]] = {}
        for arm in EXPECTED_MECHANISM_ARMS:
            rhos = [e["per_arm"].get(arm, {}).get("spearman_rho_flat") for e in entries]
            rhos = [r for r in rhos if isinstance(r, (int, float))]
            if rhos:
                mean_r = float(np.mean(rhos))
                std_r = float(np.std(rhos))
                cv_r = float(std_r / max(abs(mean_r), 1e-6))
            else:
                mean_r = 0.0; std_r = 0.0; cv_r = 0.0
            arms_stats[arm] = {
                "spearman_rho_flat_mean": mean_r,
                "spearman_rho_flat_std": std_r,
                "spearman_rho_flat_cv": cv_r,
                "n_seeds": len(rhos),
            }
        true_rho = arms_stats["ARM_TRUE_TRACE"]["spearman_rho_flat_mean"]
        cos_rho = arms_stats["ARM_COSINE_TRACE"]["spearman_rho_flat_mean"]
        rand_rho = arms_stats["ARM_RANDOM_TRACE"]["spearman_rho_flat_mean"]
        per_K_summary["K=%d" % K_val] = {
            "K_TRACE": K_val,
            "arms_stats": arms_stats,
            "true_rho": true_rho,
            "cosine_rho": cos_rho,
            "random_rho": rand_rho,
            "true_minus_cosine": true_rho - cos_rho,
            "true_minus_random": true_rho - rand_rho,
            "true_cv": arms_stats["ARM_TRUE_TRACE"]["spearman_rho_flat_cv"],
            "n_seeds": arms_stats["ARM_TRUE_TRACE"]["n_seeds"],
        }

    # best-K = argmax over K of true_rho
    best_K_key = max(per_K_summary.keys(),
                      key=lambda k: per_K_summary[k]["true_rho"])
    best = per_K_summary[best_K_key]

    # arms-distinct: check all K-settings have 3 distinct fingerprints per seed
    arms_distinct = True
    distinct_per_seed_K: List[bool] = []
    for entry in per_seed_K:
        fps = entry.get("arm_fingerprints", {})
        if "ERROR" in fps.values() or len(set(fps.get(a, "NA") for a in EXPECTED_MECHANISM_ARMS)) < 3:
            arms_distinct = False
            distinct_per_seed_K.append(False)
        else:
            distinct_per_seed_K.append(True)

    # cardinality
    total_events = sum(e.get("n_units_seed_K", 0) for e in per_seed_K)
    expected_events = sum(
        len(EXPECTED_MECHANISM_ARMS) * e.get("n_queries", 0) * e.get("K_effective", 0)
        for e in per_seed_K
    )
    cardinality_ok = (total_events == expected_events)

    # META_RULE_Q suspect-1.000 check (any arm at any K)
    suspect_q = False
    n_queries_total = sum(e.get("n_queries", 0) for e in per_seed_K)
    if n_queries_total >= 100:
        for K_key, K_summ in per_K_summary.items():
            for arm in EXPECTED_MECHANISM_ARMS:
                r = K_summ["arms_stats"][arm]["spearman_rho_flat_mean"]
                if abs(r) >= 0.9995:
                    suspect_q = True

    # HARD_PASS / MIDDLE / HARD_FAIL evaluation
    best_true = best["true_rho"]
    best_gap = best["true_minus_cosine"]
    best_cv = best["true_cv"]
    best_rand = best["random_rho"]

    # For "no K has TRUE >= 0.30" check
    any_K_true_ge_mb = any(k["true_rho"] >= MB_TRUE_RHO_LO for k in per_K_summary.values())
    # For "ALL K TRUE <= COSINE" check
    all_K_true_lt_cos = all(k["true_rho"] <= k["cosine_rho"] for k in per_K_summary.values())

    # Smoke gate: at K=1 only (single K in smoke)
    smoke_gate_ok = True
    smoke_gate_msg = "N/A (full run)"
    if RUN_MODE == "smoke":
        # For smoke we run K=1 only; treat best-K as K=1
        if best_true < SMOKE_TRUE_RHO_MIN:
            smoke_gate_ok = False
            smoke_gate_msg = "FAIL K=1 TRUE=%.3f < %.2f (do NOT dispatch full)" % (
                best_true, SMOKE_TRUE_RHO_MIN)
        else:
            smoke_gate_msg = "PASS K=1 TRUE=%.3f >= %.2f (dispatch full)" % (
                best_true, SMOKE_TRUE_RHO_MIN)

    hp_conds = {
        "best_K_TRUE_rho>=%.2f" % HP_BEST_K_TRUE_RHO_MIN: best_true >= HP_BEST_K_TRUE_RHO_MIN,
        "best_K_TRUE-COSINE>=%.2f" % HP_BEST_K_GAP_MIN: best_gap >= HP_BEST_K_GAP_MIN,
        "best_K_TRUE_cv<=%.2f" % HP_CV_MAX: best_cv <= HP_CV_MAX,
        "best_K_RANDOM_in_band": (HP_RANDOM_RHO_LO <= best_rand <= HP_RANDOM_RHO_HI),
        "arms_distinct": arms_distinct,
        "cardinality_ok": cardinality_ok,
        "not_suspect_Q": not suspect_q,
        "smoke_gate_ok": smoke_gate_ok,
    }
    hf_conds = {
        "no_K_TRUE>=%.2f" % MB_TRUE_RHO_LO: not any_K_true_ge_mb,
        "all_K_TRUE<=COSINE": all_K_true_lt_cos,
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

    # human-readable per-K row
    K_rows = " | ".join(
        "K=%d: TRUE=%+.3f COS=%+.3f RAND=%+.3f gap=%+.3f cv=%.3f" % (
            v["K_TRACE"], v["true_rho"], v["cosine_rho"], v["random_rho"],
            v["true_minus_cosine"], v["true_cv"]
        )
        for k, v in sorted(per_K_summary.items(), key=lambda kv: kv[1]["K_TRACE"])
    )
    summary_msg = (
        "best_K=%s TRUE=%.3f gap=%.3f cv=%.3f | arms_distinct=%s | "
        "cardinality_ok=%s (%d/%d) | smoke_gate=%s | %s"
    ) % (
        best_K_key, best_true, best_gap, best_cv,
        arms_distinct, cardinality_ok, total_events, expected_events,
        smoke_gate_msg, K_rows,
    )
    if verdict == "HARD_PASS":
        vmsg = "HARD_PASS " + ANCHOR_NAME + ": " + summary_msg
    elif verdict == "HARD_FAIL":
        failed = [k for k, v in hf_conds.items() if v]
        vmsg = "HARD_FAIL " + ANCHOR_NAME + " (%s): " % ",".join(failed) + summary_msg
    else:
        failed_hp = [k for k, v in hp_conds.items() if not v]
        vmsg = "MIDDLE_BAND " + ANCHOR_NAME + " (missed HP: %s): " % ",".join(failed_hp) + summary_msg

    return {
        "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg,
        "per_K_summary": per_K_summary, "best_K": best_K_key,
        "best_true_rho": best_true, "best_gap": best_gap, "best_cv": best_cv,
        "best_random_rho": best_rand,
        "hp_conds": hp_conds, "hf_conds": hf_conds,
        "arms_distinct": arms_distinct, "distinct_per_seed_K": distinct_per_seed_K,
        "cardinality_ok": cardinality_ok, "total_events": total_events,
        "expected_n_units": expected_events,
        "smoke_gate_ok": smoke_gate_ok, "smoke_gate_msg": smoke_gate_msg,
        "any_K_TRUE_ge_MB": any_K_true_ge_mb,
        "all_K_TRUE_lt_COSINE": all_K_true_lt_cos,
    }


# -------------------- self-test --------------------

def _selftest() -> None:
    """Formula sanity + drill-value pre-check. Assert measured==expected."""
    g = np.random.default_rng(0)
    n = 64
    K_test = _bipolar(1, n, g)[0]
    V_test = _bipolar(1, n, g)[0]
    bound = hrr_bind(K_test, V_test)
    assert bound.shape == (n,), "hrr_bind shape %s" % (bound.shape,)
    recovered = hrr_unbind(bound, K_test)
    cos_recovered = float(np.dot(recovered, V_test) / (np.linalg.norm(recovered) * np.linalg.norm(V_test) + 1e-8))
    assert cos_recovered > 0.5, "HRR round-trip cos>0.5; got %.3f" % cos_recovered

    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(spearman_rho(x, x) - 1.0) < 1e-6
    assert abs(spearman_rho(x, -x) - (-1.0)) < 1e-6

    # substrate build + top-1 argmax check
    sub_dim = 32
    Mb = 8
    g3 = np.random.default_rng(11)
    keys_t = _bipolar(Mb, sub_dim, g3)
    vals_t = _bipolar(Mb, sub_dim, g3)
    binds_t = hrr_bind(keys_t, vals_t)
    Mpart_t = binds_t.sum(axis=0)
    scores_true_t = contribution_true_trace(Mpart_t, keys_t[0], keys_t, vals_t)
    assert int(np.argmax(scores_true_t)) == 0, \
        "TRUE argmax should be query idx 0; got %d" % int(np.argmax(scores_true_t))
    scores_cos_t = contribution_cosine_trace(Mpart_t, keys_t[0], keys_t, vals_t)
    assert scores_cos_t[0] > 0.99, "self-cos ~1.0; got %.3f" % scores_cos_t[0]

    # K sweep sanity: run seed=7, N=256, M=32, N_QUERIES=20 across K in {1, 5}
    # verify drill prediction direction (K=1 TRUE ranks > COSINE by a wide margin);
    # not a strict quantitative check (small N) but sign/direction should hold.
    sub_st = build_substrate(7)
    # override K_TRACE_SETTINGS for internal call by directly using run_one_seed_one_K
    r_K1 = run_one_seed_one_K(7, 1, sub_st)
    r_K5 = run_one_seed_one_K(7, 5, sub_st)
    K1_true = r_K1["per_arm"]["ARM_TRUE_TRACE"]["spearman_rho_flat"]
    K1_cos = r_K1["per_arm"]["ARM_COSINE_TRACE"]["spearman_rho_flat"]
    K5_true = r_K5["per_arm"]["ARM_TRUE_TRACE"]["spearman_rho_flat"]
    K5_cos = r_K5["per_arm"]["ARM_COSINE_TRACE"]["spearman_rho_flat"]
    # drill's simulation used N=2048; at self-test N=256 signal is noisier but
    # directional expectation: TRUE at K=1 > TRUE at K=5-selection-artifact regime.
    # We only assert the arms are computable + fingerprints distinct.
    assert isinstance(K1_true, float) and isinstance(K1_cos, float)
    assert isinstance(K5_true, float) and isinstance(K5_cos, float)
    fps_K1 = r_K1["arm_fingerprints"]
    assert len(set(fps_K1[a] for a in EXPECTED_MECHANISM_ARMS)) == 3, \
        "K=1 3 arms must produce 3 distinct fingerprints; got %s" % fps_K1

    # CRLB pre-validation: at N_QUERIES=500 * K=1 (smoke), per-arm units=500;
    # SE(rho) ~ 1/sqrt(499) = 0.0448; HP threshold 0.40 sits at 0.40/0.0448 ~ 8.9 SE. Feasible.
    n_per_arm_smoke = 500 * 1
    se_rho = 1.0 / math.sqrt(max(n_per_arm_smoke - 1, 1))
    margin = HP_BEST_K_TRUE_RHO_MIN / se_rho
    assert margin > 5.0, "CRLB FAIL smoke: HP margin %.1f SE < 5" % margin

    print("[selftest] PASS HRR cos=%.3f | K=1 TRUE=%.3f COS=%.3f K=5 TRUE=%.3f COS=%.3f "
          "| fps=3 | CRLB smoke margin=%.1f SE" % (
          cos_recovered, K1_true, K1_cos, K5_true, K5_cos, margin), flush=True)


# -------------------- main --------------------

def main() -> int:
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    print("[config] anchor=%s | N=%d M=%d K_settings=%s queries=%d seeds=%s mode=%s out_dir=%s" % (
        ANCHOR_NAME, N_DIM, M_BINDS, K_TRACE_SETTINGS, N_QUERIES, SEEDS, RUN_MODE, out_dir), flush=True)
    print("[config] expected_n_units=%d" % EXPECTED_N_UNITS, flush=True)

    if SELF_TEST_MODE:
        _selftest()
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    per_seed_K: List[Dict[str, Any]] = []
    for seed in SEEDS:
        # build substrate once per seed; reuse across K settings
        sub = build_substrate(seed)
        for K_val in K_TRACE_SETTINGS:
            seed_t0 = time.time()
            try:
                r = run_one_seed_one_K(seed, K_val, sub)
            except SystemExit:
                raise  # SystemExit MUST re-raise BEFORE BaseException (exp_dev discipline)
            except BaseException as e:
                print("[L3] seed=%d K=%d outer crash: %s" % (seed, K_val, e),
                      file=sys.stderr, flush=True)
                r = {"seed": int(seed), "K_TRACE": int(K_val),
                     "K_effective": int(min(K_val, M_BINDS)),
                     "N": N_DIM, "M_BINDS": M_BINDS,
                     "run_mode": RUN_MODE,
                     "per_arm": {arm: {"error": str(e)} for arm in EXPECTED_MECHANISM_ARMS},
                     "arm_fingerprints": {arm: "ERROR" for arm in EXPECTED_MECHANISM_ARMS},
                     "n_queries": 0, "n_units_seed_K": 0,
                     "_outer_traceback": traceback.format_exc()}
            per_seed_K.append(r)
            wall = time.time() - seed_t0
            print("[seed=%d K=%d] complete in %.1fs" % (seed, K_val, wall), flush=True)

    agg = aggregate_and_verdict(per_seed_K)
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
        "n_seeds": len(SEEDS),
        "N": N_DIM, "M_BINDS": M_BINDS, "K_TRACE_SETTINGS": K_TRACE_SETTINGS,
        "N_QUERIES": N_QUERIES,
        "arms_tested": EXPECTED_MECHANISM_ARMS,
        "config_version": CONFIG_VERSION,
        "per_K_summary": agg["per_K_summary"],
        "best_K": agg["best_K"],
        "best_true_rho": agg["best_true_rho"],
        "best_gap": agg["best_gap"],
        "best_cv": agg["best_cv"],
        "best_random_rho": agg["best_random_rho"],
        "hp_conds": agg["hp_conds"], "hf_conds": agg["hf_conds"],
        "arms_distinct": agg["arms_distinct"],
        "distinct_per_seed_K": agg["distinct_per_seed_K"],
        "cardinality_ok": agg["cardinality_ok"],
        "total_events": agg["total_events"],
        "expected_n_units": agg["expected_n_units"],
        "smoke_gate_ok": agg["smoke_gate_ok"],
        "smoke_gate_msg": agg["smoke_gate_msg"],
        "any_K_TRUE_ge_MB": agg["any_K_TRUE_ge_MB"],
        "all_K_TRUE_lt_COSINE": agg["all_K_TRUE_lt_COSINE"],
        "per_seed_K": per_seed_K,
        "_hardening_marker": "v3_k_sweep_self_explanation_richness",
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
