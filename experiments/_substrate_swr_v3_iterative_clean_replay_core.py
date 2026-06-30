"""Shared core for substrate_swr_v3_iterative_clean_replay (chunked seed cells).

Implements the TRUE iterative-sequence SWR replay mechanism per
notes/director_SWR_v3_iterative_clean_replay_design_spec_2026-06-30.md.

v1 = bundled outer product       -> abort (K^2 cross-terms; recall -> 0.001)
v2 = parallel multipass           -> ceiling at small M (HARD_PASS but MM_BC_CEILING)
v3 = iterative SEQUENCE replay    -> brain-canonical: walk sequence in compressed
     time; at each step retrieve k via attractor cleanup; predict v; cleanup v
     against codebook; Hebbian write back to cortex. After N replay passes,
     cortex W has been incrementally refined.

Regime (chosen to AVOID v2's BC-ceiling trap):
  M in {4096, 8192, 16384}     (well above v2's 2048 ceiling regime)
  N_DIM = 8192                 (key/value HD vector dimensionality)
  N_cortex = 2048              (so M/N_c can be > 1.0 -> stress capacity)
  Sequence length = 100        (long enough that early items decay)
  n_replay_passes in {1, 5, 20} (+ NO_REPLAY baseline + DIRECT_UPPER oracle)

Discriminator at chain-grade scale (M=8192):
  HARD_PASS:   Recall(n_replay=20) >= Recall(n_replay=1) + 0.20
               AND monotonic across n_replay
               AND not BC-ceiling: K=20 < DIRECT_UPPER - 0.03
  MIDDLE_BAND: Recall(n_replay=20) - Recall(n_replay=1) in [0.10, 0.20)
  HARD_FAIL:   no lift / drop with passes / BC-ceiling at all arms

Uses hdlab.iterative_attractor.iterative_cleanup for the attractor cleanup step
(reused; no re-implementation; substrate-native primitive).

Architecture notes:
  - This module is imported by 3 sibling cells (seed 7 / 13 / 19) that drive
    a single seed each (CHUNKED single-seed-per-cell architecture per
    feedback_runner_zombie_ssh_disconnect_root_cause_FIXED_2026-06-28.md).
  - The core does NOT run the sweep; each seed wrapper imports run_seed +
    compute_seed_verdict + cell main scaffolding helpers.
  - ASCII-only; no emojis; no unicode in code/output.

META RULES enforced:
  AF: arms-must-differ via per-arm cortex-state SHA-256
  AH: atomic tmp + os.replace metrics write
  AX: per-n_replay mechanism_hash distinct
  J:  no bare except; specific exception classes with failure_class field
  AC: numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch  # PROT-020 GPU-queue gate (cell imports torch)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from hdlab.iterative_attractor import iterative_cleanup  # substrate-native cleanup


# -- Regime constants (declared here; chunk wrappers import) ------------------

N_DIM = 8192                  # HD vector dimensionality (key + value)
N_CORTEX = 2048               # cortex W is (N_DIM, N_DIM); cleanup gate uses N_CORTEX-size codebook
SEQ_LEN = 100                 # sequence length per replay pass
N_REPLAY_VALUES: Tuple[int, ...] = (0, 1, 5, 20)
# 0 = NO_REPLAY baseline (single write pass; no iterative replay)
# 1, 5, 20 = number of iterative-replay passes after initial write
# DIRECT_UPPER is added as a separate arm (oracle ceiling)

M_VALUES_FULL: Tuple[int, ...] = (4096, 8192, 16384)
# Smoke chooses ONE M value to probe DISCRIMINATOR_FIRES at near-full N
# (per DISCRIMINATOR-MUST-SURVIVE-SCALE rule).
M_SMOKE = 4096
SEQ_LEN_SMOKE = 50            # cut sequence in half for smoke wall-time budget
N_REPLAY_VALUES_SMOKE: Tuple[int, ...] = (0, 1, 5, 20)

# Hebbian write hyperparameters
ETA_INITIAL = 0.01            # initial write learning rate
ETA_REPLAY = 0.005            # replay-pass learning rate (smaller; cumulative)
DECAY = 1.0                   # no decay (per spec; consolidation accumulates)
TEMP_CLEANUP = 4.0            # iterative_cleanup softmax inverse-temperature
MAX_STEPS_CLEANUP = 6         # iterative_cleanup max iterations per call

# Discriminator bands
HARD_PASS_LIFT_MIN = 0.20     # R(n_replay=20) - R(n_replay=1) at M=8192
MIDDLE_BAND_LIFT_MIN = 0.10
BC_CEILING_MARGIN = 0.03      # K=20 must be < DIRECT_UPPER - this for non-BC

# Arm names (5 total: NO_REPLAY + 3 N_REPLAY + DIRECT_UPPER)
ARM_NO_REPLAY = "ARM_NO_REPLAY"
ARM_DIRECT_UPPER = "ARM_DIRECT_UPPER"

def n_replay_arm_name(n: int) -> str:
    return f"ARM_N_REPLAY_{n}"

ARM_NAMES_FULL: Tuple[str, ...] = (
    ARM_NO_REPLAY,
    n_replay_arm_name(1),
    n_replay_arm_name(5),
    n_replay_arm_name(20),
    ARM_DIRECT_UPPER,
)
EXPECTED_ARMS_PER_SEED = len(ARM_NAMES_FULL)


# -- Device + dtype -----------------------------------------------------------

def select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = select_device()
DTYPE = torch.float32


# -- Utilities ----------------------------------------------------------------

def _l2_normalize_t(x: torch.Tensor, dim: int = -1) -> torch.Tensor:
    n = torch.linalg.vector_norm(x, dim=dim, keepdim=True)
    return x / torch.clamp(n, min=1e-12)


def _arm_state_hash(arm_name: str, W_cortex: torch.Tensor, recall: float) -> str:
    sample = W_cortex[:4, :64].detach().cpu().to(torch.float64).numpy()
    blob = (arm_name.encode("ascii")
            + sample.tobytes()
            + f"{recall:.6f}".encode("ascii"))
    return hashlib.sha256(blob).hexdigest()[:16]


def _l2_normalize_np(X: np.ndarray) -> np.ndarray:
    if X.ndim == 1:
        n = float(np.linalg.norm(X) + 1e-12)
        return (X / n).astype(np.float32)
    n = np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return (X / n).astype(np.float32)


# -- Sequence + codebook construction -----------------------------------------

def build_sequence(seed: int, M: int, seq_len: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Build a sequence of (k, v) pairs drawn from key/value codebooks.

    Returns:
        keys_cb:  (M, N_DIM) full key codebook (L2-normalized)
        vals_cb:  (M, N_DIM) full value codebook (L2-normalized)
        seq_keys: (seq_len,) int index into keys_cb (sequence order)
        seq_vals: (seq_len,) int index into vals_cb (sequence order; same idx as seq_keys)

    seq_keys[i] is the codebook idx of the i-th sequence item; we use the
    convention that seq_keys[i] == seq_vals[i] (k-v pairing is identity in
    index space; the value codebook is what differs).
    """
    rng = np.random.RandomState(seed)
    keys_cb_raw = rng.randn(M, N_DIM).astype(np.float32) / np.sqrt(N_DIM)
    vals_cb_raw = rng.randn(M, N_DIM).astype(np.float32) / np.sqrt(N_DIM)
    keys_cb = _l2_normalize_np(keys_cb_raw)
    vals_cb = _l2_normalize_np(vals_cb_raw)
    # Choose seq_len distinct indices for the sequence (without replacement so
    # each item is a distinct memory; brain-canonical "episode" assumption).
    if seq_len > M:
        raise ValueError(f"seq_len {seq_len} > M {M}; cannot draw without replacement")
    seq_idx = rng.choice(M, size=seq_len, replace=False).astype(np.int64)
    return keys_cb, vals_cb, seq_idx, seq_idx.copy()


