"""hdlab/referent_per_np.py -- the REFERENT-PER-NP candidate source, promoted VERBATIM (2026-09-03) from the
owner-DONE `open_a_discourse_referent_for_every_np_not_just_coref_mentions`
(`experiments/exp_referent_per_np_end_to_end_v1.build_source(mode='rnp')` + `..._frame_detection_v1.frame_heads`).

WHY. The deployed reader sources who-did-what CANDIDATES from the CoNLL COREF column, so on real 19c prose the
gold patient is even a candidate only ~0.82 of the time (entity-typed coref annotates ~9% of content nouns) -- a
DEPLOYMENT ceiling invisible to the noun-supplied eval. The brain-faithful operation (Kamp 1981 DRT / Heim 1982
FCS; MTL concept cells + hippocampal indexing; open-broad-then-revise) is to INTRODUCE a discourse referent for
EVERY content-noun-head NP, with coreference a DOWNSTREAM linking pass -- NOT the candidate source. This organ is
that source: it REUSES the real coref parse for pronouns/clusters/gender, opens a referent per content-noun head
(reusing the coref cluster where a coref span already covers that head, else a fresh singleton the linker connects
downstream), and returns the parse_litbank_conll mention schema so every reader path behaves identically.

MEASURED (through the LIVE reader, mention source swapped, else identical; 25 real LitBank docs): effective
end-to-end who-did-what on the cleaned-DO instrument 0.4698 -> 0.8054 (+0.336 CI-sep), the info-free twin
(matched-count random-position referents) LOSES AND HURTS, NO regression on the noun-supplied eval (rnp==supplied),
REPLACE (sole source 0.805) BEATS the additive union (0.403 -- the DRT order), who-has-what theme coverage +0.115.
Introduction is register-INVARIANT (0.983 modern / 0.978 19c) -- register-sensitivity lives in the trained LINKER.

FRAME DETECTOR (§4, use_frame=True default): the brain identifies an NP by its syntactic FRAME (determiner/
possessive left-edge + head, or mid-sentence capital for a name -- function-word bootstrapping, Abney 1991), so a
frame pass RECOVERS content heads the 19c POS tagger mis-tags (introduction coverage 0.914 -> 0.931, +0.017 CI-sep,
twin loses) and is REGISTER-ROBUST by construction (closed-class function words survive archaic prose). Glass-box,
NO external LLM. The discrete referent structure is a defensible OUR-INVENTION (no dedicated neural file-opener is
attested -- Nieuwland 2019); the DRT introduction OPERATION is PINNED.
"""
from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (reader CATALOG owner-DONE + BRAIN_FOUNDATIONAL_AUDIT §2b; strategy first-hand cross-ref)'
__bf_note__ = 'Kamp/Heim DRT one-referent-per-NP discourse construction; CAT genuinely-BF'
__bf_corrections__ = []


from typing import Dict, List, Optional, Sequence, Set

from hdlab.coref import parse_litbank_conll
from hdlab.scene_segment import parse_conll_sentences
from hdlab.thematic_role_labeler import is_known_word
from hdlab.verb_role_exemplar_selector import STOP           # == the validated cell's V1.STOP (verified equal)

NOMINAL = ("NOUN", "PROPN")
# frozen from the validated cell (exp_referent_per_np_frame_detection_v1)
DETERMINERS = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their",
    "one", "each", "every", "any", "some", "no", "another", "such", "both", "all", "few", "many", "several"})
NEVER_HEAD = frozenset({"ADP", "AUX", "CCONJ", "SCONJ", "PART", "PUNCT", "SYM", "DET", "PRON"})
BROAD_PRON = frozenset({
    "i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves", "this", "that", "these", "those", "which", "who",
    "whom", "whose"})


