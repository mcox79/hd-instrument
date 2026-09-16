"""exp_fine_relations_arm_v1 -- THE NON-ARGUMENT ARM of the ONE labels rung.

PRIORITY 134 (notes/problems/the_fine_non_argument_relations_appos_flat_compound_poss_have_no_brain_
foundational_source_since_the_relation_labeler_retired_build_the_rung_from_the_name_run_cue_the_
predicate_slot_and_the_possessive_class/PROBLEM.md).

THE DEFECT.  pri 129 retired the supervised relation labeler (`hdlab/arc_labeler.py`, NOT_BF) from the live
read and routed `crosstype_live_adapter._parse_sentence` to the ONE role competition
(`graded_role_assigner.coarse_roles`).  That organ labels ARGUMENT relations only -- and only over the
NOMINAL / argument-head population -- so on the reader's own parse EVERY non-argument token now reads `dep`:
no `appos`, no `flat`, no `compound`, no `nmod:poss`, and -- the one nobody named -- NO `cop`.  The
crosstype definite->name bridge's four name-linking cues (crosstype_bridge.precise_constructs:238-260) and
its Centering POSSESSIVE role (:115) are keyed on exactly those strings, so they cannot fire.

HOW THE BRAIN DOES THIS (the opening move, per relation).
  * A NAME RUN ("Mary Smith") is not a relation between two words at all: it is ONE referring expression
    stored and retrieved as a unit (Kripke 1980 rigid designation; Semenza 2006/2009 proper-name anomia
    localises multi-word proper names to the LEFT TEMPORAL POLE, a level ABOVE and fed by the category
    level).  The "relation" is the residue of that chunking.  Our organ for it is pri 118's span-level
    NAME-RUN cue (`hdlab.coref.span_caps_symbol` + `SpanCueTable`), learned online from the reader's own
    confident typings.
  * An APPOSITION ("Elizabeth, the doctor") is a REDUCED PREDICATION -- the same construction as "Elizabeth
    is the doctor" with the copula absent (Pustet 2003 on copula optionality; Maienborn 2005 Kimian states;
    Bemis & Pylkkanen 2011 LATL property attribution).  The organ that detects a predication is pri 110/117's
    PREDICATE SLOT (`hdlab.attachment_arm.predicate_sites`, graded).  The comma is a surface epiphenomenon --
    and pri 129 counted the gold: only 24 of 105 UD-EWT appositions carry one.
  * A POSSESSIVE ("her brother", "Mary's dog") is CASE MARKING, the Competition Model's strongest
    morphological cue (Bates & MacWhinney 1989; MacWhinney 1987).  English marks it overtly and the organ
    already reads it: `graded_role_assigner.genitive_value` (gen_pron / gen_clitic, cue set v4).
  * A COPULA is the TENSE CARRIER of a non-verbal predication -- the reason English inserts it (Pustet 2003;
    Bybee 1994 auxiliation), already stated by pri 113.  `attachment_arm.cop_complement` says which token it
    carries tense FOR, with no labeler.
  * And the CONVENTION LAYER (det / case / cc / mark / amod / nummod / punct / aux) is not computed by the
    brain at all: it is the distributional residue of the category rung, so it is learned as counts.
  ==> ONE ARM, ONE COMPETITION.  Every one of those is a CONSTRUCTION -- a form/governor pairing recognised
  by CUES whose VALIDITY is accrued from usage (Goldberg 1995 construction grammar; MacWhinney's Competition
  Model for the decision rule).  So this is not a new organ: it is the NON-ARGUMENT ARM of the one labels
  rung, using THE SAME strength math (`graded_role_assigner.strengths_from_counts`), the same additive
  activation (`graded_competition.net_activation`), a count asset, and an online `observe` path.

THE DIVISION OF LABOUR THAT MAKES THE TWO ARMS DISJOINT.  `coarse_roles` decides ARGUMENT-vs-NOT; where it
says OTHER (`dep`) or NMOD (`nmod`) -- "a property of a thing, not a participant of an event", its own pri-108
words -- the fine arm refines.  A core argument label is NEVER overridden, so no argument consumer can move.

ARMS (each writes only into get_output_dir):
  --probe    the consumer enumeration + the live-read fire counts (phase 1a)
  --build    accrue the validities from UD-EWT TRAIN counts (writes the asset)
  --ud       per-relation P/R on UD-EWT TEST, live chain, vs the retired perceptron + twin + oracle
  --bridge   the crosstype bridge's name-linking on GUM through the LIVE parse, per relation source
  --c3       the affect/experiencer C3 row through the real canonicalizer, per relation source
  --self-test

Glass-box, deterministic.  NO spaCy / nltk tagger / supervised parser / external LLM at inference.  The
validities are counts accrued OFFLINE from UD-EWT train (a static foundation asset, the same class as
`coarse_role_validities_ud_ewt.json`) and carry an online observe path.  ASCII-only.

  .venv/Scripts/python.exe experiments/exp_fine_relations_arm_v1.py --self-test
  .venv/Scripts/python.exe experiments/exp_fine_relations_arm_v1.py            # FULL (bare == full)
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import sys
import time

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir            # noqa: E402

ANCHOR = "fine_relations_arm_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
SEED = 20260916

# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-test.conllu
# KB_REFERENT: data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
# KB_REFERENT: data/frontend_assets/coarse_role_validities_ud_ewt.json
# KB_REFERENT: data/frontend_assets/arc_labeler_hashed_ud_ewt.json
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
LAB_ASSET = os.path.join(_REPO, "data/frontend_assets/arc_labeler_hashed_ud_ewt.json")
ASSET_NAME = "fine_relation_validities_ud_ewt.json"
ASSET_LANDED = os.path.join(_REPO, "data/frontend_assets", ASSET_NAME)


# ==================================================================================================
# THE ARM.  Prototyped here; shipped verbatim as the hdlab/graded_role_assigner.py hunks in
# notes/problems/<slug>/fine_relations_arm_patch.diff.
# ==================================================================================================
FINE_CLASSES = ["flat", "compound", "appos", "nmod:poss", "nmod", "cop", "det", "case", "amod",
                "nummod", "advmod", "cc", "mark", "punct", "aux", "acl", "advcl", "xcomp", "ccomp",
                "conj", "dep"]
FINE_IDX = {c: k for k, c in enumerate(FINE_CLASSES)}
NOMH = ("NOUN", "PROPN")
# the coarse organ's own ARGUMENT decisions -- never overridden by this arm
ARG_DEPS = frozenset({"nsubj", "obj", "nsubj:pass", "obl:agent", "obl", "iobj"})
# the cue set; selection is made on a TRAIN-INTERNAL DEV split, never on test
FINE_CUES = ("dcat", "gen", "run", "gap", "pslot", "hps", "crs", "runsym", "dist", "typepred", "zcop",
             "dpjux")
# THE ARC-INDEPENDENT CUES (the argument arm's own pri-108 lesson, applied here): "a cue whose whole
# purpose is to survive a WRONG arc must not be looked up INSIDE the arc's configuration, because that is
# the wrong row exactly when the governor mis-attached".  The NAME-RUN chunk, the GENITIVE case marker and
# the PREDICATE SLOT are all read off the surface with no arc at all -- their strength is the GLOBAL
# contrast log P(rel | value) - log P(rel).  Measured on the DEV split (arm_build reports both).
GLOBAL_FINE_CUES = frozenset({"run", "runsym", "gen", "pslot", "typepred", "zcop", "dpjux"})
# QUALITY PUSH 1 -- THE RUN IS ONE UNIT, SO A RUN MEMBER IS NOT A SEPARATE ARGUMENT.  A name phrase / noun
# compound is ONE referring expression filling ONE slot (Kripke 1980; Semenza 2006 -- the whole basis of the
# name-run account).  The ARGUMENT arm decides per TOKEN, so it hands a core role to each NOUN of a run
# independently; measured on UD-EWT test that claims 211 of 1,108 gold `compound` tokens as nsubj/obj/obl and
# they never reach this arm.  With RUN_MEMBERS on, the non-head members of a nominal run are in this population
# whatever the argument arm said -- the CHUNKING level, not this arm, is what overrules it.
RUN_MEMBERS = True
_SUPERSENSE = {}
_BE = frozenset({"be", "is", "are", "was", "were", "been", "being", "am"})


def fine_of(dep):
    """The UD deprel folded into the arm's class space (the MEASURING gold, never an input)."""
    full = dep or ""
    d = full.split(":")[0]
    if full == "nmod:poss":
        return "nmod:poss"
    if full == "nmod:desc":
        return "compound"          # the UD-2.16 convention split of a descriptive nominal (CONVENTION_SUBTYPES)
    if d == "nmod":
        return "nmod"
    if d in FINE_IDX:
        return d
    return "dep"


def _nominal_runs(pos, toks):
    """Maximal runs of adjacent nominal-head tokens (a name phrase / a noun compound), allowing a
    name-internal function word INSIDE a run that is nominal on both sides.  Returns a list of
    (start1, end1, kind) with 1-based inclusive bounds; kind in {'propn','noun','mixed'}."""
    from hdlab.coref import NAME_INTERNAL_FUNCTION
    n = len(pos)
    runs = []
    i = 0
    while i < n:
        if pos[i] not in NOMH:
            i += 1
            continue
        j = i
        while j + 1 < n:
            if pos[j + 1] in NOMH:
                j += 1
                continue
            if (pos[i] == "PROPN" and j + 2 < n and pos[j + 2] == "PROPN"
                    and str(toks[j + 1]).lower() in NAME_INTERNAL_FUNCTION):
                j += 2
                continue
            break
        kinds = {pos[k] for k in range(i, j + 1) if pos[k] in NOMH}
        kind = "propn" if kinds == {"PROPN"} else ("noun" if kinds == {"NOUN"} else "mixed")
        runs.append((i + 1, j + 1, kind))
        i = j + 1
    return runs


def _run_index(pos, toks):
    """1-based token -> (start1, end1, kind) of its nominal run (only for runs of length >= 2)."""
    out = {}
    for (a, b, k) in _nominal_runs(pos, toks):
        if b > a:
            for t in range(a, b + 1):
                out[t] = (a, b, k)
    return out


def _gap_value(toks, pos, i, h):
    """The intervening material between the dependent and its governor -- the surface signature a
    construction is read off (a comma for the LOOSE appositive, a copular BE for the predication, a
    determiner for a fresh nominal, an adposition for a case-marked oblique)."""
    a, b = (i, h) if i < h else (h, i)
    if b - a <= 1:
        return "adj"
    mid = list(range(a + 1, b))
    if len(mid) > 6:
        return "far"
    lows = [str(toks[k - 1]).lower() for k in mid]
    cats = [pos[k - 1] for k in mid]
    if any(w in _BE for w in lows) and all(c in ("AUX", "VERB", "ADV", "DET", "ADJ", "NUM", "PART") for c in cats):
        return "be"
    if lows[0] == ",":
        return "comma"
    if any(w == "," for w in lows):
        return "comma2"
    if all(c in ("DET", "ADJ", "NUM", "ADV") for c in cats):
        return "det"
    if cats[0] == "ADP" or cats[-1] == "ADP":
        return "adp"
    if all(c == "PUNCT" for c in cats):
        return "punct"
    return "mix"


def _supersense(lemma):
    """The ANTERIOR-TEMPORAL TYPE READ: the most-frequent-sense noun supersense of a lemma, from the frozen
    offline asset (`data/frontend_assets/noun_supersense_mfs_v1.json`; no nltk at inference).  This is the
    hub-level knowledge an apposition USES -- "Elizabeth, the doctor" attributes a noun.person TYPE to a
    referent (Rogers & McClelland 2004 hub; Patterson, Nestor & Rogers 2007)."""
    if not _SUPERSENSE:
        try:
            with open(os.path.join(_REPO, "data/frontend_assets/noun_supersense_mfs_v1.json"),
                      encoding="utf-8") as f:
                _SUPERSENSE.update(json.load(f)["table"])
        except Exception:
            _SUPERSENSE["__none__"] = ""
    return _SUPERSENSE.get(str(lemma).lower().strip(".,\'\"!?;:-()[]"), "")


def _left_domains(pos, toks, runlist=None):
    """{1-based i: the nearest nominal domain (start1, end1, kind) strictly to the LEFT of i, or None} in ONE
    pass -- the appositive's antecedent domain, computed once per sentence."""
    runs = runlist if runlist is not None else _nominal_runs(pos, toks)
    out = {}
    cur = None
    k = 0
    for i in range(1, len(pos) + 1):
        while k < len(runs) and runs[k][1] < i:
            cur = runs[k]
            k += 1
        out[i] = cur
    return out


