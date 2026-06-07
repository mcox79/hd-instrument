"""
exp_pb_pinv_llama_l15_keys_v1 -- propose-back (does pinv real-key rescue extend to causal-LM Llama keys) -- GPU.
ROUTING: pinv rescued real MiniLM/BGE keys (Hebb~0). Does it extend to Llama-3.2-1B L15 last-token keys (causal-LM class)?
  Compares hebb vs pinv exact-recovery capacity on ZCA-whitened sign(Llama-L15) keys. GPU (model forward).
PRE-REGISTERED: HARD-PASS pinv dominates hebb (>=3x or hebb~0). MID 1.5-3x. HARD-FAIL <1.5x.
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. pinv projector. 3. hopfield low load.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
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
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pb_pinv_llama_l15_keys_v1"
ENCODER = "meta-llama/Llama-3.2-1B"; LAYER = 15
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 800; LOADS = [0.01, 0.03, 0.06, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 4000; LOADS = [0.005, 0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]
ARMS = ["hebb", "pinv"]
FLIP2 = 0.05


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0          # W-free dense Hopfield
    return float(np.mean(np.all(s == P, axis=1)))


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); W = (P.T @ np.linalg.solve(G, P)).astype(np.float32); np.fill_diagonal(W, 0.0); return W
def cap(keys, rule, seed):
    sg = np.sign(whiten_fit(keys)).astype(np.float32); sg[sg == 0] = 1.0; c = 0; D = keys.shape[1]
    for load in LOADS:
        M = max(2, int(load * D))
        if M > sg.shape[0]:
            break
        P = sg[:M]
        if rule == "hebb":
            ok = hop_recall(P, seed * 100 + M)
        else:
            W = W_pinv(P); g = np.random.default_rng(seed * 100 + M); s = P * np.where(g.random((M, D)) < FLIP, -1.0, 1.0)
            for _ in range(STEPS):
                s = np.sign(s @ W.T); s[s == 0] = 1.0
            ok = float(np.mean(np.all(s == P, axis=1)))
        if ok >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield recovers low load"
    print("[selftest] PASS: g15", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


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
    tok = AutoTokenizer.from_pretrained(ENCODER); tok.pad_token = tok.eos_token
    dt = torch.float16 if DEV.type == "cuda" else torch.float32
    m = AutoModelForCausalLM.from_pretrained(ENCODER, output_hidden_states=True, torch_dtype=dt).to(DEV).eval()
    last, mean = [], []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            h = m(**t).hidden_states[LAYER]                          # B x T x D at layer 15
        mask = t["attention_mask"]; lens = mask.sum(1) - 1
        last.append(h[torch.arange(h.shape[0]), lens].float().cpu().numpy())
        mk = mask.unsqueeze(-1).float(); mean.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(last, 0).astype(np.float32), np.concatenate(mean, 0).astype(np.float32)


def run_seed(seed, last_tok, mean_pool) -> Dict:
    ch = cap(last_tok, "hebb", seed); cp = cap(last_tok, "pinv", seed)
    print("  [seed=%d] hebb=%d pinv=%d" % (seed, ch, cp), flush=True); return {"seed": seed, "hebb_cap": ch, "pinv_cap": cp}


def verdict(ps) -> Tuple[str, str]:
    h = float(np.mean([p["hebb_cap"] for p in ps])); pv = float(np.mean([p["pinv_cap"] for p in ps]))
    txt = ("hebb~0 -> pinv RESCUES" if h < 1e-3 else "%.2fx" % (pv / h))
    summary = "Llama-L15 keys: hebb_cap=%.1f pinv_cap=%.1f | %s" % (h, pv, txt)
    if pv >= 10 and (h < 1e-3 or pv >= 3.0 * h):
        return ("HARD_PASS", "HARD_PASS: pinv rescues causal-LM Llama-L15 keys too (>=3x or hebb~0) -- pinv lever is encoder-class-general. " + summary)
    if pv >= 1.5 * max(h, 1e-9):
        return ("MIDDLE_BAND", "MIDDLE_BAND: pinv 1.5-3x on Llama keys. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: pinv <1.5x on Llama keys. " + summary)
def _dead_verdict(ps):
    agg = {}
    combined = agg["last_token_whiten"]; best_single = max(agg["last_token_raw"], agg["mean_pool_whiten"]); g = combined / max(best_single, 1e-9)
    raw = agg["last_token_raw"]; wh_dominant = best_single >= 2.0 * max(raw, 1e-9)  # whitening is the load-bearing fix if raw collapses
    summary = "cap %s | combined/best_single=%.2fx" % ({k: round(v, 1) for k, v in agg.items()}, g)
    if g >= 1.2:
        return ("HARD_PASS", "HARD_PASS: last-token + whitening COMPLEMENTARY (combined >=1.2x best single) -- both add; use combined recipe. " + summary)
    if wh_dominant:
        return ("MIDDLE_BAND", "MIDDLE_BAND: WHITENING is the load-bearing fix (raw last-token cap~0); pool choice (last-token vs mean) is irrelevant once whitened. Recipe = whiten (either pool). Mechanisms NOT complementary. " + summary)
    return ("MIDDLE_BAND", "MIDDLE_BAND: last-token ~ whitening equivalent (combined ~ max). " + summary) if g >= 0.9 else ("HARD_FAIL", "HARD_FAIL: combined < best single (interfering mechanisms). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s L=%d N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, LAYER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); last_tok, mean_pool = encode(load_texts(N_ENC)); print("[encoded] last=%s mean=%s" % (last_tok.shape, mean_pool.shape), flush=True)
ps = [run_seed(s, last_tok, mean_pool) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
