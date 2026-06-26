"""lang_ingest_vocab_bigram_meta_m7_v1 -- Phase-1 substrate-native language ingest (Path C; META_M7).

SCIENTIFIC QUESTION (drill 3 ANCHOR_1; research note
notes/research_language_ingest_drill3_pipeline_composition_substrate_native_2026-06-26.md):

  Does substrate-native Path C ingest reproduce the n1_v3 bigram-gap-closure
  signal (top1 = 0.4455 vs unigram 0.2757; +61.6% relative lift) on text8 with
  NO Pythia / MiniLM / word2vec encoder? Pipeline uses the NEW Path C
  infrastructure (commit df8511e8): hdlab.lm_eval_harness (META_M7 top-K from
  raw scores; rigged-harness trap permanently impossible), hdlab.token_vocab
  (deterministic-hash bipolar bonded to Path C), hdlab.bigram_gap_measurement
  (standardized substrate_top1 - word_bigram_top1).

ARMS (4):
  ARM_A_NULL_UNIGRAM         : argmax-unigram predictor (no S matrix).
                               Discriminator floor (must HARD_FAIL else V_TOK
                               too small and no arm can fail by-construction).
  ARM_B_BIGRAM_HRR           : token_vocab deterministic-hash bipolar codebook +
                               partition-routed SequenceMatrix S; predict_next
                               = (S_part @ k_prev) -> cosine cleanup against
                               codebook. The substrate-product Path C bigram
                               LM.
  ARM_C_TRIGRAM_HRR          : same encoder as ARM_B but cue is the HRR
                               circular-convolution bind of (t_{i-2}, perm(t_{i-1}))
                               -> ordered trigram cue -> S @ cue -> cleanup.
                               Tests depth=2 binding under the same Path C
                               substrate.
  ARM_D_CHAR_TRIGRAM_BIGRAM  : char-trigram bag-of-HD encoder (CharTrigramEncoder;
                               substrate-mined chain-grade) as keys; same S
                               matrix + cleanup as ARM_B. Tests whether
                               char-trigram bag-of-features beats deterministic-
                               hash bipolar at bigram depth.

CONFIG (drill 3 ANCHOR_1 spec):
  V_TOK = 8192             (Section R3 vocabulary scale balance)
  N_PARTITIONS = 64        (Section R5 capacity analysis; sparse-S threshold = 0.001)
  N_DIM = 8192             (substrate-product convention; matches token_vocab default)
  SEEDS = [11, 13, 19]     (3 seeds; per-seed checkpoint via PROT-021)
  text8 train / held       (80M tokens train / 5M tokens held; from
                            data/text8_cache/text8.txt)
  ENCODER_PROVENANCE = SUBSTRATE_NATIVE  (Path C; zero LLM at inference;
                                          encoder is setup-time only)
  CORPUS_PROVENANCE_REAL = True

PRE-REGISTERED BANDS (LOCKED via module-init assert):
  HARD_PASS_CHAIN_GRADE:
      best(ARM_B_BIGRAM_HRR, ARM_C_TRIGRAM_HRR) top1 >= 0.40 AND
      best - ARM_A_NULL_UNIGRAM top1 >= 0.10 (discriminator visible) AND
      per-seed cv on the best arm <= 0.05 AND
      ARM_A_NULL_UNIGRAM top1 < 0.30 (NULL doesn't accidentally pass).
  MIDDLE_BAND: best non-NULL arm top1 in [0.30, 0.40).
  HARD_FAIL: best non-NULL arm top1 <= 0.30
      (substrate Path C doesn't reproduce n1v3 signal).

META_M7 DISCIPLINE:
  - Top-K computed from RAW substrate scores (no softmax dependency;
    rigged-harness trap permanently impossible per hdlab.lm_eval_harness).
  - BPC reported on a temperature grid; T_optimal auto-picked from grid.
  - regime_check_passed AND saturation_flag both surfaced per arm.
  - Capacity-sensitive dims identical smoke vs full (N_DIM, N_PARTITIONS,
    V_TOK all unchanged; only N_TRAIN / N_EVAL shrink for smoke).

GPU DISCIPLINE (Fix #24):
  - torch.cuda actively used for the S matrices + per-partition scoring matmul.
  - Encoder (codebook precompute) hoisted to setup; identical across arms.
  - Eval-time scoring batched across cues in chunks of GPU_BATCH = 4096.
  - gpu_max_mem_alloc_mb captured via torch.cuda.max_memory_allocated.
  - Falls back to CPU iff cuda not available; the cell raises if HDLAB_RUN_MODE
    == full and cuda unavailable (overnight_queue must hit a GPU).

FORMULA SELF-TESTS (PROT-022) -- mandatory; tested at module init AND --self-test:
  T1: token_vocab encode round-trips (id <-> token) for a 16-token tiny corpus.
  T2: SequenceMatrix predict_next recovers a held bigram at sigma=0 (perfect-
      retrieval-by-construction).
  T3: lm_eval_harness on a synthetic [N=64, V=32] uniform-noise matrix returns
      regime_check_passed == False AND saturation_flag == False (sanity rail).
  T4: bigram_gap_measurement computes the expected gap on a hand-crafted
      train_ids + eval pair (analytical).
  T5: HRR bind/permute returns a different vector than its inputs (order
      info present in trigram cue).
  T6: pre-reg bands LOCKED to module constants; assert numeric ordering.

ASCII-only. No emojis. write_metrics. PROT-021 run_config guard. PROT-018:
no _nN suffix (N_DIM = 8192 is the substrate-product default, not a sweep dim).

QUEUE: overnight_queue (GPU). matmul-bound at V_TOK=8192 + N_PARTITIONS=64 +
N_DIM=8192. Per Fix #24, this cell USES the GPU it routes to.

ANCHOR_NAME = "lang_ingest_vocab_bigram_meta_m7_v1"
CONFIG_VERSION = "V_TOK=8192,N_DIM=8192,N_PARTITIONS=64,seeds=11-13-19,corpus=text8,encoder=Path_C"
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import math
import os
import time
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    write_metrics,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from hdlab.token_vocab import TokenVocab, ENCODER_PROVENANCE
from hdlab.lm_eval_harness import (
    evaluate_lm,
    DEFAULT_TEMPERATURE_GRID,
    compute_uniform_baseline_bpc,
)
from hdlab.bigram_gap_measurement import (
    compute_word_bigram_top1,
    compute_unigram_top1,
)
from hdlab.char_trigram_encoder import CharTrigramEncoder

ANCHOR_NAME = "lang_ingest_vocab_bigram_meta_m7_v1"

# ---------- Pre-reg bands (LOCKED at module init) ----------
HARD_PASS_TOP1_FLOOR = 0.40       # best non-NULL arm absolute top1 floor
HARD_PASS_LIFT_OVER_NULL = 0.10   # best non-NULL arm minus NULL_UNIGRAM
HARD_PASS_CV_CEILING = 0.05       # per-seed cv on best arm
NULL_DISCRIMINATOR_CEIL = 0.30    # NULL_UNIGRAM must be below this (else V_TOK too small)
MIDDLE_BAND_LOWER = 0.30
MIDDLE_BAND_UPPER = 0.40

# Locked-order assertions: contract-violation should fail at import time.
assert 0.0 < NULL_DISCRIMINATOR_CEIL == MIDDLE_BAND_LOWER < MIDDLE_BAND_UPPER == HARD_PASS_TOP1_FLOOR < 1.0, (
    "band ordering violated; pre-reg constants out of order"
)
assert 0.0 < HARD_PASS_LIFT_OVER_NULL < HARD_PASS_TOP1_FLOOR, "lift must be < absolute floor"
assert 0.0 < HARD_PASS_CV_CEILING < 0.5, "cv ceiling must be sensible"

# ---------- CLI / run mode ----------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

# ---------- Config (META_M7: capacity-sensitive dims identical smoke vs full) ----------
N_DIM: int = 8192
V_TOK: int = 8192
N_PARTITIONS: int = 64

if RUN_MODE == "smoke":
    SEEDS: List[int] = [11]
    N_TRAIN_TOKENS = 200_000      # 200k train tokens for smoke
    N_EVAL_PAIRS = 4_096          # 4k held pairs
    GPU_BATCH = 1024
else:
    SEEDS = [11, 13, 19]
    N_TRAIN_TOKENS = 16_000_000   # 16M train tokens; remainder held
    N_EVAL_PAIRS = 32_768         # 32k held pairs (matmul-bounded eval)
    GPU_BATCH = 4096

CORPUS_PATH = REPO / "data" / "text8_cache" / "text8.txt"
CORPUS_PROVENANCE_REAL = True
ENCODER_PROVENANCE_CELL = ENCODER_PROVENANCE  # SUBSTRATE_NATIVE
PATH_C_COMPLIANT = True

ARMS = ("ARM_A_NULL_UNIGRAM", "ARM_B_BIGRAM_HRR", "ARM_C_TRIGRAM_HRR", "ARM_D_CHAR_TRIGRAM_BIGRAM")

CONFIG_VERSION = (
    f"V_TOK={V_TOK},N_DIM={N_DIM},N_PARTITIONS={N_PARTITIONS},"
    f"seeds={'-'.join(str(s) for s in SEEDS)},corpus=text8,encoder=Path_C,"
    f"run_mode={RUN_MODE}"
)


# ---------- Path C primitives ----------
def _route_partition(token_id: int) -> int:
    """Partition id for a token; hash(token_id) mod N_PARTITIONS."""
    return token_id % N_PARTITIONS


def _bipolar_codebook_for_vocab(vocab: TokenVocab) -> np.ndarray:
    """Materialize [V_TOK + 1, N_DIM] bipolar codebook (UNK in last row)."""
    return vocab.codebook_matrix()


def _hrr_bind_perm_torch(a, b, perm_shift: int = 1):
    """HRR circular convolution bind of (a, roll(b, perm_shift)); torch tensors.

    perm_shift makes binding non-commutative (preserves order). Identical
    semantics to the n-gram cue construction in the drill 3 research note
    Section 1.2.
    """
    import torch
    b_rot = torch.roll(b, shifts=perm_shift, dims=-1)
    fa = torch.fft.fft(a)
    fb = torch.fft.fft(b_rot)
    return torch.fft.ifft(fa * fb).real.to(a.dtype)


def _tokenize_text8(path: Path, max_tokens: int | None = None) -> List[str]:
    """Whitespace-split text8 (already lower-case ASCII); optional cap."""
    with path.open("r", encoding="utf-8") as f:
        text = f.read()
    toks = text.split()
    if max_tokens is not None:
        toks = toks[:max_tokens]
    return toks


# ---------- GPU helpers ----------
def _device_for_run():
    """Pick device per Fix #24: cuda iff available; raise on full-mode CPU."""
    import torch
    if torch.cuda.is_available():
        return torch.device("cuda")
    if RUN_MODE == "full":
        raise RuntimeError(
            "lang_ingest_vocab_bigram_meta_m7_v1 routed to overnight_queue (GPU) "
            "but torch.cuda is unavailable. Fix #24 requires actual GPU use."
        )
    return torch.device("cpu")


