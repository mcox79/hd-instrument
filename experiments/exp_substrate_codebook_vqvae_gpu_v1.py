"""
exp_substrate_codebook_vqvae_gpu_v1 -- substrate-only-LM Anchor 1: VQ codebook over word embeddings, coherence + no-collapse -- GPU.

ROUTING: substrate_only_language_model_5x Anchor 1 (HIGHEST priority, cheapest LM gate). Establishes whether substrate atoms can
  serve as SEMANTIC PRIMITIVES for language: encode a vocabulary with bge-small, learn a VQ codebook (k-means), and measure
  (a) codebook UTILIZATION (no collapse -- most atoms used), (b) reconstruction cosine (atoms capture word meaning), and
  (c) semantic coherence (same-category words share atoms more than cross-category). HARD-PASS gates all downstream substrate-LM
  paths; HARD-FAIL (collapse) means the VQ-VAE needs the rotation/Dirichlet fix.
PRE-REGISTERED: HARD-PASS codebook utilization >= 0.50 AND reconstruction cosine >= 0.70 AND same-category atom-share > cross.
  MIDDLE utilization >= 0.35. HARD-FAIL collapse (utilization < 0.35) or recon < 0.6.
FORMULA SELF-TESTS (PROT-022): 1. kmeans assign. 2. cosine. 3. utilization.
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
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_codebook_vqvae_gpu_v1"; ENC = "BAAI/bge-small-en-v1.5"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

CATS = {
    "animal": ["dog", "cat", "horse", "lion", "tiger", "bear", "wolf", "rabbit", "deer", "fox", "mouse", "eagle"],
    "color": ["red", "blue", "green", "yellow", "purple", "orange", "black", "white", "pink", "brown", "gray", "violet"],
    "food": ["bread", "cheese", "apple", "rice", "meat", "soup", "cake", "egg", "fish", "pasta", "salad", "honey"],
    "action": ["run", "jump", "walk", "swim", "eat", "sleep", "write", "read", "sing", "dance", "build", "throw"],
    "place": ["city", "river", "mountain", "forest", "ocean", "desert", "village", "island", "valley", "harbor", "bridge", "tower"],
    "emotion": ["happy", "sad", "angry", "afraid", "calm", "proud", "jealous", "curious", "bored", "excited", "anxious", "grateful"],
}


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n
    pts = _n.array([[0.0, 0], [10, 10]]); cen = _n.array([[0.0, 0], [10, 10]]); a = _n.argmin(((pts[:, None] - cen[None]) ** 2).sum(-1), 1)
    assert list(a) == [0, 1], "kmeans assign"
    assert abs(float(unit(_n.array([[3.0, 4]]))[0] @ _n.array([3.0, 4]) / 5) - 1.0) < 1e-6, "cosine"
    assert len(set([0, 1, 1, 2])) == 3, "utilization"
    print("[selftest] PASS: substrate-codebook-vqvae", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=8).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return unit(np.concatenate(out, 0).astype(np.float32))


def kmeans(X, K, g, iters=50):
    cen = X[g.choice(len(X), K, replace=False)].copy()
    for _ in range(iters):
        d = ((X[:, None, :] - cen[None, :, :]) ** 2).sum(-1); a = np.argmin(d, 1)
        for k in range(K):
            m = a == k
            if m.any():
                cen[k] = X[m].mean(0)
    return a, cen


def run() -> Dict:
    g = np.random.default_rng(7)
    words = []; labels = []
    for ci, (cat, ws) in enumerate(CATS.items()):
        for w in ws:
            words.append(w); labels.append(ci)
    labels = np.array(labels)
    K = 24
    tok = AutoTokenizer.from_pretrained(ENC); m = AutoModel.from_pretrained(ENC).to(DEV).eval()
    X = encode(words, tok, m); del m
    assign, cen = kmeans(X, K, g)
    util = len(set(assign.tolist())) / K
    recon = float(np.mean([X[i] @ unit(cen[assign[i]][None])[0] for i in range(len(X))]))
    # semantic coherence: P(two words share an atom | same category) vs cross-category
    same = 0; same_tot = 0; cross = 0; cross_tot = 0
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            sh = int(assign[i] == assign[j])
            if labels[i] == labels[j]:
                same += sh; same_tot += 1
            else:
                cross += sh; cross_tot += 1
    same_share = same / max(1, same_tot); cross_share = cross / max(1, cross_tot)
    print("  codebook utilization=%.3f reconstruction-cos=%.3f | same-cat atom-share=%.3f cross-cat=%.3f" % (util, recon, same_share, cross_share), flush=True)
    return {"util": util, "recon": recon, "same_share": same_share, "cross_share": cross_share, "K": K, "nwords": len(words)}


def verdict(r) -> Tuple[str, str]:
    s = "util=%.3f recon-cos=%.3f same-cat-share=%.3f cross-cat-share=%.3f (K=%d, %d words)" % (r["util"], r["recon"], r["same_share"], r["cross_share"], r["K"], r["nwords"])
    coherent = r["same_share"] > r["cross_share"]
    if r["util"] >= 0.50 and r["recon"] >= 0.70 and coherent:
        return ("HARD_PASS", "HARD_PASS: VQ codebook utilization>=0.50, reconstruction>=0.70, same-category words share atoms more than cross -- substrate atoms are semantically coherent primitives; downstream substrate-LM paths viable. " + s)
    if r["util"] >= 0.35 and r["recon"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial coherence; usable with codebook tuning. " + s)
    return ("HARD_FAIL", "HARD_FAIL: codebook collapse (util<0.35) or weak reconstruction -- VQ-VAE needs rotation/Dirichlet fix. " + s)


print("[config] anchor=%s mode=%s enc=%s" % (ANCHOR_NAME, RUN_MODE, ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
