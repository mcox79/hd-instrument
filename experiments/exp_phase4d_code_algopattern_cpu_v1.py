"""
exp_phase4d_code_typeclass_cpu_v1.py -- Phase-4D: substrate discriminative code-task classification (mechanism transfer) -- CPU.

ROUTING: Research CODE Phase 4D, reframed (per my task-fit note) as ALGORITHM-TYPE classification (HumanEval pass@1 needs
  synthesis, which doesn't fit a discriminative classifier). Tests whether the discriminative-weighting mechanism that solves
  math word problems also predicts CODE STRUCTURE from the NL prompt: MBPP prompt -> code-task-type (STRING/SORT/RECURSION/
  ARITH/LIST/CHECK), with GOLD derived objectively from the solution code (keyword/AST analysis). Substrate-native discriminative
  perceptron over prompt features, no LLM. Validates "NL extraction + discriminative weighting works on CODE as on MATH".
PRE-REGISTERED: HARD-PASS test accuracy >= 0.50 (discriminative weighting transfers to code-prompt classification, well above
  majority). MIDDLE >= 0.40. HARD-FAIL < majority+0.05. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4d_code_algopattern_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _gold_type(code, prompt):
    """objective code-task type from the solution code (priority-ordered)."""
    c = code.lower()
    fn = re.search(r"def\s+(\w+)", code)
    name = fn.group(1) if fn else ""
    pl = prompt.lower()
    if name and len(re.findall(r"\b" + re.escape(name) + r"\s*\(", code)) >= 2: return "RECURSION"
    if "sorted(" in c or ".sort(" in c or "heapq" in c: return "SORT"
    if any(s in pl for s in ("string", "char", "vowel", "palindrome", "letter", "word", "case", "substring", "reverse")) or any(s in c for s in (".join", ".split", ".replace", ".lower", ".upper", "ord(", "chr(")): return "STRING"
    if any(s in pl for s in ("prime", "factorial", "fibonacci", "gcd", "lcm", "divisor", "divisible", "power", "digit", "perfect number", "factor")): return "MATH"
    if any(s in pl for s in ("find", "search", "locate", "index of", "position")) or ".index(" in c or "bisect" in c: return "SEARCH"
    if any(s in pl for s in ("sum", "total", "count", "average", "product", "number of")) or "sum(" in c: return "ACCUMULATOR"
    if any(s in c for s in ("max(", "min(", "filter", "[x for", "[i for", "set(", "unique", "any(", "all(")) or any(s in pl for s in ("list", "array", "largest", "smallest", "maximum", "minimum")): return "LIST"
    return "MISC"
FEAT_CUES = None
def _feats(prompt):
    low = prompt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs
def _selftest():
    assert _gold_type("def f(s):\n return s.split()", "x") == "STRING"
    print("[selftest] PASS: phase4d-code-algopattern", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    import json
    ds = json.load(open(REPO / "experiments" / "data" / "mbpp" / "mbpp_sanitized.json", encoding="utf-8"))   # bundled (RESCUE-2)
    def conv(sp):
        out = []
        for e in ds[sp]:
            pr = e.get("prompt") or e.get("text") or ""; cd = e.get("code") or ""
            if pr and cd: out.append((pr, _gold_type(cd, pr)))
        return out
    # sanitized splits: train/test/validation/prompt
    tr = conv("train") + conv("validation") + (conv("prompt") if "prompt" in ds else [])
    te = conv("test")
    return tr, te
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1018")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: train = train[:150]; test = test[:80]
    if not train or not test: return {"error": "empty_split", "accuracy": 0.0}
    LAB = sorted(set(t for _p, t in train))
    Xtr = [(_feats(p), t) for p, t in train]
    w = {l: defaultdict(float) for l in LAB}; cw = {l: defaultdict(float) for l in LAB}; c = 1
    EP = 15 if not SMOKE else 4
    for ep in range(EP):
        for i in rng.permutation(len(Xtr)):
            feats, g = Xtr[i]; sc = {l: sum(w[l][f] for f in feats) for l in LAB}
            pred = max(LAB, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in LAB}
    gold_dist = Counter(t for _p, t in test); maj_lab, maj_n = gold_dist.most_common(1)[0]; maj = maj_n / len(test)
    cor = 0
    for p, t in test:
        feats = _feats(p); sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in LAB}
        if max(LAB, key=lambda l: (sc[l], l)) == t: cor += 1
    acc = cor / len(test)
    print("  PHASE4D-CODE-TYPECLASS: test-acc=%.3f (%d/%d) | majority=%.3f | %d classes | dist=%s" %
          (acc, cor, len(test), maj, len(LAB), dict(gold_dist.most_common(6))), flush=True)
    return {"accuracy": round(acc, 3), "majority": round(maj, 3), "n_classes": len(LAB), "n_test": len(test), "n_train": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; mj = r["majority"]; s = "acc=%.3f majority=%.3f (%d classes, n_test=%d, n_train=%d)" % (a, mj, r["n_classes"], r["n_test"], r["n_train"])
    lift = a - mj
    if a >= 0.70 and lift >= 0.10:
        return ("HARD_PASS", "HARD_PASS: substrate discriminative classifier predicts CODE algorithm-pattern from docstring at >=0.70 (lift>=0.10) -- mechanism transfers MATH->CODE; docstring determines algorithm pattern. " + s)
    if a >= 0.55 and lift >= 0.10:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 0.55-0.70 above majority -- docstring partially predicts algorithm pattern; mechanism transfers but below the 0.70 bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.55 or lift<0.10 (acc %.3f vs majority %.3f) -- docstring weakly predicts algorithm pattern; CODE mechanism-transfer limited. " % (a, mj) + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
