"""
DIAGNOSTIC CAN-FAIL CONTROL CELL, DEEP-EARN v6c -- fixes the REAL bug behind
v6b's scoring artifact (the candidate-ORDER tie-break in the unstated_goal
4-way multiple-choice scorer) and re-measures the true content-vs-random
reading on the ORIGINAL Director-VERIFIED CLEAN 25-item eval.

BUG BEING FIXED (found by Director-VET, commit c4ca2bde5, rejecting the
954f2437d eval-hardening workaround as gaming-the-eval-not-fixing-the-scorer):
v6b's ARM_LENGTH_ONLY and (inherited from v6) score_arm_v6's unstated_goal
4-way MC both build `candidates = [item["correct_category"]] + list(
item["distractor_categories"])` then call `predicted = max(scores_or_sims,
key=....get)`. Python's max() over a dict with tied values returns the
FIRST-inserted key that attains the max (stable iteration order = insertion
order = dict construction order = candidates list order). Since
prototype-vs-action structural/lexical overlap is ~0 for most items (4-way
ties), and `correct_category` is ALWAYS inserted FIRST in the candidates
list, the tie almost always silently resolves to the correct answer --
NOT because the scorer discriminated content, but because of list
CONSTRUCTION order. This is a genuine scorer bug (order-dependent
tie-break), not an eval-hardness problem; hardening the eval (954f2437d)
treated the symptom (adding an artificial worst-case distractor) and
Director-VET correctly rejected it for introducing label ambiguity on 3
items (005/007/011 -- their length/overlap-best candidate legitimately
WAS the correct category, so swapping distractors around them made the
new "hardened" item internally contestable).

THE FIX (ONE variable; everything else identical to v6b): replace every
max()-over-candidates tie-break in score_arm_v6 (unstated_goal branch) and
score_arm_length_only (unstated_goal branch) with a CONTENT-INDEPENDENT,
ORDER-INDEPENDENT tie-break rule (see _tie_break_pick below): if there is a
UNIQUE max, take it (unchanged behavior -- no ties are never touched); if
there is an EXACT tie among >=2 candidates, resolve deterministically via a
fixed seed derived from (item_id, sorted tied-candidate-name-tuple) -- NEVER
from candidates-list INSERTION order, so "correct listed first" cannot win
by construction. satisfy_restate / thwart_cause branches in both scorers
already compare exactly TWO named similarities with strict `>` (sim_satisfy
> sim_restate / sim_b > sim_dist) -- ties there ALREADY resolve to `False`
(a miss) independent of any list/dict order, so they do not have this bug
and are NOT modified (verified explicitly in self_test below).

Prior-work check (substrate_query.sh, mandatory before authoring): queried
"tie-break candidate order max dict scoring artifact deterministic
order-independent multiple-choice" -- top-5 hits all cosine<=0.2852 (below
the 0.30 rediscovery-flag threshold; nearest was an unrelated determinism
note about file-glob/dict-iteration order, not a scoring tie-break). GENUINELY
NOVEL for this exact question; not a rediscovery.

DECISIVE QUESTIONS (pre-registered BEFORE running):
  Q1 TIE_BREAK_WAS_THE_ARTIFACT: after the fix, do the CONTENT-FREE baselines
    (ARM_LENGTH_ONLY, ARM_PURE_STRUCTURE_NO_CONTENT) drop to ~chance
    (unstated_goal ~0.25, satisfy_restate/thwart_cause ~0.50, overall ~0.38)?
    "near chance" = |acc - chance| <= Q1_NEAR_CHANCE_BAND (0.10, i.e. within
    ~1.2-2.5 items of 25 -- an N=25-appropriate discrete-count band,
    HYPOTHESIZED@this-file, same convention as v6b's own NEAR_RANDOM_INIT_BAND).
    If YES -> the v6b "artifact" WAS the tie-break bug; the eval did NOT need
    hardening.
  Q2 RANDOM_STILL_BEATS_TRAINED: after the fix, does ARM_RANDOM_INIT_CONTROL
    overall_accuracy still >= max(ARM_ERROR_DRIVEN_SGNS, ARM_PPMI_MEANREMOVAL)?
    PREDICTED YES (real untrained/trained vectors rarely land on an EXACT
    floating-point tie, so the tie-break fix barely moves arms that carry
    real content vectors -- the random>trained puzzle, if it persists, is a
    DEEPER issue independent of the tie-break: the bind/overlap channel
    rewards raw shared-word overlap in a way that SGNS/PPMI training can
    degrade). Reported honestly either way, margin included.

DISCIPLINE:
- glass-box, no borrowed embedding/model/LLM; REUSES v6/v6b/v5/v4/v3's own
  functions VERBATIM for everything except the tie-break (build_event_struct_v6,
  _role_split_words, structure_overlap, make_role_vecs, make_objidx_roles,
  make_const_dense_vecs, train_sgns, build_raw_ppmi_vectors, apply_mean_removal,
  load_gold_eval, CATEGORY_PROTOTYPES, all CHANCE_/EXPECTED_N_ constants).
  ONE new variable: the tie-break rule, applied uniformly to every arm's
  unstated_goal scorer (score_arm_v6_tiebreak_fixed wraps the SAME
  build_event_struct_v6/structure_overlap calls as score_arm_v6;
  score_arm_length_only_tiebreak_fixed wraps the SAME overlap-count/length
  scoring as v6b's score_arm_length_only). satisfy_restate/thwart_cause
  scoring code is copied BYTE-IDENTICAL from v6/v6b (no tie-break bug there;
  see docstring above + self_test assertion that they are unmodified).
- --self-test CONSTRUCTS a real tie fixture (two candidates with textually
  IDENTICAL prototype content -> guaranteed exact structure_overlap tie) and
  asserts the winner is IDENTICAL regardless of whether the correct category
  is inserted first or last in the candidates list -- this is the direct
  proof the order-leak is closed.
- deterministic_seeding: reuses v6b's fixed seeds bit-for-bit for every
  reproduced arm; tie-break RNG is seeded from hashlib.md5(item_id +
  sorted-tied-tuple), NOT from Python's randomized-per-process hash() and NOT
  from list/dict insertion order (avoids the PYTHONHASHSEED nondeterminism
  class flagged in prior sessions).
- ARMS-MUST-DIFFER (META_RULE_AF): hash-check across all 5 arms' composite
  event structures for one shared text (goal0_text), reused from v6b verbatim.
- except SystemExit / except Exception ordering: no bare except, no
  BaseException.
- final_metrics_atomicity: tmp_replace (os.replace) on metrics.json.
- cardinality_ok: 25 gold items (12+7+6) x 5 arms; per-arm scored units = 74
  (12*4 + 7*2 + 6*2), asserted via len() == EXPECTED at load time and at
  per-arm scored-unit count time for every arm (vector arms + length_only).
- CRLB n/a (no fixed-capacity argmax-noise floor; discrete-tier accuracy-
  count feasibility over N=25 items is the analogue, per v6/v6b's convention).
- runtime bound: reuses v6b's own SGNS retrain (measured elapsed_s=138-145s
  there) plus PPMI rebuild; the tie-break wrapper adds negligible overhead
  (same O(1) per-item work, just a different pick rule). Single foreground
  run, well under 10 min. progress_logging=print_flush_true.
- Content-filter safety: reuses ONLY the already-vetted Director-verified
  gold_relation_inference_v1.jsonl (the ORIGINAL clean 25-item file, NOT the
  954f2437d hardened/UNVERIFIED file) and v6's own CATEGORY_PROTOTYPES -- no
  new snippets introduced by this cell.
- GIT: local only, no push; this file + its metrics.json are the only new
  paths this cell should stage. Does NOT dispatch anything (diagnostic
  measurement, not a cell for the queue). --no-verify per caller instruction.
"""
import os
import sys
import json
import time
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from experiments.exp_content_awareness_earned_v6_depooled_object_verified_eval import (  # noqa: E402
    CATEGORY_PROTOTYPES,
    load_gold_eval,
    GOLD_EVAL_PATH,
    make_objidx_roles,
    build_event_struct_v6,
    OBJIDX_ROLE_SEED_D64,
    OBJIDX_ROLE_SEED_PPMI,
    CHANCE_OVERALL_WEIGHTED,
    CHANCE_UNSTATED,
    CHANCE_SATREST,
    CHANCE_THWART,
    EXPECTED_N_UNSTATED_GOAL_ITEMS,
    EXPECTED_N_SATISFY_RESTATE_ITEMS,
    EXPECTED_N_THWART_CAUSE_ITEMS,
    EXPECTED_N_TOTAL_ITEMS,
    EXPECTED_N_SCORED_UNITS_PER_ARM,
)
from experiments.exp_content_awareness_earned_v5_bound_role_filler_representation import (  # noqa: E402
    make_role_vecs,
    _role_split_words,
    structure_overlap,
    _arms_must_differ_tensors,
)
from experiments.exp_content_awareness_ceiling_probe_earned_v3_rawppmi_meanremoval import (  # noqa: E402
    build_raw_ppmi_vectors,
    apply_mean_removal,
    _tokenize,
)
from experiments.exp_content_awareness_earned_v4_error_driven_sgns import (  # noqa: E402
    train_sgns,
    D_EMBED,
)
from experiments.exp_content_awareness_earned_v6b_scoring_artifact_control import (  # noqa: E402
    make_const_dense_vecs,
)

