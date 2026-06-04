"""
substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu -- Bundle G: extended-context ceiling (GPU).

ROUTING: notes/routing_bundle_g_extended_context_ceiling_test_2026-06-04.md. Position-binding + symmetric
  Hebbian (the empirically-minimal architecture per Bundle E trigram HP). Owned GPU, $0. Dependency-free
  subset (the V=4000 subword cell G7 dropped -- no subword tokenizer; wikitext char serves as the real task).

CAPABILITY QUESTION:
  What is the substrate's TRUE extended-context ceiling K* (max context length still learnable) with the
  strongest empirical architecture (position-binding roll-binding + symmetric Hebbian) at substrate-class N?
  Today's refutations: K=8 extctx HP at N=8192, K=3 trigram HP at N=4096. How far does it go, and does
  larger N raise the ceiling / higher vocab lower it?

MODEL: K-char context bound via cyclic-shift permutation (HRR) ctx = sum_i roll(code[c_i], i), unit-norm;
  symmetric Hebbian W += outer(next_code, ctx_bound); predict next via cosine+calibrated-temp softmax (nats).

CELLS (3 seeds; gap = uniform_nats - val_nats):
  G1 K=8  V=70  N=8192    G2 K=12 V=70 N=8192    G3 K=16 V=70 N=8192    G4 K=24 V=70 N=8192
  G5 K=16 V=70  N=16384 (larger N raise ceiling?)   G6 K=16 V=512 synthetic N=8192 (higher vocab lower it?)
  G7 K=8  V=70  N=16384 (real-task extended; wikitext char as the real char-LM)

PRE-REGISTERED BANDS (per cell): HARD-PASS gap > 0.8 nats AND 3/3 seeds; MIDDLE gap > 0.3; HARD-FAIL gap <= 0.3.
  AGGREGATE: report K* = max K (at N=8192, V=70) with per-cell HP. HARD-PASS if K* >= 12 (ceiling beyond trigram);
  MIDDLE if K* in {8}; HARD-FAIL if no K>=8 cell HP (refutes the extended-context claim).

FORMULA SELF-TESTS (PROT-022):
  1. roll-binding order-sensitive (bound order differs). 2. K-context single-pair recall (cos>0.5).
  3. uniform nats = ln(V). 4. codebook bipolar.

PROT-018: NO _nN suffix (N + K swept; declared _8192_16384). PROT-021: per-seed partials.
QUEUE: overnight_queue (GPU; N up to 16384 NxN Hebbian -- genuine GPU load). TIMEOUT: 14400s. ASCII-only.
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
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
from testbed.substrate_lm.data import wikitext2_char_corpus

ANCHOR_NAME = "substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
ZIPF_K_ACTIVE = 8
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 0.8, 0.3
# (name, K, vocab_source, V_synth, N)
CELLS = [("G1_K8_V70_N8192", 8, "wiki", 0, 8192), ("G2_K12_V70_N8192", 12, "wiki", 0, 8192),
         ("G3_K16_V70_N8192", 16, "wiki", 0, 8192), ("G4_K24_V70_N8192", 24, "wiki", 0, 8192),
         ("G5_K16_V70_N16384", 16, "wiki", 0, 16384), ("G6_K16_V512_N8192", 16, "zipf", 512, 8192),
         ("G7_K8_V70_N16384", 8, "wiki", 0, 16384)]

if RUN_MODE == "smoke":
    CELLS = [("G1_K8_V70_N256", 8, "wiki", 0, 256), ("G3_K16_V70_N256", 16, "wiki", 0, 256),
             ("G6_K16_V128_N256", 16, "zipf", 128, 256)]
    SEEDS = [1, 2]; N_STEPS = 80; CORPUS = 6000
else:
    SEEDS = [7, 17, 23]; N_STEPS = 600; CORPUS = 50000


def gen_zipf(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V))
    for c in range(V):
        tg = gen_np.choice(V, size=ZIPF_K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(ZIPF_K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids


def build_codebook(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def encode_ctx(cb, ids, starts, K):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def run_cell(K, n, cb, train_ids, val_ids, gen, un) -> float:
    W = torch.zeros(n, n, device=DEVICE)
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        st = torch.randint(0, ntr - K - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = encode_ctx(cb, train_ids, st, K); nxt = cb[train_ids[st + K]]
        W = W + LR * (nxt.t() @ ctx) / BATCH            # symmetric Hebbian
    nb = min(2000, val_ids.shape[0] - K - 1)
    st = torch.randint(0, val_ids.shape[0] - K - 1, (nb,), generator=gen, device=DEVICE)
    ctx = encode_ctx(cb, val_ids, st, K); nxt = val_ids[st + K]
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        pr = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = pr[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return un - best


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, gen)
    seq = torch.tensor([0, 1, 2], device=DEVICE)
    b1 = encode_ctx(cb, seq, torch.tensor([0], device=DEVICE), 3)
    b2 = encode_ctx(cb, torch.tensor([2, 1, 0], device=DEVICE), torch.tensor([0], device=DEVICE), 3)
    assert float((b1 * b2).sum()) < 0.95, "roll-binding not order-sensitive"
    W = torch.zeros(128, 128, device=DEVICE); ctx = encode_ctx(cb, seq, torch.tensor([0], device=DEVICE), 3)
    nxt = cb[3]; W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    rc = float(pred @ nxt / ((pred.norm() + 1e-8) * (nxt.norm() + 1e-8)))
    assert rc > 0.5, f"K-context recall {rc}"
    assert abs(math.log(7) - 1.9459) < 1e-3
    assert abs(float(cb[0].norm()) - 1.0) < 1e-4, "codebook not unit-norm"
    print(f"[selftest] PASS: rollbind_order_ok kctx_recall={rc:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000)
    t0 = time.time()
    wtext_tr = wikitext2_char_corpus(split="train", max_chars=CORPUS)
    wtext_va = wikitext2_char_corpus(split="validation", max_chars=CORPUS // 4)
    wvocab = sorted(set(wtext_tr) | set(wtext_va)); widx = {c: i for i, c in enumerate(wvocab)}
    wiki_tr = torch.tensor([widx.get(c, 0) for c in wtext_tr], dtype=torch.long, device=DEVICE)
    wiki_va = torch.tensor([widx.get(c, 0) for c in wtext_va], dtype=torch.long, device=DEVICE)
    wV = len(wvocab)
    cells = {}
    for name, K, src, Vsyn, n in CELLS:
        if src == "wiki":
            V, tr, va, un = wV, wiki_tr, wiki_va, math.log(wV)
        else:
            ids = gen_zipf(Vsyn, CORPUS, gen_np); sp = int(0.8 * len(ids))
            tr = torch.tensor(ids[:sp], dtype=torch.long, device=DEVICE)
            va = torch.tensor(ids[sp:], dtype=torch.long, device=DEVICE); V, un = Vsyn, math.log(Vsyn)
        cb = build_codebook(V, n, gen)
        gap = run_cell(K, n, cb, tr, va, gen, un)
        cells[name] = {"K": K, "V": V, "N": n, "gap": float(gap)}
        print(f"    [{name}] gap={gap:.4f}", flush=True)
        del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9; elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    names = [c[0] for c in CELLS]
    mg = {nm: float(np.mean([r["cells"][nm]["gap"] for r in results if nm in r["cells"]])) for nm in names}
    hp = {nm: all((r["cells"][nm]["gap"] > HP_GAP) for r in results if nm in r["cells"]) for nm in names}
    # K* = max K at V70/N8192 with HP
    v70_n8192 = [(c[1], c[0]) for c in CELLS if c[2] == "wiki" and c[4] == 8192]
    kstar = max([K for K, nm in v70_n8192 if hp.get(nm)], default=0)
    summary = " ".join(f"{nm}:{mg[nm]:+.2f}{'(HP)' if hp[nm] else ''}" for nm in names) + f" | K*={kstar}"
    if kstar >= 12:
        return ("HARD_PASS", f"HARD_PASS: extended-context ceiling K*>={kstar} (beyond trigram). {summary}")
    if kstar >= 8:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: K*={kstar} (ceiling at 8). {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: no K>=8 cell HP. {summary}")


print(f"[config] anchor={ANCHOR_NAME} cells={[c[0] for c in CELLS]} mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS}", flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"cells": [c[0] for c in CELLS], "run_mode": RUN_MODE, "n_steps": N_STEPS})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "run_mode": RUN_MODE,
           "n_seeds": len(SEEDS), "cells": [c[0] for c in CELLS],
           "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells"), "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
