#!/usr/bin/env python3
"""exp_passive_cue_clause_local_v1 -- THE VOICE CUE IS A PROPERTY OF ONE PREDICATE, PERCEIVED IN ORDER.

PROBLEM (pri 111). `hdlab.thematic_role_labeler.is_passive_clause(tokens, pos)` scans the WHOLE token
sequence for ANY be-aux followed within 3 tokens by a past participle and returns ONE boolean for the
sentence. A passive relative clause, a passive coordinate clause or an adjectival participle therefore
declares EVERY predicate in the sentence passive. Measured consequence (pri 106, p7_override_anatomy.json):
of the 43 agent decisions where that cue alone licenses the marked-cue override, 33 are gold-ACTIVE
clauses; the licence fixes 1 and breaks 30 (conflict validity 0.032).

HOW THE BRAIN DOES THIS (the opening move).
  STRUCTURE: MacWhinney & Bates' Competition Model. A cue is evaluated FOR THE PREDICATE whose arguments
  are being assigned, and it enters at its VALIDITY (availability x reliability). English voice is not a
  sentence-level feature: it is the form side of a stored CONSTRUCTION -- [NP be/get V-en (by NP)]
  (Goldberg 1995) -- realised on ONE predicate by ONE auxiliary chain.
  ORDER: comprehension is incremental (Marslen-Wilson 1973; Altmann & Kamide 1999). The auxiliary is heard
  FIRST and sets up the expectation; the very next non-adverbial word either confirms it (a participial main
  verb) or cancels it (a determiner -> the aux was a copula; an infinitival `to` -> a new predicate opens).
  So the cue is an UNBROKEN LEFT CHAIN from the predicate, not a window-3 search.
  CLAUSE: the clause is the unit of argument assignment (Fodor & Bever 1965 click-displacement; Frazier &
  Fodor 1978 two-stage packaging). A cue perceived in one clause cannot license a decision in another.
  GRADED: the cue does not have to be a boolean. Additive cue activation -> logistic IS the Bayesian
  posterior for cue integration (McClelland 2013), so P(passive | cue values) read off COUNTS is the
  brain-foundational form, with an online observe path (never frozen).

WHAT IS BUILT HERE (the candidate organ, transplanted into hdlab by passive_cue_patch.diff):
  voice_cue_value(tokens, pos, v, heads)  -> the cue VALUE at predicate v (be_arc / be_chain / get_chain /
                                             be_inv / conj / prog / none / na)
  voice_posterior(...)                    -> P(passive | value, morphology, by-PP, degree-modifier) from
                                             COUNTS accrued on UD-EWT train; observe_voice_outcome() accrues
  is_passive_predicate(...)               -> the boolean the four call sites need, at a swept criterion

FLOORS / CONTROLS. Floor = the shipped whole-sentence detector, measured on the same population in the same
run. Second floor = the shipped detector scoped to the clause (`is_passive_clause(toks[lo:hi], pos[lo:hi])`,
what `agent_override_fires` does today). Third = `relcl_resolver.precise_passive` (already predicate-anchored).
TWIN = a random equal-size set of predicates declared passive (information-free, same firing rate).
Paired bootstrap over SENTENCES (detector) and over ITEMS (the agent consumer), 2000 resamples.

NO spaCy / NO nltk / NO external parser / NO LLM anywhere. UD-EWT is the MEASURING instrument only.
Run:  .venv/Scripts/python.exe experiments/exp_passive_cue_clause_local_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_passive_cue_clause_local_v1.py --run
"""
from __future__ import annotations

import argparse
import io
import collections
import json
import os
import random
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._seed_checkpoint import get_output_dir   # Q115

ANCHOR = "exp_passive_cue_clause_local_v1"
OUT_DIR = str(get_output_dir(ANCHOR))
UD_DIR = os.path.join(REPO, "data", "corpora", "ud_english_ewt")
UD_TRAIN = os.path.join(UD_DIR, "en_ewt-ud-train.conllu")
UD_TEST = os.path.join(UD_DIR, "en_ewt-ud-test.conllu")
SEED = 20260914

# =================================================================================================
# 1. THE ORGAN CANDIDATE -- the predicate-anchored, clause-local, GRADED voice cue.
#    Everything below reads ONLY tokens / categories (+ the reader's own heads, optionally). Glass-box.
# =================================================================================================
# ---8<--- ORGAN BLOCK BEGIN (transplanted VERBATIM into hdlab/thematic_role_labeler.py by --emit-patch;
#          the self-test asserts the diff's added lines are byte-identical to this block) ---8<---
# THE VOICE CUE IS A PROPERTY OF ONE PREDICATE (2026-09-14, pri 111). `is_passive_clause` below scans the
# WHOLE token sequence for any be-aux followed within 3 tokens by a past participle and returns ONE boolean
# for the sentence, so a passive relative clause / coordinate clause / adjectival participle declares EVERY
# predicate passive. Measured on UD-EWT test per predicate (live category organ + attachment arm): the
# whole-sentence read scores precision 0.3784 at recall 0.8235; this predicate-anchored read scores
# precision 0.9606 at recall 0.8971 on the same 2605 predicates (200 fixes, 11 breaks, head to head).
#
# THE BRAIN'S COMPUTATION, and why the evidence runs the other way round. Voice is a cue of the Competition
# Model (Bates & MacWhinney 1989) and it is evaluated FOR THE PREDICATE whose arguments are being assigned,
# inside that predicate's clause (the clause is the perceptual unit of sentence processing -- Fodor & Bever
# 1965; Frazier & Fodor 1978). The participial SUFFIX is not the evidence: `-ed` is systematically ambiguous
# between the simple past and the participle, which is exactly why "the horse raced past the barn fell" is a
# garden path (Bever 1970; Trueswell, Tanenhaus & Garnsey 1994). What carries the cue is the AUXILIARY, heard
# FIRST, which opens the passive expectation for the predicate it attaches to (incremental interpretation --
# Marslen-Wilson 1973; anticipatory use of the verb/aux -- Altmann & Kamide 1999; early use of voice
# morphology as an actor/undergoer cue -- Bornkessel-Schlesewsky & Schlesewsky 2006/2009 eADM). The very next
# non-adverbial word then CONFIRMS it (a participial main verb) or CANCELS it (a determiner -> the aux was a
# copula; an infinitival `to` -> a new predicate opens; `-ing` -> the construction is progressive, i.e.
# ACTIVE). So the operation is an UNBROKEN LEFT CHAIN from the predicate, not a window search over the
# sentence -- and the by-phrase, when it comes, is confirmation of the demoted agent, not a requirement.
# =================================================================================================
# The auxiliary that carries English voice. Finite and non-finite are kept apart because only a FINITE
# be can appear to the RIGHT of a fronted participle ("Attached IS a spreadsheet"); "be"/"been"/"being"
# cannot invert.
_BE_FINITE = frozenset({"is", "are", "was", "were", "am", "'s", "'re", "'m", "ai"})
_BE_NONFINITE = frozenset({"be", "been", "being"})
_BE_FORMS = _BE_FINITE | _BE_NONFINITE
_GET_FORMS = frozenset({"get", "gets", "got", "gotten", "getting"})
_AUX_POS = ("AUX", "VERB")                     # the category organ tags contracted/odd auxiliaries either way
# What the auxiliary chain may cross without breaking: adverbs, negation, stacked auxiliaries, a hyphen or a
# quote. NOT a determiner, NOT a nominal, NOT a preposition -- each of those cancels the passive expectation.
_CHAIN_POS = frozenset({"ADV", "PART", "AUX"})
_CHAIN_PUNCT = frozenset({"-", "--", '"', "'", "``", "''", chr(0x201C), chr(0x201D)})   # ASCII source
# `to` (and its spoken form `ta`) opens a NEW predicate: "will be around to assist" is not "be assist".
_CHAIN_STOP_WORDS = frozenset({"to", "ta"})
_COORD_WORDS = frozenset({"and", "or", "nor"})
# ADJECTIVAL-PASSIVE evidence (Wasow 1977): a degree modifier selects the STATIVE adjectival participle
# ("was VERY tired"), which demotes no agent and must not license an override.
_DEGREE_MOD = frozenset({"very", "quite", "so", "too", "rather", "extremely", "fairly", "somewhat",
                        "pretty", "really", "most", "more", "less", "least", "highly", "deeply"})
# REDUCED SEMI-MODAL HOSTS: "gon na" / "got ta" / "wan na" are the spoken reductions of going-to / got-to /
# want-to. The host ("gon") is not an -ing form, so the -ing test alone lets `is gon na start` through as a
# passive; the giveaway is the token AFTER it -- `na`/`ta` occur in English ONLY as the reduced infinitival
# marker of these forms, and no passive participle is ever followed by one. Found on GENTLE (the OOD split),
# where 19 of 21 remaining false fires were "gon na".
_REDUCED_INFINITIVE = frozenset({"na", "ta"})
VOICE_VALUES = ("be_arc", "be_chain", "get_arc", "get_chain", "be_inv", "conj", "prog", "semimodal",
                "none", "na")
PASSIVE_VALUES = ("be_arc", "be_chain", "get_arc", "get_chain", "be_inv", "conj")
VOICE_THETA = 0.5


def _low(toks):
    return [t.lower() for t in toks]


def _is_ing(word):
    return word.lower().endswith("ing")


def _aux_chain_left(toks, pos, v):
    """Walk LEFT from the predicate at v (1-based) across adverbs / negation / stacked auxiliaries / a hyphen
    or quote, and return (kind, index) of the first BE/GET auxiliary reached, else None. Anything else --
    a determiner, a nominal, a preposition, an infinitival `to` -- CANCELS the expectation and stops the walk.
    This is the incremental form of 'the auxiliary chain attached to THIS predicate'."""
    low = _low(toks)
    j = v - 1
    while j >= 1:
        w = low[j - 1]
        p = pos[j - 1] if j - 1 < len(pos) else None
        if p in _AUX_POS and w in _BE_FORMS:
            return ("be", j)
        if p in _AUX_POS and w in _GET_FORMS:
            return ("get", j)
        if w in _CHAIN_STOP_WORDS:
            return None
        if p in _CHAIN_POS or w in ("not", "n't") or (p == "PUNCT" and w in _CHAIN_PUNCT):
            j -= 1
            continue
        return None
    return None


def _clause_span(toks, pos, v):
    """[lo, hi) 0-based clause span of the predicate at v (1-based). Reuses the organ's own segmentation."""
    from hdlab.graded_role_assigner import clause_bounds
    return clause_bounds(list(toks), list(pos), v - 1)


def _inverted_aux(toks, pos, v):
    """Fronted participle with a POSTPOSED finite auxiliary: 'Attached is a spreadsheet'. Licensed only when
    the predicate is the clause-initial token, the finite be follows across adverbs only, and a nominal
    follows it (the postposed subject). Without all three this is the 'happens to be' false-fire."""
    low = _low(toks)
    n = len(toks)
    lo, hi = _clause_span(toks, pos, v)
    if v - 1 != lo:
        return False
    j, steps = v + 1, 0
    while j <= n and steps < 3:
        w = low[j - 1]
        p = pos[j - 1] if j - 1 < len(pos) else None
        if p in _AUX_POS and w in _BE_FINITE:
            return any((pos[k] if k < len(pos) else None) in ("NOUN", "PROPN", "PRON")
                       for k in range(j, min(n, hi)))
        if p in _CHAIN_POS:
            j += 1
            steps += 1
            continue
        return False
    return False


def _bare_aux_value(toks, pos, v, heads=None):
    """The auxiliary cue value at v WITHOUT the coordination cue (used as the base of the coordination read)."""
    c = _aux_chain_left(toks, pos, v)
    if c is not None:
        kind, j = c
        if heads and heads.get(j) == v:       # the reader's own arc CONFIRMS the auxiliary belongs to v
            return kind + "_arc"
        return kind + "_chain"
    if _inverted_aux(toks, pos, v):
        return "be_inv"
    return "none"


def _conj_of_passive(toks, pos, v, heads=None):
    """Across-the-board auxiliary sharing: 'the artworks were selected and EXHIBITED'. The second conjunct
    carries no auxiliary of its own; the coordinator is the cue that it inherits the first conjunct's voice.
    Read from the SURFACE coordinator, not from an arc -- an arc says 'v depends on h', never 'this is
    coordination', and a head-based read wrongly inherits voice across xcomp/ccomp/advcl (measured: gold
    heads 34 false fires against 12 for the surface read)."""
    low = _low(toks)
    j = v - 1
    while j >= 1:
        w = low[j - 1]
        p = pos[j - 1] if j - 1 < len(pos) else None
        if w in _COORD_WORDS or (p == "PUNCT" and w == ","):
            k = j - 1
            while k >= 1:
                pk = pos[k - 1] if k - 1 < len(pos) else None
                if pk == "VERB":
                    return (not _is_ing(toks[k - 1])) and _bare_aux_value(toks, pos, k, heads) != "none"
                if pk in ("NOUN", "PROPN", "PRON", "ADP", "SCONJ"):
                    return False
                k -= 1
            return False
        if p in _CHAIN_POS or w in ("not", "n't") or (p == "PUNCT" and w in _CHAIN_PUNCT):
            j -= 1
            continue
        return False
    return False


def voice_cue_value(toks, pos, v, heads=None, use_conj=True):
    """THE CUE VALUE for the predicate at v (1-based). One of VOICE_VALUES.
      na        -- v is not a predicate the cue applies to
      prog      -- [be V-ing]: the auxiliary is there but the construction is PROGRESSIVE, i.e. ACTIVE
      be_arc    -- a BE auxiliary the reader's own parse attached to v, reached by an unbroken chain
      be_chain  -- a BE auxiliary reached by an unbroken chain (no arc, or the arc says otherwise)
      get_arc / get_chain -- the GET-passive ('got yelled at')
      be_inv    -- fronted participle with a postposed finite be ('Attached is a spreadsheet')
      conj      -- a bare conjunct sharing the first conjunct's auxiliary
      none      -- no voice evidence at this predicate
    """
    if v < 1 or v - 1 >= len(pos) or pos[v - 1] != "VERB":
        return "na"
    if _is_ing(toks[v - 1]):
        return "prog"
    if v < len(toks) and toks[v].lower() in _REDUCED_INFINITIVE:
        return "semimodal"                      # `is gon na V` / `got ta V`: a future/modal periphrasis
    a = _bare_aux_value(toks, pos, v, heads)
    if a != "none":
        return a
    if use_conj and _conj_of_passive(toks, pos, v, heads):
        return "conj"
    return "none"


def morph_value(toks, v):
    """The predicate's own participial morphology as the reader perceives it. `ed` is the -ed GARDEN PATH
    (past OR participle); `en` is the unambiguous strong participle; `other` is a bare/irregular form which
    the auxiliary construction alone has to carry."""
    w = toks[v - 1].lower().strip(".,\"'();:")
    if w.endswith("ing"):
        return "ing"
    if w.endswith("ed") and len(w) > 3:
        return "ed"
    if w.endswith("en") and len(w) > 3:
        return "en"
    return "other"


def by_value(toks, pos, v, heads=None):
    """Is the demoted agent's by-phrase present for THIS predicate -- inside its clause, after it, with a
    nominal governed by `by`? The morphological confirmation of the passive construction."""
    low = _low(toks)
    lo, hi = _clause_span(toks, pos, v)
    for j in range(v, min(hi, len(low))):
        if low[j] != "by":
            continue
        for k in range(j + 1, min(hi, len(low))):
            p = pos[k] if k < len(pos) else None
            if p in ("NOUN", "PROPN", "PRON"):
                if heads and heads.get(k + 1) not in (None, 0) and heads.get(j + 1) not in (None, 0):
                    pass                                  # arcs are read as confirmation only, never as a gate
                return "by"
            if p in ("DET", "ADJ", "NUM", "PUNCT"):
                continue
            break
    return "none"


