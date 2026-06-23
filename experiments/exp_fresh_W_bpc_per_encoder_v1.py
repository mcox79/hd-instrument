"""fresh_W_bpc_per_encoder_v1 -- METHODOLOGY-CORRECTED Path A BPC test.

USER directive 2026-06-23 ("we need to make sure we're not testing these new ideas
against old coding or data"): the current Path A test reuses a SUBSTRATE W matrix
that was built with char_trigram during ingest, masking how good pretrained
encoders actually are. This cell builds a COMPLETELY FRESH W matrix per encoder
candidate (no char-trigram contamination), then measures BPC.

Builds on encoder_word2vec_substrate_bind_v1 (numpy + N_DIM=4096) -- moves to
torch.cuda + N_DIM=8192 + adds ARM_CHAR_TRIGRAM_FRESH_W as honest baseline.

DESIGN (5 arms x lambda sweep x 3 seeds; each arm builds its own fresh W on GPU):

  ARM_UNIGRAM            -- baseline floor; analytic, no W.
  ARM_CHAR_TRIGRAM_FRESH_W
        ingest text8 using char_trigram_encoder -> 8192d HD vectors;
        build FRESH Hebbian W = sum E[t+1] outer E[t] from scratch using
        ONLY these vectors. Honest substrate-native baseline with fresh W.
  ARM_WORD2VEC_FRESH_W
        ingest text8 using word2vec-google-news-300 -> projected to 8192d;
        build FRESH W from scratch using ONLY word2vec vectors.
  ARM_GLOVE_FRESH_W
        ingest text8 using glove-wiki-gigaword-300 -> projected to 8192d.
  ARM_FASTTEXT_FRESH_W
        ingest text8 using fasttext-wiki-news-subwords-300 -> projected to 8192d
        (handles OOV via char-ngram backoff).

CRITICAL: each arm gets its own W matrix; NO sharing of substrate state.

PRE-REG HARD bands (V2 LM gap closure; chain-grade-eligible):
  HARD_PASS: ANY ARM_*_FRESH_W achieves BPC < 7.738 (beats unigram) AND
             lift over ARM_CHAR_TRIGRAM_FRESH_W >= 0.5 bits (semantic encoder
             beats lexical encoder by >=0.5 bits on substrate).
  HARD_FAIL: ALL encoder arms BPC >= 7.738 (no encoder beats unigram even with
             fresh W); confirms substrate's rank-1 Hebbian readout is
             mathematically capped regardless of encoder; pivots V2 to descope
             or architectural rewrite.
  MIDDLE_BAND: semantic encoders lift over char_trigram but don't beat unigram
               -- partial; characterizes encoder contribution vs W-bottleneck.

SANITY:
  - At lambda=1.0 in interp, all arms reproduce ARM_*_RAW (substrate-only).
  - At lambda=0.0, each arm = pure unigram (reproduces ARM_UNIGRAM).
  - Sweep [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]; report best lambda per encoder.

GPU REQUIRED (Fix #24): torch.cuda + batched matmul for Hebbian writes;
heartbeat with util-check.

Cites:
  - preregs/2026-06-23_fresh_W_bpc_per_encoder_v1.md
  - exp_encoder_word2vec_substrate_bind_v1.py (parent; numpy + N=4096)
  - exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py (BPC ref)
  - USER 2026-06-23 methodology fix
  - USER 2026-06-22 GPU dispatch must use GPU (Fix #24)

ASCII-only. Per-seed checkpoint. atexit synthesizer.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import hashlib
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "fresh_W_bpc_per_encoder_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines (from prior cells)
UNIGRAM_BPC_REF = 7.738
PATH_A_PRIOR_BPC_REF = 7.864

# Pre-reg bands
HP_BPC_BAR = UNIGRAM_BPC_REF  # < 7.738 to HARD_PASS
HP_LIFT_OVER_TRIGRAM = 0.5     # lift over ARM_CHAR_TRIGRAM_FRESH_W must be >= 0.5
HF_BPC_BAR = UNIGRAM_BPC_REF   # all encoders >= 7.738 = HARD_FAIL
HP_BPC_CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Config
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under SMOKE_TIMEOUT_S=180s on laptop CPU
    # (matmul-heavy at full N_DIM=8192; shrink to feasible config that still
    # exercises every code path: char_trigram + 3 pretrained encoder loads,
    # fresh W build + recall, lambda sweep, verdict assembly).
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 400

ARMS = [
    "ARM_UNIGRAM",
    "ARM_CHAR_TRIGRAM_FRESH_W",
    "ARM_WORD2VEC_FRESH_W",
    "ARM_GLOVE_FRESH_W",
    "ARM_FASTTEXT_FRESH_W",
]
PRETRAINED_ARMS = {"ARM_WORD2VEC_FRESH_W", "ARM_GLOVE_FRESH_W", "ARM_FASTTEXT_FRESH_W"}
GENSIM_MODEL_FOR = {
    "ARM_WORD2VEC_FRESH_W": "word2vec-google-news-300",
    "ARM_GLOVE_FRESH_W":    "glove-wiki-gigaword-300",
    "ARM_FASTTEXT_FRESH_W": "fasttext-wiki-news-subwords-300",
}

CONFIG_VERSION = (
    "fresh_W_bpc_per_encoder_v1; N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s INGEST_CHUNK=%d RECALL_BATCH=%d device=%s "
    "lambda_grid=%s; bands HP_bpc<%.3f HP_lift>=%.2f HF_bpc>=%.3f cv_max=%.2f"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS,
    RUN_MODE, INGEST_CHUNK, RECALL_BATCH, str(DEVICE), LAMBDA_GRID,
    HP_BPC_BAR, HP_LIFT_OVER_TRIGRAM, HF_BPC_BAR, HP_BPC_CV_MAX,
)


# ============================================================================
# Encoders
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# Gensim cache
_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                v = None
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """ARM_CHAR_TRIGRAM_FRESH_W: build [V, n_dim] L2-normalized HD vectors on GPU."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def build_E_pretrained_gpu(vocab: List[str], n_dim: int, seed: int, model_name: str
                            ) -> Tuple[torch.Tensor, Dict]:
    """ARMS_*_FRESH_W (pretrained): load gensim KV -> project 300d -> n_dim on GPU.

    OOV fallback to char-trigram so we have a defined vector per vocab word
    (avoids zero-row degenerate inputs to Hebbian outer-product).
    """
    kv = _load_gensim_kv(model_name)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


