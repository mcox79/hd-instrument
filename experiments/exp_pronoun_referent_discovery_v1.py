"""exp_pronoun_referent_discovery_v1 -- OPEN A DISCOURSE REFERENT FOR EVERY PRONOUN THE CATEGORY ORGAN TAGS,
and feed ONE discovered stream to every consumer.

problem: the_reader_discovers_no_pronoun_from_text_every_pronoun_agent_and_anaphora_question_comes_from_the_
         annotation_column_open_a_referent_for_every_pronoun_in_the_one_introduction_organ_and_feed_one_
         stream_to_every_consumer   (priority 125)

THE DEFECT (verified on disk, then first-hand here).  `hdlab/referent_per_np.referent_per_np_source` opens a
discourse referent per content-noun head and takes its PRONOUNS from `hdlab/coref.parse_litbank_conll` -- the
input's COREF ANNOTATION COLUMN (`NEVER_HEAD` holds PRON, so the discovery loop can never open one).  With the
column blank the reader therefore has NO pronoun mentions:
  * `situation_reader._cm_agent_candidates` returns (None, None) on an empty `_coref_mentions` -> the
    Competition-Model AGENT is skipped and the positional fallback sees no pronoun candidate;
  * `build_pronoun_targets` schedules a pronoun only after a prior mention with the SAME GOLD CLUSTER ID ->
    zero anaphora questions on annotation-free text, and no record that any were missed.

THE BRAIN (the opening move).  A pronoun is a referent-introducing expression like any other NP: it opens a
discourse referent (Kamp 1981 DRT / Heim 1982 FCS) whose file card is nearly EMPTY except for a RETRIEVAL
DEMAND -- it must be identified with an accessible prior referent by content-addressable, cue-based retrieval
(Lewis & Vasishth 2005 ACT-R; McElree direct access), the cues being the form's own phi-features
(person/gender/number) plus animacy (Garnham 2001), over the salient forward-looking centers (Grosz-Joshi-
Weinstein Centering).  When nothing accessible matches, the referent STAYS OPEN -- an explicit abstention, not
a missing question.  PINNED: introduction-per-NP, the phi/animacy retrieval cue, Centering accessibility.
OUR-INVENTION: the discrete file-card record, the exact accessibility window (SWEPT, never adopted).

WHAT THIS CELL DOES.  It measures the proposed ORGAN CHANGE through the LIVE `SituationReader().read()` with
the reader UNPATCHED ON DISK: every arm is installed by rebinding module attributes inside this process (the
pri-116 harness pattern), so `notes/problems/<slug>/pronoun_discovery_patch.diff` is the landed form of
exactly what ran here.

ARMS
  ship        as it ships (pronouns from the annotation column; nothing on text-only)
  disc_role   pronoun discovery inside `referent_per_np_source` ONLY (the role/entity stream)
  disc        THE PROPOSAL: discovery + ONE stream (`_coref_mentions` == the discovered stream) + discovered
              pronoun targets (every 3rd-person pronoun with an accessible phi-compatible prior referent;
              an explicit ABSTENTION record with the target's token position when there is none) + the
              retrieval-cue-filtered anaphora pool + gold-alignment moved to the SCORER side
  twin        `disc` with the phi-feature table PERMUTED across pronoun forms -- identical machinery, identical
              counts, information-free about WHICH pronoun agrees with WHICH referent.  It must LOSE.

ROWS
  --repro          the five UD-EWT test documents of the evaluation appendix A2/A8, its exact scorer
  --invariance     the annotation triple (text-only / blank column / permuted cluster ids) -> byte-identity
  --agents N       N-document seeded random sample of UD-EWT test: agent / patient / state, doc-paired
                   bootstrap, floors recomputed on each arm's own population
  --pronouns N     the reader's OWN pronoun instrument on MODERN GUM test text (gold = the answer key only):
                   every 3rd-person pronoun with a gold antecedent, ABSTENTION = WRONG, floors = nearest-prior
                   -compatible-referent and the word-order agent
  --window-sweep   the accessibility window (the one free parameter on the phase diagram)

Glass-box: no spaCy, no nltk tagger, no supervised parser, no external LLM at inference.  UD-EWT and GUM are
MODERN gold and enter the SCORER only.
Run:  .venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --repro
      .venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --invariance
      .venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --agents 40
      .venv/Scripts/python.exe experiments/exp_pronoun_referent_discovery_v1.py --pronouns 16
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import argparse
import json
import random
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

SEED = 20260915
UD_TEST = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
N_BOOT = 2000


def get_output_dir(default_name: str = "pronoun_referent_discovery_v1"):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = os.path.join(_REPO, "data", "exp_" + name)
    os.makedirs(d, exist_ok=True)
    return d


OUT_DIR = get_output_dir()


# =====================================================================================================
# 1. THE PHI-FEATURE TABLE OF THE CLOSED PRONOUN CLASS -- the form's own features, nothing learned here.
#    Composed from the organs that already hold them so there is ONE table, not a new one:
#      hdlab.state_of_mind.PRONOUN_SCOPE          3rd-person gender/number
#      hdlab.affected_entity_resolver.REFLEXIVE_GN reflexives (Binding Principle A)
#      hdlab.state_of_mind.FIRST/SECOND_PERSON_PRONOUNS  the discourse-participant deixis classes
#    A form the category organ tags PRON that is in NO table opens a referent with phi UNKNOWN (an open
#    retrieval demand with no cue) -- the organ decides pronoun-hood, the lexicon supplies the features.
# =====================================================================================================
def build_phi_table():
    from hdlab.state_of_mind import (PRONOUN_SCOPE, FIRST_PERSON_PRONOUNS, SECOND_PERSON_PRONOUNS)
    from hdlab.affected_entity_resolver import REFLEXIVE_GN
    phi = {}
    for f, d in PRONOUN_SCOPE.items():
        phi[f] = {"gender": d["gender"], "number": d["number"], "person": "third"}
    for f, (g, n) in REFLEXIVE_GN.items():
        phi[f] = {"gender": g, "number": n, "person": "third"}
    # 3rd-person forms the scope table omits (theirs / whose are possessive, oneself handled above)
    phi.setdefault("theirs", {"gender": "any", "number": "plural", "person": "third"})
    for f in FIRST_PERSON_PRONOUNS:
        phi[f] = {"gender": None, "number": ("plural" if f.startswith(("we", "us", "our")) else "singular"),
                  "person": "first"}
    for f in SECOND_PERSON_PRONOUNS:
        phi[f] = {"gender": None, "number": None, "person": "second"}
    # demonstratives used as an NP: neuter, number from the form
    for f, n in (("this", "singular"), ("that", "singular"), ("these", "plural"), ("those", "plural")):
        phi[f] = {"gender": "neuter", "number": n, "person": "third"}
    return phi


PHI = None            # lazily built (imports hdlab); permuted in the twin arm
_PHI_SHIP = None


def phi_of(form):
    global PHI
    if PHI is None:
        PHI = build_phi_table()
    return PHI.get(form.lower().strip(".,'\"!?;:"))


_SCOPE_SHIP = None


def _twin_scope(seed=SEED):
    """THE CONTROL DEFECT THIS FIXES (phase 7 item 1a, found by reading the pick): the reader's anaphora pick
    re-derives the probe's features from `hdlab/state_of_mind.py` PRONOUN_SCOPE at
    `hdlab/event_centrality_coref.py:358` -- the SURFACE-FORM table -- not from the mention dict this cell
    writes.  So permuting only `PRONOUN_PHI` left the PICK's agreement cue untouched, and the twin could not
    lose: it was an INVALID control, not evidence that the cue is inert.  Permute PRONOUN_SCOPE too."""
    global _SCOPE_SHIP
    import hdlab.state_of_mind as SOM
    if _SCOPE_SHIP is None:
        _SCOPE_SHIP = {k: dict(v) for k, v in SOM.PRONOUN_SCOPE.items()}
    rng = random.Random(seed + 1)
    keys = sorted(_SCOPE_SHIP)
    gn = [(_SCOPE_SHIP[k]["gender"], _SCOPE_SHIP[k]["number"]) for k in keys]
    rng.shuffle(gn)
    for k, (g, n) in zip(keys, gn):
        SOM.PRONOUN_SCOPE[k]["gender"] = g
        SOM.PRONOUN_SCOPE[k]["number"] = n


def _restore_scope():
    import hdlab.state_of_mind as SOM
    if _SCOPE_SHIP is not None:
        for k, v in _SCOPE_SHIP.items():
            SOM.PRONOUN_SCOPE[k]["gender"] = v["gender"]
            SOM.PRONOUN_SCOPE[k]["number"] = v["number"]


def install_twin_phi(seed=SEED):
    """INFORMATION-FREE TWIN (the AGREEMENT CUE): permute the gender/number pairs ACROSS the pronoun forms
    WITHIN each person class.  Same forms discovered, same mention counts, the same number of scheduled
    anaphora questions, the same retrieval machinery -- only WHICH referent each pronoun agrees with is
    scrambled.  (Permuting `person` too would delete the question set instead of scrambling the cue, which
    would make the twin a coverage ablation rather than an information-free control.)"""
    global PHI, _PHI_SHIP
    if PHI is None:
        PHI = build_phi_table()
    if _PHI_SHIP is None:
        _PHI_SHIP = dict(PHI)
    rng = random.Random(seed)
    new = {k: dict(v) for k, v in _PHI_SHIP.items()}
    byperson = defaultdict(list)
    for k, v in _PHI_SHIP.items():
        byperson[v.get("person")].append(k)
    for person, keys in byperson.items():
        keys = sorted(keys)
        gn = [(_PHI_SHIP[k].get("gender"), _PHI_SHIP[k].get("number")) for k in keys]
        rng.shuffle(gn)
        for k, (g, n) in zip(keys, gn):
            new[k]["gender"] = g
            new[k]["number"] = n
    PHI = new
    _twin_scope(seed)


def restore_ship_phi():
    global PHI
    if _PHI_SHIP is not None:
        PHI = dict(_PHI_SHIP)
    _restore_scope()


THIRD_PERSON_TARGETS = None      # built from PHI at call time (person == third and gender/number known)


def is_anaphora_target_form(form):
    d = phi_of(form)
    if d is None or d.get("person") != "third":
        return False
    # a RETRIEVAL DEMAND needs at least one agreement cue to retrieve with
    return bool(d.get("gender")) or bool(d.get("number"))


# =====================================================================================================
# 2. THE INTRODUCTION ARM -- a discourse referent for every PRON the category organ tags, in reading order.
# =====================================================================================================
POSSESSIVE_FORMS = frozenset({"my", "your", "his", "her", "its", "our", "their", "whose"})


def _pron_mention(form_low, sent_idx, wpos, cluster, upos):
    d = phi_of(form_low) or {}
    return {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
            "wtok_start": wpos, "head": form_low, "is_pronoun": True,
            "gender": d.get("gender"), "number": d.get("number"), "name_gender": None,
            "span_toks": [form_low], "midx": -1, "span_upos": [upos or "PRON"],
            "person": d.get("person"), "discovered": True}


TWIN_POS = {"on": False, "seed": SEED}


def _infer_gender(head_low):
    from hdlab.state_of_mind import infer_nominal_gender
    return infer_nominal_gender([head_low])


def _infer_number(head_low, upos):
    if upos not in ("NOUN", "PROPN"):
        return None
    try:
        from hdlab.morphology import default_morphology
        base = default_morphology().morphy(head_low, "n")
    except Exception:
        return None
    if base and base != head_low:
        return "plural"
    if base == head_low and not head_low.endswith("s"):
        return "singular"
    return None


def discovered_pronoun_source(conll_path, tagger, name_gender_map=None, use_frame=True,
                              keep_possessive=True, fill_card=True):
    """`referent_per_np_source` + THE PRONOUN ARM.  Identical to the shipped organ except that the pronoun
    mentions come from the CATEGORY ORGAN's PRON tags on the reader's own tokens (in reading order, one
    sentence at a time), not from the coref annotation column.  Returns the same schema."""
    import hdlab.referent_per_np as RNP
    from hdlab.scene_segment import parse_conll_sentences
    from hdlab.coref import parse_litbank_conll

    coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=name_gender_map, tagger=tagger)
    sents = parse_conll_sentences(conll_path, lower=False)
    coref_head_wpos = {}
    for m in coref:
        if m["is_pronoun"]:
            continue
        span = max(0, m["gtok_end"] - m["gtok_start"])
        coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    next_cluster = max([m["cluster"] for m in coref], default=-1) + 1
    out = []
    pron = []
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        mat = None
        if hasattr(tagger, "tag_with_posterior"):
            try:
                _c, mat = tagger.tag_with_posterior(list(toks))
            except Exception:
                mat = None
        _tags = None
        if mat is not None:
            from hdlab import frontend as _F
            _lc = getattr(_F.tagger(), "_lc", None)
            _tags = list(_lc.tags) if _lc is not None else None
        base = RNP._content_head_positions(toks, up)
        heads = sorted(set(base) | RNP.frame_heads(toks, up, set(base))) if use_frame else list(base)
        # -- THE PRONOUN ARM: the closed class the organ tags, in reading order --------------------
        found = []
        for wi, w in enumerate(toks):
            if up[wi] != "PRON":
                continue
            wl = w.lower()
            if (not keep_possessive) and wl in POSSESSIVE_FORMS:
                continue
            found.append((wi, wl))
        if TWIN_POS["on"] and found:
            # INFORMATION-FREE POSITION TWIN: the SAME NUMBER of pronoun referents in this sentence, opened
            # at RANDOM token positions instead of where the category organ says a pronoun is.  Same counts,
            # same forms, same machinery -- information-free about WHICH token is the pronoun.
            rr = random.Random((TWIN_POS["seed"] * 7919 + si * 104729 + len(toks)) & 0x7FFFFFFF)
            slots = rr.sample(range(len(toks)), min(len(found), len(toks)))
            found = [(p, f) for p, (_w, f) in zip(sorted(slots), found)]
        pron_pos = set()
        for wi, wl in found:
            cl = next_cluster
            next_cluster += 1
            pron.append(_pron_mention(wl, si, wi, cl, up[wi] if wi < len(up) else "PRON"))
            pron_pos.add(wi)
        for hw in heads:
            if hw in pron_pos:
                continue
            cl = coref_head_wpos.get((si, hw))
            if cl is None:
                cl = next_cluster
                next_cluster += 1
            _m = RNP._mk_referent(toks[hw].lower(), si, hw, cl, -1,
                                  upos=up[hw] if hw < len(up) else None,
                                  tag_post=(mat[hw] if (mat is not None and hw < len(mat) and _tags)
                                            else None),
                                  tags=_tags)
            if fill_card:
                # THE FILE CARD, FILLED AT INTRODUCTION (the measured root cause of the inert phi cue):
                # `_mk_referent` writes gender/number/name_gender = None on every referent, so every
                # downstream cue that retrieves BY AGREEMENT is inert against the reader's own referents.
                _u = up[hw] if hw < len(up) else None
                _m["gender"] = _infer_gender(toks[hw].lower())
                _m["number"] = _infer_number(toks[hw].lower(), _u)
                if _m["gender"] is None and name_gender_map and _u == "PROPN":
                    from hdlab.coref import name_gender_for_span
                    _m["name_gender"] = name_gender_for_span([toks[hw].lower()], name_gender_map)
            out.append(_m)
    return RNP._finalize(pron + out), n_sents


# =====================================================================================================
# 3. THE RETRIEVAL ORGAN'S SIDE -- the accessible pool, the discovered targets, the abstention record.
# =====================================================================================================
ACCESS_WINDOW = int(os.environ.get("HDLAB_PRON_WINDOW", "0") or 0)     # 0 = whole passage (no window)


def _phi_compatible(target, cand):
    """The retrieval cue: agreement between the pronoun probe's phi-features and the candidate referent's.
    UNKNOWN on either side does NOT block (the brain retrieves on the cues it has; abstaining on unknown
    gender would delete most common-noun antecedents)."""
    tg, tn = target.get("gender"), target.get("number")
    cg = cand.get("gender") or cand.get("name_gender")
    cn = cand.get("number")
    if tg and cg and tg != "any" and cg != "any" and tg != cg:
        return False
    if tn and cn and tn != cn:
        return False
    return True


POOL_STRICT = {"on": False}


def _person_evidence(m, animacy_cache):
    """Is there POSITIVE evidence that this referent can be picked out by a gendered personal pronoun?
    MEASURED DEFECT THIS FIXES (this cell, 8 annotated GUM documents): admitting every PROPN as a person
    candidate derailed 32 of 38 pronoun resolutions -- `she` bound `youtube` in eleven consecutive
    sentences, because a company name is a PROPN with no gender cue and `lookup_animacy` returns None for
    most proper nouns, so nothing blocked it.  That is the 2026-09-03 pool-flood recurring in a milder
    form.  The brain's constraint is the ANIMACY cue on pronoun interpretation (Garnham 2001, PINNED): an
    inanimate referent is NOT RETRIEVABLE by `he`/`she`.  The glass-box evidence available to the reader is
    (1) a gender cue from the form/title (`infer_nominal_gender`), (2) the given-name gazetteer
    (`name_gender`), (3) the animacy lexicon.  A proper noun with NONE of the three is not evidence of a
    person, so it leaves the gendered-pronoun pool.  This COSTS recall on person names the gazetteer does
    not know -- an entity-TYPE knowledge gap with a brief already filed
    (`acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref`), not a mechanism gap."""
    if m.get("gender") or m.get("name_gender"):
        return True
    h = m["head"].lower()
    if h in animacy_cache:
        return animacy_cache[h]
    from hdlab.animacy_lexicon import lookup_animacy
    up = (m.get("span_upos") or [""])[-1]
    try:
        rec = lookup_animacy(h, up or "NOUN")
    except Exception:
        rec = None
    ok = bool(rec) and rec.get("animacy") == "animate"
    animacy_cache[h] = ok
    return ok


def _animate_or_featured(m, animacy_cache):
    """Is this referent in the pronoun-retrievable pool at all?  The 2026-09-03 collapse (coref 0.469 ->
    0.102) was caused by flooding the anaphora pool with FEATURE-BLANK singleton referents.  The brain's
    filter is the retrieval cue itself: a pronoun probe carries [+gender/+number/+ANIMATE] and an inanimate
    'table' is simply not retrievable by 'he' (Garnham 2001).  Keep: pronouns; referents with a gender cue;
    NAME-typed referents (person candidates); referents the animacy lexicon calls animate."""
    if m.get("is_pronoun"):
        return True
    if POOL_STRICT["on"]:
        return _person_evidence(m, animacy_cache)
    if m.get("gender") or m.get("name_gender"):
        return True
    up = (m.get("span_upos") or [""])[-1]
    if up == "PROPN":
        return True
    h = m["head"].lower()
    if h in animacy_cache:
        return animacy_cache[h]
    from hdlab.animacy_lexicon import lookup_animacy
    try:
        rec = lookup_animacy(h, "NOUN")
    except Exception:
        rec = None
    ok = bool(rec) and rec.get("animacy") == "animate"
    animacy_cache[h] = ok
    return ok


def anaphora_pool(mentions, animacy_cache=None):
    ac = animacy_cache if animacy_cache is not None else {}
    return [m for m in mentions if _animate_or_featured(m, ac)]


def discovered_pronoun_targets(mentions, window=None):
    """Schedule an anaphora question for every THIRD-PERSON pronoun in the DISCOVERED stream that has an
    accessible, phi-compatible PRIOR referent.  Returns (targets, abstentions):
      targets      the parse_litbank_conll target schema, `antecedent` = the NEAREST prior compatible
                   referent (the FLOOR's pick; a schema slot, never the resolver's answer)
      abstentions  one record per third-person pronoun with NO accessible compatible prior referent --
                   the referent stays OPEN.  {head, sent_idx, wtok_start}
    `window` = the accessibility window in sentences (0/None = the whole passage so far)."""
    win = ACCESS_WINDOW if window is None else window
    targets, abstain = [], []
    prior = []
    for m in mentions:
        if m.get("is_pronoun") and is_anaphora_target_form(m["head"]):
            cands = [p for p in prior
                     if (not p.get("is_pronoun"))
                     and (not win or (m["sent_idx"] - p["sent_idx"]) <= win)
                     and _phi_compatible(m, p)]
            if cands:
                nearest = cands[-1]
                targets.append({"target": m, "antecedent": nearest,
                                "midx_dist": m["midx"] - nearest["midx"],
                                "sent_dist": m["sent_idx"] - nearest["sent_idx"]})
            else:
                abstain.append({"head": m["head"], "sent_idx": m["sent_idx"],
                                "wtok_start": m["wtok_start"]})
        prior.append(m)
    return targets, abstain


# =====================================================================================================
# 4. THE ARM INSTALLER -- rebinding only; hdlab/ is untouched on disk.
# =====================================================================================================
_GOLD_BY_PATH = {}        # conll_path -> {"pos": {(si,wp): cluster}, "head": {head: set(cluster)}}
_DISC_CACHE = {}          # (path, arm_token) -> (mentions, n_sents)
# READ THIS BEFORE INTERPRETING AN ARM ON A PATCHED TREE.  An arm in `DELEGATED` is a configuration of the
# LANDED organ and means exactly what its name says.  An arm NOT in `DELEGATED` is installed by rebinding, so
# once the diff is applied it COMPOSES WITH the landed organ rather than replacing it -- e.g. `disc_role`
# ("discovery in the introduction organ only") was a real ablation before the diff landed and is NOT one
# afterwards, because the landed `read()` supplies the one-stream flip and the graded pick underneath it.
# The pre/post ablations that remain valid on a patched tree are the FLAG switches: ship (pre-patch),
# disc_blankcard (fill_card=False), landed_overlay_pick (graded_anaphora=False).
ARMS = ("ship", "disc_role", "disc", "twin", "twin_pos", "disc_actr", "disc_freq", "disc_case",
        "disc_nopos", "disc_full", "disc_posagent", "disc_freq2", "disc_case_freq2",
        "disc_case_hybrid", "disc_case_hybridc",
        # the DERAILMENT repair (the annotated-path no-regress leg): the gendered-pronoun pool requires
        # POSITIVE person evidence, and the accessibility window is swept
        "disc_strict", "disc_case_strict", "disc_case_strict_w2", "disc_case_strict_w3",
        "disc_actr_strict",
        # PHASE 7 item 2a: the pick as ACT-R cue-based retrieval with a GRADED phi cue sum, every
        # third-person pronoun attempted, accessibility bounded at RETRIEVAL, Principle A/B, impletion
        "disc_graded", "disc_graded_twin", "disc_graded_nophi", "disc_graded_nowin", "disc_graded_nopb",
        "disc_graded_w1", "disc_graded_w3", "disc_graded_w5", "disc_graded_all", "disc_blankcard",
        "disc_graded_g", "disc_graded_g8", "disc_graded_best", "disc_graded_best_twin",
        "disc_graded_best_nophi", "disc_graded_best_nowin", "disc_graded_best_loose",
        "disc_case_pv6", "disc_case_pv9", "disc_case_pv14",
        # names that exist ONLY as configurations of the landed organ (see DELEGATED); on an unpatched tree
        # they fall back to the plain reader, which is what makes them meaningless there and legal here.
        "landed", "landed_overlay_pick")
# reader keyword overrides per arm (the arm is still the same organ; these isolate a DOWNSTREAM consumer)
# PHASE 7 item 2c: the POSITIONAL cue's weight inside the competition.  `graded_role_assigner.py:265-267`
# sets AGENT_VALIDITIES = {"preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0,
# "adjacency": 1.0, "byagent": 6.0, ...} and its own comment says it is "a STATIC asset ... hand-set from cue
# validity, NOT trained" (and the module's __bf_status__ note says "agent weights hand-set").  So the
# word-order cue's validity was never estimated from ANY register -- not 19c, not gold heads, not the organ's
# own decisions: it is a constant, and the three non-positional cues sum to 6.0 against its 3.0, which is
# how a correct word-order pick gets outvoted on modern canonical prose.  These arms sweep it.
def _detect_live_patched():
    """True when the pri-125 diff is APPLIED to hdlab/ -- the live organ then carries the pronoun arm, the
    discovered question set and the graded pick natively.  In that case this cell must NOT monkeypatch: the
    arms are configurations of the LANDED reader (see DELEGATED), so the self-test and every row measure the
    organ as it actually ships.  On an unpatched tree the overlay installs the same computation by
    rebinding, so both paths work from one file."""
    try:
        import inspect as _i
        import hdlab.coref as _CO
        import hdlab.referent_per_np as _RNP
        import hdlab.situation_reader as _SR
        return bool(hasattr(_RNP, "PRONOUN_PHI") and hasattr(_CO, "discovered_pronoun_targets")
                    and "discover_pronouns" in _i.signature(_SR.SituationReader.__init__).parameters)
    except Exception:
        return False


_LIVE = None
_LIVE_PHI_SHIP = None
_LIVE_SCOPE_SHIP = None


def live_patched():
    global _LIVE
    if _LIVE is None:
        _LIVE = _detect_live_patched()
    return _LIVE


# the PRE-PATCH organ, expressed as flags on the landed reader (the A/B that reproduces the old behaviour)
PRE_PATCH_KW = {"discover_pronouns": False, "fill_card": False, "graded_anaphora": False,
                "case_cue_marked": False}
# arm -> the LANDED reader configuration that IS that arm; no monkeypatch needed for these
DELEGATED = {
    "ship": dict(PRE_PATCH_KW),
    "disc": {"graded_anaphora": False, "case_cue_marked": False},
    "disc_case": {"graded_anaphora": False},
    "disc_graded_best": {},
    "disc_graded_best_nowin": {},
    "landed": {},
    "disc_blankcard": {"fill_card": False},
    "landed_overlay_pick": {"graded_anaphora": False},
}
# arms that differ ONLY by the permuted phi tables (not expressible as a flag)
DELEGATED_TWIN = {"twin": {}, "disc_graded_twin": {}, "disc_graded_best_twin": {}}


def _twin_live_on():
    """Permute the phi tables the LANDED organ actually reads: `referent_per_np.PRONOUN_PHI` (discovery and
    question scheduling) AND `state_of_mind.PRONOUN_SCOPE` (what the shipped pick re-derives from at
    `event_centrality_coref.py:358`).  Permuting only one of them was the control defect this cell found."""
    global _LIVE_PHI_SHIP, _LIVE_SCOPE_SHIP
    import hdlab.referent_per_np as _RNP
    import hdlab.state_of_mind as _SOM
    if _LIVE_PHI_SHIP is None:
        _LIVE_PHI_SHIP = {k: dict(v) for k, v in _RNP.PRONOUN_PHI.items()}
        _LIVE_SCOPE_SHIP = {k: dict(v) for k, v in _SOM.PRONOUN_SCOPE.items()}
    rng = random.Random(SEED)
    byp = defaultdict(list)
    for k, v in _LIVE_PHI_SHIP.items():
        byp[v.get("person")].append(k)
    for _pp, ks in byp.items():
        ks = sorted(ks)
        gn = [(_LIVE_PHI_SHIP[k]["gender"], _LIVE_PHI_SHIP[k]["number"]) for k in ks]
        rng.shuffle(gn)
        for k, (g, n) in zip(ks, gn):
            _RNP.PRONOUN_PHI[k] = dict(_LIVE_PHI_SHIP[k], gender=g, number=n)
    ks = sorted(_LIVE_SCOPE_SHIP)
    gn = [(_LIVE_SCOPE_SHIP[k]["gender"], _LIVE_SCOPE_SHIP[k]["number"]) for k in ks]
    random.Random(SEED + 1).shuffle(gn)
    for k, (g, n) in zip(ks, gn):
        _SOM.PRONOUN_SCOPE[k]["gender"] = g
        _SOM.PRONOUN_SCOPE[k]["number"] = n


def _twin_live_off():
    import hdlab.referent_per_np as _RNP
    import hdlab.state_of_mind as _SOM
    if _LIVE_PHI_SHIP is None:
        return
    for k, v in _LIVE_PHI_SHIP.items():
        _RNP.PRONOUN_PHI[k] = dict(v)
    for k, v in _LIVE_SCOPE_SHIP.items():
        _SOM.PRONOUN_SCOPE[k]["gender"] = v["gender"]
        _SOM.PRONOUN_SCOPE[k]["number"] = v["number"]


def reader_kw(arm):
    """The reader kwargs for `arm`.  On a PATCHED tree a delegated arm is purely a configuration of the
    landed organ; on an unpatched tree the flags do not exist and only ARM_READER_KW applies."""
    kw = dict(ARM_READER_KW.get(arm, {}))
    if live_patched():
        if arm in DELEGATED:
            kw.update(DELEGATED[arm])
        elif arm in DELEGATED_TWIN:
            kw.update(DELEGATED_TWIN[arm])
    return kw


_AV = {"preverbal": 3.0, "core_arg": 2.0, "animacy": 2.0, "salience": 2.0, "adjacency": 1.0,
       "byagent": 6.0}
ARM_READER_KW = {"disc_posagent": {"cm_agent": False},
                 "disc_case_pv6": {"cm_weights": dict(_AV, preverbal=6.0)},
                 "disc_case_pv9": {"cm_weights": dict(_AV, preverbal=9.0)},
                 "disc_case_pv14": {"cm_weights": dict(_AV, preverbal=14.0)},
                 # the ALREADY-BUILT hybrid of the positional cue and the cue competition (default OFF):
                 # the principled arm for "the word-order cue outranks the competition on this
                 # construction", tested rather than re-weighted by hand.
                 "disc_case_hybrid": {"agent_hybrid": True},
                 "disc_case_hybridc": {"agent_hybrid": True, "agent_hybrid_construction": True}}
# COMPOSABLE DOWNSTREAM-CONSUMER LEVERS (phase 4).  Each is a repair to a consumer of the discovered
# stream, measurable on its own and in combination:
#   freq   the Centering GIVENNESS count, recomputed from the reader's OWN head-individuated files
#   case   the Competition-Model CASE cue as an ACCUSATIVE EXCLUSION instead of a nominative allow-list
#   nopos  possessive pronoun referents dropped from the AGENT candidate set (not a core argument)
LEVERS = {"disc_freq": ("freq",), "disc_case": ("case",), "disc_nopos": ("nopos",),
          "disc_full": ("freq", "case", "nopos"),
          # freq2 = the STRONGER form of the freq lever (the false-negative audit, phase 5b-vi): counting by
          # head string makes every `he` in the passage ONE head, so the pronoun count is a count of the
          # FORM, not of the referent -- which is why `freq` lost.  Count NON-pronoun mentions only, which is
          # the Centering Cf count of the referents that actually have an identity.
          "disc_freq2": ("freq2",), "disc_case_freq2": ("case", "freq2"),
          "disc_case_hybrid": ("case",), "disc_case_hybridc": ("case",),
          "disc_case_pv6": ("case",), "disc_case_pv9": ("case",), "disc_case_pv14": ("case",),
          "disc_case_strict": ("case",), "disc_case_strict_w2": ("case",),
          "disc_case_strict_w3": ("case",)}
STRICT_ARMS = frozenset({"disc_strict", "disc_case_strict", "disc_case_strict_w2", "disc_case_strict_w3",
                         "disc_actr_strict"})
# the GRADED-retrieval arms and their ablations (each isolates ONE term of the activation equation)
GRADED = {
    "disc_graded":       dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True,
                              w_num=1.0),
    "disc_graded_g":     dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True,
                              w_num=0.0),
    "disc_graded_g8":    dict(window=2, w_phi=8.0, w_focus=1.0, principle_b=True,  strict_person=True,
                              w_num=0.0),
    # THE CORRECTED CONFIGURATION (phase 7): gender-only agreement (number is violable and `they` is
    # ambiguous), accessibility bounded at retrieval, and NO rank-based Principle-B proxy -- my proxy
    # excluded every same-sentence core-ranked mention, which is not the clause-mate CO-ARGUMENT relation
    # and cost -0.104 on 67 questions.  Principle B is PINNED and stays a live lead; what is refuted here is
    # MY PROXY for it, not the constraint.
    "disc_graded_best":  dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=False, strict_person=True,
                              w_num=0.0),
    "disc_graded_best_twin": dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=False,
                                  strict_person=True, w_num=0.0),
    "disc_graded_best_nophi": dict(window=2, w_phi=0.0, w_focus=1.0, principle_b=False,
                                   strict_person=True, w_num=0.0),
    "disc_graded_best_nowin": dict(window=0, w_phi=4.0, w_focus=1.0, principle_b=False,
                                   strict_person=True, w_num=0.0),
    "disc_graded_best_loose": dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=False,
                                   strict_person=False, w_num=0.0),
    "disc_graded_twin":  dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True,
                              w_num=0.0),
    "disc_graded_nophi": dict(window=2, w_phi=0.0, w_focus=1.0, principle_b=True,  strict_person=True),
    "disc_graded_nowin": dict(window=0, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True),
    "disc_graded_nopb":  dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=False, strict_person=True),
    "disc_graded_all":   dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=False),
    "disc_graded_w1":    dict(window=1, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True),
    "disc_graded_w3":    dict(window=3, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True),
    "disc_graded_w5":    dict(window=5, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True),
    # the FILE-CARD ablation: the same graded pick over BLANK cards (the pre-patch introduction organ)
    "disc_blankcard":    dict(window=2, w_phi=4.0, w_focus=1.0, principle_b=True,  strict_person=True),
}
ARM_WINDOW = {"disc_case_strict_w2": 2, "disc_case_strict_w3": 3}
# English marks the OBLIQUE member of the case opposition; every other pronoun form is case-NEUTRAL and can
# head a subject.  `graded_role_assigner.NOMINATIVE_PRON` is an ALLOW-LIST of 8 forms, so a case-neutral
# subject pronoun (an indefinite `anybody`, a demonstrative `that`, `one`) is thrown out of the AGENT
# competition even though nothing marks it as non-subject.  The informative cue is the MARKED member.
ACCUSATIVE_MARKED = frozenset({"me", "him", "her", "us", "them", "whom", "thee", "hers", "theirs",
                               "mine", "ours", "yours", "myself", "yourself", "himself", "herself",
                               "itself", "ourselves", "yourselves", "themselves"})


# ---------------------------------------------------------------------------------------------------
# THE QUALITY PUSH (phase 4): the RETRIEVAL rung.  `disc` hands the discovered question to the reader's
# overlay pick (`EventCentralityReader.resolve_stream`).  The organ that already holds the PINNED
# retrieval mathematics -- ACT-R base-level activation B_i = ln SUM_k w(role_k)*(t_now - t_k)^-d over the
# entity's reference history, Centering Cf role prominence as w, the event-model FOREGROUND window,
# Binding Principle A for reflexives, and the impletion accrual that writes every resolved pronoun back
# into its referent's history -- is `hdlab/affected_entity_resolver.EntityTokens`, and it is INCREMENTAL
# (it takes the mentions in reading order, one at a time; pri 112's discipline).  ONE BRAIN STRUCTURE =
# ONE ORGAN: cue-based retrieval over discourse referents is one structure, so the discovered stream
# should be retrieved by THAT organ, not by a second pick rule.  This arm routes it there.
# ---------------------------------------------------------------------------------------------------
NUMBER_AMBIGUOUS = frozenset({"they", "them", "their", "theirs", "themselves"})


def graded_resolve(mentions, targets, gold=None, window=2, w_phi=4.0, w_focus=1.0, decay=2.0,
                   strict_person=True, principle_b=True, all_third=True, w_num=None):
    """THE ANAPHORA PICK AS ACT-R CUE-BASED RETRIEVAL WITH A GRADED CUE-MATCH SUM (phase 7 item 2a).

    WHAT WAS WRONG WITH THE TWO ARMS BEFORE THIS ONE, both located in code:
      (1) `event_centrality_coref.py:355` enters the retrieval branch ONLY for
          `m["head"] in TARGET_PRONOUNS` = {he, him, his, she, her, hers} -- SIX forms.  Every `it`, `they`,
          `them`, `their`, `this`, `that` target is scheduled and then never attempted, which is the
          coverage number (98 of 334 questions answered), not my pool.
      (2) `event_centrality_coref.py:358` reads the probe's features from `state_of_mind.PRONOUN_SCOPE[head]`
          -- the SURFACE-FORM table -- not from the mention's own `gender`/`number`.  So a pool of discovered
          referents is retrieved over by an unbounded document-wide candidate set (no accessibility bound at
          RETRIEVAL; the window I first added bounded target SCHEDULING instead, which is the wrong place).

    THE BRAIN'S FORM, replicated: retrieval activation is
        A(cand) = ln SUM_k w(role_k) * (t_now - t_k)^(-d)        [ACT-R base level; Anderson & Schooler]
                  + w_phi * phi_match(probe, cand)                [the retrieval CUE VECTOR, graded, not a filter]
                  + w_focus * 1[cand is the previous utterance's Cb]  [Centering forward-looking centre]
    with w(role) = Centering Cf prominence (SUBJECT > OBJECT > other), candidates bounded by the event-model
    FOREGROUND (accessibility window, SWEPT), Principle A for reflexives and Principle B excluding the
    clause-mate co-argument, and IMPLETION: a resolved pronoun is written into its referent's history so the
    next activation sees it.  phi_match is +1 on a known agreement match, 0 on unknown, -1 on a mismatch --
    a GRADED SUM, so the agreement cue is load-bearing and an information-free permutation of it must LOSE.
    Fully incremental (one pass, reading order).  Returns (records, abstentions)."""
    from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE
    from hdlab.affected_entity_resolver import is_reflexive
    tgt_by_midx = {t["target"]["midx"] for t in targets}
    hist = defaultdict(list)          # key -> [(order, role)]
    last_sent = {}                    # key -> last sentence it was referred to in
    feats = {}                        # key -> (gender, number)
    rank_in_sent = defaultdict(dict)  # sent -> {key: sent_role_rank}
    prev_subject = [None]             # the previous sentence's first-mentioned entity (Centering Cb proxy)
    cur_sent = [None]
    anim_cache = {}
    recs, abstain = [], []
    for m in mentions:
        order = float(m["midx"])
        si = int(m["sent_idx"])
        if cur_sent[0] is not None and si != cur_sent[0]:
            first = sorted(rank_in_sent[cur_sent[0]].items(), key=lambda kv: kv[1])
            if first:
                prev_subject[0] = first[0][0]
        cur_sent[0] = si
        role = "SUBJECT" if m.get("sent_role_rank", 99) == 0 else (
            "OBJECT" if m.get("sent_role_rank", 99) == 1 else "OTHER")
        if not m.get("is_pronoun"):
            k = m["head"].lower()
            hist[k].append((order, role))
            last_sent[k] = si
            g = m.get("gender") or m.get("name_gender")
            if k not in feats or feats[k] == (None, None):
                feats[k] = (g, m.get("number"))
            elif g and not feats[k][0]:
                feats[k] = (g, feats[k][1])
            rank_in_sent[si].setdefault(k, m.get("sent_role_rank", 99))
            continue
        if m["midx"] not in tgt_by_midx:
            continue
        pg, pn = m.get("gender"), m.get("number")
        # (a) ACCESSIBILITY at RETRIEVAL -- the event-model foreground
        cands = [k for k, s in last_sent.items() if (not window) or (si - s) <= window]
        if strict_person and pg in ("masc", "fem"):
            cands = [k for k in cands
                     if _person_evidence({"head": k, "gender": feats.get(k, (None, None))[0],
                                          "name_gender": None, "span_upos": ["NOUN"]}, anim_cache)]
        if not cands:
            abstain.append({"head": m["head"], "sent_idx": si, "wtok_start": m["wtok_start"]})
            continue
        # (b) BINDING PRINCIPLE A / B
        coarg = [k for k, r in rank_in_sent[si].items()
                 if r in (0, 1) and r != m.get("sent_role_rank", 99)]
        if is_reflexive(m.get("head")) and coarg:
            legal = [k for k in cands if k in coarg] or cands
        elif principle_b and coarg:
            legal = [k for k in cands if k not in coarg] or cands
        else:
            legal = cands
        # (c) THE GRADED CUE SUM
        best, bs = None, -1e18
        for k in legal:
            a = actr_activation(hist[k], order, decay=decay, role_prominence=ROLE_PROMINENCE)
            if a == float("-inf"):
                a = -1e9
            cg, cn = feats.get(k, (None, None))
            gmatch = 0.0
            if pg and cg and pg != "any" and cg != "any":
                gmatch = 1.0 if pg == cg else -1.0
            nmatch = 0.0
            # NUMBER IS A VIOLABLE CUE IN MODERN ENGLISH and the `they` family is number-AMBIGUOUS
            # (singular `they`; a collective read of an organisation).  Applying a -1 number mismatch to it
            # at the gender weight pushed every `they` off its true singular/collective antecedent --
            # MEASURED: the joint cue scored 0.1493 against 0.1791 with the cue off, on 67 GUM questions.
            # Gender is the reliable agreement cue in English; number enters at its own (lower) weight and
            # not at all for the ambiguous family.
            if pn and cn and m["head"].lower() not in NUMBER_AMBIGUOUS:
                nmatch = 1.0 if pn == cn else -1.0
            wn = w_phi if w_num is None else w_num
            s = (a + w_phi * gmatch + wn * nmatch
                 + w_focus * (1.0 if k == prev_subject[0] else 0.0))
            if s > bs:
                bs, best = s, k
        if best is None:
            abstain.append({"head": m["head"], "sent_idx": si, "wtok_start": m["wtok_start"]})
            continue
        # (d) IMPLETION: the resolved pronoun is itself a presentation of that referent
        hist[best].append((order, role))
        last_sent[best] = si
        rec = {"pronoun": m["head"], "sent_idx": si, "target_wpos": m["wtok_start"],
               "resolved_head": best, "n_cands": len(legal), "correct": False, "gold_cluster": -1,
               "sent_dist": max(0, si - last_sent.get(best, si))}
        if gold is not None:
            gc = gold["pos"].get((si, m["wtok_start"]))
            rc = gold["head"].get(best.lower(), set())
            rec["gold_cluster"] = -1 if gc is None else gc
            rec["correct"] = bool(gc is not None and gc in rc)
        recs.append(rec)
    return recs, abstain


def actr_resolve_discovered(mentions, targets, gold=None, window=None):
    """Retrieve every discovered anaphora question with the ACT-R object-file organ, in reading order.
    Returns (records, abstentions).  Each record: {pronoun, sent_idx, target_wpos, resolved_head,
    n_cands, correct, gold_cluster}.  `gold` = the scorer-side alignment map ({"pos":..., "head":...});
    it is read AFTER the pick, never before -- no decision touches it."""
    from hdlab.affected_entity_resolver import EntityTokens, ROLE_OF_RANK, is_reflexive
    from hdlab.state_of_mind import infer_nominal_gender
    tgt_by_midx = {t["target"]["midx"]: t for t in targets}
    et = EntityTokens()
    recs, abstain = [], []
    for m in mentions:
        order = float(m["midx"])
        sent = float(m["sent_idx"])
        role = ROLE_OF_RANK.get(m.get("sent_role_rank", 99), "OTHER")
        if not m.get("is_pronoun"):
            g = m.get("gender") or m.get("name_gender") or infer_nominal_gender(m.get("span_toks") or
                                                                                [m["head"]])
            et.observe(m["head"].lower(), order, role, sent, gender=g, number=m.get("number"), dep="",
                       payload=m)
            continue
        if m["midx"] not in tgt_by_midx:
            continue
        pick, n_c = et.resolve_pronoun(order, sent, gender=m.get("gender"), number=m.get("number"),
                                       role=role, reflexive=is_reflexive(m.get("head")))
        if pick is None:
            abstain.append({"head": m["head"], "sent_idx": m["sent_idx"],
                            "wtok_start": m["wtok_start"]})
            continue
        rec = {"pronoun": m["head"], "sent_idx": m["sent_idx"], "target_wpos": m["wtok_start"],
               "resolved_head": str(pick), "n_cands": n_c, "correct": False, "gold_cluster": -1,
               "sent_dist": m["sent_idx"] - tgt_by_midx[m["midx"]]["antecedent"]["sent_idx"]}
        if gold is not None:
            gc = gold["pos"].get((m["sent_idx"], m["wtok_start"]))
            rc = gold["head"].get(str(pick).lower(), set())
            rec["gold_cluster"] = -1 if gc is None else gc
            rec["correct"] = bool(gc is not None and gc in rc)
        recs.append(rec)
    return recs, abstain


def _stash_gold(conll_path, mentions):
    pos, head = {}, defaultdict(set)
    for m in mentions:
        pos[(m["sent_idx"], m["wtok_start"])] = m["cluster"]
        head[m["head"].lower()].add(m["cluster"])
        span = max(0, m["gtok_end"] - m["gtok_start"])
        pos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    _GOLD_BY_PATH[conll_path] = {"pos": pos, "head": dict(head)}


class Arm:
    """Install one arm for the duration of a `with` block."""

    def __init__(self, arm, window=None, keep_possessive=True):
        assert arm in ARMS, arm
        self.arm = arm
        self.window = window
        self.keep_possessive = keep_possessive
        self._saved = []
        self.abstentions = []
        self.last = {}

    def _save(self, mod, name):
        self._saved.append((mod, name, getattr(mod, name)))

    def __enter__(self):
        import hdlab.referent_per_np as RNP
        import hdlab.situation_reader as SR
        _DISC_CACHE.clear()
        self.abstentions = []
        if self.arm in ("twin", "disc_graded_twin", "disc_graded_best_twin"):
            install_twin_phi()
        else:
            restore_ship_phi()
        TWIN_POS["on"] = (self.arm == "twin_pos")
        POOL_STRICT["on"] = (self.arm in STRICT_ARMS)
        # DELEGATE when the diff is landed: the live organ IS this arm, so install NOTHING and let
        # `reader_kw` select the configuration.  Measuring the shipped organ beats measuring an overlay
        # that merely resembles it, and it is what makes this cell's reverify valid on the landed tree.
        self.delegated = bool(live_patched()
                              and (self.arm in DELEGATED or self.arm in DELEGATED_TWIN))
        if self.delegated:
            if self.arm in DELEGATED_TWIN:
                _twin_live_on()
            return self
        if self.window is None and self.arm in ARM_WINDOW:
            self.window = ARM_WINDOW[self.arm]
            win = self.window
        if self.arm == "ship":
            return self
        keep_poss = self.keep_possessive
        win = self.window
        holder_fill = [self.arm != "disc_blankcard"]   # the A/B on the file card itself

        # (a) THE INTRODUCTION ARM ------------------------------------------------------------------
        self._save(RNP, "referent_per_np_source")
        import inspect as _insp
        _real_rnp = RNP.referent_per_np_source
        _rnp_has_flag = "discover_pronouns" in _insp.signature(_real_rnp).parameters

        def _rnp(conll_path, tagger, name_gender_map=None, use_frame=True,
                 discover_pronouns=True, fill_card=None, **_extra):
            # The PATCHED situation_reader passes `discover_pronouns` / `fill_card` down to this organ, so the
            # overlay must ACCEPT them (this is exactly what crashed the self-test against the landed tree)
            # and HONOUR them: discover_pronouns=False has to reproduce the pre-patch organ.
            if not discover_pronouns:
                extra = {"discover_pronouns": False} if _rnp_has_flag else {}
                return _real_rnp(conll_path, tagger, name_gender_map=name_gender_map,
                                 use_frame=use_frame, **extra)
            fc = holder_fill[0] if fill_card is None else bool(fill_card)
            key = (conll_path, id(self), fc)
            if key not in _DISC_CACHE:
                _DISC_CACHE[key] = discovered_pronoun_source(
                    conll_path, tagger, name_gender_map=name_gender_map, use_frame=use_frame,
                    keep_possessive=keep_poss, fill_card=fc)
            ms, n = _DISC_CACHE[key]
            return [dict(m) for m in ms], n

        RNP.referent_per_np_source = _rnp
        if self.arm == "disc_role":
            return self

        # (b) ONE STREAM: `_coref_mentions` is the discovered stream; the column is parsed for SCORING only
        self._save(SR, "parse_litbank_conll")
        real_parse = SR.parse_litbank_conll

        def _one_stream(conll_path, name_gender_map=None, tagger=None):
            gold, _n = real_parse(conll_path, name_gender_map=name_gender_map, tagger=tagger)
            _stash_gold(conll_path, gold)
            ms, n = _rnp(conll_path, tagger, name_gender_map=name_gender_map)
            return ms, n

        SR.parse_litbank_conll = _one_stream

        # (c) THE DISCOVERED ANAPHORA QUESTIONS + the explicit abstentions
        self._save(SR, "build_pronoun_targets")
        holder = self

        def _targets(mentions, target_pronouns=None):
            tg, ab = discovered_pronoun_targets(mentions, window=win)
            holder.abstentions = ab
            return tg

        SR.build_pronoun_targets = _targets

        # (d) THE RETRIEVAL POOL + SCORER-SIDE GOLD ALIGNMENT
        self._save(SR.SituationReader, "_read_entities")
        real_read_entities = SR.SituationReader._read_entities

        def _read_entities(reader, mentions, targets, n_sents):
            pool = anaphora_pool(mentions)
            keep = {m["midx"] for m in pool}
            if holder.arm in GRADED:
                g = _GOLD_BY_PATH.get(getattr(reader, "_cur_conll", ""), None)
                kw = GRADED[holder.arm]
                recs, ab = graded_resolve(mentions, targets, gold=g, **kw)
                holder.abstentions = list(holder.abstentions) + ab
                res = [SR.CorefResolution(
                    pronoun=r["pronoun"], sent_idx=r["sent_idx"], gold_cluster=r["gold_cluster"],
                    resolved_cluster=-1, correct=r["correct"], attempted=True,
                    bucket=SR.sent_dist_bucket(r["sent_dist"]), sent_dist=r["sent_dist"],
                    resolved_head=r["resolved_head"]) for r in recs]
                for rr, r in zip(res, recs):
                    rr.target_wpos = r["target_wpos"]
                dummy = [{"correct": bool(r["correct"])} for r in recs]
                return res, dummy, dummy
            if holder.arm in ("disc_actr", "disc_actr_strict"):
                g = _GOLD_BY_PATH.get(getattr(reader, "_cur_conll", ""), None)
                recs, ab = actr_resolve_discovered(pool, [t for t in targets
                                                          if t["target"]["midx"] in keep], gold=g)
                holder.abstentions = list(holder.abstentions) + ab
                res = [SR.CorefResolution(
                    pronoun=r["pronoun"], sent_idx=r["sent_idx"], gold_cluster=r["gold_cluster"],
                    resolved_cluster=-1, correct=r["correct"], attempted=True,
                    bucket=SR.sent_dist_bucket(r["sent_dist"]) if hasattr(SR, "sent_dist_bucket")
                    else "same", sent_dist=r["sent_dist"], resolved_head=r["resolved_head"])
                    for r in recs]
                for rr, r in zip(res, recs):
                    rr.target_wpos = r["target_wpos"]
                dummy = [{"correct": bool(r["correct"])} for r in recs]
                return res, dummy, dummy
            resolutions, recs_ec, recs_ss = real_read_entities(
                reader, pool, [t for t in targets if t["target"]["midx"] in keep], n_sents)
            # the gold column, used for CORRECTNESS ONLY (never in a decision)
            g = _GOLD_BY_PATH.get(getattr(reader, "_cur_conll", ""), None)
            tg = [t for t in targets if t["target"]["midx"] in keep]
            for r, t in zip(resolutions, tg):
                r.target_wpos = t["target"]["wtok_start"]
                if g is not None:
                    gc = g["pos"].get((t["target"]["sent_idx"], t["target"]["wtok_start"]))
                    rc = g["head"].get((r.resolved_head or "").lower(), set())
                    r.gold_cluster = -1 if gc is None else gc
                    r.correct = bool(gc is not None and gc in rc)
            return resolutions, recs_ec, recs_ss

        SR.SituationReader._read_entities = _read_entities

        # `_cur_conll` so the scorer-side alignment can find the right gold map
        self._save(SR.SituationReader, "read")
        real_read = SR.SituationReader.read

        def _read(reader, conll_path):
            reader._cur_conll = conll_path
            return real_read(reader, conll_path)

        SR.SituationReader.read = _read

        # (e) THE CENTERING GIVENNESS REPAIR (pri 125 quality push #2).  `_cm_agent_candidates` builds
        # `agent_freq` as a count per CLUSTER id.  On the coref-column stream the gold cluster groups every
        # mention of one entity, so that count IS the Centering givenness cue.  On the DISCOVERED stream
        # every referent carries a FRESH SINGLETON cluster, so every count is 1 and the salience cue is
        # DEAD -- the exact loss the brief predicted ("a consumer that read the gold cluster COUNT as
        # givenness").  The brain's cue is the number of prior references to that referent, which the reader
        # can count from its OWN files: the head-individuated entity (the same individuation
        # `WorkingOverlay` / the landed resolver already use).  No gold, no new organ.
        levers = LEVERS.get(self.arm, ())
        if levers:
            self._save(SR.SituationReader, "_cm_agent_candidates")
            real_cand = SR.SituationReader._cm_agent_candidates

            def _cand(reader, n_sents):
                anoms, freq = real_cand(reader, n_sents)
                cms = reader._coref_mentions or []
                if "case" in levers and reader.cm_agent and reader.referent_per_np and cms:
                    # rebuild the candidate set with the case cue as an ACCUSATIVE EXCLUSION
                    from hdlab.graded_role_assigner import _nominals_keep_pron
                    anoms = _nominals_keep_pron(cms, n_sents)
                    if reader.case_filter:
                        anoms = [[m for m in lst if (not m.get("is_pronoun"))
                                  or m["head"].lower() not in ACCUSATIVE_MARKED] for lst in anoms]
                if anoms is None:
                    return anoms, freq
                if "nopos" in levers:
                    # a possessive pronoun is not a core argument of the verb, and it sits preverbally where
                    # the word-order cue is strongest -- the candidate most able to steal the subject slot
                    anoms = [[m for m in lst if not (m.get("is_pronoun")
                                                     and m["head"].lower() in POSSESSIVE_FORMS)]
                             for lst in anoms]
                if "freq" in levers or "freq2" in levers:
                    pron_ok = ("freq" in levers) and reader.include_pron_agents
                    byhead = defaultdict(int)
                    for m in cms:
                        if pron_ok or not m.get("is_pronoun"):
                            byhead[m["head"].lower()] += 1
                    freq = {m.get("cluster"): byhead[m["head"].lower()] for m in cms}
                return anoms, freq

            SR.SituationReader._cm_agent_candidates = _cand
        return self

    def __exit__(self, *exc):
        if getattr(self, "delegated", False):
            _twin_live_off()
            self.delegated = False
            restore_ship_phi()
            TWIN_POS["on"] = False
            POOL_STRICT["on"] = False
            _DISC_CACHE.clear()
            return False
        for mod, name, val in reversed(self._saved):
            setattr(mod, name, val)
        self._saved = []
        restore_ship_phi()
        TWIN_POS["on"] = False
        POOL_STRICT["on"] = False
        _DISC_CACHE.clear()
        return False


# CorefResolution needs the two additive fields the diff adds (target position / abstention flag)
def _extend_coref_resolution():
    import hdlab.situation_reader as SR
    if not hasattr(SR.CorefResolution, "target_wpos"):
        try:
            SR.CorefResolution.target_wpos = -1
        except Exception:
            pass


# =====================================================================================================
# 5. CORPUS LOADERS + THE SCORERS (gold is the ANSWER KEY only)
# =====================================================================================================
def load_ud_docs(path=UD_TEST):
    """UD-EWT with DOCUMENT boundaries (the evaluation's A2 loader shape) + lemma."""
    docs, current, sent, docid = [], [], [], None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# newdoc id = "):
            if sent:
                current.append(sent); sent = []
            if current:
                docs.append((docid, current)); current = []
            docid = line.split(" = ", 1)[1]
        elif not line.strip():
            if sent:
                current.append(sent); sent = []
        elif not line.startswith("#"):
            c = line.split("\t")
            if c[0].isdigit():
                sent.append({"id": int(c[0]), "form": c[1], "lemma": c[2], "upos": c[3],
                             "head": int(c[6]), "dep": c[7].split(":")[0], "deprel": c[7]})
    if sent:
        current.append(sent)
    if current:
        docs.append((docid, current))
    return docs


def write_conll(sentences, annotations=None, path=None):
    """(sent_idx, wtok, token, coref) rows -> the reader's CoNLL.  annotations=None -> the column is all `_`
    (TEXT ONLY: only FORM + token/sentence boundaries cross the reader's input boundary)."""
    lines = ["#begin document (pri125); part 0"]
    for si, toks in enumerate(sentences):
        if si:
            lines.append("")
        for wi, t in enumerate(toks):
            mark = (annotations or {}).get((si, wi), "_")
            lines.append("\t".join(["pri125", "0", str(wi), t] + ["_"] * 8 + [mark]))
    lines.append("")
    if path is None:
        fd, path = tempfile.mkstemp(suffix=".conll", text=True)
        os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def gold_role_items(sentence):
    """The evaluation's A2 gold recipe, per sentence: agent (active nsubj / passive obl:agent-by) and patient
    (active obj / passive nsubj:pass) for every gold VERB, plus copular holder/property."""
    ag_items, pa_items, st_items = [], [], []
    for verb in sentence:
        if verb["upos"] != "VERB":
            continue
        ch = [t for t in sentence if t["head"] == verb["id"]]
        passive = any(t["deprel"].startswith(("nsubj:pass", "aux:pass")) for t in ch)
        if passive:
            agents = [t for t in ch if t["deprel"].startswith("obl")
                      and any(c["head"] == t["id"] and c["dep"] == "case" and c["form"].lower() == "by"
                              for c in sentence)]
            patients = [t for t in ch if t["deprel"].startswith("nsubj:pass")]
        else:
            agents = [t for t in ch if t["dep"] == "nsubj" and not t["deprel"].startswith("nsubj:pass")]
            patients = [t for t in ch if t["dep"] == "obj"]
        if agents:
            ag_items.append((verb, agents, passive))
        if patients:
            pa_items.append((verb, patients, passive))
    for pred in sentence:
        ch = [t for t in sentence if t["head"] == pred["id"]]
        if pred["upos"] not in ("ADJ", "NOUN", "PROPN") or not any(t["dep"] == "cop" for t in ch):
            continue
        holders = [t for t in ch if t["dep"] in ("nsubj", "nsubj:pass")]
        if holders:
            st_items.append((pred, holders))
    return ag_items, pa_items, st_items


def score_doc(model, gold_sents):
    """The evaluation's exact scorer: exact surface head, ALL eligible questions counted, a missing answer
    counted wrong.  Returns per-item correctness vectors so a paired bootstrap can resample documents."""
    ev = defaultdict(list)
    for e in model.events:
        ev[(e.sent_idx, e.pred_idx)].append(e)
    st = defaultdict(list)
    for s in model.entity_states:
        st[s.sent_idx].append(s)
    r = {"agent": [], "patient": [], "state": [], "agent_pron": [], "missing": 0,
         "verbs_gold": 0, "verbs_detected": 0, "events": len(model.events)}
    for si, sentence in enumerate(gold_sents):
        ag, pa, stt = gold_role_items(sentence)
        for verb in sentence:
            if verb["upos"] != "VERB":
                continue
            r["verbs_gold"] += 1
            found = [e for e in ev[(si, verb["id"] - 1)]
                     if e.predicate.lower() in (verb["form"].lower(), verb["lemma"].lower())]
            r["verbs_detected"] += int(len(found) == 1)
        for role, items in (("agent", ag), ("patient", pa)):
            for verb, targets, _passive in items:
                found = [e for e in ev[(si, verb["id"] - 1)]
                         if e.predicate.lower() in (verb["form"].lower(), verb["lemma"].lower())]
                event = found[0] if len(found) == 1 else None
                answer = getattr(event, role, None) if event else None
                ok = answer is not None and answer.lower() in {t["form"].lower() for t in targets}
                r[role].append(int(ok))
                if answer in (None, "", "?"):
                    r["missing"] += 1
                if role == "agent" and any(t["upos"] == "PRON" for t in targets):
                    r["agent_pron"].append(int(ok))
        for pred, holders in stt:
            hs = {t["form"].lower() for t in holders}
            bind = [s for s in st[si] if s.holder.lower() in hs]
            r["state"].append(int(any(s.property.lower() == pred["form"].lower() for s in bind)))
    return r


def wordorder_agent_floor(sentences, gold_sents, tags_by_sent):
    """FLOOR: the word-order agent -- the nearest PREVERBAL nominal/pronoun token by position, decided from
    the category organ's own tags (English-dominant word-order cue alone, no mention stream, no retrieval)."""
    out, out_pron = [], []
    for si, sentence in enumerate(gold_sents):
        toks = sentences[si]
        up = tags_by_sent[si]
        ag, _pa, _st = gold_role_items(sentence)
        for verb, targets, _passive in ag:
            v0 = verb["id"] - 1
            pick = None
            for i in range(min(v0, len(toks)) - 1, -1, -1):
                if i < len(up) and up[i] in ("NOUN", "PROPN", "PRON"):
                    pick = toks[i]
                    break
            ok = pick is not None and pick.lower() in {t["form"].lower() for t in targets}
            out.append(int(ok))
            if any(t["upos"] == "PRON" for t in targets):
                out_pron.append(int(ok))
    return out, out_pron


# ---------------------------------------------------------------------------------- bootstrap / reporting
def paired_boot(a_docs, b_docs, n_boot=N_BOOT, seed=SEED):
    """Doc-paired bootstrap over DOCUMENTS (the unit of resampling) of the accuracy difference b - a.
    a_docs/b_docs = list per document of per-item 0/1 vectors on the SAME population."""
    rng = np.random.default_rng(seed)
    nd = len(a_docs)
    if nd == 0:
        return None
    A = [np.asarray(v, dtype=float) for v in a_docs]
    B = [np.asarray(v, dtype=float) for v in b_docs]
    tot = sum(len(v) for v in A)
    if tot == 0:
        return None
    obs = (sum(v.sum() for v in B) / tot) - (sum(v.sum() for v in A) / tot)
    diffs = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, nd, nd)
        na = sum(len(A[i]) for i in idx)
        if na == 0:
            diffs[b] = 0.0
            continue
        diffs[b] = (sum(B[i].sum() for i in idx) / na) - (sum(A[i].sum() for i in idx) / na)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"delta": round(float(obs), 4), "ci": [round(float(lo), 4), round(float(hi), 4)],
            "half": round(float(hi - lo) / 2, 4), "sep": bool(lo > 0 or hi < 0), "n_items": int(tot),
            "n_docs": nd}


