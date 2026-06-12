"""
exp_chunking_pos_cascade_cpu_v1.py -- Priority 3: PP-364 POS-HMM -> chunking cascade (mechanism transfer) -- CPU.

ROUTING: Research consolidated Priority 3 (Drill 2 P1 transfer + Tier-4 milestone). The PP-364 POS-tagger mechanism (structured-
  perceptron + Viterbi) cascaded into chunking: predict POS, use PREDICTED-POS as chunk features (canonical syntactic cascade).
  Tests the transfer-conditions framework prediction (P1, HARD-PASS chunk-F1 >= 0.93) + the Tier-4 substrate-extracted-methodology
  milestone. UD-EWT (CoNLL-2000 unloadable; benchmark-agnostic transfer test per Research -- chunk labels derived from gold POS, so
  this measures whether the predicted-POS cascade recovers them above word-only features). A/B: word-only vs +predicted-POS cascade.
  Substrate-only, no LLM.
PRE-REGISTERED (Research gate): HARD-PASS chunk-F1 >= 0.93 (cascade reaches canonical syntactic-cascade level). MIDDLE 0.90-0.93.
  HARD-FAIL < 0.90. Reports POS-cascade lift over word-only. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "chunking_pos_cascade_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NPOS = {"DET", "ADJ", "NUM", "NOUN", "PROPN", "PRON"}; VPOS = {"VERB", "AUX"}


def _chunk_type(pos):
    if pos in NPOS: return "NP"
    if pos in VPOS: return "VP"
    if pos == "ADP": return "PP"
    return "O"


def _bio(posseq):
    tags = []; prev = "O"
    for pos in posseq:
        ct = _chunk_type(pos)
        if ct == "O": tags.append("O"); prev = "O"
        elif ct == prev: tags.append("I-" + ct)
        else: tags.append("B-" + ct); prev = ct
    return tags


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper(): return "Cap"
    if "-" in w: return "HYP"
    return "low"


# ---------- POS tagger (PP-364 structured-perceptron + Viterbi) ----------
def _pos_emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def _train_seqperc(train, TAGS, emit_fn, epochs, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "T_%s~%s" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in emit_fn(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    for ep in range(epochs):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = vit(words, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in emit_fn(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in emit_fn(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return lambda words: vit(words, avg)


# ---------- chunker emission (word features + optional predicted-POS cascade) ----------
def _chunk_emit(words, pos, i, tag, use_pos):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    if use_pos and pos is not None:
        fs.append("pos_%s~%s" % (pos[i], tag))
        fs.append("ppos_%s~%s" % (pos[i - 1] if i > 0 else "<S>", tag))
        fs.append("npos_%s~%s" % (pos[i + 1] if i + 1 < len(words) else "<E>", tag))
        fs.append("posbig_%s_%s~%s" % (pos[i - 1] if i > 0 else "<S>", pos[i], tag))
    return fs


def _spans(tags):
    sp = set(); i = 0; n = len(tags)
    while i < n:
        t = tags[i]
        if t.startswith("B-"):
            ty = t[2:]; j = i + 1
            while j < n and tags[j] == "I-" + ty: j += 1
            sp.add((i, j, ty)); i = j
        else: i += 1
    return sp


def _selftest():
    assert _bio(["DET", "NOUN", "VERB"]) == ["B-NP", "I-NP", "B-VP"] and _spans(["B-NP", "I-NP", "O"]) == {(0, 2, "NP")}
    print("[selftest] PASS: chunking-pos-cascade", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval_chunk(train, test, CTAGS, use_pos, seed):
    T = len(CTAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "CT_%s~%s" % (p, t)

    def vit(words, pos, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _chunk_emit(words, pos, i, CTAGS[k], use_pos)) for k in range(T)] for i in range(n)])
        TM = np.array([[weights.get(tt(CTAGS[j], CTAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt("<S>", CTAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [CTAGS[k] for k in seq]

    for ep in range(6 if not SMOKE else 3):
        for si in rng.permutation(len(train)):
            words, gold, pos = train[si]; pred = vit(words, pos, w)
            if pred != gold:
                pg = "<S>"; pp = "<S>"
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _chunk_emit(words, pos, i, gold[i], use_pos): w[f] += 1; cw[f] += c
                        for f in _chunk_emit(words, pos, i, pred[i], use_pos): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold, pos in test:
        pred = vit(words, pos, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); return 2 * prec * rec / (prec + rec + 1e-9)


def run() -> Dict:
    try:
        tr_s = [s for s in load_conllu("train") if 1 <= len(s) <= 50]
        dv_s = [s for s in load_conllu("dev") if 1 <= len(s) <= 50]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    if not SMOKE: tr_s = tr_s[:3000]
    else: tr_s = tr_s[:300]; dv_s = dv_s[:150]
    seed = int(os.environ.get("HDLAB_SEED", "1028"))
    # POS tagger (PP-364 mechanism)
    pos_train = [([t[1] for t in s], [t[2] for t in s]) for s in tr_s]
    PTAGS = sorted({t for _w, g in pos_train for t in g})
    tagger = _train_seqperc(pos_train, PTAGS, _pos_emit, 5 if not SMOKE else 2, seed)
    # POS-tagger accuracy (diagnostic)
    ph = pt = 0
    for s in dv_s:
        words = [t[1] for t in s]; gold = [t[2] for t in s]; pred = tagger(words)
        for p, g in zip(pred, gold): ph += int(p == g); pt += 1
    pos_acc = ph / pt if pt else 0.0
    print("  [pos-tagger PP-364] dev acc=%.4f (%d tags)" % (pos_acc, len(PTAGS)), flush=True)
    # chunking data: words, gold-chunk-BIO (from gold POS), predicted POS
    def mk(sents):
        out = []
        for s in sents:
            words = [t[1] for t in s]; goldpos = [t[2] for t in s]
            chunks = _bio(goldpos); ppos = tagger(words)
            out.append((words, chunks, ppos))
        return out
    train = mk(tr_s); test = mk(dv_s)
    CTAGS = sorted({t for _w, g, _p in train for t in g})
    fb = _train_eval_chunk(train, test, CTAGS, use_pos=False, seed=seed)
    print("  [chunk word-only]    F1=%.4f" % fb, flush=True)
    fp_ = _train_eval_chunk(train, test, CTAGS, use_pos=True, seed=seed)
    print("  [chunk +POS-cascade] F1=%.4f" % fp_, flush=True)
    lift = fp_ - fb
    print("  POS-CASCADE LIFT = %+.4f | pos-acc=%.4f | train=%d test=%d" % (lift, pos_acc, len(train), len(test)), flush=True)
    return {"f1": round(fp_, 4), "f1_cascade": round(fp_, 4), "f1_wordonly": round(fb, 4), "lift": round(lift, 4),
            "pos_acc": round(pos_acc, 4), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fc = r["f1_cascade"]; fw = r["f1_wordonly"]; lift = r["lift"]
    s = "+POS-cascade F1=%.4f vs word-only %.4f (lift=%+.4f, pos-acc=%.4f, train=%d)" % (fc, fw, lift, r["pos_acc"], r["n_train"])
    if fc >= 0.93:
        return ("HARD_PASS", "HARD_PASS: PP-364 POS-HMM -> chunking cascade reaches chunk-F1 >=0.93 -- the syntactic cascade (POS-tag then chunk) transfers; transfer-conditions P1 confirmed + Tier-4 chunking milestone. " + s)
    if fc >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: cascade chunk-F1 0.90-0.93 -- strong; POS cascade helps but below the 0.93 canonical bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: cascade chunk-F1 <0.90. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
