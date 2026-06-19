"""
exp_e4_world_model_mwp_cpu_v1.py -- E4: world-model (schema-simulation) MWP solver, 1-op -- CPU.

ROUTING: Research E4 design sketch (research_to_exp_dev_E3b_HARDPASS_E4_DESIGN_INPUT). NEW mechanism class beyond the discriminative-
  perceptron family (which plateaus ~0.39 on ASDiv-1op). World-model = the substrate maps the described SCENARIO to a canonical
  schema (EQUAL_GROUPS / COMBINE / CHANGE_ADD / CHANGE_SUBTRACT / COMPARE / SHARE / TIMES), each schema carries its operation as WORLD
  KNOWLEDGE (not learned), then simulates: instantiate slots with the extracted numbers, apply the schema operation, output the state.
  Per USER brain-can-do-it rule: brain solves MWPs by mental simulation of scenarios; this tests the SUBSTRATE-equivalent mechanism
  class rather than pre-accepting the 0.39 plateau as a comprehension ceiling. Zero-shot (schema = world knowledge, no training) vs the
  trained discriminative baseline. ASDiv-1op. Substrate-only, no LLM.
PRE-REGISTERED (Research): HARD-PASS ASDiv-1op >= 0.50 (world-model breaks the discriminative 0.39 plateau). MIDDLE 0.40-0.50.
  HARD-FAIL <= 0.40 (schema op-mapping ~= discriminative -> plateau is comprehension/selection-bound NOT mechanism-bound; honest
  brain-can-do-it evidence the bottleneck is corpus/selection, supports math+science ingestion). UNKNOWN if load fails.
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
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "e4_world_model_mwp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
            "hundred": 100, "dozen": 12, "half": Fraction(1, 2), "double": 2, "twice": 2}

# schema = (cue words/phrases, operation). World knowledge: the scenario determines the canonical operation.
SCHEMAS = [
    ("SHARE", ["share", "divide", "split", "equally", "each group", "per group", "into groups", "distribut"], "/"),
    ("EQUAL_GROUPS", ["each", "per", "every", "apiece", "a piece", "in each", "rows of", "boxes of", "bags of", "times as"], "*"),
    ("TIMES", [" times", "twice as", "double", "triple", "multiplied"], "*"),
    ("COMPARE", ["more than", "fewer than", "less than", "difference", "how many more", "how many fewer", "taller", "shorter", "older", "younger", "farther"], "-"),
    ("CHANGE_SUB", ["gave", "lost", "spent", "sold", "ate", "used", "removed", "left", "remain", "broke", "dropped", "away", "fell", "took away", "gives", "gave away", "fly away", "flew", "destroyed", "melted", "popped"], "-"),
    ("CHANGE_ADD", ["got", "bought", "received", "found", "added", "gained", "more", "picked", "another", "buys", "gets", "receives", "gives him", "join", "came", "born", "planted"], "+"),
    ("COMBINE", ["total", "altogether", "in all", "combined", "sum", "together", "both", "and", "all"], "+"),
]


def _nums(text):
    out = []
    for w in re.split(r"[\s,]+", text.lower()):
        ww = w.replace("$", "").replace("%", "").rstrip("?.!:;")
        if re.match(r"^\d+(?:\.\d+)?$", ww): out.append(Fraction(ww))
        elif ww in _WORDNUM and isinstance(_WORDNUM[ww], (int, Fraction)): out.append(Fraction(_WORDNUM[ww]))
    return out


def classify(text):
    low = " " + text.lower() + " "
    for name, cues, op in SCHEMAS:
        for c in cues:
            if c in low: return name, op
    return "COMBINE", "+"  # default world-model: combining quantities


OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}


def simulate(nums, op):
    """instantiate the schema with the two principal numbers and apply the operation; for -, / pick the order giving a
    positive (and, where possible, integer) result -- world-model produces a concrete non-negative final state."""
    cand = [n for n in nums if n != 0] or nums
    if len(cand) < 2:
        return cand[0] if cand else None
    a, b = cand[0], cand[1]  # text order (first two non-zero)
    if op in ("+", "*"):
        return OPS[op](a, b)
    # -, / : order matters; prefer larger-first for a non-negative/whole result
    hi, lo = (a, b) if a >= b else (b, a)
    r = OPS[op](hi, lo)
    return r


def solve(text):
    nums = _nums(text)
    if len(nums) < 2: return None
    _name, op = classify(text)
    return simulate(nums, op)


def _selftest():
    assert solve("Seven red apples and two green apples are in the basket . how many apples ?") == Fraction(9)
    assert solve("Each box has five apples . There are three boxes . how many apples ?") == Fraction(15)
    assert solve("Tom had ten apples and gave three away . how many left ?") == Fraction(7)
    print("[selftest] PASS: e4-world-model-mwp", flush=True)


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
    cor = tot = 0; by_op = {}
    for text, ans in items:
        tot += 1; pred = solve(text)
        ok = (pred is not None and Fraction(pred).limit_denominator(10**6) == ans)
        cor += int(ok)
        _n, op = classify(text); by_op.setdefault(op, [0, 0]); by_op[op][0] += int(ok); by_op[op][1] += 1
    acc = cor / tot if tot else 0.0
    op_acc = {o: round(v[0] / v[1], 3) for o, v in by_op.items()}
    print("  E4 world-model schema-simulation: ASDiv-1op acc=%.4f (n=%d) vs discriminative ~0.39 plateau" % (acc, tot), flush=True)
    print("  per-op acc (n): %s" % {o: "%s (%d)" % (op_acc[o], by_op[o][1]) for o in op_acc}, flush=True)
    return {"f1": round(acc, 4), "accuracy": round(acc, 4), "n": tot, "op_acc": op_acc, "disc_plateau": 0.39}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "ASDiv-1op acc=%.4f (n=%d, per-op %s) vs discriminative ~0.39" % (a, r["n"], r["op_acc"])
    if a >= 0.50:
        return ("HARD_PASS", "HARD_PASS: world-model schema-simulation breaks the discriminative 0.39 plateau (>=0.50) -- new mechanism class adds beyond discriminative; world-knowledge schemas help. " + s)
    if a >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: world-model 0.40-0.50 -- modest gain over discriminative plateau. " + s)
    return ("HARD_FAIL", "HARD_FAIL: world-model schema <=0.40 ~= discriminative plateau -- HONEST brain-can-do-it evidence the 1-op MWP bottleneck is comprehension/operand-selection (corpus-bound per BMA), NOT the op-mapping mechanism; supports math+science ingestion strategy. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
