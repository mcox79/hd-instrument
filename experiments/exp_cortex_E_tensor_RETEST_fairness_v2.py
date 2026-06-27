"""cortex_E_tensor_RETEST_fairness_v2 -- Wave 1.6 ANCHOR 1 (fairness re-test).

USER 2026-06-26 FAIRNESS AUDIT motivation (load-bearing):
  v1 cell (exp_cortex_E_tensor_HARDER_REGIME_v1) HARD_FAILed with
  E_GATED rec_old=0.500 < RANDOM rec_old=0.717 < BASELINE_mag rec_old=0.800
  AND cor(E,|W|)=0.760 -- TWO fairness concerns surfaced:

  FIX A (explicit retrieval schedule):
    v1's eval queried a RANDOM subset of M_OLD without tagging which atoms
    had actually been RETRIEVED during the J continual cycles. So we couldn't
    tell whether E_GATED was failing on RETRIEVED-old (the load-bearing
    question) or on UNRETRIEVED-old (mechanically guaranteed to fail since
    those atoms got NO bumps and stayed at seed_new which decays toward 0).

    v2 partitions OLD into RETRIEVED (n_use indices, get N bumps over J cycles)
    and UNRETRIEVED (M_OLD - n_use indices, get 0 bumps over J cycles). Eval
    reports rec_old_RETRIEVED and rec_old_UNRETRIEVED separately. The load-
    bearing PASS condition is:
       E_GATED.rec_old_RETRIEVED >= 0.90  (E preserves what was used)
       E_GATED.rec_old_UNRETRIEVED ~= RANDOM.rec_old (E doesn't pretend to know)

  FIX B (decouple EWMA bump from cosine magnitude):
    v1 had cor(E,|W|)=0.76 because (hypothesis) high-|W| atoms retrieve
    correctly more often, get bumped more often, and EWMA E saturates near
    1.0 for them while staying low for low-|W| atoms -- coupling E to |W|.

    v2 uses a CONSTANT additive bump (+1.0 per retrieval HIT) regardless of
    cosine match value, and a CONSTANT linear decay per cycle. E becomes a
    HIT-COUNT proxy that is structurally decoupled from cosine score
    magnitude. PASS requires cor(E,|W|) < 0.3.

    If cor(E,|W|) > 0.5 at smoke after Fix B, the EWMA-as-importance design
    is fundamentally wrong-shaped (E is just a re-labeled magnitude); STOP
    smoke + route back to research with diagnosis.

ARMS (4 mandatory, per Research Wave 1.6 spec):
  ARM_BASELINE_NO_DOWNSCALE      -- rail; no pruning at all (Hebbian as-is).
  ARM_E_GATED_RETEST             -- Fix A + Fix B applied.
  ARM_RANDOM_GATED               -- control; random pruning of same count.
  ARM_BASELINE_MAG_GATED         -- NEW control; magnitude-quantile pruning
                                    (tests "maybe magnitude was the right
                                    signal all along" -- if MAG_GATED beats
                                    E_GATED_RETEST, retire the E mechanism).

INSTRUMENTATION (per arm):
  recall_old_RETRIEVED, recall_old_UNRETRIEVED, recall_recent,
  cor_E_magnitude, n_downscaled, downscale_frac_actual,
  E_min/E_max/E_mean (on RETRIEVED + UNRETRIEVED subsets separately),
  hit_count_per_retrieved_atom (verifies Fix B additive bump fires).

SUBSTRATE-ONLY DECODE GATE:
  n_llm_calls = 0 by structural-guarantee. Decode is sign(W @ key) cosine
  cleanup against value matrix.

PROT-018: N=1024 (no _n suffix in anchor; capability-test cell).
PROT-019: no _n>=4096 suffix -> no PROT-019 floor.

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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Fix-B E-config: ADDITIVE bump + LINEAR decay (decoupled from cosine)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EConfigV2:
    """E v2 (Fix B): hit-count proxy.

    bump_amount:  CONSTANT amount added per retrieval HIT (default +1.0).
                  No cosine scaling; no EWMA saturation.
    decay_amount: CONSTANT amount SUBTRACTED per cycle (linear, not multiplicative).
                  Default 0.001 per cycle -> 1.0 cycle-budget over J=1000.
    seed_new:     initial E[i] for freshly-written atoms (0.0 here; v1 used 0.5).
                  Starting at 0.0 ensures retrieved/unretrieved separation is
                  driven by bump dynamics, not by initial seed.
    floor:        lower clamp on E[i].
    """
    bump_amount: float = 1.0
    decay_amount: float = 0.001
    seed_new: float = 0.0
    floor: float = 0.0


def init_E(n_atoms: int) -> np.ndarray:
    return np.zeros(n_atoms, dtype=np.float64)


def seed_on_write_v2(E: np.ndarray, idx: int, cfg: EConfigV2) -> None:
    """Set E[idx] to seed_new on first write."""
    if E[idx] < cfg.seed_new:
        E[idx] = cfg.seed_new


def bump_on_retrieval_v2(E: np.ndarray, idx: int, hit: bool,
                         cfg: EConfigV2) -> None:
    """Fix B: ADDITIVE constant bump on hit; NO cosine scaling."""
    if hit:
        E[idx] = E[idx] + cfg.bump_amount


def decay_E_linear(E: np.ndarray, cfg: EConfigV2) -> None:
    """Linear decay: subtract constant per cycle, floor at cfg.floor."""
    np.subtract(E, cfg.decay_amount, out=E)
    np.clip(E, cfg.floor, None, out=E)


def correlation_E_vs_magnitude(E: np.ndarray, atom_norms: np.ndarray) -> float:
    if E.shape[0] != atom_norms.shape[0]:
        raise ValueError(
            f"shape mismatch: E={E.shape}, atom_norms={atom_norms.shape}"
        )
    if np.std(E) <= 1e-12 or np.std(atom_norms) <= 1e-12:
        return 0.0
    return float(np.corrcoef(E, atom_norms)[0, 1])


ANCHOR_NAME = "cortex_E_tensor_RETEST_fairness_v2"
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# CLI / run mode
# ---------------------------------------------------------------------------
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
# Production constants
# ---------------------------------------------------------------------------
N_FULL = 1024              # smaller than v1 (was 2048) -- 4 arms x 3 seeds budget
M_OLD_FULL = 600           # alpha_old = 0.586 (hard but not saturating)
M_RECENT_FULL = 400        # total alpha = 0.977 (above Hopfield alpha_c=0.138)
USE_FRAC_FULL = 0.30       # 30% of M_OLD get retrieved during J cycles
N_RETRIEVAL_PASSES_FULL = 1000
DOWNSCALE_SCALE = 0.20
DOWNSCALE_FRAC = 0.30      # target frac for RANDOM + MAG_GATED count match
E_THRESHOLD = 0.5          # with bump=1.0 + decay=0.001/cycle, a single late
                           # hit yields E ~ 1.0; chronic-no-hit decays to 0.
                           # Threshold 0.5 separates "ever hit recently" vs
                           # "long-decayed / never hit".
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200       # per-subset queries (RETRIEVED + UNRETRIEVED + RECENT)

if RUN_MODE == "smoke":
    N = 256
    M_OLD = 150
    M_RECENT = 100
    USE_FRAC = 0.30
    N_RETRIEVAL_PASSES = 500
    SEEDS = [7]
    N_QUERIES = 50
else:
    N = N_FULL
    M_OLD = M_OLD_FULL
    M_RECENT = M_RECENT_FULL
    USE_FRAC = USE_FRAC_FULL
    N_RETRIEVAL_PASSES = N_RETRIEVAL_PASSES_FULL
    SEEDS = SEEDS_FULL
    N_QUERIES = N_QUERIES_FULL

M_TOTAL = M_OLD + M_RECENT
ALPHA = M_TOTAL / N
N_USE = max(1, int(round(USE_FRAC * M_OLD)))    # |RETRIEVED| subset size

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N},M_OLD={M_OLD},M_RECENT={M_RECENT},"
    f"USE_FRAC={USE_FRAC},N_PASSES={N_RETRIEVAL_PASSES},"
    f"DOWNSCALE_SCALE={DOWNSCALE_SCALE},DOWNSCALE_FRAC={DOWNSCALE_FRAC},"
    f"E_THRESHOLD={E_THRESHOLD},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"N_QUERIES={N_QUERIES},RUN_MODE={RUN_MODE}"
)


# ---------------------------------------------------------------------------
# Pattern generation: bipolar keys/values
# ---------------------------------------------------------------------------
def generate_pairs(M_count: int, N_dim: int, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.RandomState(seed)
    keys = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_count, N_dim)).astype(np.float64)
    return keys, values


def build_W_from_pairs(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    return values.T @ keys


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray,
                  query_idx: np.ndarray, all_values: np.ndarray) -> float:
    N_dim = keys.shape[1]
    if len(query_idx) == 0:
        return float("nan")
    n_hits = 0
    for i in query_idx:
        pred = predict(W, keys[i])
        sims = all_values @ pred / float(N_dim)
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(query_idx))


# ---------------------------------------------------------------------------
# Substrate setup: Fix A explicit retrieval schedule
# ---------------------------------------------------------------------------
def setup_substrate(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                        np.ndarray, np.ndarray, np.ndarray,
                                        EConfigV2]:
    """Build keys/values, ingest old, run J cycles with EXPLICIT retrieval
    schedule (Fix A), then ingest recent.

    Returns: (W, all_keys, all_values, E, retrieved_idx, unretrieved_idx, cfg)
      retrieved_idx: indices of OLD atoms that got retrievals (n_use of them)
      unretrieved_idx: indices of OLD atoms that did NOT get retrievals
        (M_OLD - n_use of them); these stayed at seed_new and then decayed.
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = EConfigV2()
    E = init_E(M_TOTAL)

    # Ingest OLD via Hebbian; seed E on write.
    W = build_W_from_pairs(keys_old, values_old)
    for i in range(M_OLD):
        seed_on_write_v2(E, i, cfg)

    # Fix A: deterministically partition OLD into RETRIEVED vs UNRETRIEVED.
    rng = np.random.RandomState(seed + 401)
    retrieved_idx = rng.choice(M_OLD, size=N_USE, replace=False)
    retrieved_idx.sort()
    unretrieved_mask = np.ones(M_OLD, dtype=bool)
    unretrieved_mask[retrieved_idx] = False
    unretrieved_idx = np.where(unretrieved_mask)[0]

    # J cycles: ONLY retrieved_idx atoms get bump opportunities.
    # Each cycle: batch-predict each retrieved atom, bump on hit (Fix B
    # constant +bump_amount), then decay E for ALL atoms (linear).
    for _pass in range(N_RETRIEVAL_PASSES):
        K_use = all_keys[retrieved_idx]          # (N_USE, N)
        raw = K_use @ W.T                         # (N_USE, N)
        preds = np.sign(raw)
        preds[preds == 0] = 1.0
        sims = preds @ all_values.T / float(N)   # (N_USE, M_TOTAL)
        argmaxes = np.argmax(sims, axis=1)
        hits_mask = (argmaxes == retrieved_idx)
        for i, ui in enumerate(retrieved_idx):
            bump_on_retrieval_v2(E, ui, bool(hits_mask[i]), cfg)
        decay_E_linear(E, cfg)

    # Ingest RECENT into W; seed E on write.
    W = W + build_W_from_pairs(keys_rec, values_rec)
    for j in range(M_RECENT):
        idx = M_OLD + j
        seed_on_write_v2(E, idx, cfg)

    return W, all_keys, all_values, E, retrieved_idx, unretrieved_idx, cfg


