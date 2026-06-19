"""
exp_headtohead_math_vs_llm_cpu_v1.py -- north-star head-to-head: substrate math solver vs small LLM -- CPU.

ROUTING: Research (d) head-to-head endorsed (north-star = functional system beats LLMs of relative size measurably). Runs
  Qwen2.5-0.5B-Instruct zero-shot on the 4 math-word-problem benchmarks and compares to the substrate Tier-A solver numbers
  (full test sets). The substrate (KB + perceptron weights, <100MB) is FAR SMALLER than a 0.5B LLM (~1GB) -- a favorable size
  comparison. Reports per-benchmark accuracy + latency (LLM gen time vs substrate ~ms). No CoT (zero-shot) for the base comparison.
PRE-REGISTERED: report substrate-vs-LLM per benchmark + LLM latency. HARD-PASS substrate >= LLM on >=2/4 math benchmarks (north-star
  math dimension won). MIDDLE 1/4. HARD-FAIL 0/4. UNKNOWN if model/data fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ.setdefault("OMP_NUM_THREADS", "4")
import torch  # FIRST (OpenMP ordering vs numpy)
from transformers import AutoModelForCausalLM, AutoTokenizer  # FIRST
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, gc
from pathlib import Path
from typing import Dict, List, Tuple
from fractions import Fraction
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "headtohead_math_vs_llm_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# substrate Tier-A full-test numbers (validated this session)
SUBSTRATE = {"MAWPS": 0.806, "MultiArith": 0.753, "SVAMP": 0.297, "ASDiv": 0.224}
def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None
def _parse_pred(txt):
    nums = re.findall(r"-?\d+(?:\.\d+)?", txt.replace(",", ""))
    if not nums: return None
    try: return Fraction(nums[-1]).limit_denominator(10**6)   # last number in the answer
    except Exception: return None
def _selftest():
    assert _parse_pred("The answer is 42.") == 42
    print("[selftest] PASS: headtohead-math-vs-llm", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load_bench():
    from datasets import load_dataset
    out = {}
    try:
        ds = load_dataset("MU-NLPC/Calc-mawps", split="test")
        out["MAWPS"] = [(e["question"], _ans(e.get("result_float") or e.get("result"))) for e in ds]
    except Exception as e: print("[data] MAWPS x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("ChilleD/MultiArith", split="test")
        out["MultiArith"] = [(e["question"], _ans(e["final_ans"])) for e in ds]
    except Exception as e: print("[data] MultiArith x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("ChilleD/SVAMP", split="test")
        out["SVAMP"] = [((e.get("Body", "") + " " + e.get("Question", "")).strip(), _ans(e["Answer"])) for e in ds]
    except Exception as e: print("[data] SVAMP x", str(e)[:40], flush=True)
    try:
        ds = load_dataset("EleutherAI/asdiv", split="validation")
        out["ASDiv"] = [((e.get("body", "") + " " + e.get("question", "")).strip(), _ans(e["answer"])) for e in ds]
    except Exception as e: print("[data] ASDiv x", str(e)[:40], flush=True)
    for k in out: out[k] = [(q, a) for q, a in out[k] if q and a is not None]
    return out
def run() -> Dict:
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        name = "Qwen/Qwen2.5-0.5B-Instruct"
        torch.set_num_threads(4)
        tok = AutoTokenizer.from_pretrained(name); mdl = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32); mdl.eval()
        data = _load_bench()
    except Exception as e:
        print("[setup] fail %s" % str(e)[:90], flush=True); return {"error": "setup_failed", "wins": 0}
    if not data: return {"error": "no_data", "wins": 0}
    import torch
    SAMPLE = 30 if SMOKE else 80
    llm = {}; lat = {}; wins = 0; rows = {}
    for bench, items in data.items():
        items = items[:SAMPLE]; cor = 0; t_tot = 0.0
        for q, gold in items:
            msgs = [{"role": "user", "content": q + "\nSolve this math word problem. Answer with just the final number."}]
            p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            ins = tok(p, return_tensors="pt"); t0 = time.time()
            with torch.no_grad():
                out = mdl.generate(**ins, max_new_tokens=40, do_sample=False, pad_token_id=tok.eos_token_id)
            t_tot += time.time() - t0
            txt = tok.decode(out[0][ins["input_ids"].shape[1]:], skip_special_tokens=True)
            pred = _parse_pred(txt)
            if pred is not None and pred == gold: cor += 1
        gc.collect()
        acc = cor / len(items); llm[bench] = round(acc, 3); lat[bench] = round(t_tot / len(items), 3)
        sub = SUBSTRATE.get(bench, 0.0); win = sub >= acc; wins += int(win)
        rows[bench] = (sub, round(acc, 3), win)
        print("  %s: substrate=%.3f vs Qwen0.5B=%.3f (%s) | LLM %.2fs/item, n=%d" % (bench, sub, acc, "SUBSTRATE>=LLM" if win else "LLM>", lat[bench], len(items)), flush=True)
    print("  HEAD-TO-HEAD MATH: substrate wins %d/4 benchmarks | avg LLM latency=%.2fs/item vs substrate ~ms" % (wins, sum(lat.values()) / len(lat)), flush=True)
    return {"wins": wins, "llm_acc": llm, "substrate_acc": SUBSTRATE, "llm_latency_s": lat, "n_per": SAMPLE}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    w = r["wins"]; s = "substrate wins %d/4 | LLM acc=%s vs substrate=%s | LLM latency=%s" % (w, r["llm_acc"], r["substrate_acc"], r["llm_latency_s"])
    if w >= 2:
        return ("HARD_PASS", "HARD_PASS: substrate math solver >= Qwen-0.5B-Instruct on %d/4 benchmarks -- a FAR SMALLER substrate (<100MB) matches/beats a 0.5B LLM on math word problems. North-star math dimension won. " % w + s)
    if w == 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: substrate wins 1/4 -- niche win. " + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate wins 0/4 vs the small LLM on math. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
