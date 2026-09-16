"""hdlab/entity_resolver.py -- ONE cue-based `entity_resolver`: a single ACT-R content-addressable
retrieval CORE with pluggable, MENTION-TYPE-ROUTED cue-arms, SUBSUMING the six live coreference resolvers.

LANDED 2026-09-11 (owner-DONE consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver, Q111):
promoted VERBATIM (byte-identical behavior) from experiments/exp_entity_resolver_unified_v1.EntityResolver. The
reader's four default-on coref entry points route through this ONE organ: online_entity_cluster.online_cluster ->
`cluster`, crosstype_live_adapter's bridge -> `bridge_links`, world_state_entity_binding.EntityBinder ->
`new_stage1_binder`, situation_reader._resolve_commonnouns -> `resolve_commonnouns`. Proven byte-identical by
verification/test_entity_resolver_{unified,typed_commonnoun,reader_substitution}.py (12/12 + 2/2 + 3/3). The BF
lexical helpers this organ needs are imported from hdlab.lexical_utils (split out of the NOT_BF commonnoun_binder).

============================================================================================================
BRAIN-FOUNDATIONAL THESIS (what one structure, replicating or substituting?)
============================================================================================================
PINNED-BY-EVIDENCE. Antecedent/reference resolution is ONE content-addressable, cue-based retrieval mechanism
(Lewis & Vasishth 2005; Parker, Shvartsman & Van Dyke: "binding in comprehension is mediated by a
content-addressable memory system"). A memory chunk's retrieval strength is its ACT-R activation
    A_i = B_i(base-level: recency x frequency x role-prominence)  +  sum_cue W_cue * match_cue(i)
and the anaphor RETRIEVES the argmax. B_i is `hdlab.salience_binder.actr_activation` -- and CRUCIALLY every one
of the six organs ALREADY calls that ONE function for the base term. So the retrieval MATH is not fragmented;
the WRAPPERS are (each organ re-implements the same "assemble candidates by a cue, score by ACT-R activation,
pick argmax under a write/abstain policy" loop with a different cue set + write policy + I/O schema).

PINNED-BY-EVIDENCE, and it is why a NAIVE "one resolver, one cue" merge is WRONG (measured, refuted on disk:
form_the_unified_discourse_referent -> common nouns REGRESS, twin beats it; route_the_unified_referent ->
C2 -0.0089, C3 -0.0780). Ariel 1990 Accessibility Hierarchy: the CUE SET is mention-type-specific --
    PRONOUN (high accessibility)     -> phi-agreement + base-level salience/prominence
    DEFINITE COMMON (low access.)    -> type-compatibility + recency (a NON-writing bridge; salience is wrong)
    DEFINITE -> NAME                 -> in-text descriptive PREDICATION + confidence (Almor desc-content boost)
    NAME                             -> identity (given-name aliasing)
    INDEXICAL (I/me/my)              -> O(1) deixis to the NARRATOR origo (Buehler) -- NOT retrieval at all
So the correct consolidation is exactly "ONE STRUCTURE WITH ARMS": one retrieval CORE, and a MENTION-TYPE ROUTER
that selects the cue-arm set per Ariel. That removes the fragmentation WITHOUT re-committing the refuted merge.

KEEP-SEPARATE (audit, respected here): SALIENCE (salience_binder / event_centrality_coref = the base-level B_i
term) and DRT REFERENT CONSTRUCTION (referent_per_np) are UPSTREAM of retrieval, not the retrieval step. This
module IMPORTS actr_activation; it never re-implements it.

WHAT IS GENUINELY DISTINCT (located negatives, kept as ROUTING arms / cue-PRODUCERS, not retrieval cue-arms):
  * The INDEXICAL/PLEONASTIC dispatch (world_state_entity_binding) is deixis + expletive detection -- an O(1)
    speech-role lookup, NOT O(n) content-addressable search. It ROUTES anaphoric cases INTO the core; it is a
    routing arm, not a cue-arm.
  * The PRECISE-CONSTRUCTS predication detector (crosstype_bridge) is in-text relation EXTRACTION over UD syntax
    -- a cue-PRODUCER feeding the definite->name arm's descriptive-content license, not a retrieval itself.

============================================================================================================
WHAT THIS CELL PROVES (Q111: proposal + proof, not a landing)
============================================================================================================
`EntityResolver` below owns ONE retrieval core (`_retrieve`) + ONE write-policy engine + the Ariel router, and
exposes the SAME entry points the six organs expose, each a declarative arm config. The witnesses
(verification/test_entity_resolver_unified.py) prove -- on real GUM mentions -- that the unified core reproduces
the LIVE-wired resolvers BYTE-IDENTICALLY:
  * `cluster(ms, gaz)`            == hdlab.online_entity_cluster.online_cluster          (sm.entities producer)
  * `bridge_links(doc, gaz, ...)` == hdlab.crosstype_bridge.crosstype_bridge_links       (definite->name bridge)
  * `bind_participant`/`bind_theme` == hdlab.world_state_entity_binding.EntityBinder      (world-state Stage-1)
  * `typed_common_pick(...)`      == the typed_coref common/pronoun retrieval step (shared core)

Glass-box, CPU, nltk-WordNet only, NO external LLM at inference. Self-contained hdlab imports (the shared
primitives the organs already share); ZERO experiments/ imports at module load.
"""
from __future__ import annotations

__bf_status__ = "BF_SPIRIT"   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = "2026-09-11 consolidation landing (strategy first-hand; byte-identical port of the owner-DONE unified organ)"
__bf_note__ = ("ONE ACT-R content-addressable retrieval CORE (salience_binder.actr_activation base-level, PINNED) + the "
               "Ariel Accessibility mention-type ROUTER over pluggable cue-arms (type / name-bridge / morphosyntactic / "
               "KB-prior). Composes pinned math under one dispatcher; the single SHARED deviation is the HARD phi/type "
               "FILTER-then-rank vs L&V GRADED parallel cue-combination -- now single-point (a separate behavior-changing "
               "problem: strengthen_the_cue_based_pronoun_coreference_resolver). No NEW convenience stand-in introduced.")
