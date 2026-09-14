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


# ---------------------------------------------------------------------------------------------------------------
# THE REFERENTIAL CONTEXT CUE (Spivey-Knowlton & Sedivy 1995; Altmann & Steedman 1988)
# ---------------------------------------------------------------------------------------------------------------
# The third constraint the constraint-based literature puts on PP attachment, after lexical association and thematic
# fit, is REFERENTIAL: a modifier is read as a modifier when it is NEEDED to pick a referent out.  A DEFINITE nominal
# presupposes a unique referent, so when the discourse offers more than one candidate of that kind the reader expects
# a restrictive modifier and attaches the phrase to the NOUN; an indefinite does not, and the phrase goes to the VERB
# (Altmann & Steedman 1988's one-referent vs two-referent contexts; Spivey-Knowlton & Sedivy 1995 crossed definiteness
# with verb bias and found definiteness shifts attachment even against the verb's own preference).  Everything the cue
# needs is readable off the form: the determiner of the candidate host, and whether a LIKE referent has already
# occurred.  Values categorical, validity LEARNED by the arm's own counts like every other cue.
DEF_DET = frozenset({"the", "this", "that", "these", "those", "both", "each", "every", "all"})
INDEF_DET = frozenset({"a", "an", "some", "any", "another", "one", "no", "several", "many", "few", "other"})


def host_definiteness(toks: Sequence[str], pos: Sequence[str], q: int) -> str:
    """def / indef / poss / bare for a nominal host (its determiner), or "na" for a verb or adjective host."""
    if pos[q - 1] not in NOM_HOST:
        return "na"
    if pos[q - 1] == "PROPN":
        return "name"
    k = q - 1
    while k >= 1 and pos[k - 1] in ("ADJ", "NUM", "ADV", "NOUN", "PROPN"):
        k -= 1
    if k >= 1:
        w = toks[k - 1].lower()
        if pos[k - 1] == "DET":
            return "def" if w in DEF_DET else "indef" if w in INDEF_DET else "detother"
        if pos[k - 1] == "PART" and w in ("'s", "s", "'"):
            return "poss"
        if pos[k - 1] == "PRON" and w not in _NON_POSS_PRON:
            return "poss"
    return "bare"


def has_rival_referent(toks: Sequence[str], pos: Sequence[str], q: int) -> bool:
    """A COMPETING referent for the candidate host: another nominal earlier in the sentence of the same lemma or the
    same WordNet supersense. Altmann & Steedman's two-referent context, read off the sentence alone."""
    if pos[q - 1] not in ("NOUN", "PROPN"):
        return False
    key = host_key(toks, pos, q); cls = host_class(toks, pos, q)
    for r in range(1, q):
        if pos[r - 1] not in ("NOUN", "PROPN") or not _is_nominal_host(pos, r):
            continue
        if host_key(toks, pos, r) == key:
            return True
        if cls != "N:unk" and host_class(toks, pos, r) == cls:
            return True
    return False


def ppref_values(toks: Sequence[str], pos: Sequence[str], k_cap: int = 6) -> Dict[Tuple[int, int], str]:
    """(host, PP-object) -> "<host type>:<definiteness>[R]" for every retrieved candidate."""
    out: Dict[Tuple[int, int], str] = {}
    for prep, obj, cands in pp_sites(toks, pos, k_cap):
        for q in cands:
            if q == obj:
                continue
            v = host_type(pos[q - 1]) + ":" + host_definiteness(toks, pos, q)
            if has_rival_referent(toks, pos, q):
                v += "R"
            out[(q, obj)] = v
    return out


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


# ---------------------------------------------------------------------------------------------------------------
# THE OBLIQUE-SLOT SELECTIONAL CHANNEL (phase 7; the submission's alternate path #1, now buildable)
# ---------------------------------------------------------------------------------------------------------------
# The first submission named this "the most brain-foundational thing left in this area" and parked it because it
# needed "a third grown store".  IT ALREADY EXISTS.  `tools/grow_selectional_store_bf.py` grows the verb->role->filler
# store FROM THE SUBSTRATE'S OWN READING CHAIN (its own categories -> the attachment arm -> the role competition; no
# external parser), and it already accrues an `obl:<preposition>` slot alongside SUBJ / OBJ / IOBJ:
# data/selectional_preferences_bf_v1/selectional_slots_bf_v1.pkl holds 11,857 (verb, obl:<prep>) slots and 41,460
# oblique filler observations grown from 60,000 Simple-Wiki lines.
#
# WHY IT IS THE RIGHT CHANNEL.  The `ppobj` channel this cell already ships is typed only by the host's CATEGORY:
# P(class of the object | V-or-N, preposition).  It cannot tell "ate the pizza WITH A FORK" from "ate the pizza WITH
# ANCHOVIES", because both hosts are verbs and both objects compete against the same V-level distribution.
# Ratnaparkhi's model and the thematic-fit literature are LEXICAL in the predicate: the quadruple (v, n1, p, n2)
# (Ratnaparkhi 1998; Hindle & Rooth 1993 lexical association; McRae, Ferretti & Amyote 1997 role-as-feature-bundle --
# a thematic role is a bundle of features of the filler a PARTICULAR predicate expects).  This channel supplies the
# missing (v, p, class(n2)) term, in the typed Resnik-style form the substrate's selectional organ uses everywhere.
#
# THE READOUT IS DELIBERATELY NOT A CROSS-TYPE CONTRAST.  Section 5(a) of the submission refuted the "strongest rival"
# readout because comparing a noun host with a verb host smuggles a TYPE PRIOR into what should be an association.
# The store holds only verbs, so a population contrast here would do exactly that again.  The value is instead this
# host's LEXICAL SPECIFICITY, pointwise:  log[ P(class | this verb, this preposition) / P(class | this preposition) ]
# -- how much more this particular predicate expects this kind of oblique filler than predicates in general do.  It is
# ~0 for a predicate with no specific preference, type-neutral by construction, and a host the store has never seen
# ABSTAINS ("na"), a value whose validity the arm learns like any other.
BF_SLOT_STORE = os.path.join(REPO, "data", "selectional_preferences_bf_v1", "selectional_slots_bf_v1.pkl")


class OblSlotPreference:
    """P(class of the oblique filler | predicate lemma, preposition) as plastic COUNTS with Resnik-style type
    generalisation, read off the substrate's own grown slot store.  Counts in, one pure function out; `observe(...)`
    accrues one comprehension outcome online exactly like `PPAssoc.observe`."""

    def __init__(self, m1: float = 5.0, m2: float = 20.0):
        self.c: Dict[str, float] = defaultdict(float)     # "<verb>|<prep>|<class>"
        self.d: Dict[str, float] = defaultdict(float)     # "<verb>|<prep>"
        self.cg: Dict[str, float] = defaultdict(float)    # "<prep>|<class>"
        self.dg: Dict[str, float] = defaultdict(float)    # "<prep>"
        self.cw: Dict[str, float] = defaultdict(float)    # "<class>"
        self.tot = 0.0
        self.m1 = float(m1); self.m2 = float(m2)
        self._cache: Dict[Tuple[str, str, str], float] = {}

    def observe(self, verb: str, prep: str, cls: str, w: float = 1.0) -> None:
        self.c[verb + "|" + prep + "|" + cls] += w; self.d[verb + "|" + prep] += w
        self.cg[prep + "|" + cls] += w; self.dg[prep] += w
        self.cw[cls] += w; self.tot += w
        self._cache.clear()

    def p_global(self, prep: str, cls: str) -> float:
        pg = (self.cw.get(cls, 0.0) + 0.5) / (self.tot + 1.0)
        return (self.cg.get(prep + "|" + cls, 0.0) + self.m2 * pg) / (self.dg.get(prep, 0.0) + self.m2)

    def p_local(self, verb: str, prep: str, cls: str) -> Optional[Tuple[float, float]]:
        """(P(class | verb, prep), P(class | prep)) or None when the predicate is unseen in this slot."""
        if self.d.get(verb + "|" + prep, 0.0) <= 0.0:
            return None
        g = self.p_global(prep, cls)
        pl = (self.c.get(verb + "|" + prep + "|" + cls, 0.0) + self.m1 * g) / (self.d[verb + "|" + prep] + self.m1)
        return pl, g

    def oblique_plausibility(self, verb: str, prep: str, cls: str) -> Optional[float]:
        """The oblique slot's plausibility on the SAME 0..1 scale the object slot uses: the share this predicate's own
        oblique expectation takes against what any predicate expects with this preposition.  0.5 = no preference,
        > 0.5 = this predicate really does take this kind of thing as an oblique with this preposition."""
        pg = self.p_local(verb, prep, cls)
        if pg is None:
            return None
        pl, g = pg
        return pl / (pl + g) if (pl + g) > 0 else 0.5

    def logspec(self, verb: str, prep: str, cls: str) -> Optional[float]:
        """log[P(class | verb, prep) / P(class | prep)]; None when the predicate is unseen in this slot (ABSTAIN)."""
        if self.d.get(verb + "|" + prep, 0.0) <= 0.0:
            return None
        key = (verb, prep, cls)
        v = self._cache.get(key)
        if v is None:
            g = self.p_global(prep, cls)
            pl = (self.c.get(verb + "|" + prep + "|" + cls, 0.0) + self.m1 * g) / (self.d[verb + "|" + prep] + self.m1)
            v = math.log(max(pl, 1e-12)) - math.log(max(g, 1e-12))
            self._cache[key] = v
        return v

    @classmethod
    def from_grown_store(cls, path=None, m1: float = 5.0, m2: float = 20.0) -> "OblSlotPreference":
        """Read the substrate's own grown store and TYPE its fillers with the same WordNet supersense table the typed
        selectional-preference organ reads. Nothing is fitted here; the counts are the store's own."""
        import pickle
        from hdlab.typed_selectional_preference import noun_supersense
        self = cls(m1, m2)
        sf = pickle.load(open(path or BF_SLOT_STORE, "rb"))["slot_filler"]
        for (v, role), fillers in sf.items():
            if not role.startswith("obl:"):
                continue
            prep = role.split(":", 1)[1]
            if not prep or prep == "_":
                continue
            vl = lemma_verb(v).lower()
            for w, cnt in fillers.items():
                self.observe(vl, prep, noun_supersense(w) or "unk", float(cnt))
        return self

    def scramble(self, seed: int = 20260913) -> "OblSlotPreference":
        """INFORMATION-FREE TWIN: each predicate's oblique-filler profile is reassigned to another predicate. Every
        count, every marginal and the density are identical; only WHICH predicate expects WHICH filler is destroyed."""
        rng = random.Random(seed + 7)
        out = OblSlotPreference(self.m1, self.m2)
        verbs = sorted({k.split("|", 1)[0] for k in self.d})
        donor = list(verbs); rng.shuffle(donor); mp = dict(zip(verbs, donor))
        for k, val in self.c.items():
            v, p, c = k.split("|", 2)
            out.c[mp.get(v, v) + "|" + p + "|" + c] = val
        for k, val in self.d.items():
            v, p = k.split("|", 1)
            out.d[mp.get(v, v) + "|" + p] = val
        out.cg = defaultdict(float, self.cg); out.dg = defaultdict(float, self.dg)
        out.cw = defaultdict(float, self.cw); out.tot = self.tot
        return out

    def stats(self) -> dict:
        return {"predicate_prep_slots": len(self.d), "filler_class_cells": len(self.c),
                "prepositions": len(self.dg), "observations": round(self.tot, 1)}


