"""
exp_ner_transition_charngram_noise_crosscut_cpu_v1.py -- Compound A+B: transition-contribution & char-n-gram UNDER char-noise -- CPU.

ROUTING: strategy_request_to_exp_dev_2026-06-12_LB_complete_three_shape_typology (Cycle 243 v578). Substrate-quality-first; NO LLM frame.
  Research-invited compound cross-cut extending the L-B three-shape typology into the noisy-text regime, sharing the L-A/Ablation-3
  char-noise harness.

  Compound A (the valuable one): does the PP-404 BIO-transition contribution (+0.09 scale-invariant clean) PRESERVE or GROW under
    char-level test noise? Mechanism: BIO label legality (B before I, type consistency) is invariant under emission-level char noise,
    so the sequence model should be MORE noise-robust than surface lexical/affix features. If transition-contribution holds up under
    noise while the gazetteer lift shrinks (PP-403 RESCUE-1 cross-cut), then "the sequence model is BOTH the scale-invariant lever AND
    the noise-robustness lever; discrete features are neither."
  Compound B: does the PP-405 char-n-gram lift (~0 clean, subsumed) go MORE negative under noise (subsumed-clean -> harmful-under-noise)?
    5-gram membership is high-precision/low-recall and noise-sensitive.

DESIGN: variants {baseline, no_transition, char_ngram} x noise {clean, 10pct} x frac {5pct, 100pct}, 3 seeds. EFFICIENT: train ONCE
  per (variant, frac, seed) on CLEAN text, then evaluate the SAME model at both noise levels (training is the cost; noise is test-time
  only). Fixed noise realization per (frac,seed) so variants are paired. 4-type CoNLL collapse.

PRE-REGISTERED (substrate-property; no LLM frame):
  - Compound A headline: trans_contrib@5pct_noisy - trans_contrib@5pct_clean. HARD-PASS >= -0.01 (transition contribution PRESERVED or
    GROWS under noise -> sequence model is the noise-robustness lever). MIDDLE in [-0.03, -0.01). HARD-FAIL < -0.03 (transitions degrade
    like lexical features).
  - Compound B (annotation): char-n-gram lift clean vs noisy; expect noisy <= clean (more harmful under noise). Reported, not gated.
  UNKNOWN if data load fails.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via local_cpu_queue (dashboard-visible).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "ner_transition_charngram_noise_crosscut_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NOISE = 0.10
FRACS = [0.05, 1.0]
SEEDS = [1028, 1029, 1030]
VARIANTS = ["baseline", "no_transition", "char_ngram"]
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}


def _collapse4(tags):
    out = []
    for t in tags:
        if t == 0: out.append(0); continue
        tid = (t - 1) // 2; is_B = (t % 2 == 1)
        cz = COARSE.get(tid)
        out.append(0 if cz is None else ((1 + 2 * cz) if is_B else (2 + 2 * cz)))
    return out


def _shape(w):
    if w.isdigit(): return "DIG"
    if w[:1].isupper() and w[1:].islower(): return "Cap"
    if w.isupper(): return "UPP"
    if any(c.isdigit() for c in w): return "alnum"
    if "-" in w: return "HYP"
    return "low"


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


def _char_perturb(word, rate, rng):
    if rate <= 0 or len(word) < 2 or not word.isalpha():
        return word
    out = []
    for ch in word:
        if rng.random() < rate:
            op = rng.integers(0, 3)
            if op == 0: out.append(chr(int(rng.integers(97, 123))))
            elif op == 1: out.append(ch); out.append(chr(int(rng.integers(97, 123))))
        else:
            out.append(ch)
    return "".join(out) or word


def _char_ngrams(wl: str, n: int):
    if len(wl) < n: return []
    pad = "^" + wl + "$"
    return [pad[i:i + n] for i in range(len(pad) - n + 1)]


def _emit_feats(words, i, tag, use_char):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_char:
        for g in _char_ngrams(wl, 3): fs.append("c3_%s~%d" % (g, tag))
        for g in _char_ngrams(wl, 5): fs.append("c5_%s~%d" % (g, tag))
    return fs


def _train_model(train, variant, seed):
    """Train once on CLEAN text; return (avg_weights, TAGS, use_char, use_trans)."""
    use_char = (variant == "char_ngram"); use_trans = (variant != "no_transition")
    rng = np.random.default_rng(seed)
    TAGS = sorted({tg for _w, g in train for tg in g}); T = len(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], use_char)) for k in range(T)] for i in range(n)])
        if not use_trans:
            return [TAGS[int(np.argmax(em[i]))] for i in range(n)]
        TM = np.array([[weights.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([weights.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    EP = 6 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            words, gold = train[si]; pred = viterbi(words, w)
            if pred != gold:
                pg = -1; pp = -1
                for i in range(len(words)):
                    if pred[i] != gold[i] or i == 0 or pred[i - 1] != gold[i - 1]:
                        for f in _emit_feats(words, i, gold[i], use_char): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i], use_char): w[f] -= 1; cw[f] -= c
                    if use_trans:
                        w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                        w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    return avg, TAGS, use_char, use_trans


def _eval(avg, TAGS, use_char, use_trans, test, noise) -> float:
    T = len(TAGS)

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words):
        n = len(words)
        em = np.array([[sum(avg.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], use_char)) for k in range(T)] for i in range(n)])
        if not use_trans:
            return [TAGS[int(np.argmax(em[i]))] for i in range(n)]
        TM = np.array([[avg.get(tt(TAGS[j], TAGS[k]), 0.0) for k in range(T)] for j in range(T)])
        SV = np.array([avg.get(tt(-1, TAGS[k]), 0.0) for k in range(T)])
        V = np.empty((n, T)); bp = np.zeros((n, T), dtype=int); V[0] = em[0] + SV
        for i in range(1, n):
            cand = V[i - 1][:, None] + TM; bp[i] = np.argmax(cand, axis=0); V[i] = cand[bp[i], np.arange(T)] + em[i]
        seq = [int(np.argmax(V[n - 1]))]
        for i in range(n - 1, 0, -1): seq.append(int(bp[i][seq[-1]]))
        seq.reverse(); return [TAGS[k] for k in seq]

    nrng = np.random.default_rng(7)  # fixed noise realization (paired across variants)
    tp = fp = fn = 0
    for words, gold in test:
        tw = [_char_perturb(x, noise, nrng) for x in words] if noise > 0 else words
        pred = viterbi(tw); gs = _spans(gold); ps = _spans(pred)
        tp += len(gs & ps); fp += len(ps - gs); fn += len(gs - ps)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9)
    return 2 * prec * rec / (prec + rec + 1e-9)


def _subset(train, frac, seed):
    if frac >= 1.0: return train
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(train))[:max(5, int(len(train) * frac))]
    return [train[i] for i in idx]


def run() -> Dict:
    try:
        data = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed"}
    train = [(t, _collapse4(g)) for t, g in data["train"] if t and len(t) <= 60]
    test = [(t, _collapse4(g)) for t, g in data["test"] if t and len(t) <= 60]
    if SMOKE: train = train[:300]; test = test[:150]
    fracs = [0.05] if SMOKE else FRACS
    seeds = SEEDS[:1] if SMOKE else SEEDS
    variants = ["baseline", "no_transition", "char_ngram"]
    noises = [0.0, NOISE]
    # acc[frac][noise][variant] = list of F1 over seeds
    acc = {fr: {nz: {v: [] for v in variants} for nz in noises} for fr in fracs}
    for fr in fracs:
        for s in seeds:
            sub = _subset(train, fr, s)
            for v in variants:
                avg, TAGS, uc, ut = _train_model(sub, v, s)
                for nz in noises:
                    acc[fr][nz][v].append(_eval(avg, TAGS, uc, ut, test, nz))
    rows = []
    for fr in fracs:
        row = {"frac": fr}
        for nz in noises:
            mean = {v: round(sum(acc[fr][nz][v]) / len(acc[fr][nz][v]), 4) for v in variants}
            tc = round(mean["baseline"] - mean["no_transition"], 4)   # transition contribution
            cl = round(mean["char_ngram"] - mean["baseline"], 4)      # char n-gram lift
            row["noise%d" % int(100 * nz)] = {"means": mean, "trans_contrib": tc, "char_lift": cl}
        rows.append(row)
        c0 = row["noise0"]; cN = row["noise%d" % int(100 * NOISE)]
        print("  frac=%4.0f%% | CLEAN trans=%+.4f char=%+.4f | NOISY trans=%+.4f char=%+.4f | d_trans=%+.4f d_char=%+.4f"
              % (100 * fr, c0["trans_contrib"], c0["char_lift"], cN["trans_contrib"], cN["char_lift"],
                 cN["trans_contrib"] - c0["trans_contrib"], cN["char_lift"] - c0["char_lift"]), flush=True)
    return {"rows": rows, "noise_level": NOISE}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    nk = "noise%d" % int(100 * r["noise_level"])
    r5 = next((x for x in r["rows"] if x["frac"] == 0.05), None)
    if not r5: return ("UNKNOWN", "UNKNOWN: missing 5pct row")
    tc_clean = r5["noise0"]["trans_contrib"]; tc_noisy = r5[nk]["trans_contrib"]
    cl_clean = r5["noise0"]["char_lift"]; cl_noisy = r5[nk]["char_lift"]
    d_trans = round(tc_noisy - tc_clean, 4); d_char = round(cl_noisy - cl_clean, 4)
    s = ("Compound A: transition-contribution@5pct clean=%+.4f noisy=%+.4f (delta=%+.4f). Compound B: char-n-gram lift@5pct clean=%+.4f noisy=%+.4f (delta=%+.4f)"
         % (tc_clean, tc_noisy, d_trans, cl_clean, cl_noisy, d_char))
    if d_trans >= -0.01:
        return ("HARD_PASS", "HARD_PASS: BIO-transition contribution PRESERVED/GROWS under char noise (delta>=-0.01) -- the sequence model is the noise-robustness lever (BIO label legality is invariant to emission-level char noise), compounding with its scale-invariance. Discrete features (gazetteer) shrink under noise; the sequence model does not. " + s)
    if d_trans >= -0.03:
        return ("MIDDLE_BAND", "MIDDLE_BAND: transition contribution mildly degrades under noise (delta in [-0.03,-0.01)) -- partially noise-robust. " + s)
    return ("HARD_FAIL", "HARD_FAIL: transition contribution degrades under noise (delta<-0.03) -- sequence model not meaningfully more noise-robust than lexical features. " + s)


def _selftest():
    assert _collapse4([1, 2, 0, 15]) == [1, 2, 0, 0]
    assert _char_ngrams("cat", 3) == ["^ca", "cat", "at$"]
    rng = np.random.default_rng(1)
    assert _char_perturb("Paris", 0.0, rng) == "Paris"
    fb = _emit_feats(["Cats"], 0, 1, False); fc = _emit_feats(["Cats"], 0, 1, True)
    assert not any(x.startswith("c3_") for x in fb) and any(x.startswith("c3_") for x in fc)
    print("[selftest] PASS: ner-transition-charngram-noise-crosscut", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s noise=%.0f%%" % (ANCHOR_NAME, RUN_MODE, 100 * NOISE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
