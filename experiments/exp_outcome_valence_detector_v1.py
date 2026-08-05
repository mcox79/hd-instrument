"""exp_outcome_valence_detector_v1 -- brain-faithful OUTCOME-VALENCE DETECTOR (2026-08-05).

Builds the missing upstream DETECTION stage for the goal-owner arc, per the design drill
notes/research_outcome_valence_detector_design_2026-08-05.md (commit 4f417f920). The 14/38
TYPING_MISS bottleneck (exp_c5_realtext_c3mined_v2_38item_v1, commit dfabbde26) is NOT a
lexicon-size problem: `directed_goal_outcome_score` / `GoalOutcomeRegister` (hdlab/
goal_owner_select.py) presuppose events are already role-typed; today typing IS the
ACHIEVE_CUES/BLOCK_CUES lexicon (mine_goal_outcome_litbank_v1). This cell replaces the OUTCOME
half of that typing stage with:
  (a) RELEVANCE gate: does a candidate sentence involve the goal's OBJECT/PREDICATE content?
      (goal-object head-noun/coref-normalized-token overlap for noun goals; verb-lemma-or-scoped-
      near-synonym match for embedded-clause goals ("wanted to see her" / "knew that..."))
  (b) VALENCE: small closed-class NEGATION-SCOPE check (~12 markers) within the matched clause,
      confirmed by a small closed-class RESULTATIVE-STATE-predicate presence check (~7 words,
      the highest-precision ACHIEVE/BLOCK members) as the state-change guard; ambiguous cases
      (relevance fires, no negation, no resultative confirmation) ABSTAIN and keep scanning the
      window (mirrors ContentMatchResolver's honest-abstain pattern already used in this arc).

WIRE-DON'T-ISLAND (reuse, not reimplemented):
  - hdlab.thematic_role_labeler.lemma_verb / PSYCH_VERBS -- verb lemmatization + the psych-verb
    frame class (subj=EXPERIENCER, obj=PATIENT) that already located these goal sentences.
  - hdlab.coreference_resolver.normalize_tokens -- the SAME stopword-filtered mention-comparison
    primitive the coref resolver uses internally for head-noun overlap; used here as the
    object-relevance anchor. (Full mention-stream entity tracking (build_mention_stream /
    TrackedEntity) requires a passage['entities'] schema the mined items do not carry -- roster
    is empty on 38/38 sampled items -- so full coref-chain identity is NOT wired this cell; this
    is an honest scope reduction from the design drill's "coref-chain-identical" framing to the
    coref module's actual reusable primitive, normalize_tokens set-overlap. Flagged, not hidden.)
  - exp_situation_model_goal_outcome_dimension_v1._sentences / _ordered_tokens -- same sentence
    splitter + tokenizer the rest of this arc's cells use (exp_c5_realtext_c3mined_v1 imports the
    same pair), so sentence indexing is consistent across the arc.
  - This detector feeds a (typed_role, predicted_polarity) pair in the SAME shape
    type_sentence_events_c3 emits (R_GOAL/R_UNMET/R_MET via directed_goal_outcome_score's own
    role vocabulary, imported not reimplemented) -- NOT wired into the live C5 pipeline in this
    cell (that is the follow-up IF this eval beats the lexicon; see module docstring bottom).

GOLD-LABEL SEMANTICS NOTE (discovered this cell, must be reported honestly): the mined
goal_outcome_c3mined_v1.jsonl's `outcome_polarity` field (achieved/blocked/mixed) is SURFACE
event polarity (which lexicon class -- ACHIEVE_CUES vs BLOCK_CUES -- fired in the outcome
sentence), computed independent of goal_polarity (see mine_goal_outcome_litbank_v1.mine_novel:
outcome_polarity is set from hit_block/hit_achieve alone). It is NOT goal-relative
satisfaction. This detector's negation-scope mechanism (Section 3(b) of the design drill) is
goal-relative (MET/UNMET via a goal_polarity flip) because that is the brain-faithful
state-match/state-mismatch computation (Zwaan & Radvansky). To compare against the gold field
honestly, `predicted_polarity` maps MET->"achieved", UNMET->"blocked" (a goal-relative-agnostic
final label), which is the natural interpretation but is NOT guaranteed to track the miner's
literal-word-class semantics on aversive-goal items (only 1/38 items here, so this note is a
scope caveat for future larger aversive-goal item banks, not a driver of this eval's numbers).

SCRAMBLE-ABLATION OPERATIONALIZATION (spec wording is ambiguous, decision made + documented):
the design drill's phrase "goal i's object paired with item i+1's candidate sentences" is
under-specified -- read maximally literally (scan item i+1's OWN candidate window) the ablation
is vacuous (item i's true outcome_span structurally cannot appear in item i+1's window, so BOTH
a genuine and a disguised-lexicon detector would collapse to ~0, telling us nothing). The
INFORMATIVE reading, consistent with the drill's own stated rationale ("a detector secretly
re-deriving the lexicon hit will show little accuracy drop... a genuinely directed detector
should collapse toward the resultative-state fallback alone" -- this sentence only makes sense
if the candidate window is UNCHANGED), is: keep item i's own candidate window + own gold, swap
ONLY the goal_object/predicate anchor for item (i+1 mod 38)'s goal content. Implemented that way
below (see `scrambled_goal_content` param), documented not silently reinterpreted.

Prior-work check (SUBSTRATE-KB, mandatory before authoring): `tools/substrate_query.sh
"outcome valence detector goal resolution negation scope polarity"` run this cell -- top hit
cosine=0.3496 `negation_polarity_cpu_v1` (HARD_PASS, signed/negated-FACT recall in an embedding
store, object-recall=1.0 polarity-recall=1.0) -- a DIFFERENT problem (fact-store negation
recall, not narrative goal-outcome valence detection); next hits are WordNet/FrameNet
"Negation"/"resolution" concept entries (cosine 0.335/0.3145), not prior cells. No prior-art
collision; this is genuinely new construction per the design drill's own capability-registry
grep (also reported there, re-confirmed here).

CONTRACT: glass-box, deterministic, self-test constructs the REAL detect_outcome() on 2 real
mined items (real code path). LOCAL-ONLY, no push, in-process foreground, atomic metrics write.
No bare except (outer try/except re-raises after CELL_CRASHED diagnostic, SystemExit/
KeyboardInterrupt preserved). MEASUREMENT cell (per design drill Section 4): small-N (38),
pre-registered bands reported but verdict is the measured number + band classification, not a
forced pass/fail on a sweep.
"""
from __future__ import annotations

