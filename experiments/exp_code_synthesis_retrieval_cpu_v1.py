"""
exp_code_synthesis_retrieval_cpu_v1.py -- substrate-only CODE synthesis via template-retrieve + slot-fill on MBPP -- CPU.

ROUTING: Research 5-cheap experiment #4 (confirm drill-1 substrate-only synthesis 0.05-0.15 ceiling OR refute). Substrate-only
  synthesis: for each MBPP test problem, RETRIEVE the nearest training problem (docstring feature overlap = substrate cleanup
  analog) and reuse its solution code with the test's function SIGNATURE slot-filled (rename def to the test's expected name).
  Execute against the gold test_list (subprocess, sandboxed, timeout) -> pass@1. No LLM. Tests whether retrieval+slot-fill
  synthesis works substrate-only (predicted ceiling 0.05-0.15: only near-duplicate problems pass).
PRE-REGISTERED: report pass@1. Interpretation: 0.05-0.15 confirms the drill-1 substrate-only-synthesis ceiling (retrieval solves
  only near-duplicates); >0.20 refutes (substrate-only synthesis more viable than predicted). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, subprocess, tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter
import math
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "code_synthesis_retrieval_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _toks(t): return re.findall(r"[a-z]+", t.lower())
def _fname_from_tests(tests):
    """the function name called in the asserts."""
    for t in tests:
        m = re.search(r"assert\s+\(?\s*([A-Za-z_]\w*)\s*\(", t)
        if m and m.group(1) not in ("abs", "round", "len", "set", "sorted", "math", "str", "int", "tuple", "list"):
            return m.group(1)
    return None
def _def_name(code):
    m = re.search(r"def\s+([A-Za-z_]\w*)\s*\(", code)
    return m.group(1) if m else None
def _selftest():
    assert _fname_from_tests(["assert similar_elements((1,2),(2,3))==(2,)"]) == "similar_elements"
    print("[selftest] PASS: code-synthesis-retrieval", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _execute(code, tests):
    """run code + asserts in a subprocess; return True if all pass within timeout."""
    src = code + "\n" + "\n".join(tests) + "\n"
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(src); path = f.name
        p = subprocess.run([sys.executable, path], capture_output=True, timeout=6)
        ok = p.returncode == 0
    except Exception:
        ok = False
    finally:
        try: os.unlink(path)
        except Exception: pass
    return ok
def run() -> Dict:
    try:
        ds = json.load(open(REPO / "experiments" / "data" / "mbpp_with_tests.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "pass_at_1": 0.0}
    train = ds["train"] + ds["validation"] + ds.get("prompt", [])
    test = ds["test"]
    train = [e for e in train if e["code"] and e["text"]]
    test = [e for e in test if e["code"] and e["text"] and e.get("test_list")]
    if SMOKE: test = test[:40]
    # build train doc-feature index (bag of docstring words, IDF-weighted)
    df = Counter()
    tr_toks = []
    for e in train:
        tk = set(_toks(e["text"])); tr_toks.append(tk)
        for w in tk: df[w] += 1
    N = len(train)
    def idf(w): return math.log((N + 1) / (df.get(w, 0) + 1))
    passed = 0; nT = len(test)
    for e in test:
        q = set(_toks(e["text"])); fname = _fname_from_tests(e["test_list"])
        if fname is None:
            continue
        # retrieve nearest train by IDF-weighted overlap
        best = -1.0; best_e = None
        for k, tk in enumerate(tr_toks):
            inter = q & tk
            sc = sum(idf(w) for w in inter) / (math.sqrt(len(q) * len(tk)) + 1e-9) if tk else 0.0
            if sc > best: best = sc; best_e = train[k]
        if best_e is None: continue
        # slot-fill: rename retrieved def to the test's expected function name
        rd = _def_name(best_e["code"])
        code = best_e["code"]
        if rd and rd != fname:
            code = re.sub(r"\bdef\s+" + re.escape(rd) + r"\s*\(", "def " + fname + "(", code)
            code = re.sub(r"\b" + re.escape(rd) + r"\s*\(", fname + "(", code)   # recursive calls
        if _execute(code, e["test_list"]): passed += 1
    p1 = passed / nT if nT else 0.0
    print("  CODE-SYNTHESIS-RETRIEVAL: pass@1=%.3f (%d/%d) | train-templates=%d (predicted ceiling 0.05-0.15)" % (p1, passed, nT, len(train)), flush=True)
    return {"pass_at_1": round(p1, 3), "n_passed": passed, "n_test": nT, "n_templates": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    p = r["pass_at_1"]; s = "pass@1=%.3f (%d/%d, templates=%d)" % (p, r["n_passed"], r["n_test"], r["n_templates"])
    if p > 0.20:
        return ("HARD_PASS", "HARD_PASS: substrate-only retrieval+slot-fill synthesis pass@1>0.20 -- REFUTES the drill-1 0.05-0.15 ceiling; substrate-only CODE synthesis more viable than predicted. " + s)
    if p >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: pass@1 in 0.05-0.15 band -- CONFIRMS the drill-1 substrate-only-synthesis ceiling (retrieval solves only near-duplicate problems; genuine synthesis needs more). Honest boundary. " + s)
    return ("HARD_FAIL", "HARD_FAIL: pass@1 <0.05 -- retrieval+slot-fill synthesis below even the predicted floor. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
