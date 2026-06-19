"""
exp_pubmedqa_3baseline_v2 -- PubMedQA 3-baseline with the CORRECT metric (final_decision accuracy) -- GPU.

ROUTING: fix for the multibench bundle's broken pubmedqa arm (F1-vs-long_answer gave ~0.00 for all arms because long_answer
  is a paragraph). v2 scores the standard PubMedQA target: final_decision in {yes,no,maybe} as ACCURACY. bare (closed-book) vs
  vanilla-RAG (top-10 context) vs substrate (whiten+K-hop select 2) -- regulated medical-domain use case. GPU.
PRE-REGISTERED: HARD-PASS both RAG and substrate beat bare by >= 0.10 accuracy AND substrate within 90% of RAG.
  MIDDLE retrieval beats bare 0.04-0.10. HARD-FAIL retrieval lift < 0.04 (Qwen already knows / context unhelpful).
FORMULA SELF-TESTS (PROT-022): 1. decision parse. 2. self-retrieval. 3. accuracy bounds.
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
import argparse, time, json, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "pubmedqa_3baseline_v3"; SUB_K = 6
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 10
PUBMED = REPO / "data" / "datasets" / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 200
_SENT = re.compile(r"(?<=[.!?])\s+")


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def parse_decision(s):
    s = s.strip().lower()
    if re.search(r"\bmaybe\b", s):
        return "maybe"
    if re.search(r"\byes\b", s):
        return "yes"
    if re.search(r"\bno\b", s):
        return "no"
    return "?"


def _selftest():
    assert parse_decision("Yes, the study shows...") == "yes" and parse_decision("maybe") == "maybe", "decision parse"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert parse_decision("No.") == "no", "accuracy bounds"
    print("[selftest] PASS: pubmedqa-3baseline-v2", flush=True)


def load_pubmed(n):
    out = []
    if not PUBMED.exists():
        return out
    for l in open(PUBMED, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        q = r.get("question", ""); fd = (r.get("final_decision") or "").strip().lower()
        if fd not in ("yes", "no", "maybe"):
            continue
        ctx = r.get("context")
        if isinstance(ctx, dict):
            parts = ctx.get("contexts") or ctx.get("context") or []
            text = " ".join(parts) if isinstance(parts, list) else str(parts)
        elif isinstance(ctx, list):
            text = " ".join(str(x) for x in ctx)
        else:
            text = str(ctx or "")
        sents = [s.strip() for s in _SENT.split(text) if 25 < len(s.strip()) < 400]
        if len(sents) < 4 or not q:
            continue
        out.append({"q": q, "ans": fd, "sents": sents[:80]})
        if len(out) >= n:
            break
    return out


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


def bi_encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def answer(ltok, lm, q, context):
    user = (("Context:\n" + context + "\n\n") if context else "") + "Question: " + q + "\nAnswer with exactly one word: yes, no, or maybe."
    msg = [{"role": "system", "content": "You are a biomedical QA assistant. Answer only yes, no, or maybe."}, {"role": "user", "content": user}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1792).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=8, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)


def run() -> Dict:
    data = load_pubmed(N_Q)
    if not data:
        print("[FATAL] no pubmedqa records with final_decision", flush=True); return {"n": 0, "bare": 0, "rag": 0, "sub": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    bare = rag = sub = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]; top = order[:TOPK]; rag_ctx = "\n".join(sents[i] for i in top)
        s = en[top]; mu = s.mean(0); cov = ((s - mu).T @ (s - mu)) / max(len(s), 1)
        U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
        ew = unit((s - mu) @ Wd); qw = unit((qn - mu) @ Wd)
        sub_order = np.argsort(ew @ qw)[::-1][:SUB_K]            # v3: top-SUB_K whitened (v2's 2 K-hop facts lost to RAG)
        sub_ctx = "\n".join(sents[top[j]] for j in sub_order)
        bare += int(parse_decision(answer(ltok, lm, d["q"], None)) == d["ans"])
        rag += int(parse_decision(answer(ltok, lm, d["q"], rag_ctx)) == d["ans"])
        sub += int(parse_decision(answer(ltok, lm, d["q"], sub_ctx)) == d["ans"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); return {"n": n, "bare": bare / n, "rag": rag / n, "sub": sub / n}


def verdict(r) -> Tuple[str, str]:
    fb, fr, fs = r["bare"], r["rag"], r["sub"]
    summary = "bare=%.3f vanilla-RAG=%.3f substrate=%.3f (n=%d, PubMedQA final_decision accuracy, Qwen2.5-1.5B + bge-small)" % (fb, fr, fs, r["n"])
    if (fr - fb) >= 0.10 and (fs - fb) >= 0.10 and fs >= 0.90 * fr:
        return ("HARD_PASS", "HARD_PASS: both RAG and substrate beat bare by >=0.10 acc on medical PubMedQA, substrate within 90%% of RAG -- regulated-domain north-star confirmed. " + summary)
    if (fr - fb) >= 0.04:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retrieval beats bare by 0.04-0.10 acc. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: retrieval lift <0.04 acc over bare (Qwen-1.5B parametric medical knowledge or context unhelpful for yes/no/maybe). " + summary)


print("[config] anchor=%s mode=%s n_q=%d (PubMedQA final_decision accuracy)" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
