"""substrate_multihop_brain_pushback_composition_v2_hardened -- silent-death-proof rerun.

V2 HARDENING DELTA over v1 (commit e1614b4f):
  Mechanism is IDENTICAL to v1. Only operational hardening added so a silent
  death (process killed before any output written) becomes IMPOSSIBLE.

V1 outcome (Cycle 1 dispatch): output dir never created; no metrics.json; no
stderr/stdout captured. Could not distinguish module-import crash vs OOM-kill
vs runner-launch failure. Re-author per Orchestrator recommendation.

HARDENING (4 layers):

  L1 EARLY-WRITE on main entry:
      Output dir created + metrics.json written BEFORE any compute begins, with
      verdict=UNKNOWN, verdict_msg=STARTED, pid + ts recorded. Silent death after
      this point is now visible (file exists; verdict tells you we got past
      module init).

  L2 PER-ARM PROGRESS metrics.json updates:
      After EACH arm-depth-seed completes, metrics.json is rewritten with
      verdict=UNKNOWN, verdict_msg=PROGRESS, partial per_seed, completed_units
      count. So even mid-run death exposes how far we got. Final write only
      after verdict computation.

  L3 OUTER try/except around entire main:
      Catches ALL exceptions; writes a metrics.json with verdict=UNKNOWN,
      verdict_msg=CRASHED:<exception_class>:<message>, full traceback under
      _exception_traceback field, then re-raises. META_RULE_J held
      (record-and-halt; no silent swallow).

  L4 EARLY STDERR FLUSH on module-import errors:
      The selftest at module level can crash before main; wrap in try/except
      that writes a sentinel to a fixed path (data/exp_<anchor>/import_crash.json)
      so even import-time failure is visible.

ALL FIVE ARM FUNCTIONS, BAND THRESHOLDS, VERDICT LOGIC, PRE-REG ARE IDENTICAL
TO V1. Search this file for marker "V1_MECHANISM_IDENTICAL" to confirm.

LOAD-BEARING TEST per drill notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md
Tests whether META_BARRIER_1 (substrate-multi-hop permanent 2-hop cap) was
prematurely declared. USER push-back 2026-06-27: "i do not accept those
limitations. how does the brain do it" — explicit rejection of substrate-product
permanent 2-hop framing.

ARMS (5):
  ARM_BASELINE                       per-hop cleanup; depth-5 SANITY RAIL 0.145 +/- 0.02
  ARM_R1_REPLAY_INTO_W_C             NREM replay as OPERATOR; SEPARATE W_C
  ARM_R2_PFC_SCRATCHPAD              dedicated W_PFC scratchpad
  ARM_R3_BIDIRECTIONAL               HRR-involutive bidirectional meet-in-middle
  ARM_COMBINED_R1_R2_R3              all three stacked

PRE-REG BANDS (V1_MECHANISM_IDENTICAL; HARD-LOCKED at module init; PROSPECTIVE):
  HARD_PASS_BARRIER_BROKEN:
    ARM_COMBINED depth-5 mean >= 0.65
    AND ARM_COMBINED depth-5 > MAX(R1, R2, R3) + 0.001
    AND ARM_COMBINED depth-5 > ARM_BASELINE + 0.45
    AND cv across seeds <= 0.08
    AND ARM_BASELINE depth-5 in [0.10, 0.20] on majority of seeds
  HARD_PASS_INDIVIDUAL_WINS:
    Any individual R1/R2/R3 depth-5 mean >= 0.50 AND > BASELINE + 0.30 AND cv <= 0.08
  MIDDLE_BAND:
    ARM_COMBINED depth-5 in [0.45, 0.65)
    OR any individual R-arm depth-5 in [0.30, 0.50)
  HARD_FAIL:
    ARM_COMBINED depth-5 < 0.25
    OR ARM_COMBINED within 0.05 of ARM_BASELINE
  RAIL_SANITY_BREACH:
    ARM_BASELINE depth-5 mean outside [0.10, 0.20] on majority of seeds

CARDINALITY (META_RULE_H mandatory):
  EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 4 depths = 60 arm-depth-seed entries
  EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed * 2 depths = 10 entries

CONFIG (V1_MECHANISM_IDENTICAL):
  Full: N=8192, V_C=200, n_chains_train=200, depths=[2, 3, 5, 8], seeds=[7, 17, 23]
  Smoke: N=8192, V_C=200, n_chains=50, depths=[2, 5], seed=[7]

META_RULE_J: no silent except blocks; record+halt or re-raise.

Author: exp_dev 2026-06-27 (v2 hardening).
ASCII-only; per-seed checkpoint; substrate-only.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_multihop_brain_pushback_composition_v2_hardened"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE HARD bands (LOCKED at module init; V1_MECHANISM_IDENTICAL)
HP_BARRIER_BROKEN_COMBINED = 0.65
HP_COMBINED_LIFT_OVER_BASELINE = 0.45
HP_INDIVIDUAL_WIN = 0.50
HP_INDIVIDUAL_LIFT_OVER_BASELINE = 0.30
HP_COMPOSITION_MARGIN = 0.001
HP_CV_MAX = 0.08
MB_COMBINED_LO = 0.45
MB_INDIVIDUAL_LO = 0.30
HF_PIVOT_THRESHOLD = 0.25
HF_COMBINED_VS_BASELINE_FLAT = 0.05

BASELINE_SANITY_DEPTH = 5
BASELINE_SANITY_LO = 0.10
BASELINE_SANITY_HI = 0.20
BASELINE_SANITY_EXPECTED = 0.145

EXPECTED_ARMS = ["baseline", "r1_replay_into_w_c", "r2_pfc_scratchpad",
                 "r3_bidirectional", "combined_r1_r2_r3"]

if RUN_MODE == "smoke":
    N_DIM = 8192
    V_CONCEPTS = 200
    N_PREDICATES = 10
    SEEDS = [7]
    N_CHAINS_TRAIN = 50
    N_CHAINS_TEST = 50
    HOP_DEPTHS = [2, 5]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    N_PREDICATES = 10
    SEEDS = [7, 17, 23]
    N_CHAINS_TRAIN = 200
    N_CHAINS_TEST = 200
    HOP_DEPTHS = [2, 3, 5, 8]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

# R1 NREM replay tuning (V1_MECHANISM_IDENTICAL)
R1_REPLAY_TOP_K = 30
R1_REPLAY_COHORTS = 5
R1_REPLAY_MIN_AMPLITUDE = 0.55

# R3 bidirectional tuning (V1_MECHANISM_IDENTICAL)
R3_MEET_COSINE_TAU = 0.30

CONFIG_VERSION = (
    "brainPushbackComp-v2-hardened: N=%d V_C=%d V_P=%d N_chains_train=%d N_chains_test=%d "
    "seeds=%s depths=%s mode=%s "
    "R1_top_K=%d R1_cohorts=%d R1_min_amp=%.2f R3_tau=%.2f "
    "HP_combined>=%.2f HP_indiv>=%.2f HP_cv<=%.3f "
    "MB_combined_lo=%.2f MB_indiv_lo=%.2f HF_pivot=%.2f "
    "baseline_rail=[%.2f,%.2f] expected_arms=%d expected_n_units=%d "
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    N_DIM, V_CONCEPTS, N_PREDICATES, N_CHAINS_TRAIN, N_CHAINS_TEST,
    SEEDS, HOP_DEPTHS, RUN_MODE,
    R1_REPLAY_TOP_K, R1_REPLAY_COHORTS, R1_REPLAY_MIN_AMPLITUDE, R3_MEET_COSINE_TAU,
    HP_BARRIER_BROKEN_COMBINED, HP_INDIVIDUAL_WIN, HP_CV_MAX,
    MB_COMBINED_LO, MB_INDIVIDUAL_LO, HF_PIVOT_THRESHOLD,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI, len(EXPECTED_ARMS), EXPECTED_N_UNITS,
)


# ---------------------------- L4: early visibility helper ----------------------------

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    """L1/L2 helper: write a minimal valid metrics.json IMMEDIATELY.

    Has all REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary).
    Safe to call repeatedly; overwrites.
    """
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
            "_hardening_marker": "v2_hardened",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        # Last-ditch: if even writing metrics fails, print to stderr.
        # META_RULE_J: do NOT silent swallow; print + continue (re-raise would
        # mask the original exception in the outer handler).
        print("[_write_minimal_metrics] FAIL writing minimal metrics: %s" % e,
              file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    """L4: module-import crash visibility. Write fixed-path sentinel."""
    try:
        # Best-effort guess of output dir name (HDLAB_EXP_NAME or anchor)
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
            "_hardening_marker": "v2_hardened_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# ---------------------------- primitives (V1_MECHANISM_IDENTICAL) ----------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +-1 vectors, L2-normalized. Shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    """Hebbian outer-product binding. Returns W of shape (n_dim, n_dim)."""
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                     g: np.random.Generator, disallow_s: set
                     ) -> Tuple[List[Tuple[int, int, int]],
                                List[List[Tuple[int, int, int]]]]:
    """Build n_chains chains of max_depth hops with random predicates."""
    all_triples: List[Tuple[int, int, int]] = []
    chain_queries: List[List[Tuple[int, int, int]]] = []
    used_s = set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes: List[int] = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain: List[Tuple[int, int, int]] = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


def _retrieve_1hop(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                   s_vec: np.ndarray, p: int, sq: float) -> int:
    """Per-hop retrieval; argmax cleanup. s_vec is the (clean) source vector."""
    key = (s_vec * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


# ---------------------------- ARM_BASELINE (V1_MECHANISM_IDENTICAL) ----------------------------

def arm_baseline(E, R, sq, W_main, chains_test, depth: int) -> Dict[str, Any]:
    """Pointer-chain per-hop cleanup; intermediates feed into main W."""
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W_main, R, E[s], p, sq)
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(float(x) / max(n, 1), 4) for x in per_step_hits],
        "n_queries": n,
        "depth": depth,
        "mechanism": "baseline_per_hop_cleanup",
    }


# ---------------------------- ARM_R1: REPLAY into W_C (V1_MECHANISM_IDENTICAL) ----------------------------

def build_W_C_replay_shortcuts(E, R, sq, W_H, chains_train, n_dim: int,
                               top_K: int, cohorts: int, min_amp: float
                               ) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Replay-as-OPERATOR: extract A -> C 2-hop shortcuts; write into SEPARATE W_C."""
    shortcut_triples: List[Tuple[int, int, int]] = []
    amps_recorded: List[float] = []
    n_chains = len(chains_train)
    if n_chains == 0:
        return np.zeros((n_dim, n_dim), dtype=np.float32), {
            "n_chains_replayed": 0, "n_shortcuts": 0, "mean_amp": 0.0,
            "cohorts": cohorts, "min_amp": min_amp,
        }
    amps: List[Tuple[float, int, int]] = []
    for ci, chain in enumerate(chains_train):
        if len(chain) < 2:
            continue
        a = chain[0][0]
        b = chain[0][2]
        p1 = chain[0][1]
        c = chain[1][2]
        p2 = chain[1][1]
        key1 = (E[a] * R[p1] * sq).astype(np.float32)
        state_b = W_H @ key1
        b_pred = int((E @ state_b).argmax())
        key2 = (E[b_pred] * R[p2] * sq).astype(np.float32)
        state_c = W_H @ key2
        norm_state = float(np.linalg.norm(state_c) + 1e-8)
        amp = float(E[c] @ state_c) / norm_state
        amps.append((amp, ci, c))

    amps_sorted = sorted(amps, key=lambda x: -x[0])
    cohort_size = max(1, len(amps_sorted) // max(cohorts, 1))
    seen_shortcut_pairs: set = set()
    for ck in range(cohorts):
        cohort_slice = amps_sorted[ck * cohort_size:(ck + 1) * cohort_size]
        for amp, ci, c in cohort_slice[:top_K]:
            if amp < min_amp:
                continue
            a = chains_train[ci][0][0]
            if (a, c) in seen_shortcut_pairs:
                continue
            seen_shortcut_pairs.add((a, c))
            shortcut_triples.append((a, 0, c))
            amps_recorded.append(amp)

    W_C = ingest_hebbian(shortcut_triples, E, R, sq, n_dim)
    stats = {
        "n_chains_replayed": len(amps),
        "n_shortcuts": len(shortcut_triples),
        "mean_amp": float(np.mean(amps_recorded)) if amps_recorded else 0.0,
        "max_amp": float(np.max(amps_recorded)) if amps_recorded else 0.0,
        "min_amp_seen": float(np.min(amps_recorded)) if amps_recorded else 0.0,
        "cohorts": cohorts, "min_amp": min_amp, "top_K": top_K,
    }
    return W_C, stats


def arm_r1_replay_into_w_c(E, R, sq, W_H, W_C, chains_test, depth: int) -> Dict[str, Any]:
    """R1: Query W_C first; fall back to per-hop W_H chain on miss."""
    n = len(chains_test)
    hits = 0
    shortcut_attempts = 0
    shortcut_hits = 0
    fallback_used = 0
    for chain in chains_test:
        s_start = chain[0][0]
        c_true = chain[depth - 1][2]
        shortcut_attempts += 1
        s_pred_shortcut = _retrieve_1hop(E, W_C, R, E[s_start], 0, sq)
        if s_pred_shortcut == c_true:
            shortcut_hits += 1
            hits += 1
            continue
        fallback_used += 1
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s_pred = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            s = s_pred
        if s == c_true:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "shortcut_attempts": shortcut_attempts,
        "shortcut_hits": shortcut_hits,
        "shortcut_hit_rate": round(shortcut_hits / max(shortcut_attempts, 1), 4),
        "fallback_used": fallback_used,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r1_replay_into_w_c",
    }


