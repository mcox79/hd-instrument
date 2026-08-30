"""Extraction helpers for the force-dynamic reader's LITERALNESS gate
   (problem: the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate).

Draws clauses headed by a PHYSICALLY-CAPABLE force-dynamic verb from MODERN corpora, so the gate can
be scored for FIRE-PRECISION (does the force-dynamic reader engage only on LITERAL physical events?).

CORPORA (both MODERN -- the brief flags the McGuffey age confound; neither is used):
  * UD-EWT (Universal Dependencies English Web Treebank) -- modern web text, GOLD dependency parses
    (extraction without a parser confound). Figurative-heavy -> the NEGATIVE-rich source.
  * MCScript2 -- modern crowd-sourced everyday-activity narratives (renovating a room, baking ...),
    physical-event-rich -> the LITERAL-POSITIVE-rich source. Parsed with spaCy en_core_web_sm.

VERB SET (PHYS_FORCE_VERBS): force-dynamic verbs that CAN denote a literal physical force event --
DERIVED (not a hand list), so it GENERALIZES: the hdlab force lexicon (FrameNet Causation family)
INTERSECTED with "has a physical WordNet verb sense" (lexname in motion/contact/change/body), UNION
the patient-tendency estimator's AMBIGUOUS_VERBS (the causative-inchoative labile set). These are the
verbs where LITERAL-vs-FIGURATIVE discrimination is the live problem ("break the branch" vs "break the
news"); the psychological-only CAUSE verbs (amuse, concern) never denote physical force and are
excluded (they are always the non-physical-force bucket, trivially abstained).

A "clause" = (sentence, verb_surface, verb_lemma, affector, patient, context_tokens). affector=nsubj
(None if intransitive); patient=obj else nsubj (unaccusative); context = the patient's amod + the
verb's directional/obl/particle markers (the exact cues the patient-tendency estimator reads).

ASCII only. Deterministic. No LLM. No hdlab writes.
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from functools import lru_cache
from typing import Dict, Iterator, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._patient_tendency import AMBIGUOUS_VERBS  # the labile set (already derived)

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
UDEWT = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
# KB_REFERENT: data/corpora/mcscript2/extracted/train-data.xml
MCSCRIPT = os.path.join(_REPO, "data", "corpora", "mcscript2", "extracted", "train-data.xml")

_PHYS_LEXNAMES = {"verb.motion", "verb.contact", "verb.change", "verb.body"}


@lru_cache(maxsize=1)
def phys_force_verbs() -> frozenset:
    """DERIVED verb set: force-lexicon verbs whose DOMINANT (most-frequent) WordNet sense is physical,
    UNION the labile set. Generalizes (no hand list; derived from WordNet frequency ranking). Cached.

    The DOMINANT-sense filter (not "has ANY physical sense") is brain-faithful (Giora graded salience:
    the salient/dominant sense governs) and it is what makes the population INFORMATIVE: it drops the
    bleached light/support verbs (get/take/make/do/give/let/see/call/keep) whose dominant sense is
    non-physical (possession/social/cognition) -- those flood any corpus and are a DIFFERENT error
    class (light-verb constructions), not the literal-vs-figurative-physical discrimination this gate
    targets. It KEEPS the verbs where that discrimination is the live problem: break ("branch" vs
    "news"), open ("door" vs "opened up"), move ("box" vs "into a house"), push/pull/roll/fall/crush..."""
    from nltk.corpus import wordnet as wn
    from hdlab.force_dynamics_typer import build_force_lexicon
    lex = build_force_lexicon()
    out = set(AMBIGUOUS_VERBS)
    for v in lex:
        if not v.isalpha():
            continue
        ss = wn.synsets(v, pos=wn.VERB)
        if ss and ss[0].lexname() in _PHYS_LEXNAMES:   # DOMINANT sense is physical
            out.add(v)
    return frozenset(out)


# ---------------------------------------------------------------------------
# UD-EWT (gold parse) extraction
# ---------------------------------------------------------------------------
def _read_conllu(path: str) -> Iterator[List[dict]]:
    sent: List[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if sent:
                    yield sent
                    sent = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            sent.append({"id": int(c[0]), "form": c[1], "lemma": c[2].lower(), "upos": c[3],
                         "head": int(c[6]), "dep": c[7]})
    if sent:
        yield sent


def _clause_from_gold(sent: List[dict], t: dict) -> Optional[dict]:
    kids = [x for x in sent if x["head"] == t["id"]]
    subj = next((x for x in kids if x["dep"] in ("nsubj", "nsubj:pass")), None)
    obj = next((x for x in kids if x["dep"] in ("obj", "dobj")), None)
    patient = obj if obj else subj
    affector = subj if obj else None
    if patient is None:
        return None
    pmods = [x["form"].lower() for x in sent if x["head"] == patient["id"] and x["dep"] == "amod"]
    ctx: List[str] = []
    for x in kids:
        if x["dep"] in ("obl", "obl:npmod", "advmod", "compound:prt"):
            ctx.append(x["form"].lower())
            for y in sent:
                if y["head"] == x["id"] and y["dep"] in ("case", "amod", "advmod", "compound:prt"):
                    ctx.append(y["form"].lower())
    return {
        "sent": " ".join(x["form"] for x in sent),
        "verb": t["form"].lower(), "lemma": t["lemma"],
        "affector": affector["form"].lower() if affector else "",
        "patient": patient["form"].lower(),
        "context": pmods + ctx,
        "source": "udewt",
    }


def iter_udewt_clauses(path: str = UDEWT) -> Iterator[dict]:
    verbs = phys_force_verbs()
    for sent in _read_conllu(path):
        for t in sent:
            if t["upos"] != "VERB" or t["lemma"] not in verbs:
                continue
            cl = _clause_from_gold(sent, t)
            if cl is not None:
                yield cl


# ---------------------------------------------------------------------------
# MCScript2 (spaCy parse) extraction
# ---------------------------------------------------------------------------
def _mcscript_texts(path: str = MCSCRIPT, max_texts: Optional[int] = None) -> List[str]:
    tree = ET.parse(path)
    texts = []
    for inst in tree.getroot().iter("instance"):
        tnode = inst.find("text")
        if tnode is not None and tnode.text:
            texts.append(" ".join(tnode.text.split()))
        if max_texts and len(texts) >= max_texts:
            break
    return texts


def _clause_from_spacy(sent, t) -> Optional[dict]:
    subj = next((c for c in t.children if c.dep_ in ("nsubj", "nsubjpass")), None)
    obj = next((c for c in t.children if c.dep_ in ("dobj", "obj")), None)
    patient = obj if obj else subj
    affector = subj if obj else None
    if patient is None:
        return None
    pmods = [c.text.lower() for c in patient.children if c.dep_ == "amod"]
    ctx: List[str] = []
    for c in t.children:
        if c.dep_ in ("prep", "advmod", "prt", "npadvmod"):
            ctx.append(c.text.lower())
            for g in c.children:
                if g.dep_ in ("pobj", "amod", "advmod", "case"):
                    ctx.append(g.text.lower())
    return {
        "sent": sent.text.strip(),
        "verb": t.text.lower(), "lemma": t.lemma_.lower(),
        "affector": affector.text.lower() if affector else "",
        "patient": patient.text.lower(),
        "context": pmods + ctx,
        "source": "mcscript",
    }


def iter_mcscript_clauses(path: str = MCSCRIPT, max_texts: Optional[int] = None, nlp=None) -> Iterator[dict]:
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    verbs = phys_force_verbs()
    for doc in nlp.pipe(_mcscript_texts(path, max_texts=max_texts), batch_size=32):
        for sent in doc.sents:
            for t in sent:
                if t.pos_ != "VERB" or t.lemma_.lower() not in verbs:
                    continue
                cl = _clause_from_spacy(sent, t)
                if cl is not None:
                    yield cl


# ---------------------------------------------------------------------------
# RACE (modern reading passages) -- a THIRD, HELD-OUT genre for the generalization test (different from
# UD-EWT web-forum and MCScript2 everyday-narrative). Raw article text; parsed with spaCy.
# ---------------------------------------------------------------------------
import json as _json  # noqa: E402
# KB_REFERENT: data/corpora/race/high_test.jsonl
RACE = os.path.join(_REPO, "data", "corpora", "race", "high_test.jsonl")


def _race_texts(path: str = RACE, max_texts: Optional[int] = None) -> List[str]:
    texts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                art = _json.loads(line).get("article", "")
            except Exception:
                continue
            if art:
                texts.append(" ".join(art.split()))
            if max_texts and len(texts) >= max_texts:
                break
    return texts


def iter_race_clauses(path: str = RACE, max_texts: Optional[int] = None, nlp=None) -> Iterator[dict]:
    import spacy
    if nlp is None:
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    verbs = phys_force_verbs()
    for doc in nlp.pipe(_race_texts(path, max_texts=max_texts), batch_size=16):
        for sent in doc.sents:
            for t in sent:
                if t.pos_ != "VERB" or t.lemma_.lower() not in verbs:
                    continue
                cl = _clause_from_spacy(sent, t)
                if cl is not None:
                    cl["source"] = "race"
                    yield cl


if __name__ == "__main__":
    print(f"PHYS_FORCE_VERBS: {len(phys_force_verbs())} verbs")
    n = 0
    for cl in iter_udewt_clauses():
        n += 1
    print(f"UD-EWT gated clauses: {n}")
