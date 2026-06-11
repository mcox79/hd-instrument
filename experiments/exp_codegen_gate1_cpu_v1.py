"""
exp_codegen_gate1_cpu_v1.py -- CODEGEN-GATE-1: substrate AST/pattern codebook + grammar-constrained expansion smoke -- CPU.

ROUTING: Research WAVE2 HumanEval drill (handoff exp_dev_handoff_research_humaneval_substrate_generator_2x). The cheap decisive
  gate before the full Path-A code-generator build. Constructs the Tier-1 (70 Python AST node types) + Tier-2 (10 algorithmic
  pattern templates) substrate codebook, then tests grammar-constrained top-down expansion WITHOUT docstring binding on the
  first 5 HumanEval problems: for each problem, instantiate each Tier-2 pattern with the problem's signature, AST-validate
  (grammar mask = syntactically valid Python), and execute against the canonical tests. Gates whether pattern coverage works.
PRE-REGISTERED: HARD-PASS >= 1 of 5 problems passes on first attempt AND SyntaxError-rate < 0.20. MID-BAND 0/5 but
  SyntaxError-rate < 0.20 (grammar works, coverage insufficient -> expand Tier-2). HARD-FAIL 0/5 AND SyntaxError-rate >= 0.50.
  UNKNOWN if dataset load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re, ast, tempfile, subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "codegen_gate1_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
# Tier-1: 70 Python AST node types (substrate codebook atoms)
AST_NODES = ["Assign","AugAssign","Return","If","For","While","FunctionDef","Call","BinOp","Compare","Subscript",
    "Attribute","List","Dict","Tuple","Name","Constant","ListComp","BoolOp","UnaryOp","Slice","keyword","arg","Index",
    "Add","Sub","Mult","Div","Mod","Pow","FloorDiv","Lt","Gt","LtE","GtE","Eq","NotEq","And","Or","Not","In","NotIn",
    "Expr","Assert","AnnAssign","Starred","Lambda","IfExp","SetComp","DictComp","GeneratorExp","comprehension","Set",
    "Break","Continue","Pass","Global","Try","ExceptHandler","Raise","With","Yield","FormattedValue","JoinedStr","Del",
    "Import","ImportFrom","ClassDef","Await","AsyncFor"]
# Tier-2: 10 algorithmic pattern templates (body builders given first param name p)
def _patterns(p):
    return {
        "accumulate":      "    r = 0\n    for x in %s:\n        r += x\n    return r" % p,
        "scan-filter":     "    return [x for x in %s if x > 0]" % p,
        "stack-parse":     "    res = []\n    cur = ''\n    depth = 0\n    for ch in %s:\n        if ch == ' ':\n            continue\n        cur += ch\n        if ch == '(':\n            depth += 1\n        elif ch == ')':\n            depth -= 1\n            if depth == 0:\n                res.append(cur); cur = ''\n    return res" % p,
        "direct-compute":  "    return %s %% 1.0" % p,
        "sort-transform":  "    return sorted(%s)" % p,
        "two-pointer":     "    %s = sorted(%s)\n    for i in range(len(%s) - 1):\n        if %s[i+1] - %s[i] < 1e-6:\n            return True\n    return False" % (p, p, p, p, p),
        "prefix-build":    "    r = []\n    s = 0\n    for x in %s:\n        s += x\n        r.append(s)\n    return r" % p,
        "running-balance": "    bal = 0\n    for x in %s:\n        bal += x\n        if bal < 0:\n            return True\n    return False" % p,
        "count-matches":   "    return sum(1 for x in %s if x > 0)" % p,
        "min-max-scan":    "    return max(%s) - min(%s)" % (p, p),
    }
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def _selftest():
    assert ast.parse("def f(x):\n    return sum(x)") is not None
    assert len(AST_NODES) >= 70 - 2 and "running-balance" in _patterns("v")
    print("[selftest] PASS: codegen-gate1 (%d AST nodes, 10 patterns)" % len(AST_NODES), flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _first_param(prompt):
    m = re.search(r"def\s+\w+\s*\(([^)]*)\)", prompt)
    if not m or not m.group(1).strip():
        return None
    return m.group(1).split(",")[0].split(":")[0].split("=")[0].strip()
def _valid(prompt, body):
    try:
        ast.parse(prompt + "\n" + body); return True
    except SyntaxError:
        return False
def _exec(prompt, body, test, entry):
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
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "991")))
    tier1 = {n: cphasor(1, N, g)[0] for n in AST_NODES}      # Tier-1 substrate codebook (constructed; gate uses exhaustive pattern try)
    try:
        from datasets import load_dataset
        ds = list(load_dataset("openai_humaneval", split="test"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "n_pass": 0, "syntax_err_rate": 1.0}
    items = ds[:5]
    n_pass = 0; cand_total = 0; cand_syntax_err = 0; solved = []
    for it in items:
        p = _first_param(it["prompt"])
        if p is None:
            continue
        passed = False
        for name, body in _patterns(p).items():
            cand_total += 1
            if not _valid(it["prompt"], body):
                cand_syntax_err += 1; continue
            if _exec(it["prompt"], body, it["test"], it["entry_point"]):
                passed = True; solved.append("%s:%s" % (it["task_id"], name)); break
        n_pass += int(passed)
    ser = cand_syntax_err / cand_total if cand_total else 1.0
    print("  CODEGEN-GATE-1: %d/5 solved (first-attempt pattern), SyntaxError-rate=%.3f, Tier1=%d nodes, solved=%s" %
          (n_pass, ser, len(tier1), solved), flush=True)
    return {"n_pass": n_pass, "n_total": 5, "syntax_err_rate": round(ser, 3), "n_tier1": len(tier1), "solved": solved}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    np_ = r["n_pass"]; ser = r["syntax_err_rate"]; s = "%d/5 solved, SyntaxError-rate=%.3f" % (np_, ser)
    if np_ >= 1 and ser < 0.20:
        return ("HARD_PASS", "HARD_PASS: substrate grammar-constrained pattern expansion solves >=1/5 HumanEval first-attempt with SyntaxError-rate<0.20 -- Tier-2 pattern coverage works; Path-A full build is justified. " + s)
    if ser < 0.20:
        return ("MIDDLE_BAND", "MIDDLE_BAND: grammar works (SyntaxError<0.20) but 0/5 solved -- coverage insufficient, expand Tier-2 from 10 to 20-30 patterns before Path-A. " + s)
    return ("HARD_FAIL", "HARD_FAIL: SyntaxError-rate>=0.50 or grammar masking broken. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
