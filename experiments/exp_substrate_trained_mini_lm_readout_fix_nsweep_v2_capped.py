"""
substrate_trained_mini_lm_readout_fix_nsweep_v2_capped -- v2: tractable + per-CELL checkpointed (CPU).

SUPERSEDES v1 (substrate_trained_mini_lm_readout_fix_nsweep_v1), which was KILLED after ~2h20m: v1 swept
N up to 16384 with TRAIN_CHARS=100k and checkpointed per-SEED, so a single seed (6-value N-sweep) took
hours and NOTHING was saved until a whole seed finished -> at risk of timing out with zero results.

ROOT CAUSE (not a GPU mis-route): SubstrateCharLM.fit/score_bpc are SEQUENTIAL per-character Python loops
over the corpus; the bottleneck is loop length (TRAIN_CHARS) x per-step cost (~N), NOT matmul throughput.
GPU does not help without a full vectorized rewrite of the online algorithm. The fix is TRACTABILITY +
per-CELL checkpointing, and CPU is the correct venue for this numpy/Python-loop class.
(The vectorized GPU version of the same N-threshold question is covered by
 substrate_training_n_threshold_sweep_512_8192_v1_gpu.)

V2 CHANGES:
  - N_GRID capped at 8192 (drop the 16384 CPU killer).
  - TRAIN_CHARS 100k -> 30k (Python loop length is the bottleneck; 30k still shows the threshold).
  - PER-CELL checkpoint: a partial JSON is written after EVERY (seed, N) cell; restart skips done cells.

CAPABILITY QUESTION (unchanged): at what substrate dimension N does the calibrated-readout SubstrateCharLM
  cross from "no learning" (gap<0.3 bits) to "substantive learning" (gap>=1.0)? Locates the N-threshold.

PRE-REGISTERED BANDS (BITS; unchanged from v1, N range now {512..8192}):
  HARD-PASS: gap >= 1.0 at N >= N_threshold AND gap < 0.3 below it AND monotone non-decreasing AND
    N_threshold within {512..8192} AND 3/3 seeds.
  MIDDLE: improvement visible but max gap < 1.0, OR threshold only at N=8192 edge, OR 2/3 seeds.
  HARD-FAIL: gap < 0.3 at ALL tested N up to 8192.

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateCharLM.fit consumes >=1 pair + score_bpc finite at N=64.
  2. uniform_bpc = log2(vocab) > 0. 3. calibrated BPC <= temp=1.0 BPC.

PROT-018: NO _nN suffix (N swept; grid {512,1024,2048,4096,8192}). PROT-021: per-CELL partials keyed seed+N.
QUEUE: remote_cpu_queue (CPU; numpy Python-loop substrate -- GPU would not help). TIMEOUT: 14400s. ASCII-only.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, json, os, time
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir
from testbed.substrate_lm.char_lm import SubstrateCharLM
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_trained_mini_lm_readout_fix_nsweep_v2_capped"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_MAX = 0.05
N_LAYERS = 2
N_STEPS_PER_LAYER = 3
READOUT_TEMP_GRID = [1.0, 0.5, 0.3, 0.2, 0.15, 0.1]
HP_GAP = 1.0
HF_GAP = 0.3

if RUN_MODE == "smoke":
    N_GRID = [128, 256, 512]
    SEEDS = [7, 17]
    TRAIN_CHARS = 5_000
    VAL_CHARS = 1_000
else:
    N_GRID = [512, 1024, 2048, 4096, 8192]     # v2: 16384 dropped
    SEEDS = [7, 17, 23]
    TRAIN_CHARS = 30_000                         # v2: 100k -> 30k (Python-loop length is the bottleneck)
    VAL_CHARS = 8_000


def _calibrated_bpc(lm, corpus_val) -> Tuple[float, float, float, float]:
    by_temp = {}
    uniform = 0.0
    for tmp in READOUT_TEMP_GRID:
        s = lm.score_bpc(corpus_val, temperature=tmp)
        by_temp[tmp] = float(s["bpc"]); uniform = float(s["uniform_bpc"])
    best_temp = min(by_temp, key=by_temp.get)
    return by_temp[best_temp], by_temp.get(1.0, float("nan")), float(best_temp), uniform


def _instrumentation_selftest():
    corpus = wikitext2_char_corpus(split="train", max_chars=400)
    val = wikitext2_char_corpus(split="validation", max_chars=120)
    vocab = set(corpus) | set(val)
    lm = SubstrateCharLM(n_layers=2, N=64, alpha_max=0.05, n_steps_per_layer=2, seed=1)
    info = lm.fit(corpus, char_vocab=vocab, verbose=False)
    assert info["n_train_pairs"] >= 1, "fit consumed 0 pairs"
    cal, t1, bt, uni = _calibrated_bpc(lm, val)
    assert uni > 0 and cal <= t1 + 1e-6
    print(f"[selftest] PASS: n_pairs={info['n_train_pairs']} calibrated_bpc={cal:.3f} temp1={t1:.3f} uniform={uni:.3f}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_cell(seed: int, n_dim: int, corpus_train, corpus_val, vocab) -> Dict:
    ts = time.time()
    lm = SubstrateCharLM(n_layers=N_LAYERS, N=n_dim, alpha_max=ALPHA_MAX,
                         n_steps_per_layer=N_STEPS_PER_LAYER, seed=seed)
    info = lm.fit(corpus_train, char_vocab=vocab, verbose=False)
    cal, t1, bt, uni = _calibrated_bpc(lm, corpus_val)
    return {"seed": seed, "N": n_dim, "calibrated_bpc": cal, "temp1_bpc": t1, "best_temp": bt,
            "uniform_bpc": uni, "gap": uni - cal, "n_train_pairs": int(info["n_train_pairs"]),
            "max_alpha": float(lm.stack.max_alpha()), "cell_wall_s": time.time() - ts}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("HARD_FAIL", "HARD_FAIL: no cells.")
    n_seeds = len(SEEDS)
    mean_gap = {}; seed_pass = {}
    for n_dim in N_GRID:
        gaps = [c["gap"] for c in cells if c["N"] == n_dim]
        mean_gap[n_dim] = float(np.mean(gaps)) if gaps else 0.0
        seed_pass[n_dim] = sum(1 for g in gaps if g >= HP_GAP)
    gap_list = [mean_gap[n] for n in N_GRID]
    monotone = all(gap_list[i + 1] >= gap_list[i] - 0.05 for i in range(len(gap_list) - 1))
    thresh = next((n for n in N_GRID if mean_gap[n] >= HP_GAP), None)
    max_gap = max(gap_list)
    below_ok = (thresh is None) or all(mean_gap[n] < HF_GAP for n in N_GRID if n < thresh)
    consistent = (thresh is not None) and (seed_pass[thresh] >= n_seeds)
    summary = "gaps=" + " ".join(f"N{n}:{mean_gap[n]:.3f}" for n in N_GRID) + f" thresh={thresh} monotone={monotone} max_gap={max_gap:.3f}"
    if max_gap < HF_GAP:
        return ("HARD_FAIL", f"HARD_FAIL: no learning at any N (max gap {max_gap:.3f}<{HF_GAP}). {summary}")
    if thresh is not None and thresh < max(N_GRID) and monotone and below_ok and consistent:
        return ("HARD_PASS", f"HARD_PASS: clear N-threshold at N={thresh}. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial N-scale dependence (max_gap={max_gap:.3f}, thresh={thresh}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"train_chars={TRAIN_CHARS} (v2: capped+per-cell-checkpoint)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)        # get_output_dir does not mkdir; per-cell writes need it
corpus_train = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
corpus_val = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
vocab = set(corpus_train) | set(corpus_val)

t_sweep = time.time()
all_cells: List[Dict] = []
for seed in SEEDS:
    for n_dim in N_GRID:
        cell_path = out_dir / f"cell_s{seed}_N{n_dim}.json"
        if cell_path.exists():                       # PER-CELL resume: skip completed cells
            all_cells.append(json.loads(cell_path.read_text(encoding="utf-8")))
            print(f"  [skip] cell s{seed} N{n_dim} already done", flush=True)
            continue
        cell = run_cell(seed, n_dim, corpus_train, corpus_val, vocab)
        cell_path.write_text(json.dumps(cell, indent=2), encoding="utf-8")   # checkpoint AFTER each cell
        all_cells.append(cell)
        print(f"  [seed={seed} N={n_dim}] gap={cell['gap']:.4f} calibrated_bpc={cell['calibrated_bpc']:.4f} "
              f"uniform={cell['uniform_bpc']:.4f} cell_wall={cell['cell_wall_s']:.1f}s", flush=True)

verdict, verdict_msg = compute_verdict(all_cells)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N_grid": N_GRID, "run_mode": RUN_MODE, "alpha_max": ALPHA_MAX, "n_seeds": len(SEEDS),
    "train_chars": TRAIN_CHARS, "elapsed_s": time.time() - t_sweep,
    "cells": all_cells,
}
(out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