def acc(vs):
    n = sum(len(v) for v in vs)
    return (sum(sum(v) for v in vs) / n) if n else None


def _p(x, nd=4):
    return "n/a" if x is None else ("%." + str(nd) + "f") % x


# =====================================================================================================
# 6. ROW: the five evaluation documents, its exact scorer (the brief's phase-1 reproduction)
# =====================================================================================================
def row_repro(arms=("ship", "disc"), verbose=True):
    docs = load_ud_docs()[:5]
    from hdlab.situation_reader import SituationReader
    res = {}
    for a in arms:
        per = []
        t0 = time.time()
        with Arm(a):
            for docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                p = write_conll(sents)
                try:
                    sm = SituationReader(**reader_kw(a)).read(p)
                finally:
                    os.unlink(p)
                r = score_doc(sm, gold)
                r["doc"] = docid
                r["n_coref_res"] = len(sm.coref_resolutions)
                per.append(r)
                if verbose:
                    print("  %-10s %-52s agent %2d/%-2d pron %2d/%-2d patient %2d/%-2d state %d/%d"
                          % (a, docid[:52], sum(r["agent"]), len(r["agent"]), sum(r["agent_pron"]),
                             len(r["agent_pron"]), sum(r["patient"]), len(r["patient"]),
                             sum(r["state"]), len(r["state"])))
        res[a] = {"per_doc": per, "secs": round(time.time() - t0, 1),
                  "agent": [sum(r["agent"]) for r in per], "agent_n": [len(r["agent"]) for r in per],
                  "agent_total": sum(sum(r["agent"]) for r in per),
                  "agent_eligible": sum(len(r["agent"]) for r in per),
                  "agent_pron_total": sum(sum(r["agent_pron"]) for r in per),
                  "agent_pron_eligible": sum(len(r["agent_pron"]) for r in per),
                  "patient_total": sum(sum(r["patient"]) for r in per),
                  "patient_eligible": sum(len(r["patient"]) for r in per),
                  "state_total": sum(sum(r["state"]) for r in per),
                  "state_eligible": sum(len(r["state"]) for r in per),
                  "missing": sum(r["missing"] for r in per),
                  "verbs": [sum(r["verbs_detected"] for r in per), sum(r["verbs_gold"] for r in per)],
                  "coref_records": sum(r["n_coref_res"] for r in per)}
        if verbose:
            x = res[a]
            print("  %-10s AGENT %d/%d  pron %d/%d  PATIENT %d/%d  STATE %d/%d  missing %d  coref recs %d  %.0fs"
                  % (a, x["agent_total"], x["agent_eligible"], x["agent_pron_total"],
                     x["agent_pron_eligible"], x["patient_total"], x["patient_eligible"],
                     x["state_total"], x["state_eligible"], x["missing"], x["coref_records"], x["secs"]))
    return res


