"""GSBC graded-code (Generalized Sparse Block Code) encoder -- density m survivors.

Recovers the certified encoder MECHANISM from
experiments/exp_encoder_gsbc_gradedcode_marginpush_v1* (ship density m=5): the
block-wise top-m GRADED positive survivors, unit-L1 per block. This is the
deployed eval-time transform from that arc (v11 _encode_gsbc FORWARD, ported to
numpy to match the sibling KB encoders in hdlab/ which are numpy at the API
boundary), NOT the training scaffold.

MECHANISM (per block of blk_l coordinates, kb blocks, n_dim = kb * blk_l):
  1. Take |z| magnitudes.
  2. Keep the top-m largest magnitudes per block, zero the rest.
  3. Normalize each block to unit L1 -> a positive per-block sparse distribution.
Bind/unbind for this code is block-wise CIRCULAR CONVOLUTION (the ideal GSBC
binding, Frady/Kleyko/Rahimi arXiv:2303.13957); that algebra lives in
hdlab.binding and is not re-implemented here (this module is the ENCODER).

CERTIFIED OPERATING POINT (MEASURED, from the arc; recovered here as the default):
  geometry kb=32, blk_l=128, n_dim=4096; density m=5 (active frac 5/128=0.0391).
  Cross-seed ret_agree10 closed the 0.30 ingest bar at m=5 (5/5 seeds), where the
  coarser m=3 code left the cross-seed min below the bar (0.2568).

INPUT REGIME (load-bearing, honest scope):
  This encoder consumes a DENSE input vector z (e.g. a teacher/sentence embedding)
  and returns the graded sparse HD code. It is a dense-vector -> graded-code
  RE-ENCODER, NOT a self-contained text -> HD encoder like CharTrigramEncoder.
  To encode raw TEXT (KB ingest/query), a text -> dense front-end (the teacher
  the arc distilled from, e.g. backend.llm.bge_encoder + the trained student MLP)
  must be supplied via `teacher`. Absent a teacher, encode(text) fail-louds with
  an actionable message rather than silently returning a meaningless code.

ASCII-only. No emojis. No em dashes.
"""

from __future__ import annotations

import time
from typing import Any, Iterable, Optional

import numpy as np

from . import tracing

# Certified ship geometry + density (MEASURED@ arc; see module docstring).
DEFAULT_N_DIM = 4096
DEFAULT_KB = 32
DEFAULT_BLK_L = 128
DEFAULT_M = 5


def graded_block_code(z: np.ndarray, kb: int, blk_l: int, m: int) -> np.ndarray:
    """Block top-m graded positive survivors, unit-L1 per block. z: [.., kb*blk_l]."""
    if m < 1 or m > blk_l:
        raise ValueError(f"m={m} out of range [1, blk_l={blk_l}]")
    arr = np.asarray(z, dtype=np.float32)
    squeeze = arr.ndim == 1
    if squeeze:
        arr = arr[None, :]
    b = arr.shape[0]
    if arr.shape[1] != kb * blk_l:
        raise ValueError(f"input dim {arr.shape[1]} != kb*blk_l={kb * blk_l}")
    mag = np.abs(arr.reshape(b, kb, blk_l))
    if m >= blk_l:
        surv = mag
    else:
        # top-m magnitudes per block (unordered partition is enough; we keep values)
        idx = np.argpartition(mag, blk_l - m, axis=-1)[..., blk_l - m:]
        surv = np.zeros_like(mag)
        np.put_along_axis(surv, idx, np.take_along_axis(mag, idx, axis=-1), axis=-1)
    l1 = np.maximum(surv.sum(axis=-1, keepdims=True), 1e-8)
    out = (surv / l1).reshape(b, kb * blk_l).astype(np.float32)
    return out[0] if squeeze else out


class GsbcGradedEncoder:
    """Dense-vector -> graded sparse block HD code (top-m survivors, unit-L1/block).

    Composes with hdlab.binding.bind/unbind (block-wise circular conv) + KGStore +
    Codebook the same way CharTrigramEncoder does, but consumes a DENSE embedding
    (encode_dense) rather than raw text. encode(text) requires a text->dense
    `teacher` front-end; without one it raises (fail-loud, no silent bad code).
    """

    def __init__(self, n_dim: int = DEFAULT_N_DIM, kb: int = DEFAULT_KB,
                 blk_l: int = DEFAULT_BLK_L, m: int = DEFAULT_M,
                 teacher: Optional[Any] = None) -> None:
        if kb * blk_l != n_dim:
            raise ValueError(f"kb*blk_l={kb * blk_l} != n_dim={n_dim}")
        self.n_dim = int(n_dim)
        self.kb = int(kb)
        self.blk_l = int(blk_l)
        self.m = int(m)
        self.teacher = teacher

    def encode_dense(self, z: np.ndarray) -> np.ndarray:
        """Encode one dense vector [n_dim] -> graded code [n_dim]."""
        t0 = time.perf_counter_ns()
        out = graded_block_code(z, self.kb, self.blk_l, self.m)
        tracing.emit("gsbc_graded_encoder.encode_dense",
                     {"n_dim": self.n_dim, "m": self.m}, None,
                     elapsed_ns=time.perf_counter_ns() - t0)
        return out

    def encode_dense_batch(self, Z: np.ndarray) -> np.ndarray:
        """Encode dense batch [N, n_dim] -> graded codes [N, n_dim]."""
        return graded_block_code(np.asarray(Z), self.kb, self.blk_l, self.m)

    def _require_teacher(self) -> Any:
        if self.teacher is None:
            raise RuntimeError(
                "GsbcGradedEncoder.encode(text) requires a text->dense teacher "
                "front-end (the distillation teacher, e.g. backend.llm.bge_encoder "
                "+ the trained student). None was supplied. Use encode_dense(z) for "
                "dense inputs, or construct with teacher=<callable/obj exposing "
                "encode(text)->np.ndarray>.")
        return self.teacher

    def encode(self, text: str) -> np.ndarray:
        """Encode raw text -> graded code (REQUIRES a text->dense teacher)."""
        teacher = self._require_teacher()
        z = np.asarray(teacher.encode(text), dtype=np.float32).reshape(-1)
        return self.encode_dense(z)

    def encode_batch(self, texts: Iterable[str]) -> np.ndarray:
        """Encode a list of texts -> [N, n_dim] (REQUIRES a text->dense teacher)."""
        teacher = self._require_teacher()
        texts = list(texts)
        z = np.asarray(teacher.encode_batch(texts), dtype=np.float32)
        return self.encode_dense_batch(z)

    def random_codes(self, n: int, gen: np.random.Generator) -> np.ndarray:
        """Random positive unit-L1 graded codes [n, n_dim] (positive control)."""
        z = gen.standard_normal((n, self.n_dim)).astype(np.float32)
        return self.encode_dense_batch(z)

    def __repr__(self) -> str:
        return (f"GsbcGradedEncoder(n_dim={self.n_dim}, kb={self.kb}, "
                f"blk_l={self.blk_l}, m={self.m}, "
                f"teacher={'set' if self.teacher is not None else 'None'})")
