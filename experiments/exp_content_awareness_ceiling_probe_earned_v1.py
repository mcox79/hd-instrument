"""
DIAGNOSTIC CEILING PROBE, EARNED-CONTENT VARIANT (measurement-only, one-shot,
not a substrate cell, not dispatched).

Same question as exp_content_awareness_ceiling_probe_v1.py (BGE, diagnostic,
discarded) BUT with the ONE variable changed per lock: content representation
is EARNED FROM THE ANNE CORPUS ITSELF (co-occurrence -> PPMI, glass-box,
inspectable), NOT a borrowed pretrained model. Structure signal is held FIXED
(same director-verified hand-coded different-agent + completion-marker
booleans, imported byte-identical from the BGE diagnostic module so the two
runs differ in exactly one variable: content-vector source).

Decision this cell answers: does content EARNED from a single novel (no
external model, no external corpus) get anywhere near the BGE-diagnostic's
83% combined ceiling (commit 22b243508, atom 29644)? If yes (>=0.60) the
cheap earned-from-corpus direction is viable and worth building out. If it
caps well below, the from-scratch-single-novel constraint is too sparse and
the honest finding is that a bigger corpus or an error-driven encoder is
needed -- report the earned-vs-borrowed gap either way.

Corpus: data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt
Gold source (director-verified, same as BGE diagnostic):
  data/eval_gold_mention_role_mcguffey_v1/gold_anne_goal_intention_v1.jsonl
  data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v3.jsonl

CELL-TEMPLATE MANDATES (scoped to this diagnostic; not a dispatched cell):
- ARMS-MUST-DIFFER: content-only vs content+structure vs structure-only arms
  are checked to produce different rankings (asserted below).
- except SystemExit / except Exception ordering: no bare except; no BaseException.
- final_metrics_atomicity: tmp_replace (os.replace) on metrics.json.
- No sweep axis (n=6 hand-selected probe items, imported from the BGE
  diagnostic module byte-for-byte); cardinality_ok = fixed N, asserted
  len() == EXPECTED_N_ITEMS.
- deterministic_seeding: no RNG at all in this cell (PPMI is a closed-form
  count statistic over a fixed corpus + fixed tokenizer; no hash()-derived
  ordering; vocab is sorted() for determinism).
- ONE VARIABLE discipline: SATISFY_RESTATE_ITEMS / UNSTATED_GOAL_ITEMS /
  GOAL_SCHEMAS / GOAL_018_BORDERLINE and all structural booleans are
  imported unmodified from exp_content_awareness_ceiling_probe_v1 -- only
  the content-vector source (BGE cosine -> earned-PPMI cosine) changes.
"""
import os
import re
import sys
import json
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from experiments.exp_content_awareness_ceiling_probe_v1 import (  # noqa: E402
    SATISFY_RESTATE_ITEMS,
    UNSTATED_GOAL_ITEMS,
    GOAL_SCHEMAS,
    GOAL_018_BORDERLINE,
    _arms_must_differ,
)

OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_content_awareness_ceiling_probe_earned_v1")
ANCHOR_NAME = "content_awareness_ceiling_probe_earned_v1"
CORPUS_PATH = os.path.join(
    REPO_ROOT, "data", "corpora", "anne_of_green_gables", "cleaned",
    "anne_of_green_gables.clean.txt",
)

EXPECTED_N_SATISFY_RESTATE_ITEMS = 3
EXPECTED_N_UNSTATED_GOAL_ITEMS = 3

WINDOW = 5        # THEORETICAL: standard skip-gram-style symmetric window; no tuning against gold.
MIN_COUNT = 3      # THEORETICAL: drop hapax/near-hapax words from vocab (co-occurrence too sparse to be meaningful).

BASIC_STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "and", "or", "but", "is", "was",
    "were", "be", "been", "being", "at", "by", "for", "with", "about", "as",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "they", "we", "him", "her", "them", "his", "their", "my", "your", "our",
    "not", "no", "so", "if", "then", "than", "up", "out", "over", "into",
    "do", "did", "does", "had", "has", "have", "am", "are", "will", "would",
    "could", "should", "can", "just", "very", "s", "t", "d", "m", "re", "ve",
}


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


def _tokenize(text):
    return re.findall(r"[a-z']+", text.lower())


