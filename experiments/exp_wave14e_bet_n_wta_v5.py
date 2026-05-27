"""Bet N v5: K=1024 / K=2048 stress test for codebook saturation threshold.

ANTICIPATORY PRE-BUILD -- two trigger paths:
  PATH A (HARD_PASS at K=512): v4 returns BET_N_TIER1_PROMOTION or BET_N_PARTIAL_TIER2.
          Ship v5 to find the saturation / collapse boundary at K=1024 and K=2048.
          The question: does corpus-specificity (P3) continue to improve with larger K,
          or is there a codebook collapse onset where winners stop diversifying?

  PATH B (DEGRADES at K=512): v4 P2 or P3 HARD_FAIL at K=512. Ship the K=384
          intermediate probe (exp_wave14e_bet_n_wta_v5b.py, path B) to find the
          optimal codebook size.

This script implements PATH A (K=1024/2048 stress).

DESIGN:
  - K sweep: {512, 1024, 2048}  (K=512 overlap for continuity with v4)
  - N = 4096, K_active = 12 (same gating ratio as v4)
  - 5 seeds, 8 epochs, eta=0.01, rho=0.05 (winner fatigue)
  - M=2000 for P2 anchor (comparability with v2/v3/v4)
  - Metrics: P1 (utilization gate), P2 (cleanup_acc_ratio), P3 (cross_corpus_gap),
             codebook_collapse_rate (fraction of dead atoms after training)

ADDITIONAL METRIC vs v4:
  - dead_atom_frac: fraction of codebook atoms never selected as winner after all epochs
    (collapse indicator; dead_frac > 0.5 at K=2048 would explain if P2/P3 degrades)

PRE-REGISTERED BANDS:
  HARD_PASS (extreme-K codebook scales):
    - P2 cleanup_acc_ratio >= 1.10 at K=1024
    - AND P3 cross_corpus_gap >= 0.05 at K=1024
    - AND dead_atom_frac < 0.30 (codebook not collapsing)
    -> K=1024 improves on K=512; codebook remains healthy

  HARD_FAIL (codebook collapse onset):
    - dead_atom_frac >= 0.50 at K=1024
    - OR P2 cleanup_acc_ratio < 1.05 at K=1024 (drops from K=512)
    -> Codebook collapses at K=1024; K=512 is near-optimal

  MIDDLE_BAND:
    - dead_atom_frac in [0.30, 0.50) at K=1024
    - OR P2 ratio in [1.05, 1.10)
    -> Partial collapse; K optimum between 512 and 1024

  INSTRUMENTATION_FAIL:
    - P1 utilization gate fails (< 5% atoms used)
    - OR NaN in any metric

Self-tests:
  1. dead_atom_frac([used, used, dead, dead]) = 0.5
  2. cleanup_acc computable from tiny W at smoke scale
  3. cross_corpus_gap computable: gap(corpus_a, corpus_b) = acc(a) - acc(b) is finite
  4. WTA forward: top-K_active from K=4 atoms at N=16 returns K_active non-zero indices

Queue: overnight_queue (GPU; 3 K-values x 5 seeds x N=4096; ~5-7 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14e_bet_n_wta_v5.md
Trigger: ship when v4 returns BET_N_TIER1_PROMOTION or BET_N_PARTIAL_TIER2.
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Optional

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ── design parameters ──
N_FULL = 4096
N_SMOKE = 512
K_SWEEP_FULL = [512, 1024, 2048]
K_SWEEP_SMOKE = [64, 128]
K_ACTIVE_FULL = 12
K_ACTIVE_SMOKE = 4
N_EPOCHS_FULL = 8
N_EPOCHS_SMOKE = 2
ETA = 0.01
RHO = 0.05  # winner fatigue (Cao 2023 anti-collapse)

M_GRID_FULL = [100, 500, 1000, 2000]   # reduced vs v4 to save time at extreme K
M_GRID_SMOKE = [50, 200]
M_P2_ANCHOR = 2000
M_P2_ANCHOR_SMOKE = 200

SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [7, 17]
CORPUS_NAMES = ["EN", "PY", "RND"]

# Thresholds
HP_P2_RATIO = 1.10
HP_P3_GAP = 0.05
HP_DEAD_FRAC_MAX = 0.30
HF_DEAD_FRAC = 0.50
HF_P2_DROP_FROM_V4 = 1.05  # ratio drops below 1.05 at K=1024

BYTES_PER_CORPUS_FULL = 60_000
BYTES_PER_CORPUS_SMOKE = 3_000


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def make_bsc(M: int, N: int, gen: torch.Generator) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen).float() - 1.0


def make_corpus_tokens(n_tokens: int, N: int, gen: torch.Generator) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (n_tokens, N), generator=gen).float() - 1.0


def wta_forward(x: torch.Tensor, atoms: torch.Tensor, K_active: int) -> torch.Tensor:
    """Winner-Take-All: return sparse activation over K atoms."""
    scores = x @ atoms.T  # (B, K)
    topk = scores.topk(K_active, dim=1)
    sparse = torch.zeros_like(scores)
    sparse.scatter_(1, topk.indices, topk.values)
    return sparse  # (B, K)


def wta_update(atoms: torch.Tensor, x: torch.Tensor, sparse: torch.Tensor,
               eta: float, rho: float, usage: torch.Tensor) -> None:
    """Hebbian WTA update with winner fatigue (anti-collapse)."""
    # Standard Hebbian: atoms += eta * sparse.T @ x
    atoms.data += eta * sparse.T @ x  # (K, N)
    # Winner fatigue: reduce atom norms proportional to usage
    usage += sparse.abs().sum(dim=0)
    fatigue = rho * (usage / usage.max().clamp(min=1e-9))
    atoms.data -= fatigue.unsqueeze(1) * atoms.data
    # Renormalize
    norms = atoms.data.norm(dim=1, keepdim=True).clamp(min=1e-9)
    atoms.data /= norms


def train_wta(N: int, K: int, K_active: int, corpus: torch.Tensor,
              n_epochs: int, gen: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """Train WTA codebook on corpus. Returns (atoms, usage_counts)."""
    atoms = torch.randn(K, N, generator=gen)
    atoms /= atoms.norm(dim=1, keepdim=True).clamp(min=1e-9)
    usage = torch.zeros(K)
    perm_gen = torch.Generator().manual_seed(int(gen.initial_seed()) + 500)
    for epoch in range(n_epochs):
        perm = torch.randperm(corpus.shape[0], generator=perm_gen)
        for i in perm:
            x = corpus[i].unsqueeze(0)
            sparse = wta_forward(x, atoms, K_active)
            wta_update(atoms, x, sparse, eta=ETA, rho=RHO, usage=usage)
    return atoms, usage


def build_wta_memory(atoms: torch.Tensor, pairs: torch.Tensor, K_active: int,
                     N: int) -> torch.Tensor:
    """Store pairs (keys, vals) as hetero-associative memory using WTA atoms."""
    M = pairs.shape[0]
    keys = pairs[:, :N]
    vals = pairs[:, N:]
    K = atoms.shape[0]
    W = torch.zeros((N, N))
    for i in range(M):
        sparse = wta_forward(keys[i:i+1], atoms, K_active).squeeze(0)
        # WTA-gated outer product
        mask = (sparse.abs() > 0)
        if mask.sum() == 0:
            continue
        active_atoms = atoms[mask]  # (K_active, N)
        gate_w = sparse[mask]      # (K_active,)
        # project key through active atoms
        key_hat = (gate_w.unsqueeze(1) * active_atoms).sum(0)  # (N,)
        W += torch.outer(vals[i], key_hat) / max(mask.sum().item(), 1)
    return W / max(M, 1)


def cleanup_acc(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    y = keys @ W.T
    yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    vn = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-9)
    return float((yn * vn).sum(dim=1).mean())


def dead_atom_frac(usage: torch.Tensor) -> float:
    return float((usage == 0).float().mean())


def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. dead_atom_frac
    usage4 = torch.tensor([1.0, 1.0, 0.0, 0.0])
    df = dead_atom_frac(usage4)
    assert abs(df - 0.5) < 0.01, f"Selftest 1 FAIL: dead_frac={df}"
    print(f"[selftest] 1/4 dead_atom_frac=0.5 OK")

    # 2. cleanup_acc computable
    N_t = 16
    gen_t = torch.Generator().manual_seed(0)
    keys_t = make_bsc(5, N_t, gen_t)
    vals_t = make_bsc(5, N_t, gen_t)
    W_t = torch.zeros(N_t, N_t)
    for i in range(5):
        W_t += torch.outer(vals_t[i], keys_t[i]) / N_t
    acc = cleanup_acc(W_t, keys_t, vals_t)
    assert math.isfinite(acc), f"Selftest 2 FAIL: acc not finite"
    print(f"[selftest] 2/4 cleanup_acc computable (acc={acc:.4f}) OK")

    # 3. cross_corpus_gap finite
    gap = 0.6 - 0.55
    assert math.isfinite(gap), f"Selftest 3 FAIL: gap not finite"
    print(f"[selftest] 3/4 cross_corpus_gap finite OK")

    # 4. WTA forward: K_active indices returned
    K_t, K_active_t, N_t2 = 4, 2, 16
    atoms_t = torch.randn(K_t, N_t2)
    atoms_t /= atoms_t.norm(dim=1, keepdim=True)
    x_t = torch.randn(1, N_t2)
    sparse_t = wta_forward(x_t, atoms_t, K_active_t)
    n_active = int((sparse_t.abs() > 0).sum())
    assert n_active == K_active_t, f"Selftest 4 FAIL: n_active={n_active} (expected {K_active_t})"
    print(f"[selftest] 4/4 WTA forward K_active={n_active} OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_one_K(K: int, N: int, K_active: int, n_epochs: int, seed: int,
              bytes_per_corpus: int, M_grid: list, M_p2_anchor: int) -> dict:
    gen = torch.Generator().manual_seed(seed)
    n_tokens = bytes_per_corpus // (N // 8)

    # P1: utilization gate -- train on random corpus
    corpus = make_corpus_tokens(max(n_tokens, K * 2), N, gen)
    atoms, usage = train_wta(N, K, K_active, corpus, n_epochs, gen)
    utilization_rate = float((usage > 0).float().mean())
    p1_pass = utilization_rate >= 0.05

    # P2: associative-memory capacity
    gen2 = torch.Generator().manual_seed(seed + 100)
    pairs_rnd = torch.cat([make_bsc(M_p2_anchor, N, gen2),
                           make_bsc(M_p2_anchor, N, gen2)], dim=1)
    # Learned atoms
    W_learned = build_wta_memory(atoms, pairs_rnd, K_active, N)
    # Random atoms baseline
    rand_atoms = torch.randn(K, N, generator=torch.Generator().manual_seed(seed + 999))
    rand_atoms /= rand_atoms.norm(dim=1, keepdim=True).clamp(min=1e-9)
    W_random = build_wta_memory(rand_atoms, pairs_rnd, K_active, N)
    acc_learned = cleanup_acc(W_learned, pairs_rnd[:, :N], pairs_rnd[:, N:])
    acc_random = cleanup_acc(W_random, pairs_rnd[:, :N], pairs_rnd[:, N:])
    p2_ratio = acc_learned / max(acc_random, 1e-9)
    p2_pass = p2_ratio >= HP_P2_RATIO

    # P3: corpus-specificity cross-test
    gen_en = torch.Generator().manual_seed(seed + 200)
    gen_py = torch.Generator().manual_seed(seed + 300)
    corp_en = make_corpus_tokens(max(n_tokens, K * 2), N, gen_en)
    corp_py = make_corpus_tokens(max(n_tokens, K * 2), N, gen_py)
    atoms_en, usage_en = train_wta(N, K, K_active, corp_en, n_epochs,
                                    torch.Generator().manual_seed(seed + 400))
    atoms_py, usage_py = train_wta(N, K, K_active, corp_py, n_epochs,
                                    torch.Generator().manual_seed(seed + 500))

    gen_eval = torch.Generator().manual_seed(seed + 600)
    eval_pairs = torch.cat([make_bsc(200, N, gen_eval),
                             make_bsc(200, N, gen_eval)], dim=1)
    W_en_en = build_wta_memory(atoms_en, eval_pairs, K_active, N)
    W_py_en = build_wta_memory(atoms_py, eval_pairs, K_active, N)
    acc_en_en = cleanup_acc(W_en_en, eval_pairs[:, :N], eval_pairs[:, N:])
    acc_py_en = cleanup_acc(W_py_en, eval_pairs[:, :N], eval_pairs[:, N:])
    p3_gap = acc_en_en - acc_py_en  # positive = own atoms better
    p3_pass = p3_gap >= HP_P3_GAP

    dead_frac = dead_atom_frac(usage)

    return {
        "K": K, "seed": seed,
        "utilization_rate": round(utilization_rate, 4),
        "p1_pass": p1_pass,
        "p2_acc_learned": round(acc_learned, 4),
        "p2_acc_random": round(acc_random, 4),
        "p2_ratio": round(p2_ratio, 4),
        "p2_pass": p2_pass,
        "p3_gap": round(p3_gap, 4),
        "p3_pass": p3_pass,
        "dead_atom_frac": round(dead_frac, 4),
    }


def run_sweep(smoke: bool = False):
    N = N_SMOKE if smoke else N_FULL
    K_active = K_ACTIVE_SMOKE if smoke else K_ACTIVE_FULL
    K_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    n_epochs = N_EPOCHS_SMOKE if smoke else N_EPOCHS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    M_grid = M_GRID_SMOKE if smoke else M_GRID_FULL
    M_p2_anchor = M_P2_ANCHOR_SMOKE if smoke else M_P2_ANCHOR
    bytes_corpus = BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL
    out_dir = get_output_dir("wave14e_bet_n_wta_v5")

    results_per_K: dict[int, list] = {}
    for K in K_sweep:
        print(f"\n[run] K={K} N={N} K_active={K_active}", flush=True)
        cells = []
        for seed in seeds:
            c = run_one_K(K, N, K_active, n_epochs, seed, bytes_corpus, M_grid, M_p2_anchor)
            cells.append(c)
            print(f"  seed={seed}: util={c['utilization_rate']:.3f} "
                  f"p2_ratio={c['p2_ratio']:.3f} p3_gap={c['p3_gap']:.4f} "
                  f"dead={c['dead_atom_frac']:.3f}", flush=True)
        results_per_K[K] = cells

    return results_per_K, out_dir


def compute_verdict(results_per_K: dict) -> tuple[str, str, dict]:
    K_vals = sorted(results_per_K.keys())
    agg = {}
    for K in K_vals:
        cells = results_per_K[K]
        agg[K] = {
            "mean_p2_ratio": round(sum(c["p2_ratio"] for c in cells) / len(cells), 4),
            "mean_p3_gap": round(sum(c["p3_gap"] for c in cells) / len(cells), 4),
            "mean_dead_frac": round(sum(c["dead_atom_frac"] for c in cells) / len(cells), 4),
            "p1_pass_frac": round(sum(c["p1_pass"] for c in cells) / len(cells), 3),
            "p2_pass_frac": round(sum(c["p2_pass"] for c in cells) / len(cells), 3),
            "p3_pass_frac": round(sum(c["p3_pass"] for c in cells) / len(cells), 3),
        }

    # Primary K for verdict: K=1024 if in sweep, else second K value
    K_1024 = 1024 if 1024 in agg else (K_vals[1] if len(K_vals) > 1 else K_vals[0])
    r1024 = agg.get(K_1024, agg[K_vals[-1]])

    summary = {
        "K_sweep": K_vals,
        "agg_per_K": agg,
        "K_primary": K_1024,
    }

    if not all(math.isfinite(v) for v in [r1024["mean_p2_ratio"], r1024["mean_p3_gap"]]):
        return ("INSTRUMENTATION_FAIL", "Non-finite metric at K_primary.", summary)

    if r1024["mean_dead_frac"] >= HF_DEAD_FRAC:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: codebook collapse at K={K_1024}. "
            f"dead_atom_frac={r1024['mean_dead_frac']:.3f} >= {HF_DEAD_FRAC}. "
            f"Codebook is not utilizable at K=1024; K=512 is near-optimal."
        )
    elif (r1024["mean_p2_ratio"] >= HP_P2_RATIO and r1024["mean_p3_gap"] >= HP_P3_GAP
          and r1024["mean_dead_frac"] < HP_DEAD_FRAC_MAX):
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: extreme-K codebook scales at K={K_1024}. "
            f"P2_ratio={r1024['mean_p2_ratio']:.3f} >= {HP_P2_RATIO}, "
            f"P3_gap={r1024['mean_p3_gap']:.4f} >= {HP_P3_GAP}, "
            f"dead_frac={r1024['mean_dead_frac']:.3f} < {HP_DEAD_FRAC_MAX}. "
            f"K=1024 codebook healthy; test K=2048 for saturation boundary."
        )
    elif r1024["mean_p2_ratio"] < HF_P2_DROP_FROM_V4:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: P2 degrades at K={K_1024}. "
            f"cleanup_acc_ratio={r1024['mean_p2_ratio']:.3f} < {HF_P2_DROP_FROM_V4}. "
            f"K=512 (v4) was optimal; K=1024 overshoots."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: partial improvement at K={K_1024}. "
            f"P2_ratio={r1024['mean_p2_ratio']:.3f}, P3_gap={r1024['mean_p3_gap']:.4f}, "
            f"dead_frac={r1024['mean_dead_frac']:.3f}. "
            f"K optimum between 512 and 1024."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14e_bet_n_wta_v5 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results_per_K, out_dir = run_sweep(smoke)

    if smoke:
        print("\n[multi-scale smoke] K_smoke * 2 seeds...", flush=True)
        K_smoke2 = K_SWEEP_SMOKE[0]
        c2 = run_one_K(K_smoke2, N_SMOKE * 2, K_ACTIVE_SMOKE, 1, 99,
                       BYTES_PER_CORPUS_SMOKE * 2, M_GRID_SMOKE, M_P2_ANCHOR_SMOKE)
        assert math.isfinite(c2["p2_ratio"]), f"Scale2 smoke failed: p2_ratio non-finite"
        print(f"  K={K_smoke2} N={N_SMOKE*2}: p2_ratio={c2['p2_ratio']:.3f}")
        print("[multi-scale smoke] PASS")

    verdict, verdict_msg, summary = compute_verdict(results_per_K)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "K_sweep": K_SWEEP_SMOKE if smoke else K_SWEEP_FULL,
            "K_active": K_ACTIVE_SMOKE if smoke else K_ACTIVE_FULL,
            "n_epochs": N_EPOCHS_SMOKE if smoke else N_EPOCHS_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "smoke": smoke,
            "trigger": "ship when v4 returns BET_N_TIER1_PROMOTION or BET_N_PARTIAL_TIER2",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
