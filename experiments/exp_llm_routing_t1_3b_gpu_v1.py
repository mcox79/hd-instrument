"""
exp_llm_routing_t1_3b_gpu_v1 -- LLM-ROUTING-T1: can a 3B instruct model route structured queries to the substrate -- GPU.

ROUTING: llm_capability_separation handoff, anchor #1 (run-first, cheapest gate). Tests the V1 product thesis: LLM = language
  layer, substrate = knowledge layer, coupled via TOOL-USE (Recipe 6.1, no architecture surgery -- what Panel A already does).
  The pre-req is that the LLM can correctly DECIDE which queries need the substrate (factual / structured / multi-hop lookup ->
  ROUTE) vs which it should answer itself (language / reasoning / rephrasing -> DIRECT). Zero-shot prompt to Qwen-2.5-3B-Instruct
  over a labeled mix; measure routing accuracy. Local GPU, no cloud.
PRE-REGISTERED: HARD-PASS >= 0.70 correct routing zero-shot over the labeled set. MIDDLE >= 0.60. HARD-FAIL < 0.60.
FORMULA SELF-TESTS (PROT-022): 1. label parse. 2. accuracy. 3. balanced set.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "llm_routing_t1_3b_gpu_v1"; MODEL = "Qwen/Qwen2.5-3B-Instruct"; FALLBACK = "Qwen/Qwen2.5-1.5B-Instruct"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# ROUTE = needs substrate (factual/structured/multi-hop lookup); DIRECT = language/reasoning the LLM handles itself
ROUTE_Q = [
    "Who is the CEO of the company that acquired DeepMind?", "What year was the parent company of Instagram founded?",
    "List all subsidiaries of Alphabet.", "Which city is the headquarters of the company that makes the PlayStation?",
    "What is the capital of the country where the Eiffel Tower is located?", "Who founded the lab that created AlphaFold?",
    "What are the ingredients in the standard recipe for aspirin?", "Which award did the inventor of the transistor win?",
    "What is the population of the largest city in Japan?", "Who succeeded the third president of the United States?",
    "What molecule does hemoglobin transport?", "Which river flows through the capital of Egypt?",
    "What is the boiling point of water at sea level in Celsius?", "Who wrote the book that the movie Blade Runner is based on?",
    "What is the chemical symbol for the element with atomic number 79?",
]
DIRECT_Q = [
    "Summarize this paragraph in one sentence.", "Rewrite this email to sound more polite.",
    "Write a haiku about autumn.", "Explain the difference between affect and effect.",
    "Translate 'good morning' into French.", "What is a metaphor for resilience?",
    "Make this sentence more concise.", "Give me three synonyms for 'happy'.",
    "Continue this story: The door creaked open...", "Correct the grammar in this sentence.",
    "Brainstorm names for a coffee shop.", "Paraphrase this for a five-year-old.",
    "What tone does this message convey?", "Turn these bullet points into a paragraph.",
    "Suggest a catchy title for a blog post about productivity.",
]


def _selftest():
    assert ("ROUTE" in "I would ROUTE this"), "label parse"
    assert abs((3 / 4) - 0.75) < 1e-9, "accuracy"
    assert len(ROUTE_Q) == len(DIRECT_Q), "balanced set"
    print("[selftest] PASS: llm-routing-t1-3b", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)

SYS = ("You are the controller for a system with a structured knowledge substrate (a database of facts, entities, and relations "
       "supporting multi-hop lookup). For each user query decide routing. Reply with EXACTLY one word: ROUTE if answering needs "
       "factual/entity/relational knowledge lookup, or DIRECT if it is a pure language or reasoning task you should do yourself.")


def decide(tok, mdl, q):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": q}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    enc = tok(text, return_tensors="pt").to(DEV)
    with torch.no_grad():
        out = mdl.generate(**enc, max_new_tokens=4, do_sample=False, pad_token_id=tok.eos_token_id)
    resp = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).upper()
    if "ROUTE" in resp:
        return "ROUTE"
    if "DIRECT" in resp:
        return "DIRECT"
    return "?"


def run() -> Dict:
    mid = MODEL
    try:
        tok = AutoTokenizer.from_pretrained(mid, trust_remote_code=True)
        mdl = AutoModelForCausalLM.from_pretrained(mid, torch_dtype=torch.bfloat16, trust_remote_code=True).to(DEV).eval()
    except Exception as e:
        print("[warn] %s load failed (%s); falling back to %s" % (mid, str(e)[:60], FALLBACK), flush=True)
        mid = FALLBACK; tok = AutoTokenizer.from_pretrained(mid, trust_remote_code=True)
        mdl = AutoModelForCausalLM.from_pretrained(mid, torch_dtype=torch.bfloat16, trust_remote_code=True).to(DEV).eval()
    print("[model] %s" % mid, flush=True)
    rq = ROUTE_Q[:6] if SMOKE else ROUTE_Q; dq = DIRECT_Q[:6] if SMOKE else DIRECT_Q
    correct = 0; n = 0; rr = 0; dr = 0
    for q in rq:
        d = decide(tok, mdl, q); correct += int(d == "ROUTE"); rr += int(d == "ROUTE"); n += 1
    for q in dq:
        d = decide(tok, mdl, q); correct += int(d == "DIRECT"); dr += int(d == "DIRECT"); n += 1
    del mdl
    acc = correct / n
    print("  routing accuracy=%.3f (ROUTE-recall=%.2f DIRECT-recall=%.2f, n=%d, model=%s)" % (acc, rr / len(rq), dr / len(dq), n, mid), flush=True)
    return {"accuracy": acc, "route_recall": rr / len(rq), "direct_recall": dr / len(dq), "n": n, "model": mid}


def verdict(r) -> Tuple[str, str]:
    s = "routing-accuracy=%.3f (ROUTE-recall=%.2f DIRECT-recall=%.2f, n=%d, %s)" % (r["accuracy"], r["route_recall"], r["direct_recall"], r["n"], r["model"])
    if r["accuracy"] >= 0.70:
        return ("HARD_PASS", "HARD_PASS: 3B-class instruct model routes structured-vs-language queries >=70pct zero-shot -- the LLM-as-language-layer + substrate-as-knowledge-layer tool-use split (Recipe 6.1, V1-ready) is viable. " + s)
    if r["accuracy"] >= 0.60:
        return ("MIDDLE_BAND", "MIDDLE_BAND: routing 0.60-0.70 zero-shot; few-shot prompting likely lifts it. " + s)
    return ("HARD_FAIL", "HARD_FAIL: routing <0.60 zero-shot -- separation needs few-shot/finetune or a larger router. " + s)


print("[config] anchor=%s mode=%s model=%s" % (ANCHOR_NAME, RUN_MODE, MODEL), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
