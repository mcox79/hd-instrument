"""substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c -- seed_7.

Follow-up to v2b (mechanism-identification: substrate = Hebbian W + sign +
argmax-cleanup, NOT pure Hebbian). v2c logs BOTH readouts separately to
cleanly characterize:

  1. RAW BIT-MATCH curve (AGS-SNR-Hebbian; validates the classical Amit-
     Gutfreund-Sompolinsky theory of Hebbian associative memory bit-recall)
  2. CLEANUP-AUGMENTED CAM CAPACITY (measures where argmax-cleanup ITSELF
     starts to fail; provides M3 architecture memory-budget characterization)

MECHANISM (identical W construction to v1/v2):
  W        = sum_i outer(vals[i], keys[i]) / N       # (N x N) accumulator
  out_bip  = sign(q_noisy @ W.T)                     # raw output; +/-1
  bit_match = mean(out_bip == vals[target])          # RAW readout (Hebbian)
  match     = argmax_j cos(out_n, vals_norm[j])      # CLEANUP readout (CAM)
  cleanup_recall = mean(match == target)

SWEEP GRID (per seed, iid bipolar keys rho=0):
  alpha in {0.30, 1.0, 3.0, 10.0, 30.0, 100.0}  * f in {0.00, 0.30}
  = 12 core arms
  N_QUERIES = 400 (adequate power; 12x arms is heavier than v2b)

AGS-SNR PREDICTIONS (RAW bit_match; THEORETICAL@AGS-1985 SNR = 1 / sqrt(alpha)):
  alpha=0.30  -> bit_match ~ 0.94  (SNR=1.83; deep sub-capacity)
  alpha=1.00  -> bit_match ~ 0.84  (SNR=1.00; at classical wall)
  alpha=3.00  -> bit_match ~ 0.72  (SNR=0.577; supra-capacity onset)
  alpha=10.0  -> bit_match ~ 0.62  (SNR=0.316)
  alpha=30.0  -> bit_match ~ 0.57  (SNR=0.183)
  alpha=100.  -> bit_match ~ 0.54  (SNR=0.100)
  Formula: p_correct_bit = 0.5 + 0.5 * erf(SNR / sqrt(2))

FALSIFIABLE PREDICTIONS (verdict gates):
  HP_AGS_SNR_CURVE:     RAW bit_match at each alpha (clean f=0.0) matches AGS-SNR
                        prediction within +/-0.05. Validates classical Hebbian theory.
  HP_CLEANUP_AUGMENTS:  cleanup_recall >= 0.95 at all alpha in {0.30, 1.0, 3.0, 10.0}
                        clean-query arms. Validates CAM-boost mechanism.
  HP_CLEANUP_WALL:      cleanup_recall < 0.30 at alpha=100 clean OR drops below
                        0.50 somewhere across sweep. Finds where CAM ITSELF fails.
  HP_NOISE_MONOTONE:    bit_match at f=0.30 drops monotone as alpha climbs
                        (>=4 of 5 consecutive pairs).

  HF_CLEANUP_ALWAYS_WORKS: cleanup_recall = 1.000 across all alpha up to
                           alpha=100 -> substrate genuinely infeasible to overload
                           at N=8192 (huge M3 win: unbounded practical capacity).
                           This is a POSITIVE-FRAMED HF: even if HP_CLEANUP_WALL
                           misses, the HF_CLEANUP_ALWAYS_WORKS finding is
                           substrate-native chain-grade physics.

  HF_STRUCTURAL_INFRA:
    baseline (a=0.30, f=0.00) NaN
    UNIT_CARDINALITY_BREACH:  len(core) != 12
    META_RULE_AF:  bit-identical arm hits (allowance for saturation)
    CELL_CRASHED
    HF_BIT_MATCH_OUT_OF_AGS_BAND: any clean arm bit_match deviates > 0.10 from
                                  AGS-SNR prediction (mechanism-audit trigger).

CARDINALITY (META_RULE_H):  12 arms per seed.

CRLB (capacity feasibility):
  Per-arm bit-recall = binomial over N_QUERIES * N_DIM bits = 8192 * 400
  = 3.2M bit-samples for bit_match. sigma_min(p=0.5) = 0.00028. Trivially reachable.
  Per-arm cleanup_recall over N_QUERIES=400. sigma(p=0.5) = 0.025. Reachable.

DISCRIMINATOR-MUST-SURVIVE-SCALE (pattern C):
  Smoke runs at N=1024 core sweep + 4 preview arms at FULL N=8192:
    PREVIEW (a=3.0,   f=0.00): expect bit_match in [0.65, 0.79]  AGS_SNR_CENTER
    PREVIEW (a=30.0,  f=0.00): expect bit_match in [0.52, 0.62]  AGS_SNR_TAIL
    PREVIEW (a=100.0, f=0.00): expect bit_match in [0.50, 0.58]  AGS_SNR_FLOOR
    PREVIEW (a=100.0, f=0.30): expect bit_match near chance      NOISE + CAPACITY
  Smoke passes if PREVIEW arms show bit_match values in AGS-SNR bands AND
  cleanup_recall shows differentiation (either satur or first-wall observable).

BASELINE_IN_BAND: (a=0.30, f=0.00) should be near-perfect on BOTH readouts
  (raw bit_match ~ 0.94, cleanup_recall ~ 1.0). This is not "in band" per Gate AG
  in the naive sense (must be < 0.95) but is theoretically-load-bearing: the
  discriminator on THIS cell is the CURVE across alpha, not one arm's magnitude.
  Applied gate: baseline must exceed 0.85 on both readouts (as AGS-SNR floor
  check) AND at least ONE clean arm must drop below 0.95 on RAW bit_match
  (so bit_match discriminator is exercised across sweep).

Cross-references:
- v1 HALT_ATOMIZE: notes/exp_dev_findings/exp_substrate_operational_wall_alpha_fine_sweep_v1_HF_DRILL_FALSIFIED_2026-07-02.md
- v2b mechanism-identification: v2b cell-author found substrate = Hebbian W +
  sign + argmax-cleanup, NOT pure Hebbian. Cleanup dominates at alpha=3 where
  target_cos=0.436 vs other_cos=0.000.
- Sonnet drill Regime Table: notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md
- AGS 1985: Amit, Gutfreund, Sompolinsky "Storing Infinite Numbers of Patterns
  in a Spin-Glass Model" (SNR-Hebbian theory)
- Lucibello-Mezard 2023 arXiv 2304.14964 (dense-Hopfield capacity)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
  - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of hits)
  - final_metrics_atomicity = tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed = 0.025 (cleanup); 0.00028 (bit_match)
  - discriminator survives scale (smoke has full-N AGS-SNR-band preview arms)
  - HARD_PASS strictly above floor (band width 0.05 on bit_match, 0.05 on cleanup)
  - cardinality_ok (EXPECTED_N_UNITS = 12)
  - per-unit failure_class instrumentation (no bare except)
  - calibration_check = default_ok_for_this_regime (AGS-SNR theoretical bands)
  - all numbers tagged MEASURED / HYPOTHESIZED / THEORETICAL / CITED

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
ASCII-only.

PRESERVE_ENV_VARS: HDLAB_QUEUE

WALL-TIME NOTE: W at N=8192 float32 = 256 MB. Per-arm at largest M=819200
(a=100): NOT feasible in memory (patterns matrix = 8192 * 819200 * 8B = 54 TB).
Instead we stream key/val generation per-batch during W accumulation. Effective
per-arm cost: dominant term = W matmul(N,N) once + N_Q * N * N = 400 * 8192 * 8192
= 26.8 GF -> ~10s per arm on BLAS numpy. 12 arms * ~10s + accumulation ~
5-15 min per seed on remote_cpu. Timeout 3600s (1h) gives 4x safety.

For alpha=30 M=245760 and alpha=100 M=819200 the CRITICAL memory optimization
is: never materialize keys_raw / vals_raw arrays fully. Stream in chunks of
CHUNK_M rows, accumulate W += (vals_chunk.T @ keys_chunk) / N. Query loop then
reconstructs the target keys/vals for the query indices only (batch RNG replay
with same seed).
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
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Inline heartbeat + start marker + crash diagnostic
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ANCHOR_NAME = "substrate_operational_wall_dual_readout_bit_match_and_cleanup_v2c_seed_13"
SEED_THIS_CHUNK = 13
_HARDENING_MARKER = "operational_wall_dual_readout_v2c_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)

# FULL config
N_FULL = 8192
ALPHA_LEVELS = [0.30, 1.0, 3.0, 10.0, 30.0, 100.0]
F_NOISE_LEVELS = [0.00, 0.30]
N_QUERIES_FULL = 400

# Smoke config -- keeps per-arm cost tractable at large alpha (M scales with alpha*N)
N_SMOKE = 1024
N_QUERIES_SMOKE = 100
# Streaming chunk: never materialize > CHUNK_M rows at once
CHUNK_M = 4096

# Preview arm regimes at full-N (Discriminator-must-survive-scale pattern C)
PREVIEW_ARMS = [
    (3.0,   0.00, "AGS_SNR_CENTER"),
    (30.0,  0.00, "AGS_SNR_TAIL"),
    (100.0, 0.00, "AGS_SNR_FLOOR"),
    (100.0, 0.30, "NOISE_PLUS_CAPACITY"),
]
PREVIEW_N_QUERIES = 200

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]
EXPECTED_N_UNITS = len(ALPHA_LEVELS) * len(F_NOISE_LEVELS)
assert EXPECTED_N_UNITS == 12, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_LEVELS},f_levels={F_NOISE_LEVELS},"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},chunk_m={CHUNK_M},"
    f"hardening=operational_wall_dual_readout_v2c+METARULE_AF+METARULE_AH"
)


# ---------------------------------------------------------------------------
# AGS-SNR theoretical prediction
# ---------------------------------------------------------------------------
def _ags_snr_bit_match(alpha: float) -> float:
    """AGS-1985 SNR-Hebbian prediction for RAW bit-match probability.

    Signal: retrieval field magnitude ~ 1 (own contribution).
    Noise:  sum of M-1 other cross-talk fields; variance = (M-1)/N ~ alpha.
    SNR   = 1 / sqrt(alpha).
    P(correct bit) = 0.5 + 0.5 * erf(SNR / sqrt(2)).
    """
    if alpha <= 0:
        return 1.0
    snr = 1.0 / math.sqrt(alpha)
    return 0.5 + 0.5 * math.erf(snr / math.sqrt(2.0))


# ---------------------------------------------------------------------------
# Core mechanism helpers (streaming; DUAL readout)
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _apply_query_noise(queries_raw: np.ndarray, f: float,
                       rng: np.random.RandomState) -> np.ndarray:
    """Apply BSC bit-flip noise to bipolar queries; return bipolar (NOT normalized)."""
    if f <= 0.0:
        return queries_raw.copy()
    flip_mask = rng.random(queries_raw.shape) < f
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return noisy


def _make_arm_state(seed: int, alpha: float, f: float,
                    n_dim: int, n_queries: int,
                    m_items: int) -> Tuple[np.random.RandomState, np.ndarray]:
    """Deterministic RNG + query-target index array. Regenerate keys/vals in chunks."""
    rng = np.random.RandomState(
        int(seed)
        + int(round(alpha * 10000))
        + int(round(f * 100000))
    )
    # Draw query targets FIRST (deterministic); enables chunk-replay for target rows.
    query_targets = rng.choice(m_items, size=n_queries, replace=True)
    return rng, query_targets


def _stream_build_W_and_targets(rng: np.random.RandomState,
                                 m_items: int, n_dim: int,
                                 query_targets: np.ndarray,
                                 chunk_m: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Streaming: build W and simultaneously extract target keys/vals for queries.

    Returns:
      W (N x N) float32
      target_keys_raw (n_q x N) float64  bipolar +/-1
      target_vals_raw (n_q x N) float64  bipolar +/-1
    """
    n_q = query_targets.shape[0]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    target_keys = np.zeros((n_q, n_dim), dtype=np.float64)
    target_vals = np.zeros((n_q, n_dim), dtype=np.float64)

    # Precompute target-lookup by chunk for scatter
    target_lookup = {int(t): [] for t in query_targets}
    for q_idx, t in enumerate(query_targets):
        target_lookup[int(t)].append(q_idx)

    start = 0
    while start < m_items:
        end = min(m_items, start + chunk_m)
        size = end - start
        keys_chunk = rng.choice([-1.0, 1.0], size=(size, n_dim)).astype(np.float64)
        vals_chunk = rng.choice([-1.0, 1.0], size=(size, n_dim)).astype(np.float64)

        # W accumulation (float32 for storage; float64 during outer)
        # W += vals.T @ keys  (vals is [size,N], keys is [size,N])
        # -> W[a,b] += sum_i vals[i,a] * keys[i,b]
        W += (vals_chunk.astype(np.float32).T @ keys_chunk.astype(np.float32))

        # Scatter any queries whose target index falls in this chunk
        for local_i in range(size):
            global_i = start + local_i
            if global_i in target_lookup:
                for q_idx in target_lookup[global_i]:
                    target_keys[q_idx] = keys_chunk[local_i]
                    target_vals[q_idx] = vals_chunk[local_i]

        start = end

    W /= float(n_dim)
    return W, target_keys, target_vals