# ---------------------------------------------------------------------------------------------------
# THE PRONOUN ARM (pri 125, 2026-09-15).  A pronoun is a referent-INTRODUCING expression like any other
# NP: it opens a discourse referent whose file card is empty except for a RETRIEVAL DEMAND (Kamp 1981 DRT
# / Heim 1982 FCS), to be identified with an accessible prior referent by cue-based retrieval (Lewis &
# Vasishth 2005 ACT-R), the retrieval cues being the FORM's own phi-features.  Before this arm the organ
# took its pronouns from `parse_litbank_conll` -- the input's COREF ANNOTATION COLUMN -- so on
# annotation-free text the reader had NO pronoun mentions at all: `_cm_agent_candidates` returned
# (None, None) on the empty stream and `build_pronoun_targets` scheduled nothing.  MEASURED on the first
# five UD-EWT test documents, text only, the evaluation's own scorer: agent 9/52 and 0/33 pronoun agents
# before, 40/52 and 28/33 after (patients 30/43 and states 7/9 unchanged).
# The closed class is decided by the CATEGORY ORGAN (it tags PRON on 33/33 of those gold pronoun agents);
# the features are a property of the FORM, read out of the tables the substrate already holds -- ONE
# table composed from them, not a new one.
# ---------------------------------------------------------------------------------------------------
def _build_pronoun_phi() -> Dict[str, Dict]:
    from hdlab.state_of_mind import PRONOUN_SCOPE, FIRST_PERSON_PRONOUNS, SECOND_PERSON_PRONOUNS
    from hdlab.affected_entity_resolver import REFLEXIVE_GN
    phi: Dict[str, Dict] = {}
    for f, d in PRONOUN_SCOPE.items():                       # 3rd-person gender/number
        phi[f] = {"gender": d["gender"], "number": d["number"], "person": "third"}
    for f, (g, n) in REFLEXIVE_GN.items():                   # reflexives (Binding Principle A)
        phi[f] = {"gender": g, "number": n, "person": "third"}
    phi.setdefault("theirs", {"gender": "any", "number": "plural", "person": "third"})
    for f in FIRST_PERSON_PRONOUNS:                          # the discourse-participant deixis classes
        phi[f] = {"gender": None, "person": "first",
                  "number": ("plural" if f.startswith(("we", "us", "our")) else "singular")}
    for f in SECOND_PERSON_PRONOUNS:
        phi[f] = {"gender": None, "number": None, "person": "second"}
    for f, n in (("this", "singular"), ("that", "singular"),  # demonstratives used as an NP
                 ("these", "plural"), ("those", "plural")):
        phi[f] = {"gender": "neuter", "number": n, "person": "third"}
    return phi


PRONOUN_PHI: Dict[str, Dict] = _build_pronoun_phi()


def pronoun_phi(form: Optional[str]) -> Optional[Dict]:
    """The form's own phi-features, or None when the lexicon has no entry for it (an indefinite or a
    relative): the referent still OPENS -- an open retrieval demand -- the organ simply has no agreement
    cue to retrieve with, which is the honest state, not a reason to drop the referent."""
    return PRONOUN_PHI.get((form or "").lower().strip(".,\'\"!?;:"))


def _mk_pronoun_referent(form_low: str, sent_idx: int, wpos: int, cluster: int,
                         upos: Optional[str] = None) -> Dict:
    """A DISCOVERED pronoun mention in the parse_litbank_conll schema. `discovered` marks the provenance
    (this organ, from the category organ's tag) so a consumer can tell it from a column mention."""
    d = pronoun_phi(form_low) or {}
    return {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
            "wtok_start": wpos, "head": form_low, "is_pronoun": True,
            "gender": d.get("gender"), "number": d.get("number"), "name_gender": None,
            "span_toks": [form_low], "midx": -1, "span_upos": [upos or "PRON"],
            "person": d.get("person"), "discovered": True}


def _content_head_positions(toks: Sequence[str], up: Sequence[str]) -> List[int]:
    """Referent-per-NP head set (Kamp/Heim): token indices of every content-noun head (NOUN/PROPN, non-STOP,
    len>=3). VERBATIM the validated prototype's coverage rule."""
    return [i for i, u in enumerate(up)
            if u in NOMINAL and toks[i].lower() not in STOP and len(toks[i]) >= 3]


