"""
exp_asdiv_pp375_port_cpu_v1.py -- Path 8: port PP-375 multistep mechanism (op-sequence prediction + answer-consistency) to ASDiv -- CPU.

ROUTING: Research Path 8 (HIGHEST PRIORITY). PP-375 multistep_math is substrate-Tier-A 0.753 on MultiArith via: predict the
  OP-SEQUENCE (4 classes 1-op / 16 classes 2-op) from question features, applied over TEXT-ORDER numbers, with ANSWER-CONSISTENCY
  weak labels (gold op-seq = the one yielding the answer; no explicit gold ops). It SIDESTEPS operand selection (uses text-order
  numbers) -- the exact thing 7 prior mechanisms struggled with. NEVER applied to ASDiv. Tests whether the proven mechanism
  transfers (substrate-self-improvement: existing mechanism -> new capability) OR whether ASDiv's operand-selection need (numbers
  NOT in answer-text-order, unlike MultiArith) breaks the transfer.
  TWO variants per dataset: (A) FAITHFUL PP-375 text-order (first-2 / first-3 numbers, op-seq prediction, NO operand search);
  (B) +operand-search (predict op-seq, apply over ALL pairs/triples + plausibility verifier) = upper bound on the op-classifier.
  Bundled ASDiv. Substrate-discriminative, no LLM.
PRE-REGISTERED (Research gate, on ASDiv-1op): HARD-PASS >= 0.45 (PP-375 transfers). MIDDLE 0.40-0.45. HARD-FAIL < 0.40
  (mechanism doesn't transfer; ASDiv operand-selection breaks text-order). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, itertools
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_pp375_port_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}
OPS = list(BIN.keys())
PAIRS = [(o1, o2) for o1 in OPS for o2 in OPS]
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}


def _nums(t):
    out = []
    toks = t.lower().split()
    for w in toks:
        ww = w.replace("$", "").replace(",", "").rstrip("?.,")
        if re.match(r"^\d+(?:\.\d+)?$", ww):
            try: out.append(Fraction(ww))
            except Exception: pass
        elif ww in _WORDNUM: out.append(Fraction(_WORDNUM[ww]))
    return out


def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    try: return Fraction(m.group(0)).limit_denominator(10**6) if m else None
    except Exception: return None


def _ev1(o, a, b): return BIN[o](a, b)
def _ev2(a, b, c, o1, o2):
    t = BIN[o1](a, b)
    return None if t is None else BIN[o2](t, c)


def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share",
                "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest",
                "difference", "twice", "double", "then", "after", "remaining"):
        if cue in ws: fs.add("c:" + cue)
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs


def _plaus(r, cq): return r is not None and r >= 0 and r <= 100000 and (not cq or r.denominator == 1)
def _cq(t): return bool(re.search(r"how many", t.lower()))


def _selftest():
    assert _ev2(Fraction(64), Fraction(36), Fraction(4), "-", "/") == 7 and _nums("two dogs and 3 cats")[0] == 2
    print("[selftest] PASS: asdiv-pp375-port", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_clf(X, labels, rng, ep):
    w = {l: defaultdict(float) for l in labels}; cw = {l: defaultdict(float) for l in labels}; c = 1
    for _ in range(ep):
        for i in rng.permutation(len(X)):
            feats, g = X[i]; sc = {l: sum(w[l][f] for f in feats) for l in labels}
            pred = max(labels, key=lambda l: (sc[l], l))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    return {l: {f: w[l][f] - cw[l][f] / c for f in w[l]} for l in labels}


def _pred(avg, labels, feats): return max(labels, key=lambda l: (sum(avg[l].get(f, 0.0) for f in feats), l))


def _solve(train, test_full, search, seed):
    """search=False: faithful PP-375 text-order (first-2/first-3). search=True: predict op-seq, apply over all pairs/triples+verifier."""
    rng = np.random.default_rng(seed)
    X1 = []; X2 = []
    for txt, ans, oc in train:
        ns = _nums(txt)
        if len(ns) >= 2:
            for a, b in itertools.permutations(ns[:4] if search else ns[:2], 2):
                hit = next((o for o in OPS if _ev1(o, a, b) == ans), None)
                if hit: X1.append((_feats(txt), hit)); break
        if len(ns) >= 3:
            done = False
            for a, b, c in itertools.permutations(ns[:5] if search else ns[:3], 3):
                for op in PAIRS:
                    if _ev2(a, b, c, op[0], op[1]) == ans: X2.append((_feats(txt), op)); done = True; break
                if done: break
    if not X1: return {}, {}
    EP = 12 if not SMOKE else 4
    a1 = _train_clf(X1, OPS, rng, EP); a2 = _train_clf(X2, PAIRS, rng, EP) if X2 else None
    flags = [0] * len(test_full)
    for ti, (txt, ans, oc) in enumerate(test_full):
        ns = _nums(txt); cq = _cq(txt)
        if len(ns) < 2: continue
        feats = _feats(txt); pred_ans = None
        o1 = _pred(a1, OPS, feats)
        if search:
            cands = [(k1 + k2, _ev1(o1, ns[k1], ns[k2])) for k1, k2 in itertools.permutations(range(len(ns)), 2)]
            cands = [(p, r) for p, r in cands if _plaus(r, cq)]
            if cands: pred_ans = max(cands, key=lambda x: x[0])[1]
        else:
            r = _ev1(o1, ns[0], ns[1])
            if _plaus(r, cq): pred_ans = r
        if pred_ans is None and a2 is not None and len(ns) >= 3:
            op2 = _pred(a2, PAIRS, feats)
            if search:
                c2 = [(k1 + k2 + k3, _ev2(ns[k1], ns[k2], ns[k3], op2[0], op2[1])) for k1, k2, k3 in itertools.permutations(range(min(len(ns), 5)), 3)]
                c2 = [(p, r) for p, r in c2 if _plaus(r, cq)]
                if c2: pred_ans = max(c2, key=lambda x: x[0])[1]
            else:
                r = _ev2(ns[0], ns[1], ns[2], op2[0], op2[1])
                if _plaus(r, cq): pred_ans = r
        if pred_ans is not None and pred_ans == ans: flags[ti] = 1
    overall = sum(flags) / len(test_full) if test_full else 0.0
    by = {}
    for o in (1, 2, 3):
        ix = [i for i, (_t, _a, c) in enumerate(test_full) if c == o]
        if ix: by[o] = round(sum(flags[i] for i in ix) / len(ix), 4)
    return {"overall": round(overall, 4)}, by


def _load():
    import json
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8")); items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f: continue
        a = _ans(e.get("answer"))
        if a is None: continue
        oc = sum(f.split("=")[0].count(o) for o in "+-*/")
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), a, oc))
    cut = int(len(items) * 0.7); return items[:cut], items[cut:]


def run() -> Dict:
    train, test = _load()
    if SMOKE: train = train[:400]; test = test[:200]
    seed = int(os.environ.get("HDLAB_SEED", "1013"))
    of, byf = _solve(train, test, search=False, seed=seed)
    os_, bys = _solve(train, test, search=True, seed=seed)
    print("  PP-375 port: TEXT-ORDER overall=%.4f (1op=%s) | +SEARCH overall=%.4f (1op=%s) | vs prior ASDiv 0.224, cascade-v2 0.309, multihop-1op 0.376" % (
        of.get("overall", 0), byf.get(1), os_.get("overall", 0), bys.get(1)), flush=True)
    return {"accuracy": os_.get("overall", 0.0), "textorder_overall": of.get("overall", 0.0), "textorder_1op": byf.get(1, 0.0),
            "search_overall": os_.get("overall", 0.0), "search_1op": bys.get(1, 0.0), "n_test": len(test)}


def verdict(r) -> Tuple[str, str]:
    s1 = r["search_1op"]; t1 = r["textorder_1op"]
    s = "1op: text-order=%.4f, +search=%.4f | overall: text-order=%.4f, +search=%.4f (vs cascade-v2 0.309, multihop 0.376). PP-375 op-seq + answer-consistency." % (
        t1, s1, r["textorder_overall"], r["search_overall"])
    best1 = max(s1, t1)
    if best1 >= 0.45:
        return ("HARD_PASS", "HARD_PASS: PP-375 mechanism TRANSFERS to ASDiv-1op >=0.45 -- proven substrate-product mechanism (MultiArith 0.753) realizes ASDiv; substrate-self-improvement (existing mechanism -> new capability). " + s)
    if best1 >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: PP-375 port 0.40-0.45 on ASDiv-1op -- partial transfer. " + s)
    return ("HARD_FAIL", "HARD_FAIL: PP-375 mechanism does NOT transfer to ASDiv-1op (<0.40). MultiArith's 0.753 relied on text-order operand alignment ASDiv lacks; ASDiv needs operand SELECTION which PP-375 sidesteps. Comprehension/selection wall holds. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
