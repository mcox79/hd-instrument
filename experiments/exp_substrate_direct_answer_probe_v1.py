"""
exp_substrate_direct_answer_probe_v1 -- BUNDLED LLM-bypass fast-path probe (direct-answer fraction + threshold router) -- CPU.

ROUTING: inference_acceleration_alternatives Anchor 1 + Anchor 2 (spec-dec HARD_FAILed; this is the high-leverage path:
  bypass LLM generation for queries answerable directly from retrieval). On HotpotQA, retrieve top-1 sentence per query with
  bge-small (CPU); measure top-1 F1 vs gold answer + containment.
  A1 DIRECT-ANSWER FRACTION: fraction of queries with top-1 F1 >= 0.50 (a fast-path that skips the LLM ~50ms vs 1.23s).
  A2 THRESHOLD ROUTER: sweep top-1 similarity threshold; precision of predicting "answerable" (F1>=0.50) -- a zero-training
     production gate for routing to the fast path. CPU, encode-only.
PRE-REGISTERED: A1 HARD-PASS >= 30% of queries top-1 F1 >= 0.50; HARD-FAIL < 15% OR median top-1 F1 on answerable < 0.20.
  A2 HARD-PASS precision >= 0.80 at some threshold (coverage >= 10%). Bundle verdict: HARD_PASS if A1 passes (router is the
  bonus); MIDDLE if A1 in [15%,30%) or only A2 passes; HARD-FAIL if A1 < 15%.
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. containment. 3. self-retrieval.
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
import argparse, time, json, re, string
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_direct_answer_probe_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 40 if RUN_MODE == "smoke" else 400


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1_score(pred, gold):
    p = norm_ans(pred).split(); g = norm_ans(gold).split()
    if not p or not g:
        return float(p == g)
    nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
    if nc == 0:
        return 0.0
    pr = nc / len(p); rc = nc / len(g); return 2 * pr * rc / (pr + rc)


def contains(sentence, gold):
    return norm_ans(gold) in norm_ans(sentence)


def _selftest():
    assert abs(f1_score("bathroom", "bathroom") - 1.0) < 1e-6, "F1 identical=1"
    assert contains("Mary went to the bathroom", "bathroom") and not contains("kitchen", "bathroom"), "containment"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    print("[selftest] PASS: substrate-direct-answer-probe", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        flat = [s for ti in range(len(titles)) for s in (sl[ti] if ti < len(sl) else [])]
        if len(flat) < 8 or not ans or ans.lower() in ("yes", "no"):   # skip yes/no (not span-answerable)
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat})
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
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0}
    tok = AutoTokenizer.from_pretrained(BI); m = AutoModel.from_pretrained(BI).to(DEV).eval()
    f1s = []; sims = []; contained = []
    for d in data:
        en = unit(encode(d["sents"], tok, m)); qn = unit(encode([Q_INSTR + d["q"]], tok, m))[0]
        s = en @ qn; top1 = int(np.argmax(s)); sims.append(float(s[top1]))
        f1s.append(f1_score(d["sents"][top1], d["ans"])); contained.append(int(contains(d["sents"][top1], d["ans"])))
    del m
    f1s = np.array(f1s); sims = np.array(sims); contained = np.array(contained); n = len(f1s)
    answerable = f1s >= 0.50
    frac = float(answerable.mean()); med_ans = float(np.median(f1s[answerable])) if answerable.any() else 0.0
    contain_rate = float(contained.mean())
    print("  [A1] direct-answer fraction (top-1 F1>=0.50) = %.3f | containment-rate = %.3f | median F1(answerable)=%.3f (n=%d)" % (frac, contain_rate, med_ans, n), flush=True)
    # A2 threshold router: predict answerable if sim >= thr; precision among predicted, with coverage >= 10%
    best_prec = 0.0; best_thr = None; best_cov = 0.0
    for thr in np.quantile(sims, np.linspace(0.3, 0.95, 14)):
        pred = sims >= thr; cov = float(pred.mean())
        if cov < 0.10:
            continue
        prec = float(answerable[pred].mean()) if pred.any() else 0.0
        if prec > best_prec:
            best_prec = prec; best_thr = float(thr); best_cov = cov
    print("  [A2] best router precision=%.3f at sim>=%.3f (coverage=%.3f)" % (best_prec, best_thr or 0.0, best_cov), flush=True)
    return {"n": n, "frac": frac, "contain_rate": contain_rate, "med_ans": med_ans, "router_prec": best_prec, "router_thr": best_thr, "router_cov": best_cov}


def verdict(r) -> Tuple[str, str]:
    frac = r["frac"]; prec = r["router_prec"]
    summary = "A1 direct-answer-frac=%.3f (containment=%.3f, median-F1-answerable=%.3f); A2 router precision=%.3f at thr=%.3f cov=%.3f (n=%d)" % (
        frac, r["contain_rate"], r["med_ans"], prec, r.get("router_thr") or 0.0, r["router_cov"], r["n"])
    if frac >= 0.30:
        return ("HARD_PASS", "HARD_PASS: >=30%% of queries are directly answerable from top-1 retrieval (F1>=0.50) -- LLM-bypass fast-path is worth building (~10-25x speedup on that fraction)%s. " % ("; router precision>=0.80 gates it cleanly" if prec >= 0.80 else "") + summary)
    if frac >= 0.15 or prec >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: partial -- direct-answer fraction 15-30%% or router precise; fast-path viable for a sub-segment (consider extractive span head, Anchor 4). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: <15%% directly answerable -- raw retrieval is not an answer (sentences != spans); LLM-bypass needs extraction, not raw top-1. " + summary)


print("[config] anchor=%s mode=%s n_q=%d" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
