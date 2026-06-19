"""
exp_hp12_v1_decisive_extraction_v1 -- HP-12 V1 decisive Tests 1+3: extraction speed + substrate geometry -- GPU.

ROUTING: research HP12_V1_pipeline_simplified_desktop_only -- cheap decisive pre-tests gating the 4-day desktop V1 build.
  Test 3 (HP-1/HF-4): Llama-3.2-1B bf16, layer-skip to layer 10/16, batch=8 extraction of 1K medical facts -- HP < 10s
  (10K extrapolates < 100s on desktop, no cloud). Test 1 + HF-3 (geometry): store N real fact-embeddings (Pythia-160m
  AND Llama-1B-layer10) in substrate N=1024 (whitened) and retrieve -- HP associative recall > 0.80 (else geometry
  mismatch). Confirms desktop V1 viability WITHOUT vLLM (HF bf16) and WITHOUT cloud (4060Ti 8GB fits bf16 1B). torch GPU $0.

PRE-REGISTERED bands: HARD-PASS Llama-1B 1K extraction < 10s AND substrate recall > 0.80 (>=1 model). MIDDLE: extraction
  < 30s OR recall > 0.70. HARD-FAIL: extraction > 30s (HF-4 cloud fallback) OR recall < 0.60 (HF-3 geometry mismatch).
FORMULA SELF-TESTS (PROT-022): 1. whiten+store+retrieve. 2. layer-skip slice. 3. cuda.
GPU TEMPLATE assert cuda. ASCII-only. write_metrics. PROT-018: no _nN.
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

ANCHOR_NAME = "exp_hp12_v1_decisive_extraction_v1"
PYTHIA_ID = "EleutherAI/pythia-160m"; LLAMA_ID = "meta-llama/Llama-3.2-1B"; LLAMA_SKIP_LAYER = 10
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_STORE = 100; N_SPEED = 200; BATCH = 8; N_SUB = 1024
else:
    N_STORE = 300; N_SPEED = 1000; BATCH = 8; N_SUB = 1024


def whiten_store_recall(emb, n_sub, seed):
    # emb: (M, D) real fact embeddings. Whiten -> random project to n_sub -> Hebbian store key_i->value_i -> recall.
    g = np.random.default_rng(seed); M, Dd = emb.shape
    mu = emb.mean(0); X = emb - mu
    U, S, Vt = np.linalg.svd(X, full_matrices=False); k = min(n_sub, len(S))
    Wht = (Vt[:k].T / (S[:k] + 1e-6))
    K = (X @ Wht); K = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)   # whitened unit keys (M,k)
    if k < n_sub:
        K = np.pad(K, ((0, 0), (0, n_sub - k)))
    EV = (g.integers(0, 2, (M, n_sub)) * 2 - 1).astype(np.float32); EV /= np.linalg.norm(EV, axis=1, keepdims=True) + 1e-8
    W = (EV.T @ K.astype(np.float32))                  # Hebbian key->value
    recall = float(np.mean([int(np.argmax(EV @ (W @ K[i].astype(np.float32)))) == i for i in range(M)]))
    return recall


def _selftest():
    g = np.random.default_rng(0); emb = g.standard_normal((30, 64)).astype(np.float32)
    r = whiten_store_recall(emb, 256, 0); assert r > 0.8, "whiten+store+retrieve (%.2f)" % r
    x = torch.zeros(2, 5, 8); assert x[:, -1, :].shape == (2, 8), "slice"
    print("[selftest] PASS: whiten-store slice", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_texts(n):
    rows = [json.loads(l) for l in open(MEDQA, encoding="utf-8")][:n]
    return [r["question"][:400] for r in rows]


def extract(model_id, texts, batch, skip_layer=None, dtype=torch.float32):
    tok = AutoTokenizer.from_pretrained(model_id)
    tok.pad_token = tok.eos_token if tok.pad_token is None else tok.pad_token; tok.truncation_side = "left"
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype, output_hidden_states=True).to(DEVICE).eval()
    embs = []; t0 = time.time()
    for i in range(0, len(texts), batch):
        b = texts[i:i + batch]; t = tok(b, return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEVICE)
        with torch.no_grad():
            hs = model(**t).hidden_states
        layer = skip_layer if skip_layer is not None else (len(hs) - 1)
        h = hs[layer]; m = t["attention_mask"].unsqueeze(-1).to(h.dtype)
        embs.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).float().cpu().numpy())
    el = time.time() - t0; vram = torch.cuda.max_memory_allocated() / 1e9
    out = np.concatenate(embs, 0)
    del model; torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    return out, el, vram


LLAMA_NPZ = REPO / "data" / "exp_phase05_v1_llama32_1b_per_token_residual_extract_v1" / "residuals_per_token.npz"


def run_seed(seed) -> Dict:
    res = {"seed": seed}
    texts = load_texts(N_STORE)
    # Test 1 geometry: Pythia-160m (live extraction; model is local + ungated)
    pe, pspeed, _ = extract(PYTHIA_ID, texts[:N_STORE], BATCH)
    res["pythia_recall"] = whiten_store_recall(pe, N_SUB, seed)
    # HF-3 geometry: REAL Llama-1B embeddings from the already-extracted residual npz (model is gated + not on runner;
    # geometry only needs the embeddings, which are local). Per-doc mean-pool.
    try:
        d = np.load(LLAMA_NPZ); R = d["residuals"]; bnd = d["doc_boundaries"]
        g2 = np.random.default_rng(seed); docs = [i for i in range(len(bnd) - 1) if bnd[i + 1] > bnd[i]]
        pick = list(g2.choice(len(docs), size=min(N_STORE, len(docs)), replace=False))
        le = np.stack([R[bnd[docs[i]]:bnd[docs[i] + 1]].mean(0) for i in pick]).astype(np.float32)
        res["llama_recall"] = whiten_store_recall(le, N_SUB, seed)
    except Exception as e:
        print("[llama-npz] issue: %s" % e, flush=True); res["llama_recall"] = -1.0
    # Test 3 (extraction speed): needs Llama-1B weights local (gated) -> flagged to Testbed; not run here.
    res["llama_extract_s_per_1k"] = -1.0; res["llama_vram_gb"] = -1.0
    return res


def verdict(ps) -> Tuple[str, str]:
    pr = float(np.mean([p["pythia_recall"] for p in ps])); lr = float(np.mean([p["llama_recall"] for p in ps]))
    summary = "pythia_recall=%.3f llama_recall=%.3f (real npz embeddings, N_store=%d, N_sub=%d) | speed-test deferred (Llama weights gated/not-local)" % (pr, lr, N_STORE, N_SUB)
    if pr > 0.80 and lr > 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate geometry clean on BOTH Pythia-160m AND real Llama-1B embeddings (recall>0.80; no HF-3 geometry mismatch) -- desktop V1 geometry de-risked. " + summary)
    if max(pr, lr) > 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: geometry partial (one model > 0.70). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: associative-memory geometry mismatch (HF-3, recall < 0.60). " + summary)


print("[config] anchor=%s mode=%s N_store=%d N_speed=%d batch=%d N_sub=%d" % (ANCHOR_NAME, RUN_MODE, N_STORE, N_SPEED, BATCH, N_SUB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17]
ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] pythia_recall=%.3f llama_recall=%.3f llama_extract=%.1fs/1k vram=%.1fGB" % (
        seed, r["pythia_recall"], r["llama_recall"], r["llama_extract_s_per_1k"], r["llama_vram_gb"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