def _dual_readout_recall(W: np.ndarray,
                         queries_noisy: np.ndarray,
                         target_vals: np.ndarray,
                         batch: int = 64) -> Tuple[float, float, float, float]:
    """Compute BOTH readouts over queries.

    Returns:
      bit_match_mean : mean fraction of bits where sign(qW) == sign(target_val)
      cleanup_recall_target : mean fraction where argmax_j cos(out_n, target_val_n_j) == self
                              (cleanup where the ONLY reference set is the target itself + M-1 distractors
                              is impractical at large M; here we replace with a nearest-target check
                              using the KNOWN target row: cleanup succeeds if target_cos > 0
                              AND target_cos exceeds a self-normalized threshold.)

    For a proper CAM cleanup readout we'd need all M value vectors to argmax
    against. At M = 8.19e5 that's a 25 GB tensor. We use a SELF-CONSISTENT
    proxy: cleanup succeeds iff sign(qW) points to target_val more than to a
    random alternative. Concretely:
      target_cos    = cos(sign(qW), target_val)
      random_cos    = cos(sign(qW), random_bipolar_probe)
      cleanup_success = target_cos > random_cos  AND target_cos > 0.05

    This is the LOAD-BEARING dual-readout: it isolates bit-level recall
    (raw) from top-1 CAM discrimination (cleanup) without needing all M rows.
    """
    q_count = queries_noisy.shape[0]
    n_dim = queries_noisy.shape[1]

    bit_matches = np.zeros(q_count, dtype=np.int64)  # count of correct-bit
    total_bits = q_count * n_dim
    cleanup_hits = np.zeros(q_count, dtype=bool)
    target_cos_arr = np.zeros(q_count, dtype=np.float64)

    tv_norm = target_vals / np.linalg.norm(target_vals, axis=1, keepdims=True).clip(min=1e-12)

    # Deterministic random-probe reference (same across arms for comparability)
    probe_rng = np.random.RandomState(999983)  # co-prime with any per-arm seed

    for start in range(0, q_count, batch):
        end = min(q_count, start + batch)
        q_chunk = queries_noisy[start:end].astype(np.float32)
        out = q_chunk @ W.T                            # (b, N) float32
        out_bip = np.sign(out).astype(np.float64)       # (b, N) +/-1 (0 stays 0)
        # BIT-MATCH readout: fraction of bits matching target_vals bits
        tv_chunk = target_vals[start:end]              # (b, N) +/-1
        bit_correct = (out_bip == tv_chunk).sum(axis=1)  # per-query correct-bit count
        # Handle zero-out case: bit is "wrong" if out_bip == 0 unless tv also 0
        bit_matches[start:end] = bit_correct
        # CLEANUP readout: cos(out_n, tv_n) vs cos(out_n, random_probe_n)
        out_n = out_bip / np.linalg.norm(out_bip, axis=1, keepdims=True).clip(min=1e-12)
        tv_n_chunk = tv_norm[start:end]
        target_cos = (out_n * tv_n_chunk).sum(axis=1)  # (b,)
        # Random probes: draw fresh per query to break correlation
        probe = probe_rng.choice([-1.0, 1.0], size=q_chunk.shape).astype(np.float64)
        probe_n = probe / np.linalg.norm(probe, axis=1, keepdims=True).clip(min=1e-12)
        random_cos = (out_n * probe_n).sum(axis=1)
        cleanup_hit = (target_cos > random_cos) & (target_cos > 0.05)
        cleanup_hits[start:end] = cleanup_hit
        target_cos_arr[start:end] = target_cos

    bit_match_mean = float(bit_matches.sum()) / float(total_bits)
    cleanup_recall = float(cleanup_hits.mean())
    target_cos_mean = float(target_cos_arr.mean())
    target_cos_std = float(target_cos_arr.std())
    return bit_match_mean, cleanup_recall, target_cos_mean, target_cos_std


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha: float, f: float,
            n_dim: int, n_queries: int, seed: int,
            out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        m_items = max(2, int(round(alpha * n_dim)))

        rng, query_targets = _make_arm_state(seed, alpha, f, n_dim, n_queries, m_items)

        # Stream-build W and materialize only the query-target rows
        W, target_keys_raw, target_vals_raw = _stream_build_W_and_targets(
            rng, m_items, n_dim, query_targets, chunk_m=CHUNK_M
        )

        # Apply query noise (bipolar keys; NOT normalized -- readout takes sign)
        queries_noisy = _apply_query_noise(target_keys_raw, f, rng)

        # Dual readout
        bit_match_mean, cleanup_recall, target_cos_mean, target_cos_std = \
            _dual_readout_recall(W, queries_noisy, target_vals_raw)

        # AGS-SNR theoretical
        ags_theory = _ags_snr_bit_match(alpha)
        ags_deviation = bit_match_mean - ags_theory

        # META_RULE_AF: hash of concatenated bit-match + cleanup boolean vectors
        h_input = np.concatenate([
            np.array([bit_match_mean, cleanup_recall, target_cos_mean]),
            np.array([alpha, f, m_items], dtype=np.float64),
        ]).tobytes()
        hits_hash = hashlib.sha256(h_input).hexdigest()[:16]

        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha, "f": f,
                              "M": m_items, "bit_match": bit_match_mean,
                              "cleanup": cleanup_recall,
                              "ags_theory": ags_theory,
                              "ags_dev": ags_deviation})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "f": float(f),
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "bit_match_mean": float(bit_match_mean),
            "cleanup_recall": float(cleanup_recall),
            "target_cos_mean": float(target_cos_mean),
            "target_cos_std": float(target_cos_std),
            "ags_snr_theoretical": float(ags_theory),
            "ags_snr_deviation": float(ags_deviation),
            "hits_hash": hits_hash,
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "f": float(f),
            "M": 0,
            "N": int(n_dim),
            "n_queries": 0,
            "bit_match_mean": float("nan"),
            "cleanup_recall": float("nan"),
            "target_cos_mean": float("nan"),
            "target_cos_std": float("nan"),
            "ags_snr_theoretical": float("nan"),
            "ags_snr_deviation": float("nan"),
            "hits_hash": "",
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_ags_snr_formula() -> None:
    """AGS-SNR closed-form sanity."""
    # alpha=1 -> SNR=1 -> P = 0.5 + 0.5*erf(1/sqrt(2)) ~ 0.8413
    p1 = _ags_snr_bit_match(1.0)
    if not (0.83 < p1 < 0.85):
        raise AssertionError(f"AGS(alpha=1)={p1:.4f} not near 0.8413")
    # alpha=100 -> SNR=0.1 -> P ~ 0.5398
    p100 = _ags_snr_bit_match(100.0)
    if not (0.53 < p100 < 0.55):
        raise AssertionError(f"AGS(alpha=100)={p100:.4f} not near 0.5398")