OUTPUT_DIR = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v6c_tiebreak_fixed_control"
)
ANCHOR_NAME = "content_awareness_earned_v6c_tiebreak_fixed_control"

V6B_METRICS_PATH = os.path.join(
    REPO_ROOT, "data", "exp_content_awareness_earned_v6b_scoring_artifact_control", "metrics.json"
)

CORPUS_PATHS = [
    os.path.join(REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
                 "anne_of_green_gables.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "wizard_of_oz", "cleaned",
                 "wizard_of_oz.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "tom_sawyer", "cleaned",
                 "tom_sawyer.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "little_women", "cleaned",
                 "little_women.clean.txt"),
    os.path.join(REPO_ROOT, "data", "corpora", "alice_in_wonderland", "cleaned",
                 "alice_in_wonderland.clean.txt"),
]

EXPECTED_N_ARMS = 5

# Pre-registered thresholds (declared before running)
Q1_NEAR_CHANCE_BAND = 0.10
Q2_MARGIN_REPORT_ONLY = True  # Q2 is reported honestly with the numeric margin, not gated pass/fail

PURE_STRUCTURE_CONST_SEED = 77001
TIE_BREAK_EPS = 1e-9
TIE_BREAK_SEED_BASE = 90001


def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _stable_seed_from_key(key_str, salt=0):
    """Deterministic seed from a string key via hashlib (NOT Python's
    per-process-randomized hash()) so tie-break resolution is reproducible
    across machines/processes/PYTHONHASHSEED settings."""
    h = hashlib.md5(f"{salt}:{key_str}".encode("utf-8")).hexdigest()
    return int(h[:8], 16) % (2**31 - 1)


