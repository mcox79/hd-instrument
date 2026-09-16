"""Reusable cross-sentence pronoun-coreference primitive for the situation model.

This is the ENTITY / REFERENCE BACKBONE of the Kintsch/van-Dijk situation model:
a per-sentence reader pass that (1) adds new entities to a persistent working
overlay and (2) resolves pronouns against the running overlay, INCLUDING
antecedents introduced in PRIOR sentences.

WHAT THIS MODULE HOISTS (the situation-model phase needs a clean primitive):
  - LitBank coref-CoNLL loading WITH sentence boundaries (parse_litbank_conll).
  - pronoun -> gold-antecedent target extraction, stratified by SENTENCE distance
    (build_pronoun_targets + sent_dist_bucket): same-sentence / +1 / +2 / long.
  - CorefReader: the per-sentence reader pass that wires the VALIDATED symbolic
    WorkingOverlay (hdlab.state_of_mind) into a reading loop. Pluggable:
      * reset_per_sentence=True  -> SINGLE-SENTENCE baseline (within-sentence
        antecedents only; the cross-sentence-memory ablation).
      * reset_per_sentence=False -> CROSS-SENTENCE reader (the situation-model
        backbone: entities persist across sentence boundaries).
    strategy in {recency, recency_window, maintained, freq} is passed straight
    through to the validated WorkingOverlay resolvers (no reinvention).

PROVENANCE (faithful reuse, nothing improved over validated logic):
  - WorkingOverlay + resolvers + salience arithmetic + gender/number agreement:
    hdlab/state_of_mind.py (packaged from longdist 49bb99c24; VET a7ca3db1).
  - CoNLL gold-mention parsing pattern + surface-head entity grouping:
    experiments/exp_read_discourse_overlay_longdist_reference_v1.py.

ANTI-CIRCULAR / FAITHFUL CHOICE (matches validated longdist behavior): resolved
pronouns are NOT chained into their antecedent entity (pronouns never create or
update entities in WorkingOverlay). Gold cluster ids are used ONLY to (a) stratify
targets by distance and (b) score correctness; the resolver NEVER sees gold coref
linking. Scoring maps a resolved entity to a gold cluster via the gold cluster of
that entity's most-recent observed nominal mention (head_to_cluster side-map).

GLASS-BOX: pure symbolic; NO torch, NO external LLM, NO network. ASCII-only.
"""

from __future__ import annotations

__bf_status__ = 'BF_SPIRIT'   # BF | BF_SPIRIT | NOT_BF | BF_UNPINNED | BF_UNVERIFIED ; mirrors notes/bf_status_registry.jsonl
__bf_verified__ = '2026-09-09 BF-certification pass (operation/math read of the pinned computation + key ops; strategy first-hand)'
__bf_note__ = 'Kintsch/van-Dijk entity/reference backbone SUPPLY primitives (name-content tokens [Ariel], gender lookup, CoNLL loading) + EntityAliaser given-name clustering = OUR-INVENTION token-overlap (flagged for Bruce-Young individuation -> the filed name_branch_shatters problem)'
__bf_corrections__ = []


import math
import os
from typing import Dict, List, Optional, Tuple

try:                                   # only the graded typer needs it; the module must import without it
    import numpy as np
except Exception:                      # pragma: no cover
    np = None

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the closed-class pronoun forms the mention typer recognises (the same list the board loader carries)
PRONOUN_FORMS = frozenset({
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves", "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves", "we", "us", "our", "ours", "ourselves",
    "this", "that", "these", "those", "who", "whom", "whose", "which"})

# THE CASE CUE'S MARKED MEMBER (pri 125, 2026-09-15). English marks the OBLIQUE member of the pronoun case
# opposition and leaves every other form case-NEUTRAL, so the informative cue is "is this form marked
# ACCUSATIVE?", not "is this form one of eight listed nominatives". `graded_role_assigner.NOMINATIVE_PRON`
# is an 8-form ALLOW-LIST, so a case-neutral subject pronoun (an indefinite `anybody`/`everyone`/`one`, a
# demonstrative `that`) was thrown out of the AGENT competition with nothing marking it a non-subject.
# MEASURED through the live reader on the five UD-EWT evaluation documents, text only: 4 of 33 gold pronoun
# agents were lost at this filter, and swapping the allow-list for the exclusion recovers them (agent
# 40/52 -> 42/52, pronoun agent 28/33 -> 31/33). Reflexives are excluded too (Binding Principle A: a
# reflexive is bound by its clause-mate co-argument, so it is not an independent agent candidate).
ACCUSATIVE_MARKED = frozenset({
    "me", "him", "her", "us", "them", "whom", "thee",
    "hers", "theirs", "mine", "ours", "yours",
    "myself", "yourself", "yourselves", "himself", "herself", "itself", "ourselves", "themselves"})

from hdlab.state_of_mind import (
    OVERLAY_BETA,
    OVERLAY_TIEBREAK_LAMBDA,
    PRONOUN_SCOPE,
    TARGET_PRONOUNS,
    SetKnownBase,
    WorkingOverlay,
    infer_nominal_gender,
)

# ---------------------------------------------------------------------------
# LEVER 4 (minor filter): a GENERAL name -> gender gazetteer (a SUPPLIED fact).
# Loaded from a committed, offline TSV built from the NLTK 'names' corpus
# (tools/build_name_gender_gazetteer.py). GENERAL first-name list; NOT derived
# from LitBank book characters (anti-circular; the reading eval is held out).
# Unambiguous names only (a name in both male+female lists is OMITTED -> the
# gazetteer ABSTAINS -> agreement filter stays open = never-confidently-wrong).
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAZETTEER_PATH = os.path.join(_REPO_ROOT, "data", "lexicons",
                              "name_gender_gazetteer.tsv")


def load_name_gender(path: Optional[str] = None) -> Dict[str, str]:
    """Load the general name->gender gazetteer TSV: {lowercased_name: 'masc'|'fem'}.

    Comment lines (leading '#') and blank lines are skipped. Missing file -> {}
    (the gazetteer lever simply no-ops; callers must treat {} as "no grounding").
    """
    p = path or GAZETTEER_PATH
    out: Dict[str, str] = {}
    if not os.path.exists(p):
        return out
    with open(p, "r", encoding="ascii") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            name, gender = parts[0].strip().lower(), parts[1].strip().lower()
            if gender in ("masc", "fem"):
                out[name] = gender
    return out


def name_gender_for_span(span_toks: List[str],
                         gaz: Dict[str, str]) -> Optional[str]:
    """Gender for a proper-name mention by scanning ALL span tokens against the
    gazetteer (the first name often is not the surface head). Returns 'masc' /
    'fem' iff the span's gendered tokens agree UNANIMOUSLY; None if no token is
    in the gazetteer OR the tokens conflict (abstain = never-confidently-wrong)."""
    if not gaz:
        return None
    found = set()
    for t in span_toks:
        g = gaz.get(t.lower().strip(".,'\"!?;:"))
        if g is not None:
            found.add(g)
    if len(found) == 1:
        return next(iter(found))
    return None


# ---------------------------------------------------------------------------
# LEVER 1 (DOMINANT): CENTERING / grammatical-role prominence constants.
# Same-gender competition (multiple salient same-gender candidates) is the real
# ceiling (backbone VET seq 29506: gender=None is only ~16% of misses; misses
# are dominated by gendered entities in same-gender competition). Centering
# Theory: the topical entity -- the one repeatedly realized in the most
# grammatically-prominent (SUBJECT) role -- is the backward-looking center and
# the preferred antecedent. Glass-box role proxy: SUBJECT ~ the first referring
# mention in its sentence (first-mention / subject-position advantage; Gernsbacher;
# Centering Cf-ranking subject>object>oblique). No parser; position is the proxy.
# ---------------------------------------------------------------------------
CENTER_SUBJECT_W = 2.0     # a subject-role mention counts double an oblique one
CENTER_PARALLEL_BONUS = 0.5  # role parallelism: subject pronoun prefers subject antecedent


