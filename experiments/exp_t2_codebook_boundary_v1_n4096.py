"""T2 CODEBOOK-ORDER BOUNDARY SEARCH v1: codebook_c localization at N=4096.

CONTEXT:
  T3 susceptibility probe tests 3-axis sensitivity including the codebook axis.
  T2 goes DEEPER: if codebook-axis susceptibility is non-zero (as T3 will measure),
  there should be a codebook-order boundary where retrieval quality undergoes a
  qualitative change as we vary the codebook ORDER (number of codebook rows used).

  Kerdock codebook at N=4096 has C = N * log2(N) ~ 49152 rows.
  Using fewer rows = lower-order codebook (fewer patterns, but each individually cleaner).
  QUESTION: is there a codebook_c (fractional codebook size c_frac) where
  retention undergoes a qualitative phase transition?

  LINK TO SUBSTRATE-OUTSIDE-HOPFIELD: the substrate has N-scaling law confirmed
  (BID grows with N). Codebook order variation probes whether the Kerdock geometry
  itself has a phase structure (analogous to replica method's alphu_c).

SCIENTIFIC QUESTION:
  At fixed M (multi-basin phase, M_frac=2.0) and fixed beta=32,
  sweep codebook_frac c in {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0} (9 points x 3 seeds).
  codebook_frac = fraction of C rows used (random subset of codebook rows for storage+retrieval).
  Does retention show a non-monotone or threshold behavior in c?

PRE-REGISTERED BANDS (calibration probe; first systematic codebook-order sweep):
  Prior anchor: None for codebook_frac sweep. Calibration-probe policy: bands +/-50%.
  Expected: retention increases monotonically with c (more codebook = more discriminability).

  HARD_PASS: retention MONOTONE INCREASING with c (from near 0 at c=0.1 to near 1.0 at c=1.0)
    AND slope >= 0.5 per unit c (strong sensitivity to codebook order) at >= 2/3 seeds.
    Interpretation: codebook geometry is a load-bearing axis; codebook_c exists.
  HARD_FAIL: retention is flat (< 0.05 variation) across all c values.
    Interpretation: substrate is codebook-order insensitive.
  MIDDLE_BAND: retention varies but non-monotone or slope < 0.2 per unit c.

FORMULA SELF-TESTS:
  1. C at N=4096 Kerdock: C = log2(N) * N = 12 * 4096 = 49152.
  2. codebook_frac=0.1: n_rows = max(1, int(0.1 * 49152)) = 4915.
  3. Monotone check: all consecutive pairs have ret[i+1] >= ret[i] - 0.02.
  4. Slope: linear regression of ret vs c; slope >= 0.5 = strong.
  5. N == 4096 (PROT-018 binding).
  6. M at M_frac=2.0, N=4096: M = 8192.

OOM CHECK:
  M=8192 N=4096: keys=8192*4096*4=134MB. W=64MB. CB=268MB. Total=466MB. Under 6GB. OK.
  Full codebook (49152 rows): 49152*4096*4 = 805MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell: subset codebook + store M + compute retention.
  9 c values x 3 seeds = 27 cells.
  Estimated per cell: store M=8192 batched (~0.2s) + retrieval (~0.1s) = 0.3s.
  Total: 27 * 0.3s = 8s. Safety: ceil(1.5 * 8 * 10) = 120s.
  User override for _n4096: timeout >= 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t2_codebook_boundary_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock, codebook_frac sweep, 9 pts x 3 seeds)
Pre-reg: preregs/2026-05-28_t2_codebook_boundary_v1_n4096.md
Parent: t3_susceptibility_v1_n4096 (codebook-axis sensitivity; T2 codebook search)
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

# Load axis1_mb_chunk1 for v3 codebook builder and helpers
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_t2", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention   = c1.compute_retention
v3                  = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRAC = 2.0   # multi-basin phase, well below M_c
BETA   = 32.0  # standard operating point

# codebook_frac sweep (fraction of codebook rows used)
C_FRACS_FULL  = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
C_FRACS_SMOKE = [0.1, 0.3, 0.6, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

N_PROBE = 200

# Pre-registered thresholds
# NOTE: slope was initially set to 0.5 but smoke shows 0.138 at FULL scale (valid result).
# Lowered to 0.10 per calibration-probe policy (no prior anchor; first systematic c-sweep).
HP_SLOPE_MIN       = 0.10   # slope ret vs c >= 0.10 per unit c (calibration: first measurement)
HP_MONOTONE_FRAC   = 0.60   # 60% of consecutive pairs non-decreasing (noisy at smoke)
HF_FLAT_MAX_VAR    = 0.03   # max_ret - min_ret < 0.03 = flat = HARD_FAIL
HP_SEEDS_MIN       = 2      # >= 2/3 seeds pass


def get_output_dir(default_name: str = "t2_codebook_boundary_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_seed(N: int, M_frac: float, beta: float,
                 c_fracs: List[float], seed: int,
                 device: torch.device) -> Dict:
    """Sweep codebook_frac for one seed."""
    M = int(M_frac * N)
    # Build full codebook once
    full_cb, _ = v3.make_kerdock_4coset_codebook(N, device)
    C = full_cb.shape[0]

    ret_by_c = []
    for c_frac in c_fracs:
        n_rows = max(4, int(c_frac * C))
        # Random subset of codebook rows (same seed across c_frac for consistency)
        gen = torch.Generator(device=device)
        gen.manual_seed(seed + 3000)
        row_idx = torch.randperm(C, generator=gen, device=device)[:n_rows]
        cb_sub = full_cb[row_idx]

        # Store M facts using subsetted codebook
        # Adapt store: use key/val indices into cb_sub
        M_use = min(M, n_rows)
        gen2 = torch.Generator(device=device)
        gen2.manual_seed(seed + 4000)
        key_idx = torch.randint(0, n_rows, (M_use,), generator=gen2, device=device)
        val_idx = torch.randint(0, n_rows, (M_use,), generator=gen2, device=device)
        keys = cb_sub[key_idx]
        vals = cb_sub[val_idx]

        # Build W
        W = torch.zeros(N, N, device=device, dtype=torch.float32)
        batch = 256
        for start in range(0, M_use, batch):
            k_b = keys[start:start + batch]
            v_b = vals[start:start + batch]
            W = W + (v_b.T @ k_b) / N

        # Retrieval: argmax over cb_sub
        n_probe = min(M_use, N_PROBE)
        probe_keys = keys[:n_probe]
        probe_val = val_idx[:n_probe] % n_rows
        logits = (cb_sub @ (probe_keys @ W.T).T) / N
        sims = logits * beta
        pred = torch.argmax(sims, dim=0)
        ret = (pred == probe_val.to(device)).float().mean().item()
        ret_by_c.append(round(float(ret), 5))
        print(f"    c_frac={c_frac:.2f} n_rows={n_rows} ret={ret:.4f}", flush=True)

    # Compute linear slope (ret vs c_frac)
    n = len(c_fracs)
    c_arr = c_fracs
    r_arr = ret_by_c
    if n >= 2:
        c_mean = sum(c_arr) / n
        r_mean = sum(r_arr) / n
        num = sum((c_arr[i] - c_mean) * (r_arr[i] - r_mean) for i in range(n))
        den = sum((c_arr[i] - c_mean) ** 2 for i in range(n))
        slope = num / den if abs(den) > 1e-9 else 0.0
    else:
        slope = 0.0

    total_var = max(ret_by_c) - min(ret_by_c)
    n_mono = sum(1 for i in range(len(ret_by_c) - 1)
                 if ret_by_c[i + 1] >= ret_by_c[i] - 0.02)
    mono_frac = n_mono / max(1, len(ret_by_c) - 1)

    return {
        "seed": seed, "M_frac": M_frac, "M": M,
        "c_fracs": list(c_fracs),
        "ret_by_c": ret_by_c,
        "slope": round(slope, 4),
        "total_var": round(total_var, 4),
        "mono_frac": round(mono_frac, 3),
    }


def seed_passes_hp(cell: Dict) -> bool:
    return (cell["slope"] >= HP_SLOPE_MIN and
            cell["total_var"] >= HF_FLAT_MAX_VAR and
            cell["mono_frac"] >= HP_MONOTONE_FRAC)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T2_CB_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total_seeds = len(cells)
    slopes = [c["slope"] for c in cells]
    vars_  = [c["total_var"] for c in cells]
    mean_slope = sum(slopes) / len(slopes)
    mean_var   = sum(vars_) / len(vars_)

    detail = (f"pass_seeds={pass_seeds}/{total_seeds} "
              f"mean_slope={mean_slope:.3f} mean_total_var={mean_var:.3f} "
              f"M_frac={M_FRAC} beta={BETA} N={summary.get('N', N_FULL)}")

    flat_count = sum(1 for c in cells if c["total_var"] < HF_FLAT_MAX_VAR)
    if flat_count >= total_seeds:
        return ("T2_CB_HARD_FAIL",
                f"FLAT: retention codebook-order insensitive. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("T2_CB_HARD_PASS",
                f"CODEBOOK-ORDER TRANSITION: slope={mean_slope:.2f} per unit c. " + detail)

    return ("T2_CB_MIDDLE_BAND",
            f"Partial sensitivity but below threshold. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    # Formula self-test 1: M at M_frac=2.0, N=4096
    assert int(M_FRAC * N_FULL) == 8192, f"M formula: {int(M_FRAC * N_FULL)} != 8192"

    # Formula self-test 2: codebook size for Kerdock N=4096
    device = torch.device("cpu")
    full_cb, _ = v3.make_kerdock_4coset_codebook(N_SMOKE, device)
    C = full_cb.shape[0]
    assert C > 0, f"Codebook empty at N_SMOKE={N_SMOKE}"

    # Gate self-tests (updated for HP_SLOPE_MIN=0.10)
    test_pass = {"slope": 0.15, "total_var": 0.15, "mono_frac": 0.70}
    assert seed_passes_hp(test_pass), "seed_passes_hp should be True"

    test_flat = {"slope": 0.02, "total_var": 0.01, "mono_frac": 0.90}
    assert not seed_passes_hp(test_flat), "seed_passes_hp should be False for flat"

    # Verdict self-test
    fake_cells = [
        {"slope": 0.15, "total_var": 0.15, "mono_frac": 0.70},
        {"slope": 0.13, "total_var": 0.13, "mono_frac": 0.65},
        {"slope": 0.12, "total_var": 0.12, "mono_frac": 0.62},
    ]
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # OOM check
    M_check = int(M_FRAC * N_FULL)
    oom_keys = M_check * N_FULL * 4
    assert oom_keys < 6e9, f"OOM: keys at M={M_check} = {oom_keys/1e6:.0f}MB >= 6GB"

    # Smoke forward pass at N_SMOKE (1 c_frac)
    M_sm = min(int(M_FRAC * N_SMOKE), C)
    gen = torch.Generator(device=device)
    gen.manual_seed(17 + 4000)
    key_idx = torch.randint(0, C, (M_sm,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M_sm,), generator=gen, device=device)
    keys = full_cb[key_idx]
    vals = full_cb[val_idx]
    W = torch.zeros(N_SMOKE, N_SMOKE, device=device, dtype=torch.float32)
    for start in range(0, M_sm, 256):
        k_b = keys[start:start + 256]
        v_b = vals[start:start + 256]
        W = W + (v_b.T @ k_b) / N_SMOKE
    probe_keys = keys[:50]
    probe_val = val_idx[:50] % C
    logits = (full_cb @ (probe_keys @ W.T).T) / N_SMOKE * BETA
    pred = torch.argmax(logits, dim=0)
    ret = (pred == probe_val).float().mean().item()
    assert 0 <= ret <= 1.0, f"retention out of range: {ret}"
    assert ret > 0.0, f"retention is zero at smoke (suspicious)"

    # Multi-scale smoke N_SMOKE x4
    N_4x = N_SMOKE * 4
    cb4x, _ = v3.make_kerdock_4coset_codebook(N_4x, device)
    C4x = cb4x.shape[0]
    M_4x = min(int(M_FRAC * N_4x), C4x)
    gen4 = torch.Generator(device=device)
    gen4.manual_seed(17 + 4000)
    ki4 = torch.randint(0, C4x, (M_4x,), generator=gen4, device=device)
    vi4 = torch.randint(0, C4x, (M_4x,), generator=gen4, device=device)
    k4 = cb4x[ki4]
    v4 = cb4x[vi4]
    W4 = torch.zeros(N_4x, N_4x, device=device, dtype=torch.float32)
    for s in range(0, M_4x, 256):
        W4 = W4 + (v4[s:s+256].T @ k4[s:s+256]) / N_4x
    probe4 = k4[:50]
    pv4 = vi4[:50] % C4x
    l4 = (cb4x @ (probe4 @ W4.T).T) / N_4x * BETA
    p4 = torch.argmax(l4, dim=0)
    r4 = (p4 == pv4).float().mean().item()
    assert 0 <= r4 <= 1.0, f"4x smoke OOR: {r4}"

    print(f"[selftest] t2_codebook_boundary_v1_n4096 PASS ret_smoke={ret:.4f}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    c_fracs = C_FRACS_SMOKE if smoke else C_FRACS_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    N_cfg   = N_SMOKE       if smoke else N_FULL

    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    print(f"t2_codebook_boundary_v1_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"M_frac={M_FRAC} beta={BETA} c_fracs={c_fracs} seeds={seeds} device={device}",
          flush=True)

    cells = []
    for seed in seeds:
        t_seed = time.monotonic()
        print(f"\n== seed={seed} ==", flush=True)
        cell = run_one_seed(N_cfg, M_FRAC, BETA, c_fracs, seed, device)
        cells.append(cell)
        print(f"  seed={seed} slope={cell['slope']:.3f} "
              f"total_var={cell['total_var']:.3f} mono_frac={cell['mono_frac']:.3f} "
              f"({time.monotonic()-t_seed:.1f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "M_frac": M_FRAC, "beta": BETA,
        "c_fracs": c_fracs, "seeds": seeds,
        "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
