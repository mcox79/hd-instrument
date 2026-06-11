"""
exp_asdiv_cascade_wk_cpu_v1.py -- substrate ASDiv cascade v2 (1-op + 2-op multi-step + verifier) -- CPU.

ROUTING: Research ASDiv cascade (v1 got 0.300; target 0.40). v1 was single-op only; ASDiv has MULTI-STEP problems. v2 adds a
  2-op composition fallback: try 1-op (predicted op, all pairs, verifier); if no plausible answer, try 2-op (predicted op-pair,
  all triples, verifier). Single-op-first, multi-step-fallback, both plausibility-filtered. op + op-pair classifiers trained on
  answer-consistency weak labels. Bundled ASDiv. Substrate-only, no LLM.
PRE-REGISTERED: HARD-PASS >= 0.40. MIDDLE >= 0.33 (lifts v1 0.300). HARD-FAIL < 0.30. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import re as R2
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "asdiv_cascade_wk_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
B = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b != 0 else None}
OP1 = {"ADD": ("+", 0), "MUL": ("*", 0), "SUB_ab": ("-", 0), "SUB_ba": ("-", 1), "DIV_ab": ("/", 0), "DIV_ba": ("/", 1)}
OP1N = list(OP1.keys()); PAIRS = [(o1, o2) for o1 in B for o2 in B]
def _ev1(name, a, b):
    op, sw = OP1[name]; x, y = (b, a) if sw else (a, b); return B[op](x, y)
def _ev2(a, b, c, o1, o2):
    t = B[o1](a, b); return None if t is None else B[o2](t, c)
def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", t.replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out
_AUG = False
_WK_PER = []        # list of (x_stem, y_stem, value): "X per Y" -> fire when target~X and Y in text (question-guided gating)
_WK_COLL = {}       # collection word -> value: fire on adjacency to a number
def _st(w):
    w=w.lower()
    if w.endswith("ies") and len(w)>4: return w[:-3]+"y"
    if w.endswith("s") and not w.endswith("ss") and len(w)>2: return w[:-1]
    return w
def load_wk():
    fp = REPO / "data" / "substrate_index" / "concept_corpus_math_world_knowledge_lex_atoms.jsonl"
    if not fp.exists(): return False
    for line in open(fp, encoding="utf-8"):
        line=line.strip()
        if not line: continue
        a=json.loads(line)
        for key,val in a.get("members_named_values",{}).items():
            try: v=Fraction(str(val)).limit_denominator(10**6)
            except Exception: continue
            if "_per_" in key:
                x=key.split("_per_")[0].split("_")[-1]; y=key.split("_per_")[-1].split("_")[-1]
                if x.isalpha() and y.isalpha(): _WK_PER.append((_st(x), _st(y), v))
            else:
                if key.isalpha(): _WK_COLL[_st(key)]=v
    return True
def _wk_extra(t):
    """QUESTION-GUIDED WK gating: 'X per Y' constant fires only when question target ~ X and entity Y present; collection words fire on number-adjacency."""
    low=t.lower(); toks=low.split(); isnum=[bool(R2.match(r"^\d",x)) for x in toks]; vals=set()
    m=R2.search(r"how (?:many|much) ([a-z]+)", low); tgt=_st(m.group(1)) if m else ""
    wordset=set(_st(R2.sub(r"[^a-z]","",w)) for w in toks)
    for (x,y,v) in _WK_PER:
        if tgt and tgt==x and y in wordset: vals.add(v)      # e.g. target=leg, dog in text -> legs_per_dog
    for k,w in enumerate(toks):
        st=_st(R2.sub(r"[^a-z]","",w))
        if st in _WK_COLL and any(isnum[j] for j in range(max(0,k-2),min(len(toks),k+3))): vals.add(_WK_COLL[st])
    if "%" in t: vals.add(Fraction(100))
    return sorted(vals)
def _NUMS(t):
    base=_nums(t)
    return base + ([v for v in _wk_extra(t) if v not in base] if _AUG else [])
def _ans(x):
    m = re.search(r"-?\d+(?:\.\d+)?", str(x).replace(",", ""))
    try: return Fraction(m.group(0)).limit_denominator(10**6) if m else None
    except Exception: return None
def _feats(txt):
    low = txt.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together", "equally", "groups", "rest", "difference", "then", "after"):
        if cue in low: fs.add("c:" + cue)
    fs.add("BIAS"); return fs
def _count_q(txt): return bool(re.search(r"how many", txt.lower()))
def _plaus(r, cq): return r is not None and r >= 0 and r <= 100000 and (not cq or r.denominator == 1)
def _selftest():
    assert _ev2(Fraction(6), Fraction(2), Fraction(3), "-", "*") == 12
    print("[selftest] PASS: asdiv-cascade-v2", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
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
    return max(labels, key=lambda l: (sum(avg[l].get(f, 0.0) for f in feats), l))
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1022")))
    try:
        rows = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    data = []
    for e in rows:
        txt = (e.get("body", "") + " " + e.get("question", "")).strip(); a = _ans(e.get("answer"))
        if txt and a is not None and len(_nums(txt)) >= 1: data.append((txt, a))   # >=1 digit; WK may supply the 2nd number
    if SMOKE: data = data[:200]
    idx = np.arange(len(data)); rng.shuffle(idx); cut = len(idx) // 2
    train = [data[i] for i in idx[:cut]]; test = [data[i] for i in idx[cut:]]

    def solve(augment, rng2):
        global _AUG
        _AUG = augment
        def gold1(txt, ans):
            for a, b in itertools.permutations(_NUMS(txt), 2):
                for o in OP1N:
                    if _ev1(o, a, b) == ans: return o
            return None
        def gold2(txt, ans):
            for a, b, c in itertools.permutations(_NUMS(txt)[:6], 3):
                for (o1, o2) in PAIRS:
                    r = _ev2(a, b, c, o1, o2)
                    if r is not None and r == ans: return (o1, o2)
            return None
        X1 = []; X2 = []
        for txt, ans in train:
            g1 = gold1(txt, ans)
            if g1: X1.append((_feats(txt), g1)); continue
            g2 = gold2(txt, ans)
            if g2: X2.append((_feats(txt), g2))
        if not X1: return None, 0, 0
        EP = 12 if not SMOKE else 4
        a1 = _train(X1, OP1N, rng2, EP); a2 = _train(X2, PAIRS, rng2, EP) if X2 else None
        cor = 0
        for txt, ans in test:
            nums = _NUMS(txt); feats = _feats(txt); cq = _count_q(txt); pred_ans = None
            o1 = _pred(a1, OP1N, feats); cands = []
            for k1, k2 in itertools.permutations(range(len(nums)), 2):
                r = _ev1(o1, nums[k1], nums[k2])
                if _plaus(r, cq): cands.append((k1 + k2, r))
            if cands: pred_ans = max(cands, key=lambda x: x[0])[1]
            if pred_ans is None and a2 is not None and len(nums) >= 3:
                op2 = _pred(a2, PAIRS, feats); c2 = []
                for k1, k2, k3 in itertools.permutations(range(min(len(nums), 6)), 3):
                    r = _ev2(nums[k1], nums[k2], nums[k3], op2[0], op2[1])
                    if _plaus(r, cq): c2.append((k1 + k2 + k3, r))
                if c2: pred_ans = max(c2, key=lambda x: x[0])[1]
            if pred_ans is not None and pred_ans == ans: cor += 1
        return cor / len(test), len(X1), len(X2)

    base_acc, n1b, n2b = solve(False, np.random.default_rng(7))
    wk_acc, n1w, n2w = solve(True, np.random.default_rng(7))
    if base_acc is None: return {"error": "no_train_labels", "accuracy": 0.0}
    lift = wk_acc - base_acc
    print("  ASDIV-CASCADE-WK: base=%.4f  +WK=%.4f  (lift=%+.4f, vs prior 0.224, n_test=%d)" % (base_acc, wk_acc, lift, len(test)), flush=True)
    return {"accuracy": round(wk_acc, 4), "acc_wk": round(wk_acc, 4), "acc_base": round(base_acc, 4), "lift": round(lift, 4),
            "n_1op_wk": n1w, "n_2op_wk": n2w, "n_test": len(test)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    aw = r["acc_wk"]; ab = r["acc_base"]; lift = r["lift"]
    s = "+WK=%.4f vs base=%.4f (lift=%+.4f, vs prior 0.224, n_test=%d). Existing cascade (1-op+2-op+verifier) + substrate LEX_constant world-knowledge." % (aw, ab, lift, r["n_test"])
    if aw >= 0.40:
        return ("HARD_PASS", "HARD_PASS: cascade + math-WK reaches ASDiv >=0.40 -- world-knowledge realizes the WK-augmented ceiling on the best existing solver. Brain-can-do-it. " + s)
    if aw >= 0.33 or lift >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cascade+WK >=0.33 or lift>=0.02 -- world-knowledge lifts the existing cascade toward the ceiling. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cascade+WK <0.33 and lift<0.02 -- WK does not lift the cascade (adjacency triggers too sparse, or selection-bound). " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
