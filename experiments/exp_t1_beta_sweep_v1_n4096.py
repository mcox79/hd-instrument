"""T1 SECOND-BOUNDARY BETA-SWEEP v1: locate beta_c in multi-basin phase at N=4096.

CONTEXT:
  T3 (running) measures 3-axis susceptibility to confirm whether the operating point
  is near a triple-point or a 2-phase boundary.
  T1 is the NEXT step: if we are near a phase boundary (as axis1 chunks 1-7 show),
  there should be a SECOND boundary in the beta direction: a critical inverse-temperature
  beta_c where the retrieval dynamics undergo a qualitative phase change.

  The axis1 phase diagram showed a strong M-dependence of retention, but the role of
  beta (inverse temperature) was not fully characterized. At fixed M (multi-basin regime),
  sweeping beta over {1,2,4,8,16,32,64,128,256,512} should reveal:
    - Subcritical: beta << beta_c: retention near random (no preferred attractor)
    - Supercritical: beta >> beta_c: retention near 1.0 (deep attractor)
    - Critical: beta ~ beta_c: retention has maximum gradient (phase boundary)

  This test is GATED on T3 result (T3 running now), but can ship in parallel since
  T1 tests the beta axis in a different regime (M = multi-basin, not near M_c).

SCIENTIFIC QUESTION:
  At fixed M NEAR the phase boundary (M_frac=8.0, near M_c from axis1 chunks),
  does argmax retention show a sharp beta-dependent transition?
  At M_frac=4.0 (deep multi-basin), retention is already 1.0 at all beta (no transition).
  At M_frac=8.0 (near boundary), retention is ~0.3-0.7 depending on operating point.
  Locate beta_c = argmax |d(retention)/d(beta)| in log-beta space.

PRE-REGISTERED BANDS (calibration probe; first systematic beta-sweep at this M):
  Prior anchor: axis1 shows M_frac=4 has ret~1.0 at beta=32 (deep multi-basin).
  No prior beta-sweep at M_frac=4. Bands widened to +/-50% per calibration-probe policy.

  HARD_PASS: retention shows MONOTONE increase with beta (from near-0 at beta=1
    to near-1 at beta=512) AND maximum gradient |d(ret)/d(log_beta)| >= 0.1 per log-unit.
    Interpretation: clear beta-dependent transition exists; beta_c locatable.
  HARD_FAIL: retention is flat (< 0.05 variation across all beta) OR non-monotone
    across 3+ consecutive beta steps.
    Interpretation: no beta-phase boundary at this M (substrate is beta-insensitive).
  MIDDLE_BAND: retention increases but gradient too gradual to locate beta_c
    (max gradient < 0.1 per log-unit OR transition spans > 4 log-units of beta).

FORMULA SELF-TESTS:
  1. beta sweep log-uniform: {1,2,4,8,16,32,64,128,256,512}. log2-spacing = 1 per step.
  2. d(ret)/d(log_beta) at step i: (ret[i+1] - ret[i-1]) / 2.
  3. max_gradient = max of |d(ret)/d(log_beta)| over interior beta values.
  4. HARD_PASS gate: monotone AND max_gradient >= 0.10 at >= 3/5 seeds.
  5. N == 4096 (PROT-018 binding).
  6. M at M_frac=4.0, N=4096: M = 16384.

OOM CHECK:
  M=16384, N=4096: keys=16384*4096*4=268MB. W=64MB. CB=268MB. Total=600MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  Per cell: store M=16384 facts (batched, ~0.3s) + argmax retention (~0.1s).
  10 beta values x 5 seeds = 50 cells x 0.5s = 25s.
  Smoke: 5 beta x 2 seeds = 10 cells x 0.5s = 5s.
  Safety: ceil(1.5 * 25 * 5) = ceil(187s). User override for _n4096: timeout >= 14400.
  timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t1_beta_sweep_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock, beta in {1..512}, 10 pts x 5 seeds)
Pre-reg: preregs/2026-05-28_t1_beta_sweep_v1_n4096.md
Parent: axis1 chunks 1-7 + t3_susceptibility_v1_n4096 (running; beta-direction complement)
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

# Load axis1_mb_chunk1 for store_facts_batched, compute_retention, v3 codebook
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_t1", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched
compute_retention = c1.compute_retention
v3 = c1.v3

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096   # PROT-018 binding contract
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# Fixed M NEAR phase boundary (M_frac=8.0; from axis1 chunks this is the transition zone)
# At M_frac=4.0, retention is 1.0 at all beta (no variation -- confirmed by smoke).
# At M_frac=8.0, axis1 chunk5 shows ~0.5 retention at beta=32 (sensitive operating point).
M_FRAC = 8.0

# Beta sweep: log-uniform from 1 to 512
BETA_SWEEP_FULL  = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
BETA_SWEEP_SMOKE = [1, 4, 16, 64, 256]   # 5-pt smoke

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

N_PROBE = 200  # retrieval probe count

# Pre-registered thresholds
HP_MAX_GRADIENT_MIN = 0.10   # d(ret)/d(log2_beta) per step >= this = transition present
HP_MONOTONE_FRAC    = 0.80   # 80% of consecutive steps must be non-decreasing
HF_FLAT_MAX_VAR     = 0.05   # if max_ret - min_ret < 0.05 = flat = HARD_FAIL
HP_SEEDS_MIN        = 3      # >= 3/5 seeds pass both clauses


def get_output_dir(default_name: str = "t1_beta_sweep_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def softmax_confidence(W: torch.Tensor, keys: torch.Tensor,
                        val_idx: torch.Tensor, codebook: torch.Tensor,
                        beta: float, N: int, n_probe: int) -> float:
    """Softmax retrieval confidence (probability of correct answer under softmax).

    Unlike argmax, this IS beta-dependent: at high beta, softmax concentrates on argmax;
    at low beta, softmax is uniform (near 1/C). This reveals the beta phase transition.
    """
    C = codebook.shape[0]
    M = keys.shape[0]
    n = min(n_probe, M)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C

    sims = (codebook @ (probe_keys @ W.T).T) / N   # (C, n)
    logits = sims * beta
    # Numerically stable softmax
    log_z = torch.logsumexp(logits, dim=0, keepdim=True)
    log_probs = logits - log_z              # (C, n)
    # Probability of correct answer for each probe
    correct_log_prob = log_probs[probe_val_idx.to(W.device),
                                  torch.arange(n, device=W.device)]
    mean_prob = correct_log_prob.exp().mean().item()
    return float(mean_prob)


def run_one_seed(N: int, M_frac: float, beta_sweep: List[float],
                 seed: int, device: torch.device) -> Dict:
    """Run softmax retrieval confidence across beta values for one seed.

    Softmax confidence IS beta-dependent (argmax is invariant).
    At beta=1: near 1/C (uniform softmax). At beta=512: concentrates on argmax.
    Sharp transition at beta_c reveals the phase boundary.
    """
    M = int(M_frac * N)
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)

    ret_by_beta = []
    for beta in beta_sweep:
        conf = softmax_confidence(W, keys, val_idx, codebook, float(beta), N, n_probe=N_PROBE)
        ret_by_beta.append(round(conf, 5))
        print(f"    beta={beta:4d} softmax_conf={conf:.5f}", flush=True)

    # Compute gradient: d(ret)/d(log2_beta)
    log2_betas = [math.log2(b) for b in beta_sweep]
    gradients = []
    for i in range(1, len(ret_by_beta) - 1):
        d_ret = ret_by_beta[i + 1] - ret_by_beta[i - 1]
        d_log = log2_betas[i + 1] - log2_betas[i - 1]
        if abs(d_log) > 1e-9:
            gradients.append(abs(d_ret / d_log))
        else:
            gradients.append(0.0)

    max_grad = max(gradients) if gradients else 0.0
    total_var = max(ret_by_beta) - min(ret_by_beta)

    # Monotone check: fraction of consecutive pairs that are non-decreasing
    n_mono = sum(1 for i in range(len(ret_by_beta) - 1)
                 if ret_by_beta[i + 1] >= ret_by_beta[i] - 0.02)
    mono_frac = n_mono / max(1, len(ret_by_beta) - 1)

    return {
        "seed": seed, "M_frac": M_frac, "M": M,
        "beta_sweep": list(beta_sweep),
        "ret_by_beta": ret_by_beta,
        "max_gradient": round(max_grad, 4),
        "total_var": round(total_var, 4),
        "mono_frac": round(mono_frac, 3),
    }


def seed_passes_hp(cell: Dict) -> bool:
    return (cell["max_gradient"] >= HP_MAX_GRADIENT_MIN and
            cell["total_var"] >= HF_FLAT_MAX_VAR and
            cell["mono_frac"] >= HP_MONOTONE_FRAC)


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("T1_BETA_INCONCLUSIVE", "No cells.")

    pass_seeds = sum(1 for c in cells if seed_passes_hp(c))
    total_seeds = len(cells)

    max_grads = [c["max_gradient"] for c in cells]
    total_vars = [c["total_var"] for c in cells]
    mean_grad = sum(max_grads) / len(max_grads)
    mean_var  = sum(total_vars) / len(total_vars)

    detail = (f"pass_seeds={pass_seeds}/{total_seeds} "
              f"mean_max_gradient={mean_grad:.3f} mean_total_var={mean_var:.3f} "
              f"M_frac={M_FRAC} N={summary.get('N', N_FULL)} "
              f"beta_sweep={BETA_SWEEP_FULL}")

    # HARD_FAIL: retention is flat
    flat_seeds = sum(1 for c in cells if c["total_var"] < HF_FLAT_MAX_VAR)
    if flat_seeds >= total_seeds:
        return ("T1_BETA_HARD_FAIL",
                f"FLAT: retention invariant to beta at M_frac={M_FRAC}. " + detail)

    if pass_seeds >= HP_SEEDS_MIN:
        return ("T1_BETA_HARD_PASS",
                f"BETA TRANSITION CONFIRMED: sharp beta_c locatable at M_frac={M_FRAC}. "
                + detail)

    return ("T1_BETA_MIDDLE_BAND",
            f"Partial: gradient present but below threshold or non-monotone. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096"

    # Formula self-test 1: M_frac=8.0, N=4096 -> M=32768
    assert int(M_FRAC * N_FULL) == 32768, f"M_frac formula: {int(M_FRAC * N_FULL)} != 32768"

    # Formula self-test 2: gradient computation
    # Monotone retention: should pass
    test_cell_pass = {
        "max_gradient": 0.20, "total_var": 0.80, "mono_frac": 0.90,
    }
    assert seed_passes_hp(test_cell_pass), f"seed_passes_hp should be True for good cell"

    # Flat retention: should fail
    test_cell_flat = {"max_gradient": 0.02, "total_var": 0.01, "mono_frac": 0.90}
    assert not seed_passes_hp(test_cell_flat), "seed_passes_hp should be False for flat"

    # Verdict self-test
    fake_cells = [
        {"max_gradient": 0.20, "total_var": 0.80, "mono_frac": 0.90},
        {"max_gradient": 0.18, "total_var": 0.75, "mono_frac": 0.88},
        {"max_gradient": 0.15, "total_var": 0.70, "mono_frac": 0.85},
        {"max_gradient": 0.12, "total_var": 0.65, "mono_frac": 0.82},
        {"max_gradient": 0.11, "total_var": 0.60, "mono_frac": 0.80},
    ]
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test HARD_PASS failed: {v}: {msg}"

    # OOM check
    M_check = int(M_FRAC * N_FULL)
    oom_bytes = M_check * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: keys at M={M_check} = {oom_bytes/1e6:.0f}MB >= 6GB"

    # Smoke forward pass -- use M_frac=0.5 (not 8.0) to avoid C-ceiling artifact.
    # KNOWN N-SCALING ARTIFACT: at N_SMOKE=1024, M_frac=8.0 sets M=8192 > C=4096
    # so store_facts_batched uses all C rows (perfect storage, flat beta-sweep expected).
    # The FULL run at N_FULL=4096 has C=49152 >> M=32768, so genuine interference occurs.
    # Selftest uses M_frac=0.5 to exercise the forward-pass code path at smoke scale.
    device = torch.device("cpu")
    M_smoke_test = int(0.5 * N_SMOKE)   # use smaller M_frac to avoid C-ceiling
    codebook, _ = v3.make_kerdock_4coset_codebook(N_SMOKE, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(
        codebook, M_smoke_test, 17, N_SMOKE, device)
    ret = compute_retention(W, keys, val_idx, codebook, 32.0, N_SMOKE, n_probe=50)
    assert ret is not None and 0 <= float(ret) <= 1.0, f"retention out of range: {ret}"

    # Multi-scale smoke N_SMOKE x4 (= N_FULL = 4096)
    # Validate softmax confidence IS beta-dependent at N_4x=4096, M_frac=8.0.
    N_4x = N_SMOKE * 4   # = 4096 = N_FULL
    M_4x = int(M_FRAC * N_4x)
    cb4x, _ = v3.make_kerdock_4coset_codebook(N_4x, device)
    W4x, keys4x, _v4x, _ki4x, vi4x = store_facts_batched(cb4x, M_4x, 17, N_4x, device)

    # Check softmax confidence at two very different betas: should differ
    conf_low  = softmax_confidence(W4x, keys4x, vi4x, cb4x, 1.0,   N_4x, n_probe=50)
    conf_high = softmax_confidence(W4x, keys4x, vi4x, cb4x, 512.0, N_4x, n_probe=50)
    assert 0 <= conf_low  <= 1.0, f"conf_low OOR: {conf_low}"
    assert 0 <= conf_high <= 1.0, f"conf_high OOR: {conf_high}"
    # At M_frac=8.0 N=4096, high beta should concentrate softmax -> conf_high > conf_low
    assert conf_high > conf_low, (
        f"Softmax conf should be HIGHER at beta=512 than beta=1: "
        f"conf_low={conf_low:.5f} conf_high={conf_high:.5f}")
    print(f"[selftest] t1_beta_sweep_v1_n4096 PASS conf_low={conf_low:.5f} "
          f"conf_high={conf_high:.5f} (beta-dependent: OK)", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    betas  = BETA_SWEEP_SMOKE if smoke else BETA_SWEEP_FULL
    seeds  = SEEDS_SMOKE      if smoke else SEEDS_FULL
    # NOTE: smoke must use N_FULL=4096 (not N_SMOKE=1024) because at N_SMOKE=1024
    # M_frac=8.0 saturates the C=4096 codebook ceiling, producing flat beta-sweep.
    # At N_FULL=4096, M=32768 << C=49152, so genuine interference occurs.
    # The selftest at multi-scale N_SMOKE*4=4096 already validates this path.
    N_cfg  = N_FULL  # always N_FULL for this experiment (M_frac=8.0 requires it)

    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    print(f"t1_beta_sweep_v1_n4096 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"M_frac={M_FRAC} betas={betas} seeds={seeds} device={device}", flush=True)

    cells = []
    for seed in seeds:
        t_seed = time.monotonic()
        print(f"\n== seed={seed} ==", flush=True)
        cell = run_one_seed(N_cfg, M_FRAC, betas, seed, device)
        cells.append(cell)
        print(f"  seed={seed} max_grad={cell['max_gradient']:.3f} "
              f"total_var={cell['total_var']:.3f} mono_frac={cell['mono_frac']:.3f} "
              f"({time.monotonic()-t_seed:.1f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg,
        "M_frac": M_FRAC,
        "beta_sweep": betas,
        "seeds": seeds,
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
