"""
exp_ner_feature_ablation_cpu_v1.py -- L-B mechanism deepening, Ablations 1+2: transition contribution + char n-gram -- CPU.

ROUTING: research_to_exp_dev_L_B_REROUTE...MECHANISM_DEEPENING (2026-06-12, substrate-quality-first; NO LLM frame).

HONEST CORRECTION to the routing premise: Research's Ablation 1 assumed "structured perceptron with memoryless emissions".
  The substrate NER harness (exp_ner_4type_conll_cpu_v1) is NOT memoryless -- it already has tag-bigram transition features
  tt(prev_tag, tag) decoded by full Viterbi. So the honest Ablation 1 is a TRANSITION-CONTRIBUTION ablation: measure what the
  existing BIO->BIO transition structure contributes (transitions ON = current Viterbi vs OFF = independent per-token argmax),
  especially at low data. Ablation 2 (char-CNN) substrate-classical analogue = discrete char n-gram (3/5) membership features.

  Variants (paired at each train fraction, same subset/seed):
    - baseline    : current emit-features + tt transitions + Viterbi
    - no_transition: emit-features only, transitions zeroed, independent argmax per token (memoryless)
    - char_ngram  : baseline + char 3-gram and 5-gram features inside each word (substrate-classical "char-CNN")
  4-type CoNLL collapse (comparable to L-B curve: 5pct=0.404, 10pct=0.501, 100pct=0.644).

PRE-REGISTERED (substrate-property; no LLM frame):
  - Transition contribution: HP if baseline - no_transition >= +0.05 at 5pct (transitions are a real low-data lever via BIO consistency).
  - Char n-gram: HP char_ngram F1 at 5pct >= 0.43 (+0.03 over baseline) AND lift@5pct > lift@100pct (low-data-win).
  - Headline verdict = char_ngram band (HARD-PASS >=0.43 with low-data-win; MIDDLE 0.40-0.43; HARD-FAIL <0.40). Transition
    contribution reported alongside. UNKNOWN if data load fails.
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
ANCHOR_NAME = "ner_feature_ablation_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
LB_BASELINE = {0.05: 0.404, 0.10: 0.501, 1.0: 0.644}
FRACS = [0.05, 0.10, 1.0]
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


def _train_eval(train, test, variant, seed) -> float:
    use_char = (variant == "char_ngram")
    use_trans = (variant != "no_transition")
    rng = np.random.default_rng(seed)
    TAGS = sorted({tg for _w, g in train for tg in g}); T = len(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], use_char)) for k in range(T)] for i in range(n)])
        if not use_trans:  # memoryless: independent argmax per token
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
    tp = fp = fn = 0
    for words, gold in test:
        pred = viterbi(words, avg); gs = _spans(gold); ps = _spans(pred)
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
    variants = ["baseline", "char_ngram"] if SMOKE else VARIANTS
    curve = []
    for fr in fracs:
        row = {"frac": fr, "n_train": len(_subset(train, fr, seeds[0])), "lb_ref": LB_BASELINE.get(fr)}
        for v in variants:
            f1s = [_train_eval(_subset(train, fr, s), test, v, s) for s in seeds]
            row[v] = round(sum(f1s) / len(f1s), 4)
        curve.append(row)
        bl = row.get("baseline", 0.0)
        print("  frac=%4.0f%% " % (100 * fr) + " ".join("%s=%.4f" % (v, row.get(v, 0.0)) for v in variants)
              + " | char_lift=%+.4f trans_contrib=%+.4f" % (row.get("char_ngram", bl) - bl, bl - row.get("no_transition", bl)), flush=True)
    return {"curve": curve, "variants": variants}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    by = {row["frac"]: row for row in r["curve"]}
    b5 = by.get(0.05, {}); b100 = by.get(1.0, {})
    cg5 = b5.get("char_ngram", 0.0); base5 = b5.get("baseline", 0.0)
    char_l5 = cg5 - base5; char_l100 = b100.get("char_ngram", 0.0) - b100.get("baseline", 0.0)
    trans5 = base5 - b5.get("no_transition", base5)
    char_shape = "low-data-win" if (1.0 in by and char_l5 > char_l100) else "flat/inverted"
    s = ("char_ngram F1@5pct=%.4f (lift %+.4f vs baseline %.4f; @100pct lift %+.4f -> %s); transition-contribution@5pct=%+.4f"
         % (cg5, char_l5, base5, char_l100, char_shape, trans5))
    if cg5 >= 0.43 and (1.0 not in by or char_l5 > char_l100):
        return ("HARD_PASS", "HARD_PASS: char n-gram features lift low-data NER to >=0.43 F1@5pct with low-data-win shape -- sub-word morphology is a substrate-product low-data lever. " + s)
    if cg5 >= 0.40:
        return ("MIDDLE_BAND", "MIDDLE_BAND: char n-gram F1@5pct 0.40-0.43 -- marginal; shape/affix features largely subsume char n-grams. " + s)
    return ("HARD_FAIL", "HARD_FAIL: char n-gram F1@5pct <0.40 -- char n-grams do not lift low-data NER. " + s)


def _selftest():
    assert _collapse4([1, 2, 0, 15]) == [1, 2, 0, 0]
    assert _spans([1, 2, 0]) == {(0, 2, 0)}
    assert _char_ngrams("cat", 3) == ["^ca", "cat", "at$"]
    fb = _emit_feats(["Cats"], 0, 1, False); fc = _emit_feats(["Cats"], 0, 1, True)
    assert not any(x.startswith("c3_") for x in fb) and any(x.startswith("c3_") for x in fc)
    print("[selftest] PASS: ner-feature-ablation", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
