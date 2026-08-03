"""SECOND READING PASS: the HONESTY FIX + CONSOLIDATION LEDGER on Anne of Green Gables ch.6/9/16.

Builds on tools/read_anne_glassbox_v1.py (commit 18a0341b8, ch.1-3). Same extraction pipeline
(gazetteer mining + person-context filter + gender resolution passes), retargeted to chapters 6, 9,
16 -- the chapters containing the 6 verified-pending gold coref scenes in
data/eval_gold_mention_role_mcguffey_v1/gold_anne_coref_scenes_v1.jsonl -- so consolidation can be
scored against real gold instead of only reported structurally.

THE HONESTY FIX (core change, the reason this script exists as a v2 rather than a v1 chapter-swap):
v1's pronoun resolution (hdlab.coreference_resolver.run_match_or_allocate) has a silent fallback --
when a pronoun has ZERO gender/number-compatible tracked entity, it force-attaches to the most
RECENT entity regardless of gender/number compatibility (`elif entities: best = max(entities,
key=lambda e: e.last_pos)`). That is a FALSE CONSOLIDATION by construction: the pronoun is bound to
an entity the resolver's own agreement filter says is NOT plausible. It also overflows each
force-attached entity's AccumulateRegister with spurious events (bundling capacity is bounded), which
is the diagnosed root cause of the ch.1-3 situation-model decode-self-consistency regression
(89.8% -> 67.2%).

FIX: `resolve_honest()` below is a from-scratch re-implementation of the SAME algorithm (same
TrackedEntity, same gn_compatible filter, same salience pick, same name/nominal branch -- all
imported unchanged from hdlab.coreference_resolver / hdlab.state_of_mind) with exactly ONE behavior
change: when a pronoun has zero compatible candidates, it is FLAGGED as unresolved and NOT bound to
any entity (no _observe_pronoun call -- the register never sees it). A second, honesty-motivated
change: when a pronoun has >=2 compatible candidates whose salience scores are within
CONFIDENCE_MARGIN_THRESHOLD of each other (a genuine same-gender competition -- exactly the construct
the gold set targets), it is likewise flagged NOT-CONSOLIDATED rather than silently picking the
top-salience guess. This is the ONE conceptual variable this script changes relative to v1; the
hdlab canonical module itself is left untouched (this is an instrumented re-implementation local to
the observability script, not a change to the shared promoted resolver other cells depend on).

WILDCARD-SEED FIX (discovered validating the above -- see resolve_honest()'s "else" branch comment):
the baseline pronoun-seed-new-entity branch never records the seeding pronoun's gender/number on the
entity it creates, so that entity's gender/number stay None forever and gn_compatible's None-is-a-
wildcard rule makes it silently compatible with every later pronoun of every gender. This masked the
honesty fix's own discriminator (measured 0/514 force-attaches on the first run -- an untested
discriminator per DISCRIMINATOR-MUST-SURVIVE-SCALE). Fixed by recording the seeding pronoun's own
gender/number on entity creation, same as a name-seeded entity already records the name's gender.

RESOLVER SWAP + MASCULINE-GENDER FIX (2026-08-02, attacking the same-gender false-consolidation
residual from commit 2944a14f4): adjudication of the first honest ledger found ALL 11 false
consolidations were female->female (e.g. Blewett's "she" absorbed by far-more-frequent Marilla) --
the base resolver's frequency-dominant Centering salience (hdlab.coreference_resolver.
run_match_or_allocate) lets the protagonist's raw mention-count absorb a just-introduced same-gender
character. Two changes, run BEFORE/AFTER on the identical extraction stream so the delta isolates the
resolver's effect (any sentence-alignment artifact in score_scene_against_gold cancels in the
comparison):
  (1) RESOLVER: `resolve_honest(stream, pick_mode=...)` now supports pick_mode="strict_cb", which
      swaps the pronoun pick from salience (frequency+recency blend) to hdlab.coreference_resolver's
      literal-Centering `_pick_strict_cb` (a HARD most-recent-subject-clause preference, i.e. recency
      among grammatically-prominent antecedents) -- imported unchanged, not reimplemented. The near-
      tie ambiguity flag uses the mode-native margin: relative salience gap (<0.10) for salience mode,
      `_pronoun_strict_cb_margin`'s criterion tie (==0.0) for strict_cb mode. Both modes share the
      identical honesty fix (0-compatible -> flag, never force-attach) and identical name/nominal
      branch.
  (2) MASCULINE GENDER: `guess_gender_v2` extends v1.guess_gender's direct Mr./Master/Mrs./Miss
      title-cue scan with a SURNAME-BRIDGE cue (`build_surname_bigrams`): a first name that is never
      itself directly titled (e.g. "Matthew" -- Anne of Green Gables never writes "Mr. Matthew", only
      "Mr. Cuthbert") inherits masculine/feminine gender from a co-occurring "Firstname Surname"
      bigram (e.g. "Matthew Cuthbert") whose SURNAME does carry a direct title cue elsewhere in the
      text ("Mr. Cuthbert" -> masc). Guards: direct title/name-list cue always takes priority (this
      branch only fires on v1.guess_gender's None); a name already in female_names is never
      overridden; disagreeing surname cues abstain (None) rather than guess. This targets the
      diagnosed root cause of the 22 unresolved he/him/his mentions: without it, "Matthew" never
      resolves a gender, gets DROPPED from the gazetteer entirely (gender_of.get(t) is None ->
      excluded), and the 22 masculine pronouns have no masculine-or-wildcard entity left to bind to.

THE CONSOLIDATION LEDGER: every mention gets a FLAGGED/OUTCOME record. FLAGGED categories:
  - unresolved_pronoun_no_compatible_candidate (the fix's primary target)
  - low_confidence_ambiguous_pronoun (near-tie among >=2 compatible candidates)
  - generic_np_referent (gold-confirmed referring expressions like "that lady" that the no-NP-chunker
    extraction structurally cannot see -- counted via a fixed closed-word-list scan, not claimed as
    individually-tracked mentions)
  - gazetteer_gender_unknown_dropped (mined candidate never resolved a gender)
LEARN-ATTEMPT documents what the pipeline tried before flagging (gn_compatible search size, margin,
person-context cue tally). OUTCOME is CONSOLIDATED (bound to a stable entity, mention_count>=1 in that
entity, decode-participating) or NOT-CONSOLIDATED (flagged gap, never bound).

FALSE-CONSOLIDATION SCORING vs gold: for each of the 6 gold scenes, gold's own
hdlab.coreference_resolver.build_mention_stream(scene) gives the canonical gold-ordered mention list.
Each gold mention is greedy-matched (in order, by pronoun-word or content-token equality) against this
script's own extraction stream restricted to the scene's chapter + best-matching sentence window
(fuzzy-located via difflib against the sentence-range hint in the gold record, since gold's clause
segmentation is coarser than this pipeline's clause_split). For every CONSOLIDATED (bound) mention
that matches a gold mention, the reader's assigned entity-id is compared against the MAJORITY gold
entity of all matched mentions sharing that same entity-id within the scene; a minority disagreement
is a false consolidation. Reported per NOTE: gold_verified=false on all 6 scenes -- these numbers are
PENDING Director spot-check, not a certified score.

GLASS-BOX: no NER/parser/borrowed embeddings; every extraction step is either imported unchanged from
hdlab (the wired, VET'd capability) or a fixed closed-word-list / regex DATA rule, exactly as v1.
Determinism: fixed SEED, sorted() iteration only, no hash()-seeded randomness.
"""
from __future__ import annotations

