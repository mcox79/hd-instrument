"""K-cliff rescue, proper ACF variant (Karunaratne-Langenegger 2024).

Per noise-resonator failure research: my first attempt implemented
IMF-style iterative noise. For F=2 the actual paper winner is ACF
(Asymmetric Codebook Factorizer):
- Bit-flip mask applied ONCE at initialization to reconstruction
  codebook only
- Use A for similarity scoring (associative search)
- Use A_rc = A * BFM(r) for reconstruction step
- Hard-threshold activation (not tanh)
- No iterative noise; no annealing

For F=2 the paper reports up to 50x capacity increase over baseline.
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
K_SWEEP = [4096, 6144, 8192, 10240, 12288, 14336, 16384]
NUM_TRIALS = 30
NUM_RESTARTS = 16
NUM_ITERATIONS = 100
BFM_SPARSITY_R = 0.01  # Bernoulli bit-flip prob; paper uses {0.005, 0.01, 0.1}
THRESHOLD_T = 0.05     # hard-threshold activation


def _say(msg):
    print(msg, flush=True)


def make_bsc_atoms(k, n, gen):
    raw = torch.rand((k, n), generator=gen)
    return (2.0 * (raw > 0.5).float() - 1.0)


def make_bit_flip_mask(shape, r, gen):
    """Bernoulli bit-flip mask: +1 with prob (1-r), -1 with prob r."""
    flip = (torch.rand(shape, generator=gen) < r).float()
    return 1.0 - 2.0 * flip  # +1 where no flip, -1 where flip


def hard_threshold(x, t):
    """Sparse activation: f(x) = x if |x| > t else 0."""
    return torch.where(x.abs() > t, x, torch.zeros_like(x))


def acf_resonator_step(estimates, atoms_a_search, atoms_a_recon,
                       atoms_b_search, atoms_b_recon, bundle_target, n, t):
    """ACF resonator step: distinct search and reconstruction codebooks."""
    e1, e2 = estimates
    # Score for factor a using SEARCH codebook
    proj_for_a = bundle_target * e2
    scores_a = atoms_a_search @ proj_for_a / n
    # Hard-threshold activation
    alpha_a = hard_threshold(scores_a, t)
    # Reconstruct using ASYMMETRIC codebook
    e1_new_raw = atoms_a_recon.T @ alpha_a
    e1_new = torch.sign(e1_new_raw)
    e1_new = torch.where(e1_new == 0, torch.ones_like(e1_new), e1_new)

    proj_for_b = bundle_target * e1_new
    scores_b = atoms_b_search @ proj_for_b / n
    alpha_b = hard_threshold(scores_b, t)
    e2_new_raw = atoms_b_recon.T @ alpha_b
    e2_new = torch.sign(e2_new_raw)
    e2_new = torch.where(e2_new == 0, torch.ones_like(e2_new), e2_new)

    return [e1_new, e2_new]


def try_factor_acf(bundle, atoms_a_s, atoms_a_r, atoms_b_s, atoms_b_r,
                   n, max_iter, restarts, threshold):
    best_a = -1
    best_b = -1
    best_score = -float('inf')
    for r in range(restarts):
        gen = torch.Generator().manual_seed(r * 7919 + 1)
        e1 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        e2 = (2 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0).to(bundle.device)
        estimates = [e1, e2]
        for _ in range(max_iter):
            new_est = acf_resonator_step(estimates, atoms_a_s, atoms_a_r,
                                          atoms_b_s, atoms_b_r,
                                          bundle, n, threshold)
            if torch.equal(new_est[0], estimates[0]) and torch.equal(new_est[1], estimates[1]):
                break
            estimates = new_est
        # Final scoring uses the SEARCH codebook (associative-search)
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
    _say(f"ACF resonator (Karunaratne-Langenegger 2024 F=2 winner)")
    _say(f"  BFM_SPARSITY_R={BFM_SPARSITY_R}, THRESHOLD_T={THRESHOLD_T}")
    _say(f"  Sweep K in {K_SWEEP} at N={N}, B={B}")

    results = []
    for K in K_SWEEP:
        gen_codebooks = torch.Generator().manual_seed(SEED + K)
        # Search codebooks (associative)
        byte_atoms_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        pos_atoms_s = make_bsc_atoms(K, N, gen_codebooks).to(DEVICE)
        # Bit-flip masks (applied once at init)
        gen_bfm = torch.Generator().manual_seed(SEED + 7777 + K)
        bfm_a = make_bit_flip_mask((K, N), BFM_SPARSITY_R, gen_bfm).to(DEVICE)
        bfm_b = make_bit_flip_mask((K, N), BFM_SPARSITY_R, gen_bfm).to(DEVICE)
        # Reconstruction codebooks = search * bit-flip mask
        byte_atoms_r = byte_atoms_s * bfm_a
        pos_atoms_r = pos_atoms_s * bfm_b
        gen_trial = torch.Generator().manual_seed(SEED + 8000 + K)
        correct = 0
        for t_idx in range(NUM_TRIALS):
            true_indices = []
            bundle = torch.zeros(N, device=DEVICE)
            for _ in range(B):
                i_a = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                i_b = int(torch.randint(0, K, (1,), generator=gen_trial).item())
                true_indices.append((i_a, i_b))
                # Bundle uses SEARCH codebook (clean atoms)
                bundle += byte_atoms_s[i_a] * pos_atoms_s[i_b]
            bundle = torch.sign(bundle)
            bundle = torch.where(bundle == 0, torch.ones_like(bundle), bundle)
            rec_a, rec_b = try_factor_acf(bundle, byte_atoms_s, byte_atoms_r,
                                           pos_atoms_s, pos_atoms_r,
                                           N, NUM_ITERATIONS, NUM_RESTARTS,
                                           THRESHOLD_T)
            if (rec_a, rec_b) in true_indices:
                correct += 1
        recovery = 100 * correct / NUM_TRIALS
        _say(f"  K={K:5d} ({K/N:.2f}*N)  recovery={recovery:5.1f}%")
        results.append({"K": K, "K_over_N": K/N, "recovery_pct": recovery})

    _say(f"\n========= ACF VERDICT =========")
    _say(f"  Baseline (no noise) cliff was at K/N~0.55 (K=2304 -> 10%)")
    for r in results:
        _say(f"  K={r['K']:5d}  recovery={r['recovery_pct']:5.1f}%")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_acf_resonator_high_K"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "B": B, "K_SWEEP": K_SWEEP,
        "BFM_SPARSITY_R": BFM_SPARSITY_R, "THRESHOLD_T": THRESHOLD_T,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