def frame_heads(toks: Sequence[str], up: Sequence[str], base: Set[int]) -> Set[int]:
    """FRAME-based recovery of content heads the POS tagger MISSED (VERBATIM the validated cell): (1) a
    mid-sentence CAPITAL = a likely proper name the tagger mis-class'd; (2) a DETERMINER/possessive immediately-
    left edge with a real (known) content head. Never emits a function word / pronoun / non-word."""
    add: Set[int] = set()
    for i in range(len(toks)):
        if i in base:
            continue
        w = toks[i]; wl = w.lower()
        if len(wl) < 3 or wl in STOP or wl in BROAD_PRON or up[i] in NEVER_HEAD:
            continue
        cap = (i > 0 and w[:1].isupper())
        det_left = (i > 0 and toks[i - 1].lower() in DETERMINERS)
        det_left2 = (i > 1 and toks[i - 2].lower() in DETERMINERS and up[i - 1] in ("ADJ", "NOUN", "PROPN"))
        if cap or ((det_left or det_left2) and is_known_word(wl)):
            add.add(i)
    return add


def _file_card_features(head_low: str, upos: Optional[str], name_gender_map=None):
    """THE FILE CARD'S CONCEPTUAL FEATURES, filled AT INTRODUCTION (pri 125, 2026-09-15).

    THE MEASURED DEFECT THIS FIXES.  `_mk_referent` wrote `gender=None`, `number=None`, `name_gender=None`
    on EVERY referent, while `parse_litbank_conll` (the column source it replaced) computed
    `infer_nominal_gender(span_toks)` and the gazetteer gender for each of its mentions.  So the discourse
    referents the reader introduces itself carry a BLANK card, and every downstream cue that retrieves BY
    agreement is inert against them -- measured directly in this cell: an anaphora pick with a graded phi
    cue term weighted 4.0 scored 0.1791 and an ablation with that term set to 0.0 scored 0.1791, byte-
    identical, on 67 GUM test questions.  A cue cannot be load-bearing when the thing it matches against is
    always None.  This is the same blank-card diagnosis the 2026-09-03 SOLVED recorded for the coref
    collapse (`coref_acc` 0.4693 -> 0.1019: "leaves the file-card's conceptual features blank ... which
    blinds the brain's agreement+animacy retrieval cue"), still unfixed at the introduction organ.

    THE BRAIN: a discourse referent is a file card that carries the entity's CONCEPTUAL features -- person,
    gender, number, animacy -- bound from lexical semantics as the NP is read (Kamp/Heim file cards; MTL
    concept cells feeding the anterior-temporal hub).  Introduction and feature-binding are the SAME act.
    Every source here is already an organ on the read path: `state_of_mind.infer_nominal_gender` (title /
    kinship cues), `coref.name_gender_for_span` (the offline given-name gazetteer), and the substrate's own
    glass-box morphology for number.  NO new dependency, no external tool at inference."""
    from hdlab.state_of_mind import infer_nominal_gender
    gender = infer_nominal_gender([head_low])
    ng = None
    if gender is None and name_gender_map and upos == "PROPN":
        # the gazetteer is a PROPER-NAME list, so consult it only for a head the category organ calls a
        # PROPN; without the gate it fires on a mis-tagged common noun or verb ("saw" -> masc, observed).
        from hdlab.coref import name_gender_for_span
        ng = name_gender_for_span([head_low], name_gender_map)
    number = None
    if upos in ("NOUN", "PROPN"):
        try:
            from hdlab.morphology import default_morphology
            base = default_morphology().morphy(head_low, "n")
            if base and base != head_low:
                number = "plural"          # the surface form is an inflected plural of a known base
            elif base == head_low and not head_low.endswith("s"):
                number = "singular"
        except Exception:
            number = None
    return gender, number, ng


