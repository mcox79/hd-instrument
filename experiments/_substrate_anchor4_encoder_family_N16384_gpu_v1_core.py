"""Shared core for substrate_anchor4_encoder_family_N16384_gpu_v1 siblings.

ANCHOR 4 encoder-family CG extension to N=16384 (v4 dropped this dim
explicitly as "saturating"; this cell tests whether raising the load
axis 2x (compensating for 2x N -> 2x capacity) escapes saturation and
lets the encoder-discrimination discriminator survive at N=16384).

Prior arc (substrate-KB queried 2026-07-01):
  - v4 at N=[2048,4096,8192] HARD_PASS after META_RULE_AY fix (2026-06-30)
  - v4 EXPLICITLY excluded N=16384 as "saturating" in its regime rationale
  - v3 phantom-FULL diagnosed 2026-06-30 (dense triplet bit-identical)
  - Encoder distinctness verified at pre-flight (SHA-256 gate).

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26) — analytical + preview:
  (A) Analytical: v4 loads {8,12,16,24} at N=8192 avoided saturation. At N=16384
      capacity doubles, so equivalent-stress loads = {16,24,32,48}. Load scales
      with N so the discriminator stress regime is preserved.
  (B) Preview: smoke at N=16384 with load={16,24,32,48} verifies saturation_frac
      stays below META_RULE_Q floor (< SATURATION_FLAG_THRESH).
  (C) If smoke saturates at N=16384 despite doubled loads, HARD_FAIL_SATURATION
      fires -- v4 rationale confirmed and cell should not dispatch full.

v1 differences from v4:
  - N_DIM axis = [16384] ONLY (single dim; test v4's "saturating" claim)
  - LOADS = [16.0, 24.0, 32.0, 48.0] (v4 loads x2 for capacity-preserving stress)
  - DECAYS = [30, 60, 180] (unchanged from v4)
  - Cardinality: 5 enc * 3 decay * 4 load * 1 dim = 60 per seed FULL
                  5 enc * 2 decay * 3 load * 1 dim = 30 per seed SMOKE
  - Positive control: binary_bipolar at (dr=180, ld=16.0, N=16384) TD_DOMINATES
    (load-scaled from v4's ld=8.0)

Reuses ALL v4 primitives (encoder builds, bind ops, phase-point eval,
pre-flight distinctness, verdict-emitter with META_RULE_AY). Only the
axis constants + cardinality + positive control override.

PROT-020: `import torch` -> overnight_queue routing gate.
GPU-eligible: matmul-bound at N=16384 with 3 seeds concurrent.

ASCII-only. No unicode. No em-dashes. No emojis.

Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Tuple

import numpy as np
import torch  # PROT-020: overnight_queue routing gate

# Import ALL primitives from v4 core (encoder builds, bind ops, eval, etc.)
from experiments._substrate_anchor4_encoder_family_phase_diagram_v4_core import (
    ENCODER_FAMILIES,
    N_ATOMS_BASE, N_DAYS_SIM, R_BUCKETS, QUERY_DECAY_TAU,
    NOISE_SIGMA,
    HP_DOMINANCE_RATE_LO, HP_NET_DOMINANCE_LO, HP_RD_LOSS_RATE_HI,
    HP_RECENCY_DECODE_FLOOR, HP_MIN_PAIRS_DIFFER,
    META_AY_HARD_FAIL_FRAC, META_AY_MM_DEMOTE_FRAC,
    SATURATION_FLAG_THRESH, SATURATION_HARD_FAIL_FRAC,
    _get_device, get_backend_label,
    verify_encoder_distinctness_preflight,
    simulate_atom_timeline, build_encoded_atom_store,
    decode_recency_buckets, eval_phase_point,
    pareto_dominance_outcome, emit_verdict_with_AY,
)

# -------------------------------------------------------------------------
# v1 axis overrides (LOCKED at module init)
# -------------------------------------------------------------------------
N_DIM_SWEEP_FULL: List[int] = [16384]
N_DIM_SWEEP_SMOKE: List[int] = [16384]  # smoke at full-N (discriminator-survives-scale)
N_DIM_DEFAULT: int = 16384

# Load axis: v4 x2 (capacity-preserving for 2x N)
CAPACITY_LOAD_RATIO_FULL: List[float] = [16.0, 24.0, 32.0, 48.0]
CAPACITY_LOAD_RATIO_SMOKE: List[float] = [16.0, 32.0, 48.0]

# Decay unchanged from v4
DECAY_RATE_DAYS_FULL: List[int] = [30, 60, 180]
DECAY_RATE_DAYS_SMOKE: List[int] = [30, 180]

# Cardinality (LOCKED)
EXPECTED_N_UNITS_FULL: int = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_FULL)
    * len(CAPACITY_LOAD_RATIO_FULL) * len(N_DIM_SWEEP_FULL)
)  # 5 * 3 * 4 * 1 = 60
EXPECTED_N_UNITS_SMOKE: int = (
    len(ENCODER_FAMILIES) * len(DECAY_RATE_DAYS_SMOKE)
    * len(CAPACITY_LOAD_RATIO_SMOKE) * len(N_DIM_SWEEP_SMOKE)
)  # 5 * 2 * 3 * 1 = 30
assert EXPECTED_N_UNITS_FULL == 60, f"expected 60 got {EXPECTED_N_UNITS_FULL}"
assert EXPECTED_N_UNITS_SMOKE == 30, f"expected 30 got {EXPECTED_N_UNITS_SMOKE}"

# Positive control: binary_bipolar at (dr=180, ld=16.0, N=16384) (v4 ld=8 x2)
POSITIVE_CONTROL: Dict[str, Any] = {
    "encoder_family": "binary_bipolar",
    "decay_rate_days": 180,
    "capacity_load_ratio": 16.0,
    "N_DIM": N_DIM_DEFAULT,
    "expected_pareto_outcome": "TD_DOMINATES",
    "min_recency_decode_acc": 0.60,  # slightly relaxed vs v4 (higher load stresses more)
    "max_recency_decode_acc": 0.999,  # must NOT saturate (META_RULE_Q)
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# -------------------------------------------------------------------------
# Selftest (formula-selftests discipline)
# -------------------------------------------------------------------------
def selftest(seed: int, device: torch.device = None) -> Tuple[bool, str]:
    if device is None:
        device = _get_device(strict_gpu=False)
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 60:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 60"
    if EXPECTED_N_UNITS_SMOKE != 30:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 30"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} "
        f"SMOKE={EXPECTED_N_UNITS_SMOKE} (v4 x2 load; N=16384 only)"
    )

    # 2. Pre-flight encoder distinctness (META_RULE_AY)
    ok, hashes, pf_msg = verify_encoder_distinctness_preflight(seed, device, dim=1024)
    if not ok:
        return False, pf_msg
    msgs.append(pf_msg)

    # Verify at N=16384 (target dim)
    ok2, hashes2, pf_msg2 = verify_encoder_distinctness_preflight(seed, device, dim=16384)
    if not ok2:
        return False, pf_msg2
    msgs.append(f"preflight_distinct(dim=16384): {hashes2}")

    # 3. Recency decode fidelity per encoder at smaller dim (fast; selftest budget)
    # Sanity-check at dim=4096 (v4 known-good dim; primitives should work)
    decode_accs: Dict[str, float] = {}
    n_atoms_dec = 200
    n_buckets_dec = 32
    dim_dec = 4096
    n_days_san = 180
    arrival_d, lastq_d, _ = simulate_atom_timeline(
        n_atoms_dec, n_days_san, 1.0, QUERY_DECAY_TAU, seed + 1,
    )
    for fam in ENCODER_FAMILIES:
        store = build_encoded_atom_store(
            fam, n_atoms_dec, lastq_d, n_days_san, n_buckets_dec, dim_dec,
            seed + 1, device, noise_sigma=0.0,
        )
        _, acc = decode_recency_buckets(store)
        decode_accs[fam] = round(acc, 3)
        del store
        if device.type == "cuda":
            torch.cuda.empty_cache()
        if acc < 0.50:
            return False, (
                f"recency decode FAIL {fam}: acc={acc:.3f} < 0.50 at "
                f"n_atoms={n_atoms_dec} n_buckets={n_buckets_dec} dim={dim_dec}"
            )
    msgs.append(
        f"recency_decode_acc per encoder(dim={dim_dec}, noise=0): {decode_accs}"
    )

    # 4. Positive control: binary_bipolar at v1 op-point (dr=180, ld=16, N=16384)
    # This is the KEY selftest -- if PC saturates at N=16384 the entire cell fails.
    pt = eval_phase_point(
        encoder_family="binary_bipolar",
        decay_rate_days=POSITIVE_CONTROL["decay_rate_days"],
        capacity_load_ratio=POSITIVE_CONTROL["capacity_load_ratio"],
        n_atoms=N_ATOMS_BASE, n_days=N_DAYS_SIM, n_buckets=R_BUCKETS,
        dim=POSITIVE_CONTROL["N_DIM"],
        seed=13, device=device, noise_sigma=NOISE_SIGMA,
    )
    if pt["pareto_outcome"] != POSITIVE_CONTROL["expected_pareto_outcome"]:
        return False, (
            f"Positive control FAIL: v1 op-point "
            f"expected {POSITIVE_CONTROL['expected_pareto_outcome']}, "
            f"got {pt['pareto_outcome']}; "
            f"td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
            f"rec={pt['recency_decode_acc']:.3f}"
        )
    if pt["recency_decode_acc"] < POSITIVE_CONTROL["min_recency_decode_acc"]:
        return False, (
            f"Positive control recency_decode_acc too low at N=16384: "
            f"{pt['recency_decode_acc']:.3f} < "
            f"{POSITIVE_CONTROL['min_recency_decode_acc']}"
        )
    if pt["recency_decode_acc"] > POSITIVE_CONTROL["max_recency_decode_acc"]:
        return False, (
            f"Positive control SATURATED at N=16384 (META_RULE_Q): "
            f"recency_decode_acc={pt['recency_decode_acc']:.3f} > "
            f"{POSITIVE_CONTROL['max_recency_decode_acc']}; "
            f"v4's saturation rationale for N=16384 CONFIRMED; load axis "
            f"needs further raising to escape saturation regime"
        )
    msgs.append(
        f"positive_control v1: binary_bipolar @ (dr=180, ld=16.0, N=16384, "
        f"noise=0.1) pareto={pt['pareto_outcome']} "
        f"td.ws={pt['ARM_TIME_DECAY_EVICTION']['working_set_retention']:.3f} "
        f"rec={pt['recency_decode_acc']:.3f} saturated={pt['saturated']}"
    )

    # 5. Pareto dominance unit-checks (inherited from v4)
    assert pareto_dominance_outcome(0.9, 0.1, 0.5, 0.4) == "TD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.4, 0.9, 0.1) == "RD_DOMINATES"
    assert pareto_dominance_outcome(0.5, 0.3, 0.5, 0.3) == "TIE"
    assert pareto_dominance_outcome(0.9, 0.4, 0.5, 0.1) == "TIE"
    assert pareto_dominance_outcome(float("nan"), 0.1, 0.5, 0.4) == "TIE"
    msgs.append("pareto_dominance unit-tests pass")

    return True, "; ".join(msgs)


# -------------------------------------------------------------------------
# Per-seed phase sweep (v1 axis; reuses v4 eval_phase_point)
# -------------------------------------------------------------------------
def run_one_seed_phase_diagram(
    seed: int, run_mode: str, device: torch.device,
) -> Dict[str, Any]:
    """Run all (encoder, decay, load, N_dim=16384) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    decay_sweep = DECAY_RATE_DAYS_SMOKE if is_smoke else DECAY_RATE_DAYS_FULL
    load_sweep = CAPACITY_LOAD_RATIO_SMOKE if is_smoke else CAPACITY_LOAD_RATIO_FULL
    dim_sweep = N_DIM_SWEEP_SMOKE if is_smoke else N_DIM_SWEEP_FULL
    expected_n = (
        len(ENCODER_FAMILIES) * len(decay_sweep)
        * len(load_sweep) * len(dim_sweep)
    )

    # PRE-FLIGHT GATE (META_RULE_AY): encoder distinctness at cell entry
    preflight_ok, preflight_hashes, preflight_msg = verify_encoder_distinctness_preflight(
        seed, device, dim=1024,
    )

    print(
        f"[run_one_seed v1_N16384] seed={seed} mode={run_mode} device={device} "
        f"encoders={ENCODER_FAMILIES} decay_axis={decay_sweep} "
        f"load_axis={load_sweep} dim_axis={dim_sweep} "
        f"NOISE_SIGMA={NOISE_SIGMA} R_BUCKETS={R_BUCKETS} "
        f"n_atoms={N_ATOMS_BASE} expected_n={expected_n}",
        flush=True,
    )
    print(f"[preflight] {preflight_msg}", flush=True)

    if not preflight_ok:
        return {
            "seed": seed,
            "run_mode": run_mode,
            "preflight_ok": False,
            "preflight_hashes": preflight_hashes,
            "preflight_msg": preflight_msg,
            "phase_map": [],
            "per_encoder_summary": {},
            "encoder_tiers": {},
            "encoder_pair_distinctness": {},
            "n_pairs_differ": 0,
            "n_pairs_total": 10,
            "arms_differ_per_encoder": {},
            "positive_control_result": {"pass": False, "outcome": "PREFLIGHT_FAIL"},
            "cardinality_ok": False,
            "expected_n_units": expected_n,
            "observed_n_units": 0,
            "elapsed_seed_s": 0.0,
        }

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for fam in ENCODER_FAMILIES:
        for dr in decay_sweep:
            for cl in load_sweep:
                for nd in dim_sweep:
                    pt = eval_phase_point(
                        encoder_family=fam, decay_rate_days=dr,
                        capacity_load_ratio=cl, n_atoms=N_ATOMS_BASE,
                        n_days=N_DAYS_SIM, n_buckets=R_BUCKETS, dim=nd,
                        seed=seed, device=device, noise_sigma=NOISE_SIGMA,
                    )
                    phase_map.append(pt)
                    td = pt["ARM_TIME_DECAY_EVICTION"]
                    rd = pt["ARM_RANDOM_EVICTION"]
                    sat_marker = "[SAT]" if pt["saturated"] else "     "
                    print(
                        f"[pt] s={seed} {fam[:14]:<14} dr={dr:>3} ld={cl:.1f} "
                        f"N={nd:>5} td.ws={td['working_set_retention']:.3f} "
                        f"rd.ws={rd['working_set_retention']:.3f} "
                        f"pareto={pt['pareto_outcome']:<14} "
                        f"rec={pt['recency_decode_acc']:.3f} {sat_marker} "
                        f"t={pt['wall_s']:.2f}s",
                        flush=True,
                    )

    elapsed = time.time() - t0
    observed_n = len(phase_map)
    cardinality_ok = (observed_n == expected_n)

    # Per-encoder summary
    per_encoder_summary: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        outcomes = [p["pareto_outcome"] for p in fam_pts]
        td_wins = sum(1 for o in outcomes if o == "TD_DOMINATES")
        rd_wins = sum(1 for o in outcomes if o == "RD_DOMINATES")
        ties = sum(1 for o in outcomes if o == "TIE")
        n_pts_fam = len(fam_pts)
        dom_rate = (td_wins + 0.5 * ties) / max(n_pts_fam, 1)
        net_dom = (td_wins - rd_wins) / max(n_pts_fam, 1)
        rd_loss = rd_wins / max(n_pts_fam, 1)
        decode_accs = [p["recency_decode_acc"] for p in fam_pts]
        sat_counts = sum(1 for p in fam_pts if p["saturated"])
        per_encoder_summary[fam] = {
            "n_points": n_pts_fam,
            "td_wins": td_wins,
            "rd_wins": rd_wins,
            "ties": ties,
            "dominance_rate": round(dom_rate, 4),
            "net_dominance": round(net_dom, 4),
            "rd_loss_rate": round(rd_loss, 4),
            "recency_decode_acc_mean": round(
                float(np.mean(decode_accs)), 4) if decode_accs else 0.0,
            "recency_decode_acc_std": round(
                float(np.std(decode_accs)), 4) if decode_accs else 0.0,
            "n_saturated_cells": sat_counts,
            "saturation_frac": round(sat_counts / max(n_pts_fam, 1), 4),
        }

    # Cross-encoder pair distinctness (META_RULE_AX; C(5,2)=10 pairs)
    encoder_outcome_hashes: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = sorted(
            [p for p in phase_map if p["encoder_family"] == fam],
            key=lambda p: (p["decay_rate_days"], p["capacity_load_ratio"],
                            p["N_dim_input"]),
        )
        payload = json.dumps(
            [(p["pareto_outcome"],
              round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4),
              round(p["recency_decode_acc"], 4))
             for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        encoder_outcome_hashes[fam] = hashlib.sha256(payload).hexdigest()[:16]

    fams = list(ENCODER_FAMILIES)
    pairs_differ: Dict[str, bool] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (encoder_outcome_hashes[fams[i]]
                                  != encoder_outcome_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)
    n_pairs_total = len(pairs_differ)

    # Cross-encoder metric distinctness
    cross_enc_metric_distinct: Dict[str, float] = {}
    cells_by_grid: Dict[Tuple[int, float, int], Dict[str, float]] = {}
    for p in phase_map:
        key = (p["decay_rate_days"], p["capacity_load_ratio"], p["N_dim_input"])
        if key not in cells_by_grid:
            cells_by_grid[key] = {}
        cells_by_grid[key][p["encoder_family"]] = p["recency_decode_acc"]
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            pair_key = f"{fams[i]}_vs_{fams[j]}"
            deltas = []
            for grid_cell, accs in cells_by_grid.items():
                if fams[i] in accs and fams[j] in accs:
                    deltas.append(abs(accs[fams[i]] - accs[fams[j]]))
            cross_enc_metric_distinct[pair_key] = round(
                float(np.mean(deltas)) if deltas else 0.0, 4)
    n_pairs_metric_distinct = sum(
        1 for v in cross_enc_metric_distinct.values() if v >= 0.05
    )

    # Arms-differ per encoder (mechanism gate)
    arms_differ_per_enc: Dict[str, Dict[str, Any]] = {}
    for fam in ENCODER_FAMILIES:
        fam_pts = [p for p in phase_map if p["encoder_family"] == fam]
        td_payload = json.dumps(
            [round(p["ARM_TIME_DECAY_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        rd_payload = json.dumps(
            [round(p["ARM_RANDOM_EVICTION"]["composite"], 4) for p in fam_pts],
            sort_keys=True,
        ).encode("utf-8")
        td_hash = hashlib.sha256(td_payload).hexdigest()[:16]
        rd_hash = hashlib.sha256(rd_payload).hexdigest()[:16]
        arms_differ_per_enc[fam] = {
            "mechanism_hash": td_hash,
            "random_hash": rd_hash,
            "differ": td_hash != rd_hash,
        }

    # Positive control (v1 op-point)
    pc_matches = [
        p for p in phase_map
        if p["encoder_family"] == POSITIVE_CONTROL["encoder_family"]
        and p["decay_rate_days"] == POSITIVE_CONTROL["decay_rate_days"]
        and abs(p["capacity_load_ratio"]
                - POSITIVE_CONTROL["capacity_load_ratio"]) < 1e-6
        and p["N_dim_input"] == POSITIVE_CONTROL["N_DIM"]
    ]
    if pc_matches:
        pc_pt = pc_matches[0]
        pc_outcome = pc_pt["pareto_outcome"]
        pc_decode = pc_pt["recency_decode_acc"]
        pc_pass = (pc_outcome == POSITIVE_CONTROL["expected_pareto_outcome"]
                    and pc_decode >= POSITIVE_CONTROL["min_recency_decode_acc"]
                    and pc_decode <= POSITIVE_CONTROL["max_recency_decode_acc"])
    else:
        pc_outcome = "MISSING"
        pc_decode = -1.0
        pc_pass = False

    positive_control_result = {
        "target": POSITIVE_CONTROL,
        "measured_outcome": pc_outcome,
        "measured_recency_decode_acc": pc_decode,
        "pass": pc_pass,
    }

    # Saturation total
    n_saturated_total = sum(1 for p in phase_map if p["saturated"])
    saturation_frac = n_saturated_total / max(observed_n, 1)

    # Encoder tier classification
    means = {fam: per_encoder_summary[fam]["dominance_rate"]
             for fam in ENCODER_FAMILIES}
    best = max(means.values()) if means else 0.0
    encoder_tiers: Dict[str, str] = {}
    for fam in ENCODER_FAMILIES:
        m = means[fam]
        if m >= best - 0.05:
            others = [v for k, v in means.items() if k != fam]
            next_best = max(others) if others else 0.0
            if m == best and m - next_best > 0.10:
                encoder_tiers[fam] = "DOMINANT_ENCODER"
            else:
                encoder_tiers[fam] = "COMPETITIVE_ENCODER"
        else:
            encoder_tiers[fam] = "DOMINATED_ENCODER"

    return {
        "seed": seed,
        "run_mode": run_mode,
        "encoder_families": list(ENCODER_FAMILIES),
        "decay_sweep": decay_sweep,
        "load_sweep": load_sweep,
        "dim_sweep": dim_sweep,
        "noise_sigma": NOISE_SIGMA,
        "N_DIM_DEFAULT": N_DIM_DEFAULT,
        "R_BUCKETS": R_BUCKETS,
        "n_atoms": N_ATOMS_BASE,
        "n_days": N_DAYS_SIM,
        "preflight_ok": True,
        "preflight_hashes": preflight_hashes,
        "preflight_msg": preflight_msg,
        "phase_map": phase_map,
        "per_encoder_summary": per_encoder_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "cross_encoder_metric_distinct": cross_enc_metric_distinct,
        "n_pairs_metric_distinct": n_pairs_metric_distinct,
        "arms_differ_per_encoder": arms_differ_per_enc,
        "positive_control_result": positive_control_result,
        "n_saturated_cells_total": n_saturated_total,
        "saturation_frac_total": round(saturation_frac, 4),
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "elapsed_seed_s": round(elapsed, 2),
    }


# -------------------------------------------------------------------------
# Smoke gate predicate + verdict emitter (v1 tuned for N=16384 regime)
# -------------------------------------------------------------------------
def smoke_gate_predicate(body: Dict[str, Any]) -> Tuple[bool, str]:
    if not body.get("preflight_ok", False):
        return False, f"preflight_fail: {body.get('preflight_msg', 'unknown')}"

    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    expected_n = body.get("expected_n_units", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc = body.get("per_encoder_summary", {})
    saturation_frac = body.get("saturation_frac_total", 0.0)
    n_pairs_metric_distinct = body.get("n_pairs_metric_distinct", 0)

    if len(phase_map) != expected_n:
        return False, (
            f"cardinality_breach: expected {expected_n} got {len(phase_map)}"
        )

    for fam in ENCODER_FAMILIES:
        ad = arms_differ.get(fam, {})
        if not ad.get("differ"):
            return False, (
                f"arms_identical_encoder_{fam}: TD and RD per-encoder hashes match"
            )

    n_pairs_total = len(pairs_differ)
    n_distinct = sum(1 for v in pairs_differ.values() if v)
    if n_distinct < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        return False, (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_distinct}/{n_pairs_total} pairs differ; collapsed: {collapsed}"
        )

    if n_pairs_metric_distinct < 7:
        return False, (
            f"HARD_FAIL_METRIC_COLLAPSE: only {n_pairs_metric_distinct}/10 pairs "
            f"have |delta recency_decode| >= 0.05 at N=16384"
        )

    # v1 saturation: v4's N=16384 concern -- STRICT no-saturation at smoke
    if saturation_frac > 0.0:
        return False, (
            f"HARD_FAIL_SATURATION_N16384 (META_RULE_Q): {saturation_frac:.3f} "
            f"of cells saturate at recall=1.000; v4's N=16384 saturation "
            f"rationale CONFIRMED; load axis {CAPACITY_LOAD_RATIO_SMOKE} "
            f"insufficient to escape saturation at N=16384"
        )

    if not pc_result.get("pass"):
        return False, (
            f"positive_control_fail: target={pc_result.get('target')} "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )

    failing_decode = {}
    for fam in ENCODER_FAMILIES:
        rda = per_enc.get(fam, {}).get("recency_decode_acc_mean", 0.0)
        if rda < HP_RECENCY_DECODE_FLOOR:
            failing_decode[fam] = rda
    if failing_decode:
        return False, (
            f"HARD_FAIL_READOUT_FLOOR (META_RULE_AP): per-encoder "
            f"recency_decode_acc_mean below {HP_RECENCY_DECODE_FLOOR}: "
            f"{failing_decode}"
        )

    fams_above = [fam for fam in ENCODER_FAMILIES
                   if per_enc.get(fam, {}).get("dominance_rate", 0.0) >= 0.50]
    if len(fams_above) < 2:
        rates = {fam: per_enc.get(fam, {}).get("dominance_rate", 0.0)
                  for fam in ENCODER_FAMILIES}
        return False, (
            f"discriminator_fails_scale: only {len(fams_above)} encoders "
            f"show dominance_rate >= 0.50 at smoke at N=16384; rates={rates}"
        )

    return True, (
        f"smoke_gate_pass_v1_N16384: preflight_distinct + cardinality_ok + "
        f"arms_differ(5 enc) + pairs_differ={n_distinct}/{n_pairs_total} + "
        f"metric_distinct={n_pairs_metric_distinct}/10 + no_saturation@N=16384 + "
        f"positive_control_pass + readout_floor_ok + >=2 enc above dominance"
    )


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_NO_SEEDS: empty per_seed",
            "summary": "HARD_FAIL_NO_SEEDS",
        }

    is_smoke = (run_mode == "smoke")
    seed_key = list(per_seed.keys())[0]
    body = per_seed[seed_key]
    phase_map = body.get("phase_map", [])
    arms_differ = body.get("arms_differ_per_encoder", {})
    pairs_differ = body.get("encoder_pair_distinctness", {})
    n_pairs_differ = body.get("n_pairs_differ", 0)
    n_pairs_total = body.get("n_pairs_total", 10)
    cross_enc_metric_distinct = body.get("cross_encoder_metric_distinct", {})
    n_pairs_metric_distinct = body.get("n_pairs_metric_distinct", 0)
    pc_result = body.get("positive_control_result", {})
    per_enc_summary = body.get("per_encoder_summary", {})
    encoder_tiers = body.get("encoder_tiers", {})
    expected_n = body.get("expected_n_units", 0)
    observed_n = body.get("observed_n_units", 0)
    cardinality_ok = body.get("cardinality_ok", False)
    preflight_ok = body.get("preflight_ok", False)
    preflight_msg = body.get("preflight_msg", "")
    preflight_hashes = body.get("preflight_hashes", {})
    saturation_frac = body.get("saturation_frac_total", 0.0)
    n_saturated = body.get("n_saturated_cells_total", 0)

    outcomes = [p["pareto_outcome"] for p in phase_map]
    n_td = sum(1 for o in outcomes if o == "TD_DOMINATES")
    n_rd = sum(1 for o in outcomes if o == "RD_DOMINATES")
    n_tie = sum(1 for o in outcomes if o == "TIE")

    n_total = len(phase_map)
    overall_dom_rate = (n_td + 0.5 * n_tie) / max(n_total, 1)
    overall_net = (n_td - n_rd) / max(n_total, 1)
    overall_rd_loss = n_rd / max(n_total, 1)

    enc_chain_grade: Dict[str, bool] = {}
    for fam in ENCODER_FAMILIES:
        s = per_enc_summary.get(fam, {})
        passes = (
            s.get("dominance_rate", 0.0) >= HP_DOMINANCE_RATE_LO
            and s.get("net_dominance", 0.0) >= HP_NET_DOMINANCE_LO
            and s.get("rd_loss_rate", 1.0) <= HP_RD_LOSS_RATE_HI
            and s.get("recency_decode_acc_mean", 0.0) >= HP_RECENCY_DECODE_FLOOR
        )
        enc_chain_grade[fam] = passes
    n_chain_grade = sum(1 for v in enc_chain_grade.values() if v)

    common = {
        "preflight_ok": preflight_ok,
        "preflight_msg": preflight_msg,
        "preflight_hashes": preflight_hashes,
        "phase_map": phase_map,
        "per_encoder_summary": per_enc_summary,
        "encoder_tiers": encoder_tiers,
        "encoder_pair_distinctness": pairs_differ,
        "n_pairs_differ": n_pairs_differ,
        "n_pairs_total": n_pairs_total,
        "cross_encoder_metric_distinct": cross_enc_metric_distinct,
        "n_pairs_metric_distinct": n_pairs_metric_distinct,
        "arms_differ_per_encoder": arms_differ,
        "positive_control_result": pc_result,
        "saturation_frac_total": saturation_frac,
        "n_saturated_cells_total": n_saturated,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_n,
        "observed_n_units": observed_n,
        "pareto_outcome_counts": {
            "TD_DOMINATES": n_td, "RD_DOMINATES": n_rd, "TIE": n_tie},
        "overall_dominance_rate": round(overall_dom_rate, 4),
        "overall_net_dominance": round(overall_net, 4),
        "overall_rd_loss_rate": round(overall_rd_loss, 4),
        "per_encoder_chain_grade_pass": enc_chain_grade,
        "n_encoders_chain_grade": n_chain_grade,
        "N_DIM_sweep": body.get("dim_sweep"),
        "R_BUCKETS": body.get("R_BUCKETS"),
        "noise_sigma": body.get("noise_sigma", NOISE_SIGMA),
    }

    if not preflight_ok:
        out = dict(common)
        out.update({
            "verdict": "HARD_FAIL",
            "verdict_msg": f"HARD_FAIL_PREFLIGHT_v1_N16384: {preflight_msg}",
            "summary": "HARD_FAIL_PREFLIGHT_v1_N16384",
        })
        return out

    if is_smoke:
        passed, reason = smoke_gate_predicate(body)
        if passed:
            base_verdict = "HARD_PASS"
            base_vmsg = (
                f"HARD_PASS_SMOKE_v1_N16384: {observed_n}/{expected_n} pts; "
                f"td_wins={n_td}/{n_total} rd_wins={n_rd}/{n_total} "
                f"ties={n_tie}/{n_total}; overall_dom={overall_dom_rate:.3f}; "
                f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
                f"metric_distinct={n_pairs_metric_distinct}/10; "
                f"saturation_frac={saturation_frac:.3f}; "
                f"positive_control_pass; n_encoders_chain_grade={n_chain_grade}/5"
            )
        else:
            base_verdict = "HARD_FAIL"
            base_vmsg = (
                f"HARD_FAIL_SMOKE_v1_N16384: {reason}; "
                f"td_wins={n_td} rd_wins={n_rd} ties={n_tie}"
            )

        final_verdict, final_vmsg = emit_verdict_with_AY(
            base_verdict, base_vmsg, pairs_differ,
        )
        out = dict(common)
        out.update({
            "verdict": final_verdict,
            "verdict_msg": final_vmsg,
            "summary": final_vmsg,
            "smoke_gate_pass": passed,
            "smoke_gate_reason": reason,
            "base_verdict_pre_AY": base_verdict,
        })
        return out

    # FULL verdict
    if not cardinality_ok:
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_CARDINALITY_BREACH: expected={expected_n} "
            f"observed={observed_n}"
        )
    elif any(not ad.get("differ") for ad in arms_differ.values()):
        bad = [fam for fam in ENCODER_FAMILIES
               if not arms_differ.get(fam, {}).get("differ")]
        base_verdict = "HARD_FAIL"
        base_vmsg = f"HARD_FAIL_ARMS_IDENTICAL: encoders with TD==RD: {bad}"
    elif n_pairs_differ < HP_MIN_PAIRS_DIFFER:
        collapsed = [k for k, v in pairs_differ.items() if not v]
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_DEGENERATE_ENCODERS (META_RULE_AX): "
            f"{n_pairs_differ}/{n_pairs_total} pairs differ; collapsed: {collapsed}"
        )
    elif saturation_frac >= SATURATION_HARD_FAIL_FRAC:
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_SATURATION_N16384 (META_RULE_Q): "
            f"{saturation_frac:.3f} (>= {SATURATION_HARD_FAIL_FRAC}) of cells "
            f"saturate at N=16384; v4's saturation rationale CONFIRMED"
        )
    elif not pc_result.get("pass"):
        base_verdict = "HARD_FAIL"
        base_vmsg = (
            f"HARD_FAIL_CONTROL_FAIL: positive_control "
            f"outcome={pc_result.get('measured_outcome')} "
            f"recency={pc_result.get('measured_recency_decode_acc')}"
        )
    elif (n_chain_grade >= 4 and overall_dom_rate >= HP_DOMINANCE_RATE_LO
          and n_pairs_metric_distinct >= 7):
        base_verdict = "HARD_PASS"
        base_vmsg = (
            f"HARD_PASS_ENCODER_DISCRIMINATION_v1_N16384: {observed_n}/{expected_n} pts; "
            f"{n_chain_grade}/5 encoders pass CG; overall_dom={overall_dom_rate:.3f}; "
            f"pairs_differ={n_pairs_differ}/{n_pairs_total}; "
            f"metric_distinct={n_pairs_metric_distinct}/10; "
            f"saturation_frac={saturation_frac:.3f}; "
            f"encoder_tiers={encoder_tiers}; positive_control_pass; "
            f"encoder_family_CG_extends_to_N=16384_with_load_axis_x2"
        )
    elif overall_dom_rate >= 0.60 and n_pairs_differ >= HP_MIN_PAIRS_DIFFER:
        base_verdict = "MIDDLE_BAND"
        base_vmsg = (
            f"MIDDLE_BAND_ENCODER_DIFFERS_BUT_LOW_CHAIN_GRADE_N16384: "
            f"{n_chain_grade}/5 CG; overall_dom={overall_dom_rate:.3f}; "
            f"metric_distinct={n_pairs_metric_distinct}/10; tiers={encoder_tiers}"
        )
    else:
        base_verdict = "MIDDLE_BAND"
        base_vmsg = (
            f"MIDDLE_BAND_LOW_DISCRIMINATION_N16384: overall_dom="
            f"{overall_dom_rate:.3f}; pairs_differ={n_pairs_differ}; "
            f"n_chain_grade={n_chain_grade}/5"
        )

    final_verdict, final_vmsg = emit_verdict_with_AY(
        base_verdict, base_vmsg, pairs_differ,
    )
    out = dict(common)
    out.update({
        "verdict": final_verdict,
        "verdict_msg": final_vmsg,
        "summary": final_vmsg,
        "base_verdict_pre_AY": base_verdict,
    })
    return out


__all__ = [
    "ENCODER_FAMILIES",
    "DECAY_RATE_DAYS_FULL", "CAPACITY_LOAD_RATIO_FULL", "N_DIM_SWEEP_FULL",
    "DECAY_RATE_DAYS_SMOKE", "CAPACITY_LOAD_RATIO_SMOKE", "N_DIM_SWEEP_SMOKE",
    "EXPECTED_N_UNITS_FULL", "EXPECTED_N_UNITS_SMOKE",
    "N_DIM_DEFAULT", "NOISE_SIGMA",
    "POSITIVE_CONTROL", "REQUIRED_FIELDS",
    "_get_device", "get_backend_label",
    "selftest", "run_one_seed_phase_diagram",
    "smoke_gate_predicate", "aggregate_and_verdict",
]