def degree_value(toks, pos, v):
    """Adjectival-passive evidence (Wasow 1977): a degree modifier immediately before the participle selects
    the STATIVE adjectival reading ('was VERY tired'), which demotes no agent."""
    low = _low(toks)
    j = v - 1
    steps = 0
    while j >= 1 and steps < 3:
        w = low[j - 1]
        if w in _DEGREE_MOD:
            return "deg"
        p = pos[j - 1] if j - 1 < len(pos) else None
        if p == "ADV":
            j -= 1
            steps += 1
            continue
        break
    return "none"


def cue_config(toks, pos, v, heads=None, use_conj=True):
    """The full cue configuration the posterior is keyed on."""
    return (voice_cue_value(toks, pos, v, heads, use_conj), morph_value(toks, v),
            by_value(toks, pos, v, heads), degree_value(toks, pos, v))


# ------------------------------------------------------------------ counts -> P(passive | configuration)
def empty_counts():
    return {"cfg": {}, "aux": {}, "base": [0.0, 0.0], "alpha": 4.0}


def observe_voice_outcome(toks, pos, v, was_passive, counts, heads=None, use_conj=True):
    """ONE count per understood predicate -- the online observe path. Nothing is frozen."""
    a, m, b, d = cue_config(toks, pos, v, heads, use_conj)
    if a == "na":
        return
    k = "%s|%s|%s|%s" % (a, m, b, d)
    for tbl, key in ((counts["cfg"], k), (counts["aux"], a)):
        c = tbl.setdefault(key, [0.0, 0.0])
        c[0] += 1.0 if was_passive else 0.0
        c[1] += 1.0
    counts["base"][0] += 1.0 if was_passive else 0.0
    counts["base"][1] += 1.0


def voice_posterior(toks, pos, v, counts, heads=None, use_conj=True):
    """P(passive | the cue configuration at v). Dirichlet-smoothed toward the AUX-VALUE marginal, which is
    itself smoothed toward the base rate -- the shrinkage IS the backoff (same form as the coarse-role
    validities). Returns 0.0 for a non-predicate."""
    a, m, b, d = cue_config(toks, pos, v, heads, use_conj)
    if a == "na":
        return 0.0
    alpha = float(counts.get("alpha", 4.0))
    bs = counts.get("base", [0.0, 0.0])
    p_base = (bs[0] + 1.0) / (bs[1] + 2.0) if bs[1] else 0.05
    ca = counts.get("aux", {}).get(a, [0.0, 0.0])
    p_aux = (ca[0] + alpha * p_base) / (ca[1] + alpha)
    cc = counts.get("cfg", {}).get("%s|%s|%s|%s" % (a, m, b, d), [0.0, 0.0])
    return float((cc[0] + alpha * p_aux) / (cc[1] + alpha))


def is_passive_predicate(toks, pos, v, heads=None, counts=None, theta=None, use_conj=True):
    """THE BOOLEAN the four call sites need. With counts -> the graded posterior at a criterion; without ->
    the construction read (the cue value is a passive construction value). Both are clause-local and
    predicate-anchored; neither ever reads another clause's auxiliary."""
    if counts is None:
        return voice_cue_value(toks, pos, v, heads, use_conj) in PASSIVE_VALUES
    th = VOICE_THETA if theta is None else float(theta)
    return voice_posterior(toks, pos, v, counts, heads, use_conj) >= th


def voice_counts_asset():
    """Where the plastic counts live (the repo's hook_state, beside the other accrued reading assets)."""
    import os as _os
    return _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                         "data", "hook_state", "passive_voice_counts_v1.json")


def load_voice_counts(path=None):
    """The plastic side of the cue: counts on disk, or None (then the construction read is the decision)."""
    import json as _json
    import os as _os
    p = voice_counts_asset() if path is None else path
    if not _os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return _json.load(f)


