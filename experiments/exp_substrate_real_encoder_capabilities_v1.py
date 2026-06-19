"""
exp_substrate_real_encoder_capabilities_v1 -- substrate capabilities on REAL encoder embeddings (MiniLM/Pythia) -- GPU.

ROUTING: PHASE4A-1 follow-on -- validate the core substrate capabilities (single-hop, multi-hop 2-hop chaining,
  counterfactual update) using REAL text-encoder keys (MiniLM 384-d and Pythia-160m 768-d on medical text), not random
  codewords. Confirms capabilities survive realistic (correlated) key geometry after whitening. torch GPU $0.

PRE-REGISTERED bands: HARD-PASS all 3 dims >= 0.90 for BOTH encoders. MIDDLE: >= 0.75. HARD-FAIL: any dim < 0.60.
FORMULA SELF-TESTS (PROT-022): 1. whiten keys. 2. single-hop on whitened keys. 3. cuda.
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

ANCHOR_NAME = "substrate_real_encoder_capabilities_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"; PYTHIA_ID = "EleutherAI/pythia-160m"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_FACTS = 200; N_SUB = 1024
else:
    SEEDS = [7, 17, 23]; N_FACTS = 400; N_SUB = 1024
N_VAL = 32


def whiten(emb, n_sub):
    mu = emb.mean(0); X = emb - mu; U, S, Vt = np.linalg.svd(X, full_matrices=False); k = min(n_sub, len(S))
    K = (X @ (Vt[:k].T / (S[:k] + 1e-6))); K /= np.linalg.norm(K, axis=1, keepdims=True) + 1e-8
    if k < n_sub:
        K = np.pad(K, ((0, 0), (0, n_sub - k)))
    return K.astype(np.float32)


def bp(M, n, g):
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32); return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); emb = g.standard_normal((20, 48)).astype(np.float32); K = whiten(emb, 128)
    assert K.shape == (20, 128), "whiten keys"
    EV = bp(4, 128, g); v = g.integers(0, 4, 20); W = (EV[v].T @ K); assert int(np.argmax(EV @ (W @ K[3]))) == v[3], "single-hop on whitened"
    print("[selftest] PASS: whiten singlehop", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer


def load_texts(n):
    return [json.loads(l)["question"][:400] for l in open(MEDQA, encoding="utf-8")][:n]


def enc(model_id, texts, causal):
    tok = AutoTokenizer.from_pretrained(model_id)
    if causal:
        tok.pad_token = tok.eos_token; tok.truncation_side = "left"
        model = AutoModelForCausalLM.from_pretrained(model_id, output_hidden_states=True).to(DEVICE).eval()
    else:
        model = AutoModel.from_pretrained(model_id).to(DEVICE).eval()
    out = []
    for i in range(0, len(texts), 24):
        t = tok(texts[i:i + 24], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEVICE)
        with torch.no_grad():
            o = model(**t)
        h = o.hidden_states[12] if causal else o.last_hidden_state
        m = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).cpu().numpy())
    del model; torch.cuda.empty_cache()
    e = np.concatenate(out, 0).astype(np.float32); return e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-8)


def capabilities(K, seed):
    g = np.random.default_rng(seed); n = K.shape[1]; M = K.shape[0]; EV = bp(N_VAL, n, g)
    # single-hop
    v = [int(g.integers(0, N_VAL)) for _ in range(M)]; W = (EV[np.array(v)].T @ K).astype(np.float32)
    sh = float(np.mean([int(np.argmax(EV @ (W @ K[i]))) == v[i] for i in range(M)]))
    # multi-hop: chain K[i]->K[i+1]; 2-hop retrieve
    Wc = (K[1:].T @ K[:-1]).astype(np.float32); ev = list(range(M - 2))
    mh = float(np.mean([int(np.argmax(K @ (Wc @ K[int(np.argmax(K @ (Wc @ K[i])))]))) == i + 2 for i in ev[:200]]))
    # counterfactual: update value via delete-and-replace
    upd = list(g.choice(M, size=min(150, M), replace=False)); newv = {}
    for i in upd:
        nv = int((v[i] + 1 + g.integers(0, N_VAL - 1)) % N_VAL); W -= np.outer(W @ K[i], K[i]); W += np.outer(EV[nv], K[i]); newv[i] = nv
    cf = float(np.mean([int(np.argmax(EV @ (W @ K[i]))) == newv[i] for i in upd]))
    return sh, mh, cf


def run_seed(seed) -> Dict:
    texts = load_texts(N_FACTS)
    res = {"seed": seed}
    for name, mid, causal in [("minilm", MINILM_ID, False), ("pythia", PYTHIA_ID, True)]:
        K = whiten(enc(mid, texts, causal), N_SUB); sh, mh, cf = capabilities(K, seed)
        res[name] = {"single_hop": sh, "multi_hop": mh, "counterfactual": cf}
    return res


def verdict(ps) -> Tuple[str, str]:
    agg = {}
    for enc_name in ("minilm", "pythia"):
        for dim in ("single_hop", "multi_hop", "counterfactual"):
            agg["%s_%s" % (enc_name, dim)] = float(np.mean([p[enc_name][dim] for p in ps]))
    lo = min(agg.values())
    summary = " ".join("%s=%.2f" % (k, v) for k, v in agg.items())
    if lo >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate capabilities hold on REAL encoder embeddings (both MiniLM + Pythia, all dims >=0.90). " + summary)
    if lo >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: capabilities mostly hold on real encoders; weakest %.2f. " % lo + summary)
    return ("HARD_FAIL", "HARD_FAIL: a capability dim < 0.60 on real encoder. " + summary)


print("[config] anchor=%s mode=%s seeds=%s N_facts=%d N_sub=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, N_FACTS, N_SUB), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); ps = []
for seed in SEEDS:
    r = run_seed(seed); ps.append(r)
    print("  [seed=%d] minilm=%s pythia=%s" % (seed, r["minilm"], r["pythia"]), flush=True)
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
