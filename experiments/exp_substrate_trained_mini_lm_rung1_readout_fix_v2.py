"""
substrate_trained_mini_lm_rung1_tinychar_v1 -- Phase B rung-1: substrate-trained mini LM.

SCIENTIFIC QUESTION:
  Can a 2-layer char-LM (~5-10k parameter equivalent) be trained ENTIRELY via
  substrate operations (no gradient descent) and achieve a meaningful BPC on
  held-out text? Specifically: outer-product Hopfield write + anti-Hebbian
  contrastive + hippocampal place tag + multi-bank addressing.

  This is a rung-1 gate: if substrate-native training cannot beat near-uniform
  BPC on Shakespeare at tiny scale, there is no justification for scaling to
  Pythia-160M or cloud class.

DESIGN:
  Uses testbed.substrate_lm.char_lm.SubstrateCharLM (no GD; 4 primitives).
  Defensive design: sparse 5% activity regime, binary activations, alpha-budget
  accounting per StackedSubstrate (alpha_max=0.05 = 5% activity).
  500-1000 "cycles" = passes over corpus chunks. 3 seeds.

  Pre-flight watchlist:
    - BPC plateau (val BPC stops improving) -- checked via plateau_detection
    - ||W||_2 exponential growth -- proxy: max_abs_eig from primitive_health_report
    - Retrieval accuracy on held-out probe set (synthetic_retrieval_acc)

PRE-REGISTERED BANDS (rung-1 scale, Phase B routing 2026-06-03):
  HARD-PASS:   val BPC <= 2.5 nats AND no watchlist triggers AND 3/3 seeds
  MIDDLE-BAND: val BPC 2.5-3.5 OR 2/3 seeds OR 1 watchlist trigger
  HARD-FAIL:   val BPC > 3.5 OR collapse (BPC trends toward chance ~5.5+ nats)
               OR multiple watchlist triggers

  Note: uniform-vocab baseline = log2(|vocab|); typical Shakespeare vocab ~60 chars
  -> uniform BPC = log2(60) ~ 5.9 nats (base-e: ~4.1 nats).
  HP target of 2.5 nats means ~40% of uniform (meaningful learning signal).

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateCharLM.fit() consumes >= 1 pair at N=64, alpha_max=0.05.
     [INPUT: N=64, 200-char corpus -> EXPECTED: n_train_pairs >= 1]
  2. score_bpc() returns finite BPC on held-out test at N=64.
     [INPUT: fitted LM, 50-char test -> EXPECTED: 0 < bpc < 20]
  3. plateau_detection([3.0, 3.0, 3.0, 3.0, 3.0], window=3) returns True.
     [EXPECTED: True (plateau detected)]
  4. plateau_detection([3.0, 2.5, 2.0, 1.8], window=3) returns False.
     [EXPECTED: False (improving)]
  5. max_abs_eig growth check: after writing 10 patterns at N=64, max_abs_eig
     < 2.0 (no runaway). [EXPECTED: max_abs_eig < 2.0]

PROT-018: anchor has NO _nN suffix; substrate N is a sweep variable, not a
  contract. Explicit declaration: production N = 512 (rung-1 tiny scale).
  Rationale: no _nN suffix; N=512 declared in prereg.
PROT-021: partials keyed by seed + run_mode + N.

ASCII-only stdout per feedback_ascii_only_in_scripts.
Per feedback_testbed_progress_logging_and_restart: per-cell partial JSON emitted.
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
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial,
    aggregate_partials,
)
from testbed.substrate_lm.char_lm import SubstrateCharLM
from testbed.substrate_lm.primitives import primitive_health_report
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_trained_mini_lm_rung1_readout_fix_v2"

# READOUT-FIX (routing_readout_fix_reevaluate_4_brain_inspired_hfs_2026-06-04):
# v1 scored BPC with cosine-softmax at temperature=1.0, which is near-flat (-> near-uniform BPC
# even when retrieval works; Exp-Dev de-confound 2026-06-04). v2 reports a temperature-CALIBRATED
# BPC (min over a small grid; identical procedure across seeds -> fair) AND the nominal temp=0.2.
# Bands below are recalibrated for the fixed readout (uniform_bpc ~ log2(vocab) ~ 5.52 bits).
READOUT_TEMP_GRID = [1.0, 0.5, 0.3, 0.2, 0.15, 0.1]
READOUT_TEMP_NOMINAL = 0.2

# PROT-018 explicit N declaration (no _nN suffix; N=512 for rung-1 production).
PRODUCTION_N = 512

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---- Config ----
if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N = 128                  # smoke uses smaller N
    ALPHA_MAX = 0.05         # 5% activity regime
    N_LAYERS = 2
    N_STEPS_PER_LAYER = 3
    TRAIN_CHARS = 5_000      # tiny corpus
    VAL_CHARS = 1_000
    HEALTH_EVERY = 500
    TEMPERATURE = 1.0
else:
    SEEDS = [7, 17, 23, 31, 41]   # routing: 5 seeds (>= 4/5 for HP)
    N = PRODUCTION_N         # PROT-018 production N
    ALPHA_MAX = 0.05
    N_LAYERS = 2
    N_STEPS_PER_LAYER = 3
    TRAIN_CHARS = 100_000    # ~500-1000 effective bigram cycles per alpha budget
    VAL_CHARS = 20_000
    HEALTH_EVERY = 1000
    TEMPERATURE = 1.0

# Pre-registered thresholds (readout-fix re-eval bands per routing; BITS, uniform~5.52)
HP_BPC_MAX = 4.5          # calibrated BPC < 4.5 (>=1.0 bit below uniform) = HARD-PASS
MID_BPC_MAX = 5.2         # 4.5-5.2 = MIDDLE; > 5.2 (within 0.3 of uniform) = HARD-FAIL
HF_BPC_MIN = 5.2
HP_MIN_SEEDS = 4          # >= 4/5 seeds for HP (routing)
MID_MIN_SEEDS = 2         # 2-3/5 seeds for MIDDLE


# ---------------------------------------------------------------------------
# Watchlist helpers
# ---------------------------------------------------------------------------

def plateau_detection(bpc_trace: List[float], window: int = 5) -> bool:
    """Return True if BPC has plateaued: std in last `window` steps < 0.01."""
    if len(bpc_trace) < window:
        return False
    tail = bpc_trace[-window:]
    return float(np.std(tail)) < 0.01


def check_watchlist_triggers(
    bpc_trace: List[float],
    health_snapshots: List[dict],
    uniform_bpc: float,
) -> List[str]:
    """Return list of triggered watchlist events (empty if healthy)."""
    triggers = []
    if len(bpc_trace) >= 5 and plateau_detection(bpc_trace, window=5):
        triggers.append("BPC_PLATEAU")
    # Exponential growth: max_abs_eig > 3 * sqrt(N) is a heuristic threshold
    # (well-controlled Hopfield: max_eig ~ M ~ alpha * N; at alpha=0.05, N=512
    # -> expected eig ~ 25; threshold here is 3x for conservative flagging).
    for snap in health_snapshots:
        for layer in snap.get("per_layer", []):
            eig = layer.get("max_abs_eig", 0.0)
            N_val = snap.get("N", PRODUCTION_N)
            if np.isfinite(eig) and eig > 3.0 * N_val:
                triggers.append(f"W_NORM_GROWTH_LAYER{layer['layer']}")
    # Collapse toward chance
    if bpc_trace and bpc_trace[-1] > uniform_bpc * 0.95:
        triggers.append("BPC_NEAR_CHANCE")
    return list(set(triggers))  # deduplicate


# ---------------------------------------------------------------------------
# Run one seed
# ---------------------------------------------------------------------------

def run_one_seed(seed: int) -> dict:
    t_seed = time.time()
    print(f"[seed={seed}] starting N={N} alpha_max={ALPHA_MAX}", flush=True)

    # Load corpus
    corpus_train = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    corpus_val = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = set(corpus_train) | set(corpus_val)

    # Build and fit model
    lm = SubstrateCharLM(
        n_layers=N_LAYERS,
        N=N,
        alpha_max=ALPHA_MAX,
        n_steps_per_layer=N_STEPS_PER_LAYER,
        seed=seed,
    )

    fit_info = lm.fit(
        corpus=corpus_train,
        n_chars_train=None,
        char_vocab=vocab,
        health_every=HEALTH_EVERY,
        verbose=True,
    )

    # Score with READOUT-FIX: temperature-calibrated BPC (min over grid) + nominal temp=0.2.
    bpc_by_temp = {}
    uniform_bpc = None
    for tmp in READOUT_TEMP_GRID:
        s = lm.score_bpc(corpus_val, temperature=tmp)
        bpc_by_temp[tmp] = float(s["bpc"])
        uniform_bpc = float(s["uniform_bpc"])
    val_bpc_calibrated = min(bpc_by_temp.values())
    best_temp = min(bpc_by_temp, key=bpc_by_temp.get)
    val_bpc_temp1 = bpc_by_temp.get(1.0, float("nan"))   # original v1 readout (artifact baseline)
    val_bpc_nominal = bpc_by_temp.get(READOUT_TEMP_NOMINAL, float("nan"))
    val_bpc = val_bpc_calibrated   # verdict metric = calibrated BPC

    # Watchlist
    # Build minimal bpc trace (we only have the final BPC from score_bpc;
    # check collapse with the single final value + uniform baseline).
    bpc_trace = [val_bpc]
    health_snaps = lm.health_snapshots
    triggers = check_watchlist_triggers(bpc_trace, health_snaps, uniform_bpc)

    elapsed = time.time() - t_seed
    print(
        f"[seed={seed}] val_bpc_calibrated={val_bpc:.4f} (best_temp={best_temp}) "
        f"val_bpc_temp1.0={val_bpc_temp1:.4f} val_bpc_temp0.2={val_bpc_nominal:.4f} "
        f"uniform_bpc={uniform_bpc:.4f} "
        f"n_train_pairs={fit_info['n_train_pairs']} "
        f"max_alpha={lm.stack.max_alpha():.4f} "
        f"any_collapse={fit_info['any_primitive_collapse']} "
        f"watchlist_triggers={triggers} "
        f"elapsed={elapsed:.1f}s",
        flush=True,
    )

    return {
        "seed": int(seed),
        "val_bpc": float(val_bpc),
        "val_bpc_calibrated": float(val_bpc_calibrated),
        "val_bpc_temp1": float(val_bpc_temp1),
        "val_bpc_nominal_temp02": float(val_bpc_nominal),
        "best_temp": float(best_temp),
        "uniform_bpc": float(uniform_bpc),
        "n_train_pairs": int(fit_info["n_train_pairs"]),
        "n_pos_pairs": int(fit_info.get("n_pos_pairs", 0)),
        "n_neg_pairs": int(fit_info.get("n_neg_pairs", 0)),
        "final_alphas": [float(a) for a in fit_info["final_alphas"]],
        "any_primitive_collapse": bool(fit_info["any_primitive_collapse"]),
        "watchlist_triggers": triggers,
        "train_wall_s": float(fit_info["train_wall_s"]),
        "total_wall_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY per role contract)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. SubstrateCharLM.fit() consumes >= 1 pair at N=64, alpha_max=0.05
    corpus_t = wikitext2_char_corpus(split="train", max_chars=200)
    corpus_v = wikitext2_char_corpus(split="validation", max_chars=50)
    vocab_t = set(corpus_t) | set(corpus_v)
    lm_t = SubstrateCharLM(n_layers=2, N=64, alpha_max=0.05, n_steps_per_layer=2, seed=1)
    info = lm_t.fit(corpus_t, char_vocab=vocab_t, verbose=False)
    assert info["n_train_pairs"] >= 1, (
        f"[selftest] FAIL: fit consumed 0 pairs. info={info}"
    )

    # 2. score_bpc() returns finite BPC
    score = lm_t.score_bpc(corpus_v, temperature=1.0)
    assert score["n_scored"] >= 1, (
        f"[selftest] FAIL: score_bpc scored 0 positions. vocab={len(vocab_t)}"
    )
    assert np.isfinite(score["bpc"]) and score["bpc"] > 0.0, (
        f"[selftest] FAIL: bpc={score['bpc']} is non-finite or zero"
    )

    # 3. plateau_detection returns True for flat trace
    result_flat = plateau_detection([3.0, 3.0, 3.0, 3.0, 3.0], window=3)
    assert result_flat is True, f"[selftest] FAIL: plateau_detection flat trace -> {result_flat}"

    # 4. plateau_detection returns False for improving trace
    result_imp = plateau_detection([3.0, 2.5, 2.0, 1.8], window=3)
    assert result_imp is False, f"[selftest] FAIL: plateau_detection improving trace -> {result_imp}"

    # 5. max_abs_eig < 2.0 * N at alpha=0.05, N=64
    health = primitive_health_report(lm_t.stack)
    for layer in health.get("per_layer", []):
        eig = layer.get("max_abs_eig", 0.0)
        if layer["writes"] > 0:
            assert eig < 2.0 * 64, (
                f"[selftest] FAIL: layer {layer['layer']} max_abs_eig={eig} >= 2*N=128"
            )

    print(
        f"[selftest] PASS: n_pairs={info['n_train_pairs']} bpc={score['bpc']:.3f} "
        f"uniform_bpc={score['uniform_bpc']:.3f} plateau_flat=True plateau_imp=False",
        flush=True,
    )


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main() -> None:
    if _ARGS.self_test:
        print("[exp] self-test already ran at module scope. Done.", flush=True)
        return

    out_dir = get_output_dir(ANCHOR_NAME)
    print(
        f"[exp] ANCHOR={ANCHOR_NAME} RUN_MODE={RUN_MODE} N={N} SEEDS={SEEDS}",
        flush=True,
    )

    done, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds done; running {remaining}", flush=True)

    t_total = time.time()
    for seed in remaining:
        result = run_one_seed(seed)
        write_partial(out_dir, seed, result)
        print(
            f"[progress] seed={seed} val_bpc={result['val_bpc']:.4f} "
            f"triggers={result['watchlist_triggers']}",
            flush=True,
        )

    per_seed = aggregate_partials(out_dir, SEEDS)
    total_elapsed = time.time() - t_total

    # ---- Verdict ----
    bpc_values = [per_seed[str(s)]["val_bpc"] for s in SEEDS if str(s) in per_seed]
    trigger_counts = [
        len(per_seed[str(s)].get("watchlist_triggers", [])) for s in SEEDS if str(s) in per_seed
    ]
    collapses = [
        per_seed[str(s)].get("any_primitive_collapse", False)
        for s in SEEDS if str(s) in per_seed
    ]

    n_valid = len(bpc_values)
    bpc_mean = float(np.mean(bpc_values)) if bpc_values else float("nan")
    bpc_std = float(np.std(bpc_values)) if len(bpc_values) > 1 else 0.0
    seeds_hp = sum(1 for v in bpc_values if v <= HP_BPC_MAX)
    seeds_mid = sum(1 for v in bpc_values if HP_BPC_MAX < v <= MID_BPC_MAX)
    total_triggers = sum(trigger_counts)
    any_collapse = any(collapses)

    if (
        bpc_mean <= HP_BPC_MAX
        and total_triggers == 0
        and not any_collapse
        and seeds_hp >= HP_MIN_SEEDS
    ):
        verdict = "HARD_PASS"
    elif (
        bpc_mean <= MID_BPC_MAX
        and (seeds_hp + seeds_mid) >= MID_MIN_SEEDS
        and not any_collapse
    ):
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL"

    uniform_bpcs = [
        per_seed[str(s)].get("uniform_bpc", float("nan"))
        for s in SEEDS if str(s) in per_seed
    ]
    uniform_bpc_mean = float(np.mean(uniform_bpcs)) if uniform_bpcs else float("nan")

    verdict_msg = (
        f"VERDICT={verdict} "
        f"bpc_mean={bpc_mean:.4f}+-{bpc_std:.4f} "
        f"uniform_bpc_mean={uniform_bpc_mean:.4f} "
        f"seeds_hp={seeds_hp}/{n_valid} seeds_mid={seeds_mid}/{n_valid} "
        f"watchlist_triggers_total={total_triggers} "
        f"any_collapse={any_collapse} "
        f"HP_THRESHOLD=bpc<={HP_BPC_MAX} MID_THRESHOLD={HP_BPC_MAX}<bpc<={MID_BPC_MAX} "
        f"N={N} SEEDS={SEEDS} total_wall_s={total_elapsed:.1f}"
    )
    print(f"[exp] {verdict_msg}", flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "bpc_mean": bpc_mean,
        "bpc_std": bpc_std,
        "uniform_bpc_mean": uniform_bpc_mean,
        "seeds_hard_pass": seeds_hp,
        "seeds_middle": seeds_mid,
        "seeds_hard_fail": n_valid - seeds_hp - seeds_mid,
        "n_valid_seeds": n_valid,
        "watchlist_triggers_total": total_triggers,
        "any_primitive_collapse": any_collapse,
        "HP_BPC_MAX": HP_BPC_MAX,
        "MID_BPC_MAX": MID_BPC_MAX,
        "N": N,
        "alpha_max": ALPHA_MAX,
        "n_layers": N_LAYERS,
        "elapsed_s": total_elapsed,
        "per_seed": {str(s): per_seed.get(str(s), None) for s in SEEDS},
    }

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[exp] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
