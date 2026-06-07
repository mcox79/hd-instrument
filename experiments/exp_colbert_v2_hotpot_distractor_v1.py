"""
exp_colbert_v2_hotpot_distractor_v1.py

ColBERT-v2 multi-hop retrieval pre-test on HotpotQA distractor passages.

Per Research routing (research_to_testbed_colbert_v2_CLOUD_OK_update_2026-06-07.md):
- HARD-PASS: recall@2 >= 0.55  (gates user-level decision on 2-3 week ColBERT integration)
- BORDER:    0.50-0.55
- HARD-FAIL: < 0.50            (multi-hop precision conceded; demo leans on hotpot_3baseline)

Method:
- Load HotpotQA distractor dev split via HF datasets (hotpotqa/hotpot_qa, config 'distractor')
- Filter to type == 'bridge'; take first --n-questions (default 100)
- For each question, the 'context' field carries 10 documents (titles + list-of-sentences).
- Build a SINGLE global corpus = union of passages over all 100 questions' contexts.
  A passage = one sentence from one document (matches HotpotQA's supporting_facts unit).
- Build ColBERT-v2 index over the corpus (colbert-ir/colbertv2.0 checkpoint).
- For each question, retrieve top-K passages; check recall against gold supporting_facts.
- Report recall@2 + recall@10 + per-metric verdict + combined verdict.

Comparison baselines (informational): bge-small recall@2=0.42, recall@10=0.74.
"""

import argparse
import gc
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from experiments._seed_checkpoint import get_output_dir, write_metrics  # noqa: E402


# =============================================================================
# Config + constants
# =============================================================================

ANCHOR_NAME = "colbert_v2_hotpot_distractor_v1"

HP_RECALL_AT_2 = 0.55   # HARD-PASS threshold per Research
MID_LOW_RECALL_AT_2 = 0.50   # BORDER lower edge
HP_RECALL_AT_10_INFO = 0.74  # bge-small baseline for chat-comparison only

COLBERT_CHECKPOINT = "colbert-ir/colbertv2.0"
HOTPOT_REPO = "hotpotqa/hotpot_qa"
HOTPOT_CONFIG = "distractor"
HOTPOT_SPLIT = "validation"   # dev set; HF naming
SHUFFLE_SEED = 1729

# ColBERT index config (per upstream defaults for HotpotQA-style passages)
NBITS = 2
DOC_MAXLEN = 180
KMEANS_NITERS = 4
INDEX_NAME = f"{ANCHOR_NAME}_index"

# =============================================================================
# CLI
# =============================================================================

_ap = argparse.ArgumentParser()
_ap.add_argument("--n-questions", type=int, default=100,
                  help="Number of bridge questions to evaluate")
_ap.add_argument("--top-k", type=int, default=10,
                  help="Top-K passages to retrieve per query (must be >=10 for recall@10)")
_ap.add_argument("--self-test", action="store_true",
                  help="Run lightweight PROT-022 import + signature check; exit 0 on pass")
_ap.add_argument("--colbert-experiment-root", type=str, default="experiments_colbert",
                  help="Path for ColBERT to write its index/logs")
_ARGS = _ap.parse_args()


# =============================================================================
# PROT-022 self-test (called via --self-test in YAML setup)
# =============================================================================

