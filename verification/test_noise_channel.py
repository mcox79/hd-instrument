"""Verification: M1.3 NoiseChannel reproduces CG-anchored regime calibration."""

from __future__ import annotations

import pytest
import torch

from hdlab.noise_channel import (
    REGIME_SIGMA,
    NoiseChannel,
    _run_all_selftests,
    sigma_for_regime,
)


def test_run_all_selftests_pass() -> None:
    """All module selftests reproduce M1.3 source calibration."""
    result = _run_all_selftests()
    assert result["primitive"] == "M1.3_NoiseChannel"
    assert result["mode"] == "additive_gaussian_L2_preserving"
    assert result["storage_strategy"] == "NO_STORAGE"


def test_regime_table_cg_anchors() -> None:
    """Regime sigma table matches source substrate_router calibration (2026-07-01 c5e5e66a)."""
    assert REGIME_SIGMA["clean"] == 0.00
    assert REGIME_SIGMA["light"] == 0.05
    assert REGIME_SIGMA["moderate"] == 0.15
    assert REGIME_SIGMA["heavy"] == 0.35
    assert REGIME_SIGMA["catastrophic"] == 0.60


def test_sigma_zero_is_passthrough() -> None:
    """sigma_boundary=0 returns exact clone (identity)."""
    ch = NoiseChannel(sigma_boundary=0.0)
    v = torch.randn(1024, dtype=torch.float32)
    v = v / torch.linalg.norm(v)
    out = ch.inject(v)
    assert float((out - v).abs().max()) < 1e-6


def test_generator_determinism() -> None:
    """Same generator seed produces bit-identical output."""
    v = torch.randn(1024, dtype=torch.float32)
    v = v / torch.linalg.norm(v)
    g1 = torch.Generator().manual_seed(42)
    g2 = torch.Generator().manual_seed(42)
    o1 = NoiseChannel(sigma_boundary=0.15, generator=g1).inject(v)
    o2 = NoiseChannel(sigma_boundary=0.15, generator=g2).inject(v)
    assert float((o1 - o2).abs().max()) < 1e-6


def test_l2_norm_preserved() -> None:
    """||inject(vec)|| within 1e-4 of ||vec|| for sigma in [0.05, 0.35]."""
    v = torch.randn(1024, dtype=torch.float32)
    v = v / torch.linalg.norm(v)
    ref_norm = float(torch.linalg.norm(v))
    for sigma in (0.05, 0.15, 0.35):
        g = torch.Generator().manual_seed(int(1000 * sigma))
        out = NoiseChannel(sigma_boundary=sigma, generator=g).inject(v)
        assert abs(float(torch.linalg.norm(out)) - ref_norm) < 1e-4


def test_negative_sigma_rejected() -> None:
    """Constructor rejects negative sigma_boundary."""
    with pytest.raises(ValueError):
        NoiseChannel(sigma_boundary=-0.01)


def test_unknown_regime_rejected() -> None:
    """sigma_for_regime rejects unknown regime name."""
    with pytest.raises(ValueError):
        sigma_for_regime("unlisted_regime")
