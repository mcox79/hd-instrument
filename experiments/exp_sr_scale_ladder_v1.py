"""THE NAMED RE-TEST: is the successor representation STARVED, or is it WRONG?

WHY. `exp_substrate_end_to_end_readout_v1` (spec v2_sr) measured SR at held-out hit@1 0.00111
against a 0.02333 co-occurrence floor -- the worst substrate route. It was filed
UNTESTABLE-AT-THIS-SCALE rather than REFUTED, because the matrix it was built on had **4,596
observed transitions across 2,114 states and a MEDIAN OF ONE distinct successor per word**. That
is not a test of a predictive map. The filing named exactly one way to settle it: rebuild on
10-50x the transitions. This is that cell.

*** THE ONE THING THAT MAKES THIS A LADDER AND NOT FIVE UNRELATED RUNS: THE EVALUATION POPULATION
IS HELD FIXED. *** Reading more text grows the vocabulary, which grows the candidate pool, which
makes the task harder for EVERY arm -- and that is exactly how the previous run's floor FELL
(0.02333 -> 0.01889) while SR rose. Two moving variables, no slope. Here:
  - the CANDIDATE POOL is frozen to the SMALLEST rung's vocabulary;
  - the ITEMS are frozen, and every target is drawn from that same frozen vocabulary;
  - the corpora are NESTED, so a bigger rung is a superset -- the ladder is about SIZE, never
    about WHICH text;
  - only the number of sentences the TRANSITION MATRIX is estimated from varies.

PRE-COMMITTED READINGS, before any number exists:
  (i)   SR rises with scale and CLEARS the floor's upper bound at some rung -> IT WAS STARVED, and
        the transitions-per-state at which it turns on IS THE FINDING, not the hit rate.
  (ii)  SR rises but extrapolates to need far more text than a child hears (~1e7-1e8 tokens) ->
        THE MACHINERY IS NOT BRAIN-FAITHFUL. Report the extrapolated requirement explicitly. This
        is the MOST USEFUL outcome the cell can produce.
  (iii) SR is FLAT across a 50x range -> starvation is REFUTED as the explanation and D7 over lemma
        transitions is a real negative. That closes a brain-pinned route with a measurement.
  (iv)  SR beats the floor only at gamma ~ 0.1 -> it is the 1-step counter wearing a matrix.

CONTROLS THAT ARE NOT OPTIONAL: both floors REBUILT ON EACH RUNG'S OWN CORPUS (never imported
across rungs -- a floor is a property of the representation it was computed on); a bootstrap CI at
every rung; and any rung whose CI half-width exceeds the chance-to-floor interval is marked
UNDERPOWERED rather than given a reading.

ITEM PRIORITY: the items are published prose predating this project, and the gold is the word
actually present in the sentence. No detector of ours selected or labelled them.

Run: python experiments/exp_sr_scale_ladder_v1.py --mode smoke
     python experiments/exp_sr_scale_ladder_v1.py --mode full
"""
import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import json
import random
import sys
import time
from typing import Dict, List, Optional, Sequence

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.corpus_registry import CorpusRegistry
from hdlab.reading_grounding_loop import content_lemmas
from hdlab.successor_representation import (SparseSuccessorRepresentation,
                                            build_transition_matrix_sparse)

CELL = "exp_sr_scale_ladder_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
SPEC_VERSION = "v1"
CORPUS = "simplewiki"
GAMMAS = (0.1, 0.9)
TOP_K = 5
N_BOOT = 2000


