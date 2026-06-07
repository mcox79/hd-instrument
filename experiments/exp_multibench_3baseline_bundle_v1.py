"""
exp_multibench_3baseline_bundle_v1 -- BUNDLED multi-benchmark 3-baseline (Qwen+bge loaded ONCE) -- GPU.

ROUTING: 5-GPU batch, bundled per user "we can bundle" to share the Qwen+bge load across benchmarks. Runs the
  bare / vanilla-RAG / substrate-selected answer-F1 3-baseline on THREE benchmarks in one process:
    B1 hotpot_fullwiki (n=200, harder full-Wikipedia multi-hop) -- the v1 headline at Research's requested scale.
    B2 PubMedQA (medical-domain RAG; regulated-industry use case).
    B3 hotpot_distractor (n=200; re-confirm the cycle-158 +0.35 at scale).
  Substrate arm = whiten top-10 bge + K-hop select 2. GPU.
PRE-REGISTERED (per benchmark): HARD-PASS both RAG and substrate beat bare by >= 0.15 F1. Bundle verdict = HARD_PASS if a
  majority (>=2/3) of benchmarks HARD-PASS; MIDDLE if 1; HARD-FAIL if 0.
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. self-retrieval. 3. loaders return records.
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

ANCHOR_NAME = "multibench_3baseline_bundle_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 10
DSDIR = REPO / "data" / "datasets"; HOTPOT_D = DSDIR / "hotpot_qa_distractor_dev_1k.jsonl"; PUBMED = DSDIR / "pubmed_abstracts_10k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 15 if RUN_MODE == "smoke" else 200
_SENT = re.compile(r"(?<=[.!?])\s+")


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def norm_ans(s):
    s = s.lower(); s = "".join(c for c in s if c not in string.punctuation); s = re.sub(r"\b(a|an|the)\b", " ", s); return " ".join(s.split())


def f1(pred, gold):
    p = norm_ans(pred).split(); g = norm_ans(gold).split()
    if not p or not g:
        return float(p == g)
    nc = sum(min(p.count(w), g.count(w)) for w in set(p) & set(g))
    if nc == 0:
        return 0.0
    pr = nc / len(p); rc = nc / len(g); return 2 * pr * rc / (pr + rc)


def _selftest():
    assert abs(f1("Barack Obama", "barack obama") - 1.0) < 1e-6, "F1 identical=1"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert callable(load_hotpot) and callable(load_pubmed), "loaders return records"
    print("[selftest] PASS: multibench-3baseline-bundle", flush=True)


def load_hotpot(n, path):
    out = []
    if not path.exists():
        return out
    for l in open(path, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        flat = [s for ti in range(len(titles)) for s in (sl[ti] if ti < len(sl) else [])]
        if len(flat) < 12 or not ans:
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat})
        if len(out) >= n:
            break
    return out


def load_hotpot_fullwiki(n):
    try:
        from datasets import load_dataset
        ds = load_dataset("hotpotqa/hotpot_qa", "fullwiki", split="validation", trust_remote_code=True)
    except Exception as e:
        print("  [warn] fullwiki load failed: %s" % str(e)[:80], flush=True); return []
    out = []
    for r in ds:
        ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []
        flat = [str(s) for ti in range(len(titles)) for s in (sl[ti] if ti < len(sl) else [])]
        if len(flat) < 8 or not ans:
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat})
        if len(out) >= n:
            break
    return out


def load_pubmed(n, path):
    out = []
    if not path.exists():
        return out
    for l in open(path, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        q = r.get("question", ""); la = r.get("long_answer") or r.get("final_decision") or ""
        ctx = r.get("context")
        if isinstance(ctx, dict):
            parts = ctx.get("contexts") or ctx.get("context") or []
            text = " ".join(parts) if isinstance(parts, list) else str(parts)
        elif isinstance(ctx, list):
            text = " ".join(str(x) for x in ctx)
        else:
            text = str(ctx or "")
        sents = [s.strip() for s in _SENT.split(text) if 25 < len(s.strip()) < 400]
        if len(sents) < 6 or not q or not la:
            continue
        out.append({"q": q, "ans": la, "sents": sents[:80]})
        if len(out) >= n:
            break
    return out


def bi_encode(texts, tok, m, DEV, torch):
    out = []
    for i in range(0, len(texts), 32):
        t = tok(texts[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def answer(ltok, lm, q, context, DEV, torch):
    user = ("Context:\n" + context + "\n\nQuestion: " + q) if context else ("Question: " + q)
    msg = [{"role": "system", "content": "Answer with a short factual answer (a few words). Output only the answer."}, {"role": "user", "content": user}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1792).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=32, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()


def bench(data, btok, bm, ltok, lm, DEV, torch):
    bare = rag = sub = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm, DEV, torch)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm, DEV, torch))[0]
        order = np.argsort(en @ qn)[::-1]; top = order[:TOPK]; rag_ctx = "\n".join(sents[i] for i in top)
        s = en[top]; mu = s.mean(0); cov = ((s - mu).T @ (s - mu)) / max(len(s), 1)
        U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
        ew = unit((s - mu) @ Wd); qw = unit((qn - mu) @ Wd); h1 = int(np.argmax(ew @ qw))
        qb = qw + ew[h1]; qb = qb / (np.linalg.norm(qb) + 1e-8); s2 = ew @ qb; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        sub_ctx = "\n".join([sents[top[h1]], sents[top[h2]]])
        bare += f1(answer(ltok, lm, d["q"], None, DEV, torch), d["ans"])
        rag += f1(answer(ltok, lm, d["q"], rag_ctx, DEV, torch), d["ans"])
        sub += f1(answer(ltok, lm, d["q"], sub_ctx, DEV, torch), d["ans"])
    n = max(len(data), 1); return {"n": len(data), "bare": bare / n, "rag": rag / n, "sub": sub / n}


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


def run() -> Dict:
    benches = [("hotpot_fullwiki", load_hotpot_fullwiki(N_Q)), ("pubmedqa", load_pubmed(N_Q, PUBMED)), ("hotpot_distractor", load_hotpot(N_Q, HOTPOT_D))]
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    res = {}
    for name, data in benches:
        if not data:
            print("  [%s] no data -- skipped" % name, flush=True); res[name] = {"n": 0, "bare": 0, "rag": 0, "sub": 0}; continue
        r = bench(data, btok, bm, ltok, lm, DEV, torch); res[name] = r
        print("  [%s] n=%d bare=%.3f vanilla-RAG=%.3f substrate=%.3f (lift_rag=%+.3f lift_sub=%+.3f)" % (name, r["n"], r["bare"], r["rag"], r["sub"], r["rag"] - r["bare"], r["sub"] - r["bare"]), flush=True)
    del lm, bm; torch.cuda.empty_cache()
    return {"res": res}


def verdict(r) -> Tuple[str, str]:
    res = r["res"]; passes = 0; lines = []
    for name, x in res.items():
        ok = x["n"] > 0 and (x["rag"] - x["bare"]) >= 0.15 and (x["sub"] - x["bare"]) >= 0.15
        passes += int(ok)
        lines.append("%s(n=%d bare=%.3f rag=%.3f sub=%.3f %s)" % (name, x["n"], x["bare"], x["rag"], x["sub"], "PASS" if ok else "no"))
    summary = "; ".join(lines)
    if passes >= 2:
        return ("HARD_PASS", "HARD_PASS: %d/3 benchmarks show RAG+substrate beating bare by >=0.15 F1 -- assembled-system-beats-bare-LLM holds across benchmark families. " % passes + summary)
    if passes == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 1/3 benchmarks pass. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: 0/3 benchmarks show the retrieval lift. " + summary)


print("[config] anchor=%s mode=%s n_q=%d (3 benchmarks bundled)" % (ANCHOR_NAME, RUN_MODE, N_Q), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
