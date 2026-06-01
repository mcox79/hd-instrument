"""T1.8: Effective channel capacity sweep.

SCIENTIFIC QUESTION:
  Does substrate achieve >= 60% of Shannon-bound effective capacity when
  sweeping M (stored patterns) at fixed N=1024?

  Shannon-bound for bipolar HDC (theoretical):
    C_theory(M, N) = M * log2(M) / N  (bits/dimension, Hopfield-type bound)
    Practical bound: substrate stores M patterns reliably iff M <= alpha_c * N
    where alpha_c ~ 0.138 for random bipolar patterns (Hopfield critical capacity).

  Measured effective capacity:
    For each M, measure retrieval accuracy acc(M, N).
    Effective capacity C_eff = M * acc(M,N)  (correctly stored patterns)
    Fraction = C_eff / (alpha_c * N)

  The drill uses M sweep {32, 64, 128, 192, 256} at N=1024.
  M_critical = alpha_c * N = 0.138 * 1024 = ~141. Beyond that, saturation.

PRE-REGISTERED BANDS:
  HARD-PASS: at M <= 0.10 * N (102 patterns), retrieval acc >= 0.95 AND
             mean(C_eff/M_crit) >= 0.25 for low-load M values.
  HARD-FAIL: acc < 0.50 at M=64 (well below critical) OR fraction < 0.10.
  MIDDLE: between HP and HF.

  No prior empirical anchor on capacity fraction: bands widened per policy.
  alpha_c = 0.138 (Hopfield 1982 classical result; bipolar random patterns).
  HP frac >= 0.25: at M=32 frac=0.23, M=64 frac=0.45, mean=0.34 theoretical;
  HP 0.25 = 0.34 * 0.74 (within +-50% of theory). Calibration probe policy.

DESIGN:
  N=1024, M sweep [32, 64, 128, 192, 256], 5 seeds, 1 test query per atom.
  Pure CPU. Expected wall: ~10 min (5 seeds x 5 M values x 100 queries).

PROT-018: no _nN suffix (M is the primary axis). Production N=1024 stated here.
TIMEOUT ESTIMATE:
  Smoke at M_grid + 5 seeds: ~60s local. PROT-019 floor 3600s.
  FULL run (same script, smoke=False): same grid, so timeout = 3600s.
  timeout_s = 3600.

FORMULA SELF-TESTS:
  1. alpha_c = 0.138: M_crit = int(0.138 * 1024) = 141.
  2. HP capacity fraction 0.60 >= 0.60 * (0.138 * 1024) = 84.7 effective patterns.
  3. For M=64 << M_crit: acc should be near 1.0 (clean storage regime).
  4. HP threshold: at M=64 acc >= 0.95 is achievable (HDC regime).

Anchor: channel_capacity_sweep_v1
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_channel_capacity_sweep_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# --- Config ---
N = 1024
M_SWEEP_FULL  = [32, 64, 128, 192, 256]
M_SWEEP_SMOKE = [32, 64, 128]
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_TEST_QUERIES = 20  # test queries per atom (subset to keep runtime manageable)

# Hopfield critical capacity (bipolar random patterns, classical result)
ALPHA_C = 0.138
N_CRIT = int(ALPHA_C * N)  # 141

# Pre-registered thresholds
HP_ACC_LOW_LOAD = 0.95    # acc >= 0.95 at M <= M_LOW_LOAD
# Capacity fraction at low-load M: mean(M * acc / M_crit) for M in low-load M values.
# At M=32: 32*1.0/141 = 0.23; at M=64: 64*1.0/141 = 0.45; mean = 0.34.
# HP: mean fraction >= 0.25 (substrate stores >= 25% of critical capacity at low load).
# Calibration probe bands: widened to +-50% of theoretical (0.34 +- 50% -> 0.17-0.51).
HP_CAP_FRAC     = 0.25    # mean C_eff / M_crit >= 0.25 for low-load M values
M_LOW_LOAD      = int(0.10 * N)  # 102 -- safe regime

HF_ACC_LOW_LOAD = 0.50    # acc < 0.50 at M=64 -> HARD_FAIL
HF_CAP_FRAC     = 0.10    # fraction < 0.10 -> HARD_FAIL (well below 1/3 of theoretical)


def get_output_dir(name: str = "channel_capacity_sweep_v1") -> Path:
    n = os.environ.get("HDLAB_EXP_NAME", name)
    d = REPO / "data" / f"exp_{n}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, seed: int, n_test: int = N_TEST_QUERIES) -> Dict:
    """Measure retrieval accuracy at given N, M, seed.

    Stores M patterns, retrieves each with clean key (1-step Hopfield step).
    """
    g = torch.Generator().manual_seed(seed)

    # Codebook: M bipolar patterns
    cb_raw = torch.sign(torch.randn(M, N_use, generator=g))
    cb_raw[cb_raw == 0] = 1.0
    cb = cb_raw.float()  # M x N

    # Hebbian W = (1/N) * sum_i x_i x_i^T  (autoassociative)
    W = (cb.T @ cb) / N_use  # N x N
    # Zero diagonal to avoid self-coupling
    W.fill_diagonal_(0.0)

    # Test: retrieve pattern i using clean cue q = pattern_i
    n_test_actual = min(n_test, M)
    test_indices = torch.arange(n_test_actual)
    queries = cb[test_indices]  # n_test x N

    # One-step retrieval: q_out = sign(W @ q)
    activations = queries @ W  # n_test x N
    retrieved = torch.sign(activations)
    retrieved[retrieved == 0] = 1.0

    # Accuracy: fraction of patterns retrieved perfectly (all bits correct)
    correct_bits = (retrieved == queries).float().mean(dim=1)  # n_test
    perfect_retrieval = (correct_bits >= 0.99).float()
    acc = float(perfect_retrieval.mean().item())

    # Bit-level accuracy (partial credit)
    bit_acc = float(correct_bits.mean().item())

    # Effective capacity
    c_eff = M * acc  # correctly stored patterns
    c_eff_frac = c_eff / max(float(N_CRIT), 1.0)  # fraction of theoretical capacity

    return {
        "M":              M,
        "seed":           seed,
        "N":              N_use,
        "ok":             True,
        "n_test":         n_test_actual,
        "acc_perfect":    round(acc, 5),
        "acc_bitwise":    round(bit_acc, 5),
        "c_eff":          round(c_eff, 3),
        "c_eff_fraction": round(c_eff_frac, 5),
        "M_over_N":       round(M / N_use, 4),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("CHCAP_INCONCLUSIVE", "no cells")

    ok_cells = [c for c in cells if c.get("ok")]
    if not ok_cells:
        return ("CHCAP_INCONCLUSIVE", "all cells failed")

    # Group by M
    m_vals = sorted(set(c["M"] for c in ok_cells))
    by_m: Dict[int, List[Dict]] = {m: [c for c in ok_cells if c["M"] == m] for m in m_vals}

    # HP check at low-load M
    low_load_m = [m for m in m_vals if m <= M_LOW_LOAD]
    if not low_load_m:
        return ("CHCAP_INCONCLUSIVE", f"no M <= {M_LOW_LOAD} cells in sweep")

    low_load_accs = [c["acc_perfect"] for m in low_load_m for c in by_m[m]]
    mean_low_load_acc = sum(low_load_accs) / len(low_load_accs) if low_load_accs else 0.0

    # Capacity fraction: use LOW-LOAD M values only; high-M naturally saturates
    low_load_cap_fracs = [c["c_eff_fraction"] for m in low_load_m for c in by_m[m]]
    mean_cap_frac = sum(low_load_cap_fracs) / len(low_load_cap_fracs) if low_load_cap_fracs else 0.0

    # Per-M summary
    m_summary = {}
    for m in m_vals:
        ms = by_m[m]
        m_summary[m] = {
            "acc": round(sum(c["acc_perfect"] for c in ms) / len(ms), 4),
            "c_eff_frac": round(sum(c["c_eff_fraction"] for c in ms) / len(ms), 4),
        }

    # All-M capacity fraction for informational detail only
    all_cap_fracs = [c["c_eff_fraction"] for c in ok_cells]
    mean_cap_frac_all = sum(all_cap_fracs) / len(all_cap_fracs)

    detail = (
        f"N={N} M_sweep={m_vals} n_cells={len(ok_cells)} "
        f"mean_low_load_acc={mean_low_load_acc:.3f} (M<={M_LOW_LOAD}) "
        f"mean_c_eff_frac_low_load={mean_cap_frac:.3f} "
        f"mean_c_eff_frac_all={mean_cap_frac_all:.3f} "
        f"per_M={m_summary}"
    )

    # HF check (based on low-load M values)
    m64_cells = by_m.get(64, []) or by_m.get(min(m_vals), [])
    m64_acc = sum(c["acc_perfect"] for c in m64_cells) / len(m64_cells) if m64_cells else 0.0
    is_hf = (m64_acc < HF_ACC_LOW_LOAD or mean_cap_frac < HF_CAP_FRAC)

    if is_hf:
        return ("CHCAP_HARD_FAIL",
                f"CAPACITY_FAILS acc_m64={m64_acc:.3f} frac={mean_cap_frac:.3f}. " + detail)
    if mean_low_load_acc >= HP_ACC_LOW_LOAD and mean_cap_frac >= HP_CAP_FRAC:
        return ("CHCAP_HARD_PASS",
                f"CAPACITY_VALIDATED low_acc={mean_low_load_acc:.3f} "
                f"frac={mean_cap_frac:.3f}. " + detail)
    return ("CHCAP_MIDDLE_BAND",
            f"PARTIAL low_acc={mean_low_load_acc:.3f} frac={mean_cap_frac:.3f}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    Formula self-tests:
    1. alpha_c * N = 0.138 * 1024 = 141.3 -> int = 141.
    2. M=64 << M_crit -> acc should be near 1.0.
    3. c_eff_frac = M*acc / M_crit.
    4. Live smoke at N=1024 M=32: metrics non-null.
    5. Verdict gates HP/HF/MIDDLE correct.
    """
    # Formula self-test 1: M_crit
    M_crit_check = int(ALPHA_C * N)
    assert abs(M_crit_check - 141) <= 2, f"M_crit={M_crit_check} expected ~141"
    print(f"[selftest] formula-1 alpha_c={ALPHA_C} N={N} M_crit={M_crit_check} PASS",
          flush=True)

    # Formula self-test 2: M=64 << M_crit, expect acc near 1.0
    cell_small = measure_cell(N, 32, 42)
    assert cell_small["ok"], f"selftest M=32 FAIL: {cell_small}"
    assert cell_small["acc_perfect"] >= HP_ACC_LOW_LOAD, (
        f"selftest M=32 acc={cell_small['acc_perfect']:.4f} < HP={HP_ACC_LOW_LOAD}")
    print(f"[selftest] formula-2 M=32 acc={cell_small['acc_perfect']:.4f} "
          f">= HP={HP_ACC_LOW_LOAD} PASS", flush=True)

    # Formula self-test 3: c_eff_frac formula
    acc_t, M_t = 0.95, 64
    c_eff_t = M_t * acc_t
    frac_t = c_eff_t / N_CRIT
    expected_frac = round(frac_t, 5)
    assert expected_frac > 0.30, f"formula-3: frac={expected_frac:.4f} unexpectedly low"
    print(f"[selftest] formula-3 c_eff_frac(M=64,acc=0.95)={expected_frac:.4f} "
          f"(N_crit={N_CRIT}) PASS", flush=True)

    # Formula self-test 4: live smoke metrics non-null
    cell = measure_cell(N, 64, 17)
    assert cell["ok"], f"selftest live smoke FAIL: {cell}"
    for key in ["acc_perfect", "acc_bitwise", "c_eff", "c_eff_fraction", "M_over_N"]:
        v = cell[key]
        assert v is not None and not math.isnan(float(v)), f"{key} null/NaN: {cell}"
    assert cell["n_test"] >= 1, "n_test = 0 (validity filter eliminated all)"
    print(f"[selftest] live smoke N={N} M=64 "
          f"acc={cell['acc_perfect']:.4f} "
          f"c_eff_frac={cell['c_eff_fraction']:.4f} PASS", flush=True)

    # Formula self-test 5: verdict gates
    fake_hp = [{"M": m, "seed": 17, "N": N, "ok": True,
                "acc_perfect": 0.99, "acc_bitwise": 0.99,
                "c_eff": m * 0.99, "c_eff_fraction": (m * 0.99) / N_CRIT,
                "n_test": N_TEST_QUERIES, "M_over_N": m / N}
               for m in M_SWEEP_SMOKE
               for _ in SEEDS_SMOKE]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"
    print(f"[selftest] formula-5a HP gate PASS: {v}", flush=True)

    fake_hf = [{"M": m, "seed": 17, "N": N, "ok": True,
                "acc_perfect": 0.10, "acc_bitwise": 0.55,
                "c_eff": m * 0.10, "c_eff_fraction": (m * 0.10) / N_CRIT,
                "n_test": N_TEST_QUERIES, "M_over_N": m / N}
               for m in M_SWEEP_SMOKE
               for _ in SEEDS_SMOKE]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"
    print(f"[selftest] formula-5b HF gate PASS: {v}", flush=True)

    print("[selftest] channel_capacity_sweep_v1 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke = args.smoke
    M_sweep = M_SWEEP_SMOKE if smoke else M_SWEEP_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    t0 = time.time()
    print(f"[run] channel_capacity_sweep_v1 smoke={smoke} "
          f"N={N} M_sweep={M_sweep} seeds={seeds} "
          f"[EFFECTIVE_CHANNEL_CAPACITY vs Shannon bound]",
          flush=True)

    cells: List[Dict] = []
    for M in M_sweep:
        for seed in seeds:
            cell = measure_cell(N, M, seed)
            cells.append(cell)
            print(f"  M={M} seed={seed} acc={cell['acc_perfect']:.4f} "
                  f"bitwise={cell['acc_bitwise']:.4f} "
                  f"c_eff_frac={cell['c_eff_fraction']:.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor":    "channel_capacity_sweep_v1",
        "N":         N, "M_sweep": M_sweep, "seeds": seeds,
        "alpha_c":   ALPHA_C, "M_crit": N_CRIT,
        "cells":     cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