# ---------------------------------------------------------------------------
# CoNLL parsing WITH sentence boundaries (blank line = sentence boundary;
# the within-sentence token index in col 2 resets to 0 after each blank line).
# ---------------------------------------------------------------------------
def parse_litbank_conll(path: str,
                        name_gender_map: Optional[Dict[str, str]] = None,
                        tagger=None,
                        ) -> Tuple[List[dict], int]:
    """Parse a LitBank/OntoNotes-style coref CoNLL file, tracking sentence index.

    Returns (mentions, n_sentences). Each mention dict:
      {cluster:int, gtok_start:int, gtok_end:int, sent_idx:int, wtok_start:int,
       head:str, is_pronoun:bool, gender:str|None, number:str|None,
       name_gender:str|None, sent_role_rank:int, is_subject:bool, midx:int}
    midx = position in the start-ordered mention list. sent_idx = 0-based sentence
    number (incremented on every blank line). wtok_start = within-sentence token
    position of the mention start (subjecthood proxy). sent_role_rank = ordinal of
    this mention among referring mentions in its sentence (0 = first = subject-ish).
    name_gender = general-gazetteer gender when name_gender_map is supplied AND the
    cue-based gender is unknown (LEVER 4); None otherwise. Passing name_gender_map=
    None reproduces the legacy fields exactly (backward-compatible).

    THE FORWARD WIRE (pri-109, wiring pri-104's landed capability). `tagger` = anything with `.tag(tokens)`
    -- the reader passes `_CachedTagShim(self)`, a standalone caller passes `hdlab.frontend.tagger()`. When
    supplied, every mention carries `span_upos`, the CATEGORY ORGAN's categories for its span in span order,
    and the ten organs that call `name_content_tokens` decide name-hood from the organ instead of from
    capitalisation. `tagger=None` -> no `span_upos` key -> byte-identical to before."""
    tokens: List[Tuple[int, str]] = []      # (gtok_idx, token_text)
    tok_sent: Dict[int, int] = {}           # gtok_idx -> sent_idx
    tok_wpos: Dict[int, int] = {}           # gtok_idx -> within-sentence position
    raw_mentions: List[Tuple[int, int, int]] = []   # (cluster, start, end)
    open_stacks: Dict[int, List[int]] = {}          # cluster -> open start gtok idxs
    gidx = 0
    sent_idx = 0
    wpos = 0
    seen_tok_in_sent = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                # blank line = sentence boundary; collapse consecutive blanks so a
                # run of blank lines does not inflate sentence distance.
                if seen_tok_in_sent:
                    sent_idx += 1
                    wpos = 0
                    seen_tok_in_sent = False
                continue
            if line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 4:
                continue
            token = cols[3]
            coref = cols[-1].strip()
            tokens.append((gidx, token))
            tok_sent[gidx] = sent_idx
            tok_wpos[gidx] = wpos
            wpos += 1
            seen_tok_in_sent = True
            if coref and coref != "_":
                for part in coref.split("|"):
                    part = part.strip()
                    if part.startswith("(") and part.endswith(")"):
                        cid = int(part[1:-1])
                        raw_mentions.append((cid, gidx, gidx))
                    elif part.startswith("("):
                        cid = int(part[1:])
                        open_stacks.setdefault(cid, []).append(gidx)
                    elif part.endswith(")"):
                        cid = int(part[:-1])
                        if open_stacks.get(cid):
                            start = open_stacks[cid].pop()
                            raw_mentions.append((cid, start, gidx))
            gidx += 1

    # n_sentences = number of sentences that actually contain tokens (trailing /
    # repeated blank lines do not create empty sentences).
    n_sentences = (max(tok_sent.values()) + 1) if tok_sent else 0
    tok_text = {gi: tx for gi, tx in tokens}
    # THE FORWARD WIRE: the category organ's tags for every token, sentence by sentence, in reading order.
    tok_upos: Dict[int, str] = {}
    if tagger is not None:
        _by_sent: Dict[int, List[Tuple[int, str]]] = {}
        for gi, tx in tokens:
            _by_sent.setdefault(tok_sent.get(gi, 0), []).append((gi, tx))
        for _si in sorted(_by_sent):
            _row = sorted(_by_sent[_si], key=lambda p: p[0])
            for (_gi, _tx), _c in zip(_row, tagger.tag([p[1] for p in _row])):
                tok_upos[_gi] = _c
    out: List[dict] = []
    for cid, start, end in raw_mentions:
        span_toks = [tok_text[i] for i in range(start, end + 1) if i in tok_text]
        if not span_toks:
            continue
        head = span_toks[-1].lower()
        is_pron = head in PRONOUN_SCOPE
        if is_pron:
            gender = PRONOUN_SCOPE[head]["gender"]
            number = PRONOUN_SCOPE[head]["number"]
        else:
            gender = infer_nominal_gender(span_toks)   # None if no cue (unknown)
            number = None
        # LEVER 4: general-gazetteer gender ONLY when the cue-based gender is
        # unknown (proper names absent from the title/gendered-noun cue lists).
        ng = None
        if (not is_pron) and gender is None and name_gender_map:
            ng = name_gender_for_span(span_toks, name_gender_map)
        out.append({
            "cluster": cid, "gtok_start": start, "gtok_end": end,
            "sent_idx": tok_sent.get(start, 0),
            "wtok_start": tok_wpos.get(start, 0),
            "head": head, "is_pronoun": is_pron,
            "gender": gender, "number": number, "name_gender": ng,
            "span_toks": list(span_toks),   # RAW-CASED span tokens (entity-merge input)
        })
        if tok_upos:
            out[-1]["span_upos"] = [tok_upos.get(i, "X") for i in range(start, end + 1) if i in tok_text]
    out.sort(key=lambda m: (m["gtok_start"], m["gtok_end"]))
    for i, m in enumerate(out):
        m["midx"] = i
    # grammatical-role rank within each sentence (subjecthood proxy): order the
    # sentence's referring mentions by within-sentence position; rank 0 = the
    # first mention = subject-ish (Centering Cf-ranking / first-mention advantage).
    by_sent: Dict[int, List[dict]] = {}
    for m in out:
        by_sent.setdefault(m["sent_idx"], []).append(m)
    for sent_mentions in by_sent.values():
        for rank, m in enumerate(sorted(sent_mentions,
                                        key=lambda mm: (mm["wtok_start"], mm["midx"]))):
            m["sent_role_rank"] = rank
            m["is_subject"] = (rank == 0)
    return out, n_sentences


# ---------------------------------------------------------------------------
# Target extraction: gendered-singular pronouns with >=1 prior same-cluster
# mention. Attach the gold nearest antecedent + its SENTENCE distance.
# ---------------------------------------------------------------------------
def build_pronoun_targets(mentions: List[dict],
                          target_pronouns=TARGET_PRONOUNS) -> List[dict]:
    """Targets = gendered-singular pronoun mentions (he/she family) with a prior
    same-gold-cluster mention. Each target dict:
      {target:mention, antecedent:mention, midx_dist:int, sent_dist:int}
    sent_dist = target.sent_idx - antecedent.sent_idx (>=0; 0 = same sentence).
    """
    by_cluster_prior: Dict[int, List[dict]] = {}
    targets: List[dict] = []
    for m in mentions:
        cid = m["cluster"]
        if m["is_pronoun"] and m["head"] in target_pronouns:
            priors = by_cluster_prior.get(cid, [])
            if priors:
                nearest = priors[-1]     # largest midx < this (append-ordered)
                targets.append({
                    "target": m,
                    "antecedent": nearest,
                    "midx_dist": m["midx"] - nearest["midx"],
                    "sent_dist": m["sent_idx"] - nearest["sent_idx"],
                })
        by_cluster_prior.setdefault(cid, []).append(m)
    return targets


# ---------------------------------------------------------------------------------------------------
# THE DISCOVERED ANAPHORA QUESTION (pri 125, 2026-09-15).  `build_pronoun_targets` above schedules a
# pronoun only when a PRIOR mention carries the SAME GOLD CLUSTER ID, so on annotation-free text the
# target list is empty and a missed reference leaves no record at all.  The brain schedules the retrieval
# from the TEXT: a third-person pronoun is a retrieval probe with cues [person/gender/number], it competes
# over the ACCESSIBLE prior referents (Centering Cf; Lewis & Vasishth 2005), and when nothing accessible
# agrees the referent STAYS OPEN -- an explicit abstention with its token position, not a missing question.
# Gold cluster ids are not read here; they belong to the scorer.
# ---------------------------------------------------------------------------------------------------
def phi_compatible(target: dict, cand: dict) -> bool:
    """The agreement cue between a pronoun probe and a candidate referent. UNKNOWN on either side does NOT
    block: the brain retrieves on the cues it HAS, and refusing every gender-unknown common noun would
    delete most legitimate antecedents (measured: it is the common-noun antecedents that carry no cue)."""
    tg, tn = target.get("gender"), target.get("number")
    cg = cand.get("gender") or cand.get("name_gender")
    cn = cand.get("number")
    if tg and cg and tg != "any" and cg != "any" and tg != cg:
        return False
    if tn and cn and tn != cn:
        return False
    return True


def is_anaphora_target(head: Optional[str]) -> bool:
    """Is this form a third-person anaphor carrying at least one agreement cue to retrieve with?"""
    from hdlab.referent_per_np import pronoun_phi
    d = pronoun_phi(head)
    if d is None or d.get("person") != "third":
        return False
    return bool(d.get("gender")) or bool(d.get("number"))


def discovered_pronoun_targets(mentions: List[dict], window: int = 0, reader=None):
    """THE QUESTION SET: ONE scheduled question for EVERY third-person pronoun in the DISCOVERED mention
    stream -- the retrieval demand a pronoun opens exists whether or not a compatible referent is accessible,
    and whether it is met is the RETRIEVAL's outcome, not the scheduler's (pri 131).  Returns a LIST in the
    `build_pronoun_targets` schema:
      {target, antecedent, midx_dist, sent_dist, schedule_reason}
    `antecedent` = the nearest prior accessible phi-compatible referent -- a schema slot and the FLOOR's own
    pick, NOT the resolver's answer (that is decided downstream by cue-based retrieval over the whole
    accessible pool).  When there is none, `antecedent` is None and `schedule_reason` = 'no_compatible_prior':
    the question is still ASKED, and the referent stays open unless the pick finds a file for it.
    ONE LIST, ONE OUTCOME PER QUESTION: the reader emits exactly one `CorefResolution` per entry here, so
    discovered == attempted + abstained and a consumer can align the two by index (the pri 122 board row
    does exactly that).  `window` = the accessibility window in sentences (0 = the whole passage read so
    far); `reader` supplies it when a caller has the reader rather than the number.
    Gold cluster ids are not read here; they belong to the scorer."""
    if reader is not None and not window:
        window = int(getattr(reader, "pronoun_window", 0) or 0)
    sched: List[dict] = []
    prior: List[dict] = []
    for m in mentions:
        if m.get("is_pronoun") and is_anaphora_target(m.get("head")):
            cands = [p for p in prior
                     if (not p.get("is_pronoun"))
                     and (not window or (m["sent_idx"] - p["sent_idx"]) <= window)
                     and phi_compatible(m, p)]
            if cands:
                nearest = cands[-1]
                sched.append({"target": m, "antecedent": nearest,
                              "midx_dist": m["midx"] - nearest["midx"],
                              "sent_dist": m["sent_idx"] - nearest["sent_idx"],
                              "schedule_reason": None})
            else:
                sched.append({"target": m, "antecedent": None, "midx_dist": 0, "sent_dist": 0,
                              "schedule_reason": "no_compatible_prior"})
        prior.append(m)
    return sched


