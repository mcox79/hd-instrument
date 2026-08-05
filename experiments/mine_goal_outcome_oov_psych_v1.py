"""mine_goal_outcome_oov_psych_v1 -- mine goal-owner items whose GOAL VERB is OOV to the production
frame table (hdlab.frame_induction.is_oov / hdlab.thematic_role_labeler.VERB_FRAMES), so the
OOV-psych frame-INDUCTION wire (commit 22b9b6f8e, hdlab/frame_induction.py) actually fires when
frame_primary_role is evaluated on these items. The existing bank (goal_outcome_c3mined_v1.jsonl,
mine_goal_outcome_litbank_c3syntax_v1.py) prefiltered on PSYCH_VERBS itself -- every goal verb in it
is IN-VOCAB by construction, so it cannot exercise the induction path at all.

WIRE-DON'T-ISLAND: reuses the c3-syntax owner resolver bit-identical (build_roster_c3,
c3_syntax_owner, CandidateGenerator persisted front-end, the passive/animacy/roster gates) from
mine_goal_outcome_litbank_c3syntax_v1.py, and the outcome-cue lexicon / sentence loader / diversity
selector from mine_goal_outcome_litbank_v1.py. The only NEW logic here is (a) the OOV-psych verb
target set replacing the PSYCH_VERBS prefilter, and (b) two mining-time fixes ordered by the
Director mid-task, driven by a parallel finding that the OLD bank's dominant failure mode was
narrow text windows where the resolved owner's NAME never appears in the item's own text (bare
pronoun "she cried" with the antecedent introduced outside the window) and unattributable quoted
dialogue outcomes:
  (b1) WIDE, SELF-CONTAINED WINDOW: track (sentence_idx, name) for every named roster mention seen
       so far. When the owner is resolved via pronoun, extend the item's text window BACKWARD to
       the sentence where that name was last mentioned (the antecedent), so the owner is NAMED and
       resolvable from the item's own text, not just from off-window global state. When the owner
       is resolved directly as a name in the goal sentence, no backward extension is needed. Items
       whose antecedent is too far back (> MAX_BACKWARD_SENT sentences) are dropped -- HONEST: wide
       is bounded, not unlimited context.
  (b2) NON-QUOTED OUTCOME: skip items whose outcome sentence contains a quotation mark. Dialogue
       lines are exactly the quote-fracture pathology (speaker outside window) the Director flagged
       on the parallel C-F cell; this bank should test ROLE TYPING on the OOV verb, not the
       segmentation bug.

Prior-work check (SUBSTRATE-KB, mandatory): `tools/substrate_query.sh` queried for "goal owner OOV
psych verb frame induction eval bank mining". Top hits at cosine>0.30: the two existing mining
cells (this file's direct ancestors, f2cb51d40 / fb5b2a188 lineage) and notes/WHERE_WE_ARE_NOW.md /
director_POST_COMPACTION_BACKUP (general project state, not this specific OOV-target approach) --
this is the explicitly-planned next probe of the OOV wire, not a rediscovery.

Writes incrementally (append+flush+fsync per item) to
experiments/data/goal_outcome_oov_psych_v1.jsonl.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "hdlab"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.frame_induction import is_oov  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.state_of_mind import PRONOUN_SCOPE, infer_nominal_gender  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402

# reuse bit-identical: sentence loading, outcome-cue lexicon, diversity selector, tokenizer.
from mine_goal_outcome_litbank_v1 import (  # noqa: E402
    LITBANK_DIR, load_sentences, mentions_in, ACHIEVE_CUES, BLOCK_CUES,
    select_diverse, _tokens,
)
# reuse bit-identical: roster-fix builder + c3-syntax owner resolver (POS/passive/animacy gates).
from mine_goal_outcome_litbank_c3syntax_v1 import (  # noqa: E402
    build_roster_c3, c3_syntax_owner, POS_PATH, ARC_PATH,
)

OUT_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_outcome_oov_psych_v1.jsonl")

# ============================================================== OOV-psych target verb inventory
# Broader psych/experiencer/desiderative lexicon MINUS hdlab.thematic_role_labeler.PSYCH_VERBS
# (the production in-vocab set). Every base form + every inflected surface form confirmed
# is_oov(lemma_verb(surface)) == True by the pipeline's own lemmatizer (see provenance note in the
# task report; lemma_verb is a crude suffix-stripper so some lemma keys are non-dictionary forms
# e.g. "despis", "crav" -- that is fine, it is the SAME lemma the production pipeline computes at
# mining time and at frame_primary_role time, so OOV status is internally consistent).
OOV_PSYCH_AVERSIVE = ["loathe", "despise", "abhor", "detest", "resent", "scorn", "disdain"]
OOV_PSYCH_POSITIVE = ["crave", "covet", "cherish", "treasure", "relish", "idolize", "worship",
                      "dote", "esteem"]
OOV_PSYCH_TARGETS = set(OOV_PSYCH_AVERSIVE) | set(OOV_PSYCH_POSITIVE)
_POLARITY = {v: "aversive_desire" for v in OOV_PSYCH_AVERSIVE}
_POLARITY.update({v: "positive_desire" for v in OOV_PSYCH_POSITIVE})

# lemma_verb output can differ from the dictionary base form (suffix-stripped); build the mapping
# base-form -> stripped-lemma once so the sentence scan can match on lemma_verb(token) directly.
_BASE_TO_LEMMA = {b: lemma_verb(b) for b in OOV_PSYCH_TARGETS}
_LEMMA_TO_BASE = {lm: b for b, lm in _BASE_TO_LEMMA.items()}
assert len(_LEMMA_TO_BASE) == len(OOV_PSYCH_TARGETS), "lemma collision across OOV target set"

MAX_NOVELS = 100
PER_NOVEL_CAP_SENTENCES = 60  # OOV-psych verbs are rarer surface-forms; wider per-novel prefilter
                              # budget than the in-vocab miner (18) since most raw hits will be
                              # noun-uses (POS-gated out downstream) or fail the new window/quote
                              # filters -- budget conservatively over-provisions candidates.
MAX_BACKWARD_SENT = 6  # cap on how far back the owner-name antecedent may sit; keeps windows wide
                        # but bounded (self-contained resolvability, not unlimited context growth).
MAX_SPAN_CHARS = 2200   # wider cap than the in-vocab bank's 900 (windows are intentionally wider).

_PRON_SCOPE_EXT = dict(PRONOUN_SCOPE)
_PRON_SCOPE_EXT.setdefault("herself", {"number": "singular", "gender": "fem"})
_PRON_SCOPE_EXT.setdefault("himself", {"number": "singular", "gender": "masc"})
_GENDER_MAP = {"masc": "m", "fem": "f"}


def _is_pron(token: str) -> bool:
    scope = _PRON_SCOPE_EXT.get(token.lower())
    return scope is not None and scope["gender"] in ("masc", "fem")


def _gender_of(token: str, roster_gender: dict):
    scope = _PRON_SCOPE_EXT.get(token.lower())
    if scope is not None:
        return _GENDER_MAP.get(scope["gender"])
    if token in roster_gender:
        return roster_gender[token]
    return _GENDER_MAP.get(infer_nominal_gender([token]))


def mine_novel(gen: CandidateGenerator, path: str, budget: list, roster_min_names: int = 3):
    novel = os.path.splitext(os.path.basename(path))[0]
    sentences = load_sentences(path)
    if len(sentences) < 50:
        return [], Counter()
    roster = build_roster_c3(sentences)
    if len(roster) < roster_min_names:
        return [], Counter()
    roster_gender = {}
    last_named = []       # list of names, most-recent-last (pronoun antecedent search order)
    last_named_idx = {}   # name -> most recent sentence idx it was named in (for window widening)
    items = []
    n = len(sentences)
    n_prefilter_stats = Counter()
    for i, sent in enumerate(sentences):
        if budget[0] <= 0:
            break
        goal_tok = None
        goal_lemma = None
        for t in _tokens(sent):
            lw = t.lower()
            lemma = lemma_verb(lw)
            if lemma in _LEMMA_TO_BASE:
                goal_tok, goal_lemma = lw, lemma
                break
        pre_mentions = mentions_in(sent, roster)
        if goal_tok is None:
            for m in pre_mentions:
                if m not in roster_gender:
                    roster_gender[m] = _GENDER_MAP.get(infer_nominal_gender([m]))
                if not last_named or last_named[-1] != m:
                    last_named.append(m)
                last_named_idx[m] = i
            continue
        budget[0] -= 1
        n_prefilter_stats["oov_psych_verb_prefiltered"] += 1
        for m in pre_mentions:
            if m not in roster_gender:
                roster_gender[m] = _GENDER_MAP.get(infer_nominal_gender([m]))
        # confirm the pipeline's own OOV predicate agrees before spending a candidate slot
        if not is_oov(goal_lemma):
            n_prefilter_stats["skip_lemma_not_actually_oov"] += 1
            continue
        owner, how, diag = c3_syntax_owner(gen, sent, goal_lemma, roster, roster_gender, last_named)
        for m in pre_mentions:
            if not last_named or last_named[-1] != m:
                last_named.append(m)
            last_named_idx[m] = i
        if owner is None:
            n_prefilter_stats["owner_unresolved_" + diag.get("failure_class", "?")] += 1
            continue

        # ---- (b1) WIDE SELF-CONTAINED WINDOW: locate the owner's most recent NAMED mention <= i.
        if how == "syntactic_subject_name":
            anchor_idx = i  # owner is named directly in the goal sentence itself
        else:  # syntactic_subject_pronoun_resolved
            anchor_idx = last_named_idx.get(owner)
            if anchor_idx is None or anchor_idx > i:
                n_prefilter_stats["skip_no_named_antecedent_idx"] += 1
                continue
        if i - anchor_idx > MAX_BACKWARD_SENT:
            n_prefilter_stats["skip_antecedent_too_far"] += 1
            continue
        window_start = min(anchor_idx, i)

        polarity = _POLARITY[goal_lemma]

        outcome_idx = None
        outcome_polarity = None
        between_mentions = []
        for j in range(i + 1, min(i + 8, n)):
            osent = sentences[j]
            otoks = {t.lower() for t in _tokens(osent)}
            hit_block = bool(otoks & BLOCK_CUES)
            hit_achieve = bool(otoks & ACHIEVE_CUES)
            for m in mentions_in(osent, roster):
                between_mentions.append((j, m))
            if hit_block or hit_achieve:
                outcome_idx = j
                outcome_polarity = ("blocked" if hit_block and not hit_achieve else
                                     ("achieved" if hit_achieve and not hit_block else "mixed"))
                break
        if outcome_idx is None:
            n_prefilter_stats["no_outcome_in_window"] += 1
            continue

        outcome_sent = sentences[outcome_idx]
        # ---- (b2) NON-QUOTED OUTCOME: drop quote-fracture-prone dialogue outcomes.
        if '"' in outcome_sent:
            n_prefilter_stats["skip_outcome_has_quote"] += 1
            continue

        dist = outcome_idx - i
        dist_bucket = "adjacent" if dist <= 1 else ("near" if dist <= 3 else "dispersed")
        foil = None
        for j, m in between_mentions:
            if m != owner:
                foil = m
        structure_type = f"{polarity}_{outcome_polarity}_{dist_bucket}_{'foil' if foil else 'nofoil'}"

        span_text = " ".join(sentences[window_start:outcome_idx + 1])
        if owner not in span_text:
            n_prefilter_stats["skip_owner_name_not_literally_in_window"] += 1
            continue
        if len(span_text) > MAX_SPAN_CHARS:
            n_prefilter_stats["skip_window_too_long"] += 1
            continue

        item_roster = {m: roster_gender.get(m) for m in set(
            m for j2, m in between_mentions) | {owner} | ({foil} if foil else set())
            if roster_gender.get(m) is not None}
        items.append(dict(
            id=f"oov_{novel}__s{i}",
            text=span_text,
            window_start_sentence_idx=window_start,
            window_backward_sentences=i - window_start,
            goal_sentence_idx=i,
            owner_named_antecedent_idx=anchor_idx,
            goal_owner=owner,
            owner_resolution=how,
            owner_diag=diag,
            goal_verb=goal_tok,
            goal_verb_lemma=goal_lemma,
            is_oov_goal_verb=True,
            outcome_span=outcome_sent[:400],
            outcome_polarity=outcome_polarity,
            foil=foil,
            source_novel=novel,
            structure_type=structure_type,
            goal_polarity=polarity,
            dist_sentences=dist,
            dist_bucket=dist_bucket,
            goal_sentence=sent[:300],
            roster=item_roster,
        ))
    return items, n_prefilter_stats


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    import time
    t0 = time.perf_counter()
    print(f"[mine-oov] loading persisted PosTagger+ArcParser front-end", flush=True)
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    paths = sorted(os.path.join(LITBANK_DIR, f) for f in os.listdir(LITBANK_DIR) if f.endswith(".txt"))
    novels_to_scan = paths[:MAX_NOVELS]
    print(f"[mine-oov] scanning {len(novels_to_scan)}/{len(paths)} novels, targets={sorted(OOV_PSYCH_TARGETS)}, "
          f"per-novel budget={PER_NOVEL_CAP_SENTENCES}", flush=True)

    all_items = []
    total_stats = Counter()
    for pi, path in enumerate(novels_to_scan):
        budget = [PER_NOVEL_CAP_SENTENCES]
        try:
            found, stats = mine_novel(gen, path, budget)
        except Exception as e:
            print(f"[mine-oov] SKIP {os.path.basename(path)}: {type(e).__name__}: {e}", flush=True)
            continue
        all_items.extend(found)
        total_stats.update(stats)
        if found:
            print(f"[mine-oov] [{pi+1}/{len(novels_to_scan)}] {os.path.basename(path)}: +{len(found)} "
                  f"items (total={len(all_items)}) elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    print(f"[mine-oov] RAW owner-resolved+window-clean items={len(all_items)} "
          f"prefilter_stats={dict(total_stats)} elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    selected = select_diverse(all_items, target_n=40, per_novel_cap=2)
    struct_counts = Counter(it["structure_type"] for it in selected)
    verb_counts = Counter(it["goal_verb_lemma"] for it in selected)
    print(f"[mine-oov] SELECTED n={len(selected)} structure_type={dict(struct_counts)} "
          f"verb_lemma={dict(verb_counts)}", flush=True)

    if os.path.exists(OUT_PATH):
        os.remove(OUT_PATH)
    with open(OUT_PATH, "a", encoding="utf-8", newline="") as f:
        for it in selected:
            f.write(json.dumps(it, ensure_ascii=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    print(f"[mine-oov] wrote {len(selected)} items to {OUT_PATH}", flush=True)
    return selected, dict(total_stats)


def self_test():
    """Deterministic in-process self-test: OOV predicate + window-widening logic on a tiny synthetic
    novel, reusing the REAL c3_syntax_owner/build_roster_c3 organs (same code path FULL uses)."""
    for base in OOV_PSYCH_TARGETS:
        lm = lemma_verb(base)
        assert is_oov(lm), f"target verb {base!r} (lemma {lm!r}) must be OOV to VERB_FRAMES"
    assert len(OOV_PSYCH_TARGETS & set()) == 0
    from hdlab.thematic_role_labeler import PSYCH_VERBS
    assert not (OOV_PSYCH_TARGETS & set(PSYCH_VERBS)), "target set must not overlap production PSYCH_VERBS"

    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    sents = [
        "In the old house lived Margaret quietly.",      # 0: names Margaret (antecedent, non-initial)
        "She rose early and walked in the garden.",      # 1: pronoun mention only
        "She despised her cousin's constant flattery.",  # 2: goal sentence, pronoun subject
        "Her cousin only flattered her more the next day.",  # 3
        "Everyone saw that Margaret failed to silence him.",  # 4: outcome (BLOCK_CUES 'fail')
    ]
    roster = build_roster_c3(sents * 3)  # build_roster_c3 needs freq>=3; replicate to satisfy it
    assert "Margaret" in roster, f"roster must admit Margaret: {roster}"
    roster_gender = {"Margaret": "f"}
    last_named = ["Margaret"]
    owner, how, diag = c3_syntax_owner(gen, sents[2], "despis", roster, roster_gender, last_named)
    assert owner == "Margaret", f"pronoun should resolve to named antecedent Margaret, got {owner!r}"
    assert how == "syntactic_subject_pronoun_resolved"
    print(f"[self-test] PASS: OOV predicate holds for all {len(OOV_PSYCH_TARGETS)} target verbs; "
          f"no overlap with PSYCH_VERBS; c3_syntax_owner resolves pronoun subject of an OOV-psych "
          f"verb to its named antecedent (owner={owner!r} how={how!r}).")
    return True


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        main()
