"""pri 140 -- THE AGENT COMPETITION LOSES WITH THE RIGHT ANSWER ON THE BALLOT.

THE DEFECT (pri 126, 2026-09-16).  On UD-EWT test the reader's who-did-what AGENT row reads 424/561 = 0.7558,
BELOW its word-order floor (nearest pre-verbal nominal on the reader's OWN categories), and 109 of its 137
errors (79.6%) are PICK errors -- the gold agent WAS in the candidate stream and another candidate won.  A
competition that loses to bare word order in English is MIS-WEIGHED, not under-supplied.

WHAT THIS CELL DOES
  1. --anatomy   reproduces the pri 126 cause table first-hand (never the sealed population) AND splits every
                 pick error three ways off GOLD structure, read only AFTER the reader has answered:
                   wrong_entity            the picked token is in neither the gold agent's name run nor its NP
                   right_entity_name_token the picked token is in the gold agent's flat/compound NAME RUN
                                           (the UD first-token-of-a-name convention: `Kori` vs `Schulman`)
                   right_np_modifier       the picked token is inside the gold agent's own NP but is a modifier
                                           (`the South Korean company` -> `Korean`); a real misread, pattern 4
  2. --build     LEARNS the agent cue validities from UD-EWT TRAIN by COUNTING (MacWhinney, Bates & Kliegl 1984:
                 validity = availability x reliability), the same math the coarse role table already uses
                 (`strengths_from_counts`): strength(cue value -> AGENT) = log P(agent | config, value) -
                 log P(agent | config).  The landed AGENT_VALIDITIES are HAND-SET -- that is the defect this
                 replaces.  Writes data/frontend_assets/agent_cue_validities_ud_ewt_v1.json.
  3. --measure   runs the board's own UD-EWT agent/patient/state rows through the LIVE reader with BOTH arms in
                 ONE process (landed competition vs re-weighed competition), plus the word-order floor, the
                 info-free twin (validities permuted across cues) and a chunk-paired bootstrap.
  4. --observe   the plasticity probe: two documents read in sequence; the second document's decisions use the
                 counts the first document updated.

THE ORGAN.  The re-weighed competition is ONE arm of the existing Competition-Model organ
(`hdlab/graded_role_assigner.py`).  This cell carries a REFERENCE implementation of exactly what the proposed
diff adds to that organ, and PREFERS the organ's own implementation when it is present -- so the cell measures
the landed code after the diff lands and reproduces it before.  See `_organ_or_local`.

Writes ONLY to its own get_output_dir (Q115) plus the named asset.  No sealed file is read, listed or opened.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import sys
import tempfile
import time
from collections import Counter, defaultdict

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR = "agent_pick_reweigh_v1"
from experiments._seed_checkpoint import get_output_dir          # noqa: E402

# THE SHIM.  Inside the ORGAN BLOCK below, these names are module-level in `hdlab/graded_role_assigner.py`
# already, so importing them here lets the block be BYTE-IDENTICAL in the cell and in the organ -- which is
# what `--emit-patch` relies on to prove the diff is the code that was measured.
from hdlab.graded_role_assigner import (                          # noqa: E402
    NOMINATIVE_PRON, _AGENT_ANIM_PRON, _AGENT_NP_SKIP, _WHREL, _agent_is_animate, _agent_pp_governed, by_governs,
    clause_bounds, is_passive_predicate, mention_head_wpos, softmax)

OUT_DIR = str(get_output_dir(ANCHOR))
UD_TEST = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-train.conllu")
SEED = 20260916
UD_CAP = 719          # pri 126's own UD-EWT anatomy cap (561 gold agent items)
CHUNK = 20


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _r4(x):
    return round(float(x), 4)


# ===================================================================================================
# SECTION 1 -- THE RE-WEIGHED COMPETITION (the reference implementation the diff moves into the organ)
# ===================================================================================================
# THE BRAIN'S MATH.  Bates & MacWhinney's Competition Model: each cue carries a VALIDITY = availability
# (how often the cue is present) x reliability (how often it points at the right answer when present), and
# validities are ACCRUED FROM EXPOSURE, not set by hand.  The additive-activation-then-argmax competition
# (`graded_competition.net_activation`) is the normative integrator when each cue contributes its LOG-ODDS,
# so the strength of cue c taking value x, within configuration g (= clause voice), is the contrast
#       s_g(c, x) = log P(agent | g, c = x) - log P(agent | g)
# estimated by add-alpha counting with Dirichlet shrinkage toward the configuration marginal (availability
# falls out: a value seen rarely shrinks to 0 and cannot vote; reliability falls out: a value that is nearly
# deterministic gets a large contrast).  This is the SAME math `graded_role_assigner.strengths_from_counts`
# already uses for the coarse role table -- one organ, one accrual form.
# <<<ORGAN BLOCK BEGIN -- this text is inserted VERBATIM into hdlab/graded_role_assigner.py by --emit-patch>>>
_AGENT_VALIDITIES_PATH = os.environ.get("HDLAB_AGENT_VALIDITIES") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "frontend_assets",
    "agent_cue_validities_ud_ewt_v1.json")
# HDLAB_AGENT_REWEIGH=0 restores the hand-set AGENT_VALIDITIES competition byte-identically (the A/B switch).
AGENT_REWEIGH = os.environ.get("HDLAB_AGENT_REWEIGH", "1") != "0"
AGENT_CUES = ("order", "nearrank", "firstinclause", "case", "govern", "anim", "given",
              "struct", "scope", "cat", "agree", "vfit", "licensor")
# TWO CUES BUILT AND REFUTED ON DEV, kept here as named negatives rather than deleted silently:
#   rsubj   -- the landed role competition's P(SUBJ) marginalised over the head posterior, read graded.
#              Dev 0.7880 -> 0.7794 (WORSE).  WHY, and it is worth knowing: `coarse_role_posterior` is itself
#              an additive competition over head-class x order, case and preposition -- the SAME evidence
#              this competition already reads -- so it is not an independent cue, it is the same evidence
#              passed through a second softmax, and adding it double-counts.  A cue must be a NEW
#              measurement of the world, not a re-reading of one already taken.
#   for_to  -- `for X to VERB` / `with X VERBing` given its own `govern` VALUE (the infinitival subject is
#              marked by a preposition in English, so the oblique reading is a construction blindness).
#              The value learned the right sign (-0.10 against prep's -2.45) but the split cost dev
#              0.7942 -> 0.7880.  Not adopted; the construction is named in SOLVED.md as a live lead.
AGENT_ALPHA = 0.5
# THE ACCRUAL RATE.  How much experience a cue VALUE needs before it may outvote its own configuration:
# `m_shrink` Dirichlet pseudo-counts pull a value's rate to the configuration marginal.  SWEPT on dev, never
# adopted from anywhere else.
AGENT_M_SHRINK = float(os.environ.get("HDLAB_AGENT_M_SHRINK", "2.0"))
AGENT_TEMP = 1.0
# THE CONFIGURATION.  "voice" = the clause's voice alone (v1); "voice_order" = voice x the candidate's
# position relative to the predicate, which is what the coarse role table already does (head-class x order)
# and for the same reason: the two highest-validity cues become the CONFIGURATION and every other cue is
# read as a CONTRAST WITHIN it, so correlated cues cannot each re-count the majority class.
AGENT_CONFIG = os.environ.get("HDLAB_AGENT_CONFIG", "voice")
# THE CUE SET THAT VOTES.  All 12 cues are COMPUTED and ACCRUED (the table stays complete and the online path
# keeps learning every one of them), but only these VOTE.  Chosen by backward elimination on the UD-EWT TRAIN
# DEV slice the counts never saw, and the same four survive under all three configurations tried -- they are
# the DECORRELATED core.  WHY a subset at all: this integrator adds each cue's MARGINAL log-odds, so two cues
# that carry the same variance each re-count it (the additive form is exact only for conditionally independent
# cues).  The Competition Model's own connectionist simulations discount that overlap by error-driven weight
# competition; a COUNTS table cannot, and a fitted classifier is barred here -- so the overlap is handled by
# which cues enter, decided on dev.  THIS IS THE HONEST LIMIT OF THE COUNT FORM and it is named in SOLVED.md.
AGENT_CUE_SET = tuple((os.environ.get("HDLAB_AGENT_CUE_SET") or "order,govern,struct,cat").split(","))


def _agent_bin(x, edges, names):
    for e, nm in zip(edges, names):
        if x < e:
            return nm
    return names[-1]


def _agent_clause_scope(toks, up, v0, p, lo, hi):
    """same / rel / outside.  `rel`: the candidate is the RELATIVIZER that heads the relative clause whose verb
    is v0 -- the clause-boundary scope the landed `clause_bounds` deliberately does NOT cut at (relativizers
    EMBED), which is why a distant main-clause nominal wins the RC verb's competition (pattern 2)."""
    low = [t.lower() for t in toks]
    if lo <= p < hi:
        if low[p] in _WHREL and p < v0:
            if not any(low[k] in _WHREL for k in range(p + 1, v0)):
                return "rel"
        # a candidate separated from the predicate by an intervening relativizer sits OUTSIDE the embedded
        # clause the predicate belongs to (the distant-nominal pattern: `... it ... which BROKE`).
        if p < v0 and any(low[k] in _WHREL for k in range(p + 1, v0)):
            return "acrossrel"
        return "same"
    return "outside"


# --- THE TWO PINNED COMPETITION-MODEL CUES THE LANDED COMPETITION NEVER HAD -------------------------
# Bates & MacWhinney's English cue hierarchy is word order > AGREEMENT > animacy, and the model's cue
# inventory also carries the VERB'S OWN EXPECTATIONS (subcategorisation / semantic fit).  The landed
# `agent_supports` has neither.  Both are read here glass-box, from organs already on disk:
#   agree : subject-verb NUMBER agreement.  The verb's demand comes from its auxiliary chain (is/was/has
#           vs are/were/have) or its own present 3sg -s; the candidate's number comes from the glass-box
#           morphology organ (a noun whose WordNet base differs from its surface form is plural) or from
#           the pronoun's own form.  English marks agreement WEAKLY, so this cue's validity is expected to
#           be small -- and it is learned, not asserted.
#   vfit  : how good a SUBJECT this candidate is for THIS verb, from the substrate's own reading-grown
#           typed selectional-preference store (`typed_selectional_preference_bf_subj_v1`, Resnik 1996
#           association over supersenses, grown by the substrate's own chain -- no external parser).
_AGENT_SG_AUX = frozenset(("is", "was", "has", "'s", "does"))
_AGENT_PL_AUX = frozenset(("are", "were", "have", "do", "'re", "'ve"))
_AGENT_SG_PRON = frozenset(("he", "she", "it", "this", "that", "him", "her", "one", "who"))
_AGENT_PL_PRON = frozenset(("they", "we", "these", "those", "them", "us", "both"))
_AGENT_NUM_CACHE = {}


def _agent_number(head, tag):
    """sg / pl / unk for one candidate -- the glass-box morphology organ, no gold."""
    h = head.lower()
    if h in _AGENT_SG_PRON:
        return "sg"
    if h in _AGENT_PL_PRON:
        return "pl"
    if tag not in ("NOUN", "PROPN"):
        return "unk"
    key = (h, tag)
    hit = _AGENT_NUM_CACHE.get(key)
    if hit is not None:
        return hit
    v = "unk"
    if h.endswith("s") and len(h) > 2:
        try:
            from hdlab.morphology import morphy
            b = morphy(h, "n")
            v = "pl" if (b and b != h) else "sg"
        except Exception:
            v = "unk"
    else:
        v = "sg"
    if len(_AGENT_NUM_CACHE) > 20000:
        _AGENT_NUM_CACHE.clear()
    _AGENT_NUM_CACHE[key] = v
    return v


def _agent_verb_demand(toks, pos, low, v0):
    """sg / pl / unk -- what number THIS predicate's morphology demands of its subject."""
    for k in range(max(0, v0 - 3), v0):
        if low[k] in _AGENT_SG_AUX:
            return "sg"
        if low[k] in _AGENT_PL_AUX:
            return "pl"
    w = low[v0] if 0 <= v0 < len(low) else ""
    if w in _AGENT_SG_AUX:
        return "sg"
    if w in _AGENT_PL_AUX:
        return "pl"
    tag = pos[v0] if 0 <= v0 < len(pos) else None
    if tag in ("VERB", "AUX") and w.endswith("s") and not w.endswith("ss"):
        try:
            from hdlab.morphology import morphy
            b = morphy(w, "v")
            if b and b != w:
                return "sg"
        except Exception:
            pass
    return "unk"


