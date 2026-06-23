"""Substrate-native predictive coding (Friston / Rao-Ballard 1999).

Treats the substrate weight matrix W as a generative model:
  predict(key) = sign(W @ key)               # current best prediction
  residual    = observed - predicted          # bipolar mismatch
  gated_write = write only when residual magnitude exceeds threshold

The aim is free-energy-minimization style ingest: skip writes for patterns
the substrate already predicts, concentrate plasticity on novel / surprising
patterns. This composes with the existing Hebbian outer-product update
(W += value outer key) but multiplies the delta by a residual-derived gate.

Three gate flavours are provided so cells can A/B them:
  - threshold gate: write at full strength iff cosine(residual, observed) >= t
  - proportional gate: write strength = clipped residual magnitude in [0, 1]
  - random control (NOT in this module; cells implement to keep math here clean)

ASCII-only. NumPy; no torch dependency (matches associative-memory cells).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Core operators
# ---------------------------------------------------------------------------

def predict(W: np.ndarray, key: np.ndarray, *, sign_cleanup: bool = True) -> np.ndarray:
    """Substrate's current prediction for the value bound to key.

    W: (N, N) accumulated outer-product memory (key -> value associations).
    key: (N,) bipolar +-1 vector OR (B, N) batch of keys.
    sign_cleanup: if True, return sign(W @ key) (bipolar projection); else raw.

    Returns: (N,) or (B, N) prediction in {-1, +1} (bipolar) when sign_cleanup.
    """
    if key.ndim == 1:
        raw = W @ key
    elif key.ndim == 2:
        raw = key @ W.T  # (B, N)
    else:
        raise ValueError(f"key must be 1D or 2D, got ndim={key.ndim}")
    if not sign_cleanup:
        return raw
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def residual(observed: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    """Bipolar residual = observed - predicted.

    For bipolar vectors in {-1, +1}, residual entries are in {-2, 0, +2}.
    The L1/2 norm of this residual is proportional to the bit-mismatch count.
    """
    if observed.shape != predicted.shape:
        raise ValueError(
            f"shape mismatch: observed {observed.shape} vs predicted {predicted.shape}"
        )
    return observed - predicted


def residual_magnitude(observed: np.ndarray, predicted: np.ndarray) -> float:
    """Normalized residual magnitude in [0, 1].

    1.0 = fully opposite (every bit flipped); 0.0 = perfect prediction.
    Defined as fraction-of-bits-mismatched for bipolar inputs, computed
    via the cosine-similarity identity: mismatch_frac = (1 - cos)/2.
    """
    obs = observed.ravel()
    pred = predicted.ravel()
    n = obs.shape[0]
    if n == 0:
        return 0.0
    # For exact-bipolar inputs cos = (obs @ pred) / n; we use a safe form.
    obs_n = float(np.linalg.norm(obs))
    pred_n = float(np.linalg.norm(pred))
    if obs_n <= 1e-12 or pred_n <= 1e-12:
        return 1.0
    cos = float(np.dot(obs, pred)) / (obs_n * pred_n)
    cos = max(-1.0, min(1.0, cos))
    return 0.5 * (1.0 - cos)


# ---------------------------------------------------------------------------
# Gated write rules
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WriteDecision:
    """Outcome of a residual-gated write attempt."""
    write_strength: float       # 0.0 = skipped; >0 = applied multiplier
    residual_mag: float         # raw mismatch fraction (0=perfect, 1=opposite)
    skipped: bool               # True iff write_strength == 0
    reason: str                 # human readable disposition


def threshold_gate(
    observed: np.ndarray,
    predicted: np.ndarray,
    *,
    threshold: float,
) -> WriteDecision:
    """Write at full strength iff residual magnitude >= threshold.

    threshold semantics: residual_mag in [0, 1]; threshold 0.3 means write
    only when the substrate already gets 30% of the bits wrong (i.e. the
    pattern is at least 30% novel).
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0, 1]; got {threshold}")
    mag = residual_magnitude(observed, predicted)
    if mag >= threshold:
        return WriteDecision(
            write_strength=1.0, residual_mag=mag, skipped=False,
            reason=f"residual_mag={mag:.3f} >= threshold={threshold:.3f}",
        )
    return WriteDecision(
        write_strength=0.0, residual_mag=mag, skipped=True,
        reason=f"residual_mag={mag:.3f} < threshold={threshold:.3f}",
    )