def retrievable_referents(mentions: List[dict]) -> List[dict]:
    """The pronoun-RETRIEVABLE subset of a mention stream -- the tracked forward-looking centers a pronoun
    probe can actually address: pronouns, referents with a gender cue, NAME-typed referents, and referents
    the animacy lexicon calls animate.  WHY THIS FILTER EXISTS: on 2026-09-03 feeding the full
    referent-per-NP stream to the anaphora pool collapsed coref 0.4693 -> 0.1019 (514/539 wrong targets
    bound a NON-coreferent entity) because feature-blank singleton referents flooded the pool.  The brain's
    filter is the retrieval cue itself -- an inanimate 'table' is not retrievable by 'he' (Garnham 2001) --
    so it belongs HERE, in the retrieval organ, and not in the introduction organ (which must keep every
    referent for thematic role binding: letters and doors are patients)."""
    out: List[dict] = []
    for m in mentions:
        if m.get("is_pronoun") or m.get("gender") or m.get("name_gender"):
            out.append(m)
            continue
        if (m.get("span_upos") or [""])[-1] == "PROPN":
            out.append(m)
            continue
        try:
            from hdlab.animacy_lexicon import lookup_animacy
            rec = lookup_animacy(m["head"].lower(), "NOUN")
        except Exception:
            rec = None
        if rec and rec.get("animacy") == "animate":
            out.append(m)
    return out


# ---------------------------------------------------------------------------------------------------
# THE ANAPHORA PICK (pri 125 phase 7, 2026-09-15).  The shipped pick
# (`event_centrality_coref.resolve_stream`) has two properties that cost the discovered stream almost
# everything, both read off the code:
#   * line 355 enters the retrieval branch ONLY for `m["head"] in TARGET_PRONOUNS` = six forms
#     {he, him, his, she, her, hers}, so every `it`/`they`/`them`/`their`/`this`/`that` question is
#     scheduled and never attempted -- MEASURED 98 of 334 GUM questions answered;
#   * line 358 reads the probe's features from the SURFACE-FORM table PRONOUN_SCOPE rather than from the
#     mention, and the candidate pool is the whole document (no accessibility bound at retrieval).
# THE BRAIN'S FORM (PINNED): retrieval activation is ACT-R base level over the referent's reference history
# weighted by Centering Cf role prominence, PLUS the retrieval CUE VECTOR as a GRADED match term (Lewis &
# Vasishth 2005: cues are summed, not applied as filters), PLUS the forward-looking centre; Principle A
# binds a reflexive to its clause-mate co-argument; every retrieval is itself a presentation (impletion,
# Kahneman-Treisman-Gibbs), so a resolved pronoun is written into its referent's history.
#     A(cand) = ln SUM_k w(role_k) * (t_now - t_k)^(-d) + w_g*gender_match + w_n*number_match + w_f*Cb
# MEASURED (28 MODERN GUM test documents, 795 fixed questions from the gold, text-only input, ABSTENTION =
# WRONG, floor recomputed on the same population, documents the bootstrap unit):
#     shipped reader                    0.0000   (0 questions answered -- it has no pronoun mentions)
#     this pick                         0.3031   (783 of 795 answered)
#     nearest-prior-compatible FLOOR    0.1849   -> +0.1182 CI[+0.0430,+0.1987] half=0.0779 CI-SEPARATED
#     info-free twin (phi permuted)     0.1811   -> -0.0038 CI[-0.0454,+0.0324] AT FLOOR
# NUMBER enters at its own weight and NOT for the `they` family: modern English `they` is number-ambiguous
# (singular they; the collective read of an organisation), and applying a -1 number mismatch at the gender
# weight scored 0.1493 against 0.1791 with the cue off.  A rank-based Principle-B proxy was built and
# REFUTED (-0.104): "any other core-ranked mention in the sentence" is not the clause-mate CO-ARGUMENT
# relation, so the real clause-mate map is a filed follow-on and the proxy is NOT shipped.
# Gold is never read here; the caller scores the returned `resolved_head` / `target_wpos`.
# ---------------------------------------------------------------------------------------------------
NUMBER_AMBIGUOUS = frozenset({"they", "them", "their", "theirs", "themselves"})


def mention_span(m) -> tuple:
    """(sent_idx, wtok_start, wtok_end) -- the ANTECEDENT SPAN, so a consumer or a scorer can align the pick
    by POSITION instead of by a head string.  The discovered referents are single-token (their content head);
    a coref-column mention carries its own gtok extent."""
    ws = int(m.get("wtok_start", -1))
    gs, ge = m.get("gtok_start", -1), m.get("gtok_end", -1)
    span = 0
    if isinstance(gs, int) and isinstance(ge, int) and gs >= 0 and ge >= gs:
        span = ge - gs
    elif m.get("span_toks"):
        span = max(0, len(m["span_toks"]) - 1)
    return (int(m.get("sent_idx", -1)), ws, ws + span)


def entity_key(m):
    """THE IDENTITY BASIS OF THE RETRIEVAL (pri 131): the reader's OWN online entity-file id -- `m['cluster']`,
    written by `entity_resolver.cluster` as -(file+1) for every non-pronoun mention -- and NEVER the head
    string.  A pronoun is resolved to a DISCOURSE ENTITY, a file card / object file (Kahneman & Treisman 1992
    object files; Heim 1982 file-change semantics), so two `doctor` mentions the reader kept apart are TWO
    candidates with two histories and two cards, and a name plus the alias the reader merged into it are ONE.
    Falls back to the head string only for a mention with no cluster at all (none on the live path)."""
    c = m.get("cluster")
    return c if c is not None else ("head:" + str(m.get("head", "")).lower())


