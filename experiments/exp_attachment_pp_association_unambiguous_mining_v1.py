"""exp_attachment_pp_association_unambiguous_mining_v1 -- PP attachment (obl/nmod) as a CUE-BASED RETRIEVAL COMPETITION
over case-marked nominals, with the preposition association LEARNED FROM UNAMBIGUOUS READING (pri 94).

THE BRAIN'S MECHANISM (the opening move; PINNED where marked)
------------------------------------------------------------
A prepositional phrase is a CASE-MARKED nominal looking for a host. The reader decides its host the way it decides every
other attachment -- by cue competition (Bates & MacWhinney Competition Model; MacDonald, Pearlmutter & Seidenberg 1994
constraint satisfaction) over candidates RETRIEVED from working memory by cue match, activation decaying with distance
(Lewis & Vasishth 2005; Gibson DLT).  PINNED:
  1. CASE MARKING marks the nominal as oblique and opens the search (Pinker 1984; the Competition Model's case cue).
  2. The candidate set is EVERYTHING STILL OPEN that can license it -- verbs, predicate/attributive adjectives, and
     relational nouns -- not a fixed pair.  Retrieval is capacity-limited, so the set is bounded (K, swept).
  3. LEXICAL ASSOCIATION between the host and the preposition is the discriminating cue (Hindle & Rooth 1993 lexical
     association; Taraban & McClelland 1988 thematic expectation), and what competes is the CONTRAST between candidates,
     not an absolute number -- divisive normalisation into a population code (Carandini & Heeger 2012).
  4. It is LEARNED FROM UNAMBIGUOUS EXPERIENCE: the cases where only one host was available give clean evidence, and the
     ambiguous ones are then apportioned by the current estimate and re-estimated (Hindle & Rooth 1993's iterative
     reallocation; Ratnaparkhi 1998 mines exactly these from raw text -- 81.9 vs a 70.4 baseline, no treebank).
OURS (swept, never adopted): the retrieval cap K, the shrinkage m, the z-bin edges, the reallocation round count, the
reading volume.

WHAT WAS ON DISK BEFORE (measured, not recalled) -- the signal-loss trace
------------------------------------------------------------------------
`attachment_arm.pp_site` offers exactly TWO candidates (the nearest preceding VERB and the nearest preceding NOUN) and
only for a PP object that is a NOUN/PROPN sitting directly after DET/ADJ/NUM.  On UD-EWT test 700:
  * it fires on 253/477 gold obl (53%) and 195/534 gold nmod (37%);
  * of the fired cases the gold head is NEITHER offered candidate for 63 obl and 46 nmod;
  * so at most 339 of the 1011 gold obl+nmod tokens (33.5%) are decidable by the cue at all.
The dominant detection losses: the PP object is a PRON (109 nmod + 44 obl) or a NUM (36+19); the nominal run between the
preposition and its head contains a NOUN/PROPN/PRON (a compound or a possessive: "of Google 's new toolbar", "on your
hands") so the leftward scan stops before the preposition (98 obl + 77 nmod).  The dominant candidate-set losses: the
host is a predicate ADJECTIVE ("capable OF protecting", 24 obl) or a noun that is not the nearest one (23 nmod).
The association itself is mined from 6,000 UD-EWT training sentences: 2,230 verb|prep and 3,580 noun|prep cells, and
ambiguous sites are credited 0.5/0.5 FOREVER (Hindle & Rooth's initial estimate without their reallocation step).

WHAT THIS CELL BUILDS
---------------------
  * `pp_sites` -- case-marked-nominal detection driven by the PREPOSITION (the case marker), the object = the head of the
    nominal run after it (the arm's own NP-run convention), the candidates = the K nearest open hosts to the left of the
    preposition inside the sentence, typed V (verb) / A (adjective) / N (nominal).
  * `PPAssoc` -- P(preposition | host) as plastic COUNTS with Dirichlet shrinkage through a class backoff (verbs and
    adjectives by lemma -> their category; nouns by lemma -> their WordNet supersense, the foundation asset the typed
    selectional-preference organ already reads) to the preposition's own marginal.  `observe(...)` accrues online.
  * mining from reading (tokens + categories only, no treebank tree ever read): UNAMBIGUOUS sites (exactly one of the
    predicate slot / nominal slot present) give hard credit; ambiguous sites are reallocated by the current estimate for
    T rounds (Hindle & Rooth).  Corpus: UD-EWT train sentences (the arm's own reading slice) or Simple-English-Wikipedia
    tagged by the substrate's OWN category organ (`hdlab.lexical_categories`, count-based, live).
  * the READ-TIME cue: value = the z-bin of log P(p|h) - log max_{h' != h} P(p|h'), i.e. this candidate's association
    against its strongest competitor; the VALIDITY is learned by the arm's own soft counts exactly like every other cue.

NOT USED: spaCy, nltk, any supervised parser, any external LLM, any treebank tree during learning.  The UD treebank is
the measuring instrument only.  Categories on UD sentences are the gold UPOS column -- the same stand-in the rest of the
rung uses -- and on Simple-Wiki they are the substrate's own count-based category organ.

Run: .venv/Scripts/python.exe experiments/exp_attachment_pp_association_unambiguous_mining_v1.py --self-test
     ... --mine-simplewiki --lines 300000
     ... --full --cap 6000 --test-cap 700 --arms base,site,vol,cls,twin
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")

import argparse
import json
import math
import random
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir

from hdlab import attachment_arm as AA
from hdlab.graded_parser import single_root_marginals
from hdlab.thematic_role_labeler import lemma_verb
from tools.build_attachment_validities import (CORE_RELS, TEST, TRAIN, knowledge_free_teacher, sentences)

ANCHOR = "attachment_pp_association_unambiguous_mining_v1"


def module_provenance() -> dict:
    """WHICH hdlab is being measured. The working tree is shared with the strategy session, which lands other solvers'
    diffs into `hdlab/attachment_arm.py` while this cell runs -- so every metrics file records the exact bytes it was
    run against, and whether the pri-97 main-assertion cues are present in them."""
    import hashlib
    out = {}
    for p in ("hdlab/attachment_arm.py", "tools/build_attachment_validities.py"):
        try:
            b = open(os.path.join(REPO, p), "rb").read()
            out[p] = {"sha1": hashlib.sha1(b).hexdigest()[:12], "bytes": len(b)}
        except Exception as e:
            out[p] = {"error": str(e)}
    out["pri97_root_cues_present"] = hasattr(AA, "root_cue_values")
    out["cues_at_import"] = list(AA.CUES)
    return out
SIMPLEWIKI = os.path.join(REPO, "data", "corpora", "simplewiki", "simplewiki_clean_v1.txt")

# ---------------------------------------------------------------------------------------------------------------
# 1. CASE-MARKED NOMINAL DETECTION + CUE-BASED RETRIEVAL OF THE CANDIDATE HOSTS
# ---------------------------------------------------------------------------------------------------------------
# The nominal RUN after a preposition, using the arm's own convention (function_word_arcs.np_head_after) widened to the
# elements that actually occur inside an English NP: determiners, adjectives, numerals, adverbs (very), the possessive
# clitic, compound nouns and possessive pronouns.  The run HEAD is its last NOUN/PROPN, else its last PRON/NUM.
NP_RUN_X = frozenset({"DET", "ADJ", "NUM", "NOUN", "PROPN", "PRON", "PART", "ADV"})
NOM_HEAD = frozenset({"NOUN", "PROPN", "PRON", "NUM"})
SENT_END = frozenset({".", "!", "?", ";"})
PRED_HOST = frozenset({"VERB", "ADJ"})
NOM_HOST = frozenset({"NOUN", "PROPN", "PRON", "NUM"})


def _run_head(pos: Sequence[str], i: int) -> Optional[int]:
    """1-based head of the nominal run starting at 1-based i, or None. Last NOUN/PROPN, else last PRON/NUM."""
    n = len(pos)
    j = i
    while j <= n and pos[j - 1] in NP_RUN_X:
        j += 1
    nouns = [q for q in range(i, j) if pos[q - 1] in ("NOUN", "PROPN")]
    if nouns:
        return nouns[-1]
    other = [q for q in range(i, j) if pos[q - 1] in ("PRON", "NUM")]
    return other[-1] if other else None


def _is_nominal_host(pos: Sequence[str], q: int) -> bool:
    """A nominal candidate host is the HEAD of its own run (so a compound's modifier is not offered separately)."""
    if pos[q - 1] not in NOM_HOST:
        return False
    n = len(pos)
    if q < n and pos[q] in ("NOUN", "PROPN"):
        return False                      # a compound modifier: its run head is further right
    return True


def host_type(p: str) -> str:
    return "V" if p == "VERB" else "A" if p == "ADJ" else "N"


def pp_sites(toks: Sequence[str], pos: Sequence[str], k_cap: int = 6) -> List[Tuple[int, int, List[int]]]:
    """Every case-marked nominal: (prep_idx, object_head_idx, [candidate host indices, nearest first]), all 1-based.

    Structural, category-only, no gold: a preposition (ADP) opens a case-marked nominal whose head is the run head that
    follows it; the candidates are the open hosts to its LEFT inside the same sentence (a sentence-final mark closes the
    search), nearest first, capped at k_cap (capacity-limited retrieval)."""
    n = len(pos)
    out: List[Tuple[int, int, List[int]]] = []
    for k in range(1, n + 1):
        if pos[k - 1] != "ADP" or k == n:
            continue
        if pos[k] == "ADP":                      # "because of", "out of": the inner preposition carries the case
            continue
        if pos[k] not in NP_RUN_X:
            continue
        obj = _run_head(pos, k + 1)
        if obj is None or obj <= k:
            continue
        cands: List[int] = []
        for q in range(k - 1, 0, -1):
            p = pos[q - 1]
            if p == "PUNCT" and toks[q - 1] in SENT_END:
                break
            if p in PRED_HOST or _is_nominal_host(pos, q):
                cands.append(q)
                if len(cands) >= k_cap:
                    break
        if cands:
            out.append((k, obj, cands))
    return out


def mining_frame(toks: Sequence[str], pos: Sequence[str], k: int) -> Tuple[Optional[int], Optional[int]]:
    """Hindle & Rooth's two-slot frame at preposition k: the nearest PREDICATE host (verb or predicate adjective) and the
    nearest NOMINAL host to its left, stopping at a sentence boundary. Exactly one present = an UNAMBIGUOUS case."""
    pred = nom = None
    for q in range(k - 1, 0, -1):
        p = pos[q - 1]
        if p == "PUNCT" and toks[q - 1] in SENT_END:
            break
        if pred is None and p in PRED_HOST:
            pred = q
        if nom is None and _is_nominal_host(pos, q):
            nom = q
        if pred is not None and nom is not None:
            break
    return pred, nom


# ---------------------------------------------------------------------------------------------------------------
# 2. THE ASSOCIATION: P(preposition | host) as plastic counts with a class backoff
# ---------------------------------------------------------------------------------------------------------------
_MORPH = None


def host_key(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """<type>|<lemma>. Verbs through the arm's own verb lemmatiser; nouns/adjectives through the morphology organ."""
    global _MORPH
    t = host_type(pos[q - 1])
    w = toks[q - 1].lower()
    if t == "V":
        return "V|" + lemma_verb(toks[q - 1]).lower()
    if t == "N":
        if _MORPH is None:
            from hdlab import morphology as _m
            _MORPH = _m
        return "N|" + (_MORPH.morphy(w, "n") or w)
    return "A|" + w


def obj_class(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """The TYPE of the prepositional object -- its WordNet supersense (the same foundation table the typed
    selectional-preference organ reads), a numeral class, or 'unk'."""
    p = pos[q - 1]
    if p == "NUM":
        return "num"
    from hdlab.typed_selectional_preference import noun_supersense
    return noun_supersense(toks[q - 1]) or ("pron" if p == "PRON" else "unk")


def host_class(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """The BACKOFF class: verbs and adjectives back off to their category, nouns to their WordNet supersense (the
    foundation asset the typed selectional-preference organ reads -- Resnik-style type generalisation)."""
    t = host_type(pos[q - 1])
    if t != "N":
        return t
    from hdlab.typed_selectional_preference import noun_supersense
    ss = noun_supersense(toks[q - 1])
    return "N:" + (ss or "unk")


class PPAssoc:
    """P(preposition | host) held as COUNTS (plastic, never frozen); the probability is one pure function of them.

        P(p | h)   = (c[h][p]   + m1 * P(p | class(h))) / (d[h]   + m1)
        P(p | cls) = (cc[cls][p] + m2 * P(p))            / (dc[cls] + m2)
        P(p)       = (cp[p] + 0.5) / (tot + 1)

    Dirichlet shrinkage toward the next-coarser level -- the same shrinkage form the arm's own
    `strengths_from_arc_counts` uses toward the configuration's rate."""

    def __init__(self, m1: float = 5.0, m2: float = 20.0, use_class: bool = True, m3: float = 20.0, m4: float = 50.0):
        self.c: Dict[str, float] = defaultdict(float)     # "<type>|<lemma>|<prep>"
        self.d: Dict[str, float] = defaultdict(float)     # "<type>|<lemma>"
        self.cc: Dict[str, float] = defaultdict(float)    # "<class>|<prep>"
        self.dc: Dict[str, float] = defaultdict(float)    # "<class>"
        self.cp: Dict[str, float] = defaultdict(float)    # "<prep>"
        self.tot = 0.0
        # THEMATIC-EXPECTATION channel (Taraban & McClelland 1988; Ratnaparkhi 1998's fourth element): what KIND of
        # thing the prepositional phrase is ABOUT, given the host type and the preposition. "with a fork" after a verb
        # is an instrument; "with a garden" after a noun is a part. Typed (WordNet supersense), so it generalises the
        # way a thematic expectation does (McRae, Ferretti & Amyote 1997 role-as-feature-bundle).
        self.o: Dict[str, float] = defaultdict(float)     # "<htype>|<prep>|<objclass>"
        self.od: Dict[str, float] = defaultdict(float)    # "<htype>|<prep>"
        self.oc: Dict[str, float] = defaultdict(float)    # "<htype>|<objclass>"
        self.ocd: Dict[str, float] = defaultdict(float)   # "<htype>"
        self.og: Dict[str, float] = defaultdict(float)    # "<objclass>"
        self.otot = 0.0
        self.m1 = float(m1); self.m2 = float(m2); self.use_class = bool(use_class)
        self.m3 = float(m3); self.m4 = float(m4)
        self._cache: Dict[Tuple[str, str, str], float] = {}
        self._ocache: Dict[Tuple[str, str, str], float] = {}

    # ---- plasticity -------------------------------------------------------------------------------------------
    def observe(self, hkey: str, hcls: str, prep: str, w: float = 1.0, objclass: Optional[str] = None) -> None:
        """One comprehension outcome: host `hkey` was understood to license the case-marked phrase headed by `prep`."""
        self.c[hkey + "|" + prep] += w; self.d[hkey] += w
        self.cc[hcls + "|" + prep] += w; self.dc[hcls] += w
        self.cp[prep] += w; self.tot += w
        if objclass is not None:
            t = hkey.split("|", 1)[0]
            self.o[t + "|" + prep + "|" + objclass] += w; self.od[t + "|" + prep] += w
            self.oc[t + "|" + objclass] += w; self.ocd[t] += w
            self.og[objclass] += w; self.otot += w
            self._ocache.clear()
        self._cache.clear()

    def p_obj(self, htype: str, prep: str, objclass: str) -> float:
        """P(class of the prepositional object | host type, preposition), shrunk through P(class | host type) to the
        class's own marginal -- the typed thematic expectation of the phrase given who would license it."""
        key = (htype, prep, objclass)
        v = self._ocache.get(key)
        if v is not None:
            return v
        pg = (self.og.get(objclass, 0.0) + 0.5) / (self.otot + 1.0)
        pt = (self.oc.get(htype + "|" + objclass, 0.0) + self.m4 * pg) / (self.ocd.get(htype, 0.0) + self.m4)
        v = (self.o.get(htype + "|" + prep + "|" + objclass, 0.0) + self.m3 * pt) / (self.od.get(htype + "|" + prep, 0.0) + self.m3)
        self._ocache[key] = v
        return v

    # ---- the read ---------------------------------------------------------------------------------------------
    def p_prep(self, prep: str) -> float:
        return (self.cp.get(prep, 0.0) + 0.5) / (self.tot + 1.0)

    def p_given(self, hkey: str, hcls: str, prep: str) -> float:
        key = (hkey, hcls, prep)
        v = self._cache.get(key)
        if v is not None:
            return v
        pp = self.p_prep(prep)
        if self.use_class:
            pc = (self.cc.get(hcls + "|" + prep, 0.0) + self.m2 * pp) / (self.dc.get(hcls, 0.0) + self.m2)
        else:
            pc = pp
        v = (self.c.get(hkey + "|" + prep, 0.0) + self.m1 * pc) / (self.d.get(hkey, 0.0) + self.m1)
        self._cache[key] = v
        return v

    # ---- persistence ------------------------------------------------------------------------------------------
    def to_json(self) -> dict:
        return {"c": dict(self.c), "d": dict(self.d), "cc": dict(self.cc), "dc": dict(self.dc),
                "cp": dict(self.cp), "tot": self.tot, "m1": self.m1, "m2": self.m2, "use_class": self.use_class,
                "o": dict(self.o), "od": dict(self.od), "oc": dict(self.oc), "ocd": dict(self.ocd),
                "og": dict(self.og), "otot": self.otot, "m3": self.m3, "m4": self.m4,
                "computation": "P(prep|host) = (c + m1*P(prep|class))/(d + m1); class = UPOS for V/A, WordNet "
                               "supersense for N; P(objclass|htype,prep) = (o + m3*P(objclass|htype))/(od + m3); "
                               "mined from UNAMBIGUOUS reading (Hindle & Rooth 1993 / Ratnaparkhi 1998)"}

    @classmethod
    def from_json(cls, d: dict) -> "PPAssoc":
        self = cls(d.get("m1", 5.0), d.get("m2", 20.0), d.get("use_class", True), d.get("m3", 20.0), d.get("m4", 50.0))
        self.c = defaultdict(float, d["c"]); self.d = defaultdict(float, d["d"])
        self.cc = defaultdict(float, d["cc"]); self.dc = defaultdict(float, d["dc"])
        self.cp = defaultdict(float, d["cp"]); self.tot = d["tot"]
        self.o = defaultdict(float, d.get("o", {})); self.od = defaultdict(float, d.get("od", {}))
        self.oc = defaultdict(float, d.get("oc", {})); self.ocd = defaultdict(float, d.get("ocd", {}))
        self.og = defaultdict(float, d.get("og", {})); self.otot = d.get("otot", 0.0)
        return self

    def scramble(self, seed: int = 20260913) -> "PPAssoc":
        """INFORMATION-FREE TWIN: every host's preposition profile is reassigned to another host, keeping the counts,
        the density, the class table and the marginals identical -- only WHICH host has WHICH profile is destroyed."""
        rng = random.Random(seed)
        out = PPAssoc(self.m1, self.m2, self.use_class)
        hosts = sorted(self.d.keys())
        donor = list(hosts); rng.shuffle(donor)
        mp = dict(zip(hosts, donor))
        for k, v in self.c.items():
            h, p = k.rsplit("|", 1)
            out.c[mp.get(h, h) + "|" + p] = v
        for h, v in self.d.items():
            out.d[mp.get(h, h)] = v
        out.cc = defaultdict(float, self.cc); out.dc = defaultdict(float, self.dc)
        out.cp = defaultdict(float, self.cp); out.tot = self.tot
        # the thematic channel is destroyed the same way: the object-class profile of each (host type, preposition)
        # cell is reassigned to another cell, keeping every marginal and every count identical.
        cells = sorted(self.od.keys()); dcell = list(cells); rng.shuffle(dcell); mc = dict(zip(cells, dcell))
        for k, v in self.o.items():
            t, p, oc = k.split("|", 2)
            out.o[mc.get(t + "|" + p, t + "|" + p) + "|" + oc] = v
        out.od = defaultdict(float, self.od); out.oc = defaultdict(float, self.oc)
        out.ocd = defaultdict(float, self.ocd); out.og = defaultdict(float, self.og); out.otot = self.otot
        return out


# ---------------------------------------------------------------------------------------------------------------
# 3. MINING FROM READING -- unambiguous seed + Hindle & Rooth reallocation. No treebank tree is ever read.
# ---------------------------------------------------------------------------------------------------------------
def collect_instances(reading: Sequence[Tuple[Sequence[str], Sequence[str]]], k_cap: int = 6) -> List[dict]:
    """One record per preposition: the unambiguous host (if the frame offers exactly one) or the two competing ones."""
    out: List[dict] = []
    for toks, pos in reading:
        n = len(toks)
        for k in range(1, n + 1):
            if pos[k - 1] != "ADP" or k == n or pos[k] == "ADP" or pos[k] not in NP_RUN_X:
                continue
            if _run_head(pos, k + 1) is None:
                continue
            pred, nom = mining_frame(toks, pos, k)
            if pred is None and nom is None:
                continue
            obj = _run_head(pos, k + 1)
            prep = toks[k - 1].lower()
            rec = {"p": prep, "o": obj_class(toks, pos, obj) if obj else "unk"}
            for tag, q in (("pred", pred), ("nom", nom)):
                if q is not None:
                    rec[tag] = (host_key(toks, pos, q), host_class(toks, pos, q))
            out.append(rec)
    return out


def mine(reading, rounds: int = 2, m1: float = 5.0, m2: float = 20.0, use_class: bool = True,
         k_cap: int = 6, verbose: bool = False) -> Tuple[PPAssoc, dict]:
    """Hindle & Rooth 1993: seed on the UNAMBIGUOUS cases (only one host type available), then apportion the ambiguous
    ones by the CURRENT estimate and re-estimate. `rounds` = 0 gives the unambiguous-only seed."""
    inst = collect_instances(reading, k_cap)
    unamb = [r for r in inst if ("pred" in r) != ("nom" in r)]
    amb = [r for r in inst if ("pred" in r) and ("nom" in r)]
    A = PPAssoc(m1, m2, use_class)
    for r in unamb:
        h = r.get("pred") or r["nom"]
        A.observe(h[0], h[1], r["p"], 1.0, r.get("o"))
    stats = {"instances": len(inst), "unambiguous": len(unamb), "ambiguous": len(amb), "rounds": rounds}
    for _ in range(max(0, rounds)):
        B = PPAssoc(m1, m2, use_class)
        for r in unamb:
            h = r.get("pred") or r["nom"]
            B.observe(h[0], h[1], r["p"], 1.0, r.get("o"))
        for r in amb:
            hp, hn = r["pred"], r["nom"]; p = r["p"]; oc = r.get("o")
            a = A.p_given(hp[0], hp[1], p) * A.p_obj(hp[0].split("|", 1)[0], p, oc or "unk")
            b = A.p_given(hn[0], hn[1], p) * A.p_obj(hn[0].split("|", 1)[0], p, oc or "unk")
            w = a / (a + b) if (a + b) > 0 else 0.5
            B.observe(hp[0], hp[1], p, w, oc); B.observe(hn[0], hn[1], p, 1.0 - w, oc)
        A = B
        if verbose:
            print("   reallocation round done: %d host cells" % len(A.d), flush=True)
    stats["host_cells"] = len(A.d); stats["assoc_cells"] = len(A.c); stats["class_cells"] = len(A.dc)
    return A, stats


def simplewiki_reading(lines: int, maxlen: int = 40, skip: int = 0, log_every: int = 50000):
    """Simple-English-Wikipedia tagged by the SUBSTRATE'S OWN category organ (hdlab.lexical_categories: count-based
    emission/suffix/transition, forward-backward posterior -- the live categories rung). No external tagger."""
    from hdlab import lexical_categories as LC
    from hdlab.frontend import tokenize
    m = LC.get()
    n = 0
    with open(SIMPLEWIKI, encoding="utf-8") as f:
        for li, line in enumerate(f):
            if li < skip:
                continue
            if n >= lines:
                break
            toks = tokenize(line.strip())
            if not (4 <= len(toks) <= maxlen):
                continue
            n += 1
            if log_every and n % log_every == 0:
                print("   tagged %d lines" % n, flush=True)
            yield toks, m.tag(toks)


# ---------------------------------------------------------------------------------------------------------------
# 4. THE READ-TIME CUE -- the candidate competition, injected into the arm without editing hdlab/
# ---------------------------------------------------------------------------------------------------------------
Z_EDGES = (1.0, 0.3, -0.3, -1.0)          # swept operating point; never adopted from a brain number
Z_NAMES = ("w2", "w1", "0", "l1", "l2")
# THE READOUT FORM, measured, not assumed (2026-09-13, from the first A/B):
#   "max"   z = log P(p|h) - log max_{h' != h} P(p|h')   -- the two-candidate Hindle-Rooth contrast, generalised by
#           taking the strongest rival. MEASURED SEESAW (smoke, cap 1200, test 250): obl 0.443 -> 0.502 but nmod
#           0.458 -> 0.450 in-order and 0.454 -> 0.393 under the search decode. MECHANISM, traced: the strongest
#           rival of a noun host is almost always a verb (verbs carry far more preposition mass), so inside the
#           NOUN>NOUN configuration nearly every value is a losing bin -- the losing bin IS that configuration's
#           baseline, its learned contrast collapses to ~0, and only verb hosts get a usable ladder. The cue then
#           carries "prefer a verb", which is a type prior the CONFIGURATION already owns, not an association.
#   "share" z = log[ P(p|h) / mean_{h'} P(p|h') ] -- how much more than its fair share of the phrase this candidate
#           claims. Divisive normalisation over the retrieved population (Carandini & Heeger 2012; the spec's
#           "normalisation into a population code"), symmetric in the host types: a noun that is the best candidate
#           scores exactly as a verb that is the best candidate does.
ZFORM = "share"


def z_bin(z: float, edges=Z_EDGES) -> str:
    for e, nm in zip(edges, Z_NAMES):
        if z > e:
            return nm
    return Z_NAMES[-1]


def _contrast(sc: List[float], idx: int, form: str) -> float:
    """This candidate's score against the retrieved population. See ZFORM.
    "flat" is a CONTROL, not a readout: the cue fires on exactly the same arcs with a CONSTANT value, so the organ
    learns only "this arc is a retrieved candidate host of a case-marked nominal" and nothing about the association.
    It separates what the RETRIEVAL STRUCTURE is worth from what the ASSOCIATION CONTENT is worth -- a separation the
    scrambled twin cannot make, because scrambling preserves the structure too."""
    if form == "flat":
        return 0.0
    if form == "max":
        others = [s for i2, s in enumerate(sc) if i2 != idx]
        return sc[idx] - (max(others) if others else sc[idx] - 1.0)
    m = max(sc)
    mean = m + math.log(sum(math.exp(s - m) for s in sc) / len(sc))
    return sc[idx] - mean


def pp_arc_values(toks: Sequence[str], pos: Sequence[str], assoc: PPAssoc, k_cap: int = 6,
                  edges=Z_EDGES, typed: bool = False, obj_cue: bool = False, zform: str = ZFORM):
    """(head, dependent) -> cue value, for every retrieved candidate host of every case-marked nominal.
    `pp`    = the z-bin of log P(p|h) - log max_{h' != h} P(p|h'): this candidate's LEXICAL association with the
              preposition against its strongest competitor (divisive normalisation, not an absolute number).
    `ppobj` = the same contrast for the THEMATIC channel, log P(class(object) | type(h), p) -- what kind of thing the
              phrase is about, given who would license it (Taraban & McClelland 1988; Ratnaparkhi's fourth element).
    Returns (pp_values, ppobj_values)."""
    out: Dict[Tuple[int, int], str] = {}
    out2: Dict[Tuple[int, int], str] = {}
    for prep, obj, cands in pp_sites(toks, pos, k_cap):
        if len(cands) < 1:
            continue
        p = toks[prep - 1].lower()
        sc = []
        for q in cands:
            v = assoc.p_given(host_key(toks, pos, q), host_class(toks, pos, q), p)
            sc.append(math.log(max(v, 1e-12)))
        so = None
        if obj_cue:
            oc = obj_class(toks, pos, obj)
            so = [math.log(max(assoc.p_obj(host_type(pos[q - 1]), p, oc), 1e-12)) for q in cands]
        for idx, q in enumerate(cands):
            if q == obj:
                continue
            val = z_bin(_contrast(sc, idx, zform), edges)
            if typed:
                val = host_type(pos[q - 1]) + ":" + val
            out[(q, obj)] = val
            if so is not None:
                out2[(q, obj)] = host_type(pos[q - 1]) + ":" + z_bin(_contrast(so, idx, zform), edges)
    return out, out2


_ACTIVE: Dict[str, object] = {"assoc": None, "k_cap": 6, "edges": Z_EDGES, "typed": False, "on": False,
                              "obj_cue": False, "casefix": False, "zform": ZFORM}


# ---------------------------------------------------------------------------------------------------------------
# THE CASE-MARKING GUARD (an UPSTREAM repair found by tracing the chain, 2026-09-13)
# ---------------------------------------------------------------------------------------------------------------
# The arm's read-time meaning cue and the semantic-bootstrapping teacher both ask "is this nominal case-marked?" with
# `pos[j-2] == "ADP"` -- the preposition IMMEDIATELY before the noun.  A case marker marks the whole phrase, not the
# adjacent word (Pinker 1984: the child reads the case marker off the phrase), and any NP with more than one modifier
# breaks the adjacency test: "of Google 's new toolbar", "in the linked article", "on your hands".  MEASURED on
# UD-EWT test 700: 684 nominal run heads are case-marked by the phrase rule, only 396 by the adjacency rule -- 436
# missed (63.7%), of which 199 are gold obl and 144 gold nmod.  Those 343 prepositional objects are handed to the
# meaning cue as candidate SUBJECTS or OBJECTS of a nearby verb, which is exactly the pull the nmod/obl seesaw shows.
# ---------------------------------------------------------------------------------------------------------------
# THE OTHER CASE MARKER: THE GENITIVE (path A, built after the first measurement)
# ---------------------------------------------------------------------------------------------------------------
# The nmod population is not one thing. Split by construction (UD-EWT test 700, gold nmod, the live asset, in-order):
#   prepositional with a retrieved site 253 (recall 0.613) | POSSESSIVE PRONOUN 98 (0.449) | prepositional with no
#   site 56 (0.250) | bare PROPN 54 (0.167) | bare NOUN 35 (0.086) | GENITIVE "'s" 27 (0.074) | bare NUM 9 (0.000).
# 42% of nmod is not prepositional at all, so no preposition association can reach it -- and the two worst-served
# groups are the OTHER way English marks case: the enclitic genitive (a POSTposition) and the possessive pronoun
# (inherently genitive).  The brain principle is the same one this whole build rests on -- a case marker identifies
# the dependent and opens the search for its host (Pinker 1984; the Competition Model's case cue) -- but the genitive
# host is not competed for: a genitive specifies the nominal it precedes, so it is an item-based CONSTRUCTION
# (Tomasello 2003), the family the arm already has for coordination, NP-internal modification and function words.
# Its validity is learned by the arm's own counts like every other construction; nothing is hand-weighted.
def genitive_arcs(toks: Sequence[str], pos: Sequence[str]) -> List[Tuple[int, int]]:
    """GENITIVE construction: a nominal marked genitive -- by the enclitic ("John 's book") or by being a possessive
    pronoun ("its wares") -- depends on the head of the nominal run that follows it; the enclitic itself depends on
    the genitive nominal (the case marker attaches to its own nominal, as every case marker in this organ does)."""
    n = len(pos); out: List[Tuple[int, int], ] = []
    lows = [t.lower() for t in toks]
    for i in range(1, n + 1):
        gen = None; mark = None
        if pos[i - 1] == "PART" and lows[i - 1] in ("'s", "s", "'"):
            for q in range(i - 1, 0, -1):                       # the nominal the enclitic marks
                if pos[q - 1] in ("NOUN", "PROPN", "PRON", "NUM"):
                    gen = q; mark = i; break
                if pos[q - 1] not in NPMOD_INNER:
                    break
        elif pos[i - 1] == "PRON" and i < n and pos[i] in NP_RUN_X and lows[i - 1] not in _NON_POSS_PRON:
            gen = i
        if gen is None:
            continue
        start = (mark or gen) + 1
        while start <= n and pos[start - 1] in ("ADJ", "DET", "NUM", "ADV"):
            start += 1
        host = _run_head(pos, (mark or gen) + 1)
        if host is not None and host != gen:
            out.append((host, gen))
            if mark is not None:
                out.append((gen, mark))
    return out


NPMOD_INNER = frozenset({"DET", "ADJ", "NUM", "ADV"})
# a pronoun that is NOT a possessive determiner: the nominative/accusative forms and the demonstratives/relatives.
_NON_POSS_PRON = frozenset({"i", "he", "she", "it", "they", "we", "you", "me", "him", "them", "us", "who", "whom",
                            "which", "that", "this", "these", "those", "what", "there", "one", "all", "some", "both",
                            "each", "any", "none", "such", "another", "other", "others", "someone", "something",
                            "anyone", "anything", "everyone", "everything", "nothing", "nobody", "himself",
                            "herself", "itself", "themselves", "myself", "yourself", "ourselves"})


_CASE_CACHE: Dict[Tuple, set] = {}


def case_marked_heads(toks: Sequence[str], pos: Sequence[str], k_cap: int = 6) -> set:
    # memoised: slot_plausibility is called once per (verb, nominal) pair, so recomputing the sites there is O(n^2)
    # detector passes per sentence. A pure memo -- the set is a function of (tokens, categories, k_cap).
    key = (tuple(toks), tuple(pos), k_cap)
    v = _CASE_CACHE.get(key)
    if v is None:
        v = {obj for _, obj, _ in pp_sites(toks, pos, k_cap)}
        if len(_CASE_CACHE) > 20000:
            _CASE_CACHE.clear()
        _CASE_CACHE[key] = v
    return v


_ORIG_SLOT_PLAUS = AA.SemanticBootstrapTeacher.slot_plausibility
_ORIG_SCORE_MATRIX = AA.SemanticBootstrapTeacher.score_matrix
_ORIG_PLAUS_BIN = AA._plaus_bin


def _slot_plausibility_casefix(self, toks, pos, h, j):
    """The PHRASE-level case-marking rule applied to the meaning cue, in two forms.

    "zero" (casefix) -- a case-marked nominal is not a core participant, so the cue is silent. REFUTED AS BUILT, with
      the mechanism (cap 1500, test 700, in-order): obl 0.449 -> 0.380 ALONE and 0.449 -> 0.199 together with the PP
      cue. The over-broad adjacency guard was, by accident, the ONLY thing teaching the arm that a verb takes an
      oblique argument at all: zero it and the acquisition teacher puts almost no mass on verb -> PP-object arcs, so
      the VERB>NOUN configuration starves and obl collapses. Pinker's case rule says a case-marked nominal is not the
      SUBJECT or the OBJECT -- not that it is not a participant.
    "slot" (caseslot) -- the brain-faithful form: the nominal is still a participant, in the OBLIQUE slot. Its
      plausibility keeps its magnitude and is marked oblique (a negative sentinel that `_plaus_bin` renders as an "X"
      value), so the arm learns a SEPARATE validity for "plausible participant, oblique slot" instead of conflating it
      with the direct-object slot. The ACQUISITION teacher is untouched (`score_matrix` reads the unsigned value), so
      nothing the teacher taught is removed -- only the read-time cue gains a distinction it did not have."""
    if _ACTIVE["casefix"] and not _ACTIVE.get("_in_teacher") and j in case_marked_heads(toks, pos, _ACTIVE["k_cap"]):
        if _ACTIVE["casefix"] == "zero":
            return 0.0
        return -(abs(_ORIG_SLOT_PLAUS(self, toks, pos, h, j)) + 1e-9)
    return _ORIG_SLOT_PLAUS(self, toks, pos, h, j)


def _score_matrix_teacher(self, toks, pos):
    """The acquisition teacher reads the UNSIGNED plausibility: the case-marking distinction is a READ-TIME cue value,
    never a change to the outcome signal the validities are counted from."""
    _ACTIVE["_in_teacher"] = True
    try:
        return _ORIG_SCORE_MATRIX(self, toks, pos)
    finally:
        _ACTIVE["_in_teacher"] = False


def _plaus_bin_caseslot(p: float) -> str:
    """The arm's own plausibility bins, plus an OBLIQUE-slot family for the case-marked nominals ("X" + the same
    graded bin). Both the reference loop and the vectorised read go through this one function, so they cannot drift."""
    if p < 0.0:
        return "X" + _ORIG_PLAUS_BIN(-p)
    return _ORIG_PLAUS_BIN(p)


class PPCues(AA.SentenceCues):
    """The arm's cue pass with the widened PP cue. `pp_arc` carries the value for every (host, object) arc; the old
    two-candidate `sc.pp` path is left inert (the table's `pp_assoc` is None in every arm this cell builds)."""

    def __init__(self, toks, pos, frames, pp_assoc=None):
        super().__init__(toks, pos, frames, pp_assoc)
        self.pp_arc: Dict[Tuple[int, int], str] = {}
        self.ppobj_arc: Dict[Tuple[int, int], str] = {}
        if _ACTIVE["on"] and _ACTIVE["assoc"] is not None:
            self.pp_arc, self.ppobj_arc = pp_arc_values(self.toks, self.pos, _ACTIVE["assoc"], _ACTIVE["k_cap"],
                                                        _ACTIVE["edges"], _ACTIVE["typed"], _ACTIVE["obj_cue"],
                                                        _ACTIVE["zform"])

    def cues(self, j: int, h: int) -> Dict[str, str]:
        # the case-marking repair reaches BOTH the reference loop and the vectorised read through the ONE function
        # both of them call (`SemanticBootstrapTeacher.slot_plausibility`), so nothing here has to know about it.
        c = super().cues(j, h)
        if h and self.pp_arc:
            v = self.pp_arc.get((h, j))
            if v is not None:
                c["pp"] = v
            v2 = self.ppobj_arc.get((h, j))
            if v2 is not None:
                c["ppobj"] = v2
        return c


_ORIG_ARC_SCORES = AA.arc_scores
_ORIG_CUES = AA.SentenceCues
_ORIG_CONSTRUCTIONS = AA.CONSTRUCTIONS

# ONE cue pass per sentence, kept across the re-teaching rounds and the two arc_scores calls of one read. The arm
# rebuilds SentenceCues on every call (construction map, incremental left-corner bind, punctuation cumsum); the build
# loop calls it four times per sentence per round, and the widened PP cue adds a supersense lookup per candidate. The
# cache changes no number -- the object is a pure function of (tokens, categories, frames, association) -- only the
# time. `clear_cues_cache()` is called at every arm boundary, where `frames` and the association change.
_CUE_CACHE: Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], object] = {}
_CUE_CACHE_MAX = 40000


def clear_cues_cache() -> None:
    _CUE_CACHE.clear()


def cached_cues(toks, pos, frames, pp_assoc=None):
    key = (tuple(toks), tuple(pos))
    sc = _CUE_CACHE.get(key)
    if sc is None:
        cls = PPCues if _ACTIVE["on"] else _ORIG_CUES
        sc = cls(toks, pos, frames, pp_assoc)
        if len(_CUE_CACHE) < _CUE_CACHE_MAX:
            _CUE_CACHE[key] = sc
    return sc


def arc_scores_pp(toks, pos, table=None):
    """The arm's vectorised activation plus the widened PP cue's contributions (sparse: <= k_cap cells per site).
    Numerically identical to `AA.arc_scores_reference` under the same patched SentenceCues (checked by --self-test)."""
    A, n = _ORIG_ARC_SCORES(toks, pos, table)
    if not (_ACTIVE["on"] and _ACTIVE["assoc"] is not None):
        return A, n
    tab = table or AA.load_attachment_validities()
    ix = AA._arc_index(tab)
    sc = AA.SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"))
    for cue, arcs in (("pp", sc.pp_arc), ("ppobj", sc.ppobj_arc)):
        T = ix.cue_tab.get(cue)
        if T is None or not arcs:
            continue
        vid = ix.val_id[cue]
        for (h, j), val in arcs.items():
            if 1 <= h <= n and 1 <= j <= n and np.isfinite(A[h][j]):
                cfg = ix.cfg_id[ix.cats.get(pos[h - 1], ix.unk), ix.cats.get(pos[j - 1], ix.unk), 0 if h < j else 1]
                A[h][j] += T[cfg][vid.get(val, 0)]
    return A, n


_ORIG_CUE_NAMES = AA.CUES


def activate(assoc: Optional[PPAssoc], k_cap: int = 6, edges=Z_EDGES, typed: bool = False,
             obj_cue: bool = False, casefix=False, zform: str = ZFORM, gen_cue: bool = False) -> None:
    """Turn the widened PP cue on (assoc given) or off (None) for every subsequent call into the arm."""
    _ACTIVE.update({"assoc": assoc, "k_cap": k_cap, "edges": edges, "typed": typed, "on": assoc is not None,
                    "obj_cue": obj_cue, "casefix": casefix, "zform": zform, "gen_cue": gen_cue})
    clear_cues_cache()
    AA.SentenceCues = cached_cues
    AA.arc_scores = arc_scores_pp if assoc is not None else _ORIG_ARC_SCORES
    AA.CUES = _ORIG_CUE_NAMES + (("ppobj",) if obj_cue else ())
    AA.SemanticBootstrapTeacher.slot_plausibility = _slot_plausibility_casefix
    AA.SemanticBootstrapTeacher.score_matrix = _score_matrix_teacher
    AA._plaus_bin = _plaus_bin_caseslot
    if gen_cue:
        AA.CONSTRUCTIONS = dict(_ORIG_CONSTRUCTIONS); AA.CONSTRUCTIONS["gen"] = genitive_arcs
    else:
        AA.CONSTRUCTIONS = _ORIG_CONSTRUCTIONS


def deactivate_to_head(cache: bool = True) -> None:
    """Back to the arm exactly as HEAD ships it. `cache` keeps only the (numerically neutral) one-pass cue cache, so
    the base arm's build is timed like the others."""
    _ACTIVE.update({"assoc": None, "on": False, "obj_cue": False, "casefix": False, "zform": ZFORM})
    clear_cues_cache()
    AA.SentenceCues = cached_cues if cache else _ORIG_CUES
    AA.arc_scores = _ORIG_ARC_SCORES
    AA.CUES = _ORIG_CUE_NAMES
    AA.SemanticBootstrapTeacher.slot_plausibility = _ORIG_SLOT_PLAUS
    AA.SemanticBootstrapTeacher.score_matrix = _ORIG_SCORE_MATRIX
    AA._plaus_bin = _ORIG_PLAUS_BIN
    AA.CONSTRUCTIONS = _ORIG_CONSTRUCTIONS


# ---------------------------------------------------------------------------------------------------------------
# 5. BUILDING AN ASSET (the same pipeline as tools/build_attachment_validities.py, parameterised by the arm)
# ---------------------------------------------------------------------------------------------------------------
_TMARG_CACHE: Dict[object, list] = {}


def build_table(train, teacher, rounds: int = 3, alpha: float = 0.8, pp_assoc_legacy=None, verbose=True,
                tmarg_key=None):
    """Accrue the arm's soft arc counts from the teacher posterior, then re-teach anchored on it. Identical to the
    landed builder except that the PP cue's values come from whatever `activate(...)` installed."""
    t0 = time.time()
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _, _ in train])
    counts = AA.new_counts()
    # the TEACHER posterior depends only on the teacher (and the case-marking repair, which is in tmarg_key), never on
    # the PP cue -- so it is computed once and shared by every arm that has the same key.
    tmarg = _TMARG_CACHE.get(tmarg_key) if tmarg_key is not None else None
    reuse = tmarg is not None
    if not reuse:
        tmarg = []
    for i, (toks, pos, _, _) in enumerate(train):
        if reuse:
            mt = tmarg[i]
        else:
            A, n = teacher._score_matrix(toks, pos)
            A = AA.parallelism_boost(A, toks, pos)
            mt = single_root_marginals(A, n, 1.0)
            tmarg.append(mt)
        AA.accrue_sentence(counts, AA.SentenceCues(toks, pos, frames, pp_assoc_legacy), mt)
    if tmarg_key is not None and not reuse:
        _TMARG_CACHE[tmarg_key] = tmarg
    table = {"counts": counts, "frames": frames, "pp_assoc": pp_assoc_legacy,
             "strength": AA.strengths_from_arc_counts(counts)}
    if verbose:
        print("   round 0 accrued (%d sentences) in %.0fs" % (len(train), time.time() - t0), flush=True)
    for r in range(1, rounds + 1):
        nxt = AA.new_counts()
        for i, (toks, pos, _, _) in enumerate(train):
            ms = AA.head_posterior(toks, pos, table); mt = tmarg[i]; n = len(toks)
            mix = {j: {h: alpha * ms.get(j, {}).get(h, 0.0) + (1 - alpha) * mt.get(j, {}).get(h, 0.0)
                       for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            AA.accrue_sentence(nxt, AA.SentenceCues(toks, pos, frames, pp_assoc_legacy), mix)
        table = {"counts": nxt, "frames": frames, "pp_assoc": pp_assoc_legacy,
                 "strength": AA.strengths_from_arc_counts(nxt)}
        if verbose:
            print("   round %d re-estimated in %.0fs" % (r, time.time() - t0), flush=True)
    return table


# ---------------------------------------------------------------------------------------------------------------
# 6. MEASUREMENT -- per-relation recall, the PP-decided subpopulation, paired bootstrap over sentences
# ---------------------------------------------------------------------------------------------------------------
def per_sentence_hits(table, test, decode: str) -> List[dict]:
    """One record per test sentence: hits and totals overall, per relation, and on the PP-site subpopulation."""
    old = AA.DECODE
    AA.DECODE = decode
    out = []
    try:
        for toks, pos, gold, rels in test:
            hd = AA.heads(toks, pos, table)
            sites = {obj: (prep, c) for prep, obj, c in pp_sites(toks, pos, _ACTIVE["k_cap"] or 6)}
            rec = {"n": 0, "hit": 0, "rel": defaultdict(lambda: [0, 0]), "pp": [0, 0],
                   "pp_obl": [0, 0], "pp_nmod": [0, 0]}
            for i, g in enumerate(gold, start=1):
                if not (0 <= g <= len(toks)):
                    continue
                ok = int(hd.get(i, -1) == g)
                rec["n"] += 1; rec["hit"] += ok
                r = rels[i - 1]
                if r in CORE_RELS:
                    rec["rel"][r][0] += 1; rec["rel"][r][1] += ok
                if i in sites and r in ("obl", "nmod"):
                    rec["pp"][0] += 1; rec["pp"][1] += ok
                    rec["pp_" + r][0] += 1; rec["pp_" + r][1] += ok
            rec["rel"] = {k: v for k, v in rec["rel"].items()}
            out.append(rec)
    finally:
        AA.DECODE = old
    return out


def oracle_hits(table, test, decode: str, bonus: float = 8.0, k_cap: int = 6) -> List[dict]:
    """ORACLE-CEILING PROBE (an instrument, never a build): with the base table, add `bonus` to the arc from the GOLD
    host of every retrieved case-marked nominal. It answers "if the association channel were perfect over the candidate
    set this detector retrieves, how much is there to win?" -- the headroom of the channel, separate from the
    association's quality. The gold tree is read ONLY here, at measurement time, never during learning."""
    old = AA.DECODE
    AA.DECODE = decode
    out = []
    try:
        for toks, pos, gold, rels in test:
            A, n = AA.arc_scores(toks, pos, table)
            for prep, obj, cands in pp_sites(toks, pos, k_cap):
                g = gold[obj - 1]
                if g in cands and np.isfinite(A[g][obj]):
                    A[g][obj] += bonus
            hd = AA.decode(toks, pos, A, n, 1.0, table)[0]
            sites = {obj for _, obj, _ in pp_sites(toks, pos, k_cap)}
            rec = {"n": 0, "hit": 0, "rel": defaultdict(lambda: [0, 0]), "pp": [0, 0],
                   "pp_obl": [0, 0], "pp_nmod": [0, 0]}
            for i, g in enumerate(gold, start=1):
                if not (0 <= g <= len(toks)):
                    continue
                ok = int(hd.get(i, -1) == g)
                rec["n"] += 1; rec["hit"] += ok
                r = rels[i - 1]
                if r in CORE_RELS:
                    rec["rel"][r][0] += 1; rec["rel"][r][1] += ok
                if i in sites and r in ("obl", "nmod"):
                    rec["pp"][0] += 1; rec["pp"][1] += ok
                    rec["pp_" + r][0] += 1; rec["pp_" + r][1] += ok
            rec["rel"] = {k: v for k, v in rec["rel"].items()}
            out.append(rec)
    finally:
        AA.DECODE = old
    return out


def summarise(recs: List[dict]) -> dict:
    n = sum(r["n"] for r in recs); hit = sum(r["hit"] for r in recs)
    rel = defaultdict(lambda: [0, 0])
    for r in recs:
        for k, (t, h) in r["rel"].items():
            rel[k][0] += t; rel[k][1] += h
    pt = sum(r["pp"][0] for r in recs); ph = sum(r["pp"][1] for r in recs)
    return {"UAS": hit / max(1, n), "n_tokens": n,
            "rel": {k: round(v[1] / max(1, v[0]), 4) for k, v in sorted(rel.items())},
            "rel_n": {k: v[0] for k, v in sorted(rel.items())},
            "pp_subpop": round(ph / max(1, pt), 4), "pp_subpop_n": pt,
            "pp_subpop_obl": round(sum(r.get("pp_obl", [0, 0])[1] for r in recs) / max(1, sum(r.get("pp_obl", [0, 0])[0] for r in recs)), 4),
            "pp_subpop_obl_n": sum(r.get("pp_obl", [0, 0])[0] for r in recs),
            "pp_subpop_nmod": round(sum(r.get("pp_nmod", [0, 0])[1] for r in recs) / max(1, sum(r.get("pp_nmod", [0, 0])[0] for r in recs)), 4),
            "pp_subpop_nmod_n": sum(r.get("pp_nmod", [0, 0])[0] for r in recs)}


def paired_bootstrap(a: List[dict], b: List[dict], key, iters: int = 2000, seed: int = 20260913) -> dict:
    """Paired over sentences: the DIFFERENCE b - a of a recall, resampling sentences with replacement."""
    rng = np.random.default_rng(seed)
    m = len(a)
    ta = np.array([key(r)[0] for r in a], dtype=float); ha = np.array([key(r)[1] for r in a], dtype=float)
    tb = np.array([key(r)[0] for r in b], dtype=float); hb = np.array([key(r)[1] for r in b], dtype=float)
    base = (hb.sum() / max(1.0, tb.sum())) - (ha.sum() / max(1.0, ta.sum()))
    d = np.empty(iters)
    for i in range(iters):
        idx = rng.integers(0, m, m)
        d[i] = (hb[idx].sum() / max(1.0, tb[idx].sum())) - (ha[idx].sum() / max(1.0, ta[idx].sum()))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(base), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float(hi - lo) / 2.0, 4), "separated": bool(lo > 0 or hi < 0)}


