"""Signal-stage profiling: where in the pipeline do we lose information?

Trains the best baseline and the best combined config, then runs a diagnostic
that decomposes the bits/char loss across three stages:

  Stage A: Bundle representation. How well can we recover the K context bytes
           from the bundle alone (by unbinding with each position atom)?
  Stage B: W's hypervector prediction. After training, what fraction of test
           positions have W @ context most-similar to the correct byte atom?
           What is the distribution of margins (correct_sim - max_wrong_sim)?
  Stage C: Softmax cleanup. Given W's hypervector output, how does the
           softmax-induced loss decompose into argmax-correctness +
           confidence-calibration components?

Tells us which stage to attack to close the 0.45-bit gap to the transformer.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path

import torch

from hdlab import atoms, binding, tracing




DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 17
VOCAB_SIZE = 256
PAD_BYTE = 0
BATCH_SIZE = 64


def _say(msg: str) -> None:
    print(msg, flush=True)


def load_corpus() -> bytes:
    repo = Path(__file__).resolve().parent.parent
    files = [
        repo / "PLAN.md", repo / "NEXT_PHASE.md", repo / "README.md",
        repo / "PROGRESS.md", repo / "RESULTS.md", repo / "CLAUDE.md",
    ]
    parts = []
    for f in files:
        if f.exists():
            parts.append(f.read_bytes())
            parts.append(b"\n\n")
    return b"".join(parts)


def train_test_split(corpus: bytes, train_frac: float = 0.8) -> tuple[bytes, bytes]:
    cut = int(len(corpus) * train_frac)
    return corpus[:cut], corpus[cut:]


def _build_context_bundles_batch(byte_atoms, pos_atoms, indices):
    bound = byte_atoms[indices] * pos_atoms.unsqueeze(0)
    summed = bound.sum(dim=1)
    mag = summed.abs().clamp(min=1e-8)
    return summed / mag.to(summed.dtype)


def _predict_batch(W, ctxs, byte_atoms, beta):
    n = ctxs.shape[1]
    q = ctxs @ W.T
    sims = (byte_atoms.conj() @ q.T).real / n
    return torch.softmax(beta * sims, dim=0), sims


def train_one_pass(
    train: bytes, n: int, k: int, arousal: float, beta: float,
    seed: int, batch_size: int = BATCH_SIZE,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Train W with batched delta rule, return (W, byte_atoms, pos_atoms)."""
    quiet = tracing.TraceBus(enabled=False)
    with tracing.using(quiet):
        gen = torch.Generator().manual_seed(seed)
        byte_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(VOCAB_SIZE)]).to(DEVICE)
        pos_atoms = torch.stack([atoms.make_atom_fhrr(n, gen) for _ in range(k)]).to(DEVICE)
        W = torch.zeros((n, n), dtype=torch.complex64, device=DEVICE)

        pad = bytes([PAD_BYTE]) * k
        padded = pad + train
        T = len(padded) - k
        bytes_t = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
        offsets = torch.arange(k - 1, -1, -1, device=DEVICE)
        positions = torch.arange(T, device=DEVICE)
        idx = bytes_t[positions.unsqueeze(1) + offsets.unsqueeze(0)]
        tgt = bytes_t[positions + k]

        for batch_start in range(0, T, batch_size):
            be = min(batch_start + batch_size, T)
            idx_batch = idx[batch_start:be]
            tgt_batch = tgt[batch_start:be]
            ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)
            probs, _ = _predict_batch(W, ctxs, byte_atoms, beta)
            targets = byte_atoms[tgt_batch]
            expected = probs.T.to(byte_atoms.dtype) @ byte_atoms
            errors = targets - expected
            dW = errors.T @ ctxs.conj() / n
            W.add_(dW, alpha=arousal)

        return W, byte_atoms, pos_atoms