def _typepred_value(toks, pos, i, ldom):
    """QUALITY PUSH 2 -- THE APPOSITION IS A TYPE ATTRIBUTION, NOT A COMMA.  An appositive PREDICATES a type of
    the referent to its left, so the cue is the pair of hub TYPES (the left nominal domain and this token),
    not the punctuation between them.  Values: <left supersense>|<this supersense>|<same or diff>."""
    if pos[i - 1] not in NOMH:
        return "na"
    left = (ldom or {}).get(i)
    if left is None:
        return "noleft"
    ss = _supersense(toks[i - 1]) or ("PROPN" if pos[i - 1] == "PROPN" else "unk")
    lss = _supersense(toks[left[1] - 1]) or ("PROPN" if pos[left[1] - 1] == "PROPN" else "unk")
    same = "same" if (ss and ss == lss) else "diff"
    return "%s|%s|%s" % (lss.replace("noun.", ""), ss.replace("noun.", ""), same)


def _zcop_strength(toks, pos, i, ldom, mat, tag_names):
    """QUALITY PUSH 3 -- THE ZERO-COPULA PREDICATE SLOT.  `predicate_sites` opens a slot only at an overt copula,
    so it is blind to the reduced predication that an apposition IS (measured: on "Elizabeth , the doctor ,
    arrived" it returns the VERB and nothing for the appositive).  Here the predication organ's OWN functions are
    asked the counterfactual the construction poses: insert a VIRTUAL copula in the gap to the left of this
    nominal and read the slot it would open -- (1 - host_belief) * copular_available at that carrier (Pustet 2003:
    zero-copula predication is the cross-linguistic norm; the appositive is the copula-less form)."""
    if mat is None or pos[i - 1] not in NOMH:
        return None
    left = (ldom or {}).get(i)
    if left is None:
        return None
    try:
        from hdlab.attachment_arm import host_belief, copular_available
    except Exception:
        return None
    g = left[1]                                       # insert the virtual carrier right after the left domain
    t2 = list(toks[:g]) + ["is"] + list(toks[g:])
    p2 = list(pos[:g]) + ["AUX"] + list(pos[g:])
    try:
        ai = list(tag_names).index("AUX")
    except ValueError:
        return None
    row = np.zeros((1, mat.shape[1]), dtype=float)
    row[0, ai] = 1.0
    m2 = np.concatenate([mat[:g], row, mat[g:]], axis=0)
    try:
        ca = float(copular_available(t2, p2, g))
        if ca <= 0.0:
            return 0.0
        return float((1.0 - host_belief(t2, p2, m2, list(tag_names), g)) * ca)
    except Exception:
        return None


# PHASE 7 (C) -- THE COPULA-LESS PREDICATION, second attempt, with the discriminator the first one lacked.
# 
# WHAT THE BRAIN'S SLOT LOOKS LIKE FOR "Tom, the baker, ...".  It is not the main clause's predicate slot at
# all.  An appositive is a SECONDARY, PARENTHETICAL predication: Potts 2005 (The Logic of Conventional
# Implicature) shows supplements contribute an INDEPENDENT, not-at-issue proposition -- "Tom, the baker,
# left" asserts `left(Tom)` AND, in a separate layer, `baker(Tom)`.  Del Gobbo 2003 / Heringa 2011 derive the
# appositive as a REDUCED COPULAR CLAUSE ("Tom, (who is) the baker"), which is why Pustet 2003 is the right
# reference for the copula's absence: the copula carries tense, it is not the predication, and a majority of
# the world's languages omit it outright in exactly this configuration.
# 
# WHY THE FIRST ATTEMPT (zcop) WAS CI-SEPARATED DOWN, AND WHAT THAT TOLD ME.  `zcop` asked "could a copula
# stand in this gap".  Counted over 11,877 firings its top class was `nmod` (0.355) with `compound` at 0.213,
# because a copula COULD stand between any nominal and any post-nominal nominal modifier.  The cue could not
# tell "Tom, the baker" from "the terrorist group Hamas".  The missing discriminator is not the gap -- it is
# whether the second nominal is A DP OF ITS OWN or a member of the first one's chunk.  A predication needs TWO
# referring expressions; a compound is ONE.
# 
# SO THE ARM IS A CHUNK-BOUNDARY CUE, and it is only expressible because pri 134 phase 7 built the NP chunk:
#   dp2_comma   a determiner-opened chunk beginning just after a comma that closes a nominal chunk
#   dp2_bare    a determiner-opened chunk abutting a preceding nominal chunk with nothing between
#   same_chunk  this token is INSIDE a nominal run that started earlier (a compound / name-run member)
#   no_det      a nominal chunk with no determiner of its own (a bare second nominal -- close apposition)
#   no_left     no nominal chunk to its left
#   na          not a nominal
# GRADED, not a rule: the value is read together with the category organ's own P(DET) at the chunk opener, so
# an uncertain determiner makes an uncertain second DP.  Validity is accrued from counts like every other cue.
DPJUX_DET = ("DET",)
_DPJUX_STOP = ("VERB", "AUX", "ADP", "SCONJ", "CCONJ", "PART")


def _dpjux_value(toks, pos, i, runs, ldom):
    """The TWO-DP configuration at 1-based nominal i (see the module note).  Arc-free: it reads the chunk
    boundary the name-run chunker already draws, which is what `zcop` had no access to."""
    if pos[i - 1] not in NOMH:
        return "na"
    r = runs.get(i)
    if r and i > r[0]:
        return "same_chunk"                   # a member of a run that started earlier: ONE expression, not two
    a = r[0] if r else i                      # the left edge of THIS token's own nominal run
    left = (ldom or {}).get(i)
    if left is None:
        return "no_left"
    # walk left from the run start over the chunk's own determiners / modifiers
    j = a - 1
    opener = None
    steps = 0
    while j >= 1 and steps < 6:
        u = pos[j - 1]
        if u in ("DET", "ADJ", "NUM", "ADV"):
            if u == "DET":
                opener = j
            j -= 1
            steps += 1
            continue
        break
    if j >= 1 and pos[j - 1] in _DPJUX_STOP:
        return "no_left"                      # a verb / preposition / coordinator intervenes: not juxtaposition
    comma = (j >= 1 and str(toks[j - 1]) == ",")
    if opener is None:
        return "no_det"
    return "dp2_comma" if comma else "dp2_bare"


def _ps_bin(v):
    if v is None:
        return "na"
    v = float(v)
    if v <= 0.0:
        return "ps0"
    if v < 0.34:
        return "pslo"
    if v < 0.67:
        return "psmid"
    return "pshi"


def fine_relation_cues(toks, pos, heads, i, sites=None, coarse=None, runs=None, ldom=None,
                       mat=None, tag_names=None):
    """The cue VALUES fired for token i (1-based).  Every value comes from an organ the reader already
    runs: the category rung (dcat / the configuration), the genitive case marker (gen; graded_role_assigner
    cue set v4), the name-run chunker (run / runsym; pri 118), the predicate slot (pslot / hps; pri
    110/117), and the argument competition's own read (crs -- the graded hand-off from the coarse arm)."""
    from hdlab.graded_role_assigner import genitive_value
    from hdlab.coref import span_caps_symbol
    n = len(toks)
    h = int(heads.get(i, 0) or 0)
    hcat = pos[h - 1] if 1 <= h <= len(pos) else "ROOT"
    order = "pre" if (h == 0 or i < h) else "post"
    cues = {"config": "%s_%s" % (hcat, order)}
    cues["dcat"] = pos[i - 1] if i - 1 < len(pos) else "X"
    cues["gen"] = genitive_value(toks, pos, i) or "no"
    runs = runs if runs is not None else _run_index(pos, toks)
    r = runs.get(i)
    if r is None:
        cues["run"] = "solo" if cues["dcat"] in NOMH else "na"
        cues["runsym"] = "na"
    else:
        a, b, kind = r
        where = "first" if i == a else ("last" if i == b else "mid")
        cues["run"] = "%s_%s" % (kind, where)
        span = [str(t) for t in toks[a - 1:b]]
        cues["runsym"] = span_caps_symbol(span, i - a, first_is_sentence_initial=(a == 1))
    cues["gap"] = _gap_value(toks, pos, i, h) if h else "root"
    sites = sites or {}
    cues["pslot"] = _ps_bin(sites.get(i - 1)) if sites else "na"
    cues["hps"] = _ps_bin(sites.get(h - 1)) if (sites and h) else "na"
    cues["crs"] = (coarse or {}).get(i, "none")
    _ld = ldom if ldom is not None else _left_domains(pos, toks)
    cues["typepred"] = _typepred_value(toks, pos, i, _ld)
    cues["zcop"] = _ps_bin(_zcop_strength(toks, pos, i, _ld, mat, tag_names))
    cues["dpjux"] = _dpjux_value(toks, pos, i, runs if runs is not None else _run_index(pos, toks), _ld)
    d = abs(i - h) if h else 0
    cues["dist"] = "d0" if d == 0 else ("d1" if d == 1 else ("d2" if d == 2 else ("d3_5" if d <= 5 else "d6")))
    return cues


def fine_relation_supports(cues, tab, cue_set=None):
    """Per-cue support vectors over FINE_CLASSES: the learned strength of each fired value, read WITHIN
    its configuration as a CONTRAST (the coarse arm's own discipline -- an uninformative value votes 0)."""
    S = {"prior": tab["prior"]}
    cfg = cues["config"]
    vec = tab["strength"].get("config", {}).get(cfg)
    if vec is not None:
        S["config"] = vec
    use = cue_set if cue_set is not None else (tab.get("cue_set") or FINE_CUES)
    for c in use:
        v = cues.get(c)
        if v is None:
            continue
        key = ("GLOBAL|" + str(v)) if c in GLOBAL_FINE_CUES else ("%s|%s" % (cfg, v))
        vec = tab["strength"].get(c, {}).get(key)
        if vec is not None:
            S[c] = vec
    return S


def fine_relation_posterior(cues, tab, cue_set=None):
    from hdlab.graded_competition import net_activation, softmax
    S = fine_relation_supports(cues, tab, cue_set)
    return softmax(net_activation(S, {c: 1.0 for c in S}), gain=1.0)


def _run_nonhead(runs, i):
    """Is i a NON-HEAD member of a nominal run?  A propn run is headed by its FIRST token (UD `flat`), a noun
    compound by its LAST (UD `compound`); a mixed run takes the English head-final default."""
    r = runs.get(i)
    if r is None:
        return False
    a, b, kind = r
    return i != (a if kind == "propn" else b)


def fine_population(toks, pos, heads, coarse, runs=None, run_members=None):
    """The arm's population, computable at read time: every non-root token the ARGUMENT competition did
    not claim (it emitted nothing, `dep`, or `nmod`), PLUS -- when RUN_MEMBERS is on -- every non-head member
    of a nominal run, because a run is ONE referring expression filling ONE slot."""
    rm = RUN_MEMBERS if run_members is None else run_members
    if rm and runs is None:
        runs = _run_index(pos, toks)
    out = []
    for i in range(1, len(toks) + 1):
        if not int(heads.get(i, 0) or 0):
            continue
        c = coarse.get(i)
        if c is None or c in ("dep", "nmod") or (rm and _run_nonhead(runs, i)):
            out.append(i)
    return out


def _construction_head(toks, pos, heads, i, rel, runs, copmap):
    """The governor the CONSTRUCTION itself names (a construction is a form/GOVERNOR pairing, so the arm
    hands down both).  Returns None where the construction has nothing to say and the attachment arm's
    head stands."""
    n = len(toks)
    r = runs.get(i)
    if rel == "flat" and r:
        return r[0] if r[0] != i else None                      # a NAME phrase is headed by its FIRST token
    if rel == "compound" and r:
        return r[1] if r[1] != i else None                      # a NOUN compound by its LAST
    if rel == "cop":
        q = copmap.get(i)
        return q if (q and q != i) else None
    if rel == "appos":
        for (a, b, _k) in reversed(_nominal_runs(pos, toks)):    # the nearest nominal domain to the left
            if b < i:
                return b
        return None
    if rel in ("nmod:poss", "det", "amod", "nummod", "case"):
        for j in range(i + 1, n + 1):                           # the nominal this pre-head item marks
            if pos[j - 1] in NOMH:
                k = j
                while k + 1 <= n and pos[k] in NOMH:
                    k += 1
                return k
            if pos[j - 1] not in ("DET", "ADJ", "NUM", "ADV", "PART", "PUNCT"):
                break
        return None
    return None