def proportional_gate(
    observed: np.ndarray,
    predicted: np.ndarray,
    *,
    min_strength: float = 0.0,
    max_strength: float = 1.0,
) -> WriteDecision:
    """Write at strength equal to clipped residual magnitude.

    min_strength: floor on applied write (skip iff residual_mag == 0 exactly).
    max_strength: ceiling (residual_mag is already capped at 1.0).
    """
    if min_strength < 0.0 or max_strength <= 0.0 or min_strength > max_strength:
        raise ValueError(
            f"invalid bounds: min={min_strength}, max={max_strength}"
        )
    mag = residual_magnitude(observed, predicted)
    strength = max(min_strength, min(max_strength, mag))
    skipped = strength <= 0.0
    return WriteDecision(
        write_strength=float(strength), residual_mag=mag, skipped=skipped,
        reason=f"residual_mag={mag:.3f} -> strength={strength:.3f}",
    )


def gated_write(
    W: np.ndarray,
    key: np.ndarray,
    value: np.ndarray,
    decision: WriteDecision,
) -> tuple[np.ndarray, bool]:
    """Apply a residual-gated outer-product update to W in place (returns W).

    Returns (W, applied) where applied is True iff a non-zero update was made.
    """
    if decision.skipped or decision.write_strength <= 0.0:
        return W, False
    W += decision.write_strength * np.outer(value, key)
    return W, True


# ---------------------------------------------------------------------------
# Vanilla baseline (for cell parity)
# ---------------------------------------------------------------------------

def vanilla_hebbian_write(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> np.ndarray:
    """Full-strength outer-product update; no gate."""
    W += np.outer(value, key)
    return W


# ---------------------------------------------------------------------------
# Self-test (run when invoked as a script)
# ---------------------------------------------------------------------------

def _selftest() -> None:
    rng = np.random.RandomState(0)
    N = 64
    M = 8
    # Bipolar key/value pairs.
    keys = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float64)

    # Vanilla: write every pair.
    W_van = np.zeros((N, N), dtype=np.float64)
    for k, v in zip(keys, values):
        vanilla_hebbian_write(W_van, k, v)

    # Threshold gate (high threshold so all writes happen since W starts empty).
    W_gate = np.zeros((N, N), dtype=np.float64)
    n_skipped = 0
    for k, v in zip(keys, values):
        pred = predict(W_gate, k)
        dec = threshold_gate(v, pred, threshold=0.3)
        _, applied = gated_write(W_gate, k, v, dec)
        if not applied:
            n_skipped += 1

    # On the first write, predicted is sign(0 @ k) = all +1; residual against
    # a random bipolar value averages ~0.5 mismatch -- so threshold 0.3 admits
    # the first write. Subsequent writes may or may not be skipped depending
    # on prediction quality.
    pred0 = predict(np.zeros((N, N)), keys[0])
    mag0 = residual_magnitude(values[0], pred0)
    assert 0.2 < mag0 < 0.8, f"selftest first-write residual_mag={mag0:.3f} out of expected band"

    # Vanilla W must equal the closed-form Hebbian sum (sanity).
    expected = values.T @ keys
    assert np.allclose(W_van, expected), "vanilla_hebbian_write does not match outer-product sum"

    # Recall on vanilla: project key, sign, compare to value. At alpha=M/N=0.125
    # < alpha_c=0.138 (Hopfield), recall should be high.
    recalls = []
    for k, v in zip(keys, values):
        pred = predict(W_van, k)
        cos = float(np.dot(pred, v)) / float(N)
        recalls.append(cos)
    mean_cos = float(np.mean(recalls))
    assert mean_cos > 0.5, f"vanilla recall mean_cos={mean_cos:.3f} too low"

    print(
        f"[predictive_coding selftest] PASS  "
        f"first_residual_mag={mag0:.3f}  vanilla_mean_cos={mean_cos:.3f}  "
        f"gate_skipped={n_skipped}/{M}",
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
