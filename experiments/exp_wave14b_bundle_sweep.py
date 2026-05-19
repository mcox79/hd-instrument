"""Wave 14.B sweep: bundle-size scaling for the sum resonator.

Pre-registered (notes/wave14b_decomposition_math_survey.md):
the operational capacity for the sum resonator scales as roughly
bundle_size × log(codebook_size) <~ N. For our K=32, N=4096, the
predicted cliff is at bundle size B in [64, 256].

This experiment characterizes where 14.B breaks. The base case
(B=2) hit 100%; finding the cliff is the actual science.

Setup:
- N = 4096, K = 32
- Bundle sizes: B in {2, 4, 8, 16, 32, 64, 128}
- 100 trials per B (50 saves time vs 200 in base case)
- 8 restarts per query
- Soft resonator with temperature schedule
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch

SEED = 17
N = 4096
K = 32
NUM_TRIALS = 100
NUM_RESTARTS = 8
MAX_ITER = 100
BETA_INIT = 1.0
BETA_MULT = 1.2
BETA_MAX = 20.0
BUNDLE_SIZES = [2, 4, 8, 16, 32, 64, 128]


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen: torch.Generator) -> torch.Tensor:
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_positions(gen: torch.Generator, B: int) -> torch.Tensor:
    """B position codes, shape (B, N)."""
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def make_bundle(atoms: torch.Tensor, positions: torch.Tensor) -> torch.Tensor:
    """c = sum_i (atoms[i] (*) positions[i]). atoms shape (B,N), positions shape (B,N)."""
    return (atoms * positions).sum(dim=0)


def cleanup_hard(v: torch.Tensor, codebook: torch.Tensor) -> tuple[torch.Tensor, int]:
    scores = codebook @ v
    idx = int(scores.argmax().item())
    return codebook[idx], idx


def cleanup_soft(v: torch.Tensor, codebook: torch.Tensor, beta: float) -> torch.Tensor:
    scores = (codebook @ v) / math.sqrt(N)
    weights = torch.softmax(beta * scores, dim=0)
    return weights @ codebook


def run_resonator_soft_B(c: torch.Tensor, positions: torch.Tensor,
                        codebook: torch.Tensor, gen: torch.Generator) -> list[int]:
    """Multi-restart soft-cleanup resonator for B-element bundle.
    Returns predicted atom indices per slot."""
    B = positions.shape[0]
    best_score = -float("inf")
    best_idx = [-1] * B
    for restart in range(NUM_RESTARTS):
        # Initialize all slots randomly from codebook
        init_indices = torch.randint(0, K, (B,), generator=gen)
        atoms_hat = codebook[init_indices].clone()
        beta = BETA_INIT
        prev_atoms = atoms_hat.clone()
        for it in range(MAX_ITER):
            # For each slot, compute candidate, soft-clean
            for s in range(B):
                # Subtract all other slot contributions
                contribution_others = (atoms_hat * positions).sum(dim=0) - atoms_hat[s] * positions[s]
                candidate = (c - contribution_others) * positions[s]
                atoms_hat[s] = cleanup_soft(candidate, codebook, beta)
            beta = min(beta * BETA_MULT, BETA_MAX)
            delta = float((atoms_hat - prev_atoms).abs().mean())
            if delta < 1e-6 and beta >= BETA_MAX:
                break
            prev_atoms = atoms_hat.clone()
        # Hard projection to read off indices
        pred_idx = []
        for s in range(B):
            _, idx = cleanup_hard(atoms_hat[s], codebook)
            pred_idx.append(idx)
        # Reconstruct and score
        pred_atoms = codebook[torch.tensor(pred_idx)]
        c_recon = make_bundle(pred_atoms, positions)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def sweep_one_B(B: int, codebook: torch.Tensor) -> dict:
    """Run NUM_TRIALS at bundle size B, return per-trial recovery."""
    all_correct = 0
    avg_per_slot = 0.0
    fully_correct = 0
    gen_top = torch.Generator().manual_seed(SEED + 10000 + B)
    positions = build_positions(gen_top, B)
    per_trial = []
    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 20000 + B * 1000 + trial)
        true_indices = torch.randint(0, K, (B,), generator=tg).tolist()
        true_atoms = codebook[torch.tensor(true_indices)]
        c = make_bundle(true_atoms, positions)
        pred_indices = run_resonator_soft_B(c, positions, codebook, tg)
        slot_correct = sum(1 for t, p in zip(true_indices, pred_indices) if t == p)
        per_slot_rate = slot_correct / B
        avg_per_slot += per_slot_rate
        if slot_correct == B:
            fully_correct += 1
        if trial < 5:
            per_trial.append({"trial": trial, "true": true_indices, "pred": pred_indices,
                              "slot_correct": slot_correct, "B": B})
    return {"B": B, "trials": NUM_TRIALS,
            "fully_correct": fully_correct,
            "fully_correct_rate": fully_correct / NUM_TRIALS,
            "avg_per_slot_accuracy": avg_per_slot / NUM_TRIALS,
            "sample": per_trial}


def main() -> None:
    _say(f"Wave 14.B bundle-size sweep")
    _say(f"  N={N}, K={K}, restarts={NUM_RESTARTS}, trials/B={NUM_TRIALS}, seed={SEED}")
    _say(f"  Bundle sizes: {BUNDLE_SIZES}")
    _say(f"  Predicted cliff (per Kent-Frady): B*log(K) approx N -> B around {N/math.log(K):.0f}")

    gen = torch.Generator().manual_seed(SEED)
    codebook = build_codebook(gen)
    _say(f"  codebook shape: {tuple(codebook.shape)}")

    results = []
    t_start = time.perf_counter()
    _say(f"\n{'B':>4} | {'full %':>8} | {'avg slot %':>10} | {'elapsed':>8}")
    _say(f"{'-'*4}-+-{'-'*8}-+-{'-'*10}-+-{'-'*8}")
    for B in BUNDLE_SIZES:
        r = sweep_one_B(B, codebook)
        elapsed = time.perf_counter() - t_start
        _say(f"{B:>4} | {100*r['fully_correct_rate']:>7.1f}% | {100*r['avg_per_slot_accuracy']:>9.1f}% | {elapsed:>7.1f}s")
        results.append(r)

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_bundle_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"config": {"N": N, "K": K, "NUM_TRIALS": NUM_TRIALS,
                     "NUM_RESTARTS": NUM_RESTARTS, "BUNDLE_SIZES": BUNDLE_SIZES,
                     "SEED": SEED},
           "results": results,
           "wall_s": time.perf_counter() - t_start}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")
    _say(f"Total wall time: {(time.perf_counter()-t_start):.1f}s")


if __name__ == "__main__":
    main()
