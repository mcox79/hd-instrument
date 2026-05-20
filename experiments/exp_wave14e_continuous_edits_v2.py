"""Continuous edits v2 — explicit Bernoulli mixing per wave14e_continuous_edits_research.

Key insight from research: deterministic blend sign(alpha*A + (1-alpha)*B) is a STEP
function at alpha=0.5 (independent bipolar coords flip cleanly at midpoint). FAILS continuity.

Correct primitive: per-coordinate Bernoulli mixing
- atom_alpha[i] = atom_B[i] with prob alpha, atom_A[i] with prob (1-alpha)

This gives EXPECTED smooth interpolation in the limit. For a single sample,
the bundle is bipolar but the population-average is continuous.

Alternative: soft-bipolar latent g, atom = tanh(gamma*g). Equivalent in expectation.

Test: edit "prefix -> byte_A" toward "prefix -> byte_B" via Bernoulli mix at
alpha in {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}. Many samples per alpha; measure
mean P(byte_A) and P(byte_B). Should be smooth in alpha.

Pass: P(byte_A) and P(byte_B) move monotonically and smoothly across alpha (no
step at alpha=0.5).
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
ALPHAS = [0.0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0]
NUM_TRIALS = 200    # samples per alpha for population-mean
NUM_FACTS = 30
SEED = 17


def _say(m): print(m, flush=True)


def make_bsc(k, n, gen):
    return 2.0 * (torch.rand((k, n), generator=gen) > 0.5).float() - 1.0


def build_bundle(byte_atoms, pos_atoms, byte_indices):
    bound = byte_atoms[byte_indices] * pos_atoms
    out = torch.sign(bound.sum(dim=0))
    return torch.where(out == 0, torch.ones_like(out), out)


def bernoulli_mix_atom(atom_a, atom_b, alpha, gen):
    """For each coordinate, with probability alpha use atom_b[i], else atom_a[i]."""
    mask = torch.rand(atom_a.shape, generator=gen, device=atom_a.device) < alpha
    return torch.where(mask, atom_b, atom_a)


def deterministic_blend_atom(atom_a, atom_b, alpha):
    """For comparison: deterministic blend. Per research this FAILS at alpha=0.5."""
    raw = alpha * atom_b + (1 - alpha) * atom_a
    out = torch.sign(raw)
    return torch.where(out == 0, torch.ones_like(out), out)


def edit_bundle_at_position(bundle, byte_atoms, pos_atoms, position, old_byte_atom, new_byte_atom):
    """Replace at position: bundle - old_byte_atom * pos[position] + new_byte_atom * pos[position]."""
    delta = (new_byte_atom - old_byte_atom) * pos_atoms[position]
    return bundle + delta


def query_byte_prob_at_position(bundle, byte_atoms, pos_atom):
    proj = bundle * pos_atom
    sims = byte_atoms @ proj / N
    return torch.softmax(BETA * sims, dim=0)


def main():
    _say(f"Continuous edits v2: Bernoulli mixing vs deterministic blend, N={N}, K={K}")
    _say(f"  {NUM_FACTS} facts, {NUM_TRIALS} samples per alpha, alphas={ALPHAS}")
    gen = torch.Generator().manual_seed(SEED)
    byte_atoms = make_bsc(VOCAB_SIZE, N, gen).to(DEVICE)
    pos_atoms = make_bsc(K, N, gen).to(DEVICE)

    fact_gen = torch.Generator().manual_seed(SEED * 7)
    sample_gen = torch.Generator(device=DEVICE).manual_seed(SEED * 13)

    bernoulli_curves_a = {alpha: [] for alpha in ALPHAS}
    bernoulli_curves_b = {alpha: [] for alpha in ALPHAS}
    deterministic_curves_a = {alpha: [] for alpha in ALPHAS}
    deterministic_curves_b = {alpha: [] for alpha in ALPHAS}

    for trial in range(NUM_FACTS):
        facts = torch.randint(0, VOCAB_SIZE, (K,), generator=fact_gen).to(DEVICE)
        edit_pos = int(torch.randint(0, K, (1,), generator=fact_gen).item())
        byte_a = int(facts[edit_pos].item())
        byte_b = int(torch.randint(0, VOCAB_SIZE, (1,), generator=fact_gen).item())
        if byte_b == byte_a:
            byte_b = (byte_b + 1) % VOCAB_SIZE

        # Build base bundle (with byte_a at edit_pos)
        base = build_bundle(byte_atoms, pos_atoms, facts)
        atom_a = byte_atoms[byte_a]
        atom_b = byte_atoms[byte_b]

        for alpha in ALPHAS:
            # Bernoulli mix: average over NUM_TRIALS samples
            p_a_sum = 0.0
            p_b_sum = 0.0
            for _ in range(NUM_TRIALS):
                mixed = bernoulli_mix_atom(atom_a, atom_b, alpha, sample_gen)
                edited = edit_bundle_at_position(base, byte_atoms, pos_atoms, edit_pos, atom_a, mixed)
                edited_signed = torch.sign(edited)
                edited_signed = torch.where(edited_signed == 0, torch.ones_like(edited_signed), edited_signed)
                P = query_byte_prob_at_position(edited_signed, byte_atoms, pos_atoms[edit_pos])
                p_a_sum += float(P[byte_a].item())
                p_b_sum += float(P[byte_b].item())
            bernoulli_curves_a[alpha].append(p_a_sum / NUM_TRIALS)
            bernoulli_curves_b[alpha].append(p_b_sum / NUM_TRIALS)

            # Deterministic blend (single sample, deterministic)
            blended = deterministic_blend_atom(atom_a, atom_b, alpha)
            edited_det = edit_bundle_at_position(base, byte_atoms, pos_atoms, edit_pos, atom_a, blended)
            edited_det_signed = torch.sign(edited_det)
            edited_det_signed = torch.where(edited_det_signed == 0, torch.ones_like(edited_det_signed), edited_det_signed)
            P_det = query_byte_prob_at_position(edited_det_signed, byte_atoms, pos_atoms[edit_pos])
            deterministic_curves_a[alpha].append(float(P_det[byte_a].item()))
            deterministic_curves_b[alpha].append(float(P_det[byte_b].item()))

    # Report mean curves
    _say(f"\n  Bernoulli mix (population average across {NUM_TRIALS} samples per alpha):")
    for alpha in ALPHAS:
        ma = sum(bernoulli_curves_a[alpha]) / NUM_FACTS
        mb = sum(bernoulli_curves_b[alpha]) / NUM_FACTS
        _say(f"    alpha={alpha:.2f}: P(byte_A) mean = {ma:.3f}, P(byte_B) mean = {mb:.3f}")

    _say(f"\n  Deterministic blend (single sample per alpha):")
    for alpha in ALPHAS:
        ma = sum(deterministic_curves_a[alpha]) / NUM_FACTS
        mb = sum(deterministic_curves_b[alpha]) / NUM_FACTS
        _say(f"    alpha={alpha:.2f}: P(byte_A) mean = {ma:.3f}, P(byte_B) mean = {mb:.3f}")

    # Compute step-jumps in deterministic vs Bernoulli at alpha=0.5
    # Step measure: max jump between adjacent alpha values (for byte_B trajectory)
    bern_b_means = [sum(bernoulli_curves_b[a])/NUM_FACTS for a in ALPHAS]
    det_b_means = [sum(deterministic_curves_b[a])/NUM_FACTS for a in ALPHAS]
    bern_max_jump = max(abs(bern_b_means[i+1] - bern_b_means[i]) for i in range(len(ALPHAS)-1))
    det_max_jump = max(abs(det_b_means[i+1] - det_b_means[i]) for i in range(len(ALPHAS)-1))
    _say(f"\n  Max alpha-to-alpha jump in P(byte_B):")
    _say(f"    Bernoulli mix:   {bern_max_jump:.4f}")
    _say(f"    Deterministic:   {det_max_jump:.4f}")

    if bern_max_jump < 0.15 and det_max_jump > 2 * bern_max_jump:
        _say(f"\n  PASS: Bernoulli mixing gives smooth trajectory; deterministic shows step.")
    elif bern_max_jump < 0.20:
        _say(f"\n  PARTIAL: Bernoulli is reasonably smooth.")
    else:
        _say(f"\n  WEAK: Bernoulli not smooth enough. Need FHRR.")

    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14e_continuous_edits_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps({
        "N": N, "K": K, "ALPHAS": ALPHAS, "NUM_TRIALS": NUM_TRIALS, "NUM_FACTS": NUM_FACTS,
        "bernoulli_b_means": bern_b_means, "deterministic_b_means": det_b_means,
        "bern_max_jump": bern_max_jump, "det_max_jump": det_max_jump,
    }, indent=2))


if __name__ == "__main__":
    main()