import difflib
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
    build_mention_stream,
    gn_compatible,
    gender_number_for,
    is_pronoun_mention,
    run_match_or_allocate,
    _mention_geometry,
    _observe_nominal,
    _observe_pronoun,
    _pick_strict_cb,
    _pronoun_strict_cb_margin,
    _resolve_name_branch,
)
from hdlab.situation_model_accumulate import make_situation_register

# Reuse v1's extraction machinery verbatim (gazetteer mining, person-context filter, gender passes,
# tokenizer clitic-stripping) -- only the chapter selection + resolver + ledger logic differ.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import read_anne_glassbox_v1 as v1  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_PATH = os.path.join(
    REPO_ROOT, "data", "eval_gold_mention_role_mcguffey_v1", "gold_anne_coref_scenes_v1.jsonl",
)
OUT_DIR = os.path.join(REPO_ROOT, "data", "exp_read_anne_glassbox_v2_honest_ledger")
CHAPTERS_TO_READ = [6, 9, 16]
SEED = 20260802
CONFIDENCE_MARGIN_THRESHOLD = 0.10  # relative salience margin; near-tie among >=2 compat -> flag

# Closed word list (DATA, not a parser) for the generic-NP referring-expression coverage gap: person-
# referring common nouns this extraction structurally never mines (no NP chunker). Counts occurrences
# of determiner + one of these nouns as an honest lower-bound tally of the gap, matching the gold-
# confirmed case "that lady" (gold scene 1, referring to Rachel).
_GENERIC_PERSON_NOUNS = frozenset({
    "lady", "woman", "girl", "boy", "child", "man", "creature", "orphan", "stranger", "thing",
})
_GENERIC_NP_RE = re.compile(
    r"\b(?:the|a|an|that|this|those|these)\s+[a-z-]+\s+(" +
    "|".join(_GENERIC_PERSON_NOUNS) + r")\b", re.IGNORECASE,
)
_GENERIC_NP_RE_SIMPLE = re.compile(
    r"\b(?:the|a|an|that|this|those|these)\s+(" + "|".join(_GENERIC_PERSON_NOUNS) + r")\b",
    re.IGNORECASE,
)


def load_chapters_by_number(nums):
    with open(v1.CORPUS_PATH, encoding="utf-8") as f:
        txt = f.read()
    markers = list(re.finditer(r"# CHAPTER (\d+)\s+(.*)", txt))
    by_num = {}
    for i, m in enumerate(markers):
        n = int(m.group(1))
        if n in nums:
            start = m.end()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(txt)
            by_num[n] = {"num": n, "title": m.group(2).strip(), "text": txt[start:end].strip()}
    return [by_num[n] for n in nums if n in by_num]


def load_all_chapters():
    """Every chapter in the corpus (38 total), for whole-book gender-cue scans only (build_
    surname_bigrams / guess_gender_v2's title-cue lookups) -- NOT for extraction/resolution, which
    stays scoped to CHAPTERS_TO_READ. Same precedent as the supplied female_names list (loaded from a
    whole-corpus gender_coref_density_report.json): a name/title dictionary is allowed DATA scope
    even when the read/resolve window is 3 chapters (Matthew's only "Firstname Surname" bigram,
    "Matthew Cuthbert", occurs in ch.1-3, outside the ch.6/9/16 read slice -- restricting the cue scan
    to the read slice silently starved the surname-bridge of the one bigram it needs)."""
    with open(v1.CORPUS_PATH, encoding="utf-8") as f:
        txt = f.read()
    markers = list(re.finditer(r"# CHAPTER (\d+)\s+(.*)", txt))
    out = []
    for i, m in enumerate(markers):
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(txt)
        out.append({"num": int(m.group(1)), "title": m.group(2).strip(), "text": txt[start:end].strip()})
    return out