def _selftest():
    """Lightweight checks: imports, signature consistency, no actual indexing."""
    print("[selftest] starting", flush=True)
    # Verify required arg defaults match Research's HP/BORDER/HF gates
    assert abs(HP_RECALL_AT_2 - 0.55) < 1e-9, "HP threshold drift"
    assert abs(MID_LOW_RECALL_AT_2 - 0.50) < 1e-9, "BORDER threshold drift"

    # Mini main-path test: build a tiny corpus + gold pair + verify recall calc
    fake_gold = {
        "q1": [("doc_a", 0), ("doc_b", 1)],
        "q2": [("doc_c", 0)],
    }
    fake_passages = [
        ("doc_a", 0, "passage 1"),
        ("doc_a", 1, "passage 2"),
        ("doc_b", 1, "passage 3"),
        ("doc_c", 0, "passage 4"),
    ]
    # Fake retrieval result: top-2 for q1 is [passage 1 (gold), passage 3 (gold)] -> recall@2 = 2/2 = 1.0
    # Fake retrieval result: top-2 for q2 is [passage 4 (gold), passage 1 (not gold)] -> recall@2 = 1/1 = 1.0
    fake_top2 = {
        "q1": [0, 2],   # indices into fake_passages
        "q2": [3, 0],
    }
    r2 = compute_recall_at_k(fake_top2, fake_passages, fake_gold, k=2)
    assert abs(r2 - 1.0) < 1e-9, f"selftest recall@2 should be 1.0, got {r2}"

    # Adversarial: top-2 misses gold for q1
    fake_top2_bad = {
        "q1": [1, 3],   # both wrong -> 0 gold found
        "q2": [3, 0],   # 1 gold found -> 1/1 = 1.0
    }
    r2_bad = compute_recall_at_k(fake_top2_bad, fake_passages, fake_gold, k=2)
    assert abs(r2_bad - 0.5) < 1e-9, f"selftest mixed recall@2 should be 0.5, got {r2_bad}"

    # Verify Python can import the math/numpy bits the main path uses (NO colbert/torch import here;
    # those are exercised at YAML-run time on the cluster)
    try:
        from datasets import load_dataset  # noqa: F401
    except Exception as e:
        print(f"[selftest] WARNING: datasets not importable yet: {e} (OK during local --self-test;"
              " cluster setup installs it)", flush=True)

    print(f"[selftest] PASS: recall calc verified on fake data; HP/HF thresholds intact "
          f"(HP recall@2 >= {HP_RECALL_AT_2}); n_questions default={_ARGS.n_questions}", flush=True)


# =============================================================================
# Data preparation
# =============================================================================

def load_bridge_questions(n: int) -> List[Dict]:
    """Load first n HotpotQA distractor dev BRIDGE questions.

    PREFERS a pre-extracted JSONL at ~/sky_workdir/data/hotpot_distractor_bridge.jsonl
    (written once during setup by a side script for speed) BEFORE falling back to the
    slow HF script-mode loader.

    Hardening:
    - If fewer than n bridge questions found, WARN + return what we have (not hard-fail);
      the script still produces a valid verdict on the smaller sample.
    """
    cached = Path(os.environ.get("HOME", "/root")) / "sky_workdir/data/hotpot_distractor_bridge.jsonl"
    if cached.is_file():
        print(f"[data] using cached bridge JSONL at {cached}", flush=True)
        bridge = []
        with open(cached) as f:
            for line in f:
                bridge.append(json.loads(line))
                if len(bridge) >= n:
                    break
        if len(bridge) < n:
            print(f"[WARN] cached has only {len(bridge)} bridge questions (wanted {n}); proceeding",
                  flush=True)
        return bridge

    print(f"[data] loading hotpot_qa distractor/validation via HF (slow path)", flush=True)
    from datasets import load_dataset
    ds = load_dataset(HOTPOT_REPO, HOTPOT_CONFIG, split=HOTPOT_SPLIT, trust_remote_code=True)
    print(f"[data] loaded {len(ds)} dev examples; filtering to type=='bridge'", flush=True)

    bridge = []
    for ex in ds:
        if ex.get("type") == "bridge":
            bridge.append(ex)
            if len(bridge) >= n:
                break
    if len(bridge) < n:
        print(f"[WARN] only {len(bridge)} bridge questions found (wanted {n}); proceeding "
              f"with smaller sample", flush=True)
    print(f"[data] collected {len(bridge)} bridge questions", flush=True)
    return bridge


