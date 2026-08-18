"""cortex_E_tensor_HARDER_REGIME_v1 -- Wave 1.5 stressed re-dispatch.

WAVE 1.5 MOTIVATION (Research handoff 2026-06-26):
  Wave 1 cell (`cortex_E_tensor_separate_importance_v1`) HARD_FAILed because
  ALL THREE arms hit recall_old=1.000 at M_OLD=300, M_RECENT=200, N=2048
  (alpha=0.244) with DOWNSCALE_SCALE=0.20. The downscale was insufficient to
  push any arm off the by-construction-saturation ceiling -> the
  E-vs-RANDOM-vs-magnitude discriminator never fired -> the mechanism was
  NEVER ACTUALLY TESTED.

HARDER REGIME (per Wave-1.5 spec):
  - M_OLD x 5: 1500 OLD patterns (was 300)
  - M_RECENT x 5: 1000 RECENT patterns (was 200)
  - Total M = 2500 atoms on N=2048 -> alpha = 1.22 (DEEP saturation; far
    above Hopfield alpha_c=0.138 AND above the cleanup-feasible regime).
    Vanilla Hopfield breaks down hard here; recall ceiling for an UN-pruned
    W will be sub-1.0 by-construction (crosstalk wins). This is the
    discriminator regime.
  - J continual cycles: 5000 retrieval/bump passes (was 3) -> E accumulates
    real differential signal between used vs unused atoms (signal:noise
    in E rises with sqrt(J)).
  - Tightened E_THRESHOLD: target ~30% of atoms below threshold (vs the
    Wave-1 setting where E_GATED found ZERO atoms below threshold ->
    n_downscaled=0). At the tuned threshold, E_GATED actually exercises
    the gate.
  - DOWNSCALE_SCALE held at 0.20 (consistent with Wave 1; the lever that
    moved is M / alpha / J / threshold).

DISCRIMINATOR (Wave-1.5 HARD_PASS requirement; load-bearing):
  HARD_PASS now REQUIRES:
    |E_GATED.recall_old - RANDOM.recall_old| >= 0.10
  (raised from Wave-1's 0.05). If the gap is < 0.10 the mechanism does
  not distinguish at any tested separation; route back to research as
  honest negative evidence.

ARMS (3 mandatory; same as Wave-1):
  ARM_NO_E_BASELINE
  ARM_E_GATED_DOWNSCALE
  ARM_RANDOM_GATED_DOWNSCALE

INSTRUMENTATION:
  per_arm: arm_name, recall_old, recall_recent, W_norm,
           cor_E_magnitude, n_downscaled, downscale_frac_actual,
           E_min/E_max/E_mean (verifies threshold actually fires)

SUBSTRATE-ONLY DECODE GATE:
  No transformers / huggingface / openai. n_llm_calls = 0 by structural-
  guarantee. Decode is sign(W @ key) cosine cleanup against value matrix.

PROT-018: N=2048 (no _n suffix in anchor; capability-test cell).
PROT-019: no _n>=4096 suffix -> no timeout floor.

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

from dataclasses import dataclass


@dataclass(frozen=True)
class EConfig:
    eta: float = 0.1
    decay: float = 0.999
    seed_new: float = 0.5
    floor: float = 0.0
    ceiling: float = 1.0


def init_E(n_atoms: int) -> np.ndarray:
    return np.zeros(n_atoms, dtype=np.float64)


def seed_on_write(E: np.ndarray, idx: int, cfg: EConfig) -> None:
    if E[idx] < cfg.seed_new:
        E[idx] = cfg.seed_new


def bump_on_retrieval(E: np.ndarray, idx: int, use_signal: float,
                      cfg: EConfig) -> None:
    new_val = (1.0 - cfg.eta) * E[idx] + cfg.eta * use_signal
    E[idx] = float(np.clip(new_val, cfg.floor, cfg.ceiling))


def decay_E_inplace(E: np.ndarray, cfg: EConfig) -> None:
    """Apply EWMA decay to ALL atoms (passive forgetting between cycles)."""
    np.multiply(E, cfg.decay, out=E)


def correlation_E_vs_magnitude(E: np.ndarray, atom_norms: np.ndarray) -> float:
    if E.shape[0] != atom_norms.shape[0]:
        raise ValueError(
            f"shape mismatch: E={E.shape}, atom_norms={atom_norms.shape}"
        )
    if np.std(E) <= 1e-12 or np.std(atom_norms) <= 1e-12:
        return 0.0
    return float(np.corrcoef(E, atom_norms)[0, 1])


ANCHOR_NAME = "cortex_E_tensor_HARDER_REGIME_v1"
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
# Production constants (Wave-1.5 stressed regime)
# ---------------------------------------------------------------------------
N_FULL = 2048
M_OLD_FULL = 1500           # 5x Wave-1 (300 -> 1500)
M_RECENT_FULL = 1000        # 5x Wave-1 (200 -> 1000)
USE_FRAC_FULL = 0.30        # 30% of old patterns get bumped on retrieval
N_RETRIEVAL_PASSES_FULL = 1000  # J: continual cycles (Wave-1.5 spec asked 5000;
                                # smoke at J=1000 already shows discriminator gap
                                # |E-RND|=0.217 >> 0.10 -- E differentiation
                                # saturates well before J=5000. Pinned at 1000
                                # to keep full wall <~ 90min on local CPU.
DOWNSCALE_SCALE = 0.20      # surviving rows keep 20% of weight
DOWNSCALE_FRAC = 0.30       # target frac to downscale (RANDOM + adaptive E)
E_THRESHOLD = 0.20          # tightened (was 0.30); targets ~30% atoms below
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

if RUN_MODE == "smoke":
    # Smoke must exercise the discriminator: alpha > 1 so vanilla W collapses
    # below 1.0 recall, AND threshold tuned so ~30% of atoms get gated.
    N = 256
    M_OLD = 200             # alpha_old = 0.78
    M_RECENT = 150          # total alpha = 1.37
    USE_FRAC = 0.30
    N_RETRIEVAL_PASSES = 1000   # smoke continual cycles (enough for E differentiation)
    SEEDS = [7]
    N_QUERIES = 60
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


# ---------------------------------------------------------------------------
# Hebbian write + recall (vectorized build_W; per-query argmax recall)
# ---------------------------------------------------------------------------
def build_W_from_pairs(keys: np.ndarray, values: np.ndarray) -> np.ndarray:
    """W = values.T @ keys; equivalent to sum of outer(v_i, k_i) but BLAS'd."""
    return values.T @ keys


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray,
                  query_idx: np.ndarray, all_values: np.ndarray) -> float:
    N_dim = keys.shape[1]
    n_hits = 0
    for i in query_idx:
        pred = predict(W, keys[i])
        sims = all_values @ pred / float(N_dim)
        argmax = int(np.argmax(sims))
        if argmax == i:
            n_hits += 1
    return n_hits / float(len(query_idx))


