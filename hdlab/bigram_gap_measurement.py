"""Standardized bigram-gap measurement: substrate_top1 - word_bigram_top1.

Currently every LM cell rebuilds the bigram baseline differently (n1_v3 vs n3
vs hoc1_word_bigram_v1 each had subtly different add-alpha / OOV handling).
Standardize once so cross-cell `bigram_gap` figures are commensurable.

word_bigram_top1 is computed as the empirical-conditional top1:
  for each held bigram (t_prev, t_curr) where t_prev is seen-in-train,
  predict argmax_t' count(t_prev, t') (with optional add-alpha smoothing).
  Top1 = mean(prediction == t_curr) over held bigrams.

When t_prev is NOT seen-in-train, the bigram baseline backs off to the
unigram argmax (most-frequent token). This matches Kneser-Ney back-off
discipline at the simplest level (no discount); cells that need
KN-with-discount should compose this with a smoother downstream.

Inputs are token-id arrays (not strings) so the baseline composes cleanly
with hdlab.token_vocab.TokenVocab.

Bigram-gap convention:
  gap = substrate_top1 - word_bigram_top1
  gap > 0 -> substrate ABOVE bigram (chain-grade lift signal; n1_v3 anchor)
  gap = 0 -> substrate AT bigram
  gap < 0 -> substrate BELOW bigram (substrate fails to recover order info)

Coverage diagnostic:
  coverage = fraction of held bigrams where t_prev was seen-in-train
  (gives the fraction of held positions where the bigram baseline is
  informative rather than back-off; if coverage << 1, bigram_top1 is
  dominated by unigram back-off and the gap measurement is noisy).
"""

from __future__ import annotations

import numpy as np

BASELINE_PROVENANCE: str = "empirical_conditional_add_alpha_unigram_backoff_v1"


def _build_bigram_counts(
    train_ids: np.ndarray, vocab_size: int
) -> tuple[dict[int, dict[int, int]], np.ndarray]:
    """Build sparse bigram counts + unigram counts from train_ids stream.

    Returns:
        bigram_counts: dict t_prev -> dict t_curr -> count
        unigram_counts: np.ndarray shape [vocab_size] of counts
    """
    bigram: dict[int, dict[int, int]] = {}
    unigram = np.zeros(vocab_size, dtype=np.int64)
    train_ids = np.asarray(train_ids, dtype=np.int64).ravel()
    n = train_ids.shape[0]
    if n == 0:
        return bigram, unigram
    for tid in train_ids:
        unigram[int(tid)] += 1
    for i in range(1, n):
        t_prev = int(train_ids[i - 1])
        t_curr = int(train_ids[i])
        d = bigram.get(t_prev)
        if d is None:
            d = {}
            bigram[t_prev] = d
        d[t_curr] = d.get(t_curr, 0) + 1
    return bigram, unigram


def _argmax_bigram(
    t_prev: int,
    bigram_counts: dict[int, dict[int, int]],
    unigram_argmax: int,
) -> int:
    """argmax_t' count(t_prev, t'); back-off to unigram_argmax if t_prev unseen."""
    d = bigram_counts.get(t_prev)
    if not d:
        return unigram_argmax
    best_t = -1
    best_c = -1
    for t, c in d.items():
        if c > best_c:
            best_c = c
            best_t = t
    return best_t if best_t >= 0 else unigram_argmax


