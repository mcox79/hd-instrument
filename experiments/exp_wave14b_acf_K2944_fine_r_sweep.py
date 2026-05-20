"""ACF resonator with sparsity sweep: r in {0.005, 0.01, 0.05, 0.1}.

First ACF v2 attempt with r=0.01 partial result: K=2048 -> 20% (WORSE
than baseline 100%), K=2560 -> 60% (BETTER than baseline 10%). The
crossover is interesting but the K=2048 regression is suspicious --
likely r=0.01 is too aggressive for the easy regime.

Paper (Karunaratne-Langenegger 2024) tests r in {0.005, 0.01, 0.1}.
Smaller r should help in the easy regime. This sweep checks all three
plus 0.05 at K in {2048, 2560, 3072} -- the boundary region.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch


torch.set_num_threads(8)
DEVICE = torch.device("cpu")
SEED = 17
N = 4096
B = 2
K_SWEEP = [2944]
SPARSITY_SWEEP = [0.005, 0.01, 0.05, 0.1]
NUM_TRIALS = 50
NUM_RESTARTS = 16
NUM_ITERATIONS = 100
THRESHOLD_T = 0.05


def _say(msg):
    print(msg, flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def make_bit_flip_mask(shape, r, gen):
    flip = (torch.rand(shape, generator=gen) < r).float()
    return 1.0 - 2.0 * flip


def hard_threshold(x, t):
    return torch.where(x.abs() > t, x, torch.zeros_like(x))


def acf_step(estimates, atoms_a_s, atoms_a_r, atoms_b_s, atoms_b_r,
             bundle, n, t):
    e1, e2 = estimates
    proj_for_a = bundle * e2
    scores_a = atoms_a_s @ proj_for_a / n
    alpha_a = hard_threshold(scores_a, t)
    e1_new = torch.sign(atoms_a_r.T @ alpha_a)
    e1_new = torch.where(e1_new == 0, torch.ones_like(e1_new), e1_new)
    proj_for_b = bundle * e1_new
    scores_b = atoms_b_s @ proj_for_b / n
    alpha_b = hard_threshold(scores_b, t)
    e2_new = torch.sign(atoms_b_r.T @ alpha_b)
    e2_new = torch.where(e2_new == 0, torch.ones_like(e2_new), e2_new)
    return [e1_new, e2_new]


def try_factor_acf(bundle, atoms_a_s, atoms_a_r, atoms_b_s, atoms_b_r,
                   n, max_iter, restarts, t):
    best_a = -1
    best_b = -1
    best_score = -float('inf')
    for r in range(restarts):
        gen = torch.Generator().manual_seed(r * 7919 + 1)
        e1 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        e2 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        estimates = [e1, e2]
        for _ in range(max_iter):
            new_est = acf_step(estimates, atoms_a_s, atoms_a_r,
                                atoms_b_s, atoms_b_r, bundle, n, t)
            if torch.equal(new_est[0], estimates[0]) and torch.equal(new_est[1], estimates[1]):
                break
            estimates = new_est
        scores_a = atoms_a_s @ estimates[0] / n
        scores_b = atoms_b_s @ estimates[1] / n
        idx_a = int(scores_a.argmax().item())
        idx_b = int(scores_b.argmax().item())
        score = float(scores_a[idx_a]) + float(scores_b[idx_b])
        if score > best_score:
            best_score = score
            best_a, best_b = idx_a, idx_b
    return best_a, best_b


def main():
    _say(f"ACF sparsity sweep: r in {SPARSITY_SWEEP}, K in {K_SWEEP}")
    _say(f"  threshold={THRESHOLD_T}  trials={NUM_TRIALS}  restarts={NUM_RESTARTS}")

    grid = []
    for K in K_SWEEP:
        gen_codebooks = torch.Generator().manual_seed(SEED + K)
        atoms_a_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        atoms_b_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        for r in SPARSITY_SWEEP:
            gen_bfm = torch.Generator().manual_seed(SEED + 7777 + K + int(r * 1e6))
            bfm_a = make_bit_flip_mask((K, N), r, gen_bfm).to(DEVICE)
            bfm_b = make_bit_flip_mask((K, N), r, gen_bfm).to(DEVICE)
            atoms_a_r = atoms_a_s * bfm_a
            atoms_b_r = atoms_b_s * bfm_b
            gen_trial = torch.Generator().manual_seed(SEED + 9000 + K + int(r * 1e6))
            correct = 0
            for t_idx in range(NUM_TRIALS):
                true_indices = []
                bundle = torch.zeros(N, device=DEVICE)
                for _ in range(B):
                    i_a = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                    i_b = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                    true_indices.append((i_a, i_b))
                    bundle += atoms_a_s[i_a] * atoms_b_s[i_b]
                bundle = torch.sign(bundle)
                bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
                rec_a, rec_b = try_factor_acf(bundle, atoms_a_s, atoms_a_r,
                                                atoms_b_s, atoms_b_r,
                                                N, NUM_ITERATIONS, NUM_RESTARTS, THRESHOLD_T)
                if (rec_a, rec_b) in true_indices:
                    correct += 1
            recovery = 100 * correct / NUM_TRIALS
            _say(f"  K={K:5d}  r={r:.3f}  recovery={recovery:5.1f}%")
            grid.append({"K": K, "r": r, "recovery_pct": recovery})

    _say(f"\nBest config per K:")
    by_K = {}
    for entry in grid:
        K = entry["K"]
        if K not in by_K or entry["recovery_pct"] > by_K[K]["recovery_pct"]:
            by_K[K] = entry
    for K in K_SWEEP:
        if K in by_K:
            best = by_K[K]
            _say(f"  K={K}: best r={best['r']} -> {best['recovery_pct']:.1f}%")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_acf_K2944_fine_r_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "B": B, "K_SWEEP": K_SWEEP, "SPARSITY_SWEEP": SPARSITY_SWEEP,
        "THRESHOLD_T": THRESHOLD_T, "grid": grid,
    }, indent=2))


if __name__ == "__main__":
    main()
