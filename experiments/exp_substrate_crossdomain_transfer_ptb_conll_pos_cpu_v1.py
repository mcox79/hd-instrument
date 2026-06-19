"""
exp_substrate_crossdomain_transfer_ptb_conll_pos_cpu_v1.py -- 3rd-appearance: cross-domain POS transfer (PTB -> CoNLL-2003) -- CPU.

ROUTING: 3rd-appearance candidate for meta::RULE_cross_domain_transfer_tail_shape_is_capability_class_dependent (open-vocab
  persists / closed-feature converges). Substrate-quality-first; NO LLM frame. Anchors so far: sentiment (closed, converges) +
  topic (closed, converges) + NER (open-vocab, non-converging tail). POS tagging is OPEN-VOCABULARY sequence labeling ->
  predicted NON-CONVERGING tail (like NER): the source corpus supplies POS knowledge for words the target's limited train lacks,
  even at 100pct target data.

  Train the discriminative_perceptron (structured perceptron + Viterbi) POS tagger on PTB (WSJ, source), WARM-START transfer to
  CoNLL-2003 POS (Reuters news, target) vs train-from-scratch, at target fractions {1,2.5,5,10,100}pct, 3 seeds. Both use the
  Penn Treebank POS tagset (aligned -> shared tag space for warm-start). Token-level POS ACCURACY (standard POS metric).

  DATA: PTB bundled (ptb_treebank_tagged.json). CoNLL-2003 column-2 POS via raw GitHub mirror (env-gated -> UNKNOWN).

PRE-REGISTERED (3rd appearance; the discriminator is the TAIL at 100pct):
  HARD-PASS: ratio@100pct >= 1.02 (open-vocab tail PERSISTS, consistent with NER; confirms the rule) AND ratio@2.5pct >= 1.02
    (low-data lift present). MIDDLE: ratio@100pct in [0.99,1.02] (ambiguous tail). HARD-FAIL: ratio@100pct < 0.99 (POS converges
    like a closed-feature task -> rule needs refinement: maybe tagset-closedness matters, not just open-vocab). UNKNOWN if CoNLL fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop; laptop paused).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, urllib.request
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_crossdomain_transfer_ptb_conll_pos_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
CONLL_URL = "https://raw.githubusercontent.com/synalp/NER/master/corpus/CoNLL-2003/eng.train"
FRACS = [0.01, 0.025, 0.05, 0.10, 1.0]
SEEDS = [7, 8, 9]
SRC_CAP = 2500; TGT_TRAIN_CAP = 2500; TGT_TEST_CAP = 1000


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
    fs.append("pw_%s~%s" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%s" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    return fs


def _viterbi(words, weights, TAGS):
    T = len(TAGS); n = len(words)
    def tt(pt, t): return "tt_%s~%s" % (pt, t)
    em = np.array([[sum(weights.get(f, 0.0) for f in _emit(words, i, TAGS[k])) for k in range(T)] for i in range(n)])
    TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
    SV = np.array([weights.get(tt("<S>", TAGS[k]), 0.0) for k in range(T)])
    V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
    for i in range(1, n):
        cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
    seq = [int(np.argmax(V[n - 1]))]
    for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
    seq.reverse(); return [TAGS[k] for k in seq]


def _train(data, TAGS, epochs, w0, seed):
    rng = np.random.default_rng(seed); w = defaultdict(float)
    if w0:
        for k, v in w0.items(): w[k] = v
    cw = defaultdict(float); c = 1
    def tt(pt, t): return "tt_%s~%s" % (pt, t)
    for _ in range(epochs):
        for si in rng.permutation(len(data)):
            words, gold = data[si]; pred = _viterbi(words, w, TAGS)
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
    return {f: w[f] - cw[f] / c for f in w}


def _acc(data, w, TAGS):
    corr = tot = 0
    for words, gold in data:
        pred = _viterbi(words, w, TAGS)
        for p, g in zip(pred, gold):
            corr += int(p == g); tot += 1
    return corr / tot if tot else 0.0


def _load_ptb():
    d = json.load(open(REPO / "experiments" / "data" / "ptb_treebank_tagged.json", encoding="utf-8"))
    return [([t[0] for t in s], [t[1] for t in s]) for s in d if s and len(s) <= 60]


def _load_conll_pos():
    try:
        with urllib.request.urlopen(CONLL_URL, timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:
        print("[conll] download fail %s" % str(e)[:90], flush=True); return None
    sents = []; toks = []; tags = []
    for ln in txt.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("-DOCSTART-"):
            if toks: sents.append((toks, tags)); toks = []; tags = []
            continue
        p = ln.split()
        if len(p) >= 2: toks.append(p[0]); tags.append(p[1])
    if toks: sents.append((toks, tags))
    return [(t, g) for t, g in sents if t and len(t) <= 60]


def run() -> Dict:
    src = _load_ptb()
    tgt = _load_conll_pos()
    if tgt is None:
        return {"error": "conll_download_failed_env_gated", "note": "needs raw CoNLL-2003 mirror; harness correct + ready"}
    rng0 = np.random.default_rng(0)
    src = [src[i] for i in rng0.permutation(len(src))[:(250 if SMOKE else SRC_CAP)]]
    tgt_all = [tgt[i] for i in rng0.permutation(len(tgt))]
    tgt_te = tgt_all[:(150 if SMOKE else TGT_TEST_CAP)]
    tgt_tr_pool = tgt_all[(150 if SMOKE else TGT_TEST_CAP):(150 if SMOKE else TGT_TEST_CAP) + (300 if SMOKE else TGT_TRAIN_CAP)]
    TAGS = sorted({t for _w, g in (src + tgt_tr_pool + tgt_te) for t in g})
    ep = 3 if SMOKE else 5
    w_src = _train(src, TAGS, ep, None, 123)
    f_src_only = _acc(tgt_te, w_src, TAGS)
    print("  [src] PTB POS model zero-shot on CoNLL POS acc=%.4f (src=%d, tags=%d)" % (f_src_only, len(src), len(TAGS)), flush=True)
    fracs = [0.025] if SMOKE else FRACS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    curve = []
    for fr in fracs:
        sc = []; tf = []
        for sd in seeds:
            rng = np.random.default_rng(sd)
            n = max(5, int(len(tgt_tr_pool) * fr)); sub = [tgt_tr_pool[i] for i in rng.permutation(len(tgt_tr_pool))[:n]]
            sc.append(_acc(tgt_te, _train(sub, TAGS, ep, None, sd), TAGS))
            tf.append(_acc(tgt_te, _train(sub, TAGS, ep, w_src, sd), TAGS))
        scm = sum(sc) / len(sc); tfm = sum(tf) / len(tf)
        curve.append({"frac": fr, "scratch_acc": round(scm, 4), "transfer_acc": round(tfm, 4), "ratio": round(tfm / (scm + 1e-9), 4)})
        print("  frac=%5.1f%% scratch=%.4f transfer=%.4f ratio=%.4f" % (100 * fr, scm, tfm, curve[-1]["ratio"]), flush=True)
    return {"curve": curve, "src_only_acc": round(f_src_only, 4), "n_tags": len(TAGS), "n_tgt_test": len(tgt_te)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("conll"):
        return ("UNKNOWN", "UNKNOWN: CoNLL-2003 download unavailable (env-gated). Harness correct + ready. " + r.get("note", ""))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {c["frac"]: c for c in r["curve"]}
    r25 = by.get(0.025, {}).get("ratio"); r100 = by.get(1.0, {}).get("ratio")
    s = ("ratio@2.5pct=%s ratio@100pct=%s (TAIL discriminator); zero-shot PTB-on-CoNLL acc=%s; curve=%s" %
         (r25, r100, r.get("src_only_acc"), [(c["frac"], c["scratch_acc"], c["transfer_acc"], c["ratio"]) for c in r["curve"]]))
    if r100 is None or r25 is None:
        return ("UNKNOWN", "UNKNOWN: missing fraction. " + s)
    if r100 >= 1.02 and r25 >= 1.02:
        return ("HARD_PASS", "HARD_PASS: POS cross-domain transfer keeps a NON-CONVERGING TAIL (ratio@100pct>=1.02) -- open-vocab sequence labeling persists like NER. 3rd appearance CONFIRMS the capability-class tail-shape rule (open-vocab persists). " + s)
    if r100 >= 0.99:
        return ("MIDDLE_BAND", "MIDDLE_BAND: POS tail ambiguous (ratio@100pct in [0.99,1.02]) -- weak/no persistent tail; open-vocab prediction not cleanly confirmed for POS. " + s)
    return ("HARD_FAIL", "HARD_FAIL: POS converges (ratio@100pct<0.99) like a closed-feature task -- refutes the open-vocab-persists prediction for POS; rule may need refinement (closed TAGSET may matter, not just open vocabulary). " + s)


def _selftest():
    TAGS = ["NN", "VB"]
    data = [(["dogs", "run"], ["NN", "VB"]), (["cats", "jump"], ["NN", "VB"])] * 10
    w = _train(data, TAGS, 4, None, 0); assert _acc(data, w, TAGS) > 0.9
    assert _shape("Dog") == "Cap" and _shape("RUN") == "UPP"
    print("[selftest] PASS: crossdomain-ptb-conll-pos (acc=%.3f)" % _acc(data, w, TAGS), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
