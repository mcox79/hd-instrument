"""SSH-BSC chiral topological substrate test — minimal kink-vs-no-kink falsification.

Per wave14e2_topological_substrate_research:
- Fix two sublattice atoms a_A, a_B
- Modulation pattern h_q with q domain walls
- key = sign(a_A + h_q * a_B)
- Topological charge q = (count of sign-disagreement pairs in decoded modulation) / 2

Protection mechanism (chiral class AIII):
- I.i.d. Bernoulli(p) noise can shift q by ±1 only at sites adjacent to walls
- Larger shifts require coordinated multi-bit flips with probability ~p²
- Predicted threshold p_c ≈ 1/(2·ν_density)
- SHARP KINK in winding-recovery vs noise level (vs smooth decay for random encoding)

Minimal test: encode two facts with topological charges q=2 and q=10. Apply Bernoulli noise at p ∈ {0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3}. Decode the topological charge after noise. Compare to a random-encoding baseline.

Pass if SSH-BSC shows a sharp kink (recovery flat then sudden drop) where random-encoding shows smooth decay.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
SEED = 17
NOISE_LEVELS = [0.0, 0.01, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]
NUM_TRIALS = 100
CHARGE_VALUES = [2, 5, 10, 20]


def _say(m): print(m, flush=True)


def make_bsc_atom(n, gen):
    return 2.0 * (torch.rand(n, generator=gen) > 0.5).float() - 1.0


def make_modulation_with_walls(n, num_walls, gen):
    """Generate ±1 vector with exactly `num_walls` sign domain walls.
    Distribute walls evenly with small jitter."""
    if num_walls == 0:
        return torch.ones(n, device=DEVICE)
    if num_walls >= n:
        # Alternating pattern
        return (-1.0) ** torch.arange(n, device=DEVICE).float()
    # Choose wall positions
    positions = sorted(torch.randperm(n - 1, generator=gen)[:num_walls].tolist())
    h = torch.ones(n, device=DEVICE)
    sign = 1.0
    pos = 0
    for wall in positions:
        h[pos:wall+1] = sign
        sign = -sign
        pos = wall + 1
    h[pos:] = sign
    return h


def count_domain_walls(vec):
    """Count sign disagreements between adjacent elements."""
    diffs = (vec[1:] != vec[:-1]).int()
    return int(diffs.sum().item())


def encode_topological_key(a_A, a_B, h_q):
    """key = sign(a_A + h_q * a_B)."""
    raw = a_A + h_q * a_B
    out = torch.sign(raw)
    return torch.where(out == 0, torch.ones_like(out), out)


def decode_topological_charge(key, a_A, a_B):
    """Recover modulation by: h_recovered = sign((key - a_A) / a_B) approximately.
    Better: h_recovered[i] = +1 if (key[i] - a_A[i]) and a_B[i] have same sign, else -1.
    Then count domain walls in h_recovered."""
    # Project out a_A: residual = key - a_A. Then h = sign(residual * a_B)
    residual = key.float() - a_A.float()
    # Where residual is zero, default to +1 (a_A dominates the sign)
    h_recovered = torch.where(residual == 0, torch.ones_like(residual), torch.sign(residual * a_B))
    # Count domain walls
    walls = count_domain_walls(h_recovered)
    return walls, h_recovered


def apply_bernoulli_noise(vec, p, gen):
    """Flip each bit independently with probability p."""
    mask = torch.rand(vec.shape, generator=gen, device=vec.device) < p
    return torch.where(mask, -vec, vec)


def main():
    _say(f"SSH-BSC topological substrate test: N={N}, charges={CHARGE_VALUES}, noise levels={NOISE_LEVELS}")
    gen = torch.Generator(device="cpu").manual_seed(SEED)
    a_A = make_bsc_atom(N, gen).to(DEVICE)
    a_B = make_bsc_atom(N, gen).to(DEVICE)

    results = {}
    for q_true in CHARGE_VALUES:
        _say(f"\n[q_true={q_true}]")
        # Generate canonical modulation for this charge
        h_q = make_modulation_with_walls(N, q_true, gen).to(DEVICE)
        actual_walls = count_domain_walls(h_q)
        _say(f"  modulation built with {actual_walls} domain walls")
        key = encode_topological_key(a_A, a_B, h_q)

        # SSH-BSC topological encoding noise resistance
        ssh_results = []
        for p in NOISE_LEVELS:
            recovered_walls = []
            for trial in range(NUM_TRIALS):
                noise_gen = torch.Generator(device=DEVICE).manual_seed(SEED * 1000 + int(p * 1000) + trial)
                noisy_key = apply_bernoulli_noise(key, p, noise_gen)
                walls, _ = decode_topological_charge(noisy_key, a_A, a_B)
                recovered_walls.append(walls)
            mean_walls = sum(recovered_walls) / len(recovered_walls)
            sd_walls = (sum((w - mean_walls) ** 2 for w in recovered_walls) / len(recovered_walls)) ** 0.5
            # Categorical: correct = recovered walls is within ±1 of true
            categorical_correct = sum(1 for w in recovered_walls if abs(w - q_true) <= 1) / NUM_TRIALS
            ssh_results.append({"p": p, "mean_walls": mean_walls, "sd_walls": sd_walls,
                                  "categorical_correct": categorical_correct})
            _say(f"  noise p={p:.3f}: recovered walls = {mean_walls:.2f} ± {sd_walls:.2f}, cat correct = {categorical_correct*100:.0f}%")

        # Random-encoding baseline: encode the SAME q_true info as random bipolar bits
        # Just sign(random) — this has no topological structure
        random_key = make_bsc_atom(N, gen).to(DEVICE)
        # Define "correct" for random as: the decoded walls match q_true within ±2
        # For random keys, the walls count is ~N/2 = 2048, not q_true. So we test if noise leaves the count near the original.
        original_random_walls = count_domain_walls(random_key)
        random_results = []
        for p in NOISE_LEVELS:
            deltas = []
            for trial in range(NUM_TRIALS):
                noise_gen = torch.Generator(device=DEVICE).manual_seed(SEED * 2000 + int(p * 1000) + trial)
                noisy_random = apply_bernoulli_noise(random_key, p, noise_gen)
                noisy_walls = count_domain_walls(noisy_random)
                deltas.append(noisy_walls - original_random_walls)
            mean_delta = sum(deltas) / len(deltas)
            sd_delta = (sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)) ** 0.5
            random_results.append({"p": p, "mean_delta": mean_delta, "sd_delta": sd_delta})

        results[q_true] = {"ssh": ssh_results, "random_baseline": random_results}

    # Verdict: does SSH-BSC show categorical (flat-then-cliff) noise tolerance?
    _say("\n========= SSH-BSC TOPOLOGICAL VERDICT =========")
    for q_true in CHARGE_VALUES:
        ssh = results[q_true]["ssh"]
        # Find the noise level where categorical_correct drops below 50%
        cliff_p = None
        for r in ssh:
            if r["categorical_correct"] < 0.5:
                cliff_p = r["p"]; break
        if cliff_p is None:
            cliff_p = "no_cliff"
        _say(f"  q={q_true}: cliff at p={cliff_p}")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e2_ssh_bsc_topological"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "CHARGE_VALUES": CHARGE_VALUES, "NOISE_LEVELS": NOISE_LEVELS,
        "NUM_TRIALS": NUM_TRIALS,
        "results": {str(q): r for q, r in results.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
