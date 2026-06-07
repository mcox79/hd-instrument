"""
exp_substrate_vs_bare_llm_hotpot_v1 -- HotpotQA FULLWIKI 3-baseline (harder: 10 full-Wikipedia paras) bare vs RAG vs substrate -- GPU.

ROUTING: the actual "beats LLMs at relative size" thesis test. Even though HotpotQA recall@2hop is hard, the SYSTEM-level
  question is: does a small LLM (Qwen2.5-1.5B) answer better WITH substrate-retrieved context than CLOSED-BOOK? bge-small
  retrieves top-k context sentences; the LLM answers with vs without them. Token-level answer F1 (SQuAD/HotpotQA metric).
  This is where the assembled system should beat the bare model: the substrate supplies facts the small LLM lacks. GPU.
PRE-REGISTERED: HARD-PASS augmented F1 - bare F1 >= 0.15 (substrate-augmented decisively beats bare small LLM). MIDDLE
  0.05-0.15. HARD-FAIL < 0.05 (no system advantage).
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. F1 disjoint=0. 3. parse columnar.
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, json, re, string
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "hotpot_fullwiki_3baseline_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 10
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 120


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation)
    s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1_score(pred, gold):
    p = norm_ans(pred).split(); g = norm_ans(gold).split()
    if not p or not g:
        return float(p == g)
    common = {}
    for w in p:
        if w in g:
            common[w] = 1
    nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
    if nc == 0:
        return 0.0
    prec = nc / len(p); rec = nc / len(g); return 2 * prec * rec / (prec + rec)


def _selftest():
    assert abs(f1_score("Barack Obama", "barack obama") - 1.0) < 1e-6, "F1 identical=1"
    assert f1_score("cat", "dog") == 0.0, "F1 disjoint=0"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: substrate-vs-bare", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)


def load_hotpot(n):
    from datasets import load_dataset
    ds = load_dataset("hotpotqa/hotpot_qa", "fullwiki", split="validation", trust_remote_code=True)
    out = []
    for r in ds:
        ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = [str(x) for ti in range(len(titles)) for x in (sent_lists[ti] if ti < len(sent_lists) else [])]
        if len(flat) < 8 or not ans:
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat})
        if len(out) >= n:
            break
    return out

def bi_encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0, 384), np.float32)


def answer(ltok, lm, q, context=None):
    sys_p = "Answer the question with a short factual answer (a few words). Output only the answer."
    user_p = ("Context:\n" + context + "\n\nQuestion: " + q) if context else ("Question: " + q)
    msg = [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1024).input_ids.to(DEV)
    with torch.no_grad():
        out = lm.generate(ids, max_new_tokens=24, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"bare": 0.0, "aug": 0.0, "n": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    bare = 0.0; rag = 0.0; subF = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]; top = order[:TOPK]; rag_ctx = "\n".join(sents[i] for i in top)
        sub = en[top]; mu = sub.mean(0); cov = ((sub-mu).T @ (sub-mu)) / max(len(sub),1)
        U, S, _ = np.linalg.svd(cov + 1e-3*np.eye(cov.shape[0])); Wd = (U @ np.diag(1/np.sqrt(S+1e-3)) @ U.T).astype(np.float32)
        ew = unit((sub-mu) @ Wd); qw = unit((qn-mu) @ Wd); h1 = int(np.argmax(ew @ qw))
        qb = qw + ew[h1]; qb = qb/(np.linalg.norm(qb)+1e-8); s2 = ew @ qb; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        sub_ctx = "\n".join([sents[top[h1]], sents[top[h2]]])
        bare += f1_score(answer(ltok, lm, d["q"], None), d["ans"])
        rag += f1_score(answer(ltok, lm, d["q"], rag_ctx), d["ans"])
        subF += f1_score(answer(ltok, lm, d["q"], sub_ctx), d["ans"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); fb = bare/n; fr = rag/n; fs = subF/n
    print("  n=%d bare_F1=%.3f vanilla-RAG_F1=%.3f substrate_F1=%.3f" % (n, fb, fr, fs), flush=True)
    return {"n": n, "bare": fb, "rag": fr, "sub": fs}


def verdict(r) -> Tuple[str, str]:
    fb = r["bare"]; fr = r["rag"]; fs = r["sub"]
    summary = "bare=%.3f vanilla-RAG=%.3f substrate=%.3f (n=%d, Qwen2.5-1.5B + bge-small)" % (fb, fr, fs, r["n"])
    if (fr - fb) >= 0.15 and (fs - fb) >= 0.15:
        return ("HARD_PASS", "HARD_PASS: both RAG and substrate beat bare by >=0.15 F1 -- north-star confirmed; substrate %s vanilla-RAG by %+.3f. " % ("beats" if fs>=fr else "matches", fs-fr) + summary)
    if (fr - fb) >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retrieval beats bare by 0.05-0.15. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: retrieval lift <0.05 over bare. " + summary)


print("[config] anchor=%s mode=%s n_q=%d llm=%s bi=%s topk=%d" % (ANCHOR_NAME, RUN_MODE, N_Q, LLM, BI, TOPK), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
