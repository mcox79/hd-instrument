"""hdlab.hippocampal_encoder -- Stage 2 Spoke 3 substrate-native brain-analog primitive.

Composed brain-analog CLS pipeline:

  input (HD)
    -> DGProjection: random EXPANSION (N -> dg_dim) + top-K sparsify + sign
       (Dentate-Gyrus-analog: expansion first, then sparsify; ~1-3% active)
    -> CA3AutoAssociator: Marr-1971 Hebbian outer product on sparse code
       (one-shot binding; pattern completion via one settling step)
    -> optional CLSReplayCycle: replay CA3 attractors as inputs to cortex

Explicitly designed to AVOID the 2026-06-23 sparse_engram_allocation HF mechanism
(naive WTA-collision-sampling with no learning driver + no expansion). This
primitive uses:
  * expansion FIRST (n_dim -> dg_dim), then threshold-sparsify by magnitude
    (not by pre-allocation collision-minimization)
  * a LEARNING driver in CA3 (Hebbian outer product on the sparse DG code) --
    not pure allocation
  * target sparsity ~1% (not 0.25%)

References (brain-analog):
  * Marr 1971 -- CA3 auto-associator theory
  * McClelland/McNaughton/O'Reilly 1995 -- Complementary Learning Systems
  * Wilson/McNaughton 1994 -- hippocampal replay during SWS

Follows CLAUDE.md conventions: numpy arrays at API boundary (existing
substrate-encoder convention in ppmi_sparse_encoder / char_trigram_encoder),
explicit dtype=float32, one-line docstrings with shape annotations, no emojis,
ASCII-only. Deterministic w.r.t. rng seed.

Selftests are invoked via
    python -m hdlab.hippocampal_encoder --self-test
which is what the smoke cell's --self-test path chains into.
"""
from __future__ import annotations

import argparse
import sys
import traceback
from dataclasses import dataclass
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sparse_topk_mask(magnitudes: np.ndarray, target_rate: float) -> np.ndarray:
    """Boolean mask keeping top-target_rate fraction of dims by magnitude. [d]->[d]bool."""
    d = int(magnitudes.shape[0])
    k = max(1, int(round(float(target_rate) * d)))
    if k >= d:
        return np.ones_like(magnitudes, dtype=bool)
    # threshold = k-th largest value (using partition on the (d-k)-th index).
    threshold = np.partition(magnitudes, d - k)[d - k]
    return magnitudes >= threshold


def _unit_norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """L2-normalize the last axis. [..., d] -> [..., d]."""
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / (n + eps)


# ---------------------------------------------------------------------------
# DGProjection: expansion + top-K sparsify (Dentate-Gyrus analog)
# ---------------------------------------------------------------------------

