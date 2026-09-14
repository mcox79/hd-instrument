"""CLAUSE MEMBERSHIP and CONSTITUENCY as cues in the ATTACHMENT arm of the Competition-Model organ
(problem pri-105, `the_governor_misattaches_one_core_argument_in_four_...the_labels_rung_needs_0_95`).

THE BRAIN'S MECHANISM (the opening move -- two DISTINCT computations are failing, so two cues are built).

 (a) CLAUSE MEMBERSHIP.  An argument belongs to the predicate whose clause it is in.  The reader segments the input
     into clauses AS IT ARRIVES -- a subordinator/complementiser OPENS a clause (Diessel 2004: complementizers are
     the acquisition cue for clause dependency), an infinitival `to` opens a non-finite one, a further predicate
     PROJECTS one -- and integrates each argument inside its own clause (Frazier & Fodor 1978 sausage machine: the
     first stage packages roughly a clause; Gibson 1998/2000 DLT: integration cost is paid across intervening
     discourse referents and clause boundaries; Just & Carpenter clause-final wrap-up).  In Competition-Model terms
     (Bates & MacWhinney 1989) the clause boundary is a CUE with a very high validity that the arm does not have:
     its only "distance" cues are log-distance and PUNCTUATION marks spanned, neither of which sees a predicate or a
     complementiser standing between a noun and the verb competing for it.
     -> `clause_cue` : for the arc (h -> j), how many PREDICATES and whether a CLAUSE OPENER stand between them.
        Values "0" / "0s" / "1" / "1s" / "2" / "2s" (n intervening predicates capped at 2; `s` = an opener too).
        Validity LEARNED per configuration exactly like every other cue -- a VERB may head a VERB across a boundary
        (that IS the subordinate-clause arc) while a VERB may not head a NOUN across one; nothing is hand-weighted.

 (b) CONSTITUENCY.  A noun phrase is a UNIT: its head is its rightmost noun (Right-hand Head Rule, Williams 1981)
     and a DETERMINER projects/opens the phrase (DP hypothesis; and, as an acquisition fact, function words are the
     infant's phrase-onset markers -- Shi & Melancon 2010, Bernal et al. 2010, Christophe et al. 2008 syntactic
     bootstrapping from function words).  An argument noun that carries its OWN determiner cannot be absorbed as a
     modifier of a neighbouring noun.  The arm's `npmod` construction and the `ADP -> np_head_after` frame currently
     scan a MAXIMAL contiguous run of DET/ADJ/NUM/NOUN/PROPN and attach everything to the run's LAST noun -- so in
     "gave the man a book" the whole run `the man a book` is one phrase and `man` is hung under `book`.  That is
     exactly the dominant constituency error class (101 of 1,160 core arguments absorbed into a nominal phrase).
     -> the same computation enters TWICE, as the brain has it: as a CUE (`npb`: does a phrase-onset marker stand
        between h and j -> they are different phrases) and as the SEGMENTATION the phrase-internal constructions
        use (a run is split at every determiner/possessive; the Right-hand Head Rule then applies WITHIN a phrase).

Both cues are categorical values whose strengths are the same learned log-odds contrasts as every other cue
(`strengths_from_arc_counts`), accrued from the SAME teacher posterior, with the SAME online `observe_arc_outcome`
path -- knowledge stays in the counts (plastic, never frozen).  No treebank tree is ever read while learning; UD is
a measuring instrument only.  No spaCy, no supervised parser, no external LLM.

Run:  python experiments/exp_attachment_clause_and_constituency_v1.py [--self-test] [--anatomy] [--smoke] [--full]
Writes only its own output dir (experiments._seed_checkpoint.get_output_dir).
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse
import json
import math
import random
import sys
import time
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
from hdlab.graded_parser import single_root_marginals
from tools.build_attachment_validities import sentences, TRAIN, TEST, knowledge_free_teacher

ANCHOR = "attachment_clause_and_constituency_v1"
RELS = ("root", "nsubj", "obj", "iobj", "obl", "nmod", "ccomp", "xcomp", "advcl", "conj", "amod", "det", "case",
        "compound", "flat", "punct")
CORE = ("nsubj", "obj", "iobj")            # the core-argument population (UD subtypes stripped by `sentences`)

WH = AA.WH_FORMS
POSS = frozenset({"my", "your", "his", "her", "its", "their", "our", "whose"})
OPENER_PUNCT = frozenset({",", ";", ":", "--", "—", "–"})

# ------------------------------------------------------------------------------------------------------------------
# (a) CLAUSE MEMBERSHIP
# ------------------------------------------------------------------------------------------------------------------
CLAUSE_MAXV = 2            # intervening predicates counted up to this (swept)
CLAUSE_PUNCT = {"on": False}   # count a clause-internal punctuation mark as an opener too (swept; the `boundary`
#                                cue already carries punctuation counts, so this double-counts by default OFF)
# THE OPENER'S INPUT IS THE WEAKEST TAG IN THE CHAIN (measured here, UD-EWT test 700: SCONJ recall 0.7384 against
# AUX 0.9843 / DET 0.9804 / PUNCT 0.9984; 31 SCONJ->ADP confusions), which is what makes the clause cue lose 7.1% of
# its pair values on the live chain.  The FUNCTIONAL opener test does not read the SCONJ tag at all: a function word
# is a COMPLEMENTISER when what follows it is a CLAUSE (a predicate arrives before the phrase closes) and a
# PREPOSITION when what follows is a nominal -- the complement-type distinction the child hears (Diessel 2004
# complementizers as the acquisition cue for clause dependency; Christophe et al. 2008 function words as the
# phrase/clause onset anchors).  Window and stop-set are swept operating points, never adopted.
OPENER_FUNCTIONAL = {"on": False}
OPENER_STOP = frozenset({"PUNCT", "ADP", "SCONJ", "CCONJ"})
# A PRONOUN IS A DETERMINER PHRASE (Postal 1969 "pronouns are articles"; Abney 1987 DP): it is a phrase of its own
# and never a modifier inside a neighbouring noun phrase, so it is both an onset and part of the nominal domain the
# constituency cue speaks about.  Flag: measured separately.
PRON_DP = {"on": False}


def predicate_flags(toks, pos):
    """Per 1-based token: is it a PREDICATE (a clause's assertion-bearing word) and is it a CLAUSE OPENER?
    Predicates: every VERB, plus a copular AUX that has no verb of its own (the arm's `cop_predicates` marks the
    non-verbal predicate; the AUX is the tense carrier and counts as the predicate token for segmentation).
    Openers: SCONJ, a wh relativizer/complementiser, infinitival `to`, and (optionally) a clause-internal mark."""
    n = len(pos); lows = [t.lower() for t in toks]
    pred = np.zeros(n + 1, dtype=np.int64); opn = np.zeros(n + 1, dtype=np.int64)
    cop = AA.cop_predicates(toks, pos)          # the arm's own copular-predication detector (a verbless clause's predicate)
    for i in range(1, n + 1):
        p = pos[i - 1]; w = lows[i - 1]
        if p == "VERB" or i in cop:
            pred[i] = 1
        if p == "SCONJ":
            opn[i] = 1
        elif p in ("PRON", "DET", "ADV") and w in WH:
            opn[i] = 1
        elif p == "PART" and w == "to":
            opn[i] = 1
        elif CLAUSE_PUNCT["on"] and p == "PUNCT" and toks[i - 1] in OPENER_PUNCT:
            opn[i] = 1
        elif OPENER_FUNCTIONAL["on"] and p == "ADP" and takes_a_clause(pos, i):
            opn[i] = 1                      # a preposition-shaped word whose complement is a CLAUSE is a complementiser
        if OPENER_FUNCTIONAL["on"] and p == "SCONJ" and not takes_a_clause(pos, i):
            opn[i] = 0                      # ... and a subordinator-shaped word whose complement is a NOMINAL is not
    return pred, opn


def takes_a_clause(pos, i, window=8):
    """The COMPLEMENT-TYPE test, read off categories + position only: scanning right from the function word at
    1-based i and stopping at a punctuation mark, another function word of the same family, or the sentence end,
    does a PREDICATE arrive?  Then the word opens a clause; otherwise its complement is a nominal phrase."""
    n = len(pos)
    for k in range(i + 1, min(n, i + window) + 1):
        p = pos[k - 1]
        if p in ("VERB", "AUX"):
            return True
        if p in OPENER_STOP:
            return False
    return False


def clause_matrices(toks, pos):
    """(nv, sub) prefix-sum matrices over 0..n x 1..n: nv[h][j] = predicates strictly between h and j (h = 0 is the
    ROOT arc: nothing intervenes), sub[h][j] = 1 if a clause opener stands strictly between them."""
    n = len(pos)
    pred, opn = predicate_flags(toks, pos)
    cp = np.concatenate([[0], np.cumsum(pred[1:])]); co = np.concatenate([[0], np.cumsum(opn[1:])])
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]
    lo = np.minimum(H, J); hi = np.maximum(H, J)
    nv = cp[np.maximum(hi - 1, 0)] - cp[lo]                  # strictly between: (lo, hi)
    sb = co[np.maximum(hi - 1, 0)] - co[lo]
    nv[0, :] = 0; sb[0, :] = 0                                # the root arc crosses nothing
    return np.minimum(nv, CLAUSE_MAXV), (sb > 0).astype(np.int64)


def clause_value(nv: int, sb: int) -> str:
    return ("%d" % nv) + ("s" if sb else "")


CLAUSE_VALUES = tuple(clause_value(v, s) for v in range(CLAUSE_MAXV + 1) for s in (0, 1))


# ------------------------------------------------------------------------------------------------------------------
# (b) CONSTITUENCY -- phrase onsets, the split runs, and the cue
# ------------------------------------------------------------------------------------------------------------------
def np_starts(toks, pos):
    """Per 1-based token: does it OPEN a NEW nominal phrase?  A determiner projects a phrase (DP hypothesis; and, as
    an acquisition fact, the determiner is the infant's phrase-onset marker -- Shi & Melancon 2010), but only a
    determiner arriving AFTER the current phrase already has its noun starts a SECOND phrase: "all the people" is one
    phrase with two determiners, "the man a book" is two phrases.  A possessive pronoun does the same job."""
    n = len(pos); lows = [t.lower() for t in toks]
    out = np.zeros(n + 1, dtype=np.int64); seen_head = False
    for i in range(1, n + 1):
        p = pos[i - 1]; w = lows[i - 1]
        if p not in AA.NP_RUN:
            if PRON_DP["on"] and p == "PRON" and w not in POSS:
                out[i] = 1                   # a pronoun IS a determiner phrase (Postal 1969; Abney 1987)
            seen_head = False
            continue
        if p == "DET" or (p == "PRON" and w in POSS):
            if seen_head:
                out[i] = 1; seen_head = False
        elif p in ("NOUN", "PROPN"):
            seen_head = True
    return out


def _np_domain(pos):
    dom = [p in AA.NP_RUN or (PRON_DP["on"] and p == "PRON") for p in pos]
    return np.array([False] + dom)


def split_runs(pos, starts):
    """Contiguous NP_RUN spans, SPLIT at every phrase onset: a list of (a, b) inclusive 1-based spans."""
    n = len(pos); out = []; i = 1
    while i <= n:
        if pos[i - 1] not in AA.NP_RUN:
            i += 1; continue
        a = i; j = i + 1
        while j <= n and pos[j - 1] in AA.NP_RUN and not starts[j]:
            j += 1
        out.append((a, j - 1)); i = j
    return out


def phrase_head(pos, a, b):
    """Right-hand Head Rule INSIDE one phrase: the last NOUN/PROPN, else the last ADJ/NUM."""
    nouns = [k for k in range(a, b + 1) if pos[k - 1] in ("NOUN", "PROPN")]
    if nouns:
        return nouns[-1]
    adjs = [k for k in range(a, b + 1) if pos[k - 1] in ("ADJ", "NUM")]
    return adjs[-1] if adjs else None


def npmod_arcs_split(toks, pos):
    """The arm's `npmod_arcs`, with the run split at phrase onsets (the ONLY change)."""
    starts = np_starts(toks, pos); out = []
    for (a, b) in split_runs(pos, starts):
        h = phrase_head(pos, a, b)
        if h is None or pos[h - 1] not in ("NOUN", "PROPN"):
            continue
        for k in range(a, b + 1):
            if k != h:
                out.append((h, k))
    return out


def function_word_arcs_split(toks, pos):
    """The arm's `function_word_arcs` with ONE change: `np_head_after` respects phrase onsets, so a preposition
    binds the head of the phrase it opens, not the last noun of a run that contains several phrases."""
    starts = np_starts(toks, pos)
    orig = AA._np_head_after_impl if hasattr(AA, "_np_head_after_impl") else None

    def np_head_after0(i0):                                  # 0-based, as in the arm
        i = i0 + 1
        if pos[i - 1] not in AA.NP_RUN:
            return None
        j = i + 1
        while j <= len(pos) and pos[j - 1] in AA.NP_RUN and not starts[j]:
            j += 1
        h = phrase_head(pos, i, j - 1)
        return None if h is None or pos[h - 1] not in ("NOUN", "PROPN") else h - 1
    return _fw_arcs_with(toks, pos, np_head_after0)


def _fw_arcs_with(toks, pos, np_head_after):
    """`hdlab.attachment_arm.function_word_arcs` verbatim, with `np_head_after` injected (0-based in and out)."""
    n = len(pos); out = []; lows = [t.lower() for t in toks]
    COP = AA.COP_FORMS

    def next_verb(i):
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                return k
            if pos[k] == "PUNCT":
                break
        return None

    def next_predicate(i):
        for k in range(i + 1, n):
            if pos[k] == "VERB" or pos[k] == "PUNCT":
                return None
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                if pos[k] == "PRON":
                    return k
                h = np_head_after(k)
                if h is not None:
                    return h
                j = k
                while j + 1 < n and pos[j + 1] in ("ADJ", "ADV", "NUM"):
                    j += 1
                adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
                return adjs[-1] if adjs else k
        return None
    for i in range(n):
        p = pos[i]
        if p == "ADP" and i + 1 < n and pos[i + 1] in AA.NP_RUN:
            h = np_head_after(i + 1)
            if h is not None:
                out.append((h + 1, i + 1))
        elif p == "AUX":
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
            elif lows[i] in COP:
                q = next_predicate(i)
                if q is not None:
                    out.append((q + 1, i + 1))
                    k = i - 1
                    while k >= 0 and pos[k] in ("ADV", "PART", "PUNCT"):
                        k -= 1
                    subj = None
                    while k >= 0:
                        if pos[k] in ("NOUN", "PROPN", "PRON", "NUM"):
                            a = k
                            while a - 1 >= 0 and pos[a - 1] in AA.NP_RUN:
                                a -= 1
                            if a - 1 >= 0 and pos[a - 1] == "ADP":
                                k = a - 2
                                continue
                            subj = k
                            break
                        if pos[k] in ("VERB", "SCONJ", "CCONJ"):
                            break
                        k -= 1
                    if subj is not None and subj != q:
                        out.append((q + 1, subj + 1))
        elif p == "SCONJ" or (p == "PART" and lows[i] == "to"):
            v = next_verb(i)
            if v is not None:
                out.append((v + 1, i + 1))
        elif p == "PROPN" and i > 0 and pos[i - 1] == "PROPN":
            k = i
            while k > 0 and pos[k - 1] == "PROPN":
                k -= 1
            out.append((k + 1, i + 1))
        elif p == "PUNCT":
            cands = [k for k in range(n) if pos[k] == "VERB"]
            if cands:
                h = min(cands, key=lambda k: (abs(k - i), k))
                out.append((h + 1, i + 1))
    return out


def npb_matrix(toks, pos):
    """Value id per (h, j): 0 = "na" (not a nominal-domain pair), 1 = "in" (same phrase / no onset between),
    2 = "cross" (a phrase onset stands between them -- they are different phrases)."""
    n = len(pos)
    starts = np_starts(toks, pos)
    cs = np.concatenate([[0], np.cumsum(starts[1:])])
    dom = _np_domain(pos)
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]
    lo = np.minimum(H, J); hi = np.maximum(H, J)
    # an onset in (lo, hi] : the later token's own onset also separates it from the earlier one
    nstart = cs[hi] - cs[lo]
    v = np.where(nstart > 0, 2, 1)
    both = np.concatenate([np.zeros((1, n), dtype=bool), (dom[1:, None] & dom[None, 1:])], axis=0)
    return np.where(both, v, 0)


NPB_VALUES = ("na", "in", "cross")


# ------------------------------------------------------------------------------------------------------------------
# (c) THE COMPOUND ASSOCIATION -- the lever the reachability count points to.  MEASURED HERE (anatomy): only 3 of the
# 97 absorbed core arguments have a phrase ONSET between them and the noun that swallowed them; 94 are BARE noun-noun
# sequences, where the Right-hand Head Rule genuinely licenses the compound reading and no boundary cue can help.
# What separates "[the manager] [Monday] called" from "[the manager Monday]" is not a boundary, it is whether the two
# nouns FORM a compound -- a lexicalist constraint (MacDonald-Pearlmutter-Seidenberg 1994: lexical co-occurrence
# statistics are cues in the competition; the same shape as the Hindle & Rooth 1993 preposition association the arm
# already carries as `pp`).  Learned TREEBANK-FREE from reading: adjacent noun-noun pair counts and their marginals,
# read out as a binned pointwise association whose bin validities are learned like every other cue.
def nn_assoc_from_reading(sents):
    """Adjacent NOUN/PROPN pair counts from (tokens, categories) only."""
    from collections import defaultdict as _dd
    pair = _dd(float); left = _dd(float); right = _dd(float); tot = 0.0
    for toks, pos in sents:
        low = [t.lower() for t in toks]
        for i in range(1, len(toks)):
            if pos[i - 1] in ("NOUN", "PROPN") and pos[i] in ("NOUN", "PROPN"):
                pair[low[i - 1] + "|" + low[i]] += 1.0; left[low[i - 1]] += 1.0; right[low[i]] += 1.0; tot += 1.0
    return {"pair": dict(pair), "left": dict(left), "right": dict(right), "tot": tot}


def nn_pmi(assoc, w1, w2):
    """Pointwise association of the adjacent pair (w1 modifies w2), add-0.5 smoothed; 0.0 when either word is unseen."""
    if not assoc or assoc["tot"] <= 0:
        return 0.0
    l = assoc["left"].get(w1, 0.0); r = assoc["right"].get(w2, 0.0)
    if l <= 0 or r <= 0:
        return 0.0
    c = assoc["pair"].get(w1 + "|" + w2, 0.0)
    return math.log((c + 0.5) * assoc["tot"] / (l * r))


def _nn_bin(x):
    return "hi" if x > 1.5 else "mid" if x > 0.0 else "lo" if x > -1.5 else "no"


NN_ASSOC = {"tab": None}
NN_VALUES = ("na", "hi", "mid", "lo", "no")


def nn_matrix(toks, pos):
    """Value id per (h, j): 1..4 for an ADJACENT bare noun-noun pair, else 0 = na -- the compound reading's own
    lexical evidence, placed on the arc that proposes it."""
    n = len(pos); V = np.zeros((n + 1, n), dtype=np.int64)
    a = NN_ASSOC["tab"]
    if a is None:
        return V
    low = [t.lower() for t in toks]
    bins = {"hi": 1, "mid": 2, "lo": 3, "no": 4}
    for j in range(1, n + 1):
        if pos[j - 1] not in ("NOUN", "PROPN"):
            continue
        for h in (j - 1, j + 1):
            if h < 1 or h > n or pos[h - 1] not in ("NOUN", "PROPN"):
                continue
            w1, w2 = (low[j - 1], low[h - 1]) if j < h else (low[h - 1], low[j - 1])
            V[h][j - 1] = bins[_nn_bin(nn_pmi(a, w1, w2))]
    return V


# ------------------------------------------------------------------------------------------------------------------
# THE ACQUISITION TEACHER'S MISSING HALF (the pattern that carried pri-95 coordination and pri-97 predication: the
# read-time cue can only learn a validity from a teacher posterior that puts mass on the class of arcs the cue is
# about).  The knowledge-free teacher is locality + semantic plausibility: it has no notion of a clause or a phrase,
# so a noun's mass is spread over every nearby verb whatever stands between them.  The child's first-stage parser
# packages roughly a clause and integrates inside it (Frazier & Fodor 1978; clause-boundary integration -- reading
# time rises at clause boundaries because integration happens THERE, not across them), and a determiner opens a new
# phrase (Shi & Melancon 2010; Bernal et al. 2010; Christophe et al. 2008).  So the teacher is given the same two
# facts as a PENALTY on crossing arcs -- treebank-free, categories + position only.  gammas SWEPT, never adopted.
BOUNDARY_GAMMA = float(os.environ.get("HDLAB_CLAUSE_TEACH_GAMMA", "4.0"))


def boundary_penalty(A, toks, pos, g_clause=None, g_np=None):
    """ACQUISITION signal: penalise a teacher arc that crosses a clause boundary or a phrase onset."""
    g_clause = BOUNDARY_GAMMA if g_clause is None else g_clause
    g_np = BOUNDARY_GAMMA if g_np is None else g_np
    n = len(pos); B = A.copy()
    nv, sb = clause_matrices(toks, pos); V = npb_matrix(toks, pos)
    for j in range(1, n + 1):
        for h in range(1, n + 1):
            if h == j or not np.isfinite(B[h][j]):
                continue
            d = 0.0
            if g_clause:
                d -= g_clause * (float(nv[h][j - 1]) + float(sb[h][j - 1]))
            if g_np and V[h][j - 1] == 2:
                d -= g_np
            B[h][j] += d
    return B


# ------------------------------------------------------------------------------------------------------------------
# the patch layer (the arm is never edited: strategy lands the diff)
# ------------------------------------------------------------------------------------------------------------------
_ORIG_CUES = AA.SentenceCues.cues
_ORIG_ARC = AA.arc_scores
_ORIG_CUE_TUPLE = AA.CUES
_ORIG_NPMOD = AA.npmod_arcs
_ORIG_FW = AA.function_word_arcs
_ORIG_CONSTR = dict(AA.CONSTRUCTIONS)

ARM = {"clause": False, "npb": False, "nn": False, "split": False, "shuffle": False, "rng": None, "wrapup": False}
NEW_CUES = ("clause", "npb", "nn")


def _sent_clause(self):
    m = getattr(self, "_clause_m", None)
    if m is None:
        m = self._clause_m = clause_matrices(self.toks, self.pos)
    return m


def _sent_npb(self):
    m = getattr(self, "_npb_m", None)
    if m is None:
        m = self._npb_m = npb_matrix(self.toks, self.pos)
    return m


def _sent_nn(self):
    m = getattr(self, "_nn_m", None)
    if m is None:
        m = self._nn_m = nn_matrix(self.toks, self.pos)
    return m


def _patched_cues(self, j, h):
    d = _ORIG_CUES(self, j, h)
    if ARM["clause"]:
        nv, sb = _sent_clause(self)
        d = dict(d); d["clause"] = clause_value(int(nv[h][j - 1]), int(sb[h][j - 1]))
    if ARM["npb"]:
        V = _sent_npb(self); v = int(V[h][j - 1])
        if v:
            d = dict(d); d["npb"] = NPB_VALUES[v]
    if ARM["nn"]:
        V = _sent_nn(self); v = int(V[h][j - 1])
        if v:
            d = dict(d); d["nn"] = NN_VALUES[v]
    return d


def _cfg_ids(ix, pos, n):
    """The configuration id per (head row 0..n, dependent col 1..n) -- the same indexing the arm's fast path uses."""
    cat = np.array([ix.cats.get(p, ix.unk) for p in pos], dtype=np.int64)
    H = np.arange(0, n + 1)[:, None]; J = np.arange(1, n + 1)[None, :]
    dr = (H > J).astype(np.int64)
    hc = np.concatenate([[ix.unk], cat])
    C = ix.cfg_id[hc[:, None], cat[None, :], dr]; C[0, :] = ix.root_cfg_id[cat]
    return C


def _patched_arc_scores(toks, pos, table=None):
    """The arm's vectorised readout plus the two new cue contributions, added over the same grid (vectorised: the
    cue tables are the arm's OWN dense index, so the values enter exactly as any other cue does)."""
    A, n = _ORIG_ARC(toks, pos, table)
    if not (ARM["clause"] or ARM["npb"] or ARM["nn"]) or n == 0:
        return A, n
    tab = table or AA.load_attachment_validities()
    ix = AA._arc_index(tab); C = _cfg_ids(ix, pos, n)
    if ARM["clause"] and "clause" in ix.cue_tab:
        nv, sb = clause_matrices(toks, pos)
        if ARM["shuffle"]:
            nv, sb = _shuffle_pairs(nv, sb, n)
        vid = ix.val_id["clause"]
        lut = np.array([[vid.get(clause_value(v, s), 0) for s in (0, 1)] for v in range(CLAUSE_MAXV + 1)],
                       dtype=np.int64)
        A[:, 1:] += ix.cue_tab["clause"][C, lut[nv, sb]]
    if ARM["npb"] and "npb" in ix.cue_tab:
        V = npb_matrix(toks, pos)
        if ARM["shuffle"]:
            V = _shuffle_one(V, n)
        vid = ix.val_id["npb"]
        lut = np.array([0] + [vid.get(v, 0) for v in NPB_VALUES[1:]], dtype=np.int64)
        A[:, 1:] += ix.cue_tab["npb"][C, lut[V]]
    if ARM["nn"] and "nn" in ix.cue_tab:
        V = nn_matrix(toks, pos)
        if ARM["shuffle"]:
            V = _shuffle_one(V, n)
        vid = ix.val_id["nn"]
        lut = np.array([0] + [vid.get(v, 0) for v in NN_VALUES[1:]], dtype=np.int64)
        A[:, 1:] += ix.cue_tab["nn"][C, lut[V]]
    return A, n


def _perm(n):
    idx = list(range(1, n + 1)); ARM["rng"].shuffle(idx); return [0] + idx


def _shuffle_pairs(nv, sb, n):
    p = _perm(n)
    nv2 = np.zeros_like(nv); sb2 = np.zeros_like(sb)
    for j in range(1, n + 1):
        for h in range(0, n + 1):
            nv2[h][j - 1] = nv[p[h] if h else 0][p[j] - 1]; sb2[h][j - 1] = sb[p[h] if h else 0][p[j] - 1]
    return nv2, sb2


def _shuffle_one(V, n):
    p = _perm(n); V2 = np.zeros_like(V)
    for j in range(1, n + 1):
        for h in range(0, n + 1):
            V2[h][j - 1] = V[p[h] if h else 0][p[j] - 1]
    return V2


# ------------------------------------------------------------------------------------------------------------------
# CLAUSE-CLOSE WRAP-UP (read-time only; no rebuild).  The arm already integrates words that have waited too long at a
# CLAUSE BOUNDARY (`INCR_CLAUSE_WRAPUP`, Just & Carpenter clause-final wrap-up) -- but its trigger is punctuation or a
# coordinator ONLY, so the boundary that a subordinator/complementiser/infinitival `to` OPENS never fires one, and a
# word left waiting from the matrix clause is still competing when the embedded clause's verb arrives.  The trigger
# set is the SAME clause-opener computation as the cue.  `incremental_tree` reads `pos_seq` for nothing else, so the
# arm needs one line: the trigger becomes "punctuation, coordinator, or a clause opener".
def _wrapup_pos(toks, pos):
    _, opn = predicate_flags(toks, pos)
    return [("CCONJ" if (opn[i] and pos[i - 1] not in ("PUNCT", "CCONJ")) else pos[i - 1]) for i in range(1, len(pos) + 1)]


_ORIG_DECODE = AA.decode


def _patched_decode(toks, pos, A, n, temp=1.0, table=None):
    if not ARM.get("wrapup") or AA.DECODE != "incr":
        return _ORIG_DECODE(toks, pos, A, n, temp, table)
    hv = AA.hold_expectation(pos, table, None, toks) + AA.INCR_HOLD
    hd, post = AA.incremental_tree(A, n, AA.INCR_BEAM, hv, temp, pos_seq=_wrapup_pos(toks, pos))
    hd = AA.occupancy_repair(toks, pos, hd, post)
    hd = AA.punct_convention(toks, pos, hd)
    for j in range(1, len(toks) + 1):
        if AA.PUNCT_CONVENTION and pos[j - 1] == "PUNCT" and j in post:
            post[j] = {hd[j]: 1.0}
    return hd, post


def enable(clause=False, npb=False, nn=False, split=False, shuffle=False, seed=11, functional=False, pron_dp=False, wrapup=False):
    """Turn the arm's extension on/off.  `split` = the phrase-onset segmentation inside the constructions;
    `functional` = the complement-type opener test (no SCONJ tag); `pron_dp` = a pronoun is its own phrase."""
    ARM["clause"] = clause; ARM["npb"] = npb; ARM["nn"] = nn; ARM["split"] = split
    ARM["shuffle"] = shuffle; ARM["rng"] = random.Random(seed); ARM["wrapup"] = wrapup
    OPENER_FUNCTIONAL["on"] = functional; PRON_DP["on"] = pron_dp
    AA.decode = _patched_decode if wrapup else _ORIG_DECODE
    cues = tuple(_ORIG_CUE_TUPLE) + tuple(c for c in NEW_CUES if ARM[c])
    AA.CUES = cues
    AA.SentenceCues.cues = _patched_cues if (clause or npb or nn) else _ORIG_CUES
    AA.arc_scores = _patched_arc_scores if (clause or npb or nn) else _ORIG_ARC
    if split:
        AA.npmod_arcs = npmod_arcs_split; AA.function_word_arcs = function_word_arcs_split
        AA.CONSTRUCTIONS = dict(_ORIG_CONSTR, npmod=npmod_arcs_split, fw=function_word_arcs_split)
    else:
        AA.npmod_arcs = _ORIG_NPMOD; AA.function_word_arcs = _ORIG_FW
        AA.CONSTRUCTIONS = dict(_ORIG_CONSTR)
    AA._TABLE = None


# ------------------------------------------------------------------------------------------------------------------
# build / evaluate
# ------------------------------------------------------------------------------------------------------------------
def build_table(train, teacher, frames, pp_assoc, rounds=3, alpha=0.8, teach=False):
    """One asset build under the CURRENT arm configuration (the landed pipeline, nothing else changed).
    `teach` adds the boundary penalty to the ACQUISITION teacher (the missing-half signal)."""
    counts = AA.new_counts(); tmarg = {}
    for i, (toks, pos, _, _) in enumerate(train):
        A, n = teacher._score_matrix(toks, pos)
        A = AA.parallelism_boost(A, toks, pos)
        A = AA.predication_boost(A, toks, pos)
        if teach:
            A = boundary_penalty(A, toks, pos)
        mt = single_root_marginals(A, n, 1.0); tmarg[i] = mt
        AA.accrue_sentence(counts, AA.SentenceCues(toks, pos, frames, pp_assoc), mt)
    table = {"counts": counts, "frames": frames, "pp_assoc": pp_assoc, "strength": AA.strengths_from_arc_counts(counts)}
    for _ in range(rounds):
        nxt = AA.new_counts()
        for i, (toks, pos, _, _) in enumerate(train):
            ms = AA.head_posterior(toks, pos, table); mt = tmarg[i]; n = len(toks)
            mix = {j: {h: alpha * ms.get(j, {}).get(h, 0.0) + (1 - alpha) * mt.get(j, {}).get(h, 0.0)
                       for h in set(ms.get(j, {})) | set(mt.get(j, {}))} for j in range(1, n + 1)}
            AA.accrue_sentence(nxt, AA.SentenceCues(toks, pos, frames, pp_assoc), mix)
        table = {"counts": nxt, "frames": frames, "pp_assoc": pp_assoc, "strength": AA.strengths_from_arc_counts(nxt)}
    return table


def _classify(pos, rels, hg, hd, j):
    """The pri-103 error taxonomy for one core argument j: what did the governor do with it?"""
    g = hg[j - 1]; h = hd.get(j, -1)
    if h == g:
        return "ok"
    if h == 0:
        return "root"
    if h < 1 or h > len(pos):
        return "other"
    ph = pos[h - 1]
    if ph in ("VERB", "AUX"):
        gp = pos[g - 1] if 1 <= g <= len(pos) else ""
        if gp in ("VERB", "AUX"):
            return "wrong_predicate"
        return "wrong_clause_pred"
    if ph in ("NOUN", "PROPN", "PRON", "NUM", "ADJ"):
        return "np_absorbed"
    return "function_word"


def evaluate(table, test, decode, tags=None, tag_post=None):
    """Per-sentence hits (paired bootstrap over sentences) + the core-argument decomposition.
    `tags`: None = gold categories; a list of per-sentence category lists = the live chain.  `tag_post`: the category
    organ's POSTERIOR per sentence -- then the whole competition is marginalised over it, which is what the live
    frontend hands its consumers (`hdlab/frontend.Parser.parse`)."""
    AA.DECODE = decode
    tot = ok = 0; rt = Counter(); rk = Counter(); cls = Counter()
    per_sent = []; core_hit = []; core_n = []; root_hit = []; root_n = []
    for si, (toks, gold_pos, hg, rels) in enumerate(test):
        pos = gold_pos if tags is None else tags[si]
        if tag_post is not None:
            A, n = AA.arc_scores_graded(toks, pos, tag_post[si], table)
        else:
            A, n = AA.arc_scores(toks, pos, table)
        hd, _ = AA.decode(toks, pos, A, n)
        s_ok = 0; s_tot = 0; c_ok = 0; c_tot = 0; r_ok = 0; r_tot = 0
        for i, (g, r) in enumerate(zip(hg, rels), start=1):
            hit = int(hd.get(i, -1) == g); s_ok += hit; s_tot += 1
            if r in RELS:
                rt[r] += 1; rk[r] += hit
            if r == "root":
                r_ok += hit; r_tot += 1
            if r in CORE:
                c_ok += hit; c_tot += 1
                cls[_classify(pos, rels, hg, hd, i)] += 1
        tot += s_tot; ok += s_ok
        per_sent.append((s_ok, s_tot)); core_hit.append(c_ok); core_n.append(c_tot)
        root_hit.append(r_ok); root_n.append(r_tot)
    return {"uas": round(ok / max(1, tot), 4), "tokens": tot,
            "core": round(sum(core_hit) / max(1, sum(core_n)), 4), "core_n": sum(core_n),
            "root": round(sum(root_hit) / max(1, sum(root_n)), 4),
            "rel": {r: round(rk[r] / max(1, rt[r]), 4) for r in RELS if rt[r]},
            "classes": dict(cls),
            "_per_sent": per_sent, "_core_hit": core_hit, "_core_n": core_n,
            "_root_hit": root_hit, "_root_n": root_n}


def paired_ci(a_hit, a_n, b_hit, b_n, iters=4000, seed=17):
    rng = random.Random(seed); m = len(a_hit)
    A = sum(a_hit) / max(1, sum(a_n)); B = sum(b_hit) / max(1, sum(b_n)); ds = []
    for _ in range(iters):
        s = [rng.randrange(m) for _ in range(m)]
        an = sum(a_n[i] for i in s) or 1; bn = sum(b_n[i] for i in s) or 1
        ds.append(sum(b_hit[i] for i in s) / bn - sum(a_hit[i] for i in s) / an)
    ds.sort(); lo = ds[int(0.025 * iters)]; hi = ds[int(0.975 * iters)]
    return round(B - A, 4), round(lo, 4), round(hi, 4), round((hi - lo) / 2, 4)


def ci(a, b, key):
    return paired_ci(a["_%s_hit" % key], a["_%s_n" % key], b["_%s_hit" % key], b["_%s_n" % key])


def uas_ci(a, b):
    return paired_ci([x[0] for x in a["_per_sent"]], [x[1] for x in a["_per_sent"]],
                     [x[0] for x in b["_per_sent"]], [x[1] for x in b["_per_sent"]])


def live_tags(test, posterior=False):
    """The category organ's own tags (and, with posterior=True, its graded hand-off) -- the live chain."""
    import hdlab.lexical_categories as LC
    lc = LC.get()
    if not posterior:
        return [lc.tag(list(toks)) for toks, _, _, _ in test]
    tags = []; post = []
    for toks, _, _, _ in test:
        t, p = lc.tag_with_posterior(list(toks)); tags.append(list(t)); post.append(p)
    return tags, post


EMBED = {"ccomp", "xcomp", "advcl", "acl", "acl:relcl", "csubj", "csubj:pass", "parataxis"}
TARGET = {"nsubj", "nsubj:pass", "obj"}


def _sentences_subtyped(path, cap=700):
    """Subtype-preserving gold loader (the labels-rung diagnostic's own loader: `nsubj:pass` must not be stripped)."""
    out, toks, pos, heads, rels = [], [], [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    out.append((toks, pos, heads, rels))
                    if cap and len(out) >= cap:
                        break
                toks, pos, heads, rels = [], [], [], []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            toks.append(c[1]); pos.append(c[3]); heads.append(int(c[6])); rels.append(c[7])
    if toks and (not cap or len(out) < cap):
        out.append((toks, pos, heads, rels))
    return out


def labels_rung(table, tags, cap=700):
    """THE CONSUMER: the labels rung (`graded_role_assigner.coarse_roles`) read through THESE heads, split by clause
    type exactly as `experiments/_diag_roles_by_clause_type.py` does -- with per-sentence hits so the consequence can
    be bootstrapped paired against the floor's heads."""
    from hdlab import graded_role_assigner as GRA
    val = GRA.load_coarse_validities()
    test = _sentences_subtyped(TEST, cap=cap)
    hit = {}; tot = {}; per_sent = {}
    for si, (toks, gold_pos, gold_heads, rels) in enumerate(test):
        pos = tags[si] if tags is not None else list(gold_pos)
        heads = AA.heads(toks, pos, table)
        roles = GRA.coarse_roles(toks, pos, heads, val)
        for key in ("matrix|nsubj", "embedded|nsubj", "copular|nsubj", "matrix|obj", "embedded|obj", "all|core"):
            per_sent.setdefault(key, []).append([0, 0])
        for i in range(1, len(toks) + 1):
            g = rels[i - 1]
            if g not in TARGET:
                continue
            h = gold_heads[i - 1]
            ct = "matrix" if h <= 0 else ("copular" if gold_pos[h - 1] not in ("VERB", "AUX")
                                          else ("embedded" if rels[h - 1] in EMBED else "matrix"))
            gg = "nsubj" if g.startswith("nsubj") else "obj"
            ok = int(roles.get(i, "<none>") == g)
            for key in ("%s|%s" % (ct, gg), "all|core"):
                hit[key] = hit.get(key, 0) + ok; tot[key] = tot.get(key, 0) + 1
                if key in per_sent:
                    per_sent[key][si][0] += ok; per_sent[key][si][1] += 1
    return {"recall": {k: round(hit[k] / tot[k], 4) for k in sorted(tot)}, "n": dict(tot),
            "_per_sent": {k: v for k, v in per_sent.items()}}


def labels_ci(a, b, key):
    pa = a["_per_sent"][key]; pb = b["_per_sent"][key]
    return paired_ci([x[0] for x in pa], [x[1] for x in pa], [x[0] for x in pb], [x[1] for x in pb])


def _print(name, r):
    print("%-22s UAS %.4f core %.4f root %.3f | nsubj %.3f obj %.3f obl %.3f nmod %.3f compound %.3f ccomp %.3f conj %.3f"
          % (name, r["uas"], r["core"], r["root"], r["rel"].get("nsubj", 0), r["rel"].get("obj", 0),
             r["rel"].get("obl", 0), r["rel"].get("nmod", 0), r["rel"].get("compound", 0),
             r["rel"].get("ccomp", 0), r["rel"].get("conj", 0)), flush=True)
    print("%22s classes %s" % ("", sorted(r["classes"].items(), key=lambda kv: -kv[1])), flush=True)


# ------------------------------------------------------------------------------------------------------------------
def anatomy(cap=700):
    """The baseline decomposition on the LIVE asset: what the governor does with each core argument, and what the
    two proposed cues would have to see.  Reproduces (on the current asset) the pri-103 error taxonomy."""
    test = sentences(TEST, cap=cap, maxlen=10 ** 6)
    enable()
    tab = AA.load_attachment_validities()
    out = {}
    for dec in ("incr", "map1"):
        r = evaluate(tab, test, dec)
        out[dec] = {k: r[k] for k in ("uas", "core", "core_n", "root", "rel", "classes")}
        _print("live asset / " + dec, r)
    # how often does the intervening-predicate / phrase-onset signal actually separate right from wrong?
    AA.DECODE = "incr"
    stat = Counter()
    for toks, pos, hg, rels in test:
        A, n = AA.arc_scores(toks, pos, tab); hd, _ = AA.decode(toks, pos, A, n)
        nv, sb = clause_matrices(toks, pos); V = npb_matrix(toks, pos)
        for i, (g, r) in enumerate(zip(hg, rels), start=1):
            if r not in CORE:
                continue
            h = hd.get(i, -1)
            if h == g:
                stat["ok|clause_" + clause_value(int(nv[g][i - 1]), int(sb[g][i - 1]))] += 1
                stat["ok|npb_" + NPB_VALUES[int(V[g][i - 1])]] += 1
            elif 0 <= h <= n:
                stat["miss|clause_" + clause_value(int(nv[h][i - 1]), int(sb[h][i - 1]))] += 1
                stat["miss|npb_" + NPB_VALUES[int(V[h][i - 1])]] += 1
                stat["missgold|clause_" + clause_value(int(nv[g][i - 1]), int(sb[g][i - 1]))] += 1
                stat["missgold|npb_" + NPB_VALUES[int(V[g][i - 1])]] += 1
    # WHICH absorbed arguments can a boundary cue even reach?  Split the constituency class by whether a phrase
    # ONSET actually separates the argument from the noun that swallowed it (a determiner-marked second phrase) or
    # not (a bare noun-noun sequence, where the Right-hand Head Rule genuinely licenses the compound reading and the
    # disambiguation needs meaning, not a boundary) -- checklist item 4.
    split_stat = Counter()
    for toks, pos, hg, rels in test:
        A, n = AA.arc_scores(toks, pos, tab); hd, _ = AA.decode(toks, pos, A, n)
        V = npb_matrix(toks, pos); nv, sb = clause_matrices(toks, pos)
        for i, (g, r) in enumerate(zip(hg, rels), start=1):
            if r not in CORE:
                continue
            h = hd.get(i, -1)
            if h == g or not (1 <= h <= n):
                continue
            cl = _classify(pos, rels, hg, hd, i)
            if cl == "np_absorbed":
                split_stat["absorbed|" + NPB_VALUES[int(V[h][i - 1])]] += 1
                split_stat["absorbed|det_between" if int(V[h][i - 1]) == 2 else "absorbed|bare"] += 1
            elif cl in ("wrong_predicate", "wrong_clause_pred"):
                split_stat["wrongclause|" + clause_value(int(nv[h][i - 1]), int(sb[h][i - 1]))] += 1
    out["class_reachability"] = dict(split_stat)
    print("reachability of each error class by the two cues:", flush=True)
    for k in sorted(split_stat):
        print("   %-28s %d" % (k, split_stat[k]), flush=True)
    out["cue_separation"] = dict(stat)
    print("cue separation (chosen arc vs gold arc, core arguments):", flush=True)
    for k in sorted(stat):
        print("   %-24s %d" % (k, stat[k]), flush=True)
    return out


def ceiling(cap=700, gammas=(1.0, 2.0, 4.0, 8.0, 1000.0), which_list=("clause", "npb", "nn", "both")):
    """ORACLE-CEILING PROBE, run on the LIVE asset before trusting any learned form: how much of the core-argument
    error is reachable by the two constraints AT ALL?  Apply the boundary as a hand-set penalty at read time (NOT
    learned, NOT shipped -- this is the headroom measurement the wall-push protocol asks for) and sweep its size."""
    test = sentences(TEST, cap=cap, maxlen=10 ** 6)
    enable(); tab = AA.load_attachment_validities()
    base = evaluate(tab, test, "incr"); _print("live asset", base)
    out = {"base": {k: base[k] for k in ("uas", "core", "root", "classes")}, "sweep": {}}
    orig = AA.arc_scores
    if NN_ASSOC["tab"] is None:          # the compound association is learned from the TRAINING tokens (no gold)
        tr = sentences(TRAIN, cap=6000)
        NN_ASSOC["tab"] = nn_assoc_from_reading([(t, p) for t, p, _, _ in tr])
        print("noun-noun association: %d adjacent pairs, %d types" % (int(NN_ASSOC["tab"]["tot"]),
                                                                      len(NN_ASSOC["tab"]["pair"])), flush=True)
    for which in which_list:
        for g in gammas:
            def patched(toks, pos, table=None, _w=which, _g=g):
                A, n = orig(toks, pos, table)
                if _w in ("clause", "both"):
                    nv, sb = clause_matrices(toks, pos)
                    A[:, 1:] -= _g * (nv + sb)
                if _w in ("npb", "both"):
                    V = npb_matrix(toks, pos)
                    A[:, 1:] -= _g * (V == 2)
                if _w == "nn":
                    V = nn_matrix(toks, pos)
                    A[:, 1:] -= _g * ((V == 3) | (V == 4))     # a bare noun-noun pair with LOW association
                return A, n
            AA.arc_scores = patched
            r = evaluate(tab, test, "incr")
            out["sweep"]["%s_g%g" % (which, g)] = {k: r[k] for k in ("uas", "core", "root", "classes")}
            print("%-8s gamma %-6g core %.4f (%+.4f)  UAS %.4f (%+.4f)  compound %.3f flat %.3f  classes %s"
                  % (which, g, r["core"], r["core"] - base["core"], r["uas"], r["uas"] - base["uas"],
                     r["rel"].get("compound", 0), r["rel"].get("flat", 0),
                     sorted(r["classes"].items(), key=lambda kv: -kv[1])[:4]), flush=True)
    AA.arc_scores = orig
    return out


def why_absorbed(cap=700):
    """WHY does the argument not go to the right verb when the compound arc is removed?  For every core argument the
    governor absorbed into a nominal phrase, ask what evidence the GOLD verb arc had: (a) does the meaning channel
    cover the pair at all (the self-grown typed selectional store, which is the arm's `plaus` cue), and (b) how far
    is the true head's arc activation from the one the governor chose?  This is the upstream trace: a boundary cue
    can only re-rank alternatives that are competitive."""
    from hdlab.attachment_arm import _plaus_teacher
    test = sentences(TEST, cap=cap, maxlen=10 ** 6)
    enable(); tab = AA.load_attachment_validities(); T = _plaus_teacher()
    st = Counter(); gaps = []
    for toks, pos, hg, rels in test:
        A, n = AA.arc_scores(toks, pos, tab); hd, post = AA.decode(toks, pos, A, n)
        for i, (g, r) in enumerate(zip(hg, rels), start=1):
            if r not in CORE:
                continue
            h = hd.get(i, -1)
            ok = (h == g)
            st["all|" + ("ok" if ok else "miss")] += 1
            if ok or not (1 <= h <= n) or not (1 <= g <= n):
                continue
            cl = _classify(pos, rels, hg, hd, i)
            if cl != "np_absorbed":
                continue
            st["absorbed"] += 1
            gold_is_verb = pos[g - 1] == "VERB"
            st["absorbed|goldhead_" + ("VERB" if gold_is_verb else pos[g - 1])] += 1
            if gold_is_verb:
                pl = T.slot_plausibility(toks, pos, g, i)
                st["absorbed|plaus_" + ("zero" if pl <= 0 else "lo" if pl < 0.05 else "mid" if pl < 0.2 else "hi")] += 1
                gap = float(A[h][i - 1]) - float(A[g][i - 1])
                gaps.append(gap)
                st["absorbed|gap_" + ("le1" if gap <= 1 else "le3" if gap <= 3 else "le6" if gap <= 6 else "gt6")] += 1
    out = {"counts": dict(st), "median_gap": float(np.median(gaps)) if gaps else None,
           "mean_gap": float(np.mean(gaps)) if gaps else None, "n_gaps": len(gaps)}
    print("WHY ABSORBED (core arguments swallowed by a noun):", flush=True)
    for k in sorted(st):
        print("   %-28s %d" % (k, st[k]), flush=True)
    print("   activation gap chosen-minus-gold: median %.2f mean %.2f (n=%d)"
          % (out["median_gap"] or 0, out["mean_gap"] or 0, out["n_gaps"]), flush=True)
    return out


def labels_consequence(cap=700, gamma=8.0):
    """THE CONSEQUENCE, measured without a rebuild: the labels rung read through the SAME heads, with and without
    the boundary constraint applied at read time (the oracle-probe form, gamma swept).  This answers the bar's
    "does the labels rung move as a consequence" for a core-arc improvement of exactly the size this brief's two
    computations can deliver, using the LIVE asset for both arms so nothing else differs."""
    test = sentences(TEST, cap=cap, maxlen=10 ** 6)
    tags = live_tags(test)
    enable(); tab = AA.load_attachment_validities()
    orig = AA.arc_scores
    base_heads = evaluate(tab, test, "incr", tags=tags)
    a = labels_rung(tab, tags, cap=cap)

    def patched(toks, pos, table=None):
        A, n = orig(toks, pos, table)
        nv, sb = clause_matrices(toks, pos)
        A[:, 1:] -= gamma * (nv + sb)
        V = npb_matrix(toks, pos)
        A[:, 1:] -= gamma * (V == 2)
        return A, n
    AA.arc_scores = patched
    arm_heads = evaluate(tab, test, "incr", tags=tags)
    b = labels_rung(tab, tags, cap=cap)
    AA.arc_scores = orig
    out = {"gamma": gamma,
           "heads_floor": {k: base_heads[k] for k in ("uas", "core", "root", "classes")},
           "heads_arm": {k: arm_heads[k] for k in ("uas", "core", "root", "classes")},
           "heads_core_ci": ci(base_heads, arm_heads, "core"),
           "labels_floor": a["recall"], "labels_arm": b["recall"], "labels_n": a["n"],
           "labels_ci": {k: labels_ci(a, b, k) for k in a["_per_sent"]}}
    print("LIVE CHAIN heads: core %.4f -> %.4f  %s | UAS %.4f -> %.4f"
          % (base_heads["core"], arm_heads["core"], out["heads_core_ci"], base_heads["uas"], arm_heads["uas"]), flush=True)
    for k in sorted(a["recall"]):
        v = out["labels_ci"][k]
        print("  labels %-16s %.4f -> %.4f  %+.4f CI[%+.4f,%+.4f] (n=%d)"
              % (k, a["recall"][k], b["recall"].get(k, 0), v[0], v[1], v[2], a["n"][k]), flush=True)
    return out


def upstream(cap=700):
    """THE SIGNAL TRACE (status probe): what the two new cues read from the category rung, and what the category
    organ's own tags cost them -- per tag, per cue value, with counts.  UD's UPOS column is the measuring
    instrument only."""
    test = sentences(TEST, cap=cap, maxlen=10 ** 6)
    tags = live_tags(test)
    conf = Counter(); tagn = Counter(); taghit = Counter()
    flip_cl = 0; flip_np = 0; pairs = 0; onset_gain = Counter(); opener = Counter()
    for (toks, gp, hg, rels), lp in zip(test, tags):
        for g, l in zip(gp, lp):
            tagn[g] += 1; taghit[g] += int(g == l)
            if g != l:
                conf["%s->%s" % (g, l)] += 1
        nvg, sbg = clause_matrices(toks, gp); nvl, sbl = clause_matrices(toks, lp)
        Vg = npb_matrix(toks, gp); Vl = npb_matrix(toks, lp)
        n = len(toks)
        flip_cl += int(np.sum((nvg != nvl) | (sbg != sbl))); flip_np += int(np.sum(Vg != Vl))
        pairs += (n + 1) * n
        sg = np_starts(toks, gp); sl = np_starts(toks, lp)
        for i in range(1, n + 1):
            if sg[i] != sl[i]:
                onset_gain["%s->%s" % (gp[i - 1], lp[i - 1])] += 1
        pg, og = predicate_flags(toks, gp); pl, ol = predicate_flags(toks, lp)
        for i in range(1, n + 1):
            if og[i] != ol[i]:
                opener["%s->%s" % (gp[i - 1], lp[i - 1])] += 1
            if pg[i] != pl[i]:
                opener["PRED %s->%s" % (gp[i - 1], lp[i - 1])] += 1
    out = {"tag_recall": {t: round(taghit[t] / tagn[t], 4) for t in sorted(tagn) if tagn[t] >= 20},
           "tag_n": dict(tagn), "confusions": dict(conf.most_common(20)),
           "clause_value_flips": flip_cl, "npb_value_flips": flip_np, "pairs": pairs,
           "clause_flip_rate": round(flip_cl / max(1, pairs), 4), "npb_flip_rate": round(flip_np / max(1, pairs), 4),
           "phrase_onset_flips": dict(onset_gain.most_common(12)),
           "clause_marker_flips": dict(opener.most_common(12))}
    print(json.dumps(out, indent=1), flush=True)
    return out


def self_test():
    """Can-fail checks on the mechanism itself (no gold, no scoring)."""
    ok = True

    def chk(name, cond, extra=""):
        nonlocal ok
        print("  %-58s %s %s" % (name, "PASS" if cond else "FAIL", extra), flush=True)
        ok = ok and bool(cond)

    toks = ["I", "gave", "the", "man", "a", "book", "."]
    pos = ["PRON", "VERB", "DET", "NOUN", "DET", "NOUN", "PUNCT"]
    st = np_starts(toks, pos)
    chk("the SECOND determiner opens a second phrase", list(np.flatnonzero(st)) == [5], list(np.flatnonzero(st)))
    t2 = ["all", "the", "people", "left"]; p2 = ["DET", "DET", "NOUN", "VERB"]
    chk("'all the people' stays ONE phrase (no noun before the 2nd DET)",
        list(np.flatnonzero(np_starts(t2, p2))) == [], list(np.flatnonzero(np_starts(t2, p2))))
    chk("'all the people': the whole run is one phrase", split_runs(p2, np_starts(t2, p2)) == [(1, 3)],
        split_runs(p2, np_starts(t2, p2)))
    t3 = ["the", "man", "'s", "book", "fell"]; p3 = ["DET", "NOUN", "PART", "NOUN", "VERB"]
    chk("possessive: 'book' may still head 'man' (npb in, not cross)",
        NPB_VALUES[int(npb_matrix(t3, p3)[4][1])] == "in", NPB_VALUES[int(npb_matrix(t3, p3)[4][1])])
    runs = split_runs(pos, st)
    chk("the DET NOUN DET NOUN run splits into two phrases", runs == [(3, 4), (5, 6)], runs)
    chk("landed npmod absorbs 'man' under 'book'", (6, 4) in AA.npmod_arcs(toks, pos))
    chk("split npmod does NOT absorb 'man' under 'book'", (6, 4) not in npmod_arcs_split(toks, pos))
    V = npb_matrix(toks, pos)
    chk("npb('book' heads 'man') == cross", NPB_VALUES[int(V[6][3])] == "cross")
    chk("npb('man' heads 'the') == in", NPB_VALUES[int(V[4][2])] == "in")

    toks2 = ["I", "need", "to", "send", "stuff", "."]
    pos2 = ["PRON", "VERB", "PART", "VERB", "NOUN", "PUNCT"]
    nv, sb = clause_matrices(toks2, pos2)
    chk("clause('need' heads 'stuff') = 1 predicate + opener", clause_value(int(nv[2][4]), int(sb[2][4])) == "1s",
        clause_value(int(nv[2][4]), int(sb[2][4])))
    chk("clause('send' heads 'stuff') = same clause", clause_value(int(nv[4][4]), int(sb[4][4])) == "0",
        clause_value(int(nv[4][4]), int(sb[4][4])))
    chk("root arc crosses nothing", clause_value(int(nv[0][4]), int(sb[0][4])) == "0")

    # the cue enters the SAME learned machinery: a value that always fires contributes exactly 0
    enable(clause=True, npb=True, split=True)
    c = AA.new_counts()
    chk("new cues are in AA.CUES", "clause" in AA.CUES and "npb" in AA.CUES, AA.CUES)
    chk("new_counts carries a slot for each", "clause" in c["cues"] and "npb" in c["cues"])
    sc = AA.SentenceCues(toks, pos, {}, None)
    d = sc.cues(4, 6)
    chk("SentenceCues exposes the cue values", d.get("npb") == "cross" and "clause" in d, d)
    # accrual + strengths are pure functions of counts (plasticity path)
    marg = {j: {h: (1.0 if h == 2 else 0.0) for h in range(0, len(toks) + 1) if h != j} for j in range(1, len(toks) + 1)}
    AA.accrue_sentence(c, sc, marg)
    s1 = AA.strengths_from_arc_counts(c); s2 = AA.strengths_from_arc_counts(c)
    chk("strengths are a pure function of the counts", s1["clause"] == s2["clause"] and bool(s1["clause"]))
    tab = {"counts": c, "frames": {}, "pp_assoc": None, "strength": s1}
    A1, n1 = AA.arc_scores(toks, pos, tab)
    A2, n2 = AA.arc_scores_reference(toks, pos, tab)
    chk("fast path == reference readout with the new cues", np.allclose(np.nan_to_num(A1, neginf=-1e18),
                                                                       np.nan_to_num(A2, neginf=-1e18), atol=1e-9),
        float(np.nanmax(np.abs(np.nan_to_num(A1, neginf=0) - np.nan_to_num(A2, neginf=0)))))
    # the online observe path still works with the new cues
    AA.observe_arc_outcome(toks, pos, 4, 2, tab)
    chk("observe_arc_outcome accrues the new cue cells", any(k.endswith("|cross") or k.endswith("|in")
                                                             for k in tab["counts"]["cues"]["npb"]))
    # the clause-close wrap-up trigger fires at an opener and nowhere else new
    wp = _wrapup_pos(toks2, pos2)
    chk("wrap-up trigger fires at the clause opener 'to' and not at other words",
        wp[2] == "CCONJ" and [k for k, (a, b) in enumerate(zip(wp, pos2)) if a != b] == [2], wp)
    enable()
    chk("disable restores the landed arm", AA.arc_scores is _ORIG_ARC and AA.npmod_arcs is _ORIG_NPMOD)
    print("self-test:", "GREEN" if ok else "RED", flush=True)
    return ok


# ------------------------------------------------------------------------------------------------------------------
def run(train_cap, test_cap, rounds, arms, live=True, out=None, twin=True, save=False):
    t0 = time.time()
    train = sentences(TRAIN, cap=train_cap)
    test = sentences(TEST, cap=test_cap, maxlen=10 ** 6)
    print("train %d / test %d" % (len(train), len(test)), flush=True)
    enable()
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _, _ in train])
    pp_assoc = AA.pp_assoc_from_reading([(t, p) for t, p, _, _ in train])
    NN_ASSOC["tab"] = nn_assoc_from_reading([(t, p) for t, p, _, _ in train])
    print("noun-noun association: %d adjacent pairs, %d types" % (int(NN_ASSOC["tab"]["tot"]), len(NN_ASSOC["tab"]["pair"])), flush=True)
    teacher = knowledge_free_teacher(train, beta=10.0)
    print("teacher ready %.0fs" % (time.time() - t0), flush=True)
    tags, tpost = live_tags(test, posterior=True) if live else (None, None)
    res = {}; tables = {}
    for name, cfg in arms:
        cfg = dict(cfg); teach = cfg.pop("teach", False)
        enable(**cfg)
        tab = build_table(train, teacher, frames, pp_assoc, rounds=rounds, teach=teach)
        tables[name] = tab
        r = {}
        for dec in ("incr", "map1"):
            enable(**cfg)
            r[dec] = evaluate(tab, test, dec)
            _print("%s / %s" % (name, dec), r[dec])
        if live:
            enable(**cfg)
            r["live_incr"] = evaluate(tab, test, "incr", tags=tags)
            _print("%s / live" % name, r["live_incr"])
            enable(**cfg)
            r["live_graded"] = evaluate(tab, test, "incr", tags=tags, tag_post=tpost)
            _print("%s / live+graded" % name, r["live_graded"])
            enable(**cfg)
            r["labels"] = labels_rung(tab, tags, cap=len(test))
            print("%-22s labels rung (live chain): %s" % (name, r["labels"]["recall"]), flush=True)
        res[name] = r
        if save:
            print("  candidate asset ->", save_candidate(tab, name.replace("+", "_")), flush=True)
        print("  [%s built+scored %.0fs]" % (name, time.time() - t0), flush=True)
    if twin and len(arms) > 1:
        name, cfg = arms[-1]; cfg = {k: v for k, v in cfg.items() if k != "teach"}
        for seed in (11, 23):
            enable(shuffle=True, seed=seed, **cfg)
            r = evaluate(tables[name], test, "incr")
            _print("TWIN(seed %d) / incr" % seed, r)
            res["twin_%d" % seed] = {"incr": r}
        enable()
    return res, time.time() - t0