_AGENT_TEACHER = [None]


def _agent_subject_fit(verb_tok, head):
    """The verb's own expectation of this candidate as its SUBJECT -- a binned plausibility share from the
    substrate's reading-grown typed selectional-preference store."""
    if _AGENT_TEACHER[0] is None:
        try:
            import hdlab.attachment_arm as AA
            _AGENT_TEACHER[0] = (AA._plaus_teacher(), AA._plaus_bin)
        except Exception:
            _AGENT_TEACHER[0] = (False, None)
    t, binf = _AGENT_TEACHER[0]
    if not t:
        return "na"
    try:
        return binf(t.plausibility_subj(verb_tok, head))
    except Exception:
        return "na"


def agent_cue_values(toks, pos, v0, cands, gaz=None, cluster_freq=None, head_post=None, tag_post=None):
    """([per-candidate config], [per-candidate {cue: value}]).  `cands` = [(head_pos, head_string, cluster, span_end), ...]
    with head_pos the WITHIN-SENTENCE index of the mention's HEAD (span-independent: pri 138 may widen spans).
    head_post = the attachment arm's graded head belief {dep: {head: p}} (0-based); tag_post = the category
    organ's per-token posterior [{cat: p}].  Both optional: absent -> the cue takes value "na" and the learned
    contrast for "na" (~0 after shrinkage) makes it silent."""
    low = [t.lower() for t in toks]
    passive = is_passive_predicate(list(toks), list(pos), v0 + 1)
    cfg = "pass" if passive else "act"
    lo, hi = clause_bounds(toks, pos, v0)
    cf = cluster_freq or {}
    pres = sorted([c[0] for c in cands if c[0] < v0])
    posts = sorted([c[0] for c in cands if c[0] > v0])
    inclause = sorted([c[0] for c in cands if lo <= c[0] < hi and c[0] < v0])
    demand = _agent_verb_demand(toks, pos, low, v0)
    out = []
    for cand in cands:
        p, head, cl = cand[0], str(cand[1]), cand[2]
        hl = head.lower()
        tag = pos[p] if 0 <= p < len(pos) else None
        d = {}
        d["order"] = "pre" if p < v0 else "post"
        if p < v0:
            r = (len(pres) - 1 - pres.index(p)) if p in pres else 9
            d["nearrank"] = "n0" if r == 0 else ("n1" if r == 1 else "n2+")
        else:
            r = posts.index(p) if p in posts else 9
            d["nearrank"] = "p0" if r == 0 else "p1+"
        d["firstinclause"] = ("first" if (inclause and p == inclause[0]) else
                              ("inclause" if p in inclause else "no"))
        if tag == "PRON" or hl in _AGENT_ANIM_PRON or hl in NOMINATIVE_PRON:
            d["case"] = "nom" if hl in NOMINATIVE_PRON else ("acc" if hl in _AGENT_ANIM_PRON else "neutral")
        else:
            d["case"] = "nonpron"
        if by_governs(low, pos, p):
            d["govern"] = "by"
        elif _agent_pp_governed(low, pos, p):
            d["govern"] = "prep"
        else:
            d["govern"] = "free"
        a = _agent_is_animate(hl, tag, gaz)
        d["anim"] = "anim" if a > 0 else ("inanim" if a < 0 else "unk")
        d["given"] = "given" if cf.get(cl, 0) >= 2 else "new"
        # STRUCTURE: the attachment arm's GRADED belief that this candidate attaches to THIS predicate --
        # the arm's subject arc read as a belief, not the incremental parser's binary subject-before flag.
        if head_post is None:
            d["struct"] = "na"
        else:
            pv = float((head_post.get(p) or {}).get(v0, 0.0))
            d["struct"] = _agent_bin(pv, (0.05, 0.25, 0.60, 0.85), ("s0", "s1", "s2", "s3", "s4"))
        d["scope"] = _agent_clause_scope(toks, pos, v0, p, lo, hi)
        # LICENSOR (pri 108's finding, read as a GRADED cue): a nominal licensed by ANOTHER NOMINAL is a
        # PROPERTY of that thing, not a participant of the event -- `the people OF FALLUJAH condemn`,
        # `John Donovan FROM ARGGHHH! has put out`.  The attachment arm already knows: it puts most of this
        # candidate's head mass on another nominal, not on the predicate.  Read that mass, binned.
        if head_post is None:
            d["licensor"] = "na"
        else:
            row = head_post.get(p) or {}
            lic = max([q for h, q in row.items()
                       if h != v0 and 0 <= h < len(pos) and pos[h] in ("NOUN", "PROPN", "PRON")] or [0.0])
            d["licensor"] = _agent_bin(lic, (0.05, 0.25, 0.60, 0.85), ("l0", "l1", "l2", "l3", "l4"))
        # CATEGORY read GRADED: the posterior mass the category organ puts on a NOMINAL category at this
        # token.  An ADJ-tagged token that wins the competition (pattern 4) is the category rung read as an
        # argmax; reading it graded lets a confidently-ADJ token lose without a hard filter.
        if tag_post is None:
            d["cat"] = "na"
        else:
            tp = tag_post[p] if 0 <= p < len(tag_post) else {}
            m = float(tp.get("NOUN", 0.0) + tp.get("PROPN", 0.0) + tp.get("PRON", 0.0))
            d["cat"] = _agent_bin(m, (0.25, 0.60, 0.90), ("g0", "g1", "g2", "g3"))
        d["agree"] = demand + "_" + _agent_number(head, tag)
        d["vfit"] = _agent_subject_fit(toks[v0] if 0 <= v0 < len(toks) else "", head)
        out.append(d)
    if AGENT_CONFIG == "voice_order":
        cfgs = [cfg + "|" + d["order"] for d in out]
    elif AGENT_CONFIG == "voice_order_govern":
        cfgs = [cfg + "|" + d["order"] + "|" + d["govern"] for d in out]
    else:
        cfgs = [cfg] * len(out)
    return cfgs, out


def empty_agent_counts():
    return {"cue_set": "agent_v1", "cues": list(AGENT_CUES), "alpha": AGENT_ALPHA,
            "m_shrink": AGENT_M_SHRINK, "config": {}}


def accrue_agent(counts, cfg, values, is_agent, w=1.0):
    """Count ONE candidate's outcome.  `values` = {cue: value}; is_agent = did this candidate turn out to be
    the agent (gold at build time; the reader's own comprehension outcome on the online path)."""
    g = counts["config"].setdefault(cfg, {"n": [0.0, 0.0], "cue": {}})
    g["n"][0] += w * (1.0 if is_agent else 0.0)
    g["n"][1] += w
    for c, x in values.items():
        t = g["cue"].setdefault(c, {}).setdefault(str(x), [0.0, 0.0])
        t[0] += w * (1.0 if is_agent else 0.0)
        t[1] += w


def agent_strengths_from_counts(counts, temp=None):
    """counts -> {config: {prior, cue: {value: strength}}}.  A PURE FUNCTION of the counts, so the online
    observe path and the batch build produce the same table from the same experience."""
    a = float(counts.get("alpha", AGENT_ALPHA))
    m = float(counts.get("m_shrink", AGENT_M_SHRINK))
    T = float(AGENT_TEMP if temp is None else temp)
    out = {}
    for cfg, g in counts.get("config", {}).items():
        na, nt = float(g["n"][0]), float(g["n"][1])
        p0 = (na + a) / (nt + 2.0 * a)
        lp0 = math.log(max(p0, 1e-12))
        tab = {}
        for c, vals in g.get("cue", {}).items():
            tv = {}
            for x, kk in vals.items():
                ka, kt = float(kk[0]), float(kk[1])
                # Dirichlet shrinkage toward the configuration marginal: availability is built in -- a value
                # with few observations is pulled to p0 and its contrast goes to 0 (it cannot vote).
                p = (ka + m * p0 + a) / (kt + m + 2.0 * a)
                tv[x] = (math.log(max(p, 1e-12)) - lp0) / T
            tab[c] = tv
        out[cfg] = {"prior": lp0, "cue": tab}
    return out


def agent_table_from_counts(counts, temp=None):
    return {"built": _now(), "cue_set": counts.get("cue_set", "agent_v1"), "cues": list(AGENT_CUES),
            "counts": counts, "strengths": agent_strengths_from_counts(counts, temp),
            "math": "log P(agent | config, cue=value) - log P(agent | config); add-alpha + Dirichlet shrink"}


def agent_activation(table, cfgs, values_list, permute_seed=None, cue_set=None, permute_mode="within"):
    """Additive log-odds activation per candidate (graded_competition.net_activation's form, with the learned
    contrast as the per-cue weighted support).

    permute_seed -> THE INFO-FREE TWIN.  Two forms, both reported:
      "within"  (deployed)  each cue's learned strengths are re-assigned to its OWN values by a random
                bijection.  Every cue keeps its availability, its number of values and the exact multiset of
                strengths it earned -- and loses which value means what.  This is the same-shape twin.
      "across"  (the brief's wording) each cue's table is swapped with another cue's.  Because two cues
                share no value names this makes EVERY lookup miss, so the activation is identically zero and
                the twin degenerates to "always the first candidate" -- an info-free arm, but a WEAKER
                control than "within", so "within" is the one the gate is read against."""
    S = table["strengths"]
    if isinstance(cfgs, str):
        cfgs = [cfgs] * len(values_list)
    A = np.zeros(len(values_list), dtype=float)
    for i, vals in enumerate(values_list):
        g = S.get(cfgs[i])
        if g is None:                          # an unseen configuration backs off to its voice marginal
            g = S.get(str(cfgs[i]).split("|")[0]) or {"prior": 0.0, "cue": {}}
        cue_tab = g["cue"]
        if cue_set is not None:
            cue_tab = {k: v for k, v in cue_tab.items() if k in cue_set}
        if permute_seed is not None:
            rng = np.random.default_rng(permute_seed)
            ks = sorted(cue_tab.keys())
            if permute_mode == "across":
                perm = list(rng.permutation(len(ks)))
                cue_tab = {ks[i2]: cue_tab[ks[perm[i2]]] for i2 in range(len(ks))}
            else:
                nt = {}
                for c in ks:
                    vv = sorted(cue_tab[c].keys())
                    pp = list(rng.permutation(len(vv)))
                    nt[c] = {vv[i2]: cue_tab[c][vv[pp[i2]]] for i2 in range(len(vv))}
                cue_tab = nt
        # THE CONFIGURATION'S OWN LOG-ODDS is part of the activation: with voice x order as the
        # configuration, "is this candidate pre-verbal in an active clause" is carried HERE, once, instead
        # of by several correlated cues each re-counting it.
        tot = float(g.get("prior", 0.0))
        for c, x in vals.items():
            t = cue_tab.get(c)
            if t is not None:
                tot += float(t.get(str(x), 0.0))
        A[i] = tot
    return A


def agent_competition_reweighed(toks, pos, v, cands, cluster_freq=None, gaz=None, table=None,
                                head_post=None, tag_post=None, twin_seed=None, cue_set=None,
                                permute_mode="within"):
    """(pick_head, margin, conf) -- the AGENT by the RE-WEIGHED competition.  Same shape as the landed
    `agent_competition_pick_conf`, so it is a drop-in arm of the same organ."""
    c = [(mention_head_wpos(m), m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start")))
         for m in cands]
    if not c:
        return "?", None, None
    cfgs, vals = agent_cue_values(toks, pos, v, c, gaz=gaz, cluster_freq=cluster_freq,
                                  head_post=head_post, tag_post=tag_post)
    A = agent_activation(table, cfgs, vals, permute_seed=(None if twin_seed is None else twin_seed + v),
                         cue_set=(AGENT_CUE_SET if cue_set is None else cue_set),
                         permute_mode=permute_mode)
    pick = c[int(np.argmax(A))][1]
    As = np.sort(np.asarray(A, dtype=float))[::-1]
    if len(As) > 1:
        top2 = float(As[0] - As[1])
        p = softmax(A)
        ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(len(A)))
    else:
        top2 = float(abs(As[0]) + 1.0)
        ent = 0.0
    return pick, float(np.tanh(top2 / 3.0)), float(1.0 - ent)