@dataclass
class DGProjection:
    """Fixed random expansion projection + top-K threshold. Sparse ternary output.

    Params:
        input_dim  : cortex HD dim (e.g. 2048)
        dg_dim     : expanded DG dim (e.g. 8192 for 4x expansion). Must be > input_dim.
        sparsity   : fraction of dg dims kept (top-K by magnitude); target ~0.01-0.03.
        seed       : rng seed for the projection matrix.

    encode(x): [input_dim] -> ternary {-1, 0, +1} [dg_dim]
    """

    input_dim: int
    dg_dim: int
    sparsity: float
    seed: int = 0

    def __post_init__(self) -> None:
        if self.dg_dim <= self.input_dim:
            raise ValueError(
                f"DGProjection requires expansion: dg_dim ({self.dg_dim}) must be "
                f"strictly greater than input_dim ({self.input_dim})."
            )
        if not (0.0 < self.sparsity < 1.0):
            raise ValueError(f"sparsity must be in (0, 1); got {self.sparsity}")
        rng = np.random.default_rng(int(self.seed) * 991 + 7)
        # Bipolar {+1, -1} projection scaled by 1/sqrt(input_dim) (approx JL).
        self._P = ((rng.integers(0, 2, size=(self.dg_dim, self.input_dim)) * 2 - 1)
                   .astype(np.float32))
        self._P *= 1.0 / np.sqrt(float(self.input_dim))

    def encode(self, x: np.ndarray) -> np.ndarray:
        """Expand + sign-preserving top-K threshold. [input_dim] -> ternary [dg_dim]."""
        if x.ndim != 1 or x.shape[0] != self.input_dim:
            raise ValueError(
                f"DGProjection.encode expects [input_dim={self.input_dim}]; "
                f"got shape {x.shape}"
            )
        dense = self._P @ x.astype(np.float32)  # [dg_dim]
        mag = np.abs(dense)
        mask = _sparse_topk_mask(mag, self.sparsity)
        sign = np.sign(dense).astype(np.float32)
        sign[sign == 0] = 1.0
        return sign * mask.astype(np.float32)

    def encode_batch(self, X: np.ndarray) -> np.ndarray:
        """Batched. [n, input_dim] -> ternary [n, dg_dim]."""
        if X.ndim != 2 or X.shape[1] != self.input_dim:
            raise ValueError(
                f"DGProjection.encode_batch expects [n, {self.input_dim}]; "
                f"got shape {X.shape}"
            )
        dense = X.astype(np.float32) @ self._P.T  # [n, dg_dim]
        mag = np.abs(dense)
        d = self.dg_dim
        k = max(1, int(round(self.sparsity * d)))
        if k >= d:
            mask = np.ones_like(mag, dtype=bool)
        else:
            # per-row threshold via np.partition on axis=1
            thresh = np.partition(mag, d - k, axis=1)[:, d - k][:, None]
            mask = mag >= thresh
        sign = np.sign(dense).astype(np.float32)
        sign[sign == 0] = 1.0
        return sign * mask.astype(np.float32)

    def sparse_rate(self, code: np.ndarray) -> float:
        """Fraction of nonzero entries in a code. Diagnostics."""
        if code.ndim == 1:
            return float(np.count_nonzero(code)) / float(code.shape[0])
        return float(np.count_nonzero(code)) / float(code.size)


# ---------------------------------------------------------------------------
# CA3AutoAssociator: Marr Hebbian outer product on sparse codes.
# ---------------------------------------------------------------------------

class CA3AutoAssociator:
    """Sparse Hebbian outer-product auto-associator (Marr 1971).

    write(code): W += outer(code, code) -- one-shot Hebbian.
    settle(cue): return sign(W @ cue) -- one-step pattern completion.

    Sparse outer-product update: only nonzeros contribute -> K^2 per write.
    """

    def __init__(self, dg_dim: int) -> None:
        if dg_dim <= 0:
            raise ValueError(f"dg_dim must be > 0; got {dg_dim}")
        self.dim = int(dg_dim)
        self.W = np.zeros((self.dim, self.dim), dtype=np.float32)
        self.n_written = 0

    def write(self, code: np.ndarray) -> None:
        """One-shot Hebbian write: W += outer(code, code). [dg_dim]."""
        if code.ndim != 1 or code.shape[0] != self.dim:
            raise ValueError(
                f"CA3AutoAssociator.write expects [dg_dim={self.dim}]; "
                f"got shape {code.shape}"
            )
        nz = np.nonzero(code)[0]
        if nz.size == 0:
            return
        sub = code[nz].astype(np.float32)
        self.W[np.ix_(nz, nz)] += np.outer(sub, sub)
        self.n_written += 1

    def settle(self, cue: np.ndarray) -> np.ndarray:
        """One-step settling: sign(W @ cue). [dg_dim] -> ternary [dg_dim]."""
        if cue.ndim != 1 or cue.shape[0] != self.dim:
            raise ValueError(
                f"CA3AutoAssociator.settle expects [dg_dim={self.dim}]; "
                f"got shape {cue.shape}"
            )
        if self.n_written == 0:
            return cue.copy()
        act = self.W @ cue.astype(np.float32)
        out = np.sign(act).astype(np.float32)
        out[out == 0] = 1.0
        return out

    def settle_batch(self, cues: np.ndarray) -> np.ndarray:
        """Batched one-step settle. [n, dg_dim] -> ternary [n, dg_dim]."""
        if cues.ndim != 2 or cues.shape[1] != self.dim:
            raise ValueError(
                f"CA3AutoAssociator.settle_batch expects [n, {self.dim}]; "
                f"got shape {cues.shape}"
            )
        if self.n_written == 0:
            return cues.copy()
        act = cues.astype(np.float32) @ self.W.T
        out = np.sign(act).astype(np.float32)
        out[out == 0] = 1.0
        return out

    def settle_batch_activations(self, cues: np.ndarray) -> np.ndarray:
        """Batched one-step raw activation W @ cue. [n, dg_dim] -> float [n, dg_dim].

        Preserves magnitude for downstream top-K sparsification (keeps output
        in the sparse DG-code manifold). Used by HippocampalEncoder.retrieve
        when sparsify_after_settle is True.
        """
        if cues.ndim != 2 or cues.shape[1] != self.dim:
            raise ValueError(
                f"CA3AutoAssociator.settle_batch_activations expects [n, {self.dim}]; "
                f"got shape {cues.shape}"
            )
        if self.n_written == 0:
            return cues.copy()
        return cues.astype(np.float32) @ self.W.T