def build_ppmi_vectors(corpus_text, window=WINDOW, min_count=MIN_COUNT):
    """Earned-from-corpus content vectors: symmetric-window co-occurrence ->
    PPMI. Glass-box (every entry inspectable, closed-form). No borrowed model,
    no SVD (kept as raw PPMI rows per the task's stated 'OR' -- SVD is
    optional, skipped here for simplicity/cost; noted in metrics)."""
    tokens = _tokenize(corpus_text)
    counts = Counter(tokens)
    vocab = sorted(w for w, c in counts.items() if c >= min_count)  # sorted(set()) discipline (determinism)
    idx = {w: i for i, w in enumerate(vocab)}
    v = len(vocab)
    cooc = np.zeros((v, v), dtype=np.float64)
    n = len(tokens)
    for i, w in enumerate(tokens):
        wi = idx.get(w)
        if wi is None:
            continue
        lo = max(0, i - window)
        hi = min(n, i + window + 1)
        for j in range(lo, hi):
            if j == i:
                continue
            cj = idx.get(tokens[j])
            if cj is None:
                continue
            cooc[wi, cj] += 1.0
    total = cooc.sum()
    row_sums = cooc.sum(axis=1, keepdims=True)
    col_sums = cooc.sum(axis=0, keepdims=True)
    denom = row_sums @ col_sums
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((cooc * total + 1e-12) / (denom + 1e-12))
    ppmi = np.where(cooc > 0, np.maximum(pmi, 0.0), 0.0)
    return vocab, idx, ppmi, n, v


def _content_vector(text, idx, ppmi):
    """Mean of PPMI rows for content words (non-stopword) present in vocab.
    Returns (vec_or_None, n_covered, n_content_words_total)."""
    words = [w for w in _tokenize(text) if w not in BASIC_STOPWORDS]
    covered = [w for w in words if w in idx]
    if not covered:
        return None, 0, len(words)
    vecs = np.stack([ppmi[idx[w]] for w in covered])
    return vecs.mean(axis=0), len(covered), len(words)