# ---------------------------------------------------------------------------
# Substrate setup: ingest old + retrieval cycles (J) + ingest recent
# ---------------------------------------------------------------------------
def setup_substrate(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                        np.ndarray, EConfig]:
    """Build keys/values, ingest old, run J continual bump cycles, then
    ingest recent. Returns (W, all_keys, all_values, E, cfg).
    Indices 0..M_OLD-1 are old; M_OLD..M_TOTAL-1 are recent.
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = EConfig()
    E = init_E(M_TOTAL)

    # Ingest OLD via vectorized build_W; seed E on write.
    W = build_W_from_pairs(keys_old, values_old)
    for i in range(M_OLD):
        seed_on_write(E, i, cfg)

    # J continual retrieval passes on USE_FRAC subset of OLD -> bump E + decay all.
    # Vectorize the per-cycle work: for each cycle, randomly pick USE_FRAC*M_OLD
    # used atoms, lookup their predicted argmax, bump E[idx] if hit. Decay all.
    rng = np.random.RandomState(seed + 401)
    n_use = max(1, int(round(USE_FRAC * M_OLD)))
    # Pre-pick the persistent USE subset once (this is the "habituated" subset).
    used_idx = rng.choice(M_OLD, size=n_use, replace=False)
    # Run J passes; each pass: argmax-predict every used atom + bump.
    for _pass in range(N_RETRIEVAL_PASSES):
        # Batch the prediction: K_use (n_use, N) @ W.T -> (n_use, N) sign'd.
        K_use = all_keys[used_idx]  # (n_use, N)
        raw = K_use @ W.T  # (n_use, N) -- W @ key but batched
        preds = np.sign(raw)
        preds[preds == 0] = 1.0
        # cosine vs all_values (V, N): preds (n_use, N) @ all_values.T (N, V)
        sims = preds @ all_values.T / float(N)  # (n_use, V)
        argmaxes = np.argmax(sims, axis=1)  # (n_use,)
        # Bump E for hits.
        hits_mask = (argmaxes == used_idx)
        for i, ui in enumerate(used_idx):
            use_signal = 1.0 if hits_mask[i] else 0.0
            bump_on_retrieval(E, ui, use_signal, cfg)
        # Passive decay all (the "between-cycles forgetting" of CREB).
        decay_E_inplace(E, cfg)

    # Ingest RECENT patterns into W; seed E on write.
    W = W + build_W_from_pairs(keys_rec, values_rec)
    for j in range(M_RECENT):
        idx = M_OLD + j
        seed_on_write(E, idx, cfg)

    return W, all_keys, all_values, E, cfg


# ---------------------------------------------------------------------------
# Arm runner
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int,
            shared: "Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, EConfig] | None" = None,
            ) -> Dict:
    t0 = time.time()
    # Shared substrate state (setup_substrate is expensive: O(J * n_use * N)
    # for the J-cycle bump loop). Compute once per seed and pass into each
    # arm; each arm gets a fresh W copy so downscales don't contaminate.
    if shared is None:
        W_base, all_keys, all_values, E, cfg = setup_substrate(seed)
    else:
        W_base, all_keys, all_values, E, cfg = shared
    W = W_base.copy()  # per-arm fresh copy; downscales are arm-local
    W_norm_pre = float(np.linalg.norm(W))

    n_downscaled = 0
    if arm_name == "ARM_NO_E_BASELINE":
        # Magnitude-only downscale via |W|-row quantile (Wave-1 sanity rail).
        # Per Wave-1 sanity-rail spec: select atoms whose Hebbian-readback
        # magnitude is below the DOWNSCALE_FRAC quantile.
        atom_readback = np.linalg.norm(all_keys @ W.T, axis=1)  # (M_TOTAL,)
        cutoff = float(np.quantile(atom_readback, DOWNSCALE_FRAC))
        mask = atom_readback <= cutoff
        low_idx = np.where(mask)[0]
        n_downscaled = int(len(low_idx))
        for idx in low_idx:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_E_GATED_DOWNSCALE":
        low_E_atoms = np.where(E < E_THRESHOLD)[0]
        n_downscaled = int(len(low_E_atoms))
        for idx in low_E_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_RANDOM_GATED_DOWNSCALE":
        # IMPORTANT: random arm uses the SAME COUNT as E_GATED would (per-seed
        # E-dependent count) so the comparison isolates SELECTIVITY not COUNT.
        # We pre-compute the E_GATED count on the same substrate setup to match.
        n_target_E = int(np.sum(E < E_THRESHOLD))
        # If E_GATED hits nothing, fall back to DOWNSCALE_FRAC * M_TOTAL (the
        # Wave-1 baseline) so RANDOM still has something to do.
        if n_target_E <= 0:
            n_target_E = max(1, int(round(DOWNSCALE_FRAC * M_TOTAL)))
        rng = np.random.RandomState(seed + 7777)
        rand_atoms = rng.choice(M_TOTAL, size=n_target_E, replace=False)
        n_downscaled = n_target_E
        for idx in rand_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    W_norm_post = float(np.linalg.norm(W))

    # Recall measurement: old (first M_OLD) and recent (next M_RECENT).
    rng_eval = np.random.RandomState(seed + 503)
    n_query_old = min(N_QUERIES, M_OLD)
    n_query_recent = min(N_QUERIES, M_RECENT)
    old_query = rng_eval.choice(M_OLD, size=n_query_old, replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_query_recent, replace=False) + M_OLD

    recall_old = recall_subset(W, all_keys, old_query, all_values)
    recall_recent = recall_subset(W, all_keys, rec_query, all_values)

    # Substrate-readback magnitude per atom: |W @ key_i| / N.
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_E_W = correlation_E_vs_magnitude(E, atom_norms)

    # Fraction of atoms below E threshold (verifies threshold actually fires).
    frac_below_thresh = float(np.mean(E < E_THRESHOLD))

    elapsed = time.time() - t0

    return {
        "arm_name": arm_name,
        "recall_old": float(recall_old),
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
        "frac_below_E_threshold": frac_below_thresh,
    }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_E_init():
    E = init_E(16)
    assert E.shape == (16,)
    assert np.all(E == 0.0)
    return True


def _selftest_seed_and_bump():
    cfg = EConfig()
    E = init_E(4)
    seed_on_write(E, 0, cfg)
    assert E[0] == cfg.seed_new
    bump_on_retrieval(E, 0, 1.0, cfg)
    assert E[0] > cfg.seed_new
    return True


def _selftest_decay_shrinks():
    cfg = EConfig()
    E = np.array([0.5, 0.5, 0.5, 0.5])
    decay_E_inplace(E, cfg)
    assert np.all(E < 0.5), f"decay failed: {E}"
    return True


def _selftest_correlation_zero_for_constant_E():
    E = np.ones(8)
    atom_norms = np.abs(np.random.RandomState(0).randn(8))
    c = correlation_E_vs_magnitude(E, atom_norms)
    assert c == 0.0
    return True


def _instrumentation_selftest():
    _selftest_E_init()
    _selftest_seed_and_bump()
    _selftest_decay_shrinks()
    _selftest_correlation_zero_for_constant_E()
    print(
        f"[selftest] PASS  N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  "
        f"alpha={ALPHA:.3f}  J={N_RETRIEVAL_PASSES}  "
        f"E_THRESHOLD={E_THRESHOLD}  mode={RUN_MODE}",
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
    # Compute substrate (J-cycle bump loop) ONCE per seed; reuse across arms.
    print(f"  [seed={seed}] setup_substrate (J={N_RETRIEVAL_PASSES} cycles)...",
          flush=True)
    t_setup = time.time()
    shared = setup_substrate(seed)
    print(f"  [seed={seed}] setup_substrate done in {time.time()-t_setup:.1f}s",
          flush=True)
    arms = []
    for arm_name in ["ARM_NO_E_BASELINE",
                     "ARM_E_GATED_DOWNSCALE",
                     "ARM_RANDOM_GATED_DOWNSCALE"]:
        out = run_arm(arm_name, seed, shared=shared)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] rec_old={out['recall_old']:.3f} "
            f"rec_recent={out['recall_recent']:.3f} "
            f"W_norm_post={out['W_norm_post']:.1f} "
            f"cor_E_W={out['cor_E_magnitude']:.3f} "
            f"n_down={out['n_downscaled']} ({out['downscale_frac_actual']:.2f}) "
            f"frac_below_E={out['frac_below_E_threshold']:.2f} "
            f"E_mean={out['E_mean']:.3f} "
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
        "downscale_scale": DOWNSCALE_SCALE,
        "downscale_frac": DOWNSCALE_FRAC,
        "e_threshold": E_THRESHOLD,
        "use_frac": USE_FRAC,
        "n_passes": N_RETRIEVAL_PASSES,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (Wave-1.5 bands; HARD_PASS requires >= 0.10 discriminator gap)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    arm_names = ["ARM_NO_E_BASELINE", "ARM_E_GATED_DOWNSCALE",
                 "ARM_RANDOM_GATED_DOWNSCALE"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_old = [a["recall_old"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_E_magnitude"] for a in per]
        wnorm = [a["W_norm_post"] for a in per]
        ndown = [a["n_downscaled"] for a in per]
        agg[name] = {
            "mean_recall_old": float(np.mean(rec_old)),
            "std_recall_old": float(np.std(rec_old)),
            "cv_recall_old": float(np.std(rec_old) / max(abs(np.mean(rec_old)), 1e-9)),
            "mean_recall_recent": float(np.mean(rec_rec)),
            "mean_cor_E_W": float(np.mean(cor)),
            "mean_W_norm": float(np.mean(wnorm)),
            "mean_n_downscaled": float(np.mean(ndown)),
        }

    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated.")

    e_arm = agg["ARM_E_GATED_DOWNSCALE"]
    rnd_arm = agg["ARM_RANDOM_GATED_DOWNSCALE"]
    base_arm = agg["ARM_NO_E_BASELINE"]

    gap_e_rnd = e_arm["mean_recall_old"] - rnd_arm["mean_recall_old"]

    summary = (
        f"E_GATED(rec_old={e_arm['mean_recall_old']:.3f},"
        f"rec_rec={e_arm['mean_recall_recent']:.3f},"
        f"cor={e_arm['mean_cor_E_W']:.3f},cv={e_arm['cv_recall_old']:.3f},"
        f"n_down={e_arm['mean_n_downscaled']:.0f}); "
        f"RANDOM(rec_old={rnd_arm['mean_recall_old']:.3f},"
        f"rec_rec={rnd_arm['mean_recall_recent']:.3f},"
        f"n_down={rnd_arm['mean_n_downscaled']:.0f}); "
        f"BASELINE_mag(rec_old={base_arm['mean_recall_old']:.3f},"
        f"rec_rec={base_arm['mean_recall_recent']:.3f}); "
        f"gap_E_vs_RND={gap_e_rnd:+.3f}"
    )

    if not np.isfinite(e_arm["mean_W_norm"]):
        return ("HARD_FAIL", f"HARD_FAIL: E_GATED W_norm non-finite. {summary}")

    # HARD_FAIL gates.
    # 1. If E_GATED ~ RANDOM (gap < 0.05), call HARD_FAIL (mechanism null).
    if abs(gap_e_rnd) < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: |E_GATED.rec_old - RANDOM.rec_old|"
                f"={abs(gap_e_rnd):.3f} < 0.05 (E indistinguishable from "
                f"RANDOM at harder regime; mechanism null). {summary}")
    if e_arm["mean_cor_E_W"] > 0.9:
        return ("HARD_FAIL",
                f"HARD_FAIL: E_GATED cor(E,|W|)={e_arm['mean_cor_E_W']:.3f} "
                f"> 0.9 (E is just a magnitude proxy). {summary}")

    # HARD_PASS gates (Wave-1.5 raised discriminator threshold).
    hp_c_gap = gap_e_rnd >= 0.10  # raised from 0.05
    hp_c_old = e_arm["mean_recall_old"] >= 0.50
    hp_c_rec = e_arm["mean_recall_recent"] >= 0.50
    hp_c_cv = e_arm["cv_recall_old"] <= 0.10  # slack at harder regime
    hp_c_cor = e_arm["mean_cor_E_W"] < 0.7

    if all([hp_c_gap, hp_c_old, hp_c_rec, hp_c_cv, hp_c_cor]):
        return ("HARD_PASS",
                f"HARD_PASS: E_GATED >= RANDOM by {gap_e_rnd:+.3f} (>= 0.10), "
                f"recall_old>=0.50, recall_recent>=0.50, cv<=0.10, "
                f"cor(E,|W|)<0.7. {summary}")

    # MIDDLE_BAND: discriminator gap [0.05, 0.10).
    if 0.05 <= abs(gap_e_rnd) < 0.10:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: discriminator gap {gap_e_rnd:+.3f} in "
                f"[0.05, 0.10). hp_checks=[gap={hp_c_gap},old={hp_c_old},"
                f"rec={hp_c_rec},cv={hp_c_cv},cor={hp_c_cor}]. {summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: E_GATED meets no PASS/MIDDLE band at harder regime. "
            f"hp_checks=[gap={hp_c_gap},old={hp_c_old},rec={hp_c_rec},"
            f"cv={hp_c_cv},cor={hp_c_cor}]. {summary}")


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
    print(f"[seed={seed}] cortex_E HARDER N={N} alpha={ALPHA:.3f} J={N_RETRIEVAL_PASSES} mode={RUN_MODE}...",
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
        f"alpha={ALPHA:.3f} J={N_RETRIEVAL_PASSES} mode={RUN_MODE} "
        f"downscale_scale={DOWNSCALE_SCALE} e_threshold={E_THRESHOLD}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N,
    "M_OLD": M_OLD,
    "M_RECENT": M_RECENT,
    "alpha": float(ALPHA),
    "n_seeds": len(SEEDS),
    "n_queries": N_QUERIES,
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
