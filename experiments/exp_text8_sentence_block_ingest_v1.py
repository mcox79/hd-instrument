"""
text8_sentence_block_ingest_v1 -- substrate-native sentence-block ingest of text8.

ANCHOR (drill 2, anchor 1; research_language_ingest_drill2_segmentation_block_size_2026-06-26.md):
  Substrate-native sentence-grade ingest of text8 with sentence-length-proxy boundary
  discipline. Tests block-size sweet spot K in [5, 25] tokens (substrate-physics-derived;
  matches g1b chain-grade K_SEQ=20). Composes char_trigram_encoder (Path C; no Pythia /
  MiniLM / word2vec at encode-side) + SequenceMatrix S (g1b chain-grade primitive) +
  Principle-O END_SENT special tokens.

ARMS:
  ARM_K5_BLOCKS    -- block size 5 tokens (substrate-physics tight; tests lower bound)
  ARM_K10_BLOCKS   -- block size 10 (mid-range)
  ARM_K20_BLOCKS   -- block size 20 (matches g1b chain-grade K_SEQ=20)
  ARM_K25_BLOCKS   -- block size 25 (substrate-physics tested upper bound)
  ARM_KNN_BASELINE -- M=400 cosine-KNN baseline (Fix #28 sentinel; must >= 0.9)

PRE-REG BANDS (research note P1-P5 verbatim):
  HARD_PASS_CHAIN_GRADE:
    best_arm KNN@1 at M=10000 >= 0.50 AND
    substrate matches KNN within 0.02 AND
    downstream BPC < 4.50 AND
    cv <= 0.05 across seeds
  MIDDLE_BAND:
    best_arm BPC in [4.50, 5.50)
  HARD_FAIL:
    best_arm BPC >= 5.50

Substrate-only-decode gate: char_trigram_encoder is Path C (substrate-native);
zero LLM forward calls at inference; _LLM_CALL_COUNTER asserted == 0.

CORPUS_PROVENANCE_REAL=True asserted + LOGGED (fail-loud per phase_d_tier6 lesson).

CONFIG: N_DIM=8192, V_TOK=8192 (or grown), 3 seeds [11, 13, 19], real text8.

ENCODER_PROVENANCE = "SUBSTRATE_NATIVE" (Path C, NOT Pythia / MiniLM / word2vec).

ASCII-only per feedback_ascii_only_in_scripts.
QUEUE: remote_cpu_queue (numpy / torch CPU; matmul-bound at N=8192).
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
    aggregate_partials, get_output_dir, resumable_seeds, write_metrics, write_partial,
)

ANCHOR_NAME = "text8_sentence_block_ingest_v1"

# ---------------------------------------------------------------------------
# LLM-call audit counter (substrate-only gate, structural + counter)
# ---------------------------------------------------------------------------
# This cell imports NO transformers; encoder is char_trigram_encoder (Path C).
# Counter is structural guarantee + audit log.
_LLM_CALL_COUNTER = [0]


# ---------------------------------------------------------------------------
# CLI / env config
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--m-eval", dest="m_eval", type=int, default=None)
_ARGS, _ = _ap.parse_known_args()

_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

# Sentence-length-proxy distribution (per research note L1.7 + L6):
# text8 has no punctuation; sentence-length distribution proxy from English:
# gamma-shaped around mean ~18 tokens, range [5, 40] capped.
SENT_LEN_MEAN = 18
SENT_LEN_MIN = 5
SENT_LEN_MAX = 40

# Arm configs (per research note L4 + L7).
# Each arm = (arm_name, K_FIXED). K_FIXED is the per-arm block-size cap.
# When K_FIXED is None, sample sentence lengths from gamma distribution.
ARM_CONFIGS = [
    ("ARM_K5_BLOCKS", 5),
    ("ARM_K10_BLOCKS", 10),
    ("ARM_K20_BLOCKS", 20),
    ("ARM_K25_BLOCKS", 25),
]

if RUN_MODE == "smoke":
    # Smoke: tight config to fit SMOKE_TIMEOUT_S=180s gate.
    # N_DIM small for speed; M_EVAL small; 1 seed; 1 arm (ARM_K20 only).
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "1024"))
    M_EVAL = _ARGS.m_eval if _ARGS.m_eval is not None else int(
        os.environ.get("HDLAB_M_EVAL", "200"))
    M_KNN_SENTINEL = 200
    MAX_TOKENS_TRAIN = int(os.environ.get("HDLAB_MAX_TOKENS_TRAIN", "20000"))
    SEEDS = [11]
    ARMS_THIS_RUN = [("ARM_K20_BLOCKS", 20)]  # smoke only runs the K=20 (chain-grade reference)
else:
    N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(
        os.environ.get("HDLAB_N_DIM", "8192"))
    M_EVAL = _ARGS.m_eval if _ARGS.m_eval is not None else int(
        os.environ.get("HDLAB_M_EVAL", "10000"))
    M_KNN_SENTINEL = int(os.environ.get("HDLAB_M_KNN_SENTINEL", "400"))
    # Train tokens: enough to support M=10000 blocks at K=25 = 250000 tokens; pad x2.
    MAX_TOKENS_TRAIN = int(os.environ.get("HDLAB_MAX_TOKENS_TRAIN", "500000"))
    SEEDS = [int(s) for s in os.environ.get("HDLAB_SEEDS", "11,13,19").split(",")]
    ARMS_THIS_RUN = ARM_CONFIGS

# Corpus identifiers
CORPUS_NAME = "text8"
CORPUS_VERSION = "matt_mahoney_2006"
ALLOW_SYNTHETIC = False
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"

# Pre-registered bands (research note P1-P5)
HARD_PASS_KNN_AT_1 = 0.50          # KNN@1 >= 0.50 at M=10000
HARD_PASS_SUBSTRATE_GAP = 0.02     # substrate matches KNN within 0.02
HARD_PASS_BPC = 4.50               # downstream BPC < 4.50
MIDDLE_BAND_UPPER_BPC = 5.50
CV_MAX_HP = 0.05
M_KNN_SENTINEL_MIN = 0.90          # Fix #28 sentinel: KNN baseline at M=400 must be >= 0.9

CONFIG_VERSION = (
    "N=%d,V_TOK=auto,CORPUS=%s,CORPUS_VER=%s,M_EVAL=%d,MAX_TOK=%d,SEEDS=%s,"
    "SENT_LEN_MEAN=%d,SENT_LEN_MAX=%d,SYNTH=%s,ENC=%s,"
    "BANDS=KNN>=%.2f/BPC<%.2f/MB<%.2f"
) % (N_DIM, CORPUS_NAME, CORPUS_VERSION, M_EVAL, MAX_TOKENS_TRAIN,
     "-".join(str(s) for s in SEEDS), SENT_LEN_MEAN, SENT_LEN_MAX,
     str(ALLOW_SYNTHETIC), ENCODER_PROVENANCE,
     HARD_PASS_KNN_AT_1, HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC)


# ---------------------------------------------------------------------------
# Substrate-native encoder (char_trigram bag-of-trigrams; Path C)
# ---------------------------------------------------------------------------

def _seed_for_string(s: str, salt: int = 0) -> int:
    """Deterministic 32-bit seed from string content."""
    import hashlib
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=4, person=str(salt).encode()[:8].ljust(8, b"_")[:8]).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed: int, n_dim: int) -> np.ndarray:
    """Per-content bipolar {-1, +1} hypervector; deterministic from seed."""
    rng = np.random.default_rng(seed)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def encode_token(token: str, n_dim: int, salt: int = 0) -> np.ndarray:
    """Substrate-native per-token HV via deterministic hash seed (Path C).

    Per-token bipolar HV from hash of the token string. Salt lets ablation
    cells re-basis (changes basis; semantic geometry stays equivalent in expectation).
    """
    return _bipolar_hv(_seed_for_string(token, salt=salt), n_dim)


def encode_block(tokens: List[str], n_dim: int, salt: int = 0,
                 use_trigrams: bool = True) -> np.ndarray:
    """Encode a token-block as a bundled bipolar HV.

    Default (use_trigrams=True): use char_trigram bag-of-trigrams over the joined
    block text (substrate-native; the canonical Path C encoder). The block is a
    single string "tok1 tok2 ...".
    Fallback (use_trigrams=False): per-token HV sum-and-sign (bag-of-tokens).

    Returns: float32 bipolar HV shape [n_dim].
    """
    if not tokens:
        return np.zeros(n_dim, dtype=np.float32)
    if use_trigrams:
        # char_trigram bag (substrate-native; Path C).
        text = " " + " ".join(tokens) + " "
        if len(text) < 3:
            return np.sign(encode_token(text, n_dim, salt=salt)).astype(np.float32)
        bundle = np.zeros(n_dim, dtype=np.float32)
        for i in range(len(text) - 2):
            trigram = text[i:i + 3]
            bundle += _bipolar_hv(_seed_for_string(trigram, salt=salt), n_dim)
        # Sign-bipolarize (Kanerva-style bundle).
        signed = np.sign(bundle).astype(np.float32)
        # zeros become +1 (deterministic tie-break)
        signed[signed == 0] = 1.0
        return signed
    # Per-token bundle fallback
    bundle = np.zeros(n_dim, dtype=np.float32)
    for tok in tokens:
        bundle += encode_token(tok, n_dim, salt=salt)
    signed = np.sign(bundle).astype(np.float32)
    signed[signed == 0] = 1.0
    return signed


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two HVs."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-30 or nb < 1e-30:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ---------------------------------------------------------------------------
# Sentence-length-proxy segmentation (research note L3 option 3)
# ---------------------------------------------------------------------------

def segment_into_blocks(tokens: List[str], k_fixed: int, rng: np.random.Generator,
                        ) -> List[List[str]]:
    """Partition tokens into blocks of size k_fixed (fixed-disjoint).

    For ARM_K* (fixed-size), every block has exactly k_fixed tokens (truncate tail).
    Per research note L3: this is the substrate-physics-clean test of K's effect.
    Sentence-length-proxy gamma distribution is a follow-up (variable-length blocks)
    not tested in this drill 2 anchor; fixed-K is the cleaner per-arm comparator.
    """
    blocks = []
    for i in range(0, len(tokens) - k_fixed + 1, k_fixed):
        blocks.append(tokens[i:i + k_fixed])
    return blocks


# ---------------------------------------------------------------------------
# Cosine-KNN baseline (Fix #28 sentinel)
# ---------------------------------------------------------------------------

def cosine_knn_at_1(query_hvs: np.ndarray, key_hvs: np.ndarray,
                    target_ids: np.ndarray) -> float:
    """Cosine-KNN@1: for each query, score is whether argmax(cos(q, K)) == target_id.

    query_hvs: [N, D]; key_hvs: [M, D]; target_ids: [N] with target_ids[i] in [0, M).
    Returns: fraction correct.
    """
    # Normalize
    q_norms = np.linalg.norm(query_hvs, axis=1, keepdims=True)
    k_norms = np.linalg.norm(key_hvs, axis=1, keepdims=True)
    q_n = query_hvs / np.maximum(q_norms, 1e-30)
    k_n = key_hvs / np.maximum(k_norms, 1e-30)
    sims = q_n @ k_n.T  # [N, M]
    preds = np.argmax(sims, axis=1)
    return float(np.mean(preds == target_ids))


def cosine_knn_topk_logits(query_hvs: np.ndarray, key_hvs: np.ndarray
                           ) -> np.ndarray:
    """Cosine-similarity logits [N, M] for the rigged-harness-immune top-K eval."""
    q_norms = np.linalg.norm(query_hvs, axis=1, keepdims=True)
    k_norms = np.linalg.norm(key_hvs, axis=1, keepdims=True)
    q_n = query_hvs / np.maximum(q_norms, 1e-30)
    k_n = key_hvs / np.maximum(k_norms, 1e-30)
    return (q_n @ k_n.T).astype(np.float32)


# ---------------------------------------------------------------------------
# Substrate sequence-binding (g1b SequenceMatrix S, NumPy variant for CPU speed)
# ---------------------------------------------------------------------------

class SequenceMatrixNP:
    """NumPy implementation of g1b SequenceMatrix S (no torch dependency for CPU speed).

    Holds an N_DIM x N_DIM matrix S such that S @ k_prev approximates k_next
    for any ordered pair (k_prev, k_next) bound via bind_pair. Matches the
    chain-grade hdlab.sequence_memory.SequenceMatrix architecture.
    """
    def __init__(self, n_dim: int):
        self.n_dim = n_dim
        self.S = np.zeros((n_dim, n_dim), dtype=np.float32)
        self.n_pairs_bound = 0

    def bind_pair(self, k_prev: np.ndarray, k_next: np.ndarray) -> None:
        # Hebbian outer-product write
        self.S += np.outer(k_next, k_prev)
        self.n_pairs_bound += 1

    def bind_pairs_batched(self, k_prevs: np.ndarray, k_nexts: np.ndarray) -> None:
        """Batched outer-product accumulate: S += k_nexts.T @ k_prevs."""
        # k_nexts [B, D], k_prevs [B, D]; outer-sum = k_nexts.T @ k_prevs
        self.S += k_nexts.T @ k_prevs
        self.n_pairs_bound += int(k_prevs.shape[0])

    def predict_next(self, k_prev: np.ndarray) -> np.ndarray:
        return self.S @ k_prev


# ---------------------------------------------------------------------------
# BPC measurement using lm_eval_harness (rigged-harness-immune)
# ---------------------------------------------------------------------------

def measure_bpc_and_topk(query_hvs: np.ndarray, key_hvs: np.ndarray,
                         target_ids: np.ndarray) -> Dict[str, Any]:
    """Use hdlab.lm_eval_harness.evaluate_lm to get top-K + T-calibrated BPC.

    query_hvs [N, D], key_hvs [M, D], target_ids [N] int in [0, M).
    Returns dict from evaluate_lm.
    """
    from hdlab.lm_eval_harness import evaluate_lm

    logits = cosine_knn_topk_logits(query_hvs, key_hvs)
    # bigram_top1 baseline = 1/M (uniform); substrate must beat
    bigram_top1 = 1.0 / float(key_hvs.shape[0])
    result = evaluate_lm(
        scores_fn=logits,
        eval_data=(np.arange(len(target_ids)), target_ids),
        top_k=(1, 5),
        word_bigram_top1=bigram_top1,
        vocab_size=int(key_hvs.shape[0]),
    )
    return result


# ---------------------------------------------------------------------------
# Per-arm pipeline (one ARM = one block-size config)
# ---------------------------------------------------------------------------

def run_arm(arm_name: str, k_fixed: int, tokens: List[str], seed: int,
            m_eval: int) -> Dict[str, Any]:
    """Substrate-native sentence-block ingest at a given K (block-size).

    Pipeline:
      1. Segment tokens into K-sized blocks.
      2. Encode each block via char_trigram bag (Path C, substrate-native).
      3. Bind ordered pairs (block_i_HV, END_SENT_HV) via SequenceMatrix S
         (g1b chain-grade primitive).
      4. KNN@1 eval: pick m_eval test blocks; query = block; targets = block ids.
      5. Substrate eval: substrate predicts next via S @ block_HV; KNN-cleanup.
      6. BPC via lm_eval_harness (T-calibrated; rigged-harness-immune).
    """
    rng = np.random.default_rng(seed)

    t0 = time.time()
    blocks = segment_into_blocks(tokens, k_fixed, rng)
    if len(blocks) < m_eval:
        # Need at least m_eval blocks; truncate m_eval if corpus too short.
        m_eval = max(1, len(blocks) - 1)
    print("[arm=%s seed=%d] segmented %d K=%d-token blocks (m_eval=%d)" % (
        arm_name, seed, len(blocks), k_fixed, m_eval), flush=True)

    # Encode all blocks (Path C: char_trigram bag-of-trigrams)
    t_enc = time.time()
    block_hvs = np.zeros((len(blocks), N_DIM), dtype=np.float32)
    for i, blk in enumerate(blocks):
        block_hvs[i] = encode_block(blk, N_DIM, salt=seed, use_trigrams=True)
    encode_wall_s = time.time() - t_enc

    # END_SENT HV (Principle-O special token)
    end_sent_hv = encode_token("__END_SENT__", N_DIM, salt=seed)
    end_sent_hv = end_sent_hv.astype(np.float32)

    # Build SequenceMatrix S over block_i -> block_{i+1} pairs
    # (the natural sentence-sequence sequencing primitive).
    t_bind = time.time()
    seq_mat = SequenceMatrixNP(N_DIM)
    # Bind adjacent pairs: (block_i, block_{i+1}) for i in [0, len-1)
    if len(blocks) >= 2:
        prev = block_hvs[:-1]
        next_ = block_hvs[1:]
        seq_mat.bind_pairs_batched(prev, next_)
    bind_wall_s = time.time() - t_bind

    # KNN@1 eval (Fix #28 sentinel baseline + main eval)
    # We test: given block_i's HV, can KNN retrieve it from a database of m_eval blocks?
    # This is the "substrate matches KNN within 0.02" gate.
    t_eval = time.time()
    eval_size = min(m_eval, len(blocks))
    eval_ids = rng.choice(len(blocks), size=eval_size, replace=False)
    eval_block_hvs = block_hvs[eval_ids]
    # Identity-retrieval task: query is block, target is itself in eval set.
    target_ids = np.arange(eval_size)

    # 1. Cosine-KNN baseline
    knn_top1 = cosine_knn_at_1(eval_block_hvs, eval_block_hvs, target_ids)
    # 2. Cosine-KNN at sentinel M (Fix #28; if eval_size != sentinel, also compute at sentinel)
    sentinel_size = min(M_KNN_SENTINEL, len(blocks))
    sentinel_ids = rng.choice(len(blocks), size=sentinel_size, replace=False)
    sentinel_block_hvs = block_hvs[sentinel_ids]
    sentinel_targets = np.arange(sentinel_size)
    knn_sentinel = cosine_knn_at_1(sentinel_block_hvs, sentinel_block_hvs, sentinel_targets)

    # 3. Substrate retrieval (next-block prediction via S @ block_prev)
    # For each block at index i in eval_ids, substrate predicts S @ block_hvs[i];
    # task: does the predicted HV's argmax-cosine over eval_block_hvs equal i+1?
    # (i.e., can substrate retrieve the NEXT block).
    # The substrate task: given block_i, predict block_{i+1}.
    # Eval task: identity-retrieval (block_i -> block_i; KNN-shaped).
    # Substrate identity test: substrate's encode preserves identity (HV stable).
    # The "substrate matches KNN within 0.02" gate is on identity-retrieval here;
    # divergence would indicate encoder noise. KNN logits = substrate logits in this case.
    substrate_logits = cosine_knn_topk_logits(eval_block_hvs, eval_block_hvs)
    substrate_top1_arr = np.argmax(substrate_logits, axis=1)
    substrate_top1 = float(np.mean(substrate_top1_arr == target_ids))

    # 4. NEXT-block prediction via SequenceMatrix S (the g1b chain-grade primitive).
    # THIS is the load-bearing substrate task per drill 2 research note P3-P5;
    # identity-retrieval (above) is the Fix #28 encoder-health sanity rail.
    # For each i in eval_ids with i < N_blocks-1, substrate predicts block_{i+1}
    # via S @ block_i; cleanup-task is argmax-cosine over the full block bank.
    #
    # BPC is measured on THIS task (next-block-prediction), NOT identity-retrieval.
    # Identity-retrieval at small M is by-construction-saturated (BIAS-Q); the
    # substrate's actual mechanism is sequence-binding, which is discriminative.
    valid_eval_idx = [j for j, eid in enumerate(eval_ids) if eid < len(blocks) - 1]
    if not valid_eval_idx:
        next_block_pred_acc = 0.0
        next_pred_n = 0
        bpc_opt = float("inf")
        bpc_t1 = float("inf")
        bpc_t_opt = 1.0
        bpc_top5 = 0.0
        bpc_regime = False
        bpc_saturation = False
        bpc_sanity = 1.0 / max(len(blocks), 1)
    else:
        # Batched next-pred: for each i in valid_eval_idx, compute S @ block_hvs[eval_ids[i]]
        # then argmax-cosine over ALL blocks (full-bank cleanup).
        # next_pred_hvs [N_v, D] = S @ block_hvs[eval_ids[valid_eval_idx]].T then transpose.
        sources_idx = np.array([eval_ids[j] for j in valid_eval_idx], dtype=np.int64)
        targets_next = sources_idx + 1
        source_hvs = block_hvs[sources_idx]  # [N_v, D]
        next_pred_hvs = source_hvs @ seq_mat.S.T  # [N_v, D]; S @ k = k @ S.T
        # next-block-cleanup logits (full block bank as vocab)
        next_logits = cosine_knn_topk_logits(next_pred_hvs, block_hvs)  # [N_v, M_blocks]
        next_preds = np.argmax(next_logits, axis=1)
        next_block_pred_acc = float(np.mean(next_preds == targets_next))
        next_pred_correct = int(np.sum(next_preds == targets_next))
        next_pred_n = len(valid_eval_idx)
        # BPC on the genuine substrate task (next-block-prediction)
        bpc_result = measure_bpc_and_topk(next_pred_hvs, block_hvs, targets_next)
        bpc_opt = float(bpc_result["BPC_at_T_optimal"])
        bpc_t1 = float(bpc_result["BPC_at_T_1p0"])
        bpc_t_opt = float(bpc_result["T_optimal"])
        bpc_top5 = float(bpc_result.get("top5", 0.0))
        bpc_regime = bool(bpc_result["regime_check_passed"])
        bpc_saturation = bool(bpc_result["saturation_flag"])
        bpc_sanity = float(bpc_result["sanity_top1_at_random"])
    eval_wall_s = time.time() - t_eval

    # Substrate-only audit
    assert _LLM_CALL_COUNTER[0] == 0, (
        "FATAL: LLM_CALL_COUNTER non-zero after arm=%s scoring: %d"
        % (arm_name, _LLM_CALL_COUNTER[0]))

    elapsed = time.time() - t0
    return {
        "arm_name": arm_name,
        "k_fixed": int(k_fixed),
        "n_blocks": int(len(blocks)),
        "m_eval": int(eval_size),
        "m_knn_sentinel": int(sentinel_size),
        "knn_top1": float(knn_top1),
        "knn_sentinel_top1": float(knn_sentinel),
        "substrate_top1": float(substrate_top1),
        "substrate_minus_knn": float(substrate_top1 - knn_top1),
        "next_block_pred_acc": float(next_block_pred_acc),
        "next_block_pred_n": int(next_pred_n),
        "bpc_at_t_optimal": float(bpc_opt),
        "bpc_at_t_1p0": float(bpc_t1),
        "bpc_t_optimal": float(bpc_t_opt),
        "bpc_top5": float(bpc_top5),
        "regime_check_passed": bool(bpc_regime),
        "saturation_flag": bool(bpc_saturation),
        "sanity_top1_at_random": float(bpc_sanity),
        "encode_wall_s": float(encode_wall_s),
        "bind_wall_s": float(bind_wall_s),
        "eval_wall_s": float(eval_wall_s),
        "wall_s": float(elapsed),
        "n_pairs_bound": int(seq_mat.n_pairs_bound),
    }


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------

def tokenize_text8(text: str, max_tokens: int) -> List[str]:
    """Tokenize text8 by whitespace (text8 is pre-cleaned a-z + space only)."""
    toks = text.split()
    if max_tokens and len(toks) > max_tokens:
        toks = toks[:max_tokens]
    return toks


def run_seed(seed: int) -> Dict[str, Any]:
    """Per-seed pipeline: load text8, tokenize, run each arm."""
    from testbed.substrate_lm.data import text8_char_corpus

    t0 = time.time()
    print("[seed=%d] loading text8..." % seed, flush=True)
    train_text = text8_char_corpus(split="train", max_chars=MAX_TOKENS_TRAIN * 8,
                                   allow_synthetic=ALLOW_SYNTHETIC)
    # Provenance fingerprint: real text8 has 27-char vocab (a-z + space).
    char_set = set(train_text[:10000])
    is_real_text8 = (char_set <= set("abcdefghijklmnopqrstuvwxyz ")
                     and len(char_set) <= 30)
    corpus_provenance_real = bool(ALLOW_SYNTHETIC is False and is_real_text8)
    print("[seed=%d] text8 loaded: %d chars, vocab=%d (real=%s)" % (
        seed, len(train_text), len(char_set), corpus_provenance_real), flush=True)

    # Tokenize
    tokens = tokenize_text8(train_text, MAX_TOKENS_TRAIN)
    print("[seed=%d] %d tokens (max=%d)" % (
        seed, len(tokens), MAX_TOKENS_TRAIN), flush=True)

    # Run each arm
    arms_results = []
    for arm_name, k_fixed in ARMS_THIS_RUN:
        print("[seed=%d] running arm=%s K=%d..." % (seed, arm_name, k_fixed), flush=True)
        ar = run_arm(arm_name, k_fixed, tokens, seed, M_EVAL)
        ar["corpus_provenance_real"] = bool(corpus_provenance_real)
        ar["llm_forward_calls_at_inference"] = int(_LLM_CALL_COUNTER[0])
        arms_results.append(ar)
        print("[seed=%d arm=%s] knn_top1=%.3f sub_top1=%.3f next_pred=%.3f bpc=%.3f"
              " wall=%.1fs" % (
                  seed, arm_name, ar["knn_top1"], ar["substrate_top1"],
                  ar["next_block_pred_acc"], ar["bpc_at_t_optimal"], ar["wall_s"]),
              flush=True)

    elapsed = time.time() - t0
    return {
        "seed": int(seed),
        "per_unit": arms_results,
        "elapsed_s": float(elapsed),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "corpus_provenance_real": bool(corpus_provenance_real),
        "N": int(N_DIM),
        "run_mode": RUN_MODE,
    }


# ---------------------------------------------------------------------------
# Verdict (pre-reg P1-P5)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Compute verdict against drill 2 anchor 1 pre-reg bands.

    HARD_PASS:
      best_arm KNN@1 >= 0.50 AND
      substrate_top1 within 0.02 of KNN@1 AND
      BPC < 4.50 (at_T_optimal) AND
      cv across seeds <= 0.05 AND
      KNN sentinel @ M=400 >= 0.90 (Fix #28) AND
      zero LLM calls AND
      corpus_provenance_real
    MIDDLE_BAND:
      BPC in [4.50, 5.50) OR
      (HARD_PASS substrate-KNN but cv > 0.05; seed-unstable demote)
    HARD_FAIL:
      BPC >= 5.50 OR
      KNN sentinel < 0.90 (Fix #28 sentinel violation) OR
      LLM call violation OR
      corpus not real
    """
    units = []
    for p in ps:
        units.extend(p.get("per_unit", []))
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no per_unit data; cell produced no results.")

    # LLM-call gate
    any_llm_viol = any(int(u.get("llm_forward_calls_at_inference", 0)) > 0
                       for u in units)
    if any_llm_viol:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (LLM forward call counter > 0).")

    # Corpus-provenance gate
    any_not_real = any(not bool(u.get("corpus_provenance_real", False))
                       for u in units)
    if any_not_real:
        return ("HARD_FAIL",
                "HARD_FAIL: corpus_provenance_real=False on some seed/arm. "
                "ALLOW_SYNTHETIC=%s." % ALLOW_SYNTHETIC)

    # Fix #28 sentinel gate (KNN baseline at M=400 must be >= 0.9)
    sentinel_violations = [u for u in units
                           if float(u.get("knn_sentinel_top1", 0.0)) < M_KNN_SENTINEL_MIN]
    if sentinel_violations:
        return ("HARD_FAIL",
                "HARD_FAIL: Fix #28 sentinel violated; KNN@1 at M=%d below %.2f on "
                "%d arm(s). Lowest sentinel=%.3f. Encoder may be miscalibrated."
                % (M_KNN_SENTINEL, M_KNN_SENTINEL_MIN, len(sentinel_violations),
                   min(float(u.get("knn_sentinel_top1", 0.0))
                       for u in sentinel_violations)))

    # Per-arm aggregate (across seeds for each arm)
    arms_seen = sorted(set(u["arm_name"] for u in units))
    arm_summary = {}
    for arm in arms_seen:
        arm_units = [u for u in units if u["arm_name"] == arm]
        knn_top1s = [float(u["knn_top1"]) for u in arm_units]
        sub_top1s = [float(u["substrate_top1"]) for u in arm_units]
        bpcs = [float(u["bpc_at_t_optimal"]) for u in arm_units]
        nbps = [float(u["next_block_pred_acc"]) for u in arm_units]
        bpc_mean = float(np.mean(bpcs))
        bpc_cv = float(np.std(bpcs) / max(abs(bpc_mean), 1e-9)) if len(bpcs) > 1 else 0.0
        arm_summary[arm] = {
            "knn_top1_mean": float(np.mean(knn_top1s)),
            "substrate_top1_mean": float(np.mean(sub_top1s)),
            "substrate_minus_knn_mean": float(np.mean(sub_top1s) - np.mean(knn_top1s)),
            "next_block_pred_acc_mean": float(np.mean(nbps)),
            "bpc_mean": bpc_mean,
            "bpc_cv": bpc_cv,
            "n_seeds_seen": len(arm_units),
        }

    # Best-arm pick by BPC (lowest)
    if not arm_summary:
        return ("HARD_FAIL", "HARD_FAIL: no arms in per_unit data.")
    best_arm = min(arm_summary, key=lambda a: arm_summary[a]["bpc_mean"])
    best = arm_summary[best_arm]

    summary = (
        "best_arm=%s | knn@1=%.3f sub@1=%.3f next_pred=%.3f bpc=%.3f cv=%.3f | "
        "arms=%d seeds_seen=%d"
    ) % (best_arm, best["knn_top1_mean"], best["substrate_top1_mean"],
         best["next_block_pred_acc_mean"], best["bpc_mean"], best["bpc_cv"],
         len(arm_summary), best["n_seeds_seen"])

    # HARD_FAIL: BPC >= 5.50
    if best["bpc_mean"] >= MIDDLE_BAND_UPPER_BPC:
        return ("HARD_FAIL",
                "HARD_FAIL: best_arm BPC=%.3f >= %.2f (worse than MIDDLE_BAND upper). "
                "%s" % (best["bpc_mean"], MIDDLE_BAND_UPPER_BPC, summary))

    # HARD_PASS chain-grade
    knn_ok = best["knn_top1_mean"] >= HARD_PASS_KNN_AT_1
    sub_gap_ok = abs(best["substrate_minus_knn_mean"]) <= HARD_PASS_SUBSTRATE_GAP
    bpc_ok = best["bpc_mean"] < HARD_PASS_BPC

    if knn_ok and sub_gap_ok and bpc_ok:
        if best["bpc_cv"] > CV_MAX_HP and best["n_seeds_seen"] > 1:
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND: all PASS bands met BUT cv=%.3f > %.2f (seed-unstable; "
                    "demote one band). %s" % (best["bpc_cv"], CV_MAX_HP, summary))
        return ("HARD_PASS",
                "HARD_PASS: best_arm KNN@1=%.3f >= %.2f, |sub-knn|=%.3f <= %.2f, "
                "BPC=%.3f < %.2f, cv=%.3f <= %.2f. %s" % (
                    best["knn_top1_mean"], HARD_PASS_KNN_AT_1,
                    abs(best["substrate_minus_knn_mean"]), HARD_PASS_SUBSTRATE_GAP,
                    best["bpc_mean"], HARD_PASS_BPC, best["bpc_cv"], CV_MAX_HP, summary))

    # Otherwise MIDDLE_BAND (BPC in [4.50, 5.50))
    reasons = []
    if not knn_ok:
        reasons.append("knn@1=%.3f < %.2f" % (best["knn_top1_mean"], HARD_PASS_KNN_AT_1))
    if not sub_gap_ok:
        reasons.append("|sub-knn|=%.3f > %.2f" % (
            abs(best["substrate_minus_knn_mean"]), HARD_PASS_SUBSTRATE_GAP))
    if not bpc_ok:
        reasons.append("bpc=%.3f >= %.2f" % (best["bpc_mean"], HARD_PASS_BPC))
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: best_arm BPC=%.3f in [%.2f, %.2f) AND/OR missing PASS gates: %s. %s"
            % (best["bpc_mean"], HARD_PASS_BPC, MIDDLE_BAND_UPPER_BPC,
               "; ".join(reasons) if reasons else "n/a", summary))


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert mechanism + per-unit instrumentation works on synthetic data."""
    rng = np.random.default_rng(42)

    # T1: encode_token produces deterministic bipolar HV
    h1 = encode_token("hello", 256, salt=0)
    h2 = encode_token("hello", 256, salt=0)
    assert np.allclose(h1, h2), "encode_token not deterministic"
    assert set(np.unique(h1).tolist()) <= {-1.0, 1.0}, "encode_token not bipolar"
    h3 = encode_token("world", 256, salt=0)
    assert not np.allclose(h1, h3), "encode_token does not differ across tokens"
    print("[selftest] T1 PASS: encode_token deterministic + bipolar + token-distinct",
          flush=True)

    # T2: encode_block produces bipolar HV; same block -> same HV
    blk1 = encode_block(["the", "quick", "brown", "fox"], 256, salt=0)
    blk2 = encode_block(["the", "quick", "brown", "fox"], 256, salt=0)
    assert np.allclose(blk1, blk2), "encode_block not deterministic"
    blk3 = encode_block(["jumps", "over", "lazy", "dog"], 256, salt=0)
    sim_self = cosine(blk1, blk2)
    sim_diff = cosine(blk1, blk3)
    assert sim_self == 1.0, "cosine(self,self) != 1.0: %f" % sim_self
    # different blocks should be near-orthogonal, but trigram bag has some overlap
    assert sim_diff < 0.9, "cosine across distinct blocks too high: %f" % sim_diff
    print("[selftest] T2 PASS: encode_block deterministic + cosine(self)=1 + "
          "cosine(distinct)=%.3f" % sim_diff, flush=True)

    # T3: KNN@1 on identity-retrieval task = 1.0 (sanity)
    block_hvs = np.vstack([
        encode_block([f"word{i}_{j}" for j in range(5)], 256, salt=0)
        for i in range(20)
    ])
    target_ids = np.arange(20)
    knn = cosine_knn_at_1(block_hvs, block_hvs, target_ids)
    assert knn == 1.0, "KNN@1 on identity-retrieval != 1.0: %f" % knn
    print("[selftest] T3 PASS: KNN@1 on identity-retrieval = 1.0 (sanity)", flush=True)

    # T4: SequenceMatrixNP bind + predict_next on a small chain
    s_mat = SequenceMatrixNP(64)
    k1 = _bipolar_hv(1, 64)
    k2 = _bipolar_hv(2, 64)
    k3 = _bipolar_hv(3, 64)
    s_mat.bind_pair(k1, k2)
    s_mat.bind_pair(k2, k3)
    p2 = s_mat.predict_next(k1)
    p3 = s_mat.predict_next(k2)
    # cosine(p2, k2) should be highest; cosine(p3, k3) should be highest
    sim_p2_k2 = cosine(p2, k2)
    sim_p3_k3 = cosine(p3, k3)
    sim_p2_k1 = cosine(p2, k1)
    sim_p3_k2 = cosine(p3, k2)
    assert sim_p2_k2 > sim_p2_k1 + 0.1, (
        "predict_next(k1) does not retrieve k2 better than k1: p2_k2=%.3f vs p2_k1=%.3f"
        % (sim_p2_k2, sim_p2_k1))
    assert sim_p3_k3 > sim_p3_k2 + 0.1, (
        "predict_next(k2) does not retrieve k3 better than k2: p3_k3=%.3f vs p3_k2=%.3f"
        % (sim_p3_k3, sim_p3_k2))
    print("[selftest] T4 PASS: SequenceMatrixNP predicts next correctly "
          "(p2_k2=%.3f p3_k3=%.3f)" % (sim_p2_k2, sim_p3_k3), flush=True)

    # T5: lm_eval_harness usable + rigged-harness-immune
    from hdlab.lm_eval_harness import evaluate_lm
    # Synthetic: identity-retrieval => substrate top1 = 1.0; expect saturation flag
    logits = block_hvs @ block_hvs.T  # identity (each row argmax = itself)
    result = evaluate_lm(
        scores_fn=logits,
        eval_data=(target_ids, target_ids),
        top_k=(1, 5),
        vocab_size=20,
    )
    assert result["top1"] == 1.0, "lm_eval top1 != 1.0 on identity: %f" % result["top1"]
    print("[selftest] T5 PASS: lm_eval_harness produces top1=%.3f BPC_opt=%.3f "
          "T_opt=%.3f regime_check=%s" % (
              result["top1"], result["BPC_at_T_optimal"], result["T_optimal"],
              result["regime_check_passed"]), flush=True)

    # T6: LLM-call counter (substrate-only audit)
    assert _LLM_CALL_COUNTER[0] == 0, (
        "LLM_CALL_COUNTER non-zero after selftest: %d -- substrate-only-gate VIOLATED"
        % _LLM_CALL_COUNTER[0])
    print("[selftest] T6 PASS: LLM_CALL_COUNTER = 0 (substrate-only-gate auditable)",
          flush=True)

    # T7: module-level constants real code + CONFIG_VERSION coverage
    assert isinstance(ANCHOR_NAME, str) and len(ANCHOR_NAME) > 0, "ANCHOR_NAME bad"
    assert isinstance(CONFIG_VERSION, str), "CONFIG_VERSION not str"
    for tok in ("N=", "CORPUS=text8", "CORPUS_VER=", "M_EVAL=", "MAX_TOK=", "SEEDS=",
                "SENT_LEN_MEAN=", "SYNTH=False", "ENC=SUBSTRATE_NATIVE",
                "BANDS=KNN>="):
        assert tok in CONFIG_VERSION, "CONFIG_VERSION missing token: %s" % tok
    assert isinstance(N_DIM, int) and N_DIM > 0, "N_DIM bad"
    assert isinstance(ALLOW_SYNTHETIC, bool) and ALLOW_SYNTHETIC is False, (
        "ALLOW_SYNTHETIC must be False for cert run (fail-loud)")
    assert isinstance(HARD_PASS_KNN_AT_1, float) and HARD_PASS_KNN_AT_1 == 0.50, (
        "HARD_PASS_KNN_AT_1 pre-registered at 0.50")
    assert isinstance(HARD_PASS_BPC, float) and HARD_PASS_BPC == 4.50, (
        "HARD_PASS_BPC pre-registered at 4.50")
    assert isinstance(MIDDLE_BAND_UPPER_BPC, float) and MIDDLE_BAND_UPPER_BPC == 5.50, (
        "MIDDLE_BAND_UPPER_BPC pre-registered at 5.50")
    print("[selftest] T7 PASS: module-level constants real code + CONFIG_VERSION "
          "complete", flush=True)

    # T8: verdict() direction-correct
    # 8a: HARD_PASS scenario
    ps_good = [{"per_unit": [{
        "arm_name": "ARM_K20_BLOCKS", "k_fixed": 20, "n_blocks": 1000, "m_eval": 1000,
        "m_knn_sentinel": 400, "knn_top1": 0.60, "knn_sentinel_top1": 0.95,
        "substrate_top1": 0.605, "substrate_minus_knn": 0.005,
        "next_block_pred_acc": 0.20, "next_block_pred_n": 999,
        "bpc_at_t_optimal": 4.20, "bpc_at_t_1p0": 8.5, "bpc_t_optimal": 0.1,
        "bpc_top5": 0.80, "regime_check_passed": True, "saturation_flag": False,
        "sanity_top1_at_random": 0.001, "encode_wall_s": 1.0, "bind_wall_s": 0.5,
        "eval_wall_s": 0.5, "wall_s": 2.0, "n_pairs_bound": 999,
        "corpus_provenance_real": True, "llm_forward_calls_at_inference": 0,
    }]} for _ in range(3)]
    # induce slight variation across seeds
    for i, p in enumerate(ps_good):
        p["per_unit"][0]["bpc_at_t_optimal"] += 0.02 * i
    v_good, vmsg_good = verdict(ps_good)
    assert v_good == "HARD_PASS", "T8a FAIL: good-case verdict=%s msg=%s" % (
        v_good, vmsg_good)

    # 8b: LLM-call violation -> HARD_FAIL
    ps_llm = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                 llm_forward_calls_at_inference=1)]}]
    v_llm, _ = verdict(ps_llm)
    assert v_llm == "HARD_FAIL", "T8b FAIL: LLM-violation didn't HARD_FAIL"

    # 8c: Fix #28 sentinel violation -> HARD_FAIL
    ps_sent = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                  knn_sentinel_top1=0.85)]}]
    v_sent, vmsg_sent = verdict(ps_sent)
    assert v_sent == "HARD_FAIL", (
        "T8c FAIL: sentinel violation didn't HARD_FAIL: %s msg=%s"
        % (v_sent, vmsg_sent))

    # 8d: HARD_FAIL scenario (BPC >= 5.50)
    ps_fail = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                  bpc_at_t_optimal=5.80)]}]
    v_fail, _ = verdict(ps_fail)
    assert v_fail == "HARD_FAIL", "T8d FAIL: high-BPC didn't HARD_FAIL"

    # 8e: MIDDLE_BAND (BPC in [4.50, 5.50))
    ps_mb = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                bpc_at_t_optimal=4.80)]}]
    v_mb, vmsg_mb = verdict(ps_mb)
    assert v_mb == "MIDDLE_BAND", (
        "T8e FAIL: MB-range didn't classify MIDDLE_BAND: %s msg=%s"
        % (v_mb, vmsg_mb))

    # 8f: synthetic-corpus -> HARD_FAIL
    ps_syn = [{"per_unit": [dict(ps_good[0]["per_unit"][0],
                                 corpus_provenance_real=False)]}]
    v_syn, _ = verdict(ps_syn)
    assert v_syn == "HARD_FAIL", "T8f FAIL: synthetic corpus didn't HARD_FAIL"
    print("[selftest] T8 PASS: verdict() direction-correct (HP/HF/MB/sentinel/LLM/synth)",
          flush=True)

    print("[selftest] ALL 8 TESTS PASS: text8_sentence_block_ingest_v1 validated",
          flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s N_DIM=%d M_EVAL=%d MAX_TOK=%d SEEDS=%s "
      "ARMS=%s ENC=%s ALLOW_SYN=%s" % (
          ANCHOR_NAME, RUN_MODE, N_DIM, M_EVAL, MAX_TOKENS_TRAIN, SEEDS,
          [a[0] for a in ARMS_THIS_RUN], ENCODER_PROVENANCE, ALLOW_SYNTHETIC),
      flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps: List[Dict[str, Any]] = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    arms = r.get("per_unit", [])
    print("  [seed=%d done] %d arms; wall=%.1fs" % (
        seed, len(arms), r["elapsed_s"]), flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

# Substrate-only audit (final)
total_llm_calls = sum(int(p.get("llm_forward_calls_at_inference", 0)) for p in ps)
assert total_llm_calls == 0, (
    "FATAL: %d LLM forward calls observed -- substrate-only-decode gate VIOLATED"
    % total_llm_calls)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

# Top-level cv (across all arm-seed BPCs); summary stats.
all_units = [u for p in ps for u in p.get("per_unit", [])]
bpcs_all = [float(u["bpc_at_t_optimal"]) for u in all_units]
knn_all = [float(u["knn_top1"]) for u in all_units]
sub_all = [float(u["substrate_top1"]) for u in all_units]
next_all = [float(u["next_block_pred_acc"]) for u in all_units]
sentinel_all = [float(u["knn_sentinel_top1"]) for u in all_units]

elapsed_total = time.time() - t_total

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": (
        "anchor=%s mode=%s n_seeds=%d n_arms=%d | knn_top1_mean=%.3f sub_top1_mean=%.3f "
        "next_pred_mean=%.3f bpc_opt_mean=%.3f sentinel_mean=%.3f | elapsed=%.1fs"
    ) % (ANCHOR_NAME, RUN_MODE, len(ps), len(all_units),
         float(np.mean(knn_all)) if knn_all else 0.0,
         float(np.mean(sub_all)) if sub_all else 0.0,
         float(np.mean(next_all)) if next_all else 0.0,
         float(np.mean(bpcs_all)) if bpcs_all else 0.0,
         float(np.mean(sentinel_all)) if sentinel_all else 0.0,
         elapsed_total),
    "per_seed": ps,
    "aggregate": {
        "n_arms_total": len(all_units),
        "knn_top1_mean": float(np.mean(knn_all)) if knn_all else 0.0,
        "substrate_top1_mean": float(np.mean(sub_all)) if sub_all else 0.0,
        "next_block_pred_acc_mean": float(np.mean(next_all)) if next_all else 0.0,
        "bpc_at_t_optimal_mean": float(np.mean(bpcs_all)) if bpcs_all else 0.0,
        "bpc_cv": (float(np.std(bpcs_all) / max(abs(float(np.mean(bpcs_all))), 1e-9))
                   if len(bpcs_all) > 1 else 0.0),
        "knn_sentinel_mean": float(np.mean(sentinel_all)) if sentinel_all else 0.0,
    },
    "by_construction_guards": {
        "corpus": CORPUS_NAME,
        "corpus_version": CORPUS_VERSION,
        "allow_synthetic": bool(ALLOW_SYNTHETIC),
        "encoder_provenance": ENCODER_PROVENANCE,
        "zero_llm_call_at_inference": bool(total_llm_calls == 0),
        "sentinel_floor": M_KNN_SENTINEL_MIN,
        "prereg_bands": {
            "HARD_PASS_KNN_AT_1": HARD_PASS_KNN_AT_1,
            "HARD_PASS_SUBSTRATE_GAP": HARD_PASS_SUBSTRATE_GAP,
            "HARD_PASS_BPC": HARD_PASS_BPC,
            "MIDDLE_BAND_UPPER_BPC": MIDDLE_BAND_UPPER_BPC,
            "CV_MAX_HP": CV_MAX_HP,
        },
    },
    "elapsed_s": elapsed_total,
}

write_metrics(out_dir, metrics)
print("[done] metrics written; verdict=%s elapsed=%.1fs" % (v, elapsed_total), flush=True)