def graded_pronoun_resolve(mentions: List[dict], targets: List[dict], window: int = 0,
                           w_gender: float = 4.0, w_number: float = 0.0, w_focus: float = 1.0,
                           decay: float = 2.0, coarg=None, single_sentence: bool = False):
    """ACT-R cue-based antecedent retrieval over the reader's OWN DISCOURSE ENTITIES, in reading order, one
    pass.  Returns (records, abstentions) with EXACTLY ONE record per scheduled target:
      {pronoun, sent_idx, target_wpos, resolved_entity, resolved_head, antecedent_span, candidates,
       abstain_reason, n_cands, sent_dist}
    `resolved_entity` is the entity id (or None when the referent stays open -- NEVER a valid id used as a
    sentinel); `antecedent_span` is (sent_idx, wtok_start, wtok_end) of the mention that supplied the
    evidence; `candidates` is the scored candidate set (entity id -> activation, strongest first);
    `abstain_reason` is None | 'no_candidate' | 'no_compatible' | 'tie'.
    `coarg` = {(sent_idx, wtok): (positions of this token's clause-mate CO-ARGUMENTS)} from the reader's own
    parse -- Principle B for a plain pronoun, Principle A for a reflexive (Chomsky 1981; Reinhart 1983).
    `single_sentence` = the independent SINGLE-SENTENCE comparator: the file store is cleared at every
    sentence boundary, so the arm is structurally blind cross-sentence and can DISAGREE with the discourse
    resolver on a designed cross-sentence case.
    `window` = the accessibility bound in sentences (0 = the whole passage read so far; SWEPT 0/1/2/3/5)."""
    from hdlab.salience_binder import actr_activation, ROLE_PROMINENCE
    from hdlab.affected_entity_resolver import is_reflexive
    tgt = {t["target"]["midx"] for t in targets}
    hist: Dict[object, list] = {}      # entity id -> the FILE's reference history [(order, role), ...]
    last_sent: Dict[object, int] = {}
    last_nom: Dict[object, dict] = {}  # entity id -> its most recent NON-pronoun mention (the antecedent)
    feats: Dict[object, tuple] = {}    # entity id -> (gender, number) ACCRUED over the file's mentions
    rank_in_sent: Dict[int, Dict[object, int]] = {}
    ent_at_pos: Dict[tuple, object] = {}
    prev_cb = [None]
    cur = [None]
    recs, abstain = [], []
    for m in mentions:
        order = float(m["midx"])
        si = int(m["sent_idx"])
        if cur[0] is not None and si != cur[0]:
            row = sorted(rank_in_sent.get(cur[0], {}).items(), key=lambda kv: kv[1])
            if row:
                prev_cb[0] = row[0][0]
            if single_sentence:
                hist.clear(); last_sent.clear(); last_nom.clear(); feats.clear()
        cur[0] = si
        rk = m.get("sent_role_rank", 99)
        role = "SUBJECT" if rk == 0 else ("OBJECT" if rk == 1 else "OTHER")
        if not m.get("is_pronoun"):
            k = entity_key(m)
            ent_at_pos[(si, int(m["wtok_start"]))] = k
            hist.setdefault(k, []).append((order, role))
            last_sent[k] = si
            # 2026-09-16 (strategy, pri 136 landing): the pick ANSWERS with this file's most recent mention; since the
            # files are real object files (pri 136) that member is often a modifier or a bare dependent the gold mention
            # does not cover. Keep the most recent NOUN/PROPN mention as the answer, falling back to any (measured by
            # pri 136: +0.0340 CI-sep on the competition's files, exactly 0.0000 on the old head-bucket files).
            _u = (m.get("span_upos") or [None])[-1]
            if _u in ("NOUN", "PROPN") or k not in last_nom:
                last_nom[k] = m
            g = m.get("gender") or m.get("name_gender")
            old = feats.get(k, (None, None))
            feats[k] = (g or old[0], m.get("number") or old[1])
            rank_in_sent.setdefault(si, {}).setdefault(k, rk)
            continue
        if m["midx"] not in tgt:
            continue
        pg, pn = m.get("gender"), m.get("number")
        cands = [k for k, s in last_sent.items() if (not window) or (si - s) <= window]
        reason = None
        legal = cands
        if not cands:
            reason = "no_candidate"
        else:
            banned = set()
            if coarg:
                banned = {ent_at_pos[p] for p in (coarg.get((si, int(m["wtok_start"]))) or ())
                          if p in ent_at_pos}
            if is_reflexive(m.get("head")):
                # PRINCIPLE A: a reflexive is bound BY a clause-mate co-argument (the real relation from the
                # parse when we have it; the within-sentence core-rank set is the fallback).
                inside = [k for k in cands if k in banned] if banned else \
                    [k for k in cands
                     if k in {kk for kk, r in rank_in_sent.get(si, {}).items() if r in (0, 1) and r != rk}]
                legal = inside or cands
            elif banned:
                # PRINCIPLE B: a PLAIN pronoun may not take its clause-mate CO-ARGUMENT as its antecedent.
                legal = [k for k in cands if k not in banned]
                if not legal:
                    reason = "no_compatible"
        best, bs, ties = None, -1e18, 0
        scored = []
        amb = m["head"].lower() in NUMBER_AMBIGUOUS
        for k in legal:
            a = actr_activation(hist.get(k, ()), order, decay=decay, role_prominence=ROLE_PROMINENCE)
            if a == float("-inf"):
                a = -1e9
            cg, cn = feats.get(k, (None, None))
            gm = 0.0
            if pg and cg and pg != "any" and cg != "any":
                gm = 1.0 if pg == cg else -1.0
            nm = 0.0
            if pn and cn and not amb:
                nm = 1.0 if pn == cn else -1.0
            s = a + w_gender * gm + w_number * nm + w_focus * (1.0 if k == prev_cb[0] else 0.0)
            scored.append((k, s))
            if s > bs:
                bs, best, ties = s, k, 1
            elif s == bs:
                ties += 1
        if best is not None and ties > 1:
            best, reason = None, "tie"         # a TIE is an open referent, not a coin flip
        if best is None:
            rec = {"pronoun": m["head"], "sent_idx": si, "target_wpos": m["wtok_start"],
                   "resolved_entity": None, "resolved_head": "", "antecedent_span": None,
                   "candidates": tuple(sorted(scored, key=lambda kv: -kv[1])[:5]),
                   "abstain_reason": reason or "no_compatible", "n_cands": len(legal), "sent_dist": 0}
            recs.append(rec)
            abstain.append({"head": m["head"], "sent_idx": si, "wtok_start": m["wtok_start"],
                            "reason": rec["abstain_reason"]})
            continue
        d = max(0, si - last_sent.get(best, si))
        am = last_nom.get(best)
        hist.setdefault(best, []).append((order, role))    # IMPLETION
        last_sent[best] = si
        recs.append({"pronoun": m["head"], "sent_idx": si, "target_wpos": m["wtok_start"],
                     "resolved_entity": best,
                     "resolved_head": (am or {}).get("head", ""),
                     "antecedent_span": mention_span(am) if am is not None else None,
                     "candidates": tuple(sorted(scored, key=lambda kv: -kv[1])[:5]),
                     "abstain_reason": None, "n_cands": len(legal), "sent_dist": d})
    return recs, abstain


def sent_dist_bucket(sent_dist: int) -> str:
    """Bucket a target by antecedent sentence distance."""
    if sent_dist <= 0:
        return "same"
    if sent_dist == 1:
        return "plus1"
    if sent_dist == 2:
        return "plus2"
    return "long"


BUCKETS = ("same", "plus1", "plus2", "long")


# ---------------------------------------------------------------------------
# STEP-1c ENTITY ALIASING / MERGING (the situation-model ENTITY-UNIFICATION layer).
#
# WHY: WorkingOverlay groups entities by lowercased surface HEAD, so a single
# character fragments across >1 overlay entity ("Elizabeth" / "Miss Bennet" /
# "Bennet" = 3). Salience/centering/chaining then cannot accumulate on the true
# referent (each fragment is out-sali*enced by a locally-recent minor character).
# Readers ALIAS names: they recognize surface variants as ONE person. This layer
# clusters proper-name mention variants into ONE canonical overlay entity BEFORE
# pronoun resolution, via GENERAL rules (NOT tuned to any LitBank character):
#   - honorific / title stripping (Miss/Mr/Mrs/Dr/Aunt + Name -> the Name tokens)
#   - shared content token (Elizabeth Bennet ~ Elizabeth ~ Bennet)
#   - first-name <-> surname unification through the shared token
# OVER-MERGE GUARDRAILS (merging two DISTINCT people is worse than fragmenting one):
#   - merge ONLY when the shared-token match is UNAMBIGUOUS (a UNIQUE gender-
#     compatible existing entity). Ambiguous cross-token matches ABSTAIN (never-
#     confidently-wrong) and fall back to EXACT-surface grouping (which is always
#     safe -- identical name string), never a forced cross-merge.
#   - NEVER merge across a KNOWN gender conflict (Mr Bennet vs Mrs Bennet stay split).
# Incremental (forward-only; a mention aliases only against entities seen so far).
# GLASS-BOX: pure symbolic; no gold; no torch; ASCII-only.
# ---------------------------------------------------------------------------

# General honorifics / titles stripped before name matching (English + a few
# common French/German forms found in 19c prose). NOT LitBank-character-specific.
TITLE_TOKENS = frozenset({
    "mr", "mister", "mrs", "missus", "miss", "ms", "dr", "doctor", "sir",
    "lady", "lord", "master", "mistress", "madam", "madame", "mme", "mlle",
    "mademoiselle", "monsieur", "sr", "jr", "saint", "st", "capt", "captain",
    "col", "colonel", "gen", "general", "maj", "major", "sgt", "sergeant",
    "lt", "lieutenant", "rev", "reverend", "prof", "professor", "hon",
    "aunt", "uncle", "cousin", "father", "mother", "brother", "sister",
    "grandfather", "grandmother", "herr", "frau", "don", "dona", "signor",
    "signora", "esq", "esquire", "the",
})

MAX_NAME_TOKENS = 4    # a proper-name span is short; longer = a descriptive phrase

# Closed-class capitalized tokens that are NOT name content (sentence-initial
# determiners / prepositions / pronouns / conjunctions). General English.
STOP_CAPS = frozenset({
    "the", "a", "an", "this", "that", "these", "those", "his", "her", "hers",
    "its", "their", "my", "your", "our", "and", "or", "but", "nor", "of",
    "in", "on", "at", "to", "for", "with", "by", "from", "as", "so", "yet",
    "he", "she", "it", "they", "we", "i", "you", "who", "whom", "which",
    "what", "when", "where", "why", "how", "there", "here", "then", "than",
    "if", "no", "not", "all", "some", "any", "one",
})


# ---------------------------------------------------------------------------------------------------------------
# THE FORWARD WIRE (2026-09-14, pri-104 solver; `experiments/exp_entity_to_category_prior_v1.py --name-decision`).
#
# `name_content_tokens` is the sole NAME-vs-COMMON gate for EIGHT live organs -- online_entity_cluster,
# entity_resolver, commonnoun_binder, crosstype_live_adapter, coref_distractor_suppress, event_centrality_coref,
# gender_organ, scene_segment -- and until now it decided by CAPITALISATION plus a 60-word stop list. The substrate
# has a category organ that answers exactly this question far better, and NO organ read it: `hdlab/coref.py`,
# `hdlab/entity_resolver.py` and `hdlab/lexical_utils.py` contained the strings "upos" and "PROPN" ZERO times.
#
# WHY THIS IS THE BRAIN'S ORDER, not a convenience. A proper name is a word that refers to an INDIVIDUAL (Kripke
# 1980); the referent route that stores it (left temporal pole -- Semenza 2006/2009 proper-name anomia; Damasio et
# al. 1996) sits ABOVE the posterior-temporal word-form/category level and is FED BY it. Deciding name-hood from
# orthography instead of from the lexical category inverts the hierarchy: it makes the higher level re-derive,
# from a surface cue, something the level below it has already computed with far more evidence.
#
# MEASURED on the full UD-EWT test (25,094 tokens), scored against the same gold PROPN:
#     TOKEN level   capitalisation rule  P 0.5640 R 0.8299 F1 0.6716   (1,331 false names)
#                   category organ       P 0.8711 R 0.8564 F1 0.8637   (  263 false names)   +0.1921 F1
#     SPAN  level   capitalisation rule  P 0.7545 R 0.7904 F1 0.7720   (  352 false name spans)
#                   category organ       P 0.8896 R 0.8883 F1 0.8890   (  145 false name spans)  +0.1170 F1
# The span level is the one that matters -- a span is what these organs type -- and 207 fewer spurious name spans
# is 207 fewer bogus entity files opened per 25k tokens.
#
# HOW TO ADOPT IT, and why nothing breaks: `name_content_tokens(span_toks)` with no `upos` is BYTE-IDENTICAL to
# today. A caller that has the sentence's categories (every caller downstream of `hdlab.frontend.tagger()` does)
# passes them as the parallel `upos` list for the span, and the decision becomes the category organ's. Set
# HDLAB_NAME_SOURCE=caps to force the old behaviour even where categories are supplied (the regression arm).
NAME_SOURCE = os.environ.get("HDLAB_NAME_SOURCE", "category")     # "category" | "caps"
_NOMINAL_HEADS = ("NOUN", "PROPN")


