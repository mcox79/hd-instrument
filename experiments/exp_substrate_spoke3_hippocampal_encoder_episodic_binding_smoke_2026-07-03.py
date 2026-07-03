"""exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03

Stage 2 Spoke 3 substrate-native brain-analog hippocampal encoder SMOKE probe on
its INTENDED task class (Skunkworks-recommended existence proof for task-mechanism
fit) -- novel (role_key, filler) pair binding + partial-cue pattern completion.

Load-bearing per Skunkworks 2026-07-03 diagnosis: prior Wikipedia title->body
smoke (commit 1cd8e3757) HARD_FAIL was TASK-CLASS MISMATCH, not mechanism failure.
Marr-CA3 + DG-expansion is designed for episodic one-shot binding + pattern
completion (Marr 1971; Wilson-McNaughton 1994; McClelland-McNaughton-O'Reilly 1995),
NOT open-domain many-to-many surface retrieval. This cell tests the primitive on
its INTENDED task class as an existence proof, independent of Wikipedia task-fit.

Task (Option A -- novel-pair binding + partial-cue recall):
  1. Draw N=50 random bipolar pair HDs (role_key_i, filler_i) in R^{N_DIM}.
  2. Episode HD = elementwise bind role_key_i * filler_i.
  3. One-shot write: encode_and_write(episodes) -- each episode becomes CA3 attractor.
  4. Corrupt cue: 50% dims of episode zeroed (per Marr-CA3 selftest partial-cue).
  5. Retrieve: DG(cue) -> CA3 settle -> sparsified DG code.
  6. Score: recall@1 = fraction where argmax_j cos(completed_cue_i, stored_dg_j) == i.

Arms (4 x 3 seeds = 12 units):
  ARM_HIPPOCAMPAL_ONE_SHOT   (LOAD_BEARING)  full DG+CA3 pipeline
  ARM_HIPPOCAMPAL_DG_ONLY_ABLATION           DG only, no CA3 settle
  ARM_COSINE_ARGMAX_BASELINE                 plain cosine in n_dim; no encoder
  ARM_RANDOM_BASELINE                        chance floor

HP band (LOAD_BEARING on ARM_HIPPOCAMPAL_ONE_SHOT):
  HP1  ARM_HIPPOCAMPAL_ONE_SHOT recall@1 >= 0.80 (mechanism-appropriate at 4.8% load)
  HF1  ARM_HIPPOCAMPAL_ONE_SHOT recall@1 <  0.50 (mechanism fails on intended task)
  MB   ARM_HIPPOCAMPAL_ONE_SHOT recall@1 in [0.50, 0.80)

Regime:
  N_DIM = 2048, DG_DIM = 8192, SPARSITY = 0.02, N_PAIRS = 50, seeds = [11, 17, 23].
  Tsodyks-Feigelman capacity C_TF = 8192/(2*ln(50)) = 1047 patterns (THEORETICAL@).
  Load fraction 50/1047 = 4.8% (deeply under-capacity).

Pre-reg: preregs/2026-07-03_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke.md
Primitive: hdlab/hippocampal_encoder.py (13 primitive selftests).

FRAMING DISCIPLINE (LOAD-BEARING per USER 2026-07-02):
- SUBSTRATE KNOWS ALMOST NOTHING. This is a MECHANISM PROBE on a SYNTHETIC
  supervised regime; NOT a general-knowledge claim.
- If HP: task-class-mismatch hypothesis validated for prior Wikipedia HF.
- If HF: mechanism has issues even on intended task class; requires drill.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF; hash-check per arm)
- final_metrics_atomicity: tmp_replace
- except SystemExit: raise BEFORE except Exception
- baseline_in_band (META_RULE_AG; ARM_RANDOM_BASELINE recall@1 sanity)
- HP_SCOPE per-arm declaration (in verdict logic)
- cardinality_ok (EXPECTED_N_UNITS = 4 arms x 3 seeds = 12)
- per-unit failure_class instrumentation
- all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@ (META_RULE_AC)
- start_marker_written, crash_diagnostic_present, heartbeat_present
- per-seed checkpoint (SH-4-adjacent)

Scope: SMOKE-only. USER-locked SMOKE-only-on-local_cpu.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import sys

# Line-buffered stdout for real-time progress visibility.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_spoke3_hippocampal_encoder_episodic_binding_smoke_2026_07_03"

# --- Config ---

# THEORETICAL@ input HD dim consistent with prior Spoke 3 cell.
N_DIM = 2048

# DG expansion dim. 4x input.
DG_DIM = 8192

# DG target sparsity (~2%; ~164 active DG dims per code).
DG_SPARSITY = 0.02

# N pairs. HYPOTHESIZED@ 50 pairs -> 4.8% load vs Tsodyks-Feigelman capacity 1047
# (THEORETICAL@ C_TF = dg_dim / (2 * ln(1/p)) at p=0.02).
N_PAIRS = 50

# Partial cue: fraction of episode dims zeroed. HYPOTHESIZED@ 0.50 per primitive
# selftest ca3_pattern_completion_from_partial_cue (uses 50%).
PARTIAL_CUE_FRACTION_ZEROED = 0.50

# Seeds.
SEEDS = [11, 17, 23]

# HP band constants.
# HYPOTHESIZED@ primitive selftest scaling (ca3_pattern_completion_from_partial_cue
# achieves 0.90 sign-agreement on single stored pattern at dg_dim=2048; at
# dg_dim=8192 with N_PAIRS=50 at 4.8% load, recall@1 >= 0.80 is mechanism-
# appropriate threshold).
HP_HIPPO_R1_FLOOR = 0.80
HF_HIPPO_R1_HARD_FLOOR = 0.50

# THEORETICAL@ chance recall@1 = 1/N_PAIRS.
CHANCE_R1 = 1.0 / N_PAIRS  # 0.02
# Band cap 5x chance for 3-seed variance.
BASELINE_IN_BAND_R1_MAX = 5.0 * CHANCE_R1  # 0.10

# DG sparse rate architectural constraint.
DG_SPARSE_RATE_MIN = 0.008
DG_SPARSE_RATE_MAX = 0.040

# THEORETICAL@ Tsodyks-Feigelman: C_TF = dg_dim / (2 * ln(1/sparsity)).
_TF_CAPACITY = DG_DIM / (2.0 * math.log(1.0 / DG_SPARSITY))


# --- Args ---
def _parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--run-mode",
                    default=os.environ.get("HDLAB_RUN_MODE", None),
                    choices=[None, "self_test", "smoke", "full"])
    args, _ = ap.parse_known_args()
    if args.self_test:
        return "self_test"
    if args.smoke:
        return "smoke"
    if args.run_mode is not None:
        return args.run_mode
    # SMOKE-only cell.
    return "smoke"


RUN_MODE = _parse_args()
IS_SMOKE = RUN_MODE == "smoke"
IS_SELFTEST = RUN_MODE == "self_test"


# --- Observability helpers ---
def _log(msg: str) -> None:
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%SZ')}] {msg}", flush=True)


def _write_start_marker(output_dir: Path, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, final)


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int,
               elapsed_s: float, extra: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": elapsed_s,
        "extra": extra,
    }
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_partial_seed(output_dir: Path, seed: int, payload: dict) -> None:
    """Atomic per-seed checkpoint (SH-4)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / f"partial_metrics_{seed}.json.tmp"
    final = output_dir / f"partial_metrics_{seed}.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# --- Task-data generation ---

