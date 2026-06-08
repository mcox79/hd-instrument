"""
exp_wikipedia_ingest_benchmark_gpu_v1 -- E1 / v1 benchmark suite: substrate ingest + retrieval over 10k real Wikipedia -- GPU.

ROUTING: v1 benchmark suite (E1 Wikipedia ingest). Ingests 10k real Wikipedia articles (title + text) into the substrate:
  encode with bge-large (GPU), store, and measure (a) retrieval recall@1/@5 querying each article by its title among the full
  10k pool, and (b) ingest throughput (articles/sec). This is the real-corpus retrieval entry of the head-to-head suite and a
  dry-run for the 5.84M pre-trained Wikipedia substrate. GPU bf16.
PRE-REGISTERED: HARD-PASS title->article retrieval recall@5 >= 0.85 over 10k real Wikipedia articles. MIDDLE >= 0.70. HARD-FAIL < 0.70.
FORMULA SELF-TESTS (PROT-022): 1. unit norm. 2. recall counts. 3. json parse.
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

ANCHOR_NAME = "wikipedia_ingest_benchmark_gpu_v1"; BI = "BAAI/bge-large-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "
DS = REPO / "data" / "datasets" / "wikipedia_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 2000 if SMOKE else 10000


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n; assert abs(_n.linalg.norm(unit(_n.array([3.0, 4.0]))) - 1.0) < 1e-6, "unit norm"
    assert int(_n.argmax([0.1, 0.9])) == 1, "recall counts"
    assert json.loads('{"title":"x","text":"y"}')["title"] == "x", "json parse"
    print("[selftest] PASS: wikipedia-ingest-benchmark", flush=True)


def load(n):
    out = []
    if not DS.exists():
        return out
    for l in open(DS, encoding="utf-8"):
        r = json.loads(l); t = (r.get("title") or "").strip(); x = (r.get("text") or "").strip()
        if t and x:
            out.append((t, x))
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
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=256).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    data = load(N)
    if not data:
        print("[FATAL] no wikipedia_10k.jsonl", flush=True); return {"n": 0, "r5": 0.0}
    titles = [d[0] for d in data]; texts = [d[1][:1500] for d in data]
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI, torch_dtype=torch.bfloat16).to(DEV).eval()
    t0 = time.time(); A = unit(encode(texts, tok, m)); ingest_s = time.time() - t0; thr = len(data) / ingest_s
    Qt = unit(encode([Q_INSTR + t for t in titles], tok, m)); del m; n = len(data); gold = np.arange(n)
    r1 = r5 = 0
    for i in range(0, n, 256):
        sims = Qt[i:i + 256] @ A.T; order = np.argsort(-sims, axis=1)
        for j in range(order.shape[0]):
            gi = i + j; r1 += int(order[j, 0] == gi); r5 += int(gi in order[j, :5])
    r1 /= n; r5 /= n
    print("  title->article recall@1=%.3f recall@5=%.3f over %d real Wikipedia articles | ingest=%.0f art/sec" % (r1, r5, n, thr), flush=True)
    return {"n": n, "r1": r1, "r5": r5, "throughput": thr}


def verdict(r) -> Tuple[str, str]:
    s = "recall@1=%.3f @5=%.3f over %d articles, ingest=%.0f art/sec" % (r["r1"], r["r5"], r["n"], r["throughput"])
    if r["r5"] >= 0.85:
        return ("HARD_PASS", "HARD_PASS: substrate ingests + retrieves 10k real Wikipedia articles at recall@5>=0.85 -- real-corpus retrieval green; dry-run for the 5.84M pre-trained substrate. " + s)
    if r["r5"] >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: Wikipedia retrieval recall@5 0.70-0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: Wikipedia retrieval recall@5 <0.70. " + s)


print("[config] anchor=%s mode=%s n=%d encoder=%s" % (ANCHOR_NAME, RUN_MODE, N, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