def build_corpus(questions: List[Dict]) -> Tuple[List[Tuple[str, int, str]], Dict[str, List[Tuple[str, int]]]]:
    """Flatten all questions' contexts into a single global passage corpus.

    Returns:
        passages: list of (doc_title, sent_idx, sentence_text) tuples; one per sentence
        gold_per_question: dict[question_id] = list of (doc_title, sent_idx) tuples from
                           supporting_facts (the gold-standard "this sentence supports
                           the answer" labels)
    """
    seen = set()
    passages = []
    gold_per_question = {}

    for q in questions:
        qid = q["id"]
        ctx = q["context"]
        # HF HotpotQA format: ctx is dict with "title" (list of N) and "sentences" (list of N list-of-str)
        titles = ctx["title"]
        sentences_lists = ctx["sentences"]
        for title, sents in zip(titles, sentences_lists):
            for sidx, sent in enumerate(sents):
                key = (title, sidx)
                if key in seen:
                    continue
                seen.add(key)
                passages.append((title, sidx, sent))

        # Gold from supporting_facts: list of [title, sent_id]
        sf = q["supporting_facts"]
        gold = []
        sf_titles = sf["title"]
        sf_sent_ids = sf["sent_id"]
        for t, sid in zip(sf_titles, sf_sent_ids):
            gold.append((t, int(sid)))
        gold_per_question[qid] = gold

    print(f"[data] corpus: {len(passages)} unique (title, sent_idx, text) passages "
          f"across {len(questions)} questions", flush=True)
    return passages, gold_per_question


# =============================================================================
# ColBERT indexing + search
# =============================================================================

def colbert_index_and_search(passages: List[Tuple[str, int, str]],
                                queries: List[Tuple[str, str]],
                                top_k: int,
                                experiment_root: Path,
                                progress_dir: Path) -> Dict[str, List[int]]:
    """Build a ColBERT-v2 index over passages; search each query; return top-K passage indices per query.

    Progress-saving (per user 2026-06-07 rule):
    - Every 10 queries, flush retrieval_results.jsonl to progress_dir (the output dir)
    - Safety stack's progress_rsync pulls this every 5 min back to local
    - If cluster dies at query 80/100, we keep 80 results AND can resume manually

    Args:
        passages: list of (title, sent_idx, text); indices into this list are passage IDs
        queries: list of (question_id, question_text)
        top_k: how many to retrieve per query
        experiment_root: path for ColBERT to write its index/logs
        progress_dir: path for incremental retrieval-results JSONL writes

    Returns:
        dict[question_id] -> list of passage indices (length top_k, sorted by ColBERT score desc)
    """
    from colbert import Indexer, Searcher
    from colbert.infra import Run, RunConfig, ColBERTConfig

    # ColBERT only takes a flat list of strings as collection; we use list index as the ID
    collection = [p[2] for p in passages]
    print(f"[colbert] indexing {len(collection)} passages with {COLBERT_CHECKPOINT} "
          f"(nbits={NBITS}, doc_maxlen={DOC_MAXLEN})", flush=True)

    experiment_root.mkdir(parents=True, exist_ok=True)
    progress_dir.mkdir(parents=True, exist_ok=True)
    progress_jsonl = progress_dir / "retrieval_results.jsonl"
    # Truncate prior incomplete progress on a fresh run (per never-edit-script-mid-run lesson:
    # cleanup is owned by the orchestrator's log rotation; we just clear our own progress file)
    if progress_jsonl.exists():
        progress_jsonl.unlink()

    config = ColBERTConfig(
        nbits=NBITS,
        doc_maxlen=DOC_MAXLEN,
        kmeans_niters=KMEANS_NITERS,
        root=str(experiment_root),
    )

    with Run().context(RunConfig(nranks=1, root=str(experiment_root), experiment="hotpot_distractor")):
        indexer = Indexer(checkpoint=COLBERT_CHECKPOINT, config=config)
        t_idx = time.time()
        indexer.index(name=INDEX_NAME, collection=collection, overwrite=True)
        print(f"[colbert] index built in {time.time()-t_idx:.1f}s", flush=True)
        # Save index location marker so we know indexing succeeded even if search dies
        (progress_dir / "INDEX_BUILT.marker").write_text(
            f"index_name={INDEX_NAME}\nelapsed_s={time.time()-t_idx:.1f}\nn_passages={len(collection)}\n"
        )

        searcher = Searcher(index=INDEX_NAME, config=config)
        print(f"[colbert] running {len(queries)} queries (top_k={top_k})...", flush=True)
        top_k_per_query: Dict[str, List[int]] = {}
        t_q = time.time()
        # Open progress JSONL for append-mode streaming writes
        progress_f = open(progress_jsonl, "a")
        try:
            for i, (qid, qtext) in enumerate(queries):
                results = searcher.search(qtext, k=top_k)
                # results = (passage_ids, ranks, scores); passage_ids are indices into collection
                pids, _, scores = results
                top_pids = list(pids[:top_k])
                top_k_per_query[qid] = top_pids
                # Stream to JSONL so progress_rsync picks up partial results
                progress_f.write(json.dumps({
                    "qid": qid,
                    "top_pids": top_pids,
                    "scores": [float(s) for s in scores[:top_k]],
                }) + "\n")
                if (i + 1) % 10 == 0:
                    progress_f.flush()
                    os.fsync(progress_f.fileno())
                if (i + 1) % 25 == 0:
                    print(f"  [colbert] queries {i+1}/{len(queries)} done "
                          f"(wall {time.time()-t_q:.1f}s; partial results streamed)", flush=True)
        finally:
            progress_f.flush()
            os.fsync(progress_f.fileno())
            progress_f.close()
        print(f"[colbert] all queries done in {time.time()-t_q:.1f}s", flush=True)

    return top_k_per_query