import json
import os
import re
import sys
import traceback
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
from exp_situation_model_goal_outcome_dimension_v1 import _sentences, _ordered_tokens  # noqa: E402

ANCHOR_NAME = "outcome_valence_detector_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "metrics.json")
MINED_PATH = os.path.join(REPO_ROOT, "experiments", "data", "goal_outcome_c3mined_v1.jsonl")

LEXICON_TYPING_FIRE_RATE = 0.55  # MEASURED@data/exp_c5_realtext_c3mined_v2_38item_v1/metrics.json
                                  # (full_pipeline.typing_fire_rate), commit dfabbde26; the number
                                  # to beat per the design drill's pre-registered eval.

# ---------------------------------------------------------------------------------------------
# SUPPLIED closed classes (small, structural -- per design drill Section 3, "supplied vs earned")
# ---------------------------------------------------------------------------------------------
# ~12-item negation/failure-modal closed class (structural, not an open sentiment vocabulary).
NEGATION_MARKERS_SINGLE = {"not", "never", "no", "without", "nor", "neither", "cannot"}
NEGATION_MARKERS_MULTI = ["failed to", "unable to", "refused to", "could not", "did not"]
# (n't handled as a substring check on the raw clause -- contraction, not a separate word token)

# ~7-item resultative-state closed class (design drill's exact named example set -- the
# highest-precision ACHIEVE/BLOCK members, reused as a state-change CONFIRMATION signal only,
# not as their own polarity vote; see module docstring "GOLD-LABEL SEMANTICS NOTE").
RESULTATIVE_STATES = {"found", "lost", "gone", "returned", "dead", "free", "safe"}

