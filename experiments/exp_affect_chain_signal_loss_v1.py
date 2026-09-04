"""exp_affect_chain_signal_loss_v1 -- WHERE ALONG THE CHAIN DO WE LOSE SIGNAL, vs the brain?

The affect-answering chain, stage by stage:
   raw text -> POS tagger -> parse (frame shape) -> emotion lexicon -> psych-verb experiencer frame
            -> coreference -> per-character affect register -> "how does X feel" answer

This is an ORACLE-SUBSTITUTION LADDER: we swap each glass-box stage for its competent-reader oracle and
measure how much end-to-end accuracy each swap recovers -> the per-stage SIGNAL-LOSS BUDGET, and the
gap to the brain (the all-oracle ceiling ~ a competent reader).

Oracles (the "competent reader" upper bounds):
  - POS/parse:  spaCy en_core_web_sm (a strong tagger/parser; reference-only, NEVER on the glass-box path)
  - coref:      LitBank GOLD coref clusters (the annotation itself = the ceiling on binding)
  - emotion:    the shared gold lexicon (Warriner + NRC) -- same on both paths (not a swept stage)
  - experiencer role: the PINNED psych-verb frame -- same on both paths (its A/B lift is measured separately)

GOLD (competent-reader reference) affect set per doc = the reference pipeline's (character, emotion_cat,
valence) triples (spaCy POS + gold coref + shared lexicon + frame). Each rung's F1 is measured vs this
GOLD; the per-stage delta attributes the loss. The reference is hand-validated on a sample (see the note).

Glass-box, reference-only spaCy. Writes only to data/exp_affect_chain_signal_loss_v1/.
Run: .venv/Scripts/python.exe experiments/exp_affect_chain_signal_loss_v1.py --run [--docs N]
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, List, Optional

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.situation_reader import SituationReader  # noqa: E402
from hdlab.pos_tagger import PosTagger  # noqa: E402
from hdlab.coref import parse_litbank_conll  # noqa: E402
import experiments.exp_name_entity_clustering_v1 as NC  # noqa: E402
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer  # noqa: E402
from experiments.exp_situation_model_qa_v1 import _named_clusters, _norm, _PRONOUNS  # noqa: E402
import experiments.affect_register as AR  # noqa: E402
from experiments.affect_lexicon import AffectLexicon  # noqa: E402
from experiments.psych_verb_frames import PsychVerbFrames  # noqa: E402
import experiments.exp_affect_register_qa_v1 as QA  # noqa: E402

OUTDIR = os.path.join(REPO, "data/exp_affect_chain_signal_loss_v1")
CONLL_DIR = NC.CONLL_DIR
POS_ASSET = os.path.join(REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
_TAGGER = _LEX = _PVF = _NLP = None


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


def _spacy():
    global _NLP
    if _NLP is None:
        import spacy
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


# UD<-PTB coarse map for spaCy .tag_/.pos_ -> the UPOS the register expects
def _spacy_pos(sents):
    """spaCy POS per sentence (competent-tagger oracle), UPOS-style, aligned to the given tokenization."""
    import spacy
    nlp = _spacy()
    out = []
    for toks in sents:
        sd = spacy.tokens.Doc(nlp.vocab, words=list(toks))
        for _n, proc in nlp.pipeline:
            sd = proc(sd)
        out.append([t.pos_ for t in sd])
    return out


# ---------------------------------------------------------------------------
# GOLD-COREF canonicalizer (the coref ceiling) from LitBank clusters
# ---------------------------------------------------------------------------
def gold_coref_canonicalizer(path, gaz):
    """canon(surface, si) using LitBank GOLD coref clusters: cluster -> canonical name (longest
    non-pronoun head in the cluster); a mention's surface head (in its sentence) -> its cluster's name.
    Pronoun surfaces resolve via the pronoun mention in that sentence. This is the binding CEILING."""
    mentions, _n = parse_litbank_conll(path, name_gender_map=gaz)
    by_cluster = defaultdict(list)
    for m in mentions:
        by_cluster[m["cluster"]].append(m)
    cluster_name = {}
    for cid, ms in by_cluster.items():
        heads = [m["head"] for m in ms if _norm(m["head"]) and _norm(m["head"]) not in _PRONOUNS]
        if heads:
            cluster_name[cid] = max(heads, key=lambda h: len(_norm(h)))
    # index: (sent_idx, norm head) -> cluster ; and pronoun mentions per sentence
    head2cluster = {}
    pron_by_sent = defaultdict(list)
    for m in mentions:
        h = _norm(m["head"])
        if not h:
            continue
        head2cluster.setdefault((m["sent_idx"], h), m["cluster"])
        if m.get("is_pronoun") or h in _PRONOUNS:
            pron_by_sent[m["sent_idx"]].append((h, m["cluster"]))

    def canon(surface, si):
        s = _norm(surface)
        cid = head2cluster.get((si, s))
        if cid is not None and cid in cluster_name:
            return cluster_name[cid]
        if s in _PRONOUNS:
            # nearest pronoun mention of the same surface at/<= si
            for sj in range(si, -1, -1):
                for (p, c) in pron_by_sent.get(sj, []):
                    if p == s and c in cluster_name:
                        return cluster_name[c]
        return None
    return canon


# ---------------------------------------------------------------------------
# CYCLE 2: brain-faithful Centering SALIENCE fallback for UNRESOLVED experiencer pronouns.
# When the reader's coref returns None for a personal-pronoun experiencer, bind it to the gender-
# compatible PROTAGONIST (the most-frequently-mentioned named character of matching gender) -- the
# global-topic-salience level of Centering (Grosz-Joshi-Weinstein 1995), the research-recommended
# cheap fallback for low-confidence coref. Does NOT touch resolved pronouns (additive, low-regression).
# ---------------------------------------------------------------------------
_MASC = {"he", "him", "his", "himself"}
_FEM = {"she", "her", "hers", "herself"}
_PLUR = {"they", "them", "their", "theirs", "themselves"}


def centering_canonicalizer(path, gaz, reader_canon):
    """A GLASS-BOX Centering pronoun resolver for the experiencer (the brain-faithful mechanism the
    signal-loss study says the chain needs). Uses the reader's OWN mention stream (head/position/gender/
    subjecthood from parse_litbank_conll) -- NOT the gold coref CLUSTERS. Resolves an experiencer pronoun
    to a named character by the PINNED Centering hierarchy: (0) gender filter, (1) recency, (2)
    subjecthood tiebreak within the recent window (Grosz-Joshi-Weinstein 1995; Gordon-Grosz-Gilliom 1993).
    Falls back to the reader's coref only when Centering abstains (they/it). Prototype -- measures whether
    the mechanism closes the coref loss; a landed version belongs in the COREF organ."""
    mentions, _n = parse_litbank_conll(path, name_gender_map=gaz)

    def name_gender(head):
        return (gaz or {}).get(head.split()[0].lower()) if head else None
    named = []                                           # (gtok, sent_idx, is_subject, head, gender)
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        h = m["head"]
        g = m.get("name_gender") or name_gender(h)
        if g in ("masc", "fem"):                         # a person-name mention (candidate antecedent)
            named.append((m["gtok_start"], m["sent_idx"], bool(m.get("is_subject")), h, g))
    named.sort()

    def canon(surface, si):
        r = reader_canon(surface, si)
        if r is not None:
            return r                                     # FALLBACK-ONLY: trust the reader when it resolves
        s = _norm(surface)
        pg = "masc" if s in _MASC else "fem" if s in _FEM else None
        if pg is None:
            return None                                  # they/it/plural -> abstain
        cands = [(gt, msi, subj, head) for (gt, msi, subj, head, g) in named if msi <= si and g == pg]
        if not cands:
            return reader_canon(surface, si)
        # recency: consider the antecedents in the most recent sentence(s) up to si; prefer a SUBJECT.
        recent_sent = max(msi for (_gt, msi, _s, _h) in cands)
        window = [c for c in cands if c[1] >= recent_sent - 1]   # current + previous sentence (Cf window)
        subj_c = [c for c in window if c[2]]
        pick = max(subj_c or window, key=lambda c: c[0])          # most recent SUBJECT, else most recent
        return pick[3]
    return canon


def referent_former_canonicalizer(path, gaz, reader_canon):
    """PROTOTYPE of a MORE BRAIN-FOUNDATIONAL coref fix (the traced gap: the reader forms referents only
    for NAMED entities; 83.5% of emotion experiencers are UNNAMED common-noun entities it never clusters).
    The brain builds a discourse referent for EVERY entity (Gernsbacher 1990 Structure Building; discourse-
    model construction), linking coreferent mentions by cue coherence. This prototype forms referents over
    the mention stream (gold SPANS, as the reader already uses -- NOT gold cluster labels):
      - proper-NAME mentions -> a referent per normalized name (gaz-gendered head);
      - COMMON-NOUN mentions -> a referent per head-lemma + number (definite-NP head coherence: 'the man'
        ... 'the man' = one referent) -- the piece the reader is missing;
      - PRONOUNS -> most-recent number/gender-compatible referent (Centering recency + subjecthood).
    canonical label = the name, or the common-noun head lemma. This is the coref ORGAN's job; prototyped
    in experiments/ to measure the recovery ceiling of brain-faithful referent formation."""
    mentions, _n = parse_litbank_conll(path, name_gender_map=gaz)

    def hd(head):
        w = (head or "").strip().lower().split()
        return w[-1] if w else ""

    def name_gender(head):
        return (gaz or {}).get(head.split()[0].lower()) if head else None
    # form referents: (label, gtok, sent_idx, is_subject, gender, number)
    refs = []
    for m in mentions:
        if m.get("is_pronoun"):
            continue
        h = hd(m["head"])
        if not h:
            continue
        g = m.get("name_gender") or name_gender(m["head"])
        label = m["head"].split()[0].lower() if g in ("masc", "fem") else h   # name -> first name; else head lemma
        refs.append((label, m["gtok_start"], m["sent_idx"], bool(m.get("is_subject")),
                     g, m.get("number")))
    refs.sort(key=lambda r: r[1])
    # surface(head-lemma or name) -> label, per (sent) for direct hits
    def canon(surface, si):
        r0 = reader_canon(surface, si)
        if r0 is not None:
            return r0                                    # ADDITIVE: trust the reader wherever it resolves;
        s = _norm(surface)                               # only FORM a referent for what it abstains on
        if not s:
            return None
        # direct: a common-noun / name surface whose head-lemma matches a referent label seen by si
        cands = [r for r in refs if r[2] <= si]
        # personal-pronoun resolution (Centering recency + subjecthood + gender)
        if s in (_MASC | _FEM):
            pg = "masc" if s in _MASC else "fem"
            pc = [r for r in cands if r[4] == pg]
            if not pc:
                return reader_canon(surface, si)
            recent = max(r[2] for r in pc)
            win = [r for r in pc if r[2] >= recent - 1]
            subj = [r for r in win if r[3]]
            return max(subj or win, key=lambda r: r[1])[0]
        if s in _PLUR:
            return reader_canon(surface, si)
        # named / common-noun surface: match a referent by head-lemma / first-name (most recent by si)
        sl = s.split()[-1]
        direct = [r for r in cands if r[0] == sl or r[0] == s.split()[0]]
        if direct:
            return max(direct, key=lambda r: r[1])[0]
        return reader_canon(surface, si)
    return canon


def salience_fallback_canonicalizer(sm, reader_canon, gaz):
    names = _named_clusters(sm)                          # cluster -> canonical name
    freq = defaultdict(int)
    for e in sm.entities:
        if e.cluster in names:
            freq[e.cluster] += len(getattr(e, "heads", []) or [1])
    # gender per named cluster from the gazetteer (best-effort; None = unknown)
    def _gender(name):
        g = (gaz or {}).get(name.split()[0].lower()) if gaz else None
        return g
    ranked = sorted(names.items(), key=lambda kv: -freq.get(kv[0], 0))
    prot_masc = next((nm for _c, nm in ranked if _gender(nm) == "masc"), None)
    prot_fem = next((nm for _c, nm in ranked if _gender(nm) == "fem"), None)
    prot_any = ranked[0][1] if ranked else None

    def canon(surface, si):
        r = reader_canon(surface, si)
        if r is not None:
            return r
        s = _norm(surface)
        if s in _MASC and prot_masc:
            return prot_masc
        if s in _FEM and prot_fem:
            return prot_fem
        if s in _PLUR:
            return None                                  # plural -> ambiguous, do not guess
        return None
    return canon


# ---------------------------------------------------------------------------
# build a register under a chosen (pos_source, canon_source)
# ---------------------------------------------------------------------------
def build_affects(sents, pos, canon):
    aff = AR.extract_affect(sents, pos, _lex(), pvf=_pvf())
    AR.bind_experiencers(aff, canon)
    return aff


def _triples(affects, kinds=None):
    """(canonical-character, emotion_cat_or_sign) triples for a set of affects, reliable slice by default."""
    out = set()
    for a in affects:
        if kinds is not None and a.kind not in kinds:
            continue
        c = a.experiencer_canonical
        if not c or c == "?" or _norm(c) in _PRONOUNS:
            continue
        key = (_norm(c), a.emotion_cat or ("val%+d" % (a.valence_sign or 0)))
        out.add(key)
    return out


def _f1(pred: set, gold: set):
    tp = len(pred & gold)
    p = tp / len(pred) if pred else None
    r = tp / len(gold) if gold else None
    f = (2 * p * r / (p + r)) if (p and r) else 0.0
    return round(p or 0, 4), round(r or 0, 4), round(f, 4)


# ---------------------------------------------------------------------------
# the ladder
# ---------------------------------------------------------------------------
def run(docs, max_docs=None):
    gaz = load_given_gazetteer()
    RK = QA.RELIABLE_KINDS
    # accumulate micro F1 over docs
    agg = defaultdict(lambda: [0, 0, 0])   # rung -> [tp, pred, gold]
    detect = [0, 0]                        # glass-box detected / reference detected (recall of constructions)
    coref_bind = [0, 0, 0]                 # [n_exp_mentions, reader==gold, glassbox_reader_resolved]
    n = 0
    used = docs if max_docs is None else docs[:max_docs]
    for doc in used:
        path = os.path.join(CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        n += 1
        reader = SituationReader(gaz=gaz)
        sm = reader.read(path)
        sents = QA._conll_sents(path)
        fpos = [_tagger().tag(list(t)) for t in sents]
        spos = _spacy_pos(sents)
        reader_canon, _names = QA.make_canonicalizer(sm)
        gold_canon = gold_coref_canonicalizer(path, gaz)
        salience_canon = salience_fallback_canonicalizer(sm, reader_canon, gaz)
        centering_canon = centering_canonicalizer(path, gaz, reader_canon)
        referent_canon = referent_former_canonicalizer(path, gaz, reader_canon)
        import experiments.discourse_referents as _DR
        _rm = _DR.build_model(path, gaz, parse_litbank_conll)
        referent_model_canon = lambda surf, si, _rc=reader_canon, _m=_rm: _m.canon(surf, si, _rc)

        # rungs: (pos, canon)
        rungs = {
            "G0_glassbox": (fpos, reader_canon),
            "G1_spacyPOS": (spos, reader_canon),
            "G1b_salienceCoref": (fpos, salience_canon),   # CYCLE 2a: crude salience fallback (was a wash)
            "G1c_centeringCoref": (fpos, centering_canon), # CYCLE 2b: proper Centering resolver (prototype)
            "G1e_referentFormer": (fpos, referent_canon),  # CYCLE 3: naive head-match referent former
            "G1f_referentModel": (fpos, referent_model_canon),  # CYCLE 3b: faithful (definiteness+modifiers+recency)
            "G2_goldCoref": (fpos, gold_canon),
            "G3_ceiling": (spos, gold_canon),
        }
        aff = {k: build_affects(sents, pos, canon) for k, (pos, canon) in rungs.items()}
        gold = _triples(aff["G3_ceiling"], RK)     # competent-reader reference
        for k in rungs:
            pred = _triples(aff[k], RK)
            tp = len(pred & gold)
            a = agg[k]; a[0] += tp; a[1] += len(pred); a[2] += len(gold)

        # detection recall: emotion constructions (by sent+emotion_word) glass-box vs reference-POS
        gb_cons = {(a.sent_idx, a.emotion_word, a.kind) for a in aff["G0_glassbox"]}
        ref_cons = {(a.sent_idx, a.emotion_word, a.kind) for a in aff["G1_spacyPOS"]}
        detect[0] += len(gb_cons & ref_cons); detect[1] += len(ref_cons)

        # coref-binding: on affect experiencer mentions, does reader-coref agree with GOLD coref?
        for a in aff["G0_glassbox"]:
            surf = a.experiencer
            if not surf or _norm(surf) == "?":
                continue
            g = gold_canon(surf, a.sent_idx)
            if g is None:
                continue                         # no gold cluster for this mention -> not scorable
            coref_bind[0] += 1
            r = reader_canon(surf, a.sent_idx)
            coref_bind[1] += int(r is not None and _norm(r) == _norm(g))

    def prf(k):
        tp, pr, gd = agg[k]
        p = round(tp / pr, 4) if pr else None
        r = round(tp / gd, 4) if gd else None
        f = round(2 * p * r / (p + r), 4) if (p and r) else None
        return {"precision": p, "recall": r, "f1": f, "tp": tp, "pred": pr, "gold": gd}

    res = {
        "n_docs": n,
        "ladder": {k: prf(k) for k in ("G0_glassbox", "G1_spacyPOS", "G1b_salienceCoref",
                                       "G1c_centeringCoref", "G1e_referentFormer", "G1f_referentModel", "G2_goldCoref", "G3_ceiling")},
        "detection_recall_vs_spacyPOS": round(detect[0] / detect[1], 4) if detect[1] else None,
        "coref_binding_vs_gold": {"n_exp_mentions": coref_bind[0],
                                  "reader_agrees_gold": coref_bind[1],
                                  "acc": round(coref_bind[1] / coref_bind[0], 4) if coref_bind[0] else None},
    }
    # signal-loss attribution (F1 deltas from the ceiling)
    L = res["ladder"]
    ceil = L["G3_ceiling"]["f1"] or 0
    res["signal_loss_budget"] = {
        "ceiling_f1_competent_reader": ceil,
        "glassbox_f1": L["G0_glassbox"]["f1"],
        "total_loss_vs_ceiling": round(ceil - (L["G0_glassbox"]["f1"] or 0), 4),
        "recovered_by_spacyPOS_alone": round((L["G1_spacyPOS"]["f1"] or 0) - (L["G0_glassbox"]["f1"] or 0), 4),
        "recovered_by_salience_fallback": round((L["G1b_salienceCoref"]["f1"] or 0) - (L["G0_glassbox"]["f1"] or 0), 4),
        "recovered_by_centering_resolver": round((L["G1c_centeringCoref"]["f1"] or 0) - (L["G0_glassbox"]["f1"] or 0), 4),
        "recovered_by_goldCoref_alone": round((L["G2_goldCoref"]["f1"] or 0) - (L["G0_glassbox"]["f1"] or 0), 4),
        "note": "each 'recovered_by_X_alone' swaps ONE stage to its oracle from the glass-box baseline; "
                "the sum can differ from the total (interactions). ceiling = both oracles.",
    }
    return res


def trace_coref_loss(docs, max_docs=None):
    """TRACE what happens in the dominant (coref) loss: decompose each scorable affect-experiencer
    mention into interpretable buckets so we know WHY the reader binds it wrong 62% of the time.
    Buckets: surface type (personal pronoun / named / other); reader outcome (agree / abstain(None) /
    wrong-name); whether the GOLD canonical is a person-NAME vs a COMMON-NOUN cluster head (a naming
    mismatch, not a binding error); and, for wrong/abstain pronouns, whether a gender-compatible named
    antecedent even existed (recoverable vs not)."""
    gaz = load_given_gazetteer()
    B = defaultdict(int)
    used = docs if max_docs is None else docs[:max_docs]

    def is_person_name(h):
        return bool(h) and (gaz or {}).get(h.split()[0].lower()) in ("masc", "fem")
    for doc in used:
        path = os.path.join(CONLL_DIR, doc + ".conll")
        if not os.path.exists(path):
            continue
        reader = SituationReader(gaz=gaz)
        sm = reader.read(path)
        sents = QA._conll_sents(path)
        fpos = [_tagger().tag(list(t)) for t in sents]
        reader_canon, _n = QA.make_canonicalizer(sm)
        gold_canon = gold_coref_canonicalizer(path, gaz)
        aff = build_affects(sents, fpos, reader_canon)
        # per-doc named antecedents for the recoverability check
        ments, _ = parse_litbank_conll(path, name_gender_map=gaz)
        named = [(m["gtok_start"], m["sent_idx"], (m.get("name_gender") or (gaz or {}).get(m["head"].split()[0].lower())))
                 for m in ments if not m.get("is_pronoun") and is_person_name(m["head"])]
        for a in aff:
            surf = a.experiencer
            if not surf or _norm(surf) == "?":
                continue
            g = gold_canon(surf, a.sent_idx)
            if g is None:
                B["gold_none_unscorable"] += 1
                continue
            B["scorable"] += 1
            s = _norm(surf)
            styp = ("pron_pers" if s in (_MASC | _FEM) else "pron_plur_it" if s in _PLUR
                    else "named" if is_person_name(surf) else "other_np")
            B["surf_" + styp] += 1
            gold_is_name = is_person_name(g)
            B["goldtype_" + ("name" if gold_is_name else "commonnoun")] += 1
            r = reader_canon(surf, a.sent_idx)
            if r is not None and _norm(r) == _norm(g):
                B["outcome_agree"] += 1
            elif r is None:
                B["outcome_abstain"] += 1
                B["abstain_" + ("goldNAME" if gold_is_name else "goldCOMMON")] += 1
                if styp == "pron_pers":
                    pg = "masc" if s in _MASC else "fem"
                    avail = any(g2 == pg and msi <= a.sent_idx for (_gt, msi, g2) in named)
                    B["abstain_pron_" + ("antecedent_avail" if avail else "no_antecedent")] += 1
            else:
                B["outcome_wrongname"] += 1
                B["wrong_" + ("goldNAME" if gold_is_name else "goldCOMMON")] += 1
    return dict(B)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--trace", action="store_true")
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--docs", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        docs = QA.load_docs(3)
        res = run(docs, max_docs=3)
        print(json.dumps(res, indent=2))
        print("SELF-TEST PASS")
        return
    if args.trace:
        docs = QA.load_docs(args.docs)
        tr = trace_coref_loss(docs, max_docs=args.docs)
        os.makedirs(OUTDIR, exist_ok=True)
        with open(os.path.join(OUTDIR, "coref_loss_trace.json"), "w", encoding="ascii") as f:
            json.dump(tr, f, indent=2)
        sc = tr.get("scorable", 0) or 1
        print("=" * 70)
        print("COREF-LOSS TRACE (scorable experiencer mentions = %d)" % tr.get("scorable", 0))
        print("=" * 70)
        print("SURFACE type of the experiencer:")
        for k in ("surf_pron_pers", "surf_pron_plur_it", "surf_named", "surf_other_np"):
            print("  %-22s %4d  (%.1f%%)" % (k, tr.get(k, 0), 100 * tr.get(k, 0) / sc))
        print("GOLD canonical type:")
        for k in ("goldtype_name", "goldtype_commonnoun"):
            print("  %-22s %4d  (%.1f%%)" % (k, tr.get(k, 0), 100 * tr.get(k, 0) / sc))
        print("READER OUTCOME:")
        for k in ("outcome_agree", "outcome_abstain", "outcome_wrongname"):
            print("  %-22s %4d  (%.1f%%)" % (k, tr.get(k, 0), 100 * tr.get(k, 0) / sc))
        print("ABSTAIN breakdown:", {k: v for k, v in tr.items() if k.startswith("abstain_")})
        print("WRONG-NAME breakdown:", {k: v for k, v in tr.items() if k.startswith("wrong_")})
        print("gold_none_unscorable:", tr.get("gold_none_unscorable", 0))
        return
    docs = QA.load_docs(args.docs)
    res = run(docs, max_docs=args.docs)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "metrics.json"), "w", encoding="ascii") as f:
        json.dump(res, f, indent=2)
    print("=" * 92)
    print("AFFECT CHAIN SIGNAL-LOSS LADDER (n_docs=%d)" % res["n_docs"])
    print("=" * 92)
    for k in ("G0_glassbox", "G1_spacyPOS", "G1b_salienceCoref", "G1c_centeringCoref", "G1e_referentFormer", "G1f_referentModel", "G2_goldCoref", "G3_ceiling"):
        r = res["ladder"][k]
        print("  %-18s F1=%s (P=%s R=%s)  [tp=%d pred=%d gold=%d]" % (
            k, r["f1"], r["precision"], r["recall"], r["tp"], r["pred"], r["gold"]))
    sl = res["signal_loss_budget"]
    print("\nSIGNAL-LOSS BUDGET (F1):")
    print("  competent-reader ceiling = %s ; glass-box = %s ; total loss = %s" % (
        sl["ceiling_f1_competent_reader"], sl["glassbox_f1"], sl["total_loss_vs_ceiling"]))
    print("  recovered by spaCy POS alone       = %s" % sl["recovered_by_spacyPOS_alone"])
    print("  recovered by SALIENCE fallback     = %s  (CYCLE 2a: crude protagonist -- was a wash)" % sl["recovered_by_salience_fallback"])
    print("  recovered by CENTERING resolver    = %s  (CYCLE 2b: proper Centering, prototype)" % sl["recovered_by_centering_resolver"])
    print("  recovered by GOLD coref alone      = %s  (coref-organ ceiling)" % sl["recovered_by_goldCoref_alone"])
    print("\n  detection recall (constructions) glass-box vs spaCy-POS = %s" % res["detection_recall_vs_spacyPOS"])
    cb = res["coref_binding_vs_gold"]
    print("  coref-binding: reader agrees GOLD coref on %d/%d experiencer mentions = %s" % (
        cb["reader_agrees_gold"], cb["n_exp_mentions"], cb["acc"]))
    print("\nwrote", os.path.relpath(os.path.join(OUTDIR, "metrics.json"), REPO))


if __name__ == "__main__":
    main()