__bf_corrections__ = []

import io
import json
import math
import os
import random
from collections import Counter, defaultdict
from typing import Callable, Dict, List, Optional, Sequence, Tuple

# -- the SHARED primitives every organ already calls (the retrieval math + cues live here; not re-implemented) --
from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE, DEFAULT_DECAY
from hdlab.coref import EntityAliaser, name_content_tokens
from hdlab.state_of_mind import compatible
from hdlab.lexical_utils import head_lemma, person_synset   # BF lexical foundation (split from the NOT_BF commonnoun_binder)
import hdlab.typed_spokes as TS


NEG_INF = -1e9   # the finite floor every organ substitutes for actr_activation's -inf (empty history)

# ==========================================================================================================
# THE OBJECT-FILE MERGE/SPLIT DECISION AS ONE CUE COMPETITION  (pri 136)
# ----------------------------------------------------------------------------------------------------------
# A new mention either UPDATES an open file or OPENS a new one -- Heim (1982) file-change semantics'
# Novelty-Familiarity Condition and Kahneman & Treisman (1992) object files.  The decision is a GRADED match
# of the mention's features against the open files, not a string coincidence:
#
#   A(f) = B_i(f)  +  SUM_c w_c[value_c(m, f)]        ACT-R base-level + parallel cue evidence, SUMMED
#   update argmax A if max A >= tau + lambda(definiteness); else OPEN A NEW FILE
#
# B_i is PINNED (salience_binder.actr_activation, imported -- never re-implemented).  The additive cue
# weight is PINNED IN FORM as the log-likelihood ratio (Anderson & Milson 1989 rational analysis: the
# associative strength S_ji is the log posterior odds), and those probabilities are COUNTS -- the
# Competition Model's cue validity (MacWhinney & Bates 1989), accrued offline from GUM TRAIN partitions and
# ONLINE from the reader's own high-margin decisions (`observe_file_decision`; nothing frozen).  This is the
# SINGLE SHARED MATHEMATICAL GAP the brain-foundational audit names for this organ -- the hard phi/type
# FILTER-then-rank replaced by graded Lewis-Vasishth cue combination, with the -P*mismatch interference term
# LEARNED (a conflicting cue value simply gets a negative log-odds) rather than hand-set.
# tau (the ACT-R retrieval threshold) and the accrual margin are OUR-INVENTION: SWEPT, never adopted.
# ==========================================================================================================

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


# THE OPERATING POINT (phase diagram): tau is the ACT-R retrieval threshold, SWEPT on the GUM TRAIN split
# and reported on TEST -- never fitted on the population it is reported on.  +2.0 is the swept point at
# which the partition improves and no consumer regresses; tau=0.0 maximises partition quality and costs the
# pronoun row (both numbers are in the SOLVED).
OBJECT_FILE_TAU = 0.0   # 2026-09-16 landing (strategy): pri 136's joint grid -- tau=0 + accrual margin 1.0 = partition
#   +0.0745 CI[+0.0431,+0.1031] CI-sep, pronoun span row -0.0302 n.s. (the solver shipped 2.0 as the conservative default)

# PLASTIC, NEVER FROZEN.  The reader counts its OWN high-margin merge/split decisions as it reads and the
# strengths are recomputed from the grown counts (`observe_file_decision`); the batch fit from GUM TRAIN is
# only the starting equilibrium.  MEASURED (28 GUM test documents, 795 questions): at tau 0 the frozen
# table gives B-cubed +0.0680 CI-sep with the pronoun row CI-separated DOWN, and the PLASTIC table gives
# +0.0745 CI-sep with the pronoun row NOT separated down -- plasticity improves the organ's own metric AND
# removes the consumer regression.  Set HDLAB_OBJECT_FILE_ONLINE=0 to freeze the table (which makes a read
# order-independent, for a byte-identical A/B).
OBJECT_FILE_ONLINE_MARGIN = 1.0

OBJECT_FILE_VALIDITY_ASSET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "frontend_assets",
    "object_file_validities_gum_v1.json")
VALIDITY_ASSET = OBJECT_FILE_VALIDITY_ASSET   # the name Validities.load/save resolve at call time
_OF_VALIDITIES = None


def object_file_validities(path=None):
    """The learned merge/split cue validities (a static, re-buildable offline asset; counts -> log-odds).
    Returns None when the asset is absent -> `cluster` falls back to the pre-competition arm."""
    global _OF_VALIDITIES
    if path is None and _OF_VALIDITIES is not None:
        return _OF_VALIDITIES
    p = path or OBJECT_FILE_VALIDITY_ASSET
    if not os.path.exists(p):
        return None
    v = Validities.load(p)
    if path is None:
        _OF_VALIDITIES = v
    return v



# ==========================================================================================================
# THE ONE RETRIEVAL CORE  --  content-addressable, cue-based, ACT-R-scored argmax under a write policy.
# ==========================================================================================================
def _base_activation(history, now, decay, role_prominence) -> float:
    """B_i = ACT-R base-level activation (salience_binder), with the organs' shared -inf -> -1e9 floor."""
    a = actr_activation(history, float(now), decay, role_prominence)
    return a if a != float("-inf") else NEG_INF