def _apply_unified(src: str, diff_lines: List[str], path: str) -> str:
    """Apply the hunks of `path` from a unified diff to `src`, in memory. No file is written and nothing under hdlab/
    or tools/ is touched -- this exists so the proposed patch can be EXECUTED and checked against what this cell
    actually measured."""
    lines = src.split("\n")
    out: List[str] = []
    i = 0                                       # 0-based read cursor into `lines`
    k = 0
    active = False
    while k < len(diff_lines):
        ln = diff_lines[k]
        if ln.startswith("--- a/"):
            active = ln[6:].strip() == path
            k += 1
            continue
        if ln.startswith("+++ ") or ln.startswith("diff "):
            k += 1
            continue
        if ln.startswith("@@"):
            if not active:
                k += 1
                continue
            head = ln.split("@@")[1].strip()
            start = int(head.split(" ")[0][1:].split(",")[0]) - 1
            out.extend(lines[i:start]); i = start
            k += 1
            while k < len(diff_lines) and not diff_lines[k].startswith("@@") and not diff_lines[k].startswith("--- a/"):
                d = diff_lines[k]
                if d.startswith("+"):
                    out.append(d[1:])
                elif d.startswith("-"):
                    if lines[i] != d[1:]:
                        raise SystemExit("hunk mismatch at %d: %r != %r" % (i + 1, lines[i], d[1:]))
                    i += 1
                elif d.startswith(" ") or d == "":
                    body = d[1:] if d.startswith(" ") else ""
                    if lines[i] != body:
                        raise SystemExit("context mismatch at %d: %r != %r" % (i + 1, lines[i], body))
                    out.append(lines[i]); i += 1
                k += 1
            continue
        k += 1
    out.extend(lines[i:])
    return "\n".join(out)


