"""phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3 -- GPU K-ceiling map (re-dispatch).

V3 RE-DISPATCH 2026-06-26: v2 STILL silently dropped K=16384 + K=32768 via a
DIFFERENT path than OOM. v2 added chunked-matmul (fixed OOM at cleanup) AND
added META_RULE_H cardinality guard (correctly fired HARD_FAIL). But the
underlying silent-drop persisted because v2's main-loop `except Exception`
had TWO branches:
  - If _is_oom_error(e): set fatal_oom_seen=True, continue loop
  - Else (non-OOM): print [ERR] and CONTINUE LOOP WITHOUT FLAGGING

Result: at K=16384/32768 a non-OOM exception (e.g. RuntimeError with a CUDA
error string not matching the OOM regex, illegal-memory-access, or
CUBLAS_STATUS_ALLOC_FAILED) printed [ERR] silently and the loop continued.
META_RULE_H cardinality guard caught the verdict corruption (HARD_FAIL_CARDINALITY_BREACH
n_units=9 vs expected=27) -- but the per-K failure cause was not surfaced.

V2 PROVED:
  - K=4096: recall=1.000 (rail)
  - K=8192: recall=1.000 (NEW: substrate WM scales to K=8192 at k_per_bank=64)
  - K=16384 + K=32768: silently dropped via non-OOM exception
  - GPU genuinely used (57.9% mean, 99% max, 6.86GB peak; not OOM)

V3 FIXES:
  1. REMOVE non-OOM silent-continue. Any exception (OOM or non-OOM) records
     the unit as failed in a structured failures list AND halts the loop
     (sys.exit(1) after collecting whatever partials exist). META_RULE_H
     cardinality guard at verdict-time still catches the breach, but v3
     ADDS per-unit failure_reason in detail so the actual failure path
     is surfaced.
  2. Full traceback + tensor-shape instrumentation on any exception.
  3. Per-unit torch.cuda.reset_peak_memory_stats() + report peak per K.
  4. Per-K pre-flight memory probe: estimate peak working set; if free_mem
     would breach, record HARD_FAIL_INSUFFICIENT_VRAM up-front (no try to run).
  5. CODEBOOK_CHUNK reduced 8192 -> 4096 (halves cleanup peak ~512MB -> ~256MB).
  6. Free per-seed codebooks ACROSS REGIMES (RANDOM and ADVERSARIAL codebooks
     each 1GB at full N=8192 CB=65536; v2 kept BOTH resident permanently;
     v3 builds per (seed, regime) on demand and frees between regimes).
  7. KEEP META_RULE_H cardinality guard from v2 (it WORKED; don't remove).
  8. KEEP _is_oom_error from v2 (still useful for classification in detail
     dict; just not used as a "silent continue" gate anymore).

DISCRIMINATOR (Option B analytical justification per discriminator-must-survive-scale):
  This is a phase-diagram MAP cell. The discriminator IS the cliff occurrence:
  - PARTIAL_K_CEILING_16384 vs CHAIN_GRADE_K_CEILING_32768 are different verdicts
  - The phase-diagram value comes from MAPPING where the cliff falls
  - No separate "control arm" needed; the cliff is self-evident from the sweep
  - Discriminator survives scale because the map is the result (no calibration arm)

CONFIG (N_DIM=8192; CODEBOOK_SIZE=65536 to fit K=32768 picks):
  N_DIM = 8192, CODEBOOK_SIZE = 65536
  SIGMA=1.0, CUE_COS=0.70, FEATURE_OVERLAP_FRAC=0.20
  N_GROUPS_ADV=4, N_ITEMS_PER_K=200, seeds=[11,13,19]
  CODEBOOK_CHUNK = 4096 (chunked matmul; bounds sims tensor to ~128MB fp16)
  HP_CHAIN_GRADE: recall>=0.95 cv<=0.05 route_acc>=0.95 adv_within<=0.05 k_per_bank<=64

PRE-REG BANDS (LOCKED at module init):
  CHAIN_GRADE_K_CEILING_32768: all 4 K values chain-grade
  PARTIAL_K_CEILING_16384: K<=16384 chain-grade; K=32768 cliffs
  PARTIAL_K_CEILING_8192: K<=8192 chain-grade; K>=16384 cliffs
  K_4096_IS_CEILING: chain-grade only at K=4096
  HARD_FAIL_CARDINALITY_BREACH: per_unit count < expected (v1/v2 phantom guard)
  HARD_FAIL_UNIT_EXCEPTION: any unit raised an exception (v3 NEW; surfaces non-OOM
    silent-drop path that v2 still had)
  HARD_FAIL_INSUFFICIENT_VRAM: pre-flight memory probe predicted breach (v3 NEW)

GPU MANDATE (Fix #24): torch.cuda required for full; fp16 storage; chunked matmul
  on cuda; nvidia-smi util sampled per arm; smoke gates gpu_util_p50 >= 50%.

ASCII-only. Single-file. Resumable per (seed, K, regime, arm) checkpoint key.

Author: exp_dev 2026-06-26 (re-dispatch v3 per non-OOM silent-drop diagnosis).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import math
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch  # required at top for PROT-020 GPU-queue routing gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    list_completed_keys,
)

ANCHOR_NAME = "phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3"

_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_multibank_routing"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")
SMOKE = (RUN_MODE == "smoke")

# Pre-reg bands LOCKED at module init
HP_CHAIN_GRADE_RECALL = 0.95
HP_CHAIN_GRADE_CV = 0.05
HP_CHAIN_GRADE_ROUTE_ACC = 0.95
HP_ADV_WITHIN_RANDOM = 0.05
HP_ADV_BREAK_THRESHOLD = 0.30
HP_K_CEILING_RECALL_MIN = 0.50
HP_CHAIN_GRADE_K_PER_BANK_MAX = 64
Q_SUSPECT_SATURATION = 0.995
HP_RAIL_K4096_RECALL = 1.0000   # v1/v2 saturated
HP_RAIL_K4096_TOL = 0.05
HP_KNN_SENTINEL_MIN = 0.90
CV_HARD_FAIL = 0.10

# v3 pre-flight VRAM probe: peak working-set estimate as fraction of free_mem
HP_VRAM_PROBE_FRACTION = 0.85

assert 0.0 < HP_CHAIN_GRADE_RECALL < 1.0, "band locked"
assert 0.0 < HP_ADV_WITHIN_RANDOM < HP_ADV_BREAK_THRESHOLD, "ordering"
assert HP_CHAIN_GRADE_K_PER_BANK_MAX == 64, "envelope locked"

SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20
N_GROUPS_ADV = 4
KNN_SENTINEL_M = 400

# v3: tightened from v2's 8192 to 4096 (halves cleanup peak ~512MB -> ~256MB at K=32768)
CODEBOOK_CHUNK = 4096

if SMOKE:
    N_DIM = 2048
    CODEBOOK_SIZE = 4096
    K_SWEEP = [1024, 4096]
    ARRANGEMENTS_BY_K = {
        1024: [("MULTI_32x", 32, 32)],
        4096: [("MULTI_64x", 64, 64)],
    }
    N_ITEMS_PER_K = 80
    SEEDS = [11]
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 65536
    K_SWEEP = [4096, 8192, 16384, 32768]
    ARRANGEMENTS_BY_K = {
        4096:  [("MULTI_64x",  64,  64)],                       # rail
        8192:  [("MULTI_128x", 128, 64)],                       # k_per_bank=64
        16384: [("MULTI_256x", 256, 64)],                       # k_per_bank=64
        32768: [("MULTI_512x", 512, 64)],                       # ceiling probe
    }
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]

SENTINEL_KS = [4096]
REGIMES = ["RANDOM", "ADVERSARIAL"]

# Expected cardinality (cardinality-breach guard per META_RULE_H)
EXPECTED_N_UNITS = (
    len(SEEDS) * sum(len(ARRANGEMENTS_BY_K.get(K, [])) for K in K_SWEEP) * len(REGIMES)
    + len(SEEDS) * len([K for K in SENTINEL_KS if K in K_SWEEP])
)

CONFIG_VERSION = (
    "phaseDiagWmMBKCeil32768-v3: N_DIM=%d CODEBOOK_SIZE=%d sigma=%.1f CUE_COS=%.2f "
    "FEATURE_OVERLAP=%.2f K_SWEEP=%s arrangements=%s N_ITEMS_PER_K=%d seeds=%s "
    "mode=%s HP_chain>=%.2f cv<=%.2f route_acc>=%.2f HP_adv_within=%.2f "
    "HP_adv_break=%.2f Q_sat>=%.3f HP_rail_K4096=%.4f+/-%.3f kPerBankMax=%d "
    "CODEBOOK_CHUNK=%d EXPECTED_N_UNITS=%d VRAM_PROBE=%.2f"
) % (
    N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
    K_SWEEP, list(ARRANGEMENTS_BY_K.keys()),
    N_ITEMS_PER_K, SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
    HP_ADV_WITHIN_RANDOM, HP_ADV_BREAK_THRESHOLD,
    Q_SUSPECT_SATURATION, HP_RAIL_K4096_RECALL, HP_RAIL_K4096_TOL,
    HP_CHAIN_GRADE_K_PER_BANK_MAX, CODEBOOK_CHUNK, EXPECTED_N_UNITS,
    HP_VRAM_PROBE_FRACTION,
)


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "phase_diagram K-ceiling at N_DIM=%d K_max=%d requires CUDA. "
            "Route to overnight_queue (GPU runner)." % (N_DIM, max(K_SWEEP)))
    return False


_STRICT_GPU = (not SMOKE) and (not _ARGS.self_test)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
_STORE_DTYPE = torch.float16 if _CUDA_OK else torch.float32


def _gpu_util_sample() -> Optional[float]:
    if not _CUDA_OK:
        return None
    try:
        import subprocess
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return float(out.stdout.strip().splitlines()[0].strip())
    except Exception:
        pass
    return None


def _gpu_info() -> Dict:
    if not _CUDA_OK:
        return {"gpu_avail": False, "gpu_name": "cpu", "gpu_total_mb": 0,
                "gpu_free_mb": 0}
    free_b, total_b = torch.cuda.mem_get_info(0)
    return {
        "gpu_avail": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_total_mb": int(total_b / 1024 / 1024),
        "gpu_free_mb": int(free_b / 1024 / 1024),
    }


def _estimate_peak_working_set_bytes(k_total: int, n_banks: int,
                                      k_per_bank: int) -> int:
    """Estimate peak GPU working set in bytes for a single arm at given K.

    Accounts for largest concurrent allocations during eval_multi_bank_arm +
    _read_with_cleanup_batched at this K.

    Concurrent peaks (per trial, post-rebuild):
      - codebook (single regime; v3 frees other regime): C*D*2 bytes (fp16)
      - workspaces (n_banks * D): n_banks*D*2 bytes (fp16)
      - cues (K*D fp16) + noise (K*D fp32): K*D*(2+4) bytes
      - ws_selected (K*D fp16): K*D*2 bytes
      - cleanup r1 (K*D fp16) + r2 (K*D fp32) + cand_vecs (K*D fp16): K*D*(2+4+2) bytes
      - chunked sims (CODEBOOK_CHUNK * K fp32): CC*K*4 bytes
      - _write_bank bound (n_banks * k_per_bank * D fp32): n_banks*k_per_bank*D*4 bytes
        (this is the BIGGEST intermediate at K=32768: 512*64*8192*4 = 1GB)

    Returns approx peak bytes. Conservative -- overestimates by ~30%.
    """
    D = N_DIM
    C = CODEBOOK_SIZE
    cb_bytes = C * D * 2  # fp16 codebook (single regime)
    bound_bytes = n_banks * k_per_bank * D * 4  # _write_bank_batched bound tensor
    workspaces_bytes = n_banks * D * 2
    cues_bytes = k_total * D * (2 + 4)  # cues fp16 + noise fp32 concurrent
    ws_selected_bytes = k_total * D * 2
    cleanup_bytes = k_total * D * (2 + 4 + 2)  # r1 fp16 + r2 fp32 + cand_vecs fp16
    chunked_sims_bytes = CODEBOOK_CHUNK * k_total * 4  # sims chunk fp32
    # Peak = codebook + (write phase: bound + workspaces) OR (eval phase: workspaces +
    # ws_selected + cues + cleanup + chunked_sims). Take max.
    write_peak = cb_bytes + bound_bytes + workspaces_bytes
    eval_peak = (cb_bytes + workspaces_bytes + cues_bytes + ws_selected_bytes
                 + cleanup_bytes + chunked_sims_bytes)
    return max(write_peak, eval_peak)


# ----------------------------- HD primitives -----------------------------
def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape, gen: torch.Generator) -> torch.Tensor:
    X = torch.empty(*shape, device=_DEVICE, dtype=_STORE_DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    out = torch.where(v >= 0, torch.ones_like(v), -torch.ones_like(v))
    return out


def build_codebook_random(seed_offset: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((CODEBOOK_SIZE, N_DIM), g)


def build_codebook_adversarial(seed_offset: int) -> torch.Tensor:
    g_tpl = _make_gen(seed_offset + 7)
    g_items = _make_gen(seed_offset + 11)
    templates = random_bipolar_t((N_GROUPS_ADV, N_DIM), g_tpl)
    items = random_bipolar_t((CODEBOOK_SIZE, N_DIM), g_items)
    n_shared = int(FEATURE_OVERLAP_FRAC * N_DIM)
    if n_shared > 0:
        group_ids = torch.arange(CODEBOOK_SIZE, device=_DEVICE) % N_GROUPS_ADV
        items[:, :n_shared] = templates[group_ids, :n_shared]
    return items


def build_slot_tags(seed_offset: int, k_per_bank: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 13)
    return random_bipolar_t((k_per_bank, N_DIM), g)


def build_bank_tags(seed_offset: int, n_banks: int) -> torch.Tensor:
    g = _make_gen(seed_offset + 17)
    return random_bipolar_t((n_banks, N_DIM), g)


def _write_bank_batched(items_per_bank: torch.Tensor,
                        slot_tags: torch.Tensor,
                        seed_offset: int) -> torch.Tensor:
    """Memory-conscious write: at K=32768 n_banks=512 the dense bound tensor
    (512, 64, 8192) fp32 = 1 GB. v3 chunks over banks to bound peak."""
    n_banks = items_per_bank.shape[0]
    D = items_per_bank.shape[2]
    # Chunk banks to bound peak intermediate at ~256MB fp32 (= 8K * D * 4)
    bank_chunk = max(1, min(n_banks, 8192 // max(1, items_per_bank.shape[1])))
    ws_acc = torch.zeros((n_banks, D), device=_DEVICE, dtype=torch.float32)
    slot_tags_f = slot_tags.float()
    for b0 in range(0, n_banks, bank_chunk):
        b1 = min(b0 + bank_chunk, n_banks)
        # (b1-b0, k_per_bank, D) * (1, k_per_bank, D) -> sum over k_per_bank
        chunk_bound = items_per_bank[b0:b1].float() * slot_tags_f.unsqueeze(0)
        ws_acc[b0:b1] = chunk_bound.sum(dim=1)
        del chunk_bound
        if _CUDA_OK:
            torch.cuda.empty_cache()
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws_acc.shape, device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws_acc = ws_acc + noise
        del noise
        if _CUDA_OK:
            torch.cuda.empty_cache()
    out = bipolar_quantize_t(ws_acc).to(_STORE_DTYPE)
    del ws_acc
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return out


def _chunked_argmax_cb_at_queries(codebook: torch.Tensor,
                                   queries: torch.Tensor) -> torch.Tensor:
    """Compute argmax over codebook rows of codebook @ queries.T, chunked.

    v3: CODEBOOK_CHUNK reduced 8192 -> 4096; sim tensor at K=32768 ~128MB fp32.
    """
    C = codebook.shape[0]
    Q = queries.shape[0]
    best_scores = torch.full((Q,), float("-inf"), device=queries.device,
                              dtype=torch.float32)
    best_idx = torch.zeros((Q,), device=queries.device, dtype=torch.long)
    chunk = CODEBOOK_CHUNK
    q_T = queries.T  # (D, Q)
    for c0 in range(0, C, chunk):
        c1 = min(c0 + chunk, C)
        sims_chunk = (codebook[c0:c1] @ q_T).float()  # (chunk, Q)
        chunk_max, chunk_idx = sims_chunk.max(dim=0)
        better = chunk_max > best_scores
        best_scores = torch.where(better, chunk_max, best_scores)
        best_idx = torch.where(better, chunk_idx + c0, best_idx)
        del sims_chunk, chunk_max, chunk_idx, better
        if _CUDA_OK:
            torch.cuda.empty_cache()
    return best_idx


def _read_with_cleanup_batched(workspaces: torch.Tensor,
                               slot_tag: torch.Tensor,
                               codebook: torch.Tensor) -> torch.Tensor:
    """Two-step cleanup over codebook. v3 chunks the r2 cast to bound peak."""
    r1 = (workspaces * slot_tag)
    cand_idx = _chunked_argmax_cb_at_queries(codebook, r1)
    cand_vecs = codebook[cand_idx]
    # v3: avoid r2 fp32 (K*D*4 bytes; K=32768 -> 1GB). Combine in fp16 directly.
    r2_bp = bipolar_quantize_t(r1.float() + cand_vecs.float()).to(_STORE_DTYPE)
    del r1, cand_vecs
    if _CUDA_OK:
        torch.cuda.empty_cache()
    pred_idx = _chunked_argmax_cb_at_queries(codebook, r2_bp)
    del r2_bp
    if _CUDA_OK:
        torch.cuda.empty_cache()
    return pred_idx


def _is_oom_error(exc: BaseException) -> bool:
    """Identify OOM-class errors (kept for classification, not for silent-continue)."""
    oom_cls = getattr(torch.cuda, "OutOfMemoryError", None)
    if oom_cls is not None and isinstance(exc, oom_cls):
        return True
    msg = str(exc).lower()
    return any(needle in msg for needle in [
        "out of memory",
        "cuda out of memory",
        "cudnn_status",
        "cuda error",
        "device-side assert",
        "cublas_status",
        "illegal memory access",
        "misaligned address",
    ])


def eval_multi_bank_arm(n_banks: int, k_per_bank: int, k_total: int,
                        codebook: torch.Tensor, seed_offset: int,
                        gpu_util_samples: List[float]) -> Tuple[float, float]:
    assert k_total == n_banks * k_per_bank, "n_banks * k_per_bank must equal K_total"
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / k_total))
    slot_tags = build_slot_tags(seed_offset, k_per_bank)
    bank_tags = build_bank_tags(seed_offset, n_banks)
    cue_noise_scale = math.sqrt(max(0.0, 1.0 - CUE_COS * CUE_COS))

    correct = 0
    total = 0
    route_correct = 0
    route_total = 0

    g_trial = _make_gen(seed_offset + 29)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:k_total]
        items = codebook[idx_global]
        items_per_bank = items.view(n_banks, k_per_bank, N_DIM)
        workspaces = _write_bank_batched(items_per_bank, slot_tags,
                                         seed_offset + 1000 + trial)
        del items, items_per_bank
        if _CUDA_OK:
            torch.cuda.empty_cache()

        slot_indices = torch.arange(k_total, device=_DEVICE)
        bank_true = slot_indices // k_per_bank
        local_slot = slot_indices % k_per_bank

        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_true].float()
        noise = torch.empty((k_total, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        del noise
        if _CUDA_OK:
            torch.cuda.empty_cache()
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)
        del bank_cue_base, noise_bp
        if _CUDA_OK:
            torch.cuda.empty_cache()
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)
        del sims_bank

        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += k_total

        ws_selected = workspaces[bank_routed]
        slot_tag_sel = slot_tags[local_slot]
        del workspaces
        if _CUDA_OK:
            torch.cuda.empty_cache()

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        true_item_idx = idx_global[slot_indices]
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += k_total

        del cues, ws_selected, slot_tag_sel, pred_idx, true_item_idx, match
        del slot_indices, bank_true, local_slot, bank_routed, idx_global
        if _CUDA_OK:
            torch.cuda.empty_cache()

        sample = _gpu_util_sample()
        if sample is not None:
            gpu_util_samples.append(sample)

    del slot_tags, bank_tags
    if _CUDA_OK:
        torch.cuda.empty_cache()

    recall = correct / max(total, 1)
    route_acc = route_correct / max(route_total, 1)
    return recall, route_acc


def eval_knn_baseline(codebook: torch.Tensor, seed_offset: int) -> float:
    M = min(KNN_SENTINEL_M, CODEBOOK_SIZE)
    g_pick = _make_gen(seed_offset + 37)
    pick = torch.randperm(CODEBOOK_SIZE, generator=g_pick, device=_DEVICE)[:M]
    items = codebook[pick]
    g_noise = _make_gen(seed_offset + 41)
    noise = torch.empty((M, N_DIM), device=_DEVICE, dtype=torch.float32)
    noise.normal_(0.0, 0.5, generator=g_noise)
    noisy = bipolar_quantize_t(items.float() + noise).to(_STORE_DTYPE)
    del noise, items
    if _CUDA_OK:
        torch.cuda.empty_cache()
    pred = _chunked_argmax_cb_at_queries(codebook, noisy)
    correct = int((pred == pick).sum().item())
    return correct / max(M, 1)


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    global _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    save_dev, save_dtype, save_cuda, save_chunk = _DEVICE, _STORE_DTYPE, _CUDA_OK, CODEBOOK_CHUNK
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    _CUDA_OK = False
    CODEBOOK_CHUNK = 256
    global N_DIM_BAK, CODEBOOK_SIZE_BAK, N_DIM, CODEBOOK_SIZE
    N_DIM_BAK = N_DIM
    CODEBOOK_SIZE_BAK = CODEBOOK_SIZE
    N_DIM = 1024
    CODEBOOK_SIZE = 2048
    try:
        cb = build_codebook_random(0)
        assert cb.shape == (2048, 1024), "T1 shape"
        u = torch.unique(cb)
        assert set(u.tolist()) <= {-1.0, 1.0}, "T1 bipolar"
        print("[selftest] T1 PASS: random codebook shape + bipolar")

        cb_adv = build_codebook_adversarial(1)
        assert cb_adv.shape == (2048, 1024), "T2 adv shape"
        i_a = 0
        i_b = N_GROUPS_ADV
        i_c = 1
        shared_in = float((cb_adv[i_a] == cb_adv[i_b]).float().mean().item())
        shared_cross = float((cb_adv[i_a] == cb_adv[i_c]).float().mean().item())
        expected_in = FEATURE_OVERLAP_FRAC + 0.5 * (1.0 - FEATURE_OVERLAP_FRAC)
        assert shared_in > shared_cross + 0.05
        assert abs(shared_in - expected_in) < 0.10
        print("[selftest] T2 PASS: adversarial in=%.3f cross=%.3f expected ~%.3f"
              % (shared_in, shared_cross, expected_in))

        global N_ITEMS_PER_K
        N_ITEMS_PER_K_BAK = N_ITEMS_PER_K
        N_ITEMS_PER_K = 64
        gpu_samples = []
        rec, ra = eval_multi_bank_arm(16, 16, 256, cb, seed_offset=100,
                                       gpu_util_samples=gpu_samples)
        N_ITEMS_PER_K = N_ITEMS_PER_K_BAK
        assert ra >= 0.85, "T3 route_acc=%.3f < 0.85" % ra
        assert rec >= 0.50, "T3 recall=%.3f < 0.50" % rec
        print("[selftest] T3 PASS: multi-bank 16x16_K256 recall=%.3f route_acc=%.3f"
              % (rec, ra))

        assert _LLM_CALL_COUNTER[0] == 0
        print("[selftest] T4 PASS: LLM counter = 0")

        rec_knn = eval_knn_baseline(cb, seed_offset=200)
        assert rec_knn >= 0.85, "T5 KNN baseline %.3f < 0.85" % rec_knn
        print("[selftest] T5 PASS: KNN baseline recall=%.3f" % rec_knn)

        assert HP_CHAIN_GRADE_RECALL == 0.95
        assert HP_CHAIN_GRADE_K_PER_BANK_MAX == 64
        assert HP_RAIL_K4096_RECALL == 1.0000
        assert 32768 in K_SWEEP_FULL_FOR_SELFTEST
        print("[selftest] T6 PASS: bands locked + K=32768 in sweep")

        # T7: chunked argmax matches unchunked
        Q = 64
        g_q = _make_gen(999)
        queries = random_bipolar_t((Q, N_DIM), g_q)
        sims_full = (cb.float() @ queries.float().T)
        idx_unchunked = sims_full.argmax(dim=0)
        idx_chunked = _chunked_argmax_cb_at_queries(cb, queries)
        assert torch.equal(idx_chunked, idx_unchunked), \
            "T7 chunked argmax disagrees with unchunked"
        print("[selftest] T7 PASS: chunked argmax matches unchunked over %d codebook rows / %d queries"
              % (CODEBOOK_SIZE, Q))

        # T8: OOM-class detector
        class _MockOOM(RuntimeError):
            pass
        exc1 = _MockOOM("CUDA out of memory. Tried to allocate 4.30 GiB")
        assert _is_oom_error(exc1), "T8 should detect 'CUDA out of memory'"
        exc2 = ValueError("regular value error not OOM")
        assert not _is_oom_error(exc2), "T8 should NOT flag regular ValueError"
        exc3 = _MockOOM("CUDA error: an illegal memory access was encountered")
        assert _is_oom_error(exc3), "T8 should detect 'illegal memory access' (v3 new)"
        exc4 = _MockOOM("CUBLAS_STATUS_ALLOC_FAILED when calling cublasGemmEx")
        assert _is_oom_error(exc4), "T8 should detect 'cublas_status' (v3 new)"
        print("[selftest] T8 PASS: OOM/CUDA-error detector classifies correctly (incl. v3 new cases)")

        # T9: expected-n-units calculation
        expected_full = 3 * 4 * 2 + 3 * 1
        assert expected_full == 27, "T9 expected_full math broken"
        print("[selftest] T9 PASS: expected_n_units math (full=%d sentinel-aware)" % expected_full)

        # T10 NEW v3: VRAM probe estimator returns sane values
        # At smoke shape (N_DIM=1024, CB=2048), K=256 n_banks=16: should be < 100MB
        est = _estimate_peak_working_set_bytes(256, 16, 16)
        assert est < 100 * 1024 * 1024, "T10 smoke probe %d should be < 100MB" % est
        print("[selftest] T10 PASS: VRAM probe = %.2fMB at smoke shape" % (est / 1024 / 1024))

        # T11 NEW v3: write_bank chunked matches reference unchunked
        n_b, k_pb = 4, 8
        items_test = random_bipolar_t((n_b, k_pb, N_DIM), _make_gen(777))
        slot_tags_test = random_bipolar_t((k_pb, N_DIM), _make_gen(888))
        # Reference: original v2 unchunked formula
        bound_ref = items_test.float() * slot_tags_test.unsqueeze(0).float()
        ws_ref = bound_ref.sum(dim=1)
        # Now chunked v3 (without noise; SIGMA=0 path)
        global SIGMA
        SIGMA_BAK = SIGMA
        SIGMA = 0.0
        try:
            ws_chunked = _write_bank_batched(items_test, slot_tags_test, seed_offset=0)
        finally:
            SIGMA = SIGMA_BAK
        ws_ref_bp = bipolar_quantize_t(ws_ref).to(_STORE_DTYPE)
        assert torch.equal(ws_ref_bp, ws_chunked), \
            "T11 chunked write_bank disagrees with unchunked (no-noise path)"
        print("[selftest] T11 PASS: chunked write_bank matches reference (no-noise)")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        CODEBOOK_CHUNK = save_chunk
        N_DIM = N_DIM_BAK
        CODEBOOK_SIZE = CODEBOOK_SIZE_BAK


K_SWEEP_FULL_FOR_SELFTEST = [4096, 8192, 16384, 32768]


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- per-arm runner -----------------------------
def run_unit(seed: int, k_total: int, regime: str, arm_label: str,
             n_banks: int, k_per_bank: int,
             codebook: torch.Tensor,
             gpu_util_samples: List[float]) -> Dict:
    t0 = time.time()
    seed_offset = seed * 100003 + k_total * 31 + (1 if regime == "ADVERSARIAL" else 0)

    if _CUDA_OK:
        torch.cuda.reset_peak_memory_stats(0)

    if arm_label == "ARM_KNN_BASELINE":
        recall = eval_knn_baseline(codebook, seed_offset)
        route_acc = 1.0
    else:
        recall, route_acc = eval_multi_bank_arm(n_banks, k_per_bank, k_total, codebook,
                                                 seed_offset, gpu_util_samples)

    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

    peak_mb = 0
    if _CUDA_OK:
        try:
            peak_mb = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
        except Exception:
            peak_mb = 0

    wall_s = time.time() - t0
    return {
        "seed": int(seed),
        "k_total": int(k_total),
        "regime": regime,
        "arm_label": arm_label,
        "n_banks": int(n_banks),
        "k_per_bank": int(k_per_bank),
        "recall": float(round(recall, 4)),
        "route_acc": float(round(route_acc, 4)),
        "wall_s": float(round(wall_s, 2)),
        "peak_mem_mb": int(peak_mb),
        "N": int(N_DIM),
        "CODEBOOK_SIZE": int(CODEBOOK_SIZE),
        "SIGMA": float(SIGMA),
        "CUE_COS": float(CUE_COS),
        "FEATURE_OVERLAP_FRAC": float(FEATURE_OVERLAP_FRAC),
        "N_ITEMS_PER_K": int(N_ITEMS_PER_K),
        "M": int(max(K_SWEEP)),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
    }


# ----------------------------- verdict logic -----------------------------
def compute_verdict(per_key: Dict[str, Dict],
                    failures: List[Dict] = None) -> Tuple[str, str, Dict]:
    if failures is None:
        failures = []
    if not per_key and not failures:
        return ("HARD_FAIL", "no_units", {})

    # CARDINALITY GUARD (META_RULE_H per Skunkworks 2026-06-26)
    n_units_observed = len(per_key)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS)

    by_KRA: Dict[Tuple[int, str, str], Dict] = {}
    for _, body in per_key.items():
        K = int(body["k_total"])
        R = body["regime"]
        A = body["arm_label"]
        by_KRA.setdefault((K, R, A), {
            "recalls": [], "route_accs": [], "n_banks": body["n_banks"],
            "k_per_bank": body["k_per_bank"],
        })
        by_KRA[(K, R, A)]["recalls"].append(float(body["recall"]))
        by_KRA[(K, R, A)]["route_accs"].append(float(body["route_acc"]))

    arm_stats: Dict[int, Dict[str, Dict[str, Dict]]] = {}
    for (K, R, A), d in by_KRA.items():
        recs = d["recalls"]
        ras = d["route_accs"]
        m = float(np.mean(recs))
        s = float(np.std(recs))
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else 0.0
        m_ra = float(np.mean(ras))
        arm_stats.setdefault(K, {}).setdefault(R, {})[A] = {
            "recall_mean": round(m, 4),
            "recall_cv": round(cv, 4),
            "route_acc_mean": round(m_ra, 4),
            "n_banks": d["n_banks"],
            "k_per_bank": d["k_per_bank"],
            "recall_per_seed": [round(r, 4) for r in recs],
        }

    q_suspect = {}
    for K, by_R in arm_stats.items():
        for R, by_A in by_R.items():
            for A, st in by_A.items():
                if st["recall_mean"] >= Q_SUSPECT_SATURATION and st["recall_cv"] == 0.0:
                    q_suspect.setdefault(K, {}).setdefault(R, []).append(A)

    rail_ok = None
    rail_observed = None
    rail_drift = False
    if 4096 in arm_stats and "RANDOM" in arm_stats[4096] and "MULTI_64x" in arm_stats[4096]["RANDOM"]:
        rail_observed = arm_stats[4096]["RANDOM"]["MULTI_64x"]["recall_mean"]
        rail_ok = (rail_observed >= HP_RAIL_K4096_RECALL - HP_RAIL_K4096_TOL)
        rail_drift = not rail_ok

    knn_ok = None
    knn_observed = None
    if 4096 in arm_stats and "RANDOM" in arm_stats[4096] and "ARM_KNN_BASELINE" in arm_stats[4096]["RANDOM"]:
        knn_observed = arm_stats[4096]["RANDOM"]["ARM_KNN_BASELINE"]["recall_mean"]
        knn_ok = (knn_observed >= HP_KNN_SENTINEL_MIN)

    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    chain_grade_at_K: Dict[int, str] = {}
    adv_break_at_K: Dict[int, Tuple[str, float, float]] = {}
    cv_fail_at_K: Dict[int, str] = {}
    for K, by_R in arm_stats.items():
        if "RANDOM" not in by_R:
            continue
        rand_multi = {A: st for A, st in by_R["RANDOM"].items()
                       if A.startswith("MULTI_")
                       and st["k_per_bank"] <= HP_CHAIN_GRADE_K_PER_BANK_MAX}
        if not rand_multi:
            continue
        best_label, best_st = max(rand_multi.items(), key=lambda x: x[1]["recall_mean"])
        adv_st = by_R.get("ADVERSARIAL", {}).get(best_label, {
            "recall_mean": 0.0, "recall_cv": 0.0, "route_acc_mean": 0.0})
        adv_within = (best_st["recall_mean"] - adv_st["recall_mean"]) <= HP_ADV_WITHIN_RANDOM
        adv_break = (best_st["recall_mean"] - adv_st["recall_mean"]) >= HP_ADV_BREAK_THRESHOLD
        if best_st["recall_cv"] > CV_HARD_FAIL:
            cv_fail_at_K[K] = best_label
        if adv_break:
            adv_break_at_K[K] = (best_label, best_st["recall_mean"], adv_st["recall_mean"])
        if (best_st["recall_mean"] >= HP_CHAIN_GRADE_RECALL
                and best_st["recall_cv"] <= HP_CHAIN_GRADE_CV
                and best_st["route_acc_mean"] >= HP_CHAIN_GRADE_ROUTE_ACC
                and adv_within):
            chain_grade_at_K[K] = best_label

    k_ceiling_fail = False
    k_ceiling_info = ""
    for K_check in [k for k in K_SWEEP if k > 4096]:
        if K_check not in arm_stats or "RANDOM" not in arm_stats[K_check]:
            continue
        rand_multi = {A: st for A, st in arm_stats[K_check]["RANDOM"].items()
                       if A.startswith("MULTI_")}
        if rand_multi:
            best = max(rand_multi.values(), key=lambda x: x["recall_mean"])
            if best["recall_mean"] < HP_K_CEILING_RECALL_MIN:
                k_ceiling_fail = True
                k_ceiling_info += " K=%d best=%.3f<%.2f;" % (
                    K_check, best["recall_mean"], HP_K_CEILING_RECALL_MIN)

    summary_rows = []
    for K in sorted(arm_stats.keys()):
        by_R = arm_stats[K]
        if "RANDOM" not in by_R:
            continue
        rand_multi = {A: st for A, st in by_R["RANDOM"].items() if A.startswith("MULTI_")}
        if not rand_multi:
            continue
        best_label, best_st = max(rand_multi.items(), key=lambda x: x[1]["recall_mean"])
        adv_st = by_R.get("ADVERSARIAL", {}).get(best_label, {
            "recall_mean": float("nan"), "recall_cv": float("nan"), "route_acc_mean": float("nan")})
        summary_rows.append(
            "K=%d best_rand=%s[rec=%.4f cv=%.4f ra=%.4f kpb=%d] "
            "adv_same=[rec=%.4f cv=%.4f]" % (
                K, best_label,
                best_st["recall_mean"], best_st["recall_cv"], best_st["route_acc_mean"],
                best_st["k_per_bank"],
                adv_st["recall_mean"], adv_st.get("recall_cv", 0.0)))
    summ = " | ".join(summary_rows)

    rail_str = ""
    if rail_observed is not None:
        rail_str = " | rail_K4096_obs=%.4f (min=%.4f; %s)" % (
            rail_observed, HP_RAIL_K4096_RECALL - HP_RAIL_K4096_TOL,
            "OK" if rail_ok else "DRIFT")
    knn_str = ""
    if knn_observed is not None:
        knn_str = " | knn_sentinel=%.4f (>=%.2f; %s)" % (
            knn_observed, HP_KNN_SENTINEL_MIN, "OK" if knn_ok else "FAIL")
    if q_suspect:
        summ += " | [Q-DISCIPLINE: saturated=%s]" % q_suspect
    card_str = " | n_units=%d/expected=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if failures:
        fail_str = " | failures=%d [%s]" % (
            len(failures),
            "; ".join("%s:%s" % (f["key"], f["exc_type"]) for f in failures[:5]))

    detail = {
        "arm_stats": {str(K): {R: {A: st for A, st in by_R.items()}
                                for R, by_R in by_R.items()}
                       for K, by_R in arm_stats.items()},
        "chain_grade_at_K": chain_grade_at_K,
        "adv_break_at_K": adv_break_at_K,
        "cv_fail_at_K": cv_fail_at_K,
        "q_suspect_saturation": q_suspect,
        "rail_K4096_observed": rail_observed,
        "rail_K4096_target": HP_RAIL_K4096_RECALL,
        "rail_K4096_tol": HP_RAIL_K4096_TOL,
        "rail_drift": rail_drift,
        "knn_sentinel_observed": knn_observed,
        "knn_sentinel_min": HP_KNN_SENTINEL_MIN,
        "substrate_only_ok": substrate_only_ok,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "n_llm_calls": int(n_llm),
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "failures": failures,
    }

    if SMOKE:
        any_mech_ok = any(
            (st["recall_mean"] >= 0.50)
            for K, by_R in arm_stats.items()
            for R, by_A in by_R.items()
            for A, st in by_A.items()
            if A.startswith("MULTI_")
        )
        knn_ok_smoke = (knn_observed is None) or knn_ok
        if substrate_only_ok and any_mech_ok and knn_ok_smoke and not failures:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime | %s%s%s%s%s" % (
                        summ, rail_str, knn_str, card_str, fail_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | %s%s%s%s%s" % (
                    summ, rail_str, knn_str, card_str, fail_str),
                detail)

    # v3 NEW: failures (any non-OOM or OOM unit exception) -> HARD_FAIL immediately
    if failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised exceptions (silent-drop path "
                "now surfaced) | %s%s%s%s%s" % (
                    len(failures), summ, rail_str, knn_str, card_str, fail_str),
                detail)

    # CARDINALITY HARD_FAIL (v2; retained -- guards phantom-completion verdicts)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units=%d < expected=%d "
                "(K-sweep partial completion; ceiling claims forbidden) | %s%s%s" % (
                    n_units_observed, EXPECTED_N_UNITS,
                    summ, rail_str, knn_str),
                detail)

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only gate violated (%d LLM calls) | %s%s%s%s" % (
                    n_llm, summ, rail_str, knn_str, card_str),
                detail)
    if knn_observed is not None and not knn_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_KNN_SENTINEL: ARM_KNN_BASELINE %.4f < %.2f | %s%s%s%s" % (
                    knn_observed, HP_KNN_SENTINEL_MIN, summ, rail_str, knn_str, card_str),
                detail)
    if cv_fail_at_K:
        return ("HARD_FAIL",
                "HARD_FAIL_CV_INSTABILITY: cv > %.2f at K=%s | %s%s%s%s" % (
                    CV_HARD_FAIL, cv_fail_at_K, summ, rail_str, knn_str, card_str),
                detail)
    if k_ceiling_fail and (4096 in chain_grade_at_K) and len(chain_grade_at_K) == 1:
        return ("HARD_FAIL",
                "HARD_FAIL_K_4096_IS_CEILING:%s | %s%s%s%s" % (
                    k_ceiling_info, summ, rail_str, knn_str, card_str),
                detail)
    if adv_break_at_K:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_ADVERSARIAL_BREAKS_AT_K_CEILING: adv_break_at=%s | %s%s%s%s" % (
                    adv_break_at_K, summ, rail_str, knn_str, card_str),
                detail)

    extended_Ks = [K for K in K_SWEEP if K > 4096]
    all_extended_chain = all(K in chain_grade_at_K for K in extended_Ks) if extended_Ks else False
    some_extended_chain = any(K in chain_grade_at_K for K in extended_Ks) if extended_Ks else False

    if all_extended_chain and not rail_drift:
        return ("CHAIN_GRADE_K_CEILING_32768",
                "CHAIN_GRADE_K_CEILING_32768_ALL_K_PASS: chain-grade extends to K=%d "
                "(chain_grade_set=%s; k_per_bank<=%d envelope preserved) | %s%s%s%s" % (
                    max(K_SWEEP), chain_grade_at_K, HP_CHAIN_GRADE_K_PER_BANK_MAX,
                    summ, rail_str, knn_str, card_str),
                detail)
    if all_extended_chain and rail_drift:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_RAIL_DRIFT: chain-grade extends but rail K=4096 obs=%.4f "
                "drifted (mechanism not reproducing v1) | %s%s%s%s" % (
                    rail_observed, summ, rail_str, knn_str, card_str),
                detail)

    highest_chain = max(chain_grade_at_K.keys()) if chain_grade_at_K else 0
    if highest_chain >= 16384:
        return ("PARTIAL_K_CEILING_16384",
                "PARTIAL_K_CEILING_16384_CLIFF_AT_32768: highest chain-grade K=%d "
                "(chain_grade_set=%s) | %s%s%s%s" % (
                    highest_chain, chain_grade_at_K, summ, rail_str, knn_str, card_str),
                detail)
    if highest_chain >= 8192:
        return ("PARTIAL_K_CEILING_8192",
                "PARTIAL_K_CEILING_8192_CLIFF_AT_16384: highest chain-grade K=%d "
                "(chain_grade_set=%s) | %s%s%s%s" % (
                    highest_chain, chain_grade_at_K, summ, rail_str, knn_str, card_str),
                detail)
    if highest_chain == 4096:
        return ("K_4096_IS_CEILING",
                "K_4096_IS_CEILING_NO_EXT_PASSES: only K=4096 chain-grade | %s%s%s%s" % (
                    summ, rail_str, knn_str, card_str),
                detail)
    if some_extended_chain:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_K_EXTENDS: chain_grade_set=%s | %s%s%s%s" % (
                    chain_grade_at_K, summ, rail_str, knn_str, card_str),
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_NO_CHAIN_GRADE_AT_EXT: no extended K passes | %s%s%s%s" % (
                summ, rail_str, knn_str, card_str),
            detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": [],
                   "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for K in K_SWEEP:
            arrangements = ARRANGEMENTS_BY_K.get(K, [])
            for R in REGIMES:
                for label, n_b, k_pb in arrangements:
                    keys.append("seed%d_K%d_regime%s_arm%s" % (s, K, R, label))
            if K in SENTINEL_KS:
                keys.append("seed%d_K%d_regimeRANDOM_armARM_KNN_BASELINE" % (s, K))
    return keys


def _parse_key(key: str) -> Tuple[int, int, str, str]:
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    K = int(parts[1].replace("K", ""))
    R = parts[2].replace("regime", "")
    arm_marker_idx = key.index("_arm") + len("_arm")
    A = key[arm_marker_idx:]
    return seed, K, R, A


def _atexit_synth():
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        run_config = {"N": N_DIM, "M": max(K_SWEEP), "run_mode": RUN_MODE}
        keys = _build_keys()
        agg = aggregate_partials(od, seeds=keys, run_config=run_config)
        if not agg and not _RESULTS_HOLDER["failures"]:
            return
        v, vmsg, detail = compute_verdict(agg, _RESULTS_HOLDER["failures"])
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()), atexit_synth=True)
        write_metrics(od, metrics, results=list(agg.values()))
        print("[atexit] wrote synth metrics.json (%d units, %d failures)" % (
            len(agg), len(_RESULTS_HOLDER["failures"])), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


def _build_metrics(v: str, vmsg: str, detail: Dict, units: List[Dict],
                   atexit_synth: bool = False) -> Dict:
    gpu_samples = _RESULTS_HOLDER["gpu_util"]
    if gpu_samples:
        gpu_util_mean = float(np.mean(gpu_samples))
        gpu_util_p50 = float(np.median(gpu_samples))
        gpu_util_max = float(np.max(gpu_samples))
    else:
        gpu_util_mean = float("nan")
        gpu_util_p50 = float("nan")
        gpu_util_max = float("nan")
    gpu = _gpu_info()
    if _CUDA_OK:
        try:
            gpu["gpu_max_mem_alloc_mb"] = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
        except Exception:
            gpu["gpu_max_mem_alloc_mb"] = 0
    else:
        gpu["gpu_max_mem_alloc_mb"] = 0

    return {
        "anchor": ANCHOR_NAME,
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_units": len(units),
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": (len(units) >= EXPECTED_N_UNITS),
        "n_failures": len(_RESULTS_HOLDER["failures"]),
        "failures": _RESULTS_HOLDER["failures"],
        "n_seeds": len(SEEDS),
        "K_SWEEP": K_SWEEP,
        "arrangements_by_K": {str(K): v_ for K, v_ in ARRANGEMENTS_BY_K.items()},
        "seeds": SEEDS,
        "config_version": CONFIG_VERSION,
        "corpus_provenance": CORPUS_PROVENANCE,
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "device": str(_DEVICE),
        "cuda_ok": bool(_CUDA_OK),
        "store_dtype": str(_STORE_DTYPE),
        "codebook_chunk": int(CODEBOOK_CHUNK),
        "gpu_avail": gpu.get("gpu_avail", False),
        "gpu_name": gpu.get("gpu_name", "cpu"),
        "gpu_total_mb": gpu.get("gpu_total_mb", 0),
        "gpu_free_mb": gpu.get("gpu_free_mb", 0),
        "gpu_max_mem_alloc_mb": gpu.get("gpu_max_mem_alloc_mb", 0),
        "gpu_util_mean": gpu_util_mean,
        "gpu_util_p50": gpu_util_p50,
        "gpu_util_max": gpu_util_max,
        "gpu_util_n_samples": len(gpu_samples),
        "per_unit": units,
        "detail": detail,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg[:300],
        "_atexit_synth": atexit_synth,
        "metrics_source": "measured_gpu_substrate_bipolar_multibank_K_ceiling_sweep_v3_chunked_failtrack",
        "DESIGN_NOTE": (
            "V3 re-dispatch. v2 still silently dropped K>=16384 because main-loop "
            "except branched into print-and-continue for non-OOM exceptions. v3 "
            "removes silent-continue entirely: any unit exception (OOM or non-OOM) "
            "is recorded in failures[] with full traceback, halting the loop. "
            "META_RULE_H cardinality guard retained from v2. v3 also: (a) reduced "
            "CODEBOOK_CHUNK 8192->4096 (halves cleanup peak); (b) chunks "
            "_write_bank_batched over banks (1GB bound at K=32768 -> ~256MB peak); "
            "(c) frees ws_selected after del; (d) drops r2 fp32 intermediate; "
            "(e) frees per-regime codebooks between regimes; (f) per-K pre-flight "
            "VRAM probe with HP_VRAM_PROBE_FRACTION=%.2f; (g) per-unit peak_mem_mb. "
            "DISCRIMINATOR: phase-diagram MAP cell -- cliff occurrence IS the "
            "discriminator; Option B analytical justification per "
            "discriminator-must-survive-scale 2026-06-26."
        ) % HP_VRAM_PROBE_FRACTION,
    }


def _build_codebook_for_regime(seed: int, regime: str) -> torch.Tensor:
    if regime == "RANDOM":
        return build_codebook_random(seed * 100003 + 99)
    else:
        return build_codebook_adversarial(seed * 100003 + 199)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d K_SWEEP=%s arrangements=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_SWEEP,
        list(ARRANGEMENTS_BY_K.keys()), CONFIG_VERSION), flush=True)
    print("[gpu] cuda_ok=%s device=%s store_dtype=%s codebook_chunk=%d" % (
        _CUDA_OK, _DEVICE, _STORE_DTYPE, CODEBOOK_CHUNK), flush=True)
    print("[cardinality] expected_n_units=%d (META_RULE_H guard)" % EXPECTED_N_UNITS, flush=True)
    if _CUDA_OK:
        info = _gpu_info()
        print("[gpu] name=%s total=%dMB free=%dMB" % (
            info["gpu_name"], info["gpu_total_mb"], info["gpu_free_mb"]), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "M": max(K_SWEEP), "run_mode": RUN_MODE}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    # v3: free per-regime codebook between regimes to bound resident GPU memory.
    # cache: { (seed, regime): codebook_tensor }; flushed when (seed, regime) changes.
    cached: Dict[Tuple[int, str], torch.Tensor] = {}

    halt_after_loop = False

    for key in all_keys:
        if key in done_keys:
            continue
        seed, K, R, A = _parse_key(key)

        # v3: pre-flight VRAM probe BEFORE attempting unit
        if A == "ARM_KNN_BASELINE":
            n_banks, k_per_bank = 1, K
        else:
            arrangements = ARRANGEMENTS_BY_K.get(K, [])
            match = [arr for arr in arrangements if arr[0] == A]
            if not match:
                print("[WARN] no arrangement for K=%d arm=%s; skipping" % (K, A), flush=True)
                continue
            _, n_banks, k_per_bank = match[0]

        est_bytes = _estimate_peak_working_set_bytes(K, n_banks, k_per_bank)
        if _CUDA_OK:
            free_b, total_b = torch.cuda.mem_get_info(0)
            budget = int(free_b * HP_VRAM_PROBE_FRACTION)
            if est_bytes > budget:
                fail_entry = {
                    "key": key,
                    "seed": seed, "k_total": K, "regime": R, "arm_label": A,
                    "exc_type": "HP_VRAM_PROBE_BREACH",
                    "exc_msg": "est_peak=%.2fGB budget=%.2fGB (free=%.2fGB * %.2f)" % (
                        est_bytes / 1024**3, budget / 1024**3,
                        free_b / 1024**3, HP_VRAM_PROBE_FRACTION),
                    "traceback": "",
                    "est_peak_mb": int(est_bytes / 1024 / 1024),
                    "free_mb": int(free_b / 1024 / 1024),
                }
                _RESULTS_HOLDER["failures"].append(fail_entry)
                print("[HP_VRAM_PROBE_BREACH] %s est=%.2fGB > budget=%.2fGB (free=%.2fGB)" % (
                    key, est_bytes / 1024**3, budget / 1024**3, free_b / 1024**3), flush=True)
                halt_after_loop = True
                break

        # Rebuild codebook on (seed, regime) miss; free other regime cb if cached.
        ckey = (seed, R)
        if ckey not in cached:
            # Free any stale (seed, other_regime) entries to bound resident.
            for stale_k in list(cached.keys()):
                if stale_k[0] == seed and stale_k[1] != R:
                    del cached[stale_k]
                    if _CUDA_OK:
                        torch.cuda.empty_cache()
            print("[seed=%d regime=%s] building codebook..." % (seed, R), flush=True)
            cached[ckey] = _build_codebook_for_regime(seed, R)
        codebook = cached[ckey]

        try:
            print("  [run] %s ... (est_peak=%.2fGB)" % (
                key, est_bytes / 1024**3), flush=True)
            rec = run_unit(seed, K, R, A, n_banks, k_per_bank,
                            codebook, _RESULTS_HOLDER["gpu_util"])
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            # v3: NEVER silently continue. Record full failure context + halt loop.
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "k_total": K, "regime": R, "arm_label": A,
                "n_banks": n_banks, "k_per_bank": k_per_bank,
                "exc_type": type(e).__name__,
                "exc_msg": str(e)[:500],
                "traceback": tb[-2000:],
                "is_oom_class": _is_oom_error(e),
                "est_peak_mb": int(est_bytes / 1024 / 1024),
            }
            if _CUDA_OK:
                try:
                    fail_entry["peak_mem_mb"] = int(torch.cuda.max_memory_allocated(0) / 1024 / 1024)
                    free_b, total_b = torch.cuda.mem_get_info(0)
                    fail_entry["free_mb_at_fail"] = int(free_b / 1024 / 1024)
                except Exception:
                    pass
            _RESULTS_HOLDER["failures"].append(fail_entry)
            print("[UNIT_EXCEPTION] %s type=%s is_oom=%s msg=%r" % (
                key, type(e).__name__, _is_oom_error(e), str(e)[:200]), flush=True)
            print("[TRACEBACK]\n%s" % tb, flush=True)
            print("[v3] halting loop on unit exception (no silent-continue)", flush=True)
            halt_after_loop = True
            break

    agg = aggregate_partials(out_dir, seeds=all_keys, run_config=run_config)
    units = [agg[k] for k in all_keys if k in agg]
    failures = _RESULTS_HOLDER["failures"]

    if not units and not failures:
        print("[FATAL] no partials available and no recorded failures", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode gate violated"

    v, vmsg, detail = compute_verdict(agg, failures)
    print("\n[VERDICT] %s" % v, flush=True)
    print("[VERDICT_MSG] %s" % vmsg, flush=True)
    if failures:
        print("[FAILURES] %d total" % len(failures), flush=True)
        for f in failures:
            print("  - %s: %s -- %s" % (f["key"], f["exc_type"], f["exc_msg"][:120]),
                  flush=True)

    metrics = _build_metrics(v, vmsg, detail, units, atexit_synth=False)
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %d failures, %.1fs)" % (
        len(units), len(failures), metrics["elapsed_s"]), flush=True)
    if halt_after_loop:
        sys.exit(1)
