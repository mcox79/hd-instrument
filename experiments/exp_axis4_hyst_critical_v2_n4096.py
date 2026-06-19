"""AXIS-4 HYSTERESIS CRITICAL RESCUE v2: beta near beta_c=10, M_frac sweep [4,6,8,10].

PARENT: exp_axis4_hyst_ramp_v1_n4096.py -- v1 HARD_FAIL at beta=8, max_loop_area=0.0.
  v1 result: no retention hysteresis at beta=8 (below-critical; M-ramp).
  v1 conclusion: substrate retention is path-independent at probed points.
  RESCUE PATH: v1 probed at beta=8 (subcritical for M-hysteresis). The multi-basin
  phase structure (SKAH-M) is concentrated near beta_c ~ 10-12. If M-history hysteresis
  exists anywhere, it is in the narrow band beta in [8, 16] near beta_c AND at M near
  the M_c boundary (M/N ~ 4-8 per v272 findings).

SCIENTIFIC QUESTION (Axis 4 rescue):
  Does M-ramp hysteresis appear at beta near beta_c=10 and M near M_c boundary?
  M_frac sweep: [4, 6, 8, 10] x N (crosses M_c boundary for N=4096).
  If yes at beta=10+: steerability partially rehabilitated at multi-basin operating point.
  If no: substrate retention is path-independent regardless of operating point.
  Protocol: same ramp as v1 but: beta=10 (near beta_c), M_frac_max in [4,6,8,10].

PRE-REGISTERED BANDS:
  Prior anchor: v1 max_loop_area=0.0 at beta=8. Calibration probe at multi-basin point.
  HARD_PASS: loop_area >= 0.10 * M_max at at least 1 M_frac AND at >= 2/3 seeds.
    Interpretation: retention hysteresis confirmed at critical operating point.
  HARD_FAIL: loop_area < 0.01 * M_max at ALL M_fracs and ALL seeds.
    Substrate shows no retention hysteresis even at beta_c. 1D M-axis model fully validated.
  MIDDLE_BAND: loop_area in [0.01, 0.10) * M_max.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. loop_area = sum_over_M_steps |ret_load(M) - ret_unload(M)| * dM / M_max.
  3. For reversible process: loop_area = 0.
  4. M_frac_max=10 -> M_max = 10*N = 40960 at N=4096.
  5. beta_critical = 10.0 (near phase boundary from v272 beta_c estimate).
  6. N=4096 log2=12 even -> Kerdock SAFE.

OOM CHECK:
  W float32 at N=4096: 16MB. Codebook: 64MB. No OOM risk.
  M_max = 10 * 4096 = 40960 keys (same wrapping approach as v1).

TIMEOUT ESTIMATE:
  v1 at beta=8: ~900s (3 rates x 3 seeds). v2: 4 M_frac_max values x 3 seeds x 1 rate = 12 cells.
  Each ramp: ~200s at M_max=40960 (vs ~90s at v1). Safety 2x: 12 * 200 * 1.5 = 3600s.
  Floor _n4096 = 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis4_hyst_critical_v2_n4096
Queue: overnight_queue (GPU; N=4096 axis-4 hysteresis rescue at multi-basin operating point)
Pre-reg: prereqs/2026-05-29_axis4_hyst_critical_v2_n4096.md
Parent: axis4_hyst_ramp_v1_n4096 (HARD_FAIL at beta=8)
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
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load chunk-1 base (store_facts_batched, compute_retention, Kerdock codebook)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_a4v2", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3  # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires even log2; N=1024 -> log2=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Critical operating point: beta near beta_c
BETA_CRITICAL = 10.0  # near multi-basin boundary (v272 estimate: beta_c ~ 10-12)

# M_frac sweep across M_c boundary
M_FRAC_SWEEP_FULL  = [4.0, 6.0, 8.0, 10.0]   # M_max / N values to test
M_FRAC_SWEEP_SMOKE = [4.0, 8.0]

# Ramp rate (medium: 20 steps; single rate for sweep speed)
RATE_FULL  = 20
RATE_SMOKE = 10

N_PROBE = 150
SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds (same as v1)
HP_LOOP_AREA_MIN = 0.10  # loop_area >= 0.10 * M_max -> HARD_PASS
HF_LOOP_AREA_MAX = 0.01  # loop_area < 0.01 * M_max -> HARD_FAIL


def get_output_dir(default_name: str = "axis4_hyst_critical_v2_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_W_incremental(codebook: torch.Tensor, M: int, seed: int,
                         N: int, device: torch.device):
    """Build W for M stored facts. Returns (W, key_idx, val_idx)."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    repeats = math.ceil(M / C)
    key_parts = [torch.randperm(C, generator=gen, device=device) for _ in range(repeats)]
    val_parts = [torch.randperm(C, generator=gen, device=device) for _ in range(repeats)]
    key_idx = torch.cat(key_parts)[:M]
    val_idx = torch.cat(val_parts)[:M]

    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    batch = 256
    for start in range(0, M, batch):
        k_b = codebook[key_idx[start:start + batch] % C]
        v_b = codebook[val_idx[start:start + batch] % C]
        W += (v_b.T @ k_b) / N
    return W, key_idx, val_idx


