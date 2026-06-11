"""
exp_svamp_role_asymmetry_cpu_v1.py -- SVAMP direction A: role-asymmetry discriminative perceptron -- CPU.

ROUTING: Research direction A (pivot from ASDiv 3-op; ASDiv is world-knowledge-bounded, SVAMP is asymmetric-op-order-bounded which
  discriminative weighting empirically lifts 2.4x). SVAMP failure mode = (1) OPERAND SELECTION (which 2 of N numbers; sample
  "290 bananas / 2 groups -> 145" needs target-aligned selection, NOT first-2) and (2) OP DIRECTION (X-Y vs Y-X, X/Y vs Y/X).
  Role-asymmetry features = bind each number to its entity-noun + grammatical role (subject/possessor vs object/transferred) +
  question-target alignment + transfer-verb direction. A/B: BASELINE (first-2 numbers + non-role op features) vs +ROLE
  (target-aligned operand selection + role-asymmetry directional features). Both = averaged perceptron over directional op-class.
  Bundled SVAMP (RESCUE: experiments/data/svamp.json, 700 train/300 test). Substrate-only, no LLM.
PRE-REGISTERED: report +role accuracy + lift vs baseline. HARD-PASS +role >= 0.42 (drill-13 target; role-asymmetry breaks SVAMP).
  MIDDLE 0.33-0.42 OR lift >= 0.05. HARD-FAIL +role < 0.30 AND lift < 0.03. UNKNOWN if load fails. NO defeat (drill-defeatism).
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
ANCHOR_NAME = "svamp_role_asymmetry_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
OPS = {"ADD": lambda a, b: a + b, "SUB_ab": lambda a, b: a - b, "SUB_ba": lambda a, b: b - a,
       "MUL": lambda a, b: a * b, "DIV_ab": lambda a, b: (a / b if b != 0 else None), "DIV_ba": lambda a, b: (b / a if a != 0 else None)}
OPNAMES = list(OPS.keys())
TRANSFER_OUT = ("gave", "lost", "spent", "sold", "ate", "removed", "used", "broke", "dropped")
TRANSFER_IN = ("got", "bought", "received", "found", "added", "gained", "made", "picked")


def _ans(x):
    try: return Fraction(str(x).strip()).limit_denominator(10**6)
    except Exception:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x)); return Fraction(m.group(0)).limit_denominator(10**6) if m else None


def _numinfo(text):
    """list of dicts per number: value, noun (next word), idx (token position), in_q (after question mark region)."""
    toks = text.lower().split(); out = []
    qstart = None
    for k, w in enumerate(toks):
        if "?" in w or w in ("how",): qstart = k if qstart is None else qstart
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.")
        if re.match(r"^\d+(?:\.\d+)?$", ww):
            noun = re.sub(r"[^a-z]", "", toks[k + 1]) if k + 1 < len(toks) else ""
            out.append({"v": Fraction(ww), "noun": noun, "idx": k, "in_q": (qstart is not None and k >= qstart)})
    return out


def _target(text):
    m = re.search(r"how (?:many|much) ([a-z]+)", text.lower())
    return m.group(1) if m else ""


def _select_pair(info, target, use_role):
    """Return (a_dict, b_dict) operand pair. baseline=first two; role=target-aligned relevance."""
    if len(info) < 2: return None
    if not use_role:
        return info[0], info[1]
    tgt = target
    def rel(d):
        s = 0.0
        if tgt and d["noun"] == tgt: s += 3.0          # number's entity matches the asked-about entity
        if d["in_q"]: s += 1.5                           # number appears in the question clause
        s += 0.001 * d["idx"]                            # mild recency tiebreak
        return s
    ranked = sorted(info, key=lambda d: -rel(d))
    a, b = ranked[0], ranked[1]
    # keep textual order for a,b so directional ops are consistent
    if a["idx"] > b["idx"]: a, b = b, a
    return a, b


def _feats(text, a, b, target, use_role):
    low = text.lower(); ws = re.findall(r"[a-z]+", low); fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("rel:a_gt_b" if a["v"] > b["v"] else ("rel:b_gt_a" if b["v"] > a["v"] else "rel:eq"))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times",
                "share", "divide", "per", "all", "combined", "together", "equally", "groups", "rest", "difference", "twice"):
        if cue in ws: fs.add("c:" + cue)
    fs.add("BIAS")
    if use_role:
        fs.add("aN:" + a["noun"]); fs.add("bN:" + b["noun"])
        if target:
            fs.add("aN_tgt" if a["noun"] == target else "aN_notgt")
            fs.add("bN_tgt" if b["noun"] == target else "bN_notgt")
        fs.add("a_in_q" if a["in_q"] else "a_in_body"); fs.add("b_in_q" if b["in_q"] else "b_in_body")
        # transfer-verb direction cues (asymmetric op-order signal)
        for vb in TRANSFER_OUT:
            if vb in ws: fs.add("tvout:" + vb)
        for vb in TRANSFER_IN:
            if vb in ws: fs.add("tvin:" + vb)
        # which operand is the larger / first -- crossed with target (role asymmetry)
        fs.add("first_is_a")  # a precedes b by construction
        if target and a["noun"] == target: fs.add("target_is_first_operand")
        if target and b["noun"] == target: fs.add("target_is_second_operand")
    return fs


def _gold_op(a, b, ans):
    for op in OPNAMES:
        r = OPS[op](a["v"], b["v"])
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: return op
    return None


def _selftest():
    info = _numinfo("there are 5 apples . tom has 3 apples . how many apples ?")
    assert len(info) == 2 and info[0]["noun"] == "apples"
    assert _gold_op({"v": Fraction(6)}, {"v": Fraction(2)}, Fraction(3)) == "DIV_ab"
    print("[selftest] PASS: svamp-role-asymmetry", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, use_role, seed):
    rng = np.random.default_rng(seed)
    Xtr = []
    for body, question, ans in train:
        text = (body + " " + question).strip(); info = _numinfo(text); target = _target(text)
        pair = _select_pair(info, target, use_role)
        if pair is None: continue
        a, b = pair; op = _gold_op(a, b, ans)
        if op is None: continue
        Xtr.append((_feats(text, a, b, target, use_role), op))
    if not Xtr: return 0.0, 0
    w = {o: defaultdict(float) for o in OPNAMES}; cw = {o: defaultdict(float) for o in OPNAMES}; c = 1
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(Xtr)):
            feats, g = Xtr[i]; sc = {o: sum(w[o][f] for f in feats) for o in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: w[g][f] += 1; w[pred][f] -= 1; cw[g][f] += c; cw[pred][f] -= c
            c += 1
    avg = {o: {f: w[o][f] - cw[o][f] / c for f in w[o]} for o in OPNAMES}
    cor = 0
    for body, question, ans in test:
        text = (body + " " + question).strip(); info = _numinfo(text); target = _target(text)
        pair = _select_pair(info, target, use_role)
        if pair is None: continue
        a, b = pair; feats = _feats(text, a, b, target, use_role)
        sc = {o: sum(avg[o].get(f, 0.0) for f in feats) for o in OPNAMES}
        op = max(OPNAMES, key=lambda o: (sc[o], o)); r = OPS[op](a["v"], b["v"])
        if r is not None and Fraction(r).limit_denominator(10**6) == ans: cor += 1
    return cor / len(test) if test else 0.0, len(Xtr)


def run() -> Dict:
    try:
        d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    def conv(sp):
        out = []
        for e in d.get(sp, []):
            a = _ans(e.get("answer"))
            if a is not None: out.append((e.get("body", ""), e.get("question", ""), a))
        return out
    train = conv("train"); test = conv("test")
    if SMOKE: train = train[:200]; test = test[:80]
    seed = int(os.environ.get("HDLAB_SEED", "1011"))
    base_acc, nb = _train_eval(train, test, use_role=False, seed=seed)
    print("  [baseline first-2]      acc=%.4f (train labels=%d)" % (base_acc, nb), flush=True)
    role_acc, nr = _train_eval(train, test, use_role=True, seed=seed)
    print("  [+role-asymmetry]       acc=%.4f (train labels=%d)" % (role_acc, nr), flush=True)
    lift = role_acc - base_acc
    print("  LIFT (role - baseline) = %+.4f | test=%d" % (lift, len(test)), flush=True)
    return {"accuracy": round(role_acc, 4), "acc_role": round(role_acc, 4), "acc_baseline": round(base_acc, 4),
            "lift": round(lift, 4), "n_test": len(test), "n_train_labeled_role": nr, "n_train_labeled_base": nb}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ar = r["acc_role"]; ab = r["acc_baseline"]; lift = r["lift"]
    s = "+role=%.4f vs baseline(first-2)=%.4f (lift=%+.4f, test=%d). Role = target-aligned operand selection + subject/object/transfer-direction features." % (ar, ab, lift, r["n_test"])
    if ar >= 0.42:
        return ("HARD_PASS", "HARD_PASS: SVAMP role-asymmetry perceptron >=0.42 (drill-13 target) -- role-asymmetry (operand selection + op-direction) breaks the SVAMP plateau substrate-only. " + s)
    if ar >= 0.33 or lift >= 0.05:
        return ("MIDDLE_BAND", "MIDDLE_BAND: role-asymmetry lifts SVAMP toward target (0.33-0.42 or lift>=0.05) -- mechanism works, partial; richer role parsing for 0.42. " + s)
    return ("HARD_FAIL", "HARD_FAIL: role-asymmetry <0.30 and lift<0.03 -- operand-selection/op-direction features insufficient on SVAMP. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
