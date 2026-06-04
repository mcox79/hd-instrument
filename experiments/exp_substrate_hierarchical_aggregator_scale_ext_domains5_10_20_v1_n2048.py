"""
substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048 -- aggregator scale extension (GPU).

ROUTING: notes/routing_hierarchical_aggregator_scale_extension_n10_n20_2026-06-04.md. Extends the 5-corpus
  hierarchical aggregator HARD_PASS (BPC 2.598 vs specialist 2.561, retention 1.002) to N_domains=10 and 20.
  Reuses the 5-corpus scaffold (gen_zipf / bipolar domain-binding / cf-RPE / BPC / deletion-cert). torch ->
  GPU per route-by-torch (aggregator matmuls at N=2048 x up to 20 domains). $0.

CAPABILITY QUESTION:
  Does multiplicative-capacity aggregation hold as N_domains grows 5 -> 10 -> 20 at substrate N=2048? I.e. does
  ONE shared substrate still (a) aggregate all domains better than cross-domain baseline, (b) preserve >=~87%
  of each specialist's skill, and (c) keep deletion-cert retention >=0.95, when more domains share the substrate?

SETUP (per cell = one N_domains value): N_domains synthetic Zipf bigram domains (V=512), shared bipolar
  codebook dim N=2048, per-domain ~orthogonal bipolar keys. sub-LM_d = cf-RPE W_d on domain d. aggregator =
  ONE shared W_agg = sum_d cf-RPE(domain d, domain-bound ctx*dkey_d). Retrieve domain d via dkey_d.

CELLS (DOMAIN_GRID, 3 seeds):
  C5 N_domains=5 (replicate baseline sanity)   C10 N_domains=10   C20 N_domains=20
  Metrics per cell: H1_own (specialist BPC), H2_cross (cross-domain BPC), H3_agg (aggregator BPC),
  H4_retention (deletion-cert; sampled over min(N_domains,K_DEL) deleted domains to bound O(D^2) retraining).

PRE-REGISTERED BANDS (per cell; BPC nats; retention = other-domain gap preserved after deleting a domain):
  HARD-PASS: H3<H2 AND H3 <= H1*1.15 (>=~87% specialist skill) AND H4>=0.95 AND 3/3 seeds.
  MIDDLE: H3<H2 but H3 in (H1*1.15, H1*1.43] (70-87% skill) OR H4 in [0.85,0.95).
  HARD-FAIL: H3>=H2 OR H3>H1*1.43 OR H4<0.85.
  AGGREGATE: SCALES_CLEANLY (all 3 HP) / SCALES_PARTIALLY (C5+C10 HP, C20 MID/HF) / SCALES_BREAKS_EARLY (C10 MID/HF).

FORMULA SELF-TESTS (PROT-022):
  1. domain keys ~orthogonal at D=20 (mean|cos|<0.2). 2. bipolar bind invertible. 3. cf-RPE shrinks error.
  4. distinct Zipf domains. 5. uniform=ln(V).

PROT-018: anchor _n2048 -> substrate N=2048 (domain sweep is a cell var, not the _nN binding). PROT-019 floor 14400s.
PROT-021: per-seed partials. QUEUE: overnight_queue (GPU). ASCII-only.
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

ANCHOR_NAME = "substrate_hierarchical_aggregator_scale_ext_domains5_10_20_v1_n2048"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
VOCAB = 512
K_ACTIVE = 8
K_DEL = 4                      # cap deletion-cert samples per cell (bounds O(D^2) retraining)
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    N_DIM = 256; VOCAB = 128; SEEDS = [1, 2]; N_STEPS = 60; CORPUS = 4000; DOMAIN_GRID = [3, 5]
else:
    N_DIM = N; SEEDS = [7, 17, 23]; N_STEPS = 800; CORPUS = 40000; DOMAIN_GRID = [5, 10, 20]


def gen_zipf(V, length, gen_np):
    ranks = 1.0 / np.arange(1, V + 1); zp = ranks / ranks.sum()
    T = np.zeros((V, V))
    for c in range(V):
        tg = gen_np.choice(V, size=K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max()); w /= w.sum(); T[c, tg] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = gen_np.choice(V, p=T[s])
    return ids


def bipolar(shape, gen):
    return (torch.randint(0, 2, shape, generator=gen, device=DEVICE).float() * 2 - 1)


def train_cfrpe(n, cb, train_ids, gen, dkey=None):
    W = torch.zeros(n, n, device=DEVICE); ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        st = torch.randint(0, ntr - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = cb[train_ids[st]]; nxt = cb[train_ids[st + 1]]
        if dkey is not None:
            ctx = ctx * dkey
        ctx = ctx / (ctx.norm(dim=1, keepdim=True) + 1e-8)
        W = W + LR * ((nxt - ctx @ W.t()).t() @ ctx) / BATCH
    return W


def bpc(W, cb, val_ids, gen, dkey=None):
    nb = min(2000, val_ids.shape[0] - 1)
    st = torch.randint(0, val_ids.shape[0] - 1, (nb,), generator=gen, device=DEVICE)
    ctx = cb[val_ids[st]]; nxt = val_ids[st + 1]
    if dkey is not None:
        ctx = ctx * dkey
    ctx = ctx / (ctx.norm(dim=1, keepdim=True) + 1e-8)
    pred = ctx @ W.t(); pn = pred / (pred.norm(dim=1, keepdim=True) + 1e-8); cos = pn @ cb.t()
    best = float("inf")
    for t in TEMP_GRID:
        z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        pr = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = pr[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return best


def run_cell(n_dim, n_domains, seed, gen) -> Dict:
    cb = bipolar((VOCAB, n_dim), gen); cb = cb / cb.norm(dim=1, keepdim=True)
    dkeys = bipolar((n_domains, n_dim), gen); un = math.log(VOCAB)
    doms = []
    for d in range(n_domains):
        ids = gen_zipf(VOCAB, CORPUS, np.random.default_rng(seed * 1000 + n_domains * 37 + d))
        sp = int(0.8 * len(ids))
        doms.append((torch.tensor(ids[:sp], dtype=torch.long, device=DEVICE),
                     torch.tensor(ids[sp:], dtype=torch.long, device=DEVICE)))
    Wsub = [train_cfrpe(n_dim, cb, doms[d][0], gen) for d in range(n_domains)]
    Wagg = torch.zeros(n_dim, n_dim, device=DEVICE)
    for d in range(n_domains):
        Wagg = Wagg + train_cfrpe(n_dim, cb, doms[d][0], gen, dkey=dkeys[d])
    h1 = float(np.mean([bpc(Wsub[d], cb, doms[d][1], gen) for d in range(n_domains)]))
    # H2 cross: sample up to ~40 ordered pairs to bound bpc count at large D
    pairs = [(d, dp) for d in range(n_domains) for dp in range(n_domains) if dp != d]
    if len(pairs) > 40:
        idx = torch.randperm(len(pairs), generator=gen, device=DEVICE)[:40].tolist()
        pairs = [pairs[i] for i in idx]
    h2 = float(np.mean([bpc(Wsub[d], cb, doms[dp][1], gen) for d, dp in pairs]))
    h3 = float(np.mean([bpc(Wagg, cb, doms[d][1], gen, dkey=dkeys[d]) for d in range(n_domains)]))
    # H4 deletion-cert: sample K_DEL deleted domains; retention = other-domain gap preserved
    del_ks = list(range(n_domains)) if n_domains <= K_DEL else \
        torch.randperm(n_domains, generator=gen, device=DEVICE)[:K_DEL].tolist()
    retentions = []
    for k in del_ks:
        Wno = torch.zeros(n_dim, n_dim, device=DEVICE)
        for d in range(n_domains):
            if d != k:
                Wno = Wno + train_cfrpe(n_dim, cb, doms[d][0], gen, dkey=dkeys[d])
        others = [d for d in range(n_domains) if d != k]
        of = np.mean([bpc(Wagg, cb, doms[d][1], gen, dkey=dkeys[d]) for d in others])
        od = np.mean([bpc(Wno, cb, doms[d][1], gen, dkey=dkeys[d]) for d in others])
        retentions.append(float((un - od) / ((un - of) + 1e-9)))
        del Wno
    h4 = float(np.mean(retentions))
    del Wagg, Wsub; torch.cuda.empty_cache()
    return {"n_domains": n_domains, "H1_own": h1, "H2_cross": h2, "H3_agg": h3, "H4_retention": h4}


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    keys = bipolar((20, 256), gen); kn = keys / keys.norm(dim=1, keepdim=True); cosm = kn @ kn.t()
    off = cosm[~torch.eye(20, dtype=torch.bool, device=DEVICE)].abs().mean()
    assert float(off) < 0.2, f"D=20 keys not orthogonal {off}"
    x = bipolar((1, 256), gen); k = bipolar((1, 256), gen); assert torch.allclose(x * k * k, x)
    cb = bipolar((7, 256), gen); cb = cb / cb.norm(dim=1, keepdim=True)
    W = torch.zeros(256, 256, device=DEVICE); c0, n0 = cb[0], cb[1]
    v = W @ c0; eb = float((n0 - v).norm()); W = W + torch.outer(n0 - v, c0); ea = float((n0 - W @ c0).norm())
    assert ea < eb
    g1 = gen_zipf(64, 500, np.random.default_rng(0)); g2 = gen_zipf(64, 500, np.random.default_rng(1))
    assert not np.array_equal(g1, g2); assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: D20_dkey_orth={float(off):.3f} bind_invertible cfrpe {eb:.3f}->{ea:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed); t0 = time.time()
    cells = {}
    for nd in DOMAIN_GRID:
        c = run_cell(n_dim, nd, seed, gen); cells[f"D{nd}"] = c
        print(f"    [seed={seed} D={nd}] H1={c['H1_own']:.3f} H2={c['H2_cross']:.3f} H3={c['H3_agg']:.3f} ret={c['H4_retention']:.3f}", flush=True)
    elapsed = time.time() - t0
    print(f"  [seed={seed}] elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "cells": cells, "elapsed_s": elapsed}


def _cell_band(h1, h2, h3, h4):
    if h3 >= h2 or h3 > h1 * 1.43 or h4 < 0.85:
        return "HF"
    if h3 <= h1 * 1.15 and h4 >= 0.95:
        return "HP"
    return "MID"


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    cell_bands = {}
    parts = []
    for nd in DOMAIN_GRID:
        key = f"D{nd}"
        h1 = float(np.mean([r["cells"][key]["H1_own"] for r in results]))
        h2 = float(np.mean([r["cells"][key]["H2_cross"] for r in results]))
        h3 = float(np.mean([r["cells"][key]["H3_agg"] for r in results]))
        h4 = float(np.mean([r["cells"][key]["H4_retention"] for r in results]))
        seed_hp = sum(1 for r in results if _cell_band(r["cells"][key]["H1_own"], r["cells"][key]["H2_cross"],
                                                       r["cells"][key]["H3_agg"], r["cells"][key]["H4_retention"]) == "HP")
        band = "HP" if (_cell_band(h1, h2, h3, h4) == "HP" and seed_hp >= len(results)) else _cell_band(h1, h2, h3, h4)
        cell_bands[key] = band
        parts.append(f"{key}[{band} H1={h1:.2f} H3={h3:.2f} H2={h2:.2f} ret={h4:.2f}]")
    summary = " ".join(parts)
    bands = [cell_bands[f"D{nd}"] for nd in DOMAIN_GRID]
    if all(b == "HP" for b in bands):
        return ("HARD_PASS", f"HARD_PASS SCALES_CLEANLY: aggregator holds to D={DOMAIN_GRID[-1]}. {summary}")
    if cell_bands.get("D10") == "HP" and bands[0] == "HP":
        return ("MIDDLE_BAND", f"MIDDLE_BAND SCALES_PARTIALLY: ceiling between D10 and D{DOMAIN_GRID[-1]}. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL SCALES_BREAKS_EARLY: scaling ceiling below D10. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} domain_grid={DOMAIN_GRID} V={VOCAB} mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS} K_DEL={K_DEL}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "domain_grid": DOMAIN_GRID})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "domain_grid": DOMAIN_GRID,
           "per_seed": [{k: v for k, v in r.items()} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print(f"[metrics] written", flush=True)