HOOK = os.path.join(REPO, "data", "hook_state")
ALL_ARMS = {"floor": {}, "both_split": {"clause": True, "npb": True, "split": True},
            "both+split": {"clause": True, "npb": True, "split": True}}


def save_candidate(tab, name):
    os.makedirs(HOOK, exist_ok=True)
    p = os.path.join(HOOK, "attach_pri105_%s.json" % name)
    AA.save_attachment_validities(p, tab)
    return p


def board_noregress(floor_asset, arm_asset, cfg, cap=150):
    """NO-REGRESS: the board's PATIENT and AGENT dimensions, read through the floor asset and through the arm's
    asset, with the arm's cues on.  One run each (the brief allows one board run)."""
    import experiments.exp_board_patient_slot_v1 as PAT
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from hdlab import frontend as FE
    out = {}
    for label, asset, c in (("floor", floor_asset, {}), ("arm", arm_asset, {k: v for k, v in cfg.items() if k != "teach"})):
        enable(**c)
        AA._TABLE = AA.load_attachment_validities(asset)
        FE._P = None; FE._T = None
        rp = PAT.board_patient_dimension(cap=cap); rp = rp[0] if isinstance(rp, tuple) else rp
        ra = AG.board_agent_dimension(cap=cap); ra = ra[0] if isinstance(ra, tuple) else ra
        out[label] = {"patient": rp, "agent": ra}
        print("%-6s patient %.4f (floor %.4f)  agent %.4f (floor %.4f)"
              % (label, rp.get("model_acc", 0), rp.get("strongest_floor", rp.get("overlap_floor", 0)),
                 ra.get("model_acc", 0), ra.get("strongest_floor", ra.get("overlap_floor", 0))), flush=True)
    enable(); AA._TABLE = None; FE._P = None; FE._T = None
    return out


