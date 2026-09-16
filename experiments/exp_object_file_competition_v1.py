"""exp_object_file_competition_v1 -- THE OBJECT-FILE MERGE/SPLIT DECISION AS ONE CUE COMPETITION
(priority 136: the reader's entity clustering is the numbered pronoun lever).

WHAT THIS CELL IS FOR
---------------------
pri 131 isolated the identity basis of the pronoun pick on ONE code path and found the contract FREE
(head string 0.3263 == the reader's own entity files 0.3263, CI[0,0]) while a GOLD-ENTITY oracle for the
same pick scores 0.4431 (+0.1168 CI[+0.0241,+0.2614] CI-sep, 12 GUM documents).  So the remaining pronoun
signal is the reader's CLUSTERING (`hdlab/entity_resolver.py::cluster` + the crosstype bridge), not the pick.

HOW THE BRAIN DOES THIS (the opening move; PINNED vs OUR-INVENTION)
------------------------------------------------------------------
A new mention either UPDATES an open file or OPENS a new one -- Heim (1982) file-change semantics'
Novelty-Familiarity Condition and Kahneman & Treisman (1992) object files.  The decision is a GRADED match
of the mention's features against the open files, not a string coincidence:

  A(f) = B_i(f)                                  ACT-R base-level: recency x frequency x role prominence
       + SUM_c  w_c[value_c(m, f)]               parallel cue evidence, cues SUMMED not filtered
  update argmax A if max A >= tau ; else OPEN A NEW FILE   (ACT-R retrieval threshold; a retrieval failure
                                                            IS the novelty signal -- Norman & O'Reilly 2003
                                                            pattern separation vs completion)

  * B_i is PINNED and is `hdlab.salience_binder.actr_activation` (Anderson & Schooler 1991), already shared
    by every coref organ -- NOT re-implemented here.
  * The additive cue weight w_c[v] is PINNED IN FORM as the log-likelihood ratio (Anderson & Milson 1989
    rational analysis: the associative strength S_ji is the log posterior odds):
        w_c[v] = log P(v | SAME file) - log P(v | DIFFERENT file)
    and those probabilities are COUNTS -- the Competition Model's cue validity (MacWhinney & Bates 1989),
    accrued from the reader's own confirmed decisions (the pri 108 / pri 117 template).
  * tau (the retrieval threshold) and the accrual margin are OUR-INVENTION: SWEPT, never adopted.

WHAT THE SHIPPED ORGAN DOES INSTEAD (the deviation this cell measures)
---------------------------------------------------------------------
`EntityResolver.cluster` HARD-FILTERS (phi-compatible AND exact head-lemma identity), then takes the argmax
with policy='argmax' -- ALWAYS MERGE.  It therefore (a) cannot hold two same-head referents apart, (b) cannot
use type / predication / definiteness evidence at all, and (c) has no threshold at which it opens a new file.
Heim's indefinite ("a dog" after "a dog") is merged by construction.

ROWS
----
  --decompose N   the partition ALGEBRA decomposition of the oracle gain: refine (fix over-merges only) /
                  coarsen (fix under-splits only) / oracle, on the pronoun instrument, plus the error-type
                  counts (which cue merged, which cue was missing) -- the diagnosis.
  --cue-reach N   for every gold entity the reader SPLIT, does ANY cue in the set even reach it?
  --build-validities N   build data/frontend_assets/object_file_validities_gum_v1.json from GUM TRAIN.
  --tune N        sweep the retrieval threshold on the TRAIN split (choose the operating point here).
  --competition N the competition build on TEST: partition quality vs GUM gold (B3/MUC/CEAFe, paired
                  bootstrap over documents) + the pronoun instrument + the information-free twin.
  --readout N     the CONSUMER REPAIR: the pick's antecedent readout, with its identity control.
  --picksweep N   the consumer's own phase diagram over the new files (is its operating point stale?).
  --live N        the LIVE A/B with the organ INSTALLED (every consumer measured through read()).
  --noregress N   UD-EWT agent/patient/state through the live reader, both arms in one process.
  --self-test     corpus-free structural self-test.

EVERY ARM IS AN OFFLINE REPLAY THAT IS ASSERTED EQUAL TO THE LIVE ORGAN before any contrast is reported:
each document is read ONCE by the LIVE SituationReader on TEXT ONLY, the shipped clustering is re-run over
the captured mentions and asserted to reproduce `m["cluster"]` for every non-pronoun mention, and the pick
is replayed from those mentions and asserted to reproduce the live records item-for-item.

Glass-box, CPU, NO external LLM at inference; the offline supply is GUM TRAIN partitions + WordNet + the
frozen entity-type spoke (all static, admissible FOUNDATION assets).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import argparse
import io
import json
import math
import random
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

SEED = 20260916
N_BOOT = 2000


def get_output_dir(default_name: str = "object_file_competition_v1"):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = os.path.join(_REPO, "data", "exp_" + name)
    os.makedirs(d, exist_ok=True)
    return d


OUT_DIR = get_output_dir()
VALIDITY_ASSET = os.path.join(_REPO, "data", "frontend_assets", "object_file_validities_gum_v1.json")


def _p(x, nd=4):
    return "n/a" if x is None else ("%." + str(nd) + "f") % x


def acc(vs):
    flat = [x for row in vs for x in row]
    return float(sum(flat)) / len(flat) if flat else 0.0


def paired_boot(a_docs, b_docs, n_boot=N_BOOT, seed=SEED):
    """Paired bootstrap over DOCUMENTS (the bootstrap unit), items pooled inside a document."""
    a_docs = [list(r) for r in a_docs]
    b_docs = [list(r) for r in b_docs]
    n = len(a_docs)
    if n == 0:
        return None
    rng = random.Random(seed)
    base = acc(b_docs) - acc(a_docs)
    ds = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ar = [a_docs[i] for i in idx]
        br = [b_docs[i] for i in idx]
        ds.append(acc(br) - acc(ar))
    ds.sort()
    lo = ds[int(0.025 * len(ds))]
    hi = ds[int(0.975 * len(ds)) - 1]
    return {"delta": round(base, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2.0, 4), "sep": bool(lo > 0 or hi < 0)}


# =====================================================================================================
# 1. COREF PARTITION METRICS (B3 / MUC / CEAFe) -- the contract of
#    experiments/exp_commonnoun_coref_diagnostic_v1.{b3,muc,ceafe}; re-stated here so this cell has no
#    heavyweight import.  Cross-checked against that module in --self-test.
# =====================================================================================================
def _clusters(labels):
    d = defaultdict(set)
    for i, l in enumerate(labels):
        d[l].add(i)
    return list(d.values())


def b3(pred, gold):
    n = len(pred)
    if n == 0:
        return 0.0, 0.0, 0.0
    gp, gg = defaultdict(set), defaultdict(set)
    for i in range(n):
        gp[pred[i]].add(i)
        gg[gold[i]].add(i)
    ps = rs = 0.0
    for i in range(n):
        pc, gc = gp[pred[i]], gg[gold[i]]
        ov = len(pc & gc)
        ps += ov / len(pc)
        rs += ov / len(gc)
    p, r = ps / n, rs / n
    return p, r, (2 * p * r / (p + r) if p + r > 0 else 0.0)


def muc(pred, gold):
    def side(key, resp):
        kc = _clusters(key)
        resp_of = {}
        for ci, c in enumerate(_clusters(resp)):
            for i in c:
                resp_of[i] = ci
        num = den = 0
        for c in kc:
            if len(c) <= 1:
                continue
            num += len(c) - len({resp_of[i] for i in c})
            den += len(c) - 1
        return num, den
    rn, rd = side(gold, pred)
    pn, pd = side(pred, gold)
    rec = rn / rd if rd else 0.0
    pre = pn / pd if pd else 0.0
    return pre, rec, (2 * pre * rec / (pre + rec) if pre + rec > 0 else 0.0)


def ceafe(pred, gold):
    R, G = _clusters(pred), _clusters(gold)
    if not R or not G:
        return 0.0, 0.0, 0.0
    sim = np.zeros((len(R), len(G)))
    for i, r in enumerate(R):
        for j, g in enumerate(G):
            inter = len(r & g)
            if inter:
                sim[i, j] = 2.0 * inter / (len(r) + len(g))
    try:
        from scipy.optimize import linear_sum_assignment
        ri, gi = linear_sum_assignment(-sim)
        total = float(sim[ri, gi].sum())
    except Exception:
        total = 0.0
        usedR, usedG = set(), set()
        for s, i, j in sorted(((sim[i, j], i, j) for i in range(len(R)) for j in range(len(G))), reverse=True):
            if s <= 0:
                break
            if i in usedR or j in usedG:
                continue
            usedR.add(i)
            usedG.add(j)
            total += s
    pre, rec = total / len(R), total / len(G)
    return pre, rec, (2 * pre * rec / (pre + rec) if pre + rec > 0 else 0.0)


def b3_boot(a_docs, b_docs, n_boot=N_BOOT, seed=SEED):
    """PAIRED BOOTSTRAP OVER DOCUMENTS for B-cubed F1.  B3 is not a mean over items, so it is resampled the
    way it is computed: each resample rebuilds the pooled (pred, gold) label lists from the resampled
    DOCUMENTS (labels namespaced per draw so a document drawn twice cannot merge with itself) and recomputes
    B3 on that pool.  `a_docs`/`b_docs` are lists of (pred_labels, gold_labels) per document."""
    n = len(a_docs)
    if n == 0:
        return None
    rng = random.Random(seed)

    def pooled(rows, idx):
        pr, gl = [], []
        for k, i in enumerate(idx):
            p_, g_ = rows[i]
            tag = "%d|" % k
            pr += [tag + x for x in p_]
            gl += [tag + x for x in g_]
        return b3(pr, gl)[2]
    allidx = list(range(n))
    base = pooled(b_docs, allidx) - pooled(a_docs, allidx)
    ds = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ds.append(pooled(b_docs, idx) - pooled(a_docs, idx))
    ds.sort()
    lo = ds[int(0.025 * len(ds))]
    hi = ds[int(0.975 * len(ds)) - 1]
    return {"delta": round(base, 4), "ci": [round(lo, 4), round(hi, 4)],
            "half": round((hi - lo) / 2.0, 4), "sep": bool(lo > 0 or hi < 0)}


def pooled_partition(part_rows):
    """Pool per-document (pred, gold) label lists into ONE population for a set-level score, NAMESPACING
    each document so two documents' file ids can never merge into one cluster (the bootstrap in `b3_boot`
    does the same thing per draw; this is the point estimate)."""
    pr, gl = [], []
    for i, (p_, g_) in enumerate(part_rows):
        tag = "%d|" % i
        pr += [tag + x for x in p_]
        gl += [tag + x for x in g_]
    return partition_scores(pr, gl)


def partition_scores(pred, gold):
    _, _, fb = b3(pred, gold)
    _, _, fm = muc(pred, gold)
    _, _, fc = ceafe(pred, gold)
    bp, br, _ = b3(pred, gold)
    return {"b3_f1": round(fb, 4), "b3_p": round(bp, 4), "b3_r": round(br, 4),
            "muc_f1": round(fm, 4), "ceafe_f1": round(fc, 4),
            "conll_avg": round((fb + fm + fc) / 3.0, 4), "n": len(pred)}


# =====================================================================================================
# 2. THE OBJECT-FILE COMPETITION  --  the proposed organ (ported verbatim into hdlab/entity_resolver.py
#    by object_file_competition_patch.diff)
# =====================================================================================================
# THE PAIRWISE CUES (evidence about WHICH open file this mention updates).  Each cue's values are MUTUALLY
# EXCLUSIVE and jointly exhaustive, so no two values of one cue can both fire and two cues cannot count the
# same evidence twice -- the first teacher run exposed exactly that confound (a `head_type=na` value that
# meant BOTH "the head already matched" and "this file has no head" scored +2.52, i.e. it was reading
# head_id's signal; `name_id` and `name_surf` overlapped the same way).
CUES = ("name", "head", "etype", "predication", "phi", "cb", "np")

CUE_VALUES = {
    "name":        ("canon_match", "surf_match", "clash", "na"),
    "head":        ("lemma_match", "isa", "mismatch", "no_head"),
    "etype":       ("licensed", "blocked", "na"),
    "predication": ("linked", "na"),
    "phi":         ("agree", "conflict", "unknown"),
    "cb":          ("prev_cb", "no"),
    # THE NOMINAL-RUN CUE.  The introduction organ opens a referent per CONTENT-NOUN TOKEN, so a complex
    # nominal ("tenure track university faculty") arrives as FOUR mentions where the discourse has ONE
    # object.  English compounds are RIGHT-HEADED (Williams 1981 Right-Hand Head Rule) and a complex
    # nominal denotes ONE object, so an adjacent run of content heads is ONE file card.  Measured: 1,331 of
    # 3,689 differently-filed mention pairs of a split gold entity lie INSIDE one gold mention span.
    # ... and the run is a run of NOMINALS: the reader opens a referent on 122 VERB-headed and 30
    # ADV-headed tokens per 12 GUM documents, and merging those into a neighbour's file is what cost the
    # pronoun row items ("his" -> "put", "he" -> "top").  The category is a VALUE of the cue, not a hard
    # gate -- the teacher decides how much it is worth.
    # ... and the run is CONFIGURATION-CONDITIONED (pri 136 phase 7, from the flip audit: 21 of 72
    # right->wrong flips were merges carried by a FLAT `np` validity of +6.23).  The configuration is the
    # token immediately before the later head: a DETERMINER, a possessive, a coordinator or punctuation
    # OPENS A NEW NOMINAL (Heim again -- a determiner is a file-opening signal), so adjacency across that
    # boundary is a different cue value from adjacency inside one nominal.  This is the same lesson pri 108
    # recorded for the role competition: a flat additive table over all cue values double-counts; the
    # configuration-conditioned contrast form is required.
    "np":          ("gap1_nom", "gap1_x", "gap2_nom", "gap2_x", "same_sent_far", "other_sent"),
}

# THE CRITERION CUE, which is a property of the MENTION and not of any pair: Heim's Novelty-Familiarity
# Condition is a constraint on the UPDATE ("an indefinite introduces a new file"), not evidence about which
# file -- so it belongs on the RIGHT-hand side of the retrieval-threshold inequality, as a criterion shift
# (signal-detection: the novelty signal sets the criterion; Norman & O'Reilly 2003), NEVER as an additive
# term in the activation.  Counting it as a pairwise cue produced a base-rate artifact in the first teacher
# run (indefinite +2.84 == definite +2.84), because the candidate-set size, not identity, drove the ratio.
CRITERION = "novelty"
CRITERION_VALUES = ("indefinite", "definite", "bare")

# THE CUE-SET VERSION, SELF-GATED ON THE LOADED ASSET (the pattern `graded_role_assigner` already uses):
# an asset that does not declare `cue_set` is v1 and the organ emits v1's value space, so an older asset
# keeps reproducing its own numbers exactly.  v2 conditions the nominal-run cue on whether a DETERMINER /
# possessive / coordinator / punctuation opens a new nominal before the later head -- the fix the phase-7
# flip audit named (21 of 72 right->wrong flips were merges carried by a FLAT `np` validity of +6.23; the
# same lesson pri 108 recorded for the role competition: a flat additive table double-counts, the
# configuration-conditioned contrast form is required).
NP_VALUES = {
    "v1": ("gap1_nom", "gap1_x", "gap2_nom", "gap2_x", "same_sent_far", "other_sent"),
    "v2": ("gap1_same_np", "gap1_new_np", "gap2_same_np", "gap2_new_np",
           "gap1_x", "gap2_x", "same_sent_far", "other_sent"),
}


def cue_values(cue_set="v1"):
    v = dict(CUE_VALUES)
    v["np"] = NP_VALUES.get(cue_set, NP_VALUES["v1"])
    return v

_DEF_DET = frozenset({"the", "this", "that", "these", "those", "its", "his", "her", "their", "my",
                      "our", "your"})
_INDEF_DET = frozenset({"a", "an", "another", "some", "one", "other"})


def _definiteness(span_toks, sents=None, sent_idx=None, wpos=None):
    """Heim's Novelty-Familiarity Condition, read off the determiner: an INDEFINITE introduces a NEW file;
    a DEFINITE re-accesses an open one.  PINNED (Heim 1982); the shipped organ ignores it entirely.

    MEASURED BLOCKER: the reader's mention spans are ONE TOKEN (the content head), so the determiner is not
    on the mention at all -- on 24 GUM TRAIN documents EVERY mention reads `bare` and the condition is
    unreadable.  Given the sentence tokens the organ can look one word to the left, which is where the
    determiner is; without them it abstains to `bare` (and the criterion shift is then flat by
    construction).  `sents` is an OPTIONAL argument: the organ is correct either way."""
    if span_toks:
        w = str(span_toks[0]).lower()
        if w in _INDEF_DET:
            return "indefinite"
        if w in _DEF_DET:
            return "definite"
    if sents is not None and sent_idx is not None and wpos is not None:
        try:
            if 0 <= sent_idx < len(sents) and 0 < wpos <= len(sents[sent_idx]):
                prev = str(sents[sent_idx][wpos - 1]).lower()
                if prev in _INDEF_DET:
                    return "indefinite"
                if prev in _DEF_DET:
                    return "definite"
        except (IndexError, TypeError):
            pass
    return "bare"


# a determiner / possessive / coordinator / punctuation immediately before a nominal head OPENS a new
# nominal -- so two adjacent heads across that boundary are two NPs, not one compound.
_NP_BOUNDARY = frozenset({",", ";", ":", ".", "(", ")", "\"", "'", "and", "or", "but", "nor",
                          "of", "in", "on", "at", "to", "for", "with", "by", "from"})


def _np_boundary_before(sents, sent_idx, wpos):
    """True when the token immediately before `wpos` starts a NEW nominal (a determiner/possessive/
    coordinator/punctuation).  Abstains to False when the sentence tokens are not available."""
    if sents is None or sent_idx is None or wpos is None:
        return False
    try:
        if not (0 <= sent_idx < len(sents)) or not (0 < wpos <= len(sents[sent_idx])):
            return False
        w = str(sents[sent_idx][wpos - 1]).lower()
    except (IndexError, TypeError):
        return False
    return (w in _DEF_DET) or (w in _INDEF_DET) or (w in _NP_BOUNDARY) or w.endswith("'s")


class OFile:
    """One object file / Heim file card: the mention history (for ACT-R base-level) + the accrued card."""
    __slots__ = ("cid", "history", "gender", "number", "heads", "canons", "surfaces", "names",
                 "subj_sent", "last_order", "last_sent", "last_wpos", "last_upos")

    def __init__(self, cid):
        self.cid = cid
        self.history = []
        self.gender = None
        self.number = None
        self.heads = set()
        self.canons = set()
        self.surfaces = set()
        self.names = set()          # the NAME surfaces filed here (the entity-type spoke's key)
        self.subj_sent = -1
        self.last_order = -1
        self.last_sent = -1
        self.last_wpos = -99
        self.last_upos = ""

    def update(self, order, role, gender, number, head, sent_idx, canon, surf, is_name, wpos=-99, upos=""):
        self.history.append((float(order), role))
        if gender and self.gender is None:
            self.gender = gender
        if number and self.number is None:
            self.number = number
        if head:
            self.heads.add(head)
        if canon:
            self.canons.add(canon)
        if surf:
            self.surfaces.add(surf)
            if is_name:
                self.names.add(surf)
        if role == "SUBJECT":
            self.subj_sent = sent_idx
        self.last_order = order
        self.last_sent = sent_idx
        self.last_wpos = wpos
        self.last_upos = upos or ""


class Validities:
    """The Competition-Model cue-validity table for the merge/split decision.

    counts[cue][value] = [n_same, n_different]      (accrued; the ONLY state)
    strength[cue][value] = log P(value|same) - log P(value|different)    (Anderson & Milson log odds)

    The strengths are a PURE FUNCTION of the counts, recomputed after every accrual -- so the table is
    never frozen: `observe_file_decision` accrues one confirmed decision at read time."""

    def __init__(self, counts=None, crit_counts=None, alpha=0.5, cue_set="v1"):
        self.alpha = float(alpha)
        self.cue_set = cue_set if cue_set in NP_VALUES else "v1"
        self.values = cue_values(self.cue_set)
        self.counts = {c: {v: [0.0, 0.0] for v in self.values[c]} for c in CUES}
        # the criterion counts are [n_reaccessed_an_open_file, n_opened_a_new_file] per definiteness value
        self.crit = {v: [0.0, 0.0] for v in CRITERION_VALUES}
        if counts:
            for c, vals in counts.items():
                if c not in self.counts:
                    continue
                for v, pair in vals.items():
                    if v in self.counts[c]:
                        self.counts[c][v] = [float(pair[0]), float(pair[1])]
        if crit_counts:
            for v, pair in crit_counts.items():
                if v in self.crit:
                    self.crit[v] = [float(pair[0]), float(pair[1])]
        self.strength = {}
        self.crit_shift = {}
        self.recompute()

    def recompute(self):
        a = self.alpha
        st = {}
        for c in CUES:
            vals = self.values[c]
            ns = sum(self.counts[c][v][0] for v in vals)
            nd = sum(self.counts[c][v][1] for v in vals)
            k = len(vals)
            st[c] = {}
            for v in vals:
                if ns <= 0 or nd <= 0:
                    st[c][v] = 0.0
                    continue
                ps = (self.counts[c][v][0] + a) / (ns + a * k)
                pd = (self.counts[c][v][1] + a) / (nd + a * k)
                st[c][v] = math.log(ps) - math.log(pd)
        self.strength = st
        # THE CRITERION SHIFT: how much harder (or easier) this mention's own determiner makes it to update
        # an open file at all -- log P(new|value) - log P(new), the mention-level log odds of NOVELTY.
        tot_new = sum(self.crit[v][1] for v in CRITERION_VALUES)
        tot_all = sum(self.crit[v][0] + self.crit[v][1] for v in CRITERION_VALUES)
        base = (tot_new + a) / (tot_all + 2 * a) if tot_all > 0 else 0.5
        cs = {}
        for v in CRITERION_VALUES:
            n0, n1 = self.crit[v]
            if n0 + n1 <= 0 or tot_all <= 0:
                cs[v] = 0.0
                continue
            pnew = (n1 + a) / (n0 + n1 + 2 * a)
            cs[v] = math.log(pnew / (1.0 - pnew)) - math.log(base / (1.0 - base))
        self.crit_shift = cs

    def w(self, cue, value):
        return self.strength.get(cue, {}).get(value, 0.0)

    def tau_shift(self, definiteness):
        return self.crit_shift.get(definiteness, 0.0)

    def observe(self, cues, same):
        j = 0 if same else 1
        for c, v in cues.items():
            if c in self.counts and v in self.counts[c]:
                self.counts[c][v][j] += 1.0

    def observe_criterion(self, definiteness, opened_new):
        if definiteness in self.crit:
            self.crit[definiteness][1 if opened_new else 0] += 1.0

    def permuted(self, seed=20260916):
        """THE INFORMATION-FREE TWIN: the SAME numbers, attached to the WRONG cue values (a permutation of
        each cue's value->strength map, and of the criterion shift).  Shape, magnitude and coverage
        identical; the information destroyed."""
        rng = random.Random(seed)
        tw = Validities(alpha=self.alpha, cue_set=self.cue_set)
        tw.counts = {c: {v: list(x) for v, x in vals.items()} for c, vals in self.counts.items()}
        tw.crit = {v: list(x) for v, x in self.crit.items()}
        st = {}
        for c in CUES:
            vals = list(self.values[c])
            perm = [self.strength[c][v] for v in vals]
            rng.shuffle(perm)
            st[c] = dict(zip(vals, perm))
        tw.strength = st
        cvals = list(CRITERION_VALUES)
        cperm = [self.crit_shift[v] for v in cvals]
        rng.shuffle(cperm)
        tw.crit_shift = dict(zip(cvals, cperm))
        return tw

    def to_json(self):
        return {"source": "object-file merge/split cue validities: counts accrued from GUM TRAIN gold "
                          "partitions (offline supply) and from the reader's own high-margin decisions "
                          "(online); strength = log P(value|same) - log P(value|different)",
                "cues": list(CUES), "cue_set": self.cue_set,
                "cue_values": {c: list(v) for c, v in self.values.items()},
                "criterion": CRITERION, "criterion_values": list(CRITERION_VALUES),
                "alpha": self.alpha,
                "counts": {c: {v: [float(x) for x in pair] for v, pair in vals.items()}
                           for c, vals in self.counts.items()},
                "criterion_counts": {v: [float(x) for x in pair] for v, pair in self.crit.items()},
                "strength": {c: {v: float(x) for v, x in vals.items()} for c, vals in self.strength.items()},
                "criterion_shift": {v: float(x) for v, x in self.crit_shift.items()}}

    @staticmethod
    def load(path=None):
        path = path or VALIDITY_ASSET
        with io.open(path, encoding="utf-8") as f:
            doc = json.load(f)
        return Validities(counts=doc.get("counts"), crit_counts=doc.get("criterion_counts"),
                          alpha=float(doc.get("alpha", 0.5)), cue_set=str(doc.get("cue_set", "v1")))

    def save(self, path=None):
        path = path or VALIDITY_ASSET
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(self.to_json(), indent=1, sort_keys=True))
        return path


_TYPE_CACHE = {}
_ETYPE_CACHE = {}


def _isa_compatible(h, heads):
    """WordNet taxonomic type compatibility (hdlab.typed_spokes.coref_type_license) -- the NON-writing
    bridge comparator the substrate already uses.  Static offline lexical foundation."""
    from hdlab.typed_spokes import coref_type_license
    for g in heads:
        k = (h, g) if h <= g else (g, h)
        v = _TYPE_CACHE.get(k)
        if v is None:
            try:
                v = bool(coref_type_license(h, g))
            except Exception:
                v = False
            _TYPE_CACHE[k] = v
        if v:
            return True
    return False


def _etype_cue(head, names, have_spoke):
    """THE ENTITY-TYPE SPOKE (frozen offline asset): may a common-noun anaphor headed `head` co-refer with
    a proper NAME filed here, on recorded entity-type grounds?  'the doctor' -> a person-typed name = licensed;
    'she' -> 'youtube' (an organisation) = blocked -- the cue pri 125 named as the missing one."""
    if not have_spoke or not names or not head:
        return "na"
    from hdlab.typed_spokes import type_licenses, entity_type_lemmas
    any_typed = False
    for s in names:
        k = (head, s)
        v = _ETYPE_CACHE.get(k)
        if v is None:
            try:
                lems = entity_type_lemmas(s, backoff=True)
                v = ("licensed" if (lems and type_licenses(head, s, backoff=True))
                     else ("blocked" if lems else "na"))
            except Exception:
                v = "na"
            _ETYPE_CACHE[k] = v
        if v == "licensed":
            return "licensed"
        if v == "blocked":
            any_typed = True
    return "blocked" if any_typed else "na"


def file_cues(m, f, *, head, canon, surf, gender, number, definite, is_name, sent_idx,
              prev_cb, name_link, have_spoke, wpos=-99, upos="", sents=None, cue_set="v1"):
    """THE CUE VECTOR for (mention m, open file f) -- every cue the brief names, read from the reader's own
    state and the static foundation assets.  No gold is read anywhere."""
    from hdlab.state_of_mind import compatible
    c = {}
    if canon and canon in f.canons:
        c["name"] = "canon_match"
    elif surf and surf in f.surfaces:
        c["name"] = "surf_match"
    elif canon and f.canons:
        c["name"] = "clash"
    else:
        c["name"] = "na"
    if not head or not f.heads:
        c["head"] = "no_head"
    elif head in f.heads:
        c["head"] = "lemma_match"
    elif _isa_compatible(head, f.heads):
        c["head"] = "isa"
    else:
        c["head"] = "mismatch"
    c["etype"] = "na" if is_name else _etype_cue(head, f.names, have_spoke)
    c["predication"] = "linked" if (name_link is not None and name_link == f.cid) else "na"
    if (gender or number) and (f.gender or f.number):
        c["phi"] = "agree" if compatible(gender, number, f.gender, f.number) else "conflict"
    else:
        c["phi"] = "unknown"
    c["cb"] = "prev_cb" if (prev_cb is not None and f.cid == prev_cb) else "no"
    if f.last_sent != sent_idx:
        c["np"] = "other_sent"
    else:
        d = int(wpos) - int(f.last_wpos)
        nom = (upos in ("NOUN", "PROPN", "ADJ", "NUM")
               and f.last_upos in ("NOUN", "PROPN", "ADJ", "NUM"))
        if d not in (1, 2):
            c["np"] = "same_sent_far"
        elif not nom:
            c["np"] = "gap%d_x" % d
        elif cue_set == "v2":
            newnp = _np_boundary_before(sents, sent_idx, wpos)
            c["np"] = "gap%d_%s" % (d, "new_np" if newnp else "same_np")
        else:
            c["np"] = "gap%d_nom" % d
    return c


def competition_cluster(ms, gaz, *, validities, tau=0.0, decay=None, role_prominence=None,
                        bridge_binds=None, online=False, online_margin=2.0, trace=None,
                        lemma="concept", sents=None):
    """{midx: cluster_id} over NON-pronoun mentions -- THE PROPOSED ORGAN.

    For every new mention, activation over the OPEN FILES is the ACT-R base-level (PINNED,
    salience_binder.actr_activation, shared) PLUS the summed cue evidence weighted by ACCRUED VALIDITIES
    (log-likelihood ratios).  A new file is opened when no open file's activation clears `tau` -- the
    ACT-R retrieval-failure / Heim novelty branch, which the shipped always-merge organ does not have.

    `bridge_binds` = {midx: file_id_of_the_bound_name} from the crosstype definite->name bridge, routed in
    as ONE CUE (`predication`), never as an override (the brief's item 1c).
    `online=True` accrues the reader's own HIGH-MARGIN decisions back into the validities (the observe path;
    nothing frozen).  No gold is read on any path."""
    from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
    from hdlab.coref import EntityAliaser, name_content_tokens
    from hdlab.lexical_utils import head_lemma, concept_lemma
    from hdlab.typed_spokes import available_entity_type
    # THE KEY.  `head_lemma` is the crude regex: it over-strips ("census" -> "censu") and, worse, it
    # FALSE-MERGES -- a head with no alphabetic characters (a redaction, a number) becomes "" and every
    # such head then matches every other.  `concept_lemma` is the substrate's owner-DONE brain-foundational
    # wordform->lexical-concept map (WordNet morphy).  Swept here, not assumed.
    lemma_fn = concept_lemma if lemma == "concept" else head_lemma
    decay = DEFAULT_DECAY if decay is None else decay
    role_prominence = ROLE_PROMINENCE if role_prominence is None else role_prominence
    have_spoke = available_entity_type()
    files, labels = [], {}
    aliaser = EntityAliaser()
    prev_cb, cur_sent = None, None
    rank_in_sent = {}
    for order, m in enumerate(ms):
        if m["is_pronoun"]:
            continue
        sent_idx = m.get("sent_idx", 0)
        if cur_sent is not None and sent_idx != cur_sent:
            row = sorted(rank_in_sent.get(cur_sent, {}).items(), key=lambda kv: kv[1])
            prev_cb = row[0][0] if row else prev_cb
        cur_sent = sent_idx
        rk = m.get("sent_role_rank", 99)
        role = "SUBJECT" if rk == 0 else ("OBJECT" if rk == 1 else "OTHER")
        span = m.get("span_toks", [m["head"]])
        head = lemma_fn(m["head"])
        gender = m.get("gender") or m.get("name_gender")
        number = m.get("number")
        surf = str(m["head"]).lower()
        wpos = int(m.get("wtok_start", -99))
        upos = (m.get("span_upos") or [""])[-1] or ""
        is_name = bool(name_content_tokens(span, upos=m.get("span_upos")))
        canon = aliaser.assign(span, gender, upos=m.get("span_upos")) if is_name else None
        definite = _definiteness(span, sents, sent_idx, wpos)
        link_file = None
        if bridge_binds is not None:
            link_file = bridge_binds.get(m["midx"])
        best, best_a, runner, best_cues = None, -1e18, -1e18, None
        for f in files:
            a = actr_activation(f.history, float(order), decay, role_prominence)
            if a == float("-inf"):
                a = -1e9
            cu = file_cues(m, f, head=head, canon=canon, surf=surf, gender=gender, number=number,
                           definite=definite, is_name=is_name, sent_idx=sent_idx, prev_cb=prev_cb,
                           name_link=link_file, have_spoke=have_spoke, wpos=wpos, upos=upos,
                           sents=sents, cue_set=validities.cue_set)
            s = a + sum(validities.w(c, v) for c, v in cu.items())
            if s > best_a:
                runner = best_a
                best, best_a, best_cues = f, s, cu
            elif s > runner:
                runner = s
        opened = False
        # THE CRITERION, not the evidence: the mention's own determiner shifts the threshold (Heim's
        # Novelty-Familiarity Condition as a signal-detection criterion).
        thr = tau + validities.tau_shift(definite)
        if best is None or best_a < thr:
            best = OFile(len(files))
            files.append(best)
            opened = True
        if trace is not None:
            trace.append({"midx": m["midx"], "opened": opened, "cid": best.cid,
                          "score": None if opened else round(best_a, 3),
                          "cues": best_cues if not opened else None})
        if online and (best_a - runner) >= online_margin:
            # THE OBSERVE PATH: a decision the reader made with a high margin is its own confirmed outcome
            # (self-supervised; the pri 117 template).  Nothing gold is consulted.
            if not opened and best_cues is not None:
                validities.observe(best_cues, True)
            validities.observe_criterion(definite, opened)
            validities.recompute()
        best.update(order, role, gender, number, head, sent_idx, canon, surf, is_name, wpos=wpos,
                    upos=upos)
        rank_in_sent.setdefault(sent_idx, {}).setdefault(best.cid, rk)
        labels[m["midx"]] = best.cid
    return labels


def observe_file_decision(validities, cues, same):
    """PLASTICITY (owner 2026-09-12: nothing frozen).  Accrue ONE confirmed merge/split outcome into the
    cue-validity counts and recompute the strengths.  The caller supplies the outcome from confirmed
    comprehension (a high-margin decision, a later agreement check, a correction); the organ never reads
    gold at inference."""
    validities.observe(cues, bool(same))
    validities.recompute()


# =====================================================================================================
# 3. CAPTURE -- read each document ONCE with the LIVE reader, then replay every arm offline
# =====================================================================================================
def _sents_of(doc):
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    return [[t.form for t in sorted(by_sent[si], key=lambda x: x.idx)] for si in sorted(by_sent)]


def repaired_bridge_binds(ms, base_labels, sents, reader, gaz, conf_thr=-3.0):
    """THE MISSING JOIN.  `crosstype_live_adapter._can_build` requires a GLOBAL token index on every
    non-pronoun mention; since pri 125 made `referent_per_np` the reader's mention source those indices are
    -1 on every mention, so `merge_crosstype_bridge` ABSTAINS on every read and the definite->name bridge --
    DE-LEAK PART 2, the organ that recovered the +0.0838 CI-sep experiencer gain -- is DEAD on the live
    path.  Measured here: 0 binds on 12 of 12 GUM documents.  The index is fully determined by what the
    mention already carries: gtok = sum(len(s) for s in sents[:sent_idx]) + wtok_start.  This function
    supplies it and runs the bridge; the landed form is the same three lines inside the adapter."""
    from hdlab.entity_resolver import EntityResolver
    from hdlab.crosstype_live_adapter import build_gold_free_doc
    offs, t = [], 0
    for sspan in sents:
        offs.append(t)
        t += len(sspan)
    ART = ("the", "a", "an", "this", "that", "these", "those")
    fixed = []
    for m in ms:
        m = dict(m)
        si = int(m.get("sent_idx", 0))
        if not m.get("is_pronoun") and int(m.get("gtok_start", -1)) < 0 and 0 <= si < len(offs):
            w = int(m.get("wtok_start", 0))
            g = offs[si] + w
            if 0 <= g < t:
                m["gtok_start"] = m["gtok_end"] = g
                m["head_g"] = g
                # THE SECOND BLOCKER, and it is the same one-token-span defect: the bridge's own
                # anaphoricity test is `mention.text.split()[0] in {the, a, an, this, that, ...}`, and the
                # reader's mention TEXT is the bare head, so EVERY definite fails that test and the bridge
                # abstains even once it has indices.  The determiner is right there in the reader's own
                # tokens; read it and put it back on the mention's text.
                if len(m.get("span_toks") or []) == 1 and w > 0:
                    prev = str(sents[si][w - 1]).lower()
                    if prev in ART:
                        m["span_toks"] = [prev] + list(m["span_toks"])
                        m["gtok_start"] = g - 1
        fixed.append(m)
    doc = build_gold_free_doc(fixed, base_labels, sents, reader=reader)
    if doc is None:
        return {}
    binds = EntityResolver().bridge_links(doc, gaz, conf_thr=conf_thr)
    return {fixed[i]["midx"]: int(lab) for i, lab in binds.items() if 0 <= i < len(fixed)}


def _cache_path(n_docs, split):
    return os.path.join(OUT_DIR, "capture3_%s_%d.pkl" % (split, n_docs))


def capture_cached(n_docs, verbose=True, split="test"):
    """The capture is the ONLY expensive step (one live read per document); cache it so every arm replays
    from the same reads.  The cache stores the reader's own output, never a gold-derived decision."""
    import pickle
    p = _cache_path(n_docs, split)
    if os.path.exists(p):
        with open(p, "rb") as f:
            cap = pickle.load(f)
        if verbose:
            print("  reusing the captured reads: %s (%d documents)" % (os.path.basename(p), len(cap)))
        return cap
    cap = capture(n_docs, verbose=verbose, split=split)
    with open(p, "wb") as f:
        pickle.dump(cap, f)
    return cap


def capture(n_docs, verbose=True, split="test"):
    """Read N GUM documents with the LIVE SituationReader on TEXT-ONLY input and capture everything an
    offline arm needs.  The shipped clustering is RE-RUN over the captured mentions and asserted to
    reproduce `m["cluster"]` exactly -- so the replay IS the organ."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    from experiments.exp_pronoun_pick_identity_contract_v1 import gum_questions, _answers, _gold_eid_at
    from hdlab.situation_reader import SituationReader
    from hdlab.entity_resolver import EntityResolver
    from hdlab.crosstype_live_adapter import build_gold_free_doc
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    pool = alldocs[1::2] if split == "test" else alldocs[0::2]
    step = max(1, len(pool) // max(1, n_docs))
    docs = [pool[i] for i in range(0, len(pool), step)][:n_docs]
    cap = []
    t0 = time.time()
    for d in docs:
        pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        rd = SituationReader()
        sm = rd.read(pth)
        ms = [dict(m) for m in (rd._coref_mentions or [])]
        sents = _sents_of(d)
        # --- the shipped clustering, re-run over the captured mentions (the faithfulness assertion) ---
        base = EntityResolver().cluster(ms, gaz=rd.gaz)
        doc_ct = build_gold_free_doc(ms, base, sents, reader=rd)
        binds = EntityResolver().bridge_links(doc_ct, rd.gaz, conf_thr=-3.0) if doc_ct is not None else {}
        merged = dict(base)
        for i, name_label in binds.items():
            if 0 <= i < len(ms):
                merged[ms[i]["midx"]] = name_label
        bad = sum(1 for m in ms if not m.get("is_pronoun")
                  and merged.get(m["midx"]) is not None
                  and -(int(merged[m["midx"]]) + 1) != m.get("cluster"))
        if bad:
            raise AssertionError("the offline clustering replay is NOT the live organ (%d of %d mentions "
                                 "differ on %s)" % (bad, len(ms), d.docid))
        # the bridge's binds expressed as {midx: bound NAME's own base file id} -- the predication CUE
        bridge_cue = {}
        for i, name_label in binds.items():
            if 0 <= i < len(ms):
                bridge_cue[ms[i]["midx"]] = int(name_label)
        qs = gum_questions(d)
        cap.append({"doc": str(d.docid), "ms": ms, "qs": qs, "gold": _gold_eid_at(d),
                    "sents": sents, "shipped_labels": merged, "base_labels": base,
                    "bridge_binds": bridge_cue,
                    "bridge_binds_repaired": repaired_bridge_binds(ms, base, sents, rd, rd.gaz),
                    "live": _answers(sm, ms),
                    "coarg": rd._coargument_positions(sents, {q["sent"] for q in qs})})
        if verbose:
            print("  captured %-24s  %4d mentions  %3d questions  %5.0fs"
                  % (str(d.docid)[:24], len(ms), len(cap[-1]["qs"]), time.time() - t0))
    return cap


def _apply_labels(ms, labels):
    """Write a clustering onto a COPY of the mention list, in the live organ's negative-int file scheme."""
    out = []
    for m in ms:
        m = dict(m)
        if not m.get("is_pronoun"):
            c = labels.get(m["midx"])
            if c is not None:
                m["cluster"] = -(int(c) + 1) if isinstance(c, int) else c
        out.append(m)
    return out


def pick_rows(c, labels, principle_b=False):
    """Replay the LANDED pronoun pick over ONE clustering and score it span-wise (abstention = wrong).
    `principle_b` passes the reader's own clause-mate CO-ARGUMENT map (the pinned Chomsky-1981 exclusion,
    which ships DEFAULT-OFF in the live reader: pri 131 measured it costing items THROUGH our 0.57-UAS
    parse).  The live reader runs it OFF, so the faithfulness assertion uses principle_b=False."""
    import hdlab.coref as CO
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    ms = _apply_labels(c["ms"], labels)
    tg = CO.discovered_pronoun_targets(ms, window=0)
    recs, _ab = CO.graded_pronoun_resolve(ms, tg, window=0,
                                          coarg=(c.get("coarg") if principle_b else None))
    ans = {(r["sent_idx"], r["target_wpos"]): {"head": r["resolved_head"], "span": r["antecedent_span"]}
           for r in recs}
    return [_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in c["qs"]]


def mention_partition(c, labels):
    """(pred, gold) label lists over the NON-PRONOUN mentions whose head position falls on a gold mention."""
    pred, gold = [], []
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        if e is None:
            continue
        lab = labels.get(m["midx"])
        pred.append("f%s" % lab)
        gold.append("g%s" % e)
    return pred, gold


def purity(c, labels):
    byfile = defaultdict(set)
    bygold = defaultdict(set)
    unmapped = 0
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        if e is None:
            unmapped += 1
            continue
        byfile[labels.get(m["midx"])].add(e)
        bygold[e].add(labels.get(m["midx"]))
    return {"files": len(byfile), "impure": sum(1 for v in byfile.values() if len(v) > 1),
            "gold_entities": len(bygold), "split": sum(1 for v in bygold.values() if len(v) > 1),
            "unmapped": unmapped}


# =====================================================================================================
# 4. ROW: THE PARTITION-ALGEBRA DECOMPOSITION OF THE ORACLE GAIN
# =====================================================================================================
def _refine(c):
    """R /\\ G -- the reader's files INTERSECTED with the gold partition: over-merges fixed, under-splits kept."""
    out = {}
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        lab = c["shipped_labels"].get(m["midx"])
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        out[m["midx"]] = "r%s_%s" % (lab, e)
    return out


def _coarsen(c):
    """R \\/ G -- the transitive closure of the reader's files WITH the gold partition: under-splits fixed,
    over-merges kept (a merged file drags both gold entities' other files in with it)."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        lab = ("F", c["shipped_labels"].get(m["midx"]))
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        find(lab)
        if e is not None:
            union(lab, ("G", e))
    return {m["midx"]: "c%s" % (find(("F", c["shipped_labels"].get(m["midx"]))),)
            for m in c["ms"] if not m.get("is_pronoun")}


def _oracle(c):
    out = {}
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        out[m["midx"]] = ("o%s" % e) if e is not None else ("own%s" % c["shipped_labels"].get(m["midx"]))
    return out


def _merge_causes(c):
    """WHICH CUE MERGED two gold entities into one file, counted -- the brief's error-type breakdown."""
    from hdlab.coref import name_content_tokens
    from hdlab.lexical_utils import head_lemma
    by = defaultdict(list)
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        if e is None:
            continue
        by[c["shipped_labels"].get(m["midx"])].append((m, e))
    cause = Counter()
    for lab, rows in by.items():
        if len({e for _m, e in rows}) <= 1:
            continue
        names = [m for m, _e in rows if name_content_tokens(m.get("span_toks", [m["head"]]),
                                                            upos=m.get("span_upos"))]
        heads = {head_lemma(m["head"]) for m, _e in rows}
        bridged = any(m["midx"] in c["bridge_binds"] for m, _e in rows)
        indef = any(_definiteness(m.get("span_toks", [m["head"]])) == "indefinite" for m, _e in rows)
        if bridged:
            cause["bridge_link"] += 1
        elif names and len({str(m["head"]).lower() for m in names}) == 1 and len(names) == len(rows):
            cause["name_same_surface"] += 1
        elif len(heads) == 1:
            cause["same_head_always_merge"] += 1
        else:
            cause["mixed"] += 1
        if indef:
            cause["_involves_an_indefinite"] += 1
    return cause


def _split_causes(c):
    """WHICH CUE WAS MISSING when one gold entity is spread over several files."""
    from hdlab.coref import name_content_tokens
    from hdlab.lexical_utils import head_lemma
    by = defaultdict(list)
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = c["gold"].get((m["sent_idx"], m["wtok_start"]))
        if e is None:
            continue
        by[e].append(m)
    cause = Counter()
    for e, rows in by.items():
        labs = {c["shipped_labels"].get(m["midx"]) for m in rows}
        if len(labs) <= 1:
            continue
        isname = [bool(name_content_tokens(m.get("span_toks", [m["head"]]), upos=m.get("span_upos")))
                  for m in rows]
        heads = {head_lemma(m["head"]) for m in rows}
        if all(isname):
            cause["name_alias_not_unified"] += 1
        elif any(isname) and not all(isname):
            cause["crosstype_name_vs_common"] += 1
        elif len(heads) > 1:
            cause["different_head_no_type_link"] += 1
        else:
            cause["same_head_phi_blocked"] += 1
    return cause


def row_decompose(n_docs=12, verbose=True, cap=None):
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    live = [[_score_q(q, c["live"].get((q["sent"], q["wpos"])))[1] for q in c["qs"]] for c in cap]
    arms = {"shipped": [c["shipped_labels"] for c in cap],
            "refine_fix_merges": [_refine(c) for c in cap],
            "coarsen_fix_splits": [_coarsen(c) for c in cap],
            "oracle": [_oracle(c) for c in cap]}
    rows, part, rows_pb = {}, {}, {}
    for name, labs in arms.items():
        rows[name] = [pick_rows(c, l) for c, l in zip(cap, labs)]
        rows_pb[name] = [pick_rows(c, l, principle_b=True) for c, l in zip(cap, labs)]
        pred, gold = [], []
        for c, l in zip(cap, labs):
            p, g = mention_partition(c, l)
            off = "%s|" % c["doc"]
            pred += [off + x for x in p]
            gold += [off + x for x in g]
        part[name] = partition_scores(pred, gold)
    if rows["shipped"] != live:
        raise AssertionError("the replayed `shipped` arm is NOT the live organ")
    pu = Counter()
    for c in cap:
        for k, v in purity(c, c["shipped_labels"]).items():
            pu[k] += v
    mc, sc = Counter(), Counter()
    for c in cap:
        mc += _merge_causes(c)
        sc += _split_causes(c)
    out = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap),
           "span_acc": {k: round(acc(v), 4) for k, v in rows.items()},
           "partition": part, "purity": dict(pu),
           "merge_causes": dict(mc), "split_causes": dict(sc), "contrasts": {}}
    out["span_acc_principle_b"] = {k: round(acc(v), 4) for k, v in rows_pb.items()}
    for k in ("refine_fix_merges", "coarsen_fix_splits", "oracle"):
        out["contrasts"]["%s_vs_shipped" % k] = paired_boot(rows["shipped"], rows[k])
        out["contrasts"]["%s_vs_shipped_PB" % k] = paired_boot(rows_pb["shipped"], rows_pb[k])
    out["contrasts"]["PB_vs_noPB_shipped"] = paired_boot(rows["shipped"], rows_pb["shipped"])
    out["contrasts"]["PB_vs_noPB_oracle"] = paired_boot(rows["oracle"], rows_pb["oracle"])
    if verbose:
        print("\n  THE ORACLE GAIN, DECOMPOSED BY PARTITION ALGEBRA (%d docs, %d questions)"
              % (out["n_docs"], out["n_questions"]))
        for k in ("shipped", "refine_fix_merges", "coarsen_fix_splits", "oracle"):
            b = out["contrasts"].get("%s_vs_shipped" % k)
            bp = out["contrasts"].get("%s_vs_shipped_PB" % k)
            print("    %-22s span %s | PrincipleB %s  B3 %s (P %s R %s)"
                  % (k, _p(out["span_acc"][k]), _p(out["span_acc_principle_b"][k]),
                     _p(part[k]["b3_f1"]), _p(part[k]["b3_p"]), _p(part[k]["b3_r"])))
            if b:
                print("        vs shipped  noPB d=%+.4f CI[%+.4f,%+.4f] sep=%-5s | PB d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                      % (b["delta"], b["ci"][0], b["ci"][1], b["sep"],
                         bp["delta"], bp["ci"][0], bp["ci"][1], bp["sep"]))
        print("    purity: %s" % json.dumps(out["purity"], sort_keys=True))
        print("    merge causes: %s" % json.dumps(out["merge_causes"], sort_keys=True))
        print("    split causes: %s" % json.dumps(out["split_causes"], sort_keys=True))
    return out, cap