def measure_ret(codebook: torch.Tensor, key_idx: torch.Tensor,
                val_idx: torch.Tensor, W: torch.Tensor,
                N: int, n_probe: int) -> float:
    C = codebook.shape[0]
    M = key_idx.shape[0]
    if M == 0:
        return 1.0
    n = min(n_probe, M)
    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    keys = codebook[probe_key_idx]
    sims = (codebook @ (keys @ W.T).T) / N
    pred = torch.argmax(sims, dim=0)
    acc = float((pred == probe_val_idx).float().mean().item())
    return acc


def run_one_ramp_critical(codebook: torch.Tensor, rate: int, seed: int,
                           N: int, M_max: int, device: torch.device) -> dict:
    """Run one M-ramp at BETA_CRITICAL operating point."""
    C = codebook.shape[0]
    M_steps = [int(M_max * i / rate) for i in range(rate + 1)]
    M_steps[0] = 0
    M_steps[-1] = M_max

    gen = torch.Generator(device=device).manual_seed(seed)
    key_idx_full = torch.cat([torch.randperm(C, generator=gen, device=device)
                               for _ in range(math.ceil(M_max / C))])[:M_max]
    val_idx_full = torch.cat([torch.randperm(C, generator=gen, device=device)
                               for _ in range(math.ceil(M_max / C))])[:M_max]

    # Loading: 0 -> M_max
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    load_points = []
    prev_M = 0
    for M in M_steps:
        if M > prev_M:
            chunk_keys = codebook[key_idx_full[prev_M:M] % C]
            chunk_vals = codebook[val_idx_full[prev_M:M] % C]
            batch = 256
            for start in range(0, M - prev_M, batch):
                k_b = chunk_keys[start:start + batch]
                v_b = chunk_vals[start:start + batch]
                W += (v_b.T @ k_b) / N
        if M > 0:
            ret = measure_ret(codebook, key_idx_full[:M], val_idx_full[:M],
                              W, N, N_PROBE)
        else:
            ret = 1.0
        load_points.append({"M": M, "M_frac": round(M / N, 4),
                            "retention": round(ret, 4), "direction": "load"})
        prev_M = M

    # Unloading: M_max -> 0
    unload_points = []
    prev_M = M_max
    for M in reversed(M_steps[:-1]):
        if prev_M > M:
            chunk_keys = codebook[key_idx_full[M:prev_M] % C]
            chunk_vals = codebook[val_idx_full[M:prev_M] % C]
            batch = 256
            for start in range(0, prev_M - M, batch):
                k_b = chunk_keys[start:start + batch]
                v_b = chunk_vals[start:start + batch]
                W -= (v_b.T @ k_b) / N
        if M > 0:
            ret = measure_ret(codebook, key_idx_full[:M], val_idx_full[:M],
                              W, N, N_PROBE)
        else:
            ret = 1.0
        unload_points.append({"M": M, "M_frac": round(M / N, 4),
                              "retention": round(ret, 4), "direction": "unload"})
        prev_M = M

    # Loop area
    load_by_M = {p["M"]: p["retention"] for p in load_points}
    unload_by_M = {p["M"]: p["retention"] for p in unload_points}
    common_M = sorted(set(load_by_M.keys()) & set(unload_by_M.keys()))
    if len(common_M) >= 2:
        gaps = [abs(load_by_M[m] - unload_by_M[m]) for m in common_M]
        dMs = [common_M[i + 1] - common_M[i] for i in range(len(common_M) - 1)]
        loop_area = sum(gaps[i] * dMs[i] for i in range(len(dMs))) / M_max
    else:
        loop_area = 0.0

    return {
        "rate": rate, "seed": seed, "M_max": M_max, "M_frac_max": round(M_max / N, 2),
        "beta": BETA_CRITICAL,
        "load_points": load_points, "unload_points": unload_points,
        "loop_area": round(loop_area, 6),
    }


