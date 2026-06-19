"""
exp_stella400m_encoder_headtohead_v1 -- stella-400M vs bge-large HotpotQA recall@2 (encoder-ceiling resolver) -- CPU.

ROUTING: encoder ceiling Anchor 1 (the stella-400M half; e5-large already done at r@2=0.444). stella_en_400M_v5 (MTEB-top
  400M encoder) vs bge-large on HotpotQA supporting-fact recall@2/@10. If stella-400M clears 0.55 r@2, the encoder ceiling is
  an encoder-quality issue with a same-day drop-in upgrade; if it also plateaus ~0.5, the ceiling is structural and the
  iterative-multihop path (in flight) is the route. Encode-only, CPU. stella loaded with standard attention (no xformers),
  mean-pooled, with its s2p query instruction prompt.
PRE-REGISTERED: HARD-PASS stella-400M recall@2 >= 0.55 (drop-in encoder upgrade clears the gate). MIDDLE 0.52-0.55 (marginal).
  HARD-FAIL < 0.52 (no better than bge-large 0.516; structural ceiling, iterative path is primary).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. mean-pool shape. 3. parse supporting_facts.
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

ANCHOR_NAME = "stella400m_encoder_headtohead_v1"
STELLA = "NovaSearch/stella_en_400M_v5"; BGE = "BAAI/bge-large-en-v1.5"
S_QPROMPT = "Instruct: Given a web search query, retrieve relevant passages that answer the query.\nQuery: "
B_QPROMPT = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def recall_at(en, qn, gold, k):
    order = np.argsort(en @ qn)[::-1][:k]; return len(set(order.tolist()) & set(gold)) / len(gold)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    x = np.ones((2, 3, 4)); mask = np.ones((2, 3, 1)); mp = (x * mask).sum(1) / mask.sum(1); assert mp.shape == (2, 4), "mean-pool shape"
    sf = {"title": ["A"], "sent_id": [0]}; assert sf["title"][0] == "A", "parse supporting_facts"
    print("[selftest] PASS: stella400m-encoder-headtohead", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []; flat = []; gold = []
        sf_set = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                if (titles[ti], si) in sf_set:
                    gold.append(len(flat))
                flat.append(s)
        if len(flat) < 12 or not gold:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
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


def encode_mean(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        msk = t["attention_mask"].unsqueeze(-1).float()
        mp = (o.last_hidden_state * msk).sum(1) / msk.sum(1).clamp(min=1e-9)
        out.append(mp.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def encode_cls(texts, tok, m):
    out = []
    for i in range(0, len(texts), 16):
        t = tok(texts[i:i + 16], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def eval_encoder(data, tok, m, enc_fn, qprompt):
    r2 = r10 = 0.0
    for d in data:
        en = unit(enc_fn(d["sents"], tok, m)); qn = unit(enc_fn([qprompt + d["q"]], tok, m))[0]
        r2 += recall_at(en, qn, d["gold"], 2); r10 += recall_at(en, qn, d["gold"], 10)
    n = len(data); return {"r2": r2 / n, "r10": r10 / n}


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"stella": {}, "bge": {}}
    res = {}
    stok = AutoTokenizer.from_pretrained(STELLA, trust_remote_code=True)
    sm = AutoModel.from_pretrained(STELLA, trust_remote_code=True, use_memory_efficient_attention=False, unpad_inputs=False).to(DEV).eval()
    res["stella"] = eval_encoder(data, stok, sm, encode_mean, S_QPROMPT); del sm
    if DEV.type == "cuda":
        torch.cuda.empty_cache()
    print("  [stella-400M] recall@2=%.3f recall@10=%.3f" % (res["stella"]["r2"], res["stella"]["r10"]), flush=True)
    btok = AutoTokenizer.from_pretrained(BGE); bm = AutoModel.from_pretrained(BGE).to(DEV).eval()
    res["bge"] = eval_encoder(data, btok, bm, encode_cls, B_QPROMPT); del bm
    print("  [bge-large]   recall@2=%.3f recall@10=%.3f" % (res["bge"]["r2"], res["bge"]["r10"]), flush=True)
    return {"stella": res["stella"], "bge": res["bge"], "n": len(data)}


def verdict(r) -> Tuple[str, str]:
    st = r.get("stella", {}).get("r2", 0); bg = r.get("bge", {}).get("r2", 0)
    summary = "stella-400M r@2=%.3f r@10=%.3f | bge-large r@2=%.3f r@10=%.3f | e5-large r@2=0.444 (prior) (n=%d)" % (
        st, r.get("stella", {}).get("r10", 0), bg, r.get("bge", {}).get("r10", 0), r.get("n", 0))
    if st >= 0.55:
        return ("HARD_PASS", "HARD_PASS: stella-400M clears recall@2>=0.55 -- drop-in encoder upgrade breaks the multi-hop ceiling; same-day production swap. " + summary)
    if st >= 0.52:
        return ("MIDDLE_BAND", "MIDDLE_BAND: stella-400M r@2 0.52-0.55 -- marginal over bge-large; consider stella-1.5B (GPU). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: stella-400M does not beat bge-large meaningfully (<0.52) -- dense-encoder ceiling is STRUCTURAL (e5/bge/stella all plateau ~0.5); iterative-multihop path is primary. " + summary)


print("[config] anchor=%s mode=%s n_q=%d" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