# =====================================================================================================
# 5. ROW: BUILD THE VALIDITY ASSET FROM GUM TRAIN (offline supply; the teacher)
# =====================================================================================================
def build_validities(n_docs=24, verbose=True, out_path=None, cap=None, lemma="concept",
                     use_sents=True, cue_set="v1"):
    out_path = out_path or VALIDITY_ASSET
    """THE TEACHER: on GUM TRAIN documents (the EVEN doc indices -- the test split is [1::2] and is never
    read here), walk every non-pronoun mention in reading order, form the OPEN FILES as the gold partition
    of the mentions seen so far, and count each PAIRWISE cue value against SAME / DIFFERENT plus the
    MENTION-level criterion (did this mention open a new file?).  Those counts are the Competition Model's
    cue validities; the strengths are their log-odds.  A static, re-buildable offline asset."""
    from hdlab.coref import EntityAliaser, name_content_tokens
    from hdlab.lexical_utils import head_lemma, concept_lemma
    from hdlab.typed_spokes import available_entity_type
    lemma_fn = concept_lemma if lemma == "concept" else head_lemma
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose, split="train")
    V = Validities(cue_set=cue_set)
    have_spoke = available_entity_type()
    n_pairs = 0
    for c in cap:
        ms, gold, base = c["ms"], c["gold"], c["base_labels"]
        # the teacher's OPEN FILES are the GOLD partition, so the bridge's bind (a base-file id) has to be
        # expressed in gold-entity space: the gold entity of the mentions filed under that base id.
        gold_of_base = {}
        for mm in ms:
            if mm.get("is_pronoun"):
                continue
            bl = base.get(mm["midx"])
            ee = gold.get((mm["sent_idx"], mm["wtok_start"]))
            if bl is not None and ee is not None:
                gold_of_base.setdefault(int(bl), ee)
        files = {}
        aliaser = EntityAliaser()
        prev_cb, cur_sent, rank_in_sent = None, None, {}
        for order, m in enumerate(ms):
            if m.get("is_pronoun"):
                continue
            e = gold.get((m["sent_idx"], m["wtok_start"]))
            sent_idx = m.get("sent_idx", 0)
            if cur_sent is not None and sent_idx != cur_sent:
                row = sorted(rank_in_sent.get(cur_sent, {}).items(), key=lambda kv: kv[1])
                prev_cb = row[0][0] if row else prev_cb
            cur_sent = sent_idx
            rk = m.get("sent_role_rank", 99)
            role = "SUBJECT" if rk == 0 else ("OBJECT" if rk == 1 else "OTHER")
            span = m.get("span_toks", [m["head"]])
            head = lemma_fn(m["head"])
            gender = m.get("gender") or m.get("name_gender")
            number = m.get("number")
            surf = str(m["head"]).lower()
            wpos = int(m.get("wtok_start", -99))
            upos = (m.get("span_upos") or [""])[-1] or ""
            is_name = bool(name_content_tokens(span, upos=m.get("span_upos")))
            canon = aliaser.assign(span, gender, upos=m.get("span_upos")) if is_name else None
            definite = _definiteness(span, (c["sents"] if use_sents else None), sent_idx, wpos)
            link = None
            bl = (c.get("bridge_binds_repaired") or c["bridge_binds"]).get(m["midx"])
            if bl is not None:
                link = gold_of_base.get(bl)
            if e is None:
                continue
            for key, f in files.items():
                cu = file_cues(m, f, head=head, canon=canon, surf=surf, gender=gender, number=number,
                               definite=definite, is_name=is_name, sent_idx=sent_idx, prev_cb=prev_cb,
                               name_link=link, have_spoke=have_spoke, wpos=wpos, upos=upos,
                               sents=(c["sents"] if use_sents else None), cue_set=V.cue_set)
                V.observe(cu, key == e)
                n_pairs += 1
            # the CRITERION is counted per MENTION, not per pair: did this mention open a new file?
            V.observe_criterion(definite, e not in files)
            f = files.get(e)
            if f is None:
                f = OFile(e)
                files[e] = f
            f.update(order, role, gender, number, head, sent_idx, canon, surf, is_name, wpos=wpos,
                     upos=upos)
            rank_in_sent.setdefault(sent_idx, {}).setdefault(f.cid, rk)
    V.recompute()
    pth = V.save(out_path)
    if verbose:
        print("\n  wrote %s  (%d cue-file pairs counted on %d GUM TRAIN documents)"
              % (pth, n_pairs, len(cap)))
        for cu in CUES:
            print("    %-12s %s" % (cu, "  ".join("%s=%+.2f" % (v, V.strength[cu][v])
                                                  for v in V.values[cu])))
        print("    %-12s %s" % ("NOVELTY(tau)", "  ".join("%s=%+.2f" % (v, V.crit_shift[v])
                                                          for v in CRITERION_VALUES)))
    return {"n_docs": len(cap), "n_pairs": n_pairs, "path": pth,
            "cue_set": cue_set,
            "strength": {cu: {v: round(V.strength[cu][v], 4) for v in V.values[cu]} for cu in CUES},
            "criterion_shift": {v: round(V.crit_shift[v], 4) for v in CRITERION_VALUES}}


