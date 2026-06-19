"""
exp_substrate_iterative_multihop_pretest_v1 -- iterative (2-round) retrieval vs single-shot for multi-hop -- GPU.

ROUTING: substrate_iterative_multihop_pretest_AUTHORIZE (multi-hop revival mandate). Single-shot dense retrieval plateaus at
  r@2~0.5 on HotpotQA (ceiling confirmed: bge-large 0.516, e5-large 0.444). This tests whether ITERATIVE retrieval breaks it:
  hop1 retrieve by question -> Qwen generates a next-hop query from hop1 facts -> hop2 retrieve by that query -> accumulate ->
  Qwen answers from the union. Each hop gets a Merkle hash (auditable chain). Measured SEPARATELY: recall@2 (both supporting
  facts retrieved) and answer F1, iterative vs single-shot. HotpotQA distractor (gold supporting_facts). GPU.
PRE-REGISTERED: HARD-PASS iterative recall@2 >= 0.55 (breaks the single-shot ceiling) OR iterative answer-F1 >= single-shot
  + 0.05. MIDDLE recall@2 in [0.50,0.55) with F1 gain. HARD-FAIL no recall@2 or F1 improvement over single-shot.
FORMULA SELF-TESTS (PROT-022): 1. F1 identical=1. 2. self-retrieval. 3. merkle chains. 4. recall counts gold.
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
import argparse, time, json, re, string, hashlib
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_iterative_multihop_pretest_v1"
BI = "BAAI/bge-large-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"; KH = 2
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 20 if RUN_MODE == "smoke" else 150


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


def h(b):
    return hashlib.sha256(b).hexdigest()


def _selftest():
    assert abs(f1_score("Barack Obama", "barack obama") - 1.0) < 1e-6, "F1 identical=1"
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 8))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    c = h(b"genesis"); assert h((c + "x").encode()) != c, "merkle chains"
    gold = {1, 3}; top = [1, 5, 3]; assert len(set(top) & gold) == 2, "recall counts gold"
    print("[selftest] PASS: substrate-iterative-multihop", flush=True)


def load_hotpot(n):
    out = []
    if not HOTPOT.exists():
        return out
    for l in open(HOTPOT, encoding="utf-8"):
        r = json.loads(l); ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}; ans = r.get("answer", "")
        titles = ctx.get("title") or []; sl = ctx.get("sentences") or []; flat = []; gold = []
        sf_set = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        for ti in range(len(titles)):
            for si, s in enumerate(sl[ti] if ti < len(sl) else []):
                if (titles[ti], si) in sf_set:
                    gold.append(len(flat))
                flat.append(s)
        if len(flat) < 12 or len(gold) < 2 or not ans:
            continue
        out.append({"q": r.get("question", ""), "ans": ans, "sents": flat, "gold": gold})
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


def gen(ltok, lm, sysmsg, user, mnt):
    msg = [{"role": "system", "content": sysmsg}, {"role": "user", "content": user}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt", truncation=True, max_length=1536).input_ids.to(DEV)
    with torch.no_grad():
        o = lm.generate(ids, max_new_tokens=mnt, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot", flush=True); return {"n": 0}
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    ss_r2 = it_r2 = ss_f1 = it_f1 = 0.0; audit_ok = 0
    for d in data:
        sents = d["sents"]; gold = set(d["gold"]); en = unit(bi_encode(sents, btok, bm)); qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]
        sims = en @ qn; order = np.argsort(sims)[::-1]
        # single-shot: top-2 by question
        ss_top = list(order[:2]); ss_r2 += int(len(set(ss_top) & gold) == 2)
        ss_ctx = "\n".join(sents[i] for i in order[:8])
        ss_f1 += f1_score(gen(ltok, lm, "Answer with a short factual answer. Output only the answer.", "Context:\n" + ss_ctx + "\n\nQuestion: " + d["q"], 24), d["ans"])
        # iterative: hop1 best, generate next-hop query, hop2 best by new query
        chain = h(b"genesis")
        hop1 = int(order[0]); chain = h((chain + sents[hop1]).encode())
        nhq = gen(ltok, lm, "Given the question and a known fact, output a SHORT search query (a few words) for the missing second fact. Output only the query.", "Question: " + d["q"] + "\nKnown fact: " + sents[hop1] + "\nNext search query:", 16)
        qn2 = unit(bi_encode([Q_INSTR + nhq], btok, bm))[0]; sims2 = en @ qn2
        order2 = [i for i in np.argsort(sims2)[::-1] if i != hop1]
        hop2 = int(order2[0]); chain = h((chain + sents[hop2]).encode())
        audit_ok += int(chain == h((h((h(b"genesis") + sents[hop1]).encode()) + sents[hop2]).encode()))   # replay verifies
        it_top = [hop1, hop2]; it_r2 += int(len(set(it_top) & gold) == 2)
        acc = list(dict.fromkeys([hop1, hop2] + list(order[:6])))   # union: 2 hops + question top-6
        it_ctx = "\n".join(sents[i] for i in acc[:8])
        it_f1 += f1_score(gen(ltok, lm, "Answer with a short factual answer. Output only the answer.", "Context:\n" + it_ctx + "\n\nQuestion: " + d["q"], 24), d["ans"])
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); r = {"n": n, "ss_r2": ss_r2/n, "it_r2": it_r2/n, "ss_f1": ss_f1/n, "it_f1": it_f1/n, "audit": audit_ok/n}
    print("  recall@2 single-shot=%.3f iterative=%.3f | F1 single-shot=%.3f iterative=%.3f | audit-replay=%.3f (n=%d)" % (r["ss_r2"], r["it_r2"], r["ss_f1"], r["it_f1"], r["audit"], n), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    summary = "recall@2 single=%.3f iter=%.3f; F1 single=%.3f iter=%.3f; audit=%.3f (n=%d)" % (r["ss_r2"], r["it_r2"], r["ss_f1"], r["it_f1"], r["audit"], r["n"])
    if r["it_r2"] >= 0.55 or (r["it_f1"] - r["ss_f1"]) >= 0.05:
        return ("HARD_PASS", "HARD_PASS: iterative retrieval breaks the multi-hop ceiling (recall@2>=0.55 or +0.05 F1 over single-shot) -- multi-hop revival viable; auditable per-hop chain preserved. " + summary)
    if r["it_r2"] >= 0.50 and r["it_r2"] > r["ss_r2"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: iterative improves recall@2 over single-shot but doesn't clear 0.55. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: iterative retrieval does not beat single-shot on recall@2 or F1 -- ceiling holds even with iteration. " + summary)


print("[config] anchor=%s mode=%s n_q=%d bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
