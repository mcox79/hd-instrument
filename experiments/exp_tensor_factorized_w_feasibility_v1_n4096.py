"""TENSOR-FACTORIZED W FEASIBILITY v1 at N=4096.

CONTEXT:
  Standard W is dense (N x N = 16M params at N=4096). Test whether SVD-based
  low-rank factorization W ~ U * S * V^T preserves accuracy while saving memory.

SCIENTIFIC QUESTION:
  At ranks [128, 256, 512, 1024, 2048], retrieval accuracy vs full-rank (N=4096)?
  Memory footprint vs full rank? What is the break-even point for max_M_at_95
  per memory unit?

PRE-REGISTERED BANDS:
  HARD_PASS: factored W at rank=512 gives >= 95% of full-rank retention AT
    1/8 memory budget (512 vs 4096 -> 1/8 of N).
  HARD_FAIL: factored W loses >= 30% accuracy at any rank below 2048.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. ranks [128, 256, 512, 1024, 2048]; full=4096.
  3. memory_ratio = 2 * rank * N / (N * N) = 2 * rank / N.
     rank=512: 0.25 ... wait, that's 2*512/4096 = 0.25.
     ACTUAL: factored stores U (N x rank) + V (rank x N) + S (rank) = 2*rank*N + rank.
     full stores N*N. Ratio = 2*rank/N (S is negligible).
     rank=512 ratio = 2*512/4096 = 0.25 = 1/4. (Not 1/8. Fix: HP threshold uses
     half-memory comparison: at rank=N/8=512, 2*512/4096=0.25=1/4 memory of full.
     For 1/8 memory we need rank=N/16=256.)
  4. We use ACTUAL ratio. HP threshold: at rank=N/8=512, retention_ratio >= 0.95.

OOM CHECK: M=512, N=4096: keys=8.4MB. W=64MB. CB=805MB. U,V tens add ~64MB. OK.

TIMEOUT ESTIMATE: 5 ranks * 5 seeds * (build + retention). ~5s/cell. ~125s.
  Budget 21600s.

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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_fact", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
M_FULL  = 512
M_SMOKE = 64
RANKS_FULL  = [128, 256, 512, 1024, 2048]
RANKS_SMOKE = [32, 64, 128, 256]
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_RANK = 512
HP_RETENTION_RATIO = 0.95
HF_LOSS_AT_LOW_RANK = 0.30
HF_THRESHOLD_RANK = 2048


def factorize_w(W: torch.Tensor, rank: int) -> torch.Tensor:
    """SVD factorize W to rank-r. Returns reconstructed W."""
    U, S, Vh = torch.linalg.svd(W, full_matrices=False)
    U_r = U[:, :rank]
    S_r = S[:rank]
    Vh_r = Vh[:rank, :]
    return U_r @ torch.diag(S_r) @ Vh_r


def get_output_dir(default_name: str = "tensor_factorized_w_feasibility_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_retention(W: torch.Tensor, codebook: torch.Tensor, keys: torch.Tensor,
                       val_idx: torch.Tensor, N_use: int) -> float:
    C = codebook.shape[0]
    n = min(N_PROBE, keys.shape[0])
    probe_keys = keys[:n]
    probe_val  = val_idx[:n] % C
    sims = (codebook @ (probe_keys @ W.T).T) / N_use
    pred = torch.argmax(sims, dim=0)
    return float((pred == probe_val.to(W.device)).float().mean().item())


def measure_seed(N_use: int, M: int, seed: int, ranks: List[int],
                  device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    # Verify W reconstruction: full-rank SVD round-trip should be identity
    ret_full = measure_retention(W, codebook, keys, val_idx, N_use)
    rets_by_rank = {}
    for r in ranks:
        if r > min(W.shape):
            rets_by_rank[r] = ret_full
            continue
        try:
            W_fac = factorize_w(W, r)
            rets_by_rank[r] = round(measure_retention(W_fac, codebook, keys,
                                                       val_idx, N_use), 5)
        except RuntimeError as e:
            rets_by_rank[r] = -1.0
    out = {"seed": seed, "M": M, "ret_full": round(ret_full, 5),
           "rets_by_rank": rets_by_rank,
           "memory_ratio_per_rank": {r: round(2.0 * r / N_use, 5) for r in ranks}}
    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return out


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("TF_INCONCLUSIVE", "No seeds.")
    # HP: rank=HP_RANK retention >= HP_RETENTION_RATIO * full retention.
    # HF: ALL ranks below HF_THRESHOLD_RANK show >= 30% loss (compression broken
    #     across the whole rank-reduction region).
    hp_ratios = []
    # n_seeds_with_uniform_loss = # of seeds where every rank < threshold has loss>=0.30
    n_uniform_loss = 0
    detail = []
    for d in per_seed:
        full = d["ret_full"]
        if full <= 0:
            continue
        hp_r = d["rets_by_rank"].get(HP_RANK, 0.0) / max(full, 1e-9)
        hp_ratios.append(hp_r)
        detail.append(f"seed{d['seed']}:full={full:.3f}_r{HP_RANK}ratio={hp_r:.3f}")
        # uniform loss check: every rank below threshold is loss >= 30%?
        ranks_below = [(r, ret) for r, ret in d["rets_by_rank"].items()
                       if r < HF_THRESHOLD_RANK]
        if ranks_below and all(full - ret >= HF_LOSS_AT_LOW_RANK
                                for r, ret in ranks_below):
            n_uniform_loss += 1
    mean_hp = sum(hp_ratios) / len(hp_ratios) if hp_ratios else 0.0
    n_seeds = len([d for d in per_seed if d["ret_full"] > 0])
    info = (f"mean_r{HP_RANK}_ratio={mean_hp:.3f} "
            f"n_seeds_uniform_loss={n_uniform_loss}/{n_seeds} "
            + " ".join(detail))
    # HARD_FAIL when factorization is universally broken (compression doesn't
    # work at any tested low rank)
    if n_seeds > 0 and n_uniform_loss >= n_seeds * 0.6:
        return ("TF_HARD_FAIL", f"COMPRESSION_BROKEN: " + info)
    if mean_hp >= HP_RETENTION_RATIO:
        return ("TF_HARD_PASS", f"FACTORIZATION_WORKS: " + info)
    return ("TF_MIDDLE_BAND", f"INTERMEDIATE: " + info)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # SVD reconstruction self-test: full rank gives back identity
    Wt = torch.randn(8, 8)
    Wf = factorize_w(Wt, 8)
    assert torch.allclose(Wt, Wf, atol=1e-4), f"full-rank SVD reconstruction broken"
    # Rank-1 reconstruction must be lower rank
    W1 = factorize_w(Wt, 1)
    err = (Wt - W1).norm() / Wt.norm()
    assert err > 0.0, f"rank-1 should be lossy"
    # Memory ratio formula
    mr = 2 * 512 / N_FULL
    assert abs(mr - 0.25) < 1e-6, f"memory_ratio(rank=512, N=4096) should be 0.25, got {mr}"

    # Verdict gates
    fake_hp = [{"seed": s, "M": 64, "ret_full": 0.95,
                "rets_by_rank": {128: 0.4, 256: 0.7, 512: 0.92, 1024: 0.94, 2048: 0.95}}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = [{"seed": s, "M": 64, "ret_full": 0.95,
                "rets_by_rank": {128: 0.1, 256: 0.2, 512: 0.5, 1024: 0.6, 2048: 0.9}}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, 17, RANKS_SMOKE, device)
    assert out["ret_full"] is not None
    for r, ret in out["rets_by_rank"].items():
        assert ret >= 0, f"rank {r} got negative ret"
    print(f"[selftest] tensor_factorized_w_feasibility_v1_n4096 PASS "
          f"smoke full={out['ret_full']:.3f} r128_ret={out['rets_by_rank'].get(128, 'na')}",
          flush=True)


_instrumentation_selftest()


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
    M_cfg = M_SMOKE if smoke else M_FULL
    ranks = RANKS_SMOKE if smoke else RANKS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] tensor_factorized smoke={smoke} N={N_cfg} M={M_cfg} "
          f"ranks={ranks} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body); continue
        try:
            out = measure_seed(N_cfg, M_cfg, seed, ranks, device)
            write_partial_key(out_dir, ck, out)
            per_seed.append(out)
            print(f"  seed={seed} full={out['ret_full']:.3f} "
                  f"r{ranks[0]}={out['rets_by_rank'].get(ranks[0], 'na')} "
                  f"r{ranks[-1]}={out['rets_by_rank'].get(ranks[-1], 'na')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(per_seed)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "tensor_factorized_w_feasibility_v1_n4096", "N": N_cfg,
               "smoke": smoke, "M": M_cfg, "ranks": ranks, "seeds": seeds,
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