def extract_stream_with_sentence_idx(chapters, gazetteer, gender_of):
    """Same as v1.extract_stream but additionally records, per clause, the SENTENCE index it came
    from within its chapter (0-based, per v1.sentence_split) -- needed to locate a gold scene's
    source_sentence_range in this pipeline's own clause stream."""
    clauses_text, clause_chapter, clause_sentence_idx = [], [], []
    stream = []
    missed_caps = Counter()
    for ch in chapters:
        for sidx, sent in enumerate(v1.sentence_split(ch["text"])):
            for clause in v1.clause_split(sent):
                cidx = len(clauses_text)
                clauses_text.append(clause)
                clause_chapter.append(ch["num"])
                clause_sentence_idx.append(sidx)
                toks = [v1._base_token(t) for t in re.findall(r"[A-Za-z’']+", clause)]
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
                    if t[:1].isupper() and t not in v1.STOP_CAPS and t not in gazetteer:
                        missed_caps[t] += 1
                    i += 1
    return stream, clauses_text, clause_chapter, clause_sentence_idx, missed_caps


def build_surname_bigrams(chapters):
    """Firstname -> set(surnames) DATA-only distributional cue (not parsing): scans every adjacent
    capitalized-capitalized token pair ("Matthew Cuthbert") in sentence order, both tokens outside
    STOP_CAPS. Feeds guess_gender_v2's surname-bridge title-cue inference."""
    pairs: dict[str, set] = defaultdict(set)
    for ch in chapters:
        for sent in v1.sentence_split(ch["text"]):
            toks = [v1._base_token(t) for t in re.findall(r"[A-Za-z’']+", sent)]
            for i in range(len(toks) - 1):
                a, b = toks[i], toks[i + 1]
                if (a and b and a[0].isupper() and b[0].isupper()
                        and a not in v1.STOP_CAPS and b not in v1.STOP_CAPS):
                    pairs[a].add(b)
    return pairs


def guess_gender_v2(name, chapters, female_names, surname_bigrams):
    """v1.guess_gender's direct Mr./Mrs./Miss/Master title-cue scan, extended with a SURNAME-BRIDGE
    cue for first names that are never themselves directly titled (Anne of Green Gables never writes
    "Mr. Matthew", only "Mr. Cuthbert"): if `name` co-occurs as the first token of a "Firstname
    Surname" bigram whose SURNAME does carry a direct masc (Mr./Master) or fem (Mrs./Miss) title cue
    elsewhere in the text, inherit that gender. Guards: direct cue (incl. supplied female_names list,
    checked first inside v1.guess_gender) always takes priority -- this branch only fires when
    v1.guess_gender returns None; a name in female_names is never overridden even if v1.guess_gender's
    ordering somehow missed it; disagreeing surname cues (one masc-titled, another fem-titled) abstain
    (None) rather than guess."""
    direct = v1.guess_gender(name, chapters, female_names)
    if direct is not None:
        return direct
    if name in female_names:
        return "fem"
    found = set()
    for surname in surname_bigrams.get(name, ()):
        masc_pat = re.compile(r"\b(?:Mr\.|Master)\s+" + re.escape(surname) + r"\b")
        fem_pat = re.compile(r"\b(?:Mrs\.|Miss)\s+" + re.escape(surname) + r"\b")
        for ch in chapters:
            if masc_pat.search(ch["text"]):
                found.add("masc")
            if fem_pat.search(ch["text"]):
                found.add("fem")
    return next(iter(found)) if len(found) == 1 else None


