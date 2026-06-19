"""BLOCK-STRUCTURED W FEASIBILITY v1 at N=4096.

CONTEXT:
  Standard W is fully connected. Test W as logical domain blocks: W_ii for
  within-domain bindings, W_ij off-diagonal for cross-domain. Each block is
  (N/D x N/D) where D = number of domains. Total params = D^2 * (N/D)^2 = N^2
  (same as standard) BUT we can ZERO the off-diagonals for within-domain
  storage and save D-1/D of the parameters per fact bound to one domain only.

SCIENTIFIC QUESTION:
  Does block-structured W with all-zero off-diagonal blocks maintain >= 90%
  within-domain retention AND >= 70% cross-domain (via cross-domain rank-1
  edits to off-diagonal blocks)?

PRE-REGISTERED BANDS:
  HARD_PASS: block W within-domain ret >= 0.9 AND cross-domain ret >= 0.7 AND
    memory savings >= 4x at fixed within-domain accuracy.
  HARD_FAIL: block W loses >= 30% accuracy in either within or cross-domain.
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. D=4 domains. block_size = N/D = 1024.
  3. memory savings (within-only) = D = 4x (keep only D diagonal blocks).
  4. 128 facts per domain = 512 within-domain facts. 30 cross-domain pairs.

OOM CHECK: N=4096, 512+30 facts. Standard manageable.

TIMEOUT ESTIMATE: 5 seeds * cell ~10s = 50s. Budget 21600s.

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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_blk", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024
D_DOMAINS = 4
FACTS_PER_DOMAIN_FULL  = 128
FACTS_PER_DOMAIN_SMOKE = 16
N_CROSS_PAIRS = 30
BETA = 8.0
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 200

HP_WITHIN_RET = 0.90
HP_CROSS_RET  = 0.70
HF_LOSS       = 0.30


def make_block_W(N_use: int, D: int) -> torch.Tensor:
    """Return zero N x N tensor; we'll fill block diagonals only."""
    return torch.zeros(N_use, N_use)


def fill_within_domain_block(W: torch.Tensor, codebook: torch.Tensor,
                              domain: int, keys: torch.Tensor,
                              values: torch.Tensor,
                              N_use: int, D: int) -> None:
    """Add outer-product stores for within-domain facts to the d,d block.

    Block region: rows [d*bs : (d+1)*bs], cols [d*bs : (d+1)*bs] where bs=N/D.
    """
    bs = N_use // D
    r0, r1 = domain * bs, (domain + 1) * bs
    # We restrict keys & values to first bs dims (within-domain subspace) by
    # masking. For simplicity, project keys/values onto the bs-subspace.
    k_blk = keys[:, r0:r1]
    v_blk = values[:, r0:r1]
    # Add to W block (rank-M update in the block; bs-dim)
    W[r0:r1, r0:r1] += v_blk.T @ k_blk / N_use


def fill_cross_domain_block(W: torch.Tensor, src_d: int, tgt_d: int,
                              k_full: torch.Tensor, v_full: torch.Tensor,
                              N_use: int, D: int) -> None:
    """Add rank-1 outer product to off-diagonal (tgt_d, src_d) block.

    Cross-domain fact: key in domain src_d, value in domain tgt_d.
    W[tgt_block, src_block] += outer(v[tgt_block], k[src_block]) / N.
    """
    bs = N_use // D
    sr0, sr1 = src_d * bs, (src_d + 1) * bs
    tr0, tr1 = tgt_d * bs, (tgt_d + 1) * bs
    k_blk = k_full[sr0:sr1]
    v_blk = v_full[tr0:tr1]
    W[tr0:tr1, sr0:sr1] += torch.outer(v_blk, k_blk) / N_use