def ppslot_values(toks: Sequence[str], pos: Sequence[str], slot, k_cap: int = 6,
                  edges=Z_EDGES) -> Dict[Tuple[int, int], str]:
    """(host, PP-object) -> the z-bin of the host's lexical oblique specificity, or "na" when the store abstains."""
    out: Dict[Tuple[int, int], str] = {}
    for prep, obj, cands in pp_sites(toks, pos, k_cap):
        p = toks[prep - 1].lower()
        oc = obj_class(toks, pos, obj)
        for q in cands:
            if q == obj:
                continue
            if pos[q - 1] != "VERB":
                out[(q, obj)] = "na"
                continue
            z = slot.logspec(lemma_verb(toks[q - 1]).lower(), p, oc)
            out[(q, obj)] = "na" if z is None else z_bin(z, edges)
    return out


_ACTIVE: Dict[str, object] = {"assoc": None, "k_cap": 6, "edges": Z_EDGES, "typed": False, "on": False,
                              "obj_cue": False, "casefix": False, "zform": ZFORM, "slot": None}


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
_CASE_PREP_CACHE: Dict[Tuple, dict] = {}


def case_marked_preps(toks: Sequence[str], pos: Sequence[str], k_cap: int = 6) -> dict:
    """{object index -> the preposition that marks it}. Memoised; a pure function of (tokens, categories, k_cap)."""
    key = (tuple(toks), tuple(pos), k_cap)
    v = _CASE_PREP_CACHE.get(key)
    if v is None:
        v = {obj: toks[prep - 1].lower() for prep, obj, _ in pp_sites(toks, pos, k_cap)}
        if len(_CASE_PREP_CACHE) > 20000:
            _CASE_PREP_CACHE.clear()
        _CASE_PREP_CACHE[key] = v
    return v


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
    if _ACTIVE["casefix"] == "oblteach" and _ACTIVE.get("slot") is not None and pos[h - 1] == "VERB":
        # PINKER'S THIRD SLOT, WITH REAL CONTENT (phase 7).  The submission refuted two shortcuts here and named the
        # real fix: "give the acquisition teacher an OBLIQUE SLOT ... an OBL-slot selectional association grown the way
        # SUBJ and OBJ already are, so a case-marked nominal is scored as a plausible OBLIQUE participant rather than
        # as a bad object" (SOLVED.md section 8.1).  That store exists -- the substrate grew it from its own reading --
        # so the case-marked nominal is now scored in the OBLIQUE slot, by THIS predicate's own oblique expectation
        # with THIS preposition.  Crucially this does NOT zero the verb's pull: section 5(b) showed the over-broad
        # guard is the arm's only oblique-argument teacher, and zeroing it collapses obl 0.449 -> 0.199.  When the
        # store abstains the original value stands, so nothing the teacher taught is ever removed -- only re-scored.
        # It applies inside the ACQUISITION teacher as well as at read time, which is the whole point: the arm must
        # LEARN that a verb takes obliques of the kinds this verb takes.
        pr = case_marked_preps(toks, pos, _ACTIVE["k_cap"]).get(j)
        if pr is not None:
            v = _ACTIVE["slot"].oblique_plausibility(lemma_verb(toks[h - 1]).lower(), pr, obj_class(toks, pos, j))
            if v is not None:
                return float(v)
        return _ORIG_SLOT_PLAUS(self, toks, pos, h, j)
    if _ACTIVE["casefix"] and _ACTIVE["casefix"] != "oblteach" and not _ACTIVE.get("_in_teacher") \
            and j in case_marked_heads(toks, pos, _ACTIVE["k_cap"]):
        if _ACTIVE["casefix"] == "zero":
            return 0.0
        return -(abs(_ORIG_SLOT_PLAUS(self, toks, pos, h, j)) + 1e-9)
    return _ORIG_SLOT_PLAUS(self, toks, pos, h, j)


# ---------------------------------------------------------------------------------------------------------------
# THE NOMINAL HOST SLOT (phase 7): the acquisition teacher is VERB-ONLY, and that is the asymmetry under the nmod loss
# ---------------------------------------------------------------------------------------------------------------
# `SemanticBootstrapTeacher.score_matrix` adds its meaning term `beta * slot_plausibility(h, j)` on exactly one kind of
# arc: `pos[h-1] == "VERB" and pos[j-1] in NOMINAL`.  A NOUN host gets no meaning support at all, ever.  So while the
# arm is learning, every case-marked nominal has a verb competing for it with a large semantic vote and a noun
# competing for it with nothing -- which is precisely the direction of the nmod loss, and precisely why deleting the
# over-broad case guard collapsed obl (section 5b): that guard was the ONLY meaning signal on this population, and it
# only ever spoke for verbs.
#
# THE BRAIN DOES NOT HAVE THIS ASYMMETRY.  A relational noun selects its complement exactly as a verb selects its
# argument -- "the picture OF the girl", "the edge OF the table", "the trip TO Paris" (Barker 1995 possessive
# descriptions; Lobner's relational nouns; Rappaport Hovav & Levin on argument-taking nominals).  Psycholinguistically
# the noun's own preposition expectation is one of the two lexical terms in the original Hindle & Rooth contrast --
# the model is log[P(p | VERB) / P(p | NOUN)], symmetric by construction -- and the reader uses it online
# (Spivey-Knowlton & Sedivy 1995).  The organ has the noun side of that association already (it is mined here); what
# it lacks is a channel for the noun to VOTE while the validities are being acquired.
#
# THE COMPUTATION.  For every retrieved NOMINAL host h of a case-marked nominal j, add `beta_n * P_host(h, p)` to the
# teacher's arc score, where P_host is the same 0..1 contrast shape the object slot uses:
#       P_host = P(p | this noun) / [ P(p | this noun) + P(p | this noun's class) ]
# 0.5 when this noun is no more attracted to the preposition than nouns of its kind, above 0.5 when it is -- the noun's
# own relational expectation, from counts, with the Resnik-style class as the reference. beta_n is swept, never adopted.
def _nominal_host_support(A, n, toks, pos):
    """Give NOMINAL hosts the meaning vote the teacher currently reserves for verbs. Counts only; no gold, no tree."""
    assoc = _ACTIVE["assoc"]
    if assoc is None:
        return A
    bn = float(_ACTIVE.get("beta_nom") or 0.0)
    if bn <= 0.0:
        return A
    for prep, obj, cands in pp_sites(toks, pos, _ACTIVE["k_cap"]):
        pw = toks[prep - 1].lower()
        for q in cands:
            if q == obj or pos[q - 1] not in NOM_HOST or not (1 <= q <= n) or not np.isfinite(A[q][obj]):
                continue
            hk = host_key(toks, pos, q); hc = host_class(toks, pos, q)
            pl = assoc.p_given(hk, hc, pw)
            gc = (assoc.cc.get(hc + "|" + pw, 0.0) + assoc.m2 * assoc.p_prep(pw)) / (assoc.dc.get(hc, 0.0) + assoc.m2)
            A[q][obj] += bn * (pl / (pl + gc) if (pl + gc) > 0 else 0.5)
    return A


def _score_matrix_teacher(self, toks, pos):
    """The acquisition teacher reads the UNSIGNED plausibility: the case-marking distinction is a READ-TIME cue value,
    never a change to the outcome signal the validities are counted from.  Phase 7 adds the NOMINAL HOST SLOT here,
    inside the teacher, because that is where the verb-only asymmetry lives."""
    _ACTIVE["_in_teacher"] = True
    try:
        A, n = _ORIG_SCORE_MATRIX(self, toks, pos)
        if _ACTIVE.get("beta_nom"):
            A = _nominal_host_support(A, n, toks, pos)
        return A, n
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
        self.ppref_arc: Dict[Tuple[int, int], str] = {}
        self.ppslot_arc: Dict[Tuple[int, int], str] = {}
        if _ACTIVE.get("ref_cue"):
            self.ppref_arc = ppref_values(self.toks, self.pos, _ACTIVE["k_cap"])
        if _ACTIVE.get("slot") is not None and _ACTIVE.get("slot_cue"):
            self.ppslot_arc = ppslot_values(self.toks, self.pos, _ACTIVE["slot"], _ACTIVE["k_cap"], _ACTIVE["edges"])
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
        if h and self.ppref_arc:
            v3 = self.ppref_arc.get((h, j))
            if v3 is not None:
                c["ppref"] = v3
        if h and self.ppslot_arc:
            v4 = self.ppslot_arc.get((h, j))
            if v4 is not None:
                c["ppslot"] = v4
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
        # ANY of the cell's cues (association, referential, oblique slot) needs the widened cue pass. Before phase 7
        # this read `_ACTIVE["on"]` alone, so an arm carrying ONLY the referential cue silently reduced to `base`.
        cls = PPCues if (_ACTIVE["on"] or _ACTIVE.get("ref_cue") or _ACTIVE.get("slot_cue")) else _ORIG_CUES
        sc = cls(toks, pos, frames, pp_assoc)
        if len(_CUE_CACHE) < _CUE_CACHE_MAX:
            _CUE_CACHE[key] = sc
    return sc


def arc_scores_pp(toks, pos, table=None):
    """The arm's vectorised activation plus the widened PP cue's contributions (sparse: <= k_cap cells per site).
    Numerically identical to `AA.arc_scores_reference` under the same patched SentenceCues (checked by --self-test)."""
    A, n = _ORIG_ARC_SCORES(toks, pos, table)
    if not (_ACTIVE["on"] and _ACTIVE["assoc"] is not None) and not _ACTIVE.get("ref_cue") and not _ACTIVE.get("slot_cue"):
        return A, n
    tab = table or AA.load_attachment_validities()
    ix = AA._arc_index(tab)
    sc = AA.SentenceCues(toks, pos, tab.get("frames", {}), tab.get("pp_assoc"))
    for cue, arcs in (("pp", sc.pp_arc), ("ppobj", sc.ppobj_arc), ("ppref", sc.ppref_arc),
                      ("ppslot", getattr(sc, "ppslot_arc", {}))):
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
             obj_cue: bool = False, casefix=False, zform: str = ZFORM, gen_cue: bool = False,
             ref_cue: bool = False, slot=None, slot_cue: bool = False, beta_nom: float = 0.0) -> None:
    """Turn the widened PP cue on (assoc given) or off (None) for every subsequent call into the arm."""
    _ACTIVE.update({"assoc": assoc, "k_cap": k_cap, "edges": edges, "typed": typed, "on": assoc is not None,
                    "obj_cue": obj_cue, "casefix": casefix, "zform": zform, "gen_cue": gen_cue,
                    "ref_cue": ref_cue, "slot": slot, "slot_cue": slot_cue, "beta_nom": beta_nom})
    clear_cues_cache()
    AA.SentenceCues = cached_cues
    AA.arc_scores = arc_scores_pp if (assoc is not None or ref_cue or slot_cue) else _ORIG_ARC_SCORES
    AA.CUES = (_ORIG_CUE_NAMES + (("ppobj",) if obj_cue else ()) + (("ppref",) if ref_cue else ())
               + (("ppslot",) if slot_cue else ()))
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
    _ACTIVE.update({"assoc": None, "on": False, "obj_cue": False, "casefix": False, "zform": ZFORM,
                    "ref_cue": False, "slot": None, "slot_cue": False, "beta_nom": 0.0})
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
            if hasattr(AA, "predication_boost"):
                A = AA.predication_boost(A, toks, pos)     # pri-97's acquisition signal; present in the landed builder
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


_LC_TAGS: Dict[Tuple[str, ...], Tuple[List[str], list]] = {}


def live_tags(toks: Sequence[str]):
    """The categories rung's OWN readout: hdlab.lexical_categories (count-based generative model, forward-backward)
    -> (argmax tags, per-token posterior). Cached per sentence; it is a pure function of the tokens."""
    key = tuple(toks)
    v = _LC_TAGS.get(key)
    if v is None:
        from hdlab import lexical_categories as LC
        v = LC.get().tag_with_posterior(list(toks))
        _LC_TAGS[key] = v
    return v


