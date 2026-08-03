"""FIRST READING PASS: glass-box reading ledger for Anne of Green Gables, chapters 1-3.

Task: measure how far the reader gets on REAL prose. Not a scored experiment cell (no pre-reg,
no dispatch) -- a qualitative "watch the reader read" observability run.

ARCHITECTURE (respects the no-bolt-on-parser lock):
  EXTRACTION = supplied DATA + trivial preprocessing, NOT a parser:
    (a) NAME gazetteer: the supplied female-name list (gender_coref_density_report.json) UNIONED
        with a frequency-derived list of recurring capitalized tokens mined from the chapter text
        itself (a token counts if it appears capitalized in a NON-sentence-initial position at
        least twice -- a cheap distributional proper-noun detector, not a parser).
    (b) PRONOUN list: the fixed hdlab.coreference_resolver PRONOUN_SCOPE set (he/him/his/she/her/
        hers/it/its/they/them/their).
    (c) CLAUSE SPLITTING: sentences split on [.?!]; each sentence further split on commas/
        semicolons/colons and the bare conjunctions "and"/"but" (regex, no syntactic parse).
  Only proper-name and pronoun mentions are detected -- generic nominal NPs ("the girl", "the old
  man") are NOT extracted (no NP chunker; this is a real, reported coverage limitation).
  ROLE: clause-level agent=subject heuristic -- the FIRST mention encountered in a clause is
  tagged role=agent; every other mention in that clause is role=None (UNEXTRACTED, flagged, never
  fabricated).

COMPREHENSION = imported from hdlab, not reimplemented:
    hdlab.coreference_resolver.run_match_or_allocate  (canonical: ROBUST base that generalized on
        Anne per the promotion docstring; run_principle_b_deixis is NOT used for the main pass --
        it overfit McGuffey).
    hdlab.situation_model_accumulate.AccumulateRegister (FHRR bundle-accumulate register).
    hdlab.coreference_resolver.enrich_dialogue -- used ONLY for the bonus deixis diagnosis below,
        not wired into the main resolve pass.

Writes the full ledger (all detail) to data/exp_read_anne_glassbox_v1/ledger.json +
ledger_readable.txt. Prints only aggregate stats to stdout (content-filter-safety: no raw prose
snippets beyond 1-2 short ones).
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch

from hdlab.coreference_resolver import (
    PRONOUN_SCOPE,
    TrackedEntity,
    gn_compatible,
    normalize_tokens,
    is_pronoun_mention,
    gender_number_for,
    _resolve_name_branch,
    _observe_pronoun,
    _observe_nominal,
    _mention_geometry,
    enrich_dialogue,
    run_match_or_allocate,
    run_principle_b_deixis,
)
from hdlab.situation_model_accumulate import AccumulateRegister

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS_PATH = os.path.join(
    REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
    "anne_of_green_gables.clean.txt",
)
GENDER_REPORT_PATH = os.path.join(
    REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
    "gender_coref_density_report.json",
)
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_read_anne_glassbox_v1")
N_CHAPTERS_TO_READ = 3
SEED = 20260802

# Common capitalized function/discourse words that would otherwise pollute a naive frequency-based
# proper-noun miner (sentence-initial-heavy but occasionally non-initial too, e.g. after a dash or
# in a quoted fragment). Excluded explicitly -- this is DATA-side stoplisting, not parsing.
STOP_CAPS = frozenset({
    "The", "A", "An", "It", "Its", "She", "He", "They", "Them", "Their", "There", "But", "And",
    "If", "When", "While", "So", "For", "As", "Then", "Now", "Well", "Oh", "Yes", "No", "I", "You",
    "We", "This", "That", "These", "Those", "Here", "What", "Why", "How", "Who", "Which", "Mrs",
    "Mr", "Miss", "Master", "Chapter", "Perhaps", "Of", "In", "On", "At", "Not", "Just", "Nothing",
    "Something", "Anything", "Everything", "Everybody", "Nobody", "Somebody", "God", "Home",
})

# 2026-08-02 FIX (tokenizer/contraction bug diagnosed in the first reading pass, ba1136f1e): a raw
# apostrophe-inclusive token like "I've" / "Marilla's" was being mined/matched as ONE capitalized
# token, so curly-apostrophe contractions ("I'm", "It's", "We're", ...) polluted the gazetteer as
# spurious "recurring capitalized proper nouns" (17x "It's", 4x "We're", etc in the ch.1-3 slice) and
# a possessive like "Marilla's" silently failed to match the bare-name gazetteer entry "Marilla".
# _base_token strips a trailing apostrophe-clitic (possessive 's or a contraction suffix: 're/'ve/'d/
# 'll/'m/'t/'s), handling BOTH straight (') and curly (U+2019) apostrophes, so every downstream check
# (STOP_CAPS / gazetteer membership / missed-caps accounting) operates on the base word. This is a
# tokenizer-level DATA fix, not a parser: it never inspects syntax, only strips a fixed clitic suffix
# pattern. "I've"/"It's"/"We're" all base to "I"/"It"/"We" (already in STOP_CAPS -> excluded);
# "Marilla's"/"Barry's" base to "Marilla"/"Barry" (now correctly match the bare-name gazetteer entry).
_CLITIC_RE = re.compile(r"([A-Za-z]+)(?:['’][A-Za-z]*)?")


def _base_token(tok: str) -> str:
    """Strip a trailing apostrophe-clitic (straight ' or curly U+2019) from a raw findall token."""
    m = _CLITIC_RE.fullmatch(tok)
    return m.group(1) if m else tok


def load_chapters(n: int):
    with open(CORPUS_PATH, encoding="utf-8") as f:
        txt = f.read()
    markers = list(re.finditer(r"# CHAPTER (\d+)\s+(.*)", txt))
    chapters = []
    for i, m in enumerate(markers[:n]):
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(txt)
        chapters.append({"num": int(m.group(1)), "title": m.group(2).strip(),
                          "text": txt[start:end].strip()})
    return chapters


def sentence_split(text: str):
    # collapse newlines/whitespace first (source has hard-wrapped lines mid-sentence).
    flat = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z“‘])", flat)
    return [p.strip() for p in parts if p.strip()]