def save_agent_validities(path=None, table=None):
    p = path or _AGENT_VALIDITIES_PATH
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(table, fh)
    return p


def load_agent_validities(path=None):
    p = path or _AGENT_VALIDITIES_PATH
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        doc = json.load(fh)
    doc["strengths"] = agent_strengths_from_counts(doc["counts"])   # ALWAYS rebuilt from the counts
    return doc


_AGENT_TABLE_CACHE = [False, None]


def agent_validities(reload=False):
    """The live learned table, loaded ONCE per process (and re-loadable).  The competition consults this;
    `observe_agent_outcome` mutates the very object it returns, so a read that observes keeps learning."""
    if reload or not _AGENT_TABLE_CACHE[0]:
        _AGENT_TABLE_CACHE[0] = True
        _AGENT_TABLE_CACHE[1] = load_agent_validities()
    return _AGENT_TABLE_CACHE[1]


def observe_agent_outcome(toks, pos, v, cands, agent_head, table, gaz=None, cluster_freq=None,
                          head_post=None, tag_post=None, w=1.0):
    """THE ONLINE PATH.  One comprehended clause updates the counts and the strengths are recomputed from
    them -- the table is never frozen.  `agent_head` = the head the reader itself settled on."""
    c = [(mention_head_wpos(m), m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start")))
         for m in cands]
    if not c:
        return table
    cfgs, vals = agent_cue_values(toks, pos, v, c, gaz=gaz, cluster_freq=cluster_freq,
                                  head_post=head_post, tag_post=tag_post)
    tgt = str(agent_head or "").strip().lower()
    for k, cd in enumerate(c):
        accrue_agent(table["counts"], cfgs[k], vals[k], str(cd[1]).strip().lower() == tgt, w=w)
    table["strengths"] = agent_strengths_from_counts(table["counts"])
    return table


# ===================================================================================================
# SECTION 2 -- THE GRADED UPSTREAM INPUTS (the attachment arm's head belief, the category posterior)
# ===================================================================================================
# Both are computed from toks/POS alone, cached per sentence, so the competition can read them WITHOUT a new
# argument at any call site in hdlab/ or tools/ (the diff stays inside this one organ).
_AGENT_HP_CACHE = {}
_AGENT_TP_CACHE = {}
_AGENT_ARM_TABLE = [None]
_AGENT_CACHE_LIMIT = 4096


def agent_head_belief(toks, pos):
    """The attachment arm's graded head posterior {dep0: {head0: p}} (0-based, the arm's own root excluded)."""
    key = (tuple(toks), tuple(pos))
    hit = _AGENT_HP_CACHE.get(key)
    if hit is not None:
        return hit
    import hdlab.attachment_arm as AA
    if _AGENT_ARM_TABLE[0] is None:
        _AGENT_ARM_TABLE[0] = AA.load_attachment_validities()
    try:
        post = AA.head_posterior(list(toks), list(pos), _AGENT_ARM_TABLE[0])
    except Exception:
        post = {}
    # to 0-based on both axes (the arm speaks 1-based dependents with 0 = root)
    out = {}
    for j, row in (post or {}).items():
        out[int(j) - 1] = {int(h) - 1: float(p) for h, p in row.items() if int(h) >= 1}
    if len(_AGENT_HP_CACHE) > _AGENT_CACHE_LIMIT:
        _AGENT_HP_CACHE.clear()
    _AGENT_HP_CACHE[key] = out
    return out


def agent_category_belief(toks):
    """The category organ's per-token posterior [{cat: p}] from the live front-end tagger."""
    key = tuple(toks)
    hit = _AGENT_TP_CACHE.get(key)
    if hit is not None:
        return hit
    import hdlab.frontend as FE
    try:
        _tags, post = FE.tagger().tag_with_posterior(list(toks))
        out = [dict(r) for r in post]
    except Exception:
        out = None
    if len(_AGENT_TP_CACHE) > _AGENT_CACHE_LIMIT:
        _AGENT_TP_CACHE.clear()
    _AGENT_TP_CACHE[key] = out
    return out


# <<<ORGAN BLOCK END>>>


def _organ_or_local():
    """Prefer the ORGAN's own implementation when the diff has landed; else this cell's reference copy.
    This is what makes the cell green on the tree as landed AND on the tree before landing."""
    import hdlab.graded_role_assigner as GRA
    if hasattr(GRA, "agent_competition_reweighed") and hasattr(GRA, "load_agent_validities"):
        return GRA, "organ"
    return sys.modules[__name__], "cell"


# ===================================================================================================
# SECTION 3 -- BAR 1: THE SPLIT.  wrong ENTITY vs right entity, wrong TOKEN of its name.
# ===================================================================================================
# METHOD (stated, as the bar requires).  UD-EWT carries no coref, so the entity identity available is the
# GOLD dependency structure of the gold agent token, read only AFTER the reader has answered:
#   NAME RUN  = the maximal set of tokens connected to the gold agent head through `flat` / `flat:name` /
#               `compound` / `goeswith` arcs in either direction.  This is EXACTLY the UD convention the
#               scoring convention is an artifact of: a multi-word name is headed by its FIRST token, so
#               `Schulman` in `Kori Schulman` is a different STRING for the SAME individual.
#   NP        = the gold subtree of the gold agent head (its determiner, adjectives, PP modifiers).
# A picked token inside the NAME RUN is the same entity under a different name token; inside the NP but not
# the name run it is a MODIFIER of the right entity (`the South Korean company` -> `Korean`) -- a real
# misread of which token names the thing, not a convention artifact; outside both it is a WRONG ENTITY.
_NAME_DEPS = ("flat", "goeswith", "compound")


def _name_run(sent, head_id):
    """1-based token ids of the gold NAME RUN containing `head_id`."""
    adj = defaultdict(set)
    for t in sent:
        d = (t.get("deprel") or t.get("dep") or "").split(":")[0]
        if d in _NAME_DEPS and t["head"] > 0:
            adj[t["head"]].add(t["id"])
            adj[t["id"]].add(t["head"])
    seen, stack = set(), [head_id]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(adj.get(x, ()))
    return seen


def _subtree(sent, root_id):
    kids = defaultdict(list)
    for t in sent:
        kids[t["head"]].append(t["id"])
    out, stack = set(), [root_id]
    while stack:
        i = stack.pop()
        if i in out:
            continue
        out.add(i)
        stack.extend(kids.get(i, ()))
    return out


def split_pick_error(sent, toks, gold_id, model_head):
    """('wrong_entity' | 'right_entity_name_token' | 'right_np_modifier', strict_label).
    `strict_label` repeats the judgement using ONLY the FIRST occurrence of the model string (the anatomy's
    own convention), so the reader can see how much of the split rests on string ambiguity."""
    m = str(model_head or "").strip().lower()
    occ = [i + 1 for i, t in enumerate(toks) if str(t).strip().lower() == m]
    run = _name_run(sent, gold_id)
    np_ids = _subtree(sent, gold_id)

    def judge(ids):
        if any(i in run for i in ids):
            return "right_entity_name_token"
        if any(i in np_ids for i in ids):
            return "right_np_modifier"
        return "wrong_entity"

    return judge(occ), judge(occ[:1])


# ===================================================================================================
# SECTION 4 -- CAPTURE: one LIVE read of UD-EWT test, every gold agent item with everything the
#             competition saw.  The anatomy, the split and the offline arm sweeps all run off this, so
#             a sweep costs seconds instead of a re-read (the LIVE two-arm gate still re-reads: see
#             `run_measure`).
# ===================================================================================================
def _norm(x):
    return (str(x) or "").strip().lower()


def _ud_sents(cap=None, path=None, offset=0):
    from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
    s = load_ud(path or UD_TEST)
    return s[offset:cap] if cap else s[offset:]


def capture(cap=UD_CAP, chunk=CHUNK, progress=True, discover_pronouns=False, path_corpus=None, offset=0):
    """Read UD-EWT through the LIVE reader exactly as the board's agent row does, and record for every
    gold agent item: the sentence, the reader's own POS, the candidate mention stream the competition saw,
    the passage cluster frequencies, the reader's answer, and the gold.  `path_corpus` selects the split --
    TRAIN for the validity build, TEST for the measurement (the two are never mixed)."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    from hdlab.graded_role_assigner import clause_bounds
    gaz = load_given_gazetteer()
    sents = _ud_sents(cap, path=path_corpus, offset=offset)
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    flat = [s for ch in chunks for s in ch]
    assert len(flat) == len(sents), "the chunking must PARTITION the sentence list"
    items = []
    tmp = tempfile.mkdtemp(prefix="p140cap_")
    t0 = time.time()
    try:
        for ci, ch in enumerate(chunks):
            docid = "udewt%04d" % ci
            path = os.path.join(tmp, docid + ".conll")
            B._ud_write_chunk(ch, path, docid, discover_pronouns=discover_pronouns)
            rdr = SituationReader(gaz=gaz, **B.READER_KW)
            sm = rdr.read(path)
            anoms, afreq = rdr._cm_agent_candidates(len(ch))
            ev_by = defaultdict(list)
            for e in sm.events:
                ev_by[(e.sent_idx, e.pred_idx)].append(e)
            ments = list(getattr(rdr, "_coref_mentions", []) or [])
            cand_by_sent = defaultdict(set)
            for m in ments:
                cand_by_sent[m.get("sent_idx", -1)].add(_norm(m.get("head")))
            for si, s in enumerate(ch):
                toks = [t["form"] for t in s]
                try:
                    up = list(rdr._cached_tag(list(toks)))
                except Exception:
                    up = ["X"] * len(toks)
                for (v, ag, passive) in B._gold_agent_items(s):
                    evs = ev_by.get((si, v - 1), [])
                    cands = []
                    if anoms is not None and si < len(anoms):
                        lo, hi = clause_bounds(toks, up, v - 1)
                        inc = [m for m in anoms[si] if lo <= m["wtok_start"] < hi]
                        cands = inc or list(anoms[si])
                    items.append({
                        "docid": docid, "si": si, "toks": toks, "pos": up, "sent": s,
                        "v": v, "gold_id": ag, "passive": bool(passive),
                        "gold": _norm(toks[ag - 1]),
                        "model": _norm(evs[0].agent) if evs else "",
                        "fired": bool(evs),
                        "cands": [{"wtok_start": m.get("wtok_start"), "head": m.get("head"),
                                   "cluster": m.get("cluster"),
                                   "wtok_end": m.get("wtok_end", m.get("wtok_start")),
                                   "gtok_start": m.get("gtok_start", -1),
                                   "gtok_end": m.get("gtok_end", -1),
                                   "is_pronoun": bool(m.get("is_pronoun"))} for m in cands],
                        "freq": {str(k): int(vv) for k, vv in (afreq or {}).items()},
                        "on_ballot": _norm(toks[ag - 1]) in cand_by_sent.get(si, set()),
                    })
            del sm, rdr
            os.remove(path)
            if progress and (ci + 1) % 10 == 0:
                print("    ... %d/%d chunks, %.0fs" % (ci + 1, len(chunks), time.time() - t0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  captured %d gold agent items from %d sentences in %d chunks (%.0fs)"
          % (len(items), len(sents), len(chunks), time.time() - t0))
    return items, len(sents), len(chunks)


def anatomy_from_items(items, label, max_ex=3):
    """pri 126's cause table, recomputed first-hand, PLUS bar 1's split of every pick error."""
    C = Counter()
    SPL = Counter()
    SPL_STRICT = Counter()
    EX = defaultdict(list)
    for it in items:
        C["items"] += 1
        C["passive" if it["passive"] else "active"] += 1
        if not it["fired"]:
            C["no_event"] += 1
            continue
        if it["model"] == it["gold"]:
            C["correct"] += 1
            continue
        C["wrong"] += 1
        if not it["model"]:
            C["no_agent_emitted"] += 1
            continue
        if not it["on_ballot"]:
            C["candidate_set_miss"] += 1
            continue
        C["pick_error"] += 1
        lab, strict = split_pick_error(it["sent"], it["toks"], it["gold_id"], it["model"])
        SPL[lab] += 1
        SPL_STRICT[strict] += 1
        if len(EX[lab]) < max_ex:
            EX[lab].append("gold=%r model=%r verb=%r | %s"
                           % (it["toks"][it["gold_id"] - 1], it["model"], it["toks"][it["v"] - 1],
                              " ".join(it["toks"])[:140]))
    n = max(1, C["items"])
    err = max(1, C["items"] - C["correct"])
    print("\n" + "=" * 100)
    print("AGENT-RUNG ANATOMY -- %s" % label)
    print("=" * 100)
    print("  gold agent items          %5d   (active %d / passive %d)" % (C["items"], C["active"], C["passive"]))
    print("  correct                   %5d  (%.4f)" % (C["correct"], C["correct"] / n))
    for k in ("no_event", "no_agent_emitted", "candidate_set_miss", "pick_error"):
        print("  %-24s  %5d  (%.4f of all items, %.4f of errors)" % (k, C[k], C[k] / n, C[k] / err))
    print("  --- BAR 1: the pick errors split by ENTITY IDENTITY (gold name runs / gold NP, read after) ---")
    for k in ("wrong_entity", "right_entity_name_token", "right_np_modifier"):
        print("  %-24s  %5d  (%.4f of pick errors)  [strict-first-occurrence %d]"
              % (k, SPL[k], SPL[k] / max(1, C["pick_error"]), SPL_STRICT[k]))
        for e in EX[k][:2]:
            print("           e.g. %s" % e)
    return {"population": label, "counts": dict(C), "split": dict(SPL), "split_strict": dict(SPL_STRICT),
            "examples": {k: EX[k] for k in EX}}


_CAP_PATH = os.path.join(OUT_DIR, "capture_udtest.pkl")


def get_capture(cap=UD_CAP, chunk=CHUNK, refresh=False):
    import pickle
    if (not refresh) and os.path.exists(_CAP_PATH):
        with open(_CAP_PATH, "rb") as fh:
            d = pickle.load(fh)
        if d.get("cap") == cap and d.get("chunk") == chunk:
            print("  (capture reused: %d items)" % len(d["items"]))
            return d["items"], d["n_sents"], d["n_chunks"]
    items, ns, nc = capture(cap=cap, chunk=chunk)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(_CAP_PATH, "wb") as fh:
        pickle.dump({"cap": cap, "chunk": chunk, "items": items, "n_sents": ns, "n_chunks": nc}, fh)
    return items, ns, nc


# ===================================================================================================
# SECTION 5 -- OFFLINE REPLAY of the competition over the captured items (arm development + sweeps).
#             The LIVE two-arm gate is `run_measure`; this is the diagnostic that makes sweeping cheap.
# ===================================================================================================
def replay(items, table, arm="reweigh", gaz=None, twin_seed=None, cue_set=None, graded=True,
           permute_mode="within"):
    """Re-decide every captured item's AGENT with the named arm.  Returns per-item picks."""
    from hdlab.graded_role_assigner import agent_competition_pick_conf
    from hdlab.incremental_parser import incremental_subject_before
    mod, _src = _organ_or_local()
    picks = []
    for it in items:
        if not it["cands"]:
            picks.append(it["model"])
            continue
        toks, up, v0 = it["toks"], it["pos"], it["v"] - 1
        freq = {}
        for k, vv in it["freq"].items():
            freq[k] = vv
            try:
                freq[int(k)] = vv
            except (TypeError, ValueError):
                pass
        if arm == "landed":
            sb = incremental_subject_before(toks, up)
            h, _m, _c = agent_competition_pick_conf(toks, up, v0, it["cands"], cluster_freq=freq,
                                                    gaz=gaz, subj_before=sb, byhead_agent_cue=True)
        else:
            hp = agent_head_belief(toks, up) if graded else None
            tp = agent_category_belief(toks) if graded else None
            h, _m, _c = mod.agent_competition_reweighed(toks, up, v0, it["cands"], cluster_freq=freq,
                                                        gaz=gaz, table=table, head_post=hp, tag_post=tp,
                                                        twin_seed=twin_seed, cue_set=cue_set,
                                                        permute_mode=permute_mode)
        picks.append(_norm(h))
    return picks


def score_picks(items, picks):
    """Token-level accuracy (THE GATE), entity-level accuracy (bar 1's new column), and the wrong-ENTITY
    pick-error count -- all on the SAME population, per item, so the bootstrap can pair them."""
    tok, ent, wrong_ent = [], [], []
    for it, p in zip(items, picks):
        if not it["fired"]:
            tok.append(0); ent.append(0); wrong_ent.append(0)
            continue
        t = int(bool(p) and p != "?" and p == it["gold"])
        tok.append(t)
        if t:
            ent.append(1); wrong_ent.append(0)
            continue
        run = _name_run(it["sent"], it["gold_id"])
        forms = set(_norm(it["toks"][i - 1]) for i in run if 1 <= i <= len(it["toks"]))
        e = int(bool(p) and p != "?" and p in forms)
        ent.append(e)
        on_ballot = it["on_ballot"]
        lab = split_pick_error(it["sent"], it["toks"], it["gold_id"], p)[0] if (p and p != "?") else None
        wrong_ent.append(int(bool(on_ballot) and lab == "wrong_entity"))
    return {"tok": np.array(tok), "ent": np.array(ent), "wrong_entity": np.array(wrong_ent)}


def word_order_floor(items):
    """The board's own floor: the nearest PRE-verbal nominal on the reader's OWN categories."""
    NOMI = ("NOUN", "PROPN", "PRON")
    out = []
    for it in items:
        up, v0 = it["pos"], it["v"] - 1
        pre = [i for i in range(len(it["toks"])) if i < v0 and i < len(up) and up[i] in NOMI]
        out.append(int(bool(pre) and _norm(it["toks"][pre[-1]]) == it["gold"]))
    return np.array(out)


def paired_boot(a, b, groups, n_boot=2000, seed=SEED):
    """Item-paired bootstrap resampled over the read unit (the chunk), like the board's own."""
    rng = np.random.default_rng(seed)
    keys = sorted(set(groups))
    idx = {k: np.array([i for i, g in enumerate(groups) if g == k]) for k in keys}
    d = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(keys), len(keys))
        sel = np.concatenate([idx[keys[j]] for j in pick])
        d.append(float(a[sel].mean() - b[sel].mean()))
    d = np.array(d)
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"delta": _r4(a.mean() - b.mean()), "ci95": [_r4(lo), _r4(hi)],
            "ci_sep": bool(lo > 0.0 or hi < 0.0), "half_width": _r4((hi - lo) / 2.0)}


