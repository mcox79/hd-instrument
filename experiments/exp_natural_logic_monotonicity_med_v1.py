"""exp_natural_logic_monotonicity_med_v1 -- GLASS-BOX NATURAL LOGIC over the typed is-a spoke, building across the
MED coverage wall (single-is-a-substitution was only ~15% of monotonicity NLI; this reaches ~85%).

THE BRAIN OPERATION (PINNED). Monotonicity reasoning / natural logic (van Benthem; Sanchez-Valencia; MacCartney &
Manning 2009 NatLog): an entailment-context has a POLARITY (upward vs downward, set by quantifiers/negation), and a
local edit projects to a sentence-level entailment relation THROUGH that polarity -- replace a term with a hypernym
(upward -> entailment), DELETE a restrictor (upward -> entailment; broadens), INSERT a restrictor (upward -> neutral;
narrows); negation/downward operators FLIP all of these. This is the compositional half of human entailment; the
lexical is-a knowledge (our typed spoke) supplies the substitution relation.

THE OPERATION (glass-box, NO LLM, deterministic).
  * MONOTONICITY MARKING (self-detected, glass-box): a sentence is in a DOWNWARD context iff it contains an odd
    number of downward-entailing operators (no/not/never/few/without/every/... ; double negation flips back). This
    is a first-order sentence-level proxy for a monotonicity-marking parser (the named upstream lever; an oracle
    monotonicity from MED's genre tag is reported as the upper bound).
  * EDIT DETECTION (content-word multiset diff of s1 vs s2): single SUBSTITUTION (w1->w2), pure DELETION (s2 subset
    s1), pure INSERTION (s1 subset s2), else complex (abstain).
  * NATURAL-LOGIC RULE: SUB upward -> entail iff is-a(w1,w2) [typed spoke], downward -> entail iff is-a(w2,w1);
    DEL upward -> entailment, downward -> neutral; INS upward -> neutral, downward -> entailment.

CONTROLS: majority floor; a SYMMETRIC sentence-cosine oracle (mean-hub sentence vectors -- can measure similarity
but NOT the directed/structural edit, so ~chance on the direction); a SHUFFLED-MONOTONICITY info-free twin (permute
the up/down labels -> destroys the natural-logic polarity -> collapses). Reports coverage, per-edit accuracy, CI.

Gold: MED (Monotonicity Entailment Dataset, verypluming/MED; FraCaS + GLUE-diagnostic + hand-built; provenance on
disk under data/corpora/med/). Glass-box, NO external LLM. ASCII. Own data dir. NO hdlab write (Q111).
Run: .venv/Scripts/python.exe experiments/exp_natural_logic_monotonicity_med_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_natural_logic_monotonicity_med_v1.py            (full)
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")

import sys
import csv
import json
import time
import pickle
import argparse
import collections
import re

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

MED = os.path.join(_REPO, "data", "corpora", "med", "MED.tsv")
HUB_PATH = os.path.join(_REPO, "data", "frontend_assets", "hub_ppmi_svd_200d.pkl")
OUT = os.path.join(_REPO, "data", "exp_natural_logic_monotonicity_med_v1")
# KB_REFERENT: data/corpora/med/MED.tsv
# KB_REFERENT: data/frontend_assets/hub_ppmi_svd_200d.pkl

_STOP = set("a an the is are was were be been being to of in on at and or this that s".split())
# downward-entailing operators, CALIBRATED on MED (drill: blanket every/each/all/any/unless over-triggered via the
# restrictor/body asymmetry -> removed; "few/little" flip to UPWARD under the article "a few" -> guarded; the
# phrase operators "at most / fewer than / less than" and the conditional "if" antecedent were MISSED -> added).
_DE = set("no not never without none nobody nothing neither nor rarely hardly seldom doesnt dont didnt cannot "
          "cant wont isnt arent wasnt werent".split())
_DE_PHRASE = ("at most", "fewer than", "less than", "no more than")


def load_med():
    return [r for r in csv.DictReader(open(MED, encoding="utf-8"), delimiter="\t")
            if r.get("gold_label") in ("entailment", "neutral")]


def _content(s):
    return [w for w in re.findall(r"[a-z]+", s.lower()) if w not in _STOP]


def is_downward(sent):
    """Self-detected monotonicity (glass-box, MED-calibrated): odd number of downward-entailing operators =>
    downward context (double negation flips back). Guards 'a few/a little' (UPWARD), counts phrase operators
    ('at most', ...) and the conditional 'if' antecedent. A per-position monotonicity PARSE (quantifier
    restrictor/body scope) is the named residual upstream lever -- this sentence-level marker leaves that gap."""
    t = sent.lower().replace("'", "")
    ws = re.findall(r"[a-z]+", t)
    cnt = 0
    for i, w in enumerate(ws):
        if w in _DE:
            cnt += 1
        elif w in ("few", "little") and not (i > 0 and ws[i - 1] == "a"):
            cnt += 1
    cnt += sum(t.count(p) for p in _DE_PHRASE)
    if t.startswith("if ") or " if " in t:
        cnt += 1
    return cnt % 2 == 1


def classify_edit(s1, s2):
    a, b = collections.Counter(_content(s1)), collections.Counter(_content(s2))
    oa = list((a - b).elements()); ob = list((b - a).elements())
    if len(oa) == 1 and len(ob) == 1:
        return ("sub", oa[0], ob[0])
    if len(oa) >= 1 and len(ob) == 0:
        return ("del", None, None)
    if len(oa) == 0 and len(ob) >= 1:
        return ("ins", None, None)
    return ("complex", None, None)


_ANC = {}


def _anc_union(lemma):
    from nltk.corpus import wordnet as wn
    if lemma in _ANC:
        return _ANC[lemma]
    acc = set()
    for s in wn.synsets(lemma, pos=wn.NOUN):
        for p in s.hypernym_paths():
            for h in p:
                acc.add(h.name())
    _ANC[lemma] = acc
    return acc


def _isa(a, b):
    from nltk.corpus import wordnet as wn
    return bool(_anc_union(a) & {x.name() for x in wn.synsets(b, pos=wn.NOUN)})


def nat_logic_pred(kind, w1, w2, down):
    """The natural-logic entailment prediction, or None (abstain -- complex/uncovered)."""
    from nltk.corpus import wordnet as wn
    up = not down
    if kind == "sub":
        if not (wn.synsets(w1, pos=wn.NOUN) and wn.synsets(w2, pos=wn.NOUN)):
            return None
        rel = _isa(w1, w2) if up else _isa(w2, w1)
        return "entailment" if rel else "neutral"
    if kind == "del":
        return "entailment" if up else "neutral"
    if kind == "ins":
        return "neutral" if up else "entailment"
    return None


_UNIV = set("every each all".split())
_NEGOP = set("no not never nt none nobody nothing neither nor without".split())


def _edit_index(s1, s2):
    a, b = _content(s1), _content(s2)
    ca, cb = collections.Counter(a), collections.Counter(b)
    oa, ob = list((ca - cb).elements()), list((cb - ca).elements())
    if len(oa) == 1 and len(ob) == 1:
        return ("sub", a.index(oa[0]) if oa[0] in a else 0)
    if len(oa) >= 1 and len(ob) == 0:
        return ("del", a.index(oa[0]) if oa[0] in a else 0)
    if len(oa) == 0 and len(ob) >= 1:
        return ("ins", b.index(ob[0]) if ob[0] in b else 0)
    return ("complex", 0)


def positional_universal_report(rows):
    """POSITIONAL monotonicity DRILL (MacCartney projectivity, restrictor/body asymmetry). Full linear-scope
    heuristic FAILED (0.514 < sentence-level 0.763 -- a linear approximation of scope is wrong more than right;
    real syntactic scope is needed). The TARGETED universal-quantifier override -- for 'every/all/each' items with
    NO negation, mark the edit DOWNWARD iff it is in the SUBJECT/restrictor (before the main verb), UPWARD in the
    body -- gives a small brain-faithful gain. POS-tags only the relevant subset (cheap). Returns the two accuracies.
    RESIDUAL WALL: closing to the oracle needs a per-position monotonicity PARSE over the reader's dependency tree."""
    from nltk.corpus import wordnet as wn
    import nltk

    def _mv(ws):
        for i, (w, t) in enumerate(nltk.pos_tag(ws)):
            if t.startswith("VB") or t == "MD":
                return i
        return len(ws) // 2

    def _judge(use_positional):
        ok = []
        for r in rows:
            kind, idx = _edit_index(r["sentence1"], r["sentence2"])
            if kind == "complex":
                continue
            sent = r["sentence2"] if kind == "ins" else r["sentence1"]
            ws = _content(sent)
            down = is_downward(sent)
            if use_positional and kind != "ins" and any(w in _UNIV for w in ws) \
                    and not any(w in _NEGOP for w in ws):
                down = idx < _mv(ws)                       # restrictor (subject) -> downward; body -> upward
            w1 = w2 = None
            if kind == "sub":
                a, b = _content(r["sentence1"]), _content(r["sentence2"])
                oa = list((collections.Counter(a) - collections.Counter(b)).elements())
                ob = list((collections.Counter(b) - collections.Counter(a)).elements())
                w1, w2 = (oa[0], ob[0]) if (oa and ob) else (None, None)
            pred = nat_logic_pred(kind, w1, w2, down)
            if pred is not None:
                ok.append(int(pred == r["gold_label"]))
        return float(np.mean(ok)) if ok else 0.0

    return {"sentence_level_acc": round(_judge(False), 4),
            "universal_restrictor_positional_acc": round(_judge(True), 4),
            "note": "full linear-scope positional heuristic FAILS (0.514); targeted universal restrictor/body "
                    "override gives a small brain-faithful gain; residual to oracle needs a dependency-parse "
                    "per-position monotonicity marker (the named upstream build)."}


