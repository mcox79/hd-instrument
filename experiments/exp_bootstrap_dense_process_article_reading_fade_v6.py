# CELL-TEMPLATE (culmination v6; NOT a queue-dispatch cell). USER-caught: the "reading can't supply
# the knowledge" conclusion was OVERSTATED -- v3/v4/v5 fed a shallow extractor a SCATTERED general
# corpus (Simple Wikipedia sentences), the OPPOSITE of reading a physics textbook. This is the
# "read the book -> learn the physics" case, never tested: read DENSE, EXPLICIT, coherent
# process-ARTICLES where the process is KNOWN from the topic (article title), not guessed from
# ambiguous shared vocab. ONE VARIABLE vs v4: corpus quality (dense-explicit-topic-known) + attribution
# (process = article topic, NOT vocab-guessed); SAME extractor (v2, 0.90 on clean explicit sentences),
# SAME FHRR superposition store (v3), SAME expanded held-out (ProPara DEV, N=165), SAME seed.
#
# CORPUS: one coherent SimpleWiki ARTICLE per process (extracted from the raw dump by title;
# data/corpora/process_articles_v1/process_articles.json) -- 40 articles / 18 processes / 1229
# sentences, dense+explicit, process KNOWN from the article topic. FAIRNESS (USER-emphatic): no-leak
# (DEV NEVER read -- corpus is SimpleWiki articles, ProPara DEV is the held-out; a guard counts any
# overlap); can-fail (if dense/explicit reading STILL doesn't recover it -> the limit is deeper than
# corpus, report WHICH: article content vs reader depth); process-from-topic attribution is fair
# (that IS how a textbook chapter works). HONEST METRIC: genuine signal above scramble (scramble-clean),
# scored THROUGH the v3 superposition per (entity,process) unbind+cleanup (NOT _dom cross-process merge).
# Load-bearing subset: no bare except; tmp_replace; deterministic; self-test loads corpus + real extract.
# See preregs/2026-08-11_dense_process_article_reading_fade_v6.md.
"""exp_bootstrap_dense_process_article_reading_fade_v6 -- does reading DENSE, EXPLICIT, topic-known
process-ARTICLES recover substantially MORE genuine process-conditioned entity-fate knowledge than the
scattered-Wikipedia baseline (v4)? Compares dense reading_only + genuine-signal-above-scramble vs v4
(0.279 / 0.049) and the seed (0.315). Modes: --self-test / (no flag)=the measurement.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

ANCHOR_NAME = "bootstrap_dense_process_article_reading_fade_v6"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools", "benchmark_trap_check")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
CORPUS_PATH = os.path.join(REPO_ROOT, "data", "corpora", "process_articles_v1", "process_articles.json")

from experiments.exp_propara_bridging_distilled_kb_endtoend_v1 import _load_kb  # noqa: E402
from experiments.exp_propara_decisive_inference_arm1_oracle_v1 import _load_split  # noqa: E402
from experiments.exp_stated_entity_fate_reading_extractor_v2_highprecision import (  # noqa: E402
    extract_facts_strict, _load_or_build_frontend,
)
from experiments.exp_bootstrap_process_conditioned_reading_fade_v2 import _seed_maps  # noqa: E402
from experiments.exp_bootstrap_fhrr_superposition_fade_v3 import (  # noqa: E402
    FHRRProcessStore, EFFECTS, FHRR_DIM, STORE_SEED, _answer, _recall,
)
from experiments.exp_bootstrap_passage_context_binding_fade_v4 import (  # noqa: E402
    _build_heldout_expanded, _new_store, _fade_block,
)

# v4 SCATTERED-Wikipedia baseline (CITED@data/exp_bootstrap_passage_context_binding_fade_v4/metrics.json)
V4_READING_ONLY = 0.2788
V4_SIGNAL_ABOVE_SCRAMBLE = 0.0485


def run() -> Dict:
    t0 = time.time()
    kb = _load_kb()
    procs = kb["processes"]
    held, dev_paragraphs = _build_heldout_expanded(procs)
    dev_sentences = {s.strip() for para in dev_paragraphs for s in para["sentence_texts"]}
    keyed, seed_global, seed_vocab = _seed_maps(procs)
    gen = _load_or_build_frontend()

    corpus = json.load(open(CORPUS_PATH, encoding="utf-8"))
    articles = corpus["articles"]
    print(f"[corpus] {corpus['n_articles']} articles, {len(articles)} processes, "
          f"{corpus['total_sentences']} sentences (dense, explicit, topic-known)", flush=True)

    store = _new_store(keyed)   # FHRR store with SEED bundled (TRUST_HIGH), same as v4
    read_counts: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    n_sent = n_facts = n_leak = 0
    facts_per_proc = Counter()
    # READ each dense article; PROCESS = the article's KNOWN topic (clean attribution, no guessing)
    for proc, title_map in articles.items():
        if proc not in procs:
            continue
        for title, sents in title_map.items():
            for s in sents:
                s = s.strip()
                if not s:
                    continue
                if s in dev_sentences:   # no-leak guard (DEV never read)
                    n_leak += 1
                    continue
                n_sent += 1
                for f in extract_facts_strict(gen, s):
                    store.add_read(f["entity_head"], proc, f["fate"], count=1.0)
                    read_counts[(f["entity_head"], proc)][f["fate"]] += 1
                    n_facts += 1
                    facts_per_proc[proc] += 1
    print(f"[read] dense articles: {n_sent} sentences -> {n_facts} (entity,process,fate) facts "
          f"across {len(facts_per_proc)} processes; no-leak guard fires={n_leak}", flush=True)

    fade = _fade_block(held, store, keyed, read_counts, "dense")
    print(f"[fade] reading_only={fade['reading_only']} seed_only={fade['seed_only']} combined={fade['combined']} "
          f"gap={fade['lesion_gap']} fade_ratio={fade['fade_ratio']} overlap={fade['overlap']} "
          f"scramble_recall={fade['scramble_recall']} scramble_retained={fade['scramble_retained']} "
          f"signal_above_scramble={fade['signal_above_scramble']}", flush=True)

    # per-process reading recall on the held-out subset (where reading has the most coverage)
    from collections import defaultdict as _dd
    held_by_proc = _dd(list)
    for it in held:
        for P in it["procs"]:
            held_by_proc[P].append(it)
    per_proc = {}
    for P, items in held_by_proc.items():
        if not items:
            continue
        r = _recall(items, store, "read")
        s = _recall(items, store, "seed")
        per_proc[P] = {"n_items": len(items), "reading_only": r, "seed_only": s,
                       "n_read_facts": facts_per_proc.get(P, 0)}
    print("[per-process] reading_only vs seed_only (held-out items with reading coverage):", flush=True)
    for P in sorted(per_proc, key=lambda k: -per_proc[k]["n_items"]):
        d = per_proc[P]
        print(f"    {P:>22}: N={d['n_items']:3d} reading_only={d['reading_only']} seed_only={d['seed_only']} "
              f"(read_facts={d['n_read_facts']})", flush=True)

    # verdict inputs vs v4 scattered + seed
    dense_signal = fade["signal_above_scramble"]
    beats_v4_signal = dense_signal >= V4_SIGNAL_ABOVE_SCRAMBLE + 0.05      # substantially more genuine signal
    beats_v4_recall = fade["reading_only"] >= V4_READING_ONLY + 0.05
    approaches_seed = fade["reading_only"] >= 0.85 * fade["seed_only"]
    if beats_v4_signal and (beats_v4_recall or approaches_seed):
        verdict = "HARD_PASS_dense_explicit_reading_recovers_more"
    elif dense_signal >= V4_SIGNAL_ABOVE_SCRAMBLE + 0.03:
        verdict = "MIDDLE_BAND_dense_helps_partially"
    else:
        verdict = "HARD_FAIL_dense_explicit_no_better_than_scattered"
    verdict_msg = (
        f"{verdict}: [DENSE/EXPLICIT topic-known process-ARTICLES, no-leak(fires={n_leak}), scored through "
        f"v3 superposition per (entity,process)]. Corpus: {corpus['n_articles']} articles / {len(facts_per_proc)} "
        f"processes / {n_sent} sentences -> {n_facts} facts. reading_only={fade['reading_only']} "
        f"seed_only={fade['seed_only']} combined={fade['combined']}; GENUINE signal above scramble="
        f"{dense_signal} (scramble_recall={fade['scramble_recall']}) vs v4-SCATTERED signal {V4_SIGNAL_ABOVE_SCRAMBLE} "
        f"(reading_only {V4_READING_ONLY}); LESION gap={fade['lesion_gap']} fade_ratio={fade['fade_ratio']} "
        f"overlap={fade['overlap']} ({fade['n_seed_rederived']}/{fade['n_seed_covered']}). "
        f"beats_v4_genuine_signal={beats_v4_signal} approaches_seed={approaches_seed}")

    return {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": verdict_msg,
        "elapsed_s": round(time.time() - t0, 2), "run_mode": "dense_article_reading", "anchor_name": ANCHOR_NAME,
        "one_variable_vs_v4": "corpus quality (dense-explicit-topic-known process ARTICLES) + attribution "
                              "(process=article topic, not vocab-guessed); same extractor/store/held-out/seed",
        "fairness": {"no_leak_dev_never_read": True, "n_leak_guard_fires": n_leak,
                     "scored_via_superposition_context_separated": True, "process_from_topic_attribution": True},
        "corpus": {"n_articles": corpus["n_articles"], "n_processes": len(facts_per_proc),
                   "n_sentences_read": n_sent, "n_facts_extracted": n_facts,
                   "facts_per_process": dict(facts_per_proc.most_common()),
                   "processes_covered": corpus["processes_covered"], "source": CORPUS_PATH},
        "n_heldout_items": len(held),
        "fade": fade, "per_process": per_proc,
        "comparison": {"v4_scattered_reading_only": V4_READING_ONLY,
                       "v4_scattered_signal_above_scramble": V4_SIGNAL_ABOVE_SCRAMBLE,
                       "dense_reading_only": fade["reading_only"],
                       "dense_signal_above_scramble": dense_signal, "seed_only": fade["seed_only"],
                       "beats_v4_genuine_signal": beats_v4_signal, "approaches_seed": approaches_seed},
        "bands": {"V4_READING_ONLY": V4_READING_ONLY, "V4_SIGNAL_ABOVE_SCRAMBLE": V4_SIGNAL_ABOVE_SCRAMBLE},
    }


# ============================================================================ I/O
def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ============================================================================ self-test
def self_test() -> Dict:
    print("[self-test] starting", flush=True)
    out = {"checks": {}}
    assert os.path.exists(CORPUS_PATH), f"corpus missing: {CORPUS_PATH} (run the article extractor first)"
    corpus = json.load(open(CORPUS_PATH, encoding="utf-8"))
    assert corpus["n_articles"] >= 15 and len(corpus["articles"]) >= 15, corpus["n_articles"]
    # dense articles present for the held-out-dominant processes
    for p in ("electricity_generation", "combustion", "hydrocarbon_formation", "igneous_rock_cycle"):
        assert p in corpus["articles"] and sum(len(v) for v in corpus["articles"][p].values()) >= 10, p
    out["checks"]["corpus"] = {"n_articles": corpus["n_articles"], "n_processes": len(corpus["articles"])}
    print(f"[self-test] corpus OK: {corpus['n_articles']} articles, {len(corpus['articles'])} processes", flush=True)

    # real extractor on a dense explicit sentence + KNOWN-process attribution -> FHRR store
    gen = _load_or_build_frontend()
    kb = _load_kb()
    keyed, _sg, _sv = _seed_maps(kb["processes"])
    store = _new_store(keyed)
    facts = extract_facts_strict(gen, "Combustion is a reaction between a fuel and oxygen that produces carbon dioxide and water.")
    for f in facts:
        store.add_read(f["entity_head"], "combustion", f["fate"], count=1.0)
    rows = [store.retrieve(f["entity_head"], "combustion", "read") for f in facts]
    assert any(r is not None for r in rows), (facts, rows)
    out["checks"]["real_read"] = {"n_facts": len(facts), "sample": [(f["entity_head"], f["fate"]) for f in facts]}
    print(f"[self-test] real dense-sentence read + topic attribution + FHRR store OK: {out['checks']['real_read']}", flush=True)

    out["verdict"] = "SELFTEST_PASS"
    out["verdict_msg"] = "SELFTEST_PASS: corpus present (dense articles) + real extractor + topic attribution + store OK"
    out["summary"] = "SELFTEST_PASS"
    out["elapsed_s"] = 0.0
    out["run_mode"] = "self_test"
    out["anchor_name"] = ANCHOR_NAME
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    args = ap.parse_args()
    run_mode = "self_test" if args.self_test else "dense_article_reading"
    out_dir = OUTPUT_DIR + ("_selftest" if args.self_test else "")
    _write_start_marker(out_dir, run_mode)
    try:
        metrics = self_test() if args.self_test else run()
        if args.self_test:
            metrics["elapsed_s"] = metrics.get("elapsed_s", 0.0)
        _write_metrics(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