def resolve_honest(stream, pick_mode="salience"):
    """MATCH-OR-ALLOCATE with the honesty fix, plus a swappable pronoun pick rule (pick_mode in
    {"salience", "strict_cb"}). Identical mechanism to hdlab.coreference_resolver.run_match_or_allocate
    (pick_mode="salience") or run_strict_cb (pick_mode="strict_cb") for every branch EXCEPT the
    pronoun no-compatible-candidate fallback: instead of force-attaching to the most recent entity,
    the mention is flagged UNRESOLVED and never bound (no _observe_pronoun call). A second flag fires
    on a genuine same-candidate-pool near-tie -- the mode-native ambiguity signal: relative salience
    margin < CONFIDENCE_MARGIN_THRESHOLD for "salience" mode, hdlab.coreference_resolver.
    _pronoun_strict_cb_margin's criterion tie (==0.0, i.e. no distinguishing most-recent-subject-clause
    evidence) for "strict_cb" mode -- also left unbound. Returns (assigned: list[Optional[int]],
    ledger_rows: list[dict]) where assigned[i] is None for any flagged/unconsolidated mention."""
    assert pick_mode in ("salience", "strict_cb"), pick_mode
    entities: list[TrackedEntity] = []
    next_id = 0
    assigned: list[int | None] = []
    rows = []
    for pos, rec in enumerate(stream):
        gender, number = rec["gender"], rec["number"]
        cur_clause, cur_role = rec["clause"], rec.get("role")
        if rec["is_pronoun"]:
            compat = [e for e in entities if gn_compatible(gender, number, e.gender, e.number)]
            n_compat = len(compat)
            if compat:
                if pick_mode == "strict_cb":
                    picked = _pick_strict_cb(compat, cur_clause)
                    margin = _pronoun_strict_cb_margin(compat, cur_clause)
                    is_near_tie = n_compat >= 2 and margin == 0.0
                    learn_pick = (f"strict_cb pick (literal-Centering most-recent-subject-clause) "
                                  f"over {n_compat} candidates; criterion margin={margin}")
                else:
                    scored = sorted(((e.salience(pos), e) for e in compat), key=lambda t: -t[0])
                    top_sal = scored[0][0]
                    second_sal = scored[1][0] if len(scored) > 1 else None
                    margin = 1.0 if second_sal is None else (
                        (top_sal - second_sal) / top_sal if top_sal > 0 else 0.0)
                    is_near_tie = n_compat >= 2 and margin < CONFIDENCE_MARGIN_THRESHOLD
                    picked = scored[0][1]
                    learn_pick = (f"salience pick over {n_compat} candidates; "
                                  f"top-2 margin={margin:.4f}")
                if is_near_tie:
                    assigned.append(None)
                    rows.append({
                        "pos": pos, "clause": cur_clause, "mention_text": rec["mention_text"],
                        "is_pronoun": True, "flagged": "low_confidence_ambiguous_pronoun",
                        "outcome": "NOT_CONSOLIDATED",
                        "learn_attempt": f"gn_compatible search found {n_compat} candidates; "
                                         f"{learn_pick} < mode-native ambiguity threshold",
                        "n_compatible": n_compat, "margin": margin,
                    })
                    continue
                best = picked
                _observe_pronoun(best, pos, cur_clause, cur_role)
                assigned.append(best.eid)
                rows.append({
                    "pos": pos, "clause": cur_clause, "mention_text": rec["mention_text"],
                    "is_pronoun": True, "flagged": None, "outcome": "CONSOLIDATED",
                    "learn_attempt": f"gn_compatible search found {n_compat} candidates; "
                                     f"resolved via {learn_pick}",
                    "n_compatible": n_compat, "margin": margin, "assigned_eid": best.eid,
                })
            elif entities:
                # THE FIX: previously `best = max(entities, key=lambda e: e.last_pos)` (force-attach
                # to most recent entity regardless of gender/number compatibility). Now: flag and do
                # NOT bind -- the register never sees a spurious event for this mention.
                assigned.append(None)
                rows.append({
                    "pos": pos, "clause": cur_clause, "mention_text": rec["mention_text"],
                    "is_pronoun": True, "flagged": "unresolved_pronoun_no_compatible_candidate",
                    "outcome": "NOT_CONSOLIDATED",
                    "learn_attempt": f"gn_compatible search over {len(entities)} tracked entities "
                                     f"found 0 compatible (gender={gender}, number={number}); "
                                     f"HONESTY FIX: no force-attach, flagged instead",
                    "n_compatible": 0, "margin": None,
                })
            else:
                # SECOND FIX (uncovered while validating the first fix -- see WILDCARD-SEED note
                # below): baseline _observe_pronoun never records gender/number on the entity it
                # seeds, so a pronoun-seeded entity keeps gender=None/number=None FOREVER (pronoun
                # observations never set them; only a later NAME mention would). Under gn_compatible,
                # None is a wildcard on BOTH sides -- that entity then silently matches every future
                # pronoun of every gender/number, which masks the exact "zero compatible candidate"
                # case the honesty fix targets (verified empirically: with this bug, the fix's
                # force-attach counter measured 0/514 across ch.6/9/16, an obviously-untested
                # discriminator per DISCRIMINATOR-MUST-SURVIVE-SCALE -- entity-0, seeded by the very
                # first pronoun "they", was silently wildcard-absorbing candidates it should not be
                # compatible with). Fix: a pronoun-seeded entity records the seeding pronoun's own
                # gender/number immediately, exactly as a name-seeded entity already records the
                # name's inferred gender via _observe_nominal. This is the SAME fallback code path
                # this script already re-implements (not a change to the shared hdlab module).
                best = TrackedEntity(next_id)
                next_id += 1
                entities.append(best)
                best.gender = gender
                best.number = number
                _observe_pronoun(best, pos, cur_clause, cur_role)
                assigned.append(best.eid)
                rows.append({
                    "pos": pos, "clause": cur_clause, "mention_text": rec["mention_text"],
                    "is_pronoun": True, "flagged": None, "outcome": "CONSOLIDATED",
                    "learn_attempt": "no tracked entities yet; seeded new entity carrying the "
                                     "pronoun's own gender/number (WILDCARD-SEED fix; unavoidable "
                                     "first-mention case otherwise unchanged from baseline)",
                    "n_compatible": 0, "margin": None, "assigned_eid": best.eid,
                })
            continue
        # name/nominal branch: unchanged from baseline -- always resolves (match or allocate new),
        # never a force-attach case, so out of scope for the honesty fix.
        toks, has_determiner = _mention_geometry(rec)
        compat_n = len([e for e in entities if gn_compatible(gender, number, e.gender, e.number)])
        best, next_id = _resolve_name_branch(entities, next_id, gender, number, toks, has_determiner)
        _observe_nominal(best, pos, cur_clause, cur_role, gender, number, toks)
        assigned.append(best.eid)
        rows.append({
            "pos": pos, "clause": cur_clause, "mention_text": rec["mention_text"],
            "is_pronoun": False, "flagged": None, "outcome": "CONSOLIDATED",
            "learn_attempt": f"name/nominal token-overlap branch ({compat_n} gender-compatible "
                              f"entities); always resolves (match or allocate new)",
            "n_compatible": compat_n, "margin": None, "assigned_eid": best.eid,
        })
    return assigned, rows