# ---------------------------------------------------------------------------
# HippocampalEncoder: composed pipeline DG -> CA3 (+ optional replay).
# ---------------------------------------------------------------------------

class HippocampalEncoder:
    """Composed brain-analog pipeline: input HD -> DG sparse -> CA3 auto-assoc.

    Params:
        input_dim   : cortex HD dim
        dg_dim      : expanded DG dim (target 2-8x input_dim)
        sparsity    : DG target rate (top-K); ~0.01-0.03
        seed        : rng seed for DG projection

    encode_and_write(X): [n, input_dim] fits CA3 auto-associator with sparse DG codes.
    retrieve(Q): [n_q, input_dim] -> settled sparse [n_q, dg_dim] pattern-completed codes.
    """

    def __init__(self, input_dim: int, dg_dim: int, sparsity: float,
                 seed: int = 0) -> None:
        self.input_dim = int(input_dim)
        self.dg_dim = int(dg_dim)
        self.sparsity = float(sparsity)
        self.seed = int(seed)
        self.dg = DGProjection(input_dim=self.input_dim, dg_dim=self.dg_dim,
                               sparsity=self.sparsity, seed=self.seed)
        self.ca3 = CA3AutoAssociator(dg_dim=self.dg_dim)
        self._stored_dg_codes: Optional[np.ndarray] = None

    def encode_and_write(self, X: np.ndarray) -> np.ndarray:
        """DG-encode + store each row into CA3 as an attractor. [n, in] -> ternary [n, dg]."""
        codes = self.dg.encode_batch(X)
        for i in range(codes.shape[0]):
            self.ca3.write(codes[i])
        self._stored_dg_codes = codes
        return codes

    def retrieve(self, Q: np.ndarray, use_ca3: bool = True,
                 sparsify_after_settle: bool = True) -> np.ndarray:
        """DG-encode query, optionally settle via CA3. [n_q, in] -> ternary [n_q, dg].

        sparsify_after_settle: if True, keep top-K by |W @ cue| and sign-preserve
        (keeps output in the sparse DG-code manifold at target rate); if False,
        return dense-ternary sign(W @ cue) (classical Marr settle).
        """
        codes = self.dg.encode_batch(Q)
        if not use_ca3 or self.ca3.n_written == 0:
            return codes
        if not sparsify_after_settle:
            return self.ca3.settle_batch(codes)
        act = self.ca3.settle_batch_activations(codes)  # [n_q, dg_dim] float
        mag = np.abs(act)
        d = self.dg_dim
        k = max(1, int(round(self.sparsity * d)))
        if k >= d:
            mask = np.ones_like(mag, dtype=bool)
        else:
            thresh = np.partition(mag, d - k, axis=1)[:, d - k][:, None]
            mask = mag >= thresh
        sign = np.sign(act).astype(np.float32)
        sign[sign == 0] = 1.0
        return sign * mask.astype(np.float32)

    def dg_sparse_rate(self, codes: np.ndarray) -> float:
        """Fraction of nonzero entries in the codes. Diagnostic."""
        return self.dg.sparse_rate(codes)