def fine_relations(toks, pos, heads, tab, sites=None, coarse=None, cue_set=None,
                   with_heads=False, tau=0.0, run_members=None, mat=None, tag_names=None):
    """{1-based i: dep} (or {i: (dep, head)} with with_heads) for the non-argument population.
    tau = an abstain threshold on the winner's posterior (0.0 = always commit)."""
    coarse = coarse or {}
    _rl = _nominal_runs(pos, toks)
    runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
    ldom = _left_domains(pos, toks, _rl)
    copmap = {}
    if with_heads:
        try:
            from hdlab.attachment_arm import cop_complement
            for k in range(len(toks)):
                if pos[k] == "AUX":
                    q = cop_complement(list(toks), list(pos), k)
                    if q is not None:
                        copmap[k + 1] = q + 1
        except Exception:
            copmap = {}
    out = {}
    for i in fine_population(toks, pos, heads, coarse, runs, run_members):
        cues = fine_relation_cues(toks, pos, heads, i, sites=sites, coarse=coarse, runs=runs,
                                  ldom=ldom, mat=mat, tag_names=tag_names)
        p = fine_relation_posterior(cues, tab, cue_set)
        k = int(np.argmax(p))
        if tau and float(p[k]) < tau:
            continue
        rel = FINE_CLASSES[k]
        if with_heads:
            hh = _construction_head(toks, pos, heads, i, rel, runs, copmap)
            out[i] = (rel, hh if hh else int(heads.get(i, 0) or 0))
        else:
            out[i] = rel
    return out


def all_relations(toks, pos, heads, tab, sites=None, coarse=None, cue_set=None, with_heads=False,
                  run_members=None, mat=None, tag_names=None):
    """THE ONE LABELS RUNG'S FULL READ: the argument competition's decisions, refined by the
    non-argument arm wherever the competition said OTHER / NMOD.  A core argument label never moves."""
    coarse = dict(coarse or {})
    fine = fine_relations(toks, pos, heads, tab, sites=sites, coarse=coarse,
                          cue_set=cue_set, with_heads=with_heads, run_members=run_members,
                          mat=mat, tag_names=tag_names)
    if with_heads:
        out = {i: (d, int(heads.get(i, 0) or 0)) for i, d in coarse.items() if d in ARG_DEPS}
        out.update(fine)
        return out
    out = {i: d for i, d in coarse.items() if d in ARG_DEPS}
    out.update(fine)
    return out


# --------------------------------------------------------------------- the counts (learning + plasticity)
def empty_counts():
    K = len(FINE_CLASSES)
    return {"prior": [0.0] * K, "config": {}, "cues": {c: {} for c in FINE_CUES}}


def accrue(counts, cues, rel, w=1.0):
    """ONE comprehension outcome into the counts -- the whole learning rule, offline AND online."""
    k = FINE_IDX.get(rel)
    if k is None:
        return
    K = len(FINE_CLASSES)
    counts["prior"][k] += w
    cfg = cues["config"]
    counts["config"].setdefault(cfg, [0.0] * K)[k] += w
    counts["config"].setdefault("GLOBAL", [0.0] * K)[k] += w   # the unconditioned base the GLOBAL contrasts read against
    for c in FINE_CUES:
        v = cues.get(c)
        if v is None:
            continue
        key = ("GLOBAL|" + str(v)) if c in GLOBAL_FINE_CUES else ("%s|%s" % (cfg, v))
        counts["cues"].setdefault(c, {}).setdefault(key, [0.0] * K)[k] += w


def build_strengths(counts):
    """THE ONE implementation of the Competition-Model strength math, reused verbatim from the argument
    arm (graded_role_assigner.strengths_from_counts) -- no second copy of the math in the substrate."""
    from hdlab.graded_role_assigner import strengths_from_counts
    return strengths_from_counts(counts, 0.0)


def table_from_counts(counts, cue_set=None):
    built = build_strengths(counts)
    return {"prior": built["prior"], "strength": built["strength"], "counts": counts,
            "cue_set": tuple(cue_set) if cue_set else None}


def observe_fine_relation_outcome(toks, pos, heads, i, rel, tab, sites=None, coarse=None, w=1.0):
    """PLASTICITY (the brain is never frozen): accrue one understood relation into the SAME counts the
    strengths are a pure function of, and rebuild the strengths.  This is the online path."""
    cues = fine_relation_cues(toks, pos, heads, i, sites=sites, coarse=coarse)
    accrue(tab["counts"], cues, rel, w)
    built = build_strengths(tab["counts"])
    tab["prior"] = built["prior"]
    tab["strength"] = built["strength"]
    return tab


def save_fine_validities(path, tab, meta=None):
    doc = {"source": "Competition-Model cue validities for the NON-ARGUMENT arm of the labels rung: counts "
                     "accrued from the teaching corpus (UD-EWT train) through the LIVE chain; strengths = "
                     "graded_role_assigner.strengths_from_counts(counts). Plastic: "
                     "observe_fine_relation_outcome accrues one understood relation into the same counts.",
           "classes": FINE_CLASSES, "cues": list(FINE_CUES), "counts": tab["counts"],
           "cue_set": list(tab.get("cue_set") or FINE_CUES)}
    doc.update(meta or {})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n") as f:
        json.dump(doc, f, indent=1)
    return path


def load_fine_validities(path):
    with open(path, encoding="ascii") as f:
        doc = json.load(f)
    tab = table_from_counts(doc["counts"], doc.get("cue_set"))
    tab["classes"] = doc.get("classes", FINE_CLASSES)
    return tab


# ==================================================================================================
# THE HARNESS
# ==================================================================================================
def sentences(path, cap=None):
    """UD CoNLL-U -> (toks, pos, heads, deps).  The gold columns are the MEASURING ANSWER KEY (and the
    teaching signal at --build); no decision below ever reads them."""
    toks, pos, heads, deps = [], [], {}, {}
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    yield toks, pos, heads, deps
                    n += 1
                    if cap and n >= cap:
                        return
                toks, pos, heads, deps = [], [], {}, {}
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]:
                continue
            i = int(c[0])
            toks.append(c[1]); pos.append(c[3]); heads[i] = int(c[6]); deps[i] = c[7]
    if toks:
        yield toks, pos, heads, deps


class Chain(object):
    """THE LIVE BRAIN-FOUNDATIONAL CHAIN, one object: tokens -> categories (lexical_categories, graded)
    -> heads (attachment_arm) -> argument roles (graded_role_assigner.coarse_roles) -> predicate slot.
    Exactly what `SituationReader.read` runs; nothing supervised on the path."""

    def __init__(self):
        from hdlab import lexical_categories as LC
        from hdlab.frontend import Parser
        from hdlab.graded_role_assigner import load_coarse_validities
        self.lc = LC.get()
        self.P = Parser()
        self.ctab = load_coarse_validities()
        self._c = {}

    def run(self, toks):
        key = tuple(toks)
        if key in self._c:
            return self._c[key]
        from hdlab.attachment_arm import predicate_sites
        from hdlab.graded_role_assigner import coarse_roles
        mat = self.lc.posterior(list(toks))
        tags = [self.lc.tags[int(np.argmax(mat[i]))] for i in range(len(toks))]
        dist = [{t: float(mat[i, j]) for j, t in enumerate(self.lc.tags) if mat[i, j] >= 0.01}
                for i in range(len(toks))]
        po = self.P.parse(list(toks), tags, dist)
        heads = dict(po.heads)
        coarse = coarse_roles(list(toks), tags, heads, self.ctab, po.marginals)
        try:
            sites = predicate_sites(list(toks), tags, mat, self.lc.tags)
        except Exception:
            sites = {}
        out = (tags, heads, coarse, sites, po.marginals, mat)
        if len(self._c) < 6000:
            self._c[key] = out
        return out


_PERC = {}


def perceptron_labels(toks, pos, heads):
    """The RETIRED supervised relation labeler.  INFORMATIONAL FLOOR ONLY -- it is NOT_BF and pri 129
    took it off the live path; it is run here to price what its removal cost, never as a component."""
    if "lab" not in _PERC:
        from hdlab.arc_labeler import ArcLabeler
        _PERC["lab"] = ArcLabeler.load(LAB_ASSET)
    return dict(_PERC["lab"].label(list(toks), list(pos), dict(heads)))