def _mk_referent(head_low: str, sent_idx: int, wpos: int, cluster: int, midx: int,
                 upos: Optional[str] = None, tag_post=None, tags=None,
                 name_gender_map=None, fill_card: bool = True) -> Dict:
    """A discourse-referent mention dict in the parse_litbank_conll schema (single-token, non-pronoun).

    MEASURED DEFECT THIS FIXES (pri-109, 8 LitBank docs): `span_toks` is the LOWERCASED head, and the ten
    organs that type a mention call `coref.name_content_tokens`, which decides by CAPITALISATION. So on the
    LIVE reader's default entity stream the name decision was structurally degenerate -- 0 of 2,123
    non-pronoun mentions could EVER be typed a name (100% of spans all-lowercase), against 166 of 720 on the
    raw-cased coref-column stream. `upos` = the category organ's category for this head, so the name decision
    becomes the organ's and survives the lowercasing: 150 name mentions typed where there were 0."""
    _g, _n, _ng = (_file_card_features(head_low, upos, name_gender_map) if fill_card
                   else (None, None, None))
    d = {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
         "wtok_start": wpos, "head": head_low, "is_pronoun": False,
         "gender": _g, "number": _n, "name_gender": _ng, "span_toks": [head_low], "midx": midx}
    if upos is not None:
        d["span_upos"] = [upos]
    if tag_post is not None:
        # pri 118: the category organ's POSTERIOR row for this head, so `coref.name_content_tokens` can
        # marginalise over the type partition instead of branching on the argmax.  MEASURED on the reader's
        # own stream (16 GUM test documents, 4,059 non-pronoun mentions): it changes 9 typings -- the lever
        # that carries the gain on the board loader's stream is the SPAN-level name-run cue, and it is INERT
        # here because this builder stores span_toks=[head], ONE token per mention.  Keeping the NP span is
        # the next rung and is filed as such.
        d["span_post"] = [tag_post]
        d["span_tags"] = tags
    return d


def _finalize(mentions: List[Dict]) -> List[Dict]:
    """Recompute midx + per-sentence grammatical-role rank (subjecthood proxy), exactly as parse_litbank_conll
    does, so _sentence_nominals / _pick_role_mentions behave identically."""
    mentions.sort(key=lambda m: (m["sent_idx"], m["wtok_start"], m.get("gtok_start", 0)))
    for i, m in enumerate(mentions):
        m["midx"] = i
    by_sent: Dict[int, List[Dict]] = {}
    for m in mentions:
        by_sent.setdefault(m["sent_idx"], []).append(m)
    for lst in by_sent.values():
        for rank, m in enumerate(sorted(lst, key=lambda mm: (mm["wtok_start"], mm["midx"]))):
            m["sent_role_rank"] = rank
            m["is_subject"] = (rank == 0)
    return mentions


