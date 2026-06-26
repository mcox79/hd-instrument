"""META_M7-compliant LM eval harness: top-K + temperature-calibrated BPC + bigram-gap.

Load-bearing: the 2026-06-23 RIGGED-HARNESS audit (cert ledger row 698) traced
7+ HARD_FAILs on substrate-as-LM to a measurement-methodology confound rather
than substrate failure. The trap was treating cosine-similarity outputs as
log-probabilities and running softmax at T=1.0; cosine logits at T=1.0 are
effectively uniform, BPC explodes, top1 lift goes invisible. This harness fixes
that ONCE for every downstream LM cell:
  - Top-K (1, 5, ...) accuracy is computed directly from the scores' argsort
    (no softmax required; the rigged-harness trap cannot poison top1).
  - BPC is reported at EVERY temperature in `temperature_grid`, plus the
    auto-picked T* that minimizes held BPC (the META_M7-compliant figure).
    BPC_at_T_1p0 is preserved as a reference for the rigged metric so cells
    self-document the trap.
  - Sanity-top1-at-random = 1 / |vocab| is recorded; regime_check_passed asks
    whether substrate top1 > 2 * sanity (per discriminating-regime gate C5).
  - bigram_gap, when a word-bigram top1 baseline is supplied, is just the
    absolute difference; sign matters.

ENCODER_PROVENANCE = SUBSTRATE_NATIVE is a recommendation marker, not enforced
here (this harness is encoder-agnostic by design; cells assert Path C upstream).

Interface contract per drill 3 research note Section 3.1:
  evaluate_lm(scores_fn, eval_data, top_k=[1,5], temperature_grid=None,
              word_bigram_top1=None, vocab_size=None) -> dict

The contract intentionally accepts a `scores_fn` callable (cue -> logits row)
rather than a precomputed [N, V] matrix so cells that cannot materialize the
full matrix (large V_TOK, streaming eval) still get the same eval surface.

Bias-checklist coverage (per [[feedback-experiment-bias-master-checklist]]):
  - BIAS-N: verdict-field-vs-actual-metric -- harness returns the dict; no
    verdict text; cell-author owns classification.
  - BIAS-Q: suspect 1.000 results -- regime_check_passed encodes the
    not-saturated gate; top1 == 1.0 with sanity_top1 == 1.0 / V triggers a
    saturation flag in the return dict.
  - BIAS-S: top1-vs-top5 band-calibration -- both reported.
  - BIAS-M: instrument calibration -- T_grid sweep IS the calibration.
"""

from __future__ import annotations

import math
from typing import Callable, Sequence

import numpy as np

ENCODER_PROVENANCE: str = "SUBSTRATE_NATIVE"

# Default T-grid from drill 3 research note + 2026-06-23 META_HARNESS_RIGGED v2.
DEFAULT_TEMPERATURE_GRID: list[float] = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]


def _softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    """Numerically-stable softmax with temperature T applied row-wise; shape [N, V]."""
    if T <= 0.0:
        raise ValueError(f"temperature must be > 0; got {T}")
    z = logits / T
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def _bpc_from_probs(probs: np.ndarray, targets: np.ndarray) -> float:
    """BPC = -mean(log2 p(target)); shape probs [N, V], targets [N] int."""
    n = len(targets)
    if n == 0:
        return float("inf")
    p_tgt = probs[np.arange(n), targets]
    p_tgt = np.clip(p_tgt, 1e-30, 1.0)
    return -float(np.mean(np.log2(p_tgt)))


def _top_k_accuracy(logits: np.ndarray, targets: np.ndarray, k: int) -> float:
    """Top-k accuracy from raw scores; argpartition O(N V) (no softmax dependency)."""
    n = len(targets)
    if n == 0:
        return float("nan")
    if k <= 0:
        raise ValueError(f"k must be > 0; got {k}")
    v = logits.shape[1]
    k_use = min(k, v)
    if k_use == 1:
        pred = np.argmax(logits, axis=1)
        return float(np.mean(pred == targets))
    # Negate so largest values are smallest (argpartition picks smallest).
    top_idx = np.argpartition(-logits, kth=k_use - 1, axis=1)[:, :k_use]
    rows = np.arange(n)[:, None]
    in_topk = (top_idx == targets[:, None]).any(axis=1)
    return float(np.mean(in_topk))


