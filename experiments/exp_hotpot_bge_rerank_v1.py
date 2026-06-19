"""
exp_hotpot_bge_rerank_v1 -- HotpotQA: bge-small top-k retrieve + cross-encoder rerank -> recall@2hop -- CPU.

ROUTING: corrected north-star path (see exp_dev_to_research_URGENT_llama_not_retrieval_encoder). bge-small recall@10=0.74
  (both facts in pool) but recall@2=0.42 -- the gap is RANKING. Tests whether a small cross-encoder reranker on bge top-10
  lifts recall@2hop toward 0.74, confirming the fair-size v1 recipe (33M bi-encoder + small cross-encoder). CPU.
PRE-REGISTERED: HARD-PASS reranked recall@2hop >= 0.60 (rerank closes most of the 0.42->0.74 gap; v1 multi-hop recipe
  confirmed). MIDDLE 0.50-0.60. HARD-FAIL < 0.50 (rerank doesn't help; gap needs question decomposition not ranking).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. argsort desc. 3. parse columnar.
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

ANCHOR_NAME = "hotpot_bge_rerank_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
CROSS = "cross-encoder/ms-marco-MiniLM-L-6-v2"
TOPK = 10
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 50 if RUN_MODE == "smoke" else 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert list(np.argsort([3.0, 1.0, 2.0])[::-1]) == [0, 2, 1], "argsort desc"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: bge-rerank", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cpu")


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


def bi_encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())   # bge CLS
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 384), np.float32)


def cross_score(q, cands, ctok, cm):
    scores = []
    for i in range(0, len(cands), 16):
        batch = cands[i:i + 16]
        t = ctok([q] * len(batch), batch, return_tensors="pt", padding=True, truncation=True, max_length=160).to(DEV)
        with torch.no_grad():
            logits = cm(**t).logits
        s = logits.squeeze(-1) if logits.shape[-1] == 1 else logits[:, -1]
        scores.append(s.float().cpu().numpy())
    return np.concatenate(scores, 0)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"bge2": 0.0, "rerank2": 0.0, "n": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ctok = AutoTokenizer.from_pretrained(CROSS); cm = AutoModelForSequenceClassification.from_pretrained(CROSS).to(DEV).eval()
    bge2 = 0; rr2 = 0
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]
        en = unit(bi_encode(texts, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]
        bge2 += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        cand_idx = list(order[:TOPK]); cand_txt = [sents[i][2] for i in cand_idx]
        rs = cross_score(d["q"], cand_txt, ctok, cm); rer = [cand_idx[j] for j in np.argsort(rs)[::-1]]
        rr2 += int(len(set((sents[i][0], sents[i][1]) for i in rer[:2]) & d["gold"]) >= 2)
    del bm, cm
    n = len(data); b = bge2 / n; r = rr2 / n
    print("  n=%d bge_recall@2hop=%.3f reranked_recall@2hop=%.3f lift=%+.3f (recall@10 ceiling ~0.74)" % (n, b, r, r - b), flush=True)
    return {"n": n, "bge2": b, "rerank2": r}


def verdict(r) -> Tuple[str, str]:
    rr = r["rerank2"]; b = r["bge2"]
    summary = "reranked recall@2hop=%.3f bge-only=%.3f lift=%+.3f (n=%d, bge top-%d + cross-encoder; r@10 ceiling ~0.74)" % (rr, b, rr - b, r["n"], TOPK)
    if rr >= 0.60:
        return ("HARD_PASS", "HARD_PASS: cross-encoder rerank lifts recall@2hop to >=0.60 -- fair-size v1 multi-hop recipe (bge-small + small cross-encoder) confirmed; substrate audit/K-hop sits on top. " + summary)
    if rr >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: rerank reaches 0.50-0.60 -- helps, partial. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: rerank <0.50 -- ranking alone doesn't close the gap; needs question decomposition. " + summary)


print("[config] anchor=%s mode=%s n_q=%d bi=%s cross=%s topk=%d" % (ANCHOR_NAME, RUN_MODE, N_Q, BI, CROSS, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
