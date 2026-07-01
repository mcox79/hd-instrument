"""NoiseChannel -- M3 Cortex M1.3 stochastic noise injection at substrate boundary.

Design ref: notes/director_M3_M1_3_stochastic_noise_injection_design_spec_2026-07-01.md

Load-bearing constraint (5x drill 2026-06-30): substrate determinism is STRUCTURAL.
Bipolar bit-flip + L2-renorm gives EXACT cos = 1 - 2*p_flip with std=0 across trials
(count statistic, not stochastic process). Adaptive cells expecting a continuous
confidence PDF over [tau_low, tau_high] see a delta and refuse-gate/tau-selection
has no signal to work with.

Cortex compensation: inject stochastic coupling at the boundary between substrate
reads/writes and adaptive mechanisms so that:
  1. Substrate stays deterministic (capacity bounds, cross-seed reproducibility,
     cross-cell hash-distinctness, cert-architecture guarantees all preserved).
  2. Adaptive cells see noisy input distribution they need.
  3. Injected noise is calibrated to task regime (SNR knob at cortex level).

5 injection modes (encoder-aware):
  - additive_gaussian          : HRR real / FHRR real-part
  - additive_complex_gaussian  : FHRR complex
  - bernoulli_flip_stochastic  : bipolar int8 (fixes trial-level PDF)
  - dropout_mask               : any encoder (per-index Bernoulli zero-mask)
  - temperature_softmax        : post-substrate readout scores

Discipline:
  - NoiseChannel owns its own Generator; do NOT share substrate rng
    (breaks cross-seed determinism at substrate level per design risk #2).
  - All pre-substrate modes preserve L2(vec) via post-inject L2-renorm.
  - Cortex-scoped; does NOT modify Store atoms, W_c/W_h, encoder codebooks,
    or substrate read/write API.

No silent except: unknown mode/regime raise ValueError with the failing name.
"""

from __future__ import annotations

from typing import Union

import numpy as np
import torch


# ---------------- Regime -> sigma calibration table ----------------

# From design spec section "Regime -> sigma table". Calibrated so that
# cosine(vec, inject(vec, 'moderate')) ~= 0.85 (empirically consistent with
# refuse-gate mid_flip=0.40 point where adaptive-tau v2 was supposed to fire).
# Iteratively re-tune per M1.6 empirical calibration on 200-query cert bench.
REGIME_TABLE: dict[str, dict[str, float]] = {
    "clean":         {"sigma": 0.00, "p_flip": 0.00, "drop_frac": 0.00, "T": 1.0},
    "light":         {"sigma": 0.05, "p_flip": 0.02, "drop_frac": 0.05, "T": 1.5},
    "moderate":      {"sigma": 0.15, "p_flip": 0.08, "drop_frac": 0.15, "T": 2.5},
    "heavy":         {"sigma": 0.35, "p_flip": 0.20, "drop_frac": 0.30, "T": 5.0},
    "catastrophic":  {"sigma": 0.60, "p_flip": 0.40, "drop_frac": 0.50, "T": 10.0},
}

VALID_REGIMES: tuple[str, ...] = tuple(REGIME_TABLE.keys())

VALID_MODES: tuple[str, ...] = (
    "additive_gaussian",
    "additive_complex_gaussian",
    "bernoulli_flip_stochastic",
    "dropout_mask",
    "temperature_softmax",
)


# ---------------- Encoder-mode compatibility check ----------------

# Which torch dtypes each mode accepts. Enforced in inject() so wrong-mode
# application surfaces as a typed ValueError.
_MODE_DTYPES: dict[str, tuple[torch.dtype, ...]] = {
    # HRR real / FHRR real-part / any float
    "additive_gaussian": (torch.float32, torch.float64),
    # FHRR complex
    "additive_complex_gaussian": (torch.complex64, torch.complex128),
    # Bipolar (int8 or float representing +/-1); accept both for practicality
    "bernoulli_flip_stochastic": (torch.int8, torch.float32, torch.float64),
    # Any float (encoder-agnostic zero-mask)
    "dropout_mask": (torch.float32, torch.float64, torch.complex64, torch.complex128),
    # Post-substrate scores (real)
    "temperature_softmax": (torch.float32, torch.float64),
}


# ---------------- NoiseChannel ----------------

_RngT = Union[torch.Generator, np.random.Generator]


