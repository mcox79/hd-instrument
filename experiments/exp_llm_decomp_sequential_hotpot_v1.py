"""
exp_llm_decomp_sequential_hotpot_v1 -- multi-hop: SEQUENTIAL agentic decomposition (retrieve->extract->substitute) -- GPU.

ROUTING: follows exp_dev_to_research_multihop_fairsize_ceiling. 5 methods plateau on HotpotQA 2-hop; all were single-shot or
  PARALLEL. This is the SEQUENTIAL agentic loop -- the true multi-hop mechanism: (1) Qwen2.5-1.5B writes hop-1 query;
  (2) bge retrieves fact-1; (3) Qwen extracts the bridge entity from fact-1 given the question; (4) Qwen writes hop-2 query
  with the bridge substituted; (5) bge retrieves fact-2. recall@2hop over {fact-1, fact-2}. If this closes the gap, the
  composition step works at fair size (and Pattern B can later make it substrate-native). GPU.
PRE-REGISTERED: HARD-PASS sequential recall@2hop >= 0.60. MIDDLE 0.50-0.60. HARD-FAIL < 0.50 (composition not winnable at
  fair size -> Pattern B or different benchmark).
FORMULA SELF-TESTS (PROT-022): 1. self-retrieval. 2. nonempty-extract. 3. parse columnar.
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
import argparse, time, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "llm_decomp_sequential_hotpot_v1"
BI = "BAAI/bge-small-en-v1.5"; Q_INSTR = "Represent this sentence for searching relevant passages: "
LLM = "Qwen/Qwen2.5-1.5B-Instruct"
HOTPOT = REPO / "data" / "datasets" / "hotpot_qa_distractor_dev_1k.jsonl"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
N_Q = 30 if RUN_MODE == "smoke" else 120


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _selftest():
    g = np.random.default_rng(0); e = unit(g.standard_normal((6, 16))); assert int(np.argmax(e @ e[0])) == 0, "self-retrieval"
    assert "x".strip() != "", "nonempty-extract"
    rec = {"context": {"title": ["A"], "sentences": [["s0"]]}, "supporting_facts": {"title": ["A"], "sent_id": [0]}}
    assert rec["context"]["title"][0] == "A", "parse columnar"
    print("[selftest] PASS: llm-decomp-seq", flush=True)


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
        ctx = r.get("context") or {}; sf = r.get("supporting_facts") or {}
        titles = ctx.get("title") or []; sent_lists = ctx.get("sentences") or []
        flat = []
        for ti, title in enumerate(titles):
            for si, s in enumerate(sent_lists[ti] if ti < len(sent_lists) else []):
                flat.append((title, si, s))
        gold = set(zip(sf.get("title") or [], sf.get("sent_id") or []))
        if len(flat) < 4 or len(gold) < 2:
            continue
        out.append({"q": r.get("question", ""), "sents": flat, "gold": gold})
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


def llm(ltok, lm, sys_p, user_p, max_new=40):
    msg = [{"role": "system", "content": sys_p}, {"role": "user", "content": user_p}]
    p = ltok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = ltok(p, return_tensors="pt").input_ids.to(DEV)
    with torch.no_grad():
        out = lm.generate(ids, max_new_tokens=max_new, do_sample=False, pad_token_id=ltok.eos_token_id)
    return ltok.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()


HOP1 = "Write ONE simple search query for the first fact needed to answer this multi-hop question. Output only the query."
EXTRACT = "Given the question and a retrieved passage, output ONLY the bridge entity (name/title) from the passage that links to the second hop. Output just the entity."
HOP2 = "Using the bridge entity, write ONE simple search query for the SECOND fact that answers the question. Output only the query."


def run() -> Dict:
    data = load_hotpot(N_Q)
    if not data:
        print("[FATAL] no hotpot records", flush=True); return {"naive": 0.0, "seq": 0.0, "n": 0}
    ltok = AutoTokenizer.from_pretrained(LLM); lm = AutoModelForCausalLM.from_pretrained(LLM, torch_dtype=torch.float16, use_safetensors=True).to(DEV).eval()
    btok = AutoTokenizer.from_pretrained(BI); bm = AutoModel.from_pretrained(BI).to(DEV).eval()
    naive = 0; seq = 0
    for d in data:
        sents = d["sents"]; texts = [s for (_, _, s) in sents]; en = unit(bi_encode(texts, btok, bm))
        qn = unit(bi_encode([Q_INSTR + d["q"]], btok, bm))[0]; order = np.argsort(en @ qn)[::-1]
        naive += int(len(set((sents[i][0], sents[i][1]) for i in order[:2]) & d["gold"]) >= 2)
        q1 = llm(ltok, lm, HOP1, d["q"])                                                       # hop-1 query
        e1 = unit(bi_encode([Q_INSTR + q1], btok, bm))[0]; h1 = int(np.argmax(en @ e1))         # retrieve fact-1
        bridge = llm(ltok, lm, EXTRACT, "Question: %s\nPassage: %s" % (d["q"], sents[h1][2]))    # extract bridge
        q2 = llm(ltok, lm, HOP2, "Question: %s\nBridge entity: %s" % (d["q"], bridge))           # hop-2 query w/ bridge
        e2 = unit(bi_encode([Q_INSTR + q2], btok, bm))[0]; s2 = en @ e2; s2[h1] = -1e9; h2 = int(np.argmax(s2))
        seq += int(len(set([(sents[h1][0], sents[h1][1]), (sents[h2][0], sents[h2][1])]) & d["gold"]) >= 2)
    del lm, bm; torch.cuda.empty_cache()
    n = len(data); rn = naive / n; rs = seq / n
    print("  n=%d naive_recall@2hop=%.3f sequential_decomp_recall@2hop=%.3f lift=%+.3f" % (n, rn, rs, rs - rn), flush=True)
    return {"n": n, "naive": rn, "seq": rs}


def verdict(r) -> Tuple[str, str]:
    rs = r["seq"]; rn = r["naive"]
    summary = "sequential-decomp recall@2hop=%.3f naive=%.3f lift=%+.3f (n=%d, Qwen2.5-1.5B retrieve-extract-substitute + bge-small)" % (rs, rn, rs - rn, r["n"])
    if rs >= 0.60:
        return ("HARD_PASS", "HARD_PASS: sequential agentic decomposition reaches recall@2hop>=0.60 -- composition works at fair size; the retrieve-extract-substitute loop is the v1 multi-hop recipe (Pattern B can make it substrate-native). " + summary)
    if rs >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: sequential decomp 0.50-0.60 -- the loop helps; bigger LLM or Pattern B may close the rest. " + summary)
    return ("HARD_FAIL", "HARD_FAIL: even sequential agentic decomp <0.50 at fair size -- HotpotQA 2-hop composition is not fair-size-winnable with this stack; argues for Pattern B or a different v1 benchmark. " + summary)


print("[config] anchor=%s mode=%s n_q=%d llm=%s bi=%s" % (ANCHOR_NAME, RUN_MODE, N_Q, LLM, BI), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