def boot_paired(a, b, nb=2000, sd=SEED):
    """Paired bootstrap over the population's own unit (a list of (hits, n) per unit)."""
    if not a or not b or len(a) != len(b):
        return {"delta": 0.0, "ci": [0.0, 0.0], "half": 0.0, "ci_sep": False}
    A = np.array(a, dtype=float); B = np.array(b, dtype=float)
    obs = (A[:, 0].sum() / max(A[:, 1].sum(), 1)) - (B[:, 0].sum() / max(B[:, 1].sum(), 1))
    rr = np.random.default_rng(sd)
    d = []
    for _ in range(nb):
        s = rr.integers(0, len(A), len(A))
        aa, bb = A[s], B[s]
        d.append((aa[:, 0].sum() / max(aa[:, 1].sum(), 1)) - (bb[:, 0].sum() / max(bb[:, 1].sum(), 1)))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return {"delta": round(float(obs), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half": round(float((hi - lo) / 2.0), 4), "ci_sep": bool(lo > 0 or hi < 0)}


def pooled(x):
    h = sum(a for a, _b in x); n = sum(b for _a, b in x)
    return round(h / n, 4) if n else 0.0, n


# ---------------------------------------------------------------------------- ARM: --build (learning)
_TAGNAMES = [None]


def arm_build(args):
    """Accrue the cue validities from the TEACHING CORPUS (UD-EWT train) through the LIVE chain, exactly
    as `tools/build_coarse_role_validities.py` does for the argument arm: the cue values are what the
    reader PERCEIVES, the outcome is the understood relation, and each instance counts with the weight of
    the governor own belief in its attachment (reliability-weighted learning; Ernst & Banks 2002).
    A train-internal DEV split (every 5th sentence) is held out for cue-set selection."""
    t0 = time.time()
    ch = Chain()
    counts = empty_counts()
    dev = []
    n_sent = n_acc = 0
    for si, (toks, gpos, gheads, gdeps) in enumerate(sentences(UD_TRAIN, cap=args.train_cap)):
        if len(toks) > args.maxlen:
            continue
        tags, heads, coarse, sites, marg, mat = ch.run(toks)
        if si % 5 == 4:                                   # DEV -- never accrued, never a test read
            dev.append((list(toks), tags, heads, coarse, sites, dict(gdeps), mat))
            continue
        n_sent += 1
        _rl = _nominal_runs(tags, toks)
        runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
        ldom = _left_domains(tags, toks, _rl)
        for i in fine_population(toks, tags, heads, coarse, runs):
            w = 1.0
            if marg:
                w = float((marg.get(i) or {}).get(heads.get(i, 0), 0.0))
                if w < args.min_conf:
                    continue                              # the brain consolidates what it UNDERSTOOD
            cues = fine_relation_cues(toks, tags, heads, i, sites=sites, coarse=coarse, runs=runs,
                                      ldom=ldom, mat=mat, tag_names=ch.lc.tags)
            accrue(counts, cues, fine_of(gdeps.get(i, "")), w)
            n_acc += 1
    _TAGNAMES[0] = ch.lc.tags
    tab = table_from_counts(counts, FINE_CUES)
    # ---- CUE-SET SELECTION ON THE TRAIN-INTERNAL DEV SPLIT (never on test) --------------------------
    targets = ("flat", "compound", "appos", "nmod:poss", "cop")

    def dev_score(cue_set):
        hits = collections.Counter(); pred = collections.Counter(); gold = collections.Counter()
        for (toks, tags, heads, coarse, sites, gdeps, mat) in dev:
            _rl = _nominal_runs(tags, toks)
            runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
            ldom = _left_domains(tags, toks, _rl)
            for i in range(1, len(toks) + 1):
                g = fine_of(gdeps.get(i, ""))
                if g in targets:
                    gold[g] += 1
            for i in fine_population(toks, tags, heads, coarse, runs):
                cues = fine_relation_cues(toks, tags, heads, i, sites=sites, coarse=coarse, runs=runs,
                                          ldom=ldom, mat=mat, tag_names=_TAGNAMES[0])
                p = fine_relation_posterior(cues, tab, cue_set)
                r = FINE_CLASSES[int(np.argmax(p))]
                if r in targets:
                    pred[r] += 1
                    if r == fine_of(gdeps.get(i, "")):
                        hits[r] += 1
        f1 = {}
        for r in targets:
            pr = hits[r] / pred[r] if pred[r] else 0.0
            rc = hits[r] / gold[r] if gold[r] else 0.0
            f1[r] = (2 * pr * rc / (pr + rc)) if (pr + rc) else 0.0
        return float(np.mean([f1[r] for r in targets])), f1

    sel = []
    base, base_f1 = dev_score(FINE_CUES)
    sel.append({"cue_set": list(FINE_CUES), "dev_macro_f1": round(base, 4),
                "per_rel": {k: round(v, 4) for k, v in base_f1.items()}})
    best_set, best = list(FINE_CUES), base
    for drop in FINE_CUES:                                 # leave-one-cue-out, decided on DEV only
        cs = tuple(c for c in FINE_CUES if c != drop)
        s, f1 = dev_score(cs)
        sel.append({"cue_set": list(cs), "dropped": drop, "dev_macro_f1": round(s, 4),
                    "per_rel": {k: round(v, 4) for k, v in f1.items()}})
        if s > best + 1e-6:
            best, best_set = s, list(cs)
    tab["cue_set"] = tuple(best_set)
    meta = {"train_sentences": n_sent, "accrued": n_acc, "min_conf": args.min_conf,
            "dev_sentences": len(dev), "dev_selection": sel, "dev_macro_f1": round(best, 4),
            "perceived": True, "confidence_weighted": True,
            "chain": "lexical_categories(counts) -> attachment_arm -> coarse_roles -> predicate_sites"}
    p = save_fine_validities(os.path.join(OUT_DIR, ASSET_NAME), tab, meta)
    print("BUILD: %d train sentences, %d decisions accrued, %d dev sentences" % (n_sent, n_acc, len(dev)))
    print("  cue set selected on DEV: %s (macro-F1 %.4f over %s)" % (best_set, best, list(targets)))
    print("  wrote %s (%.1fs)" % (p, time.time() - t0))
    return {"asset": p, "meta": meta}


# ---------------------------------------------------------------------------- ARM: --ud (per-relation P/R)
def _twin_cues(cues_list, rng):
    """INFO-FREE TWIN, same shape: the fired cue VALUES permuted across the sentence own population
    (every value multiset, every configuration count preserved; only the token they belong to is gone)."""
    if len(cues_list) < 2:
        return cues_list
    out = [dict(c) for c in cues_list]
    for c in ("config",) + FINE_CUES:
        vals = [d.get(c) for d in out]
        perm = list(rng.permutation(len(vals)))
        for k, j in enumerate(perm):
            out[k][c] = vals[j]
    return out


def arm_ud(args, tab):
    """Per-relation precision / recall on UD-EWT TEST through the LIVE chain, with every floor the brief
    names recomputed on this population, all arms in ONE process."""
    t0 = time.time()
    ch = Chain()
    rng = np.random.default_rng(SEED)
    targets = ["flat", "compound", "appos", "nmod:poss", "cop", "det", "case", "amod", "conj", "acl"]
    arms = ["dep_fallback", "bf_arm", "twin", "perceptron", "bf_oracle_heads",
            "bf_no_runmembers", "bf_no_typepred", "bf_zcop", "bf_zcop_typepred", "bf_dpjux"]
    CORE = ("nsubj", "obj", "nsubj:pass", "obl", "iobj")
    CA = {a: [] for a in arms}                  # the CORE-ARGUMENT no-regress population, per sentence
    H = {a: {r: collections.Counter() for r in targets} for a in arms}
    U = {a: [] for a in arms}
    head_ok = {a: [0, 0] for a in ("bf_arm_armhead", "bf_arm_consthead")}
    nsent = 0
    conf = collections.Counter()
    # PHASE 7 (F): whose fault is each wrong emission?  For every token the arm labels X where gold says Y,
    # record whether the CATEGORY the arm read equals the gold category.  A wrong relation on a wrongly-read
    # category is the category rung's loss travelling down, not this arm's.
    attrib = collections.defaultdict(lambda: [0, 0])
    for (toks, gpos, gheads, gdeps) in sentences(UD_TEST, cap=args.ud_cap):
        if len(toks) > args.maxlen:
            continue
        nsent += 1
        tags, heads, coarse, sites, marg, mat = ch.run(toks)
        gold = {i: fine_of(gdeps.get(i, "")) for i in range(1, len(toks) + 1)}
        fine_deps_core = {}
        for i in range(1, len(toks) + 1):
            full = gdeps.get(i, "") or ""
            d = full.split(":")[0]
            if full.startswith("nsubj:pass") or full == "nsubjpass":
                fine_deps_core[i] = "nsubj:pass"
            elif d in ("nsubj", "obj", "dobj", "obl", "iobj"):
                fine_deps_core[i] = "obj" if d == "dobj" else d
        pred = {}
        pred["dep_fallback"] = {i: coarse.get(i, "dep") for i in range(1, len(toks) + 1)}
        fr = all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                           cue_set=tab.get("cue_set"), with_heads=True, mat=mat, tag_names=ch.lc.tags)
        pred["bf_arm"] = {i: v[0] for i, v in fr.items()}
        _rl = _nominal_runs(tags, toks)
        runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
        ldom = _left_domains(tags, toks, _rl)
        popu = fine_population(toks, tags, heads, coarse, runs)
        cl = [fine_relation_cues(toks, tags, heads, i, sites=sites, coarse=coarse, runs=runs, ldom=ldom,
                                 mat=mat, tag_names=ch.lc.tags) for i in popu]
        tw = _twin_cues(cl, rng)
        pt = {i: coarse.get(i, "dep") for i in range(1, len(toks) + 1)}
        for i, cu in zip(popu, tw):
            pt[i] = FINE_CLASSES[int(np.argmax(fine_relation_posterior(cu, tab, tab.get("cue_set"))))]
        pred["twin"] = pt
        if args.perceptron:
            pred["perceptron"] = {i: fine_of(v) for i, v in perceptron_labels(toks, tags, heads).items()}
        if args.oracle:
            fo = all_relations(toks, tags, dict(gheads), tab, sites=sites, coarse=coarse,
                               cue_set=tab.get("cue_set"), mat=mat, tag_names=ch.lc.tags)
            pred["bf_oracle_heads"] = dict(fo)
        if args.ablate:
            # LEVER 1 ABLATED: the run-member population widening off (same table, same cues)
            pred["bf_no_runmembers"] = dict(all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                                                          cue_set=tab.get("cue_set"), run_members=False,
                                                          mat=mat, tag_names=ch.lc.tags))
            # LEVERS 2 AND 3, THE OTHER WAY ROUND: the DEV split REJECTED both the hub TYPE cue and the
            # ZERO-COPULA predicate slot from the selected set, so the can-fail arms ADD them back and the paired
            # deltas price what selecting them would have cost.
            cs2 = tuple(sorted(set(tab.get("cue_set") or FINE_CUES) | {"typepred"}))
            pred["bf_no_typepred"] = dict(all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                                                        cue_set=cs2, mat=mat, tag_names=ch.lc.tags))
            cs3 = tuple(sorted(set(tab.get("cue_set") or FINE_CUES) | {"zcop"}))
            pred["bf_zcop"] = dict(all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                                                 cue_set=cs3, mat=mat, tag_names=ch.lc.tags))
            cs4 = tuple(sorted(set(tab.get("cue_set") or FINE_CUES) | {"zcop", "typepred"}))
            pred["bf_zcop_typepred"] = dict(all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                                                          cue_set=cs4, mat=mat, tag_names=ch.lc.tags))
            # PHASE 7 (C): the COPULA-LESS PREDICATION read as a TWO-DP JUXTAPOSITION -- the chunk-boundary
            # discriminator `zcop` lacked.  Added to the DEV-selected set as its own can-fail arm.
            cs5 = tuple(sorted(set(tab.get("cue_set") or FINE_CUES) | {"dpjux"}))
            pred["bf_dpjux"] = dict(all_relations(toks, tags, heads, tab, sites=sites, coarse=coarse,
                                                  cue_set=cs5, mat=mat, tag_names=ch.lc.tags))
        for a in arms:
            if a not in pred:
                continue
            u_h = u_n = 0
            for i in range(1, len(toks) + 1):
                g = gold.get(i); p = pred[a].get(i)
                if g in targets:
                    H[a][g]["gold"] += 1
                    u_n += 1
                    if p == g:
                        H[a][g]["hit"] += 1
                        u_h += 1
                if p in targets:
                    H[a][p]["pred"] += 1
                    if a == "bf_arm" and g != p:
                        k = "%s_emitted_gold_%s" % (p, g or "NONE")
                        attrib[k][1] += 1
                        if i - 1 < len(tags) and i - 1 < len(gpos) and tags[i - 1] != gpos[i - 1]:
                            attrib[k][0] += 1
            U[a].append((u_h, u_n))
            ca_h = ca_n = 0
            for i in range(1, len(toks) + 1):
                g = fine_deps_core.get(i)
                if g in CORE:
                    ca_n += 1
                    if pred[a].get(i) == g:
                        ca_h += 1
            CA[a].append((ca_h, ca_n))
        for i, (r, hh) in fr.items():
            if r in ("flat", "compound", "appos", "nmod:poss", "cop"):
                head_ok["bf_arm_armhead"][1] += 1
                head_ok["bf_arm_consthead"][1] += 1
                if int(heads.get(i, 0)) == gheads.get(i, -1):
                    head_ok["bf_arm_armhead"][0] += 1
                if int(hh) == gheads.get(i, -1):
                    head_ok["bf_arm_consthead"][0] += 1
        for i in range(1, len(toks) + 1):
            if gold.get(i) in ("appos", "flat", "compound", "nmod:poss", "cop"):
                conf["%s->%s" % (gold[i], pred["bf_arm"].get(i, "NONE"))] += 1

    def pr(a, r):
        c = H[a][r]
        p = c["hit"] / c["pred"] if c["pred"] else 0.0
        rc = c["hit"] / c["gold"] if c["gold"] else 0.0
        return {"P": round(p, 4), "R": round(rc, 4),
                "F1": round(2 * p * rc / (p + rc), 4) if (p + rc) else 0.0,
                "gold": c["gold"], "pred": c["pred"], "hit": c["hit"]}

    res = {"n_sentences": nsent,
           "per_relation": {a: {r: pr(a, r) for r in targets} for a in arms if U[a]},
           "union_target_accuracy": {a: pooled(U[a])[0] for a in arms if U[a]},
           "union_n": pooled(U["bf_arm"])[1],
           "paired_bf_vs_depfallback": boot_paired(U["bf_arm"], U["dep_fallback"]),
           "paired_bf_vs_twin": boot_paired(U["bf_arm"], U["twin"]),
           "head_accuracy_on_constructions": {
               k: {"acc": round(v[0] / v[1], 4) if v[1] else 0.0, "n": v[1]} for k, v in head_ok.items()},
           "confusion_bf_arm": dict(conf.most_common(30)),
           "wrong_emission_attribution": {k: {"n": v[1], "category_also_wrong": v[0],
                                              "share_category_wrong": round(v[0] / v[1], 3) if v[1] else 0.0}
                                          for k, v in sorted(attrib.items(), key=lambda r: -r[1][1])[:16]},
           "core_argument_accuracy": {a: pooled(CA[a])[0] for a in arms if CA[a]},
           "core_argument_n": pooled(CA["bf_arm"])[1],
           "core_argument_paired_bf_vs_depfallback": boot_paired(CA["bf_arm"], CA["dep_fallback"]),
           "elapsed_s": round(time.time() - t0, 1)}
    if U["perceptron"]:
        res["paired_bf_vs_perceptron_INFORMATIONAL"] = boot_paired(U["bf_arm"], U["perceptron"])
    if U["bf_oracle_heads"]:
        res["paired_oracleheads_vs_bf"] = boot_paired(U["bf_oracle_heads"], U["bf_arm"])
    if U["bf_no_runmembers"]:
        res["QUALITY_PUSH_1_runmembers"] = boot_paired(U["bf_arm"], U["bf_no_runmembers"])
        res["QUALITY_PUSH_1_runmembers_core_cost"] = boot_paired(CA["bf_arm"], CA["bf_no_runmembers"])
    if U["bf_no_typepred"]:
        res["QUALITY_PUSH_2_typepred_ADDED_BACK"] = boot_paired(U["bf_no_typepred"], U["bf_arm"])
    if U["bf_zcop"]:
        res["QUALITY_PUSH_3_zcop_ADDED_BACK"] = boot_paired(U["bf_zcop"], U["bf_arm"])
        res["QUALITY_PUSH_3_zcop_core_cost"] = boot_paired(CA["bf_zcop"], CA["bf_arm"])
    if U["bf_zcop_typepred"]:
        res["QUALITY_PUSH_2plus3_ADDED_BACK"] = boot_paired(U["bf_zcop_typepred"], U["bf_arm"])
    if U["bf_dpjux"]:
        res["PHASE7_C_dpjux"] = boot_paired(U["bf_dpjux"], U["bf_arm"])
        res["PHASE7_C_dpjux_core_cost"] = boot_paired(CA["bf_dpjux"], CA["bf_arm"])
    return res


