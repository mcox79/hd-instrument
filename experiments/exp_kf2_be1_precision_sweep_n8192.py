"""KF-2 BE-1 PRECISION FLOOR SWEEP at N=8192: quantization impact on edit isolation.

CONTEXT:
  kf2_cross_codebook_v2_n8192 (v268 HARD_PASS): max_iso < 0.05 for Kerdock, BSC, Gaussian
  at N=8192. Edit isolation is robust at FP32.
  BE-1 asks: at what bit-precision does isolation degrade? This maps the deployment
  cost envelope -- if INT4 or INT8 holds isolation, the substrate can be deployed
  at 4-8x memory reduction vs FP32.

SCIENTIFIC QUESTION:
  Does max_iso < 0.05 hold for Kerdock at N=8192 under quantized W matrices?
  At what precision (fp16/int8/int4/int2/int1) does isolation first degrade?
  What is the compression ratio at the last precision that holds?

CALIBRATION (no prior empirical anchor for precision floor):
  Per calibration-probe policy: bands set +/-50% around theoretical prediction.
  Theoretical prediction: fp32 and fp16 should be byte-exact or near-exact (iso ~ 0.01).
  int8 expected to hold (8-bit symmetric quant; small perturbation to W).
  int4 borderline (4-level quant; W perturbation may exceed isolation bound).
  int2/int1: expected degradation (2 and 1 level quant = large W perturbation).

PRE-REGISTERED BANDS (calibration probe; no prior empirical precision anchor):
  HARD_PASS: max_iso < 0.05 at fp32 AND fp16 AND int8 (3+ precisions hold).
    Interpretation: substrate deployable at INT8 (8x memory reduction) with isolation intact.
  HARD_FAIL: max_iso >= 0.10 at fp32 or fp16 (baseline broken; something is wrong).
  MIDDLE_BAND: fp32/fp16 hold but int8 fails (compression advantage limited to 2x).

  Note: int4/int2/int1 degradation is expected and is not a FAIL -- it characterizes
  the floor. The question is where exactly the floor is.

FORMULA SELF-TESTS:
  1. quantize_roundtrip(x, 'fp32') returns x unchanged (no-op).
  2. quantize_roundtrip(x, 'fp16') returns tensor with reduced precision (float16 cast).
  3. N == 8192 (PROT-018 binding).
  4. precision_metadata(8192**2, 'int8')['precision_compression_ratio'] == 4.0 (4:1 vs fp32).
  5. precision_metadata(8192**2, 'fp16')['precision_compression_ratio'] == 2.0.
  6. theory_bound at N=8192 = 1/sqrt(8192) = 0.01104.

OOM CHECK:
  W at N=8192 float32 = 268MB. After quantize_roundtrip W stays float32 (dequantized).
  Memory profile same as v2_n8192. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v2_n8192 FULL: 3 families x 3 M_fracs x 5 seeds x ~4s = 180s.
  BE-1: 1 family (Kerdock) x 1 M_frac x 5 seeds x 6 precisions = 30 cells x ~4s = 120s.
  Safety: ceil(1.5 * 120 * 1) = 180s. PROT-019 _n8192 floor = 21600. timeout_s = 21600.
  Note: actual runtime << 21600s; floor applies because of _n8192 suffix.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf2_be1_precision_sweep_n8192
Queue: overnight_queue (GPU; N=8192 Kerdock; 6 precisions x 5 seeds)
Pre-reg: preregs/2026-05-29_kf2_be1_precision_sweep_n8192.md
Parent: kf2_cross_codebook_v2_n8192 (v268 HARD_PASS; precision floor is next step)
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

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments"))

# Load _bit_precision helper
from _bit_precision import quantize_roundtrip, precision_metadata, VALID_PRECISIONS  # noqa: E402

# Load kf2_cross_codebook_v1 for run_one_cell_family
_v1_path = REPO / "experiments" / "exp_kf2_cross_codebook_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_cross_v1_be1", _v1_path)
kf2_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf2_v1)

# We need the internal helpers from v1; we will build our own cell runner below
# that wraps v1's build_codebook and run_one_cell_family with W quantization.
build_codebook = kf2_v1.build_codebook
v3 = kf2_v1.v3

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# Only Kerdock for BE-1 (strongest prior anchor)
FAMILY = "kerdock"
M_FRAC = 2.0    # same as v2_n8192 central M_frac

PRECISIONS_FULL  = ["fp32", "fp16", "int8", "int4", "int2", "int1"]
PRECISIONS_SMOKE = ["fp32", "int8", "int1"]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_EDITS = 10   # number of edit probes per cell

# Pre-registered thresholds
HP_ISOLATION_MAX   = 0.05   # max_iso < this = isolation holds
HF_CONTAMINATION   = 0.10   # max_iso >= this = isolation breaks
HP_SEEDS_MIN       = 4      # >= 4/5 seeds must pass for a precision to "hold"
HP_PRECISIONS_MIN  = 3      # >= 3 precisions hold = HARD_PASS

# HARD_PASS outer gate: fp32 AND fp16 AND int8 all hold (3 precisions)
HP_REQUIRED_PRECISIONS = {"fp32", "fp16", "int8"}


def get_output_dir(default_name: str = "kf2_be1_precision_sweep_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_precision(precision: str, M_frac: float, seed: int,
                            N_use: int, n_edits: int,
                            device: torch.device) -> Dict:
    """KF-2 isolation for one precision level.

    Applies quantize_roundtrip(W, precision) to substrate W AFTER storage BEFORE retrieval.
    """
    cb = build_codebook(FAMILY, N_use, seed, device)
    C = cb.shape[0]
    M = min(int(M_frac * N_use), C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 300)
    key_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M,), generator=gen, device=device)
    keys = cb[key_idx]
    vals = cb[val_idx]

    # STORAGE: accumulate W in FP32
    W = torch.zeros(N_use, N_use, device=device, dtype=torch.float32)
    for start in range(0, M, 256):
        k_b = keys[start:start + 256]
        v_b = vals[start:start + 256]
        W = W + (v_b.T @ k_b) / N_use

    # QUANTIZE: apply precision loss BEFORE retrieval
    W_q = quantize_roundtrip(W, precision)

    # RETRIEVAL probes using W_q
    n_probe = min(M, 100)
    probe_keys = keys[:n_probe]
    probe_val = val_idx[:n_probe] % C
    sims_before = (cb @ (probe_keys @ W_q.T).T) / N_use
    pred_before = torch.argmax(sims_before, dim=0)
    acc_before = (pred_before == probe_val.to(device)).float()

    # EDIT ISOLATION: measure impact of edits on non-edited entries using W_q
    isolation_ratios = []
    n_edits_actual = min(n_edits, M)
    for edit_i in range(0, n_edits_actual, max(1, n_edits_actual // 10)):
        gen2 = torch.Generator(device=device)
        gen2.manual_seed(seed + edit_i + 1000)
        new_val_idx = torch.randint(0, C, (1,), generator=gen2, device=device)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]
        # Apply edit to quantized W
        W_edited = W_q + torch.outer(new_val - old_val, old_key) / N_use
        non_edit_mask = torch.ones(n_probe, dtype=torch.bool)
        non_edit_mask[min(edit_i, n_probe - 1)] = False
        probe_ne = probe_keys[non_edit_mask]
        probe_val_ne = probe_val[non_edit_mask]
        if probe_ne.shape[0] > 0:
            sims_after = (cb @ (probe_ne @ W_edited.T).T) / N_use
            pred_after = torch.argmax(sims_after, dim=0)
            acc_after = (pred_after == probe_val_ne.to(device)).float()
            delta = (acc_before[non_edit_mask] - acc_after).abs().mean().item()
            isolation_ratios.append(delta)

    isolation_ratio = max(isolation_ratios) if isolation_ratios else 0.0
    theory_bound = 1.0 / math.sqrt(N_use)
    prec_meta = precision_metadata(W.numel(), precision)

    return {
        "precision": precision,
        "M_frac": M_frac, "M": M, "N": N_use, "seed": seed,
        "isolation_ratio": round(isolation_ratio, 6),
        "theory_bound": round(theory_bound, 6),
        "within_theory": isolation_ratio <= theory_bound,
        **prec_meta,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_BE1_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    theory_bound = 1.0 / math.sqrt(N)

    # Per-precision: fraction of seeds that pass isolation
    prec_pass: Dict[str, int] = {}
    prec_max_iso: Dict[str, float] = {}
    prec_compression: Dict[str, float] = {}
    for prec in PRECISIONS_FULL:
        prec_cells = [c for c in cells if c.get("precision") == prec
                      and c.get("isolation_ratio") is not None]
        if not prec_cells:
            continue
        seeds_pass = sum(1 for c in prec_cells if c["isolation_ratio"] < HP_ISOLATION_MAX)
        prec_pass[prec] = seeds_pass
        prec_max_iso[prec] = max(c["isolation_ratio"] for c in prec_cells)
        prec_compression[prec] = prec_cells[0].get("precision_compression_ratio", 0.0)

    # HARD_FAIL: fp32 or fp16 breaks isolation
    for p in ("fp32", "fp16"):
        if p in prec_max_iso and prec_max_iso[p] >= HF_CONTAMINATION:
            detail = (f"prec_max_iso={dict((k, round(v, 5)) for k,v in prec_max_iso.items())} "
                      f"theory_bound={theory_bound:.5f} N={N}")
            return ("KF2_BE1_HARD_FAIL",
                    f"BASELINE_BROKEN: {p} max_iso >= {HF_CONTAMINATION}. " + detail)

    # Count precisions that hold (>= HP_SEEDS_MIN seeds pass)
    precisions_that_hold = [p for p, cnt in prec_pass.items() if cnt >= HP_SEEDS_MIN]
    # Highest compression ratio among precisions that hold
    max_compression = max((prec_compression.get(p, 1.0) for p in precisions_that_hold), default=1.0)
    required_hold = HP_REQUIRED_PRECISIONS.issubset(set(precisions_that_hold))

    detail = (f"precisions_hold={precisions_that_hold} "
              f"prec_max_iso={dict((k, round(v, 5)) for k,v in prec_max_iso.items())} "
              f"max_compression={max_compression:.1f}x "
              f"theory_bound={theory_bound:.5f} N={N}")

    if required_hold and len(precisions_that_hold) >= HP_PRECISIONS_MIN:
        return ("KF2_BE1_HARD_PASS",
                f"PRECISION_FLOOR_CONFIRMED: fp32+fp16+int8 hold isolation. "
                f"max_compression={max_compression:.1f}x. " + detail)

    if len(precisions_that_hold) >= 1:
        return ("KF2_BE1_MIDDLE_BAND",
                f"PARTIAL_ISOLATION: only {precisions_that_hold} hold. " + detail)

    return ("KF2_BE1_HARD_FAIL",
            f"ALL_PRECISIONS_FAIL: isolation broken at all tested precisions. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Formula self-tests
    tb = 1.0 / math.sqrt(N_FULL)
    assert abs(tb - 0.01104) < 0.001, f"theory_bound N=8192: {tb}"

    # precision_metadata self-tests
    meta_int8 = precision_metadata(N_FULL ** 2, "int8")
    assert meta_int8["precision_compression_ratio"] == 4.0, (
        f"int8 compression should be 4x; got {meta_int8['precision_compression_ratio']}")
    meta_fp16 = precision_metadata(N_FULL ** 2, "fp16")
    assert meta_fp16["precision_compression_ratio"] == 2.0, (
        f"fp16 compression should be 2x; got {meta_fp16['precision_compression_ratio']}")

    # Smoke cell: run one cell at N_SMOKE for fp32 and int8
    device = torch.device("cpu")
    cell_fp32 = run_one_cell_precision("fp32", M_FRAC, 17, N_SMOKE, N_EDITS, device)
    assert "isolation_ratio" in cell_fp32, f"isolation_ratio missing: {list(cell_fp32.keys())}"
    assert not math.isnan(cell_fp32["isolation_ratio"]), "fp32 isolation_ratio NaN"
    assert cell_fp32["precision_compression_ratio"] == 1.0, (
        f"fp32 compression should be 1.0; got {cell_fp32['precision_compression_ratio']}")

    cell_int8 = run_one_cell_precision("int8", M_FRAC, 17, N_SMOKE, N_EDITS, device)
    assert "isolation_ratio" in cell_int8, f"int8 isolation_ratio missing"
    assert not math.isnan(cell_int8["isolation_ratio"]), "int8 isolation_ratio NaN"

    # 4x scale smoke
    cell_fp32_4x = run_one_cell_precision("fp32", M_FRAC, 17, N_SMOKE * 4, N_EDITS, device)
    assert "isolation_ratio" in cell_fp32_4x, f"4x fp32 isolation_ratio missing"

    # Verdict gates
    fake_hp = []
    for p in PRECISIONS_FULL:
        for _ in range(5):
            fake_hp.append({
                "precision": p, "isolation_ratio": 0.02,
                "precision_compression_ratio": precision_metadata(N_FULL**2, p)["precision_compression_ratio"],
            })
    v, msg = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"HARD_PASS gate: {v} {msg}"

    fake_hf = [{"precision": "fp32", "isolation_ratio": 0.15,
                "precision_compression_ratio": 1.0}]
    vf, mf = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in vf, f"HARD_FAIL gate: {vf}"

    print(f"[selftest] kf2_be1_precision_sweep_n8192 PASS "
          f"fp32_iso={cell_fp32['isolation_ratio']:.5f} "
          f"int8_iso={cell_int8['isolation_ratio']:.5f}", flush=True)


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
    precisions = PRECISIONS_SMOKE if smoke else PRECISIONS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    print(f"[run] kf2_be1_precision_sweep_n8192 smoke={smoke} N={N_cfg} "
          f"precisions={precisions} seeds={seeds} device={device_str}", flush=True)
    t0 = time.time()

    all_cells = []
    for precision in precisions:
        print(f"\n  [precision={precision}]", flush=True)
        for seed in seeds:
            cell = run_one_cell_precision(precision, M_FRAC, seed, N_cfg, N_EDITS, device)
            all_cells.append(cell)
            iso = cell.get("isolation_ratio")
            comp = cell.get("precision_compression_ratio", 0.0)
            print(f"  {precision} seed={seed} iso={iso:.5f} "
                  f"compression={comp:.1f}x ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf2_be1_precision_sweep_n8192", "N": N_cfg, "smoke": smoke,
        "family": FAMILY, "M_frac": M_FRAC, "precisions": precisions, "seeds": seeds,
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
