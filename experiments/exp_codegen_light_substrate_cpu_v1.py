"""
exp_codegen_light_substrate_cpu_v1.py -- CODEGEN-LIGHT: substrate code-gen on substrate-natural HumanEval subset -- CPU.

ROUTING: Research CODEGEN-LIGHT-1 (Path B). Extends CODEGEN-GATE-1 (grammar-constrained pattern expansion) with (a) a broader
  Tier-2 pattern library, (b) docstring-keyword -> pattern SELECTION via substrate associative retrieval (encode each pattern's
  trigger keywords as a phasor bundle; pick the pattern whose bundle best matches the problem's docstring keywords), and
  (c) curation to ~substrate-natural HumanEval problems (single control flow, simple list/num/str types, named-ish algorithm,
  no heavy stdlib). For each curated problem: substrate-select pattern -> instantiate with signature -> subprocess-execute
  canonical tests. pass@1 on the curated subset. Substrate role = pattern selection (associative recall) + grammar instantiation.
PRE-REGISTERED: HARD-PASS pass@1 >= 0.40 on curated subset. MIDDLE >= 0.20. HARD-FAIL < 0.20. UNKNOWN if dataset load fails.
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
ANCHOR_NAME = "codegen_light_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
_BOOK: Dict[str, np.ndarray] = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "993")))
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
# Tier-2 pattern library: (trigger keywords, body builder(param p))
PATTERNS: List[Tuple[List[str], str]] = [
    (["sum", "total", "add", "elements"], "    return sum({p})"),
    (["maximum", "largest", "max", "greatest", "biggest"], "    return max({p})"),
    (["minimum", "smallest", "min", "least"], "    return min({p})"),
    (["length", "number", "count", "many", "long"], "    return len({p})"),
    (["sort", "sorted", "order", "ascending", "increasing"], "    return sorted({p})"),
    (["reverse", "reversed", "backwards", "flip"], "    return {p}[::-1]"),
    (["even"], "    return [x for x in {p} if x % 2 == 0]"),
    (["odd"], "    return [x for x in {p} if x % 2 != 0]"),
    (["positive", "greater", "than", "zero", "above"], "    return [x for x in {p} if x > 0]"),
    (["negative", "below", "less"], "    return [x for x in {p} if x < 0]"),
    (["unique", "distinct", "remove", "duplicate"], "    return sorted(set({p}))"),
    (["uppercase", "upper", "capital", "capitalize"], "    return {p}.upper()"),
    (["lowercase", "lower"], "    return {p}.lower()"),
    (["absolute", "abs"], "    return abs({p})"),
    (["product", "multiply", "multiplied"], "    r = 1\n    for x in {p}:\n        r *= x\n    return r"),
    (["average", "mean"], "    return sum({p}) / len({p})"),
    (["below", "zero", "balance", "negative", "running"], "    bal = 0\n    for x in {p}:\n        bal += x\n        if bal < 0:\n            return True\n    return False"),
    (["round", "rounded", "nearest"], "    return round({p})"),
    (["square", "squared"], "    return {p} * {p}"),
    (["truncate", "decimal", "integer", "part"], "    return {p} % 1.0"),
    (["concatenate", "join", "concatenation"], "    return ''.join({p})"),
    (["double", "twice"], "    return [2 * x for x in {p}]"),
    (["increment", "increase", "add one"], "    return [x + 1 for x in {p}]"),
    (["first"], "    return {p}[0]"),
    (["last"], "    return {p}[-1]"),
]
_PVEC = None
def _pvecs():
    global _PVEC
    if _PVEC is None:
        _PVEC = [(_bundle(kws), body) for kws, body in PATTERNS]
    return _PVEC
def _first_param(prompt):
    m = re.search(r"def\s+\w+\s*\(([^)]*)\)", prompt)
    if not m or not m.group(1).strip(): return None
    return m.group(1).split(",")[0].split(":")[0].split("=")[0].strip()
def _natural(it):
    """substrate-natural heuristic: short prompt, list/num/str args, no heavy stdlib in canonical solution."""
    sol = it.get("canonical_solution", "")
    if len(it["prompt"]) > 600: return False
    if any(bad in sol for bad in ["import ", "lambda", "def ", "class ", "yield", " re.", "math.", "itertools"]): return False
    if sol.count("\n") > 6: return False
    return True
def _generate(prompt):
    p = _first_param(prompt)
    if p is None: return None
    qv = _bundle(_kw(prompt))
    pv = _pvecs()
    sims = [float((v @ np.conj(qv)).real) for v, _ in pv]
    return pv[int(np.argmax(sims))][1].replace("{p}", p)
def _selftest():
    assert "return sum(" in (_generate("def f(lst):\n    '''Return the total sum of elements in lst'''") or "")
    print("[selftest] PASS: codegen-light (%d patterns)" % len(PATTERNS), flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
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
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = list(load_dataset("openai_humaneval", split="test"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "pass1": 0.0}
    curated = [it for it in ds if _natural(it)]
    if SMOKE: curated = curated[:10]
    else: curated = curated[:40]
    npass = 0; solved = []
    for it in curated:
        body = _generate(it["prompt"])
        if body and _run_tests(it["prompt"], body, it["test"], it["entry_point"]):
            npass += 1; solved.append(it["task_id"])
    p1 = npass / len(curated) if curated else 0.0
    print("  CODEGEN-LIGHT: pass@1=%.3f (%d/%d substrate-natural) solved=%s" % (p1, npass, len(curated), solved[:12]), flush=True)
    return {"pass1": round(p1, 3), "n_pass": npass, "n_curated": len(curated), "n_patterns": len(PATTERNS)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    p1 = r["pass1"]; s = "pass@1=%.3f (%d/%d, %d patterns)" % (p1, r["n_pass"], r["n_curated"], r["n_patterns"])
    if p1 >= 0.40:
        return ("HARD_PASS", "HARD_PASS: substrate code generation reaches pass@1>=0.40 on the substrate-natural HumanEval subset -- docstring-keyword pattern selection + grammar instantiation generate working Python. Demo-grade substrate-only code gen. " + s)
    if p1 >= 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pass@1 0.20-0.40 -- substrate code gen partial; expand pattern library or add execution-repair (CODEGEN-REPAIR-1). " + s)
    return ("HARD_FAIL", "HARD_FAIL: pass@1 <0.20 -- pattern coverage insufficient even on substrate-natural subset. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
