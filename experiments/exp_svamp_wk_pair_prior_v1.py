"""
exp_svamp_wk_pair_prior_v1.py -- SVAMP-A WK-pair prior weight sweep -- CPU.

ROUTING: Research note `research_svamp_mechanism_redesign_2x_drill_2026-06-22.md`, Candidate A.
  Diagnosis: the prior cell (exp_svamp_math_wk_lex_cpu_v1) HARD_FAILed at acc_wk=0.3633 because the trained selector
  learned to ANTI-PREFER WK-constant pairs (training labels are in-text-pair-dominated; WK pairs are never gold in the
  580-item train split). FIX: at INFERENCE time, add a fixed positive bias to the selector score for any candidate pair
  containing a WK constant. Sweep WK_PRIOR_WEIGHT in {0.0, 0.5, 1.0, 2.0, 3.0}; seeds 1011/1012/1013; n_test=300.
PRE-REGISTERED (Research, deflated P(HARD_PASS)=0.42):
  - HARD_PASS: max(acc_wk over sweep) >= 0.40 AND in-text-only acc does NOT drop > 0.02 from base.
  - MIDDLE_BAND: max(acc_wk) in [0.38, 0.40) (mechanism real, bar not cleared).
  - HARD_FAIL: max(acc_wk) < 0.38 across all 5 weights -> route Candidate D (joint pair+op training).
  - DISCRIMINATING CONTROL: weight=0.0 arm at seed=1011 MUST reproduce acc_wk=0.3633 +/- 0.002.
ASCII-only. write_metrics. PROT-018 _v1. corpus_provenance_real=True (SVAMP real test set).
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

ANCHOR_NAME = "svamp_wk_pair_prior_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"

# CONFIG_VERSION captures the sweep grid + seeds + n_test
WK_PRIOR_WEIGHTS = [0.0, 0.5, 1.0, 2.0, 3.0]
SEEDS = [1011, 1012, 1013]
N_TEST_FULL = 300
CONFIG_VERSION = "wk_pair_prior_v1__weights=%s__seeds=%s__n_test=%d" % (
    "-".join("%g" % w for w in WK_PRIOR_WEIGHTS), "-".join(str(s) for s in SEEDS), N_TEST_FULL)
CORPUS_PROVENANCE_REAL = True   # SVAMP real test set, no synthetic

WK_TRIG: Dict[str, set] = {}


def _stem(w):
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
                trig = key.split("_per_")[-1].split("_")[-1]
            else:
                trig = key
            for t in (trig, _stem(trig)):
                if t and t.isalpha(): WK_TRIG.setdefault(t, set()).add(v)
    WK_TRIG.setdefault("percent", set()).add(Fraction(100)); WK_TRIG.setdefault("dollar", set()).add(Fraction(100))
    return len(WK_TRIG) > 0


def _wk_extra(text):
    toks = text.lower().split(); extra = []; seen = set()
    isnum = [bool(re.match(r"^\d", t.replace("$", "").replace(",", ""))) for t in toks]
    for k, w in enumerate(toks):
        st = _stem(re.sub(r"[^a-z]", "", w))
        if st not in WK_TRIG: continue
        near_num = any(isnum[j] for j in range(max(0, k - 2), min(len(toks), k + 3)))
        if not near_num: continue
        for v in WK_TRIG[st]:
            if v in seen: continue
            seen.add(v); extra.append({"v": v, "noun": st, "idx": 1000 + len(extra), "in_q": False, "wk": True})
    if "%" in text and Fraction(100) not in seen:
        extra.append({"v": Fraction(100), "noun": "percent", "idx": 1500, "in_q": False, "wk": True})
    return extra


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
    toks = text.lower().split(); out = []; qstart = None
    for k, w in enumerate(toks):
        if w == "how" and qstart is None: qstart = k
    for k, w in enumerate(toks):
        ww = w.replace("$", "").replace(",", "").rstrip("?.")
        if re.match(r"^\d+(?:\.\d+)?$", ww):
            noun = re.sub(r"[^a-z]", "", toks[k + 1]) if k + 1 < len(toks) else ""
            out.append({"v": Fraction(ww), "noun": noun, "idx": k, "in_q": (qstart is not None and k >= qstart)})
    return out


def _target(text):
    m = re.search(r"how (?:many|much) ([a-z]+)", text.lower()); return _stem(m.group(1)) if m else ""


def _pair_feats(a, b, target, ws):
    fs = ["P_BIAS"]
    am = (target and _stem(a["noun"]) == target); bm = (target and _stem(b["noun"]) == target)
    fs.append("Ptgt_both" if am and bm else ("Ptgt_one" if am or bm else "Ptgt_none"))
    fs.append("Pinq_both" if a["in_q"] and b["in_q"] else ("Pinq_one" if a["in_q"] or b["in_q"] else "Pinq_none"))
    fs.append("Psamenoun" if a["noun"] == b["noun"] and a["noun"] else "Pdiffnoun")
    fs.append("Padj" if abs(a["idx"] - b["idx"]) <= 3 else "Pfar")
    fs.append("Pmag_a_gt_b" if a["v"] > b["v"] else ("Pmag_b_gt_a" if b["v"] > a["v"] else "Pmag_eq"))
    if (am and not bm) or (bm and not am): fs.append("Pcross_target")
    fs.append("PnA:" + a["noun"]); fs.append("PnB:" + b["noun"])
    return fs


def _op_feats(text, a, b, target, ws):
    fs = set("u:" + w for w in ws)
    for i in range(len(ws) - 1): fs.add("b:%s_%s" % (ws[i], ws[i + 1]))
    fs.add("rel:a_gt_b" if a["v"] > b["v"] else ("rel:b_gt_a" if b["v"] > a["v"] else "rel:eq"))
    for cue in ("left", "remain", "more", "fewer", "less", "than", "each", "every", "total", "altogether", "times",
                "share", "divide", "per", "all", "combined", "together", "equally", "groups", "rest", "difference", "twice"):
        if cue in ws: fs.add("c:" + cue)
    fs.add("aN_tgt" if target and _stem(a["noun"]) == target else "aN_x"); fs.add("bN_tgt" if target and _stem(b["noun"]) == target else "bN_x")
    fs.add("a_in_q" if a["in_q"] else "a_body"); fs.add("b_in_q" if b["in_q"] else "b_body")
    for vb in TRANSFER_OUT:
        if vb in ws: fs.add("tvout:" + vb)
    for vb in TRANSFER_IN:
        if vb in ws: fs.add("tvin:" + vb)
    fs.add("BIAS"); return fs


def _gold(info, ans, target):
    cands = []
    n = len(info)
    for i in range(n):
        for j in range(n):
            if i == j: continue
            a, b = info[i], info[j]
            for op in OPNAMES:
                r = OPS[op](a["v"], b["v"])
                if r is not None and Fraction(r).limit_denominator(10**6) == ans:
                    tg = (target and (_stem(a["noun"]) == target or _stem(b["noun"]) == target))
                    cands.append((1 if tg else 0, i, j, op))
    if not cands: return None
    cands.sort(key=lambda x: -x[0])
    _, i, j, op = cands[0]
    return (i, j, op)


def _numpool(text, augment):
    info = _numinfo(text)
    if augment:
        extra = _wk_extra(text)
        info = info + extra
    if len(info) > 10: info = info[:10]
    return info


def _intext_solvable(text, ans):
    """True iff the gold answer is reproducible from in-text numbers alone (no WK augmentation needed)."""
    info_base = _numinfo(text)
    if len(info_base) < 2: return False
    target = _target(text)
    return _gold(info_base, ans, target) is not None


def _pipeline(train, test, wk_prior_weight, seed, intext_flags):
    """One pipeline run for a given (wk_prior_weight, seed). Returns instrumented metrics dict."""
    rng = np.random.default_rng(seed)
    # Build training labels using WK-augmented pool (consistent with base cell training).
    TR = []
    for text, ans in train:
        info = _numpool(text, augment=True)
        if len(info) < 2: continue
        target = _target(text); g = _gold(info, ans, target)
        if g is None: continue
        TR.append((text, info, target, g))
    if not TR:
        return {"acc_wk": 0.0, "acc_intext_only": 0.0, "acc_wk_required": 0.0, "selector_pair_acc": 0.0,
                "n_wk_candidates_entering": 0, "n_wk_candidates_selected": 0, "n_intext_only": 0, "n_wk_required": 0,
                "n_test_effective": 0, "n_train_labels": 0}
    sw = defaultdict(float); scw = defaultdict(float); c = 1
    def cands_of(info): return [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j]
    for ep in range(10 if not SMOKE else 4):
        for ti in rng.permutation(len(TR)):
            text, info, target, (gi, gj, gop) = TR[ti]; ws = re.findall(r"[a-z]+", text.lower())
            def sscore(i, j): return sum(sw[f] for f in _pair_feats(info[i], info[j], target, ws))
            pi, pj = max(cands_of(info), key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
            if (pi, pj) != (gi, gj):
                for f in _pair_feats(info[gi], info[gj], target, ws): sw[f] += 1; scw[f] += c
                for f in _pair_feats(info[pi], info[pj], target, ws): sw[f] -= 1; scw[f] -= c
            c += 1
    savg = {f: sw[f] - scw[f] / c for f in sw}
    # Op-classifier training (same as base cell).
    ow = {o: defaultdict(float) for o in OPNAMES}; ocw = {o: defaultdict(float) for o in OPNAMES}; c2 = 1
    OPTR = [(_op_feats(t, info[gi], info[gj], tg, re.findall(r"[a-z]+", t.lower())), gop) for (t, info, tg, (gi, gj, gop)) in TR]
    for ep in range(12 if not SMOKE else 4):
        for i in rng.permutation(len(OPTR)):
            feats, g = OPTR[i]; sc = {o: sum(ow[o][f] for f in feats) for o in OPNAMES}
            pred = max(OPNAMES, key=lambda o: (sc[o], o))
            if pred != g:
                for f in feats: ow[g][f] += 1; ow[pred][f] -= 1; ocw[g][f] += c2; ocw[pred][f] -= c2
            c2 += 1
    oavg = {o: {f: ow[o][f] - ocw[o][f] / c2 for f in ow[o]} for o in OPNAMES}
    # Inference with WK-pair prior bias (the ONE-LINE CHANGE).
    cor = 0; sel_cor = 0; sel_n = 0
    cor_intext = 0; n_intext = 0; cor_wk_req = 0; n_wk_req = 0
    n_wk_cand_in = 0; n_wk_cand_sel = 0
    for idx, (text, ans) in enumerate(test):
        info = _numpool(text, augment=True)
        if len(info) < 2: continue
        n_wk_cand_in += sum(1 for x in info if x.get("wk"))
        target = _target(text); ws = re.findall(r"[a-z]+", text.lower())
        def sscore(i, j):
            raw = sum(savg.get(f, 0.0) for f in _pair_feats(info[i], info[j], target, ws))
            if info[i].get("wk") or info[j].get("wk"):
                raw += wk_prior_weight   # ONE-LINE FIXED-PRIOR INJECTION (Candidate A)
            return raw
        pi, pj = max(cands_of(info), key=lambda ij: (sscore(*ij), -ij[0], -ij[1]))
        a, b = info[pi], info[pj]
        if a.get("wk") or b.get("wk"): n_wk_cand_sel += 1
        feats = _op_feats(text, a, b, target, ws); sc = {o: sum(oavg[o].get(f, 0.0) for f in feats) for o in OPNAMES}
        op = max(OPNAMES, key=lambda o: (sc[o], o)); r = OPS[op](a["v"], b["v"])
        correct = (r is not None and Fraction(r).limit_denominator(10**6) == ans)
        if correct: cor += 1
        # split overall acc into in-text-solvable vs WK-required (per the prereg side-check)
        if intext_flags[idx]:
            n_intext += 1
            if correct: cor_intext += 1
        else:
            n_wk_req += 1
            if correct: cor_wk_req += 1
        g = _gold(info, ans, target)
        if g is not None:
            sel_n += 1
            if (pi, pj) == (g[0], g[1]) or (pi, pj) == (g[1], g[0]): sel_cor += 1
    n_eff = len(test)
    return {
        "acc_wk": round(cor / n_eff, 4) if n_eff else 0.0,
        "acc_intext_only": round(cor_intext / n_intext, 4) if n_intext else 0.0,
        "acc_wk_required": round(cor_wk_req / n_wk_req, 4) if n_wk_req else 0.0,
        "selector_pair_acc": round(sel_cor / sel_n, 4) if sel_n else 0.0,
        "n_wk_candidates_entering": int(n_wk_cand_in),
        "n_wk_candidates_selected": int(n_wk_cand_sel),
        "n_intext_only": int(n_intext),
        "n_wk_required": int(n_wk_req),
        "n_test_effective": int(n_eff),
        "n_train_labels": int(len(TR)),
    }


def _selftest():
    info = _numinfo("there are 5 apples and 3 apples . how many apples ?")
    assert len(info) == 2 and _stem("apples") == "apple"
    # AST-checkable constants
    assert WK_PRIOR_WEIGHTS == [0.0, 0.5, 1.0, 2.0, 3.0]
    assert SEEDS == [1011, 1012, 1013]
    assert N_TEST_FULL == 300
    assert CORPUS_PROVENANCE_REAL is True
    print("[selftest] PASS: svamp-wk-pair-prior", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    if not load_wk():
        print("[wk] atoms file missing", flush=True); return {"error": "wk_atoms_missing", "accuracy": 0.0}
    print("  [wk] %d trigger words loaded" % len(WK_TRIG), flush=True)
    try:
        d = json.load(open(REPO / "experiments" / "data" / "svamp.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "accuracy": 0.0}
    def conv(sp):
        out = []
        for e in d.get(sp, []):
            a = _ans(e.get("answer"))
            if a is not None: out.append(((e.get("body", "") + " " + e.get("question", "")).strip(), a))
        return out
    train = conv("train"); test = conv("test")
    if SMOKE: train = train[:200]; test = test[:80]
    # Pre-compute in-text-solvable flag PER TEST ITEM (seed-independent; depends only on text+ans).
    intext_flags = [_intext_solvable(t, a) for (t, a) in test]
    n_test = len(test); n_intext = sum(intext_flags); n_wkreq = n_test - n_intext
    print("  [splits] n_test=%d  in_text_solvable=%d (%.1f%%)  wk_required=%d (%.1f%%)" %
          (n_test, n_intext, 100.0 * n_intext / n_test, n_wkreq, 100.0 * n_wkreq / n_test), flush=True)
    per_unit = []
    for w in WK_PRIOR_WEIGHTS:
        for s in SEEDS:
            t0u = time.time()
            m = _pipeline(train, test, wk_prior_weight=w, seed=s, intext_flags=intext_flags)
            m["wk_prior_weight"] = float(w); m["seed"] = int(s); m["wall_s"] = round(time.time() - t0u, 2)
            per_unit.append(m)
            print("  [arm] w=%.2f seed=%d acc_wk=%.4f acc_intext=%.4f acc_wkreq=%.4f sel=%.4f wk_in=%d wk_sel=%d wall=%.1fs" %
                  (w, s, m["acc_wk"], m["acc_intext_only"], m["acc_wk_required"], m["selector_pair_acc"],
                   m["n_wk_candidates_entering"], m["n_wk_candidates_selected"], m["wall_s"]), flush=True)
    # Aggregate per-weight: mean over seeds
    by_w = {}
    for m in per_unit:
        by_w.setdefault(m["wk_prior_weight"], []).append(m)
    weight_summary = []
    for w in WK_PRIOR_WEIGHTS:
        arms = by_w[w]
        mean_acc = float(np.mean([a["acc_wk"] for a in arms]))
        mean_intext = float(np.mean([a["acc_intext_only"] for a in arms]))
        mean_wkreq = float(np.mean([a["acc_wk_required"] for a in arms]))
        mean_sel = float(np.mean([a["selector_pair_acc"] for a in arms]))
        weight_summary.append({"wk_prior_weight": w, "mean_acc_wk": round(mean_acc, 4),
                                "mean_acc_intext_only": round(mean_intext, 4),
                                "mean_acc_wk_required": round(mean_wkreq, 4),
                                "mean_selector_pair_acc": round(mean_sel, 4),
                                "n_seeds": len(arms)})
    max_acc = max(ws["mean_acc_wk"] for ws in weight_summary)
    best_w = max(weight_summary, key=lambda x: x["mean_acc_wk"])
    base_intext_acc = next(ws["mean_acc_intext_only"] for ws in weight_summary if ws["wk_prior_weight"] == 0.0)
    best_intext_drop = base_intext_acc - best_w["mean_acc_intext_only"]
    # DISCRIMINATING CONTROL: weight=0 seed=1011 must reproduce 0.3633 +/- 0.002
    control_arm = next((m for m in per_unit if m["wk_prior_weight"] == 0.0 and m["seed"] == 1011), None)
    control_ok = (control_arm is not None and abs(control_arm["acc_wk"] - 0.3633) <= 0.002)
    print("\n  [summary] max_mean_acc_wk=%.4f at w=%.2f (best mean_intext=%.4f, intext_drop_vs_w=0=%.4f)" %
          (max_acc, best_w["wk_prior_weight"], best_w["mean_acc_intext_only"], best_intext_drop), flush=True)
    print("  [control] w=0 seed=1011 acc_wk=%s  expected=0.3633 +/- 0.002  match=%s" %
          (control_arm["acc_wk"] if control_arm else "N/A", control_ok), flush=True)
    return {
        "accuracy": round(max_acc, 4),
        "max_mean_acc_wk": round(max_acc, 4),
        "best_wk_prior_weight": best_w["wk_prior_weight"],
        "best_intext_drop_vs_w0": round(best_intext_drop, 4),
        "control_w0_seed1011_acc_wk": control_arm["acc_wk"] if control_arm else None,
        "control_reproduce_ok": bool(control_ok),
        "n_test": n_test, "n_intext_only": n_intext, "n_wk_required": n_wkreq,
        "config_version": CONFIG_VERSION, "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "per_unit": per_unit, "weight_summary": weight_summary,
    }


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    max_acc = r["max_mean_acc_wk"]; best_w = r["best_wk_prior_weight"]
    intext_drop = r["best_intext_drop_vs_w0"]
    ctrl_ok = r["control_reproduce_ok"]; ctrl_val = r["control_w0_seed1011_acc_wk"]
    base = ("max_mean_acc_wk=%.4f at w=%.2f, in-text-drop=%+.4f, control(w=0,seed=1011)=%s (expect 0.3633+/-0.002, match=%s), n_test=%d (intext=%d, wk_req=%d)."
            % (max_acc, best_w, intext_drop, ctrl_val, ctrl_ok, r["n_test"], r["n_intext_only"], r["n_wk_required"]))
    if not ctrl_ok:
        return ("UNKNOWN", "UNKNOWN: discriminating control FAILED -- w=0 seed=1011 did not reproduce base 0.3633+/-0.002 (got %s). Sweep is not faithfully isolating the prior. " % ctrl_val + base)
    if max_acc >= 0.40 and intext_drop <= 0.02:
        return ("HARD_PASS", "HARD_PASS: WK-pair fixed prior closes the gap -- max mean acc >= 0.40 with in-text-only acc not dropping > 0.02. The selector's anti-WK bias was the bottleneck; a one-line scoring offset rescues it. " + base)
    if max_acc >= 0.40 and intext_drop > 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: hit acc bar but in-text-only acc dropped > 0.02 (cost-of-bias side-check tripped). Prior is over-weighting non-WK problems. " + base)
    if max_acc >= 0.38:
        return ("MIDDLE_BAND", "MIDDLE_BAND: max mean acc in [0.38, 0.40) -- mechanism real, bar not cleared. Either richer trigger coverage or Candidate B (synthetic WK training labels) next. " + base)
    return ("HARD_FAIL", "HARD_FAIL: max mean acc < 0.38 across ALL 5 weights -- selector's in-text bias dominates regardless of a scalar prior. Route Candidate D (joint pair+op training) per Research 2x drill. " + base)


print("[config] anchor=%s mode=%s version=%s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
    "run_mode": RUN_MODE, "config_version": CONFIG_VERSION, "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
    "n_seeds": len(SEEDS), "per_seed": r.get("per_unit", []),
    "weight_summary": r.get("weight_summary", []),
    "max_mean_acc_wk": r.get("max_mean_acc_wk"), "best_wk_prior_weight": r.get("best_wk_prior_weight"),
    "control_w0_seed1011_acc_wk": r.get("control_w0_seed1011_acc_wk"),
    "control_reproduce_ok": r.get("control_reproduce_ok"),
    "elapsed_s": time.time() - t0,
}
write_metrics(out_dir, metrics, r.get("per_unit", []))
print("[metrics] written", flush=True)