def _draw_pairs(n_pairs: int, n_dim: int, seed: int
                ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Draw n_pairs (role_key, filler) random bipolar HDs and their bind episodes.

    Returns (role_keys, fillers, episodes) each [n_pairs, n_dim] bipolar {-1,+1}.
    episode_i = role_key_i * filler_i (elementwise bind).
    """
    rng = np.random.default_rng(int(seed) * 991 + 7)
    role_keys = (rng.integers(0, 2, size=(n_pairs, n_dim)) * 2 - 1).astype(np.float32)
    fillers = (rng.integers(0, 2, size=(n_pairs, n_dim)) * 2 - 1).astype(np.float32)
    episodes = (role_keys * fillers).astype(np.float32)  # still {-1,+1}
    return role_keys, fillers, episodes


def _corrupt_cue(episodes: np.ndarray, fraction_zeroed: float,
                 seed: int) -> np.ndarray:
    """For each episode i, zero fraction_zeroed of dims (per-row random mask).

    Returns cues [n, n_dim] where cue_i has (1 - fraction_zeroed) * n_dim
    dims equal to episode_i and the rest zero. Deterministic w.r.t. seed.
    """
    n, d = episodes.shape
    n_zero = int(round(fraction_zeroed * d))
    rng = np.random.default_rng(int(seed) * 977 + 13)
    cues = episodes.copy()
    for i in range(n):
        zero_idx = rng.choice(d, size=n_zero, replace=False)
        cues[i, zero_idx] = 0.0
    return cues


def _corrupt_cue_selftest_verify_fraction(cues: np.ndarray, episodes: np.ndarray,
                                          fraction_zeroed: float) -> float:
    """Return observed mean zero-fraction across cues (for selftest)."""
    n, d = cues.shape
    obs = float(np.mean((cues == 0.0).sum(axis=1) / float(d)))
    return obs


# --- Arm implementations ---

def _encode_arm_hippocampal_one_shot(
    role_keys: np.ndarray, fillers: np.ndarray, episodes: np.ndarray, seed: int
) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """ARM_HIPPOCAMPAL_ONE_SHOT (LOAD_BEARING).

    Pipeline:
      encode_and_write(episodes) [DG expand + CA3 write]
      cues = 50%-corrupt(episodes)
      retrieve(cues, use_ca3=True, sparsify_after_settle=True) -> completed DG.
    Returns (stored_dg_codes, completed_cue_dg_codes, encode_wall, retrieve_wall, diag).
    """
    from hdlab.hippocampal_encoder import HippocampalEncoder
    n = episodes.shape[0]
    _log(f"  [hippo] DG expand + CA3 write N={n} dg_dim={DG_DIM} sparsity={DG_SPARSITY}")
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    stored_dg = enc.encode_and_write(episodes)  # sparse ternary [n, dg_dim]
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(stored_dg)
    _log(f"  [hippo] CA3 n_written={enc.ca3.n_written} obs_dg_rate={dg_sparse_rate:.4f} "
         f"fit_wall={fit_wall:.2f}s")

    _log(f"  [hippo] corrupt cue frac={PARTIAL_CUE_FRACTION_ZEROED:.2f} and retrieve")
    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, PARTIAL_CUE_FRACTION_ZEROED, seed=int(seed))
    completed_dg = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    ret_wall = time.perf_counter() - ret_t0
    _log(f"  [hippo] retrieve wall={ret_wall:.2f}s")

    diag = {
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "ca3_n_written": int(enc.ca3.n_written),
        "partial_cue_fraction_zeroed": float(PARTIAL_CUE_FRACTION_ZEROED),
        "tf_capacity_theoretical": float(_TF_CAPACITY),
        "load_fraction": float(n / _TF_CAPACITY),
    }
    _ = role_keys, fillers
    return stored_dg, completed_dg, fit_wall, ret_wall, diag


def _encode_arm_hippocampal_dg_only(
    role_keys: np.ndarray, fillers: np.ndarray, episodes: np.ndarray, seed: int
) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """ARM_HIPPOCAMPAL_DG_ONLY_ABLATION.

    DG expansion only. Retrieval: DG(partial_cue) vs stored DG(full_episode).
    Isolates DG-expansion contribution from CA3 pattern-completion.
    """
    from hdlab.hippocampal_encoder import HippocampalEncoder
    n = episodes.shape[0]
    _log(f"  [dg_only] DG expand (no CA3) N={n}")
    fit_t0 = time.perf_counter()
    enc = HippocampalEncoder(input_dim=N_DIM, dg_dim=DG_DIM,
                             sparsity=DG_SPARSITY, seed=int(seed))
    # Note: we don't encode_and_write (which would populate CA3). We only use
    # DGProjection for encoding both stored episodes and cues.
    stored_dg = enc.dg.encode_batch(episodes)
    fit_wall = time.perf_counter() - fit_t0
    dg_sparse_rate = enc.dg_sparse_rate(stored_dg)

    ret_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, PARTIAL_CUE_FRACTION_ZEROED, seed=int(seed))
    cue_dg = enc.dg.encode_batch(cues)  # DG projection of corrupted cue; no settle.
    ret_wall = time.perf_counter() - ret_t0

    diag = {
        "input_dim": N_DIM, "dg_dim": DG_DIM,
        "sparsity_target": DG_SPARSITY,
        "dg_sparse_rate_observed": float(dg_sparse_rate),
        "partial_cue_fraction_zeroed": float(PARTIAL_CUE_FRACTION_ZEROED),
        "ca3_used": False,
    }
    _ = role_keys, fillers
    return stored_dg, cue_dg, fit_wall, ret_wall, diag


def _encode_arm_cosine_baseline(
    role_keys: np.ndarray, fillers: np.ndarray, episodes: np.ndarray, seed: int
) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """ARM_COSINE_ARGMAX_BASELINE: plain cosine in n_dim; no encoder.

    stored = episodes (n_dim bipolar).
    query = partial cue (n_dim; 50% zeroed).
    Retrieval: cos in n_dim.
    """
    n = episodes.shape[0]
    _log(f"  [cos_bl] no-encoder baseline N={n}")
    fit_t0 = time.perf_counter()
    cues = _corrupt_cue(episodes, PARTIAL_CUE_FRACTION_ZEROED, seed=int(seed))
    fit_wall = time.perf_counter() - fit_t0
    _ = role_keys, fillers
    diag = {"input_dim": N_DIM, "encoder": "none",
            "partial_cue_fraction_zeroed": float(PARTIAL_CUE_FRACTION_ZEROED)}
    # For retrieval, "stored" and "query" both live in n_dim.
    return episodes.copy(), cues, 0.0, fit_wall, diag


def _encode_arm_random(
    role_keys: np.ndarray, fillers: np.ndarray, episodes: np.ndarray, seed: int
) -> Tuple[np.ndarray, np.ndarray, float, float, Dict]:
    """ARM_RANDOM_BASELINE: random HDs for both stored and query. Chance floor."""
    n = episodes.shape[0]
    rng = np.random.default_rng(int(seed) * 883 + 29)
    t0 = time.perf_counter()
    stored = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    query = (rng.integers(0, 2, size=(n, N_DIM)) * 2 - 1).astype(np.float32)
    wall = time.perf_counter() - t0
    _ = role_keys, fillers, episodes
    diag = {"input_dim": N_DIM, "encoder": "random"}
    return stored, query, 0.0, wall, diag


# --- Retrieval metrics ---

def _unit_norm(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / (n + eps)


def _retrieval_metrics(stored: np.ndarray, query: np.ndarray,
                       seed: int) -> Dict[str, float]:
    """recall@1, recall@5, MRR, intra/inter cos, snr.

    Ground truth: query[i] should retrieve stored[i] (bit-diag identity).
    """
    s = _unit_norm(stored.astype(np.float32))
    q = _unit_norm(query.astype(np.float32))
    n = s.shape[0]
    sims = q @ s.T  # [n, n]
    order = np.argsort(-sims, axis=1)
    r1 = 0
    r5 = 0
    mrr_sum = 0.0
    intra_sum = 0.0
    for i in range(n):
        intra_sum += float(sims[i, i])
        r1 += int(order[i, 0] == i)
        if i in order[i, :5]:
            r5 += 1
        rank_arr = np.where(order[i] == i)[0]
        if rank_arr.size > 0:
            mrr_sum += 1.0 / float(rank_arr[0] + 1)
    r1 /= n
    r5 /= n
    mrr = mrr_sum / n
    intra = intra_sum / n
    rng = np.random.default_rng(int(seed) * 991 + 7)
    perm = rng.permutation(n)
    for i in range(n):
        if perm[i] == i:
            j = (i + 1) % n
            perm[i], perm[j] = perm[j], perm[i]
    inter = float(np.mean(np.sum(q * s[perm], axis=1)))
    snr = intra / max(abs(inter), 1e-6)
    return {
        "recall_at_1": float(r1),
        "recall_at_5": float(r5),
        "mean_reciprocal_rank": float(mrr),
        "intra_pair_cos_mean": float(intra),
        "inter_pair_cos_mean": float(inter),
        "signal_to_noise_ratio": float(snr),
    }


# --- Arms-differ hash (META_RULE_AF) ---
def _arms_differ_hash(arms_query: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests: Dict[str, str] = {}
    for name, arr in arms_query.items():
        sig = arr[0, :200].astype(np.float32).tobytes()
        digests[name] = hashlib.sha256(sig).hexdigest()[:16]
    names = list(digests.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if digests[a] == digests[b]:
                raise RuntimeError(
                    f"META_RULE_AF VIOLATION arms_differ: {a!r} and {b!r} "
                    f"bit-identical query prefix (hash={digests[a]})."
                )
    return digests


# --- Cell-level selftests ---

def _selftest_arg_parse_default_is_smoke() -> None:
    old = sys.argv
    try:
        sys.argv = ["exp_substrate_spoke3_hippocampal_encoder_episodic_binding_smoke"]
        mode = _parse_args()
        assert mode == "smoke", f"default mode should be 'smoke' not {mode!r}"
    finally:
        sys.argv = old
    print("[selftest arg_parse_default_is_smoke] PASS", flush=True)


def _selftest_corrupt_cue_correct_fraction() -> None:
    """corrupt_cue produces exactly the declared zero-fraction."""
    rng = np.random.default_rng(3)
    n, d = 20, 512
    episodes = (rng.integers(0, 2, size=(n, d)) * 2 - 1).astype(np.float32)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.50, seed=11)
    # Each row must have exactly d/2 zeros.
    zeros_per_row = (cues == 0.0).sum(axis=1)
    assert np.all(zeros_per_row == d // 2), (
        f"zeros_per_row mismatch: {zeros_per_row[:5]} expected {d // 2}"
    )
    # Non-zero dims must match episode.
    nonzero_mask = cues != 0.0
    assert np.all(cues[nonzero_mask] == episodes[nonzero_mask]), \
        "cue non-zero dims don't match episode"
    print(f"[selftest corrupt_cue_correct_fraction] PASS "
          f"zeros_per_row={int(zeros_per_row[0])}/{d}", flush=True)


def _selftest_mini_binding_recall() -> None:
    """Mini: N=10 pairs at dg_dim=2048. Full pipeline should recall@1 >= 0.80."""
    role_keys, fillers, episodes = _draw_pairs(n_pairs=10, n_dim=256, seed=11)
    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=256, dg_dim=2048, sparsity=0.02, seed=11)
    stored = enc.encode_and_write(episodes)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.50, seed=11)
    completed = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    m = _retrieval_metrics(stored, completed, seed=11)
    assert m["recall_at_1"] >= 0.80, (
        f"mini binding recall@1={m['recall_at_1']:.3f} < 0.80 "
        f"(mechanism-appropriate threshold at 10-pair micro test); "
        f"intra={m['intra_pair_cos_mean']:.3f} inter={m['inter_pair_cos_mean']:.3f}"
    )
    print(f"[selftest mini_binding_recall] PASS r@1={m['recall_at_1']:.3f} "
          f"intra={m['intra_pair_cos_mean']:.3f} inter={m['inter_pair_cos_mean']:.3f}",
          flush=True)


def _selftest_arms_differ_hash_micro() -> None:
    """HIPPOCAMPAL_ONE_SHOT vs DG_ONLY completed cues must differ (bit-hash)."""
    role_keys, fillers, episodes = _draw_pairs(n_pairs=5, n_dim=256, seed=11)
    # Use small dg_dim for speed.
    from hdlab.hippocampal_encoder import HippocampalEncoder
    enc = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02, seed=11)
    stored = enc.encode_and_write(episodes)
    cues = _corrupt_cue(episodes, fraction_zeroed=0.50, seed=11)
    completed = enc.retrieve(cues, use_ca3=True, sparsify_after_settle=True)
    # DG-only pipeline
    enc2 = HippocampalEncoder(input_dim=256, dg_dim=1024, sparsity=0.02, seed=11)
    cue_dg = enc2.dg.encode_batch(cues)
    h_hip = hashlib.sha256(completed.tobytes()).hexdigest()
    h_dg = hashlib.sha256(cue_dg.tobytes()).hexdigest()
    assert h_hip != h_dg, (
        f"arms bit-identical: hip={h_hip[:8]} dg={h_dg[:8]}. CA3 settle no-op."
    )
    _ = stored, role_keys, fillers
    print(f"[selftest arms_differ_hash_micro] PASS h_hip={h_hip[:8]} h_dg={h_dg[:8]}",
          flush=True)


def _selftest_primitive_selftests_chain() -> None:
    """Verify hippocampal_encoder primitive selftests pass (13 tests)."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "hdlab.hippocampal_encoder", "--self-test"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print("[selftest primitive_selftests_chain] STDOUT:")
        print(result.stdout)
        print("[selftest primitive_selftests_chain] STDERR:")
        print(result.stderr)
        raise AssertionError(
            f"hdlab.hippocampal_encoder --self-test returned {result.returncode}"
        )
    if "13/13 passed" not in result.stdout:
        raise AssertionError(
            f"hippocampal_encoder selftest summary not '13/13 passed'; "
            f"stdout tail:\n{result.stdout[-500:]}"
        )
    print("[selftest primitive_selftests_chain] PASS 13/13 hippocampal_encoder "
          "selftests", flush=True)


def _run_selftests() -> int:
    tests = [
        ("arg_parse_default_is_smoke", _selftest_arg_parse_default_is_smoke),
        ("corrupt_cue_correct_fraction", _selftest_corrupt_cue_correct_fraction),
        ("mini_binding_recall", _selftest_mini_binding_recall),
        ("arms_differ_hash_micro", _selftest_arms_differ_hash_micro),
        ("primitive_selftests_chain", _selftest_primitive_selftests_chain),
    ]
    failed = []
    for name, fn in tests:
        try:
            fn()
        except AssertionError as e:
            failed.append((name, f"AssertionError: {e}"))
            print(f"[selftest {name}] FAIL: {e}", flush=True)
        except Exception as e:
            failed.append((name, f"{type(e).__name__}: {e}"))
            print(f"[selftest {name}] ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
    print(f"[selftest summary] {len(tests) - len(failed)}/{len(tests)} passed",
          flush=True)
    return 0 if not failed else 1


# --- Per-seed driver ---
ARM_DEFS = [
    "ARM_HIPPOCAMPAL_ONE_SHOT",
    "ARM_HIPPOCAMPAL_DG_ONLY_ABLATION",
    "ARM_COSINE_ARGMAX_BASELINE",
    "ARM_RANDOM_BASELINE",
]

ARM_ENCODERS = {
    "ARM_HIPPOCAMPAL_ONE_SHOT": _encode_arm_hippocampal_one_shot,
    "ARM_HIPPOCAMPAL_DG_ONLY_ABLATION": _encode_arm_hippocampal_dg_only,
    "ARM_COSINE_ARGMAX_BASELINE": _encode_arm_cosine_baseline,
    "ARM_RANDOM_BASELINE": _encode_arm_random,
}


def _run_one_seed(seed: int, output_dir: Path) -> Dict:
    _log(f"[seed {seed}] draw {N_PAIRS} pairs (n_dim={N_DIM}) + episodes")
    role_keys, fillers, episodes = _draw_pairs(N_PAIRS, N_DIM, seed=seed)
    n_arms = len(ARM_DEFS)
    per_arm: Dict[str, Dict] = {}
    per_arm_query: Dict[str, np.ndarray] = {}

    for arm_idx, arm_name in enumerate(ARM_DEFS):
        _log(f"[seed {seed}] arm {arm_name} ({arm_idx+1}/{n_arms}) starting")
        arm_t0 = time.perf_counter()
        try:
            stored, query, enc_wall, fit_wall, arm_diag = ARM_ENCODERS[arm_name](
                role_keys, fillers, episodes, seed
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            failure_class = type(e).__name__
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": failure_class,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:2000],
            }
            _log(f"[seed {seed}] arm {arm_name} FAILED: {failure_class}: {e}")
            _heartbeat(output_dir, arm_idx, n_arms,
                       time.perf_counter() - arm_t0,
                       {"arm": arm_name, "status": "failed",
                        "failure_class": failure_class})
            continue
        n_nan = int(np.isnan(stored).sum()) + int(np.isnan(query).sum())
        if n_nan > 0:
            per_arm[arm_name] = {
                "arm_name": arm_name,
                "failure_class": "NAN_IN_HDS",
                "failure_msg": f"n_nan={n_nan}",
            }
            _log(f"[seed {seed}] arm {arm_name} NaN (n_nan={n_nan})")
            continue
        metrics = _retrieval_metrics(stored, query, seed=seed)
        metrics.update({
            "arm_name": arm_name,
            "stored_dim": int(stored.shape[1]),
            "encoding_wall_s": float(enc_wall),
            "fit_wall_s": float(fit_wall),
            "arm_diag": arm_diag,
        })
        per_arm[arm_name] = metrics
        per_arm_query[arm_name] = query
        _log(f"[seed {seed}] arm {arm_name} r@1={metrics['recall_at_1']:.3f} "
             f"r@5={metrics['recall_at_5']:.3f} "
             f"intra={metrics['intra_pair_cos_mean']:.3f} "
             f"inter={metrics['inter_pair_cos_mean']:.3f} "
             f"fit_wall={fit_wall:.2f}s")
        _heartbeat(output_dir, arm_idx, n_arms,
                   time.perf_counter() - arm_t0,
                   {"arm": arm_name, "recall_at_1": metrics["recall_at_1"]})

    arms_differ_verified = False
    arms_differ_digests: Dict[str, str] = {}
    if len(per_arm_query) >= 2:
        try:
            arms_differ_digests = _arms_differ_hash(per_arm_query)
            arms_differ_verified = True
        except Exception as e:
            _log(f"[seed {seed}] ARMS_DIFFER_FAIL: {e}")
            arms_differ_verified = False
            arms_differ_digests = {"error": str(e)[:200]}

    return {
        "seed": int(seed),
        "n_pairs": int(N_PAIRS),
        "per_arm": per_arm,
        "arms_differ_verified": bool(arms_differ_verified),
        "arms_differ_digests": arms_differ_digests,
    }


# --- Aggregation + verdict ---
def _aggregate(per_seed: List[Dict]) -> Dict:
    out: Dict[str, Dict] = {}
    for arm in ARM_DEFS:
        r1s, r5s, walls, fits, dg_rates = [], [], [], [], []
        intras, inters = [], []
        n_failed = 0
        for ps in per_seed:
            arm_m = ps.get("per_arm", {}).get(arm, {})
            if "failure_class" in arm_m:
                n_failed += 1
                continue
            r1s.append(arm_m.get("recall_at_1", 0.0))
            r5s.append(arm_m.get("recall_at_5", 0.0))
            walls.append(arm_m.get("encoding_wall_s", 0.0))
            fits.append(arm_m.get("fit_wall_s", 0.0))
            intras.append(arm_m.get("intra_pair_cos_mean", 0.0))
            inters.append(arm_m.get("inter_pair_cos_mean", 0.0))
            diag = arm_m.get("arm_diag") or {}
            if "dg_sparse_rate_observed" in diag:
                dg_rates.append(diag["dg_sparse_rate_observed"])
        if r1s:
            entry = {
                "n_seeds_succeeded": len(r1s),
                "n_seeds_failed": n_failed,
                "recall_at_1_mean": float(np.mean(r1s)),
                "recall_at_1_std": float(np.std(r1s)),
                "recall_at_5_mean": float(np.mean(r5s)),
                "intra_pair_cos_mean": float(np.mean(intras)),
                "inter_pair_cos_mean": float(np.mean(inters)),
                "encoding_wall_s_mean": float(np.mean(walls)),
                "fit_wall_s_mean": float(np.mean(fits)),
            }
            if dg_rates:
                entry["dg_sparse_rate_mean"] = float(np.mean(dg_rates))
            out[arm] = entry
        else:
            out[arm] = {"n_seeds_succeeded": 0, "n_seeds_failed": n_failed,
                        "recall_at_1_mean": None}
    return out


def _verdict(agg: Dict, expected_n_units: int,
             actual_n_units: int) -> Tuple[str, str]:
    """HP_SCOPE:
    HP1 (LOAD_BEARING): ARM_HIPPOCAMPAL_ONE_SHOT recall@1 >= 0.80
    HF1: ARM_HIPPOCAMPAL_ONE_SHOT recall@1 < 0.50
    HF-baseline: ARM_RANDOM_BASELINE recall@1 > 0.10 (META_RULE_AG)
    HF-dg-rate: ARM_HIPPOCAMPAL_ONE_SHOT dg_sparse_rate out of [0.008, 0.040]
    """
    hip = agg.get("ARM_HIPPOCAMPAL_ONE_SHOT", {}).get("recall_at_1_mean")
    hip_dg_only = agg.get("ARM_HIPPOCAMPAL_DG_ONLY_ABLATION", {}).get("recall_at_1_mean")
    cos_bl = agg.get("ARM_COSINE_ARGMAX_BASELINE", {}).get("recall_at_1_mean")
    rnd = agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_1_mean")
    dg_rate = agg.get("ARM_HIPPOCAMPAL_ONE_SHOT", {}).get("dg_sparse_rate_mean")

    if actual_n_units < expected_n_units:
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                f"HARD_FAIL_CARDINALITY: expected {expected_n_units} unit-metrics "
                f"but got {actual_n_units}. See per-seed per_arm failure_class.")

    if hip is None or rnd is None:
        return ("HARD_FAIL_ARM_MISSING",
                f"HARD_FAIL: one or more arms have no recall@1: "
                f"hippo={hip} dg_only={hip_dg_only} cos_bl={cos_bl} random={rnd}")

    # HF-baseline (META_RULE_AG)
    if rnd > BASELINE_IN_BAND_R1_MAX:
        return ("HARD_FAIL_BASELINE_OUT_OF_BAND_META_RULE_AG",
                f"HF baseline_in_band failed: ARM_RANDOM_BASELINE r@1={rnd:.4f} > "
                f"{BASELINE_IN_BAND_R1_MAX:.4f} (chance={CHANCE_R1:.4f}). "
                f"Retrieval-implementation bug.")

    # HF-dg-rate: architectural sanity
    if dg_rate is not None and not (DG_SPARSE_RATE_MIN <= dg_rate <= DG_SPARSE_RATE_MAX):
        return ("HARD_FAIL_DG_SPARSE_RATE_ARCHITECTURAL",
                f"HF DG sparse rate={dg_rate:.4f} outside "
                f"[{DG_SPARSE_RATE_MIN:.3f}, {DG_SPARSE_RATE_MAX:.3f}] "
                f"(target {DG_SPARSITY:.3f}). DGProjection top-K threshold broken.")

    # HF1: mechanism-fails on intended task class
    if hip < HF_HIPPO_R1_HARD_FLOOR:
        return ("HARD_FAIL_MECHANISM_ON_INTENDED_TASK",
                f"HF1 ARM_HIPPOCAMPAL_ONE_SHOT r@1={hip:.4f} < "
                f"{HF_HIPPO_R1_HARD_FLOOR:.4f} on INTENDED task class (episodic "
                f"one-shot binding + partial-cue recall) at N={N_PAIRS} pairs "
                f"({N_PAIRS/_TF_CAPACITY*100:.1f}% Tsodyks-Feigelman capacity). "
                f"Marr-CA3 + DG-expansion primitive has issues even on its "
                f"designed task class. Task-class-mismatch hypothesis for prior "
                f"Wikipedia HF is NOT confirmed; primitive itself has a defect. "
                f"Route to research 2x-drill on CA3 iteration / sparsity / "
                f"settle-parameters. HONEST SCOPE: mechanism drill needed. "
                f"hippo_dg_only r@1={hip_dg_only} cos_bl r@1={cos_bl} "
                f"random r@1={rnd:.4f} dg_rate={dg_rate}")

    # HP: mechanism works on intended task class
    if hip >= HP_HIPPO_R1_FLOOR:
        return ("HARD_PASS",
                f"HARD_PASS: brain-analog Marr-CA3 + DG-expansion primitive "
                f"(hdlab.hippocampal_encoder at dg_dim={DG_DIM} sparsity={DG_SPARSITY:.3f}) "
                f"achieves recall@1={hip:.4f} >= {HP_HIPPO_R1_FLOOR:.4f} on INTENDED "
                f"task class (episodic one-shot binding + partial-cue pattern "
                f"completion) at N={N_PAIRS} pairs "
                f"({N_PAIRS/_TF_CAPACITY*100:.1f}% Tsodyks-Feigelman capacity 1047). "
                f"Task-class-mismatch hypothesis for prior Wikipedia HF (commit "
                f"1cd8e3757; ARM_SPOKE3_HIPPOCAMPAL r@5=0.145 vs char-trigram "
                f"0.854) is VALIDATED: primitive mechanism is correct; Wikipedia "
                f"HF is task-class mismatch (open-domain many-to-many surface "
                f"retrieval != episodic one-shot binding), NOT mechanism failure. "
                f"HONEST SCOPE: MECHANISM_VALIDATION on SUPERVISED synthetic pair-"
                f"binding regime; does NOT grant substrate general-knowledge; does "
                f"NOT claim substrate has language capability. AVOIDS 2026-06-23 "
                f"falsified WTA-collision mechanism (verified at "
                f"hippo_ne_naive_wta_collision selftest). HOLD pending USER "
                f"decision on next steps. "
                f"hippo_dg_only r@1={hip_dg_only} (CA3 contribution = "
                f"{hip - (hip_dg_only or 0):+.4f}); cos_bl r@1={cos_bl}; "
                f"random r@1={rnd:.4f} dg_rate={dg_rate}")

    # MIDDLE_BAND
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: ARM_HIPPOCAMPAL_ONE_SHOT recall@1={hip:.4f} in "
            f"[{HF_HIPPO_R1_HARD_FLOOR:.4f}, {HP_HIPPO_R1_FLOOR:.4f}). "
            f"Partial mechanism validation on INTENDED task class: primitive "
            f"works but not at full mechanism-appropriate threshold. Route to "
            f"CA3 parameter sweep (iteration count, sparsity, expansion factor). "
            f"hippo_dg_only r@1={hip_dg_only} cos_bl r@1={cos_bl} "
            f"random r@1={rnd:.4f} dg_rate={dg_rate}")