# =====================================================================================================
# 7. ROW: annotation invariance (the triple) -- byte-identity of every DECISION
# =====================================================================================================
def _decision_fingerprint(sm):
    return {
        "events": [(e.sent_idx, e.pred_idx, e.predicate, e.agent, e.patient, getattr(e, "polarity", None))
                   for e in sm.events],
        "states": [(s.sent_idx, s.holder, s.property) for s in sm.entity_states],
        "entities": [(tuple(e.heads), e.n_mentions) for e in sm.entities],
        "pronouns": [(r.pronoun, r.sent_idx, r.resolved_head) for r in sm.coref_resolutions],
    }


def row_invariance(arms=ARMS, n_docs=3, verbose=True):
    """text-only / blank-column / permuted-cluster-ids -> the DECISIONS must be byte-identical.
    (text-only and blank column are the same file by construction; the third condition carries real
    mention brackets with PERMUTED cluster ids, which is the leak test that bites.)"""
    from hdlab.situation_reader import SituationReader
    docs = load_ud_docs()[:n_docs]
    rng = random.Random(SEED)
    out = {}
    for a in arms:
        rows = []
        with Arm(a):
            for docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                # conditions
                conds = {}
                conds["text_only"] = None
                conds["blank"] = {}
                # every nominal/pronoun token gets a bracket; ids permuted over a small id pool
                marks, ids = {}, []
                for si, s in enumerate(gold):
                    for wi, t in enumerate(s):
                        if t["upos"] in ("NOUN", "PROPN", "PRON"):
                            ids.append((si, wi))
                pool = list(range(len(ids)))
                rng.shuffle(pool)
                for (si, wi), cid in zip(ids, pool):
                    marks[(si, wi)] = "(%d)" % cid
                conds["permuted"] = marks
                fps = {}
                for label, ann in conds.items():
                    p = write_conll(sents, ann)
                    try:
                        fps[label] = _decision_fingerprint(SituationReader().read(p))
                    finally:
                        os.unlink(p)
                base = json.dumps(fps["text_only"], sort_keys=True)
                rows.append({"doc": docid,
                             "blank_identical": json.dumps(fps["blank"], sort_keys=True) == base,
                             "permuted_identical": json.dumps(fps["permuted"], sort_keys=True) == base,
                             "n_events": len(fps["text_only"]["events"]),
                             "n_pron_text": len(fps["text_only"]["pronouns"]),
                             "n_pron_perm": len(fps["permuted"]["pronouns"])})
        out[a] = rows
        if verbose:
            for r in rows:
                print("  %-10s %-46s blank==%-5s permuted==%-5s  events %d  pron %d/%d"
                      % (a, r["doc"][:46], r["blank_identical"], r["permuted_identical"],
                         r["n_events"], r["n_pron_text"], r["n_pron_perm"]))
    return out


