"""Shared core for substrate_swr_v3_2_sparse_dg_burst (chunked seed cells).

v3.2 = v3.1 mechanism (iterative SEQUENCE replay + noisy-cue retrieval)
       + SPARSE-DG BURST ENCODING (Option B per Director 2026-06-30).

Lineage:
  v3 (commit 48be1bd7)         clean-cue retrieval -> BC_CEILING (all 1.000)
  v3.1 (commit 1654fd05)       noisy-cue retrieval; still BC: clean-key
                               projection P_kc @ keys is already a fixed
                               point of iterative_cleanup (no noise to clean),
                               so 0/1/5/20 passes all return identical 0.380.
  v3.2 (this core)             KEY CHANGE: encoded keys are sparse_kWTA bursts
                               (10% active, sign-preserving). Sparse keys have
                               structural noise that iterative cleanup can
                               actually project toward the dense codebook
                               attractor basins. Mechanism now has signal to
                               clean -> replay passes can lift recall.

Mechanism (v3.2):
  keys_burst = sparse_kWTA(keys_raw @ P_kc, k_active = 0.1 * N_DIM)   # NEW
  vals_burst = sparse_kWTA(vals_raw @ P_vc, k_active = 0.1 * N_DIM)   # NEW
  -> renormalize to unit L2
  -> Hebbian write W = eta * (vals_burst.T @ keys_burst)
  for pass_idx in range(n_replay):
      for k_sparse, v_sparse in zip(seq_keys_burst, seq_vals_burst):
          k_clean = iterative_cleanup(k_sparse, keys_codebook_burst)
          v_predict = W @ k_clean
          v_clean = iterative_cleanup(v_predict, vals_codebook_burst)
          W = DECAY * W + ETA_REPLAY * outer(v_clean, k_clean)
  noisy_cue = L2(seq_keys_burst + sigma_query * randn)
  recall = (argmax(L2(noisy_cue @ W.T) @ vals_codebook_burst.T) == seq_idx).mean()

Architecture: CHUNKED single-seed-per-cell. This module is imported by 3
sibling cells (seeds 7 / 13 / 19). Reuses the v3.1 verdict logic
(NO_REPLAY <= 0.50; lift_20_vs_no >= 0.20 -- v3.2 retuned bands per spec).

META rules enforced:
  AF arms-must-differ SHA-256
  AH atomic tmp + os.replace metrics write
  AX per-n_replay mechanism_hash distinct
  J  no bare except; specific exception classes; failure_class field
  AY verdict-emitter auto-demote on encoder distinctness=False (smoke check)
  Q  saturation check at k_active boundary (sparse mass != 0)
  AC numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

# CELL-TEMPLATE MANDATORY:
# - arms_differ_verified at smoke gate (META_RULE_AF)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace)
# - except SystemExit: raise BEFORE except Exception
# - baseline_in_band at smoke (META_RULE_AG; 0.20 < NO_REPLAY < 0.80)
# - discriminator survives scale (SAME sigma_query+k_active for smoke and full)
# - HARD_PASS strictly above floor + band-width margin (META_RULE_L)
# - per-unit failure-class instrumentation (META_RULE_J)
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
import torch  # PROT-020 GPU-queue gate

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from hdlab.iterative_attractor import iterative_cleanup


# -- Regime constants (v3.2) --------------------------------------------------

N_DIM = 8192
N_CORTEX = 2048
SEQ_LEN = 100                     # full
SEQ_LEN_SMOKE = 50                # smoke
N_REPLAY_VALUES: Tuple[int, ...] = (0, 1, 5, 20)
N_REPLAY_VALUES_SMOKE: Tuple[int, ...] = (0, 1, 5, 20)

M_VALUES_FULL: Tuple[int, ...] = (4096, 8192, 16384)
M_SMOKE = 4096

# v3.2 KEY parameters
SIGMA_QUERY = 0.5                 # retained from v3.1 noisy-cue protocol
K_ACTIVE_FRAC = 0.10              # NEW: sparse-DG burst sparsity (10% of N_DIM)
                                  # HYPOTHESIZED@spec_option_B: NO_REPLAY ~0.30
                                  # (sparse encode reduces effective SNR vs dense)

ETA_INITIAL = 0.01
ETA_REPLAY = 0.005
DECAY = 1.0
TEMP_CLEANUP = 4.0
MAX_STEPS_CLEANUP = 6

# Discriminator bands (v3.2 retuned per spec)
HARD_PASS_LIFT_MIN = 0.20         # lift over NO_REPLAY
HARD_PASS_NO_REPLAY_CEILING = 0.50
MIDDLE_BAND_LIFT_MIN = 0.10
BC_CEILING_MARGIN = 0.03

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


# -- v3.2 KEY NEW: sparse_kWTA burst encoder ---------------------------------

def sparse_kWTA_t(x: torch.Tensor, k_active: int) -> torch.Tensor:
    """Sparse k-Winners-Take-All on last dim. Keep top-k by |x|; preserve signs;
    zero the rest.

    Args:
        x: (..., D) tensor.
        k_active: number of active components to keep per row.

    Returns:
        Same shape as x; sparse (rows have k_active nonzeros).
    """
    if x.dim() == 1:
        x = x.unsqueeze(0)
        squeeze_back = True
    else:
        squeeze_back = False
    abs_x = x.abs()
    # topk over last dim
    topk = torch.topk(abs_x, k_active, dim=-1, largest=True)
    mask = torch.zeros_like(x)
    mask.scatter_(-1, topk.indices, 1.0)
    out = x * mask  # preserves signs and magnitudes at active positions
    if squeeze_back:
        out = out.squeeze(0)
    return out


def encode_keys_sparse(keys_raw_t: torch.Tensor, P_kc: torch.Tensor,
                       k_active: int) -> torch.Tensor:
    """Sparse-DG burst encoder: project then kWTA, then L2-normalize.

    Args:
        keys_raw_t: (M, N_DIM) raw vectors.
        P_kc: (N_CORTEX, N_DIM) projection matrix (note: cortex is rows).
        k_active: number of active components per encoded vector.

    Returns:
        (M, N_CORTEX) sparse encoded vectors, L2-normalized.
    """
    projected = keys_raw_t @ P_kc.t()           # (M, N_CORTEX)
    sparse = sparse_kWTA_t(projected, k_active=k_active)
    return _l2_normalize_t(sparse, dim=-1)


def build_sequence(seed: int, M: int, seq_len: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys_cb_raw = rng.randn(M, N_DIM).astype(np.float32) / np.sqrt(N_DIM)
    vals_cb_raw = rng.randn(M, N_DIM).astype(np.float32) / np.sqrt(N_DIM)
    keys_cb = _l2_normalize_np(keys_cb_raw)
    vals_cb = _l2_normalize_np(vals_cb_raw)
    if seq_len > M:
        raise ValueError(f"seq_len {seq_len} > M {M}; cannot draw without replacement")
    seq_idx = rng.choice(M, size=seq_len, replace=False).astype(np.int64)
    return keys_cb, vals_cb, seq_idx, seq_idx.copy()


# -- v3.2 noisy-cue recall (operates in sparse-burst space) -------------------

def _recall_via_W_noisy_sparse(seq_keys_burst: torch.Tensor,
                               W_cortex: torch.Tensor,
                               vals_cb_burst: torch.Tensor,
                               seq_idx_t: torch.Tensor,
                               seed_for_noise: int,
                               sigma_query: float) -> float:
    """Recall under NOISY-CUE retrieval in sparse-burst encoding space.

    The cue is the sequence's sparse-burst encoded key + noise (then L2-norm).
    Predicted value = noisy_cue @ W.T, then cosine match against the
    sparse-burst vals codebook.
    """
    seq_len = seq_keys_burst.shape[0]
    g = torch.Generator(device=seq_keys_burst.device).manual_seed(int(seed_for_noise) + 4242)
    noise = sigma_query * torch.randn(seq_keys_burst.shape, generator=g,
                                      dtype=seq_keys_burst.dtype,
                                      device=seq_keys_burst.device)
    noisy_keys = _l2_normalize_t(seq_keys_burst + noise, dim=-1)
    preds = noisy_keys @ W_cortex.t()
    preds_n = _l2_normalize_t(preds, dim=-1)
    sims = preds_n @ vals_cb_burst.t()
    argmax = torch.argmax(sims, dim=1)
    n_hits = int((argmax == seq_idx_t).sum().item())
    return n_hits / float(seq_len)


# -- Arm runners --------------------------------------------------------------

def _build_codebooks(keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                     P_kc: torch.Tensor, P_vc: torch.Tensor,
                     k_active: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Encode codebooks in sparse-burst space (used for cleanup + recall)."""
    keys_cb_burst = encode_keys_sparse(keys_cb_t, P_kc, k_active)
    vals_cb_burst = encode_keys_sparse(vals_cb_t, P_vc, k_active)
    return keys_cb_burst, vals_cb_burst


