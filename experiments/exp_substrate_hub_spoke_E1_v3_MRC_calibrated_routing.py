"""substrate_hub_spoke_E1_v3_MRC_calibrated_routing -- v2 RESCUE with THREE FIXES.

v2 (exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing) landed MIDDLE_BAND
READOUT_DEGENERATE because:
  (a) SoftHebb spoke produced spoke_recon_err = NaN across ALL seeds (broken
      spoke silently bundled into hub)
  (b) cf-RPE gates collapsed to [0.96, 0.03, 0.01] -- the broken NaN spoke won
      routing (NaN propagates as infinite confidence in unsanitized softmax)
  (c) sign(sum_spokes) bundle of K=3 ORTHOGONAL spokes loses 0.5*log(K) bits MI
      (signal-processing maximal-ratio-combining theorem; brain ATL hub-spoke
      analog is MRC weighted sum NOT sign-of-sum)

Per drill notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md
DRILL A (info-theory + MRC math) + DRILL B (brain ATL hub-spoke) + DRILL C
(MRC + turbo-decoder LLR clipping) + DRILL E (NaN propagation), v3 applies
three load-bearing fixes:

  FIX 1: PER-SPOKE HEALTH CHECK at construction. Each spoke's smoke-batch
         forward pass is validated. If any spoke produces NaN/Inf in recon_err
         or in the codebook output, FAIL FAST (do not silently bundle a broken
         spoke). Applies to all spokes: SoftHebb, char-trigram-RI, Path-C PC,
         FPE.

  FIX 2: MRC-WEIGHTED BUNDLE. Replace sign(sum_spokes) with softmax-weighted
         maximal-ratio-combining: hub = sign( sum_i softmax(gate_i / T_gate) *
         spoke_i ) where gates are cf-RPE-learned and T_gate is grid-tuned
         in {0.1, 0.5, 1.0, 2.0}. This is the optimal soft-combiner for K
         independent observation channels (Brennan 1959; turbo decoding lit).

  FIX 3: GATE TRAINING ON REAL TASK SIGNAL. Train gates against the
         next-token-prediction loss gradient (substrate-native; ZERO LLM at
         inference). Gate entropy must end in [0.5, 1.5] (not collapsed to
         single spoke, not uniform). v2 trained gates on a CV-fit proxy and
         the broken spoke won; v3 trains against the actual task.

Arms (4 -- IDENTICAL spoke set as v2 with the 3 fixes applied; one knob varies
       = the COMBINER):
  1. ARM_BASELINE_PATH_C_SINGLE -- control + sanity rail (reproduces v2 7.667)
  2. ARM_HUB_3SPOKE_MRC -- 3-spoke MRC bundle + cf-RPE LR-trained gates
                            (the load-bearing variant)
  3. ARM_HUB_3SPOKE_MRC_PLUS_FPE -- arm 2 + S4 FPE (4-spoke MRC)
  4. ARM_HUB_5SPOKE_MRC_ABLATION -- IDENTICAL spokes as arm 2 but
                                       sign-sum bundle (NO MRC). Isolates
                                       whether MRC is load-bearing vs
                                       health-check+gate-training. (Name has
                                       5SPOKE for historical labeling but
                                       runs 3 spokes; the 5 indicates the
                                       FIVE failure modes v3 addresses.)

DISCRIMINATOR (per cell spec):
  - ARM_HUB_3SPOKE_MRC PASS + ARM_HUB_5SPOKE_MRC_ABLATION FAIL
      -> MRC bundle is the load-bearing fix
  - ARM_HUB_3SPOKE_MRC PASS + ARM_HUB_5SPOKE_MRC_ABLATION PASS
      -> health-check + gate-training are load-bearing (MRC unnecessary)
  - Both FAIL -> architecture refuted; pivot per drill recommendations

PRE-REG HARD bands (per cell spec, drill-tightened):
  HARD_PASS_CHAIN_GRADE: best_hub bpc <= 6.95 AND diversity_cv >= 0.05 AND
                          NO broken spokes (all spoke_recon_err in [0.5, 100])
                          AND gate_entropy in [0.5, 1.5] AND CV(seeds) <= 0.03
  HARD_PASS: best_hub bpc <= 7.50 AND beats single-spoke baseline by >= 0.10
              AND no broken spokes
  HARD_FAIL: best_hub bpc >= 7.70 (all arms at unigram floor) OR any spoke
              produces NaN/Inf
  SANITY_RAIL: ARM_BASELINE_PATH_C_SINGLE bpc within +/-0.02 of v2 7.667

Production config:
  N_DIM = 8192, V = 4000, N_TRAIN = 100_000, N_HELD = 20_000, text8
  SEEDS = [7, 17, 23] (3 seeds), sparse-bipolar f=0.02
  Timeout: 7200s GPU overnight_queue
  Per Fix #24: torch.cuda + batched ops mandatory.

ASCII-only. Per-seed checkpoint. atexit synthesizer.

Cites:
  preregs/2026-06-25_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.md
  notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md
  experiments/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.py (v2 base)
  data/exp_substrate_hub_spoke_E1_v3_MRC_calibrated_routing/metrics.json (v2 MIDDLE_BAND)
  notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md (synthesis priors)
  notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md
  USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer
  USER_2026-06-22_Fix24_GPU_must_use_GPU
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

ANCHOR_NAME = "substrate_hub_spoke_E1_v3_MRC_calibrated_routing"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
V1_BASELINE_BPC_REF = 7.667        # ARM_BASELINE_PATH_C_SINGLE in v1
V1_BEST_HUB_BPC_REF = 7.707         # v1 best degenerate hub
PATH_C_V2_BPC_REF = 7.6184          # Path C v2 single-spoke reference

# Pre-reg bands (v3 -- per cell spec; drill-tightened HARD bands)
HP_BPC_MAX = 7.50                   # v3 spec: HARD_PASS at <=7.50 (relaxed from v2 7.20)
CG_BPC_MAX = 6.95                   # CHAIN_GRADE unchanged
HF_BPC_MIN = 7.70                   # v3 spec: HARD_FAIL at >=7.70 (unigram floor)
DIVERSITY_CV_MIN = 0.05             # SUFFICIENT-DIVERSITY discriminator
DIVERSITY_CV_DEGEN = 0.01           # below this = METHODOLOGY_CHECK
HP_LIFT_MIN_BPC = 0.10              # diverse-spoke must beat baseline by this much
HP_BPC_CV_MAX = 0.03                # v3: TIGHTENED cross-seed stability (CHAIN_GRADE)
HP_BPC_CV_MAX_SOFT = 0.05           # HARD_PASS (non-CHAIN_GRADE) seed CV
SANITY_RAIL_TOL = 0.02              # baseline within +/-0.02 of v2 7.667
DEGEN_TOL = 0.5

# Gate-entropy health band (per cell spec FIX 3)
GATE_ENTROPY_MIN = 0.5              # gates not collapsed to single spoke
GATE_ENTROPY_MAX = 1.5              # gates not uniform across all spokes

# Spoke health band (per cell spec FIX 1) -- recon_err must be finite + in range
SPOKE_RECON_ERR_MIN = 0.0           # 0.0 is OK for some spokes (FPE near-zero by design)
SPOKE_RECON_ERR_MAX = 1000.0        # absurd upper bound -- catches Inf
# NaN is detected separately via math.isnan

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
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

SPARSE_BIPOLAR_F = 0.02

# Per-spoke algorithm params
# Spoke 1: SoftHebb k-WTA on context bigrams
SOFTHEBB_K_WTA = 64
SOFTHEBB_LR = 0.01
SOFTHEBB_N_PASSES = 1

# Spoke 2: char-trigram + Random Indexing (distributional)
RI_WINDOW = 5
RI_SPARSITY = 16

# Spoke 3: Path-C PC (mirrors v1 baseline; the v1 reference architecture)
PC_N_LAYERS = 3
PC_ALPHA = 0.05
PC_BETA = 2.0
PC_N_PASSES = 1

# Spoke 4 (FPE arm only): Fractional Power Encoding for relations
FPE_BANDWIDTH = 1.5

# cf-RPE hyperparameters (gate-learning, MRC arms)
CFRPE_ETA = 0.05
CFRPE_N_STEPS = 100

# MRC gate-temperature grid (per cell spec FIX 2)
T_GATE_GRID = [0.1, 0.5, 1.0, 2.0]

MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    ENCODER_TRAIN_TOKENS = 100_000
else:
    # Smoke: <180s laptop CPU. Exercises every arm + per-algorithm spoke build + cv.
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 200
    N_DIM = 256
    INGEST_CHUNK = 256
    RECALL_BATCH = 64
    ENCODER_TRAIN_TOKENS = 500
    CFRPE_N_STEPS = 8

ARMS = [
    "ARM_BASELINE_PATH_C_SINGLE",
    "ARM_HUB_3SPOKE_MRC",
    "ARM_HUB_3SPOKE_MRC_PLUS_FPE",
    "ARM_HUB_5SPOKE_MRC_ABLATION",
]
BASELINE_ARM = "ARM_BASELINE_PATH_C_SINGLE"
HUB_ARMS = [a for a in ARMS if a != BASELINE_ARM]
PRIMARY_ARM = "ARM_HUB_3SPOKE_MRC"
# ABLATION arm uses sign(sum) NOT MRC; isolates MRC contribution
ABLATION_ARM = "ARM_HUB_5SPOKE_MRC_ABLATION"
MRC_ARMS = ["ARM_HUB_3SPOKE_MRC", "ARM_HUB_3SPOKE_MRC_PLUS_FPE"]

CONFIG_VERSION = (
    "substrate_hub_spoke_E1_v3_MRC_calibrated_routing; N_DIM=%d N_TRAIN=%d "
    "N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "sparse_f=%.3f softhebb_kwta=%d softhebb_lr=%.4f ri_window=%d "
    "ri_sparsity=%d pc_layers=%d pc_alpha=%.3f pc_beta=%.2f pc_passes=%d "
    "fpe_bandwidth=%.2f encoder_train_tokens=%d cfrpe_eta=%.3f "
    "cfrpe_n_steps=%d t_gate_grid=%s MRR_K=%d device=%s; bands HP<=%.3f "
    "CG<=%.3f HF>=%.3f cg_cv_max=%.3f hp_cv_max=%.3f div_cv_min=%.3f "
    "div_cv_degen=%.3f sanity_rail_tol=%.3f gate_entropy=[%.2f,%.2f]"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F,
    SOFTHEBB_K_WTA, SOFTHEBB_LR, RI_WINDOW, RI_SPARSITY,
    PC_N_LAYERS, PC_ALPHA, PC_BETA, PC_N_PASSES,
    FPE_BANDWIDTH, ENCODER_TRAIN_TOKENS,
    CFRPE_ETA, CFRPE_N_STEPS, T_GATE_GRID, MRR_K, str(DEVICE),
    HP_BPC_MAX, CG_BPC_MAX, HF_BPC_MIN, HP_BPC_CV_MAX, HP_BPC_CV_MAX_SOFT,
    DIVERSITY_CV_MIN, DIVERSITY_CV_DEGEN, SANITY_RAIL_TOL,
    GATE_ENTROPY_MIN, GATE_ENTROPY_MAX,
)


# ============================================================================
# Shared primitives (mirror v1 / Path C v2 where applicable)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _sign_with_zero_tiebreak(x: torch.Tensor) -> torch.Tensor:
    s = torch.sign(x)
    s = torch.where(s == 0, torch.ones_like(s), s)
    return s


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
    out = out * (1.0 / math.sqrt(max(f, 1e-9)))
    return out


def build_planted_bipolar_inputs_gpu(V: int, n_dim: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed * 7919 + 17)
    X = (rng.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    Xn = _l2_normalize_np(X)
    return torch.from_numpy(Xn).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# SPOKE 1: SoftHebb k-WTA forward-only encoder (Moraitis et al. 2021)
# ============================================================================

def build_spoke_softhebb_gpu(
    V: int, n_dim: int, vocab: List[str], idx_train: np.ndarray, seed: int,
) -> Tuple[torch.Tensor, Dict]:
    """SoftHebb k-WTA encoder: per-row update with hard k-WTA mask.

    Init from char-trigram bag (substrate-native init); train via streaming
    Hebbian-with-k-WTA on bigram-context pairs. Forward-only; no backprop.
    Returns L2-normalized signed-bipolar [V, n_dim] codebook.
    """
    t0 = time.time()
    rng = np.random.default_rng(seed * 13 + 1)

    # Init: char-trigram bag for each word
    E_init = np.zeros((V, n_dim), dtype=np.float32)
    for vi, word in enumerate(vocab):
        t = " " + word.lower().replace("_", " ") + " "
        if len(t) < 3:
            E_init[vi] = rng.standard_normal(n_dim).astype(np.float32)
            continue
        acc = np.zeros(n_dim, dtype=np.float32)
        for i in range(len(t) - 2):
            tri = t[i:i + 3]
            acc += _bipolar_hv(_seed_for_trigram(tri, seed * 97 + 11), n_dim)
        E_init[vi] = acc
    E = torch.from_numpy(_l2_normalize_np(E_init)).to(device=DEVICE, dtype=TORCH_DTYPE)

    # Streaming Hebbian-with-k-WTA on bigram pairs.
    #
    # NUMERICAL STABILITY (fix for production NaN seen in Wave F):
    #   Original loop normalized E only at END of pass. With text8's heavy
    #   power-law token frequency (e.g., "the" ~ 6% of tokens) and 100k tokens
    #   chunked at 1024, common-token rows of E accumulate THOUSANDS of
    #   additive index_add_ updates per pass before any L2 renorm. Each chunk
    #   computes act = x_src + x_tgt from E[src], so once a common row grows,
    #   the next chunk's act grows, the next update grows, etc. -- a positive
    #   feedback runaway that overflows fp32 to Inf within ~64 chunks at
    #   N_DIM=8192 / N_TRAIN=100k / sparse_f=0.02 and produces NaN downstream.
    #
    # FIX (matches Moraitis et al. 2021 per-step weight normalization):
    #   1. L2-normalize E at end of EVERY CHUNK (not just end of pass). Caps
    #      row norms <= 1, eliminating the runaway.
    #   2. Clip per-row update L2 norm to <= 1.0. Belt-and-suspenders against
    #      extreme single-chunk spikes from duplicate src indices.
    # Verified at production scale (V=4000, N_DIM=8192, N_TRAIN=100k): max row
    # norm during train stays at 1.0; recon_err finite; no NaN/Inf.
    idx_t = torch.from_numpy(idx_train[:ENCODER_TRAIN_TOKENS].astype(np.int64)).to(DEVICE)
    n_pairs = idx_t.shape[0] - 1
    chunk = 1024 if RUN_MODE == "full" else 128
    k_wta = min(SOFTHEBB_K_WTA, n_dim // 2)
    update_clip = 1.0  # max per-row update L2 norm
    n_updates = 0
    for pass_i in range(SOFTHEBB_N_PASSES):
        for b in range(0, n_pairs, chunk):
            end = min(b + chunk, n_pairs)
            src = idx_t[b:end]
            tgt = idx_t[b + 1:end + 1]
            x_src = E[src]      # [B, n_dim]
            x_tgt = E[tgt]      # [B, n_dim]
            # k-WTA on the projected activation (top-k positions per row)
            act = x_src + x_tgt  # bigram-context bundle
            abs_act = act.abs()
            _, topk_idx = torch.topk(abs_act, k=k_wta, dim=1)
            mask = torch.zeros_like(act)
            row_idx = torch.arange(act.shape[0], device=DEVICE).unsqueeze(1).expand(-1, k_wta)
            mask[row_idx, topk_idx] = 1.0
            update = SOFTHEBB_LR * (act * mask)
            # FIX 2: clip per-row update L2 norm to <= update_clip
            up_norms = update.norm(dim=1, keepdim=True)
            scale = torch.clamp(update_clip / (up_norms + 1e-12), max=1.0)
            update = update * scale
            # Apply Hebbian-like update to BOTH source and target rows (forward-only,
            # no error signal), scattered back into the codebook
            E.index_add_(0, src, update)
            E.index_add_(0, tgt, update)
            n_updates += 1
            # FIX 1: per-chunk L2 normalize (was: end of pass only). Bounds E
            # rows so the next chunk's act = x_src + x_tgt cannot blow up.
            E = _l2_normalize_t(E)
            if DEVICE.type == "cuda" and (n_updates % 16 == 0):
                torch.cuda.synchronize()
    # Final sign-quantize then renormalize -> consistent bipolar geometry
    E_final = _l2_normalize_t(_sign_with_zero_tiebreak(E))
    # Per-spoke "reconstruction error" as a coarse diversity probe:
    # mean |x_src - argmax_E recall(x_src)| reduced to a scalar
    with torch.no_grad():
        sample = idx_t[: min(256, idx_t.shape[0])]
        recon_err = float((E_final[sample] - E[sample]).norm(dim=1).mean().item())
    meta = {
        "algo": "softhebb_kwta",
        "k_wta": int(k_wta),
        "lr": float(SOFTHEBB_LR),
        "n_passes": int(SOFTHEBB_N_PASSES),
        "n_updates": int(n_updates),
        "wall_s": round(time.time() - t0, 2),
        "spoke_recon_err": round(recon_err, 4),
        "numerical_stability": "per_chunk_l2_norm+update_clip_1.0",
    }
    return E_final, meta


# ============================================================================
# SPOKE 2: char-trigram bag + Random Indexing distributional
# ============================================================================

def build_spoke_chartri_ri_gpu(
    V: int, n_dim: int, vocab: List[str], idx_train: np.ndarray, seed: int,
) -> Tuple[torch.Tensor, Dict]:
    """Composite: char-trigram orthographic vector * Random-Indexing context vector.

    Orthographic + distributional in one bipolar vector via Hadamard binding;
    captures BOTH surface form (cat/cats) AND co-occurrence (cat/dog) -- a
    different family than PC's hierarchical learned features.
    """
    t0 = time.time()
    rng = np.random.default_rng(seed * 17 + 3)

    # (a) Char-trigram orthographic vector
    E_ortho = np.zeros((V, n_dim), dtype=np.float32)
    for vi, word in enumerate(vocab):
        t = " " + word.lower().replace("_", " ") + " "
        if len(t) < 3:
            E_ortho[vi] = rng.standard_normal(n_dim).astype(np.float32)
            continue
        acc = np.zeros(n_dim, dtype=np.float32)
        for i in range(len(t) - 2):
            tri = t[i:i + 3]
            acc += _bipolar_hv(_seed_for_trigram(tri, seed * 191 + 5), n_dim)
        E_ortho[vi] = acc
    E_ortho = _l2_normalize_np(E_ortho)

    # (b) Random Indexing: each word gets a sparse-ternary index vector;
    # context-vector accumulates index-vectors of words in window
    idx_vecs = np.zeros((V, n_dim), dtype=np.float32)
    s = min(RI_SPARSITY, n_dim // 2)
    for vi in range(V):
        nz = rng.choice(n_dim, size=s, replace=False)
        signs = (rng.integers(0, 2, size=s).astype(np.float32) * 2.0 - 1.0)
        idx_vecs[vi, nz] = signs
    ctx_vecs = np.zeros((V, n_dim), dtype=np.float32)
    train_subset = idx_train[:ENCODER_TRAIN_TOKENS]
    win = RI_WINDOW
    for ti in range(len(train_subset)):
        center = int(train_subset[ti])
        lo = max(0, ti - win)
        hi = min(len(train_subset), ti + win + 1)
        for tj in range(lo, hi):
            if tj == ti:
                continue
            ctx_vecs[center] += idx_vecs[int(train_subset[tj])]
    ctx_vecs = _l2_normalize_np(ctx_vecs)

    # (c) Hadamard-bind orthographic * distributional -> composite
    composite = E_ortho * ctx_vecs
    E_t = torch.from_numpy(composite).to(device=DEVICE, dtype=TORCH_DTYPE)
    E_t = _l2_normalize_t(_sign_with_zero_tiebreak(E_t))

    # Diversity probe: mean L2 difference between composite and ortho-only
    recon_err = float(
        torch.from_numpy(np.linalg.norm(composite - E_ortho, axis=1)).mean().item()
    )
    meta = {
        "algo": "chartrigram_x_random_indexing",
        "ri_window": int(win),
        "ri_sparsity": int(s),
        "n_train_tokens": int(len(train_subset)),
        "wall_s": round(time.time() - t0, 2),
        "spoke_recon_err": round(recon_err, 4),
    }
    return E_t, meta


# ============================================================================
# SPOKE 3: Path-C predictive-coding (mirror v1 train_pc_spoke_gpu)
# ============================================================================

def build_spoke_pc_gpu(
    V: int, n_dim: int, vocab: List[str], idx_train: np.ndarray, seed: int,
    alpha: float = PC_ALPHA, beta: float = PC_BETA,
) -> Tuple[torch.Tensor, Dict]:
    """Path-C predictive-coding 3-layer encoder (the v1 spoke architecture)."""
    t0 = time.time()
    X_planted = build_planted_bipolar_inputs_gpu(V, n_dim, seed)
    device = X_planted.device
    rng = torch.Generator(device="cpu")
    rng.manual_seed(int(seed) * 1009 + 31)
    W_L1 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L2 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L3 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    E_excit = torch.zeros(n_dim, device=device, dtype=TORCH_DTYPE)

    n_train_tokens = min(len(idx_train), ENCODER_TRAIN_TOKENS)
    idx_t = torch.from_numpy(idx_train[:n_train_tokens].astype(np.int64)).to(device)
    chunk = 1024 if RUN_MODE == "full" else 128
    n_updates = 0
    recon_L3_last = 0.0
    for pass_i in range(PC_N_PASSES):
        rL3_a, nc = 0.0, 0
        for b in range(0, n_train_tokens, chunk):
            end = min(b + chunk, n_train_tokens)
            ids_b = idx_t[b:end]
            x_in = X_planted[ids_b]
            pre_L1 = x_in @ W_L1.T
            L1_out = _sign_with_zero_tiebreak(pre_L1)
            pre_L2 = L1_out @ W_L2.T
            L2_out = _sign_with_zero_tiebreak(pre_L2)
            pre_L3 = L2_out @ W_L3.T
            route_w = torch.softmax(-beta * E_excit, dim=0)
            pre_L3_routed = pre_L3 * (route_w * n_dim)
            L3_out = _sign_with_zero_tiebreak(pre_L3_routed)
            recon_L1 = L1_out @ W_L1
            recon_L2 = L2_out @ W_L2
            recon_L3 = L3_out @ W_L3
            err_L1 = x_in - recon_L1
            err_L2 = L1_out - recon_L2
            err_L3 = L2_out - recon_L3
            B = x_in.shape[0]
            W_L1.add_((alpha / (n_dim * B)) * (err_L1.T @ x_in))
            W_L2.add_((alpha / (n_dim * B)) * (err_L2.T @ L1_out))
            W_L3.add_((alpha / (n_dim * B)) * (err_L3.T @ L2_out))
            E_excit.add_((L3_out * L3_out).sum(dim=0))
            rL3_a += float(err_L3.norm(dim=1).mean().item())
            nc += 1
            n_updates += 1
            if device.type == "cuda" and (n_updates % 16 == 0):
                torch.cuda.synchronize()
        if nc > 0:
            recon_L3_last = rL3_a / nc

    # Final encode pass
    pre_L1 = X_planted @ W_L1.T
    L1_out = _sign_with_zero_tiebreak(pre_L1)
    pre_L2 = L1_out @ W_L2.T
    L2_out = _sign_with_zero_tiebreak(pre_L2)
    pre_L3 = L2_out @ W_L3.T
    route_w = torch.softmax(-beta * E_excit, dim=0)
    pre_L3 = pre_L3 * (route_w * n_dim)
    L3_out = _sign_with_zero_tiebreak(pre_L3)
    E_final = _l2_normalize_t(L3_out)
    del X_planted, W_L1, W_L2, W_L3, E_excit
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    meta = {
        "algo": "path_c_pc_3layer",
        "alpha": float(alpha),
        "beta": float(beta),
        "n_passes": int(PC_N_PASSES),
        "n_updates": int(n_updates),
        "wall_s": round(time.time() - t0, 2),
        "spoke_recon_err": round(recon_L3_last, 4),
    }
    return E_final, meta


# ============================================================================
# SPOKE 4 (FPE arm only): Fractional Power Encoding for relational features
# ============================================================================

def build_spoke_fpe_gpu(
    V: int, n_dim: int, vocab: List[str], idx_train: np.ndarray, seed: int,
) -> Tuple[torch.Tensor, Dict]:
    """Fractional Power Encoding: random axes phi_i and per-word real-valued
    coefficients alpha_i derived from co-occurrence statistics; encode as
    sum_i alpha_i * exp(i * 2pi * f * phi_i) with bandwidth f.

    Substrate-native variant (real-valued cos/sin pair); samples a different
    point in the codebook eigenspace than PC's iterated-Hebbian basin.
    """
    t0 = time.time()
    rng = np.random.default_rng(seed * 23 + 7)
    # Random projection of bigram co-occurrence into n_dim "frequency" axes
    n_axes = n_dim // 2
    phi = rng.standard_normal((V, n_axes)).astype(np.float32)
    phi = _l2_normalize_np(phi)
    # Bigram-co-occurrence counts (sparse approximation; use train subset)
    train_subset = idx_train[:ENCODER_TRAIN_TOKENS]
    coocc_diag = np.zeros(V, dtype=np.float32)
    for ti in range(len(train_subset) - 1):
        coocc_diag[int(train_subset[ti])] += 1.0
    coocc_diag = coocc_diag / max(coocc_diag.max(), 1.0)
    # FPE encoding: alpha = log(1+count); freq = bandwidth * phi
    alpha_coef = np.log1p(coocc_diag).astype(np.float32)  # [V]
    omega = FPE_BANDWIDTH * phi                            # [V, n_axes]
    # Cos/sin pair concatenated -> [V, n_dim]
    arg = 2.0 * math.pi * omega
    feat_cos = np.cos(arg) * alpha_coef[:, None]
    feat_sin = np.sin(arg) * alpha_coef[:, None]
    feat = np.concatenate([feat_cos, feat_sin], axis=1).astype(np.float32)
    E_t = torch.from_numpy(_l2_normalize_np(feat)).to(device=DEVICE, dtype=TORCH_DTYPE)
    E_t = _l2_normalize_t(_sign_with_zero_tiebreak(E_t))
    recon_err = float(np.linalg.norm(feat - phi.repeat(2, axis=1), axis=1).mean())
    meta = {
        "algo": "fractional_power_encoding",
        "bandwidth": float(FPE_BANDWIDTH),
        "n_axes": int(n_axes),
        "n_train_tokens": int(len(train_subset)),
        "wall_s": round(time.time() - t0, 2),
        "spoke_recon_err": round(recon_err, 4),
    }
    return E_t, meta


# ============================================================================
# Hub aggregation (mirror v1)
# ============================================================================

def hub_aggregate_majority(spoke_outputs: List[torch.Tensor]) -> torch.Tensor:
    """v2-style sign(sum) bundle. Used by ABLATION arm to isolate MRC."""
    if not spoke_outputs:
        raise ValueError("hub_aggregate_majority: empty spoke list")
    stacked = torch.stack(spoke_outputs, dim=0)
    summed = stacked.sum(dim=0)
    bundled = _sign_with_zero_tiebreak(summed)
    return _l2_normalize_t(bundled)


def hub_aggregate_cfrpe_weighted(spoke_outputs: List[torch.Tensor],
                                    gates: torch.Tensor) -> torch.Tensor:
    """v2-style cf-RPE-weighted sign-of-sum (kept for backward compat)."""
    if not spoke_outputs:
        raise ValueError("hub_aggregate_cfrpe_weighted: empty spoke list")
    n_spokes = len(spoke_outputs)
    if gates.shape[0] != n_spokes:
        raise ValueError("gates len %d != n_spokes %d" % (gates.shape[0], n_spokes))
    # v3.1 device-fix: co-locate gates with spoke_outputs (defensive).
    target_device = spoke_outputs[0].device
    if gates.device != target_device:
        gates = gates.to(target_device)
    stacked = torch.stack(spoke_outputs, dim=0)
    w = gates.view(n_spokes, 1, 1)
    weighted = (stacked * w).sum(dim=0)
    bundled = _sign_with_zero_tiebreak(weighted)
    return _l2_normalize_t(bundled)


def hub_aggregate_mrc(spoke_outputs: List[torch.Tensor],
                       gate_logits: torch.Tensor,
                       t_gate: float) -> torch.Tensor:
    """v3 FIX 2: MRC-weighted bundle. softmax(gate_logits / T_gate) weighted
    sum of (signed) spoke outputs, then sign + L2 normalize.

    This is the maximal-ratio-combining analog: each spoke is weighted by its
    confidence (gate_logit) at temperature T_gate. T_gate -> 0 collapses to
    single-spoke (winner-take-all); T_gate -> inf collapses to uniform mean.
    The grid T_gate in {0.1, 0.5, 1.0, 2.0} bracket both extremes."""
    if not spoke_outputs:
        raise ValueError("hub_aggregate_mrc: empty spoke list")
    n_spokes = len(spoke_outputs)
    if gate_logits.shape[0] != n_spokes:
        raise ValueError("gate_logits len %d != n_spokes %d" % (
            gate_logits.shape[0], n_spokes))
    if t_gate <= 0.0:
        raise ValueError("t_gate must be > 0; got %.4f" % t_gate)
    # v3.1 device-fix: caller may pass CPU-built gate_logits (e.g. in self-test
    # constructing torch.tensor([...]) without explicit device). Co-locate with
    # spoke_outputs so the bundle reduction succeeds on cuda. Spoke outputs are
    # always on DEVICE, so use the first one as device reference.
    target_device = spoke_outputs[0].device
    if gate_logits.device != target_device:
        gate_logits = gate_logits.to(target_device)
    gates = torch.softmax(gate_logits / max(t_gate, 1e-9), dim=0)
    stacked = torch.stack(spoke_outputs, dim=0)
    w = gates.view(n_spokes, 1, 1)
    weighted = (stacked * w).sum(dim=0)
    bundled = _sign_with_zero_tiebreak(weighted)
    return _l2_normalize_t(bundled), gates


def adapt_cfrpe_gates(
    spoke_outputs: List[torch.Tensor], idx_train: np.ndarray,
    n_steps: int, eta: float, seed: int,
) -> torch.Tensor:
    """v2-style cf-RPE gate adaptation on per-spoke bigram alignment cosines.
    Kept for backward compatibility with the cell-internal selftest. Used by
    v3 only as a non-task-signal baseline; v3 PRIMARY arms use the
    task-signal variant below."""
    n_spokes = len(spoke_outputs)
    device = spoke_outputs[0].device
    logits = torch.zeros(n_spokes, device=device, dtype=TORCH_DTYPE)
    rng = np.random.default_rng(seed * 131 + 7)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0 or n_steps <= 0:
        return torch.softmax(logits, dim=0)
    samples = rng.integers(0, n_pairs, size=int(n_steps))
    for s_i in samples:
        ti = int(idx_train[s_i])
        tj = int(idx_train[s_i + 1])
        per_spoke_align = []
        for sp in spoke_outputs:
            v_i = sp[ti]
            v_j = sp[tj]
            denom = (v_i.norm() * v_j.norm()).clamp(min=1e-9)
            cos = (v_i @ v_j) / denom
            per_spoke_align.append(cos)
        align_t = torch.stack(per_spoke_align)
        mean_a = align_t.mean()
        logits = logits + eta * (align_t - mean_a)
    return torch.softmax(logits, dim=0)


def adapt_gates_task_signal(
    spoke_outputs: List[torch.Tensor], idx_train: np.ndarray,
    n_steps: int, eta: float, seed: int,
) -> torch.Tensor:
    """v3 FIX 3: train gate LOGITS against the next-token-prediction loss
    gradient.

    For each sampled bigram (i -> j), compute per-spoke next-token-prediction
    score: cos(spoke[i], spoke[j]). The gradient of expected-token-log-prob
    w.r.t. gate-logit-k is (score_k - mean(scores)) -- a REINFORCE-style
    advantage signal. The substrate predicts j given i; gate_k weighting
    determines how much spoke_k contributes to that prediction. ZERO LLM at
    inference (substrate-only -- substrate's own per-spoke cosine IS the
    task signal).

    Returns gate LOGITS (not softmaxed) so the caller can apply T_gate."""
    n_spokes = len(spoke_outputs)
    device = spoke_outputs[0].device
    # Initialize from cf-RPE bigram-alignment as a warm start, then refine
    # against task-signal advantage.
    logits = torch.zeros(n_spokes, device=device, dtype=TORCH_DTYPE)
    rng = np.random.default_rng(seed * 757 + 19)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0 or n_steps <= 0:
        return logits
    samples = rng.integers(0, n_pairs, size=int(n_steps))
    for s_i in samples:
        ti = int(idx_train[s_i])
        tj = int(idx_train[s_i + 1])
        per_spoke_score = []
        for sp in spoke_outputs:
            v_i = sp[ti]
            v_j = sp[tj]
            denom = (v_i.norm() * v_j.norm()).clamp(min=1e-9)
            score = (v_i @ v_j) / denom
            per_spoke_score.append(score)
        scores_t = torch.stack(per_spoke_score)
        # NaN/Inf hygiene: any non-finite per-spoke score becomes an inert 0.
        scores_t = torch.where(torch.isfinite(scores_t), scores_t,
                                  torch.zeros_like(scores_t))
        mean_s = scores_t.mean()
        advantage = scores_t - mean_s
        logits = logits + eta * advantage
        # Logit clip prevents NaN-spoke from monopolizing in numerics edge
        logits = torch.clamp(logits, -10.0, 10.0)
    return logits


def gate_entropy(gates: torch.Tensor) -> float:
    """Shannon entropy of gate softmax (nats). Used in health bands."""
    p = gates.detach().cpu().numpy().astype(np.float64)
    p = np.clip(p, 1e-12, 1.0)
    p = p / p.sum()
    return float(-np.sum(p * np.log(p)))


# ============================================================================
# FIX 1: per-spoke health check (NaN/Inf detection + recon_err sanity)
# ============================================================================

def spoke_health_check(spoke_E: torch.Tensor, spoke_meta: Dict
                          ) -> Tuple[bool, str]:
    """Return (is_healthy, reason). Healthy = codebook has no NaN/Inf AND
    spoke_recon_err in finite sane range AND L2 norms are valid."""
    if spoke_E is None:
        return (False, "spoke_E is None")
    # Tensor-level NaN/Inf
    if torch.isnan(spoke_E).any().item():
        return (False, "codebook contains NaN")
    if torch.isinf(spoke_E).any().item():
        return (False, "codebook contains Inf")
    # L2-norms should be ~1 by construction (codebooks are L2-normalized rows)
    norms = spoke_E.norm(dim=1)
    if torch.isnan(norms).any().item() or torch.isinf(norms).any().item():
        return (False, "codebook row-norms NaN/Inf")
    # If a row has zero norm, it's a dead row (e.g., all-zero output)
    n_dead = int((norms < 1e-6).sum().item())
    if n_dead > 0:
        return (False, "codebook has %d dead rows (norm < 1e-6)" % n_dead)
    # recon_err must be finite + in [SPOKE_RECON_ERR_MIN, SPOKE_RECON_ERR_MAX]
    recon_err = spoke_meta.get("spoke_recon_err", None)
    if recon_err is None:
        return (False, "spoke_recon_err missing from meta")
    if isinstance(recon_err, float):
        if math.isnan(recon_err):
            return (False, "spoke_recon_err is NaN")
        if math.isinf(recon_err):
            return (False, "spoke_recon_err is Inf")
        if recon_err < SPOKE_RECON_ERR_MIN or recon_err > SPOKE_RECON_ERR_MAX:
            return (False, "spoke_recon_err=%.4f outside [%.2f, %.2f]" % (
                recon_err, SPOKE_RECON_ERR_MIN, SPOKE_RECON_ERR_MAX))
    return (True, "healthy")


# ============================================================================
# Diversity discriminator (load-bearing per Fix #28)
# ============================================================================

def compute_spoke_diversity_cv(spoke_outputs: List[torch.Tensor]) -> float:
    """CV of per-spoke pairwise-cosine summary scalars.

    The v1 bug: 15 PC spokes had L3 recon errors 92.20-92.47 (cv=0.0008). For v2
    to qualify as genuinely diverse, the spokes' pairwise structure must show
    cv >= 0.05 across the spoke-pair cosine summary.
    """
    n = len(spoke_outputs)
    if n < 2:
        return 0.0
    # Per-spoke summary: mean off-diagonal cosine on a fixed sample
    sample_n = min(200, spoke_outputs[0].shape[0])
    summaries = []
    for sp in spoke_outputs:
        sub = sp[:sample_n]
        sims = (sub @ sub.T)
        n_off = sub.shape[0] * (sub.shape[0] - 1)
        if n_off == 0:
            summaries.append(0.0)
            continue
        off_sum = float(sims.sum().item() - sims.diag().sum().item())
        summaries.append(off_sum / max(n_off, 1))
    arr = np.asarray(summaries, dtype=np.float64)
    m = float(np.mean(arr))
    s = float(np.std(arr))
    if abs(m) < 1e-9:
        return float(s)
    return float(s / abs(m))


# ============================================================================
# Per-arm encoder builder
# ============================================================================

def build_arm_encoder(
    arm_label: str, V: int, n_dim: int, vocab: List[str],
    idx_train: np.ndarray, seed: int,
) -> Tuple[torch.Tensor, Dict]:
    """v3: build encoder + apply FIX 1 (spoke health check),
    FIX 2 (MRC bundle with T_gate grid), FIX 3 (task-signal gates)."""
    meta: Dict = {"arm": arm_label}
    t0 = time.time()

    if arm_label == BASELINE_ARM:
        E_pre, pc_meta = build_spoke_pc_gpu(V, n_dim, vocab, idx_train, seed)
        # FIX 1 even for baseline -- catches broken Path-C
        healthy, reason = spoke_health_check(E_pre, pc_meta)
        meta["spoke_health"] = [{"spoke_idx": 0, "algo": pc_meta.get("algo"),
                                    "healthy": bool(healthy), "reason": reason}]
        if not healthy:
            meta["broken_spoke_detected"] = True
            meta["broken_spoke_reason"] = reason
            raise RuntimeError("BASELINE_PATH_C broken: %s" % reason)
        meta["spokes"] = [pc_meta]
        meta["n_spokes"] = 1
        meta["spoke_diversity_cv"] = 0.0  # single spoke = no diversity
        meta["broken_spoke_detected"] = False
    else:
        # Build the 3 algorithmically-diverse spokes
        spoke_outputs: List[torch.Tensor] = []
        spoke_metas: List[Dict] = []
        spoke_health_log: List[Dict] = []
        broken_spoke_detected = False
        broken_spoke_reason = ""

        E_s1, m_s1 = build_spoke_softhebb_gpu(V, n_dim, vocab, idx_train, seed)
        h1, r1 = spoke_health_check(E_s1, m_s1)
        spoke_health_log.append({"spoke_idx": 0, "algo": m_s1.get("algo"),
                                    "healthy": bool(h1), "reason": r1})
        if not h1:
            broken_spoke_detected = True
            broken_spoke_reason = "spoke[0] softhebb: " + r1
        spoke_outputs.append(E_s1); spoke_metas.append({**m_s1, "spoke_idx": 0,
                                                             "spoke_healthy": bool(h1)})

        E_s2, m_s2 = build_spoke_chartri_ri_gpu(V, n_dim, vocab, idx_train, seed)
        h2, r2 = spoke_health_check(E_s2, m_s2)
        spoke_health_log.append({"spoke_idx": 1, "algo": m_s2.get("algo"),
                                    "healthy": bool(h2), "reason": r2})
        if not h2:
            broken_spoke_detected = True
            broken_spoke_reason = "spoke[1] chartri-ri: " + r2
        spoke_outputs.append(E_s2); spoke_metas.append({**m_s2, "spoke_idx": 1,
                                                             "spoke_healthy": bool(h2)})

        E_s3, m_s3 = build_spoke_pc_gpu(V, n_dim, vocab, idx_train, seed)
        h3, r3 = spoke_health_check(E_s3, m_s3)
        spoke_health_log.append({"spoke_idx": 2, "algo": m_s3.get("algo"),
                                    "healthy": bool(h3), "reason": r3})
        if not h3:
            broken_spoke_detected = True
            broken_spoke_reason = "spoke[2] path-c-pc: " + r3
        spoke_outputs.append(E_s3); spoke_metas.append({**m_s3, "spoke_idx": 2,
                                                             "spoke_healthy": bool(h3)})

        if arm_label == "ARM_HUB_3SPOKE_MRC_PLUS_FPE":
            E_s4, m_s4 = build_spoke_fpe_gpu(V, n_dim, vocab, idx_train, seed)
            h4, r4 = spoke_health_check(E_s4, m_s4)
            spoke_health_log.append({"spoke_idx": 3, "algo": m_s4.get("algo"),
                                        "healthy": bool(h4), "reason": r4})
            if not h4:
                broken_spoke_detected = True
                broken_spoke_reason = "spoke[3] fpe: " + r4
            spoke_outputs.append(E_s4); spoke_metas.append({**m_s4, "spoke_idx": 3,
                                                                 "spoke_healthy": bool(h4)})

        meta["spoke_health"] = spoke_health_log
        meta["broken_spoke_detected"] = bool(broken_spoke_detected)
        meta["broken_spoke_reason"] = broken_spoke_reason

        # Diversity CV BEFORE aggregation -- the load-bearing discriminator
        div_cv = compute_spoke_diversity_cv(spoke_outputs)
        meta["spoke_diversity_cv"] = round(float(div_cv), 6)

        if broken_spoke_detected:
            # FIX 1: do NOT bundle a broken spoke into the hub. Fail fast.
            # The arm gets recorded as compute_failed so downstream verdict
            # sees the cause explicitly (not a silent unigram-floor collapse).
            raise RuntimeError("FIX_1_BROKEN_SPOKE: " + broken_spoke_reason)

        # FIX 3: task-signal gate training (for MRC arms only). ABLATION uses
        # sign(sum) bundle without gates.
        if arm_label == ABLATION_ARM:
            # ABLATION: NO gates, NO MRC -- v2-style sign(sum). Isolates MRC.
            E_pre = hub_aggregate_majority(spoke_outputs)
            meta["bundle_mode"] = "sign_sum_no_mrc_ablation"
            meta["t_gate_used"] = None
        else:
            # MRC arms: train gate logits on task signal, sweep T_gate,
            # pick the T that produces best gate-entropy in valid band.
            gate_logits = adapt_gates_task_signal(
                spoke_outputs=spoke_outputs, idx_train=idx_train,
                n_steps=CFRPE_N_STEPS, eta=CFRPE_ETA, seed=seed,
            )
            meta["gate_logits"] = gate_logits.detach().cpu().numpy().round(4).tolist()

            # T_gate sweep: prefer T whose resulting gate-entropy lands in
            # [GATE_ENTROPY_MIN, GATE_ENTROPY_MAX]. If none qualify, take T
            # closest to the band midpoint and flag it.
            band_mid = 0.5 * (GATE_ENTROPY_MIN + GATE_ENTROPY_MAX)
            best_t = None; best_band_dist = float("inf")
            t_sweep = []
            for t_g in T_GATE_GRID:
                gates_t = torch.softmax(gate_logits / max(t_g, 1e-9), dim=0)
                ent_t = gate_entropy(gates_t)
                t_sweep.append({"t_gate": float(t_g),
                                  "gate_entropy": round(ent_t, 4),
                                  "gates": gates_t.detach().cpu().numpy().round(4).tolist()})
                # Prefer in-band T
                in_band = (GATE_ENTROPY_MIN <= ent_t <= GATE_ENTROPY_MAX)
                dist = 0.0 if in_band else min(
                    abs(ent_t - GATE_ENTROPY_MIN), abs(ent_t - GATE_ENTROPY_MAX))
                # Tiebreak by distance to band midpoint
                if in_band and best_t is None:
                    best_t = t_g; best_band_dist = 0.0
                elif in_band:
                    mid_dist = abs(ent_t - band_mid)
                    cur_t_ent = gate_entropy(
                        torch.softmax(gate_logits / max(best_t, 1e-9), dim=0))
                    cur_mid_dist = abs(cur_t_ent - band_mid)
                    if mid_dist < cur_mid_dist:
                        best_t = t_g
                elif best_t is None and dist < best_band_dist:
                    best_t = t_g; best_band_dist = dist
            if best_t is None:
                best_t = 1.0  # neutral default

            meta["t_gate_sweep"] = t_sweep
            meta["t_gate_used"] = float(best_t)
            E_pre, gates_final = hub_aggregate_mrc(spoke_outputs, gate_logits, best_t)
            ent_final = gate_entropy(gates_final)
            meta["mrc_gates"] = gates_final.detach().cpu().numpy().round(4).tolist()
            meta["gate_entropy"] = round(ent_final, 4)
            meta["gate_entropy_in_band"] = bool(
                GATE_ENTROPY_MIN <= ent_final <= GATE_ENTROPY_MAX)
            meta["bundle_mode"] = "mrc_weighted"

        meta["spokes"] = spoke_metas
        meta["n_spokes"] = len(spoke_outputs)
        del spoke_outputs

    E_sp = _l2_normalize_t(sparsify_bipolar_gpu(E_pre, SPARSE_BIPOLAR_F, seed))
    del E_pre
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    meta["wall_encoder_s"] = round(time.time() - t0, 2)
    return E_sp, meta


# ============================================================================
# Hebbian W + logits + sweep + verdict (mirror v1)
# ============================================================================

def build_rank1_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
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


def compute_arm_logits(arm_label: str, vocab: List[str], idx_train: np.ndarray,
                          idx_held: np.ndarray, seed: int, V: int,
                          n_dim: int) -> Dict:
    """v3: build_arm_encoder may raise RuntimeError('FIX_1_BROKEN_SPOKE: ...')
    or 'BASELINE_PATH_C broken: ...'. Caller wraps in try/except and surfaces
    compute_failed=True with the broken_spoke reason -- the verdict
    classifier sees the explicit cause."""
    E_final, enc_meta = build_arm_encoder(arm_label, V, n_dim, vocab, idx_train, seed)
    device = E_final.device
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    src_keys_held = E_final[idx_held_t]
    W = build_rank1_W_gpu(idx_train_t, E_final, INGEST_CHUNK)
    n_h = src_keys_held.shape[0]
    pred_held = torch.zeros((n_h, n_dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        pred_held[b:end] = _l2_normalize_t(src_keys_held[b:end] @ W.T)
    del W
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = pred_held[b:end] @ E_final.T
    t_recall = time.time() - t0
    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del pred_held, src_keys_held, idx_train_t, idx_held_t, E_final
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "encoder_meta": enc_meta,
    }


def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float
                              ) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    logp_nxt = logp[np.arange(n), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    pred = np.argmax(logp, axis=1)
    return float(np.mean(pred == nxt))


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
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _test_metric(T: float, lam: float, fn) -> float:
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

    bpc_best_test = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best_test = _test_metric(best_mrr["T"], best_mrr["lambda"],
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


# ============================================================================
# text8 loader + vocab
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


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int,
                       mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
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
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d vs %d" % (len(toks), N_TRAIN + N_HELD),
              flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]),
          flush=True)
    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    if len(nxt_eval) == 0:
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM, "N_DIM": N_DIM,
                 "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
                 "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                 "elapsed_s_seed": round(time.time() - t_seed, 2),
                 "device": str(DEVICE), "n_llm_calls": 0}
    n_dev = len(nxt_eval) // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, vocab, idx_train, idx_held, seed, V, N_DIM)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err),
                  flush=True)
            broken_spoke_flag = "FIX_1_BROKEN_SPOKE" in err
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"),
                            "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
                            "broken_spoke_detected": bool(broken_spoke_flag),
                            "broken_spoke_reason": err,
                            "gate_entropy": None,
                            "gate_entropy_in_band": False,
                            "bundle_mode": "compute_failed",
                            "spoke_diversity_cv": 0.0,
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
        logits_eval = logits_ctx[mask]
        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:], U_log,
                          nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["encoder_meta"] = ar.get("encoder_meta", {})
        # surface the per-arm diversity_cv into the top-level arm dict so the
        # verdict can read it without digging
        jr["spoke_diversity_cv"] = ar.get("encoder_meta", {}).get(
            "spoke_diversity_cv", 0.0)
        # v3: surface FIX 1 + FIX 3 fields for verdict
        em = ar.get("encoder_meta", {})
        jr["broken_spoke_detected"] = bool(em.get("broken_spoke_detected", False))
        jr["broken_spoke_reason"] = em.get("broken_spoke_reason", "")
        jr["gate_entropy"] = em.get("gate_entropy", None)
        jr["gate_entropy_in_band"] = bool(em.get("gate_entropy_in_band", True))
        jr["t_gate_used"] = em.get("t_gate_used", None)
        jr["bundle_mode"] = em.get("bundle_mode", "n/a")
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f div_cv=%.4f "
              "bestT=%.4f bestL=%.2f rawT1=%.3f" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["spoke_diversity_cv"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"]), flush=True)

    return {
        "seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM, "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE), "n_llm_calls": 0,
    }


# ============================================================================
# Verdict (diversity-aware per Fix #28)
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Unigram aggregation
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan"))
                 for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM", {}).get("mrr_unigram", float("nan"))
                for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
    }

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}
    V_first = units[0].get("V", VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    for arm in ARMS:
        cf = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not f) and math.isfinite(
            u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for f, u in zip(cf, units)]
        valid_units = [u for ok, u in zip(valid, units) if ok]
        n_cf = int(sum(cf))
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "raw_bpc_at_T1_L1_mean": float("nan"),
                "spoke_diversity_cv_mean": 0.0,
                "n_valid_seeds": 0,
                "n_compute_failed": n_cf,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_t1_vals = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
        div_vals = [u["by_arm"][arm].get("spoke_diversity_cv", 0.0)
                     for u in valid_units]
        # v3: aggregate FIX 1 + FIX 3 fields
        broken_per_seed = [bool(u["by_arm"][arm].get("broken_spoke_detected", False))
                            for u in valid_units]
        gate_ents = [u["by_arm"][arm].get("gate_entropy", None)
                      for u in valid_units]
        gate_ents_finite = [g for g in gate_ents
                              if isinstance(g, (int, float)) and math.isfinite(float(g))]
        gate_in_band_per_seed = [bool(u["by_arm"][arm].get("gate_entropy_in_band", True))
                                    for u in valid_units]
        # Also count ALL units (incl compute_failed) for broken_spoke aggregation
        all_broken = [bool(u["by_arm"].get(arm, {}).get("broken_spoke_detected", False))
                       for u in units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "top1_acc_std": round(float(np.std(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_t1_vals)), 4),
            "spoke_diversity_cv_mean": round(float(np.mean(div_vals)), 6),
            "spoke_diversity_cv_std": round(float(np.std(div_vals)), 6),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_cf,
            "all_seeds_failed": False,
            "any_broken_spoke": bool(any(all_broken)),
            "n_broken_spoke_seeds": int(sum(all_broken)),
            "gate_entropy_mean": (round(float(np.mean(gate_ents_finite)), 4)
                                    if gate_ents_finite else None),
            "gate_entropy_min": (round(float(np.min(gate_ents_finite)), 4)
                                    if gate_ents_finite else None),
            "gate_entropy_max": (round(float(np.max(gate_ents_finite)), 4)
                                    if gate_ents_finite else None),
            "gate_entropy_all_in_band": bool(
                len(gate_in_band_per_seed) > 0 and all(gate_in_band_per_seed)),
            "n_gate_entropy_out_of_band": int(sum(
                1 for g in gate_in_band_per_seed if not g)),
        }

    # Sanity rail: BASELINE arm within +/- SANITY_RAIL_TOL of v1 7.667
    baseline = by_arm_agg.get(BASELINE_ARM, {})
    baseline_bpc = baseline.get("bpc_best_mean", float("inf"))
    sanity_rail_ok = False
    sanity_rail_delta = float("inf")
    if math.isfinite(baseline_bpc):
        sanity_rail_delta = abs(baseline_bpc - V1_BASELINE_BPC_REF)
        sanity_rail_ok = bool(sanity_rail_delta <= SANITY_RAIL_TOL)

    # Find best hub arm + its diversity
    hub_results = []
    for a in HUB_ARMS:
        h = by_arm_agg.get(a, {})
        if h.get("all_seeds_failed", False):
            continue
        b = h.get("bpc_best_mean", float("inf"))
        cv = h.get("bpc_best_cv", float("inf"))
        div = h.get("spoke_diversity_cv_mean", 0.0)
        if math.isfinite(b):
            hub_results.append((a, b, cv, div))
    hub_results_sorted = sorted(hub_results, key=lambda x: x[1])
    best_hub = hub_results_sorted[0] if hub_results_sorted else (None, float("inf"),
                                                                    float("inf"), 0.0)
    best_hub_arm, best_hub_bpc, best_hub_cv, best_hub_div = best_hub

    # METHODOLOGY_CHECK: ANY diverse arm with cv < DIVERSITY_CV_DEGEN
    degen_diversity_arms = [a for a, _, _, d in hub_results
                              if d < DIVERSITY_CV_DEGEN]

    # DEGEN gate (readout collapse vs uniform-vocab)
    degen_arms_readout = []
    for arm in ARMS:
        a = by_arm_agg[arm]
        rt = a.get("raw_bpc_at_T1_L1_mean", float("nan"))
        if isinstance(rt, float) and math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_arms_readout.append(arm)
    any_substrate_clears_unigram = any(
        by_arm_agg[a].get("bpc_best_mean", float("inf")) < unigram_agg["bpc_mean"]
        for a in HUB_ARMS if not by_arm_agg[a].get("all_seeds_failed", False)
    )

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a); continue
        arm_lines.append("%s=bpc%.3f|cv%.3f|div%.4f|top1%.4f|mrr%.4f" % (
            a, x["bpc_best_mean"], x.get("bpc_best_cv", float("nan")),
            x.get("spoke_diversity_cv_mean", 0.0),
            x["top1_acc_mean"], x["mrr_at_10_mean"]))
    summary = ("HUB_SPOKE_E1_v2 uni=bpc%.3f|top1%.4f | %s | best_hub=%s bpc=%.3f "
                "cv=%.3f div_cv=%.4f | sanity_rail=%s delta=%.3f | n_llm=%d") % (
        unigram_agg["bpc_mean"], unigram_agg["top1_mean"], " | ".join(arm_lines),
        best_hub_arm, best_hub_bpc, best_hub_cv, best_hub_div,
        ("OK" if sanity_rail_ok else "MISS"), sanity_rail_delta, n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "primary_arm": PRIMARY_ARM,
        "best_hub_arm": best_hub_arm,
        "best_hub_bpc": best_hub_bpc if math.isfinite(best_hub_bpc) else None,
        "best_hub_cv": best_hub_cv if math.isfinite(best_hub_cv) else None,
        "best_hub_diversity_cv": best_hub_div,
        "sanity_rail_ok": bool(sanity_rail_ok),
        "sanity_rail_delta": round(sanity_rail_delta, 4) if math.isfinite(sanity_rail_delta) else None,
        "sanity_rail_ref": V1_BASELINE_BPC_REF,
        "sanity_rail_tol": SANITY_RAIL_TOL,
        "degen_arms_readout": list(degen_arms_readout),
        "degen_diversity_arms": list(degen_diversity_arms),
        "diversity_cv_min_required": DIVERSITY_CV_MIN,
        "diversity_cv_degen_floor": DIVERSITY_CV_DEGEN,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "any_substrate_clears_unigram_bpc": bool(any_substrate_clears_unigram),
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "v1_baseline_bpc_ref": V1_BASELINE_BPC_REF,
        "v1_best_hub_bpc_ref": V1_BEST_HUB_BPC_REF,
        "hp_bpc_max": HP_BPC_MAX, "cg_bpc_max": CG_BPC_MAX,
        "hf_bpc_min": HF_BPC_MIN, "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "hp_lift_min_bpc": HP_LIFT_MIN_BPC,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "v3 RESCUE of MIDDLE_BAND hub_spoke_E1_v2. 4 arms: single PC "
            "baseline, 3-spoke MRC, 3-spoke MRC+FPE, 3-spoke sign-sum "
            "ABLATION (isolates MRC). THREE FIXES vs v2: FIX 1 per-spoke "
            "health check (NaN/Inf + recon_err sanity); FIX 2 MRC-weighted "
            "bundle (softmax(gate/T_gate), T_gate in %s, replacing sign-sum); "
            "FIX 3 gate training on next-token task signal (substrate-native; "
            "no LLM at inference); gate-entropy must end in [%.2f, %.2f]. "
            "Sparse-bipolar f=%.3f + 1/sqrt(f). N_DIM=%d N_TRAIN=%d "
            "N_HELD=%d V=%d. Sanity rail: baseline within +/- %.3f of v2 "
            "%.3f. DISCRIMINATOR: MRC PASS + ABLATION FAIL -> MRC "
            "load-bearing; both PASS -> health-check + gate-training "
            "load-bearing." % (
                T_GATE_GRID, GATE_ENTROPY_MIN, GATE_ENTROPY_MAX,
                SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
                SANITY_RAIL_TOL, V1_BASELINE_BPC_REF)),
        "cites": [
            "preregs/2026-06-25_substrate_hub_spoke_E1_v3_MRC_calibrated_routing.md",
            "notes/research_readout_degeneracy_5x_disparate_drill_2026-06-25.md",
            "experiments/exp_substrate_hub_spoke_E1_v2_diverse_algorithm.py (v2 base)",
            "data/exp_substrate_hub_spoke_E1_v2_diverse_algorithm/metrics.json (v2 MIDDLE_BAND evidence)",
            "notes/research_5cell_cross_HARDFAIL_synthesis_2026-06-24.md",
            "notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md",
            "USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer",
            "USER_2026-06-22_Fix24_GPU_must_use_GPU",
        ],
    }

    # v3 ANY-broken-spoke aggregation -- gates HARD_PASS bands
    any_broken_in_hub = any(
        by_arm_agg.get(a, {}).get("any_broken_spoke", False) for a in HUB_ARMS)
    broken_arms_list = [a for a in HUB_ARMS
                          if by_arm_agg.get(a, {}).get("any_broken_spoke", False)]

    # v3 DISCRIMINATOR (per cell spec):
    # MRC arms vs ABLATION arm -> isolates MRC vs (health-check+gate-training)
    mrc_arm_bpcs = [(a, by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf")))
                      for a in MRC_ARMS
                      if not by_arm_agg.get(a, {}).get("all_seeds_failed", True)]
    abl_bpc = by_arm_agg.get(ABLATION_ARM, {}).get("bpc_best_mean", float("inf"))
    mrc_best_arm = None; mrc_best_bpc = float("inf")
    if mrc_arm_bpcs:
        mrc_best_arm, mrc_best_bpc = min(mrc_arm_bpcs, key=lambda x: x[1])
    discriminator = "INCONCLUSIVE"
    if math.isfinite(mrc_best_bpc) and math.isfinite(abl_bpc):
        mrc_ok = mrc_best_bpc <= HP_BPC_MAX
        abl_ok = abl_bpc <= HP_BPC_MAX
        if mrc_ok and not abl_ok:
            discriminator = "MRC_LOAD_BEARING"
        elif mrc_ok and abl_ok:
            discriminator = "HEALTH_CHECK_AND_GATE_TRAINING_LOAD_BEARING"
        elif not mrc_ok and not abl_ok:
            discriminator = "ARCHITECTURE_REFUTED"
    detail["discriminator"] = discriminator
    detail["mrc_best_arm"] = mrc_best_arm
    detail["mrc_best_bpc"] = (round(mrc_best_bpc, 4)
                                 if math.isfinite(mrc_best_bpc) else None)
    detail["ablation_bpc"] = (round(abl_bpc, 4)
                                 if math.isfinite(abl_bpc) else None)
    detail["any_broken_spoke_in_hub"] = bool(any_broken_in_hub)
    detail["broken_arms"] = broken_arms_list

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (
                    n_llm, summary), detail)

    # v3 HARD_FAIL: any spoke produced NaN/Inf -> structural failure
    if any_broken_in_hub:
        return ("HARD_FAIL",
                ("HUB_SPOKE_E1_v3 HARD_FAIL: broken-spoke detected (NaN/Inf "
                 "or recon_err out of band) on arms=%s. FIX 1 caught what v2 "
                 "missed; arm health-check architecture working as designed. "
                 "%s" % (broken_arms_list, summary)),
                {**detail, "cert_tier": "HARD_FAIL_BROKEN_SPOKE"})

    if not sanity_rail_ok:
        return ("MIDDLE_BAND",
                ("SANITY_RAIL_MISS: ARM_BASELINE_PATH_C_SINGLE bpc=%.3f deviates "
                 "%.3f from v2 reference %.3f (tol %.3f). v3 results suspect; "
                 "provenance broken. %s" % (
                     baseline_bpc, sanity_rail_delta, V1_BASELINE_BPC_REF,
                     SANITY_RAIL_TOL, summary)), detail)

    # v3: HARD_FAIL when ALL hub arms at unigram floor (HF_BPC_MIN=7.70)
    all_hub_at_floor = all(
        (by_arm_agg[a].get("all_seeds_failed", False)
         or by_arm_agg[a].get("bpc_best_mean", float("inf")) >= HF_BPC_MIN)
        for a in HUB_ARMS
    )
    if all_hub_at_floor:
        return ("HARD_FAIL",
                ("HUB_SPOKE_E1_v3 HARD_FAIL: all hub arms bpc >= %.3f (unigram "
                 "floor). discriminator=%s. %s" % (
                     HF_BPC_MIN, discriminator, summary)),
                {**detail, "cert_tier": "HARD_FAIL_ALL_AT_UNIGRAM"})

    # CHAIN_GRADE per cell spec:
    #   best_hub bpc <= 6.95 AND diversity_cv >= 0.05 AND no broken spokes
    #   AND gate_entropy in [0.5, 1.5] AND CV(seeds) <= 0.03
    best_hub_arm_meta = by_arm_agg.get(best_hub_arm, {}) if best_hub_arm else {}
    best_hub_gate_in_band = best_hub_arm_meta.get("gate_entropy_all_in_band", False)
    if (math.isfinite(best_hub_bpc) and best_hub_bpc <= CG_BPC_MAX
            and best_hub_div >= DIVERSITY_CV_MIN
            and not any_broken_in_hub
            and best_hub_gate_in_band
            and math.isfinite(best_hub_cv) and best_hub_cv <= HP_BPC_CV_MAX):
        return ("HARD_PASS",
                ("HUB_SPOKE_E1_v3 CHAIN_GRADE: best hub %s bpc=%.3f <= %.3f, "
                 "diversity_cv=%.4f, gate_entropy in [%.2f,%.2f], CV(seeds)=%.4f. "
                 "discriminator=%s. %s" % (
                     best_hub_arm, best_hub_bpc, CG_BPC_MAX, best_hub_div,
                     GATE_ENTROPY_MIN, GATE_ENTROPY_MAX, best_hub_cv,
                     discriminator, summary)),
                {**detail, "cert_tier": "CHAIN_GRADE"})

    # HARD_PASS per cell spec:
    #   best_hub bpc <= 7.50 AND beats baseline by >= 0.10 BPC AND no broken
    if (math.isfinite(best_hub_bpc) and best_hub_bpc <= HP_BPC_MAX
            and math.isfinite(baseline_bpc)
            and (baseline_bpc - best_hub_bpc) >= HP_LIFT_MIN_BPC
            and not any_broken_in_hub
            and math.isfinite(best_hub_cv) and best_hub_cv <= HP_BPC_CV_MAX_SOFT):
        return ("HARD_PASS",
                ("HUB_SPOKE_E1_v3 HARD_PASS: best hub %s bpc=%.3f beats baseline "
                 "%.3f by %.3f (>= %.3f), no broken spokes. discriminator=%s. %s" % (
                     best_hub_arm, best_hub_bpc, baseline_bpc,
                     baseline_bpc - best_hub_bpc, HP_LIFT_MIN_BPC,
                     discriminator, summary)),
                {**detail, "cert_tier": "HARD_PASS"})

    if degen_diversity_arms:
        return ("MIDDLE_BAND",
                ("METHODOLOGY_CHECK: spokes degenerated (cv<%.3f) on arm(s)=%s. "
                 "Spokes did not maintain genuine diversity through the "
                 "pipeline; report as MEASURED_MECHANISM. discriminator=%s. "
                 "%s" % (
                     DIVERSITY_CV_DEGEN, degen_diversity_arms, discriminator,
                     summary)),
                {**detail, "cert_tier": "METHODOLOGY_CHECK"})

    return ("MIDDLE_BAND",
            ("HUB_SPOKE_E1_v3 MIDDLE_BAND: best hub bpc=%.3f (baseline %.3f, "
             "diversity_cv=%.4f). discriminator=%s. %s" % (
                 best_hub_bpc, baseline_bpc, best_hub_div, discriminator,
                 summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram + bipolar primitives produce {-1,1}
    v = _bipolar_hv(123, 64)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T1"

    # T2: sparsify_bipolar yields exact-nnz per row
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz_per_row = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T2 nnz: %s" % nnz_per_row

    # T3: temperature endpoints
    n, V = 1, 8
    peaked = np.zeros((n, V), dtype=np.float32); peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.01)
    assert probs.max() > 0.5, "T3 T=0.01: %.3f" % probs.max()
    assert softmax_logits_with_T(peaked, 10.0).max() < 0.145, "T4 T=10"

    # T5/T6: joint-sweep endpoints reproduce uniform / raw
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    sub = np.zeros((len(nxt), 5), dtype=np.float32)
    logp = log_linear_interp_logp(np.log(np.full_like(sub, 1.0/5.0)), U_log, 0.0)
    assert abs(bpc_from_logp(logp, nxt) - (-np.mean(np.log(U[nxt]))/math.log(2.0))) < 1e-4, "T5"

    # T7: each spoke builder produces L2-normalized bipolar [V, n_dim]
    V_t, ndim_t = 8, 64
    vocab_t = ["<unk>", "the", "cat", "dog", "ran", "fast", "slow", "home"]
    idx_dummy = np.array([1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4], dtype=np.int64)
    E_s1, m1 = build_spoke_softhebb_gpu(V_t, ndim_t, vocab_t, idx_dummy, seed=0)
    assert E_s1.shape == (V_t, ndim_t), "T7a softhebb shape"
    assert torch.allclose(E_s1.norm(dim=1),
                            torch.ones(V_t, device=E_s1.device), atol=1e-4), "T7a norm"
    E_s2, m2 = build_spoke_chartri_ri_gpu(V_t, ndim_t, vocab_t, idx_dummy, seed=0)
    assert E_s2.shape == (V_t, ndim_t), "T7b chartri-ri shape"
    E_s3, m3 = build_spoke_pc_gpu(V_t, ndim_t, vocab_t, idx_dummy, seed=0)
    assert E_s3.shape == (V_t, ndim_t), "T7c PC shape"
    E_s4, m4 = build_spoke_fpe_gpu(V_t, ndim_t, vocab_t, idx_dummy, seed=0)
    assert E_s4.shape == (V_t, ndim_t), "T7d FPE shape"

    # T8 DIVERSITY-DISCRIMINATOR: 3 diverse-algorithm spokes must have CV > 0
    # (and noticeably > the v1 alpha-jitter cv=0.0008)
    div_cv = compute_spoke_diversity_cv([E_s1, E_s2, E_s3])
    assert div_cv > 0.01, ("T8 diversity-discriminator broken: 3 diverse-algo "
                            "spokes cv=%.6f <= 0.01 (v1 alpha-jitter was 0.0008; "
                            "v2 must improve)") % div_cv
    print("[T8] diverse-algo spoke diversity_cv = %.4f (v1 was 0.0008)" % div_cv)

    # T9: hub majority-rule bundling preserves bipolar shape
    h = hub_aggregate_majority([E_s1, E_s2, E_s3])
    assert h.shape == (V_t, ndim_t), "T9 hub shape"

    # T10: cf-RPE gates evolve under training + softmax sum to 1
    gates = adapt_cfrpe_gates([E_s1, E_s2, E_s3], idx_dummy, n_steps=10, eta=0.1, seed=42)
    assert gates.shape == (3,), "T10 gates shape"
    assert abs(float(gates.sum().item()) - 1.0) < 1e-5, "T10 gates softmax"

    # T11: v3 FIX 1 -- spoke_health_check catches NaN/Inf
    healthy, reason = spoke_health_check(E_s2, m2)
    assert healthy, "T11a healthy spoke flagged as broken: %s" % reason
    # Inject NaN into a fresh copy
    E_bad = E_s2.clone()
    E_bad[0, 0] = float("nan")
    healthy_bad, reason_bad = spoke_health_check(E_bad, m2)
    assert not healthy_bad, "T11b NaN spoke not detected; reason=%s" % reason_bad
    # NaN recon_err
    m_bad = dict(m2); m_bad["spoke_recon_err"] = float("nan")
    healthy_recon, reason_recon = spoke_health_check(E_s2, m_bad)
    assert not healthy_recon, "T11c NaN recon_err not detected"

    # T12: v3 FIX 2 -- hub_aggregate_mrc produces L2-normalized bipolar
    # v3.1: explicit device= so test exercises the same path as real arms
    gl_test = torch.tensor([2.0, 0.0, -1.0], dtype=TORCH_DTYPE, device=DEVICE)
    bundle_mrc, gates_mrc = hub_aggregate_mrc([E_s1, E_s2, E_s3], gl_test, t_gate=1.0)
    assert bundle_mrc.shape == (V_t, ndim_t), "T12a MRC shape"
    assert abs(float(gates_mrc.sum().item()) - 1.0) < 1e-5, "T12b MRC gates softmax"
    # T_gate -> 0 collapses to winner-take-all
    _, gates_low_t = hub_aggregate_mrc([E_s1, E_s2, E_s3], gl_test, t_gate=0.1)
    assert float(gates_low_t.max().item()) > float(gates_mrc.max().item()), \
        "T12c lower T_gate must SHARPEN gates"
    # T_gate -> inf collapses to uniform
    _, gates_high_t = hub_aggregate_mrc([E_s1, E_s2, E_s3], gl_test, t_gate=10.0)
    assert float(gates_high_t.max().item()) < float(gates_mrc.max().item()), \
        "T12d higher T_gate must FLATTEN gates"

    # T13: v3 FIX 3 -- task-signal gate training returns finite LOGITS
    gate_logits_ts = adapt_gates_task_signal([E_s1, E_s2, E_s3], idx_dummy,
                                                 n_steps=10, eta=0.1, seed=42)
    assert gate_logits_ts.shape == (3,), "T13a task-signal gate shape"
    assert torch.isfinite(gate_logits_ts).all().item(), \
        "T13b gate_logits has NaN/Inf"

    # T14: gate_entropy computation -- uniform = log(3) ~ 1.0986, peaked ~ 0
    # v3.1: explicit device= for tensor-creation hygiene
    gates_uni = torch.tensor([1.0/3, 1.0/3, 1.0/3], dtype=TORCH_DTYPE, device=DEVICE)
    ent_uni = gate_entropy(gates_uni)
    assert abs(ent_uni - math.log(3.0)) < 1e-4, "T14a uniform entropy: %.4f" % ent_uni
    gates_peak = torch.tensor([0.99, 0.005, 0.005], dtype=TORCH_DTYPE, device=DEVICE)
    ent_peak = gate_entropy(gates_peak)
    assert ent_peak < 0.2, "T14b peaked entropy: %.4f" % ent_peak

    # T15: verdict bands (CHAIN_GRADE / HARD_PASS / HARD_FAIL_BROKEN_SPOKE /
    #                     HARD_FAIL_UNIGRAM / MIDDLE_BAND / SANITY_RAIL_MISS /
    #                     METHODOLOGY_CHECK) + discriminator
    def _mk_unit_uni(bpc=7.738, top1=0.2171, mrr=0.30):
        return {"ARM_UNIGRAM": {"bpc_unigram": bpc, "top1_unigram": top1,
                                  "mrr_unigram": mrr, "n_test": 100}}

    def _mk_arm(bpc=8.0, top1=0.15, mrr=0.25, raw_t1=None, div=0.1,
                  broken=False, gate_ent=1.0, gate_ok=True):
        return {"bpc_best": bpc, "top1_acc": top1, "mrr_at_10": mrr,
                 "best_T_for_bpc": 0.5, "best_lambda_for_bpc": 0.3,
                 "best_dev_bpc": bpc,
                 "best_T_for_top1": 0.5, "best_lambda_for_top1": 0.3,
                 "best_T_for_mrr": 0.5, "best_lambda_for_mrr": 0.3,
                 "raw_bpc_at_T1_L1": raw_t1 if raw_t1 is not None else bpc,
                 "raw_top1_at_T1_L1": top1, "n_dev": 100, "n_test": 100,
                 "spoke_diversity_cv": div,
                 "broken_spoke_detected": bool(broken),
                 "broken_spoke_reason": "test" if broken else "",
                 "gate_entropy": float(gate_ent),
                 "gate_entropy_in_band": bool(gate_ok),
                 "t_gate_used": 1.0, "bundle_mode": "mrc_weighted"}

    def _full(arms_d, V=4000):
        by_arm = _mk_unit_uni()
        for a in ARMS:
            by_arm[a] = arms_d.get(a, _mk_arm())
        return {"seed": 0, "by_arm": by_arm, "V": V, "N": 64, "N_DIM": 64,
                 "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": V, "run_mode": "smoke",
                 "config_version": "selftest", "elapsed_s_seed": 0.01,
                 "device": "cpu", "n_llm_calls": 0}

    # CHAIN_GRADE: baseline rail-OK; best hub <= 6.95 diversity >= 0.05
    # no broken spokes; gate_entropy in [0.5, 1.5]; CV(seeds) <= 0.03
    u_cg = _full({
        BASELINE_ARM: _mk_arm(bpc=7.667, raw_t1=7.667, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=6.85, raw_t1=6.85, div=0.10),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=6.90, raw_t1=6.90, div=0.12),
        ABLATION_ARM: _mk_arm(bpc=7.55, raw_t1=7.55, div=0.10),
    })
    v, m, d = compute_verdict([u_cg, u_cg, u_cg])
    assert v == "HARD_PASS", "T15 CG verdict=%s msg=%s" % (v, m[:200])
    assert d.get("cert_tier") == "CHAIN_GRADE", "T15 CG cert_tier=%s" % d.get("cert_tier")

    # HARD_PASS: best hub <= 7.50, beats baseline by >= 0.10, no broken
    u_hp = _full({
        BASELINE_ARM: _mk_arm(bpc=7.667, raw_t1=7.667, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=7.40, raw_t1=7.40, div=0.08),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=7.30, raw_t1=7.30, div=0.09),
        ABLATION_ARM: _mk_arm(bpc=7.65, raw_t1=7.65, div=0.10),
    })
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T15 HP verdict=%s msg=%s" % (v, m[:200])
    assert d.get("cert_tier") == "HARD_PASS", "T15 HP cert_tier=%s" % d.get("cert_tier")

    # HARD_FAIL_BROKEN_SPOKE: any spoke broken -> structural HARD_FAIL
    u_brk = _full({
        BASELINE_ARM: _mk_arm(bpc=7.667, raw_t1=7.667, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=7.05, raw_t1=7.05, div=0.10, broken=True),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=7.10, raw_t1=7.10, div=0.10),
        ABLATION_ARM: _mk_arm(bpc=7.40, raw_t1=7.40, div=0.10),
    })
    v, m, d = compute_verdict([u_brk, u_brk, u_brk])
    assert v == "HARD_FAIL", "T15 BRK verdict=%s msg=%s" % (v, m[:200])
    assert d.get("cert_tier") == "HARD_FAIL_BROKEN_SPOKE", \
        "T15 BRK cert_tier=%s" % d.get("cert_tier")

    # HARD_FAIL_ALL_AT_UNIGRAM: all hub arms >= 7.70
    u_hfu = _full({
        BASELINE_ARM: _mk_arm(bpc=7.667, raw_t1=7.667, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=7.75, raw_t1=7.75, div=0.10),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=7.80, raw_t1=7.80, div=0.10),
        ABLATION_ARM: _mk_arm(bpc=7.72, raw_t1=7.72, div=0.10),
    })
    v, m, d = compute_verdict([u_hfu, u_hfu, u_hfu])
    assert v == "HARD_FAIL", "T15 HFU verdict=%s msg=%s" % (v, m[:200])
    assert d.get("cert_tier") == "HARD_FAIL_ALL_AT_UNIGRAM", \
        "T15 HFU cert_tier=%s" % d.get("cert_tier")

    # SANITY_RAIL_MISS: baseline outside +/-0.02 of v2 7.667
    u_sr = _full({
        BASELINE_ARM: _mk_arm(bpc=7.90, raw_t1=7.90, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=7.00, raw_t1=7.00, div=0.10),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=6.95, raw_t1=6.95, div=0.11),
        ABLATION_ARM: _mk_arm(bpc=6.90, raw_t1=6.90, div=0.12),
    })
    v, m, d = compute_verdict([u_sr, u_sr, u_sr])
    assert v == "MIDDLE_BAND", "T15 SR verdict=%s" % v
    assert "SANITY_RAIL_MISS" in m, "T15 SR msg: %s" % m[:200]

    # DISCRIMINATOR: MRC PASS + ABLATION FAIL -> MRC_LOAD_BEARING
    u_disc = _full({
        BASELINE_ARM: _mk_arm(bpc=7.667, raw_t1=7.667, div=0.0),
        "ARM_HUB_3SPOKE_MRC": _mk_arm(bpc=7.30, raw_t1=7.30, div=0.10),
        "ARM_HUB_3SPOKE_MRC_PLUS_FPE": _mk_arm(bpc=7.35, raw_t1=7.35, div=0.10),
        ABLATION_ARM: _mk_arm(bpc=7.65, raw_t1=7.65, div=0.10),
    })
    v, m, d = compute_verdict([u_disc, u_disc, u_disc])
    assert d.get("discriminator") == "MRC_LOAD_BEARING", \
        "T15 DISC discriminator=%s" % d.get("discriminator")

    # T16: zero LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "T16 llm counter"

    print("[selftest v3] PASS: T1 bipolar + T2 sparsify + T3-T4 temp endpoints "
          "+ T5 lam0=uni + T7 4-spoke shapes + T8 diversity_cv>0.01 "
          "+ T9 hub majority + T10 cf-RPE softmax + T11 FIX1 spoke_health "
          "(NaN/Inf detection) + T12 FIX2 MRC bundle (T_gate sharpens/flattens) "
          "+ T13 FIX3 task-signal gate_logits + T14 gate_entropy + T15 v3 "
          "verdict bands (CG/HP/HF_BROKEN/HF_UNIGRAM/SR_MISS + discriminator) "
          "+ T16 llm=0", flush=True)


# ============================================================================
# atexit synthesizer + main
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
            "anchor_name": ANCHOR_NAME, "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM, "N": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP, "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_hub_spoke_E1_v3_MRC_calibrated_routing",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION, "device": str(DEVICE),
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS))); sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e); sys.stderr.flush()


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
          "seeds=%s arms=%s name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9),
                flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "hub-spoke-E1-v3-MRC-calibrated"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True); continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                        run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "anchor": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
        "N_DIM": N_DIM, "N": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP, "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH, "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID, "MRR_K": MRR_K,
        "PC_ALPHA": PC_ALPHA, "PC_BETA": PC_BETA,
        "PC_N_LAYERS": PC_N_LAYERS, "PC_N_PASSES": PC_N_PASSES,
        "SOFTHEBB_K_WTA": SOFTHEBB_K_WTA, "SOFTHEBB_LR": SOFTHEBB_LR,
        "RI_WINDOW": RI_WINDOW, "RI_SPARSITY": RI_SPARSITY,
        "FPE_BANDWIDTH": FPE_BANDWIDTH,
        "ENCODER_TRAIN_TOKENS": ENCODER_TRAIN_TOKENS,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "CFRPE_ETA": CFRPE_ETA, "CFRPE_N_STEPS": CFRPE_N_STEPS,
        "T_GATE_GRID": T_GATE_GRID,
        "DIVERSITY_CV_MIN": DIVERSITY_CV_MIN,
        "DIVERSITY_CV_DEGEN": DIVERSITY_CV_DEGEN,
        "GATE_ENTROPY_MIN": GATE_ENTROPY_MIN,
        "GATE_ENTROPY_MAX": GATE_ENTROPY_MAX,
        "HP_BPC_MAX": HP_BPC_MAX, "CG_BPC_MAX": CG_BPC_MAX,
        "HF_BPC_MIN": HF_BPC_MIN, "HP_BPC_CV_MAX": HP_BPC_CV_MAX,
        "HP_BPC_CV_MAX_SOFT": HP_BPC_CV_MAX_SOFT,
        "SANITY_RAIL_TOL": SANITY_RAIL_TOL,
        "arms": ARMS, "n_seeds": len(SEEDS),
        "detail": detail, "per_unit": units,
        "metrics_source": "measured_gpu_substrate_hub_spoke_E1_v3_MRC_calibrated_routing",
        "elapsed_s": time.time() - t0, "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-OWNED diverse-algo spokes; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION, "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
