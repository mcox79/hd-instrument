"""
exp_substrate_hadamard_plus_whitening_combined_v1 -- Slot G7: do whitening + dim-expansion STACK? -- GPU.

ROUTING: PRIORITY_QUEUE_LIVE Slot G7. Today found two real-encoder rescues: whitening (Slot 9, 2.75x) + dim-expansion
  (Slot 14, ~linear). This tests whether they STACK. 4 conditions on MiniLM keys: base_raw, whiten_only, expand_only,
  expand_plus_whiten. Capacity (unique-value hetero). HP: combined >= 1.3x the best single rescue. torch GPU (MiniLM).

PRE-REGISTERED bands: HARD-PASS combined/best_single >= 1.3x. MIDDLE: 1.05-1.3x. HARD-FAIL: < 1.05x (no stacking).
FORMULA SELF-TESTS (PROT-022): 1. expansion lifts rank. 2. unique-value recall. 3. cuda.
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
from experiments._gpu_cap import recall_unique_t, hop_recall, hopfield_recall_t, whiten_gpu, expand_gpu

ANCHOR_NAME = "substrate_hadamard_plus_whitening_combined_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 4000; D_EXP = 2048; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25]
else:
    SEEDS = [7, 17, 23]; N_ENC = 10000; D_EXP = 4096; LOADS = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.17, 0.2, 0.25]


def expand(emb, D, g):
    return expand_gpu(emb, D, int(g.integers(0, 2**31)))


def whiten(K):
    return whiten_gpu(K)


def norml(K):
    return (K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)).astype(np.float32)


def recall_unique(keys, n, g):
    return hop_recall(keys, n, int(g.integers(0, 2**31)))   # GPU matmuls


def _selftest():
    g = np.random.default_rng(0)
    assert np.linalg.matrix_rank(expand(g.standard_normal((200, 16)).astype(np.float32), 128, g)) > 16, "expansion lifts rank"
    assert recall_unique(norml(g.standard_normal((6, 512)).astype(np.float32)), 512, g) >= 0.9, "unique-value recall"
    print("[selftest] PASS: expand whiten recall", flush=True)


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


def capacity(K, n, seed):
    cap = 0
    for load in LOADS:
        M = min(int(load * n), K.shape[0])
        if M < 2:
            continue
        g = np.random.default_rng(seed * 1000 + M)
        if recall_unique(K[g.choice(K.shape[0], M, replace=False)], n, np.random.default_rng(seed * 7 + M)) >= 0.95:
            cap = M
        else:
            break
    return cap


def run_seed(seed) -> Dict:
    emb = encode(load_texts(N_ENC)); b = emb.shape[1]
    conds = {"base_raw": (norml(emb), b), "whiten_only": (whiten(emb), b),
             "expand_only": (norml(expand(emb, D_EXP, np.random.default_rng(seed * 31))), D_EXP),
             "expand_plus_whiten": (whiten(expand(emb, D_EXP, np.random.default_rng(seed * 31))), D_EXP)}
    return {"seed": seed, "caps": {k: capacity(K, n, seed) for k, (K, n) in conds.items()}}


def verdict(ps) -> Tuple[str, str]:
    agg = {k: float(np.mean([p["caps"][k] for p in ps])) for k in ps[0]["caps"]}
    combo = agg["expand_plus_whiten"]; best_single = max(agg["whiten_only"], agg["expand_only"]); gain = combo / max(best_single, 1)
    summary = "caps: %s | combined/best_single=%.2fx" % ({k: round(v) for k, v in agg.items()}, gain)
    if gain >= 1.3:
        return ("HARD_PASS", "HARD_PASS: whitening + dim-expansion STACK (combined >=1.3x best single) -- Phase-4 apply both. " + summary)
    if gain >= 1.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: combined modestly beats best single (1.05-1.3x). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: combining does not beat best single rescue (<1.05x). " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_enc=%d D_exp=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_ENC, D_EXP), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] %s" % (seed, {k: round(v) for k, v in r["caps"].items()}), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