# =====================================================================================================
# 6. ROW: THE COMPETITION, MEASURED
# =====================================================================================================
def row_competition(n_docs=12, taus=(-8.0, -4.0, -2.0, 0.0, 2.0), verbose=True, cap=None, online=False,
                    split="test"):
    """THE TAU SWEEP.  Run it with split="train" to CHOOSE the operating point and with split="test" to
    report it -- the threshold is swept, never fitted on the population it is reported on."""
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose, split=split)
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    V = Validities.load()
    live = [[_score_q(q, c["live"].get((q["sent"], q["wpos"])))[1] for q in c["qs"]] for c in cap]
    ship_rows = [pick_rows(c, c["shipped_labels"]) for c in cap]
    if ship_rows != live:
        raise AssertionError("the replayed `shipped` arm is NOT the live organ")
    out = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap), "arms": {}, "contrasts": {},
           "shipped_span": round(acc(ship_rows), 4)}
    pred, gold = [], []
    ship_part_rows = []
    for c in cap:
        p, g = mention_partition(c, c["shipped_labels"])
        ship_part_rows.append((p, g))
        pred += ["%s|%s" % (c["doc"], x) for x in p]
        gold += ["%s|%s" % (c["doc"], x) for x in g]
    out["shipped_partition"] = partition_scores(pred, gold)
    best = None
    for tau in taus:
        for label, val in (("competition", V), ("competition_nosents", V),
                           ("competition_crudekey", V), ("twin", V.permuted())):
            if label != "competition" and best is not None and tau != best:
                continue
            rows, pr, gl, pu, part_rows = [], [], [], Counter(), []
            vv = Validities(counts=val.counts, crit_counts=val.crit, alpha=val.alpha) if online else val
            if online:
                vv.strength = {c: dict(v) for c, v in val.strength.items()}
                vv.crit_shift = dict(val.crit_shift)
            for c in cap:
                labs = competition_cluster(c["ms"], None, validities=vv, tau=tau,
                                           bridge_binds=(c.get("bridge_binds_repaired")
                                                         or c["bridge_binds"]), online=online,
                                           lemma=("crude" if label == "competition_crudekey"
                                                  else "concept"),
                                           sents=(None if label == "competition_nosents"
                                                  else c["sents"]))
                rows.append(pick_rows(c, labs))
                p, g = mention_partition(c, labs)
                part_rows.append((p, g))
                pr += ["%s|%s" % (c["doc"], x) for x in p]
                gl += ["%s|%s" % (c["doc"], x) for x in g]
                for k, v in purity(c, labs).items():
                    pu[k] += v
            key = "%s_tau%+g" % (label, tau)
            out["contrasts"]["%s_B3_vs_shipped" % key] = b3_boot(ship_part_rows, part_rows)
            out["arms"][key] = {"span_acc": round(acc(rows), 4), "partition": partition_scores(pr, gl),
                                "purity": dict(pu)}
            out["contrasts"]["%s_vs_shipped" % key] = paired_boot(ship_rows, rows)
            out["arms"][key]["rows"] = None
            if verbose:
                b = out["contrasts"]["%s_vs_shipped" % key]
                bb = out["contrasts"]["%s_B3_vs_shipped" % key]
                print("    %-26s span %s (d=%+.4f CI[%+.4f,%+.4f] sep=%-5s)  B3 %s P %s R %s "
                      "(dB3=%+.4f CI[%+.4f,%+.4f] sep=%s)  impure %d/%d"
                      % (key, _p(out["arms"][key]["span_acc"]), b["delta"], b["ci"][0], b["ci"][1], b["sep"],
                         _p(out["arms"][key]["partition"]["b3_f1"]),
                         _p(out["arms"][key]["partition"]["b3_p"]), _p(out["arms"][key]["partition"]["b3_r"]),
                         bb["delta"], bb["ci"][0], bb["ci"][1], bb["sep"], pu["impure"], pu["files"]))
            if label == "competition":
                if best is None or out["arms"][key]["partition"]["b3_f1"] > \
                        out["arms"]["competition_tau%+g" % best]["partition"]["b3_f1"]:
                    best = tau
    out["best_tau_by_b3"] = best
    if verbose:
        print("    shipped                span %s  B3 %s (P %s R %s)"
              % (_p(out["shipped_span"]), _p(out["shipped_partition"]["b3_f1"]),
                 _p(out["shipped_partition"]["b3_p"]), _p(out["shipped_partition"]["b3_r"])))
    return out, cap