def per_sentence_hits_live(table, test, decode: str) -> List[dict]:
    """THE LIVE CHAIN: no gold categories anywhere. The category organ tags each sentence and hands DOWN its posterior;
    the attachment competition is marginalised over the uncertain tokens (`arc_scores_graded`), and the PP cue reads
    the organ's own tags -- so the preposition, the nominal run and the candidate hosts are all the organ's call."""
    old = AA.DECODE
    AA.DECODE = decode
    out = []
    try:
        for toks, _gold_pos, gold, rels in test:
            pos, tpost = live_tags(toks)
            A, n = AA.arc_scores_graded(toks, pos, tpost, table)
            hd = AA.decode(toks, pos, A, n, 1.0, table)[0]
            sites = {obj for _, obj, _ in pp_sites(toks, pos, _ACTIVE["k_cap"] or 6)}
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


# ---------------------------------------------------------------------------------------------------------------
# THE SECOND DIFF: the two-sided acquisition teacher, generated and equivalence-checked in memory
# ---------------------------------------------------------------------------------------------------------------
# Strategy asked for this as a SEPARATE landing step, after `attachment_arm_pp_patch.diff`.  It is generated against
# the tree WITH that diff already applied (in memory -- nothing under hdlab/ is written), because it USES the symbols
# that diff introduces (`pp_case_marked`, `pp_sites`, `pp_obj_class`, `pp_host_key`, `pp_host_class`, `pp_p_given`,
# `PP_KCAP`, `PP_NOM_HOST`).  Its hunks are in `SemanticBootstrapTeacher.__init__`, `.slot_plausibility` and
# `.score_matrix`, one new block of module-level code, and `tools.build_attachment_validities.knowledge_free_teacher`.
TWO_SIDED_CODE = r"""

# ------------------------------------------------------------------ the TWO-SIDED acquisition teacher (pri 94 ph 7)
# `SemanticBootstrapTeacher.score_matrix` adds its meaning term `beta * slot_plausibility(h, j)` on exactly one kind
# of arc: a VERB host with a NOMINAL dependent.  A noun host receives no meaning support at all, ever.  While the arm
# learns, every case-marked nominal therefore has a verb voting for it with beta and a noun voting with nothing --
# and MEASURED (pri 94 phase 7, UD-EWT test 700), WHERE THAT BUDGET IS SPENT IS THE obl/nmod SEESAW: spend more on
# verbs and obl goes 0.541 -> 0.679 while nmod goes 0.489 -> 0.221; spend it on nouns and obl -> 0.210, nmod -> 0.566.
# The brain has no such asymmetry: a relational noun selects its complement as a verb selects its argument ("the
# picture OF the girl", "the edge OF the table"; Barker 1995 possessive descriptions; Loebner's relational nouns), and
# Hindle & Rooth 1993's contrast log[P(p|VERB)/P(p|NOUN)] is symmetric by construction.  Two additions, both counts:
#   (1) OBLIQUE SLOT.  A case-marked nominal hosted by a verb is scored in the OBLIQUE slot, by that predicate's own
#       oblique expectation with that preposition, read off the substrate's OWN grown `obl:<prep>` store (Pinker 1984
#       semantic bootstrapping with three slots instead of two).  When the store abstains the teacher's own value
#       stands, so the verb's pull is RE-SCORED and never removed -- zeroing it collapses obl 0.449 -> 0.199.
#   (2) NOMINAL HOST SLOT.  Every retrieved nominal host of a case-marked nominal gets `BETA_NOM * P_host`, where
#       P_host = P(p | this noun) / [P(p | this noun) + P(p | this noun's class)] -- 0.5 when this noun is no more
#       attracted to the preposition than nouns of its kind.
# MEASURED TOGETHER (cap 1500, test 700, paired bootstrap over sentences, in-order): retrieved-nmod +0.0752
# CI [+0.0308,+0.1231] over the floor and +0.0564 CI [+0.0115,+0.1020] over the arm without them; UAS +0.0121*,
# obl +0.0818*, nmod +0.1067*; nothing CI-separated down; and the downstream role competition returns to the floor
# (0.5769 vs 0.5760, against 0.5617 without them).  Beats a twin with BOTH stores scrambled on UAS (+0.0082*), obl
# (+0.1405*) and retrieved obl (+0.1952*).  BETA_NOM swept (2 / 6 / 14; 14 overshoots, obl 0.264), never adopted.
BETA_NOM = float(os.environ.get("HDLAB_SBT_BETA_NOM", "6.0"))       # swept operating point, never adopted
OBL_TEACH = os.environ.get("HDLAB_SBT_OBL_TEACH", "1") != "0"
OBL_SLOT_M1 = float(os.environ.get("HDLAB_SBT_OBL_M1", "5.0"))
OBL_SLOT_M2 = float(os.environ.get("HDLAB_SBT_OBL_M2", "20.0"))
_OBL_SLOTS = None


def obl_slot_store(path=None):
    '''P(class of the oblique filler | predicate lemma, preposition) as COUNTS, from the substrate's OWN grown slot
    store (tools/grow_selectional_store_bf.py: its own reading-induced categories -> this arm -> the role
    competition, 60k Simple-Wiki lines, no external parser): 6,947 (predicate, preposition) slots, 20,179
    filler-class cells, 39,222 observations.  Typed with the same WordNet supersense table the typed selectional
    organ reads.  Plastic: the counts are the store's own and grow with more reading.'''
    global _OBL_SLOTS
    if _OBL_SLOTS is not None and path is None:
        return _OBL_SLOTS
    from collections import defaultdict as _dd
    c = _dd(float); d = _dd(float); cg = _dd(float); dg = _dd(float); cw = _dd(float); tot = 0.0
    pth = path or BF_STORE
    if os.path.isfile(pth):
        import pickle
        from hdlab.typed_selectional_preference import noun_supersense
        sf = pickle.load(open(pth, "rb"))["slot_filler"]
        for (v, role), fillers in sf.items():
            if not role.startswith("obl:"):
                continue
            prep = role.split(":", 1)[1]
            if not prep or prep == "_":
                continue
            vl = lemma_verb(v).lower()
            for w, cnt in fillers.items():
                cls = noun_supersense(w) or "unk"
                cnt = float(cnt)
                c[vl + "|" + prep + "|" + cls] += cnt; d[vl + "|" + prep] += cnt
                cg[prep + "|" + cls] += cnt; dg[prep] += cnt; cw[cls] += cnt; tot += cnt
    out = {"c": dict(c), "d": dict(d), "cg": dict(cg), "dg": dict(dg), "cw": dict(cw), "tot": tot,
           "computation": "P(objclass|verb,prep) = (c + m1*P(objclass|prep))/(d + m1); oblique-slot plausibility = "
                          "P(objclass|verb,prep) / [P(objclass|verb,prep) + P(objclass|prep)]"}
    if path is None:
        _OBL_SLOTS = out
    return out


def obl_slot_plausibility(S, verb, prep, cls):
    '''The oblique slot on the SAME 0..1 scale the object slot uses; 0.5 = this predicate expects this kind of
    oblique filler no more than predicates in general do.  None = unseen predicate in this slot, and the caller must
    then leave the teacher's own value alone.'''
    d = S["d"].get(verb + "|" + prep, 0.0)
    if d <= 0.0:
        return None
    pg = (S["cw"].get(cls, 0.0) + 0.5) / (S["tot"] + 1.0)
    g = (S["cg"].get(prep + "|" + cls, 0.0) + OBL_SLOT_M2 * pg) / (S["dg"].get(prep, 0.0) + OBL_SLOT_M2)
    pl = (S["c"].get(verb + "|" + prep + "|" + cls, 0.0) + OBL_SLOT_M1 * g) / (d + OBL_SLOT_M1)
    return pl / (pl + g) if (pl + g) > 0 else 0.5


_PP_PREP_CACHE = {}


def pp_case_preps(toks, pos):
    '''{object index -> the preposition that marks it}, memoised; a pure function of (tokens, categories).'''
    key = (tuple(toks), tuple(pos))
    v = _PP_PREP_CACHE.get(key)
    if v is None:
        v = {obj: toks[prep - 1].lower() for prep, obj, _ in pp_sites(toks, pos)}
        if len(_PP_PREP_CACHE) > 20000:
            _PP_PREP_CACHE.clear()
        _PP_PREP_CACHE[key] = v
    return v
"""

TWO_SIDED_SLOT = r"""        # THE OBLIQUE SLOT (pri 94 phase 7): a case-marked nominal hosted by a verb is a plausible OBLIQUE of THIS
        # predicate with THIS preposition, not a bad direct object.  Falls through to the object / subject slots when
        # the grown store has never seen this predicate in this slot, so nothing the teacher taught is removed.
        if OBL_TEACH and self.obl_slots is not None and pos[h - 1] == "VERB":
            _pr = pp_case_preps(toks, pos).get(j)
            if _pr is not None:
                _v = obl_slot_plausibility(self.obl_slots, lemma_verb(toks[h - 1]).lower(), _pr,
                                           pp_obj_class(toks, pos, j))
                if _v is not None:
                    return float(_v)
"""

TWO_SIDED_SCORE = r"""        # THE NOMINAL HOST SLOT (pri 94 phase 7): give nominal hosts the meaning vote this teacher reserves for
        # verbs.  Applied after the root row, exactly as measured.
        if BETA_NOM > 0.0 and self.pp_assoc is not None:
            for _prep, _obj, _cands in pp_sites(toks, pos):
                _pw = toks[_prep - 1].lower()
                for _q in _cands:
                    if _q == _obj or pos[_q - 1] not in PP_NOM_HOST or not np.isfinite(A[_q][_obj]):
                        continue
                    _hc = pp_host_class(toks, pos, _q)
                    _pl = pp_p_given(self.pp_assoc, pp_host_key(toks, pos, _q), _hc, _pw)
                    _cc = self.pp_assoc["cc"]; _dc = self.pp_assoc["dc"]; _cp = self.pp_assoc["cp"]
                    _m2 = self.pp_assoc.get("m2", 20.0)
                    _pp = (_cp.get(_pw, 0.0) + 0.5) / (self.pp_assoc["tot"] + 1.0)
                    _g = (_cc.get(_hc + "|" + _pw, 0.0) + _m2 * _pp) / (_dc.get(_hc, 0.0) + _m2)
                    A[_q][_obj] += BETA_NOM * (_pl / (_pl + _g) if (_pl + _g) > 0 else 0.5)
"""