class NoiseChannel:
    """Cortex-scoped stochastic noise injector at the substrate boundary.

    Owns its own Generator so cross-seed substrate reproducibility is untouched.

    Usage:
        rng = torch.Generator().manual_seed(7)
        ch = NoiseChannel(mode='additive_gaussian', rng=rng)
        noisy = ch.inject(vec, regime='moderate')

    Attributes:
        mode: one of VALID_MODES
        rng: torch.Generator or numpy.random.Generator (owned by this channel)
    """

    def __init__(self, mode: str, rng: _RngT) -> None:
        if mode not in VALID_MODES:
            raise ValueError(
                f"NoiseChannel: unknown mode '{mode}'; valid={VALID_MODES}"
            )
        if not isinstance(rng, (torch.Generator, np.random.Generator)):
            raise ValueError(
                "NoiseChannel: rng must be torch.Generator or np.random.Generator; "
                f"got {type(rng).__name__}"
            )
        self.mode: str = mode
        self.rng: _RngT = rng

    # ---------------- Public API ----------------

    def inject(self, vec: torch.Tensor, regime: str = "moderate") -> torch.Tensor:
        """Inject stochastic noise per self.mode at the specified regime.

        Args:
            vec: input tensor; shape depends on mode:
                additive_gaussian: (B, N) real-float or (N,) real-float
                additive_complex_gaussian: (B, N) complex or (N,) complex
                bernoulli_flip_stochastic: (B, N) int8 or float bipolar
                dropout_mask: (B, N) any encoder dtype
                temperature_softmax: (B, K) scores real-float
            regime: one of VALID_REGIMES.

        Returns:
            Noise-injected tensor of same shape/dtype as input.
            L2 preserved (post-inject L2 within 1e-6 of pre-inject L2) for
            modes 1-4. Mode 5 (temperature_softmax) returns probabilities
            summing to 1 along last dim; L2 not applicable.
        """
        if not isinstance(vec, torch.Tensor):
            raise ValueError(
                f"NoiseChannel.inject: vec must be torch.Tensor; got {type(vec).__name__}"
            )
        if regime not in REGIME_TABLE:
            raise ValueError(
                f"NoiseChannel.inject: unknown regime '{regime}'; valid={VALID_REGIMES}"
            )
        allowed = _MODE_DTYPES[self.mode]
        if vec.dtype not in allowed:
            raise ValueError(
                f"NoiseChannel.inject: mode '{self.mode}' requires dtype in "
                f"{allowed}; got {vec.dtype}"
            )
        params = REGIME_TABLE[regime]

        if self.mode == "additive_gaussian":
            return self._additive_gaussian(vec, sigma=params["sigma"])
        if self.mode == "additive_complex_gaussian":
            return self._additive_complex_gaussian(vec, sigma=params["sigma"])
        if self.mode == "bernoulli_flip_stochastic":
            return self._bernoulli_flip(vec, p_flip=params["p_flip"])
        if self.mode == "dropout_mask":
            return self._dropout_mask(vec, drop_frac=params["drop_frac"])
        if self.mode == "temperature_softmax":
            return self._temperature_softmax(vec, T=params["T"])
        # Unreachable given the constructor guard; kept for defensive completeness.
        raise ValueError(f"NoiseChannel.inject: unhandled mode '{self.mode}'")

    # ---------------- Mode implementations ----------------

    def _additive_gaussian(self, vec: torch.Tensor, sigma: float) -> torch.Tensor:
        """vec + sigma * N(0, I_N); then L2-renorm."""
        if sigma == 0.0:
            return vec.clone()
        noise = torch.empty_like(vec)
        noise.normal_(mean=0.0, std=float(sigma), generator=self._torch_gen())
        out = vec + noise
        return self._l2_renorm_real(out, ref=vec)

    def _additive_complex_gaussian(self, vec: torch.Tensor, sigma: float) -> torch.Tensor:
        """vec + sigma * (N(0,I) + i*N(0,I))/sqrt(2); then complex L2-renorm."""
        if sigma == 0.0:
            return vec.clone()
        # Draw real + imag Gaussians via real-view rng then combine.
        real_dtype = torch.float32 if vec.dtype == torch.complex64 else torch.float64
        std = float(sigma) / float(np.sqrt(2.0))
        re = torch.empty(vec.shape, dtype=real_dtype, device=vec.device)
        im = torch.empty(vec.shape, dtype=real_dtype, device=vec.device)
        re.normal_(mean=0.0, std=std, generator=self._torch_gen())
        im.normal_(mean=0.0, std=std, generator=self._torch_gen())
        noise = torch.complex(re, im)
        out = vec + noise
        return self._l2_renorm_complex(out, ref=vec)

    def _bernoulli_flip(self, vec: torch.Tensor, p_flip: float) -> torch.Tensor:
        """Per-bit Bernoulli(p_flip) flip; then re-normalize to preserve L2.

        Fixes trial-level PDF: substrate's canonical flip is deterministic
        count (`n_bits * flip_frac`); this makes flip_count binomial, giving
        non-degenerate PDF across trials at the same p_flip.
        """
        if p_flip == 0.0:
            return vec.clone()
        # Draw uniform floats; where u < p_flip, flip sign.
        u = torch.empty(vec.shape, dtype=torch.float32, device=vec.device)
        u.uniform_(0.0, 1.0, generator=self._torch_gen())
        flip_mask = (u < float(p_flip))
        # Multiplicative sign flip: keep dtype.
        signs = torch.where(flip_mask, torch.tensor(-1, dtype=vec.dtype, device=vec.device),
                            torch.tensor(1, dtype=vec.dtype, device=vec.device))
        out = vec * signs
        # For bipolar, L2 is naturally preserved (sign flips don't change |x|^2).
        # But renorm defensively for the float case to hit the 1e-6 preservation contract.
        return self._l2_renorm_real(out.to(vec.dtype), ref=vec) if vec.dtype != torch.int8 else out

    def _dropout_mask(self, vec: torch.Tensor, drop_frac: float) -> torch.Tensor:
        """Per-index Bernoulli(p=drop_frac) zero-mask; L2-renorm to preserve norm."""
        if drop_frac == 0.0:
            return vec.clone()
        u = torch.empty(vec.shape, dtype=torch.float32, device=vec.device)
        u.uniform_(0.0, 1.0, generator=self._torch_gen())
        keep = (u >= float(drop_frac))
        if vec.is_complex():
            keep_c = keep.to(vec.real.dtype)
            out = vec * torch.complex(keep_c, torch.zeros_like(keep_c))
            return self._l2_renorm_complex(out, ref=vec)
        out = vec * keep.to(vec.dtype)
        return self._l2_renorm_real(out, ref=vec)

    def _temperature_softmax(self, scores: torch.Tensor, T: float) -> torch.Tensor:
        """softmax(scores / T) along last dim.

        Post-substrate readout: converts deterministic score vector into a
        confidence distribution. T > 1 sharpens uncertainty (flatter);
        T < 1 sharpens confidence (peakier). Regime T-values (1.0..10.0)
        map clean->catastrophic to progressively flatter posteriors.
        """
        if T <= 0.0:
            raise ValueError(f"_temperature_softmax: T must be > 0; got {T}")
        z = scores / float(T)
        z = z - z.amax(dim=-1, keepdim=True)  # numerical stability
        e = torch.exp(z)
        return e / e.sum(dim=-1, keepdim=True)

    # ---------------- Helpers ----------------

    def _torch_gen(self) -> torch.Generator | None:
        """Return the torch.Generator if channel owns one; else None (torch default).

        When rng is a numpy.random.Generator we can't pass it to torch tensor
        methods; instead we sample via numpy and convert. For M1.3 we only
        use the torch path in mode implementations above (numpy path reserved
        for future numpy-native encoders).
        """
        if isinstance(self.rng, torch.Generator):
            return self.rng
        # numpy path: we can't pass numpy Generator to torch.normal_/uniform_.
        # Fall back to a per-call torch.Generator seeded from numpy for reproducibility.
        seed = int(self.rng.integers(0, 2**31 - 1))
        g = torch.Generator(device="cpu")
        g.manual_seed(seed)
        return g

    @staticmethod
    def _l2_renorm_real(out: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
        """Rescale `out` so ||out|| == ||ref|| (per-batch)."""
        # Support (N,) and (B, N)
        if out.dim() == 1:
            ref_norm = torch.linalg.norm(ref.float())
            out_norm = torch.linalg.norm(out.float())
            if float(out_norm) < 1e-12:
                return out
            return (out.float() * (ref_norm / out_norm)).to(out.dtype)
        ref_norm = torch.linalg.norm(ref.float(), dim=-1, keepdim=True)
        out_norm = torch.linalg.norm(out.float(), dim=-1, keepdim=True)
        # Guard tiny norms
        out_norm = torch.clamp(out_norm, min=1e-12)
        return (out.float() * (ref_norm / out_norm)).to(out.dtype)

    @staticmethod
    def _l2_renorm_complex(out: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
        """Complex L2 renorm; ||v||_2 = sqrt(sum |v_i|^2)."""
        if out.dim() == 1:
            ref_norm = torch.sqrt((ref.real**2 + ref.imag**2).sum())
            out_norm = torch.sqrt((out.real**2 + out.imag**2).sum())
            if float(out_norm) < 1e-12:
                return out
            return out * (ref_norm / out_norm)
        ref_norm = torch.sqrt((ref.real**2 + ref.imag**2).sum(dim=-1, keepdim=True))
        out_norm = torch.sqrt((out.real**2 + out.imag**2).sum(dim=-1, keepdim=True))
        out_norm = torch.clamp(out_norm, min=1e-12)
        return out * (ref_norm / out_norm)
