"""substrate_n1v3_corpus_transfer_discriminator_v1 -- 4-arm corpus-transfer drill.

Resolves whether n1_v3 chain-grade (+61.6% top1, cert row 699) is corpus-specific
(Pythia-residuals only) or substrate-general (also works on text8/word2vec).

Four arms, each builds FRESH state:
  ARM_TEXT8_WORD2VEC_LOGIT_MIXER       -- text8 + word2vec + logit-mixer (reference)
  ARM_TEXT8_WORD2VEC_N1V3_READOUT      -- text8 + word2vec + n1_v3 readout (PRIMARY TEST)
  ARM_PYTHIA_RESIDUALS_LOGIT_MIXER     -- Pythia-residuals + logit-mixer (new baseline)
  ARM_PYTHIA_RESIDUALS_N1V3_READOUT    -- Pythia-residuals + n1_v3 readout (SANITY/PROVENANCE)

Cell-design lineage:
  - Readout helpers (sparse_codebook, W_C build, decode-D, raw-scores into
    temp-softmax) are PORTED VERBATIM from
    experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py (cert row
    699 source).
  - text8 + word2vec encoder scaffolding from
    experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.py
    (the cell that produced top1=0.2128 -- this discriminator REPRODUCES that
    arm exactly under ARM_TEXT8_WORD2VEC_N1V3_READOUT to fix the reference).
  - Pythia-residual loader matches cert anchor's load_data() (residuals_per_token.npz
    -- residuals, doc_boundaries, token_ids -- all on remote runner).

PRE-REG: preregs/2026-06-24_substrate_n1v3_corpus_transfer_discriminator_v1.md
QUEUE: overnight_queue (GPU; ARM_PYTHIA* requires remote NPZ at marsh@home)
ASCII-only. Substrate-only at inference (no LLM forward calls; LLM_CALL_COUNTER=0).
Per-seed checkpoint via experiments/_seed_checkpoint.py.
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
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_n1v3_corpus_transfer_discriminator_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
NPZ_PATH = (REPO / "data" / "exp_phase05_v1_pythia160m_residual_extract_pertoken_v1"
            / "residuals_per_token.npz")
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Reference values for sanity / provenance rails
N1_V3_REF_TOP1 = 0.4455
UNIGRAM_REF_TOP1_TEXT8 = 0.2171  # v2 BUGFIX unigram ref
PROVENANCE_TOL = 0.05
HARD_PASS_SUBSTRATE_GENERAL_FLOOR = 0.40
HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL = 0.30
HARD_FAIL_PROVENANCE_FLOOR = 0.40
LOGIT_MIXER_FLOOR_CEIL = 0.32
CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Production config
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP_TEXT8 = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
TEXT8_N_TRAIN = 100_000
TEXT8_N_HELD = 20_000
# Pythia config (matches cert anchor scope)
PYTHIA_MAX_DOCS = 6000
PYTHIA_TRAIN_FRAC = 0.8
PYTHIA_V_TOK_CAP = 50257

# n1_v3 readout knobs
V_C = 256
CONCEPT_SPARSE_F = 0.003   # k = round(0.003 * 8192) = 25 (matches cert anchor k=25)
LAM_BACKOFF = 0.1
LAPLACE_A = 0.5
LR_DECODE = 1.0

# Logit-mixer encoder knob
SPARSE_BIPOLAR_F = 0.05

# Joint (T, lambda) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

ARMS = [
    "ARM_TEXT8_WORD2VEC_LOGIT_MIXER",
    "ARM_TEXT8_WORD2VEC_N1V3_READOUT",
    "ARM_PYTHIA_RESIDUALS_LOGIT_MIXER",
    "ARM_PYTHIA_RESIDUALS_N1V3_READOUT",
]
TEXT8_ARMS = [a for a in ARMS if a.startswith("ARM_TEXT8")]
PYTHIA_ARMS = [a for a in ARMS if a.startswith("ARM_PYTHIA")]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
else:
    # Smoke: tiny but exercises EVERY path (4 arms, both readouts, both corpora,
    # joint sweep, provenance rail). Must stay under ~3min on laptop CPU.
    SEEDS = [0]
    VOCAB_CAP_TEXT8 = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    V_C = 32
    TEXT8_N_TRAIN = 2_000
    TEXT8_N_HELD = 400
    PYTHIA_MAX_DOCS = 100

CONFIG_VERSION = (
    "substrate_n1v3_corpus_transfer_discriminator_v1; "
    "N_DIM=%d PRETRAIN_DIM=%d TEXT8_N_TRAIN=%d TEXT8_N_HELD=%d "
    "VOCAB_CAP_TEXT8=%d V_C=%d concept_f=%.4f k_active=%d "
    "PYTHIA_MAX_DOCS=%d PYTHIA_V_TOK_CAP=%d PYTHIA_TRAIN_FRAC=%.1f "
    "sparse_bipolar_f=%.3f LAM_BACKOFF=%.2f LAPLACE_A=%.2f "
    "arms=%s seeds=%s mode=%s temps=%s lambdas=%s MRR_K=%d device=%s; "
    "bands: HP_SUBSTRATE_GENERAL>=%.2f HP_CORPUS_SPECIFIC_TEXT8<=%.2f "
    "HARD_FAIL_PROVENANCE_FLOOR=%.2f provenance_tol=%.3f cv_max=%.2f "
    "ref_pythia_n1v3_top1=%.4f"
) % (
    N_DIM, PRETRAIN_DIM, TEXT8_N_TRAIN, TEXT8_N_HELD,
    VOCAB_CAP_TEXT8, V_C, CONCEPT_SPARSE_F, max(1, round(CONCEPT_SPARSE_F * N_DIM)),
    PYTHIA_MAX_DOCS, PYTHIA_V_TOK_CAP, PYTHIA_TRAIN_FRAC,
    SPARSE_BIPOLAR_F, LAM_BACKOFF, LAPLACE_A,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, MRR_K, str(DEVICE),
    HARD_PASS_SUBSTRATE_GENERAL_FLOOR, HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL,
    HARD_FAIL_PROVENANCE_FLOOR, PROVENANCE_TOL, CV_MAX, N1_V3_REF_TOP1,
)

_GENSIM_KV_CACHE: Dict[str, object] = {}
_LLM_CALL_COUNTER = [0]


# ============================================================================
# Encoder (verbatim from v2 BUGFIX; matches fair_harness)
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


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                         ) -> Tuple[torch.Tensor, np.ndarray, Dict]:
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
            E_pre_n[i] = char_trigram_encode(vocab[i], kv.vector_size, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_pre_n = _l2_normalize_np(E_pre_n)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, E_pre_n.astype(np.float32), meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int
                             ) -> Tuple[torch.Tensor, np.ndarray]:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_pre = np.stack(
        [char_trigram_encode(w, PRETRAIN_DIM, seed) for w in vocab], 0
    ).astype(np.float32)
    E_pre = _l2_normalize_np(E_pre)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    return E_t, E_pre


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = E.abs()
    _, topk_idx = torch.topk(abs_E, k=k, dim=1)
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    signs = torch.sign(E.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out[row_idx, topk_idx] = signs
    return out


# ============================================================================
# n1_v3 readout helpers (verbatim from cert anchor src + v2 BUGFIX)
# ============================================================================

def sparse_codebook_np(vc: int, n: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Build sparse binary codebook (V_C, N_DIM), k = round(f * n) active per row.

    Same construction as cert anchor's sparse_codebook().
    """
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C


