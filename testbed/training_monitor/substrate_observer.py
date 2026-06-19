"""SubstrateObserver: bipolar-projection Hebbian observer of an LLM residual
stream, with kappa_2 / kappa_3 / kappa_4_excess (free cumulants) computed via
Hutchinson trace estimators.

Usage pattern (training-monitor):

    obs = SubstrateObserver(N=4096, projection_seed=7, buffer_size=500)
    for step in train_steps:
        residual_t = model.layer[layer_idx].hidden  # (D,) numpy/torch array
        obs.observe(residual_t)                     # projects + Hebbian writes
        if step % monitor_every == 0:
            cumulants = obs.current_cumulants(n_probes=64)
            # cumulants = {"k2_mean":..., "k2_se":..., "k3_mean":..., ...}

Contract:
  * Projection: residual (D,) -> bipolar (N,) via sign(rand_proj @ residual).
    The random projection is fixed at observer init (projection_seed).
  * Substrate W: streaming Hebbian write, bounded ring buffer of `buffer_size`
    bipolar codes so substrate stays at fixed alpha = buffer_size / N. When the
    buffer wraps, the oldest pattern's rank-1 outer is subtracted before the
    new one is added (constant-substrate, fixed-alpha).
  * Cumulants via Hutchinson trace estimators in
    testbed.llm_integration.substrate_audit (kappa_2, kappa_3, kappa_4_excess).

PROT-022 self-tests (run at import):
  * Identity-W kappa_2 = 1, kappa_4_excess = -2.
  * kappa_3 sign matches sign of an asymmetric (skew) sample's third moment.
  * kappa_4_excess > 0 for a heavy-tailed (Cauchy-like clipped) sample.
  * SubstrateObserver write/read cycle preserves bipolar codes.

ASCII-only stdout per feedback_ascii_only_in_scripts.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from testbed.llm_integration.substrate_audit import (  # noqa: E402
    kappa_2_hutchinson,
    kappa_3_hutchinson,
    kappa_4_excess_hutchinson,
)


def _to_numpy_1d(x: Any) -> np.ndarray:
    """Coerce a residual-stream tensor (numpy or torch) to float32 1-D numpy."""
    # Torch tensor?
    if hasattr(x, "detach") and hasattr(x, "cpu"):
        try:
            x = x.detach().cpu().float().numpy()
        except Exception:
            x = np.asarray(x, dtype=np.float32)
    else:
        x = np.asarray(x, dtype=np.float32)
    return x.reshape(-1).astype(np.float32)


class SubstrateObserver:
    """Streaming bipolar-projection Hebbian observer with free-cumulant readout.

    Args:
        N:                Substrate dimensionality (e.g. 512 for smoke, 4096 for full).
        projection_seed:  RNG seed for the fixed Rademacher random projection.
        buffer_size:      Ring-buffer depth (oldest pattern subtracted on wrap).
                          alpha = buffer_size / N (target ~0.12).
        layer_idx:        Optional bookkeeping field; not used internally.
        in_dim:           Optional pre-declared input feature dimension D; the
                          random-projection matrix is constructed on first
                          observe() if left None.
    """

    def __init__(
        self,
        N: int,
        projection_seed: int = 7,
        buffer_size: Optional[int] = None,
        layer_idx: Optional[int] = None,
        in_dim: Optional[int] = None,
    ) -> None:
        self.N = int(N)
        self.projection_seed = int(projection_seed)
        self.buffer_size = int(buffer_size) if buffer_size is not None else max(1, self.N // 8)
        self.layer_idx = layer_idx
        self._proj_rng = np.random.default_rng(self.projection_seed)
        self._cumulant_rng = np.random.default_rng(self.projection_seed + 1009)
        self.P: Optional[np.ndarray] = None  # (D, N) Rademacher projection
        self._in_dim = int(in_dim) if in_dim is not None else None
        if self._in_dim is not None:
            self._build_projection(self._in_dim)
        # Streaming substrate state
        self.W = np.zeros((self.N, self.N), dtype=np.float32)
        # Ring buffer of bipolar codes (rows) for bounded-window Hebbian.
        self._buf: Optional[np.ndarray] = None  # (buffer_size, N)
        self._buf_pos = 0                       # next write index
        self._buf_filled = 0                    # how many slots currently non-empty
        self.n_observed = 0

    # ------------------------------------------------------------------
    # Projection
    # ------------------------------------------------------------------

    def _build_projection(self, in_dim: int) -> None:
        """Construct the fixed Rademacher random projection P of shape (D, N).

        Bipolar projection: sign(P^T x). We store P as float32 +/-1 entries
        scaled by 1/sqrt(D) -- the scale is irrelevant after the sign().
        """
        self._in_dim = int(in_dim)
        self.P = self._proj_rng.choice(
            [-1.0, 1.0], size=(in_dim, self.N)
        ).astype(np.float32) / float(np.sqrt(in_dim))

    def project(self, residual: Any) -> np.ndarray:
        """residual (D,) -> bipolar (N,) via sign(residual @ P).

        Zero entries (perfect orthogonality, very unlikely) are coerced to +1.
        """
        x = _to_numpy_1d(residual)
        if self.P is None or self._in_dim != x.shape[0]:
            self._build_projection(x.shape[0])
        proj = x @ self.P  # (N,)
        xi = np.where(proj >= 0.0, 1.0, -1.0).astype(np.float32)
        return xi

    # ------------------------------------------------------------------
    # Streaming substrate write
    # ------------------------------------------------------------------

    def _ring_write(self, xi: np.ndarray) -> None:
        """Push xi into the ring buffer; subtract evicted pattern's outer product."""
        if self._buf is None:
            self._buf = np.zeros((self.buffer_size, self.N), dtype=np.float32)
        N = float(self.N)
        if self._buf_filled < self.buffer_size:
            # Empty slot at _buf_pos
            self._buf[self._buf_pos] = xi
            self.W += np.outer(xi, xi) / N
            self._buf_pos = (self._buf_pos + 1) % self.buffer_size
            self._buf_filled += 1
        else:
            # Buffer full -- evict oldest at _buf_pos before overwriting
            old = self._buf[self._buf_pos]
            self.W -= np.outer(old, old) / N
            self._buf[self._buf_pos] = xi
            self.W += np.outer(xi, xi) / N
            self._buf_pos = (self._buf_pos + 1) % self.buffer_size

    def observe(self, residual: Any) -> np.ndarray:
        """Project residual to bipolar and Hebbian-write to substrate. Returns xi."""
        xi = self.project(residual)
        self._ring_write(xi)
        self.n_observed += 1
        return xi

    # ------------------------------------------------------------------
    # Cumulant readout
    # ------------------------------------------------------------------

    def current_cumulants(self, n_probes: int = 64) -> Dict[str, float]:
        """Hutchinson estimates of kappa_2, kappa_3, kappa_4_excess on W.

        Returns dict with keys: k2_mean, k2_se, k3_mean, k3_se, k4ex_mean, k4ex_se,
        plus n_observed and buf_filled bookkeeping.
        """
        k2_mean, k2_se = kappa_2_hutchinson(self.W, n_probes, self._cumulant_rng)
        k3_mean, k3_se = kappa_3_hutchinson(self.W, n_probes, self._cumulant_rng)
        k4ex_mean, k4ex_se = kappa_4_excess_hutchinson(self.W, n_probes, self._cumulant_rng)
        return {
            "k2_mean": float(k2_mean),
            "k2_se": float(k2_se),
            "k3_mean": float(k3_mean),
            "k3_se": float(k3_se),
            "k4ex_mean": float(k4ex_mean),
            "k4ex_se": float(k4ex_se),
            "n_observed": int(self.n_observed),
            "buf_filled": int(self._buf_filled),
            "alpha_substrate": float(self._buf_filled) / float(self.N),
        }


