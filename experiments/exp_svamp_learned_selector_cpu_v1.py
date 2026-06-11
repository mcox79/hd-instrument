"""
exp_svamp_learned_selector_cpu_v1.py -- SVAMP direction A v2: LEARNED discriminative operand-pair selector -- CPU.

ROUTING: direction A follow-up. v1 (heuristic target-aligned selection) validated role-asymmetry: SVAMP 0.287 (first-2) -> 0.363
  (heuristic role). The bottleneck is OPERAND SELECTION (which 2 of N numbers; crude heuristics plateau because the answer often
  pairs a NON-target number with a target number, e.g. "290 bananas / 2 groups -> 145" with target "group"). This builds Research's
  bipartite role-assigner: a LEARNED discriminative pair-SELECTOR (averaged perceptron scoring each candidate pair) trained so the
  gold operand pair outscores all others, then the op-direction classifier on the selected pair. Two-stage substrate-discriminative.
  Bundled SVAMP (svamp.json). No LLM.
PRE-REGISTERED: report learned-selector accuracy + vs v1 heuristic (0.363) + vs first-2 (0.287). HARD-PASS >= 0.42 (drill-13 target;
  learned selection closes the gap). MIDDLE 0.36-0.42 OR >= heuristic+0.02. HARD-FAIL < 0.36 (learned selector no better than heuristic).
  UNKNOWN if load fails. NO defeat.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "svamp_learned_selector_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
HEUR_V1 = 0.363; FIRST2 = 0.287
OPS = {"ADD": lambda a, b: a + b, "SUB_ab": lambda a, b: a - b, "SUB_ba": lambda a, b: b - a,
       "MUL": lambda a, b: a * b, "DIV_ab": lambda a, b: (a / b if b != 0 else None), "DIV_ba": lambda a, b: (b / a if a != 0 else None)}
OPNAMES = list(OPS.keys())
TRANSFER_OUT = ("gave", "lost", "spent", "sold", "ate", "removed", "used", "broke", "dropped")
TRANSFER_IN = ("got", "bought", "received", "found", "added", "gained", "made", "picked")


def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None


def _stem(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4: return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2: return w[:-1]
    return w


def _numinfo(text):
    toks = text.lower().split(); out = []; qstart = None
    for k, w in enumerate(toks):
        if w == "how" and qstart is None: qstart = k
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.")
        if re.match(r"^\d+(?:\.\d+)?$", ww):
            noun = re.sub(r"[^a-z]", "", toks[k + 1]) if k + 1 < len(toks) else ""
            out.append({"v": Fraction(ww), "noun": noun, "idx": k, "in_q": (qstart is not None and k >= qstart)})
    return out


def _target(text):
    m = re.search(r"how (?:many|much) ([a-z]+)", text.lower()); return _stem(m.group(1)) if m else ""


def _pair_feats(a, b, target, ws):
    """features describing a candidate operand pair (for the SELECTOR)."""
    fs = ["P_BIAS"]
    am = (target and _stem(a["noun"]) == target); bm = (target and _stem(b["noun"]) == target)
    fs.append("Ptgt_both" if am and bm else ("Ptgt_one" if am or bm else "Ptgt_none"))
    fs.append("Pinq_both" if a["in_q"] and b["in_q"] else ("Pinq_one" if a["in_q"] or b["in_q"] else "Pinq_none"))
    fs.append("Psamenoun" if a["noun"] == b["noun"] and a["noun"] else "Pdiffnoun")
    fs.append("Padj" if abs(a["idx"] - b["idx"]) <= 3 else "Pfar")
    fs.append("Pmag_a_gt_b" if a["v"] > b["v"] else ("Pmag_b_gt_a" if b["v"] > a["v"] else "Pmag_eq"))
    # cross-entity pattern: one matches target, other does not (e.g. groups vs bananas)
    if (am and not bm) or (bm and not am): fs.append("Pcross_target")
    fs.append("PnA:" + a["noun"]); fs.append("PnB:" + b["noun"])
    return fs


def _op_feats(text, a, b, target, ws):
    fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("rel:a_gt_b" if a["v"] > b["v"] else ("rel:b_gt_a" if b["v"] > a["v"] else "rel:eq"))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times",
                "share", "divide", "per", "all", "combined", "together", "equally", "groups", "rest", "difference", "twice"):
        if cue in ws: fs.add("c:" + cue)
    fs.add("aN_tgt" if target and _stem(a["noun"]) == target else "aN_x"); fs.add("bN_tgt" if target and _stem(b["noun"]) == target else "bN_x")
    fs.add("a_in_q" if a["in_q"] else "a_body"); fs.add("b_in_q" if b["in_q"] else "b_body")
    for vb in TRANSFER_OUT:
        if vb in ws: fs.add("tvout:" + vb)
    for vb in TRANSFER_IN:
        if vb in ws: fs.add("tvin:" + vb)
    fs.add("BIAS"); return fs


def _gold(info, ans, target):
    """find gold (pair, op): the pair+directional-op yielding ans; prefer a pair with a target-matching number."""
    cands = []
    n = len(info)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            a, b = info[i], info[j]
            for op in OPNAMES:
                r = OPS[op](a["v"], b["v"])
                if r is not None and Fraction(r).limit_denominator(10**6) == ans:
                    tg = (target and (_stem(a["noun"]) == target or _stem(b["noun"]) == target))
                    cands.append((1 if tg else 0, i, j, op))
    if not cands: return None
    cands.sort(key=lambda x: -x[0])
    _, i, j, op = cands[0]
    return (i, j, op)


def _selftest():
    info = _numinfo("there are 5 apples and 3 apples . how many apples ?")
    assert len(info) == 2 and _stem("apples") == "apple"
    print("[selftest] PASS: svamp-learned-selector", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    try:
        d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    def conv(sp):
        out = []
        for e in d.get(sp, []):
            a = _ans(e.get("answer"))
            if a is not None: out.append(((e.get("body", "") + " " + e.get("question", "")).strip(), a))
        return out
    train = conv("train"); test = conv("test")
    if SMOKE: train = train[:200]; test = test[:80]
    seed = int(os.environ.get("HDLAB_SEED", "1011")); rng = np.random.default_rng(seed)
    # build training instances with gold (pair, op)
    TR = []
    for text, ans in train:
        info = _numinfo(text)
        if len(info) < 2: continue
        target = _target(text); g = _gold(info, ans, target)
        if g is None: continue
        TR.append((text, info, target, g))
    if not TR: return {"error": "no_train", "accuracy": 0.0}
    # --- train SELECTOR (structured perceptron over candidate pairs) ---
    sw = defaultdict(float); scw = defaultdict(float); c = 1
    def pair_cands(info): return [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j]
    for ep in range(10 if not SMOKE else 4):
        for ti in rng.permutation(len(TR)):
            text, info, target, (gi, gj, gop) = TR[ti]; ws = re.findall(r"[a-z]+", text.lower())
            cands = pair_cands(info)
            def sscore(i, j): return sum(sw[f] for f in _pair_feats(info[i], info[j], target, ws))
            pi, pj = max(cands, key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
            if (pi, pj) != (gi, gj):
                for f in _pair_feats(info[gi], info[gj], target, ws): sw[f] += 1; scw[f] += c
                for f in _pair_feats(info[pi], info[pj], target, ws): sw[f] -= 1; scw[f] -= c
            c += 1
    savg = {f: sw[f] - scw[f] / c for f in sw}
    # --- train OP-classifier on gold pairs (teacher forcing) ---
    ow = {o: defaultdict(float) for o in OPNAMES}; ocw = {o: defaultdict(float) for o in OPNAMES}; c2 = 1
    OPTR = []
    for text, info, target, (gi, gj, gop) in TR:
        ws = re.findall(r"[a-z]+", text.lower())
        OPTR.append((_op_feats(text, info[gi], info[gj], target, ws), gop))
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(OPTR)):
            feats, g = OPTR[i]; sc = {o: sum(ow[o][f] for f in feats) for o in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: ow[g][f] += 1; ow[pred][f] -= 1; ocw[g][f] += c2; ocw[pred][f] -= c2
            c2 += 1
    oavg = {o: {f: ow[o][f] - ocw[o][f] / c2 for f in ow[o]} for o in OPNAMES}
    # --- evaluate pipeline + selector accuracy ---
    cor = 0; sel_cor = 0; sel_n = 0
    for text, ans in test:
        info = _numinfo(text)
        if len(info) < 2: continue
        target = _target(text); ws = re.findall(r"[a-z]+", text.lower())
        cands = [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j]
        def sscore(i, j): return sum(savg.get(f, 0.0) for f in _pair_feats(info[i], info[j], target, ws))
        pi, pj = max(cands, key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
        a, b = info[pi], info[pj]
        feats = _op_feats(text, a, b, target, ws); sc = {o: sum(oavg[o].get(f, 0.0) for f in feats) for o in OPNAMES}
        op = max(OPNAMES, key=lambda o: (sc[o], o)); r = OPS[op](a["v"], b["v"])
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
        # selector-only accuracy: did the chosen pair admit ANY op reaching ans?
        g = _gold(info, ans, target)
        if g is not None:
            sel_n += 1
            if (pi, pj) == (g[0], g[1]) or (pi, pj) == (g[1], g[0]): sel_cor += 1
    acc = cor / len(test) if test else 0.0; sel_acc = sel_cor / sel_n if sel_n else 0.0
    print("  learned-selector pipeline acc=%.4f | selector-pair acc=%.4f (n=%d) | vs heuristic-v1 %.3f, first-2 %.3f, test=%d" %
          (acc, sel_acc, sel_n, HEUR_V1, FIRST2, len(test)), flush=True)
    return {"accuracy": round(acc, 4), "selector_pair_acc": round(sel_acc, 4), "vs_heuristic_v1": HEUR_V1,
            "vs_first2": FIRST2, "n_test": len(test), "n_train": len(TR)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "learned-selector acc=%.4f (selector-pair acc=%.4f) vs heuristic-v1 0.363 vs first-2 0.287 (test=%d)" % (a, r["selector_pair_acc"], r["n_test"])
    if a >= 0.42:
        return ("HARD_PASS", "HARD_PASS: learned discriminative pair-selector reaches SVAMP >=0.42 (drill-13 target) -- the bipartite role-assigner closes the operand-selection gap substrate-only. " + s)
    if a >= 0.36 or a >= HEUR_V1 + 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: learned selector >=0.36 or beats heuristic by >=0.02 -- selection mechanism helps; toward 0.42. " + s)
    return ("HARD_FAIL", "HARD_FAIL: learned selector <0.36 and no better than heuristic -- operand selection is genuinely hard (needs deeper semantics); SVAMP plateau is selection-bound. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
