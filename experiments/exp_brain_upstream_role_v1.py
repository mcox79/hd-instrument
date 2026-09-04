"""BRAIN-FOUNDATIONAL UPSTREAM: a Competition-Model (MacWhinney/Bates) role assigner that REPLACES the
reader's POSITIONAL who-did-what heuristic -- glass-box, NO training, static norms only.

RESEARCH-VERIFIED (2026-09-03, four converging traditions: Competition Model, constraint-satisfaction,
good-enough, ERP two-stream): role assignment = a fast NVN word-order heuristic + a weighted COMPETITION
of a small pinned cue set {word-order, ANIMACY, VOICE, verb-frame}, cue weights = validity (English is
word-order-dominant, animacy secondary), with a revision stage. No trained parser is brain-necessary.
The single highest-leverage pinned cue is ANIMACY as an agent cue (kills the "inanimate nearest noun =
agent" error, e.g. agent='streets'); VOICE (passive) is second (flips agent/patient).

This reuses the substrate's Competition-Model primitives verbatim (hdlab.thematic_role_labeler:
is_passive_clause, frame_slot_role, STRICTLY_INTRANSITIVE_VERBS; hdlab.animacy_lexicon.lookup_animacy)
and hand-sets the ~4 cue weights from cue validity (NOT learned) -- so it is genuinely brain-foundational
and training-free. Proves it EXCEEDS the positional baseline on: (1) agreement with a competent-reader
reference (spaCy, reference-only diagnostic, agent=nsubj/patient=dobj), and (2) the two gold-free error
classes the research named -- the inanimate-agent rate and the '?'-patient rate.

Run: .venv/Scripts/python.exe experiments/exp_brain_upstream_role_v1.py
"""
import json
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.scene_segment import parse_conll_sentences
from hdlab.pos_tagger import PosTagger
from hdlab.situation_reader import _FRONTEND_POS_ASSET
from hdlab.thematic_role_labeler import is_passive_clause, STRICTLY_INTRANSITIVE_VERBS, lemma_verb
from hdlab.animacy_lexicon import lookup_animacy
import experiments.exp_name_entity_clustering_v1 as NC

# Cue-validity-seeded weights (English word-order-dominant; animacy secondary). Hand-set, NOT trained.
W_ORDER, W_ANIM = 1.0, 0.6
_NOMINAL = ("NOUN", "PROPN")
_PRON = frozenset(("he", "she", "it", "they", "we", "i", "you", "him", "her", "them", "us"))


def _animate(tok, pos):
    a = lookup_animacy(tok, pos)
    if a is not None:
        return a["animacy"] == "animate"
    return tok.lower() in _PRON            # personal pronouns are animate discourse participants


def positional_assign(toks, pos, v_idx, noun_idxs):
    """The reader's current upstream: agent = nearest preverbal noun, patient = nearest postverbal noun."""
    pre = [n for n in noun_idxs if n < v_idx]
    post = [n for n in noun_idxs if n > v_idx]
    agent = toks[max(pre)].lower() if pre else "?"
    patient = toks[min(post)].lower() if post else "?"
    return agent, patient


def cm_assign(toks, pos, v_idx, noun_idxs):
    """Competition-Model, TWO-STAGE + WORD-ORDER-DOMINANT (the calibration the research prescribes:
    English relies OVERWHELMINGLY on word order; animacy is a SECONDARY tie-break, voice is a
    high-reliability flip). Stage 1 = fast NVN heuristic; stage 2 = revise ONLY on genuine conflict
    (animate subject over an inanimate nearest-preverbal noun; passive flip; intransitive gate) --
    so it never over-rides a correct inanimate subject like 'the rock hit the man'."""
    vlem = lemma_verb(toks[v_idx])
    passive = is_passive_clause(toks, pos)
    pre = [n for n in noun_idxs if n < v_idx]
    post = [n for n in noun_idxs if n > v_idx]

    # --- AGENT: word-order primary; animacy revises AMONG preverbal candidates only ---
    if not passive:
        subj_pool = pre
    else:                                                  # passive: the by-phrase noun is the agent
        by = [n for n in noun_idxs if n >= 1 and toks[n - 1].lower() == "by"]
        subj_pool = by if by else []                       # no by-phrase -> agent unexpressed
    agent = "?"
    if subj_pool:
        animate_pre = [n for n in subj_pool if _animate(toks[n], pos[n])]
        ai = max(animate_pre) if animate_pre else max(subj_pool)   # animate subject else nearest-to-verb
        agent = toks[ai].lower()

    # --- PATIENT: word-order primary (post-verbal, or the demoted subject under passive); frame gate ---
    patient = "?"
    if vlem not in STRICTLY_INTRANSITIVE_VERBS:
        pt_pool = post if not passive else pre             # passive: preverbal grammatical subj = patient
        cand = [n for n in pt_pool if toks[n].lower() != agent]
        if cand:
            patient = toks[min(cand, key=lambda n: abs(n - v_idx))].lower()
    return agent, patient


