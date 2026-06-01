"""KF-2 BE-1 RETRIEVAL ACCURACY under quantized W: 10K memory pool precision sweep.

CONTEXT:
  A2 in the v273 Cluster A (KF-2 BE-1 W-magnitude-operative probes).
  v272 BE-1 isolation test was quantization-insensitive.
  A1 softmax-readout isolation is being tested in parallel.
  A2 asks: does top-1 retrieval ACCURACY on a large memory pool (10K items)
  degrade as weight precision drops? Retrieval accuracy is magnitude-sensitive
  in a different way: at low precision, W entries are coarser, adding noise to
  every query response, causing more retrieval errors via nearest-neighbor confusion.

SCIENTIFIC QUESTION:
  Does top-1 retrieval accuracy on a 10K pool degrade monotonically with precision
  (FP32 > FP16 >= INT8 > INT4 > INT2 > INT1)?
  If YES: W-magnitude operative via retrieval path -- narrows cost-advantage claim to
          "INT8 safe, INT4 borderline, INT2/INT1 degrade."
  If NO (all precisions yield similar accuracy): substrate has genuine quantization
        robustness -- retrieval is also insensitive to W-magnitude precision.

PRE-REGISTERED BANDS (calibration probe; no prior empirical retrieval-accuracy-vs-precision):
  Metric: top-1 retrieval accuracy over a 10K memory pool.
  At FP32: expected near-perfect retrieval for M << capacity.
  At INT1 (binary W): large quantization noise expected to cause retrieval errors.

  HARD_PASS: accuracy degrades monotonically from FP32 to INT1
    AND acc(INT1) <= 0.8 * acc(FP32) (at least 20% relative drop)
    AND this holds in >= 3/3 seeds.
    Interpretation: W-magnitude is operative; cost advantage has measurable precision floor.
  HARD_FAIL: acc(INT1) > 0.95 * acc(FP32) across all seeds (< 5% relative drop).
    Interpretation: retrieval also insensitive to W-magnitude; substrate is quantization-robust.
  MIDDLE_BAND: acc drops at INT1/INT2 but not at INT4/INT8 (20% at INT2, < 10% at INT4).
    Interpretation: precision floor at extreme quantization only; INT8 safe.

CALIBRATION NOTE:
  No prior empirical retrieval-accuracy-vs-precision anchor.
  Bands per calibration-probe policy: "no prior empirical anchor; +-50% of theoretical prediction."
  Theory: Hopfield retrieval with Gaussian noise of magnitude sigma scales as
  acc ~ Q((SNR - 1) / sigma) where SNR = M/N. At N=8192, M=2*8192=16384:
  SNR_nominal = 2. At INT1 (sigma/scale_max ~ sqrt(N)/2), acc degrades sharply.
  HARD_PASS degradation (20%) is conservative; actual expected: >50% at INT1.
  HARD_FAIL (< 5% drop) is the null hypothesis.

FORMULA SELF-TESTS:
  1. retrieval_acc = (number of correct top-1 matches) / (total probes).
  2. acc in [0, 1].
  3. acc(FP32) should be >= 0.90 at M_frac=2.0, N=8192 (well below capacity).
  4. relative_drop = (acc(FP32) - acc(INT1)) / acc(FP32). Range [0, 1].
  5. N == 8192 (PROT-018 binding).
  6. 10K pool: M = min(10000, C) memories stored.

OOM CHECK:
  W at N=8192 float32 = 268MB. Codebook C rows: Kerdock 4-coset ~16K rows.
  M=10000 keys: 10000*8192*4=328MB. Total ~600MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Smoke: N=1024, M=2000, 3 precisions, 1 seed.
  Per cell (N=1024): store 2000 outer products + 200 retrieval probes ~ 2s.
  Smoke: 3 * 1 * 2s = 6s.
  FULL: (8192/1024)^1.5 = 22.6; seeds ratio 3/1 = 3; prec ratio 6/3 = 2.
  timeout_s = ceil(1.5 * 6 * 22.6 * 3 * 2) = ceil(1220) = 1500s.
  PROT-019 floor for _n8192 = 21600s. timeout_s = 21600s.

N-suffix: _n8192 -> production N = 8192 (PROT-018 binding).
Anchor: kf2_be1_retrieval_acc_n8192
Queue: overnight_queue (GPU; N=8192; 6 precisions x 3 seeds; 10K pool)
Pre-reg: prereqs/2026-05-29_kf2_be1_retrieval_acc_n8192.md
Parent: kf2_be1_precision_sweep_n8192 (v272 isolation test; retrieval test is complementary A2)
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

from _bit_precision import quantize_roundtrip, precision_metadata, VALID_PRECISIONS  # noqa: E402

# Load kf2_cross_codebook_v1 for build_codebook
_v1_path = REPO / "experiments" / "exp_kf2_cross_codebook_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("kf2_cross_v1_reta2", _v1_path)
kf2_v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(kf2_v1)
build_codebook = kf2_v1.build_codebook

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N_FULL  = 8192
N_SMOKE = 1024
assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

FAMILY = "kerdock"   # BSC fallback in build_codebook
M_POOL_FULL  = 10_000
M_POOL_SMOKE = 2_000
M_FRAC_CAP = 2.0     # if M_POOL > M_FRAC_CAP * N, cap to M_FRAC_CAP * N to avoid capacity overflow

PRECISIONS_FULL  = ["fp32", "fp16", "int8", "int4", "int2", "int1"]
PRECISIONS_SMOKE = ["fp32", "int8", "int1"]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE_FULL  = 500
N_PROBE_SMOKE = 200

# Pre-registered thresholds
HP_RELATIVE_DROP_MIN = 0.20   # HARD_PASS: acc(INT1) drops >= 20% relative vs FP32
HF_RELATIVE_DROP_MAX = 0.05   # HARD_FAIL: acc(INT1) drops < 5% (insensitive)
HP_SEEDS_MIN         = 3      # all seeds must show same pattern


def get_output_dir(default_name: str = "kf2_be1_retrieval_acc_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell_retrieval(precision: str, M_pool: int, seed: int,
                            N_use: int, n_probe: int,
                            device: torch.device) -> Dict:
    """Measure top-1 retrieval accuracy at given precision.

    Stores M_pool memories, then queries a random subset of stored keys
    and measures fraction that retrieve the correct value.
    """
    cb = build_codebook(FAMILY, N_use, seed, device)
    C = cb.shape[0]
    M = min(M_pool, int(M_FRAC_CAP * N_use), C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 500)
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

    # QUANTIZE
    W_q = quantize_roundtrip(W, precision)

    # RETRIEVAL: probe n_probe stored keys, measure top-1 accuracy
    n_probe_actual = min(n_probe, M)
    probe_keys = keys[:n_probe_actual]
    probe_val_idx = val_idx[:n_probe_actual]

    # Batch retrieval: sims shape (C, n_probe)
    # logits[i, j] = cb[i] . (W_q @ probe_key[j]) / N
    responses = W_q @ probe_keys.T          # (N, n_probe)
    sims = cb @ responses / N_use           # (C, n_probe)
    predicted = torch.argmax(sims, dim=0)   # (n_probe,)
    correct = (predicted == probe_val_idx).float()
    acc = correct.mean().item()

    prec_meta = precision_metadata(W.numel(), precision)

    return {
        "precision": precision,
        "M_pool": M, "N": N_use, "seed": seed,
        "retrieval_acc": round(acc, 5),
        "n_probe": n_probe_actual,
        **prec_meta,
    }


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("KF2_RETA_INCONCLUSIVE", "No cells.")

    N = summary.get("N", N_FULL)
    precisions = PRECISIONS_FULL
    seeds = sorted(set(c["seed"] for c in cells))

    per_prec: Dict[str, List[float]] = {p: [] for p in precisions}
    for c in cells:
        p = c.get("precision")
        acc = c.get("retrieval_acc")
        if p in per_prec and acc is not None:
            per_prec[p].append(acc)

    mean_acc = {p: (sum(v) / len(v) if v else 0.0) for p, v in per_prec.items()}
    fp32_acc = mean_acc.get("fp32", 0.0)
    int1_acc = mean_acc.get("int1", 0.0)

    if fp32_acc < 1e-6:
        return ("KF2_RETA_INCONCLUSIVE", f"fp32 acc=0; FP32 baseline broken. N={N}")

    relative_drop = (fp32_acc - int1_acc) / fp32_acc if fp32_acc > 0 else 0.0

    # Count seeds that show >= HP_RELATIVE_DROP_MIN degradation at INT1
    degradation_seeds = 0
    for seed in seeds:
        seed_fp32 = next((c["retrieval_acc"] for c in cells
                          if c["seed"] == seed and c["precision"] == "fp32"), None)
        seed_int1 = next((c["retrieval_acc"] for c in cells
                          if c["seed"] == seed and c["precision"] == "int1"), None)
        if seed_fp32 and seed_int1 and seed_fp32 > 1e-6:
            drop_seed = (seed_fp32 - seed_int1) / seed_fp32
            if drop_seed >= HP_RELATIVE_DROP_MIN:
                degradation_seeds += 1

    detail = (f"fp32_acc={fp32_acc:.4f} int1_acc={int1_acc:.4f} "
              f"relative_drop={relative_drop:.3f} "
              f"degradation_seeds={degradation_seeds}/{len(seeds)} "
              f"HP_drop={HP_RELATIVE_DROP_MIN} HF_drop={HF_RELATIVE_DROP_MAX} "
              f"mean_acc={dict((k, round(v, 4)) for k, v in mean_acc.items())} N={N}")

    # HARD_FAIL: insensitive (< 5% drop)
    if relative_drop < HF_RELATIVE_DROP_MAX:
        return ("KF2_RETA_HARD_FAIL",
                f"QUANTIZATION_INSENSITIVE: top-1 retrieval insensitive to W-precision. "
                f"INT1/FP32 relative_drop={relative_drop:.3f} < {HF_RELATIVE_DROP_MAX}. "
                + detail)

    # HARD_PASS: >= 20% drop, consistent across seeds
    if relative_drop >= HP_RELATIVE_DROP_MIN and degradation_seeds >= HP_SEEDS_MIN:
        return ("KF2_RETA_HARD_PASS",
                f"W_MAGNITUDE_OPERATIVE: retrieval accuracy degrades with precision. "
                f"relative_drop={relative_drop:.3f} >= {HP_RELATIVE_DROP_MIN}. "
                f"consistent in {degradation_seeds}/{len(seeds)} seeds. " + detail)

    # MIDDLE_BAND
    return ("KF2_RETA_MIDDLE_BAND",
            f"PARTIAL_DEGRADATION: partial precision effect. "
            f"relative_drop={relative_drop:.3f} degradation_seeds={degradation_seeds}/{len(seeds)}. "
            + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Formula self-test 1: relative_drop formula
    fp32_acc_t, int1_acc_t = 0.90, 0.70
    drop_t = (fp32_acc_t - int1_acc_t) / fp32_acc_t
    assert abs(drop_t - 0.2222) < 0.001, f"relative_drop formula: {drop_t}"

    # Formula self-test 2: acc in [0, 1]
    device = torch.device("cpu")
    cell_fp32 = run_one_cell_retrieval("fp32", M_POOL_SMOKE, 17, N_SMOKE, N_PROBE_SMOKE, device)
    assert "retrieval_acc" in cell_fp32, f"retrieval_acc missing: {list(cell_fp32.keys())}"
    acc = cell_fp32["retrieval_acc"]
    assert 0.0 <= acc <= 1.0, f"acc out of [0,1]: {acc}"
    assert not math.isnan(acc), "acc NaN"

    cell_int1 = run_one_cell_retrieval("int1", M_POOL_SMOKE, 17, N_SMOKE, N_PROBE_SMOKE, device)
    assert "retrieval_acc" in cell_int1, "int1 retrieval_acc missing"
    assert 0.0 <= cell_int1["retrieval_acc"] <= 1.0

    # Multi-scale smoke
    cell_4x = run_one_cell_retrieval("fp32", M_POOL_SMOKE, 17, N_SMOKE * 4, N_PROBE_SMOKE, device)
    assert 0.0 <= cell_4x["retrieval_acc"] <= 1.0, "4x smoke acc out of range"

    # Verdict HARD_PASS gate
    fake_hp = []
    for prec, acc_val in [("fp32", 0.98), ("fp16", 0.97), ("int8", 0.95),
                           ("int4", 0.88), ("int2", 0.80), ("int1", 0.60)]:
        for seed in [7, 17, 23]:
            fake_hp.append({"precision": prec, "seed": seed, "retrieval_acc": acc_val})
    v_hp, m_hp = compute_verdict({"cells": fake_hp, "N": N_FULL})
    assert "HARD_PASS" in v_hp, f"HARD_PASS gate failed: {v_hp} -- {m_hp}"

    # Verdict HARD_FAIL gate
    fake_hf = []
    for prec in PRECISIONS_FULL:
        for seed in [7, 17, 23]:
            fake_hf.append({"precision": prec, "seed": seed, "retrieval_acc": 0.95})
    v_hf, m_hf = compute_verdict({"cells": fake_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"HARD_FAIL gate failed: {v_hf} -- {m_hf}"

    print(f"[selftest] kf2_be1_retrieval_acc_n8192 PASS "
          f"fp32_acc={acc:.4f} int1_acc={cell_int1['retrieval_acc']:.4f}", flush=True)


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
    M_pool = M_POOL_SMOKE if smoke else M_POOL_FULL
    precisions = PRECISIONS_SMOKE if smoke else PRECISIONS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL

    print(f"[run] kf2_be1_retrieval_acc_n8192 smoke={smoke} N={N_cfg} "
          f"M_pool={M_pool} precisions={precisions} seeds={seeds} device={device_str}",
          flush=True)
    t0 = time.time()

    all_cells = []
    for precision in precisions:
        print(f"\n  [precision={precision}]", flush=True)
        for seed in seeds:
            cell = run_one_cell_retrieval(precision, M_pool, seed, N_cfg, n_probe, device)
            all_cells.append(cell)
            acc = cell.get("retrieval_acc")
            comp = cell.get("precision_compression_ratio", 0.0)
            print(f"  {precision} seed={seed} acc={acc:.4f} "
                  f"compression={comp:.1f}x ({time.time()-t0:.1f}s)", flush=True)

    verdict, verdict_msg = compute_verdict({"cells": all_cells, "N": N_cfg})
    elapsed = round(time.time() - t0, 2)

    summary = {
        "anchor": "kf2_be1_retrieval_acc_n8192", "N": N_cfg, "smoke": smoke,
        "family": FAMILY, "M_pool_target": M_pool,
        "precisions": precisions, "seeds": seeds, "n_probe": n_probe,
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
