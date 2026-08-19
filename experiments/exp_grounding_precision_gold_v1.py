"""DOES THE SUBSTRATE GROUND WORDS TO THE RIGHT MEANING? Scored against an independent gold.

WHY THIS CELL. The substrate's stated output is an auditable store of facts, each traceable to the
sentence it came from. It grounds terms and REFUSES roughly three quarters of what reaches its
gate. **Nothing had ever asked whether what it accepts is CORRECT.** Probes on 2026-08-19 put the
accepted set at 0.0446 against a same-terms random-anchor twin at 0.0179 -- **5 hits against 2**,
which is a width and not an effect. The named way to settle it was more grounded items, which
means more reading. This is that run.

THE GOLD IS INDEPENDENT AND ITS ADMISSIBILITY WAS CHECKED BEFORE THE CELL WAS WRITTEN.
`data/conceptnet_gold_v1`: 422,082 edges, **provenance-filtered so NO WordNet-sourced edge is
present**, meaning relations only (`/r/DerivedFrom` deliberately excluded -- it relates word FORMS,
not senses, and would reward our morphology instead of our comprehension). *The convenient
pre-extracted ConceptNet file in `data/datasets/` carries NO provenance field and is inadmissible;
it is not used here.*

*** THE CONTROL THAT DECIDES THIS CELL IS `RANDOM_ANCHOR`, NOT A FLOOR OVER OTHER ITEMS. ***
Precision is P(anchor is a gold neighbour of the term), so a term with many gold neighbours is
easier to be right about -- and the gate was MEASURED to accept terms with twice the gold degree
(42.3 vs 21.7). Any comparison against a different item set is confounded by that. `RANDOM_ANCHOR`
holds the TERMS FIXED and randomises only the ANSWER, so it isolates "is this meaning right" from
"is this term easy". `RAW_DEGREE_MATCHED` is reported too, but the paired twin is the decider.

ARMS
  SUBSTRATE            the meaning the consolidation gate actually assigned
  RANDOM_ANCHOR        same terms, an anchor drawn at random from the same emitted pool   <- DECIDER
  MOST_FREQUENT_ANCHOR same terms, always the single most common anchor
  TOP_COOCCURRENT      same terms, the word each co-occurs with most in the text that was read
  RAW_DEGREE_MATCHED   ungated argmax items resampled to the gated gold-degree distribution

PRE-COMMITTED READINGS, before any number exists:
  (i)   SUBSTRATE beats RANDOM_ANCHOR CI-separated on the paired test -> the gate assigns real
        meanings, and the degeneracy is a separate problem from the correctness.
  (ii)  SUBSTRATE ties RANDOM_ANCHOR -> the gate SELECTS terms but does not assign meanings.
        That is a real negative about grounding and it must be reported as one.
  (iii) SUBSTRATE beats RANDOM but ties TOP_COOCCURRENT -> what it has learned is co-occurrence,
        which is this project's standing diagnosis arriving on a third instrument.
  (iv)  fewer than ~300 scorable items -> UNDERPOWERED; report the n and the required n, and do
        NOT issue a verdict. A width is not an effect.

Run: python experiments/exp_grounding_precision_gold_v1.py --mode smoke
     python experiments/exp_grounding_precision_gold_v1.py --mode full
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
from typing import Dict, List, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.reading_grounding_loop import content_lemmas
from hdlab.substrate import Substrate

CELL = "exp_grounding_precision_gold_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
GOLD = os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl")
SPEC = "v1"
SEEDS = (20260819, 7, 101)
N_BOOT = 2000
N_PERM = 2000
MIN_SCORABLE = 300          # reading (iv): below this the cell reports UNDERPOWERED, not a verdict


def load_gold() -> Dict[str, set]:
    nb: Dict[str, set] = collections.defaultdict(set)
    with open(GOLD, "r", encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            nb[e["subj"]].add(e["obj"])
            nb[e["obj"]].add(e["subj"])
    return nb


def _boot_ci(x: np.ndarray, rng: np.random.Generator):
    if x.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, x.size, size=(N_BOOT, x.size))
    m = x[idx].mean(axis=1)
    lo, hi = np.percentile(m, [2.5, 97.5])
    return float(lo), float(hi), float((hi - lo) / 2.0)


def _paired_perm(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> float:
    d = a - b
    obs = abs(d.mean())
    flips = rng.integers(0, 2, size=(N_PERM, d.size)) * 2 - 1
    return float((np.sum(np.abs((flips * d).mean(axis=1)) >= obs) + 1) / (N_PERM + 1))


def _run(seed: int, n_sentences: int, chunk: int, nb: Dict[str, set]) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)
    sub = Substrate(seed=seed)
    t0 = time.time()
    read_total = 0
    corpora: List[str] = []
    while read_total < n_sentences:
        r = sub.read(n_sentences=chunk, batch=50, max_patches=3, consolidate_every=200)
        if r.n_sentences == 0:
            break
        read_total += r.n_sentences
        corpora.extend(c for c in r.corpora_visited if c not in corpora)
    read_s = time.time() - t0

    gated = [(str(p.get("subject", "")), str(p.get("object", "")))
             for p in sub.state.provenance]
    gated = [(a, b) for a, b in gated if a and b and " " not in b]
    scorable = [(a, b) for a, b in gated if a in nb]
    anchors = [b for _, b in gated] or ["way"]
    most_common = collections.Counter(anchors).most_common(1)[0][0]

    # co-occurrence over the text actually read, for the TOP_COOCCURRENT arm
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for sent in sub.state.sentence_pool:
        ls = content_lemmas(sent)
        for x in ls:
            for y in ls:
                if x != y:
                    cooc[x][y] += 1

    def hits(fn) -> np.ndarray:
        return np.asarray([int(bool(fn(a, b)) and fn(a, b) in nb.get(a, ()))
                           for a, b in scorable], dtype=np.float64)

    arms = {
        "SUBSTRATE": hits(lambda a, b: b),
        "RANDOM_ANCHOR": hits(lambda a, b: rng.choice(anchors)),
        "MOST_FREQUENT_ANCHOR": hits(lambda a, b: most_common),
        "TOP_COOCCURRENT": hits(lambda a, b: (cooc[a].most_common(1)[0][0]
                                              if cooc.get(a) else "")),
    }

    out: dict = {
        "seed": seed, "n_read": read_total, "read_seconds": round(read_s, 1),
        "corpora_visited": corpora,
        "n_grounded": len(gated), "n_scorable": len(scorable),
        "coverage": len(scorable) / max(len(gated), 1),
        "n_refused": len(sub.state.refusals),
        "distinct_anchors": len(set(anchors)),
        "anchor_diversity": len(set(anchors)) / max(len(gated), 1),
        "top_anchor": most_common,
        "top_anchor_share": collections.Counter(anchors)[most_common] / max(len(gated), 1),
        "mean_gold_degree_gated": float(np.mean([len(nb.get(a, ())) for a, _ in scorable]))
        if scorable else None,
        "UNDERPOWERED": len(scorable) < MIN_SCORABLE,
        "min_scorable_required": MIN_SCORABLE,
    }
    for name, x in arms.items():
        lo, hi, hw = _boot_ci(x, nprng)
        out[name] = {"precision": float(x.mean()) if x.size else None,
                     "hits": int(x.sum()), "n": int(x.size),
                     "ci_lo": lo, "ci_hi": hi, "ci_half_width": hw}
    if arms["SUBSTRATE"].size:
        for name in ("RANDOM_ANCHOR", "MOST_FREQUENT_ANCHOR", "TOP_COOCCURRENT"):
            out[name]["paired_perm_p_vs_SUBSTRATE"] = _paired_perm(
                arms["SUBSTRATE"], arms[name], nprng)
    print("  seed %d: read %d, grounded %d, scorable %d, SUBSTRATE %.4f (%d hits), "
          "RANDOM %.4f (%d hits)%s"
          % (seed, read_total, len(gated), len(scorable),
             out["SUBSTRATE"]["precision"] or 0.0, out["SUBSTRATE"]["hits"],
             out["RANDOM_ANCHOR"]["precision"] or 0.0, out["RANDOM_ANCHOR"]["hits"],
             "  [UNDERPOWERED]" if out["UNDERPOWERED"] else ""), flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    n_sent = 2000 if smoke else 40000
    chunk = 400 if smoke else 800
    seeds = SEEDS[:1] if smoke else SEEDS

    nb = load_gold()
    print(f"[gold] {len(nb)} terms with at least one edge", flush=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for seed in seeds:
        key = unit_key(SPEC, a.mode, seed)
        if key in done:
            print(f"[skip] {key}", flush=True)
            continue
        print(f"[run ] {key}", flush=True)
        r = _run(seed, n_sent, chunk, nb)
        r["unit_key"] = key
        if smoke:
            print(json.dumps(r, indent=2, default=str)[:2500])
        else:
            record_unit(OUTPUT_DIR, key, r)

    if smoke:
        print("SMOKE OK")
        return 0
    units = load_units(OUTPUT_DIR)
    metrics = {
        "cell": CELL, "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full", "spec": SPEC, "n_units": len(units),
        "gold": "data/conceptnet_gold_v1 -- 422,082 edges, provenance-filtered, NO WordNet source",
        "items_predate_mechanism": True,
        "items_predate_note": ("The gold is a crowd/Wiktionary knowledge base built years before "
                               "this project. The TERMS are whatever the substrate chose to "
                               "ground, so the ITEM SET is ours -- which is why the deciding "
                               "control holds the terms fixed and randomises only the ANSWER."),
        "deciding_control": "RANDOM_ANCHOR (same terms, random answer)",
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