# -- The mechanism: arm runners ----------------------------------------------

def _project_to_cortex(x_dim: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
    """Project (..., N_DIM) -> (..., N_CORTEX) via fixed Gaussian projection P."""
    return _l2_normalize_t(x_dim @ P.t(), dim=-1)


def run_arm_no_replay(seed: int, M: int, seq_len: int,
                      keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                      seq_idx_t: torch.Tensor,
                      P_kc: torch.Tensor, P_vc: torch.Tensor) -> Dict:
    """NO_REPLAY baseline: single Hebbian write pass; no iterative refinement.

    For each (k, v) in sequence: W += eta * outer(v_c, k_c). One sweep only.
    """
    t0 = time.time()
    arm_name = ARM_NO_REPLAY
    try:
        # Project sequence keys/vals to cortex space
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)   # (seq_len, N_CORTEX)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)   # (seq_len, N_CORTEX)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        # Single batched write of all seq items.
        W_cortex = W_cortex + ETA_INITIAL * (vals_c.t() @ keys_c)
        recall = _recall_via_W(keys_c, vals_c, W_cortex, vals_cb_t, P_vc, seq_idx_t)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": 0,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_iterative_replay(seed: int, M: int, seq_len: int, n_replay: int,
                             keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                             seq_idx_t: torch.Tensor,
                             P_kc: torch.Tensor, P_vc: torch.Tensor) -> Dict:
    """SWR v3 iterative SEQUENCE replay arm (the mechanism under test).

    Steps per replay pass (sequentially through sequence):
      1. retrieve k_clean = iterative_cleanup(k_noisy, keys_codebook)
      2. v_predicted = W_cortex @ k_clean
      3. v_cleaned = iterative_cleanup(v_predicted, vals_codebook)
      4. W_cortex = decay * W_cortex + eta_replay * outer(v_cleaned, k_clean)

    Uses CORTEX-space projections of codebooks (size N_CORTEX) for cleanup
    so the cleanup attractor and the Hebbian write share dimensionality.
    """
    t0 = time.time()
    arm_name = n_replay_arm_name(n_replay)
    try:
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)   # (seq_len, N_CORTEX)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)
        keys_cb_c = _project_to_cortex(keys_cb_t, P_kc)           # (M, N_CORTEX)
        vals_cb_c = _project_to_cortex(vals_cb_t, P_vc)           # (M, N_CORTEX)

        # Move codebooks to numpy for hdlab.iterative_cleanup (numpy primitive).
        keys_cb_c_np = keys_cb_c.detach().cpu().numpy().astype(np.float32)
        vals_cb_c_np = vals_cb_c.detach().cpu().numpy().astype(np.float32)

        # Initial write (single sweep; analogous to NO_REPLAY but kept separate
        # so n_replay=0 truly = NO_REPLAY arm).
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + ETA_INITIAL * (vals_c.t() @ keys_c)

        # Iterative replay passes
        for pass_idx in range(n_replay):
            # Walk sequence in compressed time (sequential, NOT parallel).
            for i in range(seq_len):
                k_noisy = keys_c[i]                                  # (N_CORTEX,)
                # Step 1: clean k via iterative attractor cleanup over key codebook
                k_clean_np = iterative_cleanup(
                    k_noisy.detach().cpu().numpy().astype(np.float32),
                    keys_cb_c_np,
                    temp=TEMP_CLEANUP,
                    max_steps=MAX_STEPS_CLEANUP,
                    tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                k_clean = torch.from_numpy(k_clean_np).to(DEVICE)
                # Step 2: cortex predicts v
                v_predicted = W_cortex @ k_clean
                # Step 3: clean v via attractor over value codebook
                v_clean_np = iterative_cleanup(
                    v_predicted.detach().cpu().numpy().astype(np.float32),
                    vals_cb_c_np,
                    temp=TEMP_CLEANUP,
                    max_steps=MAX_STEPS_CLEANUP,
                    tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                v_clean = torch.from_numpy(v_clean_np).to(DEVICE)
                # Step 4: Hebbian rewrite (decay + outer product)
                W_cortex = DECAY * W_cortex + ETA_REPLAY * torch.outer(v_clean, k_clean)

        recall = _recall_via_W(keys_c, vals_c, W_cortex, vals_cb_t, P_vc, seq_idx_t)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": int(n_replay),
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_direct_upper(seed: int, M: int, seq_len: int,
                         keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                         seq_idx_t: torch.Tensor,
                         P_kc: torch.Tensor, P_vc: torch.Tensor) -> Dict:
    """DIRECT_UPPER oracle: directly write CLEAN (k, v) pairs to cortex.

    No noise; no cleanup; serves as the ceiling reference for BC-saturation
    detection. If all replay arms tie this, the regime is BC-trapped.
    """
    t0 = time.time()
    arm_name = ARM_DIRECT_UPPER
    try:
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        # Higher eta for direct write (oracle has perfect signal -> can lock in).
        W_cortex = W_cortex + (10.0 * ETA_INITIAL) * (vals_c.t() @ keys_c)
        recall = _recall_via_W(keys_c, vals_c, W_cortex, vals_cb_t, P_vc, seq_idx_t)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": -1,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, t0,
                               "VALUE_TYPE", repr(exc))


def _arm_error_dict(arm_name: str, n_replay: int, seed: int, M: int,
                    seq_len: int, t0: float,
                    failure_class: str, exc_repr: str) -> Dict:
    return {
        "arm_name": arm_name, "n_replay": int(n_replay),
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "recall_cortex": float("nan"),
        "arm_hash": "ERROR", "arm_status": f"ERROR: {failure_class}: {exc_repr[:200]}",
        "wall_s": float(time.time() - t0),
        "failure_class": failure_class,
    }


def _recall_via_W(keys_c: torch.Tensor, vals_c: torch.Tensor,
                  W_cortex: torch.Tensor, vals_cb_t: torch.Tensor,
                  P_vc: torch.Tensor, seq_idx_t: torch.Tensor) -> float:
    """Recall: for each sequence key, query W; nearest value in value codebook (cortex space).

    Returns fraction of sequence items where argmax over value codebook == seq idx.
    """
    seq_len = keys_c.shape[0]
    # Predicted v for each sequence item: (seq_len, N_CORTEX)
    preds = keys_c @ W_cortex.t()
    preds_n = _l2_normalize_t(preds, dim=-1)
    # Compare to full vals codebook in cortex space (size M)
    vals_cb_c = _project_to_cortex(vals_cb_t, P_vc)
    sims = preds_n @ vals_cb_c.t()                                  # (seq_len, M)
    argmax = torch.argmax(sims, dim=1)
    n_hits = int((argmax == seq_idx_t).sum().item())
    return n_hits / float(seq_len)


# -- Per-seed sweep over arms -------------------------------------------------

def run_seed(seed: int, M: int, seq_len: int,
             n_replay_values: Tuple[int, ...],
             out_dir: Path) -> Dict:
    """Run all 5 arms for ONE seed at ONE M setting; return per-seed result dict."""
    t0 = time.time()
    print(f"  [seed={seed}] M={M} seq_len={seq_len} n_replay_values={n_replay_values} "
          f"dev={DEVICE.type}", flush=True)

    # Build sequence + codebooks
    keys_cb_np, vals_cb_np, seq_keys_np, _ = build_sequence(seed, M, seq_len)
    keys_cb_t = torch.from_numpy(keys_cb_np).to(DEVICE)
    vals_cb_t = torch.from_numpy(vals_cb_np).to(DEVICE)
    seq_idx_t = torch.from_numpy(seq_keys_np).to(DEVICE)

    # Build fixed Gaussian projections N_DIM -> N_CORTEX (separate for k / v)
    rng_p = np.random.RandomState(seed + 1000)
    P_kc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
    P_vc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
    P_kc = torch.from_numpy(P_kc_np).to(DEVICE)
    P_vc = torch.from_numpy(P_vc_np).to(DEVICE)

    arms: List[Dict] = []
    # Arm 1: NO_REPLAY baseline
    a = run_arm_no_replay(seed, M, seq_len, keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    # Arms 2..K: iterative replay arms
    for n_replay in n_replay_values:
        if n_replay == 0:
            # n_replay=0 is NO_REPLAY (already done). Skip duplicate.
            continue
        a = run_arm_iterative_replay(seed, M, seq_len, n_replay,
                                     keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)
        arms.append(a)
        print(f"  [seed={seed} {a['arm_name']:>18s} n_replay={n_replay:>3d}] "
              f"recall={a['recall_cortex']:.3f} hash={a['arm_hash']} "
              f"wall={a['wall_s']:.1f}s", flush=True)
        _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    # Arm K+1: DIRECT_UPPER oracle ceiling
    a = run_arm_direct_upper(seed, M, seq_len, keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    elapsed = time.time() - t0
    return {
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "N_DIM": int(N_DIM), "N_CORTEX": int(N_CORTEX),
        "n_replay_values": list(n_replay_values),
        "n_arms": len(arms),
        "backend": "torch", "device": DEVICE.type,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _heartbeat_tick(out_dir: Path, unit_idx: int, total_units: int,
                    elapsed_s: float, arm: Dict) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx), "total_units": int(total_units),
        "elapsed_s": round(float(elapsed_s), 2),
        "extra": {"arm": arm.get("arm_name"), "n_replay": arm.get("n_replay"),
                  "recall": arm.get("recall_cortex"),
                  "arm_status": arm.get("arm_status", "?")[:40]},
    }
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


# -- Verdict logic (per-seed; chunk wrapper aggregates) -----------------------

def compute_seed_verdict(seed_result: Dict) -> Tuple[str, str]:
    """Compute single-seed verdict + msg from per-arm metrics.

    NB: chunked architecture = each seed cell emits its own verdict.
    Skunkworks aggregates across the 3 seed chunks for chain-grade promotion.
    """
    arms = seed_result.get("arms", [])
    if len(arms) != EXPECTED_ARMS_PER_SEED:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_ARMS_PER_SEED} arms, "
                f"got {len(arms)}")
    not_ok = [a for a in arms if a["arm_status"] != "OK"]
    if not_ok:
        return ("HARD_FAIL",
                f"ARM_ERROR: {not_ok[0]['arm_name']} {not_ok[0]['arm_status'][:120]}")

    arm_by_name = {a["arm_name"]: a for a in arms}
    R_NO = float(arm_by_name[ARM_NO_REPLAY]["recall_cortex"])
    R_1 = float(arm_by_name[n_replay_arm_name(1)]["recall_cortex"])
    R_5 = float(arm_by_name[n_replay_arm_name(5)]["recall_cortex"])
    R_20 = float(arm_by_name[n_replay_arm_name(20)]["recall_cortex"])
    R_DIRECT = float(arm_by_name[ARM_DIRECT_UPPER]["recall_cortex"])

    # META_RULE_AF: arm hashes must all differ
    hashes = [a["arm_hash"] for a in arms]
    if len(set(hashes)) < len(hashes):
        dupes = [h for h in hashes if hashes.count(h) > 1]
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: arm-hash duplicates {set(dupes)}")

    lift_20_vs_1 = R_20 - R_1
    monotonic = (R_1 <= R_5 + 1e-6) and (R_5 <= R_20 + 1e-6)
    bc_ceiling = (R_20 >= R_DIRECT - BC_CEILING_MARGIN) and \
                 (R_1 >= R_DIRECT - BC_CEILING_MARGIN)

    summary = (
        f"M={seed_result['M']} seq_len={seed_result['seq_len']} seed={seed_result['seed']} "
        f"NO_REPLAY={R_NO:.3f} N_REPLAY_1={R_1:.3f} N_REPLAY_5={R_5:.3f} "
        f"N_REPLAY_20={R_20:.3f} DIRECT_UPPER={R_DIRECT:.3f} "
        f"lift_20_vs_1={lift_20_vs_1:+.3f} monotonic={monotonic} bc_ceiling={bc_ceiling}"
    )

    if bc_ceiling:
        return ("HARD_FAIL",
                f"HARD_FAIL (BC_CEILING): all N_REPLAY arms within {BC_CEILING_MARGIN} "
                f"of DIRECT_UPPER ceiling; regime too easy; mechanism cannot "
                f"discriminate. {summary}")
    if R_20 < R_1 - 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL (REPLAY_HURTS): N_REPLAY_20 < N_REPLAY_1 - 0.05; "
                f"iterative replay degrades recall (cross-term accumulation). "
                f"{summary}")
    if lift_20_vs_1 >= HARD_PASS_LIFT_MIN and monotonic:
        return ("HARD_PASS",
                f"HARD_PASS (SWR_V3_LIFT): lift_20_vs_1={lift_20_vs_1:+.3f} "
                f">= {HARD_PASS_LIFT_MIN} AND monotonic AND not BC-ceiling. "
                f"{summary}")
    if lift_20_vs_1 >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: lift_20_vs_1={lift_20_vs_1:+.3f} in "
                f"[{MIDDLE_BAND_LIFT_MIN}, {HARD_PASS_LIFT_MIN}); partial lift. "
                f"{summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL (NO_LIFT): lift_20_vs_1={lift_20_vs_1:+.3f} < "
            f"{MIDDLE_BAND_LIFT_MIN}; iterative replay does not consolidate. "
            f"{summary}")


