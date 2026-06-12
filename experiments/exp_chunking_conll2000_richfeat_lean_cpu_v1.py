"""
exp_chunking_conll2000_richfeat_lean_cpu_v1.py -- Priority 3 chunking richfeat, LEAN (POS->richfeat only) -- CPU.

ROUTING: Research Priority 3 (Tier-4 chunking milestone). The full richfeat cell timed out TWICE at 1500s before the richfeat
  cascade finished, because it retrains a word-only chunker we ALREADY have (basic-cascade=0.9231, word-only=0.909 from
  chunking_conll2000_cascade_cpu_v1). LEAN drops the redundant word-only retraining: trains the PP-364 POS tagger + ONLY the
  rich-feature POS-cascade chunker (POS-trigram + wider word/POS context + shape-bigram). Reports richfeat-F1 vs the KNOWN
  references (no same-run word-only A/B; the baseline is established). Identical feature set + 6-epoch training to the full cell.
  CoNLL-2000 (HUMAN chunk annotations, 8936/2012). Substrate-only, no LLM.
PRE-REGISTERED (Research gate, unchanged): HARD-PASS richfeat-F1 >= 0.93 (Tier-4 chunking milestone; richer features cross the
  0.93 canonical bar the basic cascade missed at 0.9231). MIDDLE 0.90-0.93. HARD-FAIL < 0.90. UNKNOWN if load fails.
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
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "chunking_conll2000_richfeat_lean_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
REF_WORDONLY = 0.9093     # established: chunking_conll2000_richfeat (word-only) + cascade cell
REF_BASIC_CASCADE = 0.9231  # established: chunking_conll2000_cascade_cpu_v1 (+POS-cascade, basic features)


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


# ---------- chunker emission (rich: word context + predicted-POS cascade) ----------
def _chunk_emit(words, pos, i, tag):
    n = len(words); w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_shape(w), tag)]
    for k in (2, 3):
        if len(wl) >= k: fs.append("suf%d_%s~%s" % (k, wl[-k:], tag))
    pw = words[i - 1].lower() if i > 0 else "<S>"; nw = words[i + 1].lower() if i + 1 < n else "<E>"
    ppw = words[i - 2].lower() if i > 1 else "<S>"; nnw = words[i + 2].lower() if i + 2 < n else "<E>"
    fs.append("pw_%s~%s" % (pw, tag)); fs.append("nw_%s~%s" % (nw, tag))
    fs.append("ppw_%s~%s" % (ppw, tag)); fs.append("nnw_%s~%s" % (nnw, tag))  # wider context
    fs.append("psh_%s_%s~%s" % (_shape(words[i - 1]) if i > 0 else "<S>", _shape(w), tag))  # shape bigram
    p0 = pos[i]; pm = pos[i - 1] if i > 0 else "<S>"; pn = pos[i + 1] if i + 1 < n else "<E>"
    pmm = pos[i - 2] if i > 1 else "<S>"; pnn = pos[i + 2] if i + 2 < n else "<E>"
    fs.append("pos_%s~%s" % (p0, tag)); fs.append("ppos_%s~%s" % (pm, tag)); fs.append("npos_%s~%s" % (pn, tag))
    fs.append("ppos2_%s~%s" % (pmm, tag)); fs.append("npos2_%s~%s" % (pnn, tag))             # wider POS
    fs.append("posbig_%s_%s~%s" % (pm, p0, tag)); fs.append("posbigN_%s_%s~%s" % (p0, pn, tag))
    fs.append("postri_%s_%s_%s~%s" % (pm, p0, pn, tag))                                       # POS-trigram
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
    assert _spans(["B-NP", "I-NP", "O"]) == {(0, 2, "NP")}
    assert "postri_<S>_X_<E>~T" in _chunk_emit(["a"], ["X"], 0, "T")  # POS-trigram (prev=<S>,cur=X,next=<E>) at i=0
    print("[selftest] PASS: chunking-richfeat-lean", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval_chunk(train, test, CTAGS, seed):
    T = len(CTAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "CT_%s~%s" % (p, t)

    def vit(words, pos, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _chunk_emit(words, pos, i, CTAGS[k])) for k in range(T)] for i in range(n)])
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
                        for f in _chunk_emit(words, pos, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _chunk_emit(words, pos, i, pred[i]): w[f] -= 1; cw[f] -= c
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
    import json
    try:
        d = json.load(open(REPO / "experiments" / "data" / "conll2000.json", encoding="utf-8"))
        tr_s = d["splits"]["train"]; dv_s = d["splits"]["test"]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    if SMOKE: tr_s = tr_s[:400]; dv_s = dv_s[:200]
    seed = int(os.environ.get("HDLAB_SEED", "1028"))
    pos_train = [(e["tokens"], e["pos"]) for e in tr_s if 1 <= len(e["tokens"]) <= 60]
    PTAGS = sorted({t for _w, g in pos_train for t in g})
    tagger = _train_seqperc(pos_train, PTAGS, _pos_emit, 5 if not SMOKE else 2, seed)
    ph = pt = 0
    for e in dv_s:
        words = e["tokens"]; gold = e["pos"]; pred = tagger(words)
        for p, g in zip(pred, gold): ph += int(p == g); pt += 1
    pos_acc = ph / pt if pt else 0.0
    print("  [pos-tagger PP-364] CoNLL-2000 test POS acc=%.4f (%d Penn tags)" % (pos_acc, len(PTAGS)), flush=True)

    def mk(sents):
        out = []
        for e in sents:
            if not (1 <= len(e["tokens"]) <= 60): continue
            out.append((e["tokens"], e["chunk_bio"], tagger(e["tokens"])))
        return out
    train = mk(tr_s); test = mk(dv_s)
    CTAGS = sorted({t for _w, g, _p in train for t in g})
    fc = _train_eval_chunk(train, test, CTAGS, seed)
    print("  [chunk +RICHFEAT cascade] F1=%.4f" % fc, flush=True)
    lift_vs_basic = fc - REF_BASIC_CASCADE
    print("  RICHFEAT F1=%.4f | vs basic-cascade %.4f (lift=%+.4f) | vs word-only %.4f | pos-acc=%.4f | train=%d test=%d" % (
        fc, REF_BASIC_CASCADE, lift_vs_basic, REF_WORDONLY, pos_acc, len(train), len(test)), flush=True)
    return {"f1": round(fc, 4), "f1_richfeat": round(fc, 4), "ref_basic_cascade": REF_BASIC_CASCADE,
            "ref_wordonly": REF_WORDONLY, "lift_vs_basic": round(lift_vs_basic, 4),
            "pos_acc": round(pos_acc, 4), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fc = r["f1_richfeat"]; lift = r["lift_vs_basic"]
    s = "richfeat-F1=%.4f vs basic-cascade %.4f (lift=%+.4f), word-only ref %.4f, pos-acc=%.4f, train=%d" % (
        fc, r["ref_basic_cascade"], lift, r["ref_wordonly"], r["pos_acc"], r["n_train"])
    if fc >= 0.93:
        return ("HARD_PASS", "HARD_PASS: rich-feature POS-cascade chunking reaches F1 >=0.93 -- Tier-4 chunking milestone; richer features (POS-trigram + wider context + shape-bigram) cross the canonical bar the basic cascade missed. " + s)
    if fc >= 0.90:
        return ("MIDDLE_BAND", "MIDDLE_BAND: richfeat chunk-F1 0.90-0.93 -- strong; rich features help but below the 0.93 canonical bar (0.9231 basic-cascade stands as honest result). " + s)
    return ("HARD_FAIL", "HARD_FAIL: richfeat cascade chunk-F1 <0.90. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
