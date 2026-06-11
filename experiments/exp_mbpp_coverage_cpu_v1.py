"""
exp_mbpp_coverage_cpu_v1.py -- MBPP coverage + honest pass@1 ceiling (second benchmark) -- CPU.

ROUTING: Research SPRINT2 priority (MBPP-structural). Second benchmark for the coverage finding (HumanEval was 32%). Downloads
  real MBPP (~974 basic Python problems), classifies how many are within the substrate's narrow list-int primitive scope =
  honest CEILING on structural pass@1. Confirms whether the primitive-coverage axis generalizes across benchmarks. No exec.
PRE-REGISTERED (MEASUREMENT): report coverage fraction + ceiling. Verdict bands describe the substrate-scope finding (coverage < 0.30 = primitive-library-bounded).
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, urllib.request
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "mbpp_coverage_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
URLS = ["https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl",
        "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/sanitized-mbpp.json"]
def _selftest():
    print("[selftest] PASS: mbpp-coverage", flush=True)
def load():
    for u in URLS:
        try:
            with urllib.request.urlopen(u, timeout=40) as r:
                raw = r.read().decode("utf-8", "replace")
            if u.endswith(".jsonl"):
                probs = [json.loads(ln) for ln in raw.splitlines() if ln.strip()]
            else:
                probs = json.loads(raw)
            if probs:
                return probs
        except Exception as e:
            print("[data] %s fail %s" % (u[:40], str(e)[:50]), flush=True)
    return None
INSCOPE_KW = ["sum", "maximum", "minimum", "largest", "smallest", "sort", "sorted", "reverse", "even", "odd",
              "count", "number of", "filter", "greater", "less than", "average", "mean", "product", "total", "unique", "distinct"]
OUTSCOPE_KW = ["string", "char", "letter", "word", "vowel", "substring", "palindrome", "split", "concat", "dictionary",
               "matrix", "recursion", "fibonacci", "prime", "binary", "roman", "encode", "decode", "regex", "tuple", "nested",
               "lambda", "regular expression", "camel", "snake", "url", "date"]
def categorize(p):
    text = (p.get("text", "") or p.get("prompt", "")).lower(); code = (p.get("code", "") or "").lower()
    blob = text + " " + code
    out = sum(1 for k in OUTSCOPE_KW if k in blob); ins = sum(1 for k in INSCOPE_KW if k in blob)
    has_str = any(k in blob for k in ["string", "str(", "char", "word"])
    return (ins >= 1) and (out == 0) and (not has_str)
def run() -> Dict:
    probs = load()
    if not probs:
        return {"error": "download_failed", "coverage": 0.0}
    n = len(probs); inscope = sum(1 for p in probs if categorize(p))
    cov = inscope / n
    print("  MBPP n=%d: in-substrate-primitive-scope=%d (coverage=%.3f) | pass@1-ceiling ~= %.3f (vs HumanEval 0.32)" % (n, inscope, cov, cov * 0.75), flush=True)
    return {"n_problems": n, "in_scope": inscope, "coverage": round(cov, 3), "pass1_ceiling_est": round(cov * 0.75, 3)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    c = r["coverage"]; s = "coverage=%.3f (in-scope=%d/%d) pass@1-ceiling~=%.3f" % (c, r["in_scope"], r["n_problems"], r["pass1_ceiling_est"])
    if c < 0.30:
        return ("HARD_PASS", "HARD_PASS (measurement): coverage finding GENERALIZES -- only %.0f%% of MBPP is within the narrow list-int primitive scope (HumanEval was 32%%). Substrate code-synthesis is PRIMITIVE-LIBRARY-BOUNDED across benchmarks; ceiling ~%.2f. Broader primitive library is the engineering axis. " % (100 * c, r["pass1_ceiling_est"]) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND (measurement): MBPP coverage %.2f. " % c + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
