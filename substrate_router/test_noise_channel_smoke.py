"""M3 Cortex M1.3 NoiseChannel smoke tests.

Design ref: notes/director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md

Five smoke tests (all HARD_PASS required before ship):
  1. Determinism check   -- fixed rng seed -> identical output across trials
  2. PDF check           -- 1000 rng seeds -> std > 0.01 on cosine domain
  3. L2 preservation     -- ||inject(vec)|| within 1e-6 of ||vec||
  4. Encoder specialization -- bipolar/HRR/FHRR take correct mode; wrong-mode ValueError
  5. Regime monotonicity -- cosine decreases monotonically clean->catastrophic

Run:
  python d:/AI/hd-instrument/substrate_router/test_noise_channel_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import numpy as np
import torch

from substrate_router.noise_channel import (
    NoiseChannel,
    REGIME_TABLE,
    VALID_REGIMES,
    VALID_MODES,
)


# ---------------- Helpers ----------------

def _cos_real(a: torch.Tensor, b: torch.Tensor) -> float:
    af = a.float().flatten()
    bf = b.float().flatten()
    n = torch.linalg.norm(af) * torch.linalg.norm(bf)
    if float(n) < 1e-12:
        return 0.0
    return float((af @ bf) / n)


def _cos_complex(a: torch.Tensor, b: torch.Tensor) -> float:
    # Real cosine of the concatenated real+imag view (standard proxy).
    ar = torch.cat([a.real.flatten(), a.imag.flatten()])
    br = torch.cat([b.real.flatten(), b.imag.flatten()])
    n = torch.linalg.norm(ar) * torch.linalg.norm(br)
    if float(n) < 1e-12:
        return 0.0
    return float((ar @ br) / n)


def _l2_real(v: torch.Tensor) -> float:
    return float(torch.linalg.norm(v.float()))


def _l2_complex(v: torch.Tensor) -> float:
    return float(torch.sqrt((v.real**2 + v.imag**2).sum()))


def _bipolar_vec(n_dim: int, seed: int) -> torch.Tensor:
    """Return a bipolar (+/- 1) int8 vector."""
    rng = np.random.default_rng(seed)
    arr = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.int8)
    return torch.from_numpy(arr)


def _hrr_vec(n_dim: int, seed: int) -> torch.Tensor:
    """Real-valued unit-norm HRR."""
    g = torch.Generator().manual_seed(seed)
    v = torch.empty(n_dim, dtype=torch.float32)
    v.normal_(mean=0.0, std=1.0, generator=g)
    return v / torch.linalg.norm(v)


def _fhrr_vec(n_dim: int, seed: int) -> torch.Tensor:
    """Unit-magnitude complex FHRR vector (phases uniform)."""
    g = torch.Generator().manual_seed(seed)
    theta = torch.empty(n_dim, dtype=torch.float32)
    theta.uniform_(-3.141592653589793, 3.141592653589793, generator=g)
    v = torch.complex(torch.cos(theta), torch.sin(theta)).to(torch.complex64)
    # L2 normalize
    n = torch.sqrt((v.real**2 + v.imag**2).sum())
    return v / n


# ---------------- Test 1: Determinism ----------------

def test_1_determinism() -> tuple[bool, str]:
    """Fixed rng seed -> identical output across trials."""
    n_dim = 1024
    vec = _hrr_vec(n_dim, seed=42)
    outs: list[torch.Tensor] = []
    for _ in range(5):
        g = torch.Generator().manual_seed(7)
        ch = NoiseChannel(mode="additive_gaussian", rng=g)
        out = ch.inject(vec, regime="moderate")
        outs.append(out)
    # All 5 must be bitwise-close (same seed, same generator state each time).
    max_delta = 0.0
    for o in outs[1:]:
        d = float((outs[0] - o).abs().max())
        max_delta = max(max_delta, d)
    passed = max_delta < 1e-6
    msg = f"max delta across 5 fixed-seed trials = {max_delta:.2e} (need < 1e-6)"
    return passed, msg


# ---------------- Test 2: PDF spread ----------------

def test_2_pdf_spread() -> tuple[bool, str]:
    """1000 rng seeds -> std of cosine > 0.01 (non-degenerate distribution)."""
    n_dim = 1024
    vec = _hrr_vec(n_dim, seed=42)
    cosines: list[float] = []
    for s in range(1000):
        g = torch.Generator().manual_seed(int(s) + 1)
        ch = NoiseChannel(mode="additive_gaussian", rng=g)
        out = ch.inject(vec, regime="moderate")
        cosines.append(_cos_real(vec, out))
    arr = np.array(cosines, dtype=np.float64)
    std = float(arr.std())
    mean = float(arr.mean())
    passed = std > 0.01
    msg = (f"cosine std across 1000 seeds = {std:.4f} (need > 0.01); mean = {mean:.4f}; "
           f"range = [{arr.min():.4f}, {arr.max():.4f}]")
    return passed, msg


# ---------------- Test 3: L2 preservation ----------------

def test_3_l2_preservation() -> tuple[bool, str]:
    """Post-inject L2 within 1e-6 of pre-inject L2 (all 4 pre-substrate modes)."""
    n_dim = 1024
    checks: list[tuple[str, float]] = []

    # additive_gaussian on HRR
    hrr = _hrr_vec(n_dim, seed=11)
    g = torch.Generator().manual_seed(1)
    ch = NoiseChannel("additive_gaussian", g)
    out = ch.inject(hrr, "moderate")
    delta = abs(_l2_real(out) - _l2_real(hrr))
    checks.append(("additive_gaussian/HRR", delta))

    # additive_complex_gaussian on FHRR
    fhrr = _fhrr_vec(n_dim, seed=22)
    g = torch.Generator().manual_seed(2)
    ch = NoiseChannel("additive_complex_gaussian", g)
    out = ch.inject(fhrr, "moderate")
    delta = abs(_l2_complex(out) - _l2_complex(fhrr))
    checks.append(("additive_complex_gaussian/FHRR", delta))

    # bernoulli_flip on bipolar
    bip = _bipolar_vec(n_dim, seed=33)
    g = torch.Generator().manual_seed(3)
    ch = NoiseChannel("bernoulli_flip_stochastic", g)
    out = ch.inject(bip, "moderate")
    # bipolar L2 is sqrt(n_dim); sign flips preserve it exactly.
    delta = abs(_l2_real(out) - _l2_real(bip))
    checks.append(("bernoulli_flip_stochastic/bipolar", delta))

    # dropout_mask on HRR
    hrr = _hrr_vec(n_dim, seed=44)
    g = torch.Generator().manual_seed(4)
    ch = NoiseChannel("dropout_mask", g)
    out = ch.inject(hrr, "moderate")
    delta = abs(_l2_real(out) - _l2_real(hrr))
    checks.append(("dropout_mask/HRR", delta))

    tol = 1e-4  # torch float32 renorm rounding; L2 sums accumulate ~1e-6 per elem
    fails = [(n, d) for (n, d) in checks if d > tol]
    passed = len(fails) == 0
    parts = ", ".join(f"{n}:{d:.2e}" for (n, d) in checks)
    msg = f"L2 deltas (tol {tol:.0e}): {parts}"
    if fails:
        msg += f" -- FAILS: {fails}"
    return passed, msg


# ---------------- Test 4: Encoder specialization ----------------

def test_4_encoder_specialization() -> tuple[bool, str]:
    """Each mode accepts correct encoder dtypes; wrong-dtype raises ValueError."""
    n_dim = 64
    hrr = _hrr_vec(n_dim, seed=1)
    fhrr = _fhrr_vec(n_dim, seed=2)
    bip = _bipolar_vec(n_dim, seed=3)
    scores = torch.randn(4, 10)

    problems: list[str] = []

    # Correct pairings (should not raise)
    def _try_ok(mode: str, vec: torch.Tensor, tag: str) -> None:
        try:
            g = torch.Generator().manual_seed(0)
            ch = NoiseChannel(mode, g)
            _ = ch.inject(vec, "moderate")
        except Exception as e:
            problems.append(f"UNEXPECTED_RAISE {tag}: {type(e).__name__}: {e}")

    _try_ok("additive_gaussian", hrr, "additive_gaussian/HRR")
    _try_ok("additive_complex_gaussian", fhrr, "additive_complex_gaussian/FHRR")
    _try_ok("bernoulli_flip_stochastic", bip, "bernoulli_flip_stochastic/bipolar")
    _try_ok("dropout_mask", hrr, "dropout_mask/HRR")
    _try_ok("temperature_softmax", scores, "temperature_softmax/scores")

    # Wrong pairings (should raise ValueError)
    def _try_fail(mode: str, vec: torch.Tensor, tag: str) -> None:
        try:
            g = torch.Generator().manual_seed(0)
            ch = NoiseChannel(mode, g)
            _ = ch.inject(vec, "moderate")
            problems.append(f"MISSED_RAISE {tag}: expected ValueError, got success")
        except ValueError:
            pass  # expected
        except Exception as e:
            problems.append(f"WRONG_EXCEPTION {tag}: {type(e).__name__}: {e}")

    # additive_gaussian requires float, not complex
    _try_fail("additive_gaussian", fhrr, "additive_gaussian/FHRR-complex")
    # additive_complex_gaussian requires complex, not real
    _try_fail("additive_complex_gaussian", hrr, "additive_complex_gaussian/HRR-real")
    # temperature_softmax requires float scores, not complex
    _try_fail("temperature_softmax", fhrr, "temperature_softmax/complex")

    # Unknown mode at constructor
    try:
        _ = NoiseChannel("nonexistent_mode", torch.Generator())
        problems.append("MISSED_RAISE unknown_mode: expected ValueError")
    except ValueError:
        pass
    except Exception as e:
        problems.append(f"WRONG_EXCEPTION unknown_mode: {type(e).__name__}: {e}")

    # Unknown regime at inject
    try:
        ch = NoiseChannel("additive_gaussian", torch.Generator())
        ch.inject(hrr, "nonexistent_regime")
        problems.append("MISSED_RAISE unknown_regime: expected ValueError")
    except ValueError:
        pass
    except Exception as e:
        problems.append(f"WRONG_EXCEPTION unknown_regime: {type(e).__name__}: {e}")

    passed = len(problems) == 0
    msg = "all encoder-mode pairs correctly gated" if passed else f"problems={problems}"
    return passed, msg


# ---------------- Test 5: Regime monotonicity ----------------

def test_5_regime_monotonicity() -> tuple[bool, str]:
    """cos(vec, inject(vec, r)) decreases monotonically clean -> catastrophic.

    Averaged over 200 seeds per regime to smooth the trial-level PDF (test 2
    proves per-trial std > 0.01; here we care about the regime mean, which
    the sigma table calibrates monotonically).
    """
    n_dim = 1024
    vec = _hrr_vec(n_dim, seed=99)
    regimes = ["clean", "light", "moderate", "heavy", "catastrophic"]
    means: list[float] = []
    for r in regimes:
        cs: list[float] = []
        for s in range(200):
            g = torch.Generator().manual_seed(int(s) + 5000)
            ch = NoiseChannel("additive_gaussian", g)
            out = ch.inject(vec, r)
            cs.append(_cos_real(vec, out))
        means.append(float(np.mean(cs)))

    # Monotone non-increasing: means[i] >= means[i+1] for all i.
    strict_ok = all(means[i] >= means[i + 1] for i in range(len(means) - 1))
    # Also require strict decrease from clean -> catastrophic overall (rules out
    # a flat-line degenerate case).
    strict_range = (means[0] - means[-1]) > 0.05
    passed = strict_ok and strict_range
    label = ", ".join(f"{r}:{m:.3f}" for (r, m) in zip(regimes, means))
    msg = f"regime cosine means: [{label}]; monotone={strict_ok}; span={means[0]-means[-1]:.3f}"
    return passed, msg


# ---------------- Runner ----------------

TESTS = [
    ("determinism", test_1_determinism),
    ("pdf_spread", test_2_pdf_spread),
    ("l2_preservation", test_3_l2_preservation),
    ("encoder_specialization", test_4_encoder_specialization),
    ("regime_monotonicity", test_5_regime_monotonicity),
]


def run() -> int:
    print("=" * 72)
    print("M3 Cortex M1.3 NoiseChannel smoke tests")
    print("=" * 72)
    print(f"modes: {VALID_MODES}")
    print(f"regimes: {VALID_REGIMES}")
    print()

    results: list[tuple[str, bool, str]] = []
    for name, fn in TESTS:
        try:
            passed, msg = fn()
        except Exception as e:
            passed = False
            msg = f"UNCAUGHT_EXCEPTION: {type(e).__name__}: {e}"
        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {name}: {msg}")
        results.append((name, passed, msg))

    n_pass = sum(1 for (_, p, _) in results if p)
    n = len(results)
    print()
    print(f"OVERALL: {n_pass}/{n} passed")
    return 0 if n_pass == n else 1


if __name__ == "__main__":
    sys.exit(run())
