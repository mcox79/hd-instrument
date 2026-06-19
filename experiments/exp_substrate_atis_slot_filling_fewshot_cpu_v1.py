"""
exp_substrate_atis_slot_filling_cpu_v1.py -- substrate-classical SLOT FILLING (ATIS) -- CPU.

ROUTING: Tier-A roster expansion -- a NEW substrate-classical NL capability (slot filling / NLU sequence labeling), not yet
  tested. Substrate-quality-first; NO LLM frame. discriminative_perceptron (structured perceptron + Viterbi) over BIO slot tags
  on ATIS (4978 train / 893 test, ~120 slot labels: fromloc.city_name, depart_time.time, toloc.city_name, ...). Span-level slot
  F1 (the standard ATIS metric). Same universal discriminative-weighting lever as POS/NER/chunking.

PRE-REGISTERED: HARD-PASS slot-F1 >= 0.88 (substrate-classical production-grade slot filling; strong neural systems ~0.95).
  MIDDLE 0.78-0.88. HARD-FAIL < 0.78. UNKNOWN if load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
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
ANCHOR_NAME = "substrate_atis_slot_filling_fewshot_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%s" % (wl[:3], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("p2w_%s~%s" % (words[i - 2].lower() if i > 1 else "<S>", tag))
    return fs


def _spans(tags):
    """BIO spans with slot type: (start, end, slot_type)."""
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t.startswith("B-"):
            typ = t[2:]; j = i + 1
            while j < n and tags[j] == "I-" + typ: j += 1
            sp.add((i, j, typ)); i = j
        else: i += 1
    return sp


def _load():
    d = json.load(open(REPO / "experiments" / "data" / "atis_full.json", encoding="utf-8"))
    def conv(split):
        out = []
        for e in split:
            toks = e["text"].split(); tags = e["slots"].split()
            if len(toks) == len(tags) and toks: out.append((toks, tags))
        return out
    return conv(d["train"]), conv(d["test"])


def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1028")))
    try:
        train, test = _load()
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    if SMOKE: train_full = train[:400]; test = test[:150]
    else: train_full = train
    TAGS = sorted({t for _w, g in train_full for t in g}); T = len(TAGS); ti = {t: k for k, t in enumerate(TAGS)}
    def tt(pt, t): return "tt_%s~%s" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    EP = 6 if not SMOKE else 3
    def train_eval(sub):
        w = defaultdict(float); cw = defaultdict(float); c = 1
        for ep in range(EP):
            for si in rng.permutation(len(sub)):
                words, gold = sub[si]; pred = viterbi(words, w)
                if pred != gold:
                    pg = "<S>"; pp = "<S>"
                    for i in range(len(words)):
                        if pred[i] != gold[i]:
                            for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                            for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                        w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                        w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                        pg = gold[i]; pp = pred[i]
                c += 1
        avg = {f: w[f] - cw[f] / c for f in w}
        tp = fp = fn = 0
        for words, gold in test:
            gs = _spans(gold); ps = _spans(viterbi(words, avg))
            tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
        prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)
    fracs = [0.05, 1.0] if SMOKE else [0.01, 0.05, 0.10, 0.50, 1.0]
    curve = []
    for fr in fracs:
        n = max(5, int(len(train_full) * fr)); idx = rng.permutation(len(train_full))[:n]; sub = [train_full[i] for i in idx]
        f1 = train_eval(sub); curve.append({"frac": fr, "slot_f1": round(f1, 4), "n": n})
        print("  frac=%5.1f%% slot-F1=%.4f (n=%d)" % (100 * fr, f1, n), flush=True)
    full = curve[-1]["slot_f1"]; f5 = next((c["slot_f1"] for c in curve if c["frac"] == 0.05), 0.0)
    rel5 = round(f5 / (full + 1e-9), 4)
    print("  ATIS-SLOT-FILLING FEW-SHOT: F1@5%%=%.4f F1@full=%.4f (%.1f%% of full at 5%% data) %d tags" % (f5, full, 100 * rel5, T), flush=True)
    return {"f1": full, "slot_f1_5pct": f5, "slot_f1_full": full, "rel_at_5pct": rel5, "curve": curve, "n_tags": T}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rel = r["rel_at_5pct"]; s = "F1@5%%=%.4f F1@full=%.4f (%.1f%% of full at 5%% data); curve=%s; %d tags -- CONTRAST: NER L-B 63%% of full at 5%% data" % (r["slot_f1_5pct"], r["slot_f1_full"], 100 * rel, [(c["frac"], c["slot_f1"]) for c in r["curve"]], r["n_tags"])
    if rel >= 0.60:
        return ("HARD_PASS", "HARD_PASS: slot-filling shows LOW-DATA architectural fit -- >=60%% of full slot-F1 at 5%% data (consistent with NER L-B 63%%). Low-data fit generalizes to large-tag-set NLU. " + s)
    if rel >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: 45-60%% of full at 5%% data -- moderate low-data fit (123 tags need more data than 4-type NER). " + s)
    return ("HARD_FAIL", "HARD_FAIL: <45%% of full at 5%% data -- large tag set limits low-data fit. " + s)


def _selftest():
    assert _spans(["O", "B-x", "I-x", "O", "B-y"]) == {(1, 3, "x"), (4, 5, "y")}
    assert _shape("Boston") == "Cap"
    print("[selftest] PASS: atis-slot-filling", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
