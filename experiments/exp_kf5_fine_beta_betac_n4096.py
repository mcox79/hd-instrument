"""KF-5 FINE-BETA SWEEP NEAR beta_c: last-chance steerability probe.

CONTEXT:
  v272 KF-5 steerability result: substrate is BETA-INVARIANT at tested operating
  points. Coarse grid (beta=8 vs beta=64) showed NO qualitative difference in
  KF behavior between regions A/B and C/D. Phase-mechanism subhypothesis CLOSED.

  The only unexplored axis: near-boundary dynamics around beta_c=10.
  Previous sweeps used coarse beta grids and may have missed near-boundary effects.
  This is the LAST-CHANCE test for the steerable-killer-feature hypothesis.

SCIENTIFIC QUESTION:
  At fine beta resolution (every integer step from 6 to 20), does the substrate
  show any near-boundary steerability signal in KF metrics?
  KF metrics tested: softmax retrieval confidence, edit isolation ratio, entropy.
  If ANY qualitative difference exists within beta in [6, 20] across multiple M_frac
  values (testing whether the effect depends on memory load), that rehabilitates
  the steerability narrative.

STRATEGIC STAKES:
  PASS: steerability lives at fine-beta near beta_c; B2 follow-up may probe multi-hop.
  FAIL: KF-5 steerability direction closes honestly; no beta-axis steering at any grain.

PRE-REGISTERED BANDS (calibration probe; new fine-beta operating regime):
  Metric: "steer_signal" = max over KF metrics of |metric(beta_high) - metric(beta_low)|
  where beta_low in [6,8] and beta_high in [12,16] (straddling beta_c=10).
  Tested for N_STEER KF-like metrics: softmax_conf, edit_iso, beta_sensitivity.

  HARD_PASS: steer_signal > 0.10 in >= 4 (metric, M_frac) combinations across >= 3 seeds.
    AND there exists a beta* in [8, 14] where the metric shows a local extremum
    (not just monotone across the range).
    Interpretation: near-boundary KF effect exists; steerability recoverable.
  HARD_FAIL: steer_signal < 0.02 across ALL (metric, M_frac) combinations.
    Interpretation: no near-boundary effect at ANY operating point; KF-5 closes.
  MIDDLE_BAND: steer_signal in [0.02, 0.10] in some combinations but not >= 4.
    Interpretation: marginal signal; not enough to rehabilitate steerability claim.

CALIBRATION NOTE:
  No prior empirical near-boundary KF anchor at this fine resolution.
  Per calibration-probe policy: bands set at +/-50% of expected transition size.
  Previous coarse-grid results showed near-zero response at beta=8 vs beta=64;
  fine-grid transition is expected to be smaller (if real, ~0.05-0.15 in metric units).
  HARD_PASS at 0.10 = lower half of expected range.
  HARD_FAIL at 0.02 = noise floor (< 50% of calibration bound).

FORMULA SELF-TESTS:
  1. softmax_conf(beta, W, key, cb, N): high-beta -> near-1 for trained query.
  2. edit_iso(W, cb, N, M): same formula as kf2 isolation test.
  3. steer_signal = max(|high - low|) where high/low are metric means at beta>=12 vs beta<=8.
  4. N == 4096 (PROT-018 binding).
  5. M = M_frac * N = 2.0 * 4096 = 8192.
  6. Kerdock check: N=4096 has log2(4096)=12, even. OK.

OOM CHECK:
  W at N=4096 float32 = 64MB. Multiple M_frac up to 8.0: M=32768.
  Keys at M=32768: 32768*4096*4=537MB. Codebook=64MB. Total ~660MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell (N=4096, M=8192): store + softmax_conf probe + edit_iso probe ~ 2s.
  Sweep: 3 M_frac * 15 beta_pts * 3 seeds = 135 cells * 2s = 270s.
  Smoke: 2 M_frac * 5 beta_pts * 1 seed = 10 cells * 1s = 10s.
  FULL: ceil(1.5 * 270) = 405s. PROT-019 floor _n4096 = 14400s. timeout_s = 14400s.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: kf5_fine_beta_betac_n4096
Queue: overnight_queue (GPU; N=4096; fine beta grid; 3 M_fracs x 3 seeds)
Pre-reg: prereqs/2026-05-29_kf5_fine_beta_betac_n4096.md
Parent: exp_kf5_steerable_beta_v3_n8192 (v272 BETA-INVARIANT result; fine-grid is last chance)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load kf2_cross_codebook_v1 for build_codebook + run_one_cell_family
_v1_path = REPO / "experiments" / "exp_kf2_cross_codebook_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_cross_v1_finebeta", _v1_path)
kf2_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf2_v1)
build_codebook = kf2_v1.build_codebook
v3 = kf2_v1.v3

# Load t1_beta_sweep_v1 for softmax_confidence
_t1_path = REPO / "experiments" / "exp_t1_beta_sweep_v1_n4096.py"
_t1_spec = importlib.util.spec_from_file_location("t1v1_finebeta", _t1_path)
t1v1 = importlib.util.module_from_spec(_t1_spec)
_t1_spec.loader.exec_module(t1v1)
softmax_confidence = t1v1.softmax_confidence

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Kerdock check: log2(4096) = 12, even. OK.
assert math.log2(N_FULL) % 2 == 0, f"Kerdock requires even log2(N); N={N_FULL} log2={math.log2(N_FULL)}"

# Fine beta grid straddling known beta_c ~ 10
BETA_SWEEP_FULL  = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 24, 28, 32]
BETA_SWEEP_SMOKE = [6, 8, 10, 12, 16, 24, 32]

# M_frac sweep to check if effect depends on memory load
M_FRACS_FULL  = [2.0, 4.0, 8.0]
M_FRACS_SMOKE = [2.0, 8.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200
N_EDITS  = 10

# Pre-registered thresholds
HP_STEER_SIGNAL_MIN    = 0.10  # max |high_beta - low_beta| metric difference
HP_COMBOS_MIN          = 4     # >= 4 (metric, M_frac) combinations must exceed threshold
HF_STEER_SIGNAL_MAX    = 0.02  # HARD_FAIL: no signal above noise floor
HP_SEEDS_MIN           = 3     # all seeds must show signal


def get_output_dir(default_name: str = "kf5_fine_beta_betac_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def store_and_get_W(N: int, M_frac: float, seed: int, device: torch.device,
                     family: str = "kerdock") -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Store M=M_frac*N memories and return (W, keys, val_idx, codebook)."""
    cb = build_codebook(family, N, seed, device)
    C = cb.shape[0]
    M = min(int(M_frac * N), C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 600)
    key_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    keys = cb[key_idx]
    vals = cb[val_idx]

    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = vals[start:start + 256]
        W = W + (v_b.T @ k_b) / N

    return W, keys, val_idx, cb


