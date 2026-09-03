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


def _mk_referent(head_low: str, sent_idx: int, wpos: int, cluster: int, midx: int) -> Dict:
    """A discourse-referent mention dict in the parse_litbank_conll schema (single-token, non-pronoun)."""
    return {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
            "wtok_start": wpos, "head": head_low, "is_pronoun": False,
            "gender": None, "number": None, "name_gender": None, "span_toks": [head_low], "midx": midx}


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


def referent_per_np_source(conll_path: str, tagger, name_gender_map=None, use_frame: bool = True):
    """THE candidate source: a discourse referent per content-noun-head NP (+ the determiner/name FRAME detector
    when use_frame), coref pronouns/clusters PRESERVED (coref demoted to a downstream linking pass). REPLACES the
    coref-column candidate source. Returns (mentions, n_sents) in the parse_litbank_conll schema -- a drop-in for
    `mentions, n_sents = parse_litbank_conll(...)`. `tagger` = the reader's frontend UPOS PosTagger. VERBATIM to
    the validated build_source(mode='rnp'): use_frame=False reproduces the +0.336 source byte-for-byte; use_frame=
    True adds the §4 frame recoveries on top (introduction 0.914->0.931)."""
    coref, n_sents = parse_litbank_conll(conll_path, name_gender_map=name_gender_map)
    sents = parse_conll_sentences(conll_path)
    coref_head_wpos: Dict[tuple, int] = {}
    pron = [m for m in coref if m["is_pronoun"]]
    for m in coref:
        if m["is_pronoun"]:
            continue
        span = max(0, m["gtok_end"] - m["gtok_start"])
        coref_head_wpos[(m["sent_idx"], m["wtok_start"] + span)] = m["cluster"]
    next_cluster = max([m["cluster"] for m in coref], default=-1) + 1
    out: List[Dict] = []
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        base = _content_head_positions(toks, up)
        heads = sorted(set(base) | frame_heads(toks, up, set(base))) if use_frame else base
        for hw in heads:
            cl = coref_head_wpos.get((si, hw))
            if cl is None:
                cl = next_cluster
                next_cluster += 1
            out.append(_mk_referent(toks[hw].lower(), si, hw, cl, -1))
    return _finalize(pron + out), n_sents
