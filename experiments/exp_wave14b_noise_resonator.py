"""K-cliff rescue: Langenegger 2024 noise-injection resonator.

K-cliff agent: 'noise injection extends operational capacity >=50x over
baseline.' For F=2, noise pushes solvable search space past 5x10^9 vs
~10^5 for baseline.

Implementation: inject Gaussian noise into the estimates at each
iteration. The noise prevents convergence to spurious fixed points
and lets the resonator escape local minima.

Sweep K in {2048, 2560, 3072, 4096, 6144, 8192} at B=2 N=4096.
Compare to baseline (no noise) which gave 100/10/0/0/0/0%.
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
K_SWEEP = [2048, 2560, 3072, 4096, 6144, 8192]
NUM_TRIALS = 30
NUM_RESTARTS = 16
NUM_ITERATIONS = 100
NOISE_SCALE = 0.1  # std of Gaussian noise injected at each iter


def _say(msg):
    print(msg, flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def resonator_step_noisy(estimates, atoms_a, atoms_b, bundle_target, n,
                          noise_scale, noise_gen):
    e1, e2 = estimates
    proj_for_1 = bundle_target * e2
    scores_1 = atoms_a @ proj_for_1 / n
    noisy_scores_1 = scores_1 + noise_scale * torch.randn(
        scores_1.shape, generator=noise_gen)
    e1_new = torch.sign(atoms_a.T @ torch.tanh(2.0 * noisy_scores_1))
    e1_new = torch.where(e1_new == 0, torch.ones_like(e1_new), e1_new)
    proj_for_2 = bundle_target * e1_new
    scores_2 = atoms_b @ proj_for_2 / n
    noisy_scores_2 = scores_2 + noise_scale * torch.randn(
        scores_2.shape, generator=noise_gen)
    e2_new = torch.sign(atoms_b.T @ torch.tanh(2.0 * noisy_scores_2))
    e2_new = torch.where(e2_new == 0, torch.ones_like(e2_new), e2_new)
    return [e1_new, e2_new]


def try_factor_noisy(bundle, atoms_a, atoms_b, n, max_iter, restarts, noise_scale):
    best_a = -1
    best_b = -1
    best_score = -float('inf')
    for r in range(restarts):
        gen = torch.Generator().manual_seed(r * 7919 + 1)
        noise_gen = torch.Generator().manual_seed(r * 13371 + 7)
        e1 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        e2 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        estimates = [e1, e2]
        # Anneal noise from full to zero over iterations
        for it in range(max_iter):
            current_noise = noise_scale * (1.0 - it / max_iter)
            new_est = resonator_step_noisy(estimates, atoms_a, atoms_b,
                                            bundle, n, current_noise, noise_gen)
            if torch.equal(new_est[0], estimates[0]) and torch.equal(new_est[1], estimates[1]):
                break
            estimates = new_est
        scores_a = atoms_a @ estimates[0] / n
        scores_b = atoms_b @ estimates[1] / n
        idx_a = int(scores_a.argmax().item())
        idx_b = int(scores_b.argmax().item())
        score = float(scores_a[idx_a]) + float(scores_b[idx_b])
        if score > best_score:
            best_score = score
            best_a, best_b = idx_a, idx_b
    return best_a, best_b


def main():
    _say(f"Noise-injection resonator (Langenegger 2024 rescue)")
    _say(f"  NOISE_SCALE={NOISE_SCALE} annealed to 0 over {NUM_ITERATIONS} iters")
    _say(f"  Sweep K in {K_SWEEP} at N={N}, B={B}")

    results = []
    for K in K_SWEEP:
        gen_codebooks = torch.Generator().manual_seed(SEED + K)
        byte_atoms = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        pos_atoms = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        gen_trial = torch.Generator().manual_seed(SEED + 5000 + K)
        correct = 0
        for t in range(NUM_TRIALS):
            true_indices = []
            bundle = torch.zeros(N, device=DEVICE)
            for _ in range(B):
                i_a = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                i_b = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                true_indices.append((i_a, i_b))
                bundle += byte_atoms[i_a] * pos_atoms[i_b]
            bundle = torch.sign(bundle)
            bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
            rec_a, rec_b = try_factor_noisy(bundle, byte_atoms, pos_atoms, N,
                                             NUM_ITERATIONS, NUM_RESTARTS, NOISE_SCALE)
            if (rec_a, rec_b) in true_indices:
                correct += 1
        recovery = 100 * correct / NUM_TRIALS
        _say(f"  K={K:5d} ({K/N:.2f}*N)  recovery={recovery:5.1f}%")
        results.append({"K": K, "K_over_N": K/N, "recovery_pct": recovery})

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_noise_resonator"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "B": B, "K_SWEEP": K_SWEEP, "NOISE_SCALE": NOISE_SCALE,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
