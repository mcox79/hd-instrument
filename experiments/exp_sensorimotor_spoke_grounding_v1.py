"""CAN A SENSORIMOTOR SPOKE PICK A BETTER MEANING THAN COUNTING WORDS? Scored inside the substrate.

WHY THIS CELL, AND WHY ON THIS INSTRUMENT RATHER THAN THE READ-OUT ONE.
The substrate's text channel has a measured ceiling, and the residue is not in text: pairwise
sensorimotor features reach 0.6413 where co-occurrence tops out at 0.3067, replicated unfitted on
human similarity ratings (rho 0.3171 vs 0.0826, paired bootstrap CI [+0.1605, +0.3155]). That was
an OFFLINE feature table. Nothing had tested whether the substrate can USE such a channel.

*** IT IS SCORED HERE BECAUSE THE READ-OUT CELL PROVABLY CANNOT SEE IT. ***
`exp_substrate_end_to_end_readout_v1` v3 established that the read-out never consults grounded
facts: consolidation ablated to ZERO changed the read-out in 9 of 12 cells not at all, and the
mechanism is a code fact -- `recall_sentence` reads episodic DG codes and never touches
`state.store`. A spoke feeds the consolidated side. Scoring it there would have produced a
guaranteed null. THIS instrument scores the grounded facts directly, which is the side a spoke
reaches.

THE BAR IS `TOP_COOCCURRENT`, NOT RANDOM, AND THAT IS PRE-REGISTERED.
The grounding-precision run measured SUBSTRATE 0.0244 against RANDOM_ANCHOR 0.0031 -- above
chance -- and TOP_COOCCURRENT 0.0573 beating the substrate in ALL THREE seeds. Beating random was
never the bar and clearing it would mean nothing.

BRAIN CLAIM AND WHAT IS OURS (ORGAN_MAP B5; the organ's own docstring carries the citations):
  PINNED     modality-specific cortex feeds the anterior temporal hub; text-only channels recover
             sensory meaning poorly and motor meaning minimally (Xu et al. 2025).
  BOUNDING   a sensory-INDEPENDENT code for object colour exists in the congenitally blind
             (Wang et al. 2020), so a spoke is not the only route. Not over-claimed.
  OURS       "nearest in spoke space selects the meaning" is OUR-INVENTION-BEING-TESTED. The
             hub-spoke combination rule is UNPINNED; there is no equation to be faithful to.
  SUPPLY     the norms are HUMAN RATINGS. Admissible (static, offline, no LLM at inference) but
             the substrate does not GROW this spoke. No result here is the substrate having
             learned perceptual structure.

EVERY RANKING ARM SEES THE IDENTICAL CANDIDATE POOL. The candidates are the words co-occurring
with the term in the text the substrate actually read, filtered to those with norms, and the SAME
filtered pool is handed to every arm including TOP_COOCCURRENT. Arms differ in the RANKING RULE
and in nothing else. The number of items the norm filter removed is REPORTED, because a control
that excludes nothing is not a control.

ARMS
  TOP_COOCCURRENT   the candidate the term co-occurs with most            <- THE BAR
  SPOKE_EUCLID      the candidate nearest in sensorimotor z-space
  SPOKE_COSINE      the same, by cosine -- the metric the existing organ uses
  SHUFFLED_NORMS    SPOKE_EUCLID with every profile permuted onto another word   <- CAN-FAIL
  RANDOM_CANDIDATE  a candidate drawn at random from the same pool
  SUBSTRATE         the anchor the consolidation gate actually assigned (continuity)

PRE-COMMITTED READINGS, written before any number from this cell exists:
  (A) SPOKE beats TOP_COOCCURRENT CI-separated on the paired test, AND beats SHUFFLED_NORMS ->
      the spoke supplies meaning the text channel does not. Report which metric and note that the
      norms are supplied, not learned.
  (B) SPOKE ties or loses to TOP_COOCCURRENT -> the offline 0.6413 does NOT transfer into the
      substrate's own grounding decision. A real negative about the CHANNEL AS WIRED HERE, and it
      must be reported as one. It is NOT a refutation of the sensorimotor finding, which was a
      different task and scorer.
  (C) SPOKE ties SHUFFLED_NORMS -> whatever the arm is scoring, it is not the norms. Every other
      number in the cell is void, and this is checked FIRST.
  (D) fewer than 300 scorable items, or coverage below 50% -> UNDERPOWERED / UNTESTABLE. Report
      the n and the required n and issue NO verdict. A width is not an effect.

Run: python experiments/exp_sensorimotor_spoke_grounding_v1.py --mode smoke
     python experiments/exp_sensorimotor_spoke_grounding_v1.py --mode full
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

from hdlab.reading_grounding_loop import content_lemmas
from hdlab.sensorimotor_spoke import coverage, has_profile, nearest, profile, shuffled_profiles
from hdlab.substrate import Substrate

CELL = "exp_sensorimotor_spoke_grounding_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
GOLD = os.path.join(_REPO, "data", "conceptnet_gold_v1", "edges.jsonl")
SPEC = "v1_spoke"
SEEDS = (20260819, 7, 101)
N_BOOT = 2000
N_PERM = 2000
MIN_SCORABLE = 300
MIN_COVERAGE = 0.50
MAX_CANDIDATES = 50      # SWEPT NOWHERE YET: stated so the cap is visible, not silent


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

    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for sent in sub.state.sentence_pool:
        ls = content_lemmas(sent)
        for x in ls:
            for y in ls:
                if x != y:
                    cooc[x][y] += 1

    # ---- ITEM CONSTRUCTION. Every arm gets the SAME candidates, and every exclusion is counted.
    items: List[dict] = []
    drop_no_gold = drop_no_cooc = drop_no_term_profile = drop_too_few_cands = 0
    raw_cand_pool: List[str] = []      # PRE-FILTER, for an honest coverage number
    for a, b in gated:
        if a not in nb:
            drop_no_gold += 1
            continue
        raw_cands = [w for w, _ in cooc.get(a, collections.Counter()).most_common(MAX_CANDIDATES)
                     if w != a]
        if not raw_cands:
            drop_no_cooc += 1
            continue
        raw_cand_pool.extend(raw_cands)
        if not has_profile(a):
            drop_no_term_profile += 1
            continue
        cands = [w for w in raw_cands if has_profile(w)]
        if len(cands) < 2:
            drop_too_few_cands += 1
            continue
        items.append({"term": a, "gate_anchor": b, "cands": cands,
                      "counts": {w: cooc[a][w] for w in cands},
                      "n_cands_before_norm_filter": len(raw_cands)})

    cov_terms = coverage([a for a, _ in gated])
    # COVERAGE MUST BE MEASURED BEFORE THE FILTER IT DESCRIBES. The first version of this line
    # measured coverage over the ALREADY-FILTERED candidate list and therefore reported 1.0 by
    # construction -- a number that cannot fail, which is the same defect as a control that
    # excludes nothing. Measured over the RAW pool it is a real quantity.
    cov_cands = coverage(raw_cand_pool)
    all_cands = [w for it in items for w in it["cands"]]
    cands_removed = sum(it["n_cands_before_norm_filter"] - len(it["cands"]) for it in items)

    # SHUFFLED NORMS: one permuted table per unit, built over every word this unit can ask about.
    vocab = sorted({it["term"] for it in items} | set(all_cands))
    shuf = shuffled_profiles(vocab, seed=seed)

    def score(pick) -> np.ndarray:
        return np.asarray([int(bool(pick(it)) and pick(it) in nb.get(it["term"], ()))
                           for it in items], dtype=np.float64)

    arms = {
        "TOP_COOCCURRENT": score(lambda it: max(sorted(it["cands"]),
                                                key=lambda w: it["counts"][w])),
        "SPOKE_EUCLID": score(lambda it: nearest(it["term"], it["cands"], metric="euclid")),
        "SPOKE_COSINE": score(lambda it: nearest(it["term"], it["cands"], metric="cosine")),
        "SHUFFLED_NORMS": score(lambda it: nearest(it["term"], it["cands"], metric="euclid",
                                                   profiles=shuf)),
        "RANDOM_CANDIDATE": score(lambda it: rng.choice(it["cands"])),
        "SUBSTRATE": score(lambda it: it["gate_anchor"]),
    }

    out: dict = {
        "seed": seed, "n_read": read_total, "read_seconds": round(read_s, 1),
        "corpora_visited": corpora,
        "n_grounded": len(gated), "n_scorable": len(items),
        "n_refused": len(sub.state.refusals),
        "max_candidates": MAX_CANDIDATES,
        "mean_candidates": float(np.mean([len(it["cands"]) for it in items])) if items else None,
        # EVERY exclusion counted. A control that removes nothing is not a control.
        "dropped_no_gold_entry": drop_no_gold,
        "dropped_no_cooccurrence": drop_no_cooc,
        "dropped_term_has_no_norms": drop_no_term_profile,
        "dropped_fewer_than_2_candidates_with_norms": drop_too_few_cands,
        "coverage_terms": cov_terms,
        "coverage_candidates_PRE_FILTER": cov_cands,
        "candidates_removed_by_norm_filter": cands_removed,
        "coverage_note": ("coverage_candidates is measured over the RAW co-occurrence pool, "
                          "BEFORE the norm filter. Measured after it, it would read 1.0 by "
                          "construction and could not fail."),
        "UNDERPOWERED": len(items) < MIN_SCORABLE,
        "UNTESTABLE_LOW_COVERAGE": cov_terms["coverage"] < MIN_COVERAGE,
        "min_scorable_required": MIN_SCORABLE,
        "min_coverage_required": MIN_COVERAGE,
    }
    for name, x in arms.items():
        lo, hi, hw = _boot_ci(x, nprng)
        out[name] = {"precision": float(x.mean()) if x.size else None,
                     "hits": int(x.sum()), "n": int(x.size),
                     "ci_lo": lo, "ci_hi": hi, "ci_half_width": hw}
    if arms["SPOKE_EUCLID"].size:
        for name in arms:
            if name == "SPOKE_EUCLID":
                continue
            out[name]["paired_perm_p_vs_SPOKE_EUCLID"] = _paired_perm(
                arms["SPOKE_EUCLID"], arms[name], nprng)
    # READING (C) IS CHECKED IN CODE AND FIRST. If the permuted table ties the real one, the arm
    # is not scoring the norms and nothing else in this unit means anything.
    out["READING_C_norms_carry_it"] = bool(
        arms["SPOKE_EUCLID"].mean() > arms["SHUFFLED_NORMS"].mean()) if items else None

    print("  seed %d: read %d, grounded %d, scorable %d | SPOKE_EUCLID %.4f (%d) vs "
          "TOP_COOCCURRENT %.4f (%d) vs SHUFFLED %.4f (%d)%s"
          % (seed, read_total, len(gated), len(items),
             out["SPOKE_EUCLID"]["precision"] or 0.0, out["SPOKE_EUCLID"]["hits"],
             out["TOP_COOCCURRENT"]["precision"] or 0.0, out["TOP_COOCCURRENT"]["hits"],
             out["SHUFFLED_NORMS"]["precision"] or 0.0, out["SHUFFLED_NORMS"]["hits"],
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
            print(json.dumps(r, indent=2, default=str)[:3500])
        else:
            record_unit(OUTPUT_DIR, key, r)

    if smoke:
        print("SMOKE OK")
        return 0

    units = load_units(OUTPUT_DIR)
    rows = list(units.values()) if isinstance(units, dict) else list(units)
    rows = [u for u in rows if str(u.get("unit_key", "")).startswith(SPEC + "|")]
    metrics = {
        "cell": CELL, "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full", "spec": SPEC, "n_units": len(rows),
        "gold": "data/conceptnet_gold_v1 -- 422,082 edges, provenance-filtered, NO WordNet source",
        "the_bar": "TOP_COOCCURRENT (pre-registered). Beating RANDOM_CANDIDATE is not the bar.",
        "can_fail_control": "SHUFFLED_NORMS -- every profile permuted onto another word, "
                            "marginals preserved exactly. Reading (C) is checked first.",
        "items_predate_mechanism": True,
        "items_predate_note": (
            "The gold is a crowd/Wiktionary knowledge base built years before this project, and "
            "the Lancaster norms are human ratings collected independently of it. The TERMS are "
            "whatever the substrate chose to ground, so the ITEM SET is ours -- which is why "
            "every arm is scored on the identical items and the identical candidate pool."),
        "supply_not_learning": (
            "The sensorimotor norms are SUPPLIED human ratings. Admissible under the static "
            "offline-asset ruling, but no result here is the substrate having LEARNED "
            "perceptual structure."),
        "readings_c_norms_carry_it": [u.get("READING_C_norms_carry_it") for u in rows],
        "units": rows,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(rows)} units in {time.time() - t0:.0f}s -> {path}")
    print("[gate] READING (C) norms carry it, per seed: %s"
          % metrics["readings_c_norms_carry_it"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