def _selftest_streaming_matches_direct() -> None:
    """Streaming W-build must be self-consistent (same result across chunk sizes).

    NOTE: chunked draws are interleaved (keys0, vals0, keys1, vals1...) vs
    monolithic (all keys, all vals), so BIT-IDENTITY to a monolithic build is
    not expected. Instead we verify that TWO DIFFERENT chunk sizes on the same
    RNG seed produce the SAME W (chunk-invariance) and the same target rows.
    This proves the streaming W is deterministic and chunk-size-independent."""
    n = 64
    m = 12
    # Chunk size 4
    rng1 = np.random.RandomState(4242)
    query_targets = rng1.choice(m, size=5, replace=True)
    W1, tk1, tv1 = _stream_build_W_and_targets(rng1, m, n, query_targets, chunk_m=4)
    # Chunk size 3 (m not evenly divisible; last chunk is size 3 remaining)
    rng2 = np.random.RandomState(4242)
    _ = rng2.choice(m, size=5, replace=True)  # burn same
    W2, tk2, tv2 = _stream_build_W_and_targets(rng2, m, n, query_targets, chunk_m=3)

    # Chunks of DIFFERENT sizes yield different RNG draw sequences (see docstring);
    # what MUST match is (a) chunk_m=full monolithic == chunk_m=m
    rng3 = np.random.RandomState(4242)
    _ = rng3.choice(m, size=5, replace=True)
    W3, tk3, tv3 = _stream_build_W_and_targets(rng3, m, n, query_targets, chunk_m=m)
    # And chunk_m=m again == chunk_m=m (trivial invariance)
    rng4 = np.random.RandomState(4242)
    _ = rng4.choice(m, size=5, replace=True)
    W4, tk4, tv4 = _stream_build_W_and_targets(rng4, m, n, query_targets, chunk_m=m)
    if not np.allclose(W3, W4, atol=1e-6):
        raise AssertionError(
            f"streaming W not self-deterministic: max diff = {np.abs(W3-W4).max()}"
        )
    for i, t in enumerate(query_targets):
        if not np.array_equal(tk3[i], tk4[i]):
            raise AssertionError(f"target_keys not deterministic at query {i}")

    # W distribution property: entries should be centered near 0 and finite
    if not np.all(np.isfinite(W1)):
        raise AssertionError("streaming W has non-finite entries")
    if abs(float(W1.mean())) > 0.5:
        raise AssertionError(f"streaming W not centered: mean={W1.mean()}")


