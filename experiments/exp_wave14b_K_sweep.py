"""Wave 14.B K-sweep: vary codebook size at fixed B=2.

Per math survey, sum resonator capacity scales as B*log(K) <~ N.
For N=4096, B=2: predicted cliff at K ~ 2^(N/B) which is astronomical
but actual scaling is empirically tighter. This experiment finds the
codebook-size cliff at the smallest bundle size.

Note: codebook needs to be small enough that we have 8 restarts that
can plausibly hit the right pair. With K=2048 there are 4M pairs and
only 8 starting points -- so we expect this to break around K=256-512
on the algorithm side regardless of information.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch

SEED = 17
N = 4096
B = 2
NUM_TRIALS = 100
NUM_RESTARTS = 8
MAX_ITER = 100
BETA_INIT = 1.0
BETA_MULT = 1.2
BETA_MAX = 20.0
K_SIZES = [32, 64, 128, 256, 512, 1024, 2048]


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen: torch.Generator, K: int) -> torch.Tensor:
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_positions(gen: torch.Generator) -> torch.Tensor:
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def make_bundle(atoms: torch.Tensor, positions: torch.Tensor) -> torch.Tensor:
    return (atoms * positions).sum(dim=0)


def cleanup_hard(v: torch.Tensor, codebook: torch.Tensor) -> tuple[torch.Tensor, int]:
    scores = codebook @ v
    idx = int(scores.argmax().item())
    return codebook[idx], idx


def cleanup_soft(v: torch.Tensor, codebook: torch.Tensor, beta: float) -> torch.Tensor:
    scores = (codebook @ v) / math.sqrt(N)
    weights = torch.softmax(beta * scores, dim=0)
    return weights @ codebook


def run_resonator(c: torch.Tensor, positions: torch.Tensor, codebook: torch.Tensor,
                  K: int, gen: torch.Generator) -> list[int]:
    best_score = -float("inf")
    best_idx = [-1] * B
    for restart in range(NUM_RESTARTS):
        init_indices = torch.randint(0, K, (B,), generator=gen)
        atoms_hat = codebook[init_indices].clone()
        beta = BETA_INIT
        prev_atoms = atoms_hat.clone()
        for it in range(MAX_ITER):
            for s in range(B):
                contribution_others = (atoms_hat * positions).sum(dim=0) - atoms_hat[s] * positions[s]
                candidate = (c - contribution_others) * positions[s]
                atoms_hat[s] = cleanup_soft(candidate, codebook, beta)
            beta = min(beta * BETA_MULT, BETA_MAX)
            delta = float((atoms_hat - prev_atoms).abs().mean())
            if delta < 1e-6 and beta >= BETA_MAX:
                break
            prev_atoms = atoms_hat.clone()
        pred_idx = []
        for s in range(B):
            _, idx = cleanup_hard(atoms_hat[s], codebook)
            pred_idx.append(idx)
        pred_atoms = codebook[torch.tensor(pred_idx)]
        c_recon = make_bundle(pred_atoms, positions)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def sweep_one_K(K: int, codebook: torch.Tensor, positions: torch.Tensor) -> dict:
    fully_correct = 0
    avg_per_slot = 0.0
    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 30000 + K * 1000 + trial)
        true_indices = torch.randint(0, K, (B,), generator=tg).tolist()
        true_atoms = codebook[torch.tensor(true_indices)]
        c = make_bundle(true_atoms, positions)
        pred_indices = run_resonator(c, positions, codebook, K, tg)
        slot_correct = sum(1 for t, p in zip(true_indices, pred_indices) if t == p)
        avg_per_slot += slot_correct / B
        if slot_correct == B:
            fully_correct += 1
    return {"K": K, "trials": NUM_TRIALS,
            "fully_correct": fully_correct,
            "fully_correct_rate": fully_correct / NUM_TRIALS,
            "avg_per_slot_accuracy": avg_per_slot / NUM_TRIALS}


def main() -> None:
    _say(f"Wave 14.B K-sweep (codebook size)")
    _say(f"  N={N}, B={B}, restarts={NUM_RESTARTS}, trials/K={NUM_TRIALS}, seed={SEED}")
    _say(f"  Codebook sizes: {K_SIZES}")

    gen = torch.Generator().manual_seed(SEED)
    positions = build_positions(gen)
    _say(f"  positions shape: {tuple(positions.shape)}")

    results = []
    t_start = time.perf_counter()
    _say(f"\n{'K':>5} | {'full %':>8} | {'avg slot %':>10} | {'elapsed':>8}")
    _say(f"{'-'*5}-+-{'-'*8}-+-{'-'*10}-+-{'-'*8}")
    for K in K_SIZES:
        # Need fresh codebook per K (different sizes)
        K_gen = torch.Generator().manual_seed(SEED + K)
        codebook = build_codebook(K_gen, K)
        r = sweep_one_K(K, codebook, positions)
        elapsed = time.perf_counter() - t_start
        _say(f"{K:>5} | {100*r['fully_correct_rate']:>7.1f}% | {100*r['avg_per_slot_accuracy']:>9.1f}% | {elapsed:>7.1f}s")
        results.append(r)

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_K_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"config": {"N": N, "B": B, "NUM_TRIALS": NUM_TRIALS,
                     "NUM_RESTARTS": NUM_RESTARTS, "K_SIZES": K_SIZES, "SEED": SEED},
           "results": results, "wall_s": time.perf_counter() - t_start}
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")
    _say(f"Total wall time: {(time.perf_counter()-t_start):.1f}s")


if __name__ == "__main__":
    main()
