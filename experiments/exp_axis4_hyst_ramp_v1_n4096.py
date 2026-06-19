"""AXIS-4 HYSTERESIS LOOP TOPOLOGY: M-ramp 0->M_max->0 at multiple rates.

CONTEXT:
  Pred-4 (v211): max_gap=1.84 = first-order multi-basin hysteresis (SKAH-M signature).
  That experiment used BPC as the order parameter with a beta ramp.
  This experiment uses RETENTION as the order parameter with an M-ramp:
    ramp M from 0 -> M_max -> 0 (analogous to magnetic hysteresis loop B vs H).

  The key question: does the retention-vs-M curve show a HYSTERESIS LOOP?
  If yes: the substrate has memory of the loading history (first-order phase transition).
  If no: the substrate is purely state-dependent (no memory effect).

SCIENTIFIC QUESTION (Axis 4 -- hysteresis loop topology):
  Does the substrate exhibit an M-based retention hysteresis loop?
  Specifically: does retention(M_load) != retention(M_unload) at the same M value?
  Loop area = integral |ret_load(M) - ret_unload(M)| dM over [0, M_max].

  Protocol: ramp M from 0 to M_max (loading), then back to 0 (unloading).
  At each M step: store those facts (loading) or remove them (unloading) and measure ret.
  Three rates: slow (5 large steps), medium (20 steps), fast (50 steps).
  M_max = 8*N (spans the phase transition from chunk2).
  N=4096, beta=8 (training beta from PB3).
  3 seeds.

PRE-REGISTERED BANDS:
  Prior anchor: Pred-4 v211 max_gap=1.84 (BPC-based hysteresis at N=1024).
  Calibration probe for M-based retention hysteresis (different order parameter).
  Bands widened to +-50% per calibration-probe policy (different protocol from Pred-4).

  HARD_PASS: loop_area >= 0.10 * M_max at at least 1 rate AND at >= 2/3 seeds.
    Interpretation: retention hysteresis loop confirmed; substrate has phase memory.
  HARD_FAIL: loop_area < 0.01 * M_max at ALL rates and ALL seeds.
    Substrate shows no retention hysteresis (path-independent, no history effect).
  MIDDLE_BAND: loop_area in [0.01, 0.10) * M_max.

FORMULA SELF-TESTS:
  1. loop_area = sum_over_M_steps |ret_load(M) - ret_unload(M)| * dM / M_max.
  2. For reversible process (no hysteresis): loop_area = 0.
  3. At M=0: ret = 1.0 (no memories -> perfect retrieval; trivial).
  4. At M=M_max (after full loading): ret should be near chunk2's M/N=8 value ~0.5.
  5. dM_step: for slow rate (5 steps over 0->8N): dM = 8N/5 = ~6553 at N=4096.
  6. N == 4096 (PROT-018).

OOM CHECK:
  W float32 at N=4096: 64MB. Codebook: 64MB.
  M_max = 8 * 4096 = 32768 keys (stored in key list: 32768 * 4096 * 4 = 512MB!).
  The key list is dense at high M. Fix: do NOT store all keys. Instead, reuse
  codebook indices (keys = codebook[idx % C]). Only keep W and probe subset.
  Peak: W (64MB) + codebook (64MB) + index buffer (32768 * 4 bytes = 128KB) = ~130MB. OK.

TIMEOUT ESTIMATE:
  Each ramp step: store/remove facts (O(dM)) + measure ret (O(n_probe)).
  Slow rate 5 steps x 2 directions (load+unload): 10 steps. Each step M grows by 6553.
  Cost per step at large M: ~6553/256 = ~25 batches for W update.
  Per step: ~0.1s on GPU. 3 rates: 5+20+50=75 steps * 2 = 150 total. 3 seeds.
  Total: 150 steps * 3 seeds * ~0.2s = 90s. Safety 10x for large-M overhead: 900s.
  PROT-019: _n4096 -> floor 3600s. Using 3600s.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: axis4_hyst_ramp_v1_n4096
Queue: overnight_queue (GPU; N=4096 M-ramp hysteresis loop)
Pre-reg: preregs/2026-05-28_axis4_hyst_ramp_v1_n4096.md
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
_c1_spec = importlib.util.spec_from_file_location("axis1c1_a4", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)
v3 = c1.v3  # Kerdock codebook builder

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale (Kerdock requires even log2; N=1024 -> log2=10 OK)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Ramp parameters
M_MAX_FRAC = 8.0    # ramp to M/N=8 (spans the phase transition)
BASE_BETA = 8.0     # operating beta from PB3

# Ramp rates: number of steps in the HALF-ramp (0->M_max)
RATES_FULL = [5, 20, 50]    # slow, medium, fast
RATES_SMOKE = [5, 10]       # smoke: 2 rates

N_PROBE = 150       # probe points for retention measurement
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Thresholds
HP_LOOP_AREA_MIN = 0.10  # loop_area >= 0.10 * M_max = HARD_PASS
HF_LOOP_AREA_MAX = 0.01  # loop_area < 0.01 * M_max = HARD_FAIL (no hysteresis)


def get_output_dir(default_name: str = "axis4_hyst_ramp_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build_W_at_M(codebook: torch.Tensor, M: int, seed: int, N: int,
                  device: torch.device) -> tuple:
    """Build W for M stored facts. Returns (W, key_idx, val_idx)."""
    C = codebook.shape[0]
    gen = torch.Generator(device=device).manual_seed(seed)
    # Wrap around codebook if M > C
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


def measure_ret_at_M(codebook: torch.Tensor, key_idx: torch.Tensor,
                      val_idx: torch.Tensor, W: torch.Tensor,
                      N: int, beta: float, n_probe: int) -> float:
    """Measure retention at current W state using stored key/val indices."""
    C = codebook.shape[0]
    M = key_idx.shape[0]
    if M == 0:
        return 1.0  # no facts stored -> perfect retrieval (trivial)
    n = min(n_probe, M)
    probe_key_idx = key_idx[:n] % C
    probe_val_idx = val_idx[:n] % C
    keys = codebook[probe_key_idx]  # (n, N)
    # Similarity: (C, n) = codebook @ W @ keys.T
    sims = (codebook @ (keys @ W.T).T) / N  # (C, n)
    pred = torch.argmax(sims, dim=0)        # (n,)
    acc = float((pred == probe_val_idx).float().mean().item())
    return acc


def run_one_ramp(codebook: torch.Tensor, rate: int, seed: int,
                  N: int, M_max: int, device: torch.device) -> dict:
    """Run one loading (0->M_max) + unloading (M_max->0) cycle.
    Returns: {rate, seed, load_points, unload_points, loop_area}
    Each point: {M, M_frac, retention, direction}.
    """
    C = codebook.shape[0]
    # M checkpoints for half-ramp (0 to M_max)
    M_steps = [int(M_max * i / rate) for i in range(rate + 1)]
    M_steps[0] = 0
    M_steps[-1] = M_max

    # ---- LOADING: build W incrementally from 0 to M_max ----
    W = torch.zeros(N, N, dtype=torch.float32, device=device)
    # Pre-generate all key/val indices
    gen = torch.Generator(device=device).manual_seed(seed)
    key_idx_full = torch.cat([torch.randperm(C, generator=gen, device=device)
                               for _ in range(math.ceil(M_max / C))])[:M_max]
    val_idx_full = torch.cat([torch.randperm(C, generator=gen, device=device)
                               for _ in range(math.ceil(M_max / C))])[:M_max]

    load_points = []
    prev_M = 0
    for M in M_steps:
        if M > prev_M:
            # Add facts from prev_M to M
            chunk_keys = codebook[key_idx_full[prev_M:M] % C]
            chunk_vals = codebook[val_idx_full[prev_M:M] % C]
            batch = 256
            for start in range(0, M - prev_M, batch):
                k_b = chunk_keys[start:start + batch]
                v_b = chunk_vals[start:start + batch]
                W += (v_b.T @ k_b) / N
        if M > 0:
            ret = measure_ret_at_M(codebook, key_idx_full[:M], val_idx_full[:M],
                                    W, N, BASE_BETA, N_PROBE)
        else:
            ret = 1.0  # trivial
        load_points.append({"M": M, "M_frac": round(M / N, 4), "retention": round(ret, 4),
                             "direction": "load"})
        prev_M = M

    # ---- UNLOADING: remove facts incrementally from M_max to 0 ----
    unload_points = []
    prev_M = M_max
    for M in reversed(M_steps[:-1]):  # M_max -> ... -> 0
        if prev_M > M:
            # Remove facts from prev_M down to M
            chunk_keys = codebook[key_idx_full[M:prev_M] % C]
            chunk_vals = codebook[val_idx_full[M:prev_M] % C]
            batch = 256
            for start in range(0, prev_M - M, batch):
                k_b = chunk_keys[start:start + batch]
                v_b = chunk_vals[start:start + batch]
                W -= (v_b.T @ k_b) / N
        if M > 0:
            ret = measure_ret_at_M(codebook, key_idx_full[:M], val_idx_full[:M],
                                    W, N, BASE_BETA, N_PROBE)
        else:
            ret = 1.0  # trivial
        unload_points.append({"M": M, "M_frac": round(M / N, 4), "retention": round(ret, 4),
                               "direction": "unload"})
        prev_M = M

    # Compute loop area: |ret_load(M) - ret_unload(M)| integrated over M
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
        "rate": rate,
        "seed": seed,
        "M_max": M_max,
        "load_points": load_points,
        "unload_points": unload_points,
        "loop_area": round(loop_area, 6),
    }


def compute_verdict_axis4(summary: dict) -> tuple:
    """Verdict: test for M-ramp hysteresis loop area."""
    ramp_results = summary.get("ramp_results", [])
    if not ramp_results:
        return ("AXIS4_INCONCLUSIVE", "No ramp results computed.")

    # Compute max loop_area per (rate, seed)
    loop_areas = [r["loop_area"] for r in ramp_results]
    max_loop_area = max(loop_areas) if loop_areas else 0.0
    mean_loop_area = sum(loop_areas) / len(loop_areas)

    # Check HARD_PASS: at least 1 (rate, seed) with loop_area >= 0.10
    passes_per_rate: Dict[int, int] = {}
    for r in ramp_results:
        rate = r["rate"]
        if r["loop_area"] >= HP_LOOP_AREA_MIN:
            passes_per_rate[rate] = passes_per_rate.get(rate, 0) + 1

    rates_with_pass = [rate for rate, cnt in passes_per_rate.items() if cnt >= 2]

    detail = {
        "max_loop_area": round(max_loop_area, 6),
        "mean_loop_area": round(mean_loop_area, 6),
        "loop_areas_by_rate_seed": [(r["rate"], r["seed"], r["loop_area"])
                                     for r in ramp_results],
        "rates_with_pass": rates_with_pass,
        "n_ramps": len(ramp_results),
    }

    if max_loop_area < HF_LOOP_AREA_MAX:
        return ("AXIS4_HARD_FAIL",
                f"NO RETENTION HYSTERESIS: max loop_area={max_loop_area:.6f} < {HF_LOOP_AREA_MAX}. "
                f"Substrate retention is path-independent (no M-history effect). "
                f"details={detail}.")

    if rates_with_pass:
        return ("AXIS4_HARD_PASS",
                f"M-RAMP HYSTERESIS CONFIRMED: max loop_area={max_loop_area:.6f} >= {HP_LOOP_AREA_MIN}. "
                f"rates_passing: {rates_with_pass}. "
                f"Retention shows path-dependent first-order signature. "
                f"details={detail}.")

    return ("AXIS4_MIDDLE_BAND",
            f"Weak hysteresis: max_loop_area={max_loop_area:.6f} in [{HF_LOOP_AREA_MAX},{HP_LOOP_AREA_MIN}). "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Test loop_area formula: equal load/unload -> area=0
    ramp_zero = {
        "rate": 5, "seed": 17, "M_max": 100,
        "load_points": [{"M": m, "M_frac": m / 512, "retention": 0.8, "direction": "load"}
                         for m in [0, 25, 50, 75, 100]],
        "unload_points": [{"M": m, "M_frac": m / 512, "retention": 0.8, "direction": "unload"}
                           for m in [0, 25, 50, 75]],
        "loop_area": 0.0,
    }
    v, msg = compute_verdict_axis4({"ramp_results": [ramp_zero]})
    assert "HARD_FAIL" in v, f"Self-test zero-area should be HARD_FAIL: {v}: {msg}"

    # Test HARD_PASS path: large loop area
    ramp_pass = []
    for seed in [7, 17]:
        ramp_pass.append({
            "rate": 5, "seed": seed, "M_max": 100,
            "load_points": [],
            "unload_points": [],
            "loop_area": 0.20,  # >> 0.10
        })
    v2, _ = compute_verdict_axis4({"ramp_results": ramp_pass})
    assert "HARD_PASS" in v2, f"Self-test HARD_PASS failed: {v2}"

    # Test run_one_ramp at tiny scale (smoke-within-selftest)
    device = torch.device("cpu")
    N_t = N_SMOKE
    codebook_small, _info = v3.make_kerdock_4coset_codebook(N_t, device)
    M_max_t = int(M_MAX_FRAC * N_t)

    ramp_result = run_one_ramp(codebook_small, rate=3, seed=17,
                                N=N_t, M_max=M_max_t, device=device)
    assert "loop_area" in ramp_result, "loop_area missing from ramp result"
    assert isinstance(ramp_result["loop_area"], float), \
        f"loop_area should be float: {type(ramp_result['loop_area'])}"
    assert 0.0 <= ramp_result["loop_area"], \
        f"loop_area < 0: {ramp_result['loop_area']}"
    # At M=0 (trivial): retention = 1.0 (no interference)
    if ramp_result["load_points"]:
        ret_M0 = ramp_result["load_points"][0]["retention"]
        assert 0.0 <= ret_M0 <= 1.0, f"ret at M=0 out of [0,1]: {ret_M0}"

    # Validity filter: at least 1 ramp step produced a valid retention value
    all_rets = ([p["retention"] for p in ramp_result["load_points"]] +
                [p["retention"] for p in ramp_result["unload_points"]])
    assert len(all_rets) >= 1, "validity filter: no valid retention points from ramp"

    # OOM pre-check: W at N=4096
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N=4096 = {oom_bytes:.2e} >= 6GB"

    print(f"[SELFTEST PASS] axis4_hyst_ramp_v1_n4096: N_FULL={N_FULL} "
          f"loop_area_smoke={ramp_result['loop_area']:.6f} n_load={len(ramp_result['load_points'])}",
          flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    rates = RATES_SMOKE if smoke else RATES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    M_max = int(M_MAX_FRAC * N)

    t0 = time.time()
    out_dir = get_output_dir()
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    print(f"[axis4] N={N} M_max={M_max} (M/N={M_MAX_FRAC}) beta={BASE_BETA} "
          f"rates={rates} seeds={seeds} device={device} mode={'smoke' if smoke else 'full'}",
          flush=True)

    all_ramps = []
    total = len(seeds) * len(rates)
    done = 0

    for seed in seeds:
        for rate in rates:
            ramp_result = run_one_ramp(codebook, rate, seed, N, M_max, device)
            all_ramps.append(ramp_result)
            done += 1
            print(f"  [{done}/{total}] seed={seed} rate={rate} "
                  f"loop_area={ramp_result['loop_area']:.6f}",
                  flush=True)

    summary = {
        "ramp_results": all_ramps,
        "N_used": N,
        "N_full": N_FULL,
        "M_max_frac": M_MAX_FRAC,
        "M_max": M_max,
        "base_beta": BASE_BETA,
        "smoke": smoke,
    }
    verdict, verdict_msg = compute_verdict_axis4(summary)
    elapsed = time.time() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {"smoke": smoke, "N": N, "M_max_frac": M_MAX_FRAC,
                   "rates": rates, "base_beta": BASE_BETA},
        "summary": summary,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n[axis4] VERDICT: {verdict}", flush=True)
    print(f"[axis4] {verdict_msg}", flush=True)
    print(f"[axis4] elapsed={elapsed:.1f}s output={out_path}", flush=True)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--timeout", type=int, default=3600)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
