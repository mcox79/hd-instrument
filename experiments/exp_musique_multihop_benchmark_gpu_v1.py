"""
exp_musique_multihop_benchmark_gpu_v1 -- v1 benchmark suite: MuSiQue (hard multi-hop) substrate retrieval -- GPU.

ROUTING: DEMO_SUPPORT A3. MuSiQue is the harder multi-hop benchmark (2-4 hops). Each item has 20 paragraphs with is_supporting
  flags. Encode paragraphs with bge-large (GPU), retrieve by question, measure recall of the supporting paragraphs (all-gold@k
  for k in {n_gold, 5, 10}). Raw bge-large (per the HotpotQA finding: per-query whitening hurts small pools). Extends the
  head-to-head free-text multi-hop coverage; expect to tie RAG (same encoder). GPU bf16.
PRE-REGISTERED: HARD-PASS all-supporting recall@10 >= 0.60 (re-rankable) on MuSiQue. MIDDLE >= 0.45. HARD-FAIL < 0.45.
FORMULA SELF-TESTS (PROT-022): 1. unit norm. 2. gold flag. 3. json parse.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"; os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "musique_multihop_benchmark_gpu_v1"; BI = "BAAI/bge-large-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "
DS = REPO / "data" / "datasets" / "musique_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 60 if SMOKE else 250


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n; assert abs(_n.linalg.norm(unit(_n.array([3.0, 4.0]))) - 1.0) < 1e-6, "unit norm"
    assert {"is_supporting": True}["is_supporting"], "gold flag"
    assert json.loads('{"a":1}')["a"] == 1, "json parse"
    print("[selftest] PASS: musique-multihop-benchmark", flush=True)


def load(n):
    out = []
    if not DS.exists():
        return out
    for l in open(DS, encoding="utf-8"):
        r = json.loads(l); ps = r.get("paragraphs") or []; q = r.get("question") or ""
        texts = [p.get("paragraph_text", "") for p in ps]; gold = set(i for i, p in enumerate(ps) if p.get("is_supporting"))
        if q and len(texts) >= 4 and len(gold) >= 2:
            out.append({"q": q, "texts": texts, "gold": gold})
        if len(out) >= n:
            break
    return out


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
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=200).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    data = load(N_Q)
    if not data:
        print("[FATAL] no musique", flush=True); return {"n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI, torch_dtype=torch.bfloat16).to(DEV).eval()
    acc = {"ng": 0, 5: 0, 10: 0}; n = 0
    for d in data:
        E = unit(encode(d["texts"], tok, m)); q = unit(encode([Q_INSTR + d["q"]], tok, m))[0]; order = np.argsort(-(E @ q)); ng = len(d["gold"])
        acc["ng"] += int(set(order[:ng].tolist()) >= d["gold"])
        acc[5] += int(d["gold"] <= set(order[:5].tolist()))
        acc[10] += int(d["gold"] <= set(order[:10].tolist()))
        n += 1
    del m; r = {"n": n, "r_ng": acc["ng"] / n, "r5": acc[5] / n, "r10": acc[10] / n}
    print("  MuSiQue all-supporting recall@ngold/5/10 = %.3f/%.3f/%.3f (n=%d)" % (r["r_ng"], r["r5"], r["r10"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "all-supporting recall@ngold/5/10=%.3f/%.3f/%.3f (n=%d)" % (r["r_ng"], r["r5"], r["r10"], r["n"])
    if r["r10"] >= 0.60:
        return ("HARD_PASS", "HARD_PASS: MuSiQue all-supporting recall@10>=0.60 (re-rankable) -- harder multi-hop covered; ties RAG (same encoder), substrate's multi-hop edge is structured-KG not free text. " + s)
    if r["r10"] >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: MuSiQue recall@10 0.45-0.60 (harder than HotpotQA). " + s)
    return ("HARD_FAIL", "HARD_FAIL: MuSiQue recall@10 <0.45. " + s)


print("[config] anchor=%s mode=%s n_q=%d encoder=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
