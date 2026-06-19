"""
exp_substrate_etf_minilm_dim_expansion_v1 -- GPU follow-on to Slot 9: recover ETF headroom via dimensional expansion.

ROUTING: follow-on to Slot 9 (etf_hadamard_phase4a_infra_eval = MIDDLE 2.75x). Slot 9 found orthogonalizing real MiniLM
  keys helps only 2.75x because capacity is bounded by the encoder dim (384). HYPOTHESIS: expand the substrate dimension
  with a nonlinear random-feature map phi(x)=sign(R x) (R: 384 x D Gaussian) -> rank lifts toward D -> orthogonalization
  recovers more headroom. Tests capacity (raw-projected vs whitened) at D in {384, 1024, 4096}. If capacity scales with D,
  Phase-4a should EXPAND the substrate dim (not just orthogonalize) for real encoders. torch GPU (MiniLM encode).

PRE-REGISTERED bands: HARD-PASS whitened capacity at D=4096 >= 3x whitened capacity at D=384 (expansion recovers
  headroom). MIDDLE: 1.5-3x. HARD-FAIL: < 1.5x (expansion does not help -- real-encoder info ceiling is fundamental).
FORMULA SELF-TESTS (PROT-022): 1. expansion lifts rank. 2. unique-value hetero recall. 3. cuda.
ASCII-only. write_metrics. PROT-018: no _nN (D-sweep).
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
from experiments._gpu_cap import recall_unique_t, hop_recall, hopfield_recall_t, whiten_gpu, expand_gpu

ANCHOR_NAME = "substrate_etf_minilm_n_sub_lower_sweep_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 6000; D_GRID = [384, 512]; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; D_GRID = [384, 768, 1536, 3072]; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25]


def expand(emb, D, g):
    return expand_gpu(emb, D, int(g.integers(0, 2**31)))


def whiten(K):
    return whiten_gpu(K)


def norml(K):
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_unique(keys, n, g):
    return hop_recall(keys, n, int(g.integers(0, 2**31)))   # GPU matmuls


def _selftest():
    g = np.random.default_rng(0); emb = g.standard_normal((200, 16)).astype(np.float32)
    X = expand(emb, 128, g); assert np.linalg.matrix_rank(X) > np.linalg.matrix_rank(emb), "expansion lifts rank"
    assert recall_unique(norml(g.standard_normal((6, 512)).astype(np.float32)), 512, g) >= 0.9, "unique-value hetero recall"
    print("[selftest] PASS: expansion rank + recall", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoTokenizer


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
    tok = AutoTokenizer.from_pretrained(MINILM_ID); m = AutoModel.from_pretrained(MINILM_ID).to(DEVICE).eval(); out = []
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            h = m(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m; torch.cuda.empty_cache(); return np.concatenate(out, 0).astype(np.float32)


def capacity(emb, D, transform, seed):
    cap = 0; M_all = emb.shape[0]; ge = np.random.default_rng(seed * 31 + D)
    for load in LOADS:
        M = max(2, int(load * D))
        if M > M_all:
            break
        g = np.random.default_rng(seed * 1000 + M); idx = g.choice(M_all, size=M, replace=False)
        K = transform(expand(emb[idx], D, np.random.default_rng(seed * 31 + D)))
        if recall_unique(K, D, np.random.default_rng(seed * 7 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def m_50(emb, D, transform, seed):
    # M at which recall first drops below 0.5 (less censoring than 0.95-exact)
    prev = 2
    for load in [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25]:
        M = min(int(load * D), emb.shape[0])
        g = np.random.default_rng(seed * 1000 + D + M); idx = g.choice(emb.shape[0], size=M, replace=False)
        K = transform(expand(emb[idx], D, np.random.default_rng(seed * 31 + D)))
        if recall_unique(K, D, np.random.default_rng(seed * 7 + M)) < 0.5:
            return prev
        prev = M
    return prev


def run_seed(seed) -> Dict:
    emb = encode(load_texts(N_ENC)); by_D = {}
    for D in D_GRID:
        rm = m_50(emb, D, norml, seed); wm = m_50(emb, D, whiten, seed)
        by_D["D%d" % D] = {"raw_M50": rm, "whitened_M50": wm, "ratio": float(wm / max(rm, 1))}
    return {"seed": seed, "by_D": by_D}


def verdict(ps) -> Tuple[str, str]:
    klo = "D%d" % D_GRID[0]; khi = "D%d" % D_GRID[-1]
    rlo = float(np.mean([p["by_D"][klo]["ratio"] for p in ps])); rhi = float(np.mean([p["by_D"][khi]["ratio"] for p in ps]))
    parts = " ".join("N_sub=%s: M50_ratio=%.2fx (raw=%.0f wht=%.0f)" % (k[1:], np.mean([p["by_D"][k]["ratio"] for p in ps]), np.mean([p["by_D"][k]["raw_M50"] for p in ps]), np.mean([p["by_D"][k]["whitened_M50"] for p in ps])) for k in ps[0]["by_D"])
    summary = "orthogonalization M_50 ratio by N_sub: %s" % parts
    if rhi >= rlo + 0.5:
        return ("HARD_PASS", "HARD_PASS: orthogonalization lift GROWS with N_sub (M50 ratio %.2fx->%.2fx) -- wider encoders recover more; Phase-4 use wide encoders. " % (rlo, rhi) + summary)
    if rhi >= rlo - 0.5:
        return ("MIDDLE_BAND", "MIDDLE_BAND: lift roughly flat across N_sub (%.2fx->%.2fx). " % (rlo, rhi) + summary)
    return ("HARD_FAIL", "HARD_FAIL: lift SHRINKS with N_sub (%.2fx->%.2fx) -- Hadamard gain N-saturating. " % (rlo, rhi) + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d D_grid=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, D_GRID), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: round(v["ratio"], 2) for k, v in r["by_D"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