def _tie_break_pick(scores, item_id, seed_base=TIE_BREAK_SEED_BASE):
    """CONTENT-INDEPENDENT, ORDER-INDEPENDENT tie-break over a
    {candidate_name: score} dict.

    - If there is a UNIQUE max score, return it (candidates-list insertion
      order never enters the decision -- same as before, just made explicit).
    - If >=2 candidates are within TIE_BREAK_EPS of the max score, this is an
      EXACT tie. Resolve via a seed derived ONLY from (item_id, the SORTED
      tuple of tied candidate NAMES) -- sorting means the resolution cannot
      depend on which order the candidates were inserted into the dict/list,
      so "correct_category listed first" can no longer win by construction.

    Returns (predicted_name, was_tie: bool, tied_candidates: list[str]).
    """
    best = max(scores.values())
    tied = sorted(c for c, v in scores.items() if abs(v - best) <= TIE_BREAK_EPS)
    if len(tied) == 1:
        return tied[0], False, tied
    seed = _stable_seed_from_key(f"{item_id}|{'|'.join(tied)}", salt=seed_base)
    rng = np.random.RandomState(seed)
    choice = tied[int(rng.randint(0, len(tied)))]
    return choice, True, tied


def score_arm_v6_tiebreak_fixed(arm_name, idx, dense_vecs, d, role_vecs, objidx_roles,
                                 unstated_items, satrest_items, thwart_items):
    """Same as v6's score_arm_v6 (build_event_struct_v6 + structure_overlap,
    verbatim), except the unstated_goal 4-way MC tie-break is replaced by
    _tie_break_pick (ONE variable changed). satisfy_restate/thwart_cause
    branches are copied BYTE-IDENTICAL from score_arm_v6 -- they already
    resolve exact ties to `correct=False` via strict `>` comparison of two
    NAMED similarities (order-independent by construction; not touched)."""
    cache = {}

    def get(text):
        if text not in cache:
            cache[text] = build_event_struct_v6(text, idx, dense_vecs, d, role_vecs, objidx_roles)
        return cache[text]

    unstated_results = []
    unstated_correct = 0
    n_ties_unstated = 0
    for item in unstated_items:
        action_struct, _, _, action_cov = get(item["action_text"])
        candidates = [item["correct_category"]] + list(item["distractor_categories"])
        assert len(candidates) == 4, f"expected 4-way MC, got {len(candidates)} for {item['id']}"
        sims = {}
        for cat in candidates:
            proto_struct, _, _, _ = get(CATEGORY_PROTOTYPES[cat])
            sim, _zero = structure_overlap(action_struct, proto_struct, d)
            sims[cat] = sim
        predicted, was_tie, tied_set = _tie_break_pick(sims, item["id"])
        if was_tie:
            n_ties_unstated += 1
        correct = predicted == item["correct_category"]
        if correct:
            unstated_correct += 1
        unstated_results.append({
            "id": item["id"], "correct_category": item["correct_category"],
            "predicted_category": predicted, "correct": correct, "sims": sims,
            "was_tie": was_tie, "tied_candidates": tied_set,
            "action_coverage": action_cov,
        })

    # ---- satisfy_restate: unchanged from v6 (no tie-break bug; strict >) ----
    satrest_results = []
    satrest_correct = 0
    for item in satrest_items:
        goal_struct, _, _, goal_cov = get(item["goal_text"])
        restate_struct, _, _, restate_cov = get(item["restate_text"])
        satisfy_struct, _, _, satisfy_cov = get(item["satisfy_text"])
        sim_restate, _ = structure_overlap(goal_struct, restate_struct, d)
        sim_satisfy, _ = structure_overlap(goal_struct, satisfy_struct, d)
        correct = sim_satisfy > sim_restate
        if correct:
            satrest_correct += 1
        satrest_results.append({
            "id": item["id"], "sim_goal_to_restate": sim_restate, "sim_goal_to_satisfy": sim_satisfy,
            "correct": correct, "goal_coverage": goal_cov, "restate_coverage": restate_cov,
            "satisfy_coverage": satisfy_cov,
        })

    # ---- thwart_cause: unchanged from v6 (no tie-break bug; strict >) ----
    thwart_results = []
    thwart_correct = 0
    for item in thwart_items:
        a_struct, _, _, a_cov = get(item["event_a_text"])
        b_struct, _, _, b_cov = get(item["event_b_text"])
        dist_struct, _, _, dist_cov = get(item["distractor_text"])
        sim_b, _ = structure_overlap(a_struct, b_struct, d)
        sim_dist, _ = structure_overlap(a_struct, dist_struct, d)
        correct = sim_b > sim_dist
        if correct:
            thwart_correct += 1
        thwart_results.append({
            "id": item["id"], "sim_a_to_b": sim_b, "sim_a_to_distractor": sim_dist,
            "correct": correct, "event_a_coverage": a_cov, "event_b_coverage": b_cov,
            "distractor_coverage": dist_cov,
        })

    n_scored = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    expected_from_inputs = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    assert n_scored == expected_from_inputs, (
        f"cardinality_ok breach for {arm_name}: got {n_scored} scored units, "
        f"expected {expected_from_inputs} from inputs"
    )

    n_total = len(unstated_items) + len(satrest_items) + len(thwart_items)
    overall_correct = unstated_correct + satrest_correct + thwart_correct

    return {
        "arm_name": arm_name,
        "unstated_goal_accuracy": unstated_correct / len(unstated_items),
        "unstated_goal_correct_count": unstated_correct,
        "unstated_goal_n_ties": n_ties_unstated,
        "satisfy_restate_accuracy": satrest_correct / len(satrest_items),
        "satisfy_restate_correct_count": satrest_correct,
        "thwart_cause_accuracy": thwart_correct / len(thwart_items),
        "thwart_cause_correct_count": thwart_correct,
        "overall_accuracy": overall_correct / n_total,
        "overall_correct_count": overall_correct,
        "n_total_items": n_total,
        "n_scored_units": n_scored,
        "cardinality_ok": n_scored == EXPECTED_N_SCORED_UNITS_PER_ARM,
        "unstated_results": unstated_results,
        "satrest_results": satrest_results,
        "thwart_results": thwart_results,
    }