def retrieve(files: Sequence, now: float, *,
             license: Callable, bonus: Optional[Callable] = None,
             decay: float = DEFAULT_DECAY, role_prominence: Optional[Dict[str, float]] = None,
             policy: str = "argmax", threshold: float = 0.0, margin: float = 0.0,
             abstain_below: Optional[Callable] = None, key_of: Optional[Callable] = None,
             score_of: Optional[Callable] = None,
             history_of: Callable = lambda f: f.history) -> Tuple[Optional[object], list, list]:
    """THE ONE content-addressable cue-based retrieval used by every resolver arm.

    * candidate set  = the files a cue LICENSES (parallel cue match; hard phi/type filter -- see the FIDELITY
      note in the module docstring: L&V is graded cue-combination, our organs hard-filter; that deviation is
      SHARED by all six and is preserved here so a future graded upgrade is single-point).
    * activation     = base-level B_i (ACT-R) + optional cue BONUS (e.g. Almor descriptive-content boost).
    * pick           = argmax, under a WRITE POLICY:
        'argmax'  : take the top (always-merge; online_entity_cluster default).
        'hold'    : Nieuwland hold-under-uncertainty -- merge only if top >= threshold AND it dominates the
                    runner-up by `margin` (else return None -> caller opens a new file).
        'compete' : Heim/DRT full-referent competition -- take the top only if it dominates by `margin`; an
                    `abstain_below(top_score)` predicate can veto (McElree low-activation = novel -> abstain).
    Returns (picked_file_or_None, licensed_files, activations) -- the caller does the write/open bookkeeping."""
    cands = [f for f in files if license(f)]
    if not cands:
        return None, [], []
    acts = []
    for f in cands:
        # base score: ACT-R base-level (default) OR a caller-supplied selector (e.g. pure RECENCY for a definite's
        # same-head incumbent -- Ariel: low-accessibility markers retrieve by recency, a special case of base-level).
        a = score_of(f) if score_of is not None else _base_activation(history_of(f), now, decay, role_prominence)
        if bonus is not None:
            a += bonus(f)
        acts.append(a)
    # primary key = activation (desc); optional secondary tie-break key (e.g. crosstype breaks A-ties by eid desc,
    # online_cluster uses stable/lowest-index == secondary constant). This is a per-ARM policy detail, not the core.
    if key_of is None:
        order = sorted(range(len(cands)), key=lambda k: acts[k], reverse=True)
    else:
        order = sorted(range(len(cands)), key=lambda k: (acts[k], key_of(cands[k])), reverse=True)
    top_i = order[0]
    top = acts[top_i]
    runner = acts[order[1]] if len(order) > 1 else float("-inf")
    if policy == "argmax":
        picked = cands[top_i]
    elif policy == "hold":
        picked = cands[top_i] if (top >= threshold and (len(cands) == 1 or (top - runner) >= margin)) else None
    elif policy == "compete":
        dominates = (len(cands) == 1) or ((top - runner) >= margin)
        if abstain_below is not None and abstain_below(top):
            dominates = False
        picked = cands[top_i] if dominates else None
    else:
        raise ValueError("unknown policy %r" % policy)
    return picked, cands, acts


# ==========================================================================================================
# CUE-ARM primitives (the pluggable content-match cues; each licenses a candidate given a query).
# ==========================================================================================================
_TYPE_CACHE: Dict[tuple, bool] = {}


def type_match(h1: str, h2: str, route: str) -> bool:
    """TYPE cue. route in {exact, isa, partwhole}: head identity / WordNet is-a either dir / full coref license
    (synonym U is-a U part-whole). Byte-faithful to online_entity_cluster._type_match (same memo, same routes)."""
    if h1 == h2:
        return True
    if route == "exact":
        return False
    key = (route, h1, h2) if h1 <= h2 else (route, h2, h1)
    c = _TYPE_CACHE.get(key)
    if c is not None:
        return c
    if route == "isa":
        s1 = TS._mfs_synset(h1); s2 = TS._mfs_synset(h2)
        out = bool(s1 and s2 and ((s2 in TS.isa_ancestors(s1)) or (s1 in TS.isa_ancestors(s2))))
    else:
        out = bool(TS.coref_type_license(h1, h2))
    _TYPE_CACHE[key] = out
    return out


def _role_from_rank(rank) -> str:
    """Centering Cf-rank -> prominence role (byte-faithful to online_entity_cluster._role_from_rank)."""
    return "SUBJECT" if rank == 0 else ("OBJECT" if rank == 1 else "OTHER")


# ==========================================================================================================
# THE FILE (Heim file card) -- one discourse-entity's mention history + agreement + heads + Centering subj-sent.
# ==========================================================================================================
class _File:
    __slots__ = ("cid", "history", "gender", "number", "heads", "subj_sent")

    def __init__(self, cid):
        self.cid = cid; self.history = []; self.gender = None; self.number = None
        self.heads = set(); self.subj_sent = -1

    def update(self, order, role, gender, number, head, sent_idx):
        self.history.append((float(order), role))
        if gender and self.gender is None:
            self.gender = gender
        if number and self.number is None:
            self.number = number
        if head:
            self.heads.add(head)
        if role == "SUBJECT":
            self.subj_sent = sent_idx


