"""DOES THE CORTICAL READ WORK? The organ built 2026-08-19, scored on the side it can reach.

WHY THIS CELL. `exp_substrate_end_to_end_readout_v1` v3 established that every retrieval route in
this substrate addresses the EPISODIC store: consolidation could be ablated to ZERO provenance rows
and the read-out stayed identical in 9 of 12 cells. Under Complementary Learning Systems, retrieval
of CONSOLIDATED knowledge is a CORTICAL read, and that route did not exist. `hdlab/cortical_recall.py`
is it. Nothing has yet asked whether it RETRIEVES ANYTHING.

*** THE TASK IS BUILT AROUND WHAT WAS ACTUALLY CONSOLIDATED, AND THAT IS THE WHOLE POINT. ***
Measured BEFORE this cell was written (`scratch/probe_cortical_route_feasibility.py`): on the cloze
read-out task only 6.0% of held-out targets have any entry in the consolidated store, which covers
2.4% of its candidate pool. Scoring a cortical route there would read near zero from having NO
ENTRY rather than from being wrong -- an unwinnable test, not a negative. So the candidate pool
here IS the consolidated set, and chance is reported as 1/|consolidated| rather than assumed.

THAT SPARSITY IS CORRECT BEHAVIOUR AND IS NOT BEING TUNED AWAY. 2,883 episodic lemmas against 68
consolidated facts on a 1,150-sentence read, with the gate refusing ~88%. The hippocampus holds
everything; cortex holds the slowly distilled residue. A cell that "fixed" this by loosening the
gate would be measuring a different system.

THE TASK. Read. Consolidate. Then take HELD-OUT sentences the substrate never read, mask a
consolidated term out of one, and ask each route to name it from the remaining words. Text in, a
consolidated concept out, on material the mechanism did not see.

ARMS -- every one ranks over the IDENTICAL candidate set (the consolidated terms), so the arms
differ in the ROUTE and in nothing else:
  CORTICAL_CONTEXT   the new route, in accumulated-context space
  CORTICAL_SPOKE     the same route, in sensorimotor space          <- does a second spoke help?
  CORTICAL_BOTH      both spaces concatenated                       <- do they help TOGETHER?
  EPISODIC_FILTERED  the EXISTING route, its ranking filtered to the same candidates  <- the
                     comparison that says whether the cortical route ADDS anything
  COOC_floor         co-occurrence counting over the read split, same candidates  <- FLOOR
  FREQ_floor         the most frequent consolidated term; never looks at the cue    <- FLOOR
  SCRAMBLE           CORTICAL_CONTEXT on an UNRELATED donor sentence, target kept   <- can-fail

*** ITEM PRIORITY, THE FREE QUESTION: DID THE TEST ITEMS EXIST BEFORE THE MECHANISM DID? ***
The sentences are published prose predating this project and the gold is the word actually present.
BUT THE CANDIDATE SET IS OURS -- it is whatever the gate consolidated. That is stated here rather
than discovered later, and it is why FREQ_floor and SCRAMBLE both matter: they measure how much of
any score comes from the candidate set's own shape rather than from reading the cue.

PRE-COMMITTED READINGS, written before any number from this cell exists:
  (A) a CORTICAL arm beats the strongest floor's UPPER bound (floor + its own half-width),
      CI-separated -> the cortical read retrieves. Name which space.
  (B) every CORTICAL arm ties or loses to the strongest floor -> the route exists and carries
      nothing. A real negative about the ORGAN, and it must be reported as one.
  (C) SCRAMBLE ties CORTICAL_CONTEXT -> the route is not reading the cue and EVERY other number in
      this cell is void. Checked FIRST, in code.
  (D) CORTICAL beats EPISODIC_FILTERED -> the cortical route adds something the episodic one does
      not, which is the CLS claim. If it ties, say so: the two routes are then redundant and the
      fidelity argument for building it is unsupported BY THIS INSTRUMENT.
  (E) fewer than 200 scorable items, or fewer than 50 consolidated candidates -> UNDERPOWERED.
      Report the n and the required n and issue NO verdict.

Run: python experiments/exp_cortical_read_consolidated_v1.py --mode smoke
     python experiments/exp_cortical_read_consolidated_v1.py --mode full
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
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from exp_checkpoint import completed_units, load_units, record_unit, unit_key

from hdlab.corpus_registry import CorpusRegistry
from hdlab.reading_grounding_loop import content_lemmas
from hdlab.substrate import Substrate

CELL = "exp_cortical_read_consolidated_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
SPEC = "v1_cortical"
CORPUS = "simplewiki"
SEEDS = (20260819, 7, 101)
N_BOOT = 2000
N_PERM = 2000
MIN_ITEMS = 200
MIN_CANDIDATES = 50


def _boot_ci(x: np.ndarray, rng: np.random.Generator) -> Tuple[float, float, float]:
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


def _donor(cues: Sequence[str], i: int, rng: random.Random) -> str:
    """The scramble control: an UNRELATED sentence, target kept.

    A word-ORDER shuffle is a NO-OP against a bag representation and was caught tying the real cue
    at p=1.0000 in this project. Destroy the cue's CONTENT, not its order.
    """
    if len(cues) < 2:
        return cues[0]
    j = i
    while j == i:
        j = rng.randrange(len(cues))
    return cues[j]


def _run(seed: int, n_read: int, n_items: int, chunk: int) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)

    reg = CorpusRegistry()
    pool = reg.handles[CORPUS].take(n_read + 6 * n_items)
    read_split, held_out = pool[:n_read], pool[n_read:]

    sub = Substrate(seed=seed)
    t0 = time.time()
    total = 0
    while total < n_read:
        r = sub.read(corpus=CORPUS, n_sentences=chunk, batch=50, max_patches=1,
                     consolidate_every=200)
        if r.n_sentences == 0:
            break
        total += r.n_sentences
    read_s = time.time() - t0

    cons = sub.consolidated()
    cands = sorted(cons)
    profiles = sub.profile()

    # Pre-built indices, one per space, so the cost is paid once and every item sees the same one.
    from hdlab.cortical_recall import build_cortical_index, cortical_recall
    idx = {}
    for space in ("context", "spoke", "both"):
        try:
            idx[space] = build_cortical_index(cons, profiles, space=space)
        except Exception:
            idx[space] = {}

    # Floors, computed over the SAME candidate set.
    freq: collections.Counter = collections.Counter()
    cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    cand_set = set(cands)
    for sent in read_split:
        lems = content_lemmas(sent)
        for l in lems:
            if l in cand_set:
                freq[l] += 1
        for a in lems:
            for b in lems:
                if a != b and a in cand_set:
                    cooc[b][a] += 1
    freq_rank = [w for w, _ in freq.most_common()]

    items: List[Tuple[str, str]] = []          # (sentence, target)
    for sent in held_out:
        present = [l for l in content_lemmas(sent) if l in cand_set]
        if not present:
            continue
        items.append((sent, rng.choice(sorted(set(present)))))
        if len(items) >= n_items:
            break

    def top1_cortical(space: str, sent: str, tgt: str) -> Optional[str]:
        hits = cortical_recall(content_lemmas(sent), cons, profiles, space=space, top_k=1,
                               exclude=[tgt], index=idx.get(space))
        return hits[0].term if hits else None

    def top1_episodic(sent: str, tgt: str) -> Optional[str]:
        # THE EXISTING ROUTE, FILTERED TO THE SAME CANDIDATES. Without the filter it ranks over
        # ~2,883 episodic lemmas against the cortical route's few hundred, and the comparison
        # would measure pool size rather than route.
        for lem, _ in sub.recall_sentence(sent, target=tgt, top_k=200):
            if lem in cand_set and lem != tgt:
                return lem
        return None

    def top1_cooc(sent: str, tgt: str) -> Optional[str]:
        c: collections.Counter = collections.Counter()
        cue = [l for l in content_lemmas(sent) if l != tgt]
        for l in cue:
            c.update(cooc.get(l, {}))
        for w in cue:
            c.pop(w, None)
        return c.most_common(1)[0][0] if c else None

    arms: Dict[str, np.ndarray] = {}
    for space in ("context", "spoke", "both"):
        arms["CORTICAL_" + space.upper()] = np.asarray(
            [int(top1_cortical(space, s, t) == t) for s, t in items], dtype=np.float64)
    arms["EPISODIC_FILTERED"] = np.asarray(
        [int(top1_episodic(s, t) == t) for s, t in items], dtype=np.float64)
    arms["COOC_floor"] = np.asarray(
        [int(top1_cooc(s, t) == t) for s, t in items], dtype=np.float64)
    arms["FREQ_floor"] = np.asarray(
        [int((freq_rank[0] if freq_rank else None) == t) for _, t in items], dtype=np.float64)
    arms["SCRAMBLE"] = np.asarray(
        [int(top1_cortical("context", _donor([s for s, _ in items], i, rng), t) == t)
         for i, (s, t) in enumerate(items)], dtype=np.float64)

    out: dict = {
        "seed": seed, "n_read": total, "read_seconds": round(read_s, 1),
        "n_consolidated": len(cons), "n_items": len(items),
        "index_sizes": {k: len(v) for k, v in idx.items()},
        "n_provenance": len(sub.state.provenance), "n_refused": len(sub.state.refusals),
        "chance_at_1": (1.0 / len(cands)) if cands else None,
        "distinct_targets": len({t for _, t in items}),
        "UNDERPOWERED": len(items) < MIN_ITEMS or len(cands) < MIN_CANDIDATES,
        "min_items_required": MIN_ITEMS, "min_candidates_required": MIN_CANDIDATES,
    }
    for name, x in arms.items():
        lo, hi, hw = _boot_ci(x, nprng)
        out[name] = {"hit@1": float(x.mean()) if x.size else None, "hits": int(x.sum()),
                     "n": int(x.size), "ci_lo": lo, "ci_hi": hi, "ci_half_width": hw}
    floors = {k: out[k] for k in ("COOC_floor", "FREQ_floor")}
    strongest = max(floors, key=lambda k: floors[k]["hit@1"] or 0.0)
    out["_strongest_floor"] = strongest
    out["_credible_bar"] = floors[strongest]["ci_hi"]
    for name in ("CORTICAL_CONTEXT", "CORTICAL_SPOKE", "CORTICAL_BOTH", "EPISODIC_FILTERED"):
        out[name]["clears_credible_bar"] = bool((out[name]["hit@1"] or 0.0) > out["_credible_bar"])
        out[name]["perm_p_vs_strongest_floor"] = _paired_perm(arms[name], arms[strongest], nprng)
        out[name]["perm_p_vs_EPISODIC"] = _paired_perm(arms[name], arms["EPISODIC_FILTERED"], nprng)
    # READING (C) IN CODE AND FIRST.
    out["SCRAMBLE"]["perm_p_vs_CORTICAL_CONTEXT"] = _paired_perm(
        arms["CORTICAL_CONTEXT"], arms["SCRAMBLE"], nprng)
    out["READING_C_route_reads_the_cue"] = bool(
        arms["CORTICAL_CONTEXT"].mean() > arms["SCRAMBLE"].mean())

    print("  seed %d: read %d, consolidated %d, items %d | CTX %.4f SPOKE %.4f BOTH %.4f | "
          "EPI %.4f COOC %.4f SCRAM %.4f%s"
          % (seed, total, len(cons), len(items),
             out["CORTICAL_CONTEXT"]["hit@1"], out["CORTICAL_SPOKE"]["hit@1"],
             out["CORTICAL_BOTH"]["hit@1"], out["EPISODIC_FILTERED"]["hit@1"],
             out["COOC_floor"]["hit@1"], out["SCRAMBLE"]["hit@1"],
             "  [UNDERPOWERED]" if out["UNDERPOWERED"] else ""), flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    n_read = 2000 if smoke else 20000
    n_items = 60 if smoke else 300
    chunk = 400 if smoke else 800
    seeds = SEEDS[:1] if smoke else SEEDS

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for seed in seeds:
        key = unit_key(SPEC, a.mode, seed)
        if key in done:
            print(f"[skip] {key}", flush=True)
            continue
        print(f"[run ] {key}", flush=True)
        r = _run(seed, n_read, n_items, chunk)
        r["unit_key"] = key
        if smoke:
            print(json.dumps(r, indent=2, default=str)[:3000])
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
        "run_mode": "full", "spec": SPEC, "n_units": len(rows), "corpus": CORPUS,
        "what_is_scored": ("the CORTICAL read route (hdlab/cortical_recall.py), on the "
                           "consolidated side it can actually reach"),
        "items_predate_mechanism": True,
        "items_predate_note": (
            "The sentences are published prose predating this project and the gold is the word "
            "actually present. BUT THE CANDIDATE SET IS OURS -- it is whatever the gate "
            "consolidated. FREQ_floor and SCRAMBLE exist to measure how much of any score comes "
            "from the candidate set's shape rather than from reading the cue."),
        "readings_c_route_reads_the_cue": [u.get("READING_C_route_reads_the_cue") for u in rows],
        "units": rows,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(rows)} units in {time.time() - t0:.0f}s -> {path}")
    print("[gate] READING (C) route reads the cue, per seed: %s"
          % metrics["readings_c_route_reads_the_cue"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