def profile_stages(
    W: torch.Tensor, byte_atoms: torch.Tensor, pos_atoms: torch.Tensor,
    test_bytes: bytes, k: int, beta: float, batch_size: int = BATCH_SIZE,
) -> dict:
    """Decompose bits/char loss into Stage A/B/C contributions."""
    n = W.shape[0]
    pad = bytes([PAD_BYTE]) * k
    padded = pad + test_bytes
    T = len(padded) - k
    bytes_t = torch.tensor(list(padded), dtype=torch.long).to(DEVICE)
    offsets = torch.arange(k - 1, -1, -1, device=DEVICE)
    positions = torch.arange(T, device=DEVICE)
    idx = bytes_t[positions.unsqueeze(1) + offsets.unsqueeze(0)]
    tgt = bytes_t[positions + k]

    # ------- Stage A: bundle recovery -------
    # For each context position j, unbind ctx by pos_atoms[j] and cleanup. Check if
    # the recovered byte matches the actual byte at that position.
    stage_a_correct = [0] * k
    stage_a_total = 0

    # ------- Stage B: W hypervector accuracy -------
    # argmax accuracy on next-byte prediction, and margin distribution.
    stage_b_argmax_correct = 0
    margins = []
    correct_sims = []  # sim of W@ctx to correct byte
    max_wrong_sims = []  # max sim of W@ctx to any wrong byte

    # ------- Stage C: softmax-induced bits decomposition -------
    bits_on_argmax_correct = []  # bits per char when W's argmax is right
    bits_on_argmax_wrong = []  # bits per char when W's argmax is wrong
    p_correct_when_argmax_correct = []
    p_correct_when_argmax_wrong = []

    for bs in range(0, T, batch_size):
        be = min(bs + batch_size, T)
        idx_batch = idx[bs:be]
        tgt_batch = tgt[bs:be]
        B = idx_batch.shape[0]
        stage_a_total += B

        ctxs = _build_context_bundles_batch(byte_atoms, pos_atoms, idx_batch)

        # Stage A: per-position bundle recovery via unbinding.
        for j in range(k):
            # unbind ctxs by pos_atoms[j]: multiply by conjugate elementwise.
            recovered = ctxs * pos_atoms[j].conj().unsqueeze(0)  # (B, N)
            sims_a = (byte_atoms.conj() @ recovered.T).real / n  # (V, B)
            argmax_a = sims_a.argmax(dim=0)  # (B,)
            true_byte_at_j = idx_batch[:, j]  # (B,) — byte at position j of context
            stage_a_correct[j] += int((argmax_a == true_byte_at_j).sum())

        # Stage B + C: W's hypervector prediction.
        probs, sims = _predict_batch(W, ctxs, byte_atoms, beta)  # probs (V,B), sims (V,B)
        argmax_pred = sims.argmax(dim=0)  # (B,)
        correct_mask = argmax_pred == tgt_batch
        stage_b_argmax_correct += int(correct_mask.sum())

        true_sims = sims.gather(0, tgt_batch.unsqueeze(0)).squeeze(0)  # (B,)
        masked = sims.clone()
        masked.scatter_(0, tgt_batch.unsqueeze(0), float("-inf"))
        max_wrong = masked.max(dim=0).values  # (B,)
        batch_margins = true_sims - max_wrong  # (B,)
        margins.extend(batch_margins.tolist())
        correct_sims.extend(true_sims.tolist())
        max_wrong_sims.extend(max_wrong.tolist())

        # Stage C: bits and P(correct).
        p_true = probs.gather(0, tgt_batch.unsqueeze(0)).squeeze(0).clamp(min=1e-12)
        bits = -torch.log2(p_true)
        for i in range(B):
            if bool(correct_mask[i]):
                bits_on_argmax_correct.append(float(bits[i]))
                p_correct_when_argmax_correct.append(float(p_true[i]))
            else:
                bits_on_argmax_wrong.append(float(bits[i]))
                p_correct_when_argmax_wrong.append(float(p_true[i]))

    stage_a_rates = [c / stage_a_total for c in stage_a_correct]
    stage_b_acc = stage_b_argmax_correct / stage_a_total

    overall_bits = (sum(bits_on_argmax_correct) + sum(bits_on_argmax_wrong)) / stage_a_total

    return {
        "T_test": stage_a_total,
        "stage_a_recovery_per_position": stage_a_rates,
        "stage_a_recovery_mean": sum(stage_a_rates) / len(stage_a_rates),
        "stage_b_argmax_accuracy": stage_b_acc,
        "stage_b_margin_mean": sum(margins) / len(margins),
        "stage_b_margin_median": sorted(margins)[len(margins) // 2],
        "stage_b_margin_pct_positive": sum(1 for m in margins if m > 0) / len(margins),
        "stage_b_correct_sim_mean": sum(correct_sims) / len(correct_sims),
        "stage_b_max_wrong_sim_mean": sum(max_wrong_sims) / len(max_wrong_sims),
        "stage_c_bits_overall": overall_bits,
        "stage_c_bits_when_argmax_correct": (
            sum(bits_on_argmax_correct) / max(len(bits_on_argmax_correct), 1)
        ),
        "stage_c_bits_when_argmax_wrong": (
            sum(bits_on_argmax_wrong) / max(len(bits_on_argmax_wrong), 1)
        ),
        "stage_c_pcorrect_when_argmax_correct": (
            sum(p_correct_when_argmax_correct) / max(len(p_correct_when_argmax_correct), 1)
        ),
        "stage_c_pcorrect_when_argmax_wrong": (
            sum(p_correct_when_argmax_wrong) / max(len(p_correct_when_argmax_wrong), 1)
        ),
        "fraction_argmax_correct": len(bits_on_argmax_correct) / stage_a_total,
        "fraction_argmax_wrong": len(bits_on_argmax_wrong) / stage_a_total,
    }


def upper_bound_perfect_cleanup(profile: dict) -> dict:
    """If we had perfect cleanup (1.0 on correct, 0 on wrong), what bits/char?

    Conditional on W's argmax accuracy. When argmax is correct: 0 bits (with perfect cleanup).
    When argmax is wrong: with the wrong byte getting all probability, infinite bits — but in
    a "best-effort soft cleanup" approximation, the loss is bounded by the entropy of the
    near-miss distribution.

    Reports two upper bounds:
      (a) "oracle argmax + uniform fallback": correct -> 0 bits, wrong -> log2(255) bits
      (b) "oracle argmax + current softmax fallback for wrongs": use measured wrong-case bits
    """
    frac_correct = profile["fraction_argmax_correct"]
    frac_wrong = profile["fraction_argmax_wrong"]
    fallback_wrong_uniform = math.log2(VOCAB_SIZE - 1)  # ≈ 7.99 bits
    measured_wrong = profile["stage_c_bits_when_argmax_wrong"]

    bound_a = frac_correct * 0.0 + frac_wrong * fallback_wrong_uniform
    bound_b = frac_correct * 0.0 + frac_wrong * measured_wrong

    return {
        "perfect_cleanup_if_argmax_kept": bound_b,
        "perfect_cleanup_if_argmax_correct_else_uniform": bound_a,
        "current_bits": profile["stage_c_bits_overall"],
        "lift_from_perfect_cleanup": profile["stage_c_bits_overall"] - bound_b,
    }


def main() -> None:
    _say("Loading corpus...")
    corpus = load_corpus()
    train, test = train_test_split(corpus, 0.8)
    _say(f"  train={len(train)} bytes, test={len(test)} bytes")

    # Profile two configurations: baseline and best-so-far.
    configs = [
        ("baseline N=1024", 1024, 4, 0.3, 8.0),
        ("larger N=4096", 4096, 4, 0.3, 8.0),
    ]

    all_profiles = {}
    for label, n, k, arousal, beta in configs:
        _say(f"\n===== {label} =====")
        _say(f"Training W (N={n}, K={k}, arousal={arousal}, beta={beta})...")
        t0 = time.perf_counter()
        W, byte_atoms, pos_atoms = train_one_pass(train, n, k, arousal, beta, SEED)
        _say(f"  trained in {time.perf_counter() - t0:.1f}s")

        _say("Profiling stages...")
        t0 = time.perf_counter()
        profile = profile_stages(W, byte_atoms, pos_atoms, test, k, beta)
        _say(f"  profiled in {time.perf_counter() - t0:.1f}s")

        cleanup_bounds = upper_bound_perfect_cleanup(profile)

        _say(f"\n--- {label} results ---")
        _say(f"  Overall test bits/char: {profile['stage_c_bits_overall']:.4f}")
        _say(f"")
        _say(f"  STAGE A - Bundle recovery (can we extract context bytes from the bundle?):")
        _say(f"    Per-position recovery rate (most-recent -> oldest):")
        for j, rate in enumerate(profile['stage_a_recovery_per_position']):
            _say(f"      position j={j}: {rate:.3f}  (chance = {1/VOCAB_SIZE:.4f})")
        _say(f"    Mean: {profile['stage_a_recovery_mean']:.3f}")
        _say(f"")
        _say(f"  STAGE B - W's hypervector prediction:")
        _say(f"    Argmax accuracy (W's pick == true byte): {profile['stage_b_argmax_accuracy']:.3f}  (chance = {1/VOCAB_SIZE:.4f})")
        _say(f"    Mean correct_sim:      {profile['stage_b_correct_sim_mean']:.4f}")
        _say(f"    Mean max_wrong_sim:    {profile['stage_b_max_wrong_sim_mean']:.4f}")
        _say(f"    Mean margin:           {profile['stage_b_margin_mean']:.4f}")
        _say(f"    Median margin:         {profile['stage_b_margin_median']:.4f}")
        _say(f"    Fraction with margin > 0 (argmax correct): {profile['stage_b_margin_pct_positive']:.3f}")
        _say(f"")
        _say(f"  STAGE C - Softmax bits decomposition:")
        _say(f"    Bits/char when argmax is CORRECT: {profile['stage_c_bits_when_argmax_correct']:.4f}")
        _say(f"      P(correct) on these:            {profile['stage_c_pcorrect_when_argmax_correct']:.4f}")
        _say(f"    Bits/char when argmax is WRONG:   {profile['stage_c_bits_when_argmax_wrong']:.4f}")
        _say(f"      P(correct) on these:            {profile['stage_c_pcorrect_when_argmax_wrong']:.4f}")
        _say(f"")
        _say(f"  PERFECT-CLEANUP BOUND (if softmax converted argmax to 1.0 prob):")
        _say(f"    Bits/char: {cleanup_bounds['perfect_cleanup_if_argmax_kept']:.4f}")
        _say(f"    Lift achievable from better cleanup alone: {cleanup_bounds['lift_from_perfect_cleanup']:.4f}")

        all_profiles[label] = {**profile, "cleanup_bounds": cleanup_bounds}

    _say("\n========== SUMMARY ==========")
    _say(f"{'Config':<25s} {'Test bpc':>10s} {'Bundle recv':>12s} {'W argmax':>10s} {'Margin>0':>10s} {'Perfect-cu':>11s}")
    for label, p in all_profiles.items():
        _say(
            f"  {label:<25s} {p['stage_c_bits_overall']:>10.4f} "
            f"{p['stage_a_recovery_mean']:>12.3f} "
            f"{p['stage_b_argmax_accuracy']:>10.3f} "
            f"{p['stage_b_margin_pct_positive']:>10.3f} "
            f"{p['cleanup_bounds']['perfect_cleanup_if_argmax_kept']:>11.4f}"
        )

    out = {
        "seed": SEED,
        "profiles": all_profiles,
    }
    out_path = Path(__file__).resolve().parent.parent / "data" / "exp_signal_profile"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_path / 'metrics.json'}")


if __name__ == "__main__":
    main()