# =====================================================================================================
# 8. ROW: the N-document UD-EWT sample -- agents (+ the no-regress populations), paired over documents
# =====================================================================================================
def row_agents(n_docs=40, arms=ARMS, verbose=True, seed=SEED, window=None):
    from hdlab.situation_reader import SituationReader
    from hdlab import frontend as F
    alldocs = load_ud_docs()
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(alldocs)), min(n_docs, len(alldocs))))
    docs = [alldocs[i] for i in idx]
    if verbose:
        print("UD-EWT test: %d documents total, seeded random sample of %d (documents are the unit)"
              % (len(alldocs), len(docs)))
    # the FLOOR needs the organ's own tags on the same text
    floor_ag, floor_pron = [], []
    tagger = F.tagger()
    for docid, gold in docs:
        sents = [[t["form"] for t in s] for s in gold]
        tags = [tagger.tag(list(s)) for s in sents]
        a, ap = wordorder_agent_floor(sents, gold, tags)
        floor_ag.append(a); floor_pron.append(ap)
    per_arm = {}
    for a in arms:
        rows = []
        t0 = time.time()
        with Arm(a, window=window):
            for docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                p = write_conll(sents)
                try:
                    sm = SituationReader(**reader_kw(a)).read(p)
                finally:
                    os.unlink(p)
                r = score_doc(sm, gold)
                r["doc"] = docid
                r["n_coref_res"] = len(sm.coref_resolutions)
                rows.append(r)
        per_arm[a] = {"rows": rows, "secs": round(time.time() - t0, 1)}
        if verbose:
            print("  %-10s AGENT %s (%d items)  pron %s  PATIENT %s  STATE %s  coref recs %d  %.0fs"
                  % (a, _p(acc([r["agent"] for r in rows])), sum(len(r["agent"]) for r in rows),
                     _p(acc([r["agent_pron"] for r in rows])), _p(acc([r["patient"] for r in rows])),
                     _p(acc([r["state"] for r in rows])), sum(r["n_coref_res"] for r in rows),
                     per_arm[a]["secs"]))
    res = {"docs": [d for d, _ in docs], "n_docs": len(docs), "arms": {}, "contrasts": {},
           "floor": {"agent": round(acc(floor_ag), 4), "agent_pron": round(acc(floor_pron), 4)}}
    for a in arms:
        rows = per_arm[a]["rows"]
        res["arms"][a] = {k: (round(acc([r[k] for r in rows]), 4) if acc([r[k] for r in rows]) is not None
                              else None) for k in ("agent", "agent_pron", "patient", "state")}
        res["arms"][a]["n"] = {k: sum(len(r[k]) for r in rows)
                               for k in ("agent", "agent_pron", "patient", "state")}
        res["arms"][a]["secs"] = per_arm[a]["secs"]
        res["arms"][a]["coref_records"] = sum(r["n_coref_res"] for r in rows)
    base = per_arm.get("ship", {}).get("rows")
    for a in arms:
        rows = per_arm[a]["rows"]
        c = {}
        c["vs_wordorder_floor_agent"] = paired_boot(floor_ag, [r["agent"] for r in rows])
        c["vs_wordorder_floor_agent_pron"] = paired_boot(floor_pron, [r["agent_pron"] for r in rows])
        if base is not None and a != "ship":
            for k in ("agent", "agent_pron", "patient", "state"):
                c["vs_ship_" + k] = paired_boot([r[k] for r in base], [r[k] for r in rows])
        res["contrasts"][a] = c
    for tw in ("twin", "twin_pos"):
        if "disc" in per_arm and tw in per_arm:
            res["contrasts"]["disc_vs_" + tw] = {
                k: paired_boot([r[k] for r in per_arm[tw]["rows"]], [r[k] for r in per_arm["disc"]["rows"]])
                for k in ("agent", "agent_pron", "patient", "state")}
    return res


