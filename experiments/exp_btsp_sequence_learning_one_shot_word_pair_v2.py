"""btsp_sequence_learning_one_shot_word_pair_v2 -- BTSP on order-sensitive sequence binding, SHARED-W capacity regime (GPU).

Prereg: preregs/2026-06-27_btsp_sequence_learning_one_shot_word_pair_v2.md
Predecessor: exp_btsp_sequence_learning_one_shot_word_pair_v1.py (smoke saturation: all arms hit 1.000 at fresh-W per-pair)
USER directive 2026-06-27: "tall stand vs stand tall" -- BTSP for language word-order

v1 -> v2 CHANGES (smoke discriminator must fire per META_RULE_K + Discipline #2):
  v1 used fresh W per pair -> trivial recall (additive ALSO at 1.000 -> regime too easy -> saturation HARD_FAIL).
  v2 uses SHARED W across all N_PAIRS pairs -> crosstalk loads the substrate -> additive interferes,
     BTSP-selective preserves order info via sparse tagging. THIS is the actual capacity test where
     selective consolidation should win over naive accumulation.
  v2 recalls against ALL stored contexts (2*N_PAIRS candidates) not just the paired C_X/C_Y -> harder, fairer.
  v2 fixes paired_reward: drop the broken median-threshold gate; instead, use a "context strength"
     gate (top-fq tag PLUS only fire if max-eligibility > 2*mean-eligibility -- biologically
     a neuromodulator pulse triggered by context-arrival success).

TASK -- shared-W one-shot order-sensitive sequence binding:
  - Vocab V (1000 bipolar atoms, dim N_DIM=16384 at full).
  - Generate N_PAIRS distinct atom-pairs (a_i, b_i).
  - Each pair has TWO orderings: S_AB_i = roll(a_i,1) + roll(b_i,2), S_BA_i = roll(b_i,1) + roll(a_i,2).
  - Each ordering has a unique context tag: C_AB_i, C_BA_i (random HD vectors).
  - Total 2*N_PAIRS sequence-context bindings.
  - Each ARM stores ALL 2*N_PAIRS bindings into ONE shared W via single-shot per binding.
  - Recall: query with any S, retrieve W @ S; cosine to ALL 2*N_PAIRS candidate contexts; pick argmax.
  - Correct: argmax == paired_context. Wrong: argmax == cross-order context (swapped order tag).

  Metric: order_discrimination = correct - cross_order_confusion (where 'cross order' is the SWAPPED
  context for the SAME atom-pair; the most diagnostic failure mode for order-insensitivity).

ARMS (4 + 1 diag):
  1. ARM_ADDITIVE_HEBBIAN   W = sum_i outer(C_i, S_i) -- naive accumulation; crosstalk dominates at capacity
  2. ARM_RANDOM_TAG_50PCT   only random 50% synapses updated per binding -- "any sparsity" control
  3. ARM_BTSP_SPARSE_TAG_5PCT  fp=0.005, fq=0.0025, top-k WTA input + top-fq tag + binary flip
  4. ARM_BTSP_SPARSE_TAG_PAIRED_REWARD  + context-arrival gate (only tag if max_elig > 2*mean_elig)
  5. ARM_DIAG_ATOM_ORTHOGONALITY  vary atom-similarity in {0,0.5,1.0} on BTSP_5PCT; calibration

DISCRIMINATORS (PRE-REG bands):
  HARD_PASS:
    ARM_BTSP_SPARSE_TAG_5PCT order_discrimination >= 0.30 (lower than v1 because shared-W harder)
    AND BTSP > ADDITIVE_HEBBIAN by >= +0.15
    AND BTSP > RANDOM_TAG_50PCT by >= +0.10  (sparse selectivity > random)
    AND cv across seeds < 0.10
    AND no arm at >= 0.995 saturation (META_RULE_Q)
    AND GPU_UTIL_P50 >= 30% in smoke (Fix #24)
  MIDDLE_BAND:
    BTSP order_disc in [0.10, 0.30] OR positive lift smaller than HP
  HARD_FAIL:
    BTSP <= ADDITIVE OR order_disc < 0.05 OR all-arm saturation OR GPU<30%

REGIME:
  Full:  N_DIM=16384, V=1000, N_PAIRS=200, seeds=[11,17,23,29,37]   (400 bindings into one W)
  Smoke: N_DIM=2048,  V=200,  N_PAIRS=50,  seeds=[1]                (100 bindings into one W)
  Self:  N_DIM=512,   V=50,   N_PAIRS=20,  seeds=[1]                (40 bindings; minimal)

GPU MANDATE (Fix #24): assert cuda; torch.cuda ops; nvidia-smi sampler; gpu_util_p50>=30% in smoke.
HARDENING: L1-L4 + CARDINALITY_OK + import-crash sentinel.
FAIRNESS (META_RULE_AA): same encoding + same readout + saturation guard + random-tag control.

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

ANCHOR_NAME = "btsp_sequence_learning_one_shot_word_pair_v2"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED
HP_ORDER_DISC = 0.30
HP_LIFT_OVER_ADDITIVE = 0.15
HP_LIFT_OVER_RANDOM_TAG = 0.10
HP_CV_MAX = 0.10
HF_ORDER_DISC = 0.05
HF_GPU_UTIL = 30.0
SATURATION_GUARD = 0.995

FP_INPUT_SPARSITY = 0.005
FQ_TAG_GATING = 0.0025
TAG_RANDOM_50PCT = 0.50
PAIRED_REWARD_GATE_RATIO = 2.0   # context-arrival pulse: fire if max_elig > 2*mean_elig

if SELF_TEST_MODE:
    N_DIM = 512
    V = 50
    N_PAIRS = 20
    SEEDS = [1]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V = 200
    N_PAIRS = 50
    SEEDS = [1]
else:
    N_DIM = 16384
    V = 1000
    N_PAIRS = 200
    SEEDS = [11, 17, 23, 29, 37]

EXPECTED_ARMS = [
    "additive_hebbian",
    "random_tag_50pct",
    "btsp_sparse_tag_5pct",
    "btsp_sparse_tag_paired_reward",
    "diag_atom_orthogonality",
]

# 4 arms x 2*N_PAIRS queries + 3 diag levels x 2*N_PAIRS queries
EXPECTED_N_UNITS = len(SEEDS) * (4 * 2 * N_PAIRS + 3 * 2 * N_PAIRS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,N_PAIRS=%d,seeds=%s,mode=%s,"
    "fp=%.4f,fq=%.4f,random_tag=%.2f,paired_gate=%.1f,"
    "HP_disc>=%.2f,HP_lift_add>=%.2f,HP_lift_rand>=%.2f,HF_disc<%.2f,HF_gpu<%.0f%%,"
    "sat_guard=%.3f,SHARED_W=True,RECALL_VS_ALL=True,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+GPU_UTIL_SAMPLER"
) % (
    ANCHOR_NAME, N_DIM, V, N_PAIRS, SEEDS, RUN_MODE,
    FP_INPUT_SPARSITY, FQ_TAG_GATING, TAG_RANDOM_50PCT, PAIRED_REWARD_GATE_RATIO,
    HP_ORDER_DISC, HP_LIFT_OVER_ADDITIVE, HP_LIFT_OVER_RANDOM_TAG,
    HF_ORDER_DISC, HF_GPU_UTIL, SATURATION_GUARD,
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
            "_hardening_marker": "v2_btsp_sequence_one_shot_word_pair_gpu_shared_W",
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
            "_hardening_marker": "v2_btsp_sequence_one_shot_word_pair_gpu_import_crash",
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
        self._thread: threading.Thread = None

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


# --------------------- primitives (torch.cuda) ---------------------

def _import_torch_or_die():
    try:
        import torch
        return torch
    except Exception as e:
        print("[FATAL] torch import failed: %s" % e, file=sys.stderr, flush=True)
        raise


def make_bipolar_atoms(M: int, n: int, gen, torch_mod):
    X = (torch_mod.randint(0, 2, (M, n), generator=gen, device="cuda",
                           dtype=torch_mod.float32) * 2 - 1)
    return X / (X.norm(dim=1, keepdim=True) + 1e-8)


def bind_pos(atom, pos: int, torch_mod):
    return torch_mod.roll(atom, shifts=pos, dims=0)


def topk_sparsify_vec(v, fp: float, torch_mod):
    n = v.shape[0]
    k = max(1, int(math.ceil(fp * n)))
    if k >= n:
        return torch_mod.sign(v).to(torch_mod.float32)
    absv = v.abs()
    _, idx = absv.topk(k)
    out = torch_mod.zeros_like(v)
    out[idx] = torch_mod.sign(v[idx]).to(torch_mod.float32)
    return out


# --------------------- storage rules ---------------------

def store_additive(W, C, S, torch_mod):
    """W += outer(C, S) / N (per-binding, NO sparsity)."""
    return W + torch_mod.outer(C, S) / float(S.shape[0])


def store_random_tag_50pct(W, C, S, gen, torch_mod):
    """Random 50% mask of synapses, only masked positions updated."""
    update = torch_mod.outer(C, S) / float(S.shape[0])
    mask = (torch_mod.rand(W.shape, generator=gen, device="cuda") < TAG_RANDOM_50PCT)
    return torch_mod.where(mask, W + update, W)


def store_btsp(W, C, S, torch_mod, fp: float, fq: float, paired: bool):
    """BTSP Wu-Maass: sparse k-WTA input + top-fq tag + binary flip.

    paired=True adds context-arrival gate: only update if max_elig > GATE_RATIO * mean_elig.
    """
    S_sparse = topk_sparsify_vec(S, fp, torch_mod)
    outer_signed = torch_mod.outer(C, S_sparse)
    elig = outer_signed.abs()

    if paired:
        flat_elig = elig.flatten()
        nz = flat_elig[flat_elig > 0]
        if nz.numel() == 0:
            return W
        max_e = float(flat_elig.max())
        mean_e = float(nz.mean())
        if max_e < PAIRED_REWARD_GATE_RATIO * mean_e:
            return W

    n_total = W.numel()
    n_tag = max(1, int(math.ceil(fq * n_total)))
    flat_elig = elig.flatten()
    if n_tag < n_total:
        _, tag_idx = flat_elig.topk(n_tag)
    else:
        tag_idx = torch_mod.arange(n_total, device="cuda")

    tag_mask_flat = torch_mod.zeros(n_total, device="cuda", dtype=torch_mod.bool)
    tag_mask_flat[tag_idx] = True
    tag_mask = tag_mask_flat.view(W.shape)

    flip_direction = torch_mod.sign(outer_signed).to(torch_mod.float32)
    update = torch_mod.where(flip_direction == 0, W, flip_direction)
    return torch_mod.where(tag_mask, update, W)


# --------------------- per-seed task ---------------------

def run_arm(arm_type: str, arm_kwargs: dict,
             vocab, pair_idx_a, pair_idx_b, context_AB, context_BA,
             gen, torch_mod) -> Dict[str, float]:
    """Store all 2*N_PAIRS bindings into ONE shared W, then evaluate recall."""
    n_pairs = pair_idx_a.shape[0]

    # Build all S vectors and corresponding C vectors
    seqs: List = []
    ctxs: List = []
    paired_idx: List[int] = []   # idx into context_all of the paired context for each query
    cross_idx: List[int] = []    # idx of the cross-order context (the most-confusable wrong)

    # Layout: context_all has 2*n_pairs entries; first n_pairs are AB tags, next n_pairs are BA tags
    context_all_list = [context_AB[i] for i in range(n_pairs)] + \
                       [context_BA[i] for i in range(n_pairs)]
    context_all = torch_mod.stack(context_all_list, dim=0)

    for i in range(n_pairs):
        a = vocab[int(pair_idx_a[i])]
        b = vocab[int(pair_idx_b[i])]
        S_AB = bind_pos(a, 1, torch_mod) + bind_pos(b, 2, torch_mod)
        S_BA = bind_pos(b, 1, torch_mod) + bind_pos(a, 2, torch_mod)
        S_AB = S_AB / (S_AB.norm() + 1e-8)
        S_BA = S_BA / (S_BA.norm() + 1e-8)
        seqs.append(("AB", i, S_AB))
        seqs.append(("BA", i, S_BA))

    # Initialize shared W
    n_dim = vocab.shape[1]
    if arm_type == "btsp":
        # Initialize W as random bipolar (Wu-Maass spec: binary synapses start at random sign)
        W = (torch_mod.randint(0, 2, (n_dim, n_dim), generator=gen, device="cuda",
                                dtype=torch_mod.float32) * 2 - 1)
    else:
        W = torch_mod.zeros((n_dim, n_dim), device="cuda", dtype=torch_mod.float32)

    # Single-shot store ALL bindings
    for tag, i, S in seqs:
        if tag == "AB":
            C = context_AB[i]
        else:
            C = context_BA[i]
        if arm_type == "additive":
            W = store_additive(W, C, S, torch_mod)
        elif arm_type == "random_tag":
            W = store_random_tag_50pct(W, C, S, gen, torch_mod)
        elif arm_type == "btsp":
            W = store_btsp(W, C, S, torch_mod,
                            fp=arm_kwargs["fp"], fq=arm_kwargs["fq"],
                            paired=arm_kwargs["paired"])

    # Recall: query with each S; cosine of W@S to ALL 2*n_pairs context vectors;
    # correct iff argmax == paired context index
    n_correct = 0
    n_cross_order_confusion = 0   # picked the SWAPPED-order context for the SAME pair
    n_total = 0
    for q_idx, (tag, i, S) in enumerate(seqs):
        if tag == "AB":
            paired_ix = i               # AB tag is at index i in context_all
            cross_ix = n_pairs + i      # the BA tag for the same pair
        else:
            paired_ix = n_pairs + i
            cross_ix = i

        pred = W @ S   # shape (n_dim,)
        # Normalize for cosine
        pred_n = pred / (pred.norm() + 1e-8)
        ctx_n = context_all / (context_all.norm(dim=1, keepdim=True) + 1e-8)
        sims = ctx_n @ pred_n   # shape (2*n_pairs,)
        picked = int(sims.argmax())
        n_total += 1
        if picked == paired_ix:
            n_correct += 1
        elif picked == cross_ix:
            n_cross_order_confusion += 1

    recall_correct = n_correct / float(n_total)
    cross_order_confusion = n_cross_order_confusion / float(n_total)
    # order_discrimination: how much better than the swapped-order confusable
    # (a perfectly order-blind retrieval would have correct == cross_order;
    # order-sensitive retrieval has correct >> cross_order)
    order_disc = recall_correct - cross_order_confusion
    return {
        "recall_correct": recall_correct,
        "cross_order_confusion": cross_order_confusion,
        "order_discrimination": order_disc,
        "n_queries": n_total,
        "n_total_stored": 2 * n_pairs,
    }


def run_one_seed(seed: int, torch_mod) -> Dict[str, Any]:
    g = torch_mod.Generator(device="cuda").manual_seed(int(seed))
    vocab = make_bipolar_atoms(V, N_DIM, g, torch_mod)

    pair_idx_a = torch_mod.randint(0, V, (N_PAIRS,), generator=g, device="cuda")
    pair_idx_b = torch_mod.randint(0, V, (N_PAIRS,), generator=g, device="cuda")
    coll = (pair_idx_a == pair_idx_b)
    while bool(coll.any()):
        pair_idx_b[coll] = torch_mod.randint(0, V, (int(coll.sum()),),
                                             generator=g, device="cuda")
        coll = (pair_idx_a == pair_idx_b)

    context_AB = make_bipolar_atoms(N_PAIRS, N_DIM, g, torch_mod)
    context_BA = make_bipolar_atoms(N_PAIRS, N_DIM, g, torch_mod)

    arm_specs = [
        ("additive_hebbian", "additive", {}),
        ("random_tag_50pct", "random_tag", {}),
        ("btsp_sparse_tag_5pct", "btsp", {"fp": FP_INPUT_SPARSITY,
                                            "fq": FQ_TAG_GATING, "paired": False}),
        ("btsp_sparse_tag_paired_reward", "btsp", {"fp": FP_INPUT_SPARSITY,
                                                    "fq": FQ_TAG_GATING, "paired": True}),
    ]

    arm_results: Dict[str, Dict[str, float]] = {}
    for arm_name, arm_type, arm_kwargs in arm_specs:
        # Use a derived generator per arm for storage stochasticity, but SAME data
        g_arm = torch_mod.Generator(device="cuda").manual_seed(int(seed) * 1000 + hash(arm_name) % 1000)
        arm_results[arm_name] = run_arm(arm_type, arm_kwargs,
                                          vocab, pair_idx_a, pair_idx_b,
                                          context_AB, context_BA, g_arm, torch_mod)

    # Diagnostic: vary atom orthogonality with BTSP_5PCT
    diag_results: Dict[str, Dict[str, float]] = {}
    for sim_level, sim_target in [("ortho", 0.0), ("partial", 0.5), ("identical", 1.0)]:
        g_diag = torch_mod.Generator(device="cuda").manual_seed(int(seed) * 7919)
        # Build a custom vocab where pair-atoms have controlled similarity
        diag_vocab_a = make_bipolar_atoms(N_PAIRS, N_DIM, g_diag, torch_mod)
        if sim_target == 0.0:
            diag_vocab_b = make_bipolar_atoms(N_PAIRS, N_DIM, g_diag, torch_mod)
        elif sim_target == 1.0:
            diag_vocab_b = diag_vocab_a.clone()
        else:
            # Partial: flip 25% of bits to get ~50% overlap (sim ~0.5)
            flip_mask = (torch_mod.rand(diag_vocab_a.shape, generator=g_diag,
                                          device="cuda") < 0.25)
            diag_vocab_b = torch_mod.where(flip_mask, -diag_vocab_a, diag_vocab_a)
            diag_vocab_b = diag_vocab_b / (diag_vocab_b.norm(dim=1, keepdim=True) + 1e-8)

        # Use index-pair (i,i) where vocab_a[i] is paired with vocab_b[i]
        diag_context_AB = make_bipolar_atoms(N_PAIRS, N_DIM, g_diag, torch_mod)
        diag_context_BA = make_bipolar_atoms(N_PAIRS, N_DIM, g_diag, torch_mod)
        # Build a synthetic vocab for run_arm by concatenating a and b
        synth_vocab = torch_mod.cat([diag_vocab_a, diag_vocab_b], dim=0)
        synth_idx_a = torch_mod.arange(0, N_PAIRS, device="cuda")
        synth_idx_b = torch_mod.arange(N_PAIRS, 2 * N_PAIRS, device="cuda")
        diag_arm = run_arm("btsp", {"fp": FP_INPUT_SPARSITY, "fq": FQ_TAG_GATING,
                                      "paired": False},
                            synth_vocab, synth_idx_a, synth_idx_b,
                            diag_context_AB, diag_context_BA, g_diag, torch_mod)
        diag_results[sim_level] = {
            **diag_arm,
            "atom_similarity_target": sim_target,
        }

    return {
        "seed": int(seed),
        "N_DIM": N_DIM,
        "V": V,
        "N_PAIRS": N_PAIRS,
        "n_total_bindings_into_one_W": 2 * N_PAIRS,
        "fp": FP_INPUT_SPARSITY,
        "fq": FQ_TAG_GATING,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "arm_results": arm_results,
        "diag_results": diag_results,
    }


# --------------------- verdict ---------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           gpu_summary: Dict[str, float]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    arm_agg: Dict[str, Dict[str, float]] = {}
    for arm in ["additive_hebbian", "random_tag_50pct",
                "btsp_sparse_tag_5pct", "btsp_sparse_tag_paired_reward"]:
        vals = [per_seed[s]["arm_results"][arm]["order_discrimination"]
                for s in seeds_sorted]
        rc_vals = [per_seed[s]["arm_results"][arm]["recall_correct"]
                   for s in seeds_sorted]
        cross_vals = [per_seed[s]["arm_results"][arm]["cross_order_confusion"]
                      for s in seeds_sorted]
        mean = float(np.mean(vals))
        std = float(np.std(vals)) if n_seeds > 1 else 0.0
        cv = std / abs(mean) if abs(mean) > 1e-6 else 0.0
        arm_agg[arm] = {
            "mean_order_disc": mean,
            "std_order_disc": std,
            "cv_order_disc": cv,
            "mean_recall_correct": float(np.mean(rc_vals)),
            "mean_cross_order_confusion": float(np.mean(cross_vals)),
        }

    btsp_mean = arm_agg["btsp_sparse_tag_5pct"]["mean_order_disc"]
    btsp_cv = arm_agg["btsp_sparse_tag_5pct"]["cv_order_disc"]
    btsp_rc = arm_agg["btsp_sparse_tag_5pct"]["mean_recall_correct"]
    additive_mean = arm_agg["additive_hebbian"]["mean_order_disc"]
    additive_rc = arm_agg["additive_hebbian"]["mean_recall_correct"]
    random_tag_mean = arm_agg["random_tag_50pct"]["mean_order_disc"]
    paired_mean = arm_agg["btsp_sparse_tag_paired_reward"]["mean_order_disc"]

    lift_over_additive = btsp_mean - additive_mean
    lift_over_random = btsp_mean - random_tag_mean

    saturated_arms = [a for a, v in arm_agg.items()
                       if v["mean_recall_correct"] >= SATURATION_GUARD]

    gpu_util_p50 = gpu_summary.get("gpu_util_p50", -1.0)
    gpu_util_ok = True
    gpu_util_msg = ""
    if RUN_MODE == "smoke" and gpu_util_p50 >= 0 and gpu_summary.get("n_samples", 0) >= 3:
        if gpu_util_p50 < HF_GPU_UTIL:
            gpu_util_ok = False
            gpu_util_msg = "GPU_UTIL_FAIL: p50=%.1f%% < %.0f%% (numpy-on-GPU anti-pattern) n_samples=%d" % (
                gpu_util_p50, HF_GPU_UTIL, gpu_summary.get("n_samples", 0))

    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not gpu_util_ok:
        verdict = "HARD_FAIL"
        verdict_reason = gpu_util_msg
    elif saturated_arms:
        verdict = "HARD_FAIL"
        verdict_reason = "SATURATION_GUARD: arms %s recall>=%.3f (META_RULE_Q regime too easy)" % (
            saturated_arms, SATURATION_GUARD)
    elif btsp_mean < HF_ORDER_DISC:
        verdict = "HARD_FAIL"
        verdict_reason = "ORDER_DISCRIMINATION_NULL: BTSP order_disc=%.3f < %.2f" % (
            btsp_mean, HF_ORDER_DISC)
    elif lift_over_additive < 0:
        verdict = "HARD_FAIL"
        verdict_reason = "BTSP_BELOW_ADDITIVE: BTSP=%.3f Additive=%.3f lift=%.3f" % (
            btsp_mean, additive_mean, lift_over_additive)
    elif (btsp_mean >= HP_ORDER_DISC
            and lift_over_additive >= HP_LIFT_OVER_ADDITIVE
            and lift_over_random >= HP_LIFT_OVER_RANDOM_TAG
            and (n_seeds == 1 or btsp_cv < HP_CV_MAX)):
        verdict = "HARD_PASS"
        verdict_reason = (
            "ORDER_SENSITIVE_BINDING: BTSP=%.3f Additive=%.3f Random=%.3f "
            "lift_add=%.3f lift_rand=%.3f cv=%.3f"
        ) % (btsp_mean, additive_mean, random_tag_mean,
             lift_over_additive, lift_over_random, btsp_cv)
    elif 0.10 <= btsp_mean < HP_ORDER_DISC or 0 < lift_over_additive < HP_LIFT_OVER_ADDITIVE:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_ORDER_SENSITIVITY: BTSP=%.3f Additive=%.3f lift=%.3f"
        ) % (btsp_mean, additive_mean, lift_over_additive)

    verdict_msg = (
        "%s | %s | BTSP_disc=%.3f rc=%.3f | Additive_disc=%.3f rc=%.3f | "
        "Random50_disc=%.3f Paired_disc=%.3f | "
        "lift_add=%.3f lift_rand=%.3f cv=%.3f | "
        "gpu_util_p50=%.1f%% (n=%d) | n_seeds=%d N=%d V=%d N_PAIRS=%d stored=%d"
    ) % (verdict, verdict_reason,
         btsp_mean, btsp_rc, additive_mean, additive_rc,
         random_tag_mean, paired_mean,
         lift_over_additive, lift_over_random, btsp_cv,
         gpu_util_p50, gpu_summary.get("n_samples", 0),
         n_seeds, N_DIM, V, N_PAIRS, 2 * N_PAIRS)

    completed_units = n_seeds * (4 * 2 * N_PAIRS + 3 * 2 * N_PAIRS)

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_reason": verdict_reason,
        "arm_aggregate": arm_agg,
        "lift_over_additive": lift_over_additive,
        "lift_over_random_tag": lift_over_random,
        "gpu_util_summary": gpu_summary,
        "n_seeds_complete": n_seeds,
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": completed_units,
        "cardinality_ok": (completed_units >= EXPECTED_N_UNITS),
        "saturated_arms": saturated_arms,
    }


# --------------------- main ---------------------

def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init", "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d V=%d N_PAIRS=%d seeds=%s fp=%.4f fq=%.4f SHARED_W=True" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V, N_PAIRS, SEEDS,
        FP_INPUT_SPARSITY, FQ_TAG_GATING), flush=True)

    torch_mod = _import_torch_or_die()
    if not torch_mod.cuda.is_available():
        msg = "CUDA_NOT_AVAILABLE: torch.cuda.is_available()=False on this host"
        print("[FATAL] %s" % msg, file=sys.stderr, flush=True)
        _write_minimal_metrics(out_dir, "HARD_FAIL", msg, extra={"_phase": "cuda_check"})
        return 1

    print("[GPU] %s" % torch_mod.cuda.get_device_name(0), flush=True)
    print("[GPU] memory_free=%.2f GB" % (torch_mod.cuda.mem_get_info()[0] / 1e9), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0], torch_mod)
            assert "arm_results" in r
            for arm in EXPECTED_ARMS[:4]:
                assert arm in r["arm_results"], "missing arm: %s" % arm
                ar = r["arm_results"][arm]
                assert -1.0 <= ar["order_discrimination"] <= 1.0
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: shared-W v2 all 4 arms produced valid order_disc")
            print("[selftest] OK arms: %s" % {a: round(r["arm_results"][a]["order_discrimination"], 3)
                                               for a in r["arm_results"]}, flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL", "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            traceback.print_exc()
            return 1

    gpu_sampler = GPUUtilSampler(interval_s=2.0)
    gpu_sampler.start()

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    try:
        for i, seed in enumerate(SEEDS):
            t0 = time.time()
            _write_minimal_metrics(out_dir, "RUNNING",
                                   "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(SEEDS)),
                                   extra={"_phase": "seed_running", "_current_seed": seed})
            result = run_one_seed(seed, torch_mod)
            per_seed_results[str(seed)] = result
            (out_dir / ("partial_seed_%d.json" % seed)).write_text(
                json.dumps(result, indent=2), encoding="utf-8")
            arms = result["arm_results"]
            print(("[seed=%d] complete in %.1fs | BTSP=%.3f Additive=%.3f Random=%.3f Paired=%.3f") % (
                seed, time.time() - t0,
                arms["btsp_sparse_tag_5pct"]["order_discrimination"],
                arms["additive_hebbian"]["order_discrimination"],
                arms["random_tag_50pct"]["order_discrimination"],
                arms["btsp_sparse_tag_paired_reward"]["order_discrimination"]), flush=True)
            torch_mod.cuda.empty_cache()
    finally:
        gpu_sampler.stop()

    gpu_summary = gpu_sampler.summary()
    print("[gpu_util] p50=%.1f%% max=%.1f%% mean=%.1f%% n_samples=%d" % (
        gpu_summary["gpu_util_p50"], gpu_summary["gpu_util_max"],
        gpu_summary["gpu_util_mean"], gpu_summary["n_samples"]), flush=True)

    final = aggregate_and_verdict(per_seed_results, gpu_summary)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_btsp_sequence_one_shot_word_pair_gpu_shared_W"
    final["per_seed"] = [per_seed_results[s] for s in sorted(per_seed_results.keys(), key=lambda x: int(x))]
    final["n_seeds"] = len(per_seed_results)
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
