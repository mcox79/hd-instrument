"""lln_point_mass_verification_N_V_C_f_sweep_v1 -- lift Atom 12 (LLN point-mass on in-KB max_sim) to CG.

PROMOTION CONTEXT (2026-07-01):
  Atom 12 MM (Skunkworks 2026-07-01): in-KB max_sim is a POINT MASS at 1-2f at high-dim bipolar
  FHRR (LLN concentration). Established at (N=8192, V_C=200, f=0.15). To lift to CG, need to show
  the property is a GENERAL substrate physics feature, not a specific-config artifact.

DESIGN: 3-axis sweep (N x V_C x f)
  N in {4096, 8192, 16384} (3 values)
  V_C in {100, 200, 400} (3 values)
  f in {0.05, 0.10, 0.15, 0.20, 0.30} (5 values)
  = 45 phase points per seed x 3 seeds [7, 13, 19] = 135 units total

PROTOCOL per (N, V_C, f):
  1. Build KB of V_C bipolar keys + V_C bipolar values.
  2. Build 100-item cal set: 50 in-KB (KB key + f-fraction bit flip) + 50 OOD (random keys).
  3. Compute max_sim over V_C KB per item.
  4. Record quantiles: p5/p10/p25/p50/p75/p95 (in-KB); p10/p50/p90 (OOD).
  5. Compute spread_p5_p95, theoretical_center=1-2f, theoretical_ood_floor=sqrt(2 log(V_C) / N).

VERDICT GATES (see prereg for full reasoning):
  HP_LLN_CENTER_VERIFIED: |p50_in_kb - (1-2f)| < 0.010 for ALL 45 points per seed
  HP_LLN_SPREAD_SCALING: 0.5 <= observed_spread / theoretical_normal_spread <= 2.0 for ALL 45 points
    where theoretical_normal_spread = 2 * 1.645 * sqrt(4 f (1-f) / N)
  HP_OOD_FLOOR_SCALING: |p50_ood - theoretical_ood_floor| / theoretical_ood_floor < 0.30 for ALL 45
  CHAIN_GRADE if ALL 3 HP gates clear ALL 45 points across ALL 3 seeds.
  MIDDLE_BAND if some N pass but not others.
  HARD_FAIL_LLN_BROKEN if any p50_in_kb deviates > 0.05 from 1-2f.
  HARD_FAIL_OOD_SCALING_BROKEN if any OOD floor is >2x or <0.5x theoretical.
  HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if any seed produces != 45 phase points.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: implicit (sweep produces distinct spreads across N by design)
- final_metrics_atomicity: per_iter_paths (per-seed _seed_checkpoint partials)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: "LLN concentration cell; discriminator is spread-scaling not CRLB floor"
- baseline_in_band: N/A (no baseline arm; each point self-witnesses)
- discriminator survives scale: smoke runs FULL 45-point grid at seed 7
- HARD_PASS strictly above floor + 5%: center gate 0.010 is ~5x per-p50 SE
- HP_SCOPE: all 45 phase points get all 3 HP gates
- cardinality_ok: EXPECTED_N_UNITS=45 per seed; HF if breached
- per-unit failure-class instrumentation: specific-exception catch + failure_class field
- calibration_check: adaptive_with_discriminator_gate (spread gate uses closed-form 1/sqrt(N))
- all numbers tagged: MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ per META_RULE_AC

Author: exp_dev 2026-07-01 (Atom 12 lift to CG).
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
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, resumable_seeds, write_metrics,
)
from experiments._cell_heartbeat import emit_heartbeat

ANCHOR_NAME = "lln_point_mass_verification_N_V_C_f_sweep_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ap.add_argument("--run-mode", type=str, default=None)
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()

# Explicit run_mode selection with default = full (per template §16 defensive default).
if _ARGS.self_test:
    RUN_MODE = "self_test"
elif _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
elif _ARGS.run_mode is not None:
    RUN_MODE = _ARGS.run_mode.lower()
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()

# Sweep configuration (locked at module init).
N_SWEEP = [4096, 8192, 16384]
V_C_SWEEP = [100, 200, 400]
F_SWEEP = [0.05, 0.10, 0.15, 0.20, 0.30]
N_ITEMS_IN_KB = 50
N_ITEMS_OOD = 50

if RUN_MODE == "smoke":
    SEEDS = [7]
    # Smoke runs FULL 45-point grid at seed 7 -- discriminator-must-survive-scale (Section 68).
elif RUN_MODE == "self_test":
    SEEDS = [7]
    # Self-test uses ONE tiny phase point + assertions, not the sweep.
else:
    SEEDS = [7, 13, 19]

EXPECTED_N_UNITS_PER_SEED = len(N_SWEEP) * len(V_C_SWEEP) * len(F_SWEEP)  # 45

# Verdict gate thresholds (LOCKED).
HP_CENTER_TOL = 0.010          # HP_LLN_CENTER_VERIFIED tol on |p50 - (1-2f)|
HP_SPREAD_LO = 0.5             # observed / theoretical spread lower bound
HP_SPREAD_HI = 2.0             # observed / theoretical spread upper bound
HP_OOD_REL_TOL = 0.30          # HP_OOD_FLOOR_SCALING relative tol
HF_CENTER_TOL = 0.05           # HARD_FAIL if center deviates by more than this
HF_OOD_LO = 0.5                # HARD_FAIL if observed_ood < 0.5x theoretical
HF_OOD_HI = 2.0                # HARD_FAIL if observed_ood > 2.0x theoretical

CONFIG_VERSION = (
    "ANCHOR=%s,run_mode=%s,N_SWEEP=%s,V_C_SWEEP=%s,F_SWEEP=%s,SEEDS=%s,"
    "N_ITEMS_IN_KB=%d,N_ITEMS_OOD=%d,HP_CENTER_TOL=%.4f,HP_SPREAD_LO=%.2f,"
    "HP_SPREAD_HI=%.2f,HP_OOD_REL_TOL=%.2f"
) % (
    ANCHOR_NAME, RUN_MODE, N_SWEEP, V_C_SWEEP, F_SWEEP, SEEDS,
    N_ITEMS_IN_KB, N_ITEMS_OOD,
    HP_CENTER_TOL, HP_SPREAD_LO, HP_SPREAD_HI, HP_OOD_REL_TOL,
)


# ----------------------------- primitives -----------------------------

def bipolar_random(V: int, N: int, rng: np.random.Generator) -> np.ndarray:
    """Return V random bipolar {+1, -1} vectors of dim N, L2-normalized. Shape (V, N)."""
    X = (rng.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    norms = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return X / norms


def flip_fraction(v: np.ndarray, f: float, rng: np.random.Generator) -> np.ndarray:
    """Flip each bipolar sign of v (a normalized bipolar vector, N-dim) with probability f.
    Returns re-normalized flipped vector. Preserves sign structure appropriately."""
    N = v.shape[0]
    # Recover approximate original signs from normalized vector.
    signs = np.sign(v).astype(np.float32)
    # Handle zero components (unlikely in bipolar but defensive).
    signs[signs == 0] = 1.0
    mask = rng.random(size=N) < f
    signs[mask] = -signs[mask]
    # Re-normalize
    v_new = signs
    return v_new / (np.linalg.norm(v_new) + 1e-12)


def compute_max_sim(query: np.ndarray, kb: np.ndarray) -> float:
    """Compute max cosine similarity between query (N,) and KB (V, N). Both L2-normalized."""
    # kb @ query -> (V,) since both normalized -> dot = cosine
    sims = kb @ query
    return float(np.max(sims))


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


# ----------------------------- per-phase-point measurement -----------------------------

def measure_phase_point(N: int, V_C: int, f: float, seed_offset: int,
                        rng: np.random.Generator) -> Dict[str, Any]:
    """Run one phase point: build KB, cal set, compute max_sim, return quantiles + theoreticals.

    Returns dict with all MEASURED and THEORETICAL fields per the pre-reg protocol.
    """
    # Build KB (V_C keys of dim N).
    kb = bipolar_random(V_C, N, rng)

    # Build 50 in-KB queries: pick a random KB key, flip f fraction of its signs, re-normalize.
    in_kb_sims = np.zeros(N_ITEMS_IN_KB, dtype=np.float32)
    kb_indices = rng.integers(0, V_C, size=N_ITEMS_IN_KB)
    for i, idx in enumerate(kb_indices):
        q = flip_fraction(kb[idx], f, rng)
        in_kb_sims[i] = compute_max_sim(q, kb)

    # Build 50 OOD queries: fresh random bipolar keys (never in KB).
    ood_queries = bipolar_random(N_ITEMS_OOD, N, rng)
    ood_sims = np.zeros(N_ITEMS_OOD, dtype=np.float32)
    for i in range(N_ITEMS_OOD):
        ood_sims[i] = compute_max_sim(ood_queries[i], kb)

    # Quantiles.
    in_kb_q = np.percentile(in_kb_sims, [5, 10, 25, 50, 75, 95])
    ood_q = np.percentile(ood_sims, [10, 50, 90])
    spread_p5_p95 = float(in_kb_q[5] - in_kb_q[0])

    # Theoreticals (recomputed fresh here — never cached from prompt).
    theo_center = theoretical_center(f)
    theo_std = theoretical_per_item_std(N, f)
    theo_spread = theoretical_normal_spread(N, f)
    theo_ood = theoretical_ood_floor(N, V_C)

    # Discriminators.
    dev_center = abs(float(in_kb_q[3]) - theo_center)          # p50 minus 1-2f
    spread_ratio = spread_p5_p95 / theo_spread if theo_spread > 0 else float("inf")
    dev_ood_rel = abs(float(ood_q[1]) - theo_ood) / theo_ood if theo_ood > 0 else float("inf")

    return {
        "N": int(N),
        "V_C": int(V_C),
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
        "gate_hf_center_break": bool(dev_center > HF_CENTER_TOL),
        "gate_hf_ood_break": bool(dev_ood_rel > HF_OOD_HI - 1.0),
        # Detailed HF classification for OOD (spawn wanted specific >2x / <0.5x split).
        "gate_hf_ood_ratio_break": bool(
            (float(ood_q[1]) / theo_ood > HF_OOD_HI) or (float(ood_q[1]) / theo_ood < HF_OOD_LO)
        ) if theo_ood > 0 else True,
    }


# ----------------------------- per-seed runner -----------------------------

def run_seed(seed: int, output_dir: Path) -> Dict[str, Any]:
    """Run the full 45-point sweep for one seed."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    per_unit: List[Dict[str, Any]] = []
    n_seen = 0
    failure_records: List[Dict[str, Any]] = []
    for N in N_SWEEP:
        for V_C in V_C_SWEEP:
            for f in F_SWEEP:
                phase_idx = n_seen
                try:
                    row = measure_phase_point(N, V_C, f, phase_idx, rng)
                except (ValueError, RuntimeError, MemoryError, OverflowError) as e:
                    failure_records.append({
                        "phase_idx": phase_idx,
                        "N": N, "V_C": V_C, "f": f,
                        "failure_class": type(e).__name__,
                        "failure_msg": str(e)[:400],
                    })
                    # Halt this seed on any failure; per META_RULE_J no silent continue.
                    raise
                per_unit.append(row)
                n_seen += 1
                elapsed = time.perf_counter() - t0
                if n_seen % 5 == 0 or n_seen == EXPECTED_N_UNITS_PER_SEED:
                    print(
                        f"[seed={seed}] phase {n_seen}/{EXPECTED_N_UNITS_PER_SEED} "
                        f"N={N} V_C={V_C} f={f:.2f} p50_in={row['p50_in_kb']:.4f} "
                        f"(theo {row['theoretical_in_kb_center']:.4f}) "
                        f"spread={row['spread_p5_p95_in_kb']:.4f} "
                        f"(theo {row['theoretical_normal_spread']:.4f}) "
                        f"elapsed={elapsed:.1f}s",
                        flush=True,
                    )
                    emit_heartbeat(
                        output_dir, unit_idx=n_seen, total_units=EXPECTED_N_UNITS_PER_SEED,
                        elapsed_s=elapsed,
                        extra={"seed": seed, "N": N, "V_C": V_C, "f": f,
                               "p50_in_kb": row["p50_in_kb"],
                               "theo_center": row["theoretical_in_kb_center"]},
                    )
    elapsed_s = time.perf_counter() - t0

    # Cardinality gate.
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
    any_hf_ood = False
    any_cardinality_breach = False
    hp_center_pass_per_seed: Dict[str, bool] = {}
    hp_spread_pass_per_seed: Dict[str, bool] = {}
    hp_ood_pass_per_seed: Dict[str, bool] = {}
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
        hp_center_pass_per_seed[seed_key] = hp_c
        hp_spread_pass_per_seed[seed_key] = hp_s
        hp_ood_pass_per_seed[seed_key] = hp_o
        if not (hp_c and hp_s and hp_o):
            all_seeds_ok = False
        if any(r.get("gate_hf_center_break", False) for r in pu):
            any_hf_center = True
        if any(r.get("gate_hf_ood_ratio_break", False) for r in pu):
            any_hf_ood = True

    # Verdict classification per pre-reg.
    if any_cardinality_breach:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
        verdict_msg = (
            f"CARDINALITY BREACH: expected {EXPECTED_N_UNITS_PER_SEED} per seed; "
            f"observed {n_units_per_seed}"
        )
    elif any_hf_center:
        verdict = "HARD_FAIL_LLN_BROKEN"
        verdict_msg = (
            f"LLN center broken: some phase point deviates > {HF_CENTER_TOL} from 1-2f"
        )
    elif any_hf_ood:
        verdict = "HARD_FAIL_OOD_SCALING_BROKEN"
        verdict_msg = (
            f"OOD scaling broken: some phase point OOD/theoretical ratio outside "
            f"[{HF_OOD_LO}, {HF_OOD_HI}]"
        )
    elif all_seeds_ok:
        verdict = "CHAIN_GRADE_LLN_POINT_MASS_VERIFIED"
        verdict_msg = (
            f"ALL 3 HP gates clear ALL {EXPECTED_N_UNITS_PER_SEED} phase points "
            f"across {len(per_seed)} seeds. Atom 12 lifts to CG."
        )
    else:
        verdict = "MIDDLE_BAND_LLN_REGIME_DEPENDENT"
        verdict_msg = (
            f"HP gates split across seeds/regimes. per-seed HP center={hp_center_pass_per_seed} "
            f"spread={hp_spread_pass_per_seed} ood={hp_ood_pass_per_seed}"
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_units_per_seed": n_units_per_seed,
        "hp_center_pass_per_seed": hp_center_pass_per_seed,
        "hp_spread_pass_per_seed": hp_spread_pass_per_seed,
        "hp_ood_pass_per_seed": hp_ood_pass_per_seed,
        "any_hf_center": any_hf_center,
        "any_hf_ood": any_hf_ood,
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
    """Sanity assertions for the primitives + one tiny phase point."""
    print("[selftest] running LLN point-mass primitive self-tests...", flush=True)
    rng = np.random.default_rng(42)

    # T1: bipolar_random shape + normalization.
    X = bipolar_random(10, 512, rng)
    assert X.shape == (10, 512), f"T1 shape fail: {X.shape}"
    norms = np.linalg.norm(X, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5), f"T1 norm fail: {norms[:3]}"

    # T2: theoretical formulas closed-form.
    assert abs(theoretical_center(0.15) - 0.70) < 1e-9, "T2 center fail"
    tstd = theoretical_per_item_std(8192, 0.15)
    assert 0.007 < tstd < 0.010, f"T2 std fail: {tstd}"
    tood = theoretical_ood_floor(8192, 200)
    assert 0.030 < tood < 0.040, f"T2 ood fail: {tood}"

    # T3: flip_fraction produces expected cosine with parent.
    v = X[0]
    v_flipped = flip_fraction(v, 0.15, rng)
    assert v_flipped.shape == v.shape
    # Rough cosine check: ~1 - 2*0.15 = 0.70 (finite-sample noisy at N=512).
    cos = float(v @ v_flipped)
    assert 0.55 < cos < 0.85, f"T3 flip cosine out of band: {cos}"

    # T4: one full phase point at small N produces valid quantiles.
    rng2 = np.random.default_rng(7)
    row = measure_phase_point(N=2048, V_C=100, f=0.15, seed_offset=0, rng=rng2)
    assert 0.55 < row["p50_in_kb"] < 0.85, f"T4 p50_in_kb: {row['p50_in_kb']}"
    assert row["p5_in_kb"] < row["p50_in_kb"] < row["p95_in_kb"], "T4 quantile order"
    assert 0.0 < row["p50_ood"] < 0.15, f"T4 p50_ood: {row['p50_ood']}"

    # T5: HP center gate should pass at N=2048 (well within 0.010 SE cushion at 50 items).
    # p50 SE ~ per-item-std / sqrt(50) ~ 0.014 / 7 ~ 0.002; 0.010 is 5x SE.
    assert row["gate_hp_center_pass"] or row["observed_dev_center"] < 0.020, (
        f"T5 gate_hp_center failed at reasonable N: dev={row['observed_dev_center']}"
    )

    # T6: verdict aggregation on synthetic PASS + BREACH cases.
    fake_pass_pu = [{"gate_hp_center_pass": True, "gate_hp_spread_pass": True,
                     "gate_hp_ood_pass": True, "gate_hf_center_break": False,
                     "gate_hf_ood_ratio_break": False}
                    for _ in range(45)]
    fake_pass_payload = {"per_unit": fake_pass_pu, "cardinality_ok": True}
    v_pass = aggregate_verdict({"7": fake_pass_payload, "13": fake_pass_payload,
                                 "19": fake_pass_payload})
    assert v_pass["verdict"] == "CHAIN_GRADE_LLN_POINT_MASS_VERIFIED", (
        f"T6a verdict fail: {v_pass['verdict']}"
    )

    fake_hf_pu = list(fake_pass_pu)
    fake_hf_pu[0] = dict(fake_hf_pu[0])
    fake_hf_pu[0]["gate_hf_center_break"] = True
    fake_hf_pu[0]["gate_hp_center_pass"] = False
    fake_hf_payload = {"per_unit": fake_hf_pu, "cardinality_ok": True}
    v_hf = aggregate_verdict({"7": fake_hf_payload})
    assert v_hf["verdict"] == "HARD_FAIL_LLN_BROKEN", (
        f"T6b verdict fail: {v_hf['verdict']}"
    )

    fake_short_payload = {"per_unit": fake_pass_pu[:10], "cardinality_ok": False}
    v_card = aggregate_verdict({"7": fake_short_payload})
    assert v_card["verdict"] == "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", (
        f"T6c verdict fail: {v_card['verdict']}"
    )

    print("[selftest] T1-T6 all PASS", flush=True)


# ----------------------------- main -----------------------------

def main() -> None:
    output_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(output_dir, RUN_MODE)

    print(f"[main] {ANCHOR_NAME} run_mode={RUN_MODE} seeds={SEEDS}", flush=True)
    print(f"[main] config: {CONFIG_VERSION}", flush=True)

    if RUN_MODE == "self_test":
        _self_test()
        # Write a minimal metrics.json for the runner.
        metrics = {
            "verdict": "HARD_PASS",
            "verdict_msg": "SELFTEST_PASS (primitive + verdict-aggregator T1-T6 all pass)",
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
    metrics["N_SWEEP"] = N_SWEEP
    metrics["V_C_SWEEP"] = V_C_SWEEP
    metrics["F_SWEEP"] = F_SWEEP
    metrics["expected_n_units_per_seed"] = EXPECTED_N_UNITS_PER_SEED

    # Atomic write via write_metrics (which does its own write; wrap in tmp+replace for safety).
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
