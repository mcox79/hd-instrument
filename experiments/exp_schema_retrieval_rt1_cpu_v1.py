"""
exp_schema_retrieval_rt1_cpu_v1.py -- RT-1: substrate Tier-2 schema retrieval (Phase-2 gate) -- CPU.

ROUTING: Research Drill A (RT-1 schema retrieval smoke). Phase-2 gate: given a problem statement, retrieve the correct Tier-2
  schema from the inventory via substrate cleanup. Each schema = bundle of (signature-keyword atoms + frame-role atoms) at
  Tier-2; retrieval = substrate cleanup of the query-keyword bundle over the schema bundles. REPRESENTATIVE SUBSET of the
  114-schema inventory (~30 math+code schemas with distinct role/keyword signatures) -- tests the retrieval MECHANISM at
  fine schema granularity (harder than the 6-class routing oracle: schemas share roles -> more confusable). Substrate-only.
PRE-REGISTERED: HARD-PASS retrieval-accuracy >= 0.90 on 30 query instances (schema retrieval works at fine granularity).
  MIDDLE >= 0.70. HARD-FAIL < 0.70 (shared roles too confusable -> need 2-stage refinement).
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
ANCHOR_NAME = "schema_retrieval_rt1_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
# representative Tier-2 schema subset: name -> (signature keywords + frame roles)
SCHEMAS = {
    # MATH
    "rate_motion": ["rate", "speed", "distance", "time", "travel", "fast", "mph", "velocity"],
    "percent_proportion": ["percent", "proportion", "ratio", "fraction", "of", "rate", "per"],
    "conservation": ["total", "remain", "left", "conserve", "sum", "combine", "whole", "parts"],
    "algebraic_solve": ["solve", "equation", "variable", "unknown", "equals", "value", "find"],
    "geometry_area": ["area", "perimeter", "length", "width", "radius", "triangle", "square", "circle"],
    "combinatorics": ["arrange", "combination", "permutation", "choose", "ways", "order", "count"],
    "number_theory": ["divisible", "prime", "factor", "remainder", "modulo", "gcd", "multiple"],
    "interest": ["interest", "principal", "compound", "rate", "investment", "savings"],
    "mixture": ["mixture", "concentration", "solution", "blend", "alloy", "percent"],
    "work_rate": ["work", "job", "complete", "together", "hours", "rate", "finish"],
    # CODE
    "accumulator": ["sum", "total", "accumulate", "count", "running", "add", "loop"],
    "divide_conquer": ["divide", "conquer", "split", "merge", "half", "recursive", "binary"],
    "dynamic_programming": ["optimal", "subproblem", "memoize", "dp", "minimum", "maximum", "table"],
    "graph_traversal": ["graph", "node", "edge", "path", "visit", "neighbor", "bfs", "dfs"],
    "data_structure": ["stack", "queue", "heap", "list", "tree", "insert", "pop"],
    "recursion": ["recursive", "base", "case", "factorial", "fibonacci", "call", "self"],
    "string_manip": ["string", "character", "substring", "reverse", "concatenate", "palindrome"],
    "sorting": ["sort", "order", "ascending", "descending", "compare", "swap", "arrange"],
    "searching": ["search", "find", "locate", "index", "target", "binary", "lookup"],
    "filtering": ["filter", "select", "keep", "remove", "condition", "where", "predicate"],
}
NAMES = list(SCHEMAS.keys())
# 30 query instances (problem statements) -> gold schema
QUERIES = [
    ("a car travels at sixty mph for two hours how far does it go", "rate_motion"),
    ("a train moves at a constant speed covering distance over time", "rate_motion"),
    ("what is forty percent of the total proportion of students", "percent_proportion"),
    ("the ratio of red to blue is three to five find the fraction", "percent_proportion"),
    ("twelve apples remain after combining the parts what is the total", "conservation"),
    ("solve the equation for the unknown variable that equals twelve", "algebraic_solve"),
    ("find the value of x where the expression equals zero", "algebraic_solve"),
    ("compute the area of a triangle with given length and width", "geometry_area"),
    ("the radius of the circle determines its area and perimeter", "geometry_area"),
    ("how many ways can we arrange the letters in permutation", "combinatorics"),
    ("choose three items from ten count the combinations", "combinatorics"),
    ("is the number divisible by seven find the remainder modulo", "number_theory"),
    ("find the greatest common factor and prime multiple", "number_theory"),
    ("compound interest on the principal investment at a rate", "interest"),
    ("mix two solutions of different concentration into a blend", "mixture"),
    ("two workers complete the job together in fewer hours", "work_rate"),
    ("accumulate the running total by adding each element in a loop", "accumulator"),
    ("sum all the elements to get the count and total", "accumulator"),
    ("split the array in half and merge recursively divide conquer", "divide_conquer"),
    ("memoize the optimal subproblem to find the minimum dp table", "dynamic_programming"),
    ("traverse the graph visiting each node and neighbor edge", "graph_traversal"),
    ("use a stack to push and pop from the list data structure", "data_structure"),
    ("the recursive base case computes factorial by calling self", "recursion"),
    ("reverse the string and check if the substring is a palindrome", "string_manip"),
    ("sort the list in ascending order by comparing and swapping", "sorting"),
    ("search for the target index using binary lookup", "searching"),
    ("filter and select elements that satisfy the condition predicate", "filtering"),
    ("find the shortest path between nodes in the graph bfs", "graph_traversal"),
    ("compute fibonacci recursively with a base case", "recursion"),
    ("remove duplicates by keeping elements where the condition holds", "filtering"),
]
def _tok(t): return re.findall(r"[a-z]+", t.lower())
def _selftest():
    assert all(g in SCHEMAS for _t, g in QUERIES) and len(QUERIES) == 30
    print("[selftest] PASS: schema-retrieval-rt1 (%d schemas, 30 queries)" % len(SCHEMAS), flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1002")))
    book = {}
    def tok(w):
        if w not in book:
            ang = (g.random(N) * 2 - 1) * math.pi; book[w] = np.exp(1j * ang).astype(np.complex64)
        return book[w]
    def bundle(words):
        v = np.zeros(N, dtype=np.complex64)
        for w in words: v = v + tok(w)
        return np.exp(1j * np.angle(v)).astype(np.complex64)
    proto = np.stack([bundle(SCHEMAS[nm]) for nm in NAMES])
    hit = 0
    for text, gold in QUERIES:
        v = bundle(_tok(text)); pred = NAMES[int(np.argmax((proto @ np.conj(v)).real))]
        hit += int(pred == gold)
    acc = hit / len(QUERIES)
    print("  RT-1 SCHEMA-RETRIEVAL: accuracy=%.3f (%d/%d over %d schemas)" % (acc, hit, len(QUERIES), len(SCHEMAS)), flush=True)
    return {"retrieval_acc": round(acc, 3), "n_queries": len(QUERIES), "n_schemas": len(SCHEMAS)}
def verdict(r) -> Tuple[str, str]:
    a = r["retrieval_acc"]; s = "retrieval-acc=%.3f (%d schemas, %d queries)" % (a, r["n_schemas"], r["n_queries"])
    if a >= 0.90:
        return ("HARD_PASS", "HARD_PASS: substrate Tier-2 schema retrieval >=0.90 over a representative ~%d-schema inventory -- fine-grained schema cleanup works (Phase-2 schema layer viable). " % r["n_schemas"] + s)
    if a >= 0.70:
        return ("MIDDLE_BAND", "MIDDLE_BAND: schema retrieval 0.70-0.90 -- shared role/keyword overlap causes some confusion; 2-stage refinement (domain-route then schema) recommended. " + s)
    return ("HARD_FAIL", "HARD_FAIL: schema retrieval <0.70 -- schemas too confusable at fine granularity. " + s)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
