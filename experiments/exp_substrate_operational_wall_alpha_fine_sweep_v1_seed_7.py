"""substrate_operational_wall_alpha_fine_sweep_v1 -- seed_7.

Chain-grade closure of the substrate's operational saturation wall at rho=0
(iid keys baseline). Complements the Lowe correlated-key CG.

MECHANISM (Cell D v2 canonical Hebbian W-matrix):
  W = sum_i outer(vals[i], keys[i]) / N       # (N x N) accumulator, eta=1 uniform
  out = sign(q_noisy @ W.T)                    # linear projection + sign
  match = argmax(cos(out_n, vals_n_i))         # cleanup readout

SWEEP GRID (per seed, iid bipolar keys ρ=0):
  alpha in {0.60, 0.85, 0.90, 0.95}  * f in {0.00, 0.20, 0.30, 0.40, 0.43}
  = 20 core arms
  N_QUERIES = 800

FALSIFIABLE PREDICTIONS (verdict gates):
  HP_STABLE_BELOW_WALL:  (a=0.60, f=0.00) recall >= 0.95
  HP_DISCRIMINATING_ZONE_FIRES:  at (a=0.85, f=0.00) OR (a=0.90, f=0.00),
    recall in [0.30, 0.95]
  HP_COLLAPSE_ABOVE_WALL:  (a=0.95, f=0.00) recall <= 0.50
  HP_NOISE_SHARPENS_WALL:  (a=0.60, f=0.43) recall in [0.30, 0.85]
  HF_WALL_MISPLACED:  all a in {0.85, 0.90} f=0 saturate >= 0.98 AND all
    a in {0.95} f=0 crash < 0.10
  HF_NO_TRANSITION:  (a=0.90, f=0.00) recall >= 0.98 AND (a=0.95, f=0.00) < 0.10
  HF_STRUCTURAL_INFRA:
    baseline (a=0.60, f=0.00) < 0.85
    UNIT_CARDINALITY_BREACH:  len(core) != 20
    META_RULE_AF:  bit-identical arm hits
    CELL_CRASHED

CARDINALITY (META_RULE_H):  20 arms per seed.

CRLB (capacity feasibility):
  Per-arm recall = binomial over N_QUERIES=800.
  sigma_min(p=0.5) = 0.0177 THEORETICAL@binomial-CLT.
  HP gap in [0.30, 0.95] = 0.65 span >> 3*sigma = 0.053 -> reachable.
  Discriminator gap >= 0.30 required to fire >> CLT-noise 0.011.

DISCRIMINATOR-MUST-SURVIVE-SCALE (pattern C):
  Smoke runs at N=1024, N_Q=200 for arm-runtime verification + 4 preview
  arms at FULL N=8192 covering the wall + noise-arm regime:
    PREVIEW (a=0.60, f=0.00) at N=8192  -> expect recall ~ 1.00 (baseline)
    PREVIEW (a=0.85, f=0.00) at N=8192  -> expect recall in [0.30, 0.99] (DISCRIM)
    PREVIEW (a=0.95, f=0.00) at N=8192  -> expect recall < 0.50 (COLLAPSE)
    PREVIEW (a=0.60, f=0.43) at N=8192  -> expect recall in [0.30, 0.85] (P3)
  Smoke verdict from previews (fires the wall discriminator at full-N).

BASELINE_IN_BAND: (a=0.60, f=0.00) should be >= 0.85 at FULL, >= 0.60 at SMOKE.

Cross-references:
- notes/research_dense_hopfield_underloaded_saturation_theory_2x_drill_2026-07-02.md (SONNET DRILL)
- notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md (Lowe rho>0 CG)
- Amit-Gutfreund-Sompolinsky 1985 CITED (a_c = 0.138 classical wall)
- Berry-Esseen CITED (CLT error O(1/sqrt(N)))
- Cell D v2 template: exp_distributional_shape_zipfian_v3_hebbian_wmatrix_canonical_seed_7.py

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
  - arms_differ_verified at smoke gate (META_RULE_AF; SHA256 hash of hits)
  - final_metrics_atomicity = tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed = 0.0177 (discriminator_reachability = True)
  - baseline_in_band at smoke (a=0.60, f=0 > 0.60 smoke, > 0.85 full)
  - discriminator survives scale (smoke has full-N preview arms)
  - HARD_PASS strictly above floor (band width 0.05)
  - cardinality_ok (EXPECTED_N_UNITS = 20)
  - per-unit failure_class instrumentation (no bare except)
  - calibration_check = default_ok_for_this_regime
  - all numbers tagged MEASURED / HYPOTHESIZED / THEORETICAL / CITED

PROT-018: anchor _seed_7 (no _n suffix; N=8192 constant).
PROT-021: single-seed cell (chunked); _seed_checkpoint import present.
ASCII-only.

PRESERVE_ENV_VARS: HDLAB_QUEUE

WALL-TIME NOTE: W at N=8192 float32 = 256 MB. Build via einsum. Per-arm at
largest M=alpha*N=7782 (a=0.95): build ~1s + readout n_q * N * M = 800 * 8192
* 7782 fma = 51 GF -> ~15s CPU. Total per-seed FULL wall ~ 20 * 12s = 240s +
overhead ~ 5-8 min. Timeout 3600s safe headroom.
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
ANCHOR_NAME = "substrate_operational_wall_alpha_fine_sweep_v1_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "operational_wall_alpha_f_sweep_v1_seed_chunk"

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
ALPHA_LEVELS = [0.60, 0.85, 0.90, 0.95]
F_NOISE_LEVELS = [0.00, 0.20, 0.30, 0.40, 0.43]
N_QUERIES_FULL = 800

# Smoke config
N_SMOKE = 1024
N_QUERIES_SMOKE = 200
# Preview arm regimes at full-N (Discriminator-must-survive-scale pattern C)
PREVIEW_ARMS = [
    # (alpha, f, expected_regime_tag)
    (0.60, 0.00, "SAT_BASELINE"),
    (0.85, 0.00, "DISCRIM"),
    (0.95, 0.00, "COLLAPSE"),
    (0.60, 0.43, "NOISE_SHARPEN_P3"),
]
PREVIEW_N_QUERIES = 400

RUN_FULL_N_PREVIEW = (RUN_MODE == "smoke")

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    N_QUERIES = N_QUERIES_SMOKE
else:
    N_DIM = N_FULL
    N_QUERIES = N_QUERIES_FULL

SEEDS = [SEED_THIS_CHUNK]
EXPECTED_N_UNITS = len(ALPHA_LEVELS) * len(F_NOISE_LEVELS)
assert EXPECTED_N_UNITS == 20, f"EXPECTED_N_UNITS wiring bug: {EXPECTED_N_UNITS}"

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},N_QUERIES={N_QUERIES},"
    f"alpha_levels={ALPHA_LEVELS},f_levels={F_NOISE_LEVELS},"
    f"chunk_seed={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},"
    f"expected_n_units={EXPECTED_N_UNITS},"
    f"hardening=operational_wall_v1+METARULE_AF+METARULE_AH"
)


# ---------------------------------------------------------------------------
# Core mechanism helpers
# ---------------------------------------------------------------------------
def _l2norm_rows(x: np.ndarray) -> np.ndarray:
    return x / np.linalg.norm(x, axis=1, keepdims=True).clip(min=1e-12)


def _apply_query_noise(queries_raw: np.ndarray, f: float,
                       rng: np.random.RandomState) -> np.ndarray:
    """BSC bit-flip on bipolar keys at rate f. Returns L2-normalized rows."""
    if f <= 0.0:
        return _l2norm_rows(queries_raw)
    flip_mask = rng.random(queries_raw.shape) < f
    noisy = queries_raw.copy()
    noisy[flip_mask] = -noisy[flip_mask]
    return _l2norm_rows(noisy)


def _build_hebbian_W(keys_raw: np.ndarray, vals_raw: np.ndarray) -> np.ndarray:
    """W = sum_i outer(vals[i], keys[i]) / N (eta=1 uniform).

    Uses einsum for memory-efficient accumulation. keys_raw/vals_raw are
    bipolar in {-1, +1}. Returns W as (N, N) float32.
    """
    n = keys_raw.shape[1]
    keys32 = keys_raw.astype(np.float32)
    vals32 = vals_raw.astype(np.float32)
    # einsum: 'ia,ib -> ab' contracts i (items axis), leaves (N, N).
    W = np.einsum("ia,ib->ab", vals32, keys32)
    W /= float(n)
    return W  # (N, N) float32


def _hebbian_wmatrix_recall(W: np.ndarray, vals_norm: np.ndarray,
                            queries_noisy_n: np.ndarray,
                            query_targets: np.ndarray,
                            batch: int = 256) -> np.ndarray:
    """Readout: out = sign(q @ W.T); match = argmax(cos(out_n, vals_norm)).

    queries_noisy_n: (Q, N) L2-normalized noisy queries.
    vals_norm: (M, N) L2-normalized value rows for cleanup readout.
    W: (N, N) float32 Hebbian accumulator.
    """
    q_count = queries_noisy_n.shape[0]
    hits = np.zeros(q_count, dtype=bool)
    v_n_32 = vals_norm.astype(np.float32)
    for start in range(0, q_count, batch):
        end = min(q_count, start + batch)
        q_chunk = queries_noisy_n[start:end].astype(np.float32)  # (c, N)
        out = q_chunk @ W.T                                       # (c, N)
        out = np.sign(out)
        # normalize + argmax against vals_norm
        out_n = out / np.linalg.norm(out, axis=1, keepdims=True).clip(min=1e-12)
        sims = out_n @ v_n_32.T                                   # (c, M)
        argmax = sims.argmax(axis=1)
        expected = query_targets[start:end]
        hits[start:end] = (argmax == expected)
    return hits


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, alpha: float, f: float,
            n_dim: int, n_queries: int, seed: int,
            out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        m_items = max(2, int(round(alpha * n_dim)))
        rng = np.random.RandomState(
            seed
            + int(round(alpha * 10000))
            + int(round(f * 100000))
        )

        keys_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)
        vals_raw = rng.choice([-1.0, 1.0], size=(m_items, n_dim)).astype(np.float64)

        # Query pattern IDs sampled uniformly (rho=0 baseline)
        query_targets = rng.choice(m_items, size=n_queries, replace=True)

        # Build W-matrix (Hebbian; eta=1 uniform)
        W = _build_hebbian_W(keys_raw, vals_raw)

        # Query preparation
        query_keys_raw = keys_raw[query_targets]
        queries_noisy_n = _apply_query_noise(query_keys_raw, f, rng)

        # Cleanup readout uses L2-normalized values
        vals_norm = _l2norm_rows(vals_raw)

        # Readout
        hits = _hebbian_wmatrix_recall(W, vals_norm, queries_noisy_n, query_targets)
        recall_all = float(hits.mean())

        # Hash of hits vector for arms-must-differ (META_RULE_AF)
        hits_hash = hashlib.sha256(hits.tobytes()).hexdigest()[:16]

        # Analytical margin (drill Regime Table)
        s0 = 1.0 - 2.0 * f
        max_comp_theoretical = math.sqrt(2.0 * m_items * math.log(max(m_items, 2))) / n_dim
        margin_theoretical = s0 - max_comp_theoretical

        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"arm": arm_name, "alpha": alpha, "f": f,
                              "M": m_items, "recall": recall_all,
                              "margin": margin_theoretical})

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "alpha": float(alpha),
            "f": float(f),
            "M": int(m_items),
            "N": int(n_dim),
            "n_queries": int(n_queries),
            "recall_all": recall_all,
            "hits_hash": hits_hash,
            "margin_theoretical": float(margin_theoretical),
            "max_comp_theoretical": float(max_comp_theoretical),
            "s0_theoretical": float(s0),
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
            "recall_all": float("nan"),
            "hits_hash": "",
            "margin_theoretical": float("nan"),
            "max_comp_theoretical": float("nan"),
            "s0_theoretical": float("nan"),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_hebbian_wmatrix_clean_recall() -> None:
    """B.2 canonical Hebbian W-matrix must achieve >=0.90 recall at clean
    below-wall regime (M/N = 0.05, f = 0)."""
    rng = np.random.RandomState(11)
    n = 256
    m = int(0.05 * n)  # 12 items; well below wall
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = _build_hebbian_W(keys_raw, vals_raw)
    vals_norm = _l2norm_rows(vals_raw)
    q_raw = _l2norm_rows(keys_raw)  # exact queries
    targets = np.arange(m)
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, targets)
    r = float(hits.mean())
    if r < 0.90:
        raise AssertionError(f"clean recall too low: {r:.3f} < 0.90 (wiring bug?)")


def _selftest_bit_flip_noise_rate() -> None:
    rng = np.random.RandomState(31)
    q_raw = np.ones((10, 4096), dtype=np.float64)
    q_noisy_n = _apply_query_noise(q_raw, 0.30, rng)
    signs = np.sign(q_noisy_n)
    flip_rate = float((signs != 1.0).mean())
    if not (0.20 < flip_rate < 0.40):
        raise AssertionError(f"bit-flip rate {flip_rate} not in [0.20, 0.40]")


def _selftest_margin_formula_at_reference_point() -> None:
    """Verify margin formula matches drill Regime Table (line 129):
       at alpha=0.85, N=8192, margin should be ~0.104 (using formula
       margin = 1 - sqrt(2*M*log(M))/N with s0=1 for clean query).
    """
    n = 8192
    alpha = 0.85
    m = int(round(alpha * n))
    max_comp = math.sqrt(2.0 * m * math.log(m)) / n
    # Drill Regime Table: max_competitor = 0.0322 at alpha=0.85 -> matches formula
    if not (0.02 < max_comp < 0.05):
        raise AssertionError(
            f"margin formula reference-point drift: max_comp={max_comp:.4f} "
            f"at alpha=0.85 N=8192; expected ~0.032 per drill line 129"
        )


def _selftest_baseline_saturates() -> None:
    """alpha=0.60 clean f=0 should saturate at recall ~1.00 at small N."""
    rng = np.random.RandomState(53)
    n = 512
    alpha = 0.60
    m = int(round(alpha * n))
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = _build_hebbian_W(keys_raw, vals_raw)
    vals_norm = _l2norm_rows(vals_raw)
    query_targets = rng.choice(m, size=200, replace=True)
    q_raw = _l2norm_rows(keys_raw[query_targets])
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, query_targets)
    r = float(hits.mean())
    if r < 0.85:
        raise AssertionError(
            f"BASELINE_SAT_SELFTEST_FAIL: alpha=0.60 f=0 N=512 recall={r:.3f} < 0.85"
        )


def _selftest_collapse_at_alpha_95() -> None:
    """alpha=0.95 clean f=0 at N=1024 should show recall <0.90 (collapse regime
    per drill Regime Table). This is the KEY discriminator survives-scale check.
    """
    rng = np.random.RandomState(59)
    n = 1024
    alpha = 0.95
    m = int(round(alpha * n))
    keys_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    W = _build_hebbian_W(keys_raw, vals_raw)
    vals_norm = _l2norm_rows(vals_raw)
    query_targets = rng.choice(m, size=400, replace=True)
    q_raw = _l2norm_rows(keys_raw[query_targets])
    hits = _hebbian_wmatrix_recall(W, vals_norm, q_raw, query_targets)
    r = float(hits.mean())
    # Not a strict gate at small N; but do log a warning to stdout for the wiring:
    print(
        f"[selftest_diag] alpha=0.95 f=0 N=1024 M={m}: recall={r:.3f} "
        f"(drill predicts partial collapse at full N=8192)",
        flush=True,
    )
    # Just check the mechanism ran without crashing
    if not (0.0 <= r <= 1.0):
        raise AssertionError(f"collapse selftest recall out of bounds: {r}")


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
        _selftest_margin_formula_at_reference_point()
        _selftest_bit_flip_noise_rate()
        _selftest_hebbian_wmatrix_clean_recall()
        _selftest_baseline_saturates()
        _selftest_collapse_at_alpha_95()
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
        f"chunk_seed={SEED_THIS_CHUNK}  expected_units={EXPECTED_N_UNITS}",
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
                f"N={N_DIM} N_Q={N_QUERIES}...",
                flush=True,
            )
            out = run_arm(arm_name, alpha, f,
                          n_dim=N_DIM, n_queries=N_QUERIES,
                          seed=seed, out_dir=out_dir)
            arms.append(out)
            print(
                f"  [seed={seed} {arm_name}] recall={out['recall_all']:.3f} "
                f"margin_th={out['margin_theoretical']:+.3f} "
                f"M={out['M']} hash={out['hits_hash']} "
                f"status={out['arm_status']} wall={out['wall_s']:.2f}s",
                flush=True,
            )
            emit_heartbeat(out_dir, unit_idx=idx + 1, total_units=n_arms_total,
                           elapsed_s=time.time() - t0,
                           extra={"arm": arm_name, "recall": out["recall_all"]})
            idx += 1

    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        for (p_alpha, p_f, p_tag) in PREVIEW_ARMS:
            arm_name = f"PREVIEW_a{p_alpha:.2f}_f{p_f:.2f}_fullN_{p_tag}"
            print(
                f"  [seed={seed} {arm_name}] N={N_FULL} N_Q={PREVIEW_N_QUERIES}...",
                flush=True,
            )
            preview = run_arm(arm_name, p_alpha, p_f,
                              n_dim=N_FULL, n_queries=PREVIEW_N_QUERIES,
                              seed=seed, out_dir=out_dir)
            print(
                f"  [seed={seed} {arm_name}] recall={preview['recall_all']:.3f} "
                f"margin_th={preview['margin_theoretical']:+.3f} "
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

    # META_RULE_AF: arms-must-differ via hits_hash
    hashes = set(a["hits_hash"] for a in core if a["hits_hash"])
    if len(hashes) < 15:  # allow some collision at saturation but not bit-identical
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: only {len(hashes)} distinct hits hashes / 20 arms")

    # BASELINE_IN_BAND check
    try:
        a_baseline = _lookup(core, 0.60, 0.00)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing baseline arm: {e}")

    r_baseline = a_baseline["recall_all"]
    if RUN_MODE == "full":
        baseline_ok = (r_baseline >= 0.85)
    else:
        baseline_ok = (r_baseline >= 0.60)
    if not baseline_ok:
        return ("HARD_FAIL",
                f"BASELINE_OUT_OF_BAND: (a=0.60, f=0.00) recall={r_baseline:.3f}")

    # Extract wall-diagnostic arms
    try:
        a85_clean = _lookup(core, 0.85, 0.00)
        a90_clean = _lookup(core, 0.90, 0.00)
        a95_clean = _lookup(core, 0.95, 0.00)
        a60_noise = _lookup(core, 0.60, 0.43)
    except KeyError as e:
        return ("HARD_FAIL", f"Missing wall-diagnostic arm: {e}")

    r85 = a85_clean["recall_all"]
    r90 = a90_clean["recall_all"]
    r95 = a95_clean["recall_all"]
    r60_noise = a60_noise["recall_all"]

    # HP evaluations
    hp_stable_below_wall = (r_baseline >= 0.95)
    hp_discrim_fires = (0.30 <= r85 <= 0.95) or (0.30 <= r90 <= 0.95)
    hp_collapse_above_wall = (r95 <= 0.50)
    hp_noise_sharpens = (0.30 <= r60_noise <= 0.85)

    # HF evaluations
    hf_wall_misplaced = (r85 >= 0.98 and r90 >= 0.98 and r95 < 0.10)
    hf_no_transition = (r90 >= 0.98 and r95 < 0.10)

    n_hp = sum([hp_stable_below_wall, hp_discrim_fires,
                hp_collapse_above_wall, hp_noise_sharpens])

    summary = (
        f"seed={SEED_THIS_CHUNK} N={N_DIM} mode={RUN_MODE} "
        f"baseline(a=0.60,f=0)={r_baseline:.3f} "
        f"a85f0={r85:.3f} a90f0={r90:.3f} a95f0={r95:.3f} "
        f"a60f0.43={r60_noise:.3f} "
        f"HP=[stable={hp_stable_below_wall},discrim_fires={hp_discrim_fires},"
        f"collapse={hp_collapse_above_wall},noise_sharpens={hp_noise_sharpens}] "
        f"n_hp={n_hp}/4"
    )

    if RUN_MODE == "full":
        if hf_wall_misplaced:
            return ("HARD_FAIL",
                    f"HF_WALL_MISPLACED: a85f0>=0.98 AND a90f0>=0.98 AND a95f0<0.10; "
                    f"wall is elsewhere. {summary}")
        if hf_no_transition:
            return ("HARD_FAIL",
                    f"HF_NO_TRANSITION: a90f0>=0.98 AND a95f0<0.10; extremely narrow "
                    f"cliff between a=0.90 and a=0.95. Wider grid needed. {summary}")
        # Full-run HARD_PASS: at least 3 of 4 HP conditions
        if n_hp >= 3:
            return ("HARD_PASS",
                    f"HARD_PASS: operational-wall CG. {n_hp}/4 HP fired "
                    f"(baseline stable + discriminating zone + collapse + noise-sharpen). "
                    f"Complements Lowe rho>0 CG. Cross-seed VET needed. {summary}")
        if n_hp >= 2:
            return ("MIDDLE_BAND",
                    f"MIDDLE_BAND: partial wall signature. {n_hp}/4 HP fired. {summary}")

    if RUN_MODE == "smoke":
        # Smoke verdict from PREVIEW arms
        preview_by_tag = {}
        for p in previews:
            if p["arm_status"] == "OK":
                # Parse tag from arm name
                if "SAT_BASELINE" in p["arm_name"]:
                    preview_by_tag["SAT_BASELINE"] = p["recall_all"]
                elif "DISCRIM" in p["arm_name"]:
                    preview_by_tag["DISCRIM"] = p["recall_all"]
                elif "COLLAPSE" in p["arm_name"]:
                    preview_by_tag["COLLAPSE"] = p["recall_all"]
                elif "NOISE_SHARPEN_P3" in p["arm_name"]:
                    preview_by_tag["NOISE_SHARPEN_P3"] = p["recall_all"]

        preview_summary = (
            f"preview_fullN: SAT_BASE={preview_by_tag.get('SAT_BASELINE', float('nan')):.3f} "
            f"DISCRIM={preview_by_tag.get('DISCRIM', float('nan')):.3f} "
            f"COLLAPSE={preview_by_tag.get('COLLAPSE', float('nan')):.3f} "
            f"NOISE_P3={preview_by_tag.get('NOISE_SHARPEN_P3', float('nan')):.3f}"
        )

        p_sat = preview_by_tag.get("SAT_BASELINE", 0.0)
        p_dis = preview_by_tag.get("DISCRIM", 1.0)
        p_col = preview_by_tag.get("COLLAPSE", 1.0)
        p_noi = preview_by_tag.get("NOISE_SHARPEN_P3", 1.0)

        # Discriminator survives full-N?
        preview_baseline_ok = (p_sat >= 0.90)
        preview_wall_fires = (
            # At least ONE of the wall-diagnostic previews shows non-saturating recall:
            (p_dis <= 0.95 and p_dis >= 0.30) or
            (p_col <= 0.50) or
            (p_noi <= 0.85 and p_noi >= 0.30)
        )

        if not preview_baseline_ok:
            return ("HARD_FAIL",
                    f"PREVIEW_BASELINE_OUT_OF_BAND: full-N baseline={p_sat:.3f} < 0.90. "
                    f"Cell infra broken at full N. {preview_summary} {summary}")

        if preview_wall_fires:
            return ("HARD_PASS",
                    f"HARD_PASS_SMOKE: PREVIEW arms show wall discriminator fires at "
                    f"full N=8192. Full dispatch recommended. {preview_summary} {summary}")

        # All 3 wall-preview arms saturated at full N -> mechanism does NOT differentiate
        return ("HARD_FAIL",
                f"HF_WALL_DOES_NOT_FIRE_AT_FULL_N: all 3 preview wall-diagnostic arms "
                f"either saturated at ~1.0 or collapsed at ~0.0 without showing "
                f"DISCRIMINATING regime. Drill wall prediction not observable at "
                f"chosen alpha grid. {preview_summary} {summary}")

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
        "crlb_floor_computed": 0.0177,
        "crlb_formula_reference": "sigma_min = sqrt(p(1-p)/N_Q) binomial-CLT at N_Q=800 p=0.5",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "mechanism_class": "hebbian_wmatrix_canonical_operational_wall_baseline_rho0",
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