# =====================================================================================================
# 5b. ROW: CUE REACH -- for every gold entity the reader SPLIT, does ANY cue in the set even reach it?
#     (the achievable ceiling of this cue set, measured BEFORE building on it: the wall-push "count, do
#     not narrate" move.  A cue that reaches nothing cannot be the lever however it is weighted.)
# =====================================================================================================
def row_cue_reach(n_docs=12, verbose=True, cap=None):
    from hdlab.coref import EntityAliaser, name_content_tokens
    from hdlab.lexical_utils import head_lemma
    from hdlab.typed_spokes import available_entity_type
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    have_spoke = available_entity_type()
    reach = Counter()
    tot = Counter()
    for c in cap:
        ms, gold = c["ms"], c["gold"]
        by = defaultdict(list)
        for m in ms:
            if m.get("is_pronoun"):
                continue
            e = gold.get((m["sent_idx"], m["wtok_start"]))
            if e is not None:
                by[e].append(m)
        aliaser = EntityAliaser()
        canon_of = {}
        for m in ms:
            if m.get("is_pronoun"):
                continue
            span = m.get("span_toks", [m["head"]])
            if name_content_tokens(span, upos=m.get("span_upos")):
                canon_of[m["midx"]] = aliaser.assign(span, m.get("gender") or m.get("name_gender"),
                                                     upos=m.get("span_upos"))
        for e, rows in by.items():
            labs = {c["shipped_labels"].get(m["midx"]) for m in rows}
            if len(labs) <= 1:
                continue
            tot["split_gold_entities"] += 1
            # for EVERY pair of mentions the reader put in DIFFERENT files, which cue would link them?
            hit = set()
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    a, b = rows[i], rows[j]
                    if c["shipped_labels"].get(a["midx"]) == c["shipped_labels"].get(b["midx"]):
                        continue
                    ha, hb = head_lemma(a["head"]), head_lemma(b["head"])
                    na = bool(name_content_tokens(a.get("span_toks", [a["head"]]), upos=a.get("span_upos")))
                    nb = bool(name_content_tokens(b.get("span_toks", [b["head"]]), upos=b.get("span_upos")))
                    ca, cb = canon_of.get(a["midx"]), canon_of.get(b["midx"])
                    if ca is not None and ca == cb:
                        hit.add("name_canon")
                    if ha == hb:
                        hit.add("head_lemma")
                    elif _isa_compatible(ha, {hb}):
                        hit.add("head_isa")
                    if na != nb:
                        nm = a if na else b
                        an = b if na else a
                        if _etype_cue(head_lemma(an["head"]), {str(nm["head"]).lower()},
                                      have_spoke) == "licensed":
                            hit.add("etype")
                    rb = c.get("bridge_binds_repaired") or c["bridge_binds"]
                    if a["midx"] in rb or b["midx"] in rb:
                        hit.add("predication_repaired_bridge")
                    if a["sent_idx"] == b["sent_idx"] and abs(int(a["wtok_start"]) - int(b["wtok_start"])) <= 2:
                        hit.add("np_nominal_run")
            for k in hit:
                reach[k] += 1
            if not hit:
                reach["NO_CUE_REACHES_IT"] += 1
    out = {"n_docs": len(cap), "split_gold_entities": tot["split_gold_entities"], "reached_by": dict(reach)}
    if verbose:
        print("  CUE REACH over the %d gold entities the reader SPLIT:" % tot["split_gold_entities"])
        for k, v in sorted(reach.items(), key=lambda kv: -kv[1]):
            print("    %-22s %4d  (%.1f%%)" % (k, v, 100.0 * v / max(1, tot["split_gold_entities"])))
    return out


