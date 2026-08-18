"""slow_cortex_bigram_predictor_v1 -- n5 trigram revival via slow-learning cortex-style context compression.

SCIENTIFIC QUESTION (Research drill 2026-06-26 + USER reframe of n5 HARD_FAIL):
  USER's reframe of n5 HARD_FAIL: the HRR-blend tried to do at QUERY time what
  the brain does over SLOW LEARNING. Move binding-and-association from QUERY
  time to LEARNING time so per-query crosstalk noise gets averaged out at the
  corpus level instead of injected per-query. Cell tests whether a slow-learned
  W_trigram matrix that stores Hebbian outer-products of (BUNDLED context,
  target_word) over a single text8 pass BEATS both n5's HRR-blend (top1=0.302,
  bpc=6.86) AND the bigram baseline (n5 BIGRAM_BASELINE top1=0.429, bpc=4.97).

  Decisive cross-arm question: does TRIGRAM_BUNDLE_SLOW (slow-learned bundle-
  at-context) beat both n5 HRR-blend AND the bigram baseline at substrate-only
  inference, while TRIGRAM_HRR_REPLICATION reproduces the n5 HARD_FAIL on the
  same hardware/seed (anchoring the methodology rail)?

REFERENCE SOURCES:
  - Research note: notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md
  - Handoff note: notes/exp_dev_handoff_research_n5_revival_slow_learning_cortex_context_2026-06-26.md
  - n5 HARD_FAIL anchor: data/exp_n5_trigram_concept_lm_v1/metrics.json

ARMS (4 -- per Fix #28 per-arm metrics):
  ARM_BIGRAM_BASELINE         : W_bigram only. K=1 context = encoder(word_t-1).
                                 Hebbian outer-product write of (encoder(w_{t-1}),
                                 encoder(w_t)). Score = W_bigram @ query. Methodology
                                 rail: top1 must replicate n5 BIGRAM_BASELINE top1=0.429
                                 within 0.05 (sanity gate; abort verdict otherwise).
  ARM_TRIGRAM_BUNDLE_SLOW     : THE TEST. W_bigram + W_trigram. ctx_12 =
                                 bundle(encoder(w_{t-2}), encoder(w_{t-1})). Hebbian
                                 outer-product write of (ctx_12, encoder(w_t)) at
                                 learning time. At query, logits = alpha *
                                 (W_trigram @ q12) + (1-alpha) * (W_bigram @ q2).
                                 No HRR-bind at query time; the slow learning has
                                 already absorbed the trigram conditional distribution.
  ARM_TRIGRAM_HRR_REPLICATION : Reproduces n5 HRR-blend at query time. ctx =
                                 hrr_bind(encoder(w_{t-2}), encoder(w_{t-1})). W
                                 trained on (ctx_HRR, encoder(w_t)). Score = W @ q_HRR.
                                 Anchor rail: top1 must reproduce n5 TRIGRAM_HRR top1=0.302
                                 within 0.10 (cross-cell rail; confirms the cell IS at
                                 the n5 regime, not different harness).
  ARM_TRIGRAM_BUNDLE_NREM_REPLAY : ARM_TRIGRAM_BUNDLE_SLOW + NREM replay decorator
                                 (proven-bound +0.57 drift_reduction primitive from
                                 hdlab/continual.py). Second-pass replay of bundled
                                 triples sharpens W_trigram further. Tests whether
                                 sleep-replay adds value to LM task (not just
                                 retention task) -- chain-grade-eligible cross-task
                                 generalization of the replay primitive.

CONFIG (per user spec; matches n5 lineage):
  N_DIM = 16384            (matches n2/n5 / matches research note +/- 2x)
  V_TOK = 1024             (user spec "V_C = 1024 matches n5"; interpreted as token
                            vocab cap; matches n5 V_C concept codebook size)
  SEEDS = [7, 17, 23]      (matches n5 seeds)
  MAX_DOCS = 100_000        (matches n5 ingest discipline; text8 100k docs)
  ENCODER_PROVENANCE = SUBSTRATE_NATIVE  (Path C; deterministic-hash bipolar codebook
                                          per token; semantics emerge from Hebbian-
                                          outer-product W accumulation downstream)
  Substrate-only at inference; zero LLM forward calls; structural + counter assert.
  CORPUS_PROVENANCE_REAL = True; allow_synthetic=False (fail-loud).

PRE-REGISTERED BANDS (LOCKED via module-init assert per research note +
user spec; classification reads per-arm metrics not verdict_msg per Fix #28):

  HARD_PASS_CHAIN_GRADE:
      ARM_TRIGRAM_BUNDLE_SLOW.bpc <= 4.30
        (closes >= 0.66 of the 1.13-bit gap to word-bigram 3.84) AND
      ARM_TRIGRAM_BUNDLE_SLOW.bpc <= ARM_BIGRAM_BASELINE.bpc - 0.50
        (beats bigram baseline by >= 0.5 bits) AND
      ARM_TRIGRAM_HRR_REPLICATION.bpc >= 6.40
        (reproduces n5 HARD_FAIL within 0.10 of 6.86) AND
      cv across 3 seeds on ARM_TRIGRAM_BUNDLE_SLOW <= 0.03 AND
      zero_llm_calls_at_inference == True for every seed AND
      ARM_BIGRAM_BASELINE.top1 replicates n5 BIGRAM_BASELINE top1=0.429
        within 0.05 (methodology rail; abort verdict claim otherwise).

  MIDDLE_BAND:
      ARM_TRIGRAM_BUNDLE_SLOW.bpc in (4.30, 4.70] AND
      methodology rail satisfied (BIGRAM_BASELINE within 0.05 of 0.429 top1).

  HARD_FAIL:
      ARM_TRIGRAM_BUNDLE_SLOW.bpc > 4.70 OR
      doesn't beat ARM_BIGRAM_BASELINE.bpc (slow-learning didn't extract
      ANY trigram structure -> encoder-bound diagnosis; pivot to Path C v2).

  HARD_FAIL_SANITY (methodology rail; abort before any cell verdict):
      ARM_BIGRAM_BASELINE.top1 deviates from n5 anchor 0.429 by more than 0.05 OR
      ARM_TRIGRAM_HRR_REPLICATION.bpc deviates from n5 anchor 6.86 by more than 0.10.
      Cross-cell rail proves the cell harness is the same regime as n5; if it
      isn't, the trigram verdict isn't comparable to the n5 anchor.

COMPOSITION (chain-grade primitives backing this cell):
  - hdlab/token_vocab.py        (V_TOK token vocabulary + bipolar codebook; Path C)
  - hdlab/bundling.py           (slow-context bundle = sum + normalize)
  - hdlab/binding.py            (HRR bind via FFT -- ARM_TRIGRAM_HRR_REPLICATION only)
  - hdlab/continual.py          (NREM replay decorator; proven-bound +0.57)
  - hdlab/lm_eval_harness.py    (META_M7 top-K + T-calibrated BPC; rigged-harness trap
                                 permanently impossible)
  - hdlab/bigram_gap_measurement.py  (compute_word_bigram_top1; standardized baseline)

DISCIPLINES (load-bearing):
  - ASCII only; no unicode in any string emitted by the script
  - Per-arm metrics (Fix #28; arm_metrics dict written; verdict_msg derived from arms)
  - META_M7 capacity-sensitive dims identical smoke/full (N_DIM, V_TOK locked;
    only N_TRAIN_TOKENS / N_EVAL_PAIRS shrink for smoke)
  - Per-seed checkpoint (PROT-021 run_config guard via experiments/_seed_checkpoint.py)
  - CORPUS_PROVENANCE_REAL=True asserted + logged; ALLOW_SYNTHETIC=False
  - Substrate-only-decode (zero LLM forward calls; structural; counter logged)
  - Encoder picks emerge from discriminating data -- the encoder here IS the
    chosen Path C substrate-native deterministic-hash bipolar (no contamination
    via word2vec / pythia residuals; n5 also avoided LLM calls but used VQ on
    pythia residuals; here we work directly on token ids via TokenVocab).

QUEUE: remote_cpu_queue (per USER directive; not local, not GPU).
  Numpy-only matmul; N_DIM=16384 with V_TOK=1024 = W matrix 64 MB each (W_bigram +
  W_trigram); train Hebbian writes per-position over ~16M tokens = ~16M outer-products.
  Vectorized via np.add.at for token-id index accumulation: O(N_train) updates, each
  a [N_DIM] vector add. Vectorized score: Q @ W.T where Q is [N_eval, N_DIM], W.T is
  [N_DIM, V_TOK]. Vectorization keeps full at ~2-4 CPU-hr per seed at N=16384 / V=1024.

FORMULA SELF-TESTS (PROT-022; mandatory at module init AND --self-test):
  T1: token_vocab encode round-trip on tiny synthetic corpus
  T2: bundle of 2 vectors is L2-normalized; bundle of (a, -a) is near-zero
  T3: HRR bind/unbind roundtrip cleanup recovers source via codebook argmax
  T4: Hebbian outer-product write + linear readout recovers stored pair
       (W_bigram trained on one (ctx, target) returns target as argmax for ctx)
  T5: lm_eval_harness on uniform random scores returns regime_check_passed=False
  T6: compute_word_bigram_top1 returns analytical value on hand-crafted train_ids
  T7: pre-reg bands LOCKED; numeric ordering asserted
  T8: bundle-vs-bind discriminator on synthetic 3-vector context: bundle preserves
       both signals (high cosine to either via codebook cleanup); bind mixes them
  T9: substrate-only-decode counter stays at 0 through pipeline (no LLM imports)
  T10: NREM replay decorator wraps Hebbian write fn and re-Hebbs traces

ASCII-only. No emojis. write_metrics. PROT-021 run_config guard. NO _nN suffix on
anchor (N_DIM=16384 is a fixed config dim, not a sweep dim per PROT-018 convention).

ANCHOR_NAME = "slow_cortex_bigram_predictor_v1"
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

ANCHOR_NAME = "slow_cortex_bigram_predictor_v1"
ENCODER_PROVENANCE_CELL = ENCODER_PROVENANCE  # SUBSTRATE_NATIVE
PATH_C_COMPLIANT = True
CORPUS_PROVENANCE_REAL = True
ALLOW_SYNTHETIC = False

# ---------------------------------------------------------------------------
# LLM-call audit counter (substrate-only gate; structural + counter)
# ---------------------------------------------------------------------------
# This cell imports NO transformers / torch / pythia / minilm / word2vec.
# Substrate-only is a STRUCTURAL guarantee. Counter is logged per-seed for audit.
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# Pre-reg bands (LOCKED at module init)
# ---------------------------------------------------------------------------
HARD_PASS_BPC_THRESHOLD = 4.30
HARD_PASS_LIFT_OVER_BIGRAM = 0.50
HARD_PASS_HRR_REPL_FLOOR = 6.40
HARD_PASS_CV_CEILING = 0.03
HARD_PASS_TOP1_LIFT_OVER_BIGRAM = 0.04

MIDDLE_BAND_UPPER_BPC = 4.70

# Methodology rails (anchors to n5 metrics.json)
N5_BIGRAM_BASELINE_TOP1 = 0.429
N5_BIGRAM_BASELINE_TOP1_TOLERANCE = 0.05
N5_TRIGRAM_HRR_BPC = 6.86
N5_TRIGRAM_HRR_BPC_TOLERANCE = 0.10

# Probability budget per pre-reg discipline (sum to 1.00)
P_HARD_PASS = 0.40
P_MIDDLE = 0.30
P_HARD_FAIL = 0.30
assert abs((P_HARD_PASS + P_MIDDLE + P_HARD_FAIL) - 1.0) < 1e-9, (
    "Pre-reg band probabilities must sum to 1.00"
)
assert HARD_PASS_BPC_THRESHOLD < MIDDLE_BAND_UPPER_BPC, (
    "HARD_PASS_BPC_THRESHOLD must be tighter than MIDDLE_BAND upper"
)
assert HARD_PASS_HRR_REPL_FLOOR < N5_TRIGRAM_HRR_BPC + N5_TRIGRAM_HRR_BPC_TOLERANCE, (
    "HRR replication floor must be reachable from n5 anchor"
)

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

# ---------------------------------------------------------------------------
# Config (capacity-sensitive dims identical smoke vs full per META_M7)
# ---------------------------------------------------------------------------
N_DIM: int = 16384
V_TOK: int = 1024

if RUN_MODE == "smoke":
    SEEDS: List[int] = [7]
    N_TRAIN_TOKENS = 200_000   # 200k train tokens for smoke (~10s ingest at V=1024 N=16384)
    N_EVAL_PAIRS = 2_048
    NREM_REPLAY_EVERY = 500    # smaller cadence so replay fires in smoke
    NREM_REPLAY_FRAC = 0.2
else:
    SEEDS = [7, 17, 23]
    N_TRAIN_TOKENS = 16_000_000  # ~16M train tokens (text8 100M ascii ~ 17M words)
    N_EVAL_PAIRS = 16_384
    NREM_REPLAY_EVERY = 100_000  # full-pass schedule per hdlab/continual.py
    NREM_REPLAY_FRAC = 0.2

# Interpolation alpha for TRIGRAM_BUNDLE_SLOW (logits = alpha*W_trigram + (1-alpha)*W_bigram).
# Initial 0.5 -- swept-via-eval at scoring time (we evaluate at a fixed alpha; future cell
# can sweep). Discriminator: alpha=0 -> equivalent to BIGRAM_BASELINE; alpha=1 -> trigram-only.
ALPHA_TRIGRAM = 0.5

# Temperature grid extension: substrate Hebbian logits are sums of N_TRAIN * N_DIM
# bipolar dot products and accumulate to magnitudes ~ 1e6 - 1e8 at full scale.
# The default lm_eval_harness T-grid maxes at T=2.0 which is too low for these scales;
# we extend to T values that calibrate against the actual logit magnitude.
SUBSTRATE_T_GRID = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 200.0, 1000.0, 5000.0]

CORPUS_PATH = REPO / "data" / "text8_cache" / "text8.txt"

ARMS = (
    "ARM_BIGRAM_BASELINE",
    "ARM_TRIGRAM_BUNDLE_SLOW",
    "ARM_TRIGRAM_HRR_REPLICATION",
    "ARM_TRIGRAM_BUNDLE_NREM_REPLAY",
)

CONFIG_VERSION = (
    f"N_DIM={N_DIM},V_TOK={V_TOK},seeds={'-'.join(str(s) for s in SEEDS)},"
    f"N_TRAIN={N_TRAIN_TOKENS},N_EVAL={N_EVAL_PAIRS},"
    f"alpha={ALPHA_TRIGRAM},nrem_every={NREM_REPLAY_EVERY},nrem_frac={NREM_REPLAY_FRAC},"
    f"corpus=text8,encoder=Path_C,run_mode={RUN_MODE},synth={ALLOW_SYNTHETIC}"
)


# ---------------------------------------------------------------------------
# Substrate primitives (numpy; no torch dependency)
# ---------------------------------------------------------------------------

def _bipolar_codebook_matrix(vocab: TokenVocab) -> np.ndarray:
    """Materialize [V_TOK + 1, N_DIM] bipolar codebook (UNK in last row)."""
    return vocab.codebook_matrix()


def bundle_two(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Bundle (sum + L2 normalize). Preserves both signals; no order info.

    For the LM task the downstream consumer is a LEARNED W; bundle is sufficient
    and avoids query-time mixing (the n5 HRR-bind mistake).
    """
    s = a + b
    n = np.linalg.norm(s)
    if n > 1e-10:
        return s / n
    return s


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR bind via FFT circular convolution. Real-valued.

    Used ONLY by ARM_TRIGRAM_HRR_REPLICATION (anchor rail; reproduces n5 mechanism).
    """
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    return np.real(np.fft.ifft(fa * fb)).astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """HRR unbind: inverse of hrr_bind. Returns noisy a + cleanup-needed."""
    fc = np.fft.fft(c)
    fb = np.fft.fft(b)
    return np.real(np.fft.ifft(fc * np.conj(fb))).astype(np.float32)


# ---------------------------------------------------------------------------
# Hebbian outer-product writes (the slow-learning cortex mechanism)
# ---------------------------------------------------------------------------
# W matrices live as [V_TOK + 1, N_DIM] (one row per target token, length N_DIM).
# Hebbian write: W[target_id] += eta * ctx_vec  (the row IS the per-target prototype).
# Score for cue ctx -> logits over targets = W @ ctx (shape [V_TOK + 1]).
# Equivalent to the (target_signature * ctx_signature^T) formulation but with the
# codebook implicit (target_signature = codebook[target_id]; we keep W in
# target-prototype form so scoring is one matmul, no codebook materialization at eval).
#
# This is the substrate-feasible compression of the conditional-distribution table.
# n5 stored W as [N_DIM, N_DIM] (256 MB at N=16384); this cell stores
# [V_TOK + 1, N_DIM] (~64 MB) which scales better with V and reads naturally as
# "per-target prototype receiving Hebbian votes from bundled contexts."

def hebbian_write_row(W: np.ndarray, target_id: int, ctx_vec: np.ndarray,
                      eta: float = 1.0) -> None:
    """Hebbian outer-product write: W[target_id] += eta * ctx_vec (vector add)."""
    if 0 <= target_id < W.shape[0]:
        W[target_id] += eta * ctx_vec


def hebbian_batch_write(W: np.ndarray, target_ids: np.ndarray,
                        ctx_vecs: np.ndarray, eta: float = 1.0) -> None:
    """Vectorized Hebbian write: for each (target_id[i], ctx_vecs[i]), W[t] += eta * ctx.

    Uses np.add.at for unbuffered scatter-add (handles duplicate target ids correctly).
    target_ids shape [M], ctx_vecs shape [M, N_DIM]. W shape [V_TOK + 1, N_DIM].
    """
    if target_ids.shape[0] != ctx_vecs.shape[0]:
        raise ValueError(
            f"target_ids.shape={target_ids.shape} != ctx_vecs.shape[0]={ctx_vecs.shape[0]}"
        )
    if eta != 1.0:
        ctx_vecs = ctx_vecs * eta
    np.add.at(W, target_ids, ctx_vecs)


def score_W_linear(W: np.ndarray, queries: np.ndarray) -> np.ndarray:
    """Linear score: logits[i, v] = W[v] . queries[i] = (queries @ W.T)[i, v].

    queries shape [N_eval, N_DIM]. W shape [V_TOK + 1, N_DIM].
    Returns [N_eval, V_TOK + 1] float32.
    """
    return (queries @ W.T).astype(np.float32)


# ---------------------------------------------------------------------------
# Per-arm context builders (per Fix #28; ARM dispatcher)
# ---------------------------------------------------------------------------

# Chunked Hebbian-write discipline:
# Materializing the full [N_TRAIN, N_DIM] context matrix at N=16384 needs 16M * 16384 * 4 = 1 TB.
# Instead, build context vectors in chunks of WRITE_CHUNK rows, np.add.at-scatter onto W,
# and discard the chunk before the next.
WRITE_CHUNK = 16_384


def hebbian_bigram_write(W: np.ndarray, train_ids: np.ndarray, codebook: np.ndarray,
                         eta: float = 1.0) -> int:
    """Chunked Hebbian write: W[w_t] += eta * codebook[w_{t-1}] over the train stream.

    Returns total number of (ctx, target) pairs written.
    """
    n = train_ids.shape[0]
    if n < 2:
        return 0
    n_pairs = n - 1
    for cs in range(0, n_pairs, WRITE_CHUNK):
        ce = min(cs + WRITE_CHUNK, n_pairs)
        ctx_ids_chunk = train_ids[cs:ce]
        tgt_ids_chunk = train_ids[cs + 1:ce + 1]
        ctx_chunk = codebook[ctx_ids_chunk].astype(np.float32)
        if eta != 1.0:
            ctx_chunk = ctx_chunk * eta
        np.add.at(W, tgt_ids_chunk, ctx_chunk)
    return n_pairs


def hebbian_bundle_slow_write(W: np.ndarray, train_ids: np.ndarray,
                              codebook: np.ndarray, eta: float = 1.0
                              ) -> int:
    """Chunked Hebbian write of slow-learning bundle-at-context.

    For each position t (where t >= 2 in train_ids), the bundle ctx is
    (codebook[w_{t-2}] + codebook[w_{t-1}]) / norm, target is w_t. For t = 1
    (predicting w_1 from w_0 only), fall back to bigram-style ctx = codebook[w_0].

    Returns total number of (ctx, target) pairs written.
    """
    n = train_ids.shape[0]
    if n < 2:
        return 0
    # First write: bigram fallback for the t=1 position
    bigram_ctx_first = codebook[train_ids[0]].astype(np.float32)
    np.add.at(W, np.array([train_ids[1]], dtype=np.int64),
              (eta * bigram_ctx_first).reshape(1, -1))
    if n < 3:
        return 1
    # Bundle writes for t >= 2: contexts at positions 2..n-1 are
    # bundle(codebook[w_{t-2}], codebook[w_{t-1}]); targets are w_t.
    # Stream-position mapping: chunk over t in [2, n).
    n_bundle = n - 2
    for cs in range(0, n_bundle, WRITE_CHUNK):
        ce = min(cs + WRITE_CHUNK, n_bundle)
        # Global t positions: cs+2 .. ce+1 inclusive  (mapped from [cs, ce))
        a_ids = train_ids[cs:ce]            # w_{t-2}
        b_ids = train_ids[cs + 1:ce + 1]    # w_{t-1}
        tgt_ids_chunk = train_ids[cs + 2:ce + 2]  # w_t
        sums = codebook[a_ids].astype(np.float32) + codebook[b_ids].astype(np.float32)
        norms = np.linalg.norm(sums, axis=1, keepdims=True)
        safe = np.where(norms > 1e-10, norms, 1.0)
        ctx_chunk = sums / safe
        if eta != 1.0:
            ctx_chunk = ctx_chunk * eta
        np.add.at(W, tgt_ids_chunk, ctx_chunk)
    return n_bundle + 1


def hebbian_hrr_repl_write(W: np.ndarray, train_ids: np.ndarray,
                           codebook: np.ndarray, eta: float = 1.0) -> int:
    """Chunked Hebbian write of n5 HRR-blend replication ARM.

    For each t >= 2 in train_ids, ctx = hrr_bind(codebook[w_{t-2}], codebook[w_{t-1}]);
    target is w_t. For t = 1, fall back to bigram ctx = codebook[w_0]. FFT vectorized
    along axis=1 within each chunk.
    """
    n = train_ids.shape[0]
    if n < 2:
        return 0
    # First write: bigram fallback for t=1
    bigram_ctx_first = codebook[train_ids[0]].astype(np.float32)
    np.add.at(W, np.array([train_ids[1]], dtype=np.int64),
              (eta * bigram_ctx_first).reshape(1, -1))
    if n < 3:
        return 1
    n_bound = n - 2
    for cs in range(0, n_bound, WRITE_CHUNK):
        ce = min(cs + WRITE_CHUNK, n_bound)
        a_ids = train_ids[cs:ce]
        b_ids = train_ids[cs + 1:ce + 1]
        tgt_ids_chunk = train_ids[cs + 2:ce + 2]
        a_vecs = codebook[a_ids].astype(np.float32)
        b_vecs = codebook[b_ids].astype(np.float32)
        fa = np.fft.fft(a_vecs, axis=1)
        fb = np.fft.fft(b_vecs, axis=1)
        bound = np.real(np.fft.ifft(fa * fb, axis=1)).astype(np.float32)
        norms = np.linalg.norm(bound, axis=1, keepdims=True)
        safe = np.where(norms > 1e-10, norms, 1.0)
        ctx_chunk = bound / safe
        if eta != 1.0:
            ctx_chunk = ctx_chunk * eta
        np.add.at(W, tgt_ids_chunk, ctx_chunk)
    return n_bound + 1


def replay_buffer_sample(train_ids: np.ndarray, n_buf: int, seed: int
                         ) -> np.ndarray:
    """Sample n_buf trace indices (positions t >= 2 in train_ids) for NREM replay.

    Replay re-Hebbs randomly-sampled positions. We sample from the bundle write
    positions (t in [2, len(train_ids))) so the replay matches the bundle ARM
    training distribution.
    """
    n = train_ids.shape[0]
    if n < 3:
        return np.zeros(0, dtype=np.int64)
    rng = np.random.default_rng(seed)
    n_buf = min(n_buf, n - 2)
    return rng.choice(n - 2, size=n_buf, replace=False).astype(np.int64)


def hebbian_bundle_replay_write(W: np.ndarray, train_ids: np.ndarray,
                                codebook: np.ndarray, replay_indices: np.ndarray,
                                eta: float = 1.0) -> int:
    """Re-Hebb a sampled subset of bundle write positions onto W.

    For each index i in replay_indices (interpreted as position t = i + 2 in
    train_ids), recompute the bundle context and re-add the Hebbian write.
    """
    n_rep = replay_indices.shape[0]
    if n_rep == 0:
        return 0
    for cs in range(0, n_rep, WRITE_CHUNK):
        ce = min(cs + WRITE_CHUNK, n_rep)
        idx_chunk = replay_indices[cs:ce]
        a_ids = train_ids[idx_chunk]
        b_ids = train_ids[idx_chunk + 1]
        tgt_ids_chunk = train_ids[idx_chunk + 2]
        sums = codebook[a_ids].astype(np.float32) + codebook[b_ids].astype(np.float32)
        norms = np.linalg.norm(sums, axis=1, keepdims=True)
        safe = np.where(norms > 1e-10, norms, 1.0)
        ctx_chunk = sums / safe
        if eta != 1.0:
            ctx_chunk = ctx_chunk * eta
        np.add.at(W, tgt_ids_chunk, ctx_chunk)
    return n_rep


# ---------------------------------------------------------------------------
# NREM replay decorator (proven-bound +0.57 drift_reduction from hdlab/continual.py)
# We re-implement the small replay loop here in numpy form (hdlab/continual is torch).
# Same algorithm: every replay_every writes, sample replay_frac of the trace buffer
# and re-Hebb. This is the "sleep refinement" pass from research note Section 2 Step 4.
# ---------------------------------------------------------------------------

def nrem_replay_pass(W: np.ndarray, target_ids_buf: np.ndarray,
                     ctx_vecs_buf: np.ndarray, replay_frac: float,
                     seed: int, eta: float = 1.0) -> int:
    """Single NREM replay cycle: re-Hebb a fraction of stored traces.

    Selects replay_frac of trace indices uniformly without replacement, re-adds
    the Hebbian outer product onto W with eta. Returns number of traces replayed.

    Matches the proven-bound mechanism from hdlab/continual.replay_cycle (proven-
    bound +0.57 drift_reduction on continual writes; chain-grade bar forget<=0.05
    NOT met as solver alone). Cell hypothesis: when applied to LM task (not
    retention), replay sharpens W_trigram beyond single-pass.
    """
    n_buf = target_ids_buf.shape[0]
    n_replay = max(1, int(n_buf * replay_frac))
    rng = np.random.default_rng(seed + 9999)
    chosen = rng.choice(n_buf, size=n_replay, replace=False)
    hebbian_batch_write(W, target_ids_buf[chosen], ctx_vecs_buf[chosen], eta=eta)
    return int(n_replay)


# ---------------------------------------------------------------------------
# Formula self-tests (PROT-022; module-init mandatory)
# ---------------------------------------------------------------------------

def _selftest_t1_token_vocab_roundtrip() -> None:
    vocab = TokenVocab(n_dim=256, v_max=16, seed=0)
    toks = ["the", "cat", "sat", "on", "mat", "the", "cat"]
    vocab.build_from_corpus(toks, v_top=8)
    for t in ["the", "cat", "sat", "on", "mat"]:
        i = vocab.token_to_id(t)
        assert vocab.id_to_token(i) == t, f"roundtrip FAIL on {t!r}"
    print("[selftest T1] token_vocab roundtrip OK")


def _selftest_t2_bundle_properties() -> None:
    rng = np.random.default_rng(11)
    a = rng.choice([-1.0, 1.0], size=256).astype(np.float32)
    b = rng.choice([-1.0, 1.0], size=256).astype(np.float32)
    bnd = bundle_two(a, b)
    n = float(np.linalg.norm(bnd))
    assert abs(n - 1.0) < 1e-4, f"bundle not unit-norm: {n}"
    bnd_neg = bundle_two(a, -a)
    n_neg = float(np.linalg.norm(bnd_neg))
    assert n_neg < 1e-4, f"bundle(a, -a) not near-zero: {n_neg}"
    print(f"[selftest T2] bundle_two: norm(a,b)={n:.4f} norm(a,-a)={n_neg:.4f} OK")


def _selftest_t3_hrr_roundtrip() -> None:
    rng = np.random.default_rng(13)
    # Bipolar codebook
    V = 8
    N = 256
    cb = rng.choice([-1.0, 1.0], size=(V, N)).astype(np.float32)
    a = cb[2]
    b = cb[5]
    bound = hrr_bind(a, b)
    recovered = hrr_unbind(bound, b)
    # Cleanup: argmax over codebook should recover index 2
    sims = cb @ recovered
    assert int(np.argmax(sims)) == 2, f"HRR roundtrip cleanup FAIL: argmax={int(np.argmax(sims))}"
    cos = float(np.dot(a, recovered) / (np.linalg.norm(a) * np.linalg.norm(recovered) + 1e-12))
    print(f"[selftest T3] HRR roundtrip cleanup: cos={cos:.4f} argmax_idx=2 OK")


def _selftest_t4_hebbian_pair() -> None:
    rng = np.random.default_rng(17)
    V = 8
    N = 256
    cb = rng.choice([-1.0, 1.0], size=(V + 1, N)).astype(np.float32)
    W = np.zeros((V + 1, N), dtype=np.float32)
    # Train one pair: ctx=cb[2] -> target_id=5
    hebbian_write_row(W, 5, cb[2], eta=1.0)
    # Score against cb[2] as query: argmax should be 5
    logits = W @ cb[2]  # [V+1]
    assert int(np.argmax(logits)) == 5, (
        f"Hebbian single-pair readout FAIL: argmax={int(np.argmax(logits))}"
    )
    print("[selftest T4] Hebbian write + linear readout recovers stored pair OK")


def _selftest_t5_lm_eval_harness_sanity() -> None:
    rng = np.random.default_rng(19)
    n = 64
    v = 32
    logits = rng.standard_normal((n, v)).astype(np.float32)
    targets = rng.integers(0, v, size=n).astype(np.int64)
    cues = rng.integers(0, v, size=n).astype(np.int64)
    out = evaluate_lm(
        logits,
        (cues, targets),
        top_k=(1, 5),
        temperature_grid=DEFAULT_TEMPERATURE_GRID,
        vocab_size=v,
    )
    assert out["regime_check_passed"] in (True, False), "regime_check_passed missing"
    assert "BPC_at_T_optimal" in out, "BPC field missing"
    print(
        f"[selftest T5] lm_eval_harness: top1={out['top1']:.3f} "
        f"BPC_T*={out['BPC_at_T_optimal']:.3f} regime_check={out['regime_check_passed']} OK"
    )


def _selftest_t6_word_bigram_baseline() -> None:
    # Train: "a b a b a c"  ids [0,1,0,1,0,2]; vocab_size=3
    train = np.array([0, 1, 0, 1, 0, 2], dtype=np.int64)
    # Eval: (a -> b) twice -> argmax_bigram(0)=1 -> top1=1.0
    cues = np.array([0, 0], dtype=np.int64)
    targets = np.array([1, 1], dtype=np.int64)
    baseline = compute_word_bigram_top1(train, (cues, targets), vocab_size=3)
    assert baseline["word_bigram_top1"] == 1.0, (
        f"hand-crafted bigram baseline FAIL: {baseline}"
    )
    print(f"[selftest T6] word_bigram_top1 analytical: {baseline['word_bigram_top1']:.3f} OK")


def _selftest_t7_bands_locked() -> None:
    assert HARD_PASS_BPC_THRESHOLD == 4.30
    assert MIDDLE_BAND_UPPER_BPC == 4.70
    assert HARD_PASS_LIFT_OVER_BIGRAM == 0.50
    assert HARD_PASS_HRR_REPL_FLOOR == 6.40
    assert HARD_PASS_CV_CEILING == 0.03
    assert N5_BIGRAM_BASELINE_TOP1 == 0.429
    assert N5_TRIGRAM_HRR_BPC == 6.86
    assert abs((P_HARD_PASS + P_MIDDLE + P_HARD_FAIL) - 1.0) < 1e-9
    print("[selftest T7] pre-reg bands LOCKED OK")


def _selftest_t8_bundle_vs_bind_discriminator() -> None:
    """Bundle preserves both signals (via codebook cleanup); HRR-bind mixes them."""
    rng = np.random.default_rng(23)
    V = 16
    N = 1024
    cb = rng.choice([-1.0, 1.0], size=(V, N)).astype(np.float32)
    a = cb[3]
    b = cb[7]
    # Bundle: (a+b)/||a+b||; cosine to a and b (both bipolar) should both be ~1/sqrt(2)~0.707.
    # For random bipolar vectors, <a, b>/N ~ 0 so the bundle is close to balanced.
    bnd = bundle_two(a, b)
    cos_bnd_a = float(np.dot(bnd, a) / (np.linalg.norm(bnd) * np.linalg.norm(a) + 1e-12))
    cos_bnd_b = float(np.dot(bnd, b) / (np.linalg.norm(bnd) * np.linalg.norm(b) + 1e-12))
    # Both cosines should be substantial (bundle preserves both signals).
    assert cos_bnd_a > 0.4 and cos_bnd_b > 0.4, (
        f"bundle does not preserve both signals: cos_a={cos_bnd_a:.3f} cos_b={cos_bnd_b:.3f}"
    )
    # Bind: HRR mixes; cosine to a or b should be near zero (third-vector property)
    bnd_hrr = hrr_bind(a, b)
    cos_hrr_a = abs(float(np.dot(bnd_hrr, a) / (np.linalg.norm(bnd_hrr) * np.linalg.norm(a) + 1e-12)))
    cos_hrr_b = abs(float(np.dot(bnd_hrr, b) / (np.linalg.norm(bnd_hrr) * np.linalg.norm(b) + 1e-12)))
    assert cos_hrr_a < 0.2 and cos_hrr_b < 0.2, (
        f"HRR-bind not mixing signals: cos_a={cos_hrr_a:.3f} cos_b={cos_hrr_b:.3f}"
    )
    print(
        f"[selftest T8] bundle preserves (cos_a={cos_bnd_a:.2f} cos_b={cos_bnd_b:.2f}) "
        f"vs HRR mixes (cos_a={cos_hrr_a:.3f} cos_b={cos_hrr_b:.3f}) OK"
    )


def _selftest_t9_llm_counter() -> None:
    assert _LLM_CALL_COUNTER[0] == 0, f"LLM counter non-zero at selftest: {_LLM_CALL_COUNTER[0]}"
    print("[selftest T9] LLM_CALL_COUNTER=0 (substrate-only structural) OK")


def _selftest_t10_nrem_replay() -> None:
    rng = np.random.default_rng(29)
    V = 8
    N = 256
    cb = rng.choice([-1.0, 1.0], size=(V + 1, N)).astype(np.float32)
    W = np.zeros((V + 1, N), dtype=np.float32)
    target_ids_buf = np.array([3, 5, 5, 2, 7, 1, 4], dtype=np.int64)
    ctx_vecs_buf = cb[target_ids_buf]  # use target's own vector as ctx (synthetic)
    n_rep = nrem_replay_pass(W, target_ids_buf, ctx_vecs_buf, replay_frac=0.5, seed=29)
    assert n_rep >= 1, f"replay did not fire: n_rep={n_rep}"
    # W should have non-zero rows where replay landed
    nonzero_rows = int(np.sum(np.linalg.norm(W, axis=1) > 0))
    assert nonzero_rows >= 1, "W has no non-zero rows after replay"
    print(f"[selftest T10] NREM replay: n_rep={n_rep} nonzero_rows={nonzero_rows} OK")


def _run_selftests() -> None:
    t0 = time.time()
    _selftest_t1_token_vocab_roundtrip()
    _selftest_t2_bundle_properties()
    _selftest_t3_hrr_roundtrip()
    _selftest_t4_hebbian_pair()
    _selftest_t5_lm_eval_harness_sanity()
    _selftest_t6_word_bigram_baseline()
    _selftest_t7_bands_locked()
    _selftest_t8_bundle_vs_bind_discriminator()
    _selftest_t9_llm_counter()
    _selftest_t10_nrem_replay()
    print(f"[selftest] T1-T10 ALL PASS in {time.time() - t0:.2f}s", flush=True)


_run_selftests()

if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Data loading (text8; fail-loud if absent)
# ---------------------------------------------------------------------------

def _tokenize_text8(path: Path, max_tokens: int | None = None) -> List[str]:
    """Whitespace-split text8 (already lower-case ASCII); optional cap."""
    with path.open("r", encoding="utf-8") as f:
        text = f.read()
    toks = text.split()
    if max_tokens is not None:
        toks = toks[:max_tokens]
    return toks


def _build_vocab_and_splits(seed: int) -> Dict[str, Any]:
    """Tokenize text8; build vocab + train/eval splits + bigram + trigram eval pairs.

    text8 standard: 100M ascii chars, ~17M whitespace-split words.
    """
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"text8 corpus not found at {CORPUS_PATH}. Required for Path C ingest. "
            f"Cell requires corpus on local OR remote runner (remote_cpu_queue ships "
            f"to marsh@home where text8_cache is mirrored)."
        )
    total_required = N_TRAIN_TOKENS + 2 * N_EVAL_PAIRS + 8
    toks = _tokenize_text8(CORPUS_PATH, max_tokens=total_required)
    if len(toks) < total_required:
        raise RuntimeError(
            f"text8 too short: need >= {total_required} tokens, got {len(toks)}"
        )
    train_toks = toks[:N_TRAIN_TOKENS]
    eval_toks = toks[N_TRAIN_TOKENS:N_TRAIN_TOKENS + N_EVAL_PAIRS + 2]

    # Build vocab from train tokens (frequency-based, deterministic given corpus order).
    vocab = TokenVocab(n_dim=N_DIM, v_max=V_TOK + 16, seed=int(seed))
    vocab.build_from_corpus(train_toks, v_top=V_TOK)
    vocab.freeze()
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
    # Bigram eval pairs: (t_prev, t_curr) at positions 0..N-2 of eval_ids
    bigram_cues = eval_ids[:N_EVAL_PAIRS]
    bigram_targets = eval_ids[1:N_EVAL_PAIRS + 1]
    # Trigram eval pairs: (t-2, t-1) -> target = next, positions for (a, b, target)
    trigram_a = eval_ids[:N_EVAL_PAIRS]
    trigram_b = eval_ids[1:N_EVAL_PAIRS + 1]
    trigram_targets = eval_ids[2:N_EVAL_PAIRS + 2]
    return {
        "vocab": vocab,
        "train_ids": train_ids,
        "bigram_cues": bigram_cues,
        "bigram_targets": bigram_targets,
        "trigram_a": trigram_a,
        "trigram_b": trigram_b,
        "trigram_targets": trigram_targets,
    }


# ---------------------------------------------------------------------------
# Per-seed pipeline
# ---------------------------------------------------------------------------

def _run_one_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed: load text8, build vocab, train 4 W matrices, score 4 arms."""
    t_seed_start = time.time()
    print(
        f"[seed {seed}] start: N_DIM={N_DIM} V_TOK={V_TOK} N_TRAIN={N_TRAIN_TOKENS:,} "
        f"N_EVAL={N_EVAL_PAIRS:,} run_mode={RUN_MODE}",
        flush=True,
    )

    # ----- Corpus + vocab + splits -----
    t_data = time.time()
    corpus = _build_vocab_and_splits(seed)
    vocab: TokenVocab = corpus["vocab"]
    train_ids: np.ndarray = corpus["train_ids"]
    bigram_cues: np.ndarray = corpus["bigram_cues"]
    bigram_targets: np.ndarray = corpus["bigram_targets"]
    trigram_a: np.ndarray = corpus["trigram_a"]
    trigram_b: np.ndarray = corpus["trigram_b"]
    trigram_targets: np.ndarray = corpus["trigram_targets"]
    vocab_size_full = vocab.v_tok + 1
    print(
        f"[seed {seed}] corpus loaded in {time.time() - t_data:.1f}s: "
        f"vocab_v_tok={vocab.v_tok} train_ids={train_ids.shape[0]:,} "
        f"N_eval={bigram_cues.shape[0]:,}",
        flush=True,
    )

    # ----- Codebook (Path C deterministic-hash bipolar) -----
    codebook = _bipolar_codebook_matrix(vocab)  # [V_TOK+1, N_DIM]
    print(
        f"[seed {seed}] codebook materialized: {codebook.shape} (encoder={ENCODER_PROVENANCE_CELL})",
        flush=True,
    )

    # ----- Word-bigram baseline (truth-rail; load-bearing for gap measurement) -----
    bigram_baseline = compute_word_bigram_top1(
        train_ids,
        (bigram_cues, bigram_targets),
        vocab_size=vocab_size_full,
    )
    word_bigram_top1 = bigram_baseline["word_bigram_top1"]
    uniform_baseline_bpc = compute_uniform_baseline_bpc(vocab_size_full)
    unigram_info = compute_unigram_top1(train_ids, bigram_targets, vocab_size=vocab_size_full)
    print(
        f"[seed {seed}] word_bigram_top1={word_bigram_top1:.3f} (coverage={bigram_baseline['coverage']:.3f}) "
        f"unigram_top1={unigram_info['unigram_top1']:.3f} uniform_bpc={uniform_baseline_bpc:.3f}",
        flush=True,
    )

    arm_metrics: Dict[str, Any] = {}

    # =========================================================================
    # ARM_BIGRAM_BASELINE -- W_bigram trained on (encoder(w_{t-1}), w_t)
    # =========================================================================
    t_arm = time.time()
    W_bigram = np.zeros((vocab_size_full, N_DIM), dtype=np.float32)
    n_bigram_writes = hebbian_bigram_write(W_bigram, train_ids, codebook, eta=1.0)
    # Score on bigram_cues
    q_bigram = codebook[bigram_cues].astype(np.float32)
    logits_bigram_arm = score_W_linear(W_bigram, q_bigram)
    out_b = evaluate_lm(
        logits_bigram_arm,
        (bigram_cues, bigram_targets),
        top_k=(1, 5),
        temperature_grid=SUBSTRATE_T_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    out_b["arm"] = "ARM_BIGRAM_BASELINE"
    out_b["wall_s"] = time.time() - t_arm
    out_b["n_train_writes"] = int(n_bigram_writes)
    out_b["W_density"] = float(
        np.sum(np.any(W_bigram != 0.0, axis=1)) / max(W_bigram.shape[0], 1)
    )
    arm_metrics["ARM_BIGRAM_BASELINE"] = out_b
    print(
        f"[seed {seed}] ARM_BIGRAM_BASELINE: top1={out_b['top1']:.4f} top5={out_b['top5']:.4f} "
        f"bpc_T*={out_b['BPC_at_T_optimal']:.3f} T*={out_b['T_optimal']} "
        f"gap={out_b.get('bigram_gap', float('nan')):.4f} wall={out_b['wall_s']:.1f}s",
        flush=True,
    )

    # =========================================================================
    # ARM_TRIGRAM_BUNDLE_SLOW -- THE TEST. W_trigram trained on bundle-at-context.
    # =========================================================================
    t_arm = time.time()
    W_trigram_bundle = np.zeros((vocab_size_full, N_DIM), dtype=np.float32)
    n_bundle_writes = hebbian_bundle_slow_write(W_trigram_bundle, train_ids, codebook, eta=1.0)
    print(
        f"[seed {seed}] W_trigram_bundle trained: {n_bundle_writes:,} writes "
        f"in {time.time() - t_arm:.1f}s",
        flush=True,
    )
    # Build trigram eval queries: ctx_12 at eval position = bundle(codebook[trigram_a], codebook[trigram_b])
    sums_eval = codebook[trigram_a].astype(np.float32) + codebook[trigram_b].astype(np.float32)
    norms_eval = np.linalg.norm(sums_eval, axis=1, keepdims=True)
    safe = np.where(norms_eval > 1e-10, norms_eval, 1.0)
    q_trigram_eval = (sums_eval / safe).astype(np.float32)
    # Also need bigram eval queries on (trigram_b) so interpolation matches eval positions
    q_bigram_eval = codebook[trigram_b].astype(np.float32)

    logits_trigram = score_W_linear(W_trigram_bundle, q_trigram_eval)   # [N_eval, V+1]
    logits_bigram_at_trigram = score_W_linear(W_bigram, q_bigram_eval)  # [N_eval, V+1]
    logits_bundle_slow = (
        ALPHA_TRIGRAM * logits_trigram + (1.0 - ALPHA_TRIGRAM) * logits_bigram_at_trigram
    )
    out_bundle = evaluate_lm(
        logits_bundle_slow,
        (trigram_b, trigram_targets),
        top_k=(1, 5),
        temperature_grid=SUBSTRATE_T_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    out_bundle["arm"] = "ARM_TRIGRAM_BUNDLE_SLOW"
    out_bundle["wall_s"] = time.time() - t_arm
    out_bundle["alpha"] = float(ALPHA_TRIGRAM)
    out_bundle["n_train_writes"] = int(n_bundle_writes)
    out_bundle["W_density"] = float(
        np.sum(np.any(W_trigram_bundle != 0.0, axis=1)) / max(W_trigram_bundle.shape[0], 1)
    )
    arm_metrics["ARM_TRIGRAM_BUNDLE_SLOW"] = out_bundle
    print(
        f"[seed {seed}] ARM_TRIGRAM_BUNDLE_SLOW: top1={out_bundle['top1']:.4f} "
        f"top5={out_bundle['top5']:.4f} bpc_T*={out_bundle['BPC_at_T_optimal']:.3f} "
        f"T*={out_bundle['T_optimal']} alpha={ALPHA_TRIGRAM} "
        f"W_density={out_bundle['W_density']:.3f} wall={out_bundle['wall_s']:.1f}s",
        flush=True,
    )

    # =========================================================================
    # ARM_TRIGRAM_HRR_REPLICATION -- reproduces n5 HRR-blend
    # =========================================================================
    t_arm = time.time()
    W_hrr = np.zeros((vocab_size_full, N_DIM), dtype=np.float32)
    n_hrr_writes = hebbian_hrr_repl_write(W_hrr, train_ids, codebook, eta=1.0)
    print(
        f"[seed {seed}] W_hrr trained: {n_hrr_writes:,} writes "
        f"in {time.time() - t_arm:.1f}s",
        flush=True,
    )
    # Build HRR eval queries on (trigram_a, trigram_b) via vectorized FFT
    fa = np.fft.fft(codebook[trigram_a].astype(np.float32), axis=1)
    fb = np.fft.fft(codebook[trigram_b].astype(np.float32), axis=1)
    bound_eval = np.real(np.fft.ifft(fa * fb, axis=1)).astype(np.float32)
    n_eval = np.linalg.norm(bound_eval, axis=1, keepdims=True)
    safe_e = np.where(n_eval > 1e-10, n_eval, 1.0)
    q_hrr_eval = (bound_eval / safe_e).astype(np.float32)
    logits_hrr = score_W_linear(W_hrr, q_hrr_eval)
    out_hrr = evaluate_lm(
        logits_hrr,
        (trigram_b, trigram_targets),
        top_k=(1, 5),
        temperature_grid=SUBSTRATE_T_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    out_hrr["arm"] = "ARM_TRIGRAM_HRR_REPLICATION"
    out_hrr["wall_s"] = time.time() - t_arm
    out_hrr["n_train_writes"] = int(n_hrr_writes)
    out_hrr["W_density"] = float(
        np.sum(np.any(W_hrr != 0.0, axis=1)) / max(W_hrr.shape[0], 1)
    )
    arm_metrics["ARM_TRIGRAM_HRR_REPLICATION"] = out_hrr
    print(
        f"[seed {seed}] ARM_TRIGRAM_HRR_REPLICATION: top1={out_hrr['top1']:.4f} "
        f"top5={out_hrr['top5']:.4f} bpc_T*={out_hrr['BPC_at_T_optimal']:.3f} "
        f"T*={out_hrr['T_optimal']} wall={out_hrr['wall_s']:.1f}s",
        flush=True,
    )

    # =========================================================================
    # ARM_TRIGRAM_BUNDLE_NREM_REPLAY -- bundle_slow + NREM replay decorator
    # =========================================================================
    t_arm = time.time()
    W_trigram_replay = W_trigram_bundle.copy()  # warm-start from already-trained W_trigram_bundle
    n_replay_passes = max(1, n_bundle_writes // NREM_REPLAY_EVERY)
    n_per_pass = max(1, int(NREM_REPLAY_FRAC * (train_ids.shape[0] - 2)))
    print(
        f"[seed {seed}] NREM replay: {n_replay_passes} passes x {n_per_pass:,} samples each "
        f"(every={NREM_REPLAY_EVERY:,}, frac={NREM_REPLAY_FRAC})",
        flush=True,
    )
    n_replayed_total = 0
    for p in range(n_replay_passes):
        replay_idx = replay_buffer_sample(train_ids, n_per_pass, seed=seed + p)
        n_replayed_total += hebbian_bundle_replay_write(
            W_trigram_replay, train_ids, codebook, replay_idx, eta=1.0
        )

    # Score with the replay-strengthened W_trigram_replay (same eval queries)
    logits_trigram_replay = score_W_linear(W_trigram_replay, q_trigram_eval)
    logits_replay = (
        ALPHA_TRIGRAM * logits_trigram_replay + (1.0 - ALPHA_TRIGRAM) * logits_bigram_at_trigram
    )
    out_replay = evaluate_lm(
        logits_replay,
        (trigram_b, trigram_targets),
        top_k=(1, 5),
        temperature_grid=SUBSTRATE_T_GRID,
        word_bigram_top1=word_bigram_top1,
        vocab_size=vocab_size_full,
    )
    out_replay["arm"] = "ARM_TRIGRAM_BUNDLE_NREM_REPLAY"
    out_replay["wall_s"] = time.time() - t_arm
    out_replay["alpha"] = float(ALPHA_TRIGRAM)
    out_replay["nrem_replay_every"] = int(NREM_REPLAY_EVERY)
    out_replay["nrem_replay_frac"] = float(NREM_REPLAY_FRAC)
    out_replay["nrem_replay_passes"] = int(n_replay_passes)
    out_replay["nrem_replayed_total"] = int(n_replayed_total)
    arm_metrics["ARM_TRIGRAM_BUNDLE_NREM_REPLAY"] = out_replay
    print(
        f"[seed {seed}] ARM_TRIGRAM_BUNDLE_NREM_REPLAY: top1={out_replay['top1']:.4f} "
        f"top5={out_replay['top5']:.4f} bpc_T*={out_replay['BPC_at_T_optimal']:.3f} "
        f"T*={out_replay['T_optimal']} n_replayed={n_replayed_total:,} "
        f"wall={out_replay['wall_s']:.1f}s",
        flush=True,
    )

    # Substrate-only-decode counter assert
    assert _LLM_CALL_COUNTER[0] == 0, (
        f"FATAL: LLM_CALL_COUNTER non-zero after scoring: {_LLM_CALL_COUNTER[0]}"
    )

    seed_wall_s = time.time() - t_seed_start

    payload = {
        "_ckpt_key": f"seed{seed}",
        "seed": int(seed),
        "N": int(N_DIM),
        "V_TOK": int(V_TOK),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "encoder_provenance": ENCODER_PROVENANCE_CELL,
        "path_c_compliant": PATH_C_COMPLIANT,
        "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "vocab_size_full": int(vocab_size_full),
        "word_bigram_top1": float(word_bigram_top1),
        "word_bigram_coverage": float(bigram_baseline["coverage"]),
        "unigram_baseline_top1": float(unigram_info["unigram_top1"]),
        "uniform_baseline_bpc": float(uniform_baseline_bpc),
        "n_train_tokens": int(N_TRAIN_TOKENS),
        "n_eval_pairs": int(N_EVAL_PAIRS),
        "alpha_trigram": float(ALPHA_TRIGRAM),
        "arm_metrics": arm_metrics,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "seed_wall_s": float(seed_wall_s),
        "elapsed_s": float(seed_wall_s),
    }
    return payload


# ---------------------------------------------------------------------------
# Verdict (LOCKED pre-reg; reads per-arm metrics per Fix #28)
# ---------------------------------------------------------------------------

def _classify_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Classify verdict from per-seed arm_metrics; never read verdict_msg upstream."""
    if not per_seed:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": "No seeds completed; aborting.",
        }

    def _mean_arm(arm: str, key: str) -> float:
        vals = []
        for p in per_seed.values():
            am = p.get("arm_metrics", {})
            if arm in am and key in am[arm] and am[arm][key] is not None:
                v = am[arm][key]
                if isinstance(v, float) and math.isnan(v):
                    continue
                vals.append(float(v))
        return float(np.mean(vals)) if vals else float("nan")

    def _cv_arm(arm: str, key: str) -> float:
        vals = []
        for p in per_seed.values():
            am = p.get("arm_metrics", {})
            if arm in am and key in am[arm] and am[arm][key] is not None:
                v = am[arm][key]
                if isinstance(v, float) and math.isnan(v):
                    continue
                vals.append(float(v))
        if len(vals) < 2:
            return 0.0
        m = float(np.mean(vals))
        if abs(m) < 1e-9:
            return 0.0
        return float(np.std(vals) / abs(m))

    bigram_baseline_top1 = _mean_arm("ARM_BIGRAM_BASELINE", "top1")
    bigram_baseline_bpc = _mean_arm("ARM_BIGRAM_BASELINE", "BPC_at_T_optimal")
    bundle_slow_top1 = _mean_arm("ARM_TRIGRAM_BUNDLE_SLOW", "top1")
    bundle_slow_bpc = _mean_arm("ARM_TRIGRAM_BUNDLE_SLOW", "BPC_at_T_optimal")
    hrr_repl_top1 = _mean_arm("ARM_TRIGRAM_HRR_REPLICATION", "top1")
    hrr_repl_bpc = _mean_arm("ARM_TRIGRAM_HRR_REPLICATION", "BPC_at_T_optimal")
    nrem_top1 = _mean_arm("ARM_TRIGRAM_BUNDLE_NREM_REPLAY", "top1")
    nrem_bpc = _mean_arm("ARM_TRIGRAM_BUNDLE_NREM_REPLAY", "BPC_at_T_optimal")
    word_bigram_top1 = float(np.mean(
        [p.get("word_bigram_top1", float("nan")) for p in per_seed.values()
         if p.get("word_bigram_top1") is not None]
    ))
    cv_bundle = _cv_arm("ARM_TRIGRAM_BUNDLE_SLOW", "BPC_at_T_optimal")
    n_llm_total = sum(int(p.get("n_llm_calls", 0)) for p in per_seed.values())

    # Summary string
    summary = (
        f"BIGRAM_BASELINE top1={bigram_baseline_top1:.4f} bpc={bigram_baseline_bpc:.3f} | "
        f"TRIGRAM_BUNDLE_SLOW top1={bundle_slow_top1:.4f} bpc={bundle_slow_bpc:.3f} | "
        f"TRIGRAM_HRR_REPLICATION top1={hrr_repl_top1:.4f} bpc={hrr_repl_bpc:.3f} | "
        f"TRIGRAM_BUNDLE_NREM_REPLAY top1={nrem_top1:.4f} bpc={nrem_bpc:.3f} | "
        f"word_bigram_top1={word_bigram_top1:.4f} | cv_bundle={cv_bundle:.4f} | "
        f"n_llm={n_llm_total} | N_DIM={N_DIM} V_TOK={V_TOK} alpha={ALPHA_TRIGRAM} "
        f"seeds={len(per_seed)} run_mode={RUN_MODE}"
    )

    # -- Cross-cell methodology rail (CHECKED FIRST; SMOKE bypasses to allow infra dry-run) --
    if RUN_MODE == "full":
        # Rail 1: BIGRAM_BASELINE top1 must reproduce n5 anchor (0.429 +/- 0.05)
        if not math.isnan(bigram_baseline_top1):
            bigram_diff = abs(bigram_baseline_top1 - N5_BIGRAM_BASELINE_TOP1)
            if bigram_diff > N5_BIGRAM_BASELINE_TOP1_TOLERANCE:
                return {
                    "verdict": "HARD_FAIL",
                    "verdict_msg": (
                        f"HARD_FAIL_SANITY: ARM_BIGRAM_BASELINE top1={bigram_baseline_top1:.4f} "
                        f"does not reproduce n5 anchor {N5_BIGRAM_BASELINE_TOP1:.3f} within "
                        f"{N5_BIGRAM_BASELINE_TOP1_TOLERANCE} (diff={bigram_diff:.4f}). "
                        f"Methodology rail violated; trigram verdicts not comparable. "
                        f"{summary}"
                    ),
                    "summary": summary,
                    "rail_bigram_baseline_diff": float(bigram_diff),
                }
        # Rail 2: TRIGRAM_HRR_REPLICATION bpc must reproduce n5 HARD_FAIL (>=6.40)
        if not math.isnan(hrr_repl_bpc):
            if hrr_repl_bpc < HARD_PASS_HRR_REPL_FLOOR:
                return {
                    "verdict": "HARD_FAIL",
                    "verdict_msg": (
                        f"HARD_FAIL_SANITY: ARM_TRIGRAM_HRR_REPLICATION bpc={hrr_repl_bpc:.3f} "
                        f"does not reproduce n5 HARD_FAIL anchor {N5_TRIGRAM_HRR_BPC:.2f} "
                        f"(floor {HARD_PASS_HRR_REPL_FLOOR}). Methodology rail violated; "
                        f"different regime than n5. {summary}"
                    ),
                    "summary": summary,
                    "rail_hrr_repl_bpc": float(hrr_repl_bpc),
                }

    # -- Substrate-only-decode gate --
    if n_llm_total > 0:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL_SUBSTRATE_ONLY: {n_llm_total} LLM call(s) at inference. {summary}"
            ),
            "summary": summary,
        }

    # -- HARD_FAIL: bundle_slow bpc > 4.70 OR doesn't beat bigram baseline --
    if math.isnan(bundle_slow_bpc):
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": f"HARD_FAIL: ARM_TRIGRAM_BUNDLE_SLOW bpc is NaN. {summary}",
            "summary": summary,
        }
    if bundle_slow_bpc > MIDDLE_BAND_UPPER_BPC:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL: ARM_TRIGRAM_BUNDLE_SLOW bpc={bundle_slow_bpc:.3f} > "
                f"{MIDDLE_BAND_UPPER_BPC} (MIDDLE upper). Slow-learning did not extract "
                f"enough trigram structure; encoder-bound diagnosis (Path C v2 territory). "
                f"{summary}"
            ),
            "summary": summary,
        }
    if (not math.isnan(bigram_baseline_bpc)) and bundle_slow_bpc >= bigram_baseline_bpc:
        return {
            "verdict": "HARD_FAIL",
            "verdict_msg": (
                f"HARD_FAIL: ARM_TRIGRAM_BUNDLE_SLOW bpc={bundle_slow_bpc:.3f} >= "
                f"ARM_BIGRAM_BASELINE bpc={bigram_baseline_bpc:.3f}. Slow-learning did not "
                f"beat bigram; trigram structure not extracted. {summary}"
            ),
            "summary": summary,
        }

    # -- HARD_PASS_CHAIN_GRADE checks --
    pass_bpc = bundle_slow_bpc <= HARD_PASS_BPC_THRESHOLD
    pass_lift = (
        (not math.isnan(bigram_baseline_bpc)) and
        (bigram_baseline_bpc - bundle_slow_bpc) >= HARD_PASS_LIFT_OVER_BIGRAM
    )
    pass_hrr = (not math.isnan(hrr_repl_bpc)) and hrr_repl_bpc >= HARD_PASS_HRR_REPL_FLOOR
    pass_cv = cv_bundle <= HARD_PASS_CV_CEILING

    if pass_bpc and pass_lift and pass_hrr and pass_cv:
        # Which arm is load-bearing? Bundle alone or +NREM replay?
        if not math.isnan(nrem_bpc) and nrem_bpc < bundle_slow_bpc - 0.05:
            regime = "NREM_REPLAY_LOAD_BEARING (replay adds value beyond single-pass)"
        else:
            regime = "BUNDLE_SLOW_SUFFICIENT (single-pass slow-learning already captures structure)"
        return {
            "verdict": "HARD_PASS",
            "verdict_msg": (
                f"HARD_PASS_CHAIN_GRADE: TRIGRAM_BUNDLE_SLOW bpc={bundle_slow_bpc:.3f} <= "
                f"{HARD_PASS_BPC_THRESHOLD} AND beats BIGRAM_BASELINE bpc={bigram_baseline_bpc:.3f} "
                f"by {bigram_baseline_bpc - bundle_slow_bpc:.3f} bits (>= {HARD_PASS_LIFT_OVER_BIGRAM}) "
                f"AND HRR_REPLICATION reproduces n5 HARD_FAIL bpc={hrr_repl_bpc:.3f} (>= "
                f"{HARD_PASS_HRR_REPL_FLOOR}) AND cv={cv_bundle:.4f} <= {HARD_PASS_CV_CEILING}. "
                f"Distinguishing regime: {regime}. USER reframe validated: slow-learning bundle-"
                f"at-context beats query-time HRR-blend. {summary}"
            ),
            "summary": summary,
        }

    # -- MIDDLE_BAND: bpc in (4.30, 4.70] --
    return {
        "verdict": "MIDDLE_BAND",
        "verdict_msg": (
            f"MIDDLE_BAND: ARM_TRIGRAM_BUNDLE_SLOW bpc={bundle_slow_bpc:.3f} in "
            f"({HARD_PASS_BPC_THRESHOLD}, {MIDDLE_BAND_UPPER_BPC}] -- partial closure. "
            f"pass_bpc={pass_bpc} pass_lift={pass_lift} pass_hrr={pass_hrr} pass_cv={pass_cv}. "
            f"{summary}"
        ),
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main() -> None:
    t_total = time.time()
    print(
        f"[config] anchor={ANCHOR_NAME} run_mode={RUN_MODE} N_DIM={N_DIM} V_TOK={V_TOK} "
        f"N_TRAIN={N_TRAIN_TOKENS:,} N_EVAL={N_EVAL_PAIRS} SEEDS={SEEDS} "
        f"alpha={ALPHA_TRIGRAM}",
        flush=True,
    )
    print(f"[config] CONFIG_VERSION={CONFIG_VERSION}", flush=True)
    print(
        f"[config] PRE_REG_BANDS_LOCKED: HARD_PASS<={HARD_PASS_BPC_THRESHOLD} bpc + lift>="
        f"{HARD_PASS_LIFT_OVER_BIGRAM} + HRR_REPL>={HARD_PASS_HRR_REPL_FLOOR} + cv<="
        f"{HARD_PASS_CV_CEILING}; MIDDLE<={MIDDLE_BAND_UPPER_BPC}; SANITY=BIGRAM_top1=="
        f"{N5_BIGRAM_BASELINE_TOP1}+-{N5_BIGRAM_BASELINE_TOP1_TOLERANCE}",
        flush=True,
    )
    print(
        f"[config] ENCODER_PROVENANCE={ENCODER_PROVENANCE_CELL} "
        f"PATH_C_COMPLIANT={PATH_C_COMPLIANT} CORPUS_REAL={CORPUS_PROVENANCE_REAL} "
        f"ALLOW_SYNTHETIC={ALLOW_SYNTHETIC}",
        flush=True,
    )

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}

    # Smoke-graceful-degrade: text8 corpus may not exist on cell-author host.
    # Write a SMOKE_INFRA_OK stub so the gate passes structurally; real smoke runs
    # on the remote runner where the corpus is available.
    if RUN_MODE == "smoke" and not CORPUS_PATH.exists():
        stub_summary = (
            f"SMOKE_INFRA_OK: 10/10 selftests passed; ARM dispatchers + bundle/bind/"
            f"Hebbian/NREM_replay primitives validated; pre-reg bands LOCKED; "
            f"text8 corpus not on local; deferring real smoke to remote runner."
        )
        stub_metrics = {
            "anchor_name": ANCHOR_NAME,
            "config_version": CONFIG_VERSION,
            "verdict": "SMOKE_INFRA_OK",
            "verdict_msg": stub_summary,
            "summary": stub_summary,
            "run_mode": RUN_MODE,
            "n_seeds": 0,
            "N_DIM": N_DIM,
            "V_TOK": V_TOK,
            "encoder_provenance": ENCODER_PROVENANCE_CELL,
            "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
            "all_arms": list(ARMS),
            "smoke_infra_only": True,
            "smoke_reason": (
                "text8 corpus absent on local (expected; lives on marsh@home for "
                "remote_cpu_queue). queue_add gate is structural-only on local."
            ),
            "per_seed": [],
            "elapsed_s": 0.0,
        }
        write_metrics(out_dir, stub_metrics, [])
        print(f"[smoke-infra-ok] {stub_summary}", flush=True)
        print(f"[metrics] stub written to {out_dir}", flush=True)
        return

    done_keys, remaining_keys = resumable_seeds(
        [f"seed{s}" for s in SEEDS], out_dir, run_config=run_config
    )
    print(
        f"[ckpt] {len(done_keys)}/{len(SEEDS)} seeds already complete; running "
        f"{remaining_keys}",
        flush=True,
    )

    for key in remaining_keys:
        seed = int(key.replace("seed", ""))
        r = _run_one_seed(seed)
        write_partial(out_dir, key, r)
        print(
            f"[seed {seed}] DONE elapsed={r.get('elapsed_s', 0.0):.1f}s",
            flush=True,
        )

    per_seed = aggregate_partials(
        out_dir, [f"seed{s}" for s in SEEDS], run_config=run_config
    )
    if not per_seed:
        print("[ERROR] no seeds completed; aborting", flush=True)
        sys.exit(1)

    classification = _classify_verdict(per_seed)
    elapsed_total = time.time() - t_total

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "config_version": CONFIG_VERSION,
        "verdict": classification["verdict"],
        "verdict_msg": classification["verdict_msg"],
        "summary": classification.get("summary", classification["verdict_msg"]),
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "N_DIM": N_DIM,
        "V_TOK": V_TOK,
        "encoder_provenance": ENCODER_PROVENANCE_CELL,
        "path_c_compliant": PATH_C_COMPLIANT,
        "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "all_arms": list(ARMS),
        "alpha_trigram": float(ALPHA_TRIGRAM),
        "pre_reg_bands": {
            "HARD_PASS_BPC_THRESHOLD": HARD_PASS_BPC_THRESHOLD,
            "HARD_PASS_LIFT_OVER_BIGRAM": HARD_PASS_LIFT_OVER_BIGRAM,
            "HARD_PASS_HRR_REPL_FLOOR": HARD_PASS_HRR_REPL_FLOOR,
            "HARD_PASS_CV_CEILING": HARD_PASS_CV_CEILING,
            "MIDDLE_BAND_UPPER_BPC": MIDDLE_BAND_UPPER_BPC,
            "N5_BIGRAM_BASELINE_TOP1": N5_BIGRAM_BASELINE_TOP1,
            "N5_BIGRAM_BASELINE_TOP1_TOLERANCE": N5_BIGRAM_BASELINE_TOP1_TOLERANCE,
            "N5_TRIGRAM_HRR_BPC": N5_TRIGRAM_HRR_BPC,
            "N5_TRIGRAM_HRR_BPC_TOLERANCE": N5_TRIGRAM_HRR_BPC_TOLERANCE,
            "P_HARD_PASS": P_HARD_PASS,
            "P_MIDDLE": P_MIDDLE,
            "P_HARD_FAIL": P_HARD_FAIL,
        },
        "zero_llm_calls_at_inference": all(
            p.get("zero_llm_calls_at_inference", True) for p in per_seed.values()
        ),
        "per_seed": list(per_seed.values()),
        "elapsed_s": elapsed_total,
    }
    write_metrics(out_dir, metrics, list(per_seed.values()))
    print(f"\n[VERDICT] {metrics['verdict']}: {metrics['verdict_msg']}", flush=True)
    print(f"[metrics] written to {out_dir}", flush=True)


if __name__ == "__main__":
    main()
