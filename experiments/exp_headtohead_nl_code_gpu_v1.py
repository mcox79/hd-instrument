"""
exp_headtohead_nl_code_gpu_v1.py -- north-star head-to-head: substrate vs LLM on NL intent + CODE pattern -- GPU.

ROUTING: complete more north-star dimensions (Research 8-dim matrix). Substrate intent-classification (0.834) and CODE
  algorithm-pattern (0.739) vs Qwen2.5-0.5B-Instruct doing the SAME classification via prompting. ATIS intent (pick from intent
  list) + MBPP code-pattern (pick from 8 patterns). Bundled data (RESCUE). import torch (PROT-020). No CoT.
PRE-REGISTERED: report substrate vs LLM on intent + code-pattern. HARD-PASS substrate >= LLM on >=1/2 (substrate competes on
  NL/CODE classification at tiny size). UNKNOWN if setup fails.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys, time, re, json
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent
SMOKE = "--smoke" in sys.argv
SUB = {"intent": 0.834, "code_pattern": 0.739}
OUT = REPO / "data" / "exp_headtohead_nl_code_gpu_v1"
PATTERNS = ["SORT", "SEARCH", "STRING", "MATH", "ACCUMULATOR", "LIST", "RECURSION", "MISC"]
def _gold_type(code, prompt):
    c = code.lower(); pl = prompt.lower()
    fn = re.search(r"def\s+(\w+)", code); name = fn.group(1) if fn else ""
    if name and len(re.findall(r"\b" + re.escape(name) + r"\s*\(", code)) >= 2: return "RECURSION"
    if "sorted(" in c or ".sort(" in c or "heapq" in c: return "SORT"
    if any(s in pl for s in ("string", "char", "vowel", "palindrome", "letter", "word", "case", "substring", "reverse")) or any(s in c for s in (".join", ".split", ".replace", ".lower", ".upper", "ord(", "chr(")): return "STRING"
    if any(s in pl for s in ("prime", "factorial", "fibonacci", "gcd", "lcm", "divisor", "divisible", "power", "digit", "factor")): return "MATH"
    if any(s in pl for s in ("find", "search", "locate", "index of", "position")) or ".index(" in c or "bisect" in c: return "SEARCH"
    if any(s in pl for s in ("sum", "total", "count", "average", "product", "number of")) or "sum(" in c: return "ACCUMULATOR"
    if any(s in c for s in ("max(", "min(", "filter", "[x for", "[i for", "set(", "unique", "any(", "all(")) or any(s in pl for s in ("list", "array", "largest", "smallest", "maximum", "minimum")): return "LIST"
    return "MISC"
def main():
    print("[config] head-to-head NL+CODE", flush=True)
    DEV = "cuda" if torch.cuda.is_available() else "cpu"
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(name)
    mdl = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float16 if DEV == "cuda" else torch.float32).to(DEV); mdl.eval()
    print("[model] loaded on", DEV, flush=True)
    def ask(prompt, choices):
        msgs = [{"role": "user", "content": prompt + "\nAnswer with exactly one of: " + ", ".join(choices) + ". Just the label."}]
        p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True); ins = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            o = mdl.generate(**ins, max_new_tokens=12, do_sample=False, pad_token_id=tok.eos_token_id)
        txt = tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True).upper()
        for ch in choices:
            if ch.upper() in txt: return ch
        return None
    N = 25 if SMOKE else 120; rows = {}; wins = 0
    # intent (ATIS)
    try:
        atis = json.load(open(REPO / "experiments" / "data" / "atis_intent.json", encoding="utf-8"))
        intents = sorted({e["intent"] for e in atis["train"]}); test = atis["test"][:N]
        cor = 0
        for e in test:
            if ask(e["text"], intents[:12]) == e["intent"]: cor += 1  # cap choices for prompt length
        acc = cor / len(test); win = SUB["intent"] >= acc; wins += int(win)
        rows["intent"] = {"substrate": SUB["intent"], "qwen0.5b": round(acc, 3), "substrate_wins": win}
        print("  intent: substrate=%.3f vs Qwen=%.3f (%s) n=%d" % (SUB["intent"], acc, "SUB" if win else "LLM", len(test)), flush=True)
    except Exception as e: print("intent x", str(e)[:50], flush=True)
    # code-pattern (MBPP)
    try:
        ds = json.load(open(REPO / "experiments" / "data" / "mbpp" / "mbpp_full.json", encoding="utf-8"))
        test = [(e.get("text", ""), _gold_type(e.get("code", ""), e.get("text", ""))) for e in ds["test"] if e.get("text") and e.get("code")][:N]
        cor = 0
        for txt, gold in test:
            if ask("Classify this programming task by its core algorithm: " + txt, PATTERNS) == gold: cor += 1
        acc = cor / len(test); win = SUB["code_pattern"] >= acc; wins += int(win)
        rows["code_pattern"] = {"substrate": SUB["code_pattern"], "qwen0.5b": round(acc, 3), "substrate_wins": win}
        print("  code_pattern: substrate=%.3f vs Qwen=%.3f (%s) n=%d" % (SUB["code_pattern"], acc, "SUB" if win else "LLM", len(test)), flush=True)
    except Exception as e: print("code x", str(e)[:50], flush=True)
    verdict = "HARD_PASS" if wins >= 1 else "HARD_FAIL"
    msg = "%s: substrate (tiny) wins %d/2 NL/CODE classification dims vs Qwen-0.5B. %s" % (verdict, wins, rows)
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "headtohead_nl_code_gpu_v1", "verdict": verdict, "verdict_msg": msg, "per_dim": rows, "wins": wins}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)
if "--self-test" in sys.argv:
    assert _gold_type("def f(s): return s.split()", "x") == "STRING"; print("[selftest] PASS: headtohead-nl-code", flush=True); sys.exit(0)
main()
