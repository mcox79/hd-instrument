"""
exp_effective_rank_svd_v1 -- Batch A Rank 2: effective-rank diagnostic of the substrate encoder -- CPU.

ROUTING: Research Batch A (framework gate). Validates the intrinsic-dim-limited retrieval framework underpinning CS-1 /
  DIMSPARSE3 / SIG-1 / NRO-1. Encodes text with MiniLM, computes the effective rank d_eff of the embedding matrix
  (participation ratio (sum s)^2 / sum s^2) plus the 90%/99%-variance rank. Directly tests the capacity-finding from
  today's metric work (real-encoder Hopfield capacity is bounded by the encoder's INTRINSIC dim, not the nominal 384).
  CPU (MiniLM encode brief on GPU; SVD on CPU).

PRE-REGISTERED bands: HARD-PASS d_eff (participation ratio) <= 120 (intrinsic-dim-limited framework holds; expected ~50-80).
  MIDDLE: 120-300. HARD-FAIL: d_eff > 300 (DT-framework cells need reassessment).
FORMULA SELF-TESTS (PROT-022): 1. participation ratio of identity-spectrum == n. 2. rank of rank-1 matrix small. 3. encode.
ASCII-only. write_metrics. PROT-018: no _nN.
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
import numpy as np
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "effective_rank_svd_v1"
MINILM_ID = "sentence-transformers/all-MiniLM-L6-v2"
MEDQA = REPO / "data" / "datasets" / "medqa_usmle_500.jsonl"; PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_ENC = 2000 if RUN_MODE == "smoke" else 8000


def participation_ratio(s):
    s2 = s ** 2; return float((s2.sum() ** 2) / (np.sum(s2 ** 2) + 1e-12))


def var_rank(s, frac):
    v = (s ** 2); v = v / v.sum(); c = np.cumsum(v); return int(np.searchsorted(c, frac) + 1)


def _selftest():
    s = np.ones(50); assert abs(participation_ratio(s) - 50) < 1e-6, "PR of flat spectrum == n"
    s2 = np.array([10.0] + [1e-6] * 49); assert participation_ratio(s2) < 2, "PR of rank-1 small"
    print("[selftest] PASS: participation ratio", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps missing: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[dev] %s" % DEV, flush=True)


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
    tok = AutoTokenizer.from_pretrained(MINILM_ID); m = AutoModel.from_pretrained(MINILM_ID).to(DEV).eval(); out = []
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=96).to(DEV)
        with torch.no_grad():
            h = m(**t).last_hidden_state
        mask = t["attention_mask"].unsqueeze(-1).float(); out.append(((h * mask).sum(1) / mask.sum(1).clamp(min=1)).cpu().numpy())
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    return np.concatenate(out, 0).astype(np.float32)


def verdict(d_eff, r90, r99, D) -> Tuple[str, str]:
    summary = "d_eff(participation_ratio)=%.1f  rank90=%d  rank99=%d  (nominal D=%d)" % (d_eff, r90, r99, D)
    if d_eff <= 120:
        return ("HARD_PASS", "HARD_PASS: encoder is intrinsic-dim-limited (d_eff<=120) -- validates DT/intrinsic-dim framework; real-encoder substrate capacity bounded by d_eff not nominal D. " + summary)
    if d_eff <= 300:
        return ("MIDDLE_BAND", "MIDDLE_BAND: d_eff 120-300. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: d_eff>300 -- intrinsic-dim framework does NOT hold; DT-framework cells need reassessment. " + summary)


print("[config] anchor=%s mode=%s N_enc=%d" % (ANCHOR_NAME, RUN_MODE, N_ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time()
emb = encode(load_texts(N_ENC)); X = emb - emb.mean(0)
s = np.linalg.svd(X, compute_uv=False)
d_eff = participation_ratio(s); r90 = var_rank(s, 0.90); r99 = var_rank(s, 0.99)
v, vmsg = verdict(d_eff, r90, r99, emb.shape[1]); print("[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1,
           "per_seed": [{"d_eff": d_eff, "rank90": r90, "rank99": r99, "D": int(emb.shape[1]), "n_enc": int(emb.shape[0])}],
           "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, metrics["per_seed"]); print("[metrics] written", flush=True)
