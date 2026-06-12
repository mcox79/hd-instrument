"""
exp_path1_srl_mwp_cpu_v1.py -- Path 1: SRL over substrate-classical NL for MWP operand-selection (targeted MWP-WK test) -- CPU.

ROUTING: Research GREEN-LIT (research_to_exp_dev_SRL_TRAINING_SET_30_MWP_WK_SCHEMA_11_SHIPPED). Tests the 8th methodology-rule
  candidate (targeted-not-generic-ingestion-is-the-lever) on the 5-deep MWP operand-selection plateau: does a TARGETED MWP-WK + SRL
  training set lift operand-selection where generic math primitives did not? MECHANISM (the genuinely-different LINGUISTIC angle, now
  with TRAINED labels -- Path-1-lite heuristic failed at 0.34): (1) schema-classifier (count-NB over text cues -> MWP schema -> op),
  (2) role-labeler (averaged-perceptron over per-number context -> arg_role), both trained on the 30 hand-authored SRL examples; then
  for each ASDiv-1op problem: classify schema -> op + role-template; label each number's role; select operands + ORDER via the schema's
  role template (e.g. CHANGE_SUB: initial - given; SHARE: total / recipients -- the role labeler resolves order, where E4 used a
  magnitude heuristic). Substrate-classical Tier-A SRL precedent. Substrate-only, no LLM.
PRE-REGISTERED (Research): HARD-PASS ASDiv-1op acc >= 0.45 (+0.06 over 0.39 = targeted-ingestion-is-the-lever VALIDATED). MIDDLE
  0.43-0.45 (+0.04-0.06 partial). HARD-FAIL < 0.43 (6th angle confirms 5-deep; full Path-1 stays deferred to Phase-6). UNKNOWN if load fails.
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
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "path1_srl_mwp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_WORDNUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20, "dozen": 12}
SCHEMA_OP = {"MWP/SCHEMA_COMBINE": "+", "MWP/SCHEMA_CHANGE_ADD": "+", "MWP/SCHEMA_CHANGE_SUB": "-",
             "MWP/SCHEMA_EQUAL_GROUPS": "*", "MWP/SCHEMA_COMPARE": "-", "MWP/SCHEMA_SHARE": "/"}
# operand-order roles per schema: (minuend/dividend role-substring, subtrahend/divisor role-substring)
ORDER_ROLES = {"MWP/SCHEMA_CHANGE_SUB": ("initial", "given"), "MWP/SCHEMA_SHARE": ("total", "recipient")}
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: (a / b if b != 0 else None)}


def _toks(t): return re.findall(r"[a-z]+", t.lower())


def _num_positions(text):
    """list of (value, token_index) for numbers in text (digit or word)."""
    toks = text.split(); out = []
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.!:;")
        if re.match(r"^\d+(?:\.\d+)?$", ww): out.append((Fraction(ww), k))
        elif ww.lower() in _WORDNUM: out.append((Fraction(_WORDNUM[ww.lower()]), k))
    return out, toks


def _schema_feats(text):
    low = " " + text.lower() + " "
    fs = []
    for c in ["each", "per", "every", "total", "altogether", "in all", "combined", "both", "gave", "lost", "left", "spent",
              "got", "bought", "more", "received", "share", "divide", "split", "equally", "times", "more than", "fewer than",
              "less than", "difference", "how many more", "rows of", "groups", "among"]:
        if c in low: fs.append("c:" + c.replace(" ", "_"))
    fs.append("BIAS")
    return fs


def _role_feats(toks, k):
    """per-number context features for role labeling."""
    pv = toks[k - 1].lower().rstrip(".,") if k > 0 else "<S>"
    nv = toks[k + 1].lower().rstrip(".,") if k + 1 < len(toks) else "<E>"
    nn = toks[k + 2].lower().rstrip(".,") if k + 2 < len(toks) else "<E>"
    fs = ["pv:" + pv, "nv:" + nv, "nn:" + nn, "pos:%d" % (0 if k < 4 else (1 if k < 9 else 2))]
    ctx = " ".join(t.lower() for t in toks[max(0, k - 3):k + 4])
    for c in ["each", "per", "more", "left", "gave", "got", "total", "among", "share", "groups", "every", "rows"]:
        if c in ctx: fs.append("x:" + c)
    fs.append("BIAS")
    return fs


def _train_nb(examples):
    """count-NB text-cue -> schema."""
    cls = Counter(); fcls = defaultdict(Counter); vocab = set()
    for text, sch, _ in examples:
        cls[sch] += 1
        for f in _schema_feats(text): fcls[sch][f] += 1; vocab.add(f)
    V = len(vocab); tot = sum(cls.values())

    def pred(text):
        best = None; bs = -1e18
        for sch in cls:
            import math
            s = math.log((cls[sch] + 0.5) / (tot + 0.5 * len(cls)))
            for f in _schema_feats(text):
                s += math.log((fcls[sch][f] + 0.3) / (cls[sch] + 0.3 * V))
            if s > bs: bs = s; best = sch
        return best
    return pred


def _train_role(role_ex, seed=7):
    """averaged-perceptron per-number-feats -> arg_role."""
    roles = sorted({r for _f, r in role_ex}); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1
    for _ in range(20 if not SMOKE else 5):
        for i in rng.permutation(len(role_ex)):
            feats, gold = role_ex[i]
            scores = {r: sum(w[(f, r)] for f in feats) for r in roles}
            pred = max(scores, key=scores.get)
            if pred != gold:
                for f in feats: w[(f, gold)] += 1; cw[(f, gold)] += c; w[(f, pred)] -= 1; cw[(f, pred)] -= c
            c += 1
    avg = {k: w[k] - cw[k] / c for k in w}

    def pred(feats):
        scores = {r: sum(avg.get((f, r), 0.0) for f in feats) for r in roles}
        return max(scores, key=scores.get)
    return pred, roles


def _selftest():
    assert "c:each" in _schema_feats("each box has five apples")
    assert SCHEMA_OP["MWP/SCHEMA_SHARE"] == "/"
    print("[selftest] PASS: path1-srl-mwp", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    try:
        srl = [json.loads(l) for l in open(REPO / "data" / "substrate_index" / "srl_corpus_mwp_minimal_batch_01.jsonl", encoding="utf-8") if l.strip()]
    except Exception as e:
        print("[srl] load fail %s" % str(e)[:80], flush=True); return {"error": "srl_load_failed"}
    sch_ex = [(r["text"], r["schema"], r.get("gold_op")) for r in srl]
    role_ex = []
    for r in srl:
        _np, toks = _num_positions(r["text"])
        # align labeled numbers to positions by value order
        labeled = r["numbers"]
        npos = [(v, k) for v, k in _np]
        for idx, (v, k) in enumerate(npos):
            if idx < len(labeled): role_ex.append((_role_feats(toks, k), labeled[idx]["arg_role"]))
    sch_pred = _train_nb(sch_ex); role_pred, roles = _train_role(role_ex)
    print("[train] schemas=%d role-examples=%d role-types=%d" % (len(sch_ex), len(role_ex), len(roles)), flush=True)

    try:
        d = json.load(open(REPO / "experiments" / "data" / "asdiv_validation.json", encoding="utf-8"))
    except Exception as e:
        print("[asdiv] fail %s" % str(e)[:80], flush=True); return {"error": "asdiv_load_failed"}
    items = []
    for e in d:
        f = e.get("formula", "")
        if "=" not in f or sum(f.split("=")[0].count(o) for o in "+-*/") != 1: continue
        m = re.search(r"-?\d+\.?\d*", str(e.get("answer", "")))
        if not m: continue
        items.append(((e.get("body", "") + " " + e.get("question", "")).strip(), Fraction(m.group()).limit_denominator(10**6)))
    if SMOKE: items = items[:200]

    cor = tot = 0
    for text, ans in items:
        npos, toks = _num_positions(text)
        if len(npos) < 2: continue
        tot += 1
        sch = sch_pred(text); op = SCHEMA_OP.get(sch, "+")
        # label roles for each number
        labels = [role_pred(_role_feats(toks, k)) for _v, k in npos]
        vals = [v for v, _k in npos]
        # operand selection via schema role-template
        if sch in ORDER_ROLES:
            hi_sub, lo_sub = ORDER_ROLES[sch]
            hi = next((vals[i] for i, lb in enumerate(labels) if hi_sub in lb), None)
            lo = next((vals[i] for i, lb in enumerate(labels) if lo_sub in lb), None)
            if hi is None or lo is None:  # fallback: magnitude order
                a, b = vals[0], vals[1]; hi, lo = (a, b) if a >= b else (b, a)
            r = OPS[op](hi, lo)
        else:  # COMBINE/CHANGE_ADD/EQUAL_GROUPS/COMPARE: order-free or magnitude
            a, b = vals[0], vals[1]
            if op == "-":  # COMPARE: larger - smaller
                hi, lo = (a, b) if a >= b else (b, a); r = OPS[op](hi, lo)
            else: r = OPS[op](a, b)
        cor += int(r is not None and Fraction(r).limit_denominator(10**6) == ans)
    acc = cor / tot if tot else 0.0
    print("  Path-1 SRL (trained schema + role labeler): ASDiv-1op acc=%.4f (n=%d) vs discriminative ~0.39, E4 0.34, Path-1-lite 0.34" % (acc, tot), flush=True)
    print("  targeted-MWP-WK lift over 0.39 = %+.4f" % (acc - 0.39), flush=True)
    return {"f1": round(acc, 4), "accuracy": round(acc, 4), "lift_over_baseline": round(acc - 0.39, 4), "n": tot, "n_srl_train": len(sch_ex)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["accuracy"]; s = "acc=%.4f (n=%d, SRL-train=%d) vs 0.39 discriminative / 0.34 E4+Path-1-lite" % (a, r["n"], r["n_srl_train"])
    if a >= 0.45:
        return ("HARD_PASS", "HARD_PASS: targeted MWP-WK + SRL lifts operand-selection >=+0.06 -- targeted-ingestion-is-the-lever VALIDATED (8th rule); trained SRL roles break what generic primitives + 5 untrained mechanisms could not. " + s)
    if a >= 0.43:
        return ("MIDDLE_BAND", "MIDDLE_BAND: targeted MWP-WK + SRL +0.04-0.06 -- partial; targeted helps but corpus richness still bottleneck. " + s)
    return ("HARD_FAIL", "HARD_FAIL: targeted MWP-WK + SRL <+0.04 over 0.39 -- 6th INDEPENDENT angle; trained linguistic SRL also plateaus -> corpus-deficiency needs FULL Phase-6 (not minimal targeted); 8th rule requires more targeted data per rule. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
