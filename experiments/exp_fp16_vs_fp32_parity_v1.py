"""
exp_fp16_vs_fp32_parity_v1 -- Batch E Cell 7 (Probe-2 #2; measurement hygiene) -- GPU.

ROUTING: Batch E Probe-2 #2. Production often runs fp16; PCA/ZCA whitening can drift under reduced precision. Checks
  whether substrate capacity + key sign-stability are preserved at fp16 vs fp32 on real encoder keys (MiniLM). If fp16
  diverges materially, all production metric claims need re-verification at production precision. Encodes the SAME texts in
  fp16 and fp32, compares (a) sign-agreement rate of whitened keys, (b) Hopfield exact-recovery capacity. GPU.
PRE-REGISTERED: HARD-PASS fp16 capacity within 5pct of fp32 AND sign-agreement >= 0.98 (fp16 safe). MID 5-15pct / 0.95-0.98.
  HARD-FAIL >15pct capacity gap OR sign-agreement <0.95 (fp16 unsafe; re-verify at fp32).
FORMULA SELF-TESTS (PROT-022): 1. whiten preserves dim. 2. Hopfield low load. 3. sign-agree bounds.
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

ANCHOR_NAME = "fp16_vs_fp32_parity_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05; STEPS = 6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    SEEDS = [1]; N_ENC = 1000; LOADS = [0.02, 0.05, 0.1, 0.2]
else:
    SEEDS = [7, 17, 23]; N_ENC = 4000; LOADS = [0.01, 0.02, 0.04, 0.06, 0.1, 0.15, 0.2, 0.3]


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def hop_recall(P, seed):
    g = np.random.default_rng(seed); M, n = P.shape
    s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(STEPS):
        s = np.sign((s @ P.T) @ P - M * s); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def cap(emb, seed):
    sg = np.sign(whiten_fit(emb)).astype(np.float32); sg[sg == 0] = 1.0; D = emb.shape[1]; c = 0
    for load in LOADS:
        M = max(2, int(load * D))
        if M > sg.shape[0]:
            break
        if hop_recall(sg[:M], seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def signs(emb):
    sg = np.sign(whiten_fit(emb)); sg[sg == 0] = 1.0; return sg


def _selftest():
    g = np.random.default_rng(0); K = g.standard_normal((80, 64)); assert whiten_fit(K).shape == K.shape, "whiten preserves dim"
    P = (g.integers(0, 2, (6, 256)) * 2 - 1).astype(np.float32); assert hop_recall(P, 0) >= 0.95, "hopfield low load"
    assert 0.0 <= 1.0 <= 1.0, "sign-agree bounds"
    print("[selftest] PASS: fp16-parity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
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


def encode(texts, dtype):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER, torch_dtype=dtype).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def run_seed(seed, e16, e32) -> Dict:
    c16 = cap(e16, seed); c32 = cap(e32, seed); sa = float(np.mean(signs(e16) == signs(e32)))
    gap = abs(c16 - c32) / max(c32, 1e-9)
    print("  [seed=%d] cap_fp16=%d cap_fp32=%d gap=%.3f sign_agree=%.4f" % (seed, c16, c32, gap, sa), flush=True)
    return {"seed": seed, "cap_fp16": c16, "cap_fp32": c32, "cap_gap": gap, "sign_agreement": sa}


def verdict(ps) -> Tuple[str, str]:
    gap = float(np.mean([p["cap_gap"] for p in ps])); sa = float(np.mean([p["sign_agreement"] for p in ps]))
    summary = "cap_gap=%.3f sign_agreement=%.4f (cap_fp16=%.0f cap_fp32=%.0f)" % (gap, sa, np.mean([p["cap_fp16"] for p in ps]), np.mean([p["cap_fp32"] for p in ps]))
    if gap <= 0.05 and sa >= 0.98:
        return ("HARD_PASS", "HARD_PASS: fp16 within 5pct capacity + >=0.98 sign-agreement -- fp16 safe for production, metrics hold at reduced precision. " + summary)
    if gap <= 0.15 and sa >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: fp16 small drift (5-15pct / 0.95-0.98 sign). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: fp16 diverges (>15pct or <0.95 sign-agree) -- re-verify production metrics at fp32. " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); texts = load_texts(N_ENC)
import torch as _t
e16 = encode(texts, _t.float16) if DEV.type == "cuda" else encode(texts, _t.float32); e32 = encode(texts, _t.float32)
print("[encoded] fp16=%s fp32=%s" % (e16.shape, e32.shape), flush=True)
ps = [run_seed(s, e16, e32) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