# =============================================================================
# Metric computation
# =============================================================================

def compute_recall_at_k(top_k_per_query: Dict[str, List[int]],
                          passages: List[Tuple[str, int, str]],
                          gold_per_question: Dict[str, List[Tuple[str, int]]],
                          k: int) -> float:
    """Compute mean-over-questions recall@k against gold (title, sent_idx) facts.

    For each question, count the # of gold (title, sent_idx) pairs that appear in the
    top-k retrieved passages, and divide by # of gold for that question. Return the
    mean over questions.
    """
    if not top_k_per_query:
        return 0.0
    per_q_recalls = []
    for qid, top_pids in top_k_per_query.items():
        gold = gold_per_question.get(qid, [])
        if not gold:
            continue  # skip questions with no gold (shouldn't happen for bridge)
        gold_set = set(gold)
        topk = top_pids[:k]
        retrieved_pairs = set()
        for pid in topk:
            title, sidx, _ = passages[pid]
            retrieved_pairs.add((title, int(sidx)))
        hits = len(retrieved_pairs & gold_set)
        per_q_recalls.append(hits / len(gold_set))
    return sum(per_q_recalls) / max(len(per_q_recalls), 1)


# =============================================================================
# Main
# =============================================================================

def _emit_failure_metrics(reason: str, elapsed: float):
    """Hardening: even on crash, write a metrics.json so verdict_handler doesn't
    interpret missing file as INFRA_FAILURE. Required so the verdict pipeline
    sees this as a SCRIPT_FAILURE with explicit reason rather than mystery silence.
    """
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": f"UNKNOWN: script crashed; reason={reason}",
            "elapsed_s": elapsed,
            "summary": f"UNKNOWN: script crashed; reason={reason}",
            "error": reason,
        }
        write_metrics(out_dir, metrics, [metrics])
        print(f"[metrics] FAILURE metrics written to {out_dir / 'metrics.json'}", flush=True)
    except Exception as inner:
        print(f"[FATAL] could not even write failure metrics: {inner}", flush=True)