# A coref mention span is NOT one NP run: it carries PPs, parentheticals and relative clauses, and a
# preposition / coordinator / relative marker / comma OPENS A NEW NOMINAL DOMAIN. Taking the last NOUN/PROPN
# of the WHOLE span therefore types the span by a PROPN inside a MODIFIER -- "the environments identified by
# Quilis", "a case from English", "a System Under Test ( SUT )" all came out NAME.
# MEASURED (pri-109, 17,010 GUM test mentions): the whole-span rule and the NP-domain rule disagree on 1,415
# spans (8.3%) and change the typing of 403 (241 common->name). Through the gold-free common-noun board row
# the whole-span rule costs the whole margin -- -0.0074 against +0.0023 for the domain rule (+0.0020 with no
# wire at all), while the pronoun row is identical. The head DOMAIN is the fix, not the head direction.
_NP_BREAK = ("ADP", "CCONJ", "SCONJ", "VERB", "AUX", "PART")
_REL_MARKERS = frozenset({"who", "whom", "whose", "which", "that"})


def _np_domain(span_toks: List[str], upos: List[str]) -> int:
    """Length of the FIRST nominal domain of the span (where the head lives)."""
    seen = False
    for i, u in enumerate(upos):
        low = span_toks[i].lower() if i < len(span_toks) else ""
        if u in _NOMINAL_HEADS:
            seen = True
            continue
        if seen and (u in _NP_BREAK or u == "PUNCT" or low in _REL_MARKERS):
            return i
    return len(upos)


def _span_head_is_name(span_toks: List[str], upos: List[str]) -> bool:
    """English nominal spans are head-final WITHIN the head domain: the head is the LAST NOUN/PROPN of the
    FIRST nominal domain (the same domain boundary `hdlab/attachment_arm`'s NP_SPLIT cue uses). The span is
    a NAME iff that head is a PROPN."""
    n = min(_np_domain(span_toks, upos), len(span_toks), len(upos)) or min(len(span_toks), len(upos))
    idx = [i for i in range(n) if upos[i] in _NOMINAL_HEADS]
    if not idx:
        return any(u == "PROPN" for u in upos[:n])
    return upos[idx[-1]] == "PROPN"




# ---------------------------------------------------------------------------------------------------------
# THE GRADED MENTION TYPE (2026-09-15, pri-118 solver; `experiments/exp_graded_mention_typing_v1.py`).
#
# THE DEFECT.  `name_content_tokens` -- the NAME-vs-COMMON gate for TEN live organs -- and the board loader's
# `_mention_type_organ` both decide from the category organ's ARGMAX, and the type is three-valued.  Two
# mathematical consequences, both measured:
#   (1) THE POINT ESTIMATE IS TAKEN AT THE WRONG LEVEL.  The mention type is a COARSENING of the category
#       variable, and the Bayes decision on a coarsened variable under 0-1 loss is `argmax_t sum_{c in t} P(c)`
#       -- marginalise, THEN decide -- not `type(argmax_c P(c))`.  The two differ whenever the winning single
#       category sits in a type whose TOTAL mass is smaller than a rival's (P(PROPN)=.35 vs P(NOUN)+P(ADJ)=.65).
#   (2) THE HEAD IS AN ARGMAX READ TOO.  "the last NOUN/PROPN of the first nominal domain" is computed on the
#       argmax tag sequence; graded, each position is scored by its NOMINAL MASS with a head-finality decay
#       (TYPE_ETA; eta -> inf reproduces the shipped rule exactly when the posterior is peaked).
#
# AND THE EVIDENCE ONLY THE CONSUMER CAN SEE.  The category organ reads each token's own shape relative to the
# sentence convention (`word_shape` x `position_class`).  It cannot see that "Game of Thrones", "The Rains of
# Castamere", "the Slavonic Dances" are ONE capitalised unit spanning a preposition -- a multi-word name stored
# as a lexical unit by the referent route (Kripke 1980 rigid designation; Semenza 2006/2009 proper-name anomia,
# left temporal pole, ABOVE and FED BY the category level).  `SpanCueTable` holds P(span-shape | type) as
# COUNTS, learned ONLINE from the reader's own confident typings (Fine, Jaeger, Farmer & Qian 2013 rapid
# expectation adaptation -- the same account the passage register cites one level down).  No gold, no fitted
# parameter, an observe path, and a table that can be printed.
#
# MEASURED, GUM TEST (128 documents / 17,010 mentions), operating point chosen on the TRAIN half, doc-paired
# bootstrap 2,000, the gold mention type as the ANSWER KEY:
#     type accuracy   0.9506 -> 0.9608   +0.0103 CI[+0.0067,+0.0139]   CI-SEPARATED
#     macro F1        0.9352 -> 0.9496   +0.0143 CI[+0.0097,+0.0194]   CI-SEPARATED
#     name F1         0.8907 -> 0.9171   +0.0264 CI[+0.0178,+0.0362]   (recall .8420 -> .8855, precision UP)
#     common F1       0.9262 -> 0.9420   +0.0158 CI[+0.0105,+0.0211]   pronoun F1 +0.0009 (n.s., not down)
#     info-free twin (the posterior rows permuted across the document's tokens, entropy multiset preserved):
#                     0.7177 / macro 0.5837 -- the arm beats it +0.2351 / +0.3532, CI-separated
#     the span cue's OWN twin (same table, same kappa, a RANDOM symbol per mention): +0.0021 type accuracy
#                     over the floor, NOT separated -- so the gain is the cue's CONTENT, not its free parameters
# BACKWARD COMPATIBILITY: every entry point below is inert unless a caller supplies `tag_post`.  With no
# posterior, `name_content_tokens` is BYTE-IDENTICAL to the pre-2026-09-15 function.
MENTION_TYPES = ("pronoun", "name", "common")
# the categories that can head a REFERRING EXPRESSION.  A mention span has already been segmented as one, so
# the categories that cannot head it are ruled out by the consumer's own evidence and the posterior is
# renormalised on this support (structural knowledge of the consumer, not a fitted number).
TYPE_SUPPORT = frozenset({"PRON", "PROPN", "NOUN", "ADJ", "VERB", "NUM", "ADV", "X", "SYM", "INTJ"})
TYPE_ETA = float(os.environ.get("HDLAB_TYPE_ETA", "0.5"))            # head-finality decay; inf == the shipped rule
TYPE_KAPPA_CARD = float(os.environ.get("HDLAB_TYPE_KAPPA_CARD", "0.5"))    # Heim file-card evidence at the TYPE level
TYPE_KAPPA_CAPS = float(os.environ.get("HDLAB_TYPE_KAPPA_CAPS", "1.0"))    # the span-level name-run cue
TYPE_TAU_LEARN = float(os.environ.get("HDLAB_TYPE_TAU_LEARN", "0.95"))     # a typing this confident teaches the table
SPAN_CUE_ASSET = os.environ.get("HDLAB_SPAN_CUE_ASSET") or os.path.join(
    _REPO_ROOT, "data", "hook_state", "mention_span_cue_counts.json")
_NP_BREAK_G = ("ADP", "CCONJ", "SCONJ", "VERB", "AUX", "PART")
# function words that may sit INSIDE a multi-word name without disqualifying it ("Game OF Thrones")
NAME_INTERNAL_FUNCTION = frozenset({"of", "the", "a", "an", "and", "for", "de", "van", "von", "der", "la",
                                    "le", "el", "at", "in", "on", "to", "by", "with"})


class SpanCueTable:
    """COUNTS of P(span shape | mention type), learned online from the reader's own confident typings.
    Plastic, never frozen: `observe` is the update, `logp` is a pure function of the counts, `save`/`load`
    persist them so a run compounds instead of starting blind."""

    __slots__ = ("n", "lam", "syms", "n_obs")

    def __init__(self, lam: float = 0.5):
        self.n = {t: {} for t in MENTION_TYPES}
        self.lam = lam
        self.syms = set()
        self.n_obs = 0

    def observe(self, sym, ty, w: float = 1.0) -> None:
        if ty not in self.n:
            return
        self.n[ty][sym] = self.n[ty].get(sym, 0.0) + w
        self.syms.add(sym)
        self.n_obs += 1

    def logp(self, sym, ty) -> float:
        row = self.n.get(ty) or {}
        tot = sum(row.values()) + self.lam * max(1, len(self.syms))
        return math.log((row.get(sym, 0.0) + self.lam) / tot)

    def save(self, path=None) -> None:
        import json
        p = path or SPAN_CUE_ASSET
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"n": self.n, "n_obs": self.n_obs, "lam": self.lam}, f, indent=1)
        os.replace(tmp, p)

    @classmethod
    def load(cls, path=None):
        import json
        p = path or SPAN_CUE_ASSET
        t = cls()
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            return t                      # no asset -> an EMPTY table, and the cue is silent (graceful)
        t.lam = float(d.get("lam", 0.5))
        t.n_obs = int(d.get("n_obs", 0))
        for ty, row in (d.get("n") or {}).items():
            if ty in t.n:
                t.n[ty] = {k: float(v) for k, v in row.items()}
                t.syms.update(t.n[ty])
        return t


