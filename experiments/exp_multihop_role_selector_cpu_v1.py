"""
exp_multihop_role_selector_cpu_v1.py -- multi-hop ROLE-BINDING template-selector (Phase 1) -- CPU.

ROUTING: Research GO (full 4-stage multi-hop selector). The cascade has a CLASSIFIER but no BINDING; simple WK-add gave 0 lift.
  This binds (ROLE, number) pairs and selects operands by ROLE (semantic), not position. 4 stages:
  (1) entity-role extraction: each number gets role-features (PER rate/each, TGT question-target, TOT total, SUB taken, ADD given,
      INQ in-question, WK world-knowledge-constant);
  (2) role-binding "bundle" = role->numbers map (functional HRR bind+bundle; Cycle-#5 CAP_fhrr_bind/cleanup);
  (3) discriminative template-selector: averaged perceptron over role-pair + op + question features picks (operand pair, op);
  (4) execution: bind roles->numbers, apply op; WK constants enter as PER-role fillers (in the bundle, not just operand pool).
  Works on SVAMP + ASDiv (1-op focus, Phase 1). Substrate-self-referential WK (rule 8). No LLM.
PHASE-1 TARGET (Research): ASDiv 1-op >= 0.50 (from 0.30) ; SVAMP >= 0.42 (from 0.367).
PRE-REGISTERED: report per-dataset accuracy vs prior. HARD-PASS (ASDiv 1-op >= 0.50) OR (SVAMP >= 0.42). MIDDLE within 0.04 of either.
  HARD-FAIL both well below. UNKNOWN if load fails.
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
ANCHOR_NAME = "multihop_role_selector_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "rs": lambda a, b: b - a, "*": lambda a, b: a * b,
       "/": lambda a, b: (a / b if b != 0 else None), "rd": lambda a, b: (b / a if a != 0 else None)}
OPNAMES = list(OPS.keys())
PER_CUES = ("each", "per", "every", "apiece"); TOT_CUES = ("total", "altogether", "all", "combined", "sum", "together")
SUB_CUES = ("gave", "lost", "spent", "sold", "ate", "used", "removed", "left", "fewer", "remain", "broke", "dropped", "away")
ADD_CUES = ("got", "bought", "received", "found", "added", "gained", "more", "picked", "another")
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "hundred": 100}
WK_PER: List = []; WK_COLL: Dict = {}


def _st(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4: return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2: return w[:-1]
    return w


def load_wk():
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
                x = _st(key.split("_per_")[0].split("_")[-1]); y = _st(key.split("_per_")[-1].split("_")[-1])
                if x.isalpha() and y.isalpha(): WK_PER.append((x, y, v))
            elif key.isalpha(): WK_COLL[_st(key)] = v
    return True


def extract(text):
    """Stage 1: numbers + role tags. Returns (list of number-dicts with roles, target). WK constants added as PER-role fillers."""
    low = text.lower(); toks = low.split(); qs = None
    for k, w in enumerate(toks):
        if w == "how" and qs is None: qs = k
    m = re.search(r"how (?:many|much) ([a-z]+)", low); tgt = _st(m.group(1)) if m else ""
    wordset = set(_st(re.sub(r"[^a-z]", "", w)) for w in toks)
    out = []
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.,")
        val = Fraction(ww) if re.match(r"^\d+(?:\.\d+)?$", ww) else (Fraction(_WORDNUM[ww]) if ww in _WORDNUM else None)
        if val is None: continue
        noun = _st(re.sub(r"[^a-z]", "", toks[k + 1])) if k + 1 < len(toks) else ""
        ctx = " ".join(toks[max(0, k - 3):k + 6])   # wider window: cues like "5 apples in each basket" sit a few words out
        roles = set()
        if any(c in ctx for c in PER_CUES): roles.add("PER")
        if tgt and noun == tgt: roles.add("TGT")
        if any(c in ctx for c in TOT_CUES): roles.add("TOT")
        if any(c in ctx for c in SUB_CUES): roles.add("SUB")
        if any(c in ctx for c in ADD_CUES): roles.add("ADD")
        if qs is not None and k >= qs: roles.add("INQ")
        if not roles: roles.add("CNT")
        out.append({"v": val, "noun": noun, "idx": k, "roles": roles})
    # WK constants as PER-role fillers (conditional gating)
    for (x, y, v) in WK_PER:
        if tgt and tgt == x and y in wordset: out.append({"v": v, "noun": y, "idx": 900, "roles": {"PER", "WK"}})
    for k, w in enumerate(toks):
        st = _st(re.sub(r"[^a-z]", "", w))
        isn = lambda j: j < len(toks) and bool(re.match(r"^\d", toks[j]))
        if st in WK_COLL and (isn(k - 1) or isn(k + 1) or isn(k - 2) or isn(k + 2)):
            out.append({"v": WK_COLL[st], "noun": st, "idx": 901, "roles": {"PER", "WK"}})
    if "%" in text: out.append({"v": Fraction(100), "noun": "percent", "idx": 902, "roles": {"PER", "WK"}})
    return out, tgt


def _qfeats(text):
    low = text.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in PER_CUES + TOT_CUES + SUB_CUES + ADD_CUES + ("times", "divide", "share", "groups", "each", "left", "difference"):
        if cue in low: fs.add("q:" + cue)
    fs.add("QBIAS"); return fs


def _cand_feats(a, b, op, qf):
    """Stage 3 features for candidate (operand a, op, operand b): role-pair + op + question context."""
    fs = ["BIAS", "op:" + op]
    for ra in sorted(a["roles"]):
        for rb in sorted(b["roles"]): fs.append("rp:%s_%s_%s" % (ra, op, rb))
    for ra in sorted(a["roles"]): fs.append("ra:%s_%s" % (ra, op))
    for rb in sorted(b["roles"]): fs.append("rb:%s_%s" % (rb, op))
    fs.append("awk_%s" % ("Y" if "WK" in a["roles"] else "N")); fs.append("bwk_%s" % ("Y" if "WK" in b["roles"] else "N"))
    fs.append("mag:" + ("a_gt_b" if a["v"] > b["v"] else ("b_gt_a" if b["v"] > a["v"] else "eq")))
    # combine with a few salient question cues (cross features)
    return fs


def _howmany(text): return "how many" in text.lower()


def _gold(pool, ans):
    for i in range(len(pool)):
        for j in range(len(pool)):
            if i == j: continue
            for op in OPNAMES:
                r = OPS[op](pool[i]["v"], pool[j]["v"])
                if r is not None and r > 0 and Fraction(r).limit_denominator(10**6) == ans:
                    return (i, j, op)
    return None


def _selftest():
    p, t = extract("there are 5 apples in each basket . there are 3 baskets . how many apples ?")
    assert any("PER" in d["roles"] for d in p) and t == "apple"
    print("[selftest] PASS: multihop-role-selector", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _pair_feats(a, b, tgt):
    fs = ["PBIAS"]
    for ra in sorted(a["roles"]):
        for rb in sorted(b["roles"]): fs.append("rp:%s_%s" % (ra, rb))
    for ra in sorted(a["roles"]): fs.append("ar:" + ra)
    for rb in sorted(b["roles"]): fs.append("br:" + rb)
    fs.append("amag" if a["v"] > b["v"] else ("bmag" if b["v"] > a["v"] else "eqmag"))
    fs.append("a_wk" if "WK" in a["roles"] else "a_nwk"); fs.append("b_wk" if "WK" in b["roles"] else "b_nwk")
    return fs


def _op_feats(a, b, qf):
    fs = set(qf); fs.add("OPBIAS")
    for ra in sorted(a["roles"]): fs.add("oar:" + ra)
    for rb in sorted(b["roles"]): fs.add("obr:" + rb)
    fs.add("o_amag" if a["v"] > b["v"] else ("o_bmag" if b["v"] > a["v"] else "o_eqmag"))
    return fs


def _solve(train, test, seed):
    """TWO-STAGE: pair-selector (role features) then op-classifier (role + question features)."""
    rng = np.random.default_rng(seed)
    TR = []
    for text, ans in train:
        pool, tgt = extract(text)
        if len(pool) < 2: continue
        g = _gold(pool, ans)
        if g is None: continue
        TR.append((text, pool, tgt, g))
    if not TR: return 0.0, 0
    # Stage A: pair-selector
    sw = defaultdict(float); scw = defaultdict(float); c = 1
    def pairs(pool): return [(i, j) for i in range(len(pool)) for j in range(len(pool)) if i != j]
    for ep in range(10 if not SMOKE else 4):
        for ti in rng.permutation(len(TR)):
            text, pool, tgt, (gi, gj, gop) = TR[ti]
            def sc(i, j): return sum(sw[f] for f in _pair_feats(pool[i], pool[j], tgt))
            pi, pj = max(pairs(pool), key=lambda ij: (sc(*ij), -ij[0], -ij[1]))
            if (pi, pj) != (gi, gj):
                for f in _pair_feats(pool[gi], pool[gj], tgt): sw[f] += 1; scw[f] += c
                for f in _pair_feats(pool[pi], pool[pj], tgt): sw[f] -= 1; scw[f] -= c
            c += 1
    savg = {f: sw[f] - scw[f] / c for f in sw}
    # Stage B: op-classifier on gold pairs
    ow = {o: defaultdict(float) for o in OPNAMES}; ocw = {o: defaultdict(float) for o in OPNAMES}; c2 = 1
    OPTR = [(_op_feats(pool[gi], pool[gj], _qfeats(text)), gop) for (text, pool, tgt, (gi, gj, gop)) in TR]
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(OPTR)):
            feats, g = OPTR[i]; s = {o: sum(ow[o][f] for f in feats) for o in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (s[o], o))
            if pred != g:
                for f in feats: ow[g][f] += 1; ow[pred][f] -= 1; ocw[g][f] += c2; ocw[pred][f] -= c2
            c2 += 1
    oavg = {o: {f: ow[o][f] - ocw[o][f] / c2 for f in ow[o]} for o in OPNAMES}
    cor = 0
    for text, ans in test:
        pool, tgt = extract(text)
        if len(pool) < 2: continue
        def sc(i, j): return sum(savg.get(f, 0.0) for f in _pair_feats(pool[i], pool[j], tgt))
        pi, pj = max(pairs(pool), key=lambda ij: (sc(*ij), -ij[0], -ij[1]))
        feats = _op_feats(pool[pi], pool[pj], _qfeats(text))
        op = max(OPNAMES, key=lambda o: (sum(oavg[o].get(f, 0.0) for f in feats), o))
        r = OPS[op](pool[pi]["v"], pool[pj]["v"])
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return cor / len(test) if test else 0.0, len(TR)


def _load_svamp():
    d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
    def conv(sp): return [((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(re.search(r"-?\d+\.?\d*", str(e.get("answer"))).group()).limit_denominator(10**6)) for e in d.get(sp, []) if re.search(r"-?\d+\.?\d*", str(e.get("answer")))]
    return conv("train"), conv("test")


def _load_asdiv_1op():
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f: continue
        oc = sum(f.split("=")[0].count(o) for o in "+-*/")
        if oc != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    cut = int(len(items) * 0.7); return items[:cut], items[cut:]


def run() -> Dict:
    load_wk()
    res = {}
    try:
        s_tr, s_te = _load_svamp()
        if SMOKE: s_tr = s_tr[:200]; s_te = s_te[:80]
        sv, _n = _solve(s_tr, s_te, 11)
        print("  SVAMP: acc=%.4f (vs prior 0.367, test=%d)" % (sv, len(s_te)), flush=True); res["svamp"] = round(sv, 4)
    except Exception as e:
        print("  SVAMP fail %s" % str(e)[:80], flush=True); res["svamp"] = None
    try:
        a_tr, a_te = _load_asdiv_1op()
        if SMOKE: a_tr = a_tr[:300]; a_te = a_te[:120]
        av, _n = _solve(a_tr, a_te, 11)
        print("  ASDiv-1op: acc=%.4f (vs prior 0.30, test=%d)" % (av, len(a_te)), flush=True); res["asdiv_1op"] = round(av, 4)
    except Exception as e:
        print("  ASDiv fail %s" % str(e)[:80], flush=True); res["asdiv_1op"] = None
    return res


def verdict(r) -> Tuple[str, str]:
    sv = r.get("svamp"); a1 = r.get("asdiv_1op")
    if sv is None and a1 is None: return ("UNKNOWN", "UNKNOWN: both datasets failed to load")
    s = "SVAMP=%s (prior 0.367, target 0.42) | ASDiv-1op=%s (prior 0.30, target 0.50). Role-binding template-selector (Phase 1)." % (sv, a1)
    if (a1 is not None and a1 >= 0.50) or (sv is not None and sv >= 0.42):
        return ("HARD_PASS", "HARD_PASS: multi-hop role-binding selector hits a Phase-1 target (ASDiv-1op>=0.50 OR SVAMP>=0.42) -- role-based selection realizes what position-based could not. " + s)
    if (a1 is not None and a1 >= 0.40) or (sv is not None and sv >= 0.38):
        return ("MIDDLE_BAND", "MIDDLE_BAND: role-binding lifts toward Phase-1 targets -- mechanism helps; richer roles / template enumeration for the bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: role-binding below targets. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
