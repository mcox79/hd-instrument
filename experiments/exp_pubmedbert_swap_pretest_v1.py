"""
exp_pubmedbert_swap_pretest_v1 -- PubMedBERT drop-in encoder swap (medical domain) + TriviaQA regression -- GPU.

ROUTING: pubmedbert_swap_pretest_AUTHORIZE. The PubMedQA substrate gap was diagnosed as ENCODER failure (general bge weak on
  biomedical), not substrate algebra. Drop-in fix: swap bge-small -> PubMedBERT-base-embeddings (mean-pooled, 768-dim) for the
  substrate fillers + RAG retrieval. PRIMARY: PubMedQA 3-baseline (bare/RAG/substrate, final_decision accuracy) with the
  biomedical encoder. TERTIARY: TriviaQA regression with the SAME biomedical encoder (verify per-domain encoder strategy --
  a domain encoder is expected to retrieve worse on encyclopedic TriviaQA; this confirms why per-domain selection matters).
  bare Qwen is encoder-independent. GPU.
PRE-REGISTERED: PRIMARY HARD-PASS substrate-augmented Qwen >= 0.72 acc on PubMedQA (closes most of the 28pt gap). HARD-FAIL
  < 0.60. TERTIARY is informational (report TriviaQA substrate vs RAG; large regression = expected, confirms per-domain need).
FORMULA SELF-TESTS (PROT-022): 1. decision parse. 2. mean-pool shape. 3. self-retrieval.
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

ANCHOR_NAME = "pubmedbert_swap_pretest_v1"
ENC = "NeuML/pubmedbert-base-embeddings"; LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 10; SUB_K = 6
DSDIR = REPO / "data" / "datasets"; PUBMED = DSDIR / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 200; N_TRIVIA = 15 if RUN_MODE == "smoke" else 120
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


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1(pred, aliases):
    best = 0.0
    for gold in aliases:
        p = norm_ans(pred).split(); g = norm_ans(gold).split()
        if not p or not g:
            best = max(best, float(p == g)); continue
        nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
        if nc:
            pr = nc / len(p); rc = nc / len(g); best = max(best, 2 * pr * rc / (pr + rc))
    return best


def _selftest():
    assert parse_decision("Yes.") == "yes" and parse_decision("maybe so") == "maybe", "decision parse"
    x = np.ones((2, 3, 4)); mask = np.ones((2, 3, 1)); mp = (x * mask).sum(1) / mask.sum(1); assert mp.shape == (2, 4), "mean-pool shape"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    print("[selftest] PASS: pubmedbert-swap-pretest", flush=True)


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
            parts = ctx.get("contexts") or ctx.get("context") or []; text = " ".join(parts) if isinstance(parts, list) else str(parts)
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


def load_trivia(n):
    from datasets import load_dataset
    ds = load_dataset("mandarjoshi/trivia_qa", "rc", split="validation")
    out = []
    for r in ds:
        ans = r.get("answer") or {}; aliases = [a for a in (list(ans.get("aliases") or []) + [ans.get("value", "")]) if a]
        ep = r.get("entity_pages") or {}; ctxs = ep.get("wiki_context") or []
        text = " ".join(c for c in ctxs if isinstance(c, str))[:6000]
        sents = [s.strip() for s in _SENT.split(text) if 30 < len(s.strip()) < 400]
        if len(sents) < 8 or not aliases:
            continue
        out.append({"q": r.get("question", ""), "aliases": aliases, "sents": sents[:80]})
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


def encode(texts, tok, m):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        msk = t["attention_mask"].unsqueeze(-1).float()
        mp = (o.last_hidden_state * msk).sum(1) / msk.sum(1).clamp(min=1e-9)   # mean-pool (PubMedBERT-embeddings native)
        out.append(mp.float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def substrate_ctx(sents, en, qn, k):
    order = np.argsort(en @ qn)[::-1]; top = order[:min(50, len(sents))]; s = en[top]
    mu = s.mean(0); cov = ((s - mu).T @ (s - mu)) / max(len(s), 1)
    U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
    ew = unit((s - mu) @ Wd); qw = unit((qn - mu) @ Wd); sub_order = np.argsort(ew @ qw)[::-1][:k]
    return "\n".join(sents[top[j]] for j in sub_order), [sents[i] for i in order[:TOPK]]


def answer(ltok, lm, q, context, mode):
    if mode == "pubmed":
        user = (("Context:\n" + context + "\n\n") if context else "") + "Question: " + q + "\nAnswer with exactly one word: yes, no, or maybe."
        sysmsg = "You are a biomedical QA assistant. Answer only yes, no, or maybe."; mnt = 8
    else:
        user = (("Context:\n" + context + "\n\n") if context else "") + "Question: " + q
        sysmsg = "Answer with a short factual answer (a few words). Output only the answer."; mnt = 24
    msg = [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1792).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=mnt, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)


def bench(data, etok, em, ltok, lm, mode):
    bare = rag = sub = 0.0
    for d in data:
        sents = d["sents"]; en = unit(encode(sents, etok, em)); qn = unit(encode([d["q"]], etok, em))[0]
        sub_ctx, rag_list = substrate_ctx(sents, en, qn, SUB_K); rag_ctx = "\n".join(rag_list)
        if mode == "pubmed":
            sc = lambda pred: int(parse_decision(pred) == d["ans"])
        else:
            sc = lambda pred: f1(pred, d["aliases"])
        bare += sc(answer(ltok, lm, d["q"], None, mode))
        rag += sc(answer(ltok, lm, d["q"], rag_ctx, mode))
        sub += sc(answer(ltok, lm, d["q"], sub_ctx, mode))
    n = max(len(data), 1); return {"n": len(data), "bare": bare / n, "rag": rag / n, "sub": sub / n}


def run() -> Dict:
    pm = load_pubmed(N_Q); tv = load_trivia(N_TRIVIA)
    if not pm:
        print("[FATAL] no pubmedqa", flush=True); return {"pm": {}, "tv": {}}
    etok = AutoTokenizer.from_pretrained(ENC); em = AutoModel.from_pretrained(ENC).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    pmr = bench(pm, etok, em, ltok, lm, "pubmed")
    print("  [PubMedQA/PubMedBERT] n=%d bare=%.3f RAG=%.3f substrate=%.3f" % (pmr["n"], pmr["bare"], pmr["rag"], pmr["sub"]), flush=True)
    tvr = bench(tv, etok, em, ltok, lm, "trivia") if tv else {"n": 0, "bare": 0, "rag": 0, "sub": 0}
    print("  [TriviaQA/PubMedBERT regression] n=%d bare=%.3f RAG=%.3f substrate=%.3f" % (tvr["n"], tvr["bare"], tvr["rag"], tvr["sub"]), flush=True)
    del lm, em; torch.cuda.empty_cache()
    return {"pm": pmr, "tv": tvr}


def verdict(r) -> Tuple[str, str]:
    pm = r["pm"]; tv = r["tv"]
    summary = "PubMedQA/PubMedBERT: bare=%.3f RAG=%.3f substrate=%.3f | TriviaQA/PubMedBERT(regression): bare=%.3f RAG=%.3f substrate=%.3f (n_pm=%d)" % (
        pm.get("bare", 0), pm.get("rag", 0), pm.get("sub", 0), tv.get("bare", 0), tv.get("rag", 0), tv.get("sub", 0), pm.get("n", 0))
    if pm.get("sub", 0) >= 0.72:
        return ("HARD_PASS", "HARD_PASS: biomedical encoder closes the PubMedQA gap (substrate>=0.72) -- per-domain encoder swap works; TriviaQA regression is informational (domain encoder expected to retrieve worse on encyclopedic, confirming per-domain selection). " + summary)
    if pm.get("sub", 0) >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: PubMedBERT substrate 0.60-0.72 -- partial gap closure; consider MedCPT (secondary). " + summary)
    return ("HARD_FAIL", "HARD_FAIL: PubMedBERT substrate <0.60 -- encoder swap does not close the gap; deeper substrate-domain issue. " + summary)


print("[config] anchor=%s mode=%s n_pm=%d n_trivia=%d enc=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, N_TRIVIA, ENC), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