def _emit_two_sided(main_diff_path, out_path):
    """Build the post-main source in memory, apply the two-sided edits, write and return the unified diff."""
    import difflib
    src0 = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8").read()
    main = open(main_diff_path, encoding="utf-8").read().split("\n")
    src1 = _apply_unified(src0, main, "hdlab/attachment_arm.py")
    src2 = src1
    a = 'PP_CASE_RULE = os.environ.get("HDLAB_ARM_PP_CASE_RULE", "0") != "0"'
    assert src2.count(a) == 1, "anchor PP_CASE_RULE"
    src2 = src2.replace(a, a + "\n" + TWO_SIDED_CODE, 1)
    a = "    def __init__(self, beta: float = 10.0, lam: float = 0.3, tsp_asset: Optional[str] = None):"
    assert src2.count(a) == 1, "anchor teacher __init__"
    src2 = src2.replace(a, "    def __init__(self, beta: float = 10.0, lam: float = 0.3, tsp_asset: Optional[str] = None,\n"
                           "                 pp_assoc: Optional[Dict[str, object]] = None):", 1)
    a = "        self.beta = float(beta); self.lam = float(lam); self._cache: Dict[Tuple[str, str], float] = {}"
    assert src2.count(a) == 1, "anchor teacher fields"
    src2 = src2.replace(a, "        self.pp_assoc = pp_assoc            # the NOUN side of Hindle & Rooth, for the nominal host slot\n"
                           "        self.obl_slots = obl_slot_store() if OBL_TEACH else None\n" + a, 1)
    # the MAIN diff already inserts its (default-off) phrase case rule between these two lines, so anchor on the
    # POST-MAIN text and put the oblique slot first -- exactly where the measured cell put it.
    _nl = chr(10)
    a = '        n = len(toks)' + _nl + '        if PP_CASE_RULE and j in pp_case_marked(toks, pos):'
    assert src2.count(a) == 1, "anchor slot_plausibility body"
    src2 = src2.replace(a, '        n = len(toks)' + _nl + TWO_SIDED_SLOT
                        + '        if PP_CASE_RULE and j in pp_case_marked(toks, pos):', 1)
    a = ('                A[0][j] = (self.beta * best_arg[j] if pos[j - 1] == "VERB" else -1.0) - 0.5\n'
         '        return A, n')
    assert src2.count(a) == 1, "anchor score_matrix return"
    src2 = src2.replace(a, '                A[0][j] = (self.beta * best_arg[j] if pos[j - 1] == "VERB" else -1.0) - 0.5\n'
                           + TWO_SIDED_SCORE + '        return A, n', 1)
    d = list(difflib.unified_diff(src1.split("\n"), src2.split("\n"),
                                  fromfile="a/hdlab/attachment_arm.py", tofile="b/hdlab/attachment_arm.py",
                                  lineterm="", n=3))
    # The tools-side hunk is generated against the CURRENT file, not the post-main one: the main diff's hunks in
    # tools/build_attachment_validities.py are at lines 17 / 131 / 149 / 162 / 171 and `knowledge_free_teacher` is at
    # line 88, so the two never touch the same region and `patch` absorbs the offset.
    b0 = open(os.path.join(REPO, "tools", "build_attachment_validities.py"), encoding="utf-8").read()
    b1 = b0
    b2 = b1
    a = "def knowledge_free_teacher(train, rounds=2, beta=0.0, tsp_asset=None):"
    assert b2.count(a) == 1, "anchor knowledge_free_teacher"
    b2 = b2.replace(a, "def knowledge_free_teacher(train, rounds=2, beta=0.0, tsp_asset=None, pp_assoc=None):", 1)
    a = "    meaning = AA.SemanticBootstrapTeacher(beta=beta, lam=m.lam, tsp_asset=tsp_asset)"
    assert b2.count(a) == 1, "anchor teacher construction"
    b2 = b2.replace(a, "    # the NOMINAL HOST SLOT needs the noun side of the association while the arm is LEARNING\n"
                       "    meaning = AA.SemanticBootstrapTeacher(beta=beta, lam=m.lam, tsp_asset=tsp_asset, pp_assoc=pp_assoc)", 1)
    d += list(difflib.unified_diff(b1.split("\n"), b2.split("\n"),
                                   fromfile="a/tools/build_attachment_validities.py",
                                   tofile="b/tools/build_attachment_validities.py", lineterm="", n=3))
    text = "\n".join(d) + "\n"
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return text


def two_sided_diff(main_diff_path, out_path, n_sent: int = 30) -> int:
    """Emit the second diff and CHECK IT: execute the patched module and compare its acquisition teacher's score
    matrix, arc for arc, with the two-sided teacher this cell measured."""
    import types
    text = _emit_two_sided(main_diff_path, out_path)
    print("  wrote %s (%d lines)" % (out_path, text.count("\n")))
    src0 = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8").read()
    main = open(main_diff_path, encoding="utf-8").read().split("\n")
    src1 = _apply_unified(src0, main, "hdlab/attachment_arm.py")
    src2 = _apply_unified(src1, text.split("\n"), "hdlab/attachment_arm.py")
    mod = types.ModuleType("attachment_arm_two_sided")
    mod.__file__ = os.path.join(REPO, "hdlab", "attachment_arm.py")
    exec(compile(src2, mod.__file__, "exec"), mod.__dict__)
    S = mod.obl_slot_store()
    print("  patched module executes; oblique store: %d predicate-prep slots, %d filler cells, %.0f observations"
          % (len(S["d"]), len(S["c"]), S["tot"]))
    train = sentences(TRAIN, cap=n_sent * 4)
    assoc, _ = mine([(t, p) for t, p, _, _ in train], rounds=1)
    v2 = {"c": dict(assoc.c), "d": dict(assoc.d), "cc": dict(assoc.cc), "dc": dict(assoc.dc), "cp": dict(assoc.cp),
          "tot": assoc.tot, "m1": assoc.m1, "m2": assoc.m2, "o": dict(assoc.o), "od": dict(assoc.od),
          "oc": dict(assoc.oc), "ocd": dict(assoc.ocd), "og": dict(assoc.og), "otot": assoc.otot}
    OB = OblSlotPreference.from_grown_store()
    ours = AA.SemanticBootstrapTeacher(beta=10.0)
    theirs = mod.SemanticBootstrapTeacher(beta=10.0, pp_assoc=v2)
    activate(assoc, 6, Z_EDGES, False, True, "oblteach", "share", True, False, OB, False, 6.0)
    worst = 0.0; checked = 0
    try:
        for (tk, ps, _, _) in train[:n_sent]:
            A1, n1 = AA.SemanticBootstrapTeacher.score_matrix(ours, tk, ps)
            A2, n2 = theirs.score_matrix(tk, ps)
            fin = np.isfinite(A1) & np.isfinite(A2)
            if n1 != n2 or not np.array_equal(np.isfinite(A1), np.isfinite(A2)):
                worst = 1e9
            elif fin.any():
                worst = max(worst, float(np.abs(A1[fin] - A2[fin]).max()))
            checked += 1
    finally:
        deactivate_to_head()
    print("  two-sided teacher: the patch vs what this cell measured, %d sentences, max |delta| = %.2e"
          % (checked, worst))
    ok = worst < 1e-9
    print("  TWO-SIDED PATCH EQUIVALENCE:", "PASS" if ok else "FAIL")
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


# ---------------------------------------------------------------------------------------------------------------
# A BUG FOUND IN PHASE 7, AND THE FIX: the post-hoc diagnostics were reading every table with its own cue OFF.
# ---------------------------------------------------------------------------------------------------------------
# `main` runs each arm inside `try: ... finally: deactivate_to_head()`, so by the time `roles_diag`,
# `gap_decomposition` and `label_transfer` run -- after the arm loop -- `AA.arc_scores`, `AA.SentenceCues` and
# `AA.CONSTRUCTIONS` are back to the module's own defaults.  Those three diagnostics therefore evaluated the
# objgen TABLE with no PP cue, no thematic cue and no genitive construction: the learned validities were present but
# nothing ever fired them.  Any number they produced was a different arm from the one the headline measured (it shows
# up as objgen's gap-decomposition CORRECT count, 220, being BELOW base's 229 while its measured nmod recall is
# higher).  `arm_context` puts the arm back on for the duration of a diagnostic, so a diagnostic reads exactly the
# arm the headline reads.
class arm_context:
    """Re-install an arm's cue configuration for a post-hoc diagnostic, then restore HEAD."""

    def __init__(self, cfg: Optional[dict], k_cap: int = 6, zform: str = ZFORM, typed: bool = False):
        self.cfg = cfg; self.k_cap = k_cap; self.zform = zform; self.typed = typed

    def __enter__(self):
        c = self.cfg
        if not c or (c.get("assoc") is None and not c.get("casefix") and not c.get("gen") and not c.get("ref")
                     and not c.get("slot_cue") and not c.get("beta_nom")):
            deactivate_to_head()
        else:
            activate(c.get("assoc"), self.k_cap, Z_EDGES, self.typed, c.get("obj", False), c.get("casefix", False),
                     c.get("zform", self.zform), c.get("gen", False), c.get("ref", False), c.get("slot"),
                     c.get("slot_cue", False), c.get("beta_nom", 0.0))
        return self

    def __exit__(self, *exc):
        deactivate_to_head()
        return False


def roles_diag(tables: Dict[str, object], test, decode: str = "incr", cfgs: Optional[dict] = None,
               k_cap: int = 6) -> dict:
    """HEADS -> LABELS. 283 gold nmod are labelled `obl` by the role competition under the base heads. Is that the
    labeler's CUE SET (it reads head class x order, so a nominal hanging off a verb looks oblique whatever the head
    rung says) or the HEAD HAND-OFF (the head is simply wrong)? The decisive control is the role competition run on
    GOLD heads: if the confusion survives gold heads it is the cue set, if it disappears it is the hand-off."""
    from hdlab.graded_role_assigner import coarse_roles, load_coarse_validities, NOMINAL as RNOM
    rtab = load_coarse_validities()
    old = AA.DECODE
    AA.DECODE = decode
    out = {}
    try:
        for name, tab in tables.items():
            conf = defaultdict(int); head_ok = defaultdict(lambda: [0, 0])
            ctx = arm_context((cfgs or {}).get(name), k_cap); ctx.__enter__()
            for toks, pos, gold, rels in test:
                if name == "GOLD-HEADS":
                    hd = {i: gold[i - 1] for i in range(1, len(toks) + 1) if 0 <= gold[i - 1] <= len(toks)}
                    post = {i: {hd[i]: 1.0} for i in hd}
                else:
                    A, n = AA.arc_scores(toks, pos, tab)
                    hd, post = AA.decode(toks, pos, A, n, 1.0, tab)
                dep = coarse_roles(toks, pos, hd, rtab, post)
                for i in range(1, len(toks) + 1):
                    if pos[i - 1] not in RNOM or rels[i - 1] not in ("obl", "nmod"):
                        continue
                    got = dep.get(i, "dep")
                    conf[rels[i - 1] + "->" + got] += 1
                    ok = int(hd.get(i, -1) == gold[i - 1])
                    head_ok[rels[i - 1] + ("|headOK" if ok else "|headBAD")][0] += 1
                    head_ok[rels[i - 1] + ("|headOK" if ok else "|headBAD")][1] += int(got == rels[i - 1])
            ctx.__exit__()
            out[name] = {"confusions": dict(sorted(conf.items(), key=lambda kv: -kv[1])[:10]),
                         "label_recall_by_head_correctness": {k: [v[0], v[1], round(v[1] / max(1, v[0]), 3)]
                                                              for k, v in sorted(head_ok.items())}}
    finally:
        AA.DECODE = old
    return out


# ---------------------------------------------------------------------------------------------------------------
# THE HEADS -> LABELS HAND-OFF (phase 7: does the head gain reach the relation the consumer reads?)
# ---------------------------------------------------------------------------------------------------------------
# UD's own definition of the distinction this problem is about: a case-marked nominal is `obl` when its HOST is a
# PREDICATE (a verb, an auxiliary, or a predicate adjective -- "capable OF x") and `nmod` when its host is a NOMINAL.
# The distinction is therefore a pure function of the HOST'S CATEGORY, i.e. of exactly what the heads rung decides.
# The brain's counterpart is the same: "with the telescope" is an INSTRUMENT of an event when a predicate licenses it
# and a PROPERTY of a thing when a nominal does (Talmy's figure/ground; the Competition Model's case cue is read
# against the licensing host, not against the phrase).  A consumer that reads the host's category converts every head
# gain on this population into a label gain one-for-one.  A consumer whose role inventory has no NMOD class cannot.
PRED_HEAD_CATS = frozenset({"VERB", "AUX", "ADJ", "ADV"})


def head_derived_label(pos: Sequence[str], h: int) -> str:
    """obl / nmod read off the HOST'S CATEGORY -- the distinction's definition, and all a consumer needs."""
    if not h or h <= 0 or h > len(pos):
        return "root"
    return "obl" if pos[h - 1] in PRED_HEAD_CATS else "nmod"