# Small, PER-GOAL-VERB-SCOPED near-synonym sets (design drill: "escape ~ {flee, get_away,
# break_free} -- knowledge, not a general achieve/block list; scoped per-goal-verb, not
# corpus-wide"). Built from the goal_verb_lemma distribution actually present in the 38-item
# bank (see completion report) plus the drill's own escape example.
NEAR_SYNONYMS = {
    "see": {"saw", "spot", "spotted", "glimpse", "glimpsed", "observe", "observed", "meet", "met"},
    "know": {"learn", "learned", "learnt", "discover", "discovered", "realize", "realized",
             "understand", "understood"},
    "hear": {"heard", "overhear", "overheard", "learn", "learned"},
    "think": {"believe", "believed", "suppose", "supposed", "imagine", "imagined"},
    "feel": {"sense", "sensed", "perceive", "perceived"},
    "want": {"wish", "wished", "desire", "desired", "long", "longed"},
    "wonder": {"ask", "asked", "question", "questioned", "ponder", "pondered"},
    "like": {"enjoy", "enjoyed", "fond", "admire", "admired"},
    "dread": {"fear", "feared", "afraid"},
    "prefer": {"favor", "favored", "rather"},
    "trust": {"rely", "relied", "confide", "confided"},
    "consider": {"regard", "regarded", "deem", "deemed"},
    "remember": {"recall", "recalled", "recollect"},
    "suspect": {"doubt", "doubted", "distrust"},
    "mind": {"care", "cared", "object", "objected"},
    "escape": {"flee", "fled", "escaped"},
}

# Additional function-word/pronoun filter for object-extraction ONLY (structural closed class,
# NOT a sentiment lexicon -- WH-words/deictic-adverbs/bare-pronouns carry no identifiable
# head-noun content for the relevance anchor; coreference_resolver.STOPWORDS is deliberately
# tiny (articles/possessives only) so this cell adds its OWN scoped filter for this purpose).
_OBJ_FILLER = {"where", "when", "how", "why", "what", "who", "which", "now", "then", "here",
               "there", "and", "but", "or", "so", "very", "too", "again", "just", "still", "also"}
_OBJ_PRONOUNS = {"me", "you", "him", "her", "it", "them", "us", "himself", "herself", "itself",
                  "themselves", "one", "he", "she", "they", "i", "we"}


# ---------------------------------------------------------------------------------------------
# GOAL-CONTENT extraction (relevance anchor)
# ---------------------------------------------------------------------------------------------
def extract_goal_content(goal_sentence: str, goal_verb: str, goal_verb_lemma: str) -> dict:
    """Given the goal sentence + its psych-verb (surface + lemma, from C3's own PSYCH_VERBS
    prefilter that already located this sentence), extract the goal's OBJECT/STATE anchor:
    embedded-clause predicate ("wanted to see her" -> predicate 'see') or noun-object head
    tokens ("wanted the necklace" -> {'necklace'}). Returns {'kind': 'none'} if neither the
    verb nor any usable content can be located (honest abstain upstream).

    CLAUSE-BOUNDARY CLIPPING (structural, not new supplied knowledge): the object window is
    clipped at the first clause boundary (,;:) or coordinating conjunction (and/but/or/for/nor/
    so/yet) found in the RAW text after the verb, so a long 19th-c. compound sentence does not
    bleed the NEXT independent clause's content into the goal's own object anchor (measured
    this cell: without clipping, object_tokens were dominated by cross-clause noise on real
    prose -- e.g. 'Bingley...to see you; and I will send...' extracted {'will','send',...}
    instead of stopping at the semicolon)."""
    toks = _ordered_tokens(goal_sentence)
    gv = goal_verb.lower().strip(".,\"'();:")
    vi = None
    if gv in toks:
        vi = toks.index(gv)
    else:
        for idx, t in enumerate(toks):
            if lemma_verb(t) == goal_verb_lemma:
                vi = idx
                break
    if vi is None:
        return {"kind": "none"}

    window = toks[vi + 1: vi + 6]
    if window and window[0] == "to" and len(window) > 1:
        pred = window[1]
        return {"kind": "embedded", "predicate_lemma": lemma_verb(pred), "predicate_surface": pred}
    if "that" in window[:2]:
        ti = window.index("that")
        rest = window[ti + 1:]
        if rest:
            return {"kind": "embedded", "predicate_lemma": lemma_verb(rest[0]),
                    "predicate_surface": rest[0]}

    # Clause-boundary-aware object span: locate the verb's RAW-text position (word-boundary,
    # case-insensitive), take everything after it up to the first clause-boundary punctuation
    # or coordinating conjunction, THEN tokenize (preserves the boundary the punctuation-
    # stripped tokenizer above cannot see).
    m = re.search(r"\b" + re.escape(gv) + r"\b", goal_sentence, flags=re.IGNORECASE)
    if m:
        tail = goal_sentence[m.end():]
    else:
        tail = " ".join(toks[vi + 1:])
    boundary = re.search(r"[,;:]|\b(and|but|or|for|nor|so|yet)\b", tail, flags=re.IGNORECASE)
    clipped = tail[:boundary.start()] if boundary else tail
    obj_span = [t for t in _ordered_tokens(clipped) if t not in ("to", "that")][:8]
    obj_text = " ".join(obj_span)
    obj_tokens = normalize_tokens(obj_text) - _OBJ_FILLER - _OBJ_PRONOUNS
    if not obj_tokens:
        return {"kind": "none"}
    return {"kind": "object", "object_tokens": obj_tokens}


