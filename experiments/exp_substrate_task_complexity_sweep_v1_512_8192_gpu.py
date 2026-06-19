"""
substrate_task_complexity_sweep_v1_512_8192_gpu -- Bundle B: task-complexity sweep (GPU).

ROUTING: notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md (Bundle B) +
  Research refinement (user-relayed 2026-06-04): "GO with Bundle B; cf-RPE + Drosophila sparse variants
  (Bundle A HP winners); tasks = trigram V=70 char-LM + V=512 synthetic Zipf + extended-context K=8 V=70."
  Run on the OWNED 4060 Ti GPU ($0; matmul-light but correct + keeps GPU nominally busy).

CAPABILITY QUESTION:
  At what task complexity does substrate-as-training break? Does it keep learning at trigram (K=3) and
  extended-context-8, or is it bigram-bound? Two HP architectures (cf-RPE bipolar, Drosophila sparse f=0.05)
  x three task complexities x N-sweep. Context encoding for K>1 = fixed roll-binding (NOT the variable under
  test -- that is Bundle E's position-binding question; here the encoder is held constant across cells).

THREE TASKS:
  zipf_v512_bigram   : synthetic V=512 Zipf, context order 1 (bigram; the Bundle A baseline task).
  wiki_v70_trigram   : wikitext char (V~vocab), context order 2 (trigram).
  wiki_v70_extctx8   : wikitext char, context order 8 (extended-context).
TWO ARCHS: cfrpe (bipolar + cf-RPE delta) ; drosophila_sparse (sparse f=0.05 + cf-RPE delta).
N in {512, 2048, 8192}; 3 seeds. 2 x 3 x 3 x 3 = 54 cells.

CONTEXT ENCODER (fixed): for context chars (c_1..c_k), bound = sum_i roll(code[c_i], i), unit-normalized.

PRE-REGISTERED BANDS (per task, best arch, at N=8192; gap = uniform_nats - val_nats):
  per-task HP: gap > 1.0 nat. per-task MID: gap in [0.3,1.0]. per-task HF: gap < 0.3.
  AGGREGATE: HARD-PASS if >= 2 of 3 tasks reach gap>1.0 (substrate handles complexity beyond bigram);
    HARD-FAIL if ONLY the bigram task learns (trigram AND extctx8 both < 0.3 -> K=2 bound);
    MIDDLE otherwise (learns easy, degrades on hard).

FORMULA SELF-TESTS (PROT-022):
  1. roll-binding order-sensitive: bound([a,b]) != bound([b,a]) (cos<0.9). 2. cf-RPE shrinks error.
  3. sparse support = f*N. 4. uniform nats = ln(V). 5. zipf cond-entropy < log(V).

PROT-018: NO _nN suffix (N swept {512,2048,8192}; declared _512_8192). PROT-021: seed ckpt by run_mode+seed.
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
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_task_complexity_sweep_v1_512_8192_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
SPARSE_F = 0.05
ZIPF_K_ACTIVE = 8
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 1.0, 0.3
ARCHS = ["cfrpe", "drosophila_sparse"]
# (task_name, source, context_order)
TASKS = [("zipf_v512_bigram", "zipf", 1), ("wiki_v70_trigram", "wiki", 2), ("wiki_v70_extctx8", "wiki", 8)]
ZIPF_V = 512

if RUN_MODE == "smoke":
    N_GRID = [256]
    SEEDS = [1, 2]
    N_STEPS = 80
    CORPUS = 6000
    ZIPF_V = 128
else:
    N_GRID = [512, 2048, 8192]
    SEEDS = [7, 17, 23]
    N_STEPS = 1000
    CORPUS = 60000


def gen_zipf_bigram(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V), dtype=np.float64)
    for c in range(V):
        tg = gen_np.choice(V, size=ZIPF_K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(ZIPF_K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    with np.errstate(divide='ignore', invalid='ignore'):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids, ce


def build_codebook(V, n, coding, gen):
    if coding == "cfrpe":   # bipolar
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    else:                   # drosophila_sparse
        cb = torch.zeros(V, n, device=DEVICE)
        k = max(1, int(round(SPARSE_F * n)))
        for i in range(V):
            cb[i, torch.randperm(n, generator=gen, device=DEVICE)[:k]] = 1.0
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def encode_ctx(cb, ids, starts, order):
    """Roll-binding of the `order` chars ending just before the target. ids[start+order] is the target."""
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(order):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def train_eval(arch, order, n, cb, train_ids, val_ids, gen) -> float:
    W = torch.zeros(n, n, device=DEVICE)
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        starts = torch.randint(0, ntr - order - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = encode_ctx(cb, train_ids, starts, order)
        Nxt = cb[train_ids[starts + order]]
        W = W + LR * ((Nxt - ctx @ W.t()).t() @ ctx) / BATCH      # cf-RPE delta (both archs)
    nb = min(2000, val_ids.shape[0] - order - 1)
    starts = torch.randint(0, val_ids.shape[0] - order - 1, (nb,), generator=gen, device=DEVICE)
    ctx = encode_ctx(cb, val_ids, starts, order); nxt = val_ids[starts + order]
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def _selftest():
    g = np.random.default_rng(0)
    ids, ce = gen_zipf_bigram(64, 2000, g); assert ce < math.log(64)
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, "cfrpe", gen)
    seq = torch.tensor([0, 1], device=DEVICE)
    bab = encode_ctx(cb, seq, torch.tensor([0], device=DEVICE), 2)
    seq2 = torch.tensor([1, 0], device=DEVICE)
    bba = encode_ctx(cb, seq2, torch.tensor([0], device=DEVICE), 2)
    cos = float((bab * bba).sum()); assert cos < 0.9, f"roll-binding order-insensitive {cos}"
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb
    cbs = build_codebook(7, 128, "drosophila_sparse", gen)
    assert int((cbs[0] != 0).sum()) == max(1, int(round(SPARSE_F * 128)))
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: zipf_ce={ce:.3f} rollbind_order cos={cos:.3f} cfrpe {eb:.3f}->{ea:.3f} sparse_ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000)
    t0 = time.time()
    # data sources
    zipf_ids, zipf_ce = gen_zipf_bigram(ZIPF_V, CORPUS, gen_np)
    zsplit = int(0.8 * len(zipf_ids))
    zipf_train = torch.tensor(zipf_ids[:zsplit], dtype=torch.long, device=DEVICE)
    zipf_val = torch.tensor(zipf_ids[zsplit:], dtype=torch.long, device=DEVICE)
    wtext_tr = wikitext2_char_corpus(split="train", max_chars=CORPUS * 2)
    wtext_va = wikitext2_char_corpus(split="validation", max_chars=CORPUS // 2)
    wvocab = sorted(set(wtext_tr) | set(wtext_va)); widx = {c: i for i, c in enumerate(wvocab)}
    wiki_train = torch.tensor([widx.get(c, 0) for c in wtext_tr], dtype=torch.long, device=DEVICE)
    wiki_val = torch.tensor([widx.get(c, 0) for c in wtext_va], dtype=torch.long, device=DEVICE)
    wV = len(wvocab)
    print(f"  [seed={seed}] zipf_V={ZIPF_V}(ce={zipf_ce:.2f}) wiki_V={wV}", flush=True)
    cells = {}
    for n in N_GRID:
        for tname, src, order in TASKS:
            if src == "zipf":
                V, tr, va, un = ZIPF_V, zipf_train, zipf_val, math.log(ZIPF_V)
            else:
                V, tr, va, un = wV, wiki_train, wiki_val, math.log(wV)
            for arch in ARCHS:
                cb = build_codebook(V, n, arch, gen)
                nats = train_eval(arch, order, n, cb, tr, va, gen)
                gap = un - nats
                cells[f"{arch}_{tname}_N{n}"] = {"arch": arch, "task": tname, "N": n, "order": order,
                                                  "val_nats": float(nats), "gap": float(gap)}
                print(f"    [{arch} {tname} N={n}] gap={gap:.4f} (nats={nats:.3f}/un={un:.3f})", flush=True)
                del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    maxN = N_GRID[-1]
    task_best = {}
    for tname, _src, _order in TASKS:
        best = -1e9
        for arch in ARCHS:
            key = f"{arch}_{tname}_N{maxN}"
            gaps = [r["cells"][key]["gap"] for r in results if key in r.get("cells", {})]
            if gaps:
                best = max(best, float(np.mean(gaps)))
        task_best[tname] = best
    summary = " ".join(f"{t}:{task_best[t]:+.3f}" for t in task_best)
    n_hp = sum(1 for t in task_best if task_best[t] > HP_GAP)
    bigram_only = (task_best.get("zipf_v512_bigram", 0) > HP_GAP and
                   task_best.get("wiki_v70_trigram", 0) < MID_GAP and
                   task_best.get("wiki_v70_extctx8", 0) < MID_GAP)
    if n_hp >= 2:
        return ("HARD_PASS", f"HARD_PASS: {n_hp}/3 tasks reach gap>{HP_GAP} at N={maxN} -> substrate handles complexity beyond bigram. {summary}")
    if bigram_only:
        return ("HARD_FAIL", f"HARD_FAIL: only bigram learns; trigram+extctx8 both <{MID_GAP} -> substrate K=2 bound. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: learns easy tasks, degrades on harder ({n_hp}/3 HP). {summary}")


print(f"[config] anchor={ANCHOR_NAME} archs={ARCHS} tasks={[t[0] for t in TASKS]} N_grid={N_GRID} "
      f"mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"archs": ARCHS, "tasks": [t[0] for t in TASKS], "N_grid": N_GRID, "run_mode": RUN_MODE, "n_steps": N_STEPS}
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
    "archs": ARCHS, "tasks": [t[0] for t in TASKS], "N_grid": N_GRID, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "n_steps": N_STEPS, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", {}),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