def label_transfer(tables: Dict[str, object], test, decode: str = "incr", cfgs: Optional[dict] = None,
                   k_cap: int = 6):
    """Trace the hand-off two ways, on the gold obl+nmod population.

    (1) THE ORGAN AS BUILT -- `graded_role_assigner.coarse_roles`.  Its inventory is ROLE_CLASSES =
        [SUBJ, OBJ, PASS_SUBJ, BY_AGENT, OBL, OTHER, IOBJ] and ROLE_TO_DEP can emit only
        nsubj / nsubj:pass / obj / iobj / obl / obl:agent / dep -- there is NO nmod class.  So a gold nmod is
        counted wrong whatever the heads rung hands down.  Measured here, not asserted, including under GOLD HEADS.
    (2) A CONSUMER THAT CAN EXPRESS THE DISTINCTION -- `head_derived_label`.  This says how much of the head gain is
        AVAILABLE to a label rung, i.e. whether the gain is real signal or an artefact of the head metric.

    Returns (summary, per-sentence records per arm) so the derived label can be bootstrapped paired over sentences
    exactly like every other number in this cell."""
    from hdlab.graded_role_assigner import coarse_roles, load_coarse_validities, NOMINAL as RNOM, ROLE_TO_DEP
    rtab = load_coarse_validities()
    old = AA.DECODE
    AA.DECODE = decode
    out: Dict[str, dict] = {"_inventory": {"emittable_deps": sorted(set(ROLE_TO_DEP.values())),
                                           "has_nmod_class": "nmod" in set(ROLE_TO_DEP.values())}}
    recs_by_arm: Dict[str, List[dict]] = {}
    heads_by_arm: Dict[str, List[dict]] = {}
    try:
        for name, tab in tables.items():
            organ = defaultdict(lambda: [0, 0])       # gold rel -> [n, organ-correct]
            deriv = defaultdict(lambda: [0, 0])       # gold rel -> [n, derived-label-correct]
            recs: List[dict] = []
            hmap: List[dict] = []
            ctx = arm_context((cfgs or {}).get(name), k_cap); ctx.__enter__()
            for si, (toks, pos, gold, rels) in enumerate(test):
                if name == "GOLD-HEADS":
                    hd = {i: gold[i - 1] for i in range(1, len(toks) + 1) if 0 <= gold[i - 1] <= len(toks)}
                    post = {i: {hd[i]: 1.0} for i in hd}
                else:
                    A, n = AA.arc_scores(toks, pos, tab)
                    hd, post = AA.decode(toks, pos, A, n, 1.0, tab)
                dep = coarse_roles(toks, pos, hd, rtab, post)
                rec = {"n": 0, "hit": 0, "rel": defaultdict(lambda: [0, 0])}
                hh = {}
                for i in range(1, len(toks) + 1):
                    r = rels[i - 1]
                    if r not in ("obl", "nmod"):
                        continue
                    lab = head_derived_label(pos, hd.get(i, 0))
                    ok = int(lab == r)
                    deriv[r][0] += 1; deriv[r][1] += ok
                    rec["n"] += 1; rec["hit"] += ok
                    rec["rel"][r][0] += 1; rec["rel"][r][1] += ok
                    hh[i] = (int(hd.get(i, -1) == gold[i - 1]), lab, r)
                    if pos[i - 1] in RNOM:
                        organ[r][0] += 1; organ[r][1] += int(dep.get(i, "dep") == r)
                rec["rel"] = {k: v for k, v in rec["rel"].items()}
                recs.append(rec); hmap.append(hh)
            ctx.__exit__()
            recs_by_arm[name] = recs; heads_by_arm[name] = hmap
            out[name] = {
                "organ_recall": {k: [v[0], v[1], round(v[1] / max(1, v[0]), 4)] for k, v in sorted(organ.items())},
                "head_derived_recall": {k: [v[0], v[1], round(v[1] / max(1, v[0]), 4)] for k, v in sorted(deriv.items())},
                "head_derived_overall": round(sum(v[1] for v in deriv.values()) / max(1, sum(v[0] for v in deriv.values())), 4)}
    finally:
        AA.DECODE = old
    # WHICH GAINS SURVIVE: the per-token transfer table between the floor arm and every other arm.
    if "base" in heads_by_arm:
        for name, hmap in heads_by_arm.items():
            if name == "base":
                continue
            t = defaultdict(int)
            for hb, ha in zip(heads_by_arm["base"], hmap):
                for i, (ok_b, lab_b, r) in hb.items():
                    ok_a, lab_a, _ = ha.get(i, (0, "root", r))
                    t["head_%s_%s" % ("OK" if ok_b else "BAD", "OK" if ok_a else "BAD")] += 1
                    t["label_%s_%s" % ("OK" if lab_b == r else "BAD", "OK" if lab_a == r else "BAD")] += 1
                    if not ok_b and ok_a:                       # a head the change REPAIRED
                        t["repaired_head"] += 1
                        t["repaired_head_label_" + ("gained" if (lab_b != r and lab_a == r) else
                                                    "already_right" if lab_b == r else "still_wrong")] += 1
                    if ok_b and not ok_a:
                        t["broke_head"] += 1
                        t["broke_head_label_" + ("lost" if (lab_b == r and lab_a != r) else "unchanged")] += 1
            out[name]["transfer_vs_base"] = dict(sorted(t.items()))
    return out, recs_by_arm


def gap_decomposition(table, assoc: Optional[PPAssoc], test, decode: str = "incr", k_cap: int = 6,
                      obj_cue: bool = True, cfg: Optional[dict] = None) -> dict:
    """WHERE THE REMAINING SIGNAL IS LOST, per gold obl/nmod token, with counts. Four mutually exclusive causes:
      NOT_CASE_MARKED  the detector does not see a case-marked nominal here at all (bare adverbials, possessives that
                       the genitive construction handles instead, appositions) -- out of this cue's reach;
      NOT_RETRIEVED    detected, but the gold host is not in the retrieved candidate set (beyond the capacity cap,
                       or across a sentence boundary);
      ASSOCIATION      detected and retrievable, but the association ranks another candidate above the gold host --
                       the cue's OWN error, the only bucket more reading or a better association can fix;
      DECODE           detected, retrievable, the association ranks the gold host FIRST, and the arc is still lost --
                       the rest of the competition (locality, constructions, the tree/beam) overrules it."""
    old = AA.DECODE
    AA.DECODE = decode
    cause = defaultdict(int); tot = defaultdict(int)
    ctx = arm_context(cfg, k_cap); ctx.__enter__()
    try:
        for toks, pos, gold, rels in test:
            hd = AA.heads(toks, pos, table)
            sites = {obj: (prep, c) for prep, obj, c in pp_sites(toks, pos, k_cap)}
            for i in range(1, len(toks) + 1):
                r = rels[i - 1]
                if r not in ("obl", "nmod"):
                    continue
                tot[r] += 1
                if hd.get(i, -1) == gold[i - 1]:
                    cause[r + ":CORRECT"] += 1
                    continue
                if i not in sites:
                    cause[r + ":NOT_CASE_MARKED"] += 1
                    continue
                prep, cands = sites[i]
                if gold[i - 1] not in cands:
                    cause[r + ":NOT_RETRIEVED"] += 1
                    continue
                if assoc is None:
                    cause[r + ":DECODE"] += 1
                    continue
                p = toks[prep - 1].lower(); oc = obj_class(toks, pos, i)
                best, bs = None, -1e18
                for q in cands:
                    v = math.log(max(assoc.p_given(host_key(toks, pos, q), host_class(toks, pos, q), p), 1e-12))
                    if obj_cue:
                        v += math.log(max(assoc.p_obj(host_type(pos[q - 1]), p, oc), 1e-12))
                    if v > bs:
                        best, bs = q, v
                cause[r + (":DECODE" if best == gold[i - 1] else ":ASSOCIATION")] += 1
    finally:
        ctx.__exit__()
        AA.DECODE = old
    out = {"totals": dict(tot)}
    for r in ("obl", "nmod"):
        out[r] = {k.split(":")[1]: v for k, v in sorted(cause.items()) if k.startswith(r + ":")}
        out[r + "_share"] = {k: round(v / max(1, tot[r]), 3) for k, v in out[r].items()}
    return out


def capacity_probe(test, caps=(4, 6, 8, 12, 24)) -> dict:
    """WHY THE CAPACITY CAP IS NOT BINDING -- the distribution the sweep only summarised.

    `pp_sites` scans LEFT from the preposition and STOPS at a sentence-final mark, offering every open host it meets.
    The question the K-sweep answered empirically (K = 6 and K = 12 retrieve the identical 556 tokens) has a
    structural cause, and this probe measures it: how many open hosts actually exist to the left of a preposition
    inside its own sentence, and at what RANK the gold host sits. Lewis & Vasishth's capacity limit only bites when
    the candidate set is bigger than the limit."""
    from collections import Counter
    n_c = Counter(); rank = Counter(); tot = 0; found = 0
    for toks, pos, gold, rels in test:
        for prep, obj, cands in pp_sites(toks, pos, 10 ** 6):     # UNCAPPED retrieval
            if rels[obj - 1] not in ("obl", "nmod"):
                continue
            tot += 1
            n_c[min(len(cands), 25)] += 1
            g = gold[obj - 1]
            if g in cands:
                found += 1
                rank[min(cands.index(g) + 1, 25)] += 1
    cum = {}; run = 0
    for r in sorted(rank):
        run += rank[r]; cum[r] = round(run / max(1, tot), 4)
    return {"sites_on_gold_obl_nmod": tot, "gold_host_present_uncapped": found,
            "candidate_set_size_histogram": dict(sorted(n_c.items())),
            "sites_with_more_than_6_candidates": sum(v for k, v in n_c.items() if k > 6),
            "gold_host_rank_histogram": dict(sorted(rank.items())),
            "cumulative_recall_by_rank": cum,
            "recall_at_K": {K: round(sum(v for k, v in rank.items() if k <= K) / max(1, tot), 4) for K in caps}}


def flip_diag(tables: Dict[str, object], test, rels_of_interest, decode: str = "incr",
              cfgs: Optional[dict] = None, k_cap: int = 6) -> dict:
    """WHICH TOKENS OF A RELATION FLIP, AND WHERE THEY GO -- for understanding a regression instead of reporting it.

    For every gold token of the named relations, compare the floor arm's head with each other arm's head and
    classify: kept-right, kept-wrong, BROKEN (right -> wrong) or REPAIRED (wrong -> right); for the broken ones,
    record the CATEGORY of the head they moved to and whether the token sits inside a retrieved PP site or a
    genitive arc, which is the only way the change could have reached it."""
    old = AA.DECODE
    AA.DECODE = decode
    heads_by_arm: Dict[str, List[dict]] = {}
    marks: List[dict] = []
    try:
        for name, tab in tables.items():
            ctx = arm_context((cfgs or {}).get(name), k_cap); ctx.__enter__()
            per = []
            for toks, pos, gold, rels in test:
                hd = AA.heads(toks, pos, tab)
                per.append({i: (hd.get(i, -1), gold[i - 1], rels[i - 1]) for i in range(1, len(toks) + 1)
                            if rels[i - 1] in rels_of_interest})
                if name == list(tables)[0]:
                    sites = {obj for _, obj, _ in pp_sites(toks, pos, k_cap)}
                    gens = {d for _h, d in genitive_arcs(toks, pos)}
                    marks.append({"pos": pos, "sites": sites, "gens": gens})
            ctx.__exit__()
            heads_by_arm[name] = per
    finally:
        AA.DECODE = old
    floor = list(tables)[0]
    out = {}
    for name in tables:
        if name == floor:
            continue
        c = defaultdict(int); moved = defaultdict(int); reach = defaultdict(int)
        for si, (f, a2) in enumerate(zip(heads_by_arm[floor], heads_by_arm[name])):
            pos = marks[si]["pos"]
            for i, (hf, g, r) in f.items():
                ha = a2[i][0]
                okf, oka = hf == g, ha == g
                c[r + (":kept_right" if okf and oka else ":BROKEN" if okf else
                       ":REPAIRED" if oka else ":kept_wrong")] += 1
                if okf and not oka:
                    moved[r + " -> head=" + (pos[ha - 1] if 1 <= ha <= len(pos) else "ROOT")] += 1
                    reach[r + (":in_pp_site" if i in marks[si]["sites"] else
                               ":in_genitive" if i in marks[si]["gens"] else ":NOT_REACHED_BY_THE_CHANGE")] += 1
        out[name] = {"flips": dict(sorted(c.items())),
                     "broken_moved_to": dict(sorted(moved.items(), key=lambda kv: -kv[1])[:8]),
                     "broken_reachability": dict(sorted(reach.items()))}
    return out


