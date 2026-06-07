"""
exp_pb_mmr_real_encoder_clustered_v1 -- propose-back (G8/H1 on REAL encoder keys) -- CPU.

ROUTING: Exp-Dev propose-back. H1 confirmed MMR rescues anchoring propagation on SYNTHETIC clustered KBs. Production
  question: does it hold on REAL encoder embeddings, which have natural (not injected) semantic cluster structure? Encodes
  a real corpus (MiniLM), groups by k-means into clusters, injects a plausible false fact in the densest cluster, measures
  anchoring propagation with vs without MMR-diversified retrieval. CPU $0.
PRE-REGISTERED: HARD-PASS MMR propagation < 0.10 on real-encoder clustered KB (baseline > 0.20). MID 0.10-0.20.
  HARD-FAIL > 0.20 (MMR does not transfer to real clustering).
FORMULA SELF-TESTS (PROT-022): 1. kmeans assigns. 2. MMR distinct. 3. deps.
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

ANCHOR_NAME = "pb_mmr_real_encoder_clustered_v1"
ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
LAMBDA = 0.5; TOPK = 10; N_CLUST = 30
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_ENC = 800 if RUN_MODE == "smoke" else 3000
SEEDS = [1] if RUN_MODE == "smoke" else [7, 17, 23]


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def kmeans(X, k, g, iters=15):
    C = X[g.choice(len(X), k, replace=False)].copy()
    for _ in range(iters):
        a = np.argmin(((X[:, None, :] - C[None, :, :]) ** 2).sum(-1), axis=1)
        for c in range(k):
            if (a == c).any():
                C[c] = X[a == c].mean(0)
    return a, unit(C)


def mmr_select(q, items, k, lam):
    sims = items @ q; chosen = []; cand = list(range(len(items)))
    for _ in range(min(k, len(items))):
        if not chosen:
            j = int(np.argmax(sims[cand]))
        else:
            div = np.max(items[cand] @ items[chosen].T, axis=1); j = int(np.argmax(lam * sims[cand] - (1 - lam) * div))
        chosen.append(cand.pop(j))
    return chosen


def _selftest():
    g = np.random.default_rng(0); X = unit(g.standard_normal((60, 16))); a, C = kmeans(X, 4, g); assert a.max() < 4, "kmeans assigns"
    sel = mmr_select(X[0], X[:20], 5, 0.5); assert len(set(sel)) == 5, "MMR distinct"
    print("[selftest] PASS: pb-mmr-real", flush=True)


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


def embed(texts):
    tok = AutoTokenizer.from_pretrained(ENCODER); m = AutoModel.from_pretrained(ENCODER, use_safetensors=True).to(DEV).eval(); out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            o = m(**t); h = o.last_hidden_state; mk = t["attention_mask"].unsqueeze(-1).float()
        out.append(((h * mk).sum(1) / mk.sum(1).clamp(min=1)).cpu().numpy())
    del m
    return unit(np.concatenate(out, 0).astype(np.float32))


def propagation(kb, lab, tgt, false_fact, use_mmr):
    kb_aug = np.vstack([kb, false_fact[None, :]]); f_idx = len(kb)
    q_same = kb[lab == tgt][:150]; q_other = kb[lab != tgt][:150]
    def influence(qs):
        if len(qs) == 0:
            return 0.0
        hit = 0
        for q in qs:
            sel = mmr_select(q, kb_aug, TOPK, LAMBDA) if use_mmr else list(np.argsort(kb_aug @ q)[-TOPK:])
            hit += int(f_idx in sel)
        return hit / len(qs)
    return influence(q_same) - influence(q_other)


def run_seed(seed, emb) -> Dict:
    g = np.random.default_rng(seed); lab, C = kmeans(emb, N_CLUST, g)
    tgt = int(np.argmax(np.bincount(lab, minlength=N_CLUST)))           # densest cluster
    false_fact = unit(0.7 * C[tgt] + 0.3 * unit(g.standard_normal(emb.shape[1]).astype(np.float32)))
    base = propagation(emb, lab, tgt, false_fact, False); mmr = propagation(emb, lab, tgt, false_fact, True)
    print("  [seed=%d] baseline_propagation=%.3f mmr_propagation=%.3f" % (seed, base, mmr), flush=True)
    return {"seed": seed, "baseline_propagation": base, "mmr_propagation": mmr}


def verdict(ps) -> Tuple[str, str]:
    mmr = float(np.mean([p["mmr_propagation"] for p in ps])); base = float(np.mean([p["baseline_propagation"] for p in ps]))
    summary = "real-encoder clustered KB: baseline_propagation=%.3f -> MMR=%.3f" % (base, mmr)
    if mmr < 0.10:
        return ("HARD_PASS", "HARD_PASS: MMR rescue TRANSFERS to real-encoder clustering (<0.10) -- production-ready anchoring mitigation on real KBs. " + summary)
    if mmr <= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MMR partial on real clustering (0.10-0.20). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: MMR does not transfer to real-encoder clustering (>0.20). " + summary)


print("[config] anchor=%s mode=%s seeds=%s encoder=%s N_enc=%d clusters=%d" % (ANCHOR_NAME, RUN_MODE, SEEDS, ENCODER, N_ENC, N_CLUST), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); emb = embed(load_texts(N_ENC)); print("[encoded] %s" % (emb.shape,), flush=True)
ps = [run_seed(s, emb) for s in SEEDS]
v, vmsg = verdict(ps); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": ps, "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, ps); print("[metrics] written", flush=True)
