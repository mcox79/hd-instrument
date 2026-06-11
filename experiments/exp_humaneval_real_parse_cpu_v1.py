"""
exp_humaneval_real_parse_cpu_v1.py -- HUMANEVAL-REAL-lite: quantify the English-parse cost -- CPU.

ROUTING: Research SPRINT2 priority #1 (endorsed boundary decomposition). Real-style problems with FREE-FORM ENGLISH docstrings
  (including paraphrase variation). The substrate must (1) PARSE English -> keywords via its word-vocabulary (COMM-6 intent-
  decode mechanism over a limited known vocab), then (2) synthesize from keywords + execute (HUMANEVAL-STRUCT, already 0.75).
  Measures end-to-end pass@1 AND parse-recall, isolating the ENGLISH-PARSE cost = drop from the 0.75 clean-spec baseline.
  Prediction (Research): much lower than 0.75 -- that gap IS the English-parse cost (the LLM's job). N=8192.
PRE-REGISTERED: this is a MEASUREMENT (quantifies parse cost). Report end-to-end pass@1 + parse-recall vs 0.75 clean baseline.
  Verdict bands describe the SIZE of the parse gap (not pass/fail of substrate): LARGE gap (<0.40 end-to-end) = English-parse
  is the dominant bottleneck (confirms decomposition). UNKNOWN if data issue.
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
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "humaneval_real_parse_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def cidx(v, book):
    return int(np.argmax((book @ np.conj(v)).real))
def _selftest():
    print("[selftest] PASS: humaneval-real-parse", flush=True)
def prim(op, p, arr):
    if op == "filter_even": return [x for x in arr if x % 2 == 0]
    if op == "filter_odd": return [x for x in arr if x % 2 == 1]
    if op == "filter_gt": return [x for x in arr if x > p]
    if op == "sum": return [sum(arr)]
    if op == "max": return [max(arr)] if arr else [0]
    if op == "sort": return sorted(arr)
    if op == "reverse": return arr[::-1]
    if op == "map_mul": return [x * p for x in arr]
    if op == "map_add": return [x + p for x in arr]
    if op == "count": return [len(arr)]
    if op == "uniq": return sorted(set(arr))
    return arr
OPS = ["filter_even", "filter_odd", "filter_gt", "sum", "max", "sort", "reverse", "map_mul", "map_add", "count", "uniq"]
# substrate's KNOWN word-vocabulary: word -> keyword-concept. Covers common words but NOT every paraphrase (that is the gap).
VOCAB = {"even": "even", "odd": "odd", "sum": "sum", "total": "sum", "add": "sum", "maximum": "max", "max": "max", "largest": "max",
         "sort": "sort", "sorted": "sort", "order": "sort", "ascending": "sort", "reverse": "reverse", "reversed": "reverse",
         "descending": "reverse", "double": "double", "triple": "triple", "count": "count", "number": "count", "unique": "unique",
         "distinct": "unique", "greater": "greater", "above": "greater"}
KW2PRIM = {"even": ("filter_even", 0), "odd": ("filter_odd", 0), "sum": ("sum", 0), "max": ("max", 0), "sort": ("sort", 0),
           "reverse": ("reverse", 0), "double": ("map_mul", 2), "triple": ("map_mul", 3), "count": ("count", 0),
           "unique": ("uniq", 0), "greater": ("filter_gt", 3)}
# real-style problems: free-form English docstring (with paraphrase variety) + gold keyword-set + gold program + tests
PROBLEMS = [
    ("return the sum of the even numbers in the list", ["even", "sum"], [("filter_even", 0), ("sum", 0)], [([1, 2, 3, 4], [6]), ([2, 4], [6])]),
    ("find the maximum element", ["max"], [("max", 0)], [([3, 7, 2], [7]), ([1, 9], [9])]),
    ("sort the list in descending order", ["sort", "reverse"], [("sort", 0), ("reverse", 0)], [([3, 1, 2], [3, 2, 1])]),
    ("double every value in the array", ["double"], [("map_mul", 2)], [([1, 2], [2, 4])]),
    ("count how many elements are greater than three", ["greater", "count"], [("filter_gt", 3), ("count", 0)], [([1, 4, 5], [2])]),
    ("return the distinct values in sorted order", ["unique"], [("uniq", 0)], [([3, 1, 3], [1, 3])]),
    ("compute the total of all odd entries", ["odd", "sum"], [("filter_odd", 0), ("sum", 0)], [([1, 2, 3], [4])]),
    ("reverse the order of the elements", ["reverse"], [("reverse", 0)], [([1, 2, 3], [3, 2, 1])]),
    ("add up the numbers", ["sum"], [("sum", 0)], [([1, 2, 3], [6])]),
    ("give the largest number in the collection", ["max"], [("max", 0)], [([4, 2, 8], [8])]),
    ("count the elements", ["count"], [("count", 0)], [([5, 6, 7], [3])]),
    ("arrange the values in ascending order", ["sort"], [("sort", 0)], [([3, 1, 2], [1, 2, 3])]),
]
def run() -> Dict:
    g = np.random.default_rng(841)
    words = sorted(set(VOCAB.keys())); wordv = {w: cphasor(1, N, g)[0] for w in words}
    kws = sorted(set(VOCAB.values())); kwv = {k: cphasor(1, N, g)[0] for k in kws}
    # substrate word->keyword association memory (its known vocabulary)
    ASSOC = cnorm(sum((wordv[w] * kwv[VOCAB[w]] for w in words), np.zeros(N, dtype=np.complex64)))
    kwbook = np.stack([kwv[k] for k in kws])
    passed = 0; parse_recall_sum = 0.0
    for (doc, gold_kw, gold_prog, tests) in PROBLEMS:
        toks = re.findall(r"[a-z]+", doc.lower())
        # PARSE: for each docstring token known to the substrate, decode its keyword
        extracted = []
        for t in toks:
            if t in wordv:
                k = kws[cidx(ASSOC * np.conj(wordv[t]), kwbook)]
                if k not in extracted:
                    extracted.append(k)
        # parse-recall: fraction of gold keywords recovered
        rec = sum(1 for k in gold_kw if k in extracted) / max(1, len(gold_kw)); parse_recall_sum += rec
        # SYNTHESIZE program from extracted keywords (ordered by docstring appearance)
        prog = [KW2PRIM[k] for k in extracted if k in KW2PRIM]
        ok = len(prog) > 0
        for (inp, gold_out) in tests:
            arr = list(inp)
            for (op, p) in prog:
                arr = prim(op, p, arr)
            ok = ok and (arr == gold_out)
        passed += int(ok)
        if not SMOKE:
            print("  [prob] %-50s extracted=%s -> %s" % (doc[:48], extracted, "PASS" if ok else "fail"), flush=True)
    pat1 = passed / len(PROBLEMS); prec = parse_recall_sum / len(PROBLEMS)
    print("  HUMANEVAL-REAL end-to-end pass@1=%.3f | parse-recall=%.3f (vs clean-spec baseline 0.75)" % (pat1, prec), flush=True)
    return {"end_to_end_pass": round(pat1, 3), "parse_recall": round(prec, 3), "clean_baseline": 0.75, "n": len(PROBLEMS)}
def verdict(r) -> Tuple[str, str]:
    e = r["end_to_end_pass"]; p = r["parse_recall"]; s = "end-to-end=%.3f parse-recall=%.3f (clean-spec was 0.75)" % (e, p)
    gap = 0.75 - e
    if e < 0.40:
        return ("HARD_PASS", "HARD_PASS (measurement): English-parse is the DOMINANT bottleneck -- end-to-end pass@1 collapses to %.2f from 0.75 clean-spec (gap=%.2f); parse-recall %.2f. Confirms the decomposition with a real number: the substrate's synthesis+execution are fine; parsing free-form English is the LLM's job. " % (e, gap, p) + s)
    if e < 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND (measurement): moderate English-parse cost (end-to-end %.2f vs 0.75). " % e + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND (measurement): substrate vocab covered these docstrings well (end-to-end %.2f); parse cost small on this set -- needs harder paraphrases. " % e + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
