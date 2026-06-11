"""
exp_ner_gazetteer_substrate_cpu_v1.py -- NER: substrate-self-referential entity-type gazetteer features -- CPU.

ROUTING: Research Request-1 last substrate-only NER path (rule 8 us-or-substrate: substrate concept partition IS its own gazetteer).
  Research hand-authored 8 entity-type lexicon atoms (data/substrate_index/concept_corpus_ner_gazetteer_atoms.jsonl: PERSON/ORG/
  GPE/MONEY/DATE/TIME/PERCENT/QUANTITY, each a member surface-form list). Gazetteer features differ from clusters/POS: they
  generalize to UNSEEN entity surfaces via the curated list (helps test-set OOV). Add per-token gazetteer-hit features (+prev/next)
  to the structured-perceptron NER. A/B: baseline vs +gazetteer. OntoNotes 18-type. Substrate-only.
DECISION TREE (Research): gaz <0.62 -> ACCEPT boundary (promote CoNLL-equivalent 0.648 as PRIMARY); gaz >=0.65 -> keep pushing.
PRE-REGISTERED (NO defeat): report +gaz F1 + lift vs 0.5817 baseline. HARD-PASS F1 >= 0.65 (gazetteer breaks past detection ceiling;
  more headroom). MIDDLE F1 0.60-0.65 OR lift >= 0.02. HARD-FAIL lift < 0.01 (gazetteer saturates like other features). UNKNOWN if load fails.
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
from typing import Dict, Tuple, Set
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_gazetteer_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
F1_BASELINE = 0.5817
GAZ_EXACT: Dict[str, Set[str]] = {}   # type -> set of exact-surface members
GAZ_LOWER: Dict[str, Set[str]] = {}   # type -> set of lowercased members
GAZ_TYPES = []


def load_gazetteers():
    global GAZ_TYPES
    fp = REPO / "data" / "substrate_index" / "concept_corpus_ner_gazetteer_atoms.jsonl"
    if not fp.exists(): return False
    for line in open(fp, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        a = json.loads(line); t = a["id"].replace("LEX_entity_", "").upper(); mem = a.get("members", [])
        GAZ_EXACT[t] = set(mem); GAZ_LOWER[t] = set(m.lower() for m in mem)
    GAZ_TYPES = sorted(GAZ_EXACT.keys())
    return len(GAZ_TYPES) > 0


def _gazhits(tok):
    """set of gazetteer types this token matches (exact surface OR lowercased)."""
    hits = []
    wl = tok.lower()
    for t in GAZ_TYPES:
        if tok in GAZ_EXACT[t] or wl in GAZ_LOWER[t]: hits.append(t)
    return hits


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag, use_gaz):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_gaz:
        for t in _gazhits(w): fs.append("gaz_%s~%d" % (t, tag))
        if i > 0:
            for t in _gazhits(words[i - 1]): fs.append("pgaz_%s~%d" % (t, tag))
        if i + 1 < len(words):
            for t in _gazhits(words[i + 1]): fs.append("ngaz_%s~%d" % (t, tag))
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
    assert _spans([0, 1, 2, 0]) == {(1, 3, 0)} and _shape("Bob") == "Cap"
    print("[selftest] PASS: ner-gazetteer-substrate", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _train_eval(train, test, TAGS, use_gaz, seed):
    T = len(TAGS); rng = np.random.default_rng(seed)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(p, t): return "tt_%d~%d" % (p, t)

    def vit(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k], use_gaz)) for k in range(T)] for i in range(n)])
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
                        for f in _emit(words, i, gold[i], use_gaz): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i], use_gaz): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    tp = fp = fn = 0
    for words, gold in test:
        pred = vit(words, avg); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    return f1, prec, rec


def run() -> Dict:
    if not load_gazetteers():
        print("[gaz] atoms file missing", flush=True); return {"error": "gazetteer_atoms_missing", "f1": 0.0}
    print("  [gaz] %d entity-type gazetteers: %s" % (len(GAZ_TYPES), ",".join(GAZ_TYPES)), flush=True)
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "f1": 0.0}
    train = [(t, g) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, g) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    TAGS = sorted({t for _w, g in train for t in g}); seed = int(os.environ.get("HDLAB_SEED", "1028"))
    # coverage diagnostic
    hit_tokens = sum(1 for _t, _g in test for wtok in _t if _gazhits(wtok)); tot_tokens = sum(len(_t) for _t, _g in test)
    print("  [gaz] test token gazetteer-hit rate = %.3f (%d/%d)" % (hit_tokens / max(1, tot_tokens), hit_tokens, tot_tokens), flush=True)
    fb, pb, rb = _train_eval(train, test, TAGS, use_gaz=False, seed=seed)
    print("  [baseline]    F1=%.4f (P=%.3f R=%.3f)" % (fb, pb, rb), flush=True)
    fg, pg, rg = _train_eval(train, test, TAGS, use_gaz=True, seed=seed)
    print("  [+gazetteer]  F1=%.4f (P=%.3f R=%.3f)" % (fg, pg, rg), flush=True)
    lift = fg - fb
    print("  GAZETTEER LIFT = %+.4f | vs reference 0.5817 | train=%d test=%d" % (lift, len(train), len(test)), flush=True)
    return {"f1": round(fg, 4), "f1_gaz": round(fg, 4), "f1_baseline": round(fb, 4), "lift": round(lift, 4),
            "prec": round(pg, 3), "rec": round(rg, 3), "n_train": len(train), "gaz_hit_rate": round(hit_tokens / max(1, tot_tokens), 4)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    fg = r["f1_gaz"]; fb = r["f1_baseline"]; lift = r["lift"]
    s = "+gaz F1=%.4f vs baseline %.4f (lift=%+.4f, P=%.3f R=%.3f, gaz-hit-rate=%.3f, train=%d)" % (fg, fb, lift, r["prec"], r["rec"], r["gaz_hit_rate"], r["n_train"])
    if fg >= 0.65:
        return ("HARD_PASS", "HARD_PASS: substrate-self-referential gazetteer breaks NER past 0.65 detection ceiling -- substrate has more headroom; keep pushing (Research decision tree). " + s)
    if fg >= 0.60 or lift >= 0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: gazetteer lifts NER (F1>=0.60 or lift>=0.02) -- substrate-self-referential lexicon helps but does not break ceiling; stacks with clusters/POS. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gazetteer lift <0.02 and F1<0.60 -- substrate-self-referential gazetteer SATURATES like other in-corpus features (lexical surfaces already learned at scale). ACCEPT boundary; promote CoNLL-equivalent 0.648 as PRIMARY NER claim. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