_CLAUSE_SPLIT_RE = re.compile(r"[,;:]|\b(?:and|but)\b")


def clause_split(sentence: str):
    raw = _CLAUSE_SPLIT_RE.split(sentence)
    clauses = [c.strip(" —-") for c in raw]
    return [c for c in clauses if c]


def mine_gazetteer(chapters):
    """Frequency-derived capitalized-token gazetteer (proper-noun DATA, not parsing)."""
    any_count = Counter()
    noninitial_count = Counter()
    for ch in chapters:
        for sent in sentence_split(ch["text"]):
            toks = [_base_token(t) for t in re.findall(r"[A-Za-z’']+", sent)]
            for i, t in enumerate(toks):
                if not t or not t[0].isupper():
                    continue
                if t in STOP_CAPS:
                    continue
                any_count[t] += 1
                if i != 0:
                    noninitial_count[t] += 1
    candidates = {t for t, c in noninitial_count.items() if c >= 2}
    return candidates, any_count, noninitial_count


# 2026-08-02 FIX (gazetteer person-filtering): the mined candidate set alone absorbed place/common
# nouns wholesale -- "Avonlea" (615 mentions, 604 pronouns merged into it via gender=None wildcard
# compatibility) was the dominant contamination case diagnosed in ba1136f1e. Admission now requires a
# PERSON-CONTEXT cue -- lexical/contextual DATA, not a parser (no POS tags, no dependency parse; just
# adjacent-word membership tests against small closed word lists):
#   STRONG person cues (admit regardless of place-context count):
#     - TITLE cue: preceded by Mr./Mrs./Miss/Master
#     - SPEECH-VERB cue: immediately before/after a quotative verb (said/asked/replied/...)
#   WEAK person cue: clause-initial position (crude subject-of-a-clause proxy)
#   PLACE/common-noun cue: immediately preceded by a preposition (in/at/to/from/...) or "the"
# A candidate with no strong cue is admitted only if its weak (subject-initial) cue count exceeds its
# place-cue count -- this is the majority-place exclusion the task asks for ("exclude tokens that
# appear predominantly after prepositions ... or as 'the X'").
_PREP_BEFORE = frozenset({
    "in", "at", "to", "from", "of", "near", "through", "across", "toward", "towards",
    "into", "onto", "around", "beyond", "along", "over", "up", "down", "on", "by",
})
_TITLE_BEFORE = frozenset({"mr", "mrs", "miss", "master"})
_SPEECH_VERBS = frozenset({
    "said", "says", "replied", "reply", "asked", "answered", "cried", "exclaimed",
    "whispered", "shouted", "added", "continued", "remarked", "returned", "responded", "inquired",
})