def build_situation_model_consolidated_only(stream, assigned, d=256, backend="multibank"):
    """Same algebra as v1.build_situation_model, but skips any mention with assigned eid None (the
    honesty fix's flagged/unconsolidated mentions never touch the register).

    backend="multibank" (default, 2026-08-03): routes through
    hdlab.situation_model_accumulate.make_situation_register, which defaults to
    MultiBankAccumulateRegister (n_banks=8, validated capacity headroom -- see that factory's
    docstring). At this reader's pilot scale (few mentions/entity per chapter) multibank and
    flat decode identically; this is capacity-headroom future-proofing, not a claimed accuracy
    lift at current scale. Pass backend="flat" to reproduce the prior AccumulateRegister-only
    behavior exactly."""
    gen = torch.Generator().manual_seed(SEED)
    reg = make_situation_register(
        role_vocab=["agent", "mentioned"], d=d, generator=gen, max_event_slots=8, backend=backend
    )
    per_entity_events = defaultdict(list)
    counts = defaultdict(int)
    n_skipped = 0
    for rec, eid in zip(stream, assigned):
        if eid is None:
            n_skipped += 1
            continue
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
    return per_entity_events, decode_check, (n_ok / n_total if n_total else None), n_skipped


def _content_tokens(text):
    """Lowercase content-token set for cross-format (gold-vs-extraction) matching: strips titles,
    trailing possessive/contraction clitics, and pure-stopword tokens."""
    TITLE = {"mr", "mrs", "miss", "master"}
    STOP = {"the", "a", "an", "that", "this", "those", "these"}
    base = [v1._base_token(t).lower() for t in re.findall(r"[A-Za-z’']+", text)]
    return {t for t in base if t and t not in TITLE and t not in STOP}


def locate_scene_window(clauses_text, clause_chapter, clause_sentence_idx, chapter_num,
                         sentence_split_len, gold_clauses, hint_range):
    """Fuzzy-locate the contiguous run of THIS pipeline's clauses (all in `chapter_num`) whose
    concatenated text best matches the gold scene's concatenated clause text.

    NOTE (diagnosed empirically): the `hint_range` (gold's own source_sentence_range) is NOT a
    reliable anchor here. This pipeline's sentence_split() regex splits on [.?!] and does not treat
    "Mr." / "Mrs." as a non-boundary abbreviation, so it over-splits every "Mrs. X" occurrence into
    two spurious sentences -- by chapter 16 this drift accumulates to ~40 sentences off the gold
    hint. Rather than trust the hint, this does a WHOLE-CHAPTER brute-force clause-window scan
    (bounded: only this chapter's clauses, window lengths sized off len(gold_clauses)) and reports
    the best-scoring window regardless of where it falls relative to the hint -- honest about the
    hint being unusable rather than silently anchoring to a wrong, hint-biased window.
    """
    gold_blob = " ".join(gold_clauses).lower()
    chapter_idxs = [i for i, c in enumerate(clause_chapter) if c == chapter_num]
    if not chapter_idxs:
        return None, -1.0
    n_gold = len(gold_clauses)
    best = None
    best_score = -1.0
    for wlen in range(max(1, n_gold - 2), n_gold + 16):
        for start in range(0, len(chapter_idxs) - wlen + 1):
            idxs = chapter_idxs[start:start + wlen]
            blob = " ".join(clauses_text[i] for i in idxs).lower()
            score = difflib.SequenceMatcher(None, gold_blob, blob).ratio()
            if score > best_score:
                best_score = score
                best = (idxs[0], idxs[-1])
    if best is None or best_score < 0.25:
        return None, best_score
    return best, best_score


def score_scene_against_gold(scene, stream, assigned, clauses_text, clause_chapter,
                              clause_sentence_idx, n_sentences_by_chapter):
    gold_stream = build_mention_stream(scene)
    chapter_num = scene["source_chapter"]
    window, sim = locate_scene_window(
        clauses_text, clause_chapter, clause_sentence_idx, chapter_num,
        n_sentences_by_chapter[chapter_num], scene["clauses"], tuple(scene["source_sentence_range"]))
    result = {
        "passage_id": scene["passage_id"], "window_located": window is not None,
        "window_similarity": round(sim, 4), "n_gold_mentions": len(gold_stream),
    }
    if window is None:
        result.update({"n_matched": 0, "n_consolidated_matched": 0, "n_false_consolidation": 0,
                        "unmatched_gold_mentions": [g["mention_text"] for g in gold_stream],
                        "disagreements": []})
        return result

    c_start, c_end = window
    scene_recs = [(rec, eid) for rec, eid in zip(stream, assigned)
                  if c_start <= rec["clause"] <= c_end]

    matches = []
    ptr = 0
    LOOKAHEAD = 20
    for g in gold_stream:
        g_is_pron = is_pronoun_mention(g["mention_text"])
        g_toks = _content_tokens(g["mention_text"])
        found = None
        for k in range(ptr, min(len(scene_recs), ptr + LOOKAHEAD)):
            rec, eid = scene_recs[k]
            if rec["is_pronoun"] != g_is_pron:
                continue
            if g_is_pron:
                if rec["mention_text"].lower() == g["mention_text"].lower().strip(".,'\"!?;:()"):
                    found = k
                    break
            else:
                r_toks = _content_tokens(rec["mention_text"])
                if r_toks and g_toks and (r_toks & g_toks):
                    found = k
                    break
        if found is not None:
            rec, eid = scene_recs[found]
            matches.append({"gold_entity": g["gold_entity"], "gold_mention": g["mention_text"],
                             "gold_role": g.get("role"), "reader_mention": rec["mention_text"],
                             "reader_eid": eid})
            ptr = found + 1

    consolidated = [m for m in matches if m["reader_eid"] is not None]
    by_eid = defaultdict(list)
    for m in consolidated:
        by_eid[m["reader_eid"]].append(m["gold_entity"])
    majority = {eid: Counter(names).most_common(1)[0][0] for eid, names in by_eid.items()}

    disagreements = []
    n_false = 0
    for m in consolidated:
        maj = majority[m["reader_eid"]]
        if m["gold_entity"] != maj:
            n_false += 1
            disagreements.append({
                "reader_eid": m["reader_eid"], "gold_mention": m["gold_mention"],
                "gold_entity_this_mention": m["gold_entity"],
                "reader_cluster_majority_gold_entity": maj,
            })

    matched_gold_texts = {m["gold_mention"] for m in matches}
    unmatched = [g["mention_text"] for g in gold_stream if g["mention_text"] not in matched_gold_texts]

    result.update({
        "n_matched": len(matches), "n_consolidated_matched": len(consolidated),
        "n_flagged_matched": len(matches) - len(consolidated),
        "n_false_consolidation": n_false,
        "false_consolidation_rate": (n_false / len(consolidated)) if consolidated else None,
        "unmatched_gold_mentions": unmatched,
        "disagreements": disagreements,
    })
    return result