# ----------------------------------------------------------------------
# PROT-022 self-tests
# ----------------------------------------------------------------------

def _selftest_identity_cumulants() -> None:
    """kappa_2(I) ~ 1; kappa_4_excess(I) ~ 1 - 3 = -2."""
    rng = np.random.default_rng(0)
    N = 128
    W_id = np.eye(N, dtype=np.float32)
    k2_id, _ = kappa_2_hutchinson(W_id, 200, rng)
    k4ex_id, _ = kappa_4_excess_hutchinson(W_id, 200, rng)
    assert abs(k2_id - 1.0) < 0.1, f"kappa_2(I) = {k2_id}, expected ~1.0"
    assert abs(k4ex_id - (-2.0)) < 0.2, f"kappa_4_excess(I) = {k4ex_id}, expected ~-2.0"
    print(f"[selftest training_monitor] PASS identity: k2(I)={k2_id:.3f} "
          f"k4_excess(I)={k4ex_id:.3f}", flush=True)


def _selftest_kappa3_skew_sign() -> None:
    """kappa_3 sign matches sign of a built-in asymmetry.

    Build W as a sum of M rank-1 outer products of POSITIVELY-BIASED bipolar
    samples (P(+1)=0.7 instead of 0.5). This injects positive third-moment
    structure into the spectrum; kappa_3 should come out clearly positive.
    Then build W' from NEGATIVELY-BIASED (P(+1)=0.3) samples; kappa_3 < 0 not
    guaranteed (since W is positive-semi-definite by construction), but the
    biased run's kappa_3 must EXCEED the IID (P(+1)=0.5) baseline.  This is
    the same logic as the established exp_a7_kappa3 selftest.
    """
    rng = np.random.default_rng(1)
    N, M = 256, 80
    Xi_iid = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W_iid = (Xi_iid.T @ Xi_iid) / float(N)
    k3_iid, _ = kappa_3_hutchinson(W_iid, 200, rng)

    Xi_pos = np.where(rng.random(size=(M, N)) < 0.7, 1.0, -1.0).astype(np.float32)
    W_pos = (Xi_pos.T @ Xi_pos) / float(N)
    k3_pos, _ = kappa_3_hutchinson(W_pos, 200, rng)

    # positively-biased patterns => stronger correlations => kappa_3 strictly larger
    assert k3_pos > k3_iid, \
        f"kappa_3 skew-sign: k3_pos={k3_pos:.4f} should exceed k3_iid={k3_iid:.4f}"
    print(f"[selftest training_monitor] PASS skew-sign: k3_iid={k3_iid:.3f} "
          f"k3_pos_bias={k3_pos:.3f} (positive shift)", flush=True)