def classify_gazetteer_candidates(chapters, candidates):
    """Person-context filter over the mined candidate set (Fix 3). Returns (admitted: set[str],
    rejected: dict[str, dict]) where rejected values report the person/place cue tallies that led to
    exclusion (audit trail -- what the filter admits/rejects, not a silent drop)."""
    title_cnt = Counter()
    speech_cnt = Counter()
    subj_cnt = Counter()
    place_cnt = Counter()
    total_cnt = Counter()
    for ch in chapters:
        for sent in sentence_split(ch["text"]):
            for clause in clause_split(sent):
                bases = [_base_token(t) for t in re.findall(r"[A-Za-z’']+", clause)]
                lowers = [b.lower() for b in bases]
                for i, b in enumerate(bases):
                    if b not in candidates:
                        continue
                    total_cnt[b] += 1
                    prev_low = lowers[i - 1] if i > 0 else None
                    next_low = lowers[i + 1] if i + 1 < len(bases) else None
                    if prev_low in _TITLE_BEFORE:
                        title_cnt[b] += 1
                    if prev_low in _SPEECH_VERBS or next_low in _SPEECH_VERBS:
                        speech_cnt[b] += 1
                    if i == 0:
                        subj_cnt[b] += 1
                    if prev_low in _PREP_BEFORE or prev_low == "the":
                        place_cnt[b] += 1
    admitted = set()
    rejected = {}
    for tok in candidates:
        strong = title_cnt[tok] + speech_cnt[tok]
        weak, place = subj_cnt[tok], place_cnt[tok]
        if strong > 0 or weak > place:
            admitted.add(tok)
        else:
            rejected[tok] = {
                "title_cues": title_cnt[tok], "speech_cues": speech_cnt[tok],
                "subject_initial_cues": weak, "place_cues": place,
                "total_occurrences": total_cnt[tok],
            }
    return admitted, rejected


def load_female_names():
    with open(GENDER_REPORT_PATH, encoding="utf-8") as f:
        rep = json.load(f)
    return set(rep["summary"]["female_names_ever_appearing"])


def guess_gender(name: str, chapters, female_names):
    if name in female_names:
        return "fem"
    # cheap title-cue scan: look for "Mr. <name>" / "Master <name>" (masc) or "Mrs./Miss <name>" (fem)
    masc_pat = re.compile(r"\b(?:Mr\.|Master)\s+" + re.escape(name) + r"\b")
    fem_pat = re.compile(r"\b(?:Mrs\.|Miss)\s+" + re.escape(name) + r"\b")
    for ch in chapters:
        if masc_pat.search(ch["text"]):
            return "masc"
        if fem_pat.search(ch["text"]):
            return "fem"
    return None


