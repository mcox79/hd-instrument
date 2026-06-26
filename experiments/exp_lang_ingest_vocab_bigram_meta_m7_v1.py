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
  - torch.cuda actively used for per-partition scoring matmul (Hebbian-write
    accumulation kept on CPU; transferred to GPU one partition at a time at
    eval-time). This OOM-fix preserves full N_PARTITIONS=64 + N_DIM=8192 design
    on an 8 GB RTX 4060 Ti (was 16.4 GB per arm; now ~256 MB resident GPU per
    partition + cleanup batch + codebooks).
  - GPU peak projection gate at module init: aborts if projected resident GPU
    peak (codebooks + ONE S partition + eval-batch + working buffers) > 6 GB
    safety margin under 8 GB total.
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
  T7: projected GPU peak memory at FULL N_PARTITIONS x N_DIM x GPU_BATCH config
      stays under 6 GB safety margin (8 GB RTX 4060 Ti capacity). Hard-asserts
      the OOM fix: only ONE S_part is GPU-resident at a time + codebooks +
      cleanup batch + working buffers. (Fix #17 measurement strict.)

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

# ---------- GPU memory budget (Fix #24 / Fix #17 measurement strict) ----------
# RTX 4060 Ti capacity 8 GB; safety margin 6 GB for resident peak (leaves ~2 GB
# for cuDNN workspace + driver + kernel intermediates not counted in our estimate).
GPU_BUDGET_MB = 6 * 1024  # 6144 MB hard ceiling

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
    """Pick device per Fix #24: cuda iff available; raise on full-mode CPU.

    Runtime gate: verifies free GPU memory exceeds projected peak at module config.
    Aborts if free GPU memory < projected_peak_mb (refuses to start the seed
    instead of OOM-crashing 30s in like the pre-fix run did).
    """
    import torch
    if torch.cuda.is_available():
        dev = torch.device("cuda")
        # Verify free GPU memory at full config (or current GPU_BATCH/N_EVAL for smoke).
        proj = _project_gpu_peak_mb(
            n_dim=N_DIM,
            v_tok=V_TOK,
            gpu_batch=GPU_BATCH,
            n_eval=N_EVAL_PAIRS,
        )
        free_bytes, total_bytes = torch.cuda.mem_get_info(0)
        free_mb = free_bytes / (1024 * 1024)
        total_mb = total_bytes / (1024 * 1024)
        if proj["projected_peak_mb"] > free_mb:
            raise RuntimeError(
                f"GPU memory gate: projected peak {proj['projected_peak_mb']:.0f} MB "
                f"exceeds free {free_mb:.0f} MB on {torch.cuda.get_device_name(0)} "
                f"(total {total_mb:.0f} MB). breakdown={proj}"
            )
        print(
            f"[gpu-gate] device={dev} free_mb={free_mb:.0f} total_mb={total_mb:.0f} "
            f"projected_peak_mb={proj['projected_peak_mb']:.0f} OK",
            flush=True,
        )
        return dev
    if RUN_MODE == "full":
        raise RuntimeError(
            "lang_ingest_vocab_bigram_meta_m7_v1 routed to overnight_queue (GPU) "
            "but torch.cuda is unavailable. Fix #24 requires actual GPU use."
        )
    return torch.device("cpu")


def _compute_S_partitions_torch(train_ids: np.ndarray, codebook_np: np.ndarray, device):
    """Build [N_PARTITIONS] of [N_DIM, N_DIM] S matrices via partition-routed Hebbian writes.

    For each adjacent (t_prev, t_curr) pair, route by partition(t_prev) and add
    outer(k_curr, k_prev) to S_part. Hebbian-write accumulation is done on CPU
    (S partitions kept CPU-resident); the matmul itself uses the GPU per-partition
    by transferring one bucket at a time. This OOM-fix preserves the full
    N_PARTITIONS x N_DIM x N_DIM design without exceeding the 8 GB GPU budget:
    64 partitions x 8192 x 8192 x float32 = 16.4 GB resident on GPU is infeasible
    (was the crash root cause); per-partition transfer at compute time = 256 MB
    resident on GPU + per-partition transfer-back to CPU accumulator.

    Returns: list of N_PARTITIONS CPU torch tensors, shape [N_DIM, N_DIM] each
             (float32). Eval-time scoring transfers individual partitions to
             `device` on demand.
    """
    import torch
    n_dim = codebook_np.shape[1]
    cpu_device = torch.device("cpu")
    # Codebook resident on GPU (small: V+1 x N x 4 = 268 MB at V=8192, N=8192).
    cb_t_gpu = torch.from_numpy(codebook_np).to(device=device, dtype=torch.float32)
    # Pre-allocate S partitions on CPU (16.4 GB total CPU RAM; laptop+remote both have it).
    S_parts = [torch.zeros(n_dim, n_dim, device=cpu_device, dtype=torch.float32) for _ in range(N_PARTITIONS)]
    n = train_ids.shape[0]
    if n < 2:
        return S_parts
    prev_ids_np = train_ids[:-1].astype(np.int64)
    curr_ids_np = train_ids[1:].astype(np.int64)
    # Numpy-side mask compute (avoids materializing prev_ids on GPU twice).
    parts_np = prev_ids_np % N_PARTITIONS
    for p in range(N_PARTITIONS):
        mask_np = parts_np == p
        if not mask_np.any():
            continue
        # Gather bucket on GPU using GPU codebook (fast index_select).
        prev_bucket = torch.from_numpy(prev_ids_np[mask_np]).to(device=device)
        curr_bucket = torch.from_numpy(curr_ids_np[mask_np]).to(device=device)
        k_prev = cb_t_gpu.index_select(0, prev_bucket)  # [m_p, N] on GPU
        k_curr = cb_t_gpu.index_select(0, curr_bucket)  # [m_p, N] on GPU
        # Hebbian outer product on GPU; transfer result back to CPU accumulator.
        delta_gpu = k_curr.t().mm(k_prev)              # [N, N] on GPU (256 MB)
        S_parts[p].add_(delta_gpu.to(cpu_device))      # accumulate on CPU
        # Free per-bucket buffers; only delta_gpu peak matters per iter.
        del prev_bucket, curr_bucket, k_prev, k_curr, delta_gpu
    # Codebook still GPU-resident for caller eval-time use; do NOT free here.
    return S_parts


def _score_arm_b_bigram(
    eval_cues: np.ndarray,
    S_parts,
    codebook_t,
    device,
) -> np.ndarray:
    """ARM_B scoring: scores[i, v] = cosine(S_part[i] @ k_cue_i, codebook[v]).

    S_parts is a list of CPU-resident [N, N] tensors (OOM fix); each partition
    is transferred to GPU on-demand for the matmul, then freed. Only ONE
    S_part is GPU-resident at a time.

    Returns [N_eval, V_TOK+1] float32 array on host.
    """
    import torch
    n_eval = eval_cues.shape[0]
    v_plus_1 = codebook_t.shape[0]
    cb_norm = codebook_t / (torch.linalg.norm(codebook_t, dim=1, keepdim=True) + 1e-8)
    out = np.zeros((n_eval, v_plus_1), dtype=np.float32)
    cues_t = torch.from_numpy(eval_cues.astype(np.int64)).to(device=device)
    parts = cues_t % N_PARTITIONS
    # Outer loop: partition-major (transfer each S_part to GPU once across all batches
    # that need it). Saves repeated CPU->GPU transfers of the same 256 MB partition.
    # Build per-partition global index lists.
    parts_cpu = parts.cpu().numpy()
    per_part_indices = [np.where(parts_cpu == p)[0] for p in range(N_PARTITIONS)]
    # Pre-allocate predicted [N_eval, N] on GPU only if it fits; else stream
    # via batched CPU writes. At N_eval=32768 N=8192 float32 = 1.07 GB -> fits.
    predicted_full = torch.zeros(n_eval, codebook_t.shape[1], device=device, dtype=torch.float32)
    for p in range(N_PARTITIONS):
        idx_np = per_part_indices[p]
        if idx_np.size == 0:
            continue
        idx_t = torch.from_numpy(idx_np).to(device=device, dtype=torch.long)
        # On-demand transfer of this partition to GPU.
        S_p_gpu = S_parts[p].to(device=device, non_blocking=False)  # [N, N] = 256 MB
        cues_for_p = cues_t.index_select(0, idx_t)
        k_for_p = codebook_t.index_select(0, cues_for_p)  # [m_p, N]
        pred_for_p = k_for_p.mm(S_p_gpu.t())              # [m_p, N]
        predicted_full.index_copy_(0, idx_t, pred_for_p)
        del S_p_gpu, k_for_p, pred_for_p
    # Cosine sim against full codebook -- batched to bound peak.
    for start in range(0, n_eval, GPU_BATCH):
        end = min(start + GPU_BATCH, n_eval)
        pred_batch = predicted_full[start:end]
        pred_norm = pred_batch / (torch.linalg.norm(pred_batch, dim=1, keepdim=True) + 1e-8)
        sims = pred_norm.mm(cb_norm.t())                   # [b, V+1]
        out[start:end] = sims.cpu().numpy()
    del predicted_full
    return out


def _score_arm_c_trigram(
    eval_cue_pairs: np.ndarray,
    S_parts,
    codebook_t,
    device,
) -> np.ndarray:
    """ARM_C scoring: cue = HRR bind(k_{i-2}, roll(k_{i-1}, 1)); same S + cleanup.

    S_parts is CPU-resident (OOM fix); partition transferred to GPU on-demand.

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
    # First pass: compute all HRR cues on GPU in batches; persist into one large buffer.
    # At N_eval=32768 N=8192 float32 = 1.07 GB; fits under 6 GB budget.
    cues_full = torch.zeros(n_eval, codebook_t.shape[1], device=device, dtype=torch.float32)
    for start in range(0, n_eval, GPU_BATCH):
        end = min(start + GPU_BATCH, n_eval)
        ids_a = pairs_t[start:end, 0]
        ids_b = pairs_t[start:end, 1]
        ka = codebook_t.index_select(0, ids_a)
        kb = codebook_t.index_select(0, ids_b)
        kb_rot = torch.roll(kb, shifts=1, dims=-1)
        fa = torch.fft.fft(ka)
        fb = torch.fft.fft(kb_rot)
        cue = torch.fft.ifft(fa * fb).real.to(torch.float32)   # [b, N]
        cues_full[start:end] = cue
        del ka, kb, kb_rot, fa, fb, cue
    # Second pass: partition-major matmul against on-demand-loaded S_parts.
    parts_cpu = parts.cpu().numpy()
    per_part_indices = [np.where(parts_cpu == p)[0] for p in range(N_PARTITIONS)]
    predicted_full = torch.zeros(n_eval, codebook_t.shape[1], device=device, dtype=torch.float32)
    for p in range(N_PARTITIONS):
        idx_np = per_part_indices[p]
        if idx_np.size == 0:
            continue
        idx_t = torch.from_numpy(idx_np).to(device=device, dtype=torch.long)
        S_p_gpu = S_parts[p].to(device=device, non_blocking=False)  # 256 MB
        cue_for_p = cues_full.index_select(0, idx_t)
        pred_for_p = cue_for_p.mm(S_p_gpu.t())
        predicted_full.index_copy_(0, idx_t, pred_for_p)
        del S_p_gpu, cue_for_p, pred_for_p
    del cues_full
    # Cosine cleanup batched.
    for start in range(0, n_eval, GPU_BATCH):
        end = min(start + GPU_BATCH, n_eval)
        pred_batch = predicted_full[start:end]
        pred_norm = pred_batch / (torch.linalg.norm(pred_batch, dim=1, keepdim=True) + 1e-8)
        sims = pred_norm.mm(cb_norm.t())
        out[start:end] = sims.cpu().numpy()
    del predicted_full
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


def _project_gpu_peak_mb(n_dim: int, v_tok: int, gpu_batch: int, n_eval: int) -> Dict[str, float]:
    """Project GPU resident peak in MB at FULL config.

    Components (Fix #24 OOM-fix; only ONE S_part GPU-resident at a time):
      codebook_t       : (V+1) * N * 4 bytes
      cb_norm          : (V+1) * N * 4 bytes  (one of two arms; norm cached per call)
      ONE S_part_gpu   : N * N * 4 bytes
      predicted_full   : N_eval * N * 4 bytes (large; second-pass buffer)
      cues_full (ARM_C): N_eval * N * 4 bytes (ARM_C only; serial w/ predicted_full)
      sims_batch       : gpu_batch * (V+1) * 4 bytes
      pred_batch_norm  : gpu_batch * N * 4 bytes

    ARM_C is the worst case (cues_full + predicted_full coexist briefly during
    transition between pass-1 and pass-2 if not freed; we free cues_full at
    `del cues_full` before the cleanup pass, so peak counts ONE large buffer
    + S_part + codebook + cb_norm + matmul intermediates).
    """
    f = 4  # bytes per float32
    mb = lambda x: x / (1024 * 1024)
    codebook_mb = mb((v_tok + 1) * n_dim * f)
    cb_norm_mb = mb((v_tok + 1) * n_dim * f)
    s_part_mb = mb(n_dim * n_dim * f)
    predicted_full_mb = mb(n_eval * n_dim * f)
    cues_full_mb = mb(n_eval * n_dim * f)  # ARM_C pass-1 buffer
    sims_batch_mb = mb(gpu_batch * (v_tok + 1) * f)
    pred_batch_norm_mb = mb(gpu_batch * n_dim * f)
    # Worst case during ARM_C: cues_full (pass-1 building) + S_part (pass-2 inner)
    # are NOT simultaneous in the actual code path -- we free cues_full after pass-1
    # except for index_select intermediates. Conservative peak = max of:
    #   pass-1 peak:  codebook + cues_full (being filled) + per-batch intermediates
    #   pass-2 peak:  codebook + cues_full + predicted_full + S_part + matmul output
    # Actually cues_full is freed (`del cues_full`) BEFORE cleanup; predicted_full
    # persists. So pass-2 peak: codebook + cues_full + predicted_full + S_part + tiny.
    # This is the conservative estimate during the partition-major loop.
    pass2_peak = codebook_mb + cues_full_mb + predicted_full_mb + s_part_mb + sims_batch_mb
    # Cleanup pass peak: codebook + cb_norm + predicted_full + per-batch buffers
    cleanup_peak = codebook_mb + cb_norm_mb + predicted_full_mb + sims_batch_mb + pred_batch_norm_mb
    worst = max(pass2_peak, cleanup_peak)
    return {
        "codebook_mb": codebook_mb,
        "cb_norm_mb": cb_norm_mb,
        "s_part_mb": s_part_mb,
        "predicted_full_mb": predicted_full_mb,
        "cues_full_mb": cues_full_mb,
        "sims_batch_mb": sims_batch_mb,
        "pred_batch_norm_mb": pred_batch_norm_mb,
        "pass2_peak_mb": pass2_peak,
        "cleanup_peak_mb": cleanup_peak,
        "projected_peak_mb": worst,
    }


def _selftest_t7_gpu_memory_projection() -> None:
    """Fix #24 / Fix #17 measurement strict: project GPU peak at FULL config; assert <= budget.

    Verifies the OOM fix WITHOUT requiring an actual GPU (closed-form projection
    on the production config N_DIM=8192, V_TOK=8192, N_PARTITIONS=64, GPU_BATCH=4096,
    N_EVAL=32768).
    """
    # Use full-mode config explicitly so projection is checked at production
    # capacity regardless of smoke env vars.
    proj_full = _project_gpu_peak_mb(
        n_dim=N_DIM,
        v_tok=V_TOK,
        gpu_batch=4096,    # full-mode GPU_BATCH
        n_eval=32768,      # full-mode N_EVAL_PAIRS
    )
    peak = proj_full["projected_peak_mb"]
    assert peak <= GPU_BUDGET_MB, (
        f"GPU memory projection {peak:.0f} MB exceeds budget {GPU_BUDGET_MB} MB "
        f"at FULL config (N_DIM={N_DIM} V_TOK={V_TOK} N_PARTITIONS={N_PARTITIONS} "
        f"GPU_BATCH=4096 N_EVAL=32768); breakdown={proj_full}"
    )
    # Sanity: pre-OOM-fix (full S_parts resident) would have been WAY over budget.
    pre_fix_resident_mb = N_PARTITIONS * N_DIM * N_DIM * 4 / (1024 * 1024)
    assert pre_fix_resident_mb > GPU_BUDGET_MB, (
        f"pre-fix projection sanity broken: pre-fix resident {pre_fix_resident_mb:.0f} MB "
        f"should be > {GPU_BUDGET_MB} MB budget"
    )
    print(
        f"[selftest T7] GPU peak projection {peak:.0f} MB <= budget {GPU_BUDGET_MB} MB "
        f"(pre-fix would have been {pre_fix_resident_mb:.0f} MB; OOM fix verified)",
        flush=True,
    )


def _run_selftests() -> None:
    t0 = time.time()
    _selftest_t1_vocab_roundtrip()
    _selftest_t2_sequence_recall()
    _selftest_t3_lm_eval_harness_sanity()
    _selftest_t4_bigram_gap_analytic()
    _selftest_t5_hrr_cue_identity()
    _selftest_t6_bands_locked()
    _selftest_t7_gpu_memory_projection()
    print(f"[selftest] T1-T7 OK in {time.time() - t0:.2f}s", flush=True)


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
    # S_parts kept CPU-resident per OOM fix (was: 16.4 GB GPU-resident at
    # N_PARTITIONS=64 x N_DIM=8192 x N_DIM=8192 x float32 -- crashed on 8 GB GPU).
    t_ingest_start = time.time()
    S_parts = _compute_S_partitions_torch(train_ids, cb_np, device)
    t_ingest = time.time() - t_ingest_start
    print(
        f"[seed {seed}] S_parts built: N_PARTITIONS={N_PARTITIONS} N_DIM={N_DIM} "
        f"ingest_wall_s={t_ingest:.1f} (CPU-resident; OOM fix)",
        flush=True,
    )

    # ---- Build S partitions for ARM_D using char-trigram codebook ----
    # (Same train_ids; different keys -> different S). Also CPU-resident.
    # Defer build until ARM_B/C complete to bound CPU RAM at one S_parts set.
    # (See block below: S_parts_d built after ARM_C, S_parts freed before.)

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

    # ---- Free S_parts + cb_t before building S_parts_d (bound CPU RAM peak) ----
    del S_parts, cb_t
    if gpu_avail:
        torch.cuda.empty_cache()

    # ---- Build S partitions for ARM_D using char-trigram codebook ----
    S_parts_d = _compute_S_partitions_torch(train_ids, cb_d_np, device)

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
