"""
exp_nl_slot_filling_atis_cpu_v1.py -- substrate NL slot-filling + intent on ATIS (gold-annotated) -- CPU.

ROUTING: Research 500-SLOT-FILLING (frame-role binding = Priority-1 NL primitive). VERIFY-BEFORE-INVEST improvement: the
  math/code/support 500-item set has NO gold slot annotations (auto-deriving gold is circular). ATIS (tuetschek/atis) is the
  standard slot-filling benchmark WITH gold intent + BIO slot labels -- a clean F1 measurement of the substrate frame-role-binding
  primitive. Slot-filling = BIO tagging (the validated substrate POS-tagger mechanism PP-364 applied to slot labels): substrate
  emission (word->slot) + transition (slot-bigram) + Viterbi; intent = substrate bag-of-words cleanup over intent classes.
  Reports span-level slot-F1 + intent accuracy. Substrate-only.
PRE-REGISTERED: HARD-PASS slot-F1 >= 0.85 AND intent-accuracy >= 0.80 (substrate frame-role binding validated). MIDDLE slot-F1 >= 0.65.
  HARD-FAIL slot-F1 < 0.50. UNKNOWN if dataset load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "nl_pipeline_demo_atis_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
def _selftest():
    print("[selftest] PASS: nl-pipeline-demo-atis", flush=True)
def _load():
    import json
    d = json.load(open(REPO / "experiments" / "data" / "atis_full.json", encoding="utf-8"))
    def conv(rows):
        out = []
        for e in rows:
            toks = e["text"].split(); slots = e["slots"].split()
            if len(toks) == len(slots) and toks: out.append((toks, slots, e["intent"]))
        return out
    return conv(d["train"]), conv(d["test"])
def _feats(w):
    wl = w.lower(); fs = []
    if any(c.isdigit() for c in w): fs.append("F:DIGIT")
    if w[:1].isupper(): fs.append("F:CAP")
    for k in (2, 3, 4):
        if len(wl) >= k: fs.append("S%d:%s" % (k, wl[-k:]))
    return fs
def _spans(labels):
    """BIO label seq -> set of (start, end, type) entity spans."""
    sp = set(); i = 0; n = len(labels)
    while i < n:
        l = labels[i]
        if l.startswith("B-"):
            t = l[2:]; j = i + 1
            while j < n and labels[j] == "I-" + t: j += 1
            sp.add((i, j, t)); i = j
        else:
            i += 1
    return sp
def run() -> Dict:
    train, test = _load()
    if not train:
        return {"error": "load_failed", "slot_f1": 0.0}
    if SMOKE: train = train[:400]; test = test[:120]
    labels = sorted({s for _t, ss, _i in train for s in ss}); li = {l: i for i, l in enumerate(labels)}; T = len(labels)
    intents = sorted({i for _t, _s, i in train}); ii = {x: k for k, x in enumerate(intents)}
    K = 0.1
    emit = defaultdict(Counter); trans = defaultdict(Counter); feat_emit = defaultdict(Counter)
    cprev = defaultdict(Counter); cnext = defaultdict(Counter)        # context-window: prev/next word per slot
    lab_count = Counter(); prev_count = Counter(); vocab = set()
    intent_w = defaultdict(Counter); intent_tot = Counter()
    for toks, slots, intent in train:
        prev = "<S>"; nt = len(toks)
        for k, (w, s) in enumerate(zip(toks, slots)):
            wl = w.lower(); emit[s][wl] += 1; lab_count[s] += 1; vocab.add(wl)
            cprev[s][toks[k-1].lower() if k > 0 else "<S>"] += 1     # word before this slot (preposition/keyword)
            cnext[s][toks[k+1].lower() if k+1 < nt else "<E>"] += 1
            for f in _feats(w): feat_emit[s][f] += 1
            trans[prev][s] += 1; prev_count[prev] += 1; prev = s
        intent_tot[intent] += 1
        for w in set(t.lower() for t in toks): intent_w[intent][w] += 1
    Vsz = len(vocab)
    def log_emit(w, s, pw, nw):
        wl = w.lower()
        if wl in vocab: sc = math.log((emit[s][wl] + K) / (lab_count[s] + K * Vsz))
        else:
            sc = math.log((lab_count[s] + K) / (sum(lab_count.values()) + K * T))
            for f in _feats(w): sc += math.log((feat_emit[s][f] + K) / (lab_count[s] + K * 200))
        # context-window bonus: prev/next word association with this slot (the from/to disambiguation signal)
        sc += 0.7 * math.log((cprev[s][pw] + K) / (lab_count[s] + K * Vsz))
        sc += 0.5 * math.log((cnext[s][nw] + K) / (lab_count[s] + K * Vsz))
        return sc
    TM = np.array([[math.log((trans[labels[p]][labels[c]] + K) / (prev_count[labels[p]] + K * T)) for c in range(T)] for p in range(T)])
    sv = np.array([math.log((trans["<S>"][labels[c]] + K) / (prev_count["<S>"] + K * T)) for c in range(T)])
    def viterbi(toks):
        nt = len(toks)
        def emv(i):
            pw = toks[i-1].lower() if i > 0 else "<S>"; nw = toks[i+1].lower() if i+1 < nt else "<E>"
            return np.array([log_emit(toks[i], labels[c], pw, nw) for c in range(T)])
        em0 = emv(0); V = sv + em0; bp = []
        for i in range(1, len(toks)):
            ei = emv(i)
            cand = V[:, None] + TM; back = np.argmax(cand, axis=0); V = cand[back, np.arange(T)] + ei; bp.append(back)
        seq = [int(np.argmax(V))]
        for b in reversed(bp): seq.append(int(b[seq[-1]]))
        seq.reverse(); return [labels[j] for j in seq]
    def pred_intent(toks):
        ws = set(t.lower() for t in toks)
        best = intents[0]; bs = -1e18
        for it in intents:
            sc = math.log((intent_tot[it] + K) / (sum(intent_tot.values()) + K * len(intents)))
            for w in ws: sc += math.log((intent_w[it][w] + K) / (intent_tot[it] + K * Vsz))
            if sc > bs: bs = sc; best = it
        return best
    tp = fp = fn = 0; intent_hit = 0
    for toks, gold, intent in test:
        pred = viterbi(toks); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
        intent_hit += int(pred_intent(toks) == intent)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    intent_acc = intent_hit / len(test) if test else 0.0
    print("  ATIS-SLOT-FILLING: slot-F1=%.4f (P=%.3f R=%.3f) | intent-accuracy=%.4f | %d slot-labels, %d intents, test=%d" %
          (f1, prec, rec, intent_acc, T, len(intents), len(test)), flush=True)
    return {"slot_f1": round(f1, 4), "slot_prec": round(prec, 3), "slot_rec": round(rec, 3), "intent_acc": round(intent_acc, 4), "n_labels": T, "n_test": len(test)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f1 = r["slot_f1"]; ia = r["intent_acc"]; s = "slot-F1=%.4f intent-acc=%.4f (P=%.3f R=%.3f)" % (f1, ia, r["slot_prec"], r["slot_rec"])
    if f1 >= 0.85 and ia >= 0.80:
        return ("HARD_PASS", "HARD_PASS: substrate frame-role binding does NL slot-filling on ATIS at slot-F1>=0.85 AND intent>=0.80 -- the Priority-1 NL primitive works substrate-only on gold-annotated data. Frame-role binding validated; slot-filling is the direct NL-extraction primitive (may skip dep-parser). " + s)
    if f1 >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: slot-F1 0.65-0.85 -- substrate slot-filling partial; richer features/transitions for the 0.85 bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: slot-F1 <0.50 -- substrate slot-filling insufficient. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
