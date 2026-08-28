"""Scalar-adjective magnitude channel -- the "ruler" meaning operation for gradable adjectives (hot/cold, big/small).

Landed 2026-08-28 (landing-step 2 of the integrated `build_the_composed_scalar_magnitude_meaning_channel`,
SOLVED/EXCELLENT, owner-DONE). One callable magnitude channel: dimension -> grounded ORIENTED axis (pole+degree unified
place code) -> markedness fine-degree -> FPE(log degree) substrate code -> `unbind` comparator. Ports the validated
`ScalarMagnitudeChannel` VERBATIM; builds on the landed `hdlab.fractional_power_encoding` (an hdlab organ cannot import
`experiments/`).

WHAT IS PINNED (copy the operation):
  * The brain builds magnitude from OPPONENT monotonic pools into a peaked log-Gaussian place code, read out on ONE
    ORIENTED signed axis (Roitman/Brannon/Platt LIP more/less pools; Nieder log-Gaussian; Verguts & Fias 2004; SNARC).
    CONSEQUENCE: pole and degree are NOT two operations -- once the axis is ORIENTED by the pole, one signed projection
    carries BOTH. `oriented_position` is that single grounded oriented readout.
  * DEGREE = LOG-distance from a context standard (Kennedy reference-point; Moyer distance effect). Markedness = -log(freq)
    IS a log-distance from the unmarked default (Horn/Zipf); the log is pinned by Laughlin efficient coding.
  * DIMENSION/standard SELECTION is semantic control (LIFG/pMTG) -- the dimension is an INPUT here (wire to
    `hdlab.semantic_control` at the composition step). GROUNDING is PER-DIMENSION: evaluative dims from antonym/SemAxis
    poles; denotational (concreteness) from Lancaster perceptual strength.
  * The stored form binds a DISCRETE pole+dimension symbol: code = bind(bind(DIM_key, POLE_key), FPE_log(degree)); the
    comparator is a native `unbind` (== FPE_log(degree1/degree2), the Weber ratio signal).

WHAT IS OUR-INVENTION-UNDER-TEST (honestly labelled): the exact FHRR binding scheme; the FPE rate distribution; the
gradability gate (the ROUTER, a separate step). The offline static assets (GloVe word vectors `gv`, word frequency `freq`,
Lancaster perceptual strength `lanc`) are SUPPLIED by the caller (admissible offline foundation) -- this organ is the
OPERATION, not the asset loader.

VALIDATED (re-verified FIRST-HAND at integration, `verify_composed_magnitude_channel.py` ALL PASS): the composed channel
beats the strongest single sub-op (+0.081 CI-sep) AND the incumbent cosine (+0.40 CI-sep) on human VAD+concreteness
(Warriner + Brysbaert, n~3600-5300); as a COMPARISON system it beats the incumbent CLEANLY (relative-comparison 0.758 vs
0.552 +0.206 CI-sep, Moyer distance effect +0.340, semantic-congruity AUC 1.000 where the incumbent gloss cosine INVERTS
to 0.215); FPE-log preserves Weber on-substrate (ratio-CV 0.000 vs 0.686 linear). Info-free twins lose (random-axis,
shuffled-degree, structure-free FPE). HONEST: the sub-op CI-win is concreteness-routing (evaluative dims tie the antonym
SemAxis by construction); markedness/FPE-log's value is the comparison + Weber code, not static rating recovery.

DEFAULT-SAFE island: new module, nothing imports it (the ROUTER that dispatches gradable adjectives to this channel is the
next landing step). Reuses `hdlab.fractional_power_encoding`, `hdlab.binding`, `hdlab.situation_model_accumulate.unit_phase_vec`.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

import numpy as np
import torch

from . import binding
from . import fractional_power_encoding as fpe
from .situation_model_accumulate import unit_phase_vec

DEFAULT_D_SUB = 4096
DEFAULT_SEED = 20260827

EVAL_DIMS: List[str] = ["valence", "arousal", "dominance", "concreteness"]
DENOTATIONAL = {"concreteness"}          # grounded PERCEPTUALLY (Lancaster), not by antonym poles (PROBE C)

# A-priori bipolar pole seed pairs (SemAxis): the axis is ANCHORED by the explicit antonym relation, position is geometric.
DIM_SEEDS: Dict[str, List[tuple]] = {
    "valence":      [("good", "bad"), ("pleasant", "unpleasant"), ("happy", "sad"),
                     ("positive", "negative"), ("nice", "nasty"), ("wonderful", "awful")],
    "arousal":      [("exciting", "boring"), ("active", "passive"), ("energetic", "sluggish"),
                     ("intense", "calm"), ("aroused", "relaxed"), ("frantic", "peaceful")],
    "dominance":    [("powerful", "weak"), ("dominant", "submissive"), ("strong", "helpless"),
                     ("controlling", "controlled"), ("mighty", "powerless")],
    "concreteness": [("concrete", "abstract"), ("physical", "mental"), ("tangible", "intangible"),
                     ("material", "spiritual"), ("solid", "imaginary")],
}


def dim_axis(dim: str, gv: Dict[str, np.ndarray]) -> Optional[np.ndarray]:
    """Grounded bipolar axis for an evaluative dim: normalized mean pole-difference over the seed pairs (SemAxis)."""
    diffs = [gv[a] - gv[b] for a, b in DIM_SEEDS[dim] if a in gv and b in gv]
    if not diffs:
        return None
    ax = np.mean(diffs, axis=0)
    return ax / (np.linalg.norm(ax) + 1e-12)


class ScalarMagnitudeChannel:
    """One callable magnitude meaning channel. `oriented_position` = routed grounded readout; `signed_magnitude` =
    pole x log-degree comparison readout; `code` = the stored FHRR form; `compare` = the unbind ratio comparator."""

    def __init__(self, gv: Dict[str, np.ndarray], freq: Dict[str, float], lanc: Dict[str, float],
                 d_sub: int = DEFAULT_D_SUB, seed: int = DEFAULT_SEED) -> None:
        self.gv = gv
        self.freq = freq
        self.lanc = lanc
        self.d_sub = int(d_sub)
        self.seed = int(seed)
        self._axis: Dict[str, np.ndarray] = {}
        self._rates = fpe.phase_rates("gauss", d_sub, seed, sigma=1.0)                       # shared log-phase axis
        self._dim_key = {d: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 100 + i))
                         for i, d in enumerate(EVAL_DIMS)}
        self._pole_key = {+1: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 200)),
                          -1: unit_phase_vec(d_sub, torch.Generator().manual_seed(seed + 201))}

    def axis(self, dim: str) -> Optional[np.ndarray]:
        """Grounded bipolar axis: evaluative from antonym/SemAxis poles; denotational from Lancaster perceptual (PROBE C)."""
        if dim in self._axis:
            return self._axis[dim]
        ax = self._perceptual_axis() if dim in DENOTATIONAL else dim_axis(dim, self.gv)
        if ax is not None:
            self._axis[dim] = ax
        return ax

    def _perceptual_axis(self) -> Optional[np.ndarray]:
        anchor = sorted(set(self.lanc) & set(self.gv))
        if not anchor:
            return None
        ap = np.array([self.lanc[w] for w in anchor])
        hi = [w for w in anchor if self.lanc[w] >= np.percentile(ap, 90)]
        lo = [w for w in anchor if self.lanc[w] <= np.percentile(ap, 10)]
        if not hi or not lo:
            return None
        pax = np.mean([self.gv[w] for w in hi], axis=0) - np.mean([self.gv[w] for w in lo], axis=0)
        return pax / (np.linalg.norm(pax) + 1e-12)

    def oriented_position(self, w: str, dim: str) -> Optional[float]:
        """Routed grounded oriented projection (the unified pole+degree place code; higher = more of the dim)."""
        ax = self.axis(dim)
        if w not in self.gv or ax is None:
            return None
        return float(self.gv[w] @ ax)

    def pole(self, w: str, dim: str) -> Optional[int]:
        p = self.oriented_position(w, dim)
        return None if p is None else (1 if p >= 0 else -1)

    def degree(self, w: str) -> Optional[float]:
        """Markedness degree ~= log-distance from the unmarked standard: -log(frequency) (Horn/Zipf; log PINNED by
        Laughlin efficient coding). Positive, monotone in rarity."""
        f = self.freq.get(w)
        if f is None or f <= 0:
            return None
        return float(-np.log(f + 0.1) + np.log(1e6))

    def signed_magnitude(self, w: str, dim: str) -> Optional[float]:
        pl, dg = self.pole(w, dim), self.degree(w)
        return None if (pl is None or dg is None) else pl * dg

    def code(self, w: str, dim: str) -> Optional[torch.Tensor]:
        """Stored form: bind(DIM_key, POLE_key, FPE_log(degree)). Composable FHRR vector."""
        pl, dg = self.pole(w, dim), self.degree(w)
        if pl is None or dg is None or dim not in self._dim_key or dg <= 0:
            return None
        return binding.bind(binding.bind(self._dim_key[dim], self._pole_key[pl]), fpe.log_encode(self._rates, dg))

    def compare(self, w1: str, w2: str, dim: str) -> Optional[torch.Tensor]:
        """Native ratio comparator: unbind(code(w1), code(w2)) == FPE_log(degree1/degree2) for same-pole pairs."""
        c1, c2 = self.code(w1, dim), self.code(w2, dim)
        return None if (c1 is None or c2 is None) else binding.unbind(c1, c2)