# =====================================================================================================
# 6a. ROW: THE CONSUMER REPAIR -- does the pick's ANTECEDENT READOUT have to change to receive the
#     richer files?  (owner 2026-09-12: a downstream regression after a brain-foundational upstream is
#     not failure -- keep the rung ON and repair the consumer.)
# =====================================================================================================
def row_readout(n_docs=12, tau=0.0, verbose=True, cap=None):
    """The landed pick answers with `last_nom[k]` -- the chosen file's MOST RECENT non-pronoun mention.
    That is right for a head-bucket and wrong for a FILE: the introduction organ opens a referent on
    VERB- and ADV-headed tokens too, so a real object file's most recent mention is often not its head.
    The HEAD-PREFERRING readout asks the same chosen file for its most recent NOUN/PROPN mention instead.
    Nothing else changes -- same clustering, same winner, same questions -- and on the SHIPPED files it is
    an identity (their most recent mention is already the head), so the arm cannot win for free."""
    import hdlab.coref as CO
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load()

    def run(c, labels):
        ms = _apply_labels(c["ms"], labels)
        tg = CO.discovered_pronoun_targets(ms, window=0)
        recs, _ab = CO.graded_pronoun_resolve(ms, tg, window=0)
        seq = sorted([m for m in ms if not m.get("is_pronoun")],
                     key=lambda m: (m["sent_idx"], m["wtok_start"]))
        a_recent, a_head = {}, {}
        for r in recs:
            k = (r["sent_idx"], r["target_wpos"])
            a_recent[k] = {"head": r["resolved_head"], "span": r["antecedent_span"]}
            ent, sp = r.get("resolved_entity"), r["antecedent_span"]
            if ent is not None:
                prior = [m for m in seq
                         if (m["sent_idx"], m["wtok_start"]) < k and m.get("cluster") == ent]
                noms = [m for m in prior if (m.get("span_upos") or [""])[-1] in ("NOUN", "PROPN")]
                pick = noms or prior
                if pick:
                    m = pick[-1]
                    sp = (m["sent_idx"], m["wtok_start"], m["wtok_start"])
            a_head[k] = {"head": r["resolved_head"], "span": sp}
        return a_recent, a_head

    rows = {k: [] for k in ("shipped_recent", "shipped_head", "competition_recent", "competition_head")}
    for c in cap:
        comp = competition_cluster(c["ms"], None, validities=V, tau=tau,
                                   bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]),
                                   sents=c["sents"])
        for tag, L in (("shipped", c["shipped_labels"]), ("competition", comp)):
            ar, ah = run(c, L)
            rows[tag + "_recent"].append([_score_q(q, ar.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
            rows[tag + "_head"].append([_score_q(q, ah.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
    out = {"n_docs": len(cap), "tau": tau, "n_questions": sum(len(c["qs"]) for c in cap),
           "span_acc": {k: round(acc(v), 4) for k, v in rows.items()}, "contrasts": {}}
    for a, b in (("shipped_recent", "shipped_head"), ("shipped_recent", "competition_recent"),
                 ("shipped_recent", "competition_head"), ("competition_recent", "competition_head")):
        out["contrasts"]["%s_vs_%s" % (b, a)] = paired_boot(rows[a], rows[b])
    if verbose:
        for k, v in out["span_acc"].items():
            print("    %-20s span %s" % (k, _p(v)))
        for k, v in out["contrasts"].items():
            print("      %-42s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                  % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return out, cap


# =====================================================================================================
# 6a2. ROW: IS THE CONSUMER'S OPERATING POINT STALE?  pri 131 swept the pick's cue weights over the
#      HEAD-BUCKET files and found the shipped point best THERE.  Real object files are bigger (more
#      history -> more ACT-R base-level), so the balance between the base-level and the agreement cue is
#      a different balance.  Sweep the PICK over the competition's files, the same grid, one code path.
# =====================================================================================================
def row_picksweep(n_docs=28, tau=0.0, verbose=True, cap=None):
    import hdlab.coref as CO
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load()
    labs_of = {}
    for c in cap:
        labs_of[c["doc"]] = competition_cluster(
            c["ms"], None, validities=V, tau=tau, sents=c["sents"],
            bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]))

    def score(labels_of_doc, cfg, head_readout):
        rows = []
        for c in cap:
            ms = _apply_labels(c["ms"], labels_of_doc(c))
            tg = CO.discovered_pronoun_targets(ms, window=cfg.get("window", 0))
            recs, _ab = CO.graded_pronoun_resolve(
                ms, tg, window=cfg.get("window", 0), w_gender=cfg.get("w_gender", 4.0),
                w_number=cfg.get("w_number", 0.0), w_focus=cfg.get("w_focus", 1.0),
                decay=cfg.get("decay", 2.0))
            seq = sorted([m for m in ms if not m.get("is_pronoun")],
                         key=lambda m: (m["sent_idx"], m["wtok_start"]))
            ans = {}
            for r in recs:
                k = (r["sent_idx"], r["target_wpos"])
                sp = r["antecedent_span"]
                ent = r.get("resolved_entity")
                if head_readout and ent is not None:
                    prior = [m for m in seq
                             if (m["sent_idx"], m["wtok_start"]) < k and m.get("cluster") == ent]
                    noms = [m for m in prior if (m.get("span_upos") or [""])[-1] in ("NOUN", "PROPN")]
                    pick = noms or prior
                    if pick:
                        m = pick[-1]
                        sp = (m["sent_idx"], m["wtok_start"], m["wtok_start"])
                ans[k] = {"head": r["resolved_head"], "span": sp}
            rows.append([_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        return rows

    base = score(lambda c: c["shipped_labels"], {}, False)
    out = {"n_docs": len(cap), "tau": tau, "n_questions": sum(len(c["qs"]) for c in cap),
           "shipped_default": round(acc(base), 4), "grid": []}
    grid = [{}]
    grid += [{"w_gender": g} for g in (8.0, 16.0, 32.0)]
    grid += [{"w_focus": f} for f in (0.0, 4.0)]
    grid += [{"decay": d} for d in (3.0, 4.0)]
    grid += [{"window": w} for w in (2, 4)]
    grid += [{"w_gender": 16.0, "decay": 3.0}, {"w_gender": 16.0, "w_focus": 0.0}]
    for cfg in grid:
        rows = score(lambda c: labs_of[c["doc"]], cfg, True)
        b = paired_boot(base, rows)
        out["grid"].append({"cfg": cfg, "span_acc": round(acc(rows), 4), "vs_shipped_default": b})
        if verbose:
            print("    %-34s span %s  d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                  % (json.dumps(cfg, sort_keys=True), _p(round(acc(rows), 4)),
                     b["delta"], b["ci"][0], b["ci"][1], b["sep"]))
    if verbose:
        print("    shipped organ at its own default: %s" % _p(out["shipped_default"]))
    return out, cap


# =====================================================================================================
# 7. PHASE 7 -- the flip audit (A), the joint phase diagram (C) and Principle B (D)
# =====================================================================================================
def _answers_from(ms, recs, readout):
    """The pick's answers under one ANTECEDENT READOUT.

      False / "recent"  the landed organ: the chosen file's MOST RECENT non-pronoun mention (`last_nom[k]`)
      True  / "head"    its most recent NOUN/PROPN mention (the first consumer repair)
              "actr"    the file's MOST ACCESSIBLE record -- argmax of the PINNED per-presentation ACT-R
                        term w(role) * (t_now - t_k)^(-d) over the file's own mentions (Anderson & Schooler;
                        object-file reviewing re-accesses a file at its most available record, not at
                        whatever token came last).  Role prominence is imported, never re-implemented.
    """
    from hdlab.salience_binder import ROLE_PROMINENCE, DEFAULT_DECAY
    if readout is True:
        readout = "head"
    elif readout is False:
        readout = "recent"
    seq = sorted([m for m in ms if not m.get("is_pronoun")],
                 key=lambda m: (m["sent_idx"], m["wtok_start"]))
    order_of = {(m["sent_idx"], m["wtok_start"]): float(m["midx"]) for m in seq}
    out = {}
    for r in recs:
        k = (r["sent_idx"], r["target_wpos"])
        sp, ent = r["antecedent_span"], r.get("resolved_entity")
        if readout != "recent" and ent is not None:
            prior = [m for m in seq if (m["sent_idx"], m["wtok_start"]) < k and m.get("cluster") == ent]
            if readout == "head":
                noms = [m for m in prior if (m.get("span_upos") or [""])[-1] in ("NOUN", "PROPN")]
                pick = (noms or prior)[-1:]
            else:
                now = max((order_of.get((m["sent_idx"], m["wtok_start"]), 0.0) for m in prior),
                          default=0.0) + 1.0
                best, bs = None, -1e18
                for m in prior:
                    rk = m.get("sent_role_rank", 99)
                    role = "SUBJECT" if rk == 0 else ("OBJECT" if rk == 1 else "OTHER")
                    t = max(now - order_of.get((m["sent_idx"], m["wtok_start"]), 0.0), 1e-6)
                    a = ROLE_PROMINENCE.get(role, 1.0) * (t ** (-DEFAULT_DECAY))
                    if (m.get("span_upos") or [""])[-1] in ("NOUN", "PROPN"):
                        a *= 2.0          # a nominal record IS the file's head; swept as a single factor
                    if a > bs:
                        best, bs = m, a
                pick = [best] if best is not None else []
            if pick:
                mm = pick[-1]
                sp = (mm["sent_idx"], mm["wtok_start"], mm["wtok_start"])
        out[k] = {"head": r["resolved_head"], "span": sp, "entity": ent}
    return out


def _run_pick(c, labels, readout, cfg=None, coarg=None):
    import hdlab.coref as CO
    cfg = cfg or {}
    ms = _apply_labels(c["ms"], labels)
    tg = CO.discovered_pronoun_targets(ms, window=cfg.get("window", 0))
    recs, _ab = CO.graded_pronoun_resolve(
        ms, tg, window=cfg.get("window", 0), w_gender=cfg.get("w_gender", 4.0),
        w_number=cfg.get("w_number", 0.0), w_focus=cfg.get("w_focus", 1.0),
        decay=cfg.get("decay", 2.0), coarg=coarg)
    return ms, _answers_from(ms, recs, readout)


def row_flips(n_docs=28, tau=0.0, verbose=True, cap=None):
    """(A) EVERY FLIP, ITEM BY ITEM, WITH THE DECISION THAT CAUSED IT.  For each question that the shipped
    organ answers right and the competition answers wrong (and the reverse), find the clustering decision
    responsible: the gold antecedent mention the shipped pick used, the file the competition put it in, and
    -- from the competition's own decision TRACE -- which cue value carried that decision and what validity
    it had.  Then group the causes."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load()
    causes = Counter()
    kinds = Counter()
    rows_s, rows_c, items = [], [], []
    for c in cap:
        tr = []
        comp = competition_cluster(c["ms"], None, validities=V, tau=tau, sents=c["sents"],
                                   bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]),
                                   trace=tr)
        tr_by = {t["midx"]: t for t in tr}
        ms_s, a_s = _run_pick(c, c["shipped_labels"], False)
        ms_c, a_c = _run_pick(c, comp, True)
        by_pos = {(m["sent_idx"], m["wtok_start"]): m for m in c["ms"] if not m.get("is_pronoun")}
        gold_span_of = c.get("gold_span", {})
        sv, cv = [], []
        for q in c["qs"]:
            k = (q["sent"], q["wpos"])
            s1 = _score_q(q, a_s.get(k))[1]
            s2 = _score_q(q, a_c.get(k))[1]
            sv.append(s1)
            cv.append(s2)
            if s1 == s2:
                continue
            lost = bool(s1 and not s2)
            kinds["right_to_wrong" if lost else "wrong_to_right"] += 1
            if not lost:
                continue
            # the mention the SHIPPED pick used (a correct antecedent) and where the competition filed it
            sp = (a_s.get(k) or {}).get("span")
            m_true = by_pos.get((sp[0], sp[1])) if sp else None
            sp2 = (a_c.get(k) or {}).get("span")
            m_got = by_pos.get((sp2[0], sp2[1])) if sp2 else None
            cause, cue, val = "unclassified", None, None
            if m_true is None:
                cause = "no_shipped_antecedent_mention"
            else:
                f_true = comp.get(m_true["midx"])
                f_got = comp.get(m_got["midx"]) if m_got is not None else None
                t = tr_by.get(m_true["midx"])
                if f_got is not None and f_true == f_got:
                    # same file -- the competition chose the RIGHT file and the readout took another member
                    cause = "readout_same_file_other_member"
                elif t is not None and not t["opened"] and t.get("cues"):
                    # the true antecedent was MERGED into some file by a cue; which one carried it?
                    cu = t["cues"]
                    w = sorted(((V.w(cc, vv), cc, vv) for cc, vv in cu.items()), reverse=True)
                    val, cue, cuev = w[0][0], w[0][1], w[0][2]
                    cause = "merge_swallowed_the_antecedent:%s=%s" % (cue, cuev)
                elif t is not None and t["opened"]:
                    cause = "split_hid_the_antecedent_new_file"
                else:
                    cause = "competition_picked_a_different_file"
            causes[cause] += 1
            if len(items) < 60:
                items.append({"doc": c["doc"], "sent": q["sent"], "form": q["form"], "cause": cause,
                              "cue": cue, "validity": (None if val is None else round(val, 3)),
                              "shipped_span": sp, "competition_span": sp2})
        rows_s.append(sv)
        rows_c.append(cv)
    grouped = Counter()
    for k, v in causes.items():
        if k.startswith("merge_swallowed"):
            cue = k.split(":")[1].split("=")[0]
            grouped["(i/ii) a merge carried by cue `%s`" % cue] += v
        elif k == "readout_same_file_other_member":
            grouped["(iv) consumer readout: right file, wrong member"] += v
        elif k == "split_hid_the_antecedent_new_file":
            grouped["(ii) a split opened a new file for the antecedent"] += v
        else:
            grouped["(other) %s" % k] += v
    out = {"n_docs": len(cap), "tau": tau, "n_questions": sum(len(c["qs"]) for c in cap),
           "shipped_span": round(acc(rows_s), 4), "competition_head_span": round(acc(rows_c), 4),
           "flips": dict(kinds), "causes": dict(causes), "grouped": dict(grouped),
           "contrast": paired_boot(rows_s, rows_c), "items": items}
    if verbose:
        print("  shipped %s -> competition+readout %s   flips: %s"
              % (_p(out["shipped_span"]), _p(out["competition_head_span"]), json.dumps(dict(kinds))))
        for k, v in sorted(grouped.items(), key=lambda kv: -kv[1]):
            print("    %-56s %4d" % (k, v))
        for it in items[:10]:
            print("      %-22s s%-3d %-6s %-46s cue=%s w=%s"
                  % (it["doc"][:22], it["sent"], it["form"], it["cause"][:46], it["cue"], it["validity"]))
    return out, cap


def row_grid(n_docs=28, verbose=True, cap=None):
    """(C) THE JOINT PHASE DIAGRAM: the ACT-R retrieval threshold `tau` x the ONLINE ACCRUAL RATE (the
    margin above which the reader treats its own decision as confirmed and counts it).  Both rows at every
    point: the entity partition (B-cubed, paired bootstrap over documents) and the pronoun instrument with
    the head-preferring readout.  The operating point is free to move."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V0 = Validities.load()
    ship_rows, ship_part = [], []
    for c in cap:
        _ms, a = _run_pick(c, c["shipped_labels"], False)
        ship_rows.append([_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
        ship_part.append(mention_partition(c, c["shipped_labels"]))
    out = {"n_docs": len(cap), "n_questions": sum(len(c["qs"]) for c in cap),
           "shipped_span": round(acc(ship_rows), 4),
           "shipped_b3": pooled_partition(ship_part)["b3_f1"],
           "grid": []}
    grid = [(t, m) for t in (0.0, 1.0, 2.0) for m in (None, 2.0, 1.0)]
    for tau, margin in grid:
        rows, part = [], []
        Vx = V0
        if margin is not None:
            # ONE plastic table walked across the whole test set, exactly as a reader would
            Vx = Validities(counts=V0.counts, crit_counts=V0.crit, alpha=V0.alpha)
        for c in cap:
            labs = competition_cluster(
                c["ms"], None, validities=Vx, tau=tau, sents=c["sents"],
                bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]),
                online=(margin is not None), online_margin=(margin or 2.0))
            _ms, a = _run_pick(c, labs, True)
            rows.append([_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
            part.append(mention_partition(c, labs))
        b = paired_boot(ship_rows, rows)
        bb = b3_boot(ship_part, part)
        rec = {"tau": tau, "accrual_margin": margin, "span_acc": round(acc(rows), 4),
               "b3_f1": pooled_partition(part)["b3_f1"],
               "span_vs_shipped": b, "b3_vs_shipped": bb}
        out["grid"].append(rec)
        if verbose:
            print("    tau %+5.1f accrual %-5s  span %s (d=%+.4f CI[%+.4f,%+.4f] sep=%-5s)  B3 %s "
                  "(d=%+.4f CI[%+.4f,%+.4f] sep=%s)"
                  % (tau, ("off" if margin is None else margin), _p(rec["span_acc"]), b["delta"],
                     b["ci"][0], b["ci"][1], b["sep"], _p(rec["b3_f1"]), bb["delta"], bb["ci"][0],
                     bb["ci"][1], bb["sep"]))
    ok = [g for g in out["grid"] if not g["span_vs_shipped"]["sep"] and g["b3_vs_shipped"]["sep"]
          and g["b3_vs_shipped"]["delta"] > 0]
    out["points_with_b3_up_and_span_not_down"] = [
        {"tau": g["tau"], "accrual_margin": g["accrual_margin"], "span": g["span_acc"], "b3": g["b3_f1"]}
        for g in ok]
    if verbose:
        print("    shipped span %s  B3 %s" % (_p(out["shipped_span"]), _p(out["shipped_b3"])))
        print("    points with B3 CI-sep UP and the pronoun row NOT CI-sep down: %s"
              % json.dumps(out["points_with_b3_up_and_span_not_down"]))
    return out, cap


def row_principleb(n_docs=28, tau=0.0, verbose=True, cap=None):
    """(D) PRINCIPLE B over the LANDED competition.  The flag `situation_reader.pronoun_principle_b`
    (:1044) ships False; pri 131 measured the exclusion through the reader's OWN ~0.57-UAS parse at
    -0.0152 n.s. and through the TREEBANK parse at +0.0203, and named the flip condition: 'when the
    attachment rung improves'.  pri 133 LANDED tonight (infinitival heads +0.0979 CI-sep, UAS up), so the
    reason is re-testable.  Four arms, one code path: {shipped, competition} x {Principle B off, on}."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load()
    rows = {k: [] for k in ("shipped_off", "shipped_on", "competition_off", "competition_on")}
    for c in cap:
        comp = competition_cluster(c["ms"], None, validities=V, tau=tau, sents=c["sents"],
                                   bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]))
        for tag, labs, hr in (("shipped", c["shipped_labels"], False), ("competition", comp, True)):
            for pb in (False, True):
                _ms, a = _run_pick(c, labs, hr, coarg=(c.get("coarg") if pb else None))
                rows["%s_%s" % (tag, "on" if pb else "off")].append(
                    [_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
    out = {"n_docs": len(cap), "tau": tau, "n_questions": sum(len(c["qs"]) for c in cap),
           "span_acc": {k: round(acc(v), 4) for k, v in rows.items()}, "contrasts": {}}
    for a, b in (("shipped_off", "shipped_on"), ("competition_off", "competition_on"),
                 ("shipped_off", "competition_on")):
        out["contrasts"]["%s_vs_%s" % (b, a)] = paired_boot(rows[a], rows[b])
    if verbose:
        for k, v in out["span_acc"].items():
            print("    %-18s span %s" % (k, _p(v)))
        for k, v in out["contrasts"].items():
            print("      %-42s d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                  % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out, cap


# =====================================================================================================
# 7a2. THE QUALITY PUSH the flip audit named: (i) the flat `np` validity (21 of 72 losses) becomes
#      CONFIGURATION-CONDITIONED, and (iv) the antecedent readout (32 of 72) becomes the PINNED ACT-R
#      accessibility argmax instead of "the most recent nominal".
# =====================================================================================================
def _entity_scored(c, labels, ms, ans):
    """SCORE THE PICK BY IDENTITY, NOT BY SPAN.  The brain returns a FILE; the span scorer demands a
    surface record, so a correct file answered at a non-head token scores wrong.  Here the answer is the
    picked file's MAJORITY gold entity (which penalises an impure merge, so it is not a free pass), and the
    question is the target's own gold entity.  ABSTENTION = WRONG, same 795 questions."""
    gold = c["gold"]
    maj = defaultdict(Counter)
    for m in ms:
        if m.get("is_pronoun"):
            continue
        e = gold.get((m["sent_idx"], m["wtok_start"]))
        if e is not None:
            maj[m.get("cluster")][e] += 1
    best = {f: cnt.most_common(1)[0][0] for f, cnt in maj.items() if cnt}
    out = []
    for q in c["qs"]:
        a = ans.get((q["sent"], q["wpos"])) or {}
        ent = a.get("entity")
        out.append(int(ent is not None and best.get(ent) == q["eid"]))
    return out


def row_push(n_docs=28, tau=0.0, verbose=True, cap=None, asset=None):
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load(asset)
    rows, part = {}, {}
    ship = []
    for c in cap:
        _ms, a = _run_pick(c, c["shipped_labels"], "recent")
        ship.append([_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
    rows["shipped"] = ship
    part["shipped"] = [mention_partition(c, c["shipped_labels"]) for c in cap]
    ent = {"shipped": []}
    for c in cap:
        ms, a = _run_pick(c, c["shipped_labels"], "recent")
        ent["shipped"].append(_entity_scored(c, c["shipped_labels"], ms, a))
    comp = {}
    for c in cap:
        comp[c["doc"]] = competition_cluster(
            c["ms"], None, validities=V, tau=tau, sents=c["sents"],
            bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]))
    for ro in ("recent", "head", "actr"):
        r, e = [], []
        for c in cap:
            ms, a = _run_pick(c, comp[c["doc"]], ro)
            r.append([_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in c["qs"]])
            if ro == "recent":
                e.append(_entity_scored(c, comp[c["doc"]], ms, a))
        rows["competition_%s" % ro] = r
        if ro == "recent":
            ent["competition"] = e
        part["competition_%s" % ro] = [mention_partition(c, comp[c["doc"]]) for c in cap]
    out = {"n_docs": len(cap), "tau": tau, "asset": asset or VALIDITY_ASSET,
           "n_questions": sum(len(c["qs"]) for c in cap),
           "span_acc": {k: round(acc(v), 4) for k, v in rows.items()},
           "b3": {k: pooled_partition(part[k])["b3_f1"] for k in part},
           "contrasts": {}}
    for k in ("competition_recent", "competition_head", "competition_actr"):
        out["contrasts"]["%s_vs_shipped_span" % k] = paired_boot(rows["shipped"], rows[k])
    out["contrasts"]["b3_vs_shipped"] = b3_boot(part["shipped"], part["competition_recent"])
    out["entity_scored"] = {k: round(acc(v), 4) for k, v in ent.items()}
    out["contrasts"]["entity_scored_competition_vs_shipped"] = paired_boot(ent["shipped"],
                                                                          ent["competition"])
    if verbose:
        for k in ("shipped", "competition_recent", "competition_head", "competition_actr"):
            print("    %-22s span %s  B3 %s" % (k, _p(out["span_acc"][k]), _p(out["b3"][k])))
        print("    SCORED BY IDENTITY (the picked file's majority gold entity, abstention = wrong): "
              "shipped %s -> competition %s"
              % (_p(out["entity_scored"]["shipped"]), _p(out["entity_scored"]["competition"])))
        for k, v in out["contrasts"].items():
            print("      %-42s d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                  % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out, cap


# =====================================================================================================
# 7b. (B) THE NP-SPAN REPAIR, MEASURED -- the upstream defect at hdlab/referent_per_np.py:111-115 + :194
# =====================================================================================================
def np_spans(sents, mention_wpos):
    """Group the introduction organ's CONTENT-HEAD TOKENS into NPs using the reader's OWN parse: a mention
    token that is a PRE-HEAD dependent of another mention token in the same sentence belongs to that
    token's nominal (the attachment arm's head + its dependents), and the surviving head is the RIGHTMOST
    member -- Williams 1981's Right-Hand Head Rule for English compounds.  Post-head dependents are NOT
    swallowed (the prior work's `boundary_nphead` finding: the head is the nominal BEFORE post-modification).
    Returns {sent_idx: {head_wpos: (start_wpos, end_wpos, [member wpos...])}}."""
    from hdlab import frontend as F
    tg, pr = F.tagger(), F.parser()
    out = {}
    for si, toks in enumerate(sents):
        want = sorted(mention_wpos.get(si, ()))
        if not want:
            continue
        pos = tg.tag(list(toks))
        heads = pr.parse(list(toks), pos).heads          # 1-based child -> head, 0 = root
        parent = {}
        for w in want:
            h = int(heads.get(w + 1, 0)) - 1              # back to 0-based
            parent[w] = h if (h in mention_wpos.get(si, ())) else None
        grp = {}
        for w in want:
            root, seen = w, set()
            while parent.get(root) is not None and parent[root] > root and root not in seen:
                seen.add(root)
                root = parent[root]                      # follow PRE-head dependency only (parent to the right)
            grp.setdefault(root, []).append(w)
        out[si] = {}
        for h, members in grp.items():
            members = sorted(members)
            lo, hi = members[0], h
            if lo > 0 and str(toks[lo - 1]).lower() in (_DEF_DET | _INDEF_DET):
                lo -= 1                                  # the determiner IS part of the NP (Heim's condition)
            out[si][h] = (lo, hi, members)
    return out


def row_npspan(n_docs=28, tau=0.0, verbose=True, cap=None):
    """(B) WHAT A SPAN REPAIR BUYS.  The introduction organ opens ONE referent per CONTENT-NOUN TOKEN
    (`hdlab/referent_per_np.py:111-115 _content_head_positions`) and stores `span_toks=[head_low]`
    (`:194`, and `gtok_start/gtok_end = -1` at `:192`).  Rebuild the mention stream as ONE mention per NP
    and measure the four things that defect blocks, plus both rows."""
    from experiments.exp_pronoun_pick_identity_contract_v1 import _score_q
    from hdlab.entity_resolver import EntityResolver
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    V = Validities.load()
    tot = Counter()
    rows = {k: [] for k in ("shipped", "shipped_npspan", "competition", "competition_npspan")}
    part = {k: [] for k in rows}
    for c in cap:
        by_sent = defaultdict(set)
        for m in c["ms"]:
            if not m.get("is_pronoun"):
                by_sent[m["sent_idx"]].add(int(m["wtok_start"]))
        spans = np_spans(c["sents"], by_sent)
        # ---- the repaired mention stream: one mention per NP, headed by the right-hand head ----
        keep, absorbed = {}, {}
        for si, d in spans.items():
            for h, (lo, hi, members) in d.items():
                keep[(si, h)] = (lo, hi)
                for w in members:
                    absorbed[(si, w)] = (si, h)
        ms2 = []
        for m in c["ms"]:
            k = (m["sent_idx"], int(m["wtok_start"]))
            if m.get("is_pronoun"):
                ms2.append(dict(m))
                continue
            if k in keep:
                m2 = dict(m)
                lo, hi = keep[k]
                m2["span_toks"] = [str(t).lower() for t in c["sents"][m["sent_idx"]][lo:hi + 1]]
                ms2.append(m2)
                tot["mentions_after"] += 1
            else:
                tot["mentions_absorbed"] += 1
            tot["mentions_before"] += 1
        c2 = dict(c)
        c2["ms"] = _finalize_midx(ms2)
        # ---- (1) the determiner read ----
        for m in c2["ms"]:
            if m.get("is_pronoun"):
                continue
            tot["def_read_after" if _definiteness(m["span_toks"]) != "bare" else "def_bare_after"] += 1
        for m in c["ms"]:
            if m.get("is_pronoun"):
                continue
            tot["def_read_before" if _definiteness(m["span_toks"]) != "bare" else "def_bare_before"] += 1
        # ---- (2) the bridge's binds ----
        base2 = EntityResolver().cluster(c2["ms"], gaz=None)
        c2["base_labels"] = base2
        b2 = repaired_bridge_binds(c2["ms"], base2, c2["sents"], None, _gaz())
        c2["bridge_binds_repaired"] = b2
        c2["bridge_binds"] = {}
        tot["bridge_binds_after"] += len(b2)
        tot["bridge_binds_before"] += len(c.get("bridge_binds_repaired") or {})
        # ---- (3) the same-gold-span cross-file pair count, and (4) both rows ----
        ship2 = {m["midx"]: base2.get(m["midx"]) for m in c2["ms"] if not m.get("is_pronoun")}
        comp = competition_cluster(c["ms"], None, validities=V, tau=tau, sents=c["sents"],
                                   bridge_binds=(c.get("bridge_binds_repaired") or c["bridge_binds"]))
        comp2 = competition_cluster(c2["ms"], None, validities=V, tau=tau, sents=c2["sents"],
                                    bridge_binds=b2)
        for tag, cc, labs, hr in (("shipped", c, c["shipped_labels"], False),
                                  ("shipped_npspan", c2, ship2, False),
                                  ("competition", c, comp, True),
                                  ("competition_npspan", c2, comp2, True)):
            _ms, a = _run_pick(cc, labs, hr)
            rows[tag].append([_score_q(q, a.get((q["sent"], q["wpos"])))[1] for q in cc["qs"]])
            part[tag].append(mention_partition(cc, labs))
            tot["pairs_same_gold_span_%s" % tag] += _same_span_pairs(cc, labs)
    out = {"n_docs": len(cap), "tau": tau, "counts": dict(tot),
           "span_acc": {k: round(acc(v), 4) for k, v in rows.items()},
           "b3": {k: pooled_partition(part[k]) for k in part},
           "contrasts": {}}
    for a, b in (("shipped", "shipped_npspan"), ("competition", "competition_npspan"),
                 ("shipped", "competition_npspan")):
        out["contrasts"]["%s_vs_%s_span" % (b, a)] = paired_boot(rows[a], rows[b])
        out["contrasts"]["%s_vs_%s_b3" % (b, a)] = b3_boot(part[a], part[b])
    if verbose:
        print("    mentions %d -> %d (%d absorbed into an NP)"
              % (tot["mentions_before"], tot["mentions_after"], tot["mentions_absorbed"]))
        print("    determiner readable on %d of %d mentions -> %d of %d"
              % (tot["def_read_before"], tot["def_read_before"] + tot["def_bare_before"],
                 tot["def_read_after"], tot["def_read_after"] + tot["def_bare_after"]))
        print("    crosstype bridge binds %d -> %d" % (tot["bridge_binds_before"], tot["bridge_binds_after"]))
        for k in ("shipped", "shipped_npspan", "competition", "competition_npspan"):
            print("    %-22s span %s  B3 %s (P %s R %s)  same-gold-span cross-file pairs %d"
                  % (k, _p(out["span_acc"][k]), _p(out["b3"][k]["b3_f1"]), _p(out["b3"][k]["b3_p"]),
                     _p(out["b3"][k]["b3_r"]), tot["pairs_same_gold_span_%s" % k]))
        for k, v in out["contrasts"].items():
            if v:
                print("      %-46s d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out, cap


_GOLD_SPANS = {}


def gold_span_map(docid):
    """(sent_idx, wtok) -> the GOLD mention span (start_g, end_g) it falls in -- the answer key only, used
    to COUNT how many of the reader's splits are inside one gold mention."""
    if not _GOLD_SPANS:
        import experiments.gum_coref as G
        for d in G.load_docs(gum_only=True, decision_source="gold"):
            by_sent = defaultdict(list)
            for t in d.toks:
                by_sent[t.sent].append(t)
            pos = {}
            for si in sorted(by_sent):
                for w, t in enumerate(sorted(by_sent[si], key=lambda x: x.idx)):
                    pos[t.gidx] = (si, w)
            m = {}
            for men in d.mentions:
                for g in range(men.start_g, men.end_g + 1):
                    if g in pos:
                        m.setdefault(pos[g], (men.start_g, men.end_g))
            _GOLD_SPANS[str(d.docid)] = m
    return _GOLD_SPANS.get(str(docid), {})


_GAZ = [None]


def _gaz():
    if _GAZ[0] is None:
        from hdlab.coref import load_name_gender
        _GAZ[0] = load_name_gender()
    return _GAZ[0]


def _finalize_midx(ms):
    """Re-number midx in reading order exactly as `referent_per_np._finalize` does, and recompute the
    per-sentence grammatical-role rank, so every consumer behaves identically on the rebuilt stream."""
    ms = sorted(ms, key=lambda m: (m["sent_idx"], m["wtok_start"]))
    for i, m in enumerate(ms):
        m["midx"] = i
    by = defaultdict(list)
    for m in ms:
        by[m["sent_idx"]].append(m)
    for _si, lst in by.items():
        for rank, m in enumerate(sorted(lst, key=lambda mm: (mm["wtok_start"], mm["midx"]))):
            m["sent_role_rank"] = rank
    return ms


def _same_span_pairs(c, labels):
    """Mention pairs of ONE gold entity that sit in DIFFERENT reader files AND inside one gold mention
    span -- the count the NP-span defect owns."""
    gold = c["gold"]
    byg = defaultdict(list)
    for m in c["ms"]:
        if m.get("is_pronoun"):
            continue
        e = gold.get((m["sent_idx"], m["wtok_start"]))
        if e is not None:
            byg[e].append(m)
    n = 0
    gs = gold_span_map(c["doc"])
    for _e, rws in byg.items():
        for i in range(len(rws)):
            for j in range(i + 1, len(rws)):
                a, b = rws[i], rws[j]
                if labels.get(a["midx"]) == labels.get(b["midx"]):
                    continue
                sa = gs.get((a["sent_idx"], a["wtok_start"]))
                sb = gs.get((b["sent_idx"], b["wtok_start"]))
                if sa is not None and sa == sb:
                    n += 1
    return n


# =====================================================================================================
# 7c. (E) THE ONLINE PATH -- the validities accrue DURING a read, across documents
# =====================================================================================================
def row_online(n_docs=28, tau=0.0, margin=2.0, verbose=True, cap=None):
    """(E) NOTHING FROZEN, DEMONSTRATED.  One plastic table is carried across two documents: the first
    document's HIGH-MARGIN decisions are accrued into the counts (`observe_file_decision`), the strengths
    are recomputed from those counts, and the SECOND document is then clustered with the updated table.
    The control is the same second document clustered with the table as it was BEFORE document one."""
    cap = cap if cap is not None else capture_cached(n_docs, verbose=verbose)
    c1, c2 = cap[0], cap[1]
    V0 = Validities.load()
    before = {cu: dict(V0.strength[cu]) for cu in CUES}
    crit_before = dict(V0.crit_shift)
    Vp = Validities(counts=V0.counts, crit_counts=V0.crit, alpha=V0.alpha)
    competition_cluster(c1["ms"], None, validities=Vp, tau=tau, sents=c1["sents"],
                        bridge_binds=(c1.get("bridge_binds_repaired") or c1["bridge_binds"]),
                        online=True, online_margin=margin)
    moved = {cu: {v: round(Vp.strength[cu][v] - before[cu][v], 4) for v in Vp.values[cu]
                  if abs(Vp.strength[cu][v] - before[cu][v]) > 1e-9} for cu in CUES}
    moved = {k: v for k, v in moved.items() if v}
    crit_moved = {v: round(Vp.crit_shift[v] - crit_before[v], 4) for v in CRITERION_VALUES
                  if abs(Vp.crit_shift[v] - crit_before[v]) > 1e-9}
    frozen = competition_cluster(c2["ms"], None, validities=V0, tau=tau, sents=c2["sents"],
                                 bridge_binds=(c2.get("bridge_binds_repaired") or c2["bridge_binds"]))
    plastic = competition_cluster(c2["ms"], None, validities=Vp, tau=tau, sents=c2["sents"],
                                  bridge_binds=(c2.get("bridge_binds_repaired") or c2["bridge_binds"]))
    diff = sum(1 for k in frozen if frozen[k] != plastic[k])
    nfiles = (len(set(frozen.values())), len(set(plastic.values())))
    pf, gf = mention_partition(c2, frozen)
    pp, gp = mention_partition(c2, plastic)
    out = {"doc_taught_on": c1["doc"], "doc_read_after": c2["doc"], "accrual_margin": margin, "tau": tau,
           "pairs_accrued": int(sum(sum(x) for cu in CUES for x in Vp.counts[cu].values())
                                - sum(sum(x) for cu in CUES for x in V0.counts[cu].values())),
           "strength_moved": moved, "criterion_moved": crit_moved,
           "second_doc_mentions_filed_differently": diff,
           "second_doc_files_frozen_vs_plastic": nfiles,
           "second_doc_b3": {"frozen": partition_scores(pf, gf)["b3_f1"],
                             "plastic": partition_scores(pp, gp)["b3_f1"]}}
    if verbose:
        print("    taught on %s, then read %s" % (out["doc_taught_on"], out["doc_read_after"]))
        print("    cue-value observations accrued during the first read: %d" % out["pairs_accrued"])
        print("    strengths that MOVED: %s" % json.dumps(moved, sort_keys=True))
        print("    criterion that MOVED: %s" % json.dumps(crit_moved, sort_keys=True))
        print("    second document: %d mentions filed differently by the updated table; files %s -> %s; "
              "B3 %s -> %s" % (diff, nfiles[0], nfiles[1], _p(out["second_doc_b3"]["frozen"]),
                               _p(out["second_doc_b3"]["plastic"])))
    return out, cap


# =====================================================================================================
# 6b. ROW: THE LIVE A/B -- the competition INSTALLED as the organ, every consumer measured in ONE process
# =====================================================================================================
class installed(object):
    """Install the proposed organ by rebinding EXACTLY the attribute the diff changes
    (`EntityResolver.cluster`) for the duration of the block -- so the comparison is CODE vs CODE in one
    process, not run vs run.  `twin` installs the permuted-validity version (information-free)."""

    def __init__(self, name, tau=0.0, online=False, sents=True):
        self.name = name
        self.tau = tau
        self.online = online
        self.sents = bool(sents)
        self._saved = None
        self._saved_pcs = None

    def __enter__(self):
        import hdlab.entity_resolver as ER
        import hdlab.situation_reader as SR
        if self.name == "shipped":
            return self
        V = Validities.load()
        if self.name == "twin":
            V = V.permuted()
        self._saved = ER.EntityResolver.cluster
        tau, online, use_sents = self.tau, self.online, self.sents
        box = {"sents": None}

        # THE ONE-LINE CALL-SITE CHANGE, STOOD IN FOR EXACTLY.  `cluster` takes an OPTIONAL `sents`; the
        # live call site (`situation_reader.read`, the online_entity_cluster block) does not pass it today,
        # and without it Heim's definiteness is unreadable (every mention is `bare`).  Rather than edit
        # situation_reader.py -- which this brief may not touch -- the arm intercepts the SAME
        # `parse_conll_sentences(conll_path, lower=False)` value the call site already holds two lines
        # above, so the organ receives byte-identically what `sents=sents` would hand it.
        self._saved_pcs = SR.parse_conll_sentences

        def _pcs(path, *a, **kw):
            out = self._saved_pcs(path, *a, **kw)
            if not kw.get("lower", True):
                box["sents"] = out
            return out

        def _cluster(inner, ms, gaz, **kw):
            return competition_cluster(ms, gaz, validities=V, tau=tau, online=online,
                                       sents=(box["sents"] if use_sents else None))
        if use_sents:
            SR.parse_conll_sentences = _pcs
        ER.EntityResolver.cluster = _cluster
        return self

    def __exit__(self, *exc):
        import hdlab.entity_resolver as ER
        import hdlab.situation_reader as SR
        if self._saved is not None:
            ER.EntityResolver.cluster = self._saved
        if getattr(self, "_saved_pcs", None) is not None:
            SR.parse_conll_sentences = self._saved_pcs
        return False


def row_live(n_docs=12, tau=0.0, arms=("shipped", "competition", "twin"), verbose=True, online=False):
    """THE LIVE A/B: read each GUM document with the organ INSTALLED, so the pronoun instrument, the
    common-noun resolution consumer and the entity layer are all measured through the real read().  Both
    arms in ONE process; the SHIPPED arm is restored by rebinding the exact attribute the diff touches."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    import experiments.gum_coref as G
    from experiments.exp_pronoun_pick_identity_contract_v1 import (gum_questions, _answers, _score_q,
                                                                   _gold_eid_at)
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    pool = G.load_docs(gum_only=True, decision_source="gold")[1::2]
    step = max(1, len(pool) // max(1, n_docs))
    docs = [pool[i] for i in range(0, len(pool), step)][:n_docs]
    prepared = []
    for d in docs:
        pth = P.gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        prepared.append((d, pth, gum_questions(d), _gold_eid_at(d)))
    out = {"n_docs": len(prepared), "tau": tau, "online": bool(online),
           "n_questions": sum(len(q) for _d, _p2, q, _g in prepared), "arms": {}, "contrasts": {}}
    rows, cnrows = {}, {}
    for a in arms:
        sp, cn, part_p, part_g, pu = [], [], [], [], Counter()
        t0 = time.time()
        with installed(a, tau=tau, online=online):
            for d, pth, qs, gold in prepared:
                rd = SituationReader()
                sm = rd.read(pth)
                ms = list(getattr(rd, "_coref_mentions", []) or [])
                ans = _answers(sm, ms)
                sp.append([_score_q(q, ans.get((q["sent"], q["wpos"])))[1] for q in qs])
                # THE COMMON-NOUN RESOLUTION CONSUMER (sm.commonnoun_resolution): a resolved referent is
                # CORRECT when the resolved mention's gold entity matches the anaphor's own gold entity.
                bymidx = {m["midx"]: m for m in ms}
                own = {}
                for r in (getattr(sm, "commonnoun_resolution", None) or []):
                    m = bymidx.get(r["midx"])
                    if m is None:
                        continue
                    own[r["own_ref"]] = gold.get((m["sent_idx"], m["wtok_start"]))
                v = []
                for r in (getattr(sm, "commonnoun_resolution", None) or []):
                    m = bymidx.get(r["midx"])
                    if m is None or r.get("resolved_ref") is None:
                        continue
                    ge = gold.get((m["sent_idx"], m["wtok_start"]))
                    if ge is None:
                        continue
                    v.append(int(own.get(r["resolved_ref"]) == ge))
                cn.append(v)
                c = {"ms": ms, "gold": gold}
                labs = {m["midx"]: m.get("cluster") for m in ms if not m.get("is_pronoun")}
                pp, gg = mention_partition(c, labs)
                part_p += ["%s|%s" % (d.docid, x) for x in pp]
                part_g += ["%s|%s" % (d.docid, x) for x in gg]
                for k, vv in purity(c, labs).items():
                    pu[k] += vv
        rows[a] = sp
        cnrows[a] = cn
        out["arms"][a] = {"span_acc": round(acc(sp), 4), "commonnoun_res_acc": round(acc(cn), 4),
                          "commonnoun_n": sum(len(x) for x in cn),
                          "partition": partition_scores(part_p, part_g), "purity": dict(pu),
                          "secs": round(time.time() - t0, 1)}
        if verbose:
            o = out["arms"][a]
            print("    %-12s span %s  commonnoun %s (n=%d)  B3 %s (P %s R %s)  impure %d/%d  %.0fs"
                  % (a, _p(o["span_acc"]), _p(o["commonnoun_res_acc"]), o["commonnoun_n"],
                     _p(o["partition"]["b3_f1"]), _p(o["partition"]["b3_p"]), _p(o["partition"]["b3_r"]),
                     pu["impure"], pu["files"], o["secs"]))
    for a in arms:
        if a != "shipped" and "shipped" in rows:
            out["contrasts"]["%s_vs_shipped_span" % a] = paired_boot(rows["shipped"], rows[a])
            out["contrasts"]["%s_vs_shipped_commonnoun" % a] = paired_boot(cnrows["shipped"], cnrows[a])
        if a != "twin" and "twin" in rows:
            out["contrasts"]["%s_vs_twin_span" % a] = paired_boot(rows["twin"], rows[a])
    if verbose:
        for k, v in out["contrasts"].items():
            if v:
                print("      %-34s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return out


def row_noregress(n_docs=10, tau=0.0, verbose=True):
    """NO-REGRESS on the OTHER consumers of the entity layer: UD-EWT agent / patient / state through the
    live reader, the organ installed, both arms in ONE process."""
    import experiments.exp_pronoun_referent_discovery_v1 as P
    from hdlab.situation_reader import SituationReader
    docs = P.load_ud_docs()[:n_docs]
    out = {"n_docs": len(docs), "tau": tau, "arms": {}}
    rows = {}
    for a in ("shipped", "competition"):
        per = {"agent": [], "patient": [], "state": []}
        with installed(a, tau=tau):
            for _docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                pth = P.write_conll(sents)
                try:
                    sm = SituationReader().read(pth)
                finally:
                    try:
                        os.unlink(pth)
                    except OSError:
                        pass
                sc = P.score_doc(sm, gold)
                for k in per:
                    per[k].append(sc.get(k, []))
        rows[a] = per
        out["arms"][a] = {k: round(acc(v), 4) for k, v in per.items()}
        if verbose:
            print("  %-12s %s" % (a, json.dumps(out["arms"][a], sort_keys=True)))
    out["contrasts"] = {k: paired_boot(rows["shipped"][k], rows["competition"][k])
                        for k in ("agent", "patient", "state")}
    if verbose:
        for k, v in out["contrasts"].items():
            if v:
                print("    %-10s d=%+.4f CI[%+.4f,%+.4f] sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["sep"]))
    return out


# =====================================================================================================
# 7. SELF-TEST (corpus-free)
# =====================================================================================================
def self_test(verbose=True):
    fails = []
    # S1 the metrics agree with the substrate's own implementation
    try:
        import experiments.exp_commonnoun_coref_diagnostic_v1 as D
        a = ["A", "A", "B", "B"]
        g = ["x", "x", "y", "z"]
        ok = (round(b3(a, g)[2], 6) == round(D.b3(a, g)[2], 6)
              and round(ceafe(a, g)[2], 6) == round(D.ceafe(a, g)[2], 6))
    except Exception as ex:
        ok = False
        print("  metric cross-check unavailable: %r" % (ex,))
    print("  %s S1 B3/CEAFe reproduce the substrate's own implementation" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("S1")
    # S2 the validity strengths ARE log-odds of the counts, and permuting destroys the information
    V = Validities()
    V.counts["head"]["lemma_match"] = [90.0, 5.0]
    V.counts["head"]["mismatch"] = [5.0, 90.0]
    V.recompute()
    ok2 = V.w("head", "lemma_match") > 1.5 > 0 > V.w("head", "mismatch")
    tw = V.permuted(seed=1)
    ok2b = sorted(round(x, 6) for x in tw.strength["head"].values()) == \
        sorted(round(x, 6) for x in V.strength["head"].values())
    print("  %s S2 strengths are log-odds (match %+.2f > 0 > mismatch %+.2f); the twin keeps the numbers, "
          "permutes the values" % ("PASS" if ok2 and ok2b else "FAIL",
                                   V.w("head", "lemma_match"), V.w("head", "mismatch")))
    if not (ok2 and ok2b):
        fails.append("S2")
    # S3 THE CAN-FAIL CONTROL the shipped organ fails: two same-head referents stay TWO files, and an
    #    indefinite re-introduction opens a new one (Heim), while the shipped organ merges both.
    ms = [
        {"midx": 0, "head": "doctor", "span_toks": ["a", "doctor"], "is_pronoun": False, "sent_idx": 0,
         "sent_role_rank": 0, "gender": None, "number": "singular", "cluster": 1},
        {"midx": 1, "head": "doctor", "span_toks": ["a", "doctor"], "is_pronoun": False, "sent_idx": 1,
         "sent_role_rank": 0, "gender": None, "number": "singular", "cluster": 2},
        {"midx": 2, "head": "doctor", "span_toks": ["the", "doctor"], "is_pronoun": False, "sent_idx": 2,
         "sent_role_rank": 0, "gender": None, "number": "singular", "cluster": 2},
    ]
    V2 = Validities()
    V2.counts["head"]["lemma_match"] = [90.0, 5.0]
    V2.counts["head"]["mismatch"] = [5.0, 90.0]
    V2.crit["indefinite"] = [5.0, 95.0]      # an indefinite almost always OPENS a file (Heim)
    V2.crit["definite"] = [80.0, 20.0]       # a definite almost always re-accesses one
    V2.crit["bare"] = [50.0, 50.0]
    V2.recompute()
    from hdlab.entity_resolver import EntityResolver
    shipped = EntityResolver().cluster(ms, gaz=None)
    labs = [(t, competition_cluster(ms, None, validities=V2, tau=t)) for t in (-4.0, -2.0, 0.0, 2.0, 4.0)]
    hit = [(t, l) for t, l in labs if l[0] != l[1] and l[1] == l[2]]
    ok3 = bool(hit) and (shipped[0] == shipped[1] == shipped[2])
    print("  %s S3 Heim novelty: SOME operating point opens a NEW file for the 2nd INDEFINITE and "
          "re-accesses on the DEFINITE %s; the shipped organ merges all three %s"
          % ("PASS" if ok3 else "FAIL", hit[:1] or labs, shipped))
    if not ok3:
        fails.append("S3")
    # S4 the observe path moves a strength (nothing frozen)
    V3 = Validities()
    before = V3.w("phi", "agree")
    for _ in range(50):
        observe_file_decision(V3, {"phi": "agree"}, True)
    for _ in range(50):
        observe_file_decision(V3, {"phi": "conflict"}, False)
    ok4 = V3.w("phi", "agree") > before
    print("  %s S4 the observe path moves the validity (agree %+.3f -> %+.3f)"
          % ("PASS" if ok4 else "FAIL", before, V3.w("phi", "agree")))
    if not ok4:
        fails.append("S4")
    # S5 the partition algebra: refine >= shipped and coarsen >= shipped on a toy
    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return {"fails": fails, "green": not fails}


# =====================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--decompose", type=int, default=0)
    ap.add_argument("--competition", type=int, default=0)
    ap.add_argument("--build-validities", type=int, default=0, dest="build_validities")
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--live", type=int, default=0)
    ap.add_argument("--noregress", type=int, default=0)
    ap.add_argument("--tau", type=float, default=0.0)
    ap.add_argument("--cue-reach", type=int, default=0, dest="cue_reach")
    ap.add_argument("--tune", type=int, default=0)
    ap.add_argument("--readout", type=int, default=0)
    ap.add_argument("--picksweep", type=int, default=0)
    ap.add_argument("--flips", type=int, default=0)
    ap.add_argument("--grid", type=int, default=0)
    ap.add_argument("--principleb", type=int, default=0)
    ap.add_argument("--npspan", type=int, default=0)
    ap.add_argument("--push", type=int, default=0)
    ap.add_argument("--asset", type=str, default=None)
    ap.add_argument("--cue-set", type=str, default="v1", dest="cue_set")
    ap.add_argument("--online-path", type=int, default=0, dest="online_path")
    ap.add_argument("--taus", type=str, default="-8,-4,-2,0,2")
    a = ap.parse_args()
    res = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": SEED}
    cap = None
    if a.self_test:
        res["self_test"] = self_test()
    if a.build_validities:
        print("\n== THE TEACHER: cue validities from GUM TRAIN gold partitions ==")
        res["build_validities"] = build_validities(a.build_validities, out_path=a.asset,
                                                   cue_set=a.cue_set)
    if a.decompose:
        print("\n== THE ORACLE GAIN, DECOMPOSED (refine / coarsen / oracle) ==")
        res["decompose"], cap = row_decompose(a.decompose, cap=cap)
    if a.cue_reach:
        print("\n== CUE REACH (can any cue even link what the reader split?) ==")
        res["cue_reach"] = row_cue_reach(a.cue_reach, cap=cap)
    if a.tune:
        print("\n== THE TAU SWEEP ON THE TRAIN SPLIT (choose the operating point here, report on test) ==")
        res["tune"], _ = row_competition(a.tune, cap=None, split="train",
                                         taus=tuple(float(x) for x in a.taus.split(",")))
    if a.competition:
        print("\n== THE OBJECT-FILE COMPETITION ==")
        res["competition"], cap = row_competition(a.competition, cap=cap,
                                                  taus=tuple(float(x) for x in a.taus.split(",")),
                                                  online=a.online)
    if a.readout:
        print("\n== THE CONSUMER REPAIR: the pick's ANTECEDENT READOUT ==")
        res["readout"], cap = row_readout(a.readout, tau=a.tau, cap=cap)
    if a.picksweep:
        print("\n== IS THE PICK'S OPERATING POINT STALE FOR REAL OBJECT FILES? ==")
        res["picksweep"], cap = row_picksweep(a.picksweep, tau=a.tau, cap=cap)
    if a.flips:
        print("\n== (A) EVERY FLIP, WITH THE CLUSTERING DECISION THAT CAUSED IT ==")
        res["flips"], cap = row_flips(a.flips, tau=a.tau, cap=cap)
    if a.principleb:
        print("\n== (D) PRINCIPLE B OVER THE LANDED COMPETITION ==")
        res["principleb"], cap = row_principleb(a.principleb, tau=a.tau, cap=cap)
    if a.push:
        print("\n== THE QUALITY PUSH: configuration-conditioned `np` + the ACT-R accessibility readout ==")
        res["push"], cap = row_push(a.push, tau=a.tau, cap=cap, asset=a.asset)
    if a.npspan:
        print("\n== (B) THE NP-SPAN REPAIR AT THE INTRODUCTION ORGAN ==")
        res["npspan"], cap = row_npspan(a.npspan, tau=a.tau, cap=cap)
    if a.online_path:
        print("\n== (E) THE ONLINE PATH: the validities accrue DURING a read, across documents ==")
        res["online_path"], cap = row_online(a.online_path, tau=a.tau, cap=cap)
    if a.grid:
        print("\n== (C) THE JOINT PHASE DIAGRAM: retrieval threshold x online accrual rate ==")
        res["grid"], cap = row_grid(a.grid, cap=cap)
    if a.live:
        print("\n== THE LIVE A/B (the organ installed; every consumer measured) ==")
        res["live"] = row_live(a.live, tau=a.tau, online=a.online)
    if a.noregress:
        print("\n== NO-REGRESS (UD-EWT agent / patient / state) ==")
        res["noregress"] = row_noregress(a.noregress, tau=a.tau)
    if len(res) > 2:
        p = os.path.join(OUT_DIR, "metrics_%s.json" % "_".join(
            k for k in ("self_test", "build_validities", "decompose", "cue_reach", "tune",
                        "competition", "readout", "picksweep", "flips", "principleb", "npspan",
                        "online_path", "push", "grid", "live", "noregress") if k in res))
        with io.open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps(res, indent=2, sort_keys=True, default=str))
        print("\nwrote %s" % p)


if __name__ == "__main__":
    main()