def referent_per_np_source(conll_path: str, tagger, name_gender_map=None, use_frame: bool = True,
                          discover_pronouns: bool = True, fill_card: bool = True):
    """THE candidate source: a discourse referent per content-noun-head NP (+ the determiner/name FRAME detector
    when use_frame), coref pronouns/clusters PRESERVED (coref demoted to a downstream linking pass). REPLACES the
    coref-column candidate source. Returns (mentions, n_sents) in the parse_litbank_conll schema -- a drop-in for
    `mentions, n_sents = parse_litbank_conll(...)`. `tagger` = the reader's frontend UPOS PosTagger. VERBATIM to
    the validated build_source(mode='rnp'): use_frame=False reproduces the +0.336 source byte-for-byte; use_frame=
    True adds the §4 frame recoveries on top (introduction 0.914->0.931).

    `discover_pronouns=True` (pri 125, the DEFAULT): the pronoun referents come from the CATEGORY ORGAN's
    own PRON tags on the reader's own tokens, in reading order -- so the organ discovers its mentions from
    TEXT and the coref annotation column reaches no decision.  `discover_pronouns=False` reproduces the
    pre-2026-09-15 organ byte-for-byte (pronouns lifted from the column), for A/B only."""
    coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=name_gender_map, tagger=tagger)
    sents = parse_conll_sentences(conll_path, lower=False)  # pri-116: cased -- +0.4106 PROPN F1 (see scene_segment);
    # `frame_heads`' mid-sentence-CAPITAL cue can fire again, and `_content_head_positions` opens a referent for
    # every content noun the organ can now see. MEASURED through the live reader on 16 modern GUM test documents:
    # entity files 2,459 -> 2,563 (+4.2%), NAME-typed referent mentions 242 -> 599 (2.48x).
    coref_head_wpos: Dict[tuple, int] = {}
    # REFLEXIVES (himself/herself/itself/themselves) are pronouns too (Binding Principle A; strategy 2026-09-12):
    # the CoNLL mention stream marks only PRONOUN_SCOPE forms as pronouns, so a reflexive coref mention was dropped
    # here (neither a pronoun nor a content-noun head). Keep it as a pronoun mention with its form's gender/number.
    from hdlab.affected_entity_resolver import is_reflexive, REFLEXIVE_GN
    pron = []
    if not discover_pronouns:
        for m in coref:
            if m["is_pronoun"]:
                pron.append(m)
            elif is_reflexive(m.get("head")):
                g, n = REFLEXIVE_GN.get(m["head"].lower(), (None, None))
                m = dict(m); m["is_pronoun"] = True
                m["gender"] = m.get("gender") or g; m["number"] = m.get("number") or n
                pron.append(m)
    refl_pos = {(m["sent_idx"], m["wtok_start"]) for m in pron if is_reflexive(m.get("head"))}
    for m in coref:
        if m["is_pronoun"] or is_reflexive(m.get("head")):
            continue
        span = max(0, m["gtok_end"] - m["gtok_start"])
        coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    next_cluster = max([m["cluster"] for m in coref], default=-1) + 1
    out: List[Dict] = []
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        mat = None
        if hasattr(tagger, "tag_with_posterior"):      # capability, not assumption (the perceptron has none)
            try:
                _c, mat = tagger.tag_with_posterior(list(toks))
            except Exception:
                mat = None
        _tags = None
        if mat is not None:
            from hdlab import frontend as _F
            _lc = getattr(_F.tagger(), "_lc", None)
            _tags = list(_lc.tags) if _lc is not None else None
        base = _content_head_positions(toks, up)
        heads = sorted(set(base) | frame_heads(toks, up, set(base))) if use_frame else base
        # THE PRONOUN ARM: open a referent for every PRON the category organ tags in THIS sentence, in
        # reading order (the in-order feed of pri 112 -- no whole-passage pass).  Possessive pronouns are
        # kept: "his mother" refers to the POSSESSOR, a discourse referent of its own (the CASE cue in
        # `_cm_agent_candidates` is what keeps an oblique form out of the AGENT competition, not this organ).
        pron_pos = set()
        if discover_pronouns:
            for wi, w in enumerate(toks):
                if wi >= len(up) or up[wi] != "PRON":
                    continue
                pron.append(_mk_pronoun_referent(w.lower(), si, wi, next_cluster, up[wi]))
                next_cluster += 1
                pron_pos.add(wi)
        for hw in heads:
            if (si, hw) in refl_pos or hw in pron_pos:
                continue                                   # the reflexive/pronoun is already a mention
            cl = coref_head_wpos.get((si, hw))
            if cl is None:
                cl = next_cluster
                next_cluster += 1
            out.append(_mk_referent(toks[hw].lower(), si, hw, cl, -1,
                                    upos=up[hw] if hw < len(up) else None,
                                    tag_post=(mat[hw] if (mat is not None and hw < len(mat)
                                                          and _tags) else None),
                                    tags=_tags,
                                    name_gender_map=name_gender_map, fill_card=fill_card))
    return _finalize(pron + out), n_sents