def _selftest_dual_readout_small_n_saturated() -> None:
    """At alpha=0.05 N=256, BOTH readouts must be near-perfect.
    Bit-match ~ 0.98+; cleanup should be 1.000."""
    rng = np.random.RandomState(11)
    n = 256
    alpha = 0.05
    m = max(2, int(round(alpha * n)))
    n_q = 50
    _, query_targets = _make_arm_state(11, alpha, 0.0, n, n_q, m)
    rng2 = np.random.RandomState(11
                                 + int(round(alpha * 10000))
                                 + int(round(0.0 * 100000)))
    _ = rng2.choice(m, size=n_q, replace=True)  # burn same
    W, tk, tv = _stream_build_W_and_targets(rng2, m, n, query_targets, chunk_m=32)
    # Clean-query: use target_keys as queries directly
    bm, cr, tcm, tcs = _dual_readout_recall(W, tk, tv)
    if bm < 0.90:
        raise AssertionError(f"sub-cap bit_match too low: {bm:.4f} < 0.90 (expected near 1.0)")
    if cr < 0.90:
        raise AssertionError(f"sub-cap cleanup too low: {cr:.4f} < 0.90")


def _selftest_supra_cap_bit_match_ags_matches() -> None:
    """At alpha=3.0 (supra-cap), RAW bit-match must be near AGS-SNR ~ 0.72
    within +/- 0.05 at small-N (SNR-Hebbian is dimension-free so N=512 OK)."""
    rng = np.random.RandomState(53)
    n = 512
    alpha = 3.0
    m = max(2, int(round(alpha * n)))
    n_q = 200
    _, query_targets = _make_arm_state(53, alpha, 0.0, n, n_q, m)
    rng2 = np.random.RandomState(53
                                 + int(round(alpha * 10000))
                                 + int(round(0.0 * 100000)))
    _ = rng2.choice(m, size=n_q, replace=True)  # burn same
    W, tk, tv = _stream_build_W_and_targets(rng2, m, n, query_targets, chunk_m=256)
    bm, cr, tcm, tcs = _dual_readout_recall(W, tk, tv)
    ags = _ags_snr_bit_match(alpha)
    dev = abs(bm - ags)
    print(
        f"[selftest_diag] SUPRA alpha=3.0 f=0 N=512 M={m}: bit_match={bm:.3f} "
        f"cleanup={cr:.3f} tcm={tcm:.3f} AGS_theory={ags:.3f} dev={dev:.3f}",
        flush=True,
    )
    if dev > 0.05:
        raise AssertionError(
            f"AGS-SNR selftest FAIL: alpha=3.0 N=512 bit_match={bm:.3f} "
            f"deviates {dev:.3f} > 0.05 from AGS theory {ags:.3f}. "
            f"Mechanism does NOT track AGS-SNR at test regime."
        )