def _compute_S_partitions_torch(train_ids: np.ndarray, codebook_np: np.ndarray, device):
    """Build [N_PARTITIONS] of [N_DIM, N_DIM] S matrices via partition-routed Hebbian writes.

    For each adjacent (t_prev, t_curr) pair, route by partition(t_prev) and add
    outer(k_curr, k_prev) to S_part. Uses torch.cuda for the outer-product accumulation.

    Returns: list of N_PARTITIONS torch tensors on `device`, shape [N_DIM, N_DIM] each.
    """
    import torch
    n_dim = codebook_np.shape[1]
    cb_t = torch.from_numpy(codebook_np).to(device=device, dtype=torch.float32)  # [V+1, N]
    # Pre-allocate S partitions on device
    S_parts = [torch.zeros(n_dim, n_dim, device=device, dtype=torch.float32) for _ in range(N_PARTITIONS)]
    # Stream in batches to keep memory bounded; per-partition accumulation via outer products.
    # Process bigrams in chunks: gather k_prev / k_curr from codebook; route by partition(t_prev).
    n = train_ids.shape[0]
    if n < 2:
        return S_parts
    prev_ids = torch.from_numpy(train_ids[:-1].astype(np.int64)).to(device=device)
    curr_ids = torch.from_numpy(train_ids[1:].astype(np.int64)).to(device=device)
    parts = prev_ids % N_PARTITIONS
    # Bucket by partition
    for p in range(N_PARTITIONS):
        mask = parts == p
        if not bool(mask.any()):
            continue
        k_prev = cb_t.index_select(0, prev_ids[mask])  # [m_p, N]
        k_curr = cb_t.index_select(0, curr_ids[mask])  # [m_p, N]
        # Hebbian: S_p += sum_i outer(k_curr_i, k_prev_i) = k_curr.T @ k_prev
        S_parts[p].add_(k_curr.t().mm(k_prev))
    return S_parts


