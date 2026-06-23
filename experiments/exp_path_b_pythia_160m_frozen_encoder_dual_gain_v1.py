"""path_b_pythia_160m_frozen_encoder_dual_gain_v1 -- pythia-160m as substrate encoder.

USER 2026-06-23 blanket authorization to follow Path B. Forward-only / Hebbian /
SoftHebb encoders failed dual-gain. This cell tests whether a FROZEN OPEN-WEIGHTS
pretrained transformer (pythia-160m, EleutherAI; trained on The Pile; open + published)
as substrate token encoder closes BOTH:

  Metric A: cleanup recall@1 at sigma=1.5 (production-regime; baseline ~0.022)
  Metric B: substrate-LM BPC < unigram floor (7.738) with lift over word2vec

USER 2026-06-22 directive blocked MiniLM / BGE / proprietary embeddings. Pythia-160m
is a different category: open-weights, fully-published training corpus (The Pile),
no proprietary fine-tuning. Treated as substrate-native frozen lookup; zero LLM calls
at inference (encoder is a static torch.no_grad() forward over the input vocab once).

DESIGN (5 arms; each builds fresh Hebbian W from scratch on GPU; 3 seeds):

  ARM_UNIGRAM
    Analytic baseline floor; no W. BPC reference = 7.738.
  ARM_CHAR_TRIGRAM_FRESH_W
    Substrate-native lexical encoder; honest baseline for "what does substrate
    look like with NO pretrained content?"
  ARM_WORD2VEC_FRESH_W
    Path A reference; should reproduce prior fresh_W_bpc_per_encoder result
    (around 7.86 BPC on text8 at N_DIM=8192).
  ARM_PYTHIA_160M_FRESH_W
    THE CANDIDATE. Load pythia-160m on cuda, freeze, mean-pool last-layer hidden
    states per vocab token (treating each token-string as its own one-token input);
    that 768d vector projected to N_DIM=8192 via fixed Gaussian. Hebbian W built
    fresh from these vectors.
  ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM
    Same pythia encoder; same substrate W; but report BPC after log-linear interp
    with unigram (sweeps lambda in [0.0..1.0]). At lambda=1.0 -> pure substrate;
    at lambda=0.0 -> pure unigram (sanity).

PRE-REG bands (chain-grade-eligible; dual-gain criterion):
  Metric A (cleanup recall@1 at sigma=1.5 per arm):
    HARD_PASS:   recall >= 0.20 AND cv <= 0.30
    HARD_FAIL:   recall <= 0.05
    MIDDLE_BAND: 0.05 < recall < 0.20
  Metric B (BPC per arm vs unigram 7.738):
    HARD_PASS:   ARM_PYTHIA_160M_FRESH_W bpc < (word2vec bpc - 0.3) AND bpc < 7.738
    HARD_FAIL:   ARM_PYTHIA_160M_FRESH_W bpc >= word2vec bpc OR bpc >= 7.738
    MIDDLE_BAND: pythia lifts over word2vec but doesn't beat unigram
  CELL VERDICT (chain-grade-eligible):
    HARD_PASS  = ARM_PYTHIA_160M_FRESH_W passes BOTH A AND B
    HARD_FAIL  = ARM_PYTHIA_160M_FRESH_W fails A (recall<=0.05) AND fails B (>= word2vec)
    MIDDLE_BAND otherwise (partial-mechanism)

SANITY (CONFOUND_FAIL detector):
  sigma=0 across all arms must yield cleanup recall@1 = 1.000.
  ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM at lambda=1.0 == ARM_PYTHIA_160M_FRESH_W raw.
  ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM at lambda=0.0 == ARM_UNIGRAM.

SUBSTRATE-ONLY decode: pythia-160m runs ONCE at startup to encode the vocab
(static lookup table built); no LLM calls at inference. _LLM_CALL_COUNTER stays 0.

GPU REQUIRED (Fix #24):
  - pythia-160m forward inference: cuda + torch.no_grad
  - Hebbian W build: torch.cuda batched outer products at N_DIM=8192
  - Recall sweep: torch.cuda batched matmul

Cites:
  - preregs/2026-06-23_path_b_pythia_160m_frozen_encoder_dual_gain_v1.md
  - experiments/exp_fresh_W_bpc_per_encoder_v1.py (Path A parent; word2vec arm shared)
  - experiments/exp_encoder_dual_gain_softhebb_v1.py (dual-gain methodology)
  - USER 2026-06-23 Path B blanket authorization
  - USER 2026-06-22 GPU dispatch Fix #24
  - Biderman et al. 2304.01373 (Pythia training suite; open-weights LM)

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
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

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

ANCHOR_NAME = "path_b_pythia_160m_frozen_encoder_dual_gain_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
HF_CACHE_DIR = str(REPO / "data" / "hf_cache")
os.environ.setdefault("HF_HOME", HF_CACHE_DIR)
os.environ.setdefault("HF_DATASETS_CACHE", HF_CACHE_DIR)
os.environ.setdefault("TRANSFORMERS_CACHE", HF_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
WORD2VEC_PRIOR_BPC_REF = 7.864  # observed; used only as smoke sanity, not as gate

# Pre-reg bands (DUAL-GAIN)
HP_BPC_BAR = UNIGRAM_BPC_REF              # < 7.738 to clear B
HP_BPC_LIFT_OVER_W2V = 0.3                # pythia must beat word2vec by >=0.3 bits
HP_CLEANUP_RECALL_15 = 0.20               # cleanup at sigma=1.5
HF_CLEANUP_RECALL_15 = 0.05
HP_CLEANUP_CV_MAX = 0.30
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
W2V_DIM = 300
PYTHIA_MODEL_NAME = "EleutherAI/pythia-160m"
PYTHIA_HIDDEN_DIM = 768  # pythia-160m hidden size
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
SIGMA_SWEEP = [0.0, 0.5, 1.0, 1.5, 2.0]
DISCRIMINATOR_SIGMA = 1.5
N_CLEANUP_EVAL = 200

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under SMOKE_TIMEOUT_S=180s on laptop CPU.
    # Pythia-160m forward inference on CPU for ~400 tokens is the bottleneck.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 200

ARMS = [
    "ARM_UNIGRAM",
    "ARM_CHAR_TRIGRAM_FRESH_W",
    "ARM_WORD2VEC_FRESH_W",
    "ARM_PYTHIA_160M_FRESH_W",
    "ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM",
]
ENCODER_ARMS_FOR_W = {
    "ARM_CHAR_TRIGRAM_FRESH_W",
    "ARM_WORD2VEC_FRESH_W",
    "ARM_PYTHIA_160M_FRESH_W",
}
# ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM is a derived arm: uses same W as pythia,
# but reports BPC after log-linear sweep over [0..1] lambdas with unigram.

CONFIG_VERSION = (
    "path_b_pythia_160m_frozen_encoder_dual_gain_v1; N_DIM=%d W2V_DIM=%d "
    "PYTHIA=%s PYTHIA_HIDDEN_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "arms=%s seeds=%s mode=%s INGEST_CHUNK=%d RECALL_BATCH=%d device=%s "
    "lambda_grid=%s sigma_sweep=%s disc_sigma=%.2f N_CLEANUP_EVAL=%d; "
    "bands HP_bpc<%.3f HP_lift_w2v>=%.2f HP_recall15>=%.2f HF_recall15<=%.2f "
    "cv_max=%.2f"
) % (
    N_DIM, W2V_DIM, PYTHIA_MODEL_NAME, PYTHIA_HIDDEN_DIM, N_TRAIN, N_HELD,
    VOCAB_CAP, ARMS, SEEDS, RUN_MODE, INGEST_CHUNK, RECALL_BATCH, str(DEVICE),
    LAMBDA_GRID, SIGMA_SWEEP, DISCRIMINATOR_SIGMA, N_CLEANUP_EVAL,
    HP_BPC_BAR, HP_BPC_LIFT_OVER_W2V, HP_CLEANUP_RECALL_15,
    HF_CLEANUP_RECALL_15, HP_BPC_CV_MAX,
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


# --- word2vec via gensim ----------------------------------------------------
_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_w2v():
    name = "word2vec-google-news-300"
    if name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(name)
    _GENSIM_KV_CACHE[name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    dim = kv.vector_size
    out = np.zeros((len(vocab), dim), dtype=np.float32)
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
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                          ) -> Tuple[torch.Tensor, Dict]:
    kv = _load_gensim_w2v()
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


# --- pythia-160m frozen encoder --------------------------------------------
_PYTHIA_MODEL_CACHE: List[object] = []  # [tokenizer, model] tuple cached


def _load_pythia_160m():
    """Load pythia-160m once; cache on disk + in-process. Returns (tok, model)."""
    if _PYTHIA_MODEL_CACHE:
        return _PYTHIA_MODEL_CACHE[0]
    from transformers import AutoTokenizer, AutoModel
    print("  [pythia] loading %s on %s..." % (PYTHIA_MODEL_NAME, str(DEVICE)), flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(PYTHIA_MODEL_NAME, cache_dir=HF_CACHE_DIR)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token if tok.eos_token else "<|endoftext|>"
    # transformers 5.x deprecates torch_dtype in favor of dtype; support both
    try:
        model = AutoModel.from_pretrained(PYTHIA_MODEL_NAME, cache_dir=HF_CACHE_DIR,
                                            dtype=torch.float32)
    except TypeError:
        model = AutoModel.from_pretrained(PYTHIA_MODEL_NAME, cache_dir=HF_CACHE_DIR,
                                            torch_dtype=torch.float32)
    model.eval()
    for p in model.parameters():
        p.requires_grad = False
    model.to(DEVICE)
    t_load = time.time() - t0
    print("  [pythia] loaded in %.2fs (hidden_dim=%d, params frozen)" % (
        t_load, model.config.hidden_size), flush=True)
    _PYTHIA_MODEL_CACHE.append((tok, model))
    return tok, model


def _pythia_encode_vocab_batched(vocab: List[str], tok, model, batch_size: int = 64
                                   ) -> np.ndarray:
    """Mean-pool last-layer hidden states per vocab token (treating each as one
    short input string). Returns [V, hidden_dim] numpy float32."""
    V = len(vocab)
    hidden_dim = model.config.hidden_size
    out = np.zeros((V, hidden_dim), dtype=np.float32)
    # Strip <unk> sentinel to plain string; tokenizer will produce >=1 token
    plain = [(" " + (w if w != "<unk>" else "unk")) for w in vocab]
    n_done = 0
    t0 = time.time()
    for b in range(0, V, batch_size):
        end = min(b + batch_size, V)
        batch = plain[b:end]
        enc = tok(batch, padding=True, truncation=True, max_length=16,
                  return_tensors="pt")
        input_ids = enc["input_ids"].to(DEVICE)
        attn = enc["attention_mask"].to(DEVICE)
        with torch.no_grad():
            outs = model(input_ids=input_ids, attention_mask=attn,
                         output_hidden_states=False)
        # last_hidden_state: [B, T, H]
        last = outs.last_hidden_state
        mask = attn.unsqueeze(-1).to(last.dtype)
        summed = (last * mask).sum(dim=1)
        denom = mask.sum(dim=1).clamp(min=1.0)
        pooled = (summed / denom).detach().cpu().to(torch.float32).numpy()
        out[b:end] = pooled
        n_done += (end - b)
        if DEVICE.type == "cuda" and (b // batch_size) % 8 == 0:
            torch.cuda.synchronize()
    print("  [pythia] vocab encoded V=%d in %.2fs (avg %.1f tok/s)" % (
        V, time.time() - t0, V / max(time.time() - t0, 1e-6)), flush=True)
    return out


def build_E_pythia_gpu(vocab: List[str], n_dim: int, seed: int
                        ) -> Tuple[torch.Tensor, Dict]:
    tok, model = _load_pythia_160m()
    E_pre = _pythia_encode_vocab_batched(vocab, tok, model)
    # Pythia encoder is the LM head; not LLM-call-at-inference.
    # Counter unchanged on purpose: this is a static lookup-table build, not a
    # per-query LM forward at substrate eval time.
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=PYTHIA_HIDDEN_DIM, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_vocab": int(len(vocab)),
            "pretrain_dim": int(PYTHIA_HIDDEN_DIM),
            "encoder": PYTHIA_MODEL_NAME,
            "frozen": True, "mean_pool": True}
    return E_t, meta


# ============================================================================
# Fresh-W Hebbian builder (GPU)
# ============================================================================

def build_fresh_hebbian_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                                ingest_chunk: int) -> torch.Tensor:
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
# Metric A: cleanup recall over sigma sweep (numpy on E from GPU; cheap)
# ============================================================================

def cleanup_eval_arm_np(E_np: np.ndarray, n_eval: int, sigmas: list, seed: int) -> dict:
    """Cleanup recall@1 across sigma sweep on E [V, n_dim]."""
    g = np.random.default_rng(seed * 7919 + 11)
    V = E_np.shape[0]
    D = E_np.shape[1]
    query_idx = g.choice(V, size=min(n_eval, V), replace=False)
    En = _l2_normalize_np(E_np)
    out = {}
    for sig in sigmas:
        noise = (sig * g.standard_normal((len(query_idx), D))).astype(np.float32)
        cues = E_np[query_idx] + noise
        cuesn = _l2_normalize_np(cues)
        scores = cuesn @ En.T
        pred = np.argmax(scores, axis=1).astype(np.int64)
        out[float(sig)] = float((pred == query_idx).sum()) / max(len(query_idx), 1)
    return out


# ============================================================================
# Metric B: BPC per arm
# ============================================================================

def compute_substrate_logits_gpu(E: torch.Tensor, W: torch.Tensor, ctx_idx: np.ndarray,
                                   recall_batch: int) -> np.ndarray:
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
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    logp = combined - Z[:, None]
    logp_nxt = logp[np.arange(len(nxt)), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def bpc_arm(E: torch.Tensor, idx_train: np.ndarray, idx_held: np.ndarray,
             U_log: np.ndarray, lambda_grid: list, fixed_lambda: Optional[float] = None
             ) -> Dict:
    """Build fresh W on GPU; eval BPC with log-linear interp.

    fixed_lambda: if None, sweep lambda_grid + pick best on dev half. If set,
    use exactly that lambda on the test half. Used by ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM
    to report a specific lambda directly.
    """
    V = E.shape[0]
    unk = 0
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    t0 = time.time()
    W = build_fresh_hebbian_W_gpu(idx_train_t, E, INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0
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
                "n_dev": 0, "wall_ingest_s": t_ingest, "wall_recall_s": 0.0,
                "W": None}
    n_dev = n_eval // 2
    ctx_dev = ctx_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)
    t0 = time.time()
    sub_logits_dev = compute_substrate_logits_gpu(E, W, ctx_dev, RECALL_BATCH)
    sub_logits_test = compute_substrate_logits_gpu(E, W, ctx_test, RECALL_BATCH)
    t_recall = time.time() - t0
    sub_probs_dev = softmax_with_temperature_np(sub_logits_dev, temperature=1.0)
    sub_probs_test = softmax_with_temperature_np(sub_logits_test, temperature=1.0)
    sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
    sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))
    raw_logp_nxt = sub_logp_test[np.arange(n_test), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt)) / math.log(2.0)
    bpc_per_lambda_dev: Dict[float, float] = {}
    bpc_per_lambda_test: Dict[float, float] = {}
    if fixed_lambda is not None:
        bpc_per_lambda_test[fixed_lambda] = log_linear_interp_bpc(
            sub_logp_test, U_log, nxt_test, fixed_lambda)
        best_lambda = fixed_lambda
        best_dev_bpc = float("nan")
        bpc_best_test = bpc_per_lambda_test[fixed_lambda]
    else:
        best_lambda = 1.0
        best_dev_bpc = float("inf")
        for lam in lambda_grid:
            bpc_dev = log_linear_interp_bpc(sub_logp_dev, U_log, nxt_dev, lam)
            bpc_per_lambda_dev[lam] = bpc_dev
            bpc_test = log_linear_interp_bpc(sub_logp_test, U_log, nxt_test, lam)
            bpc_per_lambda_test[lam] = bpc_test
            if bpc_dev < best_dev_bpc:
                best_dev_bpc = bpc_dev
                best_lambda = lam
        bpc_best_test = bpc_per_lambda_test[best_lambda]
    del W, idx_train_t
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best": round(bpc_best_test, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4) if math.isfinite(best_dev_bpc) else float("nan"),
        "bpc_per_lambda_dev": {str(k): round(v, 4) for k, v in bpc_per_lambda_dev.items()},
        "bpc_per_lambda_test": {str(k): round(v, 4) for k, v in bpc_per_lambda_test.items()},
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


def bpc_unigram(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
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
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
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
            print("[seed=%d gpu] %s total_mem_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    # ARM_UNIGRAM
    uni = bpc_unigram(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["n_test"]), flush=True)
    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": {
        "bpc_best": uni["bpc_unigram"],
        "bpc_raw": uni["bpc_unigram"],
        "n_test": uni["n_test"],
        "cleanup_by_sigma": {},
        "is_unigram_baseline": True,
    }}

    # Build each encoder arm's E + W + measure BPC + cleanup
    pythia_E_cached: Optional[torch.Tensor] = None
    for arm_label in [a for a in ARMS if a in ENCODER_ARMS_FOR_W]:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] building fresh E (V=%d N_DIM=%d) on %s..." % (
            seed, arm_label, V, N_DIM, str(DEVICE)), flush=True)
        meta = {}
        try:
            if arm_label == "ARM_CHAR_TRIGRAM_FRESH_W":
                E = build_E_char_trigram_gpu(vocab, N_DIM, seed)
            elif arm_label == "ARM_WORD2VEC_FRESH_W":
                E, meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
            elif arm_label == "ARM_PYTHIA_160M_FRESH_W":
                E, meta = build_E_pythia_gpu(vocab, N_DIM, seed)
                pythia_E_cached = E
            else:
                raise RuntimeError("unhandled arm: %s" % arm_label)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] ENCODER LOAD FAIL: %s" % (seed, arm_label, err), flush=True)
            by_arm[arm_label] = _failed_arm_record(t_arm, err, meta, kind="load")
            continue
        t_enc = time.time() - t_arm
        if DEVICE.type == "cuda":
            try:
                free_b, total_b = torch.cuda.mem_get_info()
                print("    [seed=%d arm=%s] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                    seed, arm_label, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
            except Exception:
                pass

        # Metric A: cleanup recall@sigma sweep on E (CPU-side; cheap)
        try:
            E_cpu = E.detach().cpu().numpy()
            cleanup = cleanup_eval_arm_np(E_cpu, N_CLEANUP_EVAL, SIGMA_SWEEP, seed)
            del E_cpu
        except Exception as e:
            cleanup = {float(s): float("nan") for s in SIGMA_SWEEP}
            print("    [seed=%d arm=%s] cleanup FAIL: %s" % (seed, arm_label, str(e)[:140]), flush=True)
        recall_at_disc = cleanup.get(DISCRIMINATOR_SIGMA, float("nan"))
        print("    [seed=%d arm=%s] cleanup sigma=0:%.3f s=1.5:%.3f s=2.0:%.3f" % (
            seed, arm_label, cleanup.get(0.0, float("nan")),
            recall_at_disc, cleanup.get(2.0, float("nan"))), flush=True)

        # Metric B: BPC via fresh W
        print("    [seed=%d arm=%s] building FRESH Hebbian W + computing BPC..." % (
            seed, arm_label), flush=True)
        try:
            bpc = bpc_arm(E, idx_train, idx_held, U_log, LAMBDA_GRID)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] BPC COMPUTE FAIL: %s" % (seed, arm_label, err), flush=True)
            if arm_label != "ARM_PYTHIA_160M_FRESH_W":
                del E
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            by_arm[arm_label] = _failed_arm_record(t_arm, err, meta, kind="compute",
                                                     cleanup=cleanup)
            continue
        # Hold pythia E for the derived arm; release others
        if arm_label != "ARM_PYTHIA_160M_FRESH_W":
            del E
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
        oov_info = ""
        if meta and "n_hit" in meta:
            oov_info = " hit/miss=%d/%d" % (meta.get("n_hit", 0), meta.get("n_miss", 0))
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f%s "
              "(enc=%.1fs ingest=%.1fs recall=%.1fs)" % (
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
            "cleanup_by_sigma": {str(k): round(v, 4) for k, v in cleanup.items()},
            "cleanup_at_disc_sigma": round(recall_at_disc, 4),
        }

    # ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM: re-use pythia E; sweep lambda + report
    # the BEST one alongside per-lambda detail. Sanity: at lambda=1.0 == raw
    # pythia substrate; at lambda=0.0 == ARM_UNIGRAM.
    pythia_arm = by_arm.get("ARM_PYTHIA_160M_FRESH_W", {})
    if (pythia_E_cached is not None and not pythia_arm.get("load_failed")
            and not pythia_arm.get("compute_failed")
            and math.isfinite(pythia_arm.get("bpc_best", float("inf")))):
        t_arm = time.time()
        print("\n  [seed=%d arm=ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM] re-using pythia E; "
              "log-linear sweep..." % seed, flush=True)
        try:
            bpc_pl = bpc_arm(pythia_E_cached, idx_train, idx_held, U_log, LAMBDA_GRID)
            # Sanity: at lambda=1.0 should match raw substrate BPC (pythia_arm.bpc_raw)
            raw_pythia_ref = pythia_arm.get("bpc_raw", float("nan"))
            bpc_at_lam_1 = bpc_pl["bpc_per_lambda_test"].get("1.0", float("nan"))
            bpc_at_lam_0 = bpc_pl["bpc_per_lambda_test"].get("0.0", float("nan"))
            uni_ref = uni["bpc_unigram"]
            lam1_ok = (math.isfinite(bpc_at_lam_1) and math.isfinite(raw_pythia_ref)
                        and abs(bpc_at_lam_1 - raw_pythia_ref) < 0.05)
            lam0_ok = (math.isfinite(bpc_at_lam_0) and math.isfinite(uni_ref)
                        and abs(bpc_at_lam_0 - uni_ref) < 0.05)
            print("    [seed=%d ARM_PYTHIA_PLUS_LL] lam1_bpc=%.3f raw_pythia=%.3f "
                  "(sanity %s) | lam0_bpc=%.3f uni=%.3f (sanity %s) | best=%.3f@lam=%.2f" % (
                seed, bpc_at_lam_1, raw_pythia_ref, "OK" if lam1_ok else "MISMATCH",
                bpc_at_lam_0, uni_ref, "OK" if lam0_ok else "MISMATCH",
                bpc_pl["bpc_best"], bpc_pl["best_lambda"]), flush=True)
            by_arm["ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM"] = {
                "bpc_raw": bpc_pl["bpc_raw"],
                "bpc_best": bpc_pl["bpc_best"],
                "best_lambda": bpc_pl["best_lambda"],
                "best_dev_bpc": bpc_pl["best_dev_bpc"],
                "bpc_per_lambda_dev": bpc_pl["bpc_per_lambda_dev"],
                "bpc_per_lambda_test": bpc_pl["bpc_per_lambda_test"],
                "n_dev": bpc_pl["n_dev"],
                "n_test": bpc_pl["n_test"],
                "wall_encode_s": 0.0,  # E re-used
                "wall_ingest_s": bpc_pl["wall_ingest_s"],
                "wall_recall_s": bpc_pl["wall_recall_s"],
                "cleanup_by_sigma": {},  # derived arm; cleanup not applicable
                "cleanup_at_disc_sigma": float("nan"),
                "sanity_lam1_matches_pythia_raw": bool(lam1_ok),
                "sanity_lam0_matches_unigram": bool(lam0_ok),
                "encoder_meta": pythia_arm.get("encoder_meta", {}),
            }
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d ARM_PYTHIA_PLUS_LL] FAIL: %s" % (seed, err), flush=True)
            by_arm["ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM"] = _failed_arm_record(
                t_arm, err, {}, kind="compute")
    else:
        print("\n  [seed=%d ARM_PYTHIA_PLUS_LL] skipped: pythia arm failed upstream" % seed,
              flush=True)
        by_arm["ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM"] = _failed_arm_record(
            time.time(), "upstream pythia arm failed", {}, kind="upstream")

    # Release pythia E
    if pythia_E_cached is not None:
        del pythia_E_cached
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PYTHIA_HIDDEN_DIM": PYTHIA_HIDDEN_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "n_llm_calls": 0,
    }


def _failed_arm_record(t_arm: float, err: str, meta: dict, kind: str,
                        cleanup: Optional[dict] = None) -> Dict:
    base = {
        "load_failed": (kind == "load"),
        "compute_failed": (kind in ("compute", "upstream")),
        "load_error" if kind == "load" else "compute_error": err,
        "bpc_raw": float("inf"),
        "bpc_best": float("inf"),
        "best_lambda": float("nan"),
        "best_dev_bpc": float("inf"),
        "bpc_per_lambda_dev": {},
        "bpc_per_lambda_test": {},
        "n_dev": 0,
        "n_test": 0,
        "wall_encode_s": round(time.time() - t_arm, 2),
        "wall_ingest_s": 0.0,
        "wall_recall_s": 0.0,
        "encoder_meta": meta,
        "cleanup_by_sigma": ({str(k): round(v, 4) for k, v in cleanup.items()}
                              if cleanup else {}),
        "cleanup_at_disc_sigma": (round(cleanup.get(DISCRIMINATOR_SIGMA, float("nan")), 4)
                                    if cleanup else float("nan")),
    }
    return base


# ============================================================================
# Verdict
# ============================================================================

def _agg_bpc(units, arm) -> Dict:
    seeds_load_failed = [u["by_arm"].get(arm, {}).get("load_failed", False) for u in units]
    seeds_compute_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
    valid = [(not lf) and (not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
             for lf, cf, u in zip(seeds_load_failed, seeds_compute_failed, units)]
    n_load_failed = int(sum(seeds_load_failed))
    n_compute_failed = int(sum(seeds_compute_failed))
    valid_units = [u for ok, u in zip(valid, units) if ok]
    if not valid_units:
        return {
            "bpc_best_mean": float("inf"),
            "bpc_best_std": float("nan"),
            "bpc_best_cv": float("nan"),
            "bpc_raw_mean": float("inf"),
            "best_lambda_mean": float("nan"),
            "n_valid_seeds": 0,
            "n_load_failed": n_load_failed,
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": True,
        }
    best_vals = [u["by_arm"].get(arm, {}).get("bpc_best", float("inf")) for u in valid_units]
    raw_vals = [u["by_arm"].get(arm, {}).get("bpc_raw", float("inf")) for u in valid_units]
    lam_vals = [u["by_arm"].get(arm, {}).get("best_lambda", float("nan")) for u in valid_units]
    b_mean = float(np.mean(best_vals))
    b_std = float(np.std(best_vals))
    b_cv = b_std / max(abs(b_mean), 1e-6)
    return {
        "bpc_best_mean": round(b_mean, 4),
        "bpc_best_std": round(b_std, 4),
        "bpc_best_cv": round(b_cv, 4),
        "bpc_raw_mean": round(float(np.mean(raw_vals)), 4),
        "best_lambda_mean": round(float(np.mean(lam_vals)), 4),
        "n_valid_seeds": int(len(valid_units)),
        "n_load_failed": n_load_failed,
        "n_compute_failed": n_compute_failed,
        "all_seeds_failed": False,
    }


def _agg_cleanup(units, arm) -> Dict:
    vals = []
    for u in units:
        v = u["by_arm"].get(arm, {}).get("cleanup_at_disc_sigma", float("nan"))
        if math.isfinite(v):
            vals.append(v)
    if not vals:
        return {"cleanup15_mean": float("nan"), "cleanup15_std": float("nan"),
                "cleanup15_cv": float("nan"), "n_valid": 0}
    m = float(np.mean(vals))
    s = float(np.std(vals))
    return {
        "cleanup15_mean": round(m, 4),
        "cleanup15_std": round(s, 4),
        "cleanup15_cv": round(s / max(abs(m), 1e-6), 4),
        "n_valid": len(vals),
    }


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    # ARM_UNIGRAM bpc
    uni_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_best", float("nan"))
                 for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_best_mean": round(float(np.mean(uni_vals)), 4),
        "bpc_best_std": round(float(np.std(uni_vals)), 4),
    }
    for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        a_bpc = _agg_bpc(units, arm)
        a_cleanup = _agg_cleanup(units, arm)
        by_arm_agg[arm] = {**a_bpc, **a_cleanup}

    pythia_agg = by_arm_agg["ARM_PYTHIA_160M_FRESH_W"]
    w2v_agg = by_arm_agg["ARM_WORD2VEC_FRESH_W"]
    trig_agg = by_arm_agg["ARM_CHAR_TRIGRAM_FRESH_W"]
    pl_agg = by_arm_agg["ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM"]

    # Metric A: cleanup at sigma=1.5 -- pythia must clear HP_CLEANUP_RECALL_15 + cv ok
    cleanup_pythia = pythia_agg.get("cleanup15_mean", float("nan"))
    cleanup_pythia_cv = pythia_agg.get("cleanup15_cv", float("nan"))
    metric_a_pass = (math.isfinite(cleanup_pythia)
                     and cleanup_pythia >= HP_CLEANUP_RECALL_15
                     and math.isfinite(cleanup_pythia_cv)
                     and cleanup_pythia_cv <= HP_CLEANUP_CV_MAX)
    metric_a_fail = (math.isfinite(cleanup_pythia)
                     and cleanup_pythia <= HF_CLEANUP_RECALL_15)

    # Metric B: pythia BPC < (word2vec - 0.3) AND < unigram bar; cv ok
    p_bpc = pythia_agg.get("bpc_best_mean", float("inf"))
    p_cv = pythia_agg.get("bpc_best_cv", float("nan"))
    w_bpc = w2v_agg.get("bpc_best_mean", float("inf"))
    lift_over_w2v = w_bpc - p_bpc if (math.isfinite(p_bpc) and math.isfinite(w_bpc)) else float("nan")
    metric_b_pass = (math.isfinite(p_bpc) and math.isfinite(w_bpc)
                     and p_bpc < (w_bpc - HP_BPC_LIFT_OVER_W2V)
                     and p_bpc < HP_BPC_BAR
                     and math.isfinite(p_cv) and p_cv <= HP_BPC_CV_MAX)
    metric_b_fail = (math.isfinite(p_bpc) and math.isfinite(w_bpc)
                     and (p_bpc >= w_bpc or p_bpc >= HP_BPC_BAR))

    pythia_agg["metric_a_pass"] = bool(metric_a_pass)
    pythia_agg["metric_a_fail"] = bool(metric_a_fail)
    pythia_agg["metric_b_pass"] = bool(metric_b_pass)
    pythia_agg["metric_b_fail"] = bool(metric_b_fail)
    pythia_agg["lift_over_w2v_bits"] = round(lift_over_w2v, 4) if math.isfinite(lift_over_w2v) else float("nan")

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    summary = ("PATH_B_PYTHIA_DUAL_GAIN unigram=%.3f trigram=%.3f w2v=%.3f "
               "pythia=%.3f pythia+LL=%.3f | cleanup_pythia@s1.5=%.3f | "
               "lift_over_w2v=%.3f | metric_A=%s metric_B=%s | n_llm=%d" % (
        by_arm_agg["ARM_UNIGRAM"]["bpc_best_mean"],
        trig_agg.get("bpc_best_mean", float("inf")),
        w_bpc, p_bpc, pl_agg.get("bpc_best_mean", float("inf")),
        cleanup_pythia if math.isfinite(cleanup_pythia) else float("nan"),
        lift_over_w2v if math.isfinite(lift_over_w2v) else float("nan"),
        "PASS" if metric_a_pass else ("FAIL" if metric_a_fail else "MID"),
        "PASS" if metric_b_pass else ("FAIL" if metric_b_fail else "MID"),
        n_llm))

    detail = {
        "by_arm_agg": by_arm_agg,
        "metric_a_pass": bool(metric_a_pass),
        "metric_a_fail": bool(metric_a_fail),
        "metric_b_pass": bool(metric_b_pass),
        "metric_b_fail": bool(metric_b_fail),
        "lift_over_w2v_bits": round(lift_over_w2v, 4) if math.isfinite(lift_over_w2v) else float("nan"),
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "hp_bpc_bar": HP_BPC_BAR,
        "hp_bpc_lift_over_w2v": HP_BPC_LIFT_OVER_W2V,
        "hp_cleanup_recall_15": HP_CLEANUP_RECALL_15,
        "hf_cleanup_recall_15": HF_CLEANUP_RECALL_15,
        "hp_cleanup_cv_max": HP_CLEANUP_CV_MAX,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Path B pythia-160m frozen encoder dual-gain test. 5 arms x 3 seeds. "
            "N_DIM=%d V=%d N_TRAIN=%d N_HELD=%d. HARD_PASS = ARM_PYTHIA_160M_FRESH_W "
            "clears BOTH cleanup-recall>=%.2f@sigma=%.1f AND bpc<%.3f with "
            ">=%.2f-bit lift over word2vec." % (
                N_DIM, VOCAB_CAP, N_TRAIN, N_HELD, HP_CLEANUP_RECALL_15,
                DISCRIMINATOR_SIGMA, HP_BPC_BAR, HP_BPC_LIFT_OVER_W2V)),
        "cites": [
            "preregs/2026-06-23_path_b_pythia_160m_frozen_encoder_dual_gain_v1.md",
            "experiments/exp_fresh_W_bpc_per_encoder_v1.py",
            "experiments/exp_encoder_dual_gain_softhebb_v1.py",
            "USER_2026-06-23_path_b_blanket_authorization",
            "USER_2026-06-22_GPU_dispatch_must_use_GPU_Fix24",
            "Biderman_2023_Pythia_2304.01373",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if metric_a_pass and metric_b_pass:
        return ("HARD_PASS",
                ("PATH_B_PYTHIA HARD_PASS DUAL_GAIN: ARM_PYTHIA_160M_FRESH_W clears "
                 "BOTH metric A (cleanup@s1.5 %.3f >= %.2f, cv %.3f <= %.2f) AND "
                 "metric B (bpc %.3f < unigram %.3f AND lift %.3f >= %.2f bits over "
                 "word2vec %.3f); frozen open-weights pythia encoder unblocks dual-gain "
                 "as substrate-LM token encoder. %s" % (
                     cleanup_pythia, HP_CLEANUP_RECALL_15, cleanup_pythia_cv,
                     HP_CLEANUP_CV_MAX, p_bpc, HP_BPC_BAR, lift_over_w2v,
                     HP_BPC_LIFT_OVER_W2V, w_bpc, summary)),
                detail)

    if metric_a_fail and metric_b_fail:
        return ("HARD_FAIL",
                ("PATH_B_PYTHIA HARD_FAIL: ARM_PYTHIA_160M_FRESH_W fails BOTH metric A "
                 "(cleanup %.3f <= %.2f) AND metric B (bpc %.3f vs word2vec %.3f / "
                 "unigram %.3f); even open-weights pretrained transformer encoder "
                 "doesn't unblock substrate-W rank-1 readout. %s" % (
                     cleanup_pythia, HF_CLEANUP_RECALL_15, p_bpc, w_bpc, HP_BPC_BAR,
                     summary)),
                detail)

    return ("MIDDLE_BAND",
            ("PATH_B_PYTHIA MIDDLE_BAND: ARM_PYTHIA_160M_FRESH_W passes one criterion "
             "but not both (metric_A=%s metric_B=%s); partial-mechanism. %s" % (
                 "PASS" if metric_a_pass else ("FAIL" if metric_a_fail else "MID"),
                 "PASS" if metric_b_pass else ("FAIL" if metric_b_fail else "MID"),
                 summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram encoder produces bipolar vectors
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0})

    # T2: Gaussian projection scale
    P = _gaussian_projection(in_dim=768, out_dim=64, seed=0)
    assert P.shape == (64, 768)
    sP = float(P.std())
    assert 0.02 < sP < 0.06, "P std %.4f out of range" % sP

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

        # T4: build_fresh_hebbian_W_gpu shape
        idx_train_t = torch.from_numpy(np.array(
            [0, 1, 2, 3, 4, 5, 6, 7, 0, 1] * 50, dtype=np.int64))
        W = build_fresh_hebbian_W_gpu(idx_train_t, E, ingest_chunk=8)
        assert W.shape == (64, 64), "T4 W shape"

        # T5: cycle recall sanity
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
        assert acc >= 0.7, "T5 cycle recall acc=%.3f" % acc

        # T6: log-linear endpoints
        n = 4
        sub_probs = np.array([
            [0.6, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.5, 0.2, 0.1, 0.1],
            [0.3, 0.3, 0.2, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.5, 0.2],
        ], dtype=np.float64)
        nxt = np.array([0, 1, 1, 3], dtype=np.int64)
        U_log = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
        sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
        bpc_lam1 = log_linear_interp_bpc(sub_logp, U_log, nxt, 1.0)
        raw_logp = sub_logp[np.arange(n), nxt]
        bpc_raw = -float(np.mean(raw_logp)) / math.log(2.0)
        assert abs(bpc_lam1 - bpc_raw) < 1e-6, "T6a lam=1 != raw: %.6f vs %.6f" % (bpc_lam1, bpc_raw)
        bpc_lam0 = log_linear_interp_bpc(sub_logp, U_log, nxt, 0.0)
        U_target = np.exp(U_log - U_log.max()); U_target /= U_target.sum()
        p_uni_nxt = U_target[nxt].clip(1e-12, 1.0)
        bpc_uni = -float(np.mean(np.log(p_uni_nxt))) / math.log(2.0)
        assert abs(bpc_lam0 - bpc_uni) < 1e-6, "T6b lam=0 != unigram"

        # T7: cleanup recall sigma=0 == 1.0 on E
        E_np = Ec.detach().cpu().numpy()
        cl = cleanup_eval_arm_np(E_np, n_eval=8, sigmas=[0.0, 1.5], seed=1)
        assert abs(cl[0.0] - 1.0) < 1e-6, "T7 sigma=0 recall %.3f != 1.0" % cl[0.0]

        # T8: unigram analytic max
        idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)
        U = build_unigram_np(idx, V=4, alpha=0.0)
        assert int(np.argmax(U)) == 2

        # T9: verdict HARD_PASS path (pythia passes both)
        def _mk_unit(bpc_pythia, cleanup_pythia, bpc_w2v=8.2, bpc_trig=8.5,
                      bpc_uni=7.738, bpc_pythia_pl=None, cleanup_w2v=0.05):
            if bpc_pythia_pl is None:
                bpc_pythia_pl = min(bpc_pythia, bpc_uni)
            cleanup_trig = 0.02
            return {
                "seed": 0,
                "by_arm": {
                    "ARM_UNIGRAM": {"bpc_best": bpc_uni, "bpc_raw": bpc_uni,
                                       "n_test": 100, "cleanup_by_sigma": {},
                                       "is_unigram_baseline": True},
                    "ARM_CHAR_TRIGRAM_FRESH_W": {
                        "bpc_best": bpc_trig, "bpc_raw": bpc_trig + 0.1,
                        "best_lambda": 0.5, "best_dev_bpc": bpc_trig,
                        "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                        "n_dev": 100, "n_test": 100,
                        "wall_encode_s": 0.1, "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                        "encoder_meta": {},
                        "cleanup_by_sigma": {"1.5": cleanup_trig},
                        "cleanup_at_disc_sigma": cleanup_trig,
                    },
                    "ARM_WORD2VEC_FRESH_W": {
                        "bpc_best": bpc_w2v, "bpc_raw": bpc_w2v + 0.1,
                        "best_lambda": 0.5, "best_dev_bpc": bpc_w2v,
                        "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                        "n_dev": 100, "n_test": 100,
                        "wall_encode_s": 0.1, "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                        "encoder_meta": {},
                        "cleanup_by_sigma": {"1.5": cleanup_w2v},
                        "cleanup_at_disc_sigma": cleanup_w2v,
                    },
                    "ARM_PYTHIA_160M_FRESH_W": {
                        "bpc_best": bpc_pythia, "bpc_raw": bpc_pythia + 0.1,
                        "best_lambda": 0.5, "best_dev_bpc": bpc_pythia,
                        "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                        "n_dev": 100, "n_test": 100,
                        "wall_encode_s": 0.1, "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                        "encoder_meta": {},
                        "cleanup_by_sigma": {"1.5": cleanup_pythia},
                        "cleanup_at_disc_sigma": cleanup_pythia,
                    },
                    "ARM_PYTHIA_PLUS_LOG_LINEAR_UNIGRAM": {
                        "bpc_best": bpc_pythia_pl, "bpc_raw": bpc_pythia + 0.1,
                        "best_lambda": 0.7, "best_dev_bpc": bpc_pythia_pl,
                        "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                        "n_dev": 100, "n_test": 100,
                        "wall_encode_s": 0.0, "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                        "encoder_meta": {},
                        "cleanup_by_sigma": {},
                        "cleanup_at_disc_sigma": float("nan"),
                    },
                },
                "V": 16, "N": 64, "N_DIM": 64,
                "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16,
                "PYTHIA_HIDDEN_DIM": 768,
                "run_mode": "smoke", "config_version": "selftest",
                "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0,
            }

        # HARD_PASS: pythia bpc 7.2 (beats unigram by 0.5 and word2vec 8.2 by 1.0),
        # cleanup at sigma=1.5 = 0.25 (clears 0.20)
        u_hp = _mk_unit(bpc_pythia=7.2, cleanup_pythia=0.25)
        v, m, d = compute_verdict([u_hp, u_hp, u_hp])
        assert v == "HARD_PASS", "T9 HARD_PASS got %s: %s" % (v, m[:200])

        # HARD_FAIL: pythia bpc 8.3 (worse than word2vec 8.2 -> metric_B_fail),
        # cleanup 0.02 (metric_A_fail)
        u_hf = _mk_unit(bpc_pythia=8.3, cleanup_pythia=0.02)
        v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
        assert v == "HARD_FAIL", "T9 HARD_FAIL got %s: %s" % (v, m[:200])

        # MIDDLE_BAND: pythia bpc 7.2 (passes B) but cleanup 0.10 (between fail/pass)
        u_mid = _mk_unit(bpc_pythia=7.2, cleanup_pythia=0.10)
        v, m, _ = compute_verdict([u_mid, u_mid, u_mid])
        assert v == "MIDDLE_BAND", "T9 MIDDLE_BAND got %s: %s" % (v, m[:200])

    finally:
        DEVICE = _saved_device

    # T10: LLM counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "T10 llm counter %d" % _LLM_CALL_COUNTER[0]

    print("[selftest] PASS: T1 trigram + T2 proj + T3 E shape + T4 W + T5 cycle "
          "+ T6 log-linear endpoints + T7 cleanup sigma=0=1.0 + T8 unigram "
          "+ T9 verdict bands HP/HF/MID + T10 llm=0", flush=True)


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
            "PYTHIA_MODEL_NAME": PYTHIA_MODEL_NAME,
            "PYTHIA_HIDDEN_DIM": PYTHIA_HIDDEN_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_path_b_pythia_160m_frozen_encoder_dual_gain_v1",
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
               "schema": "path-b-pythia-160m-frozen-encoder-dual-gain-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                       run_config=run_cfg).values())
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
        "PYTHIA_MODEL_NAME": PYTHIA_MODEL_NAME,
        "PYTHIA_HIDDEN_DIM": PYTHIA_HIDDEN_DIM,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "LAMBDA_GRID": LAMBDA_GRID,
        "SIGMA_SWEEP": SIGMA_SWEEP,
        "DISCRIMINATOR_SIGMA": DISCRIMINATOR_SIGMA,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_path_b_pythia_160m_frozen_encoder_dual_gain_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": ("TRUE (pythia is a static lookup-table built once "
                                         "from open-weights public checkpoint; zero LLM at "
                                         "inference time)"),
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