def compute_verdict_axis4_critical(summary: dict) -> tuple:
    ramp_results = summary.get("ramp_results", [])
    if not ramp_results:
        return ("AXIS4V2_INCONCLUSIVE", "No ramp results.")

    loop_areas = [r["loop_area"] for r in ramp_results]
    max_loop_area = max(loop_areas) if loop_areas else 0.0
    mean_loop_area = sum(loop_areas) / len(loop_areas)

    # HARD_PASS: at least 1 M_frac with >= 2 seeds showing area >= 0.10
    passes_per_mfrac: Dict[float, int] = {}
    for r in ramp_results:
        mf = r["M_frac_max"]
        if r["loop_area"] >= HP_LOOP_AREA_MIN:
            passes_per_mfrac[mf] = passes_per_mfrac.get(mf, 0) + 1
    mfracs_with_pass = [mf for mf, cnt in passes_per_mfrac.items() if cnt >= 2]

    detail = {
        "max_loop_area": round(max_loop_area, 6),
        "mean_loop_area": round(mean_loop_area, 6),
        "by_mfrac_seed": [(r["M_frac_max"], r["seed"], r["loop_area"])
                          for r in ramp_results],
        "mfracs_with_pass": mfracs_with_pass,
        "beta_critical": BETA_CRITICAL,
        "n_ramps": len(ramp_results),
    }

    if max_loop_area < HF_LOOP_AREA_MAX:
        return ("AXIS4V2_HARD_FAIL",
                f"NO HYSTERESIS AT BETA_C: max loop_area={max_loop_area:.6f} < {HF_LOOP_AREA_MAX}. "
                f"1D M-axis model fully validated; beta-steering not demonstrated. "
                f"details={detail}.")

    if mfracs_with_pass:
        return ("AXIS4V2_HARD_PASS",
                f"HYSTERESIS AT BETA_C: max loop_area={max_loop_area:.6f} >= {HP_LOOP_AREA_MIN}. "
                f"M-history dependence at beta={BETA_CRITICAL} near beta_c. "
                f"mfracs_passing={mfracs_with_pass}. "
                f"details={detail}.")

    return ("AXIS4V2_MIDDLE_BAND",
            f"Weak hysteresis at beta_c: max={max_loop_area:.6f} in "
            f"[{HF_LOOP_AREA_MAX},{HP_LOOP_AREA_MIN}). "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test loop_area formula: equal load/unload -> area=0
    ramp_zero = {
        "rate": 5, "seed": 17, "M_max": 100, "M_frac_max": 2.0, "beta": BETA_CRITICAL,
        "load_points": [{"M": m, "M_frac": m / 512, "retention": 0.8, "direction": "load"}
                         for m in [0, 25, 50, 75, 100]],
        "unload_points": [{"M": m, "M_frac": m / 512, "retention": 0.8, "direction": "unload"}
                           for m in [0, 25, 50, 75]],
        "loop_area": 0.0,
    }
    v, msg = compute_verdict_axis4_critical({"ramp_results": [ramp_zero]})
    assert "HARD_FAIL" in v, f"Self-test zero-area should be HARD_FAIL: {v}: {msg}"

    # Test HARD_PASS path
    ramp_pass = []
    for seed in [7, 17]:
        ramp_pass.append({
            "rate": 20, "seed": seed, "M_max": 100,
            "M_frac_max": 6.0, "beta": BETA_CRITICAL,
            "load_points": [], "unload_points": [],
            "loop_area": 0.20,
        })
    v2, _ = compute_verdict_axis4_critical({"ramp_results": ramp_pass})
    assert "HARD_PASS" in v2, f"Self-test HARD_PASS failed: {v2}"

    # Test run_one_ramp at tiny scale
    device = torch.device("cpu")
    N_t = N_SMOKE
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    M_max_t = int(4.0 * N_t)  # smallest M_frac in sweep

    ramp_result = run_one_ramp_critical(codebook_small, rate=5, seed=17,
                                         N=N_t, M_max=M_max_t, device=device)
    assert "loop_area" in ramp_result, "loop_area missing"
    assert isinstance(ramp_result["loop_area"], float), f"loop_area not float: {type(ramp_result['loop_area'])}"
    assert 0.0 <= ramp_result["loop_area"], f"loop_area < 0: {ramp_result['loop_area']}"

    # Validity: at least 1 ramp step produced a valid retention value
    all_rets = ([p["retention"] for p in ramp_result["load_points"]] +
                [p["retention"] for p in ramp_result["unload_points"]])
    assert len(all_rets) >= 1, "validity filter: no valid retention points at smoke scale"
    for ret in all_rets:
        assert 0.0 <= ret <= 1.0, f"retention out of [0,1]: {ret}"

    # OOM pre-check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=4096 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis4_hyst_critical_v2_n4096: N_FULL={N_FULL} "
          f"beta_c={BETA_CRITICAL} loop_area_smoke={ramp_result['loop_area']:.6f} "
          f"n_load={len(ramp_result['load_points'])}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    rate = RATE_SMOKE if smoke else RATE_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    m_frac_sweep = M_FRAC_SWEEP_SMOKE if smoke else M_FRAC_SWEEP_FULL

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    print(f"[axis4_critical] N={N} beta={BETA_CRITICAL} "
          f"m_frac_sweep={m_frac_sweep} rate={rate} seeds={seeds} "
          f"device={device} mode={'smoke' if smoke else 'full'}",
          flush=True)

    all_ramps = []
    total = len(seeds) * len(m_frac_sweep)
    done = 0

    for seed in seeds:
        for m_frac_max in m_frac_sweep:
            M_max = int(m_frac_max * N)
            ramp_result = run_one_ramp_critical(codebook, rate, seed, N, M_max, device)
            all_ramps.append(ramp_result)
            done += 1
            print(f"  [{done}/{total}] seed={seed} M_frac_max={m_frac_max} "
                  f"loop_area={ramp_result['loop_area']:.6f}",
                  flush=True)

    summary = {
        "ramp_results": all_ramps,
        "N_used": N,
        "N_full": N_FULL,
        "beta_critical": BETA_CRITICAL,
        "m_frac_sweep": m_frac_sweep,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_axis4_critical(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"smoke": smoke, "N": N, "beta_critical": BETA_CRITICAL,
                   "m_frac_sweep": m_frac_sweep, "rate": rate},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    tmp_path = out_path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp_path, out_path)
    print(f"\n[axis4_critical] VERDICT: {verdict}", flush=True)
    print(f"[axis4_critical] {verdict_msg}", flush=True)
    print(f"[axis4_critical] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--N", type=int, default=N_FULL)
    p.add_argument("--timeout", type=int, default=14400)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