def infer_gender_from_pronoun_feedback(stream, assigned, gender_of):
    """2026-08-02 FIX (gender resolution, Fix 4c): pronoun-coreference feedback. For entities whose
    name-derived gender is still unknown after title-cue + supplied-name-list resolution (was 37/52
    unknown), infer gender from the gender of PRONOUNS that resolved to the same entity in a first
    resolve pass, then backfill gender_of for every name token that entity used. Fires only when the
    entity's observed pronoun-gender history is CONSISTENT (masc-only or fem-only; no conflicting
    masc+fem pronouns resolved to the same entity) -- a noisy or genuinely-mixed-reference entity is
    left unknown rather than guessed. Caller re-runs extract_stream + resolve with the updated
    gender_of as a second pass; this narrows the gn_compatible candidate pool for later mentions of
    that same name, it does not change the first pass's own resolution (which already ran without the
    inferred gender). Returns (updated gender_of, backfilled: dict[name_token, inferred_gender]) --
    audit trail, not a silent mutation of the caller's dict."""
    pron_genders_by_eid = defaultdict(Counter)
    name_tokens_by_eid = defaultdict(set)
    for rec, eid in zip(stream, assigned):
        if rec["is_pronoun"]:
            if rec["gender"] in ("masc", "fem"):
                pron_genders_by_eid[eid][rec["gender"]] += 1
        else:
            name_tokens_by_eid[eid].add(rec["mention_text"].split()[0])

    updated = dict(gender_of)
    backfilled = {}
    for eid, toks in name_tokens_by_eid.items():
        unknown_toks = [t for t in toks if updated.get(t) is None]
        if not unknown_toks:
            continue
        genders_seen = pron_genders_by_eid.get(eid)
        if not genders_seen:
            continue
        distinct = sorted(g for g, c in genders_seen.items() if c > 0)
        if len(distinct) != 1:
            continue  # conflicting pronoun genders observed for this entity -- do not guess
        inferred = distinct[0]
        for t in unknown_toks:
            updated[t] = inferred
            backfilled[t] = inferred
    return updated, backfilled


def extract_stream(chapters, gazetteer, gender_of):
    """Build the flat mention stream (clause + text_pos ordered) across the whole read slice, plus
    the raw clause-text list, plus per-clause chapter-index map (for per-chapter ledger sections).
    Also returns unextracted-word diagnostics: capitalized tokens NOT in the gazetteer that recur
    (candidate misses -- honest coverage-gap accounting, not silently dropped)."""
    clauses_text = []
    clause_chapter = []
    stream = []
    missed_caps = Counter()
    for ch in chapters:
        for sent in sentence_split(ch["text"]):
            for clause in clause_split(sent):
                cidx = len(clauses_text)
                clauses_text.append(clause)
                clause_chapter.append(ch["num"])
                toks = [_base_token(t) for t in re.findall(r"[A-Za-z’']+", clause)]
                clause_lower = clause.lower()
                first_role_assigned = False
                pos_cursor = 0
                i = 0
                while i < len(toks):
                    t = toks[i]
                    tl = t.lower()
                    if tl in PRONOUN_SCOPE:
                        pos = clause_lower.find(tl, pos_cursor)
                        pos = pos if pos >= 0 else pos_cursor
                        pos_cursor = pos + len(tl)
                        is_pron = True
                        mention_text = t
                        gender, number = gender_number_for(mention_text, True)
                        role = "agent" if not first_role_assigned else None
                        first_role_assigned = True
                        stream.append({
                            "gold_entity": None, "clause": cidx, "mention_text": mention_text,
                            "is_pronoun": True, "gender": gender, "number": number,
                            "text_pos": pos, "has_determiner": False, "role": role,
                        })
                        i += 1
                        continue
                    if t[:1].isupper() and t in gazetteer:
                        # greedily absorb a following gazetteer token as a two-word name span
                        # (e.g. "Rachel Lynde") -- still trivial lexical merging, not a parser.
                        span_toks = [t]
                        j = i + 1
                        if j < len(toks) and toks[j][:1].isupper() and toks[j] in gazetteer:
                            span_toks.append(toks[j])
                            j += 1
                        mention_text = " ".join(span_toks)
                        pos = clause_lower.find(span_toks[0].lower(), pos_cursor)
                        pos = pos if pos >= 0 else pos_cursor
                        pos_cursor = pos + len(mention_text)
                        gender = gender_of.get(span_toks[0])
                        role = "agent" if not first_role_assigned else None
                        first_role_assigned = True
                        stream.append({
                            "gold_entity": None, "clause": cidx, "mention_text": mention_text,
                            "is_pronoun": False, "gender": gender, "number": "singular",
                            "text_pos": pos, "has_determiner": False, "role": role,
                        })
                        i = j
                        continue
                    if t[:1].isupper() and t not in STOP_CAPS and t not in gazetteer:
                        missed_caps[t] += 1
                    i += 1
    return stream, clauses_text, clause_chapter, missed_caps


