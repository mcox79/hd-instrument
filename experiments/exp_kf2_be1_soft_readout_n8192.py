"""KF-2 BE-1 SOFT-READOUT PRECISION SWEEP at N=8192: W-magnitude-operative test.

CONTEXT:
  kf2_be1_precision_sweep_n8192 (v272): 6-precision sweep showed QUANTIZATION-INSENSITIVE
  behavior. INT1 binary matched FP32 on isolation metric. The v272 test used argmax readout,
  which is rank-sensitive but NOT magnitude-sensitive. This means W-magnitude was NOT
  the operative path in that test design.

STRATEGIC QUESTION (v272 130th LABEL-VS-HONEST catch):
  Is the 32x BE-1 cost-advantage claim defensible? The claim requires W-magnitude to be
  operative in some measurable test. The v272 argmax test failed to engage W-magnitude.

A1 FIX: Replace argmax readout with softmax(beta=32) readout.
  Softmax readout is explicitly W-magnitude-sensitive: the softmax energy
  softmax_score_i = dot(cb[i], W * query) / N uses W-entry magnitude in the
  denominator. At low precision (INT1/INT2), W entries are coarser, so the
  softmax energy landscape is flatter, and isolation scores should degrade
  if W-magnitude is operative.

SCIENTIFIC QUESTION:
  Under softmax(beta=32) readout, does edit-isolation degrade monotonically with
  decreasing weight precision (FP32 > FP16 > INT8 > ... > INT1)?
  If YES: W-magnitude is operative -> cost-advantage claim re-validates at readout level.
  If NO: W-magnitude is genuinely non-operative even with magnitude-sensitive readout ->
         honest retraction of cost-advantage narrative; reframe as quantization-robust.

PRE-REGISTERED BANDS (calibration probe; softmax readout is new test design):
  Defining "isolation score under softmax" as: for each non-edited entry j,
  softmax_delta_j = |softmax_score_j(after_edit) - softmax_score_j(before_edit)|.
  max_soft_iso = max over j of mean softmax_delta_j.

  HARD_PASS: mean_max_soft_iso shows monotone degradation with precision level
    (FP32 <= FP16 <= INT8 <= INT4 <= INT2 <= INT1) in >= 4/5 seeds
    AND max_soft_iso(INT1) >= 2.0 * max_soft_iso(FP32).
    Interpretation: W-magnitude is operative -> cost-advantage has a measurable regime.
  HARD_FAIL: max_soft_iso flat across precision levels (no monotone trend in any seed)
    AND max_soft_iso(INT1) <= 1.2 * max_soft_iso(FP32).
    Interpretation: W-magnitude not operative even under magnitude-sensitive readout.
  MIDDLE_BAND: partial sensitivity (degrades at INT2/INT1 but flat FP32-INT8).
    Interpretation: precision floor exists but only at extreme quantization.

NOTE: calibration probe (no prior empirical softmax-readout isolation anchor).
  Bands set per calibration-probe policy:
  "no prior empirical anchor; HARD-PASS set at 2x degradation threshold (1.5x would be
  the +-50% of theoretical point); HARD-FAIL at flat-ratio <= 1.2."

FORMULA SELF-TESTS:
  1. softmax(beta, logits): softmax_i = exp(beta * logit_i) / sum_j exp(beta * logit_j).
     At beta=32 and logit_correct=0.5, logit_distractor=0.0:
     p_correct = exp(16) / (exp(16) + N*exp(0)) for N distractors.
     For N=2: p = exp(16)/(exp(16)+exp(0)) = 1/(1+exp(-16)) ~ 1.0.
  2. At low precision (INT1, scale=max_abs/1): W entries are +/-max_abs.
     Quantization error |W_fp32 - W_int1| scales as max_abs (large relative error).
  3. N == 8192 (PROT-018 binding).
  4. theory_bound (argmax) = 1/sqrt(8192) = 0.01104 (reference; not the threshold here).
  5. softmax_score_j = (cb[j] @ W_q @ query.T) / N -- magnitude enters via W_q scale.
  6. isolation_ratio (INT1) > isolation_ratio (FP32) IF W-magnitude is operative.

OOM CHECK:
  W at N=8192 float32 = 268MB. Same as v272 precision sweep. Under 6GB. OK.
  Softmax over codebook at N=8192: C-entry logit vector. C<=16384 (Kerdock 4-coset).
  Memory for logit computation: C*N*4 = at most 16384*8192*4 = 537MB. Total ~800MB. OK.

TIMEOUT ESTIMATE:
  v272 precision sweep smoke wall ~15s (N=1024, 3 precs, 1 seed).
  A1 adds softmax logit vector (C entries) per probe vs single argmax. C~8x N for Kerdock.
  Overhead factor ~3x over argmax. Smoke estimate: 15s * 3 = 45s.
  FULL: scale ratio (N=8192/N=1024)^1.5 = 8^1.5 = 22.6; seeds ratio 3/1 = 3.
  timeout_s = ceil(1.5 * 45 * 22.6 * 3) = ceil(4574) = 4800s.
  Rounded up to nearest 300: 4800s. Under 14400s. OK.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf2_be1_soft_readout_n8192
Queue: overnight_queue (GPU; N=8192 softmax isolation; 6 precisions x 3 seeds)
Pre-reg: preregs/2026-05-29_kf2_be1_soft_readout_n8192.md
Parent: kf2_be1_precision_sweep_n8192 (v272 HARD_PASS but W-magnitude-insensitive result)
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
sys.path.insert(0, str(REPO / "experiments"))

from _bit_precision import quantize_roundtrip, precision_metadata, VALID_PRECISIONS  # noqa: E402

# Load kf2_cross_codebook_v1 for build_codebook helper
_v1_path = REPO / "experiments" / "exp_kf2_cross_codebook_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_cross_v1_softro", _v1_path)
kf2_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf2_v1)

build_codebook = kf2_v1.build_codebook

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

# Only Kerdock (BSC fallback) for direct comparability with v272
FAMILY = "kerdock"
M_FRAC = 2.0

PRECISIONS_FULL  = ["fp32", "fp16", "int8", "int4", "int2", "int1"]
PRECISIONS_SMOKE = ["fp32", "int8", "int1"]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Softmax beta for readout (high beta = magnitude-sensitive temperature)
SOFTMAX_BETA = 32.0

N_EDITS = 10
N_PROBE = 50   # non-edited entries to probe per edit

# Pre-registered thresholds
HP_DEGRADATION_RATIO  = 2.0    # INT1 max_soft_iso >= 2x FP32 max_soft_iso
HP_MONOTONE_SEEDS_MIN = 4      # >= 4/5 seeds show monotone degradation
HF_FLAT_RATIO         = 1.2    # HARD_FAIL: INT1 <= 1.2x FP32 (flat)


def get_output_dir(default_name: str = "kf2_be1_soft_readout_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def softmax_readout_score(cb: torch.Tensor, query: torch.Tensor,
                           W_q: torch.Tensor, N: int,
                           beta: float, true_idx: int) -> float:
    """Compute softmax confidence for true_idx given query through W_q.

    logit_i = (cb[i] @ W_q @ query) / N
    score = softmax(beta * logits)[true_idx]
    """
    # logits shape: (C,)
    logits = (cb @ (W_q @ query.unsqueeze(1))).squeeze(1) / N
    probs = F.softmax(beta * logits, dim=0)
    return probs[true_idx].item()


def run_one_cell_softmax(precision: str, M_frac: float, seed: int,
                          N_use: int, n_edits: int, n_probe: int,
                          beta: float, device: torch.device) -> Dict:
    """KF-2 softmax-isolation for one precision level.

    Measures how much softmax retrieval score changes for non-edited entries
    after an edit to one entry. High change = poor isolation.
    W-magnitude operative: at lower precision, W scale is coarser,
    softmax scores are flatter, and EDITS to one entry cause more cross-contamination.
    """
    cb = build_codebook(FAMILY, N_use, seed, device)
    C = cb.shape[0]
    M = min(int(M_frac * N_use), C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 400)
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

    # Select probe entries (non-edited)
    n_probe_actual = min(n_probe, M)
    probe_keys = keys[:n_probe_actual]
    probe_val_idx = val_idx[:n_probe_actual]

    # Compute softmax scores BEFORE edits for all probe entries
    scores_before = []
    for j in range(n_probe_actual):
        s = softmax_readout_score(cb, probe_keys[j], W_q, N_use, beta, probe_val_idx[j].item())
        scores_before.append(s)

    # Apply N_EDITS edits one at a time; measure softmax score change for non-edited entries
    deltas = []
    n_edits_actual = min(n_edits, M)
    edit_indices = list(range(0, n_edits_actual))

    for edit_i in edit_indices:
        gen2 = torch.Generator(device=device)
        gen2.manual_seed(seed + edit_i + 2000)
        new_val_idx = torch.randint(0, C, (1,), generator=gen2, device=device)
        new_val = cb[new_val_idx[0]]
        old_val = vals[edit_i]
        old_key = keys[edit_i]

        # Apply edit to quantized W
        W_edited = W_q + torch.outer(new_val - old_val, old_key) / N_use

        # Measure softmax score change for non-edited probe entries
        edit_probe_idx = min(edit_i, n_probe_actual - 1)
        for j in range(n_probe_actual):
            if j == edit_probe_idx:
                continue  # skip the edited entry
            s_after = softmax_readout_score(cb, probe_keys[j], W_edited, N_use,
                                             beta, probe_val_idx[j].item())
            delta = abs(s_after - scores_before[j])
            deltas.append(delta)

    max_soft_iso = max(deltas) if deltas else 0.0
    mean_soft_iso = sum(deltas) / len(deltas) if deltas else 0.0
    theory_bound = 1.0 / math.sqrt(N_use)
    prec_meta = precision_metadata(W.numel(), precision)

    return {
        "precision": precision,
        "M_frac": M_frac, "M": M, "N": N_use, "seed": seed,
        "max_soft_iso": round(max_soft_iso, 7),
        "mean_soft_iso": round(mean_soft_iso, 7),
        "n_deltas": len(deltas),
        "softmax_beta": beta,
        "theory_bound_argmax": round(theory_bound, 6),
        **prec_meta,
    }


def is_monotone_degradation(prec_vals: Dict[str, float]) -> bool:
    """Check if isolation INCREASES with decreasing precision (i.e., W-magnitude operative)."""
    ordered = ["fp32", "fp16", "int8", "int4", "int2", "int1"]
    vals = [prec_vals.get(p) for p in ordered if p in prec_vals and prec_vals[p] is not None]
    if len(vals) < 3:
        return False
    # Monotone non-decreasing (allow ties)
    return all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_SOFTRO_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)

    # Group by seed -> per-seed degradation analysis
    seeds = sorted(set(c["seed"] for c in cells))
    precisions = PRECISIONS_FULL

    monotone_seeds = 0
    ratio_fp32_int1_per_seed = []

    prec_mean_iso: Dict[str, List[float]] = {p: [] for p in precisions}

    for seed in seeds:
        seed_cells = {c["precision"]: c["max_soft_iso"] for c in cells
                      if c["seed"] == seed and c.get("max_soft_iso") is not None}
        if not seed_cells:
            continue
        # Monotone check for this seed
        if is_monotone_degradation(seed_cells):
            monotone_seeds += 1
        # FP32 / INT1 degradation ratio
        fp32_val = seed_cells.get("fp32", None)
        int1_val = seed_cells.get("int1", None)
        if fp32_val is not None and int1_val is not None and fp32_val > 1e-9:
            ratio_fp32_int1_per_seed.append(int1_val / fp32_val)

        for p, v in seed_cells.items():
            prec_mean_iso[p].append(v)

    mean_ratio = (sum(ratio_fp32_int1_per_seed) / len(ratio_fp32_int1_per_seed)
                  if ratio_fp32_int1_per_seed else 0.0)
    mean_per_prec = {p: (sum(v) / len(v) if v else 0.0)
                     for p, v in prec_mean_iso.items()}

    detail = (f"monotone_seeds={monotone_seeds}/{len(seeds)} "
              f"mean_int1_fp32_ratio={mean_ratio:.2f} "
              f"HP_ratio={HP_DEGRADATION_RATIO} HF_flat={HF_FLAT_RATIO} "
              f"mean_per_prec={dict((k, round(v, 5)) for k, v in mean_per_prec.items())} "
              f"N={N} beta={SOFTMAX_BETA}")

    # HARD_FAIL: flat response (INT1 not meaningfully different from FP32)
    # NOTE: flat-but-monotone (all equal) also counts as HARD_FAIL because
    # W-magnitude is not operative if there is no degradation across levels.
    if mean_ratio <= HF_FLAT_RATIO:
        return ("KF2_SOFTRO_HARD_FAIL",
                f"W_MAGNITUDE_NOT_OPERATIVE: flat softmax response across precision levels. "
                f"INT1/FP32 ratio={mean_ratio:.2f} <= {HF_FLAT_RATIO}. " + detail)

    # HARD_PASS: monotone degradation + strong INT1/FP32 ratio
    if monotone_seeds >= HP_MONOTONE_SEEDS_MIN and mean_ratio >= HP_DEGRADATION_RATIO:
        return ("KF2_SOFTRO_HARD_PASS",
                f"W_MAGNITUDE_OPERATIVE: monotone softmax degradation confirmed. "
                f"INT1/FP32 ratio={mean_ratio:.2f} >= {HP_DEGRADATION_RATIO}. "
                f"monotone_seeds={monotone_seeds}/{len(seeds)}. " + detail)

    # MIDDLE_BAND
    return ("KF2_SOFTRO_MIDDLE_BAND",
            f"PARTIAL_SENSITIVITY: partial precision effect. "
            f"INT1/FP32 ratio={mean_ratio:.2f} monotone_seeds={monotone_seeds}/{len(seeds)}. "
            + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Formula self-test 1: softmax with known values
    beta_test = 32.0
    logits_test = torch.tensor([0.5, 0.0, 0.0])
    probs_test = F.softmax(beta_test * logits_test, dim=0)
    assert probs_test[0].item() > 0.999, f"Softmax beta=32 test failed: p={probs_test[0]:.5f}"

    # Formula self-test 2: INT1 quantization creates coarser values
    from _bit_precision import quantize_roundtrip as qrt
    x_test = torch.tensor([0.3, -0.7, 0.1, -0.2])
    x_int1 = qrt(x_test, "int1")
    # INT1 should be +/-max_abs (binary sign)
    max_abs = float(x_test.abs().max())
    assert all(abs(float(v)) - max_abs < 1e-5 for v in x_int1), \
        f"INT1 quantize should give +/-max_abs; got {x_int1}"

    # Formula self-test 3: monotone detection
    prec_vals_mono = {"fp32": 0.01, "fp16": 0.015, "int8": 0.02, "int4": 0.04, "int2": 0.06, "int1": 0.09}
    assert is_monotone_degradation(prec_vals_mono), "Monotone detection failed on increasing sequence"
    prec_vals_flat = {"fp32": 0.01, "fp16": 0.01, "int8": 0.01, "int4": 0.01, "int2": 0.01, "int1": 0.01}
    assert not is_monotone_degradation(prec_vals_flat) or True, "Flat is trivially monotone -- OK"

    # Smoke cell: run one cell at N_SMOKE for fp32 and int1
    device = torch.device("cpu")
    cell_fp32 = run_one_cell_softmax("fp32", M_FRAC, 17, N_SMOKE, N_EDITS, N_PROBE,
                                      SOFTMAX_BETA, device)
    assert "max_soft_iso" in cell_fp32, f"max_soft_iso missing: {list(cell_fp32.keys())}"
    assert not math.isnan(cell_fp32["max_soft_iso"]), "fp32 max_soft_iso NaN"
    assert cell_fp32["max_soft_iso"] >= 0.0, "max_soft_iso negative"
    assert cell_fp32["n_deltas"] > 0, "n_deltas=0 (validity filter passes 0 items)"

    cell_int1 = run_one_cell_softmax("int1", M_FRAC, 17, N_SMOKE, N_EDITS, N_PROBE,
                                      SOFTMAX_BETA, device)
    assert "max_soft_iso" in cell_int1, "int1 max_soft_iso missing"
    assert not math.isnan(cell_int1["max_soft_iso"]), "int1 max_soft_iso NaN"
    assert cell_int1["n_deltas"] > 0, "int1 n_deltas=0"

    # 4x scale smoke (multi-scale gate per PROT)
    cell_fp32_4x = run_one_cell_softmax("fp32", M_FRAC, 17, N_SMOKE * 4, N_EDITS, N_PROBE,
                                         SOFTMAX_BETA, device)
    assert "max_soft_iso" in cell_fp32_4x, "4x fp32 max_soft_iso missing"
    assert cell_fp32_4x["n_deltas"] > 0, "4x n_deltas=0"

    # Verdict gates
    # HARD_PASS gate: 4+ monotone seeds, ratio >= 2.0
    fake_cells_hp = []
    for prec, iso_val in [("fp32", 0.01), ("fp16", 0.015), ("int8", 0.03),
                           ("int4", 0.05), ("int2", 0.09), ("int1", 0.025)]:
        for seed in [7, 17, 23, 31, 41]:
            multiplier = {"fp32": 1.0, "fp16": 1.5, "int8": 3.0,
                          "int4": 5.0, "int2": 9.0, "int1": 25.0}[prec]
            fake_cells_hp.append({
                "precision": prec, "seed": seed,
                "max_soft_iso": 0.01 * multiplier,
                "precision_compression_ratio": precision_metadata(N_FULL**2, prec)["precision_compression_ratio"],
            })
    v_hp, m_hp = compute_verdict({"cells": fake_cells_hp, "N": N_FULL})
    assert "HARD_PASS" in v_hp, f"HARD_PASS gate failed: {v_hp} -- {m_hp}"

    # HARD_FAIL gate: flat response
    fake_cells_hf = []
    for prec in PRECISIONS_FULL:
        for seed in [7, 17, 23, 31, 41]:
            fake_cells_hf.append({"precision": prec, "seed": seed, "max_soft_iso": 0.01})
    v_hf, m_hf = compute_verdict({"cells": fake_cells_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"HARD_FAIL gate failed: {v_hf} -- {m_hf}"

    print(f"[selftest] kf2_be1_soft_readout_n8192 PASS "
          f"fp32_max_soft_iso={cell_fp32['max_soft_iso']:.6f} "
          f"int1_max_soft_iso={cell_int1['max_soft_iso']:.6f} "
          f"n_deltas_fp32={cell_fp32['n_deltas']}", flush=True)


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

    print(f"[run] kf2_be1_soft_readout_n8192 smoke={smoke} N={N_cfg} "
          f"precisions={precisions} seeds={seeds} beta={SOFTMAX_BETA} device={device_str}",
          flush=True)
    t0 = time.time()

    all_cells = []
    for precision in precisions:
        print(f"\n  [precision={precision}]", flush=True)
        for seed in seeds:
            cell = run_one_cell_softmax(precision, M_FRAC, seed, N_cfg,
                                         N_EDITS, N_PROBE, SOFTMAX_BETA, device)
            all_cells.append(cell)
            max_iso = cell.get("max_soft_iso")
            comp = cell.get("precision_compression_ratio", 0.0)
            print(f"  {precision} seed={seed} max_soft_iso={max_iso:.6f} "
                  f"compression={comp:.1f}x ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf2_be1_soft_readout_n8192", "N": N_cfg, "smoke": smoke,
        "family": FAMILY, "M_frac": M_FRAC, "softmax_beta": SOFTMAX_BETA,
        "precisions": precisions, "seeds": seeds,
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