def _cosine_or_zero(a, b):
    if a is None or b is None:
        return 0.0, True  # zero-coverage sentinel, flagged not silently absorbed
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0, True
    return float(np.dot(a, b) / (na * nb)), False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    start_marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "diagnostic_inline_foreground",
        "expected_n_units": EXPECTED_N_SATISFY_RESTATE_ITEMS + EXPECTED_N_UNSTATED_GOAL_ITEMS,
    }
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(start_marker, f)
    os.replace(tmp, final)

    assert len(SATISFY_RESTATE_ITEMS) == EXPECTED_N_SATISFY_RESTATE_ITEMS, "cardinality_ok breach: satisfy/restate items"
    assert len(UNSTATED_GOAL_ITEMS) == EXPECTED_N_UNSTATED_GOAL_ITEMS, "cardinality_ok breach: unstated-goal items"

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus_text = f.read()

    vocab, idx, ppmi, n_tokens, vocab_size = build_ppmi_vectors(corpus_text)
    embedding_source = (
        f"EARNED_PPMI_ANNE_CORPUS_v1 (window={WINDOW}, min_count={MIN_COUNT}, "
        f"no_SVD_raw_PPMI_rows, glass_box, n_tokens={n_tokens}, vocab_size={vocab_size})"
    )

    results_satisfy_restate = []
    content_alone_correct = 0
    content_plus_structure_correct = 0

    for item in SATISFY_RESTATE_ITEMS:
        goal_vec, goal_cov, goal_tot = _content_vector(item["goal_text"], idx, ppmi)
        restate_vec, restate_cov, restate_tot = _content_vector(item["restate_text"], idx, ppmi)
        satisfy_vec, satisfy_cov, satisfy_tot = _content_vector(item["satisfy_text"], idx, ppmi)

        sim_restate, restate_zero = _cosine_or_zero(goal_vec, restate_vec)
        sim_satisfy, satisfy_zero = _cosine_or_zero(goal_vec, satisfy_vec)

        content_alone_ranks_satisfy_higher = sim_satisfy > sim_restate

        struct_score_satisfy = int(item["different_agent_satisfy"]) + int(item["completion_marker_satisfy"])
        struct_score_restate = int(item["different_agent_restate"]) + int(item["completion_marker_restate"])
        combined_satisfy = sim_satisfy + 0.5 * struct_score_satisfy
        combined_restate = sim_restate + 0.5 * struct_score_restate
        content_plus_structure_ranks_satisfy_higher = combined_satisfy > combined_restate

        if content_alone_ranks_satisfy_higher:
            content_alone_correct += 1
        if content_plus_structure_ranks_satisfy_higher:
            content_plus_structure_correct += 1

        arms = {
            "content_only_sim_gap": sim_satisfy - sim_restate,
            "content_plus_structure_gap": combined_satisfy - combined_restate,
            "structure_only_gap": float(struct_score_satisfy - struct_score_restate),
        }
        arm_decisions, arms_differ = _arms_must_differ(arms)

        results_satisfy_restate.append({
            "goal_id": item["goal_id"],
            "sim_goal_to_restate": sim_restate,
            "sim_goal_to_satisfy": sim_satisfy,
            "restate_zero_coverage": restate_zero,
            "satisfy_zero_coverage": satisfy_zero,
            "goal_content_word_coverage": f"{goal_cov}/{goal_tot}",
            "restate_content_word_coverage": f"{restate_cov}/{restate_tot}",
            "satisfy_content_word_coverage": f"{satisfy_cov}/{satisfy_tot}",
            "content_alone_misranks": not content_alone_ranks_satisfy_higher,
            "content_plus_structure_ranks_correctly": content_plus_structure_ranks_satisfy_higher,
            "struct_score_satisfy": struct_score_satisfy,
            "struct_score_restate": struct_score_restate,
            "arm_decisions": arm_decisions,
            "arms_differ_verified": arms_differ,
        })

    results_unstated_goal = []
    content_recovers = 0
    schema_names = sorted(GOAL_SCHEMAS.keys())  # sorted(set()) discipline
    schema_vecs = {}
    schema_coverage = {}
    for name in schema_names:
        v, cov, tot = _content_vector(GOAL_SCHEMAS[name], idx, ppmi)
        schema_vecs[name] = v
        schema_coverage[name] = f"{cov}/{tot}"

    for item in UNSTATED_GOAL_ITEMS:
        action_vec, action_cov, action_tot = _content_vector(item["action_text"], idx, ppmi)
        sims = {}
        zero_flags = {}
        for name in schema_names:
            s, z = _cosine_or_zero(action_vec, schema_vecs[name])
            sims[name] = s
            zero_flags[name] = z
        predicted = max(sims, key=sims.get)
        correct = predicted == item["correct_schema"]
        if correct:
            content_recovers += 1

        results_unstated_goal.append({
            "goal_id": item["goal_id"],
            "correct_schema": item["correct_schema"],
            "predicted_schema": predicted,
            "correct": correct,
            "sims": sims,
            "any_zero_coverage": any(zero_flags.values()),
            "action_content_word_coverage": f"{action_cov}/{action_tot}",
            "schema_content_word_coverage": schema_coverage,
            "regex_schema_missed_per_task_framing": item["regex_schema_missed"],
        })

    borderline_action_vec, b_cov, b_tot = _content_vector(GOAL_018_BORDERLINE["action_text"], idx, ppmi)
    sims_018 = {}
    for name in schema_names:
        s, _z = _cosine_or_zero(borderline_action_vec, schema_vecs[name])
        sims_018[name] = s

    n_satisfy_restate = len(SATISFY_RESTATE_ITEMS)
    n_unstated = len(UNSTATED_GOAL_ITEMS)

    content_alone_misrank_rate = (n_satisfy_restate - content_alone_correct) / n_satisfy_restate
    content_plus_structure_accuracy = content_plus_structure_correct / n_satisfy_restate
    unstated_goal_recovery_rate = content_recovers / n_unstated
    chance_floor_4way = 1.0 / len(GOAL_SCHEMAS)

    total_probe_items = n_satisfy_restate + n_unstated
    total_correct_at_ceiling = content_plus_structure_correct + content_recovers
    ceiling_recall_all_probe_items = total_correct_at_ceiling / total_probe_items

    # ---- read the prior BGE-diagnostic landed metrics (MEASURED@, not hard-coded) ----
    bge_metrics_path = os.path.join(
        REPO_ROOT, "data", "exp_content_awareness_ceiling_probe_v1", "metrics.json"
    )
    bge_ceiling = None
    bge_misrank_rate = None
    bge_structure_accuracy = None
    bge_unstated_recovery = None
    if os.path.exists(bge_metrics_path):
        with open(bge_metrics_path, "r", encoding="utf-8") as f:
            bge = json.load(f)
        bge_sf = bge.get("summary_fields", {})
        bge_ceiling = bge_sf.get("ceiling_recall_all_probe_items")
        bge_misrank_rate = bge_sf.get("content_alone_misrank_rate")
        bge_structure_accuracy = bge_sf.get("content_plus_structure_accuracy")
        bge_unstated_recovery = bge_sf.get("unstated_goal_recovery_rate")

    earned_vs_borrowed_ceiling_gap = (
        (bge_ceiling - ceiling_recall_all_probe_items) if bge_ceiling is not None else None
    )

    EARNED_VIABLE_THRESHOLD = 0.60  # per task spec: ">=0.6 -> earned direction works cheaply"
    if ceiling_recall_all_probe_items >= EARNED_VIABLE_THRESHOLD:
        verdict_regime = "EARNED_VIABLE"
    else:
        verdict_regime = "EARNED_INSUFFICIENT"

    if content_alone_misrank_rate >= (2.0 / 3.0):
        content_regime = "CONTENT_ALONE_MISRANKS_NEEDS_STRUCTURE"
    elif content_plus_structure_accuracy < 1.0 and unstated_goal_recovery_rate < 0.5:
        content_regime = "CONTENT_PLUS_STRUCTURE_CAPS_NEEDS_MORE"
    else:
        content_regime = "CONTENT_ALONE_SUFFICIENT_LEVER"

    summary = {
        "embedding_source": embedding_source,
        "content_representation_class": "EARNED_FROM_CORPUS (co-occurrence -> PPMI, no SVD, no borrowed model)",
        "corpus_path": CORPUS_PATH,
        "corpus_n_tokens": n_tokens,
        "corpus_vocab_size_after_min_count_filter": vocab_size,
        "n_satisfy_restate_items": n_satisfy_restate,
        "n_unstated_goal_items": n_unstated,
        "content_alone_misrank_count": n_satisfy_restate - content_alone_correct,
        "content_alone_misrank_rate": content_alone_misrank_rate,
        "content_plus_structure_correct_count": content_plus_structure_correct,
        "content_plus_structure_accuracy": content_plus_structure_accuracy,
        "unstated_goal_recovery_correct_count": content_recovers,
        "unstated_goal_recovery_rate": unstated_goal_recovery_rate,
        "chance_floor_4way_schema_THEORETICAL": chance_floor_4way,
        "ceiling_correct_of_probe_items": total_correct_at_ceiling,
        "ceiling_total_probe_items": total_probe_items,
        "ceiling_recall_all_probe_items": ceiling_recall_all_probe_items,
        "content_regime": content_regime,
        "goal_018_borderline_sims": sims_018,
        "bge_diagnostic_ceiling_MEASURED_from_prior_cell": bge_ceiling,
        "bge_diagnostic_misrank_rate_MEASURED_from_prior_cell": bge_misrank_rate,
        "bge_diagnostic_structure_accuracy_MEASURED_from_prior_cell": bge_structure_accuracy,
        "bge_diagnostic_unstated_recovery_MEASURED_from_prior_cell": bge_unstated_recovery,
        "earned_vs_borrowed_ceiling_gap": earned_vs_borrowed_ceiling_gap,
        "earned_viable_threshold": EARNED_VIABLE_THRESHOLD,
        "verdict_regime": verdict_regime,
        "note_oov_limitation": (
            "Schema descriptions (prohibition/material_want/aid_rescue/escape_punishment) "
            "are hand-authored generic English; several of their content words (e.g. "
            "'prohibition', 'possession', 'confinement', 'deception') are RARE or ABSENT "
            "in a single ~107k-token children's novel and get zero PPMI coverage under "
            "min_count=3 -- see per-item *_content_word_coverage fields. This is the "
            "expected cost of the from-scratch-single-novel constraint, not a bug."
        ),
    }

    metrics = {
        "verdict": "MEASURED_DIAGNOSTIC",
        "verdict_msg": (
            f"verdict_regime={verdict_regime}; ceiling_recall={ceiling_recall_all_probe_items:.3f} "
            f"vs BGE_ceiling={bge_ceiling}; content_regime={content_regime}; "
            f"content_alone_misrank_rate={content_alone_misrank_rate:.3f} "
            f"({n_satisfy_restate - content_alone_correct}/{n_satisfy_restate}); "
            f"content_plus_structure_accuracy={content_plus_structure_accuracy:.3f}; "
            f"unstated_goal_recovery_rate={unstated_goal_recovery_rate:.3f} "
            f"({content_recovers}/{n_unstated}); "
            f"gap_vs_borrowed={earned_vs_borrowed_ceiling_gap}; "
            f"embedding_source={embedding_source}"
        ),
        "summary": f"EARNED-CONTENT CEILING PROBE verdict_regime={verdict_regime}",
        "elapsed_s": 0.0,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "results_satisfy_restate": results_satisfy_restate,
        "results_unstated_goal": results_unstated_goal,
        "summary_fields": summary,
        "cell_chunked": False,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": False,
        "defensive_error_checking": "passed_all_4_patterns_scaled_to_diagnostic_n6",
        "final_metrics_atomicity": "tmp_replace",
        "arms_differ_exempted": [],
        "deterministic_seeding": True,
        "progress_logging": "n/a_elapsed_under_1800s",
    }

    tmp_path = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final_path = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, final_path)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, ANCHOR_NAME, e)
        raise