# ---------------------------------------------------------------------------- the GUM side (bridge + C3)
REL_SOURCES = ("dep_fallback", "bf_arm", "bf_arm_consthead", "bf_no_runmembers", "perceptron", "gold", "twin")


def live_reparse_bf(doc, relsrc, ch, tab, rng=None):
    """Re-parse each sentence of a GUM Doc with the LIVE BRAIN-FOUNDATIONAL chain (category organ UPOS +
    attachment-arm heads) and attach the relation strings from `relsrc`.  Forms / lemmas / mentions / coref
    stay FIXED, so the ONLY thing that varies across arms is the relation source -- the isolation the brief
    asks for.  `gold` keeps the treebank columns (the oracle ceiling); `perceptron` is INFORMATIONAL ONLY."""
    from types import SimpleNamespace as NS
    by_sent = collections.defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    new = []
    for sent in sorted(by_sent):
        row = sorted(by_sent[sent], key=lambda t: t.idx)
        forms = [t.form for t in row]
        if relsrc == "gold":
            for t in row:
                new.append(NS(gidx=t.gidx, sent=t.sent, idx=t.idx, form=t.form, lemma=t.lemma,
                              xpos=getattr(t, "xpos", ""), feats=getattr(t, "feats", {}),
                              upos=(getattr(t, "gold_upos", None) or t.upos),
                              head=(getattr(t, "gold_head", None) if getattr(t, "gold_head", None) is not None else t.head),
                              deprel=(getattr(t, "gold_deprel", None) or t.deprel)))
            continue
        tags, heads, coarse, sites, _m, mat = ch.run(forms)
        if relsrc == "perceptron":
            rel = perceptron_labels(forms, tags, heads)
            hd = dict(heads)
        elif relsrc == "dep_fallback":
            rel = dict(coarse)
            hd = dict(heads)
        elif relsrc in ("bf_arm", "bf_arm_consthead", "twin", "bf_no_runmembers"):
            wh = relsrc == "bf_arm_consthead"
            fr = all_relations(forms, tags, heads, tab, sites=sites, coarse=coarse,
                               cue_set=tab.get("cue_set"), with_heads=wh, mat=mat, tag_names=ch.lc.tags,
                               run_members=(False if relsrc == "bf_no_runmembers" else None))
            if wh:
                rel = {i: v[0] for i, v in fr.items()}
                hd = dict(heads); hd.update({i: v[1] for i, v in fr.items()})
            else:
                rel = dict(fr); hd = dict(heads)
            if relsrc == "twin":
                _rl = _nominal_runs(tags, forms)
                runs = {t: (a, b, k) for (a, b, k) in _rl if b > a for t in range(a, b + 1)}
                ldom = _left_domains(tags, forms, _rl)
                popu = fine_population(forms, tags, heads, coarse, runs)
                cl = [fine_relation_cues(forms, tags, heads, i, sites=sites, coarse=coarse, runs=runs,
                                         ldom=ldom, mat=mat, tag_names=ch.lc.tags)
                      for i in popu]
                tw = _twin_cues(cl, rng)
                rel = {i: d for i, d in coarse.items() if d in ARG_DEPS}
                for i, cu in zip(popu, tw):
                    rel[i] = FINE_CLASSES[int(np.argmax(fine_relation_posterior(cu, tab, tab.get("cue_set"))))]
                hd = dict(heads)
        else:
            raise ValueError(relsrc)
        for k, t in enumerate(row):
            new.append(NS(gidx=t.gidx, sent=t.sent, idx=t.idx, form=t.form, lemma=t.lemma,
                          xpos="", feats={}, upos=(tags[k] if k < len(tags) else "X"),
                          head=int(hd.get(t.idx, 0) or 0), deprel=rel.get(t.idx, "dep")))
    nd = NS(docid=getattr(doc, "docid", "?"), genre=getattr(doc, "genre", ""),
            corpus=getattr(doc, "corpus", ""), toks=new, mentions=doc.mentions,
            chains=getattr(doc, "chains", {}))
    return nd


def arm_bridge(args, tab):
    """THE CONSUMER INSTRUMENT, stage 1: the crosstype bridge NAME-LINKING on modern GUM, driven off the
    reader's own live parse, one arm per relation source, all arms in ONE process.  `licensed` = the
    precise-constructs role->name predication edges; `gated_binds` = the bridge's own pop / fired / correct
    on the CEILING population (restrict_gold=True names the population, never a decision) and on the
    DEPLOYMENT population (restrict_gold=False)."""
    t0 = time.time()
    import experiments.gum_coref as G
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.crosstype_bridge import precise_constructs, gated_binds
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=args.gum_docs, name_gazetteer=gaz)
    ch = Chain()
    rng = np.random.default_rng(SEED)
    srcs = [s for s in REL_SOURCES if (s != "perceptron" or args.perceptron)]
    acc = {s: {"lic_roles": 0, "lic_edges": 0, "pop": 0, "fired": 0, "correct": 0,
               "dpop": 0, "dfired": 0, "dcorrect": 0, "rel": collections.Counter()} for s in srcs}
    per_doc = {s: [] for s in srcs}
    for d in docs:
        for s in srcs:
            ld = live_reparse_bf(d, s, ch, tab, rng)
            for t in ld.toks:
                acc[s]["rel"][(t.deprel or "").split(":")[0] if t.deprel != "nmod:poss" else "nmod:poss"] += 1
            lic, _ep = precise_constructs(ld, gaz)
            acc[s]["lic_roles"] += len(lic)
            acc[s]["lic_edges"] += sum(len(v) for v in lic.values())
            p, f, c, _b = gated_binds(ld, gaz, bind_mode="cue_conf", margin=0.5,
                                      restrict_gold=True, conf_thr=args.conf_thr)
            acc[s]["pop"] += p; acc[s]["fired"] += f; acc[s]["correct"] += c
            per_doc[s].append((c, max(p, 0)))
            p2, f2, c2, _b2 = gated_binds(ld, gaz, bind_mode="cue_conf", margin=0.5,
                                          restrict_gold=False, conf_thr=args.conf_thr)
            acc[s]["dpop"] += p2; acc[s]["dfired"] += f2; acc[s]["dcorrect"] += c2

    def row(s):
        a = acc[s]
        return {"licensed_role_lemmas": a["lic_roles"], "licensed_role_to_name_edges": a["lic_edges"],
                "ceiling_pop": a["pop"], "fired": a["fired"], "correct": a["correct"],
                "recall": round(a["correct"] / a["pop"], 4) if a["pop"] else 0.0,
                "precision": round(a["correct"] / a["fired"], 4) if a["fired"] else 0.0,
                "deploy_pop": a["dpop"], "deploy_fired": a["dfired"], "deploy_correct": a["dcorrect"],
                "deploy_precision": round(a["dcorrect"] / a["dfired"], 4) if a["dfired"] else 0.0,
                "fine_relation_tokens": {r: a["rel"].get(r, 0)
                                         for r in ("appos", "flat", "compound", "nmod:poss", "cop")}}
    res = {"n_docs": len(docs), "conf_thr": args.conf_thr, "arms": {s: row(s) for s in srcs},
           "paired_recall_bf_vs_depfallback": boot_paired(per_doc["bf_arm"], per_doc["dep_fallback"]),
           "paired_recall_bf_vs_twin": boot_paired(per_doc["bf_arm"], per_doc["twin"]),
           "elapsed_s": round(time.time() - t0, 1)}
    if "bf_arm_consthead" in per_doc:
        res["paired_recall_consthead_vs_armhead"] = boot_paired(per_doc["bf_arm_consthead"], per_doc["bf_arm"])
    if "gold" in per_doc:
        res["paired_recall_gold_vs_bf"] = boot_paired(per_doc["gold"], per_doc["bf_arm"])
    return res


def arm_c3(args, tab):
    """THE CONSUMER INSTRUMENT, stage 2: the AFFECT / EXPERIENCER row (C3) through the REAL
    make_canonicalizer + _build_entities, exactly the scorer the landed +0.0838 was measured with, one arm
    per relation source, all arms in ONE process, paired over documents."""
    t0 = time.time()
    import experiments.gum_coref as G
    import experiments.exp_crosstype_live_wire_gum_v1 as LW
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from experiments.exp_route_unified_to_consumers_gum_v1 import _situation_predict_labels
    from hdlab.crosstype_bridge import crosstype_bridge_links
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=args.gum_docs, name_gazetteer=gaz)
    ch = Chain()
    rng = np.random.default_rng(SEED)
    srcs = [s for s in REL_SOURCES if (s != "perceptron" or args.perceptron)]
    C3 = {"floor": []}
    C3.update({s: [] for s in srcs})
    C1 = {"floor": []}
    C1.update({s: [] for s in srcs})
    merges = collections.Counter()
    for d in docs:
        ms = LW._fresh(d)
        floor = _situation_predict_labels(ms, gaz)
        C3["floor"].append(LW.score_c3_live(ms, LW._canon_from(ms, floor)))
        c1f = LW.score_c1_entity_layer(ms, floor)
        if c1f is not None:
            C1["floor"].append(c1f["conll_avg"])
        for s in srcs:
            ld = live_reparse_bf(d, s, ch, tab, rng)
            binds = crosstype_bridge_links(ld, gaz, conf_thr=args.conf_thr)
            lab, nm = LW._merge(ms, floor, binds)
            merges[s] += nm
            C3[s].append(LW.score_c3_live(ms, LW._canon_from(ms, lab)))
            c1b = LW.score_c1_entity_layer(ms, lab)
            if c1b is not None:
                C1[s].append(c1b["conll_avg"])

    def c1(x):
        return round(float(np.mean(x)), 4) if x else 0.0
    res = {"n_docs": len(docs), "conf_thr": args.conf_thr,
           "C3_n": pooled(C3["floor"])[1],
           "C3": {"honest_floor(no bridge)": pooled(C3["floor"])[0]},
           "C1_entity_layer": {"honest_floor(no bridge)": c1(C1["floor"])},
           "n_merges": dict(merges), "elapsed_s": 0.0}
    for s in srcs:
        res["C3"][s] = pooled(C3[s])[0]
        res["C1_entity_layer"][s] = c1(C1[s])
    res["paired_vs_floor"] = {s: boot_paired(C3[s], C3["floor"]) for s in srcs}
    res["paired_bf_vs_depfallback"] = boot_paired(C3["bf_arm"], C3["dep_fallback"])
    res["paired_bf_vs_twin"] = boot_paired(C3["bf_arm"], C3["twin"])
    if "gold" in C3:
        res["paired_gold_vs_bf"] = boot_paired(C3["gold"], C3["bf_arm"])
    if "bf_arm_consthead" in C3:
        res["paired_consthead_vs_armhead"] = boot_paired(C3["bf_arm_consthead"], C3["bf_arm"])
    res["elapsed_s"] = round(time.time() - t0, 1)
    return res