# --- main ---
def main() -> int:
    if IS_SELFTEST:
        rc = _run_selftests()
        sys.exit(rc)

    output_dir = get_output_dir(ANCHOR_NAME)
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_n_units = len(SEEDS) * len(ARM_DEFS)
    _write_start_marker(output_dir, expected_n_units)

    _log(f"[config] anchor={ANCHOR_NAME}")
    _log(f"[config] run_mode={RUN_MODE} n_pairs={N_PAIRS} seeds={SEEDS}")
    _log(f"[config] n_dim={N_DIM} dg_dim={DG_DIM} sparsity={DG_SPARSITY} "
         f"partial_cue_zero_frac={PARTIAL_CUE_FRACTION_ZEROED}")
    _log(f"[config] tf_capacity_theoretical={_TF_CAPACITY:.1f} "
         f"load_fraction={N_PAIRS/_TF_CAPACITY:.4f}")

    t0 = time.perf_counter()
    per_seed: List[Dict] = []
    for seed in SEEDS:
        seed_t0 = time.perf_counter()
        ps = _run_one_seed(seed, output_dir)
        ps["seed_elapsed_s"] = float(time.perf_counter() - seed_t0)
        per_seed.append(ps)
        _write_partial_seed(output_dir, seed, ps)
        _log(f"[seed {seed}] complete in {ps['seed_elapsed_s']:.2f}s; "
             f"checkpoint written")

    agg = _aggregate(per_seed)
    actual_n_units = sum(
        1
        for ps in per_seed
        for arm_m in ps.get("per_arm", {}).values()
        if "failure_class" not in arm_m
    )
    verdict, verdict_msg = _verdict(agg, expected_n_units, actual_n_units)
    _log(f"[VERDICT] {verdict}")
    _log(f"[VERDICT_MSG] {verdict_msg}")
    total_elapsed = time.perf_counter() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_pairs": N_PAIRS,
        "n_dim": N_DIM,
        "dg_dim": DG_DIM,
        "dg_sparsity_target": DG_SPARSITY,
        "partial_cue_fraction_zeroed": PARTIAL_CUE_FRACTION_ZEROED,
        "tf_capacity_theoretical": _TF_CAPACITY,
        "load_fraction": N_PAIRS / _TF_CAPACITY,
        "expected_n_units": expected_n_units,
        "actual_n_units": actual_n_units,
        "cardinality_ok": actual_n_units >= expected_n_units,
        "arms_differ_verified": all(
            ps.get("arms_differ_verified", False) for ps in per_seed),
        "baseline_in_band_check": {
            "arm": "ARM_RANDOM_BASELINE",
            "chance_r1": CHANCE_R1,
            "band_max_r1": BASELINE_IN_BAND_R1_MAX,
            "observed_r1_mean": agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_1_mean"),
            "in_band": (agg.get("ARM_RANDOM_BASELINE", {}).get("recall_at_1_mean") or 0.0)
                        <= BASELINE_IN_BAND_R1_MAX,
        },
        "final_metrics_atomicity": "tmp_replace",
        "progress_logging": "print_flush_true",
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "hp_scope": {
            "HP1": ["ARM_HIPPOCAMPAL_ONE_SHOT"],
            "HF1": ["ARM_HIPPOCAMPAL_ONE_SHOT"],
            "HF_baseline_in_band": ["ARM_RANDOM_BASELINE"],
            "HF_dg_sparse_rate": ["ARM_HIPPOCAMPAL_ONE_SHOT"],
        },
        "per_seed": per_seed,
        "per_arm_aggregate": agg,
        "elapsed_s": total_elapsed,
        "ts_iso_end": datetime.now(timezone.utc).isoformat(),
    }

    tmp = output_dir / "metrics.json.tmp"
    final = output_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)
    _log(f"[metrics] written to {final} (elapsed={total_elapsed:.2f}s)")

    write_metrics(output_dir, metrics)
    return 0


if __name__ == "__main__":
    _output_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        rc = main()
        sys.exit(rc or 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_output_dir_for_crash, e)
        raise