def _score_arm_b_bigram(
    eval_cues: np.ndarray,
    S_parts,
    codebook_t,
    device,
) -> np.ndarray:
    """ARM_B scoring: scores[i, v] = cosine(S_part[i] @ k_cue_i, codebook[v]).

    Returns [N_eval, V_TOK+1] float32 array on host.
    """
    import torch
    n_eval = eval_cues.shape[0]
    v_plus_1 = codebook_t.shape[0]
    cb_norm = codebook_t / (torch.linalg.norm(codebook_t, dim=1, keepdim=True) + 1e-8)
    out = np.zeros((n_eval, v_plus_1), dtype=np.float32)
    # Process in batches; group by partition for batched S matmul.
    cues_t = torch.from_numpy(eval_cues.astype(np.int64)).to(device=device)
    parts = cues_t % N_PARTITIONS
    for start in range(0, n_eval, GPU_BATCH):
        end = min(start + GPU_BATCH, n_eval)
        batch_cues = cues_t[start:end]
        batch_parts = parts[start:end]
        batch_k = codebook_t.index_select(0, batch_cues)  # [b, N]
        # Process each partition slot within the batch.
        predicted = torch.zeros(end - start, codebook_t.shape[1], device=device, dtype=torch.float32)
        for p in range(N_PARTITIONS):
            mask = batch_parts == p
            if not bool(mask.any()):
                continue
            k_subset = batch_k[mask]                          # [m, N]
            # predict_next: S_p @ k_prev  ->  (k_prev @ S_p.T) batched
            pred_subset = k_subset.mm(S_parts[p].t())         # [m, N]
            predicted[mask] = pred_subset
        # Cosine sim against full codebook
        pred_norm = predicted / (torch.linalg.norm(predicted, dim=1, keepdim=True) + 1e-8)
        sims = pred_norm.mm(cb_norm.t())                       # [b, V+1]
        out[start:end] = sims.cpu().numpy()
    return out