# =====================================================================================================
# 9. ROW: the reader's OWN pronoun instrument on MODERN GUM test, text only
# =====================================================================================================
def gum_textonly_conll(doc, path):
    """The GUM document as the reader's CoNLL with the coref column BLANK -- text only."""
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    lines = ["#begin document (%s); part 0" % str(doc.docid).replace(" ", "_")]
    for si in sorted(by_sent):
        for w, t in enumerate(sorted(by_sent[si], key=lambda x: x.idx)):
            lines.append("\t".join([str(doc.docid), "0", str(w), (t.form or "_")] + ["_"] * 8 + ["_"]))
        lines.append("")
    lines.append("#end document")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def gum_pronoun_questions(doc):
    """THE FIXED QUESTION SET (gold = the answer key only): every THIRD-PERSON pronoun mention that has a
    prior mention in the same gold chain.  Returns per-question
    {sent, wpos, form, gold_heads} where gold_heads = the surface heads of all PRIOR non-pronoun mentions of
    that gold entity (the reader's pick must name one of them).  ABSTENTION = WRONG."""
    sent_wpos = {}
    by_sent = defaultdict(list)
    for t in doc.toks:
        by_sent[t.sent].append(t)
    for si in sorted(by_sent):
        for w, t in enumerate(sorted(by_sent[si], key=lambda x: x.idx)):
            sent_wpos[t.gidx] = (si, w)
    gidx_form = {t.gidx: t.form for t in doc.toks}
    qs = []
    seen = defaultdict(list)
    for m in sorted(doc.mentions, key=lambda x: (x.start_g, x.end_g)):
        hform = gidx_form.get(m.head_g, m.text.split()[-1] if m.text else "")
        if m.mtype == "pronoun" and is_anaphora_target_form(hform):
            priors = [p for p in seen[m.eid] if p[0] != "pronoun"]
            if priors:
                si, w = sent_wpos.get(m.head_g, (None, None))
                if si is None:
                    continue
                qs.append({"sent": si, "wpos": w, "form": hform.lower(),
                           "gold_heads": sorted({h for _t, h in priors})})
        seen[m.eid].append((m.mtype, (gidx_form.get(m.head_g, "") or "").lower()))
    return qs


