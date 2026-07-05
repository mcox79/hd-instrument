"""JOINT CAPACITY x HUB-DEGREE x REDUNDANCY sweep -- is the bundle-capacity limit a
COMPUTE COST or a WALL, and establish the (load x degree x redundancy) recall envelope
that two downstream build cells depend on.

Constructive build probe (NO LLM, NO GPU, read-only synthetic vector algebra). Answers the
three open gaps from the 5x memory-convergence drill
(notes/research_5x_drill_memory_spec_and_brain_mechanism_2026-07-05.md):

  GAP 1  Does PROTECTED/INDEX binding (hippocampal-indexing analog: protect a compact unique
         address per binding) hold across the FULL hub-degree spectrum (deg1..deg20+), and as
         load grows toward the capacity ceiling -- or does the fix itself degrade under load?
  GAP 2  Does protecting hubs COST raw non-hub (leaf) capacity? (index footprint concern)
  GAP 3  Is the residual capacity limit a WALL, or a COMPUTE COST buyable with redundancy?

MODEL (one global superposition bundle = the object of study; bundle-capacity characterization):
  B = sum over L associations of bind(addr, value), addr,value in R^N unit vectors.
    - a HUB key k_h is reused K times with distinct values (hub-degree K); leaves are unique keys.
    - UNPROTECTED addr = key            -> the K hub reuses collide at ONE address (recall ~1/K).
    - PROTECTED   addr = roll(key, j)   -> distinct per-slot address (permutation index; DIMENSION-FREE:
                                          a unitary rotation, no extra dimension budget). Hippocampal
                                          index analog. Recall decoupled from K.
    - REDUNDANCY  R = R independent banks (indep keys/bank, SAME value); recall = mean of R unbinds
                     before cleanup. Crosstalk averages ~1/sqrt(R) -> capacity_alpha scales ~R IF the
                     limit is a COST (buyable). This is the PP-354-class redundancy lever.

MEASURES per (seed, load L/N, degree K, arm, R) cell:
  (a) exact recall = unbind + argmax cleanup vs codebook -> correct discrete atom (top-1).
  (b) algebra round-trip fidelity on PROTECTED hub atoms:
        - fid_clean = post-cleanup exact round-trip (= recall; the functionally-relevant discrete
          fidelity for a glass-box memory), gated;
        - fid_raw   = pre-cleanup cosine(recovered, true) (honest diagnostic; load-limited ~1/sqrt(L_eff),
          NOT gated -- a global superposition is expected raw-noisy, cleanup is the point).
  (c) leaf (deg1) capacity_alpha with protection vs without (parity => protection is dimension-free).

DECISIVE READOUTS:
  - COST vs WALL: leaf recall + capacity_alpha rise sharply with R (redundancy) => COMPUTE COST.
  - GENERALIZATION: protected hub recall flat + high across degree spectrum => fix generalizes.
  - PARITY: protected leaf capacity == unprotected leaf capacity => protection is free.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (protected vs unprotected recovery arrays hash-distinct)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb declared: retrieval SNR feasibility simulated at N=8192 (see prereg); HP below ceiling
# - baseline (unprotected deg5+ / leaf@R1) in-band (0.05<x<0.95) => measurable failure to rescue
# - discriminator survives scale: SMOKE runs at FULL N=8192 (reduced grid) so capacity physics identical
# - HP_SCOPE: HP gates apply to protected arm + leaf-parity + redundancy-lever; NOT to unprotected baseline
# - cardinality_ok: EXPECTED_N_UNITS = seeds*loads*degrees*arms*R gate
# - per-unit failure-class instrumentation (no bare except; SystemExit re-raised first)
# - calibration_check: default_ok (synthetic i.i.d. unit vectors; no data leakage; clean-synthetic per USER)
# - Gate D positive control: unprotected deg5 recall reproduces the measured ~0.219 hub-collapse floor
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Storage strategy: BUNDLED (the object of study -- bundle-capacity characterization; exempt (b) per
SHARDED-STORAGE-DEFAULT rule: testing bundle-storage as the discriminator). A SHARDED reference point
is also measured (ARM D diagnostic) to quantify sharded headroom for the downstream build cells.

Compute architecture: (b) sequential/vectorized-CPU. Pure HRR bundle algebra at N=8192 via batched
numpy rfft (roll via freq-domain phase = bit-identical to np.roll-then-bind, asserted in --self-test
against hdlab.binding). No material GPU speedup at N=8192 (rfft length 8192 is microseconds); this cell
IS the CPU reference for the substrate bundle primitive. Full wall estimate < 25 min (3 seeds).

ASCII-only. CPU only. No substrate mutation.
Run:  python experiments/exp_mem_joint_capacity_hub_degree_redundancy_v1.py --run-mode {smoke,full}
Self: python experiments/exp_mem_joint_capacity_hub_degree_redundancy_v1.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(line_buffering=True)  # progress flushing (section 17)
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial, aggregate_partials, get_output_dir,
)

ANCHOR_NAME = "mem_joint_capacity_hub_degree_redundancy_v1"
EPS = 1e-12

# ---- MEASURED/THEORETICAL reference anchors (tagged per META_RULE_AC) ----
# Unprotected hub deg>=5 single-shot collapse floor (positive control target, Gate D):
#   0.219  MEASURED@data/exp_cortex_readiness_real_atom_algebra_v1 (deg>=5 top1 ~0.21) and
#          MEASURED@data/exp_deep_reasoning_hub_robustness_v1 (ss_raw deg>=5 ~0.219; idx_bind rescue).
#   For synthetic i.i.d. atoms the unprotected hub recall THEORETICAL@~1/K (each of K same-address
#   reuses superposes; argmax recovers at most one) -> deg5 ~ 0.20, brackets the 0.219 measurement.
HUB_COLLAPSE_FLOOR_REF = 0.219  # MEASURED (positive-control center for unprotected deg5)


# ============================================================
# Defensive-error-checking helpers (section 13)
# ============================================================


def _write_start_marker(out_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(out_dir: Path, metrics: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "unknown",
    }
    _write_metrics_atomic(out_dir, diag)


# ============================================================
# HRR bundle algebra (batched numpy rfft). Roll via freq-domain phase.
# ============================================================


def _unit(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + EPS)).astype(np.float32)


def _rfft(X: np.ndarray, N: int) -> np.ndarray:
    return np.fft.rfft(X, n=N, axis=-1)


def _irfft(F: np.ndarray, N: int) -> np.ndarray:
    return np.fft.irfft(F, n=N, axis=-1).astype(np.float32)


def _phase_ramp(N: int, shifts: np.ndarray) -> np.ndarray:
    """exp(-2i*pi*k*j/N) for k=0..N/2 (freq-domain equivalent of time-domain np.roll by j).
    shifts (S,) -> (S, N//2+1)."""
    k = np.arange(N // 2 + 1)
    return np.exp(-2j * np.pi * np.outer(shifts.astype(np.float64), k) / N)


# ============================================================
# Core: build one global bundle + evaluate hub + leaf recall
# ============================================================


def build_and_eval(seed_rng, N, load_ratio, K, protected, R, n_hubs):
    """One (load, degree K, arm, redundancy R) cell. Returns dict of measured scalars."""
    L = int(round(load_ratio * N))
    # cap hub slots to at most half the load so leaves exist for a leaf-capacity read
    n_hub_slots = n_hubs * K
    if n_hub_slots > L // 2:
        n_hubs = max(1, (L // 2) // K)
        n_hub_slots = n_hubs * K
    n_leaf = L - n_hub_slots
    if n_leaf < 1:
        n_leaf = 1
        L = n_hub_slots + n_leaf
    C = L  # codebook = all stored distinct values

    values = _unit(seed_rng.standard_normal((C, N)).astype(np.float32))
    values_rf = _rfft(values, N)  # (C, F)
    perm = seed_rng.permutation(C)
    hub_vi = perm[:n_hub_slots].reshape(n_hubs, K)     # value index per hub slot
    leaf_vi = perm[n_hub_slots:n_hub_slots + n_leaf]   # value index per leaf

    slot_shifts = np.arange(K)                          # within-hub permutation power j=0..K-1
    phases = _phase_ramp(N, slot_shifts)                # (K, F)

    # accumulate recovered (averaged over R banks) BEFORE cleanup
    rec_hub = np.zeros((n_hub_slots, N), dtype=np.float32)
    rec_leaf = np.zeros((n_leaf, N), dtype=np.float32)

    F = N // 2 + 1
    for _r in range(R):
        hub_keys = _unit(seed_rng.standard_normal((n_hubs, N)).astype(np.float32))
        leaf_keys = _unit(seed_rng.standard_normal((n_leaf, N)).astype(np.float32))
        hub_keys_rf = _rfft(hub_keys, N)                # (n_hubs, F)
        leaf_keys_rf = _rfft(leaf_keys, N)              # (n_leaf, F)

        # protected: addr_rf[h,j] = hub_keys_rf[h] * phases[j]; unprotected: addr_rf[h,j]=hub_keys_rf[h]
        if protected:
            hub_addr_rf = (hub_keys_rf[:, None, :] * phases[None, :, :]).reshape(n_hub_slots, F)
        else:
            hub_addr_rf = np.broadcast_to(hub_keys_rf[:, None, :], (n_hubs, K, F)).reshape(n_hub_slots, F)

        # bundle B (freq domain, linear): sum over hub slots + leaves of addr_rf * value_rf
        Bf = (hub_addr_rf * values_rf[hub_vi.reshape(-1)]).sum(0)
        Bf = Bf + (leaf_keys_rf * values_rf[leaf_vi]).sum(0)

        # unbind: rec = irfft( Bf * conj(addr_rf) )
        rec_hub += _irfft(Bf[None, :] * np.conj(hub_addr_rf), N)
        rec_leaf += _irfft(Bf[None, :] * np.conj(leaf_keys_rf), N)

    rec_hub /= R
    rec_leaf /= R

    rhn = _unit(rec_hub)
    sc_hub = rhn @ values.T
    hub_true = hub_vi.reshape(-1)
    hub_pred = sc_hub.argmax(1)
    hub_recall = float((hub_pred == hub_true).mean())
    # raw pre-cleanup fidelity (diagnostic): mean cosine(recovered, true value); load-limited.
    fid_raw = float(np.mean(np.sum(rhn * values[hub_true], axis=1)))

    rln = _unit(rec_leaf)
    sc_leaf = rln @ values.T
    leaf_recall = float((sc_leaf.argmax(1) == leaf_vi).mean())

    return {
        "load": load_ratio, "K": int(K), "protected": bool(protected), "R": int(R),
        "N": int(N), "L": int(L), "n_hubs": int(n_hubs), "n_hub_slots": int(n_hub_slots),
        "n_leaf": int(n_leaf), "C": int(C),
        "hub_recall": round(hub_recall, 4),
        "hub_fid_raw_cos": round(fid_raw, 4),
        "hub_fid_clean": round(hub_recall, 4),   # post-cleanup discrete round-trip == recall
        "leaf_recall": round(leaf_recall, 4),
        # small recovery digest for arms-differ hash
        "_digest": hashlib.sha256(hub_pred[:512].astype(np.int64).tobytes()).hexdigest(),
    }


def build_sharded_eval(seed_rng, N, load_ratio, K, R, n_hubs):
    """ARM D diagnostic: SHARDED storage -- each hub is its OWN trace (K items only), protected
    addressing. Quantifies sharded headroom vs the global bundle (for downstream build cells)."""
    # each shard bundles only its K edges; recall limited by K + codebook C (not global L)
    L = int(round(load_ratio * N))
    C = max(L, n_hubs * K)
    values = _unit(seed_rng.standard_normal((C, N)).astype(np.float32))
    values_rf = _rfft(values, N)
    perm = seed_rng.permutation(C)
    hub_vi = perm[:n_hubs * K].reshape(n_hubs, K)
    phases = _phase_ramp(N, np.arange(K))
    F = N // 2 + 1
    rec = np.zeros((n_hubs * K, N), dtype=np.float32)
    for _r in range(R):
        hub_keys = _unit(seed_rng.standard_normal((n_hubs, N)).astype(np.float32))
        hub_keys_rf = _rfft(hub_keys, N)
        addr_rf = (hub_keys_rf[:, None, :] * phases[None, :, :]).reshape(n_hubs * K, F)  # (S,F)
        # per-shard bundle: trace_h = sum_j addr[h,j]*value[h,j]; store as (n_hubs, F)
        vv = values_rf[hub_vi.reshape(-1)].reshape(n_hubs, K, F)
        aa = addr_rf.reshape(n_hubs, K, F)
        traces = (aa * vv).sum(1)                          # (n_hubs, F)
        traces_per_slot = np.repeat(traces, K, axis=0)     # (S, F)
        rec += _irfft(traces_per_slot * np.conj(addr_rf), N)
    rec /= R
    rn = _unit(rec)
    pred = (rn @ values.T).argmax(1)
    true = hub_vi.reshape(-1)
    return float((pred == true).mean())


# ============================================================
# Config
# ============================================================


def get_config(run_mode):
    if run_mode == "self_test":
        return {"N": 1024, "seeds": [7], "loads": [0.1], "degrees": [1, 5],
                "arms": [False, True], "redund": [1, 4], "n_hubs": 10,
                "leaf_R": [1, 4], "dim_lever_N": [1024], "dim_lever_load": 0.2,
                "op_load": 0.1, "op_R": 4, "sharded_degrees": [5]}
    if run_mode == "smoke":
        # SMOKE at FULL N=8192 (discriminator-survives-scale option A), reduced grid + 2 seeds.
        return {"N": 8192, "seeds": [7, 13], "loads": [0.1, 0.2], "degrees": [1, 5, 20],
                "arms": [False, True], "redund": [1, 4], "n_hubs": 25,
                "leaf_R": [1, 2, 4, 8], "dim_lever_N": [4096, 8192], "dim_lever_load": 0.2,
                "op_load": 0.2, "op_R": 4, "sharded_degrees": [5, 20]}
    # full
    return {"N": 8192, "seeds": [7, 13, 19], "loads": [0.1, 0.2, 0.3, 0.4],
            "degrees": [1, 2, 3, 5, 10, 20], "arms": [False, True], "redund": [1, 4],
            "n_hubs": 50, "leaf_R": [1, 2, 4, 8], "dim_lever_N": [4096, 8192, 16384],
            "dim_lever_load": 0.2, "op_load": 0.2, "op_R": 4, "sharded_degrees": [5, 10, 20]}


# ============================================================
# Per-seed run
# ============================================================


def run_one_seed(seed, cfg, out_dir, t0):
    N = cfg["N"]
    cells = {}  # keyed by (load,K,arm,R)
    total = len(cfg["loads"]) * len(cfg["degrees"]) * len(cfg["arms"]) * len(cfg["redund"])
    idx = 0
    for load in cfg["loads"]:
        for K in cfg["degrees"]:
            for arm in cfg["arms"]:
                for R in cfg["redund"]:
                    rng = np.random.default_rng(seed * 100003 + idx)
                    res = build_and_eval(rng, N, load, K, arm, R, cfg["n_hubs"])
                    key = f"load{load}_K{K}_{'prot' if arm else 'unprot'}_R{R}"
                    cells[key] = res
                    idx += 1
                    if idx % 8 == 0:
                        _heartbeat(out_dir, idx, total, t0,
                                   extra={"seed": seed, "arm_A_cell": key,
                                          "hub_recall": res["hub_recall"]})
                        print(f"  [seed {seed}] A {idx}/{total} {key}: "
                              f"hub={res['hub_recall']:.3f} leaf={res['leaf_recall']:.3f}", flush=True)

    # ARM B: redundancy lever on leaf capacity (deg1 leaf-only, across R)
    armB = {}
    for load in cfg["loads"]:
        for R in cfg["leaf_R"]:
            rng = np.random.default_rng(seed * 100003 + 900000 + int(load * 1000) + R)
            res = build_and_eval(rng, N, load, 1, False, R, max(1, cfg["n_hubs"] // 5))
            armB[f"load{load}_R{R}"] = {"leaf_recall": res["leaf_recall"], "load": load, "R": R}
    print(f"  [seed {seed}] ARM B (redundancy lever) done", flush=True)

    # ARM C: dimension lever (leaf capacity vs N at fixed load, R=1)
    armC = {}
    for Nl in cfg["dim_lever_N"]:
        rng = np.random.default_rng(seed * 100003 + 800000 + Nl)
        res = build_and_eval(rng, Nl, cfg["dim_lever_load"], 1, False, 1, max(1, cfg["n_hubs"] // 5))
        armC[f"N{Nl}"] = {"leaf_recall": res["leaf_recall"], "N": Nl, "L": res["L"],
                          "load": cfg["dim_lever_load"]}
    print(f"  [seed {seed}] ARM C (dimension lever) done", flush=True)

    # ARM D: sharded-vs-bundled diagnostic at operating load, R=1
    armD = {}
    for K in cfg["sharded_degrees"]:
        rng = np.random.default_rng(seed * 100003 + 700000 + K)
        sh = build_sharded_eval(rng, N, cfg["op_load"], K, 1, cfg["n_hubs"])
        armD[f"K{K}"] = {"sharded_hub_recall": round(sh, 4), "K": K, "load": cfg["op_load"]}
    print(f"  [seed {seed}] ARM D (sharded diagnostic) done", flush=True)

    return {"seed": seed, "N": N, "run_mode": cfg.get("_mode"), "cells": cells,
            "armB_redundancy": armB, "armC_dimension": armC, "armD_sharded": armD,
            "config_version": f"ANCHOR={ANCHOR_NAME},N={N},run_mode={cfg.get('_mode')}"}


# ============================================================
# Aggregation + joint-gate verdict
# ============================================================


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else float("nan")


def _cell(per_seed, load, K, arm, R, field):
    key = f"load{load}_K{K}_{'prot' if arm else 'unprot'}_R{R}"
    return _mean([per_seed[s]["cells"][key][field] for s in per_seed if key in per_seed[s]["cells"]])


def classify(per_seed, cfg):
    """Joint gate: do NOT credit a capacity gain that collapses parity/algebra."""
    seeds = list(per_seed.keys())
    op_load = cfg["op_load"]
    op_R = cfg["op_R"]
    hub_degs = [d for d in cfg["degrees"] if d >= 2]
    hub_ge5 = [d for d in cfg["degrees"] if d >= 5]

    # ---- gate quantities (cross-seed means) ----
    # HP1: protected hub recall at OP, per degree
    prot_op = {d: _cell(per_seed, op_load, d, True, op_R, "hub_recall") for d in hub_degs}
    prot_op_min = min(prot_op.values())
    prot_op_deg1 = _cell(per_seed, op_load, 1, True, op_R, "hub_recall")
    prot_op_spread = max(prot_op.values()) - min(prot_op.values())

    # HP2: protection lift at validated-win regime (lowest load, R=1)
    lo_load = min(cfg["loads"])
    lift_prot = _mean([_cell(per_seed, lo_load, d, True, 1, "hub_recall") for d in hub_ge5])
    lift_unprot = _mean([_cell(per_seed, lo_load, d, False, 1, "hub_recall") for d in hub_ge5])
    protection_lift = lift_prot - lift_unprot

    # HP3: redundancy moves envelope (leaf recall at op_load, R1 -> maxR)
    maxR = max(cfg["leaf_R"])
    leaf_R1 = _mean([per_seed[s]["armB_redundancy"][f"load{op_load}_R1"]["leaf_recall"] for s in seeds
                     if f"load{op_load}_R1" in per_seed[s]["armB_redundancy"]])
    leaf_Rmax = _mean([per_seed[s]["armB_redundancy"][f"load{op_load}_R{maxR}"]["leaf_recall"] for s in seeds
                       if f"load{op_load}_R{maxR}" in per_seed[s]["armB_redundancy"]])
    redundancy_gain = leaf_Rmax - leaf_R1

    # HP4: leaf capacity parity (protected vs unprotected leaf) at OP
    leaf_parity_prot = _cell(per_seed, op_load, 1, True, op_R, "leaf_recall")
    leaf_parity_unprot = _cell(per_seed, op_load, 1, False, op_R, "leaf_recall")
    parity_gap = abs(leaf_parity_prot - leaf_parity_unprot)

    # HP5: protected hub algebra fidelity (post-cleanup) at OP for deg5+
    fid_clean = _mean([_cell(per_seed, op_load, d, True, op_R, "hub_fid_clean") for d in hub_ge5])

    # positive control (Gate D): unprotected deg5 recall reproduces ~0.219 collapse floor
    pc_unprot_deg5 = _cell(per_seed, lo_load, 5, False, 1, "hub_recall")
    pos_control_ok = 0.10 <= pc_unprot_deg5 <= 0.35  # brackets 1/5=0.20 and measured 0.219

    diag = {
        "op_load": op_load, "op_R": op_R,
        "HP1_protected_hub_recall_by_deg_at_OP": {str(d): round(prot_op[d], 4) for d in hub_degs},
        "HP1_protected_hub_recall_min": round(prot_op_min, 4),
        "HP1_protected_deg_spread": round(prot_op_spread, 4),
        "HP1_protected_deg1_at_OP": round(prot_op_deg1, 4),
        "HP2_protection_lift_deg5plus_loLoad_R1": round(protection_lift, 4),
        "HP2_prot_deg5plus": round(lift_prot, 4), "HP2_unprot_deg5plus": round(lift_unprot, 4),
        "HP3_leaf_recall_R1": round(leaf_R1, 4), "HP3_leaf_recall_Rmax": round(leaf_Rmax, 4),
        "HP3_redundancy_gain": round(redundancy_gain, 4), "HP3_maxR": maxR,
        "HP4_leaf_parity_gap": round(parity_gap, 4),
        "HP4_leaf_prot": round(leaf_parity_prot, 4), "HP4_leaf_unprot": round(leaf_parity_unprot, 4),
        "HP5_protected_hub_fid_clean_deg5plus": round(fid_clean, 4),
        "GateD_pos_control_unprot_deg5_loLoad": round(pc_unprot_deg5, 4),
        "GateD_pos_control_ok": pos_control_ok,
    }

    # ---- discriminator-fires (META_RULE_K): baseline collapses + mechanism fires + lever fires ----
    fires_baseline_collapse = lift_unprot < 0.30          # there IS a hub wall to rescue
    fires_mechanism = protection_lift >= 0.20             # protection meaningfully rescues
    fires_lever = redundancy_gain >= 0.10                 # redundancy moves envelope
    discriminator_fired = fires_baseline_collapse and fires_mechanism and fires_lever
    diag["discriminator_fired"] = discriminator_fired
    diag["fires"] = {"baseline_collapse": bool(fires_baseline_collapse),
                     "mechanism": bool(fires_mechanism), "lever": bool(fires_lever)}

    if not discriminator_fired:
        return "DISCRIMINATOR_DID_NOT_FIRE", (
            f"discriminator did not fire (baseline_collapse={fires_baseline_collapse} "
            f"unprot_deg5+={lift_unprot:.3f}; mechanism={fires_mechanism} lift={protection_lift:.3f}; "
            f"lever={fires_lever} redun_gain={redundancy_gain:.3f}); regime insufficient to test hypothesis"), diag

    # ---- HARD-FAIL (any) ----
    if prot_op_min < 0.40:
        return "HARD_FAIL_PROTECTION_COLLAPSES_UNDER_LOAD", (
            f"protected hub recall {prot_op_min:.3f} < 0.40 at op_load={op_load} R={op_R} "
            f"(protection collapses before ceiling)"), diag
    if (leaf_parity_unprot - leaf_parity_prot) > 0.25:
        return "HARD_FAIL_PROTECTION_TAXES_CAPACITY", (
            f"protected leaf recall {leaf_parity_prot:.3f} is >0.25 below unprotected "
            f"{leaf_parity_unprot:.3f} (protection robs non-hub capacity)"), diag
    if fid_clean < 0.40:
        return "HARD_FAIL_ALGEBRA_BREAKS_ON_PROTECTED", (
            f"protected hub round-trip fidelity {fid_clean:.3f} < 0.40 (protection breaks algebra)"), diag
    if redundancy_gain < 0.10:
        return "HARD_FAIL_CAPACITY_IS_A_WALL", (
            f"redundancy R1->R{maxR} raises leaf recall by only {redundancy_gain:.3f} (<0.10): "
            f"the capacity limit behaves like a WALL, not a compute cost"), diag

    # ---- HARD-PASS (all; strictly above floor per META_RULE_L) ----
    hp = {
        "HP1_generalizes": prot_op_min >= 0.65 and prot_op_spread <= 0.20,
        "HP2_lift": protection_lift >= 0.30,
        "HP3_cost_not_wall": redundancy_gain >= 0.30 and leaf_Rmax >= 2.0 * max(leaf_R1, 0.01),
        "HP4_parity": parity_gap <= 0.05,
        "HP5_fidelity": fid_clean >= 0.65,
    }
    diag["hard_pass_gates"] = hp
    if all(hp.values()) and pos_control_ok:
        return "HARD_PASS_COMPUTE_COST_ENVELOPE_ESTABLISHED", (
            f"PROTECTED/INDEX binding generalizes across degree spectrum (min hub recall "
            f"{prot_op_min:.3f} >=0.65, spread {prot_op_spread:.3f} <=0.20 at op_load={op_load} R={op_R}); "
            f"protection lift +{protection_lift:.3f} at deg5+ reproduces the hub-rescue win; leaf capacity "
            f"parity gap {parity_gap:.3f} <=0.05 (protection is dimension-free); redundancy raises leaf "
            f"recall +{redundancy_gain:.3f} (R1={leaf_R1:.3f}->R{maxR}={leaf_Rmax:.3f}) => bundle-capacity "
            f"limit is a COMPUTE COST buyable with redundancy, NOT a wall. Envelope established."), diag

    # ---- MIDDLE_BAND ----
    passed = [k for k, v in hp.items() if v]
    failed = [k for k, v in hp.items() if not v]
    return "MIDDLE_BAND", (
        f"partial: passed {passed}; failed {failed}. protected hub min={prot_op_min:.3f} "
        f"lift=+{protection_lift:.3f} parity_gap={parity_gap:.3f} redun_gain=+{redundancy_gain:.3f} "
        f"fid={fid_clean:.3f}. Routes to erasure-coding (PP-354) / larger fixed index budget rescue."), diag


# ============================================================
# Self-test (formula selftests; queue --self-test gate; exit 0 <180s)
# ============================================================


def self_test(out_dir):
    import torch
    from hdlab import binding
    t0 = time.perf_counter()
    print("[self-test] formula self-tests...", flush=True)

    # 1. batched rfft HRR == hdlab.binding (bit-close)
    N = 1024
    rng = np.random.default_rng(0)
    a = _unit(rng.standard_normal((4, N)).astype(np.float32))
    b = _unit(rng.standard_normal((4, N)).astype(np.float32))
    mine = _irfft(_rfft(a, N) * _rfft(b, N), N)
    theirs = binding.bind(torch.from_numpy(a), torch.from_numpy(b)).numpy()
    d1 = float(np.abs(mine - theirs).max())
    assert d1 < 1e-4, f"batched-bind != hdlab.binding.bind (max|d|={d1})"

    mine_u = _irfft(_rfft(mine, N) * np.conj(_rfft(b, N)), N)
    theirs_u = binding.unbind(torch.from_numpy(theirs), torch.from_numpy(b)).numpy()
    d2 = float(np.abs(mine_u - theirs_u).max())
    assert d2 < 1e-4, f"batched-unbind != hdlab.binding.unbind (max|d|={d2})"

    # 2. freq-domain phase roll == time-domain np.roll then bind (the PROTECTED index primitive)
    key = _unit(rng.standard_normal((1, N)).astype(np.float32))[0]
    val = _unit(rng.standard_normal((1, N)).astype(np.float32))[0]
    j = 7
    rolled = np.roll(key, j)
    bind_rolled = _irfft(_rfft(rolled[None], N) * _rfft(val[None], N), N)[0]
    ph = _phase_ramp(N, np.array([j]))[0]
    bind_phase = _irfft((_rfft(key[None], N)[0] * ph)[None] * _rfft(val[None], N), N)[0]
    d3 = float(np.abs(bind_rolled - bind_phase).max())
    assert d3 < 1e-4, f"phase-roll != np.roll-then-bind (max|d|={d3}); PROTECTED primitive wrong"

    # 3. mechanism-direction sanity (tiny): unprotected deg5 collapses ~1/K; protected >> unprotected;
    #    redundancy lifts leaf recall.
    cfg = get_config("self_test")
    rngc = np.random.default_rng(7)
    up = build_and_eval(rngc, cfg["N"], 0.1, 5, False, 1, cfg["n_hubs"])
    rngc = np.random.default_rng(7)
    pr = build_and_eval(rngc, cfg["N"], 0.1, 5, True, 1, cfg["n_hubs"])
    assert up["hub_recall"] < 0.45, f"unprotected deg5 not collapsing (got {up['hub_recall']})"
    assert pr["hub_recall"] > up["hub_recall"] + 0.10, (
        f"protection did not help (prot={pr['hub_recall']} unprot={up['hub_recall']})")
    rngc = np.random.default_rng(11)
    lr1 = build_and_eval(rngc, cfg["N"], 0.1, 1, False, 1, cfg["n_hubs"])["leaf_recall"]
    rngc = np.random.default_rng(11)
    lr4 = build_and_eval(rngc, cfg["N"], 0.1, 1, False, 4, cfg["n_hubs"])["leaf_recall"]
    assert lr4 >= lr1, f"redundancy did not help leaf recall (R1={lr1} R4={lr4})"

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "SELFTEST_PASS",
        "verdict_msg": (f"formula self-tests pass: bind-diff={d1:.1e} unbind-diff={d2:.1e} "
                        f"phaseroll-diff={d3:.1e}; unprot_deg5={up['hub_recall']:.3f} < "
                        f"prot_deg5={pr['hub_recall']:.3f}; leaf R1={lr1:.3f}<=R4={lr4:.3f}"),
        "summary": "SELFTEST_PASS (formula self-tests: HRR bit-identity + phase-roll + mechanism direction)",
        "run_mode": "self_test",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(out_dir, metrics)
    print(f"[self-test] PASS in {elapsed:.1f}s :: {metrics['verdict_msg']}", flush=True)
    return 0


# ============================================================
# main
# ============================================================


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; flag accepted for runner compat
    args = ap.parse_args()

    if args.self_test:
        out_dir = get_output_dir(ANCHOR_NAME)
        return self_test(out_dir)

    run_mode = args.run_mode or os.environ.get("HDLAB_RUN_MODE", "full")
    run_mode = run_mode if run_mode in ("smoke", "full") else "full"
    cfg = get_config(run_mode)
    cfg["_mode"] = run_mode

    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.perf_counter()

    n_units = len(cfg["seeds"]) * len(cfg["loads"]) * len(cfg["degrees"]) * len(cfg["arms"]) * len(cfg["redund"])
    _write_start_marker(out_dir, run_mode, n_units)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={cfg['N']} seeds={cfg['seeds']} "
          f"loads={cfg['loads']} degrees={cfg['degrees']} redund={cfg['redund']} "
          f"expected_units={n_units}", flush=True)

    run_config = {"N": cfg["N"], "run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(cfg["seeds"], out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, running {remaining}", flush=True)

    for seed in remaining:
        print(f"\n[seed {seed}] building bundles (N={cfg['N']})...", flush=True)
        res = run_one_seed(seed, cfg, out_dir, t0)
        res["N"] = cfg["N"]
        res["run_mode"] = run_mode
        write_partial(out_dir, seed, res)
        _heartbeat(out_dir, seed, cfg["seeds"][-1], t0, extra={"stage": "seed_done", "seed": seed})

    per_seed = aggregate_partials(out_dir, cfg["seeds"], run_config=run_config)
    n_collected = sum(len(per_seed[s]["cells"]) for s in per_seed)
    expected_cells = n_units
    cardinality_ok = (len(per_seed) == len(cfg["seeds"])) and (n_collected == expected_cells)

    # arms-differ (META_RULE_AF): protected vs unprotected recovery digests distinct
    arms_differ_ok = True
    arms_differ_note = "ok"
    for s in per_seed:
        cells = per_seed[s]["cells"]
        for load in cfg["loads"]:
            for K in cfg["degrees"]:
                if K < 2:
                    continue  # deg1: protected==unprotected BY DESIGN (single item; permutation is identity-like)
                for R in cfg["redund"]:
                    kp = f"load{load}_K{K}_prot_R{R}"
                    ku = f"load{load}_K{K}_unprot_R{R}"
                    if kp in cells and ku in cells and cells[kp]["_digest"] == cells[ku]["_digest"]:
                        arms_differ_ok = False
                        arms_differ_note = f"IDENTICAL prot/unprot at {kp} (seed {s})"

    verdict, vmsg, diag = classify(per_seed, cfg)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: collected {n_collected} cells / "
                f"{len(per_seed)} seeds; expected {expected_cells} cells / {len(cfg['seeds'])} seeds | " + vmsg)
    if not arms_differ_ok:
        verdict = "HARD_FAIL_ARMS_IDENTICAL"
        vmsg = f"META_RULE_AF VIOLATION: {arms_differ_note} | " + vmsg

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: joint capacity x hub-degree x redundancy envelope ({run_mode}, N={cfg['N']})",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "n_seeds": len(cfg["seeds"]),
        "seeds": cfg["seeds"],
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
        "expected_n_units": expected_cells,
        "n_units_counted": n_collected,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_note": arms_differ_note,
        "gate_diagnostics": diag,
        "per_seed": per_seed,
    }
    _write_metrics_atomic(out_dir, metrics)

    written = json.load(open(out_dir / "metrics.json"))
    assert written["run_mode"] == run_mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {run_mode}"

    print(f"\n[VERDICT] {verdict}", flush=True)
    print(f"[msg] {vmsg}", flush=True)
    print(f"[diag] HP1_min={diag.get('HP1_protected_hub_recall_min')} "
          f"HP2_lift={diag.get('HP2_protection_lift_deg5plus_loLoad_R1')} "
          f"HP3_gain={diag.get('HP3_redundancy_gain')} HP4_parity={diag.get('HP4_leaf_parity_gap')} "
          f"HP5_fid={diag.get('HP5_protected_hub_fid_clean_deg5plus')}", flush=True)
    print(f"[metrics] {out_dir / 'metrics.json'} ({elapsed:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    _out_dir = None
    try:
        _st = "--self-test" in sys.argv
        _rm = None
        for i, a in enumerate(sys.argv):
            if a == "--run-mode" and i + 1 < len(sys.argv):
                _rm = sys.argv[i + 1]
        if _st:
            _rm = "self_test"
        else:
            _rm = _rm or os.environ.get("HDLAB_RUN_MODE", "full")
            _rm = _rm if _rm in ("smoke", "full") else "full"
        _out_dir = get_output_dir(ANCHOR_NAME)
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _out_dir is not None:
            _write_crash_metrics(_out_dir, e)
        raise
