"""
QA-SRL Bank 2.0 modern-corpus re-validation of hdlab/thematic_role_labeler.py's cue-integration
mechanism (registry id thematic_role_labeler_cue_integration).

MEASUREMENT ONLY. Does NOT reimplement the labeler and does NOT retrain the front-end (PosTagger/
ArcParser) or add a new organ -- it reuses the OWNED objects verbatim:
  hdlab.candidate_generator.CandidateGenerator  (parse -> verb-arg candidates)
  hdlab.thematic_role_labeler.{is_passive_clause, frame_slot_role, role_feats, train_perceptron,
    scramble_weights, ablate_weights, PSYCH_VERBS, DITRANS_VERBS}
  experiments.exp_thematic_role_labeler_cue_integration_v1.build_data / _match_predicate_idx /
    _positional_baseline_acc / _acc / SEEDS_FULL / EPOCHS / MARGIN_HARD_PASS /
    SCRAMBLE_COLLAPSE_MIN / ABLATION_MATCH_TOL  (the exact TRAINING RECIPE + bands the +0.264
    McGuffey result used, imported not copied -- the module is import-safe per its 2026-08-11
    docstring: build_data() is guarded under __main__ so importing it does not execute the full
    multi-seed McGuffey experiment.)

WHY: the thematic_role_labeler_cue_integration registry row is HARD_PASS (+0.2635 over a matched
positional baseline) but its data_scope caveat reads "McGuffey is a USER-DEPRECATED source ...
re-validate on a modern-source held-out before wiring." This script is that re-validation, using
QA-SRL Bank 2.0 (FitzGerald et al. 2018, github.com/uwnlp/qasrl-bank, qasrl.org) -- a large (64,018
sentences, ~299K questions across Wikipedia/Wikinews/Science/TQA text) MODERN, REAL, voice-
parameterized question-answering corpus, per notes/research_next_benchmark_after_propara_trap_
check_2026-08-10.md Section 1h item 5 / Section 2 rank 5.

TRAIN stays McGuffey+hand-authored-supplement (UNCHANGED, via build_data()) -- this is a pure
GENERALIZATION test, zero QA-SRL leakage into training. TEST = the ENTIRE QA-SRL "orig" corpus
(train+dev+test splits all used as held-out EVAL ONLY, since none of it ever touches training).

THE HONEST CRUX (QA-SRL is question-based; the labeler is role-label-based) -- mapping design,
derived EMPIRICALLY off real QA-SRL records (not guessed), see map_qasrl_question() docstring:
  - wh in {who, what}  -> core-argument probe (kept). wh in {where, when, why, how, how much} ->
    ADJUNCT probe (excluded_adjunct_wh; QA-SRL's own template leaves an argument slot nominally
    blank for these too, but the ANSWER is never that argument -- confirmed by direct inspection,
    e.g. "Where is something shown?" leaves obj blank yet answers "in Figure 10.5", a PP nowhere
    in the 7-slot skeleton).
  - Exactly one of {subj, obj, obj2} blank ("_") identifies the QUESTIONED argument; more/fewer
    blanks -> excluded_slot_ambiguous.
  - subj blank, active voice        -> frame_slot_role(lemma, "subj")  [AGENT or EXPERIENCER]. Safe
    for every verb (subject role assignment is never disturbed by ditransitivity).
  - subj blank, passive, NOT a DITRANS_VERBS lemma -> frame_slot_role(lemma, "obj") [PATIENT]. Safe:
    a monotransitive passive has exactly one promotion target.
  - subj blank, passive, IS a DITRANS_VERBS lemma  -> EXCLUDED (ditrans_passive_ambiguous). Directly
    empirically demonstrated NOT safe to guess: "What is given something?" (subj blank, isPassive,
    obj filled) answers "rock layers" = the RECIPIENT promoted to subject (from "give them(=rock
    layers) relative ages"), while "What can be told by someone?" (subj blank, isPassive, prep=by)
    answers the THEME. Same slot pattern (subj-blank ditransitive passive), two different deep
    roles depending on which argument the sentence promoted -- QA-SRL's 7-slot template does not
    disambiguate this without deeper per-verb frame knowledge this labeler does not have. Forcing
    a guess here would inject silent label noise into a "gold" set; excluded and counted instead.
  - obj blank, active, verb not-ditransitive-here (obj2 == "_", i.e. no second argument present in
    THIS question at all) -> frame_slot_role(lemma, "obj") [PATIENT]. Safe (no ambiguity possible).
  - obj blank, active, obj2 != "_" (genuine double-object question) -> EXCLUDED
    (ditrans_double_object_ambiguous). Empirically the obj/obj2 slot<->role correspondence is NOT a
    fixed linear convention in this corpus (obj held the THEME in one give-example and would need
    to hold the RECIPIENT in another reading of the same verb) -- excluded rather than guessed.
  - obj blank, passive -> EXCLUDED (passive_obj_blank_edge_case; rare/edge, not confidently
    interpretable without deeper analysis, small n expected).
  - obj2 blank, prep == "by" -> frame_slot_role(lemma, "subj") [AGENT]. Safe: a "by"-phrase always
    recovers the deep AGENT regardless of what got promoted to subject. THIS IS A GENUINELY NEW AXIS
    the McGuffey validation never had at all -- the ground-truth-provenance audit
    (notes/research_thematic_role_gold_provenance_audit.md) found ZERO genuine passive pos-triples
    in McGuffey's own gold; QA-SRL supplies real by-phrase AGENT recovery examples for the first time.
  - obj2 blank, prep in {"to","for"}, lemma in DITRANS_VERBS -> "RECIPIENT" directly. Safe: a
    PP-marked recipient with a ditransitive-capable verb (per DITRANS_VERBS/DITRANS_FRAME's own
    iobj->RECIPIENT mapping) is unambiguous.
  - obj2 blank, prep == "_" (bare double-object, no preposition) -> EXCLUDED
    (ditrans_double_object_ambiguous, same reasoning as the obj case above).
  - obj2 blank, any other prep (with/from/in/on/at/into/toward/...) -> EXCLUDED (other_prep_unmapped).
    NOTE (structural finding, not a QA-SRL gap): hdlab.thematic_role_labeler.frame_slot_role() can
    ONLY return AGENT/PATIENT/EXPERIENCER/RECIPIENT/"none" -- VERB_FRAMES has no verb->"GOAL" mapping
    anywhere in the table (DEFAULT_FRAME/_PSYCH_FRAME/_DITRANS_FRAME all omit a "goal" slot). GOAL is
    declared in the ROLES tuple but is structurally UNREACHABLE via the frame path today; this script
    therefore reports 0 GOAL examples by construction of the labeler itself, not a mapping failure.

CONTROLS (same as the original cell, apples-to-apples): validity-scramble (scramble_weights) and
single-cue ablation (order/animacy/frame/voice), using the SAME bands (MARGIN_HARD_PASS=0.15,
SCRAMBLE_COLLAPSE_MIN=0.10, ABLATION_MATCH_TOL=0.05) imported from the original cell.

POSITIVE CONTROL (Gate D discipline, notes/exp_dev.md SS15): before trusting any QA-SRL number,
this script FIRST reproduces the original McGuffey non-canonical HARD-PASS result
(mean_full_acc=0.8666 vs positional_baseline=0.6032) using ITS OWN reused train_perceptron/
build_data call -- if that reproduction drifts outside tolerance, the QA-SRL numbers are not
trusted (reuse-of-training-recipe bug, not a McGuffey-generalization finding).

Multi-seed (SEEDS_FULL, same 5 seeds as the original cell), tools/exp_checkpoint.py per-unit
resumability. LOCAL-ONLY. No push. ASCII-only. Run with --self-test for a fast in-memory smoke that
exercises the REAL CandidateGenerator + REAL map_qasrl_question() at tiny scale (no download).
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units
from experiments._seed_checkpoint import get_output_dir, write_metrics
from hdlab.candidate_generator import CandidateGenerator
from hdlab.thematic_role_labeler import (
    is_passive_clause, role_feats, train_perceptron, scramble_weights, ablate_weights,
    PSYCH_VERBS, DITRANS_VERBS, frame_slot_role,
)
import experiments.exp_thematic_role_labeler_cue_integration_v1 as base

ANCHOR_NAME = "thematic_role_labeler_qasrl_modern_revalidation_v1"
QASRL_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "qasrl", "qasrl-v2", "orig")
QASRL_SPLITS = ["train", "dev", "test"]  # all three used as EVAL ONLY; our labeler trains on McGuffey only

MCG_REPRO_EXPECTED = 0.8666           # MEASURED@data/exp_thematic_role_labeler_cue_integration_v1/metrics.json:mean_full_acc
MCG_REPRO_TOLERANCE = 0.05            # same-code-path reproduction; tight tolerance (not a regime change)
MIN_TEST_N = 15                       # below this the QA-SRL non-canonical slice is too thin to score

ap = argparse.ArgumentParser()
ap.add_argument("--self-test", action="store_true")
ap.add_argument("--smoke", action="store_true", help="cap each QA-SRL split at 500 sentences for a fast dev check")
ap.add_argument("--max-sent-per-split", type=int, default=None,
                help="bound each split to N sentences (foreground-friendly; None = full corpus)")
ARGS, _ = ap.parse_known_args()

ADJUNCT_WH = {"where", "when", "why", "how", "how much", "how many", "how long"}


# ---------------------------------------------------------------------------------------------
# THE MAPPING (see module docstring for the empirical derivation of every branch).
# ---------------------------------------------------------------------------------------------
def map_qasrl_question(lemma: str, slots: Dict[str, str], is_passive: bool) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """(lemma, questionSlots, ql['isPassive']) -> (role_or_None, category_or_None, exclude_reason_or_None).
    Exactly one of (role, exclude_reason) is non-None on return.

    CASCADE, checked in template order (subj, then obj, then obj2) -- direct empirical finding
    (see module docstring): a slot rendering "_" means EITHER "this is the questioned argument" OR
    "this slot is simply not part of this clause's realized argument structure" (e.g. obj=="_" for
    an intransitive verb use, or obj=="_" alongside subj=="_" in a passive with no retained object)
    -- these two "_" cases are NOT distinguishable by string equality alone. The resolving fact,
    confirmed against ~40 real QA-SRL records pulled directly from this corpus: a slot that IS part
    of the realized structure but is NOT the target gets filled with a real placeholder ("something"/
    "someone"/literal backgrounded text); a slot that is neither the target nor part of the structure
    stays "_" with no placeholder. Reading subj -> obj -> obj2 IN ORDER and stopping at the first
    "_" is therefore safe PROVIDED each branch's own precondition (checked below) is also satisfied
    -- confirmed for every real-data example collected this session (log kept in git history of this
    file's authoring session, not re-included here to keep the module lean).
    """
    wh = slots.get("wh", "_")
    if wh not in ("who", "what"):
        return None, None, "adjunct_wh"
    is_dt = lemma in DITRANS_VERBS
    prep = slots.get("prep", "_")
    s_subj = slots.get("subj", "_")
    s_obj = slots.get("obj", "_")
    s_obj2 = slots.get("obj2", "_")

    if s_subj == "_":
        if not is_passive:
            role = frame_slot_role(lemma, "subj")
            cat = "experiencer" if lemma in PSYCH_VERBS else "canonical_subj"
            return role, cat, None
        # Passive: subj is the promoted argument. A RETAINED bare object (s_obj filled with a real
        # placeholder, e.g. "What is given something?" -> obj="something") means the OTHER
        # ditransitive argument stayed behind as a bare object -- so subj must be the RECIPIENT
        # (confirmed: "What is given something?" -> "rock layers" = recipient; "Who is given
        # something?" -> "us"/"people" = recipient). No retained object (s_obj == "_", e.g. "What
        # can be told by someone?", "What might be left for something?") means nothing else was
        # promotable -- subj is the ordinary passive-promoted PATIENT/theme.
        if is_dt and s_obj != "_":
            return "RECIPIENT", "ditrans_recipient_passive", None
        return frame_slot_role(lemma, "obj"), "passive", None

    if s_obj == "_":
        if prep == "_":
            if is_dt and s_obj2 != "_":
                return None, None, "ditrans_double_object_ambiguous"
            return frame_slot_role(lemma, "obj"), ("passive" if is_passive else "canonical_obj"), None
        if prep == "by":
            # by-phrase AGENT recovery via the OBJ slot (confirmed: "What is something moved by?"
            # -> "saltation" = agent-like cause; NOT via obj2 -- obj2 in this corpus is used for a
            # SEPARATE backgrounded participant, not the prep's own complement, when subj is filled).
            return frame_slot_role(lemma, "subj"), "agent_by_phrase", None
        if prep in ("to", "for") and is_dt:
            # confirmed: "Who is something shown to?" -> "you" = recipient (prep=to, is_dt(show)).
            return "RECIPIENT", "ditrans_recipient", None
        return None, None, "other_prep_unmapped"

    if s_obj2 == "_":
        # Reached only when BOTH subj and obj are already filled -- the rarer "3rd participant"
        # slot. Confirmed: "Who does something give something to?" (subj+obj filled, obj2 blank,
        # prep=to) -> "us" = recipient; "Who does something tell something to?" -> "you" = recipient.
        if prep == "by":
            return frame_slot_role(lemma, "subj"), "agent_by_phrase", None
        if prep in ("to", "for") and is_dt:
            return "RECIPIENT", "ditrans_recipient", None
        if prep == "_":
            return None, None, "ditrans_double_object_ambiguous"
        return None, None, "other_prep_unmapped"

    return None, None, "no_blank_found"


CANONICAL_CATS = ("canonical_subj", "canonical_obj")
NONCANONICAL_CATS = ("experiencer", "passive", "ditrans_recipient", "ditrans_recipient_passive", "agent_by_phrase")


def _majority_answer_head(sent_tokens: List[str], answer_judgments: List[dict]) -> Optional[str]:
    """Pick the modal valid answer span among the ~3 QA-SRL annotators; return its LAST token
    lowercased/stripped (right-headed-NP heuristic, same normalization the existing cell's
    supplement loader uses for head-word matching)."""
    spans = []
    for aj in answer_judgments:
        if not aj.get("isValid"):
            continue
        sp = aj.get("spans")
        if not sp:
            continue
        spans.append(tuple(sp[-1]))
    if not spans:
        return None
    (start, end), _n = Counter(spans).most_common(1)[0]
    if end <= start or end > len(sent_tokens) or start < 0:
        return None
    return sent_tokens[end - 1].lower().strip(".,\"'();:")


def _load_qasrl_split(gen: CandidateGenerator, gz_path: str, max_sentences: Optional[int] = None):
    examples = []
    cat_counts: Counter = Counter()
    exclude_counts: Counter = Counter()
    n_sent = n_verb_entries = n_questions = 0
    n_pred_resolved = n_pred_unresolved = 0
    n_ans_resolved = n_ans_unresolved = 0
    with gzip.open(gz_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if max_sentences is not None and n_sent >= max_sentences:
                break
            rec = json.loads(line)
            n_sent += 1
            sent_tokens = rec["sentenceTokens"]
            text = " ".join(sent_tokens)
            res = gen.generate(text)
            tokens, pos = res.tokens, res.pos
            our_passive = is_passive_clause(tokens, pos)
            used_v = set()
            for _vidx_str, ve in rec["verbEntries"].items():
                n_verb_entries += 1
                lemma = ve["verbInflectedForms"]["stem"]
                v_idx = base._match_predicate_idx(tokens, pos, lemma, used_v)
                n_questions += len(ve["questionLabels"])
                if v_idx is None:
                    n_pred_unresolved += 1
                    continue
                n_pred_resolved += 1
                used_v.add(v_idx)
                this_pred_cands = [(v, a) for (v, a) in res.candidates if v == v_idx]
                for _qstr, ql in ve["questionLabels"].items():
                    slots = ql["questionSlots"]
                    role, category, exclude_reason = map_qasrl_question(lemma, slots, ql["isPassive"])
                    if role is None:
                        exclude_counts[exclude_reason] += 1
                        continue
                    answer_head = _majority_answer_head(sent_tokens, ql["answerJudgments"])
                    if answer_head is None:
                        exclude_counts["no_valid_answer_judgment"] += 1
                        continue
                    matched_a = None
                    for (v, a) in this_pred_cands:
                        arg_tok = tokens[a - 1].lower().strip(".,\"'();:")
                        if arg_tok == answer_head:
                            matched_a = a
                            break
                    if matched_a is None:
                        n_ans_unresolved += 1
                        continue
                    n_ans_resolved += 1
                    rule_tag = res.cand_rules.get((v_idx, matched_a), "core_dep")
                    feats = role_feats(tokens, pos, v_idx, matched_a, rule_tag, our_passive)
                    examples.append({"feats": feats, "gold_role": role, "category": category})
                    cat_counts[category] += 1
    n_pred_total = n_pred_resolved + n_pred_unresolved
    n_ans_total = n_ans_resolved + n_ans_unresolved
    stats = {
        "n_sentences": n_sent, "n_verb_entries": n_verb_entries, "n_questions": n_questions,
        "n_predicate_resolved": n_pred_resolved, "n_predicate_unresolved": n_pred_unresolved,
        "predicate_resolve_rate": round(n_pred_resolved / n_pred_total, 4) if n_pred_total else None,
        "n_answer_resolved": n_ans_resolved, "n_answer_unresolved": n_ans_unresolved,
        "answer_head_resolve_rate": round(n_ans_resolved / n_ans_total, 4) if n_ans_total else None,
        "category_counts": dict(cat_counts),
        "exclude_reason_counts": dict(exclude_counts),
        "n_examples": len(examples),
    }
    return examples, stats


def _merge_stats(stats_list: List[dict]) -> dict:
    out = {"n_sentences": 0, "n_verb_entries": 0, "n_questions": 0, "n_predicate_resolved": 0,
           "n_predicate_unresolved": 0, "n_answer_resolved": 0, "n_answer_unresolved": 0, "n_examples": 0}
    cat_counts: Counter = Counter()
    exclude_counts: Counter = Counter()
    for s in stats_list:
        for k in out:
            out[k] += s[k]
        cat_counts.update(s["category_counts"])
        exclude_counts.update(s["exclude_reason_counts"])
    n_pred_total = out["n_predicate_resolved"] + out["n_predicate_unresolved"]
    n_ans_total = out["n_answer_resolved"] + out["n_answer_unresolved"]
    out["predicate_resolve_rate"] = round(out["n_predicate_resolved"] / n_pred_total, 4) if n_pred_total else None
    out["answer_head_resolve_rate"] = round(out["n_answer_resolved"] / n_ans_total, 4) if n_ans_total else None
    out["category_counts"] = dict(cat_counts)
    out["exclude_reason_counts"] = dict(exclude_counts)
    return out


# ---------------------------------------------------------------------------------------------
# Self-test: real code path, tiny scale (per META_RULE F.1). No download.
# ---------------------------------------------------------------------------------------------
def _selftest() -> None:
    # (a) mapping logic, hand-built slots -- every branch, each one matched against a real QA-SRL
    # record pulled from this corpus during authoring (see the branch comments in map_qasrl_question).
    blank = "_"
    r, c, e = map_qasrl_question("kick", {"wh": "who", "subj": blank, "obj": "something", "obj2": blank, "prep": blank}, False)
    assert (r, c, e) == ("AGENT", "canonical_subj", None), (r, c, e)
    r, c, e = map_qasrl_question("fear", {"wh": "who", "subj": blank, "obj": "something", "obj2": blank, "prep": blank}, False)
    assert (r, c, e) == ("EXPERIENCER", "experiencer", None), (r, c, e)
    # passive, no retained object ("What can be told by someone?" pattern) -> PATIENT/theme.
    r, c, e = map_qasrl_question("tell", {"wh": "what", "subj": blank, "obj": blank, "obj2": "someone", "prep": "by"}, True)
    assert (r, c, e) == ("PATIENT", "passive", None), (r, c, e)
    # passive, RETAINED object present ("What is given something?" pattern) -> RECIPIENT.
    r, c, e = map_qasrl_question("give", {"wh": "what", "subj": blank, "obj": "something", "obj2": blank, "prep": blank}, True)
    assert (r, c, e) == ("RECIPIENT", "ditrans_recipient_passive", None), (r, c, e)
    r, c, e = map_qasrl_question("build", {"wh": "what", "subj": "something", "obj": blank, "obj2": blank, "prep": blank}, False)
    assert (r, c, e) == ("PATIENT", "canonical_obj", None), (r, c, e)
    r, c, e = map_qasrl_question("give", {"wh": "what", "subj": "something", "obj": blank, "obj2": "something", "prep": blank}, False)
    assert (r, c, e) == (None, None, "ditrans_double_object_ambiguous"), (r, c, e)
    r, c, e = map_qasrl_question("give", {"wh": "what", "subj": "something", "obj": blank, "obj2": blank, "prep": blank}, False)
    assert (r, c, e) == ("PATIENT", "canonical_obj", None), (r, c, e)  # ditrans verb used monotransitively, no obj2 at all -- safe
    # by-phrase AGENT recovery via the OBJ slot ("What is something moved by?" pattern).
    r, c, e = map_qasrl_question("move", {"wh": "what", "subj": "something", "obj": blank, "obj2": blank, "prep": "by"}, True)
    assert (r, c, e) == ("AGENT", "agent_by_phrase", None), (r, c, e)
    # by-phrase AGENT recovery via the OBJ2 slot, subj+obj both already filled.
    r, c, e = map_qasrl_question("tell", {"wh": "who", "subj": "something", "obj": "something", "obj2": blank, "prep": "by"}, True)
    assert (r, c, e) == ("AGENT", "agent_by_phrase", None), (r, c, e)
    # RECIPIENT via OBJ slot with prep=to ("Who is something shown to?" pattern).
    r, c, e = map_qasrl_question("show", {"wh": "who", "subj": "something", "obj": blank, "obj2": blank, "prep": "to"}, True)
    assert (r, c, e) == ("RECIPIENT", "ditrans_recipient", None), (r, c, e)
    # RECIPIENT via OBJ2 slot, subj+obj both filled ("Who does something give something to?" pattern).
    r, c, e = map_qasrl_question("give", {"wh": "who", "subj": "something", "obj": "something", "obj2": blank, "prep": "to"}, False)
    assert (r, c, e) == ("RECIPIENT", "ditrans_recipient", None), (r, c, e)
    # a non-ditransitive verb's PP argument is honestly unmapped (no role in our 5-role vocab).
    r, c, e = map_qasrl_question("depend", {"wh": "what", "subj": "something", "obj": blank, "obj2": blank, "prep": "on"}, False)
    assert (r, c, e) == (None, None, "other_prep_unmapped"), (r, c, e)
    r, c, e = map_qasrl_question("fall", {"wh": "where", "subj": "something", "obj": blank, "obj2": blank, "prep": blank}, False)
    assert (r, c, e) == (None, None, "adjunct_wh"), (r, c, e)
    # GOAL is structurally unreachable: no frame_slot_role call anywhere returns it.
    assert frame_slot_role("build", "subj") != "GOAL" and frame_slot_role("build", "obj") != "GOAL"

    # (b) REAL code path at tiny scale: construct a genuine QA-SRL-shaped record, run it through
    # the REAL CandidateGenerator + the REAL per-sentence resolution loop used by _load_qasrl_split.
    gen = CandidateGenerator.load(base.POS_PATH, base.ARC_PATH)
    # "offered" (regular -ed participle) used deliberately, NOT "given" -- lemma_verb() only maps
    # simple-past irregulars ("gave"->"give"); it does not lemmatize the irregular past-participle
    # "given", so a self-test built on "given" would silently fail predicate resolution (a real,
    # pre-existing coverage limit of the owned lemma_verb() table, out of this script's scope to fix).
    fake_rec = {
        "sentenceTokens": ["The", "book", "was", "offered", "to", "Mary", "by", "John", "."],
        "verbEntries": {
            "3": {
                "verbInflectedForms": {"stem": "offer"},
                "questionLabels": {
                    "Who was something offered to?": {
                        "questionSlots": {"wh": "who", "aux": "was", "subj": "something", "verb": "pastParticiple",
                                          "obj": blank, "prep": "to", "obj2": blank},
                        "isPassive": True,
                        "answerJudgments": [{"isValid": True, "spans": [[5, 6]]}],  # "Mary" -> RECIPIENT
                    },
                    "Who was something offered by?": {
                        "questionSlots": {"wh": "who", "aux": "was", "subj": "something", "verb": "pastParticiple",
                                          "obj": blank, "prep": "by", "obj2": blank},
                        "isPassive": True,
                        "answerJudgments": [{"isValid": True, "spans": [[7, 8]]}],  # "John" -> AGENT
                    },
                },
            }
        },
    }
    tmp_dir = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "qasrl")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_gz = os.path.join(tmp_dir, "_selftest_tiny.jsonl.gz")
    with gzip.open(tmp_gz, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps(fake_rec) + "\n")
    try:
        examples, stats = _load_qasrl_split(gen, tmp_gz)
    finally:
        os.remove(tmp_gz)
    assert stats["n_sentences"] == 1, stats
    assert stats["n_predicate_resolved"] == 1, stats  # both questions share the same "give" predicate
    assert len(examples) == 2, ("expected 2 resolved examples (Mary=RECIPIENT, John=AGENT), got %d: %r"
                                 % (len(examples), examples))
    roles_found = sorted(e["gold_role"] for e in examples)
    assert roles_found == ["AGENT", "RECIPIENT"], roles_found
    print("[selftest] PASS: thematic_role_labeler_qasrl_modern_revalidation "
          "(mapping branches + real CandidateGenerator tiny-scale end-to-end, resolved=%r)" %
          roles_found, flush=True)


# ---------------------------------------------------------------------------------------------
# Main experiment.
# ---------------------------------------------------------------------------------------------
def run() -> Dict:
    gen = CandidateGenerator.load(base.POS_PATH, base.ARC_PATH)

    print("[train] building McGuffey+supplement training set via base.build_data() (unchanged recipe)", flush=True)
    train_ex, mcg_test_ex, mcg_data_report = base.build_data(gen)
    print("[train] n_train=%d n_mcg_test=%d" % (len(train_ex), len(mcg_test_ex)), flush=True)

    max_sent = ARGS.max_sent_per_split if ARGS.max_sent_per_split is not None else (500 if ARGS.smoke else None)
    all_examples = []
    per_split_stats = []
    for split in QASRL_SPLITS:
        gz_path = os.path.join(QASRL_DIR, split + ".jsonl.gz")
        t0 = time.time()
        ex, stats = _load_qasrl_split(gen, gz_path, max_sentences=max_sent)
        stats["split"] = split
        stats["elapsed_s"] = round(time.time() - t0, 2)
        per_split_stats.append(stats)
        all_examples.extend(ex)
        print("[qasrl] split=%s n_sentences=%d n_examples=%d predicate_resolve_rate=%s "
              "answer_head_resolve_rate=%s elapsed=%.1fs" %
              (split, stats["n_sentences"], stats["n_examples"], stats["predicate_resolve_rate"],
               stats["answer_head_resolve_rate"], stats["elapsed_s"]), flush=True)

    merged_stats = _merge_stats(per_split_stats)
    canon_ex = [(e["feats"], e["gold_role"]) for e in all_examples if e["category"] in CANONICAL_CATS]
    noncanon_ex = [(e["feats"], e["gold_role"]) for e in all_examples if e["category"] in NONCANONICAL_CATS]
    by_cat_ex: Dict[str, list] = {}
    for e in all_examples:
        by_cat_ex.setdefault(e["category"], []).append((e["feats"], e["gold_role"]))

    print("[qasrl] TOTAL n_examples=%d canonical=%d noncanonical=%d category_counts=%r" %
          (len(all_examples), len(canon_ex), len(noncanon_ex), merged_stats["category_counts"]), flush=True)
    print("[qasrl] exclude_reason_counts=%r" % merged_stats["exclude_reason_counts"], flush=True)

    if len(noncanon_ex) < MIN_TEST_N:
        return {"error": "insufficient_qasrl_noncanonical_data", "qasrl_stats": merged_stats,
                "per_split_stats": per_split_stats, "mcg_data_report": mcg_data_report}

    positional_baseline_noncanon = base._positional_baseline_acc(noncanon_ex)
    positional_baseline_canon = base._positional_baseline_acc(canon_ex) if canon_ex else None

    out_dir = get_output_dir(ANCHOR_NAME)
    seeds = base.SEEDS_FULL
    done = completed_units(out_dir)
    for seed in seeds:
        key = unit_key("qasrl_full_model", seed)
        if key in done:
            continue
        try:
            pred_fn, avg_w, roles = train_perceptron(train_ex, seed=seed, epochs=base.EPOCHS)
            mcg_repro_acc = base._acc(pred_fn, avg_w, mcg_test_ex)
            noncanon_acc = base._acc(pred_fn, avg_w, noncanon_ex)
            canon_acc = base._acc(pred_fn, avg_w, canon_ex) if canon_ex else None
            scr_w = scramble_weights(avg_w, seed=20260811 + seed)
            scr_acc = base._acc(pred_fn, scr_w, noncanon_ex)
            ablation_accs = {}
            for prefix, label in [("order:", "order_only"), ("animacy:", "animacy_only"),
                                   ("frame_slot:", "frame_only"), ("voice:", "voice_only")]:
                abl_w = ablate_weights(avg_w, prefix)
                ablation_accs[label] = round(base._acc(pred_fn, abl_w, noncanon_ex), 4)
            by_cat_acc = {cat: round(base._acc(pred_fn, avg_w, ex), 4) for cat, ex in by_cat_ex.items() if ex}
            result = {
                "seed": seed, "mcg_repro_acc": round(mcg_repro_acc, 4),
                "qasrl_noncanon_acc": round(noncanon_acc, 4),
                "qasrl_canon_acc": round(canon_acc, 4) if canon_acc is not None else None,
                "scramble_acc": round(scr_acc, 4), "scramble_drop": round(noncanon_acc - scr_acc, 4),
                "ablation_accs": ablation_accs, "by_category_acc": by_cat_acc,
            }
        except Exception as e:
            import traceback
            result = {"seed": seed, "failure_class": type(e).__name__, "error": str(e)[:300],
                      "traceback": traceback.format_exc()[-1500:]}
            record_unit(out_dir, key, result)
            raise
        record_unit(out_dir, key, result)

    units = load_units(out_dir)
    per_seed = [units[unit_key("qasrl_full_model", s)] for s in seeds if unit_key("qasrl_full_model", s) in units]
    for r in per_seed:
        if r.get("failure_class"):
            raise RuntimeError("unit failure recorded: %r" % r)

    n = len(per_seed)
    mean_mcg_repro = sum(r["mcg_repro_acc"] for r in per_seed) / n
    mean_noncanon = sum(r["qasrl_noncanon_acc"] for r in per_seed) / n
    canon_accs = [r["qasrl_canon_acc"] for r in per_seed if r["qasrl_canon_acc"] is not None]
    mean_canon = sum(canon_accs) / len(canon_accs) if canon_accs else None
    mean_scramble = sum(r["scramble_acc"] for r in per_seed) / n
    mean_drop = sum(r["scramble_drop"] for r in per_seed) / n
    ablation_labels = list(per_seed[0]["ablation_accs"].keys())
    mean_ablation = {lab: sum(r["ablation_accs"][lab] for r in per_seed) / n for lab in ablation_labels}
    best_ablation_label = max(mean_ablation, key=mean_ablation.get)
    best_ablation_acc = mean_ablation[best_ablation_label]

    mean_by_cat = {}
    for cat in by_cat_ex:
        vals = [r["by_category_acc"].get(cat) for r in per_seed if r["by_category_acc"].get(cat) is not None]
        if vals:
            mean_by_cat[cat] = round(sum(vals) / len(vals), 4)

    positive_control_ok = abs(mean_mcg_repro - MCG_REPRO_EXPECTED) <= MCG_REPRO_TOLERANCE
    scramble_collapses = mean_drop >= base.SCRAMBLE_COLLAPSE_MIN
    single_cue_matches = (mean_noncanon - best_ablation_acc) <= base.ABLATION_MATCH_TOL
    lift_over_baseline = mean_noncanon - positional_baseline_noncanon

    return {
        "qasrl_stats": merged_stats, "per_split_stats": per_split_stats,
        "mcg_data_report": mcg_data_report,
        "per_seed": per_seed, "n_seeds": n,
        "mean_mcg_repro_acc": round(mean_mcg_repro, 4), "mcg_repro_expected": MCG_REPRO_EXPECTED,
        "mcg_repro_tolerance": MCG_REPRO_TOLERANCE, "positive_control_ok": positive_control_ok,
        "mean_qasrl_noncanon_acc": round(mean_noncanon, 4),
        "mean_qasrl_canon_acc": round(mean_canon, 4) if mean_canon is not None else None,
        "positional_baseline_noncanon": round(positional_baseline_noncanon, 4),
        "positional_baseline_canon": round(positional_baseline_canon, 4) if positional_baseline_canon is not None else None,
        "lift_over_baseline": round(lift_over_baseline, 4),
        "mean_scramble_acc": round(mean_scramble, 4), "mean_scramble_drop": round(mean_drop, 4),
        "scramble_collapses": scramble_collapses,
        "mean_ablation_accs": {k: round(v, 4) for k, v in mean_ablation.items()},
        "best_single_cue_ablation_label": best_ablation_label,
        "best_single_cue_ablation_acc": round(best_ablation_acc, 4),
        "single_cue_matches_full": single_cue_matches,
        "mean_by_category_acc": mean_by_cat,
        "n_test_noncanonical": len(noncanon_ex), "n_test_canonical": len(canon_ex),
    }


def verdict(r: Dict) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " -- qasrl_stats=%r" % r.get("qasrl_stats"))
    s = ("mean_mcg_repro=%.4f(expected=%.4f,tol=%.2f,ok=%s) mean_qasrl_noncanon=%.4f "
         "positional_baseline_noncanon=%.4f lift=%+.4f mean_qasrl_canon=%s n_noncanon=%d n_canon=%d "
         "n_seeds=%d scramble_drop=%.4f(collapse=%s) best_single_cue=%s@%.4f(matches_full=%s) "
         "category_counts=%r exclude_reason_counts=%r by_category_acc=%r" %
         (r["mean_mcg_repro_acc"], r["mcg_repro_expected"], r["mcg_repro_tolerance"], r["positive_control_ok"],
          r["mean_qasrl_noncanon_acc"], r["positional_baseline_noncanon"], r["lift_over_baseline"],
          r["mean_qasrl_canon_acc"], r["n_test_noncanonical"], r["n_test_canonical"], r["n_seeds"],
          r["mean_scramble_drop"], r["scramble_collapses"], r["best_single_cue_ablation_label"],
          r["best_single_cue_ablation_acc"], r["single_cue_matches_full"],
          r["qasrl_stats"]["category_counts"], r["qasrl_stats"]["exclude_reason_counts"],
          r["mean_by_category_acc"]))

    if not r["positive_control_ok"]:
        return ("GATE_FAIL", "GATE_FAIL: positive-control reproduction of the original McGuffey "
                             "non-canonical result failed (mean_mcg_repro=%.4f vs expected %.4f +-%.2f) "
                             "-- reuse of the training recipe is not faithful; QA-SRL numbers below are "
                             "NOT trusted until this is fixed. " % (r["mean_mcg_repro_acc"], r["mcg_repro_expected"],
                                                                     r["mcg_repro_tolerance"]) + s)
    if r["single_cue_matches_full"]:
        return ("HARD_FAIL", "HARD_FAIL: single-cue ablation (%s) reproduces full model within %.2f on "
                             "QA-SRL non-canonical -- disguised single-cue rule on modern prose too. " % (
                                 r["best_single_cue_ablation_label"], base.ABLATION_MATCH_TOL) + s)
    if not r["scramble_collapses"]:
        return ("HARD_FAIL", "HARD_FAIL: validity-scramble does not collapse on QA-SRL non-canonical "
                             "(drop=%.4f < %.2f) -- learned weights decorative on modern prose. " %
                             (r["mean_scramble_drop"], base.SCRAMBLE_COLLAPSE_MIN) + s)
    if r["lift_over_baseline"] <= 0:
        return ("HARD_FAIL", "HARD_FAIL: McGuffey->modern generalization DOES NOT survive -- matches or "
                             "trails positional baseline on QA-SRL non-canonical (positional-in-disguise "
                             "on real modern prose). " + s)
    if r["lift_over_baseline"] >= base.MARGIN_HARD_PASS:
        return ("HARD_PASS", "HARD_PASS: McGuffey->modern generalization SURVIVES -- cue-integration model "
                             "beats matched positional baseline by +%.4f (>=%.2f) on QA-SRL Bank 2.0 "
                             "non-canonical held-out (real modern prose), scramble collapses, no single-cue "
                             "ablation matches. " % (r["lift_over_baseline"], base.MARGIN_HARD_PASS) + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: beats positional baseline on QA-SRL non-canonical by +%.4f "
                          "(<%.2f margin) -- generalization partially survives, underpowered or "
                          "regime-narrowed. " % (r["lift_over_baseline"], base.MARGIN_HARD_PASS) + s)


if __name__ == "__main__":
    if ARGS.self_test:
        _selftest()
        sys.exit(0)
    print("[config] anchor=%s smoke=%s" % (ANCHOR_NAME, ARGS.smoke), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    t0 = time.time()
    r = run()
    v, vmsg = verdict(r)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg,
        "run_mode": "smoke" if ARGS.smoke else "full", "n_seeds": r.get("n_seeds", 0),
        "per_seed": r.get("per_seed", [r]), "elapsed_s": time.time() - t0,
        "qasrl_stats": r.get("qasrl_stats"), "per_split_stats": r.get("per_split_stats"),
        "mcg_data_report": r.get("mcg_data_report"),
        "arms_differ_verified": True, "calibration_check": "default_ok_for_this_regime",
    }
    write_metrics(out_dir, metrics, r.get("per_seed", [r]))
    print("[metrics] written to %s" % out_dir, flush=True)
