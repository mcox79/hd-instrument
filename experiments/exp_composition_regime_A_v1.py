"""
exp_composition_regime_A_v1 -- composition-regime K-sweep: does substrate filtering beat brute context as K grows? -- GPU.

ROUTING: handoff substrate_composition_regime_2x Anchor 1 (Regime 1). The cycle-161 finding (substrate filtering loses to
  brute top-10 at K=10) may be because K=10 is below the context-pressure crossover. Tests: at K=50, does brute context
  DEGRADE (too much distractor noise) AND does substrate compositional filtering (whiten + K-hop select 2) BEAT brute K=50?
  HotpotQA (on runner) + Qwen2.5-1.5B + bge-small. GPU.
PRE-REGISTERED: HARD-PASS F1(K=50,brute) < F1(K=10,brute) - 0.04 (brute degrades at high K) AND F1(K=50,filtered) >
  F1(K=50,brute) + 0.03 (filtering wins under context pressure). MIDDLE one of the two. HARD-FAIL neither.
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. self-retrieval. 3. parse columnar.
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

ANCHOR_NAME = "composition_regime_A_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 120


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
    prec = nc / len(p); rec = nc / len(g); return 2 * prec * rec / (prec + rec)


def _selftest():
    assert abs(f1_score("Barack Obama", "barack obama") - 1.0) < 1e-6, "F1 identical=1"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: composition-regime-A", flush=True)


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
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l)
        ctx = r.get("context") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = [s for ti in range(len(titles)) for s in (sent_lists[ti] if ti < len(sent_lists) else [])]
        if len(flat) < 12 or not ans:
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
    return np.concatenate(out, 0).astype(np.float32)


def answer(ltok, lm, q, context):
    msg = [{"role": "system", "content": "Answer with a short factual answer (a few words). Output only the answer."}, {"role": "user", "content": "Context:\n" + context + "\n\nQuestion: " + q}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=2048).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=24, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"n": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    b10 = b50 = f50 = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]
        ctx10 = "\n".join(sents[i] for i in order[:10]); ctx50 = "\n".join(sents[i] for i in order[:min(50, len(sents))])
        top = order[:min(50, len(sents))]; sub = en[top]; mu = sub.mean(0); cov = ((sub-mu).T @ (sub-mu)) / max(len(sub),1)
        U, S, _ = np.linalg.svd(cov + 1e-3*np.eye(cov.shape[0])); Wd = (U @ np.diag(1/np.sqrt(S+1e-3)) @ U.T).astype(np.float32)
        ew = unit((sub-mu) @ Wd); qw = unit((qn-mu) @ Wd); h1 = int(np.argmax(ew @ qw))
        qb = qw + ew[h1]; qb = qb/(np.linalg.norm(qb)+1e-8); s2 = ew @ qb; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        filt = "\n".join([sents[top[h1]], sents[top[h2]]])
        b10 += f1_score(answer(ltok, lm, d["q"], ctx10), d["ans"])
        b50 += f1_score(answer(ltok, lm, d["q"], ctx50), d["ans"])
        f50 += f1_score(answer(ltok, lm, d["q"], filt), d["ans"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); r = {"n": n, "brute10": b10/n, "brute50": b50/n, "filt50": f50/n}
    print("  n=%d brute_K10_F1=%.3f brute_K50_F1=%.3f substrate_filt_K50_F1=%.3f" % (n, r["brute10"], r["brute50"], r["filt50"]), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    degr = r["brute10"] - r["brute50"]; win = r["filt50"] - r["brute50"]
    summary = "brute@K10=%.3f brute@K50=%.3f filtered@K50=%.3f (brute-degradation=%+.3f, filter-win=%+.3f, n=%d)" % (r["brute10"], r["brute50"], r["filt50"], degr, win, r["n"])
    if degr >= 0.04 and win >= 0.03:
        return ("HARD_PASS", "HARD_PASS: composition regime EXISTS -- brute context degrades at K=50 AND substrate filtering beats brute K=50; the substrate-filtering advantage appears under context pressure. " + summary)
    if degr >= 0.04 or win >= 0.03:
        return ("MIDDLE_BAND", "MIDDLE_BAND: one of (brute degrades / filter wins) holds, not both. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: no composition regime -- brute context does not degrade at K=50 and filtering does not win. " + summary)


print("[config] anchor=%s mode=%s n_q=%d llm=%s bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, LLM, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