_SPAN_CUE = None


def span_cue_table():
    """The process-wide span-cue table (loaded once from the asset; empty and silent when there is none)."""
    global _SPAN_CUE
    if _SPAN_CUE is None:
        _SPAN_CUE = SpanCueTable.load()
    return _SPAN_CUE


def span_caps_symbol(span_toks, head_i, first_is_sentence_initial=False):
    """The span-level name-run symbol, EXCLUDING the head, so nothing the category organ already read is
    counted twice: how many OTHER mid-span capitals the span carries, and whether it carries a lowercase
    content word (the descriptive-phrase disqualifier this module's capitalisation rule already uses)."""
    ncap = 0
    lower_content = 0
    for i, t in enumerate(span_toks):
        if i == head_i:
            continue
        core = str(t).strip(".,'\"!?;:-()[]")
        if not core.isalpha():
            continue
        mid = not (i == 0 and first_is_sentence_initial)
        if core[:1].isupper() and mid:
            ncap += 1
        elif not core[:1].isupper() and core.lower() not in NAME_INTERNAL_FUNCTION and len(core) > 2:
            lower_content += 1
    return "o%d_l%d" % (min(ncap, 3), 1 if lower_content else 0)


def _graded_head(span_toks, upos, tag_post, tags, eta=None):
    """The head of the span, chosen on NOMINAL MASS with a head-finality decay inside the first nominal
    domain.  Returns the index into the span.  eta -> inf reproduces `_np_domain` + "the last NOUN/PROPN"."""
    eta = TYPE_ETA if eta is None else eta
    ip = [tags.index(t) if t in tags else -1 for t in ("NOUN", "PROPN")]
    ib = [tags.index(t) for t in (_NP_BREAK_G + ("PUNCT",)) if t in tags]
    n = min(len(span_toks), len(tag_post))
    nm, bm = [], []
    for i in range(n):
        r = tag_post[i]
        nm.append(float(sum(r[j] for j in ip if j >= 0)))
        bm.append(float(sum(r[j] for j in ib)))
    cut, seen = n, False
    for i in range(n):
        if nm[i] >= 0.5:
            seen = True
            continue
        rel = str(span_toks[i]).lower() in _REL_MARKERS
        if seen and ((bm[i] - nm[i]) > 0.0 or rel):
            cut = i
            break
    dom = list(range(cut)) or list(range(n))
    last = dom[-1]
    best, best_s = None, None
    for i in dom:
        if nm[i] <= 0.0:
            continue
        pen = 0.0 if (eta == 0.0 or last == i) else eta * (last - i)
        s = math.log(max(nm[i], 1e-12)) - pen
        if best_s is None or s > best_s:
            best, best_s = i, s
    if best is not None:
        return best
    for i in range(n - 1, -1, -1):
        if upos and i < len(upos) and upos[i] != "PUNCT":
            return i
    return max(0, n - 1)


def _type_mix(q, tags, table, key, cover, back=None):
    """log P(cue | type) from a per-CATEGORY count table, mixed inside each type by the posterior's own
    weights -- one additive log term per type, the same shape as every cue in the category organ."""
    lg = {}
    for ty in MENTION_TYPES:
        idx = [i for i in cover[ty] if tags[i] in table]
        w = sum(float(q[i]) for i in idx)
        if w <= 0 or not idx:
            lg[ty] = 0.0
            continue
        acc = 0.0
        for i in idx:
            row = table.get(tags[i]) or {}
            v = row.get(key, back.get(tags[i]) if back else None)
            if v is None:
                continue
            acc += (float(q[i]) / w) * math.exp(v)
        lg[ty] = math.log(max(acc, 1e-12))
    return lg


def mention_type_graded(span_toks, upos=None, tag_post=None, tags=None, span_tab=None, card_sym=None,
                        log_entc=None, ent_back=None, first_is_sentence_initial=False, observe=False):
    """{'pronoun': P, 'name': P, 'common': P} for one mention span, plus the head index it was read at.

    `tag_post` = the category organ's POSTERIOR rows for the span (one row per token, over `tags`).  Without
    it this returns the shipped three-valued decision as a degenerate distribution, so every caller is
    backward-compatible by construction.  `span_tab` supplies the online span-shape counts; `card_sym` +
    `log_entc` supply the Heim file-card evidence at the TYPE level (the category organ reads it ONLY where a
    word has no lexical entry -- MacDonald 1994 cue competition -- which is right for the CATEGORY question
    and wrong for the TYPE question, which is the referent system's own).  `observe=True` lets a confident
    typing teach the span table (the plastic path)."""
    toks = list(span_toks)
    up = list(upos) if upos else None
    if tag_post is None or tags is None or not len(tag_post):
        hi = None
        if up:
            n = min(_np_domain(toks, up), len(toks), len(up)) or min(len(toks), len(up))
            idx = [i for i in range(n) if up[i] in _NOMINAL_HEADS]
            hi = idx[-1] if idx else (n - 1 if n else 0)
            low = toks[hi].lower() if hi < len(toks) else ""
            if up[hi] == "PRON" or (low in PRONOUN_FORMS and up[hi] != "PROPN"):
                t = "pronoun"
            else:
                t = "name" if up[hi] == "PROPN" else "common"
        else:
            t = "name" if _caps_name_tokens(toks) else "common"
            hi = len(toks) - 1
        return {x: (1.0 if x == t else 0.0) for x in MENTION_TYPES}, hi
    ti = {t: i for i, t in enumerate(tags)}
    hi = _graded_head(toks, up, tag_post, tags)
    hi = min(hi, len(tag_post) - 1)
    sup = np.array([1.0 if t in TYPE_SUPPORT else 0.0 for t in tags], dtype=float)         if np is not None else None
    q = [float(x) for x in tag_post[hi]]
    if sup is not None:
        q = [a * b for a, b in zip(q, sup)]
    s = sum(q)
    if s <= 0:
        q = [float(x) for x in tag_post[hi]]
        s = sum(q) or 1.0
    q = [x / s for x in q]
    i_pron, i_propn = ti.get("PRON", -1), ti.get("PROPN", -1)
    mass = {"pronoun": q[i_pron] if i_pron >= 0 else 0.0,
            "name": q[i_propn] if i_propn >= 0 else 0.0}
    mass["common"] = max(0.0, 1.0 - mass["pronoun"] - mass["name"])
    low = toks[hi].lower() if hi < len(toks) else ""
    # the closed-class lexical fact: a listed pronoun form cannot be typed a NAME on sub-majority PROPN mass
    if low in PRONOUN_FORMS and mass["name"] < mass["pronoun"] + mass["common"]:
        mass["pronoun"] += mass["common"]
        mass["common"] = 0.0
    cover = {"pronoun": [i_pron] if i_pron >= 0 else [],
             "name": [i_propn] if i_propn >= 0 else [],
             "common": [i for t, i in ti.items() if t not in ("PRON", "PROPN")]}
    z = {ty: math.log(max(mass[ty], 1e-12)) for ty in MENTION_TYPES}
    used = False
    if TYPE_KAPPA_CARD and log_entc and card_sym and not str(card_sym).startswith("e_first"):
        lg = _type_mix(q, tags, log_entc, card_sym, cover, ent_back)
        for ty in MENTION_TYPES:
            z[ty] += TYPE_KAPPA_CARD * lg[ty]
        used = True
    cue = span_caps_symbol(toks, hi, first_is_sentence_initial)
    tab = span_tab if span_tab is not None else span_cue_table()
    if TYPE_KAPPA_CAPS and tab is not None and tab.n_obs > 0:
        for ty in MENTION_TYPES:
            z[ty] += TYPE_KAPPA_CAPS * tab.logp(cue, ty)
        used = True
    if used:
        mx = max(z.values())
        e = {ty: math.exp(z[ty] - mx) for ty in MENTION_TYPES}
        tot = sum(e.values()) or 1.0
        mass = {ty: e[ty] / tot for ty in MENTION_TYPES}
    tot = sum(mass.values()) or 1.0
    dist = {ty: mass[ty] / tot for ty in MENTION_TYPES}
    if observe and tab is not None:
        top = max(MENTION_TYPES, key=lambda t: dist[t])
        if dist[top] >= TYPE_TAU_LEARN:
            tab.observe(cue, top)
    return dist, hi


def mention_type(span_toks, upos=None, tag_post=None, tags=None, **kw):
    """The ARGMAX of the graded type -- for the consumers that must branch on a label."""
    dist, _hi = mention_type_graded(span_toks, upos=upos, tag_post=tag_post, tags=tags, **kw)
    return max(MENTION_TYPES, key=lambda t: dist[t])



def _caps_name_tokens(span_toks) -> bool:
    """The pre-2026-09-14 capitalisation test, kept as the last-resort fallback (no categories, no posterior)."""
    for t in span_toks:
        core = str(t).strip(".,'\"!?;:-()[]")
        if core and core.isalpha() and core[:1].isupper() and core.lower() not in STOP_CAPS:
            return True
    return False