# ---------------------------------------------------------------------------
# CLSReplayCycle: replay CA3 attractors to cortex Hebbian rule.
# ---------------------------------------------------------------------------

def cls_replay_cycle(ca3: CA3AutoAssociator, stored_codes: np.ndarray,
                     cortex_W: Optional[np.ndarray], n_cycles: int,
                     lr: float = 0.05) -> np.ndarray:
    """Replay stored CA3 attractors as inputs to a cortical W over n_cycles.

    stored_codes: [n_items, dg_dim]. cortex_W: [dg_dim, dg_dim] or None (created).
    Returns updated cortex_W (Hebbian: W += lr * outer(code, settle(code))).
    This is a minimal composition point; the FULL cortex is Spoke1+2 and would
    receive projected codes rather than raw DG. Kept minimal to selftest replay
    semantics -- production consolidation is a v2 concern.
    """
    dg_dim = stored_codes.shape[1]
    if cortex_W is None:
        cortex_W = np.zeros((dg_dim, dg_dim), dtype=np.float32)
    for _ in range(int(n_cycles)):
        # random walk through stored codes (approximates replay order jitter)
        idx = np.arange(stored_codes.shape[0])
        for i in idx:
            settled = ca3.settle(stored_codes[i])
            cortex_W += lr * np.outer(stored_codes[i], settled).astype(np.float32)
    return cortex_W


# ===========================================================================
# SELFTESTS -- 10+ mechanism-level assertions per USER-locked design mandates.
# ===========================================================================

def _cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _st_dg_output_ternary() -> None:
    """DG output must be ternary {-1, 0, +1}."""
    dg = DGProjection(input_dim=64, dg_dim=256, sparsity=0.02, seed=11)
    x = np.random.default_rng(1).standard_normal(64).astype(np.float32)
    c = dg.encode(x)
    uniq = np.unique(c)
    assert set(uniq.tolist()).issubset({-1.0, 0.0, 1.0}), (
        f"DG output not ternary: got unique values {uniq}"
    )
    print(f"[selftest dg_output_ternary] PASS unique={uniq.tolist()}", flush=True)


def _st_dg_sparse_rate_matches_target() -> None:
    """DG sparse rate must land within [0.5*target, 2*target] over a small batch."""
    dg = DGProjection(input_dim=128, dg_dim=1024, sparsity=0.02, seed=17)
    rng = np.random.default_rng(3)
    X = rng.standard_normal((20, 128)).astype(np.float32)
    C = dg.encode_batch(X)
    rate = float(np.count_nonzero(C)) / float(C.size)
    assert 0.5 * 0.02 <= rate <= 2.0 * 0.02, (
        f"DG sparse rate {rate:.4f} outside band [0.01, 0.04] for target 0.02"
    )
    print(f"[selftest dg_sparse_rate_matches_target] PASS rate={rate:.4f}", flush=True)


def _st_dg_pattern_separation() -> None:
    """Similar inputs get more-different DG codes (code_cos < input_cos - 0.2).

    This is the load-bearing DG property: expansion + top-K threshold
    amplifies small input differences into larger code differences.
    The size of the drop depends on input_cos and sparsity; here we assert
    a monotone gap (code less similar than input) of >= 0.20.
    """
    rng = np.random.default_rng(5)
    x1 = rng.standard_normal(256).astype(np.float32)
    # Moderate perturbation to make cos ~ 0.85-0.95.
    x2 = (x1 + 0.40 * rng.standard_normal(256)).astype(np.float32)
    input_cos = _cos_sim(x1, x2)
    dg = DGProjection(input_dim=256, dg_dim=2048, sparsity=0.02, seed=29)
    c1 = dg.encode(x1)
    c2 = dg.encode(x2)
    code_cos = _cos_sim(c1, c2)
    assert code_cos < input_cos - 0.20, (
        f"DG pattern separation gap too small: input_cos={input_cos:.3f} "
        f"code_cos={code_cos:.3f} (expected code_cos < input_cos - 0.20)"
    )
    print(f"[selftest dg_pattern_separation] PASS input_cos={input_cos:.3f} "
          f"code_cos={code_cos:.3f} gap={input_cos - code_cos:.3f}", flush=True)


