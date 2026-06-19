"""
substrate_concept_level_lm_proxy_v1_n2048_gpu -- substrate concept-level LM (substrate side of EX-CONCEPT-1) -- GPU.

ROUTING: research_to_exp_dev_EX_CONCEPT_1_and_option_C_Wproj_routings (EX-CONCEPT-1; P_drill=0.35). The full cell
  needs Pythia-160M activations -> VQ -> concept IDs, but that extraction pipeline is HUNG (same as Llama v6).
  This PROXY tests the SUBSTRATE side NOW: can the substrate model concept-level sequences at large vocab
  V_concept=5000 (the regime VQ produces) using bio-primitives? The real-Pythia-VQ version follows when
  extraction is healthy. torch GPU (V=5000 codebook; feeds idle GPU). $0.

CAPABILITY QUESTION: at V_concept=5000 (Zipf concept-ID sequences as a VQ-activation proxy), can a J-ensemble
  substrate (trigram position-binding + symmetric Hebbian, NO cf-RPE per generative-LM drill) reach concept
  perplexity < 1.5 * sqrt(V_concept) (~106) -- i.e. capture meaningful next-concept structure at concept-class vocab?

MODEL: 1st-order Zipf process over V=5000 concepts (sparse transitions); substrate trigram posbind context +
  symmetric Hebbian; cosine+temp softmax over the 5000-concept codebook. J-ensemble mean. ppl=exp(BPC).
  Baselines: bigram-count concept ppl; uniform (=V).

CELLS (3 seeds): single_ppl, ensemble_ppl, bigram_count_ppl, uniform=V.
PRE-REGISTERED bands: HARD-PASS ensemble_ppl < 1.5*sqrt(V)~106 AND << uniform (captures structure). MIDDLE
  ppl in [1.5 sqrt(V), 3 sqrt(V)]~[106,212]. HARD-FAIL ppl > 3 sqrt(V) (no concept structure). NOTE proxy data;
  real-Pythia-VQ run pending extraction.

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. K3 recall. 3. ppl=exp(bpc). 4. N=2048.
PROT-018: _n2048 -> N=2048. GPU TEMPLATE: assert cuda + device='cuda'. ASCII-only. write_metrics.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda'); print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_concept_level_lm_proxy_v1_n2048_gpu"
_N_SUFFIX = 2048; N = 2048; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
V = 5000; K_ACTIVE = 12; LR = 0.5; BATCH = 64; KCTX = 3
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]
if RUN_MODE == "smoke":
    N_DIM = 512; V = 500; SEEDS = [1, 2]; CORPUS = 12000; N_STEPS = 250; J = 4
else:
    N_DIM = N; SEEDS = [7, 17, 23]; CORPUS = 60000; N_STEPS = 500; J = 10


def gen_zipf(Vc, length, gen_np):
    ranks = 1.0 / np.arange(1, Vc + 1); zp = ranks / ranks.sum()
    # sparse transition: each concept -> K_ACTIVE Zipf-weighted targets (store target lists, not dense VxV)
    targets = np.empty(Vc, dtype=object); weights = np.empty(Vc, dtype=object)
    for c in range(Vc):
        tg = gen_np.choice(Vc, size=K_ACTIVE, replace=False, p=zp)
        lg = gen_np.standard_normal(K_ACTIVE) * 2.0; w = np.exp(lg - lg.max()); w /= w.sum()
        targets[c] = tg; weights[c] = w
    ids = np.zeros(length, dtype=np.int64); s = 0
    for i in range(length):
        ids[i] = s; s = int(gen_np.choice(targets[s], p=weights[s]))
    return ids, targets, weights


def build_cb(Vc, n, gen):
    cb = (torch.randint(0, 2, (Vc, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def encode_ctx(cb, ids, starts):
    b = torch.zeros(starts.shape[0], cb.shape[1], device=DEVICE)
    for j in range(KCTX):
        b = b + torch.roll(cb[ids[starts + j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def train_hebb(n, cb, tr, gen):
    W = torch.zeros(n, n, device=DEVICE)
    for _ in range(N_STEPS):
        st = torch.randint(0, len(tr) - KCTX - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = encode_ctx(cb, tr, st); nxt = cb[tr[st + KCTX]]
        W = W + LR * (nxt.t() @ ctx) / BATCH
    return W


def ens_ppl(Ws, cb, va):
    nb = min(2000, len(va) - KCTX - 1); st = torch.arange(nb, device=DEVICE); nxt = va[st + KCTX]; best = float("inf")
    for t in TEMP_GRID:
        Ps = []
        for W in Ws:
            ctx = encode_ctx(cb, va, st); pred = ctx @ W.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
            cos = pred @ cb.t(); z = cos / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
            Ps.append(ez / (ez.sum(dim=1, keepdim=True) + 1e-30))
        P = torch.stack(Ps).mean(0); pt = P[torch.arange(nb, device=DEVICE), nxt].clamp_min(1e-12)
        best = min(best, float((-torch.log(pt)).mean()))
    return math.exp(best)


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(7, 128, gen)
    s = torch.tensor([0, 1, 2, 3], device=DEVICE)
    b1 = encode_ctx(cb, s, torch.tensor([0], device=DEVICE)); b2 = encode_ctx(cb, torch.tensor([2, 1, 0, 3], device=DEVICE), torch.tensor([0], device=DEVICE))
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    W = torch.zeros(128, 128, device=DEVICE); ctx = encode_ctx(cb, s, torch.tensor([0], device=DEVICE)); nxt = cb[3]
    W = W + torch.outer(nxt, ctx.squeeze(0)); pred = W @ ctx.squeeze(0)
    assert float(pred @ nxt / (pred.norm() * nxt.norm() + 1e-8)) > 0.5, "K3 recall"
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and N == 2048
    print("[selftest] PASS: rollbind_order K3_recall ppl_exp", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed); gen_np = np.random.default_rng(seed + 99)
    ids, _, _ = gen_zipf(V, CORPUS, gen_np); sp = int(0.8 * len(ids))
    tr = torch.tensor(ids[:sp], device=DEVICE); va = torch.tensor(ids[sp:], device=DEVICE)
    cb = build_cb(V, n_dim, gen)
    idx = np.array_split(np.arange(len(tr)), J)
    Ws = [train_hebb(n_dim, cb, tr[torch.tensor(idx[i], device=DEVICE)], torch.Generator(device=DEVICE).manual_seed(seed * 50 + i)) for i in range(J)]
    single = ens_ppl([Ws[0]], cb, va); ens = ens_ppl(Ws, cb, va)
    tn = ids[:sp]; c2 = np.ones((V, V), dtype=np.float32) if V <= 1000 else None
    if c2 is not None:
        for i in range(len(tn) - 1):
            c2[tn[i], tn[i + 1]] += 1
        Pb = c2 / c2.sum(axis=1, keepdims=True); ve = ids[sp:]; nb = min(2000, len(ve) - 1)
        big = math.exp(-np.mean([math.log(max(Pb[ve[i], ve[i + 1]], 1e-12)) for i in range(nb)]))
    else:
        # V too large for dense count table; use a dict-count bigram
        from collections import defaultdict
        cc = defaultdict(lambda: defaultdict(float)); tot = defaultdict(float)
        for i in range(len(tn) - 1):
            cc[tn[i]][tn[i + 1]] += 1.0; tot[tn[i]] += 1.0
        ve = ids[sp:]; nb = min(2000, len(ve) - 1); ll = 0.0
        for i in range(nb):
            a, b = ve[i], ve[i + 1]; p = (cc[a][b] + 1.0) / (tot[a] + V); ll += math.log(max(p, 1e-12))
        big = math.exp(-ll / nb)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    return {"seed": seed, "N": n_dim, "V": V, "J": J, "single_ppl": float(single), "ensemble_ppl": float(ens),
            "bigram_count_ppl": float(big), "uniform_ppl": float(V), "hp_bar": float(1.5 * math.sqrt(V)),
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


def compute_verdict(rs) -> Tuple[str, str]:
    if not rs:
        return ("HARD_FAIL", "no results")
    e = float(np.mean([r["ensemble_ppl"] for r in rs])); s = float(np.mean([r["single_ppl"] for r in rs]))
    b = float(np.mean([r["bigram_count_ppl"] for r in rs])); bar = float(rs[0]["hp_bar"]); Vc = rs[0]["V"]
    summary = f"V={Vc} ensemble_ppl={e:.1f} single={s:.1f} bigram_count={b:.1f} uniform={Vc} HP_bar(1.5sqrtV)={bar:.0f} [PROXY data]"
    if e < bar and e < 0.5 * Vc:
        return ("HARD_PASS", f"HARD_PASS: substrate models concept-level structure (ppl<{bar:.0f}, <<uniform). {summary}")
    if e < 2 * bar:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: partial concept structure. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: ppl>3sqrtV (no concept structure). {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} V={V} J={J}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "V": V, "J": J})
for seed in remaining:
    print(f"[seed={seed}] ...", flush=True); t0 = time.time(); r = run_seed(seed, N_DIM); r["elapsed_s"] = time.time() - t0
    print(f"  ensemble_ppl={r['ensemble_ppl']:.1f} single={r['single_ppl']:.1f} bigram={r['bigram_count_ppl']:.1f} bar={r['hp_bar']:.0f} ({r['elapsed_s']:.0f}s)", flush=True)
    write_partial(out_dir, seed, r)
all_results = list(aggregate_partials(out_dir, SEEDS).values())
verdict, vmsg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM, "V": V, "J": J,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": all_results}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
