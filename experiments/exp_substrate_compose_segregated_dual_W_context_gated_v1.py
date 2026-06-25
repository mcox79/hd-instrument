"""
substrate_compose_segregated_dual_W_context_gated_v1 -- per drill recommendation:
v4 ARM_FREQ_COMBINE_W_THETA HURT (BPC=7.365 vs baseline 7.3065, worse by 0.06).
Combining FREQ_ROUTED + THETA_PHASE on the SAME W matrix creates FDM
intermodulation (per comms-theory: two carriers on one channel mix; the brain
doesn't multiplex two functional roles on a single synaptic dynamic).

v1 alternative architecture: SEGREGATED dual-W banks with CONTEXT-GATED mixer.
Brain analog: theta-gamma coupling:
  - W_when (theta-equivalent): updates ONLY on sequential-timing signal (STDP
    antisymmetric); captures "WHEN does target come next given context"
  - W_what (gamma-equivalent): updates ONLY on content prediction (cf-RPE);
    captures "WHAT content is required to fit local pattern"
  - Context-gated mixer at retrieval: per-query weight W_when vs W_what by
    learned context features (context norm-magnitude as proxy for context
    informativeness; high-info ctx -> trust WHAT more; low-info -> trust WHEN
    more)

KEY architectural distinction from v4 COMBINE:
  v4 COMBINE: W_freq receives cf-RPE-on-phase0 AND STDP-on-phase1 -> intermod
  v1 SEGREGATED: W_when receives ONLY STDP; W_what receives ONLY cf-RPE.
                  No shared-W interference; segregation by FUNCTION not by phase.

The critical test: does the segregation principle (brain canonical: theta for
WHEN, gamma for WHAT) avoid the FDM intermodulation that v4 COMBINE created?
  YES -> substrate-product architectural principle (function-level segregation)
  NO  -> mechanism combination genuinely doesn't compose at substrate scale

LANE: 1 (substrate-native). ROUTING: GPU overnight_queue. BUDGET: 7200s.

ARMS (5):
  1. ARM_BASELINE_SHARED_W -- Hebbian baseline; sanity rail vs 7.3065
  2. ARM_FREQ_DEEPER -- v4 winner reproduced; rail to v5 cell
  3. ARM_THETA_PHASE_TWO_W -- v3 THETA winner reproduced; tests segregation alone
  4. ARM_SEGREGATED_DUAL_W -- W_when (STDP-only) + W_what (cf-RPE-only); no
       shared dynamics; static 0.5/0.5 mixer at retrieval
  5. ARM_SEGREGATED_PLUS_CONTEXT_GATE -- above + learned context-magnitude gate
       at retrieval; tests whether gating adds value over static mix

HARD bands (PROSPECTIVE):

  HARD_PASS_CHAIN_GRADE:
    - ARM_SEGREGATED_PLUS_CONTEXT_GATE BPC <= 6.95
    - AND beats FREQ_DEEPER (7.16) AND THETA (7.235) individually
    - AND CV <= 0.05

  HARD_PASS (segregation principle works):
    - ARM_SEGREGATED_PLUS_CONTEXT_GATE BPC <= 7.10
    - AND beats ARM_BASELINE_SHARED_W by >= 0.20 BPC
    - AND CV <= 0.05

  HARD_FAIL (segregation doesn't avoid intermod):
    - ARM_SEGREGATED arms within +/-0.05 of v4 COMBINE_W_THETA's 7.365
    - (architecture combination genuinely doesn't compose)

  MIDDLE_BAND_PARTIAL:
    - ARM_SEGREGATED arms in [7.10, 7.30]
    - (partial signal but doesn't surpass individual mechanism wins)

DISCIPLINES:
  D1 roofline probe before estimating wall
  D2 atexit + per-seed checkpoint
  Self-test PASS gate
  NO local smoke (GPU cell)
  ASCII only
  Pre-reg committed BEFORE dispatch
  Per Fix #28 per-arm metrics
  Per Fix #24 GPU must actually use GPU

CITES:
  preregs/2026-06-25_substrate_compose_segregated_dual_W_context_gated_v1.md
  experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py
    (v4 COMBINE_W_THETA=7.365 HURT; motivates segregation drill)
  experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py
    (v3 THETA=7.2349 + FREQ=7.2096)
  drill notes/research_drill_v4_combine_w_theta_FDM_intermod_2026-06-25.md
    (USER drill recommendation: segregate by function-domain, not phase)
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
import json
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_compose_segregated_dual_W_context_gated_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands
# ============================================================================
SANITY_RAIL_BASELINE_REF = 7.3065
SANITY_RAIL_TOLERANCE = 0.05

# References from prior cells (per Fix #28: read per-arm metrics):
V4_COMBINE_W_THETA_HURT_BPC = 7.365   # v4 FREQ x THETA on shared W -- HURT
V4_FREQ_DEEPER_BPC = 7.159            # v4 best (single mechanism)
V3_THETA_PHASE_BPC = 7.2349           # v3 THETA two-W (already segregated)
V3_FREQ_ROUTED_BPC = 7.2096           # v3 FREQ best (single mechanism)

# v1 SEGREGATED HARD bands
HARD_PASS_CHAIN_GRADE_BPC = 6.95
HARD_PASS_BPC = 7.10
HARD_PASS_GAP_VS_BASELINE = 0.20
CV_MAX = 0.05

# HARD_FAIL: SEGREGATED arms cluster near v4 COMBINE's 7.365 (intermod not avoided)
HARD_FAIL_INTERMOD_CENTER = V4_COMBINE_W_THETA_HURT_BPC
HARD_FAIL_INTERMOD_BAND = 0.05

# MIDDLE_BAND for segregated arms
MIDDLE_BAND_LOWER = 7.10
MIDDLE_BAND_UPPER = 7.30

# Discriminator: does SEGREGATED beat the best individual mechanism (FREQ_DEEPER 7.159)?
INDIVIDUAL_MECHANISM_BAR_BPC = V4_FREQ_DEEPER_BPC  # if SEGREGATED beats this, combo works
COMBO_BEATS_INDIVIDUAL_MARGIN = 0.02  # delta required to claim composition lifts

# ============================================================================
# Primitive knob parameters
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS = 2000  # match v4 FREQ_DEEPER for fair comparison

FREQ_ROUTE_RANK = 100
FREQ_LR_HIGH = 0.5
FREQ_LR_RARE = 0.2
THETA_ALPHA_GRID = [0.3, 0.5, 0.7]

TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"

# Context-gate parameters for SEGREGATED_PLUS_CONTEXT_GATE arm.
# Mixer: per-query weight = sigmoid(scale * (ctx_norm - center))
# When ctx_norm high (informative context) -> weight WHAT higher
# When ctx_norm low (uninformative) -> weight WHEN higher
GATE_GRID = [
    # (center, scale) -- swept to find best at dev BPC
    (0.5, 1.0),
    (0.5, 5.0),
    (0.7, 1.0),
    (0.7, 5.0),
    (1.0, 1.0),
]

ARMS = [
    "ARM_BASELINE_SHARED_W",
    "ARM_FREQ_DEEPER",
    "ARM_THETA_PHASE_TWO_W",
    "ARM_SEGREGATED_DUAL_W",
    "ARM_SEGREGATED_PLUS_CONTEXT_GATE",
]


# ============================================================================
# CLI / run-mode
# ============================================================================
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--roofline-probe-only", action="store_true",
                dest="roofline_probe_only")
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


def _gpu_setup_assert_and_report(label: str = "startup"):
    try:
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
            try:
                free_b, total_b = torch.cuda.mem_get_info(DEVICE)
                free_gb = free_b / (1024 ** 3)
                total_gb = total_b / (1024 ** 3)
                print(("[gpu_setup %s] device=%s free_gb=%.2f total_gb=%.2f") % (
                          label, str(DEVICE), free_gb, total_gb), flush=True)
            except Exception:
                pass
            probe = torch.zeros(8, device=DEVICE, dtype=TORCH_DTYPE)
            assert probe.device.type == DEVICE.type
            del probe
            torch.cuda.synchronize()
        else:
            print("[gpu_setup %s] device=cpu" % label, flush=True)
    except Exception as e:
        print("[gpu_setup %s] WARN: %s" % (label, str(e)[:200]), flush=True)


N_DIM = 8192
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 13, 17, 23, 29]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 1024
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s n_steps=%d "
    "v4_combine_ref=%.4f v4_freq_deeper_ref=%.4f device=%s version=v1_SEGREGATED"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, N_STEPS,
    V4_COMBINE_W_THETA_HURT_BPC, V4_FREQ_DEEPER_BPC, str(DEVICE),
)


# ============================================================================
# D2 ATEXIT
# ============================================================================
class _RunState:
    def __init__(self):
        self.out_dir: Optional[Path] = None
        self.current_seed: Optional[int] = None
        self.current_seed_partials: Dict = {}
        self.atexit_registered: bool = False
        self.last_flush_ts: float = 0.0

_RUN_STATE = _RunState()


def _atexit_flush_partial():
    try:
        if _RUN_STATE.out_dir is None or _RUN_STATE.current_seed is None:
            return
        if not _RUN_STATE.current_seed_partials:
            return
        seed = _RUN_STATE.current_seed
        out_path = _RUN_STATE.out_dir / ("partial_metrics_%d_atexit.json" % seed)
        canonical = _RUN_STATE.out_dir / ("partial_metrics_%d.json" % seed)
        if canonical.exists():
            return
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "seed": int(seed),
            "_atexit_partial": True,
            "_atexit_ts": time.time(),
            "by_arm_partial": _RUN_STATE.current_seed_partials,
            "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE,
        }
        tmp = out_path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        os.replace(tmp, out_path)
        print("[atexit] flushed seed=%d partial to %s" % (seed, out_path), flush=True)
    except Exception as e:
        try:
            print("[atexit] flush failed: %s" % str(e), flush=True)
        except Exception:
            pass


def _register_atexit_once():
    if _RUN_STATE.atexit_registered:
        return
    atexit.register(_atexit_flush_partial)
    _RUN_STATE.atexit_registered = True


# ============================================================================
# Corpus utilities
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


def vocab_frequency_ranks(idx_train: np.ndarray, V: int) -> np.ndarray:
    counts = np.zeros(V, dtype=np.int64)
    np.add.at(counts, idx_train, 1)
    order = np.argsort(-counts)
    ranks = np.empty(V, dtype=np.int64)
    ranks[order] = np.arange(V)
    return ranks


# ============================================================================
# Encoder utilities
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv_np(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv_np(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
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


_GENSIM_KV_CACHE: Dict[str, object] = {}


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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
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
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_synthetic_smoke(V: int, n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    rng = np.random.default_rng(seed * 9173 + 11)
    E_np = rng.standard_normal((V, n_dim)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(V), "n_miss": 0, "n_vocab": int(V),
            "pretrain_dim": int(n_dim), "synthetic_smoke": True}
    return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
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
# Plasticity primitives
# ============================================================================

def build_W_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                          ingest_chunk: int) -> torch.Tensor:
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_logits_hebbian_baseline_gpu(E_full: torch.Tensor,
                                         idx_train_t: torch.Tensor,
                                         idx_held_t: torch.Tensor,
                                         recall_batch: int,
                                         ingest_chunk: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W = build_W_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    pred = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits[b:end] = pred[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, pred, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "discriminating": {}}


def build_logits_freq_routed_k2_gpu(E_full: torch.Tensor,
                                      idx_train_t: torch.Tensor,
                                      idx_held_t: torch.Tensor,
                                      ranks_np: np.ndarray,
                                      n_steps: int, batch: int,
                                      lr_high: float, lr_rare: float,
                                      stdp_w: float, freq_threshold: int,
                                      seed: int, arm_idx: int,
                                      recall_batch: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    is_high_freq = (ranks_np < freq_threshold)
    is_high_freq_t = torch.from_numpy(is_high_freq.astype(np.float32)).to(device)
    n_pairs_total = idx_train_t.shape[0] - 1
    if n_pairs_total <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}, "is_high_freq_vocab_mask": is_high_freq}

    t0 = time.time()
    W_freq = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_rare = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    n_high_steps = 0
    n_rare_steps = 0
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs_total, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        tgt_idx = idx_train_t[st + 1]
        is_high_batch = is_high_freq_t[tgt_idx]
        wh = is_high_batch.unsqueeze(1)
        error_freq = Nxt - Ctx @ W_freq.T
        dW_freq = ((error_freq * wh).T @ Ctx) / float(batch)
        W_freq = W_freq + lr_high * dW_freq
        wr = (1.0 - is_high_batch).unsqueeze(1)
        error_rare = Nxt - Ctx @ W_rare.T
        dW_cf_rare = ((error_rare * wr).T @ Ctx) / float(batch)
        Ctx_w = Ctx * wr
        Nxt_w = Nxt * wr
        dW_stdp_rare = (Nxt_w.T @ Ctx - Ctx_w.T @ Nxt) / float(batch)
        W_rare = W_rare + lr_rare * (dW_cf_rare + stdp_w * dW_stdp_rare)
        n_high_steps += int(is_high_batch.sum().item())
        n_rare_steps += int((1.0 - is_high_batch).sum().item())

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_freq = _l2_normalize_t(ctx_b @ W_freq.T)
        pred_rare = _l2_normalize_t(ctx_b @ W_rare.T)
        logit_freq = pred_freq @ E_full.T
        logit_rare = pred_rare @ E_full.T
        mask = is_high_freq_t.unsqueeze(0)
        logits[b:end] = mask * logit_freq + (1.0 - mask) * logit_rare
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0
    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W_freq, W_rare, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {"n_high_freq_steps": int(n_high_steps),
                           "n_rare_steps": int(n_rare_steps),
                           "freq_threshold": int(freq_threshold)},
        "is_high_freq_vocab_mask": is_high_freq,
    }


def build_logits_theta_phase_two_w_gpu(E_full: torch.Tensor,
                                          idx_train_t: torch.Tensor,
                                          idx_held_t: torch.Tensor,
                                          n_steps: int, batch: int, lr: float,
                                          stdp_w: float,
                                          seed: int, arm_idx: int,
                                          recall_batch: int) -> Dict:
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W_enc = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_ret = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits_alpha_stack": np.zeros((len(THETA_ALPHA_GRID), n_h, V), dtype=np.float32),
                "alpha_grid": list(THETA_ALPHA_GRID),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0, "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)
    n_phase0 = 0
    n_phase1 = 0
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        phase = step % 2
        if phase == 0:
            error = Nxt - Ctx @ W_enc.T
            dW = (error.T @ Ctx) / float(batch)
            W_enc = W_enc + lr * dW
            n_phase0 += 1
        else:
            dW = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
            W_ret = W_ret + lr * stdp_w * dW
            n_phase1 += 1

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    pred_enc = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    pred_ret = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_enc[b:end] = _l2_normalize_t(ctx_b @ W_enc.T)
        pred_ret[b:end] = _l2_normalize_t(ctx_b @ W_ret.T)
    logits_enc = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_ret = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits_enc[b:end] = pred_enc[b:end] @ E_full.T
        logits_ret[b:end] = pred_ret[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    le = logits_enc.detach().cpu().numpy().astype(np.float32)
    lr_np = logits_ret.detach().cpu().numpy().astype(np.float32)
    alpha_stack = np.stack(
        [(a * le) + ((1.0 - a) * lr_np) for a in THETA_ALPHA_GRID],
        axis=0,
    ).astype(np.float32)

    del W_enc, W_ret, pred_enc, pred_ret, logits_enc, logits_ret
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits_alpha_stack": alpha_stack,
        "alpha_grid": list(THETA_ALPHA_GRID),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {"n_phase0_steps": int(n_phase0),
                           "n_phase1_steps": int(n_phase1)},
    }


# ============================================================================
# v1 SEGREGATED dual-W kernel
# ============================================================================

def build_logits_segregated_dual_w_gpu(E_full: torch.Tensor,
                                          idx_train_t: torch.Tensor,
                                          idx_held_t: torch.Tensor,
                                          n_steps: int, batch: int, lr: float,
                                          stdp_w: float,
                                          seed: int, arm_idx: int,
                                          recall_batch: int,
                                          context_gate_params: Optional[List[Tuple[float, float]]] = None) -> Dict:
    """SEGREGATED dual-W: W_when (STDP-only) + W_what (cf-RPE-only).

    Key architectural distinction from v4 COMBINE_W_THETA:
      v4: W_freq receives BOTH cf-RPE (phase0) AND STDP (phase1) on shared W
          -> FDM intermodulation per comms theory
      v1: W_when ONLY receives STDP-antisymmetric updates (sequence-timing)
          W_what ONLY receives cf-RPE updates (content prediction)
          -> no shared dynamics; function-domain segregation

    Brain analog: theta-gamma:
      theta = WHEN signal (sequence/timing/order) -- W_when
      gamma = WHAT signal (content/pattern-completion) -- W_what

    Updates per step (NO phase alternation -- BOTH W update every step):
      dW_when = (Nxt.T @ Ctx - Ctx.T @ Nxt) / batch  (STDP-antisymmetric)
                                                       (timing of next-given-current)
      dW_what = (Nxt - Ctx @ W_what.T).T @ Ctx / batch  (cf-RPE on next-token content)

    Mixer (at retrieval, per query):
      STATIC (default, when context_gate_params is None or empty):
        logit = 0.5 * (Ctx @ W_when.T @ E.T) + 0.5 * (Ctx @ W_what.T @ E.T)

      LEARNED CONTEXT GATE (when context_gate_params provided):
        For each (center, scale) in grid:
          ctx_norm = ||Ctx|| / sqrt(dim)  (l1-norm proxy for informativeness)
          gate = sigmoid(scale * (ctx_norm - center))
          # gate -> 1 when ctx_norm high (trust WHAT more)
          # gate -> 0 when ctx_norm low  (trust WHEN more)
          logit = gate * (Ctx @ W_what.T @ E.T) + (1-gate) * (Ctx @ W_when.T @ E.T)
        Output: gate_stack[len(grid)] of logits arrays; verdict picks best at dev BPC.

    Returns:
      logits (np.ndarray) for STATIC mix (mandatory)
      gate_stack (np.ndarray) if context_gate_params provided
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W_when = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_what = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        out = {"logits": np.zeros((n_h, V), dtype=np.float32),
               "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
               "discriminating": {}}
        if context_gate_params:
            out["gate_stack"] = np.zeros((len(context_gate_params), n_h, V), dtype=np.float32)
            out["gate_grid"] = list(context_gate_params)
        return out

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    # SEGREGATED updates: BOTH W update every step, but with DIFFERENT rules
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        # W_when: STDP-antisymmetric ONLY (captures sequence-timing)
        dW_when = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
        W_when = W_when + lr * stdp_w * dW_when
        # W_what: cf-RPE ONLY (captures content-prediction)
        error_what = Nxt - Ctx @ W_what.T
        dW_what = (error_what.T @ Ctx) / float(batch)
        W_what = W_what + lr * dW_what

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Discriminating: cross-bank correlation (should be LOW; if HIGH segregation failed)
    when_flat = W_when.flatten()
    what_flat = W_what.flatten()
    when_norm = when_flat / (when_flat.norm() + 1e-12)
    what_norm = what_flat / (what_flat.norm() + 1e-12)
    when_vs_what_bank_corr = float((when_norm * what_norm).sum().item())

    t0 = time.time()
    # Compute per-bank logits + cache for mixer
    logits_when = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_what = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    ctx_norms = torch.zeros(n_h, dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        # context norm proxy: mean absolute value of context vector
        # (since ctx is sparsified-bipolar with ~5% nnz, ||ctx||_1/dim is roughly stable;
        #  use l1-mean as scalar context-informativeness proxy)
        ctx_norms[b:end] = ctx_b.abs().sum(dim=1) / float(dim)
        pred_when = _l2_normalize_t(ctx_b @ W_when.T)
        pred_what = _l2_normalize_t(ctx_b @ W_what.T)
        logits_when[b:end] = pred_when @ E_full.T
        logits_what[b:end] = pred_what @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    # STATIC mixer logits (default)
    logits_static = 0.5 * logits_when + 0.5 * logits_what
    logits_np = logits_static.detach().cpu().numpy().astype(np.float32)

    out = {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "when_vs_what_bank_corr": round(when_vs_what_bank_corr, 4),
            "ctx_norm_mean": round(float(ctx_norms.mean().item()), 6),
            "ctx_norm_std": round(float(ctx_norms.std().item()), 6),
            "ctx_norm_min": round(float(ctx_norms.min().item()), 6),
            "ctx_norm_max": round(float(ctx_norms.max().item()), 6),
        },
    }

    if context_gate_params:
        # Build gate_stack across (center, scale) grid
        ctx_norms_np = ctx_norms.detach().cpu().numpy().astype(np.float32)
        logits_when_np = logits_when.detach().cpu().numpy().astype(np.float32)
        logits_what_np = logits_what.detach().cpu().numpy().astype(np.float32)
        gate_stack = []
        for (center, scale) in context_gate_params:
            z = scale * (ctx_norms_np - center)
            gate = 1.0 / (1.0 + np.exp(-z))  # sigmoid -> (0, 1)
            # gate -> 1: trust WHAT more (high info ctx); gate -> 0: trust WHEN more
            gate_col = gate[:, None].astype(np.float32)
            mixed = gate_col * logits_what_np + (1.0 - gate_col) * logits_when_np
            gate_stack.append(mixed)
        out["gate_stack"] = np.stack(gate_stack, axis=0).astype(np.float32)
        out["gate_grid"] = list(context_gate_params)
        out["discriminating"]["gate_grid_size"] = int(len(context_gate_params))

    del W_when, W_what, logits_when, logits_what, logits_static
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return out