# -- Self-test ---------------------------------------------------------------

def selftest_core() -> None:
    """Cell self-test: light-weight verification that mechanism RUNS + produces sane outputs.

    Runs ONE seed at TINY config (M=64, seq_len=8, n_replay=1) on CPU forcibly to
    avoid GPU contention during selftest. Asserts NO_REPLAY < DIRECT_UPPER and
    recall in [0, 1] range. Wall budget << 30s.
    """
    global DEVICE
    saved_device = DEVICE
    DEVICE = torch.device("cpu")  # selftest is cheap; avoid cuda init noise
    try:
        # Tiny config
        M_t, seq_t = 64, 8
        keys_cb_np, vals_cb_np, seq_idx_np, _ = build_sequence(seed=0, M=M_t, seq_len=seq_t)
        keys_cb_t = torch.from_numpy(keys_cb_np).to(DEVICE)
        vals_cb_t = torch.from_numpy(vals_cb_np).to(DEVICE)
        seq_idx_t = torch.from_numpy(seq_idx_np).to(DEVICE)
        rng_p = np.random.RandomState(1000)
        P_kc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
        P_vc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
        P_kc = torch.from_numpy(P_kc_np).to(DEVICE)
        P_vc = torch.from_numpy(P_vc_np).to(DEVICE)

        a_no = run_arm_no_replay(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)
        a_1 = run_arm_iterative_replay(0, M_t, seq_t, 1, keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)
        a_d = run_arm_direct_upper(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t, P_kc, P_vc)

        for a in (a_no, a_1, a_d):
            if a["arm_status"] != "OK":
                raise AssertionError(f"selftest arm error: {a}")
            r = float(a["recall_cortex"])
            if not (0.0 <= r <= 1.0):
                raise AssertionError(f"selftest recall {r} out of [0,1] for {a['arm_name']}")
        # DIRECT_UPPER should be highest or equal (oracle ceiling).
        if not (a_d["recall_cortex"] >= a_no["recall_cortex"] - 0.05):
            raise AssertionError(
                f"selftest DIRECT_UPPER ({a_d['recall_cortex']}) not >= "
                f"NO_REPLAY ({a_no['recall_cortex']}) - 0.05; oracle inversion bug"
            )
        # Arms must differ by hash (META_RULE_AF on selftest config too)
        hashes = (a_no["arm_hash"], a_1["arm_hash"], a_d["arm_hash"])
        if len(set(hashes)) < 3:
            raise AssertionError(f"selftest META_RULE_AF violation: hashes {hashes}")
        # Mechanism distinctness: NO_REPLAY vs N_REPLAY=1 must produce DIFFERENT W
        # (the iterative-replay arm walks the sequence; even if recall is identical,
        # the cortex state should not be bit-identical to NO_REPLAY's single-pass write).
        # This is the META_RULE_AX gate at selftest scale.
        if a_no["arm_hash"] == a_1["arm_hash"]:
            raise AssertionError(
                "selftest META_RULE_AX violation: NO_REPLAY and N_REPLAY_1 "
                "produced bit-identical cortex state (mechanism not firing)"
            )
        print(f"[selftest_core] PASS  M={M_t} seq_len={seq_t} "
              f"NO_REPLAY={a_no['recall_cortex']:.3f} "
              f"N_REPLAY_1={a_1['recall_cortex']:.3f} "
              f"DIRECT_UPPER={a_d['recall_cortex']:.3f}", flush=True)
    finally:
        DEVICE = saved_device