# ==========================================================================================================
# THE UNIFIED RESOLVER  --  one core, one write engine, the Ariel mention-type router; the six organs' entries.
# ==========================================================================================================
class EntityResolver:
    """ONE cue-based entity resolver. Every public method is a declarative config of {router selects arm-set,
    retrieve() scores by the shared ACT-R core, write policy commits}. The methods reproduce the six organs'
    live entry points byte-identically (proof: verification/test_entity_resolver_unified.py)."""

    def __init__(self, *, decay: float = DEFAULT_DECAY, role_prominence: Optional[Dict[str, float]] = None,
                 validities=None):
        self.decay = decay
        self.role_prominence = ROLE_PROMINENCE if role_prominence is None else role_prominence
        # 2026-09-16 (strategy, pri 136 landing): the PLASTIC object-file table this resolver accrues into. The reader
        # passes its own copy (one reader = one brain, plastic across its documents); a resolver built without one
        # takes a fresh deep copy of the frozen asset at first use. The module-level asset cache is NEVER mutated, so
        # an ON-vs-OFF witness that builds one reader per arm stays comparable (before this, the accrual mutated the
        # shared cache and every later read in the process was order-dependent by construction).
        self._of_validities = validities

    # ---------------------------------------------------------------------------------------------------
    # ARM 1 (default-on live) -- ONLINE CLUSTERING of names + definite commons  == online_entity_cluster
    #   Router: NAME -> identity (aliaser); COMMON -> [phi, type_exact] cue, base-level argmax, always-merge.
    # ---------------------------------------------------------------------------------------------------
    def cluster(self, ms, gaz, *, type_route: str = "exact", centering: bool = False,
                hold: Optional[float] = None, margin: float = 1.0, sents=None, reader=None,
                competition: Optional[bool] = None, tau: float = OBJECT_FILE_TAU,
                bridge_binds=None) -> Dict[int, int]:
        """{midx: cluster_id} over NON-pronoun mentions.

        DEFAULT (pri 136): the OBJECT-FILE CUE COMPETITION above -- every open file scored by the ACT-R
        base-level plus the summed cue evidence at its accrued validity, a new file opened when nothing
        clears the retrieval threshold.  Set `competition=False` (or HDLAB_OBJECT_FILE_COMPETITION=0, or
        remove the validity asset) for the pre-2026-09-16 hard-filter-then-always-merge arm, which is what
        the paragraph below describes and what `_cluster_hard_filter` still is, byte-identical.

        THE HARD-FILTER ARM (kept for the A/B): reproduces online_entity_cluster.online_cluster.
        NAME -> given-name aliaser file (identity). COMMON -> retrieve() over the phi-compatible, type-licensed
        prior files, scored by the shared ACT-R base-level (+ optional Centering-Cb continuity bonus), committed
        by the write policy (always-merge, or hold-under-uncertainty)."""
        if competition is None:
            competition = os.environ.get("HDLAB_OBJECT_FILE_COMPETITION", "1") != "0"
        if competition:
            V = self._of_validities
            if V is None:
                _base = object_file_validities()
                if _base is not None:
                    import copy as _copy
                    V = _copy.deepcopy(_base)      # this resolver's own plastic copy; the cache stays frozen
                    self._of_validities = V
            if V is not None:
                _on = os.environ.get("HDLAB_OBJECT_FILE_ONLINE", "1") != "0"
                return competition_cluster(ms, gaz, validities=V, tau=tau, decay=self.decay,
                                           role_prominence=self.role_prominence,
                                           bridge_binds=bridge_binds, sents=sents,
                                           online=_on, online_margin=OBJECT_FILE_ONLINE_MARGIN)
        return self._cluster_hard_filter(ms, gaz, type_route=type_route, centering=centering,
                                         hold=hold, margin=margin)

    def _cluster_hard_filter(self, ms, gaz, *, type_route: str = "exact", centering: bool = False,
                             hold: Optional[float] = None, margin: float = 1.0) -> Dict[int, int]:
        """THE PRE-2026-09-16 ARM, byte-identical: phi + exact-head HARD FILTER, then always-merge argmax."""
        files: List[_File] = []
        labels: Dict[int, int] = {}
        aliaser = EntityAliaser(); canon2f: Dict[object, _File] = {}; surf2f: Dict[str, _File] = {}
        for order, m in enumerate(ms):
            if m["is_pronoun"]:
                continue
            role = _role_from_rank(m.get("sent_role_rank", 99))
            sent_idx = m.get("sent_idx", 0)
            number = m.get("number")
            head = head_lemma(m["head"]); gender = m.get("gender") or m.get("name_gender")
            name_toks = name_content_tokens(m.get("span_toks", [m["head"]]), upos=m.get("span_upos"))
            if name_toks:                                           # NAME -> identity (given-name file)
                canon = aliaser.assign(m.get("span_toks", [m["head"]]), gender,
                                       upos=m.get("span_upos"))
                key = canon if canon is not None else ("surf:" + m["head"])
                f = canon2f.get(key) or surf2f.get(m["head"])
                if f is None:
                    f = _File(len(files)); files.append(f)
                    if canon is not None:
                        canon2f[key] = f
                    surf2f[m["head"]] = f
                f.update(order, role, gender, number, None, sent_idx)
                labels[m["midx"]] = f.cid
            else:                                                   # COMMON -> ONE cue-based retrieval
                def _license(f, _h=head, _g=gender, _n=number, _r=type_route):
                    return compatible(_g, _n, f.gender, f.number) and any(type_match(_h, h, _r) for h in f.heads)

                def _bonus(f, _si=sent_idx):
                    return 0.5 if (centering and f.subj_sent == _si - 1 and _si > 0) else 0.0

                policy = "argmax" if hold is None else "hold"
                picked, _c, _a = retrieve(files, order, license=_license,
                                          bonus=_bonus if centering else None,
                                          decay=self.decay, role_prominence=self.role_prominence,
                                          policy=policy, threshold=(hold or 0.0), margin=margin)
                if picked is None:
                    picked = _File(len(files)); files.append(picked)
                picked.update(order, role, gender, number, head, sent_idx)
                labels[m["midx"]] = picked.cid
        return labels

    # ---------------------------------------------------------------------------------------------------
    # ARM 0 (GENERALIZE: the pronoun arm) -- PRONOUN pick (Ariel high-accessibility)  == salience_binder.bind
    #   Router: PRONOUN. Cue: phi-agreement (applied by the caller -> it supplies the phi-compatible candidate
    #   HISTORIES) + base-level ACT-R salience. Retrieve: argmax activation (the pinned pronoun pick). This shows
    #   the ONE core serves ALL FOUR Ariel mention types; the SALIENCE MATH (actr_activation) stays in
    #   salience_binder (KEEP-separate) -- only the argmax RETRIEVAL is the shared core.
    # ---------------------------------------------------------------------------------------------------
    def pronoun_pick(self, candidates, now, *, decay=None, role_prominence=None) -> int:
        """Return the index of the retrieved antecedent for a pronoun -- reproduces salience_binder.bind (argmax
        ACT-R base-level activation over the caller's phi-compatible candidate histories; ties -> lowest index).
        `candidates` is a sequence of mention HISTORIES [(time, role), ...]. -1 if empty."""
        n = len(candidates)
        if n == 0:
            return -1
        _p, cands, acts = retrieve(list(candidates), now, license=lambda f: True,
                                   decay=(self.decay if decay is None else decay),
                                   role_prominence=(self.role_prominence if role_prominence is None else role_prominence),
                                   policy="argmax", history_of=lambda h: h)
        # cands preserves input order (license all-True) -> reproduce np.argmax first-max (lowest-index) tie-break.
        best = 0
        for i in range(1, len(acts)):
            if acts[i] > acts[best]:
                best = i
        return best

    # ---------------------------------------------------------------------------------------------------
    # ARM 2 (default-on live) -- DEFINITE -> NAME cross-type BRIDGE  == crosstype_bridge.crosstype_bridge_links
    #   Router: definite person role-noun. Cue-PRODUCER: precise_constructs (in-text predication, imported).
    #   Retrieve: [predication-desc-boost + phi] over the NAME cards, base-level ACT-R, compete + confidence.
    # ---------------------------------------------------------------------------------------------------
    def bridge_links(self, doc, gaz, *, conf_thr: float, margin: float = 0.5, mode: str = "cue_conf") -> Dict[int, int]:
        """{role_midx: name_eid} -- reproduces crosstype_bridge.crosstype_bridge_links for ALL FIVE cue modes
        (cue_retrieval / cue_gated / cue_competed / cue_novelty / cue_conf), restrict_gold=False, salience='actr'.
        LIVE reader uses mode='cue_conf' @ conf_thr=-3.0 (via crosstype_live_adapter); the board experiencer
        instrument uses mode='cue_competed'. The predication detector (precise_constructs) is a cue-PRODUCER
        (imported, not re-implemented -- a genuinely distinct in-text extraction); the RETRIEVAL/competition stage
        is the shared core with a descriptive-content boost bonus + a per-mode gate/abstain policy."""
        from hdlab.crosstype_bridge import (precise_constructs, head_lemma as _hl,
                                            _AGE_GENDER, _ART, _NONPERSON_STOP, _DESC_BOOST, _ORD_SUP, _mention_role)
        licensed, ent_person = precise_constructs(doc, gaz)
        ms = doc.mentions
        by_gidx = {t.gidx: t for t in doc.toks}
        # children index (by head gidx) -- needed only by the cue_novelty establishing-modifier gate.
        _bysi = {(t.sent, t.idx): t.gidx for t in doc.toks}
        _children = defaultdict(list)
        for _t in doc.toks:
            _hg = _bysi.get((_t.sent, _t.head))
            if _hg is not None:
                _children[_hg].append(_t)

        def _establishing_modifier(head_g):
            """Hawkins/Bean-Riloff: a restrictive establishing modifier (relcl, post-head nmod, superlative,
            ordinal) marks a definite as first-mention -> abstain. Byte-faithful to crosstype_bridge."""
            h = by_gidx.get(head_g)
            if h is None:
                return False
            for c in _children.get(head_g, ()):
                full = (c.deprel or ""); dep = full.split(":")[0]
                if full == "acl:relcl" or dep == "acl":
                    return True
                if dep == "nmod" and c.idx > h.idx:
                    return True
                if dep == "amod" and (c.xpos == "JJS" or (c.form or "").lower() in _ORD_SUP):
                    return True
                if dep == "nummod" or (c.form or "").lower() in _ORD_SUP:
                    return True
            return False

        def _person_def(L):
            return L not in _NONPERSON_STOP and person_synset(L) is not None

        firstname: Dict[object, int] = {}
        name_gender_order: List[tuple] = []
        name_gender: Dict[object, str] = {}
        name_hist = defaultdict(list)
        common_head_orders = defaultdict(list)
        for i, m in enumerate(ms):
            if m.mtype == "common":
                common_head_orders[_hl(m.lemma_head)].append(i)
            if m.mtype == "name" and m.eid in ent_person:
                firstname.setdefault(m.eid, i)
                name_gender_order.append((i, m.eid, m.gender))
                name_hist[m.eid].append((i, _mention_role(by_gidx, m)))
                if m.gender in ("m", "f") and m.eid not in name_gender:
                    name_gender[m.eid] = "masc" if m.gender == "m" else "fem"
        binds: Dict[int, int] = {}
        for i, m in enumerate(ms):
            if m.mtype != "common":
                continue
            L = _hl(m.lemma_head); toks = m.text.lower().split()
            if not toks or toks[0] not in _ART or not _person_def(L):
                continue
            if not any(o < i for (o, _e, _g) in name_gender_order):     # DEPLOYMENT population (restrict_gold=False)
                continue
            named = licensed.get(L, set())
            ag = _AGE_GENDER.get(L)
            # per-mode ANAPHORICITY gate (byte-faithful to gated_binds):
            #  cue_gated  -> fire only on predication-licensed OR age/gender re-mention;
            #  cue_competed/cue_novelty/cue_conf -> full-referent competition (a same-head prior common wins);
            #  cue_novelty -> also abstain on a Hawkins establishing modifier;
            #  cue_retrieval -> no gate.
            gate_ok = not (mode == "cue_gated" and not named and ag is None)
            if mode in ("cue_competed", "cue_novelty", "cue_conf"):
                prior_common = any(o < i for o in common_head_orders.get(L, ()))
                if not named and prior_common:
                    gate_ok = False
            if mode == "cue_novelty" and not named and _establishing_modifier(m.head_g):
                gate_ok = False

            # candidate NAME cards, phi(age/gender)-filtered; retrieved by the shared core over their name-mention
            # histories, with the Almor descriptive-content boost for predication-licensed names.
            class _NameCard:
                __slots__ = ("eid", "history")

                def __init__(self, eid, history):
                    self.eid = eid; self.history = history

            cards = []
            for e, hist in (name_hist.items() if gate_ok else ()):
                priors = [(o, r) for (o, r) in hist if o < i]
                if not priors:
                    continue
                if ag is not None and ag != "any":
                    g = name_gender.get(e)
                    if g is not None and g != ag:
                        continue
                cards.append(_NameCard(e, priors))

            def _license(c):
                return True                                             # phi already applied; predication is a bonus

            def _bonus(c, _named=named, _boost=_DESC_BOOST):
                return _boost if c.eid in _named else 0.0

            def _abstain_below(top, _thr=conf_thr, _boost=_DESC_BOOST, _mode=mode):
                # cue_conf ONLY: abstain when the best NON-predicated candidate's activation < conf_thr (McElree novel).
                return _mode == "cue_conf" and top < _boost and top < _thr

            picked, _c, _a = retrieve(cards, i, license=_license, bonus=_bonus,
                                      decay=DEFAULT_DECAY, role_prominence=ROLE_PROMINENCE,
                                      policy="compete", margin=margin, abstain_below=_abstain_below,
                                      key_of=lambda c: c.eid)
            if picked is not None:
                binds[i] = picked.eid
        return binds

    # ---------------------------------------------------------------------------------------------------
    # ARM 1b (default-on live) -- TYPED COMMON-NOUN RESOLUTION  == situation_reader._resolve_commonnouns
    #   The typed_coref binding on the reader's own dict stream (Ariel low-accessibility definite):
    #     NAME    -> identity (aliaser / concept-key);
    #     COMMON same-head -> RECENCY incumbent (score_of=last_midx through the ONE core);
    #     COMMON diff-head -> NON-WRITING type/appos/C8/conceptual/coarse bridge, ACT-R argmax (the ONE core);
    #     PRONOUN -> phi + ACT-R argmax (writes the salience card only; Ariel/Nieuwland de-pollution).
    #   The 5 bridge CUES (in-text appos is-a, typed-spokes license, C8 encyclopedic, conceptual, coarse-focus)
    #   are cue-PRODUCERS supplied by the reader/organs -- feature extractors, not retrieval; the retrieval loop
    #   folds into the ONE core. Reproduces reader._resolve_commonnouns BYTE-IDENTICALLY (takes `reader` for its
    #   cue-producers + bridge flags; the hdlab landing repoints the reader method to call this).
    # ---------------------------------------------------------------------------------------------------
    def resolve_commonnouns(self, role_mentions, sents, reader) -> list:
        """{per non-pronoun mention: midx/mtype/own_ref/resolved_ref} -- byte-identical to
        situation_reader._resolve_commonnouns. `reader` supplies the cue-producers (_commonnoun_appos_map,
        _cn_type_rel) and the bridge flags (conceptual_bridge / focus_bridge / uniqueness_bridge / uniq_window)."""
        import hdlab.typed_coref as _TC
        from hdlab.lexical_utils import concept_lemma, is_name, _num_of, DEF_DET, coarse_class
        from hdlab.coref import EntityAliaser
        from hdlab.typed_spokes import type_licenses as _c8_type_licenses, available_entity_type as _c8_available
        from hdlab.situation_reader import _pron_gn
        _c8_on = _c8_available(); _c8_cache = {}

        def _c8_lic(head, surface):
            if not _c8_on:
                return False
            k = (head, surface); v = _c8_cache.get(k)
            if v is None:
                v = _c8_type_licenses(head, surface); _c8_cache[k] = v
            return v

        appos_map = reader._commonnoun_appos_map(sents)
        _g2mfn = {"masc": "m", "fem": "f", "neut": "n"}

        class _Ref:
            __slots__ = ("rid", "history", "heads", "name_tokens", "name_surfaces", "gender", "number",
                         "has_name", "last_midx")

            def __init__(self, rid):
                self.rid = rid; self.history = []; self.heads = set(); self.name_tokens = set()
                self.name_surfaces = set(); self.gender = ""; self.number = ""; self.has_name = False
                self.last_midx = -1

            def write(self, order, role, mtype, hl, mg, mn, ntoks_):
                self.history.append((order, role)); self.last_midx = order
                if mg and not self.gender:
                    self.gender = mg
                if mn and not self.number:
                    self.number = mn
                if mtype == "name":
                    self.has_name = True; self.name_tokens |= ntoks_
                elif mtype == "common":
                    self.heads.add(hl)

        def mfn(m):
            return _g2mfn.get(m.get("gender") or m.get("name_gender") or "", "")

        def gn_ok(rg, rn, mg, mn):
            if mg and rg and mg != rg:
                return False
            if mn and rn and mn != rn:
                return False
            return True

        def ntoks(span):
            return {w.lower() for w in span if w.lower() not in _TC.TITLES and any(c.isalpha() for c in w)}

        aliaser = EntityAliaser(); canon2ref = {}; name_surf = {}
        refs = []; out = []; nid = [0]

        def new_ref():
            r = _Ref(nid[0]); nid[0] += 1; refs.append(r); return r

        _conc_ch = [None]; _conc_cache = {}

        def _coarse_compat(a, heads):
            ca = coarse_class(a)
            return ca is not None and any(coarse_class(h) == ca for h in heads)

        def _conc_bridge(a, b):
            if a == b:
                return True
            k = (a, b) if a <= b else (b, a); v = _conc_cache.get(k)
            if v is None:
                if _conc_ch[0] is None:
                    from hdlab.conceptual_meaning import ConceptualChannel
                    _conc_ch[0] = ConceptualChannel()
                try:
                    s = _conc_ch[0].similarity(a, "N", b, "N")
                except Exception:
                    s = None
                v = (s is not None and s >= 0.40); _conc_cache[k] = v
            return v

        for m in sorted(role_mentions, key=lambda x: x["midx"]):
            order = m["midx"]
            role = "SUBJECT" if m.get("sent_role_rank", 99) == 0 else "OTHER"
            span = m.get("span_toks", [m["head"]])
            if m["is_pronoun"]:
                mg, mn = _pron_gn(m["head"].lower())
                cands = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
                if cands:                                           # PRONOUN: phi + ACT-R argmax (the ONE core)
                    picked, _c, _a = retrieve(cands, order, license=lambda f: True,
                                              decay=self.decay, role_prominence=self.role_prominence, policy="argmax")
                    picked.write(order, role, "pronoun", "", mg, mn, set())
                continue
            hl = concept_lemma(m["head"]); mg, mn = mfn(m), _num_of(m)
            if is_name(m, None):                                     # NAME: identity (aliaser / concept-key)
                canon = aliaser.assign(span, (m.get("gender") or m.get("name_gender")) or None)
                if canon is not None and canon in canon2ref:
                    r = canon2ref[canon]; opened = False
                elif hl in name_surf:
                    r = name_surf[hl]; opened = False
                else:
                    r = new_ref(); opened = True
                    if canon is not None:
                        canon2ref[canon] = r
                    name_surf[hl] = r
                out.append({"midx": order, "mtype": "name", "own_ref": r.rid,
                            "resolved_ref": (None if opened else r.rid)})
                r.write(order, role, "name", hl, mg, mn, ntoks(span))
                r.name_surfaces.add(" ".join(span))
                continue
            same = [r for r in refs if r.last_midx < order and hl in r.heads and gn_ok(r.gender, r.number, mg, mn)]
            picked = None; opened = True; nowrite = None
            definite = bool(span) and span[0].lower() in DEF_DET
            if same:                                                 # SAME-HEAD: RECENCY incumbent (the ONE core, score_of=last_midx)
                picked, _c, _a = retrieve(same, order, license=lambda f: True,
                                          score_of=lambda r: r.last_midx, policy="argmax"); opened = False
            else:                                                    # DIFF-HEAD: non-writing type/appos/C8/conceptual/coarse bridge
                tset = appos_map.get(hl, set())
                prior_gn = [r for r in refs if r.last_midx < order and gn_ok(r.gender, r.number, mg, mn)]
                br = [r for r in prior_gn if (r.heads & tset)
                      or (r.has_name and any(t in r.name_tokens for t in tset))
                      or any(reader._cn_type_rel(hl, h) for h in r.heads)
                      or (r.has_name and any(_c8_lic(hl, ns) for ns in r.name_surfaces))
                      or (reader.conceptual_bridge and any(_conc_bridge(hl, h) for h in r.heads))
                      or (reader.focus_bridge and definite and _coarse_compat(hl, r.heads))]
                if br:                                               # ACT-R argmax over the licensed bridge set (the ONE core)
                    nowrite, _c, _a = retrieve(br, order, license=lambda f: True,
                                               decay=self.decay, role_prominence=self.role_prominence, policy="argmax")
                elif reader.uniqueness_bridge and definite:
                    infocus = [r for r in prior_gn if r.last_midx >= order - reader.uniq_window]
                    if len(infocus) == 1:
                        nowrite = infocus[0]
            if picked is None:
                picked = new_ref()
            resolved = (nowrite.rid if nowrite is not None else (None if opened else picked.rid))
            out.append({"midx": order, "mtype": "common", "own_ref": picked.rid, "resolved_ref": resolved})
            picked.write(order, role, "common", hl, mg, mn, set())
        return out

    # ---------------------------------------------------------------------------------------------------
    # ARM 3 (default-on live) -- WORLD-STATE STAGE-1 DISPATCH  == world_state_entity_binding.EntityBinder
    #   A DEICTIC ROUTER (indexical -> narrator O(1); pleonastic-it filter; anaphoric -> consume core output;
    #   nominal -> canonical head). Located negative: the deictic routes are NOT content-addressable retrieval.
    # ---------------------------------------------------------------------------------------------------
    def new_stage1_binder(self, narrator_key: str = "~NARRATOR"):
        """Return an EntityBinder-equivalent Stage-1 dispatcher (the output-normalisation + deixis arm). It
        ROUTES: indexical (I/me/my) -> narrator (O(1) deixis, not retrieval); anaphoric (he/she) -> consume the
        core's coref cluster; object-anaphora (it/them) -> the salient recent nominal theme (Centering-lite);
        nominal -> canonical head. This is a routing arm around the retrieval core, kept distinct because deixis
        is an O(1) speech-role lookup, not O(n) content-addressable search."""
        return _Stage1Dispatcher(narrator_key)

    # ---------------------------------------------------------------------------------------------------
    # ARM 4 (DORMANT) -- KB-PRIOR cue-arm  == entity_world_model_resolver (role/kinship/scenario prior)
    #   The sixth organ folds into the ONE resolver as its KB-PRIOR arm. It is DORMANT (reader flag
    #   entity_kb_resolver=False) -> there is NO live behavior to reproduce byte-identically; it is folded
    #   PROVEN-IN-KIND: a curated role/kinship world-knowledge prior is a `bonus` cue over the shared core,
    #   the SAME `bonus` slot the crosstype descriptive-content boost (`_DESC_BOOST`) already uses byte-identically.
    #   When activated, its role/kinship/scenario prior enters retrieve() as an additive activation bonus (it does
    #   NOT introduce a new retrieval STRUCTURE). Kept as a lazy delegation so this module carries NO experiments/
    #   import at load (self-containment); the dormant chain's own experiments-import debt is a filed follow-on.
    # ---------------------------------------------------------------------------------------------------
    def kb_prior_cluster(self, mentions, gaz, *, reader_coref=None, window: int = 8) -> Dict[int, object]:
        """{midx: label} via the DORMANT role/kinship/scenario KB-prior arm (entity_world_model_resolver). Folds
        the sixth organ into the ONE resolver as a KB-prior cue-arm (a `bonus` over the shared retrieval core --
        the same slot crosstype's descriptive-content boost uses). DORMANT: not on any default live path
        (entity_kb_resolver=False); reachable only when a caller opts into the KB prior. Lazy delegation keeps
        this organ free of experiments/ imports at module load."""
        from hdlab.entity_world_model_resolver import resolve_common_noun
        return resolve_common_noun(mentions, gaz, reader_coref=reader_coref, window=window)