def row_pronouns(n_docs=16, arms=ARMS, verbose=True, window=None):
    import experiments.gum_coref as G
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")   # GOLD = the answer key only
    test = alldocs[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    if verbose:
        print("GUM: %d docs, TEST=%d, using %d (text-only input; gold is the scorer's only input)"
              % (len(alldocs), len(test), len(docs)))
    prepared = []
    for d in docs:
        p = gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        prepared.append((d, p, gum_pronoun_questions(d)))
    # FLOOR 1: nearest-prior-compatible-referent, computed on the reader's OWN discovered stream
    # FLOOR 2: the word-order agent's answer for the pronoun's own clause (a decision-free positional pick)
    per_arm, floor1, floor2 = {}, [], []
    from hdlab import frontend as F
    for a in arms:
        rows = []
        t0 = time.time()
        with Arm(a, window=window) as arm:
            for d, p, qs in prepared:
                sm = SituationReader(**reader_kw(a)).read(p)
                pick = {}
                for r in sm.coref_resolutions:
                    pick[(r.sent_idx, getattr(r, "target_wpos", -1))] = (r.resolved_head or "").lower()
                byform = defaultdict(list)
                for r in sm.coref_resolutions:
                    byform[(r.sent_idx, r.pronoun.lower())].append((r.resolved_head or "").lower())
                corr = []
                for q in qs:
                    ans = pick.get((q["sent"], q["wpos"]))
                    if ans is None:
                        cand = byform.get((q["sent"], q["form"]), [])
                        ans = cand[0] if len(cand) == 1 else None
                    corr.append(int(bool(ans) and ans in q["gold_heads"]))
                rows.append({"doc": d.docid, "corr": corr, "n_q": len(qs),
                             "answered": sum(1 for q in qs
                                             if pick.get((q["sent"], q["wpos"])) not in (None, "")),
                             "n_res": len(sm.coref_resolutions),
                             "n_abstain": len(arm.abstentions)})
        per_arm[a] = {"rows": rows, "secs": round(time.time() - t0, 1)}
        if verbose:
            print("  %-10s PRONOUN %s (%d questions, %d answered, %d abstention records)  %.0fs"
                  % (a, _p(acc([r["corr"] for r in rows])), sum(r["n_q"] for r in rows),
                     sum(r["answered"] for r in rows), sum(r["n_abstain"] for r in rows),
                     per_arm[a]["secs"]))
    # the floors, on the same question population
    tagger = F.tagger()
    for d, p, qs in prepared:
        f1v, f2v = [], []
        by_sent = defaultdict(list)
        for t in d.toks:
            by_sent[t.sent].append(t)
        sents = [[t.form for t in sorted(by_sent[si], key=lambda x: x.idx)] for si in sorted(by_sent)]
        tags = [tagger.tag(list(s)) for s in sents]
        # nearest prior compatible referent: scan backwards over the organ's nominal tokens
        for q in qs:
            tphi = phi_of(q["form"]) or {}
            ans1 = ans2 = None
            for si in range(q["sent"], -1, -1):
                lim = q["wpos"] if si == q["sent"] else len(sents[si])
                for wi in range(min(lim, len(sents[si])) - 1, -1, -1):
                    if tags[si][wi] not in ("NOUN", "PROPN"):
                        continue
                    from hdlab.state_of_mind import infer_nominal_gender
                    g = infer_nominal_gender([sents[si][wi]])
                    if ans2 is None:
                        ans2 = sents[si][wi].lower()
                    if tphi.get("gender") and g and tphi["gender"] not in ("any",) and g != tphi["gender"]:
                        continue
                    ans1 = sents[si][wi].lower()
                    break
                if ans1 is not None:
                    break
            f1v.append(int(bool(ans1) and ans1 in q["gold_heads"]))
            f2v.append(int(bool(ans2) and ans2 in q["gold_heads"]))
        floor1.append(f1v); floor2.append(f2v)
    res = {"n_docs": len(docs), "docs": [str(d.docid) for d, _p, _q in prepared], "arms": {},
           "floor": {"nearest_prior_compatible": round(acc(floor1), 4),
                     "nearest_prior_any": round(acc(floor2), 4)},
           "contrasts": {}}
    for a in arms:
        rows = per_arm[a]["rows"]
        res["arms"][a] = {"pronoun_acc": (round(acc([r["corr"] for r in rows]), 4)
                                          if acc([r["corr"] for r in rows]) is not None else None),
                          "n_questions": sum(r["n_q"] for r in rows),
                          "answered": sum(r["answered"] for r in rows),
                          "abstention_records": sum(r["n_abstain"] for r in rows),
                          "resolutions": sum(r["n_res"] for r in rows),
                          "secs": per_arm[a]["secs"]}
        res["contrasts"][a] = {
            "vs_nearest_prior_compatible": paired_boot(floor1, [r["corr"] for r in per_arm[a]["rows"]]),
            "vs_nearest_prior_any": paired_boot(floor2, [r["corr"] for r in per_arm[a]["rows"]])}
    for tw in ("twin", "twin_pos"):
        if "disc" in per_arm and tw in per_arm:
            res["contrasts"]["disc_vs_" + tw] = paired_boot([r["corr"] for r in per_arm[tw]["rows"]],
                                                            [r["corr"] for r in per_arm["disc"]["rows"]])
    if "disc" in per_arm and "ship" in per_arm:
        res["contrasts"]["disc_vs_ship"] = paired_boot([r["corr"] for r in per_arm["ship"]["rows"]],
                                                        [r["corr"] for r in per_arm["disc"]["rows"]])
    return res


# =====================================================================================================
# 10. THE ACCESSIBILITY-WINDOW SWEEP (the one free parameter; the phase diagram)
# =====================================================================================================
def row_window_sweep(n_docs=8, windows=(0, 1, 2, 3, 5, 8), verbose=True):
    out = {}
    for w in windows:
        r = row_pronouns(n_docs=n_docs, arms=("disc",), verbose=False, window=w)
        out[str(w)] = {"acc": r["arms"]["disc"]["pronoun_acc"], "n": r["arms"]["disc"]["n_questions"],
                       "answered": r["arms"]["disc"]["answered"],
                       "floor": r["floor"]["nearest_prior_compatible"]}
        if verbose:
            print("  window %-3s pronoun acc %s  answered %d/%d  (floor %s)"
                  % (w if w else "all", _p(out[str(w)]["acc"]), out[str(w)]["answered"],
                     out[str(w)]["n"], _p(out[str(w)]["floor"])))
    return out


# =====================================================================================================
# 10b. THE SIGNAL-LOSS TRACE -- chain by chain, with counts, for the signal the end read needs
#      (the AGENT of a clause whose subject is a pronoun; and the anaphora question).
#      Each rung: what the hand-off PRODUCES, what the next rung READS, what is LOST.
# =====================================================================================================
def row_trace(n_docs=5, arms=("ship", "disc"), verbose=True):
    from hdlab.situation_reader import SituationReader
    from hdlab.graded_role_assigner import NOMINATIVE_PRON
    from hdlab import frontend as F
    docs = load_ud_docs()[:n_docs]
    tagger = F.tagger()
    # RUNG 1: tokens -> categories.  Does the organ see the pronoun at all?
    r1 = {"gold_pron": 0, "organ_pron": 0, "organ_pron_on_gold": 0, "tokens": 0,
          "gold_agent_pron": 0, "gold_agent_pron_tagged": 0}
    for docid, gold in docs:
        for s in gold:
            toks = [t["form"] for t in s]
            up = tagger.tag(list(toks))
            r1["tokens"] += len(toks)
            for i, t in enumerate(s):
                r1["gold_pron"] += int(t["upos"] == "PRON")
                r1["organ_pron"] += int(up[i] == "PRON")
                r1["organ_pron_on_gold"] += int(t["upos"] == "PRON" and up[i] == "PRON")
            ag, _pa, _st = gold_role_items(s)
            for _v, targets, _p in ag:
                for t in targets:
                    if t["upos"] == "PRON":
                        r1["gold_agent_pron"] += 1
                        r1["gold_agent_pron_tagged"] += int(up[t["id"] - 1] == "PRON")
    out = {"rung1_tokens_to_categories": r1, "arms": {}}
    for a in arms:
        rr = {"rung2_referent_opened": 0, "rung3_in_agent_candidate_set": 0,
              "rung3_lost_case_filter": 0, "rung4_picked_correct": 0,
              "anaphora_scheduled": 0, "anaphora_abstained": 0, "anaphora_answered": 0,
              "gold_agent_pron": 0, "coref_mentions": 0, "role_mentions_pron": 0}
        with Arm(a) as arm:
            for docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                p = write_conll(sents)
                try:
                    reader = SituationReader(**reader_kw(a))
                    sm = reader.read(p)
                finally:
                    os.unlink(p)
                cms = reader._coref_mentions or []
                rr["coref_mentions"] += len(cms)
                rr["role_mentions_pron"] += sum(1 for m in cms if m.get("is_pronoun"))
                anoms, _freq = reader._cm_agent_candidates(len(gold))
                ev = defaultdict(list)
                for e in sm.events:
                    ev[(e.sent_idx, e.pred_idx)].append(e)
                for si, s in enumerate(gold):
                    ag, _pa, _st = gold_role_items(s)
                    present = {(m["sent_idx"], m["wtok_start"]) for m in cms}
                    for verb, targets, _p in ag:
                        for t in targets:
                            if t["upos"] != "PRON":
                                continue
                            rr["gold_agent_pron"] += 1
                            here = (si, t["id"] - 1) in present
                            rr["rung2_referent_opened"] += int(here)
                            incand = False
                            if anoms is not None and si < len(anoms):
                                incand = any(m["wtok_start"] == t["id"] - 1 for m in anoms[si])
                            rr["rung3_in_agent_candidate_set"] += int(incand)
                            if here and not incand and t["form"].lower() not in NOMINATIVE_PRON:
                                rr["rung3_lost_case_filter"] += 1
                            found = [e for e in ev[(si, verb["id"] - 1)]
                                     if e.predicate.lower() in (verb["form"].lower(), verb["lemma"].lower())]
                            answer = found[0].agent if len(found) == 1 else None
                            rr["rung4_picked_correct"] += int(
                                answer is not None and answer.lower() == t["form"].lower())
                rr["anaphora_scheduled"] += len(sm.coref_resolutions)
                rr["anaphora_answered"] += sum(1 for r in sm.coref_resolutions if r.resolved_head)
                rr["anaphora_abstained"] += len(arm.abstentions)
        out["arms"][a] = rr
        if verbose:
            print("  %-10s referent opened %3d/%-3d -> agent candidate %3d/%-3d (case-filter loss %d)"
                  " -> picked %3d/%-3d | anaphora scheduled %d answered %d open-abstentions %d"
                  % (a, rr["rung2_referent_opened"], rr["gold_agent_pron"],
                     rr["rung3_in_agent_candidate_set"], rr["gold_agent_pron"],
                     rr["rung3_lost_case_filter"], rr["rung4_picked_correct"], rr["gold_agent_pron"],
                     rr["anaphora_scheduled"], rr["anaphora_answered"], rr["anaphora_abstained"]))
    if verbose:
        print("  RUNG 1 tokens->categories: gold PRON %d, organ tags PRON on %d of them (%.4f);"
              " gold AGENT pronouns %d, organ tags PRON on %d (%.4f)"
              % (r1["gold_pron"], r1["organ_pron_on_gold"],
                 r1["organ_pron_on_gold"] / max(1, r1["gold_pron"]), r1["gold_agent_pron"],
                 r1["gold_agent_pron_tagged"], r1["gold_agent_pron_tagged"] / max(1, r1["gold_agent_pron"])))
    return out


# =====================================================================================================
# 10e. THE ANNOTATED-PATH A/B (bar item 6-iv, at the level a solver can reach).  The board's seven rows do
#      NOT run `SituationReader.read` (pri 122 / evaluation E01: enumerated on disk -- only the STATE row
#      builds a reader, via `all_capabilities_off`, which sets referent_per_np False, so this arm is inert
#      there).  The honest equivalent is therefore the READER's own annotated read: give it GUM documents
#      WITH their gold coref column and check that `disc` does not lose coref/agent/patient against the
#      pre-patch organ on the same documents.
# =====================================================================================================
def row_annotated_ab(n_docs=8, verbose=True, arms=("ship", "disc", "disc_case")):
    import experiments.gum_coref as G
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    from hdlab.situation_reader import SituationReader
    scratch = os.path.join(OUT_DIR, "gum_gold_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    test = alldocs[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    prepared = []
    for d in docs:
        p = os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll")
        gum_to_conll(d, p)
        prepared.append((d, p))
    out = {"n_docs": len(prepared), "arms": {}}
    per = {}
    for a in arms:
        rows = []
        with Arm(a):
            for d, p in prepared:
                sm = SituationReader().read(p)
                n = len(sm.coref_resolutions)
                rows.append({"doc": str(d.docid), "n": n,
                             "corr": [int(bool(r.correct)) for r in sm.coref_resolutions],
                             "events": len(sm.events), "entities": len(sm.entities),
                             "abstain": len(getattr(sm, "pronoun_abstentions", []) or [])})
        per[a] = rows
        out["arms"][a] = {"coref_acc": (round(acc([r["corr"] for r in rows]), 4)
                                        if acc([r["corr"] for r in rows]) is not None else None),
                          "n_targets": sum(r["n"] for r in rows),
                          "events": sum(r["events"] for r in rows),
                          "entities": sum(r["entities"] for r in rows),
                          "abstentions": sum(r["abstain"] for r in rows)}
        if verbose:
            print("  %-10s ANNOTATED coref %s over %d targets  events %d  entities %d"
                  % (a, _p(out["arms"][a]["coref_acc"]), out["arms"][a]["n_targets"],
                     out["arms"][a]["events"], out["arms"][a]["entities"]))
    if "ship" in per:
        for a in per:
            if a != "ship":
                out["contrasts_vs_ship_" + a] = paired_boot([r["corr"] for r in per["ship"]],
                                                            [r["corr"] for r in per[a]])
    return out


# =====================================================================================================
# 10d. THE CONSUMER AUDIT (item 3, GENERALIZE): every INFERENCE-PATH reader of the coref annotation column,
#      enumerated on disk (not recalled) and then COUNTED on text-only input.
# =====================================================================================================
def row_consumer_audit(n_docs=3, verbose=True):
    from hdlab.coref import parse_litbank_conll
    from hdlab import frontend as F
    from hdlab.situation_reader import SituationReader
    import hdlab.space_reader as SP
    docs = load_ud_docs()[:n_docs]
    out = {"consumers": [], "counts": {}}
    tot = defaultdict(int)
    for docid, gold in docs:
        sents = [[t["form"] for t in s] for s in gold]
        p = write_conll(sents)
        try:
            # 1+2. the reader's own two streams, ship vs disc
            for a in ("ship", "disc"):
                with Arm(a):
                    reader = SituationReader()
                    sm = reader.read(p)
                    tot[a + "_coref_stream"] += len(reader._coref_mentions or [])
                    tot[a + "_pron_in_stream"] += sum(1 for m in (reader._coref_mentions or [])
                                                      if m.get("is_pronoun"))
                    tot[a + "_pron_questions"] += len(sm.coref_resolutions)
                    tot[a + "_locations"] += (1 if sm.locations is not None else 0)
            # 3. THE SPACE dimension re-parses the file ITSELF (hdlab/space_reader.py:248) -- it never sees
            #    the reader's discovered stream, so the arm cannot reach it.
            ms, _n = parse_litbank_conll(p, tagger=F.tagger())
            tot["space_reader_mentions"] += len(ms)
            tot["space_reader_pron"] += sum(1 for m in ms if m["is_pronoun"])
        finally:
            os.unlink(p)
    out["counts"] = dict(tot)
    out["consumers"] = [
        {"consumer": "hdlab/referent_per_np.py referent_per_np_source (pronoun source)",
         "reads": "coref annotation column", "status": "FIXED by this diff (category organ's PRON tags)"},
        {"consumer": "hdlab/situation_reader.py read() -> _coref_mentions (AGENT competition)",
         "reads": "coref annotation column", "status": "FIXED by this diff (ONE discovered stream)"},
        {"consumer": "hdlab/situation_reader.py read() -> build_pronoun_targets (anaphora questions)",
         "reads": "same GOLD CLUSTER ID", "status": "FIXED by this diff (discovered_pronoun_targets)"},
        {"consumer": "hdlab/situation_reader.py _read_entities correctness",
         "reads": "gold cluster off the DECISION stream",
         "status": "FIXED by this diff (scorer-side alignment, after the pick)"},
        {"consumer": "hdlab/space_reader.py:248 (the SPACE dimension, track_space default ON)",
         "reads": "coref annotation column, RE-PARSED from the file",
         "status": "NOT FIXED -- outside the three files this brief may diff; measured below"},
        {"consumer": "hdlab/{bundle_focus_coref,coref_distractor_suppress,event_centrality_coref}.py"
                     " build_pronoun_targets",
         "reads": "gold clusters", "status": "NOT on the inference path -- all uses are _selftest_* only"},
    ]
    if verbose:
        for c in out["consumers"]:
            print("  %-78s %s" % (c["consumer"][:78], c["status"]))
        print("  COUNTS on %d text-only documents: %s" % (n_docs, json.dumps(out["counts"], sort_keys=True)))
    return out


# =====================================================================================================
# 10c. PATCH VERIFICATION -- the proposed .diff is not a sketch: load the PATCHED SOURCE of the three
#      hdlab files into the live module objects (same __file__, so every asset path still resolves) and
#      run the reader through it.  This proves the landed form of the arm behaves as the harness arm did.
#      hdlab/ on disk is never written.
# =====================================================================================================
def verify_patch(patched_dir, verbose=True):
    import hdlab.referent_per_np as RNP
    import hdlab.coref as CO
    import hdlab.situation_reader as SR
    order = [("coref.py", CO), ("referent_per_np.py", RNP), ("situation_reader.py", SR)]
    for fn, mod in order:
        src = open(os.path.join(patched_dir, "hdlab", fn), encoding="utf-8").read()
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    out = {"loaded": [fn for fn, _m in order]}
    assert hasattr(RNP, "PRONOUN_PHI") and RNP.pronoun_phi("He")["gender"] == "masc"
    assert hasattr(CO, "discovered_pronoun_targets") and hasattr(CO, "retrievable_referents")
    r = SR.SituationReader()
    assert r.discover_pronouns is True and r.pronoun_window == 0, "flag defaults wrong"
    # THE LIVE READ, text only
    sents = [["Alice", "thanked", "Bob", "."], ["She", "was", "happy", "."],
             ["They", "own", "blogger", ",", "of", "course", "."]]
    p = write_conll(sents)
    try:
        sm = SR.SituationReader().read(p)
    finally:
        os.unlink(p)
    out["events"] = [(e.sent_idx, e.predicate, e.agent, e.patient) for e in sm.events]
    out["pronouns"] = [(x.pronoun, x.sent_idx, x.target_wpos, x.resolved_head) for x in sm.coref_resolutions]
    out["abstentions"] = list(sm.pronoun_abstentions)
    out["states"] = [(s.sent_idx, s.holder, s.property) for s in sm.entity_states]
    assert out["pronouns"], "the PATCHED reader scheduled no pronoun question on text-only input"
    assert any(e[1] == "own" and (e[2] or "").lower() == "they" for e in out["events"]), \
        "the patched reader did not recover the pronoun AGENT of `They own blogger`: %r" % (out["events"],)
    # the A/B switch must still reproduce the old organ
    p = write_conll(sents)
    try:
        sm_off = SR.SituationReader(discover_pronouns=False).read(p)
    finally:
        os.unlink(p)
    out["off_pronouns"] = len(sm_off.coref_resolutions)
    assert out["off_pronouns"] == 0, "discover_pronouns=False did not reproduce the pre-patch organ"
    # ANNOTATION INVARIANCE through the PATCHED source
    fps = []
    rng = random.Random(SEED)
    for ann in (None, {}, {(0, 0): "(7)", (0, 2): "(3)", (1, 0): "(7)", (2, 0): "(3)"}):
        p = write_conll(sents, ann)
        try:
            fps.append(json.dumps(_decision_fingerprint(SR.SituationReader().read(p)), sort_keys=True))
        finally:
            os.unlink(p)
    out["invariant"] = (fps[0] == fps[1] == fps[2])
    assert out["invariant"], "the PATCHED reader is not annotation-invariant"
    # THE LANDED FORM ON THE FIVE EVALUATION DOCUMENTS -- the number the harness arm produced must be the
    # number the DIFF produces, or the diff ships a different organ.
    docs = load_ud_docs()[:5]
    tot = {"agent": 0, "agent_n": 0, "pron": 0, "pron_n": 0, "patient": 0, "patient_n": 0,
           "state": 0, "state_n": 0, "missing": 0, "coref": 0, "abstain": 0}
    for _docid, gold in docs:
        sents = [[t["form"] for t in s] for s in gold]
        p = write_conll(sents)
        try:
            sm = SR.SituationReader().read(p)
        finally:
            os.unlink(p)
        r = score_doc(sm, gold)
        tot["agent"] += sum(r["agent"]); tot["agent_n"] += len(r["agent"])
        tot["pron"] += sum(r["agent_pron"]); tot["pron_n"] += len(r["agent_pron"])
        tot["patient"] += sum(r["patient"]); tot["patient_n"] += len(r["patient"])
        tot["state"] += sum(r["state"]); tot["state_n"] += len(r["state"])
        tot["missing"] += r["missing"]
        tot["coref"] += len(sm.coref_resolutions)
        tot["abstain"] += len(sm.pronoun_abstentions)
    out["five_docs"] = tot
    if verbose:
        print("  PATCH VERIFY: five evaluation documents, text only -- AGENT %d/%d  pron %d/%d"
              "  PATIENT %d/%d  STATE %d/%d  missing %d  coref recs %d  open referents %d"
              % (tot["agent"], tot["agent_n"], tot["pron"], tot["pron_n"], tot["patient"],
                 tot["patient_n"], tot["state"], tot["state_n"], tot["missing"], tot["coref"],
                 tot["abstain"]))
    assert tot["agent"] >= 42 and tot["pron"] >= 31, \
        "the DIFF does not reproduce the harness arm's 42/52 and 31/33: %r" % (tot,)
    assert tot["patient"] == 30 and tot["state"] == 7, \
        "the DIFF changed a no-regress population: %r" % (tot,)
    if verbose:
        print("  PATCH VERIFY: events %r" % (out["events"],))
        print("  PATCH VERIFY: pronoun picks %r  abstentions %r" % (out["pronouns"], out["abstentions"]))
        print("  PATCH VERIFY: discover_pronouns=False -> %d pronoun records (pre-patch organ reproduced)"
              % out["off_pronouns"])
        print("  PATCH VERIFY: annotation-invariant across text-only / blank / linked-ids = %s"
              % out["invariant"])
    return out


# =====================================================================================================
# 10f. THE LANDED MEASUREMENT -- the bar, measured on the DIFF itself rather than on the harness arms,
#      BOTH ARMS IN ONE PROCESS.  The patched source is loaded into the live modules (10c), and the two
#      arms are then just two reader configurations of the LANDED organ:
#        landed   SituationReader()                                        -- the proposal
#        pre      SituationReader(discover_pronouns=False, case_cue_marked=False)  -- the pre-patch organ
#      Floors are recomputed on this population; the position twin is the information-free control.
# =====================================================================================================
def row_landed(patched_dir, n_docs=40, verbose=True, seed=SEED):
    verify_patch(patched_dir, verbose=False)
    import hdlab.situation_reader as SR
    from hdlab import frontend as F
    alldocs = load_ud_docs()
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(alldocs)), min(n_docs, len(alldocs))))
    docs = [alldocs[i] for i in idx]
    tagger = F.tagger()
    floor_ag, floor_pron = [], []
    for _docid, gold in docs:
        sents = [[t["form"] for t in s] for s in gold]
        tags = [tagger.tag(list(s)) for s in sents]
        a, ap = wordorder_agent_floor(sents, gold, tags)
        floor_ag.append(a); floor_pron.append(ap)
    cfgs = {"pre": {"discover_pronouns": False, "case_cue_marked": False},
            "landed": {},
            "landed_hybrid": {"agent_hybrid": True, "agent_hybrid_construction": True},
            "twin_pos": {}}
    per = {}
    for name, kw in cfgs.items():
        rows = []
        t0 = time.time()
        TWIN_POS["on"] = (name == "twin_pos")
        try:
            for _docid, gold in docs:
                sents = [[t["form"] for t in s] for s in gold]
                p = write_conll(sents)
                try:
                    sm = SR.SituationReader(**kw).read(p)
                finally:
                    os.unlink(p)
                r = score_doc(sm, gold)
                r["abstain"] = len(getattr(sm, "pronoun_abstentions", []) or [])
                r["coref"] = len(sm.coref_resolutions)
                rows.append(r)
        finally:
            TWIN_POS["on"] = False
        per[name] = rows
        if verbose:
            print("  %-14s AGENT %s  pron %s  PATIENT %s  STATE %s  coref %d  open %d  %.0fs"
                  % (name, _p(acc([r["agent"] for r in rows])), _p(acc([r["agent_pron"] for r in rows])),
                     _p(acc([r["patient"] for r in rows])), _p(acc([r["state"] for r in rows])),
                     sum(r["coref"] for r in rows), sum(r["abstain"] for r in rows), time.time() - t0))
    out = {"n_docs": len(docs), "docs": [d for d, _g in docs], "arms": {}, "contrasts": {},
           "floor": {"wordorder_agent": round(acc(floor_ag), 4),
                     "wordorder_agent_pron": round(acc(floor_pron), 4)}}
    for name, rows in per.items():
        out["arms"][name] = {k: (round(acc([r[k] for r in rows]), 4)
                                 if acc([r[k] for r in rows]) is not None else None)
                             for k in ("agent", "agent_pron", "patient", "state")}
        out["arms"][name]["n"] = {k: sum(len(r[k]) for r in rows)
                                  for k in ("agent", "agent_pron", "patient", "state")}
        out["arms"][name]["coref_records"] = sum(r["coref"] for r in rows)
        out["arms"][name]["open_referents"] = sum(r["abstain"] for r in rows)
    for name in per:
        if name == "pre":
            continue
        c = {}
        for k in ("agent", "agent_pron", "patient", "state"):
            c["vs_pre_" + k] = paired_boot([r[k] for r in per["pre"]], [r[k] for r in per[name]])
        c["vs_wordorder_floor_agent"] = paired_boot(floor_ag, [r["agent"] for r in per[name]])
        c["vs_wordorder_floor_agent_pron"] = paired_boot(floor_pron,
                                                         [r["agent_pron"] for r in per[name]])
        if name != "twin_pos":
            for k in ("agent", "agent_pron"):
                c["vs_twin_pos_" + k] = paired_boot([r[k] for r in per["twin_pos"]],
                                                    [r[k] for r in per[name]])
        out["contrasts"][name] = c
    return out


