"""
exp_svamp_math_wk_lex_cpu_v1.py -- SVAMP Path 1: substrate-self-referential math-world-knowledge LEX constants -- CPU.

ROUTING: Research BOUNDARIES-REJECTED note, SVAMP Path 1 (USER-LOCKED brain-can-do-it rule: world-knowledge is NOT outside-substrate;
  the brain retrieves "dozen->12", "dog->4 legs" from semantic memory; substrate equivalent = LEX_constant concept partition, rule 8).
  v2 learned-selector plateaued at 0.367 with ~26% items world-knowledge-bound (no text-solvable pair). This adds Research's
  hand-authored math-WK LEX atoms (concept_corpus_math_world_knowledge_lex_atoms.jsonl: dozen=12, days_per_week=7, legs_per_dog=4,
  percent=100, ...). Mechanism: when a constant TRIGGER word appears in the text, add its value to the number pool; the learned
  selector + op-classifier then compose with it (e.g. "2 dogs" + 4 -> 2*4=8 legs). A/B: base pool vs WK-augmented pool. Bundled SVAMP.
  Substrate-self-referential (rule 8 us-or-substrate); no external knowledge, no LLM.
PRE-REGISTERED (Research gate): HARD-PASS >= 0.42 (math-WK closes the world-knowledge gap, past target). MIDDLE 0.39-0.42.
  HARD-FAIL < 0.39. UNKNOWN if load fails. NO defeat (drill-defeatism + brain-can-do-it).
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
ANCHOR_NAME = "svamp_math_wk_lex_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
LEARNED_BASE = 0.367
WK_TRIG: Dict[str, set] = {}   # trigger stem -> set of constant values


def load_wk():
    """parse Research math-WK LEX atoms -> trigger-word(stem) -> set of integer values. 'A_per_B' -> trigger B(last word); else key itself."""
    fp = REPO / "data" / "substrate_index" / "concept_corpus_math_world_knowledge_lex_atoms.jsonl"
    if not fp.exists(): return False
    for line in open(fp, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        a = json.loads(line)
        for key, val in a.get("members_named_values", {}).items():
            try: v = Fraction(str(val)).limit_denominator(10**6)
            except Exception: continue
            if "_per_" in key:
                trig = key.split("_per_")[-1].split("_")[-1]
            else:
                trig = key
            for t in (trig, _stem(trig)):
                if t and t.isalpha(): WK_TRIG.setdefault(t, set()).add(v)
    # symbol triggers
    WK_TRIG.setdefault("percent", set()).add(Fraction(100)); WK_TRIG.setdefault("dollar", set()).add(Fraction(100))
    return len(WK_TRIG) > 0


def _wk_extra(text):
    """constants triggered ONLY when a world-knowledge word is ADJACENT to a number (a unit/multiplier tied to a quantity:
    "3 dozen", "2 dogs", "5 weeks"). Restricting firing avoids over-triggering noise that distracts the operand selector."""
    toks = text.lower().split(); extra = []; seen = set()
    isnum = [bool(re.match(r"^\d", t.replace("$", "").replace(",", ""))) for t in toks]
    for k, w in enumerate(toks):
        st = _stem(re.sub(r"[^a-z]", "", w))
        if st not in WK_TRIG: continue
        near_num = any(isnum[j] for j in range(max(0, k - 2), min(len(toks), k + 3)))
        if not near_num: continue   # only fire for quantity-unit patterns
        for v in WK_TRIG[st]:
            if v in seen: continue
            seen.add(v); extra.append({"v": v, "noun": st, "idx": 1000 + len(extra), "in_q": False, "wk": True})
    if "%" in text and Fraction(100) not in seen:
        extra.append({"v": Fraction(100), "noun": "percent", "idx": 1500, "in_q": False, "wk": True})
    return extra
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


def _numpool(text, augment):
    info = _numinfo(text)
    if augment:
        extra = _wk_extra(text)
        info = info + extra
    if len(info) > 10: info = info[:10]   # bound pair-search blowup
    return info


def _pipeline(train, test, augment, seed):
    rng = np.random.default_rng(seed)
    TR = []
    for text, ans in train:
        info = _numpool(text, augment)
        if len(info) < 2: continue
        target = _target(text); g = _gold(info, ans, target)
        if g is None: continue
        TR.append((text, info, target, g))
    if not TR: return 0.0, 0.0, 0
    sw = defaultdict(float); scw = defaultdict(float); c = 1
    def cands_of(info): return [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j]
    for ep in range(10 if not SMOKE else 4):
        for ti in rng.permutation(len(TR)):
            text, info, target, (gi, gj, gop) = TR[ti]; ws = re.findall(r"[a-z]+", text.lower())
            def sscore(i, j): return sum(sw[f] for f in _pair_feats(info[i], info[j], target, ws))
            pi, pj = max(cands_of(info), key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
            if (pi, pj) != (gi, gj):
                for f in _pair_feats(info[gi], info[gj], target, ws): sw[f] += 1; scw[f] += c
                for f in _pair_feats(info[pi], info[pj], target, ws): sw[f] -= 1; scw[f] -= c
            c += 1
    savg = {f: sw[f] - scw[f] / c for f in sw}
    ow = {o: defaultdict(float) for o in OPNAMES}; ocw = {o: defaultdict(float) for o in OPNAMES}; c2 = 1
    OPTR = [(_op_feats(t, info[gi], info[gj], tg, re.findall(r"[a-z]+", t.lower())), gop) for (t, info, tg, (gi, gj, gop)) in TR]
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(OPTR)):
            feats, g = OPTR[i]; sc = {o: sum(ow[o][f] for f in feats) for o in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: ow[g][f] += 1; ow[pred][f] -= 1; ocw[g][f] += c2; ocw[pred][f] -= c2
            c2 += 1
    oavg = {o: {f: ow[o][f] - ocw[o][f] / c2 for f in ow[o]} for o in OPNAMES}
    cor = 0; sel_cor = 0; sel_n = 0
    for text, ans in test:
        info = _numpool(text, augment)
        if len(info) < 2: continue
        target = _target(text); ws = re.findall(r"[a-z]+", text.lower())
        def sscore(i, j): return sum(savg.get(f, 0.0) for f in _pair_feats(info[i], info[j], target, ws))
        pi, pj = max(cands_of(info), key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
        a, b = info[pi], info[pj]
        feats = _op_feats(text, a, b, target, ws); sc = {o: sum(oavg[o].get(f, 0.0) for f in feats) for o in OPNAMES}
        op = max(OPNAMES, key=lambda o: (sc[o], o)); r = OPS[op](a["v"], b["v"])
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
        g = _gold(info, ans, target)
        if g is not None:
            sel_n += 1
            if (pi, pj) == (g[0], g[1]) or (pi, pj) == (g[1], g[0]): sel_cor += 1
    return (cor / len(test) if test else 0.0), (sel_cor / sel_n if sel_n else 0.0), len(TR)


def _selftest():
    info = _numinfo("there are 5 apples and 3 apples . how many apples ?")
    assert len(info) == 2 and _stem("apples") == "apple"
    print("[selftest] PASS: svamp-math-wk-lex", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not load_wk():
        print("[wk] atoms file missing", flush=True); return {"error": "wk_atoms_missing", "accuracy": 0.0}
    print("  [wk] %d trigger words loaded (e.g. dozen->%s, dog->%s, week->%s)" % (
        len(WK_TRIG), sorted(WK_TRIG.get("dozen", set())), sorted(WK_TRIG.get("dog", set())), sorted(WK_TRIG.get("week", set()))), flush=True)
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
    seed = int(os.environ.get("HDLAB_SEED", "1011"))
    base_acc, base_sel, nb = _pipeline(train, test, augment=False, seed=seed)
    print("  [base pool]      acc=%.4f (selector-pair %.4f, train labels=%d)" % (base_acc, base_sel, nb), flush=True)
    wk_acc, wk_sel, nw = _pipeline(train, test, augment=True, seed=seed)
    print("  [+math-WK LEX]   acc=%.4f (selector-pair %.4f, train labels=%d)" % (wk_acc, wk_sel, nw), flush=True)
    lift = wk_acc - base_acc
    print("  WK LIFT = %+.4f | vs learned-base 0.367, first-2 0.287 | test=%d" % (lift, len(test)), flush=True)
    return {"accuracy": round(wk_acc, 4), "acc_wk": round(wk_acc, 4), "acc_base": round(base_acc, 4), "lift": round(lift, 4),
            "wk_selector_pair_acc": round(wk_sel, 4), "n_test": len(test), "n_train_wk": nw}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    aw = r["acc_wk"]; ab = r["acc_base"]; lift = r["lift"]
    s = "+math-WK=%.4f vs base-pool=%.4f (lift=%+.4f, WK-selector-pair=%.4f, test=%d). World-knowledge via substrate LEX_constant concept partition (rule 8)." % (aw, ab, lift, r["wk_selector_pair_acc"], r["n_test"])
    if aw >= 0.42:
        return ("HARD_PASS", "HARD_PASS: substrate math-world-knowledge LEX constants push SVAMP >=0.42 (Research target) -- the ~26pct world-knowledge gap closes via substrate-self-referential semantic memory (brain-can-do-it: dozen->12, dog->4 legs). NOT outside-substrate. " + s)
    if aw >= 0.39:
        return ("MIDDLE_BAND", "MIDDLE_BAND: math-WK lifts SVAMP to 0.39-0.42 -- world-knowledge closes much of the gap; richer trigger coverage / multi-hop for 0.42. " + s)
    return ("HARD_FAIL", "HARD_FAIL: math-WK <0.39 -- trigger coverage or selection insufficient; more substrate-only paths (multi-hop selector, subset-sum) before any claim. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