# ==========================================================================================================
# ARM 3 impl -- byte-faithful reproduction of world_state_entity_binding.EntityBinder (the deictic router).
# ==========================================================================================================
_FIRST_SG = {"i", "me", "my", "mine", "myself"}
_HE_SHE = {"he", "him", "his", "she", "her", "hers"}
_OBJ_PRON = {"it", "them", "they", "its"}
_SCOPE_OUT = {"we", "us", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves"}
_PLEONASTIC_VERBS = {"take", "takes", "took", "give", "gives", "gave", "cost", "costs", "require", "requires"}


class _Stage1Dispatcher:
    def __init__(self, narrator_key="~NARRATOR"):
        self.narrator = narrator_key
        self.recent_nominal_theme: Optional[str] = None
        self.stats = Counter()

    @staticmethod
    def route_of(head: Optional[str]) -> str:
        if head is None:
            return "none"
        h = head.lower()
        if h in _FIRST_SG:
            return "indexical"
        if h in _HE_SHE:
            return "anaphoric"
        if h in _OBJ_PRON:
            return "object_anaphora"
        if h in _SCOPE_OUT:
            return "scope_out"
        return "nominal"

    def is_pleonastic_it(self, head, verb, role) -> bool:
        if head.lower() != "it":
            return False
        if role == "agent" and verb and verb.lower() in _PLEONASTIC_VERBS:
            return True
        if role in ("theme", "object") and self.recent_nominal_theme is None:
            return True
        return False

    def bind_participant(self, head, coref_cluster=None, verb=None, coref_entropy=None, abstain_tau=None) -> tuple:
        r = self.route_of(head)
        if r == "indexical":
            self.stats["indexical"] += 1
            return self.narrator, "indexical"
        if r == "anaphoric":
            if coref_cluster is None:
                self.stats["anaphoric_unresolved"] += 1
                return None, "anaphoric_abstain"
            if abstain_tau is not None and coref_entropy is not None and coref_entropy > abstain_tau:
                self.stats["anaphoric_low_conf_abstain"] += 1
                return None, "anaphoric_low_conf_abstain"
            self.stats["anaphoric_resolved"] += 1
            return "C%s" % coref_cluster, "anaphoric"
        if r == "object_anaphora":
            self.stats["participant_objpron_abstain"] += 1
            return None, "abstain"
        if r == "scope_out":
            self.stats["scope_out_abstain"] += 1
            return None, "scope_out"
        if r == "nominal":
            self.stats["nominal"] += 1
            return head.lower(), "nominal"
        return None, "none"

    def bind_theme(self, head, verb=None) -> tuple:
        if head is None:
            return None, "none"
        r = self.route_of(head)
        if r == "object_anaphora":
            if self.is_pleonastic_it(head, verb, "theme"):
                self.stats["pleonastic_it_abstain"] += 1
                return None, "pleonastic_abstain"
            if self.recent_nominal_theme is not None:
                self.stats["object_anaphora_resolved"] += 1
                return self.recent_nominal_theme, "object_anaphora"
            self.stats["object_anaphora_noantecedent"] += 1
            return head.lower(), "object_raw"
        if r == "nominal":
            self.recent_nominal_theme = head.lower()
            self.stats["theme_nominal"] += 1
            return head.lower(), "nominal"
        if r == "indexical":
            return self.narrator, "indexical"
        return (head.lower() if head else None), r


# ==========================================================================================================
# module self-test (corpus-free): the ONE core reproduces each arm's decision on a small deterministic case.
# ==========================================================================================================
def _selftest() -> int:
    fails = []
    R = EntityResolver()

    # ARM 1: two 'the dog' + one 'the cat' -> two files; name -> own; pronoun skipped (== online_cluster).
    ms = [
        {"midx": 0, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 0, "gender": None, "number": "sing"},
        {"midx": 1, "head": "cat", "span_toks": ["the", "cat"], "is_pronoun": False, "sent_idx": 0, "sent_role_rank": 1, "gender": None, "number": "sing"},
        {"midx": 2, "head": "it", "span_toks": ["it"], "is_pronoun": True, "sent_idx": 1, "sent_role_rank": 0},
        {"midx": 3, "head": "dog", "span_toks": ["the", "dog"], "is_pronoun": False, "sent_idx": 1, "sent_role_rank": 0, "gender": None, "number": "sing"},
    ]
    lab = R.cluster(ms, gaz=None)
    ok1 = lab.get(0) == lab.get(3) and lab.get(0) != lab.get(1) and 2 not in lab and all(isinstance(v, int) for v in lab.values())
    print("  %s A1 cluster: same-head merges (0==3), cat separate, pronoun skipped, int ids: %s" % ("PASS" if ok1 else "FAIL", lab))
    if not ok1:
        fails.append("A1")

    # ARM 3: indexical collapse, anaphoric consume, object-anaphora Centering, pleonastic + scope-out abstain.
    b = R.new_stage1_binder()
    ok3 = (b.bind_participant("I")[0] == b.bind_participant("me")[0] == "~NARRATOR"
           and b.bind_participant("he", coref_cluster=5) == ("C5", "anaphoric")
           and b.bind_participant("she", coref_cluster=None)[1] == "anaphoric_abstain"
           and b.bind_participant("we")[0] is None)
    b2 = R.new_stage1_binder()
    ok3b = (b2.bind_theme("it")[1] == "pleonastic_abstain" and b2.bind_theme("cup")[0] == "cup"
            and b2.bind_theme("it") == ("cup", "object_anaphora"))
    print("  %s A3 stage1 dispatch: indexical/anaphoric/object-anaphora/pleonastic routes: %s" % ("PASS" if ok3 and ok3b else "FAIL", ok3 and ok3b))
    if not (ok3 and ok3b):
        fails.append("A3")

    # core: the write policies behave (argmax vs hold-under-uncertainty).
    class _F:
        def __init__(self, cid, hist):
            self.cid = cid; self.history = hist
    files = [_F(0, [(0.0, "SUBJECT")]), _F(1, [(1.0, "OTHER")])]
    p_arg, _, _ = retrieve(files, 3.0, license=lambda f: True, policy="argmax")
    p_hold, _, _ = retrieve(files, 3.0, license=lambda f: True, policy="hold", threshold=100.0, margin=1.0)
    okc = p_arg is files[0] and p_hold is None
    print("  %s CORE policies: argmax picks top; hold-under-high-threshold opens new: %s" % ("PASS" if okc else "FAIL", okc))
    if not okc:
        fails.append("CORE")

    print("RESULT: %s" % ("PASS" if not fails else "FAIL (%s)" % ",".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())
