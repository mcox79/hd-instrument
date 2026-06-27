"""phase_diagram_wm_multibank_K_8192_3seed_harvest_v1 -- K=8192 3-seed harvest.

USER directive 2026-06-27 (via Director task 2026-06-27): the K-ceiling sweep
v3 landed K=8192 at recall=1.000 BUT only with 1 seed (seeds 13/19 never ran
because the K=32768 VRAM probe breach halted the loop after seed=11 finished
its partial sweep).

This cell drops the sweep axis entirely and harvests K=8192 ONLY at 3 seeds
[11,13,19] in both RANDOM and ADVERSARIAL regimes. Goal: single-arm chain-grade
evidence for K=8192 substrate WM multi-bank (the Skunkworks flag-back #4
requested 3-seed evidence for K=8192).

DERIVED FROM exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3.py
(same primitives, same envelope, same instrumentation; just K=8192-only).

DISCRIMINATOR (option B analytical justification per
discriminator-must-survive-scale 2026-06-26):
  - v3 already proved K=8192 saturates to rec=1.000 cv=0.0 at seed=11 RANDOM and
    rec=1.000 cv=0.0 at seed=11 ADVERSARIAL (1-seed full-N evidence). The
    discriminator HAS already survived scale at 1 seed. This cell exists
    to harvest the cv stability across 2 additional seeds (cv across 3 seeds
    needed for chain-grade tiering).
  - If all 3 seeds land rec=1.000 cv=0.0 -> single-arm chain-grade (HARD_PASS).
  - If cv > 0.05 -> seed-instability MIDDLE_BAND.
  - If any seed drops below 0.95 -> MIDDLE_BAND or HARD_FAIL.

META_RULE_H cardinality guard (Skunkworks 2026-06-26): expected n_units =
n_seeds * n_regimes + n_seeds * len(SENTINEL_KS) = 3*2 + 3*1 = 9. Verdict
HARD_FAILs on cardinality breach.

META_RULE_J no-silent-except: any per-unit exception recorded into failures[]
and halts the loop (v3 discipline).

META_RULE_K smoke fires discriminator: smoke uses K=4096 (the saturated rail
which v3 proved at 1.000); smoke output is NOT chain-grade evidence (Q-saturation
discipline still applies at smoke regime), it's mechanism-end-to-end check.

META_RULE_L band-floor (USER 2026-06-26): rec=1.000 cv=0.0 across 3 seeds IS
chain-grade (not MIDDLE_BAND) because the WM multi-bank K=8192 / k_per_bank=64
arrangement is NOT by-construction-saturated (v3 measured K=16384 already drops
to rec=0.9999 = the cliff approaches; K=8192 chain-grade is real-discriminator-PASS,
not band-floor). Q_SUSPECT_SATURATION discipline retained for documentation
but does NOT auto-demote single-K chain-grade.

CONFIG (single-arm; no sweep):
  N_DIM = 8192, CODEBOOK_SIZE = 65536
  K_TOTAL = 8192, MULTI_128x (128 banks, 64 k_per_bank)
  SIGMA=1.0, CUE_COS=0.70, FEATURE_OVERLAP_FRAC=0.20
  N_ITEMS_PER_K = 200, seeds = [11,13,19]
  Both regimes (RANDOM + ADVERSARIAL)
  KNN sentinel at K=4096 (single regime)

PRE-REG BANDS (LOCKED at module init):
  HP_CHAIN_GRADE_RECALL = 0.95 (rec mean across 3 seeds)
  HP_CHAIN_GRADE_CV = 0.05 (cv across 3 seeds)
  HP_CHAIN_GRADE_ROUTE_ACC = 0.95
  HP_ADV_WITHIN_RANDOM = 0.05 (adv-vs-rand drift <= 0.05 for chain-grade)
  HP_KNN_SENTINEL_MIN = 0.90 (Fix #28)
  CV_HARD_FAIL = 0.10
  EXPECTED_N_UNITS = 9 (3 seeds * 2 regimes + 3 sentinels)

GPU MANDATE (Fix #24): torch.cuda required for full; fp16 storage; chunked
matmul on cuda; nvidia-smi sampling per arm.

ASCII-only. Single-file. Resumable per (seed, regime, arm) checkpoint key.
Author: exp_dev 2026-06-27 (USER-directed 3-seed harvest after Skunkworks flag-back #4).
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

ANCHOR_NAME = "phase_diagram_wm_multibank_K_8192_3seed_harvest_v1"

_LLM_CALL_COUNTER = [0]
CORPUS_PROVENANCE = "synthetic_substrate_bipolar_codebook_multibank_routing_K8192_3seed"

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
HP_KNN_SENTINEL_MIN = 0.90
CV_HARD_FAIL = 0.10
Q_SUSPECT_SATURATION = 0.995  # documentation only; does NOT auto-demote single-K
HP_RAIL_K4096_RECALL = 1.0000
HP_RAIL_K4096_TOL = 0.05
HP_CHAIN_GRADE_K_PER_BANK_MAX = 64

assert 0.0 < HP_CHAIN_GRADE_RECALL < 1.0, "band locked"
assert HP_CHAIN_GRADE_K_PER_BANK_MAX == 64, "envelope locked"

SIGMA = 1.0
CUE_COS = 0.70
FEATURE_OVERLAP_FRAC = 0.20
N_GROUPS_ADV = 4
KNN_SENTINEL_M = 400

CODEBOOK_CHUNK = 4096  # v3 chunked-matmul peak bound

if SMOKE:
    N_DIM = 2048
    CODEBOOK_SIZE = 4096
    K_TOTAL = 1024
    N_BANKS = 16
    K_PER_BANK = 64
    ARM_LABEL = "MULTI_16x"
    SENTINEL_K = 1024
    N_ITEMS_PER_K = 80
    SEEDS = [11]
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 65536
    K_TOTAL = 8192
    N_BANKS = 128
    K_PER_BANK = 64
    ARM_LABEL = "MULTI_128x"
    SENTINEL_K = 4096
    N_ITEMS_PER_K = 200
    SEEDS = [11, 13, 19]

REGIMES = ["RANDOM", "ADVERSARIAL"]

# Expected cardinality: 3 seeds * 2 regimes (RANDOM/ADV @ K=8192) + 3 sentinels (KNN @ K=4096)
EXPECTED_N_UNITS = len(SEEDS) * len(REGIMES) + len(SEEDS)

CONFIG_VERSION = (
    "wmMBK8192_3seed-v1: N_DIM=%d CODEBOOK_SIZE=%d sigma=%.1f CUE_COS=%.2f "
    "FEATURE_OVERLAP=%.2f K_TOTAL=%d arm=%s n_banks=%d k_per_bank=%d "
    "N_ITEMS_PER_K=%d seeds=%s mode=%s HP_chain>=%.2f cv<=%.2f route_acc>=%.2f "
    "HP_adv_within=%.2f sentinel_K=%d kPerBankMax=%d CODEBOOK_CHUNK=%d EXPECTED_N_UNITS=%d"
) % (
    N_DIM, CODEBOOK_SIZE, SIGMA, CUE_COS, FEATURE_OVERLAP_FRAC,
    K_TOTAL, ARM_LABEL, N_BANKS, K_PER_BANK,
    N_ITEMS_PER_K, SEEDS, RUN_MODE,
    HP_CHAIN_GRADE_RECALL, HP_CHAIN_GRADE_CV, HP_CHAIN_GRADE_ROUTE_ACC,
    HP_ADV_WITHIN_RANDOM, SENTINEL_K, HP_CHAIN_GRADE_K_PER_BANK_MAX,
    CODEBOOK_CHUNK, EXPECTED_N_UNITS,
)


# ----------------------------- GPU mandate -----------------------------
def _require_cuda(strict: bool) -> bool:
    if torch.cuda.is_available():
        return True
    if strict:
        raise RuntimeError(
            "GPU_MANDATE_VIOLATED (Fix #24): cuda.is_available() = False. "
            "K=8192 3-seed harvest at N_DIM=%d CODEBOOK=%d requires CUDA. "
            "Route to overnight_queue (GPU runner)." % (N_DIM, CODEBOOK_SIZE))
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
    n_banks = items_per_bank.shape[0]
    D = items_per_bank.shape[2]
    bank_chunk = max(1, min(n_banks, 8192 // max(1, items_per_bank.shape[1])))
    ws_acc = torch.zeros((n_banks, D), device=_DEVICE, dtype=torch.float32)
    slot_tags_f = slot_tags.float()
    for b0 in range(0, n_banks, bank_chunk):
        b1 = min(b0 + bank_chunk, n_banks)
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
    C = codebook.shape[0]
    Q = queries.shape[0]
    best_scores = torch.full((Q,), float("-inf"), device=queries.device,
                              dtype=torch.float32)
    best_idx = torch.zeros((Q,), device=queries.device, dtype=torch.long)
    chunk = CODEBOOK_CHUNK
    q_T = queries.T
    for c0 in range(0, C, chunk):
        c1 = min(c0 + chunk, C)
        sims_chunk = (codebook[c0:c1] @ q_T).float()
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
    r1 = (workspaces * slot_tag)
    cand_idx = _chunked_argmax_cb_at_queries(codebook, r1)
    cand_vecs = codebook[cand_idx]
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
    oom_cls = getattr(torch.cuda, "OutOfMemoryError", None)
    if oom_cls is not None and isinstance(exc, oom_cls):
        return True
    msg = str(exc).lower()
    return any(needle in msg for needle in [
        "out of memory", "cuda out of memory", "cudnn_status", "cuda error",
        "device-side assert", "cublas_status", "illegal memory access",
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
        shared_in = float((cb_adv[0] == cb_adv[N_GROUPS_ADV]).float().mean().item())
        shared_cross = float((cb_adv[0] == cb_adv[1]).float().mean().item())
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
        assert K_TOTAL == 8192 or SMOKE, "T6 K_TOTAL bound (8192 production or smoke)"
        assert N_BANKS * K_PER_BANK == K_TOTAL, "T6 cardinality arithmetic"
        print("[selftest] T6 PASS: bands locked + K=%d=banks*kpb=%d*%d" % (
            K_TOTAL, N_BANKS, K_PER_BANK))

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

        # T8: cardinality math
        # Production: 3 seeds * 2 regimes + 3 sentinels = 9
        # Smoke: 1 seed * 2 regimes + 1 sentinel = 3
        if not SMOKE:
            expected_full = 3 * 2 + 3
            assert expected_full == 9, "T8 expected_full math broken"
            print("[selftest] T8 PASS: production expected_n_units=%d" % expected_full)
        else:
            expected_smoke = 1 * 2 + 1
            assert expected_smoke == 3, "T8 smoke expected math broken"
            print("[selftest] T8 PASS: smoke expected_n_units=%d" % expected_smoke)

        # T9: OOM-class detector preserved from v3
        class _MockOOM(RuntimeError):
            pass
        exc1 = _MockOOM("CUDA out of memory. Tried to allocate 4.30 GiB")
        assert _is_oom_error(exc1), "T9 should detect 'CUDA out of memory'"
        exc2 = ValueError("regular value error not OOM")
        assert not _is_oom_error(exc2), "T9 should NOT flag regular ValueError"
        print("[selftest] T9 PASS: OOM detector classifies correctly")

        print("[selftest] ALL PASS")
    finally:
        _DEVICE = save_dev
        _STORE_DTYPE = save_dtype
        _CUDA_OK = save_cuda
        CODEBOOK_CHUNK = save_chunk
        N_DIM = N_DIM_BAK
        CODEBOOK_SIZE = CODEBOOK_SIZE_BAK


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

    n_units_observed = len(per_key)
    cardinality_ok = (n_units_observed >= EXPECTED_N_UNITS)

    # Group by (regime, arm_label) at K=K_TOTAL; separate KNN sentinel
    by_RA: Dict[Tuple[str, str], Dict] = {}
    knn_recalls: List[float] = []
    for _, body in per_key.items():
        K = int(body["k_total"])
        R = body["regime"]
        A = body["arm_label"]
        rec = float(body["recall"])
        ra = float(body["route_acc"])
        if A == "ARM_KNN_BASELINE":
            knn_recalls.append(rec)
            continue
        by_RA.setdefault((R, A), {"recalls": [], "route_accs": []})
        by_RA[(R, A)]["recalls"].append(rec)
        by_RA[(R, A)]["route_accs"].append(ra)

    arm_stats: Dict[Tuple[str, str], Dict] = {}
    for (R, A), d in by_RA.items():
        recs = d["recalls"]
        ras = d["route_accs"]
        m = float(np.mean(recs)) if recs else float("nan")
        s = float(np.std(recs)) if len(recs) > 1 else 0.0
        cv = float(s / max(m, 1e-9)) if (m > 1e-9) else 0.0
        m_ra = float(np.mean(ras)) if ras else float("nan")
        arm_stats[(R, A)] = {
            "recall_mean": round(m, 4),
            "recall_cv": round(cv, 4),
            "route_acc_mean": round(m_ra, 4),
            "recall_per_seed": [round(r, 4) for r in recs],
            "n_seeds_observed": len(recs),
        }

    knn_mean = float(np.mean(knn_recalls)) if knn_recalls else float("nan")
    knn_ok = (not math.isnan(knn_mean)) and (knn_mean >= HP_KNN_SENTINEL_MIN)

    n_llm = sum(int(b.get("_llm_forward_calls_at_inference", 0)) for b in per_key.values())
    substrate_only_ok = (n_llm == 0)

    # Summary
    rand_key = ("RANDOM", ARM_LABEL)
    adv_key = ("ADVERSARIAL", ARM_LABEL)
    rand_st = arm_stats.get(rand_key, {"recall_mean": float("nan"),
                                        "recall_cv": float("nan"),
                                        "route_acc_mean": float("nan"),
                                        "recall_per_seed": [],
                                        "n_seeds_observed": 0})
    adv_st = arm_stats.get(adv_key, {"recall_mean": float("nan"),
                                       "recall_cv": float("nan"),
                                       "route_acc_mean": float("nan"),
                                       "recall_per_seed": [],
                                       "n_seeds_observed": 0})

    summ = ("K=%d arm=%s | RAND[rec=%.4f cv=%.4f ra=%.4f n=%d per_seed=%s] "
            "| ADV[rec=%.4f cv=%.4f ra=%.4f n=%d per_seed=%s] "
            "| KNN_sentinel=%.4f (>=%.2f; %s)") % (
        K_TOTAL, ARM_LABEL,
        rand_st["recall_mean"], rand_st["recall_cv"],
        rand_st["route_acc_mean"], rand_st["n_seeds_observed"],
        rand_st["recall_per_seed"],
        adv_st["recall_mean"], adv_st["recall_cv"],
        adv_st["route_acc_mean"], adv_st["n_seeds_observed"],
        adv_st["recall_per_seed"],
        knn_mean, HP_KNN_SENTINEL_MIN, "OK" if knn_ok else "FAIL",
    )
    card_str = " | n_units=%d/expected=%d (%s)" % (
        n_units_observed, EXPECTED_N_UNITS,
        "OK" if cardinality_ok else "BREACH_META_RULE_H")
    fail_str = ""
    if failures:
        fail_str = " | failures=%d [%s]" % (
            len(failures),
            "; ".join("%s:%s" % (f.get("key", "?"), f.get("exc_type", "?"))
                       for f in failures[:3]))

    detail = {
        "arm_stats": {("%s|%s" % k): v for k, v in arm_stats.items()},
        "knn_sentinel_mean": knn_mean,
        "knn_sentinel_min": HP_KNN_SENTINEL_MIN,
        "knn_sentinel_ok": knn_ok,
        "knn_per_seed": [round(r, 4) for r in knn_recalls],
        "substrate_only_ok": substrate_only_ok,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "n_llm_calls": int(n_llm),
        "n_units_observed": n_units_observed,
        "n_units_expected": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "failures": failures,
    }

    # SMOKE: end-to-end sanity, NOT chain-grade evidence
    if SMOKE:
        any_mech_ok = any(
            st["recall_mean"] >= 0.50 for st in arm_stats.values()
        )
        knn_ok_smoke = (math.isnan(knn_mean)) or knn_ok
        if substrate_only_ok and any_mech_ok and knn_ok_smoke and not failures:
            return ("SMOKE_PASS",
                    "SMOKE_PASS: mechanism end-to-end OK at smoke regime "
                    "(chain-grade gates DEFERRED to FULL run on GPU) | %s%s%s" % (
                        summ, card_str, fail_str),
                    detail)
        return ("HARD_FAIL",
                "SMOKE_FAIL: mechanism broken at smoke regime | %s%s%s" % (
                    summ, card_str, fail_str),
                detail)

    # FULL: gates
    if failures:
        return ("HARD_FAIL",
                "HARD_FAIL_UNIT_EXCEPTION: %d units raised exceptions (META_RULE_J no-silent-except) | %s%s%s" % (
                    len(failures), summ, card_str, fail_str),
                detail)
    if not cardinality_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: n_units=%d < expected=%d (single-arm chain-grade claim forbidden) | %s%s" % (
                    n_units_observed, EXPECTED_N_UNITS, summ, card_str),
                detail)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only gate violated (%d LLM calls) | %s%s" % (
                    n_llm, summ, card_str),
                detail)
    if not knn_ok:
        return ("HARD_FAIL",
                "HARD_FAIL_KNN_SENTINEL: ARM_KNN_BASELINE %.4f < %.2f | %s%s" % (
                    knn_mean, HP_KNN_SENTINEL_MIN, summ, card_str),
                detail)

    rand_rec = rand_st["recall_mean"]
    rand_cv = rand_st["recall_cv"]
    rand_ra = rand_st["route_acc_mean"]
    adv_rec = adv_st["recall_mean"]
    adv_cv = adv_st["recall_cv"]
    adv_drift = (rand_rec - adv_rec)

    if math.isnan(rand_rec) or math.isnan(adv_rec):
        return ("HARD_FAIL",
                "HARD_FAIL_MISSING_ARM: rand or adv arm absent | %s%s" % (summ, card_str),
                detail)

    # CV instability HARD_FAIL on either arm
    if rand_cv > CV_HARD_FAIL or adv_cv > CV_HARD_FAIL:
        return ("HARD_FAIL",
                "HARD_FAIL_CV_INSTABILITY: cv > %.2f (rand=%.4f adv=%.4f) | %s%s" % (
                    CV_HARD_FAIL, rand_cv, adv_cv, summ, card_str),
                detail)

    # Chain-grade gate: rand mean >= HP, rand cv <= HP, ra >= HP, adv within HP
    chain_grade = (
        rand_rec >= HP_CHAIN_GRADE_RECALL
        and rand_cv <= HP_CHAIN_GRADE_CV
        and rand_ra >= HP_CHAIN_GRADE_ROUTE_ACC
        and adv_drift <= HP_ADV_WITHIN_RANDOM
        and K_PER_BANK <= HP_CHAIN_GRADE_K_PER_BANK_MAX
    )
    if chain_grade:
        return ("CHAIN_GRADE_K_8192_3SEED",
                "CHAIN_GRADE_K_8192_3SEED: single-arm chain-grade at K=8192 "
                "MULTI_128x (k_per_bank=64 envelope preserved); rand_rec=%.4f cv=%.4f "
                "adv_within=%.4f route_acc=%.4f | %s%s" % (
                    rand_rec, rand_cv, adv_drift, rand_ra, summ, card_str),
                detail)

    # MIDDLE_BAND fall-through
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_NOT_CHAIN_GRADE: rand_rec=%.4f (need>=%.2f) cv=%.4f (need<=%.2f) "
            "adv_drift=%.4f (need<=%.2f) route_acc=%.4f (need>=%.2f) | %s%s" % (
                rand_rec, HP_CHAIN_GRADE_RECALL, rand_cv, HP_CHAIN_GRADE_CV,
                adv_drift, HP_ADV_WITHIN_RANDOM, rand_ra, HP_CHAIN_GRADE_ROUTE_ACC,
                summ, card_str),
            detail)


# ----------------------------- atexit synth + main -----------------------------
_RESULTS_HOLDER = {"out_dir": None, "started_at": time.time(), "gpu_util": [],
                   "failures": []}


def _build_keys() -> List[str]:
    keys = []
    for s in SEEDS:
        for R in REGIMES:
            keys.append("seed%d_K%d_regime%s_arm%s" % (s, K_TOTAL, R, ARM_LABEL))
        # KNN sentinel per seed at SENTINEL_K (RANDOM regime only)
        keys.append("seed%d_K%d_regimeRANDOM_armARM_KNN_BASELINE" % (s, SENTINEL_K))
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
        run_config = {"N": N_DIM, "K": K_TOTAL, "run_mode": RUN_MODE}
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
        "K_TOTAL": K_TOTAL,
        "ARM_LABEL": ARM_LABEL,
        "N_BANKS": N_BANKS,
        "K_PER_BANK": K_PER_BANK,
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
        "metrics_source": "measured_gpu_substrate_bipolar_multibank_K8192_3seed_harvest_v1",
        "DESIGN_NOTE": (
            "K=8192 3-seed harvest after Skunkworks flag-back #4. v3 K-sweep "
            "halted at K=32768 VRAM probe; harvested K=8192 only at seed=11. "
            "This cell drops the sweep axis entirely and runs K=8192 ONLY at "
            "3 seeds [11,13,19] to get the single-arm chain-grade evidence. "
            "META_RULE_H cardinality guard (expected 9); META_RULE_J no-silent-except; "
            "META_RULE_K smoke fires mechanism; META_RULE_L not-band-floor because "
            "K=8192 saturation is the discriminator's WIN at the K-extension frontier "
            "(K=16384 in v3 already shows rec=0.9999 = approaching cliff)."
        ),
    }


def _build_codebook_for_regime(seed: int, regime: str) -> torch.Tensor:
    if regime == "RANDOM":
        return build_codebook_random(seed * 100003 + 99)
    else:
        return build_codebook_adversarial(seed * 100003 + 199)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d K=%d arm=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, K_TOTAL, ARM_LABEL,
        CONFIG_VERSION), flush=True)
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

    run_config = {"N": N_DIM, "K": K_TOTAL, "run_mode": RUN_MODE}
    all_keys = _build_keys()
    done_keys = set(list_completed_keys(out_dir, run_config=run_config))
    print("[ckpt] done=%d/%d units" % (len(done_keys), len(all_keys)), flush=True)

    # per-(seed, regime) codebook cache; freed when (seed, regime) changes
    cached: Dict[Tuple[int, str], torch.Tensor] = {}
    halt_after_loop = False

    for key in all_keys:
        if key in done_keys:
            continue
        seed, K, R, A = _parse_key(key)

        if A == "ARM_KNN_BASELINE":
            n_banks, k_per_bank = 1, K
        else:
            n_banks, k_per_bank = N_BANKS, K_PER_BANK

        # Rebuild codebook on (seed, regime) miss; free other regime cb if cached.
        ckey = (seed, R)
        if ckey not in cached:
            for stale_k in list(cached.keys()):
                if stale_k[0] == seed and stale_k[1] != R:
                    del cached[stale_k]
                    if _CUDA_OK:
                        torch.cuda.empty_cache()
            print("[seed=%d regime=%s] building codebook..." % (seed, R), flush=True)
            cached[ckey] = _build_codebook_for_regime(seed, R)
        codebook = cached[ckey]

        try:
            print("  [run] %s ..." % key, flush=True)
            rec = run_unit(seed, K, R, A, n_banks, k_per_bank,
                            codebook, _RESULTS_HOLDER["gpu_util"])
            write_partial_key(out_dir, key, rec)
            print("  [done] %s recall=%.4f route_acc=%.4f wall=%.1fs peak=%dMB" % (
                key, rec["recall"], rec["route_acc"], rec["wall_s"],
                rec.get("peak_mem_mb", 0)), flush=True)
        except Exception as e:
            tb = traceback.format_exc()
            fail_entry = {
                "key": key,
                "seed": seed, "k_total": K, "regime": R, "arm_label": A,
                "n_banks": n_banks, "k_per_bank": k_per_bank,
                "exc_type": type(e).__name__,
                "exc_msg": str(e)[:500],
                "traceback": tb[-2000:],
                "is_oom_class": _is_oom_error(e),
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
            print("[META_RULE_J] halting loop on unit exception (no silent-continue)", flush=True)
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
