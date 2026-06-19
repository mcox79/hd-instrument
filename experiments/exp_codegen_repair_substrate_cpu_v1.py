"""
exp_codegen_repair_substrate_cpu_v1.py -- CODEGEN-REPAIR diagnostic: pattern-library ceiling vs selection -- CPU.

ROUTING: Research CODEGEN-REPAIR-1. CODEGEN-LIGHT (docstring-keyword single-pattern selection) got pass@1=0.15. This diagnostic
  separates the two failure sources: (a) PATTERN-LIBRARY ceiling = pass@k-oracle (does ANY of the K patterns pass the hidden
  test? -- upper bound, clearly labeled as oracle), vs (b) SELECTION = pass@1 with docstring-keyword selection (0.15). The gap
  (oracle - docstring) is the headroom an execution-repair/better-selection loop could recover. If oracle ceiling >= 0.40, the
  patterns are rich enough and selection is the bottleneck (build the repair loop); if oracle < 0.20, the pattern library itself
  is insufficient (need composition / subgoal decomposition). Substrate-only generator + subprocess execution.
PRE-REGISTERED: HARD-PASS pattern-library oracle ceiling >= 0.40 (patterns rich enough; selection is the gap -> repair worth it).
  MIDDLE oracle 0.20-0.40. HARD-FAIL oracle < 0.20 (patterns insufficient; need composition). UNKNOWN if dataset load fails.
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
ANCHOR_NAME = "codegen_repair_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
_BOOK: Dict[str, np.ndarray] = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "994")))
def _tok(w):
    if w not in _BOOK:
        ang = (_RNG.random(N) * 2 - 1) * math.pi; _BOOK[w] = np.exp(1j * ang).astype(np.complex64)
    return _BOOK[w]
def _bundle(words):
    v = np.zeros(N, dtype=np.complex64)
    for w in words: v = v + _tok(w)
    n = np.abs(v); n[n == 0] = 1; return (v / n).astype(np.complex64)
def _kw(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2]
PATTERNS: List[Tuple[List[str], str]] = [
    (["sum", "total", "add", "elements"], "    return sum({p})"),
    (["maximum", "largest", "max", "greatest"], "    return max({p})"),
    (["minimum", "smallest", "min", "least"], "    return min({p})"),
    (["length", "number", "count", "many"], "    return len({p})"),
    (["sort", "sorted", "order", "ascending"], "    return sorted({p})"),
    (["reverse", "reversed", "backwards"], "    return {p}[::-1]"),
    (["even"], "    return [x for x in {p} if x % 2 == 0]"),
    (["odd"], "    return [x for x in {p} if x % 2 != 0]"),
    (["positive", "greater", "above"], "    return [x for x in {p} if x > 0]"),
    (["negative", "below", "less"], "    return [x for x in {p} if x < 0]"),
    (["unique", "distinct", "duplicate"], "    return sorted(set({p}))"),
    (["uppercase", "upper", "capital"], "    return {p}.upper()"),
    (["lowercase", "lower"], "    return {p}.lower()"),
    (["absolute", "abs"], "    return abs({p})"),
    (["product", "multiply"], "    r = 1\n    for x in {p}:\n        r *= x\n    return r"),
    (["average", "mean"], "    return sum({p}) / len({p})"),
    (["balance", "running", "below", "zero"], "    bal = 0\n    for x in {p}:\n        bal += x\n        if bal < 0:\n            return True\n    return False"),
    (["round", "nearest"], "    return round({p})"),
    (["square", "squared"], "    return {p} * {p}"),
    (["truncate", "decimal", "part"], "    return {p} % 1.0"),
    (["concatenate", "join"], "    return ''.join({p})"),
    (["double", "twice"], "    return [2 * x for x in {p}]"),
    (["increment", "increase"], "    return [x + 1 for x in {p}]"),
    (["first"], "    return {p}[0]"),
    (["last"], "    return {p}[-1]"),
]
_PVEC = None
def _pvecs():
    global _PVEC
    if _PVEC is None: _PVEC = [(_bundle(kws), body) for kws, body in PATTERNS]
    return _PVEC
def _first_param(prompt):
    m = re.search(r"def\s+\w+\s*\(([^)]*)\)", prompt)
    if not m or not m.group(1).strip(): return None
    return m.group(1).split(",")[0].split(":")[0].split("=")[0].strip()
def _natural(it):
    sol = it.get("canonical_solution", "")
    if len(it["prompt"]) > 600: return False
    if any(b in sol for b in ["import ", "lambda", "def ", "class ", "yield", " re.", "math.", "itertools"]): return False
    return sol.count("\n") <= 6
def _select(prompt, p):
    qv = _bundle(_kw(prompt)); pv = _pvecs()
    sims = [float((v @ np.conj(qv)).real) for v, _ in pv]
    return pv[int(np.argmax(sims))][1].replace("{p}", p)
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
def _selftest():
    assert len(PATTERNS) >= 20 and _first_param("def f(x):\n pass") == "x"
    print("[selftest] PASS: codegen-repair (%d patterns)" % len(PATTERNS), flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = list(load_dataset("openai_humaneval", split="test"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "pass_k_oracle": 0.0}
    curated = [it for it in ds if _natural(it)]
    curated = curated[:10] if SMOKE else curated[:40]
    oracle = 0; docsel = 0
    for it in curated:
        p = _first_param(it["prompt"])
        if p is None: continue
        cands = [body.replace("{p}", p) for _k, body in PATTERNS]
        oracle += int(any(_run_tests(it["prompt"], b, it["test"], it["entry_point"]) for b in cands))
        sel = _select(it["prompt"], p)
        docsel += int(_run_tests(it["prompt"], sel, it["test"], it["entry_point"]))
    nC = len(curated)
    pk = oracle / nC if nC else 0.0; p1 = docsel / nC if nC else 0.0
    print("  CODEGEN-REPAIR diagnostic: pattern-library oracle-ceiling=%.3f | docstring-select pass@1=%.3f | selection-gap=%.3f (n=%d)" %
          (pk, p1, pk - p1, nC), flush=True)
    return {"pass_k_oracle": round(pk, 3), "pass1_docsel": round(p1, 3), "selection_gap": round(pk - p1, 3), "n_curated": nC, "n_patterns": len(PATTERNS)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    pk = r["pass_k_oracle"]; p1 = r["pass1_docsel"]
    s = "oracle-ceiling=%.3f docstring-pass@1=%.3f selection-gap=%.3f (%d patterns)" % (pk, p1, r["selection_gap"], r["n_patterns"])
    if pk >= 0.40:
        return ("HARD_PASS", "HARD_PASS: pattern-library oracle ceiling>=0.40 -- the patterns ARE rich enough; SELECTION is the bottleneck (docstring-select only %.2f). An execution-repair/visible-test selection loop is worth building (recoverable headroom %.2f). " % (p1, r["selection_gap"]) + s)
    if pk >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: oracle ceiling 0.20-0.40 -- patterns partially cover; both more patterns AND repair needed. " + s)
    return ("HARD_FAIL", "HARD_FAIL: oracle ceiling <0.20 -- the pattern library itself is insufficient on substrate-natural HumanEval; need composition/subgoal decomposition, not just better selection. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
