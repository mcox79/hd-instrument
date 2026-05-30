"""ADAPTIVE CLEANUP OPERATOR v1 at N=4096.

CONTEXT:
  Standard substrate cleanup: argmax(W @ k_query). What if we apply a tunable
  cleanup operator: project onto top-k codeword space scaled by strength alpha?
  Test 7 strength values; identify operating-point-specific optimum.

SCIENTIFIC QUESTION:
  Does cleanup-strength = alpha * (max-codeword projection) + (1-alpha) * raw
  yield >= 5% retention improvement over standard (alpha=1.0)?

CLEANUP OPERATOR:
  For query k:
    raw   = W @ k
    cand  = top-k codewords by sim(c, raw)  (k=1 used here)
    out   = alpha * raw_proj_onto_cand_subspace + (1-alpha) * raw
  Then argmax(codebook @ out). At alpha=1.0 this collapses to standard cleanup;
  at alpha=0.0 this skips cleanup; in between modulates strength.

PRE-REGISTERED BANDS:
  HARD_PASS: optimal alpha != 1.0 AND retention(best_alpha) - retention(1.0)
    >= 0.05 in >= 3 of 5 seeds.
  HARD_FAIL: alpha=1.0 optimal in >= 4 of 5 seeds (no benefit).
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. alpha=1.0: cleanup_out == cand. Verify in selftest.
  3. alpha=0.0: cleanup_out == raw. Verify in selftest.
  4. M = 2*N = 8192 (M_frac=2 production).

OOM CHECK: M=8192. keys=134MB. W=64MB. CB=805MB. Total ~1GB. OK.

TIMEOUT ESTIMATE: 7 alphas * 5 seeds. ~5s/cell. ~175s. Budget 14400s.

N-suffix: _n4096 (PROT-018).
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

from experiments._metric_battery import make_substrate  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_clean", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_FRAC  = 2.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
ALPHA_SWEEP = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0]
BETA = 8.0
N_PROBE = 200

HP_MIN_IMPROVEMENT = 0.05
HP_N_SEEDS = 3
HF_STD_OPTIMAL_N = 4


def cleanup(W: torch.Tensor, k: torch.Tensor, codebook: torch.Tensor,
            alpha: float, N_use: int) -> torch.Tensor:
    """Adaptive cleanup with strength alpha.

    raw = W @ k (per-row)
    For each query, find top-1 candidate codeword c*; cleanup output is
    alpha * c* + (1 - alpha) * raw. At alpha=1.0 this IS standard projection
    onto top codeword (replaces the noisy raw with the clean codeword). At
    alpha=0.0 this is identity (no cleanup). alpha>1.0 over-corrects.
    """
    raw = k @ W.T                          # (n, N)
    sims = (codebook @ raw.T) / N_use      # (C, n)
    top_idx = torch.argmax(sims, dim=0)
    cand = codebook[top_idx]               # (n, N)
    return alpha * cand + (1.0 - alpha) * raw


def measure_retention_at_alpha(N_use: int, M: int, seed: int, alpha: float,
                                device: torch.device) -> float:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    C = codebook.shape[0]
    n = min(N_PROBE, M)
    probe_keys = keys[:n]
    probe_val  = val_idx[:n] % C
    out = cleanup(W, probe_keys, codebook, alpha, N_use)
    # Score: argmax(codebook @ out) == probe_val?
    final_sims = (codebook @ out.T) / N_use
    pred = torch.argmax(final_sims, dim=0)
    acc = float((pred == probe_val.to(device)).float().mean().item())
    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return acc


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("ACO_INCONCLUSIVE", "No seeds.")
    n_improved = 0; n_std_optimal = 0
    detail = []
    for d in per_seed:
        best = d["best_alpha"]
        std  = d["retention_at_1p0"]
        bret = d["retention_at_best"]
        gain = bret - std
        detail.append(f"seed{d['seed']}:best={best:g}@{bret:.3f}(gain{gain:+.3f})")
        if best != 1.0 and gain >= HP_MIN_IMPROVEMENT:
            n_improved += 1
        if best == 1.0:
            n_std_optimal += 1
    info = (f"n_improved={n_improved}/{len(per_seed)} "
            f"n_std_opt={n_std_optimal}/{len(per_seed)} " + " ".join(detail))
    if n_improved >= HP_N_SEEDS:
        return ("ACO_HARD_PASS", f"ADAPTIVE_HELPS: " + info)
    if n_std_optimal >= HF_STD_OPTIMAL_N:
        return ("ACO_HARD_FAIL", f"STD_IS_OPTIMAL: " + info)
    return ("ACO_MIDDLE_BAND", f"MIXED: " + info)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Cleanup formula self-tests on tiny synthetic data
    device = torch.device("cpu")
    Ntest = 8
    cb = torch.eye(8)                              # 8 codewords
    W = torch.eye(8) * 8.0
    k = cb[0:2]                                    # 2 probe keys
    # alpha=1.0 -> output should equal cand (top codeword)
    out = cleanup(W, k, cb, 1.0, Ntest)
    raw = k @ W.T
    sims = (cb @ raw.T) / Ntest
    top = cb[torch.argmax(sims, dim=0)]
    assert torch.allclose(out, top, atol=1e-5), f"alpha=1 should give cand; out={out}"
    # alpha=0.0 -> output should equal raw
    out0 = cleanup(W, k, cb, 0.0, Ntest)
    assert torch.allclose(out0, raw, atol=1e-5), f"alpha=0 should give raw"

    # Verdict gates
    fake_hp = [
        {"seed": s, "best_alpha": 0.5, "retention_at_1p0": 0.7,
         "retention_at_best": 0.85} for s in [7, 17, 23]
    ] + [
        {"seed": s, "best_alpha": 1.0, "retention_at_1p0": 0.9,
         "retention_at_best": 0.9} for s in [31, 41]
    ]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    fake_hf = [
        {"seed": s, "best_alpha": 1.0, "retention_at_1p0": 0.9,
         "retention_at_best": 0.9} for s in [7, 17, 23, 31]
    ] + [
        {"seed": 41, "best_alpha": 0.5, "retention_at_1p0": 0.9,
         "retention_at_best": 0.92}
    ]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Smoke: measure_retention_at_alpha at small N
    acc = measure_retention_at_alpha(N_SMOKE, 256, 17, 1.0, device)
    assert 0.0 <= acc <= 1.0, f"retention out of range: {acc}"
    print(f"[selftest] adaptive_cleanup_operator_v1_n4096 PASS "
          f"smoke alpha=1.0 ret={acc:.3f}", flush=True)


_instrumentation_selftest()


def get_output_dir(default_name: str = "adaptive_cleanup_operator_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = max(1, int(M_FRAC * N_cfg))
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    alphas = ALPHA_SWEEP

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] adaptive_cleanup smoke={smoke} N={N_cfg} M={M} alphas={alphas} "
          f"seeds={seeds} done={len(done)} device={device_str}", flush=True)

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body); continue
        rets = []
        for a in alphas:
            try:
                acc = measure_retention_at_alpha(N_cfg, M, seed, a, device)
                rets.append(round(acc, 5))
                print(f"  seed={seed} alpha={a:g} ret={acc:.4f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  seed={seed} alpha={a:g} FAILED: {e}", flush=True)
                rets.append(0.0)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()
        best_idx = max(range(len(rets)), key=lambda i: rets[i])
        body = {"seed": seed, "M": M, "alphas": alphas,
                "retentions": rets,
                "best_alpha": float(alphas[best_idx]),
                "retention_at_best": rets[best_idx],
                "retention_at_1p0": rets[alphas.index(1.0)]
                                       if 1.0 in alphas else 0.0}
        write_partial_key(out_dir, ck, body)
        per_seed.append(body)

    verdict, vm = compute_verdict(per_seed)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adaptive_cleanup_operator_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M, "alphas": alphas, "seeds": seeds,
               "per_seed": per_seed,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