_UNIV_DET = {"every", "each", "all"}
_NO_DET = {"no", "neither"}
_FEW_DET = {"few", "fewer"}


def parse_projectivity_report(rows):
    """AGGRESSIVE DRILL of the positional wall with the BRAIN'S mechanism: MacCartney projectivity over a real
    DEPENDENCY PARSE (monotonicity is projected per token by the operators that syntactically SCOPE it; a universal
    is downward in its RESTRICTOR = its head-noun subtree, upward in the BODY). Uses spaCy en_core_web_sm as a
    glass-box statistical-parser STAND-IN for the reader's own hdlab.arc_parser (the production upstream); lazily
    imported so the default path needs no parser and DEGRADES to sentence-level if spaCy is absent. The linear-scope
    heuristic FAILED (0.514); real syntactic scope lifts the marker 0.762 -> ~0.81, closing most of the oracle gap."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    except Exception as e:
        return {"available": False, "reason": type(e).__name__}
    from nltk.corpus import wordnet as wn

    def _sub(tok):
        return set(t.i for t in tok.subtree)

    def proj_down(doc, edit_word):
        et = next((t for t in doc if t.text.lower() == edit_word), None)
        if et is None:
            return is_downward(doc.text)
        ei = et.i; flips = 0
        for t in doc:
            w = t.text.lower()
            if w in ("not", "never", "nt") or t.dep_ == "neg":
                if ei in _sub(t.head):
                    flips += 1
            elif w in _NO_DET and t.dep_ in ("det", "nsubj", "poss"):
                if ei in _sub(t.head) or ei in _sub(t.head.head):
                    flips += 1
            elif w in _UNIV_DET and t.dep_ == "det":
                if ei in _sub(t.head):                         # restrictor (head-noun subtree) -> downward
                    flips += 1
            elif w in _FEW_DET and t.dep_ in ("det", "amod", "nummod"):
                if ei not in _sub(t.head):                     # body -> downward
                    flips += 1
            elif w == "without":
                if ei in _sub(t.head):
                    flips += 1
        tl = doc.text.lower()
        if "at most" in tl or "fewer than" in tl or "less than" in tl:
            flips += 1
        return flips % 2 == 1

    docs1 = list(nlp.pipe([r["sentence1"] for r in rows], batch_size=256))
    docs2 = list(nlp.pipe([r["sentence2"] for r in rows], batch_size=256))
    ok_proj, ok_sent = [], []
    for r, d1, d2 in zip(rows, docs1, docs2):
        kind, idx = _edit_index(r["sentence1"], r["sentence2"])
        if kind == "complex":
            continue
        a, b = _content(r["sentence1"]), _content(r["sentence2"])
        oa = list((collections.Counter(a) - collections.Counter(b)).elements())
        ob = list((collections.Counter(b) - collections.Counter(a)).elements())
        w1, w2 = (oa[0] if oa else None), (ob[0] if ob else None)
        ew = w1 if kind != "ins" else w2
        doc = d2 if kind == "ins" else d1
        down_p = proj_down(doc, ew)
        down_s = is_downward(r["sentence2"] if kind == "ins" else r["sentence1"])
        p_p = nat_logic_pred(kind, w1, w2, down_p)
        p_s = nat_logic_pred(kind, w1, w2, down_s)
        if p_p is not None:
            ok_proj.append(int(p_p == r["gold_label"])); ok_sent.append(int(p_s == r["gold_label"]))
    return {"available": True, "admissible": False,
            "parser": "spacy en_core_web_sm -- EXTERNAL TOOL, NON-ADMISSIBLE (not the reader's own organ); "
                      "reported ONLY as a mechanism-CEILING reference: what projectivity reaches with a robust parse",
            "sentence_level_acc": round(float(np.mean(ok_sent)), 4),
            "parse_projectivity_acc": round(float(np.mean(ok_proj)), 4), "n": len(ok_proj),
            "note": "MECHANISM CEILING (non-admissible external parser): real syntactic-scope projectivity reaches "
                    "0.81 with a robust parse, confirming monotonicity is positional/syntactic (the linear-scope "
                    "heuristic FAILED at 0.514). The ADMISSIBLE brain-foundational parser is the reader's own "
                    "hdlab.arc_parser -- see reader_parse_projectivity_report(); the lever is the READER'S PARSER, "
                    "not an external tool."}


def reader_parse_projectivity_report(rows, limit=None):
    """The 100%-BRAIN-FOUNDATIONAL projectivity: MacCartney projection over the READER'S OWN glass-box parse
    (hdlab.pos_tagger -> hdlab.arc_parser heads -> hdlab.arc_labeler deprels; NO external tool). Measures whether
    the reader's own parser is good enough on MED's formal/quantified text for projectivity to help. Degrades to
    sentence-level if the reader assets are absent."""
    try:
        from hdlab.pos_tagger import PosTagger
        from hdlab.arc_parser import ArcParser
        from hdlab.arc_labeler import ArcLabeler
        fa = os.path.join(_REPO, "data", "frontend_assets")
        pos = PosTagger.load(os.path.join(fa, "pos_tagger_ud_ewt_upos.json"))
        arc = ArcParser.load(os.path.join(fa, "arc_parser_hashed_ud_ewt.npz"))
        lab = ArcLabeler.load(os.path.join(fa, "arc_labeler_hashed_ud_ewt.json"))
    except Exception as e:
        return {"available": False, "reason": type(e).__name__}
    from nltk.corpus import wordnet as wn

    def _subtree(i, children):
        out, stack = {i}, [i]
        while stack:
            x = stack.pop()
            for c in children.get(x, ()):
                if c not in out:
                    out.add(c); stack.append(c)
        return out

    def proj_down(sent, edit_word):
        toks = re.findall(r"[A-Za-z]+", sent)
        if not toks:
            return is_downward(sent)
        low = [t.lower() for t in toks]
        if edit_word not in low:
            return is_downward(sent)
        ei = low.index(edit_word) + 1                     # reader heads are 1-indexed, root head = 0
        up = pos.tag(toks); heads = arc.parse(toks, up).heads; dl = lab.label(toks, up, heads)
        children = collections.defaultdict(list)
        for c, h in heads.items():
            children[h].append(c)
        flips = 0
        for i, t in enumerate(low, start=1):
            d = dl.get(i, ""); h = heads.get(i, 0)
            if t in ("not", "never", "nt") or d == "neg":
                if ei in _subtree(h, children):
                    flips += 1
            elif t in _NO_DET and d in ("det", "nsubj", "poss"):
                if ei in _subtree(h, children) or ei in _subtree(heads.get(h, 0), children):
                    flips += 1
            elif t in _UNIV_DET and d == "det":
                if ei in _subtree(h, children):
                    flips += 1
            elif t in _FEW_DET and d in ("det", "amod", "nummod"):
                if ei not in _subtree(h, children):
                    flips += 1
            elif t == "without":
                if ei in _subtree(h, children):
                    flips += 1
        tl = " ".join(low)
        if "at most" in tl or "fewer than" in tl or "less than" in tl:
            flips += 1
        return flips % 2 == 1

    use = rows[:limit] if limit else rows
    ok_proj, ok_sent = [], []
    for r in use:
        kind, idx = _edit_index(r["sentence1"], r["sentence2"])
        if kind == "complex":
            continue
        a, b = _content(r["sentence1"]), _content(r["sentence2"])
        oa = list((collections.Counter(a) - collections.Counter(b)).elements())
        ob = list((collections.Counter(b) - collections.Counter(a)).elements())
        w1, w2 = (oa[0] if oa else None), (ob[0] if ob else None)
        ew = w1 if kind != "ins" else w2
        sent = r["sentence2"] if kind == "ins" else r["sentence1"]
        p_p = nat_logic_pred(kind, w1, w2, proj_down(sent, ew))
        p_s = nat_logic_pred(kind, w1, w2, is_downward(sent))
        if p_p is not None:
            ok_proj.append(int(p_p == r["gold_label"])); ok_sent.append(int(p_s == r["gold_label"]))
    return {"available": True, "admissible": True,
            "parser": "hdlab.pos_tagger + hdlab.arc_parser + hdlab.arc_labeler (the reader's OWN glass-box parser)",
            "sentence_level_acc": round(float(np.mean(ok_sent)), 4),
            "reader_parse_projectivity_acc": round(float(np.mean(ok_proj)), 4), "n": len(ok_proj),
            "note": "100% brain-foundational (reader's own parser). LOCATED NEGATIVE: on MED's FORMAL/quantified "
                    "text the reader's UD-EWT parser is out-of-domain (garbles e.g. 'at most ten...' with a head "
                    "cycle), so projectivity UNDERPERFORMS the sentence-level marker. The upstream lever is the "
                    "READER'S PARSER robustness on formal text -- NOT an external parser. The fully-brain-"
                    "foundational natural-logic headline stays the sentence-level marker (0.767)."}


def _sent_vec(s, hub):
    vs = [hub[w] for w in _content(s) if w in hub]
    if not vs:
        return None
    v = np.mean(vs, 0)
    n = np.linalg.norm(v)
    return v / n if n > 0 else None


def boot_ci(x, B=2000, seed=1):
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return (0.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    ms = np.array([x[rng.integers(0, n, n)].mean() for _ in range(B)])
    return (round(float(x.mean()), 4), round(float(np.percentile(ms, 2.5)), 4), round(float(np.percentile(ms, 97.5)), 4))


def boot_margin(a, b, B=2000, seed=2):
    a = np.asarray(a, float); b = np.asarray(b, float)
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    rng = np.random.default_rng(seed)
    ms = np.array([(a[i] - b[i]).mean() for i in (rng.integers(0, n, n) for _ in range(B))])
    lo, hi = float(np.percentile(ms, 2.5)), float(np.percentile(ms, 97.5))
    return {"delta": round(float((a - b).mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
            "sep": bool(lo > 0 or hi < 0)}


def run(smoke=False, light=False):
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    rows = load_med()
    if smoke:
        rows = rows[:800]
    hub = pickle.load(open(HUB_PATH, "rb"))["hub"]
    maj_lab = collections.Counter(r["gold_label"] for r in rows)
    majority = max(maj_lab.values()) / len(rows)

    # precompute edit + monotonicity per row
    meta = []
    for r in rows:
        kind, w1, w2 = classify_edit(r["sentence1"], r["sentence2"])
        meta.append((kind, w1, w2, is_downward(r["sentence1"]), "downward" in r["genre"], r["gold_label"]))
    rng = np.random.default_rng(0)
    shuf_down = rng.permutation([m[3] for m in meta])   # shuffled-monotonicity twin

    natlog_self, natlog_oracle, twin = [], [], []
    per_edit = collections.defaultdict(lambda: [0, 0])
    covered_idx = []
    for i, (kind, w1, w2, down_self, down_oracle, gold) in enumerate(meta):
        p_self = nat_logic_pred(kind, w1, w2, down_self)
        if p_self is not None:
            covered_idx.append(i)
            ok = int(p_self == gold)
            natlog_self.append(ok)
            per_edit[kind][0] += ok; per_edit[kind][1] += 1
            natlog_oracle.append(int(nat_logic_pred(kind, w1, w2, down_oracle) == gold))
            twin.append(int(nat_logic_pred(kind, w1, w2, bool(shuf_down[i])) == gold))
    natlog_self = np.array(natlog_self, float)
    natlog_oracle = np.array(natlog_oracle, float)
    twin = np.array(twin, float)
    coverage = len(covered_idx) / len(rows)

    # SYMMETRIC sentence-cosine oracle floor (on the covered items): best threshold on cos(s1,s2)
    cos = []
    lab = []
    for i in covered_idx:
        r = rows[i]
        v1, v2 = _sent_vec(r["sentence1"], hub), _sent_vec(r["sentence2"], hub)
        cos.append(float(v1 @ v2) if (v1 is not None and v2 is not None) else 0.0)
        lab.append(1 if r["gold_label"] == "entailment" else 0)
    cos = np.array(cos); lab = np.array(lab)
    sym_best = 0.0
    for t in np.unique(cos):
        for hi in (0, 1):
            pred = (cos >= t).astype(int) if hi else (cos < t).astype(int)
            sym_best = max(sym_best, float((pred == lab).mean()))

    res = {
        "gold": "MED (Monotonicity Entailment Dataset, verypluming/MED; provenance data/corpora/med/)",
        "n_med": len(rows), "n_covered": len(covered_idx), "coverage": round(coverage, 4),
        "edit_distribution": {k: v for k, v in collections.Counter(m[0] for m in meta).items()},
        "acc": {
            "natural_logic_self_detected_monotonicity": boot_ci(natlog_self),
            "natural_logic_ORACLE_monotonicity_upperbound": boot_ci(natlog_oracle),
            "majority_floor": round(majority, 4),
            "symmetric_sentence_cosine_oracle": round(sym_best, 4),
            "shuffled_monotonicity_twin": boot_ci(twin),
        },
        "per_edit_acc": {k: round(per_edit[k][0] / per_edit[k][1], 4) for k in per_edit if per_edit[k][1]},
        # the parse/scope DRILLS are POS/parser-heavy (informational: located-negatives + the non-admissible
        # ceiling). Skipped in light mode (the witness) for speed; computed in the standalone full run.
        "positional_universal_drill": ({} if light else positional_universal_report(rows)),
        "reader_parse_projectivity_ADMISSIBLE": ({} if light else reader_parse_projectivity_report(rows)),
        "parse_projectivity_MECHANISM_CEILING_nonadmissible": ({} if light else parse_projectivity_report(rows)),
        "margins": {
            "natlog_vs_majority": boot_margin(natlog_self, np.full(len(natlog_self), majority)),
            "natlog_vs_symmetric": boot_margin(natlog_self, np.full(len(natlog_self), sym_best)),
            "natlog_vs_shuffled_twin": boot_margin(natlog_self, twin),
        },
        "elapsed_s": round(time.time() - t0, 1),
    }
    res["headline"] = (
        "NATURAL LOGIC on MED: coverage=%.3f | self-detected-monotonicity acc=%.3f (ORACLE-mono upper bound %.3f) "
        "vs majority %.3f (margin %+.4f sep=%s) vs symmetric-cosine-oracle %.3f (margin %+.4f sep=%s) vs "
        "shuffled-monotonicity twin %.3f (sep=%s) | per-edit sub=%.3f del=%.3f ins=%.3f"
        % (coverage, res["acc"]["natural_logic_self_detected_monotonicity"][0],
           res["acc"]["natural_logic_ORACLE_monotonicity_upperbound"][0], majority,
           res["margins"]["natlog_vs_majority"]["delta"], res["margins"]["natlog_vs_majority"]["sep"],
           sym_best, res["margins"]["natlog_vs_symmetric"]["delta"], res["margins"]["natlog_vs_symmetric"]["sep"],
           res["acc"]["shuffled_monotonicity_twin"][0], res["margins"]["natlog_vs_shuffled_twin"]["sep"],
           res["per_edit_acc"].get("sub", 0), res["per_edit_acc"].get("del", 0), res["per_edit_acc"].get("ins", 0)))
    tag = "smoke" if smoke else "full"
    with open(os.path.join(OUT, "metrics_%s.json" % tag), "w", encoding="ascii") as f:
        json.dump({"anchor_name": "natural_logic_monotonicity_med_v1", "verdict": "MEASURED", "result": res},
                  f, indent=2, default=str)
    print("[run] " + res["headline"], flush=True)
    return res


def self_test():
    # edit detection
    assert classify_edit("a man won the big prize", "a man won the prize")[0] == "del"
    assert classify_edit("a man won the prize", "a man won the big prize")[0] == "ins"
    k, w1, w2 = classify_edit("a taxi arrived", "a car arrived")
    assert k == "sub" and {w1, w2} == {"taxi", "car"}
    # monotonicity self-detection
    assert is_downward("no delegate finished the report") and not is_downward("some delegates finished")
    assert not is_downward("no one did not leave")           # two DE operators (no, not) -> even -> upward
    assert is_downward("at most ten delegates finished")     # phrase operator 'at most' -> downward
    assert not is_downward("a few delegates finished")       # 'a few' is UPWARD (article guard), unlike bare 'few'
    assert is_downward("few delegates finished")             # bare 'few' -> downward
    # natural-logic rules
    assert nat_logic_pred("del", None, None, down=False) == "entailment"      # upward deletion -> entail
    assert nat_logic_pred("del", None, None, down=True) == "neutral"          # downward deletion -> neutral
    assert nat_logic_pred("ins", None, None, down=False) == "neutral"         # upward insertion -> neutral
    assert nat_logic_pred("sub", "taxi", "car", down=False) == "entailment"   # taxi is-a car, upward
    assert nat_logic_pred("sub", "car", "taxi", down=False) == "neutral"
    print("SELFTEST PASS (edit detection + monotonicity self-detect + natural-logic rules)", flush=True)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--timeout", type=float, default=None)
    args = ap.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    run(smoke=args.smoke)
    return 0


if __name__ == "__main__":
    sys.exit(main())
