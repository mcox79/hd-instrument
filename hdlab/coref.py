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

import math
import os
from typing import Dict, List, Optional, Tuple

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
                        name_gender_map: Optional[Dict[str, str]] = None
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
    None reproduces the legacy fields exactly (backward-compatible)."""
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


def name_content_tokens(span_toks: List[str]) -> List[str]:
    """GENERAL clean-name extraction: the lowercased, title-stripped name tokens of a
    mention span, IFF the span is a CLEAN proper name. Empty -> the mention is NOT a
    proper name (a pronoun, a common nominal, or a DESCRIPTIVE phrase) -> no aliasing.

    A span is a clean name iff EVERY alphabetic token is either (a) a Capitalized name
    token or (b) a TITLE/suffix. A single lowercase common word (village, of, mistress,
    who, ...) disqualifies the whole span -- that is a descriptive noun phrase, not a
    name (kills the 'the village of Kellynch' / 'a sensible deserving woman who ...'
    over-merge class). Titles/closed-class capitals are dropped from the returned name
    tokens. Capitalized names are position-invariant (no parser, no gold)."""
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

    def assign(self, span_toks: List[str], gender: Optional[str]) -> Optional[str]:
        toks = name_content_tokens(span_toks)
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