def run_match_or_allocate_instrumented(stream):
    """Faithful re-execution of hdlab.coreference_resolver.run_match_or_allocate (same imported
    helpers/branches), additionally logging n_compatible per pronoun decision so the ledger can
    flag genuinely-ambiguous resolutions (>=2 gender/number-compatible candidates competing) versus
    unambiguous ones (0 or 1 candidate). Assigned ids are byte-identical to run_match_or_allocate;
    verified below via a direct comparison before the ledger is trusted."""
    entities = []
    next_id = 0
    assigned = []
    flags = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_compat = len(compat)
            if compat:
                best = max(compat, key=lambda e: e.salience(pos))
                fallback = False
            elif entities:
                best = max(entities, key=lambda e: e.last_pos)
                fallback = True
            else:
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
                fallback = False
            flags.append({"pos": pos, "is_pronoun": True, "n_compatible": n_compat,
                           "ambiguous": n_compat >= 2, "fallback_no_compatible": fallback})
            _observe_pronoun(best, pos, cur_clause, cur_role)
            assigned.append(best.eid)
            continue
        toks, has_determiner = _mention_geometry(rec)
        compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
        flags.append({"pos": pos, "is_pronoun": False, "n_compatible": len(compat),
                       "ambiguous": False, "fallback_no_compatible": False})
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
    return assigned, flags


def build_situation_model(stream, assigned, d=256):
    gen = torch.Generator().manual_seed(SEED)
    reg = AccumulateRegister(role_vocab=["agent", "mentioned"], d=d, generator=gen, max_event_slots=8)
    per_entity_events = defaultdict(list)
    counts = defaultdict(int)
    for rec, eid in zip(stream, assigned):
        role_bucket = "agent" if rec.get("role") == "agent" else "mentioned"
        eidx = min(counts[eid], 7)
        counts[eid] += 1
        reg.add_event(str(eid), role_bucket, eidx)
        per_entity_events[eid].append({"clause": rec["clause"], "role_bucket": role_bucket,
                                        "event_idx": eidx, "mention_text": rec["mention_text"]})
    decode_check = {}
    n_ok, n_total = 0, 0
    for eid in reg.entities():
        rows = []
        for ev in per_entity_events[int(eid)][:8]:
            pred, _ = reg.decode(eid, ev["event_idx"])
            ok = pred == ev["role_bucket"]
            n_total += 1
            n_ok += int(ok)
            rows.append({"event_idx": ev["event_idx"], "written": ev["role_bucket"],
                         "decoded": pred, "match": ok})
        decode_check[eid] = rows
    return per_entity_events, decode_check, (n_ok / n_total if n_total else None)


def diagnose_deixis(chapters, stream, clauses_text):
    passage = {"clauses": clauses_text}
    enriched = enrich_dialogue(passage, stream)
    n_in_quote = sum(1 for r in enriched if r["in_quote"])
    n_speaker_detected_clauses = sum(1 for c in clauses_text if _speaker_probe(c))
    straight_quote_count = sum(c.count('"') for c in clauses_text)
    curly_quote_count = sum(c.count("“") + c.count("”") for c in clauses_text)
    return enriched, {
        "n_mentions_flagged_in_quote": n_in_quote,
        "n_clauses_with_quotative_speaker_cue": n_speaker_detected_clauses,
        "n_clauses_total": len(clauses_text),
        "straight_ascii_quote_char_count_in_slice": straight_quote_count,
        "curly_unicode_quote_char_count_in_slice": curly_quote_count,
    }


def _speaker_probe(clause_text):
    from hdlab.coreference_resolver import _detect_speaker
    return _detect_speaker(clause_text) is not None


