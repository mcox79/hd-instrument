"""Iterative attractor cleanup primitive (brain-inspired; mech 5 broad-exploration drill 2026-06-22).

Substrate-native iterative attractor dynamics replacing one-shot argmax cleanup.

Mechanism (convergent across 4+ brain mechanisms; cited):
  - CAN-bump dynamics (Amari; Wilson-Cowan): bump-state settles into nearest basin via lateral
    excitation + global inhibition; iterative not single-shot.
  - DG-CA3 pattern completion (Marr; Treves-Rolls): recurrent collaterals iteratively pull a
    noisy/partial input toward the stored attractor.
  - Ring attractors (head-direction; Skaggs-Knierim): continuous-manifold of fixed points;
    settling via short-range excitation.
  - Modern dense associative memory (Krotov-Hopfield 2016; Ramsauer 2021): exponential capacity
    with softmax-attractor update rule; substrate-as-MHN reframing per Saxena-Bartlett 2024
    arXiv:2212.01196 "VSA Finite State Machines in Attractor Neural Networks".

Replaces: single-shot argmax over codebook (the failure mode in n4 / n9 / n10 / p1 partials).
Forward-only; no backprop; substrate-native; composes with existing codebook + HD vectors.

PUBLIC API (substrate-flat; cell-author drop-in):
  iterative_cleanup(query, codebook, *, temp=1.0, max_steps=8, tol=1e-3, return_trace=False)
  attractor_basin_robustness(codebook, target_idx, noise_sigmas, *, temp=1.0, max_steps=8,
                              seed=0, n_trials=50)

Key design notes:
  - Codebook is assumed L2-normalized (cosine-similarity attractor). We renormalize internally.
  - state at step t+1 = renormalize(softmax(temp * scores(state_t @ codebook.T)) @ codebook).
    softmax over codebook scores = soft attractor weights; temp -> infty recovers argmax (hard
    attractor); temp -> 0 is uniform (no pull). LOW temp here means LOW softmax temperature
    (= HIGH beta = sharper) and HIGH temp = LESS sharp; we use the convention
    "scores = temp * (state @ codebook.T)" so larger temp = sharper basin.
  - Convergence by L2 step-size: ||state_{t+1} - state_t|| < tol * sqrt(D).
  - Returns final state + diagnostics: n_iterations, converged_bool, final_argmax_idx.
"""
from __future__ import annotations
from typing import Optional
import numpy as np


def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalize (B, D) or (D,) -> same shape; safe against zero rows."""
    if X.ndim == 1:
        n = float(np.linalg.norm(X) + eps)
        return (X / n).astype(np.float32)
    n = np.linalg.norm(X, axis=1, keepdims=True) + eps
    return (X / n).astype(np.float32)


def _softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax along axis."""
    z = z - z.max(axis=axis, keepdims=True)
    ez = np.exp(z.astype(np.float64))
    return (ez / (ez.sum(axis=axis, keepdims=True) + 1e-30)).astype(np.float32)


def iterative_cleanup(
    query: np.ndarray,
    codebook: np.ndarray,
    *,
    temp: float = 1.0,
    max_steps: int = 8,
    tol: float = 1e-3,
    return_trace: bool = False,
    scale_by_sqrt_d: bool = True,
):
    """Iterative soft-attractor cleanup of query against codebook.

    Args:
        query: shape (B, D) or (D,). Noisy cue.
        codebook: shape (M, D). Stored attractors (need not be pre-normalized; we normalize).
        temp: softmax inverse-temperature multiplier. Higher = sharper (closer to argmax).
              With `scale_by_sqrt_d=True` (default), effective beta = temp * sqrt(D)
              (the standard attention-scaling trick; Ramsauer 2021 + Vaswani 2017). At D=4096
              this makes temp=4.0 give effective beta ~256, which is sharp enough to recover
              attractors with random Gaussian L2-normalized codebooks where cosine gap is
              ~1/sqrt(D). Set False to use raw temp (legacy / unit-test).
        max_steps: cap on iterations. Brain reference: theta cycles ~ 7-10 gamma sub-cycles.
        tol: per-D convergence threshold. Stop when ||x_t+1 - x_t|| < tol * sqrt(D).
        return_trace: if True, also return per-iteration L2 step sizes.
        scale_by_sqrt_d: scale effective inverse-temperature by sqrt(D) (default True).

    Returns:
        dict with keys:
          state: shape (B, D) final cleaned state (L2-normalized)
          argmax_idx: shape (B,) int — nearest codebook entry to final state
          n_iterations: int — number of update steps actually taken
          converged: bool — True if step-size fell below tol before max_steps
          trace (optional): list of per-step L2 distances
    """
    squeeze = query.ndim == 1
    if squeeze:
        query = query[None, :]
    query = query.astype(np.float32)
    codebook = codebook.astype(np.float32)
    cb_norm = _l2_normalize(codebook)
    state = _l2_normalize(query)
    D = state.shape[1]
    effective_beta = temp * float(np.sqrt(D)) if scale_by_sqrt_d else temp
    step_threshold = tol * float(np.sqrt(D))
    trace = []
    converged = False
    steps_taken = 0
    for t in range(max_steps):
        scores = effective_beta * (state @ cb_norm.T)
        weights = _softmax(scores, axis=1)  # (B, M) soft attractor weights
        new_state = _l2_normalize(weights @ cb_norm)
        step_dist = float(np.mean(np.linalg.norm(new_state - state, axis=1)))
        trace.append(step_dist)
        state = new_state
        steps_taken = t + 1
        if step_dist < step_threshold:
            converged = True
            break
    # nearest codebook idx
    final_scores = state @ cb_norm.T
    argmax_idx = np.argmax(final_scores, axis=1).astype(np.int64)
    if squeeze:
        state = state[0]
        argmax_idx = int(argmax_idx[0])
    result = {
        "state": state,
        "argmax_idx": argmax_idx,
        "n_iterations": steps_taken,
        "converged": converged,
    }
    if return_trace:
        result["trace"] = trace
    return result


