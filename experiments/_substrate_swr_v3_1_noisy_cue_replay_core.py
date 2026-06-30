"""Shared core for substrate_swr_v3_1_noisy_cue_replay (chunked seed cells).

v3.1 = v3 mechanism + NOISY-CUE RETRIEVAL protocol.

Background: v3 (commit 48be1bd7) honest-aborted at smoke with BC_CEILING
across all M / seq_len regimes. Spec-gap finding (cell-author 2026-06-30):
v3 retained clean-cue retrieval (recall queries with the encoded k directly),
which makes iterative cleanup VACUOUS at write time. Sanity probe:
sigma_query=0.0 -> NO_REPLAY=1.000; sigma_query=0.5 -> NO_REPLAY=0.34;
sigma_query=1.5 -> NO_REPLAY=0.02. Noisy-cue retrieval opens the discriminator.

v3.1 change (minimal; Option A per Director 2026-06-30):
  - Recall test injects sigma_query * randn noise on retrieval cue
  - sigma_query = 0.5 (preregistered; expected NO_REPLAY ~0.34)
  - HARD_PASS retuned: NO_REPLAY <= 0.40 AND lift_20_vs_no >= 0.30 AND monotonic
  - MIDDLE_BAND: lift_20_vs_no in [0.10, 0.30)
  - HARD_FAIL: no lift / BC-ceiling / decreasing recall with passes / drop with replay

Mechanism unchanged from v3 (iterative SEQUENCE replay via
hdlab.iterative_attractor.iterative_cleanup at every step on key AND value).

Architecture: CHUNKED single-seed-per-cell. This module is imported by 3
sibling cells (seeds 7 / 13 / 19). Reuses v3 internals where unchanged
(arm runners, hashing, build_sequence, metrics writers); only verdict
bands + recall noise injection differ.

META rules enforced (unchanged from v3):
  AF arms-must-differ SHA-256
  AH atomic tmp + os.replace metrics write
  AX per-n_replay mechanism_hash distinct
  J no bare except; specific exception classes; failure_class field
  AY (proposed today): verdict-emitter auto-demote if encoder_pair_distinctness=False
  AC numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
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


# -- Regime constants (v3.1) --------------------------------------------------

N_DIM = 8192
N_CORTEX = 2048
SEQ_LEN = 100                     # full
SEQ_LEN_SMOKE = 50                # smoke
N_REPLAY_VALUES: Tuple[int, ...] = (0, 1, 5, 20)
N_REPLAY_VALUES_SMOKE: Tuple[int, ...] = (0, 1, 5, 20)

M_VALUES_FULL: Tuple[int, ...] = (4096, 8192, 16384)
M_SMOKE = 4096

# v3.1 NEW: noisy-cue retrieval protocol parameter
SIGMA_QUERY = 0.5                 # HYPOTHESIZED@spec_action_2: NO_REPLAY ~0.34 at this sigma
# Justification: cell-author 2026-06-30 sanity probe:
#   sigma=0.00 NO_REPLAY=1.000 (v3 BC_CEILING)
#   sigma=0.30 NO_REPLAY=0.620
#   sigma=0.50 NO_REPLAY=0.340  <- chosen: room for iterative cleanup to lift
#   sigma=0.80 NO_REPLAY=0.070
#   sigma=1.50 NO_REPLAY=0.020  (too noisy; signal floor)
# 0.50 places NO_REPLAY in the middle band (BC-floor checked at 0.05 + 5% width)

ETA_INITIAL = 0.01
ETA_REPLAY = 0.005
DECAY = 1.0
TEMP_CLEANUP = 4.0
MAX_STEPS_CLEANUP = 6

# Discriminator bands (v3.1 retuned for noisy-cue regime)
HARD_PASS_LIFT_MIN = 0.30        # lift over NO_REPLAY (not over N_REPLAY_1) for v3.1
HARD_PASS_NO_REPLAY_CEILING = 0.40
MIDDLE_BAND_LIFT_MIN = 0.10
BC_CEILING_MARGIN = 0.03          # K=20 must be < DIRECT_UPPER - this for non-BC

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


# -- Utilities (unchanged from v3) -------------------------------------------

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


def _project_to_cortex(x_dim: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
    return _l2_normalize_t(x_dim @ P.t(), dim=-1)


# -- v3.1 KEY CHANGE: noisy-cue recall ---------------------------------------

def _recall_via_W_noisy(keys_c: torch.Tensor, W_cortex: torch.Tensor,
                        vals_cb_t: torch.Tensor, P_vc: torch.Tensor,
                        seq_idx_t: torch.Tensor, seed_for_noise: int,
                        sigma_query: float) -> float:
    """Recall under NOISY-CUE retrieval (v3.1 KEY CHANGE vs v3).

    Inject sigma_query * randn noise on each retrieval cue, then L2-renormalize.
    Without this, single-pass Hebbian write trivially solves recall (v3
    BC_CEILING). With noise, iterative cleanup at write time has a meaningful
    signal-cleaning role: each replay pass effectively re-projects the
    sequence representation toward attractor basins, hardening signal/noise.
    """
    seq_len = keys_c.shape[0]
    # Deterministic noise per (seed_for_noise, cue) for reproducibility
    g = torch.Generator(device=keys_c.device).manual_seed(int(seed_for_noise) + 4242)
    noise = sigma_query * torch.randn(keys_c.shape, generator=g,
                                      dtype=keys_c.dtype, device=keys_c.device)
    noisy_keys = _l2_normalize_t(keys_c + noise, dim=-1)
    preds = noisy_keys @ W_cortex.t()
    preds_n = _l2_normalize_t(preds, dim=-1)
    vals_cb_c = _project_to_cortex(vals_cb_t, P_vc)
    sims = preds_n @ vals_cb_c.t()
    argmax = torch.argmax(sims, dim=1)
    n_hits = int((argmax == seq_idx_t).sum().item())
    return n_hits / float(seq_len)


# -- Arm runners (v3.1: pass sigma_query to recall) ---------------------------

def run_arm_no_replay(seed: int, M: int, seq_len: int,
                      keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                      seq_idx_t: torch.Tensor,
                      P_kc: torch.Tensor, P_vc: torch.Tensor,
                      sigma_query: float) -> Dict:
    """NO_REPLAY baseline: single Hebbian write pass + noisy-cue recall."""
    t0 = time.time()
    arm_name = ARM_NO_REPLAY
    try:
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + ETA_INITIAL * (vals_c.t() @ keys_c)
        recall = _recall_via_W_noisy(keys_c, W_cortex, vals_cb_t, P_vc,
                                     seq_idx_t, seed, sigma_query)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": 0,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, 0, seed, M, seq_len, sigma_query, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_iterative_replay(seed: int, M: int, seq_len: int, n_replay: int,
                             keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                             seq_idx_t: torch.Tensor,
                             P_kc: torch.Tensor, P_vc: torch.Tensor,
                             sigma_query: float) -> Dict:
    """SWR v3 iterative SEQUENCE replay + noisy-cue retrieval (the mechanism)."""
    t0 = time.time()
    arm_name = n_replay_arm_name(n_replay)
    try:
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)
        keys_cb_c = _project_to_cortex(keys_cb_t, P_kc)
        vals_cb_c = _project_to_cortex(vals_cb_t, P_vc)
        keys_cb_c_np = keys_cb_c.detach().cpu().numpy().astype(np.float32)
        vals_cb_c_np = vals_cb_c.detach().cpu().numpy().astype(np.float32)

        # Initial write
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + ETA_INITIAL * (vals_c.t() @ keys_c)

        # Iterative replay passes (mechanism unchanged from v3)
        for pass_idx in range(n_replay):
            for i in range(seq_len):
                k_noisy = keys_c[i]
                k_clean_np = iterative_cleanup(
                    k_noisy.detach().cpu().numpy().astype(np.float32),
                    keys_cb_c_np,
                    temp=TEMP_CLEANUP, max_steps=MAX_STEPS_CLEANUP, tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                k_clean = torch.from_numpy(k_clean_np).to(DEVICE)
                v_predicted = W_cortex @ k_clean
                v_clean_np = iterative_cleanup(
                    v_predicted.detach().cpu().numpy().astype(np.float32),
                    vals_cb_c_np,
                    temp=TEMP_CLEANUP, max_steps=MAX_STEPS_CLEANUP, tol=1e-3,
                    scale_by_sqrt_d=True,
                )["state"]
                v_clean = torch.from_numpy(v_clean_np).to(DEVICE)
                W_cortex = DECAY * W_cortex + ETA_REPLAY * torch.outer(v_clean, k_clean)

        recall = _recall_via_W_noisy(keys_c, W_cortex, vals_cb_t, P_vc,
                                     seq_idx_t, seed, sigma_query)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": int(n_replay),
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, n_replay, seed, M, seq_len, sigma_query, t0,
                               "VALUE_TYPE", repr(exc))


def run_arm_direct_upper(seed: int, M: int, seq_len: int,
                         keys_cb_t: torch.Tensor, vals_cb_t: torch.Tensor,
                         seq_idx_t: torch.Tensor,
                         P_kc: torch.Tensor, P_vc: torch.Tensor,
                         sigma_query: float) -> Dict:
    """DIRECT_UPPER oracle ceiling under NOISY-CUE recall.

    NB: even DIRECT_UPPER is sigma_query-limited; oracle ceiling is what
    a perfect linear-system write CAN do under retrieval noise.
    """
    t0 = time.time()
    arm_name = ARM_DIRECT_UPPER
    try:
        keys_c = _project_to_cortex(keys_cb_t[seq_idx_t], P_kc)
        vals_c = _project_to_cortex(vals_cb_t[seq_idx_t], P_vc)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=DTYPE, device=DEVICE)
        W_cortex = W_cortex + (10.0 * ETA_INITIAL) * (vals_c.t() @ keys_c)
        recall = _recall_via_W_noisy(keys_c, W_cortex, vals_cb_t, P_vc,
                                     seq_idx_t, seed, sigma_query)
        arm_hash = _arm_state_hash(arm_name, W_cortex, recall)
        del W_cortex
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "arm_name": arm_name, "n_replay": -1,
            "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
            "sigma_query": float(sigma_query),
            "recall_cortex": float(recall),
            "arm_hash": arm_hash, "arm_status": "OK",
            "wall_s": float(time.time() - t0),
            "failure_class": None,
        }
    except torch.cuda.OutOfMemoryError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, t0,
                               "CUDA_OOM", repr(exc))
    except RuntimeError as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, t0,
                               "TORCH_RUNTIME", repr(exc))
    except (ValueError, TypeError) as exc:
        return _arm_error_dict(arm_name, -1, seed, M, seq_len, sigma_query, t0,
                               "VALUE_TYPE", repr(exc))


def _arm_error_dict(arm_name: str, n_replay: int, seed: int, M: int,
                    seq_len: int, sigma_query: float, t0: float,
                    failure_class: str, exc_repr: str) -> Dict:
    return {
        "arm_name": arm_name, "n_replay": int(n_replay),
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "sigma_query": float(sigma_query),
        "recall_cortex": float("nan"),
        "arm_hash": "ERROR", "arm_status": f"ERROR: {failure_class}: {exc_repr[:200]}",
        "wall_s": float(time.time() - t0),
        "failure_class": failure_class,
    }


# -- Per-seed sweep -----------------------------------------------------------

def run_seed(seed: int, M: int, seq_len: int,
             n_replay_values: Tuple[int, ...],
             sigma_query: float,
             out_dir: Path) -> Dict:
    """Run all 5 arms for ONE seed at ONE M setting under sigma_query noisy-cue."""
    t0 = time.time()
    print(f"  [seed={seed}] M={M} seq_len={seq_len} sigma_query={sigma_query} "
          f"n_replay_values={n_replay_values} dev={DEVICE.type}", flush=True)

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
                          P_kc, P_vc, sigma_query)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    for n_replay in n_replay_values:
        if n_replay == 0:
            continue
        a = run_arm_iterative_replay(seed, M, seq_len, n_replay,
                                     keys_cb_t, vals_cb_t, seq_idx_t,
                                     P_kc, P_vc, sigma_query)
        arms.append(a)
        print(f"  [seed={seed} {a['arm_name']:>18s} n_replay={n_replay:>3d}] "
              f"recall={a['recall_cortex']:.3f} hash={a['arm_hash']} "
              f"wall={a['wall_s']:.1f}s", flush=True)
        _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    a = run_arm_direct_upper(seed, M, seq_len, keys_cb_t, vals_cb_t, seq_idx_t,
                             P_kc, P_vc, sigma_query)
    arms.append(a)
    print(f"  [seed={seed} {a['arm_name']:>18s}] recall={a['recall_cortex']:.3f} "
          f"hash={a['arm_hash']} wall={a['wall_s']:.1f}s", flush=True)
    _heartbeat_tick(out_dir, len(arms), len(n_replay_values) + 2, time.time() - t0, a)

    elapsed = time.time() - t0
    return {
        "seed": int(seed), "M": int(M), "seq_len": int(seq_len),
        "sigma_query": float(sigma_query),
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


# -- v3.1 verdict logic -------------------------------------------------------

def compute_seed_verdict(seed_result: Dict) -> Tuple[str, str]:
    """v3.1 verdict bands (retuned for noisy-cue regime):

    HARD_PASS: NO_REPLAY <= 0.40 AND R(N_REPLAY_20) - R(NO_REPLAY) >= 0.30
               AND monotonic AND not BC-ceiling
    MIDDLE_BAND: lift_20_vs_no in [0.10, 0.30)
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
    # Monotonic NON-DECREASING through 0->1->5->20
    monotonic = (R_NO <= R_1 + 1e-6) and (R_1 <= R_5 + 1e-6) and (R_5 <= R_20 + 1e-6)
    bc_ceiling = (R_20 >= R_DIRECT - BC_CEILING_MARGIN) and \
                 (R_NO >= R_DIRECT - BC_CEILING_MARGIN)

    summary = (
        f"M={seed_result['M']} seq_len={seed_result['seq_len']} "
        f"sigma_query={seed_result['sigma_query']:.2f} seed={seed_result['seed']} "
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
                f"HARD_PASS (SWR_V3_1_NOISY_CUE_LIFT): NO_REPLAY={R_NO:.3f} <= "
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
    """Light selftest at TINY config on CPU to verify mechanism RUNS."""
    global DEVICE
    saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        M_t, seq_t = 64, 8
        sigma_t = 0.5
        keys_cb_np, vals_cb_np, seq_idx_np, _ = build_sequence(seed=0, M=M_t, seq_len=seq_t)
        keys_cb_t = torch.from_numpy(keys_cb_np).to(DEVICE)
        vals_cb_t = torch.from_numpy(vals_cb_np).to(DEVICE)
        seq_idx_t = torch.from_numpy(seq_idx_np).to(DEVICE)
        rng_p = np.random.RandomState(1000)
        P_kc = torch.from_numpy((rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)).to(DEVICE)
        P_vc = torch.from_numpy((rng_p.randn(N_CORTEX, N_DIM) / np.sqrt(N_DIM)).astype(np.float32)).to(DEVICE)

        a_no = run_arm_no_replay(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t,
                                 P_kc, P_vc, sigma_t)
        a_1 = run_arm_iterative_replay(0, M_t, seq_t, 1, keys_cb_t, vals_cb_t,
                                       seq_idx_t, P_kc, P_vc, sigma_t)
        a_d = run_arm_direct_upper(0, M_t, seq_t, keys_cb_t, vals_cb_t, seq_idx_t,
                                   P_kc, P_vc, sigma_t)

        for a in (a_no, a_1, a_d):
            if a["arm_status"] != "OK":
                raise AssertionError(f"selftest arm error: {a}")
            r = float(a["recall_cortex"])
            if not (0.0 <= r <= 1.0):
                raise AssertionError(f"selftest recall {r} out of [0,1] for {a['arm_name']}")
        if not (a_d["recall_cortex"] >= a_no["recall_cortex"] - 0.05):
            raise AssertionError(
                f"selftest DIRECT_UPPER ({a_d['recall_cortex']}) not >= "
                f"NO_REPLAY ({a_no['recall_cortex']}) - 0.05"
            )
        hashes = (a_no["arm_hash"], a_1["arm_hash"], a_d["arm_hash"])
        if len(set(hashes)) < 3:
            raise AssertionError(f"selftest META_RULE_AF violation: hashes {hashes}")
        if a_no["arm_hash"] == a_1["arm_hash"]:
            raise AssertionError(
                "selftest META_RULE_AX violation: NO_REPLAY and N_REPLAY_1 "
                "bit-identical (mechanism not firing)"
            )
        print(f"[selftest_core] PASS  M={M_t} seq_len={seq_t} sigma_query={sigma_t} "
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
                    f"mode={run_mode} device={DEVICE.type} swr_v3_1_noisy_cue_replay"),
        "elapsed_s": float(elapsed_s),
        "config_version": config_version,
        "seed": seed_result.get("seed"),
        "M": seed_result.get("M"), "seq_len": seed_result.get("seq_len"),
        "sigma_query": seed_result.get("sigma_query"),
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
