"""
exp_ner_gazetteer_noise_crosscut_cpu_v1.py -- RESCUE-1 cross-cut: external-gazetteer x char-noise robustness -- CPU.

ROUTING: strategy_request_to_exp_dev_2026-06-12_gazetteer_char_noise_cross_cut (verdict_handler cycle 242, PP-403 cap_map v577).
  Substrate-quality-first, NO LLM frame.

HYPOTHESIS: external-gazetteer binary membership features are MORE noise-robust than char-surface lexical/affix features,
  so the gazetteer LIFT (gaz - baseline) should HOLD UP or GROW under char-level test noise -- compounding the low-data-win
  with a noisy-text robustness story.
  Honest mechanism caveat: gazetteer membership is EXACT-MATCH on the (possibly noised) lowercased token, so it ALSO
  degrades when noise corrupts a gazetteer word. The empirical question is whether it degrades SLOWER than the lexical/affix
  features it supplements. This cell measures that directly; the answer is not obvious a priori.

DESIGN: {baseline, +ext-gazetteer} x {clean, noisy@10pct char-perturb} x {5pct, 100pct} train fraction, 3 seeds.
  Test-time char noise (L-A style _char_perturb) with a FIXED noise realization per (frac, seed) so baseline and gaz see
  the SAME perturbed test -> clean paired lift. Training is on clean text (noise is adversarial test-time only).
  4-type CoNLL collapse (comparable to L-B curve + PP-403 gazetteer ablation).

PRE-REGISTERED (cross-cut headline = lift@5pct):
  - HARD-PASS: lift@5pct_noisy >= lift@5pct_clean + 0.02 (gazetteer compounds with noise robustness).
  - MIDDLE: lift@5pct_noisy in [lift@5pct_clean - 0.02, lift@5pct_clean + 0.02] (gazetteer noise-invariant).
  - HARD-FAIL: lift@5pct_noisy < lift@5pct_clean - 0.02 (gazetteer degrades under noise; refutes robustness claim).
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
ANCHOR_NAME = "ner_gazetteer_noise_crosscut_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
NOISE = 0.10  # moderate char-perturb (L-A: ~83pct retention at 10pct)
FRACS = [0.05, 1.0]
SEEDS = [1028, 1029, 1030]
COARSE = {0: 0, 3: 1, 4: 2, 5: 2, 2: 2, 1: 3, 6: 3, 14: 3, 15: 3, 16: 3, 17: 3}

# EXTERNAL gazetteers (identical to PP-403 exp_ner_gazetteer_external_cpu_v1).
_PER = """james john robert michael william david richard joseph thomas charles christopher daniel matthew anthony donald mark paul
steven andrew kenneth george joshua kevin brian edward ronald timothy jason jeffrey ryan jacob gary nicholas eric stephen jonathan
larry justin scott brandon frank benjamin gregory samuel raymond patrick alexander jack dennis jerry mary patricia jennifer linda
elizabeth barbara susan jessica sarah karen nancy lisa margaret betty sandra ashley dorothy kimberly emily donna michelle carol
amanda melissa deborah stephanie laura rebecca sharon cynthia kathleen helen amy angela anna ruth brenda pamela nicole katherine
smith johnson williams brown jones garcia miller davis rodriguez martinez hernandez lopez gonzalez wilson anderson thomas taylor
moore jackson martin lee perez thompson white harris sanchez clark ramirez lewis robinson walker young allen king wright scott
torres nguyen hill flores green adams nelson baker hall rivera campbell mitchell carter roberts gomez phillips evans turner diaz
parker cruz edwards collins reyes stewart morris morales murphy cook rogers gutierrez ortiz morgan cooper peterson bailey reed
kelly howard ramos kim cox ward richardson watson brooks chavez wood james bennett gray mendoza ruiz hughes price alvarez
obama trump clinton bush biden putin merkel xi modi abe blair churchill lincoln washington kennedy reagan nixon gandhi mandela""".split()
_LOC = """afghanistan albania algeria angola argentina armenia australia austria azerbaijan bangladesh belarus belgium bolivia brazil
bulgaria cambodia cameroon canada chile china colombia congo croatia cuba cyprus denmark ecuador egypt england estonia ethiopia
finland france germany ghana greece guatemala haiti honduras hungary iceland india indonesia iran iraq ireland israel italy jamaica
japan jordan kazakhstan kenya korea kuwait laos latvia lebanon liberia libya lithuania malaysia mali mexico mongolia morocco
mozambique myanmar nepal netherlands nicaragua niger nigeria norway pakistan panama paraguay peru philippines poland portugal qatar
romania russia rwanda saudi scotland senegal serbia singapore slovakia slovenia somalia spain sudan sweden switzerland syria taiwan
tanzania thailand tunisia turkey uganda ukraine uruguay uzbekistan venezuela vietnam wales yemen zambia zimbabwe america american
britain european alabama alaska arizona arkansas california colorado connecticut delaware florida georgia hawaii idaho illinois
indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota mississippi missouri montana nebraska nevada
ohio oklahoma oregon pennsylvania tennessee texas utah vermont virginia washington wisconsin wyoming london paris tokyo beijing
moscow berlin madrid rome cairo delhi mumbai shanghai seoul bangkok sydney toronto chicago boston houston atlanta dallas miami
detroit seattle denver phoenix philadelphia francisco angeles vegas orleans baghdad kabul tehran jerusalem gaza kashmir taipei
hong kong europe asia africa pacific atlantic mediterranean himalayas siberia amazon sahara""".split()
_ORG = """university college institute corporation corp incorporated inc company co ltd limited llc group holdings industries
ministry department agency administration bureau commission committee council board association federation union league society
foundation organization organisation party congress senate parliament assembly court tribunal bank fund reserve treasury exchange
airlines airways motors electronics systems technologies networks media press times post news journal gazette herald tribune
google microsoft apple amazon facebook ibm intel oracle samsung sony toyota honda nissan boeing airbus shell exxon chevron walmart
reuters cnn bbc nbc cbs abc espn nasa fbi cia nsa fda epa irs pentagon kremlin nato un opec eu nafta unesco unicef interpol
yahoo netflix tesla nvidia twitter uber paypal visa mastercard pfizer moderna novartis hsbc citigroup goldman barclays nomura
hamas hezbollah taliban qaeda isis democrats republicans tories labour kremlin senate""".split()
PER = frozenset(_PER); LOC = frozenset(_LOC); ORG = frozenset(_ORG)


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


def _gaz_tag(wl: str) -> str:
    if wl in PER: return "P"
    if wl in LOC: return "L"
    if wl in ORG: return "O"
    return ""


def _emit_feats(words, i, tag, use_gaz):
    w = words[i]; wl = w.lower(); fs = ["w_%s~%d" % (wl, tag), "sh_%s~%d" % (_shape(w), tag)]
    for k in (1, 2, 3, 4):
        if len(wl) >= k: fs.append("suf%d_%s~%d" % (k, wl[-k:], tag))
    if len(wl) >= 3: fs.append("pre3_%s~%d" % (wl[:3], tag))
    fs.append("pw_%s~%d" % (words[i - 1].lower() if i > 0 else "<S>", tag))
    fs.append("nw_%s~%d" % (words[i + 1].lower() if i + 1 < len(words) else "<E>", tag))
    fs.append("psh_%s~%d" % (_shape(words[i - 1]) if i > 0 else "<S>", tag))
    if use_gaz:
        gc = _gaz_tag(wl)
        if gc: fs.append("gaz_%s~%d" % (gc, tag))
        gp = _gaz_tag(words[i - 1].lower()) if i > 0 else ""
        if gp: fs.append("pgaz_%s~%d" % (gp, tag))
        gn = _gaz_tag(words[i + 1].lower()) if i + 1 < len(words) else ""
        if gn: fs.append("ngaz_%s~%d" % (gn, tag))
    return fs


def _train_eval(train, test, use_gaz, noise, seed) -> float:
    rng = np.random.default_rng(seed)
    TAGS = sorted({tg for _w, g in train for tg in g}); T = len(TAGS)
    w = defaultdict(float); cw = defaultdict(float); c = 1

    def tt(pt, t): return "tt_%d~%d" % (pt, t)

    def viterbi(words, weights):
        n = len(words)
        em = np.array([[sum(weights.get(f, 0.0) for f in _emit_feats(words, i, TAGS[k], use_gaz)) for k in range(T)] for i in range(n)])
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
                        for f in _emit_feats(words, i, gold[i], use_gaz): w[f] += 1; cw[f] += c
                        for f in _emit_feats(words, i, pred[i], use_gaz): w[f] -= 1; cw[f] -= c
                    w[tt(pg, gold[i])] += 1; cw[tt(pg, gold[i])] += c
                    w[tt(pp, pred[i])] -= 1; cw[tt(pp, pred[i])] -= c
                    pg = gold[i]; pp = pred[i]
            c += 1
    avg = {f: w[f] - cw[f] / c for f in w}
    nrng = np.random.default_rng(7)  # FIXED noise realization: same perturbed test for baseline vs gaz (paired)
    tp = fp = fn = 0
    for words, gold in test:
        tw = [_char_perturb(x, noise, nrng) for x in words] if noise > 0 else words
        pred = viterbi(tw, avg); gs = _spans(gold); ps = _spans(pred)
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
    cells = []
    for fr in fracs:
        for noise in (0.0, NOISE):
            bs = [_train_eval(_subset(train, fr, s), test, False, noise, s) for s in seeds]
            gz = [_train_eval(_subset(train, fr, s), test, True, noise, s) for s in seeds]
            bmu = sum(bs) / len(bs); gmu = sum(gz) / len(gz)
            cells.append({"frac": fr, "noise": noise, "baseline_f1": round(bmu, 4), "gaz_f1": round(gmu, 4), "lift": round(gmu - bmu, 4)})
            print("  frac=%4.0f%% noise=%2.0f%% baseline=%.4f gaz=%.4f lift=%+.4f"
                  % (100 * fr, 100 * noise, bmu, gmu, gmu - bmu), flush=True)
    return {"cells": cells, "noise_level": NOISE}


def _cross(cells, frac):
    def L(noise): return next((c["lift"] for c in cells if c["frac"] == frac and c["noise"] == noise), None)
    return L(0.0), L(NOISE)


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    cells = r["cells"]
    lc5, ln5 = _cross(cells, 0.05)
    lc100, ln100 = _cross(cells, 1.0)
    if lc5 is None or ln5 is None:
        return ("UNKNOWN", "UNKNOWN: missing 5pct cells")
    delta = ln5 - lc5
    s = ("lift@5pct clean=%+.4f noisy@%.0f%%=%+.4f (delta=%+.4f); lift@100pct clean=%s noisy=%s"
         % (lc5, 100 * r["noise_level"], ln5, delta, lc100, ln100))
    if delta >= 0.02:
        return ("HARD_PASS", "HARD_PASS: gazetteer lift GROWS under char noise (delta>=+0.02) -- external-gazetteer membership is MORE noise-robust than lexical/affix features; low-data-win compounds with noise robustness. " + s)
    if delta >= -0.02:
        return ("MIDDLE_BAND", "MIDDLE_BAND: gazetteer lift is NOISE-INVARIANT (|delta|<0.02) -- membership holds up about as well as it helps; robust but not compounding. " + s)
    return ("HARD_FAIL", "HARD_FAIL: gazetteer lift SHRINKS under char noise (delta<-0.02) -- exact-match membership degrades on perturbed tokens; noise-robustness claim refuted. " + s)


def _selftest():
    assert _gaz_tag("france") == "L" and _gaz_tag("zzzz") == ""
    assert _collapse4([1, 2, 0]) == [1, 2, 0]
    rng = np.random.default_rng(1)
    assert _char_perturb("Washington", 0.0, rng) == "Washington"
    assert isinstance(_char_perturb("Washington", 0.5, rng), str)
    print("[selftest] PASS: ner-gazetteer-noise-crosscut (PER=%d LOC=%d ORG=%d)" % (len(PER), len(LOC), len(ORG)), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s noise=%.0f%%" % (ANCHOR_NAME, RUN_MODE, 100 * NOISE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