def _st_dg_determinism() -> None:
    """Same seed + input -> bit-identical DG code."""
    x = np.random.default_rng(9).standard_normal(64).astype(np.float32)
    dg1 = DGProjection(input_dim=64, dg_dim=512, sparsity=0.02, seed=101)
    dg2 = DGProjection(input_dim=64, dg_dim=512, sparsity=0.02, seed=101)
    c1 = dg1.encode(x)
    c2 = dg2.encode(x)
    assert np.array_equal(c1, c2), "DG projection not deterministic under same seed"
    print("[selftest dg_determinism] PASS", flush=True)


def _st_dg_dim_mismatch_guard() -> None:
    """DGProjection rejects input_dim >= dg_dim (no expansion)."""
    try:
        DGProjection(input_dim=256, dg_dim=256, sparsity=0.02, seed=0)
    except ValueError:
        print("[selftest dg_dim_mismatch_guard] PASS (equal dim rejected)", flush=True)
        return
    raise AssertionError("DGProjection should reject dg_dim == input_dim")


def _st_dg_sparsity_bound_guard() -> None:
    """DGProjection rejects sparsity outside (0, 1)."""
    for bad in [0.0, 1.0, 1.5, -0.1]:
        try:
            DGProjection(input_dim=64, dg_dim=256, sparsity=bad, seed=0)
        except ValueError:
            continue
        raise AssertionError(f"DGProjection accepted invalid sparsity {bad}")
    print("[selftest dg_sparsity_bound_guard] PASS", flush=True)


def _st_ca3_one_shot_binding_recall() -> None:
    """After ONE write, CA3 completes the exact pattern from itself (recall > 0.99).

    This is the minimum Marr-CA3 requirement: writing pattern p to CA3 then
    settling from p yields p (up to sign of zero-activation dims).
    """
    dg_dim = 1024
    ca3 = CA3AutoAssociator(dg_dim=dg_dim)
    rng = np.random.default_rng(31)
    # sparse ternary pattern with ~2% density
    k = int(0.02 * dg_dim)
    idx = rng.choice(dg_dim, size=k, replace=False)
    signs = (rng.integers(0, 2, size=k) * 2 - 1).astype(np.float32)
    p = np.zeros(dg_dim, dtype=np.float32)
    p[idx] = signs
    ca3.write(p)
    p_ret = ca3.settle(p)
    # p_ret is dense-ternary; compare sign-agreement on active dims of p
    n_agree = int(np.sum(np.sign(p_ret[idx]) == signs))
    frac = n_agree / float(k)
    assert frac >= 0.99, f"CA3 self-recall failed: sign-agreement {frac:.3f} < 0.99"
    print(f"[selftest ca3_one_shot_binding_recall] PASS sign_agree={frac:.3f}",
          flush=True)


