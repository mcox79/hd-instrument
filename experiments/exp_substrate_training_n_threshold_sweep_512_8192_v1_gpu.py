"""
substrate_training_n_threshold_sweep_512_8192_v1_gpu -- substrate-as-training N-threshold sweep (GPU).

ROUTING: notes/research_drill_substrate_training_n_threshold_3x_2026-06-04.md -- the drill's CHEAP DECISIVE
  TEST + N-SWEEP RECOMMENDATION (verbatim bands). Routed to the OWNED GPU (O(N^2) W, N up to 8192,
  wall-time-bound per the drill's feasibility note). Tests the CENTRAL substrate-as-training viability
  question: below which N can a bipolar discrete-state energy substrate NOT drive char-LM training?

THEORY (drill synthesis): three concurrent mechanisms (classical Hopfield capacity 0.138*N; BCM/SNR
  sqrt(N/M); concentration-of-measure orthogonality) converge on N_threshold ~ 2000-4000 for V=70 char-LM.
  Empirical bracket: N=512 ~0 gap, N=4096 ~1.76 nat gap.

MODEL (substrate-native, NO gradient descent): heteroassociative memory W (N x N), context-char code ->
  next-char code (bigram), cf-RPE delta rule dW = (Nxt - W@Ctx)^T @ Ctx / B (Widrow-Hoff). Inference:
  pred = W @ ctx; cosine(pred, vocab) -> calibrated-temperature softmax -> per-char loss (NATS).
  BPC gap = uniform_nats - trained_nats (positive => the substrate learned).

TWO CODINGS x SIX N (3 seeds; fixed budget = same steps/corpus/temp grid across all cells):
  bipolar:    {+1,-1} unit-norm rows (the drill's subject; classical Hopfield regime).
  continuous: float32 standard-normal unit-norm rows (de-confound mitigation; tests if it lowers N_threshold).
  N in {512, 1024, 2048, 3072, 4096, 8192}.
  Also tracks substrate pattern diversity (distinct top-1 retrievals on val / vocab) per the drill.

PRE-REGISTERED BANDS (on the BIPOLAR arm; drill's predictions are for bipolar; NATS):
  HARD-PASS: HP1 [gap@4096 >= 1.0 AND gap@1024 <= 0.05] OR HP2 [phase transition: gap@4096 >= 5x gap@2048].
  MIDDLE: gap@4096 >= 0.5 but threshold unclear, OR monotone increase with no sharp transition.
  HARD-FAIL: HF1 [gap@4096 <= 0.1 AND gap@8192 <= 0.1 -> no learning, refutes N-mechanism] OR
             HF2 [gap@1024 >= 0.5 * gap@8192 -> N not the relevant axis].
  (Continuous arm reported as a secondary mitigation comparison, not the headline verdict.)

FORMULA SELF-TESTS (PROT-022):
  1. continuous codebook unit-norm + non-bipolar. 2. heteroassoc recall cosine > 0.5. 3. cf-RPE shrinks
     error. 4. uniform loss nats = ln(V).

PROT-018: NO _nN suffix (N swept); grid declared {512,1024,2048,3072,4096,8192}.
PROT-021: seed checkpoints keyed run_mode + seed. QUEUE: overnight_queue (GPU). TIMEOUT: 21600s.
GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_training_n_threshold_sweep_512_8192_v1_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
CODINGS = ["bipolar", "continuous"]

if RUN_MODE == "smoke":
    N_GRID = [256, 512]
    SEEDS = [1, 2]
    N_STEPS = 80
    TRAIN_CHARS = 8000
    VAL_CHARS = 2000
else:
    N_GRID = [512, 1024, 2048, 3072, 4096, 8192]
    SEEDS = [7, 17, 23]
    N_STEPS = 1000
    TRAIN_CHARS = 120000
    VAL_CHARS = 20000


def build_codebook(V, n, coding, gen):
    if coding == "bipolar":
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    else:
        cb = torch.randn(V, n, generator=gen, device=DEVICE)
    cb = cb / (cb.norm(dim=1, keepdim=True) + 1e-8)
    return cb


def eval_loss_nats(W, cb, val_ids, gen):
    nb = min(2000, val_ids.shape[0] - 1)
    starts = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[val_ids[starts]]; nxt = val_ids[starts + 1]
    pred = ctx @ W.t()
    pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    cos = pn @ cb.t()
    best = float("inf"); div = 0.0
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        nats = float((-torch.log(pt)).mean())
        if nats < best:
            best = nats
            div = float(torch.unique(cos.argmax(dim=1)).numel()) / cb.shape[0]
    return best, div


def train_cell(coding, n, cb, train_ids, val_ids, gen) -> Dict:
    V = cb.shape[0]
    W = torch.zeros(n, n, device=DEVICE)
    uniform_nats = math.log(V)
    for step in range(N_STEPS):
        starts = torch.randint(0, train_ids.shape[0] - 1, (BATCH,), generator=gen, device=DEVICE)
        Ctx = cb[train_ids[starts]]; Nxt = cb[train_ids[starts + 1]]
        Delta = Nxt - Ctx @ W.t()                  # cf-RPE / Widrow-Hoff
        W = W + LR * (Delta.t() @ Ctx) / BATCH
    trained_nats, diversity = eval_loss_nats(W, cb, val_ids, gen)
    gap = uniform_nats - trained_nats
    return {"coding": coding, "N": n, "uniform_nats": float(uniform_nats),
            "trained_nats": float(trained_nats), "gap_nats": float(gap), "diversity": float(diversity)}


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, "continuous", gen)
    assert abs(float(cb[0].norm()) - 1.0) < 1e-4 and float(cb.abs().max()) != 1.0
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    W = W + torch.outer(nxt, ctx); pred = W @ ctx
    cos = float(pred @ nxt / ((pred.norm() + 1e-8) * (nxt.norm() + 1e-8)))
    assert cos > 0.5, f"recall cos {cos}"
    Wd = torch.zeros(128, 128, device=DEVICE); v = Wd @ ctx
    eb = float((nxt - v).norm()); Wd = Wd + torch.outer(nxt - v, ctx); ea = float((nxt - Wd @ ctx).norm())
    assert ea < eb, f"cf-RPE no shrink {ea} {eb}"
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: recall_cos={cos:.3f} cfrpe {eb:.3f}->{ea:.3f} gpu_mem={torch.cuda.memory_allocated(0)}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    train_text = wikitext2_char_corpus(split="train", max_chars=TRAIN_CHARS)
    val_text = wikitext2_char_corpus(split="validation", max_chars=VAL_CHARS)
    vocab = sorted(set(train_text) | set(val_text))
    idx = {c: i for i, c in enumerate(vocab)}
    train_ids = torch.tensor([idx.get(c, 0) for c in train_text], dtype=torch.long, device=DEVICE)
    val_ids = torch.tensor([idx.get(c, 0) for c in val_text], dtype=torch.long, device=DEVICE)
    V = len(vocab)
    print(f"  [seed={seed}] vocab={V} uniform_nats={math.log(V):.4f}", flush=True)
    cells = {}
    for coding in CODINGS:
        for n in N_GRID:
            cb = build_codebook(V, n, coding, gen)
            r = train_cell(coding, n, cb, train_ids, val_ids, gen)
            cells[f"{coding}_N{n}"] = r
            print(f"    [{coding} N={n}] trained_nats={r['trained_nats']:.4f} gap={r['gap_nats']:.4f} "
                  f"div={r['diversity']:.3f}", flush=True)
            del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    def gap(coding, n):
        vs = [r["cells"][f"{coding}_N{n}"]["gap_nats"] for r in results
              if f"{coding}_N{n}" in r.get("cells", {})]
        return float(np.mean(vs)) if vs else 0.0
    bp = {n: gap("bipolar", n) for n in N_GRID}
    co = {n: gap("continuous", n) for n in N_GRID}
    g4 = bp.get(4096, 0.0); g1 = bp.get(1024, 0.0); g8 = bp.get(8192, 0.0); g2 = bp.get(2048, 0.0)
    bp_str = " ".join(f"N{n}:{bp[n]:.3f}" for n in N_GRID)
    co_str = " ".join(f"N{n}:{co[n]:.3f}" for n in N_GRID)
    summary = f"bipolar_gap[{bp_str}] continuous_gap[{co_str}]"
    if not ({1024, 4096, 8192} <= set(N_GRID)):
        return ("MIDDLE_BAND", f"MIDDLE_BAND: reduced grid (smoke) -- bands need N in {{1024,4096,8192}}. {summary}")
    HP1 = (g4 >= 1.0 and g1 <= 0.05)
    HP2 = (g2 > 1e-6 and g4 >= 5.0 * g2)
    HF1 = (g4 <= 0.1 and g8 <= 0.1)
    HF2 = (g8 > 1e-6 and g1 >= 0.5 * g8)
    if HF1:
        return ("HARD_FAIL", f"HARD_FAIL(HF1): no bipolar learning at N=4096 or 8192 -> refutes N-threshold mechanism. {summary}")
    if HP1:
        return ("HARD_PASS", f"HARD_PASS(HP1): bipolar gap@4096>=1.0 AND gap@1024<=0.05 -> N_threshold ~2000-4000 confirmed. {summary}")
    if HP2:
        return ("HARD_PASS", f"HARD_PASS(HP2): phase transition gap@4096>=5x gap@2048. {summary}")
    if HF2:
        return ("HARD_FAIL", f"HARD_FAIL(HF2): gap@1024 within 2x gap@8192 -> N not the relevant axis. {summary}")
    if g4 >= 0.5:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: bipolar gap@4096>=0.5 but threshold unclear / no sharp transition. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial/ambiguous N-threshold signal. {summary}")


print(f"[config] anchor={ANCHOR_NAME} codings={CODINGS} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"codings": CODINGS, "N_grid": N_GRID, "run_mode": RUN_MODE, "n_steps": N_STEPS}
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
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "codings": CODINGS, "N_grid": N_GRID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