# ---------------------------------------------------------------------------
# Arm runner (4 arms, including new BASELINE_MAG_GATED)
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: "Tuple | None" = None) -> Dict:
    t0 = time.time()
    if shared is None:
        W_base, all_keys, all_values, E, retrieved_idx, unretrieved_idx, cfg = setup_substrate(seed)
    else:
        W_base, all_keys, all_values, E, retrieved_idx, unretrieved_idx, cfg = shared
    W = W_base.copy()
    W_norm_pre = float(np.linalg.norm(W))

    n_downscaled = 0
    if arm_name == "ARM_BASELINE_NO_DOWNSCALE":
        # Rail: do NOTHING. No pruning at all.
        n_downscaled = 0
    elif arm_name == "ARM_E_GATED_RETEST":
        # Prune atoms with E < threshold.
        low_E_atoms = np.where(E < E_THRESHOLD)[0]
        n_downscaled = int(len(low_E_atoms))
        for idx in low_E_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_RANDOM_GATED":
        # Match count to what E_GATED would prune.
        n_target = int(np.sum(E < E_THRESHOLD))
        if n_target <= 0:
            n_target = max(1, int(round(DOWNSCALE_FRAC * M_TOTAL)))
        rng = np.random.RandomState(seed + 7777)
        rand_atoms = rng.choice(M_TOTAL, size=n_target, replace=False)
        n_downscaled = n_target
        for idx in rand_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_BASELINE_MAG_GATED":
        # Magnitude-quantile prune (Wave-1 sanity rail). Tests "maybe
        # magnitude was the right importance signal all along".
        atom_readback = np.linalg.norm(all_keys @ W.T, axis=1)
        n_target = int(np.sum(E < E_THRESHOLD))
        if n_target <= 0:
            n_target = max(1, int(round(DOWNSCALE_FRAC * M_TOTAL)))
        # Pick the n_target ATOMS with the SMALLEST readback magnitude.
        low_idx = np.argsort(atom_readback)[:n_target]
        n_downscaled = int(len(low_idx))
        for idx in low_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    W_norm_post = float(np.linalg.norm(W))

    # Recall measurement: RETRIEVED-old vs UNRETRIEVED-old + RECENT (Fix A).
    rng_eval = np.random.RandomState(seed + 503)
    n_q_ret = min(N_QUERIES, len(retrieved_idx))
    n_q_unret = min(N_QUERIES, len(unretrieved_idx))
    n_q_rec = min(N_QUERIES, M_RECENT)
    ret_query = rng_eval.choice(retrieved_idx, size=n_q_ret, replace=False)
    unret_query = rng_eval.choice(unretrieved_idx, size=n_q_unret, replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_q_rec, replace=False) + M_OLD

    recall_old_retrieved = recall_subset(W, all_keys, ret_query, all_values)
    recall_old_unretrieved = recall_subset(W, all_keys, unret_query, all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    # Substrate-readback magnitude per atom.
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_E_W = correlation_E_vs_magnitude(E, atom_norms)

    # E stats on RETRIEVED vs UNRETRIEVED (verifies Fix B separation).
    E_retrieved = E[retrieved_idx]
    E_unretrieved = E[unretrieved_idx]

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "recall_old_RETRIEVED": float(recall_old_retrieved),
        "recall_old_UNRETRIEVED": float(recall_old_unretrieved),
        "recall_recent": float(recall_recent),
        "W_norm_pre": W_norm_pre,
        "W_norm_post": W_norm_post,
        "cor_E_magnitude": float(cor_E_W),
        "n_downscaled": int(n_downscaled),
        "downscale_frac_actual": float(n_downscaled) / float(M_TOTAL),
        "wall_s": float(elapsed),
        "E_min": float(np.min(E)),
        "E_max": float(np.max(E)),
        "E_mean": float(np.mean(E)),
        "E_retrieved_mean": float(np.mean(E_retrieved)),
        "E_retrieved_min": float(np.min(E_retrieved)),
        "E_unretrieved_mean": float(np.mean(E_unretrieved)),
        "E_unretrieved_max": float(np.max(E_unretrieved)),
        "n_retrieved": int(len(retrieved_idx)),
        "n_unretrieved": int(len(unretrieved_idx)),
        "frac_below_E_threshold": float(np.mean(E < E_THRESHOLD)),
    }


