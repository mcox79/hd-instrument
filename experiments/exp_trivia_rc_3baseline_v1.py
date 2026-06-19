"""
exp_trivia_rc_3baseline_v1 -- TriviaQA-rc 3-baseline (bare vs vanilla-RAG vs substrate) answer F1 -- GPU.

ROUTING: handoff hotpot_fullwiki_authorize #2 (re-stage trivia_qa rc + build 3-baseline). Uses the rc config's Wikipedia
  evidence docs as the retrieval corpus: split entity_pages.wiki_context into sentences, bge-small retrieve top-10, Qwen
  answer. Three arms: bare (closed-book) / vanilla-RAG (top-10 context) / substrate (whiten+K-hop select 2). Encyclopedic
  single-fact recall -- complements HotpotQA's multi-hop. Alias-aware F1 (TriviaQA answers have many aliases). GPU.
PRE-REGISTERED: HARD-PASS both RAG and substrate beat bare by >= 0.15 F1. MIDDLE retrieval beats bare 0.05-0.15.
  HARD-FAIL retrieval lift < 0.05.
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. alias max. 3. self-retrieval.
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
import argparse, time, re, string
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "trivia_rc_3baseline_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 10
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 150


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1_one(pred, gold):
    p = norm_ans(pred).split(); g = norm_ans(gold).split()
    if not p or not g:
        return float(p == g)
    nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
    if nc == 0:
        return 0.0
    pr = nc / len(p); rc = nc / len(g); return 2 * pr * rc / (pr + rc)


def f1_aliases(pred, aliases):
    return max((f1_one(pred, a) for a in aliases), default=0.0)


def _selftest():
    assert abs(f1_one("Mount Everest", "mount everest") - 1.0) < 1e-6, "F1 identical=1"
    assert f1_aliases("Everest", ["K2", "Everest"]) == 1.0, "alias max"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    print("[selftest] PASS: trivia-rc-3baseline", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
    from datasets import load_dataset
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA required.", flush=True); sys.exit(1)
DEV = torch.device("cuda"); print("[GPU] %s" % torch.cuda.get_device_name(0), flush=True)
_SENT = re.compile(r"(?<=[.!?])\s+")


def load_trivia(n):
    ds = load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")
    out = []
    for r in ds:
        ans = r.get("answer") or {}; aliases = list(ans.get("aliases") or []) + [ans.get("value", "")]
        aliases = [a for a in aliases if a]
        ep = r.get("entity_pages") or {}; ctxs = ep.get("wiki_context") or []
        text = " ".join(c for c in ctxs if isinstance(c, str))[:6000]
        sents = [s.strip() for s in _SENT.split(text) if 30 < len(s.strip()) < 400]
        if len(sents) < 8 or not aliases:
            continue
        out.append({"q": r.get("question", ""), "aliases": aliases, "sents": sents[:80]})
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
    return np.concatenate(out, 0).astype(np.float32)


def answer(ltok, lm, q, context):
    user = ("Context:\n" + context + "\n\nQuestion: " + q) if context else ("Question: " + q)
    msg = [{"role": "system", "content": "Answer with a short factual answer (a few words). Output only the answer."}, {"role": "user", "content": user}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1536).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=24, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run() -> Dict:
    data = load_trivia(N_Q)
    if not data:
        print("[FATAL] no trivia records", flush=True); return {"n": 0, "bare": 0, "rag": 0, "sub": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    bare = rag = subF = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]; top = order[:TOPK]; rag_ctx = "\n".join(sents[i] for i in top)
        sub = en[top]; mu = sub.mean(0); cov = ((sub - mu).T @ (sub - mu)) / max(len(sub), 1)
        U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
        ew = unit((sub - mu) @ Wd); qw = unit((qn - mu) @ Wd); h1 = int(np.argmax(ew @ qw))
        qb = qw + ew[h1]; qb = qb / (np.linalg.norm(qb) + 1e-8); s2 = ew @ qb; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        sub_ctx = "\n".join([sents[top[h1]], sents[top[h2]]])
        bare += f1_aliases(answer(ltok, lm, d["q"], None), d["aliases"])
        rag += f1_aliases(answer(ltok, lm, d["q"], rag_ctx), d["aliases"])
        subF += f1_aliases(answer(ltok, lm, d["q"], sub_ctx), d["aliases"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); return {"n": n, "bare": bare / n, "rag": rag / n, "sub": subF / n}


def verdict(r) -> Tuple[str, str]:
    fb = r["bare"]; fr = r["rag"]; fs = r["sub"]
    summary = "bare=%.3f vanilla-RAG=%.3f substrate=%.3f (n=%d, TriviaQA-rc, Qwen2.5-1.5B + bge-small)" % (fb, fr, fs, r["n"])
    if (fr - fb) >= 0.15 and (fs - fb) >= 0.15:
        return ("HARD_PASS", "HARD_PASS: both RAG and substrate beat bare by >=0.15 F1 on TriviaQA -- encyclopedic-recall north-star confirmed; substrate %s RAG by %+.3f. " % ("beats" if fs >= fr else "matches", fs - fr) + summary)
    if (fr - fb) >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retrieval beats bare by 0.05-0.15. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: retrieval lift <0.05 over bare (Qwen-1.5B may already know these encyclopedic facts parametrically). " + summary)


print("[config] anchor=%s mode=%s n_q=%d llm=%s bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, LLM, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
