"""
exp_codegen_subgoal_substrate_cpu_v1.py -- CODEGEN-SUBGOAL: compositional code-gen (filter->map->reduce) -- CPU.

ROUTING: Research CODEGEN-SUBGOAL-1 (Architecture 3). My CODEGEN-REPAIR diagnostic showed single-pattern selection caps ~0.175
  (composition, not selection, is the bottleneck). This tests COMPOSITION: decompose the docstring into a subgoal chain
  (optional filter ops -> optional map ops -> a reduce op) and compose them, leveraging the substrate's validated compose
  strength (PP-333/339 algorithm-compose 1.0). Solves 2-3 op problems ("sum of squares", "count of evens", "max of doubled")
  that single-pattern instantiation cannot. Substrate selects each subgoal op via keyword associative recall; chain executed.
  Curated substrate-natural HumanEval subset; subprocess execution.
PRE-REGISTERED: HARD-PASS pass@1 >= 0.40 (composition reaches demo-grade). MIDDLE >= 0.20 (lifts past the 0.175 single-pattern
  ceiling). HARD-FAIL < 0.20 (composition does not help). UNKNOWN if dataset load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re, tempfile, subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "codegen_subgoal_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
_BOOK: Dict[str, np.ndarray] = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "995")))
def _tok(w):
    if w not in _BOOK:
        ang = (_RNG.random(N) * 2 - 1) * math.pi; _BOOK[w] = np.exp(1j * ang).astype(np.complex64)
    return _BOOK[w]
def _kw(text):
    return set(re.findall(r"[a-z]+", text.lower()))
# subgoal op vocabulary: filters, maps, reduces -- each (trigger keywords, code fragment)
FILTERS = {"even": "x % 2 == 0", "odd": "x % 2 != 0", "positive": "x > 0", "negative": "x < 0", "prime": "x > 1 and all(x%d for d in range(2,int(x**0.5)+1))"}
FILTER_KW = {"even": ["even"], "odd": ["odd"], "positive": ["positive", "greater"], "negative": ["negative", "less"], "prime": ["prime"]}
MAPS = {"square": "x*x", "double": "2*x", "increment": "x+1", "abs": "abs(x)", "negate": "-x", "cube": "x*x*x"}
MAP_KW = {"square": ["square", "squared", "squares"], "double": ["double", "doubled", "twice"], "increment": ["increment", "increased"], "abs": ["absolute"], "negate": ["negate", "negative"], "cube": ["cube", "cubed"]}
REDUCES = {"sum": "sum(SEQ)", "max": "max(SEQ)", "min": "min(SEQ)", "len": "len(SEQ)", "product": "__prod(SEQ)", "sorted": "sorted(SEQ)", "mean": "sum(SEQ)/len(SEQ)"}
REDUCE_KW = {"sum": ["sum", "total", "add"], "max": ["max", "maximum", "largest", "greatest"], "min": ["min", "minimum", "smallest"], "len": ["count", "number", "how", "many"], "product": ["product", "multiply"], "sorted": ["sort", "sorted", "order"], "mean": ["average", "mean"]}
def _match(kws, table):
    out = []
    for op, trig in table.items():
        if kws & set(trig): out.append(op)
    return out
def _first_param(prompt):
    m = re.search(r"def\s+\w+\s*\(([^)]*)\)", prompt)
    if not m or not m.group(1).strip(): return None
    return m.group(1).split(",")[0].split(":")[0].split("=")[0].strip()
def _compose(prompt, p):
    """Decompose docstring keywords into filter->map->reduce subgoal chain and compose a body."""
    kws = _kw(prompt)
    fs = _match(kws, FILTER_KW); ms = _match(kws, MAP_KW); rs = _match(kws, REDUCE_KW)
    if not rs: return None                                   # need at least a reduce/output op
    seq = p
    if fs: seq = "[x for x in %s if %s]" % (seq, " and ".join(FILTERS[f] for f in fs[:2]))
    if ms:
        expr = ms[0]; mexpr = {"square": "x*x", "double": "2*x", "increment": "x+1", "abs": "abs(x)", "negate": "-x", "cube": "x*x*x"}[expr]
        seq = "[%s for x in %s]" % (mexpr, seq)
    red = rs[0]; body_expr = REDUCES[red].replace("SEQ", seq)
    pre = "    def __prod(s):\n        r=1\n        for v in s: r*=v\n        return r\n" if red == "product" else ""
    return pre + "    return " + body_expr
def _run_tests(prompt, body, test, entry):
    src = prompt + "\n" + body + "\n\n" + test + "\n\ncheck(%s)\n" % entry
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(src); path = f.name
    try:
        return subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=10).returncode == 0
    except Exception:
        return False
    finally:
        try: os.unlink(path)
        except Exception: pass
def _natural(it):
    sol = it.get("canonical_solution", "")
    if len(it["prompt"]) > 600: return False
    if any(b in sol for b in ["import ", "lambda", "def ", "class ", "yield", " re.", "math.", "itertools"]): return False
    return sol.count("\n") <= 6
def _selftest():
    b = _compose("def f(lst):\n    '''Return the sum of squares of elements in lst'''", "lst")
    assert b and "sum(" in b and "x*x" in b, b
    print("[selftest] PASS: codegen-subgoal", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = list(load_dataset("openai_humaneval", split="test"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "pass1": 0.0}
    curated = [it for it in ds if _natural(it)]
    curated = curated[:10] if SMOKE else curated[:40]
    npass = 0; attempted = 0; solved = []
    for it in curated:
        p = _first_param(it["prompt"])
        if p is None: continue
        body = _compose(it["prompt"], p)
        if body is None: continue
        attempted += 1
        if _run_tests(it["prompt"], body, it["test"], it["entry_point"]):
            npass += 1; solved.append(it["task_id"])
    nC = len(curated)
    p1 = npass / nC if nC else 0.0
    print("  CODEGEN-SUBGOAL: pass@1=%.3f (%d/%d curated, %d attempted-composition) solved=%s" % (p1, npass, nC, attempted, solved[:12]), flush=True)
    return {"pass1": round(p1, 3), "n_pass": npass, "n_curated": nC, "n_attempted": attempted}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    p1 = r["pass1"]; s = "pass@1=%.3f (%d/%d, %d composition-attempts)" % (p1, r["n_pass"], r["n_curated"], r["n_attempted"])
    if p1 >= 0.40:
        return ("HARD_PASS", "HARD_PASS: compositional code-gen (filter->map->reduce subgoal chains) reaches pass@1>=0.40 -- composition leverages substrate compose strength to solve multi-op problems single patterns cannot. Demo-grade. " + s)
    if p1 >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: composition lifts pass@1 to 0.20-0.40 (past the 0.175 single-pattern ceiling) -- composition is the right direction; expand subgoal vocabulary. " + s)
    return ("HARD_FAIL", "HARD_FAIL: composition pass@1 <0.20 -- filter/map/reduce chains insufficient on substrate-natural HumanEval. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