# ===================================================================================================
# SECTION 6 -- THE BUILD: cue validities ACCRUED FROM READING UD-EWT TRAIN.
# ===================================================================================================
# The counts come from READING: the same pseudo-documents, the same mention stream, the same perceived
# categories and the same clause scoping the reader uses at inference -- so a cue's availability at build
# time is its availability at read time.  The OUTCOME accrued is the gold agent of the clause (the
# comprehension outcome an English-learning reader eventually converges on); the SAME accrual function is
# what the online `observe_agent_outcome` calls with the reader's own settled agent, so the table is a
# running count, never a fit.
_TRAIN_CAP_DEFAULT = 3000
_TRAIN_CACHE = os.path.join(OUT_DIR, "capture_udtrain.pkl")


def get_train_capture(cap=_TRAIN_CAP_DEFAULT, chunk=CHUNK, refresh=False):
    import pickle
    if (not refresh) and os.path.exists(_TRAIN_CACHE):
        with open(_TRAIN_CACHE, "rb") as fh:
            d = pickle.load(fh)
        if d.get("cap") == cap and d.get("chunk") == chunk:
            print("  (train capture reused: %d items)" % len(d["items"]))
            return d["items"]
    items, _ns, _nc = capture(cap=cap, chunk=chunk, path_corpus=UD_TRAIN)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(_TRAIN_CACHE, "wb") as fh:
        pickle.dump({"cap": cap, "chunk": chunk, "items": items}, fh)
    return items


