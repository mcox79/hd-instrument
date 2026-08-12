"""Substrate-native excitability tensor E[i] (per-atom importance signal).

The "this matters" signal that is ORTHOGONAL to weight magnitude |W[i]|.
Brain analog: CREB / synaptic-tag-and-capture / spine-stability proxy. The
substrate-product reading per cortex 4x drill 2026-06-26: every cortex-class
failure (Cell B / STC / cold-storage) tried to read importance off |W| (the
noisy thing the substrate writes into); E is the separate dial.

Mechanism (NumPy; no torch dependency; matches associative-memory cells):
  E[i] in [0, 1] per atom
  on_retrieval: E[i] <- (1 - eta) * E[i] + eta * use_signal      (EWMA bump)
  slow_decay:   E[i] <- E[i] * decay_per_step                    (timescale)
  novelty_seed: E[i] <- max(E[i], seed_value) when atom first written

ASCII-only. No emojis. No em-dashes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class EConfig:
    """Excitability tracker hyperparameters.

    eta:       EWMA learn-rate on retrieval bumps (default 0.1).
    decay:     multiplicative slow-decay per time step (default 0.999).
    seed_new:  initial E[i] for freshly-written atoms (default 0.5).
    floor:     lower clamp on E[i] (default 0.0).
    ceiling:   upper clamp on E[i] (default 1.0).
    """
    eta: float = 0.1
    decay: float = 0.999
    seed_new: float = 0.5
    floor: float = 0.0
    ceiling: float = 1.0


def init_E(n_atoms: int) -> np.ndarray:
    """Allocate the per-atom excitability tensor; starts at zeros (no use yet)."""
    if n_atoms <= 0:
        raise ValueError(f"n_atoms must be positive; got {n_atoms}")
    return np.zeros(n_atoms, dtype=np.float64)


def seed_on_write(E: np.ndarray, idx: int, cfg: EConfig) -> None:
    """Bump E[idx] up to seed_new on first write (novelty seed)."""
    if E[idx] < cfg.seed_new:
        E[idx] = cfg.seed_new


def bump_on_retrieval(E: np.ndarray, idx: int, use_signal: float,
                      cfg: EConfig) -> None:
    """EWMA bump: E[i] <- (1 - eta) * E[i] + eta * use_signal."""
    if use_signal < 0.0 or use_signal > 1.0:
        raise ValueError(f"use_signal must be in [0,1]; got {use_signal}")
    new_val = (1.0 - cfg.eta) * E[idx] + cfg.eta * use_signal
    E[idx] = float(np.clip(new_val, cfg.floor, cfg.ceiling))


def slow_decay(E: np.ndarray, cfg: EConfig) -> None:
    """Multiplicative slow decay across all atoms (timescale)."""
    np.multiply(E, cfg.decay, out=E)
    np.clip(E, cfg.floor, cfg.ceiling, out=E)


def downscale_gate_by_E(W: np.ndarray, E: np.ndarray, scale: float,
                         threshold: float) -> int:
    """E-gated downscale: rows of W with E[i] < threshold get multiplied by scale.

    Returns the number of rows downscaled.
    """
    if not 0.0 <= scale <= 1.0:
        raise ValueError(f"scale must be in [0,1]; got {scale}")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0,1]; got {threshold}")
    mask = E < threshold
    n_hit = int(np.sum(mask))
    if n_hit > 0:
        W[mask, :] *= scale
    return n_hit


def downscale_gate_by_magnitude(W: np.ndarray, threshold_frac: float,
                                 scale: float) -> int:
    """Magnitude-only downscale (the BASELINE; reproduces Cell B failure).

    Rows of W whose L2-norm rank in the bottom threshold_frac get scaled.
    Returns count downscaled.
    """
    if not 0.0 <= scale <= 1.0:
        raise ValueError(f"scale must be in [0,1]; got {scale}")
    if not 0.0 < threshold_frac < 1.0:
        raise ValueError(f"threshold_frac must be in (0,1); got {threshold_frac}")
    norms = np.linalg.norm(W, axis=1)
    cutoff = float(np.quantile(norms, threshold_frac))
    mask = norms <= cutoff
    n_hit = int(np.sum(mask))
    if n_hit > 0:
        W[mask, :] *= scale
    return n_hit


def downscale_gate_random(W: np.ndarray, frac: float, scale: float,
                           rng: np.random.RandomState) -> int:
    """RANDOM control: downscale frac of rows chosen uniformly at random.

    Returns count downscaled.
    """
    if not 0.0 <= scale <= 1.0:
        raise ValueError(f"scale must be in [0,1]; got {scale}")
    if not 0.0 < frac < 1.0:
        raise ValueError(f"frac must be in (0,1); got {frac}")
    n_rows = W.shape[0]
    n_hit = int(round(frac * n_rows))
    idx = rng.choice(n_rows, size=n_hit, replace=False)
    W[idx, :] *= scale
    return n_hit


def correlation_E_vs_magnitude(E: np.ndarray, W: np.ndarray) -> float:
    """Pearson correlation between E[i] and ||W[i,:]||_2.

    Load-bearing: if cor(E, |W|) > 0.9, E is just a magnitude proxy (HARD_FAIL
    discriminator per cortex anchor 1 pre-reg).
    """
    if E.shape[0] != W.shape[0]:
        raise ValueError(f"shape mismatch: E={E.shape}, W rows={W.shape[0]}")
    norms = np.linalg.norm(W, axis=1)
    if np.std(E) <= 1e-12 or np.std(norms) <= 1e-12:
        return 0.0
    return float(np.corrcoef(E, norms)[0, 1])


def _selftest() -> None:
    rng = np.random.RandomState(0)
    n_atoms = 64
    cfg = EConfig()
    E = init_E(n_atoms)
    assert E.shape == (n_atoms,)
    assert np.all(E == 0.0)

    # Seed-on-write: bumps to seed_new only if below.
    seed_on_write(E, 5, cfg)
    assert E[5] == cfg.seed_new
    seed_on_write(E, 5, cfg)
    assert E[5] == cfg.seed_new  # idempotent at seed_new

    # Bump-on-retrieval: EWMA toward use_signal.
    bump_on_retrieval(E, 10, 1.0, cfg)
    assert abs(E[10] - 0.1) < 1e-9
    bump_on_retrieval(E, 10, 1.0, cfg)
    assert E[10] > 0.1  # accumulating

    # Slow-decay: multiplies all.
    E_pre = E.copy()
    slow_decay(E, cfg)
    assert np.all(E <= E_pre + 1e-12)

    # Correlation: random W with E zero -> 0.
    W = rng.randn(n_atoms, n_atoms).astype(np.float64)
    c = correlation_E_vs_magnitude(np.zeros(n_atoms), W)
    assert c == 0.0  # zero-variance E -> 0

    # Downscale gates.
    E_test = rng.rand(n_atoms).astype(np.float64)
    W_e = W.copy()
    n_hit_e = downscale_gate_by_E(W_e, E_test, scale=0.5, threshold=0.5)
    assert 0 < n_hit_e <= n_atoms
    norm_drop = np.linalg.norm(W_e) < np.linalg.norm(W)
    assert norm_drop

    W_m = W.copy()
    n_hit_m = downscale_gate_by_magnitude(W_m, threshold_frac=0.3, scale=0.5)
    assert n_hit_m > 0

    W_r = W.copy()
    n_hit_r = downscale_gate_random(W_r, frac=0.3, scale=0.5, rng=rng)
    assert n_hit_r == int(round(0.3 * n_atoms))

    print(
        f"[excitability selftest] PASS  E_seed={cfg.seed_new}  "
        f"hit_E={n_hit_e}  hit_mag={n_hit_m}  hit_rnd={n_hit_r}",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