def save_voice_counts(counts, path=None):
    import json as _json
    import os as _os
    p = voice_counts_asset() if path is None else path
    _os.makedirs(_os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        _json.dump(counts, f, indent=1, sort_keys=True)
# ---8<--- ORGAN BLOCK END ---8<---


# =================================================================================================
# 2. THE MEASURING INSTRUMENT -- UD-EWT, read for gold ONLY at scoring time.
# =================================================================================================
def conllu(path):
    toks, pos, heads, deps = [], [], {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if toks:
                    yield toks, pos, heads, deps
                toks, pos, heads, deps = [], [], {}, {}
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if "-" in c[0] or "." in c[0]:
                continue
            i = int(c[0])
            toks.append(c[1])
            pos.append(c[3])
            heads[i] = int(c[6])
            deps[i] = c[7]
    if toks:
        yield toks, pos, heads, deps


def voice_gold(path, cap=None):
    """Per-predicate gold voice. TWO targets, both reported:
      raw  -- UD marks the passive on the predicate that carries aux:pass / nsubj:pass / csubj:pass.
      prop -- plus a bare CONJUNCT of such a predicate (UD annotates the shared auxiliary once; the second
              conjunct of 'were selected and exhibited' IS passive for every consumer of this cue).
    Returns [(sent_idx, toks, gold_pos, gold_heads, v, raw, prop), ...] over gold-VERB predicates."""
    rows = []
    for si, (toks, pos, heads, deps) in enumerate(conllu(path)):
        if cap and si >= cap:
            break
        n = len(toks)
        ch = collections.defaultdict(list)
        for i in range(1, n + 1):
            ch[heads[i]].append(i)
        raw = {v: (pos[v - 1] == "VERB" and any(deps[c].startswith(("aux:pass", "nsubj:pass", "csubj:pass"))
                                                for c in ch[v])) for v in range(1, n + 1)}
        prop = dict(raw)
        for _ in range(3):
            for v in range(1, n + 1):
                if pos[v - 1] != "VERB" or prop[v]:
                    continue
                h = heads[v]
                if deps[v].startswith("conj") and prop.get(h) and not any(
                        deps[c].startswith(("aux", "nsubj", "csubj", "obj")) for c in ch[v]):
                    prop[v] = True
        for v in range(1, n + 1):
            if pos[v - 1] == "VERB":
                rows.append((si, toks, pos, heads, v, raw[v], prop[v]))
    return rows


_LIVE_CACHE = {}


def live_chain(toks):
    """tokens -> (categories, heads) through the LIVE brain-foundational frontend (the count-based category
    organ + the attachment arm). No gold anywhere."""
    key = tuple(toks)
    hit = _LIVE_CACHE.get(key)
    if hit is None:
        import hdlab.frontend as FE
        forms = list(toks)
        up, post = FE.tagger().tag_with_posterior(forms)
        po = FE.parser().parse(forms, up, post)
        hit = (list(up), dict(po.heads))
        _LIVE_CACHE[key] = hit
    return hit


def paired_boot(a, b, groups=None, n_boot=2000, seed=SEED):
    """Paired bootstrap of mean(b) - mean(a). `groups` clusters items (by sentence) when given."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    rng = np.random.default_rng(seed)
    if groups is None:                                     # each ITEM is its own cluster (vectorised)
        d0 = float(b.mean() - a.mean())
        n = len(a)
        diff = b - a
        draws = diff[rng.integers(0, n, (n_boot, n))].mean(axis=1)
        lo, hi = np.percentile(draws, [2.5, 97.5])
        return {"delta": round(d0, 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
                "half_width": round(float((hi - lo) / 2.0), 4), "separated": bool(lo > 0 or hi < 0)}
    # CLUSTER bootstrap, aggregated: resampling clusters and taking the ratio of summed differences to
    # summed counts is EXACTLY the per-item mean over the resampled items, and is O(n_boot x n_clusters).
    uniq = {}
    for i, g in enumerate(groups):
        uniq.setdefault(g, []).append(i)
    keys = list(uniq.values())
    diff = b - a
    gdiff = np.asarray([diff[np.asarray(v)].sum() for v in keys], dtype=float)
    gcnt = np.asarray([len(v) for v in keys], dtype=float)
    d = float(b.mean() - a.mean())
    G = len(keys)
    pick = rng.integers(0, G, (n_boot, G))
    draws = gdiff[pick].sum(axis=1) / gcnt[pick].sum(axis=1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"delta": round(d, 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "half_width": round(float((hi - lo) / 2.0), 4), "separated": bool(lo > 0 or hi < 0)}


def prf(pred, gold):
    tp = sum(1 for p, g in zip(pred, gold) if p and g)
    fp = sum(1 for p, g in zip(pred, gold) if p and not g)
    fn = sum(1 for p, g in zip(pred, gold) if not p and g)
    P = tp / max(1, tp + fp)
    R = tp / max(1, tp + fn)
    return {"fires": tp + fp, "tp": tp, "fp": fp, "fn": fn, "precision": round(P, 4), "recall": round(R, 4),
            "f1": round(2 * P * R / max(1e-9, P + R), 4),
            "accuracy": round(sum(1 for p, g in zip(pred, gold) if bool(p) == bool(g)) / max(1, len(gold)), 4)}


# =================================================================================================
# 3. ARM 1 -- THE DETECTOR ITSELF, against UD-EWT test, floors and twin measured in the same run.
# =================================================================================================
def build_counts(cap=None, use_conj=True, verbose=True):
    """Accrue P(passive | cue configuration) from UD-EWT TRAIN through the LIVE chain -- the same perception
    the consumer will have. One observe call per predicate; that IS the online path."""
    counts = empty_counts()
    rows = voice_gold(UD_TRAIN, cap=cap)
    t0 = time.time()
    seen = 0
    for si, toks, gpos, gheads, v, raw, prop in rows:
        up, lh = live_chain(toks)
        observe_voice_outcome(toks, up, v, prop, counts, heads=lh, use_conj=use_conj)
        seen += 1
        if verbose and seen % 5000 == 0:
            print("   [counts] %d predicates %.0fs" % (seen, time.time() - t0), flush=True)
    counts["n_predicates"] = seen
    counts["source"] = "UD-EWT train, live category organ + attachment arm, target = propagated voice gold"
    return counts


def arm_detector(counts, cap=None, n_boot=2000, verbose=True):
    from hdlab.thematic_role_labeler import is_passive_clause
    from hdlab.relcl_resolver import precise_passive
    rows = voice_gold(UD_TEST, cap=cap)
    rng = random.Random(SEED)
    out = {"n_predicates": len(rows), "n_sentences": len({r[0] for r in rows}),
           "n_gold_raw": sum(int(r[5]) for r in rows), "n_gold_prop": sum(int(r[6]) for r in rows)}
    t0 = time.time()
    per = {"groups": [], "gold_raw": [], "gold_prop": []}
    arms = {}
    names = ["floor_whole_sentence", "floor_clause_scoped", "floor_precise_passive",
             "new_construction", "new_graded", "new_no_conj", "twin_random"]
    for nm in names:
        arms[nm] = []
    for k, (si, toks, gpos, gheads, v, raw, prop) in enumerate(rows):
        up, lh = live_chain(toks)
        lo, hi = _clause_span(toks, up, v)
        per["groups"].append(si)
        per["gold_raw"].append(int(raw))
        per["gold_prop"].append(int(prop))
        arms["floor_whole_sentence"].append(int(is_passive_clause(list(toks), list(up))))
        arms["floor_clause_scoped"].append(int(is_passive_clause(list(toks[lo:hi]), list(up[lo:hi]))))
        arms["floor_precise_passive"].append(int(precise_passive(list(toks), list(up), v)))
        arms["new_construction"].append(int(is_passive_predicate(toks, up, v, heads=lh)))
        arms["new_graded"].append(int(is_passive_predicate(toks, up, v, heads=lh, counts=counts)))
        arms["new_no_conj"].append(int(is_passive_predicate(toks, up, v, heads=lh, use_conj=False)))
        if verbose and k and k % 1000 == 0:
            print("   [detector] %d/%d %.0fs" % (k, len(rows), time.time() - t0), flush=True)
    # TWIN: an information-free detector that fires on a RANDOM equal-size set of predicates.
    rate = sum(arms["new_construction"]) / max(1, len(rows))
    arms["twin_random"] = [int(rng.random() < rate) for _ in rows]
    out["firing_rate_new"] = round(rate, 4)
    for target in ("gold_raw", "gold_prop"):
        g = per[target]
        out[target] = {nm: prf(arms[nm], g) for nm in names}
        base = np.asarray([int(bool(x) == bool(y)) for x, y in zip(arms["floor_whole_sentence"], g)], dtype=float)
        out[target + "_vs_floor"] = {}
        for nm in names:
            vec = np.asarray([int(bool(x) == bool(y)) for x, y in zip(arms[nm], g)], dtype=float)
            out[target + "_vs_floor"][nm] = paired_boot(base, vec, groups=per["groups"], n_boot=n_boot)
    # where the shipped cue is wrong and the new one is right, and the reverse -- the anatomy, in counts
    fixes = sum(1 for a, b, g in zip(arms["floor_whole_sentence"], arms["new_construction"], per["gold_prop"])
                if bool(a) != bool(g) and bool(b) == bool(g))
    breaks = sum(1 for a, b, g in zip(arms["floor_whole_sentence"], arms["new_construction"], per["gold_prop"])
                 if bool(a) == bool(g) and bool(b) != bool(g))
    out["anatomy_vs_shipped"] = {"fixes": fixes, "breaks": breaks}
    vc = collections.Counter()
    for si, toks, gpos, gheads, v, raw, prop in rows:
        up, lh = live_chain(toks)
        vc[voice_cue_value(toks, up, v, lh)] += 1
    out["cue_value_distribution"] = dict(vc)
    return out


# =================================================================================================
# 4. ARM 2 -- THE CONSUMER: the board's who-did-what AGENT decision and the override anatomy.
# =================================================================================================
def agent_rows(counts, cap=None, verbose=True):
    """The pri-106 agent population: UD-EWT test gold agents (nsubj active / obl:agent passive), the live
    chain, the board arm's own candidate set. One row per gold agent decision."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.thematic_role_labeler import is_passive_clause
    import hdlab.graded_role_assigner as GRA
    import hdlab.frontend as FE

    gaz = load_given_gazetteer()
    sents = load_ud(UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    rows = []
    cache = {}
    t0 = time.time()
    for k, (toks, v, ag, passive_gold) in enumerate(items):
        key = tuple(toks)
        if key not in cache:
            forms = list(toks)
            up, post = FE.tagger().tag_with_posterior(forms)
            po = FE.parser().parse(forms, up, post)
            cache[key] = (list(up), post, dict(po.heads))
        up, post, lh = cache[key]
        cands = AG._clause_local_nominals(toks, up, v, post=post)
        if not cands:
            continue
        cf = [c for c in cands if str(c["head"]).lower() not in GRA._AGENT_ANIM_PRON
              or str(c["head"]).lower() in GRA.NOMINATIVE_PRON]
        cm_cands = cf or cands
        base_i = AG._floor_positional_idx(v, cands)
        base = toks[base_i] if base_i is not None else None
        cm = GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None, gaz=gaz)
        low = _low(toks)
        lo, hi = GRA.clause_bounds(list(toks), list(up), v - 1)
        has_by = any(low[i] == "by" for i in range(lo, min(hi, len(low))))
        rows.append({
            "gold": toks[ag - 1], "base": base, "cm": cm, "gold_passive": bool(passive_gold),
            # the three marked cues, EACH measured under the shipped and the new voice read
            "passive_shipped": bool(is_passive_clause(list(toks), list(up))),
            "passive_clause_scoped": bool(is_passive_clause(list(toks[lo:hi]), list(up[lo:hi]))),
            "passive_new": bool(is_passive_predicate(toks, up, v, heads=lh)),
            "passive_new_graded": bool(is_passive_predicate(toks, up, v, heads=lh, counts=counts)),
            "has_by": bool(has_by),
            "by_local": by_value(toks, up, v, lh) == "by",
            "pp_gov": bool(base_i is not None and GRA._agent_pp_governed(low, up, base_i)),
            "noncase": bool(base is not None and str(base).lower() in GRA._AGENT_ANIM_PRON
                            and str(base).lower() not in GRA.NOMINATIVE_PRON),
            "sent": key,
        })
        if verbose and k and k % 500 == 0:
            print("   [agent] %d/%d %.0fs" % (k, len(items), time.time() - t0), flush=True)
    return rows


def _match(a, b):
    return a is not None and str(a).lower() == str(b).lower()


def arm_override(rows, n_boot=2000):
    """Every arm is the SAME hybrid (word-order default, competition on a marked cue) with ONE thing changed:
    which voice read licenses the passive cue."""
    def score(voice_key, require_by=False, twin_rng=None):
        hit, marked = [], []
        for r in rows:
            p = r[voice_key] if voice_key else False
            if twin_rng is not None:
                p = twin_rng.random() < twin_rng.rate
            if require_by and p:
                p = p and r["by_local"]
            m = bool(p or r["pp_gov"] or r["noncase"])
            pick = r["cm"] if m else r["base"]
            hit.append(int(_match(pick, r["gold"])))
            marked.append(m)
        return np.asarray(hit, dtype=float), marked

    out = {"n": len(rows), "n_gold_passive": sum(int(r["gold_passive"]) for r in rows)}
    # THE FLOOR IS THE POSITIONAL PICK ITSELF -- the nearest pre-verbal candidate, no override of any kind.
    # (`score(None)` is NOT the floor: it disables only the passive licence and keeps pp_gov / noncase, which
    # are worth +0.0007 on their own. It is reported separately as `hybrid_without_the_passive_licence`.)
    floor = np.asarray([int(_match(r["base"], r["gold"])) for r in rows], dtype=float)
    nopass, _ = score(None)
    arms = collections.OrderedDict()
    arms["floor_positional"] = (floor, None)
    arms["hybrid_without_the_passive_licence"] = (nopass, None)
    for nm, key, rb in (("landed_whole_sentence", "passive_shipped", False),
                        ("clause_scoped", "passive_clause_scoped", False),
                        ("clause_scoped_with_by", "passive_clause_scoped", True),
                        ("new_predicate_anchored", "passive_new", False),
                        ("new_predicate_anchored_with_by", "passive_new", True),
                        ("new_graded", "passive_new_graded", False),
                        ("new_graded_with_by", "passive_new_graded", True)):
        v, m = score(key, require_by=rb)
        arms[nm] = (v, m)
    # TWIN: the passive licence fires on a RANDOM equal-size set of decisions (same rate, no information)
    class _R:
        def __init__(self, rate, seed):
            self.rate = rate
            self._r = random.Random(seed)

        def random(self):
            return self._r.random()
    rate_new = sum(int(r["passive_new"]) for r in rows) / max(1, len(rows))
    tv, tm = score("passive_new", twin_rng=_R(rate_new, SEED))
    arms["twin_random_passive"] = (tv, tm)

    out["accuracy"] = {nm: round(float(v.mean()), 4) for nm, (v, m) in arms.items()}
    out["vs_floor"] = {nm: paired_boot(floor, v, n_boot=n_boot) for nm, (v, m) in arms.items() if nm != "floor_positional"}
    landed = arms["landed_whole_sentence"][0]
    out["vs_landed"] = {nm: paired_boot(landed, v, n_boot=n_boot) for nm, (v, m) in arms.items()
                        if nm not in ("floor_positional", "landed_whole_sentence")}
    # THE OVERRIDE ANATOMY, per voice read: of the decisions where the PASSIVE cue ALONE licenses the
    # override, how many does it fix, how many does it break, and how many fire on a gold-ACTIVE clause.
    out["passive_licence_anatomy"] = {}
    for nm, key, rb in (("landed_whole_sentence", "passive_shipped", False),
                        ("clause_scoped", "passive_clause_scoped", False),
                        ("clause_scoped_with_by", "passive_clause_scoped", True),
                        ("new_predicate_anchored", "passive_new", False),
                        ("new_predicate_anchored_with_by", "passive_new", True),
                        ("new_graded_with_by", "passive_new_graded", True)):
        n = fx = bk = nt = act = 0
        for r in rows:
            p = bool(r[key])
            if rb:
                p = p and r["by_local"]
            if not p or r["pp_gov"] or r["noncase"]:
                continue                                # the PASSIVE cue ALONE (pri 106's partition)
            n += 1
            act += int(not r["gold_passive"])
            fo = _match(r["base"], r["gold"])
            ho = _match(r["cm"], r["gold"])
            fx += int(ho and not fo)
            bk += int(fo and not ho)
            nt += int(ho == fo)
        out["passive_licence_anatomy"][nm] = {"n": n, "fixes": fx, "breaks": bk, "neutral": nt,
                                              "fired_gold_active": act,
                                              "conflict_validity": round(fx / max(1, fx + bk), 4)}
    return out


# =================================================================================================
# 5. ARM 3 -- NO-REGRESS on the OTHER consumers of the same cue (the four call sites).
# =================================================================================================
def arm_call_sites(counts, cap=700, n_boot=2000, verbose=True):
    """Call site 1 (coarse_role_cues voice_order, line ~659) and call site 2 (agent_supports, line ~1584).

    CALL SITE 1 is the one that can regress: the `voice_order` cue VALUE keys a LEARNED validity table that
    was accrued with the shipped detector. Swapping the detector without re-accruing the table changes which
    counts a decision reads. So it is measured BOTH ways: the shipped table with the new cue, and the shipped
    table unchanged (the no-regress reference). Population: every ARGUMENT head UD-EWT labels, live heads.
    """
    import hdlab.graded_role_assigner as GRA
    tab = GRA.load_coarse_validities()
    orig_cues = GRA.coarse_role_cues

    def patched_cues(toks, pos, heads, i, frames=None, v3=False, conf=None, v4=False):
        cues = orig_cues(toks, pos, heads, i, frames, v3, conf, v4)
        h = heads.get(i, 0) or 0
        hc = GRA._head_class(pos, h, v3)
        if hc in ("VERB", "AUX") and h:
            vc = GRA.voice_cues(toks, pos, h)
            strong = bool(vc["vc_strong"] or vc["vc_get"] or vc["vc_being"])
            weak = bool(vc["vc_bypp"] or is_passive_predicate(toks, pos, h, heads=heads, counts=counts))
            order = "pre" if (h and i < h) else ("post" if h else "root")
            cues["voice_order"] = ("passive_strong_" if strong else ("passive_weak_" if weak else "active_")) + order
            passive = strong or weak
            if cues.get("prep") in ("by", "by_passive"):
                cues["prep"] = "by_passive" if passive else "by"
        return cues

    rows = []
    for si, (toks, gpos, gheads, deps) in enumerate(conllu(UD_TEST)):
        if cap and si >= cap:
            break
        rows.append((si, toks, gpos, gheads, deps))
    pops = {"all_arguments": [], "nsubj_pass": [], "obl_agent": [], "core": []}
    preds = {"shipped": [], "patched": []}
    t0 = time.time()
    for k, (si, toks, gpos, gheads, deps) in enumerate(rows):
        up, lh = live_chain(toks)
        for tag, fn in (("shipped", orig_cues), ("patched", patched_cues)):
            GRA.coarse_role_cues = fn
            try:
                r = GRA.coarse_roles(list(toks), list(up), dict(lh), tab)
            finally:
                GRA.coarse_role_cues = orig_cues
            preds[tag].append(r)
        r_sh, r_pa = preds["shipped"][-1], preds["patched"][-1]
        for i in range(1, len(toks) + 1):
            g = deps.get(i, "")
            gb = g.split(":")[0]
            base = g if g in ("nsubj:pass", "obl:agent") else gb
            if base not in ("nsubj", "obj", "iobj", "obl", "nmod") and g not in ("nsubj:pass", "obl:agent"):
                continue
            item = (int(_deps_match(r_sh.get(i), g)), int(_deps_match(r_pa.get(i), g)), si)
            pops["all_arguments"].append(item)
            if gb in ("nsubj", "obj", "iobj"):
                pops["core"].append(item)
            if g.startswith("nsubj:pass"):
                pops["nsubj_pass"].append(item)
            if g.startswith("obl:agent"):
                pops["obl_agent"].append(item)
        if verbose and k and k % 200 == 0:
            print("   [call-site-1] %d/%d %.0fs" % (k, len(rows), time.time() - t0), flush=True)
    out = {}
    for nm, lst in pops.items():
        if not lst:
            out[nm] = {"n": 0}
            continue
        a = np.asarray([x[0] for x in lst], dtype=float)
        b = np.asarray([x[1] for x in lst], dtype=float)
        g = [x[2] for x in lst]
        out[nm] = {"n": len(lst), "shipped": round(float(a.mean()), 4), "patched": round(float(b.mean()), 4),
                   "delta": paired_boot(a, b, groups=g, n_boot=n_boot)}
    return out


def _deps_match(pred, gold):
    if pred is None:
        return False
    if gold in ("nsubj:pass", "obl:agent"):
        return pred == gold
    return pred.split(":")[0] == gold.split(":")[0]


def arm_agent_supports(counts, rows, n_boot=2000):
    """CALL SITE 2 (`agent_supports`, line ~1584): `passive = is_passive_clause(toks, pos)` flips EVERY
    candidate's preverbal / byagent support for the WHOLE sentence. Measured as the competition's own pick
    accuracy on the same agent population, shipped voice read vs predicate-anchored."""
    import hdlab.graded_role_assigner as GRA
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.thematic_role_labeler import is_passive_clause
    gaz = load_given_gazetteer()
    orig = GRA.is_passive_clause
    sents = load_ud(UD_TEST)
    items = AG.gold_agent_items(sents)
    res = {}
    for tag in ("shipped", "patched"):
        hits = []
        groups = []
        for si, (toks, v, ag, gp) in enumerate(items):
            up, lh = live_chain(toks)
            cands = AG._clause_local_nominals(toks, up, v, post=None)
            if not cands:
                continue
            cf = [c for c in cands if str(c["head"]).lower() not in GRA._AGENT_ANIM_PRON
                  or str(c["head"]).lower() in GRA.NOMINATIVE_PRON]
            if tag == "patched":
                flag = is_passive_predicate(toks, up, v, heads=lh, counts=counts)
                GRA.is_passive_clause = lambda t, p, w=3, _f=flag: _f
            else:
                GRA.is_passive_clause = orig
            try:
                pick = GRA.agent_competition_pick(toks, up, v - 1, cf or cands, cluster_freq=None, gaz=gaz)
            finally:
                GRA.is_passive_clause = orig
            hits.append(int(_match(pick, toks[ag - 1])))
            groups.append(si)
        res[tag] = (np.asarray(hits, dtype=float), groups)
    a, g = res["shipped"]
    b, _ = res["patched"]
    return {"n": len(a), "shipped_competition": round(float(a.mean()), 4),
            "patched_competition": round(float(b.mean()), 4),
            "delta": paired_boot(a, b, groups=g, n_boot=n_boot)}


# =================================================================================================
# 6. SELF-TEST, RUN, CLI
# =================================================================================================
def self_test():
    P = F = 0

    def ck(name, cond, detail=""):
        nonlocal P, F
        if cond:
            P += 1
            print("  ok   %s" % name)
        else:
            F += 1
            print("  FAIL %s %s" % (name, detail))

    T = "The dog was bitten by the man .".split()
    U = ["DET", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
    ck("canonical passive fires", voice_cue_value(T, U, 4) == "be_chain", voice_cue_value(T, U, 4))
    ck("by-phrase is seen for the predicate", by_value(T, U, 4) == "by", by_value(T, U, 4))
    H = {1: 2, 2: 4, 3: 4, 4: 0, 5: 7, 6: 7, 7: 4, 8: 4}
    ck("the arc CONFIRMS the auxiliary", voice_cue_value(T, U, 4, H) == "be_arc", voice_cue_value(T, U, 4, H))

    T2 = "He built it .".split()
    U2 = ["PRON", "VERB", "PRON", "PUNCT"]
    ck("active does not fire", not is_passive_predicate(T2, U2, 2))

    # THE DEFECT ITSELF: a passive RELATIVE clause must not make the MAIN predicate passive.
    T3 = "The man who was arrested killed the dog .".split()
    U3 = ["DET", "NOUN", "PRON", "AUX", "VERB", "VERB", "DET", "NOUN", "PUNCT"]
    from hdlab.thematic_role_labeler import is_passive_clause
    ck("shipped detector false-fires on the main predicate", is_passive_clause(T3, U3) is True)
    ck("clause-local cue fires on the relative predicate", is_passive_predicate(T3, U3, 5))
    ck("clause-local cue does NOT fire on the main predicate", not is_passive_predicate(T3, U3, 6),
       voice_cue_value(T3, U3, 6))

    # progressive is ACTIVE even though the auxiliary is there
    T4 = "The dog was chasing the cat .".split()
    U4 = ["DET", "NOUN", "AUX", "VERB", "DET", "NOUN", "PUNCT"]
    ck("be + V-ing is PROGRESSIVE, not passive", voice_cue_value(T4, U4, 4) == "prog")

    # a copula + determiner cancels the expectation ("Here is a revised draft")
    T5 = "Here is a revised draft .".split()
    U5 = ["ADV", "AUX", "DET", "VERB", "NOUN", "PUNCT"]
    ck("a determiner between aux and participle cancels", not is_passive_predicate(T5, U5, 4))

    # an infinitival `to` opens a new predicate ("will be around to assist them")
    T6 = "We will be around to assist them .".split()
    U6 = ["PRON", "AUX", "AUX", "ADV", "PART", "VERB", "PRON", "PUNCT"]
    ck("infinitival `to` stops the auxiliary chain", not is_passive_predicate(T6, U6, 6))

    # coordination shares the auxiliary
    T7 = "The artworks were selected and exhibited .".split()
    U7 = ["DET", "NOUN", "AUX", "VERB", "CCONJ", "VERB", "PUNCT"]
    ck("a bare conjunct inherits the auxiliary", voice_cue_value(T7, U7, 6) == "conj", voice_cue_value(T7, U7, 6))
    ck("without the coordination cue it abstains", not is_passive_predicate(T7, U7, 6, use_conj=False))

    # get-passive
    T8 = "I got yelled at .".split()
    U8 = ["PRON", "AUX", "VERB", "ADP", "PUNCT"]
    ck("get-passive fires", voice_cue_value(T8, U8, 3) == "get_chain", voice_cue_value(T8, U8, 3))

    # fronted participle with postposed finite be
    T9 = "Attached is a spreadsheet .".split()
    U9 = ["VERB", "AUX", "DET", "NOUN", "PUNCT"]
    ck("fronted participle + postposed be fires", voice_cue_value(T9, U9, 1) == "be_inv", voice_cue_value(T9, U9, 1))

    # degree modifier -> adjectival participle evidence is SEEN (a cue value, not a hard veto)
    T11 = "we 're gon na start off .".split()
    U11 = ["PRON", "AUX", "VERB", "PART", "VERB", "ADP", "PUNCT"]
    ck("a reduced semi-modal host (`gon na`) is not a passive",
       voice_cue_value(T11, U11, 3) == "semimodal", voice_cue_value(T11, U11, 3))

    T10 = "She was very tired .".split()
    U10 = ["PRON", "AUX", "ADV", "VERB", "PUNCT"]
    ck("a degree modifier is recorded as adjectival evidence", degree_value(T10, U10, 4) == "deg")

    # counts: the posterior is a probability, moves with observation, and round-trips
    c = empty_counts()
    for _ in range(50):
        observe_voice_outcome(T, U, 4, True, c)
        observe_voice_outcome(T2, U2, 2, False, c)
    p_pass = voice_posterior(T, U, 4, c)
    p_act = voice_posterior(T2, U2, 2, c)
    ck("posterior is in [0,1]", 0.0 <= p_pass <= 1.0 and 0.0 <= p_act <= 1.0)
    ck("observation moves the belief the right way", p_pass > 0.8 > p_act, (p_pass, p_act))
    ck("the graded read at the criterion agrees with the construction read",
       is_passive_predicate(T, U, 4, counts=c) and not is_passive_predicate(T2, U2, 2, counts=c))
    ck("non-predicates return `na`", voice_cue_value(T, U, 2) == "na")

    # THE EXISTING WITNESS'S VOICE ASSERTIONS STILL HOLD UNDER THE PATCHED CUE (verification/
    # test_coarse_role_competition.py checks `voice_order == passive_strong_pre`, `prep == by_passive`,
    # `nsubj:pass` and `obl:agent` on "The dog was bitten by the man ."). Run here against the PATCHED
    # coarse_role_cues -- the witness itself is untouched and green at HEAD (37/37).
    try:
        import hdlab.graded_role_assigner as _G
        _tab = _G.load_coarse_validities()
        _orig = _G.coarse_role_cues

        def _patched(toks, pos, heads, i, frames=None, v3=False, conf=None, v4=False):
            cues = _orig(toks, pos, heads, i, frames, v3, conf, v4)
            h = heads.get(i, 0) or 0
            hc = _G._head_class(pos, h, v3)
            if hc in ("VERB", "AUX") and h:
                vc = _G.voice_cues(toks, pos, h)
                strong = bool(vc["vc_strong"] or vc["vc_get"] or vc["vc_being"])
                weak = bool(vc["vc_bypp"] or is_passive_predicate(toks, pos, h, heads=heads))
                order = "pre" if (h and i < h) else ("post" if h else "root")
                cues["voice_order"] = ("passive_strong_" if strong else
                                       ("passive_weak_" if weak else "active_")) + order
                if cues.get("prep") in ("by", "by_passive"):
                    cues["prep"] = "by_passive" if (strong or weak) else "by"
            return cues
        _t = "The dog was bitten by the man .".split()
        _p = ["DET", "NOUN", "AUX", "VERB", "ADP", "DET", "NOUN", "PUNCT"]
        _h = {1: 2, 2: 4, 3: 4, 4: 0, 5: 7, 6: 7, 7: 4, 8: 4}
        _G.coarse_role_cues = _patched
        try:
            c2 = _G.coarse_role_cues(_t, _p, _h, 2); c7 = _G.coarse_role_cues(_t, _p, _h, 7)
            r = _G.coarse_roles(_t, _p, _h, _tab)
        finally:
            _G.coarse_role_cues = _orig
        ck("witness assertions hold under the patched cue (voice_order / by_passive / nsubj:pass / obl:agent)",
           c2["voice_order"] == "passive_strong_pre" and c7["prep"] == "by_passive"
           and r.get(2) == "nsubj:pass" and r.get(7) == "obl:agent", (c2, c7, r))
    except Exception as e:                                          # pragma: no cover
        ck("witness assertions hold under the patched cue", False, repr(e)[:200])

    # THE PATCH IS THE ORGAN THAT WAS MEASURED, and it applies to the working tree.
    try:
        emit_patch(verbose=False)
        ok, why = patch_matches_cell()
        ck("PATCH == CELL (the diff's organ block is byte-identical to this file's)", ok, why)
        import subprocess
        r = subprocess.run(["git", "apply", "--check", "--ignore-whitespace", PATCH_PATH],
                           cwd=REPO, capture_output=True, text=True)
        ck("the diff applies cleanly to the working tree", r.returncode == 0, r.stderr.strip()[:200])
        # PATCH FIDELITY: build the PATCHED module in a temp file, import it, and check the organ answers
        # exactly what this cell answered -- on disk nothing in hdlab/ is touched.
        import importlib.util
        import tempfile
        _src, patched = _apply(os.path.join(REPO, "hdlab", "thematic_role_labeler.py"),
                               _TRL_DEPRECATE, _TRL_ANCHOR, organ_block())
        tmp = os.path.join(tempfile.gettempdir(), "_trl_patched_pri111.py")
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(patched)
        spec = importlib.util.spec_from_file_location("_trl_patched_pri111", tmp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cases = [(T, U, 4), (T2, U2, 2), (T3, U3, 5), (T3, U3, 6), (T4, U4, 4), (T5, U5, 4),
                 (T6, U6, 6), (T7, U7, 6), (T8, U8, 3), (T9, U9, 1)]
        same = all(mod.is_passive_predicate(t, u, v) == is_passive_predicate(t, u, v) for t, u, v in cases)
        ck("the PATCHED hdlab module answers identically to this cell", same)
        ck("the patched module still exports the deprecated sentence-level cue",
           mod.is_passive_clause(T, U) is True and "DEPRECATED" in (mod.is_passive_clause.__doc__ or ""))
        # PHASE 7b: every patched file must still COMPILE, and the three folded detectors must be gone /
        # delegating. Compiled from the patched text; nothing under hdlab/ is written.
        for rel, edits, ib, il in (("hdlab/graded_role_assigner.py", _GRA_EDITS, None, None),
                                   ("hdlab/relcl_resolver.py", _RELCL_EDITS, None, None),
                                   ("hdlab/arc_labeler.py", _AL_EDITS, None, None),
                                   ("experiments/exp_board_agent_slot_ud_v1.py", _BOARD_EDITS, None, None)):
            _s, _o = _apply(os.path.join(REPO, *rel.split("/")), edits, ib, il)
            try:
                compile(_o, rel, "exec")
                ck("the patched %s compiles" % rel, True)
            except SyntaxError as e:
                ck("the patched %s compiles" % rel, False, "%s line %s" % (e.msg, e.lineno))
        _s, _al = _apply(os.path.join(REPO, "hdlab", "arc_labeler.py"), _AL_EDITS)
        _code = [l for l in _al.splitlines() if not l.lstrip().startswith("#")]
        ck("label_voice_correct / VOICE_CORRECTION / _BE_AUX are GONE from the patched arc_labeler's CODE",
           not any(("label_voice_correct" in l or "VOICE_CORRECTION" in l or "_BE_AUX" in l) for l in _code),
           [l.strip()[:90] for l in _code if "label_voice_correct" in l or "VOICE_CORRECTION" in l
            or "_BE_AUX" in l][:3])
        ck("the patched arc_labeler still accepts voice_correction= (no caller churns)",
           "voice_correction: " in _al)
        _s, _rr = _apply(os.path.join(REPO, "hdlab", "relcl_resolver.py"), _RELCL_EDITS)
        ck("the patched precise_passive delegates to the one organ",
           "return bool(is_passive_predicate(toks, pos, v))" in _rr)
    except SystemExit as e:
        ck("patch anchors still match the live files", False, str(e)[:300])

    print("\n%d/%d checks passed" % (P, P + F))
    return 0 if F == 0 else 1


def run(smoke=False, n_boot=2000, verbose=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    cap_tr = 400 if smoke else None
    cap_te = 200 if smoke else None
    nb = 200 if smoke else n_boot
    t0 = time.time()
    print("[1] accruing P(passive | cue configuration) on UD-EWT TRAIN through the live chain ...", flush=True)
    counts = build_counts(cap=cap_tr, verbose=verbose)
    save_voice_counts(counts)
    print("    %d predicates; base rate %.4f" % (counts["n_predicates"],
                                                 counts["base"][0] / max(1.0, counts["base"][1])), flush=True)
    print("[2] the detector against UD-EWT TEST ...", flush=True)
    det = arm_detector(counts, cap=cap_te, n_boot=nb, verbose=verbose)
    json.dump(det, open(os.path.join(OUT_DIR, "detector.json"), "w"), indent=1)
    print("[3] the agent consumer + the override anatomy ...", flush=True)
    rows = agent_rows(counts, cap=cap_te, verbose=verbose)
    ovr = arm_override(rows, n_boot=nb)
    json.dump(ovr, open(os.path.join(OUT_DIR, "override.json"), "w"), indent=1)
    print("[4] the other call sites (no-regress) ...", flush=True)
    cs = arm_call_sites(counts, cap=(60 if smoke else 700), n_boot=nb, verbose=verbose)
    json.dump(cs, open(os.path.join(OUT_DIR, "call_sites.json"), "w"), indent=1)
    res = {"anchor": ANCHOR, "elapsed_s": round(time.time() - t0, 1), "smoke": bool(smoke),
           "counts": {"n_predicates": counts["n_predicates"],
                      "base_rate": round(counts["base"][0] / max(1.0, counts["base"][1]), 4),
                      "n_configurations": len(counts["cfg"])},
           "detector": det, "override": ovr, "call_sites": cs}
    json.dump(res, open(os.path.join(OUT_DIR, "metrics.json"), "w"), indent=1)
    _print(res)
    return res


def _print(res):
    d = res["detector"]
    print("\n=== DETECTOR (UD-EWT test, %d predicates, %d gold passive [propagated %d]) ==="
          % (d["n_predicates"], d["n_gold_raw"], d["n_gold_prop"]))
    for nm, v in d["gold_prop"].items():
        print("  %-28s P %.4f R %.4f F %.4f  acc %.4f  (fires %d)"
              % (nm, v["precision"], v["recall"], v["f1"], v["accuracy"], v["fires"]))
    o = res["override"]
    print("\n=== AGENT CONSUMER (n=%d) ===" % o["n"])
    for nm, v in o["accuracy"].items():
        s = o["vs_floor"].get(nm)
        print("  %-32s %.4f%s" % (nm, v, ("   vs floor %+.4f CI%s%s" % (s["delta"], s["ci95"],
                                                                       " SEP" if s["separated"] else "")) if s else ""))
    print("\n=== PASSIVE-LICENCE ANATOMY ===")
    for nm, v in o["passive_licence_anatomy"].items():
        print("  %-32s n %3d fixes %2d breaks %2d neutral %2d  gold-active %2d  validity %.3f"
              % (nm, v["n"], v["fixes"], v["breaks"], v["neutral"], v["fired_gold_active"], v["conflict_validity"]))
    print("\n=== NO-REGRESS (coarse role labels, live heads) ===")
    for nm, v in res["call_sites"].items():
        if v.get("n"):
            print("  %-18s n %5d  shipped %.4f -> patched %.4f  %+.4f CI%s"
                  % (nm, v["n"], v["shipped"], v["patched"], v["delta"]["delta"], v["delta"]["ci95"]))


# =================================================================================================
# 7. THE PATCH -- generated FROM this file's organ block, so the shipped organ IS the measured organ.
# =================================================================================================
SLUG = ("the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides"
        "_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes")
PATCH_PATH = os.path.join(REPO, "notes", "problems", SLUG, "passive_cue_patch.diff")
_BEGIN = "# ---8<--- ORGAN BLOCK BEGIN"
_END = "# ---8<--- ORGAN BLOCK END ---8<---"


def organ_block():
    """The organ source, taken from THIS file between the markers -- the single source of truth."""
    with open(os.path.abspath(__file__), encoding="utf-8", newline="") as f:
        lines = f.read().splitlines(True)
    b = next(i for i, l in enumerate(lines) if l.startswith(_BEGIN))
    e = next(i for i, l in enumerate(lines) if l.startswith(_END))
    return lines[b + 2:e]          # skip the two marker-comment lines at the top; stop before END


# Each entry: (path, [(exact_old, new), ...]). Exact-string edits so a silent mismatch FAILS loudly.
_RELCL_IMPORT_OLD = 'from hdlab.thematic_role_labeler import _is_participle   # participle test for the precise voice cue\n'
_RELCL_IMPORT_NEW = 'from hdlab.thematic_role_labeler import _is_participle, is_passive_predicate   # the ONE voice organ (pri 111)\n'
_PP_OLD = 'def precise_passive(toks: Sequence[str], pos: Sequence[str], v: int) -> bool:\n    """Precise voice cue: a BE-aux in the 3 tokens before v AND the verb token is a past participle."""\n    lo = max(1, v - 3)\n    has_be = any(toks[j - 1].lower() in BE_AUX for j in range(lo, v))\n    vtag = pos[v - 1] if v - 1 < len(pos) else None\n    return has_be and _is_participle(toks[v - 1], vtag)\n'
_PP_NEW = 'def precise_passive(toks: Sequence[str], pos: Sequence[str], v: int) -> bool:\n    """FOLDED ONTO THE ONE VOICE ORGAN (pri 111, 2026-09-14). This was a SECOND implementation of the same\n    computation -- "a BE-aux in the 3 tokens before v AND a past-participle suffix at v" -- and it is dominated\n    by `thematic_role_labeler.is_passive_predicate` on every population measured: per predicate, UD-EWT test\n    0.9464/0.7794 against 0.9606/0.8971, GUM 0.9321/0.7982 against 0.9503/0.8517, GENTLE (OOD) 0.9397/0.9083\n    against 0.9821/0.9167. The NAME is kept so that no call site churns; the COMPUTATION is now the organ\'s,\n    which means the get-passive, the fronted-participle inversion and the shared-auxiliary conjunct reach the\n    six consumers of this function for the first time, and `be + V-ing` stops reading as a passive.\n    Measured at the consumers before landing: the board\'s who-did-what PATIENT row 0.8120 -> 0.8135 with its\n    floor and its gold-parse ceiling unchanged."""\n    return bool(is_passive_predicate(toks, pos, v))\n'
_GATE_OLD = '    if not (0 <= v0 < len(toks)):\n        return False\n    tag = pos[v0] if v0 < len(pos) else None\n    if not _is_participle(toks[v0], tag):\n        return False\n'
_GATE_NEW = "    if not (0 <= v0 < len(toks)):\n        return False\n    # pri 111 (2026-09-14): the participle SUFFIX test is replaced by the ONE voice organ. `_is_participle`\n    # missed irregular participles that carry no -ed/-en (`blown`, `put`, `shut`), which is why `was blown up\n    # by a bomb` never emitted the byhead CASE cue. Measured: the gate's firing rate HALVES (32 -> 16 of 1423\n    # agent decisions -- it now fires only where the predicate really is passive) and the agent row is +0.0007.\n    if not is_passive_predicate(toks, pos, v0 + 1):\n        return False\n"
_AL_HEAD_OLD = 'VOICE_CORRECTION: bool = True     # the LIVE default (owner-DONE; measured no-regress, patient recall up)\n_BE_AUX = {"be", "is", "are", "was", "were", "been", "being", "am", "get", "got", "gotten"}\n\n\ndef label_voice_correct(toks: Sequence[str], pos: Sequence[str], heads: Dict[int, int],\n                        labels: Dict[int, str]) -> Dict[int, str]:\n    """An `nsubj` whose head is a VERB/AUX carrying a be/get auxiliary child and a past-participle form -> `nsubj:pass`.\n    Indices 1-based (dep -> head); `labels` is not mutated."""\n    n = len(toks)\n    out = dict(labels)\n    ch: Dict[int, list] = {}\n    for i in range(1, n + 1):\n        ch.setdefault(heads.get(i, 0), []).append(i)\n    for i in range(1, n + 1):\n        h = heads.get(i, 0)\n        if h and pos[h - 1] in ("VERB", "AUX") and out.get(i) == "nsubj":\n            aux = [c for c in ch.get(h, []) if pos[c - 1] == "AUX" and toks[c - 1].lower() in _BE_AUX]\n            if aux and toks[h - 1].lower().endswith(("ed", "en")):\n                out[i] = "nsubj:pass"\n    return out\n'
_AL_HEAD_NEW = '# RETIRED 2026-09-14 (pri 111): `VOICE_CORRECTION` / `_BE_AUX` / `label_voice_correct` are DELETED. They were a\n# SIXTH implementation of the voice cue (an aux CHILD of the head plus an `ed`/`en` suffix), and they are DEAD on\n# the live path: counted on UD-EWT test 700, the correction changes 25 labels with the competition OFF and\n# EXACTLY ZERO with `COMPETITION_ROLES` live -- the Competition-Model organ below already decides every label it\n# would have changed, and decides it from a better voice read. The `voice_correction` keyword survives on\n# `label()` (accepted, ignored) so that no caller churns; it now truthfully names a step that does not exist.\n'
_AL_BODY_OLD = '        use = VOICE_CORRECTION if voice_correction is None else voice_correction\n        out = label_voice_correct(tokens, pos, heads, out) if use else out\n        use_cm = COMPETITION_ROLES if competition_roles is None else competition_roles\n'
_AL_BODY_NEW = '        # pri 111: the voice post-correction is retired (see the note above); `voice_correction` is ignored.\n        use_cm = COMPETITION_ROLES if competition_roles is None else competition_roles\n'
_RELCL_EDITS = [
    (_RELCL_IMPORT_OLD, _RELCL_IMPORT_NEW),
    (_PP_OLD, _PP_NEW),
]
_AL_DOC_OLD = '        the byte-identical fast plan (~9x); output is identical to _predict_label for ANY weights (theorem). Then\n        the VOICE post-correction (module default VOICE_CORRECTION; pass False for the raw perceptron labels)."""\n'
_AL_DOC_NEW = '        the byte-identical fast plan (~9x); output is identical to _predict_label for ANY weights (theorem).\n        `voice_correction` is ACCEPTED AND IGNORED since pri 111 retired the voice post-correction (see above)."""\n'
_AL_EDITS = [
    (_AL_HEAD_OLD, _AL_HEAD_NEW),
    (_AL_DOC_OLD, _AL_DOC_NEW),
    (_AL_BODY_OLD, _AL_BODY_NEW),
]



_Q = chr(34) * 3        # a triple quote, spelled so this file can hold it inside a string
_TRL_ANCHOR = ("# ---------------------------------------------------------------------------------------------\n"
               "# EARNED cue-integration: feature-dict builder for a (verb_idx, arg_idx) candidate pair.\n")
_GRA_EDITS = [
    ("from hdlab.thematic_role_labeler import _is_participle, is_passive_clause, lemma_verb\n",
     "from hdlab.thematic_role_labeler import _is_participle, is_passive_clause, is_passive_predicate, lemma_verb\n"),
    ('        weak = bool(vc["vc_bypp"] or is_passive_clause(toks, pos, h))             # by-PP / reduced-passive evidence\n',
     '        # pri 111: the voice cue is a property of the PREDICATE h, not of the sentence. (The old call also passed\n'
     '        # the head index `h` into `is_passive_clause`\'s WINDOW parameter -- a latent defect: the scan widened with\n'
     '        # the predicate\'s position in the sentence.)\n'
     '        weak = bool(vc["vc_bypp"] or is_passive_predicate(toks, pos, h, heads=heads))   # by-PP / clause-local passive\n'),
    ("    low = [t.lower() for t in toks]\n    passive = is_passive_clause(toks, pos)\n",
     "    low = [t.lower() for t in toks]\n"
     "    passive = is_passive_predicate(toks, pos, v0 + 1)   # pri 111: the voice of THIS predicate, not of the sentence\n"),
    ("    passive_local = is_passive_clause(toks[lo:hi], pos[lo:hi])\n",
     "    passive_local = is_passive_predicate(toks, pos, v0 + 1)   # pri 111: predicate-anchored, not any passive in the span\n"),
    ('    from hdlab.thematic_role_labeler import is_passive_clause\n'
     '    want = "BY_AGENT" if is_passive_clause(list(toks), list(pos)) else "SUBJ"\n',
     '    from hdlab.thematic_role_labeler import is_passive_predicate\n'
     '    want = "BY_AGENT" if is_passive_predicate(list(toks), list(pos), v0 + 1, heads=heads) else "SUBJ"\n'),
]
# Q1 (phase 7): RETIRE THE BOARD ARM'S DUPLICATE. `hybrid_agent_pick` there is a SECOND implementation of
# hdlab.graded_role_assigner.hybrid_agent_pick that had drifted from it in two LIVE ways -- it read voice
# over the WHOLE SENTENCE with no by-phrase requirement, and it never passed `byhead_agent_cue=True`, so
# the by-phrase CASE cue landed 2026-09-06 had never reached the board. ONE STRUCTURE, ONE ORGAN: it
# becomes a thin call. Measured by the board's OWN board_agent_dimension -- see SOLVED section 17.
_GRA_EDITS.append((_GATE_OLD, _GATE_NEW))   # D4 (phase 7b)
_BOARD_EDITS = [
    ('    failure modes. Returns a head string.' + _Q + '\n'
     '    base_i = _floor_positional_idx(v, cands)\n'
     '    base = toks[base_i] if base_i is not None else None\n'
     '    from hdlab.thematic_role_labeler import is_passive_clause\n'
     '    low_base = str(base).lower() if base is not None else ""\n'
     '    passive = is_passive_clause(toks, up)\n'
     '    pp_gov = base_i is not None and GRA._agent_pp_governed([t.lower() for t in toks], up, base_i)\n'
     '    noncase = low_base in GRA._AGENT_ANIM_PRON and low_base not in GRA.NOMINATIVE_PRON\n'
     '    if passive or pp_gov or noncase:\n'
     '        return GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None,\n'
     '                                          weights=weights, gaz=gaz)\n'
     '    return base                                                  # canonical: word-order default (== positional)\n',
     '    failure modes. Returns a head string.\n'
     '\n'
     '    RETIRED AS A SEPARATE IMPLEMENTATION (pri 111, 2026-09-14) -- this is now a THIN CALL to the ONE\n'
     '    organ. It had drifted from hdlab.graded_role_assigner.hybrid_agent_pick in two ways, both live:\n'
     '    the voice cue was read over the WHOLE SENTENCE with no by-phrase requirement (the organ scopes it\n'
     '    to the predicate being decided and requires the by-phrase), and `byhead_agent_cue` was never\n'
     '    passed, so it defaulted to False and the by-phrase CASE cue landed 2026-09-06 never reached the\n'
     '    board. `cm_cands` stays in the signature for the callers that pass it; the organ competes over the\n'
     '    same list it takes its positional default from, which is what the live reader does\n'
     '    (situation_reader passes one `acand`).' + _Q + '\n'
     '    return GRA.hybrid_agent_pick(toks, up, v - 1, cands, cluster_freq=None, weights=weights, gaz=gaz)\n'),
]
_TRL_DEPRECATE = [
    ('def is_passive_clause(tokens: Sequence[str], pos: Sequence[str], window: int = 3) -> bool:\n'
     '    """BE-aux followed within `window` tokens (allowing an intervening adverb) by a past-participle.\n',
     'def is_passive_clause(tokens: Sequence[str], pos: Sequence[str], window: int = 3) -> bool:\n'
     '    """DEPRECATED (pri 111, 2026-09-14) -- SENTENCE-level, and therefore wrong for every consumer that is\n'
     '    deciding ONE predicate: precision 0.3784 / recall 0.8235 per predicate on UD-EWT test against\n'
     '    `is_passive_predicate`\'s 0.9606 / 0.8971. Kept only for callers that genuinely want "does this sentence\n'
     '    contain a passive anywhere". New code calls `is_passive_predicate`.\n\n'
     '    BE-aux followed within `window` tokens (allowing an intervening adverb) by a past-participle.\n'),
]


def _apply(path, edits, insert_before=None, insert_lines=None):
    with open(path, encoding="utf-8", newline="") as f:
        src = f.read()
    nl = "\r\n" if "\r\n" in src else "\n"

    def fix(s):
        return s.replace("\r\n", "\n").replace("\n", nl)
    out = src
    for old, new in edits:
        old, new = fix(old), fix(new)
        if out.count(old) != 1:
            raise SystemExit("PATCH ANCHOR MISMATCH in %s (%d occurrences):\n%r" % (path, out.count(old), old[:120]))
        out = out.replace(old, new)
    if insert_before is not None:
        insert_before = fix(insert_before)
        if out.count(insert_before) != 1:
            raise SystemExit("PATCH INSERT ANCHOR MISMATCH in %s" % path)
        block = "".join(l.rstrip("\r\n") + nl for l in insert_lines)
        out = out.replace(insert_before, block + nl + insert_before)
    return src, out


def emit_patch(verbose=True):
    import difflib
    block = organ_block()
    pieces = []
    for path, edits, ib, il in (
            (os.path.join(REPO, "hdlab", "thematic_role_labeler.py"), _TRL_DEPRECATE, _TRL_ANCHOR, block),
            (os.path.join(REPO, "hdlab", "graded_role_assigner.py"), _GRA_EDITS, None, None),
            (os.path.join(REPO, "hdlab", "relcl_resolver.py"), _RELCL_EDITS, None, None),
            (os.path.join(REPO, "hdlab", "arc_labeler.py"), _AL_EDITS, None, None),
            (os.path.join(REPO, "experiments", "exp_board_agent_slot_ud_v1.py"), _BOARD_EDITS, None, None)):
        rel = os.path.relpath(path, REPO).replace("\\", "/")
        src, out = _apply(path, edits, ib, il)
        d = difflib.unified_diff(src.splitlines(True), out.splitlines(True),
                                 fromfile="a/" + rel, tofile="b/" + rel, n=3)
        pieces.append("diff --git a/%s b/%s\n" % (rel, rel) + "".join(d))
    os.makedirs(os.path.dirname(PATCH_PATH), exist_ok=True)
    with open(PATCH_PATH, "w", encoding="utf-8", newline="") as f:
        f.write("".join(pieces))
    if verbose:
        print("wrote %s (%d bytes)" % (PATCH_PATH, os.path.getsize(PATCH_PATH)))
    return PATCH_PATH


def patch_matches_cell():
    """The diff's ADDED organ lines are byte-identical to this cell's organ block -- so the arm that was
    measured is the arm that would ship."""
    if not os.path.exists(PATCH_PATH):
        return False, "no patch on disk"
    with open(PATCH_PATH, encoding="utf-8", newline="") as f:
        added = [l[1:] for l in f.read().splitlines(True) if l.startswith("+") and not l.startswith("+++")]
    blk = [l.rstrip("\r\n") for l in organ_block()]
    add = [l.rstrip("\r\n") for l in added]
    for i in range(len(add) - len(blk) + 1):
        if add[i:i + len(blk)] == blk:
            return True, "organ block found verbatim in the diff (%d lines)" % len(blk)
    return False, "organ block NOT byte-identical in the diff"


# =================================================================================================
# 8. EXTRA ARMS -- the criterion sweep, the heads contrast, call site 2, and the adjectival residual.
# =================================================================================================
def arm_extra(n_boot=2000, cap_tr=None, cap_te=None, verbose=True):
    from hdlab.thematic_role_labeler import is_passive_clause
    counts = load_voice_counts()
    out = {}
    # (a) CRITERION SWEEP on TRAIN (never on the evaluation split), then applied unchanged to TEST.
    tr = voice_gold(UD_TRAIN, cap=cap_tr)
    te = voice_gold(UD_TEST, cap=cap_te)
    grid = [0.15, 0.25, 0.35, 0.5, 0.65, 0.75, 0.85]
    sweep = {}
    tr_p = []
    for si, toks, gp, gh, v, raw, prop in tr:
        up, lh = live_chain(toks)
        tr_p.append((voice_posterior(toks, up, v, counts, heads=lh), prop))
    for th in grid:
        tp = sum(1 for p, g in tr_p if p >= th and g)
        fp = sum(1 for p, g in tr_p if p >= th and not g)
        fn = sum(1 for p, g in tr_p if p < th and g)
        P = tp / max(1, tp + fp)
        R = tp / max(1, tp + fn)
        sweep["theta=%.2f" % th] = {"precision": round(P, 4), "recall": round(R, 4),
                                    "f1": round(2 * P * R / max(1e-9, P + R), 4)}
    best = max(grid, key=lambda t: sweep["theta=%.2f" % t]["f1"])
    out["train_criterion_sweep"] = sweep
    out["train_best_theta"] = best
    # (b) HEADS vs NO HEADS -- does the reader's own arc change the DECISION, or only the cue value?
    diff = 0
    same_val = collections.Counter()
    te_rows = []
    for si, toks, gp, gh, v, raw, prop in te:
        up, lh = live_chain(toks)
        a = is_passive_predicate(toks, up, v, heads=lh)
        b = is_passive_predicate(toks, up, v, heads=None)
        diff += int(a != b)
        same_val[voice_cue_value(toks, up, v, lh)] += 1
        te_rows.append((toks, up, lh, v, raw, prop, si))
    out["heads_vs_no_heads"] = {"n": len(te), "decisions_changed_by_the_arc": diff,
                               "cue_values_under_live_heads": dict(same_val)}
    # (c) THE ADJECTIVAL RESIDUAL (checklist item 4): of the remaining false fires, how many carry the
    #     adjectival-participle lexical evidence (a degree modifier)?
    fps = [(toks, up, lh, v) for toks, up, lh, v, raw, prop, si in te_rows
           if is_passive_predicate(toks, up, v, heads=lh) and not prop]
    deg = sum(1 for toks, up, lh, v in fps if degree_value(toks, up, v) == "deg")
    out["adjectival_residual"] = {"false_fires": len(fps), "with_degree_modifier": deg,
                                  "examples": [" ".join(t[max(0, v - 5):v + 3]) for t, u, h, v in fps[:12]]}
    # (c2) UPSTREAM SIGNAL LOSS: the cue can only fire on a token the CATEGORY organ calls a VERB. How many
    #      gold passives does the live tagger hand down as something else -- i.e. lost one rung above this one?
    lost_tag = 0
    lost_examples = []
    for toks, up, lh, v, raw, prop, si in te_rows:
        if prop and (v - 1 >= len(up) or up[v - 1] != "VERB"):
            lost_tag += 1
            if len(lost_examples) < 10:
                lost_examples.append("%s [%s=%s]" % (" ".join(toks[max(0, v - 4):v + 2]), toks[v - 1],
                                                     up[v - 1] if v - 1 < len(up) else "?"))
    out["upstream_category_loss"] = {"gold_passive_predicates": sum(1 for r in te_rows if r[5]),
                                     "not_tagged_VERB_by_the_category_organ": lost_tag,
                                     "examples": lost_examples}
    # (d) CALL SITE 2 -- the competition's own pick with the whole-sentence voice flip vs the predicate read.
    out["call_site_2_agent_supports"] = arm_agent_supports(counts, None, n_boot=n_boot)
    # (e) the shipped detector's own false-fire anatomy on the SAME population, for the record
    ff = sum(1 for toks, up, lh, v, raw, prop, si in te_rows if is_passive_clause(list(toks), list(up)) and not prop)
    out["shipped_false_fires"] = ff
    return out


# =================================================================================================
# 9. THE PUSH -- the cue is now right; WHERE DOES THE SIGNAL GO NEXT? The gold-passive subpopulation.
# =================================================================================================
_ORIG_AGENT_SUPPORTS = None


def _patched_agent_supports(toks, pos, v0, cands, *a, **kw):
    """CALL SITE 2 as the diff ships it. `agent_supports` reads `is_passive_clause(toks, pos)` at line 1584 --
    the ONLY use of that name inside the function -- so binding it to the predicate-anchored answer for THIS
    call is exactly what the patched line computes, with no copy of the body to drift."""
    import hdlab.graded_role_assigner as GRA
    global _ORIG_AGENT_SUPPORTS
    if _ORIG_AGENT_SUPPORTS is None:
        _ORIG_AGENT_SUPPORTS = GRA.agent_supports
    flag = bool(is_passive_predicate(toks, pos, v0 + 1))
    _o = GRA.is_passive_clause
    GRA.is_passive_clause = lambda t, pz, w=3, _f=flag: _f
    try:
        return _ORIG_AGENT_SUPPORTS(toks, pos, v0, cands, *a, **kw)
    finally:
        GRA.is_passive_clause = _o


class _AllCallSites(object):
    """Context manager installing EVERY hdlab call site the diff changes -- call site 2 (agent_supports) and
    call site 3 (agent_override_fires) -- so the arm that is measured is the arm that would ship. Call sites
    1 and 4 are exercised by their own arms (arm_labels / arm_call_sites and agent_override_licensed, which
    is opt-in behind `heads` and OFF here)."""

    def __enter__(self):
        import hdlab.graded_role_assigner as GRA
        global _ORIG_AGENT_SUPPORTS
        if _ORIG_AGENT_SUPPORTS is None:
            _ORIG_AGENT_SUPPORTS = GRA.agent_supports
        self._G = GRA
        self._saved = (GRA.agent_override_fires, GRA.agent_supports)
        GRA.agent_override_fires = _patched_agent_override_fires
        GRA.agent_supports = _patched_agent_supports
        return self

    def __exit__(self, *exc):
        self._G.agent_override_fires, self._G.agent_supports = self._saved
        return False


def _patched_agent_override_fires(toks, pos, v0, cands):
    """hdlab.graded_role_assigner.agent_override_fires WITH the pri-111 line: the voice cue is read at the
    PREDICATE, not as "any passive inside the clause span". Everything else is byte-identical to the organ."""
    import hdlab.graded_role_assigner as GRA
    low = [t.lower() for t in toks]
    lo, hi = GRA.clause_bounds(toks, pos, v0)
    passive_local = is_passive_predicate(toks, pos, v0 + 1)          # <-- the one changed line
    has_by = any(low[i] == "by" for i in range(lo, min(hi, len(low))))
    if passive_local and has_by:
        return True
    base = GRA._positional_agent_base(cands, v0)
    if base is None:
        return False
    bi = base["wtok_start"]
    if GRA._agent_pp_governed(low, pos, bi):
        return True
    bh = str(base["head"]).lower()
    if bh in GRA._AGENT_ANIM_PRON and bh not in GRA.NOMINATIVE_PRON:
        return True
    return False


def arm_push(n_boot=2000, cap=None, verbose=True):
    """Having fixed the cue, trace it one rung DOWN. On the agent population the passive licence can only
    ever touch the gold-PASSIVE items (n=16 of 1423: UD's `obl:agent` by-phrases), so the arithmetic bound on
    the whole lever is 16 items. On THAT subpopulation, which rung loses the signal?

    Arms, each differing in exactly one thing:
      floor            -- nearest pre-verbal nominal (word order)
      board_cm         -- the board arm's competition: agent_competition_pick with byhead_agent_cue=FALSE
                          (its default -- the board arm never passes it, so the by-phrase CASE cue is OFF)
      cm_byhead        -- the SAME competition with byhead_agent_cue=TRUE (what hdlab.hybrid_agent_pick passes)
      organ_hybrid     -- hdlab.graded_role_assigner.hybrid_agent_pick itself (byhead on by default)
      oracle_bygoverned-- pick the candidate GOVERNED BY `by` (the ceiling the case cue could reach)
    """
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    import hdlab.graded_role_assigner as GRA
    import hdlab.frontend as FE

    gaz = load_given_gazetteer()
    sents = load_ud(UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    cache = {}
    rows = []
    t0 = time.time()
    for k, (toks, v, ag, gp) in enumerate(items):
        key = tuple(toks)
        if key not in cache:
            forms = list(toks)
            up, post = FE.tagger().tag_with_posterior(forms)
            po = FE.parser().parse(forms, up, post)
            cache[key] = (list(up), post, dict(po.heads))
        up, post, lh = cache[key]
        cands = AG._clause_local_nominals(toks, up, v, post=post)
        if not cands:
            continue
        cf = [c for c in cands if str(c["head"]).lower() not in GRA._AGENT_ANIM_PRON
              or str(c["head"]).lower() in GRA.NOMINATIVE_PRON]
        cm_cands = cf or cands
        bi = AG._floor_positional_idx(v, cands)
        low = _low(toks)
        picks = {
            "floor": toks[bi] if bi is not None else None,
            "board_cm": GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None, gaz=gaz),
            "cm_byhead": GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None, gaz=gaz,
                                                    byhead_agent_cue=True),
            # the ORGAN as the live reader calls it: ONE candidate list (situation_reader passes `acand`)
            "organ_hybrid": GRA.hybrid_agent_pick(toks, up, v - 1, cands, cluster_freq=None, gaz=gaz),
        }
        # THE SHIPPED ORGAN WITH THE PATCH IN: hybrid_agent_pick calling the PATCHED agent_override_fires
        # (byte-copy of the organ's with the one line the diff changes). Monkeypatched for the call only.
        with _AllCallSites():
            picks["organ_hybrid_patched"] = GRA.hybrid_agent_pick(toks, up, v - 1, cands,
                                                                  cluster_freq=None, gaz=gaz)
        # THE BOARD ARM's own copy of the hybrid -- what the board scores today -- and the same copy with the
        # one line the diff changes (its voice read). The board arm is a SEPARATE implementation from the organ.
        picks["board_hybrid"] = AG.hybrid_agent_pick(toks, up, v, cands, cm_cands, gaz)
        _ = None
        _bi = AG._floor_positional_idx(v, cands)
        _base = toks[_bi] if _bi is not None else None
        _lb = str(_base).lower() if _base is not None else ""
        _pv = is_passive_predicate(toks, up, v)
        _pp = _bi is not None and GRA._agent_pp_governed(low, up, _bi)
        _nc = _lb in GRA._AGENT_ANIM_PRON and _lb not in GRA.NOMINATIVE_PRON
        picks["board_hybrid_patched"] = (GRA.agent_competition_pick(toks, up, v - 1, cm_cands,
                                                                    cluster_freq=None, gaz=gaz)
                                         if (_pv or _pp or _nc) else _base)
        # DECOMPOSITION (phase 7, 1c): the SAME board arm with the corrected voice read AND the byhead
        # by-phrase CASE cue the board arm never passes -- isolates difference (B) from difference (A).
        picks["board_hybrid_patched_byhead"] = (GRA.agent_competition_pick(toks, up, v - 1, cm_cands,
                                                                           cluster_freq=None, gaz=gaz,
                                                                           byhead_agent_cue=True)
                                                if (_pv or _pp or _nc) else _base)
        # and the by-phrase REQUIREMENT on top (difference A''), which is what the organ's override adds
        _byloc = by_value(toks, up, v, lh) == "by"
        picks["board_hybrid_patched_byhead_byreq"] = (
            GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None, gaz=gaz,
                                       byhead_agent_cue=True)
            if ((_pv and _byloc) or _pp or _nc) else _base)
        # THE GATE THE ORACLE SEES: the head of the by-NP is the LAST noun of the nominal group, except a
        # flat NAME, which UD heads on its FIRST token (measured bound only -- not shipped, see SOLVED 16b).
        _by = [c for c in cands if GRA.by_governs(low, up, c["wtok_start"])]
        if _by:
            _names = [c for c in _by if (up[c["wtok_start"]] if c["wtok_start"] < len(up) else None) == "PROPN"]
            picks["oracle_by_nphead"] = (_names[0]["head"] if _names
                                         else max(_by, key=lambda c: c["wtok_start"])["head"])
        else:
            picks["oracle_by_nphead"] = picks["floor"]
        byg = [c for c in cands if GRA.by_governs(low, up, c["wtok_start"])]
        picks["oracle_bygoverned"] = byg[0]["head"] if byg else picks["floor"]
        rows.append({"gold": toks[ag - 1], "gp": bool(gp), "picks": picks,
                     "voice_new": bool(is_passive_predicate(toks, up, v, heads=lh)),
                     "bypp_gate": bool(GRA.participle_bypp_gate(toks, up, v - 1))})
        if verbose and k and k % 500 == 0:
            print("   [push] %d/%d %.0fs" % (k, len(items), time.time() - t0), flush=True)
    names = ["floor", "board_cm", "cm_byhead", "board_hybrid", "board_hybrid_patched",
             "board_hybrid_patched_byhead", "board_hybrid_patched_byhead_byreq",
             "organ_hybrid", "organ_hybrid_patched", "oracle_bygoverned", "oracle_by_nphead"]
    out = {"n": len(rows), "n_gold_passive": sum(int(r["gp"]) for r in rows)}
    for pop, sel in (("gold_passive_only", lambda r: r["gp"]), ("full", lambda r: True),
                     ("active_only", lambda r: not r["gp"])):
        sub = [r for r in rows if sel(r)]
        acc = {nm: np.asarray([int(_match(r["picks"][nm], r["gold"])) for r in sub], dtype=float) for nm in names}
        out[pop] = {"n": len(sub), "accuracy": {nm: round(float(acc[nm].mean()), 4) for nm in names},
                    "vs_floor": {nm: paired_boot(acc["floor"], acc[nm], n_boot=n_boot)
                                 for nm in names if nm != "floor"},
                    "vs_board_hybrid": {nm: paired_boot(acc["board_hybrid"], acc[nm], n_boot=n_boot)
                                        for nm in ("board_hybrid_patched", "organ_hybrid", "organ_hybrid_patched")},
                    "patched_vs_unpatched": {
                        "organ": paired_boot(acc["organ_hybrid"], acc["organ_hybrid_patched"], n_boot=n_boot),
                        "board": paired_boot(acc["board_hybrid"], acc["board_hybrid_patched"], n_boot=n_boot)}}
    # THE VOICE CUE'S OWN RECALL AT THIS CONSUMER: does the fixed cue fire on the gold-passive items?
    gp_rows = [r for r in rows if r["gp"]]
    out["voice_cue_on_gold_passive"] = {"n": len(gp_rows),
                                        "cue_fires": sum(int(r["voice_new"]) for r in gp_rows),
                                        "bypp_gate_fires": sum(int(r["bypp_gate"]) for r in gp_rows)}
    return out


# =================================================================================================
# 10. GENERALIZE -- a SECOND modern gold the counts never saw: GUM (multi-genre) and GENTLE (OOD).
# =================================================================================================
def arm_gum(n_boot=2000, cap=None, verbose=True):
    """The detector on GUM, whose UD deprels give the same voice gold. The count asset was accrued on UD-EWT
    TRAIN only, so GUM is held out entirely and GENTLE (the deliberately out-of-domain companion) doubly so."""
    from hdlab.thematic_role_labeler import is_passive_clause
    from hdlab.relcl_resolver import precise_passive
    gd = os.path.join(REPO, "data", "corpora", "gum", "conllu")
    counts = load_voice_counts()
    files = sorted(os.listdir(gd))
    out = {}
    for split, sel in (("gum", lambda f: not f.startswith("GENTLE")),
                       ("gentle_ood", lambda f: f.startswith("GENTLE"))):
        fs = [f for f in files if sel(f) and f.endswith(".conllu")]
        if cap:
            fs = fs[:cap]
        rows = []
        for fi, f in enumerate(fs):
            for r in voice_gold(os.path.join(gd, f)):
                rows.append((fi * 100000 + r[0],) + tuple(r[1:]))   # cluster id UNIQUE across files
        rng = random.Random(SEED)
        names = ["floor_whole_sentence", "floor_precise_passive", "new_construction", "new_graded",
                 "new_no_conj", "new_no_contraction", "twin_random"]
        arms = {nm: [] for nm in names}
        gold, groups = [], []
        fpv = collections.Counter(); ffp = collections.Counter()
        t0 = time.time()
        for k, (si, toks, gp, gh, v, raw, prop) in enumerate(rows):
            up, lh = live_chain(toks)
            gold.append(int(prop))
            groups.append(si)
            arms["floor_whole_sentence"].append(int(is_passive_clause(list(toks), list(up))))
            arms["floor_precise_passive"].append(int(precise_passive(list(toks), list(up), v)))
            arms["new_construction"].append(int(is_passive_predicate(toks, up, v, heads=lh)))
            arms["new_graded"].append(int(is_passive_predicate(toks, up, v, heads=lh, counts=counts)))
            arms["new_no_conj"].append(int(is_passive_predicate(toks, up, v, heads=lh, use_conj=False)))
            # CONTRACTION ARM: 's/'re/'m are ambiguous between BE and HAVE ("he's finished" = perfect OR
            # passive). Drop them from the auxiliary inventory and see what the precision does.
            _cv = voice_cue_value(toks, up, v, lh)
            _j = None
            _c = _aux_chain_left(toks, up, v)
            if _c is not None:
                _j = _c[1]
            arms["new_no_contraction"].append(int(_cv in PASSIVE_VALUES and not (
                _j is not None and toks[_j - 1].lower() in ("'s", "'re", "'m", "s", "re", "m"))))
            fpv[(_cv, int(prop))] += 1
            if _cv in PASSIVE_VALUES and not prop:
                ffp[_cv] += 1
            if verbose and k and k % 5000 == 0:
                print("   [%s] %d/%d %.0fs" % (split, k, len(rows), time.time() - t0), flush=True)
        rate = sum(arms["new_construction"]) / max(1, len(rows))
        arms["twin_random"] = [int(rng.random() < rate) for _ in rows]
        base = np.asarray([int(bool(x) == bool(y)) for x, y in zip(arms["floor_whole_sentence"], gold)], dtype=float)
        out[split] = {"n_predicates": len(rows), "n_gold_passive": sum(gold), "n_files": len(fs),
                      "false_fires_by_cue_value": dict(ffp),
                      "cue_value_by_gold": {"%s|%d" % k: v for k, v in fpv.items()},
                      "prf": {nm: prf(arms[nm], gold) for nm in names},
                      "vs_floor": {nm: paired_boot(base, np.asarray(
                          [int(bool(x) == bool(y)) for x, y in zip(arms[nm], gold)], dtype=float), n_boot=n_boot)
                          for nm in names}}
    return out


# =================================================================================================
# 11. THE BOARD ROW ITSELF -- exp_board_agent_slot_ud_v1.board_agent_dimension, run twice.
# =================================================================================================
def _patched_board_hybrid(toks, up, v, cands, cm_cands, gaz, weights=None):
    """experiments.exp_board_agent_slot_ud_v1.hybrid_agent_pick with the ONE line the diff changes."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    import hdlab.graded_role_assigner as GRA
    base_i = AG._floor_positional_idx(v, cands)
    base = toks[base_i] if base_i is not None else None
    low_base = str(base).lower() if base is not None else ""
    passive = is_passive_predicate(toks, up, v)                       # <-- the one changed line
    pp_gov = base_i is not None and GRA._agent_pp_governed([t.lower() for t in toks], up, base_i)
    noncase = low_base in GRA._AGENT_ANIM_PRON and low_base not in GRA.NOMINATIVE_PRON
    if passive or pp_gov or noncase:
        with _AllCallSites():                       # call site 2 is in the diff as well
            return GRA.agent_competition_pick(toks, up, v - 1, cm_cands, cluster_freq=None,
                                              weights=weights, gaz=gaz)
    return base


def _organ_board_hybrid(toks, up, v, cands, cm_cands, gaz, weights=None):
    """The board arm REPLACED by the ORGAN (hdlab.graded_role_assigner.hybrid_agent_pick), which requires the
    by-phrase for the passive licence and passes the byhead by-phrase CASE cue -- with the pri-111 voice read."""
    import hdlab.graded_role_assigner as GRA
    with _AllCallSites():
        return GRA.hybrid_agent_pick(toks, up, v - 1, cands, cluster_freq=None, weights=weights, gaz=gaz)


def arm_board_dimension(n_boot=2000, cap=None):
    """The board's who_did_what_agent ROW, computed by the board's own function, under three arms."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    orig = AG.hybrid_agent_pick
    out = {}
    try:
        for name, fn in (("landed", orig), ("pri111_voice", _patched_board_hybrid),
                         ("pri111_voice_plus_organ", _organ_board_hybrid)):
            AG.hybrid_agent_pick = fn
            row, detail = AG.board_agent_dimension(cap=cap, n_boot=n_boot)
            out[name] = {"row": row, "by_voice": detail["by_voice"],
                         "full_cm_agent": detail["full_cm_agent"]}
            print("  %-24s model %.4f floor %.4f twin %.4f  model-floor %s sep=%s | passive n=%d hyb %.4f"
                  % (name, row["model_acc"], row["strongest_floor"], row["twin_acc"],
                     row["model_minus_strongest"], row["ci_sep_over_strongest"],
                     detail["by_voice"]["passive"]["n"], detail["by_voice"]["passive"]["hybrid"]), flush=True)
    finally:
        AG.hybrid_agent_pick = orig
    return out


# =================================================================================================
# 12. PHASE 7 (Q2) -- RE-ACCRUE THE CUE VALIDITIES WITH THE CORRECTED `voice_order` CUE.
#     The live v4 table was fitted with the OLD detector, so the no-regress number in section 5.5 is the
#     as-if-landed-today number. The table's own builder is REUSED (never edited, never written over): its
#     OUT constant is redirected into data/hook_state/ and `graded_role_assigner.coarse_role_cues` is
#     substituted for the run. TWO tables are built on the CURRENT chain -- one with the shipped cue and one
#     with the corrected cue -- so the comparison isolates the cue and not the upstream landing at 13:10.
# =================================================================================================
HOOK_DIR = os.path.join(REPO, "data", "hook_state")
_ORIG_COARSE_CUES = None


def patched_coarse_role_cues(toks, pos, heads, i, frames=None, v3=False, conf=None, v4=False):
    """`graded_role_assigner.coarse_role_cues` with the pri-111 line: the voice cue is read at the PREDICATE
    that governs this nominal, not over the whole sentence. Byte-identical everywhere else."""
    import hdlab.graded_role_assigner as GRA
    cues = _ORIG_COARSE_CUES(toks, pos, heads, i, frames, v3, conf, v4)
    h = heads.get(i, 0) or 0
    hc = GRA._head_class(pos, h, v3)
    if hc in ("VERB", "AUX") and h:
        vc = GRA.voice_cues(toks, pos, h)
        strong = bool(vc["vc_strong"] or vc["vc_get"] or vc["vc_being"])
        weak = bool(vc["vc_bypp"] or is_passive_predicate(toks, pos, h, heads=heads))
        order = "pre" if (h and i < h) else ("post" if h else "root")
        cues["voice_order"] = ("passive_strong_" if strong else ("passive_weak_" if weak else "active_")) + order
        if cues.get("prep") in ("by", "by_passive"):
            cues["prep"] = "by_passive" if (strong or weak) else "by"
    return cues


def reaccrue(which="patched", verbose=True):
    """Rebuild the coarse-role validity table with the builder's OWN math, into data/hook_state/."""
    global _ORIG_COARSE_CUES
    import importlib.util
    import hdlab.graded_role_assigner as GRA
    _bp = os.path.join(REPO, "tools", "build_coarse_role_validities.py")
    _spec = importlib.util.spec_from_file_location("_bcrv_pri111", _bp)
    BC = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(BC)                    # the builder is READ and REUSED, never edited
    if _ORIG_COARSE_CUES is None:
        _ORIG_COARSE_CUES = GRA.coarse_role_cues
    os.makedirs(HOOK_DIR, exist_ok=True)
    BC.OUT = os.path.join(HOOK_DIR, "coarse_role_validities_pri111_%s.json" % which)
    argv = list(sys.argv)
    sys.argv = ["build", "--perceived", "--weight", "--v4"]
    if which == "patched":
        GRA.coarse_role_cues = patched_coarse_role_cues
    try:
        t0 = time.time()
        BC.main()
        if verbose:
            print("   [reaccrue:%s] %.0fs" % (which, time.time() - t0), flush=True)
    finally:
        GRA.coarse_role_cues = _ORIG_COARSE_CUES
        sys.argv = argv
    return BC.OUT.replace(".json", "_perceived_w_v4.json")


def arm_labels(n_boot=2000, cap=700, verbose=True):
    """THE LABELS RUNG on UD-EWT test: all-nominal role accuracy and the voice-bearing classes, under
    (a) the LIVE table with the shipped cue, (b) the LIVE table with the corrected cue (= section 5.5),
    (c) the RE-ACCRUED tables (shipped-cue and corrected-cue) with the corrected cue."""
    global _ORIG_COARSE_CUES
    import hdlab.graded_role_assigner as GRA
    if _ORIG_COARSE_CUES is None:
        _ORIG_COARSE_CUES = GRA.coarse_role_cues
    live = GRA.load_coarse_validities()
    arms = collections.OrderedDict()
    arms["live_table_shipped_cue"] = (live, _ORIG_COARSE_CUES)
    arms["live_table_corrected_cue"] = (live, patched_coarse_role_cues)
    for which in ("shipped", "patched"):
        p = os.path.join(HOOK_DIR, "coarse_role_validities_pri111_%s_perceived_w_v4.json" % which)
        if os.path.exists(p):
            arms["reaccrued_%s_cue_table" % which] = (GRA.load_coarse_validities(p),
                                                      _ORIG_COARSE_CUES if which == "shipped"
                                                      else patched_coarse_role_cues)
    rows = []
    for si, (toks, gpos, gheads, deps) in enumerate(conllu(UD_TEST)):
        if cap and si >= cap:
            break
        rows.append((si, toks, deps))
    names = list(arms)
    preds = {k: [] for k in names}
    t0 = time.time()
    for k, (si, toks, deps) in enumerate(rows):
        up, lh = live_chain(toks)
        for nm in names:
            tab, fn = arms[nm]
            GRA.coarse_role_cues = fn
            try:
                preds[nm].append(GRA.coarse_roles(list(toks), list(up), dict(lh), tab))
            finally:
                GRA.coarse_role_cues = _ORIG_COARSE_CUES
        if verbose and k and k % 200 == 0:
            print("   [labels] %d/%d %.0fs" % (k, len(rows), time.time() - t0), flush=True)
    pops = {"all_nominals": [], "core": [], "PASS_SUBJ_nsubj_pass": [], "BY_AGENT_obl_agent": [],
            "SUBJ_nsubj_active": [], "OBJ_obj": []}
    for k, (si, toks, deps) in enumerate(rows):
        for i in range(1, len(toks) + 1):
            g = deps.get(i, "")
            gb = g.split(":")[0]
            if gb not in ("nsubj", "obj", "iobj", "obl", "nmod"):
                continue
            hit = tuple(int(_deps_match(preds[nm][k].get(i), g)) for nm in names) + (si,)
            pops["all_nominals"].append(hit)
            if gb in ("nsubj", "obj", "iobj"):
                pops["core"].append(hit)
            if g.startswith("nsubj:pass"):
                pops["PASS_SUBJ_nsubj_pass"].append(hit)
            elif gb == "nsubj":
                pops["SUBJ_nsubj_active"].append(hit)
            if g.startswith("obl:agent"):
                pops["BY_AGENT_obl_agent"].append(hit)
            if gb == "obj":
                pops["OBJ_obj"].append(hit)
    out = {"arms": names, "n_sentences": len(rows)}
    for pop, lst in pops.items():
        if not lst:
            out[pop] = {"n": 0}
            continue
        vecs = {nm: np.asarray([x[j] for x in lst], dtype=float) for j, nm in enumerate(names)}
        g = [x[-1] for x in lst]
        base = vecs[names[0]]
        out[pop] = {"n": len(lst), "accuracy": {nm: round(float(v.mean()), 4) for nm, v in vecs.items()},
                    "vs_live_shipped": {nm: paired_boot(base, vecs[nm], groups=g, n_boot=n_boot)
                                        for nm in names[1:]}}
    return out


# =================================================================================================
# 13. PHASE 7 (Q3) -- THE SIX VOICE DETECTORS AND THEIR CONSUMERS, each measured with the ONE organ in.
# =================================================================================================
VOICE_DETECTORS = [
    ("D1 is_passive_clause", "hdlab/thematic_role_labeler.py:428",
     ["hdlab/graded_role_assigner.py:659 coarse_role_cues", "hdlab/graded_role_assigner.py:1584 agent_supports",
      "hdlab/graded_role_assigner.py:1765 agent_override_fires",
      "hdlab/graded_role_assigner.py:1874 agent_override_licensed",
      "experiments/exp_board_agent_slot_ud_v1.py:149 hybrid_agent_pick"]),
    ("D2 precise_passive", "hdlab/relcl_resolver.py:58",
     ["hdlab/relcl_resolver.py:72 two_line_patient", "hdlab/relcl_resolver.py:134 resolve_patient",
      "hdlab/graded_role_assigner.py:197 hybrid_role_patient", "hdlab/predicate_argument_frontend.py:454",
      "hdlab/predicate_argument_frontend.py:710", "hdlab/situation_reader.py:2294 patient confidence",
      "experiments/exp_valency_labeled_patient_v1.py:229 (the BOARD patient arm)"]),
    ("D3 voice_cues / robust_passive", "hdlab/graded_role_assigner.py:78 / :99",
     ["hdlab/graded_role_assigner.py:658 coarse_role_cues (strong/get/being)",
      "hdlab/graded_role_assigner.py:154 cue_supports (passive_strong / passive_weak)",
      "hdlab/verb_subcat.py:95", "hdlab/situation_reader.py:1549 structural_patient_pick",
      "experiments/exp_valency_labeled_patient_v1.py:69 the DEPLOYED FLOOR"]),
    ("D4 participle_bypp_gate", "hdlab/graded_role_assigner.py:1473",
     ["hdlab/graded_role_assigner.py:1754 agent_supports (the byhead CASE cue's gate)"]),
    ("D5 label_voice_correct", "hdlab/arc_labeler.py:59",
     ["hdlab/arc_labeler.py label() with VOICE_CORRECTION=True -> every label consumer"]),
    ("D6 predicate_argument_frontend", "hdlab/predicate_argument_frontend.py:454,710",
     ["delegates to D2 -- not an independent computation"]),
]


def _patched_participle_bypp_gate(toks, pos, v0):
    """`participle_bypp_gate` with the pri-111 voice read in place of the `_is_participle` suffix test."""
    import hdlab.graded_role_assigner as GRA
    if not (0 <= v0 < len(toks)):
        return False
    if not is_passive_predicate(toks, pos, v0 + 1):
        return False
    low = [t.lower() for t in toks]
    return any(GRA.by_governs(low, pos, i) for i in range(len(toks))
               if (pos[i] if i < len(pos) else None) in GRA._BYHEAD_NOM)


def arm_detectors(n_boot=2000, cap=None, verbose=True):
    out = {"inventory": [{"detector": d, "site": f, "consumers": c} for d, f, c in VOICE_DETECTORS]}

    # ---- D2: the BOARD's who_did_what_patient row, computed by the board's own function, with
    #      relcl_resolver.precise_passive substituted by the organ (the R_final voice input).
    import experiments.exp_valency_labeled_patient_v1 as VLP
    import experiments.exp_board_patient_slot_v1 as BP
    orig_pp = VLP.precise_passive
    d2 = {}
    for nm, fn in (("landed_precise_passive", orig_pp),
                   ("one_organ_is_passive_predicate", lambda t, pz, v: is_passive_predicate(t, pz, v))):
        VLP.precise_passive = fn
        try:
            row, det = BP.board_patient_dimension(cap=cap)
            d2[nm] = {"model_acc": row["model_acc"], "floor": row["strongest_floor"], "twin": row["twin_acc"],
                      "model_minus_floor": row["model_minus_strongest"], "n": row["n"],
                      "ceiling_gold_parse": det["ceiling_gold_parse"]}
            if verbose:
                print("  [D2 patient board] %-32s model %.4f floor %.4f twin %.4f  m-f %s"
                      % (nm, row["model_acc"], row["strongest_floor"], row["twin_acc"],
                         row["model_minus_strongest"]), flush=True)
        finally:
            VLP.precise_passive = orig_pp
    out["D2_patient_board"] = d2

    # ---- D4: the byhead CASE cue's gate, on the agent population's gold-PASSIVE slice.
    import experiments.exp_board_agent_slot_ud_v1 as AG
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    import hdlab.graded_role_assigner as GRA
    import hdlab.frontend as FE
    gaz = load_given_gazetteer()
    sents = load_ud(UD_TEST)
    if cap:
        sents = sents[:cap]
    items = AG.gold_agent_items(sents)
    orig_gate = GRA.participle_bypp_gate
    d4 = {}
    cache = {}
    for nm, gate in (("landed_participle_suffix_gate", orig_gate),
                     ("one_organ_voice_gate", _patched_participle_bypp_gate)):
        hits, gp_hits, fires = [], [], 0
        GRA.participle_bypp_gate = gate
        _cs = _AllCallSites(); _cs.__enter__()
        try:
            for toks, v, ag, gp in items:
                key = tuple(toks)
                if key not in cache:
                    up, post = FE.tagger().tag_with_posterior(list(toks))
                    po = FE.parser().parse(list(toks), up, post)
                    cache[key] = (list(up), post, dict(po.heads))
                up, post, lh = cache[key]
                cands = AG._clause_local_nominals(toks, up, v, post=post)
                if not cands:
                    continue
                pick = GRA.hybrid_agent_pick(toks, up, v - 1, cands, cluster_freq=None, gaz=gaz)
                ok = int(_match(pick, toks[ag - 1]))
                hits.append(ok)
                fires += int(bool(gate(toks, up, v - 1)))
                if gp:
                    gp_hits.append(ok)
        finally:
            _cs.__exit__()
            GRA.participle_bypp_gate = orig_gate
        d4[nm] = {"n": len(hits), "full": round(float(np.mean(hits)), 4),
                  "gold_passive_n": len(gp_hits), "gold_passive": round(float(np.mean(gp_hits)), 4),
                  "gate_fires": fires}
        if verbose:
            print("  [D4 byhead gate] %-30s full %.4f  gold-passive %.4f (n=%d)  gate fires %d"
                  % (nm, d4[nm]["full"], d4[nm]["gold_passive"], d4[nm]["gold_passive_n"], fires), flush=True)
    out["D4_byhead_gate"] = d4

    # ---- D5: does arc_labeler's own voice correction still change anything with COMPETITION_ROLES on?
    import hdlab.arc_labeler as AL
    import hdlab.causation_typing as CT
    changed_raw = changed_live = n_tok = 0
    lab = AL.ArcLabeler.load(CT._LAB_ASSET)
    rows = []
    for si, (toks, gpos, gheads, deps) in enumerate(conllu(UD_TEST)):
        if si >= (cap or 700):
            break
        rows.append((toks, deps))
    for toks, deps in rows:
        up, lh = live_chain(toks)
        try:
            base = lab.label(list(toks), list(up), dict(lh), voice_correction=False, competition_roles=False)
            vc = lab.label(list(toks), list(up), dict(lh), voice_correction=True, competition_roles=False)
            live_off = lab.label(list(toks), list(up), dict(lh), voice_correction=False, competition_roles=True)
            live_on = lab.label(list(toks), list(up), dict(lh), voice_correction=True, competition_roles=True)
        except Exception as e:                                        # pragma: no cover
            out["D5_error"] = repr(e)[:200]
            break
        n_tok += len(toks)
        changed_raw += sum(1 for i in base if base.get(i) != vc.get(i))
        changed_live += sum(1 for i in live_off if live_off.get(i) != live_on.get(i))
    out["D5_arc_labeler_voice_correction"] = {
        "tokens": n_tok, "labels_changed_without_competition_roles": changed_raw,
        "labels_changed_WITH_competition_roles_live": changed_live}
    if verbose:
        print("  [D5 arc labeler] voice correction changes %d labels alone, %d with COMPETITION_ROLES live"
              % (changed_raw, changed_live), flush=True)
    return out


# =================================================================================================
# 14. PHASE 7b -- FOLD D2 + D4 ONTO THE ONE ORGAN AND DELETE D5. One structure, many consumers.
# =================================================================================================
class _Folded(object):
    """Install the fold at EVERY binding the diff changes, so the measured arm is the shipped arm.

    D2 `precise_passive` becomes a thin delegate to `is_passive_predicate`. Because three modules did
    `from hdlab.relcl_resolver import precise_passive` at import time, the delegate must be installed on each
    of those module objects as well as on `relcl_resolver` itself -- exactly the set of names the diff edits.
    D4 `participle_bypp_gate` reads the organ's voice instead of the `_is_participle` suffix test.
    D5 `label_voice_correct` is DELETED; `VOICE_CORRECTION = False` is the behavioural equivalent for a
    measurement that may not edit hdlab/.
    """

    def __init__(self, d2=True, d4=True, d5=True, call_sites=True):
        self.d2, self.d4, self.d5, self.cs = d2, d4, d5, call_sites

    def __enter__(self):
        import hdlab.relcl_resolver as RR
        import hdlab.graded_role_assigner as GRA
        import hdlab.predicate_argument_frontend as PAF
        import hdlab.arc_labeler as AL
        self._mods = (RR, GRA, PAF, AL)
        self._saved = {}
        if self.d2:
            dele = (lambda toks, pos, v: bool(is_passive_predicate(toks, pos, v)))
            for m in (RR, GRA, PAF):
                self._saved[(m, "precise_passive")] = m.precise_passive
                m.precise_passive = dele
            try:
                import experiments.exp_valency_labeled_patient_v1 as VLP
                self._saved[(VLP, "precise_passive")] = VLP.precise_passive
                VLP.precise_passive = dele
                self._mods = self._mods + (VLP,)
            except Exception:
                pass
        if self.d4:
            self._saved[(GRA, "participle_bypp_gate")] = GRA.participle_bypp_gate
            GRA.participle_bypp_gate = _patched_participle_bypp_gate
        if self.d5:
            self._saved[(AL, "VOICE_CORRECTION")] = AL.VOICE_CORRECTION
            AL.VOICE_CORRECTION = False
        self._cs = _AllCallSites() if self.cs else None
        if self._cs:
            self._cs.__enter__()
        return self

    def __exit__(self, *exc):
        if self._cs:
            self._cs.__exit__()
        for (m, name), val in self._saved.items():
            setattr(m, name, val)
        return False


def arm_fold(n_boot=2000, cap=None, verbose=True):
    """Every consumer of D2 / D4 / D5, measured with the fold OFF and ON, in one run."""
    import experiments.exp_board_agent_slot_ud_v1 as AG
    import experiments.exp_board_patient_slot_v1 as BP
    import hdlab.graded_role_assigner as GRA
    out = {}

    # ---- the BOARD's who_did_what_PATIENT row (D2's biggest consumer), by the board's own function
    d = {}
    for nm, fold in (("landed", None), ("D2+D4+D5 folded", _Folded())):
        if fold is None:
            row, det = BP.board_patient_dimension(cap=cap)
        else:
            with fold:
                row, det = BP.board_patient_dimension(cap=cap)
        d[nm] = {"n": row["n"], "model": row["model_acc"], "floor": row["strongest_floor"],
                 "twin": row["twin_acc"], "model_minus_floor": row["model_minus_strongest"],
                 "ceiling_gold_parse": det["ceiling_gold_parse"]}
        if verbose:
            print("  [patient board] %-18s model %.4f floor %.4f twin %.4f  m-f %s ceil %.4f"
                  % (nm, row["model_acc"], row["strongest_floor"], row["twin_acc"],
                     row["model_minus_strongest"], det["ceiling_gold_parse"]), flush=True)
    out["patient_board"] = d

    # ---- the BOARD's who_did_what_AGENT row (D4's consumer + this brief's own)
    orig_hy = AG.hybrid_agent_pick
    d = {}
    try:
        for nm, fn, fold in (("landed", orig_hy, None),
                             ("pri111 voice + organ (7a)", _organ_board_hybrid, None),
                             ("+ D2+D4+D5 folded", _organ_board_hybrid, _Folded())):
            AG.hybrid_agent_pick = fn
            if fold is None:
                row, det = AG.board_agent_dimension(cap=cap, n_boot=n_boot)
            else:
                with fold:
                    row, det = AG.board_agent_dimension(cap=cap, n_boot=n_boot)
            d[nm] = {"model": row["model_acc"], "floor": row["strongest_floor"], "twin": row["twin_acc"],
                     "model_minus_floor": row["model_minus_strongest"],
                     "ci_sep": row["ci_sep_over_strongest"],
                     "passive": det["by_voice"]["passive"], "active": det["by_voice"]["active"]}
            if verbose:
                print("  [agent board]   %-26s model %.4f  m-f %s sep=%s | passive %.4f active %.4f"
                      % (nm, row["model_acc"], row["model_minus_strongest"], row["ci_sep_over_strongest"],
                         det["by_voice"]["passive"]["hybrid"], det["by_voice"]["active"]["hybrid"]), flush=True)
    finally:
        AG.hybrid_agent_pick = orig_hy
    out["agent_board"] = d

    # ---- the LABELS rung (D5's consumer: every label consumer reads arc_labeler.label)
    tab = GRA.load_coarse_validities()
    rows = []
    for si, (toks, gpos, gheads, deps) in enumerate(conllu(UD_TEST)):
        if si >= (cap or 700):
            break
        rows.append((si, toks, deps))
    import hdlab.arc_labeler as AL
    import hdlab.causation_typing as CT
    lab = AL.ArcLabeler.load(CT._LAB_ASSET)
    pops = {"all_nominals": [], "PASS_SUBJ_nsubj_pass": [], "BY_AGENT_obl_agent": []}
    for si, toks, deps in rows:
        up, lh = live_chain(toks)
        a = lab.label(list(toks), list(up), dict(lh))
        with _Folded():
            b = lab.label(list(toks), list(up), dict(lh))
        for i in range(1, len(toks) + 1):
            g = deps.get(i, "")
            gb = g.split(":")[0]
            if gb not in ("nsubj", "obj", "iobj", "obl", "nmod"):
                continue
            hit = (int(_deps_match(a.get(i), g)), int(_deps_match(b.get(i), g)), si)
            pops["all_nominals"].append(hit)
            if g.startswith("nsubj:pass"):
                pops["PASS_SUBJ_nsubj_pass"].append(hit)
            if g.startswith("obl:agent"):
                pops["BY_AGENT_obl_agent"].append(hit)
    lab_out = {}
    for pop, lst in pops.items():
        if not lst:
            lab_out[pop] = {"n": 0}
            continue
        A = np.asarray([x[0] for x in lst], dtype=float)
        B = np.asarray([x[1] for x in lst], dtype=float)
        lab_out[pop] = {"n": len(lst), "landed": round(float(A.mean()), 4), "folded": round(float(B.mean()), 4),
                        "delta": paired_boot(A, B, groups=[x[2] for x in lst], n_boot=n_boot)}
        if verbose:
            print("  [arc labels]    %-22s n %5d  landed %.4f -> folded %.4f  %+0.4f CI%s"
                  % (pop, len(lst), lab_out[pop]["landed"], lab_out[pop]["folded"],
                     lab_out[pop]["delta"]["delta"], lab_out[pop]["delta"]["ci95"]), flush=True)
    out["arc_labeler_labels"] = lab_out
    return out


WITNESSES = [
    "verification/test_coarse_role_competition.py",
    "verification/test_arc_labeler_fastpath_hdlab_landing.py",
    "verification/test_byhead_agent_cue_landing.py",
    "verification/test_labeled_patient_landing.py",
    "verification/test_modern_board_landing.py",
    "verification/test_noncanonical_agent_bymorph_organ.py",
    "verification/test_noncanonical_role_assigner.py",
    "verification/test_precision_defer_landing.py",
    "verification/test_valency_labeled_patient_landing_organ.py",
]


def arm_witnesses(verbose=True):
    """Run every shipped witness that names one of the folded detectors, with the fold OFF then ON, in
    process (hdlab/ is never written). Reports the exit code and the tail of the output for each."""
    import contextlib
    import importlib.util
    out = {}
    for rel in WITNESSES:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            out[rel] = {"missing": True}
            continue
        res = {}
        for nm, fold in (("landed", False), ("folded", True)):
            buf = io.StringIO() if False else None
            import io as _io
            buf = _io.StringIO()
            code = 0
            try:
                spec = importlib.util.spec_from_file_location("_w_" + os.path.basename(rel)[:-3] + "_" + nm, path)
                mod = importlib.util.module_from_spec(spec)
                argv = list(sys.argv)
                sys.argv = [path]
                ctx = _Folded() if fold else None
                if ctx:
                    ctx.__enter__()
                try:
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "main"):
                            r = mod.main()
                            code = int(r) if isinstance(r, int) else 0
                except SystemExit as e:
                    code = int(e.code or 0)
                except Exception as e:                                  # pragma: no cover
                    code = 99
                    buf.write("\nEXCEPTION: %r" % (e,))
                finally:
                    if ctx:
                        ctx.__exit__()
                    sys.argv = argv
            except Exception as e:                                      # pragma: no cover
                code = 98
                buf.write("\nLOAD ERROR: %r" % (e,))
            txt = buf.getvalue()
            fails = [l for l in txt.splitlines() if l.strip().startswith("FAIL") or " FAIL" in l
                     or "AssertionError" in l]
            res[nm] = {"exit": code, "n_fail_lines": len(fails), "fails": fails[:6],
                       "tail": [l for l in txt.splitlines() if l.strip()][-3:]}
        res["verdict"] = ("GREEN both" if res["landed"]["exit"] == 0 == res["folded"]["exit"]
                          else ("RED after the fold" if res["landed"]["exit"] == 0 else
                                ("RED before AND after" if res["folded"]["exit"] else "GREEN after (was red)")))
        out[rel] = res
        if verbose:
            print("  %-56s landed exit %-3d folded exit %-3d  %s"
                  % (rel.split("/")[-1], res["landed"]["exit"], res["folded"]["exit"], res["verdict"]), flush=True)
            for l in res["folded"]["fails"]:
                print("        FOLDED:", l.strip()[:150], flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--extra", action="store_true")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--gum", action="store_true")
    ap.add_argument("--board-dim", action="store_true")
    ap.add_argument("--reaccrue", type=str, default=None, choices=["shipped", "patched", "both"])
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--detectors", action="store_true")
    ap.add_argument("--fold", action="store_true")
    ap.add_argument("--witnesses", action="store_true")
    ap.add_argument("--emit-patch", action="store_true")
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.emit_patch:
        emit_patch()
        ok, why = patch_matches_cell()
        print(("PATCH == CELL: " if ok else "PATCH != CELL: ") + why)
        return 0 if ok else 1
    if a.reaccrue:
        for which in (["shipped", "patched"] if a.reaccrue == "both" else [a.reaccrue]):
            print("wrote", reaccrue(which))
        return 0
    if a.labels:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_labels(n_boot=(200 if a.smoke else a.n_boot), cap=(40 if a.smoke else 700))
        json.dump(r, open(os.path.join(OUT_DIR, "labels.json"), "w"), indent=1)
        for pop in ("all_nominals", "core", "SUBJ_nsubj_active", "OBJ_obj", "PASS_SUBJ_nsubj_pass",
                    "BY_AGENT_obl_agent"):
            v = r[pop]
            if not v.get("n"):
                continue
            print("%-22s n %5d" % (pop, v["n"]))
            for nm, x in v["accuracy"].items():
                d = v["vs_live_shipped"].get(nm)
                print("     %-34s %.4f %s" % (nm, x, ("%+0.4f CI%s %s" % (d["delta"], d["ci95"],
                      "SEP" if d["separated"] else "")) if d else ""))
        return 0
    if a.witnesses:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_witnesses()
        json.dump(r, open(os.path.join(OUT_DIR, "witnesses.json"), "w"), indent=1)
        return 0
    if a.fold:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_fold(n_boot=(200 if a.smoke else a.n_boot), cap=(40 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "fold.json"), "w"), indent=1)
        return 0
    if a.detectors:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_detectors(n_boot=(200 if a.smoke else a.n_boot), cap=(40 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "detectors.json"), "w"), indent=1)
        return 0
    if a.board_dim:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_board_dimension(n_boot=(200 if a.smoke else a.n_boot), cap=(200 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "board_dimension.json"), "w"), indent=1)
        return 0
    if a.gum:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_gum(n_boot=(200 if a.smoke else a.n_boot), cap=(4 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "gum.json"), "w"), indent=1)
        for sp, v in r.items():
            print("=== %s: %d predicates in %d files, %d gold passive"
                  % (sp, v["n_predicates"], v["n_files"], v["n_gold_passive"]))
            for nm, q in v["prf"].items():
                s_ = v["vs_floor"][nm]
                print("   %-24s P %.4f R %.4f F %.4f acc %.4f  %+0.4f CI%s %s"
                      % (nm, q["precision"], q["recall"], q["f1"], q["accuracy"], s_["delta"], s_["ci95"],
                         "SEP" if s_["separated"] else ""))
        return 0
    if a.push:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_push(n_boot=(200 if a.smoke else a.n_boot), cap=(200 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "push.json"), "w"), indent=1)
        print(json.dumps(r, indent=1))
        return 0
    if a.extra:
        os.makedirs(OUT_DIR, exist_ok=True)
        r = arm_extra(n_boot=(200 if a.smoke else a.n_boot),
                      cap_tr=(400 if a.smoke else None), cap_te=(200 if a.smoke else None))
        json.dump(r, open(os.path.join(OUT_DIR, "extra.json"), "w"), indent=1)
        print(json.dumps({k: v for k, v in r.items() if k != "adjectival_residual"}, indent=1)[:4000])
        print("adjectival residual:", r["adjectival_residual"]["false_fires"], "false fires,",
              r["adjectival_residual"]["with_degree_modifier"], "with a degree modifier")
        for e in r["adjectival_residual"]["examples"]:
            print("   ", e)
        return 0
    run(smoke=a.smoke, n_boot=a.n_boot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