# ---------------------------------------------------------------------------
# Self-tests (Fix B mechanism unit-test FIRST per handoff section 7a)
# ---------------------------------------------------------------------------
def _selftest_init():
    E = init_E(16)
    assert E.shape == (16,)
    assert np.all(E == 0.0)
    return True


def _selftest_seed_and_bump_constant():
    cfg = EConfigV2()
    E = init_E(4)
    seed_on_write_v2(E, 0, cfg)
    assert E[0] == cfg.seed_new  # 0.0 by default
    # Fix B: constant +1.0 bump on hit, regardless of cosine.
    bump_on_retrieval_v2(E, 0, True, cfg)
    assert abs(E[0] - 1.0) < 1e-9, f"expected 1.0 after one hit, got {E[0]}"
    bump_on_retrieval_v2(E, 0, True, cfg)
    assert abs(E[0] - 2.0) < 1e-9, f"expected 2.0 after two hits, got {E[0]}"
    # No bump on miss.
    bump_on_retrieval_v2(E, 1, False, cfg)
    assert E[1] == cfg.seed_new
    return True


def _selftest_decay_linear():
    cfg = EConfigV2()
    E = np.array([1.0, 0.5, 0.0005, 0.0])
    decay_E_linear(E, cfg)
    # After one cycle: [0.999, 0.499, 0.0, 0.0] (floored at 0)
    assert abs(E[0] - 0.999) < 1e-9
    assert abs(E[1] - 0.499) < 1e-9
    assert E[2] == 0.0  # floored
    assert E[3] == 0.0  # floored
    return True


