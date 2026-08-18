"""cortex_E_tensor_separate_importance_v1 -- per-atom E[i] vs |W[i]| selectivity.

MOTIVATION (Research cortex 4x cross-discipline drill 2026-06-26):
  3/5 cortex failures (Cell B Two-Tier, STC, cold-storage) tried to read
  importance off |W| (the noisy thing the substrate writes into); E is the
  orthogonal signal. CREB analog: per-atom EWMA-on-retrieval excitability
  tracker, decoupled from weight magnitude.

  Substrate-product test: ingest M_old "old" patterns, then later ingest
  M_recent "recent" patterns; periodically use a subset of "old" patterns
  (the bump-on-retrieval signal). Then run a downscale step (the "forgetting"
  step in cortex / Two-Tier / cold-storage). Compare 3 downscale gates:
    - ARM_NO_E_BASELINE        : magnitude-only (|W|-quantile) downscale; the
                                 Cell B failure mode reproduction. SANITY RAIL.
    - ARM_E_GATED_DOWNSCALE    : E-threshold downscale (low-E rows shrunk);
                                 the proposed CREB-analog mechanism.
    - ARM_RANDOM_GATED_DOWNSCALE: uniform-random downscale at the same frac;
                                 the LOAD-BEARING DISCRIMINATOR (proves
                                 SELECTIVITY matters, not "any sparsification
                                 works").

HYPOTHESIS (PRE-REG, must answer in verdict):
  At M_old=300 (older patterns, used 30% of the time) + M_recent=200 (recent
  patterns, never explicitly retrieved before measurement) on N=2048 substrate:
  E_GATED preserves recall_old (the items E says matter) AND keeps recall_recent
  high, while magnitude-only collapses recall_old (it scales the small-norm
  used items) and RANDOM collapses both indiscriminately.

PRE-REGISTERED HARD BANDS (from research handoff verbatim):
  HARD_PASS (ALL of):
    - ARM_E_GATED recall_old >= 0.60
    - ARM_E_GATED recall_recent >= 0.85
    - ||W||_F finite and bounded (no blow-up)
    - cv across seeds <= 0.05 on E_GATED arm
    - cor(E, |W|) < 0.7 in the E_GATED arm (E carries info |W| does not)
    - ARM_E_GATED recall_old strictly exceeds ARM_RANDOM_GATED recall_old
      by >= 0.05 (selectivity is load-bearing)
    - substrate_only_decode_gate: n_llm_calls == 0
  MIDDLE_BAND:
    - ARM_E_GATED recall_old in [0.30, 0.60)
  HARD_FAIL (ANY of):
    - ARM_E_GATED recall_old < 0.30
    - cor(E, |W|) > 0.9 in E_GATED arm (E is just a magnitude proxy)
    - |ARM_E_GATED recall_old - ARM_RANDOM_GATED recall_old| < 0.03
      (E indistinguishable from RANDOM -> mechanism null)
    - n_llm_calls > 0

ARMS (3 mandatory per handoff):
  ARM_NO_E_BASELINE
  ARM_E_GATED_DOWNSCALE
  ARM_RANDOM_GATED_DOWNSCALE

INSTRUMENTATION:
  per_arm: arm_name, recall_old, recall_recent, W_norm,
           cor_E_magnitude, n_downscaled, downscale_frac
  per_seed: full per_arm payload

SUBSTRATE-ONLY DECODE GATE:
  Imports NO transformers / huggingface / openai. n_llm_calls is logged 0
  by structural-guarantee. Decode is sign(W @ key) cosine cleanup against
  value matrix.

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

# ---------------------------------------------------------------------------
# Inlined excitability primitive (canonical copy at hdlab/excitability.py; we
# inline here for self-containment on whatever runner picks up the cell).
# ---------------------------------------------------------------------------
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


def downscale_gate_by_E(W: np.ndarray, E: np.ndarray, scale: float,
                         threshold: float) -> int:
    mask = E < threshold
    n_hit = int(np.sum(mask))
    if n_hit > 0:
        W[mask, :] *= scale
    return n_hit


def downscale_gate_by_magnitude(W: np.ndarray, threshold_frac: float,
                                 scale: float) -> int:
    norms = np.linalg.norm(W, axis=1)
    cutoff = float(np.quantile(norms, threshold_frac))
    mask = norms <= cutoff
    n_hit = int(np.sum(mask))
    if n_hit > 0:
        W[mask, :] *= scale
    return n_hit


def downscale_gate_random(W: np.ndarray, frac: float, scale: float,
                           rng: np.random.RandomState) -> int:
    n_rows = W.shape[0]
    n_hit = int(round(frac * n_rows))
    idx = rng.choice(n_rows, size=n_hit, replace=False)
    W[idx, :] *= scale
    return n_hit


def correlation_E_vs_magnitude(E: np.ndarray, atom_norms: np.ndarray) -> float:
    """Pearson cor(E[i], per-atom substrate-readback-magnitude[i]).

    The substrate-native "what would |W| say is important?" proxy: for each
    atom i, the projection magnitude |W @ key_i| post-downscale. If E carries
    information the substrate's readback magnitude does NOT, cor < 0.7.
    """
    if E.shape[0] != atom_norms.shape[0]:
        raise ValueError(
            f"shape mismatch: E={E.shape}, atom_norms={atom_norms.shape}"
        )
    if np.std(E) <= 1e-12 or np.std(atom_norms) <= 1e-12:
        return 0.0
    return float(np.corrcoef(E, atom_norms)[0, 1])


ANCHOR_NAME = "cortex_E_tensor_separate_importance_v1"

# Substrate-only-decode audit counter (structural; 0 by no-LLM-import).
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
N_FULL = 2048
M_OLD_FULL = 300            # M_old/N = 0.146 (just above alpha_c=0.138)
M_RECENT_FULL = 200         # adds 0.098 -> total alpha ~ 0.244
USE_FRAC_FULL = 0.30        # 30% of old patterns get bumped on retrieval
N_RETRIEVAL_PASSES_FULL = 3
DOWNSCALE_SCALE = 0.20      # surviving rows keep 20% of weight
DOWNSCALE_FRAC = 0.40       # target frac of rows to downscale (RANDOM + MAGNITUDE)
E_THRESHOLD = 0.30          # E < 0.30 -> downscale (E-GATED arm)
SEEDS_FULL = [7, 17, 23]
N_QUERIES_FULL = 200

if RUN_MODE == "smoke":
    N = 256
    M_OLD = 50
    M_RECENT = 30
    USE_FRAC = 0.30
    N_RETRIEVAL_PASSES = 2
    SEEDS = [7]
    N_QUERIES = 40
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
# Hebbian write + recall
# ---------------------------------------------------------------------------
def hebbian_write(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> None:
    W += np.outer(value, key)


def predict(W: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def recall_subset(W: np.ndarray, keys: np.ndarray, values: np.ndarray,
                  query_idx: np.ndarray, all_values: np.ndarray) -> float:
    """Recall@1: for each indexed query, sign(W @ key) cosine-match against all_values."""
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
# Arm runners
# ---------------------------------------------------------------------------
def setup_substrate(seed: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray,
                                        np.ndarray, EConfig]:
    """Build keys/values, ingest old + recent into W; track E on retrievals.

    Returns (W, all_keys, all_values, E, cfg). Indices 0..M_OLD-1 are old;
    M_OLD..M_OLD+M_RECENT-1 are recent.
    """
    keys_old, values_old = generate_pairs(M_OLD, N, seed)
    keys_rec, values_rec = generate_pairs(M_RECENT, N, seed + 999)
    all_keys = np.concatenate([keys_old, keys_rec], axis=0)
    all_values = np.concatenate([values_old, values_rec], axis=0)

    cfg = EConfig()
    E = init_E(M_TOTAL)
    W = np.zeros((N, N), dtype=np.float64)

    # Ingest OLD patterns; seed E on write.
    for i in range(M_OLD):
        hebbian_write(W, all_keys[i], all_values[i])
        seed_on_write(E, i, cfg)

    # Retrieval passes on a USE_FRAC subset of OLD patterns -> bump E.
    rng = np.random.RandomState(seed + 401)
    n_use = max(1, int(round(USE_FRAC * M_OLD)))
    used_idx = rng.choice(M_OLD, size=n_use, replace=False)
    for _pass in range(N_RETRIEVAL_PASSES):
        for i in used_idx:
            pred = predict(W, all_keys[i])
            sims = all_values @ pred / float(N)
            argmax = int(np.argmax(sims))
            use_signal = 1.0 if argmax == i else 0.0
            bump_on_retrieval(E, i, use_signal, cfg)

    # Ingest RECENT patterns; seed E on write.
    for j in range(M_RECENT):
        idx = M_OLD + j
        hebbian_write(W, all_keys[idx], all_values[idx])
        seed_on_write(E, idx, cfg)

    return W, all_keys, all_values, E, cfg


def run_arm(arm_name: str, seed: int) -> Dict:
    t0 = time.time()
    W, all_keys, all_values, E, cfg = setup_substrate(seed)
    W_norm_pre = float(np.linalg.norm(W))

    n_downscaled = 0
    if arm_name == "ARM_NO_E_BASELINE":
        # Magnitude-only downscale (the Cell B failure reproduction; sanity rail).
        n_downscaled = downscale_gate_by_magnitude(
            W, threshold_frac=DOWNSCALE_FRAC, scale=DOWNSCALE_SCALE,
        )
    elif arm_name == "ARM_E_GATED_DOWNSCALE":
        # Downscale outer-product rows whose ATOM index has E < threshold.
        # Note: W shape is (N, N) where rows index OUTPUT dim, not atom dim.
        # The brain analog acts at the ATOM level: shrink the OUTER-PRODUCT
        # contribution of low-E atoms. Realize by subtracting (1-scale) *
        # outer(value, key) for each low-E atom.
        low_E_atoms = np.where(E < E_THRESHOLD)[0]
        n_downscaled = int(len(low_E_atoms))
        for idx in low_E_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    elif arm_name == "ARM_RANDOM_GATED_DOWNSCALE":
        # Uniform-random downscale of frac of atoms (the discriminator).
        # Same atom-level mechanism as E_GATED but selection is random.
        rng = np.random.RandomState(seed + 7777)
        n_target = int(round(DOWNSCALE_FRAC * M_TOTAL))
        rand_atoms = rng.choice(M_TOTAL, size=n_target, replace=False)
        n_downscaled = n_target
        for idx in rand_atoms:
            W -= (1.0 - DOWNSCALE_SCALE) * np.outer(
                all_values[idx], all_keys[idx],
            )
    else:
        raise ValueError(f"unknown arm {arm_name}")

    W_norm_post = float(np.linalg.norm(W))

    # Recall measurement: separate old (first M_OLD) and recent (next M_RECENT).
    rng_eval = np.random.RandomState(seed + 503)
    n_query_old = min(N_QUERIES, M_OLD)
    n_query_recent = min(N_QUERIES, M_RECENT)
    old_query = rng_eval.choice(M_OLD, size=n_query_old, replace=False)
    rec_query = rng_eval.choice(M_RECENT, size=n_query_recent, replace=False) + M_OLD

    recall_old = recall_subset(W, all_keys, all_values, old_query, all_values)
    recall_recent = recall_subset(W, all_keys, all_values, rec_query, all_values)

    # Substrate-readback magnitude per atom: ||W @ key_i|| / N (the substrate's
    # own "how strong is this atom's projection?" signal; the thing |W|-gated
    # arms read off, not the row-norm).
    atom_norms = np.linalg.norm(all_keys @ W.T, axis=1) / float(N)
    cor_E_W = correlation_E_vs_magnitude(E, atom_norms)

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
    }


# ---------------------------------------------------------------------------
# Self-tests (run at import; gate the script)
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
    assert E[0] > cfg.seed_new  # bumped up
    return True


def _selftest_correlation_zero_for_constant_E():
    E = np.ones(8)
    atom_norms = np.abs(np.random.RandomState(0).randn(8))
    c = correlation_E_vs_magnitude(E, atom_norms)
    assert c == 0.0  # constant-E -> std(E)=0 -> 0
    return True


def _selftest_baseline_recall_high():
    """No downscale (vanilla Hebbian) at alpha=0.05: recall_at_1 should be high."""
    rng = np.random.RandomState(1)
    N_t = 256
    M_t = 12  # alpha 0.047
    keys = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    values = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    W = np.zeros((N_t, N_t))
    for k, v in zip(keys, values):
        hebbian_write(W, k, v)
    rng2 = np.random.RandomState(2)
    q = rng2.choice(M_t, size=M_t, replace=False)
    r = recall_subset(W, keys, values, q, values)
    assert r >= 0.80, f"baseline recall too low: {r:.3f}"
    return r


def _selftest_arm_runs():
    """Smoke that each arm completes and yields finite metrics on a tiny config."""
    saved_N = N
    saved_M_OLD = M_OLD
    saved_M_RECENT = M_RECENT
    # We need to use the actual module-level configs for runtime; arm code
    # references the globals. Just call run_arm at the current smoke/full config.
    out = run_arm("ARM_NO_E_BASELINE", seed=0)
    assert np.isfinite(out["recall_old"]) and np.isfinite(out["recall_recent"])
    return True


def _instrumentation_selftest():
    _selftest_E_init()
    _selftest_seed_and_bump()
    _selftest_correlation_zero_for_constant_E()
    rec = _selftest_baseline_recall_high()
    # The arm-runs selftest is expensive at full N; only run when smoke.
    if RUN_MODE == "smoke":
        _selftest_arm_runs()
    print(
        f"[selftest] PASS  baseline_recall_low_alpha={rec:.3f}  "
        f"N={N}  M_OLD={M_OLD}  M_RECENT={M_RECENT}  alpha={ALPHA:.3f}  "
        f"mode={RUN_MODE}",
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
    arms = []
    for arm_name in ["ARM_NO_E_BASELINE",
                     "ARM_E_GATED_DOWNSCALE",
                     "ARM_RANDOM_GATED_DOWNSCALE"]:
        out = run_arm(arm_name, seed)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] rec_old={out['recall_old']:.3f} "
            f"rec_recent={out['recall_recent']:.3f} "
            f"W_norm_post={out['W_norm_post']:.1f} "
            f"cor_E_W={out['cor_E_magnitude']:.3f} "
            f"n_down={out['n_downscaled']} ({out['downscale_frac_actual']:.2f}) "
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
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (PRE-REG bands)
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")

    # Aggregate per-arm across seeds.
    arm_names = ["ARM_NO_E_BASELINE", "ARM_E_GATED_DOWNSCALE",
                 "ARM_RANDOM_GATED_DOWNSCALE"]
    agg: Dict[str, Dict[str, float]] = {}
    for name in arm_names:
        per = [_arm_by_name(r["arms"], name) for r in results]
        rec_old = [a["recall_old"] for a in per]
        rec_rec = [a["recall_recent"] for a in per]
        cor = [a["cor_E_magnitude"] for a in per]
        wnorm = [a["W_norm_post"] for a in per]
        agg[name] = {
            "mean_recall_old": float(np.mean(rec_old)),
            "std_recall_old": float(np.std(rec_old)),
            "cv_recall_old": float(np.std(rec_old) / max(abs(np.mean(rec_old)), 1e-9)),
            "mean_recall_recent": float(np.mean(rec_rec)),
            "mean_cor_E_W": float(np.mean(cor)),
            "mean_W_norm": float(np.mean(wnorm)),
        }

    # Substrate-only-decode gate.
    any_llm = any(r.get("n_llm_calls", 0) > 0 for r in results)
    if any_llm:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate violated (n_llm_calls > 0).")

    e_arm = agg["ARM_E_GATED_DOWNSCALE"]
    rnd_arm = agg["ARM_RANDOM_GATED_DOWNSCALE"]
    base_arm = agg["ARM_NO_E_BASELINE"]

    summary = (
        f"E_GATED(rec_old={e_arm['mean_recall_old']:.3f},"
        f"rec_rec={e_arm['mean_recall_recent']:.3f},"
        f"cor={e_arm['mean_cor_E_W']:.3f},cv={e_arm['cv_recall_old']:.3f}); "
        f"RANDOM(rec_old={rnd_arm['mean_recall_old']:.3f},"
        f"rec_rec={rnd_arm['mean_recall_recent']:.3f}); "
        f"BASELINE_mag(rec_old={base_arm['mean_recall_old']:.3f},"
        f"rec_rec={base_arm['mean_recall_recent']:.3f})"
    )

    # Finite-W check.
    if not np.isfinite(e_arm["mean_W_norm"]):
        return ("HARD_FAIL", f"HARD_FAIL: E_GATED W_norm non-finite. {summary}")

    # HARD_FAIL checks first.
    if e_arm["mean_recall_old"] < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: E_GATED recall_old={e_arm['mean_recall_old']:.3f} < 0.30. "
                f"{summary}")
    if e_arm["mean_cor_E_W"] > 0.9:
        return ("HARD_FAIL",
                f"HARD_FAIL: E_GATED cor(E,|W|)={e_arm['mean_cor_E_W']:.3f} > 0.9 "
                f"(E is just a magnitude proxy). {summary}")
    if abs(e_arm["mean_recall_old"] - rnd_arm["mean_recall_old"]) < 0.03:
        return ("HARD_FAIL",
                f"HARD_FAIL: |E_GATED.rec_old - RANDOM.rec_old|"
                f"={abs(e_arm['mean_recall_old']-rnd_arm['mean_recall_old']):.3f} "
                f"< 0.03 (E indistinguishable from RANDOM). {summary}")

    # HARD_PASS checks (all required).
    hp_c1 = e_arm["mean_recall_old"] >= 0.60
    hp_c2 = e_arm["mean_recall_recent"] >= 0.85
    hp_c3 = e_arm["cv_recall_old"] <= 0.05
    hp_c4 = e_arm["mean_cor_E_W"] < 0.7
    hp_c5 = e_arm["mean_recall_old"] - rnd_arm["mean_recall_old"] >= 0.05

    if all([hp_c1, hp_c2, hp_c3, hp_c4, hp_c5]):
        return ("HARD_PASS",
                f"HARD_PASS: E_GATED preserves old recall + recent recall + "
                f"discriminates vs RANDOM + E carries info |W| does not. {summary}")

    # MIDDLE_BAND.
    if 0.30 <= e_arm["mean_recall_old"] < 0.60:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: E_GATED recall_old in [0.30,0.60). "
                f"hp_checks=[c1={hp_c1},c2={hp_c2},c3={hp_c3},c4={hp_c4},c5={hp_c5}]. "
                f"{summary}")

    return ("HARD_FAIL",
            f"HARD_FAIL: E_GATED recall_old={e_arm['mean_recall_old']:.3f} "
            f"meets no PASS/MIDDLE band. "
            f"hp_checks=[c1={hp_c1},c2={hp_c2},c3={hp_c3},c4={hp_c4},c5={hp_c5}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] cortex_E N={N} alpha={ALPHA:.3f} mode={RUN_MODE}...",
          flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

# Mode guard (Fix #5).
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
        f"alpha={ALPHA:.3f} mode={RUN_MODE} downscale_scale={DOWNSCALE_SCALE} "
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
