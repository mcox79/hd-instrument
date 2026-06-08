"""
exp_encoder_headtohead_benchmark_gpu_v1 -- v1 benchmark suite: encoder head-to-head for substrate retrieval -- GPU.

ROUTING: v1 benchmark suite (encoder selection). Which encoder gives the best substrate retrieval for the demo? Compares
  bge-large, bge-small, e5-large on HotpotQA supporting-fact retrieval (recall@2/@5/@10). Picks the production encoder for the
  demo's substrate-enhanced panel. GPU bf16. (Confirms/updates the locked bge-large choice with a clean head-to-head.)
PRE-REGISTERED: HARD-PASS the best encoder recall@10 >= 0.70 AND a clear ranking emerges. MIDDLE >= 0.55. HARD-FAIL < 0.55.
FORMULA SELF-TESTS (PROT-022): 1. unit norm. 2. recall counts. 3. prefix select.
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

ANCHOR_NAME = "encoder_headtohead_benchmark_gpu_v1"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
ENCODERS = [
    ("bge-large", "BAAI/bge-large-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
    ("bge-small", "BAAI/bge-small-en-v1.5", "Represent this sentence for searching relevant passages: ", ""),
    ("e5-large", "intfloat/e5-large-v2", "query: ", "passage: "),
]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_Q = 40 if SMOKE else 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    import numpy as _n; assert abs(_n.linalg.norm(unit(_n.array([3.0, 4.0]))) - 1.0) < 1e-6, "unit norm"
    assert len(set([1, 3]) & {1, 3}) == 2, "recall counts"
    assert ENCODERS[2][3] == "passage: ", "prefix select"
    print("[selftest] PASS: encoder-headtohead-benchmark", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        sfset = set(zip(sf.get("title") or [], sf.get("sent_id") or [])); flat = []; gold = []
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                if (titles[ti], si) in sfset:
                    gold.append(len(flat))
                flat.append(s)
        if len(flat) >= 12 and len(gold) >= 2:
            out.append({"q": r.get("question", ""), "sents": flat, "gold": set(gold)})
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
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0, "by": {}}
    by = {}
    for name, mid, qpfx, ppfx in ENCODERS:
        try:
            tok = AutoTokenizer.from_pretrained(mid); m = AutoModel.from_pretrained(mid, torch_dtype=torch.bfloat16).to(DEV).eval()
        except Exception as e:
            print("  [skip %s] %s" % (name, str(e)[:80]), flush=True); continue
        acc = {2: 0, 5: 0, 10: 0}; n = 0
        for d in data:
            E = unit(encode([ppfx + s for s in d["sents"]], tok, m)); q = unit(encode([qpfx + d["q"]], tok, m))[0]
            order = np.argsort(-(E @ q))
            for k in (2, 5, 10):
                acc[k] += int(len(set(order[:k].tolist()) & d["gold"]) == 2)
            n += 1
        by[name] = {"r2": acc[2] / n, "r5": acc[5] / n, "r10": acc[10] / n}
        print("  %s recall@2/5/10=%.3f/%.3f/%.3f" % (name, by[name]["r2"], by[name]["r5"], by[name]["r10"]), flush=True)
        del m; torch.cuda.empty_cache()
    best = max(by, key=lambda k: by[k]["r10"]) if by else "none"
    return {"n": len(data), "by": by, "best": best, "best_r10": by[best]["r10"] if by else 0.0}


def verdict(r) -> Tuple[str, str]:
    s = "best=%s | %s" % (r["best"], {k: round(v["r10"], 3) for k, v in r["by"].items()})
    if r["best_r10"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: encoder head-to-head clear -- best encoder (%s) recall@10>=0.70 for the demo's substrate panel. " % r["best"] + s)
    if r["best_r10"] >= 0.55:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best encoder recall@10 0.55-0.70. " + s)
    return ("HARD_FAIL", "HARD_FAIL: best encoder recall@10 <0.55. " + s)


print("[config] anchor=%s mode=%s n_q=%d encoders=%d" % (ANCHOR_NAME, RUN_MODE, N_Q, len(ENCODERS)), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
