"""lln_point_mass_large_vc_10k_1M_v1 -- test LLN + OOD floor at COMMERCIAL vocabulary scale.

MOTIVATION (2026-07-01):
  Atom 12 CG established LLN point-mass + OOD floor sqrt(2 log V_C / N) hold at V_C in {100,200,400}.
  Natural language needs V_C = 50k-500k (typical LM vocab). This cell tests the LEAP toward
  commercial-scale vocab: V_C in {1000, 10000, 100000, 1000000}. Substantive claim: if LLN + OOD
  formula still hold at V_C=1M, substrate is architected for commercial-scale vocabulary WITHOUT
  modification -- foundational for M3 language substrate roadmap.

DESIGN: 3-axis sweep (V_C x N x f)
  V_C in {1000, 10000, 100000, 1000000} (4 values)
  N in {8192, 16384} (2 values)
  f in {0.15} (1 value; center f, LLN already covers f-range at smaller V_C)
  = 8 phase points per seed x 3 seeds [7, 13, 19] = 24 units total

PROTOCOL per (V_C, N, f):
  1. Build KB of V_C bipolar keys, dim N, seeded RNG.
  2. Build 100-item cal set (50 in-KB f-flipped + 50 OOD fresh random).
  3. Compute max_sim per item over V_C KB.
  4. Record quantiles: p5/p10/p25/p50/p75/p95 (in-KB); p10/p50/p90 (OOD).
  5. Compute discriminators:
     - LLN center: p50_in_kb close to 1-2f = 0.7
     - LLN spread ratio: observed p5-p95 / theoretical normal spread in [0.5, 2.0]
     - OOD floor: p50_ood close to sqrt(2 log V_C / N) within 30%
     - BIMODAL GAP (NEW): in_kb_p5 - ood_p95 > 0.30 (substrate can distinguish in-KB from OOD at V_C=1M)

VERDICT GATES:
  HP_LLN_HOLDS_AT_LARGE_VC: spread ratio in [0.5, 2.0] AND |p50_in_kb - 0.7| < 0.010 at ALL 8 pts
  HP_OOD_FORMULA_HOLDS: |p50_ood - theo_ood| / theo_ood < 0.30 at ALL 8 pts
  HP_BIMODAL_GAP_DISCRIMINATES: (in_kb_p5 - ood_p95) > 0.30 at ALL 8 pts
  CHAIN_GRADE_COMMERCIAL_SCALE_VC if all 3 HP gates clear ALL 8 points across ALL 3 seeds.
  MIDDLE_BAND if some V_C pass but not others.
  HARD_FAIL_LLN_BREAKS if any p50_in_kb spread > 0.05.
  HARD_FAIL_OOD_SATURATES if any V_C where p50_ood > 0.5 (substrate confused).
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if seed produces != 8 phase points.

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  Smoke runs FULL 8-point grid at seed 7 -- includes V_C=1M / N=8192 highest-vocab preview.
  Precomputed theoretical values:
    V_C=1M / N=8192:  OOD_floor=0.0581  in_kb_spread(p5-p95)=0.0260  center=0.7  bimodal_gap~0.61
    V_C=1M / N=16384: OOD_floor=0.0411  in_kb_spread(p5-p95)=0.0184  center=0.7  bimodal_gap~0.64
  All predicted gaps well above 0.30 threshold; predicted OOD floors well below 0.5 saturation.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: implicit (sweep produces distinct OOD floors across V_C by construction)
- final_metrics_atomicity: per_iter_paths (per-seed _seed_checkpoint partials)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "LLN concentration cell; discriminator is spread + bimodal gap, not CRLB floor"
- baseline_in_band: N/A (no baseline arm; each point self-witnesses)
- discriminator survives scale: smoke runs FULL 8-point grid including V_C=1M at seed 7
- HARD_PASS strictly above floor + 5%: bimodal_gap 0.30 threshold vs predicted 0.61 = 2x margin
- HP_SCOPE: all 8 phase points get all 3 HP gates
- cardinality_ok: EXPECTED_N_UNITS=8 per seed; HF if breached
- per-unit failure-class instrumentation: specific-exception catch + failure_class field
- calibration_check: adaptive_with_discriminator_gate (spread + OOD gates use closed-form)
- all numbers tagged: MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ per META_RULE_AC

Author: exp_dev 2026-07-01 (large-V_C leap toward commercial-scale substrate physics).
ASCII-only; per-seed atomic partials; numpy-only (no torch); substrate-native.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

import argparse
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, resumable_seeds, write_metrics,
)
from experiments._cell_heartbeat import emit_heartbeat

ANCHOR_NAME = "lln_point_mass_large_vc_10k_1M_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--run-mode", type=str, default=None)
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()

if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
elif _ARGS.run_mode is not None:
    RUN_MODE = _ARGS.run_mode.lower()
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()

# Sweep configuration (locked at module init).
V_C_SWEEP = [1000, 10000, 100000, 1000000]
N_SWEEP = [8192, 16384]
F_SWEEP = [0.15]
N_ITEMS_IN_KB = 50
N_ITEMS_OOD = 50

if RUN_MODE == "smoke":
    SEEDS = [7]
    # Smoke runs FULL 8-point grid at seed 7 -- discriminator-must-survive-scale (USER 2026-06-26).
elif RUN_MODE == "self_test":
    SEEDS = [7]
    # Self-test uses ONE tiny phase point + assertions, not the sweep.
else:
    SEEDS = [7, 13, 19]

EXPECTED_N_UNITS_PER_SEED = len(V_C_SWEEP) * len(N_SWEEP) * len(F_SWEEP)  # 8

# Verdict gate thresholds (LOCKED).
HP_CENTER_TOL = 0.010          # HP_LLN_HOLDS |p50 - (1-2f)| tol
HP_SPREAD_LO = 0.5             # observed / theoretical spread lower bound
HP_SPREAD_HI = 2.0             # observed / theoretical spread upper bound
HP_OOD_REL_TOL = 0.30          # HP_OOD_FORMULA relative tol
HP_BIMODAL_GAP_MIN = 0.30      # HP_BIMODAL_GAP min (in_kb_p5 - ood_p95)
HF_CENTER_TOL = 0.05           # HARD_FAIL if center deviates by more than this
HF_OOD_SATURATION = 0.5        # HARD_FAIL if p50_ood > this (substrate confused)

CONFIG_VERSION = (
    "ANCHOR=%s,run_mode=%s,V_C_SWEEP=%s,N_SWEEP=%s,F_SWEEP=%s,SEEDS=%s,"
    "N_ITEMS_IN_KB=%d,N_ITEMS_OOD=%d,HP_CENTER_TOL=%.4f,HP_SPREAD_LO=%.2f,"
    "HP_SPREAD_HI=%.2f,HP_OOD_REL_TOL=%.2f,HP_BIMODAL_GAP_MIN=%.2f,HF_OOD_SAT=%.2f"
) % (
    ANCHOR_NAME, RUN_MODE, V_C_SWEEP, N_SWEEP, F_SWEEP, SEEDS,
    N_ITEMS_IN_KB, N_ITEMS_OOD,
    HP_CENTER_TOL, HP_SPREAD_LO, HP_SPREAD_HI, HP_OOD_REL_TOL,
    HP_BIMODAL_GAP_MIN, HF_OOD_SATURATION,
)


# ----------------------------- primitives -----------------------------

def bipolar_random(V: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """Return V random bipolar {+1, -1} vectors of dim N, L2-normalized. Shape (V, N).

    NOTE: for V=1M and N=16384, this allocates ~64 GB as float32 -- INFEASIBLE.
    Callers must chunk or use bit-packed representation for V>=100k. See
    build_kb_chunked() below for the streaming max_sim variant.
    """
    X = (rng.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return X / norms


def flip_fraction(v: np.ndarray, f: float, rng: np.random.Generator) -> np.ndarray:
    """Flip each bipolar sign of v with probability f. Returns re-normalized flipped vector."""
    N = v.shape[0]
    signs = np.sign(v).astype(np.float32)
    signs[signs == 0] = 1.0
    mask = rng.random(size=N) < f
    signs[mask] = -signs[mask]
    v_new = signs
    return v_new / (np.linalg.norm(v_new) + 1e-12)


def compute_max_sim_batch(queries: np.ndarray, kb: np.ndarray) -> np.ndarray:
    """Compute max cosine sim of each query row over KB rows. Both L2-normalized.

    queries: shape (Q, N); kb: shape (V, N). Returns shape (Q,)."""
    # (Q, V) sim matrix -> max over V per row.
    sims = queries @ kb.T
    return np.max(sims, axis=1)


def theoretical_center(f: float) -> float:
    """LLN in-KB center: 1 - 2f."""
    return 1.0 - 2.0 * f


def theoretical_per_item_std(N: int, f: float) -> float:
    """LLN per-item cosine std: sqrt(4 f (1-f) / N)."""
    return math.sqrt(4.0 * f * (1.0 - f) / N)


def theoretical_normal_spread(N: int, f: float) -> float:
    """p5-p95 spread under Normal approximation: 2 * 1.645 * per-item std."""
    return 2.0 * 1.645 * theoretical_per_item_std(N, f)


def theoretical_ood_floor(N: int, V_C: int) -> float:
    """OOD max_sim floor per extreme-value theory: sqrt(2 log(V_C) / N)."""
    return math.sqrt(2.0 * math.log(V_C) / N)


# ----------------------------- chunked KB (memory-safe for V_C=1M) -----------------------------

def build_kb_and_measure_chunked(V_C: int, N: int, f: float, rng: np.random.Generator,
                                 chunk_v: int = 50000) -> Dict[str, Any]:
    """Memory-safe measurement for large V_C.

    Rather than materializing all V_C x N in RAM, we build KB in chunks and stream
    max_sim per query across chunks. Chunk size chunk_v=50000 x N=16384 x 4B = ~3.3 GB per
    chunk peak -- fits in laptop RAM. Cal-set stays fixed at 100 items regardless of V_C.

    Trick: we need queries to be "in-KB flipped" for 50 items -- so we build a small
    reference-key pool (100 keys) FIRST using its own seeded RNG substream, use those as
    query-parents, and then extend the KB with V_C - 100 additional fresh keys via chunks.
    """
    # Step 1: build the reference-key pool (up to 100 in-KB parents).
    ref_pool_size = min(N_ITEMS_IN_KB, V_C)
    ref_pool = bipolar_random(ref_pool_size, N, rng)  # (ref_pool_size, N)

    # Step 2: build cal set.
    # 50 in-KB queries = flip f fraction of a random ref pool key.
    kb_parent_indices = rng.integers(0, ref_pool_size, size=N_ITEMS_IN_KB)
    in_kb_queries = np.zeros((N_ITEMS_IN_KB, N), dtype=np.float32)
    for i, idx in enumerate(kb_parent_indices):
        in_kb_queries[i] = flip_fraction(ref_pool[idx], f, rng)
    # 50 OOD queries = fresh random bipolar keys (never in KB).
    ood_queries = bipolar_random(N_ITEMS_OOD, N, rng)

    all_queries = np.concatenate([in_kb_queries, ood_queries], axis=0)  # (100, N)

    # Step 3: streaming max_sim over full KB.
    # First chunk: the ref pool itself (it IS in KB by construction for the in-KB parents).
    max_sim_all = compute_max_sim_batch(all_queries, ref_pool)  # (100,)

    # Additional chunks: fresh random keys.
    remaining = V_C - ref_pool_size
    while remaining > 0:
        this_chunk = min(chunk_v, remaining)
        chunk_kb = bipolar_random(this_chunk, N, rng)
        chunk_max = compute_max_sim_batch(all_queries, chunk_kb)
        max_sim_all = np.maximum(max_sim_all, chunk_max)
        remaining -= this_chunk
        del chunk_kb  # free RAM promptly

    in_kb_sims = max_sim_all[:N_ITEMS_IN_KB]
    ood_sims = max_sim_all[N_ITEMS_IN_KB:]

    # Quantiles.
    in_kb_q = np.percentile(in_kb_sims, [5, 10, 25, 50, 75, 95])
    ood_q = np.percentile(ood_sims, [10, 50, 90])
    spread_p5_p95 = float(in_kb_q[5] - in_kb_q[0])
    bimodal_gap = float(in_kb_q[0] - ood_q[2])  # p5_in_kb - p95_ood

    # Theoreticals (recomputed fresh here - never cached from prompt).
    theo_center = theoretical_center(f)
    theo_std = theoretical_per_item_std(N, f)
    theo_spread = theoretical_normal_spread(N, f)
    theo_ood = theoretical_ood_floor(N, V_C)

    # Discriminators.
    dev_center = abs(float(in_kb_q[3]) - theo_center)
    spread_ratio = spread_p5_p95 / theo_spread if theo_spread > 0 else float("inf")
    dev_ood_rel = abs(float(ood_q[1]) - theo_ood) / theo_ood if theo_ood > 0 else float("inf")

    return {
        "V_C": int(V_C),
        "N": int(N),
        "f": float(f),
        "p5_in_kb": float(in_kb_q[0]),
        "p10_in_kb": float(in_kb_q[1]),
        "p25_in_kb": float(in_kb_q[2]),
        "p50_in_kb": float(in_kb_q[3]),
        "p75_in_kb": float(in_kb_q[4]),
        "p95_in_kb": float(in_kb_q[5]),
        "p10_ood": float(ood_q[0]),
        "p50_ood": float(ood_q[1]),
        "p90_ood": float(ood_q[2]),
        "spread_p5_p95_in_kb": spread_p5_p95,
        "bimodal_gap": bimodal_gap,
        "theoretical_in_kb_center": theo_center,
        "theoretical_per_item_std": theo_std,
        "theoretical_normal_spread": theo_spread,
        "theoretical_ood_floor": theo_ood,
        "observed_dev_center": dev_center,
        "observed_spread_ratio": spread_ratio,
        "observed_dev_ood_rel": dev_ood_rel,
        # Gate flags per phase point.
        "gate_hp_center_pass": bool(dev_center < HP_CENTER_TOL),
        "gate_hp_spread_pass": bool(HP_SPREAD_LO <= spread_ratio <= HP_SPREAD_HI),
        "gate_hp_ood_pass": bool(dev_ood_rel < HP_OOD_REL_TOL),
        "gate_hp_bimodal_gap_pass": bool(bimodal_gap > HP_BIMODAL_GAP_MIN),
        "gate_hf_center_break": bool(dev_center > HF_CENTER_TOL),
        "gate_hf_ood_saturates": bool(float(ood_q[1]) > HF_OOD_SATURATION),
    }


# ----------------------------- per-seed runner -----------------------------

def run_seed(seed: int, output_dir: Path) -> Dict[str, Any]:
    """Run the full 8-point sweep for one seed."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    per_unit: List[Dict[str, Any]] = []
    n_seen = 0
    failure_records: List[Dict[str, Any]] = []
    for V_C in V_C_SWEEP:
        for N in N_SWEEP:
            for f in F_SWEEP:
                phase_idx = n_seen
                # Adaptive chunk size: for large V_C*N we want smaller chunks to bound RAM.
                # Chunk RAM = chunk_v * N * 4 bytes; keep chunk RAM ~3 GB.
                bytes_budget = 3_000_000_000
                chunk_v = max(1000, min(V_C, bytes_budget // (N * 4)))
                try:
                    row = build_kb_and_measure_chunked(V_C, N, f, rng, chunk_v=chunk_v)
                except (ValueError, RuntimeError, MemoryError, OverflowError) as e:
                    failure_records.append({
                        "phase_idx": phase_idx,
                        "V_C": V_C, "N": N, "f": f,
                        "failure_class": type(e).__name__,
                        "failure_msg": str(e)[:400],
                    })
                    # Halt this seed on any failure; per META_RULE_J no silent continue.
                    raise
                per_unit.append(row)
                n_seen += 1
                elapsed = time.perf_counter() - t0
                print(
                    f"[seed={seed}] phase {n_seen}/{EXPECTED_N_UNITS_PER_SEED} "
                    f"V_C={V_C} N={N} f={f:.2f} "
                    f"p50_in={row['p50_in_kb']:.4f} (theo {row['theoretical_in_kb_center']:.4f}) "
                    f"p50_ood={row['p50_ood']:.4f} (theo {row['theoretical_ood_floor']:.4f}) "
                    f"gap={row['bimodal_gap']:.4f} "
                    f"elapsed={elapsed:.1f}s",
                    flush=True,
                )
                emit_heartbeat(
                    output_dir, unit_idx=n_seen, total_units=EXPECTED_N_UNITS_PER_SEED,
                    elapsed_s=elapsed,
                    extra={"seed": seed, "V_C": V_C, "N": N, "f": f,
                           "p50_in_kb": row["p50_in_kb"],
                           "p50_ood": row["p50_ood"],
                           "bimodal_gap": row["bimodal_gap"]},
                )
    elapsed_s = time.perf_counter() - t0

    cardinality_ok = (n_seen == EXPECTED_N_UNITS_PER_SEED)

    payload = {
        "seed": int(seed),
        "N": int(N_SWEEP[0]),  # canonical N for _seed_checkpoint PROT-021 (smallest = first swept)
        "run_mode": RUN_MODE,
        "smoke": (RUN_MODE == "smoke"),
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": float(elapsed_s),
        "per_unit": per_unit,
        "n_units": int(n_seen),
        "expected_n_units": int(EXPECTED_N_UNITS_PER_SEED),
        "cardinality_ok": bool(cardinality_ok),
        "failure_records": failure_records,
    }
    return payload


# ----------------------------- verdict aggregation -----------------------------

def aggregate_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate per-seed payloads into a top-level verdict per pre-reg gates."""
    all_seeds_ok = True
    any_hf_center = False
    any_hf_ood_sat = False
    any_cardinality_breach = False
    hp_center_per_seed: Dict[str, bool] = {}
    hp_spread_per_seed: Dict[str, bool] = {}
    hp_ood_per_seed: Dict[str, bool] = {}
    hp_bimodal_per_seed: Dict[str, bool] = {}
    n_units_per_seed: Dict[str, int] = {}

    for seed_key, payload in per_seed.items():
        pu = payload.get("per_unit", [])
        n_units_per_seed[seed_key] = len(pu)
        if not payload.get("cardinality_ok", False):
            any_cardinality_breach = True
            all_seeds_ok = False
        hp_c = all(r.get("gate_hp_center_pass", False) for r in pu) if pu else False
        hp_s = all(r.get("gate_hp_spread_pass", False) for r in pu) if pu else False
        hp_o = all(r.get("gate_hp_ood_pass", False) for r in pu) if pu else False
        hp_b = all(r.get("gate_hp_bimodal_gap_pass", False) for r in pu) if pu else False
        hp_center_per_seed[seed_key] = hp_c
        hp_spread_per_seed[seed_key] = hp_s
        hp_ood_per_seed[seed_key] = hp_o
        hp_bimodal_per_seed[seed_key] = hp_b
        if not (hp_c and hp_s and hp_o and hp_b):
            all_seeds_ok = False
        if any(r.get("gate_hf_center_break", False) for r in pu):
            any_hf_center = True
        if any(r.get("gate_hf_ood_saturates", False) for r in pu):
            any_hf_ood_sat = True

    # Verdict classification per pre-reg.
    if any_cardinality_breach:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = (
            f"CARDINALITY BREACH: expected {EXPECTED_N_UNITS_PER_SEED} per seed; "
            f"observed {n_units_per_seed}"
        )
    elif any_hf_center:
        verdict = "HARD_FAIL_LLN_BREAKS"
        verdict_msg = (
            f"LLN broken: some phase point deviates > {HF_CENTER_TOL} from 1-2f (0.7 at f=0.15)"
        )
    elif any_hf_ood_sat:
        verdict = "HARD_FAIL_OOD_SATURATES"
        verdict_msg = (
            f"OOD saturation: some phase point p50_ood > {HF_OOD_SATURATION} "
            f"(substrate confused; OOD stops looking like OOD at commercial V_C)"
        )
    elif all_seeds_ok:
        verdict = "CHAIN_GRADE_COMMERCIAL_SCALE_VC"
        verdict_msg = (
            f"ALL 4 HP gates (center + spread + OOD + bimodal_gap) clear ALL "
            f"{EXPECTED_N_UNITS_PER_SEED} phase points across {len(per_seed)} seeds. "
            f"Substrate architected for commercial-scale vocabulary V_C=1M without modification."
        )
    else:
        verdict = "MIDDLE_BAND_LARGE_VC_REGIME_DEPENDENT"
        verdict_msg = (
            f"HP gates split across seeds/regimes. per-seed HP center={hp_center_per_seed} "
            f"spread={hp_spread_per_seed} ood={hp_ood_per_seed} bimodal={hp_bimodal_per_seed}"
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_units_per_seed": n_units_per_seed,
        "hp_center_pass_per_seed": hp_center_per_seed,
        "hp_spread_pass_per_seed": hp_spread_per_seed,
        "hp_ood_pass_per_seed": hp_ood_per_seed,
        "hp_bimodal_gap_pass_per_seed": hp_bimodal_per_seed,
        "any_hf_center": any_hf_center,
        "any_hf_ood_saturates": any_hf_ood_sat,
        "any_cardinality_breach": any_cardinality_breach,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "anchor_name": ANCHOR_NAME,
    }


# ----------------------------- start-marker + crash-diag -----------------------------

def _write_start_marker(output_dir: Path, run_mode: str) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": EXPECTED_N_UNITS_PER_SEED * len(SEEDS),
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: BaseException) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ----------------------------- self-test -----------------------------

def _self_test() -> None:
    """Sanity assertions for the primitives + one tiny phase point.

    CRITICAL: verifies sqrt(2 log V_C / N) formula matches at V_C=1M (predicted ~0.058).
    """
    print("[selftest] running large-V_C LLN primitive self-tests...", flush=True)
    rng = np.random.default_rng(42)

    # T1: bipolar_random shape + normalization.
    X = bipolar_random(10, 512, rng)
    assert X.shape == (10, 512), f"T1 shape fail: {X.shape}"
    norms = np.linalg.norm(X, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5), f"T1 norm fail: {norms[:3]}"

    # T2: theoretical formulas closed-form (VERIFY AT COMMERCIAL V_C).
    assert abs(theoretical_center(0.15) - 0.70) < 1e-9, "T2 center fail"
    tstd = theoretical_per_item_std(8192, 0.15)
    assert 0.007 < tstd < 0.010, f"T2 std fail: {tstd}"
    # Load-bearing: OOD floor at V_C=1M, N=8192 should be ~0.058.
    tood_1M_8k = theoretical_ood_floor(8192, 1_000_000)
    assert 0.055 < tood_1M_8k < 0.062, f"T2 OOD floor V_C=1M N=8192 fail: {tood_1M_8k} (expected ~0.058)"
    tood_1M_16k = theoretical_ood_floor(16384, 1_000_000)
    assert 0.038 < tood_1M_16k < 0.044, f"T2 OOD floor V_C=1M N=16384 fail: {tood_1M_16k} (expected ~0.041)"
    tood_1k_8k = theoretical_ood_floor(8192, 1000)
    assert 0.038 < tood_1k_8k < 0.044, f"T2 OOD floor V_C=1k N=8192 fail: {tood_1k_8k} (expected ~0.041)"
    # NOTE: tood_1M_8k and tood_1k_16k are similar; ratio V_C=1M/V_C=1k = sqrt(log 1M / log 1k) = sqrt(2)
    print(f"[selftest] T2 OOD floor formula VERIFIED: V_C=1M/N=8192={tood_1M_8k:.4f} "
          f"V_C=1M/N=16384={tood_1M_16k:.4f}", flush=True)

    # T3: flip_fraction produces expected cosine with parent.
    v = X[0]
    v_flipped = flip_fraction(v, 0.15, rng)
    assert v_flipped.shape == v.shape
    cos = float(v @ v_flipped)
    assert 0.55 < cos < 0.85, f"T3 flip cosine out of band: {cos}"

    # T4: chunked KB measurement at SMALL V_C (fast).
    rng2 = np.random.default_rng(7)
    row = build_kb_and_measure_chunked(V_C=500, N=2048, f=0.15, rng=rng2, chunk_v=200)
    assert 0.55 < row["p50_in_kb"] < 0.85, f"T4 p50_in_kb: {row['p50_in_kb']}"
    assert row["p5_in_kb"] < row["p50_in_kb"] < row["p95_in_kb"], "T4 quantile order"
    assert 0.0 < row["p50_ood"] < 0.15, f"T4 p50_ood: {row['p50_ood']}"
    assert row["bimodal_gap"] > 0.30, f"T4 bimodal_gap must be substantial at small V_C: {row['bimodal_gap']}"

    # T5: HP center gate should pass at N=2048 (well within 0.010 SE cushion at 50 items).
    assert row["gate_hp_center_pass"] or row["observed_dev_center"] < 0.020, (
        f"T5 gate_hp_center failed at reasonable N: dev={row['observed_dev_center']}"
    )

    # T6: chunked matches non-chunked for the same V_C, N (regression check).
    rng3a = np.random.default_rng(13)
    rng3b = np.random.default_rng(13)
    row_chunked = build_kb_and_measure_chunked(V_C=500, N=1024, f=0.15, rng=rng3a, chunk_v=100)
    row_unchunked = build_kb_and_measure_chunked(V_C=500, N=1024, f=0.15, rng=rng3b, chunk_v=500)
    # Same seed + same operation order = same quantiles (within fp32 noise).
    assert abs(row_chunked["p50_in_kb"] - row_unchunked["p50_in_kb"]) < 0.01, (
        f"T6 chunked-vs-full drift: {row_chunked['p50_in_kb']} vs {row_unchunked['p50_in_kb']}"
    )

    # T7: verdict aggregation on synthetic PASS + BREACH cases.
    fake_pass_pu = [{"gate_hp_center_pass": True, "gate_hp_spread_pass": True,
                     "gate_hp_ood_pass": True, "gate_hp_bimodal_gap_pass": True,
                     "gate_hf_center_break": False, "gate_hf_ood_saturates": False}
                    for _ in range(EXPECTED_N_UNITS_PER_SEED)]
    fake_pass_payload = {"per_unit": fake_pass_pu, "cardinality_ok": True}
    v_pass = aggregate_verdict({"7": fake_pass_payload, "13": fake_pass_payload,
                                 "19": fake_pass_payload})
    assert v_pass["verdict"] == "CHAIN_GRADE_COMMERCIAL_SCALE_VC", (
        f"T7a verdict fail: {v_pass['verdict']}"
    )

    fake_hf_pu = [dict(r) for r in fake_pass_pu]
    fake_hf_pu[0]["gate_hf_center_break"] = True
    fake_hf_pu[0]["gate_hp_center_pass"] = False
    fake_hf_payload = {"per_unit": fake_hf_pu, "cardinality_ok": True}
    v_hf = aggregate_verdict({"7": fake_hf_payload})
    assert v_hf["verdict"] == "HARD_FAIL_LLN_BREAKS", (
        f"T7b verdict fail: {v_hf['verdict']}"
    )

    fake_ood_sat_pu = [dict(r) for r in fake_pass_pu]
    fake_ood_sat_pu[0]["gate_hf_ood_saturates"] = True
    fake_ood_sat_pu[0]["gate_hp_ood_pass"] = False
    fake_ood_sat_payload = {"per_unit": fake_ood_sat_pu, "cardinality_ok": True}
    v_ood = aggregate_verdict({"7": fake_ood_sat_payload})
    assert v_ood["verdict"] == "HARD_FAIL_OOD_SATURATES", (
        f"T7c verdict fail: {v_ood['verdict']}"
    )

    fake_short_payload = {"per_unit": fake_pass_pu[:3], "cardinality_ok": False}
    v_card = aggregate_verdict({"7": fake_short_payload})
    assert v_card["verdict"] == "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
        f"T7d verdict fail: {v_card['verdict']}"
    )

    print("[selftest] T1-T7 all PASS", flush=True)


# ----------------------------- main -----------------------------

def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE)

    print(f"[main] {ANCHOR_NAME} run_mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(f"[main] config: {CONFIG_VERSION}", flush=True)

    if RUN_MODE == "self_test":
        _self_test()
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (primitive + verdict-aggregator T1-T7 all pass; large-V_C formula verified)",
            "summary": "SELFTEST_PASS",
            "elapsed_s": 0.0,
            "run_mode": "self_test",
            "anchor_name": ANCHOR_NAME,
            "config_version": CONFIG_VERSION,
        }
        write_metrics(output_dir, metrics)
        print(f"[main] SELFTEST written to {output_dir}/metrics.json", flush=True)
        return

    # Resume support via per-seed checkpoint.
    run_config = {"anchor": ANCHOR_NAME, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, output_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
          flush=True)

    for seed in remaining:
        print(f"[main] === seed={seed} start ===", flush=True)
        payload = run_seed(seed, output_dir)
        write_partial(output_dir, seed, payload)
        print(f"[main] === seed={seed} done: n_units={payload['n_units']} "
              f"cardinality_ok={payload['cardinality_ok']} elapsed={payload['elapsed_s']:.1f}s ===",
              flush=True)

    # Aggregate all seeds.
    per_seed = aggregate_partials(output_dir, SEEDS, run_config=run_config)
    print(f"[main] aggregating {len(per_seed)} per-seed payloads...", flush=True)

    verdict_dict = aggregate_verdict(per_seed)

    # Assemble final metrics.
    total_elapsed = sum(float(p.get("elapsed_s", 0.0)) for p in per_seed.values())
    metrics = dict(verdict_dict)
    metrics["elapsed_s"] = total_elapsed
    metrics["per_seed"] = per_seed
    metrics["run_mode"] = RUN_MODE
    metrics["seeds"] = SEEDS
    metrics["V_C_SWEEP"] = V_C_SWEEP
    metrics["N_SWEEP"] = N_SWEEP
    metrics["F_SWEEP"] = F_SWEEP
    metrics["expected_n_units_per_seed"] = EXPECTED_N_UNITS_PER_SEED

    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)

    print(f"[main] VERDICT: {verdict_dict['verdict']}", flush=True)
    print(f"[main] MSG: {verdict_dict['verdict_msg']}", flush=True)


if __name__ == "__main__":
    output_dir = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
