"""
exp_srht_realkey_zkl_fix_v1 -- Authorization 3 (SRHT fix; UNBLOCKED by R3 anisotropy confirm) -- CPU.

ROUTING: handoff 8-authorizations #3 (conditional on Auth 2 R3 = anisotropy CONFIRMED, which passed). Apply SRHT (random-sign
  diagonal D then Walsh-Hadamard transform, optionally subsampled) to REAL encoder keys BEFORE sign-quantization+storage, to
  randomize the anisotropic concentrated directions R3 found. Re-run the membership-inference attack (k=50) and compare ZKL:
  real-plain vs real-SRHT vs synthetic-random target. Tests whether SRHT recovers the synthetic-key privacy behavior on real
  keys -- the fix for the cycle-151 11x-worse-on-real-keys finding. Real MiniLM. CPU.
PRE-REGISTERED: HARD-PASS real-SRHT ZKL <= 1.5x synthetic ZKL (SRHT closes the real-key gap). MIDDLE 1.5-3x. HARD-FAIL > 3x
  (SRHT does not recover real-key privacy; deeper fix needed).
FORMULA SELF-TESTS (PROT-022): 1. hadamard orthogonal. 2. SRHT preserves norm. 3. TPR@FPR monotone.
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

ANCHOR_NAME = "srht_realkey_zkl_fix_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
PARA_NOISE = 0.35; FPR = 0.01; K = 50
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_KB = 300; N_TGT = 60
else:
    N_KB = 2000; N_TGT = 300


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def hadamard(n):
    H = np.array([[1.0]], np.float32)
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H / np.sqrt(H.shape[0])


def srht(X, g):
    n = X.shape[1]; m = 1
    while m < n:
        m *= 2
    Xp = np.zeros((X.shape[0], m), np.float32); Xp[:, :n] = X
    D = (g.integers(0, 2, m) * 2 - 1).astype(np.float32); H = hadamard(m)
    return (Xp * D[None, :]) @ H.T                                   # random-sign diagonal then Hadamard


def tpr_at_fpr(member, nonmember, fpr):
    thr = np.quantile(nonmember, 1 - fpr); return float((member >= thr).mean())


def stat(targets, kb_sign, k, g):
    out = []
    for t in targets:
        paras = unit(t[None, :] + PARA_NOISE * g.standard_normal((k, t.shape[0])).astype(np.float32))
        pq = np.sign(paras).astype(np.float32); pq[pq == 0] = 1.0
        out.append(float((pq @ kb_sign.T).max(axis=1).mean() / kb_sign.shape[1]))
    return np.array(out)


def zkl_for(keys_raw, sel, g):
    sign = np.sign(keys_raw).astype(np.float32); sign[sign == 0] = 1.0
    mem = unit(keys_raw[sel]); non = unit(keys_raw[N_KB:N_KB + N_TGT])
    return tpr_at_fpr(stat(mem, sign[:N_KB], K, np.random.default_rng(1)), stat(non, sign[:N_KB], K, np.random.default_rng(2)), FPR)


def _selftest():
    H = hadamard(8); G = H @ H.T; assert np.allclose(G, np.eye(8), atol=1e-5), "hadamard orthogonal"
    g = np.random.default_rng(0); X = g.standard_normal((5, 6)).astype(np.float32); Y = srht(X, g)
    assert abs(np.linalg.norm(Y[0]) - np.linalg.norm(np.r_[X[0], np.zeros(2)])) < 1e-3, "SRHT preserves norm"
    assert tpr_at_fpr(np.array([5.0, 6]), np.array([0.0, 1]), 0.01) >= 0.9, "TPR@FPR monotone"
    print("[selftest] PASS: srht-zkl-fix", flush=True)


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
    real = encode(load_texts(N_KB + N_TGT)); g = np.random.default_rng(7); sel = g.choice(N_KB, N_TGT, replace=False)
    z_plain = zkl_for(real, sel, g)                                  # real keys, no SRHT
    z_srht = zkl_for(srht(real, np.random.default_rng(11)), sel, g)  # real keys + SRHT
    synth = g.standard_normal(real.shape).astype(np.float32); z_synth = zkl_for(synth, sel, g)   # synthetic target
    ratio = z_srht / max(z_synth, 1e-9)
    print("  ZKL real_plain=%.4f real_SRHT=%.4f synthetic=%.4f | SRHT/synth=%.2f" % (z_plain, z_srht, z_synth, ratio), flush=True)
    return {"zkl_real_plain": float(z_plain), "zkl_real_srht": float(z_srht), "zkl_synthetic": float(z_synth), "srht_over_synth": float(ratio)}


def verdict(r) -> Tuple[str, str]:
    ratio = r["srht_over_synth"]
    summary = "ZKL real_plain=%.4f real_SRHT=%.4f synthetic=%.4f | SRHT/synth=%.2f" % (r["zkl_real_plain"], r["zkl_real_srht"], r["zkl_synthetic"], ratio)
    if ratio <= 1.5:
        return ("HARD_PASS", "HARD_PASS: SRHT recovers synthetic-key privacy on real keys (real-SRHT ZKL <=1.5x synthetic) -- the real-key ZKL gap is fixed; SRHT-before-storage ships. " + summary)
    if ratio <= 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: SRHT partially closes the gap (1.5-3x synthetic). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: SRHT does not recover real-key privacy (>3x synthetic) -- deeper fix needed. " + summary)


print("[config] anchor=%s mode=%s n_kb=%d n_tgt=%d k=%d device=cpu" % (ANCHOR_NAME, RUN_MODE, N_KB, N_TGT, K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