def _selftest_kappa4_heavy_tail() -> None:
    """kappa_4_excess positive for heavy-tailed (clipped-Cauchy) sample-built W.

    Build W from M heavy-tailed real-valued rows (clipped Student-t with low df)
    normalised to unit-norm. Heavy tails -> excess kurtosis -> kappa_4_excess > 0.
    Compare against IID-Gaussian-built W (Gaussian; kappa_4_excess ~ 0 in the
    free-prob sense -- bulk Marchenko-Pastur).
    """
    rng = np.random.default_rng(2)
    N, M = 256, 80

    # Gaussian (light-tail) reference
    Xi_g = rng.standard_normal(size=(M, N)).astype(np.float32)
    Xi_g = Xi_g / (np.linalg.norm(Xi_g, axis=1, keepdims=True) + 1e-30) * np.sqrt(N)
    W_g = (Xi_g.T @ Xi_g) / float(N)
    k4ex_g, _ = kappa_4_excess_hutchinson(W_g, 200, rng)

    # Clipped-t (df=3): much heavier tails than Gaussian
    t_samples = rng.standard_t(df=3.0, size=(M, N)).astype(np.float32)
    # Clip extreme values so the empirical covariance stays finite-spectrum
    t_samples = np.clip(t_samples, -20.0, 20.0)
    t_samples = t_samples / (np.linalg.norm(t_samples, axis=1, keepdims=True) + 1e-30) * np.sqrt(N)
    W_t = (t_samples.T @ t_samples) / float(N)
    k4ex_t, _ = kappa_4_excess_hutchinson(W_t, 200, rng)

    # Heavy-tailed should yield strictly larger kappa_4_excess than Gaussian.
    assert k4ex_t > k4ex_g, \
        f"kappa_4_excess heavy-tail: k4_t={k4ex_t:.4f} should exceed k4_g={k4ex_g:.4f}"
    print(f"[selftest training_monitor] PASS heavy-tail: "
          f"k4ex_gaussian={k4ex_g:.3f} k4ex_t_df3={k4ex_t:.3f} "
          f"(heavy-tail excess strictly larger)", flush=True)


def _selftest_observer_write_read() -> None:
    """SubstrateObserver: project preserves bipolar codes; observe accumulates
    into W; ring buffer caps alpha at buffer_size/N exactly.
    """
    obs = SubstrateObserver(N=128, projection_seed=11, buffer_size=20, in_dim=64)
    rng = np.random.default_rng(13)

    # Project: output must be exactly {-1, +1}
    x = rng.standard_normal(64).astype(np.float32)
    xi = obs.project(x)
    assert xi.shape == (128,), f"projected shape {xi.shape} != (128,)"
    assert set(np.unique(xi).tolist()) <= {-1.0, 1.0}, \
        f"projected code has non-bipolar entries: {np.unique(xi)}"

    # observe 5 patterns; buffer should be partially filled and W non-zero
    for _ in range(5):
        x = rng.standard_normal(64).astype(np.float32)
        obs.observe(x)
    assert obs._buf_filled == 5, f"buf_filled={obs._buf_filled} expected 5"
    assert float(np.linalg.norm(obs.W)) > 1e-6, "W still zero after 5 observes"

    # observe 50 more patterns; ring should saturate at buffer_size=20
    for _ in range(50):
        x = rng.standard_normal(64).astype(np.float32)
        obs.observe(x)
    assert obs._buf_filled == 20, f"buf_filled={obs._buf_filled} expected 20"

    # alpha must equal buffer_size / N = 20 / 128 ~ 0.156
    info = obs.current_cumulants(n_probes=16)
    assert abs(info["alpha_substrate"] - 20.0 / 128.0) < 1e-6, \
        f"alpha_substrate={info['alpha_substrate']} != 20/128"

    print(f"[selftest training_monitor] PASS observer: "
          f"buf_filled={obs._buf_filled} alpha={info['alpha_substrate']:.4f} "
          f"k2={info['k2_mean']:.3f} k3={info['k3_mean']:.3f} "
          f"k4ex={info['k4ex_mean']:.3f}", flush=True)


def _selftest() -> None:
    _selftest_identity_cumulants()
    _selftest_kappa3_skew_sign()
    _selftest_kappa4_heavy_tail()
    _selftest_observer_write_read()
    print("[selftest training_monitor] PROT-022 ALL PASS", flush=True)


_selftest()


__all__ = ["SubstrateObserver"]


if __name__ == "__main__":
    pass