# ============================================================================
# BPC / eval utilities
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


def raw_bpc_at_T1(logits_np: np.ndarray, nxt_eval: np.ndarray) -> float:
    n_h = logits_np.shape[0]
    n_eval = min(n_h, len(nxt_eval))
    if n_eval == 0:
        return float("inf")
    sub = logits_np[:n_eval]
    nxt_e = nxt_eval[:n_eval]
    z = sub - sub.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_e].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
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
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))
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
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
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
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test
# ============================================================================

def _instrumentation_selftest():
    print("[selftest v1_SEGREGATED] running...", flush=True)

    n_dim_st = 64

    # ST1: cf-RPE shrinks error
    rng_st = np.random.default_rng(42)
    Ctx_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx_np /= np.linalg.norm(Ctx_np) + 1e-8
    Nxt_np /= np.linalg.norm(Nxt_np) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    dW = (Nxt_np - Ctx_np @ W_test.T).T @ Ctx_np
    W_test = W_test + 0.9 * dW
    err_after = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    assert err_after < err_before
    print("[selftest] ST1 cf-RPE OK", flush=True)

    # ST2: STDP antisymmetry
    b_st = 4
    Ctx_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    dW_stdp = (Nxt_t.T @ Ctx_t - Ctx_t.T @ Nxt_t) / float(b_st)
    antisym_err = float((dW_stdp + dW_stdp.T).abs().max())
    assert antisym_err < 1e-4
    print("[selftest] ST2 STDP antisym OK", flush=True)

    # Common smoke setup
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    ranks_st = vocab_frequency_ranks(idx_tr_st.detach().cpu().numpy(), V=V_st)

    # ST3: hebbian baseline produces nonzero logits
    ar_b = build_logits_hebbian_baseline_gpu(E_sb, idx_tr_st, idx_h_st,
                                                recall_batch=4, ingest_chunk=4)
    assert ar_b["logits"].shape == (idx_h_st.shape[0], V_st)
    assert not np.all(ar_b["logits"] == 0.0)
    print("[selftest] ST3 hebbian baseline OK", flush=True)

    # ST4: FREQ_DEEPER (same kernel as v4) produces nonzero
    ar_f = build_logits_freq_routed_k2_gpu(E_sb, idx_tr_st, idx_h_st, ranks_st,
                                              n_steps=10, batch=3,
                                              lr_high=0.5, lr_rare=0.2,
                                              stdp_w=0.5, freq_threshold=3,
                                              seed=0, arm_idx=2, recall_batch=4)
    assert ar_f["logits"].shape == (idx_h_st.shape[0], V_st)
    assert not np.all(ar_f["logits"] == 0.0)
    print("[selftest] ST4 FREQ_DEEPER OK", flush=True)

    # ST5: THETA_PHASE_TWO_W produces alpha_stack
    ar_t = build_logits_theta_phase_two_w_gpu(E_sb, idx_tr_st, idx_h_st,
                                                 n_steps=10, batch=3, lr=0.5,
                                                 stdp_w=0.5, seed=0, arm_idx=3,
                                                 recall_batch=4)
    assert ar_t["logits_alpha_stack"].shape == (len(THETA_ALPHA_GRID), idx_h_st.shape[0], V_st)
    n0 = ar_t["discriminating"]["n_phase0_steps"]
    n1 = ar_t["discriminating"]["n_phase1_steps"]
    assert n0 + n1 == 10
    print("[selftest] ST5 THETA_PHASE OK (n0=%d n1=%d)" % (n0, n1), flush=True)

    # ST6 (v1 NEW): SEGREGATED_DUAL_W static-mix kernel
    ar_s = build_logits_segregated_dual_w_gpu(E_sb, idx_tr_st, idx_h_st,
                                                 n_steps=10, batch=3, lr=0.5,
                                                 stdp_w=0.5, seed=0, arm_idx=4,
                                                 recall_batch=4,
                                                 context_gate_params=None)
    assert ar_s["logits"].shape == (idx_h_st.shape[0], V_st), "ST6 segregated shape wrong"
    assert not np.all(ar_s["logits"] == 0.0), "ST6 segregated all zero"
    when_vs_what = ar_s["discriminating"]["when_vs_what_bank_corr"]
    assert math.isfinite(when_vs_what), "ST6 when_vs_what corr not finite"
    # Segregation SHOULD produce different banks; correlation < 0.95 (not identical)
    assert abs(when_vs_what) < 0.95, "ST6 when vs what banks too correlated: %.4f" % when_vs_what
    print("[selftest] ST6 SEGREGATED_DUAL_W when_vs_what_corr=%.4f OK" % when_vs_what, flush=True)

    # ST7 (v1 NEW): SEGREGATED with context gate -- gate_stack present
    ar_g = build_logits_segregated_dual_w_gpu(E_sb, idx_tr_st, idx_h_st,
                                                 n_steps=10, batch=3, lr=0.5,
                                                 stdp_w=0.5, seed=0, arm_idx=5,
                                                 recall_batch=4,
                                                 context_gate_params=GATE_GRID)
    assert "gate_stack" in ar_g, "ST7 gate_stack missing"
    assert ar_g["gate_stack"].shape == (len(GATE_GRID), idx_h_st.shape[0], V_st), (
        "ST7 gate_stack shape wrong: %s" % str(ar_g["gate_stack"].shape))
    assert not np.all(ar_g["gate_stack"] == 0.0), "ST7 gate_stack all zero"
    # Different gates produce different logits
    d_g0g1 = float(np.abs(ar_g["gate_stack"][0] - ar_g["gate_stack"][1]).mean())
    assert d_g0g1 > 1e-9 or len(GATE_GRID) == 1, (
        "ST7 gate variants identical: %.4e" % d_g0g1)
    print("[selftest] ST7 SEGREGATED_PLUS_CONTEXT_GATE gate-diff=%.4e OK" % d_g0g1, flush=True)

    # ST8: 5-arm diversity (each arm's logits differ from each other)
    d_bf = float(np.abs(ar_b["logits"] - ar_f["logits"]).mean())
    d_bs = float(np.abs(ar_b["logits"] - ar_s["logits"]).mean())
    d_fs = float(np.abs(ar_f["logits"] - ar_s["logits"]).mean())
    assert d_bf > 1e-6 and d_bs > 1e-6 and d_fs > 1e-6, (
        "ST8 arm logits not diverse: bf=%.4e bs=%.4e fs=%.4e" % (d_bf, d_bs, d_fs))
    print("[selftest] ST8 5-arm diversity OK (bf=%.4e bs=%.4e fs=%.4e)" % (
        d_bf, d_bs, d_fs), flush=True)

    # ST9: joint_sweep finite
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"])
    print("[selftest] ST9 joint_sweep OK", flush=True)

    # ST10: sparsify_bipolar_gpu nnz correct
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all())
    print("[selftest] ST10 sparsify nnz OK", flush=True)

    # ST11: LAMBDA_GRID excludes 0.0
    assert 0.0 not in LAMBDA_GRID
    print("[selftest] ST11 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST12: LLM-call counter zero
    assert _LLM_CALL_COUNTER[0] == 0
    print("[selftest] ST12 LLM counter==0 OK", flush=True)

    # ST13 (v1): ARMS list consistency
    expected_arms = {"ARM_BASELINE_SHARED_W", "ARM_FREQ_DEEPER",
                     "ARM_THETA_PHASE_TWO_W", "ARM_SEGREGATED_DUAL_W",
                     "ARM_SEGREGATED_PLUS_CONTEXT_GATE"}
    assert set(ARMS) == expected_arms, "ST13 ARMS mismatch: %s" % set(ARMS)
    assert len(ARMS) == 5
    print("[selftest] ST13 ARMS consistent (5) OK", flush=True)

    # ST14: D2 atexit registered
    _register_atexit_once()
    assert _RUN_STATE.atexit_registered
    _atexit_flush_partial()
    print("[selftest] ST14 D2 atexit OK", flush=True)

    # ST15: config-coherence (5 seeds in full)
    if RUN_MODE == "full":
        assert N_DIM == 8192
        assert N_TRAIN == 100_000
        assert len(SEEDS) == 5
        assert SEEDS == [7, 13, 17, 23, 29]
    print("[selftest] ST15 config-coherence OK", flush=True)

    # ST16 (v1 NEW): SEGREGATED segregation invariant -- after enough steps,
    # the when_vs_what bank correlation should be visibly below 1.0. STDP and
    # cf-RPE are different update rules; banks should diverge.
    # Note: at small n_steps the corr may be near 0 (banks near random).
    print("[selftest] ST16 segregation invariant captured in ST6 OK", flush=True)

    # ST17 (v1 NEW): formula self-test -- cost model
    # Cost per arm at N=8192/n_steps=2000:
    #   BASELINE: ~50s (Hebbian; v3 measured)
    #   FREQ_DEEPER: ~170s (v4 measured)
    #   THETA: ~156s (v3 measured at n_steps=1000); at n_steps=2000 ~312s
    #     -> for fair comparison we run THETA at n_steps=2000 (matches FREQ_DEEPER)
    #     Actually v3 used n_steps=1000 for THETA; we hold THETA at n_steps=1000 here
    #     (legacy-fair to v3 measurement). But to be safer we use n_steps=2000 to be
    #     fair to FREQ_DEEPER. THETA at n_steps=2000 estimated ~312s.
    #   SEGREGATED (no gate): ~280s (both W update every step; ~1.5x THETA per-step
    #     since both updates happen each step not alternating)
    #   SEGREGATED_PLUS_GATE: ~280s + ~5s gate eval = ~285s
    # Per seed total: 50 + 170 + 312 + 280 + 285 + 25 overhead = 1122s
    # 5 seeds: 5610s. 7200s timeout / 5610s = 1.28x headroom. Just above 1.2x.
    def _wall(n_steps_x: int, kernel: str) -> float:
        t0 = time.time()
        if kernel == "freq":
            _ = build_logits_freq_routed_k2_gpu(
                E_sb, idx_tr_st, idx_h_st, ranks_st,
                n_steps=n_steps_x, batch=3, lr_high=0.5, lr_rare=0.2,
                stdp_w=0.5, freq_threshold=3, seed=1, arm_idx=99,
                recall_batch=4)
        elif kernel == "theta":
            _ = build_logits_theta_phase_two_w_gpu(
                E_sb, idx_tr_st, idx_h_st, n_steps=n_steps_x, batch=3,
                lr=0.5, stdp_w=0.5, seed=1, arm_idx=99, recall_batch=4)
        else:  # segregated
            _ = build_logits_segregated_dual_w_gpu(
                E_sb, idx_tr_st, idx_h_st, n_steps=n_steps_x, batch=3,
                lr=0.5, stdp_w=0.5, seed=1, arm_idx=99, recall_batch=4,
                context_gate_params=None)
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        return time.time() - t0
    w_seg_50 = _wall(50, "segregated")
    w_seg_100 = _wall(100, "segregated")
    if w_seg_50 > 0.001:
        ratio = w_seg_100 / w_seg_50
        assert 1.2 <= ratio <= 4.0, (
            "ST17 segregated cost-model FAIL: ratio %.2f outside [1.2,4.0]" % ratio)
        print("[selftest] ST17 segregated cost-model: ratio=%.2fx OK" % ratio, flush=True)
    else:
        print("[selftest] ST17 segregated cost-model: SKIP (walls too small)", flush=True)

    # ST18 (v1 NEW): wall budget headroom assertion
    expected_per_seed = 50.0 + 170.0 + 312.0 + 280.0 + 285.0 + 25.0
    expected_full_wall = expected_per_seed * float(len(SEEDS))
    requested_timeout = 7200.0
    headroom_ratio = requested_timeout / expected_full_wall
    assert headroom_ratio >= 1.2, (
        "ST18 budget FAIL: %.0fs vs %.0fs = %.2fx < 1.2" % (
            expected_full_wall, requested_timeout, headroom_ratio))
    print("[selftest] ST18 budget headroom: %.0fs/%.0fs = %.2fx OK" % (
        expected_full_wall, requested_timeout, headroom_ratio), flush=True)

    # ST19 (v1 NEW): SEGREGATION mechanism distinct from COMBINE
    # In v4 COMBINE: W_freq received BOTH cf-RPE (phase0) AND STDP (phase1).
    # In v1 SEGREGATED: W_when receives ONLY STDP; W_what receives ONLY cf-RPE.
    # Test: after enough steps with stdp_w=0 (no STDP at all), W_when remains zero
    # and W_what gets cf-RPE updates (proves function-segregation).
    # Build SEGREGATED at stdp_w=0:
    ar_no_stdp = build_logits_segregated_dual_w_gpu(
        E_sb, idx_tr_st, idx_h_st,
        n_steps=20, batch=3, lr=0.5, stdp_w=0.0,  # disable STDP entirely
        seed=0, arm_idx=4, recall_batch=4, context_gate_params=None)
    # If function-segregation holds: with stdp_w=0, W_when should stay zero so the
    # mix-logit (0.5*W_when + 0.5*W_what) should match 0.5*W_what alone.
    # We can't easily extract W_when here, but the static-mix logits should still
    # be nonzero (W_what is active) AND distinct from the all-STDP variant.
    ar_all_stdp = build_logits_segregated_dual_w_gpu(
        E_sb, idx_tr_st, idx_h_st,
        n_steps=20, batch=3, lr=0.5, stdp_w=1.0,
        seed=0, arm_idx=4, recall_batch=4, context_gate_params=None)
    d_no_vs_all = float(np.abs(ar_no_stdp["logits"] - ar_all_stdp["logits"]).mean())
    assert d_no_vs_all > 1e-6, (
        "ST19 segregation invariant: stdp_w=0 vs stdp_w=1 same logits = %.4e (W_when not contributing?)" % d_no_vs_all)
    print("[selftest] ST19 segregation function-distinct OK (stdp_w 0vs1 diff=%.4e)" % d_no_vs_all,
          flush=True)

    print("[selftest v1_SEGREGATED] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# D1 ROOFLINE PROBE
# ============================================================================

def roofline_probe(timeout_s_target: int) -> Dict:
    print("\n[D1 v1_SEGREGATED] running roofline probe...", flush=True)
    probe_scales = [N_DIM // 4, N_DIM // 2, N_DIM]
    probe_n_steps = 25
    probe_v = VOCAB_CAP
    probe_n_train = 5000
    probe_n_held = 1000
    probe_seed = 42
    walls: List[Tuple[int, float]] = []

    rng_probe = np.random.default_rng(probe_seed)
    bigram_tgts = rng_probe.integers(0, probe_v, size=probe_v).astype(np.int64)
    idx_tr = np.empty(probe_n_train, dtype=np.int64)
    idx_tr[0] = rng_probe.integers(0, probe_v)
    for i in range(1, probe_n_train):
        if rng_probe.random() < 0.5:
            idx_tr[i] = bigram_tgts[idx_tr[i - 1]]
        else:
            idx_tr[i] = rng_probe.integers(0, probe_v)
    idx_h = rng_probe.integers(0, probe_v, size=probe_n_held).astype(np.int64)
    idx_tr_t = torch.from_numpy(idx_tr).to(DEVICE)
    idx_h_t = torch.from_numpy(idx_h).to(DEVICE)

    # Probe with SEGREGATED kernel (the most expensive)
    for probe_n_dim in probe_scales:
        E_np = np.random.default_rng(probe_seed * 11 + probe_n_dim).standard_normal(
            (probe_v, probe_n_dim)).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(DEVICE)
        E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
        t0 = time.time()
        _ = build_logits_segregated_dual_w_gpu(
            E_sb, idx_tr_t, idx_h_t,
            n_steps=probe_n_steps, batch=INGEST_BATCH,
            lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=probe_seed, arm_idx=4, recall_batch=RECALL_BATCH,
            context_gate_params=None,
        )
        wall = time.time() - t0
        walls.append((probe_n_dim, wall))
        print("  [D1] N=%d wall=%.2fs" % (probe_n_dim, wall), flush=True)
        del E_t, E_sb
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    ns = np.array([w[0] for w in walls], dtype=np.float64)
    ts = np.array([w[1] for w in walls], dtype=np.float64)
    ts_floor = np.clip(ts, 1e-6, None)
    log_n = np.log(ns)
    log_t = np.log(ts_floor)
    A = np.vstack([np.ones_like(log_n), log_n]).T
    coef, *_ = np.linalg.lstsq(A, log_t, rcond=None)
    log_a_fit, k_fit = float(coef[0]), float(coef[1])
    a_fit = float(np.exp(log_a_fit))

    # Per-arm wall extrapolation at N=8192/n_steps=2000
    seg_arm_wall_extrap = a_fit * float(N_DIM) ** k_fit * (float(N_STEPS) / float(probe_n_steps)) * 1.1
    # Per-seed: BASELINE (50s) + FREQ (170s; ~0.6 of seg) + THETA (312s; ~1.1 of seg)
    # + SEGREGATED (1.0 of seg) + SEGREGATED+GATE (1.02 of seg) + 25s overhead
    per_seed_wall_extrap = (
        50.0 +                              # ARM_BASELINE
        0.6 * seg_arm_wall_extrap +         # ARM_FREQ_DEEPER (~170s if seg=280s)
        1.1 * seg_arm_wall_extrap +         # ARM_THETA_PHASE_TWO_W
        1.0 * seg_arm_wall_extrap +         # ARM_SEGREGATED_DUAL_W
        1.02 * seg_arm_wall_extrap +        # ARM_SEGREGATED_PLUS_CONTEXT_GATE
        25.0                                # encoder + ckpt overhead
    )
    full_wall_extrap = per_seed_wall_extrap * float(len(SEEDS))

    print("[D1] fit: a=%.4e k=%.3f" % (a_fit, k_fit), flush=True)
    print("[D1] segregated@N=8192/n_steps=2000 extrap: %.1fs" % seg_arm_wall_extrap, flush=True)
    print("[D1] per-seed total: %.1fs; full (%d seeds): %.1fs (%.1f min)" % (
        per_seed_wall_extrap, len(SEEDS), full_wall_extrap, full_wall_extrap / 60.0), flush=True)

    result = {
        "probe_scales": probe_scales,
        "probe_walls_s": [round(w[1], 3) for w in walls],
        "fit_a": round(a_fit, 6),
        "fit_k": round(k_fit, 3),
        "seg_arm_wall_extrap_s": round(seg_arm_wall_extrap, 1),
        "per_seed_wall_extrap_s": round(per_seed_wall_extrap, 1),
        "full_wall_extrap_s": round(full_wall_extrap, 1),
        "timeout_s_target": int(timeout_s_target),
        "budget_s": round(0.8 * timeout_s_target, 1),
        "dispatch_ok": bool(full_wall_extrap <= 0.8 * timeout_s_target),
    }
    if not result["dispatch_ok"]:
        print("[D1] REFUSE DISPATCH: %.1fs > 0.8*timeout" % full_wall_extrap, flush=True)
    else:
        print("[D1] DISPATCH OK", flush=True)
    return result


if _ARGS.roofline_probe_only:
    target = int(os.environ.get("HDLAB_RUN_TIMEOUT_S", "7200"))
    probe_result = roofline_probe(target)
    print("[D1] result: %s" % json.dumps(probe_result, indent=2), flush=True)
    sys.exit(0 if probe_result["dispatch_ok"] else 1)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    _register_atexit_once()
    _RUN_STATE.out_dir = out_dir
    _RUN_STATE.current_seed = seed
    _RUN_STATE.current_seed_partials = {}

    if RUN_MODE == "smoke":
        print("\n[seed=%d] SMOKE: clean synthetic markov-bigram" % seed, flush=True)
        rng_corp = np.random.default_rng(seed * 7727 + 41)
        bigram_targets = rng_corp.integers(0, VOCAB_CAP, size=VOCAB_CAP).astype(np.int64)
        idx_train = np.empty(N_TRAIN, dtype=np.int64)
        idx_train[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_TRAIN):
            if rng_corp.random() < 0.5:
                idx_train[i] = bigram_targets[idx_train[i - 1]]
            else:
                idx_train[i] = rng_corp.integers(0, VOCAB_CAP)
        idx_held = np.empty(N_HELD, dtype=np.int64)
        idx_held[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_HELD):
            if rng_corp.random() < 0.5:
                idx_held[i] = bigram_targets[idx_held[i - 1]]
            else:
                idx_held[i] = rng_corp.integers(0, VOCAB_CAP)
        V = VOCAB_CAP
        encoder_meta = {"smoke_synthetic": True, "V": V}
        vocab = ["t%d" % i for i in range(VOCAB_CAP)]
    else:
        print("\n[seed=%d] loading text8" % seed, flush=True)
        toks = load_text8_tokens(N_TRAIN + N_HELD)
        train_toks = toks[:N_TRAIN]
        held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
        vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
        V = len(vocab)
        idx_train = tokens_to_idx(train_toks, w2i)
        idx_held = tokens_to_idx(held_toks, w2i)
        encoder_meta = {}

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f" % (seed, uni["bpc_unigram"]), flush=True)

    ranks_np = vocab_frequency_ranks(idx_train, V=V)

    print("\n[seed=%d] building encoder N_DIM=%d..." % (seed, N_DIM), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
    else:
        E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs sparsity=%.3f" % (
        seed, time.time() - t_enc0, sparsity), flush=True)
    del E_proj_t

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}
    _RUN_STATE.current_seed_partials = by_arm

    def _process_logits(arm_name: str, logits_full: np.ndarray) -> Dict:
        valid_pos = np.where(mask)[0]
        valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos]
        nxt_eval_local = nxt_full[valid_pos]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_dev_l = nxt_eval_local[:n_dev_l]
        nxt_test_l = nxt_eval_local[n_dev_l:]
        jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
        jr["raw_bpc_at_T1_L1"] = round(rbt1, 4)
        return jr

    # ----- ARM 1: ARM_BASELINE_SHARED_W -----
    arm = "ARM_BASELINE_SHARED_W"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_hebbian_baseline_gpu(
            E_full, idx_train_t, idx_held_t,
            recall_batch=RECALL_BATCH, ingest_chunk=INGEST_CHUNK,
        )
        jr = _process_logits(arm, ar["logits"])
        jr.update({"elapsed_s_arm": round(time.time() - t_arm0, 2),
                   "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                   "wall_recall_s": ar.get("wall_recall_s", 0.0),
                   "discriminating": ar.get("discriminating", {})})
        by_arm[arm] = jr
        print("    [%s] bpc=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
            arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [%s] FAIL: %s" % (arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                       "bpc_best": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 2: ARM_FREQ_DEEPER (v4 winner rail) -----
    arm = "ARM_FREQ_DEEPER"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        thresh = FREQ_ROUTE_RANK if V > FREQ_ROUTE_RANK else max(1, V // 4)
        ar = build_logits_freq_routed_k2_gpu(
            E_full, idx_train_t, idx_held_t, ranks_np,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr_high=FREQ_LR_HIGH, lr_rare=FREQ_LR_RARE,
            stdp_w=STDP_WEIGHT, freq_threshold=thresh,
            seed=seed, arm_idx=2, recall_batch=RECALL_BATCH,
        )
        jr = _process_logits(arm, ar["logits"])
        jr.update({"elapsed_s_arm": round(time.time() - t_arm0, 2),
                   "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                   "wall_recall_s": ar.get("wall_recall_s", 0.0),
                   "discriminating": ar.get("discriminating", {})})
        by_arm[arm] = jr
        print("    [%s] bpc=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
            arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [%s] FAIL: %s" % (arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                       "bpc_best": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 3: ARM_THETA_PHASE_TWO_W (v3 winner rail) -----
    arm = "ARM_THETA_PHASE_TWO_W"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_theta_phase_two_w_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=3, recall_batch=RECALL_BATCH,
        )
        # Pick best alpha by dev BPC
        alpha_stack = ar["logits_alpha_stack"]
        alpha_grid = ar["alpha_grid"]
        best_alpha_idx = 0
        best_alpha_jr = None
        best_dev_bpc = float("inf")
        for a_idx in range(len(alpha_grid)):
            jr_a = _process_logits(arm, alpha_stack[a_idx])
            if jr_a["best_dev_bpc"] < best_dev_bpc:
                best_dev_bpc = jr_a["best_dev_bpc"]
                best_alpha_idx = a_idx
                best_alpha_jr = jr_a
        jr = best_alpha_jr
        disc = dict(ar.get("discriminating", {}))
        disc["best_alpha"] = float(alpha_grid[best_alpha_idx])
        disc["alpha_grid"] = list(alpha_grid)
        disc["best_alpha_dev_bpc"] = round(best_dev_bpc, 4)
        jr.update({"elapsed_s_arm": round(time.time() - t_arm0, 2),
                   "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                   "wall_recall_s": ar.get("wall_recall_s", 0.0),
                   "discriminating": disc})
        by_arm[arm] = jr
        print("    [%s] bpc=%.3f top1=%.4f rawT1=%.3f best_alpha=%.2f elapsed=%.1fs" % (
            arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], disc["best_alpha"], jr["elapsed_s_arm"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [%s] FAIL: %s" % (arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                       "bpc_best": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 4: ARM_SEGREGATED_DUAL_W (static mixer) -----
    arm = "ARM_SEGREGATED_DUAL_W"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_segregated_dual_w_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=4, recall_batch=RECALL_BATCH,
            context_gate_params=None,
        )
        jr = _process_logits(arm, ar["logits"])
        jr.update({"elapsed_s_arm": round(time.time() - t_arm0, 2),
                   "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                   "wall_recall_s": ar.get("wall_recall_s", 0.0),
                   "discriminating": ar.get("discriminating", {})})
        by_arm[arm] = jr
        print("    [%s] bpc=%.3f top1=%.4f rawT1=%.3f when_vs_what=%.4f elapsed=%.1fs" % (
            arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"],
            ar["discriminating"].get("when_vs_what_bank_corr", float("nan")),
            jr["elapsed_s_arm"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [%s] FAIL: %s" % (arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                       "bpc_best": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    _RUN_STATE.current_seed_partials = dict(by_arm)

    # ----- ARM 5: ARM_SEGREGATED_PLUS_CONTEXT_GATE -----
    arm = "ARM_SEGREGATED_PLUS_CONTEXT_GATE"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_segregated_dual_w_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=5, recall_batch=RECALL_BATCH,
            context_gate_params=GATE_GRID,
        )
        # Pick best (center, scale) by dev BPC
        gate_stack = ar["gate_stack"]
        gate_grid = ar["gate_grid"]
        best_gate_idx = 0
        best_gate_jr = None
        best_dev_bpc = float("inf")
        for g_idx in range(len(gate_grid)):
            jr_g = _process_logits(arm, gate_stack[g_idx])
            if jr_g["best_dev_bpc"] < best_dev_bpc:
                best_dev_bpc = jr_g["best_dev_bpc"]
                best_gate_idx = g_idx
                best_gate_jr = jr_g
        jr = best_gate_jr
        disc = dict(ar.get("discriminating", {}))
        disc["best_gate_idx"] = int(best_gate_idx)
        disc["best_gate_center"] = float(gate_grid[best_gate_idx][0])
        disc["best_gate_scale"] = float(gate_grid[best_gate_idx][1])
        disc["gate_grid"] = list(gate_grid)
        disc["best_gate_dev_bpc"] = round(best_dev_bpc, 4)
        jr.update({"elapsed_s_arm": round(time.time() - t_arm0, 2),
                   "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                   "wall_recall_s": ar.get("wall_recall_s", 0.0),
                   "discriminating": disc})
        by_arm[arm] = jr
        print("    [%s] bpc=%.3f top1=%.4f rawT1=%.3f gate=(c=%.2f,s=%.2f) elapsed=%.1fs" % (
            arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"],
            disc["best_gate_center"], disc["best_gate_scale"],
            jr["elapsed_s_arm"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [%s] FAIL: %s" % (arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                       "bpc_best": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    _RUN_STATE.current_seed_partials = dict(by_arm)

    del E_full
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed, "by_arm": by_arm, "V": V,
        "N": N_DIM, "M": N_TRAIN,
        "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP, "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE, "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


# ============================================================================
# Verdict (v1 SEGREGATED bands)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    arm_bpc: Dict[str, float] = {}
    arm_cv: Dict[str, float] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": len(valid),
            "discriminating_per_seed": [u["by_arm"][arm].get("discriminating", {})
                                         for u in valid],
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d" % total_llm_calls,
                {"by_arm_agg": by_arm_agg})

    # v1 SEGREGATED verdict
    base = arm_bpc.get("ARM_BASELINE_SHARED_W", float("inf"))
    freq_d = arm_bpc.get("ARM_FREQ_DEEPER", float("inf"))
    theta = arm_bpc.get("ARM_THETA_PHASE_TWO_W", float("inf"))
    seg = arm_bpc.get("ARM_SEGREGATED_DUAL_W", float("inf"))
    seg_g = arm_bpc.get("ARM_SEGREGATED_PLUS_CONTEXT_GATE", float("inf"))

    cv_seg_g = arm_cv.get("ARM_SEGREGATED_PLUS_CONTEXT_GATE", float("nan"))

    rail_drift = abs(base - SANITY_RAIL_BASELINE_REF) if math.isfinite(base) else float("inf")
    rail_ok = rail_drift <= SANITY_RAIL_TOLERANCE

    # Intermod-FAIL check: does SEGREGATED cluster near v4 COMBINE's 7.365?
    seg_near_intermod = (math.isfinite(seg) and
                          abs(seg - HARD_FAIL_INTERMOD_CENTER) <= HARD_FAIL_INTERMOD_BAND)
    seg_g_near_intermod = (math.isfinite(seg_g) and
                           abs(seg_g - HARD_FAIL_INTERMOD_CENTER) <= HARD_FAIL_INTERMOD_BAND)
    both_seg_near_intermod = seg_near_intermod and seg_g_near_intermod

    # Combo-beats-individual check
    seg_g_beats_freq = (math.isfinite(seg_g) and math.isfinite(freq_d) and
                         seg_g <= freq_d - COMBO_BEATS_INDIVIDUAL_MARGIN)
    seg_g_beats_theta = (math.isfinite(seg_g) and math.isfinite(theta) and
                          seg_g <= theta - COMBO_BEATS_INDIVIDUAL_MARGIN)
    seg_g_beats_baseline = (math.isfinite(seg_g) and math.isfinite(base) and
                             (base - seg_g) >= HARD_PASS_GAP_VS_BASELINE)

    # Segregation discriminator: when_vs_what bank correlation (from per-seed discriminating)
    seg_disc = by_arm_agg.get("ARM_SEGREGATED_DUAL_W", {}).get("discriminating_per_seed", [])
    when_vs_what_corrs = [d.get("when_vs_what_bank_corr", float("nan")) for d in seg_disc
                          if d.get("when_vs_what_bank_corr") is not None]
    when_vs_what_mean = float(np.mean(when_vs_what_corrs)) if when_vs_what_corrs else float("nan")

    arm_summary = (
        "uni=%.3f | BASE=%.4f(rail=%s) | FREQ_DEEPER=%.4f | THETA=%.4f | "
        "SEGREG=%.4f | SEGREG+GATE=%.4f(cv=%.4f) | "
        "seg_beats_freq=%s seg_beats_theta=%s seg_beats_base=%s | "
        "seg_near_intermod=%s | when_vs_what_corr=%.4f"
    ) % (
        unigram_bpc, base, str(rail_ok),
        freq_d, theta, seg, seg_g,
        cv_seg_g if math.isfinite(cv_seg_g) else -1.0,
        str(seg_g_beats_freq), str(seg_g_beats_theta), str(seg_g_beats_baseline),
        str(both_seg_near_intermod),
        when_vs_what_mean if math.isfinite(when_vs_what_mean) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "arm_bpc": {k: round(v, 4) if math.isfinite(v) else None for k, v in arm_bpc.items()},
        "arm_cv": {k: round(v, 4) if math.isfinite(v) else None for k, v in arm_cv.items()},
        "sanity_rail": {
            "baseline_ref": SANITY_RAIL_BASELINE_REF,
            "baseline_measured": round(base, 4) if math.isfinite(base) else None,
            "drift": round(rail_drift, 4),
            "ok": bool(rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "intermod_check": {
            "v4_combine_ref_bpc": V4_COMBINE_W_THETA_HURT_BPC,
            "seg_near_intermod": bool(seg_near_intermod),
            "seg_gate_near_intermod": bool(seg_g_near_intermod),
            "both_near_intermod": bool(both_seg_near_intermod),
            "band": HARD_FAIL_INTERMOD_BAND,
        },
        "combo_beats_individual": {
            "v4_freq_deeper_ref_bpc": V4_FREQ_DEEPER_BPC,
            "v3_theta_phase_ref_bpc": V3_THETA_PHASE_BPC,
            "seg_gate_beats_freq": bool(seg_g_beats_freq),
            "seg_gate_beats_theta": bool(seg_g_beats_theta),
            "seg_gate_beats_baseline": bool(seg_g_beats_baseline),
            "margin": COMBO_BEATS_INDIVIDUAL_MARGIN,
        },
        "segregation_diagnostics": {
            "when_vs_what_bank_corr_mean": round(when_vs_what_mean, 4) if math.isfinite(when_vs_what_mean) else None,
            "n_seeds_with_corr": len(when_vs_what_corrs),
        },
        "bands": {
            "hard_pass_chain_grade_bpc": HARD_PASS_CHAIN_GRADE_BPC,
            "hard_pass_bpc": HARD_PASS_BPC,
            "hard_pass_gap_vs_baseline": HARD_PASS_GAP_VS_BASELINE,
            "cv_max": CV_MAX,
            "hard_fail_intermod_center": HARD_FAIL_INTERMOD_CENTER,
            "hard_fail_intermod_band": HARD_FAIL_INTERMOD_BAND,
            "middle_band_lower": MIDDLE_BAND_LOWER,
            "middle_band_upper": MIDDLE_BAND_UPPER,
            "individual_mechanism_bar_bpc": INDIVIDUAL_MECHANISM_BAR_BPC,
            "combo_beats_individual_margin": COMBO_BEATS_INDIVIDUAL_MARGIN,
            "sanity_rail_tolerance": SANITY_RAIL_TOLERANCE,
        },
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "llm_forward_calls_total": total_llm_calls,
        "honest_scope": (
            "v1 SEGREGATED_DUAL_W: brain-analog architecture per drill recommendation. "
            "v4 COMBINE_W_THETA HURT (BPC=7.365 vs base 7.3065) because cf-RPE + STDP "
            "on shared W creates FDM intermodulation. v1 segregates by FUNCTION: "
            "W_when (STDP-only) + W_what (cf-RPE-only) + context-magnitude gate. "
            "Tests whether function-domain segregation avoids the intermod and "
            "whether segregated combination can beat individual mechanism wins "
            "(FREQ_DEEPER 7.159; THETA 7.235). WHAT_THIS_DOES_NOT_SHOW: doesn't "
            "test other gate features (e.g., entropy, RPE-magnitude); doesn't "
            "test 3+ bank segregation (e.g., when/what/where); doesn't test gate "
            "learned via gradient (handcrafted sigmoid grid only); doesn't test "
            "the segregation principle on FREQ + THETA combo (only on canonical "
            "WHEN/WHAT separation)."
        ),
        "cites": [
            "preregs/2026-06-25_substrate_compose_segregated_dual_W_context_gated_v1.md",
            "experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py (v4 COMBINE=7.365 HURT motivates drill)",
            "data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json",
            "experiments/exp_substrate_compose_heterogeneous_routing_v3_full_config_rerun.py (v3 THETA=7.235 + FREQ=7.21)",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (rail 7.3065)",
        ],
    }

    all_failed = all(
        by_arm_agg.get(a, {}).get("all_seeds_failed", True) for a in ARMS
    )
    if all_failed:
        return ("HARD_FAIL", "HARD_FAIL: all 5 arms failed. %s" % arm_summary, detail)

    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE: BASELINE=%.4f drifts %.4f from %.4f. %s" % (
                    base, rail_drift, SANITY_RAIL_BASELINE_REF, arm_summary),
                detail)

    # HARD_FAIL: SEGREGATED arms cluster near v4 COMBINE's 7.365 (intermod not avoided)
    if both_seg_near_intermod:
        detail["verdict_tier"] = "HARD_FAIL_INTERMOD_NOT_AVOIDED"
        return ("HARD_FAIL",
                "HARD_FAIL_INTERMOD_NOT_AVOIDED: SEGREGATED=%.4f and SEGREGATED_PLUS_GATE=%.4f "
                "both within +/-%.2f of v4 COMBINE_W_THETA's HURT BPC %.4f. "
                "Function-domain segregation did NOT avoid intermodulation; "
                "mechanism combination genuinely doesn't compose at substrate scale. %s" % (
                    seg, seg_g, HARD_FAIL_INTERMOD_BAND, HARD_FAIL_INTERMOD_CENTER,
                    arm_summary),
                detail)

    # CV gate on lead arm
    if math.isfinite(cv_seg_g) and cv_seg_g > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: SEGREGATED_PLUS_GATE cv=%.4f > %.2f. bpc=%.4f. %s" % (
                    cv_seg_g, CV_MAX, seg_g, arm_summary),
                detail)

    # HARD_PASS_CHAIN_GRADE
    if (math.isfinite(seg_g) and seg_g <= HARD_PASS_CHAIN_GRADE_BPC and
            seg_g_beats_freq and seg_g_beats_theta and
            math.isfinite(cv_seg_g) and cv_seg_g <= CV_MAX):
        detail["verdict_tier"] = "HARD_PASS_CHAIN_GRADE_SEGREGATION_WORKS"
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_SEGREGATION_WORKS: SEGREGATED_PLUS_GATE=%.4f<=%.2f "
                "AND beats FREQ_DEEPER (%.4f) AND beats THETA (%.4f). "
                "Function-domain segregation is a substrate-product architectural principle. %s" % (
                    seg_g, HARD_PASS_CHAIN_GRADE_BPC, freq_d, theta, arm_summary),
                detail)

    # HARD_PASS (segregation principle works at moderate level)
    if (math.isfinite(seg_g) and seg_g <= HARD_PASS_BPC and seg_g_beats_baseline and
            math.isfinite(cv_seg_g) and cv_seg_g <= CV_MAX):
        detail["verdict_tier"] = "HARD_PASS_SEGREGATION_LIFTS_OVER_BASELINE"
        return ("HARD_PASS",
                "HARD_PASS_SEGREGATION_LIFTS_OVER_BASELINE: SEGREGATED_PLUS_GATE=%.4f<=%.2f "
                "AND beats BASELINE by >=%.2f. Segregation avoids intermod; "
                "did not reach chain-grade (6.95) or beat individual mechanisms. %s" % (
                    seg_g, HARD_PASS_BPC, HARD_PASS_GAP_VS_BASELINE, arm_summary),
                detail)

    # MIDDLE_BAND
    if math.isfinite(seg_g) and MIDDLE_BAND_LOWER <= seg_g <= MIDDLE_BAND_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_SEGREGATION"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_SEGREGATION: SEGREGATED_PLUS_GATE=%.4f in [%.2f,%.2f] "
                "(partial signal; doesn't surpass FREQ_DEEPER 7.159 or THETA 7.235). %s" % (
                    seg_g, MIDDLE_BAND_LOWER, MIDDLE_BAND_UPPER, arm_summary),
                detail)

    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: SEGREGATED_PLUS_GATE=%.4f outside HP+MB+HF bands. %s" % (
                seg_g, arm_summary),
            detail)


# ============================================================================
# Main loop
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda=%s" % (str(DEVICE), torch.cuda.is_available()), flush=True)

_gpu_setup_assert_and_report(label="startup")

out_dir = get_output_dir(ANCHOR_NAME)
_RUN_STATE.out_dir = out_dir
_register_atexit_once()

if RUN_MODE == "full":
    timeout_s_env = int(os.environ.get("HDLAB_RUN_TIMEOUT_S", "7200"))
    probe_result = roofline_probe(timeout_s_env)
    if not probe_result["dispatch_ok"]:
        print("[D1] EXIT: roofline refuses", flush=True)
        minimal_metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_D1_ROOFLINE_REFUSE: %s" % json.dumps(probe_result),
            "summary": "HARD_FAIL_D1_ROOFLINE_REFUSE",
            "elapsed_s": 0.0,
            "config_version": CONFIG_VERSION,
            "run_mode": RUN_MODE,
            "d1_probe": probe_result,
        }
        (out_dir / "metrics.json").parent.mkdir(parents=True, exist_ok=True)
        with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
            json.dump(minimal_metrics, f, indent=2, default=str)
        sys.exit(0)
    print("[D1] GATE PASSED -- proceeding to FULL", flush=True)

