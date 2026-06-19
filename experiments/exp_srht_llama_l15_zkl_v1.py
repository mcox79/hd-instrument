"""
exp_srht_llama_l15_zkl_v1 -- SRHT next-steps test 2: production encoder Llama-3.2-1B L15 left-pad -- GPU.

ROUTING: handoff research_to_exp_dev_SRHT_next_steps test 2. The customer claim must be on the PRODUCTION encoder
  (Llama-3.2-1B BASE, layer 15, LEFT-padded, last-token pool -- the cycle 150/151 encoder), not the MiniLM proxy. Runs the
  cycle-150 LiRA attack (max-over-k-paraphrase sign-grounding, FPR=0.01, k=50) with SRHT passes {0,1,2,3} on Llama L15 keys.
  Confirms whether the 1.74x relative effect + the ~0.175 plateau transfer to the real encoder (decides qualified-claim
  framing). GPU (Llama forward). use_safetensors for torch<2.6.
PRE-REGISTERED: HARD-PASS some SRHT pass count reaches ZKL(50)<=0.10 on Llama (HIPAA claim restorable). MIDDLE reduces but
  plateaus >0.10 (qualified ~Nx claim). HARD-FAIL SRHT no effect on Llama (relative claim also at risk).
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. iterated srht preserves norm. 3. tpr@fpr monotone.
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "srht_llama_l15_zkl_v1"
MODEL = "meta-llama/Llama-3.2-1B"; LAYER = 15
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50; PASSES = [0, 1, 2, 3]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 200; N_TGT = 60
else:
    N_KB = 1500; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H / np.sqrt(H.shape[0])


def srht_iter(X, passes, g):
    n = X.shape[1]; m = 1
    while m < n:
        m *= 2
    Xp = np.zeros((X.shape[0], m), np.float32); Xp[:, :n] = X; H = hadamard(m)
    for _ in range(passes):
        D = (g.integers(0, 2, m) * 2 - 1).astype(np.float32); Xp = (Xp * D[None, :]) @ H.T
    return Xp


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def stat_sign(targets, kb_sign, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
    return np.array(out)


def _selftest():
    H = hadamard(8); assert np.allclose(H @ H.T, np.eye(8), atol=1e-5), "hadamard orthogonal"
    g = np.random.default_rng(0); X = g.standard_normal((4, 6)).astype(np.float32); Y = srht_iter(X, 2, g)
    assert abs(np.linalg.norm(Y[0]) - np.linalg.norm(np.r_[X[0], np.zeros(2)])) < 1e-3, "iterated srht preserves norm"
    assert tpr_at_fpr(np.array([5.0, 6]), np.array([0.0, 1]), 0.01) >= 0.9, "tpr@fpr monotone"
    print("[selftest] PASS: srht-llama-l15", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
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
    tok = AutoTokenizer.from_pretrained(MODEL); tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    m = AutoModelForCausalLM.from_pretrained(MODEL, use_safetensors=True, output_hidden_states=True, torch_dtype=torch.float16).to(DEV).eval(); out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.hidden_states[LAYER]                   # (B,T,D); left-pad -> last token is real last token
        out.append(h[:, -1, :].float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def zkl50(keys_raw, sel, g):
    Wkb, mu, Wd = whiten_fit(keys_raw[:N_KB]); kb_sign = np.sign(unit(Wkb)).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
    mem = unit((keys_raw[sel] - mu) @ Wd); non = unit((keys_raw[N_KB:N_KB + N_TGT] - mu) @ Wd)
    return tpr_at_fpr(stat_sign(mem, kb_sign, K, np.random.default_rng(1)), stat_sign(non, kb_sign, K, np.random.default_rng(2)), FPR)


def run() -> Dict:
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False); by = {}
    print("  [encoded] Llama L%d left-pad last-token, D=%d" % (LAYER, real.shape[1]), flush=True)
    for p in PASSES:
        keys = real if p == 0 else srht_iter(real, p, np.random.default_rng(10 + p))
        by["P%d" % p] = zkl50(keys, sel, g); print("  [SRHT passes=%d] ZKL(50)=%.4f" % (p, by["P%d" % p]), flush=True)
    return {"by_passes": by, "D": int(real.shape[1])}


def verdict(r) -> Tuple[str, str]:
    vals = [r["by_passes"]["P%d" % p] for p in PASSES]; mn = min(vals); base = vals[0]
    summary = "Llama-L15 ZKL(50) by SRHT passes: %s | base=%.4f min=%.4f (HIPAA<=0.10)" % ({("P%d" % p): round(r["by_passes"]["P%d" % p], 4) for p in PASSES}, base, mn)
    if mn <= 0.10:
        return ("HARD_PASS", "HARD_PASS: on production Llama-L15 encoder, iterated SRHT reaches ZKL(50)<=0.10 -- HIPAA absolute claim restorable on the real encoder. " + summary)
    if mn < base * 0.7:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SRHT reduces Llama-L15 ZKL but plateaus >0.10 -- ship the qualified ~%.1fx-improvement claim, not absolute HIPAA. " % (base / max(mn, 1e-9)) + summary)
    return ("HARD_FAIL", "HARD_FAIL: SRHT has little effect on Llama-L15 -- relative claim also at risk; re-scope. " + summary)


print("[config] anchor=%s mode=%s model=%s layer=%d n_kb=%d n_tgt=%d passes=%s" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, N_KB, N_TGT, PASSES), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