def compare_deixis_resolver(enriched_stream):
    """Structural (not correctness-graded -- Anne has no gold coref labels) comparison of
    run_principle_b_deixis against run_principle_b + run_match_or_allocate on the same enriched
    stream, once enrich_dialogue can actually see quote spans (Fix 1). Reports how often the deixis
    filter fires and how many assignment decisions it changes relative to each baseline resolver --
    the honest ceiling of what's measurable without a gold-annotated Anne coref set."""
    from hdlab.coreference_resolver import run_principle_b as _rpb
    mo_a = run_match_or_allocate(enriched_stream)
    pb, _pb_actions = _rpb(enriched_stream)
    pbd, pbd_actions = run_principle_b_deixis(enriched_stream)
    n_differs_from_pb = sum(1 for a, b in zip(pb, pbd) if a != b)
    n_differs_from_moa = sum(1 for a, b in zip(mo_a, pbd) if a != b)
    return {
        "deixis_action_counts": pbd_actions,
        "n_mentions": len(enriched_stream),
        "n_assignments_differ_from_run_principle_b": n_differs_from_pb,
        "n_assignments_differ_from_run_match_or_allocate": n_differs_from_moa,
        "note": ("structural firing/divergence counts only -- Anne ch.1-3 has no gold coreference "
                 "annotation, so whether the divergences are CORRECTIONS or new errors is not "
                 "measurable here; deixis_fired>0 confirms the mechanism now activates on real "
                 "curly-quoted prose (Fix 1), which it could not before (0 spans found)."),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters = load_chapters(N_CHAPTERS_TO_READ)
    female_names = load_female_names()
    gaz_candidates_raw, any_count, noninitial_count = mine_gazetteer(chapters)

    # Fix 3: person-context filter over the mined candidates (place/common-noun names like "Avonlea"
    # never get a person cue and are rejected).
    gaz_admitted, gaz_rejected = classify_gazetteer_candidates(chapters, gaz_candidates_raw)

    gazetteer = gaz_admitted | female_names
    gender_of_pass1 = {n: guess_gender(n, chapters, female_names) for n in gazetteer}

    # ---- Pass 1: title-cue + supplied-name-list gender only ----
    stream1, clauses_text, clause_chapter, missed_caps = extract_stream(
        chapters, gazetteer, gender_of_pass1)
    assigned1 = run_match_or_allocate(stream1)

    # Fix 4: pronoun-coreference feedback -- backfill gender_of for entities whose pronoun history is
    # gender-consistent, then re-extract + re-resolve with the enriched gender map (Pass 2).
    gender_of, gender_backfilled = infer_gender_from_pronoun_feedback(stream1, assigned1, gender_of_pass1)
    if gender_backfilled:
        stream2, clauses_text, clause_chapter, missed_caps = extract_stream(
            chapters, gazetteer, gender_of)
    else:
        stream2 = stream1

    # Pass 3 (safety gate, discovered empirically re-running this script after Fixes 3+4: a MINED
    # candidate that clears the person-context filter -- Fix 3 -- but never resolves a gender via
    # EITHER title-cue OR pronoun feedback is structurally the same wildcard-magnet failure mode that
    # made "Avonlea" absorb 604 pronouns: gn_compatible treats gender=None as compatible with every
    # entity, so an unresolved-gender mined token silently magnetizes any nearby compatible pronoun
    # ("June" -- a calendar-month common noun that slipped past the person-context filter via a
    # clause-initial false-positive subject cue -- absorbed 232 pronoun mentions under only Fixes 3+4).
    # Supplied female_names are NEVER dropped here (trusted DATA, not subject to this gate) -- only
    # mined candidates. Re-extract + re-resolve one final time with the reduced gazetteer.
    assigned2 = run_match_or_allocate(stream2)
    unresolved_mined = {t for t in gaz_admitted if gender_of.get(t) is None}
    if unresolved_mined:
        gazetteer = gazetteer - unresolved_mined
        stream, clauses_text, clause_chapter, missed_caps = extract_stream(
            chapters, gazetteer, gender_of)
    else:
        stream = stream2

    # sanity: the instrumented resolver must reproduce run_match_or_allocate bit-for-bit before the
    # ledger's assignment ids can be trusted as "the canonical reader's output".
    canonical_assigned = run_match_or_allocate(stream)
    assigned, flags = run_match_or_allocate_instrumented(stream)
    assert assigned == canonical_assigned, "instrumented wrapper diverged from run_match_or_allocate"

    per_entity_events, decode_check, decode_acc = build_situation_model(stream, assigned)
    enriched_stream, deixis_diag = diagnose_deixis(chapters, stream, clauses_text)
    deixis_resolver_comparison = compare_deixis_resolver(enriched_stream)

    # per-entity summary: canonical name = most frequent NAME-type mention text, else "PRON-only-<eid>"
    name_mentions_by_eid = defaultdict(Counter)
    mention_count_by_eid = Counter()
    clause_span_by_eid = defaultdict(list)
    for rec, eid in zip(stream, assigned):
        mention_count_by_eid[eid] += 1
        clause_span_by_eid[eid].append(rec["clause"])
        if not rec["is_pronoun"]:
            name_mentions_by_eid[eid][rec["mention_text"]] += 1

    entity_ledger = []
    for eid in sorted(mention_count_by_eid):
        names = name_mentions_by_eid[eid]
        canonical = names.most_common(1)[0][0] if names else f"PRON-only-entity-{eid}"
        spans = clause_span_by_eid[eid]
        entity_ledger.append({
            "eid": eid, "canonical_name_guess": canonical,
            "mention_count": mention_count_by_eid[eid],
            "n_distinct_name_forms": len(names),
            "name_forms": dict(names),
            "first_clause": min(spans), "last_clause": max(spans),
            "consolidated": mention_count_by_eid[eid] >= 3,
        })
    entity_ledger.sort(key=lambda r: -r["mention_count"])

    n_role_unassigned = sum(1 for r in stream if r.get("role") is None)
    n_ambiguous = sum(1 for f in flags if f["ambiguous"])
    n_fallback = sum(1 for f in flags if f["fallback_no_compatible"])
    n_pron = sum(1 for r in stream if r["is_pronoun"])
    n_name = len(stream) - n_pron
    n_singleton = sum(1 for e in entity_ledger if e["mention_count"] == 1)
    n_consolidated = sum(1 for e in entity_ledger if e["consolidated"])

    per_chapter = defaultdict(lambda: {"n_clauses": 0, "n_mentions": 0, "entities_touched": set()})
    for cidx, chnum in enumerate(clause_chapter):
        per_chapter[chnum]["n_clauses"] += 1
    for rec, eid in zip(stream, assigned):
        chnum = clause_chapter[rec["clause"]]
        per_chapter[chnum]["n_mentions"] += 1
        per_chapter[chnum]["entities_touched"].add(eid)
    per_chapter_summary = {
        str(k): {"n_clauses": v["n_clauses"], "n_mentions": v["n_mentions"],
                 "n_distinct_entities_touched": len(v["entities_touched"])}
        for k, v in sorted(per_chapter.items())
    }

    ledger = {
        "chapters_read": [{"num": c["num"], "title": c["title"]} for c in chapters],
        "extraction_description": {
            "gazetteer_size": len(gazetteer),
            "gazetteer_female_supplied": sorted(female_names),
            "gazetteer_mined_candidates_raw": sorted(gaz_candidates_raw),
            "gazetteer_mined_candidates_admitted": sorted(gaz_admitted),
            "gazetteer_person_filter_rejected": gaz_rejected,
            "gender_assigned": {k: v for k, v in gender_of.items() if v is not None},
            "gender_unknown_count": sum(1 for v in gender_of.values() if v is None),
            "gender_backfilled_via_pronoun_feedback": gender_backfilled,
            "gazetteer_dropped_unresolved_gender_mined_tokens": sorted(unresolved_mined),
            "n_clauses_total": len(clauses_text),
            "n_mentions_total": len(stream),
            "n_pronoun_mentions": n_pron,
            "n_name_mentions": n_name,
            "missed_capitalized_tokens_recurring": {k: v for k, v in missed_caps.items() if v >= 2},
        },
        "deixis_resolver_comparison": deixis_resolver_comparison,
        "flagged_gaps": {
            "role_unassigned_count": n_role_unassigned,
            "role_unassigned_fraction": n_role_unassigned / len(stream) if stream else None,
            "ambiguous_pronoun_resolutions": n_ambiguous,
            "fallback_no_compatible_candidate": n_fallback,
        },
        "consolidation": {
            "n_entities_tracked": len(entity_ledger),
            "n_consolidated_ge3_mentions": n_consolidated,
            "n_singleton_1_mention": n_singleton,
            "situation_model_decode_self_consistency": decode_acc,
        },
        "entities": entity_ledger,
        "per_chapter": per_chapter_summary,
        "deixis_diagnosis": deixis_diag,
        "situation_model_decode_detail_sample": {
            str(eid): rows for eid, rows in list(decode_check.items())[:5]
        },
    }

    ledger_path = os.path.join(OUT_DIR, "ledger.json")
    tmp = ledger_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ledger_path)

    readable_path = os.path.join(OUT_DIR, "ledger_readable.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write("GLASS-BOX READING LEDGER -- Anne of Green Gables ch.1-3\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Chapters: {[c['num'] for c in chapters]}\n")
        f.write(f"Clauses: {len(clauses_text)}  Mentions: {len(stream)} "
                f"(pron={n_pron}, name={n_name})\n")
        f.write(f"Entities tracked: {len(entity_ledger)} "
                f"(consolidated>=3mentions={n_consolidated}, singleton={n_singleton})\n\n")
        f.write("TOP TRACKED ENTITIES:\n")
        for e in entity_ledger[:15]:
            f.write(f"  eid={e['eid']:>3}  {e['canonical_name_guess']:<20} "
                     f"mentions={e['mention_count']:<4} clauses[{e['first_clause']}-{e['last_clause']}] "
                     f"consolidated={e['consolidated']}\n")
        f.write("\nFLAGGED GAPS:\n")
        f.write(json.dumps(ledger["flagged_gaps"], indent=2) + "\n")
        f.write("\nDEIXIS DIAGNOSIS:\n")
        f.write(json.dumps(deixis_diag, indent=2) + "\n")
        f.write("\nPER-CHAPTER:\n")
        f.write(json.dumps(per_chapter_summary, indent=2) + "\n")

    print(json.dumps({
        "chapters_read": [c["num"] for c in chapters],
        "n_clauses": len(clauses_text),
        "n_mentions": len(stream), "n_pronoun_mentions": n_pron, "n_name_mentions": n_name,
        "n_entities_tracked": len(entity_ledger),
        "n_consolidated": n_consolidated, "n_singleton": n_singleton,
        "role_unassigned_fraction": round(n_role_unassigned / len(stream), 4) if stream else None,
        "ambiguous_pronoun_resolutions": n_ambiguous,
        "ambiguous_pronoun_rate": round(n_ambiguous / n_pron, 4) if n_pron else None,
        "fallback_no_compatible": n_fallback,
        "situation_model_decode_self_consistency": decode_acc,
        "deixis_diagnosis": deixis_diag,
        "deixis_resolver_comparison": deixis_resolver_comparison,
        "gazetteer_mined_raw_count": len(gaz_candidates_raw),
        "gazetteer_mined_admitted_count": len(gaz_admitted),
        "gazetteer_person_filter_rejected_count": len(gaz_rejected),
        "gender_unknown_count": sum(1 for v in gender_of.values() if v is None),
        "gender_backfilled_count": len(gender_backfilled),
        "top_entity_by_mentions": {
            "canonical_name_guess": entity_ledger[0]["canonical_name_guess"],
            "mention_count": entity_ledger[0]["mention_count"],
        } if entity_ledger else None,
        "ledger_path": ledger_path,
        "readable_path": readable_path,
    }, indent=2))


if __name__ == "__main__":
    main()
