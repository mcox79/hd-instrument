"""
exp_babilong_qa1_substrate_v1 -- BABILong qa1 (long-context needle): substrate retrieval vs bare Qwen -- GPU.

ROUTING: tier4 Gap 1 (BABILong; Titans published strong score; substrate untested). BABILong embeds a bAbI single-supporting-
  fact question in a long distractor context. Tests whether substrate retrieval (bge over the context sentences, top-k) cuts
  through the distractors better than feeding bare Qwen the FULL long context. Config "2k" (2k-token distractor context),
  split qa1. bare = Qwen on full input; vanilla-RAG = Qwen on bge top-8; substrate = Qwen on whiten+top-5. Accuracy (target
  substring). GPU.
PRE-REGISTERED: HARD-PASS both retrieval arms beat bare by >= 0.15 accuracy (retrieval cuts distractors). MIDDLE 0.05-0.15.
  HARD-FAIL < 0.05 (Qwen handles the 2k context fine without retrieval).
FORMULA SELF-TESTS (PROT-022): 1. substring match. 2. self-retrieval. 3. sentence split.
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
import argparse, time, re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "babilong_qa1_substrate_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; TOPK = 8; SUB_K = 5; CFG = "2k"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 15 if RUN_MODE == "smoke" else 100
_SENT = re.compile(r"(?<=[.!?])\s+")


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def hit(pred, target):
    return int(target.strip().lower() in pred.strip().lower())


def _selftest():
    assert hit("The answer is bathroom.", "bathroom") == 1 and hit("kitchen", "bathroom") == 0, "substring match"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert len(_SENT.split("A. B. C.")) == 3, "sentence split"
    print("[selftest] PASS: babilong-qa1-substrate", flush=True)


def load_babilong(n):
    from datasets import load_dataset
    ds = load_dataset("RMT-team/babilong", CFG, split="qa1")
    out = []
    for r in ds:
        ctx = r.get("input", ""); q = r.get("question", ""); t = r.get("target", "")
        sents = [s.strip() for s in _SENT.split(ctx) if 8 < len(s.strip()) < 400]
        if len(sents) < 8 or not q or not t:
            continue
        out.append({"q": q, "ans": t, "sents": sents})
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
    for i in range(0, len(texts), 64):
        t = tok(texts[i:i + 64], return_tensors="pt", padding=True, truncation=True, max_length=64).to(DEV)
        with torch.no_grad():
            o = m(**t)
        out.append(o.last_hidden_state[:, 0, :].float().cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


def answer(ltok, lm, q, context):
    msg = [{"role": "system", "content": "Answer with a single word (the location). Output only the answer."}, {"role": "user", "content": context + "\n\n" + q}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=4096).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=8, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True)


def run() -> Dict:
    data = load_babilong(N_Q)
    if not data:
        print("[FATAL] no babilong records", flush=True); return {"n": 0, "bare": 0, "rag": 0, "sub": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    bare = rag = sub = 0.0
    for d in data:
        sents = d["sents"]; en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        order = np.argsort(en @ qn)[::-1]; top = order[:TOPK]; rag_ctx = "\n".join(sents[i] for i in top)
        s = en[top]; mu = s.mean(0); cov = ((s - mu).T @ (s - mu)) / max(len(s), 1)
        U, S, _ = np.linalg.svd(cov + 1e-3 * np.eye(cov.shape[0])); Wd = (U @ np.diag(1 / np.sqrt(S + 1e-3)) @ U.T).astype(np.float32)
        ew = unit((s - mu) @ Wd); qw = unit((qn - mu) @ Wd); sub_order = np.argsort(ew @ qw)[::-1][:SUB_K]
        sub_ctx = "\n".join(sents[top[j]] for j in sub_order)
        full_ctx = " ".join(sents)
        bare += hit(answer(ltok, lm, d["q"], full_ctx), d["ans"])
        rag += hit(answer(ltok, lm, d["q"], rag_ctx), d["ans"])
        sub += hit(answer(ltok, lm, d["q"], sub_ctx), d["ans"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); return {"n": n, "bare": bare / n, "rag": rag / n, "sub": sub / n}


def verdict(r) -> Tuple[str, str]:
    fb, fr, fs = r["bare"], r["rag"], r["sub"]
    summary = "bare(full-ctx)=%.3f vanilla-RAG=%.3f substrate=%.3f (n=%d, BABILong-%s qa1, Qwen2.5-1.5B + bge-small)" % (fb, fr, fs, r["n"], CFG)
    if (fr - fb) >= 0.15 and (fs - fb) >= 0.15:
        return ("HARD_PASS", "HARD_PASS: retrieval cuts through BABILong distractors -- both RAG and substrate beat full-context bare by >=0.15 acc; substrate %s RAG by %+.3f. " % ("beats" if fs >= fr else "matches", fs - fr) + summary)
    if (fr - fb) >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: retrieval beats bare by 0.05-0.15 acc on long-context needle. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: retrieval lift <0.05 -- Qwen handles the %s distractor context without retrieval. " % CFG + summary)


print("[config] anchor=%s mode=%s n_q=%d cfg=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, CFG), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