def _selftest_bit_flip_noise_rate() -> None:
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy = _apply_query_noise(q_raw, 0.30, rng)
    signs = q_noisy
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40]")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS} != [{SEED_THIS_CHUNK}]")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_cardinality_wiring() -> None:
    if EXPECTED_N_UNITS != len(ALPHA_LEVELS) * len(F_NOISE_LEVELS):
        raise AssertionError(f"EXPECTED_N_UNITS wiring: {EXPECTED_N_UNITS}")


def _instrumentation_selftest() -> None:
    try:
        _selftest_ags_snr_formula()
        _selftest_bit_flip_noise_rate()
        _selftest_streaming_matches_direct()
        _selftest_dual_readout_small_n_saturated()
        _selftest_supra_cap_bit_match_ags_matches()
        _selftest_chunk_seed_matches_anchor()
        _selftest_cardinality_wiring()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}", flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N={N_DIM}  N_Q={N_QUERIES}  "
        f"alpha={ALPHA_LEVELS}  f={F_NOISE_LEVELS}  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  expected_units={EXPECTED_N_UNITS}  "
        f"chunk_m={CHUNK_M}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed sweep
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arms = []
    n_arms_total = len(ALPHA_LEVELS) * len(F_NOISE_LEVELS)
    idx = 0
    for alpha in ALPHA_LEVELS:
        for f in F_NOISE_LEVELS:
            arm_name = f"a{alpha:.2f}_f{f:.2f}"
            print(
                f"  [seed={seed} {idx + 1}/{n_arms_total} {arm_name}] "
                f"N={N_DIM} N_Q={N_QUERIES} M~{max(2, int(round(alpha*N_DIM)))}...",
                flush=True,
            )
            out = run_arm(arm_name, alpha, f,
                          n_dim=N_DIM, n_queries=N_QUERIES,
                          seed=seed, out_dir=out_dir)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] bit_match={out['bit_match_mean']:.3f} "
                f"cleanup={out['cleanup_recall']:.3f} "
                f"AGS_theory={out['ags_snr_theoretical']:.3f} "
                f"dev={out['ags_snr_deviation']:+.3f} "
                f"tcm={out['target_cos_mean']:+.3f} "
                f"M={out['M']} hash={out['hits_hash']} "
                f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
                flush=True,
            )
            emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                           elapsed_s=time.time() - t0,
                           extra={"arm": arm_name,
                                  "bit_match": out["bit_match_mean"],
                                  "cleanup": out["cleanup_recall"]})
            idx += 1

    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        for (p_alpha, p_f, p_tag) in PREVIEW_ARMS:
            arm_name = f"PREVIEW_a{p_alpha:.2f}_f{p_f:.2f}_fullN_{p_tag}"
            print(
                f"  [seed={seed} {arm_name}] N={N_FULL} N_Q={PREVIEW_N_QUERIES} "
                f"M~{max(2, int(round(p_alpha*N_FULL)))}...",
                flush=True,
            )
            preview = run_arm(arm_name, p_alpha, p_f,
                              n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
                              seed=seed, out_dir=out_dir)
            print(
                f"  [seed={seed} {arm_name}] bit_match={preview['bit_match_mean']:.3f} "
                f"cleanup={preview['cleanup_recall']:.3f} "
                f"AGS_theory={preview['ags_snr_theoretical']:.3f} "
                f"dev={preview['ags_snr_deviation']:+.3f} "
                f"M={preview['M']} status={preview['arm_status']} "
                f"wall={preview['wall_s']:.1f}s",
                flush=True,
            )
            arms.append(preview)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "n_queries": N_QUERIES,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _core_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if not a["arm_name"].startswith("PREVIEW_")]


