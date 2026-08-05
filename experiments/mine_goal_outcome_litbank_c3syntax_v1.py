"""mine_goal_outcome_litbank_c3syntax_v1 -- re-mine litbank goal->outcome items using COMPONENT-3's
SYNTAX (PosTagger+ArcParser candidate generation + frame-primary role) for owner-ID, replacing the
NO-SYNTAX surface miner (mine_goal_outcome_litbank_v1.py, commit f2cb51d40) that got 22.5% owner-
label accuracy because it grabbed the first roster proper-noun/pronoun in the sentence -- no check
that the candidate was syntactically the psych verb's SUBJECT, no POS gate against nominal/
adjectival lemma false-fires (e.g. "love" as a noun, "wanting" mistagged).

WIRE-DON'T-ISLAND: reuses hdlab/candidate_generator.py (PosTagger+ArcParser persisted front-end,
CandidateGenerator.generate -> candidates_from_parse) exactly as the existing production consumer
experiments/exp_frame_primary_role_assigner_endtoend_v1.py does to resolve slot=subj/obj (arg_idx
< v_idx -> subj slot; see that file's _resolve_real_parse, reused pattern here): a candidate
(verb_idx, arg_idx) pair is only trusted as SUBJECT if (a) the arc parser's own structure licenses
it (candidates_from_parse), (b) it sits BEFORE the verb, (c) the verb token itself POS-tags as VERB
(gates the adjectival/nominal-lemma false-fire the surface miner had no defense against).

PSYCH-VERB PREFILTER: hdlab/thematic_role_labeler.py PSYCH_VERBS (frame subj=EXPERIENCER in
VERB_FRAMES) -- lemma_verb() surface->lemma match, broader + more principled than the surface
miner's hand-typed inflection table (catches "desired/craved/dreaded/feared/hated/yearned" etc via
the shared irregular-table+suffix-strip lemmatizer, not a hardcoded surface list).

OUTCOME TYPING (mining/candidate-identification only, unchanged from the surface miner): the broad
ACHIEVE_CUES/BLOCK_CUES lexicon (mine_goal_outcome_litbank_v1.py) -- general achieve/block cues for
real 19th-c. prose, reused bit-identical; NOT the authored-template-tuned V2_OUTCOME_MET/UNMET
lexicon (exp_self_extension_grounded_realprose_v1) that exp_component5_gold_role_isolated_v1's
type_sentence_events uses downstream for the C5 SELECTION stage -- that is a SEPARATE, later gate
(see run_c5_stage below) and is deliberately not conflated with mining/candidate-ID here.

Prior-work check (SUBSTRATE-KB, mandatory): `tools/substrate_query.sh` queried for "goal owner
selection coherence binding recency outcome real text mining syntax subject". Top hits at
cosine>0.30: notes/WHERE_WE_ARE_NOW.md, notes/director_POST_COMPACTION_BACKUP_2026-08-04.md (both
general project-state docs, not this specific mining approach), and the two mining/C5 cells cited
above (f2cb51d40, fb5b2a188 lineage) -- this cell is the explicitly-planned NEXT STEP named in
commit 2cb05bfce's own finding ("goal-owner ID needs syntax=C3, miner islanded a bad extractor"),
not a rediscovery.

Writes incrementally (append+flush+fsync per item) to experiments/data/goal_outcome_c3mined_v1.jsonl.
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

from hdlab.thematic_role_labeler import PSYCH_VERBS, lemma_verb  # noqa: E402
from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.state_of_mind import PRONOUN_SCOPE, infer_nominal_gender  # noqa: E402

# reuse bit-identical: sentence loading, roster-building, outcome-cue lexicon, diversity selection
from mine_goal_outcome_litbank_v1 import (  # noqa: E402
    LITBANK_DIR, load_sentences, build_roster, mentions_in, ACHIEVE_CUES, BLOCK_CUES,
    select_diverse, _tokens,
)

OUT_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_outcome_c3mined_v1.jsonl")
POS_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_PATH = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")

MAX_PREFILTERED_SENTENCES = 450  # bound per task brief ("if too slow, bound it") -- PER-NOVEL cap
MAX_NOVELS = 100  # spread the sentence budget across many novels for structural/source diversity
PER_NOVEL_CAP_SENTENCES = 18  # per-novel prefiltered-sentence budget (keeps any one long novel from
                              # eating the whole global budget, per finding: novel #1 alone consumed
                              # the entire original 450-budget with zero source diversity)

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


def c3_syntax_owner(gen: CandidateGenerator, sentence: str, verb_lemma: str, roster: set,
                     roster_gender: dict, last_named: list):
    """Return (owner_or_None, resolution_tag, diag_dict). Uses the REAL persisted parse: verb
    token must POS-tag VERB and lemma-match; subject candidate must be a parser-licensed
    (verb,arg) pair strictly before the verb (subj slot per candidates_from_parse convention,
    same convention exp_frame_primary_role_assigner_endtoend_v1._resolve_real_parse uses)."""
    cr = gen.generate(sentence)
    toks, pos = cr.tokens, cr.pos
    v_idx0 = None
    for i, t in enumerate(toks):
        if pos[i] == "VERB" and lemma_verb(t) == verb_lemma:
            v_idx0 = i
            break
    if v_idx0 is None:
        return None, None, {"failure_class": "VERB_NOT_POS_VERB_OR_NOT_LOCATED"}
    v1 = v_idx0 + 1
    subj_cands = [a for (vv, a) in cr.candidates if vv == v1 and a < v1]
    if not subj_cands:
        return None, None, {"failure_class": "NO_PARSER_LICENSED_SUBJ_CANDIDATE"}
    ranked = sorted(subj_cands, key=lambda a: (cr.cand_rules.get((v1, a)) != "core_dep", -a))
    a_idx0 = ranked[0] - 1
    tok = toks[a_idx0]
    ptag = pos[a_idx0]
    diag = {"v_idx0": v_idx0, "a_idx0": a_idx0, "a_pos": ptag, "a_tok": tok,
            "cand_rule": cr.cand_rules.get((v1, ranked[0])), "n_subj_cands": len(subj_cands)}
    if ptag in ("PROPN", "NOUN") and tok in roster:
        return tok, "syntactic_subject_name", diag
    if _is_pron(tok):
        want = _gender_of(tok, roster_gender)
        for e in reversed(last_named):
            if _gender_of(e, roster_gender) == want:
                return e, "syntactic_subject_pronoun_resolved", diag
        return None, None, {**diag, "failure_class": "PRONOUN_NO_GENDER_COMPATIBLE_ANTECEDENT"}
    return None, None, {**diag, "failure_class": "SUBJ_TOKEN_NOT_ROSTER_NAME_OR_PRONOUN"}


def mine_novel(gen: CandidateGenerator, path: str, budget: list, roster_min_names: int = 3):
    novel = os.path.splitext(os.path.basename(path))[0]
    sentences = load_sentences(path)
    if len(sentences) < 50:
        return []
    roster = build_roster(sentences)
    if len(roster) < roster_min_names:
        return []
    roster_gender = {}  # populate lazily via infer_nominal_gender per name below
    last_named = []
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
            if lemma in PSYCH_VERBS:
                goal_tok, goal_lemma = lw, lemma
                break
        # update roster mention trail BEFORE resolving this sentence's owner (unchanged causal order)
        pre_mentions = mentions_in(sent, roster)
        if goal_tok is None:
            for m in pre_mentions:
                if m not in roster_gender:
                    roster_gender[m] = _GENDER_MAP.get(infer_nominal_gender([m]))
                if not last_named or last_named[-1] != m:
                    last_named.append(m)
            continue
        budget[0] -= 1
        n_prefilter_stats["psych_verb_prefiltered"] += 1
        for m in pre_mentions:
            if m not in roster_gender:
                roster_gender[m] = _GENDER_MAP.get(infer_nominal_gender([m]))
        owner, how, diag = c3_syntax_owner(gen, sent, goal_lemma, roster, roster_gender, last_named)
        for m in pre_mentions:
            if not last_named or last_named[-1] != m:
                last_named.append(m)
        if owner is None:
            n_prefilter_stats["owner_unresolved_" + diag.get("failure_class", "?")] += 1
            continue
        polarity = "aversive_desire" if goal_lemma in ("fear", "dread", "hate", "dislike") else "positive_desire"

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

        dist = outcome_idx - i
        dist_bucket = "adjacent" if dist <= 1 else ("near" if dist <= 3 else "dispersed")
        foil = None
        for j, m in between_mentions:
            if m != owner:
                foil = m
        structure_type = f"{polarity}_{outcome_polarity}_{dist_bucket}_{'foil' if foil else 'nofoil'}"

        span_text = " ".join(sentences[i:outcome_idx + 1])
        item_roster = {m: roster_gender.get(m) for m in set(
            m for j2, m in between_mentions) | {owner} | ({foil} if foil else set())
            if roster_gender.get(m) is not None}
        items.append(dict(
            id=f"c3_{novel}__s{i}",
            text=span_text[:900],
            goal_owner=owner,
            owner_resolution=how,
            owner_diag=diag,
            goal_verb=goal_tok,
            goal_verb_lemma=goal_lemma,
            outcome_span=sentences[outcome_idx][:400],
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
    print(f"[mine-c3] loading persisted PosTagger+ArcParser front-end", flush=True)
    gen = CandidateGenerator.load(POS_PATH, ARC_PATH)
    paths = sorted(os.path.join(LITBANK_DIR, f) for f in os.listdir(LITBANK_DIR) if f.endswith(".txt"))
    novels_to_scan = paths[:MAX_NOVELS]
    print(f"[mine-c3] scanning {len(novels_to_scan)}/{len(paths)} novels, per-novel budget="
          f"{PER_NOVEL_CAP_SENTENCES} psych-verb-prefiltered sentences", flush=True)

    all_items = []
    total_stats = Counter()
    for pi, path in enumerate(novels_to_scan):
        budget = [PER_NOVEL_CAP_SENTENCES]
        try:
            found, stats = mine_novel(gen, path, budget)
        except Exception as e:
            print(f"[mine-c3] SKIP {os.path.basename(path)}: {type(e).__name__}: {e}", flush=True)
            continue
        all_items.extend(found)
        total_stats.update(stats)
        print(f"[mine-c3] [{pi+1}/{len(novels_to_scan)}] {os.path.basename(path)}: +{len(found)} "
              f"items (total={len(all_items)}) elapsed={time.perf_counter()-t0:.1f}s", flush=True)

    n_with_foil = sum(1 for it in all_items if it["foil"] is not None)
    print(f"[mine-c3] RAW owner-resolved items={len(all_items)} with_foil={n_with_foil} "
          f"prefilter_stats={dict(total_stats)}", flush=True)

    selected = select_diverse(all_items, target_n=40, per_novel_cap=2)
    struct_counts = Counter(it["structure_type"] for it in selected)
    print(f"[mine-c3] SELECTED n={len(selected)} structure_type breakdown={dict(struct_counts)}",
          flush=True)

    if os.path.exists(OUT_PATH):
        os.remove(OUT_PATH)
    with open(OUT_PATH, "a", encoding="utf-8", newline="") as f:
        for it in selected:
            f.write(json.dumps(it, ensure_ascii=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
    print(f"[mine-c3] wrote {len(selected)} items to {OUT_PATH}", flush=True)
    return selected, dict(total_stats)


if __name__ == "__main__":
    main()
