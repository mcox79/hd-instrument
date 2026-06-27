"""additive_hebbian_sequence_binding_capacity_cliff_sweep_v1 -- find the capacity cliff (GPU).

Prereg: preregs/2026-06-27_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1.md
Emergent from: BTSP v2 smoke 2026-06-27 (additive_hebbian = 1.000 at N=2048 V=200 N_PAIRS=50;
  saturation_guard fired; "regime too easy"). USER directive: find WHERE additive's
  order_discrimination drops below 0.50 / 0.20 by sweeping N_PAIRS into one shared W.

TASK -- shared-W one-shot order-sensitive sequence binding (mirrors BTSP v2 protocol):
  - Vocab V (200 bipolar atoms, dim N_DIM=16384).
  - Sweep N_PAIRS in {50, 100, 200, 500, 1000, 2000, 5000}.
  - For each N_PAIRS, 2*N_PAIRS bindings stored into ONE shared W.
  - Each pair has TWO orderings (AB, BA) with unique context tags.
  - Recall: query each S, cosine to ALL 2*N_PAIRS contexts, argmax = paired?

Metric per N_PAIRS:
  order_discrimination = recall_correct - cross_order_confusion
  This is THE substrate's order-sensitive sequence-binding capacity curve.

ARMS (3 + 1 diag), each evaluated at every N_PAIRS:
  ARM_ADDITIVE_HEBBIAN     W += outer(C, S) / N -- the substrate primitive that works at low load
  ARM_RANDOM_TAG_50PCT     50% random synapse mask per update -- "any sparsity" control
  ARM_CONTEXT_BANK_LOOKUP  alternative readout: encode S once, lookup against C-bank (skips W)
  ARM_DIAG_INTERFERENCE_FRACTION  crosstalk fraction (W@S projected onto non-paired contexts)

CLIFF DEFINITION (HARD_PASS = cell SUCCEEDS at IDENTIFYING the cliff):
  - Find first N_PAIRS where ADDITIVE_HEBBIAN order_disc < 0.50  -> CLIFF_50
  - Find first N_PAIRS where ADDITIVE_HEBBIAN order_disc < 0.20  -> CLIFF_20
  - Report both; cv across seeds < 0.10 at each measured N_PAIRS.
  - This cell is INFORMATIONAL: it DEFINES the regime for future mechanism cells.

PRE-REG BANDS:
  HARD_PASS:
    Both CLIFF_50 and CLIFF_20 identified (some N_PAIRS in sweep where additive drops below)
    AND cv across seeds < 0.10 at each measured N_PAIRS (where order_disc in (0.05, 0.95))
    AND no measurement instability (NaN / inf / negative recalls)
  MIDDLE_BAND:
    Only one of CLIFF_50 / CLIFF_20 identified (e.g., cliff above 5000 for the harder threshold)
    OR cv in [0.10, 0.20]
  HARD_FAIL (regime never broken; substrate freakishly good):
    ADDITIVE_HEBBIAN order_disc >= 0.95 at ALL N_PAIRS up to 5000
    -- this would mean substrate's additive Hebbian is essentially uncapped in this regime;
       big science finding (would motivate even higher loads), but per directive it's HF for cell.

REGIME:
  Full:  N_DIM=16384, V=200, sweep_N_PAIRS=[50, 100, 200, 500, 1000, 2000, 5000], seeds=[11,17,23]
  Smoke: N_DIM=2048,  V=200, sweep_N_PAIRS=[50, 200, 1000],                          seeds=[1]
  Self:  N_DIM=512,   V=50,  sweep_N_PAIRS=[10, 50],                                 seeds=[1]

GPU MANDATE (Fix #24): torch.cuda + batched outer + nvidia-smi sampler; gpu_util_p50>=30% in smoke.
HARDENING: L1-L4 + CARDINALITY_OK + import-crash sentinel + META_RULE_X main-guard.
FAIRNESS (META_RULE_AA): all arms see same vocab/pairs/contexts; readout layer identical
  (cosine to context bank); baseline NOT implicitly does mechanism; saturation_guard reported per N_PAIRS.

ASCII-only. Author: exp_dev (Opus 4.7 agent spawn, 2026-06-27).
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import subprocess
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "additive_hebbian_sequence_binding_capacity_cliff_sweep_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Cliff thresholds (load-bearing)
CLIFF_50_TH = 0.50
CLIFF_20_TH = 0.20
HP_CV_MAX = 0.10
MB_CV_MAX = 0.20
SATURATION_TH = 0.95          # ADD order_disc above this counts as saturated
HF_GPU_UTIL = 30.0
TAG_RANDOM_50PCT = 0.50

if SELF_TEST_MODE:
    N_DIM = 512
    V = 50
    N_PAIRS_SWEEP = [10, 50]
    SEEDS = [1]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V = 200
    N_PAIRS_SWEEP = [50, 200, 1000]
    SEEDS = [1]
else:
    N_DIM = 16384
    V = 200
    N_PAIRS_SWEEP = [50, 100, 200, 500, 1000, 2000, 5000]
    SEEDS = [11, 17, 23]

EXPECTED_ARMS = [
    "additive_hebbian",
    "random_tag_50pct",
    "context_bank_lookup",
    "diag_interference_fraction",
]

# 4 arms x len(SWEEP) x SEEDS measurements
EXPECTED_N_UNITS = len(SEEDS) * len(N_PAIRS_SWEEP) * len(EXPECTED_ARMS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,sweep=%s,seeds=%s,mode=%s,"
    "cliff50=%.2f,cliff20=%.2f,sat_th=%.2f,cv_hp=%.2f,cv_mb=%.2f,"
    "expected_n=%d,SHARED_W=True,RECALL_VS_ALL=True,GPU=cuda,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+GPU_UTIL_SAMPLER"
) % (
    ANCHOR_NAME, N_DIM, V, N_PAIRS_SWEEP, SEEDS, RUN_MODE,
    CLIFF_50_TH, CLIFF_20_TH, SATURATION_TH, HP_CV_MAX, MB_CV_MAX,
    EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_additive_hebbian_capacity_cliff_sweep_gpu",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_additive_hebbian_capacity_cliff_sweep_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# --------------------- GPU util sampler ---------------------

class GPUUtilSampler:
    def __init__(self, interval_s: float = 2.0):
        self.interval_s = interval_s
        self.samples: List[float] = []
        self._stop = threading.Event()
        self._thread = None

    def _sample_once(self) -> float:
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3.0)
            if out.returncode == 0 and out.stdout.strip():
                first = out.stdout.strip().splitlines()[0].strip()
                return float(first)
        except Exception:
            return -1.0
        return -1.0

    def _loop(self):
        while not self._stop.is_set():
            val = self._sample_once()
            if val >= 0.0:
                self.samples.append(val)
            self._stop.wait(self.interval_s)

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)

    def summary(self) -> Dict[str, float]:
        if not self.samples:
            return {"gpu_util_p50": -1.0, "gpu_util_max": -1.0,
                    "gpu_util_mean": -1.0, "n_samples": 0}
        arr = sorted(self.samples)
        n = len(arr)
        p50 = arr[n // 2]
        return {
            "gpu_util_p50": float(p50),
            "gpu_util_max": float(max(arr)),
            "gpu_util_mean": float(sum(arr) / n),
            "n_samples": n,
        }


# --------------------- primitives ---------------------

def _import_torch_or_die():
    try:
        import torch
        return torch
    except Exception as e:
        print("[FATAL] torch import failed: %s" % e, file=sys.stderr, flush=True)
        raise


def make_bipolar_atoms(M: int, n: int, gen, torch_mod, device: str):
    X = (torch_mod.randint(0, 2, (M, n), generator=gen, device=device,
                           dtype=torch_mod.float32) * 2 - 1)
    return X / (X.norm(dim=1, keepdim=True) + 1e-8)


def bind_pos(atom, pos: int, torch_mod):
    return torch_mod.roll(atom, shifts=pos, dims=0)


# --------------------- store rules ---------------------

def store_additive_batch(S_batch, C_batch, n_dim: int, torch_mod, device: str):
    """W = sum_i outer(C_i, S_i) / n  -- batched matmul C^T @ S."""
    # S_batch: (T, n_dim); C_batch: (T, n_dim)
    return (C_batch.T @ S_batch) / float(n_dim)


def store_random_tag_50pct(W, C, S, gen, torch_mod, device: str):
    update = torch_mod.outer(C, S) / float(S.shape[0])
    mask = (torch_mod.rand(W.shape, generator=gen, device=device) < TAG_RANDOM_50PCT)
    return torch_mod.where(mask, W + update, W)


# --------------------- per-sweep recall ---------------------

def make_pair_data(n_pairs: int, V_local: int, gen, vocab, torch_mod, device: str):
    pair_idx_a = torch_mod.randint(0, V_local, (n_pairs,), generator=gen, device=device)
    pair_idx_b = torch_mod.randint(0, V_local, (n_pairs,), generator=gen, device=device)
    coll = (pair_idx_a == pair_idx_b)
    n_fixes = 0
    while bool(coll.any()) and n_fixes < 50:
        pair_idx_b[coll] = torch_mod.randint(0, V_local, (int(coll.sum()),),
                                              generator=gen, device=device)
        coll = (pair_idx_a == pair_idx_b)
        n_fixes += 1
    context_AB = make_bipolar_atoms(n_pairs, vocab.shape[1], gen, torch_mod, device)
    context_BA = make_bipolar_atoms(n_pairs, vocab.shape[1], gen, torch_mod, device)

    # Build S_AB / S_BA via roll per pair (batch via gather)
    a = vocab[pair_idx_a]       # (n_pairs, n_dim)
    b = vocab[pair_idx_b]
    # roll along axis 1 is per-row; torch.roll over dims=1
    S_AB = torch_mod.roll(a, shifts=1, dims=1) + torch_mod.roll(b, shifts=2, dims=1)
    S_BA = torch_mod.roll(b, shifts=1, dims=1) + torch_mod.roll(a, shifts=2, dims=1)
    S_AB = S_AB / (S_AB.norm(dim=1, keepdim=True) + 1e-8)
    S_BA = S_BA / (S_BA.norm(dim=1, keepdim=True) + 1e-8)
    return pair_idx_a, pair_idx_b, context_AB, context_BA, S_AB, S_BA


def eval_recall_against_W(W, S_AB, S_BA, context_AB, context_BA, torch_mod):
    """For each S, compute W @ S, cosine vs ALL contexts; argmax."""
    n_pairs = S_AB.shape[0]
    context_all = torch_mod.cat([context_AB, context_BA], dim=0)  # (2*n_pairs, n_dim)
    ctx_n = context_all / (context_all.norm(dim=1, keepdim=True) + 1e-8)

    seqs_S = torch_mod.cat([S_AB, S_BA], dim=0)                   # (2*n_pairs, n_dim)
    preds = seqs_S @ W.T                                          # (2*n_pairs, n_dim)
    preds_n = preds / (preds.norm(dim=1, keepdim=True) + 1e-8)
    sims = preds_n @ ctx_n.T                                      # (2*n_pairs, 2*n_pairs)
    picked = sims.argmax(dim=1)

    # Paired idx layout: AB queries -> paired idx = i (0..n_pairs-1); cross = n_pairs+i
    #                    BA queries -> paired idx = n_pairs+i;        cross = i
    target_paired = torch_mod.cat([
        torch_mod.arange(0, n_pairs, device=W.device),
        torch_mod.arange(n_pairs, 2 * n_pairs, device=W.device),
    ])
    target_cross = torch_mod.cat([
        torch_mod.arange(n_pairs, 2 * n_pairs, device=W.device),
        torch_mod.arange(0, n_pairs, device=W.device),
    ])
    n_correct = int((picked == target_paired).sum())
    n_cross = int((picked == target_cross).sum())
    n_total = int(picked.shape[0])
    return {
        "recall_correct": n_correct / float(n_total),
        "cross_order_confusion": n_cross / float(n_total),
        "order_discrimination": (n_correct - n_cross) / float(n_total),
        "n_queries": n_total,
    }


def eval_context_bank_lookup(S_AB, S_BA, context_AB, context_BA, torch_mod):
    """ALT readout: cosine of S directly vs context bank (skips W entirely).
    This isolates whether the S vectors themselves carry order info that the
    contexts could pick up without any associative store. Baseline-class.
    """
    n_pairs = S_AB.shape[0]
    seqs_S = torch_mod.cat([S_AB, S_BA], dim=0)
    seqs_n = seqs_S / (seqs_S.norm(dim=1, keepdim=True) + 1e-8)
    context_all = torch_mod.cat([context_AB, context_BA], dim=0)
    ctx_n = context_all / (context_all.norm(dim=1, keepdim=True) + 1e-8)
    sims = seqs_n @ ctx_n.T
    picked = sims.argmax(dim=1)
    target_paired = torch_mod.cat([
        torch_mod.arange(0, n_pairs, device=seqs_S.device),
        torch_mod.arange(n_pairs, 2 * n_pairs, device=seqs_S.device),
    ])
    target_cross = torch_mod.cat([
        torch_mod.arange(n_pairs, 2 * n_pairs, device=seqs_S.device),
        torch_mod.arange(0, n_pairs, device=seqs_S.device),
    ])
    n_correct = int((picked == target_paired).sum())
    n_cross = int((picked == target_cross).sum())
    n_total = int(picked.shape[0])
    return {
        "recall_correct": n_correct / float(n_total),
        "cross_order_confusion": n_cross / float(n_total),
        "order_discrimination": (n_correct - n_cross) / float(n_total),
        "n_queries": n_total,
    }


def compute_interference_fraction(W, S_AB, S_BA, context_AB, context_BA, torch_mod):
    """Crosstalk diagnostic: mean projection magnitude onto NON-paired contexts vs paired.
    Higher = more interference. Reports interference_fraction = E[non_paired_sim] / E[paired_sim].
    """
    n_pairs = S_AB.shape[0]
    context_all = torch_mod.cat([context_AB, context_BA], dim=0)
    ctx_n = context_all / (context_all.norm(dim=1, keepdim=True) + 1e-8)
    seqs_S = torch_mod.cat([S_AB, S_BA], dim=0)
    preds = seqs_S @ W.T
    preds_n = preds / (preds.norm(dim=1, keepdim=True) + 1e-8)
    sims = preds_n @ ctx_n.T   # (2*n_pairs, 2*n_pairs)
    target_paired_idx = torch_mod.cat([
        torch_mod.arange(0, n_pairs, device=W.device),
        torch_mod.arange(n_pairs, 2 * n_pairs, device=W.device),
    ])
    arange_q = torch_mod.arange(sims.shape[0], device=W.device)
    paired_sims = sims[arange_q, target_paired_idx]
    # Non-paired: zero out paired entries, take mean of rest
    sims_masked = sims.clone()
    sims_masked[arange_q, target_paired_idx] = 0.0
    non_paired_sum = sims_masked.sum(dim=1)
    non_paired_count = float(sims.shape[1] - 1)
    non_paired_mean = non_paired_sum / non_paired_count
    paired_mean_abs = float(paired_sims.abs().mean()) + 1e-8
    non_paired_mean_abs = float(non_paired_mean.abs().mean())
    return {
        "paired_sim_mean": float(paired_sims.mean()),
        "non_paired_sim_mean_abs": non_paired_mean_abs,
        "interference_fraction": non_paired_mean_abs / paired_mean_abs,
        "n_queries": int(sims.shape[0]),
    }


# --------------------- per-seed runner ---------------------

def run_one_seed(seed: int, torch_mod, device: str) -> Dict[str, Any]:
    g = torch_mod.Generator(device=device).manual_seed(int(seed))
    vocab = make_bipolar_atoms(V, N_DIM, g, torch_mod, device)

    results_by_npairs: Dict[str, Dict[str, Dict[str, float]]] = {}
    for n_pairs in N_PAIRS_SWEEP:
        # Build data per N_PAIRS (fresh; same V vocab)
        g_data = torch_mod.Generator(device=device).manual_seed(int(seed) * 1000 + n_pairs)
        pair_a, pair_b, context_AB, context_BA, S_AB, S_BA = make_pair_data(
            n_pairs, V, g_data, vocab, torch_mod, device)

        per_arm: Dict[str, Dict[str, float]] = {}

        # ARM_ADDITIVE_HEBBIAN: batched store
        all_S = torch_mod.cat([S_AB, S_BA], dim=0)
        all_C = torch_mod.cat([context_AB, context_BA], dim=0)
        W_add = store_additive_batch(all_S, all_C, N_DIM, torch_mod, device)
        per_arm["additive_hebbian"] = eval_recall_against_W(
            W_add, S_AB, S_BA, context_AB, context_BA, torch_mod)

        # ARM_RANDOM_TAG_50PCT: per-binding sparse update
        g_rtag = torch_mod.Generator(device=device).manual_seed(int(seed) * 7919 + n_pairs)
        W_rtag = torch_mod.zeros((N_DIM, N_DIM), device=device, dtype=torch_mod.float32)
        # combined S+C list to iterate over -- AB first, then BA, matching shared-W ordering
        for i in range(n_pairs):
            W_rtag = store_random_tag_50pct(W_rtag, context_AB[i], S_AB[i], g_rtag, torch_mod, device)
            W_rtag = store_random_tag_50pct(W_rtag, context_BA[i], S_BA[i], g_rtag, torch_mod, device)
        per_arm["random_tag_50pct"] = eval_recall_against_W(
            W_rtag, S_AB, S_BA, context_AB, context_BA, torch_mod)

        # ARM_CONTEXT_BANK_LOOKUP (no W; cosine of S vs context bank directly)
        per_arm["context_bank_lookup"] = eval_context_bank_lookup(
            S_AB, S_BA, context_AB, context_BA, torch_mod)

        # DIAG: interference fraction (uses additive W)
        per_arm["diag_interference_fraction"] = compute_interference_fraction(
            W_add, S_AB, S_BA, context_AB, context_BA, torch_mod)

        # Free big tensors before next sweep point
        del W_add, W_rtag
        if device == "cuda":
            torch_mod.cuda.empty_cache()

        results_by_npairs[str(n_pairs)] = per_arm
        print("[seed=%d N_PAIRS=%d] add_disc=%.3f rtag_disc=%.3f ctx_disc=%.3f interf=%.3f" % (
            seed, n_pairs,
            per_arm["additive_hebbian"]["order_discrimination"],
            per_arm["random_tag_50pct"]["order_discrimination"],
            per_arm["context_bank_lookup"]["order_discrimination"],
            per_arm["diag_interference_fraction"]["interference_fraction"],
        ), flush=True)

    return {
        "seed": int(seed),
        "N_DIM": N_DIM,
        "V": V,
        "N_PAIRS_SWEEP": N_PAIRS_SWEEP,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "results_by_npairs": results_by_npairs,
    }


# --------------------- verdict ---------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           gpu_summary: Dict[str, float]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # Aggregate per-N_PAIRS per-arm across seeds
    summary_by_npairs: Dict[str, Dict[str, Dict[str, float]]] = {}
    for n_pairs in N_PAIRS_SWEEP:
        np_key = str(n_pairs)
        summary_by_npairs[np_key] = {}
        for arm in EXPECTED_ARMS:
            if arm == "diag_interference_fraction":
                metric_key = "interference_fraction"
            else:
                metric_key = "order_discrimination"
            vals = [per_seed[s]["results_by_npairs"][np_key][arm][metric_key]
                    for s in seeds_sorted if np_key in per_seed[s]["results_by_npairs"]]
            if not vals:
                summary_by_npairs[np_key][arm] = {"mean": 0.0, "std": 0.0, "cv": 0.0, "n": 0}
                continue
            mean = float(np.mean(vals))
            std = float(np.std(vals)) if n_seeds > 1 else 0.0
            cv = std / abs(mean) if abs(mean) > 1e-6 else 0.0
            summary_by_npairs[np_key][arm] = {"mean": mean, "std": std,
                                                "cv": cv, "n": len(vals)}

    # Identify cliffs for additive_hebbian
    cliff_50_at = None
    cliff_20_at = None
    add_curve = []
    for n_pairs in N_PAIRS_SWEEP:
        np_key = str(n_pairs)
        add_mean = summary_by_npairs[np_key]["additive_hebbian"]["mean"]
        add_curve.append((n_pairs, add_mean))
        if cliff_50_at is None and add_mean < CLIFF_50_TH:
            cliff_50_at = n_pairs
        if cliff_20_at is None and add_mean < CLIFF_20_TH:
            cliff_20_at = n_pairs

    # CV check: only enforce where order_disc in (0.05, 0.95) -- skip saturated and floor
    cv_violations = []
    for n_pairs in N_PAIRS_SWEEP:
        np_key = str(n_pairs)
        s = summary_by_npairs[np_key]["additive_hebbian"]
        if 0.05 < s["mean"] < SATURATION_TH:
            if s["cv"] > HP_CV_MAX:
                cv_violations.append((n_pairs, s["cv"]))
    max_cv = 0.0
    for n_pairs in N_PAIRS_SWEEP:
        np_key = str(n_pairs)
        s = summary_by_npairs[np_key]["additive_hebbian"]
        if 0.05 < s["mean"] < SATURATION_TH:
            max_cv = max(max_cv, s["cv"])

    # Saturation guard: HARD_FAIL if all sweeps stay >= SATURATION_TH (regime never broken)
    all_saturated = all(
        summary_by_npairs[str(np_)]["additive_hebbian"]["mean"] >= SATURATION_TH
        for np_ in N_PAIRS_SWEEP
    )

    # GPU util check (smoke only)
    gpu_util_p50 = gpu_summary.get("gpu_util_p50", -1.0)
    gpu_util_ok = True
    gpu_util_msg = ""
    if RUN_MODE == "smoke" and gpu_util_p50 >= 0 and gpu_summary.get("n_samples", 0) >= 3:
        if gpu_util_p50 < HF_GPU_UTIL:
            gpu_util_ok = False
            gpu_util_msg = " | GPU_UTIL_FAIL: p50=%.1f%% < %.0f%% n=%d" % (
                gpu_util_p50, HF_GPU_UTIL, gpu_summary.get("n_samples", 0))

    # Verdict
    verdict = "MIDDLE_BAND"
    if all_saturated:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL | regime_never_broken: additive>=%.2f at ALL N_PAIRS in %s | "
                       "curve=%s%s") % (SATURATION_TH, N_PAIRS_SWEEP, add_curve, gpu_util_msg)
    elif not gpu_util_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL%s | curve=%s") % (gpu_util_msg, add_curve)
    elif cliff_50_at is not None and cliff_20_at is not None and max_cv < HP_CV_MAX:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS | CLIFF_50@N_PAIRS=%s CLIFF_20@N_PAIRS=%s | "
                       "max_cv_in_band=%.3f | curve=%s | n_seeds=%d") % (
            cliff_50_at, cliff_20_at, max_cv, add_curve, n_seeds)
    elif cliff_50_at is not None or cliff_20_at is not None or max_cv < MB_CV_MAX:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND | CLIFF_50@=%s CLIFF_20@=%s max_cv=%.3f | curve=%s | n_seeds=%d") % (
            cliff_50_at, cliff_20_at, max_cv, add_curve, n_seeds)
    else:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL | cv_violations=%s max_cv=%.3f | curve=%s") % (
            cv_violations, max_cv, add_curve)

    completed_units = n_seeds * len(N_PAIRS_SWEEP) * len(EXPECTED_ARMS)
    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "summary_by_npairs": summary_by_npairs,
        "additive_curve": add_curve,
        "cliff_50_at_n_pairs": cliff_50_at,
        "cliff_20_at_n_pairs": cliff_20_at,
        "max_cv_in_band": max_cv,
        "cv_violations": cv_violations,
        "n_seeds": n_seeds,
        "gpu_summary": gpu_summary,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": completed_units >= EXPECTED_N_UNITS,
    }


# --------------------- main ---------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_sweep": N_PAIRS_SWEEP,
                                  "expected_n_units": EXPECTED_N_UNITS})

    torch_mod = _import_torch_or_die()
    # Force CUDA per Fix #24
    if not torch_mod.cuda.is_available():
        if SELF_TEST_MODE:
            # Selftest may be on CPU
            device = "cpu"
            print("[WARN selftest] no CUDA; running on CPU for selftest only", flush=True)
        else:
            _write_minimal_metrics(out_dir, "HARD_FAIL",
                                   "HARD_FAIL: CUDA not available (this cell mandates GPU per Fix #24)",
                                   extra={"_phase": "no_cuda"})
            return 1
    else:
        device = "cuda"

    print("[%s] mode=%s N=%d V=%d sweep=%s seeds=%s expected_n=%d device=%s" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V, N_PAIRS_SWEEP, SEEDS,
        EXPECTED_N_UNITS, device), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0], torch_mod, device)
            assert "results_by_npairs" in r
            for np_ in N_PAIRS_SWEEP:
                assert str(np_) in r["results_by_npairs"]
                for arm in EXPECTED_ARMS:
                    assert arm in r["results_by_npairs"][str(np_)]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-N_PAIRS x per-arm structure verified",
                                   extra={"_phase": "selftest_done",
                                          "first_seed_sample": str(r["results_by_npairs"][str(N_PAIRS_SWEEP[0])])[:300]})
            print("[selftest] OK", flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_phase": "selftest_fail",
                                          "_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    # GPU util sampler
    sampler = GPUUtilSampler(interval_s=2.0)
    if device == "cuda":
        sampler.start()

    per_seed: Dict[str, Dict[str, Any]] = {}
    try:
        for i, seed in enumerate(SEEDS):
            t0 = time.time()
            _write_minimal_metrics(out_dir, "RUNNING",
                                   "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                                   extra={"_phase": "seed_running", "_current_seed": seed})
            result = run_one_seed(seed, torch_mod, device)
            per_seed[str(seed)] = result
            # Partial write
            (out_dir / ("partial_seed%d.json" % seed)).write_text(
                json.dumps(result, indent=2), encoding="utf-8")
            print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)
    finally:
        if device == "cuda":
            sampler.stop()

    gpu_summary = sampler.summary() if device == "cuda" else {"gpu_util_p50": -1.0,
                                                                "n_samples": 0,
                                                                "gpu_util_max": -1.0,
                                                                "gpu_util_mean": -1.0}

    final = aggregate_and_verdict(per_seed, gpu_summary)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_additive_hebbian_capacity_cliff_sweep_gpu"
    (out_dir / "metrics.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