def verify_patch(diff_path: str, n_sent: int = 40) -> int:
    """PATCH EQUIVALENCE: build the patched `hdlab/attachment_arm.py` IN MEMORY from the proposed diff, execute it as a
    module, and check that its arc activations equal the ones this cell measured with its own injected cue -- so the
    number in SOLVED.md is the number the patch produces. Also checks the patched module's own fast path against its
    own reference loop."""
    import types
    src = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8").read()
    diff = open(diff_path, encoding="utf-8").read().split("\n")
    patched = _apply_unified(src, diff, "hdlab/attachment_arm.py")
    mod = types.ModuleType("attachment_arm_patched")
    mod.__file__ = os.path.join(REPO, "hdlab", "attachment_arm.py")
    exec(compile(patched, mod.__file__, "exec"), mod.__dict__)
    print("  patched module executes: %d cues %s" % (len(mod.CUES), list(mod.CUES)))
    train = sentences(TRAIN, cap=n_sent * 4)
    reading = [(t, p) for t, p, _, _ in train]
    assoc, _ = mine(reading, rounds=1)
    v2 = {"c": dict(assoc.c), "d": dict(assoc.d), "cc": dict(assoc.cc), "dc": dict(assoc.dc), "cp": dict(assoc.cp),
          "tot": assoc.tot, "o": dict(assoc.o), "od": dict(assoc.od), "oc": dict(assoc.oc), "ocd": dict(assoc.ocd),
          "og": dict(assoc.og), "otot": assoc.otot}
    # 1. the cue VALUES the patch computes must equal the ones this cell computes
    bad = 0; tot = 0
    for (tk, ps, _, _) in train[:n_sent]:
        a1, b1 = pp_arc_values(tk, ps, assoc, 6, Z_EDGES, False, True, "share")
        a2, b2 = mod.pp_arc_values(tk, ps, v2)
        tot += len(a1)
        if a1 != a2 or b1 != b2:
            bad += 1
    print("  cue values identical on %d sentences (%d arcs): %s" % (n_sent, tot, "YES" if bad == 0 else "NO (%d)" % bad))
    gbad = sum(1 for (tk, ps, _, _) in train[:n_sent] if genitive_arcs(tk, ps) != mod.genitive_arcs(tk, ps))
    print("  genitive construction registered: %s; identical on %d sentences: %s"
          % ("gen" in mod.CONSTRUCTIONS, n_sent, "YES" if gbad == 0 else "NO (%d)" % gbad))
    # 2. the patched module's own vectorised read must equal its own reference loop
    teacher = knowledge_free_teacher(train, beta=10.0)
    activate(assoc, 6, Z_EDGES, False, True, True, "share")
    try:
        tab = build_table(train, teacher, rounds=0, verbose=False)
    finally:
        deactivate_to_head()
    tab["pp_assoc_v2"] = v2; tab["pp_assoc"] = None
    worst = 0.0
    for (tk, ps, _, _) in train[:n_sent]:
        A1, _ = mod.arc_scores(tk, ps, tab)
        A2, _ = mod.arc_scores_reference(tk, ps, tab)
        fin = np.isfinite(A1) & np.isfinite(A2)
        if not np.array_equal(np.isfinite(A1), np.isfinite(A2)):
            worst = 1e9
        elif fin.any():
            worst = max(worst, float(np.abs(A1[fin] - A2[fin]).max()))
    print("  patched fast path vs its own reference loop: max |delta| = %.2e" % worst)
    ok = bad == 0 and worst < 1e-9 and gbad == 0 and "gen" in mod.CONSTRUCTIONS
    print("  PATCH EQUIVALENCE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def consumer_roles(table, test, decode: str) -> dict:
    """THE DOWNSTREAM CONSUMER (brief section 7): the role competition (`graded_role_assigner.coarse_roles`) reads the
    heads this arm produces and decides OBL vs OBJ vs NSUBJ. Reported, never edited -- so strategy can see the hand-off.
    Accuracy is over the nominal tokens whose gold relation the organ can express."""
    from hdlab.graded_role_assigner import coarse_roles, load_coarse_validities, NOMINAL as RNOM
    rtab = load_coarse_validities()
    old = AA.DECODE
    AA.DECODE = decode
    EXPR = ("nsubj", "obj", "iobj", "obl", "nmod")
    hit = tot = 0
    conf = defaultdict(int)
    try:
        for toks, pos, gold, rels in test:
            A, n = AA.arc_scores(toks, pos, table)
            hd, post = AA.decode(toks, pos, A, n, 1.0, table)
            dep = coarse_roles(toks, pos, hd, rtab, post)
            for i in range(1, len(toks) + 1):
                if pos[i - 1] not in RNOM or rels[i - 1] not in EXPR:
                    continue
                tot += 1
                got = dep.get(i, "dep")
                hit += int(got == rels[i - 1])
                if rels[i - 1] in ("obl", "nmod"):
                    conf[rels[i - 1] + "->" + got] += 1
    finally:
        AA.DECODE = old
    return {"role_accuracy": round(hit / max(1, tot), 4), "n": tot,
            "obl_nmod_confusions": dict(sorted(conf.items(), key=lambda kv: -kv[1])[:8])}


def validity_by_value(table, cue: str) -> dict:
    """What the organ LEARNED for each value of a cue: the count-weighted mean contrast over its configurations.
    A working association cue must learn a monotone ladder (w2 > w1 > 0 > l1 > l2) without being told to."""
    st = table["strength"].get(cue, {}) or {}
    cnt = table["counts"]["cues"].get(cue, {}) or {}
    agg: Dict[str, List[float]] = defaultdict(lambda: [0.0, 0.0])
    for key, v in st.items():
        val = key.split("|", 1)[1]
        n = cnt.get(key, [0.0, 0.0])[1]
        agg[val][0] += v * n; agg[val][1] += n
    return {k: round(a / b, 3) for k, (a, b) in sorted(agg.items()) if b > 0}


def key_overall(r):
    return (r["n"], r["hit"])


def key_rel(rel):
    def f(r):
        t, h = r["rel"].get(rel, [0, 0])
        return (t, h)
    return f


def key_pp(r):
    return (r["pp"][0], r["pp"][1])


def key_pp_rel(rel):
    def f(r):
        t, h = r.get("pp_" + rel, [0, 0])
        return (t, h)
    return f


# ---------------------------------------------------------------------------------------------------------------
# 7. SELF-TEST -- the computation, not a number fitted to this file
# ---------------------------------------------------------------------------------------------------------------
def self_test() -> int:
    P = F = 0

    def ck(name, cond, detail=""):
        nonlocal P, F
        if cond:
            P += 1; print("  ok   " + name)
        else:
            F += 1; print("  FAIL " + name + " " + str(detail))

    toks = "She saw the man with the telescope .".split()
    pos = ["PRON", "VERB", "DET", "NOUN", "ADP", "DET", "NOUN", "PUNCT"]
    S = pp_sites(toks, pos)
    ck("case-marked nominal detected: 'with the telescope' -> object 'telescope'", S and S[0][0] == 5 and S[0][1] == 7, S)
    ck("candidates are the open hosts to the left, nearest first: man, saw, She", S and S[0][2][:3] == [4, 2, 1], S)

    t2 = "we are capable of it despite the noise of Google 's new toolbar .".split()
    p2 = ["PRON", "AUX", "ADJ", "ADP", "PRON", "ADP", "DET", "NOUN", "ADP", "PROPN", "PART", "ADJ", "NOUN", "PUNCT"]
    S2 = {prep: (obj, c) for prep, obj, c in pp_sites(t2, p2)}
    ck("an ADJECTIVE is a candidate host ('capable of ...')", 4 in S2 and 3 in S2[4][1], S2.get(4))
    ck("the run head skips a compound/possessive ('of Google 's new toolbar' -> toolbar)", 9 in S2 and S2[9][0] == 13, S2.get(9))
    # a gerund complement ("capable of protecting") is NOT a case-marked NOMINAL: UD labels it acl/advcl, and this cue
    # is about obl/nmod. Recorded as a deliberate scope boundary, checked so it cannot drift in silently.
    S2b = pp_sites("capable of protecting it .".split(), ["ADJ", "ADP", "VERB", "PRON", "PUNCT"])
    ck("a gerund complement is NOT treated as a case-marked nominal (scope boundary)", S2b == [], S2b)

    t3 = "He gave it to her .".split(); p3 = ["PRON", "VERB", "PRON", "ADP", "PRON", "PUNCT"]
    S3 = pp_sites(t3, p3)
    ck("a PRONOUN PP object is detected ('to her')", S3 and S3[0][1] == 5, S3)

    # unambiguous mining: only one host type present
    r_unamb = collect_instances([("Birds fly in the sky .".split(), ["NOUN", "VERB", "ADP", "DET", "NOUN", "PUNCT"])])
    ck("mining frame finds both a predicate and a nominal slot when both exist",
       r_unamb and "pred" in r_unamb[0] and "nom" in r_unamb[0], r_unamb)
    r2 = collect_instances([("Sentences about grammar .".split(), ["NOUN", "ADP", "NOUN", "PUNCT"])])
    ck("a nominal-only frame is UNAMBIGUOUS (no predicate slot)", r2 and "nom" in r2[0] and "pred" not in r2[0], r2)

    # association: counts -> probability is a pure function; observing moves it; the marginal backoff exists
    A = PPAssoc(m1=1.0, m2=1.0)
    p_before = A.p_given("V|eat", "V", "with")
    for _ in range(50):
        A.observe("V|eat", "V", "with")
    p_after = A.p_given("V|eat", "V", "with")
    ck("observing a host-preposition outcome raises P(prep | host)", p_after > p_before + 0.2, (p_before, p_after))
    A2 = PPAssoc.from_json(json.loads(json.dumps(A.to_json())))
    ck("the association round-trips through JSON exactly", abs(A2.p_given("V|eat", "V", "with") - p_after) < 1e-12)
    ck("an unseen host backs off to its class, never to zero", A.p_given("V|devour", "V", "with") > 0.0)

    # the z-bin cue is a CONTRAST: adding a constant to every candidate leaves every value unchanged
    A3 = PPAssoc(m1=1.0, m2=1.0)
    for _ in range(40):
        A3.observe("V|see", "V", "with", 1.0, "noun.artifact"); A3.observe("N|man", "N:noun.person", "of", 1.0, "noun.person")
    v, v2 = pp_arc_values(toks, pos, A3, obj_cue=True)
    ck("the PP cue fires on the retrieved candidate arcs only", set(v.keys()) <= {(4, 7), (2, 7), (1, 7)}, v)
    ck("the winning candidate gets a winning bin", v.get((2, 7)) in ("w1", "w2"), v)
    ck("the thematic channel fires on the same arcs and carries the host type", set(v2) == set(v)
       and all(x.split(":")[0] in ("V", "A", "N") for x in v2.values()), v2)
    ck("P(object class | host type, prep) is a proper backed-off probability",
       0.0 < A3.p_obj("V", "with", "noun.artifact") <= 1.0 and A3.p_obj("V", "with", "noun.food") > 0.0)

    # scramble twin: same density, same marginals, permuted profiles
    tw = A3.scramble()
    ck("the twin keeps the cell count and the preposition marginal", len(tw.c) == len(A3.c) and abs(tw.tot - A3.tot) < 1e-9)
    ck("the twin keeps the thematic channel's marginals", abs(tw.otot - A3.otot) < 1e-9 and len(tw.o) == len(A3.o))

    # equality of the vectorised read with the arm's own reference loop
    train = sentences(TRAIN, cap=60)
    assoc, _ = mine([(t, p) for t, p, _, _ in train], rounds=1)
    teacher = knowledge_free_teacher(train, beta=10.0)
    activate(assoc, obj_cue=True)
    try:
        tab = build_table(train, teacher, rounds=0, verbose=False)
        worst = 0.0
        for (tk, ps, _, _) in train[:25]:
            Aa, n = AA.arc_scores(tk, ps, tab)
            Ab, _ = AA.arc_scores_reference(tk, ps, tab)
            fin = np.isfinite(Aa) & np.isfinite(Ab)
            worst = max(worst, float(np.abs(Aa[fin] - Ab[fin]).max()) if fin.any() else 0.0)
            ck_inf = np.array_equal(np.isfinite(Aa), np.isfinite(Ab))
            if not ck_inf:
                worst = 1e9
        ck("the vectorised PP read equals the arm's reference loop (%.2e)" % worst, worst < 1e-9, worst)
        ck("both PP cues actually reach the learned counts",
           len(tab["counts"]["cues"].get("pp", {})) > 0 and len(tab["counts"]["cues"].get("ppobj", {})) > 0,
           (len(tab["counts"]["cues"].get("pp", {})), len(tab["counts"]["cues"].get("ppobj", {}))))
        post = AA.head_posterior(train[0][0], train[0][1], tab)
        ck("the head posterior is still a distribution per dependent",
           all(abs(sum(d.values()) - 1.0) < 1e-6 for d in post.values()))
    finally:
        deactivate_to_head(cache=False)
    ck("deactivating restores the arm's own SentenceCues, arc_scores and cue list",
       AA.SentenceCues is _ORIG_CUES and AA.arc_scores is _ORIG_ARC_SCORES and AA.CUES == _ORIG_CUE_NAMES)
    # the cue cache is numerically neutral: the same table, read with and without it, gives the same arc scores
    activate(assoc, obj_cue=True)
    A1, _ = AA.arc_scores(train[0][0], train[0][1], tab)
    clear_cues_cache()
    A2, _ = AA.arc_scores(train[0][0], train[0][1], tab)
    fin = np.isfinite(A1) & np.isfinite(A2)
    ck("the one-pass cue cache changes no number", float(np.abs(A1[fin] - A2[fin]).max()) == 0.0)
    deactivate_to_head(cache=False)
    print("\n%d/%d checks passed" % (P, P + F))
    return 0 if F == 0 else 1


# ---------------------------------------------------------------------------------------------------------------
# 8. MAIN
# ---------------------------------------------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verify-patch", default=None, help="path to the proposed diff: apply it in memory and check equivalence")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--mine-simplewiki", action="store_true")
    ap.add_argument("--lines", type=int, default=300000)
    ap.add_argument("--cap", type=int, default=6000)
    ap.add_argument("--test-cap", type=int, default=700)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--alpha", type=float, default=0.8)
    ap.add_argument("--beta", type=float, default=10.0)
    ap.add_argument("--realloc", type=int, default=2)
    ap.add_argument("--kcap", type=int, default=6)
    ap.add_argument("--m1", type=float, default=5.0)
    ap.add_argument("--m2", type=float, default=20.0)
    ap.add_argument("--typed", action="store_true")
    ap.add_argument("--zform", default=ZFORM, choices=("share", "max", "flat"), help="the contrast readout over the retrieved population")
    ap.add_argument("--seed", type=int, default=20260913)
    ap.add_argument("--twin-obj", action="store_true", help="give the twin the thematic channel too (twin of the obj arm)")
    ap.add_argument("--twin-casefix", action="store_true", help="give the twin the case-marking repair too")
    ap.add_argument("--oracle", action="store_true", help="also run the oracle-ceiling probe on the base table")
    ap.add_argument("--oracle-bonus", type=float, default=8.0)
    ap.add_argument("--pairs", default="", help="comma-separated floor:arm pairs to bootstrap against each other")
    ap.add_argument("--consumer", action="store_true", help="also measure the downstream role competition on each arm's heads")
    ap.add_argument("--arms", default="base,site,vol,twin")
    ap.add_argument("--decodes", default="incr,map1")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.verify_patch:
        return verify_patch(a.verify_patch)

    out_dir = str(get_output_dir(ANCHOR))
    os.makedirs(out_dir, exist_ok=True)
    PROV_START = module_provenance()
    print("hdlab provenance:", json.dumps(PROV_START["hdlab/attachment_arm.py"]),
          "pri97_cues=", PROV_START["pri97_root_cues_present"], flush=True)
    swpath = os.path.join(out_dir, "pp_assoc_simplewiki_%d.json" % a.lines)

    if a.mine_simplewiki:
        t0 = time.time()
        print("mining Simple-Wiki (%d lines) with the substrate's own category organ ..." % a.lines, flush=True)
        assoc, st = mine(simplewiki_reading(a.lines), rounds=a.realloc, m1=a.m1, m2=a.m2, k_cap=a.kcap, verbose=True)
        d = assoc.to_json(); d["mining"] = st; d["lines"] = a.lines; d["elapsed_s"] = round(time.time() - t0, 1)
        with open(swpath, "w", encoding="utf-8") as f:
            json.dump(d, f)
        print("wrote", swpath, st, "in %.0fs" % (time.time() - t0), flush=True)
        return 0

    smoke = a.smoke or not a.full
    cap = 1200 if smoke else a.cap
    test_cap = 250 if smoke else a.test_cap
    arms = [x for x in a.arms.split(",") if x]
    decodes = [x for x in a.decodes.split(",") if x]
    print("arms=%s decodes=%s cap=%d test=%d" % (arms, decodes, cap, test_cap), flush=True)

    train = sentences(TRAIN, cap=cap)
    test = sentences(TEST, cap=test_cap, maxlen=10 ** 6)
    ud_reading = [(t, p) for t, p, _, _ in train]
    t0 = time.time()
    teacher = knowledge_free_teacher(train, beta=a.beta)
    print("teacher ready in %.0fs" % (time.time() - t0), flush=True)

    assoc_ud, st_ud = mine(ud_reading, rounds=a.realloc, m1=a.m1, m2=a.m2, k_cap=a.kcap)
    print("UD-mined association:", st_ud, flush=True)
    assoc_sw = None
    if os.path.isfile(swpath):
        with open(swpath, encoding="utf-8") as f:
            dsw = json.load(f)
        assoc_sw = PPAssoc.from_json(dsw); assoc_sw.m1 = a.m1; assoc_sw.m2 = a.m2
        print("Simple-Wiki association loaded:", dsw.get("mining"), flush=True)

    legacy_pp = AA.pp_assoc_from_reading(ud_reading)      # the incumbent two-candidate association (the base arm)

    def arm_config(name):
        # base = the incumbent pipeline, unchanged (the floor: it reproduces the landed asset's build)
        if name == "base":
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": False}
        if name == "casefix":                     # phrase-level case marking, ZEROING form (refuted as built)
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": "zero"}
        if name == "caseslot":                    # phrase-level case marking, OBLIQUE-SLOT form
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": "slot"}
        if name == "objslotud":                   # the PP cue + thematic channel + the oblique slot, UD-mined
            return {"assoc": assoc_ud, "legacy": None, "obj": True, "casefix": "slot"}
        if name == "objslot":                     # the same, Simple-Wiki-mined at volume -- the full build
            return {"assoc": assoc_sw, "legacy": None, "obj": True, "casefix": "slot"}
        if name == "site":                        # widened detector + candidate competition, UD-mined association
            return {"assoc": assoc_ud, "legacy": None, "obj": False, "casefix": False}
        if name == "vol":                         # + the association mined from Simple-Wiki at volume
            return {"assoc": assoc_sw, "legacy": None, "obj": False, "casefix": False}
        if name == "objud":                       # + the typed thematic channel (object class), UD-mined
            return {"assoc": assoc_ud, "legacy": None, "obj": True, "casefix": False}
        if name == "obj":                         # + the typed thematic channel, Simple-Wiki-mined
            return {"assoc": assoc_sw, "legacy": None, "obj": True, "casefix": False}
        if name == "all":                         # volume + thematic channel + the ZEROING case rule (refuted)
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "zero"}
        if name == "allud":
            return {"assoc": assoc_ud, "legacy": None, "obj": True, "casefix": "zero"}
        if name == "noclass":                     # ABLATION: no class backoff (lexical cells only)
            src = assoc_sw or assoc_ud
            b = PPAssoc.from_json(src.to_json()); b.use_class = False; b.m1 = a.m1; b.m2 = a.m2
            return {"assoc": b, "legacy": None, "obj": True, "casefix": "slot"}
        if name == "maxud":                       # the refuted "strongest rival" readout, UD-mined
            return {"assoc": assoc_ud, "legacy": None, "obj": True, "casefix": False, "zform": "max"}
        if name == "maxform":                     # the refuted readout form, kept measurable
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "slot", "zform": "max"}
        if name == "flat":                        # CONTROL: the same arcs, a constant value (structure without content)
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "zform": "flat"}
        if name == "flatslot":
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "slot", "zform": "flat"}
        if name == "flatgen":
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "zform": "flat", "gen": True}
        if name == "gen":                         # ONLY the genitive construction (no PP cue)
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": False, "gen": True}
        if name == "objgen":                      # the full build: volume association + thematic channel + genitive
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "gen": True}
        if name == "twingen":                     # INFORMATION-FREE TWIN of `objgen`
            src = assoc_sw or assoc_ud
            return {"assoc": src.scramble(a.seed), "legacy": None, "obj": True, "casefix": False, "gen": True}
        if name == "twinslot":                    # INFORMATION-FREE TWIN of the `objslot` arm (same case rule)
            src = assoc_sw or assoc_ud
            return {"assoc": src.scramble(a.seed), "legacy": None, "obj": True, "casefix": "slot"}
        if name == "twin":                        # INFORMATION-FREE TWIN of the strongest arm
            src = assoc_sw or assoc_ud
            return {"assoc": src.scramble(a.seed), "legacy": None, "obj": a.twin_obj,
                    "casefix": ("slot" if a.twin_casefix else False)}
        raise SystemExit("unknown arm " + name)

    results = {}
    per_sent = {}
    for name in arms:
        cfg = arm_config(name)
        if name in ("vol", "obj", "objslot", "objgen", "twin", "twinslot", "twingen", "all", "noclass", "maxform",
                    "flat", "flatslot", "flatgen") and cfg["assoc"] is None and assoc_sw is None:
            print("SKIP arm %s: no Simple-Wiki association on disk (%s)" % (name, swpath), flush=True)
            continue
        t1 = time.time()
        if cfg["assoc"] is None and not cfg["casefix"] and not cfg.get("gen"):
            deactivate_to_head()
        else:
            activate(cfg["assoc"], a.kcap, Z_EDGES, a.typed, cfg["obj"], cfg["casefix"],
                     cfg.get("zform", a.zform), cfg.get("gen", False))
        try:
            tab = build_table(train, teacher, rounds=a.rounds, alpha=a.alpha, pp_assoc_legacy=cfg["legacy"],
                              tmarg_key=("casefix" if cfg["casefix"] else "plain"))
            results[name] = {"build_s": round(time.time() - t1, 1),
                             "pp_cue_cells": len(tab["counts"]["cues"].get("pp", {})),
                             "ppobj_cue_cells": len(tab["counts"]["cues"].get("ppobj", {})),
                             "pp_validity_by_value": validity_by_value(tab, "pp"),
                             "ppobj_validity_by_value": validity_by_value(tab, "ppobj")}
            for dec in decodes:
                recs = per_sentence_hits(tab, test, dec)
                per_sent[(name, dec)] = recs
                results[name][dec] = summarise(recs)
                print("  %-6s %-5s UAS %.4f  obl %.3f  nmod %.3f  pp-subpop %.3f (n=%d)" % (
                    name, dec, results[name][dec]["UAS"], results[name][dec]["rel"].get("obl", 0),
                    results[name][dec]["rel"].get("nmod", 0), results[name][dec]["pp_subpop"],
                    results[name][dec]["pp_subpop_n"]), flush=True)
            if a.consumer and decodes:
                results[name]["consumer"] = consumer_roles(tab, test, decodes[0])
                print("  %-6s consumer role accuracy %.4f  %s" % (
                    name, results[name]["consumer"]["role_accuracy"],
                    results[name]["consumer"]["obl_nmod_confusions"]), flush=True)
            if name == "base" and a.oracle:
                for dec in decodes:
                    recs = oracle_hits(tab, test, dec, a.oracle_bonus, a.kcap)
                    per_sent[("oracle", dec)] = recs
                    results.setdefault("oracle", {})[dec] = summarise(recs)
                    s = results["oracle"][dec]
                    print("  %-6s %-5s UAS %.4f  obl %.3f  nmod %.3f  pp-subpop %.3f" % (
                        "oracle", dec, s["UAS"], s["rel"].get("obl", 0), s["rel"].get("nmod", 0), s["pp_subpop"]),
                        flush=True)
            if cfg["assoc"] is not None:
                aj = os.path.join(out_dir, "pp_assoc_%s%s.json" % (name, a.tag))
                with open(aj, "w", encoding="utf-8") as f:
                    json.dump(cfg["assoc"].to_json(), f)
        finally:
            deactivate_to_head()

    # paired bootstrap of every arm against `base`
    boots = {}
    if "base" in arms:
        for name in arms:
            if name == "base" or name not in results:
                continue
            for dec in decodes:
                if (name, dec) not in per_sent or ("base", dec) not in per_sent:
                    continue
                A0 = per_sent[("base", dec)]; A1 = per_sent[(name, dec)]
                boots["%s|%s" % (name, dec)] = {
                    "UAS": paired_bootstrap(A0, A1, key_overall, a.boot),
                    "obl": paired_bootstrap(A0, A1, key_rel("obl"), a.boot),
                    "nmod": paired_bootstrap(A0, A1, key_rel("nmod"), a.boot),
                    "pp_subpop": paired_bootstrap(A0, A1, key_pp, a.boot),
                    "pp_subpop_obl": paired_bootstrap(A0, A1, key_pp_rel("obl"), a.boot),
                    "pp_subpop_nmod": paired_bootstrap(A0, A1, key_pp_rel("nmod"), a.boot),
                }
                b = boots["%s|%s" % (name, dec)]
                print("  BOOT %-6s %-5s UAS %+.4f%s  obl %+.4f%s  nmod %+.4f%s  pp %+.4f%s" % (
                    name, dec, b["UAS"]["delta"], "*" if b["UAS"]["separated"] else " ",
                    b["obl"]["delta"], "*" if b["obl"]["separated"] else " ",
                    b["nmod"]["delta"], "*" if b["nmod"]["separated"] else " ",
                    b["pp_subpop"]["delta"], "*" if b["pp_subpop"]["separated"] else " "), flush=True)

    for pr in [x for x in a.pairs.split(",") if x]:
        lo, hi = pr.split(":")
        for dec in decodes:
            if (lo, dec) not in per_sent or (hi, dec) not in per_sent:
                continue
            A0 = per_sent[(lo, dec)]; A1 = per_sent[(hi, dec)]
            boots["%s_vs_%s|%s" % (hi, lo, dec)] = {
                "UAS": paired_bootstrap(A0, A1, key_overall, a.boot),
                "obl": paired_bootstrap(A0, A1, key_rel("obl"), a.boot),
                "nmod": paired_bootstrap(A0, A1, key_rel("nmod"), a.boot),
                "pp_subpop": paired_bootstrap(A0, A1, key_pp, a.boot),
                "pp_subpop_obl": paired_bootstrap(A0, A1, key_pp_rel("obl"), a.boot),
                "pp_subpop_nmod": paired_bootstrap(A0, A1, key_pp_rel("nmod"), a.boot),
            }
            b = boots["%s_vs_%s|%s" % (hi, lo, dec)]
            print("  PAIR %-10s vs %-8s %-5s UAS %+.4f%s  obl %+.4f%s  nmod %+.4f%s  ppobl %+.4f%s  ppnmod %+.4f%s" % (
                hi, lo, dec, b["UAS"]["delta"], "*" if b["UAS"]["separated"] else " ",
                b["obl"]["delta"], "*" if b["obl"]["separated"] else " ",
                b["nmod"]["delta"], "*" if b["nmod"]["separated"] else " ",
                b["pp_subpop_obl"]["delta"], "*" if b["pp_subpop_obl"]["separated"] else " ",
                b["pp_subpop_nmod"]["delta"], "*" if b["pp_subpop_nmod"]["separated"] else " "), flush=True)

    doc = {"anchor": ANCHOR, "mode": "smoke" if smoke else "full", "train_cap": cap, "test_cap": test_cap,
           "rounds": a.rounds, "alpha": a.alpha, "beta": a.beta, "realloc": a.realloc, "kcap": a.kcap,
           "m1": a.m1, "m2": a.m2, "typed": a.typed, "z_edges": list(Z_EDGES), "zform": a.zform,
           "ud_mining": st_ud, "simplewiki_assoc": bool(assoc_sw),
           "hdlab_provenance_at_start": PROV_START, "hdlab_provenance_at_end": module_provenance(),
           "arms": results, "bootstrap_vs_base": boots,
           "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    mp = os.path.join(out_dir, "metrics%s.json" % (a.tag or ("_smoke" if smoke else "")))
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("wrote", mp, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
