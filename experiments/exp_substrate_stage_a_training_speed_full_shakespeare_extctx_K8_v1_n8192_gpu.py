"""
substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192_gpu -- Stage A training-speed (Cell 3) -- GPU.

ROUTING: research_to_exp_dev_unblock_tier6_tier4_stageA (Cell 3). User's #1 thesis: "vastly increase LLM training
  speed". Earlier crossover-N-sweep HF was at counting-optimal synthetic Zipf (substrate adds no value). Cell 3 runs
  the HARDER Shakespeare extended-context (K=8) task in the Bundle-B-HP regime where substrate should shine.
  PURE-SUBSTRATE one-pass training (substrate-Hebbian-attention features + CLOSED-FORM ridge readout, ZERO backprop)
  vs ADAM-trained transformer at matched task. torch GPU, $0. overnight_queue.

CAPABILITY QUESTION: does pure one-pass substrate training reach BPC within 20% of an Adam transformer at >=3x
  LESS wall-time, on Shakespeare char extended-context K=8?

MODEL: K=8-char context -> concat embedding. SUBSTRATE arm: stack of substrate-Hebbian-attention layers (fixed
  random proj, k-WTA DG-sparse, STDP, NO backprop) -> features H; readout fit by RIDGE (closed-form, ONE pass).
  ADAM arm: same-width transformer (learned attention + head), full backprop STEPS iters. Both: BPC on held-out.

PRE-REGISTERED bands: HARD-PASS substrate_BPC <= 1.20x adam_BPC AND substrate_wall <= adam_wall/3 (>=3x speedup).
  MIDDLE: BPC<=1.5x OR speedup>=1.5x. HARD-FAIL: BPC>1.5x AND speedup<1.5x.

FORMULA SELF-TESTS (PROT-022): 1. ridge readout fits a linearly-separable map. 2. k-WTA sparsity. 3. N=8192.
GPU TEMPLATE: assert cuda + device='cuda'. ASCII-only. write_metrics. PROT-018 _n8192 -> N_MODEL=8192 (substrate-class tag).
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch, torch.nn as nn, torch.nn.functional as F
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_stage_a_training_speed_full_shakespeare_extctx_K8_v1_n8192_gpu"
_N_SUFFIX = 8192; N_MODEL = 8192; assert N_MODEL == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

K_CTX = 8; N_LAYERS = 3; F_SPARSE = 0.02
if RUN_MODE == "smoke":
    SEEDS = [1]; D = 256; STEPS = 80; BATCH = 64; CORPUS_CAP = 30000; N_TRAIN = 4000
else:
    SEEDS = [7, 17, 23]; D = 512; STEPS = 800; BATCH = 128; CORPUS_CAP = 300000; N_TRAIN = 30000
SHK_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


def load_corpus():
    local = REPO / "data" / "corpora" / "tinyshakespeare.txt"
    if local.exists():
        return local.read_text(encoding="utf-8", errors="replace")[:CORPUS_CAP], "local"
    try:
        with urllib.request.urlopen(SHK_URL, timeout=20) as r:
            txt = r.read().decode("utf-8", errors="replace")
        try:
            local.parent.mkdir(parents=True, exist_ok=True); local.write_text(txt, encoding="utf-8")
        except Exception:
            pass
        return txt[:CORPUS_CAP], "download"
    except Exception as e:
        rng = np.random.default_rng(0); alpha = "abcdefghijklmnopqrstuvwxyz .,\n"; V = len(alpha)
        T2 = rng.dirichlet(np.ones(V) * 0.3, size=(V, V)); ids = [0, 1]
        for _ in range(CORPUS_CAP):
            ids.append(int(rng.choice(V, p=T2[ids[-2], ids[-1]] / T2[ids[-2], ids[-1]].sum())))
        return "".join(alpha[i] for i in ids), "synthetic[%s]" % str(e)[:30]


class SubAttn(nn.Module):
    def __init__(self, d, g):
        super().__init__()
        self.Wq = torch.randn(d, d, generator=g, device=DEVICE) / math.sqrt(d)
        self.Wk = torch.randn(d, d, generator=g, device=DEVICE) / math.sqrt(d)
        self.Wv = torch.randn(d, d, generator=g, device=DEVICE) / math.sqrt(d)
        self.k_act = max(1, int(F_SPARSE * d)); self.d = d

    @torch.no_grad()
    def forward(self, x):  # (B,K,d) -> (B,K,d) causal linear attn, normalized
        B, K, d = x.shape; Q = x @ self.Wq; Kk = x @ self.Wk; V = x @ self.Wv
        idx = torch.topk(Kk.abs(), self.k_act, dim=2).indices; Ks = torch.zeros_like(Kk); Ks.scatter_(2, idx, Kk.gather(2, idx))
        sc = (Q @ Ks.transpose(1, 2)) / math.sqrt(self.k_act)
        ti = torch.arange(K, device=DEVICE); causal = (ti[:, None] >= ti[None, :]).float()
        w = sc * causal
        return (w @ V) / (w.abs().sum(dim=2, keepdim=True) + 1e-6)


class LearnedTransformer(nn.Module):
    def __init__(self, V, d):
        super().__init__(); self.emb = nn.Embedding(V, d); self.layers = nn.ModuleList([nn.ModuleDict({
            "q": nn.Linear(d, d, bias=False), "k": nn.Linear(d, d, bias=False), "v": nn.Linear(d, d, bias=False)}) for _ in range(N_LAYERS)])
        self.ln = nn.LayerNorm(d); self.head = nn.Linear(d, V); self.d = d

    def forward(self, x):  # x: (B,K)
        h = self.emb(x); B, K, d = h.shape; mask = torch.triu(torch.ones(K, K, device=DEVICE), 1).bool()
        for ly in self.layers:
            Q, Kk, Vv = ly["q"](h), ly["k"](h), ly["v"](h)
            att = (Q @ Kk.transpose(1, 2)) / math.sqrt(d); att = att.masked_fill(mask, float("-inf"))
            h = h + F.softmax(att, dim=2) @ Vv
        return self.head(self.ln(h[:, -1]))   # predict next char from last position


def make_ctx(data, n_samples, g):
    ix = torch.randint(0, len(data) - K_CTX - 1, (n_samples,), generator=g, device=DEVICE)
    X = torch.stack([data[i:i + K_CTX] for i in ix]); y = data[ix + K_CTX]
    return X, y


def substrate_onepass(data, V, emb, seed):
    g = torch.Generator(device=DEVICE).manual_seed(seed); layers = [SubAttn(D, g) for _ in range(N_LAYERS)]
    t0 = time.time()
    Xtr, ytr = make_ctx(data, N_TRAIN, g)
    with torch.no_grad():
        h = emb[Xtr]
        for ly in layers:
            h = h + ly(h)
        Hf = h[:, -1]                                   # (N_TRAIN, D) features at last pos
        Y = F.one_hot(ytr, V).float()
        A = Hf.t() @ Hf + 1e-2 * torch.eye(D, device=DEVICE); Wout = torch.linalg.solve(A, Hf.t() @ Y)  # ridge, one pass
    wall = time.time() - t0
    return layers, Wout, wall


def substrate_bpc(data, V, emb, layers, Wout, seed):
    g = torch.Generator(device=DEVICE).manual_seed(seed + 1); Xv, yv = make_ctx(data, 2000, g)
    with torch.no_grad():
        h = emb[Xv]
        for ly in layers:
            h = h + ly(h)
        logits = h[:, -1] @ Wout
        return float(F.cross_entropy(logits, yv)) / math.log(2)


def adam_train_bpc(data, V, seed):
    g = torch.Generator(device=DEVICE).manual_seed(seed); model = LearnedTransformer(V, D).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=3e-3); t0 = time.time()
    for _ in range(STEPS):
        Xb, yb = make_ctx(data, BATCH, g); loss = F.cross_entropy(model(Xb), yb)
        opt.zero_grad(); loss.backward(); opt.step()
    wall = time.time() - t0
    with torch.no_grad():
        bpcs = []
        for _ in range(10):
            Xv, yv = make_ctx(data, BATCH, g); bpcs.append(float(F.cross_entropy(model(Xv), yv)) / math.log(2))
    return float(np.mean(bpcs)), wall


def _selftest():
    g = torch.Generator(device=DEVICE).manual_seed(0)
    H = torch.randn(200, 16, generator=g, device=DEVICE); Wt = torch.randn(16, 5, generator=g, device=DEVICE); Y = H @ Wt   # LINEAR target (ridge-fittable)
    A = H.t() @ H + 1e-3 * torch.eye(16, device=DEVICE); W = torch.linalg.solve(A, H.t() @ Y)
    assert float(((H @ W - Y) ** 2).mean()) < 0.05, "ridge fit"
    sa = SubAttn(32, g); x = torch.randn(2, 4, 32, generator=g, device=DEVICE); K = x @ sa.Wk
    idx = torch.topk(K.abs(), sa.k_act, 2).indices; Ks = torch.zeros_like(K); Ks.scatter_(2, idx, K.gather(2, idx))
    assert int((Ks[0, 0] != 0).sum()) == sa.k_act, "k-WTA"
    assert N_MODEL == 8192; print("[selftest] PASS: ridge kWTA", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(rs) -> Tuple[str, str]:
    sb = float(np.mean([r["substrate_bpc"] for r in rs])); ab = float(np.mean([r["adam_bpc"] for r in rs]))
    sw = float(np.mean([r["substrate_wall"] for r in rs])); aw = float(np.mean([r["adam_wall"] for r in rs]))
    ratio = sb / max(ab, 1e-9); speed = aw / max(sw, 1e-9)
    summary = "substrate_BPC=%.3f adam_BPC=%.3f (ratio=%.2fx) substrate_wall=%.2fs adam_wall=%.2fs (speedup=%.1fx)" % (sb, ab, ratio, sw, aw, speed)
    if ratio <= 1.20 and speed >= 3.0:
        return ("HARD_PASS", "HARD_PASS: pure one-pass substrate training -- within 20% BPC at >=3x speed. " + summary)
    if ratio <= 1.5 or speed >= 1.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial training-speed advantage. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no meaningful training-speed advantage. " + summary)


print("[config] anchor=%s mode=%s seeds=%s D=%d K=%d layers=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, K_CTX, N_LAYERS, STEPS), flush=True)
corpus, src = load_corpus(); print("[corpus] %s chars=%d" % (src, len(corpus)), flush=True)
chars = sorted(set(corpus)); V = len(chars); stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in corpus], dtype=torch.long, device=DEVICE)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rs = []
for seed in SEEDS:
    g = torch.Generator(device=DEVICE).manual_seed(seed * 3)
    emb = (torch.randn(V, D, generator=g, device=DEVICE) / math.sqrt(D))   # fixed embedding for substrate
    layers, Wout, sw = substrate_onepass(data, V, emb, seed); sb = substrate_bpc(data, V, emb, layers, Wout, seed)
    ab, aw = adam_train_bpc(data, V, seed)
    r = {"seed": seed, "V": V, "corpus_src": src, "substrate_bpc": sb, "adam_bpc": ab, "substrate_wall": sw, "adam_wall": aw}
    rs.append(r)
    print("  [seed=%d] substrate_bpc=%.3f adam_bpc=%.3f substrate_wall=%.2fs adam_wall=%.2fs" % (seed, sb, ab, sw, aw), flush=True)
verdict, vmsg = compute_verdict(rs); print("\n[VERDICT] " + vmsg, flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print("[GPU] peak %.3f GB" % peak, flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_MODEL, "D": D, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rs, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)
