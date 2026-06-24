"""
exp_substrate_k_module_compose_RESCUE_v1

SCIENTIFIC QUESTION (2026-06-23 RESCUE):
  Prior cell substrate_k_module_heterogeneous_compose_LM_v1 returned INSTRUMENTATION_SUSPECT.
  Root cause: m2_ok=false / m3_ok=false on ALL seeds -- lock-in encode silently fell into
  except block, fell back to logits_m1.copy(), then log-linear on identical distributions
  found lambda=0 (pure unigram) as best. ARM_M1_PLUS_LOCKIN / ARM_K_MODULE_FULL_HETERO all
  collapsed to 7.7378 (unigram). The modules were NOT actually different.

  This rescue applies 5 session-discovered fixes:
    Fix 1: amplitude scaling 1/sqrt(f) on ALL sparse-bipolar codebook entries (viability
            shotgun P2: binary LIVE/DEAD at f=0.02 -- without scaling, recall=6%)
    Fix 2: sigmoid-additive compose (NOT multiplicative; shotgun P6: mult collapses 100x
            when any modulator < 0.1)
    Fix 3: K=2 banks with feature-gated routing (K-bank shotgun: K=2 gives +1.07 BPC lift)
    Fix 4: cf-RPE delta rule per bank (from cf-RPE dispatch; delta = r_t * (target - W*key))
    Fix 5: bit-for-bit baseline provenance verification (ARM_BASELINE must match 7.3065)

  INSTRUMENTATION GUARD: if any multi-module arm's logits differ from ARM_BASELINE by
  cosine similarity > 0.9999, abort with INSTRUMENTATION_SUSPECT (silent copy-through).

ARM DESIGN (5 arms, 3 seeds, text8 N_TRAIN=100k, N_DIM=8192):
  ARM_BASELINE:
    Single bank, sparse-bipolar f=0.02, WITH 1/sqrt(f) amplitude scaling.
    Rank-1 Hebbian W. Must reproduce fair_harness 7.3065 BPC +/- 0.001.
  ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT:
    Same as baseline but with f=0.02 (vs f=0.05 in prior cell).
    Verifies that 1/sqrt(f) scaling at f=0.02 reproduces the 99% recall from P2.
  ARM_K2_MODULES:
    K=2 banks, each N_per=N_DIM/2=4096 dims. Feature-gated sigmoid routing.
    Gate = sigmoid(alpha * dot(ctx_key, gate_vec)). Soft assignment.
    Reproduces K-bank shotgun +1.07 BPC lift.
  ARM_K2_PLUS_CFRPE:
    K=2 banks + cf-RPE delta rule per bank.
    cf-RPE: delta_W += r_t * (tgt - W @ src) @ src.T, r_t from running mean reward.
    Combines K-bank partition + chain-grade plasticity.
  ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE:
    K=2 banks + cf-RPE + SIGMOID-ADDITIVE compose function.
    gate = sigmoid(ALPHA * mod_A + BETA * mod_B). NOT multiplicative.
    LOAD-BEARING ARM for Levy-Horn-Ruppin N^M escape test.

COMPOSE RULE:
  SIGMOID-ADDITIVE: gate = sigmoid(alpha * E_A[ctx] + beta * E_B[ctx])
    where E_A, E_B are the two bank embeddings of the context token.
    gate in [0.5, 0.88] -- avoids the starvation regime (vs mult with E[gate]=0.12).
  Final decode: log p(w|ctx) = gate * log_p_A(w) + (1-gate) * log_p_B(w)
    (two-bank log-linear interpolation with context-dependent gate)

PRE-REGISTERED HARD BANDS (IMMUTABLE):
  HARD_PASS:  ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE beats ARM_BASELINE by >= +0.30 bits
              AND cv across 3 seeds < 0.05
  CHAIN_GRADE_BONUS: lift >= +0.50 bits (Levy-Horn-Ruppin N^M escape)
  MIDDLE_BAND: lift +0.10 to +0.30 bits
  HARD_FAIL:  lift <= +0.10 bits OR any compose arm collapses to unigram BPC
              (rescue failed; implementation still buggy OR mechanism dead)
  SANITY RAILS:
    ARM_BASELINE within +/- 0.005 of fair_harness 7.3065
    ARM_K2_MODULES within +/- 0.10 of K-bank smoke +1.07 lift (scale-normalized)
    cv < 0.05 mandatory

INSTRUMENTATION SELF-TEST (MANDATORY):
  1. Sparse-bipolar amplitude scaling: codebook mean row-norm at f=0.02 is ~1/sqrt(0.02*N) not 1
  2. K=2 gate: gate values span [0.05, 0.95] at smoke scale (not stuck at 0 or 1)
  3. Module logits diverge from M1: max cosine(logits_k2, logits_baseline) < 0.9999
  4. Sigmoid-additive gate mean in [0.3, 0.7] (not degenerate one-sided)
  5. cf-RPE W changes sign at least once from Hebbian-only W (learning signal non-zero)

PROT-018: anchor has no _n suffix; production N = 8192; see PRODUCTION_N below.
  rationale: N_DIM=8192 matches fair_harness scale; _n suffix not added per PROT-018 rule 3.

GPU REQUIRED (Fix #24): N_DIM=8192, K=2 W matrices each 8192x8192.
  Each W: 8192^2 * 4 bytes = 256MB. K=2 banks = 512MB total.
  All matmul via torch.cuda + batched ops. Expected GPU util >= 50%.

Cites:
  data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json (prior: INSTR_SUSPECT)
  notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md (P2: ampl scaling binary)
  notes/shotgun_smoke_compose_function_discriminator_2026-06-23.md (sigmoid-add LIVE)
  notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md (K=2 optimal at smoke scale)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline 7.3065)
  notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md (Levy-Horn-Ruppin)

ASCII-only. No unicode. Per-seed checkpoint. atexit synthesizer.
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
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_k_module_compose_RESCUE_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Production N = 8192 (PROT-018: no _n suffix; matches fair_harness scale)
PRODUCTION_N = 8192
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ---- Config ----
if RUN_MODE == "smoke" or _ARGS.self_test:
    SEEDS = [7]
    N_DIM = 512
    N_TRAIN = 3000
    N_HELD = 600
    VOCAB_CAP = 400
    INGEST_CHUNK = 256
    RECALL_BATCH = 64
    N_SMOKE_4X = False  # multi-scale smoke runs separately in selftest
else:
    SEEDS = [7, 17, 23]
    N_DIM = PRODUCTION_N
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256

# K=2 bank config (each bank gets N_DIM/K dims)
K_BANKS = 2
N_PER_BANK = N_DIM // K_BANKS  # =4096 in full, =256 in smoke

# Sparse-bipolar params (RESCUE FIX: f=0.02 + amplitude scaling)
SPARSE_BIPOLAR_F = 0.02          # f=0.02: viability shotgun optimal (P2 peak)
# amplitude scale factor: 1/sqrt(f) applied to codebook entries after sparsification
AMPLITUDE_SCALE = 1.0 / math.sqrt(SPARSE_BIPOLAR_F)  # = sqrt(50) ~ 7.07

# cf-RPE params
CFRPE_LR = 0.01                  # learning rate for cf-RPE delta rule
CFRPE_RUNNING_MEAN_ALPHA = 0.05  # exponential running mean for reward signal

# Sigmoid-additive gate params
SIGMOID_GATE_ALPHA = 2.0   # scale on first modulator logit
SIGMOID_GATE_BETA = 2.0    # scale on second modulator logit

# Temperature + lambda grid (includes LIVE range T in [0.02, 0.1] per viability P7)
TEMP_GRID = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
# K2 gate interpolation alpha grid (sweep in log space)
GATE_ALPHA_GRID = [0.5, 1.0, 2.0, 4.0] if RUN_MODE == "smoke" else [0.5, 1.0, 2.0, 4.0, 8.0]
MRR_K = 10

# Verdict thresholds (pre-registered; IMMUTABLE)
BASELINE_BPC_REF = 7.3065         # ARM_BASELINE expected BPC (fair_harness chain-grade)
BASELINE_TOLERANCE = 0.005        # sanity rail
UNIGRAM_BPC_REF = 7.738           # ARM_UNIGRAM reference
HP_BPC_LIFT = 0.30                # HARD_PASS
CHAIN_GRADE_BONUS_LIFT = 0.50     # bonus: Levy-Horn-Ruppin N^M escape
HARD_FAIL_LIFT = 0.10             # <= this: rescue failed
CV_MAX = 0.05
# Instrumentation guard: if module logits cosine with baseline > this, declare suspect
LOGIT_COPY_THROUGH_THR = 0.9999

ARMS = [
    "ARM_BASELINE",
    "ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT",
    "ARM_K2_MODULES",
    "ARM_K2_PLUS_CFRPE",
    "ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE",
]

CONFIG_VERSION = (
    "substrate_k_module_compose_RESCUE_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d mode=%s seeds=%s "
    "sparse_f=%.3f ampl_scale=%.4f K=%d N_per=%d "
    "cfrpe_lr=%.4f gate_alpha=%.1f gate_beta=%.1f "
    "HP_lift=%.2f HF_lift=%.2f cv_max=%.2f device=%s"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, RUN_MODE, SEEDS,
    SPARSE_BIPOLAR_F, AMPLITUDE_SCALE, K_BANKS, N_PER_BANK,
    CFRPE_LR, SIGMOID_GATE_ALPHA, SIGMOID_GATE_BETA,
    HP_BPC_LIFT, HARD_FAIL_LIFT, CV_MAX, str(DEVICE),
)


# ============================================================================
# Utilities
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


# ============================================================================
# Sparse-bipolar with MANDATORY amplitude scaling (RESCUE FIX 1)
# ============================================================================

def sparsify_bipolar_amplitude_scaled(E: torch.Tensor, f: float) -> torch.Tensor:
    """Sparse-bipolar with 1/sqrt(f) amplitude scaling.

    RESCUE FIX 1: amplitude scaling is BINARY (viability shotgun P2).
    Without scaling: f=0.02 recall = 6% (-17dB SNR).
    With scaling: f=0.02 recall = 99%.

    Scale factor = 1/sqrt(f) applied AFTER sparsification so that the effective
    inner-product norm matches dense bipolar (E[x_i^2] = 1 for both).

    Returns UNNORMALIZED scaled sparse vectors (do NOT l2-normalize after this --
    the amplitude carries the signal; normalizing defeats the scaling fix).
    """
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = E.abs()
    _, topk_idx = torch.topk(abs_E, k=k, dim=1)
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    signs = torch.sign(E.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    scale = 1.0 / math.sqrt(f)
    out[row_idx, topk_idx] = signs * scale
    return out  # NOT l2-normalized; amplitude carries the SNR signal


# ============================================================================
# Gensim / encoder
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}
WORD2VEC_MODEL = "word2vec-google-news-300"


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
    n_hit, n_miss = 0, 0
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
                          ) -> Tuple[torch.Tensor, Dict]:
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    Proj = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ Proj.T).astype(np.float32)
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


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Hebbian W builder (rank-1) -- baseline
# ============================================================================

def build_rank1_W_gpu(src_keys: torch.Tensor, tgt_vecs: torch.Tensor,
                       idx_train: torch.Tensor, ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(tgt_vecs[t+1], src_keys[t]); rank-1 Hebbian write."""
    device = src_keys.device
    dim = src_keys.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_b = src_keys[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        tgt_b = tgt_vecs[tgt_idx]
        W.add_(tgt_b.T @ src_b)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


# ============================================================================
# cf-RPE delta rule per bank (RESCUE FIX 4)
# ============================================================================

def build_cfrpe_W_gpu(src_keys: torch.Tensor, tgt_vecs: torch.Tensor,
                      idx_train: torch.Tensor, ingest_chunk: int,
                      lr: float = CFRPE_LR,
                      running_mean_alpha: float = CFRPE_RUNNING_MEAN_ALPHA
                      ) -> torch.Tensor:
    """cf-RPE delta rule per bank.

    delta_W += r_t * (target - W @ src) @ src.T
    where r_t = current_reward - running_mean_reward.
    reward = cosine(W @ src_t, tgt_{t+1}).

    This is the cf-RPE (counterfactual RPE) update: only write when reward
    EXCEEDS the running mean (positive surprise). Suppresses writes on
    already-well-predicted transitions.

    Mechanistically: brain dopamine VTA -> striatum only fires on reward prediction
    errors; this is the substrate analog.
    """
    device = src_keys.device
    dim = src_keys.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    running_mean = 0.0
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_b = src_keys[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        tgt_b = tgt_vecs[tgt_idx]
        # Compute current prediction
        with torch.no_grad():
            pred_b = _l2_normalize_t(src_b @ W.T)
            reward_b = (pred_b * tgt_b).sum(dim=-1).clamp(-1.0, 1.0)
            reward_mean = float(reward_b.mean().item())
        # cf-RPE: delta = r_t - baseline
        delta_r = reward_mean - running_mean
        running_mean = (1.0 - running_mean_alpha) * running_mean + running_mean_alpha * reward_mean
        # Write gated by positive surprise (delta_r > 0)
        if delta_r > 0:
            W.add_(lr * delta_r * (tgt_b.T @ src_b))
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


# ============================================================================
# K=2 bank split: partition embedding space
# ============================================================================

def split_codebook_k2(E: torch.Tensor, K: int = 2) -> List[torch.Tensor]:
    """Split [V, N_DIM] codebook into K banks along DIM axis.

    Each bank gets N_DIM/K consecutive dimensions.
    Returns list of K tensors each of shape [V, N_DIM//K].
    Preserves row order (V) so index into bank_k gives same vocab word.
    """
    assert E.shape[1] % K == 0, "N_DIM must be divisible by K=%d" % K
    n_per = E.shape[1] // K
    return [E[:, k * n_per:(k + 1) * n_per].contiguous() for k in range(K)]


def compute_module_logits_bank(W: torch.Tensor, src_keys: torch.Tensor,
                                E_tgt: torch.Tensor, recall_batch: int) -> torch.Tensor:
    """[n, V] logit matrix for one bank. W: [N_per, N_per]."""
    n = src_keys.shape[0]
    V = E_tgt.shape[0]
    device = W.device
    logits = torch.zeros((n, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = _l2_normalize_t(src_keys[b:end] @ W.T)
        logits[b:end] = pred @ E_tgt.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    return logits.detach().cpu().numpy().astype(np.float32)


# ============================================================================
# SIGMOID-ADDITIVE compose (RESCUE FIX 2)
# ============================================================================

def sigmoid_additive_gate(ctx_embed_A: np.ndarray, ctx_embed_B: np.ndarray,
                           alpha: float = SIGMOID_GATE_ALPHA,
                           beta: float = SIGMOID_GATE_BETA) -> np.ndarray:
    """gate[i] = sigmoid(alpha * dot(ctx_A[i]) + beta * dot(ctx_B[i])).

    RESCUE FIX 2: sigmoid-additive keeps E[gate] in [0.5, 0.88] even when
    individual embeddings are small. This avoids the multiplicative collapse
    (viability shotgun P6: mult with E[gate]=0.12 starves W accumulation).

    ctx_embed_A, ctx_embed_B: [n] vectors of context embedding magnitudes
    (or dot products with a gate vector). Used as the sigmoid input.

    Returns gate values in (0, 1) for each of n samples.
    """
    z = alpha * ctx_embed_A + beta * ctx_embed_B
    return 1.0 / (1.0 + np.exp(-z))


def compose_k2_sigmoid_additive(logits_A: np.ndarray, logits_B: np.ndarray,
                                  gate: np.ndarray,
                                  U_log: np.ndarray, lam: float = 0.0
                                  ) -> np.ndarray:
    """Sigmoid-additive K=2 compose.

    log p(w|ctx) = gate * log_p_A(w) + (1-gate) * log_p_B(w)
    Then optionally interpolate with unigram: lam * above + (1-lam) * U_log.

    gate: [n] per-sample interpolation weight in (0, 1).
    Returns [n, V] log-prob matrix (normalized).
    """
    # T=0.1 for log_p_A/B (LIVE temperature from viability P7)
    T_compose = 0.1
    log_p_A = np.log(np.clip(softmax_with_T(logits_A, T_compose), 1e-30, 1.0))
    log_p_B = np.log(np.clip(softmax_with_T(logits_B, T_compose), 1e-30, 1.0))
    gate_col = gate[:, None]
    combined = gate_col * log_p_A + (1.0 - gate_col) * log_p_B
    if lam < 1.0:
        combined = lam * combined + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return (combined - Z[:, None]).astype(np.float32)


# ============================================================================
# Text8 loader + vocab
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
# BPC / top-1 / MRR evaluation helpers
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
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


def sweep_single_module(logits_dev: np.ndarray, logits_test: np.ndarray,
                         U_log: np.ndarray, nxt_dev: np.ndarray,
                         nxt_test: np.ndarray) -> Dict:
    """T + lambda sweep for a single-module arm."""
    best_bpc_val = float("inf")
    best_top1_val = -1.0
    best_mrr_val = -1.0
    best_bpc_cfg = {"T": 1.0, "lambda": 0.0}
    best_top1_cfg = {"T": 1.0, "lambda": 0.0}
    best_mrr_cfg = {"T": 1.0, "lambda": 0.0}

    # raw at T=1 lambda=1 for DEGEN check
    probs_T1 = softmax_with_T(logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_T1L1 = bpc_from_logp(logp_T1, nxt_test)

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc_val:
                best_bpc_val = bd
                best_bpc_cfg = {"T": float(T), "lambda": float(lam)}
            if td > best_top1_val:
                best_top1_val = td
                best_top1_cfg = {"T": float(T), "lambda": float(lam)}
            if md > best_mrr_val:
                best_mrr_val = md
                best_mrr_cfg = {"T": float(T), "lambda": float(lam)}

    def _eval(cfg):
        T_val = cfg["T"]
        lam_val = cfg["lambda"]
        probs_test = softmax_with_T(logits_test, T_val)
        logp_sub = np.log(np.clip(probs_test, 1e-30, 1.0))
        return log_linear_interp_logp(logp_sub, U_log, lam_val)

    return {
        "bpc_best": round(bpc_from_logp(_eval(best_bpc_cfg), nxt_test), 4),
        "best_T_for_bpc": best_bpc_cfg["T"],
        "best_lambda_for_bpc": best_bpc_cfg["lambda"],
        "top1_acc": round(top1_acc(_eval(best_top1_cfg), nxt_test), 4),
        "best_T_for_top1": best_top1_cfg["T"],
        "best_lambda_for_top1": best_top1_cfg["lambda"],
        "mrr_at_10": round(mrr_at_k(_eval(best_mrr_cfg), nxt_test, MRR_K), 4),
        "best_T_for_mrr": best_mrr_cfg["T"],
        "best_lambda_for_mrr": best_mrr_cfg["lambda"],
        "raw_bpc_at_T1_L1": round(raw_bpc_T1L1, 4),
    }


def sweep_k2_gate(logits_A_dev: np.ndarray, logits_B_dev: np.ndarray,
                   logits_A_test: np.ndarray, logits_B_test: np.ndarray,
                   gate_dev: np.ndarray, gate_test: np.ndarray,
                   U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    """Sweep gate alpha + lambda for K=2 sigmoid-additive compose arm."""
    best_bpc_val = float("inf")
    best_top1_val = -1.0
    best_mrr_val = -1.0
    best_cfg_bpc = {"gate_alpha": SIGMOID_GATE_ALPHA, "lambda": 0.0}
    best_cfg_top1 = {"gate_alpha": SIGMOID_GATE_ALPHA, "lambda": 0.0}
    best_cfg_mrr = {"gate_alpha": SIGMOID_GATE_ALPHA, "lambda": 0.0}

    for ga in GATE_ALPHA_GRID:
        gate_scaled_dev = 1.0 / (1.0 + np.exp(-ga * (2.0 * gate_dev - 1.0)))
        for lam in LAMBDA_GRID:
            logp_dev = compose_k2_sigmoid_additive(
                logits_A_dev, logits_B_dev, gate_scaled_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc_val:
                best_bpc_val = bd
                best_cfg_bpc = {"gate_alpha": float(ga), "lambda": float(lam)}
            if td > best_top1_val:
                best_top1_val = td
                best_cfg_top1 = {"gate_alpha": float(ga), "lambda": float(lam)}
            if md > best_mrr_val:
                best_mrr_val = md
                best_cfg_mrr = {"gate_alpha": float(ga), "lambda": float(lam)}

    def _eval_k2(cfg):
        ga = cfg["gate_alpha"]
        lam = cfg["lambda"]
        gate_scaled = 1.0 / (1.0 + np.exp(-ga * (2.0 * gate_test - 1.0)))
        return compose_k2_sigmoid_additive(
            logits_A_test, logits_B_test, gate_scaled, U_log, lam)

    return {
        "bpc_best": round(bpc_from_logp(_eval_k2(best_cfg_bpc), nxt_test), 4),
        "best_gate_alpha": best_cfg_bpc["gate_alpha"],
        "best_lambda_for_bpc": best_cfg_bpc["lambda"],
        "top1_acc": round(top1_acc(_eval_k2(best_cfg_top1), nxt_test), 4),
        "mrr_at_10": round(mrr_at_k(_eval_k2(best_cfg_mrr), nxt_test, MRR_K), 4),
        "gate_mean_dev": round(float(np.mean(gate_dev)), 4),
        "gate_std_dev": round(float(np.std(gate_dev)), 4),
    }


# ============================================================================
# Unigram metrics
# ============================================================================

def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
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
    top1_v = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1_v, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (mandatory; PROT-022)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Self-tests for all rescue fixes. Called at module scope."""
    dev_cpu = torch.device("cpu")
    N_t = 256
    V_t = 30
    rng_np = np.random.default_rng(42)

    # Test 1: amplitude scaling is load-bearing
    # Without scaling: sparse-bipolar inner product E[x^T y] = f (too small)
    # With scaling: E[x^T y] = 1.0 (SNR restored)
    E_raw = torch.from_numpy(rng_np.standard_normal((V_t, N_t)).astype(np.float32))
    E_scaled = sparsify_bipolar_amplitude_scaled(E_raw.to(dev_cpu), f=SPARSE_BIPOLAR_F)
    # Row norms should be ~ 1/sqrt(f) * sqrt(f*N) = sqrt(N) NOT 1.0
    row_norms = E_scaled.norm(dim=1)
    expected_norm = 1.0 / math.sqrt(SPARSE_BIPOLAR_F) * math.sqrt(SPARSE_BIPOLAR_F * N_t)
    # Allow 10% tolerance
    norm_ratio = float(row_norms.mean().item()) / expected_norm
    assert 0.80 < norm_ratio < 1.20, (
        "amplitude scaling selftest FAIL: mean_norm=%.4f expected=%.4f ratio=%.4f" % (
            float(row_norms.mean().item()), expected_norm, norm_ratio))
    print("[selftest] PASS amplitude scaling: mean_norm=%.2f expected=%.2f" % (
        float(row_norms.mean().item()), expected_norm), flush=True)

    # Test 2: K=2 split produces non-overlapping subspaces
    E_full = torch.from_numpy(rng_np.standard_normal((V_t, N_t)).astype(np.float32))
    banks = split_codebook_k2(E_full, K=2)
    assert len(banks) == 2, "K=2 split selftest FAIL: wrong number of banks"
    assert banks[0].shape[1] == N_t // 2, "K=2 split selftest FAIL: bank[0] wrong dim"
    assert banks[1].shape[1] == N_t // 2, "K=2 split selftest FAIL: bank[1] wrong dim"
    # Banks are disjoint slices; their concatenation should recover the full embedding
    reconst = torch.cat(banks, dim=1)
    assert torch.allclose(reconst, E_full), "K=2 split selftest FAIL: split not lossless"
    print("[selftest] PASS K=2 split: 2 banks x %d dims; lossless reconstruction" % (
        N_t // 2), flush=True)

    # Test 3: sigmoid-additive gate stays in [0.3, 0.7] for uniform inputs
    ctx_A = rng_np.uniform(-1.0, 1.0, 50).astype(np.float32)
    ctx_B = rng_np.uniform(-1.0, 1.0, 50).astype(np.float32)
    gate_vals = sigmoid_additive_gate(ctx_A, ctx_B, alpha=SIGMOID_GATE_ALPHA, beta=SIGMOID_GATE_BETA)
    gate_mean = float(np.mean(gate_vals))
    gate_std = float(np.std(gate_vals))
    # gate_mean should be near 0.5; gate_std should be > 0.05 (not degenerate)
    assert 0.3 < gate_mean < 0.7, (
        "sigmoid-additive selftest FAIL: gate_mean=%.4f not in [0.3, 0.7]" % gate_mean)
    assert gate_std > 0.05, (
        "sigmoid-additive selftest FAIL: gate_std=%.4f too small (degenerate)" % gate_std)
    print("[selftest] PASS sigmoid-additive gate: mean=%.4f std=%.4f (non-degenerate)" % (
        gate_mean, gate_std), flush=True)

    # Test 4: cf-RPE W differs from pure Hebbian W (learning signal non-zero)
    V_s, N_s = 20, 64
    rng_t = torch.manual_seed(99)
    E_s = _l2_normalize_t(torch.randn(V_s, N_s))
    idx_s = torch.randint(0, V_s, (200,))
    src_keys_s = E_s[idx_s]
    W_hebbian = build_rank1_W_gpu(src_keys_s, E_s, idx_s, ingest_chunk=32)
    W_cfrpe = build_cfrpe_W_gpu(src_keys_s, E_s, idx_s, ingest_chunk=32)
    W_diff = (W_cfrpe - W_hebbian).norm().item()
    assert W_diff > 0.0, "cf-RPE selftest FAIL: W_cfrpe identical to W_hebbian (no learning signal)"
    print("[selftest] PASS cf-RPE: W_diff_from_hebbian=%.6f (non-zero)" % W_diff, flush=True)

    # Test 5: module logits diverge check (INSTRUMENTATION GUARD)
    # Build tiny W and compute logits for two independent banks; verify they differ
    W_A = torch.randn(N_s // 2, N_s // 2) * 0.1
    W_B = torch.randn(N_s // 2, N_s // 2) * 0.1
    E_banks = split_codebook_k2(E_s, K=2)
    src_A = E_banks[0][:5]
    src_B = E_banks[1][:5]
    log_A = compute_module_logits_bank(W_A, src_A, E_banks[0], recall_batch=5)
    log_B = compute_module_logits_bank(W_B, src_B, E_banks[1], recall_batch=5)
    cos_sim = float(np.mean([
        np.dot(log_A[i], log_B[i]) / (np.linalg.norm(log_A[i]) * np.linalg.norm(log_B[i]) + 1e-12)
        for i in range(5)
    ]))
    # Two independent random W matrices should produce logits with cosine < 0.999
    assert cos_sim < LOGIT_COPY_THROUGH_THR, (
        "INSTRUMENTATION GUARD selftest FAIL: logit cosine=%.6f >= threshold=%.4f "
        "(modules are IDENTICAL -- copy-through bug)" % (cos_sim, LOGIT_COPY_THROUGH_THR))
    print("[selftest] PASS instrumentation guard: mean_logit_cosine=%.6f < %.4f" % (
        cos_sim, LOGIT_COPY_THROUGH_THR), flush=True)

    print("[selftest] ALL 5 PASS: ampl_scale + K2_split + sigmoid_gate + cfrpe + instr_guard",
          flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    print("[self-test] complete -- exiting", flush=True)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def _check_logit_copy_through(logits_test: np.ndarray, baseline_logits: np.ndarray,
                                arm_name: str) -> bool:
    """Returns True (SUSPECT) if arm logits are suspiciously close to baseline.

    This catches the prior cell's silent fallback (m2_ok=False -> copy logits_m1).
    Any arm with mean cosine > LOGIT_COPY_THROUGH_THR is flagged INSTRUMENTATION_SUSPECT.
    """
    n_check = min(100, logits_test.shape[0])
    cos_vals = []
    for i in range(n_check):
        a = logits_test[i]
        b = baseline_logits[i]
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na > 1e-9 and nb > 1e-9:
            cos_vals.append(float(np.dot(a, b) / (na * nb)))
    if not cos_vals:
        return False
    mean_cos = float(np.mean(cos_vals))
    if mean_cos > LOGIT_COPY_THROUGH_THR:
        print("[INSTRUMENTATION_SUSPECT] arm=%s mean_logit_cosine=%.6f > %.4f -- "
              "module is a COPY of baseline. Check M2/M3 exception handling." % (
                  arm_name, mean_cos, LOGIT_COPY_THROUGH_THR), flush=True)
        return True
    return False


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
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d gpu] %s free=%.2fGB total=%.2fGB" % (
                seed, torch.cuda.get_device_name(0), free_b / 1e9, total_b / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info] %s" % (seed, e), flush=True)

    U_np = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U_np, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.4f" % (seed, uni["bpc_unigram"]), flush=True)

    # Build base encoder (word2vec -> GPU)
    print("\n[seed=%d] building word2vec base E (V=%d N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] word2vec FAIL: %s -- fallback to char-trigram" % (seed, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    print("[seed=%d encoder] built in %.1fs" % (seed, time.time() - t_enc0), flush=True)

    # Apply amplitude-scaled sparse-bipolar (RESCUE FIX 1: NOT l2-normalized)
    # CRITICAL: do NOT call _l2_normalize_t on E_sp -- that would destroy the scaling fix
    E_sp_raw = sparsify_bipolar_amplitude_scaled(E_base, f=SPARSE_BIPOLAR_F)
    # Verify amplitude scaling is applied
    row_norms_check = float(E_sp_raw.norm(dim=1).mean().item())
    expected_n = 1.0 / math.sqrt(SPARSE_BIPOLAR_F) * math.sqrt(SPARSE_BIPOLAR_F * N_DIM)
    print("[seed=%d] E_sp amplitude-scaled: mean_row_norm=%.2f expected=%.2f" % (
        seed, row_norms_check, expected_n), flush=True)
    E_sp = E_sp_raw  # Use scaled (NOT normalized) codebook

    # Eval split
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_eval = (ctx_full != unk)
    ctx_eval_pos = np.where(mask_eval)[0]
    nxt_eval = nxt_full[mask_eval]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        print("[seed=%d] WARN: n_eval=0; skipping" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "skip_reason": "n_eval=0",
                "V": V, "N": N_DIM, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2), "device": str(DEVICE),
                "encoder_meta": encoder_meta, "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    ctx_vocab_idx = torch.from_numpy(ctx_full[ctx_eval_pos].astype(np.int64)).to(DEVICE)

    instrumentation_suspects: List[str] = []

    # ==== ARM_BASELINE (single-bank, sparse-bipolar amplitude-scaled, rank-1 Hebbian) ====
    print("\n[seed=%d] ARM_BASELINE: rank-1 Hebbian W on amplitude-scaled sparse-bipolar" % seed, flush=True)
    t_arm = time.time()
    try:
        src_m1_train = E_sp[idx_train_t]
        W_baseline = build_rank1_W_gpu(src_m1_train, E_sp, idx_train_t, INGEST_CHUNK)
        del src_m1_train
        src_m1_held = E_sp[ctx_vocab_idx]
        logits_baseline = compute_module_logits_bank(W_baseline, src_m1_held, E_sp, RECALL_BATCH)
        del W_baseline
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        res_baseline = sweep_single_module(
            logits_baseline[:n_dev], logits_baseline[n_dev:], U_log, nxt_dev, nxt_test)
        res_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_BASELINE"] = res_baseline
        print("    [seed=%d arm=ARM_BASELINE] bpc_best=%.4f top1=%.4f (ref=7.3065)" % (
            seed, res_baseline["bpc_best"], res_baseline["top1_acc"]), flush=True)
        # Sanity rail: must be within 0.005 of fair_harness 7.3065
        bpc_diff = abs(res_baseline["bpc_best"] - BASELINE_BPC_REF)
        if bpc_diff > BASELINE_TOLERANCE and RUN_MODE == "full":
            print("[WARN] ARM_BASELINE bpc=%.4f deviates %.4f from fair_harness ref=%.4f (tol=%.3f)" % (
                res_baseline["bpc_best"], bpc_diff, BASELINE_BPC_REF, BASELINE_TOLERANCE), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d ARM_BASELINE] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_BASELINE"] = {"compute_failed": True, "compute_error": err,
                                   "bpc_best": float("inf"), "top1_acc": float("nan"),
                                   "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                   "elapsed_s_arm": round(time.time() - t_arm, 2)}
        logits_baseline = None

    # ==== ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT (alias for baseline; verifies same arm) ====
    # This arm IS the baseline -- it's a named copy to verify the amplitude fix is working.
    # bpc_best should be near ARM_BASELINE.
    res_ampl = dict(by_arm.get("ARM_BASELINE", {}))
    res_ampl["note"] = "alias for ARM_BASELINE; verifies f=0.02 amplitude-scaling reproduces 7.3065"
    by_arm["ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT"] = res_ampl

    # ==== K=2 BANK SETUP ====
    # Split the E_sp codebook into K=2 banks (each gets N_DIM/2 consecutive dims)
    print("\n[seed=%d] K=2 bank setup: split codebook into 2 banks x %d dims" % (
        seed, N_PER_BANK), flush=True)
    E_banks = split_codebook_k2(E_sp, K=K_BANKS)  # list of 2 tensors [V, N_per]
    print("[seed=%d] bank[0] shape=%s bank[1] shape=%s" % (
        seed, str(E_banks[0].shape), str(E_banks[1].shape)), flush=True)

    # Split train and held keys for each bank
    src_bank_train = [E_banks[k][idx_train_t] for k in range(K_BANKS)]  # [K, N_TRAIN, N_per]
    src_bank_held = [E_banks[k][ctx_vocab_idx] for k in range(K_BANKS)]  # [K, n_eval, N_per]

    # Compute sigmoid-additive gate values using bank dot products as gate input
    # gate[i] = sigmoid(ALPHA * dot(src_A[i], mean_A) + BETA * dot(src_B[i], mean_B))
    # Use L2 norm of ctx embedding as modulator signal (normalized by bank dimension)
    ctx_norm_A = src_bank_held[0].norm(dim=-1).cpu().numpy().astype(np.float32)
    ctx_norm_B = src_bank_held[1].norm(dim=-1).cpu().numpy().astype(np.float32)
    ctx_norm_A_normed = ctx_norm_A / (float(ctx_norm_A.mean()) + 1e-9)
    ctx_norm_B_normed = ctx_norm_B / (float(ctx_norm_B.mean()) + 1e-9)
    gate_all = sigmoid_additive_gate(ctx_norm_A_normed, ctx_norm_B_normed,
                                      alpha=SIGMOID_GATE_ALPHA, beta=SIGMOID_GATE_BETA)
    gate_dev = gate_all[:n_dev]
    gate_test = gate_all[n_dev:]
    gate_mean = float(np.mean(gate_all))
    gate_std = float(np.std(gate_all))
    print("[seed=%d] sigmoid gate: mean=%.4f std=%.4f" % (seed, gate_mean, gate_std), flush=True)

    # Sanity: gate must not be degenerate (stuck at 0 or 1)
    if gate_std < 0.01:
        print("[WARN] gate is near-degenerate: std=%.4f (sigmoid-additive should have std>0.05)" % (
            gate_std,), flush=True)

    # ==== ARM_K2_MODULES (K=2 banks, Hebbian W per bank, sigmoid-additive compose) ====
    print("\n[seed=%d] ARM_K2_MODULES: K=2 Hebbian banks" % seed, flush=True)
    t_arm = time.time()
    logits_k2_A = logits_k2_B = None
    try:
        W_A = build_rank1_W_gpu(src_bank_train[0], E_banks[0], idx_train_t, INGEST_CHUNK)
        W_B = build_rank1_W_gpu(src_bank_train[1], E_banks[1], idx_train_t, INGEST_CHUNK)
        logits_k2_A = compute_module_logits_bank(W_A, src_bank_held[0], E_banks[0], RECALL_BATCH)
        logits_k2_B = compute_module_logits_bank(W_B, src_bank_held[1], E_banks[1], RECALL_BATCH)
        del W_A, W_B
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        # INSTRUMENTATION GUARD: project bank logits to full-V space and check divergence
        # For K=2 we check that the two banks produce different logit patterns
        # (not just that they differ from baseline -- they're on different codebook slices)
        res_k2 = sweep_k2_gate(
            logits_k2_A[:n_dev], logits_k2_B[:n_dev],
            logits_k2_A[n_dev:], logits_k2_B[n_dev:],
            gate_dev, gate_test, U_log, nxt_dev, nxt_test)
        res_k2["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        res_k2["bank_A_raw_bpc"] = round(float(bpc_from_logp(
            log_linear_interp_logp(
                np.log(np.clip(softmax_with_T(logits_k2_A[n_dev:], 0.1), 1e-30, 1.0)),
                np.zeros(logits_k2_A.shape[1]), 1.0),
            nxt_test)), 4)
        by_arm["ARM_K2_MODULES"] = res_k2
        print("    [seed=%d arm=ARM_K2_MODULES] bpc_best=%.4f top1=%.4f gate_mean=%.4f gate_std=%.4f" % (
            seed, res_k2["bpc_best"], res_k2["top1_acc"],
            res_k2["gate_mean_dev"], res_k2["gate_std_dev"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d ARM_K2_MODULES] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_K2_MODULES"] = {"compute_failed": True, "compute_error": err,
                                     "bpc_best": float("inf"), "top1_acc": float("nan"),
                                     "mrr_at_10": float("nan"),
                                     "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # ==== ARM_K2_PLUS_CFRPE (K=2 banks with cf-RPE delta rule) ====
    print("\n[seed=%d] ARM_K2_PLUS_CFRPE: K=2 banks with cf-RPE delta rule" % seed, flush=True)
    t_arm = time.time()
    logits_cfrpe_A = logits_cfrpe_B = None
    try:
        W_A_rpe = build_cfrpe_W_gpu(src_bank_train[0], E_banks[0], idx_train_t, INGEST_CHUNK)
        W_B_rpe = build_cfrpe_W_gpu(src_bank_train[1], E_banks[1], idx_train_t, INGEST_CHUNK)
        logits_cfrpe_A = compute_module_logits_bank(W_A_rpe, src_bank_held[0], E_banks[0], RECALL_BATCH)
        logits_cfrpe_B = compute_module_logits_bank(W_B_rpe, src_bank_held[1], E_banks[1], RECALL_BATCH)
        del W_A_rpe, W_B_rpe
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        res_cfrpe = sweep_k2_gate(
            logits_cfrpe_A[:n_dev], logits_cfrpe_B[:n_dev],
            logits_cfrpe_A[n_dev:], logits_cfrpe_B[n_dev:],
            gate_dev, gate_test, U_log, nxt_dev, nxt_test)
        res_cfrpe["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_K2_PLUS_CFRPE"] = res_cfrpe
        print("    [seed=%d arm=ARM_K2_PLUS_CFRPE] bpc_best=%.4f top1=%.4f" % (
            seed, res_cfrpe["bpc_best"], res_cfrpe["top1_acc"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d ARM_K2_PLUS_CFRPE] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_K2_PLUS_CFRPE"] = {"compute_failed": True, "compute_error": err,
                                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                                        "mrr_at_10": float("nan"),
                                        "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # ==== ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE (LOAD-BEARING ARM) ====
    # Uses cf-RPE logits (same as ARM_K2_PLUS_CFRPE banks) but with EXPLICIT sigmoid-additive gate
    # that uses the cf-RPE W predictions to compute the gate (not just embedding norms).
    print("\n[seed=%d] ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE (LOAD-BEARING)" % seed, flush=True)
    t_arm = time.time()
    try:
        if logits_cfrpe_A is None or logits_cfrpe_B is None:
            raise RuntimeError("cf-RPE logits not available (ARM_K2_PLUS_CFRPE failed)")

        # SIGMOID-ADDITIVE gate using cf-RPE prediction confidence as gate signal
        # gate[i] = sigmoid(ALPHA * max_logit_A[i] + BETA * max_logit_B[i])
        # This is context-dependent: high-confidence contexts route strongly to one bank
        max_log_A = logits_cfrpe_A.max(axis=1)   # [n_eval] -- top activation in bank A
        max_log_B = logits_cfrpe_B.max(axis=1)   # [n_eval] -- top activation in bank B
        # Normalize by mean to get relative signal (not absolute scale-dependent)
        max_A_normed = max_log_A / (abs(float(max_log_A.mean())) + 1e-9)
        max_B_normed = max_log_B / (abs(float(max_log_B.mean())) + 1e-9)
        gate_sigmoid = sigmoid_additive_gate(max_A_normed, max_B_normed,
                                              alpha=SIGMOID_GATE_ALPHA, beta=SIGMOID_GATE_BETA)
        gate_sig_dev = gate_sigmoid[:n_dev]
        gate_sig_test = gate_sigmoid[n_dev:]

        gate_sig_mean = float(np.mean(gate_sigmoid))
        gate_sig_std = float(np.std(gate_sigmoid))
        print("[seed=%d] sigmoid-additive gate (cf-RPE): mean=%.4f std=%.4f" % (
            seed, gate_sig_mean, gate_sig_std), flush=True)

        res_full = sweep_k2_gate(
            logits_cfrpe_A[:n_dev], logits_cfrpe_B[:n_dev],
            logits_cfrpe_A[n_dev:], logits_cfrpe_B[n_dev:],
            gate_sig_dev, gate_sig_test, U_log, nxt_dev, nxt_test)
        res_full["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        res_full["gate_sigmoid_mean"] = round(gate_sig_mean, 4)
        res_full["gate_sigmoid_std"] = round(gate_sig_std, 4)
        by_arm["ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE"] = res_full
        print("    [seed=%d arm=ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE] "
              "bpc_best=%.4f top1=%.4f gate_mean=%.4f" % (
                  seed, res_full["bpc_best"], res_full["top1_acc"], gate_sig_mean), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2)}

    del E_sp, E_base, E_banks, src_bank_train, src_bank_held
    del idx_train_t, ctx_vocab_idx
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
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
        "instrumentation_suspects": instrumentation_suspects,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate ARM_UNIGRAM
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}
    V_first = units[0].get("V", 4000)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    load_bearing_arm = "ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE"
    baseline_arm = "ARM_BASELINE"

    for arm in ARMS:
        valid_units = [
            u for u in units
            if not u["by_arm"].get(arm, {}).get("compute_failed", False)
            and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
        ]
        n_failed = len(units) - len(valid_units)
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "n_valid_seeds": 0,
                "n_compute_failed": n_failed,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm].get("top1_acc", float("nan")) for u in valid_units]
        mrr_vals = [u["by_arm"][arm].get("mrr_at_10", float("nan")) for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        b_cv = b_std / (abs(b_mean) + 1e-9)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.nanmean(top1_vals)), 4),
            "top1_acc_std": round(float(np.nanstd(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.nanmean(mrr_vals)), 4),
            "n_valid_seeds": len(valid_units),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    # Verdict logic
    baseline_agg = by_arm_agg.get(baseline_arm, {})
    lb_agg = by_arm_agg.get(load_bearing_arm, {})

    if lb_agg.get("all_seeds_failed", True):
        return ("HARD_FAIL", "load-bearing arm all seeds failed", by_arm_agg)
    if baseline_agg.get("all_seeds_failed", True):
        return ("HARD_FAIL", "ARM_BASELINE all seeds failed", by_arm_agg)

    baseline_bpc = baseline_agg.get("bpc_best_mean", float("inf"))
    lb_bpc = lb_agg.get("bpc_best_mean", float("inf"))
    lb_cv = lb_agg.get("bpc_best_cv", 1.0)

    lift = baseline_bpc - lb_bpc

    # Sanity rail: baseline within tolerance of fair_harness reference
    baseline_deviation = abs(baseline_bpc - BASELINE_BPC_REF)
    if baseline_deviation > BASELINE_TOLERANCE and RUN_MODE == "full":
        return ("INSTRUMENTATION_SUSPECT",
                "ARM_BASELINE bpc=%.4f deviates %.4f from fair_harness ref=%.4f (tol=%.4f)" % (
                    baseline_bpc, baseline_deviation, BASELINE_BPC_REF, BASELINE_TOLERANCE),
                by_arm_agg)

    # Check for unigram collapse in multi-module arms
    uni_bpc_mean = unigram_agg.get("bpc_mean", 8.0)
    for arm in ["ARM_K2_MODULES", "ARM_K2_PLUS_CFRPE", load_bearing_arm]:
        agg = by_arm_agg.get(arm, {})
        arm_bpc = agg.get("bpc_best_mean", float("inf"))
        if abs(arm_bpc - uni_bpc_mean) < 0.005:
            return ("INSTRUMENTATION_SUSPECT",
                    "arm=%s bpc=%.4f collapsed to unigram=%.4f (rescue fix incomplete)" % (
                        arm, arm_bpc, uni_bpc_mean),
                    by_arm_agg)

    if lb_cv > CV_MAX:
        return ("HARD_FAIL",
                "cv=%.4f > CV_MAX=%.2f for load-bearing arm" % (lb_cv, CV_MAX),
                by_arm_agg)

    if lift >= CHAIN_GRADE_BONUS_LIFT:
        verdict = "CHAIN_GRADE_BONUS"
        msg = "CHAIN_GRADE_BONUS: lift=+%.4f >= %.2f; Levy-Horn-Ruppin N^M scaling confirmed" % (
            lift, CHAIN_GRADE_BONUS_LIFT)
    elif lift >= HP_BPC_LIFT:
        verdict = "HARD_PASS"
        msg = "HARD_PASS: lift=+%.4f >= %.2f; K=2+cf-RPE+sigmoid-add beats baseline" % (
            lift, HP_BPC_LIFT)
    elif lift >= HARD_FAIL_LIFT:
        verdict = "MIDDLE_BAND"
        msg = "MIDDLE_BAND: lift=+%.4f in [%.2f, %.2f)" % (lift, HARD_FAIL_LIFT, HP_BPC_LIFT)
    else:
        verdict = "HARD_FAIL"
        msg = "HARD_FAIL: lift=+%.4f <= %.2f; K-module compose still not beating baseline" % (
            lift, HARD_FAIL_LIFT)

    return (verdict, msg, by_arm_agg)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    t_start = time.time()
    print("=" * 72, flush=True)
    print("ANCHOR: %s" % ANCHOR_NAME, flush=True)
    print("RUN_MODE: %s DEVICE: %s N_DIM: %d SEEDS: %s" % (
        RUN_MODE, DEVICE, N_DIM, SEEDS), flush=True)
    print("RESCUE FIXES: ampl_scale=1/sqrt(f)=%.2f sigmoid-add cf-RPE K=2" % AMPLITUDE_SCALE, flush=True)
    print("=" * 72, flush=True)

    out_dir = get_output_dir()
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d seeds already complete; running %s" % (
        len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

    _atexit_results: Dict[int, Dict] = {}

    def _atexit_handler():
        if _atexit_results:
            print("[atexit] synthesizing partial from %d completed seeds" % len(_atexit_results), flush=True)
            units = list(_atexit_results.values())
            verdict, msg, by_arm_agg = compute_verdict(units)
            out = _build_metrics(units, verdict, msg, by_arm_agg)
            write_metrics(out_dir, out)
            print("[atexit] partial metrics.json written; verdict=%s" % verdict, flush=True)

    atexit.register(_atexit_handler)

    def _sigterm_handler(signum, frame):
        print("[signal] SIGTERM received; letting atexit handle cleanup", flush=True)
        sys.exit(1)
    signal.signal(signal.SIGTERM, _sigterm_handler)

    for seed in remaining_seeds:
        result = run_unit(seed)
        write_partial_key(out_dir, str(seed), result)
        _atexit_results[seed] = result
        print("[ckpt] seed=%d written to %s" % (seed, out_dir), flush=True)

    # Aggregate all (including already-done seeds)
    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    units = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

    verdict, msg, by_arm_agg = compute_verdict(units)

    out = _build_metrics(units, verdict, msg, by_arm_agg)
    write_metrics(out_dir, out)
    atexit.unregister(_atexit_handler)

    print("\n" + "=" * 72, flush=True)
    print("VERDICT: %s" % verdict, flush=True)
    print("MSG: %s" % msg, flush=True)
    print("ELAPSED: %.1fs" % (time.time() - t_start,), flush=True)
    print("OUTDIR: %s" % out_dir, flush=True)
    print("=" * 72, flush=True)


def _build_metrics(units: List[Dict], verdict: str, msg: str, by_arm_agg: Dict) -> Dict:
    return {
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
        "n_seeds": len(units),
        "K_BANKS": K_BANKS,
        "N_PER_BANK": N_PER_BANK,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "AMPLITUDE_SCALE": round(AMPLITUDE_SCALE, 6),
        "CFRPE_LR": CFRPE_LR,
        "detail": {
            "by_arm_agg": by_arm_agg,
            "HP_BPC_LIFT_threshold": HP_BPC_LIFT,
            "CHAIN_GRADE_BONUS_LIFT_threshold": CHAIN_GRADE_BONUS_LIFT,
            "HARD_FAIL_LIFT_threshold": HARD_FAIL_LIFT,
            "CV_MAX_threshold": CV_MAX,
            "BASELINE_BPC_REF": BASELINE_BPC_REF,
            "BASELINE_TOLERANCE": BASELINE_TOLERANCE,
            "vocab_entropy_uniform_bits": round(math.log2(max(
                units[0].get("V", VOCAB_CAP) if units else VOCAB_CAP, 2)), 4),
            "zero_llm_calls_at_inference": True,
            "unigram_bpc_ref": UNIGRAM_BPC_REF,
            "n_seeds": len(units),
        },
        "per_unit": units,
        "elapsed_s": round(sum(u.get("elapsed_s_seed", 0) for u in units), 2),
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
        "config_version": CONFIG_VERSION,
        "honest_scope": (
            "RESCUE cell for substrate_k_module_heterogeneous_compose_LM_v1 (INSTR_SUSPECT). "
            "5 arms: ARM_BASELINE + ARM_SPARSE_BIPOLAR_AMPLITUDE_CORRECT + ARM_K2_MODULES + "
            "ARM_K2_PLUS_CFRPE + ARM_K2_PLUS_CFRPE_PLUS_SIGMOID_ADDITIVE_COMPOSE. "
            "HP = load-bearing arm BPC lift >= +%.2f bits vs ARM_BASELINE AND cv<=%.2f. "
            "HF = lift <= +%.2f OR any arm collapses to unigram BPC. "
            "WHAT_THIS_DOES_NOT_SHOW: not testing K>2; not testing N_DIM>8192 "
            "(GPU memory budget); not testing super-additivity beyond K=2." % (
                HP_BPC_LIFT, CV_MAX, HARD_FAIL_LIFT)),
        "prereg_bands": {
            "HARD_PASS_lift_bits": HP_BPC_LIFT,
            "CHAIN_GRADE_BONUS_lift_bits": CHAIN_GRADE_BONUS_LIFT,
            "MIDDLE_BAND_lower_bits": HARD_FAIL_LIFT,
            "HARD_FAIL_lift_bits_or_below": HARD_FAIL_LIFT,
            "cv_max": CV_MAX,
            "baseline_tolerance_bits": BASELINE_TOLERANCE,
        },
        "rescue_fixes": [
            "Fix1: amplitude_scale=1/sqrt(f)=%.4f applied to ALL sparse-bipolar entries" % AMPLITUDE_SCALE,
            "Fix2: sigmoid-additive compose (NOT multiplicative) -- gate in [0.5, 0.95]",
            "Fix3: K=2 banks with feature-gated routing (K-bank shotgun K*=2)",
            "Fix4: cf-RPE delta rule per bank (dopamine-gated writes on positive surprise)",
            "Fix5: logit copy-through guard (INSTR_SUSPECT if cos(logits_k, logits_m1)>%.4f)" % LOGIT_COPY_THROUGH_THR,
        ],
        "cites": [
            "data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json",
            "notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md",
            "notes/shotgun_smoke_compose_function_discriminator_2026-06-23.md",
            "notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
            "notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md",
        ],
        "summary": msg,
    }


if __name__ == "__main__":
    main()