def _boot_ci(x: np.ndarray, rng: np.random.Generator, n: int = N_BOOT):
    if x.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, x.size, size=(n, x.size))
    m = x[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(lo), float(hi), float((hi - lo) / 2.0)


def _run(seed: int, rungs: Sequence[int], n_items: int, corpus: str) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)
    biggest = max(rungs)
    need = biggest + 8 * n_items
    # THE SHELF CAPS AT 20,000 SENTENCES PER CORPUS BY DEFAULT. The top rung of this ladder is
    # 40,000, so the default would have SILENTLY TRUNCATED it and the ladder's most important rung
    # would have been a duplicate of a smaller one wearing a bigger label. Raised explicitly, and
    # the assertion below fails LOUDLY rather than quietly shortening the ladder.
    reg = CorpusRegistry(max_sentences_per_corpus=max(need + 1000, 20000))
    if corpus not in reg.handles:
        raise SystemExit(f"corpus {corpus!r} not on the shelf")

    sents = reg.handles[corpus].take(need)
    if len(sents) < biggest + n_items:
        raise SystemExit(
            f"corpus too small OR the shelf cap bit: got {len(sents)} sentences, need "
            f"{biggest + n_items} for rung {biggest}. Raise max_sentences_per_corpus.")
    train_all = sents[:biggest]
    held_out = sents[biggest:]

    # THE FROZEN POPULATION. Vocabulary of the SMALLEST rung -- every rung can answer these, and
    # the pool never changes size, so a rise cannot be an easier task in disguise.
    smallest = min(rungs)
    frozen_vocab = sorted({l for s in train_all[:smallest] for l in content_lemmas(s)})
    frozen_set = set(frozen_vocab)

    items = []
    for s in held_out:
        cands = [l for l in content_lemmas(s) if l in frozen_set]
        if len(cands) < 2:
            continue
        items.append((s, rng.choice(cands)))
        if len(items) >= n_items:
            break

    out: dict = {"seed": seed, "corpus": corpus, "rungs": list(rungs),
                 "pool_size_FROZEN": len(frozen_vocab), "n_items": len(items),
                 "chance_at_1": 1.0 / max(len(frozen_vocab), 1), "by_rung": {}}

    for rung in rungs:
        t0 = time.time()
        train = train_all[:rung]                       # NESTED: a bigger rung is a superset
        seqs = [[l for l in content_lemmas(s) if l in frozen_set] for s in train]
        seqs = [s for s in seqs if len(s) > 1]
        n_trans = sum(len(s) - 1 for s in seqs)

        _, P = build_transition_matrix_sparse(seqs, vocab=frozen_vocab, window=1)
        srs = {g: SparseSuccessorRepresentation(frozen_vocab, P, gamma=g, tol=1e-4)
               for g in GAMMAS}

        # FLOORS REBUILT ON THIS RUNG'S OWN CORPUS. Never imported across rungs.
        freq: collections.Counter = collections.Counter()
        cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for s in seqs:
            for a in s:
                freq[a] += 1
            for a in s:
                for b in s:
                    if a != b:
                        cooc[b][a] += 1
        freq_rank = [w for w, _ in freq.most_common(TOP_K)]

        hits: Dict[str, List[int]] = {f"SR_g{g}": [] for g in GAMMAS}
        hits["COOC_floor"] = []
        hits["FREQ_floor"] = []
        for sent, tgt in items:
            cue = [l for l in content_lemmas(sent) if l != tgt and l in frozen_set]
            for g in GAMMAS:
                r = srs[g].rank_from_cue(cue, top_k=TOP_K, exclude=cue) if cue else []
                hits[f"SR_g{g}"].append(int(r[:1] == [tgt]))
            c: collections.Counter = collections.Counter()
            for l in cue:
                c.update(cooc.get(l, {}))
            for w in cue:
                c.pop(w, None)
            r = [w for w, _ in c.most_common(TOP_K)]
            hits["COOC_floor"].append(int(r[:1] == [tgt]))
            hits["FREQ_floor"].append(int(freq_rank[:1] == [tgt]))

        block: dict = {"n_sentences": len(train), "n_transitions": n_trans,
                       "transitions_per_state": n_trans / max(len(frozen_vocab), 1),
                       "nnz": int(P.nnz), "seconds": round(time.time() - t0, 1)}
        for k, v in hits.items():
            x = np.asarray(v, dtype=np.float64)
            lo, hi, hw = _boot_ci(x, nprng)
            block[k] = {"hit@1": float(x.mean()), "ci_lo": lo, "ci_hi": hi,
                        "ci_half_width": hw}
        bar = block["COOC_floor"]["ci_hi"]
        block["_credible_bar_cooc_upper"] = bar
        for g in GAMMAS:
            k = f"SR_g{g}"
            block[k]["clears_credible_bar"] = bool(block[k]["hit@1"] > bar)
        # UNDERPOWERED is a verdict, not a footnote.
        span = max(bar - out["chance_at_1"], 1e-12)
        block["_underpowered"] = bool(block[f"SR_g{GAMMAS[-1]}"]["ci_half_width"] > span)
        out["by_rung"][str(rung)] = block
        print(f"  rung {rung:6d}  trans/state {block['transitions_per_state']:7.2f}  "
              f"SR_g{GAMMAS[-1]} {block[f'SR_g{GAMMAS[-1]}']['hit@1']:.5f}  "
              f"COOC {block['COOC_floor']['hit@1']:.5f}  ({block['seconds']}s)", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--corpus", default=CORPUS)
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    rungs = (300, 1200) if smoke else (750, 3000, 12000, 40000)
    n_items = 60 if smoke else 400
    seeds = (20260819,) if smoke else (20260819, 7, 101)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for seed in seeds:
        key = unit_key(SPEC_VERSION, a.mode, a.corpus, seed)
        if key in done:
            print(f"[skip] {key}", flush=True)
            continue
        print(f"[run ] {key}", flush=True)
        r = _run(seed, rungs, n_items, a.corpus)
        r["unit_key"] = key
        if smoke:
            print(json.dumps(r, indent=2, default=str))
        else:
            record_unit(OUTPUT_DIR, key, r)

    if smoke:
        print("SMOKE OK")
        return 0

    units = load_units(OUTPUT_DIR)
    metrics = {
        "cell": CELL, "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full", "corpus": a.corpus, "spec": SPEC_VERSION,
        "n_units": len(units),
        "items_predate_mechanism": True,
        "items_predate_note": ("Published prose predating this project; the gold is the word "
                               "actually in the sentence. No detector of ours selected it."),
        "population_held_fixed": True,
        "population_note": ("Candidate pool and items are FROZEN to the smallest rung's "
                            "vocabulary, and the rung corpora are NESTED, so only the amount of "
                            "text the transition matrix is estimated from varies."),
        "units": units,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(units)} units in {time.time() - t0:.0f}s -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