# ---------------------------------------------------------------------------------------------
# VALENCE (negation-scope) helpers
# ---------------------------------------------------------------------------------------------
def _clause_split(sentence: str):
    return [c.strip() for c in re.split(r"[,;]", sentence) if c.strip()]


def _negation_present(clause_text: str) -> bool:
    low = clause_text.lower()
    if "n't" in low:
        return True
    toks = set(_ordered_tokens(clause_text))
    if toks & NEGATION_MARKERS_SINGLE:
        return True
    for m in NEGATION_MARKERS_MULTI:
        if m in low:
            return True
    return False


def _resultative_present(clause_text: str) -> bool:
    toks = _ordered_tokens(clause_text)
    if set(toks) & RESULTATIVE_STATES:
        return True
    lemmas = {lemma_verb(t) for t in toks}
    return bool(lemmas & RESULTATIVE_STATES)


# ---------------------------------------------------------------------------------------------
# MAIN DETECTOR
# ---------------------------------------------------------------------------------------------
def detect_outcome(item: dict, goal_content_override: dict | None = None) -> dict:
    """Scan item['text']'s forward window (sentences after the goal sentence) for the FIRST
    relevance-passing, polarity-resolved candidate (Zwaan: readers resolve at first confirming/
    disconfirming evidence). `goal_content_override` is the scramble-ablation hook: substitute a
    DIFFERENT item's goal content while keeping this item's own candidate window + gold (see
    module docstring SCRAMBLE-ABLATION OPERATIONALIZATION)."""
    goal_content = goal_content_override if goal_content_override is not None else \
        extract_goal_content(item["goal_sentence"], item["goal_verb"], item["goal_verb_lemma"])
    sentences = _sentences(item["text"])
    if len(sentences) < 2 or goal_content["kind"] == "none":
        return dict(fired=False, picked_idx=None, picked_sentence=None,
                     reason="no_goal_content_or_no_candidates", goal_kind=goal_content["kind"])

    candidates = sentences[1:]
    goal_polarity = item["goal_polarity"]

    for ci, cand in enumerate(candidates):
        raw_toks = _ordered_tokens(cand)
        matched = False
        match_token = None
        if goal_content["kind"] == "embedded":
            target_lemma = goal_content["predicate_lemma"]
            syn_set = NEAR_SYNONYMS.get(target_lemma, set())
            for t in raw_toks:
                if lemma_verb(t) == target_lemma or t in syn_set or lemma_verb(t) in syn_set:
                    matched = True
                    match_token = t
                    break
        else:
            cand_tokens = normalize_tokens(cand)
            inter = goal_content["object_tokens"] & cand_tokens
            if inter:
                matched = True
                match_token = sorted(inter)[0]

        if not matched:
            continue

        clauses = _clause_split(cand)
        match_clause = cand
        for c in clauses:
            if match_token in _ordered_tokens(c):
                match_clause = c
                break

        neg = _negation_present(match_clause)
        resultative = _resultative_present(match_clause)
        if not neg and not resultative:
            continue  # honest abstain on this candidate; keep scanning window

        if goal_polarity == "positive_desire":
            role = "UNMET" if neg else "MET"
        else:  # aversive_desire
            role = "MET" if neg else "UNMET"
        predicted_polarity = "achieved" if role == "MET" else "blocked"

        return dict(fired=True, picked_idx=ci + 1, picked_sentence=cand, match_token=match_token,
                     negation_present=neg, resultative_present=resultative, role=role,
                     predicted_polarity=predicted_polarity, goal_kind=goal_content["kind"])

    return dict(fired=False, picked_idx=None, picked_sentence=None,
                reason="no_relevance_resolved_in_window", goal_kind=goal_content["kind"])