# ============================================================================
# Fresh-W Hebbian builder (GPU)
# ============================================================================

def build_fresh_hebbian_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                                ingest_chunk: int) -> torch.Tensor:
    """Build a COMPLETELY FRESH W [N_DIM, N_DIM] from scratch using ONLY E.

    W += sum over (t, t+1) of outer(E[idx[t+1]], E[idx[t]])
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


# ============================================================================
# text8 loader / vocab
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# BPC computation: substrate logits via fresh W; log-linear interp w/ unigram
# ============================================================================

def compute_substrate_logits_gpu(E: torch.Tensor, W: torch.Tensor, ctx_idx: np.ndarray,
                                   recall_batch: int) -> np.ndarray:
    """Per-position substrate logits over full vocab: [n, V] float32 (numpy)."""
    V = E.shape[0]
    n = len(ctx_idx)
    logits_out = np.zeros((n, V), dtype=np.float32)
    ctx_t = torch.from_numpy(ctx_idx).to(DEVICE)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        ctx_b = ctx_t[b:end]
        pred_vec = E[ctx_b] @ W.T
        pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
        pred_vec = pred_vec / pn
        logits_b = pred_vec @ E.T
        logits_out[b:end] = logits_b.detach().cpu().numpy()
        if DEVICE.type == "cuda" and (b // recall_batch) % 16 == 0:
            torch.cuda.synchronize()
    return logits_out


def softmax_with_temperature_np(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = logits / max(temperature, 1e-6)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_bpc(sub_logp: np.ndarray, U_log: np.ndarray, nxt: np.ndarray,
                           lam: float) -> float:
    """BPC with log-linear interp p(t) propto exp(lam * log p_sub + (1-lam) * log p_uni)."""
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    logp = combined - Z[:, None]
    logp_nxt = logp[np.arange(len(nxt)), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def bpc_arm(E: torch.Tensor, idx_train: np.ndarray, idx_held: np.ndarray,
             U_log: np.ndarray, lambda_grid: list) -> Dict:
    """Build fresh W on GPU; sweep lambda on dev half; report test BPC at best lambda."""
    V = E.shape[0]
    unk = 0
    # Build fresh W
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    t0 = time.time()
    W = build_fresh_hebbian_W_gpu(idx_train_t, E, INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0
    # Eval split (50/50 of held: dev for lambda, test for report)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    ctx_eval = ctx[mask]
    nxt_eval = nxt[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        del W
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {"bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": 1.0, "bpc_per_lambda_test": {}, "n_test": 0,
                "n_dev": 0, "wall_ingest_s": t_ingest, "wall_recall_s": 0.0}
    n_dev = n_eval // 2
    ctx_dev = ctx_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)
    # Substrate logits on dev + test
    t0 = time.time()
    sub_logits_dev = compute_substrate_logits_gpu(E, W, ctx_dev, RECALL_BATCH)
    sub_logits_test = compute_substrate_logits_gpu(E, W, ctx_test, RECALL_BATCH)
    t_recall = time.time() - t0
    sub_probs_dev = softmax_with_temperature_np(sub_logits_dev, temperature=1.0)
    sub_probs_test = softmax_with_temperature_np(sub_logits_test, temperature=1.0)
    sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
    sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))
    # raw BPC at lambda=1.0 (pure substrate) on test
    raw_logp_nxt = sub_logp_test[np.arange(n_test), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt)) / math.log(2.0)
    # sweep lambda on dev; record test BPC at every lambda for transparency
    best_lambda = 1.0
    best_dev_bpc = float("inf")
    bpc_per_lambda_dev: Dict[float, float] = {}
    bpc_per_lambda_test: Dict[float, float] = {}
    for lam in lambda_grid:
        bpc_dev = log_linear_interp_bpc(sub_logp_dev, U_log, nxt_dev, lam)
        bpc_per_lambda_dev[lam] = bpc_dev
        bpc_test = log_linear_interp_bpc(sub_logp_test, U_log, nxt_test, lam)
        bpc_per_lambda_test[lam] = bpc_test
        if bpc_dev < best_dev_bpc:
            best_dev_bpc = bpc_dev
            best_lambda = lam
    bpc_best_test = bpc_per_lambda_test[best_lambda]
    # Free GPU
    del W, idx_train_t
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best": round(bpc_best_test, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "bpc_per_lambda_dev": {str(k): round(v, 4) for k, v in bpc_per_lambda_dev.items()},
        "bpc_per_lambda_test": {str(k): round(v, 4) for k, v in bpc_per_lambda_test.items()},
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


def bpc_unigram(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
    """Analytic unigram baseline BPC on test half of held."""
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    p_true = U[nxt_test].clip(1e-12, 1.0)
    nll = float(-np.mean(np.log(p_true)))
    return {"bpc_unigram": round(nll / math.log(2.0), 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Per-seed runner: build fresh W per arm; record BPC per arm
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 corpus + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d vs %d" % (len(toks), N_TRAIN + N_HELD), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    # Build unigram log for log-linear interp
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    # ARM_UNIGRAM
    uni = bpc_unigram(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc_unigram=%.3f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": {"bpc_unigram": uni["bpc_unigram"],
                                                  "n_test": uni["n_test"]}}

    for arm_label in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] building fresh E (vocab=%d N_DIM=%d) on %s..." % (
            seed, arm_label, V, N_DIM, str(DEVICE)), flush=True)
        meta = {}
        if arm_label == "ARM_CHAR_TRIGRAM_FRESH_W":
            E = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        else:
            model_name = GENSIM_MODEL_FOR[arm_label]
            E, meta = build_E_pretrained_gpu(vocab, N_DIM, seed, model_name)
        t_enc = time.time() - t_arm
        if DEVICE.type == "cuda":
            try:
                free_b, total_b = torch.cuda.mem_get_info()
                print("    [seed=%d arm=%s] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                    seed, arm_label, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
            except Exception:
                pass

        print("    [seed=%d arm=%s] building FRESH Hebbian W + computing BPC..." % (
            seed, arm_label), flush=True)
        bpc = bpc_arm(E, idx_train, idx_held, U_log, LAMBDA_GRID)
        del E
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        oov_info = ""
        if meta:
            oov_info = " hit/miss=%d/%d" % (meta.get("n_hit", 0), meta.get("n_miss", 0))
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f%s (enc=%.1fs ingest=%.1fs recall=%.1fs)" % (
            seed, arm_label, bpc["bpc_raw"], bpc["bpc_best"], bpc["best_lambda"],
            oov_info, t_enc, bpc["wall_ingest_s"], bpc["wall_recall_s"]), flush=True)
        by_arm[arm_label] = {
            "bpc_raw": bpc["bpc_raw"],
            "bpc_best": bpc["bpc_best"],
            "best_lambda": bpc["best_lambda"],
            "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_per_lambda_dev": bpc["bpc_per_lambda_dev"],
            "bpc_per_lambda_test": bpc["bpc_per_lambda_test"],
            "n_dev": bpc["n_dev"],
            "n_test": bpc["n_test"],
            "wall_encode_s": round(t_enc, 2),
            "wall_ingest_s": bpc["wall_ingest_s"],
            "wall_recall_s": bpc["wall_recall_s"],
            "encoder_meta": meta,
        }

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # aggregate per arm
    by_arm_agg: Dict[str, Dict] = {}
    # ARM_UNIGRAM
    uni_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_vals)), 4),
        "bpc_std": round(float(np.std(uni_vals)), 4),
    }
    # encoder arms
    encoder_arms = [a for a in ARMS if a != "ARM_UNIGRAM"]
    for arm in encoder_arms:
        best_vals = [u["by_arm"].get(arm, {}).get("bpc_best", float("nan")) for u in units]
        raw_vals = [u["by_arm"].get(arm, {}).get("bpc_raw", float("nan")) for u in units]
        lam_vals = [u["by_arm"].get(arm, {}).get("best_lambda", float("nan")) for u in units]
        b_mean = float(np.mean(best_vals))
        b_std = float(np.std(best_vals))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "bpc_raw_mean": round(float(np.mean(raw_vals)), 4),
            "best_lambda_mean": round(float(np.mean(lam_vals)), 4),
        }

    # Compute lift over CHAR_TRIGRAM_FRESH_W
    trigram_mean = by_arm_agg.get("ARM_CHAR_TRIGRAM_FRESH_W", {}).get("bpc_best_mean", float("nan"))
    for arm in encoder_arms:
        m = by_arm_agg[arm]["bpc_best_mean"]
        # lift = trigram_mean - this_mean (positive = better than trigram)
        if math.isfinite(trigram_mean) and math.isfinite(m):
            by_arm_agg[arm]["lift_over_trigram_bits"] = round(trigram_mean - m, 4)
        else:
            by_arm_agg[arm]["lift_over_trigram_bits"] = float("nan")

    # HARD_PASS classification per arm
    semantic_arms = [a for a in encoder_arms if a != "ARM_CHAR_TRIGRAM_FRESH_W"]
    hp_arms = []
    for arm in semantic_arms:
        a = by_arm_agg[arm]
        bpc_ok = a["bpc_best_mean"] < HP_BPC_BAR
        cv_ok = a["bpc_best_cv"] <= HP_BPC_CV_MAX
        lift_ok = (math.isfinite(a.get("lift_over_trigram_bits", float("nan")))
                   and a["lift_over_trigram_bits"] >= HP_LIFT_OVER_TRIGRAM)
        if bpc_ok and cv_ok and lift_ok:
            hp_arms.append(arm)
        a["bpc_ok"] = bool(bpc_ok)
        a["cv_ok"] = bool(cv_ok)
        a["lift_ok"] = bool(lift_ok)
        a["arm_hard_pass"] = bool(bpc_ok and cv_ok and lift_ok)

    all_encoder_arms = encoder_arms
    all_fail = all(by_arm_agg[a]["bpc_best_mean"] >= HF_BPC_BAR for a in all_encoder_arms)
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    parts = []
    for a in encoder_arms:
        b = by_arm_agg[a]
        parts.append("%s=bpc%.3f(lam%.2f,lift%.3f)" % (
            a, b["bpc_best_mean"], b["best_lambda_mean"],
            b.get("lift_over_trigram_bits", float("nan"))))
    summary = "FRESH_W_BPC unigram=%.3f | %s | n_llm=%d" % (
        by_arm_agg["ARM_UNIGRAM"]["bpc_mean"], " | ".join(parts), n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "hard_pass_arms": list(hp_arms),
        "all_encoder_arms_fail_vs_unigram": bool(all_fail),
        "trigram_mean_bpc": trigram_mean,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "hp_bpc_bar": HP_BPC_BAR,
        "hp_lift_over_trigram": HP_LIFT_OVER_TRIGRAM,
        "hf_bpc_bar": HF_BPC_BAR,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Methodology-corrected V2 LM gap test: each of 4 encoder arms builds a "
            "COMPLETELY FRESH Hebbian W from scratch (no shared substrate state, no "
            "char-trigram contamination). N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d. "
            "HARD_PASS = ANY semantic encoder arm clears BPC<%.3f AND lift over "
            "ARM_CHAR_TRIGRAM_FRESH_W >= %.2f bits. HARD_FAIL = ALL encoder arms "
            ">=%.3f (substrate-W bottleneck encoder-invariant)." % (
                N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, HP_BPC_BAR,
                HP_LIFT_OVER_TRIGRAM, HF_BPC_BAR)),
        "cites": [
            "preregs/2026-06-23_fresh_W_bpc_per_encoder_v1.md",
            "experiments/exp_encoder_word2vec_substrate_bind_v1.py",
            "experiments/exp_text8_substrate_pseudoLM_v2_temperature_calibrated_v1.py",
            "USER_2026-06-23_methodology_correction_no_old_W",
            "USER_2026-06-22_GPU_dispatch_must_use_GPU_Fix24",
            "Mikolov_2013_word2vec",
            "Pennington_2014_GloVe",
            "Bojanowski_2017_fastText",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if hp_arms:
        # Sort by best (lowest) bpc
        hp_arms.sort(key=lambda x: by_arm_agg[x]["bpc_best_mean"])
        top = hp_arms[0]
        t = by_arm_agg[top]
        return ("HARD_PASS",
                ("FRESH_W_BPC HARD_PASS: encoder %s clears BPC %.3f < %.3f bar "
                 "(cv=%.3f) AND lift %.3f bits >= %.2f over CHAR_TRIGRAM_FRESH_W "
                 "(%.3f); semantic encoder beats lexical encoder on fresh substrate W; "
                 "V2 LM gap closure decisive evidence; %d HP arm(s) total. %s" % (
                     top, t["bpc_best_mean"], HP_BPC_BAR, t["bpc_best_cv"],
                     t["lift_over_trigram_bits"], HP_LIFT_OVER_TRIGRAM,
                     trigram_mean, len(hp_arms), summary)),
                detail)

    if all_fail:
        return ("HARD_FAIL",
                ("FRESH_W_BPC HARD_FAIL: ALL %d encoder arms have BPC >= unigram %.3f "
                 "with fresh W; substrate Hebbian-rank-1 readout is mathematically "
                 "capped regardless of encoder semantic content; V2 LM gap closure "
                 "rejected at production scale via fresh-W methodology; pivot to "
                 "descope or architectural rewrite. %s" % (
                     len(all_encoder_arms), UNIGRAM_BPC_REF, summary)),
                detail)

    return ("MIDDLE_BAND",
            ("FRESH_W_BPC MIDDLE_BAND: some encoder arms lift over CHAR_TRIGRAM_FRESH_W "
             "but none clear BPC<%.3f AND lift>=%.2f simultaneously; partial "
             "characterization of encoder contribution vs substrate-W bottleneck. %s" % (
                 HP_BPC_BAR, HP_LIFT_OVER_TRIGRAM, summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram encoder produces bipolar L2-normalizable vectors
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0})

    # T2: Gaussian projection JL-scaled
    P = _gaussian_projection(in_dim=300, out_dim=64, seed=0)
    assert P.shape == (64, 300)
    std_P = float(P.std())
    assert 0.04 < std_P < 0.08, "P std %.4f out of range" % std_P

    # T3: build_E_char_trigram_gpu on CPU device shape
    vocab_t = ["w%d" % i for i in range(8)]
    global DEVICE
    _saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        E = build_E_char_trigram_gpu(vocab_t, 64, seed=0)
        assert E.shape == (8, 64), "T3 E shape"
        nrms = E.norm(dim=1).numpy()
        assert np.allclose(nrms, 1.0, atol=1e-5), "T3 E norms"

        # T4: build_fresh_hebbian_W_gpu produces correct shape on CPU
        idx_train_t = torch.from_numpy(np.array([0, 1, 2, 3, 4, 5, 6, 7, 0, 1] * 50, dtype=np.int64))
        W = build_fresh_hebbian_W_gpu(idx_train_t, E, ingest_chunk=8)
        assert W.shape == (64, 64), "T4 W shape"

        # T5: cycle recall sanity (small)
        cycle_vocab = ["tok%d" % i for i in range(10)]
        Ec = build_E_char_trigram_gpu(cycle_vocab, 512, seed=0)
        seq = np.tile(np.arange(10), 5).astype(np.int64)
        seq_t = torch.from_numpy(seq)
        Wc = build_fresh_hebbian_W_gpu(seq_t, Ec, ingest_chunk=8)
        ctx_t = seq_t[:-1]
        pred_vec = Ec[ctx_t] @ Wc.T
        pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
        pred_vec = pred_vec / pn
        logits = pred_vec @ Ec.T
        am = logits.argmax(dim=1).numpy()
        acc = float((am == seq[1:]).mean())
        assert acc >= 0.7, "T5 cycle recall acc=%.3f < 0.7" % acc

        # T6: log-linear endpoints (HANDOFF self-test):
        #   lambda=1.0 -> pure substrate; lambda=0.0 -> pure unigram
        n = 4
        V_t = 5
        sub_probs = np.array([
            [0.6, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.5, 0.2, 0.1, 0.1],
            [0.3, 0.3, 0.2, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.5, 0.2],
        ], dtype=np.float64)
        nxt = np.array([0, 1, 1, 3], dtype=np.int64)
        U_log = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
        sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
        # lambda=1.0 -> reproduce substrate; bpc must equal raw substrate
        bpc_lam1 = log_linear_interp_bpc(sub_logp, U_log, nxt, 1.0)
        raw_logp = sub_logp[np.arange(n), nxt]
        bpc_raw = -float(np.mean(raw_logp)) / math.log(2.0)
        assert abs(bpc_lam1 - bpc_raw) < 1e-6, "T6a lambda=1 != raw substrate; %.6f vs %.6f" % (bpc_lam1, bpc_raw)
        # lambda=0.0 -> reproduce unigram
        bpc_lam0 = log_linear_interp_bpc(sub_logp, U_log, nxt, 0.0)
        U_target = np.exp(U_log - U_log.max())
        U_target = U_target / U_target.sum()
        p_uni_nxt = U_target[nxt].clip(1e-12, 1.0)
        bpc_uni = -float(np.mean(np.log(p_uni_nxt))) / math.log(2.0)
        assert abs(bpc_lam0 - bpc_uni) < 1e-6, "T6b lambda=0 != unigram; %.6f vs %.6f" % (bpc_lam0, bpc_uni)

        # T7: unigram analytic max-class
        idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)
        U = build_unigram_np(idx, V=4, alpha=0.0)
        assert int(np.argmax(U)) == 2

        # T8: pretrained mock-KV pipeline
        class _MockKV:
            def __init__(self, dim=10):
                self.vector_size = dim
                self.key_to_index = {"w0": 0, "w1": 1, "w2": 2}
                self._vecs = np.random.default_rng(0).standard_normal((3, dim)).astype(np.float32)
            def __contains__(self, key):
                return key in self.key_to_index
            def __getitem__(self, key):
                return self._vecs[self.key_to_index[key]]
            def get_vector(self, key, norm=False):
                if key in self.key_to_index:
                    return self._vecs[self.key_to_index[key]]
                raise KeyError(key)
        mock = _MockKV(dim=10)
        E_pre, n_hit, n_miss = _embed_vocab_via_gensim(["w0", "w1", "w2", "OOV"], mock)
        assert n_hit == 3 and n_miss == 1, "T8 hit/miss"
        assert float(np.linalg.norm(E_pre[3])) < 1e-9, "T8 OOV not zero"

        # T9: verdict classification HARD_PASS path
        def _mk_unit(bpc_by_arm, lift_implicit=True):
            by_arm_local = {"ARM_UNIGRAM": {"bpc_unigram": 7.738, "n_test": 100}}
            for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
                bp = bpc_by_arm.get(arm, 8.0)
                by_arm_local[arm] = {
                    "bpc_raw": bp + 0.2, "bpc_best": bp, "best_lambda": 0.5,
                    "best_dev_bpc": bp, "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                    "n_dev": 100, "n_test": 100,
                    "wall_encode_s": 0.1, "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                    "encoder_meta": {},
                }
            return {"seed": 0, "by_arm": by_arm_local, "V": 16, "N": 64, "N_DIM": 64,
                    "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16, "PRETRAIN_DIM": 10,
                    "run_mode": "smoke", "config_version": "selftest", "elapsed_s_seed": 0.01,
                    "device": "cpu", "n_llm_calls": 0}

        # HARD_PASS: word2vec beats unigram with sufficient lift
        u_hp = _mk_unit({"ARM_CHAR_TRIGRAM_FRESH_W": 7.9, "ARM_WORD2VEC_FRESH_W": 7.2,
                         "ARM_GLOVE_FRESH_W": 7.5, "ARM_FASTTEXT_FRESH_W": 7.6})
        v, m, d = compute_verdict([u_hp, u_hp, u_hp])
        assert v == "HARD_PASS", "T9 HARD_PASS got %s msg=%s" % (v, m[:200])
        assert "ARM_WORD2VEC_FRESH_W" in d["hard_pass_arms"], "T9 wrong arm"

        # HARD_FAIL: all encoder arms >= unigram
        u_hf = _mk_unit({"ARM_CHAR_TRIGRAM_FRESH_W": 7.9, "ARM_WORD2VEC_FRESH_W": 7.85,
                         "ARM_GLOVE_FRESH_W": 7.9, "ARM_FASTTEXT_FRESH_W": 7.88})
        v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
        assert v == "HARD_FAIL", "T9 HARD_FAIL got %s msg=%s" % (v, m[:200])

        # MIDDLE_BAND: word2vec beats unigram (7.73 < 7.738) but lift only 0.17 < 0.5
        # (trigram=7.9 - word2vec=7.73 = 0.17 lift; doesn't clear HP_LIFT_OVER_TRIGRAM=0.5);
        # but it does beat unigram so NOT all-fail; -> MIDDLE_BAND
        u_mid = _mk_unit({"ARM_CHAR_TRIGRAM_FRESH_W": 7.9, "ARM_WORD2VEC_FRESH_W": 7.73,
                          "ARM_GLOVE_FRESH_W": 7.74, "ARM_FASTTEXT_FRESH_W": 7.75})
        v, m, _ = compute_verdict([u_mid, u_mid, u_mid])
        assert v == "MIDDLE_BAND", "T9 MIDDLE_BAND got %s msg=%s" % (v, m[:200])

    finally:
        DEVICE = _saved_device

    # T10: counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "T10 LLM counter"

    print("[selftest] PASS: T1 trigram + T2 proj + T3 E shape + T4 W shape + T5 cycle "
          "+ T6 log-linear endpoints (lam=1 raw, lam=0 unigram) + T7 unigram + T8 mock-KV "
          "+ T9 verdict bands HP/HF/MID + T10 llm=0",
          flush=True)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Optional[Path]] = [None]
_T0_REF: List[Optional[float]] = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "PRETRAIN_DIM": PRETRAIN_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_fresh_W_bpc_per_encoder_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
            "device": str(DEVICE),
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
          "seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "fresh-W-bpc-per-encoder-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "LAMBDA_GRID": LAMBDA_GRID,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_fresh_W_bpc_per_encoder_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-native Hebbian W per arm; pretrained encoders are open-weight static lookups; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
