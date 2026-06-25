"""
substrate_compose_freq_routing_v5_DEFINITIVE -- v4 ARM_FREQ_DEEPER_TRAIN landed
CHAIN_GRADE_PARTIAL at BPC=7.159 (cv=0.0029, beat baseline 7.3065 by 0.1475).
v4 was the first Stage 2 architectural win but NOT DEFINITIVE because:
  - n=3 seeds (this v5 ships 5 seeds for tighter cv estimate)
  - single config (N_DIM=8192 only); could be config-fragile

v5 converts to DEFINITIVE via:
  1. 5 seeds [7, 13, 17, 23, 29] (was 3)
  2. Cross-N replication: same FREQ_DEEPER arm at N_DIM=4096 as well as N=8192
     to show architectural advantage isn't N=8192-specific
  3. ARM_FREQ_DEEPER_NSTEPS_3000 to test upper-bound of training-depth lever

If FREQ_DEEPER beats its same-N baseline at BOTH N=8192 AND N=4096 with cv<=0.03
across 5 seeds, the v4 win is DEFINITIVE.

LANE: 1 (substrate-native). ROUTING: GPU overnight_queue. BUDGET: 7200s.

ARMS (5):
  1. ARM_BASELINE_N8192 (Hebbian sanity rail; must reproduce 7.3065 +/- 0.05)
  2. ARM_FREQ_DEEPER_N8192 (the v4 winner at N=8192; freq_rank=100, lr_high=0.5,
       lr_rare=0.2, n_steps=2000)
  3. ARM_BASELINE_N4096 (Hebbian sanity rail at N=4096; reference TBD per run)
  4. ARM_FREQ_DEEPER_N4096 (replicate at smaller N; tests architectural advantage
       isn't N=8192-specific)
  5. ARM_FREQ_DEEPER_NSTEPS_3000 (N=8192, n_steps=3000; tests upper-bound of
       training-depth lever)

Phase-diagram scan baked in: 2 N values (8192, 4096) cross 2 n_steps values
(2000, 3000) on the FREQ arm. Defines operating envelope around v4 winner.

HARD bands (PROSPECTIVE per Skunkworks META_RULE_retrospective_band_correction;
v5 is genuine new cell -- 5 seeds + cross-N replication is not a retrofit):

  HARD_PASS_CHAIN_GRADE_DEFINITIVE:
    - ARM_FREQ_DEEPER_N8192 BPC <= 7.20
    - AND ARM_FREQ_DEEPER_N4096 BPC beats its baseline by >= 0.10 (cross-config
      replication confirms architecture, not just config)
    - AND CV <= 0.03 across 5 seeds on ARM_FREQ_DEEPER_N8192
    - AND both sanity rails pass (BASELINE_N8192 within +/-0.05 of 7.3065 AND
      BASELINE_N4096 within +/-0.05 of measured-this-cell N=4096 ref)

  HARD_PASS (single-config replication of v4 finding):
    - ARM_FREQ_DEEPER_N8192 BPC <= 7.20
    - AND CV <= 0.05 (same as v4 bar; 5 seeds is just tighter measurement)
    - AND sanity_rail BASELINE_N8192 OK

  HARD_FAIL_NULL (replication failed; v4 was noise):
    - ARM_FREQ_DEEPER_N8192 BPC >= 7.30

  MIDDLE_BAND:
    - ARM_FREQ_DEEPER_N8192 BPC in [7.20, 7.30] (partial reproduction)

Sanity rails BOTH must pass (per cell spec). N=4096 baseline ref will be
recorded this cell; the N=4096 BASELINE arm establishes the rail concurrently.

DISCRIMINATOR (per Fix #28):
  - per-arm BPC sits in detail.by_arm_agg.<arm>.bpc_best_mean
  - cross-N gap sits in detail.crossN_check.{n8192_lift, n4096_lift, both_pass}
  - upper-bound check sits in detail.nsteps_3000_vs_2000.{n8192_delta, plateaued}

DISCIPLINES:
  D1 roofline probe before estimating wall
  D2 atexit + per-seed checkpoint MANDATORY
  Self-test PASS gate
  NO local smoke (GPU cell; route directly to overnight_queue)
  Pre-reg notes committed BEFORE dispatch
  ASCII only
  Per Fix #28: per-arm metrics; verdict_msg cites per-arm numerics
  Per Fix #24: GPU MUST actually use GPU (torch.cuda + batched ops)

CITES:
  preregs/2026-06-25_substrate_compose_freq_routing_v5_DEFINITIVE.md
  experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py (v4 base)
  data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json
    (ARM_FREQ_DEEPER_TRAIN = 7.159 CHAIN_GRADE_PARTIAL)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
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

ANCHOR_NAME = "substrate_compose_freq_routing_v5_DEFINITIVE"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# v5 Pre-reg threshold bands
# ============================================================================
SANITY_RAIL_BASELINE_REF_N8192 = 7.3065  # fair_harness rail at N=8192
SANITY_RAIL_TOLERANCE = 0.05

# Per cell spec:
HARD_PASS_CAP_BPC = 7.20             # HARD_PASS BPC bar on ARM_FREQ_DEEPER_N8192
HARD_PASS_GAP_VS_BASELINE = 0.10     # min lift over same-N baseline
CV_MAX_HARD_PASS = 0.05              # HARD_PASS CV cap (was v4 0.05; same here)
CV_MAX_CHAIN_GRADE_DEFINITIVE = 0.03 # tighter CV for DEFINITIVE
HARD_FAIL_NULL_FLOOR = 7.30          # HARD_FAIL if ARM_FREQ_DEEPER_N8192 >= this
MIDDLE_BAND_LOWER = 7.20
MIDDLE_BAND_UPPER = 7.30

# Reference: v4 measured ARM_FREQ_DEEPER_TRAIN = 7.159 (CHAIN_GRADE_PARTIAL).
# v5 expects within +/- 0.05 of v4 ref to call "replicated".
V4_FREQ_DEEPER_REF_BPC = 7.159
V4_REPLICATION_TOLERANCE = 0.05

# ============================================================================
# Primitive knob parameters
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64

FREQ_ROUTE_RANK = 100
FREQ_LR_HIGH = 0.5
FREQ_LR_RARE = 0.2

TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"

# v5 5-arm DEFINITIVE: cross-N replication + n_steps upper-bound
ARMS = [
    "ARM_BASELINE_N8192",
    "ARM_FREQ_DEEPER_N8192",
    "ARM_BASELINE_N4096",
    "ARM_FREQ_DEEPER_N4096",
    "ARM_FREQ_DEEPER_NSTEPS_3000",
]

# Per-arm config: each arm pins (n_dim, n_steps, type). type in {BASELINE, FREQ}.
ARM_CONFIGS = {
    "ARM_BASELINE_N8192": {
        "n_dim": 8192, "n_steps": 0, "type": "BASELINE",
        "describe": "Hebbian baseline at N=8192; sanity rail vs fair_harness 7.3065",
    },
    "ARM_FREQ_DEEPER_N8192": {
        "n_dim": 8192, "n_steps": 2000, "type": "FREQ",
        "freq_rank": 100, "lr_high": 0.5, "lr_rare": 0.2,
        "describe": "v4 winner reproduced at 5 seeds (was 3); primary replication target",
    },
    "ARM_BASELINE_N4096": {
        "n_dim": 4096, "n_steps": 0, "type": "BASELINE",
        "describe": "Hebbian baseline at N=4096; sanity rail (this cell establishes ref)",
    },
    "ARM_FREQ_DEEPER_N4096": {
        "n_dim": 4096, "n_steps": 2000, "type": "FREQ",
        "freq_rank": 100, "lr_high": 0.5, "lr_rare": 0.2,
        "describe": "FREQ_DEEPER at smaller N; tests cross-config replication",
    },
    "ARM_FREQ_DEEPER_NSTEPS_3000": {
        "n_dim": 8192, "n_steps": 3000, "type": "FREQ",
        "freq_rank": 100, "lr_high": 0.5, "lr_rare": 0.2,
        "describe": "Deeper-still training at N=8192; tests upper-bound of n_steps lever",
    },
}

# ============================================================================
# CLI / run-mode
# ============================================================================
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--roofline-probe-only", action="store_true",
                dest="roofline_probe_only",
                help="Run D1 roofline probe only; report wall extrapolation; exit.")
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


# ============================================================================
# GPU setup hardening
# ============================================================================

def _gpu_setup_assert_and_report(label: str = "startup"):
    try:
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
            try:
                free_b, total_b = torch.cuda.mem_get_info(DEVICE)
                free_gb = free_b / (1024 ** 3)
                total_gb = total_b / (1024 ** 3)
                print(("[gpu_setup %s] device=%s free_gb=%.2f total_gb=%.2f "
                       "headroom_frac=%.3f") % (
                          label, str(DEVICE), free_gb, total_gb,
                          free_b / max(total_b, 1)), flush=True)
            except Exception:
                pass
            probe = torch.zeros(8, device=DEVICE, dtype=TORCH_DTYPE)
            assert probe.device.type == DEVICE.type
            del probe
            torch.cuda.synchronize()
        else:
            print("[gpu_setup %s] device=cpu (no GPU available)" % label, flush=True)
    except Exception as e:
        print("[gpu_setup %s] WARN: %s" % (label, str(e)[:200]), flush=True)


# ============================================================================
# v5 config -- 5 arms, 5 seeds, dual-N
# ============================================================================
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

# N_STEPS_BASE = 2000 is the v4 winner's setting; v5 ARM_FREQ_DEEPER_NSTEPS_3000
# tests upper bound.

if RUN_MODE == "full":
    SEEDS = [7, 13, 17, 23, 29]  # 5 seeds (v4 had 3 [7, 17, 23])
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "cfrpe_lr=%.3f stdp_w=%.3f batch=%d "
    "arms_config=%s "
    "v4_freq_deeper_ref=%.4f device=%s version=v5_DEFINITIVE"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, CFRPE_LR, STDP_WEIGHT,
    INGEST_BATCH,
    json.dumps({k: {kk: vv for kk, vv in c.items() if kk != 'describe'}
                for k, c in ARM_CONFIGS.items()}, sort_keys=True),
    V4_FREQ_DEEPER_REF_BPC, str(DEVICE),
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
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "run_mode": RUN_MODE,
            "_note": "D2 atexit partial -- seed was mid-flight when process exited",
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
# Corpus utilities (identical to v4)
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
# Plasticity primitives (identical to v4 -- IDENTICAL kernel for comparison)
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
        error_freq = Nxt - Ctx @ W_freq.T
        wh = is_high_batch.unsqueeze(1)
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
    discriminating = {
        "n_high_freq_steps": int(n_high_steps),
        "n_rare_steps": int(n_rare_steps),
        "freq_threshold": int(freq_threshold),
        "n_high_freq_vocab": int(is_high_freq.sum()),
        "n_rare_vocab": int(V - is_high_freq.sum()),
    }
    del W_freq, W_rare, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": discriminating,
        "is_high_freq_vocab_mask": is_high_freq,
    }


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
    print("[selftest v5] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE shrinks error
    n_dim_st = 64
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
    assert err_after < err_before, "ST1 cf-RPE failed to shrink error"
    print("[selftest] ST1 cf-RPE %.4f -> %.4f OK" % (err_before, err_after), flush=True)

    # ST2: STDP antisymmetry
    b_st = 4
    Ctx_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    dW_stdp = (Nxt_t.T @ Ctx_t - Ctx_t.T @ Nxt_t) / float(b_st)
    antisym_err = float((dW_stdp + dW_stdp.T).abs().max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry failed"
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: freq_ranks: most-freq token at rank 0
    idx_st = np.array([1, 2, 1, 3, 1, 2, 1], dtype=np.int64)
    ranks = vocab_frequency_ranks(idx_st, V=5)
    assert ranks[1] == 0, "ST3 most-freq token rank not 0"
    print("[selftest] ST3 freq-ranks OK", flush=True)

    # ST4: hebbian baseline produces nonzero logits
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    ar = build_logits_hebbian_baseline_gpu(E_sb, idx_tr_st, idx_h_st,
                                              recall_batch=4, ingest_chunk=4)
    assert ar["logits"].shape == (idx_h_st.shape[0], V_st), "ST4 baseline shape"
    assert not np.all(ar["logits"] == 0.0), "ST4 baseline all zero"
    print("[selftest] ST4 hebbian baseline OK", flush=True)

    # ST5: freq_routed produces valid mask + nonzero logits
    ranks_st = vocab_frequency_ranks(idx_tr_st.detach().cpu().numpy(), V=V_st)
    ar_freq = build_logits_freq_routed_k2_gpu(E_sb, idx_tr_st, idx_h_st, ranks_st,
                                                 n_steps=10, batch=3,
                                                 lr_high=0.5, lr_rare=0.2,
                                                 stdp_w=0.5, freq_threshold=3,
                                                 seed=0, arm_idx=2, recall_batch=4)
    assert ar_freq["logits"].shape == (idx_h_st.shape[0], V_st), "ST5 freq shape"
    assert not np.all(ar_freq["logits"] == 0.0), "ST5 freq all zero"
    print("[selftest] ST5 freq_routed OK", flush=True)

    # ST6: arm diversity (baseline vs freq differ)
    d_bf = float(np.abs(ar["logits"] - ar_freq["logits"]).mean())
    assert d_bf > 1e-6, "ST6 baseline vs freq identical"
    print("[selftest] ST6 arm diversity OK (bf=%.4e)" % d_bf, flush=True)

    # ST7: joint_sweep finite
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST7 bpc_best not finite"
    print("[selftest] ST7 joint_sweep OK", flush=True)

    # ST8: sparsify nnz correct
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), "ST8 nnz mismatch"
    print("[selftest] ST8 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST9: LAMBDA_GRID excludes 0.0
    assert 0.0 not in LAMBDA_GRID, "ST9 LAMBDA_GRID must exclude 0.0"
    print("[selftest] ST9 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST10: LLM-call counter zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST10 LLM counter non-zero"
    print("[selftest] ST10 LLM counter==0 OK", flush=True)

    # ST11 (v5): ARMS list consistency -- 5 arms
    expected_arms = {"ARM_BASELINE_N8192", "ARM_FREQ_DEEPER_N8192",
                     "ARM_BASELINE_N4096", "ARM_FREQ_DEEPER_N4096",
                     "ARM_FREQ_DEEPER_NSTEPS_3000"}
    assert set(ARMS) == expected_arms, "ST11 ARMS mismatch: %s" % set(ARMS)
    assert len(ARMS) == 5, "ST11 v5 expects 5 arms"
    assert set(ARM_CONFIGS.keys()) == set(ARMS), "ST11 ARM_CONFIGS keys mismatch"
    print("[selftest] ST11 ARMS consistent (%d) OK" % len(ARMS), flush=True)

    # ST12: D2 atexit registered
    _register_atexit_once()
    assert _RUN_STATE.atexit_registered, "ST12 atexit not registered"
    _atexit_flush_partial()  # no-op (current_seed=None)
    print("[selftest] ST12 D2 atexit OK", flush=True)

    # ST13 (v5): config-coherence -- 5 seeds in full mode + cross-N coverage
    if RUN_MODE == "full":
        assert len(SEEDS) == 5, "ST13 v5 expects 5 seeds in full; got %d" % len(SEEDS)
        assert SEEDS == [7, 13, 17, 23, 29], "ST13 v5 expects SEEDS=[7,13,17,23,29]"
        n_dims_present = set(c["n_dim"] for c in ARM_CONFIGS.values())
        assert n_dims_present == {4096, 8192}, "ST13 expects N in {4096, 8192}: got %s" % n_dims_present
        n_steps_present = set(c["n_steps"] for c in ARM_CONFIGS.values() if c["type"] == "FREQ")
        assert n_steps_present == {2000, 3000}, "ST13 expects FREQ n_steps in {2000, 3000}: got %s" % n_steps_present
    print("[selftest] ST13 config-coherence OK (seeds=%d arms=%d)" % (len(SEEDS), len(ARMS)),
          flush=True)

    # ST14 (v5 NEW): per-arm config dict well-formed
    for arm_n, cfg in ARM_CONFIGS.items():
        assert "n_dim" in cfg and cfg["n_dim"] in (4096, 8192), (
            "ST14 cfg %s n_dim invalid" % arm_n)
        assert "n_steps" in cfg and cfg["n_steps"] >= 0, (
            "ST14 cfg %s n_steps invalid" % arm_n)
        assert "type" in cfg and cfg["type"] in ("BASELINE", "FREQ"), (
            "ST14 cfg %s type invalid" % arm_n)
        if cfg["type"] == "FREQ":
            for k in ("freq_rank", "lr_high", "lr_rare"):
                assert k in cfg, "ST14 FREQ cfg %s missing %s" % (arm_n, k)
                assert cfg[k] > 0, "ST14 FREQ cfg %s.%s not positive" % (arm_n, k)
    print("[selftest] ST14 ARM_CONFIGS well-formed OK", flush=True)

    # ST15 (v5 NEW): formula self-test -- runtime cost MODEL
    # Cost model claims per-seed wall = sum_arms wall, with FREQ wall scaling
    # ~ (N_DIM/8192)^2 * (n_steps/1000). v4 measured FREQ@N8192/n_steps=2000 ~170s.
    # v5 per-seed: BASE_N8192 50s + FREQ_N8192/n=2000 170s + BASE_N4096 13s +
    # FREQ_N4096/n=2000 43s + FREQ_N8192/n=3000 255s + 25s overhead = ~556s.
    # 5 seeds = 2780s. 7200s timeout / 2780s = 2.59x headroom. >= 1.5 OK.
    def _wall_for_freq_arm(n_steps_x: int, n_dim_x: int) -> float:
        # tiny synthetic for relative timing
        E_tmp_np = np.random.default_rng(0).standard_normal((V_st, n_dim_x)).astype(np.float32)
        E_tmp_np = _l2_normalize_np(E_tmp_np)
        E_tmp_t = torch.from_numpy(E_tmp_np).to(DEVICE)
        E_tmp_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_tmp_t, SPARSE_BIPOLAR_F))
        t0 = time.time()
        _ = build_logits_freq_routed_k2_gpu(
            E_tmp_sb, idx_tr_st, idx_h_st, ranks_st,
            n_steps=n_steps_x, batch=3, lr_high=0.5, lr_rare=0.2,
            stdp_w=0.5, freq_threshold=3, seed=1, arm_idx=99,
            recall_batch=4)
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        return time.time() - t0
    w_1x = _wall_for_freq_arm(50, 128)
    w_2x = _wall_for_freq_arm(100, 128)
    if w_1x > 0.001:
        ratio = w_2x / w_1x
        assert 1.2 <= ratio <= 4.0, (
            "ST15 cost-model FAIL: n_steps doubling wall ratio %.2f outside [1.2,4.0]. "
            "w_1x=%.4fs w_2x=%.4fs" % (ratio, w_1x, w_2x))
        print("[selftest] ST15 cost-model: ratio=%.2fx OK" % ratio, flush=True)
    else:
        print("[selftest] ST15 cost-model: SKIP (walls too small)", flush=True)

    # ST16 (v5 NEW): expected wall budget under 7200s timeout with headroom
    # Per-seed model: BASE_N8192 50s + FREQ_N8192_n2000 170s + BASE_N4096 13s +
    # FREQ_N4096_n2000 43s + FREQ_N8192_n3000 255s + 25s overhead = 556s
    expected_per_seed = 50.0 + 170.0 + 13.0 + 43.0 + 255.0 + 25.0
    expected_full_wall = expected_per_seed * float(len(SEEDS))
    requested_timeout = 7200.0
    headroom_ratio = requested_timeout / expected_full_wall
    assert headroom_ratio >= 1.3, (
        "ST16 budget FAIL: expected_full=%.0fs vs timeout=%.0fs; headroom=%.2fx < 1.3" % (
            expected_full_wall, requested_timeout, headroom_ratio))
    print("[selftest] ST16 budget headroom: %.0fs/%.0fs = %.2fx OK" % (
        expected_full_wall, requested_timeout, headroom_ratio), flush=True)

    print("[selftest v5] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# D1 ROOFLINE PROBE -- pre-FULL gate
# ============================================================================

def roofline_probe(timeout_s_target: int) -> Dict:
    """Time FREQ arm at 3 N scales + extrapolate full v5 wall."""
    print("\n[D1 probe v5] running roofline probe...", flush=True)
    # Probe at N=2048, 4096, 8192 to span both production N values
    probe_scales = [2048, 4096, 8192]
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
    ranks_probe = vocab_frequency_ranks(idx_tr, V=probe_v)
    freq_thresh = FREQ_ROUTE_RANK if probe_v > FREQ_ROUTE_RANK else max(1, probe_v // 4)

    for probe_n_dim in probe_scales:
        E_np = np.random.default_rng(probe_seed * 11 + probe_n_dim).standard_normal(
            (probe_v, probe_n_dim)).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(DEVICE)
        E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
        t0 = time.time()
        _ = build_logits_freq_routed_k2_gpu(
            E_sb, idx_tr_t, idx_h_t, ranks_probe,
            n_steps=probe_n_steps, batch=INGEST_BATCH,
            lr_high=FREQ_LR_HIGH, lr_rare=FREQ_LR_RARE,
            stdp_w=STDP_WEIGHT, freq_threshold=freq_thresh,
            seed=probe_seed, arm_idx=2, recall_batch=RECALL_BATCH,
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

    # Per-arm wall extrapolation
    def _arm_wall(n_dim_x: int, n_steps_x: int) -> float:
        # FREQ arm scales: a_fit * N^k_fit * (n_steps/probe_n_steps) * 1.1 safety
        return a_fit * (float(n_dim_x) ** k_fit) * (float(n_steps_x) / float(probe_n_steps)) * 1.1

    # Hebbian baseline wall: v4 measured ~50s at N=8192, scales ~ N^2 (matmul)
    # so ~13s at N=4096.
    def _baseline_wall(n_dim_x: int) -> float:
        return 50.0 * (float(n_dim_x) / 8192.0) ** 2

    per_seed_arm_walls = {
        "ARM_BASELINE_N8192": _baseline_wall(8192),
        "ARM_FREQ_DEEPER_N8192": _arm_wall(8192, 2000),
        "ARM_BASELINE_N4096": _baseline_wall(4096),
        "ARM_FREQ_DEEPER_N4096": _arm_wall(4096, 2000),
        "ARM_FREQ_DEEPER_NSTEPS_3000": _arm_wall(8192, 3000),
    }
    per_seed_total = sum(per_seed_arm_walls.values()) + 25.0  # 25s overhead
    full_wall_extrap = per_seed_total * float(len(SEEDS))

    print("[D1] fit: a=%.4e k=%.3f" % (a_fit, k_fit), flush=True)
    print("[D1] per-arm walls: %s" % json.dumps(
        {k: round(v, 1) for k, v in per_seed_arm_walls.items()}), flush=True)
    print("[D1] per-seed total: %.1fs; full (%d seeds): %.1fs (%.1f min)" % (
        per_seed_total, len(SEEDS), full_wall_extrap, full_wall_extrap / 60.0), flush=True)
    print("[D1] target timeout: %ds; budget 0.8x = %.1fs" % (
        timeout_s_target, 0.8 * timeout_s_target), flush=True)

    result = {
        "probe_scales": probe_scales,
        "probe_walls_s": [round(w[1], 3) for w in walls],
        "fit_a": round(a_fit, 6),
        "fit_k": round(k_fit, 3),
        "per_seed_arm_walls": {k: round(v, 1) for k, v in per_seed_arm_walls.items()},
        "per_seed_total_s": round(per_seed_total, 1),
        "full_wall_extrap_s": round(full_wall_extrap, 1),
        "timeout_s_target": int(timeout_s_target),
        "budget_s": round(0.8 * timeout_s_target, 1),
        "dispatch_ok": bool(full_wall_extrap <= 0.8 * timeout_s_target),
    }

    if not result["dispatch_ok"]:
        print("[D1] REFUSE DISPATCH: %.1fs > 0.8 * timeout" % full_wall_extrap, flush=True)
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

def _build_corpus(seed: int):
    if RUN_MODE == "smoke":
        print("\n[seed=%d] SMOKE: clean synthetic markov-bigram (V=%d N_TRAIN=%d N_HELD=%d)" % (
            seed, VOCAB_CAP, N_TRAIN, N_HELD), flush=True)
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
        vocab = ["t%d" % i for i in range(VOCAB_CAP)]
        V = VOCAB_CAP
        encoder_meta = {"smoke_synthetic": True, "V": V}
    else:
        print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
        toks = load_text8_tokens(N_TRAIN + N_HELD)
        if len(toks) < N_TRAIN + N_HELD:
            print("[WARN] corpus short: %d tokens loaded" % len(toks), flush=True)
        train_toks = toks[:N_TRAIN]
        held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
        vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
        V = len(vocab)
        idx_train = tokens_to_idx(train_toks, w2i)
        idx_held = tokens_to_idx(held_toks, w2i)
        encoder_meta = {}
    return idx_train, idx_held, vocab, V, encoder_meta


def _build_encoder(vocab: List[str], V: int, n_dim: int, seed: int):
    print("[seed=%d] building encoder N_DIM=%d V=%d..." % (seed, n_dim, V), flush=True)
    t0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, meta = build_E_synthetic_smoke(V, n_dim, seed)
    else:
        E_proj_t, meta = build_E_word2vec(vocab, n_dim, seed)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs sparsity=%.3f N_DIM=%d" % (
        seed, time.time() - t0, sparsity, n_dim), flush=True)
    del E_proj_t
    return E_full, meta


def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    _register_atexit_once()
    _RUN_STATE.out_dir = out_dir
    _RUN_STATE.current_seed = seed
    _RUN_STATE.current_seed_partials = {}

    idx_train, idx_held, vocab, V, encoder_meta = _build_corpus(seed)

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"]), flush=True)

    ranks_np = vocab_frequency_ranks(idx_train, V=V)
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}
    _RUN_STATE.current_seed_partials = by_arm

    # Build encoders for each distinct N value (memoize within seed)
    # ARMS use N_DIM in {4096, 8192}.
    distinct_n_dims = sorted(set(c["n_dim"] for c in ARM_CONFIGS.values()))
    encoders: Dict[int, Tuple[torch.Tensor, Dict]] = {}
    for n_dim_v in distinct_n_dims:
        E_full, e_meta = _build_encoder(vocab, V, n_dim_v, seed)
        encoders[n_dim_v] = (E_full, e_meta)

    by_arm["w2v_meta"] = encoders[distinct_n_dims[0]][1]

    def _process_arm(arm_name: str, ar: Dict) -> Dict:
        logits_full = ar["logits"]
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

    def _freq_per_class(arm_name: str, ar: Dict, jr: Dict) -> Dict:
        # Add high-vs-low freq top1 breakdown for FREQ arms
        logits_full = ar["logits"]
        is_high_freq_mask = ar.get("is_high_freq_vocab_mask")
        if is_high_freq_mask is None:
            return jr
        valid_pos = np.where(mask)[0]
        valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos]
        nxt_eval_local = nxt_full[valid_pos]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_test_l = nxt_eval_local[n_dev_l:]
        best_T = jr["best_T_for_top1"]
        best_lam = jr["best_lambda_for_top1"]
        probs_test = softmax_with_T(logits_eval[n_dev_l:], best_T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp(logp_sub_test, U_log, best_lam)
        pred_top1 = np.argmax(logp_test, axis=1)
        is_correct = (pred_top1 == nxt_test_l).astype(np.float32)
        nxt_is_high_freq = is_high_freq_mask[nxt_test_l]
        if nxt_is_high_freq.sum() > 0:
            top1_high = float(is_correct[nxt_is_high_freq].mean())
        else:
            top1_high = float("nan")
        if (~nxt_is_high_freq).sum() > 0:
            top1_low = float(is_correct[~nxt_is_high_freq].mean())
        else:
            top1_low = float("nan")
        freq_diff = abs(top1_high - top1_low) if (
            math.isfinite(top1_high) and math.isfinite(top1_low)) else float("nan")
        disc = dict(ar.get("discriminating", {}))
        disc.update({
            "top1_high_freq_tokens": round(top1_high, 4) if math.isfinite(top1_high) else None,
            "top1_low_freq_tokens": round(top1_low, 4) if math.isfinite(top1_low) else None,
            "freq_top1_differential": round(freq_diff, 4) if math.isfinite(freq_diff) else None,
            "n_high_freq_tgts_in_test": int(nxt_is_high_freq.sum()),
            "n_low_freq_tgts_in_test": int((~nxt_is_high_freq).sum()),
        })
        return disc

    arm_idx_v = 1
    for arm_name in ARMS:
        cfg = ARM_CONFIGS[arm_name]
        n_dim_v = cfg["n_dim"]
        t_arm0 = time.time()
        E_full = encoders[n_dim_v][0]
        print("\n  [seed=%d arm=%s n_dim=%d type=%s] computing..." % (
            seed, arm_name, n_dim_v, cfg["type"]), flush=True)
        try:
            if cfg["type"] == "BASELINE":
                ar = build_logits_hebbian_baseline_gpu(
                    E_full, idx_train_t, idx_held_t,
                    recall_batch=RECALL_BATCH, ingest_chunk=INGEST_CHUNK,
                )
                jr = _process_arm(arm_name, ar)
                jr["discriminating"] = ar.get("discriminating", {})
            else:
                thresh = cfg["freq_rank"] if V > cfg["freq_rank"] else max(1, V // 4)
                ar = build_logits_freq_routed_k2_gpu(
                    E_full, idx_train_t, idx_held_t, ranks_np,
                    n_steps=cfg["n_steps"], batch=INGEST_BATCH,
                    lr_high=cfg["lr_high"], lr_rare=cfg["lr_rare"],
                    stdp_w=STDP_WEIGHT, freq_threshold=thresh,
                    seed=seed, arm_idx=arm_idx_v, recall_batch=RECALL_BATCH,
                )
                jr = _process_arm(arm_name, ar)
                jr["discriminating"] = _freq_per_class(arm_name, ar, jr)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm_name, err), flush=True)
            by_arm[arm_name] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "arm_config": cfg,
            }
        else:
            jr.update({
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                "wall_recall_s": ar.get("wall_recall_s", 0.0),
                "arm_config": cfg,
            })
            by_arm[arm_name] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
                seed, arm_name, jr["bpc_best"], jr["top1_acc"],
                jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
        _RUN_STATE.current_seed_partials = dict(by_arm)
        arm_idx_v += 1

    # Cleanup encoders for this seed
    for n_dim_v in distinct_n_dims:
        del encoders[n_dim_v]
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    result = {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": -1,  # multi-N cell; per-arm N in arm_config
        "M": N_TRAIN,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }
    return result


# ============================================================================
# Verdict (v5 DEFINITIVE bands)
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
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
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
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant)." % total_llm_calls,
                {"by_arm_agg": by_arm_agg, "llm_forward_calls_total": total_llm_calls})

    # ====== v5 DEFINITIVE verdict ======
    base_n8192 = arm_bpc.get("ARM_BASELINE_N8192", float("inf"))
    base_n4096 = arm_bpc.get("ARM_BASELINE_N4096", float("inf"))
    freq_n8192 = arm_bpc.get("ARM_FREQ_DEEPER_N8192", float("inf"))
    freq_n4096 = arm_bpc.get("ARM_FREQ_DEEPER_N4096", float("inf"))
    freq_n8192_3k = arm_bpc.get("ARM_FREQ_DEEPER_NSTEPS_3000", float("inf"))

    cv_freq_n8192 = arm_cv.get("ARM_FREQ_DEEPER_N8192", float("nan"))

    # Sanity rail: BASELINE_N8192 must match fair_harness rail 7.3065 +/- 0.05
    n8192_rail_drift = abs(base_n8192 - SANITY_RAIL_BASELINE_REF_N8192) if math.isfinite(base_n8192) else float("inf")
    n8192_rail_ok = n8192_rail_drift <= SANITY_RAIL_TOLERANCE
    # BASELINE_N4096 rail is "this cell establishes it"; just check finite + lower than UNIGRAM
    n4096_rail_ok = math.isfinite(base_n4096) and base_n4096 < unigram_bpc

    # Cross-N replication: FREQ_DEEPER beats baseline at SAME N
    n8192_lift = base_n8192 - freq_n8192 if (math.isfinite(base_n8192) and math.isfinite(freq_n8192)) else float("nan")
    n4096_lift = base_n4096 - freq_n4096 if (math.isfinite(base_n4096) and math.isfinite(freq_n4096)) else float("nan")
    crossN_both_pass = (math.isfinite(n8192_lift) and math.isfinite(n4096_lift) and
                       n8192_lift >= HARD_PASS_GAP_VS_BASELINE and
                       n4096_lift >= HARD_PASS_GAP_VS_BASELINE)

    # v4 replication check
    v4_repro_drift = abs(freq_n8192 - V4_FREQ_DEEPER_REF_BPC) if math.isfinite(freq_n8192) else float("inf")
    v4_repro_ok = v4_repro_drift <= V4_REPLICATION_TOLERANCE

    # n_steps 3000 vs 2000 upper-bound check
    nsteps_delta = freq_n8192 - freq_n8192_3k if (math.isfinite(freq_n8192) and math.isfinite(freq_n8192_3k)) else float("nan")
    plateaued = abs(nsteps_delta) <= 0.02 if math.isfinite(nsteps_delta) else None

    arm_summary = (
        "uni=%.3f | BASE_N8192=%.4f(rail=%s,drift=%+.4f) | BASE_N4096=%.4f | "
        "FREQ_N8192=%.4f(lift=%+.4f,cv=%.4f) | FREQ_N4096=%.4f(lift=%+.4f) | "
        "FREQ_N8192_n3000=%.4f(delta=%+.4f,plateaued=%s) | "
        "v4_repro=%.4f(drift=%+.4f,ok=%s) | crossN_both_pass=%s"
    ) % (
        unigram_bpc, base_n8192, str(n8192_rail_ok), base_n8192 - SANITY_RAIL_BASELINE_REF_N8192,
        base_n4096,
        freq_n8192, n8192_lift if math.isfinite(n8192_lift) else float("nan"),
        cv_freq_n8192 if math.isfinite(cv_freq_n8192) else -1.0,
        freq_n4096, n4096_lift if math.isfinite(n4096_lift) else float("nan"),
        freq_n8192_3k, nsteps_delta if math.isfinite(nsteps_delta) else float("nan"),
        str(plateaued),
        freq_n8192, freq_n8192 - V4_FREQ_DEEPER_REF_BPC, str(v4_repro_ok),
        str(crossN_both_pass),
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "arm_bpc": {k: round(v, 4) if math.isfinite(v) else None for k, v in arm_bpc.items()},
        "arm_cv": {k: round(v, 4) if math.isfinite(v) else None for k, v in arm_cv.items()},
        "sanity_rails": {
            "baseline_n8192_ref": SANITY_RAIL_BASELINE_REF_N8192,
            "baseline_n8192_drift": round(n8192_rail_drift, 4),
            "baseline_n8192_ok": bool(n8192_rail_ok),
            "baseline_n4096_measured": round(base_n4096, 4) if math.isfinite(base_n4096) else None,
            "baseline_n4096_ok": bool(n4096_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "crossN_check": {
            "n8192_lift": round(n8192_lift, 4) if math.isfinite(n8192_lift) else None,
            "n4096_lift": round(n4096_lift, 4) if math.isfinite(n4096_lift) else None,
            "both_pass": bool(crossN_both_pass),
            "min_lift_required": HARD_PASS_GAP_VS_BASELINE,
        },
        "v4_replication_check": {
            "v4_freq_deeper_ref_bpc": V4_FREQ_DEEPER_REF_BPC,
            "v5_freq_n8192_bpc": round(freq_n8192, 4) if math.isfinite(freq_n8192) else None,
            "drift_from_v4_ref": round(v4_repro_drift, 4) if math.isfinite(v4_repro_drift) else None,
            "ok": bool(v4_repro_ok),
            "tolerance": V4_REPLICATION_TOLERANCE,
        },
        "nsteps_upper_bound_check": {
            "freq_n8192_n2000_bpc": round(freq_n8192, 4) if math.isfinite(freq_n8192) else None,
            "freq_n8192_n3000_bpc": round(freq_n8192_3k, 4) if math.isfinite(freq_n8192_3k) else None,
            "delta_2000_to_3000": round(nsteps_delta, 4) if math.isfinite(nsteps_delta) else None,
            "plateaued": plateaued,
        },
        "bands": {
            "hard_pass_cap_bpc": HARD_PASS_CAP_BPC,
            "hard_pass_gap_vs_baseline": HARD_PASS_GAP_VS_BASELINE,
            "cv_max_hard_pass": CV_MAX_HARD_PASS,
            "cv_max_chain_grade_definitive": CV_MAX_CHAIN_GRADE_DEFINITIVE,
            "hard_fail_null_floor": HARD_FAIL_NULL_FLOOR,
            "middle_band_lower": MIDDLE_BAND_LOWER,
            "middle_band_upper": MIDDLE_BAND_UPPER,
            "sanity_rail_tolerance": SANITY_RAIL_TOLERANCE,
            "v4_replication_tolerance": V4_REPLICATION_TOLERANCE,
        },
        "arms_config": {a: ARM_CONFIGS[a] for a in ARMS},
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "llm_forward_calls_total": total_llm_calls,
        "honest_scope": (
            "v5 DEFINITIVE upgrade of v4 ARM_FREQ_DEEPER_TRAIN (BPC=7.159 "
            "CHAIN_GRADE_PARTIAL at 3 seeds, single config). v5 ships 5 seeds + "
            "cross-N replication (N=8192 + N=4096) + upper-bound n_steps probe "
            "(2000 vs 3000). DEFINITIVE = primary FREQ_DEEPER at N=8192 reproduces "
            "v4 7.159 within +/-0.05 AND beats same-N baseline by >=0.10 AND "
            "FREQ_DEEPER at N=4096 also beats its baseline by >=0.10 AND CV<=0.03 "
            "across 5 seeds AND both sanity rails pass. WHAT_THIS_DOES_NOT_SHOW: "
            "doesn't test other (rank/lr/architectural-composition) knobs; doesn't "
            "test V scaling; doesn't test corpus size scaling; cross-N at only "
            "two points (4096 + 8192); the n_steps 3000 arm tests upper-bound at "
            "N=8192 only."
        ),
        "cites": [
            "preregs/2026-06-25_substrate_compose_freq_routing_v5_DEFINITIVE.md",
            "experiments/exp_substrate_compose_freq_routing_v4_hparam_sweep.py (v4 base; ARM_FREQ_DEEPER_TRAIN=7.159 CHAIN_GRADE_PARTIAL)",
            "data/exp_substrate_compose_freq_routing_v4_hparam_sweep/metrics.json",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)",
        ],
    }

    all_arms_failed = all(
        by_arm_agg.get(a, {}).get("all_seeds_failed", True) for a in ARMS
    )
    if all_arms_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: all 5 arms failed all seeds. %s" % arm_summary,
                detail)

    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not n8192_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE_BASELINE_N8192: %.4f drifts %.4f from fair_harness ref %.4f (>%.2f tol). %s" % (
                    base_n8192, n8192_rail_drift, SANITY_RAIL_BASELINE_REF_N8192,
                    SANITY_RAIL_TOLERANCE, arm_summary),
                detail)

    # HARD_FAIL_NULL: FREQ_DEEPER_N8192 failed to even reach v3 range
    if math.isfinite(freq_n8192) and freq_n8192 >= HARD_FAIL_NULL_FLOOR:
        detail["verdict_tier"] = "HARD_FAIL_NULL"
        return ("HARD_FAIL",
                "HARD_FAIL_NULL_REPLICATION: ARM_FREQ_DEEPER_N8192=%.4f >= %.2f. "
                "v4 result (7.159) NOT replicated; v4 was likely noise. %s" % (
                    freq_n8192, HARD_FAIL_NULL_FLOOR, arm_summary),
                detail)

    # CV gate
    if math.isfinite(cv_freq_n8192) and cv_freq_n8192 > CV_MAX_HARD_PASS:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: ARM_FREQ_DEEPER_N8192 cv=%.4f > %.2f. bpc=%.4f. %s" % (
                    cv_freq_n8192, CV_MAX_HARD_PASS, freq_n8192, arm_summary),
                detail)

    # HARD_PASS_CHAIN_GRADE_DEFINITIVE
    if (math.isfinite(freq_n8192) and freq_n8192 <= HARD_PASS_CAP_BPC and
            crossN_both_pass and
            math.isfinite(cv_freq_n8192) and cv_freq_n8192 <= CV_MAX_CHAIN_GRADE_DEFINITIVE and
            n8192_rail_ok and n4096_rail_ok):
        detail["verdict_tier"] = "HARD_PASS_CHAIN_GRADE_DEFINITIVE"
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_DEFINITIVE: ARM_FREQ_DEEPER_N8192=%.4f<=%.2f AND "
                "cross-N both pass (N8192 lift=%+.4f N4096 lift=%+.4f >= %.2f) AND "
                "CV=%.4f<=%.3f AND both sanity rails pass. v4 FREQ_DEEPER win is "
                "DEFINITIVE across config + 5 seeds. %s" % (
                    freq_n8192, HARD_PASS_CAP_BPC,
                    n8192_lift, n4096_lift, HARD_PASS_GAP_VS_BASELINE,
                    cv_freq_n8192, CV_MAX_CHAIN_GRADE_DEFINITIVE,
                    arm_summary),
                detail)

    # HARD_PASS (single-config replication of v4)
    if (math.isfinite(freq_n8192) and freq_n8192 <= HARD_PASS_CAP_BPC and
            math.isfinite(n8192_lift) and n8192_lift >= HARD_PASS_GAP_VS_BASELINE and
            math.isfinite(cv_freq_n8192) and cv_freq_n8192 <= CV_MAX_HARD_PASS and
            n8192_rail_ok):
        detail["verdict_tier"] = "HARD_PASS_SINGLE_CONFIG_REPLICATION"
        return ("HARD_PASS",
                "HARD_PASS_SINGLE_CONFIG_REPLICATION: ARM_FREQ_DEEPER_N8192=%.4f<=%.2f "
                "AND beats BASE_N8192 by %+.4f>=%.2f AND CV=%.4f<=%.2f. v4 result "
                "replicated at 5 seeds (single config). Cross-N missed: N4096 lift=%+.4f. %s" % (
                    freq_n8192, HARD_PASS_CAP_BPC,
                    n8192_lift, HARD_PASS_GAP_VS_BASELINE,
                    cv_freq_n8192, CV_MAX_HARD_PASS,
                    n4096_lift if math.isfinite(n4096_lift) else float("nan"),
                    arm_summary),
                detail)

    # MIDDLE_BAND
    if math.isfinite(freq_n8192) and MIDDLE_BAND_LOWER <= freq_n8192 <= MIDDLE_BAND_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_REPLICATION"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_REPLICATION: ARM_FREQ_DEEPER_N8192=%.4f in [%.2f, %.2f] "
                "(v4's 7.159 not reproduced). %s" % (
                    freq_n8192, MIDDLE_BAND_LOWER, MIDDLE_BAND_UPPER, arm_summary),
                detail)

    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: ARM_FREQ_DEEPER_N8192=%.4f outside MB+HP+HF. %s" % (
                freq_n8192, arm_summary),
            detail)


# ============================================================================
# Main loop
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda_available=%s" % (str(DEVICE), torch.cuda.is_available()),
      flush=True)

_gpu_setup_assert_and_report(label="startup")

out_dir = get_output_dir(ANCHOR_NAME)
_RUN_STATE.out_dir = out_dir
_register_atexit_once()

if RUN_MODE == "full":
    timeout_s_env = int(os.environ.get("HDLAB_RUN_TIMEOUT_S", "7200"))
    probe_result = roofline_probe(timeout_s_env)
    if not probe_result["dispatch_ok"]:
        print("[D1] EXIT: roofline refuses dispatch", flush=True)
        minimal_metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL_D1_ROOFLINE_REFUSE: extrapolated wall %.1fs > 0.8 * timeout %ds. Probe: %s" % (
                probe_result["full_wall_extrap_s"], probe_result["timeout_s_target"],
                json.dumps(probe_result)),
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
    print("[D1] GATE PASSED -- proceeding to FULL run", flush=True)

# PROT-021 config-mismatch guard: this is a multi-N cell so N is per-arm
run_config = {"N": -1, "M": N_TRAIN, "run_mode": RUN_MODE}

done_seeds_init: List[int] = []
remaining_seeds_init: List[int] = SEEDS[:]
try:
    done_seeds_init, remaining_seeds_init = _resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds_init), len(remaining_seeds_init), remaining_seeds_init), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds_init = SEEDS[:]

for seed in remaining_seeds_init:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written to %s" % (seed, out_dir), flush=True)
    _RUN_STATE.current_seed = None
    _RUN_STATE.current_seed_partials = {}

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

summary_str = (
    "%s | arms=%d seeds=%d v5_DEFINITIVE freq_deeper_crossN" % (
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
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "FREQ_ROUTE_RANK_DEFAULT": FREQ_ROUTE_RANK,
    "FREQ_LR_HIGH_DEFAULT": FREQ_LR_HIGH,
    "FREQ_LR_RARE_DEFAULT": FREQ_LR_RARE,
    "ARM_CONFIGS": {a: {k: v for k, v in c.items() if k != 'describe'}
                     for a, c in ARM_CONFIGS.items()},
    "V4_FREQ_DEEPER_REF_BPC": V4_FREQ_DEEPER_REF_BPC,
    "V4_REPLICATION_TOLERANCE": V4_REPLICATION_TOLERANCE,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_TRAIN": u.get("N_TRAIN"),
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
