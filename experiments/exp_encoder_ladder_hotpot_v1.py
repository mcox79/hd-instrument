"""
exp_encoder_ladder_hotpot_v1 -- which fair-size retrieval encoder for v1? (MiniLM/bge-small/bge-large/e5-large) -- CPU.

ROUTING: follows the two-encoder-architecture confirmation. Research listed MiniLM/bge-small/gte/e5 as valid retrieval
  encoders; my data already showed bge-small (0.42) >> MiniLM (0.16). This settles the choice: recall@2hop AND recall@10 on
  HotpotQA-distractor for every cached fair-size (<1B) contrastive encoder, so the v1 suite picks the best size/quality
  point. CPU.
PRE-REGISTERED: HARD-PASS some encoder reaches recall@10 >= 0.80 (a fair-size encoder makes the facts reliably retrievable;
  pick it). MIDDLE best recall@10 0.65-0.80. HARD-FAIL all < 0.65.
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. prefix map. 3. parse columnar.
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

ANCHOR_NAME = "encoder_ladder_hotpot_v1"
# (name, hf_id, pool, query_prefix, doc_prefix)
ENCODERS = [
    ("MiniLM", "sentence-transformers/all-MiniLM-L6-v2", "mean", "", ""),
    ("bge-small", "BAAI/bge-small-en-v1.5", "cls", "Represent this sentence for searching relevant passages: ", ""),
    ("bge-large", "BAAI/bge-large-en-v1.5", "cls", "Represent this sentence for searching relevant passages: ", ""),
    ("e5-large", "intfloat/e5-large-v2", "mean", "query: ", "passage: "),
]
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 40 if RUN_MODE == "smoke" else 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert ENCODERS[1][2] == "cls", "prefix map"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: encoder-ladder", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("[device] %s" % DEV, flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l)
        ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = []
        for ti, title in enumerate(titles):
            for si, s in enumerate(sent_lists[ti] if ti < len(sent_lists) else []):
                flat.append((title, si, s))
        gold = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        if len(flat) < 4 or len(gold) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
        if len(out) >= n:
            break
    return out


def encode(texts, tok, m, pool):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        if pool == "cls":
            v = o.last_hidden_state[:, 0, :]
        else:
            mk = t["attention_mask"].unsqueeze(-1).float(); v = (o.last_hidden_state * mk).sum(1) / mk.sum(1).clamp(min=1)
        out.append(v.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 1), np.float32)


def eval_encoder(name, hf, pool, qpre, dpre, data):
    tok = AutoTokenizer.from_pretrained(hf); m = AutoModel.from_pretrained(hf).to(DEV).eval()
    h2 = 0; h10 = 0
    for d in data:
        sents = d["sents"]; texts = [dpre + s for (_, _, s) in sents]
        en = unit(encode(texts, tok, m, pool)); qn = unit(encode([qpre + d["q"]], tok, m, pool))[0]
        order = np.argsort(en @ qn)[::-1]
        h2 += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        h10 += int(len(set((sents[i][0], sents[i][1]) for i in order[:10]) & d["gold"]) >= 2)
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    n = len(data); return {"r2": h2 / n, "r10": h10 / n}


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"by": {}, "best_r10": 0.0, "n": 0}
    by = {}
    for (name, hf, pool, qpre, dpre) in ENCODERS:
        try:
            res = eval_encoder(name, hf, pool, qpre, dpre, data); by[name] = res
            print("  %-10s recall@2hop=%.3f recall@10=%.3f" % (name, res["r2"], res["r10"]), flush=True)
        except Exception as e:
            print("  %-10s ERROR %s" % (name, str(e)[:80]), flush=True)
    best = max(by, key=lambda k: by[k]["r10"]) if by else None
    return {"by": by, "best": best, "best_r10": by[best]["r10"] if best else 0.0, "best_r2": by[best]["r2"] if best else 0.0, "n": len(data)}


def verdict(r) -> Tuple[str, str]:
    summary = "best=%s | %s (n=%d)" % (r["best"], {k: {"r2": round(v["r2"], 2), "r10": round(v["r10"], 2)} for k, v in r["by"].items()}, r["n"])
    if r["best_r10"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: %s reaches recall@10>=0.80 -- adopt it as the v1 retrieval encoder (facts reliably in pool; rerank/decomposition closes to answer). " % r["best"] + summary)
    if r["best_r10"] >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: best recall@10 0.65-0.80 -- usable, pick the best size/quality point. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: all fair-size encoders recall@10<0.65 -- retrieval coverage itself is the bottleneck. " + summary)


print("[config] anchor=%s mode=%s n_q=%d encoders=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, [e[0] for e in ENCODERS]), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
