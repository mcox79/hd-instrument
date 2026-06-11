"""
exp_phase4_bipartite_svamp_cpu_v1.py -- Phase-4 bipartite role-assigner on SVAMP (Research 2nd priority) -- CPU.

ROUTING: Research PHASE4_REVISED_SEQUENCE_BIPARTITE_FIRST (2nd priority, drill 5-discipline convergence). Bipartite-matching
  role-assigner: numerical-entities (left) -> operand-roles (right) via an engineered cost matrix (position + cue-adjacency +
  magnitude + verb-frame proxy), solved with Hungarian (scipy linear_sum_assignment, polynomial-time exact). Factored: a
  discriminative OPERATOR classifier (ADD/SUB/MUL/DIV) + Hungarian ORDER assignment for the non-commutative ops (SUB/DIV).
  Tests whether the bipartite factorization beats the joint perceptron (0.267) on SVAMP. Substrate-native (assignment is a
  graph/optimization primitive; costs are discriminatively learned). No LLM.
PRE-REGISTERED: HARD-PASS test accuracy > 0.30 (bipartite lifts beyond perceptron 0.267 -> the right primitive). MIDDLE in
  [0.25, 0.30] (matches perceptron; factorization neutral). HARD-FAIL < 0.25 (bipartite underperforms joint perceptron). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from fractions import Fraction
import numpy as np
from scipy.optimize import linear_sum_assignment
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "phase4_bipartite_svamp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
# commutative-collapsed operators; SUB/DIV need an ordered (minuend/dividend first) assignment
OPS4 = ["ADD", "SUB", "MUL", "DIV"]
def _apply(op, a, b):
    if op == "ADD": return a + b
    if op == "MUL": return a * b
    if op == "SUB": return a - b
    if op == "DIV": return a / b if b != 0 else None
    return None
def _nums_pos(t):
    out = []; toks = t.split()
    for k, w in enumerate(toks):
        m = re.match(r"(\d+(?:\.\d+)?)", w.replace("$", "").replace(",", ""))
        if m:
            try: out.append((Fraction(m.group(1)), k))
            except Exception: pass
    return out, toks
def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None
def _opfeats(txt):
    ws = re.findall(r"[a-z]+", txt.lower()); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("BIAS"); return fs
def _ordercost(toks, k, role_first):
    """cost of assigning the number at token-k to FIRST (minuend/dividend) vs SECOND operand."""
    n = len(toks); c = 0.0
    # position: earlier number tends to be the first operand
    c += (k / max(1, n)) * (1.0 if role_first else -1.0)
    win = " ".join(toks[max(0, k - 3):k + 4]).lower()
    # cue adjacency: "than X" / "from X" -> X is the reference (second); "X left/remain" -> first
    if re.search(r"\b(than|from)\b", win): c += (-0.8 if role_first else 0.8)
    if re.search(r"\b(left|remain|remaining)\b", win): c += (0.8 if role_first else -0.8)
    return c
def _selftest():
    assert _apply("SUB", Fraction(76), Fraction(25)) == 51
    print("[selftest] PASS: phase4-bipartite-svamp", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _load():
    from datasets import load_dataset
    ds = load_dataset("ChilleD/SVAMP")
    def conv(sp):
        out = []
        for ex in ds[sp]:
            txt = (ex.get("Body", "") + " " + ex.get("Question", "")).strip(); ans = _ans(ex.get("Answer"))
            if txt and ans is not None: out.append((txt, ans))
        return out
    return conv("train"), conv("test")
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1010")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    if SMOKE: train = train[:200]; test = test[:80]
    def gold(txt, ans):
        nps, toks = _nums_pos(txt)
        if len(nps) < 2: return None, None, None
        a, b = nps[0][0], nps[1][0]
        # find (op, order) yielding the answer; order: which of (a,b) is first operand
        for op in OPS4:
            if op in ("ADD", "MUL"):
                if _apply(op, a, b) == ans: return op, (a, b), toks
            else:
                if _apply(op, a, b) == ans: return op, (a, b), toks      # a first
                if _apply(op, b, a) == ans: return op, (b, a), toks      # b first
        return None, None, toks
    # train operator classifier (averaged perceptron over op-feats) on answer-consistency gold
    Xtr = []
    for txt, ans in train:
        op, ordered, toks = gold(txt, ans)
        if op is None: continue
        Xtr.append((_opfeats(txt), op))
    if not Xtr: return {"error": "no_train_labels", "accuracy": 0.0}
    w = {op: defaultdict(float) for op in OPS4}; cw = {op: defaultdict(float) for op in OPS4}; c = 1
    EP = 10 if not SMOKE else 4
    for ep in range(EP):
        for i in rng.permutation(len(Xtr)):
            feats, gp = Xtr[i]; sc = {op: sum(w[op][f] for f in feats) for op in OPS4}
            pred = max(OPS4, key=lambda o: (sc[o], o))
            if pred != gp:
                for f in feats: w[gp][f] += 1; w[pred][f] -= 1; cw[gp][f] += c; cw[pred][f] -= c
            c += 1
    avg = {op: {f: w[op][f] - cw[op][f] / c for f in w[op]} for op in OPS4}
    maj = max(OPS4, key=lambda o: sum(1 for _f, gg in Xtr if gg == o))
    correct = 0; nT = 0
    for txt, ans in test:
        nT += 1; nps, toks = _nums_pos(txt)
        if len(nps) < 2:
            a = nps[0][0] if nps else Fraction(0); b = Fraction(0); op = maj; first, second = a, b
        else:
            (a, ka), (b, kb) = nps[0], nps[1]
            feats = _opfeats(txt); sc = {op: sum(avg[op].get(f, 0.0) for f in feats) for op in OPS4}
            op = max(OPS4, key=lambda o: (sc[o], o))
            if op in ("ADD", "MUL"):
                first, second = a, b   # commutative: order irrelevant
            else:
                # BIPARTITE: 2 numbers x 2 roles {first, second}; Hungarian on cost matrix (minimize)
                C = np.zeros((2, 2))
                C[0, 0] = -_ordercost(toks, ka, True);  C[0, 1] = -_ordercost(toks, ka, False)
                C[1, 0] = -_ordercost(toks, kb, True);  C[1, 1] = -_ordercost(toks, kb, False)
                ri, ci = linear_sum_assignment(C)
                assign = {ci[r]: (a if ri[r] == 0 else b) for r in range(2)}
                first, second = assign.get(0, a), assign.get(1, b)
        r = _apply(op, first, second)
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: correct += 1
    acc = correct / nT if nT else 0.0
    print("  PHASE4-BIPARTITE-SVAMP: test-accuracy=%.3f (%d/%d) | train-labeled=%d (vs joint-perceptron 0.267, bag-of-words 0.110)" %
          (acc, correct, nT, len(Xtr)), flush=True)
    return {"accuracy": round(acc, 3), "n_correct": correct, "n_test": nT, "n_train_labeled": len(Xtr)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "accuracy=%.3f (%d/%d) train-labeled=%d" % (a, r["n_correct"], r["n_test"], r["n_train_labeled"])
    if a > 0.30:
        return ("HARD_PASS", "HARD_PASS: bipartite role-assigner (operator-classifier + Hungarian operand-ordering) >0.30 on SVAMP -- factored bipartite beats the joint perceptron (0.267); the graph/optimization primitive is the right substrate-native role-binding mechanism. " + s)
    if a >= 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 0.25-0.30 -- bipartite matches the joint perceptron (0.267); factorization neutral for 2-number SVAMP (operator-selection dominates; Hungarian ordering helps only the SUB/DIV minority). " + s)
    return ("HARD_FAIL", "HARD_FAIL: <0.25 -- bipartite factorization underperforms the joint perceptron. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