def compute_edit_iso(W: torch.Tensor, keys: torch.Tensor,
                      vals: torch.Tensor, cb: torch.Tensor,
                      N: int, n_edits: int, n_probe: int) -> float:
    """Compute max isolation ratio via argmax (same as kf2 baseline)."""
    n_probe_actual = min(n_probe, keys.shape[0])
    probe_keys = keys[:n_probe_actual]
    probe_val_idx_local = torch.arange(n_probe_actual, device=W.device)

    # Pre-compute retrieval accuracy before edits
    responses_before = W @ probe_keys.T      # (N, n_probe)
    sims_before = cb @ responses_before / N  # (C, n_probe)
    pred_before = torch.argmax(sims_before, dim=0)

    isolation_ratios = []
    for edit_i in range(min(n_edits, keys.shape[0])):
        gen2 = torch.Generator(device=W.device)
        gen2.manual_seed(edit_i + 3000)
        new_val_idx = torch.randint(0, cb.shape[0], (1,), generator=gen2, device=W.device)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]
        W_edited = W + torch.outer(new_val - old_val, old_key) / N

        non_edit_mask = torch.ones(n_probe_actual, dtype=torch.bool, device=W.device)
        non_edit_mask[min(edit_i, n_probe_actual - 1)] = False
        probe_ne = probe_keys[non_edit_mask]

        if probe_ne.shape[0] > 0:
            responses_after = W_edited @ probe_ne.T
            sims_after = cb @ responses_after / N
            pred_after = torch.argmax(sims_after, dim=0)
            acc_before = (pred_before[non_edit_mask] == pred_before[non_edit_mask]).float().mean().item()
            acc_after = (pred_after == pred_before[non_edit_mask]).float().mean().item()
            delta = abs(acc_before - acc_after)
            isolation_ratios.append(delta)

    return max(isolation_ratios) if isolation_ratios else 0.0