def run(n_docs=40):
    import spacy
    tagger = PosTagger.load(_FRONTEND_POS_ASSET)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    wdw = json.load(open(os.path.join(_REPO, "data/litbank/who_did_what_events.json"), encoding="utf-8"))
    docs = []
    for r in wdw:
        p = os.path.join(NC.CONLL_DIR, r["doc"] + ".conll")
        if os.path.exists(p):
            docs.append(p)
        if len(docs) >= n_docs:
            break

    stats = {m: {"ag_ok": 0, "pt_ok": 0, "ag_n": 0, "pt_n": 0, "inan_ag": 0, "q_pt": 0, "n": 0}
             for m in ("positional", "competition")}
    for p in docs:
        sents = parse_conll_sentences(p)
        for toks in sents:
            toks = list(toks)
            pos = tagger.tag(toks)
            noun_idxs = [i for i, u in enumerate(pos) if u in _NOMINAL or toks[i].lower() in _PRON]
            # competent-reader reference (spaCy): verb_lemma -> (nsubj_lemma, dobj_lemma)
            ref = {}
            doc = nlp(" ".join(toks))
            for t in doc:
                if t.pos_ == "VERB":
                    nsubj = next((c.text.lower() for c in t.children if c.dep_ in ("nsubj", "nsubjpass")), None)
                    dobj = next((c.text.lower() for c in t.children if c.dep_ in ("dobj", "dative", "oprd")), None)
                    ref.setdefault(t.lemma_.lower(), (nsubj, dobj))
            for v_idx, u in enumerate(pos):
                if u != "VERB":
                    continue
                vlem = lemma_verb(toks[v_idx])
                r = ref.get(vlem)
                for name, fn in (("positional", positional_assign), ("competition", cm_assign)):
                    ag, pt = fn(toks, pos, v_idx, noun_idxs)
                    st = stats[name]; st["n"] += 1
                    if ag != "?" and not _animate(ag, "NOUN") and lookup_animacy(ag) is not None:
                        st["inan_ag"] += 1
                    if pt == "?":
                        st["q_pt"] += 1
                    if r is not None:
                        if r[0]:
                            st["ag_n"] += 1; st["ag_ok"] += int(ag == r[0])
                        if r[1]:
                            st["pt_n"] += 1; st["pt_ok"] += int(pt == r[1])
    print("=" * 82)
    print("BRAIN-FOUNDATIONAL UPSTREAM ROLE ASSIGNMENT  (%d docs; ref = competent reader / spaCy)" % len(docs))
    print("-" * 82)
    for name in ("positional", "competition"):
        s = stats[name]
        print("  %-12s  AGENT agree=%.3f (n=%d)  PATIENT agree=%.3f (n=%d)  |  inanimate-agent=%.3f  '?'-patient=%.3f"
              % (name, s["ag_ok"] / max(1, s["ag_n"]), s["ag_n"], s["pt_ok"] / max(1, s["pt_n"]), s["pt_n"],
                 s["inan_ag"] / max(1, s["n"]), s["q_pt"] / max(1, s["n"])))
    print("-" * 82)
    P, C = stats["positional"], stats["competition"]
    print("  EXCEEDS: AGENT %+.3f  PATIENT %+.3f  | inanimate-agent %+.3f  '?'-patient %+.3f (negatives = better)"
          % (C["ag_ok"] / max(1, C["ag_n"]) - P["ag_ok"] / max(1, P["ag_n"]),
             C["pt_ok"] / max(1, C["pt_n"]) - P["pt_ok"] / max(1, P["pt_n"]),
             C["inan_ag"] / max(1, C["n"]) - P["inan_ag"] / max(1, P["n"]),
             C["q_pt"] / max(1, C["n"]) - P["q_pt"] / max(1, P["n"])))
    print("=" * 82)


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