def compute_word_bigram_top1(
    train_ids: np.ndarray,
    eval_pairs: tuple[np.ndarray, np.ndarray],
    vocab_size: int,
) -> dict:
    """Compute word-bigram top1 baseline + coverage on `eval_pairs`.

    Args:
        train_ids: [N_train] int array of token ids in stream order.
        eval_pairs: (cues [N_eval], targets [N_eval]) int arrays;
            cues[i] = t_prev token id, targets[i] = t_curr token id.
        vocab_size: V (used for unigram array sizing).

    Returns: dict with keys
        word_bigram_top1: top1 accuracy of bigram-argmax-predictor on eval
        coverage: fraction of eval cues where t_prev was seen-in-train
        n_eval: # eval pairs
        unigram_argmax_id: most-frequent train token id (the back-off pred)
        baseline_provenance: BASELINE_PROVENANCE
    """
    cues, targets = eval_pairs
    cues = np.asarray(cues, dtype=np.int64).ravel()
    targets = np.asarray(targets, dtype=np.int64).ravel()
    n_eval = int(cues.shape[0])
    if n_eval == 0:
        raise ValueError("eval_pairs is empty")
    if cues.shape != targets.shape:
        raise ValueError(
            f"cues and targets shape mismatch: {cues.shape} vs {targets.shape}"
        )

    bigram, unigram = _build_bigram_counts(train_ids, int(vocab_size))
    if unigram.sum() == 0:
        raise ValueError("train_ids has no tokens; cannot compute unigram back-off")
    unigram_argmax = int(np.argmax(unigram))

    correct = 0
    n_covered = 0
    for i in range(n_eval):
        t_prev = int(cues[i])
        t_curr = int(targets[i])
        if t_prev in bigram and bigram[t_prev]:
            n_covered += 1
        pred = _argmax_bigram(t_prev, bigram, unigram_argmax)
        if pred == t_curr:
            correct += 1

    return {
        "word_bigram_top1": float(correct) / float(n_eval),
        "coverage": float(n_covered) / float(n_eval),
        "n_eval": n_eval,
        "unigram_argmax_id": unigram_argmax,
        "baseline_provenance": BASELINE_PROVENANCE,
    }


def compute_bigram_gap(
    substrate_top1: float,
    train_ids: np.ndarray,
    eval_pairs: tuple[np.ndarray, np.ndarray],
    vocab_size: int,
) -> dict:
    """Compute bigram_gap = substrate_top1 - word_bigram_top1 with consistent baseline.

    Args:
        substrate_top1: substrate's top1 accuracy on the SAME eval_pairs
            (cell must compute this upstream; this fn does NOT score the
            substrate, only the bigram baseline).
        train_ids: [N_train] int array of training token-ids in stream order.
        eval_pairs: (cues, targets) int arrays per compute_word_bigram_top1.
        vocab_size: V.

    Returns: dict with keys
        bigram_gap_bits: NOT log-bits; the absolute top1 delta is reported
            in `bigram_gap` (kept for clarity); we expose the field as
            "bigram_gap" (top1 units; per drill 3 research note convention).
        bigram_gap: substrate_top1 - word_bigram_top1 (top1 units; > 0 = lift)
        substrate_top1: passed through
        word_bigram_top1: from compute_word_bigram_top1
        coverage: from compute_word_bigram_top1
        n_eval: # eval pairs
        baseline_provenance: BASELINE_PROVENANCE
    """
    if not (0.0 <= substrate_top1 <= 1.0):
        raise ValueError(
            f"substrate_top1 must be in [0, 1]; got {substrate_top1}"
        )
    baseline = compute_word_bigram_top1(train_ids, eval_pairs, vocab_size)
    gap = float(substrate_top1) - baseline["word_bigram_top1"]
    out = {
        "bigram_gap": gap,
        "bigram_gap_bits": gap,  # alias preserved per research-note field name
        "substrate_top1": float(substrate_top1),
        "word_bigram_top1": baseline["word_bigram_top1"],
        "coverage": baseline["coverage"],
        "n_eval": baseline["n_eval"],
        "unigram_argmax_id": baseline["unigram_argmax_id"],
        "baseline_provenance": baseline["baseline_provenance"],
    }
    return out


def compute_unigram_top1(
    train_ids: np.ndarray,
    eval_targets: np.ndarray,
    vocab_size: int,
) -> dict:
    """Unigram-argmax baseline top1 (predict most-frequent train token always).

    Useful as the lower-bound rung in the discriminating-regime gate per drill
    3 ANCHOR_1 (ARM_A_NULL_UNIGRAM). Returns dict with `unigram_top1` and the
    argmax id used.
    """
    train_ids = np.asarray(train_ids, dtype=np.int64).ravel()
    eval_targets = np.asarray(eval_targets, dtype=np.int64).ravel()
    if train_ids.size == 0:
        raise ValueError("train_ids is empty")
    if eval_targets.size == 0:
        raise ValueError("eval_targets is empty")
    unigram = np.zeros(int(vocab_size), dtype=np.int64)
    for tid in train_ids:
        unigram[int(tid)] += 1
    argmax_id = int(np.argmax(unigram))
    top1 = float(np.mean(eval_targets == argmax_id))
    return {
        "unigram_top1": top1,
        "unigram_argmax_id": argmax_id,
        "n_eval": int(eval_targets.size),
    }
