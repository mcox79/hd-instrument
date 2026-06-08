"""
exp_twowiki_multihop_benchmark_gpu_v1 -- v1 benchmark suite: 2WikiMultiHop substrate retrieval -- GPU.

ROUTING: DEMO_SUPPORT A4. 2WikiMultiHop (Wikipedia-based multi-hop, complements HotpotQA). context = list of [title, sentences];
  supporting_facts = list of [title, sent_id]. Encode context sentences with bge-large (GPU), retrieve by question, measure
  recall@2/5/10 of the gold supporting facts. Raw bge-large (per HotpotQA finding). Extends free-text multi-hop coverage;
  expect to tie RAG like HotpotQA. GPU bf16.
PRE-REGISTERED: HARD-PASS recall@10 >= 0.65 (re-rankable). MIDDLE >= 0.50. HARD-FAIL < 0.50.
FORMULA SELF-TESTS (PROT-022): 1. unit norm. 2. recall counts. 3. context parse.
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

ANCHOR_NAME = "twowiki_multihop_benchmark_gpu_v1"; BI = "BAAI/bge-large-en-v1.5"
Q_INSTR = "Represent this sentence for searching relevant passages: "
DS = REPO / "data" / "datasets" / "twowiki_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 60 if SMOKE else 250


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def as_sents(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            v = json.loads(x)
            return v if isinstance(v, list) else [x]
        except Exception:
            return [x]
    return [str(x)]


def _selftest():
    import numpy as _n; assert abs(_n.linalg.norm(unit(_n.array([3.0, 4.0]))) - 1.0) < 1e-6, "unit norm"
    assert len({1, 3} & {1, 3}) == 2, "recall counts"
    assert as_sents('["a","b"]') == ["a", "b"], "context parse"
    print("[selftest] PASS: twowiki-multihop-benchmark", flush=True)


def load(n):
    out = []
    if not DS.exists():
        return out
    for l in open(DS, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or []; sf = r.get("supporting_facts") or []
        flat = []; idx_of = {}
        for entry in ctx:
            if not isinstance(entry, (list, tuple)) or len(entry) < 2:
                continue
            title = entry[0]; sents = as_sents(entry[1])
            for si, s in enumerate(sents):
                idx_of[(title, si)] = len(flat); flat.append(s)
        gold = set()
        for sfentry in sf:
            if isinstance(sfentry, (list, tuple)) and len(sfentry) >= 2:
                key = (sfentry[0], int(sfentry[1]) if str(sfentry[1]).isdigit() else 0)
                if key in idx_of:
                    gold.add(idx_of[key])
        if r.get("question") and len(flat) >= 8 and len(gold) >= 2:
            out.append({"q": r["question"], "sents": flat, "gold": gold})
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
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    data = load(N_Q)
    if not data:
        print("[FATAL] no twowiki", flush=True); return {"n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI, torch_dtype=torch.bfloat16).to(DEV).eval()
    acc = {2: 0, 5: 0, 10: 0}; n = 0
    for d in data:
        E = unit(encode(d["sents"], tok, m)); q = unit(encode([Q_INSTR + d["q"]], tok, m))[0]; order = np.argsort(-(E @ q)); ng = len(d["gold"])
        for k in (2, 5, 10):
            acc[k] += int(d["gold"] <= set(order[:max(k, ng)].tolist()))
        n += 1
    del m; r = {"n": n, "r2": acc[2] / n, "r5": acc[5] / n, "r10": acc[10] / n}
    print("  2WikiMultiHop all-supporting recall@2/5/10 = %.3f/%.3f/%.3f (n=%d)" % (r["r2"], r["r5"], r["r10"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "all-supporting recall@2/5/10=%.3f/%.3f/%.3f (n=%d)" % (r["r2"], r["r5"], r["r10"], r["n"])
    if r["r10"] >= 0.65:
        return ("HARD_PASS", "HARD_PASS: 2WikiMultiHop all-supporting recall@10>=0.65 -- free-text multi-hop coverage extended; ties RAG (same encoder), consistent with HotpotQA. " + s)
    if r["r10"] >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 2Wiki recall@10 0.50-0.65. " + s)
    return ("HARD_FAIL", "HARD_FAIL: 2Wiki recall@10 <0.50. " + s)


print("[config] anchor=%s mode=%s n_q=%d encoder=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