def coverage_probe(test, k_cap: int = 6) -> dict:
    """WHAT THE CASE-MARKED-NOMINAL DETECTOR STILL CANNOT SEE, and WHY, with counts.

    A preposition is only ONE of the ways English marks a nominal oblique.  The genitive is a second (this cell added
    it).  A third is SEMANTIC: a bare temporal or measure nominal -- "last year", "three times", "Monday", "home" --
    is an oblique with no case marker at all, and every language that lets this happen lets it happen for exactly
    these semantic classes (Bates & MacWhinney's cue coalitions: when the morphological cue is absent the semantic
    cue carries the same job; UD calls these `obl` with no `case` child).  This probe breaks the UNDETECTED gold
    obl/nmod population down by the token's own WordNet supersense so the next case cue can be chosen by size, not
    by guess.  Instrument only: the gold tree selects the population, nothing is learned from it."""
    from hdlab.typed_selectional_preference import noun_supersense
    miss = defaultdict(lambda: defaultdict(int)); tot = defaultdict(int); det = defaultdict(int)
    gen_covered = defaultdict(int)
    for toks, pos, gold, rels in test:
        sites = {obj for _, obj, _ in pp_sites(toks, pos, k_cap)}
        gens = {d for _h, d in genitive_arcs(toks, pos)}
        for i in range(1, len(toks) + 1):
            r = rels[i - 1]
            if r not in ("obl", "nmod"):
                continue
            tot[r] += 1
            if i in sites:
                det[r] += 1
                continue
            if i in gens:
                gen_covered[r] += 1
                continue
            cat = pos[i - 1]
            ss = noun_supersense(toks[i - 1]) if cat in ("NOUN", "PROPN") else None
            miss[r]["%s/%s" % (cat, ss or "-")] += 1
    out = {"totals": dict(tot), "detected_by_preposition": dict(det),
           "covered_by_the_genitive_construction": dict(gen_covered)}
    for r in ("obl", "nmod"):
        rows = sorted(miss[r].items(), key=lambda kv: -kv[1])
        out[r + "_undetected_by_class"] = dict(rows[:14])
        out[r + "_undetected_total"] = sum(v for _, v in rows)
    return out


NEAR_W = 1.0          # the weight of the locality term in the rank probe (swept by --near-w, never adopted)


