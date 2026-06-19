"""
exp_path5_schema_retrieval_mwp_cpu_v1.py -- Path 5: hippocampal schema retrieval for MWP operand-selection -- CPU.

ROUTING: Research operand-selection drill HANDOFF (exp_dev_handoff_research_operand_selection_top_2_paths_2026-06-12), Path 5
  (cheap-first, P_deflated 0.45). Brain analogue: Tse 2007 schema integration + vMPFC-hippocampal. MECHANISM: prior solved MWP
  scenarios (the training set = substrate solution-history) are stored as SCHEMA vectors (cue + structural features); a new problem
  retrieves its k-nearest solved schemas via similarity; the retrieved schemas' OPERATION + operand-order template is transferred to
  the new problem's numbers. This is structural-MEMORY operand-selection (retrieve similar solved scenario, reuse its solution shape),
  vs the global discriminative perceptron (~0.39 plateau). If ASDiv has schema-repetition, retrieval beats the global classifier; if
  novel schemas dominate, it doesn't (-> 4th triangulation angle = corpus-bound). ASDiv-1op. Substrate-only, no LLM.
PRE-REGISTERED (drill fail-band): HARD-PASS acc >= 0.49 (+0.10 over 0.39). MIDDLE 0.45-0.49 (+0.06-0.10). HARD-FAIL < 0.43 (<+0.04 ->
  corpus-deficiency confirmed at operand level, 4th independent angle; honest negative IS evidence per refined brain-can-do-it rule).
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
from collections import Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "path5_schema_retrieval_mwp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20, "dozen": 12}
CUES = ["each", "per", "every", "apiece", "total", "altogether", "all", "combined", "sum", "together", "both", "in all",
        "gave", "lost", "spent", "sold", "ate", "used", "left", "remain", "fewer", "away", "dropped", "broke",
        "got", "bought", "received", "found", "more", "picked", "another", "added", "gained",
        "share", "divide", "split", "equally", "each group", "times", "twice", "double",
        "more than", "fewer than", "less than", "difference", "how many more", "how much", "how many"]
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}


def _nums(text):
    out = []
    for w in re.split(r"[\s,]+", text.lower()):
        ww = w.replace("$", "").rstrip("?.!:;")
        if re.match(r"^\d+(?:\.\d+)?$", ww): out.append(Fraction(ww))
        elif ww in _WORDNUM: out.append(Fraction(_WORDNUM[ww]))
    return out


def _schema_feats(text):
    low = " " + text.lower() + " "
    fs = set(c.replace(" ", "_") for c in CUES if c in low)
    n = len(_nums(text))
    fs.add("nnum_%d" % min(n, 4))
    fs.add("qword_%s" % ("howmany" if "how many" in low else ("howmuch" if "how much" in low else "other")))
    # last verb-ish cue near the question
    return fs


def _gold_op(formula):
    lhs = formula.split("=")[0]
    for op in "+-*/":
        if op in lhs: return op
    return None


def _gold_order(formula):
    """from 'a OP b = c' return whether first operand > second (text-order in formula)."""
    m = re.match(r"\s*(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)", formula)
    if not m: return "lo_first"
    a = float(m.group(1)); b = float(m.group(3))
    return "hi_first" if a >= b else "lo_first"


def _solve(nums, op, order):
    cand = [x for x in nums if x != 0] or nums
    if len(cand) < 2: return cand[0] if cand else None
    a, b = cand[0], cand[1]
    if op in ("+", "*"): return OPS[op](a, b)
    hi, lo = (a, b) if a >= b else (b, a)
    x, y = (hi, lo) if order == "hi_first" else (lo, hi)
    return OPS[op](x, y)


def _jac(a, b):
    if not a and not b: return 0.0
    return len(a & b) / len(a | b)


def _selftest():
    assert _gold_op("7+2=9") == "+" and _gold_op("10-3=7") == "-"
    assert _gold_order("10-3=7") == "hi_first" and _gold_order("3-10=-7") == "lo_first"
    assert _solve([Fraction(10), Fraction(3)], "-", "hi_first") == Fraction(7)
    assert "each" in _schema_feats("each box has five apples") or "nnum_1" in _schema_feats("each box has five apples")
    print("[selftest] PASS: path5-schema-retrieval", flush=True)


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
        text = (e.get("body", "") + " " + e.get("question", "")).strip()
        items.append((text, f, Fraction(m.group()).limit_denominator(10**6)))
    return items


def run() -> Dict:
    try:
        items = _load_asdiv_1op()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    rng = np.random.default_rng(11); idx = rng.permutation(len(items))
    items = [items[i] for i in idx]
    if SMOKE: items = items[:300]
    cut = int(len(items) * 0.7); train, test = items[:cut], items[cut:]
    # schema store: (features, op, order) for each solved training scenario
    store = [(_schema_feats(t), _gold_op(f), _gold_order(f)) for t, f, _a in train]
    store = [(fs, op, od) for fs, op, od in store if op]
    K = 7 if not SMOKE else 5
    # global-prior baselines for comparison
    op_prior = Counter(op for _f, op, _o in store).most_common(1)[0][0]
    sch_cor = maj_cor = tot = 0
    for text, formula, ans in test:
        nums = _nums(text)
        if len(nums) < 2: continue
        tot += 1
        fs = _schema_feats(text)
        sims = sorted(((_jac(fs, sfs), op, od) for sfs, op, od in store), reverse=True)[:K]
        if sims and sims[0][0] > 0:
            wop = Counter(); word = Counter()
            for s, op, od in sims:
                wop[op] += s; word[od] += s
            pop = wop.most_common(1)[0][0]; pord = word.most_common(1)[0][0]
        else:
            pop = op_prior; pord = "hi_first"
        r = _solve(nums, pop, pord)
        sch_cor += int(r is not None and Fraction(r).limit_denominator(10**6) == ans)
        # majority-op baseline (no retrieval): always op_prior, magnitude order
        rm = _solve(nums, op_prior, "hi_first")
        maj_cor += int(rm is not None and Fraction(rm).limit_denominator(10**6) == ans)
    sch = sch_cor / tot if tot else 0.0; maj = maj_cor / tot if tot else 0.0
    print("  Path-5 schema-retrieval (k=%d): acc=%.4f (n=%d)" % (K, sch, tot), flush=True)
    print("  majority-op baseline (no retrieval): acc=%.4f" % maj, flush=True)
    print("  discriminative-perceptron plateau reference: ~0.39", flush=True)
    print("  schema-retrieval lift over 0.39 baseline = %+.4f" % (sch - 0.39), flush=True)
    return {"f1": round(sch, 4), "accuracy": round(sch, 4), "schema_acc": round(sch, 4), "majority_acc": round(maj, 4),
            "lift_over_baseline": round(sch - 0.39, 4), "n": tot, "k": K}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["schema_acc"]; s = "schema-retrieval acc=%.4f (majority-op %.4f, n=%d, k=%d) vs discriminative ~0.39" % (a, r["majority_acc"], r["n"], r["k"])
    if a >= 0.49:
        return ("HARD_PASS", "HARD_PASS: hippocampal schema retrieval lifts operand-selection >=+0.10 over 0.39 -- structural memory beats global classifier; ASDiv schema-repetition exploitable. " + s)
    if a >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: schema retrieval +0.06-0.10 -- partial operand-selection win via structural memory. " + s)
    return ("HARD_FAIL", "HARD_FAIL: schema retrieval <+0.04 over 0.39 -- structural-memory retrieval does NOT break the operand-selection plateau; 4th INDEPENDENT triangulation angle = MWP plateau is corpus/comprehension-bound (per brain-can-do-it refined rule, honest negative IS evidence; supports Phase-6 math+science ingestion). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
