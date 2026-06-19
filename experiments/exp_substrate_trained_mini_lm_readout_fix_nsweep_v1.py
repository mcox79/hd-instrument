"""
substrate_trained_mini_lm_readout_fix_nsweep_v1 -- substrate-trained mini-LM N-sweep, calibrated readout.

ROUTING: notes/routing_substrate_training_n_sweep_readout_fix_2026-06-04.md (Research; USER AUTHORIZED).

CAPABILITY QUESTION:
  At what substrate dimension N does the substrate-trained mini-LM (calibrated readout temp) cross from
  "no learning" (N=512: BPC gap ~0.02 below uniform) to "substantive learning" (Exp-Dev preview: gap
  ~1.76)? Substrate signal scales with N (bipolar quantization MI per coord; SNR ~ sqrt(N)); this sweep
  locates the N-threshold and locks the substrate-as-training-mechanism story to a scale claim.

DESIGN: same 4-primitive SubstrateCharLM scaffold (alpha_max=0.05, n_layers=2), readout BPC scored at a
  CALIBRATED temperature (min over a small grid; identical procedure per cell -> fair). Sweep substrate
  dimension N over {512,1024,2048,4096,8192,16384}; 3 seeds each. Metric: calibrated val BPC (bits) and
  gap = uniform_bpc - calibrated_bpc per N.

PRE-REGISTERED BANDS (per routing; BITS):
  HARD-PASS (clear N-threshold): gap >= 1.0 at N >= N_threshold AND gap < 0.3 at N < N_threshold AND
    gap monotone non-decreasing in N (no inversions) AND N_threshold within {512..16384} AND 3/3 seeds.
  MIDDLE: improvement visible at large N but max gap < 1.0, OR threshold at edge (only at N=16384),
    OR 2/3 seeds consistent.
  HARD-FAIL (refutes de-confound): gap < 0.3 at ALL tested N up to 16384.

FORMULA SELF-TESTS (PROT-022):
  1. SubstrateCharLM.fit consumes >=1 pair + score_bpc finite at N=64.
  2. uniform_bpc = log2(vocab) > 0.
  3. calibrated BPC <= temp=1.0 BPC (calibration never worse).

PROT-018: NO _nN suffix (N is the swept variable); N grid declared = {512,1024,2048,4096,8192,16384}.
PROT-021: source=local CPU, run_mode=full, n_seeds=3; partials keyed by seed.
QUEUE: remote_cpu_queue (CPU; pure numpy substrate). TIMEOUT: ~3-5h sequential.
ASCII-only stdout.
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
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials
from testbed.substrate_lm.char_lm import SubstrateCharLM
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_trained_mini_lm_readout_fix_nsweep_v1"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_MAX = 0.05
N_LAYERS = 2
N_STEPS_PER_LAYER = 3
READOUT_TEMP_GRID = [1.0, 0.5, 0.3, 0.2, 0.15, 0.1]
HP_GAP = 1.0          # gap = uniform_bpc - bpc >= this -> "substantive learning"
HF_GAP = 0.3          # gap < this -> "no learning"

if RUN_MODE == "smoke":
    N_GRID = [128, 256, 512]
    SEEDS = [7, 17]
    TRAIN_CHARS = 5_000
    VAL_CHARS = 1_000
else:
    N_GRID = [512, 1024, 2048, 4096, 8192, 16384]
    SEEDS = [7, 17, 23]
    TRAIN_CHARS = 100_000
    VAL_CHARS = 20_000


def _calibrated_bpc(lm, corpus_val) -> Tuple[float, float, float, float]:
    """Return (calibrated_bpc, temp1_bpc, best_temp, uniform_bpc)."""
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
    assert uni > 0, "uniform_bpc not positive"
    assert cal <= t1 + 1e-6, f"calibrated ({cal}) worse than temp1 ({t1})"
    print(f"[selftest] PASS: n_pairs={info['n_train_pairs']} calibrated_bpc={cal:.3f} "
          f"temp1_bpc={t1:.3f} uniform={uni:.3f} best_temp={bt}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    corpus_train = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    corpus_val = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = set(corpus_train) | set(corpus_val)
    cells = []
    for n_dim in N_GRID:
        ts = time.time()
        lm = SubstrateCharLM(n_layers=N_LAYERS, N=n_dim, alpha_max=ALPHA_MAX,
                             n_steps_per_layer=N_STEPS_PER_LAYER, seed=seed)
        info = lm.fit(corpus_train, char_vocab=vocab, verbose=False)
        cal, t1, bt, uni = _calibrated_bpc(lm, corpus_val)
        gap = uni - cal
        cells.append({"N": n_dim, "calibrated_bpc": cal, "temp1_bpc": t1, "best_temp": bt,
                      "uniform_bpc": uni, "gap": gap, "n_train_pairs": int(info["n_train_pairs"]),
                      "max_alpha": float(lm.stack.max_alpha())})
        print(f"  [seed={seed} N={n_dim}] calibrated_bpc={cal:.4f} temp1_bpc={t1:.4f} gap={gap:.4f} "
              f"uniform={uni:.4f} pairs={info['n_train_pairs']} max_alpha={lm.stack.max_alpha():.4f} "
              f"cell_wall={time.time()-ts:.1f}s", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    n_seeds = len(results)
    mean_gap = {}
    seed_pass = {}   # per N: how many seeds have gap >= HP_GAP
    for n_dim in N_GRID:
        gaps = [c["gap"] for r in results for c in r.get("cells", []) if c["N"] == n_dim]
        mean_gap[n_dim] = float(np.mean(gaps)) if gaps else 0.0
        seed_pass[n_dim] = sum(1 for g in gaps if g >= HP_GAP)
    gap_list = [mean_gap[n] for n in N_GRID]
    monotone = all(gap_list[i + 1] >= gap_list[i] - 0.05 for i in range(len(gap_list) - 1))
    # N_threshold = first N with mean_gap >= HP_GAP
    thresh = None
    for n_dim in N_GRID:
        if mean_gap[n_dim] >= HP_GAP:
            thresh = n_dim; break
    max_gap = max(gap_list)
    below_ok = (thresh is None) or all(mean_gap[n] < HF_GAP for n in N_GRID if n < thresh)
    seeds_consistent_at_thresh = (thresh is not None) and (seed_pass[thresh] >= n_seeds)
    summary = ("gaps=" + " ".join(f"N{n}:{mean_gap[n]:.3f}" for n in N_GRID) +
               f" thresh={thresh} monotone={monotone} max_gap={max_gap:.3f}")

    if max_gap < HF_GAP:
        return ("HARD_FAIL",
                f"HARD_FAIL: no learning at any N (max gap {max_gap:.3f} < {HF_GAP}); de-confound refuted. {summary}")
    if (thresh is not None and thresh < max(N_GRID) and monotone and below_ok and seeds_consistent_at_thresh):
        return ("HARD_PASS",
                f"HARD_PASS: clear N-threshold at N={thresh} (gap>={HP_GAP} above, <{HF_GAP} below, monotone, "
                f"{n_seeds}/{n_seeds} seeds). {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial N-scale dependence (max_gap={max_gap:.3f}, thresh={thresh}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"alpha_max={ALPHA_MAX} temp_grid={READOUT_TEMP_GRID}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "run_mode": RUN_MODE, "alpha_max": ALPHA_MAX, "seeds": SEEDS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N_grid": N_GRID, "run_mode": RUN_MODE, "alpha_max": ALPHA_MAX, "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
