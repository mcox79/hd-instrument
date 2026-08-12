"""exp_context_conditioned_sense_selection_v2 -- re-run of v1 on the v5 term-boundary-repaired
definitional fact set, aimed squarely at the ONE question v1 could not answer at adequate power:
does the sense-from-own-sentences positive control survive TOPIC CONTROL (same-segment) once the
data-scarcity constraint (621/723 v3 senses had exactly one source sentence) is eased.

PRE-REG: preregs/2026-08-12_context_conditioned_sense_selection_v2.md (filed before any accuracy
number existed on v5 material).

WHAT IS REUSED, UNCHANGED, FROM v1 (imported, not copy-pasted, so it cannot drift):
  tokenize, build_mask_terms, masked_context_tokens   -- L2 masking
  DistSelector, PercSelector, argmax_deterministic, rank_of, evaluate, summarize, wilson
  run_c3, analyse_tail                                 -- fully generic over the `multi` dict,
                                                           so they work unchanged on either index
The three machine-asserted leakage mechanisms (L1 fit-corpus exclusion, L2 symmetric masking,
L3 no-extractor-metadata-in-scorer) are the same code paths as v1 -- re-asserted fresh against
this run's data, not weakened.

WHAT IS NEW:
  - facts source: v5 (`definitional_facts_v5.jsonl`) instead of v3
  - fit corpus: the v5 CANONICAL corpus (line-aware bio loader, F9) instead of v3's joined-line
    corpus -- using the old loader here would be a corpus/fact-extraction mismatch, not just a
    missed improvement
  - BOTH subject-key indexes (`subject` full-term = PRIMARY; `subject_head_lemma` = SECONDARY,
    reported but not determinative) instead of v1's `subject`-only
  - floor is RECOMPUTED for v5's k-distribution on each index (NOT v1's 0.4316 -- that belonged
    to v3's k-distribution and does not apply here)
  - C3 (incl. same-segment topic control) is run on BOTH indexes; v1 ran it on `subject` only

ASCII only. Deterministic. Single CPU process.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from typing import Dict, List, Tuple

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.random_indexing import RandomIndexingEncoder
from experiments.exp_context_conditioned_sense_selection_v1 import (
    tokenize, build_mask_terms, masked_context_tokens,
    DistSelector, PercSelector, argmax_deterministic, rank_of,
    evaluate, summarize, wilson, run_c3, analyse_tail,
)

FACTS_PATH = os.path.join(REPO_ROOT, "data", "foundation",
                          "reading_grounding_v5_termboundary", "definitional_facts_v5.jsonl")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_context_conditioned_sense_selection_v2")

RI_N = 8192
RI_SPARSITY = 10
RI_WINDOW = 5
RI_MIN_COUNT = 3
RI_SEED = 0
N_SWAP_SEEDS = 5
N_FLOOR_SIM_SEEDS = 1000

# pre-registered indexes, PRIMARY declared before any accuracy exists
INDEXES = ["subject", "subject_head_lemma"]
PRIMARY_INDEX = "subject"

# pre-registered expected census (asserted at runtime; mismatch blocks the run -- the eval set
# on disk must still match what the prereg fixed)
EXPECTED = {
    "subject": {"n_multisense": 288, "mean_k": 2.2431, "floor": 0.4634},
    "subject_head_lemma": {"n_multisense": 379, "mean_k": 2.4538, "floor": 0.4401},
}


# ============================================================== eval-set construction
def load_multisense_eval(index_key: str) -> Tuple[Dict[str, List[dict]], List[dict], dict]:
    """Same construction as v1.load_multisense_eval, parameterized by which subject key indexes
    the words -- 'subject' (full term, PRIMARY) or 'subject_head_lemma' (SECONDARY,
    over-general per the v5 note, eval-only, never a stored-fact key)."""
    rows = [json.loads(line) for line in open(FACTS_PATH, encoding="utf-8")]
    by_subj: Dict[str, List[dict]] = collections.defaultdict(list)
    for r in rows:
        by_subj[r[index_key]].append(r)
    multi = {w: v for w, v in sorted(by_subj.items()) if len({r["object"] for r in v}) > 1}

    trials: List[dict] = []
    n_ambiguous = 0
    ambiguous_words = set()
    for w in sorted(multi):
        facts = multi[w]
        sent_owner: Dict[str, set] = collections.defaultdict(set)
        for f in facts:
            for s in f["source_sentences"]:
                sent_owner[s].add(f["object"])
        for f in facts:
            for s in f["source_sentences"]:
                if len(sent_owner[s]) > 1:
                    n_ambiguous += 1
                    ambiguous_words.add(w)
                    continue
                trials.append({"word": w, "true_object": f["object"], "sentence": s,
                               "fid": f["fid"], "k": len({x["object"] for x in facts}),
                               "n_src": len(f["source_sentences"])})

    ks = [len({r["object"] for r in v}) for v in multi.values()]
    n_facts_multisense = sum(len(v) for v in multi.values())
    # senses_with_gt1_source_sentence / words_all_gt1: PER STORED ROW, not merged across rows
    # that share an index key -- the conservative convention C3's power actually depends on.
    senses_gt1 = sum(1 for v in multi.values() for f in v if len(f["source_sentences"]) > 1)
    words_all_gt1 = sum(1 for v in multi.values()
                        if all(len(f["source_sentences"]) > 1 for f in v))
    census = {
        "index_key": index_key,
        "n_facts_total": len(rows),
        "n_distinct_subjects": len(by_subj),
        "n_multisense_subjects": len(multi),
        "multisense_subject_frac": round(len(multi) / len(by_subj), 4),
        "n_facts_in_multisense": n_facts_multisense,
        "mean_k": round(sum(ks) / len(ks), 4),
        "k_distribution": dict(sorted(collections.Counter(ks).items())),
        "analytic_floor_subject_weighted": round(sum(1.0 / k for k in ks) / len(ks), 4),
        "analytic_floor_micro_per_fact": round(len(multi) / n_facts_multisense, 4),
        "n_trials": len(trials),
        "n_trials_excluded_label_ambiguous": n_ambiguous,
        "n_words_with_ambiguous_sentence": len(ambiguous_words),
        "senses_with_gt1_source_sentence": senses_gt1,
        "words_with_ALL_senses_gt1": words_all_gt1,
        "src_sentence_count_distribution": dict(sorted(collections.Counter(
            len(f["source_sentences"]) for v in multi.values() for f in v).items())),
    }
    return multi, trials, census


# ============================================================== per-index run
def run_one_index(index_key: str, enc: RandomIndexingEncoder, fit_corpus_removed: int,
                  smoke: bool) -> dict:
    print("[index=%s] loading eval set..." % index_key, flush=True)
    multi, trials, census = load_multisense_eval(index_key)
    print("[index=%s census] %s" % (index_key, json.dumps(census)), flush=True)

    exp = EXPECTED[index_key]
    assert census["n_multisense_subjects"] == exp["n_multisense"], \
        "eval set drifted for %s: %r" % (index_key, census)
    assert abs(census["mean_k"] - exp["mean_k"]) < 5e-4, \
        "mean_k drifted for %s: %r" % (index_key, census)
    assert abs(census["analytic_floor_subject_weighted"] - exp["floor"]) < 5e-4, \
        "floor drifted for %s: %r" % (index_key, census)
    floor = census["analytic_floor_subject_weighted"]

    # empirical floor check
    ks = [len({r["object"] for r in v}) for v in multi.values()]
    rng = np.random.default_rng(12345)
    sims = [float(np.mean([1.0 if rng.integers(k) == 0 else 0.0 for k in ks]))
            for _ in range(N_FLOOR_SIM_SEEDS if not smoke else 50)]
    emp = float(np.mean(sims))
    assert abs(emp - floor) < 0.02, "empirical floor %r != analytic %r for %s" % (emp, floor, index_key)
    print("[index=%s floor] analytic=%.4f empirical=%.4f" % (index_key, floor, emp), flush=True)

    if smoke:
        trials = trials[:40]

    s1, s2 = DistSelector(enc), PercSelector()
    selectors = [s1, s2]

    mask_cache = {w: build_mask_terms(w, multi[w]) for w in sorted(multi)}
    ctx_cache: Dict[Tuple[str, str], List[str]] = {}

    def ctx_primary(tr: dict) -> List[str]:
        key = (tr["word"], tr["sentence"])
        if key not in ctx_cache:
            toks = masked_context_tokens(tr["sentence"], mask_cache[tr["word"]])
            cand_tokens = set()
            for f in multi[tr["word"]]:
                cand_tokens.update(tokenize(f["object"]))
            assert not (set(toks) & cand_tokens), \
                "L2 VIOLATION [%s]: candidate token survived masking for %r" % (index_key, tr["word"])
            ctx_cache[key] = toks
        return ctx_cache[key]

    n_empty_ctx = sum(1 for tr in trials if not ctx_primary(tr))
    ctx_lens = [len(ctx_primary(tr)) for tr in trials]
    print("[index=%s L2] masked ok; mean ctx tokens=%.2f empty=%d" %
          (index_key, sum(ctx_lens) / max(1, len(ctx_lens)), n_empty_ctx), flush=True)

    print("[index=%s] primary..." % index_key, flush=True)
    primary = {k: summarize(v) for k, v in evaluate(trials, multi, selectors, ctx_primary).items()}
    for k, v in primary.items():
        print("  [%s] %s subj_w=%s micro=%s n=%s" %
              (index_key, k, v["subject_weighted_acc"], v["micro_acc"], v["n_trials"]), flush=True)

    print("[index=%s] C1 cross-item swap..." % index_key, flush=True)
    all_sents = sorted({(tr["word"], tr["sentence"]) for tr in trials})
    c1_runs: List[Dict[str, dict]] = []
    for seed in range(N_SWAP_SEEDS if not smoke else 2):
        r = np.random.default_rng(1000 + seed)
        swap: Dict[Tuple[str, str], List[str]] = {}
        for tr in trials:
            w2, s2_ = tr["word"], tr["sentence"]
            for _try in range(20):
                w2, s2_ = all_sents[int(r.integers(len(all_sents)))]
                if w2 != tr["word"]:
                    break
            swap[(tr["word"], tr["sentence"])] = masked_context_tokens(s2_, mask_cache[tr["word"]])
        c1_runs.append({k: summarize(v) for k, v in evaluate(
            trials, multi, selectors, lambda tr: swap[(tr["word"], tr["sentence"])]).items()})
    c1 = {k: {"subject_weighted_acc": round(float(np.mean([run[k]["subject_weighted_acc"]
                                                           for run in c1_runs])), 4),
              "subject_weighted_sd": round(float(np.std([run[k]["subject_weighted_acc"]
                                                         for run in c1_runs])), 4),
              "micro_acc": round(float(np.mean([run[k]["micro_acc"] for run in c1_runs])), 4),
              "n_seeds": len(c1_runs)} for k in c1_runs[0]}
    for k, v in c1.items():
        print("  [%s] C1 %s subj_w=%s (sd %s)" %
              (index_key, k, v["subject_weighted_acc"], v["subject_weighted_sd"]), flush=True)

    print("[index=%s] C2 lesion..." % index_key, flush=True)
    c2 = {k: summarize(v) for k, v in evaluate(trials, multi, selectors, lambda tr: []).items()}
    for k, v in c2.items():
        print("  [%s] C2 %s subj_w=%s" % (index_key, k, v["subject_weighted_acc"]), flush=True)

    print("[index=%s] C3 strict LOO..." % index_key, flush=True)
    c3 = run_c3(multi, s1, mask_cache)
    c3_swap_runs = [run_c3(multi, s1, mask_cache, mode="swap", swap_seed=i)
                    for i in range(1 if smoke else N_SWAP_SEEDS)]
    c3_swap = {"acc": round(float(np.mean([r["acc"] for r in c3_swap_runs])), 4),
               "acc_sd": round(float(np.std([r["acc"] for r in c3_swap_runs])), 4),
               "n_seeds": len(c3_swap_runs), "n_trials": c3_swap_runs[0]["n_trials"]}
    c3_cm = run_c3(multi, s1, mask_cache, count_match=True)
    c3_seg = run_c3(multi, s1, mask_cache, same_segment_only=True)
    c3_seg_swap = run_c3(multi, s1, mask_cache, same_segment_only=True, mode="swap", swap_seed=1)
    print("  [%s] C3=%s C3-SWAP=%s C3-CM=%s C3-SEG=%s (n=%s ci=%s) C3-SEG-SWAP=%s" %
          (index_key, c3.get("acc"), c3_swap["acc"], c3_cm.get("acc"), c3_seg.get("acc"),
           c3_seg.get("n_trials"), c3_seg.get("ci95"), c3_seg_swap.get("acc")), flush=True)

    rich = [tr for tr in trials if len(ctx_primary(tr)) >= 3]
    primary_rich = {k: summarize(v) for k, v in
                    evaluate(rich, multi, selectors, ctx_primary).items()}

    tail = analyse_tail(trials, multi, selectors, ctx_primary, s1, s2)

    best_name = max(("S1_DIST", "S2_PERC", "S3_COMBO"),
                    key=lambda n: primary[n]["subject_weighted_acc"] or 0.0)
    acc = primary[best_name]["subject_weighted_acc"] or 0.0
    c1_best = c1[best_name]["subject_weighted_acc"]
    c2_best = c2[best_name]["subject_weighted_acc"] or 0.0
    c1_drop = round(acc - c1_best, 4)
    both_at_floor = ((primary["S1_DIST"]["subject_weighted_acc"] or 0) <= floor + 0.03
                     and (primary["S2_PERC"]["subject_weighted_acc"] or 0) <= floor + 0.03)
    seg_ci_lo = (c3_seg.get("ci95") or [0.0, 0.0])[0]
    seg_clears_floor = (c3_seg.get("acc") is not None and c3_seg["acc"] > floor
                        and seg_ci_lo > floor)

    if both_at_floor or c1_drop < 0.05 or c2_best >= acc - 0.03:
        verdict = "HARD_FAIL_context_conditioned_sense_selection_DOES_NOT_WORK"
    elif acc <= 0.60:
        verdict = "MIDDLE_BAND"
    elif acc >= 0.70 and c2_best <= floor + 0.03 and c1_drop >= 0.08 and seg_clears_floor:
        verdict = "HARD_PASS"
    elif c1_drop >= 0.08 and c2_best <= floor + 0.03:
        verdict = "PASS"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "index_key": index_key,
        "is_primary": index_key == PRIMARY_INDEX,
        "census": census,
        "floor": {"analytic_subject_weighted": floor, "empirical_subject_weighted": round(emp, 4),
                  "analytic_micro_per_fact": census["analytic_floor_micro_per_fact"]},
        "leakage_control": {
            "L1_eval_sentences_removed_from_shared_fit_corpus": fit_corpus_removed,
            "L2_answer_tokens_masked_asserted": True,
            "L2_mean_context_tokens": round(sum(ctx_lens) / max(1, len(ctx_lens)), 2),
            "L2_empty_context_trials": n_empty_ctx,
            "L3_no_extractor_metadata_in_scorer": True,
        },
        "primary": primary,
        "primary_context_rich_only": {"n_trials": len(rich), **primary_rich},
        "C1_cross_item_context_swap": c1,
        "C2_context_lesion": c2,
        "C3_strict_leave_one_sentence_out": c3,
        "C3_control_query_swap": c3_swap,
        "C3_control_count_matched": c3_cm,
        "C3_control_same_segment_only": c3_seg,
        "C3_control_same_segment_only_query_swap": c3_seg_swap,
        "C3_same_segment_clears_floor_with_ci": seg_clears_floor,
        "best_selector": best_name,
        "best_subject_weighted_acc": acc,
        "C1_drop": c1_drop,
        "inseparable_tail": tail,
        "index_verdict": verdict,
    }


# ============================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="tiny corpus + 40 trials/index, gate only")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--timeout", type=int, default=3600)
    args = ap.parse_args()

    if args.self_test:
        run_self_tests()
        print("SELF-TEST OK")
        return

    t_start = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    from experiments.exp_definitional_grounding_v5 import load_corpus_v5

    # build both eval sets first so the shared fit corpus can remove the UNION of their eval
    # sentences (L1) -- one RI fit serves both index arms, they cannot leak into each other's
    # sentence set because the union removes strictly more than either alone needs.
    trial_sents: set = set()
    for idx in INDEXES:
        _multi, trials, _census = load_multisense_eval(idx)
        trial_sents.update(tr["sentence"] for tr in trials)
    print("[union] %d distinct eval sentences across both indexes" % len(trial_sents), flush=True)

    print("[corpus] loading v5 CANONICAL (line-aware) corpus...", flush=True)
    corpus = load_corpus_v5(200 if args.smoke else None, lineaware=True)
    kept = [s for _seg, s in corpus if s not in trial_sents]
    n_removed = len(corpus) - len(kept)
    assert not (set(kept) & trial_sents), "L1 VIOLATION: an eval sentence survived in the fit corpus"
    print("[corpus] %d sentences, %d removed as eval (union), %d kept" %
          (len(corpus), n_removed, len(kept)), flush=True)

    fit_tokens: List[str] = []
    for s in kept:
        fit_tokens.extend(tokenize(s))
    print("[corpus] %d fit tokens" % len(fit_tokens), flush=True)

    enc = RandomIndexingEncoder(N=1024 if args.smoke else RI_N, sparsity=RI_SPARSITY,
                                window=RI_WINDOW, min_count=RI_MIN_COUNT, seed=RI_SEED)
    t0 = time.time()
    enc.fit_corpus(fit_tokens)
    print("[ri] vocab=%d fit_s=%.1f" % (enc.vocab_size(), time.time() - t0), flush=True)

    per_index = {}
    for idx in INDEXES:
        per_index[idx] = run_one_index(idx, enc, n_removed, args.smoke)
        print("[index=%s] DONE verdict=%s" % (idx, per_index[idx]["index_verdict"]), flush=True)

    primary_result = per_index[PRIMARY_INDEX]
    final_verdict = primary_result["index_verdict"]

    metrics = {
        "cell": "exp_context_conditioned_sense_selection_v2",
        "prereg": "preregs/2026-08-12_context_conditioned_sense_selection_v2.md",
        "v1_prereg_for_reference": "preregs/2026-08-12_context_conditioned_sense_selection_v1.md",
        "facts_source": FACTS_PATH,
        "corpus_loader": "exp_definitional_grounding_v5.load_corpus_v5(lineaware=True)",
        "ri_encoder": {"N": enc.N, "sparsity": enc.sparsity, "window": enc.window,
                       "min_count": enc.min_count, "seed": enc.seed,
                       "vocab_size": enc.vocab_size(), "n_tokens_seen": enc._n_tokens_seen},
        "L1_union_eval_sentences_removed": n_removed,
        "L1_asserted_disjoint": True,
        "primary_index": PRIMARY_INDEX,
        "removed_control_cannot_fail": (
            "WORD-ORDER SCRAMBLE of the context: both selectors are bag-of-words aggregates, so "
            "permuting token order leaves every score bit-identical -- cannot fail by "
            "construction. Re-verified fresh in this run's self-test against the imported "
            "(unchanged) selector classes, not merely cited from v1."),
        "per_index": per_index,
        "final_verdict": final_verdict,
        "final_verdict_basis": "primary index (%s) main-arm bands" % PRIMARY_INDEX,
        "runtime_s": round(time.time() - t_start, 1),
        "smoke": bool(args.smoke),
    }
    out = os.path.join(OUTPUT_DIR, "metrics_smoke.json" if args.smoke else "metrics.json")
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out)
    print("VERDICT %s  primary_idx=%s acc=%.4f floor=%.4f" %
          (final_verdict, PRIMARY_INDEX, primary_result["best_subject_weighted_acc"],
           primary_result["floor"]["analytic_subject_weighted"]), flush=True)
    print("wrote %s" % out, flush=True)


# ============================================================== formula self-tests
def run_self_tests() -> None:
    # (1) masking still works via the imported (unchanged) v1 functions
    facts = [{"object": "company", "definiens_surface": "the biggest company",
              "definiendum_surface": "Apple", "source_sentences": ["x"]},
             {"object": "valuable", "definiens_surface": "the most valuable",
              "definiendum_surface": "Apple", "source_sentences": ["y"]}]
    mt = build_mask_terms("apple", facts)
    assert "company" in mt and "valuable" in mt and "apple" in mt, mt
    toks = masked_context_tokens("The brand value of Apple, the biggest company, rose", mt)
    assert "company" not in toks and "apple" not in toks, toks
    assert "brand" in toks, toks

    # (2) deterministic tie-break, never random
    assert argmax_deterministic([0.5, 0.5, 0.5], ["a", "b", "c"]) == "a"
    assert argmax_deterministic([0.1, 0.9], ["a", "b"]) == "b"

    # (3) floor formulas match the pre-registered v5 numbers, PER INDEX (not v1's 0.4316)
    for idx, exp in EXPECTED.items():
        kd_key = "k_distribution"
        _multi, _trials, census = load_multisense_eval(idx)
        assert census["n_multisense_subjects"] == exp["n_multisense"], (idx, census)
        assert abs(census["mean_k"] - exp["mean_k"]) < 5e-4, (idx, census)
        assert abs(census["analytic_floor_subject_weighted"] - exp["floor"]) < 5e-4, (idx, census)
        ks = [k for k, n in census[kd_key].items() for _ in range(n)]
        f = sum(1.0 / k for k in ks) / len(ks)
        assert abs(f - exp["floor"]) < 5e-4, (idx, f)

    # (4) wilson sanity
    lo, hi = wilson(50, 100)
    assert lo < 0.5 < hi and hi - lo < 0.25, (lo, hi)

    # (5) THE removed control really is invariant, re-checked fresh against the IMPORTED
    # (unchanged) selector classes this run actually uses -- not cited from v1's own self-test.
    class _Enc:
        def has(self, w): return True
        def encode(self, w): return np.array([hash(w) % 7, len(w), 1.0], dtype=np.float64)
    sel = DistSelector(_Enc())
    t = ["alpha", "beta", "gamma", "delta"]
    a = sel.scores(t, ["one", "two"])
    b = sel.scores(list(reversed(t)), ["one", "two"])
    assert max(abs(x - y) for x, y in zip(a, b)) < 1e-9, \
        "word-order scramble is NOT invariant -- the removal rationale is wrong: %r vs %r" % (a, b)
    assert argmax_deterministic(a, ["one", "two"]) == argmax_deterministic(b, ["one", "two"])

    # (6) rank helper (imported, sanity only)
    assert rank_of([0.1, 0.9, 0.5]) == [2, 0, 1]

    # (7) the v5 fact set on disk still matches what THIS prereg fixed
    assert os.path.exists(FACTS_PATH), FACTS_PATH
    n_rows = sum(1 for _ in open(FACTS_PATH, encoding="utf-8"))
    assert n_rows == 2092, n_rows

    # (8) both index eval sets are genuinely different (arms-must-differ)
    multi_a, trials_a, _ = load_multisense_eval("subject")
    multi_b, trials_b, _ = load_multisense_eval("subject_head_lemma")
    assert set(multi_a) != set(multi_b), "subject and subject_head_lemma indexes are identical"
    assert len(trials_a) != len(trials_b)


if __name__ == "__main__":
    main()
