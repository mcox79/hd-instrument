"""Wave 14.B: Resonator decomposition of 2-atom HDC bundles.

Pre-registered at notes/wave14b_preregistration.md. Three diagnostic
gates (binding invertibility, oracle resonator, full resonator) run
sequentially with hard halt-on-fail. Gate 3 has a pre-registered
falsification criterion of >= 50% recovery.

Task: recover (a, b) from c = a (*) p1 + b (*) p2 where (*) is
elementwise product and a, b are unknown atoms from a known codebook
of K = 32 bipolar vectors in dimension N = 4096. p1, p2 are fixed
random bipolar position codes.

This is the HDC-native version of the Wave 14.A shuffle Hopf idea:
decomposition via alternating projection instead of literal
deconcatenation.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import torch

# ---- Pre-registered configuration ----
SEED = 17
N = 4096
K = 32
M = 2  # bundle size (atoms per query)
NUM_TRIALS = 200
NUM_RESTARTS = 8
MAX_ITER = 100
CONV_TOL = 1e-6
BETA_INIT = 1.0
BETA_MULT = 1.2
BETA_MAX = 20.0


def _say(msg: str) -> None:
    print(msg, flush=True)


def build_codebook(gen: torch.Generator) -> torch.Tensor:
    """K random bipolar atoms in dimension N, shape (K, N)."""
    bits = torch.randint(0, 2, (K, N), generator=gen)
    return (bits * 2 - 1).to(torch.float32)


def build_positions(gen: torch.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    """Two random bipolar position codes p1, p2 in dimension N."""
    bits = torch.randint(0, 2, (2, N), generator=gen)
    pos = (bits * 2 - 1).to(torch.float32)
    return pos[0], pos[1]


def make_bundle(a: torch.Tensor, b: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor) -> torch.Tensor:
    """c = a (*) p1 + b (*) p2."""
    return a * p1 + b * p2


def cleanup_hard(v: torch.Tensor, codebook: torch.Tensor) -> tuple[torch.Tensor, int]:
    """Project v onto codebook by argmax cosine. Returns (atom, idx)."""
    scores = codebook @ v
    idx = int(scores.argmax().item())
    return codebook[idx], idx


def cleanup_soft(v: torch.Tensor, codebook: torch.Tensor, beta: float) -> torch.Tensor:
    """Soft projection: softmax-weighted superposition over codebook."""
    scores = (codebook @ v) / math.sqrt(N)
    weights = torch.softmax(beta * scores, dim=0)
    return weights @ codebook


def information_theoretic_check(codebook: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor) -> dict:
    """Empirically verify that distinct codebook pairs give distinguishable c-vectors."""
    same_overlaps = []
    diff_overlaps = []
    gen = torch.Generator().manual_seed(SEED + 7777)
    for _ in range(200):
        i = int(torch.randint(0, K, (1,), generator=gen).item())
        j = int(torch.randint(0, K, (1,), generator=gen).item())
        ii = int(torch.randint(0, K, (1,), generator=gen).item())
        jj = int(torch.randint(0, K, (1,), generator=gen).item())
        c1 = make_bundle(codebook[i], codebook[j], p1, p2)
        c2 = make_bundle(codebook[ii], codebook[jj], p1, p2)
        ov = float((c1 @ c2) / (c1.norm() * c2.norm() + 1e-12))
        if (i, j) == (ii, jj):
            same_overlaps.append(ov)
        else:
            diff_overlaps.append(ov)
    same = sum(same_overlaps) / max(len(same_overlaps), 1) if same_overlaps else None
    diff = sum(diff_overlaps) / max(len(diff_overlaps), 1) if diff_overlaps else None
    diff_max = max(diff_overlaps) if diff_overlaps else None
    return {"same_mean": same, "diff_mean": diff, "diff_max": diff_max,
            "n_same": len(same_overlaps), "n_diff": len(diff_overlaps)}


def gate1_binding_invertibility(codebook: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor) -> dict:
    """Given true a, deterministic algebraic recovery of b must be 100%."""
    correct = 0
    gen = torch.Generator().manual_seed(SEED + 100)
    for _ in range(NUM_TRIALS):
        i = int(torch.randint(0, K, (1,), generator=gen).item())
        j = int(torch.randint(0, K, (1,), generator=gen).item())
        a = codebook[i]
        b = codebook[j]
        c = make_bundle(a, b, p1, p2)
        b_hat_raw = (c - a * p1) * p2  # should equal b exactly
        _, b_hat_idx = cleanup_hard(b_hat_raw, codebook)
        if b_hat_idx == j:
            correct += 1
    return {"correct": correct, "total": NUM_TRIALS, "rate": correct / NUM_TRIALS}


def resonator_step_hard(a_hat: torch.Tensor, b_hat: torch.Tensor, c: torch.Tensor,
                       p1: torch.Tensor, p2: torch.Tensor,
                       codebook: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, int, int]:
    """One resonator step with HARD codebook projection. Returns (a, b, a_idx, b_idx)."""
    a_candidate = (c - b_hat * p2) * p1
    a_new, a_idx = cleanup_hard(a_candidate, codebook)
    b_candidate = (c - a_new * p1) * p2
    b_new, b_idx = cleanup_hard(b_candidate, codebook)
    return a_new, b_new, a_idx, b_idx


def run_resonator_hard(c: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor,
                      codebook: torch.Tensor, gen: torch.Generator) -> tuple[int, int]:
    """Multi-restart hard-cleanup resonator. Returns (a_idx, b_idx) best by score."""
    best_score = -float("inf")
    best_a, best_b = -1, -1
    for restart in range(NUM_RESTARTS):
        # Initialize from random codebook atoms
        a_init_idx = int(torch.randint(0, K, (1,), generator=gen).item())
        b_init_idx = int(torch.randint(0, K, (1,), generator=gen).item())
        a_hat = codebook[a_init_idx].clone()
        b_hat = codebook[b_init_idx].clone()
        prev_a_idx, prev_b_idx = -1, -1
        for it in range(MAX_ITER):
            a_hat, b_hat, a_idx, b_idx = resonator_step_hard(a_hat, b_hat, c, p1, p2, codebook)
            if a_idx == prev_a_idx and b_idx == prev_b_idx:
                break
            prev_a_idx, prev_b_idx = a_idx, b_idx
        # Score this restart by reconstruction
        c_recon = make_bundle(a_hat, b_hat, p1, p2)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_a, best_b = a_idx, b_idx
    return best_a, best_b


def gate2_oracle_resonator(codebook: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor) -> dict:
    """Hard-cleanup resonator. With perfect projection, must converge on >= 95% of trials."""
    correct = 0
    correct_either = 0
    gen = torch.Generator().manual_seed(SEED + 200)
    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 200 + trial)
        i = int(torch.randint(0, K, (1,), generator=tg).item())
        j = int(torch.randint(0, K, (1,), generator=tg).item())
        a = codebook[i]
        b = codebook[j]
        c = make_bundle(a, b, p1, p2)
        a_idx, b_idx = run_resonator_hard(c, p1, p2, codebook, tg)
        # Symmetric: (i,j) and (j,i) both correct (bundle is symmetric? NO - p1 vs p2 distinguish)
        # Actually c = a*p1 + b*p2 is NOT symmetric in (a,b). Order matters.
        if a_idx == i and b_idx == j:
            correct += 1
        if a_idx == i or b_idx == j:
            correct_either += 1
    return {"correct_both": correct, "correct_either": correct_either, "total": NUM_TRIALS,
            "rate_both": correct / NUM_TRIALS, "rate_either": correct_either / NUM_TRIALS}


def resonator_step_soft(a_hat: torch.Tensor, b_hat: torch.Tensor, c: torch.Tensor,
                       p1: torch.Tensor, p2: torch.Tensor,
                       codebook: torch.Tensor, beta: float) -> tuple[torch.Tensor, torch.Tensor]:
    """One resonator step with SOFT cleanup at temperature beta."""
    a_candidate = (c - b_hat * p2) * p1
    a_new = cleanup_soft(a_candidate, codebook, beta)
    b_candidate = (c - a_new * p1) * p2
    b_new = cleanup_soft(b_candidate, codebook, beta)
    return a_new, b_new


def run_resonator_soft(c: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor,
                      codebook: torch.Tensor, gen: torch.Generator) -> tuple[int, int]:
    """Multi-restart soft-cleanup resonator with temperature schedule."""
    best_score = -float("inf")
    best_a, best_b = -1, -1
    for restart in range(NUM_RESTARTS):
        a_init_idx = int(torch.randint(0, K, (1,), generator=gen).item())
        b_init_idx = int(torch.randint(0, K, (1,), generator=gen).item())
        a_hat = codebook[a_init_idx].clone()
        b_hat = codebook[b_init_idx].clone()
        beta = BETA_INIT
        prev_a_hat = a_hat.clone()
        for it in range(MAX_ITER):
            a_hat, b_hat = resonator_step_soft(a_hat, b_hat, c, p1, p2, codebook, beta)
            beta = min(beta * BETA_MULT, BETA_MAX)
            delta = float((a_hat - prev_a_hat).abs().mean())
            if delta < CONV_TOL and beta >= BETA_MAX:
                break
            prev_a_hat = a_hat.clone()
        # Final hard projection to read off indices
        _, a_idx = cleanup_hard(a_hat, codebook)
        _, b_idx = cleanup_hard(b_hat, codebook)
        a_final = codebook[a_idx]
        b_final = codebook[b_idx]
        c_recon = make_bundle(a_final, b_final, p1, p2)
        score = float((c @ c_recon) / (c.norm() * c_recon.norm() + 1e-12))
        if score > best_score:
            best_score = score
            best_a, best_b = a_idx, b_idx
    return best_a, best_b


def gate3_full_resonator(codebook: torch.Tensor, p1: torch.Tensor, p2: torch.Tensor) -> dict:
    """Soft-cleanup resonator. Pre-registered pass: >= 50% recovery (both atoms)."""
    correct = 0
    correct_either = 0
    per_trial = []
    gen = torch.Generator().manual_seed(SEED + 300)
    for trial in range(NUM_TRIALS):
        tg = torch.Generator().manual_seed(SEED + 300 + trial)
        i = int(torch.randint(0, K, (1,), generator=tg).item())
        j = int(torch.randint(0, K, (1,), generator=tg).item())
        a = codebook[i]
        b = codebook[j]
        c = make_bundle(a, b, p1, p2)
        a_idx, b_idx = run_resonator_soft(c, p1, p2, codebook, tg)
        ok_both = (a_idx == i and b_idx == j)
        ok_either = (a_idx == i or b_idx == j)
        per_trial.append({"trial": trial, "true_a": i, "true_b": j,
                          "pred_a": a_idx, "pred_b": b_idx, "both": ok_both})
        if ok_both:
            correct += 1
        if ok_either:
            correct_either += 1
    return {"correct_both": correct, "correct_either": correct_either, "total": NUM_TRIALS,
            "rate_both": correct / NUM_TRIALS, "rate_either": correct_either / NUM_TRIALS,
            "per_trial": per_trial[:20]}  # save first 20 for audit


def main() -> None:
    _say(f"Wave 14.B: Resonator decomposition diagnostics (pre-registered)")
    _say(f"  N={N}, K={K}, M={M}, restarts={NUM_RESTARTS}, trials={NUM_TRIALS}, seed={SEED}")
    _say(f"  Pre-reg falsification: Gate 3 must hit >= 50% recovery")

    gen = torch.Generator().manual_seed(SEED)
    codebook = build_codebook(gen)
    p1, p2 = build_positions(gen)
    _say(f"  codebook shape: {tuple(codebook.shape)}, p1 shape: {tuple(p1.shape)}")

    out = {"config": {"N": N, "K": K, "M": M, "restarts": NUM_RESTARTS,
                     "trials": NUM_TRIALS, "seed": SEED}}

    _say(f"\n--- Information-theoretic check ---")
    it_check = information_theoretic_check(codebook, p1, p2)
    _say(f"  Mean overlap of c with c' (distinct pairs): {it_check['diff_mean']:.4f}  (n={it_check['n_diff']})")
    _say(f"  Max overlap of c with c' (distinct pairs):  {it_check['diff_max']:.4f}")
    _say(f"  Expected: distinct-pair overlap << 1 (~{1.0/math.sqrt(N):.4f} std dev expected)")
    out["it_check"] = it_check
    if it_check["diff_max"] is not None and it_check["diff_max"] > 0.5:
        _say(f"  WARNING: distinct pairs have suspiciously high overlap. Information may not separate cleanly.")

    _say(f"\n--- Gate 1: Binding invertibility (must be 100%) ---")
    g1 = gate1_binding_invertibility(codebook, p1, p2)
    _say(f"  Recovery rate: {g1['correct']}/{g1['total']} = {100*g1['rate']:.1f}%")
    out["gate1"] = g1
    if g1["correct"] != g1["total"]:
        _say(f"  GATE 1 FAILED. Binding/unbinding implementation is wrong. HALTING.")
        _write_metrics(out)
        return
    _say(f"  GATE 1 PASS.")

    _say(f"\n--- Gate 2: Oracle resonator (hard cleanup, must be >= 95%) ---")
    g2 = gate2_oracle_resonator(codebook, p1, p2)
    _say(f"  Both correct:   {g2['correct_both']}/{g2['total']} = {100*g2['rate_both']:.1f}%")
    _say(f"  Either correct: {g2['correct_either']}/{g2['total']} = {100*g2['rate_either']:.1f}%")
    out["gate2"] = g2
    if g2["rate_both"] < 0.95:
        _say(f"  GATE 2 FAILED (< 95%). Alternating projection itself does not converge for this setup.")
        _say(f"  This is independent of cleanup softness. Reconsider the binding choice.")
        _write_metrics(out)
        return
    _say(f"  GATE 2 PASS.")

    _say(f"\n--- Gate 3: Full system (soft cleanup, pre-reg falsification >= 50%) ---")
    g3 = gate3_full_resonator(codebook, p1, p2)
    _say(f"  Both correct:   {g3['correct_both']}/{g3['total']} = {100*g3['rate_both']:.1f}%")
    _say(f"  Either correct: {g3['correct_either']}/{g3['total']} = {100*g3['rate_either']:.1f}%")
    out["gate3"] = g3

    _say(f"\n========= PRE-REGISTERED VERDICT =========")
    if g3["rate_both"] >= 0.50:
        _say(f"  HYPOTHESIS SUPPORTED. Gate 3 = {100*g3['rate_both']:.1f}% >= 50%.")
        _say(f"  Next: sweep M and K. Then continual-learning integration.")
        out["verdict"] = "supported"
    else:
        _say(f"  HYPOTHESIS REJECTED. Gate 3 = {100*g3['rate_both']:.1f}% < 50%.")
        _say(f"  Do NOT proceed to longer bundles or continual integration.")
        _say(f"  Reconsider whether resonator + Hadamard is the right primitive.")
        out["verdict"] = "rejected"

    _write_metrics(out)


def _write_metrics(out: dict) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "data" / "exp_wave14b_resonator_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(out, indent=2, default=str))
    _say(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    t0 = time.perf_counter()
    main()
    dt = time.perf_counter() - t0
    _say(f"\nWall time: {dt:.1f}s")
