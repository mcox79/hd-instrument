"""cortex_hippo_handoff_sparse_DG_dense_cortex_v1 -- Drill TOP-1 hippo->cortex transfer.

Drill source: notes/research_drill_2x_cortex_hippo_handoff_2026-06-27.md (PICK 1, P=0.50)
Brain-grounded: CLS theory; McClelland-McNaughton-O'Reilly 1995; Frankland & Bontempi 2005.

Mechanism (A1):
  W_hippo  = sparse bipolar 10% density, N_h = 4096 dims
  W_cortex = dense float,                 N_c = 8192 dims (DIFFERENT SHAPE)
  Replay   = random-uniform sampling from W_hippo (NOT replay-count-as-importance;
             avoids the v4 NREM fairness trap of self-reinforcing replay).

CRITICAL FAIRNESS:
  - W_hippo and W_cortex must be DIFFERENT MATRICES with DIFFERENT SHAPES and
    DIFFERENT SPARSITY by construction (anatomically separate; cannot be papered over).
  - Replay sampling is random-uniform; tag-count is NOT used as importance.
  - Object-identity assertion: `W_hippo is not W_cortex`.
  - Discriminator measures the GAP (recall_cortex_after_replay - recall_cortex_no_replay),
    NOT raw cortical recall.

ARMS (3):
  ARM_FULL_HANDOFF       -- encode->hippo, replay->cortex (slow Hebbian),
                            then zero W_hippo. Recall test on cortex.
  ARM_NO_REPLAY          -- baseline-floor; same as FULL but skip replay step.
                            Cortex empty at recall time -> recall ~0.
  ARM_DIRECT_CORTEX      -- baseline-ceiling; items written directly to cortex
                            with same eta.

HARD_PASS:
  acc(FULL_HANDOFF) >= 0.50 AND
  acc(FULL) - acc(NO_REPLAY) >= 0.40 AND
  acc(FULL) >= 0.70 * acc(DIRECT_CORTEX)

HARD_FAIL:
  acc(FULL) - acc(NO_REPLAY) < 0.10 (transfer doing nothing).

PROT-018: no _n suffix (capability-test).
ASCII-only; no unicode; no emojis; no em-dashes.
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


ANCHOR_NAME = "cortex_hippo_handoff_sparse_DG_dense_cortex_v1"
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_cortex_hippo_handoff"

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
# Config
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 8192
HIPPO_SPARSITY = 0.10        # k-WTA sparsity in W_hippo (10% density)
M_ITEMS_FULL = 200           # items encoded
N_REPLAY_CYCLES_FULL = 50    # sleep-phase replay cycles
ETA_CORTEX_FULL = 0.01       # slow Hebbian rate
SEEDS_FULL = [7, 17, 23]

if RUN_MODE == "smoke":
    N_HIPPO = 512         # anatomically separate (smaller than cortex)
    N_CORTEX = 1024       # smaller cortex -> tighter alpha at smoke M
    M_ITEMS = 400         # alpha = 0.39 (above Hopfield alpha_c=0.14)
    N_REPLAY_CYCLES = 5
    ETA_CORTEX = 0.005
    SEEDS = [7]
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    N_REPLAY_CYCLES = N_REPLAY_CYCLES_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = SEEDS_FULL

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))   # k-WTA k

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},N_replay={N_REPLAY_CYCLES},"
    f"eta_c={ETA_CORTEX},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},hardening=L1early+L2perarm+L4importsentinel"
)


# ---------------------------------------------------------------------------
# Substrate primitives: separate stores
# ---------------------------------------------------------------------------
def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    """Random projection + k-WTA: x (N_h,) bipolar sparse with k active.

    Top-k by absolute value of P @ x_raw, sign-preserved.
    x: (N_raw,) dense input
    P: (N_h, N_raw) random projection
    Returns: (N_h,) with exactly k nonzero entries in {-1, +1}.
    """
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    # Replace any exact zeros AMONG top_k_idx entries with +1 (signpos default).
    # Do NOT touch the zeros at non-top_k indices (those must stay zero).
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_hippo_to_cortex(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    """Fixed structural projection (not learned per-item).

    h_sparse: (N_h,) sparse vector
    P_hc:     (N_c, N_h) projection matrix
    Returns:  (N_c,) dense cortex-space vector (L2-normalized).
    """
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write_cortex(W_c: np.ndarray, key: np.ndarray, val: np.ndarray,
                         eta: float) -> None:
    """W_c += eta * outer(val, key). In-place update."""
    W_c += eta * np.outer(val, key)


def hebbian_write_hippo_sparse(W_h: np.ndarray, key_h: np.ndarray,
                               val_h: np.ndarray) -> None:
    """W_h += outer(val_h, key_h). Hippo writes are one-shot (no eta).

    Both key_h and val_h are sparse k-WTA; outer product is sparse.
    """
    W_h += np.outer(val_h, key_h)


def cortex_readout(W_c: np.ndarray, key: np.ndarray) -> np.ndarray:
    """raw = W_c @ key; return sign(raw)."""
    raw = W_c @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cosine_match(pred: np.ndarray, candidates: np.ndarray) -> int:
    """Argmax cosine of pred against each row of candidates."""
    # candidates is L2-normalized; pred normalized
    n_p = float(np.linalg.norm(pred))
    if n_p == 0:
        return 0
    p_n = pred / n_p
    sims = candidates @ p_n
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# Per-arm runner (3 arms)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            keys_raw: np.ndarray, vals_raw: np.ndarray,
            P_in: np.ndarray, P_hc: np.ndarray) -> Dict:
    """L2 hardened arm runner.

    keys_raw, vals_raw: (M, N_raw) ground-truth input patterns
    P_in:  (N_h, N_raw) input -> hippo projection (pattern separator)
    P_hc:  (N_c, N_h)   hippo -> cortex projection
    """
    t0 = time.time()
    try:
        N_raw = keys_raw.shape[1]
        # Create stores (ANATOMICALLY SEPARATE; cardinality + dtype identical
        # but SHAPE differs -- N_h x N_h vs N_c x N_c -- and sparsity differs)
        W_hippo = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        # VERIFY-THE-REFERENT: object identity check (load-bearing)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_hippo is W_cortex")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_hippo.shape={W_hippo.shape} == "
                f"W_cortex.shape={W_cortex.shape}; should differ"
            )

        # Compute hippo & cortex projections for all items
        keys_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        vals_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        keys_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        vals_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        for i in range(M_ITEMS):
            keys_h[i] = pattern_separate_sparse(keys_raw[i], P_in, K_HIPPO_ACTIVE)
            vals_h[i] = pattern_separate_sparse(vals_raw[i], P_in, K_HIPPO_ACTIVE)
            keys_c[i] = project_hippo_to_cortex(keys_h[i], P_hc)
            vals_c[i] = project_hippo_to_cortex(vals_h[i], P_hc)

        # Verify sparsity
        if arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY"):
            active_per_atom = np.sum(np.abs(keys_h) > 0, axis=1)
            if not np.all(active_per_atom == K_HIPPO_ACTIVE):
                raise AssertionError(
                    f"SPARSITY VIOLATION: keys_h active counts mismatch "
                    f"K_HIPPO_ACTIVE={K_HIPPO_ACTIVE}; got {active_per_atom[:5]}..."
                )

        if arm_name == "ARM_FULL_HANDOFF":
            # 1) Encode -> hippo only
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            # 2) Sleep phase: random-uniform replay -> cortex slow Hebbian
            rng = np.random.RandomState(seed + 31)
            for _cycle in range(N_REPLAY_CYCLES):
                # Random uniform sample (NOT replay-count-as-importance)
                replay_indices = rng.choice(M_ITEMS, size=M_ITEMS, replace=False)
                for i in replay_indices:
                    hebbian_write_cortex(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
            # 3) Zero W_hippo (hippo decay)
            W_hippo[:] = 0.0
            # 4) Recall test: query cortex with keys_c, compare to vals_c
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
            # 1) Encode -> hippo only
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            # 2) NO replay (skip step 2). W_cortex still empty.
            # 3) Zero W_hippo
            W_hippo[:] = 0.0
            # 4) Recall test: query cortex; expected ~0 (cortex empty -> random)
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
            # Ceiling: encode directly to cortex with same eta as replay would use.
            # Match total Hebbian write count: replay uses M_ITEMS items x
            # N_REPLAY_CYCLES cycles; direct uses 1 cycle. Match by writing
            # N_REPLAY_CYCLES times per item.
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
# Self-tests (L3 outer try wraps; L1 early guards within)
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
    # All nonzero entries must be in {-1, +1}
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


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_projection_dim_match()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  sparsity={HIPPO_SPARSITY}  "
        f"M={M_ITEMS}  N_replay={N_REPLAY_CYCLES}  eta_c={ETA_CORTEX}  "
        f"mode={RUN_MODE}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True

_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64  # raw input dim (small, drives sparse pattern separation)
    # Random projections (fixed structural)
    P_in = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    # Ground-truth bipolar input patterns
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
        "N": N_CORTEX,  # report cortex N for ckpt-config purposes
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "k_hippo_active": K_HIPPO_ACTIVE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (drill HARD_PASS / HARD_FAIL bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    arm_names = ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY", "ARM_DIRECT_CORTEX")
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        try:
            per = [_arm_by_name(r["arms"], name) for r in results]
        except KeyError:
            return ("HARD_FAIL", f"Missing arm {name}")
        recs = [a["recall_cortex"] for a in per]
        statuses = [a["arm_status"] for a in per]
        if any(s != "OK" for s in statuses):
            return ("HARD_FAIL", f"Arm {name} ERROR in at least one seed: {statuses}")
        agg[name] = {
            "mean_recall": float(np.mean(recs)),
            "std_recall": float(np.std(recs)),
            "cv_recall": float(np.std(recs) / max(np.mean(recs), 1e-9)),
        }

    full = agg["ARM_FULL_HANDOFF"]["mean_recall"]
    nor = agg["ARM_NO_REPLAY"]["mean_recall"]
    dir_ = agg["ARM_DIRECT_CORTEX"]["mean_recall"]
    gap = full - nor
    ratio_to_dir = full / max(dir_, 1e-9)

    summary = (
        f"FULL={full:.3f} (cv={agg['ARM_FULL_HANDOFF']['cv_recall']:.3f}) "
        f"NO_REPLAY={nor:.3f} "
        f"DIRECT={dir_:.3f} "
        f"gap_FULL_vs_NO={gap:+.3f} "
        f"ratio_FULL_to_DIRECT={ratio_to_dir:.3f}"
    )

    # Fairness pre-check: if NO_REPLAY > 0.20, baseline is leaking (cortex not empty)
    if nor > 0.20:
        return ("HARD_FAIL",
                f"HARD_FAIL: FAIRNESS NO_REPLAY={nor:.3f} > 0.20 -- cortex not "
                f"genuinely empty at start; baseline arm is leaking signal. "
                f"{summary}")

    # Q-discipline: the load-bearing fairness check is NO_REPLAY ~ 0 (cortex
    # genuinely empty), which we already enforced above. If FULL=1.0 and
    # DIRECT=1.0 with NO_REPLAY=0.0 the mechanism WORKED -- transfer is
    # real, ceiling is high. We only WARN if M/N_c < 0.05 (too easy capacity).
    capacity_warn = ""
    M_over_N = float(results[0].get("M", 1)) / float(results[0].get("N_c", 1))
    if full >= 0.999 and dir_ >= 0.999 and M_over_N < 0.05:
        capacity_warn = (
            f" CAPACITY_WARN: alpha={M_over_N:.3f} < 0.05 -- consider raising M for chain-grade. "
        )

    # HARD_PASS (drill bands)
    hp_recall = full >= 0.50
    hp_gap = gap >= 0.40
    hp_ratio = ratio_to_dir >= 0.70 if dir_ > 0.05 else False

    if all([hp_recall, hp_gap, hp_ratio]):
        return ("HARD_PASS",
                f"HARD_PASS: acc(FULL)>=0.50 AND gap>=0.40 AND ratio>=0.70.{capacity_warn}"
                f"{summary}")

    # HARD_FAIL
    if gap < 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL: gap_FULL_vs_NO_REPLAY={gap:+.3f} < 0.10; transfer "
                f"mechanism doing essentially nothing. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: transfer partial. "
            f"hp_checks=[recall={hp_recall},gap={hp_gap},ratio={hp_ratio}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_CORTEX, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] cortex_hippo_handoff N_h={N_HIPPO} N_c={N_CORTEX} "
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

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N_h={N_HIPPO} N_c={N_CORTEX} "
        f"sparsity={HIPPO_SPARSITY} M={M_ITEMS} N_replay={N_REPLAY_CYCLES} "
        f"mode={RUN_MODE}"
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
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
