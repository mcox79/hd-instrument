"""
exp_substrate_noise_bft_bge_v1 -- top20 #9: substrate noise/BFT robustness vs bge-small -- GPU.

ROUTING: handoff top20 #9 (value-add drill cheap pre-test #2). Encodes real text (HotpotQA sentences) with bge-small;
  adds Gaussian noise at std {0.05,0.20,0.50}; compares bare-bge nearest-neighbor recall@1 to substrate (sign-binarize +
  pseudoinverse W + H=2 multi-head BFT read-average) recall@1 at each noise level. Tests whether the substrate's
  error-correcting read is more noise-robust than raw cosine. GPU for the bge encode (small; CPU-feasible).
PRE-REGISTERED: HARD-PASS substrate recall@1 >= 0.90 at noise 0.50 AND bge degrades by >= 0.20. MIDDLE substrate beats bge
  by >= 0.10 at 0.50. HARD-FAIL substrate <= bge at 0.50.
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. sign binarize. 3. orthogonal rotation.
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

ANCHOR_NAME = "substrate_noise_bft_bge_v1"; BI = "BAAI/bge-small-en-v1.5"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
NITEMS = 300 if RUN_MODE == "smoke" else 1000; NOISES = [0.05, 0.20, 0.50]; H = 2


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert set(np.unique(np.sign(g.standard_normal(20)))) <= {-1.0, 0.0, 1.0}, "sign binarize"
    Q, _ = np.linalg.qr(g.standard_normal((8, 8))); assert np.allclose(Q @ Q.T, np.eye(8), atol=1e-5), "orthogonal rotation"
    print("[selftest] PASS: substrate-noise-bft", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def load_sents(n):
    out = []; seen = set()
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        for sl in (r.get("context") or {}).get("sentences") or []:
            for s in sl:
                t = s.strip()
                if 40 < len(t) < 300 and t not in seen:
                    seen.add(t); out.append(t)
                    if len(out) >= n:
                        return out
    return out


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    sents = load_sents(NITEMS)
    if len(sents) < 50:
        print("[FATAL] corpus too small", flush=True); return {"by": {}, "n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    E = encode(sents, tok, m); del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    n = len(E); En = unit(E)
    # substrate: sign-binarize keys; H=2 orthogonal-rotation heads, read-average consensus on the binarized space
    g = np.random.default_rng(7); B = np.sign(En).astype(np.float32); D = B.shape[1]
    Rs = [np.linalg.qr(g.standard_normal((D, D)).astype(np.float32))[0] for _ in range(H)]
    heads = [unit(B @ R.T) for R in Rs]
    by = {}
    for ns in NOISES:
        q = En + ns * g.standard_normal(En.shape).astype(np.float32); qn = unit(q)
        # bge nearest neighbor
        bge_hit = 0
        for i in range(0, n, 256):
            s = qn[i:i + 256] @ En.T; bge_hit += int((np.argmax(s, axis=1) == np.arange(i, min(i + 256, n))).sum())
        # substrate: binarize noisy query, H-head read-average over binarized space
        qb = np.sign(q).astype(np.float32); sub_hit = 0
        for i in range(0, n, 256):
            qq = qb[i:i + 256]; s = sum(unit(qq @ R.T) @ hd.T for R, hd in zip(Rs, heads)) / H
            sub_hit += int((np.argmax(s, axis=1) == np.arange(i, min(i + 256, n))).sum())
        by["n%.2f" % ns] = {"bge": bge_hit / n, "sub": sub_hit / n}
        print("  noise=%.2f bge_recall@1=%.3f substrate_recall@1=%.3f" % (ns, by["n%.2f" % ns]["bge"], by["n%.2f" % ns]["sub"]), flush=True)
    return {"by": by, "n": n}


def verdict(r) -> Tuple[str, str]:
    hi = r["by"].get("n0.50", {"bge": 0, "sub": 0}); lo = r["by"].get("n0.05", {"bge": 1, "sub": 1})
    summary = "at noise0.50 bge=%.3f substrate=%.3f (bge drop from 0.05: %.3f); n=%d" % (hi["bge"], hi["sub"], lo["bge"] - hi["bge"], r["n"])
    if hi["sub"] >= 0.90 and (lo["bge"] - hi["bge"]) >= 0.20:
        return ("HARD_PASS", "HARD_PASS: substrate recall@1>=0.90 at noise 0.50 while bge degrades >=0.20 -- substrate error-correcting read is decisively more noise-robust. " + summary)
    if hi["sub"] - hi["bge"] >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate beats bge by >=0.10 at noise 0.50. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: substrate does not beat bge at noise 0.50. " + summary)


print("[config] anchor=%s mode=%s n_items=%d noises=%s H=%d" % (ANCHOR_NAME, RUN_MODE, NITEMS, NOISES, H), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
