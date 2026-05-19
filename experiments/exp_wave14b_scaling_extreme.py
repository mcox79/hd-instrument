"""Wave 14.B scaling at N=131072 (128K) and N=262144 (256K).

Extends the scaling sweep beyond N=65K. We confirmed 100% recovery up
to N=65K with B=128 K=2048. Does the substrate maintain 100% at 128K
and 256K? This characterizes the upper limit of the operating envelope.

Smaller test grid since N=256K with B=128 is expensive:
- N in {131072, 262144}
- B in {2, 32}        (skip 8, 128 to save time)
- K in {32, 256, 2048}

Parameter variant of exp_wave14b_scaling_sweep.py — only N_VALUES and
some range trims differ.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
NUM_TRIALS = 30  # reduced from 50 since each is much more expensive
NUM_RESTARTS = 8
MAX_ITER = 100
BETA_INIT = 1.0
BETA_MULT = 1.2
BETA_MAX = 20.0

N_VALUES = [131072, 262144]
BUNDLE_SIZES = [2, 32]
K_SIZES = [32, 256, 2048]


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen, K, N):
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32).to(DEVICE)


def build_positions(gen, B, N):
    bits = torch.randint(0, 2, (B, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32).to(DEVICE)


def make_bundle(atoms, positions):
    return (atoms * positions).sum(dim=0)


def cleanup_hard(v, codebook):
    scores = codebook @ v
    idx = int(scores.argmax().item())
    return codebook[idx], idx


def cleanup_soft(v, codebook, beta, N):
    scores = (codebook @ v) / math.sqrt(N)
    weights = torch.softmax(beta * scores, dim=0)
    return weights @ codebook


def run_resonator(c, positions, codebook, K, N, gen):
    B = positions.shape[0]
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
                atoms_hat[s] = cleanup_soft(candidate, codebook, beta, N)
            beta = min(beta * BETA_MULT, BETA_MAX)
            delta = float((atoms_hat - prev_atoms).abs().mean())
            if delta < 1e-6 and beta >= BETA_MAX:
                break
            prev_atoms = atoms_hat.clone()
        pred_idx = []
        for s in range(B):
            _, idx = cleanup_hard(atoms_hat[s], codebook)
            pred_idx.append(idx)
        pred_atoms = codebook[torch.tensor(pred_idx, device=DEVICE)]
        c_recon = make_bundle(pred_atoms, positions)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_idx = pred_idx
    return best_idx


def sweep_one(B, K, N, codebook, positions, num_trials):
    fully_correct = 0
    for trial in range(num_trials):
        tg = torch.Generator(device='cpu').manual_seed(SEED + 50000 + N + B * 100 + trial)
        true_indices = torch.randint(0, K, (B,), generator=tg).tolist()
        true_atoms = codebook[torch.tensor(true_indices, device=DEVICE)]
        c = make_bundle(true_atoms, positions)
        pred_indices = run_resonator(c, positions, codebook, K, N, tg)
        slot_correct = sum(1 for t, p in zip(true_indices, pred_indices) if t == p)
        if slot_correct == B:
            fully_correct += 1
    return fully_correct / num_trials


def main():
    _say(f"Wave 14.B extreme scaling: N in {N_VALUES}")
    _say(f"  B in {BUNDLE_SIZES}, K in {K_SIZES}, trials={NUM_TRIALS}")

    all_results = []
    t_start = time.perf_counter()
    for N in N_VALUES:
        _say(f"\n========== N = {N} ==========")
        gen = torch.Generator(device='cpu').manual_seed(SEED + N)
        cb_default = build_codebook(gen, 32, N)
        # B sweep at K=32
        _say(f"\nB sweep (K=32):")
        for B in BUNDLE_SIZES:
            positions = build_positions(gen, B, N)
            t0 = time.perf_counter()
            rate = sweep_one(B, 32, N, cb_default, positions, NUM_TRIALS)
            dt = time.perf_counter() - t0
            _say(f"  B={B}: {100*rate:.1f}%  ({dt:.0f}s)")
            all_results.append({"N": N, "B": B, "K": 32, "recovery": rate, "wall_s": dt})
        # K sweep at B=2
        _say(f"\nK sweep (B=2):")
        positions_b2 = build_positions(gen, 2, N)
        for K in K_SIZES:
            cb = build_codebook(torch.Generator(device='cpu').manual_seed(SEED + N + K), K, N)
            t0 = time.perf_counter()
            rate = sweep_one(2, K, N, cb, positions_b2, NUM_TRIALS)
            dt = time.perf_counter() - t0
            _say(f"  K={K}: {100*rate:.1f}%  ({dt:.0f}s)")
            all_results.append({"N": N, "B": 2, "K": K, "recovery": rate, "wall_s": dt})
        # Incremental save
        out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_scaling_extreme"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "metrics.json").write_text(json.dumps(
            {"results_so_far": all_results, "elapsed_s": time.perf_counter() - t_start},
            indent=2, default=str))

    _say(f"\n========= FULL SUMMARY =========")
    for r in all_results:
        _say(f"  N={r['N']}, B={r['B']}, K={r['K']}: {100*r['recovery']:.1f}%")
    _say(f"\nTotal wall: {(time.perf_counter() - t_start)/60:.1f} min")


if __name__ == "__main__":
    main()