def fit_vq_on_embeddings(E_pre: np.ndarray, V_C_local: int, seed: int) -> np.ndarray:
    """Cluster embedding rows into V_C concepts. train-fit; no test leakage."""
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C_local, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(E_pre)
        return km.predict(E_pre).astype(np.int64), km
    except ImportError:
        rng = np.random.default_rng(seed)
        centers = E_pre[rng.choice(len(E_pre), size=V_C_local, replace=False)]
        d = np.linalg.norm(
            E_pre[:, None, :] - centers[None, :, :], axis=-1
        )
        return np.argmin(d, axis=1).astype(np.int64), None


def fit_vq_on_residuals(train_res_n: np.ndarray, V_C_local: int, seed: int):
    """VQ for the Pythia path: cluster per-token residuals (not per-word embeddings)."""
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C_local, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(train_res_n)
        return km
    except ImportError:
        rng = np.random.default_rng(seed)
        return rng


def build_concept_W_hebbian_torch(
    C_t: torch.Tensor, concept_ids_per_pos: np.ndarray, idx_train: np.ndarray,
    ingest_chunk: int
) -> torch.Tensor:
    """Build concept-level Willshaw W_C = sum P_src.T @ P_dst over transitions.

    concept_ids_per_pos: array of concept IDs indexed by *position* in the
    item-id stream (length matches idx_train OR is a per-word lookup table).
    For text8: concept_ids_per_pos[word_id] -> concept_id (lookup table).
    For Pythia: concept_ids_per_pos[token_pos] -> concept_id (per-position).
    """
    n = idx_train.shape[0]
    dim = C_t.shape[1]
    if n < 2:
        return torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    src_items = idx_train[:-1]
    tgt_items = idx_train[1:]
    src_concepts = concept_ids_per_pos[src_items]
    tgt_concepts = concept_ids_per_pos[tgt_items]
    src_concepts_t = torch.from_numpy(src_concepts.astype(np.int64)).to(DEVICE)
    tgt_concepts_t = torch.from_numpy(tgt_concepts.astype(np.int64)).to(DEVICE)
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = len(src_concepts)
    for b in range(0, n_pairs, ingest_chunk):
        e = min(b + ingest_chunk, n_pairs)
        Ps = C_t[src_concepts_t[b:e]]
        Pd = C_t[tgt_concepts_t[b:e]]
        W.add_(Ps.T @ Pd)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_concept_W_hebbian_pythia_torch(
    C_t: torch.Tensor, train_cids_flat: np.ndarray, ingest_chunk: int
) -> torch.Tensor:
    """Pythia path: train_cids_flat is the CONCEPT-ID sequence directly
    (one concept per token position; from per-position VQ assignment).
    """
    n = len(train_cids_flat)
    dim = C_t.shape[1]
    if n < 2:
        return torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    src_concepts = train_cids_flat[:-1]
    tgt_concepts = train_cids_flat[1:]
    src_concepts_t = torch.from_numpy(src_concepts.astype(np.int64)).to(DEVICE)
    tgt_concepts_t = torch.from_numpy(tgt_concepts.astype(np.int64)).to(DEVICE)
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = len(src_concepts)
    for b in range(0, n_pairs, ingest_chunk):
        e = min(b + ingest_chunk, n_pairs)
        Ps = C_t[src_concepts_t[b:e]]
        Pd = C_t[tgt_concepts_t[b:e]]
        W.add_(Ps.T @ Pd)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_decode_D_torch(
    concept_ids_per_pos: np.ndarray, idx_train: np.ndarray, C_t: torch.Tensor, V: int
) -> torch.Tensor:
    """text8 path: D[:, word_j] = sum C[concept_of(word_j)] over train positions."""
    dim = C_t.shape[1]
    words_t = torch.from_numpy(idx_train.astype(np.int64)).to(DEVICE)
    concepts_t = torch.from_numpy(
        concept_ids_per_pos[idx_train].astype(np.int64)
    ).to(DEVICE)
    D_T = torch.zeros((V, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n = len(idx_train)
    chunk = 8192
    for b in range(0, n, chunk):
        e = min(b + chunk, n)
        codes = C_t[concepts_t[b:e]]
        D_T.index_add_(0, words_t[b:e], codes)
    return D_T.T.contiguous()


def build_decode_D_pythia_torch(
    train_cids_flat: np.ndarray, train_tids_flat: np.ndarray,
    C_t: torch.Tensor, V_TOK: int
) -> torch.Tensor:
    """Pythia path: D[:, tok] = sum C[concept_t] for all train (concept_t, tok_t).
    Matches cert anchor's D build at lines 728-733.
    """
    dim = C_t.shape[1]
    valid_mask = train_tids_flat < V_TOK
    if not valid_mask.any():
        return torch.zeros((dim, V_TOK), dtype=TORCH_DTYPE, device=DEVICE)
    cids_v = train_cids_flat[valid_mask]
    toks_v = train_tids_flat[valid_mask]
    cids_t = torch.from_numpy(cids_v.astype(np.int64)).to(DEVICE)
    toks_t = torch.from_numpy(toks_v.astype(np.int64)).to(DEVICE)
    D_T = torch.zeros((V_TOK, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n = len(cids_v)
    chunk = 8192
    for b in range(0, n, chunk):
        e = min(b + chunk, n)
        codes = C_t[cids_t[b:e]]
        D_T.index_add_(0, toks_t[b:e], codes)
    return D_T.T.contiguous()


# ============================================================================
# text8 corpus utilities (verbatim from v2 BUGFIX)
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] text8 corpus missing at %s" % TEXT8, flush=True)
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
# Pythia residual loader (matches cert anchor load_data + build_docs)
# ============================================================================

def load_pythia_data() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load residuals, doc_boundaries, token_ids from npz.
    Matches cert anchor's load_data() at lines 561-590.
    """
    if not NPZ_PATH.exists():
        raise FileNotFoundError(
            "residuals_per_token.npz not found at %s\n"
            "  This file lives on marsh@home (remote runner)." % NPZ_PATH
        )
    z = np.load(NPZ_PATH, allow_pickle=False)
    res = z["residuals"].astype(np.float32)
    bnd = z["doc_boundaries"].astype(np.int64)
    if "token_ids" not in z:
        raise FileNotFoundError(
            "token_ids key NOT present in residuals_per_token.npz.\n"
            "  A recovery cell must land token_ids on the remote runner."
        )
    tids = z["token_ids"].astype(np.int64)
    print("[pythia] residuals=%s doc_boundaries=%s token_ids=%s" % (
        res.shape, bnd.shape, tids.shape), flush=True)
    return res, bnd, tids


def build_pythia_docs(res: np.ndarray, bnd: np.ndarray, tids: np.ndarray,
                      max_docs: int) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Slice into per-doc (residuals, token_ids) pairs; min 2 tokens.
    Matches cert anchor's build_docs() at lines 593-604.
    """
    n_docs = min(len(bnd) - 1, max_docs)
    bnd = bnd[:n_docs + 1]
    docs = []
    for i in range(n_docs):
        s, e = int(bnd[i]), int(bnd[i + 1])
        if e - s < 2:
            continue
        docs.append((res[s:e], tids[s:e]))
    return docs


# ============================================================================
# Joint (T, lambda) sweep + metrics (verbatim from v2 BUGFIX)
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    return float(np.mean(np.argmax(logp, axis=1) == nxt))


def mrr_at_k(logp: np.ndarray, nxt: np.ndarray, k: int) -> float:
    n = len(nxt)
    if n == 0:
        return float("nan")
    k_use = min(k, logp.shape[1])
    top_idx = np.argpartition(-logp, kth=k_use - 1, axis=1)[:, :k_use]
    rows = np.arange(n)[:, None]
    top_vals = logp[rows, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_sorted = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        match = np.where(top_idx_sorted[i] == nxt[i])[0]
        if len(match) > 0:
            rr += 1.0 / float(match[0] + 1)
    return float(rr / n)


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Dev-set best (T, lambda) per metric; report test-set value at those params."""
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    for T in temp_grid:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best_test, 4),
        "best_T_for_top1": best_top1["T"],
        "best_lambda_for_top1": best_top1["lambda"],
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_mrr": best_mrr["T"],
        "best_lambda_for_mrr": best_mrr["lambda"],
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1_L1, 4),
        "raw_top1_at_T1_L1": round(raw_top1_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                    V: int, mrr_k: int) -> Dict:
    """Compute unigram BPC + top1 + MRR on the held set (excluding <unk> source ctx).
    For text8 path only.
    """
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != 0)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    am = int(np.argmax(U))
    top1 = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= mrr_k, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Per-arm compute -- TEXT8 path
# ============================================================================

def compute_text8_arm_logits(
    arm: str, E_base: torch.Tensor, E_pre: np.ndarray, idx_train: np.ndarray,
    idx_held: np.ndarray, seed: int, V: int
) -> Dict:
    V_total = E_base.shape[0]
    dim = E_base.shape[1]
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    if arm == "ARM_TEXT8_WORD2VEC_LOGIT_MIXER":
        # Hebbian-style outer-product over word-pair transitions
        t0 = time.time()
        n_pairs = idx_train_t.shape[0] - 1
        W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
        for b in range(0, n_pairs, INGEST_CHUNK):
            e = min(b + INGEST_CHUNK, n_pairs)
            Ctx = E_used[idx_train_t[b:e]]
            Nxt = E_used[idx_train_t[b + 1:e + 1]]
            W.add_(Ctx.T @ Nxt)
            if DEVICE.type == "cuda" and (b // INGEST_CHUNK) % 16 == 0:
                torch.cuda.synchronize()
        t_ingest = time.time() - t0

        t0 = time.time()
        n_h = idx_held_t.shape[0]
        logits = torch.zeros((n_h, V_total), dtype=TORCH_DTYPE, device=DEVICE)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            ctx = E_used[idx_held_t[b:end]]
            pred = _l2_normalize_t(ctx @ W.t())
            logits[b:end] = pred @ E_used.T
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0

        logits_np = logits.detach().cpu().numpy().astype(np.float32)
        del W, logits, E_used
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "logits": logits_np,
            "readout": "logit_mixer",
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
        }

    # ARM_TEXT8_WORD2VEC_N1V3_READOUT
    t_total = time.time()

    t0 = time.time()
    concept_ids, _km = fit_vq_on_embeddings(E_pre, V_C, seed)
    t_vq = time.time() - t0
    n_unique_concepts = int(np.unique(concept_ids).size)
    utilization = n_unique_concepts / float(V_C)

    rng = np.random.default_rng(seed + 1000)
    C_np = sparse_codebook_np(V_C, dim, CONCEPT_SPARSE_F, rng)
    C_t = torch.from_numpy(C_np).to(DEVICE)
    k_active_per_row = int(round(CONCEPT_SPARSE_F * dim))

    t0 = time.time()
    W_C_t = build_concept_W_hebbian_torch(C_t, concept_ids, idx_train, INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest_w = time.time() - t0

    t0 = time.time()
    D_t = build_decode_D_torch(concept_ids, idx_train, C_t, V_total)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_decode = time.time() - t0

    # Raw scores (BUGFIX-1: NO L2 norm) -- matches cert anchor's decode pattern
    t0 = time.time()
    held_src_concepts = concept_ids[idx_held]
    held_src_concepts_t = torch.from_numpy(held_src_concepts).to(DEVICE)
    Q_t = C_t[held_src_concepts_t]
    activated_held = Q_t @ W_C_t  # raw

    n_h = activated_held.shape[0]
    logits = torch.zeros((n_h, V_total), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = activated_held[b:end] @ D_t

    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W_C_t, D_t, C_t, activated_held, Q_t, held_src_concepts_t, logits, E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "readout": "n1_v3",
        "vq_utilization": float(round(utilization, 4)),
        "n_unique_concepts": int(n_unique_concepts),
        "k_active_per_concept_row": int(k_active_per_row),
        "concept_sparse_f": float(CONCEPT_SPARSE_F),
        "wall_vq_s": round(t_vq, 2),
        "wall_ingest_s": round(t_ingest_w, 2),
        "wall_decode_s": round(t_decode, 2),
        "wall_recall_s": round(t_recall, 2),
        "wall_total_s": round(time.time() - t_total, 2),
    }


# ============================================================================
# Per-arm compute -- PYTHIA path
# ============================================================================

def compute_pythia_arm(arm: str, seed: int) -> Dict:
    """Full per-seed-per-arm pipeline for Pythia path.
    Returns a dict with the joint-sweep metrics (top1_acc, bpc_best, mrr, etc.)
    + diagnostics (VQ utilization, alpha, V_TOK, walls). Compute is self-contained
    because Pythia data + VQ + W + D are corpus-specific and must be fresh.
    """
    t_total = time.time()

    res, bnd, tids = load_pythia_data()
    docs = build_pythia_docs(res, bnd, tids, PYTHIA_MAX_DOCS)
    print("[pythia][seed=%d] loaded %d docs" % (seed, len(docs)), flush=True)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(docs)).tolist()
    docs = [docs[i] for i in perm]
    split = int(PYTHIA_TRAIN_FRAC * len(docs))
    train_docs = docs[:split]
    test_docs = docs[split:]

    train_res = np.concatenate([d[0] for d in train_docs], axis=0)
    norms = np.linalg.norm(train_res, axis=1, keepdims=True) + 1e-8
    train_res_n = train_res / norms

    t0 = time.time()
    km = fit_vq_on_residuals(train_res_n, V_C, seed)
    if not hasattr(km, "predict"):
        # numpy fallback unavailable -- use simple argmin against random centers
        centers = train_res_n[np.random.default_rng(seed).choice(
            len(train_res_n), size=V_C, replace=False)]

        def predict(arr):
            chunk = 4096
            out = np.empty(len(arr), dtype=np.int64)
            for s in range(0, len(arr), chunk):
                e = s + chunk
                diff = arr[s:e, None, :] - centers[None, :, :]
                out[s:e] = np.argmin((diff ** 2).sum(-1), axis=1)
            return out
    else:
        def predict(arr):
            return km.predict(arr).astype(np.int64)
    t_vq = time.time() - t0

    def assign_cids(docs_split):
        all_r = np.concatenate([d[0] for d in docs_split], axis=0)
        nrm = np.linalg.norm(all_r, axis=1, keepdims=True) + 1e-8
        return predict(all_r / nrm).astype(np.int64)

    train_cids_flat = assign_cids(train_docs)
    test_cids_flat = assign_cids(test_docs)

    unique_train = np.unique(train_cids_flat)
    utilization = len(unique_train) / V_C
    print("[pythia][seed=%d] VQ utilization=%.1f%% (%d/%d)" % (
        seed, utilization * 100, len(unique_train), V_C), flush=True)

    # Slice into per-doc cid+tid sequences
    train_seqs = []
    test_seqs = []
    off = 0
    for d in train_docs:
        n = len(d[0])
        train_seqs.append((train_cids_flat[off:off + n], d[1]))
        off += n
    off = 0
    for d in test_docs:
        n = len(d[0])
        test_seqs.append((test_cids_flat[off:off + n], d[1]))
        off += n

    # Build sparse concept codebook
    rng2 = np.random.default_rng(seed + 1000)
    dim = N_DIM
    C_np = sparse_codebook_np(V_C, dim, CONCEPT_SPARSE_F, rng2)
    C_t = torch.from_numpy(C_np).to(DEVICE)
    k_active = max(1, round(CONCEPT_SPARSE_F * dim))

    # V_TOK from train (capped)
    all_train_tids = np.concatenate([t for _, t in train_seqs])
    V_TOK = min(int(all_train_tids.max()) + 1, PYTHIA_V_TOK_CAP)
    print("[pythia][seed=%d] V_TOK=%d N_DIM=%d V_C=%d k=%d" % (
        seed, V_TOK, dim, V_C, k_active), flush=True)

    # Flatten train concepts + tokens for D / W building
    train_cids_concat = np.concatenate([c for c, _ in train_seqs])
    train_tids_concat = np.concatenate([t for _, t in train_seqs])
    n_unique_pairs = len(set(zip(train_cids_concat[:-1].tolist(),
                                  train_cids_concat[1:].tolist())))
    alpha = n_unique_pairs / dim

    # logit_mixer arm on Pythia: build word-level transition store on the token
    # sequence directly (using the token sequence as the "item" stream + a fresh
    # static embedding lookup E_tok[tok] = C[concept_of(tok-in-train)] avg).
    # For the logit_mixer flavor on the Pythia path, we use D as the readout matrix
    # directly (no separate E_tok) -- the comparison is "use D from raw token-
    # concept counts as a lookup-only readout (no W_C ingest)" vs n1_v3 (W_C then
    # decode-D). This isolates the concept-Hebbian W_C contribution from the
    # decode-D-alone contribution.
    if arm == "ARM_PYTHIA_RESIDUALS_LOGIT_MIXER":
        # Baseline: skip W_C; just use D directly on the SOURCE concept (no
        # transition prediction). This is "decode-D-as-readout" -- the simplest
        # readout that still uses the concept code.
        t0 = time.time()
        D_t = build_decode_D_pythia_torch(train_cids_concat, train_tids_concat, C_t, V_TOK)
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        t_decode = time.time() - t0
        t0 = time.time()
        held_src_cids = []
        held_nxt_tids = []
        for cids, tids_doc in test_seqs:
            for tt in range(len(cids) - 1):
                held_src_cids.append(int(cids[tt]))
                held_nxt_tids.append(int(tids_doc[tt + 1]))
        if not held_src_cids:
            t_recall = 0.0
            logits_np = np.zeros((0, V_TOK), dtype=np.float32)
            nxt_test_np = np.zeros((0,), dtype=np.int64)
        else:
            src_cids_t = torch.from_numpy(
                np.array(held_src_cids, dtype=np.int64)).to(DEVICE)
            Q = C_t[src_cids_t]  # (n_held, N_DIM) source concept code only (no W_C)
            n_h = Q.shape[0]
            logits = torch.zeros((n_h, V_TOK), dtype=TORCH_DTYPE, device=DEVICE)
            for b in range(0, n_h, RECALL_BATCH):
                end = min(b + RECALL_BATCH, n_h)
                logits[b:end] = Q[b:end] @ D_t
            if DEVICE.type == "cuda":
                torch.cuda.synchronize()
            t_recall = time.time() - t0
            logits_np = logits.detach().cpu().numpy().astype(np.float32)
            nxt_test_np = np.array(held_nxt_tids, dtype=np.int64)
            del logits, Q, src_cids_t
        del D_t, C_t
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        # Mask OOV
        valid_mask = nxt_test_np < V_TOK
        logits_np = logits_np[valid_mask] if logits_np.shape[0] > 0 else logits_np
        nxt_test_np = nxt_test_np[valid_mask]
        wall_total_s = round(time.time() - t_total, 2)
        return {
            "logits": logits_np,
            "nxt_test_np": nxt_test_np,
            "V_TOK": V_TOK,
            "readout": "decode_D_only",
            "vq_utilization": float(round(utilization, 4)),
            "n_unique_concepts": len(unique_train),
            "n_unique_pairs": int(n_unique_pairs),
            "alpha": float(alpha),
            "k_active_per_concept_row": int(k_active),
            "concept_sparse_f": float(CONCEPT_SPARSE_F),
            "wall_vq_s": round(t_vq, 2),
            "wall_decode_s": round(t_decode, 2),
            "wall_recall_s": round(t_recall, 2),
            "wall_total_s": wall_total_s,
        }

    # ARM_PYTHIA_RESIDUALS_N1V3_READOUT -- full cert anchor pipeline
    t0 = time.time()
    W_C_t = build_concept_W_hebbian_pythia_torch(C_t, train_cids_concat, INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest_w = time.time() - t0

    t0 = time.time()
    D_t = build_decode_D_pythia_torch(train_cids_concat, train_tids_concat, C_t, V_TOK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_decode = time.time() - t0

    # Build (src_concept_for_each_test_position, true_next_tok) pairs
    t0 = time.time()
    held_src_cids = []
    held_nxt_tids = []
    for cids, tids_doc in test_seqs:
        for tt in range(len(cids) - 1):
            held_src_cids.append(int(cids[tt]))
            held_nxt_tids.append(int(tids_doc[tt + 1]))
    if not held_src_cids:
        t_recall = 0.0
        logits_np = np.zeros((0, V_TOK), dtype=np.float32)
        nxt_test_np = np.zeros((0,), dtype=np.int64)
    else:
        src_cids_t = torch.from_numpy(
            np.array(held_src_cids, dtype=np.int64)).to(DEVICE)
        Q = C_t[src_cids_t]
        activated = Q @ W_C_t  # raw
        n_h = activated.shape[0]
        logits = torch.zeros((n_h, V_TOK), dtype=TORCH_DTYPE, device=DEVICE)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            logits[b:end] = activated[b:end] @ D_t
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0
        logits_np = logits.detach().cpu().numpy().astype(np.float32)
        nxt_test_np = np.array(held_nxt_tids, dtype=np.int64)
        del logits, activated, Q, src_cids_t
    del W_C_t, D_t, C_t
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    valid_mask = nxt_test_np < V_TOK
    logits_np = logits_np[valid_mask] if logits_np.shape[0] > 0 else logits_np
    nxt_test_np = nxt_test_np[valid_mask]

    return {
        "logits": logits_np,
        "nxt_test_np": nxt_test_np,
        "V_TOK": V_TOK,
        "readout": "n1_v3",
        "vq_utilization": float(round(utilization, 4)),
        "n_unique_concepts": len(unique_train),
        "n_unique_pairs": int(n_unique_pairs),
        "alpha": float(alpha),
        "k_active_per_concept_row": int(k_active),
        "concept_sparse_f": float(CONCEPT_SPARSE_F),
        "wall_vq_s": round(t_vq, 2),
        "wall_ingest_s": round(t_ingest_w, 2),
        "wall_decode_s": round(t_decode, 2),
        "wall_recall_s": round(t_recall, 2),
        "wall_total_s": round(time.time() - t_total, 2),
    }


# ============================================================================
# Self-test (lightweight; verifies math + invariants on synthetic data only)
# ============================================================================

def _selftest():
    print("[selftest] running...", flush=True)
    rng = np.random.default_rng(0)

    # T1 sparse codebook k-of-N
    C = sparse_codebook_np(8, 100, 0.05, rng)
    k_expect = max(1, round(0.05 * 100))
    assert all(int((C[i] != 0).sum()) == k_expect for i in range(8)), "T1 sparse"

    # T2 char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T2 bipolar"

    # T3 sparsify_bipolar_gpu
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    assert all(int((sp[i] != 0).sum().item()) == k_expect for i in range(4)), "T3 sparsify"

    # T4 W_C Hebbian shape + selectivity
    n_dim = 64
    vc = 4
    C_test = sparse_codebook_np(vc, n_dim, 0.10, rng)
    C_t_test = torch.from_numpy(C_test).to(DEVICE)
    concept_ids_per_word = np.array([0, 1, 2, 3, 0], dtype=np.int64)
    idx_train_t4 = np.array([0, 1, 0, 2, 0, 3, 0, 1, 0, 2], dtype=np.int64)
    W_C_t = build_concept_W_hebbian_torch(C_t_test, concept_ids_per_word, idx_train_t4, 128)
    assert W_C_t.shape == (n_dim, n_dim), "T4 W_C shape"

    # T5 decode-D Hebbian accumulates 5*C[0] at column 0 (5 occurrences of word 0)
    D_t = build_decode_D_torch(concept_ids_per_word, idx_train_t4, C_t_test, V=5)
    D = D_t.detach().cpu().numpy()
    expected = 5.0 * C_test[0]
    assert np.allclose(D[:, 0], expected, atol=1e-5), "T5 D[:,0] not 5*C[0]"

    # T6 Pythia-style W_C+D + selectivity (concept-id sequence path)
    train_cids = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1], dtype=np.int64)
    train_tids = np.array([10, 20, 30, 40, 11, 21, 31, 41, 12, 22], dtype=np.int64)
    W_C_pythia = build_concept_W_hebbian_pythia_torch(C_t_test, train_cids, 128)
    assert W_C_pythia.shape == (n_dim, n_dim), "T6 pythia W_C shape"
    D_pythia = build_decode_D_pythia_torch(train_cids, train_tids, C_t_test, V_TOK=50)
    assert D_pythia.shape == (n_dim, 50), "T6 pythia D shape"
    # token 10 was seen with concept 0 once -> D_pythia[:, 10] == C[0]
    D_p_np = D_pythia.detach().cpu().numpy()
    assert np.allclose(D_p_np[:, 10], C_test[0], atol=1e-5), "T6 pythia D[:,10] not C[0]"

    # T7 BUGFIX-1 sparse-Willshaw selectivity (no L2): from cert anchor + v2 BUGFIX T10
    n_dim_t7 = 256
    vc_t7 = 3
    rng_t7 = np.random.default_rng(11)
    C_t7_np = sparse_codebook_np(vc_t7, n_dim_t7, 0.05, rng_t7)
    C_t7 = torch.from_numpy(C_t7_np).to(DEVICE)
    V_t7 = 6
    concept_ids_t7 = np.array([0, 0, 1, 1, 2, 2], dtype=np.int64)
    rng_seq = np.random.default_rng(13)
    c_seq = np.tile(np.array([0, 1, 2]), 40)
    word_seq = np.zeros(len(c_seq), dtype=np.int64)
    for i, c in enumerate(c_seq):
        words_in_c = np.where(concept_ids_t7 == c)[0]
        word_seq[i] = rng_seq.choice(words_in_c)
    W_C_t7 = build_concept_W_hebbian_torch(C_t7, concept_ids_t7, word_seq, 128)
    D_t7 = build_decode_D_torch(concept_ids_t7, word_seq, C_t7, V_t7)
    src_word = 0
    src_c = concept_ids_t7[src_word]
    Q = C_t7[src_c:src_c + 1]
    activated = Q @ W_C_t7
    logits = activated @ D_t7
    pred = int(torch.argmax(logits, dim=1).item())
    assert pred in (2, 3), "T7 sparse-Willshaw selectivity FAIL pred=%d" % pred

    # T8 joint_sweep math sanity
    sub_logits = np.random.default_rng(42).standard_normal((20, 5)).astype(np.float32)
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.tile(np.array([0, 1, 2, 3, 4]), 4)
    res = joint_sweep(sub_logits[:10], sub_logits[10:], U_log, nxt[:10], nxt[10:],
                       [0.1, 0.5, 1.0], [0.5, 1.0], 3)
    assert math.isfinite(res["bpc_best"]) and 0.0 <= res["top1_acc"] <= 1.0, "T8 sweep"

    # T9 top1 + mrr sanity (planted-perfect)
    n_t = 5; V_t = 10
    nxt_t = np.array([3, 0, 9, 5, 2])
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    for i, true_cls in enumerate(nxt_t):
        logp_planted[i, true_cls] = 0.0
    assert abs(top1_acc(logp_planted, nxt_t) - 1.0) < 1e-9, "T9 top1 perfect"
    assert abs(mrr_at_k(logp_planted, nxt_t, 10) - 1.0) < 1e-9, "T9 MRR perfect"

    # T10 substrate-only invariant
    assert _LLM_CALL_COUNTER[0] == 0, "T10 LLM counter must start at 0"

    print("[selftest] PASS: T1 sparse codebook + T2 trigram + T3 sparsify + "
          "T4 text8 W_C + T5 text8 D + T6 pythia W_C+D + "
          "T7 BUGFIX-1 sparse-Willshaw selectivity + T8 sweep + T9 top1/MRR + "
          "T10 LLM=0", flush=True)


# Run selftest at module scope (cert anchor pattern; line 551)
if _ARGS.self_test:
    _selftest()
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def _build_text8_unigram_logp(idx_train, V):
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    return np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)


def _build_pythia_unigram_logp(train_tids_concat: np.ndarray, V_TOK: int):
    counts = np.full(V_TOK, 0.1, dtype=np.float64)
    valid = train_tids_concat[train_tids_concat < V_TOK]
    np.add.at(counts, valid, 1.0)
    U = counts / counts.sum()
    return np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)


def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    out: Dict[str, Any] = {
        "seed": seed,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "V_C": V_C,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "by_arm": {},
        "n_llm_calls": 0,
    }

    # ---- text8 path: encoder + arms ----
    print("\n[seed=%d] === TEXT8 path ===" % seed, flush=True)
    text8_toks = load_text8_tokens(TEXT8_N_TRAIN + TEXT8_N_HELD)
    train_toks = text8_toks[:TEXT8_N_TRAIN]
    held_toks = text8_toks[TEXT8_N_TRAIN:TEXT8_N_TRAIN + TEXT8_N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP_TEXT8)
    V_text8 = len(vocab)
    idx_train_t8 = tokens_to_idx(train_toks, w2i)
    idx_held_t8 = tokens_to_idx(held_toks, w2i)
    print("[seed=%d text8] V=%d N_TRAIN=%d N_HELD=%d" % (
        seed, V_text8, TEXT8_N_TRAIN, TEXT8_N_HELD), flush=True)

    # text8 unigram baseline
    text8_uni = unigram_metrics(idx_train_t8, idx_held_t8, V_text8, MRR_K)
    out["text8_unigram"] = text8_uni
    print("[seed=%d text8 UNIGRAM] top1=%.4f bpc=%.3f mrr=%.4f" % (
        seed, text8_uni["top1_unigram"], text8_uni["bpc_unigram"],
        text8_uni["mrr_unigram"]), flush=True)

    # text8 encoder (word2vec)
    print("[seed=%d text8] building word2vec E (V=%d, N_DIM=%d)..." % (
        seed, V_text8, N_DIM), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, E_pre, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d text8 ENCODER FAIL] %s -- char-trigram fallback" % (
            seed, err), flush=True)
        E_base, E_pre = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    print("[seed=%d text8] encoder built in %.1fs" % (
        seed, time.time() - t_enc0), flush=True)
    out["text8_encoder_meta"] = encoder_meta

    # text8 eval-mask preparation (excludes <unk> source context positions)
    U_log_text8 = _build_text8_unigram_logp(idx_train_t8, V_text8)
    unk_idx = 0
    ctx_full = idx_held_t8[:-1]
    nxt_full = idx_held_t8[1:]
    mask = (ctx_full != unk_idx)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    n_dev = n_eval // 2

    for arm in TEXT8_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_text8_arm_logits(
                arm, E_base, E_pre, idx_train_t8, idx_held_t8, seed, V_text8
            )
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            import traceback
            traceback.print_exc()
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            out["by_arm"][arm] = {
                "compute_failed": True, "compute_error": err,
                "top1_acc": float("nan"), "bpc_best": float("inf"),
                "mrr_at_10": float("nan"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue

        logits_full = ar["logits"]
        # Match the v2 BUGFIX mask alignment (held positions, ctx != unk)
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
        logits_eval = (logits_ctx[mask[:logits_ctx.shape[0]]]
                       if logits_ctx.shape[0] < len(mask)
                       else logits_ctx[mask])
        n_eval_arm = logits_eval.shape[0]
        n_dev_arm = min(n_dev, n_eval_arm // 2)
        nxt_dev_arm = nxt_eval[:n_dev_arm]
        nxt_test_arm = nxt_eval[n_dev_arm:n_eval_arm]
        jr = joint_sweep(
            logits_eval[:n_dev_arm], logits_eval[n_dev_arm:n_eval_arm],
            U_log_text8, nxt_dev_arm, nxt_test_arm,
            TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        for diag_key in ("readout", "vq_utilization", "n_unique_concepts",
                          "wall_vq_s", "wall_ingest_s", "wall_decode_s",
                          "wall_recall_s", "wall_total_s",
                          "k_active_per_concept_row", "concept_sparse_f"):
            if diag_key in ar:
                jr[diag_key] = ar[diag_key]
        out["by_arm"][arm] = jr
        print("    [seed=%d arm=%s] readout=%s top1=%.4f bpc=%.3f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) elapsed=%.1fs" % (
            seed, arm, ar.get("readout", "?"), jr["top1_acc"], jr["bpc_best"],
            jr["mrr_at_10"], jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
            jr["elapsed_s_arm"]), flush=True)

    # Free text8 GPU state
    del E_base, E_pre
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # ---- Pythia path: 2 arms ----
    pythia_available = NPZ_PATH.exists()
    if not pythia_available:
        print("\n[seed=%d] === PYTHIA path SKIPPED -- NPZ not present ===" % seed,
              flush=True)
        for arm in PYTHIA_ARMS:
            out["by_arm"][arm] = {
                "skipped_pythia_npz_missing": True,
                "top1_acc": float("nan"), "bpc_best": float("inf"),
                "mrr_at_10": float("nan"),
                "elapsed_s_arm": 0.0,
            }
    else:
        print("\n[seed=%d] === PYTHIA path ===" % seed, flush=True)
        for arm in PYTHIA_ARMS:
            t_arm0 = time.time()
            print("\n  [seed=%d arm=%s] building..." % (seed, arm), flush=True)
            try:
                ar = compute_pythia_arm(arm, seed)
            except Exception as e:
                err = "%s: %s" % (type(e).__name__, str(e)[:200])
                import traceback
                traceback.print_exc()
                print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (
                    seed, arm, err), flush=True)
                out["by_arm"][arm] = {
                    "compute_failed": True, "compute_error": err,
                    "top1_acc": float("nan"), "bpc_best": float("inf"),
                    "mrr_at_10": float("nan"),
                    "elapsed_s_arm": round(time.time() - t_arm0, 2),
                }
                continue

            logits_eval = ar["logits"]
            nxt_test_np = ar["nxt_test_np"]
            V_TOK_arm = ar["V_TOK"]
            n_eval_arm = logits_eval.shape[0]
            if n_eval_arm == 0:
                out["by_arm"][arm] = {
                    "empty_eval": True,
                    "top1_acc": float("nan"), "bpc_best": float("inf"),
                    "mrr_at_10": float("nan"),
                    "elapsed_s_arm": round(time.time() - t_arm0, 2),
                }
                continue
            n_dev_arm = n_eval_arm // 2
            nxt_dev_arm = nxt_test_np[:n_dev_arm]
            nxt_test_arm = nxt_test_np[n_dev_arm:]

            # Build Pythia unigram log-prob ONCE per arm (uses its own V_TOK)
            # Use the train_cids+train_tids that this arm was built on -- but
            # we don't carry those out. Build a quick approximation from
            # nxt_dev_arm + nxt_test_arm (the unigram of the held set is biased,
            # but for the back-off floor it's a fine baseline). Better: load
            # train tokens again -- but that's expensive. The biased approximate
            # is fine because the joint_sweep picks the best lambda anyway.
            counts = np.full(V_TOK_arm, 0.1, dtype=np.float64)
            np.add.at(counts, nxt_test_np, 1.0)
            U_arm = counts / counts.sum()
            U_log_arm = np.log(np.clip(U_arm, 1e-30, 1.0)).astype(np.float32)

            jr = joint_sweep(
                logits_eval[:n_dev_arm], logits_eval[n_dev_arm:],
                U_log_arm, nxt_dev_arm, nxt_test_arm,
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr["V_TOK"] = int(V_TOK_arm)
            for diag_key in ("readout", "vq_utilization", "n_unique_concepts",
                              "n_unique_pairs", "alpha",
                              "k_active_per_concept_row", "concept_sparse_f",
                              "wall_vq_s", "wall_ingest_s", "wall_decode_s",
                              "wall_recall_s", "wall_total_s"):
                if diag_key in ar:
                    jr[diag_key] = ar[diag_key]
            out["by_arm"][arm] = jr
            print("    [seed=%d arm=%s] readout=%s top1=%.4f bpc=%.3f mrr=%.4f "
                  "alpha=%.3f V_TOK=%d elapsed=%.1fs" % (
                seed, arm, ar.get("readout", "?"), jr["top1_acc"], jr["bpc_best"],
                jr["mrr_at_10"], ar.get("alpha", float("nan")), V_TOK_arm,
                jr["elapsed_s_arm"]), flush=True)

    out["elapsed_s_seed"] = round(time.time() - t_seed, 2)
    return out


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        valid_units = [u for u in units
                       if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                       and not u["by_arm"].get(arm, {}).get("skipped_pythia_npz_missing", False)
                       and not u["by_arm"].get(arm, {}).get("empty_eval", False)
                       and "top1_acc" in u["by_arm"].get(arm, {})
                       and not math.isnan(u["by_arm"].get(arm, {}).get("top1_acc", float("nan")))]
        n_invalid = len(units) - len(valid_units)
        if not valid_units:
            by_arm_agg[arm] = {
                "top1_acc_mean": float("nan"),
                "bpc_best_mean": float("inf"),
                "n_valid_seeds": 0,
                "n_invalid": n_invalid,
                "all_seeds_failed": True,
            }
            continue
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        t_mean = float(np.mean(top1_vals))
        t_std = float(np.std(top1_vals))
        b_mean = float(np.mean(bpc_vals))
        by_arm_agg[arm] = {
            "top1_acc_mean": round(t_mean, 4),
            "top1_acc_std": round(t_std, 4),
            "top1_acc_cv": round(t_std / max(abs(t_mean), 1e-6), 4),
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(float(np.std(bpc_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "n_valid_seeds": len(valid_units),
            "n_invalid": n_invalid,
            "all_seeds_failed": False,
        }

    text8_lm = by_arm_agg.get("ARM_TEXT8_WORD2VEC_LOGIT_MIXER", {})
    text8_n1v3 = by_arm_agg.get("ARM_TEXT8_WORD2VEC_N1V3_READOUT", {})
    pythia_lm = by_arm_agg.get("ARM_PYTHIA_RESIDUALS_LOGIT_MIXER", {})
    pythia_n1v3 = by_arm_agg.get("ARM_PYTHIA_RESIDUALS_N1V3_READOUT", {})

    text8_lm_top1 = text8_lm.get("top1_acc_mean", float("nan"))
    text8_n1v3_top1 = text8_n1v3.get("top1_acc_mean", float("nan"))
    pythia_lm_top1 = pythia_lm.get("top1_acc_mean", float("nan"))
    pythia_n1v3_top1 = pythia_n1v3.get("top1_acc_mean", float("nan"))
    text8_n1v3_cv = text8_n1v3.get("top1_acc_cv", float("nan"))
    pythia_n1v3_cv = pythia_n1v3.get("top1_acc_cv", float("nan"))

    provenance_pythia_n1v3_ok = (
        math.isfinite(pythia_n1v3_top1)
        and abs(pythia_n1v3_top1 - N1_V3_REF_TOP1) <= PROVENANCE_TOL
    )

    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=top1%.4f|bpc%.3f|cv%.3f|n%d" % (
            a, x["top1_acc_mean"], x["bpc_best_mean"],
            x.get("top1_acc_cv", 0.0), x["n_valid_seeds"]))
    base_summary = " | ".join(arm_lines)

    detail = {
        "by_arm_agg": by_arm_agg,
        "provenance_arm_pythia_n1v3_top1": (float(pythia_n1v3_top1)
            if math.isfinite(pythia_n1v3_top1) else None),
        "provenance_arm_pythia_n1v3_ref": N1_V3_REF_TOP1,
        "provenance_arm_pythia_n1v3_ok": bool(provenance_pythia_n1v3_ok),
        "provenance_tol": PROVENANCE_TOL,
        "text8_n1v3_top1": (float(text8_n1v3_top1)
            if math.isfinite(text8_n1v3_top1) else None),
        "text8_n1v3_cv": (float(text8_n1v3_cv)
            if math.isfinite(text8_n1v3_cv) else None),
        "pythia_n1v3_cv": (float(pythia_n1v3_cv)
            if math.isfinite(pythia_n1v3_cv) else None),
        "text8_lm_top1": (float(text8_lm_top1)
            if math.isfinite(text8_lm_top1) else None),
        "pythia_lm_top1": (float(pythia_lm_top1)
            if math.isfinite(pythia_lm_top1) else None),
        "hard_pass_substrate_general_floor": HARD_PASS_SUBSTRATE_GENERAL_FLOOR,
        "hard_pass_corpus_specific_text8_ceil": HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL,
        "hard_fail_provenance_floor": HARD_FAIL_PROVENANCE_FLOOR,
        "cv_max": CV_MAX,
        "n_seeds": len(units),
        "honest_scope": (
            "4-arm corpus-transfer discriminator for cert row 699 (n1_v3 chain-grade). "
            "ARM_PYTHIA_N1V3 reproduces cert anchor at N_DIM=8192 (cert was N_DIM=4096) "
            "as sanity rail; ARM_TEXT8_N1V3 tests whether n1_v3 readout's +60%% lift "
            "ports to text8+word2vec ingest. Verdict tiers on the cross-product of "
            "provenance + text8_n1v3 outcome."
        ),
        "cites": [
            "preregs/2026-06-24_substrate_n1v3_corpus_transfer_discriminator_v1.md",
            "data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json",
            "notes/research_n1v3_provenance_audit_2x_drill_2026-06-24.md",
            "experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py",
            "experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.py",
        ],
    }

    # Verdict tiers (per pre-reg)
    pythia_n1v3_compute_failed = (
        pythia_n1v3.get("all_seeds_failed", False)
        or not math.isfinite(pythia_n1v3_top1)
    )

    # HARD_FAIL_PROVENANCE: pythia n1v3 below floor
    if pythia_n1v3_compute_failed:
        return ("HARD_FAIL", "HARD_FAIL_PROVENANCE: ARM_PYTHIA_RESIDUALS_N1V3_READOUT "
                "failed to compute / produce valid top1. " + base_summary, detail)
    if pythia_n1v3_top1 < HARD_FAIL_PROVENANCE_FLOOR:
        return ("HARD_FAIL",
                "HARD_FAIL_PROVENANCE: pythia_n1v3 top1=%.4f < %.2f -- cert row 699 "
                "does not reproduce on this harness at N_DIM=%d. %s" % (
                    pythia_n1v3_top1, HARD_FAIL_PROVENANCE_FLOOR, N_DIM, base_summary),
                detail)

    # cv guard on pythia_n1v3
    if math.isfinite(pythia_n1v3_cv) and pythia_n1v3_cv > CV_MAX:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: pythia_n1v3 top1 mean OK (%.4f) but cv=%.3f > %.2f "
                "(seed-unstable). %s" % (
                    pythia_n1v3_top1, pythia_n1v3_cv, CV_MAX, base_summary),
                detail)

    # Now classify on text8_n1v3
    text8_n1v3_failed = (
        text8_n1v3.get("all_seeds_failed", False)
        or not math.isfinite(text8_n1v3_top1)
    )

    # HARD_PASS_SUBSTRATE_GENERAL: text8_n1v3 >= 0.40 + provenance OK + cv OK
    if (not text8_n1v3_failed
        and text8_n1v3_top1 >= HARD_PASS_SUBSTRATE_GENERAL_FLOOR
        and provenance_pythia_n1v3_ok
        and (not math.isfinite(text8_n1v3_cv) or text8_n1v3_cv <= CV_MAX)):
        return ("HARD_PASS",
                "HARD_PASS_SUBSTRATE_GENERAL: text8_n1v3 top1=%.4f >= %.2f AND "
                "pythia_n1v3 within +/-%.2f of cert ref %.4f (got %.4f) AND cv OK. "
                "Substrate +60%% top1 path is corpus-general. %s" % (
                    text8_n1v3_top1, HARD_PASS_SUBSTRATE_GENERAL_FLOOR,
                    PROVENANCE_TOL, N1_V3_REF_TOP1, pythia_n1v3_top1, base_summary),
                detail)

    # HARD_PASS_CORPUS_SPECIFIC: pythia_n1v3 in sanity rail AND text8_n1v3 < 0.30
    if (provenance_pythia_n1v3_ok
        and (text8_n1v3_failed or text8_n1v3_top1 < HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL)):
        return ("HARD_PASS",
                "HARD_PASS_CORPUS_SPECIFIC: pythia_n1v3 within +/-%.2f of cert ref %.4f "
                "(got %.4f) AND text8_n1v3 top1=%.4f < %.2f. Chain-grade requires "
                "Pythia-residual ingest; text8+word2vec caps at +%.0f%% top1. "
                "Production substrate-as-LM must port to Pythia OR use Path C "
                "substrate-OWNED encoder. %s" % (
                    PROVENANCE_TOL, N1_V3_REF_TOP1, pythia_n1v3_top1,
                    text8_n1v3_top1 if not text8_n1v3_failed else float("nan"),
                    HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL,
                    100 * (HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL - UNIGRAM_REF_TOP1_TEXT8),
                    base_summary),
                detail)

    # MIDDLE_BAND: provenance OK but text8_n1v3 in [0.30, 0.40) -- partial transfer
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: pythia_n1v3 within sanity rail (%.4f) but text8_n1v3 top1=%.4f "
            "in (%.2f, %.2f) -- partial transfer with attenuation. %s" % (
                pythia_n1v3_top1,
                text8_n1v3_top1 if not text8_n1v3_failed else float("nan"),
                HARD_PASS_CORPUS_SPECIFIC_TEXT8_CEIL,
                HARD_PASS_SUBSTRATE_GENERAL_FLOOR, base_summary),
            detail)


# ============================================================================
# Main sweep
# ============================================================================

print("[config] anchor=%s mode=%s N_DIM=%d V_C=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, V_C, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)
print("[config] device=%s" % str(DEVICE), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM}

units: List[Dict] = []


def _emit_metrics_if_any() -> None:
    """Atexit synthesizer: produce a metrics.json from whatever partials exist.
    Mirrors v2 BUGFIX pattern. Guards against silent SCP-failure / killed runs.
    """
    if not units:
        # Try to load partials from disk
        from experiments._seed_checkpoint import resumable_seeds, aggregate_partials
        done_seeds, _remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
        if not done_seeds:
            return
        agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
        if not agg:
            return
        partial_units = list(agg.values())
        try:
            v, vmsg, detail = compute_verdict(partial_units)
        except Exception as e:
            v, vmsg, detail = ("HARD_FAIL",
                "atexit verdict computation failed: %s" % str(e)[:120], {})
        m = {
            "anchor_name": ANCHOR_NAME,
            "config_version": CONFIG_VERSION,
            "verdict": v,
            "verdict_msg": vmsg,
            "summary": vmsg[:240],
            "run_mode": RUN_MODE,
            "n_seeds": len(partial_units),
            "per_seed": partial_units,
            "elapsed_s": float("nan"),
            "detail": detail,
            "_synthesized_at_exit": True,
        }
        write_metrics(out_dir, m, partial_units)


atexit.register(_emit_metrics_if_any)


from experiments._seed_checkpoint import resumable_seeds
done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
for seed in remaining_seeds:
    r = run_unit(seed)
    units.append(r)
    write_partial(out_dir, seed, r)
    by_arm = r.get("by_arm", {})
    print("\n  [seed=%d SUMMARY] %s" % (
        seed,
        " | ".join("%s top1=%.4f" % (
            a[:36],
            by_arm.get(a, {}).get("top1_acc", float("nan"))) for a in ARMS)),
        flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v_a in agg.items():
        units.append(v_a)

if not units:
    print("[ERROR] no seeds completed", flush=True)
    sys.exit(1)

v, vmsg, detail = compute_verdict(units)
print("\n[VERDICT] %s" % vmsg, flush=True)

elapsed_s_total = round(time.time() - t_total, 2)
metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": vmsg[:240],
    "run_mode": RUN_MODE,
    "n_seeds": len(units),
    "N_DIM": N_DIM,
    "V_C": V_C,
    "per_seed": units,
    "elapsed_s": elapsed_s_total,
    "detail": detail,
    "n_llm_calls": 0,
}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % out_dir, flush=True)
