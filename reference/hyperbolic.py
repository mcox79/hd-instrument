"""Hyperbolic VSA reference, tier-1 tangent-space approach in the Lorentz model.

Atoms live on the upper sheet of the Lorentz hyperboloid x_0^2 - x_1^2 - ... - x_n^2 = 1
with x_0 > 0. Bind/bundle/unbind operations happen in the tangent space at the origin
o = (1, 0, ..., 0), which is the Euclidean R^n subspace where the first coordinate is 0.
Atoms are mapped to/from tangent space via the exponential and logarithmic maps.

Cleanup uses hyperbolic distance for ranking, which is the one place where the manifold's
geometric structure actually enters the computation.

All math in float64 for numerical stability; the arcosh near 1 is delicate and float32 fails.

This is tier 1: cheap to implement, possibly limited in advantage because bind/bundle don't
use the curvature. Tier 2 (true hyperbolic binding via Lorentz isometries) would push further
if tier 1 shows promise.
"""

from __future__ import annotations

import math

import torch


# ---------------------------------------------------------------------------
# Lorentz model helpers (all in float64).
# ---------------------------------------------------------------------------


def minkowski_inner(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """<x, y>_M = -x_0 y_0 + x_1 y_1 + ... + x_n y_n   (mostly-plus signature)."""
    return -x[..., 0] * y[..., 0] + (x[..., 1:] * y[..., 1:]).sum(dim=-1)


def is_on_hyperboloid(x: torch.Tensor, atol: float = 1e-5) -> bool:
    """Check x_0^2 - sum(x_i^2) ~= 1 for i >= 1."""
    val = x[..., 0] ** 2 - (x[..., 1:] ** 2).sum(dim=-1)
    return bool(torch.all(torch.abs(val - 1.0) < atol))


def origin(n: int, dtype: torch.dtype = torch.float64) -> torch.Tensor:
    """The "top" of the Lorentz hyperboloid: o = (1, 0, ..., 0). Shape: (n+1,)."""
    o = torch.zeros(n + 1, dtype=dtype)
    o[0] = 1.0
    return o


def exp_origin(v_spatial: torch.Tensor) -> torch.Tensor:
    """Exp map at the origin. v_spatial: (n,) tangent vector. Returns (n+1,) point on hyperboloid.

    exp_o((0, v)) = (cosh(|v|), (sinh(|v|)/|v|) * v).
    """
    v_spatial = v_spatial.to(torch.float64)
    norm = v_spatial.norm()
    if float(norm) < 1e-12:
        out = torch.zeros(v_spatial.shape[-1] + 1, dtype=torch.float64)
        out[0] = 1.0
        return out
    cosh_n = torch.cosh(norm)
    sinh_over_n = torch.sinh(norm) / norm
    out = torch.empty(v_spatial.shape[-1] + 1, dtype=torch.float64)
    out[0] = cosh_n
    out[1:] = sinh_over_n * v_spatial
    return out


def log_origin(x: torch.Tensor) -> torch.Tensor:
    """Log map at the origin. x: (n+1,) point on hyperboloid. Returns (n,) tangent vector.

    log_o(x) = (arcosh(x_0) / |x_spatial|) * x_spatial.
    Returns zero vector if x ~= origin.
    """
    x = x.to(torch.float64)
    x_spatial = x[1:]
    spatial_norm = x_spatial.norm()
    if float(spatial_norm) < 1e-12:
        return torch.zeros_like(x_spatial)
    # Clamp x[0] >= 1 to avoid nan in arcosh due to float roundoff
    x0_clamped = torch.clamp(x[0], min=1.0)
    arcosh_x0 = torch.acosh(x0_clamped)
    return (arcosh_x0 / spatial_norm) * x_spatial


def hyperbolic_distance(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Hyperbolic distance via Minkowski inner product. Returns d(x, y) >= 0."""
    x = x.to(torch.float64)
    y = y.to(torch.float64)
    # For batched: -<x, y>_M >= 1 for points on the upper hyperboloid; can dip below by roundoff
    inner = -minkowski_inner(x, y)
    inner = torch.clamp(inner, min=1.0)
    return torch.acosh(inner)


# ---------------------------------------------------------------------------
# Atoms, binding, bundle, similarity for hyperbolic VSA.
# ---------------------------------------------------------------------------


def make_atom(n: int, generator: torch.Generator, radius: float = 1.0) -> torch.Tensor:
    """Sample a hyperbolic atom: random direction in tangent space, exp-map to hyperboloid.

    radius controls how "deep" into hyperbolic space atoms live. r ~ 1 is in the curved regime
    without numerical disaster.
    """
    v = torch.randn(n, generator=generator, dtype=torch.float64)
    v = v / v.norm() * radius
    return exp_origin(v)


def bind(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Tangent-space VSA bind: log -> circular convolution -> exp.

    bind_tangent(u, v) = u circ_conv v (via FFT)
    bind(x, y) = exp_o(bind_tangent(log_o(x), log_o(y)))
    """
    u = log_origin(x)
    v = log_origin(y)
    # Circular convolution in real domain (HRR-style)
    n = u.shape[-1]
    fu = torch.fft.fft(u)
    fv = torch.fft.fft(v)
    result_tangent = torch.fft.ifft(fu * fv).real
    return exp_origin(result_tangent)


def unbind(c: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Tangent-space VSA unbind: log -> circular correlation -> exp."""
    u = log_origin(c)
    v = log_origin(y)
    fu = torch.fft.fft(u)
    fv = torch.fft.fft(v)
    result_tangent = torch.fft.ifft(fu * fv.conj()).real
    return exp_origin(result_tangent)


def bundle(vectors: torch.Tensor) -> torch.Tensor:
    """L2-normalized tangent-space sum, exp back. This keeps the result at hyperbolic
    radius 1 (the same radius as atoms), so cleanup distances aren't confounded by
    bundle-induced radial shrinkage.

    vectors: (k, n+1) tensor of points on hyperboloid. Returns (n+1,).
    """
    tangents = torch.stack([log_origin(vectors[i]) for i in range(vectors.shape[0])])
    summed = tangents.sum(dim=0)
    norm = summed.norm()
    if float(norm) > 1e-12:
        summed = summed / norm  # tangent has unit norm = result at hyperbolic radius 1
    return exp_origin(summed)


def similarity(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Similarity via negative hyperbolic distance (so higher = more similar)."""
    return -hyperbolic_distance(a, b)


def similarity_to_pool(query: torch.Tensor, pool: torch.Tensor) -> torch.Tensor:
    """Batched similarity for cleanup. pool: (k, n+1). Returns (k,)."""
    # Compute hyperbolic distance from query to each pool atom in batch
    query = query.to(torch.float64)
    pool = pool.to(torch.float64)
    inner = -(-query[0] * pool[:, 0] + (query[1:].unsqueeze(0) * pool[:, 1:]).sum(dim=-1))
    inner = torch.clamp(inner, min=1.0)
    dists = torch.acosh(inner)
    return -dists  # higher similarity = smaller distance
