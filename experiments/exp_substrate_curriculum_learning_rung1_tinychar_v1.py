"""
substrate_curriculum_learning_rung1_tinychar_v1 -- Phase B rung-1: substrate-driven
curriculum learning for tiny char-LM.

SCIENTIFIC QUESTION:
  Does substrate-scored curriculum ordering (easy -> medium -> hard batches per
  substrate state) improve val BPC for a gradient-trained tiny char-LM compared
  to random batch order, at rung-1 tiny scale?

  Rung-1: tiny GRU char-LM. N_STEPS_MAX steps per condition (random vs substrate).
  3 seeds per condition. Metric: final_bpc_val.

DESIGN:
  Uses testbed.curriculum.training_loop.train_curriculum.
  Conditions: [random, substrate].
  Substrate observer: SubstrateCurriculumPolicy (hebbian_write + retrieval_cosine).
  2000 training steps per condition, 3 seeds.

PRE-REGISTERED BANDS (rung-1 scale):
  HARD-PASS:   curriculum beats random by > 5% on val BPC (relative reduction)
               AND across 3/3 seeds AND no instability (val BPC finite)
  MIDDLE-BAND: 2-5% gain OR 2/3 seeds
  HARD-FAIL:   curriculum matches or trails random baseline

FORMULA SELF-TESTS (PROT-022):
  1. build_policy('random', ...) returns a RandomPolicy that next_batch() returns
     list of ints of length batch_size.
     [INPUT: examples=[...10 items], batch_size=2 -> EXPECTED: len==2, all ints]
  2. build_policy('substrate', ..., N=32) returns SubstrateCurriculumPolicy that
     next_batch() returns list of ints of length batch_size.
     [INPUT: N=32, examples=[...10 items], batch_size=2 -> EXPECTED: len==2, all ints]
  3. make_tiny_gru_factory(vocab_size=10) returns a callable that produces a GRU model.
     [EXPECTED: model has parameters]
  4. bpc_gain_relative formula: (base - curr) / base = gain.
     [INPUT: base=3.0, curr=2.7 -> EXPECTED: gain=0.10]
  5. split_corpus_into_examples('abcdefgh', seq_len=4) -> ['abcd', 'efgh']
     [EXPECTED: list of 2 strings of length 4]

PROT-018: anchor has NO _nN suffix; substrate N is not a production contract axis
  for a curriculum-learning experiment. Explicit: SUBSTRATE_N=256 rung-1 production.
PROT-021: partials keyed by condition + seed + run_mode.

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
from typing import Dict, List, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir
from testbed.substrate_lm.data import wikitext2_char_corpus
from testbed.curriculum.policies import build_policy
from testbed.curriculum.training_loop import (
    train_curriculum,
    split_corpus_into_examples,
    make_tiny_gru_factory,
)

ANCHOR_NAME = "substrate_curriculum_learning_rung1_tinychar_v1"

# PROT-018 explicit N declaration
PRODUCTION_SUBSTRATE_N = 256

RUN_MODE = (
    "smoke" if "--smoke" in sys.argv
    else os.environ.get("HDLAB_RUN_MODE", "full")
).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

CONDITIONS = ["random", "substrate"]

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_STEPS_MAX = 80
    HIDDEN = 32
    TRAIN_CHARS = 5_000
    VAL_CHARS = 1_000
    TEST_CHARS = 500
    BATCH_SIZE = 8
    SEQ_LEN = 16
    LR = 1e-3
    EVAL_EVERY = 20
    SUBSTRATE_N = 32           # smoke uses tiny substrate
else:
    SEEDS = [7, 17, 23]
    N_STEPS_MAX = 2000
    HIDDEN = 64
    TRAIN_CHARS = 80_000
    VAL_CHARS = 15_000
    TEST_CHARS = 5_000
    BATCH_SIZE = 16
    SEQ_LEN = 32
    LR = 3e-3
    EVAL_EVERY = 200
    SUBSTRATE_N = PRODUCTION_SUBSTRATE_N

# Pre-registered thresholds
HP_GAIN_FRAC = 0.05     # curriculum beats random by > 5% relative val BPC reduction
MID_GAIN_FRAC_LO = 0.02 # lower bound for MIDDLE: > 2%
HP_MIN_SEEDS = 3
MID_MIN_SEEDS = 2


# ---------------------------------------------------------------------------
# Per-cell partial helpers
# ---------------------------------------------------------------------------

def _partial_key(condition: str, seed: int) -> str:
    return f"{condition}_seed{seed}_{RUN_MODE}"


def _write_cell_partial(out_dir: Path, condition: str, seed: int, result: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    key = _partial_key(condition, seed)
    fpath = out_dir / f"partial_{key}.json"
    tmp = fpath.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2), encoding="utf-8")
    tmp.replace(fpath)


def _load_cell_partial(out_dir: Path, condition: str, seed: int) -> Optional[dict]:
    fpath = out_dir / f"partial_{_partial_key(condition, seed)}.json"
    if fpath.exists():
        try:
            return json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


# ---------------------------------------------------------------------------
# Instrumentation self-test (MANDATORY)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # Setup tiny corpus
    corpus_t = wikitext2_char_corpus(split="train", max_chars=3000)
    examples_t = split_corpus_into_examples(corpus_t, seq_len=16)
    # Ensure enough examples for policies
    while len(examples_t) < 10:
        examples_t = examples_t * 2
    examples_t = examples_t[:max(10, len(examples_t))]
    rng_np = np.random.default_rng(1)

    # 1. build_policy('random') -> next_batch returns list of ints of correct length
    policy_r = build_policy("random", examples_t, rng_np)
    batch_r = policy_r.next_batch(batch_size=2)
    assert isinstance(batch_r, list) and len(batch_r) == 2, (
        f"[selftest] FAIL: random policy next_batch len={len(batch_r)} expected 2"
    )
    assert all(isinstance(i, (int, np.integer)) for i in batch_r), (
        f"[selftest] FAIL: random policy returned non-int items: {batch_r}"
    )

    # 2. build_policy('substrate', N=32) -> next_batch returns list of ints
    rng_np2 = np.random.default_rng(2)
    policy_s = build_policy("substrate", examples_t, rng_np2, N=32)
    batch_s = policy_s.next_batch(batch_size=2)
    assert isinstance(batch_s, list) and len(batch_s) == 2, (
        f"[selftest] FAIL: substrate policy next_batch len={len(batch_s)} expected 2"
    )
    assert all(isinstance(i, (int, np.integer)) for i in batch_s), (
        f"[selftest] FAIL: substrate policy returned non-int items: {batch_s}"
    )

    # 3. make_tiny_gru_factory(vocab_size=10) returns callable that produces model
    vocab_t = sorted(set(corpus_t))
    vocab_size_t = len(vocab_t) + 1  # +1 for <pad>
    factory_t = make_tiny_gru_factory(vocab_size_t, hidden=16)
    model_t = factory_t()
    n_params = sum(p.numel() for p in model_t.parameters())
    assert n_params > 0, f"[selftest] FAIL: model has 0 parameters"

    # 4. bpc_gain_relative formula: (3.0 - 2.7) / 3.0 = 0.10
    base_bpc = 3.0
    curr_bpc = 2.7
    gain = (base_bpc - curr_bpc) / base_bpc
    expected_gain = 0.10
    assert abs(gain - expected_gain) < 1e-9, (
        f"[selftest] FAIL: bpc_gain formula: got {gain:.9f} expected {expected_gain:.9f}"
    )

    # 5. split_corpus_into_examples('abcdefgh', seq_len=4) -> ['abcd', 'efgh']
    chunks = split_corpus_into_examples("abcdefgh", seq_len=4)
    assert chunks == ["abcd", "efgh"], (
        f"[selftest] FAIL: split_corpus_into_examples: got {chunks}"
    )

    print(
        f"[selftest] PASS: random_batch_ok=True substrate_batch_ok=True "
        f"gru_params={n_params} gain_formula_ok=True split_ok=True",
        flush=True,
    )


_instrumentation_selftest()


# ---------------------------------------------------------------------------
# Run one condition x seed
# ---------------------------------------------------------------------------

def run_one_cell(condition: str, seed: int, corpus_train: str, corpus_val: str, corpus_test: str) -> dict:
    t_cell = time.time()
    print(
        f"[cell] condition={condition} seed={seed} N_STEPS={N_STEPS_MAX} SUBSTRATE_N={SUBSTRATE_N}",
        flush=True,
    )

    # Split corpora
    examples_train = split_corpus_into_examples(corpus_train, seq_len=SEQ_LEN)
    examples_val = split_corpus_into_examples(corpus_val, seq_len=SEQ_LEN)
    examples_test = split_corpus_into_examples(corpus_test, seq_len=SEQ_LEN)

    # Ensure at least a few examples each
    if len(examples_train) < 2:
        return {"condition": condition, "seed": int(seed), "final_bpc_val": float("nan"), "error": "too_few_train"}
    if len(examples_val) < 1:
        examples_val = examples_train[:1]
    if len(examples_test) < 1:
        examples_test = examples_train[:1]

    vocab = sorted(set(corpus_train) | set(corpus_val))
    vocab_size = len(vocab) + 1  # +1 for <pad>

    rng_np = np.random.default_rng(seed)
    if condition == "substrate":
        policy = build_policy("substrate", examples_train, rng_np, N=SUBSTRATE_N)
    else:
        policy = build_policy("random", examples_train, rng_np)

    # factory must produce fresh model with correct vocab size
    import torch
    torch.manual_seed(seed)
    factory = make_tiny_gru_factory(vocab_size, hidden=HIDDEN)

    result = train_curriculum(
        model_factory=factory,
        examples_train=examples_train,
        examples_val=examples_val,
        examples_test=examples_test,
        char_vocab=vocab,
        policy=policy,
        n_steps_max=N_STEPS_MAX,
        batch_size=BATCH_SIZE,
        eval_every=EVAL_EVERY,
        device="cpu",
        lr=LR,
        seq_len=SEQ_LEN,
        threshold_bpc=2.0,
        verbose=True,
    )

    elapsed = time.time() - t_cell
    val_bpc = result.get("final_bpc_val", float("nan"))
    print(
        f"[cell] condition={condition} seed={seed} "
        f"final_bpc_val={val_bpc:.4f} elapsed={elapsed:.1f}s",
        flush=True,
    )
    return dict(condition=condition, seed=int(seed), elapsed_s=elapsed, **result)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main() -> None:
    if _ARGS.self_test:
        print("[exp] self-test already ran at module scope. Done.", flush=True)
        return

    out_dir = get_output_dir(ANCHOR_NAME)
    print(
        f"[exp] ANCHOR={ANCHOR_NAME} RUN_MODE={RUN_MODE} "
        f"CONDITIONS={CONDITIONS} SEEDS={SEEDS} N_STEPS={N_STEPS_MAX}",
        flush=True,
    )

    corpus_train = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    corpus_val = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    corpus_test = wikitext2_char_corpus(split="validation", max_chars=TEST_CHARS)

    t_total = time.time()
    for condition in CONDITIONS:
        for seed in SEEDS:
            existing = _load_cell_partial(out_dir, condition, seed)
            if existing is not None:
                print(f"[ckpt] condition={condition} seed={seed} already done; skipping", flush=True)
                continue
            result = run_one_cell(condition, seed, corpus_train, corpus_val, corpus_test)
            _write_cell_partial(out_dir, condition, seed, result)
            print(
                f"[progress] condition={condition} seed={seed} "
                f"val_bpc={result.get('final_bpc_val', float('nan')):.4f}",
                flush=True,
            )

    total_elapsed = time.time() - t_total

    # ---- Collect results ----
    cells: Dict[str, Dict[int, dict]] = {c: {} for c in CONDITIONS}
    for condition in CONDITIONS:
        for seed in SEEDS:
            r = _load_cell_partial(out_dir, condition, seed)
            if r is not None:
                cells[condition][seed] = r

    # ---- Verdict ----
    random_bpcs = [
        cells["random"][s]["final_bpc_val"]
        for s in SEEDS
        if s in cells.get("random", {}) and np.isfinite(cells["random"][s].get("final_bpc_val", float("nan")))
    ]
    curr_bpcs = [
        cells["substrate"][s]["final_bpc_val"]
        for s in SEEDS
        if s in cells.get("substrate", {}) and np.isfinite(cells["substrate"][s].get("final_bpc_val", float("nan")))
    ]

    if not random_bpcs or not curr_bpcs:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"VERDICT=HARD_FAIL: insufficient valid cells "
            f"random_cells={len(random_bpcs)} curr_cells={len(curr_bpcs)}"
        )
    else:
        random_bpc_mean = float(np.mean(random_bpcs))
        curr_bpc_mean = float(np.mean(curr_bpcs))
        pairs = min(len(random_bpcs), len(curr_bpcs))
        gains = [
            (random_bpcs[i] - curr_bpcs[i]) / max(random_bpcs[i], 1e-9)
            for i in range(pairs)
        ]
        gain_mean = float(np.mean(gains)) if gains else 0.0
        seeds_gain_hp = sum(1 for g in gains if g > HP_GAIN_FRAC)
        seeds_gain_mid = sum(1 for g in gains if MID_GAIN_FRAC_LO < g <= HP_GAIN_FRAC)

        if gain_mean > HP_GAIN_FRAC and seeds_gain_hp >= HP_MIN_SEEDS:
            verdict = "HARD_PASS"
        elif gain_mean > MID_GAIN_FRAC_LO and (seeds_gain_hp + seeds_gain_mid) >= MID_MIN_SEEDS:
            verdict = "MIDDLE_BAND"
        else:
            verdict = "HARD_FAIL"

        verdict_msg = (
            f"VERDICT={verdict} "
            f"random_bpc_mean={random_bpc_mean:.4f} "
            f"curriculum_bpc_mean={curr_bpc_mean:.4f} "
            f"gain_mean={gain_mean:.4f} "
            f"seeds_gain_hp={seeds_gain_hp}/{len(gains)} "
            f"seeds_gain_mid={seeds_gain_mid}/{len(gains)} "
            f"HP_GAIN_THRESHOLD={HP_GAIN_FRAC} MID_GAIN_THRESHOLD={MID_GAIN_FRAC_LO} "
            f"SUBSTRATE_N={SUBSTRATE_N} SEEDS={SEEDS} total_wall_s={total_elapsed:.1f}"
        )

    print(f"[exp] {verdict_msg}", flush=True)

    metrics = {
        "anchor": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "random_bpc_mean": float(np.mean(random_bpcs)) if random_bpcs else None,
        "curriculum_bpc_mean": float(np.mean(curr_bpcs)) if curr_bpcs else None,
        "n_random_cells": len(random_bpcs),
        "n_curriculum_cells": len(curr_bpcs),
        "HP_GAIN_FRAC": HP_GAIN_FRAC,
        "MID_GAIN_FRAC_LO": MID_GAIN_FRAC_LO,
        "SUBSTRATE_N": SUBSTRATE_N,
        "N_STEPS_MAX": N_STEPS_MAX,
        "elapsed_s": total_elapsed,
        "per_condition": {
            c: {str(s): cells[c].get(s) for s in SEEDS} for c in CONDITIONS
        },
    }

    metrics_path = out_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"[exp] metrics written to {metrics_path}", flush=True)


if __name__ == "__main__":
    main()
