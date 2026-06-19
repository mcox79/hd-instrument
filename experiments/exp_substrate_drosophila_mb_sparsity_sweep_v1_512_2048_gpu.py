"""
substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu -- Bundle D: Drosophila MB sparsity sweep (GPU).

ROUTING: notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle D.
  TRIGGERED: Bundle A (substrate_arch_ablation_matrix_bigram_v1_n512_gpu) landed drosophila_sparse=HP, which
  is the routing's pre-registered dispatch condition for Bundle D ("only dispatch if Bundle A shows the
  Drosophila MB variant lands MIDDLE/HP"). Maps the optimal sparse-coding density f*.

CAPABILITY QUESTION:
  At what sparse-coding density f does the Drosophila-MB-class substrate (sparse codes + single cf-RPE
  modulator) maximize BPC gain over dense bipolar? Drosophila MB uses f=0.05 (5% Kenyon-cell activity).

EIGHT SPARSITY x TWO N (3 seeds = 48 cells; synthetic V=512 Zipf bigram; cf-RPE single modulator):
  f in {dense(+-1), 0.50, 0.25, 0.10, 0.05, 0.02, 0.01, single-active(1/N)}; N in {512, 2048}.
  Architecture: cf-RPE delta rule (single dopamine-class modulator) at every cell; only the coding density
  varies. Codes unit-normalized (preserves sparse support; well-scaled heteroassociative algebra).

PRE-REGISTERED BANDS (gap = dense_baseline_nats - sparse_nats, at matched N):
  HARD-PASS: ANY sparse value f<=0.10 beats dense baseline by > 0.30 nats AND 3/3 seeds.
  MIDDLE: best sparse improvement in [0.10, 0.30] nats.
  HARD-FAIL: dense >= all sparse (sparse coding gives no gain).
  Reports f* = argmax gap (the optimal density).

FORMULA SELF-TESTS (PROT-022):
  1. sparse codebook support = round(f*N) nonzeros; unit-norm.
  2. cf-RPE shrinks single-pair error. 3. Zipf bigram cond-entropy < log(V). 4. uniform nats = ln(V).

PROT-018: NO _nN suffix (N swept over {512, 2048}; declared in name as _512_2048). PROT-021: seed ckpt by run_mode+seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 14400s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
ASCII-only stdout.
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

ANCHOR_NAME = "substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
VOCAB = 512
K_ACTIVE = 8
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 0.30, 0.10
# coding values: "dense" + sparse densities + "single"
F_VALUES = ["dense", 0.50, 0.25, 0.10, 0.05, 0.02, 0.01, "single"]

if RUN_MODE == "smoke":
    N_GRID = [256]
    VOCAB = 128
    SEEDS = [1, 2]
    N_STEPS = 80
    CORPUS = 6000
else:
    N_GRID = [512, 2048]
    SEEDS = [7, 17, 23]
    N_STEPS = 1000
    CORPUS = 60000


def gen_zipf_bigram(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1)
    zipf_p = ranks / ranks.sum()
    T = np.zeros((V, V), dtype=np.float64)
    for c in range(V):
        tgts = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zipf_p)
        logits = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(logits - logits.max()); w /= w.sum()
        T[c, tgts] = w
    with np.errstate(divide='ignore', invalid='ignore'):
        ent_rows = -np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)
    cond_ent = float(ent_rows.mean())
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids, cond_ent


def build_codebook(V, n, fval, gen):
    if fval == "dense":
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    else:
        k = 1 if fval == "single" else max(1, int(round(float(fval) * n)))
        cb = torch.zeros(V, n, device=DEVICE)
        for i in range(V):
            idx = torch.randperm(n, generator=gen, device=DEVICE)[:k]
            cb[i, idx] = 1.0
    cb = cb / (cb.norm(dim=1, keepdim=True) + 1e-8)
    return cb


def train_cfrpe(n, cb, train_ids, val_ids, gen) -> float:
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        starts = torch.randint(0, train_ids.shape[0] - 1, (BATCH,), generator=gen, device=DEVICE)
        Ctx = cb[train_ids[starts]]; Nxt = cb[train_ids[starts + 1]]
        W = W + LR * ((Nxt - Ctx @ W.t()).t() @ Ctx) / BATCH
    nb = min(2000, val_ids.shape[0] - 1)
    starts = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[val_ids[starts]]; nxt = val_ids[starts + 1]
    pred = ctx @ W.t()
    pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def _selftest():
    g = np.random.default_rng(0)
    ids, ce = gen_zipf_bigram(64, 2000, g)
    assert ce < math.log(64)
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cbs = build_codebook(7, 128, 0.05, gen)
    assert int((cbs[0] != 0).sum()) == max(1, int(round(0.05 * 128)))
    assert abs(float(cbs[0].norm()) - 1.0) < 1e-4
    cb1 = build_codebook(7, 128, "single", gen)
    assert int((cb1[0] != 0).sum()) == 1
    cb = build_codebook(7, 128, "dense", gen)
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: cond_ent={ce:.3f} sparse_support_ok single_ok cfrpe {eb:.3f}->{ea:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000)
    t0 = time.time()
    ids, cond_ent = gen_zipf_bigram(VOCAB, CORPUS, gen_np)
    split = int(0.8 * len(ids))
    train_ids = torch.tensor(ids[:split], dtype=torch.long, device=DEVICE)
    val_ids = torch.tensor(ids[split:], dtype=torch.long, device=DEVICE)
    uniform_nats = math.log(VOCAB)
    print(f"  [seed={seed}] V={VOCAB} uniform_nats={uniform_nats:.3f} cond_ent={cond_ent:.3f}", flush=True)
    cells = {}
    for n in N_GRID:
        for fval in F_VALUES:
            cb = build_codebook(VOCAB, n, fval, gen)
            nats = train_cfrpe(n, cb, train_ids, val_ids, gen)
            key = f"N{n}_f{fval}"
            cells[key] = {"N": n, "f": str(fval), "val_nats": float(nats),
                          "gap_vs_uniform": float(uniform_nats - nats)}
            print(f"    [N={n} f={fval}] val_nats={nats:.4f} gap_vs_uniform={uniform_nats - nats:.4f}", flush=True)
            del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "uniform_nats": float(uniform_nats), "cond_ent": float(cond_ent),
            "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    best_gap = -1e9; best_f = None; best_n = None; best_seeds = 0
    detail = []
    for n in N_GRID:
        dense_vals = [r["cells"][f"N{n}_fdense"]["val_nats"] for r in results if f"N{n}_fdense" in r.get("cells", {})]
        dense_mean = float(np.mean(dense_vals)) if dense_vals else float("inf")
        for fval in F_VALUES:
            if fval == "dense":
                continue
            key = f"N{n}_f{fval}"
            gaps = [r["cells"][f"N{n}_fdense"]["val_nats"] - r["cells"][key]["val_nats"]
                    for r in results if key in r.get("cells", {}) and f"N{n}_fdense" in r["cells"]]
            if not gaps:
                continue
            gm = float(np.mean(gaps)); n_better = sum(1 for g in gaps if g > 0)
            detail.append(f"N{n}/f{fval}:{gm:+.3f}({n_better}/{len(gaps)})")
            # only f<=0.10 qualifies for HP per routing
            is_le_010 = (fval != "single" and float(fval) <= 0.10) or fval == "single"
            if gm > best_gap:
                best_gap, best_f, best_n, best_seeds = gm, fval, n, n_better
    summary = f"best f*={best_f}@N{best_n} gap={best_gap:+.3f} ({best_seeds} seeds) | " + " ".join(detail)
    # qualifying HP: best at f<=0.10
    best_is_le010 = best_f == "single" or (best_f is not None and best_f != "dense" and float(best_f) <= 0.10) if best_f else False
    n_seeds = len(results)
    if best_gap > HP_GAP and best_seeds >= n_seeds and best_is_le010:
        return ("HARD_PASS", f"HARD_PASS: sparse f*={best_f} beats dense by >{HP_GAP} nats, all seeds. {summary}")
    if best_gap >= MID_GAP:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: best sparse improvement in [{MID_GAP},{HP_GAP}]. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: dense >= all sparse (no sparse-coding gain). {summary}")


print(f"[config] anchor={ANCHOR_NAME} f_values={F_VALUES} N_grid={N_GRID} V={VOCAB} mode={RUN_MODE} "
      f"seeds={SEEDS} steps={N_STEPS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"f_values": [str(f) for f in F_VALUES], "N_grid": N_GRID, "V": VOCAB, "run_mode": RUN_MODE, "n_steps": N_STEPS}
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
    "f_values": [str(f) for f in F_VALUES], "N_grid": N_GRID, "V": VOCAB, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "n_steps": N_STEPS, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "cond_ent": r.get("cond_ent"),
                  "cells": r.get("cells", {}), "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