def _selftest_decoupling_synthetic():
    """Fix B synthetic check: under additive+linear dynamics, an atom with
    HIGH hit-count has HIGH E independent of any cosine magnitude.

    Construct two atoms: atom 0 gets 5 hits over 100 cycles; atom 1 gets 0
    hits. After dynamics, E[0] should be ~5 - 100*0.001 ~ 4.9 and E[1] ~ 0.
    """
    cfg = EConfigV2()
    E = init_E(2)
    for cycle in range(100):
        if cycle in (10, 30, 50, 70, 90):
            bump_on_retrieval_v2(E, 0, True, cfg)
        decay_E_linear(E, cfg)
    # E[0] = 5 * 1.0 - 100 * 0.001 = 4.9 (assuming no clipping; floor 0)
    assert 4.5 < E[0] < 5.0, f"E[0] expected ~4.9, got {E[0]}"
    assert E[1] == 0.0, f"E[1] expected 0.0, got {E[1]}"
    return True


def _selftest_correlation_zero_for_constant_E():
    E = np.ones(8)
    atom_norms = np.abs(np.random.RandomState(0).randn(8))
    c = correlation_E_vs_magnitude(E, atom_norms)
    assert c == 0.0
    return True


def _instrumentation_selftest():
    _selftest_init()
    _selftest_seed_and_bump_constant()
    _selftest_decay_linear()
    _selftest_decoupling_synthetic()
    _selftest_correlation_zero_for_constant_E()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J={N_RETRIEVAL_PASSES}  "
        f"E_THRESHOLD={E_THRESHOLD}  N_USE={N_USE}  mode={RUN_MODE}",
        flush=True,
    )


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] setup_substrate (J={N_RETRIEVAL_PASSES} cycles, "
          f"N_USE={N_USE} of M_OLD={M_OLD})...", flush=True)
    t_setup = time.time()
    shared = setup_substrate(seed)
    print(f"  [seed={seed}] setup_substrate done in {time.time()-t_setup:.1f}s",
          flush=True)
    arms = []
    for arm_name in ["ARM_BASELINE_NO_DOWNSCALE",
                     "ARM_E_GATED_RETEST",
                     "ARM_RANDOM_GATED",
                     "ARM_BASELINE_MAG_GATED"]:
        out = run_arm(arm_name, seed, shared=shared)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"rec_RETR={out['recall_old_RETRIEVED']:.3f} "
            f"rec_UNRETR={out['recall_old_UNRETRIEVED']:.3f} "
            f"rec_rec={out['recall_recent']:.3f} "
            f"cor_E_W={out['cor_E_magnitude']:.3f} "
            f"n_down={out['n_downscaled']} ({out['downscale_frac_actual']:.2f}) "
            f"E_ret={out['E_retrieved_mean']:.3f} "
            f"E_unret={out['E_unretrieved_mean']:.3f} "
            f"wall={out['wall_s']:.1f}s",
            flush=True,
        )
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N,
        "M_OLD": M_OLD,
        "M_RECENT": M_RECENT,
        "alpha": float(ALPHA),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "n_queries": int(N_QUERIES),
        "n_use": int(N_USE),
        "downscale_scale": DOWNSCALE_SCALE,
        "downscale_frac": DOWNSCALE_FRAC,
        "e_threshold": E_THRESHOLD,
        "use_frac": USE_FRAC,
        "n_passes": N_RETRIEVAL_PASSES,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (Wave-1.6 fairness pre-reg bands; LOAD-BEARING per USER)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    arm_names = ["ARM_BASELINE_NO_DOWNSCALE", "ARM_E_GATED_RETEST",
                 "ARM_RANDOM_GATED", "ARM_BASELINE_MAG_GATED"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_retr = [a["recall_old_RETRIEVED"] for a in per]
        rec_unretr = [a["recall_old_UNRETRIEVED"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_E_magnitude"] for a in per]
        wnorm = [a["W_norm_post"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        agg[name] = {
            "mean_rec_RETRIEVED": float(np.mean(rec_retr)),
            "std_rec_RETRIEVED": float(np.std(rec_retr)),
            "cv_rec_RETRIEVED": float(np.std(rec_retr) / max(abs(np.mean(rec_retr)), 1e-9)),
            "mean_rec_UNRETRIEVED": float(np.mean(rec_unretr)),
            "mean_rec_recent": float(np.mean(rec_rec)),
            "mean_cor_E_W": float(np.mean(cor)),
            "mean_W_norm": float(np.mean(wnorm)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL", "HARD_FAIL: substrate-only-decode gate violated.")

    e = agg["ARM_E_GATED_RETEST"]
    rnd = agg["ARM_RANDOM_GATED"]
    base = agg["ARM_BASELINE_NO_DOWNSCALE"]
    mag = agg["ARM_BASELINE_MAG_GATED"]

    # Load-bearing fairness deltas.
    delta_retrieved = e["mean_rec_RETRIEVED"] - rnd["mean_rec_RETRIEVED"]
    delta_unretrieved = abs(e["mean_rec_UNRETRIEVED"] - rnd["mean_rec_UNRETRIEVED"])
    e_vs_mag_retrieved = e["mean_rec_RETRIEVED"] - mag["mean_rec_RETRIEVED"]

    summary = (
        f"E_GATED(retr={e['mean_rec_RETRIEVED']:.3f},"
        f"unretr={e['mean_rec_UNRETRIEVED']:.3f},"
        f"rec={e['mean_rec_recent']:.3f},"
        f"cor={e['mean_cor_E_W']:.3f},cv={e['cv_rec_RETRIEVED']:.3f},"
        f"n_down={e['mean_n_downscaled']:.0f}); "
        f"RANDOM(retr={rnd['mean_rec_RETRIEVED']:.3f},"
        f"unretr={rnd['mean_rec_UNRETRIEVED']:.3f}); "
        f"MAG(retr={mag['mean_rec_RETRIEVED']:.3f},"
        f"unretr={mag['mean_rec_UNRETRIEVED']:.3f}); "
        f"NO_DOWNSCALE(retr={base['mean_rec_RETRIEVED']:.3f},"
        f"unretr={base['mean_rec_UNRETRIEVED']:.3f}); "
        f"d_retr_E_vs_RND={delta_retrieved:+.3f} "
        f"d_unretr_abs={delta_unretrieved:.3f} "
        f"d_E_vs_MAG_retr={e_vs_mag_retrieved:+.3f}"
    )

    if not np.isfinite(e["mean_W_norm"]):
        return ("HARD_FAIL", f"HARD_FAIL: E_GATED W_norm non-finite. {summary}")

    # ---- HARD_FAIL gates (USER fairness audit; load-bearing) ----

    # Fix B failure: cor(E,|W|) still high after constant-bump dynamics.
    # If >= 0.5, the EWMA design is fundamentally wrong-shaped (E is just |W|).
    if e["mean_cor_E_W"] > 0.5:
        return ("HARD_FAIL",
                f"HARD_FAIL: Fix B failed. cor(E,|W|)={e['mean_cor_E_W']:.3f} "
                f">= 0.5 -- E mechanism is fundamentally wrong-shaped (E "
                f"reduces to a magnitude proxy after constant-bump + linear "
                f"decay). Route back to research for alternative selectivity "
                f"signals. {summary}")

    # Fix A failure: E_GATED prunes the RETRIEVED-old subset.
    # PASS requires RETRIEVED preserved >= 0.90.
    if e["mean_rec_RETRIEVED"] < 0.90:
        return ("HARD_FAIL",
                f"HARD_FAIL: Fix A failed. E_GATED preserves only "
                f"{e['mean_rec_RETRIEVED']:.3f} of RETRIEVED-old "
                f"(< 0.90 fairness floor); the mechanism does NOT preserve "
                f"the atoms it should. {summary}")

    # MAG_GATED beats E_GATED on RETRIEVED-old by >= 5pp -> magnitude wins.
    if e_vs_mag_retrieved < -0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: ARM_BASELINE_MAG_GATED beats E_GATED on "
                f"RETRIEVED-old by {-e_vs_mag_retrieved:.3f} (>= 0.05). "
                f"Magnitude IS the right importance signal; retire the E "
                f"mechanism. {summary}")

    # ---- HARD_PASS gates ----
    # E_GATED preserves RETRIEVED >= 0.90 AND prunes UNRETRIEVED similarly to
    # RANDOM (within 0.10) AND beats MAG_GATED on RETRIEVED by >= 0.05.
    hp_retrieved = e["mean_rec_RETRIEVED"] >= 0.90
    hp_unretrieved_fair = delta_unretrieved <= 0.10
    hp_beats_mag = e_vs_mag_retrieved >= 0.05
    hp_cor = e["mean_cor_E_W"] < 0.30  # USER pre-reg: cor < 0.3 = decoupled
    hp_cv = e["cv_rec_RETRIEVED"] <= 0.10

    if all([hp_retrieved, hp_unretrieved_fair, hp_beats_mag, hp_cor, hp_cv]):
        return ("HARD_PASS",
                f"HARD_PASS: E mechanism preserves RETRIEVED, treats "
                f"UNRETRIEVED ~ RANDOM, beats MAG, cor(E,|W|)<0.3, cv<=0.10. "
                f"{summary}")

    # MIDDLE_BAND: Fix A passes (>=0.90 retrieved) AND Fix B passes (cor<0.3)
    # but other gates fail (e.g., doesn't beat MAG by 5pp, or unretrieved
    # fairness slightly off).
    if hp_retrieved and hp_cor:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: Fix A + Fix B passed but full PASS gate not "
                f"cleared. hp_checks=[retr={hp_retrieved},"
                f"unretr_fair={hp_unretrieved_fair},beats_mag={hp_beats_mag},"
                f"cor={hp_cor},cv={hp_cv}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: E mechanism does not clear PASS or MIDDLE bands. "
            f"hp_checks=[retr={hp_retrieved},unretr_fair={hp_unretrieved_fair},"
            f"beats_mag={hp_beats_mag},cor={hp_cor},cv={hp_cv}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_OLD": M_OLD, "M_RECENT": M_RECENT,
              "J": N_RETRIEVAL_PASSES, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] cortex_E v2 RETEST N={N} alpha={ALPHA:.3f} "
          f"J={N_RETRIEVAL_PASSES} N_USE={N_USE} mode={RUN_MODE}...",
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
        f"n_seeds={len(all_results)} N={N} M_OLD={M_OLD} M_RECENT={M_RECENT} "
        f"alpha={ALPHA:.3f} J={N_RETRIEVAL_PASSES} N_USE={N_USE} "
        f"mode={RUN_MODE} downscale_scale={DOWNSCALE_SCALE} "
        f"e_threshold={E_THRESHOLD}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "M_OLD": M_OLD,
    "M_RECENT": M_RECENT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
    "n_use": int(N_USE),
    "n_passes": N_RETRIEVAL_PASSES,
    "downscale_scale": float(DOWNSCALE_SCALE),
    "downscale_frac": float(DOWNSCALE_FRAC),
    "e_threshold": float(E_THRESHOLD),
    "use_frac": float(USE_FRAC),
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