def argmax_cleanup(query: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Reference: single-step argmax cleanup (the substrate baseline)."""
    query = _l2_normalize(query.astype(np.float32))
    cb_norm = _l2_normalize(codebook.astype(np.float32))
    if query.ndim == 1:
        scores = query @ cb_norm.T
        return int(np.argmax(scores))
    scores = query @ cb_norm.T
    return np.argmax(scores, axis=1).astype(np.int64)


def attractor_basin_robustness(
    codebook: np.ndarray,
    target_indices: np.ndarray,
    noise_sigmas,
    *,
    temp: float = 1.0,
    max_steps: int = 8,
    seed: int = 0,
    n_trials: int = 50,
):
    """Sweep noise levels; measure fraction of trials that recover target index after cleanup.

    Returns dict: {sigma: float -> recall_at_1 across n_trials*len(target_indices)}.
    """
    g = np.random.default_rng(seed)
    codebook = codebook.astype(np.float32)
    cb_norm = _l2_normalize(codebook)
    M, D = cb_norm.shape
    target_indices = np.asarray(target_indices, dtype=np.int64)
    results = {}
    for sigma in noise_sigmas:
        n_correct = 0
        n_total = 0
        for tgt_i in target_indices:
            target = cb_norm[tgt_i]
            for _ in range(n_trials):
                noise = sigma * g.standard_normal(D).astype(np.float32)
                cue = target + noise
                out = iterative_cleanup(cue, cb_norm, temp=temp, max_steps=max_steps)
                if int(out["argmax_idx"]) == int(tgt_i):
                    n_correct += 1
                n_total += 1
        results[float(sigma)] = float(n_correct) / max(n_total, 1)
    return results


def _selftest() -> None:
    """Mechanism selftest: zero-noise identity, basin convergence, argmax-limit, soft-vs-hard."""
    g = np.random.default_rng(0)
    M, D = 64, 256
    cb = g.standard_normal((M, D)).astype(np.float32)
    cb = _l2_normalize(cb)
    # 1. Zero-noise: codebook entry recovers itself
    for i in [0, 7, 33]:
        out = iterative_cleanup(cb[i].copy(), cb, temp=10.0, max_steps=4)
        assert int(out["argmax_idx"]) == i, f"zero-noise recovery failed at i={i} -> {out['argmax_idx']}"
    # 2. Low-noise: should still recover
    noise = 0.05 * g.standard_normal(D).astype(np.float32)
    out = iterative_cleanup(cb[5] + noise, cb, temp=20.0, max_steps=6)
    assert int(out["argmax_idx"]) == 5, f"low-noise recovery failed: got {out['argmax_idx']}"
    # 3. High-temp limit equivalent to argmax for moderate noise
    noise = 0.1 * g.standard_normal(D).astype(np.float32)
    cue = cb[10] + noise
    iter_out = iterative_cleanup(cue, cb, temp=100.0, max_steps=1)
    argmax_out = argmax_cleanup(cue, cb)
    assert int(iter_out["argmax_idx"]) == int(argmax_out), \
        f"high-temp 1-step != argmax: iter={iter_out['argmax_idx']} argmax={argmax_out}"
    # 4. Iterative converges (step-size decreases monotonically on average for clean cues)
    out = iterative_cleanup(cb[20] + 0.2 * g.standard_normal(D).astype(np.float32),
                            cb, temp=8.0, max_steps=12, return_trace=True)
    assert out["n_iterations"] >= 1
    # final step-size must be smaller than first step-size for typical attractor dynamics
    trace = out["trace"]
    assert trace[-1] <= trace[0] * 1.1, f"trace not contracting: first={trace[0]} last={trace[-1]}"
    # 5. Batched shape sanity
    B = 7
    cues = cb[:B] + 0.1 * g.standard_normal((B, D)).astype(np.float32)
    out = iterative_cleanup(cues, cb, temp=10.0, max_steps=5)
    assert out["state"].shape == (B, D)
    assert out["argmax_idx"].shape == (B,)
    # 6. argmax_cleanup matches reference for clean inputs
    assert int(argmax_cleanup(cb[3], cb)) == 3
    # 7. basin_robustness returns sane structure
    rob = attractor_basin_robustness(cb, np.arange(8), [0.0, 0.2], temp=10.0,
                                     max_steps=4, seed=1, n_trials=10)
    assert 0.0 in rob and 0.2 in rob
    assert rob[0.0] >= 0.95, f"zero-noise robustness low: {rob[0.0]}"
    print("[hdlab.iterative_attractor selftest] PASS: identity-recovery + low-noise + argmax-limit "
          "+ contracting-trace + batched-shape + basin-robustness OK", flush=True)


if __name__ == "__main__":
    _selftest()