def name_content_tokens(span_toks: List[str], upos: Optional[List[str]] = None,
                        tag_post=None, tags=None, span_tab=None, card_sym=None, log_entc=None,
                        ent_back=None, first_is_sentence_initial: bool = False,
                        observe: bool = False) -> List[str]:
    """GENERAL clean-name extraction: the lowercased, title-stripped name tokens of a
    mention span, IFF the span is a CLEAN proper name. Empty -> the mention is NOT a
    proper name (a pronoun, a common nominal, or a DESCRIPTIVE phrase) -> no aliasing.

    A span is a clean name iff EVERY alphabetic token is either (a) a Capitalized name
    token or (b) a TITLE/suffix. A single lowercase common word (village, of, mistress,
    who, ...) disqualifies the whole span -- that is a descriptive noun phrase, not a
    name (kills the 'the village of Kellynch' / 'a sensible deserving woman who ...'
    over-merge class). Titles/closed-class capitals are dropped from the returned name
    tokens. Capitalized names are position-invariant (no parser, no gold).

    `upos` (THE FORWARD WIRE, see the block above): the CATEGORY ORGAN's per-token categories for this span, in
    span order. When supplied and NAME_SOURCE != "caps", the name decision is the organ's -- the span is a name iff
    its head (the last NOUN/PROPN of the run) is a PROPN -- and capitalisation is demoted to what it actually is,
    the cue that picks WHICH tokens of a name span carry the name. Omitted -> byte-identical to the old rule."""
    if tag_post is not None and tags is not None and NAME_SOURCE != "caps" and len(tag_post):
        # THE GRADED READ (pri 118): marginalise-then-decide over the category posterior, the head chosen on
        # nominal mass, plus the span-level name-run counts.  Falls through to the token extraction below,
        # which is unchanged -- capitalisation stays what it is, the cue that picks WHICH tokens carry the name.
        _dist, _hi = mention_type_graded(list(span_toks), upos=upos, tag_post=tag_post, tags=tags,
                                         span_tab=span_tab, card_sym=card_sym, log_entc=log_entc,
                                         ent_back=ent_back,
                                         first_is_sentence_initial=first_is_sentence_initial, observe=observe)
        if max(MENTION_TYPES, key=lambda t: _dist[t]) != "name":
            return []
        if upos is None:
            upos = ["PROPN" if i == _hi else "X" for i in range(len(span_toks))]
    if upos is not None and NAME_SOURCE != "caps" and len(upos) == len(span_toks):
        if tag_post is None and not _span_head_is_name(list(span_toks), list(upos)):
            return []
        # the NAME TOKENS come from the head domain too -- "the National Library of the Netherlands" is a
        # name whose tokens are National/Library, not Netherlands (which names a different individual).
        _n = min(_np_domain(list(span_toks), list(upos)), len(span_toks)) or len(span_toks)
        out: List[str] = []
        for t, u in zip(list(span_toks)[:_n], list(upos)[:_n]):
            core = t.strip(".,'\"!?;:-()[]")
            if not core:
                continue
            low = core.lower()
            if low in TITLE_TOKENS:
                continue
            if u == "PROPN" and len(core) >= 2:
                out.append(low)
        if not out:                                   # a PROPN head the stripper threw away -- keep the head form
            core = span_toks[-1].strip(".,'\"!?;:-()[]").lower()
            if core:
                out.append(core)
        return out[:MAX_NAME_TOKENS] if len(out) <= MAX_NAME_TOKENS else []
    out: List[str] = []
    for t in span_toks:
        core = t.strip(".,'\"!?;:-()[]")
        if not core:
            continue                      # pure punctuation -> ignore
        low = core.lower()
        if low in TITLE_TOKENS:
            continue                      # title / honorific / suffix -> drop
        if core[:1].isupper() and core.isalpha() and len(core) >= 2 and low not in STOP_CAPS:
            out.append(low)               # a capitalized name token
        elif core.isalpha() and len(core) >= 2:
            return []                     # a lowercase common word -> descriptive span
        # else: short token / numeral fragment -> ignore (does not disqualify)
    if len(out) > MAX_NAME_TOKENS:
        return []                         # too long to be a name (defensive)
    return out


class EntityAliaser:
    """Incremental proper-name variant merger (situation-model entity unification).

    assign(span_toks, gender) -> canonical entity key (str) for a nominal mention,
    or None if the mention is not a clean proper name (caller groups it by surface
    head). Forward-only; a mention only ever JOINS one existing entity (canons are
    stable -- two pre-existing entities are never fused, so earlier-returned canons
    never go stale).

    STRUCTURED name model (high precision on family novels): a multi-token name has a
    GIVEN (first token) and a SURNAME (last token). Merge rules:
      - multi-token M(given, surname): join the UNIQUE gender-compatible existing
        entity whose surname is absent-or-equal AND given is absent-or-equal. A full
        name with the SAME surname but a DIFFERENT given ("Sir Walter Elliot" vs
        "William Walter Elliot") is a DIFFERENT person -> blocked (family guard).
      - single-token M(t): join the UNIQUE gender-compatible entity for which t is its
        given OR its surname OR a bare token. Ambiguous (>1, e.g. a shared family
        surname) -> ABSTAIN into a fresh bare entity (never-confidently-wrong)."""

    def __init__(self) -> None:
        self._entities: List[dict] = []          # {canon, given, surname, tokens, gender}
        self._given_index: Dict[str, List[int]] = {}
        self._surname_index: Dict[str, List[int]] = {}
        self._bare_index: Dict[str, List[int]] = {}
        self.n_new = 0
        self.n_cross_merge = 0                    # genuine cross-head unifications
        self.n_exact_attach = 0                   # same-surface / bare re-mentions joined
        self.n_abstain_new = 0                    # ambiguous -> fresh entity

    def _gender_ok(self, ei: int, gender: Optional[str]) -> bool:
        eg = self._entities[ei]["gender"]
        if gender is None or eg is None:
            return True
        return gender == eg

    def _add_role(self, idx: int, role: str, tok: Optional[str]) -> None:
        if tok is None:
            return
        index = {"given": self._given_index, "surname": self._surname_index,
                 "bare": self._bare_index}[role]
        lst = index.setdefault(tok, [])
        if idx not in lst:
            lst.append(idx)

    def _new_entity(self, given, surname, tokset, gender, bare_tok=None) -> str:
        idx = len(self._entities)
        canon = "~ent%d" % idx
        self._entities.append({"canon": canon, "given": given, "surname": surname,
                               "tokens": set(tokset), "gender": gender})
        self._add_role(idx, "given", given)
        self._add_role(idx, "surname", surname)
        self._add_role(idx, "bare", bare_tok)
        self.n_new += 1
        return canon

    def _absorb(self, ei: int, given, surname, tokset, gender) -> str:
        e = self._entities[ei]
        if e["given"] is None and given is not None:
            e["given"] = given
            self._add_role(ei, "given", given)
        if e["surname"] is None and surname is not None:
            e["surname"] = surname
            self._add_role(ei, "surname", surname)
        e["tokens"].update(tokset)
        if e["gender"] is None and gender is not None:
            e["gender"] = gender
        return e["canon"]

    def assign(self, span_toks: List[str], gender: Optional[str],
               upos: Optional[List[str]] = None) -> Optional[str]:
        # THE FORWARD WIRE (pri-109): `upos` = the category organ's categories for this span. Omitted ->
        # byte-identical to the capitalisation rule.
        toks = name_content_tokens(span_toks, upos=upos)
        if not toks:
            return None
        tokset = set(toks)
        if len(toks) >= 2:
            given, surname = toks[0], toks[-1]
            cand = set(self._surname_index.get(surname, ()))
            cand.update(self._given_index.get(given, ()))
            cand.update(self._bare_index.get(surname, ()))
            cand.update(self._bare_index.get(given, ()))
            compat = []
            for ei in cand:
                if not self._gender_ok(ei, gender):
                    continue
                e = self._entities[ei]
                if e["surname"] is not None and e["surname"] != surname:
                    continue              # different surname full name -> not this person
                if e["given"] is not None and e["given"] != given:
                    continue              # same surname, different given -> family guard
                compat.append(ei)
            if len(compat) == 1:
                self.n_cross_merge += 1
                return self._absorb(compat[0], given, surname, tokset, gender)
            return self._new_entity(given, surname, tokset, gender)
        # single-token mention (role unknown; could be given OR surname).
        t = toks[0]
        # 1. An existing BARE group for this exact token -> ALWAYS join it (surface-
        #    head grouping; this is exactly what the backbone does, so bare re-mentions
        #    NEVER fragment worse than backbone).
        bare_cands = [ei for ei in self._bare_index.get(t, ()) if self._gender_ok(ei, gender)]
        if bare_cands:
            self.n_exact_attach += 1
            return self._absorb(bare_cands[0], None, None, tokset, gender)
        # 2. No bare group yet -> merge into a UNIQUE gender-compatible FULL-name entity
        #    (the aliasing win: "Bennet"/"Elizabeth" -> the one "Elizabeth Bennet").
        full = set(self._given_index.get(t, ()))
        full.update(self._surname_index.get(t, ()))
        full = [ei for ei in full if self._gender_ok(ei, gender)]
        if len(full) == 1:
            self.n_cross_merge += 1
            return self._absorb(full[0], None, None, tokset, gender)
        # 3. Ambiguous across full names (shared family name) OR no match -> ONE bare
        #    group for this token (abstain from cross-merge; never-confidently-wrong).
        if len(full) > 1:
            self.n_abstain_new += 1
        return self._new_entity(None, None, tokset, gender, bare_tok=t)


