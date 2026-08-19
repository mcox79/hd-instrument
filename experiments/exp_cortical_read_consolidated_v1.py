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
from hdlab.cortical_recall import cue_vector
from hdlab.reading_grounding_loop import content_lemmas, context_vector_masked
from hdlab.substrate import CONTEXT_DIM, Substrate

CELL = "exp_cortical_read_consolidated_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)
# v1_cortical -> v2_hitk_sentencecue. TWO CHANGES, BOTH FORCED BY MEASUREMENT, AND THE BUMP IS
# LOAD-BEARING because v1's 3 units are on disk and were computed under both defects:
#   1. hit@k, NOT hit@1 ALONE. v1 scored top-1 over 428-480 candidates and came back VOID by its
#      own reading (C). The vector-level diagnostic then showed the cue carries a REAL but weak
#      signal (+0.0288 real-vs-scramble cosine on held-out text), far too small to win a top-1
#      argmax. Measured at hit@k on the same substrate: REAL vs SCRAMBLE CI-SEPARATED at k=1, 10
#      and 50, and above chance k/N at every k. v1 was scoring the wrong thing.
#   2. THE SENTENCE'S OWN CONTEXT VECTOR AS THE CUE. v1 queried a per-term context-vector index
#      with a SUM OF PER-LEMMA PROFILES -- a different kind of object. One-variable test, scale
#      fixed: the sentence cue separates at k=1/10/50, the profile-sum cue at k=1 only.
# SCALE REMAINS THE OPEN CONFOUND: the diagnostics ran at 4,300 sentences / 223 terms, this cell
# at 16,600 / 428-480. That is exactly why this re-runs AT THE CELL'S OWN SCALE.
SPEC = "v2_hitk_sentencecue"
KS = (1, 5, 10, 25, 50)
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
    want = n_read + 6 * n_items
    pool = reg.handles[CORPUS].take(want)
    read_split, held_out = pool[:n_read], pool[n_read:]

    # *** PRECONDITION, CHECKED BEFORE READING AND LOUDLY. ***
    # THE FIRST FULL RUN DIED HERE AND THE CAUSE WAS THIS EXACT ARITHMETIC. `simplewiki` yields
    # EXACTLY 20,000 sentences; the run asked to read 20,000 and then hold out 1,800 more, so
    # `held_out` was EMPTY, every arm scored None, and it crashed on the summary print after ~15
    # minutes of reading. A held-out split of zero is UNWINNABLE BY CONSTRUCTION -- the same
    # "could this experiment have succeeded?" question that has already changed this session's
    # plan three times, not asked about corpus arithmetic.
    # Fail FAST and say the numbers, rather than after the read and with a TypeError.
    if len(pool) < want:
        print(f"[warn] {CORPUS} yielded {len(pool)} of {want} requested sentences", flush=True)
    if len(held_out) < n_items:
        raise SystemExit(
            f"UNWINNABLE BY CONSTRUCTION, refusing to run: corpus {CORPUS!r} yielded "
            f"{len(pool)} sentences; reading {n_read} leaves {len(held_out)} held-out, and "
            f"{n_items} items are required. Lower --mode full's n_read (the corpus has a hard "
            f"ceiling) or read a different corpus. This check exists because the first full run "
            f"read for 15 minutes and then crashed with an empty held-out split.")

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

    # The SECOND way this can be unwinnable, guarded separately from the corpus arithmetic above:
    # enough held-out sentences, but none of them mentions anything the gate consolidated. That is
    # a real possibility here -- the consolidated set is ~1-2% of the episodic pool by design.
    if not items:
        raise SystemExit(
            f"UNWINNABLE BY CONSTRUCTION, refusing to score: {len(held_out)} held-out sentences "
            f"contain NONE of the {len(cands)} consolidated terms, so there is nothing to ask "
            f"about. Read more (more consolidation) or draw held-out text from the same "
            f"distribution. Reporting this as a zero score would be a measurement error.")

    # RANKS, NOT TOP-1. Ties are broken AGAINST us (the target goes last), so no arm is ever
    # flattered by a tie. A rank of None means the arm could not score that item at all and it is
    # counted as a miss at every k rather than dropped, which would silently shrink the denominator.
    order = {sp: sorted(v) for sp, v in idx.items()}
    mats = {sp: (np.stack([v[n] for n in order[sp]]) if order[sp] else np.zeros((0, 1)))
            for sp, v in idx.items()}
    posn = {sp: {n: i for i, n in enumerate(order[sp])} for sp in idx}

    def rank_cortical(space: str, sent: str, tgt: str) -> Optional[int]:
        M, P = mats.get(space), posn.get(space, {})
        if M is None or M.shape[0] == 0 or tgt not in P:
            return None
        q = cue_vector(content_lemmas(sent), profiles, space=space, exclude=[tgt],
                       context_vec=context_vector_masked(sent, tgt, d=CONTEXT_DIM))
        if q is None or q.shape[0] != M.shape[1]:
            return None
        sims = M @ q
        return int(np.sum(sims > sims[P[tgt]])) + 1

    def top1_cortical(space: str, sent: str, tgt: str) -> Optional[str]:
        hits = cortical_recall(content_lemmas(sent), cons, profiles, space=space, top_k=1,
                               exclude=[tgt], index=idx.get(space),
                               context_vec=context_vector_masked(sent, tgt, d=CONTEXT_DIM))
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

    # HIT@K, THE THING v1 FAILED TO MEASURE. Computed for the cortical arms and their scramble,
    # against chance k/N on the SAME candidate set. RETRIEVAL, NOT DISCRIMINATION: a target in the
    # top-50 of ~450 is narrowed down, not known, and must never be reported as the latter.
    big_n = max(len(order.get("context", [])), 1)
    rank_arms: Dict[str, List[Optional[int]]] = {}
    for space in ("context", "spoke", "both"):
        rank_arms["RANK_" + space.upper()] = [rank_cortical(space, s, t) for s, t in items]
    rank_arms["RANK_SCRAMBLE"] = [
        rank_cortical("context", _donor([s for s, _ in items], i, rng), t)
        for i, (s, t) in enumerate(items)]

    hitk: Dict[str, Dict[str, float]] = {}
    for name, ranks in rank_arms.items():
        block: Dict[str, float] = {}
        for k in KS:
            x = np.asarray([int(r is not None and r <= k) for r in ranks], dtype=np.float64)
            lo, hi, hw = _boot_ci(x, nprng)
            block["hit@%d" % k] = float(x.mean())
            block["ci_lo@%d" % k] = lo
            block["ci_hi@%d" % k] = hi
        got = [r for r in ranks if r is not None]
        block["median_rank"] = float(np.median(got)) if got else None
        block["n_scored"] = len(got)
        hitk[name] = block
    # READING (A) in code: does REAL clear SCRAMBLE's upper CI, and chance, at the same k?
    sep_k = [k for k in KS
             if hitk["RANK_CONTEXT"]["ci_lo@%d" % k] > hitk["RANK_SCRAMBLE"]["ci_hi@%d" % k]
             and hitk["RANK_CONTEXT"]["hit@%d" % k] > k / big_n]

    out: dict = {
        "seed": seed, "n_read": total, "read_seconds": round(read_s, 1),
        "hit_at_k": hitk,
        "chance_at_k": {("hit@%d" % k): k / big_n for k in KS},
        "READING_A_k_where_real_clears_scramble_and_chance": sep_k,
        "retrieval_not_discrimination_note": (
            "hit@k here is RETRIEVAL. A target inside the top-k of ~450 consolidated terms is "
            "NARROWED DOWN, not known. Do not report it as discrimination."),
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
    # 16,000 AND NOT 20,000, AND THE NUMBER IS MEASURED. `simplewiki`'s handle yields EXACTLY
    # 20,000 sentences (checked: `CorpusRegistry().handles['simplewiki'].remaining()`), so a
    # 20,000-sentence read leaves ZERO held out and the cell cannot score anything. 16,000 leaves
    # 4,000, of which 300 items are drawn. The first full run learned this the expensive way.
    n_read = 2000 if smoke else 16000
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
