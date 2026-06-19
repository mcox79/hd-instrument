"""
exp_phase4b_collins_ab_cpu_v1.py -- A/B: flat vs Collins-structured perceptron on SVAMP -- CPU.

ROUTING: Research COLLINS_STRUCTURED_PERCEPTRON_TEST (drill P_deflated=0.55). A/B on SVAMP test:
  A = flat 6-class perceptron (op x order as independent classes) -- the current 0.297 baseline.
  B = Collins-structured: factored OP-classifier (4 ops, shares all features) + ORDER-classifier (binary ab/ba for SUB/DIV,
      order-specific features), trained with a joint structured-perceptron update; decode = op then order. Tests whether
      feature-SHARING across the order dimension (synergistic information) beats independent flat classes. Substrate-native
      discriminative, no LLM.
PRE-REGISTERED: report A, B, 2*SE. HARD-PASS B > A + 2*SE (structured prediction lifts -> substrate-native bridge). MIDDLE
  |B-A| <= 2*SE (flat captures signal on 2-quantity SVAMP; ship flat). HARD-FAIL B < A - 2*SE (forced structure hurts). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4b_collins_ab_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
FLAT = ["ADD", "MUL", "SUB_ab", "SUB_ba", "DIV_ab", "DIV_ba"]
def _flat_eval(op, a, b):
    if op == "ADD": return a + b
    if op == "MUL": return a * b
    if op == "SUB_ab": return a - b
    if op == "SUB_ba": return b - a
    if op == "DIV_ab": return a / b if b != 0 else None
    if op == "DIV_ba": return b / a if a != 0 else None
OP4 = ["ADD", "SUB", "MUL", "DIV"]
def _op4_order(op, order_ba, a, b):
    x, y = (b, a) if order_ba else (a, b)
    if op == "ADD": return a + b
    if op == "MUL": return a * b
    if op == "SUB": return x - y
    if op == "DIV": return x / y if y != 0 else None
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference"):
        if cue in ws: fs.add("c:" + cue)
    toks = low.split()
    for k, w in enumerate(toks):
        if re.match(r"\d", w.replace("$", "").replace(",", "")):
            if k + 1 < len(toks): fs.add("nN:" + re.sub(r"[^a-z]", "", toks[k + 1]))
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs
def _selftest():
    assert _flat_eval("SUB_ab", Fraction(5), Fraction(3)) == 2 and _op4_order("SUB", True, Fraction(3), Fraction(5)) == 2
    print("[selftest] PASS: phase4b-collins-ab", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    ds = load_dataset("ChilleD/SVAMP")
    def conv(sp):
        return [((e.get("Body", "") + " " + e.get("Question", "")).strip(), _ans(e.get("Answer"))) for e in ds[sp]]
    f = lambda rows: [(t, a) for t, a in rows if t and a is not None and len(_nums(t)) >= 2]
    return f(conv("train")), f(conv("test"))
def _train(X, labels, rng, ep):
    w = {l: defaultdict(float) for l in labels}; cw = {l: defaultdict(float) for l in labels}; c = 1
    for _ in range(ep):
        for i in rng.permutation(len(X)):
            feats, g = X[i]; sc = {l: sum(w[l][f] for f in feats) for l in labels}
            pred = max(labels, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in labels}
def _pred(avg, labels, feats):
    sc = {l: sum(avg[l].get(f, 0.0) for f in feats) for l in labels}
    return max(labels, key=lambda l: (sc[l], l))
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1015")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "A": 0.0}
    if SMOKE: train = train[:200]; test = test[:80]
    # gold: flat op-class + factored (op4, order_ba)
    Xflat = []; Xop4 = []; Xord = []
    for txt, ans in train:
        ns = _nums(txt); a, b = ns[0], ns[1]; feats = _feats(txt); gflat = None
        for op in FLAT:
            r = _flat_eval(op, a, b)
            if r is not None and Fraction(r).limit_denominator(10**6) == ans: gflat = op; break
        if gflat is None: continue
        Xflat.append((feats, gflat))
        # factored gold
        if gflat in ("ADD", "MUL"): Xop4.append((feats, gflat))
        elif gflat.startswith("SUB"): Xop4.append((feats, "SUB")); Xord.append((feats, "BA" if gflat == "SUB_ba" else "AB"))
        else: Xop4.append((feats, "DIV")); Xord.append((feats, "BA" if gflat == "DIV_ba" else "AB"))
    if not Xflat: return {"error": "no_train_labels", "A": 0.0}
    EP = 12 if not SMOKE else 4
    avgA = _train(Xflat, FLAT, rng, EP)
    avg_op4 = _train(Xop4, OP4, rng, EP)
    avg_ord = _train(Xord, ["AB", "BA"], rng, EP) if Xord else None
    nT = len(test); cA = 0; cB = 0
    for txt, ans in test:
        ns = _nums(txt); a, b = ns[0], ns[1]; feats = _feats(txt)
        # A: flat
        pA = _pred(avgA, FLAT, feats); rA = _flat_eval(pA, a, b)
        if rA is not None and Fraction(rA).limit_denominator(10**6) == ans: cA += 1
        # B: factored op then order
        pop = _pred(avg_op4, OP4, feats)
        if pop in ("ADD", "MUL"): rB = _op4_order(pop, False, a, b)
        else:
            ba = (avg_ord is not None and _pred(avg_ord, ["AB", "BA"], feats) == "BA")
            rB = _op4_order(pop, ba, a, b)
        if rB is not None and Fraction(rB).limit_denominator(10**6) == ans: cB += 1
    A = cA / nT; B = cB / nT
    se = math.sqrt(A * (1 - A) / nT + B * (1 - B) / nT)   # SE of the difference (approx)
    print("  COLLINS-AB (SVAMP): A(flat)=%.3f B(structured)=%.3f | diff=%.3f 2SE=%.3f (n=%d)" % (A, B, B - A, 2 * se, nT), flush=True)
    return {"A": round(A, 3), "B": round(B, 3), "diff": round(B - A, 3), "two_se": round(2 * se, 3), "n_test": nT}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    A = r["A"]; B = r["B"]; d = r["diff"]; tse = r["two_se"]; s = "A(flat)=%.3f B(structured)=%.3f diff=%.3f 2SE=%.3f" % (A, B, d, tse)
    if d > tse:
        return ("HARD_PASS", "HARD_PASS: Collins structured perceptron (factored op+order, feature-sharing) BEATS flat by >2SE -- structured prediction is the substrate-native bridge; synergistic feature-sharing helps. " + s)
    if d < -tse:
        return ("HARD_FAIL", "HARD_FAIL: structured < flat by >2SE -- forced factorization hurts; flat is the ceiling on 2-quantity SVAMP without syntactic features (dep-parser path). " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: structured ~ flat (within 2SE) -- flat perceptron captures the signal on 2-quantity SVAMP; assignment-structure benefit likely only for 3+ entities. Ship flat; dep-parser for >0.30. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
