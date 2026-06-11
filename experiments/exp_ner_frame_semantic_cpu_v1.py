"""
exp_ner_frame_semantic_cpu_v1.py -- Priority 2: frame-semantic entity-type construction features -- CPU.

ROUTING: Research consolidated Priority 2 (Drill 4 top, P=0.50). NER in-corpus features SATURATE (gazetteer +0.007, clusters/POS
  small) because LEXICAL features memorize seen surfaces. Frame-semantic hypothesis (anti-shrinkage): predict entity type by the
  token's SLOT in an activated CONSTRUCTION FRAME -- features that ABSTRACT over the specific trigger word and GENERALIZE to unseen
  entities. Brain analogue: anterior-temporal-lobe person-selective + left-vlPFC category-membership. Construction frames:
  TITLE+X -> X=PERSON ; X+ORGSUFFIX -> X=ORG ; PREP+Cap -> GPE/LOC ; X+REPORTING-VERB -> X=PERSON/ORG ; DATE/MONEY/PERCENT cues.
  These are SINGLE abstract features firing across all triggers (vs per-word lexical features). Add to the structured-perceptron NER
  emission; A/B baseline vs +frame. OntoNotes 18-type. Substrate-self-referential (concept-partition frames), no LLM.
PRE-REGISTERED (Research gate): HARD-PASS F1 lift >= +0.08. MIDDLE +0.02 to +0.08. HARD-FAIL <= +0.02 (frame abstraction saturates
  like lexical features). UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_frame_semantic_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_BASELINE = 0.5817
# ---- construction-frame trigger classes (abstract over specific words) ----
TITLE = {"mr", "mrs", "ms", "dr", "prof", "professor", "president", "senator", "mayor", "governor", "king", "queen",
         "sir", "lord", "lady", "rev", "gen", "capt", "sgt", "officer", "chief", "secretary", "minister", "ceo", "chairman"}
ORGSUF = {"inc", "corp", "ltd", "co", "llc", "company", "corporation", "group", "holdings", "industries", "foundation",
          "institute", "university", "college", "bank", "agency", "association", "committee", "council", "department", "ministry"}
PREP = {"in", "at", "from", "to", "near", "across", "throughout", "around", "outside", "inside", "via"}
REPVERB = {"said", "told", "announced", "reported", "stated", "added", "noted", "claimed", "argued", "wrote", "told", "asked"}
MONTH = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
         "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
MONEYW = {"dollars", "dollar", "cents", "cent", "usd", "eur", "euros", "pounds", "yen", "pesos"}
UNITW = {"meters", "meter", "kilometers", "miles", "feet", "inches", "pounds", "kilograms", "tons", "liters", "gallons",
         "percent", "degrees", "hours", "minutes", "years", "days", "weeks", "months"}


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _frame_feats(words, i, tag):
    """abstract construction-frame features for token i (generalize across trigger words)."""
    fs = []
    w = words[i]; cap = (w[:1].isupper())
    pw = words[i - 1].lower().rstrip(".") if i > 0 else "<S>"
    nw = words[i + 1].lower().rstrip(".") if i + 1 < len(words) else "<E>"
    wl = w.lower().rstrip(".")
    if pw in TITLE and cap: fs.append("FR_after_title~%d" % tag)        # Mr. X -> PERSON
    if nw in ORGSUF: fs.append("FR_before_orgsuf~%d" % tag)            # X Inc. -> ORG
    if wl in ORGSUF: fs.append("FR_is_orgsuf~%d" % tag)
    if pw in PREP and cap: fs.append("FR_after_prep_cap~%d" % tag)     # in X -> GPE/LOC
    if nw in REPVERB: fs.append("FR_before_repverb~%d" % tag)          # X said -> PERSON/ORG
    if wl in MONTH: fs.append("FR_month~%d" % tag)                     # DATE
    if pw in MONTH or nw in MONTH: fs.append("FR_near_month~%d" % tag)
    if wl in MONEYW or pw == "$" or "$" in w: fs.append("FR_money~%d" % tag)
    if wl in UNITW: fs.append("FR_unit~%d" % tag)
    if w.isdigit() and nw in (MONTH | UNITW | MONEYW): fs.append("FR_num_before_unit~%d" % tag)
    if cap and pw in TITLE and nw not in ("<E>",) and words[i + 1][:1].isupper(): fs.append("FR_title_multiword~%d" % tag)
    return fs


def _emit(words, i, tag, use_frame):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_frame: fs.extend(_frame_feats(words, i, tag))
    return fs


def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t > 0 and t % 2 == 1:
            j = i + 1
            while j < n and tags[j] == t + 1: j += 1
            sp.add((i, j, (t - 1) // 2)); i = j
        else: i += 1
    return sp


def _selftest():
    assert _spans([0, 1, 2, 0]) == {(1, 3, 0)} and "FR_after_title~1" in _frame_feats(["Mr.", "Smith"], 1, 1)
    print("[selftest] PASS: ner-frame-semantic", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, TAGS, use_frame, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%d~%d" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k], use_frame)) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(6 if not SMOKE else 3):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = vit(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit(words, i, gold[i], use_frame): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i], use_frame): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in test:
        pred = vit(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g}); seed = int(os.environ.get("HDLAB_SEED", "1028"))
    fb = _train_eval(train, test, TAGS, use_frame=False, seed=seed)
    print("  [baseline]      F1=%.4f" % fb, flush=True)
    ff = _train_eval(train, test, TAGS, use_frame=True, seed=seed)
    print("  [+frame-semantic] F1=%.4f" % ff, flush=True)
    lift = ff - fb
    print("  FRAME LIFT = %+.4f | vs reference 0.5817 | train=%d test=%d" % (lift, len(train), len(test)), flush=True)
    return {"f1": round(ff, 4), "f1_frame": round(ff, 4), "f1_baseline": round(fb, 4), "lift": round(lift, 4), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    ff = r["f1_frame"]; fb = r["f1_baseline"]; lift = r["lift"]
    s = "+frame F1=%.4f vs baseline %.4f (lift=%+.4f, train=%d)" % (ff, fb, lift, r["n_train"])
    if lift >= 0.08:
        return ("HARD_PASS", "HARD_PASS: frame-semantic construction features lift NER >=+0.08 -- abstract construction frames are ANTI-SHRINKAGE (generalize beyond lexical features); breaks NER feature saturation. " + s)
    if lift >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: frame features lift +0.02 to +0.08 -- construction abstraction helps, partial. " + s)
    return ("HARD_FAIL", "HARD_FAIL: frame lift <=+0.02 -- construction-frame abstraction SATURATES like lexical features (the prev/next-word features already captured the constructions at scale). " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