# ---------------------------------------------------------------------------------------------
# Eval plumbing
# ---------------------------------------------------------------------------------------------
def _norm_cmp(a: str, b: str) -> bool:
    """Robust sentence-equality for gold-index-free matching (handles the mining-vs-eval sentence
    splitter mismatch honestly rather than assuming index alignment)."""
    na = re.sub(r"[^a-z0-9 ]", "", (a or "").lower()).split()
    nb = re.sub(r"[^a-z0-9 ]", "", (b or "").lower()).split()
    return na == nb or (na and nb and (na == nb[:len(na)] or nb == na[:len(nb)]))


def _load_mined():
    items = []
    with open(MINED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def is_gold_lexically_reachable(item: dict) -> bool:
    """Would this item's OWN relevance test fire on its own gold outcome_span? Used to split
    the item bank into lexical-overlap vs paraphrase buckets (per design drill's named risk)."""
    goal_content = extract_goal_content(item["goal_sentence"], item["goal_verb"], item["goal_verb_lemma"])
    if goal_content["kind"] == "none":
        return False
    span_toks = _ordered_tokens(item["outcome_span"])
    if goal_content["kind"] == "embedded":
        target = goal_content["predicate_lemma"]
        syn_set = NEAR_SYNONYMS.get(target, set())
        return any(lemma_verb(t) == target or t in syn_set or lemma_verb(t) in syn_set for t in span_toks)
    span_tokens = normalize_tokens(item["outcome_span"])
    return bool(goal_content["object_tokens"] & span_tokens)


def self_test():
    """Pre-flight smoke: (1) real detect_outcome() on 2 real mined items (real code path, not
    synthetic-only); (2) embedded-goal relevance fires via near-synonym; (3) negation-scope flips
    polarity; (4) resultative fallback confirms a non-negated relevance hit."""
    mined = {it["id"]: it for it in _load_mined()}
    assert len(mined) == 38, f"expected 38 mined items, got {len(mined)}"

    # (1) real code path on 2 real items.
    it_a = mined["c3_1342_pride_and_prejudice__s30"]
    res_a = detect_outcome(it_a)
    assert "fired" in res_a, f"detect_outcome must return a fired field: {res_a}"
    it_b = mined["c3_113_the_secret_garden__s32"]
    res_b = detect_outcome(it_b)
    assert "fired" in res_b, f"detect_outcome must return a fired field: {res_b}"

    # (2) embedded-goal predicate + near-synonym relevance fire.
    gc = extract_goal_content("She wanted to escape the house", "wanted", "want")
    assert gc["kind"] == "embedded" and gc["predicate_lemma"] == "escape", \
        f"'wanted to escape' should extract the embedded predicate 'escape': {gc}"
    gc2 = extract_goal_content("She hoped to see him again", "hoped", "hope")
    assert gc2["kind"] == "embedded" and gc2["predicate_lemma"] == "see", f"embedded extraction failed: {gc2}"
    fake_item = dict(
        text="She hoped to see him again. Months later she glimpsed him and was found safe.",
        goal_sentence="She hoped to see him again", goal_verb="hoped", goal_verb_lemma="hope",
        goal_polarity="positive_desire")
    res_syn = detect_outcome(fake_item)
    assert res_syn["fired"] is True and res_syn["match_token"] == "glimpsed", \
        f"near-synonym relevance ('glimpsed' ~ 'see') must fire: {res_syn}"
    assert res_syn["predicted_polarity"] == "achieved", f"no-negation+resultative-confirmed should be " \
        f"achieved (positive_desire, no negation -> MET): {res_syn}"

    # (3) negation-scope flips polarity (positive_desire + negation -> blocked/UNMET).
    fake_item_neg = dict(
        text="She hoped to see him again. She never saw him and was left alone forever.",
        goal_sentence="She hoped to see him again", goal_verb="hoped", goal_verb_lemma="hope",
        goal_polarity="positive_desire")
    res_neg = detect_outcome(fake_item_neg)
    assert res_neg["fired"] is True and res_neg["negation_present"] is True, f"negation must fire: {res_neg}"
    assert res_neg["predicted_polarity"] == "blocked", f"negated relevance hit -> blocked/UNMET: {res_neg}"

    # (4) abstain: relevance fires, no negation, no resultative confirmation -> keep scanning
    # (verifies the mechanism does NOT force a call on every relevance hit).
    fake_item_abstain = dict(
        text="She hoped to see him again. She saw a bird flying overhead. Later she saw him and was found safe.",
        goal_sentence="She hoped to see him again", goal_verb="hoped", goal_verb_lemma="hope",
        goal_polarity="positive_desire")
    res_ab = detect_outcome(fake_item_abstain)
    assert res_ab["fired"] is True, f"third candidate (resultative-confirmed) must eventually fire: {res_ab}"
    assert res_ab["picked_idx"] == 2, f"first two relevance-firing-but-unconfirmed candidates must be " \
        f"skipped (abstain-and-continue), not force-called: {res_ab}"

    print(f"[SELFTEST PASS] real code path on 2 mined items (fired_a={res_a['fired']} "
          f"fired_b={res_b['fired']}); embedded/near-synonym relevance fires; negation-scope flips "
          f"polarity; abstain-and-continue verified (picked_idx={res_ab['picked_idx']} of 3 candidates).",
          flush=True)
    return True


def main():
    mined_list = _load_mined()
    mined = {it["id"]: it for it in mined_list}
    assert len(mined) == 38, f"expected 38 mined items on disk, got {len(mined)}"
    all_ids = list(mined.keys())
    n = len(all_ids)

    per_item = {}
    for mid in all_ids:
        item = mined[mid]
        res = detect_outcome(item)
        gold_span = item["outcome_span"]
        detection_correct = bool(res["fired"] and res["picked_sentence"] is not None and
                                  _norm_cmp(res["picked_sentence"], gold_span))
        lex_reachable = is_gold_lexically_reachable(item)
        per_item[mid] = dict(
            fired=res["fired"], picked_sentence=res.get("picked_sentence"),
            gold_outcome_span=gold_span, detection_correct=detection_correct,
            predicted_polarity=res.get("predicted_polarity"), gold_polarity=item["outcome_polarity"],
            valence_correct=(res.get("predicted_polarity") == item["outcome_polarity"]) if res["fired"] else None,
            lexical_overlap=lex_reachable, structure_type=item.get("structure_type"),
            goal_kind=res.get("goal_kind"),
        )
        print(f"[detect] {mid}: fired={res['fired']} detection_correct={detection_correct} "
              f"predicted_polarity={res.get('predicted_polarity')} gold={item['outcome_polarity']} "
              f"lexical_overlap={lex_reachable}", flush=True)

    n_fired = sum(1 for r in per_item.values() if r["fired"])
    n_detection_correct = sum(1 for r in per_item.values() if r["detection_correct"])
    detector_fire_rate = round(n_fired / n, 4)
    outcome_detection_accuracy = round(n_detection_correct / n, 4)

    fired_non_mixed = [r for r in per_item.values() if r["fired"] and r["gold_polarity"] != "mixed"]
    n_valence_correct = sum(1 for r in fired_non_mixed if r["valence_correct"])
    outcome_valence_accuracy = (round(n_valence_correct / len(fired_non_mixed), 4)
                                 if fired_non_mixed else None)
    n_fired_mixed_gold = sum(1 for r in per_item.values() if r["fired"] and r["gold_polarity"] == "mixed")

    # --- non-vacuousness scramble ablation ---
    scramble_correct = 0
    for i, mid in enumerate(all_ids):
        item = mined[mid]
        other = mined[all_ids[(i + 1) % n]]
        scrambled_content = extract_goal_content(other["goal_sentence"], other["goal_verb"],
                                                   other["goal_verb_lemma"])
        res_s = detect_outcome(item, goal_content_override=scrambled_content)
        if res_s["fired"] and res_s["picked_sentence"] is not None and \
                _norm_cmp(res_s["picked_sentence"], item["outcome_span"]):
            scramble_correct += 1
    scramble_detection_accuracy = round(scramble_correct / n, 4)
    scramble_ablation_drop = round(outcome_detection_accuracy - scramble_detection_accuracy, 4)

    # --- paraphrase split ---
    lex_items = [r for r in per_item.values() if r["lexical_overlap"]]
    par_items = [r for r in per_item.values() if not r["lexical_overlap"]]
    lex_acc = (round(sum(1 for r in lex_items if r["detection_correct"]) / len(lex_items), 4)
               if lex_items else None)
    par_acc = (round(sum(1 for r in par_items if r["detection_correct"]) / len(par_items), 4)
               if par_items else None)

    # --- bands (per design drill Section 4, pre-registered before running) ---
    hard_pass = (outcome_detection_accuracy >= 0.55 and
                 (outcome_valence_accuracy is not None and outcome_valence_accuracy >= 0.65) and
                 scramble_ablation_drop >= 0.20)
    hard_fail = (outcome_detection_accuracy < 0.35 or scramble_ablation_drop < 0.05 or
                 detector_fire_rate < 0.30)
    if hard_pass:
        band = "HARD_PASS"
    elif hard_fail:
        band = "HARD_FAIL"
    else:
        band = "MIDDLE_BAND"

    verdict_msg = (
        f"{band} (measurement, N=38): detection_acc={outcome_detection_accuracy} "
        f"(vs lexicon fire-rate floor {LEXICON_TYPING_FIRE_RATE}) "
        f"valence_acc={outcome_valence_accuracy} (n={len(fired_non_mixed)}, mixed-gold-fired={n_fired_mixed_gold}) "
        f"detector_fire_rate={detector_fire_rate} "
        f"scramble_ablation_drop={scramble_ablation_drop} "
        f"(base={outcome_detection_accuracy} scrambled={scramble_detection_accuracy}) "
        f"paraphrase_split: lexical_overlap_acc={lex_acc}(n={len(lex_items)}) "
        f"paraphrase_acc={par_acc}(n={len(par_items)})"
    )

    metrics = dict(
        anchor_name=ANCHOR_NAME,
        verdict=band,
        verdict_msg=verdict_msg,
        summary=verdict_msg,
        n_items=n,
        n_fired=n_fired,
        detector_fire_rate=detector_fire_rate,
        outcome_detection_accuracy=outcome_detection_accuracy,
        outcome_valence_accuracy=outcome_valence_accuracy,
        n_valence_eligible=len(fired_non_mixed),
        n_fired_mixed_gold=n_fired_mixed_gold,
        scramble_detection_accuracy=scramble_detection_accuracy,
        scramble_ablation_drop=scramble_ablation_drop,
        paraphrase_split=dict(
            lexical_overlap_n=len(lex_items), lexical_overlap_acc=lex_acc,
            paraphrase_n=len(par_items), paraphrase_acc=par_acc,
        ),
        lexicon_typing_fire_rate_baseline=LEXICON_TYPING_FIRE_RATE,
        bands=dict(hard_pass_detection=">=0.55", hard_pass_valence=">=0.65",
                   hard_pass_scramble_drop=">=0.20", hard_fail_detection="<0.35",
                   hard_fail_scramble_drop="<0.05", hard_fail_fire_rate="<0.30"),
        per_item=per_item,
        elapsed_s=0.0,
        ts_iso=datetime.now(timezone.utc).isoformat(),
        source_mined_path=MINED_PATH,
        prereg_note="MEASUREMENT cell per design drill Section 4 (notes/research_outcome_"
                     "valence_detector_design_2026-08-05.md); small-N(38) directional bands, "
                     "not a forced sweep pass/fail.",
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = OUTPUT_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, OUTPUT_PATH)
    print(f"[VERDICT] {verdict_msg}", flush=True)
    return metrics


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    try:
        if args.self_test:
            raise SystemExit(0 if self_test() else 1)
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        tmp = OUTPUT_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            json.dump(dict(
                verdict="CELL_CRASHED", verdict_msg=f"{type(e).__name__}: {str(e)[:500]}",
                summary=f"CELL_CRASHED: {type(e).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(),
                anchor_name=ANCHOR_NAME,
            ), f, indent=2)
        os.replace(tmp, OUTPUT_PATH)
        raise