def evaluate_lm(
    scores_fn: Callable[[int], np.ndarray] | np.ndarray,
    eval_data: Sequence[tuple[int, int]] | tuple[np.ndarray, np.ndarray],
    top_k: Sequence[int] = (1, 5),
    temperature_grid: Sequence[float] | None = None,
    word_bigram_top1: float | None = None,
    vocab_size: int | None = None,
) -> dict:
    """META_M7-compliant LM eval; returns top-K + T-calibrated BPC + bigram_gap.

    Args:
        scores_fn: either
            (a) callable cue_id -> logits np.ndarray shape [V] (substrate
                scoring fn; harness materializes [N, V] internally), OR
            (b) precomputed logits np.ndarray shape [N, V] (cell already
                ran scoring).
        eval_data: either
            (a) sequence of (cue_id, target_id) pairs, OR
            (b) (cues_array shape [N], targets_array shape [N]).
        top_k: iterable of K values to compute top-K accuracy for.
        temperature_grid: T values for BPC calibration. None = DEFAULT.
        word_bigram_top1: optional baseline for bigram_gap. None = skip gap.
        vocab_size: V. Required if scores_fn is callable (cannot infer).

    Returns: dict with at minimum (always present):
        top1, top5 (and any other top_k requested as top<k>)
        BPC_at_T_optimal, T_optimal, BPC_at_T_1p0
        BPC_grid: dict {str(T) -> BPC}
        sanity_top1_at_random
        regime_check_passed (top1 > 2 * sanity_top1)
        saturation_flag (top1 == 1.0 and sanity != 1.0)
        n_eval
        vocab_size
        encoder_provenance
    If word_bigram_top1 supplied:
        bigram_gap (substrate_top1 - word_bigram_top1; sign matters)
        word_bigram_top1
    """
    # Normalize eval_data
    if isinstance(eval_data, tuple) and len(eval_data) == 2 and isinstance(
        eval_data[0], np.ndarray
    ):
        cues = np.asarray(eval_data[0], dtype=np.int64)
        targets = np.asarray(eval_data[1], dtype=np.int64)
    else:
        pairs = list(eval_data)
        if not pairs:
            raise ValueError("eval_data is empty")
        cues = np.asarray([p[0] for p in pairs], dtype=np.int64)
        targets = np.asarray([p[1] for p in pairs], dtype=np.int64)
    if cues.shape != targets.shape:
        raise ValueError(
            f"cues and targets must have equal shape; "
            f"got cues={cues.shape}, targets={targets.shape}"
        )
    n_eval = int(cues.shape[0])
    if n_eval == 0:
        raise ValueError("eval_data has zero pairs")

    # Materialize / use logits
    if callable(scores_fn):
        if vocab_size is None:
            raise ValueError(
                "vocab_size required when scores_fn is a callable; "
                "cannot infer matrix width."
            )
        v = int(vocab_size)
        logits = np.zeros((n_eval, v), dtype=np.float32)
        for i, cue in enumerate(cues):
            row = np.asarray(scores_fn(int(cue)), dtype=np.float32)
            if row.shape != (v,):
                raise ValueError(
                    f"scores_fn({int(cue)}) returned shape {row.shape}; "
                    f"expected ({v},)"
                )
            logits[i] = row
    else:
        logits = np.asarray(scores_fn, dtype=np.float32)
        if logits.ndim != 2 or logits.shape[0] != n_eval:
            raise ValueError(
                f"precomputed logits shape {logits.shape} mismatches "
                f"n_eval={n_eval} (expected [N, V])"
            )
        v = int(logits.shape[1])
        if vocab_size is not None and vocab_size != v:
            raise ValueError(
                f"vocab_size={vocab_size} mismatches logits width {v}"
            )

    # Targets in range?
    if (targets < 0).any() or (targets >= v).any():
        raise ValueError(
            f"targets out of [0, V={v}); "
            f"min={int(targets.min())}, max={int(targets.max())}"
        )

    # Top-K accuracies (independent of softmax temperature)
    out: dict = {}
    for k in top_k:
        out[f"top{int(k)}"] = _top_k_accuracy(logits, targets, int(k))
    top1 = out["top1"]

    # Temperature grid BPC
    t_grid = list(temperature_grid) if temperature_grid is not None else list(
        DEFAULT_TEMPERATURE_GRID
    )
    if 1.0 not in t_grid:
        t_grid = t_grid + [1.0]
    bpc_grid: dict[str, float] = {}
    best_T = t_grid[0]
    best_bpc = float("inf")
    for T in t_grid:
        probs = _softmax_with_T(logits, float(T))
        bpc = _bpc_from_probs(probs, targets)
        bpc_grid[f"{float(T):.4g}"] = bpc
        if bpc < best_bpc:
            best_bpc = bpc
            best_T = float(T)
    bpc_at_T_1p0 = bpc_grid["1"] if "1" in bpc_grid else bpc_grid[
        f"{1.0:.4g}"
    ]

    # Sanity / regime
    sanity_top1 = 1.0 / float(v)
    regime_check_passed = bool(top1 > 2.0 * sanity_top1)
    # Saturation flag: top1 == 1.0 AND not just because vocab is trivial.
    saturation_flag = bool(
        top1 >= 0.99999 and (v > 1) and (sanity_top1 < 0.5)
    )

    out.update(
        {
            "BPC_at_T_optimal": float(best_bpc),
            "T_optimal": float(best_T),
            "BPC_at_T_1p0": float(bpc_at_T_1p0),
            "BPC_grid": bpc_grid,
            "sanity_top1_at_random": float(sanity_top1),
            "regime_check_passed": regime_check_passed,
            "saturation_flag": saturation_flag,
            "n_eval": n_eval,
            "vocab_size": v,
            "encoder_provenance": ENCODER_PROVENANCE,
        }
    )
    if word_bigram_top1 is not None:
        out["word_bigram_top1"] = float(word_bigram_top1)
        out["bigram_gap"] = float(top1) - float(word_bigram_top1)

    return out


def compute_uniform_baseline_bpc(vocab_size: int) -> float:
    """BPC of uniform distribution over V tokens = log2(V); reference floor."""
    if vocab_size <= 0:
        raise ValueError(f"vocab_size must be > 0; got {vocab_size}")
    return math.log2(float(vocab_size))