def _st_ca3_pattern_completion_from_partial_cue() -> None:
    """After one write of pattern p, 50%-partial cue completes to >= 0.90 sign-agree.

    Load-bearing property: Marr auto-associator recovers p from a fraction of p.
    """
    dg_dim = 2048
    ca3 = CA3AutoAssociator(dg_dim=dg_dim)
    rng = np.random.default_rng(43)
    k = int(0.02 * dg_dim)  # 40 active dims
    idx = rng.choice(dg_dim, size=k, replace=False)
    signs = (rng.integers(0, 2, size=k) * 2 - 1).astype(np.float32)
    p = np.zeros(dg_dim, dtype=np.float32)
    p[idx] = signs
    ca3.write(p)
    # Partial cue: 50% of active dims retained
    keep = rng.choice(k, size=k // 2, replace=False)
    cue = np.zeros(dg_dim, dtype=np.float32)
    cue[idx[keep]] = signs[keep]
    p_ret = ca3.settle(cue)
    n_agree = int(np.sum(np.sign(p_ret[idx]) == signs))
    frac = n_agree / float(k)
    assert frac >= 0.90, (
        f"CA3 partial-cue completion failed: sign-agreement {frac:.3f} < 0.90 "
        f"on 50%-partial cue"
    )
    print(f"[selftest ca3_pattern_completion_from_partial_cue] PASS "
          f"sign_agree={frac:.3f}", flush=True)


def _st_ca3_dim_mismatch_guard() -> None:
    """CA3 rejects wrong-dim inputs."""
    ca3 = CA3AutoAssociator(dg_dim=128)
    try:
        ca3.write(np.zeros(64, dtype=np.float32))
    except ValueError:
        pass
    else:
        raise AssertionError("CA3.write should reject wrong-dim")
    try:
        ca3.settle(np.zeros(64, dtype=np.float32))
    except ValueError:
        pass
    else:
        raise AssertionError("CA3.settle should reject wrong-dim")
    print("[selftest ca3_dim_mismatch_guard] PASS", flush=True)


def _st_hippo_encoder_end_to_end_recall() -> None:
    """Compose: encode_and_write(X) then retrieve(X, sparsify=True) yields high recall.

    With sparsify_after_settle=True the retrieved code stays in the sparse
    DG-code manifold; comparing to stored code via cosine should be high.
    """
    enc = HippocampalEncoder(input_dim=64, dg_dim=512, sparsity=0.02, seed=7)
    rng = np.random.default_rng(11)
    X = rng.standard_normal((10, 64)).astype(np.float32)
    stored = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    cs = []
    for i in range(X.shape[0]):
        cs.append(_cos_sim(ret[i], stored[i]))
    mean_c = float(np.mean(cs))
    assert mean_c >= 0.7, f"end-to-end recall failed: mean cos={mean_c:.3f} < 0.7"
    print(f"[selftest hippo_encoder_end_to_end_recall] PASS mean_cos={mean_c:.3f}",
          flush=True)


def _st_hippo_ne_naive_wta_collision_2026_06_23() -> None:
    """Verify at MECHANISM level: this primitive is NOT naive WTA-collision sampling.

    The 2026-06-23 falsified mechanism (a) started sparse (no expansion) and
    (b) picked K dims by lowest collision, with NO input-dependent projection.
    Our primitive is architecturally different:
      * dg_dim > input_dim (expansion enforced in __post_init__)
      * dim selection is input-driven (top-K by |P x| magnitude), not by
        pre-registered collision counts
      * learning driver via Hebbian outer product in CA3 (not pure allocation)

    Empirical check: two different inputs pick DIFFERENT DG dims (top-K sets
    differ substantially) -- proving selection is input-driven, not fixed.
    """
    dg = DGProjection(input_dim=128, dg_dim=1024, sparsity=0.03, seed=57)
    rng = np.random.default_rng(13)
    x1 = rng.standard_normal(128).astype(np.float32)
    x2 = rng.standard_normal(128).astype(np.float32)
    c1 = dg.encode(x1)
    c2 = dg.encode(x2)
    s1 = set(np.nonzero(c1)[0].tolist())
    s2 = set(np.nonzero(c2)[0].tolist())
    jaccard = len(s1 & s2) / max(1, len(s1 | s2))
    assert jaccard < 0.6, (
        f"DG top-K sets not input-driven (jaccard={jaccard:.3f} >= 0.6). "
        f"Collision-sampling detected."
    )
    print(f"[selftest hippo_ne_naive_wta_collision] PASS jaccard={jaccard:.3f}",
          flush=True)


def _st_hippo_scale_sentinel_n8192() -> None:
    """Scale sentinel: at input_dim=2048, dg_dim=8192, sparsity=0.02 the encode
    runs and produces expected sparse rate."""
    enc = HippocampalEncoder(input_dim=2048, dg_dim=8192, sparsity=0.02, seed=7)
    rng = np.random.default_rng(23)
    X = rng.standard_normal((5, 2048)).astype(np.float32)
    codes = enc.encode_and_write(X)
    rate = float(np.count_nonzero(codes)) / float(codes.size)
    assert 0.010 <= rate <= 0.040, (
        f"scale sentinel: rate {rate:.4f} outside expected [0.01, 0.04] "
        f"for sparsity=0.02"
    )
    print(f"[selftest hippo_scale_sentinel_n8192] PASS rate={rate:.4f}", flush=True)


def _st_hippo_arms_differ() -> None:
    """DG-only vs DG+CA3 differ on NOVEL queries (not stored patterns).

    When CA3 stores {p1..pN} and query q is different from all pi, DG-only
    returns q's raw DG code while DG+CA3 completes q -> nearest attractor.
    The two outputs must differ.
    """
    import hashlib
    enc = HippocampalEncoder(input_dim=128, dg_dim=1024, sparsity=0.02, seed=41)
    rng = np.random.default_rng(19)
    X_train = rng.standard_normal((10, 128)).astype(np.float32)
    enc.encode_and_write(X_train)
    # Novel queries (different draws than X_train).
    Q_novel = rng.standard_normal((5, 128)).astype(np.float32)
    ret_dg_only = enc.retrieve(Q_novel, use_ca3=False)
    ret_dg_ca3 = enc.retrieve(Q_novel, use_ca3=True, sparsify_after_settle=True)
    h_dg = hashlib.sha256(ret_dg_only.tobytes()).hexdigest()
    h_ca3 = hashlib.sha256(ret_dg_ca3.tobytes()).hexdigest()
    assert h_dg != h_ca3, (
        f"arms bit-identical (hash={h_dg}) on novel queries despite "
        f"CA3 write of {enc.ca3.n_written} items"
    )
    # Require sym-diff on at least one row -- CA3 should pull novel toward attractors.
    max_diff = 0.0
    for i in range(Q_novel.shape[0]):
        s1 = set(np.nonzero(ret_dg_only[i])[0].tolist())
        s2 = set(np.nonzero(ret_dg_ca3[i])[0].tolist())
        diff = len(s1 ^ s2) / max(1, len(s1 | s2))
        max_diff = max(max_diff, diff)
    assert max_diff >= 0.05, (
        f"CA3 settle barely changed any novel query DG code "
        f"(max_sym_diff={max_diff:.3f} < 0.05)"
    )
    print(f"[selftest hippo_arms_differ] PASS h_dg={h_dg[:8]} h_ca3={h_ca3[:8]} "
          f"max_sym_diff={max_diff:.3f}", flush=True)


_SELFTESTS = [
    ("dg_output_ternary", _st_dg_output_ternary),
    ("dg_sparse_rate_matches_target", _st_dg_sparse_rate_matches_target),
    ("dg_pattern_separation", _st_dg_pattern_separation),
    ("dg_determinism", _st_dg_determinism),
    ("dg_dim_mismatch_guard", _st_dg_dim_mismatch_guard),
    ("dg_sparsity_bound_guard", _st_dg_sparsity_bound_guard),
    ("ca3_one_shot_binding_recall", _st_ca3_one_shot_binding_recall),
    ("ca3_pattern_completion_from_partial_cue",
     _st_ca3_pattern_completion_from_partial_cue),
    ("ca3_dim_mismatch_guard", _st_ca3_dim_mismatch_guard),
    ("hippo_encoder_end_to_end_recall", _st_hippo_encoder_end_to_end_recall),
    ("hippo_ne_naive_wta_collision_2026_06_23",
     _st_hippo_ne_naive_wta_collision_2026_06_23),
    ("hippo_scale_sentinel_n8192", _st_hippo_scale_sentinel_n8192),
    ("hippo_arms_differ", _st_hippo_arms_differ),
]


def run_all_selftests() -> int:
    failed = []
    for name, fn in _SELFTESTS:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, f"AssertionError: {e}"))
            print(f"[selftest {name}] FAIL: {e}", flush=True)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(_SELFTESTS) - len(failed)}/{len(_SELFTESTS)} "
          f"passed", flush=True)
    return 0 if not failed else 1


def _main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args, _ = ap.parse_known_args()
    if args.self_test:
        return run_all_selftests()
    # Default: also run selftests when module invoked directly.
    return run_all_selftests()


if __name__ == "__main__":
    sys.exit(_main())