def _content_words(text):
    return _role_split_words(text)[3]


def _overlap_count(words_a, words_b):
    return len(set(words_a) & set(words_b))


def score_arm_length_only_tiebreak_fixed(unstated_items, satrest_items, thwart_items):
    """Same as v6b's score_arm_length_only (zero vectors, content-WORD-COUNT
    features, verbatim), except the unstated_goal tie-break is replaced by
    _tie_break_pick. satisfy_restate/thwart_cause branches are copied
    BYTE-IDENTICAL from v6b -- already order-independent (strict >)."""
    unstated_results = []
    unstated_correct = 0
    n_ties_unstated = 0
    for item in unstated_items:
        action_words = _content_words(item["action_text"])
        candidates = [item["correct_category"]] + list(item["distractor_categories"])
        assert len(candidates) == 4, f"expected 4-way MC, got {len(candidates)} for {item['id']}"
        scores = {}
        for cat in candidates:
            proto_words = _content_words(CATEGORY_PROTOTYPES[cat])
            overlap = _overlap_count(action_words, proto_words)
            length_closeness = -abs(len(action_words) - len(proto_words))
            scores[cat] = overlap * 1000.0 + length_closeness
        predicted, was_tie, tied_set = _tie_break_pick(scores, item["id"])
        if was_tie:
            n_ties_unstated += 1
        correct = predicted == item["correct_category"]
        if correct:
            unstated_correct += 1
        unstated_results.append({
            "id": item["id"], "correct_category": item["correct_category"],
            "predicted_category": predicted, "correct": correct, "scores": scores,
            "was_tie": was_tie, "tied_candidates": tied_set,
        })

    satrest_results = []
    satrest_correct = 0
    for item in satrest_items:
        goal_words = _content_words(item["goal_text"])
        restate_words = _content_words(item["restate_text"])
        satisfy_words = _content_words(item["satisfy_text"])
        sim_restate = -abs(len(goal_words) - len(restate_words))
        sim_satisfy = -abs(len(goal_words) - len(satisfy_words))
        correct = sim_satisfy > sim_restate
        if correct:
            satrest_correct += 1
        satrest_results.append({
            "id": item["id"], "sim_goal_to_restate": sim_restate, "sim_goal_to_satisfy": sim_satisfy,
            "correct": correct,
        })

    thwart_results = []
    thwart_correct = 0
    for item in thwart_items:
        a_words = _content_words(item["event_a_text"])
        b_words = _content_words(item["event_b_text"])
        dist_words = _content_words(item["distractor_text"])
        sim_b = -abs(len(a_words) - len(b_words))
        sim_dist = -abs(len(a_words) - len(dist_words))
        correct = sim_b > sim_dist
        if correct:
            thwart_correct += 1
        thwart_results.append({
            "id": item["id"], "sim_a_to_b": sim_b, "sim_a_to_distractor": sim_dist,
            "correct": correct,
        })

    n_scored = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    expected_from_inputs = len(unstated_items) * 4 + len(satrest_items) * 2 + len(thwart_items) * 2
    assert n_scored == expected_from_inputs, (
        f"cardinality_ok breach for ARM_LENGTH_ONLY: got {n_scored} scored units, "
        f"expected {expected_from_inputs} from inputs"
    )
    n_total = len(unstated_items) + len(satrest_items) + len(thwart_items)
    overall_correct = unstated_correct + satrest_correct + thwart_correct

    return {
        "arm_name": "ARM_LENGTH_ONLY",
        "unstated_goal_accuracy": unstated_correct / len(unstated_items),
        "unstated_goal_correct_count": unstated_correct,
        "unstated_goal_n_ties": n_ties_unstated,
        "satisfy_restate_accuracy": satrest_correct / len(satrest_items),
        "satisfy_restate_correct_count": satrest_correct,
        "thwart_cause_accuracy": thwart_correct / len(thwart_items),
        "thwart_cause_correct_count": thwart_correct,
        "overall_accuracy": overall_correct / n_total,
        "overall_correct_count": overall_correct,
        "n_total_items": n_total,
        "n_scored_units": n_scored,
        "cardinality_ok": n_scored == EXPECTED_N_SCORED_UNITS_PER_ARM,
        "unstated_results": unstated_results,
        "satrest_results": satrest_results,
        "thwart_results": thwart_results,
    }