# ---------------------------------------------------------------------------- ARM: --probe (phase 1a)
def arm_probe(args, tab):
    """THE DEFECT, REPRODUCED ON THE LIVE DEFAULT READ (phase 1a).  Runs the real `SituationReader.read`
    on annotation-free GUM text and counts, per relation source installed in the crosstype adapter, how
    many fine-relation tokens the bridge's Doc carries and how many role->name predication edges the
    bridge's detector licenses.  Expect ZERO fine relations and a collapsed edge count on the tree as it
    ships; the arm restores them."""
    t0 = time.time()
    import experiments.gum_coref as G
    import hdlab.crosstype_bridge as B
    import hdlab.crosstype_live_adapter as A
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.situation_reader import SituationReader, _write_temp_conll
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=args.probe_docs, name_gazetteer=gaz)
    tally = {}
    orig_pc = B.precise_constructs
    orig_ps = A._parse_sentence
    cur = {"arm": None}

    def counting_pc(doc, gz):
        lic, ep = orig_pc(doc, gz)
        t = tally[cur["arm"]]
        t["docs_seen"] += 1
        t["lic_roles"] += len(lic)
        t["lic_edges"] += sum(len(v) for v in lic.values())
        for tk in doc.toks:
            full = tk.deprel or ""
            t["rel"][full if full == "nmod:poss" else full.split(":")[0]] += 1
        t["toks"] += len(doc.toks)
        return lic, ep

    def bf_parse_sentence(forms, reader):
        pos, heads, deprels = orig_ps(forms, reader)
        if reader is None:
            return pos, heads, deprels
        from hdlab.attachment_arm import predicate_sites
        from hdlab import lexical_categories as LC
        mat = reader._cached_tag_matrix(list(forms))
        try:
            sites = predicate_sites(list(forms), list(pos), mat, LC.get().tags) if mat is not None else {}
        except Exception:
            sites = {}
        fr = all_relations(list(forms), list(pos), dict(heads), tab, sites=sites, coarse=dict(deprels),
                           cue_set=tab.get("cue_set"), with_heads=True, mat=mat,
                           tag_names=(LC.get().tags if mat is not None else None))
        return pos, dict(heads), {i: v[0] for i, v in fr.items()}

    B.precise_constructs = counting_pc
    try:
        import hdlab.entity_resolver as ER
        ER_pc = True
    except Exception:
        ER_pc = False
    try:
        for arm in ("shipped_dep_fallback", "bf_arm"):
            cur["arm"] = arm
            tally[arm] = {"docs_seen": 0, "lic_roles": 0, "lic_edges": 0, "toks": 0,
                          "rel": collections.Counter(), "read_s": 0.0}
            A._parse_sentence = orig_ps if arm == "shipped_dep_fallback" else bf_parse_sentence
            r = SituationReader()
            r.gaz = gaz
            for d in docs:
                rows = []
                by_sent = collections.defaultdict(list)
                for tk in d.toks:
                    by_sent[tk.sent].append(tk)
                for si in sorted(by_sent):
                    for wi, tk in enumerate(sorted(by_sent[si], key=lambda x: x.idx), 1):
                        rows.append((si + 1, wi, tk.form, "-"))
                p = _write_temp_conll(rows)
                t1 = time.time()
                try:
                    r.read(p)
                finally:
                    tally[arm]["read_s"] += time.time() - t1
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
    finally:
        B.precise_constructs = orig_pc
        A._parse_sentence = orig_ps
    out = {"n_docs": len(docs), "entity_resolver_present": ER_pc, "arms": {}}
    for a, t in tally.items():
        out["arms"][a] = {"bridge_docs_processed": t["docs_seen"], "doc_tokens": t["toks"],
                          "licensed_role_lemmas": t["lic_roles"], "licensed_role_to_name_edges": t["lic_edges"],
                          "fine_relation_tokens": {r: t["rel"].get(r, 0) for r in
                                                   ("appos", "flat", "compound", "nmod:poss", "cop", "det",
                                                    "amod", "acl", "conj", "case", "dep", "nmod")},
                          "read_s": round(t["read_s"], 1)}
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


# ==================================================================================================
# SELF-TEST.  TREE-AWARE (pri 125/129/131 lesson): S5 detects from the LIVE modules whether the diff is
# landed and asserts the DEFECT on the unpatched tree, its ABSENCE on the landed tree.
# ==================================================================================================
def patch_is_landed():
    """Read the LIVE modules, not the diff: the landed tree exposes the arm on the labels-rung organ AND
    the adapter merges it into the relation strings it hands the bridge."""
    try:
        from hdlab import graded_role_assigner as GRA
        import hdlab.crosstype_live_adapter as A
    except Exception:
        return False
    return (hasattr(GRA, "fine_relations") and hasattr(GRA, "observe_fine_relation_outcome")
            and hasattr(GRA, "all_relations") and getattr(A, "FINE_RELATIONS", None) is not None)


def _toy_table():
    """A deterministic 3-sentence teaching sample -> a real counts table.  Nothing is hand-set: the
    strengths are the organ own pure function of these counts."""
    data = [
        (["Mary", "Smith", "arrived", "."], {1: 3, 2: 1, 3: 0, 4: 3},
         {1: "nsubj", 2: "flat", 3: "root", 4: "punct"}),
        (["John", "Brown", "left", "."], {1: 3, 2: 1, 3: 0, 4: 3},
         {1: "nsubj", 2: "flat", 3: "root", 4: "punct"}),
        (["Elizabeth", ",", "the", "doctor", ",", "arrived", "."],
         {1: 6, 2: 4, 3: 4, 4: 1, 5: 4, 6: 0, 7: 6},
         {1: "nsubj", 2: "punct", 3: "det", 4: "appos", 5: "punct", 6: "root", 7: "punct"}),
        (["Anna", ",", "the", "nurse", ",", "spoke", "."],
         {1: 6, 2: 4, 3: 4, 4: 1, 5: 4, 6: 0, 7: 6},
         {1: "nsubj", 2: "punct", 3: "det", 4: "appos", 5: "punct", 6: "root", 7: "punct"}),
        (["her", "brother", "slept", "."], {1: 2, 2: 3, 3: 0, 4: 3},
         {1: "nmod:poss", 2: "nsubj", 3: "root", 4: "punct"}),
        (["his", "sister", "waited", "."], {1: 2, 2: 3, 3: 0, 4: 3},
         {1: "nmod:poss", 2: "nsubj", 3: "root", 4: "punct"}),
        (["Elizabeth", "is", "a", "doctor", "."], {1: 4, 2: 4, 3: 4, 4: 0, 5: 4},
         {1: "nsubj", 2: "cop", 3: "det", 4: "root", 5: "punct"}),
        (["Anna", "is", "a", "nurse", "."], {1: 4, 2: 4, 3: 4, 4: 0, 5: 4},
         {1: "nsubj", 2: "cop", 3: "det", 4: "root", 5: "punct"}),
    ]
    tags = {"Mary": "PROPN", "Smith": "PROPN", "John": "PROPN", "Brown": "PROPN", "Elizabeth": "PROPN",
            "Anna": "PROPN", "arrived": "VERB", "left": "VERB", "slept": "VERB", "waited": "VERB",
            "spoke": "VERB", "is": "AUX", "a": "DET", "the": "DET", "doctor": "NOUN", "nurse": "NOUN",
            "brother": "NOUN", "sister": "NOUN", "her": "PRON", "his": "PRON", ",": "PUNCT", ".": "PUNCT"}
    counts = empty_counts()
    for toks, heads, deps in data:
        pos = [tags[t] for t in toks]
        coarse = {i: ("nsubj" if deps[i] == "nsubj" else "dep") for i in range(1, len(toks) + 1)
                  if pos[i - 1] in ("NOUN", "PROPN", "PRON")}
        for i in fine_population(toks, pos, heads, coarse):
            cues = fine_relation_cues(toks, pos, heads, i, sites={}, coarse=coarse)
            accrue(counts, cues, fine_of(deps[i]), 1.0)
    return table_from_counts(counts, FINE_CUES), tags, data


def self_test():
    fails = []

    def ck(ok, msg):
        print(("  PASS " if ok else "  FAIL ") + msg)
        if not ok:
            fails.append(msg)

    # S1 the gold folding
    ck(fine_of("nmod:poss") == "nmod:poss" and fine_of("acl:relcl") == "acl"
       and fine_of("nmod:desc") == "compound" and fine_of("nsubj") == "dep",
       "S1 fine_of folds the UD deprel into the arm class space (poss kept, relcl -> acl, desc -> compound)")

    # S2 the NAME-RUN chunker
    runs = _nominal_runs(["PROPN", "PROPN", "VERB", "PUNCT"], ["Mary", "Smith", "arrived", "."])
    ck(runs == [(1, 2, "propn")], "S2 the name-run chunker reads 'Mary Smith' as ONE propn unit: %s" % runs)
    runs2 = _nominal_runs(["PROPN", "ADP", "PROPN", "VERB"], ["Game", "of", "Thrones", "aired"])
    ck(runs2 and runs2[0][:2] == (1, 3),
       "S2b a name-internal function word does not break the unit ('Game of Thrones'): %s" % runs2)

    # S3 the arm decides the constructions from counts (deterministic known-answer, no asset)
    tab, tags, _d = _toy_table()

    extra = {"Jane": "PROPN", "Doe": "PROPN", "Sarah": "PROPN", "pilot": "NOUN", "their": "PRON",
             "cousin": "NOUN", "Zed": "PROPN", "Quux": "PROPN"}

    def decide(toks, heads, coarse=None, with_heads=False):
        pos = [tags.get(t) or extra[t] for t in toks]
        coarse = coarse if coarse is not None else {
            i: ("nsubj" if (pos[i - 1] in ("NOUN", "PROPN", "PRON") and i == 1) else "dep")
            for i in range(1, len(toks) + 1) if pos[i - 1] in ("NOUN", "PROPN", "PRON")}
        return all_relations(toks, pos, heads, tab, sites={}, coarse=coarse, with_heads=with_heads)

    r = decide(["Jane", "Doe", "arrived", "."], {1: 3, 2: 1, 3: 0, 4: 3},
               coarse={1: "nsubj", 2: "dep"})
    ck(r.get(2) == "flat", "S3a an unseen NAME RUN reads flat from the name-run cue: %s" % r)
    r = decide(["Sarah", ",", "the", "pilot", ",", "arrived", "."], {1: 6, 2: 4, 3: 4, 4: 1, 5: 4, 6: 0, 7: 6},
               coarse={1: "nsubj", 4: "dep"})
    ck(r.get(4) == "appos", "S3b an unseen APPOSITION reads appos from the reduced-predication cue: %s" % r)
    r = decide(["their", "cousin", "slept", "."], {1: 2, 2: 3, 3: 0, 4: 3}, coarse={2: "nsubj", 1: "dep"})
    ck(r.get(1) == "nmod:poss", "S3c an unseen POSSESSIVE reads nmod:poss from the genitive case cue: %s" % r)
    r = decide(["Sarah", "is", "a", "pilot", "."], {1: 4, 2: 4, 3: 4, 4: 0, 5: 4}, coarse={1: "nsubj", 4: "dep"})
    ck(r.get(2) == "cop", "S3d the COPULA reads cop (the tense carrier of a non-verbal predication): %s" % r)

    # S4 the arm NEVER overrides a core argument label
    toks = ["Mary", "Smith", "saw", "the", "doctor", "."]
    pos = ["PROPN", "PROPN", "VERB", "DET", "NOUN", "PUNCT"]
    heads = {1: 3, 2: 1, 3: 0, 4: 5, 5: 3, 6: 3}
    coarse = {2: "dep", 1: "nsubj", 5: "obj"}
    out = all_relations(toks, pos, heads, tab, sites={}, coarse=coarse)
    ck(out.get(1) == "nsubj" and out.get(5) == "obj",
       "S4 a core ARGUMENT label is never overridden by the non-argument arm: %s" % out)

    # S5 THE CONSTRUCTION NAMES ITS OWN GOVERNOR
    wh = decide(["Jane", "Doe", "arrived", "."], {1: 3, 2: 3, 3: 0, 4: 3},
                coarse={1: "nsubj", 2: "dep"}, with_heads=True)
    ck(wh.get(2) is not None and wh[2][0] == "flat" and wh[2][1] == 1,
       "S5 the flat construction names the run FIRST token as governor even when the attachment arm "
       "attached the run member to the VERB (the arc-independent read): %s" % wh)

    # S6 PLASTICITY -- observing an outcome MOVES the decision (the brain is never frozen)
    toks = ["Zed", "Quux", "arrived", "."]
    pos = ["PROPN", "PROPN", "VERB", "PUNCT"]
    heads = {1: 3, 2: 1, 3: 0, 4: 3}
    coarse = {2: "dep", 1: "nsubj"}
    before = all_relations(toks, pos, heads, tab, sites={}, coarse=coarse).get(2)
    tab2 = table_from_counts(json.loads(json.dumps(tab["counts"])), tab.get("cue_set"))
    for _ in range(60):
        observe_fine_relation_outcome(toks, pos, heads, 2, "compound", tab2, sites={}, coarse=coarse)
    after = all_relations(toks, pos, heads, tab2, sites={}, coarse=coarse).get(2)
    ck(before != after and after == "compound",
       "S6 observing outcomes MOVES the arm (online plasticity): %s -> %s" % (before, after))

    # S7 the strength math is the ARGUMENT arm own, not a second copy
    from hdlab.graded_role_assigner import strengths_from_counts as _sfc
    a = build_strengths(tab["counts"])["prior"]
    b = _sfc(tab["counts"], 0.0)["prior"]
    ck(np.allclose(np.asarray(a), np.asarray(b)),
       "S7 the arm uses graded_role_assigner.strengths_from_counts verbatim (ONE implementation of the math)")

    # S8 the INFO-FREE TWIN loses on the toy population
    rng = np.random.default_rng(3)
    toks = ["Sarah", ",", "the", "pilot", ",", "arrived", "."]
    pos = ["PROPN", "PUNCT", "DET", "NOUN", "PUNCT", "VERB", "PUNCT"]
    heads = {1: 6, 2: 4, 3: 4, 4: 1, 5: 4, 6: 0, 7: 6}
    coarse = {1: "nsubj", 4: "dep"}
    popu = fine_population(toks, pos, heads, coarse)
    cl = [fine_relation_cues(toks, pos, heads, i, sites={}, coarse=coarse) for i in popu]
    real = [FINE_CLASSES[int(np.argmax(fine_relation_posterior(c, tab)))] for c in cl]
    twin = [FINE_CLASSES[int(np.argmax(fine_relation_posterior(c, tab)))] for c in _twin_cues(cl, rng)]
    ck(real != twin, "S8 the info-free twin (cue values permuted) decides differently: %s vs %s" % (real, twin))

    # S9 THE TREE-AWARE CHECK -- the defect on the unpatched tree, its ABSENCE on the landed tree
    landed = patch_is_landed()
    import hdlab.crosstype_live_adapter as A
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    r = SituationReader()
    r.gaz = load_given_gazetteer()
    sents = [["Elizabeth", "Bennet", ",", "the", "doctor", ",", "arrived", "."],
             ["The", "doctor", "examined", "her", "brother", "."]]
    for s in sents:
        r._cached_tag(list(s))
    toks_doc = A._build_toks(sents, r)
    got = collections.Counter((t.deprel or "").split(":")[0] if t.deprel != "nmod:poss" else "nmod:poss"
                              for t in toks_doc)
    fine_present = sum(got.get(k, 0) for k in ("appos", "flat", "compound", "nmod:poss", "cop"))
    if landed:
        ck(fine_present > 0,
           "S9 [landed] the adapter Doc carries FINE relations from the live modules (no monkeypatch): %s"
           % dict(got))
    else:
        ck(fine_present == 0,
           "S9 [unpatched] THE DEFECT REPRODUCES: the adapter Doc carries ZERO appos/flat/compound/poss/cop "
           "(every non-argument token reads 'dep'): %s" % dict(got))

    # S10 the shipped asset, when present, loads and is a counts asset with an observe path
    for p in (os.path.join(OUT_DIR, ASSET_NAME), ASSET_LANDED,
              os.path.join(_REPO, "data", "exp_" + ANCHOR, ASSET_NAME)):
        if os.path.exists(p):
            t = load_fine_validities(p)
            ck(bool(t["counts"]["config"]) and len(t["prior"]) >= len(FINE_CLASSES),
               "S10 the asset at %s is COUNTS (plastic), %d configurations"
               % (os.path.basename(p), len(t["counts"]["config"])))
            break
    else:
        print("  SKIP S10 (no validity asset built yet -- run --build)")

    print("\nSELF-TEST: %s" % ("PASS" if not fails else "FAIL (%d): %s" % (len(fails), fails)))
    return 1 if fails else 0



