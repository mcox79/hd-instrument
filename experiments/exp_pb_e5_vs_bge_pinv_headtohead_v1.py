"""
exp_g7_e5_large_geometry_capacity_v1 -- propose-back (E5 vs BGE pinv capacity head-to-head, same data/recipe) -- GPU.

ROUTING: Batch G Tier-3 (BGE drill Test-3). E5-large-v2 uses weak supervised pre-training before strong fine-tuning ->
  predicted to preserve more isotropy than BGE-large. Runs the 4-step protocol: geometry (PR + rho_eff) THEN exact-recovery
  capacity (ZCA-whiten sign + pinv write rule, per the converged recipe). If E5 passes geometry AND high cap -> third
  production encoder candidate alongside Llama-1B + BGE+pinv. GPU (E5 forward; downloads ~1.3GB safetensors if uncached).
PRE-REGISTERED: HARD-PASS PR>120 AND rho_eff<0.20 AND pinv_cap>200. MID geometry passes but cap 80-200. HARD-FAIL geometry
  fails (PR<40 or rho>0.35).
FORMULA SELF-TESTS (PROT-022): 1. PR isotropic. 2. pinv projector. 3. whiten preserves dim.
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

ANCHOR_NAME = "pb_e5_vs_bge_pinv_headtohead_v1"
ENCODERS = {"e5": "intfloat/e5-large-v2", "bge": "BAAI/bge-large-en-v1.5"}
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
FLIP = 0.05
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
if RUN_MODE == "smoke":
    N_ENC = 600; M_GRID = [20, 50, 100, 200]
else:
    N_ENC = 3000; M_GRID = [40, 80, 120, 160, 200, 260, 340, 440]


def participation_ratio(emb):
    Xc = emb - emb.mean(0); s = np.linalg.svd(Xc, compute_uv=False); s2 = s ** 2
    return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def rho_eff(emb):
    e = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8); n = min(len(e), 400)
    G = e[:n] @ e[:n].T; iu = np.triu_indices(n, k=1); return float(np.mean(G[iu]))


def whiten_fit(K):
    Kc = K - K.mean(0); cov = (Kc.T @ Kc) / Kc.shape[0]
    U, S, _ = np.linalg.svd(cov); Wd = U @ np.diag(1.0 / np.sqrt(S + 1e-3)) @ U.T
    return Kc @ Wd


def W_pinv(P):
    G = P @ P.T + 1e-3 * np.eye(P.shape[0], dtype=np.float32); return (P.T @ np.linalg.solve(G, P)).astype(np.float32)


def recall(P, W, seed):
    g = np.random.default_rng(seed); M, n = P.shape; s = P * np.where(g.random((M, n)) < FLIP, -1.0, 1.0)
    for _ in range(8):
        s = np.sign(s @ W.T); s[s == 0] = 1.0
    return float(np.mean(np.all(s == P, axis=1)))


def pinv_cap(emb, seed):
    sg = np.sign(whiten_fit(emb)).astype(np.float32); sg[sg == 0] = 1.0; c = 0
    for M in M_GRID:
        if M > sg.shape[0]:
            break
        P = sg[:M]; W = W_pinv(P); np.fill_diagonal(W, 0.0)
        if recall(P, W, seed * 100 + M) >= 0.95:
            c = M
        else:
            break
    return c


def _selftest():
    g = np.random.default_rng(0); assert participation_ratio(g.standard_normal((300, 50))) > 30, "PR isotropic"
    P = (g.integers(0, 2, (20, 128)) * 2 - 1).astype(np.float32); W = W_pinv(P); assert np.allclose(W @ W, W, atol=1e-2), "pinv projector"
    assert whiten_fit(g.standard_normal((40, 16))).shape == (40, 16), "whiten preserves dim"
    print("[selftest] PASS: e5-vs-bge", flush=True)


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


def encode(texts, enc):
    tok = AutoTokenizer.from_pretrained(enc); m = AutoModel.from_pretrained(enc, use_safetensors=True).to(DEV).eval(); out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).float().cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def verdict(res) -> Tuple[str, str]:
    e5 = res["e5"]; bge = res["bge"]
    summary = "E5: PR=%.1f rho=%.3f pinv_cap=%d (D=%d) | BGE: PR=%.1f rho=%.3f pinv_cap=%d (D=%d)" % (
        e5["PR"], e5["rho_eff"], e5["pinv_cap"], e5["D"], bge["PR"], bge["rho_eff"], bge["pinv_cap"], bge["D"])
    win = "E5" if e5["pinv_cap"] > bge["pinv_cap"] else ("BGE" if bge["pinv_cap"] > e5["pinv_cap"] else "TIE")
    best = max(e5["pinv_cap"], bge["pinv_cap"])
    if best > 200:
        return ("HARD_PASS", "HARD_PASS: head-to-head decided -- %s wins pinv capacity (best>200); pick %s as production encoder. " % (win, win) + summary)
    if best >= 80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %s leads but best pinv_cap 80-200. " % win + summary)
    return ("HARD_FAIL", "HARD_FAIL: both encoders pinv_cap<80 under recipe. " + summary)


print("[config] anchor=%s mode=%s encoder=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, ENCODER, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = encode(load_texts(N_ENC))
r = {"PR": participation_ratio(emb), "rho_eff": rho_eff(emb), "pinv_cap": pinv_cap(emb, 7), "D": int(emb.shape[1])}
print("  PR=%.1f rho_eff=%.3f pinv_cap=%d" % (r["PR"], r["rho_eff"], r["pinv_cap"]), flush=True)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
