"""
exp_humaneval_structural_cpu_v1.py -- HumanEval (n=164) substrate structural generator -- CPU.

ROUTING: Research WAVE2 Tier-1 (HumanEval Cell 1, structural). Substrate is the GENERATOR. Pipeline: parse each problem's
  signature + docstring keywords -> encode as a substrate query (bundle of keyword phasors) -> retrieve the nearest Python
  IDIOM from a substrate-indexed idiom library (each idiom = keyword-signature bundle + a body-template) -> instantiate the
  body with the problem's parameter names -> subprocess-execute against the canonical tests. pass@1 = fraction passing all
  tests. This is a GENUINE first-pass substrate-retrieval generator (honest baseline; not a stub). Substrate-only. N=8192.
PRE-REGISTERED: HARD-PASS pass@1 >= 0.30. HP-GATE >= 0.15 (small-LLM-baseline). MIDDLE >= 0.05. HARD-FAIL < 0.05.
  UNKNOWN if dataset load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re, tempfile, subprocess, textwrap
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "humaneval_structural_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
# ---- substrate token codebook (lazy, keyword -> phasor) ----
_BOOK: Dict[str, np.ndarray] = {}
_RNG = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "990")))
def _tok(w):
    if w not in _BOOK:
        ang = (_RNG.random(N) * 2 - 1) * math.pi; _BOOK[w] = np.exp(1j * ang).astype(np.complex64)
    return _BOOK[w]
def _bundle(words):
    v = np.zeros(N, dtype=np.complex64)
    for w in words:
        v = v + _tok(w)
    n = np.abs(v); n[n == 0] = 1; return (v / n).astype(np.complex64)
def _kw(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2]
# ---- idiom library: (trigger keywords, body builder given param name p) ----
IDIOMS: List[Tuple[List[str], str]] = [
    (["sum", "total", "add", "elements"], "    return sum({p})"),
    (["maximum", "largest", "max", "biggest"], "    return max({p})"),
    (["minimum", "smallest", "min"], "    return min({p})"),
    (["length", "number", "count", "many"], "    return len({p})"),
    (["sorted", "sort", "order", "ascending"], "    return sorted({p})"),
    (["reverse", "reversed", "backwards"], "    return {p}[::-1]"),
    (["even", "divisible", "two"], "    return [x for x in {p} if x % 2 == 0]"),
    (["odd"], "    return [x for x in {p} if x % 2 == 1]"),
    (["positive", "greater", "than", "zero"], "    return [x for x in {p} if x > 0]"),
    (["unique", "distinct", "remove", "duplicates"], "    return sorted(set({p}))"),
    (["uppercase", "upper", "capital"], "    return {p}.upper()"),
    (["lowercase", "lower"], "    return {p}.lower()"),
    (["absolute", "abs"], "    return abs({p})"),
    (["product", "multiply", "multiplied"], "    r = 1\n    for x in {p}:\n        r *= x\n    return r"),
    (["average", "mean"], "    return sum({p}) / len({p})"),
    (["square", "squared"], "    return {p} * {p}"),
    (["concatenate", "join", "concatenation"], "    return ''.join({p})"),
    (["string", "characters", "count"], "    return len({p})"),
    (["round", "rounded"], "    return round({p})"),
    (["factorial"], "    r = 1\n    for i in range(1, {p} + 1):\n        r *= i\n    return r"),
]
_IDIOM_VEC = None
def _idiom_vecs():
    global _IDIOM_VEC
    if _IDIOM_VEC is None:
        _IDIOM_VEC = [(_bundle(kws), body) for kws, body in IDIOMS]
    return _IDIOM_VEC
def _first_param(sig):
    m = re.search(r"def\s+\w+\s*\(([^)]*)\)", sig)
    if not m or not m.group(1).strip():
        return None
    return m.group(1).split(",")[0].split(":")[0].split("=")[0].strip()
def _generate(prompt):
    """Substrate-retrieve the nearest idiom for the problem and instantiate its body."""
    p = _first_param(prompt)
    if p is None:
        return None
    qv = _bundle(_kw(prompt))
    iv = _idiom_vecs()
    sims = [float((v @ np.conj(qv)).real) for v, _ in iv]
    body = iv[int(np.argmax(sims))][1]
    return body.replace("{p}", p)
def _selftest():
    assert _first_param("def f(lst):\n  pass") == "lst"
    assert "return sum(" in (_generate("def f(lst):\n    '''return the sum of all elements in lst'''") or "")
    print("[selftest] PASS: humaneval-structural", flush=True)
def _run_tests(prompt, body, test, entry):
    src = prompt + "\n" + body + "\n\n" + test + "\n\ncheck(%s)\n" % entry
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(src); path = f.name
    try:
        p = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=10)
        return p.returncode == 0
    except Exception:
        return False
    finally:
        try: os.unlink(path)
        except Exception: pass
def run() -> Dict:
    try:
        from datasets import load_dataset
        ds = load_dataset("openai_humaneval", split="test")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "pass1": 0.0}
    items = list(ds)
    if SMOKE:
        items = items[:20]
    npass = 0; ntot = 0; solved = []
    for it in items:
        body = _generate(it["prompt"])
        ok = bool(body) and _run_tests(it["prompt"], body, it["test"], it["entry_point"])
        npass += int(ok); ntot += 1
        if ok: solved.append(it["task_id"])
    p1 = npass / ntot if ntot else 0.0
    print("  HUMANEVAL-STRUCTURAL pass@1=%.3f (%d/%d) solved=%s" % (p1, npass, ntot, solved[:12]), flush=True)
    return {"pass1": round(p1, 3), "n_pass": npass, "n_total": ntot, "n_idioms": len(IDIOMS)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    p1 = r["pass1"]; s = "pass@1=%.3f (%d/%d, %d idioms)" % (p1, r["n_pass"], r["n_total"], r["n_idioms"])
    if p1 >= 0.30:
        return ("HARD_PASS", "HARD_PASS: substrate structural generator solves HumanEval at pass@1>=0.30 -- beats small-LLM baseline. " + s)
    if p1 >= 0.15:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pass@1 0.15-0.30 (meets small-LLM baseline gate; below categorical). " + s)
    if p1 >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pass@1 0.05-0.15 -- first-pass idiom-retrieval generator establishes a baseline; needs the full op-composition pipeline for the >=0.15 claim. " + s)
    return ("HARD_FAIL", "HARD_FAIL: pass@1 <0.05 -- idiom-retrieval generator is too limited; full Tier1-4 op-composition generator required. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
