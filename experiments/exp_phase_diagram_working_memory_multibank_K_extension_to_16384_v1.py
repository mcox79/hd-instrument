"""phase_diagram_working_memory_multibank_K_extension_to_16384_v1 -- GPU K-extension to K=16384.

USER directive 2026-06-26: phase-diagram extension of multi-bank working-memory beyond K=4096
(v1 K-extension cell `exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1`
chain-graded MULTI_64x at K=4096 recall=0.9927 cv=0.0006 random / 0.9810 cv=0.0015 adversarial).

PROMOTION CONTEXT:
  Brain working-memory effective capacity is ~7+/-2 conscious items, but routing/binding
  capacity at substrate level is much higher. Need to MAP CLIFF for production deployment
  confidence: where does multi-bank K cliff above 4096? K=8192? K=16384? Or no cliff?

DESIGN: K-extension with FIVE phase-points + rail check at K=4096
  K=4096 [MULTI_64x]                    (RAIL; must reproduce 0.9927 within 0.02)
  K=8192 [MULTI_64x, MULTI_128x]        (2x extension; novel)
  K=16384 [MULTI_128x, MULTI_256x]      (4x extension; novel)
Each at RANDOM regime + ADVERSARIAL regime (FEATURE_OVERLAP_FRAC=0.20)
Plus sentinel: ARM_KNN_BASELINE at M=400 (>= 0.9, Fix #28 sentinel)
Plus floor: ARM_NAIVE_SINGLE_BANK at K=4096 (reproduces ~0.002)

CONFIG (N_DIM=8192 per USER spec):
  N_DIM = 8192, CODEBOOK_SIZE = 32768, SIGMA=1.0, CUE_COS=0.70
  FEATURE_OVERLAP_FRAC=0.20, N_GROUPS_ADV=4, N_ITEMS_PER_K=200, seeds=[11,13,19]
  HP_CHAIN_GRADE: recall>=0.95 cv<=0.05 route_acc>=0.95 adv_within<=0.05 k_per_bank<=64

PRE-REG BANDS (LOCKED at module init; see prereg .md for full details):
  CHAIN_GRADE_K_EXTENDS_TO_16384: K=8192 AND K=16384 best arm >= 0.95 AND adv within 0.05 AND
    cv <= 0.05 AND k_per_bank in chain-grade envelope (<=64)
  PARTIAL_K_EXTENDS_TO_8192: K=8192 chain-grade; K=16384 partial
  K_4096_IS_CEILING: K=8192 best random recall < 0.50
  ADVERSARIAL_BREAKS_AT_K_EXT: adv drops >= 0.30 vs random at K=8192 OR K=16384

GPU MANDATE (Fix #24): torch.cuda required for full; fp16 storage; batched matmul on cuda;
  nvidia-smi util sampled per arm; smoke gates gpu_util_p50 >= 50%.

ASCII-only. Single-file. Resumable per (seed, K, regime, arm) checkpoint key.

Author: exp_dev 2026-06-25 (USER-directed phase-diagram extension).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
# PyTorch CUDA allocator (fragmentation mitigation for fp16 + 8GB cards)
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import argparse
import atexit
import math
import time
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

ANCHOR_NAME = "phase_diagram_working_memory_multibank_K_extension_to_16384_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM forward MUST increment.
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
HP_K_CEILING_RECALL_MIN = 0.50  # K=8192 best < this => HARD_FAIL K_4096_IS_CEILING
HP_CHAIN_GRADE_K_PER_BANK_MAX = 64  # chain-grade requires k_per_bank in envelope (per Cell D rail)
Q_SUSPECT_SATURATION = 0.995
HP_RAIL_K4096_RECALL = 0.9927   # v1 K-extension cell rail (random MULTI_64x)
HP_RAIL_K4096_TOL = 0.02
HP_KNN_SENTINEL_MIN = 0.90       # ARM_KNN_BASELINE M=400 sentinel (Fix #28)
CV_HARD_FAIL = 0.10

assert 0.0 < HP_CHAIN_GRADE_RECALL < 1.0, "band locked"
assert 0.0 < HP_ADV_WITHIN_RANDOM < HP_ADV_BREAK_THRESHOLD, "ordering"
assert HP_CHAIN_GRADE_K_PER_BANK_MAX == 64, "envelope locked"

# Smoke vs full config (META_M7: capacity-sensitive dims identical)
SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20
N_GROUPS_ADV = 4
KNN_SENTINEL_M = 400  # ARM_KNN_BASELINE corpus size

if SMOKE:
    N_DIM = 2048
    CODEBOOK_SIZE = 4096
    K_SWEEP = [1024, 4096]
    # arrangements: only one per K in smoke
    ARRANGEMENTS_BY_K = {
        1024: [("MULTI_32x", 32, 32)],
        4096: [("MULTI_64x", 64, 64)],
    }
    N_ITEMS_PER_K = 80
    SEEDS = [11]
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 32768
    K_SWEEP = [4096, 8192, 16384]
    ARRANGEMENTS_BY_K = {
        4096:  [("MULTI_64x",  64,  64)],                       # rail
        8192:  [("MULTI_64x",  64, 128), ("MULTI_128x", 128, 64)],
        16384: [("MULTI_128x", 128, 128), ("MULTI_256x", 256, 64)],
    }
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]

# Sentinel + naive arms (run only at K=4096 to keep cost bounded)
SENTINEL_KS = [4096]  # K-values at which to also run KNN_BASELINE + NAIVE_SINGLE_BANK
# Regimes
REGIMES = ["RANDOM", "ADVERSARIAL"]

CONFIG_VERSION = (
    "phaseDiagWmMBKExt-v1: N_DIM=%d CODEBOOK_SIZE=%d sigma=%.1f CUE_COS=%.2f "
    "FEATURE_OVERLAP=%.2f K_SWEEP=%s arrangements=%s N_ITEMS_PER_K=%d seeds=%s "
    "mode=%s HP_chain>=%.2f cv<=%.2f route_acc>=%.2f HP_adv_within=%.2f "
    "HP_adv_break=%.2f Q_sat>=%.3f HP_rail_K4096=%.4f+/-%.3f kPerBankMax=%d"
) % (
    N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
    K_SWEEP, list(ARRANGEMENTS_BY_K.keys()),
    N_ITEMS_PER_K, SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
    HP_ADV_WITHIN_RANDOM, HP_ADV_BREAK_THRESHOLD,
    Q_SUSPECT_SATURATION, HP_RAIL_K4096_RECALL, HP_RAIL_K4096_TOL,
    HP_CHAIN_GRADE_K_PER_BANK_MAX,
)


# ----------------------------- GPU mandate (Fix #22 + Fix #24) -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "phase_diagram K-extension at N_DIM=%d K_max=%d requires CUDA. "
            "Route to overnight_queue (GPU runner)." % (N_DIM, max(K_SWEEP)))
    return False


_STRICT_GPU = (not SMOKE) and (not _ARGS.self_test)
_CUDA_OK = _require_cuda(strict=_STRICT_GPU)
_DEVICE = torch.device("cuda:0") if _CUDA_OK else torch.device("cpu")
_STORE_DTYPE = torch.float16 if _CUDA_OK else torch.float32


def _gpu_util_sample() -> Optional[float]:
    """nvidia-smi util %% sample. Returns None on unavailable."""
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
        return {"gpu_avail": False, "gpu_name": "cpu", "gpu_total_mb": 0}
    free_b, total_b = torch.cuda.mem_get_info(0)
    return {
        "gpu_avail": True,
        "gpu_name": torch.cuda.get_device_name(0),
        "gpu_total_mb": int(total_b / 1024 / 1024),
        "gpu_free_mb": int(free_b / 1024 / 1024),
    }


# ----------------------------- HD primitives (torch on cuda) -----------------------------

def _make_gen(seed_int: int) -> torch.Generator:
    g = torch.Generator(device=_DEVICE)
    g.manual_seed(int(seed_int))
    return g


def random_bipolar_t(shape, gen: torch.Generator) -> torch.Tensor:
    """Random +/-1 bipolar tensor in _STORE_DTYPE on _DEVICE.

    PyTorch bernoulli_ on fp16 cuda is natively supported (validated in p1_v3).
    """
    X = torch.empty(*shape, device=_DEVICE, dtype=_STORE_DTYPE)
    X.bernoulli_(0.5, generator=gen).mul_(2.0).sub_(1.0)
    return X


def bipolar_quantize_t(v: torch.Tensor) -> torch.Tensor:
    """Sign-quantize to +/-1 in same dtype (0 -> +1)."""
    out = torch.where(v >= 0,
                      torch.ones_like(v),
                      -torch.ones_like(v))
    return out


def build_codebook_random(seed_offset: int) -> torch.Tensor:
    g = _make_gen(seed_offset)
    return random_bipolar_t((CODEBOOK_SIZE, N_DIM), g)


def build_codebook_adversarial(seed_offset: int) -> torch.Tensor:
    """ADVERSARIAL codebook: items partitioned into N_GROUPS_ADV groups; within a group,
    FIRST FEATURE_OVERLAP_FRAC*N_DIM bits are COPIED from the group template (shared prefix);
    remaining bits are independent random bipolar.

    Two items in same group: expected match fraction = FEATURE_OVERLAP_FRAC + 0.5*(1-FEATURE_OVERLAP_FRAC)
    Two items in different groups: ~0.5 (all random).

    Vectorized: build all N_DIM bipolar bits independently THEN overwrite the first n_shared
    columns with the corresponding group template's first n_shared bits.
    """
    g_tpl = _make_gen(seed_offset + 7)
    g_items = _make_gen(seed_offset + 11)
    templates = random_bipolar_t((N_GROUPS_ADV, N_DIM), g_tpl)
    items = random_bipolar_t((CODEBOOK_SIZE, N_DIM), g_items)
    n_shared = int(FEATURE_OVERLAP_FRAC * N_DIM)
    if n_shared > 0:
        # Item i is in group (i % N_GROUPS_ADV); copy first n_shared bits from template
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
    """Write each bank's workspace as bipolar-quantized noisy sum-of-(item * slot_tag).

    items_per_bank: (n_banks, k_per_bank, N) STORE_DTYPE on _DEVICE
    slot_tags:      (k_per_bank, N) STORE_DTYPE on _DEVICE
    returns workspaces: (n_banks, N) STORE_DTYPE on _DEVICE

    GPU-batched (no Python per-bank loop).
    """
    # element-wise (items * slot_tags) broadcast over n_banks: (n_banks, k_per_bank, N)
    # then sum over k_per_bank axis -> (n_banks, N)
    # Use fp32 accumulation for sum to avoid fp16 overflow at large k_per_bank
    bound = items_per_bank.float() * slot_tags.unsqueeze(0).float()  # (n_banks, k_per_bank, N)
    ws_acc = bound.sum(dim=1)  # (n_banks, N) fp32
    if SIGMA > 0.0:
        g_noise = _make_gen(seed_offset + 23)
        noise = torch.empty(ws_acc.shape, device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, SIGMA, generator=g_noise)
        ws_acc = ws_acc + noise
    return bipolar_quantize_t(ws_acc).to(_STORE_DTYPE)


def _read_with_cleanup_batched(workspaces: torch.Tensor,
                               slot_tag: torch.Tensor,
                               codebook: torch.Tensor) -> torch.Tensor:
    """One-step iterative cleanup. Vectorized across multiple bank/slot queries.

    workspaces: (n_query, N) -- the bank workspace selected for each query
    slot_tag:   (n_query, N) -- the slot-tag for each query
    codebook:   (CODEBOOK_SIZE, N)
    returns:    (n_query,) int64 predicted indices

    Two-step cleanup: r1 = ws * slot; cand = argmax(codebook @ r1.T);
                       r2 = 0.5*(r1 + codebook[cand]); idx = argmax(codebook @ r2_bp.T)
    """
    n_query = workspaces.shape[0]
    r1 = (workspaces * slot_tag)  # (n_query, N) STORE_DTYPE
    # sims1 = codebook @ r1.T  -> (CODEBOOK, n_query)
    sims1 = codebook @ r1.T
    cand_idx = sims1.argmax(dim=0)  # (n_query,)
    # r2 = 0.5*(r1 + codebook[cand_idx])
    cand_vecs = codebook[cand_idx]  # (n_query, N)
    r2 = (0.5 * r1.float() + 0.5 * cand_vecs.float())
    r2_bp = bipolar_quantize_t(r2).to(_STORE_DTYPE)
    sims2 = codebook @ r2_bp.T  # (CODEBOOK, n_query)
    pred_idx = sims2.argmax(dim=0)  # (n_query,)
    return pred_idx


def eval_multi_bank_arm(n_banks: int, k_per_bank: int, k_total: int,
                        codebook: torch.Tensor, seed_offset: int,
                        gpu_util_samples: List[float]) -> Tuple[float, float]:
    """Multi-bank arm eval. Returns (recall, route_acc).

    GPU-batched throughout. Build bank workspaces via batched write, then evaluate ALL
    k_total slot queries with single batched matmul.
    """
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
        # Sample k_total items from codebook without replacement
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:k_total]
        items = codebook[idx_global]  # (k_total, N)
        items_per_bank = items.view(n_banks, k_per_bank, N_DIM)
        # Write all banks: (n_banks, N)
        workspaces = _write_bank_batched(items_per_bank, slot_tags,
                                         seed_offset + 1000 + trial)

        # Build batched queries: (k_total, N) cues with bank_tag perturbation
        # bank_true for slot s = s // k_per_bank
        slot_indices = torch.arange(k_total, device=_DEVICE)
        bank_true = slot_indices // k_per_bank  # (k_total,)
        local_slot = slot_indices % k_per_bank   # (k_total,)

        # cue = CUE_COS * bank_tags[bank_true] + cue_noise_scale * bipolar(noise)
        g_cue = _make_gen(seed_offset + 5000 + trial)
        bank_cue_base = bank_tags[bank_true].float()  # (k_total, N)
        noise = torch.empty((k_total, N_DIM), device=_DEVICE, dtype=torch.float32)
        noise.normal_(0.0, 1.0, generator=g_cue)
        noise_bp = bipolar_quantize_t(noise)
        cues = (CUE_COS * bank_cue_base + cue_noise_scale * noise_bp).to(_STORE_DTYPE)
        # sims_bank = cues @ bank_tags.T -> (k_total, n_banks)
        sims_bank = cues @ bank_tags.T
        bank_routed = sims_bank.argmax(dim=1)  # (k_total,)

        route_correct += int((bank_routed == bank_true).sum().item())
        route_total += k_total

        # For each slot: select workspaces[bank_routed[i]] + slot_tags[local_slot[i]]
        ws_selected = workspaces[bank_routed]  # (k_total, N)
        slot_tag_sel = slot_tags[local_slot]   # (k_total, N)

        pred_idx = _read_with_cleanup_batched(ws_selected, slot_tag_sel, codebook)
        # correct iff pred matches true item AND bank_routed == bank_true
        true_item_idx = idx_global[slot_indices]  # (k_total,)
        match = (pred_idx == true_item_idx) & (bank_routed == bank_true)
        correct += int(match.sum().item())
        total += k_total

        # Free transient
        del items, items_per_bank, workspaces, cues, sims_bank, ws_selected, slot_tag_sel, pred_idx
        if _CUDA_OK:
            torch.cuda.empty_cache()

        sample = _gpu_util_sample()
        if sample is not None:
            gpu_util_samples.append(sample)

    recall = correct / max(total, 1)
    route_acc = route_correct / max(route_total, 1)
    return recall, route_acc


def eval_naive_single_bank(k_total: int, codebook: torch.Tensor, seed_offset: int) -> float:
    """NAIVE single-bank baseline: write k_total items as bipolar-quantized noisy sum;
    read with cleanup; reproduces ~0.002 floor at large K (cliffs naturally past K~64).
    """
    n_trials = max(1, math.ceil(N_ITEMS_PER_K / k_total))
    slot_tags = build_slot_tags(seed_offset, k_total)  # single bank uses k_total slots
    correct = 0
    total = 0
    g_trial = _make_gen(seed_offset + 31)
    for trial in range(n_trials):
        idx_global = torch.randperm(CODEBOOK_SIZE, generator=g_trial, device=_DEVICE)[:k_total]
        items = codebook[idx_global]  # (k_total, N)
        # Single bank: write = bipolar-quantize(sum of items * slot_tags + noise)
        items_b = items.unsqueeze(0)  # (1, k_total, N)
        ws = _write_bank_batched(items_b, slot_tags, seed_offset + 1700 + trial)  # (1, N)
        ws_b = ws.expand(k_total, -1)  # (k_total, N)
        pred_idx = _read_with_cleanup_batched(ws_b, slot_tags, codebook)
        match = (pred_idx == idx_global)
        correct += int(match.sum().item())
        total += k_total
        del items, items_b, ws, ws_b, pred_idx
        if _CUDA_OK:
            torch.cuda.empty_cache()
    return correct / max(total, 1)


def eval_knn_baseline(codebook: torch.Tensor, seed_offset: int) -> float:
    """ARM_KNN_BASELINE: KNN top-1 over codebook on noised key at small M.

    For M items (M=KNN_SENTINEL_M=400): noise each item with sigma=NOISE_FRAC and check
    top-1 cleanup against codebook. Should be >= 0.90 (sentinel; Fix #28).
    """
    M = min(KNN_SENTINEL_M, CODEBOOK_SIZE)
    g_pick = _make_gen(seed_offset + 37)
    pick = torch.randperm(CODEBOOK_SIZE, generator=g_pick, device=_DEVICE)[:M]
    items = codebook[pick]  # (M, N)
    g_noise = _make_gen(seed_offset + 41)
    noise = torch.empty((M, N_DIM), device=_DEVICE, dtype=torch.float32)
    noise.normal_(0.0, 0.5, generator=g_noise)  # mild noise (sigma=0.5 on bipolar)
    noisy = bipolar_quantize_t(items.float() + noise).to(_STORE_DTYPE)
    sims = noisy @ codebook.T  # (M, CODEBOOK)
    pred = sims.argmax(dim=1)  # (M,)
    correct = int((pred == pick).sum().item())
    return correct / max(M, 1)


# ----------------------------- self-test (CPU; fp32) -----------------------------
def _selftest():
    """5 formula self-tests on CPU in fp32 (selftest gate)."""
    global _DEVICE, _STORE_DTYPE, _CUDA_OK
    save_dev, save_dtype, save_cuda = _DEVICE, _STORE_DTYPE, _CUDA_OK
    _DEVICE = torch.device("cpu")
    _STORE_DTYPE = torch.float32
    _CUDA_OK = False
    # Smoke globals temporarily (small N for selftest)
    global N_DIM_BAK, CODEBOOK_SIZE_BAK, N_DIM, CODEBOOK_SIZE
    N_DIM_BAK = N_DIM
    CODEBOOK_SIZE_BAK = CODEBOOK_SIZE
    N_DIM = 1024
    CODEBOOK_SIZE = 2048
    try:
        # T1: codebook random shape + bipolar
        cb = build_codebook_random(0)
        assert cb.shape == (2048, 1024), "T1 shape"
        u = torch.unique(cb)
        assert set(u.tolist()) <= {-1.0, 1.0}, "T1 bipolar"
        print("[selftest] T1 PASS: random codebook shape + bipolar")

        # T2: adversarial codebook shape + in-group > cross-group overlap
        cb_adv = build_codebook_adversarial(1)
        assert cb_adv.shape == (2048, 1024), "T2 adv shape"
        i_a = 0  # group 0
        i_b = N_GROUPS_ADV  # also group 0
        i_c = 1  # group 1
        shared_in = float((cb_adv[i_a] == cb_adv[i_b]).float().mean().item())
        shared_cross = float((cb_adv[i_a] == cb_adv[i_c]).float().mean().item())
        expected_in = FEATURE_OVERLAP_FRAC + 0.5 * (1.0 - FEATURE_OVERLAP_FRAC)
        assert shared_in > shared_cross + 0.05, (
            "T2 adversarial groups don't differ: in=%.3f cross=%.3f" % (shared_in, shared_cross))
        assert abs(shared_in - expected_in) < 0.10, (
            "T2 in-group overlap %.3f vs expected ~%.3f" % (shared_in, expected_in))
        print("[selftest] T2 PASS: adversarial in=%.3f cross=%.3f expected ~%.3f vs 0.5" % (
            shared_in, shared_cross, expected_in))

        # T3: multi-bank 8x32_K256 random gives high recall + route_acc on tiny config
        # NOTE: temporary override of N_ITEMS_PER_K for selftest
        global N_ITEMS_PER_K
        N_ITEMS_PER_K_BAK = N_ITEMS_PER_K
        N_ITEMS_PER_K = 64
        gpu_samples = []
        # Use 16 banks * 16 slots = K=256 to keep k_per_bank small for clean recall at N=1024
        rec, ra = eval_multi_bank_arm(16, 16, 256, cb, seed_offset=100,
                                       gpu_util_samples=gpu_samples)
        N_ITEMS_PER_K = N_ITEMS_PER_K_BAK
        assert ra >= 0.85, "T3 route_acc=%.3f < 0.85" % ra
        assert rec >= 0.50, "T3 recall=%.3f < 0.50" % rec
        print("[selftest] T3 PASS: multi-bank 16x16_K256 recall=%.3f route_acc=%.3f" % (rec, ra))

        # T4: LLM counter zero
        assert _LLM_CALL_COUNTER[0] == 0, "T4 LLM counter non-zero"
        print("[selftest] T4 PASS: LLM counter = 0")

        # T5: KNN baseline sentinel >= 0.90 on tiny codebook
        rec_knn = eval_knn_baseline(cb, seed_offset=200)
        assert rec_knn >= 0.85, "T5 KNN baseline %.3f < 0.85" % rec_knn
        print("[selftest] T5 PASS: KNN baseline recall=%.3f" % rec_knn)

        # T6: bands locked (sanity)
        assert HP_CHAIN_GRADE_RECALL == 0.95
        assert HP_CHAIN_GRADE_K_PER_BANK_MAX == 64
        print("[selftest] T6 PASS: bands locked")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        N_DIM = N_DIM_BAK
        CODEBOOK_SIZE = CODEBOOK_SIZE_BAK


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ----------------------------- per-arm runner -----------------------------
def run_unit(seed: int, k_total: int, regime: str, arm_label: str,
             n_banks: int, k_per_bank: int,
             cb_random: torch.Tensor, cb_adv: torch.Tensor,
             gpu_util_samples: List[float]) -> Dict:
    """Run one (seed, K, regime, arm) cell."""
    t0 = time.time()
    codebook = cb_random if regime == "RANDOM" else cb_adv
    seed_offset = seed * 100003 + k_total * 31 + (1 if regime == "ADVERSARIAL" else 0)

    if arm_label == "ARM_KNN_BASELINE":
        recall = eval_knn_baseline(codebook, seed_offset)
        route_acc = 1.0  # n/a
    elif arm_label == "ARM_NAIVE_SINGLE_BANK":
        recall = eval_naive_single_bank(k_total, codebook, seed_offset)
        route_acc = 1.0
    else:
        recall, route_acc = eval_multi_bank_arm(n_banks, k_per_bank, k_total, codebook,
                                                 seed_offset, gpu_util_samples)

    sample = _gpu_util_sample()
    if sample is not None:
        gpu_util_samples.append(sample)

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
def compute_verdict(per_key: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    if not per_key:
        return ("HARD_FAIL", "no_units", {})

    # Group by (K, regime, arm_label) -> list of (seed, recall, route_acc)
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

    # Compute stats
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

    # Q-discipline saturation flags
    q_suspect = {}
    for K, by_R in arm_stats.items():
        for R, by_A in by_R.items():
            for A, st in by_A.items():
                if st["recall_mean"] >= Q_SUSPECT_SATURATION and st["recall_cv"] == 0.0:
                    q_suspect.setdefault(K, {}).setdefault(R, []).append(A)

    # Rail check: K=4096 MULTI_64x random recall within +/-HP_RAIL_K4096_TOL of HP_RAIL_K4096_RECALL
    rail_ok = None
    rail_observed = None
    rail_drift = False
    if 4096 in arm_stats and "RANDOM" in arm_stats[4096] and "MULTI_64x" in arm_stats[4096]["RANDOM"]:
        rail_observed = arm_stats[4096]["RANDOM"]["MULTI_64x"]["recall_mean"]
        rail_ok = abs(rail_observed - HP_RAIL_K4096_RECALL) <= HP_RAIL_K4096_TOL
        rail_drift = not rail_ok

    # KNN sentinel check (Fix #28)
    knn_ok = None
    knn_observed = None
    if 4096 in arm_stats and "RANDOM" in arm_stats[4096] and "ARM_KNN_BASELINE" in arm_stats[4096]["RANDOM"]:
        knn_observed = arm_stats[4096]["RANDOM"]["ARM_KNN_BASELINE"]["recall_mean"]
        knn_ok = (knn_observed >= HP_KNN_SENTINEL_MIN)

    # Substrate-only gate
    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    # Per-K chain-grade check
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

    # K_4096_IS_CEILING check
    k_ceiling_fail = False
    k_ceiling_info = ""
    if 8192 in arm_stats and "RANDOM" in arm_stats[8192]:
        rand_multi_8k = {A: st for A, st in arm_stats[8192]["RANDOM"].items()
                          if A.startswith("MULTI_")}
        if rand_multi_8k:
            best_8k = max(rand_multi_8k.values(), key=lambda x: x["recall_mean"])
            if best_8k["recall_mean"] < HP_K_CEILING_RECALL_MIN:
                k_ceiling_fail = True
                k_ceiling_info = "K=8192 best random recall=%.3f < %.2f" % (
                    best_8k["recall_mean"], HP_K_CEILING_RECALL_MIN)

    # Build summary rows
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
        rail_str = " | rail_K4096_obs=%.4f (target=%.4f +/-%.3f; %s)" % (
            rail_observed, HP_RAIL_K4096_RECALL, HP_RAIL_K4096_TOL,
            "OK" if rail_ok else "DRIFT")
    knn_str = ""
    if knn_observed is not None:
        knn_str = " | knn_sentinel=%.4f (>=%.2f; %s)" % (
            knn_observed, HP_KNN_SENTINEL_MIN, "OK" if knn_ok else "FAIL")
    if q_suspect:
        summ += " | [Q-DISCIPLINE: saturated=%s]" % q_suspect

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
    }

    # Smoke-mode: produce SMOKE_PASS verdict if mechanism end-to-end works
    # (smoke at smaller N cannot reproduce full rail at N=8192; verdict ladder is
    # only meaningful for full run)
    if SMOKE:
        any_mech_ok = any(
            (st["recall_mean"] >= 0.50)
            for K, by_R in arm_stats.items()
            for R, by_A in by_R.items()
            for A, st in by_A.items()
            if A.startswith("MULTI_")
        )
        knn_ok_smoke = (knn_observed is None) or knn_ok
        if substrate_only_ok and any_mech_ok and knn_ok_smoke:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime | %s%s%s" % (
                        summ, rail_str, knn_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | %s%s%s" % (
                    summ, rail_str, knn_str),
                detail)

    # Verdict ladder (FULL run only)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only gate violated (%d LLM calls) | %s%s%s" % (
                    n_llm, summ, rail_str, knn_str),
                detail)
    if knn_observed is not None and not knn_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_KNN_SENTINEL: ARM_KNN_BASELINE %.4f < %.2f | %s%s%s" % (
                    knn_observed, HP_KNN_SENTINEL_MIN, summ, rail_str, knn_str),
                detail)
    if cv_fail_at_K:
        return ("HARD_FAIL",
                "HARD_FAIL_CV_INSTABILITY: cv > %.2f at K=%s | %s%s%s" % (
                    CV_HARD_FAIL, cv_fail_at_K, summ, rail_str, knn_str),
                detail)
    if k_ceiling_fail:
        return ("HARD_FAIL",
                "HARD_FAIL_K_4096_IS_CEILING: %s | %s%s%s" % (
                    k_ceiling_info, summ, rail_str, knn_str),
                detail)
    if adv_break_at_K:
        return ("HARD_FAIL",
                "HARD_FAIL_ADVERSARIAL_BREAKS_AT_K_EXT: %s | %s%s%s" % (
                    adv_break_at_K, summ, rail_str, knn_str),
                detail)

    # Chain-grade analysis
    extended_Ks = [K for K in K_SWEEP if K > 4096]  # the novel extension points
    all_extended_chain = all(K in chain_grade_at_K for K in extended_Ks) if extended_Ks else False
    some_extended_chain = any(K in chain_grade_at_K for K in extended_Ks) if extended_Ks else False

    if all_extended_chain and not rail_drift:
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_K_EXTENDS_TO_16384: chain-grade extends across K=%s "
                "(chain_grade_set=%s; k_per_bank<=%d envelope preserved) | %s%s%s" % (
                    extended_Ks, chain_grade_at_K, HP_CHAIN_GRADE_K_PER_BANK_MAX,
                    summ, rail_str, knn_str),
                detail)
    if all_extended_chain and rail_drift:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_RAIL_DRIFT: chain-grade extends to K=16384 but rail K=4096 obs=%.4f "
                "drifted outside %.4f+/-%.3f (mechanism not bit-identically reproducing v1) | %s%s%s" % (
                    rail_observed, HP_RAIL_K4096_RECALL, HP_RAIL_K4096_TOL,
                    summ, rail_str, knn_str),
                detail)
    if some_extended_chain:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_K_EXTENDS: chain-grade at K=%s; partial elsewhere "
                "(chain_grade_set=%s) | %s%s%s" % (
                    [K for K in extended_Ks if K in chain_grade_at_K],
                    chain_grade_at_K, summ, rail_str, knn_str),
                detail)
    # Look at K=8192 best to decide MIDDLE vs HARD_FAIL
    if 8192 in arm_stats and "RANDOM" in arm_stats[8192]:
        rand_multi_8k = {A: st for A, st in arm_stats[8192]["RANDOM"].items()
                          if A.startswith("MULTI_")}
        if rand_multi_8k:
            best = max(rand_multi_8k.values(), key=lambda x: x["recall_mean"])
            if best["recall_mean"] >= 0.50:
                return ("MIDDLE_BAND",
                        "MIDDLE_BAND_NO_CHAIN_GRADE_AT_EXT: best K=8192 random=%.4f in [0.50, %.2f); "
                        "no extended K passes chain-grade gate | %s%s%s" % (
                            best["recall_mean"], HP_CHAIN_GRADE_RECALL,
                            summ, rail_str, knn_str),
                        detail)
    return ("HARD_FAIL",
            "HARD_FAIL_NO_K_HOLDS: no extended K passes chain-grade gate | %s%s%s" % (
                summ, rail_str, knn_str),
            detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": []}


def _build_keys() -> List[str]:
    """Enumerate all (seed, K, regime, arm) ckpt keys."""
    keys = []
    for s in SEEDS:
        for K in K_SWEEP:
            arrangements = ARRANGEMENTS_BY_K.get(K, [])
            for R in REGIMES:
                for label, n_b, k_pb in arrangements:
                    keys.append("seed%d_K%d_regime%s_arm%s" % (s, K, R, label))
            # sentinel arms at K=4096 only, RANDOM only
            if K in SENTINEL_KS:
                keys.append("seed%d_K%d_regimeRANDOM_armARM_KNN_BASELINE" % (s, K))
                keys.append("seed%d_K%d_regimeRANDOM_armARM_NAIVE_SINGLE_BANK" % (s, K))
    return keys


def _parse_key(key: str) -> Tuple[int, int, str, str]:
    # seed<S>_K<K>_regime<R>_arm<A>
    parts = key.split("_")
    seed = int(parts[0].replace("seed", ""))
    K = int(parts[1].replace("K", ""))
    R = parts[2].replace("regime", "")
    # arm_label may contain underscores
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
        if not agg:
            return
        v, vmsg, detail = compute_verdict(agg)
        metrics = _build_metrics(v, vmsg, detail, list(agg.values()), atexit_synth=True)
        write_metrics(od, metrics, results=list(agg.values()))
        print("[atexit] wrote synth metrics.json (%d units)" % len(agg), flush=True)
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
        "gpu_avail": gpu.get("gpu_avail", False),
        "gpu_name": gpu.get("gpu_name", "cpu"),
        "gpu_total_mb": gpu.get("gpu_total_mb", 0),
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
        "metrics_source": "measured_gpu_substrate_bipolar_multibank_K_extension",
        "DESIGN_NOTE": (
            "Phase-diagram extension of multi-bank working-memory K beyond 4096. "
            "Sweeps K in {4096, 8192, 16384} at N_DIM=%d with chain-grade envelope "
            "k_per_bank<=64 preserved across MULTI_64x/128x/256x arrangements. Tests RANDOM "
            "AND ADVERSARIAL feature-overlap regimes for cross-regime robustness. Rail-checks "
            "K=4096 MULTI_64x random against v1 K-extension cell's 0.9927 within +/-0.02. "
            "Sentinel ARM_KNN_BASELINE >= %.2f (Fix #28). GPU-batched matmul on fp16 cuda; "
            "gpu_util sampled per arm (Fix #24). Pre-reg per preregs/2026-06-25_%s.md."
        ) % (N_DIM, HP_KNN_SENTINEL_MIN, ANCHOR_NAME),
    }


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d K_SWEEP=%s arrangements=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_SWEEP,
        list(ARRANGEMENTS_BY_K.keys()), CONFIG_VERSION), flush=True)
    print("[gpu] cuda_ok=%s device=%s store_dtype=%s" % (
        _CUDA_OK, _DEVICE, _STORE_DTYPE), flush=True)
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

    # Build codebooks per seed (cached across K within a seed)
    seed_codebooks: Dict[int, Tuple[torch.Tensor, torch.Tensor]] = {}

    for key in all_keys:
        if key in done_keys:
            continue
        seed, K, R, A = _parse_key(key)
        if seed not in seed_codebooks:
            print("[seed=%d] building codebooks..." % seed, flush=True)
            cb_r = build_codebook_random(seed * 100003 + 99)
            cb_a = build_codebook_adversarial(seed * 100003 + 199)
            seed_codebooks[seed] = (cb_r, cb_a)
        cb_random, cb_adv = seed_codebooks[seed]

        # Resolve n_banks, k_per_bank for the arm
        if A in ("ARM_KNN_BASELINE", "ARM_NAIVE_SINGLE_BANK"):
            n_banks, k_per_bank = 1, K
        else:
            arrangements = ARRANGEMENTS_BY_K.get(K, [])
            match = [arr for arr in arrangements if arr[0] == A]
            if not match:
                print("[WARN] no arrangement for K=%d arm=%s; skipping" % (K, A), flush=True)
                continue
            _, n_banks, k_per_bank = match[0]

        try:
            print("  [run] %s ..." % key, flush=True)
            rec = run_unit(seed, K, R, A, n_banks, k_per_bank,
                            cb_random, cb_adv, _RESULTS_HOLDER["gpu_util"])
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"]), flush=True)
        except Exception as e:
            print("[WARN] %s failed: %s" % (key, e), flush=True)

    agg = aggregate_partials(out_dir, seeds=all_keys, run_config=run_config)
    units = [agg[k] for k in all_keys if k in agg]
    if not units:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "substrate-only-decode gate violated"

    v, vmsg, detail = compute_verdict(agg)
    print("\n[VERDICT] %s" % v, flush=True)
    print("[VERDICT_MSG] %s" % vmsg, flush=True)

    metrics = _build_metrics(v, vmsg, detail, units, atexit_synth=False)
    write_metrics(out_dir, metrics, results=units)
    print("[done] metrics.json written (%d units, %.1fs)" % (
        len(units), metrics["elapsed_s"]), flush=True)