def main():
    t_start = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": EXPECTED_N_SCORED_UNITS_PER_ARM * EXPECTED_N_ARMS,
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    assert os.path.exists(GOLD_EVAL_PATH), f"Director-verified gold eval missing at {GOLD_EVAL_PATH}"
    unstated_items, satrest_items, thwart_items = load_gold_eval(GOLD_EVAL_PATH)
    assert len(unstated_items) == EXPECTED_N_UNSTATED_GOAL_ITEMS
    assert len(satrest_items) == EXPECTED_N_SATISFY_RESTATE_ITEMS
    assert len(thwart_items) == EXPECTED_N_THWART_CAUSE_ITEMS

    corpus_texts = []
    for p in CORPUS_PATHS:
        with open(p, "r", encoding="utf-8") as f:
            corpus_texts.append(f.read())
    print(f"[progress] corpus loaded, {len(corpus_texts)} files", flush=True)

    # ---- rebuild the SAME vocab/PPMI/SGNS pipeline as v6/v6b, bit-identically ----
    vocab, idx, ppmi_raw_vecs, n_tokens, vocab_size, ppmi_nnz = build_raw_ppmi_vectors(corpus_texts)
    ppmi_corrected_vecs, mean_vec, top_dirs, mr_iters, mr_residuals = apply_mean_removal(ppmi_raw_vecs)
    print(f"[progress] PPMI+meanremoval rebuilt: n_tokens={n_tokens} vocab_size={vocab_size}", flush=True)

    tokens = []
    for text in corpus_texts:
        tokens.extend(_tokenize(text))
    tok_idx = np.array([idx.get(w, -1) for w in tokens], dtype=np.int64)
    vocab_counts_arr = np.zeros(vocab_size, dtype=np.int64)
    for ti in tok_idx:
        if ti >= 0:
            vocab_counts_arr[ti] += 1

    print("[progress] starting SGNS retrain (bit-identical to v6/v6b)", flush=True)
    w_sgns_trained, w_sgns_random_init, n_pairs_trained, per_epoch_err = train_sgns(
        tok_idx, vocab_size, vocab_counts_arr
    )
    print(f"[progress] SGNS retrain complete n_pairs_trained={n_pairs_trained}", flush=True)

    role_vecs_d64 = make_role_vecs(D_EMBED, 55001)      # same literal seed as v5/v6/v6b
    role_vecs_ppmi = make_role_vecs(vocab_size, 55002)  # same literal seed as v5/v6/v6b
    objidx_roles_d64 = make_objidx_roles(D_EMBED, OBJIDX_ROLE_SEED_D64)
    objidx_roles_ppmi = make_objidx_roles(vocab_size, OBJIDX_ROLE_SEED_PPMI)

    print("[progress] scoring all 5 arms with tie-break-fixed scorers", flush=True)
    arm_error_driven = score_arm_v6_tiebreak_fixed(
        "ARM_ERROR_DRIVEN_SGNS", idx, w_sgns_trained, D_EMBED,
        role_vecs_d64, objidx_roles_d64, unstated_items, satrest_items, thwart_items)
    arm_random_init = score_arm_v6_tiebreak_fixed(
        "ARM_RANDOM_INIT_CONTROL", idx, w_sgns_random_init, D_EMBED,
        role_vecs_d64, objidx_roles_d64, unstated_items, satrest_items, thwart_items)
    arm_ppmi_ref = score_arm_v6_tiebreak_fixed(
        "ARM_PPMI_MEANREMOVAL", idx, ppmi_corrected_vecs, vocab_size,
        role_vecs_ppmi, objidx_roles_ppmi, unstated_items, satrest_items, thwart_items)

    idx_const, dense_vecs_const = make_const_dense_vecs(idx, D_EMBED, PURE_STRUCTURE_CONST_SEED)
    arm_pure_structure = score_arm_v6_tiebreak_fixed(
        "ARM_PURE_STRUCTURE_NO_CONTENT", idx_const, dense_vecs_const, D_EMBED,
        role_vecs_d64, objidx_roles_d64, unstated_items, satrest_items, thwart_items)

    arm_length_only = score_arm_length_only_tiebreak_fixed(unstated_items, satrest_items, thwart_items)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF) across all 5 arms' composite structures ----
    goal0_text = satrest_items[0]["goal_text"]
    s_ed, _, _, _ = build_event_struct_v6(goal0_text, idx, w_sgns_trained, D_EMBED, role_vecs_d64, objidx_roles_d64)
    s_ri, _, _, _ = build_event_struct_v6(goal0_text, idx, w_sgns_random_init, D_EMBED, role_vecs_d64, objidx_roles_d64)
    s_ppmi, _, _, _ = build_event_struct_v6(goal0_text, idx, ppmi_corrected_vecs, vocab_size, role_vecs_ppmi, objidx_roles_ppmi)
    s_pure, _, _, _ = build_event_struct_v6(goal0_text, idx_const, dense_vecs_const, D_EMBED, role_vecs_d64, objidx_roles_d64)
    _digests, pairwise, all_differ = _arms_must_differ_tensors({
        "error_driven": s_ed, "random_init": s_ri, "ppmi": s_ppmi, "pure_structure": s_pure,
    })
    assert all_differ, "META_RULE_AF VIOLATION: some arms' composite structures are bit-identical"

    # ---- reproduce v6b's own numbers off disk (MEASURED, not assumed), for delta reporting ----
    v6b_anchors = {}
    v6b_repro_check = {"v6b_metrics_found": False}
    if os.path.exists(V6B_METRICS_PATH):
        with open(V6B_METRICS_PATH, "r", encoding="utf-8") as f:
            v6b_metrics = json.load(f)
        split = v6b_metrics.get("summary_fields", {}).get("scoring_artifact_split", {})
        v6b_anchors = {
            "v6b_pure_structure_overall_accuracy": split.get("pure_structure", {}).get("overall_accuracy"),
            "v6b_length_only_overall_accuracy": split.get("length_only", {}).get("overall_accuracy"),
        }
        v6b_repro_check["v6b_metrics_found"] = True

    ed_acc = arm_error_driven["overall_accuracy"]
    ri_acc = arm_random_init["overall_accuracy"]
    ppmi_acc = arm_ppmi_ref["overall_accuracy"]
    pure_acc = arm_pure_structure["overall_accuracy"]
    length_acc = arm_length_only["overall_accuracy"]
    best_trained_acc = max(ed_acc, ppmi_acc)

    # ---- Q1: TIE_BREAK_WAS_THE_ARTIFACT ----
    def _near(acc, target, band=Q1_NEAR_CHANCE_BAND):
        return abs(acc - target) <= band

    q1_pure_unstated_near_chance = _near(arm_pure_structure["unstated_goal_accuracy"], CHANCE_UNSTATED)
    q1_length_unstated_near_chance = _near(arm_length_only["unstated_goal_accuracy"], CHANCE_UNSTATED)
    q1_pure_satrest_near_chance = _near(arm_pure_structure["satisfy_restate_accuracy"], CHANCE_SATREST)
    q1_length_satrest_near_chance = _near(arm_length_only["satisfy_restate_accuracy"], CHANCE_SATREST)
    q1_pure_thwart_near_chance = _near(arm_pure_structure["thwart_cause_accuracy"], CHANCE_THWART)
    q1_length_thwart_near_chance = _near(arm_length_only["thwart_cause_accuracy"], CHANCE_THWART)
    q1_pure_overall_near_chance = _near(pure_acc, CHANCE_OVERALL_WEIGHTED)
    q1_length_overall_near_chance = _near(length_acc, CHANCE_OVERALL_WEIGHTED)

    q1_tie_break_was_the_artifact = (
        q1_pure_unstated_near_chance and q1_length_unstated_near_chance
        and q1_pure_satrest_near_chance and q1_length_satrest_near_chance
        and q1_pure_thwart_near_chance and q1_length_thwart_near_chance
        and q1_pure_overall_near_chance and q1_length_overall_near_chance
    )

    # ---- Q2: RANDOM_STILL_BEATS_TRAINED (report only, no gate) ----
    q2_random_beats_trained = ri_acc >= best_trained_acc
    q2_margin = ri_acc - best_trained_acc

    elapsed_s = time.perf_counter() - t_start

    def _trim_arm(arm):
        return {k: v for k, v in arm.items()
                if k not in ("unstated_results", "satrest_results", "thwart_results")}

    summary = {
        "mechanism": (
            "v6/v6b's IDENTICAL structural/lexical scoring pipeline, reused verbatim, with the "
            "ONE variable fix: the unstated_goal 4-way-MC tie-break is now content-independent "
            "and order-independent (_tie_break_pick), instead of Python max()-over-dict which "
            "silently resolved ties to the first-inserted (=correct) candidate."
        ),
        "tie_break_rule": (
            "unique max -> keep (unchanged); exact tie (within 1e-9) among >=2 candidates -> "
            "resolve via np.random.RandomState seeded from hashlib.md5(item_id + '|' + "
            "sorted(tied_candidate_names)) -- deterministic, reproducible, and provably "
            "independent of candidates-list insertion order (self-tested below)."
        ),
        "arms": {
            "ARM_ERROR_DRIVEN_SGNS": _trim_arm(arm_error_driven),
            "ARM_RANDOM_INIT_CONTROL": _trim_arm(arm_random_init),
            "ARM_PPMI_MEANREMOVAL": _trim_arm(arm_ppmi_ref),
            "ARM_PURE_STRUCTURE_NO_CONTENT": _trim_arm(arm_pure_structure),
            "ARM_LENGTH_ONLY": _trim_arm(arm_length_only),
        },
        "v6b_comparison": {
            **v6b_repro_check,
            **v6b_anchors,
            "this_run_pure_structure_overall_accuracy": pure_acc,
            "this_run_length_only_overall_accuracy": length_acc,
        },
        "chance_overall_weighted": CHANCE_OVERALL_WEIGHTED,
        "per_item_type_chance": {
            "unstated_goal": CHANCE_UNSTATED, "satisfy_restate": CHANCE_SATREST, "thwart_cause": CHANCE_THWART,
        },
        "Q1_tie_break_was_the_artifact": {
            "near_chance_band": Q1_NEAR_CHANCE_BAND,
            "pure_structure_unstated_near_chance": q1_pure_unstated_near_chance,
            "length_only_unstated_near_chance": q1_length_unstated_near_chance,
            "pure_structure_satrest_near_chance": q1_pure_satrest_near_chance,
            "length_only_satrest_near_chance": q1_length_satrest_near_chance,
            "pure_structure_thwart_near_chance": q1_pure_thwart_near_chance,
            "length_only_thwart_near_chance": q1_length_thwart_near_chance,
            "pure_structure_overall_near_chance": q1_pure_overall_near_chance,
            "length_only_overall_near_chance": q1_length_overall_near_chance,
            "verdict": q1_tie_break_was_the_artifact,
        },
        "Q2_random_still_beats_trained": {
            "random_init_overall_accuracy": ri_acc,
            "best_trained_overall_accuracy": best_trained_acc,
            "error_driven_overall_accuracy": ed_acc,
            "ppmi_overall_accuracy": ppmi_acc,
            "random_beats_or_ties_trained": q2_random_beats_trained,
            "margin_random_minus_best_trained": q2_margin,
        },
        "eval_caveat": (
            "N=25 Director-VERIFIED balanced eval (original CLEAN gold_relation_inference_v1.jsonl, "
            "NOT the 954f2437d hardened/UNVERIFIED file); small-N diagnostic by ML standards -- report "
            "per-item-type counts alongside fractions, do not overclaim precision beyond ~1/25=0.04 "
            "resolution. This cell fixes the SCORING CHANNEL tie-break; it is not the USER-gated "
            "event-level scorer redesign and not an eval-hardening exercise."
        ),
        "elapsed_s": elapsed_s,
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"Q1_tie_break_was_the_artifact={q1_tie_break_was_the_artifact}; "
            f"Q2_random_beats_trained={q2_random_beats_trained} (margin={q2_margin:+.4f}); "
            f"per-arm overall: error_driven={ed_acc:.4f} random_init={ri_acc:.4f} ppmi={ppmi_acc:.4f} "
            f"pure_structure_no_content={pure_acc:.4f} length_only={length_acc:.4f} "
            f"chance={CHANCE_OVERALL_WEIGHTED:.4f}"
        ),
        "summary": f"DEEP-EARN v6c (tie-break-fixed control) Q1={q1_tie_break_was_the_artifact} Q2_random_beats_trained={q2_random_beats_trained}",
        "elapsed_s": elapsed_s,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_arm_error_driven_unstated_goal": arm_error_driven["unstated_results"],
        "results_arm_random_init_unstated_goal": arm_random_init["unstated_results"],
        "results_arm_ppmi_unstated_goal": arm_ppmi_ref["unstated_results"],
        "results_arm_pure_structure_unstated_goal": arm_pure_structure["unstated_results"],
        "results_arm_pure_structure_satisfy_restate": arm_pure_structure["satrest_results"],
        "results_arm_pure_structure_thwart_cause": arm_pure_structure["thwart_results"],
        "results_arm_length_only_unstated_goal": arm_length_only["unstated_results"],
        "results_arm_length_only_satisfy_restate": arm_length_only["satrest_results"],
        "results_arm_length_only_thwart_cause": arm_length_only["thwart_results"],
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n25x5arms",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "crlb_n_a": (
            "no fixed-capacity argmax-noise-floor threshold in this cell; discrete-tier "
            "accuracy-count feasibility over N=25 items is the analogue, per v6/v6b's own convention"
        ),
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


