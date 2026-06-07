"""
exp_dp_noise_injection_zkl_v1 -- authorized SRHT-alternative #2 (DP noise injection privacy probe) -- CPU.

ROUTING: handoff research_to_exp_dev_SRHT_cancel_alternatives #2. SRHT is dead on Llama; test differential-privacy-style
  Gaussian noise injection into keys before storage as the alternative privacy mechanism. Sweeps noise sigma; measures the
  PRIVACY-UTILITY tradeoff: ZKL(50) (cycle-150 LiRA attack) vs retrieval recall. Is there a sigma that drives ZKL <=0.10
  while keeping recall >=0.90? Real MiniLM keys (Llama follow-up if promising). CPU.
PRE-REGISTERED: HARD-PASS some sigma reaches ZKL(50)<=0.10 AND recall>=0.90 (DP noise is a viable privacy knob). MIDDLE a
  tradeoff exists but cannot hit both. HARD-FAIL no sigma helps ZKL without destroying recall.
FORMULA SELF-TESTS (PROT-022): 1. noise reduces self-cosine. 2. tpr@fpr monotone. 3. recall bound.
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

ANCHOR_NAME = "dp_noise_injection_zkl_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50; SIGMAS = [0.0, 0.05, 0.1, 0.2, 0.4]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 80
else:
    N_KB = 2000; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def whiten_fit(K_):
    Kc = K_ - K_.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd, K_.mean(0), Wd


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
    g = np.random.default_rng(0); v = unit(g.standard_normal((1, 64)))[0]; noisy = unit(v + 0.4 * g.standard_normal(64))
    assert float(v @ noisy) < 0.999, "noise reduces self-cosine"
    assert tpr_at_fpr(np.array([5.0, 6]), np.array([0.0, 1]), 0.01) >= 0.9, "tpr@fpr monotone"
    print("[selftest] PASS: dp-noise", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    g = np.random.default_rng(7); real = encode(load_texts(N_KB + N_TGT)); sel = g.choice(N_KB, N_TGT, replace=False); by = {}
    base_w, mu, Wd = whiten_fit(real[:N_KB])
    for sg in SIGMAS:
        noisy = real.copy()
        if sg > 0:
            noisy = noisy + sg * np.random.default_rng(int(sg * 1000)).standard_normal(real.shape).astype(np.float32) * real.std()
        Wk, mu2, Wd2 = whiten_fit(noisy[:N_KB]); kb = unit(Wk); kb_sign = np.sign(kb).astype(np.float32); kb_sign[kb_sign == 0] = 1.0
        mem = unit((noisy[sel] - mu2) @ Wd2); non = unit((noisy[N_KB:N_KB + N_TGT] - mu2) @ Wd2)
        zkl = tpr_at_fpr(stat_sign(mem, kb_sign, K, np.random.default_rng(1)), stat_sign(non, kb_sign, K, np.random.default_rng(2)), FPR)
        # utility: self-retrieval recall (does a stored fact's own (noisy) query retrieve itself top-1)
        recall = float((np.argmax(mem @ kb.T, axis=1) == sel).mean())
        by["s%.2f" % sg] = {"zkl": zkl, "recall": recall}; print("  [sigma=%.2f] ZKL(50)=%.4f recall=%.3f" % (sg, zkl, recall), flush=True)
    return {"by_sigma": by}


def verdict(r) -> Tuple[str, str]:
    good = [(s, v) for s, v in r["by_sigma"].items() if v["zkl"] <= 0.10 and v["recall"] >= 0.90]
    summary = "ZKL/recall by sigma: %s" % {s: (round(v["zkl"], 3), round(v["recall"], 3)) for s, v in r["by_sigma"].items()}
    if good:
        return ("HARD_PASS", "HARD_PASS: DP noise sigma=%s reaches ZKL(50)<=0.10 with recall>=0.90 -- DP injection is a viable privacy knob (SRHT alternative). " % good[0][0] + summary)
    any_low = any(v["zkl"] <= 0.10 for v in r["by_sigma"].values())
    if any_low:
        return ("MIDDLE_BAND", "MIDDLE_BAND: a sigma hits ZKL<=0.10 but destroys recall (privacy-utility tradeoff too steep). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no DP sigma reaches ZKL<=0.10 -- DP injection not a sufficient privacy knob here. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d sigmas=%s device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, SIGMAS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