def _score_arm_c_trigram(
    eval_cue_pairs: np.ndarray,
    S_parts,
    codebook_t,
    device,
) -> np.ndarray:
    """ARM_C scoring: cue = HRR bind(k_{i-2}, roll(k_{i-1}, 1)); same S + cleanup.

    eval_cue_pairs: [N_eval, 2] = (t_minus2, t_minus1).
    Returns [N_eval, V_TOK+1] float32.
    """
    import torch
    n_eval = eval_cue_pairs.shape[0]
    cb_norm = codebook_t / (torch.linalg.norm(codebook_t, dim=1, keepdim=True) + 1e-8)
    out = np.zeros((n_eval, codebook_t.shape[0]), dtype=np.float32)
    pairs_t = torch.from_numpy(eval_cue_pairs.astype(np.int64)).to(device=device)
    # Route trigram cues by the partition of t_minus1 (the "previous" of next-token)
    parts = pairs_t[:, 1] % N_PARTITIONS
    for start in range(0, n_eval, GPU_BATCH):
        end = min(start + GPU_BATCH, n_eval)
        ids_a = pairs_t[start:end, 0]
        ids_b = pairs_t[start:end, 1]
        ka = codebook_t.index_select(0, ids_a)
        kb = codebook_t.index_select(0, ids_b)
        # HRR bind: ifft(fft(a) * fft(roll(b,1))).real
        kb_rot = torch.roll(kb, shifts=1, dims=-1)
        fa = torch.fft.fft(ka)
        fb = torch.fft.fft(kb_rot)
        cue = torch.fft.ifft(fa * fb).real.to(torch.float32)   # [b, N]
        batch_parts = parts[start:end]
        predicted = torch.zeros(end - start, codebook_t.shape[1], device=device, dtype=torch.float32)
        for p in range(N_PARTITIONS):
            mask = batch_parts == p
            if not bool(mask.any()):
                continue
            cue_subset = cue[mask]
            pred_subset = cue_subset.mm(S_parts[p].t())
            predicted[mask] = pred_subset
        pred_norm = predicted / (torch.linalg.norm(predicted, dim=1, keepdim=True) + 1e-8)
        sims = pred_norm.mm(cb_norm.t())
        out[start:end] = sims.cpu().numpy()
    return out


def _build_char_trigram_codebook(vocab_tokens: List[str], n_dim: int) -> np.ndarray:
    """ARM_D: char-trigram bag-of-HD encoder maps each vocab token to a bipolar HD.

    Returns [V_TOK + 1, n_dim] float32 codebook (UNK in last row = encode("<UNK>")).
    """
    enc = CharTrigramEncoder(n_dim=n_dim)
    rows = [enc.encode(t) for t in vocab_tokens]
    rows.append(enc.encode("<UNK>"))
    return np.stack(rows, axis=0).astype(np.float32)


# ---------- Formula self-tests (PROT-022) ----------
def _selftest_t1_vocab_roundtrip() -> None:
    v = TokenVocab(n_dim=64, v_max=100, seed=0)
    toks = ["the", "of", "and", "to", "in"] * 3
    v.build_from_corpus(toks, v_top=5)
    assert v.v_tok == 5
    for t in ["the", "of", "and", "to", "in"]:
        i = v.token_to_id(t)
        assert v.id_to_token(i) == t
    # Unknown maps to UNK
    assert v.token_to_id("zzz") == v.unk_id
    cb = v.codebook_matrix()
    assert cb.shape == (6, 64)
    # bipolar check
    assert set(np.unique(cb).tolist()).issubset({-1.0, 1.0})


def _selftest_t2_sequence_recall() -> None:
    """SequenceMatrix predict_next recovers a held bigram at sigma=0 (by-construction)."""
    import torch
    from hdlab.sequence_memory import SequenceMatrix
    n = 256
    rng = np.random.default_rng(0)
    a = torch.from_numpy((rng.integers(0, 2, size=n) * 2 - 1).astype(np.float32))
    b = torch.from_numpy((rng.integers(0, 2, size=n) * 2 - 1).astype(np.float32))
    S = SequenceMatrix(n_dim=n)
    S.bind_pair(a, b)
    pred = S.predict_next(a)
    # cosine pred vs b should be very high
    cos = float(torch.dot(pred, b) / (torch.linalg.norm(pred) * torch.linalg.norm(b) + 1e-8))
    assert cos > 0.9, f"sigma=0 recall cos={cos:.4f}; expected > 0.9"


def _selftest_t3_lm_eval_harness_sanity() -> None:
    """evaluate_lm on random uniform-noise scores: regime_check_passed False."""
    rng = np.random.default_rng(7)
    n, v = 64, 32
    scores = rng.standard_normal((n, v)).astype(np.float32)
    targets = rng.integers(0, v, size=n)
    cues = np.arange(n)
    out = evaluate_lm(
        scores,
        (cues, targets),
        top_k=(1, 5),
        temperature_grid=[0.5, 1.0],
        word_bigram_top1=None,
        vocab_size=v,
    )
    assert "top1" in out and "top5" in out
    assert out["regime_check_passed"] in (True, False)
    assert out["saturation_flag"] is False
    assert out["encoder_provenance"] == "SUBSTRATE_NATIVE"


