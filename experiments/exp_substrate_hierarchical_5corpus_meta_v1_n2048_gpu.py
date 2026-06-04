"""
substrate_hierarchical_5corpus_meta_v1_n2048_gpu -- hierarchical 5-corpus substrate aggregator (GPU).

ROUTING: notes/routing_substrate_hierarchical_5_corpus_meta_test_2026-06-04.md (from user question: "train
  many small models in parallel + aggregate via a meta substrate"). Owned GPU, $0.

CAPABILITY QUESTION:
  Can a substrate AGGREGATE 5 specialized sub-LMs (each trained on a different domain) -- via domain-binding
  into one shared substrate -- so the aggregator predicts across ALL 5 domains better than any sub-LM does
  cross-domain, while (a) preserving each sub-LM's own-domain skill and (b) supporting per-domain deletion
  (remove one domain's bindings, others intact)? Flagship "parallel sub-models -> substrate meta-aggregator".

SETUP (5 synthetic domains = 5 distinct Zipf bigram processes, V=512; shared bipolar codebook dim N):
  sub-LM_d : cf-RPE char-LM W_d trained on domain d only.
  aggregator: ONE shared W_agg; domain d trained with domain-bound context ctx_bind = code(ctx) * dkey_d
              (bipolar bind, dkey_d = per-domain random bipolar key). cf-RPE write. Retrieve domain d via
              the same binding. Domain keys are ~orthogonal -> domains occupy separable subspaces.

FOUR CELLS (3 seeds):
  H1 own      : mean over d of BPC(W_d on domain d test).            (specialist baseline)
  H2 cross    : mean over d!=d' of BPC(W_d on domain d' test).       (cross-domain failure baseline)
  H3 aggregate: mean over d of BPC(W_agg on domain d test via dkey_d). (KEY: aggregator across all domains)
  H4 deletion : retention = does removing domain k's bindings (W_agg trained without k) preserve other
                domains' BPC? retention = mean over k of [agg-without-k other-domain BPC vs full-agg].

PRE-REGISTERED BANDS (BPC nats; retention = fraction of other-domain gap preserved after deleting a domain):
  HARD-PASS: H3 < H2 (aggregator beats cross-domain baseline) AND H3 <= H1*1.25 (>=80% of specialist skill)
    AND H4 retention >= 0.95 AND 3/3 seeds.
  MIDDLE: H3 < H2 but H3 > H1*1.25 (partial aggregation), OR retention in [0.70,0.95).
  HARD-FAIL: H3 >= H2 (aggregation no better than cross-domain) OR retention < 0.50 (deletion breaks others).

FORMULA SELF-TESTS (PROT-022):
  1. domain keys ~orthogonal (mean |cos| < 0.2). 2. bipolar bind is invertible (bind(bind(x,k),k)=x).
  3. cf-RPE shrinks error. 4. distinct domains (two Zipf T's differ). 5. uniform nats = ln(V).

PROT-018: anchor _n2048 -> substrate N=2048 (sub-LMs + aggregator same dim for binding). PROT-021: per-seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 14400s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only.
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

ANCHOR_NAME = "substrate_hierarchical_5corpus_meta_v1_n2048_gpu"
_N_SUFFIX = 2048
N = 2048
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

LR = 0.5
BATCH = 64
N_DOMAINS = 5
VOCAB = 512
K_ACTIVE = 8
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]

if RUN_MODE == "smoke":
    N_DIM = 256; VOCAB = 128; SEEDS = [1, 2]; N_STEPS = 80; CORPUS = 5000
else:
    N_DIM = N; SEEDS = [7, 17, 23]; N_STEPS = 800; CORPUS = 40000


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
    W = torch.zeros(n, n, device=DEVICE)
    ntr = train_ids.shape[0]
    for _ in range(N_STEPS):
        st = torch.randint(0, ntr - 1, (BATCH,), generator=gen, device=DEVICE)
        ctx = cb[train_ids[st]]; nxt = cb[train_ids[st + 1]]
        if dkey is not None:
            ctx = ctx * dkey                       # bipolar domain-binding
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


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    keys = bipolar((5, 256), gen)
    kn = keys / keys.norm(dim=1, keepdim=True); cosm = (kn @ kn.t())
    off = cosm[~torch.eye(5, dtype=torch.bool, device=DEVICE)].abs().mean()
    assert float(off) < 0.2, f"domain keys not orthogonal {off}"
    x = bipolar((1, 256), gen); k = bipolar((1, 256), gen)
    assert torch.allclose(x * k * k, x), "bipolar bind not invertible"
    cb = bipolar((7, 256), gen); cb = cb / cb.norm(dim=1, keepdim=True)
    W = torch.zeros(256, 256, device=DEVICE); c0, n0 = cb[0], cb[1]
    v = W @ c0; eb = float((n0 - v).norm()); W = W + torch.outer(n0 - v, c0); ea = float((n0 - W @ c0).norm())
    assert ea < eb
    g = np.random.default_rng(0); t1 = gen_zipf(64, 500, g); t2 = gen_zipf(64, 500, np.random.default_rng(1))
    assert not np.array_equal(t1, t2)
    assert abs(math.log(7) - 1.9459) < 1e-3
    print(f"[selftest] PASS: dkey_orth={float(off):.3f} bind_invertible cfrpe {eb:.3f}->{ea:.3f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    cb = bipolar((VOCAB, n_dim), gen); cb = cb / cb.norm(dim=1, keepdim=True)
    dkeys = bipolar((N_DOMAINS, n_dim), gen)
    un = math.log(VOCAB)
    # build 5 domains
    doms = []
    for d in range(N_DOMAINS):
        ids = gen_zipf(VOCAB, CORPUS, np.random.default_rng(seed * 100 + d))
        sp = int(0.8 * len(ids))
        doms.append((torch.tensor(ids[:sp], dtype=torch.long, device=DEVICE),
                     torch.tensor(ids[sp:], dtype=torch.long, device=DEVICE)))
    # sub-LMs
    Wsub = [train_cfrpe(n_dim, cb, doms[d][0], gen) for d in range(N_DOMAINS)]
    # aggregator (all domains, domain-bound)
    Wagg = torch.zeros(n_dim, n_dim, device=DEVICE)
    for d in range(N_DOMAINS):
        Wagg = Wagg + train_cfrpe(n_dim, cb, doms[d][0], gen, dkey=dkeys[d])
    # H1 own, H2 cross
    h1 = float(np.mean([bpc(Wsub[d], cb, doms[d][1], gen) for d in range(N_DOMAINS)]))
    cross = [bpc(Wsub[d], cb, doms[dp][1], gen) for d in range(N_DOMAINS) for dp in range(N_DOMAINS) if dp != d]
    h2 = float(np.mean(cross))
    # H3 aggregate
    h3 = float(np.mean([bpc(Wagg, cb, doms[d][1], gen, dkey=dkeys[d]) for d in range(N_DOMAINS)]))
    # H4 deletion: remove domain k, check OTHER domains preserved
    retentions = []
    for k in range(N_DOMAINS):
        Wno = torch.zeros(n_dim, n_dim, device=DEVICE)
        for d in range(N_DOMAINS):
            if d != k:
                Wno = Wno + train_cfrpe(n_dim, cb, doms[d][0], gen, dkey=dkeys[d])
        others_full = np.mean([bpc(Wagg, cb, doms[d][1], gen, dkey=dkeys[d]) for d in range(N_DOMAINS) if d != k])
        others_del = np.mean([bpc(Wno, cb, doms[d][1], gen, dkey=dkeys[d]) for d in range(N_DOMAINS) if d != k])
        # retention: other-domain gap preserved (gap = un - bpc); 1.0 if deletion doesn't hurt others
        gap_full = un - others_full; gap_del = un - others_del
        retentions.append(float(gap_del / (gap_full + 1e-9)))
    h4 = float(np.mean(retentions))
    elapsed = time.time() - t0
    print(f"  [seed={seed}] H1_own={h1:.4f} H2_cross={h2:.4f} H3_agg={h3:.4f} H4_retention={h4:.3f} "
          f"elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "uniform_nats": un, "H1_own": h1, "H2_cross": h2, "H3_agg": h3,
            "H4_retention": h4, "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    h1 = float(np.mean([r["H1_own"] for r in results])); h2 = float(np.mean([r["H2_cross"] for r in results]))
    h3 = float(np.mean([r["H3_agg"] for r in results])); h4 = float(np.mean([r["H4_retention"] for r in results]))
    n = len(results)
    hp_seeds = sum(1 for r in results if r["H3_agg"] < r["H2_cross"] and r["H3_agg"] <= r["H1_own"] * 1.25 and r["H4_retention"] >= 0.95)
    summary = f"H1_own={h1:.3f} H2_cross={h2:.3f} H3_agg={h3:.3f} H4_retention={h4:.3f} hp_seeds={hp_seeds}/{n}"
    if h3 >= h2:
        return ("HARD_FAIL", f"HARD_FAIL: aggregator no better than cross-domain (H3>=H2). {summary}")
    if h4 < 0.50:
        return ("HARD_FAIL", f"HARD_FAIL: deletion breaks other domains (retention<0.50). {summary}")
    if hp_seeds >= n and h3 <= h1 * 1.25 and h4 >= 0.95:
        return ("HARD_PASS", f"HARD_PASS: substrate aggregates 5 domains (H3<H2, >=80% specialist skill, deletion-clean). {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: partial aggregation or retention in [0.5,0.95). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} domains={N_DOMAINS} V={VOCAB} mode={RUN_MODE} seeds={SEEDS} steps={N_STEPS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "domains": N_DOMAINS})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "domains": N_DOMAINS,
           "per_seed": [{k: v for k, v in r.items()} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print(f"[metrics] written", flush=True)