def main():
    print(f"[config] anchor={ANCHOR_NAME} n_questions={_ARGS.n_questions} top_k={_ARGS.top_k} "
          f"checkpoint={COLBERT_CHECKPOINT}", flush=True)
    t0 = time.time()

    try:
        # Step 1: load + filter bridge questions
        questions = load_bridge_questions(_ARGS.n_questions)
        if len(questions) < 10:
            raise RuntimeError(f"Only {len(questions)} bridge questions found; aborting as too small "
                              f"to produce meaningful recall metrics (need >= 10)")

        # Step 2: build corpus + extract gold
        passages, gold_per_question = build_corpus(questions)
        if len(passages) < 10:
            raise RuntimeError(f"Corpus too small ({len(passages)} passages); something wrong with HotpotQA loading")

        # Progress save: corpus + gold (cheap, ~few MB; safety stack rsyncs every 5 min)
        out_dir_for_progress = get_output_dir(ANCHOR_NAME)
        out_dir_for_progress.mkdir(parents=True, exist_ok=True)
        with open(out_dir_for_progress / "corpus_and_gold.json", "w") as f:
            json.dump({
                "n_questions": len(questions),
                "n_passages": len(passages),
                "passages": [{"title": t, "sidx": s, "text": txt} for (t, s, txt) in passages],
                "gold_per_question": {qid: [list(p) for p in gold] for qid, gold in gold_per_question.items()},
                "question_ids": [q["id"] for q in questions],
            }, f, indent=2)
        print(f"[progress] corpus_and_gold.json saved ({len(passages)} passages)", flush=True)

        # Hardening: log GPU memory pre-index so OOM is diagnosable
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                free_mem, total_mem = torch.cuda.mem_get_info(0)
                print(f"[gpu] {props.name} VRAM total={total_mem/1e9:.1f} GB free={free_mem/1e9:.1f} GB "
                      f"BEFORE indexing", flush=True)
        except Exception as e:
            print(f"[gpu] could not log VRAM: {e}", flush=True)

        # Step 3: index + retrieve via ColBERT-v2
        query_pairs = [(q["id"], q["question"]) for q in questions]
        # Index goes to sky_workdir, NOT /tmp (which could fill on small ephemeral disks)
        experiment_root = Path(_ARGS.colbert_experiment_root)
        if not experiment_root.is_absolute():
            experiment_root = Path(os.environ.get("HOME", "/root")) / "sky_workdir" / experiment_root
        top_k_per_query = colbert_index_and_search(passages, query_pairs, _ARGS.top_k,
                                                      experiment_root, out_dir_for_progress)

        if len(top_k_per_query) != len(questions):
            print(f"[WARN] retrieved {len(top_k_per_query)} sets but expected {len(questions)} "
                  f"-- some queries failed silently", flush=True)

        # Step 4: compute metrics
        recall_at_2 = compute_recall_at_k(top_k_per_query, passages, gold_per_question, k=2)
        recall_at_10 = compute_recall_at_k(top_k_per_query, passages, gold_per_question, k=10)

        # Step 5: per-metric verdict
        if recall_at_2 >= HP_RECALL_AT_2:
            verdict = "HARD_PASS"
        elif recall_at_2 >= MID_LOW_RECALL_AT_2:
            verdict = "MID"   # BORDER per Research; will tag as MID in metrics
        else:
            verdict = "HARD_FAIL"

        elapsed = time.time() - t0
        summary = (f"{verdict}: recall@2={recall_at_2:.4f} (HP>={HP_RECALL_AT_2}, MID>={MID_LOW_RECALL_AT_2}); "
                   f"recall@10={recall_at_10:.4f} (bge baseline 0.74); "
                   f"{len(questions)} bridge questions on {len(passages)} passages")
        print(f"\n[VERDICT] {summary}", flush=True)

        # Step 6: write metrics
        out_dir = get_output_dir(ANCHOR_NAME)
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": summary,
            "recall_at_2": recall_at_2,
            "recall_at_10": recall_at_10,
            "hp_recall_at_2": HP_RECALL_AT_2,
            "mid_low_recall_at_2": MID_LOW_RECALL_AT_2,
            "bge_baseline_recall_at_2": 0.42,
            "bge_baseline_recall_at_10": 0.74,
            "n_questions": len(questions),
            "n_passages": len(passages),
            "top_k": _ARGS.top_k,
            "colbert_checkpoint": COLBERT_CHECKPOINT,
            "hotpot_split": HOTPOT_SPLIT,
            "hotpot_config": HOTPOT_CONFIG,
            "nbits": NBITS,
            "doc_maxlen": DOC_MAXLEN,
            "kmeans_niters": KMEANS_NITERS,
            "elapsed_s": elapsed,
            "summary": summary,
        }
        write_metrics(out_dir, metrics, [metrics])
        print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)

    except Exception as exc:
        elapsed = time.time() - t0
        reason = f"{type(exc).__name__}: {exc}"
        print(f"\n[FATAL] {reason}", flush=True)
        import traceback
        traceback.print_exc()
        _emit_failure_metrics(reason, elapsed)
        raise


if __name__ == "__main__":
    if _ARGS.self_test:
        _selftest()
        print("[--self-test] PROT-022 PASS; exiting before model load.", flush=True)
        sys.exit(0)
    main()
