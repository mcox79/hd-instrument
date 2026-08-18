"""exp_c3_relation_alphabet_fragmentation_v1 -- HOW MUCH CROSS-ITEM EVIDENCE SURVIVES BINDING,
MEASURED ON THE ACTUAL C3 CORPUS AND THE ACTUAL DEPENDENCY FRONT-END?

DIAGNOSTIC CELL, NOT A GATED ONE. No pre-registered PASS/FAIL band; it measures a quantity, it
does not test a capability claim. Durable (not scratch/) because a report cites its numbers.

WHY
---
exp_bound_key_crossitem_similarity_cost_v1 shows on synthetic codes that a bound key costs
NOTHING when every item uses the same key (R=1, bit-exact equality) and destroys cross-item
retrieval as the key ALPHABET grows -- because two independently built anchors share evidence
only where they agree on the key. This cell asks whether that mechanism is present at the size
that would explain exp_structured_code_vs_flat_bag_c3_v1's STRUCTURE_HURTS (0.03675 vs 0.0480),
using the REAL corpus, the REAL persisted UD front-end and the REAL feature extractor.

WHAT IS HELD CONSTANT, AND WHY THAT MATTERS
-------------------------------------------
The A1-vs-A2 contrast in the C3 cell changes TWO things at once: WHICH words enter the code
(a context window vs 1-hop dependency neighbours) and WHETHER they are bound to a relation key.
This cell holds the content FIXED -- the identical (relation, filler) feature list from
StructuralEncoder.features -- and varies ONLY whether the relation label is part of the symbol:

    FLAT_FILLERS  : the symbol is  filler
    BOUND_PAIRS   : the symbol is  (relation, filler)

so any difference is attributable to BINDING ALONE. This is therefore NOT a reproduction of the
A1/A2 numbers and must never be quoted as one.

MEASURES (reported separately, never averaged)
  1. relation-alphabet concentration: p(rel) over all emitted features, and
     R_eff = 1 / sum_r p_r^2 -- the inverse probability that two independent occurrences AGREE
     on the relation. R_eff, not the raw number of relation types, is what the synthetic sweep
     showed the cost tracks.
  2. fragmentation: distinct symbols and repeat-coherence (mean count per distinct symbol) per
     lemma, FLAT vs BOUND. Binding cannot reduce the symbol count; it can only split it.
  3. THE LOAD-BEARING ONE -- surviving cross-item evidence. Count-vector cosine between two
     lemmas' feature bags, computed FLAT and BOUND, on
       GOLD pairs  : (L, g) with g in C3.gold_meaning_set(L), the pairs a hit@1 needs to rank
       RANDOM pairs: the matched no-relation control
     The discriminative signal is (gold - random). The ratio of that signal, BOUND over FLAT,
     is the fraction of usable cross-item evidence that binding leaves behind.

NO EXTERNAL LLM. ASCII-only. CPU. READ-ONLY on every asset. data/foundation/** never opened.
hdlab/reading_grounding_loop.py is IMPORTED, never modified.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import hdlab.reading_grounding_loop as RGL
from hdlab.reading_grounding_loop import StructuralEncoder
import experiments.exp_grounding_readout_known_answer_v1 as C3
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "c3_relation_alphabet_fragmentation_v1"
CODE_VERSION = "v1.0"
SEED = C3.MASTER_SEED
N_RANDOM_PAIRS = 20000


def cos_counts(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    small, large = (a, b) if len(a) <= len(b) else (b, a)
    dot = sum(v * large.get(k, 0) for k, v in small.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (na * nb)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-lemmas", type=int, default=0, help="0 = all")
    ap.add_argument("--smoke", action="store_true")
    _a, _ = ap.parse_known_args()
    t0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if _a.smoke else ""))
    out_dir.mkdir(parents=True, exist_ok=True)

    sents = C3.build_corpus("smoke" if _a.smoke else "full")
    buckets, counts = C3.build_buckets(sents)
    lemmas = sorted(buckets)
    if _a.max_lemmas:
        lemmas = lemmas[:_a.max_lemmas]
    print(f"[corpus] n_sents={len(sents)} n_lemmas={len(buckets)} using={len(lemmas)} "
          f"({time.time()-t0:.1f}s)", flush=True)

    enc = StructuralEncoder(str(REPO), d=RGL.CTX_D)
    flat_bags: Dict[str, Counter] = {}
    bound_bags: Dict[str, Counter] = {}
    rel_counter: Counter = Counter()
    n_feats = 0
    for k, w in enumerate(lemmas):
        fb: Counter = Counter()
        bb: Counter = Counter()
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            for rel, filler in enc.features(sents[i], w):
                fb[filler] += 1
                bb[(rel, filler)] += 1
                rel_counter[rel] += 1
                n_feats += 1
        if fb:
            flat_bags[w] = fb
            bound_bags[w] = bb
        if k % 250 == 0 or k == len(lemmas) - 1:
            print(f"[features] {k+1}/{len(lemmas)} n_parsed={enc.n_parsed} n_feats={n_feats} "
                  f"elapsed={time.time()-t0:.1f}s", flush=True)

    have = sorted(flat_bags)
    tot = float(sum(rel_counter.values()))
    p = np.array([c / tot for _, c in rel_counter.most_common()], dtype=np.float64)
    r_eff = float(1.0 / np.sum(p * p))

    frag = {
        "n_lemmas_with_features": len(have),
        "n_features_total": n_feats,
        "n_relation_types": len(rel_counter),
        "R_eff_inverse_simpson": r_eff,
        "p_two_independent_occurrences_agree_on_relation": float(np.sum(p * p)),
        "top_relations": [{"rel": r, "p": c / tot} for r, c in rel_counter.most_common(15)],
        "mean_distinct_symbols_FLAT": float(np.mean([len(flat_bags[w]) for w in have])),
        "mean_distinct_symbols_BOUND": float(np.mean([len(bound_bags[w]) for w in have])),
        "mean_repeat_coherence_FLAT": float(np.mean(
            [sum(flat_bags[w].values()) / len(flat_bags[w]) for w in have])),
        "mean_repeat_coherence_BOUND": float(np.mean(
            [sum(bound_bags[w].values()) / len(bound_bags[w]) for w in have])),
    }
    frag["symbol_split_factor"] = (frag["mean_distinct_symbols_BOUND"]
                                   / max(frag["mean_distinct_symbols_FLAT"], 1e-9))
    print("[fragmentation] " + json.dumps(frag)[:900], flush=True)

    # ---- gold pairs: the pairs a hit@1 must rank first
    have_set = set(have)
    gold_pairs: List[Tuple[str, str]] = []
    for w in have:
        for g in sorted(C3.gold_meaning_set(w)):
            if g in have_set and g != w and not C3._is_variant(g, w):
                gold_pairs.append((w, g))
    gold_pairs = sorted(set(tuple(sorted(pr)) for pr in gold_pairs))
    print(f"[pairs] n_gold_pairs={len(gold_pairs)} ({time.time()-t0:.1f}s)", flush=True)

    rng = np.random.default_rng(SEED)
    gold_set = set(gold_pairs)
    rand_pairs: List[Tuple[str, str]] = []
    while len(rand_pairs) < N_RANDOM_PAIRS:
        a, b = have[int(rng.integers(len(have)))], have[int(rng.integers(len(have)))]
        if a == b:
            continue
        pr = tuple(sorted((a, b)))
        if pr in gold_set:
            continue
        rand_pairs.append(pr)

    def block(prs):
        f = np.array([cos_counts(flat_bags[a], flat_bags[b]) for a, b in prs])
        bnd = np.array([cos_counts(bound_bags[a], bound_bags[b]) for a, b in prs])
        return f, bnd

    gf, gb = block(gold_pairs)
    rf, rb = block(rand_pairs)

    def ci(x):
        idx = rng.integers(0, len(x), size=(2000, len(x)))
        m = x[idx].mean(1)
        return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]

    sig_flat = float(gf.mean() - rf.mean())
    sig_bound = float(gb.mean() - rb.mean())
    survive = sig_bound / sig_flat if sig_flat != 0 else float("nan")

    evidence = {
        "n_gold_pairs": len(gold_pairs), "n_random_pairs": len(rand_pairs),
        "FLAT_FILLERS": {"gold_cos_mean": float(gf.mean()), "gold_cos_ci95": ci(gf),
                         "random_cos_mean": float(rf.mean()), "random_cos_ci95": ci(rf),
                         "discriminative_signal_gold_minus_random": sig_flat},
        "BOUND_PAIRS": {"gold_cos_mean": float(gb.mean()), "gold_cos_ci95": ci(gb),
                        "random_cos_mean": float(rb.mean()), "random_cos_ci95": ci(rb),
                        "discriminative_signal_gold_minus_random": sig_bound},
        "SURVIVING_FRACTION_of_discriminative_signal_bound_over_flat": survive,
        "predicted_from_relation_agreement_p": float(np.sum(p * p)),
    }

    vmsg = (f"On the REAL C3 corpus, holding content fixed and varying only whether the "
            f"relation label is part of the symbol: R_eff={r_eff:.2f} relations "
            f"(p(agree)={float(np.sum(p*p)):.4f}); binding splits each lemma's symbol set by "
            f"{frag['symbol_split_factor']:.2f}x and drops repeat-coherence from "
            f"{frag['mean_repeat_coherence_FLAT']:.2f} to "
            f"{frag['mean_repeat_coherence_BOUND']:.2f}. The discriminative cross-item signal "
            f"(gold minus random count-vector cosine) falls from {sig_flat:.4f} FLAT to "
            f"{sig_bound:.4f} BOUND -- {survive*100:.1f}% survives. DIAGNOSTIC: content held "
            f"fixed, so this is the cost of BINDING ALONE and is NOT the A1-vs-A2 contrast.")

    metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION,
               "run_mode": "smoke" if _a.smoke else "full",
               "cell_class": "DIAGNOSTIC -- no pre-registered PASS/FAIL band",
               "encoder_stats": enc.stats(), "fragmentation": frag,
               "cross_item_evidence": evidence,
               "verdict": "MEASURED", "verdict_msg": vmsg, "summary": vmsg,
               "elapsed_s": time.time() - t0}
    write_metrics(out_dir, metrics)
    print(json.dumps({"fragmentation": frag, "cross_item_evidence": evidence}, indent=1))
    print("VERDICT_MSG:", vmsg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
