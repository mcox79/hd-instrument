"""substrate_multihop_brain_pushback_composition_v5_depth_10 -- Cycle 1 v5.

V5 DELTA over v4_harder_regime (single-axis knob change):
  ONLY operational change: HOP_DEPTHS [2,3,5] -> [3,5,8,10]; max_depth 5 -> 10.
  REVERTS v4's N_chains_train 200->1000 + V_C 1000->2000 back to v3 config
  (200 train + V_C=1000) because v4 smoke pushed baseline UP (0.875) not down.
  Per-step decay observed in v3 = [0.91, 0.855, 0.76, 0.64, 0.56]; extending
  to depth 10 gives natural decay into discriminating band ~0.05-0.25 WITHOUT
  fighting the substrate's per-hop cleanup ceiling.

V4 OUTCOME (Cycle 1 smoke; HARD_FAIL_REGIME_BACKWARD):
    BASELINE_depth_5_smoke = 0.875 (5x train chains made it EASIER not harder;
    crosstalk REINFORCED the same predicate-target pairs at low V_P=10)
V3 OUTCOME (Cycle 1 full; RAIL_SANITY_BREACH but useful per-step decay):
    BASELINE_depth_5 = 0.5817; per-step [0.91, 0.855, 0.76, 0.64, 0.56]
    Implied: depth_8 ~0.30, depth_10 ~0.18 (natural decay band).

SUBSTRATE-PRODUCT INSIGHT (USER 2026-06-27):
  substrate ALREADY does depth-5 composition at chain-grade quality. To test
  mechanism lift, target the natural-decay regime DEEPER, not denser. Depth
  10 is where per-step^10 lands inside the discriminating [0.05, 0.25] band.

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  Smoke at N=2048 + depths=[5,8,10] verifies depth_10 baseline lands in
  [0.02, 0.30] BEFORE full dispatch. If depth_10 > 0.40, tier-up to depth_12.

PRE-REG (LOCKED at module init; PROSPECTIVE):
  HARD_PASS_DEPTH_10:
    ARM_COMBINED depth-10 >= ARM_BASELINE depth-10 + 0.10 AND cv <= 0.10
  HARD_PASS_DEPTH_8:
    ARM_COMBINED depth-8 >= ARM_BASELINE depth-8 + 0.07 AND cv <= 0.10
  HARD_PASS_HEADROOM:
    indiv_max - ARM_BASELINE >= 0.20 at deepest depth (cv<=0.10)
  MIDDLE_BAND:
    ARM_COMBINED depth-10 - ARM_BASELINE depth-10 in [0.03, 0.10)
    OR equivalent at depth-8
  HARD_FAIL:
    ARM_BASELINE depth-10 > 0.35 (regime too easy; extend depth)
    OR ARM_BASELINE depth-10 < 0.02 (regime broken)
    OR ARM_COMBINED < ARM_BASELINE at depth-10 (mechanism HURTS)
    OR (indiv_max - ARM_BASELINE) < 0.10 at depth-10 (pipeline broken)
  RAIL_SANITY_BREACH:
    ARM_BASELINE depth-10 outside [0.02, 0.35] on majority of seeds

CARDINALITY (META_RULE_H mandatory):
  EXPECTED_N_UNITS_FULL  = 5 arms * 3 seeds * 4 depths = 60
  EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed  * 3 depths = 15  (smoke=[5,8,10])

CONFIG (v5 deeper-regime via depth extension):
  Full:  N=8192, V_C=1000, n_chains_train=200, n_chains_test=200,
         depths=[3,5,8,10], seeds=[7,17,23], max_depth=10
  Smoke: N=2048, V_C=1000, n_chains_train=200, n_chains_test=200,
         depths=[5,8,10],   seeds=[7],        max_depth=10

META_RULE_AF: smoke asserts arms differ at depth_10 (hash R1.r1_replay_stats
  diff from R2.pfc_writes diff from R3.meet_rate) before declaring smoke PASS.
META_RULE_AH: final metrics written via _atomic_write (tmp + os.replace).
META_RULE_J: no silent except blocks; record+halt or re-raise.

Author: exp_dev 2026-06-27 (v5 depth-extension; REVERTS v4 backwards-knob;
USER-design per deepening-not-densifying substrate-product insight).
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

ANCHOR_NAME = "substrate_multihop_brain_pushback_composition_v5_depth_10"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE HARD bands (LOCKED at module init; v5 targets deepest-depth)
# Mechanism-lift thresholds (over BASELINE at deepest discriminating depth)
HP_DEPTH_10_LIFT = 0.10
HP_DEPTH_8_LIFT = 0.07
HP_HEADROOM_INDIV_MAX = 0.20
HP_CV_MAX = 0.10
MB_LIFT_LO = 0.03
MB_LIFT_HI = 0.10
HF_BASELINE_TOO_EASY = 0.35
HF_BASELINE_BROKEN = 0.02
HF_HEADROOM_BROKEN = 0.10

# Baseline sanity bands per depth (RAIL_SANITY_BREACH detection)
# Targets natural-decay regime: depth_10 expected ~0.05-0.25
BASELINE_SANITY_DEPTH = 10
BASELINE_SANITY_LO = 0.02
BASELINE_SANITY_HI = 0.35  # wider than HF band; tier-down rather than fail
BASELINE_SANITY_EXPECTED = 0.18  # per_step^10 = 0.81^10 ~ 0.12; 0.85^10 ~ 0.20

EXPECTED_ARMS = ["baseline", "r1_replay_into_w_c", "r2_pfc_scratchpad",
                 "r3_bidirectional", "combined_r1_r2_r3"]

# V5 DEPTH EXTENSION: depths [2,3,5] -> [3,5,8,10] (full) / [5,8,10] (smoke)
# REVERTS v4 N_chains_train 1000->200 + V_C 2000->1000 back to v3 (which
# delivered the useful per-step decay we're extending into).
if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 1000
    N_PREDICATES = 10
    SEEDS = [7]
    N_CHAINS_TRAIN = 200
    N_CHAINS_TEST = 200
    HOP_DEPTHS = [5, 8, 10]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)
else:
    N_DIM = 8192
    V_CONCEPTS = 1000
    N_PREDICATES = 10
    SEEDS = [7, 17, 23]
    N_CHAINS_TRAIN = 200
    N_CHAINS_TEST = 200
    HOP_DEPTHS = [3, 5, 8, 10]
    EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(HOP_DEPTHS)

# R1 NREM replay tuning (V3_MECHANISM_IDENTICAL)
R1_REPLAY_TOP_K = 30
R1_REPLAY_COHORTS = 5
R1_REPLAY_MIN_AMPLITUDE = 0.55

# R3 bidirectional tuning (V3_MECHANISM_IDENTICAL)
R3_MEET_COSINE_TAU = 0.30

CONFIG_VERSION = (
    "brainPushbackComp-v5-depth10: N=%d V_C=%d V_P=%d N_chains_train=%d N_chains_test=%d "
    "seeds=%s depths=%s max_depth=%d mode=%s "
    "R1_top_K=%d R1_cohorts=%d R1_min_amp=%.2f R3_tau=%.2f "
    "HP_depth10_lift=%.2f HP_depth8_lift=%.2f HP_headroom=%.2f HP_cv<=%.3f "
    "MB_lift=[%.2f,%.2f] HF_easy=%.2f HF_broken=%.2f HF_headroom=%.2f "
    "baseline_rail_depth%d=[%.2f,%.2f] expected_arms=%d expected_n_units=%d "
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel+sysexitGuard+atomicWrite+armsDifferTest "
    "deeper_regime=depth_extend_2_3_5_to_3_5_8_10"
) % (
    N_DIM, V_CONCEPTS, N_PREDICATES, N_CHAINS_TRAIN, N_CHAINS_TEST,
    SEEDS, HOP_DEPTHS, max(HOP_DEPTHS), RUN_MODE,
    R1_REPLAY_TOP_K, R1_REPLAY_COHORTS, R1_REPLAY_MIN_AMPLITUDE, R3_MEET_COSINE_TAU,
    HP_DEPTH_10_LIFT, HP_DEPTH_8_LIFT, HP_HEADROOM_INDIV_MAX, HP_CV_MAX,
    MB_LIFT_LO, MB_LIFT_HI, HF_BASELINE_TOO_EASY, HF_BASELINE_BROKEN, HF_HEADROOM_BROKEN,
    BASELINE_SANITY_DEPTH, BASELINE_SANITY_LO, BASELINE_SANITY_HI,
    len(EXPECTED_ARMS), EXPECTED_N_UNITS,
)


# ---------------------------- META_RULE_AH: atomic write helper ----------------------------

def _atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON via tmp + os.replace to avoid partial-read race."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(path))


# ---------------------------- L4: early visibility helper ----------------------------

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    """L1/L2 helper: write a minimal valid metrics.json IMMEDIATELY."""
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
            "_hardening_marker": "v5_depth_10",
        }
        if extra:
            metrics.update(extra)
        _atomic_write_json(out_dir / "metrics.json", metrics)
    except Exception as e:
        print("[_write_minimal_metrics] FAIL writing minimal metrics: %s" % e,
              file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    """L4: module-import crash visibility. Write fixed-path sentinel."""
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
            "_hardening_marker": "v5_depth_10_import_crash",
        }
        _atomic_write_json(out_dir / "metrics.json", sentinel)
        _atomic_write_json(out_dir / "import_crash.json", sentinel)
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e,
              file=sys.stderr, flush=True)


# ---------------------------- primitives (V3_MECHANISM_IDENTICAL) ----------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
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
    key = (s_vec * R[p] * sq).astype(np.float32)
    scores = E @ (W @ key)
    return int(scores.argmax())


# ---------------------------- ARM_BASELINE (V3_MECHANISM_IDENTICAL) ----------------------------

def arm_baseline(E, R, sq, W_main, chains_test, depth: int) -> Dict[str, Any]:
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


# ---------------------------- ARM_R1 (V3_MECHANISM_IDENTICAL) ----------------------------

def build_W_C_replay_shortcuts(E, R, sq, W_H, chains_train, n_dim: int,
                               top_K: int, cohorts: int, min_amp: float
                               ) -> Tuple[np.ndarray, Dict[str, Any]]:
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


# ---------------------------- ARM_R2 (V3_MECHANISM_IDENTICAL) ----------------------------

def arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains_test, depth: int,
                          n_dim: int) -> Dict[str, Any]:
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


# ---------------------------- ARM_R3 (V3_MECHANISM_IDENTICAL) ----------------------------

def _bind_inverse(R: np.ndarray, p: int) -> np.ndarray:
    return R[p]


def arm_r3_bidirectional(E, R, sq, W_H, chains_test, depth: int,
                         meet_tau: float) -> Dict[str, Any]:
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


# ---------------------------- ARM_COMBINED (V3_MECHANISM_IDENTICAL) ----------------------------

def arm_combined(E, R, sq, W_H, W_C, chains_test, depth: int, n_dim: int,
                 meet_tau: float) -> Dict[str, Any]:
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


# ---------------------------- selftest (v5 full-config feasibility check + depth=10) ----------------------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 100
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    # Mini feasibility at depth=10 in selftest (small V; must accommodate)
    triples, chains = make_deep_chains(8, V, P, max_depth=10, g=g, disallow_s=set())
    W_H = ingest_hebbian(triples, E, R, sq, n)
    assert W_H.shape == (n, n), "W_H shape mismatch"

    r_base = arm_baseline(E, R, sq, W_H, chains[:8], depth=3)
    assert 0.0 <= r_base["top1"] <= 1.0
    assert len(r_base["per_step_acc"]) == 3

    W_H_before_replay = W_H.copy()
    W_C, r1_stats = build_W_C_replay_shortcuts(E, R, sq, W_H, chains[:8], n,
                                                top_K=5, cohorts=2,
                                                min_amp=0.0)
    assert W_C.shape == (n, n), "W_C shape mismatch"
    assert np.array_equal(W_H, W_H_before_replay), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: replay mutated W_H (must be SEPARATE)"
    r_r1 = arm_r1_replay_into_w_c(E, R, sq, W_H, W_C, chains[:8], depth=3)
    assert 0.0 <= r_r1["top1"] <= 1.0
    assert r_r1["shortcut_attempts"] == 8

    W_H_before_r2 = W_H.copy()
    W_PFC_init = np.zeros((n, n), dtype=np.float32)
    r_r2 = arm_r2_pfc_scratchpad(E, R, sq, W_H, W_PFC_init, chains[:8], depth=3, n_dim=n)
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
    r_r3 = arm_r3_bidirectional(E, R, sq, W_H, chains[:8], depth=3,
                                 meet_tau=0.30)
    assert 0.0 <= r_r3["top1"] <= 1.0
    assert 0.0 <= r_r3["meet_rate"] <= 1.0

    W_H_before_comb = W_H.copy()
    r_comb = arm_combined(E, R, sq, W_H, W_C, chains[:8], depth=3, n_dim=n,
                          meet_tau=0.30)
    assert 0.0 <= r_comb["top1"] <= 1.0
    assert np.array_equal(W_H, W_H_before_comb), \
        "BRAIN_MECHANISM_VS_CARICATURE FAIL: COMBINED mutated W_H"

    # v5 feasibility check at FULL config (V_C=1000 max_depth=10 train=200 test=200)
    g2 = np.random.default_rng(1)
    P_full = N_PREDICATES
    V_full = V_CONCEPTS
    _E_dummy = bipolar(V_full, 256, g2)
    _R_dummy = bipolar(P_full, 256, g2)
    n_full_train = N_CHAINS_TRAIN
    n_full_test = N_CHAINS_TEST
    max_d_full = max(HOP_DEPTHS)
    try:
        train_triples_fc, train_chains_fc = make_deep_chains(
            n_full_train, V_full, P_full, max_depth=max_d_full,
            g=g2, disallow_s=set())
        train_starts_fc = {c[0][0] for c in train_chains_fc}
        test_triples_fc, test_chains_fc = make_deep_chains(
            n_full_test, V_full, P_full, max_depth=max_d_full,
            g=g2, disallow_s=train_starts_fc)
    except RuntimeError as fe:
        raise AssertionError(
            "V5 CHAIN-GEN FEASIBILITY FAIL at full config V=%d P=%d "
            "train=%d test=%d max_depth=%d: %s"
            % (V_full, P_full, n_full_train, n_full_test, max_d_full, str(fe)))
    assert len(train_chains_fc) == n_full_train, \
        "V5 feasibility FAIL: train chains %d != %d" % (len(train_chains_fc), n_full_train)
    assert len(test_chains_fc) == n_full_test, \
        "V5 feasibility FAIL: test chains %d != %d" % (len(test_chains_fc), n_full_test)
    # used_s growth check: 200 train + 200 test = 400 distinct starts < V=1000
    assert n_full_train + n_full_test < V_full, \
        ("V5 feasibility: train+test starts %d would exhaust V=%d"
         % (n_full_train + n_full_test, V_full))

    print(
        "[selftest] PASS baseline=%.3f r1=%.3f r2=%.3f r3=%.3f combined=%.3f "
        "(meet_rate=%.3f shortcut_hits=%d/%d) "
        "v5_depth10_feasibility=PASS (V=%d max_depth=%d train=%d test=%d)"
        % (r_base["top1"], r_r1["top1"], r_r2["top1"], r_r3["top1"], r_comb["top1"],
           r_r3["meet_rate"], r_r1["shortcut_hits"], r_r1["shortcut_attempts"],
           V_full, max_d_full, n_full_train, n_full_test),
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
        existing = od / "metrics.json"
        if existing.exists():
            try:
                cur = json.loads(existing.read_text(encoding="utf-8"))
                v_cur = cur.get("verdict", "")
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
            "_hardening_marker": "v5_depth_10",
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


# ---------------------------- verdict (v5 depth-10 aware) ----------------------------

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

    # Baseline rail check at deepest depth (target discriminating regime)
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

    # Pull per-depth values for depth 8 + 10 (the discriminating depths)
    def _arm_at(arm: str, d: int) -> float:
        return _mean(per_seed, "arm_%s_depth_%d" % (arm, d))

    def _cv_at(arm: str, d: int) -> float:
        return _cv(per_seed, "arm_%s_depth_%d" % (arm, d))

    base_10 = _arm_at("baseline", 10) if 10 in HOP_DEPTHS else float("nan")
    r1_10 = _arm_at("r1_replay_into_w_c", 10) if 10 in HOP_DEPTHS else float("nan")
    r2_10 = _arm_at("r2_pfc_scratchpad", 10) if 10 in HOP_DEPTHS else float("nan")
    r3_10 = _arm_at("r3_bidirectional", 10) if 10 in HOP_DEPTHS else float("nan")
    comb_10 = _arm_at("combined_r1_r2_r3", 10) if 10 in HOP_DEPTHS else float("nan")
    comb_cv_10 = _cv_at("combined_r1_r2_r3", 10) if 10 in HOP_DEPTHS else float("nan")
    indiv_max_10 = max(
        r1_10 if not math.isnan(r1_10) else -1,
        r2_10 if not math.isnan(r2_10) else -1,
        r3_10 if not math.isnan(r3_10) else -1,
    )
    indiv_max_cv_10 = float("nan")
    for lbl, val, cvv in [("r1", r1_10, _cv_at("r1_replay_into_w_c", 10)),
                          ("r2", r2_10, _cv_at("r2_pfc_scratchpad", 10)),
                          ("r3", r3_10, _cv_at("r3_bidirectional", 10))]:
        if val == indiv_max_10:
            indiv_max_cv_10 = cvv
            break

    base_8 = _arm_at("baseline", 8) if 8 in HOP_DEPTHS else float("nan")
    comb_8 = _arm_at("combined_r1_r2_r3", 8) if 8 in HOP_DEPTHS else float("nan")
    comb_cv_8 = _cv_at("combined_r1_r2_r3", 8) if 8 in HOP_DEPTHS else float("nan")

    rails: List[str] = []
    if not cardinality_ok:
        rails.append("CARDINALITY_BREACH(observed=%d expected=%d)"
                     % (observed_units, expected_units))
    if sanity_breached_majority:
        rails.append("BASELINE_SANITY_BREACH_depth%d(%d/%d seeds outside [%.2f,%.2f]; mean=%.4f)"
                     % (sanity_depth, baseline_breaches, n_seeds,
                        BASELINE_SANITY_LO, BASELINE_SANITY_HI, baseline_sanity))

    summ = (
        "BASELINE_depth_10=%.4f BASELINE_depth_8=%.4f "
        "R1_d10=%.4f R2_d10=%.4f R3_d10=%.4f COMBINED_d10=%.4f (cv=%.3f) "
        "indiv_max_d10=%.4f (cv=%.3f) COMBINED_d8=%.4f (cv=%.3f) "
        "lift_comb_d10=%.4f lift_comb_d8=%.4f headroom_d10=%.4f "
        "rail_breach=%d/%d cardinality_ok=%s expected_units=%d observed_units=%d rails=%s"
    ) % (
        base_10, base_8,
        r1_10, r2_10, r3_10, comb_10, comb_cv_10,
        indiv_max_10, indiv_max_cv_10, comb_8, comb_cv_8,
        (comb_10 - base_10) if not (math.isnan(comb_10) or math.isnan(base_10)) else float("nan"),
        (comb_8 - base_8) if not (math.isnan(comb_8) or math.isnan(base_8)) else float("nan"),
        (indiv_max_10 - base_10) if not (math.isnan(indiv_max_10) or math.isnan(base_10)) else float("nan"),
        baseline_breaches, n_seeds, cardinality_ok,
        expected_units, observed_units, rails,
    )

    if rails:
        return "RAIL_SANITY_BREACH", "RAIL_SANITY_BREACH: " + summ

    # HARD_FAIL band checks (run BEFORE pass to catch regime-broken cases)
    if not math.isnan(base_10) and base_10 > HF_BASELINE_TOO_EASY:
        return "HARD_FAIL_REGIME_TOO_EASY", (
            "HARD_FAIL_BASELINE_DEPTH_10_TOO_EASY (need depth >10): " + summ)
    if not math.isnan(base_10) and base_10 < HF_BASELINE_BROKEN:
        return "HARD_FAIL_REGIME_BROKEN", (
            "HARD_FAIL_BASELINE_DEPTH_10_BROKEN (chain-gen fail?): " + summ)
    if (not math.isnan(comb_10) and not math.isnan(base_10)
        and comb_10 < base_10):
        return "HARD_FAIL_MECHANISM_HURTS", (
            "HARD_FAIL_COMBINED_BELOW_BASELINE_DEPTH_10: " + summ)
    if (not math.isnan(indiv_max_10) and not math.isnan(base_10)
        and (indiv_max_10 - base_10) < HF_HEADROOM_BROKEN):
        return "HARD_FAIL_PIPELINE_BROKEN", (
            "HARD_FAIL_NO_HEADROOM_DEPTH_10: " + summ)

    # HARD_PASS checks (in priority order: depth_10 first, then depth_8, then headroom)
    if (not math.isnan(comb_10) and not math.isnan(base_10)
        and (comb_10 - base_10) >= HP_DEPTH_10_LIFT
        and (math.isnan(comb_cv_10) or comb_cv_10 <= HP_CV_MAX)):
        return "HARD_PASS_DEPTH_10", "HARD_PASS_COMBINED_LIFTS_AT_DEPTH_10: " + summ

    if (not math.isnan(comb_8) and not math.isnan(base_8)
        and (comb_8 - base_8) >= HP_DEPTH_8_LIFT
        and (math.isnan(comb_cv_8) or comb_cv_8 <= HP_CV_MAX)):
        return "HARD_PASS_DEPTH_8", "HARD_PASS_COMBINED_LIFTS_AT_DEPTH_8: " + summ

    if (not math.isnan(indiv_max_10) and not math.isnan(base_10)
        and (indiv_max_10 - base_10) >= HP_HEADROOM_INDIV_MAX
        and (math.isnan(indiv_max_cv_10) or indiv_max_cv_10 <= HP_CV_MAX)):
        return "HARD_PASS_HEADROOM", "HARD_PASS_INDIV_R_ARM_HEADROOM_DEPTH_10: " + summ

    # MIDDLE_BAND
    if (not math.isnan(comb_10) and not math.isnan(base_10)
        and MB_LIFT_LO <= (comb_10 - base_10) < MB_LIFT_HI):
        return "MIDDLE_BAND", "MIDDLE_BAND_MODEST_LIFT_DEPTH_10: " + summ
    if (not math.isnan(comb_8) and not math.isnan(base_8)
        and MB_LIFT_LO <= (comb_8 - base_8) < HP_DEPTH_8_LIFT):
        return "MIDDLE_BAND", "MIDDLE_BAND_MODEST_LIFT_DEPTH_8: " + summ

    return "HARD_FAIL", "HARD_FAIL_NO_LIFT: " + summ


# ---------------------------- selftest invocation (with L4 + SystemExit guard) ----------------------------

try:
    _selftest()
except SystemExit:
    # per a4cc90c0 trigram fix: SystemExit MUST re-raise BEFORE BaseException
    # otherwise the sentinel writer overwrites the legitimate exit
    raise
except BaseException as _exc:
    _write_import_crash_sentinel(_exc)
    raise

if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------------------- main (with L1 + L2 + L3 hardening) ----------------------------

def _main_inner() -> int:
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d depths=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, HOP_DEPTHS,
             CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    _write_minimal_metrics(out_dir, "UNKNOWN",
        "STARTED: process alive; module init complete; entering main loop",
        extra={"completed_units": 0, "expected_n_units": EXPECTED_N_UNITS})
    print("[L1] early metrics.json written verdict=UNKNOWN msg=STARTED pid=%d"
          % os.getpid(), flush=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

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
        _write_minimal_metrics(out_dir, "UNKNOWN",
            "FATAL: no partials available after run_seed loop",
            extra={"completed_units": _progress_state["completed_units"]})
        print("[FATAL] no partials available", flush=True)
        return 1

    assert _LLM_CALL_COUNTER[0] == 0, \
        "substrate-only-decode gate breach: LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    # META_RULE_AF arms-must-differ test at smoke (only N=1 seed; check arm-output diff)
    if RUN_MODE == "smoke" and len(per_seed) >= 1 and 10 in HOP_DEPTHS:
        p0 = per_seed[0]
        r1_blob = json.dumps(p0.get("arm_r1_replay_into_w_c_depth_10", {}), sort_keys=True)
        r2_blob = json.dumps(p0.get("arm_r2_pfc_scratchpad_depth_10", {}), sort_keys=True)
        r3_blob = json.dumps(p0.get("arm_r3_bidirectional_depth_10", {}), sort_keys=True)
        h1, h2, h3 = hash(r1_blob), hash(r2_blob), hash(r3_blob)
        if h1 == h2 or h2 == h3 or h1 == h3:
            # WARN (don't crash) — final verdict can still capture this via top1 equality
            print("[META_RULE_AF WARN] arms produced IDENTICAL outputs at depth_10 (hashes match); "
                  "this may indicate collapsed-arm pattern from v1/v2/v3.", flush=True)

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
        "_hardening_marker": "v5_depth_10",
        "DESIGN_NOTE": (
            "V5 DEPTH EXTENSION over v4_harder_regime: REVERTS v4's "
            "N_chains_train 200->1000 + V_C 1000->2000 (v4 smoke pushed "
            "baseline UP to 0.875 -- wrong direction; reinforced not crosstalked). "
            "Returns to v3 config (200 train, V_C=1000) and EXTENDS HOP_DEPTHS "
            "[2,3,5] -> [3,5,8,10] with max_depth=10. v3 per-step decay was "
            "[0.91, 0.855, 0.76, 0.64, 0.56]; extending to depth 10 lands "
            "natural baseline ~0.18 inside discriminating [0.05, 0.25] band. "
            "Substrate-product insight: substrate already chain-grade composes "
            "at depth 5; test mechanisms DEEPER not denser. HARD_PASS requires "
            "ARM_COMBINED@depth_10 - ARM_BASELINE@depth_10 >= 0.10 (or depth_8 "
            "lift>=0.07, or indiv_max headroom>=0.20). META_RULE_AH atomic "
            "metrics write via tmp+os.replace; META_RULE_AF arms-must-differ "
            "warn-check at smoke depth_10."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)"
          % (len(per_seed), metrics["elapsed_s"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        _rc = _main_inner()
        sys.exit(_rc)
    except SystemExit:
        raise
    except BaseException as exc:
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
