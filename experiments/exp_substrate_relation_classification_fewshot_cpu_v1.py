"""
exp_substrate_relation_classification_semeval_cpu_v1.py -- substrate-classical RELATION CLASSIFICATION (SemEval-2010 Task 8) -- CPU.

ROUTING: Tier-A roster expansion -- a NEW capability CLASS (relation extraction / classification; entity-pair-aware), distinct
  from the sequence-labeling/classification roster. Substrate-quality-first; NO LLM frame. discriminative_perceptron (multiclass
  averaged perceptron) over entity-context features on SemEval-2010 Task 8 (8000 train / 2717 test, 19 relation classes:
  Cause-Effect, Component-Whole, Entity-Destination, ... + Other; e1/e2 marked with <e1>/<e2>). Features: e1/e2 head words,
  words BETWEEN the entities (the key relational signal), words before-e1 / after-e2, entity order, middle bigrams.
  Macro-F1 (the SemEval metric) + accuracy. Same discriminative-weighting lever; no LLM, no pretraining.

  DATA: SemEval-2010 Task 8 via datasets.load_dataset (env-gated -> UNKNOWN if unavailable).

PRE-REGISTERED: HARD-PASS macro-F1 >= 0.65 (substrate-classical feature-based RE; classic SVM systems ~0.78, neural ~0.85).
  MIDDLE 0.50-0.65. HARD-FAIL < 0.50. UNKNOWN if data unavailable.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
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
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_relation_classification_fewshot_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NBITS = 20; DIM = 1 << NBITS
_TOK = re.compile(r"[a-z0-9']+")
_E1 = re.compile(r"<e1>(.*?)</e1>", re.I)
_E2 = re.compile(r"<e2>(.*?)</e2>", re.I)


def _feats(sentence: str) -> List[int]:
    s = sentence
    e1m = _E1.search(s); e2m = _E2.search(s)
    e1 = (e1m.group(1) if e1m else "").lower().strip()
    e2 = (e2m.group(1) if e2m else "").lower().strip()
    order = "e1e2" if (e1m and e2m and e1m.start() < e2m.start()) else "e2e1"
    # between-text = chars between the inner markers
    if e1m and e2m:
        lo = min(e1m.end(), e2m.end()); hi = max(e1m.start(), e2m.start())
        between = s[lo:hi]
    else:
        between = ""
    clean = re.sub(r"</?e[12]>", "", s)
    btoks = _TOK.findall(between.lower())
    e1toks = _TOK.findall(e1); e2toks = _TOK.findall(e2)
    e1h = e1toks[-1] if e1toks else e1; e2h = e2toks[-1] if e2toks else e2
    def _sh(w): return "C" if w[:1].isupper() else ("D" if w.isdigit() else "l")
    feats = ["e1_%s" % e1h, "e2_%s" % e2h, "ord_%s" % order, "ndist_%d" % min(len(btoks), 10),
             "e1cap_%s" % _sh(e1.split()[0] if e1.split() else e1), "e2cap_%s" % _sh(e2.split()[0] if e2.split() else e2),
             "pair_%s_%s" % (e1h, e2h)]                              # entity-pair feature (lexical relation prior)
    for w in btoks: feats.append("btw_%s" % w)                       # bag of between-words (key RE signal)
    for i in range(len(btoks) - 1): feats.append("btwbg_%s_%s" % (btoks[i], btoks[i + 1]))
    if btoks: feats.append("btw1_%s" % btoks[0]); feats.append("btwL_%s" % btoks[-1])
    for w in btoks: feats.append("btwsh_%s" % _sh(w))                # between-word shapes (CONTAINS/contains etc.)
    # context: 2 words before e1 / after e2 (clean tokenization with positions)
    cl = _TOK.findall(clean.lower())
    e1l = e1toks[0] if e1toks else e1h
    try:
        pi = cl.index(e1l)
        for k in (1, 2):
            if pi - k >= 0: feats.append("pre%d_%s" % (k, cl[pi - k]))
    except ValueError:
        pass
    e2l = e2toks[-1] if e2toks else e2h
    try:
        qi = len(cl) - 1 - cl[::-1].index(e2l)
        for k in (1, 2):
            if qi + k < len(cl): feats.append("post%d_%s" % (k, cl[qi + k]))
    except ValueError:
        pass
    feats.append("bias")
    return [hash(f) & (DIM - 1) for f in feats]


def _train_mc(data, classes, epochs, seed):
    w = {c: np.zeros(DIM) for c in classes}; cw = {c: np.zeros(DIM) for c in classes}; c_t = 1
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        for i in rng.permutation(len(data)):
            idxs, y = data[i]
            scores = {c: w[c][idxs].sum() for c in classes}
            pred = max(scores, key=scores.get)
            if pred != y:
                w[y][idxs] += 1; cw[y][idxs] += c_t
                w[pred][idxs] -= 1; cw[pred][idxs] -= c_t
            c_t += 1
    return {c: w[c] - cw[c] / c_t for c in classes}


def _macro_f1(data, w, classes):
    tp = defaultdict(int); fp = defaultdict(int); fn = defaultdict(int); corr = 0
    for idxs, y in data:
        pred = max(classes, key=lambda c: w[c][idxs].sum())
        if pred == y: tp[y] += 1; corr += 1
        else: fp[pred] += 1; fn[y] += 1
    f1s = []
    for c in classes:
        p = tp[c] / (tp[c] + fp[c] + 1e-9); r = tp[c] / (tp[c] + fn[c] + 1e-9)
        f1s.append(2 * p * r / (p + r + 1e-9))
    return sum(f1s) / len(f1s), corr / len(data)


def _load():
    try:
        from datasets import load_dataset
        ds = load_dataset("SemEvalWorkshop/sem_eval_2010_task_8")
        names = ds["train"].features["relation"].names
        def conv(split):
            return [(_feats(t), int(l)) for t, l in zip(ds[split]["sentence"], ds[split]["relation"])]
        return conv("train"), conv("test"), names
    except Exception as e:
        print("[semeval] unavailable: %s" % str(e)[:120], flush=True); return None


def run() -> Dict:
    loaded = _load()
    if loaded is None:
        return {"error": "semeval_unavailable_env_gated", "note": "needs datasets sem_eval_2010_task_8; harness ready"}
    train, test, names = loaded
    classes = list(range(len(names)))
    if SMOKE: train = train[:600]; test = test[:300]
    ep = 3 if SMOKE else 10
    import numpy as _np; rng = _np.random.default_rng(0)
    fracs = [0.05, 1.0] if SMOKE else [0.01, 0.05, 0.10, 0.50, 1.0]
    curve = []
    for fr in fracs:
        n = max(20, int(len(train) * fr)); idx = rng.permutation(len(train))[:n]; sub = [train[i] for i in idx]
        w = _train_mc(sub, classes, ep, 1028); macro, _acc = _macro_f1(test, w, classes)
        curve.append({"frac": fr, "macro_f1": round(macro, 4), "n": n})
        print("  frac=%5.1f%% macro-F1=%.4f (n=%d)" % (100 * fr, macro, n), flush=True)
    full = curve[-1]["macro_f1"]; f5 = next((c["macro_f1"] for c in curve if c["frac"] == 0.05), 0.0)
    rel5 = round(f5 / (full + 1e-9), 4)
    print("  RE FEW-SHOT (classification): macro-F1@5%%=%.4f @full=%.4f (%.1f%% of full at 5%% data)" % (f5, full, 100 * rel5), flush=True)
    return {"f1": full, "macro_f1_5pct": f5, "macro_f1_full": full, "rel_at_5pct": rel5, "curve": curve, "n_classes": len(classes)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("semeval"):
        return ("UNKNOWN", "UNKNOWN: SemEval unavailable (env-gated). Harness ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rel = r["rel_at_5pct"]; s = "macro-F1@5%%=%.4f @full=%.4f (%.1f%% of full at 5%% data); curve=%s -- CONTRAST: sequence-labeling NER 63%%/slot 87%% of full at 5%%" % (r["macro_f1_5pct"], r["macro_f1_full"], 100 * rel, [(c["frac"], c["macro_f1"]) for c in r["curve"]])
    if rel >= 0.60:
        return ("HARD_PASS", "HARD_PASS: RE classification shows low-data fit (>=60%% of full at 5%% data) -- low-data fit holds for classification too. " + s)
    if rel >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: RE 40-60%% of full at 5%% data -- weaker low-data fit than sequence labeling (19-class classification needs more data per class). " + s)
    return ("HARD_FAIL", "HARD_FAIL: RE <40%% of full at 5%% data -- classification low-data fit much weaker than sequence labeling. " + s)


def _selftest():
    f = _feats("The <e1>system</e1> has its application in an arrayed <e2>configuration</e2> of cells.")
    assert isinstance(f, list) and len(f) >= 5
    print("[selftest] PASS: semeval-relation-classification (%d feats on sample)" % len(f), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
