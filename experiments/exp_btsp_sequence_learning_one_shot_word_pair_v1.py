"""btsp_sequence_learning_one_shot_word_pair_v1 -- BTSP on one-shot ORDER-SENSITIVE sequence binding (GPU).

Prereg: preregs/2026-06-27_btsp_sequence_learning_one_shot_word_pair_v1.md
Research drill: notes/research_drill_2x_btsp_binary_signal_collapse_revival_2026-06-27.md (Angle B)
USER directive 2026-06-27: "btsp sounds important in the context of language and, in particular,
   scoring word weight based on order. tall stand vs stand tall."

CONTEXT:
  BTSP HARD_FAILed earlier today at PROTOTYPE-CLASSIFICATION (wrong task class per drill Angle B).
  Wu-Maass 2025 + Bittner-Milstein 2017 designed BTSP for ONE-SHOT EPISODIC SEQUENCE binding
  (hippocampal place-cell sequences during behavior). This cell tests BTSP on the RIGHT task
  class: one-shot order-sensitive sequence binding ("tall stand" vs "stand tall").

TASK -- one-shot order-sensitive sequence binding:
  Per-trial:
    1. Pick 2 random atoms a, b from vocabulary V (size 1000 distinct HD words).
    2. Form sequence-vector S_AB = bind(POS_1, a) + bind(POS_2, b)  # "a b"
    3. Form sequence-vector S_BA = bind(POS_1, b) + bind(POS_2, a)  # "b a"
    4. Generate context-tag-vector C_X = random unique HD vector ("meaning" of "a b")
    5. Generate context-tag-vector C_Y = random unique HD vector ("meaning" of "b a")
    6. EACH ARM: ONE-SHOT bind S_AB -> C_X and S_BA -> C_Y via arm-specific storage rule.

  Recall (per pair):
    Query with S_AB -> recall = nearest stored {C_X, C_Y}; correct = C_X.
    Query with S_BA -> recall = nearest stored {C_X, C_Y}; correct = C_Y.

  Metric: order_discrimination = recall_correct - recall_wrong (in {-1, 0, +1} per query;
  averaged over all queries across all pairs).
  Higher = more order-sensitive.

ARMS (4 mandatory + 1 diagnostic):
  1. ARM_ADDITIVE_HEBBIAN   baseline: W += outer(C, S) -- naive sum; tests if linear additive
                              storage preserves order info.
  2. ARM_RANDOM_TAG_50PCT   control: random 50% mask of synapses; only masked positions
                              receive update. Tests if random selectivity differs from full
                              storage (control for "any sparsity helps").
  3. ARM_BTSP_SPARSE_TAG_5PCT  Wu-Maass spec: fp=0.005 input sparsity, fq=0.0025 gating;
                              eligibility-trace gated; neuromodulator-triggered ONE-SHOT
                              binary flip of tagged synapses. THE MECHANISM ARM.
  4. ARM_BTSP_SPARSE_TAG_PAIRED_REWARD  refinement: tag fires only on context-arrival
                              (neuromodulator pulse = success-marker pairing the sequence
                              with the context tag).
  5. ARM_DIAG_ATOM_ORTHOGONALITY  diagnostic: vary atom-similarity in {0.0, 0.5, 1.0};
                              ortho atoms easy; identical hard. Calibrates discriminator
                              against task difficulty.

DISCRIMINATORS (PRE-REG):
  HARD_PASS:
    ARM_BTSP_SPARSE_TAG_5PCT order_discrimination >= 0.50
    AND BTSP > ADDITIVE_HEBBIAN by >= +0.20
    AND BTSP > RANDOM_TAG_50PCT by >= +0.10   (sparse selectivity > random selectivity)
    AND cv across seeds < 0.10
    AND no arm hits 1.000-saturation (META_RULE_Q)
  MIDDLE_BAND:
    BTSP order_discrimination in [0.20, 0.50] OR positive lift smaller than HP threshold
  HARD_FAIL:
    BTSP <= ADDITIVE_HEBBIAN
    OR order_discrimination < 0.10  (substrate can't bind order-sensitively even with BTSP)
    OR GPU_UTIL_P50 < 30% in smoke (numpy-on-GPU anti-pattern; Fix #24)
    OR fairness violation (different encoding / readout per arm)

REGIME:
  N_DIM=16384 (GPU-eligible scale; matmul-heavy)
  V=1000 (vocab)
  N_PAIRS=200 (test pairs)
  n_seeds=5
  Single-shot binding (M=1 update per pair; THAT is the BTSP point)

GPU MANDATE (Fix #24):
  - assert torch.cuda.is_available() else HARD_FAIL
  - all bind / outer / matmul on torch.cuda
  - sample gpu_util every 5s during smoke; gpu_util_p50 must be >= 30%
  - NOT numpy-then-transfer

HARDENING (META_RULE_X + L1-L4):
  - STARTED metrics written immediately
  - Per-arm progress metrics
  - Outer try/except
  - Import-crash sentinel
  - CARDINALITY_OK pre-reg field (5 seeds * 5 arms * 200 pairs = 5000 datapoints + 5 GPU samples)

FAIRNESS (META_RULE_AA):
  - All arms use SAME sequence-vector encoding (same bind operation via torch.roll)
  - All arms READ same way (cosine to nearest stored context-vector via W @ S_query)
  - RANDOM_TAG_50PCT controls for "any sparsity wins"
  - 1.000-saturation guard

ASCII-only; no emojis; no em-dashes.
Author: exp_dev (Opus 4.7 agent spawn, 2026-06-27).
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

ANCHOR_NAME = "btsp_sequence_learning_one_shot_word_pair_v1"

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
HP_ORDER_DISC = 0.50
HP_LIFT_OVER_ADDITIVE = 0.20
HP_LIFT_OVER_RANDOM_TAG = 0.10
HP_CV_MAX = 0.10
HF_ORDER_DISC = 0.10
HF_GPU_UTIL = 30.0
SATURATION_GUARD = 0.995

# BTSP sparsity params (Wu-Maass 2025 spec)
FP_INPUT_SPARSITY = 0.005    # input k-WTA fraction
FQ_TAG_GATING = 0.0025       # gating sparsity (synapses tagged for ONE-SHOT flip)
TAG_RANDOM_50PCT = 0.50      # control arm: random 50% tag

# Regime
if SELF_TEST_MODE:
    N_DIM = 512
    V = 50
    N_PAIRS = 10
    SEEDS = [1]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V = 200
    N_PAIRS = 20
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

# CARDINALITY: per seed, 4 mandatory arms x N_PAIRS queries x 2 (S_AB + S_BA)
# plus diag arm with 3 similarity levels x N_PAIRS x 2
EXPECTED_N_UNITS = len(SEEDS) * (4 * N_PAIRS * 2 + 3 * N_PAIRS * 2)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,N_PAIRS=%d,seeds=%s,mode=%s,"
    "fp=%.4f,fq=%.4f,random_tag=%.2f,"
    "HP_disc>=%.2f,HP_lift_add>=%.2f,HP_lift_rand>=%.2f,HF_disc<%.2f,HF_gpu<%.0f%%,"
    "sat_guard=%.3f,hardening=L1early+L2perarm+L3outertry+L4importsentinel+GPU_UTIL_SAMPLER"
) % (
    ANCHOR_NAME, N_DIM, V, N_PAIRS, SEEDS, RUN_MODE,
    FP_INPUT_SPARSITY, FQ_TAG_GATING, TAG_RANDOM_50PCT,
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
            "_hardening_marker": "v1_btsp_sequence_one_shot_word_pair_gpu",
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
            "_hardening_marker": "v1_btsp_sequence_one_shot_word_pair_gpu_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# --------------------- GPU util sampler ---------------------

class GPUUtilSampler:
    """Background thread that samples nvidia-smi for gpu_util percentage."""

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
    """Make M bipolar atoms of dim n. L2-normalized."""
    X = (torch_mod.randint(0, 2, (M, n), generator=gen, device="cuda",
                           dtype=torch_mod.float32) * 2 - 1)
    return X / (X.norm(dim=1, keepdim=True) + 1e-8)


def bind_pos(atom, pos: int, torch_mod):
    """Position-binding via circular shift (HRR-style). atom shape (n,) -> shifted (n,)."""
    return torch_mod.roll(atom, shifts=pos, dims=0)


def cosine(a, b, torch_mod):
    """Cosine similarity between two 1-D vectors."""
    return float((a * b).sum() / ((a.norm() * b.norm()) + 1e-8))


def topk_sparsify(v, fp: float, torch_mod):
    """k-WTA: keep top fp*n |entries|; zero the rest. Returns sparse bipolar."""
    n = v.shape[0]
    k = max(1, int(math.ceil(fp * n)))
    if k >= n:
        return torch_mod.sign(v).to(torch_mod.float32)
    absv = v.abs()
    _, idx = absv.topk(k)
    out = torch_mod.zeros_like(v)
    out[idx] = torch_mod.sign(v[idx]).to(torch_mod.float32)
    return out


# --------------------- arms ---------------------

def storage_additive_hebbian(W, S_AB, C_X, S_BA, C_Y, gen, torch_mod):
    """Naive additive Hebbian: W += outer(C, S) summed over both pairs.
    W shape (n_dim, n_dim).
    """
    W = W + torch_mod.outer(C_X, S_AB) / float(S_AB.shape[0])
    W = W + torch_mod.outer(C_Y, S_BA) / float(S_BA.shape[0])
    return W


def storage_random_tag_50pct(W, S_AB, C_X, S_BA, C_Y, gen, torch_mod):
    """Control: random 50% of synapses tagged; only tagged positions updated."""
    update1 = torch_mod.outer(C_X, S_AB) / float(S_AB.shape[0])
    mask1 = (torch_mod.rand(W.shape, generator=gen, device="cuda") < TAG_RANDOM_50PCT)
    W = torch_mod.where(mask1, W + update1, W)
    update2 = torch_mod.outer(C_Y, S_BA) / float(S_BA.shape[0])
    mask2 = (torch_mod.rand(W.shape, generator=gen, device="cuda") < TAG_RANDOM_50PCT)
    W = torch_mod.where(mask2, W + update2, W)
    return W


def storage_btsp_sparse_tag(W, S_AB, C_X, S_BA, C_Y, gen, torch_mod,
                              fp: float, fq: float, paired: bool):
    """BTSP Wu-Maass: sparse input + sparse tagging + one-shot binary flip.

    Mechanism:
      1. Sparsify input sequence via top-fp k-WTA (only top fp*n positions active).
      2. Compute eligibility trace ~= |outer(C, S_sparse)| (instantaneous outer-product magnitude).
      3. Tag top fq fraction of synapses (highest eligibility).
      4. One-shot binary flip: tagged synapses take sign of outer(C, S_sparse).

    If paired=True: tag activation also gated by context-arrival success marker
    (here: only tag if max-eligibility > threshold, simulating neuromodulator pulse).
    """
    for (S, C) in [(S_AB, C_X), (S_BA, C_Y)]:
        S_sparse = topk_sparsify(S, fp, torch_mod)
        outer_signed = torch_mod.outer(C, S_sparse)
        elig = outer_signed.abs()

        n_total = W.numel()
        n_tag = max(1, int(math.ceil(fq * n_total)))

        flat_elig = elig.flatten()
        # Top-k tag selection: tag synapses with highest eligibility
        if n_tag < n_total:
            _, tag_idx = flat_elig.topk(n_tag)
        else:
            tag_idx = torch_mod.arange(n_total, device="cuda")

        if paired:
            # Paired-reward: only fire tag if max eligibility passes a "context-arrival" threshold.
            # Use the median of nonzero eligibility as a proxy for "successful pairing signal."
            nz = flat_elig[flat_elig > 0]
            if nz.numel() > 0:
                thresh = float(nz.median())
                max_elig = float(flat_elig.max())
                if max_elig < thresh * 1.5:
                    # Insufficient pairing signal; skip update
                    continue

        # Build flat tag mask
        tag_mask_flat = torch_mod.zeros(n_total, device="cuda", dtype=torch_mod.bool)
        tag_mask_flat[tag_idx] = True
        tag_mask = tag_mask_flat.view(W.shape)

        # One-shot binary flip at tagged synapses
        flip_direction = torch_mod.sign(outer_signed).to(torch_mod.float32)
        # If sign is 0, preserve current W; else write the sign
        update = torch_mod.where(flip_direction == 0, W, flip_direction)
        W = torch_mod.where(tag_mask, update, W)
    return W


# --------------------- per-seed task ---------------------

def run_one_seed(seed: int, torch_mod) -> Dict[str, Any]:
    """Run one seed: generate vocab + N_PAIRS pairs; for each pair test all arms."""
    g = torch_mod.Generator(device="cuda").manual_seed(int(seed))

    # Vocabulary (V bipolar atoms, dim N_DIM)
    vocab = make_bipolar_atoms(V, N_DIM, g, torch_mod)
    # Sample 2 * N_PAIRS atom-pairs (a, b)
    pair_idx_a = torch_mod.randint(0, V, (N_PAIRS,), generator=g, device="cuda")
    pair_idx_b = torch_mod.randint(0, V, (N_PAIRS,), generator=g, device="cuda")
    # Avoid a == b (re-roll where collision)
    coll = (pair_idx_a == pair_idx_b)
    while bool(coll.any()):
        pair_idx_b[coll] = torch_mod.randint(0, V, (int(coll.sum()),),
                                             generator=g, device="cuda")
        coll = (pair_idx_a == pair_idx_b)

    # Context-tag vectors C_X, C_Y per pair (random unique HD)
    context_X = make_bipolar_atoms(N_PAIRS, N_DIM, g, torch_mod)
    context_Y = make_bipolar_atoms(N_PAIRS, N_DIM, g, torch_mod)

    arm_results: Dict[str, Dict[str, float]] = {}

    # ARMS to run
    arm_specs = [
        ("additive_hebbian", "additive", {}),
        ("random_tag_50pct", "random_tag", {}),
        ("btsp_sparse_tag_5pct", "btsp", {"fp": FP_INPUT_SPARSITY,
                                            "fq": FQ_TAG_GATING, "paired": False}),
        ("btsp_sparse_tag_paired_reward", "btsp", {"fp": FP_INPUT_SPARSITY,
                                                    "fq": FQ_TAG_GATING, "paired": True}),
    ]

    for arm_name, arm_type, arm_kwargs in arm_specs:
        n_correct = 0
        n_wrong_picked = 0
        n_total = 0
        # Fresh W per pair (no cross-pair contamination; this is one-shot per pair)
        per_pair_disc = []
        for p in range(N_PAIRS):
            a = vocab[int(pair_idx_a[p])]
            b = vocab[int(pair_idx_b[p])]
            # Sequence vectors via position-binding (HRR-style: roll by position)
            S_AB = bind_pos(a, 1, torch_mod) + bind_pos(b, 2, torch_mod)
            S_BA = bind_pos(b, 1, torch_mod) + bind_pos(a, 2, torch_mod)
            S_AB = S_AB / (S_AB.norm() + 1e-8)
            S_BA = S_BA / (S_BA.norm() + 1e-8)

            C_X = context_X[p]
            C_Y = context_Y[p]

            # Fresh W per pair (clean ONE-SHOT test)
            W = torch_mod.zeros((N_DIM, N_DIM), device="cuda",
                                dtype=torch_mod.float32)

            if arm_type == "additive":
                W = storage_additive_hebbian(W, S_AB, C_X, S_BA, C_Y, g, torch_mod)
            elif arm_type == "random_tag":
                W = storage_random_tag_50pct(W, S_AB, C_X, S_BA, C_Y, g, torch_mod)
            elif arm_type == "btsp":
                W = storage_btsp_sparse_tag(W, S_AB, C_X, S_BA, C_Y, g, torch_mod,
                                              fp=arm_kwargs["fp"],
                                              fq=arm_kwargs["fq"],
                                              paired=arm_kwargs["paired"])

            # Recall: query with S_AB, retrieved = W @ S_AB; cosine to C_X, C_Y
            pred_from_AB = W @ S_AB
            pred_from_BA = W @ S_BA

            sim_AB_to_CX = cosine(pred_from_AB, C_X, torch_mod)
            sim_AB_to_CY = cosine(pred_from_AB, C_Y, torch_mod)
            sim_BA_to_CX = cosine(pred_from_BA, C_X, torch_mod)
            sim_BA_to_CY = cosine(pred_from_BA, C_Y, torch_mod)

            # Query AB should pick C_X (not C_Y)
            ab_correct = (sim_AB_to_CX > sim_AB_to_CY)
            # Query BA should pick C_Y (not C_X)
            ba_correct = (sim_BA_to_CY > sim_BA_to_CX)

            n_total += 2
            if ab_correct:
                n_correct += 1
            else:
                n_wrong_picked += 1
            if ba_correct:
                n_correct += 1
            else:
                n_wrong_picked += 1

            # Per-pair order_discrimination = (correct - wrong) / 2 over the 2 queries
            per_pair_disc.append(
                ((1.0 if ab_correct else -1.0) + (1.0 if ba_correct else -1.0)) / 2.0
            )

            del W

        recall_correct = n_correct / float(n_total)
        recall_wrong = n_wrong_picked / float(n_total)
        order_disc = recall_correct - recall_wrong   # in [-1, +1]
        arm_results[arm_name] = {
            "recall_correct": recall_correct,
            "recall_wrong": recall_wrong,
            "order_discrimination": order_disc,
            "n_queries": n_total,
            "per_pair_disc_mean": float(sum(per_pair_disc) / len(per_pair_disc)),
        }

    # Diagnostic arm: vary atom orthogonality
    diag_results: Dict[str, float] = {}
    for sim_level, sim_target in [("ortho", 0.0), ("partial", 0.5), ("identical", 1.0)]:
        # Use BTSP_5PCT mechanism on atoms with controlled similarity
        n_correct = 0
        n_wrong_picked = 0
        n_total = 0
        for p in range(N_PAIRS):
            base = make_bipolar_atoms(1, N_DIM, g, torch_mod)[0]
            # Generate b at target similarity to a
            if sim_target == 0.0:
                # ortho-ish: independent bipolar
                b_atom = make_bipolar_atoms(1, N_DIM, g, torch_mod)[0]
            elif sim_target == 1.0:
                b_atom = base.clone()
            else:
                # Partial: flip (1-sim)/2 fraction of bits
                flip = torch_mod.rand(N_DIM, generator=g, device="cuda") < 0.25
                b_atom = base.clone()
                b_atom = torch_mod.where(flip, -b_atom, b_atom)
                b_atom = b_atom / (b_atom.norm() + 1e-8)
            a_atom = base / (base.norm() + 1e-8)

            S_AB = bind_pos(a_atom, 1, torch_mod) + bind_pos(b_atom, 2, torch_mod)
            S_BA = bind_pos(b_atom, 1, torch_mod) + bind_pos(a_atom, 2, torch_mod)
            S_AB = S_AB / (S_AB.norm() + 1e-8)
            S_BA = S_BA / (S_BA.norm() + 1e-8)

            C_X = context_X[p]
            C_Y = context_Y[p]

            W = torch_mod.zeros((N_DIM, N_DIM), device="cuda",
                                dtype=torch_mod.float32)
            W = storage_btsp_sparse_tag(W, S_AB, C_X, S_BA, C_Y, g, torch_mod,
                                          fp=FP_INPUT_SPARSITY,
                                          fq=FQ_TAG_GATING, paired=False)
            pred_from_AB = W @ S_AB
            pred_from_BA = W @ S_BA
            ab_correct = (cosine(pred_from_AB, C_X, torch_mod) >
                          cosine(pred_from_AB, C_Y, torch_mod))
            ba_correct = (cosine(pred_from_BA, C_Y, torch_mod) >
                          cosine(pred_from_BA, C_X, torch_mod))
            n_total += 2
            if ab_correct: n_correct += 1
            else: n_wrong_picked += 1
            if ba_correct: n_correct += 1
            else: n_wrong_picked += 1
            del W
        rc = n_correct / float(n_total)
        rw = n_wrong_picked / float(n_total)
        diag_results[sim_level] = {
            "recall_correct": rc,
            "recall_wrong": rw,
            "order_discrimination": rc - rw,
            "atom_similarity_target": sim_target,
            "n_queries": n_total,
        }

    return {
        "seed": int(seed),
        "N_DIM": N_DIM,
        "V": V,
        "N_PAIRS": N_PAIRS,
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
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials",
            "summary": "no per-seed partials",
        }

    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    n_seeds = len(seeds_sorted)

    # Aggregate per-arm order_discrimination across seeds
    arm_agg: Dict[str, Dict[str, float]] = {}
    for arm in ["additive_hebbian", "random_tag_50pct",
                "btsp_sparse_tag_5pct", "btsp_sparse_tag_paired_reward"]:
        vals = [per_seed[s]["arm_results"][arm]["order_discrimination"]
                for s in seeds_sorted]
        mean = float(np.mean(vals))
        std = float(np.std(vals)) if n_seeds > 1 else 0.0
        cv = std / abs(mean) if abs(mean) > 1e-6 else 0.0
        arm_agg[arm] = {
            "mean_order_disc": mean,
            "std_order_disc": std,
            "cv_order_disc": cv,
        }

    btsp_mean = arm_agg["btsp_sparse_tag_5pct"]["mean_order_disc"]
    btsp_cv = arm_agg["btsp_sparse_tag_5pct"]["cv_order_disc"]
    additive_mean = arm_agg["additive_hebbian"]["mean_order_disc"]
    random_tag_mean = arm_agg["random_tag_50pct"]["mean_order_disc"]
    paired_mean = arm_agg["btsp_sparse_tag_paired_reward"]["mean_order_disc"]

    lift_over_additive = btsp_mean - additive_mean
    lift_over_random = btsp_mean - random_tag_mean

    # Saturation guard
    saturated_arms = [a for a, v in arm_agg.items()
                       if v["mean_order_disc"] >= SATURATION_GUARD]

    # GPU util check (smoke only; full does not gate on gpu_util)
    gpu_util_p50 = gpu_summary.get("gpu_util_p50", -1.0)
    gpu_util_ok = True
    gpu_util_msg = ""
    if RUN_MODE == "smoke" and gpu_util_p50 >= 0:
        if gpu_util_p50 < HF_GPU_UTIL:
            gpu_util_ok = False
            gpu_util_msg = "GPU_UTIL_FAIL: p50=%.1f%% < %.0f%% (numpy-on-GPU anti-pattern)" % (
                gpu_util_p50, HF_GPU_UTIL)

    # Verdict logic
    verdict = "MIDDLE_BAND"
    verdict_reason = ""

    if not gpu_util_ok:
        verdict = "HARD_FAIL"
        verdict_reason = gpu_util_msg
    elif saturated_arms:
        verdict = "HARD_FAIL"
        verdict_reason = "SATURATION_GUARD: arms %s at >=%.3f (META_RULE_Q regime too easy)" % (
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
    elif 0.20 <= btsp_mean < HP_ORDER_DISC or 0 < lift_over_additive < HP_LIFT_OVER_ADDITIVE:
        verdict = "MIDDLE_BAND"
        verdict_reason = (
            "PARTIAL_ORDER_SENSITIVITY: BTSP=%.3f Additive=%.3f lift=%.3f"
        ) % (btsp_mean, additive_mean, lift_over_additive)

    verdict_msg = (
        "%s | %s | BTSP=%.3f Additive=%.3f Random50=%.3f Paired=%.3f | "
        "lift_add=%.3f lift_rand=%.3f cv=%.3f | gpu_util_p50=%.1f%% n_seeds=%d N=%d V=%d N_PAIRS=%d"
    ) % (verdict, verdict_reason,
         btsp_mean, additive_mean, random_tag_mean, paired_mean,
         lift_over_additive, lift_over_random, btsp_cv,
         gpu_util_p50, n_seeds, N_DIM, V, N_PAIRS)

    completed_units = n_seeds * (4 * N_PAIRS * 2 + 3 * N_PAIRS * 2)
    cardinality_ok = (completed_units >= EXPECTED_N_UNITS)

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
        "cardinality_ok": cardinality_ok,
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

    print("[%s] mode=%s N=%d V=%d N_PAIRS=%d seeds=%s fp=%.4f fq=%.4f" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, V, N_PAIRS, SEEDS,
        FP_INPUT_SPARSITY, FQ_TAG_GATING), flush=True)

    torch_mod = _import_torch_or_die()
    if not torch_mod.cuda.is_available():
        msg = "CUDA_NOT_AVAILABLE: torch.cuda.is_available()=False on this host"
        print("[FATAL] %s" % msg, file=sys.stderr, flush=True)
        _write_minimal_metrics(out_dir, "HARD_FAIL", msg,
                               extra={"_phase": "cuda_check"})
        return 1

    print("[GPU] %s" % torch_mod.cuda.get_device_name(0), flush=True)
    print("[GPU] cuda available=%s memory_free=%s" % (
        torch_mod.cuda.is_available(),
        str(torch_mod.cuda.mem_get_info()[0] / 1e9) + "GB"), flush=True)

    if SELF_TEST_MODE:
        try:
            # Quick mechanism check: 1 seed, tiny N
            r = run_one_seed(SEEDS[0], torch_mod)
            assert "arm_results" in r
            for arm in ["additive_hebbian", "random_tag_50pct",
                        "btsp_sparse_tag_5pct", "btsp_sparse_tag_paired_reward"]:
                assert arm in r["arm_results"], "missing arm: %s" % arm
                ar = r["arm_results"][arm]
                assert "order_discrimination" in ar
                # Order disc must be in [-1, +1]
                assert -1.0 <= ar["order_discrimination"] <= 1.0, (
                    "arm %s order_disc out of range: %.3f" % (arm, ar["order_discrimination"]))
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: all 4 arms produced valid order_disc")
            print("[selftest] OK arms ran: %s" % {a: round(r["arm_results"][a]["order_discrimination"], 3)
                                                   for a in r["arm_results"]}, flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            traceback.print_exc()
            return 1

    # Start GPU sampler
    gpu_sampler = GPUUtilSampler(interval_s=2.0)
    gpu_sampler.start()

    per_seed_results: Dict[str, Dict[str, Any]] = {}
    try:
        for i, seed in enumerate(SEEDS):
            t0 = time.time()
            _write_minimal_metrics(out_dir, "RUNNING",
                                   "RUNNING: seed=%d (%d/%d)" % (
                                       seed, i + 1, len(SEEDS)),
                                   extra={"_phase": "seed_running",
                                          "_current_seed": seed})
            result = run_one_seed(seed, torch_mod)
            per_seed_results[str(seed)] = result
            # Write per-seed partial
            (out_dir / ("partial_seed_%d.json" % seed)).write_text(
                json.dumps(result, indent=2), encoding="utf-8")
            arms = result["arm_results"]
            print(("[seed=%d] complete in %.1fs | "
                   "BTSP=%.3f Additive=%.3f Random50=%.3f Paired=%.3f") % (
                seed, time.time() - t0,
                arms["btsp_sparse_tag_5pct"]["order_discrimination"],
                arms["additive_hebbian"]["order_discrimination"],
                arms["random_tag_50pct"]["order_discrimination"],
                arms["btsp_sparse_tag_paired_reward"]["order_discrimination"]),
                  flush=True)
            # Free GPU memory between seeds
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
    final["_hardening_marker"] = "v1_btsp_sequence_one_shot_word_pair_gpu"
    final["per_seed"] = [per_seed_results[s] for s in sorted(per_seed_results.keys(), key=lambda x: int(x))]
    final["n_seeds"] = len(per_seed_results)
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
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
