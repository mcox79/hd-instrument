"""
substrate_arch_ablation_matrix_bigram_v1_n512_gpu -- Bundle A: architectural-ablation matrix (GPU).

ROUTING: notes/routing_bundled_substrate_explorations_for_gpu_occupancy_2026-06-04.md, Bundle A -- the
  IMMEDIATE highest-value dispatch. REPLACES the 7-individual-test convergent batch (same architectural
  coverage, one dispatch). Bundled to keep the 4060 Ti occupied + cover more design space per dispatch.

CAPABILITY QUESTION:
  Of the 7 brain-drill-identified architectural variants, which (if any) give measurable BPC gain over the
  K=1 Hebbian baseline at the SAME task + scale? Task = synthetic V=512 Zipf bigram (deliberately harder
  than wikitext char-bigram, where all architectures saturated at ~1.2 nat gap with no differentiation).

SEVEN VARIANTS (5 seeds each = 35 cells; N=512 substrate, ~V=512 codes, 1000 training steps):
  1. hebbian_k1     : pure Hebbian outer-product dW = Nxt^T Ctx (current substrate baseline; bipolar).
  2. cfrpe          : Hebbian + rank-1 counterfactual substitution (Widrow-Hoff delta) dW = (Nxt - W Ctx)^T Ctx.
  3. drosophila_sparse: sparse {0,1} f=0.05 codes + single cf-RPE modulator (Drosophila MB template).
  4. stdp_asym      : W += LR*(W_Hebbian + 0.5 * W_STDP), W_STDP = antisymmetric (Nxt^T Ctx - Ctx^T Nxt) (order).
  5. friston_fep    : precision-weighted cf-RPE dW = (Pi * eps)^T Ctx, Pi = 1/running-var(eps) (FEP precision).
  6. two_region     : codes split N/2 bipolar (region 1, Hebbian) + N/2 sparse (region 2, sparse-Hebbian); cf-RPE per region.
  7. bottleneck_adaptor: K=8 W-expert channels, bottleneck random-projection router (top-1 gate); cf-RPE to gated expert.

  All use continuous-cosine readout (calibrated temperature) -> per-char loss in NATS. Codings noted per variant.

PRE-REGISTERED BANDS (per-variant; gap_vs_baseline = baseline_nats - variant_nats):
  HP per variant: variant beats K=1 baseline by > 0.30 nats AND on 4/5 seeds.
  MIDDLE: 0.10-0.30 nats better.
  HARD-FAIL: variant >= baseline (no measurable gain).
AGGREGATE verdict:
  HARD-PASS if ANY of the 6 non-baseline variants lands HP.
  HARD-FAIL if ALL 6 land HF (refutes ALL brain-drill predictions at the bigram task).
  MIDDLE otherwise.

FORMULA SELF-TESTS (PROT-022):
  1. Zipf bigram corpus: conditional entropy H(next|ctx) < log(V) (learnable structure).
  2. cf-RPE shrinks single-pair error. 3. STDP antisymmetric part has zero diagonal-symmetry (W_STDP+W_STDP^T=0).
  4. sparse codebook support = f*N. 5. uniform loss nats = ln(V).

PROT-018: anchor _n512 -> substrate N=512. PROT-021: seed checkpoints keyed run_mode+seed.
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

ANCHOR_NAME = "substrate_arch_ablation_matrix_bigram_v1_n512_gpu"
_N_SUFFIX = 512
N = 512
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
VOCAB = 512
K_ACTIVE = 8          # nonzero next-chars per context in the Zipf bigram transition
SPARSE_F = 0.05
K_CHANNELS = 8
BNECK = 64            # bottleneck-adaptor router projection dim
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
HP_GAP, MID_GAP = 0.30, 0.10
VARIANTS = ["hebbian_k1", "cfrpe", "drosophila_sparse", "stdp_asym", "friston_fep", "two_region", "bottleneck_adaptor"]

if RUN_MODE == "smoke":
    N_DIM = 256
    VOCAB = 128
    SEEDS = [1, 2]
    N_STEPS = 80
    CORPUS = 6000
else:
    N_DIM = N
    SEEDS = [7, 17, 23, 31, 41]
    N_STEPS = 1000
    CORPUS = 60000


def gen_zipf_bigram(V, length, gen_np):
    """Synthetic Zipf bigram corpus. Transition T: each ctx -> K_ACTIVE targets with softmax logits;
    target choice weighted by Zipf so the marginal is Zipf-like. Returns ids (length,) + cond entropy."""
    ranks = 1.0 / np.arange(1, V + 1)
    zipf_p = ranks / ranks.sum()
    T = np.zeros((V, V), dtype=np.float64)
    for c in range(V):
        tgts = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zipf_p)
        logits = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(logits - logits.max()); w /= w.sum()
        T[c, tgts] = w
    # conditional entropy (uniform over contexts, in nats)
    with np.errstate(divide='ignore', invalid='ignore'):
        ent_rows = -np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)
    cond_ent = float(ent_rows.mean())
    ids = np.zeros(length, dtype=np.int64)
    s = 0
    for i in range(length):
        ids[i] = s
        s = gen_np.choice(V, p=T[s])
    return ids, cond_ent


def build_codebook(V, n, coding, gen):
    if coding == "bipolar":
        cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    elif coding == "sparse":
        cb = torch.zeros(V, n, device=DEVICE)
        k = max(1, int(round(SPARSE_F * n)))
        for i in range(V):
            idx = torch.randperm(n, generator=gen, device=DEVICE)[:k]
            cb[i, idx] = 1.0
    elif coding == "split":   # first half bipolar, second half sparse (variant 6)
        h = n // 2
        cb = torch.zeros(V, n, device=DEVICE)
        cb[:, :h] = (torch.randint(0, 2, (V, h), generator=gen, device=DEVICE).float() * 2 - 1)
        k = max(1, int(round(SPARSE_F * (n - h))))
        for i in range(V):
            idx = torch.randperm(n - h, generator=gen, device=DEVICE)[:k]
            cb[i, h + idx] = 1.0
    cb = cb / (cb.norm(dim=1, keepdim=True) + 1e-8)
    return cb


def calibrated_nats(pred, cb, nxt):
    pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
    cos = pn @ cb.t()
    nb = pred.shape[0]
    best = float("inf")
    for temp in TEMP_GRID:
        z = cos / temp; z = z - z.max(dim=1, keepdim=True).values
        ez = torch.exp(z); prob = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = prob[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def train_variant(variant, n, cb, train_ids, val_ids, gen) -> float:
    """Train one variant; return calibrated val loss (nats)."""
    h = n // 2
    if variant in ("two_region",):
        W1 = torch.zeros(h, h, device=DEVICE); W2 = torch.zeros(n - h, n - h, device=DEVICE)
    elif variant == "bottleneck_adaptor":
        Wk = torch.zeros(K_CHANNELS, n, n, device=DEVICE)
        Router = torch.randn(n, K_CHANNELS, generator=gen, device=DEVICE) / math.sqrt(n)  # bottleneck proj
    else:
        W = torch.zeros(n, n, device=DEVICE)
    var_run = torch.ones(n, device=DEVICE)  # FEP running error variance

    def sample(ids):
        starts = torch.randint(0, ids.shape[0] - 1, (BATCH,), generator=gen, device=DEVICE)
        return cb[ids[starts]], cb[ids[starts + 1]]

    for step in range(N_STEPS):
        Ctx, Nxt = sample(train_ids)
        if variant == "hebbian_k1":
            W = W + LR * (Nxt.t() @ Ctx) / BATCH
        elif variant in ("cfrpe", "drosophila_sparse"):
            W = W + LR * ((Nxt - Ctx @ W.t()).t() @ Ctx) / BATCH
        elif variant == "stdp_asym":
            Heb = (Nxt.t() @ Ctx) / BATCH
            Asym = (Nxt.t() @ Ctx - Ctx.t() @ Nxt) / BATCH
            W = W + LR * (Heb + 0.5 * Asym)
        elif variant == "friston_fep":
            eps = Nxt - Ctx @ W.t()
            Pi = 1.0 / (var_run + 1e-3)
            W = W + LR * ((eps * Pi).t() @ Ctx) / BATCH
            var_run = 0.9 * var_run + 0.1 * (eps * eps).mean(dim=0)
        elif variant == "two_region":
            C1, C2 = Ctx[:, :h], Ctx[:, h:]; N1, N2 = Nxt[:, :h], Nxt[:, h:]
            W1 = W1 + LR * ((N1 - C1 @ W1.t()).t() @ C1) / BATCH
            W2 = W2 + LR * ((N2 - C2 @ W2.t()).t() @ C2) / BATCH
        elif variant == "bottleneck_adaptor":
            score = Ctx @ Router                       # (B,K) bottleneck router scores
            top1 = score.argmax(dim=1)                 # (B,) gated expert per item
            for k in range(K_CHANNELS):
                m = (top1 == k)
                if m.any():
                    Ck, Nk = Ctx[m], Nxt[m]
                    Wk[k] = Wk[k] + LR * ((Nk - Ck @ Wk[k].t()).t() @ Ck) / max(int(m.sum()), 1)

    # eval
    nb = min(2000, val_ids.shape[0] - 1)
    starts = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[val_ids[starts]]; nxt = val_ids[starts + 1]
    if variant == "two_region":
        c1, c2 = ctx[:, :h], ctx[:, h:]
        pred = torch.cat([c1 @ W1.t(), c2 @ W2.t()], dim=1)
    elif variant == "bottleneck_adaptor":
        score = ctx @ Router
        gate = torch.softmax(score, dim=1)             # (nb,K)
        pred = torch.zeros(nb, n, device=DEVICE)
        for k in range(K_CHANNELS):
            pred = pred + gate[:, k:k + 1] * (ctx @ Wk[k].t())
    else:
        pred = ctx @ W.t()
    return calibrated_nats(pred, cb, nxt)


def _selftest():
    g = np.random.default_rng(0)
    ids, ce = gen_zipf_bigram(64, 2000, g)
    assert ce < math.log(64), f"cond entropy {ce} not < log(V)"
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    cb = build_codebook(7, 128, "bipolar", gen)
    W = torch.zeros(128, 128, device=DEVICE); ctx, nxt = cb[0], cb[1]
    v = W @ ctx; eb = float((nxt - v).norm()); W = W + torch.outer(nxt - v, ctx); ea = float((nxt - W @ ctx).norm())
    assert ea < eb, "cf-RPE no shrink"
    Asym = torch.outer(nxt, ctx) - torch.outer(ctx, nxt)
    assert float((Asym + Asym.t()).abs().max()) < 1e-4, "STDP antisym part not antisymmetric"
    cbs = build_codebook(7, 128, "sparse", gen)
    assert int((cbs[0] != 0).sum()) == max(1, int(round(SPARSE_F * 128)))
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: cond_ent={ce:.3f}<logV cfrpe {eb:.3f}->{ea:.3f} stdp_antisym_ok sparse_support_ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    gen_np = np.random.default_rng(seed + 5000)
    t0 = time.time()
    ids, cond_ent = gen_zipf_bigram(VOCAB, CORPUS, gen_np)
    split = int(0.8 * len(ids))
    train_ids = torch.tensor(ids[:split], dtype=torch.long, device=DEVICE)
    val_ids = torch.tensor(ids[split:], dtype=torch.long, device=DEVICE)
    uniform_nats = math.log(VOCAB)
    print(f"  [seed={seed}] V={VOCAB} N={n_dim} uniform_nats={uniform_nats:.3f} cond_ent={cond_ent:.3f}", flush=True)
    coding = {"hebbian_k1": "bipolar", "cfrpe": "bipolar", "drosophila_sparse": "sparse",
              "stdp_asym": "bipolar", "friston_fep": "bipolar", "two_region": "split",
              "bottleneck_adaptor": "bipolar"}
    cells = {}
    for v in VARIANTS:
        cb = build_codebook(VOCAB, n_dim, coding[v], gen)
        nats = train_variant(v, n_dim, cb, train_ids, val_ids, gen)
        cells[v] = {"variant": v, "coding": coding[v], "val_nats": float(nats),
                    "gap_vs_uniform": float(uniform_nats - nats)}
        print(f"    [{v}] val_nats={nats:.4f} gap_vs_uniform={uniform_nats - nats:.4f}", flush=True)
        del cb; torch.cuda.empty_cache()
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "run_mode": RUN_MODE, "uniform_nats": float(uniform_nats),
            "cond_ent": float(cond_ent), "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    base = [r["cells"]["hebbian_k1"]["val_nats"] for r in results if "hebbian_k1" in r.get("cells", {})]
    base_mean = float(np.mean(base)) if base else float("inf")
    per_variant = {}
    for v in VARIANTS:
        if v == "hebbian_k1":
            continue
        gaps = []
        better = 0
        for r in results:
            if v in r.get("cells", {}) and "hebbian_k1" in r["cells"]:
                g = r["cells"]["hebbian_k1"]["val_nats"] - r["cells"][v]["val_nats"]
                gaps.append(g)
                if g > 0:
                    better += 1
        gm = float(np.mean(gaps)) if gaps else 0.0
        n = len(gaps)
        if gm > HP_GAP and better >= math.ceil(0.8 * n):
            band = "HP"
        elif gm >= MID_GAP:
            band = "MID"
        else:
            band = "HF"
        per_variant[v] = (band, gm, better, n)
    bands = [b for (b, _, _, _) in per_variant.values()]
    summary = (f"baseline_nats={base_mean:.3f} | " +
               " ".join(f"{v}:{per_variant[v][0]}(gap{per_variant[v][1]:+.3f},{per_variant[v][2]}/{per_variant[v][3]})"
                        for v in per_variant))
    if "HP" in bands:
        winners = [v for v in per_variant if per_variant[v][0] == "HP"]
        return ("HARD_PASS", f"HARD_PASS: variant(s) {winners} beat K=1 baseline by >{HP_GAP} nats. {summary}")
    if all(b == "HF" for b in bands):
        return ("HARD_FAIL", f"HARD_FAIL: ALL 6 variants <= baseline (refutes brain-drill predictions at bigram). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: some variants modestly help (0.1-0.3 nats), none HP. {summary}")


print(f"[config] anchor={ANCHOR_NAME} variants={VARIANTS} N={N_DIM} V={VOCAB} mode={RUN_MODE} seeds={SEEDS} "
      f"steps={N_STEPS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError(f"PROT-018: N_DIM={N_DIM} != _N_SUFFIX={_N_SUFFIX}")

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "V": VOCAB, "run_mode": RUN_MODE, "variants": VARIANTS, "n_steps": N_STEPS}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_DIM)
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
    "N": N_DIM, "V": VOCAB, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "n_steps": N_STEPS,
    "variants": VARIANTS, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "uniform_nats": r.get("uniform_nats"), "cond_ent": r.get("cond_ent"),
                  "cells": r.get("cells", {}), "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")}
                 for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