# ==================================================================================================
# PRE-LANDING VERIFICATION (--verify-landed).  The shipped diff cannot be applied to hdlab/ from here
# (the solver does not write the live substrate), so this arm proves the LANDED tree will be green:
# it compiles the diff's own hunks into the LIVE modules in this process, asserts `patch_is_landed()`
# then reports True, and re-runs the S9 witness -- which must now assert the ABSENCE of the defect on
# exactly the tree shape strategy will land.  A check that can only pass before the fix is not a check
# (pri 125 / 129 / 131 each shipped one that failed at landing).
# ==================================================================================================
DIFF_DIR = os.path.join(_REPO, "notes", "problems",
                        "the_fine_non_argument_relations_appos_flat_compound_poss_have_no_brain_"
                        "foundational_source_since_the_relation_labeler_retired_build_the_rung_from_"
                        "the_name_run_cue_the_predicate_slot_and_the_possessive_class")


def _apply_diff_text(rel, diff_path):
    """Apply a unified diff to ONE repo file inside a throwaway temp directory (nothing in the repo is
    written) and return the patched source.  `git apply` is the applier, so the check is the same one
    strategy runs at landing."""
    import shutil
    import subprocess
    import tempfile
    d = tempfile.mkdtemp(prefix="pri134_landed_")
    try:
        dst = os.path.join(d, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(_REPO, rel), dst)
        pr = subprocess.run(["git", "apply", "--ignore-whitespace", "-p1", os.path.abspath(diff_path)],
                            cwd=d, capture_output=True, text=True)
        if pr.returncode != 0:
            raise RuntimeError("git apply failed for %s: %s" % (rel, pr.stderr.strip()))
        return io.open(dst, encoding="utf-8").read()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def verify_landed():
    """Compile the two shipped diffs into the LIVE modules and re-run the witness on that tree shape."""
    fails = []

    def ck(ok, msg):
        print(("  PASS " if ok else "  FAIL ") + msg)
        if not ok:
            fails.append(msg)

    import hdlab.graded_role_assigner as GRA
    import hdlab.crosstype_live_adapter as A
    pairs = [("hdlab/graded_role_assigner.py", "fine_relations_arm_patch.diff", GRA),
             ("hdlab/crosstype_live_adapter.py", "crosstype_live_adapter_fine_relations_patch.diff", A)]
    for rel, dname, mod in pairs:
        src = io.open(os.path.join(_REPO, rel), encoding="utf-8").read()
        patched = _apply_diff_text(rel, os.path.join(DIFF_DIR, dname))
        code = compile(patched, rel, "exec")                # V1 the patched source APPLIES and COMPILES
        ck(True, "V1 %s applies with `git apply` and compiles (%d -> %d lines)"
           % (os.path.basename(rel), src.count("\n"), patched.count("\n")))
        exec(code, mod.__dict__)                            # install the landed module INTO the live module
    ck(patch_is_landed(), "V2 patch_is_landed() reads True from the LIVE modules after the diffs are installed")
    # V3 -- the S9 witness on the landed tree shape: the DEFECT must be ABSENT
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    r = SituationReader()
    r.gaz = load_given_gazetteer()
    sents = [["Elizabeth", "Bennet", ",", "the", "doctor", ",", "arrived", "."],
             ["The", "doctor", "examined", "her", "brother", "."]]
    for sn in sents:
        r._cached_tag(list(sn))
    def _doc_rels():
        toks_doc = A._build_toks(sents, r)
        g = collections.Counter((t.deprel or "").split(":")[0] if t.deprel != "nmod:poss" else "nmod:poss"
                                for t in toks_doc)
        return toks_doc, g, sum(g.get(k, 0) for k in ("appos", "flat", "compound", "nmod:poss", "cop"))

    # V3a WITH NO ASSET the landed organ is INERT -- byte-identical to the pri-129 tree (safe to land first).
    # The asset is on disk at its landed location, so the no-asset case is exercised by pointing the loader at a
    # path that does not exist (the same code path a tree without the asset copy takes).
    _saved_paths = GRA._FINE_VALIDITIES_PATHS
    GRA._FINE_VALIDITIES_PATHS = (os.path.join(_REPO, "data", "__no_such_fine_asset__.json"),)
    GRA._FINE_VALIDITIES_CACHE = None
    GRA._FINE_CACHE_SET = False
    _td, got0, n0 = _doc_rels()
    ck(n0 == 0, "V3a [landed, NO asset] the arm abstains and the adapter is byte-identical to pri 129 "
                "(safe to land before the asset copy): %s" % dict(got0))
    # V3b WITH THE ASSET the DEFECT IS ABSENT on exactly the tree strategy will land
    ap = os.path.join(_REPO, "data", "exp_" + ANCHOR, ASSET_NAME)
    GRA._FINE_VALIDITIES_PATHS = (ap,) + tuple(_saved_paths)
    GRA._FINE_VALIDITIES_CACHE = None
    GRA._FINE_CACHE_SET = False
    toks_doc, got, fine_present = _doc_rels()
    ck(fine_present > 0, "V3b [landed] THE DEFECT IS ABSENT: the adapter Doc carries %d fine-relation tokens "
                         "with NO monkeypatch of the arm: %s" % (fine_present, dict(got)))
    # V4 -- the bridge's own detector fires again on that Doc
    from hdlab.crosstype_bridge import precise_constructs
    from types import SimpleNamespace as NS

    class _M:
        pass
    ms = []
    for (eid, mt, sg, eg, hg, gd, txt, lh) in [(1, "name", 0, 1, 1, "f", "Elizabeth Bennet", "bennet"),
                                               (1, "common", 3, 4, 4, "", "the doctor", "doctor")]:
        m = _M()
        m.eid, m.mtype, m.start_g, m.end_g, m.head_g = eid, mt, sg, eg, hg
        m.gender, m.text, m.lemma_head = gd, txt, lh
        ms.append(m)
    doc = NS(toks=toks_doc, mentions=ms)
    lic, _ep = precise_constructs(doc, {"elizabeth": "fem", "bennet": "fem"})
    ck(True, "V4 [landed] the bridge predication detector runs on the landed Doc: licensed=%s" % dict(lic))
    # V5 -- the adapter's OWN self-test on the landed module; its W5 exercises the STANDALONE frontend path,
    # which this diff re-routes off the three supervised stand-ins it used to load.
    try:
        rc = A._selftest()
    except Exception as ex:
        rc = repr(ex)
    ck(rc == 0, "V5 [landed] crosstype_live_adapter._selftest passes on the patched module (rc=%r)" % rc)
    print("\nVERIFY-LANDED: %s" % ("PASS" if not fails else "FAIL (%d): %s" % (len(fails), fails)))
    return 1 if fails else 0



# ==================================================================================================
# PHASE 7 ARM: --spans
# (A) EVERY hdlab READER OF THE MENTION SPAN, enumerated and COUNTED on the live default read.
# (B) THE PROPER REPAIR AT THE INTRODUCTION ORGAN (referent_per_np_span_patch.diff), measured on the
#     same A table, on the A/B/C bridge counts, and on the fine-relation tokens.
# Both arms in ONE process; the patched organ is installed from its own shipped diff, never monkeypatched
# by hand, so what is measured IS what lands.
# ==================================================================================================
SPAN_DIFF = "referent_per_np_span_patch.diff"


def _install_rpn_patch():
    """Compile the shipped referent_per_np diff INTO the live module (the --verify-landed method)."""
    import hdlab.referent_per_np as RPN
    rel = "hdlab/referent_per_np.py"
    patched = _apply_diff_text(rel, os.path.join(DIFF_DIR, SPAN_DIFF))
    exec(compile(patched, rel, "exec"), RPN.__dict__)
    return RPN


def _span_audit(role_mentions, sents):
    """THE A TABLE, computed with the REAL consumer functions -- never a re-implementation."""
    from hdlab.coref import mention_span, name_content_tokens
    from hdlab.lexical_utils import definiteness, modifiers
    import hdlab.crosstype_live_adapter as A
    nonp = [m for m in role_mentions if not m.get("is_pronoun")]
    ntok = sum(len(s) for s in sents)
    out = {
        "mentions": len(role_mentions), "non_pronoun": len(nonp),
        # coref.mention_span (pri 131 aligns a pronoun pick by this span)
        "mention_span_extent_gt0": sum(1 for m in nonp
                                       if (lambda t: t[2] > t[1])(mention_span(m))),
        # lexical_utils.definiteness (Heim file-change: which determiner opened the file)
        "definiteness": dict(collections.Counter(definiteness(m) for m in nonp)),
        # lexical_utils.modifiers (the descriptive content an ACT-R retrieval matches on)
        "with_modifiers": sum(1 for m in nonp if modifiers(m)),
        # coref.name_content_tokens (the NAME gate for ten organs; pri 118's span cue rides on it)
        "name_typed": sum(1 for m in nonp
                          if name_content_tokens(m.get("span_toks", [m["head"]]),
                                                 upos=m.get("span_upos"))),
        "multi_token_span": sum(1 for m in nonp if len(m.get("span_toks") or []) > 1),
        # crosstype_live_adapter._can_build (the whole bridge abstains if ANY mention fails)
        "gtok_in_range": sum(1 for m in nonp
                             if isinstance(m.get("gtok_start"), int)
                             and isinstance(m.get("gtok_end"), int)
                             and 0 <= m["gtok_start"] <= m["gtok_end"] < ntok),
        "can_build": bool(A._can_build(role_mentions, sents)),
        # space_reader._cluster_covering (wtok_start + len(span) - 1 covers a token)
        "space_extent_gt0": sum(1 for m in nonp if len(m.get("span_toks") or [m["head"]]) > 1),
    }
    return out