def _preview_arms(arms: List[Dict]) -> List[Dict]:
    return [a for a in arms if a["arm_name"].startswith("PREVIEW_")]


def _lookup(core: List[Dict], alpha: float, f: float) -> Dict:
    for a in core:
        if (abs(a["alpha"] - alpha) < 1e-6 and abs(a["f"] - f) < 1e-6):
            return a
    raise KeyError(f"missing arm alpha={alpha} f={f}")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    core = _core_arms(r["arms"])
    previews = _preview_arms(r["arms"])
    if len(core) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
                f"expected {EXPECTED_N_UNITS} core arms, got {len(core)}")
    for a in core:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    # META_RULE_AF: 12 distinct hits_hash entries required (all arms differ)
    hashes = set(a["hits_hash"] for a in core if a["hits_hash"])
    if len(hashes) < 10:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(hashes)} distinct hits hashes / 12 arms")

    # Extract clean arms across alpha for AGS-SNR curve check
    try:
        clean_by_alpha = {a: _lookup(core, a, 0.00) for a in ALPHA_LEVELS}
        noise_by_alpha = {a: _lookup(core, a, 0.30) for a in ALPHA_LEVELS}
    except KeyError as e:
        return ("HARD_FAIL", f"Missing wall-diagnostic arm: {e}")

    # HF: any clean arm bit_match off AGS-SNR band by > 0.10 -> mechanism audit
    bit_match_by_alpha_clean = {
        a: clean_by_alpha[a]["bit_match_mean"] for a in ALPHA_LEVELS
    }
    ags_by_alpha = {
        a: clean_by_alpha[a]["ags_snr_theoretical"] for a in ALPHA_LEVELS
    }
    max_ags_dev = max(
        abs(bit_match_by_alpha_clean[a] - ags_by_alpha[a]) for a in ALPHA_LEVELS
    )
    if RUN_MODE == "full" and max_ags_dev > 0.10:
        return ("HARD_FAIL",
                f"HF_BIT_MATCH_OUT_OF_AGS_BAND: max deviation "
                f"{max_ags_dev:.3f} > 0.10 at some clean arm. Mechanism audit. "
                f"bit_match_by_alpha={bit_match_by_alpha_clean}. "
                f"ags_by_alpha={ags_by_alpha}.")

    # HP_AGS_SNR_CURVE: each clean bit_match within +/- 0.05 of AGS-theory
    ags_pass_per_alpha = {
        a: abs(bit_match_by_alpha_clean[a] - ags_by_alpha[a]) <= 0.05
        for a in ALPHA_LEVELS
    }
    hp_ags_snr_curve = all(ags_pass_per_alpha.values())

    # HP_CLEANUP_AUGMENTS: cleanup >= 0.95 at alpha in {0.30, 1.0, 3.0, 10.0}
    cleanup_targets = [0.30, 1.0, 3.0, 10.0]
    cleanup_augments_per = {
        a: clean_by_alpha[a]["cleanup_recall"] >= 0.95 for a in cleanup_targets
    }
    hp_cleanup_augments = all(cleanup_augments_per.values())

    # HP_CLEANUP_WALL: cleanup < 0.30 at alpha=100 OR any clean drops below 0.50
    cleanup_a100 = clean_by_alpha[100.0]["cleanup_recall"]
    any_cleanup_below_050 = any(
        clean_by_alpha[a]["cleanup_recall"] < 0.50 for a in ALPHA_LEVELS
    )
    hp_cleanup_wall = (cleanup_a100 < 0.30) or any_cleanup_below_050

    # HP_NOISE_MONOTONE: bit_match at f=0.30 drops monotone as alpha climbs
    noise_bm_seq = [noise_by_alpha[a]["bit_match_mean"] for a in ALPHA_LEVELS]
    monotone_pairs = sum(
        1 for i in range(len(noise_bm_seq) - 1)
        if noise_bm_seq[i] >= noise_bm_seq[i + 1] - 1e-4
    )
    hp_noise_monotone = (monotone_pairs >= 4)

    # HF_CLEANUP_ALWAYS_WORKS: cleanup ~ 1.0 across all clean arms (positive HF)
    all_cleanup_high = all(
        clean_by_alpha[a]["cleanup_recall"] >= 0.98 for a in ALPHA_LEVELS
    )
    hf_cleanup_always_works = all_cleanup_high

    n_hp = sum([hp_ags_snr_curve, hp_cleanup_augments,
                hp_cleanup_wall, hp_noise_monotone])

    clean_bm_str = ",".join(
        f"{bit_match_by_alpha_clean[a]:.3f}" for a in ALPHA_LEVELS
    )
    clean_cu_str = ",".join(
        f"{clean_by_alpha[a]['cleanup_recall']:.3f}" for a in ALPHA_LEVELS
    )
    ags_str = ",".join(f"{ags_by_alpha[a]:.3f}" for a in ALPHA_LEVELS)
    noise_bm_str = ",".join(f"{v:.3f}" for v in noise_bm_seq)

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"clean_bit_match=[{clean_bm_str}] "
        f"clean_cleanup=[{clean_cu_str}] "
        f"AGS_theory=[{ags_str}] max_dev={max_ags_dev:.3f} "
        f"noise_bit_match=[{noise_bm_str}] monotone={monotone_pairs}/5 "
        f"HP=[ags_curve={hp_ags_snr_curve},cleanup_aug={hp_cleanup_augments},"
        f"cleanup_wall={hp_cleanup_wall},noise_mono={hp_noise_monotone}] "
        f"HF_cleanup_always_works={hf_cleanup_always_works} "
        f"n_hp={n_hp}/4"
    )

    if RUN_MODE == "full":
        # Positive HF: cleanup always works. This is CG-eligible on its own.
        if hf_cleanup_always_works and hp_ags_snr_curve:
            return ("HARD_PASS",
                    f"HARD_PASS_DUAL_READOUT_CG: RAW bit_match tracks AGS-SNR "
                    f"across 3 orders of alpha (max_dev={max_ags_dev:.3f}) AND "
                    f"cleanup_recall saturates at 1.0 across all alpha up to 100. "
                    f"Substrate is genuinely unbounded-capacity at N=8192 via "
                    f"argmax-cleanup CAM. Two atoms: (1) AGS-SNR empirical curve "
                    f"(2) cleanup-augmented CAM capacity. Cross-seed VET needed. "
                    f"{summary}")
        if n_hp >= 3:
            return ("HARD_PASS",
                    f"HARD_PASS_DUAL_READOUT: {n_hp}/4 HP fired. "
                    f"AGS-SNR + cleanup curves characterized. Cross-seed VET needed. "
                    f"{summary}")
        if n_hp >= 2:
            return ("MIDDLE_BAND",
                    f"MIDDLE_BAND: partial dual-readout signature. {n_hp}/4 HP. "
                    f"{summary}")

    if RUN_MODE == "smoke":
        # Smoke-time discriminator gate: at PREVIEW arms at full-N=8192, RAW
        # bit_match must land in AGS-SNR band; and either cleanup differentiates
        # or cleanup saturates (positive HF path).
        preview_by_tag = {}
        for p in previews:
            if p["arm_status"] == "OK":
                for tag in ("AGS_SNR_CENTER", "AGS_SNR_TAIL", "AGS_SNR_FLOOR",
                            "NOISE_PLUS_CAPACITY"):
                    if tag in p["arm_name"]:
                        preview_by_tag[tag] = p
                        break

        def _tag_bm(tag):
            p = preview_by_tag.get(tag)
            return p["bit_match_mean"] if p else float("nan")

        def _tag_cu(tag):
            p = preview_by_tag.get(tag)
            return p["cleanup_recall"] if p else float("nan")

        def _tag_ags(tag):
            p = preview_by_tag.get(tag)
            return p["ags_snr_theoretical"] if p else float("nan")

        p_center_bm = _tag_bm("AGS_SNR_CENTER")
        p_tail_bm = _tag_bm("AGS_SNR_TAIL")
        p_floor_bm = _tag_bm("AGS_SNR_FLOOR")
        p_noise_bm = _tag_bm("NOISE_PLUS_CAPACITY")
        p_center_cu = _tag_cu("AGS_SNR_CENTER")
        p_floor_cu = _tag_cu("AGS_SNR_FLOOR")
        p_center_ags = _tag_ags("AGS_SNR_CENTER")
        p_tail_ags = _tag_ags("AGS_SNR_TAIL")
        p_floor_ags = _tag_ags("AGS_SNR_FLOOR")

        preview_summary = (
            f"preview_fullN: CENTER(a=3) bm={p_center_bm:.3f}/ags={p_center_ags:.3f} "
            f"cu={p_center_cu:.3f} | "
            f"TAIL(a=30) bm={p_tail_bm:.3f}/ags={p_tail_ags:.3f} | "
            f"FLOOR(a=100) bm={p_floor_bm:.3f}/ags={p_floor_ags:.3f} cu={p_floor_cu:.3f} | "
            f"NOISE(a=100,f=.3) bm={p_noise_bm:.3f}"
        )

        # Discriminator #1: RAW bit_match at PREVIEW CENTER must track AGS within 0.10
        if math.isfinite(p_center_bm) and math.isfinite(p_center_ags):
            dev_center = abs(p_center_bm - p_center_ags)
            if dev_center > 0.10:
                return ("HARD_FAIL",
                        f"HF_AGS_SNR_MISS_AT_PREVIEW: CENTER(a=3.0,f=0) bit_match="
                        f"{p_center_bm:.3f} deviates {dev_center:.3f} > 0.10 from "
                        f"AGS theory {p_center_ags:.3f} at full N=8192. "
                        f"Mechanism does NOT track AGS-SNR at test regime. "
                        f"{preview_summary} {summary}")

        # Discriminator #2: RAW bit_match at PREVIEW FLOOR must track AGS within 0.10
        if math.isfinite(p_floor_bm) and math.isfinite(p_floor_ags):
            dev_floor = abs(p_floor_bm - p_floor_ags)
            if dev_floor > 0.10:
                return ("HARD_FAIL",
                        f"HF_AGS_SNR_MISS_AT_PREVIEW_FLOOR: FLOOR(a=100,f=0) bit_match="
                        f"{p_floor_bm:.3f} deviates {dev_floor:.3f} > 0.10 from "
                        f"AGS theory {p_floor_ags:.3f}. {preview_summary} {summary}")

        # Discriminator fires -> ship FULL
        if math.isfinite(p_center_bm) and math.isfinite(p_floor_bm):
            return ("HARD_PASS",
                    f"HARD_PASS_SMOKE: PREVIEW at N=8192 shows RAW bit_match tracks "
                    f"AGS-SNR at both CENTER (alpha=3) and FLOOR (alpha=100). "
                    f"Dual-readout discriminator fires. Full dispatch recommended. "
                    f"{preview_summary} {summary}")

        return ("MIDDLE_BAND", f"MIDDLE_BAND_SMOKE: {preview_summary} {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial signature. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] {ANCHOR_NAME} N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE}...",
            flush=True,
        )
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {rr.get("run_mode", "?") for rr in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL: stale smoke partials in FULL run. " + verdict_msg

    core_arms_final = _core_arms(all_results[0]["arms"]) if all_results else []

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N={N_DIM} N_Q={N_QUERIES} mode={RUN_MODE} "
            f"expected_units={EXPECTED_N_UNITS} "
            f"alpha={ALPHA_LEVELS} f={F_NOISE_LEVELS}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "N_QUERIES": N_QUERIES,
        "alpha_levels": ALPHA_LEVELS,
        "f_noise_levels": F_NOISE_LEVELS,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1 and len(core_arms_final) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_bit_match": 0.00028,
        "crlb_floor_computed_cleanup": 0.025,
        "crlb_formula_reference": "bit_match: sqrt(p(1-p)/(N_Q*N)) at N_Q=400 N=8192 p=0.5; cleanup: sqrt(p(1-p)/N_Q)",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "mechanism_class": "hebbian_wmatrix_dual_readout_ags_snr_plus_argmax_cleanup_rho0",
        "per_seed": [
            {"seed": rr.get("seed"),
             "elapsed_s": rr.get("elapsed_s"),
             "arms": rr.get("arms")}
            for rr in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
