"""
exp_pos_tagger_ptb_substrate_cpu_v1.py -- substrate-only POS tagger on Penn Treebank (LLM-boundary test) -- CPU.

ROUTING: Research WAVE2 / LLM-boundary 3x DEEP drill. The cheapest decisive test of "substrate can do NL" -- if a substrate-only
  tagger matches the classical-era SOTA (Brill 1995 = 96.7%) the "LLM-only-for-NL-parse" claim is refuted. Substrate-native:
  Tier-1 = POS tags as phasor atoms; Tier-3 = per-word lexicon vectors (freq-weighted bundle of tag phasors); tag = cleanup
  of a word's lexicon vector over the Tier-1 tag atoms (substrate associative recall). OOV words backed off via suffix-feature
  lexicon (PP-342 wug-mechanism). DATA NOTE: uses the NLTK Penn Treebank SAMPLE (~3914 WSJ sentences) with a train/test split
  by sentence order (mimicking sec02-21 train / sec24 test) -- the full LDC WSJ sections are licensed and not freely available;
  this is the honest accessible PTB-derived substitute. Substrate-only, pure-numpy + nltk. N=4096.
PRE-REGISTERED: HARD-PASS tag-accuracy >= 0.90 (Brill 1995 = 96.7%). HARD-PASS-STRONG >= 0.95. MIDDLE >= 0.80. HARD-FAIL < 0.80.
  UNKNOWN if corpus download fails.
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
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "pos_tagger_ptb_substrate_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 4096
def cphasor(m, d, g):
    ang = (g.random((m, d)) * 2 - 1) * math.pi; return np.exp(1j * ang).astype(np.complex64)
def cnorm(v):
    return np.exp(1j * np.angle(v)).astype(np.complex64)
def _selftest():
    g = np.random.default_rng(0); book = cphasor(3, N, g)
    v = cnorm(book[1] * 2 + book[0]); assert int(np.argmax((book @ np.conj(v)).real)) == 1, "cleanup"
    print("[selftest] PASS: pos-tagger-ptb-substrate", flush=True)
def _load():
    try:
        import nltk
        try:
            nltk.data.find("corpora/treebank")
        except LookupError:
            nltk.download("treebank", quiet=True)
        from nltk.corpus import treebank
        return [s for s in treebank.tagged_sents() if s]
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return None
def run() -> Dict:
    g = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "970")))
    sents = _load()
    if not sents:
        return {"error": "corpus_load_failed", "tag_acc": 0.0}
    if SMOKE:
        sents = sents[:400]
    nsp = int(0.8 * len(sents)); train, test = sents[:nsp], sents[nsp:]
    tags = sorted({t for s in train for (_w, t) in s}); ti = {t: i for i, t in enumerate(tags)}; T = len(tags)
    tag_book = cphasor(T, N, g)
    # Tier-3 word lexicon: freq-weighted bundle of tag phasors per word
    word_acc = defaultdict(lambda: np.zeros(N, dtype=np.complex64))
    feat_acc = defaultdict(lambda: np.zeros(N, dtype=np.complex64))   # morphological feature -> tag bundle (PP-342 wug)
    def _feats(w):
        wl = w.lower(); fs = []
        if any(c.isdigit() for c in w): fs.append("F:DIGIT")
        if w[:1].isupper(): fs.append("F:CAP")
        if "-" in w: fs.append("F:HYPHEN")
        for k in (2, 3, 4):
            if len(wl) >= k: fs.append("S%d:%s" % (k, wl[-k:]))   # multi-length suffix
        return fs
    for s in train:
        for (w, t) in s:
            wl = w.lower(); word_acc[wl] = word_acc[wl] + tag_book[ti[t]]
            for f in _feats(w): feat_acc[f] = feat_acc[f] + tag_book[ti[t]]
    lex = {w: cnorm(v) for w, v in word_acc.items()}
    feat = {f: cnorm(v) for f, v in feat_acc.items()}
    def predict(w):
        wl = w.lower()
        if wl in lex:
            v = lex[wl]
        else:                                                # OOV: combine morphological feature evidence
            acc = np.zeros(N, dtype=np.complex64); got = False
            for f in _feats(w):
                if f in feat: acc = acc + feat[f]; got = True
            if not got:
                return "NN"
            v = cnorm(acc)
        return tags[int(np.argmax((tag_book @ np.conj(v)).real))]
    hit = 0; tot = 0; oov = 0
    for s in test:
        for (w, t) in s:
            p = predict(w); hit += int(p == t); tot += 1; oov += int(w.lower() not in lex)
    acc = hit / tot if tot else 0.0
    print("  POS-TAGGER (substrate): tag-accuracy=%.4f (%d/%d tokens, %.1f%% OOV, %d tags, train=%d sents)" %
          (acc, hit, tot, 100 * oov / tot, T, len(train)), flush=True)
    return {"tag_acc": round(acc, 4), "n_tokens": tot, "oov_rate": round(oov / tot, 3), "n_tags": T, "n_train_sents": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    a = r["tag_acc"]; s = "tag-acc=%.4f (%d tokens, OOV=%.1f%%, %d tags)" % (a, r["n_tokens"], 100 * r["oov_rate"], r["n_tags"])
    if a >= 0.90:
        extra = " STRONG (matches/approaches Brill 1995 96.7%)" if a >= 0.95 else ""
        return ("HARD_PASS", "HARD_PASS: substrate-only POS tagger reaches tag-accuracy>=0.90%s -- a substrate associative lexicon + suffix backoff does PTB POS tagging without an LLM. The 'LLM-only-for-NL-parse' claim is empirically refuted at low cost. " % extra + s)
    if a >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: tag-accuracy 0.80-0.90 (substrate tags but below classical SOTA). " + s)
    return ("HARD_FAIL", "HARD_FAIL: tag-accuracy <0.80 -- substrate lexicon insufficient for POS tagging. " + s)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s N=%d" % (ANCHOR_NAME, RUN_MODE, N), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