# ---------------------------- ARM_R2: PFC scratchpad (V1_MECHANISM_IDENTICAL) ----------------------------

def arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains_test, depth: int,
                          n_dim: int) -> Dict[str, Any]:
    """R2: dedicated W_PFC scratchpad holds clean intermediates."""
    n = len(chains_test)
    hits = 0
    pfc_writes = 0
    pfc_reads = 0
    for chain in chains_test:
        W_PFC = W_PFC_init.copy()
        s_start = chain[0][0]
        slot_key_0 = (E[0] * R[0] * sq).astype(np.float32)
        W_PFC = W_PFC + (E[s_start].reshape(-1, 1) @ slot_key_0.reshape(1, -1)) / n_dim
        pfc_writes += 1
        s_clean_idx = s_start
        for i in range(depth):
            p = chain[i][1]
            pfc_reads += 1
            s_pred = _retrieve_1hop(E, W_H, R, E[s_clean_idx], p, sq)
            slot_idx = (i + 1) % V_CONCEPTS
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC = W_PFC + (E[s_pred].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            pfc_writes += 1
            s_clean_idx = s_pred
        if s_clean_idx == chain[depth - 1][2]:
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "pfc_writes": pfc_writes,
        "pfc_reads": pfc_reads,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r2_pfc_scratchpad",
    }


