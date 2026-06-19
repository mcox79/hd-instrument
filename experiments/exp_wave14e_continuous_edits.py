"""Continuous edits via soft bipolar relaxation — can α-interpolated edits move predictions smoothly?

Approach: replace sign() with tanh(γ·x) for finite γ. Edit atom A → atom B with
α ∈ [0,1]: interpolated_atom = tanh(γ·(α·atom_B + (1-α)·atom_A)).

Minimal test:
- Encode a fact "prefix → byte_A" as a bundle with byte_A's atom.
- Edit toward "prefix → byte_B" with α ∈ {0, 0.25, 0.5, 0.75, 1.0}.
- Measure P(byte_A | prefix) and P(byte_B | prefix) at each α.
- Pass if P(byte_A) monotonically decreases AND P(byte_B) monotonically increases as α grows.
"""

from __future__ import annotations

import json
from pathlib import Path

import torch

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
N = 4096
K = 4
VOCAB_SIZE = 256
BETA = 8.0
GAMMA_VALUES = [1.0, 2.0, 4.0, 8.0]
ALPHAS = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
NUM_TRIALS = 50
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_bundle(byte_atoms, pos_atoms, byte_indices):
    bound = byte_atoms[byte_indices] * pos_atoms
    summed = bound.sum(dim=0)
    out = torch.sign(summed)
    return torch.where(out == 0, torch.ones_like(out), out)


def soft_atom_blend(atom_a, atom_b, alpha, gamma):
    """Interpolate from atom_a (alpha=0) to atom_b (alpha=1) via tanh-relaxed bipolar."""
    raw = alpha * atom_b + (1 - alpha) * atom_a
    return torch.tanh(gamma * raw)


def edit_bundle_continuous(bundle, byte_atoms, pos_atoms, edit_position, old_byte, new_byte, alpha, gamma):
    """Remove old_byte's contribution at edit_position; add interpolated atom contribution."""
    old_atom = byte_atoms[old_byte] * pos_atoms[edit_position]
    interp_byte_atom = soft_atom_blend(byte_atoms[old_byte], byte_atoms[new_byte], alpha, gamma)
    new_contribution = interp_byte_atom * pos_atoms[edit_position]
    new_bundle = bundle - old_atom + new_contribution
    return new_bundle  # NOT sign'd -- soft bundle


def query_byte_prob(bundle, byte_atoms, soft=True):
    """Probability over bytes via softmax of bundle·byte_atom / N."""
    sims = (byte_atoms @ bundle) / N
    return torch.softmax(BETA * sims, dim=0)


def main():
    _say(f"Continuous edits via soft bipolar: N={N}, K={K}, gammas={GAMMA_VALUES}")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)

    trial_gen = torch.Generator().manual_seed(SEED * 7)
    results_per_gamma = {}
    for gamma in GAMMA_VALUES:
        monotone_count_a = 0
        monotone_count_b = 0
        for trial in range(NUM_TRIALS):
            # Pick K-byte fact + edit position + new byte
            facts = torch.randint(0, VOCAB_SIZE, (K,), generator=trial_gen)
            edit_pos = int(torch.randint(0, K, (1,), generator=trial_gen).item())
            byte_a = int(facts[edit_pos].item())
            byte_b = int(torch.randint(0, VOCAB_SIZE, (1,), generator=trial_gen).item())
            if byte_b == byte_a: byte_b = (byte_b + 1) % VOCAB_SIZE
            facts_dev = facts.to(DEVICE)

            # Build base bundle
            base = build_bundle(byte_atoms, pos_atoms, facts_dev)

            p_a_curve = []
            p_b_curve = []
            for alpha in ALPHAS:
                edited = edit_bundle_continuous(base, byte_atoms, pos_atoms,
                                                  edit_pos, byte_a, byte_b, alpha, gamma)
                # decode position edit_pos
                proj = edited * pos_atoms[edit_pos]
                P = query_byte_prob(proj, byte_atoms)
                p_a_curve.append(float(P[byte_a].item()))
                p_b_curve.append(float(P[byte_b].item()))

            # Check monotonicity
            mono_a = all(p_a_curve[i] >= p_a_curve[i+1] - 0.005 for i in range(len(p_a_curve) - 1))
            mono_b = all(p_b_curve[i] <= p_b_curve[i+1] + 0.005 for i in range(len(p_b_curve) - 1))
            if mono_a: monotone_count_a += 1
            if mono_b: monotone_count_b += 1

        mono_a_rate = monotone_count_a / NUM_TRIALS
        mono_b_rate = monotone_count_b / NUM_TRIALS
        results_per_gamma[gamma] = {"mono_a_rate": mono_a_rate, "mono_b_rate": mono_b_rate}
        _say(f"  gamma={gamma}: P(byte_A) monotone-decrease = {mono_a_rate*100:.1f}%, P(byte_B) monotone-increase = {mono_b_rate*100:.1f}%")

    best_gamma = max(results_per_gamma, key=lambda g: results_per_gamma[g]["mono_a_rate"] + results_per_gamma[g]["mono_b_rate"])
    best = results_per_gamma[best_gamma]
    _say(f"\n  Best gamma: {best_gamma}")
    if best["mono_a_rate"] >= 0.8 and best["mono_b_rate"] >= 0.8:
        _say(f"  PASS: continuous edits work via soft bipolar at gamma={best_gamma}.")
    else:
        _say(f"  WEAK: smoothness not robust. Need FHRR or different relaxation.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_continuous_edits"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "GAMMA_VALUES": GAMMA_VALUES, "ALPHAS": ALPHAS,
        "results_per_gamma": {str(g): r for g, r in results_per_gamma.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