def _deltas(res, floor, arm):
    out = {}
    for dec in res[arm]:
        if dec == "labels":
            a = res[floor]["labels"]; b = res[arm]["labels"]
            out["labels"] = {"floor": a["recall"], "arm": b["recall"], "n": a["n"],
                             "ci": {k: labels_ci(a, b, k) for k in a["_per_sent"]}}
            continue
        a = res[floor][dec]; b = res[arm][dec]
        out[dec] = {"floor_uas": a["uas"], "arm_uas": b["uas"], "uas_ci": uas_ci(a, b),
                    "floor_core": a["core"], "arm_core": b["core"], "core_ci": ci(a, b, "core"),
                    "floor_root": a["root"], "arm_root": b["root"], "root_ci": ci(a, b, "root"),
                    "floor_classes": a["classes"], "arm_classes": b["classes"],
                    "floor_rel": a["rel"], "arm_rel": b["rel"]}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--anatomy", action="store_true"); ap.add_argument("--full", action="store_true")
    ap.add_argument("--upstream", action="store_true")
    ap.add_argument("--ceiling", action="store_true")
    ap.add_argument("--labels-consequence", action="store_true")
    ap.add_argument("--why-absorbed", action="store_true")
    ap.add_argument("--ceiling-which", default="clause,npb,nn,both")
    ap.add_argument("--gammas", default="1,2,4,8,1000")
    ap.add_argument("--save-assets", action="store_true")
    ap.add_argument("--board", default="", help="floor_asset,arm_asset,arm_name -- the board no-regress run")
    ap.add_argument("--board-cap", type=int, default=150)
    ap.add_argument("--train-cap", type=int, default=None); ap.add_argument("--test-cap", type=int, default=None)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--arms", default="floor,clause,npb,both,both+split")
    ap.add_argument("--tag", default="")
    a = ap.parse_args(argv)
    outdir = str(get_output_dir(ANCHOR)); os.makedirs(outdir, exist_ok=True)
    if a.self_test:
        return 0 if self_test() else 1
    if a.board:
        parts = a.board.split(",")
        fl = os.path.join(HOOK, "attach_pri105_%s.json" % parts[0])
        ar = os.path.join(HOOK, "attach_pri105_%s.json" % parts[1])
        cfg = {"clause": True, "npb": True, "split": True} if len(parts) < 3 else ALL_ARMS[parts[2]]
        d = board_noregress(fl, ar, cfg, cap=a.board_cap)
        with open(os.path.join(outdir, "board_noregress.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        return 0
    if a.why_absorbed:
        d = why_absorbed(cap=a.test_cap or 700)
        with open(os.path.join(outdir, "why_absorbed.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        return 0
    if a.labels_consequence:
        d = labels_consequence(cap=a.test_cap or 700)
        with open(os.path.join(outdir, "labels_consequence.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        return 0
    if a.ceiling:
        d = ceiling(cap=a.test_cap or 700, gammas=tuple(float(x) for x in a.gammas.split(",")),
                    which_list=tuple(a.ceiling_which.split(",")))
        with open(os.path.join(outdir, "ceiling.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        return 0
    if a.upstream:
        d = upstream(cap=a.test_cap or 700)
        with open(os.path.join(outdir, "upstream_trace.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        return 0
    if a.anatomy:
        d = anatomy(cap=a.test_cap or 700)
        with open(os.path.join(outdir, "anatomy.json"), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        print("wrote", os.path.join(outdir, "anatomy.json"), flush=True)
        return 0
    ALL = {"floor": {}, "clause": {"clause": True}, "npb": {"npb": True}, "split": {"split": True},
           "npb+split": {"npb": True, "split": True},
           "both": {"clause": True, "npb": True}, "both+split": {"clause": True, "npb": True, "split": True},
           "clause+split": {"clause": True, "split": True},
           "clause+fn": {"clause": True, "functional": True},
           "npb+pron": {"npb": True, "pron_dp": True},
           "all": {"clause": True, "npb": True, "split": True, "functional": True, "pron_dp": True},
           "all-fn": {"clause": True, "npb": True, "split": True, "pron_dp": True},
           "all-pron": {"clause": True, "npb": True, "split": True, "functional": True},
           "teach": {"teach": True},
           "both+split+teach": {"clause": True, "npb": True, "split": True, "teach": True},
           "all+teach": {"clause": True, "npb": True, "split": True, "pron_dp": True, "teach": True},
           "wrapup": {"wrapup": True}, "both+split+wrapup": {"clause": True, "npb": True, "split": True, "wrapup": True},
           "nn": {"nn": True}, "clause+nn": {"clause": True, "nn": True},
           "all3": {"clause": True, "npb": True, "nn": True, "split": True},
           "all3+wrapup": {"clause": True, "npb": True, "nn": True, "split": True, "wrapup": True}}
    arms = [(k, ALL[k]) for k in a.arms.split(",") if k in ALL]
    train_cap = a.train_cap or (1500 if a.smoke else 6000)
    test_cap = a.test_cap or (300 if a.smoke else 700)
    res, secs = run(train_cap, test_cap, a.rounds, arms, live=not a.smoke, save=a.save_assets)
    doc = {"anchor": ANCHOR, "train_cap": train_cap, "test_cap": test_cap, "rounds": a.rounds,
           "arms": [k for k, _ in arms], "elapsed_s": round(secs, 1),
           "results": {k: {d: ({"recall": v["recall"], "n": v["n"]} if d == "labels"
                                else {kk: v[kk] for kk in ("uas", "core", "core_n", "root", "rel", "classes")})
                           for d, v in r.items()} for k, r in res.items()},
           "deltas": {k: _deltas(res, arms[0][0], k) for k, _ in arms[1:] if k in res}}
    name = "metrics%s.json" % (("_" + a.tag) if a.tag else ("_smoke" if a.smoke else ""))
    with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("wrote", os.path.join(outdir, name), flush=True)
    for k in doc["deltas"]:
        for dec, d in doc["deltas"][k].items():
            if dec == "labels":
                for kk, v in d["ci"].items():
                    print("%-12s labels %-16s %.4f -> %.4f  %+.4f CI[%+.4f,%+.4f] (n=%d)"
                          % (k, kk, d["floor"].get(kk, 0), d["arm"].get(kk, 0), v[0], v[1], v[2], d["n"].get(kk, 0)),
                          flush=True)
                continue
            print("%-12s %-10s core %.4f -> %.4f  delta %+.4f CI[%+.4f,%+.4f] | UAS %.4f -> %.4f %+.4f CI[%+.4f,%+.4f]"
                  % (k, dec, d["floor_core"], d["arm_core"], d["core_ci"][0], d["core_ci"][1], d["core_ci"][2],
                     d["floor_uas"], d["arm_uas"], d["uas_ci"][0], d["uas_ci"][1], d["uas_ci"][2]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
