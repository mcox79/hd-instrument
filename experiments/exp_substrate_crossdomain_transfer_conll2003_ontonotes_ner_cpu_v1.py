"""
exp_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1.py -- RESCUE-3: cross-domain NER transfer (CoNLL-2003 -> OntoNotes) -- CPU.

ROUTING: strategy_request RESCUE-3 (2nd-appearance hook for meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever).
  Substrate-quality-first; NO LLM frame. PP-409 (SST-2->IMDB sentiment) was the 1st appearance; this is a NON-SENTIMENT
  (sequence-labeling NER) 2nd appearance. Train the discriminative_perceptron (structured perceptron + Viterbi) NER tagger on
  CoNLL-2003 (Reuters news, source domain), WARM-START transfer to OntoNotes NER (mixed-genre, target) vs train-from-scratch,
  at target fractions {1,2.5,5,10,100}pct. Both collapsed to the SAME 4-type CoNLL scheme (PER/ORG/LOC/MISC) so the feature +
  tag spaces align for warm-start.

  DATA: CoNLL-2003 via raw GitHub mirror (synalp/NER eng.train; env-gated -> UNKNOWN if download fails). OntoNotes bundled
  (experiments/data/ontonotes_ner.json, integer conll2012 tags -> 4-type collapse).

PRE-REGISTERED (RESCUE-1 methodology fix: steepest slope 1-5pct): transfer F1 / scratch F1 at 2.5pct OntoNotes data:
  HARD-PASS ratio@2.5pct >= 1.20 (positive cross-domain transfer; discriminative lever generalizes NER across domain).
  MIDDLE 0.95-1.20. HARD-FAIL < 0.95 (negative transfer). UNKNOWN if CoNLL-2003 download fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, urllib.request
from pathlib import Path
from typing import Dict, Tuple, List
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
CONLL_URL = "https://raw.githubusercontent.com/synalp/NER/master/corpus/CoNLL-2003/eng.train"
FRACS = [0.01, 0.025, 0.05, 0.10, 1.0]
SEEDS = [7, 8, 9]
SRC_CAP = 3000
TGT_TRAIN_CAP = 3000
TGT_TEST_CAP = 1000
# CoNLL-2003 IOB1 NER label -> 4-type coarse id (0=PER,1=ORG,2=LOC,3=MISC) ; matches OntoNotes _collapse4 output scheme.
_CONLL_COARSE = {"PER": 0, "ORG": 1, "LOC": 2, "MISC": 3}
# OntoNotes type_id -> coarse (same as exp_ner_4type_conll)
_ON_COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}


def _on_collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; isB = (t % 2 == 1); cz = _ON_COARSE.get(tid)
        out.append(0 if cz is None else ((1 + 2 * cz) if isB else (2 + 2 * cz)))
    return out


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


def _emit(words, i, tag):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
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


# fixed 9-tag space (0=O + B/I for 4 coarse types) so source+target share the tag set for warm-start
TAGS = [0, 1, 2, 3, 4, 5, 6, 7, 8]; T = len(TAGS)


def _tt(pt, t): return "tt_%d~%d" % (pt, t)


def _viterbi(words, weights):
    n = len(words)
    em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
    TM = np.array([[weights.get(_tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
    SV = np.array([weights.get(_tt(-1, TAGS[k]), 0.0) for k in range(T)])
    V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
    for i in range(1, n):
        cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
    seq = [int(np.argmax(V[n - 1]))]
    for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
    seq.reverse(); return [TAGS[k] for k in seq]


def _train(data, epochs, w0, seed):
    rng = np.random.default_rng(seed)
    w = defaultdict(float)
    if w0:
        for k, v in w0.items(): w[k] = v
    cw = defaultdict(float); c = 1
    for ep in range(epochs):
        for si in rng.permutation(len(data)):
            words, gold = data[si]; pred = _viterbi(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit(words, i, gold[i]): w[f] += 1; cw[f] += c
                        for f in _emit(words, i, pred[i]): w[f] -= 1; cw[f] -= c
                    w[_tt(pg, gold[i])] += 1; cw[_tt(pg, gold[i])] += c
                    w[_tt(pp, pred[i])] -= 1; cw[_tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    return {f: w[f] - cw[f] / c for f in w}


def _f1(data, w):
    tp = fp = fn = 0
    for words, gold in data:
        ps = _spans(_viterbi(words, w)); gs = _spans(gold)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9); return 2 * p * r / (p + r + 1e-9)


def _load_conll():
    try:
        with urllib.request.urlopen(CONLL_URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("[conll] download fail %s" % str(e)[:100], flush=True); return None
    sents = []; toks = []; tags = []; prev = None
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("-DOCSTART-"):
            if toks: sents.append((toks, tags)); toks = []; tags = []; prev = None
            continue
        parts = ln.split()
        if len(parts) < 4: continue
        word = parts[0]; ner = parts[-1]
        if ner == "O" or "-" not in ner:
            tags.append(0); prev = None
        else:
            typ = ner.split("-", 1)[1]; cz = _CONLL_COARSE.get(typ)
            if cz is None: tags.append(0); prev = None
            else:
                isB = (prev != cz)  # IOB1->BIO: start when type changes from prev token
                tags.append((1 + 2 * cz) if isB else (2 + 2 * cz)); prev = cz
        toks.append(word)
    if toks: sents.append((toks, tags))
    return [(t, g) for t, g in sents if t and len(t) <= 60]


def run() -> Dict:
    src = _load_conll()
    if src is None:
        return {"error": "conll2003_download_failed_env_gated", "note": "needs raw CoNLL-2003 mirror; harness correct + ready"}
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        return {"error": "ontonotes_load_failed: " + str(e)[:80]}
    tgt_tr = [(t, _on_collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    tgt_te = [(t, _on_collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    rng0 = np.random.default_rng(0)
    src = [src[i] for i in rng0.permutation(len(src))[:(300 if SMOKE else SRC_CAP)]]
    tgt_tr = [tgt_tr[i] for i in rng0.permutation(len(tgt_tr))[:(400 if SMOKE else TGT_TRAIN_CAP)]]
    tgt_te = [tgt_te[i] for i in rng0.permutation(len(tgt_te))[:(150 if SMOKE else TGT_TEST_CAP)]]
    ep = 3 if SMOKE else 6
    w_src = _train(src, ep, None, 123)
    f_src_only = _f1(tgt_te, w_src)
    print("  [src] CoNLL-2003 model zero-shot on OntoNotes F1=%.4f (src=%d sents)" % (f_src_only, len(src)), flush=True)
    fracs = [0.025] if SMOKE else FRACS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    curve = []
    for fr in fracs:
        sc = []; tf = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            n = max(5, int(len(tgt_tr) * fr)); sub = [tgt_tr[i] for i in rng.permutation(len(tgt_tr))[:n]]
            f_sc = _f1(tgt_te, _train(sub, ep, None, sd))
            f_tf = _f1(tgt_te, _train(sub, ep, w_src, sd))
            sc.append(f_sc); tf.append(f_tf)
        scm = sum(sc) / len(sc); tfm = sum(tf) / len(tf); ratio = tfm / (scm + 1e-9)
        curve.append({"frac": fr, "scratch_f1": round(scm, 4), "transfer_f1": round(tfm, 4), "ratio": round(ratio, 4)})
        print("  frac=%5.1f%% scratch=%.4f transfer=%.4f ratio=%.4f" % (100 * fr, scm, tfm, ratio), flush=True)
    return {"curve": curve, "src_only_f1": round(f_src_only, 4), "n_src": len(src), "n_tgt_test": len(tgt_te)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("conll2003_download"):
        return ("UNKNOWN", "UNKNOWN: CoNLL-2003 download unavailable (env-gated). Harness correct + ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["frac"]: c for c in r["curve"]}
    r25 = by.get(0.025, {})
    ratio = r25.get("ratio")
    s = ("ratio@2.5pct=%s (transfer %.4f / scratch %.4f); zero-shot CoNLL-on-OntoNotes F1=%s; curve=%s" %
         (ratio, r25.get("transfer_f1", 0.0), r25.get("scratch_f1", 0.0), r.get("src_only_f1"),
          [(c["frac"], c["scratch_f1"], c["transfer_f1"], c["ratio"]) for c in r["curve"]]))
    if ratio is None:
        return ("UNKNOWN", "UNKNOWN: 2.5pct fraction missing. " + s)
    if ratio >= 1.20:
        return ("HARD_PASS", "HARD_PASS: positive cross-domain NER transfer -- CoNLL-2003-pretrained discriminative_perceptron lifts OntoNotes F1 by >=20pct at 2.5pct data. 2nd-appearance (non-sentiment) for the cross-domain discriminative-weighting lever. " + s)
    if ratio >= 0.95:
        return ("MIDDLE_BAND", "MIDDLE_BAND: neutral/weak cross-domain NER transfer (ratio 0.95-1.20 at 2.5pct). " + s)
    return ("HARD_FAIL", "HARD_FAIL: negative cross-domain NER transfer (ratio <0.95 at 2.5pct). " + s)


def _selftest():
    assert _on_collapse4([1, 2, 0]) == [1, 2, 0]
    assert _spans([1, 2, 0]) == {(0, 2, 0)}
    # IOB1->BIO conversion sanity on a tiny CoNLL-like fragment handled in _load_conll; check coarse map
    assert _CONLL_COARSE["ORG"] == 1 and _CONLL_COARSE["PER"] == 0
    print("[selftest] PASS: crossdomain-conll-ontonotes-ner", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
