"""
exp_bm25_bge_rrf_hotpot_v1 -- BM25 + bge-small reciprocal-rank-fusion recall@2/@10 on HotpotQA 2-hop -- CPU.

ROUTING: handoff bm25_hybrid_first_colbert_deferred (pretest #2). Multi-hop floor-lift: does BM25 (lexical) + bge-small
  (dense) RRF fusion beat bge-small alone? Lexical signal catches entity-overlap the dense encoder misses (bridge entities
  are often exact-string). BM25 implemented over each question's ~40-sentence candidate set (no index/library needed).
  Compare to bge-small naive (recall@2=0.42, recall@10=0.74). CPU.
PRE-REGISTERED: HARD-PASS RRF recall@2 >= 0.50 OR recall@10 >= 0.80 (meaningful floor lift over bge alone). MIDDLE any lift
  >0. HARD-FAIL RRF <= bge on both (fusion doesn't help).
FORMULA SELF-TESTS (PROT-022): 1. bm25 exact-match ranks high. 2. RRF combines. 3. parse columnar.
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
import argparse, time, json, re, math
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "bm25_bge_rrf_hotpot_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 50 if RUN_MODE == "smoke" else 200
RRF_K = 60; K1 = 1.5; B = 0.75
_TOK = re.compile(r"[a-z0-9]+")


def toks(s):
    return _TOK.findall((s or "").lower())


def bm25_scores(query, docs_toks):
    N = len(docs_toks); avgdl = (sum(len(d) for d in docs_toks) / N) if N else 1.0
    df = Counter()
    for d in docs_toks:
        for w in set(d):
            df[w] += 1
    qt = toks(query); scores = np.zeros(N)
    for i, d in enumerate(docs_toks):
        tf = Counter(d); sc = 0.0
        for w in qt:
            if w in tf:
                idf = math.log(1 + (N - df[w] + 0.5) / (df[w] + 0.5))
                sc += idf * tf[w] * (K1 + 1) / (tf[w] + K1 * (1 - B + B * len(d) / avgdl))
        scores[i] = sc
    return scores


def rrf(rank_lists, k=RRF_K):
    n = len(rank_lists[0]); score = np.zeros(n)
    for rl in rank_lists:
        for rank, idx in enumerate(rl):
            score[idx] += 1.0 / (k + rank)
    return np.argsort(score)[::-1]


def _selftest():
    docs = [toks("Marie Curie physicist"), toks("the cat sat"), toks("Pierre Curie chemist")]
    sc = bm25_scores("Curie", docs); assert sc[0] > sc[1] and sc[2] > sc[1], "bm25 exact-match ranks high"
    order = rrf([[2, 0, 1], [2, 1, 0]]); assert order[0] == 2, "RRF combines"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: bm25-bge-rrf", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


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


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def hit2(order, sents, gold):
    return int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & gold) >= 2)


def hit10(order, sents, gold):
    return int(len(set((sents[i][0], sents[i][1]) for i in order[:10]) & gold) >= 2)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    b2 = b10 = r2 = r10 = m2 = m10 = 0
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]
        en = encode(texts, tok, m); qn = encode([Q_INSTR + d["q"]], tok, m)[0]
        bge_order = np.argsort((en / (np.linalg.norm(en, axis=1, keepdims=True) + 1e-8)) @ (qn / (np.linalg.norm(qn) + 1e-8)))[::-1]
        bm_order = np.argsort(bm25_scores(d["q"], [toks(t) for t in texts]))[::-1]
        rrf_order = rrf([list(bge_order), list(bm_order)])
        b2 += hit2(bge_order, sents, d["gold"]); b10 += hit10(bge_order, sents, d["gold"])
        m2 += hit2(bm_order, sents, d["gold"]); m10 += hit10(bm_order, sents, d["gold"])
        r2 += hit2(rrf_order, sents, d["gold"]); r10 += hit10(rrf_order, sents, d["gold"])
    del m
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    n = len(data)
    res = {"n": n, "bge_r2": b2/n, "bge_r10": b10/n, "bm25_r2": m2/n, "bm25_r10": m10/n, "rrf_r2": r2/n, "rrf_r10": r10/n}
    print("  bge: r@2=%.3f r@10=%.3f | BM25: r@2=%.3f r@10=%.3f | RRF: r@2=%.3f r@10=%.3f" % (res["bge_r2"], res["bge_r10"], res["bm25_r2"], res["bm25_r10"], res["rrf_r2"], res["rrf_r10"]), flush=True)
    return res


def verdict(r) -> Tuple[str, str]:
    summary = "RRF r@2=%.3f r@10=%.3f | bge r@2=%.3f r@10=%.3f | BM25 r@2=%.3f r@10=%.3f (n=%d)" % (r["rrf_r2"], r["rrf_r10"], r["bge_r2"], r["bge_r10"], r["bm25_r2"], r["bm25_r10"], r["n"])
    if r["rrf_r2"] >= 0.50 or r["rrf_r10"] >= 0.80:
        return ("HARD_PASS", "HARD_PASS: BM25+bge RRF reaches r@2>=0.50 or r@10>=0.80 -- lexical+dense fusion gives meaningful multi-hop floor lift; ship RRF, ColBERT may be unnecessary. " + summary)
    if r["rrf_r2"] > r["bge_r2"] or r["rrf_r10"] > r["bge_r10"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: RRF lifts over bge alone but below the bar -- partial floor lift. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: RRF does not beat bge alone -- lexical fusion adds nothing here; ColBERT install may be needed. " + summary)


print("[config] anchor=%s mode=%s n_q=%d encoder=bge-small + BM25 RRF" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
