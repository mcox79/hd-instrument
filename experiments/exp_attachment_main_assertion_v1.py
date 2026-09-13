"""THE MAIN ASSERTION: root cues for the attachment arm of the Competition-Model organ (problem pri-97,
`the_main_assertion_is_a_scorer_deficit_the_governor_rates_non_verbal_predicates_and_subordinate_first_clauses_as_non_roots`).

THE BRAIN'S MECHANISM (the opening move).  Which word carries the main assertion is decided by the SAME cue competition
that decides every other attachment (Bates & MacWhinney 1989 Competition Model; MacDonald-Pearlmutter-Seidenberg 1994
constraint satisfaction) -- a competition among the sentence's candidate PREDICATES, with cues whose validities are
LEARNED.  The cues a reader has (all PINNED as acquisition facts, all readable off form + position, none from a treebank):
  (1) FINITENESS.  The asserted proposition is the TENSED one; tense/agreement morphology is what marks it.  Children's
      root-infinitive stage (Wexler 1994; Rizzi 1993 "root infinitives") is precisely the emergence of this cue: a
      to-infinitive or a bare participle cannot carry the main assertion, a tensed or auxiliary-supported verb can.
      Read off the visual word form by morphological decomposition (Rastle & Davis 2008; Taft 1979 -- our
      `hdlab.morphology` organ) plus the auxiliary frame (Mintz 2003 frequent frames).
  (2) COPULAR PREDICATION.  "the vote is confusing" asserts CONFUSING; the copula is the tense carrier, the non-verbal
      predicate is the assertion (Pustet 2003; the UD convention the consumers read agrees).  Detected by the frame the
      arm already has (`function_word_arcs`: a copula with no following lexical verb + the predicate head after it).
  (3) SUBORDINATION MARKING.  A clause opened by a subordinator or a relativizer is DEPENDENT -- its verb is not the
      root ("When I arrived, she LEFT").  Complementizers are the acquisition cue for clause dependency (Diessel 2004).
  (4) MAIN-CLAUSE POSITION / SUBJECT SUPPORT.  English asserts matrix-first, and a canonical predicate has a nominal
      to its left with no predicate in between.  (Competition-Model word-order cue.)
The OPERATION is copied (categorical cue values -> log-odds contrast within the ROOT configuration -> additive
activation); every NUMBER (which value, how much) is LEARNED from the teacher posterior or SWEPT.

THE DEFICIT THIS FIXES, measured on disk before building anything (`scratch` anatomy, reproduced by --anatomy):
  * `SentenceCues.cues(j, h)` returns `{}` when h == 0.  The ENTIRE root signal in the live asset is 17 numbers --
    one per category (ROOT:VERB +2.192, ROOT:NOUN +1.208, ROOT:ADJ -1.336, ...).  Every VERB in a sentence therefore
    has the IDENTICAL root activation: 378 of 700 test sentences (54%) have two or more candidates TIED at the best
    root score, so the root decision is settled by tie-breaking, not by evidence.
  * ORACLE-CEILING probe (add +20 to the gold root arc, change nothing else): root 0.721 -> 0.943 and UAS 0.6125 ->
    0.6574 under the in-order decode.  The headroom behind the root row alone is ~4.5 UAS points.
  * UPSTREAM (the wall is not here): the ACQUISITION TEACHER is blind to non-verbal predication.  Posterior mass on
    the gold root arc by gold-root category (n=400 test sentences, teacher trained on 1.5k train sentences):
    VERB 0.358, NOUN 0.404, PROPN 0.260, but **ADJ 0.001 (100% below 0.05), ADV 0.000, PRON 0.000**.  The teacher's
    root row is `beta * (best subject fit + best object fit)` for a VERB and a flat -1.5 for everything else, so a
    copular predicate can never out-root a verb -- the `cop` cue would have had nothing to learn from.  Same shape as
    the coordination win (pri-95): the read-time mechanism was missing AND its teacher was blind.

WHAT IS BUILT (both halves treebank-free, both plastic -- knowledge lives in the counts):
  A. READ TIME -- three cue families on the ROOT configuration, accrued and read like every other cue:
       `rpred`  finiteness class of a verbal candidate ("to" / "auxbe" / "auxhave" / "auxmod" / "ing" / "ed" / "s" /
                "base"), or predication status of a non-verbal candidate ("cop" / "nov" = no verb in the sentence at
                all, a legitimate fragment root / "hasv").
       `rsub`   the clause-dependency marking in force at this candidate ("sconj" / "wh" / "cc" / "none").
       `rpos`   rank among the sentence's assertion candidates ("1" / "2" / "3+") x whether a nominal sits to its left
                with no predicate in between ("S").
  B. ACQUISITION -- `predication_boost`, the teacher's missing half (the exact analogue of `parallelism_boost`):
       the copular predicate's root arc is boosted, a subordinate-marked or non-finite predicate's root arc is
       penalised, in the teacher's score matrix only.  Derived from categories + the copula word list + morphology;
       no tree is ever read.  gammas SWEPT.

Run: python experiments/exp_attachment_main_assertion_v1.py [--self-test] [--anatomy] [--sweep] [--smoke] [--full]
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
from collections import Counter, defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from experiments._seed_checkpoint import get_output_dir
import hdlab.attachment_arm as AA
from hdlab.graded_parser import single_root_marginals
from hdlab.thematic_role_labeler import lemma_verb
from tools.build_attachment_validities import sentences, TRAIN, TEST, knowledge_free_teacher

ANCHOR = "attachment_main_assertion_v1"
RELS = ("root", "nsubj", "obj", "obl", "nmod", "ccomp", "xcomp", "advcl", "conj", "amod", "det", "case", "punct")

# ------------------------------------------------------------------------------------------------ the cue machinery
ROOT_CUES = ("rpred", "rsub", "rpos")
CONJ_RPRED = {"on": False}

COP = {"be", "is", "are", "was", "were", "been", "being", "am", "become", "became", "becomes", "seem", "seems",
       "seemed", "'m", "'s", "'re", "s", "m", "re"}                      # the arm's own copula list (function_word_arcs)
AUX_BE = {"be", "is", "are", "was", "were", "been", "being", "am", "'m", "'s", "'re", "m", "re", "s"}
AUX_HAVE = {"have", "has", "had", "'ve", "'d", "ve", "d", "having"}
AUX_MOD = {"will", "would", "can", "could", "may", "might", "shall", "should", "must", "do", "does", "did", "done",
           "'ll", "ll", "wo", "ca", "need", "dare", "ought", "let"}
WH = {"who", "whom", "whose", "which", "that", "what", "where", "when", "why", "how", "whatever", "whoever", "whenever"}
SENT_END = {".", "!", "?", ";"}
_NOMINAL = ("NOUN", "PRON", "PROPN", "NUM")


def _finiteness(toks, pos, i):
    """Morphological + auxiliary-frame finiteness class of the verbal candidate at 1-based i.  Form only: the token vs
    its lemma (the morphology organ's decomposition) and the closest preceding auxiliary/infinitival marker."""
    lows = [t.lower() for t in toks]
    k = i - 1                                            # scan left over adverbs / negation for the marker
    while k >= 1 and (pos[k - 1] == "ADV" or lows[k - 1] in ("not", "n't", "never", "also", "just", "really")):
        k -= 1
    if k >= 1:
        if pos[k - 1] == "PART" and lows[k - 1] == "to":
            return "to"
        if pos[k - 1] == "AUX":
            w = lows[k - 1]
            if w in AUX_HAVE:
                return "auxhave"
            if w in AUX_BE:
                return "auxbe"
            return "auxmod"
        if pos[k - 1] == "VERB" and lows[k - 1] in AUX_MOD:
            return "auxmod"
    w = lows[i - 1]; lem = lemma_verb(toks[i - 1]).lower()
    if w.endswith("ing") and w != lem:
        return "ing"
    if w == lem:
        return "base"
    if w.endswith("s") and not w.endswith("ss"):
        return "s"
    return "ed"


COPFIX = {"on": False}


def _cop_predicates_fixed(toks, pos):
    """CORRECTED copular detection (LEVER 4a; found while building the subject cue, and it is the ROOT CAUSE of the
    dominant copular-subject miss). `function_word_arcs` binds an AUX to `next_verb`, which scans right and stops
    only at PUNCT -- so in "we ARE capable of PROTECTING it" the copula binds to `protecting`, a verb sitting behind
    a PREPOSITION inside the predicate phrase, and the copular reading NEVER FIRES AT ALL. An auxiliary marks the
    tense of ITS OWN clause; a verb behind a preposition, a subordinator or infinitival `to` is in an embedded
    phrase, not the auxiliary's verb group -- the same locality every other cue in this organ respects. So the scan
    stops at ADP / SCONJ / PART-`to` / CCONJ as well as PUNCT."""
    n = len(pos); lows = [t.lower() for t in toks]; out = set()
    for i in range(n):
        if pos[i] != "AUX" or lows[i] not in COP:
            continue
        v = None
        for k in range(i + 1, n):
            if pos[k] == "VERB":
                v = k; break
            if pos[k] in ("PUNCT", "ADP", "SCONJ", "CCONJ") or (pos[k] == "PART" and lows[k] == "to"):
                break
        if v is not None:
            continue
        for k in range(i + 1, n):
            if pos[k] in ("VERB", "PUNCT"):
                break
            if pos[k] in ("ADJ", "NOUN", "PROPN", "PRON", "NUM"):
                if pos[k] == "PRON":
                    out.add(k + 1); break
                j = k
                while j + 1 < n and pos[j + 1] in AA.NP_RUN:
                    j += 1
                heads = [m for m in range(k, j + 1) if pos[m] in ("NOUN", "PROPN")]
                if heads:
                    out.add(heads[-1] + 1); break
                adjs = [m for m in range(k, j + 1) if pos[m] in ("ADJ", "NUM")]
                out.add((adjs[-1] if adjs else k) + 1); break
    return out


def _cop_predicates(toks, pos):
    """1-based indices that the arm's OWN copular frame makes the predicate of a copula (no lexical verb after it)."""
    if COPFIX["on"]:
        return _cop_predicates_fixed(toks, pos)
    out = set()
    try:
        for (h, d) in AA.function_word_arcs(list(toks), list(pos)):
            if 1 <= d <= len(pos) and 1 <= h <= len(pos) and pos[d - 1] == "AUX" and toks[d - 1].lower() in COP \
                    and pos[h - 1] != "VERB" and d < h:
                out.add(h)
    except Exception:
        pass
    return out


def _subord(toks, pos, i):
    """The clause-dependency marking in force at 1-based i: the nearest preceding clause opener with no finite
    predicate in between (a VERB closes the search; a sentence-final mark closes it)."""
    lows = [t.lower() for t in toks]
    for k in range(i - 1, 0, -1):
        p = pos[k - 1]; w = lows[k - 1]
        if p == "VERB":
            return "none"
        if p == "PUNCT" and w in SENT_END:
            return "none"
        if p == "SCONJ":
            return "sconj"
        if p in ("PRON", "DET", "ADV") and w in WH:
            return "wh"
        if p == "CCONJ":
            return "cc"
    return "none"


# ---- the FOURTH cue (quality push): ARGUMENT SUPPORT on the root row -------------------------------------------------
# The Competition Model's semantic-plausibility cue already exists at read time for ordinary verb->nominal arcs
# (`plaus`), and the acquisition teacher already scores a verb's ROOT arc by beta*(best subject fit + best object fit)
# -- but the ARM's root row never saw it.  A predicate whose participants fit their roles IS the asserted event
# (Pinker 1984 semantic bootstrapping; MacDonald 1994 constraint satisfaction).  Value = binned (best subject fit +
# best object fit) using the SAME self-grown typed store the arm already reads; bins swept, never adopted.
_ARG_T = {"t": None}


def _arg_teacher():
    if _ARG_T["t"] is None:
        _ARG_T["t"] = AA.SemanticBootstrapTeacher()
    return _ARG_T["t"]


def _arg_bin(x):
    return "0" if x <= 0.0 else "lo" if x < 0.05 else "mid" if x < 0.2 else "hi"


def _arg_support(toks, pos, j, cop):
    """Best subject fit + best object fit of the candidate predicate at 1-based j (0 for a non-predicate)."""
    n = len(pos)
    if pos[j - 1] != "VERB":
        return 0.0
    t = _arg_teacher(); bs = bo = 0.0
    for k in range(1, n + 1):
        if k == j or pos[k - 1] not in _NOMINAL or (k >= 2 and pos[k - 2] == "ADP"):
            continue
        p = t.slot_plausibility(list(toks), list(pos), j, k)
        if k < j:
            bs = max(bs, p)
        else:
            bo = max(bo, p)
    return bs + bo


def root_cue_values(toks, pos):
    """Per 1-based token: the ROOT-configuration cue values (index 0 unused).  Tokens + categories only."""
    n = len(pos); cop = _cop_predicates(toks, pos)
    has_verb = any(p == "VERB" for p in pos)
    cand = [j for j in range(1, n + 1) if pos[j - 1] == "VERB" or j in cop
            or (pos[j - 1] == "AUX" and not has_verb)]
    if not cand:
        # A VERBLESS, COPULA-LESS utterance still asserts -- its assertion is carried by the head of its phrase
        # (a headline, a list item, a signature, a price: "Great prices on shoes!").  Measured residual before this
        # rule: 47 of 169 remaining root misses were exactly these, and the rank cue was PENALISING them for not
        # being candidates at all.  Candidates = the content heads (a nominal run's last NOUN/PROPN, else any
        # content word), so the rank cue's competition is over the right set.
        heads = [j for j in range(1, n + 1)
                 if pos[j - 1] in ("NOUN", "PROPN") and (j == n or pos[j] not in ("NOUN", "PROPN"))]
        cand = heads or [j for j in range(1, n + 1) if pos[j - 1] in AA.CONTENT or pos[j - 1] == "INTJ"]
    rank = {j: (1 if k == 0 else 2 if k == 1 else 3) for k, j in enumerate(cand)}
    last_cand = cand[-1] if cand else None
    out = [None] * (n + 1)
    for j in range(1, n + 1):
        p = pos[j - 1]
        if p in ("VERB", "AUX"):
            rpred = _finiteness(toks, pos, j)
        elif j in cop:
            rpred = "cop"
        else:
            rpred = "hasv" if has_verb else "nov"
        # a nominal to the left with no predicate in between = the canonical subject-predicate configuration
        subj = False
        for k in range(j - 1, 0, -1):
            if pos[k - 1] in ("VERB",):
                break
            if pos[k - 1] in _NOMINAL:
                subj = True; break
        # CONJUNCTIVE FINITENESS (the fix the rung-3 trace exposed): a BARE "ed" form conflates VerbForm=Fin (148 of
        # 967 test VERB tokens) with a bare VerbForm=Part (65) -- past tense vs a reduced relative -- and a bare
        # "base" form conflates Fin (146) with Inf (46). Same cue value, OPPOSITE predication status: a conflated
        # value handing a point estimate down. The disambiguator the reader has is subject support (a nominal to the
        # left with no predicate in between): "the man WALKED" (finite) vs "the man SEEN yesterday" (participle).
        # The additive form cannot represent that interaction, so the ambiguous classes take a CONJUNCTIVE value.
        if CONJ_RPRED["on"] and rpred in ("ed", "base"):
            # RANK, not subject support. "the man SEEN yesterday LEFT" and "the man WALKED home" BOTH have a nominal
            # to the left with no intervening predicate, so the S flag cannot separate them (verified on the worked
            # example before spending a build). What separates them is whether ANOTHER finite predicate later in the
            # clause already claims that nominal -- i.e. RANK plus whether a LATER candidate exists at all. Rank
            # alone also fails ("seen" is rank 1 in "the man SEEN yesterday LEFT", exactly like "walked" in "the man
            # WALKED home"); what separates them is that "seen" is NOT the last candidate and "walked" is.
            rpred = rpred + ("%d" % (rank.get(j) or 0)) + ("L" if j == last_cand else "x")
        r = rank.get(j)
        rpos = ("%d" % r if r else "x") + ("S" if subj else "")
        d = {"rpred": rpred, "rsub": _subord(toks, pos, j), "rpos": rpos}
        if "rarg" in ROOT_CUES:
            d["rarg"] = _arg_bin(_arg_support(toks, pos, j, cop))
        out[j] = {k: v for k, v in d.items() if k in ROOT_CUES}
    return out


# ------------------------------------------------------------------------------------------ the acquisition teacher
def predication_boost(A, toks, pos, g_cop=8.0, g_sub=8.0, g_fin=8.0):
    """THE TEACHER'S MISSING HALF (the analogue of `parallelism_boost`).  The acquisition teacher's root row is
    beta*(subject fit + object fit) for a VERB and a flat -1.5 for everything else, so it puts 0.001 posterior mass on
    an adjectival predicate's root arc (measured).  Predication + dependency marking, both treebank-free:
      * a copular predicate (a copula with no lexical verb after it) CARRIES the assertion -> boost its root arc;
      * a predicate whose clause is opened by a subordinator / relativizer is DEPENDENT -> penalise its root arc;
      * a to-infinitival or bare participial verb is NOT finite -> penalise its root arc.
    gammas are a swept operating point, never adopted."""
    n = len(pos); B = A.copy(); cop = _cop_predicates(toks, pos)   # independent of which cues are switched on
    for j in range(1, n + 1):
        if not np.isfinite(B[0][j]):
            continue
        d = 0.0
        rpred = _finiteness(toks, pos, j) if pos[j - 1] in ("VERB", "AUX") else ("cop" if j in cop else "")
        if rpred == "cop":
            d += g_cop
        if _subord(toks, pos, j) in ("sconj", "wh"):
            d -= g_sub
        if rpred in ("to", "ing"):
            d -= g_fin
        B[0][j] += d
    return B


# ------------------------------------------------------ LEVER 2: the clausal construction must know WHICH clause hangs
# `clausal_arcs` proposes, for every non-initial VERB, an arc from the NEAREST PRECEDING VERB to it -- always in that
# direction.  That is the wrong half of the subordination fact: a subordinator marks WHICH clause is dependent, so in
# "When I ARRIVED, she LEFT" the dependency runs LEFT -> ARRIVED, not the other way.  The construction as built
# therefore proposes the exact reverse of the gold arc in every subordinate-FIRST sentence, and the learned `constr`
# validity rewards it -- which is how the subordinate clause's verb ends up crowned and advcl sits at 0.32.
# Brain-foundational: the complementizer is the acquisition cue for clause dependency AND for its direction (Diessel
# 2004); the reversed proposal is a SEPARATE construction family so its validity is learned separately, never assumed.
def _clausal_pairs(pos):
    out = []; prev = None
    for i in range(len(pos)):
        if pos[i] == "VERB":
            if prev is not None and not (i > 0 and pos[i - 1] == "CCONJ"):
                out.append((prev + 1, i + 1))
            prev = i
    return out


def _reversed_pair(toks, pos, a, b):
    return _subord(toks, pos, a) in ("sconj", "wh") and _subord(toks, pos, b) == "none"


def clausal_arcs_fwd(toks, pos):
    return [(a, b) for a, b in _clausal_pairs(pos) if not _reversed_pair(toks, pos, a, b)]


def clausal_arcs_rev(toks, pos):
    """The subordinate-first case: the MATRIX verb heads the subordinate verb (advcl / csubj direction)."""
    return [(b, a) for a, b in _clausal_pairs(pos) if _reversed_pair(toks, pos, a, b)]


_ORIG_CONSTRUCTIONS = dict(AA.CONSTRUCTIONS)


def enable_clausal_direction(on=True):
    if on:
        AA.CONSTRUCTIONS = dict(_ORIG_CONSTRUCTIONS, clausal=clausal_arcs_fwd, clausalrev=clausal_arcs_rev)
    else:
        AA.CONSTRUCTIONS = dict(_ORIG_CONSTRUCTIONS)



# ---- LEVER 4: the COPULAR SUBJECT is an nsubj-ARC cue, not a root cue ------------------------------------------
# Strategy's slice: of 161 gold nsubj whose head is a NON-VERBAL predicate the live governor gets 0.460, and the
# DOMINANT miss (49 of 161) is the subject pulled to a LATER VERB inside the predicate's own clause ("we [are
# capable of] protecting" -> protecting). The root cue moves the "crowned as ROOT" mode (20 -> 18) and leaves this
# one untouched (49 -> 47), because it is a competition on the SUBJECT arc, not on the root arc. Brain-foundational
# form: with a copula and no lexical verb the predicate is the clause's predication and takes its subject (Pustet
# 2003); a verb further right is inside the predicate phrase and is NOT competing for that nominal. Categorical cue
# values, validity LEARNED like every other cue -- nothing is hand-weighted.
CSUB = {"on": False}


def csub_sites(toks, pos):
    """(head, dependent) -> cue value, for the copular-subject competition. Categories + the copula list only."""
    n = len(pos); cop = _cop_predicates(toks, pos); out = {}
    for q in sorted(cop):
        c = None                                   # the copula that licenses q
        for k in range(q - 1, 0, -1):
            if pos[k - 1] == "AUX" and toks[k - 1].lower() in COP:
                c = k; break
            if pos[k - 1] == "VERB":
                break
        if c is None:
            continue
        subj = None                                # the nearest nominal head before the copula, skipping PP objects
        k = c - 1
        while k >= 1:
            if pos[k - 1] in _NOMINAL:
                a = k
                while a - 1 >= 1 and pos[a - 2] in AA.NP_RUN:
                    a -= 1
                if a - 1 >= 1 and pos[a - 2] == "ADP":
                    k = a - 2; continue
                subj = k; break
            if pos[k - 1] in ("VERB", "SCONJ", "CCONJ"):
                break
            k -= 1
        if subj is None:
            continue
        out[(q, subj)] = "pred"                    # the predicate claiming its own subject
        for v in range(q + 1, n + 1):              # any verb to the RIGHT is inside the predicate phrase
            if pos[v - 1] == "VERB":
                out.setdefault((v, subj), "later")
    return out

# --------------------------------------------------------------------------------------------------- the arm patch
_ORIG_CUES = AA.SentenceCues.cues
_ORIG_ARC = AA.arc_scores
_ORIG_CUE_TUPLE = AA.CUES
_SHUFFLE = {"on": False, "rng": None}


def _patched_cues(self, j, h):
    if h == 0:
        rv = getattr(self, "_root_cue_values", None)
        if rv is None:
            rv = root_cue_values(self.toks, self.pos); self._root_cue_values = rv
        return rv[j]
    d = _ORIG_CUES(self, j, h)
    if CSUB["on"]:
        sites = getattr(self, "_csub_sites", None)
        if sites is None:
            sites = self._csub_sites = csub_sites(self.toks, self.pos)
        v = sites.get((h, j))
        if v is not None:
            d = dict(d); d["csub"] = v
    return d


# THE ROOT SLOT HAS CAPACITY ONE, so the cue evidence must be read as a COMPETITION among the sentence's candidates,
# not as an absolute bonus per word.  Measured (smoke, 300 test sentences): the uncentred form lifts the in-order
# decode (root +0.050 CI-sep) and BREAKS the whole-sentence search (root -0.047 CI-sep), because raising the whole
# root row also raises root-vs-attach for every word, and the search decode weighs that globally.  Centring the
# cue contribution to zero mean over the finite root candidates keeps the root-vs-attach balance the decode was
# calibrated on and lets the cues do only what they are evidence about: WHICH candidate wins the one root slot.
# (Competition Model: cue strengths decide the winner of a competition for a slot -- MacWhinney 1987 "the
# competition is for a single slot"; the arm already states the same principle for the object slot, OCCUPANCY.)
CENTER = {"on": True}


def _patched_arc_scores(toks, pos, table=None):
    A, n = _ORIG_ARC(toks, pos, table)
    tab = table or AA.load_attachment_validities(); st = tab["strength"]
    rv = root_cue_values(toks, pos)
    if _SHUFFLE["on"]:                                  # INFORMATION-FREE TWIN: same cues, values permuted across tokens
        idx = list(range(1, n + 1)); _SHUFFLE["rng"].shuffle(idx)
        rv = [None] + [rv[k] for k in idx]
    d = np.zeros(n + 1); live = []
    for j in range(1, n + 1):
        if not np.isfinite(A[0][j]):
            continue
        cfg = "ROOT:" + pos[j - 1]; sc = 0.0
        for c, v in rv[j].items():
            sc += st.get(c, {}).get(cfg + "|" + v, 0.0)
        d[j] = sc; live.append(j)
    if CSUB["on"]:
        T = st.get("csub", {})
        for (h, jj), v in csub_sites(toks, pos).items():
            if 1 <= h <= n and 1 <= jj <= n and np.isfinite(A[h][jj]):
                A[h][jj] += T.get("%s>%s:%s|%s" % (pos[h - 1], pos[jj - 1], "L" if h < jj else "R", v), 0.0)
    if live:
        if CENTER["on"]:
            d[live] -= float(np.mean(d[live]))
        for j in live:
            A[0][j] += d[j]
    return A, n


def enable_root_cues(on=True):
    if on:
        AA.CUES = tuple(_ORIG_CUE_TUPLE) + ROOT_CUES + (("csub",) if CSUB["on"] else ())
        AA.SentenceCues.cues = _patched_cues
        AA.arc_scores = _patched_arc_scores
    else:
        AA.CUES = _ORIG_CUE_TUPLE
        AA.SentenceCues.cues = _ORIG_CUES
        AA.arc_scores = _ORIG_ARC
    AA._TABLE = None


# ----------------------------------------------------------------------------------------------------------- build
def build_table(train, cues_on, teach, gammas=(8.0, 8.0, 8.0), rounds=3, alpha=0.8, beta=10.0, teacher=None,
                clausal=False):
    """One asset build: the landed pipeline with the root cues on/off and the predication teaching signal on/off."""
    enable_root_cues(cues_on); enable_clausal_direction(clausal)
    frames = AA.verb_frames_from_reading([(t, p) for t, p, _, _ in train])
    pp_assoc = AA.pp_assoc_from_reading([(t, p) for t, p, _, _ in train])
    teacher = teacher or knowledge_free_teacher(train, beta=beta)
    tmarg = {}; counts = AA.new_counts()
    for i, (toks, pos, _, _) in enumerate(train):
        A, n = teacher._score_matrix(toks, pos)
        A = AA.parallelism_boost(A, toks, pos)
        if teach:
            A = predication_boost(A, toks, pos, *gammas)
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


# ------------------------------------------------------------------------------------------------------ evaluation
def evaluate(table, test, decode, cues_on, clausal=False):
    """Per-sentence hits so a PAIRED bootstrap over sentences is possible; UAS + per-relation recall."""
    enable_root_cues(cues_on); enable_clausal_direction(clausal)
    AA.DECODE = decode
    per_sent = []; rt = Counter(); rk = Counter(); tot = ok = 0
    root_hit = []; root_n = []; cop_hit = []; cop_n = []
    for toks, pos, hg, rels in test:
        A, n = AA.arc_scores(toks, pos, table)
        hd, _ = AA.decode(toks, pos, A, n)
        s_ok = 0; s_tot = 0; r_ok = 0; r_tot = 0; c_ok = 0; c_tot = 0
        for i, (g, r) in enumerate(zip(hg, rels), start=1):
            hit = int(hd.get(i, -1) == g); s_ok += hit; s_tot += 1
            if r in RELS:
                rt[r] += 1; rk[r] += hit
            if r == "root":
                r_ok += hit; r_tot += 1
            # COPULAR-SUBJECT ATTACHMENT (strategy's measured evidence, 2026-09-13): a gold nsubj whose gold HEAD is a
            # NON-VERBAL predicate -- the same copular-predication fact the root cue is about, read from the subject
            # side.  Live governor 0.460 over 161 such arcs; the predicate must take BOTH the root and the subject
            # against a later verb's pull, so this is the second number the cue has to move.
            if r == "nsubj" and 1 <= g <= len(pos) and pos[g - 1] not in ("VERB", "AUX"):
                c_ok += hit; c_tot += 1
        tot += s_tot; ok += s_ok
        per_sent.append((s_ok, s_tot)); root_hit.append(r_ok); root_n.append(r_tot)
        cop_hit.append(c_ok); cop_n.append(c_tot)
    return {"uas": ok / max(1, tot), "tokens": tot, "n_sent": len(test),
            "rel": {r: round(rk[r] / max(1, rt[r]), 4) for r in RELS if rt[r]},
            "rel_n": {r: rt[r] for r in RELS if rt[r]},
            "cop_nsubj": round(sum(cop_hit) / max(1, sum(cop_n)), 4), "cop_nsubj_n": sum(cop_n),
            "_per_sent": per_sent, "_root_hit": root_hit, "_root_n": root_n,
            "_cop_hit": cop_hit, "_cop_n": cop_n}


def paired_ci(a_hit, a_n, b_hit, b_n, iters=4000, seed=17):
    """Paired bootstrap over SENTENCES of the recall difference (b - a); returns (delta, lo, hi, halfwidth)."""
    rng = random.Random(seed); m = len(a_hit); idx = list(range(m))
    A = sum(a_hit) / max(1, sum(a_n)); B = sum(b_hit) / max(1, sum(b_n))
    ds = []
    for _ in range(iters):
        s = [rng.randrange(m) for _ in range(m)]
        an = sum(a_n[i] for i in s) or 1; bn = sum(b_n[i] for i in s) or 1
        ds.append(sum(b_hit[i] for i in s) / bn - sum(a_hit[i] for i in s) / an)
    ds.sort(); lo = ds[int(0.025 * iters)]; hi = ds[int(0.975 * iters)]
    return round(B - A, 4), round(lo, 4), round(hi, 4), round((hi - lo) / 2, 4)


def uas_ci(a, b, iters=4000, seed=17):
    ah = [x[0] for x in a["_per_sent"]]; an = [x[1] for x in a["_per_sent"]]
    bh = [x[0] for x in b["_per_sent"]]; bn = [x[1] for x in b["_per_sent"]]
    return paired_ci(ah, an, bh, bn, iters, seed)


def rel_hits(res, test, rel):
    """Per-sentence (hits, n) for one relation -- recomputed from the stored per-sentence data is not possible, so the
    evaluation stores root explicitly; other relations use the aggregate only."""
    raise NotImplementedError


# ---------------------------------------------------------------------------------------------------------- report
def live_chain(table, cues_on, clausal, test_cap=700):
    """The LIVE-chain number: the same asset read under the CATEGORY ORGAN's own tags instead of gold categories."""
    import hdlab.lexical_categories as LC
    enable_root_cues(cues_on); enable_clausal_direction(clausal)
    lc = LC.get(); test = sentences(TEST, cap=test_cap, maxlen=10 ** 6)
    out = {}
    for dec in ("incr", "map1"):
        AA.DECODE = dec
        rt = Counter(); rk = Counter(); tot = ok = 0
        for toks, gold_pos, hg, rels in test:
            tags = lc.tag(list(toks))
            A, n = AA.arc_scores(toks, tags, table)
            hd, _ = AA.decode(toks, tags, A, n)
            for i, (g, r) in enumerate(zip(hg, rels), start=1):
                tot += 1; hit = hd.get(i, -1) == g; ok += hit
                if r in RELS:
                    rt[r] += 1; rk[r] += hit
        out[dec] = {"uas": round(ok / max(1, tot), 4),
                    "rel": {r: round(rk[r] / max(1, rt[r]), 3) for r in RELS if rt[r]}}
    return out


def summarise(name, r):
    return {"arm": name, "uas": round(r["uas"], 4), "rel": r["rel"], "cop_nsubj": r.get("cop_nsubj"),
            "cop_nsubj_n": r.get("cop_nsubj_n")}


def _print(name, r):
    print("%-16s UAS %.4f  root %.3f copsubj %.3f nsubj %.3f ccomp %.3f advcl %.3f xcomp %.3f obj %.3f conj %.3f nmod %.3f obl %.3f"
          % (name, r["uas"], r["rel"].get("root", 0), r.get("cop_nsubj", 0), r["rel"].get("nsubj", 0), r["rel"].get("ccomp", 0),
             r["rel"].get("advcl", 0), r["rel"].get("xcomp", 0), r["rel"].get("obj", 0), r["rel"].get("conj", 0),
             r["rel"].get("nmod", 0), r["rel"].get("obl", 0)), flush=True)


# ------------------------------------------------------------------------------------------------------- self-test
def self_test():
    ok = True

    def chk(cond, msg):
        nonlocal ok
        print(("  PASS  " if cond else "  FAIL  ") + msg, flush=True)
        ok = ok and bool(cond)

    toks = ["When", "I", "arrived", ",", "the", "vote", "is", "a", "little", "confusing", "."]
    pos = ["SCONJ", "PRON", "VERB", "PUNCT", "DET", "NOUN", "AUX", "DET", "ADV", "ADJ", "PUNCT"]
    rv = root_cue_values(toks, pos)
    chk(rv[3]["rsub"] == "sconj", "the verb of a 'When ...' clause is marked subordinate (got %s)" % rv[3]["rsub"])
    chk(rv[10]["rpred"] == "cop", "the adjective after the copula is the copular predicate (got %s)" % rv[10]["rpred"])
    chk(rv[6]["rpred"] == "hasv", "a plain noun in a sentence with a verb is 'hasv' (got %s)" % rv[6]["rpred"])

    t2 = ["I", "want", "to", "go", "home", "."]; p2 = ["PRON", "VERB", "PART", "VERB", "NOUN", "PUNCT"]
    r2 = root_cue_values(t2, p2)
    chk(r2[4]["rpred"] == "to", "an infinitival verb is non-finite ('to'), got %s" % r2[4]["rpred"])
    chk(r2[2]["rpred"] == "base" and r2[2]["rpos"].startswith("1"), "the matrix verb is candidate 1 (got %s/%s)"
        % (r2[2]["rpred"], r2[2]["rpos"]))
    chk(r2[2]["rpos"].endswith("S"), "the matrix verb has a nominal to its left (got %s)" % r2[2]["rpos"])

    t3 = ["Great", "prices", "on", "shoes", "!"]; p3 = ["ADJ", "NOUN", "ADP", "NOUN", "PUNCT"]
    r3 = root_cue_values(t3, p3)
    chk(r3[2]["rpred"] == "nov", "a verbless fragment marks its nominals 'nov' (got %s)" % r3[2]["rpred"])

    t4 = ["She", "has", "left", "."]; p4 = ["PRON", "AUX", "VERB", "PUNCT"]
    chk(root_cue_values(t4, p4)[3]["rpred"] == "auxhave", "a perfect participle is auxhave")
    t5 = ["He", "was", "running", "."]; p5 = ["PRON", "AUX", "VERB", "PUNCT"]
    chk(root_cue_values(t5, p5)[3]["rpred"] == "auxbe", "a progressive is auxbe")
    t6 = ["The", "man", "seen", "yesterday", "left", "."]
    p6 = ["DET", "NOUN", "VERB", "NOUN", "VERB", "PUNCT"]
    chk(root_cue_values(t6, p6)[3]["rpred"] == "ed", "a bare participle keeps its 'ed' form class")

    # the patch is reversible and inert when off
    enable_root_cues(False)
    tab = AA.load_attachment_validities()
    A0, n0 = AA.arc_scores(["The", "dog", "ran", "."], ["DET", "NOUN", "VERB", "PUNCT"], tab)
    enable_root_cues(True)
    A1, n1 = AA.arc_scores(["The", "dog", "ran", "."], ["DET", "NOUN", "VERB", "PUNCT"], tab)
    enable_root_cues(False)
    A2, _ = AA.arc_scores(["The", "dog", "ran", "."], ["DET", "NOUN", "VERB", "PUNCT"], tab)
    fin = np.isfinite(A0)
    chk(np.allclose(A0[fin], A2[fin]), "disabling the patch restores the reference activations byte-for-byte")
    chk(np.allclose(A0[1:][np.isfinite(A0[1:])], A1[1:][np.isfinite(A1[1:])]),
        "the root cues touch ONLY the root row (non-root rows unchanged)")
    chk(np.allclose(A0[0][np.isfinite(A0[0])], A1[0][np.isfinite(A1[0])]),
        "with an asset that has no root-cue cells the root row is unchanged (backwards compatible)")

    # the teaching boost only moves the root row
    tb = ["The", "vote", "is", "confusing"]; pb = ["DET", "NOUN", "AUX", "ADJ"]
    B = np.zeros((5, 5)); C = predication_boost(B, tb, pb)
    chk(np.allclose(C[1:], B[1:]), "predication_boost touches only the teacher's root row")
    chk(C[0][4] > 0, "predication_boost boosts the copular predicate's root arc (got %.2f)" % C[0][4])
    tc = ["When", "I", "arrived", "she", "left"]; pc = ["SCONJ", "PRON", "VERB", "PRON", "VERB"]
    D = predication_boost(np.zeros((6, 6)), tc, pc)
    chk(D[0][3] < 0 <= D[0][5], "the subordinate-clause verb is penalised, the matrix verb is not (%.1f vs %.1f)"
        % (D[0][3], D[0][5]))

    # PLASTICITY: one online comprehension outcome must accrue into the ROOT cue counts
    enable_root_cues(True)
    t7 = ["The", "vote", "is", "confusing", "."]; p7 = ["DET", "NOUN", "AUX", "ADJ", "PUNCT"]
    tt = {"counts": AA.new_counts(), "frames": {}, "pp_assoc": None}
    tt["strength"] = AA.strengths_from_arc_counts(tt["counts"])
    AA.observe_arc_outcome(t7, p7, 4, 0, table=tt)
    cell = tt["counts"]["cues"].get("rpred", {}).get("ROOT:ADJ|cop")
    chk(cell is not None and cell[0] > 0, "observe_arc_outcome accrues the ROOT cue online (cell %s)" % (cell,))
    chk(tt["strength"] is not None, "strengths recomputed after the online observation")
    enable_root_cues(False)

    print("SELF-TEST", "GREEN" if ok else "RED", flush=True)
    return 0 if ok else 1


# --------------------------------------------------------------------------------------------------------- anatomy
def anatomy(cap=700):
    enable_root_cues(False)
    test = sentences(TEST, cap=cap, maxlen=10 ** 6); tab = AA.load_attachment_validities()
    st = tab["strength"]
    print("root-keyed cue cells in the live asset:",
          {c: sum(1 for k in st.get(c, {}) if k.startswith("ROOT:")) for c in AA.CUES})
    arcs = [AA.arc_scores(t, p, tab) for t, p, _, _ in test]
    ties = Counter()
    for (toks, pos, hg, rels), (A, n) in zip(test, arcs):
        v = [A[0][j] for j in range(1, n + 1) if np.isfinite(A[0][j])]
        if v:
            m = max(v); ties[min(sum(1 for x in v if x >= m - 1e-9), 5)] += 1
    print("sentences by number of candidates TIED at the best root score:", dict(sorted(ties.items())))
    out = {"ties": dict(sorted(ties.items())), "root_cue_cells": 0}
    for dec in ("incr", "map1"):
        AA.DECODE = dec
        for label, delta in (("base", 0.0), ("ORACLE", 20.0)):
            tot = ok = 0; rt = Counter(); rk = Counter()
            for (toks, pos, hg, rels), (A, n) in zip(test, arcs):
                B = A.copy()
                if delta:
                    for j in range(1, n + 1):
                        if hg[j - 1] == 0 and np.isfinite(B[0][j]):
                            B[0][j] += delta
                hd, _ = AA.decode(toks, pos, B, n)
                for i, (g, r) in enumerate(zip(hg, rels), start=1):
                    tot += 1; hit = hd.get(i, -1) == g; ok += hit
                    if r in RELS:
                        rt[r] += 1; rk[r] += hit
            rec = {"uas": round(ok / tot, 4), "rel": {r: round(rk[r] / max(1, rt[r]), 3) for r in RELS if rt[r]}}
            out["%s_%s" % (dec, label)] = rec
            print(dec, label, rec, flush=True)
    return out


# ------------------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true"); ap.add_argument("--anatomy", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--cap", type=int, default=None); ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--test-cap", type=int, default=700)
    ap.add_argument("--gcop", type=float, default=8.0); ap.add_argument("--gsub", type=float, default=8.0)
    ap.add_argument("--gfin", type=float, default=8.0)
    ap.add_argument("--arms", default="base,cues,cues_teach,twin,abl_rpred,abl_rsub,abl_rpos,teach_only")
    ap.add_argument("--save-tables", default=None, help="pickle the built tables here for follow-up probes")
    ap.add_argument("--live", action="store_true", help="also report the live-chain number (category organ's own tags)")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    out_dir = get_output_dir(ANCHOR); os.makedirs(out_dir, exist_ok=True)
    if a.anatomy:
        rec = anatomy(a.test_cap)
        with open(os.path.join(str(out_dir), "anatomy.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        return 0
    smoke = not a.full
    cap = a.cap if a.cap is not None else (1500 if smoke else 6000)
    test_cap = a.test_cap
    t0 = time.time()
    train = sentences(TRAIN, cap=cap)
    test = sentences(TEST, cap=test_cap, maxlen=10 ** 6)
    print("train %d, test %d (%s)" % (len(train), len(test), "smoke" if smoke else "FULL"), flush=True)

    if a.sweep:
        enable_root_cues(True)
        teacher = knowledge_free_teacher(train, beta=10.0)
        rows = []
        for g in (0.0, 2.0, 4.0, 8.0, 16.0):
            tab = build_table(train, True, g > 0, (g, g, g), rounds=a.rounds, teacher=teacher)
            r = evaluate(tab, test, "incr", True)
            rows.append({"gamma": g, "uas": round(r["uas"], 4), "root": r["rel"].get("root")})
            print("gamma %5.1f -> UAS %.4f root %.3f (%.0fs)" % (g, r["uas"], r["rel"].get("root", 0), time.time() - t0), flush=True)
        with open(os.path.join(str(out_dir), "sweep.json"), "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)
        return 0

    global ROOT_CUES
    arms = a.arms.split(",")
    teacher = knowledge_free_teacher(train, beta=10.0)
    print("teacher ready in %.0fs" % (time.time() - t0), flush=True)
    gam = (a.gcop, a.gsub, a.gfin)
    tables = {}
    ALL = ("rpred", "rsub", "rpos")
    specs = {"base": (False, False, ALL, False), "cues": (True, False, ALL, False),
             "cues_teach": (True, True, ALL, False), "twin": (True, True, ALL, False),
             "teach_only": (False, True, ALL, False),
             "abl_rpred": (True, False, ("rpred",), False), "abl_rsub": (True, False, ("rsub",), False),
             "abl_rpos": (True, False, ("rpos",), False),
             "arg": (True, False, ALL + ("rarg",), False),
             "cues_flat": (True, False, ALL, False), "cues_teach_flat": (True, True, ALL, False),
             "conj": (True, True, ALL, False), "conj_flat": (True, True, ALL, False),
             "csub": (True, True, ALL, False), "conjcsub": (True, True, ALL, False),
             "copfix": (True, True, ALL, False), "copfix_csub": (True, True, ALL, False),
             "copfix_conj_csub": (True, True, ALL, False),
             "clausal": (False, False, ALL, True),
             "cues_clausal": (True, False, ALL, True),
             "full": (True, True, ALL, True),
             "twin_full": (True, True, ALL, True)}
    keep = ROOT_CUES
    results = {}
    for arm in arms:
        cues_on, teach, subset, clau = specs[arm]
        ROOT_CUES = tuple(subset)
        CENTER["on"] = arm.endswith("_centre")   # FLAT is the shipped readout; centring was refuted
        CONJ_RPRED["on"] = arm.startswith("conj")
        CSUB["on"] = "csub" in arm
        COPFIX["on"] = "copfix" in arm
        src = {"twin": "cues", "twin_teach": "cues_teach", "twin_full": "full"}.get(arm)
        if src:
            tab = tables.get(src)
            if tab is None:
                cs, tc, ss, cl = specs[src]
                tab = build_table(train, cs, tc, gam, rounds=a.rounds, teacher=teacher, clausal=cl); tables[src] = tab
        else:
            tab = build_table(train, cues_on, teach, gam, rounds=a.rounds, teacher=teacher, clausal=clau)
            tables[arm] = tab
        for dec in ("incr", "map1"):
            _SHUFFLE["on"] = arm.startswith("twin"); _SHUFFLE["rng"] = random.Random(4242)
            r = evaluate(tab, test, dec, cues_on, clau)
            _SHUFFLE["on"] = False
            results["%s|%s" % (arm, dec)] = r
            _print("%s/%s" % (arm, dec), r)
        ROOT_CUES = keep
        print("   [%s done at %.0fs]" % (arm, time.time() - t0), flush=True)

    # paired CIs against the base arm, both decodes
    cis = {}
    for dec in ("incr", "map1"):
        b = results.get("base|%s" % dec)
        if b is None:
            continue
        for arm in arms:
            k = "%s|%s" % (arm, dec)
            if arm == "base" or k not in results:
                continue
            r = results[k]
            cis["root %s vs base (%s)" % (arm, dec)] = paired_ci(b["_root_hit"], b["_root_n"], r["_root_hit"], r["_root_n"])
            cis["UAS %s vs base (%s)" % (arm, dec)] = uas_ci(b, r)
            cis["copsubj %s vs base (%s)" % (arm, dec)] = paired_ci(b["_cop_hit"], b["_cop_n"], r["_cop_hit"], r["_cop_n"])
    for k, v in cis.items():
        print("  CI  %-34s delta %+.4f  CI [%+.4f, %+.4f]  hw %.4f" % (k, v[0], v[1], v[2], v[3]), flush=True)

    if a.save_tables:
        import pickle
        with open(a.save_tables, "wb") as f:
            pickle.dump(tables, f)
        print("tables pickled ->", a.save_tables, flush=True)
    live = {}
    if a.live:
        for arm in ("base", "full"):
            if arm in tables:
                cs, tc, ss, cl = specs[arm]
                ROOT_CUES = tuple(ss)
                live[arm] = live_chain(tables[arm], cs, cl, test_cap=len(test))
                ROOT_CUES = keep
                print("LIVE-CHAIN %-6s %s" % (arm, live[arm]), flush=True)

    doc = {"anchor": ANCHOR, "live_chain": live, "mode": "smoke" if smoke else "full", "train_cap": cap, "test_sentences": len(test),
           "rounds": a.rounds, "gammas": {"cop": a.gcop, "sub": a.gsub, "fin": a.gfin},
           "arms": {k: summarise(k, v) for k, v in results.items()},
           "rel_n": results[list(results)[0]]["rel_n"],
           "paired_ci_over_sentences": {k: {"delta": v[0], "lo": v[1], "hi": v[2], "halfwidth": v[3]} for k, v in cis.items()},
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(str(out_dir), "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("wrote", os.path.join(str(out_dir), "metrics.json"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
