"""discourse_referents: a BRAIN-FOUNDATIONAL discourse-referent former for COMMON-NOUN entities.

THE GAP (traced in signal_loss_chain_analysis_2026-09-04.md): the reader's coref is proper-name-centric
and forms NO discourse referent for entities referred to only by common nouns ("the man", "the child") --
83.5% of narrative emotion experiencers. This is the dominant end-to-end signal loss (gold coref recovers
+0.43 F1). The brain builds a discourse referent for EVERY entity (Gernsbacher 1990 Structure Building),
linking coreferent mentions by DESCRIPTIVE-CONTENT match + the GIVENNESS hierarchy (definiteness):
  - an INDEFINITE NP ("a man") INTRODUCES a new referent (Gundel-Hedberg-Zacharski 1993; Heim 1982 file
    change semantics);
  - a DEFINITE NP ("the man", "his father") LINKS to an existing compatible referent (Poesio-Vieira 1998
    "direct anaphora" -- the dominant, tractable common-noun coref case);
  - compatibility = same head-noun lemma + number agreement + NON-CONTRADICTING modifiers ("the old man"
    != "the young man"); ties broken by RECENCY (the most recent compatible referent).
This is the cheap glass-box first step the mechanism-diff drill recommends (head-match + definiteness),
before bridging inference and cue-based retrieval. It ADDS to the reader's coref (reader-first): it only
forms/resolves referents the reader abstains on, so it cannot regress the reader's named-entity handling.

Prototype (this is the COREF ORGAN's job; built in experiments/ to measure the recovery ceiling and hand
strategy a validated diff). Glass-box, deterministic, NO LLM. ASCII.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
from typing import Dict, List, Optional

DEF_DET = {"the", "this", "that", "these", "those", "his", "her", "my", "your", "our", "their", "its"}
INDEF_DET = {"a", "an", "some", "any", "another", "no", "each", "every", "one"}
_MASC = {"he", "him", "his", "himself"}
_FEM = {"she", "her", "hers", "herself"}
_PLURP = {"they", "them", "their", "theirs", "themselves"}
_PRON = _MASC | _FEM | _PLURP | {"it", "its", "itself", "i", "me", "we", "us", "you"}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _hl(head: str) -> str:
    w = _norm(head).split()
    return w[-1] if w else ""


def read_global_tokens(path: str):
    """(gtok -> token text) and (gtok -> sent_idx) for a LitBank coref conll (col 3 = token)."""
    tok, sent = {}, {}
    g = si = 0
    seen = False
    for line in open(path, encoding="utf-8"):
        s = line.rstrip("\n")
        if not s.strip():
            if seen:
                si += 1; seen = False
            continue
        if s.startswith("#"):
            continue
        cols = s.split("\t")
        if len(cols) < 4:
            continue
        tok[g] = cols[3]; sent[g] = si; g += 1; seen = True
    return tok, sent


class Referent:
    __slots__ = ("rid", "label", "hl", "number", "gender", "mods", "last_gtok", "last_sent", "subj", "is_name")

    def __init__(self, rid, label, hl, number, gender, mods, gtok, sent, subj, is_name):
        self.rid = rid; self.label = label; self.hl = hl; self.number = number; self.gender = gender
        self.mods = set(mods); self.last_gtok = gtok; self.last_sent = sent; self.subj = subj; self.is_name = is_name


class ReferentModel:
    """Forms discourse referents from the mention stream + the raw tokens (for definiteness/modifiers),
    then canonicalizes an experiencer surface to a referent label. reader-first ADDITIVE."""

    def __init__(self, mentions, tok, sent, gaz):
        self.gaz = gaz or {}
        self.refs: List[Referent] = []
        self.by_gtok: Dict[int, Referent] = {}          # each non-pronoun mention gtok_start -> referent
        self._build(mentions, tok, sent)

    def _gender_of_name(self, head):
        return self.gaz.get(_norm(head).split()[0]) if head else None

    def _span(self, m, tok):
        return [tok.get(g, "") for g in range(m["gtok_start"], m["gtok_end"] + 1)]

    def _build(self, mentions, tok, sent):
        ms = sorted(mentions, key=lambda m: m["gtok_start"])
        rid = 0
        for m in ms:
            if m.get("is_pronoun") or _norm(m["head"]) in _PRON:
                continue
            span = self._span(m, tok)
            low = [w.lower() for w in span]
            det = low[0] if low else ""
            head = m["head"]; hl = _hl(head)
            if not hl:
                continue
            gname = self._gender_of_name(head)
            is_name = gname in ("masc", "fem")
            number = m.get("number") or ("plur" if head.lower().endswith("s") and not is_name else "sing")
            mods = {w for w in low[1:] if w not in DEF_DET and w not in INDEF_DET and _hl(w) != hl and w.isalpha()}
            g0 = m["gtok_start"]
            if is_name:
                fn = _norm(head).split()[0]
                cand = next((r for r in reversed(self.refs) if r.is_name and _norm(r.label).split()[0] == fn), None)
                if cand is None:
                    r = Referent(rid, head, hl, number, gname, mods, g0, m["sent_idx"], bool(m.get("is_subject")), True)
                    self.refs.append(r); rid += 1
                else:
                    if len(head) > len(cand.label):
                        cand.label = head
                    cand.last_gtok = g0; cand.last_sent = m["sent_idx"]; cand.subj = cand.subj or bool(m.get("is_subject"))
                    r = cand
            else:
                indef = det in INDEF_DET
                # candidate: same head-lemma, number-compatible, non-contradicting modifiers, most recent
                cand = None
                if not indef:
                    for rr in reversed(self.refs):
                        if rr.is_name or rr.hl != hl or rr.number != number:
                            continue
                        if mods and rr.mods and mods.isdisjoint(rr.mods) and (mods | rr.mods):
                            # both have modifiers and they do not overlap -> likely distinct (old vs young)
                            if len(mods & rr.mods) == 0:
                                continue
                        cand = rr; break
                if cand is None:
                    label = " ".join(span).strip() if len(span) <= 4 else head
                    r = Referent(rid, head if len(_norm(head).split()) == 1 else label, hl, number,
                                 None, mods, g0, m["sent_idx"], bool(m.get("is_subject")), False)
                    self.refs.append(r); rid += 1
                else:
                    cand.mods |= mods
                    cand.last_gtok = g0; cand.last_sent = m["sent_idx"]; cand.subj = cand.subj or bool(m.get("is_subject"))
                    r = cand
            self.by_gtok[g0] = r

    def _label(self, r: Referent) -> str:
        return r.label

    def canon(self, surface: str, si: int, reader_canon) -> Optional[str]:
        r0 = reader_canon(surface, si)
        if r0 is not None:
            return r0                                    # ADDITIVE: trust the reader wherever it resolves
        s = _norm(surface)
        if not s:
            return None
        seen = [r for r in self.refs if r.last_sent <= si]
        if s in _MASC or s in _FEM:
            pg = "masc" if s in _MASC else "fem"
            pc = [r for r in seen if r.gender == pg]
            if not pc:
                return None
            recent = max(r.last_sent for r in pc)
            win = [r for r in pc if r.last_sent >= recent - 1]
            subj = [r for r in win if r.subj]
            return self._label(max(subj or win, key=lambda r: r.last_gtok))
        if s in _PLURP or s in ("it", "its"):
            return None
        # named / common-noun surface: link to the most recent referent with matching head-lemma or name
        sl = _hl(s); fn = s.split()[0]
        cc = [r for r in seen if r.hl == sl or (r.is_name and _norm(r.label).split()[0] == fn)]
        if cc:
            return self._label(max(cc, key=lambda r: r.last_gtok))
        return None


def build_model(path, gaz, parse_litbank_conll):
    mentions, _n = parse_litbank_conll(path, name_gender_map=gaz)
    tok, sent = read_global_tokens(path)
    return ReferentModel(mentions, tok, sent, gaz)