def accrue_from_items(items, gaz=None, graded=True, counts=None, w_conf=False):
    """Count every candidate of every gold agent clause.  Returns the counts dict."""
    counts = counts if counts is not None else empty_agent_counts()
    from hdlab.graded_role_assigner import mention_head_wpos
    n_obs = 0
    for it in items:
        if not it["cands"]:
            continue
        toks, up, v0 = it["toks"], it["pos"], it["v"] - 1
        freq = {}
        for k, vv in it["freq"].items():
            freq[k] = vv
            try:
                freq[int(k)] = vv
            except (TypeError, ValueError):
                pass
        hp = agent_head_belief(toks, up) if graded else None
        tp = agent_category_belief(toks) if graded else None
        c = [(mention_head_wpos(m), m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start")))
             for m in it["cands"]]
        cfgs, vals = agent_cue_values(toks, up, v0, c, gaz=gaz, cluster_freq=freq,
                                      head_post=hp, tag_post=tp)
        gold = it["gold"]
        for k, cd in enumerate(c):
            accrue_agent(counts, cfgs[k], vals[k], _norm(cd[1]) == gold, w=1.0)
            n_obs += 1
    counts["config_kind"] = AGENT_CONFIG
    counts["n_observations"] = int(counts.get("n_observations", 0)) + n_obs
    return counts


def build_validities(cap=_TRAIN_CAP_DEFAULT, chunk=CHUNK, out=None, refresh=False):
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    items = get_train_capture(cap=cap, chunk=chunk, refresh=refresh)
    counts = accrue_from_items(items, gaz=gaz, graded=True)
    counts["source"] = "UD-EWT TRAIN read through the live reader (%d sentences, %d-sentence pseudo-docs)" % (
        cap, chunk)
    tab = agent_table_from_counts(counts)
    p = save_agent_validities(out, tab)
    print("  validities accrued from %d candidate observations over %d gold agent clauses"
          % (counts["n_observations"], sum(1 for it in items if it["cands"])))
    for cfg, g in sorted(tab["strengths"].items()):
        n = counts["config"][cfg]["n"]
        print("  config %-5s  base rate P(agent) = %.4f   (%d candidates)" % (cfg, n[0] / max(1.0, n[1]), n[1]))
        for c in AGENT_CUES:
            t = g["cue"].get(c) or {}
            if not t:
                continue
            s = "  ".join("%s %+.2f" % (k, v) for k, v in sorted(t.items(), key=lambda kv: -kv[1]))
            print("      %-14s %s" % (c, s))
    print("  wrote %s" % os.path.relpath(p, _REPO))
    return tab


# ===================================================================================================
# SECTION 7 -- THE LIVE TWO-ARM GATE.  Both arms in ONE process, the reader re-read per arm.
# ===================================================================================================
class _reweighed_competition(object):
    """Swap the organ's `agent_competition_pick_conf` for the re-weighed arm for the duration of a read.
    The shipped form needs no swap at all (the diff puts the arm INSIDE the organ, self-gated on the asset);
    this is how the cell measures the arm BEFORE the diff lands and, once it has landed, still runs green."""

    def __init__(self, table, twin_seed=None, cue_set=None, graded=True):
        self.table, self.twin_seed, self.cue_set, self.graded = table, twin_seed, cue_set, graded
        self.saved = None

    def __enter__(self):
        import hdlab.graded_role_assigner as GRA
        mod, _src = _organ_or_local()
        self.saved = GRA.agent_competition_pick_conf
        T, TW, CS, GR = self.table, self.twin_seed, self.cue_set, self.graded

        def patched(toks, pos, v, cands, cluster_freq=None, weights=None, gaz=None, twin_seed=None,
                    subj_before=None, byhead_agent_cue=False):
            hp = agent_head_belief(toks, pos) if GR else None
            tp = agent_category_belief(toks) if GR else None
            return mod.agent_competition_reweighed(toks, pos, v, cands, cluster_freq=cluster_freq, gaz=gaz,
                                                   table=T, head_post=hp, tag_post=tp, twin_seed=TW,
                                                   cue_set=CS)
        GRA.agent_competition_pick_conf = patched
        return self

    def __exit__(self, *a):
        import hdlab.graded_role_assigner as GRA
        GRA.agent_competition_pick_conf = self.saved
        return False


def _run_board_rows(cap, chunk, n_boot, seed, tag):
    """The board's OWN UD-EWT rows (agent / patient / state) through the LIVE reader, per chunk, returning
    per-item hit vectors so the two arms can be paired item-by-item."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    sents = _ud_sents(cap)
    chunks = [sents[i:i + chunk] for i in range(0, len(sents), chunk)]
    agent_hit, agent_ent, agent_wrongent, groups = [], [], [], []
    pat_hit, pat_groups, st_hit, st_groups = [], [], [], []
    ans = {"agent_items": 0, "agent_answered": 0}
    tmp = tempfile.mkdtemp(prefix="p140m_")
    t0 = time.time()
    try:
        for ci, ch in enumerate(chunks):
            docid = "udewt%04d" % ci
            path = os.path.join(tmp, docid + ".conll")
            B._ud_write_chunk(ch, path, docid, discover_pronouns=False)
            rdr = SituationReader(gaz=gaz, **B.READER_KW)
            sm = rdr.read(path)
            ev_by = defaultdict(list)
            for e in sm.events:
                ev_by[(e.sent_idx, e.pred_idx)].append(e)
            for si, s in enumerate(ch):
                toks = [t["form"] for t in s]
                try:
                    up = list(rdr._cached_tag(list(toks)))
                except Exception:
                    up = ["X"] * len(toks)
                for (v, ag, passive) in B._gold_agent_items(s):
                    gold = _norm(toks[ag - 1])
                    evs = ev_by.get((si, v - 1), [])
                    model = _norm(evs[0].agent) if evs else ""
                    hit = int(bool(model) and model != "?" and model == gold)
                    ans["agent_items"] += 1
                    ans["agent_answered"] += int(bool(evs))
                    run = _name_run(s, ag)
                    forms = set(_norm(toks[i - 1]) for i in run if 1 <= i <= len(toks))
                    ent = hit or int(bool(model) and model != "?" and model in forms)
                    lab = (split_pick_error(s, toks, ag, model)[0]
                           if (model and model != "?" and not hit) else None)
                    agent_hit.append(hit)
                    agent_ent.append(int(bool(ent)))
                    agent_wrongent.append(int(lab == "wrong_entity"))
                    groups.append(docid)
                for (v, pt, passive) in B._gold_patient_items(s):
                    gold = _norm(toks[pt - 1])
                    evs = ev_by.get((si, v - 1), [])
                    model = _norm(evs[0].patient) if evs else ""
                    pat_hit.append(int(bool(model) and model != "?" and model == gold))
                    pat_groups.append(docid)
                import experiments.exp_copular_is_a_binding_readout_v1 as COP
                tup = [(t["id"], t["form"], t["form"], t["upos"], "", t["head"], t["deprel"]) for t in s]
                gs = [(h, p, ty) for (h, p, ty) in COP.typed_gold(tup) if ty in ("pred_adj", "pred_nom")]
                if gs:
                    mp = defaultdict(set)
                    for st in sm.entity_states:
                        if st.sent_idx == si:
                            mp[_norm(st.holder)].add(_norm(st.property))
                    for (h, p, ty) in gs:
                        st_hit.append(int(_norm(toks[p]) in mp.get(_norm(toks[h]), set())))
                        st_groups.append(docid)
            del sm, rdr
            os.remove(path)
            if (ci + 1) % 10 == 0:
                print("    [%s] ... %d/%d chunks, %.0fs" % (tag, ci + 1, len(chunks), time.time() - t0),
                      flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"agent": np.array(agent_hit), "agent_entity": np.array(agent_ent),
            "agent_wrong_entity": np.array(agent_wrongent), "groups": groups,
            "patient": np.array(pat_hit), "patient_groups": pat_groups,
            "state": np.array(st_hit), "state_groups": st_groups,
            "answered": ans, "elapsed_s": round(time.time() - t0, 1)}



# ===================================================================================================
# SECTION 9 -- THE DEV SPLIT (where every arm CHOICE is made) and the arm sweep.
# ===================================================================================================
# UD-EWT ships train + test only.  The validities are counted on TRAIN sentences [0, train_cap); every arm
# choice (which cues, graded or not, the accrual rate, the decision temperature) is made on a DEV slice of
# TRAIN that the counts never saw, [train_cap, train_cap + dev_n).  TEST is read once per reported arm.
_DEV_N = 1200
_DEV_CACHE = os.path.join(OUT_DIR, "capture_uddev.pkl")


def get_dev_capture(train_cap=None, dev_n=_DEV_N, chunk=CHUNK, refresh=False):
    import pickle
    train_cap = _TRAIN_CAP_DEFAULT if train_cap is None else train_cap
    key = (train_cap, dev_n, chunk)
    if (not refresh) and os.path.exists(_DEV_CACHE):
        with open(_DEV_CACHE, "rb") as fh:
            d = pickle.load(fh)
        if tuple(d.get("key", ())) == key:
            print("  (dev capture reused: %d items)" % len(d["items"]))
            return d["items"]
    items, _ns, _nc = capture(cap=train_cap + dev_n, chunk=chunk, path_corpus=UD_TRAIN, offset=train_cap)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(_DEV_CACHE, "wb") as fh:
        pickle.dump({"key": key, "items": items}, fh)
    return items


def _arm_report(items, picks, groups, floor_hits, label):
    sc = score_picks(items, picks)
    return {"arm": label, "n": int(len(items)),
            "token_acc": _r4(sc["tok"].mean()), "entity_acc": _r4(sc["ent"].mean()),
            "wrong_entity_pick_errors": int(sc["wrong_entity"].sum()),
            "vs_floor": paired_boot(sc["tok"], floor_hits, groups),
            "_v": sc}


def sweep_arms(items, table, gaz, n_boot=2000, label="dev"):
    """Every arm, replayed offline over one captured population.  This is where CHOICES are made (on dev)."""
    groups = [it["docid"] for it in items]
    floor = word_order_floor(items)
    live = np.array([int(it["fired"] and it["model"] == it["gold"]) for it in items])
    base = _arm_report(items, [it["model"] for it in items], groups, floor, "live_landed_read")
    rows = {"live_landed_read": base}
    rows["floor_word_order"] = {"arm": "floor_word_order", "n": int(len(items)),
                                "token_acc": _r4(floor.mean())}
    arms = [("reweigh_graded", dict(graded=True, cue_set=None, twin=None)),
            ("reweigh_ungraded", dict(graded=False, cue_set=None, twin=None)),
            ("all_12_cues", dict(graded=True, cue_set=tuple(AGENT_CUES), twin=None)),
            ("twin_within", dict(graded=True, cue_set=None, twin=SEED)),
            ("twin_across", dict(graded=True, cue_set=None, twin=SEED, mode="across"))]
    for c in AGENT_CUE_SET:
        arms.append(("drop_" + c,
                     dict(graded=True, cue_set=tuple(k for k in AGENT_CUE_SET if k != c), twin=None)))
    for name, kw in arms:
        picks = replay(items, table, arm="reweigh", gaz=gaz, twin_seed=kw.get("twin"),
                       cue_set=kw.get("cue_set"), graded=kw.get("graded", True),
                       permute_mode=kw.get("mode", "within"))
        rows[name] = _arm_report(items, picks, groups, floor, name)
    for k, r in rows.items():
        if "_v" in r and k != "live_landed_read":
            r["vs_landed"] = paired_boot(r["_v"]["tok"], base["_v"]["tok"], groups, n_boot=n_boot)
            r["wrong_entity_vs_landed"] = paired_boot(r["_v"]["wrong_entity"], base["_v"]["wrong_entity"],
                                                      groups, n_boot=n_boot)
    print("\n" + "=" * 100)
    print("ARM SWEEP -- %s population (n=%d items, floor %.4f, landed read %.4f)"
          % (label, len(items), floor.mean(), live.mean()))
    print("=" * 100)
    print("  %-22s %8s %8s %10s   %s" % ("arm", "token", "entity", "wrongent", "vs the landed read"))
    for k in ["live_landed_read", "reweigh_graded", "reweigh_ungraded", "twin_within", "twin_across"] + \
             ["drop_" + c for c in AGENT_CUES]:
        r = rows.get(k)
        if not r or "token_acc" not in r:
            continue
        vs = r.get("vs_landed")
        print("  %-22s %8.4f %8.4f %10d   %s"
              % (k, r["token_acc"], r.get("entity_acc", float("nan")),
                 r.get("wrong_entity_pick_errors", -1),
                 ("%+.4f %s%s" % (vs["delta"], vs["ci95"], "  CI-SEP" if vs["ci_sep"] else "")) if vs else ""))
    for r in rows.values():
        r.pop("_v", None)
    rows["_floor"] = _r4(floor.mean())
    return rows


def greedy_select(items, table, gaz, n_boot=1000, label="dev"):
    """BACKWARD ELIMINATION ON DEV ONLY.  Start from every cue, drop the one whose removal helps most, stop
    when nothing helps.  The chosen set is then read ONCE on test -- test never chooses anything."""
    groups = [it["docid"] for it in items]
    floor = word_order_floor(items)
    cur = list(AGENT_CUES)

    def acc(cs):
        return score_picks(items, replay(items, table, gaz=gaz, cue_set=tuple(cs)))["tok"].mean()

    best = acc(cur)
    print(chr(10) + "=" * 100)
    print("BACKWARD CUE SELECTION on %s (floor %.4f) -- every choice is made here, never on test"
          % (label, floor.mean()))
    print("=" * 100)
    print("  all %d cues: %.4f" % (len(cur), best))
    while len(cur) > 2:
        cand = []
        for c in cur:
            cand.append((acc([k for k in cur if k != c]), c))
        cand.sort(reverse=True)
        a, c = cand[0]
        if a <= best + 1e-9:
            break
        cur = [k for k in cur if k != c]
        best = a
        print("  drop %-14s -> %.4f  (%d cues left)" % (c, best, len(cur)))
    print("  CHOSEN: %s" % ", ".join(cur))
    v = score_picks(items, replay(items, table, gaz=gaz, cue_set=tuple(cur)))
    out = {"chosen": cur, "dropped": [c for c in AGENT_CUES if c not in cur],
           "dev_token_acc": _r4(best), "dev_floor": _r4(floor.mean()),
           "dev_vs_floor": paired_boot(v["tok"], floor, groups, n_boot=n_boot),
           "dev_wrong_entity": int(v["wrong_entity"].sum())}
    print("  dev vs floor: %+0.4f %s%s" % (out["dev_vs_floor"]["delta"], out["dev_vs_floor"]["ci95"],
                                           "   CI-SEPARATED" if out["dev_vs_floor"]["ci_sep"] else ""))
    return out


def run_select(chunk=CHUNK, n_boot=1000, train_cap=None, dev_n=_DEV_N):
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    mod, src = _organ_or_local()
    table = mod.load_agent_validities()
    if table is None:
        raise SystemExit("no validity asset -- run --build first")
    return greedy_select(get_dev_capture(train_cap=train_cap, chunk=chunk, dev_n=dev_n), table, gaz,
                         n_boot=n_boot)


def run_rate_sweep(chunk=CHUNK, n_boot=1000, train_cap=None, rates=(0.5, 2.0, 8.0, 32.0, 128.0, 512.0)):
    """THE ACCRUAL RATE, SWEPT ON DEV (the brief's one swept parameter).  `m_shrink` is how much experience a
    cue VALUE needs before it may outvote its own configuration: a large rate keeps a weak or redundant cue
    near-silent, which is the COUNT-BASED cure for correlated cues double-counting in an additive integrator.
    Nothing here is adopted from anywhere else -- the rate is chosen on dev and read once on test."""
    import copy
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    mod, _src = _organ_or_local()
    base = mod.load_agent_validities()
    if base is None:
        raise SystemExit("no validity asset -- run --build first")
    items = get_dev_capture(train_cap=train_cap, chunk=chunk)
    groups = [it["docid"] for it in items]
    floor = word_order_floor(items)
    print(chr(10) + "=" * 100)
    print("ACCRUAL-RATE SWEEP on dev (all %d cues, config=%s, floor %.4f)"
          % (len(AGENT_CUES), AGENT_CONFIG, floor.mean()))
    print("=" * 100)
    out = {}
    for r in rates:
        t = copy.deepcopy(base)
        t["counts"]["m_shrink"] = float(r)
        t["strengths"] = mod.agent_strengths_from_counts(t["counts"])
        v = score_picks(items, replay(items, t, gaz=gaz))
        b = paired_boot(v["tok"], floor, groups, n_boot=n_boot)
        out["m_shrink_%g" % r] = {"token_acc": _r4(v["tok"].mean()), "entity_acc": _r4(v["ent"].mean()),
                                  "wrong_entity": int(v["wrong_entity"].sum()), "vs_floor": b}
        print("  m_shrink %-6g token %.4f  entity %.4f  wrongent %4d   vs floor %+0.4f %s%s"
              % (r, v["tok"].mean(), v["ent"].mean(), v["wrong_entity"].sum(), b["delta"], b["ci95"],
                 "  CI-SEP" if b["ci_sep"] else ""))
    return {"dev_floor": _r4(floor.mean()), "config": AGENT_CONFIG, "rates": out}


def run_sweep(cap=UD_CAP, chunk=CHUNK, n_boot=2000, dev=True, train_cap=None, dev_n=_DEV_N):
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    gaz = load_given_gazetteer()
    mod, src = _organ_or_local()
    table = mod.load_agent_validities()
    if table is None:
        raise SystemExit("no validity asset -- run --build first")
    out = {"implementation": src}
    if dev:
        out["dev"] = sweep_arms(get_dev_capture(train_cap=train_cap, chunk=chunk, dev_n=dev_n), table, gaz,
                                n_boot=n_boot, label="UD-EWT TRAIN dev slice (the counts never saw it)")
    items, ns, nc = get_capture(cap=cap, chunk=chunk)
    out["test"] = sweep_arms(items, table, gaz, n_boot=n_boot,
                             label="UD-EWT TEST (%d sentences, %d chunks)" % (ns, nc))
    return out


# ===================================================================================================
# SECTION 10 -- THE LIVE GATE and THE PLASTICITY PROBE.
# ===================================================================================================
def run_measure(cap=UD_CAP, chunk=CHUNK, n_boot=2000, cue_set=None):
    """Both arms, LIVE, in ONE process: the landed competition and the re-weighed competition, each read by
    `SituationReader.read` on the annotation-free UD-EWT text, plus the info-free twin; agent / patient /
    state scored off the reader's own situation model."""
    mod, src = _organ_or_local()
    table = mod.load_agent_validities()
    if table is None:
        raise SystemExit("no validity asset -- run --build first")
    items, ns, nc = get_capture(cap=cap, chunk=chunk)
    floor = word_order_floor(items)
    print("\nLIVE ARM 1/3: the landed competition ...")
    A = _run_board_rows(cap, chunk, n_boot, SEED, "landed")
    print("LIVE ARM 2/3: the re-weighed competition ...")
    with _reweighed_competition(table, cue_set=cue_set):
        B = _run_board_rows(cap, chunk, n_boot, SEED, "reweigh")
    print("LIVE ARM 3/3: the info-free twin (the learned strengths permuted within each cue) ...")
    with _reweighed_competition(table, twin_seed=SEED, cue_set=cue_set):
        T = _run_board_rows(cap, chunk, n_boot, SEED, "twin")
    g = A["groups"]
    assert len(g) == len(B["groups"]) == len(T["groups"]) == len(floor), \
        "the three live arms must score the SAME population, item for item"
    rows = {
        "landed": {"agent": _r4(A["agent"].mean()), "agent_entity": _r4(A["agent_entity"].mean()),
                   "wrong_entity_pick_errors": int(A["agent_wrong_entity"].sum()),
                   "patient": _r4(A["patient"].mean()), "state": _r4(A["state"].mean()),
                   "n": int(len(A["agent"])), "elapsed_s": A["elapsed_s"]},
        "reweigh": {"agent": _r4(B["agent"].mean()), "agent_entity": _r4(B["agent_entity"].mean()),
                    "wrong_entity_pick_errors": int(B["agent_wrong_entity"].sum()),
                    "patient": _r4(B["patient"].mean()), "state": _r4(B["state"].mean()),
                    "n": int(len(B["agent"])), "elapsed_s": B["elapsed_s"]},
        "twin": {"agent": _r4(T["agent"].mean()), "agent_entity": _r4(T["agent_entity"].mean()),
                 "wrong_entity_pick_errors": int(T["agent_wrong_entity"].sum()),
                 "patient": _r4(T["patient"].mean()), "state": _r4(T["state"].mean()),
                 "n": int(len(T["agent"]))},
        "floor": {"agent": _r4(floor.mean()), "what": "nearest pre-verbal nominal on the reader's OWN "
                                                      "categories (the board's own agent floor)"},
    }
    con = {
        "agent_vs_floor": paired_boot(B["agent"], floor, g, n_boot=n_boot),
        "landed_agent_vs_floor": paired_boot(A["agent"], floor, g, n_boot=n_boot),
        "agent_reweigh_vs_landed": paired_boot(B["agent"], A["agent"], g, n_boot=n_boot),
        "agent_reweigh_vs_twin": paired_boot(B["agent"], T["agent"], g, n_boot=n_boot),
        "wrong_entity_reweigh_vs_landed": paired_boot(B["agent_wrong_entity"], A["agent_wrong_entity"],
                                                      g, n_boot=n_boot),
        "entity_reweigh_vs_landed": paired_boot(B["agent_entity"], A["agent_entity"], g, n_boot=n_boot),
    }
    nr = {"patient": paired_boot(B["patient"], A["patient"], A["patient_groups"], n_boot=n_boot),
          "state": paired_boot(B["state"], A["state"], A["state_groups"], n_boot=n_boot)}
    print("\n" + "=" * 100)
    print("LIVE TWO-ARM GATE -- UD-EWT test, %d sentences, both arms in ONE process" % ns)
    print("=" * 100)
    print("  %-10s %8s %8s %10s %9s %8s" % ("arm", "agent", "entity", "wrongent", "patient", "state"))
    for k in ("floor", "landed", "reweigh", "twin"):
        r = rows[k]
        print("  %-10s %8.4f %8s %10s %9s %8s"
              % (k, r["agent"],
                 ("%.4f" % r["agent_entity"]) if "agent_entity" in r else "-",
                 str(r.get("wrong_entity_pick_errors", "-")),
                 ("%.4f" % r["patient"]) if "patient" in r else "-",
                 ("%.4f" % r["state"]) if "state" in r else "-"))
    for k, v in con.items():
        print("  %-32s %+0.4f  CI95 %s%s" % (k, v["delta"], v["ci95"], "   CI-SEPARATED" if v["ci_sep"] else ""))
    for k, v in nr.items():
        print("  no-regress %-21s %+0.4f  CI95 %s%s" % (k, v["delta"], v["ci95"],
                                                        "   CI-SEPARATED" if v["ci_sep"] else ""))
    return {"rows": rows, "contrasts": con, "no_regress": nr, "implementation": src,
            "config": AGENT_CONFIG, "m_shrink": AGENT_M_SHRINK,
            "population": "UD-EWT test %d sentences in %d chunks, read annotation-free by SituationReader.read"
                          % (ns, nc), "answered": A["answered"], "cue_set": list(cue_set or AGENT_CUE_SET)}


def run_observe(chunk=CHUNK):
    """PLASTICITY: read document 1, let the competition OBSERVE its own comprehended agents, then show that
    document 2's decisions are taken with the updated counts -- and that the update is the direction the
    experience carried (a second read of document 1 is more confident about what it settled on)."""
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    mod, src = _organ_or_local()
    gaz = load_given_gazetteer()
    table = mod.load_agent_validities()
    if table is None:
        raise SystemExit("no validity asset -- run --build first")
    items, _ns, _nc = get_capture()
    docs = sorted(set(it["docid"] for it in items))
    d1 = [it for it in items if it["docid"] == docs[0]]
    d2 = [it for it in items if it["docid"] == docs[1]]
    import copy
    tab = copy.deepcopy(table)
    n0 = sum(g["n"][1] for g in tab["counts"]["config"].values())
    before2 = replay(d2, tab, arm="reweigh", gaz=gaz)
    m0 = [float(mod.agent_activation(tab, *_vals(it, gaz)).max()) for it in d2 if it["cands"]]
    for it in d1:
        if not it["cands"]:
            continue
        hp = agent_head_belief(it["toks"], it["pos"])
        tp = agent_category_belief(it["toks"])
        freq = _freq(it)
        pick = replay([it], tab, arm="reweigh", gaz=gaz)[0]
        mod.observe_agent_outcome(it["toks"], it["pos"], it["v"] - 1, it["cands"], pick, tab,
                                  gaz=gaz, cluster_freq=freq, head_post=hp, tag_post=tp)
    n1 = sum(g["n"][1] for g in tab["counts"]["config"].values())
    after2 = replay(d2, tab, arm="reweigh", gaz=gaz)
    m1 = [float(mod.agent_activation(tab, *_vals(it, gaz)).max()) for it in d2 if it["cands"]]
    changed = sum(1 for a, b in zip(before2, after2) if a != b)
    out = {"counts_before": _r4(n0), "counts_after": _r4(n1),
           "document_1_clauses_observed": sum(1 for it in d1 if it["cands"]),
           "document_2_items": len(d2), "document_2_decisions_changed_by_the_update": int(changed),
           "document_2_mean_top_activation_before": _r4(np.mean(m0) if m0 else 0.0),
           "document_2_mean_top_activation_after": _r4(np.mean(m1) if m1 else 0.0),
           "implementation": src}
    print("\nPLASTICITY PROBE (the table is counts, and reading updates them)")
    for k, v in out.items():
        print("  %-52s %s" % (k, v))
    assert n1 > n0, "reading document 1 must have grown the counts"
    return out




def run_exposure_curve(steps=(2, 5, 15, 50, 200, 1000, 4929), chunk=CHUNK, train_cap=None,
                       n_boot=1000):
    """PLASTIC, NOT FROZEN -- the demonstration that survived the honest version of the probe.

    THE PROBE THAT FAILED FIRST, and why it is worth recording: reading document 1 and observing the
    reader's OWN settled agent changes NO decision on document 2, from the shipped 29,191-count table
    (0.3% of the counts) AND from a 960-count cold start.  Self-supervised accrual is a FIXED POINT: the
    table is reinforced toward the argmax it already takes, so its argmax does not move.  That is a real
    property of the online path, not a bug in it -- an online teaching signal has to be a comprehension
    OUTCOME the competition did not itself produce (a later revision, a downstream correction), and the
    organ has no such signal yet.  It is named in SOLVED.md as the open end of bar 4.

    What DOES demonstrate that the validities are accrued from reading is the EXPOSURE CURVE: the same
    competition, the same cues, the same code, reading 25 / 100 / 400 / 1600 / 4929 clauses of UD-EWT
    TRAIN before it is asked, scored on UD-EWT TEST.  If the weights were hand-set the curve would be
    flat."""
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    mod, src = _organ_or_local()
    gaz = load_given_gazetteer()
    train = [t for t in get_train_capture(cap=(train_cap or _TRAIN_CAP_DEFAULT), chunk=chunk) if t["cands"]]
    items, ns, nc = get_capture()
    groups = [it["docid"] for it in items]
    floor = word_order_floor(items)
    rows = []
    prev = None
    for k in steps:
        counts = accrue_from_items(train[:k], gaz=gaz, graded=True)
        tab = mod.agent_table_from_counts(counts)
        picks = replay(items, tab, gaz=gaz)
        v = score_picks(items, picks)
        rows.append({"clauses_read": int(k),
                     "candidate_observations": int(counts["n_observations"]),
                     "token_acc": _r4(v["tok"].mean()),
                     "wrong_entity_pick_errors": int(v["wrong_entity"].sum()),
                     "decisions_changed_since_the_previous_step":
                         (None if prev is None else int(sum(1 for x, y in zip(prev, picks) if x != y)))})
        prev = picks
    print(chr(10) + "=" * 100)
    print("THE EXPOSURE CURVE -- the same competition, read on UD-EWT TEST (n=%d, floor %.4f) after reading "
          "N clauses" % (len(items), floor.mean()))
    print("=" * 100)
    for r in rows:
        print("  clauses read %5d (%6d candidate observations)  test %.4f   wrong-entity %4d   "
              "decisions changed since the previous step %s"
              % (r["clauses_read"], r["candidate_observations"], r["token_acc"],
                 r["wrong_entity_pick_errors"],
                 "-" if r["decisions_changed_since_the_previous_step"] is None
                 else r["decisions_changed_since_the_previous_step"]))
    assert rows[-1]["token_acc"] > rows[0]["token_acc"], \
        "reading more must make the competition better, or the weights are not learned from reading"
    assert any(r["decisions_changed_since_the_previous_step"] for r in rows[1:]), \
        "more experience must change what the competition decides"
    return {"population": "UD-EWT test n=%d in %d chunks" % (len(items), nc), "floor": _r4(floor.mean()),
            "steps": rows, "implementation": src}

def _freq(it):
    f = {}
    for k, vv in it["freq"].items():
        f[k] = vv
        try:
            f[int(k)] = vv
        except (TypeError, ValueError):
            pass
    return f


def _vals(it, gaz):
    c = [(mention_head_wpos(m), m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start")))
         for m in it["cands"]]
    cfgs, vals = agent_cue_values(it["toks"], it["pos"], it["v"] - 1, c, gaz=gaz, cluster_freq=_freq(it),
                                  head_post=agent_head_belief(it["toks"], it["pos"]),
                                  tag_post=agent_category_belief(it["toks"]))
    return cfgs, vals


# ===================================================================================================
# SECTION 11 -- THE PATCH.  The diff is GENERATED from the cell's own ORGAN BLOCK, so the code that
#              lands is byte-identical to the code that was measured (the fidelity guarantee pri 111
#              introduced and this cell reuses).
# ===================================================================================================
_BEGIN = "# <<<ORGAN BLOCK BEGIN"
_END = "# <<<ORGAN BLOCK END>>>"
PATCH_OUT = os.path.join(
    _REPO, "notes", "problems",
    "the_agent_competition_loses_with_the_right_answer_on_the_ballot_77_to_80_percent_of_agent_errors_"
    "on_sealed_and_test_text_are_pick_errors_split_wrong_entity_from_wrong_name_token_then_reweigh_the_cues",
    "agent_reweigh_patch.diff")

_WIRE_ANCHOR = '''    w = AGENT_VALIDITIES if weights is None else weights
    c = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in cands]
    if not c:
        return "?", None, None'''

_WIRE_NEW = '''    # pri 140 (2026-09-16): THE RE-WEIGHED ARM.  The AGENT cue weights above are HAND-SET; the Competition
    # Model says a cue's weight is its VALIDITY, accrued from exposure.  When the counts-accrued table is on
    # disk (`agent_validities()`) and the caller has not supplied its own weights, the competition is decided
    # by those learned log-odds contrasts instead -- same organ, same additive activation, same argmax, same
    # (pick, margin, conf) return shape.  HDLAB_AGENT_REWEIGH=0 restores this function byte-identically.
    if AGENT_REWEIGH and weights is None:
        _t = agent_validities()
        if _t is not None:
            return agent_competition_reweighed(toks, pos, v, cands, cluster_freq=cluster_freq, gaz=gaz,
                                               table=_t, head_post=agent_head_belief(toks, pos),
                                               tag_post=agent_category_belief(toks), twin_seed=twin_seed)
    w = AGENT_VALIDITIES if weights is None else weights
    c = [(m["wtok_start"], m["head"], m.get("cluster"), m.get("wtok_end", m.get("wtok_start"))) for m in cands]
    if not c:
        return "?", None, None'''

_ALL_OLD = '''           "purpose_cues", "purpose_complement_posterior", "observe_purpose_outcome",
           "load_purpose_validities", "save_purpose_validities", "PURPOSE_CLASSES"]'''
_ALL_NEW = '''           "purpose_cues", "purpose_complement_posterior", "observe_purpose_outcome",
           "load_purpose_validities", "save_purpose_validities", "PURPOSE_CLASSES",
           "AGENT_CUES", "AGENT_REWEIGH", "agent_cue_values", "empty_agent_counts", "accrue_agent",
           "agent_strengths_from_counts", "agent_table_from_counts", "agent_activation",
           "agent_competition_reweighed", "save_agent_validities", "load_agent_validities",
           "agent_validities", "observe_agent_outcome", "agent_head_belief", "agent_category_belief"]'''

_IMPORT_OLD = '''import json
import functools
import os'''
_IMPORT_NEW = '''import json
import functools
import math
import os'''

# --- the board scorer hunk: the ENTITY-LEVEL column bar 1 asks for, beside the token-level gate ---
_SCORER_OLD = '''            diag["agent_span_credit"] += int(bool(model) and model not in ("?",)
                                             and model in _subtree_forms(s, ag))'''
_SCORER_NEW = '''            diag["agent_span_credit"] += int(bool(model) and model not in ("?",)
                                             and model in _subtree_forms(s, ag))
            # pri 140 bar 1: THE ENTITY-LEVEL COLUMN.  UD heads a multi-word name on its FIRST token, so a
            # reader that answers `Schulman` for `Kori Schulman` has named the RIGHT INDIVIDUAL and the
            # head-string match calls it wrong.  This counts the gold agent's own NAME RUN (flat / compound /
            # goeswith, in either direction) as right.  It is a SCORING CONVENTION column reported BESIDE the
            # gate, never instead of it -- and it deliberately does NOT credit an NP-internal MODIFIER
            # (`the South Korean company` -> `Korean`), which is a real misread of which token names the thing.
            diag["agent_entity_credit"] += int(bool(model) and model not in ("?",)
                                               and model in _name_run_forms(s, ag))'''

_SCORER_FN_OLD = '''def _norm(x):
    return (str(x) or "").strip().lower()'''
_SCORER_FN_NEW = '''def _norm(x):
    return (str(x) or "").strip().lower()


_NAME_RUN_DEPS = ("flat", "goeswith", "compound")


def _name_run_forms(s, head_id):
    """The token FORMS of the gold NAME RUN containing `head_id` -- the tokens joined to it by flat /
    compound / goeswith in either direction, i.e. the other words of the same name.  pri 140 bar 1."""
    adj = defaultdict(set)
    for t in s:
        d = (t.get("deprel") or t.get("dep") or "").split(":")[0]
        if d in _NAME_RUN_DEPS and t["head"] > 0:
            adj[t["head"]].add(t["id"])
            adj[t["id"]].add(t["head"])
    seen, stack = set(), [head_id]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(adj.get(x, ()))
    by = {t["id"]: t for t in s}
    return set(_norm(by[i]["form"]) for i in seen if i in by)'''

_SCORER_EXTRA_OLD = '''                extra["instrument_span_credit"] = {
                    "acc_if_any_token_of_the_gold_ARGUMENT_counts":
                        _r4(d.get(key + "_span_credit", 0) / max(1, d.get(key + "_items", 1))),
                    "note": "an UPPER BOUND on what a bare head-string match costs the instrument; the row's "
                            "model_acc is the strict head match."}'''
_SCORER_EXTRA_NEW = '''                extra["instrument_span_credit"] = {
                    "acc_if_any_token_of_the_gold_ARGUMENT_counts":
                        _r4(d.get(key + "_span_credit", 0) / max(1, d.get(key + "_items", 1))),
                    "note": "an UPPER BOUND on what a bare head-string match costs the instrument; the row's "
                            "model_acc is the strict head match."}
                if key == "agent":
                    extra["entity_level_credit"] = {
                        "acc_if_any_token_of_the_gold_agent_NAME_RUN_counts":
                            _r4(d.get("agent_entity_credit", 0) / max(1, d.get("agent_items", 1))),
                        "note": "pri 140 bar 1. The UD convention heads a multi-word name on its FIRST token, "
                                "so `Schulman` for `Kori Schulman` names the right individual and the strict "
                                "head match scores it wrong. This column credits the gold agent's own NAME RUN "
                                "and NOTHING else -- an NP-internal modifier is still counted wrong. The "
                                "row's model_acc (the strict head match) REMAINS THE GATE."}'''


def _organ_block_text():
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    a = s.index(_BEGIN)
    a = s.index("\n", a) + 1
    b = s.index(_END)
    return s[a:b].rstrip("\n") + "\n"


def _udiff(path, old, new):
    import difflib
    rel = os.path.relpath(path, _REPO).replace(os.sep, "/")
    return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                        fromfile="a/" + rel, tofile="b/" + rel, n=3))


def emit_patch(out=None, check=True):
    """Build the unified diff for hdlab/graded_role_assigner.py + the board scorer and write it."""
    gra = os.path.join(_REPO, "hdlab", "graded_role_assigner.py")
    old = open(gra, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in old[:4000] else "\n"
    blk = _organ_block_text()
    header = ("\n\n"
              "# =====================================================================================\n"
              "# pri 140 -- THE AGENT CUE VALIDITIES, ACCRUED FROM READING (the re-weighed competition)\n"
              "# =====================================================================================\n"
              "# The AGENT weights above (`AGENT_VALIDITIES`) are HAND-SET, and the Competition Model says a\n"
              "# cue's weight IS its validity -- availability x reliability, accrued from exposure (MacWhinney,\n"
              "# Bates & Kliegl 1984).  This block is that accrual, in the SAME form the coarse role table\n"
              "# already uses (`strengths_from_counts`): counts in, log-odds contrasts out, one online observe\n"
              "# path, no fit.  It is self-gating: with no asset on disk `agent_validities()` returns None and\n"
              "# `agent_competition_pick_conf` is byte-identical to the landed competition.\n")
    def _n(t):
        return t.replace("\r\n", "\n")
    o = _n(old)
    assert o.count(_IMPORT_OLD) == 1 and o.count(_WIRE_ANCHOR) == 1 and o.count(_ALL_OLD) == 1, \
        "the organ has moved under this patch -- re-derive it before landing"
    new = o.replace(_IMPORT_OLD, _IMPORT_NEW)
    new = new.replace(_WIRE_ANCHOR, _WIRE_NEW)
    # the block goes BEFORE the whole `__all__` statement, never INSIDE its list literal (the first
    # draft inserted it between the list's head and its last two lines, and the patched organ then did
    # not compile; the sandbox apply-and-compile check in --self-test is what caught that).
    _ALL_HEAD = '__all__ = ["hybrid_role_patient"'
    assert new.count(_ALL_HEAD) == 1, "the organ's __all__ has moved under this patch"
    new = new.replace(_ALL_HEAD, header + blk + "\n\n" + _ALL_HEAD)
    new = new.replace(_ALL_OLD, _ALL_NEW)
    d1 = _udiff(gra, o, new)

    brd = os.path.join(_REPO, "experiments", "exp_board_rows_on_the_reader_v1.py")
    b_old = _n(open(brd, encoding="utf-8", newline="").read())
    assert (b_old.count(_SCORER_FN_OLD) == 1 and b_old.count(_SCORER_OLD) == 1
            and b_old.count(_SCORER_EXTRA_OLD) == 1), "the board scorer has moved under this patch"
    b_new = b_old.replace(_SCORER_FN_OLD, _SCORER_FN_NEW).replace(_SCORER_OLD, _SCORER_NEW) \
                 .replace(_SCORER_EXTRA_OLD, _SCORER_EXTRA_NEW)
    d2 = _udiff(brd, b_old, b_new)

    txt = d1 + d2
    p = out or PATCH_OUT
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(txt)
    ok = None
    if check:
        import subprocess
        r = subprocess.run(["git", "apply", "--check", "--ignore-whitespace", p], cwd=_REPO,
                           capture_output=True, text=True)
        ok = (r.returncode == 0)
        print("  git apply --check: %s%s" % ("OK" if ok else "FAILED", ("  " + r.stderr.strip()) if r.stderr else ""))
    print("  wrote %s (%d lines)" % (os.path.relpath(p, _REPO), txt.count("\n")))
    return {"path": os.path.relpath(p, _REPO), "git_apply_check": ok,
            "organ_block_lines": blk.count("\n"), "files": 2}

# ===================================================================================================
# SECTION 8 -- SELF-TEST + MAIN
# ===================================================================================================
def self_test():
    ok = [True]

    def ck(name, cond, extra=""):
        ok[0] = ok[0] and bool(cond)
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))

    print("SELF-TEST exp_agent_pick_reweigh_v1 (no sealed file is read, listed or opened)")
    mod, src = _organ_or_local()
    print("  competition implementation in use: %s" % src)

    # (1) THE SPLIT can tell the three cases apart, and CAN FAIL.
    # UD puts a name's head FIRST, so the gold agent id is 1 and `Schulman` is the same individual.
    sent = [{"id": 1, "form": "Kori", "upos": "PROPN", "head": 2, "deprel": "nsubj", "dep": "nsubj"},
            {"id": 2, "form": "Schulman", "upos": "PROPN", "head": 1, "deprel": "flat", "dep": "flat"},
            {"id": 3, "form": "wrote", "upos": "VERB", "head": 0, "deprel": "root", "dep": "root"},
            {"id": 4, "form": "Obama", "upos": "PROPN", "head": 3, "deprel": "obj", "dep": "obj"}]
    toks = [t["form"] for t in sent]
    ck("a second token of the gold NAME is 'right entity, wrong token'",
       split_pick_error(sent, toks, 1, "Schulman")[0] == "right_entity_name_token")
    ck("a different entity is 'wrong entity'", split_pick_error(sent, toks, 1, "Obama")[0] == "wrong_entity")
    sent2 = [{"id": 1, "form": "the", "upos": "DET", "head": 3, "deprel": "det", "dep": "det"},
             {"id": 2, "form": "Korean", "upos": "ADJ", "head": 3, "deprel": "amod", "dep": "amod"},
             {"id": 3, "form": "company", "upos": "NOUN", "head": 4, "deprel": "nsubj", "dep": "nsubj"},
             {"id": 4, "form": "said", "upos": "VERB", "head": 0, "deprel": "root", "dep": "root"}]
    ck("an NP-internal modifier is 'right NP, wrong token' (NOT a name-run convention artifact)",
       split_pick_error(sent2, [t["form"] for t in sent2], 3, "Korean")[0] == "right_np_modifier")

    # (2) The validity math is a PURE FUNCTION of the counts, and availability silences a rare value.
    c = empty_agent_counts()
    for _ in range(200):
        accrue_agent(c, "act", {"order": "pre"}, True)
    for _ in range(200):
        accrue_agent(c, "act", {"order": "post"}, False)
    accrue_agent(c, "act", {"order": "weird"}, True)
    S = agent_strengths_from_counts(c)["act"]["cue"]["order"]
    ck("a reliable cue value earns a positive contrast", S["pre"] > 0.3, "pre %+.3f" % S["pre"])
    ck("an anti-reliable cue value earns a negative contrast", S["post"] < -0.3, "post %+.3f" % S["post"])
    ck("a value seen ONCE is shrunk toward silence (availability)", abs(S["weird"]) < abs(S["pre"]),
       "weird %+.3f vs pre %+.3f" % (S["weird"], S["pre"]))
    ck("the strengths are a pure function of the counts (rebuild == build)",
       agent_strengths_from_counts(json.loads(json.dumps(c))) == agent_strengths_from_counts(c))

    # (3) THE ONLINE PATH moves the table (plastic, never frozen).
    tab = agent_table_from_counts(c)
    before = json.dumps(tab["strengths"], sort_keys=True)
    n_before = sum(g["n"][1] for g in tab["counts"]["config"].values())
    cands = [{"wtok_start": 0, "head": "dog", "cluster": 1, "wtok_end": 0},
             {"wtok_start": 3, "head": "cat", "cluster": 2, "wtok_end": 3}]
    observe_agent_outcome(["dog", "and", "the", "cat", "ran"], ["NOUN", "CCONJ", "DET", "NOUN", "VERB"],
                          4, cands, "dog", tab)
    ck("one observed clause changes the learned strengths (there IS an observe path)",
       json.dumps(tab["strengths"], sort_keys=True) != before)
    ck("the counts grew",
       sum(g["n"][1] for g in tab["counts"]["config"].values()) > n_before)

    # (4) The competition runs and returns a candidate head.
    h, m, cf = agent_competition_reweighed(["dog", "and", "the", "cat", "ran"],
                                           ["NOUN", "CCONJ", "DET", "NOUN", "VERB"], 4, cands, table=tab)
    ck("the re-weighed competition returns one of its own candidates", h in ("dog", "cat"), "pick %r" % h)
    ck("it also returns a margin in [0,1)", m is not None and 0.0 <= m < 1.0)

    # (5) THE INFO-FREE TWIN is a real destruction: permuting the learned tables ACROSS cues changes picks.
    big = empty_agent_counts()
    rng = random.Random(7)
    for _ in range(4000):
        pre = rng.random() < 0.5
        v = {"order": "pre" if pre else "post", "anim": rng.choice(["anim", "inanim", "unk"])}
        accrue_agent(big, "act", v, pre)
    bt = agent_table_from_counts(big)
    vals = [{"order": "pre", "anim": "inanim"}, {"order": "post", "anim": "anim"}]
    a0 = agent_activation(bt, "act", vals)
    a1 = agent_activation(bt, "act", vals, permute_seed=3)
    a2 = agent_activation(bt, "act", vals, permute_seed=3, permute_mode="across")
    ck("the twin permutation reaches the activation (it is not a no-op)",
       not np.allclose(a0, a1), "%s vs within %s vs across %s"
       % (np.round(a0, 3), np.round(a1, 3), np.round(a2, 3)))
    ck("the within-cue twin keeps the SHAPE (same multiset of strengths per cue)",
       sorted(np.round(np.abs(a1), 6)) != sorted(np.round(np.abs(a2), 6)) or np.allclose(a2, 0.0))

    # (6) The graded upstream reads work on a real sentence and are graded (not 0/1).
    tk = ["The", "company", "that", "he", "runs", "makes", "chips", "."]
    tg = ["DET", "NOUN", "PRON", "PRON", "VERB", "VERB", "NOUN", "PUNCT"]
    hp = agent_head_belief(tk, tg)
    tp = agent_category_belief(tk)
    ck("the attachment arm hands back a GRADED head belief", bool(hp) and any(
        0.0 < p < 1.0 for row in hp.values() for p in row.values()))
    ck("the category organ hands back a GRADED category posterior", tp is not None and any(
        0.0 < float(r.get("NOUN", 0.0)) < 1.0 for r in tp))

    # (7) The cue values are computed and the graded cues actually vary.
    cfg, vv = agent_cue_values(tk, tg, 4, [(1, "company", 1, 1), (3, "he", 2, 3), (6, "chips", 3, 6)],
                               head_post=hp, tag_post=tp)
    ck("the configuration is per-candidate and names the clause voice",
       all(str(x).split("|")[0] in ("act", "pass") for x in cfg), cfg)
    ck("every declared cue takes a value on every candidate",
       all(set(d) == set(AGENT_CUES) for d in vv), sorted(vv[0]))
    ck("the structure cue is graded across candidates (not one constant)",
       len(set(d["struct"] for d in vv)) > 1, [d["struct"] for d in vv])

    # (8) The witness's landed-state detector names a real module.
    ck("the organ/cell detector names a real module", hasattr(mod, "agent_competition_reweighed"))

    # (9) THE PATCH IS THE CODE THAT WAS MEASURED, AND IT COMPILES AND RUNS.  The diff is GENERATED from the
    # ORGAN BLOCK above, applied to a COPY of the two target files in a sandbox, compiled, imported and asked
    # a question -- so "the diff is what I measured" is a check, not a claim.  hdlab/ is never written.
    import importlib.util
    import shutil
    import subprocess
    d = emit_patch(out=os.path.join(OUT_DIR, "selftest_patch.diff"), check=False)
    tmp = tempfile.mkdtemp(prefix="p140st_")
    try:
        for rel in ("hdlab/graded_role_assigner.py", "experiments/exp_board_rows_on_the_reader_v1.py"):
            os.makedirs(os.path.join(tmp, os.path.dirname(rel)), exist_ok=True)
            shutil.copy(os.path.join(_REPO, rel), os.path.join(tmp, rel))
        r = subprocess.run(["git", "apply", "--ignore-whitespace", os.path.join(OUT_DIR, "selftest_patch.diff")],
                           cwd=tmp, capture_output=True, text=True)
        ck("the generated patch APPLIES to the tree as it stands", r.returncode == 0, r.stderr.strip()[:120])
        gp = os.path.join(tmp, "hdlab", "graded_role_assigner.py")
        src = open(gp, encoding="utf-8").read()
        bsrc = open(os.path.join(tmp, "experiments", "exp_board_rows_on_the_reader_v1.py"),
                    encoding="utf-8").read()
        ok_c = True
        try:
            compile(src, gp, "exec")
            compile(bsrc, "board", "exec")
        except SyntaxError as e:
            ok_c = False
            print("        %s" % e)
        ck("both patched files COMPILE", ok_c)
        blk = _organ_block_text().rstrip("\n")
        ck("the patched organ contains the measured ORGAN BLOCK byte-for-byte",
           blk in src.replace("\r\n", "\n"))
        ck("the board scorer gains the entity-level column beside the token-level gate",
           "_name_run_forms" in bsrc and "entity_level_credit" in bsrc and "agent_entity_credit" in bsrc)
        spec = importlib.util.spec_from_file_location("p140_patched_gra", gp)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        toks = ["The", "company", "of", "Fallujah", "condemned", "it", "."]
        pos = ["DET", "NOUN", "ADP", "PROPN", "VERB", "PRON", "PUNCT"]
        cands = [{"wtok_start": 1, "head": "company", "cluster": 1, "wtok_end": 1},
                 {"wtok_start": 3, "head": "Fallujah", "cluster": 2, "wtok_end": 3}]
        os.environ["HDLAB_AGENT_VALIDITIES"] = _AGENT_VALIDITIES_PATH
        m._AGENT_VALIDITIES_PATH = _AGENT_VALIDITIES_PATH
        m._AGENT_TABLE_CACHE[0] = False
        got = m.agent_competition_pick_conf(toks, pos, 4, cands)[0]
        ck("THE DEFECT, ON THE SHIPPED PATH: the patched organ picks the NP HEAD, not the postmodifier "
           "inside it (`The company OF FALLUJAH condemned it`)", got == "company", "picked %r" % got)
        off = m.agent_competition_pick_conf(toks, pos, 4, cands, weights=m.AGENT_VALIDITIES)[0]
        ck("and the landed hand-set competition -- the A/B arm -- still picks the postmodifier, so the "
           "check CAN FAIL", off == "Fallujah", "picked %r" % off)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("SELF-TEST " + ("PASS" if ok[0] else "FAIL"))
    return ok[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--anatomy", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--observe", action="store_true")
    ap.add_argument("--emit-patch", action="store_true")
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--rate-sweep", action="store_true")
    ap.add_argument("--dev-n", type=int, default=_DEV_N)
    ap.add_argument("--cap", type=int, default=UD_CAP)
    ap.add_argument("--train-cap", type=int, default=_TRAIN_CAP_DEFAULT)
    ap.add_argument("--chunk", type=int, default=CHUNK)
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--no-dev", action="store_true")
    ap.add_argument("--cues", default="")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.self_test or a.smoke:
        raise SystemExit(0 if self_test() else 1)
    M = {"ts_iso": _now(), "anchor": ANCHOR}
    did = False
    if a.anatomy:
        items, ns, nc = get_capture(cap=a.cap, chunk=a.chunk, refresh=a.refresh)
        M["anatomy_udtest"] = anatomy_from_items(
            items, "UD-EWT TEST (the board's own read split, %d sentences in %d chunks)" % (ns, nc))
        did = True
    if a.build:
        M["build"] = {"cap": a.train_cap, "asset": os.path.relpath(_AGENT_VALIDITIES_PATH, _REPO)}
        tab = build_validities(cap=a.train_cap, chunk=a.chunk, refresh=a.refresh)
        M["build"]["n_observations"] = tab["counts"]["n_observations"]
        did = True
    if a.rate_sweep:
        M["rate_sweep"] = run_rate_sweep(chunk=a.chunk, n_boot=a.n_boot, train_cap=a.train_cap)
        did = True
    if a.select:
        M["select"] = run_select(chunk=a.chunk, n_boot=a.n_boot, train_cap=a.train_cap, dev_n=a.dev_n)
        did = True
    if a.sweep:
        M["sweep"] = run_sweep(cap=a.cap, chunk=a.chunk, n_boot=a.n_boot, dev=not a.no_dev,
                               train_cap=a.train_cap, dev_n=a.dev_n)
        did = True
    if a.measure:
        M["measure"] = run_measure(cap=a.cap, chunk=a.chunk, n_boot=a.n_boot,
                                   cue_set=(tuple(a.cues.split(",")) if a.cues else None))
        did = True
    if a.observe:
        M["observe"] = run_observe(chunk=a.chunk)
        M["exposure_curve"] = run_exposure_curve(chunk=a.chunk, train_cap=a.train_cap)
        did = True
    if a.emit_patch:
        M["patch"] = emit_patch()
        did = True
    if not did:
        ap.print_help()
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "metrics%s.json" % (("_" + a.tag) if a.tag else "")
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
        json.dump(M, fh, indent=2, default=str)
    print("\nwrote %s" % os.path.relpath(os.path.join(OUT_DIR, name), _REPO))


if __name__ == "__main__":
    main()
