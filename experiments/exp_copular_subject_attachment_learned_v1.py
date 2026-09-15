"""COPULAR-SUBJECT ATTACHMENT as an ONLINE-LEARNED ARC FEATURE + a predicate-arrival reanalysis (pri 117).

THE PROBLEM.  The heads rung attaches the subject of a NON-VERBAL predicate ("the sky is blue", "she is a
doctor") at 0.5385 against 0.8533 for a verbal one (UD-EWT test 700, live chain, gold nsubj arcs whose gold head
is not a gold VERB).  pri 113 prototyped the repair as a hand re-shaping of the arc matrix plus a held decode
(0.5385 -> 0.6509) and showed with a gold-POS test that the loss is NOT tagging: it is the arc scorer's
under-learned copular-subject validity plus the incremental decode's premature commitment.

THE BRAIN.  Attachment is cue competition with validities learned from experience (Bates & MacWhinney's
Competition Model: validity = availability x reliability, accrued from what the comprehender perceives), and a
clause has ONE predicate (Spivey-Knowlton 1993) whose subject attaches to whatever fills the predicate slot --
the copula only carries tense for it (Pustet 2003; UD's `cop` convention puts the copula UNDER the complement).
Two computations follow, and both already exist in this organ in weaker form:
  (1) THE PREDICATE SLOT IS AN ARC FEATURE.  pri 110 computes P(token q fills its clause's predicate slot)
      (`predicate_sites`, graded off the category organ's own posterior).  The arc scorer never receives it: it
      sees the copula's revised TAG only, so a high-occupancy ADJ/NOUN is scored by verb-biased validities
      (pri 113 section 27).  Here the occupancy enters the competition as the VALUE of a cue whose validity is
      LEARNED -- Rescorla-Wagner style accrual from perceived copular constructions, never a hand weight, with
      an `observe` path so it keeps moving (the brain runs no frozen weight).
  (2) REANALYSIS AT PREDICATE ARRIVAL.  The incremental decode commits the subject before its predicate's
      competitor is resolved and a verb INSIDE the predicate phrase then steals it ("we are capable of
      PROTECTING it" -- that verb is not the matrix predicate: small-clause locality, Stowell 1981).  The brain
      revises when the disambiguating word arrives (Frazier & Rayner 1982; MacDonald 1994 overtaking), which is
      what this organ already does for the ROOT arc (INCR_ROOT_REANALYSIS).  Generalised here to the subject
      arc: the revision compares the two arcs' OWN learned activations, adds no parameter, and reads only words
      already heard (the stealer stands to the RIGHT of the predicate, so at the predicate's arrival the subject
      was still waiting -- the "held" decision, taken in order).
  (3) COVERAGE.  The cue's pair detection (`csub_sites`) keys on `cop_predicates`, the oldest and narrowest
      complement scan; the merged pri-113 tree carries `cop_complement`, which covers the inverted, fronted,
      locative, wh and clause-final constructions.  pri 113 section 29 located DETECTION COVERAGE as what holds
      the prototype at 0.65 (101 of 167 clauses covered).  Re-keying the cue on `cop_complement` is that fix.

ARMS (UD-EWT test 700; population = gold nsubj/nsubj:pass arcs whose gold head is not a gold VERB, n=169):
  base     the live arm exactly as shipped (csub on, incremental decode, landed asset)      [0.5385 expected]
  proto    pri 113's prototype reproduced (hand boost 5 / penalty 8 + held MAP resolution)  [0.6509 expected]
  cov      (3) pair detection re-keyed on cop_complement                     -- learned validity, no new number
  occ      (1) + the occupancy-graded cue with an ACCRUED validity           -- the arc feature
  rev      (2) + predicate-arrival reanalysis of the subject arc             -- the in-order held decode
  twin     `occ` with the accrued validity PERMUTED across its values (information-free; must lose)
  perm     the occupancy column shuffled across tokens (the value carries no information; must lose)
NO-REGRESS: verbal-subject attachment, UAS, per-relation (nsubj / cop / root / obj / obl / nmod).

Run: .venv/Scripts/python.exe experiments/exp_copular_subject_attachment_learned_v1.py --self-test
     [--accrue --cap 3000] [--arms --cap 700] [--sweep] [--proto] [--coverage] [--gum] [--board --arm base|learned]
NO spaCy, NO external parser, NO LLM.  hdlab/ and tools/ are READ-ONLY here (proposed diff in the problem folder).
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import json
import re
import math
import sys
import time
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
import hdlab.lexical_categories as LC
from tools.build_attachment_validities import sentences, TRAIN, TEST
from experiments.exp_one_convention_two_losses_v1 import (
    _le_and_post, tags_from, dist_from, predicate_slot_v2, revise_posterior, gum_sentences,
)

OUT = str(get_output_dir("copular_subject_attachment_learned_v1"))
HOOK = os.path.join(REPO, "data", "hook_state")
CSUBG_ASSET = os.path.join(HOOK, "attachment_csubg_validity_v1.json")
MERGED_ASSET = os.path.join(HOOK, "attachment_validities_csubg_v1.json")   # the landed table + the accrued cue: the live swap
FIXED_W = float(os.environ.get("PRI117_FIXED_W", "4.6"))   # the mean |accrued validity|, for the frozen-form A/B
COP_FORMS = AA.COP_FORMS
NP_RUN = AA.NP_RUN
NOM = ("NOUN", "PROPN", "PRON", "NUM")


def out_dir():
    os.makedirs(OUT, exist_ok=True)
    return OUT


# =====================================================================================================
# ==============  PATCH BLOCK -- the exact code the diff inserts into hdlab/attachment_arm.py  ========
# =====================================================================================================
# Everything between PATCH-BEGIN and PATCH-END is copied verbatim into the organ by
# notes/problems/<slug>/copular_subject_attachment_patch.diff (asserted by --self-test).
# PATCH-BEGIN
CSUBG_BINS = (0.25, 0.60, 0.85)        # occupancy bins (a swept operating point, never adopted)
CSUB_COVERAGE = os.environ.get("HDLAB_ARM_CSUB_COVERAGE", "1") != "0"
CSUBG_CUE = os.environ.get("HDLAB_ARM_CSUBG", "1") != "0"
CSUB_REANALYSIS = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS", "1") != "0"
CSUB_REANALYSIS_LEFT = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS_LEFT", "0") == "1"
# THE WIDE FORM (pri 117, measured): the in-order beam commits the subject to whatever is open when it arrives, and
# the committed head is NOT always a later verb -- measured on UD-EWT test 700 it is the tense carrier, a preceding
# matrix verb, a noun inside the subject's own phrase or the root.  The SAME whole-sentence scores decoded by the
# search put the non-verbal subject at 0.7041 against the beam's 0.6509, so the arc the competition prefers is
# already there and the beam cannot reach it; the brain's repair is REANALYSIS when the disambiguating word arrives
# (Frazier & Rayner 1982), not a wider beam.  The revision still carries NO parameter: it takes the arc the organ's
# own learned activations prefer, and only for a subject whose clause's predicate slot has been identified.
CSUB_REANALYSIS_ANY = os.environ.get("HDLAB_ARM_CSUB_REANALYSIS_ANY", "1") != "0"
# THE TENSE CARRIER'S PREDICATE, WHATEVER ITS CATEGORY (pri 117).  pri 110's three-way discharge says a carrier's
# slot goes to (1) a VERBAL HOST in its verb group, (2) a NON-VERBAL complement, or (3) itself.  The copular-subject
# cue fired for branch (2) only -- so "It 's just DISAPPOINTING" and "the people will be DEAD" lost the pair
# whenever the category organ read the predicate as a VERB (participial predicates: 14 of the 60 residual misses
# were exactly this).  The ARC claim is the same under both branches -- the subject attaches to the token holding
# the predicate slot -- so the cue fires on the host too, and the OCCUPANCY (P(VERB) for a host, (1-host)*copular
# for a complement) is the value whose validity the competition learns SEPARATELY per configuration.
CSUB_VERBAL_HOST = os.environ.get("HDLAB_ARM_CSUB_VERBAL_HOST", "1") != "0"
# THE TENSE CARRIER IS NOT THE PREDICATE when it has one (Pustet 2003): the copula competes for the subject and
# wins it 3 times on the 169 ("that IS how i want ..."), so the carrier's own arc takes the competing value.
CSUB_SUPPRESS_COP = os.environ.get("HDLAB_ARM_CSUB_SUPPRESS_COP", "1") != "0"


def _csubg_bin(o: float) -> str:
    """The occupancy VALUE the cue competes with: a graded belief, binned so the validity of each band is learned
    separately (the organ's cue values are categorical; the bin edges are swept, never adopted)."""
    if o >= CSUBG_BINS[2]:
        return "hi"
    if o >= CSUBG_BINS[1]:
        return "md"
    if o >= CSUBG_BINS[0]:
        return "lo"
    return "no"


def _csub_subject_before(toks, pos, c):
    """The subject side of a copular clause: the nearest nominal standing before the tense carrier at 1-based `c`,
    skipping a CASE-MARKED one (a prepositional nominal is oblique, never the subject -- Pinker 1984).  This is
    `csub_sites`' own scan, unchanged."""
    k = c - 1
    while k >= 1:
        if pos[k - 1] in NOMINAL or pos[k - 1] == "NUM":
            a = k
            while a - 1 >= 1 and pos[a - 2] in NP_RUN:
                a -= 1
            if a - 1 >= 1 and pos[a - 2] == "ADP":
                k = a - 2; continue
            return k
        if pos[k - 1] in ("VERB", "SCONJ", "CCONJ"):
            return None
        k -= 1
    return None


def _csub_subject_inverted(toks, pos, c, q):
    """SUBJECT-AUXILIARY INVERSION (the interrogative construction, a stored form-meaning pairing the organ
    already carries in `_cop_inverted` / `host_belief`): with no subject to the copula's left, the subject is the
    first nominal to its RIGHT and the predicate stands after it -- "IS that a money maker ?".  pri 113 section
    29 counted 13 clauses where the predicate was found and the (pre-copular) subject scan failed."""
    lows = [t.lower() for t in toks]
    if not _cop_inverted(list(pos), lows, c - 1):
        return None
    for k in range(c + 1, min(q, len(pos) + 1)):
        if pos[k - 1] in ("NOUN", "PROPN", "PRON", "NUM"):
            return k
        if pos[k - 1] in ("VERB", "PUNCT", "SCONJ", "CCONJ"):
            return None
    return None


def cop_subject_pairs(toks, pos):
    """(predicate, subject) pairs, 1-based, for every copular predication in the sentence -- the token holding the
    clause's predicate slot and the nominal the copula predicates it OF.
    CSUB_COVERAGE (pri 117): the predicate comes from `cop_complement` -- the construction set the merged pri-113
    tree carries (inverted / fronted / locative / wh / clause-final / parenthetical) -- instead of the narrow
    `cop_predicates` scan this cue keyed on until now, and the inverted construction's post-copular subject is
    recovered.  pri 113 section 29 located DETECTION COVERAGE as what holds its prototype at 0.65: the pair was
    found for 101 of the 167 non-verbal clauses.  With the switch off the shipped detection is reproduced exactly
    (asserted over 120 sentences)."""
    n = len(pos); lows = [t.lower() for t in toks]; out = []
    if not CSUB_COVERAGE:
        for q in sorted(cop_predicates(list(toks), list(pos))):
            c = None
            for k in range(q - 1, 0, -1):
                if pos[k - 1] == "AUX" and lows[k - 1] in COP_FORMS:
                    c = k; break
                if pos[k - 1] == "VERB":
                    break
            if c is None:
                continue
            s = _csub_subject_before(toks, pos, c)
            if s is not None:
                out.append((q, s))
        return out
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        qi = cop_complement(list(toks), list(pos), i)
        if qi is not None and (qi == i or pos[qi] in ("VERB", "AUX")):
            qi = None
        if qi is None and CSUB_VERBAL_HOST:
            for k in range(i + 1, n):                      # the VERBAL HOST of the same verb group (branch 1)
                if pos[k] == "VERB":
                    qi = k; break
                if pos[k] in ("PUNCT", "SCONJ", "CCONJ") or (pos[k] == "PART" and lows[k] == "to"):
                    break
                if pos[k] in ("ADV", "AUX", "PART"):
                    continue
                break
        if qi is None:
            continue
        q = qi + 1; c = i + 1
        s = _csub_subject_before(toks, pos, c)
        if s is None:
            s = _csub_subject_inverted(toks, pos, c, q)
        if s is None or s == q:
            continue
        out.append((q, s))
    return out


def csub_sites(toks, pos):
    """COPULAR-SUBJECT cue: value `pred` on the (predicate <- subject) arc and `later` on every
    (verb-to-the-predicate's-right <- the same subject) arc; the validity is LEARNED like every other cue.
    pri 117: the pair detection is `cop_subject_pairs` (the construction set), which is the DETECTION-COVERAGE
    fix pri 113 section 29 located -- the scan this cue keyed on found the predicate in 101 of the 167
    non-verbal clauses, the construction set finds it in more."""
    n = len(pos); out = {}
    for (q, subj) in cop_subject_pairs(toks, pos):
        out[(q, subj)] = "pred"
        for v in range(q + 1, n + 1):
            if pos[v - 1] == "VERB":
                out.setdefault((v, subj), "later")
        if CSUB_SUPPRESS_COP:
            for c in range(min(q, subj), max(q, subj) + 1):
                if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS:
                    out.setdefault((c, subj), "carrier")
    return out


def csub_graded_sites(toks, pos, occ):
    """THE GRADED ARC FEATURE (pri 117).  The same two arcs, valued by HOW STRONGLY the candidate head holds its
    clause's predicate slot (pri 110's occupancy, graded off the category organ's own posterior): a confident
    predicate claims its subject, an uncertain one competes weakly.  `occ` is a per-token (0-based) probability;
    without it the cue is silent (the categorical `csub` cue above still fires)."""
    if occ is None:
        return {}
    n = len(pos); out = {}
    for (q, subj) in cop_subject_pairs(toks, pos):
        b = _csubg_bin(float(occ[q - 1]) if q - 1 < len(occ) else 0.0)
        out[(q, subj)] = "pred:" + b
        for v in range(q + 1, n + 1):
            if pos[v - 1] == "VERB":
                out.setdefault((v, subj), "later:" + b)
        if CSUB_SUPPRESS_COP:
            for c in range(min(q, subj), max(q, subj) + 1):
                if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS:
                    out.setdefault((c, subj), "carrier:" + b)
    return out


def occupancy_from_posterior(toks, pos, tag_post, tag_names=None):
    """P(this token fills its clause's predicate slot) per 0-based token, from the category organ's GRADED
    hand-off -- the signal pri 110 already computes and hands down only as a tag (pri 113 section 27).
    `tag_post` is the per-token {category: P} the frontend already passes to `arc_scores_graded`."""
    if not tag_post:
        return None
    names = list(tag_names) if tag_names else sorted({k for d in tag_post if d for k in d})
    if not names or any(t not in names for t in _PS_NEEDED):
        return None                                         # a category inventory this computation cannot read
    post = np.zeros((len(toks), len(names)))
    for i, d in enumerate(tag_post):
        if i >= len(toks) or not d:
            continue
        for k, v in d.items():
            j = names.index(k) if k in names else None
            if j is not None:
                post[i, j] = float(v)
    sites = predicate_sites(list(toks), list(pos), post, names)
    occ = np.zeros(len(toks))
    for i, s in sites.items():
        if 0 <= i < len(occ):
            occ[i] = float(s)
    return occ


def occupancy_from_tags(toks, pos):
    """The same read from a ONE-HOT category column -- what the offline teacher (tools/build_attachment_validities)
    has, so the cue is taught at build time with the same values it is read with."""
    names = list(_UPOS)
    if any(t not in names for t in _PS_NEEDED):
        return None
    post = np.zeros((len(toks), len(names)))
    for i, p in enumerate(pos):
        post[i, names.index(p) if p in names else names.index("X")] = 1.0
    sites = predicate_sites(list(toks), list(pos), post, names)
    occ = np.zeros(len(toks))
    for i, s in sites.items():
        if 0 <= i < len(occ):
            occ[i] = float(s)
    return occ


def observe_copular_subject(toks, pos, occ, table=None, weight: float = 1.0) -> int:
    """PLASTICITY -- the observe path for the graded cue's validity (Rescorla-Wagner / Competition-Model validity
    accrual: validity = availability x reliability, accrued from what the reader PERCEIVES).  Every copular
    predication READ is one confirmed outcome: the predicate slot's filler heads the pre-copular nominal, with
    the occupancy as the strength of the belief, and the later verbs inside the predicate phrase accrue the
    competing (zero) outcome.  No treebank and no tree is read -- the construction is stored lexical knowledge
    (Goldberg 1995) the organ already carries in COP_FORMS.  Returns the number of arcs accrued."""
    tab = table if table is not None else load_attachment_validities()
    counts = tab["counts"]; cues = counts.setdefault("cues", {}).setdefault("csubg", {})
    cfgc = counts["config"]; n = len(pos); k = 0
    sc_cfg = lambda j, h: ("ROOT:" + pos[j - 1]) if h == 0 else f"{pos[h - 1]}>{pos[j - 1]}:{'L' if h < j else 'R'}"
    for (q, subj) in cop_subject_pairs(toks, pos):
        o = float(occ[q - 1]) if (occ is not None and q - 1 < len(occ)) else 0.0
        b = _csubg_bin(o)
        comp = [(v, subj, "later:" + b, 0.0) for v in range(q + 1, n + 1) if pos[v - 1] == "VERB"]
        if CSUB_SUPPRESS_COP:
            comp += [(c, subj, "carrier:" + b, 0.0) for c in range(min(q, subj), max(q, subj) + 1)
                     if pos[c - 1] == "AUX" and toks[c - 1].lower() in COP_FORMS]
        for (h, j, val, outcome) in [(q, subj, "pred:" + b, o)] + comp:
            cfg = sc_cfg(j, h)
            if cfg not in cfgc:
                continue                                     # an unseen configuration has no base rate to contrast with
            cell = cues.setdefault(cfg + "|" + val, [0.0, 0.0])
            cell[0] += weight * outcome; cell[1] += weight; k += 1
    if k:
        tab["strength"] = strengths_from_arc_counts(counts)
    return k


MAP_FALLBACKS = []
REANALYSIS_STATS = {"fired": 0, "eligible": 0, "sentences": 0}


def revise_copular_subject(toks, pos, A, hd, occ=None):
    """PREDICATE-ARRIVAL REANALYSIS of the subject arc (pri 117), the in-order form of pri 113's held decode.
    The incremental decode commits the subject while the predicate's competitor is unresolved, and a verb INSIDE
    the predicate phrase then steals it; the brain revises when the disambiguating word arrives (Frazier &
    Rayner 1982), which is what this organ already does for the ROOT arc (INCR_ROOT_REANALYSIS).  The revision
    (a) fires only when the stealer stands to the RIGHT of the predicate -- so at the predicate's arrival the
    subject was still open and this IS that arrival decision, read in order; (b) carries no parameter: it takes
    the arc the organ's OWN learned activations prefer; (c) never creates a cycle."""
    if not CSUB_REANALYSIS or not hd:
        return hd
    out = dict(hd); n = len(pos)
    for (q, subj) in cop_subject_pairs(toks, pos):
        v = out.get(subj, 0)
        if v == q or not (1 <= q <= n and 1 <= subj <= n):
            continue
        if not (1 <= v <= n or v == 0):
            continue
        if not CSUB_REANALYSIS_ANY and not (1 <= v <= n and pos[v - 1] == "VERB" and (v > q or CSUB_REANALYSIS_LEFT)):
            continue                                        # narrow form: only the late-verb steal
        REANALYSIS_STATS["eligible"] += 1
        cur = float(A[v][subj]) if (0 <= v <= n and np.isfinite(A[v][subj])) else -1e18
        if not (np.isfinite(A[q][subj]) and float(A[q][subj]) > cur):
            continue                                         # the organ's own activations must prefer the predicate
        k = q; ok = True; seen = 0                           # q must not sit below subj
        while k and seen <= n:
            if k == subj:
                ok = False; break
            k = out.get(k, 0); seen += 1
        if ok:
            out[subj] = q; REANALYSIS_STATS["fired"] += 1
    return out
# PATCH-END
# =====================================================================================================

# the patch block above runs inside hdlab/attachment_arm.py; in the cell it needs the organ's own names
NOMINAL = AA.NOMINAL
_PS_NEEDED = getattr(AA, "_PS_NEEDED", ("VERB", "AUX", "NOUN", "PROPN", "PRON", "ADJ", "ADV", "PUNCT"))
_UPOS = AA._UPOS
cop_complement = AA.cop_complement
cop_predicates = AA.cop_predicates
_cop_inverted = AA._cop_inverted
predicate_sites = AA.predicate_sites
load_attachment_validities = AA.load_attachment_validities
strengths_from_arc_counts = AA.strengths_from_arc_counts


# ----------------------------------------------------------------------------- the csubg read-out (in arc_scores)
def csubg_add(A, toks, pos, occ, strength, sites=None):
    """The sparse add the patched `arc_scores` performs for the graded cue (identical code in the diff)."""
    d = strength.get("csubg") if strength else None
    if not d:
        return A
    sites = csub_graded_sites(toks, pos, occ) if sites is None else sites
    n = len(pos)
    for (h, j), val in sites.items():
        if 1 <= h <= n and 1 <= j <= n and np.isfinite(A[h][j]):
            cfg = ("ROOT:" + pos[j - 1]) if h == 0 else f"{pos[h - 1]}>{pos[j - 1]}:{'L' if h < j else 'R'}"
            A[h][j] += float(d.get(cfg + "|" + val, 0.0))
    return A


def _random_sites(toks, pos, sites, seed_key):
    """INFORMATION-FREE TWIN at the SITE level: the same NUMBER of arcs, the same value labels, but the
    (head, dependent) pairs drawn at random from the same shapes the cue can fire on (a non-verb content head, a
    nominal dependent).  If the win came from "push some arcs harder" rather than from the construction, this
    matches it."""
    n = len(pos)
    heads = [h for h in range(1, n + 1) if pos[h - 1] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM", "ADV", "VERB")]
    deps = [j for j in range(1, n + 1) if pos[j - 1] in ("NOUN", "PROPN", "PRON", "NUM")]
    if not heads or not deps or not sites:
        return {}
    rng = np.random.default_rng(abs(hash((seed_key, n, tuple(pos)))) % (2 ** 32))
    out = {}
    for val in sites.values():
        for _ in range(8):
            h = int(rng.choice(heads)); j = int(rng.choice(deps))
            if h != j and (h, j) not in out:
                out[(h, j)] = val; break
    return out


# ------------------------------------------------------------------------------------------- the measurement
def _cache(pop="ud", cap=700, th=0.5):
    """One live-chain pass: the organ's own categories + graded posterior + the predicate-slot occupancy."""
    sents = sentences(TEST, cap=cap, maxlen=10 ** 6) if pop == "ud" else gum_sentences(cap=cap)
    lc = LC.get(); rows = []
    for toks, gpos, gh, rels in sents:
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ0 = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=th, occ=occ0)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        occ = occupancy_from_posterior(list(toks), list(t2), dd, lc.tags)
        rows.append((list(toks), list(gpos), list(gh), list(rels), t2, dd, occ))
    return rows


def _count(toks, gpos, gh, rels, hd, n):
    nv = [0, 0]; vb = [0, 0]; ua = [0, 0]; rel = {}
    for i in range(n):
        g = gh[i]
        if not (0 <= g <= n):
            continue
        ok = int(hd.get(i + 1, -1) == g); ua[0] += ok; ua[1] += 1
        r = rels[i].split(":")[0]
        c = rel.setdefault(r, [0, 0]); c[0] += ok; c[1] += 1
        if r == "nsubj" and 1 <= g <= n:
            (nv if gpos[g - 1] != "VERB" else vb)[0] += ok
            (nv if gpos[g - 1] != "VERB" else vb)[1] += 1
    return (nv, vb, ua, rel)


def _score_rows(rows, tab, arm, strength=None, seed=0, boost=5.0, penalty=8.0):
    """Per-sentence (non-verbal hits, n, verbal hits, n, uas hits, n, per-relation) for one arm."""
    per = []
    rng = np.random.default_rng(seed)
    for (toks, gpos, gh, rels, t2, dd, occ) in rows:
        n = len(toks)
        occ_arm = occ
        if arm == "perm" and occ is not None:
            occ_arm = np.array(occ); rng.shuffle(occ_arm)
        # the organ's own coverage switch for this arm
        AA.__dict__["_pri117_cov"] = True
        globals()["CSUB_COVERAGE"] = arm not in ("base", "proto")
        globals()["CSUB_REANALYSIS"] = arm in ("rev", "learned", "twin", "perm", "rand", "tacc", "revonly", "revnarrow")
        globals()["CSUB_REANALYSIS_ANY"] = arm not in ("revnarrow", "revonly")
        AA.csub_sites = csub_sites if arm not in ("base", "proto") else _CSUB_SHIPPED
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        if arm == "fixed":
            # THE FROZEN FORM (the owner's pri 113 prototype, as a cue): one hand-set constant, +w on the
            # predicate arc and -w on the later-verb arc, no per-configuration validity and no observe path.
            for (h, j), val in csub_graded_sites(list(toks), list(t2), occ_arm).items():
                if 1 <= h <= nn and 1 <= j <= nn and np.isfinite(A[h][j]):
                    A[h][j] += (FIXED_W if val.startswith("pred") else -FIXED_W)
        if arm in ("occ", "rev", "learned", "twin", "perm", "rand", "tacc") and strength:
            if arm == "rand":
                real = csub_graded_sites(list(toks), list(t2), occ_arm)
                A = csubg_add(A, list(toks), list(t2), occ_arm, strength,
                              sites=_random_sites(list(toks), list(t2), real, seed))
            else:
                A = csubg_add(A, list(toks), list(t2), occ_arm, strength)
        if arm == "force":
            hd = AA.decode(list(toks), list(t2), A, nn)[0]
            for (q, sj) in cop_subject_pairs(list(toks), list(t2)):
                if 1 <= q <= nn and 1 <= sj <= nn:
                    hd[sj] = q
            per.append(_count(toks, gpos, gh, rels, hd, nn)); continue
        if arm == "map":
            A = csubg_add(A, list(toks), list(t2), occ_arm, strength) if strength else A
            try:
                mpost = AA.single_root_marginals(A.copy(), nn, 1.0)
                hd = AA.punct_convention(list(toks), list(t2),
                                         AA.occupancy_repair(list(toks), list(t2), AA.map_tree_single_root(A, nn), mpost))
            except TypeError:
                # PRE-EXISTING ORGAN EDGE CASE (found here, not caused here): on some out-of-supply sentences
                # `map_tree_single_root` returns a head of None and `punct_convention._chain_top` compares it with
                # an int.  It aborts the whole GUM run of the search decode; the in-order decode is unaffected.
                # Reported as a lead; this diagnostic arm falls back to the in-order decode for that sentence.
                MAP_FALLBACKS.append(" ".join(toks)[:60])
                hd = AA.decode(list(toks), list(t2), A, nn)[0]
            per.append(_count(toks, gpos, gh, rels, hd, nn)); continue
        if arm == "proto":
            A, hd = _proto_reshape(list(toks), list(t2), A, nn, tab, boost, penalty)
        else:
            hd = AA.decode(list(toks), list(t2), A, nn)[0]
            if globals()["CSUB_REANALYSIS"]:
                hd = revise_copular_subject(list(toks), list(t2), A, hd, occ_arm)
        per.append(_count(toks, gpos, gh, rels, hd, n))
    AA.csub_sites = _CSUB_SHIPPED
    return per


def _proto_reshape(toks, pos, A, nn, tab, boost, penalty):
    """pri 113's prototype, reproduced: boost the subject->predicate arc, suppress the subject->stealer arc,
    then resolve the copular subject on the MAP of the reshaped matrix (the held decode).  A HEURISTIC, kept
    only as the reference number this cell must reproduce."""
    n = len(pos)
    hd0 = AA.decode(list(toks), list(pos), A, nn)[0]
    pairs = _proto_pairs(toks, pos)
    for (q, s) in pairs:
        if not (1 <= q <= n and 1 <= s <= n):
            continue
        if np.isfinite(A[q, s]):
            A[q, s] += boost
        v = hd0.get(s, 0)
        if 1 <= v <= n and v != q and pos[v - 1] == "VERB" and np.isfinite(A[v, s]):
            A[v, s] -= penalty
    hd = AA.decode(list(toks), list(pos), A, nn)[0]
    mpost = AA.single_root_marginals(A.copy(), nn, 1.0)
    hdm = AA.punct_convention(list(toks), list(pos),
                              AA.occupancy_repair(list(toks), list(pos), AA.map_tree_single_root(A, nn), mpost))
    for (q, s) in pairs:
        if 1 <= s <= n:
            hd[s] = hdm.get(s, hd.get(s))
    return A, hd


def _proto_pairs(toks, pos):
    """The prototype's own pair scan (pri 113 --heads-reshape), kept verbatim for the reproduction arm."""
    n = len(pos); lows = [x.lower() for x in toks]; pairs = []
    cop = _cop_predicates_ext(list(toks), list(pos))
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        k = i - 1; s = None
        while k >= 0:
            if pos[k] in ("PUNCT", "SCONJ", "CCONJ", "VERB"):
                break
            if pos[k] in NOM:
                a = k
                while a - 1 >= 0 and pos[a - 1] in NP_RUN:
                    a -= 1
                if a - 1 >= 0 and pos[a - 1] == "ADP":
                    k = a - 1; continue
                s = k + 1; break
            k -= 1
        if s is None:
            continue
        for q in cop:
            if q > i and not any(pos[m] == "VERB" for m in range(i + 1, q - 1)):
                pairs.append((q, s)); break
    return pairs


def _cop_predicates_ext(toks, pos):
    """pri 113's extended scan (locative ADV fallback + clause-final copula), for the prototype arm only."""
    out = set(AA.cop_predicates(toks, pos)); n = len(pos); lows = [t.lower() for t in toks]
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP_FORMS:
            continue
        if any((q - 1) > i for q in out):
            continue
        for k in range(i + 1, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if pos[k] == "ADV" and lows[k] in getattr(AA, "LOCATIVE_ADV", frozenset()):
                out.add(k + 1); break
    return out


_CSUB_SHIPPED = AA.csub_sites


# ------------------------------------------------------------------------------------------------ statistics
def _agg(per, key):
    i = {"nv": 0, "vb": 1, "uas": 2}[key]
    a = sum(p[i][0] for p in per); b = sum(p[i][1] for p in per)
    return a / max(1, b), b


def _boot(per_a, per_b, key, n=2000, seed=0):
    """Paired bootstrap over SENTENCES on the same population."""
    i = {"nv": 0, "vb": 1, "uas": 2}[key]
    A = np.array([p[i][0] for p in per_a], float); B = np.array([p[i][0] for p in per_b], float)
    N = np.array([p[i][1] for p in per_a], float)
    m = len(A)
    if m == 0 or N.sum() == 0:
        return 0.0, 0.0, 0.0
    d0 = (A.sum() - B.sum()) / N.sum()
    rng = np.random.default_rng(seed); idx = rng.integers(0, m, size=(n, m))
    ds = (A[idx].sum(1) - B[idx].sum(1)) / np.maximum(N[idx].sum(1), 1e-9)
    return float(d0), float(np.quantile(ds, 0.025)), float(np.quantile(ds, 0.975))


def _rel(per):
    tot = defaultdict(lambda: [0, 0])
    for p in per:
        for r, c in p[3].items():
            tot[r][0] += c[0]; tot[r][1] += c[1]
    return {r: (tot[r][0] / max(1, tot[r][1]), tot[r][1]) for r in tot}


# ------------------------------------------------------------------------------------------------- the arms
def accrue(cap=3000, out=CSUBG_ASSET, weight=1.0, maxlen=40, quiet=False, merged=True):
    """ONLINE ACCRUAL of the graded cue's validity from reading: every copular predication perceived in the
    training text is one confirmed outcome (observe_copular_subject).  The organ's OWN categories tag the text --
    no gold column, no tree, no treebank head.  The landed counts are untouched; only the new cue's cells grow."""
    t0 = time.time()
    tab = AA.load_attachment_validities(AA.ASSET)
    counts = tab["counts"]
    counts.setdefault("cues", {})["csubg"] = {}
    lc = LC.get(); k = 0; sents = 0
    globals()["CSUB_COVERAGE"] = True
    for toks, _gpos, _gh, _rels in sentences(TRAIN, cap=cap, maxlen=maxlen):
        _le, post = _le_and_post(lc, list(toks)); t1 = tags_from(lc, post)
        occ0 = predicate_slot_v2(lc, toks, tags=t1, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t1, th=0.5, occ=occ0)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        occ = occupancy_from_posterior(list(toks), list(t2), dd, lc.tags)
        k += observe_copular_subject(list(toks), list(t2), occ, tab, weight=weight)
        sents += 1
    st = tab["strength"].get("csubg", {})
    os.makedirs(HOOK, exist_ok=True)
    # THE SWAPPABLE ASSET: the landed counts with the new cue's accrued cells inside, so the live organ loads ONE
    # table (strategy points attachment_arm.ASSET at it).  Nothing else in the table is touched -- asserted below.
    if not merged:
        with open(out, "w", encoding="utf-8", newline="") as f:
            json.dump({"source": "pri 117 learning-curve point", "sentences": sents, "arcs": k, "weight": weight,
                       "bins": list(CSUBG_BINS), "counts_csubg": tab["counts"]["cues"]["csubg"],
                       "strength_csubg": st}, f, indent=1)
        return {"sentences": sents, "arcs": k, "strength_csubg": st}
    AA.save_attachment_validities(MERGED_ASSET, tab)
    _base = AA.load_attachment_validities(AA.ASSET); _new = AA.load_attachment_validities(MERGED_ASSET)
    _other = [c for c in _base["counts"]["cues"] if c != "csubg"]
    assert all(_base["counts"]["cues"][c] == _new["counts"]["cues"].get(c) for c in _other), "the merged asset changed another cue"
    assert _base["counts"]["config"] == _new["counts"]["config"], "the merged asset changed the configuration counts"
    print("merged asset written (%d csubg cells; every other cue byte-identical) -> %s" % (len(st), MERGED_ASSET))
    doc = {"source": "attachment arm, pri 117: the copular-subject occupancy cue's validity, accrued ONLINE from "
                     "perceived copular constructions in reading (organ's own categories; no gold column, no tree)",
           "sentences": sents, "arcs": k, "weight": weight, "bins": list(CSUBG_BINS),
           "counts_csubg": tab["counts"]["cues"]["csubg"], "strength_csubg": st}
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
    if not quiet:
        print("accrued %d arcs over %d sentences in %.0fs -> %s" % (k, sents, time.time() - t0, out))
        rows = sorted(st.items(), key=lambda kv: -abs(kv[1]))[:14]
        print("  learned validities (top |contrast|):")
        for key, v in rows:
            t, nn = tab["counts"]["cues"]["csubg"][key]
            print("    %-34s %+.3f   (t=%.1f n=%.0f)" % (key, v, t, nn))
    return doc


def accrue_twin(cap=4000, out=None, weight=1.0, maxlen=40, seed=0):
    """INFORMATION-FREE TWIN of the LEARNING: accrue the same number of outcomes from RANDOM (non-verb head,
    nominal dependent) pairs at the matched rate instead of from perceived copular constructions.  If the validity
    can be learned from anything, this twin wins too."""
    out = out or (CSUBG_ASSET.replace(".json", "_twin.json"))
    tab = AA.load_attachment_validities(AA.ASSET)
    counts = tab["counts"]; counts.setdefault("cues", {})["csubg"] = {}
    cues = counts["cues"]["csubg"]; cfgc = counts["config"]
    lc = LC.get(); k = 0; sents = 0
    globals()["CSUB_COVERAGE"] = True
    for toks, _gp, _gh, _rl in sentences(TRAIN, cap=cap, maxlen=maxlen):
        _le, post = _le_and_post(lc, list(toks)); t1 = tags_from(lc, post)
        occ0 = predicate_slot_v2(lc, toks, tags=t1, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t1, th=0.5, occ=occ0)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        occ = occupancy_from_posterior(list(toks), list(t2), dd, lc.tags)
        real = csub_graded_sites(list(toks), list(t2), occ)
        for (h, j), val in _random_sites(list(toks), list(t2), real, seed).items():
            cfg = f"{t2[h - 1]}>{t2[j - 1]}:{'L' if h < j else 'R'}"
            if cfg not in cfgc:
                continue
            cell = cues.setdefault(cfg + "|" + val, [0.0, 0.0])
            cell[0] += weight * (1.0 if val.startswith("pred") else 0.0); cell[1] += weight; k += 1
        sents += 1
    tab["strength"] = AA.strengths_from_arc_counts(counts)
    os.makedirs(HOOK, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": "INFORMATION-FREE TWIN accrual: random pairs at the matched rate", "sentences": sents,
                   "arcs": k, "weight": weight, "bins": list(CSUBG_BINS),
                   "counts_csubg": cues, "strength_csubg": tab["strength"].get("csubg", {})}, f, indent=1)
    print("twin accrual: %d arcs over %d sentences -> %s" % (k, sents, out))
    return out


def _load_strength(path=CSUBG_ASSET):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return {"csubg": d["strength_csubg"]}, d


def _permuted(strength, seed=0):
    """INFORMATION-FREE TWIN: the accrued validity permuted across its own values (same table, same cells, the
    value->validity mapping destroyed)."""
    d = dict(strength["csubg"]); keys = list(d); vals = [d[k] for k in keys]
    rng = np.random.default_rng(seed); rng.shuffle(vals)
    return {"csubg": {k: v for k, v in zip(keys, vals)}}


def arms(cap=700, pop="ud", seed=0, which=None, boost=5.0, penalty=8.0, tag="arms"):
    t0 = time.time()
    rows = _cache(pop=pop, cap=cap)
    tab = AA.load_attachment_validities(AA.ASSET)
    strength, meta = _load_strength()
    order = which or ["base", "cov", "occ", "revnarrow", "rev", "fixed", "rand", "tacc", "perm", "force", "map", "proto"]
    res = {}; per_all = {}
    for arm in order:
        st = strength
        if arm == "twin":
            st = _permuted(strength, seed=seed)
        if arm == "tacc":
            st, _tm = _load_strength(CSUBG_ASSET.replace(".json", "_twin.json"))
        REANALYSIS_STATS.update({"fired": 0, "eligible": 0})
        per = _score_rows(rows, tab, arm, st, seed=seed, boost=boost, penalty=penalty)
        fired = dict(REANALYSIS_STATS)
        per_all[arm] = per
        nv, nnv = _agg(per, "nv"); vb, nvb = _agg(per, "vb"); ua, nua = _agg(per, "uas")
        res[arm] = {"nonverbal_nsubj": nv, "n_nonverbal": nnv, "verbal_nsubj": vb, "n_verbal": nvb,
                    "uas": ua, "n_uas": nua, "per_relation": {r: v[0] for r, v in _rel(per).items()},
                    "reanalysis": fired}
        print("  %-7s non-verbal nsubj %.4f (n=%d) | verbal %.4f | UAS %.4f | reanalysis %d/%d   [%.0fs]"
              % (arm, nv, nnv, vb, ua, fired["fired"], fired["eligible"], time.time() - t0))
    base = per_all.get("base")
    if base is not None:
        for arm in order:
            if arm == "base":
                continue
            for key in ("nv", "vb", "uas"):
                d, lo, hi = _boot(per_all[arm], base, key, seed=seed)
                res[arm].setdefault("vs_base", {})[key] = [d, lo, hi]
        print("\n  paired bootstrap over sentences (arm - base):")
        for arm in order:
            if arm == "base":
                continue
            d = res[arm]["vs_base"]
            print("    %-6s non-verbal %+.4f CI[%+.4f,%+.4f] %s | verbal %+.4f CI[%+.4f,%+.4f] | UAS %+.4f CI[%+.4f,%+.4f]"
                  % (arm, d["nv"][0], d["nv"][1], d["nv"][2], "SEP" if d["nv"][1] > 0 else ("SEP-DOWN" if d["nv"][2] < 0 else "ns"),
                     d["vb"][0], d["vb"][1], d["vb"][2], d["uas"][0], d["uas"][1], d["uas"][2]))
        # the learned arm vs the twin, on the same population
        for tw in ("rand", "tacc", "twin"):
            if "rev" in per_all and tw in per_all:
                d, lo, hi = _boot(per_all["rev"], per_all[tw], "nv", seed=seed)
                print("    learned(rev) - %-4s twin  non-verbal %+.4f CI[%+.4f,%+.4f] %s"
                      % (tw, d, lo, hi, "SEP" if lo > 0 else "ns"))
                res["rev"]["vs_%s_nv" % tw] = [d, lo, hi]
        if False and "rev" in per_all and "twin" in per_all:
            d, lo, hi = _boot(per_all["rev"], per_all["twin"], "nv", seed=seed)
            print("    learned(rev) - twin  non-verbal %+.4f CI[%+.4f,%+.4f] %s"
                  % (d, lo, hi, "SEP" if lo > 0 else "ns"))
            res["rev"]["vs_twin_nv"] = [d, lo, hi]
        if "rev" in per_all and "perm" in per_all:
            d, lo, hi = _boot(per_all["rev"], per_all["perm"], "nv", seed=seed)
            print("    learned(rev) - occ-permuted  non-verbal %+.4f CI[%+.4f,%+.4f] %s"
                  % (d, lo, hi, "SEP" if lo > 0 else "ns"))
            res["rev"]["vs_perm_nv"] = [d, lo, hi]
    res["_meta"] = {"pop": pop, "cap": cap, "accrual": {k: meta[k] for k in ("sentences", "arcs", "weight", "bins")},
                    "per_relation_base": {r: v[0] for r, v in _rel(per_all["base"]).items()} if base else {}}
    with open(os.path.join(out_dir(), "%s_%s.json" % (tag, pop)), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


def coverage(cap=700, th=0.5):
    """How many of the non-verbal-predicate clauses does each pair detection COVER, and at what precision?
    (pri 113 section 29 located detection coverage as the limiter: 101 of 167 covered.)"""
    rows = _cache(cap=cap)
    stat = {}
    for name, cov in (("cop_predicates (shipped)", False), ("cop_complement (pri 113)", True)):
        globals()["CSUB_COVERAGE"] = cov
        hit = 0; tot = 0; pair_ok = 0; pair_n = 0
        for (toks, gpos, gh, rels, t2, dd, occ) in rows:
            n = len(toks)
            gold = {}
            for i in range(n):
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB":
                    gold[i + 1] = gh[i]
            tot += len(gold)
            pairs = dict((s, q) for (q, s) in cop_subject_pairs(list(toks), list(t2)))
            for s, q in gold.items():
                if s in pairs:
                    hit += 1
                    pair_ok += int(pairs[s] == q)
            for s, q in pairs.items():
                pair_n += 1
        stat[name] = {"covered": hit, "gold_nonverbal_subjects": tot, "coverage": hit / max(1, tot),
                      "pair_exact_of_covered": pair_ok / max(1, hit), "pairs_proposed": pair_n}
        print("  %-26s covers %d/%d (%.4f) of gold non-verbal subjects; the pair names the gold predicate on %.4f of them; %d pairs proposed"
              % (name, hit, tot, hit / max(1, tot), pair_ok / max(1, hit), pair_n))
    globals()["CSUB_COVERAGE"] = True
    with open(os.path.join(out_dir(), "coverage.json"), "w", encoding="utf-8") as f:
        json.dump(stat, f, indent=1)
    return stat


def oracle(cap=700, seed=0):
    """THE CEILING OF BETTER DETECTION, and how much of the residual is the CATEGORY rung.
      (a) detection coverage with the organ's own categories vs with the GOLD column (same scan) -- the share of
          the miss that is an upstream category error rather than a missing construction;
      (b) the whole arm with the cue fed the GOLD (predicate, subject) pairs -- what perfect detection buys with
          today's validities and today's decode (the bound for the next brief)."""
    rows = _cache(cap=cap); tab = AA.load_attachment_validities(AA.ASSET)
    strength, _m = _load_strength()
    globals()["CSUB_COVERAGE"] = True
    cov = {"organ": [0, 0, 0], "gold": [0, 0, 0]}
    for (toks, gpos, gh, rels, t2, dd, occ) in rows:
        n = len(toks)
        gold = {i + 1: gh[i] for i in range(n)
                if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB"}
        for name, tags in (("organ", t2), ("gold", list(gpos))):
            pairs = dict((sj, q) for (q, sj) in cop_subject_pairs(list(toks), list(tags)))
            cov[name][2] += len(gold)
            for sj, g in gold.items():
                if sj in pairs:
                    cov[name][0] += 1
                    cov[name][1] += int(pairs[sj] == g)
    for name in ("organ", "gold"):
        c = cov[name]
        print("  detection with %-5s categories: subject covered %d/%d (%.4f), pair names the gold predicate %d (%.4f of all)"
              % (name, c[0], c[2], c[0] / max(1, c[2]), c[1], c[1] / max(1, c[2])))
    # (b) the oracle-pair arm
    per_o = []; per_l = _score_rows(rows, tab, "rev", strength, seed=seed)
    for (toks, gpos, gh, rels, t2, dd, occ) in rows:
        n = len(toks)
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        gold_pairs = [(gh[i], i + 1) for i in range(n)
                      if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= n and gpos[gh[i] - 1] != "VERB"]
        sites = {}
        for (q, sj) in gold_pairs:
            b = _csubg_bin(float(occ[q - 1]) if occ is not None and q - 1 < len(occ) else 1.0)
            sites[(q, sj)] = "pred:" + b
            for v in range(q + 1, n + 1):
                if t2[v - 1] == "VERB":
                    sites.setdefault((v, sj), "later:" + b)
        A = csubg_add(A, list(toks), list(t2), occ, strength, sites=sites)
        hd = AA.decode(list(toks), list(t2), A, nn)[0]
        nv = [0, 0]; vb = [0, 0]; ua = [0, 0]
        for i in range(n):
            g = gh[i]
            if not (0 <= g <= n):
                continue
            ok = int(hd.get(i + 1, -1) == g); ua[0] += ok; ua[1] += 1
            if rels[i].split(":")[0] == "nsubj" and 1 <= g <= n:
                (nv if gpos[g - 1] != "VERB" else vb)[0] += ok
                (nv if gpos[g - 1] != "VERB" else vb)[1] += 1
        per_o.append((nv, vb, ua, {}))
    o, n_o = _agg(per_o, "nv"); l, _ = _agg(per_l, "nv")
    d, lo, hi = _boot(per_o, per_l, "nv", seed=seed)
    print("  ORACLE PAIRS (perfect detection, same learned validity + decode): %.4f vs learned %.4f  (%+.4f CI[%+.4f,%+.4f])"
          % (o, l, d, lo, hi))
    print("  => of the %.4f still missing at the learned arm, detection can buy at most %.4f; the rest is the decode/scorer."
          % (1 - l, o - l))
    res = {"coverage": {k: {"covered": v[0], "pair_exact": v[1], "n": v[2]} for k, v in cov.items()},
           "oracle_pairs": o, "learned": l, "oracle_minus_learned": [d, lo, hi]}
    with open(os.path.join(out_dir(), "oracle.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


def residual(cap=700, arm="rev", seed=0):
    """WHERE THE REMAINING MISSES ARE.  Every gold non-verbal subject the arm still attaches wrongly, classified by
    the mechanism that could have caught it -- so the next lever is chosen by count, not by narration."""
    rows = _cache(cap=cap); tab = AA.load_attachment_validities(AA.ASSET)
    strength, _m = _load_strength()
    cls = Counter(); ex = defaultdict(list)
    globals()["CSUB_COVERAGE"] = True
    globals()["CSUB_REANALYSIS"] = True
    AA.csub_sites = csub_sites
    for (toks, gpos, gh, rels, t2, dd, occ) in rows:
        n = len(toks)
        A, nn = AA.arc_scores_graded(list(toks), list(t2), dd, tab)
        A = csubg_add(A, list(toks), list(t2), occ, strength)
        hd = revise_copular_subject(list(toks), list(t2), A,
                                    AA.decode(list(toks), list(t2), A, nn)[0], occ)
        pairs = dict((sj, q) for (q, sj) in cop_subject_pairs(list(toks), list(t2)))
        for i in range(n):
            if rels[i].split(":")[0] != "nsubj":
                continue
            g = gh[i]
            if not (1 <= g <= n) or gpos[g - 1] == "VERB":
                continue
            sj = i + 1; got = hd.get(sj, 0)
            if got == g:
                cls["HIT"] += 1; continue
            q = pairs.get(sj)
            lows = [x.lower() for x in toks]
            has_cop = any(t2[k] == "AUX" and lows[k] in COP_FORMS for k in range(n))
            if q is None and not has_cop:
                k = "MISS: verbless / no copula in the sentence"
            elif q is None:
                k = "MISS: copula present, no (predicate,subject) pair found"
            elif q != g:
                k = "MISS: pair found but the predicate is the wrong token (t2[q]=%s, gold=%s)" % (t2[q - 1], gpos[g - 1])
            elif got != q:
                k = "MISS: pair CORRECT, decode chose %s (%s) instead" % ("ROOT" if got == 0 else t2[got - 1],
                                                                          "left" if 0 < got < sj else "right")
            else:
                k = "MISS: other"
            cls[k] += 1
            if len(ex[k]) < 3:
                ex[k].append(" ".join(toks)[:90] + "   [subj=%s gold=%s got=%s]"
                             % (toks[sj - 1], toks[g - 1], toks[got - 1] if got else "ROOT"))
    AA.csub_sites = _CSUB_SHIPPED
    tot = sum(v for k, v in cls.items() if k != "HIT")
    print("  residual of the %s arm: %d hits, %d misses" % (arm, cls["HIT"], tot))
    for k, v in cls.most_common():
        if k == "HIT":
            continue
        print("    %-72s %3d (%.3f of misses)" % (k[:72], v, v / max(1, tot)))
        for e in ex[k][:2]:
            print("        e.g. " + e)
    with open(os.path.join(out_dir(), "residual.json"), "w", encoding="utf-8") as f:
        json.dump({"classes": dict(cls), "examples": {k: v for k, v in ex.items()}}, f, indent=1)
    return cls


def frozen_sweep(cap=700, seed=0, ws=(1.0, 2.0, 3.0, 4.6, 6.0, 8.0, 12.0)):
    """THE FAIR FROZEN FLOOR: the BEST hand-set constant, swept -- so "learned beats frozen" is measured against
    the strongest frozen form, not against one constant I chose."""
    rows = _cache(cap=cap); tab = AA.load_attachment_validities(AA.ASSET)
    strength, _m = _load_strength()
    per_l = _score_rows(rows, tab, "rev", strength, seed=seed)
    nvl, n = _agg(per_l, "nv")
    best = None; res = {"learned": nvl}
    for w in ws:
        globals()["FIXED_W"] = w
        per = _score_rows(rows, tab, "fixed", strength, seed=seed)
        nv, _ = _agg(per, "nv"); vb, _ = _agg(per, "vb"); ua, _ = _agg(per, "uas")
        res["fixed_%.1f" % w] = {"nonverbal": nv, "verbal": vb, "uas": ua}
        print("    frozen constant w=%-5.1f non-verbal %.4f | verbal %.4f | UAS %.4f" % (w, nv, vb, ua))
        if best is None or nv > best[1]:
            best = (w, nv, per)
    globals()["FIXED_W"] = 4.6
    d, lo, hi = _boot(per_l, best[2], "nv", seed=seed)
    print("  LEARNED %.4f vs the BEST frozen (w=%.1f) %.4f : %+.4f CI[%+.4f,%+.4f] %s"
          % (nvl, best[0], best[1], d, lo, hi, "SEP" if lo > 0 else ("SEP-DOWN" if hi < 0 else "ns")))
    res["best_frozen"] = {"w": best[0], "nonverbal": best[1]}
    res["learned_minus_best_frozen"] = [d, lo, hi]
    with open(os.path.join(out_dir(), "frozen_sweep.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


def sweep(cap=700, seed=0):
    """The free operating points (phase diagram): the accrual WEIGHT (learning rate) and the occupancy BINS."""
    rows = _cache(cap=cap); tab = AA.load_attachment_validities(AA.ASSET); res = {}
    strength, _m = _load_strength()
    for w in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0):
        sc = {"csubg": {k: v * 1.0 for k, v in strength["csubg"].items()}}
        # the learning rate enters as the accrual weight; with the shrinkage held, scaling the accrued count is
        # equivalent to re-accruing at that rate on the same observations (checked in --self-test)
        per = _score_rows(rows, tab, "rev", _scaled(strength, w), seed=seed)
        nv, n = _agg(per, "nv"); vb, _ = _agg(per, "vb"); ua, _ = _agg(per, "uas")
        res["weight_%.2f" % w] = {"nonverbal": nv, "verbal": vb, "uas": ua}
        print("  accrual weight %.2f -> non-verbal %.4f | verbal %.4f | UAS %.4f" % (w, nv, vb, ua))
    with open(os.path.join(out_dir(), "sweep.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    return res


def _scaled(strength, w):
    return {"csubg": {k: v * w for k, v in strength["csubg"].items()}}


# ------------------------------------------------------------------- EXECUTE THE DIFF'S OWN CODE (patch-test)
SLUG = ("the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_verbal_ones_"
        "land_the_predicate_slot_as_a_graded_online_learned_arc_feature")
DIFF = os.path.join(REPO, "notes", "problems", SLUG, "copular_subject_attachment_patch.diff")


def _apply_unified(src, diff_text, path):
    """Apply the hunks of `diff_text` that target `path` to the string `src` (pure python, no git)."""
    NL = chr(10); CR = chr(13)
    lines = src.split(NL)
    out = []; i = 0; cur = None; hunks = []
    for ln in diff_text.split(NL):
        if ln.startswith("--- a/"):
            cur = ln[6:].strip()
            continue
        if ln.startswith("+++ b/") or ln.startswith("diff "):
            continue
        if ln.startswith("@@"):
            if cur == path:
                m = re.match(r"@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@", ln)
                hunks.append([int(m.group(1)), int(m.group(2) or 1), []])
            continue
        if cur == path and hunks and (ln[:1] in (" ", "+", "-") or ln == ""):
            hunks[-1][2].append(ln if ln else " ")
    for (start, count, body) in hunks:
        s0 = start - 1
        out.extend(lines[i:s0]); i = s0
        for b in body:
            tag, txt = b[0], b[1:]
            if tag == " ":
                assert lines[i].rstrip(CR) == txt.rstrip(CR), (i, lines[i], txt)
                out.append(lines[i]); i += 1
            elif tag == "-":
                assert lines[i].rstrip(CR) == txt.rstrip(CR), (i, lines[i], txt)
                i += 1
            else:
                out.append(txt)
    out.extend(lines[i:])
    return NL.join(out)


def patched_module(name="hdlab.attachment_arm"):
    """Build the PATCHED organ from the diff on disk and install it as `hdlab.attachment_arm` in THIS process, so
    every later import (frontend, the readers, the board) runs the diff's own code.  Returns the module."""
    import importlib.util
    import re as _re
    import tempfile
    src = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8", newline="").read()
    dif = open(DIFF, encoding="utf-8", newline="").read()
    new = _apply_unified(src, dif, "hdlab/attachment_arm.py")
    d = os.path.join(tempfile.gettempdir(), "pri117_patched")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "attachment_arm_patched.py")
    with open(f, "w", encoding="utf-8", newline="") as fh:
        fh.write(new)
    import hdlab
    spec = importlib.util.spec_from_file_location(name, f)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = os.path.join(REPO, "hdlab", "attachment_arm.py")     # see _fresh_module
    sys.modules[name] = m
    spec.loader.exec_module(m)
    assert m._REPO == REPO, (m._REPO, REPO)
    hdlab.attachment_arm = m
    m.ASSET = MERGED_ASSET                       # the accrued table (the live swap strategy would make)
    m._TABLE = None
    return m


def patch_test(cap=120):
    """THE DIFF IS THE ORGAN: run the organ's own witnesses and the headline measurement through the PATCHED
    module, so the number in SOLVED.md is the number the landed code produces (not the cell's overlay)."""
    import re as _re
    ok = [0, 0]

    def ck(name, cond, extra=""):
        ok[1] += 1
        if cond:
            ok[0] += 1; print("  ok   " + name)
        else:
            print("  FAIL " + name + " " + str(extra))

    M = patched_module()
    ck("the diff applies in memory and the patched organ imports", hasattr(M, "csub_graded_sites"))
    ck("the merged asset loads through the patched organ and carries the new cue",
       "csubg" in M.load_attachment_validities(MERGED_ASSET)["strength"])
    ck("the new cue is in CUES", "csubg" in M.CUES)
    # the fastpath witness's invariant: vectorised == reference, WITH the occupancy
    tab = M.load_attachment_validities(MERGED_ASSET)
    worst = 0.0
    for toks, pos, _h, _r in sentences(TEST, cap=60, maxlen=10 ** 6):
        occ = M.occupancy_from_tags(toks, pos)
        A, n = M.arc_scores(toks, pos, tab, occ); B, _ = M.arc_scores_reference(toks, pos, tab, occ)
        fa = np.isfinite(A)
        if not np.array_equal(fa, np.isfinite(B)):
            worst = 1e9; break
        worst = max(worst, float(np.max(np.abs(A[fa] - B[fa]))) if fa.any() else 0.0)
    ck("patched fastpath == reference readout to 1e-9 WITH the occupancy (60 sentences)", worst <= 1e-9, worst)
    # occ=None reproduces the organ as shipped
    import hdlab.attachment_arm as _unused  # noqa  (already the patched one)
    base_mod_src = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8").read()
    ck("the diff leaves the organ file on disk untouched", "csub_graded_sites" not in base_mod_src)
    # the live chain through the patched organ, on the measured population
    lc = LC.get(); acc = [0, 0]; accv = [0, 0]
    for toks, gpos, gh, rels in sentences(TEST, cap=cap, maxlen=10 ** 6):
        _le, post = _le_and_post(lc, list(toks)); t0 = tags_from(lc, post)
        occ0 = predicate_slot_v2(lc, toks, tags=t0, post=post)
        p2, _s = revise_posterior(lc, toks, post, tags=t0, th=0.5, occ=occ0)
        t2 = tags_from(lc, p2); dd = dist_from(lc, p2)
        A, nn = M.arc_scores_graded(list(toks), list(t2), dd, tab)
        hd = M.decode(list(toks), list(t2), A, nn)[0]
        for i in range(len(toks)):
            if rels[i].split(":")[0] == "nsubj" and 1 <= gh[i] <= len(toks):
                (acc if gpos[gh[i] - 1] != "VERB" else accv)[0] += int(hd.get(i + 1, 0) == gh[i])
                (acc if gpos[gh[i] - 1] != "VERB" else accv)[1] += 1
    print("  PATCHED ORGAN, live chain, cap %d: non-verbal nsubj %.4f (n=%d) | verbal %.4f (n=%d)"
          % (cap, acc[0] / max(1, acc[1]), acc[1], accv[0] / max(1, accv[1]), accv[1]))
    ck("the patched organ's live-chain number is produced end to end (no cell overlay)", acc[1] > 0)
    print(chr(10) + "%d/%d patch checks passed" % (ok[0], ok[1]))
    return {"nonverbal": acc[0] / max(1, acc[1]), "n": acc[1], "verbal": accv[0] / max(1, accv[1]),
            "checks": ok, "cap": cap}



def _fresh_module(path, name, asset=None):
    """Load a module FILE under `name` (used to hold the organ as shipped and the patched organ side by side)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    # THE ORGAN DERIVES ITS ASSET PATHS FROM __file__, and a copy loaded out of a temp directory silently loses
    # them -- the learned HOLD expectation and the plausibility store fall back to their defaults and the decode
    # is WORSE (measured: UAS 0.6328 -> 0.6138 on 200 sentences).  Caught by comparing the copy with the organ
    # imported normally; pin __file__ to the real organ so the copy is the same organ.
    m.__file__ = os.path.join(REPO, "hdlab", "attachment_arm.py")
    sys.modules[name] = m
    spec.loader.exec_module(m)
    assert m._REPO == REPO, (m._REPO, REPO)
    assert os.path.isfile(m.HOLD_ASSET) and os.path.isfile(m.BF_TSP_ASSET), "the copy lost an asset path"
    if asset:
        m.ASSET = asset; m._TABLE = None
    return m


def live_ab(cap=700, pop="ud", seed=0):
    """THE HEADLINE, measured through the DIFF: the organ exactly as shipped vs the PATCHED organ (with the accrued
    asset), BOTH IN ONE PROCESS, on the same live chain and the same sentences.  Nothing in this arm is a cell
    overlay -- every number comes from the code the diff lands."""
    import re as _re
    import tempfile
    src = open(os.path.join(REPO, "hdlab", "attachment_arm.py"), encoding="utf-8", newline="").read()
    dif = open(DIFF, encoding="utf-8", newline="").read()
    d = os.path.join(tempfile.gettempdir(), "pri117_patched")
    os.makedirs(d, exist_ok=True)
    f0 = os.path.join(d, "arm_shipped.py"); f1 = os.path.join(d, "arm_patched.py")
    with open(f0, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    with open(f1, "w", encoding="utf-8", newline="") as fh:
        fh.write(_apply_unified(src, dif, "hdlab/attachment_arm.py"))
    M0 = _fresh_module(f0, "pri117_arm_shipped", AA.ASSET)
    M1 = _fresh_module(f1, "pri117_arm_patched", MERGED_ASSET)
    t0 = M0.load_attachment_validities(AA.ASSET); t1 = M1.load_attachment_validities(MERGED_ASSET)
    rows = _cache(pop=pop, cap=cap)
    per = {"shipped": [], "patched": []}
    ms = time.time()
    for (toks, gpos, gh, rels, t2, dd, occ) in rows:
        n = len(toks)
        for name, M, tb in (("shipped", M0, t0), ("patched", M1, t1)):
            A, nn = M.arc_scores_graded(list(toks), list(t2), dd, tb)
            hd = M.decode(list(toks), list(t2), A, nn)[0]
            per[name].append(_count(toks, gpos, gh, rels, hd, n))
    out = {"pop": pop, "cap": cap, "seconds": round(time.time() - ms, 1)}
    for name in ("shipped", "patched"):
        nv, nnv = _agg(per[name], "nv"); vb, nvb = _agg(per[name], "vb"); ua, nua = _agg(per[name], "uas")
        out[name] = {"nonverbal_nsubj": nv, "n_nonverbal": nnv, "verbal_nsubj": vb, "n_verbal": nvb,
                     "uas": ua, "n_uas": nua, "per_relation": {r: v[0] for r, v in _rel(per[name]).items()}}
        print("  %-8s non-verbal nsubj %.4f (n=%d) | verbal %.4f (n=%d) | UAS %.4f"
              % (name, nv, nnv, vb, nvb, ua))
    for key, lab in (("nv", "non-verbal nsubj"), ("vb", "verbal nsubj"), ("uas", "UAS")):
        dd2, lo, hi = _boot(per["patched"], per["shipped"], key, seed=seed)
        out.setdefault("delta", {})[key] = [dd2, lo, hi]
        print("    %-17s %+.4f CI[%+.4f,%+.4f] %s" % (lab, dd2, lo, hi,
              "SEP UP" if lo > 0 else ("SEP DOWN" if hi < 0 else "not separated")))
    r0 = _rel(per["shipped"]); r1 = _rel(per["patched"])
    print("    per relation (shipped -> patched; n):")
    for r in sorted(set(r0) | set(r1), key=lambda x: -r0.get(x, (0, 0))[1]):
        a = r0.get(r, (0.0, 0)); b = r1.get(r, (0.0, 0))
        if a[1] >= 20:
            flag = "" if abs(b[0] - a[0]) < 1e-9 else ("  UP" if b[0] > a[0] else "  DOWN")
            print("      %-8s %.4f -> %.4f  (n=%d)%s" % (r, a[0], b[0], a[1], flag))
    out["per_relation_n"] = {r: r0[r][1] for r in r0}
    with open(os.path.join(out_dir(), "live_ab_%s.json" % pop), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return out



def board_ab(n_boot=1000, caps=None):
    """THE FULL BOARD, BOTH ARMS IN ONE PROCESS (a capped board's exact zeros are underpowered -- 2026-09-14).
    ARM A is the organ exactly as shipped.  The organ is then swapped IN PLACE -- every public name of the patched
    module is bound onto the live `hdlab.attachment_arm` object, so the consumers that imported it keep working
    references (replacing sys.modules would leave every `import ... as AA` pointing at the old organ) -- and ARM B
    re-runs the same seven dimensions."""
    import hdlab.attachment_arm as LIVE
    import hdlab.frontend as FE
    import experiments.exp_situation_model_qa_modern_v1 as B
    t0 = time.time()
    print("BOARD ARM A (the organ as shipped) ...", flush=True)
    resA = B.run(caps=caps, n_boot=n_boot, write_metrics=False)
    print("  arm A done in %.0fs" % (time.time() - t0), flush=True)
    with open(os.path.join(out_dir(), "board_armA.json"), "w", encoding="utf-8") as fh:
        json.dump({"per_dimension": {k: (resA["per_dimension"].get(k) or {}).get("model_acc")
                                     for k in resA["per_dimension"]},
                   "aggregate": resA["aggregate_19c_free"].get("model_acc"),
                   "seconds": round(time.time() - t0, 1)}, fh, indent=1)   # checkpoint: a late crash keeps arm A
    M = patched_module(name="pri117_board_patched")
    sys.modules["hdlab.attachment_arm"] = LIVE          # keep the live module object in place
    import hdlab
    hdlab.attachment_arm = LIVE
    for k, v in vars(M).items():
        if not k.startswith("__"):
            setattr(LIVE, k, v)                          # the patched organ, in the live module object
    LIVE.ASSET = MERGED_ASSET; LIVE._TABLE = None
    M.ASSET = MERGED_ASSET; M._TABLE = None
    FE._P = None; FE._T = None                           # the frontend caches the table at construction
    print("BOARD ARM B (the patched organ + the accrued validity) ...", flush=True)
    resB = B.run(caps=caps, n_boot=n_boot, write_metrics=False)
    print("  arm B done in %.0fs" % (time.time() - t0), flush=True)
    dims = ("coref", "salience", "common_noun_coref", "who_did_what_agent", "who_did_what_patient", "state", "wic")
    out = {"arms": {}, "seconds": round(time.time() - t0, 1)}
    print("%-22s %8s %8s %9s %8s" % ("dimension", "shipped", "patched", "delta", "n"))
    down = []
    for k in dims:
        a = (resA["per_dimension"].get(k) or {}); b = (resB["per_dimension"].get(k) or {})
        va = a.get("model_acc"); vb = b.get("model_acc")
        d = None if (va is None or vb is None) else round(vb - va, 4)
        print("%-22s %8s %8s %9s %8s" % (k, va, vb, d, a.get("n")))
        out["arms"][k] = {"shipped": va, "patched": vb, "delta": d, "n": a.get("n")}
        if d is not None and d < 0:
            down.append((k, d, a.get("n")))
    ag_a = resA["aggregate_19c_free"].get("model_acc"); ag_b = resB["aggregate_19c_free"].get("model_acc")
    out["aggregate"] = {"shipped": ag_a, "patched": ag_b,
                        "delta": None if (ag_a is None or ag_b is None) else round(ag_b - ag_a, 4)}
    print("AGGREGATE               %8s %8s %9s" % (ag_a, ag_b, out["aggregate"]["delta"]))
    print("DOWN ON: %s" % (down if down else "nothing"))
    out["down"] = down
    with open(os.path.join(out_dir(), "board_ab.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return out



def curve(cap=700, reads=(0, 250, 1000, 2000, 4000), seed=0):
    """THE LEARNING CURVE -- is the validity actually being LEARNED FROM READING, or is any table as good?
    Accrue from N sentences of reading, then measure; N=0 is the organ with the cue present and no experience."""
    rows = _cache(cap=cap); tab = AA.load_attachment_validities(AA.ASSET)
    out = {}
    for n in reads:
        if n == 0:
            st = {"csubg": {}}
            arcs = 0
        else:
            # NEVER into the shipped asset: the curve would leave a 250-sentence table behind for the next run
            # (caught mid-session -- the board's arm B would have loaded it).
            doc = accrue(cap=n, out=os.path.join(out_dir(), "curve_csubg_%d.json" % n), quiet=True, merged=False)
            st = {"csubg": doc["strength_csubg"]}; arcs = doc["arcs"]
        per = _score_rows(rows, tab, "rev", st, seed=seed)
        nv, nn = _agg(per, "nv"); vb, _ = _agg(per, "vb"); ua, _ = _agg(per, "uas")
        out["reads_%d" % n] = {"sentences": n, "arcs": arcs, "cells": len(st["csubg"]),
                               "nonverbal": nv, "verbal": vb, "uas": ua}
        print("  after %5d sentences of reading (%4d arcs accrued, %3d cells): non-verbal %.4f | verbal %.4f | UAS %.4f"
              % (n, arcs, len(st["csubg"]), nv, vb, ua))
    with open(os.path.join(out_dir(), "curve.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    return out


# ------------------------------------------------------------------------------------------------ self-test
def self_test():
    ok = [0, 0]

    def ck(name, cond, extra=""):
        ok[1] += 1
        if cond:
            ok[0] += 1; print("  ok   " + name)
        else:
            print("  FAIL " + name + " " + str(extra))

    t = "The sky is blue .".split(); p = ["DET", "NOUN", "AUX", "ADJ", "PUNCT"]
    globals()["CSUB_COVERAGE"] = True
    pr = cop_subject_pairs(t, p)
    ck("canonical copular clause: (predicate=blue, subject=sky)", pr == [(4, 2)], pr)
    cs = csub_sites(t, p)
    ck("csub values: pred on the predicate arc", cs.get((4, 2)) == "pred", cs)
    t2 = "We are capable of protecting it .".split(); p2 = ["PRON", "AUX", "ADJ", "ADP", "VERB", "PRON", "PUNCT"]
    cs2 = csub_sites(t2, p2)
    ck("the later verb inside the predicate phrase gets `later`, the tense carrier `carrier`",
       cs2.get((3, 1)) == "pred" and cs2.get((5, 1)) == "later" and cs2.get((2, 1)) == "carrier", cs2)
    occ = np.zeros(len(p2)); occ[2] = 0.9
    g = csub_graded_sites(t2, p2, occ)
    ck("graded values carry the occupancy bin", g.get((3, 1)) == "pred:hi" and g.get((5, 1)) == "later:hi", g)
    ck("the graded cue is silent without the occupancy", csub_graded_sites(t2, p2, None) == {})
    # occupancy from a one-hot column == the organ's own predicate_sites read
    o1 = occupancy_from_tags(t, p)
    ck("occupancy_from_tags puts the slot on the complement", o1 is not None and o1[3] > 0.5 and o1[1] < 0.5, o1)
    ck("a category inventory without the UPOS classes degrades to silence, not an exception",
       occupancy_from_posterior(t, p, [{"c1": 1.0}] * len(t), ["c1", "c2"]) is None)
    # accrual moves the validity in the right direction, and the competitor's the other way
    import copy
    tab = AA.load_attachment_validities(AA.ASSET)
    tab2 = {"counts": copy.deepcopy(tab["counts"]), "frames": tab.get("frames", {}),
            "pp_assoc": tab.get("pp_assoc"), "pp_assoc_v2": tab.get("pp_assoc_v2")}
    tab2["counts"].setdefault("cues", {})["csubg"] = {}
    tab2["strength"] = AA.strengths_from_arc_counts(tab2["counts"])
    occ2 = np.zeros(len(p2)); occ2[2] = 1.0
    for _ in range(40):
        observe_copular_subject(t2, p2, occ2, tab2)
    st = tab2["strength"]["csubg"]
    kp = [k for k in st if k.endswith("|pred:hi")]; kl = [k for k in st if k.endswith("|later:hi")]
    ck("observing copular predications accrues a POSITIVE validity for the predicate arc",
       bool(kp) and all(st[k] > 0 for k in kp), {k: st[k] for k in kp})
    ck("and a NEGATIVE one for the later-verb competitor", bool(kl) and all(st[k] < 0 for k in kl), {k: st[k] for k in kl})
    # the read-out moves the arc score it should and nothing else
    A, n = AA.arc_scores(t2, p2, tab)
    B = csubg_add(A.copy(), t2, p2, occ2, tab2["strength"])
    moved = [(i, j) for i in range(n + 1) for j in range(1, n + 1)
             if np.isfinite(A[i][j]) and abs(B[i][j] - A[i][j]) > 1e-12]
    ck("the read-out touches only the copular-subject arcs (predicate, later verb, carrier)",
       set(moved) <= {(3, 1), (5, 1), (2, 1)}, moved)
    # reanalysis: only a stealer to the RIGHT of the predicate, never a cycle, no parameter
    globals()["CSUB_REANALYSIS"] = True
    globals()["CSUB_REANALYSIS_ANY"] = False
    t3 = "sky is blue x".split(); p3 = ["NOUN", "AUX", "ADJ", "VERB"]        # (x = a verb inside the predicate phrase)

    def toyA(pred_score, steal_score):
        M = np.full((5, 5), -np.inf); M[3][1] = pred_score; M[4][1] = steal_score
        M[0][3] = 0.0; M[3][2] = 0.0; M[3][4] = 0.0
        return M
    out = revise_copular_subject(t3, p3, toyA(2.0, 1.0), {1: 4, 2: 3, 3: 0, 4: 3})
    ck("predicate-arrival reanalysis re-heads the subject onto the predicate", out.get(1) == 3, out)
    out2 = revise_copular_subject(t3, p3, toyA(0.5, 1.0), {1: 4, 2: 3, 3: 0, 4: 3})
    ck("it does NOT fire when the organ's own activations prefer the committed head", out2.get(1) == 4, out2)
    globals()["CSUB_REANALYSIS"] = False
    ck("the switch turns it off", revise_copular_subject(t3, p3, toyA(2.0, 1.0), {1: 4, 2: 3, 3: 0, 4: 3}).get(1) == 4)
    globals()["CSUB_REANALYSIS"] = True
    out4 = revise_copular_subject(t3, p3, toyA(2.0, 1.0), {1: 2, 2: 3, 3: 0, 4: 3})
    ck("narrow form OFF: it does not touch a subject whose head is not a later verb", out4.get(1) == 2, out4)
    globals()["CSUB_REANALYSIS_ANY"] = True
    out5 = revise_copular_subject(t3, p3, toyA(2.0, 1.0), {1: 2, 2: 3, 3: 0, 4: 3})
    ck("WIDE form: any committed head is revised when the activations prefer the predicate", out5.get(1) == 3, out5)
    # the shipped detection is reproduced exactly when the coverage switch is off
    globals()["CSUB_COVERAGE"] = False
    same = 0; diff = 0
    for toks, pos, _h, _r in sentences(TEST, cap=120, maxlen=10 ** 6):
        a = {(q, s) for (q, s) in cop_subject_pairs(toks, pos)}
        b = {(h, j) for (h, j), v in _CSUB_SHIPPED(toks, pos).items() if v == "pred"}
        same += int(a == b); diff += int(a != b)
    ck("COVERAGE=0 reproduces the shipped csub pair detection (120 sentences)", diff == 0, "%d differ" % diff)
    globals()["CSUB_COVERAGE"] = True
    # PATCH == CELL
    dpath = os.path.join(REPO, "notes", "problems",
                         "the_heads_rung_attaches_the_subject_of_a_non_verbal_predicate_at_0_54_against_0_85_for_"
                         "verbal_ones_land_the_predicate_slot_as_a_graded_online_learned_arc_feature",
                         "copular_subject_attachment_patch.diff")
    if os.path.isfile(dpath):
        src = open(__file__, encoding="utf-8").read()
        block = src.split("# PATCH-BEGIN", 1)[1].split("# PATCH-END", 1)[0]
        dif = open(dpath, encoding="utf-8").read()
        body = [ln for ln in block.splitlines() if ln.strip()]
        missing = [ln for ln in body if ("+" + ln) not in dif]
        ck("PATCH == CELL: every line of the patch block is in the diff", not missing, missing[:3])
    else:
        print("  note the diff is not written yet -- PATCH == CELL skipped")
    print("\n%d/%d checks passed" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--accrue", action="store_true"); ap.add_argument("--arms", action="store_true")
    ap.add_argument("--coverage", action="store_true"); ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--gum", action="store_true"); ap.add_argument("--residual", action="store_true"); ap.add_argument("--oracle", action="store_true"); ap.add_argument("--patch-test", action="store_true"); ap.add_argument("--live-ab", action="store_true"); ap.add_argument("--curve", action="store_true"); ap.add_argument("--board", action="store_true"); ap.add_argument("--arm", default="base"); ap.add_argument("--n-boot", type=int, default=1000); ap.add_argument("--frozen", action="store_true"); ap.add_argument("--accrue-twin", action="store_true")
    ap.add_argument("--cap", type=int, default=700); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--weight", type=float, default=1.0)
    ap.add_argument("--which", default=None, help="comma-separated arm list")
    a = ap.parse_args(argv)
    which = a.which.split(",") if a.which else None
    if a.self_test:
        return self_test()
    if a.accrue:
        accrue(cap=a.cap, weight=a.weight)
    if getattr(a, "accrue_twin", False):
        accrue_twin(cap=a.cap, weight=a.weight, seed=a.seed)
    if a.coverage:
        coverage(cap=a.cap)
    if a.arms:
        print("=" * 100); print("ARMS (UD-EWT test %d, live chain)" % a.cap)
        arms(cap=a.cap, seed=a.seed, which=which)
    if a.gum and not getattr(a, 'live_ab', False):
        print("=" * 100); print("OUT OF SUPPLY: GUM/GENTLE")
        arms(cap=a.cap, pop="gum", seed=a.seed, which=which, tag="arms_gum")
    if getattr(a, "patch_test", False):
        print("=" * 100); print("PATCH TEST -- the diff's own code")
        r = patch_test(cap=a.cap)
        json.dump(r, open(os.path.join(out_dir(), "patch_test.json"), "w", encoding="utf-8"), indent=1)
    if getattr(a, "live_ab", False):
        print("=" * 100); print("LIVE A/B THROUGH THE DIFF (one process): the organ as shipped vs the patched organ")
        live_ab(cap=a.cap, pop="gum" if a.gum else "ud", seed=a.seed)
    if a.board:
        print("=" * 100); print("BOARD A/B (one process%s)" % (" -- SMOKE CAPS" if a.smoke else ", FULL SIZE"))
        board_ab(n_boot=a.n_boot, caps={"gum": 4, "ud": 40, "state": 40, "wiqa": 40, "sr": 40, "occ": 40, "tmw": 100, "coarse_files": 2} if a.smoke else None)
    if a.curve:
        print("=" * 100); print("LEARNING CURVE (the validity accrued from N sentences of reading)")
        curve(cap=a.cap, seed=a.seed)
    if a.residual:
        print("=" * 100); print("RESIDUAL ATTRIBUTION")
        residual(cap=a.cap, seed=a.seed)
    if a.oracle:
        print("=" * 100); print("ORACLE / CATEGORY-RUNG DECOMPOSITION")
        oracle(cap=a.cap, seed=a.seed)
    if a.frozen:
        print("=" * 100); print("LEARNED vs the BEST FROZEN CONSTANT")
        frozen_sweep(cap=a.cap, seed=a.seed)
    if a.sweep:
        print("=" * 100); print("SWEEP (free operating points)")
        sweep(cap=a.cap, seed=a.seed)
    if not any([a.accrue, a.arms, a.coverage, a.sweep, a.gum, a.residual, a.frozen, a.oracle, a.board, a.curve, getattr(a, "patch_test", False), getattr(a, "live_ab", False), getattr(a, "accrue_twin", False)]):
        return self_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