# =====================================================================================================
# 10g. THE LANDED PRONOUN INSTRUMENT -- the diff's own anaphora pick, scored on the same fixed question set,
#      with its floor and a VALID info-free twin, all in ONE process.
# =====================================================================================================
def row_landed_pron(patched_dir, n_docs=28, verbose=True):
    verify_patch(patched_dir, verbose=False)
    import hdlab.situation_reader as SR
    import hdlab.referent_per_np as RNP
    import hdlab.state_of_mind as SOM
    import experiments.gum_coref as G
    from hdlab import frontend as F
    scratch = os.path.join(OUT_DIR, "gum_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    test = alldocs[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    prepared = []
    for d in docs:
        pth = gum_textonly_conll(d, os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll"))
        prepared.append((d, pth, gum_pronoun_questions(d)))
    # the VALID twin permutes BOTH tables the landed organ reads: the patched module's own PRONOUN_PHI
    # (discovery + scheduling) and state_of_mind.PRONOUN_SCOPE (what the shipped pick re-derives from).
    phi_ship = {k: dict(v) for k, v in RNP.PRONOUN_PHI.items()}
    scope_ship = {k: dict(v) for k, v in SOM.PRONOUN_SCOPE.items()}

    def _twin_on():
        rng = random.Random(SEED)
        byp = defaultdict(list)
        for k, v in phi_ship.items():
            byp[v.get("person")].append(k)
        for _pp, ks in byp.items():
            ks = sorted(ks)
            gn = [(phi_ship[k]["gender"], phi_ship[k]["number"]) for k in ks]
            rng.shuffle(gn)
            for k, (g, n) in zip(ks, gn):
                RNP.PRONOUN_PHI[k] = dict(phi_ship[k], gender=g, number=n)
        ks = sorted(scope_ship)
        gn = [(scope_ship[k]["gender"], scope_ship[k]["number"]) for k in ks]
        random.Random(SEED + 1).shuffle(gn)
        for k, (g, n) in zip(ks, gn):
            SOM.PRONOUN_SCOPE[k]["gender"] = g
            SOM.PRONOUN_SCOPE[k]["number"] = n

    def _twin_off():
        for k, v in phi_ship.items():
            RNP.PRONOUN_PHI[k] = dict(v)
        for k, v in scope_ship.items():
            SOM.PRONOUN_SCOPE[k]["gender"] = v["gender"]
            SOM.PRONOUN_SCOPE[k]["number"] = v["number"]

    cfgs = {"landed": {}, "landed_overlay_pick": {"graded_anaphora": False},
            "landed_blankcard": {"fill_card": False}, "twin": {}}
    per = {}
    for name, kw in cfgs.items():
        if name == "twin":
            _twin_on()
        rows = []
        t0 = time.time()
        try:
            for d, pth, qs in prepared:
                sm = SR.SituationReader(**kw).read(pth)
                pick = {}
                for r in sm.coref_resolutions:
                    pick[(r.sent_idx, getattr(r, "target_wpos", -1))] = (r.resolved_head or "").lower()
                corr = [int(bool(pick.get((q["sent"], q["wpos"]))) and
                            pick.get((q["sent"], q["wpos"])) in q["gold_heads"]) for q in qs]
                rows.append({"doc": str(d.docid), "corr": corr, "n_q": len(qs),
                             "answered": sum(1 for q in qs
                                             if pick.get((q["sent"], q["wpos"])) not in (None, "")),
                             "open": len(getattr(sm, "pronoun_abstentions", []) or [])})
        finally:
            if name == "twin":
                _twin_off()
        per[name] = rows
        if verbose:
            print("  %-20s PRONOUN %s  (%d questions, %d answered, %d open referents)  %.0fs"
                  % (name, _p(acc([r["corr"] for r in rows])), sum(r["n_q"] for r in rows),
                     sum(r["answered"] for r in rows), sum(r["open"] for r in rows), time.time() - t0))
    # the floor on the same population
    tagger = F.tagger()
    floor = []
    for d, _pth, qs in prepared:
        by_sent = defaultdict(list)
        for t in d.toks:
            by_sent[t.sent].append(t)
        sents = [[t.form for t in sorted(by_sent[si], key=lambda x: x.idx)] for si in sorted(by_sent)]
        tags = [tagger.tag(list(x)) for x in sents]
        v = []
        for q in qs:
            tphi = RNP.pronoun_phi(q["form"]) or {}
            ans = None
            for si in range(q["sent"], -1, -1):
                lim = q["wpos"] if si == q["sent"] else len(sents[si])
                for wi in range(min(lim, len(sents[si])) - 1, -1, -1):
                    if tags[si][wi] not in ("NOUN", "PROPN"):
                        continue
                    from hdlab.state_of_mind import infer_nominal_gender
                    g = infer_nominal_gender([sents[si][wi]])
                    if tphi.get("gender") and g and tphi["gender"] != "any" and g != tphi["gender"]:
                        continue
                    ans = sents[si][wi].lower()
                    break
                if ans is not None:
                    break
            v.append(int(bool(ans) and ans in q["gold_heads"]))
        floor.append(v)
    out = {"n_docs": len(prepared), "floor_nearest_prior_compatible": round(acc(floor), 4), "arms": {},
           "contrasts": {}}
    for name, rows in per.items():
        out["arms"][name] = {"pronoun_acc": round(acc([r["corr"] for r in rows]), 4),
                             "n_questions": sum(r["n_q"] for r in rows),
                             "answered": sum(r["answered"] for r in rows),
                             "open_referents": sum(r["open"] for r in rows)}
        out["contrasts"]["%s_vs_floor" % name] = paired_boot(floor, [r["corr"] for r in rows])
    for name in per:
        if name != "twin":
            out["contrasts"]["%s_vs_twin" % name] = paired_boot([r["corr"] for r in per["twin"]],
                                                                [r["corr"] for r in per[name]])
    if verbose:
        print("  floor (nearest prior compatible referent) %s" % _p(out["floor_nearest_prior_compatible"]))
        for k, v in out["contrasts"].items():
            if v:
                print("    %-32s d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s"
                      % (k, v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return out


# =====================================================================================================
# 10h. THE LANDED ANNOTATED-PATH A/B -- the only measured REGRESSION, re-measured on the diff itself.
# =====================================================================================================
def row_landed_annab(patched_dir, n_docs=8, verbose=True):
    verify_patch(patched_dir, verbose=False)
    import hdlab.situation_reader as SR
    import experiments.gum_coref as G
    from experiments.exp_crosstype_gum_conll_fullread_v1 import gum_to_conll
    scratch = os.path.join(OUT_DIR, "gum_gold_conll")
    os.makedirs(scratch, exist_ok=True)
    alldocs = G.load_docs(gum_only=True, decision_source="gold")
    test = alldocs[1::2]
    step = max(1, len(test) // max(1, n_docs))
    docs = [test[i] for i in range(0, len(test), step)][:n_docs]
    prepared = []
    for d in docs:
        pth = os.path.join(scratch, str(d.docid).replace(" ", "_") + ".conll")
        gum_to_conll(d, pth)
        prepared.append((d, pth))
    cfgs = {"pre": {"discover_pronouns": False, "case_cue_marked": False, "graded_anaphora": False,
                    "fill_card": False},
            "landed": {}}
    per, out = {}, {"n_docs": len(prepared), "arms": {}, "contrasts": {}}
    for name, kw in cfgs.items():
        rows = []
        for d, pth in prepared:
            sm = SR.SituationReader(**kw).read(pth)
            rows.append({"doc": str(d.docid), "corr": [int(bool(r.correct)) for r in sm.coref_resolutions],
                         "n": len(sm.coref_resolutions), "events": len(sm.events),
                         "entities": len(sm.entities)})
        per[name] = rows
        out["arms"][name] = {"coref_acc": (round(acc([r["corr"] for r in rows]), 4)
                                           if acc([r["corr"] for r in rows]) is not None else None),
                             "n_targets": sum(r["n"] for r in rows),
                             "events": sum(r["events"] for r in rows),
                             "entities": sum(r["entities"] for r in rows)}
        if verbose:
            print("  %-8s ANNOTATED coref %s over %d targets  events %d  entities %d"
                  % (name, _p(out["arms"][name]["coref_acc"]), out["arms"][name]["n_targets"],
                     out["arms"][name]["events"], out["arms"][name]["entities"]))
    out["contrasts"]["landed_vs_pre"] = paired_boot([r["corr"] for r in per["pre"]],
                                                    [r["corr"] for r in per["landed"]])
    if verbose and out["contrasts"]["landed_vs_pre"]:
        v = out["contrasts"]["landed_vs_pre"]
        print("    landed - pre  d=%+.4f CI[%+.4f,%+.4f] half=%.4f sep=%s (NOTE: different question SETS --"
              " pre schedules only gold-linked he/she, landed schedules every third-person pronoun)"
              % (v["delta"], v["ci"][0], v["ci"][1], v["half"], v["sep"]))
    return out


# =====================================================================================================
# 11. SELF-TESTS (formula self-tests, can-fail)
# =====================================================================================================
def self_test(verbose=True):
    ok = 0
    # 1. the phi table covers the closed class and the twin really scrambles it
    restore_ship_phi()
    t = build_phi_table()
    assert t["he"]["gender"] == "masc" and t["she"]["gender"] == "fem", "phi table wrong"
    assert t["they"]["number"] == "plural" and t["i"]["person"] == "first", "phi person wrong"
    assert phi_of("He")["gender"] == "masc", "phi lookup not case-folded"
    ok += 1
    install_twin_phi()
    n_moved = sum(1 for k in t if (phi_of(k) or {}) != t[k])
    assert n_moved > 10, "twin did not scramble the agreement cue (%d moved)" % n_moved
    restore_ship_phi()
    assert phi_of("he")["gender"] == "masc", "restore failed"
    ok += 1
    # 2. the target builder schedules on the DISCOVERED stream and abstains explicitly
    ments = [
        {"midx": 0, "sent_idx": 0, "wtok_start": 0, "head": "alice", "is_pronoun": False,
         "gender": "fem", "number": None, "span_upos": ["PROPN"], "cluster": 0},
        {"midx": 1, "sent_idx": 0, "wtok_start": 2, "head": "bob", "is_pronoun": False,
         "gender": "masc", "number": None, "span_upos": ["PROPN"], "cluster": 1},
        _pron_mention("she", 1, 0, 2, "PRON"),
        _pron_mention("it", 2, 0, 3, "PRON"),
    ]
    for i, m in enumerate(ments):
        m["midx"] = i
    tg, ab = discovered_pronoun_targets(ments, window=0)
    assert len(tg) == 1 and tg[0]["target"]["head"] == "she", "she not scheduled: %r" % tg
    assert tg[0]["antecedent"]["head"] == "alice", "phi cue not applied: %r" % tg[0]["antecedent"]["head"]
    assert len(ab) == 1 and ab[0]["head"] == "it", "no explicit abstention for `it`: %r" % ab
    assert ab[0]["wtok_start"] == 0 and ab[0]["sent_idx"] == 2, "abstention has no token position"
    ok += 1
    # 3. CAN-FAIL: the agreement cue is LOAD-BEARING -- scrambling phi must change the floor's antecedent
    #    picks on a substantial share of a multi-pronoun fixture (a single form can survive a permutation
    #    by chance, so the claim is made over the inventory, which is what "information-free" means).
    fixture = [
        {"midx": 0, "sent_idx": 0, "wtok_start": 0, "head": "alice", "is_pronoun": False,
         "gender": "fem", "number": "singular", "span_upos": ["PROPN"], "cluster": 0},
        {"midx": 1, "sent_idx": 0, "wtok_start": 3, "head": "bob", "is_pronoun": False,
         "gender": "masc", "number": "singular", "span_upos": ["PROPN"], "cluster": 1},
        {"midx": 2, "sent_idx": 0, "wtok_start": 6, "head": "sisters", "is_pronoun": False,
         "gender": "fem", "number": "plural", "span_upos": ["NOUN"], "cluster": 2},
    ]
    forms = ("she", "he", "her", "him", "they", "them", "his", "it")

    def _fx():
        fx = [dict(m) for m in fixture]
        for j, f in enumerate(forms):
            fx.append(_pron_mention(f, 1 + j, 0, 50 + j, "PRON"))   # built UNDER the live phi table
        for i, m in enumerate(fx):
            m["midx"] = i
        return fx

    ship_pick = {t["target"]["head"]: t["antecedent"]["head"]
                 for t in discovered_pronoun_targets(_fx(), window=0)[0]}
    install_twin_phi()
    twin_pick = {t["target"]["head"]: t["antecedent"]["head"]
                 for t in discovered_pronoun_targets(_fx(), window=0)[0]}
    restore_ship_phi()
    moved = sum(1 for k in ship_pick if twin_pick.get(k) != ship_pick[k])
    assert moved >= max(1, len(ship_pick) // 3), \
        "the twin reproduces the true picks (%d/%d moved) -- the cue is not load-bearing" % (
            moved, len(ship_pick))
    ok += 1
    # 4. the accessibility window really bounds retrieval
    far = [dict(ments[0]), _pron_mention("she", 9, 0, 5, "PRON")]
    for i, m in enumerate(far):
        m["midx"] = i
    assert len(discovered_pronoun_targets(far, window=2)[0]) == 0, "window does not bound retrieval"
    assert len(discovered_pronoun_targets(far, window=0)[0]) == 1, "window=0 should be unbounded"
    ok += 1
    # 5. the pool filter keeps featured referents and drops feature-blank inanimates
    pool = anaphora_pool(ments + [{"midx": 9, "sent_idx": 0, "wtok_start": 5, "head": "table",
                                   "is_pronoun": False, "gender": None, "number": None,
                                   "span_upos": ["NOUN"], "cluster": 9}])
    assert all(m["head"] != "table" for m in pool), "inanimate feature-blank referent not filtered"
    assert any(m["head"] == "alice" for m in pool), "gendered name dropped from the pool"
    ok += 1
    # 6. THE ORGAN, ON WHICHEVER TREE THIS RUNS ON.  With the pri-125 diff APPLIED the arms DELEGATE, so
    #    this exercises the LANDED organ with no monkeypatch at all; on an unpatched tree it exercises the
    #    overlay.  The claim is the same either way and it can fail either way.
    from hdlab.situation_reader import SituationReader
    sents = [["Alice", "thanked", "Bob", "."], ["She", "was", "happy", "."],
             ["They", "own", "blogger", ",", "of", "course", "."]]
    p = write_conll(sents)
    live = None
    try:
        with Arm("ship") as _a:
            a = SituationReader(**reader_kw("ship")).read(p)
            ship_delegated = _a.delegated
        with Arm("disc") as _b:
            b = SituationReader(**reader_kw("disc")).read(p)
            disc_delegated = _b.delegated
        if live_patched():
            live = SituationReader().read(p)        # the organ exactly as it ships, no arm involved
    finally:
        os.unlink(p)
    assert len(a.coref_resolutions) == 0, \
        "the PRE-PATCH organ already resolves on text-only (%d records)" % len(a.coref_resolutions)
    assert len(b.coref_resolutions) >= 1, "discovery scheduled no pronoun question on text-only"
    assert b.coref_resolutions[0].resolved_head, "no antecedent named"
    if live is not None:
        assert len(live.coref_resolutions) >= 1, \
            "THE LANDED ORGAN scheduled no pronoun question on annotation-free text"
        assert any((e.agent or "").lower() == "they"
                   for e in live.events if e.predicate == "own"), \
            "the LANDED organ did not recover the pronoun AGENT of `They own blogger`: %r" % (
                [(e.predicate, e.agent) for e in live.events],)
        assert ship_delegated and disc_delegated, \
            "the diff is landed but the cell monkeypatched instead of delegating to hdlab"
    ok += 1
    # 7. nothing leaked past the with-block, on either path
    import hdlab.referent_per_np as RNP
    import hdlab.situation_reader as SR
    from hdlab.coref import parse_litbank_conll as real_plc, build_pronoun_targets as real_bpt
    assert SR.parse_litbank_conll is real_plc and SR.build_pronoun_targets is real_bpt, \
        "arm leaked past its with-block"
    if live_patched():
        assert RNP.PRONOUN_PHI["he"]["gender"] == "masc", "the twin's PRONOUN_PHI permutation leaked"
        import hdlab.state_of_mind as SOM
        assert SOM.PRONOUN_SCOPE["she"]["gender"] == "fem", "the twin's PRONOUN_SCOPE permutation leaked"
    ok += 1
    if verbose:
        print("SELF-TEST %d/8 PASS (tree: %s)"
              % (ok, "pri-125 diff APPLIED -- arms DELEGATE to hdlab" if live_patched()
                 else "unpatched -- arms installed by rebinding"))
    return ok


# =====================================================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--repro", action="store_true")
    ap.add_argument("--invariance", action="store_true")
    ap.add_argument("--agents", type=int, default=0)
    ap.add_argument("--pronouns", type=int, default=0)
    ap.add_argument("--window-sweep", type=int, default=0, dest="window_sweep")
    ap.add_argument("--trace", type=int, default=0)
    ap.add_argument("--verify-patch", type=str, default="", dest="verify_patch")
    ap.add_argument("--consumer-audit", type=int, default=0, dest="consumer_audit")
    ap.add_argument("--annotated-ab", type=int, default=0, dest="annotated_ab")
    ap.add_argument("--landed", type=int, default=0)
    ap.add_argument("--landed-pron", type=int, default=0, dest="landed_pron")
    ap.add_argument("--landed-annab", type=int, default=0, dest="landed_annab")
    ap.add_argument("--patched", type=str, default="")
    ap.add_argument("--arms", type=str, default="")
    ap.add_argument("--window", type=int, default=None)
    ap.add_argument("--tag", type=str, default="")
    a = ap.parse_args()
    arms = tuple(x for x in a.arms.split(",") if x) or ARMS
    _extend_coref_resolution()
    res = {"ts_iso": datetime.now(timezone.utc).isoformat(), "seed": SEED, "arms": list(arms)}
    if a.self_test:
        res["self_test"] = self_test()
    if a.repro:
        print("== ROW: the five evaluation documents, its exact scorer ==")
        res["repro"] = row_repro(arms=arms)
    if a.invariance:
        print("== ROW: annotation invariance (text-only / blank / permuted cluster ids) ==")
        res["invariance"] = row_invariance(arms=arms)
    if a.agents:
        print("== ROW: %d-document UD-EWT sample -- agent / patient / state ==" % a.agents)
        res["agents"] = row_agents(n_docs=a.agents, arms=arms, window=a.window)
    if a.pronouns:
        print("== ROW: the reader's own pronoun instrument, MODERN GUM test, text only ==")
        res["pronouns"] = row_pronouns(n_docs=a.pronouns, arms=arms, window=a.window)
    if a.trace:
        print("== ROW: the signal-loss trace, chain by chain ==")
        res["trace"] = row_trace(n_docs=a.trace, arms=tuple(x for x in arms if x in ("ship", "disc_role",
                                                                                     "disc")))
    if a.window_sweep:
        print("== ROW: accessibility-window sweep ==")
        res["window_sweep"] = row_window_sweep(n_docs=a.window_sweep)
    if a.landed:
        print("== ROW: THE LANDED MEASUREMENT -- the diff itself, both arms in ONE process ==")
        res["landed"] = row_landed(a.patched, n_docs=a.landed)
    if a.landed_pron:
        print("== ROW: THE LANDED PRONOUN INSTRUMENT -- the diff's own pick, its floor and a valid twin ==")
        res["landed_pron"] = row_landed_pron(a.patched, n_docs=a.landed_pron)
    if a.landed_annab:
        print("== ROW: THE LANDED ANNOTATED-PATH A/B (the only measured regression, on the diff itself) ==")
        res["landed_annab"] = row_landed_annab(a.patched, n_docs=a.landed_annab)
    if a.annotated_ab:
        print("== ROW: the ANNOTATED-path A/B (the reader's own annotated read; the board rows never run it) ==")
        res["annotated_ab"] = row_annotated_ab(n_docs=a.annotated_ab, arms=arms)
    if a.consumer_audit:
        print("== ROW: the consumer audit -- every inference-path reader of the annotation column ==")
        res["consumer_audit"] = row_consumer_audit(n_docs=a.consumer_audit)
    if a.verify_patch:
        print("== PATCH VERIFICATION: the proposed diff, loaded and run ==")
        res["verify_patch"] = verify_patch(a.verify_patch)
    name = "metrics" + (("_" + a.tag) if a.tag else "") + ".json"
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, default=str)
    print("WROTE %s" % os.path.join(OUT_DIR, name))


if __name__ == "__main__":
    main()