def rank_probe(assoc: Optional[PPAssoc], test, k_cap: int = 6, slot=None, channels=("assoc",),
               ref: bool = False) -> dict:
    """THE CHANNEL'S OWN RANKING ACCURACY, with no table and no decode in the way.

    The organ's per-relation recall confounds three things: whether the case-marked nominal is DETECTED, whether the
    gold host is RETRIEVED, and whether the association RANKS it first -- and then the tree decode can still overrule
    all three.  This probe holds the first two fixed and asks only the third: over the gold obl+nmod tokens whose gold
    host IS in the retrieved candidate set, how often does a given combination of channels put the gold host on top?
    It is an INSTRUMENT (it reads the gold tree to select the population and to score), never a build, and it is the
    cheapest honest way to tell "the channel has no signal" apart from "the decode threw the signal away"."""
    hit = defaultdict(int); tot = defaultdict(int)
    for toks, pos, gold, rels in test:
        for prep, obj, cands in pp_sites(toks, pos, k_cap):
            r = rels[obj - 1]
            if r not in ("obl", "nmod"):
                continue
            g = gold[obj - 1]
            if g not in cands:
                continue
            pw = toks[prep - 1].lower(); oc = obj_class(toks, pos, obj)
            best, bs = None, -1e18
            for q in cands:
                v = 0.0
                if "assoc" in channels and assoc is not None:
                    v += math.log(max(assoc.p_given(host_key(toks, pos, q), host_class(toks, pos, q), pw), 1e-12))
                if "ppobj" in channels and assoc is not None:
                    v += math.log(max(assoc.p_obj(host_type(pos[q - 1]), pw, oc), 1e-12))
                if "slot" in channels and slot is not None and pos[q - 1] == "VERB":
                    z = slot.logspec(lemma_verb(toks[q - 1]).lower(), pw, oc)
                    if z is not None:
                        v += z
                if "near" in channels:
                    # LOCALITY as the arm carries it: activation decays with the distance back to the host
                    # (Lewis & Vasishth 2005 retrieval decay; Gibson 1998 DLT).  NEAR_W is swept, never adopted.
                    v += -NEAR_W * math.log(1.0 + (prep - q))
                if v > bs:
                    best, bs = q, v
            tot[r] += 1; hit[r] += int(best == g)
            tot["all"] += 1; hit["all"] += int(best == g)
    return {k: [tot[k], hit[k], round(hit[k] / max(1, tot[k]), 4)] for k in ("all", "obl", "nmod")}


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

    # ---- phase 7: the OBLIQUE-SLOT selectional channel, the referential wiring, and the heads->labels readout ----
    O = OblSlotPreference()
    O.observe("eat", "with", "artifact", 20.0); O.observe("eat", "with", "food", 1.0)
    O.observe("go", "with", "person", 20.0); O.observe("go", "with", "food", 1.0)
    ck("the oblique-slot channel prefers the filler class its own predicate was seen with",
       O.logspec("eat", "with", "artifact") > O.logspec("go", "with", "artifact"))
    ck("a predicate never seen in this slot ABSTAINS rather than guessing",
       O.logspec("sleep", "with", "artifact") is None)
    O2 = O.scramble(1)
    ck("the oblique-slot twin keeps every count and marginal; only the predicate->profile map is destroyed",
       abs(O2.tot - O.tot) < 1e-9 and dict(O2.cg) == dict(O.cg) and len(O2.d) == len(O.d)
       and sorted(O2.c.values()) == sorted(O.c.values()))
    tk = "She ate the pizza with a fork .".split()
    ps = ["PRON", "VERB", "DET", "NOUN", "ADP", "DET", "NOUN", "PUNCT"]
    sv = ppslot_values(tk, ps, O)
    ck("the oblique-slot cue fires on the retrieved candidate arcs and abstains on non-predicate hosts",
       bool(sv) and all(k[1] == 7 for k in sv) and sv.get((4, 7)) == "na", sv)
    if os.path.isfile(BF_SLOT_STORE):
        G = OblSlotPreference.from_grown_store()
        st = G.stats()
        ck("the grown store really carries oblique slots (the first submission parked this for want of one)",
           st["predicate_prep_slots"] > 1000 and st["observations"] > 10000, st)
        ck("a KNOWN FACT falls out of the grown oblique store with no supervision anywhere: live-in-<location> "
           "outranks live-in-<food>",
           (G.logspec("live", "in", "noun.location") or -9.0) > (G.logspec("live", "in", "noun.food") or -9.0),
           (G.logspec("live", "in", "noun.location"), G.logspec("live", "in", "noun.food")))
    # the referential cue must actually REACH the arm: before this fix a ref-only arm silently reduced to `base`
    activate(None, ref_cue=True)
    try:
        sc_ref = AA.SentenceCues(tk, ps, {})
        ck("a referential-only arm installs the widened cue pass and the fast path (the phase-7 wiring fix)",
           isinstance(sc_ref, PPCues) and bool(sc_ref.ppref_arc) and AA.arc_scores is arc_scores_pp,
           (type(sc_ref).__name__, len(getattr(sc_ref, "ppref_arc", {}))))
        ck("the referential cue reads definiteness off the candidate host's own determiner",
           host_definiteness(tk, ps, 4) == "def" and host_definiteness(tk, ps, 2) == "na",
           (host_definiteness(tk, ps, 4), host_definiteness(tk, ps, 2)))
    finally:
        deactivate_to_head(cache=False)
    # Pinker's THIRD SLOT in the acquisition teacher: it must re-score the case-marked nominal, and it must NEVER
    # zero the verb's pull (section 5(b): the over-broad guard is the arm's only oblique-argument teacher).
    Ot = OblSlotPreference()
    Ot.observe("eat", "with", "noun.artifact", 40.0); Ot.observe("eat", "with", "noun.food", 1.0)
    ck("the oblique slot scores on the object slot's 0..1 scale, 0.5 = no preference",
       0.5 < (Ot.oblique_plausibility("eat", "with", "noun.artifact") or 0) < 1.0
       and (Ot.oblique_plausibility("eat", "with", "noun.food") or 1) < 0.5,
       (Ot.oblique_plausibility("eat", "with", "noun.artifact"), Ot.oblique_plausibility("eat", "with", "noun.food")))
    ck("an unseen predicate leaves the teacher's own value in place (the pull is re-scored, never removed)",
       Ot.oblique_plausibility("sleep", "with", "noun.artifact") is None)
    _tea = AA.SemanticBootstrapTeacher(beta=10.0)
    tk3 = "She ate the pizza with a fork .".split()
    ps3 = ["PRON", "VERB", "DET", "NOUN", "ADP", "DET", "NOUN", "PUNCT"]
    p_before = _ORIG_SLOT_PLAUS(_tea, tk3, ps3, 2, 7)
    activate(None, casefix="oblteach", slot=Ot)
    try:
        p_after = AA.SemanticBootstrapTeacher.slot_plausibility(_tea, tk3, ps3, 2, 7)
        ck("the third slot reaches the ACQUISITION teacher (it is applied inside score_matrix too, unlike the two "
           "refuted read-time-only forms)", p_after != p_before, (p_before, p_after))
        ck("a nominal that is NOT case-marked is untouched by the third slot",
           AA.SentenceCues is cached_cues
           and AA.SemanticBootstrapTeacher.slot_plausibility(_tea, tk3, ps3, 2, 4)
           == _ORIG_SLOT_PLAUS(_tea, tk3, ps3, 2, 4))
    finally:
        deactivate_to_head(cache=False)
    # REGRESSION GUARD for the phase-7 bug: the post-hoc diagnostics used to read every table with its own cue OFF,
    # because `main` deactivates the arm before they run.  `arm_context` must put it back.
    ck("a diagnostic runs with the arm's own cue ON (arm_context), not with the module defaults",
       AA.arc_scores is _ORIG_ARC_SCORES)
    with arm_context({"assoc": assoc, "obj": True, "gen": True}) as _c:
        ck("arm_context installs the widened cue pass, the fast path and the genitive construction",
           AA.arc_scores is arc_scores_pp and "gen" in AA.CONSTRUCTIONS and "ppobj" in AA.CUES,
           (AA.arc_scores is arc_scores_pp, list(AA.CONSTRUCTIONS), list(AA.CUES)))
    ck("arm_context restores HEAD on the way out",
       AA.arc_scores is _ORIG_ARC_SCORES and "gen" not in AA.CONSTRUCTIONS and AA.CUES == _ORIG_CUE_NAMES)
    with arm_context(None):
        ck("arm_context with no configuration is exactly HEAD (the floor arm)",
           AA.arc_scores is _ORIG_ARC_SCORES and AA.CUES == _ORIG_CUE_NAMES)
    ck("obl vs nmod is a pure function of the HOST'S category -- the distinction the label rung needs",
       head_derived_label(ps, 2) == "obl" and head_derived_label(ps, 4) == "nmod")
    from hdlab.graded_role_assigner import ROLE_TO_DEP as _R2D
    ck("MEASURED, not asserted: the downstream role organ has NO nmod class, so a gold nmod cannot be labelled "
       "correctly whatever the heads rung hands it", "nmod" not in set(_R2D.values()), sorted(set(_R2D.values())))

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
    ap.add_argument("--skip", type=int, default=0, help="skip the first N corpus lines (a disjoint reading slice)")
    ap.add_argument("--mine-out", default=None, help="where to write the mined / merged association")
    ap.add_argument("--merge-assoc", default=None, help="comma-separated associations to ADD together (more reading)")
    ap.add_argument("--assoc", default=None, help="use this association file instead of the pp_assoc_simplewiki_<lines> default")
    ap.add_argument("--live", action="store_true", help="also evaluate the LIVE chain (the category organ's own tags)")
    ap.add_argument("--save-asset", default=None, help="write the built table of --save-arm as an asset")
    ap.add_argument("--save-arm", default="objgen")
    ap.add_argument("--roles-diag", default="", help="comma-separated arms to run the heads->labels diagnostic on")
    ap.add_argument("--gap-decomp", default="", help="comma-separated arms to decompose the residual for")
    ap.add_argument("--coverage-probe", action="store_true", help="what the detector still cannot see, by class")
    ap.add_argument("--two-sided-diff", default=None, help="path to the MAIN diff; emits + checks the second diff")
    ap.add_argument("--two-sided-out", default=None, help="where to write the second diff")
    ap.add_argument("--capacity-probe", action="store_true", help="candidate-set sizes and gold-host ranks, uncapped")
    ap.add_argument("--flip-diag", default="", help="comma-separated relations to trace flips on (needs >=2 arms)")
    ap.add_argument("--rank-probe", action="store_true", help="channel ranking accuracy only: no table, no decode")
    ap.add_argument("--near-w", type=float, default=1.0, help="the locality weight in the rank probe (swept)")
    ap.add_argument("--label-transfer", default="", help="comma-separated arms to trace the heads->labels hand-off on")
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
    if a.two_sided_diff:
        return two_sided_diff(a.two_sided_diff, a.two_sided_out)
    if a.capacity_probe:
        test_k = sentences(TEST, cap=a.test_cap, maxlen=10 ** 6)
        cp = capacity_probe(test_k)
        print(json.dumps(cp, indent=1), flush=True)
        od = str(get_output_dir(ANCHOR)); os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, "capacity_probe%s.json" % (a.tag or "")), "w", encoding="utf-8") as f:
            json.dump({"anchor": ANCHOR, "probe": "capacity_probe", "test_cap": a.test_cap, "results": cp,
                       "hdlab_provenance": module_provenance(),
                       "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=1)
        return 0
    if a.coverage_probe:
        test_c = sentences(TEST, cap=a.test_cap, maxlen=10 ** 6)
        cv = coverage_probe(test_c, a.kcap)
        print(json.dumps(cv, indent=1), flush=True)
        od = str(get_output_dir(ANCHOR)); os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, "coverage_probe%s.json" % (a.tag or "")), "w", encoding="utf-8") as f:
            json.dump({"anchor": ANCHOR, "probe": "coverage_probe", "test_cap": a.test_cap, "results": cv,
                       "hdlab_provenance": module_provenance(),
                       "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=1)
        return 0
    if a.rank_probe:
        global NEAR_W
        NEAR_W = a.near_w
        test_r = sentences(TEST, cap=a.test_cap, maxlen=10 ** 6)
        with open(a.assoc or os.path.join(REPO, "data", "hook_state",
                                          "attachment_pp_assoc_v2_simplewiki100k_candidate.json"), encoding="utf-8") as f:
            A_ = PPAssoc.from_json(json.load(f))
        A_.m1 = a.m1; A_.m2 = a.m2
        S_ = OblSlotPreference.from_grown_store(m1=a.m1, m2=a.m2) if os.path.isfile(BF_SLOT_STORE) else None
        St_ = S_.scramble(a.seed) if S_ is not None else None
        A_tw = A_.scramble(a.seed)
        # THE FLOOR ON THIS POPULATION IS NOT ZERO AND IT IS NOT THE ASSOCIATION -- IT IS PROXIMITY.  The nearest open
        # host is right for 71% of the retrievable obl+nmod tokens (92% of nmod), because an nmod's host is usually the
        # noun immediately before the preposition.  The arm already carries that as its `locality` cue, so the only
        # question that matters for a NEW channel is what it adds ON TOP OF locality -- measured here, every channel
        # both alone and stacked on the locality floor, each against its own information-free twin.
        combos = [("locality only (the floor on this population)", A_, None, ("near",)),
                  ("association alone", A_, None, ("assoc",)),
                  ("association + thematic alone (the shipped pair)", A_, None, ("assoc", "ppobj")),
                  ("OBLIQUE SLOT alone", A_, S_, ("slot",)),
                  ("locality + association", A_, None, ("near", "assoc")),
                  ("locality + association + thematic", A_, None, ("near", "assoc", "ppobj")),
                  ("locality + OBLIQUE SLOT", A_, S_, ("near", "slot")),
                  ("locality + association + thematic + OBLIQUE SLOT", A_, S_, ("near", "assoc", "ppobj", "slot")),
                  ("TWIN of the shipped pair (scrambled association)", A_tw, None, ("assoc", "ppobj")),
                  ("TWIN on the locality floor (scrambled association)", A_tw, None, ("near", "assoc", "ppobj")),
                  ("TWIN of the oblique slot (scrambled predicates)", A_, St_, ("near", "slot")),
                  ("TWIN of everything on the locality floor", A_tw, St_, ("near", "assoc", "ppobj", "slot"))]
        out = {}
        for nm, aa, ss, ch in combos:
            out[nm] = rank_probe(aa, test_r, a.kcap, ss, ch)
            print("  RANK %-42s all %s  obl %s  nmod %s" % (nm, out[nm]["all"], out[nm]["obl"], out[nm]["nmod"]),
                  flush=True)
        od = str(get_output_dir(ANCHOR)); os.makedirs(od, exist_ok=True)
        mp_ = os.path.join(od, "rank_probe%s.json" % (a.tag or ""))
        out["_near_w"] = a.near_w
        with open(mp_, "w", encoding="utf-8") as f:
            json.dump({"anchor": ANCHOR, "probe": "rank_probe", "test_cap": a.test_cap, "kcap": a.kcap,
                       "slot_stats": (S_.stats() if S_ else None), "results": out,
                       "hdlab_provenance": module_provenance(),
                       "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f, indent=1)
        print("wrote", mp_, flush=True)
        return 0

    out_dir = str(get_output_dir(ANCHOR))
    os.makedirs(out_dir, exist_ok=True)
    PROV_START = module_provenance()
    print("hdlab provenance:", json.dumps(PROV_START["hdlab/attachment_arm.py"]),
          "pri97_cues=", PROV_START["pri97_root_cues_present"], flush=True)
    swpath = os.path.join(out_dir, "pp_assoc_simplewiki_%d.json" % a.lines)

    if a.mine_simplewiki:
        t0 = time.time()
        out = a.mine_out or swpath
        print("mining Simple-Wiki (%d lines, skip %d) with the substrate's own category organ ..." % (a.lines, a.skip),
              flush=True)
        assoc, st = mine(simplewiki_reading(a.lines, skip=a.skip), rounds=a.realloc, m1=a.m1, m2=a.m2,
                         k_cap=a.kcap, verbose=True)
        d = assoc.to_json(); d["mining"] = st; d["lines"] = a.lines; d["skip"] = a.skip
        d["elapsed_s"] = round(time.time() - t0, 1)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(d, f)
        print("wrote", out, st, "in %.0fs" % (time.time() - t0), flush=True)
        return 0

    if a.merge_assoc:
        # MORE READING = MORE COUNTS. The association is held as counts and the probability is a pure function of
        # them, so a second disjoint reading slice is merged by ADDING the counts -- exactly what `observe(...)`
        # does one outcome at a time. No refitting, no retraining: the plastic path.
        parts = [x for x in a.merge_assoc.split(",") if x]
        tot = PPAssoc(a.m1, a.m2)
        lines = 0
        for q in parts:
            with open(q, encoding="utf-8") as f:
                dq = json.load(f)
            A2 = PPAssoc.from_json(dq); lines += dq.get("lines", 0)
            for fld in ("c", "d", "cc", "dc", "cp", "o", "od", "oc", "ocd", "og"):
                dst = getattr(tot, fld)
                for k, v in getattr(A2, fld).items():
                    dst[k] = dst.get(k, 0.0) + v
            tot.tot += A2.tot; tot.otot += A2.otot
        d = tot.to_json()
        d["mining"] = {"merged_from": parts, "host_cells": len(tot.d), "assoc_cells": len(tot.c)}
        d["lines"] = lines
        with open(a.mine_out, "w", encoding="utf-8") as f:
            json.dump(d, f)
        print("merged", len(parts), "slices ->", a.mine_out, d["mining"], flush=True)
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
    if a.assoc:
        swpath = a.assoc
    if os.path.isfile(swpath):
        with open(swpath, encoding="utf-8") as f:
            dsw = json.load(f)
        assoc_sw = PPAssoc.from_json(dsw); assoc_sw.m1 = a.m1; assoc_sw.m2 = a.m2
        print("Simple-Wiki association loaded:", dsw.get("mining"), flush=True)

    legacy_pp = AA.pp_assoc_from_reading(ud_reading)      # the incumbent two-candidate association (the base arm)
    OBLSLOT = None
    if os.path.isfile(BF_SLOT_STORE):
        OBLSLOT = OblSlotPreference.from_grown_store(m1=a.m1, m2=a.m2)
        print("oblique-slot selectional channel (grown store):", OBLSLOT.stats(), flush=True)

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
        if name.startswith("landed:"):        # an asset ON DISK, loaded not rebuilt (the landed cap-6000 candidate)
            return {"assoc": None, "legacy": None, "obj": False, "casefix": False, "load": name.split(":", 1)[1]}
        if name == "flat":                        # CONTROL: the same arcs, a constant value (structure without content)
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "zform": "flat"}
        if name == "flatslot":
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "slot", "zform": "flat"}
        if name == "flatgen":
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "zform": "flat", "gen": True}
        if name == "ref":                         # ONLY the referential/definiteness cue
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": False, "ref": True}
        if name == "objgenref":                   # the shipped build + the referential cue
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False,
                    "gen": True, "ref": True}
        if name == "twingenref":
            src = assoc_sw or assoc_ud
            return {"assoc": src.scramble(a.seed), "legacy": None, "obj": True, "casefix": False,
                    "gen": True, "ref": True}
        if name.startswith("objgenoblnom"):       # BOTH SIDES of Pinker's bootstrapping in the teacher at once:
            # the oblique slot gives the VERB real oblique content and the nominal host slot gives the NOUN its vote.
            # Measured separately (12.5e/f) each one is a seesaw; the brain has both, so the pair is the honest build.
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "oblteach", "gen": True,
                    "slot": OBLSLOT, "beta_nom": float(name[12:].replace("_", ".") or 6.0)}
        if name.startswith("twinoblnom"):         # its INFORMATION-FREE TWIN: both stores scrambled
            _s2 = (assoc_sw or assoc_ud).scramble(a.seed)
            return {"assoc": _s2, "legacy": None, "obj": True, "casefix": "oblteach", "gen": True,
                    "slot": OBLSLOT.scramble(a.seed), "beta_nom": float(name[10:].replace("_", ".") or 6.0)}
        if name.startswith("objgennom"):          # the shipped build + the NOMINAL HOST SLOT in the teacher
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False, "gen": True,
                    "beta_nom": float(name[9:].replace("_", ".") or 4.0)}
        if name.startswith("twinnom"):            # its INFORMATION-FREE TWIN (scrambled association in both roles)
            _src = (assoc_sw or assoc_ud).scramble(a.seed)
            return {"assoc": _src, "legacy": None, "obj": True, "casefix": False, "gen": True,
                    "beta_nom": float(name[7:].replace("_", ".") or 4.0)}
        if name == "objgenoblboth":               # the third slot in the teacher AND as a read-time cue
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "oblteach",
                    "gen": True, "slot": OBLSLOT, "slot_cue": True}
        if name == "oblteach":                    # ONLY Pinker's third slot in the acquisition teacher
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": "oblteach", "slot": OBLSLOT}
        if name == "objgenoblteach":              # the shipped build + the third slot in the teacher
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "oblteach",
                    "gen": True, "slot": OBLSLOT}
        if name == "twinoblteach":                # INFORMATION-FREE TWIN of the third slot (scrambled predicates)
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": "oblteach",
                    "gen": True, "slot": OBLSLOT.scramble(a.seed)}
        if name == "slot":                        # ONLY the oblique-slot selectional channel (no association)
            return {"assoc": None, "legacy": legacy_pp, "obj": False, "casefix": False, "slot": OBLSLOT,
                    "slot_cue": True}
        if name == "objgenslot":                  # the shipped build + the lexical oblique-slot READ-TIME cue
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False,
                    "gen": True, "slot": OBLSLOT, "slot_cue": True}
        if name == "twinslotpref":                # INFORMATION-FREE TWIN of the oblique-slot read-time cue
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False,
                    "gen": True, "slot": OBLSLOT.scramble(a.seed), "slot_cue": True}
        if name == "objgenslotref":               # everything: association + thematic + genitive + slot + referential
            return {"assoc": assoc_sw or assoc_ud, "legacy": None, "obj": True, "casefix": False,
                    "gen": True, "slot": OBLSLOT, "slot_cue": True, "ref": True}
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
    built: Dict[str, object] = {}
    assoc_by_arm: Dict[str, object] = {}
    cfg_by_arm: Dict[str, dict] = {}
    for name in arms:
        cfg = arm_config(name)
        cfg.setdefault("load", None)
        if (name in ("slot", "objgenslot", "twinslotpref", "objgenslotref", "oblteach", "objgenoblteach",
                     "twinoblteach", "objgenoblboth") or name.startswith("objgenoblnom")
                or name.startswith("twinoblnom")) and OBLSLOT is None:
            print("SKIP arm %s: no grown slot store on disk (%s)" % (name, BF_SLOT_STORE), flush=True)
            continue
        if name in ("vol", "obj", "objslot", "objgen", "twin", "twinslot", "twingen", "all", "noclass", "maxform",
                    "flat", "flatslot", "flatgen", "objgenref", "twingenref", "objgenslot", "twinslotpref",
                    "objgenslotref", "objgenoblteach", "twinoblteach", "objgenoblboth") and cfg["assoc"] is None and assoc_sw is None:
            print("SKIP arm %s: no Simple-Wiki association on disk (%s)" % (name, swpath), flush=True)
            continue
        t1 = time.time()
        if (cfg["assoc"] is None and not cfg["casefix"] and not cfg.get("gen") and not cfg.get("ref")
                and cfg.get("slot") is None and not cfg.get("load")):
            deactivate_to_head()
        else:
            activate(cfg["assoc"], a.kcap, Z_EDGES, a.typed, cfg["obj"], cfg["casefix"],
                     cfg.get("zform", a.zform), cfg.get("gen", False), cfg.get("ref", False),
                     cfg.get("slot"), cfg.get("slot_cue", False), cfg.get("beta_nom", 0.0))
        try:
            if cfg["load"]:
                with open(cfg["load"], encoding="utf-8") as _f:
                    _doc = json.load(_f)
                tab = {"counts": _doc["counts"], "frames": _doc.get("frames", {}),
                       "pp_assoc": _doc.get("pp_assoc"), "pp_assoc_v2": _doc.get("pp_assoc_v2"),
                       "strength": AA.strengths_from_arc_counts(_doc["counts"])}
                print("  loaded asset", os.path.basename(cfg["load"]), flush=True)
            else:
                tab = build_table(train, teacher, rounds=a.rounds, alpha=a.alpha, pp_assoc_legacy=cfg["legacy"],
                                  tmarg_key=((str(cfg["casefix"]) + "|" + name) if (cfg["casefix"] or cfg.get("beta_nom")) else "plain"))
            results[name] = {"build_s": round(time.time() - t1, 1),
                             "pp_cue_cells": len(tab["counts"]["cues"].get("pp", {})),
                             "ppobj_cue_cells": len(tab["counts"]["cues"].get("ppobj", {})),
                             "pp_validity_by_value": validity_by_value(tab, "pp"),
                             "ppobj_validity_by_value": validity_by_value(tab, "ppobj"),
                             "ppref_validity_by_value": validity_by_value(tab, "ppref"),
                             "ppslot_validity_by_value": validity_by_value(tab, "ppslot"),
                             # the cues that carry the acquisition teacher's meaning budget, so the seesaw can be
                             # read off the LEARNED TABLES instead of inferred from the outcome
                             "plaus_validity_by_value": validity_by_value(tab, "plaus"),
                             "locality_validity_by_value": validity_by_value(tab, "locality"),
                             "constr_validity_by_value": validity_by_value(tab, "constr"),
                             "pp_ladder_spread": (lambda L: round(max(L.values()) - min(L.values()), 4) if L else None)(
                                 validity_by_value(tab, "pp"))}
            for dec in decodes:
                recs = per_sentence_hits(tab, test, dec)
                per_sent[(name, dec)] = recs
                results[name][dec] = summarise(recs)
                print("  %-6s %-5s UAS %.4f  obl %.3f  nmod %.3f  pp-subpop %.3f (n=%d)" % (
                    name, dec, results[name][dec]["UAS"], results[name][dec]["rel"].get("obl", 0),
                    results[name][dec]["rel"].get("nmod", 0), results[name][dec]["pp_subpop"],
                    results[name][dec]["pp_subpop_n"]), flush=True)
            built[name] = tab; assoc_by_arm[name] = cfg["assoc"]; cfg_by_arm[name] = dict(cfg)
            if a.live:
                for dec in decodes:
                    recs = per_sentence_hits_live(tab, test, dec)
                    per_sent[(name + "@live", dec)] = recs
                    results[name]["live_" + dec] = summarise(recs)
                    s2 = results[name]["live_" + dec]
                    print("  %-8s %-5s LIVE UAS %.4f  obl %.3f  nmod %.3f  pp-subpop %.3f" % (
                        name, dec, s2["UAS"], s2["rel"].get("obl", 0), s2["rel"].get("nmod", 0), s2["pp_subpop"]),
                        flush=True)
            if a.save_asset and name == a.save_arm:
                doc = {"source": "attachment arm, pri-94 build: soft arc counts from the knowledge-free + semantic-"
                                 "bootstrapping teacher with the parallelism and predication acquisition signals, "
                                 "PLUS the case-marked-nominal PP cue (association mined from unambiguous reading) "
                                 "and the genitive construction; strengths = strengths_from_arc_counts",
                       "counts": tab["counts"], "frames": tab.get("frames", {}), "pp_assoc": tab.get("pp_assoc"),
                       "pp_assoc_v2": (cfg["assoc"].to_json() if cfg["assoc"] is not None else None)}
                with open(a.save_asset, "w", encoding="utf-8", newline=chr(10)) as f:
                    json.dump(doc, f, indent=1)
                print("  wrote asset", a.save_asset, flush=True)
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
                if (name + "@live", dec) in per_sent and ("base@live", dec) in per_sent:
                    L0 = per_sent[("base@live", dec)]; L1 = per_sent[(name + "@live", dec)]
                    boots["%s|%s|live" % (name, dec)] = {
                        "UAS": paired_bootstrap(L0, L1, key_overall, a.boot),
                        "obl": paired_bootstrap(L0, L1, key_rel("obl"), a.boot),
                        "nmod": paired_bootstrap(L0, L1, key_rel("nmod"), a.boot),
                        "pp_subpop": paired_bootstrap(L0, L1, key_pp, a.boot),
                        "pp_subpop_obl": paired_bootstrap(L0, L1, key_pp_rel("obl"), a.boot),
                        "pp_subpop_nmod": paired_bootstrap(L0, L1, key_pp_rel("nmod"), a.boot)}
                    bl = boots["%s|%s|live" % (name, dec)]
                    print("  LIVE %-8s %-5s UAS %+.4f%s  obl %+.4f%s  nmod %+.4f%s" % (
                        name, dec, bl["UAS"]["delta"], "*" if bl["UAS"]["separated"] else " ",
                        bl["obl"]["delta"], "*" if bl["obl"]["separated"] else " ",
                        bl["nmod"]["delta"], "*" if bl["nmod"]["separated"] else " "), flush=True)
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

    if a.roles_diag:
        want = [x for x in a.roles_diag.split(",") if x]
        rd = roles_diag({k: v for k, v in built.items() if k in want} | {"GOLD-HEADS": None}, test, decodes[0],
                        cfg_by_arm, a.kcap)
        for k, v in rd.items():
            print("  ROLEDIAG %-10s %s" % (k, v["confusions"]), flush=True)
            print("           by head correctness: %s" % v["label_recall_by_head_correctness"], flush=True)
        results["roles_diag"] = rd
    if a.label_transfer:
        want = [x for x in a.label_transfer.split(",") if x]
        lt, lrecs = label_transfer({k: v for k, v in built.items() if k in want} | {"GOLD-HEADS": None},
                                   test, decodes[0], cfg_by_arm, a.kcap)
        print("  LABELXFER inventory %s" % lt["_inventory"], flush=True)
        for k, v in lt.items():
            if k == "_inventory":
                continue
            print("  LABELXFER %-10s organ %s | head-derived %s (overall %.4f)"
                  % (k, v["organ_recall"], v["head_derived_recall"], v["head_derived_overall"]), flush=True)
            if "transfer_vs_base" in v:
                print("            transfer vs base: %s" % v["transfer_vs_base"], flush=True)
        for nm in want:
            if nm == "base" or nm not in lrecs or "base" not in lrecs:
                continue
            bt = {"derived_overall": paired_bootstrap(lrecs["base"], lrecs[nm], key_overall, a.boot),
                  "derived_obl": paired_bootstrap(lrecs["base"], lrecs[nm], key_rel("obl"), a.boot),
                  "derived_nmod": paired_bootstrap(lrecs["base"], lrecs[nm], key_rel("nmod"), a.boot)}
            lt.setdefault("bootstrap", {})[nm] = bt
            print("  LABELXFER BOOT %-8s derived %+.4f%s  obl %+.4f%s  nmod %+.4f%s" % (
                nm, bt["derived_overall"]["delta"], "*" if bt["derived_overall"]["separated"] else " ",
                bt["derived_obl"]["delta"], "*" if bt["derived_obl"]["separated"] else " ",
                bt["derived_nmod"]["delta"], "*" if bt["derived_nmod"]["separated"] else " "), flush=True)
        results["label_transfer"] = lt
    if a.flip_diag:
        rl = tuple(x for x in a.flip_diag.split(",") if x)
        fd = flip_diag(built, test, rl, decodes[0], cfg_by_arm, a.kcap)
        for k, v in fd.items():
            print("  FLIP %-14s %s" % (k, v["flips"]), flush=True)
            print("       broken moved to: %s" % v["broken_moved_to"], flush=True)
            print("       broken reachability: %s" % v["broken_reachability"], flush=True)
        results["flip_diag"] = fd
    if a.gap_decomp:
        for nm in [x for x in a.gap_decomp.split(",") if x]:
            if nm not in built:
                continue
            gd = gap_decomposition(built[nm], assoc_by_arm.get(nm), test, decodes[0], a.kcap,
                                   cfg=cfg_by_arm.get(nm))
            print("  GAP %-9s obl %s" % (nm, gd["obl"]), flush=True)
            print("      %-9s nmod %s" % ("", gd["nmod"]), flush=True)
            results.setdefault("gap_decomposition", {})[nm] = gd

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