def run_arm_no_replay(seed: int, M: int, seq_len: int,
                      keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                      seq_idx_t: torch.Tensor,
                      P_kc: torch.Tensor, P_vc: torch.Tensor,
                      sigma_query: float, k_active: int) -> Dict:
    """NO_REPLAY baseline: single Hebbian write in sparse-burst space."""
    t0 = time.time()
    arm_name = ARM_NO_REPLAY
    try:
        keys_cb_burst, vals_cb_burst = _build_codebooks(
            keys_cb_t, vals_cb_t, P_kc, P_vc, k_active)
        keys_seq_burst = keys_cb_burst[seq_idx_t]
        vals_seq_burst = vals_cb_burst[seq_idx_t]
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + ETA_INITIAL * (vals_seq_burst.t() @ keys_seq_burst)
        recall = _recall_via_W_noisy_sparse(keys_seq_burst, W_cortex,
                                            vals_cb_burst, seq_idx_t,
                                            seed, sigma_query)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex, keys_cb_burst, vals_cb_burst
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": 0,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "k_active": int(k_active),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, k_active, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, k_active, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, k_active, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_iterative_replay(seed: int, M: int, seq_len: int, n_replay: int,
                             keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                             seq_idx_t: torch.Tensor,
                             P_kc: torch.Tensor, P_vc: torch.Tensor,
                             sigma_query: float, k_active: int) -> Dict:
    """SWR v3.2 iterative SEQUENCE replay in sparse-burst space + noisy-cue retrieval."""
    t0 = time.time()
    arm_name = n_replay_arm_name(n_replay)
    try:
        keys_cb_burst, vals_cb_burst = _build_codebooks(
            keys_cb_t, vals_cb_t, P_kc, P_vc, k_active)
        keys_seq_burst = keys_cb_burst[seq_idx_t]
        vals_seq_burst = vals_cb_burst[seq_idx_t]

        keys_cb_burst_np = keys_cb_burst.detach().cpu().numpy().astype(np.float32)
        vals_cb_burst_np = vals_cb_burst.detach().cpu().numpy().astype(np.float32)

        # Initial single-pass Hebbian write
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + ETA_INITIAL * (vals_seq_burst.t() @ keys_seq_burst)

        # Iterative replay passes (sparse-burst cleanup signal -- now non-vacuous)
        for pass_idx in range(n_replay):
            for i in range(seq_len):
                k_sparse = keys_seq_burst[i]
                k_clean_np = iterative_cleanup(
                    k_sparse.detach().cpu().numpy().astype(np.float32),
                    keys_cb_burst_np,
                    temp=TEMP_CLEANUP, max_steps=MAX_STEPS_CLEANUP, tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                k_clean = torch.from_numpy(k_clean_np).to(DEVICE)
                v_predicted = W_cortex @ k_clean
                v_clean_np = iterative_cleanup(
                    v_predicted.detach().cpu().numpy().astype(np.float32),
                    vals_cb_burst_np,
                    temp=TEMP_CLEANUP, max_steps=MAX_STEPS_CLEANUP, tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                v_clean = torch.from_numpy(v_clean_np).to(DEVICE)
                W_cortex = DECAY * W_cortex + ETA_REPLAY * torch.outer(v_clean, k_clean)

        recall = _recall_via_W_noisy_sparse(keys_seq_burst, W_cortex,
                                            vals_cb_burst, seq_idx_t,
                                            seed, sigma_query)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex, keys_cb_burst, vals_cb_burst
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": int(n_replay),
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "k_active": int(k_active),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, k_active, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, k_active, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, k_active, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_direct_upper(seed: int, M: int, seq_len: int,
                         keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                         seq_idx_t: torch.Tensor,
                         P_kc: torch.Tensor, P_vc: torch.Tensor,
                         sigma_query: float, k_active: int) -> Dict:
    """DIRECT_UPPER oracle: no encoding noise (dense keys), no retrieval noise.

    Uses CLEAN dense L2-normalized keys at cortex projection (not sparse_kWTA);
    bypasses retrieval noise entirely. Functions as the absolute ceiling for
    this regime; informs cell-author whether mechanism + sparse encoding
    can plausibly reach the oracle bound.
    """
    t0 = time.time()
    arm_name = ARM_DIRECT_UPPER
    try:
        # Dense clean key projection (NOT sparse_kWTA) for oracle ceiling
        keys_c_dense = _l2_normalize_t(keys_cb_t[seq_idx_t] @ P_kc.t(), dim=-1)
        vals_c_dense = _l2_normalize_t(vals_cb_t[seq_idx_t] @ P_vc.t(), dim=-1)
        vals_cb_dense = _l2_normalize_t(vals_cb_t @ P_vc.t(), dim=-1)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + (10.0 * ETA_INITIAL) * (vals_c_dense.t() @ keys_c_dense)
        # Oracle: no retrieval noise (sigma=0)
        preds = keys_c_dense @ W_cortex.t()
        preds_n = _l2_normalize_t(preds, dim=-1)
        sims = preds_n @ vals_cb_dense.t()
        argmax = torch.argmax(sims, dim=1)
        n_hits = int((argmax == seq_idx_t).sum().item())
        recall = n_hits / float(seq_len)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": -1,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "k_active": int(k_active),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, k_active, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, k_active, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, k_active, t0,
                               "VALUE_TYPE", repr(exc))


def _arm_error_dict(arm_name: str, n_replay: int, seed: int, M: int,
                    seq_len: int, sigma_query: float, k_active: int, t0: float,
                    failure_class: str, exc_repr: str) -> Dict:
    return {
        "arm_name": arm_name, "n_replay": int(n_replay),
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "sigma_query": float(sigma_query),
        "k_active": int(k_active),
        "recall_cortex": float("nan"),
        "arm_hash": "ERROR", "arm_status": f"ERROR: {failure_class}: {exc_repr[:200]}",
        "wall_s": float(time.time() - t0),
        "failure_class": failure_class,
    }


# -- Per-seed sweep -----------------------------------------------------------

def run_seed(seed: int, M: int, seq_len: int,
             n_replay_values: Tuple[int, ...],
             sigma_query: float,
             k_active: int,
             out_dir: Path) -> Dict:
    """Run all 5 arms for ONE seed under (sigma_query, k_active) regime."""
    t0 = time.time()
    print(f"  [seed={seed}] M={M} seq_len={seq_len} sigma_query={sigma_query} "
          f"k_active={k_active} n_replay_values={n_replay_values} dev={DEVICE.type}",
          flush=True)

    keys_cb_np, vals_cb_np, seq_keys_np, _ = build_sequence(seed, M, seq_len)
    keys_cb_t = torch.from_numpy(keys_cb_np).to(DEVICE)
    vals_cb_t = torch.from_numpy(vals_cb_np).to(DEVICE)
    seq_idx_t = torch.from_numpy(seq_keys_np).to(DEVICE)

    rng_p = np.random.RandomState(seed + 1000)
    P_kc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
    P_vc_np = (rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)
    P_kc = torch.from_numpy(P_kc_np).to(DEVICE)
    P_vc = torch.from_numpy(P_vc_np).to(DEVICE)

    arms: List[Dict] = []
    a = run_arm_no_replay(seed, M, seq_len, keys_cb_t, vals_cb_t, seq_idx_t,
                          P_kc, P_vc, sigma_query, k_active)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    for n_replay in n_replay_values:
        if n_replay == 0:
            continue
        a = run_arm_iterative_replay(seed, M, seq_len, n_replay,
                                     keys_cb_t, vals_cb_t, seq_idx_t,
                                     P_kc, P_vc, sigma_query, k_active)
        arms.append(a)
        print(f"  [seed={seed} {a['arm_name']:>18s} n_replay={n_replay:>3d}] "
              f"recall={a['recall_cortex']:.3f} hash={a['arm_hash']} "
              f"wall={a['wall_s']:.1f}s", flush=True)
        _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    a = run_arm_direct_upper(seed, M, seq_len, keys_cb_t, vals_cb_t, seq_idx_t,
                             P_kc, P_vc, sigma_query, k_active)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    elapsed = time.time() - t0
    return {
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "sigma_query": float(sigma_query),
        "k_active": int(k_active),
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


# -- v3.2 verdict logic -------------------------------------------------------

def compute_seed_verdict(seed_result: Dict) -> Tuple[str, str]:
    """v3.2 verdict bands (retuned for sparse-burst regime):

    HARD_PASS: NO_REPLAY <= 0.50 AND R(N_REPLAY_20) - R(NO_REPLAY) >= 0.20
               AND monotonic AND not BC-ceiling
    MIDDLE_BAND: lift_20_vs_no in [0.10, 0.20)
    HARD_FAIL: no lift / replay HURTS / BC-ceiling / cardinality / AF violation
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

    # META_RULE_AF
    hashes = [a["arm_hash"] for a in arms]
    if len(set(hashes)) < len(hashes):
        dupes = [h for h in hashes if hashes.count(h) > 1]
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: arm-hash duplicates {set(dupes)}")

    lift_20_vs_no = R_20 - R_NO
    lift_20_vs_1 = R_20 - R_1
    monotonic = (R_NO <= R_1 + 1e-6) and (R_1 <= R_5 + 1e-6) and (R_5 <= R_20 + 1e-6)
    bc_ceiling = (R_20 >= R_DIRECT - BC_CEILING_MARGIN) and \
                 (R_NO >= R_DIRECT - BC_CEILING_MARGIN)

    summary = (
        f"M={seed_result['M']} seq_len={seed_result['seq_len']} "
        f"sigma_query={seed_result['sigma_query']:.2f} "
        f"k_active={seed_result['k_active']} seed={seed_result['seed']} "
        f"NO_REPLAY={R_NO:.3f} N_REPLAY_1={R_1:.3f} N_REPLAY_5={R_5:.3f} "
        f"N_REPLAY_20={R_20:.3f} DIRECT_UPPER={R_DIRECT:.3f} "
        f"lift_20_vs_no={lift_20_vs_no:+.3f} lift_20_vs_1={lift_20_vs_1:+.3f} "
        f"monotonic={monotonic} bc_ceiling={bc_ceiling}"
    )

    if bc_ceiling:
        return ("HARD_FAIL",
                f"HARD_FAIL (BC_CEILING): NO_REPLAY and N_REPLAY_20 both within "
                f"{BC_CEILING_MARGIN} of DIRECT_UPPER; regime too easy. {summary}")
    if R_20 < R_NO - 0.05 or R_20 < R_1 - 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL (REPLAY_HURTS): iterative replay degrades recall. {summary}")
    if (R_NO <= HARD_PASS_NO_REPLAY_CEILING
        and lift_20_vs_no >= HARD_PASS_LIFT_MIN
        and monotonic):
        return ("HARD_PASS",
                f"HARD_PASS (SWR_V3_2_SPARSE_DG_LIFT): NO_REPLAY={R_NO:.3f} <= "
                f"{HARD_PASS_NO_REPLAY_CEILING} AND lift_20_vs_no={lift_20_vs_no:+.3f} "
                f">= {HARD_PASS_LIFT_MIN} AND monotonic AND not BC-ceiling. {summary}")
    if lift_20_vs_no >= MIDDLE_BAND_LIFT_MIN:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: lift_20_vs_no={lift_20_vs_no:+.3f} in "
                f"[{MIDDLE_BAND_LIFT_MIN}, {HARD_PASS_LIFT_MIN}); partial lift. {summary}")
    return ("HARD_FAIL",
            f"HARD_FAIL (NO_LIFT): lift_20_vs_no={lift_20_vs_no:+.3f} < "
            f"{MIDDLE_BAND_LIFT_MIN}; iterative replay does not consolidate. {summary}")


# -- Self-test ---------------------------------------------------------------

def selftest_core() -> None:
    """Light selftest at TINY config on CPU to verify mechanism RUNS + sparse encode works."""
    global DEVICE
    saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        M_t, seq_t = 64, 8
        sigma_t = 0.5
        # k_active proportional to N_DIM unchanged at selftest
        k_active_t = max(1, int(K_ACTIVE_FRAC * N_CORTEX))

        keys_cb_np, vals_cb_np, seq_idx_np, _ = build_sequence(seed=0, M=M_t, seq_len=seq_t)
        keys_cb_t = torch.from_numpy(keys_cb_np).to(DEVICE)
        vals_cb_t = torch.from_numpy(vals_cb_np).to(DEVICE)
        seq_idx_t = torch.from_numpy(seq_idx_np).to(DEVICE)
        rng_p = np.random.RandomState(1000)
        P_kc = torch.from_numpy((rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)).to(DEVICE)
        P_vc = torch.from_numpy((rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)).to(DEVICE)

        # Sparse encoder sanity: encoded vector has exactly k_active nonzeros
        encoded = encode_keys_sparse(keys_cb_t, P_kc, k_active_t)
        nnz_per_row = (encoded != 0).sum(dim=-1)
        if not bool((nnz_per_row == k_active_t).all().item()):
            raise AssertionError(
                f"sparse_kWTA: rows should have exactly k_active={k_active_t} "
                f"nonzeros; got min={int(nnz_per_row.min())} max={int(nnz_per_row.max())}"
            )

        a_no = run_arm_no_replay(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t,
                                 P_kc, P_vc, sigma_t, k_active_t)
        a_1 = run_arm_iterative_replay(0, M_t, seq_t, 1, keys_cb_t, vals_cb_t,
                                       seq_idx_t, P_kc, P_vc, sigma_t, k_active_t)
        a_d = run_arm_direct_upper(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t,
                                   P_kc, P_vc, sigma_t, k_active_t)

        for a in (a_no, a_1, a_d):
            if a["arm_status"] != "OK":
                raise AssertionError(f"selftest arm error: {a}")
            r = float(a["recall_cortex"])
            if not (0.0 <= r <= 1.0):
                raise AssertionError(f"selftest recall {r} out of [0,1] for {a['arm_name']}")
        hashes = (a_no["arm_hash"], a_1["arm_hash"], a_d["arm_hash"])
        if len(set(hashes)) < 3:
            raise AssertionError(f"selftest META_RULE_AF violation: hashes {hashes}")
        if a_no["arm_hash"] == a_1["arm_hash"]:
            raise AssertionError(
                "selftest META_RULE_AX violation: NO_REPLAY and N_REPLAY_1 "
                "bit-identical (mechanism not firing)"
            )
        print(f"[selftest_core] PASS  M={M_t} seq_len={seq_t} sigma_query={sigma_t} "
              f"k_active={k_active_t} "
              f"NO_REPLAY={a_no['recall_cortex']:.3f} "
              f"N_REPLAY_1={a_1['recall_cortex']:.3f} "
              f"DIRECT_UPPER={a_d['recall_cortex']:.3f}", flush=True)
    finally:
        DEVICE = saved_device


# -- Metrics writers ----------------------------------------------------------

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
    arms = seed_result.get("arms", [])
    per_arm_rows = []
    for a in arms:
        per_arm_rows.append({
            "arm_name": a["arm_name"],
            "n_replay": a.get("n_replay"),
            "sigma_query": a.get("sigma_query"),
            "k_active": a.get("k_active"),
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
                    f"seq_len={seed_result.get('seq_len')} "
                    f"sigma_query={seed_result.get('sigma_query'):.2f} "
                    f"k_active={seed_result.get('k_active')} "
                    f"mode={run_mode} device={DEVICE.type} swr_v3_2_sparse_dg_burst"),
        "elapsed_s": float(elapsed_s),
        "config_version": config_version,
        "seed": seed_result.get("seed"),
        "M": seed_result.get("M"), "seq_len": seed_result.get("seq_len"),
        "sigma_query": seed_result.get("sigma_query"),
        "k_active": seed_result.get("k_active"),
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
