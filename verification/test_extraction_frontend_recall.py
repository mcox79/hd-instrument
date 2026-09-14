"""SCAFFOLD-FREE WITNESS for problem the_extraction_front_end_recovers_only_a_third_of_events_and_roles.

Recomputes EVERY headline from source (UD-EWT / QA-SRL / LitBank gold + the live extractor's own
rule constants + the in-substrate UPOS tagger). Does NOT read any exp cell's metrics.json and does
NOT import the exp cells -- it reimplements the detection rules + scoring inline, so a green run is
independent evidence.

Run:  .venv/Scripts/python.exe verification/test_extraction_frontend_recall.py
"""
import glob
import gzip
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from experiments import _temporal_ordering as T   # the live extractor's own rule constants
from hdlab.pos_tagger import PosTagger

AUX = set(T.AUX_LEMMAS); MODAL = set(T.MODAL_LEMMAS); COP = set(T.COPULA_BE)
UD = os.path.join(ROOT, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
QASRL = os.path.join(ROOT, "data", "benchmark_trap_check", "qasrl", "qasrl-v2", "orig", "dev.jsonl.gz")
LITBRAT = os.path.join(ROOT, "data", "litbank", "events", "brat")
ASSET = os.path.join(ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")

import nltk
_ = nltk.pos_tag(["test"])

PASS = []
def check(name, cond, detail=""):
    PASS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}  {detail}")


# ---- loaders -----------------------------------------------------------------
def load_ud(cap=None):
    S = []; cur = []
    for ln in open(UD, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#"):
            continue
        if not ln.strip():
            if cur: S.append(cur); cur = []
            continue
        c = ln.split("\t")
        if "-" in c[0] or "." in c[0]:
            continue
        cur.append(c)
    if cur: S.append(cur)
    return S[:cap] if cap else S

def load_qasrl(cap):
    S = []
    with gzip.open(QASRL, "rt", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            S.append((d["sentenceTokens"], set(int(k) for k in d["verbEntries"].keys())))
            if len(S) >= cap: break
    return S

def load_litbank(cap_books):
    S = []
    for txt in sorted(glob.glob(os.path.join(LITBRAT, "*.txt")))[:cap_books]:
        ann = txt[:-4] + ".ann"
        if not os.path.exists(ann): continue
        raw = open(txt, encoding="utf-8").read()
        starts = set()
        for line in open(ann, encoding="utf-8"):
            p = line.split("\t")
            if len(p) >= 2 and p[1].startswith("EVENT"):
                fs = p[1].split()
                if len(fs) >= 2: starts.add(int(fs[1]))
        pos = 0
        for line in raw.split("\n"):
            if not line.strip():
                pos += len(line) + 1; continue
            toks = line.split(" "); gold = set(); cp = pos
            for ti, tk in enumerate(toks):
                if cp in starts: gold.add(ti)
                cp += len(tk) + 1
            S.append((toks, gold)); pos += len(line) + 1
    return S


# ---- detection rules (reimplemented inline) ----------------------------------
def fire_current(tokens, xpos, i, lemmas=None):
    if tokens[i].lower() in AUX or (lemmas and lemmas[i].lower() in AUX): return False
    xp = xpos[i]; lows = [t.lower() for t in tokens]
    if xp == "VBD": return True
    if xp == "VBN":
        return any(lows[j] == "had" for j in range(max(0, i-3), i)) or \
               any(lows[j] in COP for j in range(max(0, i-3), i))
    if xp == "VB":
        return any(lows[j] in MODAL for j in range(max(0, i-3), i))
    if xp == "VBG":
        return not any(lows[j] in COP for j in range(max(0, i-3), i))
    return False

def fire_fix_tense(tokens, xpos, i, lemmas=None):     # CURRENT + VBZ/VBP (lemma-aware AUX filter)
    if fire_current(tokens, xpos, i, lemmas): return True
    if tokens[i].lower() in AUX or (lemmas and lemmas[i].lower() in AUX): return False
    return xpos[i] in ("VBZ", "VBP")


# ---- A/B/C: gold-POS diagnosis + rule fix (isolates the rule) -----------------
ud = load_ud()
tagger = PosTagger.load(ASSET)

def recall_prec_goldpos(sents, fire):
    tp = fires = gold = 0
    for rows in sents:
        toks = [c[1] for c in rows]; xp = [c[4] for c in rows]; lem = [c[2] for c in rows]
        for i, c in enumerate(rows):
            if c[3] == "VERB": gold += 1
            if fire(toks, xp, i, lem):
                fires += 1
                if c[3] == "VERB": tp += 1
    return tp/gold, (tp/fires if fires else 0), gold

rc, pc, g = recall_prec_goldpos(ud, fire_current)
rt, pt, _ = recall_prec_goldpos(ud, fire_fix_tense)
check("A. CURRENT event-detection recall ~0.33 on UD-EWT gold (the archetype)",
      0.30 <= rc <= 0.36, f"recall={rc:.4f} (n={g})")
check("B. CURRENT precision near-perfect in gold space (detection FPs ~0)",
      pc >= 0.99, f"precision={pc:.4f}")
check("C. FIX_TENSE recall lifts >=+0.12 with NO precision regression (rule is precision-neutral)",
      (rt - rc) >= 0.12 and pt >= pc - 0.005, f"d_recall=+{rt-rc:.4f} prec {pc:.4f}->{pt:.4f}")

# present-tense 100% miss under CURRENT
pres_gold = pres_det = 0
for rows in ud:
    toks = [c[1] for c in rows]; xp = [c[4] for c in rows]
    for i, c in enumerate(rows):
        if c[3] == "VERB" and c[4] in ("VBZ", "VBP"):
            pres_gold += 1
            if fire_current(toks, xp, i): pres_det += 1
check("D. present-tense finite verbs (VBZ/VBP) are missed 100% by CURRENT",
      pres_det == 0 and pres_gold > 100, f"detected {pres_det}/{pres_gold}")


# ---- E: realized fix (home-grown UPOS tagger, fire on VERB) beats CURRENT + generalizes ----
def eval_realized(sents_tok_gold, use_gold_xpos=None):
    """sents as list of (tokens, gold_event_idx_set). CURRENT via NLTK PTB; FIX via home-grown UPOS."""
    cur_tp = cur_g = fix_tp = fix_fi = 0
    per = []
    for item in sents_tok_gold:
        toks, gold = item
        xp = [t[1] for t in nltk.pos_tag(toks)]
        up = tagger.tag(toks)
        ct = sum(1 for i in gold if fire_current(toks, xp, i))
        ft = sum(1 for i in range(len(toks)) if up[i] == "VERB" and i in gold)   # pure UPOS==VERB
        ffi = sum(1 for i in range(len(toks)) if up[i] == "VERB")
        cur_tp += ct; fix_tp += ft; fix_fi += ffi; cur_g += len(gold)
        per.append((ct, ft, len(gold)))
    per = np.array(per, float)
    rng = np.random.default_rng(7)
    dr = np.array([(lambda s: (s[1]/s[2] if s[2] else 0) - (s[0]/s[2] if s[2] else 0))(per[rng.integers(0, len(per), len(per))].sum(0)) for _ in range(800)])
    return cur_tp/cur_g, fix_tp/cur_g, float(np.percentile(dr, 2.5))

# UD-EWT (tokens, gold) form
ud_tg = [([c[1] for c in rows], set(i for i, c in enumerate(rows) if c[3] == "VERB")) for rows in ud[:1200]]
rc2, rf2, lo2 = eval_realized(ud_tg)
check("E1. FIX (UPOS tagger, fire-on-VERB) recall CI-separated above CURRENT on UD-EWT",
      lo2 > 0 and rf2 > rc2 + 0.3, f"CURRENT={rc2:.4f} FIX={rf2:.4f} boot_lo=+{lo2:.4f}")

qa = load_qasrl(1200)
rc3, rf3, lo3 = eval_realized(qa)
check("E2. GENERALIZES OOD-modern (QA-SRL): FIX recall CI-separated above CURRENT",
      lo3 > 0 and rf3 > rc3 + 0.2, f"CURRENT={rc3:.4f} FIX={rf3:.4f} boot_lo=+{lo3:.4f}")

lit = load_litbank(8)
rc4, rf4, lo4 = eval_realized(lit)
check("E3. GENERALIZES OOD-19c (LitBank event triggers): FIX recall CI-separated above CURRENT",
      lo4 > 0 and rf4 > rc4, f"CURRENT={rc4:.4f} FIX={rf4:.4f} boot_lo=+{lo4:.4f}")


# ---- F: downstream who-did-what lift -----------------------------------------
NOM = {"NOUN", "PROPN", "PRON"}
def gold_tuples(rows):
    tup = set()
    for i, r in enumerate(rows):
        if r[3] != "VERB": continue
        for c in rows:
            h = int(c[6]) - 1 if c[6].isdigit() else -2
            if h == i and c[7] in ("nsubj",): tup.add((i, c[2].lower(), "A"))
            elif h == i and c[7] in ("obj", "dobj"): tup.add((i, c[2].lower(), "P"))
    return tup
def positional(rows, pi, upos):
    a = p = None
    for j in range(pi-1, -1, -1):
        if upos[j] in NOM: a = rows[j][2].lower(); break
    for j in range(pi+1, len(rows)):
        if upos[j] in NOM: p = rows[j][2].lower(); break
    return a, p
def wdw_recall(detset_fn):
    got = tot = 0
    for rows in ud[:1200]:
        toks = [c[1] for c in rows]; upos = [c[3] for c in rows]
        det = detset_fn(rows, toks)
        g = gold_tuples(rows); tot += len(g)
        for (pi, arg, role) in g:
            if pi not in det: continue
            a, p = positional(rows, pi, upos)
            if (a if role == "A" else p) == arg: got += 1
    return got/tot if tot else 0
def det_current(rows, toks):
    xp = [t[1] for t in nltk.pos_tag(toks)]
    return set(i for i in range(len(toks)) if fire_current(toks, xp, i))
def det_fix(rows, toks):
    up = tagger.tag(toks)
    return set(i for i in range(len(toks)) if up[i] == "VERB")   # pure UPOS==VERB
wc = wdw_recall(det_current); wf = wdw_recall(det_fix)
check("F. downstream who-did-what tuple recall lifts >=+0.25 with FIX detection",
      (wf - wc) >= 0.25, f"CURRENT={wc:.4f} FIX={wf:.4f} d=+{wf-wc:.4f}")

# ---- G: END-TO-END through the live SituationReader.read() (strategy's standing trap) ----
import tempfile
from hdlab import situation_reader as SR
def _fixed_extract(text, tagger=None):
    toks = text.split(); up = tagger_g.tag(toks); evs = []
    for i, tk in enumerate(toks):
        if up[i] == "VERB":   # pure UPOS==VERB
            evs.append(T.Event(lemma=tk.lower(), idx=i, pos=up[i], tense=T.TENSE_SIMPLE_PAST, is_pp=False))
    return evs, []
tagger_g = tagger
ud_e2e = load_ud(150)
lines = ["#begin document (w); part 0"]
for si, rows in enumerate(ud_e2e):
    if si: lines.append("")
    for wi, c in enumerate(rows):
        lines.append("\t".join(["w", "0", str(wi), c[1]] + ["_"] * 7 + ["_"]))
lines.append("")
fd, cp = tempfile.mkstemp(suffix=".conll"); os.close(fd)
open(cp, "w", encoding="utf-8").write("\n".join(lines) + "\n")
def _e2e_recall(events, rows_list):
    from collections import Counter as _C
    by = {}
    for e in events: by.setdefault(e.sent_idx, _C())[str(e.predicate).lower()] += 1
    tp = gold = 0
    for si, rows in enumerate(rows_list):
        gf = _C(c[1].lower() for c in rows if c[3] == "VERB"); gold += sum(gf.values())
        for f, n in by.get(si, _C()).items(): tp += min(n, gf.get(f, 0))
    return tp / gold if gold else 0
# 2026-09-14 (strategy): the reader's default detector is the category-organ VERB detector (tense_agnostic_events default-ON),
# which never calls T.extract_events -- monkeypatching it reached neither read (CURRENT == FIX == 0.9228, a stale instrument, not
# a regression). CURRENT = the reader with the stock tense-gated detector selected (tense_agnostic_events=False); FIX = the default.
rd_cur = SR.SituationReader(tense_agnostic_events=False)
rc = _e2e_recall(rd_cur.read(cp).events, ud_e2e)
rd = SR.SituationReader()
rf = _e2e_recall(rd.read(cp).events, ud_e2e)
os.unlink(cp)
check("G. END-TO-END through live SituationReader.read(): FIX recall lifts >=+0.3 (not a gold-isolation artifact)",
      (rf - rc) >= 0.3, f"CURRENT={rc:.4f} FIX={rf:.4f} d=+{rf-rc:.4f}")

# ---- H/I: ROLE stage -- the built-but-unwired precise_voice fix, through the REAL hdlab _assign_roles ----
from hdlab import situation_reader as SR
def _ud_full(cap):
    S, cur = [], []
    for ln in open(UD, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.startswith("#"): continue
        if not ln.strip():
            if cur: S.append(cur); cur = []
            continue
        c = ln.split("\t")
        if "-" in c[0] or "." in c[0]: continue
        cur.append(dict(form=c[1], lemma=c[2].lower(), upos=c[3],
                        head=(int(c[6]) - 1 if c[6].isdigit() else -1), deprel=c[7]))
    if cur: S.append(cur)
    return S[:cap]
def _gold_roles(rows):
    out = {}
    for i, r in enumerate(rows):
        if r["upos"] != "VERB": continue
        ag = pt = None; ai = pi = None; nc = False
        for j, c in enumerate(rows):
            if c["head"] != i: continue
            d = c["deprel"]
            if d == "nsubj:pass": pt = c["lemma"]; pi = j; nc = True
            elif d == "obl:agent": ag = c["lemma"]; ai = j; nc = True
            elif d.split(":")[0] == "nsubj": ag = c["lemma"]; ai = j
            elif d.split(":")[0] in ("obj", "iobj"): pt = c["lemma"]; pi = j
        if pi is not None and pi < i: nc = True
        if ai is not None and ai > i: nc = True
        if ag or pt: out[i] = (ag, pt, nc)
    return out
NOMU = {"NOUN", "PROPN", "PRON"}
sr = np.random.default_rng(5)
acc = {a: {"c": [0, 0], "n": [0, 0]} for a in ("OFF", "ON", "TW")}   # [correct, total]
for rows in _ud_full(1200):
    toks = [r["form"] for r in rows]; up = tagger.tag(toks)
    det = set(i for i in range(len(toks)) if up[i] == "VERB")
    noms = [dict(wtok_start=j, midx=j, sent_idx=0, is_pronoun=False, is_subject=False, head=rows[j]["lemma"])
            for j in range(len(toks)) if up[j] in NOMU]
    nl = [m["head"] for m in noms]
    for vi, (ga, gp, nc) in _gold_roles(rows).items():
        if vi not in det: continue
        k = "n" if nc else "c"
        aoff, poff = SR._assign_roles(vi, noms, lemma=toks[vi], toks=toks, precise_voice=False)
        aon, pon = SR._assign_roles(vi, noms, lemma=toks[vi], toks=toks, precise_voice=True)
        ta = nl[sr.integers(0, len(nl))] if nl else "?"; tp = nl[sr.integers(0, len(nl))] if nl else "?"
        for role, gv in (("A", ga), ("P", gp)):
            if gv is None: continue
            acc["OFF"][k][1] += 1; acc["ON"][k][1] += 1; acc["TW"][k][1] += 1
            acc["OFF"][k][0] += int((aoff if role == "A" else poff) == gv)
            acc["ON"][k][0] += int((aon if role == "A" else pon) == gv)
            acc["TW"][k][0] += int((ta if role == "A" else tp) == gv)
def _a(x): return x[0] / x[1] if x[1] else 0.0
off_nc, on_nc, tw_nc = _a(acc["OFF"]["n"]), _a(acc["ON"]["n"]), _a(acc["TW"]["n"])
off_c, on_c = _a(acc["OFF"]["c"]), _a(acc["ON"]["c"])
check("H. ROLE: built-but-unwired precise_voice lifts NON-CANONICAL who-did-what >=+0.15 (through real hdlab _assign_roles)",
      (on_nc - off_nc) >= 0.15, f"OFF={off_nc:.4f} ON={on_nc:.4f} d=+{on_nc-off_nc:.4f}")
check("I. ROLE: no canonical regression (>=-0.01) AND info-free twin loses on non-canonical",
      (on_c - off_c) >= -0.01 and on_nc > tw_nc, f"canon {off_c:.4f}->{on_c:.4f}; twin_nc={tw_nc:.4f} vs ON {on_nc:.4f}")

print(f"\n{'ALL PASS' if all(PASS) else 'SOME FAILED'}: {sum(PASS)}/{len(PASS)} checks")
sys.exit(0 if all(PASS) else 1)