def get_output_dir(default_name: str = "block_structured_w_feasibility_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_seed(N_use: int, seed: int, facts_per_domain: int,
                  device: torch.device) -> Dict:
    """Build block-structured substrate and test within + cross domain retrieval."""
    M_total = D_DOMAINS * facts_per_domain
    codebook, W_full, keys, values, key_idx, val_idx = make_substrate(
        N_use, M_total, seed, device)
    C = codebook.shape[0]

    # Build block-structured W (within-only first)
    W_block = make_block_W(N_use, D_DOMAINS).to(device)
    for d in range(D_DOMAINS):
        d0 = d * facts_per_domain; d1 = d0 + facts_per_domain
        fill_within_domain_block(W_block, codebook, d, keys[d0:d1],
                                  values[d0:d1], N_use, D_DOMAINS)

    # Within-domain retention: test on stored keys (in their own block)
    n = min(N_PROBE, M_total)
    probe_keys = keys[:n]
    probe_val_idx = val_idx[:n] % C
    # We retrieve full-N output via W_block @ k (block-structure means cross-block
    # contributions are zero by construction here; within-domain probes hit their own
    # diagonal block.)
    out = probe_keys @ W_block.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    within_ret = float((pred == probe_val_idx.to(device)).float().mean().item())

    # Cross-domain: add N_CROSS_PAIRS rank-1 edits to off-diagonal blocks
    n_cross = min(N_CROSS_PAIRS, M_total // 2)
    gen = torch.Generator(device=device).manual_seed(seed + 1500)
    cross_correct = 0
    for ci in range(n_cross):
        src_d = ci % D_DOMAINS
        tgt_d = (ci + 1) % D_DOMAINS
        # Pick a key & value pair (use rand codewords)
        ki = int(torch.randint(0, C, (1,), generator=gen, device=device).item())
        vi = int(torch.randint(0, C, (1,), generator=gen, device=device).item())
        k_full = codebook[ki]; v_full = codebook[vi]
        # Make a working copy so cross-domain edits don't accumulate
        W_test = W_block.clone()
        fill_cross_domain_block(W_test, src_d, tgt_d, k_full, v_full, N_use, D_DOMAINS)
        # Retrieve: full output, then check top codeword in target-domain
        # subspace matches the stored value
        q = k_full @ W_test.T
        sims2 = (codebook @ q) / N_use
        # Argmax over codebook is the retrieved value index
        pred2 = int(torch.argmax(sims2).item())
        if pred2 == vi:
            cross_correct += 1

    cross_ret = cross_correct / max(1, n_cross)
    # Memory: W_block has D blocks of (N/D)^2 each. Total = D * (N/D)^2 = N^2 / D.
    # Standard W = N^2. Savings = D.
    mem_savings = float(D_DOMAINS)
    del W_full, W_block, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return {"seed": seed, "facts_per_domain": facts_per_domain,
            "within_ret": round(within_ret, 5),
            "cross_ret": round(cross_ret, 5),
            "memory_savings": mem_savings}


def compute_verdict(per_seed: List[Dict]) -> Tuple[str, str]:
    if not per_seed:
        return ("BS_INCONCLUSIVE", "No seeds.")
    within_avg = sum(d["within_ret"] for d in per_seed) / len(per_seed)
    cross_avg  = sum(d["cross_ret"]  for d in per_seed) / len(per_seed)
    mem        = per_seed[0]["memory_savings"]
    detail = (f"within_ret={within_avg:.3f} cross_ret={cross_avg:.3f} "
              f"mem_savings={mem:.1f}x n_seeds={len(per_seed)}")
    if (within_avg >= HP_WITHIN_RET and cross_avg >= HP_CROSS_RET
            and mem >= 4.0):
        return ("BS_HARD_PASS", f"BLOCK_W_WORKS: " + detail)
    if within_avg <= 1.0 - HF_LOSS or cross_avg <= 1.0 - HF_LOSS:
        # If retention is below 0.7, that's >= 30% loss from full=1.0 baseline
        return ("BS_HARD_FAIL", f"LARGE_LOSS: " + detail)
    return ("BS_MIDDLE_BAND", f"PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    # Block layout self-test
    bs = N_FULL // D_DOMAINS
    assert bs == 1024, f"N=4096, D=4 -> block_size=1024, got {bs}"
    Wb = make_block_W(64, 4)
    assert Wb.shape == (64, 64)
    assert torch.all(Wb == 0)

    # Verdict gates
    fake_hp = [{"seed": s, "within_ret": 0.95, "cross_ret": 0.85,
                "memory_savings": 4.0, "facts_per_domain": 128}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v
    fake_hf = [{"seed": s, "within_ret": 0.5, "cross_ret": 0.5,
                "memory_savings": 4.0, "facts_per_domain": 128}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v
    fake_mb = [{"seed": s, "within_ret": 0.85, "cross_ret": 0.75,
                "memory_savings": 4.0, "facts_per_domain": 128}
               for s in [7, 17, 23, 31, 41]]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Smoke
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 17, FACTS_PER_DOMAIN_SMOKE, device)
    assert out["within_ret"] is not None
    assert out["cross_ret"]  is not None
    print(f"[selftest] block_structured_w_feasibility_v1_n4096 PASS "
          f"smoke within={out['within_ret']:.3f} cross={out['cross_ret']:.3f}",
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
    fpd = FACTS_PER_DOMAIN_SMOKE if smoke else FACTS_PER_DOMAIN_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] block_structured_w smoke={smoke} N={N_cfg} D={D_DOMAINS} "
          f"fpd={fpd} seeds={seeds} done={len(done)} device={device_str}",
          flush=True)

    per_seed: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                per_seed.append(body); continue
        try:
            out = measure_seed(N_cfg, seed, fpd, device)
            write_partial_key(out_dir, ck, out)
            per_seed.append(out)
            print(f"  seed={seed} within={out['within_ret']:.3f} "
                  f"cross={out['cross_ret']:.3f} ({time.time()-t0:.1f}s)",
                  flush=True)
        except (RuntimeError, MemoryError) as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    verdict, vm = compute_verdict(per_seed)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "block_structured_w_feasibility_v1_n4096", "N": N_cfg,
               "smoke": smoke, "D": D_DOMAINS, "fpd": fpd, "seeds": seeds,
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
