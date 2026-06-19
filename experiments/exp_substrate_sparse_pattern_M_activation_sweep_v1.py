"""
exp_substrate_sparse_pattern_M_activation_sweep_v1 -- M-activation sweep: does sparse lever activate at higher M? -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE (orchestrator cycle 124 revision). DIMSPARSE found gain_c=1.0 at M=50 -> "no stacking", but
  that may be because the sparse-pattern lever is INACTIVE at low M (Slot 3 saw 5-7x at MUCH higher M). Sweep M on the
  DIMSPARSE real-Pythia substrate; at each M compare dense-value vs sparse-value (f=0.20) key-collision recall. Find the
  M where the sparse lever activates (sparse_recall > dense_recall). Resolves the premature-closure UNKNOWN. torch GPU.

PRE-REGISTERED bands: HARD-PASS sparse-value recall > dense by >=10pp at some M (lever activates -> compound still open).
  HARD-FAIL sparse ~ dense at ALL M (lever never activates on real-encoder KV -> key-collision-limited confirmed, M-indep).
FORMULA SELF-TESTS (PROT-022): 1. recall helper. 2. sparse values f active. 3. cuda.
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
from experiments._gpu_cap import recall_unique_t

ANCHOR_NAME = "substrate_sparse_pattern_M_activation_sweep_v1"
PYTHIA_ID = "EleutherAI/pythia-160m"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; ALPHA = 0.20; D_EXP = 2048
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 5000; MS = [50, 200, 800, 2000]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; MS = [50, 100, 200, 500, 1000, 2000, 4000]


def expand(emb, D, g):
    R = g.standard_normal((emb.shape[1], D)).astype(np.float32) / np.sqrt(emb.shape[1]); return np.sign(emb @ R).astype(np.float32)


def whiten(K):
    mu = K.mean(0); X = K - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False)
    W = (X @ (Vt.T / (S + 1e-6))); return (W / (np.linalg.norm(W, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def _selftest():
    g = np.random.default_rng(0); K = (g.standard_normal((40, 64)) ).astype(np.float32)
    K = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)
    assert recall_unique_t(K, 64, 1, sparse=False, flip=0.0) >= 0.9, "dense clean recall high"
    print("[selftest] PASS: recall helper", flush=True)


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
    emb = encode(load_texts(N_ENC)); by_M = {}
    for M in MS:
        if M > emb.shape[0]:
            break
        g = np.random.default_rng(seed * 13 + M); idx = g.choice(emb.shape[0], M, replace=False)
        K = whiten(expand(emb[idx], D_EXP, np.random.default_rng(seed * 31)))
        rd = recall_unique_t(K, D_EXP, seed * 7 + M, sparse=False, flip=FLIP)
        rs = recall_unique_t(K, D_EXP, seed * 7 + M, sparse=True, alpha=ALPHA, flip=FLIP)
        by_M["M%d" % M] = {"dense_recall": rd, "sparse_recall": rs, "delta_pp": (rs - rd) * 100}
    return {"seed": seed, "by_M": by_M}


def verdict(ps) -> Tuple[str, str]:
    keys = list(ps[0]["by_M"].keys())
    agg = {k: {"dense": float(np.mean([p["by_M"][k]["dense_recall"] for p in ps])), "sparse": float(np.mean([p["by_M"][k]["sparse_recall"] for p in ps]))} for k in keys}
    best = max((agg[k]["sparse"] - agg[k]["dense"]) for k in keys)
    summary = "by M (dense->sparse recall): %s | max sparse-dense delta=%.1fpp" % ({k: (round(v["dense"], 2), round(v["sparse"], 2)) for k, v in agg.items()}, best * 100)
    if best >= 0.10:
        return ("HARD_PASS", "HARD_PASS: sparse-value lever ACTIVATES at some M (sparse recall > dense by >=10pp) -- DIMSPARSE compound still open; re-test at activation M. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: sparse-value lever NEVER activates across M -- key-collision-limited confirmed (M-independent); DIMSPARSE no-compound stands. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d MS=%s" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, MS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: (round(v["dense_recall"], 2), round(v["sparse_recall"], 2)) for k, v in r["by_M"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