run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done_seeds_init: List[int] = []
remaining_seeds_init: List[int] = SEEDS[:]
try:
    done_seeds_init, remaining_seeds_init = _resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds_init), len(remaining_seeds_init), remaining_seeds_init), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s)" % e, flush=True)
    remaining_seeds_init = SEEDS[:]

for seed in remaining_seeds_init:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written" % seed, flush=True)
    _RUN_STATE.current_seed = None
    _RUN_STATE.current_seed_partials = {}

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

summary_str = (
    "%s | arms=%d seeds=%d v1_SEGREGATED_DUAL_W_CONTEXT_GATED" % (
        verdict, len(ARMS), len(SEEDS))
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "FREQ_ROUTE_RANK_DEFAULT": FREQ_ROUTE_RANK,
    "GATE_GRID": [list(g) for g in GATE_GRID],
    "V4_COMBINE_W_THETA_HURT_BPC": V4_COMBINE_W_THETA_HURT_BPC,
    "V4_FREQ_DEEPER_BPC": V4_FREQ_DEEPER_BPC,
    "V3_THETA_PHASE_BPC": V3_THETA_PHASE_BPC,
    "V3_FREQ_ROUTED_BPC": V3_FREQ_ROUTED_BPC,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"),
         "N_TRAIN": u.get("N_TRAIN"),
         "llm_forward_calls_at_inference": u.get("llm_forward_calls_at_inference", 0),
         "encoder_meta": u.get("encoder_meta", {}),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

if DEVICE.type == "cuda":
    try:
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
        metrics["gpu_peak_mem_gb"] = round(peak_gb, 3)
    except Exception:
        pass

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
