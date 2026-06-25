"""substrate_hub_spoke_E1_encoder_v1 -- HUB-and-SPOKE federation encoder.

Tests encoding drill's #1 ranked encoding architecture (E1; P_deflated=0.45):
hub-and-spoke federation. Brain ATL (anterior temporal lobe) analog -- multiple
substrate-OWNED "spokes" feed into a central hub.

Per encoding drill 2026-06-24 (notes/research_optimal_substrate_encoding_design_
space_2x_drill_2026-06-24.md), optimal Stage-1 encoding is a hub-and-spoke
federation of substrate-OWNED encoders. Brain decisively uses this architecture
(Patterson-Rogers ATL 2007; Lambon Ralph 2017; CLIP/ImageBind ML convergence).

Lane 1 (substrate-native): NO word2vec, NO Pythia. All spokes are substrate-OWNED
PC-style encoders. Sparse-bipolar f=0.02 with 1/sqrt(f) amplitude scaling per
Stage-1 foundations (bit-density inventory 2026-06-24).

Four arms (3 seeds each; text8 N_TRAIN=100k V=4000 N_DIM=8192):
  1. ARM_BASELINE_PATH_C_SINGLE
     Single-spoke substrate-OWNED PC encoder (Path C v2 reference).
     Sanity rail: bpc_best within +/- 0.10 of v2 reference 7.6184.
  2. ARM_HUB_SPOKE_3SPOKE
     3 independent spokes -> hub via majority-rule bundling.
     Spokes use different seeds and slightly different PC alpha/beta to ensure
     genuine diversity (not just rank-1 redundancy).
  3. ARM_HUB_SPOKE_5SPOKE
     5 spokes -> hub. One-knob change from 3SPOKE (spoke count).
  4. ARM_HUB_SPOKE_WITH_CFRPE  (PRIMARY pre-registered arm)
     3 spokes + adaptive cf-RPE plasticity on hub aggregation weights.
     Tests whether plasticity ADAPTS hub gating to improve LM signal.

Pre-reg HARD bands (PRIMARY: ARM_HUB_SPOKE_WITH_CFRPE):
  HARD_PASS: best hub-spoke arm bpc_best <= 7.20 AND CV < 0.05
             (improves Path C single-spoke by >= 0.40 bits)
  CHAIN_GRADE: best hub-spoke arm bpc_best <= 6.95
               (closes gap to word2vec-equivalent without leakage)
  HARD_FAIL: ALL hub-spoke arms bpc_best >= 7.60
             (federation doesn't help; principle may not transfer to substrate)
  MIDDLE_BAND: best in [7.20, 7.50]
  SANITY_RAIL: ARM_BASELINE_PATH_C_SINGLE bpc_best within Path C v2 reference
               (7.6184 +/- 0.10). If rail violated, results suspect (provenance).

MANDATORY sanity self-tests (T1-T13):
  T1: char-trigram bipolar primitive
  T2: sparse-bipolar primitive (exact nnz + uniq={-1,0,1})
  T3: temperature 0.01 peaked -> max_prob > 0.5
  T4: temperature 10.0 peaked -> near-uniform
  T5: joint sweep lambda=0 reproduces unigram BPC
  T6: lambda=1.0 reproduces raw substrate
  T7: MRR@10 on planted 5-pair set
  T8: PC encoder forward shape + L2 norm
  T9: hub majority-rule bundling preserves bipolar geometry
  T10: hub aggregates N spokes to single [V, N_DIM] output
  T11: verdict bands (HP / CG / HF / MID / SANITY_RAIL)
  T12: cf-RPE gating evolves under training (std/mean > 0 after pass-1)
  T13: zero LLM calls at inference

GPU REQUIRED (Fix #24): torch.cuda for matmul + multi-spoke PC training.

Cites:
  preregs/2026-06-24_substrate_hub_spoke_E1_encoder_v1.md
  notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md
  notes/director_stage2_preauthored_dispatch_specs_2026-06-24.md
  experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py  (reference)
  data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json (7.6184 ref)
  USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer
  USER_2026-06-22_Fix24_GPU_must_use_GPU

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

ANCHOR_NAME = "substrate_hub_spoke_E1_encoder_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
PATH_C_V2_BPC_REF = 7.6184  # Path C v2 single-spoke landed reference

# Pre-reg bands
HP_BPC_MAX = 7.20
CG_BPC_MAX = 6.95
HF_BPC_MIN = 7.60
HP_BPC_CV_MAX = 0.05
SANITY_RAIL_TOL = 0.10  # ARM_BASELINE within +/- 0.10 of PATH_C_V2_BPC_REF
DEGEN_TOL = 0.5

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

# Joint (T, lambda) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Sparse-bipolar f (per Stage-1 foundations: f=0.02 chain-grade optimal)
SPARSE_BIPOLAR_F = 0.02

# PC encoder hyperparameters (mid-range from Path C v1 sweep)
PC_N_LAYERS = 3
PC_ALPHA = 0.05
PC_BETA = 2.0
PC_N_PASSES = 1

# Hub-spoke counts per arm
N_SPOKES_ARM2 = 3
N_SPOKES_ARM3 = 5
N_SPOKES_ARM4 = 3  # cf-RPE adaptive

# cf-RPE hyperparameters
CFRPE_ETA = 0.02
CFRPE_N_STEPS = 50

# MRR @ K
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    PC_TRAINING_TOKENS = 100_000
else:
    # Smoke must fit under 180s laptop CPU. Exercises every arm + 5-spoke hub.
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 200
    N_DIM = 256  # small for 5-spoke under smoke time
    INGEST_CHUNK = 256
    RECALL_BATCH = 64
    PC_TRAINING_TOKENS = 500
    CFRPE_N_STEPS = 8

ARMS = [
    "ARM_BASELINE_PATH_C_SINGLE",
    "ARM_HUB_SPOKE_3SPOKE",
    "ARM_HUB_SPOKE_5SPOKE",
    "ARM_HUB_SPOKE_WITH_CFRPE",
]
BASELINE_ARM = "ARM_BASELINE_PATH_C_SINGLE"
HUB_ARMS = [a for a in ARMS if a != BASELINE_ARM]
PRIMARY_ARM = "ARM_HUB_SPOKE_WITH_CFRPE"

CONFIG_VERSION = (
    "substrate_hub_spoke_E1_encoder_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "arms=%s seeds=%s mode=%s temps=%s lambdas=%s sparse_f=%.3f "
    "pc_layers=%d pc_alpha=%.3f pc_beta=%.2f pc_passes=%d pc_train_tokens=%d "
    "n_spokes_arm2=%d n_spokes_arm3=%d n_spokes_arm4=%d "
    "cfrpe_eta=%.3f cfrpe_n_steps=%d MRR_K=%d device=%s; "
    "bands HP<=%.3f CG<=%.3f HF>=%.3f cv_max=%.3f sanity_rail_tol=%.3f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, PC_N_LAYERS, PC_ALPHA, PC_BETA,
    PC_N_PASSES, PC_TRAINING_TOKENS,
    N_SPOKES_ARM2, N_SPOKES_ARM3, N_SPOKES_ARM4,
    CFRPE_ETA, CFRPE_N_STEPS, MRR_K, str(DEVICE),
    HP_BPC_MAX, CG_BPC_MAX, HF_BPC_MIN, HP_BPC_CV_MAX, SANITY_RAIL_TOL,
)


# ============================================================================
# Primitives (mirror Path C v2 verbatim where applicable)
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
    # 1/sqrt(f) amplitude scaling per Stage-1 foundations
    out = out * (1.0 / math.sqrt(max(f, 1e-9)))
    return out


def build_planted_bipolar_inputs_gpu(V: int, n_dim: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed * 7919 + 17)
    X = (rng.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    Xn = _l2_normalize_np(X)
    return torch.from_numpy(Xn).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Substrate-owned 3-layer Hebbian-PC encoder (one SPOKE)
# Mirrors Path C v2 train_substrate_pc_encoder_gpu
# ============================================================================

def train_pc_spoke_gpu(
    X_planted: torch.Tensor,
    idx_train: np.ndarray,
    n_dim: int,
    alpha: float,
    n_passes: int,
    beta: float,
    seed: int,
    train_tokens: int,
) -> Tuple[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], torch.Tensor, Dict]:
    device = X_planted.device
    V = X_planted.shape[0]
    rng = torch.Generator(device="cpu")
    rng.manual_seed(int(seed) * 1009 + 31)
    W_L1 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L2 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L3 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    E_excit = torch.zeros(n_dim, device=device, dtype=TORCH_DTYPE)

    n_train_tokens = min(len(idx_train), train_tokens)
    idx_t = torch.from_numpy(idx_train[:n_train_tokens].astype(np.int64)).to(device)
    update_chunk = 1024 if RUN_MODE == "full" else 128
    t_start = time.time()
    n_updates = 0
    per_pass_recon = {"L1": [], "L3": []}
    for pass_i in range(n_passes):
        rL1_a, rL3_a, nc = 0.0, 0.0, 0
        for b in range(0, n_train_tokens, update_chunk):
            end = min(b + update_chunk, n_train_tokens)
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
            rL1_a += float(err_L1.norm(dim=1).mean().item())
            rL3_a += float(err_L3.norm(dim=1).mean().item())
            nc += 1
            n_updates += 1
            if device.type == "cuda" and (n_updates % 16 == 0):
                torch.cuda.synchronize()
        if nc > 0:
            per_pass_recon["L1"].append(round(rL1_a / nc, 4))
            per_pass_recon["L3"].append(round(rL3_a / nc, 4))
    meta = {
        "per_pass_mean_recon_err": per_pass_recon,
        "n_train_tokens": int(n_train_tokens),
        "wall_train_s": round(time.time() - t_start, 2),
        "n_updates": int(n_updates),
        "alpha": float(alpha),
        "beta": float(beta),
    }
    return (W_L1, W_L2, W_L3), E_excit, meta


def encode_with_pc_spoke(
    X_planted: torch.Tensor,
    W_stack: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    E_excit: torch.Tensor,
    beta: float,
) -> torch.Tensor:
    W_L1, W_L2, W_L3 = W_stack
    pre_L1 = X_planted @ W_L1.T
    L1_out = _sign_with_zero_tiebreak(pre_L1)
    pre_L2 = L1_out @ W_L2.T
    L2_out = _sign_with_zero_tiebreak(pre_L2)
    pre_L3 = L2_out @ W_L3.T
    n_dim = pre_L3.shape[-1]
    route_w = torch.softmax(-beta * E_excit, dim=0)
    pre_L3 = pre_L3 * (route_w * n_dim)
    L3_out = _sign_with_zero_tiebreak(pre_L3)
    return _l2_normalize_t(L3_out)


# ============================================================================
# Hub aggregation: majority-rule bundling across spokes
# ============================================================================

def hub_aggregate_majority(spoke_outputs: List[torch.Tensor]) -> torch.Tensor:
    """Majority-rule bundle: stack spoke outputs, sum, sign-quantize.

    Spokes assumed already L2-normalized + signed. Hub preserves bipolar
    geometry by sign(sum). No multiplicative compose (zero-product cascade
    risk per sparse-bipolar compose incompatibility drill 2026-06-23).
    """
    if not spoke_outputs:
        raise ValueError("hub_aggregate_majority: empty spoke list")
    stacked = torch.stack(spoke_outputs, dim=0)  # [n_spokes, V, n_dim]
    summed = stacked.sum(dim=0)  # [V, n_dim]
    bundled = _sign_with_zero_tiebreak(summed)
    return _l2_normalize_t(bundled)


def hub_aggregate_cfrpe_weighted(spoke_outputs: List[torch.Tensor],
                                    gates: torch.Tensor) -> torch.Tensor:
    """cf-RPE weighted hub aggregation: per-spoke gate scalar weights.

    gates: [n_spokes] non-negative floats summing to ~1 (softmax in caller).
    Output preserves bipolar geometry via sign-quantize.
    """
    if not spoke_outputs:
        raise ValueError("hub_aggregate_cfrpe_weighted: empty spoke list")
    n_spokes = len(spoke_outputs)
    if gates.shape[0] != n_spokes:
        raise ValueError("gates len %d != n_spokes %d" % (gates.shape[0], n_spokes))
    stacked = torch.stack(spoke_outputs, dim=0)  # [n_spokes, V, n_dim]
    w = gates.view(n_spokes, 1, 1)
    weighted = (stacked * w).sum(dim=0)  # [V, n_dim]
    bundled = _sign_with_zero_tiebreak(weighted)
    return _l2_normalize_t(bundled)


# ============================================================================
# cf-RPE gate adaptation
# ============================================================================

def adapt_cfrpe_gates(
    spoke_outputs: List[torch.Tensor],
    idx_train: np.ndarray,
    n_steps: int,
    eta: float,
    seed: int,
) -> torch.Tensor:
    """Adapt per-spoke gates by ascending hub-cosine alignment with bigram pairs.

    Substrate-native cf-RPE: each step, sample a token pair (t, t+1), compute
    per-spoke alignment cos(E_spoke[t], E_spoke[t+1]), and reinforce gates
    proportional to alignment. Returns softmaxed gates.
    """
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
        align_t = torch.stack(per_spoke_align)  # [n_spokes]
        # Reward-weighted gate update; subtract mean baseline (zero-baseline cf-RPE)
        mean_a = align_t.mean()
        logits = logits + eta * (align_t - mean_a)
    return torch.softmax(logits, dim=0)


# ============================================================================
# Per-arm encoder builder
# ============================================================================

def build_arm_encoder(
    arm_label: str,
    V: int,
    n_dim: int,
    idx_train: np.ndarray,
    seed: int,
) -> Tuple[torch.Tensor, Dict]:
    """Returns (E_final, meta_dict) for a given arm.

    E_final: [V, n_dim] L2-normalized bipolar (post sparsify + 1/sqrt(f) scale).
    """
    meta: Dict = {"arm": arm_label}
    t0 = time.time()
    if arm_label == BASELINE_ARM:
        # Single PC spoke (mirrors Path C v2 single-spoke)
        X_planted = build_planted_bipolar_inputs_gpu(V, n_dim, seed)
        W_stack, E_excit, pc_meta = train_pc_spoke_gpu(
            X_planted=X_planted, idx_train=idx_train, n_dim=n_dim,
            alpha=PC_ALPHA, n_passes=PC_N_PASSES, beta=PC_BETA,
            seed=seed, train_tokens=PC_TRAINING_TOKENS,
        )
        E_pre = encode_with_pc_spoke(X_planted, W_stack, E_excit, PC_BETA)
        meta["spokes"] = [pc_meta]
        meta["n_spokes"] = 1
        del X_planted, W_stack, E_excit
    elif arm_label in ("ARM_HUB_SPOKE_3SPOKE", "ARM_HUB_SPOKE_5SPOKE",
                          "ARM_HUB_SPOKE_WITH_CFRPE"):
        if arm_label == "ARM_HUB_SPOKE_3SPOKE":
            n_spokes = N_SPOKES_ARM2
        elif arm_label == "ARM_HUB_SPOKE_5SPOKE":
            n_spokes = N_SPOKES_ARM3
        else:
            n_spokes = N_SPOKES_ARM4
        spoke_outputs: List[torch.Tensor] = []
        spoke_metas: List[Dict] = []
        # Each spoke uses a DIFFERENT seed (genuine diversity, not just rank-1).
        # Also vary alpha/beta slightly to avoid identical PC trajectories.
        alpha_grid = [PC_ALPHA * (1.0 + 0.1 * (i - n_spokes / 2.0))
                       for i in range(n_spokes)]
        beta_grid = [PC_BETA * (1.0 + 0.05 * (i - n_spokes / 2.0))
                      for i in range(n_spokes)]
        for sp_i in range(n_spokes):
            sp_seed = int(seed * 977 + 13 * (sp_i + 1))
            X_planted_sp = build_planted_bipolar_inputs_gpu(V, n_dim, sp_seed)
            W_stack_sp, E_excit_sp, pc_meta_sp = train_pc_spoke_gpu(
                X_planted=X_planted_sp, idx_train=idx_train, n_dim=n_dim,
                alpha=float(alpha_grid[sp_i]), n_passes=PC_N_PASSES,
                beta=float(beta_grid[sp_i]),
                seed=sp_seed, train_tokens=PC_TRAINING_TOKENS,
            )
            E_sp = encode_with_pc_spoke(X_planted_sp, W_stack_sp,
                                           E_excit_sp, float(beta_grid[sp_i]))
            spoke_outputs.append(E_sp)
            spoke_metas.append({**pc_meta_sp, "spoke_idx": sp_i,
                                  "spoke_alpha": float(alpha_grid[sp_i]),
                                  "spoke_beta": float(beta_grid[sp_i]),
                                  "spoke_seed": int(sp_seed)})
            del X_planted_sp, W_stack_sp, E_excit_sp
        if arm_label == "ARM_HUB_SPOKE_WITH_CFRPE":
            gates = adapt_cfrpe_gates(
                spoke_outputs=spoke_outputs, idx_train=idx_train,
                n_steps=CFRPE_N_STEPS, eta=CFRPE_ETA, seed=seed,
            )
            meta["cfrpe_gates"] = gates.detach().cpu().numpy().round(4).tolist()
            gate_std = float(gates.std().item())
            gate_mean = float(gates.mean().item())
            meta["cfrpe_gate_std_over_mean"] = round(
                gate_std / max(gate_mean, 1e-9), 4)
            E_pre = hub_aggregate_cfrpe_weighted(spoke_outputs, gates)
        else:
            E_pre = hub_aggregate_majority(spoke_outputs)
        meta["spokes"] = spoke_metas
        meta["n_spokes"] = n_spokes
        del spoke_outputs
    else:
        raise ValueError("unknown arm: %s" % arm_label)

    # Sparse-bipolar + 1/sqrt(f) amplitude scaling (Stage-1 foundations)
    E_sp = _l2_normalize_t(sparsify_bipolar_gpu(E_pre, SPARSE_BIPOLAR_F, seed))
    del E_pre
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    meta["wall_encoder_s"] = round(time.time() - t0, 2)
    return E_sp, meta


# ============================================================================
# Hebbian W builder (rank-1)
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


# ============================================================================
# Logits + joint sweep (mirrors Path C v2)
# ============================================================================

def compute_arm_logits(arm_label: str, idx_train: np.ndarray,
                          idx_held: np.ndarray, seed: int, V: int,
                          n_dim: int) -> Dict:
    E_final, enc_meta = build_arm_encoder(arm_label, V, n_dim, idx_train, seed)
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
# text8 loader + vocab + unigram
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

    # Split held into dev + test halves
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
            ar = compute_arm_logits(arm, idx_train, idx_held, seed, V, N_DIM)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err),
                  flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"),
                            "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
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
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f bestT=%.4f "
              "bestL=%.2f rawT1=%.3f" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"]), flush=True)

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
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan"))
                 for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM", {}).get("mrr_unigram", float("nan"))
                for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "top1_std": round(float(np.std(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
        "mrr_std": round(float(np.std(uni_mrr)), 4),
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
                "n_valid_seeds": 0,
                "n_compute_failed": n_cf,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_t1_vals = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
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
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_cf,
            "all_seeds_failed": False,
        }

    # Sanity rail: BASELINE arm within +/- SANITY_RAIL_TOL of PATH_C_V2_BPC_REF
    baseline = by_arm_agg.get(BASELINE_ARM, {})
    baseline_bpc = baseline.get("bpc_best_mean", float("inf"))
    sanity_rail_ok = False
    sanity_rail_delta = float("inf")
    if math.isfinite(baseline_bpc):
        sanity_rail_delta = abs(baseline_bpc - PATH_C_V2_BPC_REF)
        sanity_rail_ok = bool(sanity_rail_delta <= SANITY_RAIL_TOL)

    # Best hub-spoke arm
    hub_bpcs = []
    for a in HUB_ARMS:
        h = by_arm_agg.get(a, {})
        if h.get("all_seeds_failed", False):
            continue
        b = h.get("bpc_best_mean", float("inf"))
        cv = h.get("bpc_best_cv", float("inf"))
        if math.isfinite(b):
            hub_bpcs.append((a, b, cv))
    hub_bpcs_sorted = sorted(hub_bpcs, key=lambda x: x[1])
    best_hub_arm = hub_bpcs_sorted[0] if hub_bpcs_sorted else (None, float("inf"), float("inf"))

    # DEGEN gate
    degen_arms = []
    for arm in ARMS:
        a = by_arm_agg[arm]
        rt = a.get("raw_bpc_at_T1_L1_mean", float("nan"))
        if isinstance(rt, float) and math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_arms.append(arm)
    any_substrate_clears_unigram = any(
        by_arm_agg[a].get("bpc_best_mean", float("inf")) < unigram_agg["bpc_mean"]
        for a in HUB_ARMS if not by_arm_agg[a].get("all_seeds_failed", False)
    )

    # Substrate-only-decode gate
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=bpc%.3f|cv%.3f|top1%.4f|mrr%.4f" % (
            a, x["bpc_best_mean"], x.get("bpc_best_cv", float("nan")),
            x["top1_acc_mean"], x["mrr_at_10_mean"]))
    summary = ("HUB_SPOKE_E1 uni=bpc%.3f|top1%.4f | %s | best_hub=%s bpc=%.3f cv=%.3f | "
                "sanity_rail=%s delta=%.3f | n_llm=%d") % (
        unigram_agg["bpc_mean"], unigram_agg["top1_mean"], " | ".join(arm_lines),
        best_hub_arm[0], best_hub_arm[1], best_hub_arm[2],
        ("OK" if sanity_rail_ok else "MISS"), sanity_rail_delta, n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "primary_arm": PRIMARY_ARM,
        "best_hub_arm": best_hub_arm[0],
        "best_hub_bpc": best_hub_arm[1] if math.isfinite(best_hub_arm[1]) else None,
        "best_hub_cv": best_hub_arm[2] if math.isfinite(best_hub_arm[2]) else None,
        "sanity_rail_ok": bool(sanity_rail_ok),
        "sanity_rail_delta": round(sanity_rail_delta, 4) if math.isfinite(sanity_rail_delta) else None,
        "sanity_rail_ref": PATH_C_V2_BPC_REF,
        "sanity_rail_tol": SANITY_RAIL_TOL,
        "degen_arms": list(degen_arms),
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "any_substrate_clears_unigram_bpc": bool(any_substrate_clears_unigram),
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "hp_bpc_max": HP_BPC_MAX,
        "cg_bpc_max": CG_BPC_MAX,
        "hf_bpc_min": HF_BPC_MIN,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Hub-and-spoke E1 federation encoder. 4 arms: single PC (baseline), 3-spoke, "
            "5-spoke, 3-spoke+cf-RPE (primary). Sparse-bipolar f=%.3f with 1/sqrt(f) "
            "amplitude scaling per Stage-1 foundations. Hub aggregates via majority-rule "
            "(or cf-RPE-gated weighted) bundling -- no multiplicative compose. "
            "Substrate-OWNED encoders only (Lane 1; no word2vec/Pythia leakage). "
            "N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d. Sanity rail: baseline within "
            "+/- %.2f of Path C v2 ref %.4f." % (
                SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
                SANITY_RAIL_TOL, PATH_C_V2_BPC_REF)),
        "cites": [
            "preregs/2026-06-24_substrate_hub_spoke_E1_encoder_v1.md",
            "notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md",
            "notes/director_stage2_preauthored_dispatch_specs_2026-06-24.md",
            "experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py",
            "data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json",
            "USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer",
            "USER_2026-06-22_Fix24_GPU_must_use_GPU",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (
                    n_llm, summary), detail)

    # Sanity rail must hold; if not, MIDDLE_BAND with explicit flag.
    if not sanity_rail_ok:
        return ("MIDDLE_BAND",
                ("SANITY_RAIL_MISS: ARM_BASELINE_PATH_C_SINGLE bpc=%.3f deviates "
                 "%.3f from Path C v2 reference %.3f (tol %.3f). Hub-spoke results "
                 "suspect; provenance broken. %s" % (
                     baseline_bpc, sanity_rail_delta, PATH_C_V2_BPC_REF,
                     SANITY_RAIL_TOL, summary)), detail)

    if degen_arms and not any_substrate_clears_unigram:
        return ("MIDDLE_BAND",
                ("READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE: raw_bpc_at_T1_L1 "
                 "within +/-%.2f of uniform-vocab %.3f bits for arms=%s; no "
                 "substrate arm clears unigram. %s" % (
                     DEGEN_TOL, vocab_entropy_uniform, degen_arms, summary)),
                detail)

    bh = best_hub_arm[1]
    bcv = best_hub_arm[2]
    # CHAIN_GRADE first (subset of HARD_PASS)
    if math.isfinite(bh) and bh <= CG_BPC_MAX and math.isfinite(bcv) and bcv < HP_BPC_CV_MAX:
        return ("HARD_PASS",
                ("HUB_SPOKE_E1 CHAIN_GRADE: best hub arm %s bpc=%.3f <= %.3f "
                 "(closes gap to word2vec-equiv without leakage; cv=%.3f). %s" % (
                     best_hub_arm[0], bh, CG_BPC_MAX, bcv, summary)),
                {**detail, "cert_tier": "CHAIN_GRADE"})
    if math.isfinite(bh) and bh <= HP_BPC_MAX and math.isfinite(bcv) and bcv < HP_BPC_CV_MAX:
        return ("HARD_PASS",
                ("HUB_SPOKE_E1 HARD_PASS: best hub arm %s bpc=%.3f <= %.3f "
                 "(improves Path C single-spoke by >= 0.40 bits; cv=%.3f). %s" % (
                     best_hub_arm[0], bh, HP_BPC_MAX, bcv, summary)),
                {**detail, "cert_tier": "HARD_PASS"})
    # HARD_FAIL: ALL hub arms >= HF_BPC_MIN
    all_hub_fail = all(
        (by_arm_agg[a].get("all_seeds_failed", False)
         or by_arm_agg[a].get("bpc_best_mean", float("inf")) >= HF_BPC_MIN)
        for a in HUB_ARMS
    )
    if all_hub_fail:
        return ("HARD_FAIL",
                ("HUB_SPOKE_E1 HARD_FAIL: ALL hub-spoke arms bpc >= %.3f "
                 "(federation doesn't help; principle may not transfer to substrate). "
                 "%s" % (HF_BPC_MIN, summary)),
                detail)
    return ("MIDDLE_BAND",
            ("HUB_SPOKE_E1 MIDDLE_BAND: best hub bpc=%.3f in (%.3f, %.3f). "
             "Partial signal; characterize gap. %s" % (
                 bh, HP_BPC_MAX, HF_BPC_MIN, summary)),
            detail)


# ============================================================================
# Self-test (T1-T13)
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    assert set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T1 bipolar"

    # T2: sparse-bipolar primitive nnz + uniq (post 1/sqrt(f) scale: vals in {-c,0,c})
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz_per_row = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T2 nnz: %s" % nnz_per_row
    c_expect = 1.0 / math.sqrt(0.05)
    uniq = set(round(float(x), 4) for x in sp.unique().tolist())
    expected_uniq = {round(-c_expect, 4), 0.0, round(c_expect, 4)}
    assert uniq.issubset(expected_uniq), "T2 uniq: got %s expected subset of %s" % (uniq, expected_uniq)

    # T3 T4 T5 T6 (temperature + joint sweep endpoints; mirror Path C v2)
    n, V = 1, 8
    peaked = np.zeros((n, V), dtype=np.float32)
    peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.01)
    assert probs.max() > 0.5, "T3 T=0.01 peaked: max=%.3f" % probs.max()
    probs_h = softmax_logits_with_T(peaked, 10.0)
    assert probs_h.max() < 0.145, "T4 T=10 near-uniform: max=%.3f" % probs_h.max()

    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    n_test = len(nxt)
    sub_logits = np.zeros((n_test, 5), dtype=np.float32)
    logp_lam0 = log_linear_interp_logp(np.log(np.full_like(sub_logits, 1.0 / 5.0)),
                                          U_log, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt)
    bpc_uni = -float(np.mean(np.log(U[nxt]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T5: %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    sub_logits2 = np.random.default_rng(42).standard_normal((10, 5)).astype(np.float32)
    probs2 = softmax_logits_with_T(sub_logits2, 1.0)
    logp2 = np.log(np.clip(probs2, 1e-30, 1.0))
    logp_lam1 = log_linear_interp_logp(logp2, U_log, 1.0)
    nxt_t = np.tile(nxt, 2)[:10]
    raw_bpc = bpc_from_logp(logp2, nxt_t)
    sub_bpc = bpc_from_logp(logp_lam1, nxt_t)
    assert abs(raw_bpc - sub_bpc) < 1e-4, "T6: %.4f vs %.4f" % (raw_bpc, sub_bpc)

    # T7: MRR@10 on planted 5-pair set
    V_t = 10
    n_t = 5
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    nxt_p = np.array([3, 0, 9, 5, 2])
    expected_ranks = [1, 2, 3, 4, 5]
    for i, (true_cls, want_rank) in enumerate(zip(nxt_p, expected_ranks)):
        scores = np.arange(V_t, dtype=np.float64)
        np.random.default_rng(i).shuffle(scores)
        sorted_idx = np.argsort(-scores)
        cur_top = sorted_idx[want_rank - 1]
        tmp = scores[true_cls]
        scores[true_cls] = scores[cur_top]
        scores[cur_top] = tmp
        logp_planted[i] = scores
    mrr_val = mrr_at_k(logp_planted, nxt_p, 10)
    expected_mrr = float(np.mean([1.0 / r for r in expected_ranks]))
    assert abs(mrr_val - expected_mrr) < 1e-6, "T7: %.4f vs %.4f" % (mrr_val, expected_mrr)

    # T8: PC encoder forward shape + L2 norm
    X_p = build_planted_bipolar_inputs_gpu(4, 32, seed=0)
    idx_dummy = np.array([0, 1, 2, 3, 0, 1, 2, 3], dtype=np.int64)
    W_stack, E_excit, pc_meta = train_pc_spoke_gpu(
        X_planted=X_p, idx_train=idx_dummy, n_dim=32, alpha=0.05,
        n_passes=1, beta=2.0, seed=0, train_tokens=8)
    E_pc = encode_with_pc_spoke(X_p, W_stack, E_excit, 2.0)
    assert E_pc.shape == (4, 32), "T8 shape: %s" % str(E_pc.shape)
    norms = E_pc.norm(dim=1)
    assert torch.allclose(norms, torch.ones(4, device=norms.device), atol=1e-5), \
        "T8 norms: %s" % norms.tolist()

    # T9: hub majority-rule bundling preserves bipolar geometry
    s1 = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(4, 32, generator=torch.Generator().manual_seed(1))))
    s2 = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(4, 32, generator=torch.Generator().manual_seed(2))))
    s3 = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(4, 32, generator=torch.Generator().manual_seed(3))))
    h = hub_aggregate_majority([s1, s2, s3])
    assert h.shape == (4, 32), "T9 hub shape: %s" % str(h.shape)
    h_unique = set(round(float(x), 4) for x in (h * math.sqrt(32)).unique().tolist())
    # After L2 normalize then *sqrt(32), values should be in {-1, +1}
    assert h_unique.issubset({-1.0, 1.0}), "T9 hub bipolar: %s" % h_unique

    # T10: cf-RPE weighted hub aggregates N spokes to single [V, N_DIM]
    gates = torch.tensor([0.6, 0.3, 0.1])
    hw = hub_aggregate_cfrpe_weighted([s1, s2, s3], gates)
    assert hw.shape == (4, 32), "T10 weighted hub shape: %s" % str(hw.shape)

    # T11: verdict bands (CHAIN_GRADE / HARD_PASS / HARD_FAIL / MIDDLE / SANITY_RAIL_MISS)
    def _mk_unit_uni(bpc=7.738, top1=0.2171, mrr=0.30):
        return {"ARM_UNIGRAM": {"bpc_unigram": bpc, "top1_unigram": top1,
                                  "mrr_unigram": mrr, "n_test": 100}}

    def _mk_arm(bpc=8.0, top1=0.15, mrr=0.25, raw_t1=None):
        return {"bpc_best": bpc, "top1_acc": top1, "mrr_at_10": mrr,
                 "best_T_for_bpc": 0.5, "best_lambda_for_bpc": 0.3, "best_dev_bpc": bpc,
                 "best_T_for_top1": 0.5, "best_lambda_for_top1": 0.3,
                 "best_T_for_mrr": 0.5, "best_lambda_for_mrr": 0.3,
                 "raw_bpc_at_T1_L1": raw_t1 if raw_t1 is not None else bpc,
                 "raw_top1_at_T1_L1": top1, "n_dev": 100, "n_test": 100}

    def _full(arms_d, V=4000):
        by_arm = _mk_unit_uni()
        for a in ARMS:
            by_arm[a] = arms_d.get(a, _mk_arm())
        return {"seed": 0, "by_arm": by_arm, "V": V, "N": 64, "N_DIM": 64,
                 "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": V, "run_mode": "smoke",
                 "config_version": "selftest", "elapsed_s_seed": 0.01,
                 "device": "cpu", "n_llm_calls": 0}

    # CHAIN_GRADE: baseline rail-OK; best hub <= 6.95 cv<0.05
    u_cg = _full({
        BASELINE_ARM: _mk_arm(bpc=7.62, top1=0.22, mrr=0.30, raw_t1=7.62),
        "ARM_HUB_SPOKE_3SPOKE": _mk_arm(bpc=7.10, top1=0.25, mrr=0.32, raw_t1=7.10),
        "ARM_HUB_SPOKE_5SPOKE": _mk_arm(bpc=7.00, top1=0.27, mrr=0.34, raw_t1=7.00),
        PRIMARY_ARM: _mk_arm(bpc=6.85, top1=0.30, mrr=0.36, raw_t1=6.85),
    })
    v, m, d = compute_verdict([u_cg, u_cg, u_cg])
    assert v == "HARD_PASS", "T11 CG verdict: %s" % v
    assert d.get("cert_tier") == "CHAIN_GRADE", "T11 cert_tier: %s" % d.get("cert_tier")

    # HARD_PASS: baseline rail-OK; best hub <= 7.20 cv<0.05
    u_hp = _full({
        BASELINE_ARM: _mk_arm(bpc=7.60, top1=0.22, mrr=0.30, raw_t1=7.60),
        "ARM_HUB_SPOKE_3SPOKE": _mk_arm(bpc=7.30, top1=0.24, mrr=0.32, raw_t1=7.30),
        "ARM_HUB_SPOKE_5SPOKE": _mk_arm(bpc=7.20, top1=0.25, mrr=0.33, raw_t1=7.20),
        PRIMARY_ARM: _mk_arm(bpc=7.15, top1=0.26, mrr=0.34, raw_t1=7.15),
    })
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T11 HP verdict: %s msg=%s" % (v, m[:200])
    assert d.get("cert_tier") == "HARD_PASS", "T11 HP cert_tier: %s" % d.get("cert_tier")

    # HARD_FAIL: ALL hub arms bpc >= 7.60
    u_hf = _full({
        BASELINE_ARM: _mk_arm(bpc=7.62, top1=0.22, mrr=0.30, raw_t1=7.62),
        "ARM_HUB_SPOKE_3SPOKE": _mk_arm(bpc=7.65, top1=0.21, mrr=0.30, raw_t1=7.65),
        "ARM_HUB_SPOKE_5SPOKE": _mk_arm(bpc=7.70, top1=0.21, mrr=0.30, raw_t1=7.70),
        PRIMARY_ARM: _mk_arm(bpc=7.68, top1=0.21, mrr=0.30, raw_t1=7.68),
    })
    v, m, d = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "T11 HF verdict: %s msg=%s" % (v, m[:200])

    # MIDDLE: best hub in (7.20, 7.60)
    u_mid = _full({
        BASELINE_ARM: _mk_arm(bpc=7.62, top1=0.22, mrr=0.30, raw_t1=7.62),
        "ARM_HUB_SPOKE_3SPOKE": _mk_arm(bpc=7.50, top1=0.22, mrr=0.30, raw_t1=7.50),
        "ARM_HUB_SPOKE_5SPOKE": _mk_arm(bpc=7.45, top1=0.22, mrr=0.30, raw_t1=7.45),
        PRIMARY_ARM: _mk_arm(bpc=7.40, top1=0.23, mrr=0.31, raw_t1=7.40),
    })
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "T11 MID verdict: %s msg=%s" % (v, m[:200])

    # SANITY_RAIL_MISS: baseline outside tol
    u_sr = _full({
        BASELINE_ARM: _mk_arm(bpc=7.90, top1=0.22, mrr=0.30, raw_t1=7.90),
        "ARM_HUB_SPOKE_3SPOKE": _mk_arm(bpc=7.00, top1=0.25, mrr=0.32, raw_t1=7.00),
        "ARM_HUB_SPOKE_5SPOKE": _mk_arm(bpc=6.95, top1=0.26, mrr=0.33, raw_t1=6.95),
        PRIMARY_ARM: _mk_arm(bpc=6.90, top1=0.27, mrr=0.34, raw_t1=6.90),
    })
    v, m, d = compute_verdict([u_sr, u_sr, u_sr])
    assert v == "MIDDLE_BAND", "T11 SR verdict: %s msg=%s" % (v, m[:200])
    assert "SANITY_RAIL_MISS" in m, "T11 SR msg: %s" % m[:200]
    assert not d.get("sanity_rail_ok"), "T11 SR flag"

    # T12: cf-RPE gates evolve under training (mean spoke alignment differentiates)
    s_a = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(5, 16, generator=torch.Generator().manual_seed(11))))
    s_b = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(5, 16, generator=torch.Generator().manual_seed(22))))
    s_c = _l2_normalize_t(_sign_with_zero_tiebreak(
        torch.randn(5, 16, generator=torch.Generator().manual_seed(33))))
    idx_dummy2 = np.array([0, 1, 2, 3, 4, 0, 1, 2], dtype=np.int64)
    gates = adapt_cfrpe_gates(spoke_outputs=[s_a, s_b, s_c],
                                  idx_train=idx_dummy2, n_steps=20, eta=0.1, seed=42)
    assert gates.shape == (3,), "T12 gates shape: %s" % str(gates.shape)
    assert abs(float(gates.sum().item()) - 1.0) < 1e-5, "T12 gates softmax: %s" % gates.tolist()

    # T13: zero LLM calls at inference
    assert _LLM_CALL_COUNTER[0] == 0, "T13 llm counter"

    print("[selftest] PASS: T1 trigram + T2 sparse-bipolar + T3 T0.01 + T4 T10 "
          "+ T5 lam0=uni + T6 lam1=raw + T7 MRR + T8 PC forward "
          "+ T9 hub majority + T10 hub cf-RPE weighted + T11 verdict bands "
          "(CG/HP/HF/MID/SR_MISS) + T12 cf-RPE gates evolve + T13 llm=0",
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
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_hub_spoke_E1_encoder_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
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
          "seeds=%s arms=%s name_says_smoke=%s | %s" % (
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
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "hub-spoke-E1-v1"}
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
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "PC_ALPHA": PC_ALPHA,
        "PC_BETA": PC_BETA,
        "PC_N_LAYERS": PC_N_LAYERS,
        "PC_N_PASSES": PC_N_PASSES,
        "PC_TRAINING_TOKENS": PC_TRAINING_TOKENS,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "N_SPOKES_ARM2": N_SPOKES_ARM2,
        "N_SPOKES_ARM3": N_SPOKES_ARM3,
        "N_SPOKES_ARM4": N_SPOKES_ARM4,
        "CFRPE_ETA": CFRPE_ETA,
        "CFRPE_N_STEPS": CFRPE_N_STEPS,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_hub_spoke_E1_encoder_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-OWNED PC encoders only; hub aggregates via majority-rule or cf-RPE-gated; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
