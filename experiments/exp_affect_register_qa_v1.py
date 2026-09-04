"""exp_affect_register_qa_v1 -- the AFFECT/EMOTION dimension, measured on real LitBank narrative.

Builds the missing EMOTION dimension of the situation model as a per-character AFFECT REGISTER over
the reader's OWN glass-box extraction (frontend POS tagger + coref; NO spaCy on the inference path, NO
external LLM), then answers affect-QA CI-separated over a most-recent-emotion-word floor with an
info-free SHUFFLED-CHARACTER twin LOSING.

  A) "How does X feel?"  (character-bound emotion identity)
       gold  = the emotion (category + valence) of X's explicit construction (grammar over the tokens)
       floor = MOST-RECENT-EMOTION-WORD: the nearest emotion word in the text, CHARACTER-BLIND (the
               trivial 'name the last emotion mentioned') -- recomputed per population.
       twin  = SHUFFLED emotion->character binding (the emotion set is right, the binding is deranged).
       +positive control: multi-character passages where the char-blind floor returns the WRONG
               character's emotion.
  VALENCE accuracy: does the register recover the +/- sign (vs the Warriner gold)?
  B) "How did X feel about Y?"  (stimulus-directed; psych verbs + of-PP)

UPSTREAM A/B (the psych-verb EXPERIENCER-LINKING frame): naive subject=experiencer vs the brain-
foundational psych_verb_frames (fear-type exp=subject, frighten-type exp=object). On object-experiencer
verbs the naive rule binds the emotion to the STIMULUS (often inanimate) instead of the character.

Also reports the glass-box register's extraction precision vs a spaCy ORACLE (reference-only, never
inference) and the located negative (INFERRED/unstated emotion needs the OCC-appraisal meaning channel).

Glass-box. Writes only to data/exp_affect_register_qa_v1/. Does NOT modify hdlab/.
Run: .venv/Scripts/python.exe experiments/exp_affect_register_qa_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_affect_register_qa_v1.py --run [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import copy
import json
import sys
from collections import defaultdict
from typing import Dict, List, Optional

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import SituationReader  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402
import experiments.exp_name_entity_clustering_v1 as NC  # noqa: E402
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer  # noqa: E402
from experiments.exp_situation_model_qa_v1 import _named_clusters, _norm, _PRONOUNS  # noqa: E402
import experiments.affect_register as AR  # noqa: E402
from experiments.affect_lexicon import AffectLexicon  # noqa: E402
from experiments.psych_verb_frames import PsychVerbFrames  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_affect_register_qa_v1")
WDW_GOLD = os.path.join(REPO, "data/litbank/who_did_what_events.json")
CONLL_DIR = NC.CONLL_DIR
POS_ASSET = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")

_TAGGER = None
_LEX = None
_PVF = None
RELIABLE_KINDS = ("copular_adj", "felt_noun", "psych_verb", "to_poss", "noun_poss")


def _tagger():
    global _TAGGER
    if _TAGGER is None:
        _TAGGER = PosTagger.load(POS_ASSET)
    return _TAGGER


def _lex():
    global _LEX
    if _LEX is None:
        _LEX = AffectLexicon.load()
    return _LEX


def _pvf():
    global _PVF
    if _PVF is None:
        _PVF = PsychVerbFrames.load()
    return _PVF


def _conll_sents(path: str) -> List[List[str]]:
    sents, cur = [], []
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            continue
        if not line.strip():
            if cur:
                sents.append(cur); cur = []
            continue
        cur.append(line.rstrip("\n").split("\t")[3])
    if cur:
        sents.append(cur)
    return sents


def load_docs(n: Optional[int]) -> List[str]:
    data = json.load(open(WDW_GOLD, encoding="utf-8"))
    docs = [rec["doc"] for rec in data]
    return docs[:n] if n else docs


def make_canonicalizer(sm):
    """Canonical entity naming (name -> cluster; pronoun -> coref), byte-identical to the goal QA cell."""
    names = _named_clusters(sm)
    head2canon: Dict[str, str] = {}
    for e in sm.entities:
        canon = names.get(e.cluster)
        if not canon:
            continue
        for h in e.heads:
            hn = _norm(h)
            if hn and hn not in _PRONOUNS:
                head2canon.setdefault(hn, canon)
    pron_by_sent: Dict[int, list] = defaultdict(list)
    for r in sm.coref_resolutions:
        canon = names.get(r.resolved_cluster)
        if canon:
            pron_by_sent[r.sent_idx].append((r.pronoun.lower(), canon))

    def canon(surface: str, si: int) -> Optional[str]:
        s = _norm(surface)
        if s in head2canon:
            return head2canon[s]
        if s in _PRONOUNS or surface.lower() in _PRONOUNS:
            for sj in range(si, -1, -1):
                for (p, c) in pron_by_sent.get(sj, []):
                    if p == surface.lower():
                        return c
        return None

    return canon, names


# ---------------------------------------------------------------------------
# read a doc + build the affect register
# ---------------------------------------------------------------------------
_DOC_CACHE: Dict[tuple, object] = {}


def read_doc(doc: str, gaz, pvf="default"):
    """Build the reader + affect register for a doc. `pvf`: 'default' = the psych-verb experiencer frame
    (the upstream brain-foundational fix); None = naive subject=experiencer (the A/B baseline)."""
    pv = _pvf() if pvf == "default" else pvf
    key = (doc, "frame" if pv is not None else "naive")
    if key in _DOC_CACHE:
        return _DOC_CACHE[key]
    path = os.path.join(CONLL_DIR, doc + ".conll")
    if not os.path.exists(path):
        _DOC_CACHE[key] = None
        return None
    reader = SituationReader(gaz=gaz)
    sm = reader.read(path)
    sents = _conll_sents(path)
    pos = [_tagger().tag(list(t)) for t in sents]
    affects = AR.extract_affect(sents, pos, _lex(), pvf=pv)
    canon, names = make_canonicalizer(sm)
    AR.bind_experiencers(affects, canon)
    reg = AR.AffectRegister(affects)
    # char-blind emotion-word occurrences (the floor population): every emotion word, in order
    emo_occ = []
    for si, toks in enumerate(sents):
        up = pos[si] if si < len(pos) else []
        for ti, w in enumerate(toks):
            uj = up[ti] if ti < len(up) else "X"
            if uj in ("ADJ", "NOUN", "VERB", "ADV") and _lex().is_emotion_word(w):
                emo_occ.append((si, ti, w.lower()))
    d = {"sm": sm, "sents": sents, "pos": pos, "affects": affects, "reg": reg,
         "canon": canon, "names": names, "emo_occ": emo_occ, "path": path}
    _DOC_CACHE[key] = d
    return d


# ---------------------------------------------------------------------------
# scoring helpers
# ---------------------------------------------------------------------------
def _cat_match(a: Optional[AR.Affect], gold_cat, gold_sign) -> int:
    if a is None:
        return 0
    if gold_cat is not None and a.emotion_cat is not None:
        return int(a.emotion_cat == gold_cat)
    # fall back to valence sign when a category is unavailable on either side
    return int(a.valence_sign is not None and a.valence_sign == gold_sign)


def _sign_match(a: Optional[AR.Affect], gold_sign) -> int:
    return int(a is not None and a.valence_sign is not None and a.valence_sign == gold_sign)


def floor_recent_emotion(d, before_si, before_ti):
    """MOST-RECENT-EMOTION-WORD floor (character-blind): the nearest emotion word STRICTLY BEFORE the
    question's construction (so it does NOT see the construction's own emotion word -- that would be
    circular). The trivial 'answer with the last emotion mentioned', ignoring WHO feels it.
    Returns (category, valence_sign) of that word."""
    best = None
    for (si, ti, w) in d["emo_occ"]:
        if (si, ti) < (before_si, before_ti):
            best = w
        else:
            break
    if best is None:
        return None, None
    return _lex().category(best), _lex().valence_sign(best)


# ---------------------------------------------------------------------------
# question builders (gold from the construction grammar)
# ---------------------------------------------------------------------------
def build_feel_questions(d) -> List[dict]:
    """A) 'How does X feel?' -- one per affect with a canonical experiencer. gold = the construction's
    emotion (category + valence sign). Non-circular vs the char-blind floor + the shuffled twin."""
    qs = []
    for a in d["affects"]:
        c = a.experiencer_canonical
        if not c or c == "?" or _norm(c) in _PRONOUNS:
            continue
        qs.append({"char": c, "gold_cat": a.emotion_cat, "gold_sign": a.valence_sign,
                   "kind": a.kind, "sent_idx": a.sent_idx, "tok": a.tok, "negated": a.negated})
    return qs


def shuffled_register(d, seed: int) -> "AR.AffectRegister":
    """Info-free twin: derange the emotion->character binding."""
    rng = np.random.default_rng(seed)
    affects = d["affects"]
    chars = [a.experiencer_canonical for a in affects]
    uniq = list(dict.fromkeys([c for c in chars if c and _norm(c) not in _PRONOUNS]))
    if len(uniq) < 2:
        perm = list(rng.permutation(chars))
    else:
        remap = {}
        for _ in range(2000):
            p = list(rng.permutation(uniq))
            if all(p[i] != uniq[i] for i in range(len(uniq))):
                remap = {uniq[i]: p[i] for i in range(len(uniq))}
                break
        perm = [remap.get(c, c) for c in chars]
    shuffled = []
    for a, c in zip(affects, perm):
        aa = copy.copy(a)
        aa.experiencer_canonical = c
        shuffled.append(aa)
    return AR.AffectRegister(shuffled)


# ---------------------------------------------------------------------------
# aggregation (paired per-doc cluster bootstrap, mirroring the goal QA cell)
# ---------------------------------------------------------------------------
def _cluster_boot(per_doc, docs, ia, ib, seed, B):
    dd = [d for d in docs if d in per_doc]
    if not dd:
        return [None, None]
    N = np.array([per_doc[d][0] for d in dd], float)
    A = np.array([per_doc[d][ia] for d in dd], float)
    Bk = np.array([per_doc[d][ib] for d in dd], float)
    rng = np.random.default_rng(seed + 7)
    nD = len(dd)
    diffs = np.empty(B)
    for b in range(B):
        s = rng.integers(0, nD, nD)
        na = N[s].sum()
        diffs[b] = (A[s].sum() / na - Bk[s].sum() / na) if na else 0.0
    diffs.sort()
    return [round(float(diffs[int(0.025 * B)]), 4), round(float(diffs[int(0.975 * B)]), 4)]


def _agg(rows, per_doc, docs, seed, B, keys, labels):
    def acc(k):
        v = [r[k] for r in rows if k in r]
        return round(sum(v) / len(v), 4) if v else None
    out = {"n": len(rows), "acc": {lab: acc(k) for k, lab in zip(keys, labels)}}
    ci = {}
    for j, k in enumerate(keys[1:], start=2):
        lo, hi = _cluster_boot(per_doc, docs, 1, j, seed, B)
        ci["model_minus_" + labels[keys.index(k)]] = [lo, hi]
        ci["sep_over_" + labels[keys.index(k)]] = bool(lo is not None and lo > 0)
    if rows:
        lo, hi = _cluster_boot(per_doc, docs, 1, 2, seed, B)
        out["ci_halfwidth_model_minus_floor"] = round((hi - lo) / 2, 4) if lo is not None else None
    out["ci"] = ci
    return out


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------
def run(docs, seed=20260904, n_boot=2000, n_twin=200):
    gaz = load_given_gazetteer()
    feel_rows, feel_rel_rows, val_rows = [], [], []
    per_doc = defaultdict(lambda: [0, 0, 0, 0])          # [n, model_ok, floor_ok, twin_ok] (category)
    per_doc_rel = defaultdict(lambda: [0, 0, 0, 0])
    per_doc_val = defaultdict(lambda: [0, 0, 0, 0])      # valence sign: [n, model, floor, twin]
    slice_counts = defaultdict(int)
    n_docs = 0
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        n_docs += 1
        reg = d["reg"]
        twin = shuffled_register(d, seed)
        for q in build_feel_questions(d):
            slice_counts[q["kind"]] += 1
            c = q["char"]
            mg = reg.feels(c)
            m_ok = _cat_match(mg, q["gold_cat"], q["gold_sign"])
            fcat, fsign = floor_recent_emotion(d, q["sent_idx"], q["tok"])
            f_ok = int((q["gold_cat"] is not None and fcat == q["gold_cat"]) or
                       (q["gold_cat"] is None and fsign is not None and fsign == q["gold_sign"]))
            tg = twin.feels(c)
            t_ok = _cat_match(tg, q["gold_cat"], q["gold_sign"])
            # valence-sign arm
            mv = _sign_match(mg, q["gold_sign"])
            fv = int(fsign is not None and fsign == q["gold_sign"])
            tv = _sign_match(tg, q["gold_sign"])
            row = {"doc": doc, "kind": q["kind"], "model_ok": m_ok, "floor_ok": f_ok, "twin_ok": t_ok}
            feel_rows.append(row)
            val_rows.append({"model_ok": mv, "floor_ok": fv, "twin_ok": tv})
            pd = per_doc[doc]; pd[0] += 1; pd[1] += m_ok; pd[2] += f_ok; pd[3] += t_ok
            pv = per_doc_val[doc]; pv[0] += 1; pv[1] += mv; pv[2] += fv; pv[3] += tv
            if q["kind"] in RELIABLE_KINDS:
                feel_rel_rows.append(row)
                pr = per_doc_rel[doc]; pr[0] += 1; pr[1] += m_ok; pr[2] += f_ok; pr[3] += t_ok
    res = {
        "n_docs": n_docs,
        "slice_counts": dict(slice_counts),
        "feel_all": _agg(feel_rows, per_doc, docs, seed, n_boot,
                         ("model_ok", "floor_ok", "twin_ok"),
                         ("model", "floor_recent_emotion", "twin_shuffled_char")),
        "feel_reliable": _agg(feel_rel_rows, per_doc_rel, docs, seed, n_boot,
                              ("model_ok", "floor_ok", "twin_ok"),
                              ("model", "floor_recent_emotion", "twin_shuffled_char")),
        "valence_sign": _agg(val_rows, per_doc_val, docs, seed, n_boot,
                             ("model_ok", "floor_ok", "twin_ok"),
                             ("model", "floor_recent_emotion", "twin_shuffled_char")),
        "seed": seed,
    }
    res["feel_all"]["twin_null_p95"] = _twin_null_p95(docs, gaz, seed, n_twin)
    return res


def _twin_null_p95(docs, gaz, seed, n_twin):
    cache = []
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        qs = build_feel_questions(d)
        if qs:
            cache.append((d, qs))
    if not cache:
        return None
    accs = []
    for t in range(n_twin):
        ok = tot = 0
        for (d, qs) in cache:
            tw = shuffled_register(d, seed + 1000 + t)
            for q in qs:
                tg = tw.feels(q["char"])
                ok += _cat_match(tg, q["gold_cat"], q["gold_sign"])
                tot += 1
        if tot:
            accs.append(ok / tot)
    accs.sort()
    return {"mean": round(float(np.mean(accs)), 4), "p95": round(float(accs[int(0.95 * len(accs))]), 4),
            "max": round(float(max(accs)), 4), "n_seeds": len(accs)}


# ---------------------------------------------------------------------------
# positive control: multi-character passages where the char-blind floor returns the WRONG character
# ---------------------------------------------------------------------------
def positive_control(docs, gaz):
    n = mr_fw = fr_mw = both = 0
    for doc in docs:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        qs = build_feel_questions(d)
        chars = list(dict.fromkeys(q["char"] for q in qs))
        if len(chars) < 2:
            continue
        reg = d["reg"]
        for q in qs:
            mg = reg.feels(q["char"])
            m_ok = _cat_match(mg, q["gold_cat"], q["gold_sign"])
            fcat, fsign = floor_recent_emotion(d, q["sent_idx"], q["tok"])
            f_ok = int((q["gold_cat"] is not None and fcat == q["gold_cat"]) or
                       (q["gold_cat"] is None and fsign is not None and fsign == q["gold_sign"]))
            n += 1
            mr_fw += int(m_ok and not f_ok)
            fr_mw += int(f_ok and not m_ok)
            both += int(m_ok and f_ok)
    return {"n_multi_char_feel": n, "model_right_charblind_wrong": mr_fw,
            "charblind_right_model_wrong": fr_mw, "both_right": both}


# ---------------------------------------------------------------------------
# UPSTREAM A/B: the psych-verb experiencer-linking frame vs naive subject=experiencer
# ---------------------------------------------------------------------------
_PERSONAL_PRON = {"he", "she", "they", "him", "her", "them", "i", "we", "you", "me", "us"}


def _animate_experiencer(a, namesf) -> bool:
    """The experiencer is ANIMATE (a real feeler): a personal pronoun, or resolves to a named character.
    The correctness proxy for psych-verb binding -- an inanimate stimulus ('the storm') is NOT animate."""
    return (AR._norm(a.experiencer or "") in _PERSONAL_PRON) or (_norm(a.experiencer_canonical or "") in namesf)


def experiencer_ab(docs, gaz):
    """UPSTREAM A/B on the psych-verb slice: does the emotion bind to an ANIMATE experiencer (pronoun /
    named character) rather than the inanimate stimulus? The frame corrects object-experiencer verbs
    ('the storm frightened her' -> her, not storm). Reports the animate-binding rate per arm overall and
    on the OBJECT-EXPERIENCER active subset (the class naive gets wrong), plus the corrections."""
    frame_anim = frame_n = naive_anim = naive_n = diff = 0
    oe_frame = oe_naive = oe_n = 0
    pvf = _pvf()
    for doc in docs:
        df = read_doc(doc, gaz, pvf="default")
        dn = read_doc(doc, gaz, pvf=None)
        if df is None or dn is None:
            continue
        namesf = set(_norm(v) for v in df["names"].values())
        naive_by_key = {}
        for a in dn["affects"]:
            if a.kind == "psych_verb":
                naive_by_key.setdefault((a.sent_idx, a.emotion_word), a)
        for a in df["affects"]:
            if a.kind != "psych_verb":
                continue
            frame_n += 1
            frame_anim += int(_animate_experiencer(a, namesf))
            na = naive_by_key.get((a.sent_idx, a.emotion_word))
            if na is not None:
                naive_n += 1
                naive_anim += int(_animate_experiencer(na, namesf))
                if AR._norm(na.experiencer or "") != AR._norm(a.experiencer or ""):
                    diff += 1
                if pvf.experiencer_position(a.emotion_word,
                                            has_object=True if pvf.klass(a.emotion_word) == "alternating" else None) == "object":
                    oe_n += 1
                    oe_frame += int(_animate_experiencer(a, namesf))
                    oe_naive += int(_animate_experiencer(na, namesf))
    return {"n_psych_verb": frame_n,
            "frame_animate_exp_rate": round(frame_anim / frame_n, 4) if frame_n else None,
            "naive_animate_exp_rate": round(naive_anim / naive_n, 4) if naive_n else None,
            "n_experiencer_corrections": diff,
            "object_experiencer_active_subset": {
                "n": oe_n, "frame_animate_exp": oe_frame, "naive_animate_exp": oe_naive}}


# ---------------------------------------------------------------------------
# AUTHORED experiencer A/B (the decisive upstream demonstration): constructed object-experiencer +
# subject-experiencer sentences with hand-set gold experiencers. The psych-verb frame binds the right
# character; naive subject=experiencer mis-binds every object-experiencer sentence. Non-circular
# (hand gold), can-fail. Object-experiencer actives are rare in LitBank, so this isolates the capability.
# ---------------------------------------------------------------------------
_EXP_AB_GOLD = [
    # (tokens, pos, gold_experiencer_low)  -- object-experiencer verbs: experiencer = OBJECT
    (["The", "dog", "frightened", "Mary", "."], ["DET", "NOUN", "VERB", "PROPN", "PUNCT"], "mary"),
    (["The", "storm", "terrified", "the", "children", "."], ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"], "children"),
    (["The", "news", "delighted", "John", "."], ["DET", "NOUN", "VERB", "PROPN", "PUNCT"], "john"),
    (["The", "noise", "annoyed", "her", "."], ["DET", "NOUN", "VERB", "PRON", "PUNCT"], "her"),
    (["The", "letter", "disappointed", "Elizabeth", "."], ["DET", "NOUN", "VERB", "PROPN", "PUNCT"], "elizabeth"),
    (["The", "sight", "amazed", "Tom", "."], ["DET", "NOUN", "VERB", "PROPN", "PUNCT"], "tom"),
    (["The", "gift", "pleased", "Anna", "."], ["DET", "NOUN", "VERB", "PROPN", "PUNCT"], "anna"),
    (["The", "thunder", "scared", "the", "boy", "."], ["DET", "NOUN", "VERB", "DET", "NOUN", "PUNCT"], "boy"),
    # subject-experiencer verbs: experiencer = SUBJECT (both arms should agree -> no regression)
    (["Mary", "feared", "the", "dog", "."], ["PROPN", "VERB", "DET", "NOUN", "PUNCT"], "mary"),
    (["John", "loved", "the", "garden", "."], ["PROPN", "VERB", "DET", "NOUN", "PUNCT"], "john"),
    (["Anna", "hated", "the", "noise", "."], ["PROPN", "VERB", "DET", "NOUN", "PUNCT"], "anna"),
    (["Tom", "dreaded", "the", "exam", "."], ["PROPN", "VERB", "DET", "NOUN", "PUNCT"], "tom"),
]


def authored_experiencer_ab() -> dict:
    """Frame vs naive on constructed psych-verb sentences with hand-set gold experiencers."""
    pvf = _pvf(); lex = _lex()
    f_ok = n_ok = n_oe = f_oe = n_se = f_se = 0
    n = 0
    for toks, pos, gold in _EXP_AB_GOLD:
        n += 1
        gf = AR.extract_affect([toks], [pos], lex, pvf=pvf)      # frame
        gn = AR.extract_affect([toks], [pos], lex, pvf=None)     # naive subject=exp
        af = next((a for a in gf if a.kind == "psych_verb"), None)
        an = next((a for a in gn if a.kind == "psych_verb"), None)
        # frame correctness
        f_ok += int(af is not None and af.experiencer.lower() == gold)
        n_ok += int(an is not None and an.experiencer.lower() == gold)
        # split by verb class
        pos_cls = pvf.experiencer_position(af.emotion_word) if af else "subject"
        if pos_cls == "object":
            n_oe += 1; f_oe += int(af is not None and af.experiencer.lower() == gold)
        else:
            n_se += 1; f_se += int(af is not None and af.experiencer.lower() == gold)
    return {"n": n, "frame_acc": round(f_ok / n, 4), "naive_acc": round(n_ok / n, 4),
            "object_exp": {"n": n_oe, "frame_correct": f_oe},
            "subject_exp": {"n": n_se, "frame_correct": f_se},
            "note": "object-experiencer sentences: the frame binds the OBJECT (experiencer); naive binds the "
                    "SUBJECT (the inanimate stimulus) and is wrong on every one. Subject-experiencer: both agree."}


# ---------------------------------------------------------------------------
# spaCy ORACLE (reference-only): extraction precision of the glass-box register
# ---------------------------------------------------------------------------
_NLP = None


def _spacy():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def oracle_extraction_quality(docs, gaz, max_docs=25):
    """Precision of the glass-box register's (experiencer-head, emotion-lemma) pairs vs a FAIR spaCy
    oracle that reads the SAME five constructions off an independent dependency parse (using the gold
    psych-verb class for the experiencer position -- a linguistic universal, not our implementation).
    Reference-only; spaCy never on the inference path. Reported on the RELIABLE slice (the constructions
    the oracle models) -- the noisy metaphor/adverb tail is excluded from the precision denominator."""
    import spacy
    nlp = _spacy()
    lex = _lex(); pvf = _pvf()
    COP = {"be", "feel", "seem", "look", "appear", "become", "grow", "remain", "sound", "get"}
    tp = fp = 0
    n = 0
    for doc in docs[:max_docs]:
        d = read_doc(doc, gaz)
        if d is None:
            continue
        n += 1
        oracle = set()
        for toks in d["sents"]:
            sd = spacy.tokens.Doc(nlp.vocab, words=list(toks))
            for _nm, proc in nlp.pipeline:
                sd = proc(sd)
            def nsubj_of(tok):
                """nsubj among tok's OWN children (predicate-adjective ROOT case), else of its head
                (acomp/xcomp copula case). spaCy makes 'happy' in 'she was happy' the ROOT with 'she' its
                own nsubj -- the earlier oracle looked only at the head and missed the whole copular slice."""
                s = [c for c in tok.children if c.dep_ in ("nsubj", "nsubjpass")]
                if not s and tok.head is not None and tok.head is not tok:
                    s = [c for c in tok.head.children if c.dep_ in ("nsubj", "nsubjpass")]
                return s

            for t in sd:
                lw = t.lemma_.lower()
                emo = lex.is_emotion_word(t.text) or lex.is_emotion_word(lw)
                # (1) copular / feel + emotion ADJ (or participle-ADJ tagged VERB) -> experiencer = subject
                if emo and t.pos_ == "ADJ":
                    subj = nsubj_of(t)
                    if subj:
                        oracle.add((subj[0].text.lower(), lw))
                # (2) psych VERB -> experiencer position from the GOLD class (subject-exp=nsubj, object-exp=dobj)
                if t.pos_ == "VERB" and pvf.is_psych_verb(lw):
                    pos = pvf.experiencer_position(lw, has_object=any(c.dep_ in ("dobj", "obj") for c in t.children)
                                                   if pvf.klass(lw) == "alternating" else None)
                    dep = ("nsubj", "nsubjpass") if pos == "subject" else ("dobj", "obj")
                    arg = [c for c in t.children if c.dep_ in dep]
                    if arg:
                        oracle.add((arg[0].text.lower(), lw))
                # emotion VERB not in the psych lexicon (rejoice/grieve/...) -> subject-experiencer
                elif emo and t.pos_ == "VERB":
                    subj = nsubj_of(t)
                    if subj:
                        oracle.add((subj[0].text.lower(), lw))
                # (3) affective ADVERB -> experiencer = nsubj of the modified verb
                if emo and t.pos_ == "ADV" and t.text.lower().endswith("ly") and t.head is not None:
                    subj = nsubj_of(t.head)
                    if subj:
                        oracle.add((subj[0].text.lower(), lw))
                # (4/5) emotion NOUN with possessor / "to X's N" -> experiencer = poss
                if emo and t.pos_ in ("NOUN", "PROPN"):
                    poss = [c for c in t.children if c.dep_ == "poss"]
                    if poss:
                        oracle.add((poss[0].text.lower(), lw))
        reg_pairs = {(_norm(a.experiencer), AR._lemma(a.emotion_word)) for a in d["affects"]
                     if a.kind in RELIABLE_KINDS}
        for p in reg_pairs:
            hit = any((_norm(p[0]) == _norm(o[0]) or _norm(p[0]) in _norm(o[0]) or _norm(o[0]) in _norm(p[0]))
                      and (p[1][:4] == AR._lemma(o[1])[:4]) for o in oracle)
            tp += int(hit); fp += int(not hit)
    prec = round(tp / (tp + fp), 4) if (tp + fp) else None
    return {"n_docs": n, "precision_vs_oracle": prec, "tp": tp, "fp": fp,
            "note": "FAIR spaCy oracle over the same 5 reliable constructions (gold psych class); "
                    "REFERENCE-ONLY, no spaCy at inference. Precision on the reliable slice only."}


# ---------------------------------------------------------------------------
# located negative: how much affect is INFERRED (unstated) vs EXPLICIT
# ---------------------------------------------------------------------------
def inferred_vs_explicit(docs, gaz, max_docs=None):
    """Coverage bound on the explicit tier: the fraction of events (actions) that carry NO explicit
    affect construction -> their emotional import (if any) would need the OCC-appraisal meaning channel
    (the located negative), not the glass-box explicit extractor."""
    n_events = n_affect = 0
    for doc in (docs if max_docs is None else docs[:max_docs]):
        d = read_doc(doc, gaz)
        if d is None:
            continue
        n_events += len(d["sm"].events)
        n_affect += len(d["affects"])
    return {"n_events": n_events, "n_explicit_affect": n_affect,
            "explicit_affect_per_event": round(n_affect / n_events, 4) if n_events else None,
            "note": "explicit affect is sparse relative to events; unstated action-implied emotion "
                    "('she slammed the door' -> anger) needs the OCC-appraisal meaning channel (located negative)."}


# ---------------------------------------------------------------------------
# self-test + main
# ---------------------------------------------------------------------------
def _selftest():
    docs = load_docs(3)
    res = run(docs, n_boot=300, n_twin=20)
    assert res["feel_all"]["n"] >= 1, res["feel_all"]
    gaz = load_given_gazetteer()
    ab = experiencer_ab(docs, gaz)
    aab = authored_experiencer_ab()
    print(json.dumps({"feel_all_n": res["feel_all"]["n"], "acc": res["feel_all"]["acc"],
                      "reliable_n": res["feel_reliable"]["n"], "reliable_acc": res["feel_reliable"]["acc"],
                      "slices": res["slice_counts"], "experiencer_ab": ab,
                      "authored_experiencer_ab": aab}, indent=2))
    print("SELF-TEST PASS")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--oracle-docs", type=int, default=25, dest="oracle_docs")
    ap.add_argument("--seed", type=int, default=20260904)
    args = ap.parse_args()
    if args.self_test or args.smoke:
        _selftest()
        return
    docs = load_docs(args.docs)
    gaz = load_given_gazetteer()
    res = run(docs, seed=args.seed)
    res["positive_control"] = positive_control(docs, gaz)
    res["experiencer_ab"] = experiencer_ab(docs, gaz)
    res["authored_experiencer_ab"] = authored_experiencer_ab()
    res["inferred_vs_explicit"] = inferred_vs_explicit(docs, gaz)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    # spaCy oracle (reference-only) LAST so it cannot lose the primary metrics
    res["oracle_extraction_quality"] = oracle_extraction_quality(docs, gaz, max_docs=args.oracle_docs)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)

    fa, fr, vs = res["feel_all"], res["feel_reliable"], res["valence_sign"]
    print("=" * 92)
    print("AFFECT/EMOTION dimension -- per-character affect register QA on LitBank (n_docs=%d)" % res["n_docs"])
    print("=" * 92)
    print("\nRELIABLE slice (copular_adj/felt_noun/psych_verb/to_poss/noun_poss)  n=%d" % fr["n"])
    print("   model=%s  floor[recent-emotion-word]=%s  twin[shuffled-char]=%s" % (
        fr["acc"]["model"], fr["acc"]["floor_recent_emotion"], fr["acc"]["twin_shuffled_char"]))
    print("   model-floor CI=%s sep=%s | model-twin CI=%s sep=%s" % (
        fr["ci"].get("model_minus_floor_recent_emotion"), fr["ci"].get("sep_over_floor_recent_emotion"),
        fr["ci"].get("model_minus_twin_shuffled_char"), fr["ci"].get("sep_over_twin_shuffled_char")))
    print("\nA) HOW DOES X FEEL? (category)  n=%d" % fa["n"])
    print("   model=%s floor=%s twin=%s | twin null p95=%s" % (
        fa["acc"]["model"], fa["acc"]["floor_recent_emotion"], fa["acc"]["twin_shuffled_char"],
        (fa.get("twin_null_p95") or {}).get("p95")))
    print("   model-floor CI=%s sep=%s | model-twin CI=%s sep=%s" % (
        fa["ci"].get("model_minus_floor_recent_emotion"), fa["ci"].get("sep_over_floor_recent_emotion"),
        fa["ci"].get("model_minus_twin_shuffled_char"), fa["ci"].get("sep_over_twin_shuffled_char")))
    print("\nVALENCE SIGN  n=%d  model=%s floor=%s twin=%s (model-floor CI=%s)" % (
        vs["n"], vs["acc"]["model"], vs["acc"]["floor_recent_emotion"], vs["acc"]["twin_shuffled_char"],
        vs["ci"].get("model_minus_floor_recent_emotion")))
    pc = res["positive_control"]
    print("\nPOSITIVE CONTROL (multi-char, n=%d): model-right & char-blind-floor-wrong=%d vs reverse=%d" % (
        pc["n_multi_char_feel"], pc["model_right_charblind_wrong"], pc["charblind_right_model_wrong"]))
    ab = res["experiencer_ab"]; aab = res["authored_experiencer_ab"]
    print("\nUPSTREAM A/B (psych-verb experiencer frame vs naive subject=exp):")
    print("   AUTHORED (n=%d): frame_acc=%s naive_acc=%s | object-exp %s | subject-exp %s" % (
        aab["n"], aab["frame_acc"], aab["naive_acc"], json.dumps(aab["object_exp"]), json.dumps(aab["subject_exp"])))
    print("   LitBank psych-verb n=%d: frame animate-exp=%s naive animate-exp=%s corrections=%d obj-exp-active=%s" % (
        ab["n_psych_verb"], ab["frame_animate_exp_rate"], ab["naive_animate_exp_rate"],
        ab["n_experiencer_corrections"], json.dumps(ab["object_experiencer_active_subset"])))
    oq = res["oracle_extraction_quality"]
    print("\nORACLE (spaCy, ref-only) extraction precision=%s (tp=%d fp=%d)" % (
        oq["precision_vs_oracle"], oq["tp"], oq["fp"]))
    iv = res["inferred_vs_explicit"]
    print("LOCATED NEGATIVE: explicit affect / event = %s (unstated emotion needs the meaning channel)" % (
        iv["explicit_affect_per_event"]))
    print("slice counts:", json.dumps(res["slice_counts"]))
    print("\nwrote", os.path.relpath(os.path.join(OUTDIR, "metrics.json"), REPO))


if __name__ == "__main__":
    main()
