"""
exp_headtohead_math_vs_llm_v2_cpu_v1.py -- north-star head-to-head (MINIMAL, no numpy) -- CPU.

ROUTING: Research (d) head-to-head. v1 segfaulted (numpy imported before torch via _seed_checkpoint -> OpenMP conflict on this
  Windows CPU). This v2 imports torch FIRST, avoids numpy/_seed_checkpoint entirely, writes metrics JSON directly. Compares the
  substrate Tier-A math numbers vs Qwen2.5-0.5B-Instruct zero-shot on MAWPS/MultiArith/SVAMP/ASDiv. Substrate (<100MB) is far
  smaller than a 0.5B LLM -- favorable size comparison for the north-star.
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ.setdefault("OMP_NUM_THREADS", "4")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys, time, re, json
from pathlib import Path
from fractions import Fraction
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
REPO = Path(__file__).resolve().parent.parent
SMOKE = "--smoke" in sys.argv
SUBSTRATE = {"MAWPS": 0.806, "MultiArith": 0.753, "SVAMP": 0.297, "ASDiv": 0.224}
OUT = REPO / "data" / "exp_headtohead_math_vs_llm_v2_cpu_v1"
def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    try: return Fraction(m.group(0)).limit_denominator(10**6) if m else None
    except Exception: return None
def _pred(txt):
    nums = re.findall(r"-?\d+(?:\.\d+)?", txt.replace(",", ""))
    try: return Fraction(nums[-1]).limit_denominator(10**6) if nums else None
    except Exception: return None
def _load():
    out = {}
    mb = json.load(open(REPO / "experiments" / "data" / "math_benchmarks_test.json", encoding="utf-8"))
    for k, rows in mb.items(): out[k] = [(r["q"], _ans(r["a"])) for r in rows]
    rows = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    out["ASDiv"] = [((e.get("body", "") + " " + e.get("question", "")).strip(), _ans(e.get("answer"))) for e in rows]
    for k in list(out): out[k] = [(q, a) for q, a in out[k] if q and a is not None]
    return out
def main():
    print("[config] head-to-head v2 (minimal)", flush=True)
    torch.set_num_threads(4)
    name = "Qwen/Qwen2.5-0.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(name); mdl = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32); mdl.eval()
    print("[model] loaded", flush=True)
    data = _load(); SAMPLE = 25 if SMOKE else 80
    rows = {}; wins = 0; lat = {}
    for bench, items in data.items():
        items = items[:SAMPLE]; cor = 0; t_tot = 0.0
        for q, gold in items:
            msgs = [{"role": "user", "content": q + "\nSolve this math word problem. Answer with just the final number."}]
            p = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            ins = tok(p, return_tensors="pt"); t0 = time.time()
            with torch.no_grad():
                o = mdl.generate(**ins, max_new_tokens=40, do_sample=False, pad_token_id=tok.eos_token_id)
            t_tot += time.time() - t0
            pr = _pred(tok.decode(o[0][ins["input_ids"].shape[1]:], skip_special_tokens=True))
            if pr is not None and pr == gold: cor += 1
        acc = cor / len(items); sub = SUBSTRATE.get(bench, 0.0); win = sub >= acc; wins += int(win)
        lat[bench] = round(t_tot / len(items), 3); rows[bench] = {"substrate": sub, "qwen0.5b": round(acc, 3), "substrate_wins": win}
        print("  %s: substrate=%.3f vs Qwen0.5B=%.3f (%s) %.2fs/item n=%d" % (bench, sub, acc, "SUB>=LLM" if win else "LLM>", lat[bench], len(items)), flush=True)
    verdict = "HARD_PASS" if wins >= 2 else ("MIDDLE_BAND" if wins == 1 else "HARD_FAIL")
    msg = "%s: substrate (tiny, <100MB) wins %d/4 math benchmarks vs Qwen-0.5B-Instruct (zero-shot). avg LLM latency=%.2fs/item vs substrate ~ms. North-star: %s" % (verdict, wins, sum(lat.values()) / len(lat) if lat else 0, "math dimension WON" if wins >= 2 else "see per-benchmark")
    print("\n[VERDICT] " + msg, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"anchor_name": "headtohead_math_vs_llm_v2_cpu_v1", "verdict": verdict, "verdict_msg": msg, "per_benchmark": rows, "llm_latency_s": lat, "wins": wins}, open(OUT / "metrics.json", "w", encoding="utf-8"))
    print("[metrics] written", flush=True)
if "--self-test" in sys.argv:
    assert _pred("answer 42") == 42; print("[selftest] PASS: headtohead-v2", flush=True); sys.exit(0)
main()
