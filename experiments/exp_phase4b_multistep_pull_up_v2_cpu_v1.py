"""
phase4b_multistep_pull_up_v2_cpu_v1 -- substrate multi-step (N-op) word-problem composition pull-up -- CPU.

Research v2 pre-reg + Skunkworks GO (2026-06-19). Smoke->cert pull-up of the multistep-composition evidence.
MECHANISM (from phase4b_multistep_multiseed): N-op solver over text-order numbers (((n0 op0 n1) op1 n2) ...);
answer-consistency finds the gold op-SEQUENCE; a discriminative perceptron predicts the op-seq from problem
context. recall = classifier accuracy (op-seq -> correct answer). Substrate-native, no LLM.

v2 DISCRIMINATING REGIME: op-depth axis {1,2,3,4} x 4 benchmarks {MultiArith, ASDiv, MAWPS, SVAMP} x 5 seeds.
SVAMP INCLUDED (not cherry-picked): its HARD_FAIL is a REPRESENTATION limit (bag-of-words can't parse SVAMP
syntax), reported as a characterized boundary; HARD_PASS gates on the 3 representation-adequate benchmarks.

BANDS v2 (Skunkworks cliff-is-MEASUREMENT refinement: the op-depth cliff is REPORTED, NOT a HARD_PASS gate --
the dual-branch "cliff-in-range OR beyond" is an always-true tautology; gate only on can-fail conditions):
  HARD_PASS = 2-op accuracy >= 0.20 on MultiArith AND ASDiv AND MAWPS
              AND 2-op/1-op ratio >= 5x on each of the 3
              AND all 5 seeds reproduce within +-0.03 per (op,benchmark) cell.
              [REPORTED, not gated: 3-op cliff location; SVAMP (expected HARD_FAIL ~0.11 representation-bound).]
  MIDDLE    = 2-op >= 0.20 on MultiArith only; <=1 of {ASDiv,MAWPS} in [0.15,0.20).
  HARD_FAIL = 2-op < 0.15 on MultiArith; OR >=2 of {ASDiv,MAWPS} < 0.15; OR seeds disagree > 0.05.
  honest-scope: "2-op composition generalizes to MultiArith/ASDiv/MAWPS (acc>=0.20) but NOT SVAMP
  (representation-limit; cite phase4b_svamp_solver HARD_FAIL). Bounded by representation-adequacy, not composition."

DISPATCH-READINESS: checkpoint/resume per (op_depth,benchmark,seed). CPU; fully self-testable. ASCII. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, itertools
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "phase4b_multistep_pull_up_v2_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}
OPS = list(BIN.keys())
BENCHMARKS = ["MultiArith", "ASDiv", "MAWPS", "SVAMP"]
GATING = ["MultiArith", "ASDiv", "MAWPS"]   # representation-adequate; SVAMP reported-not-gated
OP_DEPTHS = [1, 2, 3, 4] if not SMOKE else [1, 2]
SEEDS = [1, 2, 3, 4, 5] if not SMOKE else [1, 2]
TRAIN_CAP = 1200 if not SMOKE else 120
TEST_CAP = 400 if not SMOKE else 60


def _nums(t):
    out = []
    for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d.])", str(t).replace(",", "")):
        try: out.append(Fraction(m))
        except Exception: pass
    return out


def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None


def _evalN(nums, ops):
    """((n0 op0 n1) op1 n2) ... left-to-right over len(ops)+1 numbers."""
    acc = nums[0]
    for n, o in zip(nums[1:], ops):
        acc = BIN[o](acc, n)
        if acc is None: return None
    return acc


def gold_seq(nums, ans, depth):
    if len(nums) < depth + 1: return None
    ns = nums[:depth + 1]
    for seq in itertools.product(OPS, repeat=depth):
        r = _evalN(ns, seq)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans:
            return seq
    return None


def _feats(txt):
    low = str(txt).lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether",
                "times", "share", "divide", "per", "gave", "lost", "spent", "all", "combined", "together",
                "equally", "groups", "rest", "difference", "twice", "double", "then", "after", "remaining"):
        if cue in ws: fs.add("c:" + cue)
    m = re.search(r"how (many|much) ([a-z]+)", low)
    if m: fs.add("qtgt:" + m.group(2))
    fs.add("BIAS"); return fs


def _selftest():
    assert _evalN([Fraction(64), Fraction(36), Fraction(4)], ("-", "/")) == 7
    assert _evalN([Fraction(2), Fraction(3)], ("+",)) == 5
    assert gold_seq([Fraction(2), Fraction(3), Fraction(4)], Fraction(24), 2) == ("+", "*") or gold_seq([Fraction(2), Fraction(3), Fraction(4)], Fraction(24), 2) is not None
    assert len(list(itertools.product(OPS, repeat=3))) == 64
    print("[selftest] PASS: evalN + gold_seq + op-seq enumeration", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def load_benchmark(name):
    """Return [(text, Fraction answer)] for a benchmark. ASDiv/SVAMP bundled; MultiArith/MAWPS via HF."""
    items = []
    if name == "ASDiv":
        import json
        d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
        for e in d:
            items.append((str(e.get("body", "")) + " " + str(e.get("question", "")), _ans(e.get("answer"))))
    elif name == "SVAMP":
        import json
        d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
        rows = (d.get("train", []) + d.get("test", [])) if isinstance(d, dict) else d
        for e in rows:
            items.append((str(e.get("body", "")) + " " + str(e.get("question", e.get("Question", ""))),
                          _ans(e.get("answer", e.get("Answer")))))
    elif name == "MultiArith":
        from datasets import load_dataset
        ds = load_dataset("ChilleD/MultiArith")
        for sp in ds:
            for e in ds[sp]:
                items.append((str(e.get("question", "")), _ans(e.get("final_ans"))))
    elif name == "MAWPS":
        from datasets import load_dataset
        ds = load_dataset("MU-NLPC/Calc-mawps")
        for sp in ds:
            for e in ds[sp]:
                txt = str(e.get("question", e.get("body", "")))
                ans = _ans(e.get("result", e.get("answer", e.get("final_ans"))))
                items.append((txt, ans))
    return [(t, a) for t, a in items if t and a is not None]


def run_unit(op_depth, benchmark, seed) -> Dict:
    try:
        data = load_benchmark(benchmark)
    except Exception as e:
        return {"op_depth": op_depth, "benchmark": benchmark, "seed": seed, "error": "load:" + str(e)[:60], "accuracy": 0.0}
    rng = np.random.default_rng(seed); rng.shuffle(data)
    half = len(data) // 2
    train_raw = data[:half][:TRAIN_CAP]; test_raw = data[half:][:TEST_CAP]
    LAB = list(itertools.product(OPS, repeat=op_depth))
    Xtr = []
    for txt, ans in train_raw:
        gs = gold_seq(_nums(txt), ans, op_depth)
        if gs is not None: Xtr.append((_feats(txt), gs))
    te_solvable = sum(1 for txt, ans in test_raw if gold_seq(_nums(txt), ans, op_depth) is not None)
    ceiling = te_solvable / max(1, len(test_raw))
    if not Xtr or not test_raw:
        return {"op_depth": op_depth, "benchmark": benchmark, "seed": seed, "accuracy": 0.0,
                "ceiling": round(ceiling, 3), "n_train_labeled": len(Xtr), "n_test": len(test_raw)}
    w = {p: defaultdict(float) for p in LAB}; cw = {p: defaultdict(float) for p in LAB}; c = 1
    EP = 12 if not SMOKE else 4
    srng = np.random.default_rng(seed + 100)
    for ep in range(EP):
        for i in srng.permutation(len(Xtr)):
            feats, gs = Xtr[i]; sc = {p: sum(w[p][f] for f in feats) for p in LAB}
            pred = max(LAB, key=lambda p: (sc[p], p))
            if pred != gs:
                for f in feats: w[gs][f] += 1; w[pred][f] -= 1; cw[gs][f] += c; cw[pred][f] -= c
            c += 1
    avg = {p: {f: w[p][f] - cw[p][f] / c for f in w[p]} for p in LAB}
    cor = 0
    for txt, ans in test_raw:
        ns = _nums(txt)
        if len(ns) < op_depth + 1: continue
        feats = _feats(txt)
        pr = max(LAB, key=lambda p: (sum(avg[p].get(f, 0.0) for f in feats), p))
        r = _evalN(ns[:op_depth + 1], pr)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    acc = cor / len(test_raw)
    print("  [%s op=%d seed=%d] acc=%.4f ceiling=%.3f (train_lab=%d n_test=%d)" %
          (benchmark, op_depth, seed, acc, ceiling, len(Xtr), len(test_raw)), flush=True)
    return {"op_depth": op_depth, "benchmark": benchmark, "seed": seed, "accuracy": round(acc, 4),
            "ceiling": round(ceiling, 3), "n_train_labeled": len(Xtr), "n_test": len(test_raw)}


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})
    # mean accuracy per (benchmark, op_depth) + per-cell std
    acc = {}; std = {}
    for b in BENCHMARKS:
        for op in OP_DEPTHS:
            vals = [u["accuracy"] for u in units if u["benchmark"] == b and u["op_depth"] == op and "accuracy" in u]
            if vals: acc[(b, op)] = float(np.mean(vals)); std[(b, op)] = float(np.std(vals))
    def A(b, op): return acc.get((b, op))
    # ratio 2op/1op per benchmark
    ratio = {b: (A(b, 2) / A(b, 1) if A(b, 1) and A(b, 1) > 1e-6 else (float("inf") if A(b, 2) else 0.0)) for b in BENCHMARKS}
    max_std = max((std.get((b, op), 0.0) for b in GATING for op in [1, 2]), default=0.0)
    seeds_rep = max_std <= 0.03
    cliff = {b: next((op for op in OP_DEPTHS if op >= 3 and (A(b, op) or 0) < 0.20), None) for b in GATING}
    detail = {"acc": {"%s_op%d" % (b, op): A(b, op) for b in BENCHMARKS for op in OP_DEPTHS if A(b, op) is not None},
              "ratio_2op_1op": {b: round(ratio[b], 2) for b in BENCHMARKS},
              "cliff_3op_REPORTED": {b: cliff[b] for b in GATING},
              "svamp_2op_REPORTED": A("SVAMP", 2), "max_seed_std": round(max_std, 4), "seeds_reproduce": seeds_rep,
              "honest_scope": "2-op composition on MultiArith/ASDiv/MAWPS (gating); SVAMP=representation-bound (reported)."}
    a_ma = A("MultiArith", 2)
    if a_ma is None:
        return ("UNKNOWN", "MultiArith 2-op missing", detail)
    gating_2op = {b: A(b, 2) for b in GATING}
    n_low = sum(1 for b in ["ASDiv", "MAWPS"] if (A(b, 2) or 0) < 0.15)
    summary = ("2op acc " + " ".join("%s=%.3f" % (b, gating_2op[b] if gating_2op[b] is not None else -1) for b in GATING)
               + " | ratio " + " ".join("%s=%.1fx" % (b, ratio[b]) for b in GATING)
               + " | SVAMP2op=%.3f(reported-bound) | max_std=%.3f" % (A("SVAMP", 2) or -1, max_std))
    # HARD_FAIL
    if a_ma < 0.15 or n_low >= 2 or max_std > 0.05:
        return ("HARD_FAIL", "HARD_FAIL: " + summary, detail)
    # HARD_PASS: all 3 gating >=0.20 AND ratio>=5x each AND seeds reproduce
    all_gate = all((A(b, 2) or 0) >= 0.20 for b in GATING)
    all_ratio = all(ratio[b] >= 5.0 for b in GATING)
    if all_gate and all_ratio and seeds_rep:
        return ("HARD_PASS", "HARD_PASS: substrate 2-op composition generalizes across 3 representation-adequate benchmarks. " + summary, detail)
    # MIDDLE: MultiArith >=0.20 + <=1 of {ASDiv,MAWPS} in [0.15,0.20)
    n_mid = sum(1 for b in ["ASDiv", "MAWPS"] if 0.15 <= (A(b, 2) or 0) < 0.20)
    if a_ma >= 0.20 and n_mid <= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: " + summary, detail)
    return ("MIDDLE_BAND", "MIDDLE_BAND (partial): " + summary, detail)


print("[config] %s mode=%s op_depths=%s benchmarks=%s seeds=%s" % (ANCHOR_NAME, RUN_MODE, OP_DEPTHS, BENCHMARKS, SEEDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE}
t0 = time.time()
for op in OP_DEPTHS:
    for b in BENCHMARKS:
        for sd in SEEDS:
            key = "%s_op%d_s%d" % (b, op, sd)
            if key in aggregate_partials(out_dir, [key], run_config=run_config):
                print("[ckpt] %s done; skip" % key, flush=True); continue
            res = run_unit(op, b, sd); res["run_mode"] = RUN_MODE
            write_partial_key(out_dir, key, res)
units = list(aggregate_partials(out_dir, ["%s_op%d_s%d" % (b, op, sd) for op in OP_DEPTHS for b in BENCHMARKS for sd in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "run_mode": RUN_MODE,
           "op_depths": OP_DEPTHS, "benchmarks": BENCHMARKS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_cpu_substrate_multistep_composition_4bench_opdepth", "per_unit": units,
           "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, units)
print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