def count_generic_np_referents(chapters):
    total = 0
    per_noun = Counter()
    for ch in chapters:
        for sent in v1.sentence_split(ch["text"]):
            for m in _GENERIC_NP_RE_SIMPLE.finditer(sent):
                total += 1
                per_noun[m.group(1).lower()] += 1
    return total, dict(per_noun)


def build_ledger_for_mode(mode, stream, clauses_text, clause_chapter, clause_sentence_idx,
                           n_sentences_by_chapter, chapters, gazetteer, n_pron, n_name, missed_caps,
                           n_gender_unknown_dropped, n_generic_np, generic_np_by_noun, gold_scenes):
    """Run resolve_honest(stream, pick_mode=mode) to completion + score vs gold + write
    mode-suffixed output files. Returns (ledger dict, ledger_rows, assigned) for the comparison pass."""
    assigned, ledger_rows = resolve_honest(stream, pick_mode=mode)

    n_force_attach_would_have_fired = sum(
        1 for row in ledger_rows if row["flagged"] == "unresolved_pronoun_no_compatible_candidate")
    n_low_confidence_ambiguous = sum(
        1 for row in ledger_rows if row["flagged"] == "low_confidence_ambiguous_pronoun")
    n_flagged_total = sum(1 for row in ledger_rows if row["flagged"] is not None)
    n_consolidated_mentions = sum(1 for row in ledger_rows if row["outcome"] == "CONSOLIDATED")

    per_entity_events, decode_check, decode_acc, n_skipped = \
        build_situation_model_consolidated_only(stream, assigned)

    # entity ledger (skip None).
    name_mentions_by_eid = defaultdict(Counter)
    mention_count_by_eid = Counter()
    clause_span_by_eid = defaultdict(list)
    for rec, eid in zip(stream, assigned):
        if eid is None:
            continue
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
            "eid": eid, "canonical_name_guess": canonical, "mention_count": mention_count_by_eid[eid],
            "n_distinct_name_forms": len(names), "first_clause": min(spans), "last_clause": max(spans),
            "consolidated": mention_count_by_eid[eid] >= 3,
            "event_trajectory": [
                {"clause": e["clause"], "role_bucket": e["role_bucket"], "mention_text": e["mention_text"]}
                for e in per_entity_events.get(eid, [])
            ],
        })
    entity_ledger.sort(key=lambda r: -r["mention_count"])

    scene_scores = []
    for scene in gold_scenes:
        if scene["source_chapter"] not in CHAPTERS_TO_READ:
            continue
        scene_scores.append(score_scene_against_gold(
            scene, stream, assigned, clauses_text, clause_chapter, clause_sentence_idx,
            n_sentences_by_chapter))

    total_consolidated_matched = sum(s["n_consolidated_matched"] for s in scene_scores)
    total_false = sum(s["n_false_consolidation"] for s in scene_scores)
    overall_false_rate = (total_false / total_consolidated_matched) if total_consolidated_matched else None

    # he/him/his binding: how many of those specific pronoun surfaces ended CONSOLIDATED vs flagged.
    he_him_rows = [row for row in ledger_rows if row["mention_text"].lower() in ("he", "him", "his")]
    he_him_bound = sum(1 for row in he_him_rows if row["outcome"] == "CONSOLIDATED")

    ledger = {
        "resolver_mode": mode,
        "chapters_read": [{"num": c["num"], "title": c["title"]} for c in chapters],
        "honesty_fix": {
            "description": "pronoun with 0 gn_compatible candidates: flagged UNRESOLVED, not bound "
                            "(was: force-attach to most-recent entity). Mode-native near-tie: also "
                            "flagged, not bound.",
            "pick_mode": mode,
            "confidence_margin_threshold": CONFIDENCE_MARGIN_THRESHOLD if mode == "salience" else None,
            "n_pronoun_mentions_total": n_pron,
            "n_force_attach_would_have_fired_under_baseline": n_force_attach_would_have_fired,
            "n_low_confidence_ambiguous_flagged": n_low_confidence_ambiguous,
            "n_flagged_total_all_mention_types": n_flagged_total,
            "n_consolidated_mentions": n_consolidated_mentions,
            "n_mentions_total": len(stream),
        },
        "extraction_description": {
            "gazetteer_size": len(gazetteer), "n_clauses_total": len(clauses_text),
            "n_mentions_total": len(stream), "n_pronoun_mentions": n_pron, "n_name_mentions": n_name,
            "gender_unknown_dropped_count": n_gender_unknown_dropped,
            "missed_capitalized_tokens_recurring": {k: v for k, v in missed_caps.items() if v >= 2},
            "generic_np_referent_count_closed_word_list": n_generic_np,
            "generic_np_referent_by_noun": generic_np_by_noun,
        },
        "consolidation": {
            "n_entities_tracked": len(entity_ledger),
            "n_consolidated_ge3_mentions": sum(1 for e in entity_ledger if e["consolidated"]),
            "n_singleton_1_mention": sum(1 for e in entity_ledger if e["mention_count"] == 1),
            "situation_model_decode_self_consistency": decode_acc,
            "n_mentions_skipped_from_situation_model_because_flagged": n_skipped,
        },
        "he_him_his_binding": {
            "n_he_him_his_mentions": len(he_him_rows),
            "n_bound_consolidated": he_him_bound,
            "n_flagged_unresolved": len(he_him_rows) - he_him_bound,
        },
        "false_consolidation_vs_gold": {
            "note": "gold_verified=false on all 6 scenes (pending Director spot-check); this rate "
                     "is PENDING, not certified.",
            "overall_false_consolidation_rate": overall_false_rate,
            "total_consolidated_matched_mentions": total_consolidated_matched,
            "total_false_consolidations": total_false,
            "per_scene": scene_scores,
        },
        "entities": entity_ledger,
        "mention_ledger_sample": ledger_rows[:80],
    }

    ledger_path = os.path.join(OUT_DIR, f"ledger_{mode}.json")
    tmp = ledger_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
    os.replace(tmp, ledger_path)

    full_rows_path = os.path.join(OUT_DIR, f"mention_ledger_full_{mode}.jsonl")
    tmp2 = full_rows_path + ".tmp"
    with open(tmp2, "w", encoding="utf-8") as f:
        for row in ledger_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(tmp2, full_rows_path)

    readable_path = os.path.join(OUT_DIR, f"ledger_readable_{mode}.txt")
    with open(readable_path, "w", encoding="utf-8") as f:
        f.write(f"HONEST CONSOLIDATION LEDGER (mode={mode}) -- Anne of Green Gables ch.6/9/16\n")
        f.write("=" * 60 + "\n\n")
        f.write(json.dumps({k: v for k, v in ledger.items()
                             if k not in ("entities", "mention_ledger_sample")}, indent=2) + "\n\n")
        f.write("TOP TRACKED ENTITIES:\n")
        for e in entity_ledger[:15]:
            f.write(f"  eid={e['eid']:>3}  {e['canonical_name_guess']:<20} "
                     f"mentions={e['mention_count']:<4} clauses[{e['first_clause']}-{e['last_clause']}] "
                     f"consolidated={e['consolidated']}\n")

    ledger["_paths"] = {"ledger_path": ledger_path, "readable_path": readable_path,
                         "full_rows_path": full_rows_path}
    return ledger, ledger_rows, assigned


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chapters = load_chapters_by_number(CHAPTERS_TO_READ)
    n_sentences_by_chapter = {ch["num"]: len(v1.sentence_split(ch["text"])) for ch in chapters}
    female_names = v1.load_female_names()
    gaz_candidates_raw, _, noninitial_count = v1.mine_gazetteer(chapters)
    gaz_admitted, gaz_rejected = v1.classify_gazetteer_candidates(chapters, gaz_candidates_raw)
    gazetteer = gaz_admitted | female_names
    # whole-corpus scope for the gender-cue dictionaries only (same precedent as female_names, itself
    # whole-corpus derived) -- extraction/resolution below stays scoped to the ch.6/9/16 read slice.
    all_chapters = load_all_chapters()
    surname_bigrams = build_surname_bigrams(all_chapters)
    # THE MASCULINE-GENDER FIX: guess_gender_v2 (direct title cue, then surname-bridge title cue)
    # replaces v1.guess_gender for pass-1 gender resolution.
    gender_of_pass1 = {n: guess_gender_v2(n, all_chapters, female_names, surname_bigrams)
                        for n in gazetteer}

    stream1, _, _, _, _ = extract_stream_with_sentence_idx(chapters, gazetteer, gender_of_pass1)
    assigned1 = run_match_or_allocate(stream1)  # baseline canonical resolver, pass-1 gender only
    gender_of, gender_backfilled = v1.infer_gender_from_pronoun_feedback(
        stream1, assigned1, gender_of_pass1)

    if gender_backfilled:
        stream2, _, _, _, _ = extract_stream_with_sentence_idx(chapters, gazetteer, gender_of)
    else:
        stream2 = stream1
    assigned2 = run_match_or_allocate(stream2)
    unresolved_mined = {t for t in gaz_admitted if gender_of.get(t) is None}
    if unresolved_mined:
        gazetteer = gazetteer - unresolved_mined
    (stream, clauses_text, clause_chapter, clause_sentence_idx, missed_caps
     ) = extract_stream_with_sentence_idx(chapters, gazetteer, gender_of)

    n_pron = sum(1 for r in stream if r["is_pronoun"])
    n_name = len(stream) - n_pron
    n_gender_unknown_dropped = len(unresolved_mined)
    n_generic_np, generic_np_by_noun = count_generic_np_referents(chapters)

    with open(GOLD_PATH, encoding="utf-8") as f:
        gold_scenes = [json.loads(line) for line in f if line.strip()]

    # THE RESOLVER-SWAP EXPERIMENT: run BOTH pick modes on the IDENTICAL stream (same extraction,
    # same gender resolution) so the delta isolates the resolver's effect. (resolve_honest's own
    # 0-compatible-candidate branch is mode-independent, so "would force-attach fire" is measured
    # directly off each mode's own ledger_rows -- no separate uninstrumented baseline resolver call
    # is needed here.)
    results = {}
    for mode in ("salience", "strict_cb"):
        ledger, ledger_rows, assigned = build_ledger_for_mode(
            mode, stream, clauses_text, clause_chapter, clause_sentence_idx, n_sentences_by_chapter,
            chapters, gazetteer, n_pron, n_name, missed_caps, n_gender_unknown_dropped, n_generic_np,
            generic_np_by_noun, gold_scenes)
        results[mode] = ledger

    # comparison: disagreements that flip between modes, PER-SCENE MULTISET diff (not a global text
    # set -- the same mention text, e.g. "she", recurs across scenes/positions, so a plain set would
    # silently collapse distinct occurrences and misreport the flip count; total_false counts above
    # are exact regardless, this is the human-readable "which specific disagreements changed" detail).
    def _scene_disagree_counter(ledger):
        by_scene = {}
        for s in ledger["false_consolidation_vs_gold"]["per_scene"]:
            by_scene[s["passage_id"]] = Counter(
                (d["gold_mention"], d["gold_entity_this_mention"]) for d in s["disagreements"])
        return by_scene

    sal_by_scene = _scene_disagree_counter(results["salience"])
    cb_by_scene = _scene_disagree_counter(results["strict_cb"])
    flipped_to_correct, newly_broken = [], []
    for pid in sorted(set(sal_by_scene) | set(cb_by_scene)):
        sal_c, cb_c = sal_by_scene.get(pid, Counter()), cb_by_scene.get(pid, Counter())
        for key, n in (sal_c - cb_c).items():
            flipped_to_correct.extend([f"{pid}:{key[0]}(was {key[1]})"] * n)
        for key, n in (cb_c - sal_c).items():
            newly_broken.extend([f"{pid}:{key[0]}(was {key[1]})"] * n)

    comparison = {
        "note": "before=salience (frequency-dominant Centering, hdlab.coreference_resolver."
                "run_match_or_allocate pick rule); after=strict_cb (literal-Centering "
                "most-recent-subject-clause pick, hdlab.coreference_resolver._pick_strict_cb). Both "
                "modes share the identical honesty fix, identical extraction stream, identical "
                "masculine-gender-fixed gender_of -- the ONLY variable is the pronoun pick rule.",
        "false_consolidation_rate": {
            "salience_before": results["salience"]["false_consolidation_vs_gold"][
                "overall_false_consolidation_rate"],
            "strict_cb_after": results["strict_cb"]["false_consolidation_vs_gold"][
                "overall_false_consolidation_rate"],
            "total_false_before": results["salience"]["false_consolidation_vs_gold"][
                "total_false_consolidations"],
            "total_false_after": results["strict_cb"]["false_consolidation_vs_gold"][
                "total_false_consolidations"],
            "total_consolidated_matched_before": results["salience"]["false_consolidation_vs_gold"][
                "total_consolidated_matched_mentions"],
            "total_consolidated_matched_after": results["strict_cb"]["false_consolidation_vs_gold"][
                "total_consolidated_matched_mentions"],
        },
        "disagreements_flipped_to_correct_under_strict_cb": flipped_to_correct,
        "disagreements_newly_broken_under_strict_cb": newly_broken,
        "he_him_his_binding": {
            "salience": results["salience"]["he_him_his_binding"],
            "strict_cb": results["strict_cb"]["he_him_his_binding"],
        },
        "consolidation_intact_check": {
            "salience": results["salience"]["consolidation"],
            "strict_cb": results["strict_cb"]["consolidation"],
        },
        "flag_pile_still_honest_check": {},  # filled below from the FULL per-mode mention ledger
    }

    # honest recompute of the it/its flag count from the FULL per-mode mention ledger (not the
    # 80-row sample) -- the flag-pile-still-honest check the task asks for.
    for mode in ("salience", "strict_cb"):
        full_path = results[mode]["_paths"]["full_rows_path"]
        with open(full_path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f]
        it_its_flagged = sum(1 for r in rows if r["mention_text"].lower() in ("it", "its")
                              and r["flagged"] == "unresolved_pronoun_no_compatible_candidate")
        comparison["flag_pile_still_honest_check"][mode] = {"it_its_flagged_count": it_its_flagged}

    comparison_path = os.path.join(OUT_DIR, "comparison_salience_vs_strict_cb.json")
    tmp = comparison_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    os.replace(tmp, comparison_path)

    print(json.dumps({
        "chapters_read": CHAPTERS_TO_READ,
        "n_clauses": len(clauses_text), "n_mentions": len(stream),
        "n_pronoun_mentions": n_pron, "n_name_mentions": n_name,
        "gender_unknown_dropped_count": n_gender_unknown_dropped,
        "generic_np_referent_count": n_generic_np,
        "false_consolidation_rate": comparison["false_consolidation_rate"],
        "he_him_his_binding": comparison["he_him_his_binding"],
        "disagreements_flipped_to_correct_under_strict_cb": flipped_to_correct,
        "disagreements_newly_broken_under_strict_cb": newly_broken,
        "flag_pile_still_honest_check": comparison["flag_pile_still_honest_check"],
        "salience_ledger_path": results["salience"]["_paths"]["ledger_path"],
        "strict_cb_ledger_path": results["strict_cb"]["_paths"]["ledger_path"],
        "comparison_path": comparison_path,
    }, indent=2))


if __name__ == "__main__":
    main()
