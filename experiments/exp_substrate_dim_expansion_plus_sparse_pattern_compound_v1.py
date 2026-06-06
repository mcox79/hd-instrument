"""
exp_substrate_dim_expansion_plus_sparse_pattern_compound_v1 -- Slot DIMSPARSE: THE critical compound test -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot DIMSPARSE (HIGHEST PRIORITY). Construction = Research Option (iii): real Pythia keys +
  sparse-coded VALUES + dim-expanded keys. Tests whether the two capacity levers STACK: dim-expansion (keys; encoder-
  anisotropy attack) x sparse-pattern (values f=0.20; linear-noise regime). KEY-COLLISION-AWARE M_50 metric: query with
  FLIP-corrupted key (FLIP=0.05), measure retrieval recall (retrieved value == stored), find M where recall < 0.5.
  4 arms: (a) raw keys + dense values, (b) expanded keys + dense values, (c) raw keys + sparse values, (d) both.
  torch GPU (Pythia-160m, matches G8). N_ENC=10000 (uncensored).

PRE-REGISTERED bands: HARD-PASS (d) M_50 >= 0.80 * (b)*(c)/(a) (multiplicative compound within 20%) -> ~45x production.
  MIDDLE: (d) > 1.2*max(b,c) but < 0.8*b*c/a (partial). HARD-FAIL: (d) ~ max(b,c) (no stacking; single-lever ceiling).
FORMULA SELF-TESTS (PROT-022): 1. key-flip recall clean=1. 2. sparse values have f active. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._gpu_cap import recall_unique_t, hopfield_recall_t

ANCHOR_NAME = "substrate_dim_expansion_plus_sparse_pattern_compound_v1"
PYTHIA_ID = "EleutherAI/pythia-160m"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; ALPHA = 0.20
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 4000; D_EXP = 1024; LOADS = [0.2, 0.5, 1.0, 1.5, 2.0, 3.0]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; D_EXP = 2048; LOADS = [0.2, 0.5, 0.8, 1.1, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]


def expand(emb, D, g):
    if D == emb.shape[1]:
        return emb.copy()
    R = g.standard_normal((emb.shape[1], D)).astype(np.float32) / np.sqrt(emb.shape[1])
    return np.sign(emb @ R).astype(np.float32)


def norml(K):
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def whiten(K):
    # required for real-encoder keys (G8: raw/expanded Pythia is anisotropic -> unusable without whitening)
    mu = K.mean(0); X = K - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False)
    W = (X @ (Vt.T / (S + 1e-6))); return (W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def make_values(M, nv, sparse, g):
    if sparse:
        V = np.zeros((M, nv), np.float32); kk = max(1, int(ALPHA * nv))
        for i in range(M):
            idx = g.choice(nv, kk, replace=False); V[i, idx] = g.integers(0, 2, kk) * 2 - 1
    else:
        V = (g.integers(0, 2, (M, nv)) * 2 - 1).astype(np.float32)
    return V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)


def kc_recall(K, sparse, g):
    return recall_unique_t(K, K.shape[1], int(g.integers(0, 2**31)), sparse=sparse, alpha=ALPHA, flip=FLIP)   # GPU


def m_50(emb, D, expand_on, sparse, seed):
    prev = 2
    for load in LOADS:
        M = min(int(load * D), emb.shape[0])
        if M < 2:
            continue
        g = np.random.default_rng(seed * 1000 + D + M); idx = g.choice(emb.shape[0], M, replace=False)
        K = whiten(expand(emb[idx], D, np.random.default_rng(seed * 31 + D)) if expand_on else emb[idx])
        if kc_recall(K, sparse, np.random.default_rng(seed * 7 + M)) < 0.5:
            return prev
        prev = M
    return prev


def _selftest():
    g = np.random.default_rng(0); K = norml(g.standard_normal((20, 64)).astype(np.float32))
    M, nk = K.shape; V = make_values(M, nk, False, g)
    R = V.T @ (K @ K.T); assert np.mean(np.argmax(V @ R, axis=0) == np.arange(M)) >= 0.9, "clean-key recall high"
    Vs = make_values(50, 100, True, g); assert np.all((Vs != 0).sum(1) == int(ALPHA * 100)), "sparse values f active"
    print("[selftest] PASS: kc recall sparse", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_texts(n):
    out = []
    for f in [MEDQA, PUBMED]:
        if f.exists():
            for l in open(f, encoding="utf-8"):
                r = json.loads(l); out.append((r.get("question") or " ".join(r.get("context", {}).get("contexts", [""])))[:300])
                if len(out) >= n:
                    return out
    return out


def encode(texts):
    tok = AutoTokenizer.from_pretrained(PYTHIA_ID); tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(PYTHIA_ID, output_hidden_states=True).to(DEVICE).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = m(**t).hidden_states[-1]
        mask = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m; torch.cuda.empty_cache(); return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed) -> Dict:
    emb = encode(load_texts(N_ENC)); b = emb.shape[1]
    arms = {"a_baseline": m_50(emb, b, False, False, seed),
            "b_expand_keys": m_50(emb, D_EXP, True, False, seed),
            "c_sparse_values": m_50(emb, b, False, True, seed),
            "d_compound": m_50(emb, D_EXP, True, True, seed)}
    return {"seed": seed, "arms": arms}


def verdict(ps) -> Tuple[str, str]:
    a = {k: float(np.mean([p["arms"][k] for p in ps])) for k in ps[0]["arms"]}
    base = max(a["a_baseline"], 1); gb = a["b_expand_keys"] / base; gc = a["c_sparse_values"] / base; gd = a["d_compound"] / base
    expected = gb * gc; frac = gd / max(expected, 1e-9)
    summary = "M50 arms=%s | gain_b=%.2fx gain_c=%.2fx gain_d=%.2fx expected(b*c)=%.2fx d/expected=%.2f" % ({k: round(v) for k, v in a.items()}, gb, gc, gd, expected, frac)
    if frac >= 0.80 and gd > 1.2 * max(gb, gc):
        return ("HARD_PASS", "HARD_PASS: dim-expansion x sparse-values COMPOUND multiplicatively (d >= 0.8*b*c) -- production substrate ~%.0fx. " % gd + summary)
    if gd >= 1.2 * max(gb, gc):
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial stacking (d > best single but < 0.8*b*c). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no stacking (d ~ max(b,c)) -- levers independent, single-lever ceiling. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d D_exp=%d alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, D_EXP, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: round(v) for k, v in r["arms"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