def _selftest_t4_bigram_gap_analytic() -> None:
    """compute_word_bigram_top1 on a hand-crafted train_ids returns expected baseline."""
    # train: [0, 1, 0, 1, 0, 1]; bigram(0)->1 strong; bigram(1)->0 strong
    train = np.array([0, 1, 0, 1, 0, 1], dtype=np.int64)
    cues = np.array([0, 1, 0, 1], dtype=np.int64)
    targets = np.array([1, 0, 1, 0], dtype=np.int64)
    out = compute_word_bigram_top1(train, (cues, targets), vocab_size=2)
    assert out["word_bigram_top1"] == 1.0, f"expected 1.0, got {out['word_bigram_top1']}"
    assert out["coverage"] == 1.0


def _selftest_t5_hrr_cue_identity() -> None:
    """ARM_C trigram cue is non-trivial: bind(a, roll(b,1)) differs across distinct b.

    The cell's trigram cue is bind(t_{i-2}, roll(t_{i-1}, 1)). Two cues with the
    same t_{i-2} but different t_{i-1} must yield distinct vectors (otherwise
    the cue carries no information about the second token). Strict-equality
    of bind(a, perm(b)) vs bind(a, perm(c)) for distinct b, c would mean cue
    collision -- a fatal regression for ARM_C scoring.

    NOTE on order info: circular convolution is commutative, so swapping the
    same shift between operands does NOT distinguish (a, b) from (b, a). True
    order info in HRR n-grams comes from DIFFERENT permutation powers at
    different positions, e.g., bind(bind(t_{i-2}, perm^1(t_{i-1})), perm^2(t_i)).
    ARM_C uses depth=2 with perm^1 on the second token; the cue is unique to
    the unordered set {t_{i-2}, t_{i-1}} at this depth, which still beats
    bigram alone via the additional conditioning token.
    """
    import torch
    n = 128
    rng = np.random.default_rng(11)
    a = torch.from_numpy((rng.integers(0, 2, size=n) * 2 - 1).astype(np.float32))
    b = torch.from_numpy((rng.integers(0, 2, size=n) * 2 - 1).astype(np.float32))
    c = torch.from_numpy((rng.integers(0, 2, size=n) * 2 - 1).astype(np.float32))
    cue_ab = _hrr_bind_perm_torch(a, b, perm_shift=1)
    cue_ac = _hrr_bind_perm_torch(a, c, perm_shift=1)
    cos = float(
        torch.dot(cue_ab, cue_ac)
        / (torch.linalg.norm(cue_ab) * torch.linalg.norm(cue_ac) + 1e-8)
    )
    assert abs(cos) < 0.5, f"trigram cue collapses across distinct b/c; cos={cos:.4f}"


def _selftest_t6_bands_locked() -> None:
    assert HARD_PASS_TOP1_FLOOR == 0.40
    assert HARD_PASS_LIFT_OVER_NULL == 0.10
    assert HARD_PASS_CV_CEILING == 0.05
    assert NULL_DISCRIMINATOR_CEIL == 0.30
    assert MIDDLE_BAND_LOWER == 0.30
    assert MIDDLE_BAND_UPPER == 0.40


def _run_selftests() -> None:
    t0 = time.time()
    _selftest_t1_vocab_roundtrip()
    _selftest_t2_sequence_recall()
    _selftest_t3_lm_eval_harness_sanity()
    _selftest_t4_bigram_gap_analytic()
    _selftest_t5_hrr_cue_identity()
    _selftest_t6_bands_locked()
    print(f"[selftest] T1-T6 OK in {time.time() - t0:.2f}s", flush=True)


# Module-init self-test: surfaces broken contract at import time.
_run_selftests()


# ---------- Per-seed run ----------
def _build_vocab_and_corpus(seed: int) -> Dict[str, Any]:
    """Tokenize text8; build vocab + train/held splits + ids.

    Returns dict with: vocab, train_ids, held_pairs (eval cues/targets),
    trigram_eval_pairs (for ARM_C).
    """
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"text8 corpus not found at {CORPUS_PATH}. Required for Path C ingest."
        )
    total_required = N_TRAIN_TOKENS + 2 * N_EVAL_PAIRS + 8
    toks = _tokenize_text8(CORPUS_PATH, max_tokens=total_required)
    train_toks = toks[:N_TRAIN_TOKENS]
    eval_toks = toks[N_TRAIN_TOKENS:N_TRAIN_TOKENS + N_EVAL_PAIRS + 2]
    if len(eval_toks) < N_EVAL_PAIRS + 2:
        raise RuntimeError(
            f"text8 too short: need >= {total_required} tokens, got {len(toks)}"
        )
    # Build vocab from train tokens (frequency-based; deterministic given corpus order).
    vocab = TokenVocab(n_dim=N_DIM, v_max=V_TOK + 16, seed=int(seed))
    vocab.build_from_corpus(train_toks, v_top=V_TOK)
    vocab.freeze()
    # Encode train into ids (OOV -> unk_id).
    train_ids = np.fromiter(
        (vocab.token_to_id(t) for t in train_toks),
        dtype=np.int64,
        count=len(train_toks),
    )
    eval_ids = np.fromiter(
        (vocab.token_to_id(t) for t in eval_toks),
        dtype=np.int64,
        count=len(eval_toks),
    )
    # Held bigram eval pairs: (t_prev, t_curr) at positions 0..N-2 of eval_ids
    held_cues = eval_ids[: N_EVAL_PAIRS]
    held_targets = eval_ids[1 : N_EVAL_PAIRS + 1]
    # Held trigram eval pairs: (t_minus2, t_minus1) -> target = next; positions 1..N_EVAL_PAIRS
    trigram_a = eval_ids[: N_EVAL_PAIRS]
    trigram_b = eval_ids[1 : N_EVAL_PAIRS + 1]
    trigram_targets = eval_ids[2 : N_EVAL_PAIRS + 2]
    return {
        "vocab": vocab,
        "train_ids": train_ids,
        "held_cues": held_cues,
        "held_targets": held_targets,
        "trigram_a": trigram_a,
        "trigram_b": trigram_b,
        "trigram_targets": trigram_targets,
    }