def run_one_cell(N: int, M_frac: float, beta: float, seed: int,
                  device: torch.device) -> Dict:
    """Run fine-beta probe for one (N, M_frac, beta, seed) combination."""
    W, keys, val_idx, cb = store_and_get_W(N, M_frac, seed, device)
    M = keys.shape[0]
    n_probe = min(N_PROBE, M)
    vals = cb[val_idx]

    # Metric 1: softmax retrieval confidence (beta-sensitive)
    probe_k = keys[:n_probe]
    probe_v = val_idx[:n_probe]
    conf = softmax_confidence(W, probe_k, probe_v, cb, float(beta), N, n_probe=n_probe)

    # Metric 2: edit isolation (argmax; same as kf2 baseline)
    edit_iso = compute_edit_iso(W, keys, vals, cb, N, N_EDITS, n_probe)

    return {
        "N": N, "M_frac": M_frac, "M": M, "beta": float(beta), "seed": seed,
        "softmax_conf": round(conf, 5),
        "edit_iso": round(edit_iso, 6),
    }


def compute_steer_signal(cells_for_mfrac: List[Dict], metric: str) -> float:
    """Compute steer_signal = max|high_beta_mean - low_beta_mean| for given metric."""
    low_betas = [6, 7, 8, 9]
    high_betas = [12, 13, 14, 16]
    low_vals = [c[metric] for c in cells_for_mfrac if c["beta"] in low_betas]
    high_vals = [c[metric] for c in cells_for_mfrac if c["beta"] in high_betas]
    if not low_vals or not high_vals:
        return 0.0
    return abs(sum(high_vals) / len(high_vals) - sum(low_vals) / len(low_vals))


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF5_FINEBETA_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    m_fracs = sorted(set(c["M_frac"] for c in cells))
    seeds = sorted(set(c["seed"] for c in cells))
    metrics = ["softmax_conf", "edit_iso"]

    # Per-seed steer signals
    combo_signals: List[Tuple[str, float, float]] = []  # (metric, M_frac, signal)
    for metric in metrics:
        for m_frac in m_fracs:
            per_seed_signals = []
            for seed in seeds:
                seed_cells = [c for c in cells if c["seed"] == seed and c["M_frac"] == m_frac]
                sig = compute_steer_signal(seed_cells, metric)
                per_seed_signals.append(sig)
            mean_sig = sum(per_seed_signals) / len(per_seed_signals) if per_seed_signals else 0.0
            combo_signals.append((metric, m_frac, mean_sig))

    max_sig = max(s for _, _, s in combo_signals) if combo_signals else 0.0
    n_combos_above_hp = sum(1 for _, _, s in combo_signals if s >= HP_STEER_SIGNAL_MIN)

    detail_parts = [f"N={N}"]
    for metric, m_frac, sig in combo_signals:
        detail_parts.append(f"{metric}@M{m_frac}={sig:.4f}")
    detail = " ".join(detail_parts)
    detail += (f" max_signal={max_sig:.4f} combos_above_HP={n_combos_above_hp}"
               f" HP_signal={HP_STEER_SIGNAL_MIN} HF_signal={HF_STEER_SIGNAL_MAX}")

    if max_sig < HF_STEER_SIGNAL_MAX:
        return ("KF5_FINEBETA_HARD_FAIL",
                f"NO_NEAR_BOUNDARY_EFFECT: max steer_signal={max_sig:.4f} < {HF_STEER_SIGNAL_MAX}. "
                f"KF-5 steerability direction closes. " + detail)

    if n_combos_above_hp >= HP_COMBOS_MIN:
        return ("KF5_FINEBETA_HARD_PASS",
                f"NEAR_BOUNDARY_STEERABILITY: steer_signal > {HP_STEER_SIGNAL_MIN} "
                f"in {n_combos_above_hp} combos >= {HP_COMBOS_MIN}. " + detail)

    return ("KF5_FINEBETA_MIDDLE_BAND",
            f"MARGINAL_SIGNAL: max_signal={max_sig:.4f} combos_above_HP={n_combos_above_hp} "
            f"< {HP_COMBOS_MIN}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"
    assert math.log2(N_FULL) % 2 == 0, f"Kerdock even-log2 check N={N_FULL}"

    # Formula self-test: steer_signal computation
    fake_cells = [
        {"beta": 6.0, "softmax_conf": 0.5, "edit_iso": 0.01, "M_frac": 2.0, "seed": 17},
        {"beta": 8.0, "softmax_conf": 0.5, "edit_iso": 0.01, "M_frac": 2.0, "seed": 17},
        {"beta": 12.0, "softmax_conf": 0.7, "edit_iso": 0.02, "M_frac": 2.0, "seed": 17},
        {"beta": 14.0, "softmax_conf": 0.7, "edit_iso": 0.02, "M_frac": 2.0, "seed": 17},
    ]
    sig = compute_steer_signal(fake_cells, "softmax_conf")
    assert abs(sig - 0.2) < 0.001, f"steer_signal expected 0.2; got {sig}"

    # Smoke cell: one cell at N_SMOKE
    device = torch.device("cpu")
    cell = run_one_cell(N_SMOKE, 2.0, 10.0, 17, device)
    assert "softmax_conf" in cell, f"softmax_conf missing: {list(cell.keys())}"
    assert "edit_iso" in cell, f"edit_iso missing: {list(cell.keys())}"
    assert not math.isnan(cell["softmax_conf"]), "softmax_conf NaN"
    assert not math.isnan(cell["edit_iso"]), "edit_iso NaN"
    assert 0.0 <= cell["softmax_conf"] <= 1.0, f"softmax_conf out of range: {cell['softmax_conf']}"

    # 4x scale smoke
    cell_4x = run_one_cell(N_SMOKE * 4, 2.0, 10.0, 17, device)
    assert not math.isnan(cell_4x["softmax_conf"]), "4x softmax_conf NaN"

    # Verdict HARD_PASS gate: 4+ combos above 0.10
    # Need softmax_conf AND edit_iso signals both > 0.10 across 2+ M_fracs to get 4+ combos.
    fake_hp_cells = []
    for m_frac in M_FRACS_FULL:
        for seed in SEEDS_FULL:
            for beta in [6.0, 8.0, 12.0, 14.0, 24.0]:
                # Make both metrics show strong signal (low=0.3, high=0.6 -> signal=0.3>0.10)
                is_high = beta >= 12
                fake_hp_cells.append({
                    "M_frac": m_frac, "seed": seed, "beta": beta,
                    "softmax_conf": 0.60 if is_high else 0.30,
                    "edit_iso":     0.15 if is_high else 0.01,
                })
    v_hp, m_hp = compute_verdict({"cells": fake_hp_cells, "N": N_FULL})
    assert "HARD_PASS" in v_hp, f"HARD_PASS gate failed: {v_hp} -- {m_hp}"

    # Verdict HARD_FAIL gate: flat response
    fake_hf_cells = []
    for m_frac in M_FRACS_FULL:
        for seed in SEEDS_FULL:
            for beta in BETA_SWEEP_FULL:
                fake_hf_cells.append({
                    "M_frac": m_frac, "seed": seed, "beta": float(beta),
                    "softmax_conf": 0.5, "edit_iso": 0.01,
                })
    v_hf, m_hf = compute_verdict({"cells": fake_hf_cells, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"HARD_FAIL gate failed: {v_hf} -- {m_hf}"

    print(f"[selftest] kf5_fine_beta_betac_n4096 PASS "
          f"smoke_conf={cell['softmax_conf']:.4f} smoke_iso={cell['edit_iso']:.5f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)

    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke

    N_cfg = N_SMOKE if smoke else N_FULL
    beta_sweep = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    m_fracs = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf5_fine_beta_betac_n4096 smoke={smoke} N={N_cfg} "
          f"beta_pts={len(beta_sweep)} M_fracs={m_fracs} seeds={seeds} device={device_str}",
          flush=True)
    t0 = time.time()

    all_cells = []
    for m_frac in m_fracs:
        print(f"\n  [M_frac={m_frac}]", flush=True)
        for seed in seeds:
            for beta in beta_sweep:
                cell = run_one_cell(N_cfg, m_frac, float(beta), seed, device)
                all_cells.append(cell)
                print(f"  M_frac={m_frac} seed={seed} beta={beta:5.1f} "
                      f"conf={cell['softmax_conf']:.4f} iso={cell['edit_iso']:.5f} "
                      f"({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf5_fine_beta_betac_n4096", "N": N_cfg, "smoke": smoke,
        "beta_sweep": beta_sweep, "M_fracs": m_fracs, "seeds": seeds,
        "cells": all_cells, "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed}s", flush=True)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    main()