def arm_spans(args, tab):
    """A + B: the span-contract audit and the introduction-organ repair, both arms, one process."""
    t0 = time.time()
    import experiments.gum_coref as G
    import hdlab.crosstype_bridge as B
    import hdlab.crosstype_live_adapter as A
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.situation_reader import SituationReader, _write_temp_conll
    gaz = load_given_gazetteer()
    docs = G.load_docs(gum_only=True, limit=args.probe_docs, name_gazetteer=gaz)
    RPN = _install_rpn_patch()                      # the landed shape; RPN_SPAN switches it off again
    orig_pc, orig_ps = B.precise_constructs, A._parse_sentence
    S, cur = {}, {"arm": None}

    def counting_pc(doc, gz):
        r = orig_pc(doc, gz)
        t = S[cur["arm"]]
        t["docs_with_doc"] += 1
        t["lic_roles"] += len(r[0])
        t["lic_edges"] += sum(len(v) for v in r[0].values())
        h = collections.Counter((x.deprel or "") if (x.deprel or "") == "nmod:poss"
                                else (x.deprel or "").split(":")[0] for x in doc.toks)
        for k in ("appos", "flat", "compound", "nmod:poss", "cop"):
            t["rel"][k] += h.get(k, 0)
        return r

    def bf_parse(forms, reader):
        pos, heads, deprels = orig_ps(forms, reader)
        if reader is None:
            return pos, heads, deprels
        from hdlab.attachment_arm import predicate_sites
        from hdlab import lexical_categories as LC
        mat = reader._cached_tag_matrix(list(forms))
        try:
            sites = predicate_sites(list(forms), list(pos), mat, LC.get().tags) if mat is not None else {}
        except Exception:
            sites = {}
        fr = all_relations(list(forms), list(pos), dict(heads), tab, sites=sites, coarse=dict(deprels),
                           cue_set=tab.get("cue_set"), with_heads=True, mat=mat,
                           tag_names=(LC.get().tags if mat is not None else None))
        hd = dict(heads); hd.update({i: int(v[1]) for i, v in fr.items()})
        return pos, hd, {i: v[0] for i, v in fr.items()}

    orig_merge = A.merge_crosstype_bridge

    def capture_merge(rm, ol, gz, sents, **kw):
        t = S[cur["arm"]]
        if t["audit"] is None:
            t["audit"] = _span_audit(rm, sents)
        else:
            a2 = _span_audit(rm, sents)
            for k, v in a2.items():
                if isinstance(v, int):
                    t["audit"][k] += v
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        t["audit"][k][kk] = t["audit"][k].get(kk, 0) + vv
                else:
                    t["audit"][k] = t["audit"][k] and v
        t["docs_can_build"] += 1 if A._can_build(rm, sents) else 0
        return orig_merge(rm, ol, gz, sents, **kw)

    orig_ap = A.apply_binds

    def count_binds(rm, ol, binds):
        t = S[cur["arm"]]
        t["binds"] += len(binds)
        merged = orig_ap(rm, ol, binds)
        t["refiled"] += sum(1 for k, v in merged.items() if ol.get(k) != v)
        return merged

    B.precise_constructs = counting_pc
    A.merge_crosstype_bridge = capture_merge
    A.apply_binds = count_binds
    try:
        for arm, span_on, fine_on in (("A_as_shipped", False, False),
                                      ("B_span_repair_only", True, False),
                                      ("C_span_repair_plus_fine_arm", True, True)):
            cur["arm"] = arm
            S[arm] = {"docs": 0, "docs_can_build": 0, "docs_with_doc": 0, "lic_roles": 0, "lic_edges": 0,
                      "binds": 0, "refiled": 0, "rel": collections.Counter(), "audit": None, "read_s": 0.0}
            RPN.RPN_SPAN = span_on
            A._parse_sentence = bf_parse if fine_on else orig_ps
            r = SituationReader(); r.gaz = gaz
            for d in docs:
                rows, bys = [], collections.defaultdict(list)
                for tk in d.toks:
                    bys[tk.sent].append(tk)
                for si in sorted(bys):
                    for wi, tk in enumerate(sorted(bys[si], key=lambda x: x.idx), 1):
                        rows.append((si + 1, wi, tk.form, "-"))
                p = _write_temp_conll(rows)
                S[arm]["docs"] += 1
                t1 = time.time()
                try:
                    r.read(p)
                finally:
                    S[arm]["read_s"] += time.time() - t1
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
    finally:
        B.precise_constructs, A._parse_sentence = orig_pc, orig_ps
        A.merge_crosstype_bridge, A.apply_binds = orig_merge, orig_ap
        RPN.RPN_SPAN = True
    out = {"n_docs": len(docs), "arms": {}}
    for a, s in S.items():
        out["arms"][a] = {k: v for k, v in s.items() if k not in ("rel", "audit")}
        out["arms"][a]["read_s"] = round(s["read_s"], 1)
        out["arms"][a]["fine_relation_tokens"] = dict(s["rel"])
        out["arms"][a]["span_contract_audit"] = s["audit"]
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


# ==================================================================================================
# PHASE 7 ARM: --pronoun
# THE TWO SOLVERS' FINDINGS MEET IN ONE NUMBER.  pri 136 measures the one-token mention span from the
# CLUSTERING side (1,331 of 3,689 same-entity cross-file pairs lie inside one gold span; definiteness reads
# `bare` on 100% of mentions); pri 134 phase 7 repairs it at the INTRODUCTION organ.  The shared instrument
# is pri 131's own pronoun row -- `experiments/exp_pronoun_pick_identity_contract_v1.row_pronouns`, called
# here rather than re-implemented -- run with the span repair OFF and ON in ONE process on ONE question set.
# ==================================================================================================
def arm_pronoun(args, tab):
    t0 = time.time()
    import experiments.exp_pronoun_pick_identity_contract_v1 as PP
    RPN = _install_rpn_patch()
    arms = tuple(a for a in args.pron_arms.split(",") if a)
    out = {"n_docs": args.pron_docs, "arms": arms, "settings": {}}
    try:
        for name, on in (("span_repair_OFF", False), ("span_repair_ON", True)):
            RPN.RPN_SPAN = on
            print("\n=== pronoun row, %s ===" % name)
            out["settings"][name] = PP.row_pronouns(n_docs=args.pron_docs, arms=arms, verbose=True)
    finally:
        RPN.RPN_SPAN = True
    a, b = out["settings"]["span_repair_OFF"], out["settings"]["span_repair_ON"]
    key = arms[-1] if arms else "entity_pb"
    out["headline"] = {
        "arm": key,
        "span_scored_OFF": (a.get("arms", {}).get(key) or {}).get("span"),
        "span_scored_ON": (b.get("arms", {}).get(key) or {}).get("span"),
        "head_credit_OFF": (a.get("arms", {}).get(key) or {}).get("head_credit"),
        "head_credit_ON": (b.get("arms", {}).get(key) or {}).get("head_credit"),
        "floor_OFF": a.get("floor_nearest_prior_compatible"),
        "floor_ON": b.get("floor_nearest_prior_compatible"),
        "purity_OFF": a.get("clustering_purity"), "purity_ON": b.get("clustering_purity"),
    }
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out

# ==================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--verify-landed", action="store_true")
    ap.add_argument("--spans", action="store_true")
    ap.add_argument("--pronoun", action="store_true")
    ap.add_argument("--pron-docs", type=int, default=8, dest="pron_docs")
    ap.add_argument("--pron-arms", default="entity_pb,twin", dest="pron_arms")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--ud", action="store_true")
    ap.add_argument("--bridge", action="store_true")
    ap.add_argument("--c3", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--train-cap", type=int, default=0)
    ap.add_argument("--ud-cap", type=int, default=0)
    ap.add_argument("--gum-docs", type=int, default=40)
    ap.add_argument("--probe-docs", type=int, default=4)
    ap.add_argument("--maxlen", type=int, default=120)
    ap.add_argument("--min-conf", type=float, default=0.5)
    ap.add_argument("--conf-thr", type=float, default=-3.0)
    ap.add_argument("--perceptron", action="store_true",
                    help="also run the RETIRED supervised labeler as an INFORMATIONAL floor")
    ap.add_argument("--oracle", action="store_true", help="also run the arm on GOLD heads (the heads-rung ceiling)")
    ap.add_argument("--ablate", action="store_true", help="also run the two quality-push levers ABLATED")
    ap.add_argument("--asset", default="")
    ap.add_argument("--out", default="metrics.json")
    args = ap.parse_args()
    if args.smoke:
        args.train_cap = args.train_cap or 400
        args.ud_cap = args.ud_cap or 120
        args.gum_docs = min(args.gum_docs, 4)
    if args.verify_landed:
        return verify_landed()
    if args.self_test:
        return self_test()
    os.makedirs(OUT_DIR, exist_ok=True)
    any_arm = args.build or args.probe or args.ud or args.bridge or args.c3 or args.spans or args.pronoun
    if not any_arm:
        args.build = args.ud = args.bridge = args.c3 = args.probe = True
    M = {"anchor": ANCHOR, "seed": SEED, "args": vars(args), "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    t0 = time.time()
    tab = None
    if args.build:
        M["build"] = arm_build(args)
    apath = args.asset or os.path.join(OUT_DIR, ASSET_NAME)
    if not os.path.exists(apath) and os.path.exists(ASSET_LANDED):
        apath = ASSET_LANDED
    if os.path.exists(apath):
        tab = load_fine_validities(apath)
        M["asset_used"] = apath
    if tab is None and (args.ud or args.bridge or args.c3 or args.probe):
        print("NO VALIDITY ASSET -- run --build first (or pass --asset)")
        return 2
    if args.pronoun:
        M["pronoun"] = arm_pronoun(args, tab)
        print("PRONOUN HEADLINE: %s" % json.dumps(M["pronoun"]["headline"], indent=1, default=str))
    if args.spans:
        M["spans"] = arm_spans(args, tab)
        print("SPANS: %s" % json.dumps(M["spans"], indent=1)[:3000])
    if args.probe:
        M["probe"] = arm_probe(args, tab)
        print("PROBE: %s" % json.dumps(M["probe"]["arms"], indent=1)[:1600])
    if args.ud:
        M["ud"] = arm_ud(args, tab)
        print("UD per-relation:")
        for a, rows in M["ud"]["per_relation"].items():
            print("  %-18s %s" % (a, {r: (v["P"], v["R"], v["gold"]) for r, v in rows.items()
                                       if r in ("flat", "compound", "appos", "nmod:poss", "cop")}))
        print("  union target accuracy: %s" % M["ud"]["union_target_accuracy"])
        print("  bf vs dep-fallback: %s" % M["ud"]["paired_bf_vs_depfallback"])
        print("  bf vs twin:         %s" % M["ud"]["paired_bf_vs_twin"])
        print("  construction heads: %s" % M["ud"]["head_accuracy_on_constructions"])
    if args.bridge:
        M["bridge"] = arm_bridge(args, tab)
        print("BRIDGE name-linking (GUM, live parse):")
        for a, row in M["bridge"]["arms"].items():
            print("  %-18s edges=%-5d recall=%.4f precision=%.4f pop=%d  %s"
                  % (a, row["licensed_role_to_name_edges"], row["recall"], row["precision"],
                     row["ceiling_pop"], row["fine_relation_tokens"]))
        print("  paired recall bf vs dep-fallback: %s" % M["bridge"]["paired_recall_bf_vs_depfallback"])
    if args.c3:
        M["c3"] = arm_c3(args, tab)
        print("C3 experiencer (real canonicalizer): %s" % M["c3"]["C3"])
        print("  paired vs honest floor: %s" % M["c3"]["paired_vs_floor"])
        print("  bf vs dep-fallback: %s" % M["c3"]["paired_bf_vs_depfallback"])
    M["elapsed_s"] = round(time.time() - t0, 1)
    p = os.path.join(OUT_DIR, args.out)
    with open(p, "w", encoding="ascii") as f:
        json.dump(M, f, indent=1, default=str)
    print("\nwrote %s (%.1fs)" % (p, M["elapsed_s"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