# ---------------------------- ARM_R3: BIDIRECTIONAL (V1_MECHANISM_IDENTICAL) ----------------------------

def _bind_inverse(R: np.ndarray, p: int) -> np.ndarray:
    """Bipolar inverse: bipolar self-inverse."""
    return R[p]


def arm_r3_bidirectional(E, R, sq, W_H, chains_test, depth: int,
                         meet_tau: float) -> Dict[str, Any]:
    """R3: forward + backward walks; commit on meet."""
    n = len(chains_test)
    hits = 0
    meets = 0
    fwd_only_hits = 0
    bwd_only_hits = 0
    sum_meet_step = 0.0
    for chain in chains_test:
        s_start = chain[0][0]
        s_goal = chain[depth - 1][2]
        fwd_states_idx: List[int] = [s_start]
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            fwd_states_idx.append(s)
        fwd_final = fwd_states_idx[depth]

        bwd_states_idx: List[int] = [s_goal]
        b = s_goal
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            inv_p = _bind_inverse(R, p)
            key = (E[b] * inv_p * sq).astype(np.float32)
            scores = E @ (W_H.T @ key)
            b = int(scores.argmax())
            bwd_states_idx.append(b)
        bwd_final = bwd_states_idx[depth]

        meet_found = False
        meet_step = -1
        for k in range(depth + 1):
            f_idx = fwd_states_idx[k]
            b_idx = bwd_states_idx[depth - k]
            if f_idx == b_idx:
                meet_found = True
                meet_step = k
                break
            cos = float(E[f_idx] @ E[b_idx])
            if cos >= meet_tau and k != 0 and k != depth:
                meet_found = True
                meet_step = k
                break
        if meet_found:
            meets += 1
            sum_meet_step += meet_step
            if fwd_final == s_goal or bwd_final == s_start:
                hits += 1
        else:
            if fwd_final == s_goal:
                hits += 1
        if fwd_final == s_goal:
            fwd_only_hits += 1
        if bwd_final == s_start:
            bwd_only_hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "meet_rate": round(meets / max(n, 1), 4),
        "fwd_only_top1": round(fwd_only_hits / max(n, 1), 4),
        "bwd_only_top1": round(bwd_only_hits / max(n, 1), 4),
        "mean_meet_step": round(sum_meet_step / max(meets, 1), 2) if meets > 0 else None,
        "n_queries": n,
        "depth": depth,
        "mechanism": "r3_bidirectional_meet_in_middle",
    }