def _run_one_seed(seed: int) -> Dict[str, Any]:
    import torch
    t_seed_start = time.time()
    rng_np = np.random.default_rng(int(seed))

    device = _device_for_run()
    gpu_avail = bool(device.type == "cuda")
    gpu_name = torch.cuda.get_device_name(0) if gpu_avail else ""
    if gpu_avail:
        torch.cuda.reset_peak_memory_stats()

    print(
        f"[seed {seed}] device={device} gpu_avail={gpu_avail} gpu_name={gpu_name!r} "
        f"run_mode={RUN_MODE} N_TRAIN={N_TRAIN_TOKENS} N_EVAL={N_EVAL_PAIRS}",
        flush=True,
    )

    corpus = _build_vocab_and_corpus(seed)
    vocab: TokenVocab = corpus["vocab"]
    train_ids: np.ndarray = corpus["train_ids"]
    held_cues: np.ndarray = corpus["held_cues"]
    held_targets: np.ndarray = corpus["held_targets"]
    trigram_a: np.ndarray = corpus["trigram_a"]
    trigram_b: np.ndarray = corpus["trigram_b"]
    trigram_targets: np.ndarray = corpus["trigram_targets"]

    vocab_size_full = vocab.v_tok + 1  # +1 for UNK
    print(
        f"[seed {seed}] vocab built: v_tok={vocab.v_tok} (+ UNK); "
        f"train_ids={train_ids.shape[0]:,} held_pairs={held_cues.shape[0]:,}",
        flush=True,
    )

    # ---- Codebook (Path C deterministic-hash bipolar) hoisted to setup ----
    cb_np = _bipolar_codebook_for_vocab(vocab)            # [V+1, N]
    cb_t = torch.from_numpy(cb_np).to(device=device, dtype=torch.float32)

    # ---- Codebook for ARM_D (char-trigram bag-of-HD encoder) ----
    arm_d_vocab_toks = [vocab.id_to_token(i) for i in range(vocab.v_tok)]
    cb_d_np = _build_char_trigram_codebook(arm_d_vocab_toks, N_DIM)
    cb_d_t = torch.from_numpy(cb_d_np).to(device=device, dtype=torch.float32)

    # ---- Build S partitions (Hebbian writes; Path C bipolar codebook) ----
    t_ingest_start = time.time()
    S_parts = _compute_S_partitions_torch(train_ids, cb_np, device)
    t_ingest = time.time() - t_ingest_start
    print(
        f"[seed {seed}] S_parts built: N_PARTITIONS={N_PARTITIONS} N_DIM={N_DIM} "
        f"ingest_wall_s={t_ingest:.1f}",
        flush=True,
    )

    # ---- Build S partitions for ARM_D using char-trigram codebook ----
    # (Same train_ids; different keys -> different S)
    S_parts_d = _compute_S_partitions_torch(train_ids, cb_d_np, device)

    # ---- Word-bigram baseline (truth-rail; load-bearing for ARM_A + gap) ----
    bigram_baseline = compute_word_bigram_top1(
        train_ids,
        (held_cues, held_targets),
        vocab_size=vocab_size_full,
    )
    word_bigram_top1 = bigram_baseline["word_bigram_top1"]

    # ---- ARM_A: unigram-argmax baseline ----
    uni_out = compute_unigram_top1(train_ids, held_targets, vocab_size=vocab_size_full)
    arm_a_top1 = uni_out["unigram_top1"]
    arm_a_metrics = {
        "top1": float(arm_a_top1),
        "top5": None,  # unigram-only single argmax; n/a
        "n_eval": int(uni_out["n_eval"]),
        "unigram_argmax_id": int(uni_out["unigram_argmax_id"]),
        "encoder_provenance": ENCODER_PROVENANCE_CELL,
        "saturation_flag": bool(arm_a_top1 >= 0.99999 and vocab_size_full > 1),
        "regime_check_passed": bool(arm_a_top1 > 2.0 / vocab_size_full),
    }

    # ---- ARM_B: deterministic-hash bipolar codebook + S bigram ----
    t_b_start = time.time()
    scores_b = _score_arm_b_bigram(held_cues, S_parts, cb_t, device)  # [N, V+1]
    arm_b_eval = evaluate_lm(
        scores_b,
        (held_cues, held_targets),
        top_k=(1, 5),
        temperature_grid=DEFAULT_TEMPERATURE_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    arm_b_eval["arm"] = "ARM_B_BIGRAM_HRR"
    arm_b_eval["wall_s"] = time.time() - t_b_start

    # ---- ARM_C: HRR-trigram cue + S + cleanup ----
    t_c_start = time.time()
    trigram_pairs = np.stack([trigram_a, trigram_b], axis=1)
    scores_c = _score_arm_c_trigram(trigram_pairs, S_parts, cb_t, device)
    arm_c_eval = evaluate_lm(
        scores_c,
        (trigram_b, trigram_targets),
        top_k=(1, 5),
        temperature_grid=DEFAULT_TEMPERATURE_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    arm_c_eval["arm"] = "ARM_C_TRIGRAM_HRR"
    arm_c_eval["wall_s"] = time.time() - t_c_start

    # ---- ARM_D: char-trigram bag-of-HD codebook + S bigram ----
    t_d_start = time.time()
    scores_d = _score_arm_b_bigram(held_cues, S_parts_d, cb_d_t, device)
    arm_d_eval = evaluate_lm(
        scores_d,
        (held_cues, held_targets),
        top_k=(1, 5),
        temperature_grid=DEFAULT_TEMPERATURE_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    arm_d_eval["arm"] = "ARM_D_CHAR_TRIGRAM_BIGRAM"
    arm_d_eval["wall_s"] = time.time() - t_d_start

    # ---- Memory / GPU metrics (Fix #24) ----
    gpu_max_mem_alloc_mb = (
        float(torch.cuda.max_memory_allocated() / (1024 * 1024)) if gpu_avail else 0.0
    )

    # ---- Per-arm dict ----
    per_arm = {
        "ARM_A_NULL_UNIGRAM": arm_a_metrics,
        "ARM_B_BIGRAM_HRR": dict(arm_b_eval),
        "ARM_C_TRIGRAM_HRR": dict(arm_c_eval),
        "ARM_D_CHAR_TRIGRAM_BIGRAM": dict(arm_d_eval),
    }
    payload = {
        "_ckpt_key": f"seed{seed}",
        "seed": int(seed),
        "N": int(N_DIM),
        "V_TOK": int(V_TOK),
        "N_PARTITIONS": int(N_PARTITIONS),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "encoder_provenance": ENCODER_PROVENANCE_CELL,
        "path_c_compliant": PATH_C_COMPLIANT,
        "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "vocab_size_full": int(vocab_size_full),
        "word_bigram_top1": float(word_bigram_top1),
        "word_bigram_coverage": float(bigram_baseline["coverage"]),
        "unigram_baseline_top1": float(arm_a_top1),
        "uniform_baseline_bpc": float(compute_uniform_baseline_bpc(vocab_size_full)),
        "per_arm": per_arm,
        "gpu_avail": gpu_avail,
        "gpu_name": gpu_name,
        "gpu_max_mem_alloc_mb": gpu_max_mem_alloc_mb,
        "ingest_wall_s": float(t_ingest),
        "seed_wall_s": float(time.time() - t_seed_start),
    }
    print(
        f"[seed {seed}] per_arm top1: "
        f"A={arm_a_top1:.4f} "
        f"B={arm_b_eval['top1']:.4f} "
        f"C={arm_c_eval['top1']:.4f} "
        f"D={arm_d_eval['top1']:.4f} | "
        f"bigram_baseline={word_bigram_top1:.4f} | "
        f"gpu_max_mb={gpu_max_mem_alloc_mb:.1f} | "
        f"wall_s={payload['seed_wall_s']:.1f}",
        flush=True,
    )
    return payload


# ---------- Aggregator + verdict ----------
def _classify_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Apply LOCKED pre-reg bands to aggregated metrics."""
    if not per_seed:
        return {
            "verdict": "FAIL",
            "verdict_msg": "no seed payloads aggregated",
            "tier": "FAIL",
        }
    # Aggregate per-arm top1 across seeds.
    seeds_sorted = sorted(per_seed.keys())
    arm_top1: Dict[str, List[float]] = {a: [] for a in ARMS}
    for s in seeds_sorted:
        p = per_seed[s]
        for a in ARMS:
            v = p.get("per_arm", {}).get(a, {}).get("top1")
            if v is not None:
                arm_top1[a].append(float(v))
    arm_summary: Dict[str, Dict[str, float]] = {}
    for a, vals in arm_top1.items():
        if not vals:
            arm_summary[a] = {"mean": float("nan"), "std": float("nan"), "cv": float("nan"), "n": 0}
            continue
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=0))
        cv = float(std / mean) if mean > 1e-9 else float("inf")
        arm_summary[a] = {"mean": mean, "std": std, "cv": cv, "n": len(vals)}

    null_mean = arm_summary["ARM_A_NULL_UNIGRAM"]["mean"]
    bc_mean = max(
        arm_summary["ARM_B_BIGRAM_HRR"]["mean"],
        arm_summary["ARM_C_TRIGRAM_HRR"]["mean"],
    )
    best_arm = (
        "ARM_B_BIGRAM_HRR"
        if arm_summary["ARM_B_BIGRAM_HRR"]["mean"] >= arm_summary["ARM_C_TRIGRAM_HRR"]["mean"]
        else "ARM_C_TRIGRAM_HRR"
    )
    best_cv = arm_summary[best_arm]["cv"]
    lift_over_null = bc_mean - null_mean

    # Discriminator gate: NULL must HARD_FAIL
    null_discriminator_visible = null_mean < NULL_DISCRIMINATOR_CEIL

    if (
        bc_mean >= HARD_PASS_TOP1_FLOOR
        and lift_over_null >= HARD_PASS_LIFT_OVER_NULL
        and best_cv <= HARD_PASS_CV_CEILING
        and null_discriminator_visible
    ):
        verdict = "HARD_PASS"
        tier = "CHAIN_GRADE_CANDIDATE"
        msg = (
            f"HARD_PASS: best={best_arm} top1={bc_mean:.4f} (>= {HARD_PASS_TOP1_FLOOR}); "
            f"lift_over_null={lift_over_null:.4f} (>= {HARD_PASS_LIFT_OVER_NULL}); "
            f"cv={best_cv:.4f} (<= {HARD_PASS_CV_CEILING}); "
            f"null={null_mean:.4f} (< {NULL_DISCRIMINATOR_CEIL})"
        )
    elif MIDDLE_BAND_LOWER <= bc_mean < MIDDLE_BAND_UPPER:
        verdict = "MIDDLE_BAND"
        tier = "MEASURED_MECHANISM"
        msg = (
            f"MIDDLE_BAND: best={best_arm} top1={bc_mean:.4f} in "
            f"[{MIDDLE_BAND_LOWER}, {MIDDLE_BAND_UPPER}); "
            f"null={null_mean:.4f}; lift={lift_over_null:.4f}; cv={best_cv:.4f}"
        )
    else:
        verdict = "HARD_FAIL"
        tier = "FAIL"
        msg = (
            f"HARD_FAIL: best={best_arm} top1={bc_mean:.4f} (<= {NULL_DISCRIMINATOR_CEIL}); "
            f"null={null_mean:.4f}; lift={lift_over_null:.4f}; cv={best_cv:.4f}; "
            f"discriminator_visible={null_discriminator_visible}"
        )
    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "tier": tier,
        "arm_summary": arm_summary,
        "best_arm": best_arm,
        "best_arm_mean_top1": bc_mean,
        "best_arm_cv": best_cv,
        "null_mean_top1": null_mean,
        "lift_over_null": lift_over_null,
        "null_discriminator_visible": null_discriminator_visible,
    }


def main() -> None:
    if _ARGS.self_test:
        # Self-test already ran at module init; print marker + exit.
        print("SELF_TEST_OK", flush=True)
        return
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[main] anchor={ANCHOR_NAME} out_dir={out_dir} CONFIG={CONFIG_VERSION}", flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds([f"seed{s}" for s in SEEDS], out_dir, run_config=run_config)
    print(f"[main] resumable: done={done} remaining={remaining}", flush=True)

    for key in remaining:
        seed = int(key.replace("seed", ""))
        result = _run_one_seed(seed)
        write_partial(out_dir, key, result)

    agg = aggregate_partials(out_dir, [f"seed{s}" for s in SEEDS], run_config=run_config)
    classification = _classify_verdict(agg)

    summary = {
        "config_version": CONFIG_VERSION,
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "V_TOK": V_TOK,
        "N_PARTITIONS": N_PARTITIONS,
        "SEEDS": SEEDS,
        "encoder_provenance": ENCODER_PROVENANCE_CELL,
        "path_c_compliant": PATH_C_COMPLIANT,
        "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "pre_reg": {
            "HARD_PASS_TOP1_FLOOR": HARD_PASS_TOP1_FLOOR,
            "HARD_PASS_LIFT_OVER_NULL": HARD_PASS_LIFT_OVER_NULL,
            "HARD_PASS_CV_CEILING": HARD_PASS_CV_CEILING,
            "NULL_DISCRIMINATOR_CEIL": NULL_DISCRIMINATOR_CEIL,
            "MIDDLE_BAND_LOWER": MIDDLE_BAND_LOWER,
            "MIDDLE_BAND_UPPER": MIDDLE_BAND_UPPER,
        },
        **{k: v for k, v in classification.items() if k != "verdict_msg"},
    }
    elapsed_s = time.time() - t0
    metrics = {
        "verdict": classification["verdict"],
        "verdict_msg": classification["verdict_msg"],
        "elapsed_s": elapsed_s,
        "summary": summary,
        "per_seed": agg,
    }
    write_metrics(out_dir, metrics)
    print(f"[main] verdict={metrics['verdict']} elapsed_s={elapsed_s:.1f}", flush=True)
    print(f"[main] verdict_msg: {metrics['verdict_msg']}", flush=True)


if __name__ == "__main__":
    main()