def build_merge_map(mentions: List[dict], *, use_gazetteer: bool = False
                    ) -> Tuple[Dict[int, str], Dict[str, List[int]], dict]:
    """Run the incremental EntityAliaser over a document's mentions (reading order).

    Returns (midx_to_canon, canon_to_nominal_midxs, stats).
      midx_to_canon: nominal proper-name mention midx -> canonical entity key.
        Non-name nominal mentions and pronouns are ABSENT (caller uses surface head).
      canon_to_nominal_midxs: canonical key -> list of nominal mention midxs.
      stats: {n_new, n_cross_merge, n_exact_attach, n_abstain_new, n_name_mentions}.
    gender fed to the aliaser matches the reader's eff_gender: cue-gender, or the
    general gazetteer gender when use_gazetteer (proper names absent from cue lists)."""
    al = EntityAliaser()
    midx_to_canon: Dict[int, str] = {}
    canon_to_mid: Dict[str, List[int]] = {}
    n_name = 0
    for m in mentions:
        if m["is_pronoun"]:
            continue
        eff_gender = m.get("gender")
        if eff_gender is None and use_gazetteer:
            eff_gender = m.get("name_gender")
        canon = al.assign(m.get("span_toks", [m["head"]]), eff_gender)
        if canon is not None:
            n_name += 1
            midx_to_canon[m["midx"]] = canon
            canon_to_mid.setdefault(canon, []).append(m["midx"])
    stats = {"n_new": al.n_new, "n_cross_merge": al.n_cross_merge,
             "n_exact_attach": al.n_exact_attach, "n_abstain_new": al.n_abstain_new,
             "n_name_mentions": n_name}
    return midx_to_canon, canon_to_mid, stats


# ---------------------------------------------------------------------------
# The per-sentence reader pass (wires WorkingOverlay into a reading loop).
# ---------------------------------------------------------------------------
class CorefReader:
    """Per-sentence reader: replays mentions in reading order into a WorkingOverlay,
    resolving each target pronoun against the running overlay.

    reset_per_sentence=True  -> a FRESH overlay at each sentence boundary
                                (SINGLE-SENTENCE baseline; within-sentence only).
    reset_per_sentence=False -> a persistent overlay (CROSS-SENTENCE reader;
                                entities survive sentence boundaries).
    """

    def __init__(self, *, base=None, beta: float = 0.5, lam: float = 0.1,
                 window_k: int = 5) -> None:
        self._base = base if base is not None else SetKnownBase()
        self._beta = beta
        self._lam = lam
        self._window_k = window_k

    def _new_overlay(self) -> WorkingOverlay:
        return WorkingOverlay(base=self._base, beta=self._beta, lam=self._lam,
                              window_k=self._window_k)

    # ---- lever pick helpers (glass-box, deterministic) --------------------
    def _centering_pick(self, cands: List["object"], now: int, target_rank: int,
                        midx_to_role: Dict[int, int]) -> Optional["object"]:
        """LEVER 1 (DOMINANT): among gender-compatible candidates, pick the TOPICAL
        entity by Centering role-prominence: role-weighted mention mass (SUBJECT
        mentions weigh CENTER_SUBJECT_W, others 1.0) + recency tie-break + a role
        PARALLELISM bonus (subject pronoun prefers a subject antecedent). Breaks
        same-gender competition toward the discourse topic. First-wins tie-break."""
        if not cands:
            return None
        target_is_subj = (target_rank == 0)
        best, best_s = None, -1.0
        for e in cands:
            s = 0.0
            for mx in e.mention_midxs:
                s += CENTER_SUBJECT_W if midx_to_role.get(mx, 99) == 0 else 1.0
            s += self._beta * math.exp(-self._lam * (now - e.last_midx))
            if (midx_to_role.get(e.last_midx, 99) == 0) == target_is_subj:
                s += CENTER_PARALLEL_BONUS
            if s > best_s:
                best_s = s
                best = e
        return best

    def _adaptive_pick(self, overlay: WorkingOverlay, head: str,
                       cands: List["object"], now: int, target_rank: int,
                       midx_to_role: Dict[int, int],
                       far_strategy: str = "centering") -> Optional["object"]:
        """LEVER 2 (distance-adaptive): RECENCY owns short distance -- resolve via
        the VALIDATED recency_window (window_k) first; if NO compatible antecedent
        falls inside the window, the antecedent is far -> fall back to the far
        strategy (default CENTERING; 'maintained'/'freq' for the leave-one-out
        ablation). Window is mention-stream distance, NOT gold sentence distance
        (glass-box; the reader never sees gold to pick its strategy)."""
        ent = overlay.resolve_pronoun(head, strategy="recency_window")
        if ent is not None:
            return ent
        if far_strategy == "centering":
            return self._centering_pick(cands, now, target_rank, midx_to_role)
        return overlay.resolve_pronoun(head, strategy=far_strategy)

    def resolve_stream(self, mentions: List[dict], targets: List[dict], *,
                       reset_per_sentence: bool, strategy: str = "maintained",
                       prefer_agreement: bool = False,
                       use_gazetteer: bool = False, chain_pronouns: bool = False,
                       centering: bool = False, adaptive: bool = False,
                       far_strategy: str = "centering",
                       merge_entities: bool = False) -> List[dict]:
        """Read mentions in order; resolve each target. Returns per-target records:
          {target_midx, gold_cluster, sent_dist, bucket, resolved_head,
           resolved_cluster, attempted, correct}
        attempted=False means the reader ABSTAINED (no compatible entity in the
        overlay -> never-confidently-wrong). correct requires attempted.

        LEVERS (all default OFF = validated backbone behavior, bit-identical):
          use_gazetteer   LEVER 4: fill unknown proper-name gender from the general
                          name gazetteer (requires parse with name_gender_map).
          centering       LEVER 1 (DOMINANT): Centering role-prominence pick.
          adaptive        LEVER 2: recency-within-window else far strategy.
          chain_pronouns  LEVER 3: chain each resolved pronoun back onto its
                          antecedent entity (boost salience on pronominal mentions).
          merge_entities  STEP-1c ENTITY UNIFICATION: alias proper-name surface
                          variants into ONE canonical overlay entity BEFORE
                          resolution (build_merge_map). REQUIRES reset_per_sentence=
                          False (document-global aliasing). Salience/centering then
                          accumulate on the UNIFIED referent, not each fragment.
        centering/adaptive/chaining/merge REQUIRE reset_per_sentence=False (cross-
        sentence overlay); with reset=True the overlay-midx != mention midx and
        roles/chains would misalign -- the cell only uses these on persistent arms."""
        midx_to_canon: Dict[int, str] = {}
        if merge_entities:
            midx_to_canon, _c2m, _ms = build_merge_map(mentions, use_gazetteer=use_gazetteer)
        midx_to_role = {m["midx"]: m.get("sent_role_rank", 99) for m in mentions}
        target_by_midx = {t["target"]["midx"]: t for t in targets}
        overlay = self._new_overlay()
        head_to_cluster: Dict[str, int] = {}
        cur_sent = mentions[0]["sent_idx"] if mentions else 0
        records: List[dict] = []

        for m in mentions:
            if reset_per_sentence and m["sent_idx"] != cur_sent:
                overlay = self._new_overlay()
                head_to_cluster = {}
                cur_sent = m["sent_idx"]

            resolved_ent = None
            # Resolve EVERY gendered-singular pronoun (not only scored targets) so
            # chaining accumulates salience across the whole protagonist chain.
            if m["is_pronoun"] and m["head"] in TARGET_PRONOUNS:
                now = overlay.n_observed
                if centering or adaptive:
                    sc = PRONOUN_SCOPE[m["head"]]
                    cands = overlay._compatible_entities(sc["gender"], sc["number"])
                    trank = midx_to_role.get(m["midx"], 99)
                    if adaptive:
                        resolved_ent = self._adaptive_pick(
                            overlay, m["head"], cands, now, trank, midx_to_role,
                            far_strategy=far_strategy)
                    else:
                        resolved_ent = self._centering_pick(
                            cands, now, trank, midx_to_role)
                else:
                    resolved_ent = overlay.resolve_pronoun(
                        m["head"], strategy=strategy,
                        prefer_agreement=prefer_agreement)

                if m["midx"] in target_by_midx:
                    tinfo = target_by_midx[m["midx"]]
                    if resolved_ent is None:
                        resolved_head, resolved_cluster = None, None
                        attempted, correct = False, False
                    else:
                        resolved_head = resolved_ent.head
                        resolved_cluster = head_to_cluster.get(resolved_ent.head)
                        attempted = True
                        correct = (resolved_cluster is not None
                                   and resolved_cluster == m["cluster"])
                    records.append({
                        "target_midx": m["midx"],
                        "gold_cluster": m["cluster"],
                        "sent_dist": tinfo["sent_dist"],
                        "bucket": sent_dist_bucket(tinfo["sent_dist"]),
                        "resolved_head": resolved_head,
                        "resolved_cluster": resolved_cluster,
                        "attempted": attempted,
                        "correct": correct,
                    })

            # advance the mention stream (pronouns advance but create no entity)
            if m["is_pronoun"]:
                overlay.observe(m["head"], is_pronoun=True,
                                gender=m["gender"], number=m["number"])
                # LEVER 3: chain the resolved pronoun back onto its antecedent so
                # the antecedent's salience is boosted on this pronominal mention.
                if chain_pronouns and resolved_ent is not None:
                    resolved_ent.mention_midxs.append(m["midx"])
            else:
                eff_gender = m["gender"]
                if eff_gender is None and use_gazetteer:
                    eff_gender = m.get("name_gender")
                obs_head = m["head"]
                if merge_entities:
                    canon = midx_to_canon.get(m["midx"])
                    if canon is not None:
                        obs_head = canon
                overlay.observe(obs_head, gender=eff_gender, number=m["number"])
                head_to_cluster[obs_head] = m["cluster"]

        return records