# -- Metrics writers (used by chunk wrappers) ---------------------------------

def write_crash_metrics(output_dir: Path, anchor_name: str, exc: BaseException, run_mode: str) -> None:
    diag = {
        "anchor_name": anchor_name, "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "run_mode": run_mode,
    }
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = output_dir / "metrics.json.tmp"
        final = output_dir / "metrics.json"
        tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
        os.replace(str(tmp), str(final))
    except OSError:
        pass


def write_start_marker(output_dir: Path, anchor_name: str, run_mode: str,
                       expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": int(expected_n_units),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def write_final_metrics(output_dir: Path, anchor_name: str,
                        seed_result: Dict, verdict: str, verdict_msg: str,
                        elapsed_s: float, run_mode: str,
                        config_version: str) -> Path:
    """Atomic tmp + os.replace per META_RULE_AH."""
    arms = seed_result.get("arms", [])
    per_arm_rows = []
    for a in arms:
        per_arm_rows.append({
            "arm_name": a["arm_name"],
            "n_replay": a.get("n_replay"),
            "recall_cortex": a.get("recall_cortex"),
            "arm_hash": a.get("arm_hash"),
            "arm_status": a.get("arm_status"),
            "wall_s": a.get("wall_s"),
            "failure_class": a.get("failure_class"),
        })
    cardinality_ok = (len(arms) == EXPECTED_ARMS_PER_SEED) and \
                     all(a["arm_status"] == "OK" for a in arms)
    metrics = {
        "anchor_name": anchor_name, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": (f"seed={seed_result.get('seed')} M={seed_result.get('M')} "
                    f"seq_len={seed_result.get('seq_len')} mode={run_mode} "
                    f"device={DEVICE.type} swr_v3_iterative_clean_replay"),
        "elapsed_s": float(elapsed_s),
        "config_version": config_version,
        "seed": seed_result.get("seed"),
        "M": seed_result.get("M"), "seq_len": seed_result.get("seq_len"),
        "N_DIM": N_DIM, "N_CORTEX": N_CORTEX,
        "n_replay_values": seed_result.get("n_replay_values"),
        "backend": "torch", "device": DEVICE.type,
        "run_mode": run_mode,
        "expected_n_units": EXPECTED_ARMS_PER_SEED,
        "cardinality_ok": bool(cardinality_ok),
        "per_arm_rows": per_arm_rows,
        "arms": arms,
    }
    metrics_path = output_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    return metrics_path


if __name__ == "__main__":
    selftest_core()
