"""
exp_phase4_v25_gated_cpu_v1.py -- Phase-4 v2.5: cleanup-margin confidence-gated slot-binding -- CPU.

ROUTING: Research PHASE4_V25_CONFIDENCE_GATED_RESCUE (1st priority, 2hr, decisive). The v2 regression (anchored 0.041 < v1
  positional 0.050) was UNGATED heuristic application (5-literature convergence: Chow reject-option, Cortes-Mohri abstention,
  Gigerenzer, basal-ganglia gating, ACC conflict-monitoring). Fix: use substrate cleanup-margin (schema-retrieval top1-top2)
  as native confidence -> HIGH margin engages anchored binding; LOW margin falls back to positional (v1). No external
  calibrator -- the substrate's own convergence margin IS the gating signal. Same 5-schema set as v1/v2 to isolate gating.
PRE-REGISTERED: HARD-PASS v2.5 >= v1 (0.050) AND >= v2 (0.041) [gating fix validated]. MIDDLE in [0.041, 0.050). HARD-FAIL < 0.041.
  Reports gating split. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math, re
from pathlib import Path
from typing import Dict, List, Tuple
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4_v25_gated_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
SCHEMA_KW = {
    "rate_motion": ["rate", "speed", "travels", "mph", "miles", "per", "hour", "distance", "fast", "drives"],
    "percent_of": ["percent", "of"],
    "work_together": ["together", "work", "job", "complete", "hours", "finish"],
    "interest": ["interest", "principal", "invested", "annual"],
    "direct_arith": ["sum", "difference", "product", "total", "evaluate", "simplify", "compute"],
}
NAMES = list(SCHEMA_KW.keys())
def _tok(t): return re.findall(r"[a-z]+", t.lower())
def _boxed(sol):
    i = sol.find("oxed{")
    if i < 0: return None
    j = i + 5; dd = 1; out = []
    while j < len(sol) and dd > 0:
        c = sol[j]
        if c == "{": dd += 1
        elif c == "}": dd -= 1
        if dd > 0: out.append(c)
        j += 1
    return "".join(out)
def _frac(x):
    try:
        x = (x or "").replace("$", "").replace(",", "").replace("\\%", "").strip()
        if re.fullmatch(r"-?\d+(\.\d+)?", x): return Fraction(x).limit_denominator(10**6)
        if re.fullmatch(r"-?\d+/\d+", x): return Fraction(x)
        return None
    except Exception: return None
def _nums(q): return [Fraction(n) for n in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.%])", q)]
def _anchored(q, cues):
    toks = q.lower().split(); best = None; bestd = 999
    for i, t in enumerate(toks):
        m = re.match(r"(\d+(?:\.\d+)?)", t)
        if not m: continue
        for j, u in enumerate(toks):
            if any(c in u for c in cues):
                d = abs(i - j)
                if d < bestd: bestd = d; best = Fraction(m.group(1))
    return best
def _selftest():
    assert _boxed("$\\boxed{7}$") == "7"
    print("[selftest] PASS: phase4-v25-gated", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1009")))
    try:
        from datasets import load_dataset
        probs = []
        for cfg in ["prealgebra", "algebra"]:
            ds = load_dataset("EleutherAI/hendrycks_math", cfg, split="test")
            probs += [x for x in ds if x.get("level") == "Level 1"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: probs = probs[:60]
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        return np.exp(1j * np.angle(v)).astype(np.complex64) if np.any(v) else v
    proto = np.stack([bundle(SCHEMA_KW[nm]) for nm in NAMES])
    def retrieve(q):
        v = bundle(_tok(q))
        if not np.any(v): return NAMES[0], 0.0
        sc = (proto @ np.conj(v)).real; order = np.argsort(-sc)
        margin = float(sc[order[0]] - sc[order[1]])   # substrate cleanup-margin = confidence
        return NAMES[order[0]], margin
    def solve(schema, q, anchored):
        pcts = re.findall(r"(\d+(?:\.\d+)?)\s*\\?%\s*of\s*(\d+(?:\.\d+)?)", q); nums = _nums(q); ql = q.lower()
        if schema == "percent_of" and pcts:
            vals = [Fraction(a) / 100 * Fraction(b) for a, b in pcts]
            if "difference" in ql and len(vals) >= 2: return abs(vals[0] - vals[1])
            return vals[0]
        if schema == "rate_motion":
            if anchored:
                rt = _anchored(q, ["mph", "speed", "rate", "mile", "km"]); tm = _anchored(q, ["hour", "minute", "time", "day"])
                if rt is not None and tm is not None: return rt * tm
            if len(nums) >= 2: return nums[0] * nums[1]
        if schema == "work_together" and len(nums) >= 2 and nums[0] != 0 and nums[1] != 0:
            return 1 / (1 / nums[0] + 1 / nums[1])
        if schema == "interest":
            if anchored:
                pr = _anchored(q, ["principal", "invest", "deposit"]); rr = _anchored(q, ["rate", "percent", "annual"])
                if pr is not None and rr is not None: return pr * rr / 100
            if len(nums) >= 2: return nums[0] * nums[1] / 100
        if schema == "direct_arith":
            expr = q
            expr = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", expr)
            expr = expr.replace("\\times", "*").replace("\\cdot", "*").replace("$", "").replace("^", "**")
            m = re.search(r"[-+]?[0-9][0-9\.\+\-\*\/\(\)\s]*[0-9\)]", expr)
            if m:
                try: return Fraction(eval(m.group(0), {"__builtins__": {}}, {})).limit_denominator(10**6)
                except Exception: return None
        return None
    # collect margins to set the gate threshold (median -> ~half anchored); also run pure-v1 and pure-v2 for the comparison
    rows = []
    for p in probs:
        gold = _frac(_boxed(p.get("solution", "")))
        if gold is None: continue
        sch, margin = retrieve(p["problem"]); rows.append((p["problem"], gold, sch, margin))
    margins = sorted(r[3] for r in rows); thresh = margins[len(margins) // 2] if margins else 0.0   # median gate
    def score(mode):  # mode: 'v1'(positional), 'v2'(anchored), 'gated'
        cor = 0
        for q, gold, sch, margin in rows:
            if mode == "v1": anc = False
            elif mode == "v2": anc = True
            else: anc = margin >= thresh                  # confidence-gated
            ans = solve(sch, q, anc)
            if ans is not None and ans == gold: cor += 1
        return cor / len(rows) if rows else 0.0
    a_v1 = score("v1"); a_v2 = score("v2"); a_gated = score("gated")
    n_anch = sum(1 for r in rows if r[3] >= thresh)
    print("  PHASE4-v2.5: gated=%.3f | v1(positional)=%.3f v2(anchored)=%.3f | thresh=%.3f anchored-frac=%.2f (n=%d)" %
          (a_gated, a_v1, a_v2, thresh, n_anch / len(rows) if rows else 0, len(rows)), flush=True)
    return {"accuracy": round(a_gated, 3), "v1": round(a_v1, 3), "v2": round(a_v2, 3), "anchored_frac": round(n_anch / len(rows), 3) if rows else 0.0, "n": len(rows)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "gated=%.3f (v1=%.3f v2=%.3f, anchored-frac=%.2f)" % (a, r["v1"], r["v2"], r["anchored_frac"])
    if a >= max(r["v1"], r["v2"]) and a >= 0.050:
        return ("HARD_PASS", "HARD_PASS: cleanup-margin confidence-gating >= both v1 and v2 -- substrate-native uncertainty quantification fixes the ungated-heuristic regression. Gate anchoring by schema cleanup-margin. " + s)
    if a >= r["v2"]:
        return ("MIDDLE_BAND", "MIDDLE_BAND: gating >= v2 but < v1 -- partial; threshold tuning or conformal calibration next. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gating < v2 -- cleanup-margin signal insufficient as a gate. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
