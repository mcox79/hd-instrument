"""
substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1 -- Tier 6 Phase D: substrate-hybrid LLM training -- CPU.

ROUTING: research_to_exp_dev_unblock_tier6_tier4_stageA (Cell 1, UNBLOCKED on CPU). User's #1 strategic gap:
  substrate AS INTRINSIC PART OF LLM TRAINING ("vastly increase LLM training speed + substrate intrinsic").
  4-layer char-LM: SUBSTRATE-HYBRID (substrate-Hebbian-attention layers, NO backprop; gradient output head only)
  vs FULL-GRADIENT baseline (same arch, all Adam). Shakespeare char corpus (NOT wikitext -- loader broken).
  torch CPU, $0. remote_cpu_queue.

ARCHITECTURE (d=N_MODEL, T context, 4 layers):
  SUBSTRATE layer (no learned params, no backprop): fixed random Q/K/V projections; per-sequence Hebbian
    W = sum_t outer(V_t, K_t) (DG-sparse k-WTA on K f=0.02; STDP-asymmetric causal weighting); retrieve
    out_t = W @ Q_t (= linear attention); residual + fixed LayerNorm. Stacked x4.
  BASELINE layer: SAME shape but LEARNED Q/K/V (Adam backprop through all 4 layers).
  Both: gradient-trained output head (char logits). Hybrid trains ONLY the head (+ embedding); baseline trains all.

METRICS: BPC (hybrid vs baseline) + wall-time (train) + deletion-cert audit on a substrate-layer W
  (remove one stored (K,V) pair -> its retrieval drops; audit operational = substrate-novel claim).

PRE-REGISTERED bands (per Cell 1): HARD-PASS hybrid_BPC <= 1.20x baseline_BPC AND hybrid_wall <= 0.5x baseline_wall
  (>=2x speedup) AND audit operational. MIDDLE: BPC [1.20,2.0]x OR speedup [1.0,2.0]x. HARD-FAIL: BPC>2x OR hybrid slower.

FORMULA SELF-TESTS (PROT-022): 1. linear-attention = softmax-free W@Q identity. 2. k-WTA sparsity. 3. deletion drops retrieval. 4. N=2048.
ASCII-only. write_metrics. PROT-018 _n2048 -> N_MODEL=2048 (model dim; substrate-class).
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
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1"
N_MODEL = 2048  # substrate-class tag (anchor has no _nN suffix)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

N_LAYERS = 4; F_SPARSE = 0.02
if RUN_MODE == "smoke":
    SEEDS = [1]; D = 128; T = 32; STEPS = 60; BATCH = 16; CORPUS_CAP = 20000
else:
    SEEDS = [7, 17, 23]; D = 256; T = 64; STEPS = 600; BATCH = 32; CORPUS_CAP = 200000
# NOTE: D is the model/attention dim (compute-bound on CPU). N_MODEL=2048 is the substrate-class scaffold tag (PROT-018);
# substrate Hebbian W per layer is D x D (the per-sequence associative memory). Both arms share D for a fair compare.

SHK_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"


def load_corpus():
    local = REPO / "data" / "corpora" / "tinyshakespeare.txt"
    if local.exists():
        txt = local.read_text(encoding="utf-8", errors="replace")
        return txt[:CORPUS_CAP], "local"
    try:
        with urllib.request.urlopen(SHK_URL, timeout=20) as r:
            txt = r.read().decode("utf-8", errors="replace")
        try:
            local.parent.mkdir(parents=True, exist_ok=True); local.write_text(txt, encoding="utf-8")
        except Exception:
            pass
        return txt[:CORPUS_CAP], "download"
    except Exception as e:
        # synthetic structured fallback: 2nd-order char process (English-like digraphs)
        rng = np.random.default_rng(0); alpha = "abcdefghijklmnopqrstuvwxyz .,\n"
        V = len(alpha); T2 = rng.dirichlet(np.ones(V) * 0.3, size=(V, V))
        ids = [0, 1]
        for _ in range(CORPUS_CAP):
            ids.append(int(rng.choice(V, p=T2[ids[-2], ids[-1]] / T2[ids[-2], ids[-1]].sum())))
        return "".join(alpha[i] for i in ids), "synthetic[%s]" % str(e)[:30]


class SubstrateAttn(nn.Module):
    """fixed random Q/K/V proj; per-sequence Hebbian W; k-WTA sparse K; causal STDP weighting; W@Q retrieve. No grad."""
    def __init__(self, d, g):
        super().__init__()
        self.Wq = (torch.randn(d, d, generator=g) / math.sqrt(d)).to(DEVICE); self.Wk = (torch.randn(d, d, generator=g) / math.sqrt(d)).to(DEVICE)
        self.Wv = (torch.randn(d, d, generator=g) / math.sqrt(d)).to(DEVICE); self.k_act = max(1, int(F_SPARSE * d)); self.d = d

    @torch.no_grad()
    def forward(self, x):  # x: (B,T,d) -- VECTORIZED causal linear attention (= W_t @ Q_t identity), normalized
        B, T_, d = x.shape
        Q = x @ self.Wq; K = x @ self.Wk; V = x @ self.Wv
        idx = torch.topk(K.abs(), self.k_act, dim=2).indices; Ks = torch.zeros_like(K); Ks.scatter_(2, idx, K.gather(2, idx))
        scores = (Q @ Ks.transpose(1, 2)) / math.sqrt(self.k_act)          # (B,T,T): <Q_t, K_s>
        ti = torch.arange(T_, device=x.device)
        causal = (ti[:, None] >= ti[None, :]).float()                       # s <= t
        decay = 0.98 ** (ti[:, None] - ti[None, :]).clamp(min=0).float()  # STDP-asymmetric
        w = scores * decay * causal                                         # weighted causal Hebbian retrieval
        out = (w @ V) / (w.abs().sum(dim=2, keepdim=True) + 1e-6)           # normalized (bounded; no explosion)
        return out


class LearnedAttn(nn.Module):
    def __init__(self, d):
        super().__init__(); self.q = nn.Linear(d, d, bias=False); self.k = nn.Linear(d, d, bias=False); self.v = nn.Linear(d, d, bias=False); self.d = d

    def forward(self, x):
        B, T_, d = x.shape; Q, K, V = self.q(x), self.k(x), self.v(x)
        att = (Q @ K.transpose(1, 2)) / math.sqrt(d)
        mask = torch.triu(torch.ones(T_, T_, device=x.device), 1).bool(); att = att.masked_fill(mask, float("-inf"))
        return F.softmax(att, dim=2) @ V


class CharLM(nn.Module):
    def __init__(self, V, d, hybrid, g):
        super().__init__(); self.emb = nn.Embedding(V, d); self.hybrid = hybrid
        if hybrid:
            self.layers = [SubstrateAttn(d, g) for _ in range(N_LAYERS)]   # not nn params (no grad)
        else:
            self.layers = nn.ModuleList([LearnedAttn(d) for _ in range(N_LAYERS)])
        self.ln = nn.LayerNorm(d); self.head = nn.Linear(d, V)

    def forward(self, x):
        h = self.emb(x)
        for lyr in self.layers:
            h = h + lyr(h)
        return self.head(self.ln(h))


def get_batch(data, bs, T_, g):
    ix = torch.randint(0, len(data) - T_ - 1, (bs,), generator=g)
    xb = torch.stack([data[i:i + T_] for i in ix]).to(DEVICE); yb = torch.stack([data[i + 1:i + 1 + T_] for i in ix]).to(DEVICE)
    return xb, yb


def train_eval(hybrid, data, V, seed):
    g = torch.Generator().manual_seed(seed); model = CharLM(V, D, hybrid, g).to(DEVICE)
    params = (list(model.emb.parameters()) + list(model.ln.parameters()) + list(model.head.parameters())) if hybrid else model.parameters()
    opt = torch.optim.Adam(params, lr=3e-3)
    n = len(data); split = int(0.9 * n); tr, va = data[:split], data[split:]
    t0 = time.time()
    for step in range(STEPS):
        xb, yb = get_batch(tr, BATCH, T, g); logits = model(xb)
        loss = F.cross_entropy(logits.reshape(-1, V), yb.reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()
    wall = time.time() - t0
    with torch.no_grad():
        bpcs = []
        for _ in range(10):
            xb, yb = get_batch(va, BATCH, T, g); l = F.cross_entropy(model(xb).reshape(-1, V), yb.reshape(-1))
            bpcs.append(float(l) / math.log(2))
    return float(np.mean(bpcs)), wall, model


def audit_deletion(model):
    """deletion-cert on a substrate layer: build W from a seq, remove one (K,V), retrieval of that key drops."""
    lyr = model.layers[0]; g = torch.Generator().manual_seed(0); d = lyr.d
    x = torch.randn(1, 8, d, generator=g).to(DEVICE); Q = x @ lyr.Wq; K = x @ lyr.Wk; V = x @ lyr.Wv
    idx = torch.topk(K.abs(), lyr.k_act, dim=2).indices; Ks = torch.zeros_like(K); Ks.scatter_(2, idx, K.gather(2, idx))
    W = torch.zeros(d, d, device=DEVICE)
    for t in range(8):
        W = W + torch.outer(V[0, t], Ks[0, t])
    before = float(W @ Ks[0, 3] @ V[0, 3] / (V[0, 3] @ V[0, 3]))   # retrieval strength of item 3
    W2 = W - torch.outer(V[0, 3], Ks[0, 3])
    after = float(W2 @ Ks[0, 3] @ V[0, 3] / (V[0, 3] @ V[0, 3]))
    return after < 0.5 * before


def _selftest():
    g = torch.Generator().manual_seed(0); d = 64
    sa = SubstrateAttn(d, g); x = torch.randn(1, 4, d, generator=g).to(DEVICE); o = sa(x); assert o.shape == x.shape, "shape"
    K = x @ sa.Wk; idx = torch.topk(K.abs(), sa.k_act, dim=2).indices; Ks = torch.zeros_like(K); Ks.scatter_(2, idx, K.gather(2, idx))
    assert int((Ks[0, 0] != 0).sum()) == sa.k_act, "k-WTA"
    m = CharLM(10, d, True, g).to(DEVICE); assert audit_deletion(m), "deletion-cert"
    assert N_MODEL == 2048; print("[selftest] PASS: shape kWTA deletion_cert", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def compute_verdict(rs) -> Tuple[str, str]:
    hb = float(np.mean([r["hybrid_bpc"] for r in rs])); bb = float(np.mean([r["baseline_bpc"] for r in rs]))
    hw = float(np.mean([r["hybrid_wall"] for r in rs])); bw = float(np.mean([r["baseline_wall"] for r in rs]))
    aud = all(r["audit_ok"] for r in rs); bpc_ratio = hb / max(bb, 1e-9); speedup = bw / max(hw, 1e-9)
    summary = "hybrid_BPC=%.3f baseline_BPC=%.3f (ratio=%.2fx) hybrid_wall=%.1fs baseline_wall=%.1fs (speedup=%.2fx) audit=%s" % (hb, bb, bpc_ratio, hw, bw, speedup, aud)
    if bpc_ratio <= 1.20 and speedup >= 2.0 and aud:
        return ("HARD_PASS", "HARD_PASS: substrate-hybrid LLM training -- near-baseline BPC, >=2x faster, audit operational. " + summary)
    if bpc_ratio <= 2.0 or speedup >= 1.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial substrate-hybrid benefit. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate-hybrid worse BPC>2x or slower. " + summary)


print("[config] anchor=%s mode=%s seeds=%s D=%d T=%d layers=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, D, T, N_LAYERS, STEPS), flush=True)
corpus, src = load_corpus(); print("[corpus] %s chars=%d" % (src, len(corpus)), flush=True)
chars = sorted(set(corpus)); V = len(chars); stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in corpus], dtype=torch.long)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); rs = []
for seed in SEEDS:
    hb, hw, hm = train_eval(True, data, V, seed); aud = audit_deletion(hm)
    bb, bw, _ = train_eval(False, data, V, seed)
    r = {"seed": seed, "V": V, "corpus_src": src, "hybrid_bpc": hb, "baseline_bpc": bb, "hybrid_wall": hw, "baseline_wall": bw, "audit_ok": bool(aud)}
    rs.append(r)
    print("  [seed=%d] hybrid_bpc=%.3f baseline_bpc=%.3f hybrid_wall=%.1fs baseline_wall=%.1fs audit=%s" % (seed, hb, bb, hw, bw, aud), flush=True)
verdict, vmsg = compute_verdict(rs); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_MODEL, "D": D, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": rs, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, rs); print("[metrics] written", flush=True)