# ---------------------------- ARM_COMBINED (V1_MECHANISM_IDENTICAL) ----------------------------

def arm_combined(E, R, sq, W_H, W_C, chains_test, depth: int, n_dim: int,
                 meet_tau: float) -> Dict[str, Any]:
    """R1+R2+R3 stacked."""
    n = len(chains_test)
    hits = 0
    shortcut_hits = 0
    meet_hits = 0
    fallback_fwd_hits = 0
    for chain in chains_test:
        s_start = chain[0][0]
        c_true = chain[depth - 1][2]
        s_pred_short = _retrieve_1hop(E, W_C, R, E[s_start], 0, sq)
        if s_pred_short == c_true:
            shortcut_hits += 1
            hits += 1
            continue
        W_PFC_fwd = np.zeros((n_dim, n_dim), dtype=np.float32)
        W_PFC_bwd = np.zeros((n_dim, n_dim), dtype=np.float32)
        fwd_idx_list: List[int] = [s_start]
        s = s_start
        for i in range(depth):
            p = chain[i][1]
            s = _retrieve_1hop(E, W_H, R, E[s], p, sq)
            slot_idx = (i + 1) % V_CONCEPTS
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC_fwd = W_PFC_fwd + (E[s].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            fwd_idx_list.append(s)
        fwd_final = fwd_idx_list[depth]

        bwd_idx_list: List[int] = [c_true]
        b = c_true
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            inv_p = _bind_inverse(R, p)
            key = (E[b] * inv_p * sq).astype(np.float32)
            scores = E @ (W_H.T @ key)
            b = int(scores.argmax())
            slot_idx = (i + 1) % V_CONCEPTS
            slot_key = (E[slot_idx] * R[0] * sq).astype(np.float32)
            W_PFC_bwd = W_PFC_bwd + (E[b].reshape(-1, 1) @ slot_key.reshape(1, -1)) / n_dim
            bwd_idx_list.append(b)
        bwd_final = bwd_idx_list[depth]

        meet_found = False
        for k in range(depth + 1):
            f_idx = fwd_idx_list[k]
            b_idx = bwd_idx_list[depth - k]
            if f_idx == b_idx:
                meet_found = True
                break
            cos = float(E[f_idx] @ E[b_idx])
            if cos >= meet_tau and k != 0 and k != depth:
                meet_found = True
                break

        if meet_found and (fwd_final == c_true or bwd_final == s_start):
            meet_hits += 1
            hits += 1
        elif fwd_final == c_true:
            fallback_fwd_hits += 1
            hits += 1
    return {
        "top1": round(hits / max(n, 1), 4),
        "shortcut_hits": shortcut_hits,
        "meet_hits": meet_hits,
        "fallback_fwd_hits": fallback_fwd_hits,
        "n_queries": n,
        "depth": depth,
        "mechanism": "combined_r1_r2_r3",
    }


# ---------------------------- selftest (V1_MECHANISM_IDENTICAL) ----------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    triples, chains = make_deep_chains(8, V, P, max_depth=3, g=g, disallow_s=set())
    W_H = ingest_hebbian(triples, E, R, sq, n)
    assert W_H.shape == (n, n), "W_H shape mismatch"

    r_base = arm_baseline(E, R, sq, W_H, chains[:8], depth=2)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert len(r_base["per_step_acc"]) == 2

    W_H_before_replay = W_H.copy()
    W_C, r1_stats = build_W_C_replay_shortcuts(E, R, sq, W_H, chains[:8], n,
                                                top_K=5, cohorts=2,
                                                min_amp=0.0)
    assert W_C.shape == (n, n), "W_C shape mismatch"
    assert np.array_equal(W_H, W_H_before_replay), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: replay mutated W_H (must be SEPARATE)"
    r_r1 = arm_r1_replay_into_w_c(E, R, sq, W_H, W_C, chains[:8], depth=2)
    assert 0.0 <= r_r1["top1"] <= 1.0
    assert r_r1["shortcut_attempts"] == 8

    W_H_before_r2 = W_H.copy()
    W_PFC_init = np.zeros((n, n), dtype=np.float32)
    r_r2 = arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains[:8], depth=2, n_dim=n)
    assert 0.0 <= r_r2["top1"] <= 1.0
    assert np.array_equal(W_H, W_H_before_r2), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: R2 mutated W_H (must be SEPARATE)"

    p = 0
    selfinv = R[p] * R[p]
    expected = 1.0 / n
    assert np.allclose(selfinv, expected, atol=1e-4), \
        ("BRAIN_MECHANISM_VS_CARICATURE FAIL: L2-normalized bipolar R[p] not "
         "uniform-self-inverse; got mean=%.6f var=%.6e expected=%.6f"
         % (float(selfinv.mean()), float(selfinv.var()), expected))
    r_r3 = arm_r3_bidirectional(E, R, sq, W_H, chains[:8], depth=2,
                                 meet_tau=0.30)
    assert 0.0 <= r_r3["top1"] <= 1.0
    assert 0.0 <= r_r3["meet_rate"] <= 1.0

    W_H_before_comb = W_H.copy()
    r_comb = arm_combined(E, R, sq, W_H, W_C, chains[:8], depth=2, n_dim=n,
                          meet_tau=0.30)
    assert 0.0 <= r_comb["top1"] <= 1.0
    assert np.array_equal(W_H, W_H_before_comb), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: COMBINED mutated W_H"

    print(
        "[selftest] PASS baseline=%.3f r1=%.3f r2=%.3f r3=%.3f combined=%.3f "
        "(meet_rate=%.3f shortcut_hits=%d/%d)"
        % (r_base["top1"], r_r1["top1"], r_r2["top1"], r_r3["top1"], r_comb["top1"],
           r_r3["meet_rate"], r_r1["shortcut_hits"], r_r1["shortcut_attempts"]),
        flush=True,
    )


