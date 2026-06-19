"""
exp_path1lite_entity_binding_mwp_cpu_v1.py -- Path-1-LITE: entity-quantity binding for MWP operand-selection (no CoNLL-2005) -- CPU.

ROUTING: Research operand-selection drill Path 1 (SRL over Tier-A) is 3-5d + needs CoNLL-2005. This LITE probe tests the SAME linguistic
  angle ("which number goes with which agent/object" -- the SRL discriminating signal) with HEURISTIC role binding (no SRL training
  data, no trained parser): each number is bound to its (entity, object) via local syntax (nearest preceding name/possessor + following
  noun); the question's queried (entity, object) selects/combines the relevant quantities; op from verb-cue. Informs the full-Path-1
  decision: if heuristic entity-binding already lifts > +0.04 over 0.39, full SRL is worth building; if it plateaus, that's the 5th
  independent triangulation angle (operand-selection corpus-bound). ASDiv-1op. Substrate-only, no LLM.
PRE-REGISTERED (drill fail-band): HARD-PASS acc >= 0.49 (+0.10). MIDDLE 0.43-0.49 (+0.04-0.10; full Path-1 SRL warranted). HARD-FAIL
  < 0.43 (5th triangulation angle -> operand-selection corpus-bound; full SRL likely also plateaus; defer to Phase-6).
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
from typing import Dict, Tuple
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "path1lite_entity_binding_mwp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20, "dozen": 12}
SUB = ("gave", "lost", "spent", "sold", "ate", "used", "left", "remain", "fewer", "away", "dropped", "broke", "fell", "flew", "took")
ADD = ("got", "bought", "received", "found", "more", "picked", "another", "added", "gained", "altogether", "total", "in all", "together", "both", "sum", "combined")
MUL = ("each", "per", "every", "apiece", "times", "twice", "double", "rows of", "boxes of")
DIV = ("share", "divide", "split", "equally", "each group")
CMP = ("more than", "fewer than", "less than", "difference", "how many more", "how many fewer", "taller", "older")


def _st(w):
    w = w.lower()
    if w.endswith("ies") and len(w) > 4: return w[:-3] + "y"
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2: return w[:-1]
    return w


def _tokens(text): return text.split()


def _numinfo(text):
    """each number -> (value, object_noun, entity, pos)."""
    toks = _tokens(text); out = []
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.!:;")
        val = Fraction(ww) if re.match(r"^\d+(?:\.\d+)?$", ww) else (Fraction(_WORDNUM[ww.lower()]) if ww.lower() in _WORDNUM else None)
        if val is None: continue
        obj = _st(re.sub(r"[^a-zA-Z]", "", toks[k + 1])) if k + 1 < len(toks) else ""
        ent = ""
        for j in range(k - 1, max(-1, k - 6), -1):  # nearest preceding capitalized name
            t = toks[j].rstrip(".,?")
            if t[:1].isupper() and t.lower() not in ("how", "there", "the", "a", "an"): ent = t.lower(); break
        out.append({"v": val, "obj": obj, "ent": ent, "pos": k})
    return out


def _op_from_cues(text):
    low = " " + text.lower() + " "
    if any(c in low for c in CMP): return "-"
    if any(c in low for c in DIV): return "/"
    if any(c in low for c in MUL): return "*"
    if any(c in low for c in SUB): return "-"
    if any(c in low for c in ADD): return "+"
    return "+"


OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}


def solve(text):
    low = text.lower(); nums = _numinfo(text)
    if len(nums) < 2: return None
    m = re.search(r"how (?:many|much) ([a-z]+)", low); qobj = _st(m.group(1)) if m else ""
    # entity-binding selection: prefer the 2 numbers whose object matches the queried object (entity-grounded)
    if qobj:
        match = [d for d in nums if d["obj"] == qobj]
        cand = match if len(match) >= 2 else nums
    else:
        cand = nums
    op = _op_from_cues(text)
    vals = [d["v"] for d in cand[:2]] if len(cand) >= 2 else [d["v"] for d in nums[:2]]
    a, b = vals[0], vals[1]
    if op in ("+", "*"): return OPS[op](a, b)
    hi, lo = (a, b) if a >= b else (b, a)
    return OPS[op](hi, lo)


def _selftest():
    ni = _numinfo("Tom has 5 apples and Mary has 3 oranges")
    assert ni[0]["v"] == Fraction(5) and ni[0]["obj"] == "apple" and ni[0]["ent"] == "tom"
    assert solve("Tom has ten apples and gave three away . how many apples ?") == Fraction(7)
    assert _op_from_cues("how many total altogether") == "+"
    print("[selftest] PASS: path1lite-entity-binding", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _load_asdiv_1op():
    d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8")); items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    return items


def run() -> Dict:
    try:
        items = _load_asdiv_1op()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    if SMOKE: items = items[:200]
    cor = tot = 0; cor_multi = tot_multi = 0
    for text, ans in items:
        tot += 1; pred = solve(text)
        ok = (pred is not None and Fraction(pred).limit_denominator(10**6) == ans); cor += int(ok)
        if len(_numinfo(text)) > 2:  # distractor-number subset (where entity-binding should matter most)
            tot_multi += 1; cor_multi += int(ok)
    acc = cor / tot if tot else 0.0; acc_multi = cor_multi / tot_multi if tot_multi else 0.0
    print("  Path-1-lite entity-binding: ASDiv-1op acc=%.4f (n=%d) vs discriminative ~0.39" % (acc, tot), flush=True)
    print("  distractor-subset (>2 numbers) acc=%.4f (n=%d) -- where entity-binding matters" % (acc_multi, tot_multi), flush=True)
    print("  lift over 0.39 baseline = %+.4f" % (acc - 0.39), flush=True)
    return {"f1": round(acc, 4), "accuracy": round(acc, 4), "lift_over_baseline": round(acc - 0.39, 4),
            "distractor_acc": round(acc_multi, 4), "n_distractor": tot_multi, "n": tot}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "acc=%.4f (distractor-subset %.4f n=%d, n=%d) vs discriminative ~0.39" % (a, r["distractor_acc"], r["n_distractor"], r["n"])
    if a >= 0.49:
        return ("HARD_PASS", "HARD_PASS: heuristic entity-quantity binding lifts operand-selection >=+0.10 -- the linguistic angle works; full Path-1 SRL strongly warranted. " + s)
    if a >= 0.43:
        return ("MIDDLE_BAND", "MIDDLE_BAND: entity-binding +0.04-0.10 -- linguistic angle has signal; full Path-1 SRL (CoNLL-2005) warranted to realize it. " + s)
    return ("HARD_FAIL", "HARD_FAIL: heuristic entity-binding <+0.04 over 0.39 -- 5th INDEPENDENT triangulation angle; operand-selection corpus/comprehension-bound; full Path-1 SRL likely also plateaus -> defer to Phase-6 ingestion per refined brain-can-do-it (honest negative IS evidence). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