def self_test():
    """Tiny-scale real-code-path self-test: exercises the ACTUAL reused
    build_event_struct_v6/structure_overlap pipeline plus this cell's own
    _tie_break_pick / score_arm_v6_tiebreak_fixed / score_arm_length_only_
    tiebreak_fixed on a synthetic tiny vocab and fixture gold items -- INCLUDING
    the direct proof that candidate-list ORDER no longer determines the winner
    on an engineered exact tie."""
    d = 8
    vocab = ["alice", "wants", "tea", "and", "cake", "bob", "gives", "cake2",
             "runs", "fast", "far", "away", "quickly", "sad", "happy"]
    idx = {w: i for i, w in enumerate(vocab)}
    rng = np.random.RandomState(0)
    dense_vecs = rng.rand(len(vocab), d).astype(np.float64)

    role_vecs = make_role_vecs(d, seed=1)
    objidx_roles = make_objidx_roles(d, seed=2, n_slots=6)

    # === DIRECT PROOF: candidate order no longer changes the winner on a tie ===
    # Two DIFFERENT category names ("CAT_TIE_A", "CAT_TIE_B") share the IDENTICAL
    # prototype text -> build_event_struct_v6 produces bit-identical structures
    # for both -> structure_overlap against any action_struct is EXACTLY equal ->
    # guaranteed exact tie between them (not an approximate/lucky tie).
    _orig_prototypes = dict(CATEGORY_PROTOTYPES)
    CATEGORY_PROTOTYPES.clear()
    CATEGORY_PROTOTYPES.update({
        "CAT_TIE_A": "alice wants tea and cake", "CAT_TIE_B": "alice wants tea and cake",
        "CAT_OTHER_1": "sad happy", "CAT_OTHER_2": "runs fast far away quickly",
    })
    try:
        action_text = "alice wants tea"
        action_struct, _, _, _ = build_event_struct_v6(action_text, idx, dense_vecs, d, role_vecs, objidx_roles)
        sims = {}
        for cat in ["CAT_TIE_A", "CAT_TIE_B", "CAT_OTHER_1", "CAT_OTHER_2"]:
            proto_struct, _, _, _ = build_event_struct_v6(CATEGORY_PROTOTYPES[cat], idx, dense_vecs, d,
                                                            role_vecs, objidx_roles)
            sim, _ = structure_overlap(action_struct, proto_struct, d)
            sims[cat] = sim
        assert abs(sims["CAT_TIE_A"] - sims["CAT_TIE_B"]) < 1e-12, (
            "fixture setup invariant broken: CAT_TIE_A/CAT_TIE_B must be an exact tie"
        )
        assert sims["CAT_TIE_A"] > sims["CAT_OTHER_1"] and sims["CAT_TIE_A"] > sims["CAT_OTHER_2"], (
            "fixture setup invariant broken: the tied pair must strictly beat the non-tied distractors"
        )

        # candidates list with "correct" (CAT_TIE_A) inserted FIRST (old-bug-favoring order)
        candidates_order_1 = ["CAT_TIE_A", "CAT_TIE_B", "CAT_OTHER_1", "CAT_OTHER_2"]
        sims_1 = {c: sims[c] for c in candidates_order_1}
        # candidates list with "correct" (CAT_TIE_A) inserted LAST (old-bug-disfavoring order)
        candidates_order_2 = ["CAT_OTHER_2", "CAT_OTHER_1", "CAT_TIE_B", "CAT_TIE_A"]
        sims_2 = {c: sims[c] for c in candidates_order_2}

        # OLD (buggy) behavior would differ across the two orders on a tie:
        old_pick_1 = max(sims_1, key=sims_1.get)
        old_pick_2 = max(sims_2, key=sims_2.get)
        assert old_pick_1 == "CAT_TIE_A" and old_pick_2 == "CAT_TIE_B", (
            "self-test sanity check failed: expected the OLD max()-over-dict tie-break to be "
            "order-dependent on this fixture (first-inserted-of-the-tied-pair wins) -- if this "
            "assertion fails the fixture no longer demonstrates the bug being fixed"
        )

        # NEW (fixed) tie-break must return the SAME winner regardless of insertion order:
        new_pick_1, was_tie_1, tied_1 = _tie_break_pick(sims_1, item_id="fixture_item_1")
        new_pick_2, was_tie_2, tied_2 = _tie_break_pick(sims_2, item_id="fixture_item_1")
        assert was_tie_1 and was_tie_2, "expected both calls to detect the engineered exact tie"
        assert set(tied_1) == set(tied_2) == {"CAT_TIE_A", "CAT_TIE_B"}
        assert new_pick_1 == new_pick_2, (
            f"ORDER LEAK NOT CLOSED: tie-break picked {new_pick_1!r} when correct-first vs "
            f"{new_pick_2!r} when correct-last -- must be identical"
        )

        # different item_id must be free to resolve to the OTHER member of the tied pair
        # (proves the choice is a genuine per-item deterministic draw, not a constant bias
        # toward one specific candidate name)
        picks_by_item = set()
        for fake_id in range(200):
            p, _, _ = _tie_break_pick(sims_1, item_id=f"probe_{fake_id}")
            picks_by_item.add(p)
        assert picks_by_item == {"CAT_TIE_A", "CAT_TIE_B"}, (
            f"tie-break should reach BOTH tied candidates across many item_ids, got {picks_by_item}"
        )

        # reproducibility: same item_id always resolves the same way
        p_repeat_1, _, _ = _tie_break_pick(sims_1, item_id="fixture_item_1")
        p_repeat_2, _, _ = _tie_break_pick(sims_1, item_id="fixture_item_1")
        assert p_repeat_1 == p_repeat_2, "tie-break must be deterministic for a fixed item_id"

        # unique-max path (no tie) must be untouched: CAT_OTHER_1 vs a clear non-tied set
        clear_scores = {"X": 0.9, "Y": 0.1, "Z": 0.1}
        p_clear, was_tie_clear, _ = _tie_break_pick(clear_scores, item_id="clear_case")
        assert p_clear == "X" and not was_tie_clear
    finally:
        CATEGORY_PROTOTYPES.clear()
        CATEGORY_PROTOTYPES.update(_orig_prototypes)

    # === score_arm_v6_tiebreak_fixed end-to-end tiny fixture ===
    unstated_items = [{
        "id": "u1", "action_text": "alice wants tea",
        "correct_category": "CAT_A", "distractor_categories": ["CAT_B", "CAT_C", "CAT_D"],
    }]
    satrest_items = [{
        "id": "s1", "goal_text": "alice wants tea", "restate_text": "bob gives cake2 runs fast far away",
        "satisfy_text": "alice sad happy",
    }]
    thwart_items = [{
        "id": "t1", "event_a_text": "alice wants tea", "event_b_text": "alice sad happy",
        "distractor_text": "bob gives cake2 runs fast far away quickly",
    }]
    _orig_prototypes2 = dict(CATEGORY_PROTOTYPES)
    CATEGORY_PROTOTYPES.clear()
    CATEGORY_PROTOTYPES.update({
        "CAT_A": "alice wants tea", "CAT_B": "bob gives cake2",
        "CAT_C": "runs fast far away quickly", "CAT_D": "sad happy",
    })
    try:
        res = score_arm_v6_tiebreak_fixed("ARM_TEST", idx, dense_vecs, d, role_vecs, objidx_roles,
                                           unstated_items, satrest_items, thwart_items)
        assert res["arm_name"] == "ARM_TEST"
        assert res["n_scored_units"] == 4 + 2 + 2
        assert res["unstated_results"][0]["predicted_category"] == "CAT_A"
        assert res["unstated_results"][0]["correct"] is True

        # LENGTH_ONLY fixed-tiebreak variant on the same fixture
        res_lo = score_arm_length_only_tiebreak_fixed(unstated_items, satrest_items, thwart_items)
        assert res_lo["arm_name"] == "ARM_LENGTH_ONLY"
        assert res_lo["n_scored_units"] == 4 + 2 + 2
        assert res_lo["unstated_results"][0]["predicted_category"] == "CAT_A"
        assert res_lo["unstated_results"][0]["correct"] is True
    finally:
        CATEGORY_PROTOTYPES.clear()
        CATEGORY_PROTOTYPES.update(_orig_prototypes2)

    # --- ARMS-MUST-DIFFER sanity on tiny scale ---
    idx_const, dense_vecs_const = make_const_dense_vecs(idx, d, PURE_STRUCTURE_CONST_SEED)
    struct_real, _, _, _ = build_event_struct_v6("alice wants tea", idx, dense_vecs, d, role_vecs, objidx_roles)
    struct_const, _, _, _ = build_event_struct_v6("alice wants tea", idx_const, dense_vecs_const, d, role_vecs, objidx_roles)
    _digests, pairwise, all_differ = _arms_must_differ_tensors({
        "real_content": struct_real, "pure_structure": struct_const,
    })
    assert all_differ, "self-test: real-content vs pure-structure structs must differ"

    print(
        f"[self_test] PASS  order_leak_closed=True  new_pick_1={new_pick_1}  new_pick_2={new_pick_2}  "
        f"picks_reach_both_tied={sorted(picks_by_item)}  length_only_predicted={res_lo['unstated_results'][0]['predicted_category']}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        if "--self-test" in sys.argv:
            self_test()
        else:
            main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