# ---------------------------- holder + atexit ----------------------------

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        # Only synthesize if metrics.json missing or still in PROGRESS/STARTED state
        existing = od / "metrics.json"
        if existing.exists():
            try:
                cur = json.loads(existing.read_text(encoding="utf-8"))
                v_cur = cur.get("verdict", "")
                # If verdict is a final value (HARD_PASS/HARD_FAIL/MIDDLE_BAND/RAIL_SANITY_BREACH),
                # don't overwrite. If UNKNOWN (STARTED/PROGRESS/CRASHED), DO synth.
                if v_cur and not v_cur.startswith("UNKNOWN") and v_cur != "":
                    if not v_cur.startswith("UNKNOWN"):
                        return
            except Exception:
                pass
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
            "_hardening_marker": "v2_hardened",
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAIL recording verdict synth: %s" % e, flush=True)
        raise


atexit.register(_atexit_synth)


# ---------------------------- per-seed runner ----------------------------

def run_seed(seed: int, progress_writer=None) -> Dict[str, Any]:
    """Run one seed across all arms + depths.

    progress_writer: optional callable (arm_name, depth, partial_record) ->
        writes a PROGRESS metrics.json after each arm-depth.
    """
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(N_PREDICATES, N_DIM, g)
    max_depth = max(HOP_DEPTHS)

    print("  [seed=%d] building W_H from %d training chains depth=%d..."
          % (seed, N_CHAINS_TRAIN, max_depth), flush=True)
    t_build = time.time()
    train_triples, train_chains = make_deep_chains(
        N_CHAINS_TRAIN, V_CONCEPTS, N_PREDICATES, max_depth=max_depth,
        g=g, disallow_s=set())
    W_H = ingest_hebbian(train_triples, E, R, sq, N_DIM)
    print("  [seed=%d] W_H built (%d triples) t=%.1fs"
          % (seed, len(train_triples), time.time() - t_build), flush=True)

    train_starts = {c[0][0] for c in train_chains}
    test_triples, test_chains = make_deep_chains(
        N_CHAINS_TEST, V_CONCEPTS, N_PREDICATES, max_depth=max_depth,
        g=g, disallow_s=train_starts)
    W_H_test = W_H + ingest_hebbian(test_triples, E, R, sq, N_DIM)
    W_H_for_eval = W_H_test

    print("  [seed=%d] building W_C via replay (top_K=%d cohorts=%d min_amp=%.2f)..."
          % (seed, R1_REPLAY_TOP_K, R1_REPLAY_COHORTS, R1_REPLAY_MIN_AMPLITUDE),
          flush=True)
    t_replay = time.time()
    W_C, r1_replay_stats = build_W_C_replay_shortcuts(
        E, R, sq, W_H_for_eval, test_chains, N_DIM,
        top_K=R1_REPLAY_TOP_K, cohorts=R1_REPLAY_COHORTS,
        min_amp=R1_REPLAY_MIN_AMPLITUDE,
    )
    print("  [seed=%d] W_C built (n_shortcuts=%d mean_amp=%.3f) t=%.1fs"
          % (seed, r1_replay_stats["n_shortcuts"], r1_replay_stats["mean_amp"],
             time.time() - t_replay), flush=True)

    W_H_checkpoint = W_H_for_eval.copy()
    W_PFC_init = np.zeros((N_DIM, N_DIM), dtype=np.float32)

    out: Dict[str, Any] = {
        "_ckpt_key": seed, "seed": seed, "run_mode": RUN_MODE, "N": N_DIM,
        "V_C": V_CONCEPTS, "n_predicates": N_PREDICATES,
        "n_chains_train": N_CHAINS_TRAIN, "n_chains_test": N_CHAINS_TEST,
        "max_depth": max_depth, "depths": HOP_DEPTHS,
        "r1_replay_stats": r1_replay_stats,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    arm_funcs = [
        ("baseline", lambda d: arm_baseline(E, R, sq, W_H_for_eval, test_chains, d)),
        ("r1_replay_into_w_c",
            lambda d: arm_r1_replay_into_w_c(E, R, sq, W_H_for_eval, W_C, test_chains, d)),
        ("r2_pfc_scratchpad",
            lambda d: arm_r2_pfc_scratchpad(E, R, sq, W_H_for_eval, W_PFC_init,
                                             test_chains, d, N_DIM)),
        ("r3_bidirectional",
            lambda d: arm_r3_bidirectional(E, R, sq, W_H_for_eval, test_chains, d,
                                            R3_MEET_COSINE_TAU)),
        ("combined_r1_r2_r3",
            lambda d: arm_combined(E, R, sq, W_H_for_eval, W_C, test_chains, d,
                                    N_DIM, R3_MEET_COSINE_TAU)),
    ]
    for arm_name, arm_fn in arm_funcs:
        for d in HOP_DEPTHS:
            t_arm = time.time()
            r = arm_fn(d)
            r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            key = "arm_%s_depth_%d" % (arm_name, d)
            out[key] = r
            extra = ""
            if "meet_rate" in r:
                extra = " meet=%.3f" % r["meet_rate"]
            elif "shortcut_hit_rate" in r:
                extra = " shortcut_hit=%.3f" % r["shortcut_hit_rate"]
            elif "shortcut_hits" in r:
                extra = " short=%d meet=%d fwd_fb=%d" % (
                    r["shortcut_hits"], r.get("meet_hits", 0),
                    r.get("fallback_fwd_hits", 0))
            print("  [seed=%d] ARM_%s_depth_%d top1=%.4f%s t=%.1fs"
                  % (seed, arm_name.upper(), d, r["top1"], extra,
                     r["elapsed_s_arm"]), flush=True)
            # L2: per-arm progress write
            if progress_writer is not None:
                try:
                    progress_writer(seed, arm_name, d, dict(out))
                except Exception as pe:
                    print("[progress_writer] FAIL: %s" % pe,
                          file=sys.stderr, flush=True)

    if not np.array_equal(W_H_for_eval, W_H_checkpoint):
        raise RuntimeError(
            "BRAIN_MECHANISM_VS_CARICATURE FAIL: W_H mutated during arm execution; "
            "SEPARATE-W discipline violated; cell results uninterpretable.")
    out["separate_w_assertion_held"] = True

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ---------------------------- verdict (V1_MECHANISM_IDENTICAL) ----------------------------

def _mean(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed
            if key in p and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.mean(vals)) if vals else float("nan")


def _cv(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed
            if key in p and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    if len(vals) < 2:
        return float("nan")
    m = float(np.mean(vals))
    if abs(m) < 1e-9:
        return float("nan")
    return float(np.std(vals) / m)


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    observed_units = 0
    for p in per_seed:
        for arm in EXPECTED_ARMS:
            for d in HOP_DEPTHS:
                if "arm_%s_depth_%d" % (arm, d) in p:
                    observed_units += 1
    expected_units = len(per_seed) * len(EXPECTED_ARMS) * len(HOP_DEPTHS)
    cardinality_ok = (observed_units == expected_units)

    sanity_depth = BASELINE_SANITY_DEPTH if BASELINE_SANITY_DEPTH in HOP_DEPTHS \
                   else max(HOP_DEPTHS)
    baseline_sanity_key = "arm_baseline_depth_%d" % sanity_depth
    baseline_sanity = _mean(per_seed, baseline_sanity_key)
    baseline_breaches = 0
    for p in per_seed:
        v = p.get(baseline_sanity_key, {}).get("top1")
        if v is None or math.isnan(v):
            baseline_breaches += 1
        elif not (BASELINE_SANITY_LO <= v <= BASELINE_SANITY_HI):
            baseline_breaches += 1
    n_seeds = len(per_seed)
    sanity_breached_majority = (baseline_breaches > n_seeds // 2)

    target_depth = BASELINE_SANITY_DEPTH if BASELINE_SANITY_DEPTH in HOP_DEPTHS \
                   else max(HOP_DEPTHS)
    baseline_t = _mean(per_seed, "arm_baseline_depth_%d" % target_depth)
    r1_t = _mean(per_seed, "arm_r1_replay_into_w_c_depth_%d" % target_depth)
    r2_t = _mean(per_seed, "arm_r2_pfc_scratchpad_depth_%d" % target_depth)
    r3_t = _mean(per_seed, "arm_r3_bidirectional_depth_%d" % target_depth)
    comb_t = _mean(per_seed, "arm_combined_r1_r2_r3_depth_%d" % target_depth)

    baseline_cv = _cv(per_seed, "arm_baseline_depth_%d" % target_depth)
    r1_cv = _cv(per_seed, "arm_r1_replay_into_w_c_depth_%d" % target_depth)
    r2_cv = _cv(per_seed, "arm_r2_pfc_scratchpad_depth_%d" % target_depth)
    r3_cv = _cv(per_seed, "arm_r3_bidirectional_depth_%d" % target_depth)
    comb_cv = _cv(per_seed, "arm_combined_r1_r2_r3_depth_%d" % target_depth)

    rails: List[str] = []
    if not cardinality_ok:
        rails.append("CARDINALITY_BREACH(observed=%d expected=%d)"
                     % (observed_units, expected_units))
    if sanity_breached_majority:
        rails.append("BASELINE_SANITY_BREACH(%d/%d seeds outside [%.2f,%.2f]; mean=%.4f)"
                     % (baseline_breaches, n_seeds, BASELINE_SANITY_LO,
                        BASELINE_SANITY_HI, baseline_sanity))

    indiv_max = max(
        r1_t if not math.isnan(r1_t) else -1,
        r2_t if not math.isnan(r2_t) else -1,
        r3_t if not math.isnan(r3_t) else -1,
    )
    indiv_max_cv = float("nan")
    for label, val, cv in [("r1", r1_t, r1_cv), ("r2", r2_t, r2_cv),
                            ("r3", r3_t, r3_cv)]:
        if val == indiv_max:
            indiv_max_cv = cv
            break

    summ = (
        "BASELINE_depth_%d=%.4f (cv=%.3f rail_breach=%d/%d) "
        "R1=%.4f (cv=%.3f) R2=%.4f (cv=%.3f) R3=%.4f (cv=%.3f) "
        "COMBINED=%.4f (cv=%.3f) indiv_max=%.4f cardinality_ok=%s "
        "expected_units=%d observed_units=%d rails=%s"
    ) % (
        target_depth, baseline_t, baseline_cv, baseline_breaches, n_seeds,
        r1_t, r1_cv, r2_t, r2_cv, r3_t, r3_cv,
        comb_t, comb_cv, indiv_max, cardinality_ok,
        expected_units, observed_units, rails,
    )

    if rails:
        return "RAIL_SANITY_BREACH", "RAIL_SANITY_BREACH: " + summ

    if (not math.isnan(comb_t)
        and comb_t >= HP_BARRIER_BROKEN_COMBINED
        and comb_t > indiv_max + HP_COMPOSITION_MARGIN
        and comb_t > baseline_t + HP_COMBINED_LIFT_OVER_BASELINE
        and (math.isnan(comb_cv) or comb_cv <= HP_CV_MAX)):
        return "HARD_PASS_BARRIER_BROKEN", "HARD_PASS_BARRIER_1_BROKEN: " + summ

    if (not math.isnan(indiv_max)
        and indiv_max >= HP_INDIVIDUAL_WIN
        and indiv_max > baseline_t + HP_INDIVIDUAL_LIFT_OVER_BASELINE
        and (math.isnan(indiv_max_cv) or indiv_max_cv <= HP_CV_MAX)):
        return "HARD_PASS_INDIVIDUAL_WINS", "HARD_PASS_INDIVIDUAL_R_ARM_WINS: " + summ

    if (not math.isnan(comb_t) and comb_t < HF_PIVOT_THRESHOLD):
        return "HARD_FAIL_PIVOT", "HARD_FAIL_PIVOT_TO_X1_PRIMITIVE_REPLACEMENT: " + summ
    if (not math.isnan(comb_t)
        and abs(comb_t - baseline_t) <= HF_COMBINED_VS_BASELINE_FLAT):
        return "HARD_FAIL_FLAT", "HARD_FAIL_COMBINED_FLAT_VS_BASELINE: " + summ

    if (not math.isnan(comb_t) and MB_COMBINED_LO <= comb_t < HP_BARRIER_BROKEN_COMBINED):
        return "MIDDLE_BAND", "MIDDLE_BAND_COMBINED_PARTIAL: " + summ
    if (not math.isnan(indiv_max)
        and MB_INDIVIDUAL_LO <= indiv_max < HP_INDIVIDUAL_WIN):
        return "MIDDLE_BAND", "MIDDLE_BAND_INDIVIDUAL_PARTIAL: " + summ

    return "HARD_FAIL", "HARD_FAIL_NO_LIFT: " + summ


# ---------------------------- selftest invocation (with L4 sentinel) ----------------------------

try:
    _selftest()
except BaseException as _exc:
    _write_import_crash_sentinel(_exc)
    raise

if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------- main (with L1 + L2 + L3 hardening) ----------------------------

def _main_inner() -> int:
    """Inner main; L3 wraps this in try/except."""
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d depths=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, HOP_DEPTHS,
             CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    # L1 EARLY-WRITE: visible metrics.json before any compute
    _write_minimal_metrics(out_dir, "UNKNOWN",
        "STARTED: process alive; module init complete; entering main loop",
        extra={"completed_units": 0, "expected_n_units": EXPECTED_N_UNITS})
    print("[L1] early metrics.json written verdict=UNKNOWN msg=STARTED pid=%d"
          % os.getpid(), flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    # L2 progress-writer closure: rewrites metrics.json after each arm
    _progress_state = {"completed_units": 0, "partial_per_seed": {}}

    def _progress_writer(seed: int, arm_name: str, depth: int,
                          out_so_far: Dict[str, Any]) -> None:
        _progress_state["completed_units"] += 1
        _progress_state["partial_per_seed"][seed] = out_so_far
        completed = _progress_state["completed_units"]
        _write_minimal_metrics(out_dir, "UNKNOWN",
            "PROGRESS: completed %d/%d units; last=seed%d arm=%s depth=%d"
            % (completed, EXPECTED_N_UNITS, seed, arm_name, depth),
            extra={
                "completed_units": completed,
                "expected_n_units": EXPECTED_N_UNITS,
                "last_seed": seed, "last_arm": arm_name, "last_depth": depth,
                "partial_per_seed_keys": sorted(list(
                    _progress_state["partial_per_seed"].keys())),
            })

    for s in remaining:
        rec = run_seed(s, progress_writer=_progress_writer)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        # Write a CRASHED state then exit
        _write_minimal_metrics(out_dir, "UNKNOWN",
            "FATAL: no partials available after run_seed loop",
            extra={"completed_units": _progress_state["completed_units"]})
        print("[FATAL] no partials available", flush=True)
        return 1

    assert _LLM_CALL_COUNTER[0] == 0, \
        "substrate-only-decode gate breach: LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "expected_n_units": EXPECTED_N_UNITS,
        "expected_arms": EXPECTED_ARMS,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "_hardening_marker": "v2_hardened",
        "DESIGN_NOTE": (
            "V2 HARDENING DELTA over v1 (commit e1614b4f): mechanism IDENTICAL; "
            "only added L1 early-write + L2 per-arm-progress + L3 outer try/except + "
            "L4 import-crash sentinel so silent death is now visible. Tests whether "
            "META_BARRIER_1 (substrate multi-hop permanent 2-hop) was prematurely "
            "declared. Per drill 2026-06-27, 4 of 5 prior refutations tested "
            "CARICATURES of brain mechanisms. R1=NREM replay-as-OPERATOR with "
            "SEPARATE W_C. R2=PFC scratchpad in SEPARATE W_PFC. R3=bidirectional "
            "meet-in-middle via HRR-involutive unbinding. HARD_PASS_BARRIER_BROKEN "
            "requires ARM_COMBINED depth-5 >= 0.65 AND composition wins individual "
            "AND +0.45 over baseline AND cv<=0.08."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)"
          % (len(per_seed), metrics["elapsed_s"]), flush=True)
    return 0


if __name__ == "__main__":
    # L3 OUTER try/except: catches anything escaping _main_inner
    try:
        _rc = _main_inner()
        sys.exit(_rc)
    except BaseException as exc:
        # Record-and-halt per META_RULE_J. Write a CRASHED metrics.json then re-raise.
        out_dir = _RESULTS_HOLDER.get("out_dir")
        if out_dir is None:
            try:
                out_dir = get_output_dir(ANCHOR_NAME)
                out_dir.mkdir(parents=True, exist_ok=True)
                _RESULTS_HOLDER["out_dir"] = out_dir
            except Exception:
                out_dir = None
        if out_dir is not None:
            tb = traceback.format_exc()
            _write_minimal_metrics(out_dir, "UNKNOWN",
                "CRASHED: %s: %s" % (type(exc).__name__, str(exc)),
                extra={
                    "_exception_class": type(exc).__name__,
                    "_exception_message": str(exc),
                    "_exception_traceback": tb,
                })
            print("[L3] outer try/except wrote CRASHED metrics.json", flush=True)
        print("[L3] re-raising original exception", flush=True)
        raise
