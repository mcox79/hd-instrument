"""
exp_ner_gazetteer_external_cpu_v1.py -- L-B mechanism deepening, Ablation 3: EXTERNAL gazetteer features -- CPU.

ROUTING: research_to_exp_dev_L_B_REROUTE...MECHANISM_DEEPENING_CRF_CHAR_CNN_GAZETTEER (2026-06-12, substrate-quality-first).
  The existing exp_ner_gazetteer_cpu_v1 uses a SELF-gazetteer (word -> dominant TRAIN tag). That cannot help the low-data regime:
  at 5pct data the self-gazetteer is exactly as sparse as the training set it is derived from. The substrate-product question is
  whether an EXTERNAL discrete feature library (curated person/location/org name lists -- prior knowledge the model cannot learn
  from sparse labels) lifts low-data NER. This is the discrete-feature-library low-data-win hypothesis (substrate aux-features
  shrink with data: strongest at 1-5pct, flat at 100pct).

  Design: PAIRED comparison at each train fraction. Same train subset (same seed) trained TWICE -- baseline emit-features vs
  baseline + binary external-gazetteer features (token in PER / LOC / ORG list, for prev/cur/next token). 4-type CoNLL collapse
  (reuses exp_ner_4type_conll_cpu_v1._collapse4) so it is directly comparable to the L-B few-shot curve (5pct=0.404, 10pct=0.501,
  100pct=0.644). Reports baseline F1, gaz F1, and lift per fraction.

PRE-REGISTERED (drill Ablation 3): HARD-PASS gaz F1 at 5pct >= 0.50 (+0.10 over L-B baseline 0.404) AND lift at 5pct > lift at
  100pct (low-data-win shape). MIDDLE gaz F1 at 5pct 0.45-0.50. HARD-FAIL < 0.45 (external gazetteer does not help low-data NER).
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
ANCHOR_NAME = "ner_gazetteer_external_cpu_v1"
# Inlined from exp_ner_4type_conll_cpu_v1 (importing it would run that cell's module-level experiment).
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

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
LB_BASELINE = {0.05: 0.404, 0.10: 0.501, 1.0: 0.644}  # L-B few-shot curve (4-type) for reference
FRACS = [0.05, 0.10, 1.0]
SEEDS = [1028, 1029, 1030]

# ---- EXTERNAL gazetteers (curated; lowercase single-token membership; prior knowledge NOT derived from train) ----
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


def _gaz_tag(wl: str) -> str:
    """External-gazetteer membership char for a lowercased token: P/L/O/'' (priority PER>LOC>ORG; multi-list resolved by priority)."""
    if wl in PER: return "P"
    if wl in LOC: return "L"
    if wl in ORG: return "O"
    return ""


def _emit_feats(words, i, tag, use_gaz: bool):
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


def _train_eval(train, test, use_gaz, seed) -> float:
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
    curve = []
    for fr in fracs:
        bs, gs = [], []
        for s in seeds:
            sub = _subset(train, fr, s)
            bs.append(_train_eval(sub, test, False, s))
            gs.append(_train_eval(sub, test, True, s))
        bmu = sum(bs) / len(bs); gmu = sum(gs) / len(gs)
        row = {"frac": fr, "baseline_f1": round(bmu, 4), "gaz_f1": round(gmu, 4),
               "lift": round(gmu - bmu, 4), "n_train": len(_subset(train, fr, seeds[0])), "lb_ref": LB_BASELINE.get(fr)}
        curve.append(row)
        print("  frac=%4.0f%% baseline=%.4f gaz=%.4f lift=%+.4f (n_train=%d, L-B ref %.3f)"
              % (100 * fr, bmu, gmu, gmu - bmu, row["n_train"], LB_BASELINE.get(fr, 0.0)), flush=True)
    return {"curve": curve, "n_per": len(PER), "n_loc": len(LOC), "n_org": len(ORG)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    curve = r["curve"]; by = {row["frac"]: row for row in curve}
    g5 = by.get(0.05, {}).get("gaz_f1", 0.0); l5 = by.get(0.05, {}).get("lift", 0.0)
    l100 = by.get(1.0, {}).get("lift", 0.0)
    shape = "low-data-win" if (1.0 in by and l5 > l100) else "flat/inverted"
    s = ("gaz F1@5pct=%.4f (lift %+.4f over baseline %.4f); lift@5pct=%+.4f vs lift@100pct=%+.4f -> %s; gaz lists PER=%d LOC=%d ORG=%d"
         % (g5, l5, by.get(0.05, {}).get("baseline_f1", 0.0), l5, l100, shape, r["n_per"], r["n_loc"], r["n_org"]))
    if g5 >= 0.50 and (1.0 not in by or l5 > l100):
        return ("HARD_PASS", "HARD_PASS: external gazetteer lifts low-data NER to >=0.50 F1@5pct with low-data-win shape -- discrete external feature library is a substrate-product low-data lever (prior knowledge the model cannot learn from sparse labels). " + s)
    if g5 >= 0.45:
        return ("MIDDLE_BAND", "MIDDLE_BAND: external gazetteer gaz F1@5pct 0.45-0.50 -- helps but below the +0.10 bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: external gazetteer gaz F1@5pct <0.45 -- curated discrete lists do not meaningfully lift low-data NER (coverage too thin or shape features already subsume). " + s)


def _selftest():
    assert _gaz_tag("james") == "P" and _gaz_tag("france") == "L" and _gaz_tag("microsoft") == "O" and _gaz_tag("xyzzy") == ""
    fs = _emit_feats(["James", "visited", "France"], 0, 1, True)
    assert any(f.startswith("gaz_P") for f in fs), fs
    fs0 = _emit_feats(["James", "visited", "France"], 0, 1, False)
    assert not any(f.startswith("gaz_") for f in fs0)
    assert _collapse4([1, 2, 0]) == [1, 2, 0]
    print("[selftest] PASS: ner-gazetteer-external (PER=%d LOC=%d ORG=%d)" % (len(PER), len(LOC), len(ORG)), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
