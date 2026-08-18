"""cortex_hippo_handoff_FULL_seed_23_v1 -- single-seed chunk of FULL multi-seed verification.

Parent cell:    experiments/exp_cortex_hippo_handoff_sparse_DG_dense_cortex_v1.py
Parent prereg:  preregs/2026-06-27_cortex_hippo_handoff_sparse_DG_dense_cortex_v1.md
Parent smoke:   data/exp_cortex_hippo_handoff_sparse_DG_dense_cortex_v1/partial_metrics_7.json
                (HARD_PASS at smoke scale; FULL=1.000 NO_REPLAY=0.003 DIRECT=1.000 wall=50s)

Re-architecture rationale:
  Original FULL cell died at 4h runner timeout (2026-06-27 22:11Z); only
  partial_metrics_7 (smoke-mode) saved.  Original FULL config:
    N_h=512 N_c=8192 M=200 N_replay=50, seeds=[7,17,23], ~2.35h per seed = ~7h total.
  Chunked architecture: 3 single-seed cells (this one + _seed_17 + _seed_23) run
  in parallel/series under 4h cap each.  Skunkworks aggregates across the 3
  cells for chain-grade promotion of parent atom cortex_hippo_handoff.

Mechanism (unchanged from parent A1):
  W_hippo  = sparse bipolar 10% density, N_h = 512 dims (small, but k-WTA active)
  W_cortex = dense float,                N_c = 8192 dims (DIFFERENT SHAPE)
  Replay   = random-uniform sampling from W_hippo

ARMS (3, unchanged from parent):
  ARM_FULL_HANDOFF       -- encode->hippo, replay->cortex (slow Hebbian),
                            then zero W_hippo. Recall test on cortex.
  ARM_NO_REPLAY          -- baseline-floor; same as FULL but skip replay step.
  ARM_DIRECT_CORTEX      -- baseline-ceiling; items written directly to cortex
                            with same eta.

HARD_PASS (single-seed):
  acc(FULL_HANDOFF) >= 0.50 AND
  acc(FULL) - acc(NO_REPLAY) >= 0.40 AND
  acc(FULL) >= 0.70 * acc(DIRECT_CORTEX)

HARD_FAIL (single-seed):
  acc(FULL) - acc(NO_REPLAY) < 0.10 (transfer doing nothing)
  OR NO_REPLAY > 0.20 (cortex leaks signal)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 arms x 1 seed = 3 arms
  HARD_FAIL_CARDINALITY_BREACH when observed != 3.

PROT-018: no _n suffix (capability-test).
ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ.
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
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_handoff_FULL_seed_23_v1"
SEED_THIS_CHUNK = 23
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_cortex_hippo_handoff_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Config (FULL matches parent's SEEDS_FULL config; smoke matches parent's smoke)
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 512           # MATCHES original FULL (per orchestrator report)
N_CORTEX_FULL = 8192
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 200
N_REPLAY_CYCLES_FULL = 50
ETA_CORTEX_FULL = 0.01

# Single seed per chunk (chunked architecture)
SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    N_HIPPO = 512
    N_CORTEX = 1024
    M_ITEMS = 400
    N_REPLAY_CYCLES = 5
    ETA_CORTEX = 0.005
    SEEDS = [SEED_THIS_CHUNK]
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    N_REPLAY_CYCLES = N_REPLAY_CYCLES_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = SEEDS_FULL

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},N_replay={N_REPLAY_CYCLES},"
    f"eta_c={ETA_CORTEX},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"hardening=L1early+L2perarm+L4importsentinel+METARULE_AF+METARULE_AH"
)

# CRLB pre-validation (per exp_dev.md section 9):
#   Per-arm recall is a binomial proportion over M_ITEMS=200 (FULL) trials.
#   CRLB for binomial p: var(p_hat) >= p*(1-p)/M.  At p=0.5, M=200:
#     sigma_min = sqrt(0.25/200) = 0.0354.
#   Discriminator gap = recall(FULL) - recall(NO_REPLAY).  Var(gap) <= var(FULL)+var(NO_REPLAY)
#   <= 2 * 0.25/200 = 0.0025 => sigma(gap) >= 0.05.
#   HARD_PASS gap band = 0.40; FAIL gap band = 0.10.  Margin >>5*sigma.  PASS.

# Cardinality (META_RULE_H): 3 arms x 1 seed = 3 arms expected.
EXPECTED_N_UNITS = 3


# ---------------------------------------------------------------------------
# Substrate primitives (unchanged from parent)
# ---------------------------------------------------------------------------
def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_hippo_to_cortex(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write_cortex(W_c: np.ndarray, key: np.ndarray, val: np.ndarray,
                         eta: float) -> None:
    W_c += eta * np.outer(val, key)


def hebbian_write_hippo_sparse(W_h: np.ndarray, key_h: np.ndarray,
                               val_h: np.ndarray) -> None:
    W_h += np.outer(val_h, key_h)


def cortex_readout(W_c: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W_c @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cosine_match(pred: np.ndarray, candidates: np.ndarray) -> int:
    n_p = float(np.linalg.norm(pred))
    if n_p == 0:
        return 0
    p_n = pred / n_p
    sims = candidates @ p_n
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# Per-arm runner (unchanged from parent)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            keys_raw: np.ndarray, vals_raw: np.ndarray,
            P_in: np.ndarray, P_hc: np.ndarray) -> Dict:
    t0 = time.time()
    try:
        W_hippo = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_hippo is W_cortex")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_hippo.shape={W_hippo.shape} == "
                f"W_cortex.shape={W_cortex.shape}; should differ"
            )

        keys_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        vals_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        keys_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        vals_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        for i in range(M_ITEMS):
            keys_h[i] = pattern_separate_sparse(keys_raw[i], P_in, K_HIPPO_ACTIVE)
            vals_h[i] = pattern_separate_sparse(vals_raw[i], P_in, K_HIPPO_ACTIVE)
            keys_c[i] = project_hippo_to_cortex(keys_h[i], P_hc)
            vals_c[i] = project_hippo_to_cortex(vals_h[i], P_hc)

        if arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY"):
            active_per_atom = np.sum(np.abs(keys_h) > 0, axis=1)
            if not np.all(active_per_atom == K_HIPPO_ACTIVE):
                raise AssertionError(
                    f"SPARSITY VIOLATION: keys_h active counts mismatch "
                    f"K_HIPPO_ACTIVE={K_HIPPO_ACTIVE}; got {active_per_atom[:5]}..."
                )

        if arm_name == "ARM_FULL_HANDOFF":
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            rng = np.random.RandomState(seed + 31)
            for _cycle in range(N_REPLAY_CYCLES):
                replay_indices = rng.choice(M_ITEMS, size=M_ITEMS, replace=False)
                for i in replay_indices:
                    hebbian_write_cortex(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
            W_hippo[:] = 0.0
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                argmax = cosine_match(pred, vals_c)
                if argmax == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(np.linalg.norm(W_hippo))
            cortex_norm = float(np.linalg.norm(W_cortex))

        elif arm_name == "ARM_NO_REPLAY":
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            W_hippo[:] = 0.0
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                argmax = cosine_match(pred, vals_c)
                if argmax == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(np.linalg.norm(W_hippo))
            cortex_norm = float(np.linalg.norm(W_cortex))

        elif arm_name == "ARM_DIRECT_CORTEX":
            for _cycle in range(N_REPLAY_CYCLES):
                for i in range(M_ITEMS):
                    hebbian_write_cortex(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                argmax = cosine_match(pred, vals_c)
                if argmax == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = 0.0
            cortex_norm = float(np.linalg.norm(W_cortex))

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "hippo_post_zero_norm": float(hippo_post_zero_norm),
            "cortex_norm": float(cortex_norm),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
            "wall_s": float(wall),
            "arm_status": "OK",
        }

    except SystemExit:
        # META_RULE: re-raise SystemExit BEFORE catching BaseException
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float("nan"),
            "n_items": 0,
            "hippo_post_zero_norm": float("nan"),
            "cortex_norm": float("nan"),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
    W_c = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c (same object)")
    if W_h.shape == W_c.shape:
        raise AssertionError(
            f"shapes match: W_h={W_h.shape} W_c={W_c.shape} (must differ)"
        )


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    P = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = pattern_separate_sparse(x, P, K_HIPPO_ACTIVE)
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != K_HIPPO_ACTIVE:
        raise AssertionError(
            f"k-WTA sparsity wrong: got {n_active} active, want {K_HIPPO_ACTIVE}"
        )
    nz = h[np.abs(h) > 0]
    if not np.all(np.isin(nz, [-1.0, 1.0])):
        raise AssertionError("sparse code not bipolar")


def _selftest_projection_dim_match() -> None:
    rng = np.random.RandomState(11)
    h = np.zeros(N_HIPPO, dtype=np.float64)
    h[:K_HIPPO_ACTIVE] = 1.0
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    c = project_hippo_to_cortex(h, P_hc)
    if c.shape != (N_CORTEX,):
        raise AssertionError(f"projection shape wrong: {c.shape} != ({N_CORTEX},)")
    norm = float(np.linalg.norm(c))
    if not (0.5 < norm < 1.5):
        raise AssertionError(f"projection not L2-normed: norm={norm}")


def _selftest_chunk_seed_matches_anchor() -> None:
    # Defends against ANCHOR_NAME_N_SUFFIX_CONFIG_MISMATCH: anchor says
    # seed_7 but SEEDS list contains different value.
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(
            f"chunk seed mismatch: SEEDS_FULL={SEEDS_FULL} != "
            f"[SEED_THIS_CHUNK={SEED_THIS_CHUNK}]"
        )
    if f"seed_{SEED_THIS_CHUNK}_" not in ANCHOR_NAME:
        raise AssertionError(
            f"anchor name '{ANCHOR_NAME}' does not contain "
            f"seed_{SEED_THIS_CHUNK}_; ANCHOR_NAME_CONFIG_MISMATCH"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_projection_dim_match()
        _selftest_chunk_seed_matches_anchor()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  sparsity={HIPPO_SPARSITY}  "
        f"M={M_ITEMS}  N_replay={N_REPLAY_CYCLES}  eta_c={ETA_CORTEX}  "
        f"mode={RUN_MODE}  chunk_seed={SEED_THIS_CHUNK}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    P_in = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    print(f"  [seed={seed}] N_h={N_HIPPO} (sparse k={K_HIPPO_ACTIVE}), "
          f"N_c={N_CORTEX} (dense), M={M_ITEMS}, N_replay={N_REPLAY_CYCLES}",
          flush=True)

    arms = []
    for arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY", "ARM_DIRECT_CORTEX"):
        out = run_arm(arm_name, seed, keys_raw, vals_raw, P_in, P_hc)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"recall={out['recall_cortex']:.3f} "
            f"hippo_post={out['hippo_post_zero_norm']:.2e} "
            f"cortex_norm={out['cortex_norm']:.2e} "
            f"status={out['arm_status']} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_CORTEX,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "k_hippo_active": K_HIPPO_ACTIVE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (single-seed: no cv check; raw arm comparison only)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    # Single-seed chunk: exactly 1 seed expected.
    if len(results) != 1:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arm_names = ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY", "ARM_DIRECT_CORTEX")
    # META_RULE_H cardinality_ok: 3 arms x 1 seed = 3 arms
    n_arms = len(r["arms"])
    if n_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_N_UNITS} arms, got {n_arms}")
    try:
        per = [_arm_by_name(r["arms"], name) for name in arm_names]
    except KeyError as e:
        return ("HARD_FAIL", f"Missing arm: {e}")
    for a in per:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    full = per[0]["recall_cortex"]
    nor = per[1]["recall_cortex"]
    dir_ = per[2]["recall_cortex"]
    gap = full - nor
    ratio_to_dir = full / max(dir_, 1e-9)

    # META_RULE_AF arms-must-differ: FULL and NO_REPLAY must produce
    # different recall values (otherwise the mechanism isn't acting).
    if abs(full - nor) < 1e-6:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: FULL={full} == NO_REPLAY={nor}; "
                f"arms identical -- replay mechanism not engaged")

    summary = (
        f"seed={SEED_THIS_CHUNK} "
        f"FULL={full:.3f} NO_REPLAY={nor:.3f} DIRECT={dir_:.3f} "
        f"gap_FULL_vs_NO={gap:+.3f} ratio_FULL_to_DIRECT={ratio_to_dir:.3f}"
    )

    if nor > 0.20:
        return ("HARD_FAIL",
                f"HARD_FAIL: FAIRNESS NO_REPLAY={nor:.3f} > 0.20 -- cortex not "
                f"genuinely empty; baseline leaking. {summary}")

    capacity_warn = ""
    M_over_N = float(r.get("M", 1)) / float(r.get("N_c", 1))
    if full >= 0.999 and dir_ >= 0.999 and M_over_N < 0.05:
        capacity_warn = (
            f" CAPACITY_WARN: alpha={M_over_N:.3f} < 0.05 -- consider raising M for chain-grade. "
        )

    hp_recall = full >= 0.50
    hp_gap = gap >= 0.40
    hp_ratio = ratio_to_dir >= 0.70 if dir_ > 0.05 else False

    if all([hp_recall, hp_gap, hp_ratio]):
        return ("HARD_PASS",
                f"HARD_PASS: acc(FULL)>=0.50 AND gap>=0.40 AND ratio>=0.70.{capacity_warn}"
                f"{summary}")

    if gap < 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL: gap_FULL_vs_NO_REPLAY={gap:+.3f} < 0.10; transfer "
                f"mechanism doing essentially nothing. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: transfer partial. "
            f"hp_checks=[recall={hp_recall},gap={hp_gap},ratio={hp_ratio}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver (guarded by __main__)
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] cortex_hippo_handoff_FULL_seed_{SEED_THIS_CHUNK} "
              f"N_h={N_HIPPO} N_c={N_CORTEX} "
              f"M={M_ITEMS} N_replay={N_REPLAY_CYCLES} mode={RUN_MODE}...",
              flush=True)
        result = run_seed(seed)
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # META_RULE_AH atomic-write: tmp + os.replace
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY} "
            f"M={M_ITEMS} N_replay={N_REPLAY_CYCLES} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and len(all_results[0].get("arms", [])) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


if __name__ == "__main__":
    _main()
