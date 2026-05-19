"""ACF with K-dependent r per Karunaratne 2024 paper's appendix.

Sparsity sweep showed ACF is asymmetric: hurts K<=2048 (easy regime),
rescues K>=2560. Per research synthesis, the paper itself uses
K-dependent r. This experiment implements that prescription:
- r = 0 for K/N <= 0.50 (baseline behavior, no ACF perturbation)
- r = 0.005 for 0.50 < K/N <= 0.55
- r = 0.01 for K/N > 0.55

K_SWEEP spans both regimes. Compare to baseline (no ACF) at low K and
fixed-r=0.01 at high K. Predict: K-dependent r matches baseline at
K=2048 (100%) AND matches fixed r=0.01 at K=3072 (85%).
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
K_SWEEP = [2048, 2304, 2560, 3072, 4096, 6144]
NUM_TRIALS = 30
NUM_RESTARTS = 16
NUM_ITERATIONS = 100
THRESHOLD_T = 0.05


def _say(msg):
    print(msg, flush=True)


def r_for_K(K_over_N):
    """Per paper's appendix grid. r=0 for easy regime."""
    if K_over_N <= 0.50:
        return 0.0
    elif K_over_N <= 0.55:
        return 0.005
    else:
        return 0.01


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def make_bit_flip_mask(shape, r, gen):
    if r <= 0:
        return torch.ones(shape)
    flip = (torch.rand(shape, generator=gen) < r).float()
    return 1.0 - 2.0 * flip


def hard_threshold(x, t):
    return torch.where(x.abs() > t, x, torch.zeros_like(x))


def baseline_step(estimates, atoms_a, atoms_b, bundle, n):
    """Original (non-ACF) resonator step using tanh."""
    e1, e2 = estimates
    proj_for_1 = bundle * e2
    scores_1 = atoms_a @ proj_for_1 / n
    e1_new = torch.sign(atoms_a.T @ torch.tanh(2.0 * scores_1))
    e1_new = torch.where(e1_new == 0, torch.ones_like(e1_new), e1_new)
    proj_for_2 = bundle * e1_new
    scores_2 = atoms_b @ proj_for_2 / n
    e2_new = torch.sign(atoms_b.T @ torch.tanh(2.0 * scores_2))
    e2_new = torch.where(e2_new == 0, torch.ones_like(e2_new), e2_new)
    return [e1_new, e2_new]


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


def try_factor(bundle, atoms_a_s, atoms_a_r, atoms_b_s, atoms_b_r,
               n, max_iter, restarts, t, use_acf):
    best_a = -1
    best_b = -1
    best_score = -float('inf')
    for r in range(restarts):
        gen = torch.Generator().manual_seed(r * 7919 + 1)
        e1 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        e2 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        estimates = [e1, e2]
        for _ in range(max_iter):
            if use_acf:
                new_est = acf_step(estimates, atoms_a_s, atoms_a_r,
                                    atoms_b_s, atoms_b_r, bundle, n, t)
            else:
                new_est = baseline_step(estimates, atoms_a_s, atoms_b_s, bundle, n)
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
    _say(f"ACF with K-dependent r (per paper appendix grid)")
    _say(f"  r=0 for K/N<=0.50, r=0.005 for 0.50-0.55, r=0.01 for >0.55")

    results = []
    for K in K_SWEEP:
        K_over_N = K / N
        r = r_for_K(K_over_N)
        use_acf = r > 0
        gen_codebooks = torch.Generator().manual_seed(SEED + K)
        atoms_a_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        atoms_b_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        gen_bfm = torch.Generator().manual_seed(SEED + 7777 + K)
        if use_acf:
            bfm_a = make_bit_flip_mask((K, N), r, gen_bfm).to(DEVICE)
            bfm_b = make_bit_flip_mask((K, N), r, gen_bfm).to(DEVICE)
            atoms_a_r = atoms_a_s * bfm_a
            atoms_b_r = atoms_b_s * bfm_b
        else:
            atoms_a_r = atoms_a_s
            atoms_b_r = atoms_b_s
        gen_trial = torch.Generator().manual_seed(SEED + 11000 + K)
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
            rec_a, rec_b = try_factor(bundle, atoms_a_s, atoms_a_r, atoms_b_s, atoms_b_r,
                                       N, NUM_ITERATIONS, NUM_RESTARTS, THRESHOLD_T, use_acf)
            if (rec_a, rec_b) in true_indices:
                correct += 1
        recovery = 100 * correct / NUM_TRIALS
        _say(f"  K={K:5d} (K/N={K_over_N:.2f}) r={r:.3f} use_acf={use_acf} recovery={recovery:5.1f}%")
        results.append({"K": K, "K_over_N": K_over_N, "r": r, "use_acf": use_acf,
                        "recovery_pct": recovery})

    _say(f"\n========= K-DEPENDENT ACF VERDICT =========")
    _say(f"  Predict: K=2048->100% (matches baseline, r=0)")
    _say(f"           K=2304->10-50% (rescue region, r=0.005)")
    _say(f"           K=3072->85% (matches fixed-r ACF, r=0.01)")
    for r in results:
        _say(f"  K={r['K']}: {r['recovery_pct']:.1f}%")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_acf_K_dependent"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "B": B, "K_SWEEP": K_SWEEP, "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
