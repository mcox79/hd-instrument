"""
exp_substrate_relation_classification_pos_composed_cpu_v1.py -- CAPABILITY COMPOSITION: substrate POS tagger -> relation classification -- CPU.

ROUTING: substrate-product positioning -- CAPABILITY COMPOSITION. The substrate composes its OWN primitives: a POS tagger
  (structured perceptron trained on PTB, Tier-A 0.95) tags the SemEval sentences, and the POS tags become features for the
  relation classifier (multiclass perceptron). Lexical RE capped at ~0.672 (separate cell); POS structure is the standard
  feature that lifts feature-based RE. Tests whether substrate capability COMPOSITION (POS -> RE) lifts RE past the lexical
  ceiling -- a positioning point LLMs do implicitly, the substrate does as EXPLICIT composed primitives. Substrate-quality-first; NO LLM.

  DATA: PTB bundled (POS source). SemEval-2010 Task 8 via datasets (env-gated -> UNKNOWN).

PRE-REGISTERED: HARD-PASS POS-composed macro-F1 >= 0.69 (>=+0.02 over lexical-only 0.672 -- composition lifts RE). MIDDLE
  0.65-0.69 (composition neutral; lexical already strong). HARD-FAIL < 0.65 (POS composition hurts). UNKNOWN if data unavailable.
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
ANCHOR_NAME = "substrate_relation_classification_pos_composed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NBITS = 20; DIM = 1 << NBITS
_TOK = re.compile(r"[A-Za-z0-9']+")
_E1 = re.compile(r"<e1>(.*?)</e1>", re.I)
_E2 = re.compile(r"<e2>(.*?)</e2>", re.I)


# ---------- substrate POS tagger (structured perceptron + Viterbi, trained on PTB) ----------
def _pshape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _pemit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%s" % (wl, tag), "sh_%s~%s" % (_pshape(w), tag)]
    for k in (1, 2, 3):
        if len(wl) >= k: fs.append("sf%d_%s~%s" % (k, wl[-k:], tag))
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def _train_pos(train, TAGS, epochs, seed):
    T = len(TAGS); rng = np.random.default_rng(seed); w = defaultdict(float); cw = defaultdict(float); c = 1
    def tt(pt, t): return "tt_%s~%s" % (pt, t)
    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _pemit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
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
                    if pred[i] != gold[i]:
                        for f in _pemit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _pemit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return avg, TAGS


def _pos_tag(words, avg, TAGS):
    T = len(TAGS); n = len(words)
    def tt(pt, t): return "tt_%s~%s" % (pt, t)
    em = np.array([[sum(avg.get(f, 0.0) for f in _pemit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
    TM = np.array([[avg.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
    SV = np.array([avg.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
    V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
    for i in range(1, n):
        cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
    seq = [int(np.argmax(V[n - 1]))]
    for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
    seq.reverse(); return [TAGS[k] for k in seq]


# ---------- relation features (lexical + composed POS) ----------
def _re_feats(sentence, pos_avg, pos_tags, use_pos):
    e1m = _E1.search(sentence); e2m = _E2.search(sentence)
    e1 = (e1m.group(1) if e1m else "").strip(); e2 = (e2m.group(1) if e2m else "").strip()
    order = "e1e2" if (e1m and e2m and e1m.start() < e2m.start()) else "e2e1"
    clean = re.sub(r"</?e[12]>", " ", sentence)
    toks = _TOK.findall(clean)
    e1toks = _TOK.findall(e1); e2toks = _TOK.findall(e2)
    e1h = (e1toks[-1] if e1toks else e1).lower(); e2h = (e2toks[-1] if e2toks else e2).lower()
    # locate e1/e2 head positions in toks (lowercased match)
    low = [t.lower() for t in toks]
    try: p1 = low.index(e1h)
    except ValueError: p1 = 0
    try: p2 = len(low) - 1 - low[::-1].index(e2h)
    except ValueError: p2 = len(low) - 1
    lo, hi = (p1, p2) if p1 <= p2 else (p2, p1)
    btoks = low[lo + 1:hi]
    feats = ["e1_%s" % e1h, "e2_%s" % e2h, "ord_%s" % order, "pair_%s_%s" % (e1h, e2h), "ndist_%d" % min(hi - lo, 10), "bias"]
    for w in btoks: feats.append("btw_%s" % w)
    for i in range(len(btoks) - 1): feats.append("btwbg_%s_%s" % (btoks[i], btoks[i + 1]))
    if btoks: feats.append("btw1_%s" % btoks[0]); feats.append("btwL_%s" % btoks[-1])
    if use_pos and toks:
        pos = _pos_tag(toks, pos_avg, pos_tags)
        ptw = pos[lo + 1:hi]
        feats.append("e1pos_%s" % (pos[p1] if p1 < len(pos) else "?"))
        feats.append("e2pos_%s" % (pos[p2] if p2 < len(pos) else "?"))
        for pt in ptw: feats.append("btwpos_%s" % pt)                # POS of between-words (composed from substrate POS tagger)
        for i in range(len(ptw) - 1): feats.append("btwposbg_%s_%s" % (ptw[i], ptw[i + 1]))
        feats.append("posseq_%s" % "-".join(ptw[:5]))               # POS path proxy
    return [hash(f) & (DIM - 1) for f in feats]


def _train_mc(data, classes, epochs, seed):
    w = {c: np.zeros(DIM) for c in classes}; cw = {c: np.zeros(DIM) for c in classes}; c_t = 1
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        for i in rng.permutation(len(data)):
            idxs, y = data[i]; scores = {c: w[c][idxs].sum() for c in classes}; pred = max(scores, key=scores.get)
            if pred != y:
                w[y][idxs] += 1; cw[y][idxs] += c_t; w[pred][idxs] -= 1; cw[pred][idxs] -= c_t
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
        p = tp[c] / (tp[c] + fp[c] + 1e-9); r = tp[c] / (tp[c] + fn[c] + 1e-9); f1s.append(2 * p * r / (p + r + 1e-9))
    return sum(f1s) / len(f1s), corr / len(data)


def _load_ptb():
    d = json.load(open(REPO / "experiments" / "data" / "ptb_treebank_tagged.json", encoding="utf-8"))
    return [([t[0] for t in s], [t[1] for t in s]) for s in d if s and len(s) <= 60]


def _load_semeval():
    from datasets import load_dataset
    ds = load_dataset("SemEvalWorkshop/sem_eval_2010_task_8")
    names = ds["train"].features["relation"].names
    return ds, names


def run() -> Dict:
    try:
        ptb = _load_ptb()
    except Exception as e:
        return {"error": "ptb_load_failed: " + str(e)[:60]}
    try:
        ds, names = _load_semeval()
    except Exception as e:
        print("[semeval] unavailable: %s" % str(e)[:100], flush=True)
        return {"error": "semeval_unavailable_env_gated", "note": "needs datasets; harness ready"}
    # train substrate POS tagger on PTB
    if SMOKE: ptb = ptb[:300]
    PTAGS = sorted({t for _w, g in ptb for t in g})
    pos_avg, pos_tags = _train_pos(ptb, PTAGS, 3 if SMOKE else 5, 7)
    print("  [compose] substrate POS tagger trained on PTB (%d sents, %d tags)" % (len(ptb), len(PTAGS)), flush=True)
    classes = list(range(len(names)))
    ntr = 600 if SMOKE else 8000; nte = 300 if SMOKE else 2717
    tr_sent = list(zip(ds["train"]["sentence"], ds["train"]["relation"]))[:ntr]
    te_sent = list(zip(ds["test"]["sentence"], ds["test"]["relation"]))[:nte]
    ep = 3 if SMOKE else 10
    out = {}
    for use_pos in (False, True):
        tr = [(_re_feats(s, pos_avg, pos_tags, use_pos), int(l)) for s, l in tr_sent]
        te = [(_re_feats(s, pos_avg, pos_tags, use_pos), int(l)) for s, l in te_sent]
        w = _train_mc(tr, classes, ep, 1028)
        macro, acc = _macro_f1(te, w, classes)
        out["pos" if use_pos else "lexical"] = {"macro_f1": round(macro, 4), "acc": round(acc, 4)}
        print("  RE %s: macro-F1=%.4f acc=%.4f" % (("+POS-composed" if use_pos else "lexical-only"), macro, acc), flush=True)
    lift = round(out["pos"]["macro_f1"] - out["lexical"]["macro_f1"], 4)
    print("  COMPOSITION LIFT (POS->RE): %+.4f" % lift, flush=True)
    return {"f1": out["pos"]["macro_f1"], "lexical": out["lexical"], "pos_composed": out["pos"], "composition_lift": lift, "n_classes": len(classes)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("semeval"):
        return ("UNKNOWN", "UNKNOWN: SemEval unavailable (env-gated). " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    pm = r["pos_composed"]["macro_f1"]; lift = r["composition_lift"]
    s = "POS-composed macro-F1=%.4f vs lexical %.4f (composition lift %+.4f)" % (pm, r["lexical"]["macro_f1"], lift)
    if pm >= 0.69 and lift >= 0.02:
        return ("HARD_PASS", "HARD_PASS: substrate CAPABILITY COMPOSITION (POS tagger -> relation classifier) lifts RE by >=+0.02 to >=0.69 -- the substrate composes its OWN primitives to lift a downstream task (explicit, unlike LLM implicit). " + s)
    if pm >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: POS composition neutral/small (lift <0.02) -- lexical features already capture most signal; composition works but adds little here. " + s)
    return ("HARD_FAIL", "HARD_FAIL: POS composition hurts (<0.65) -- out-of-domain POS tags add noise. " + s)


def _selftest():
    f = _re_feats("The <e1>cat</e1> sat on the <e2>mat</e2> .", {}, ["NN", "VB"], False)
    assert isinstance(f, list) and len(f) >= 5
    print("[selftest] PASS: relation-pos-composed", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
