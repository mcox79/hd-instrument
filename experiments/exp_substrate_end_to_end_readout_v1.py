"""PHASE 2: THE END-TO-END CAN-FAIL TEST OF THE ASSEMBLED SUBSTRATE. It did not exist before.

WHY THIS CELL EXISTS. `hdlab/substrate.py` wires nine organs into one reader. Every one of them
was validated ALONE, and wiring components that each look fine is exactly how this project
accumulated 2,678 claimed passes of which 30 were vetted and 1 survived. Nothing about the
assembly should be believed until one test that CAN FAIL has been run on it.

THE TASK. Read a corpus. Then, on sentences from the SAME corpus that were NEVER READ, mask one
content word out of its own context and ask the substrate to name it from what it has stored.
Text in, a traceable answer out, on material the mechanism did not see.

*** THE TASK FAVOURS THE FLOORS BY CONSTRUCTION, AND THAT IS STATED UP FRONT RATHER THAN
DISCOVERED LATER. *** Naming a word from its neighbours is close to a cloze task, and raw
co-occurrence counting is a strong baseline on cloze BY DESIGN. So a loss here is informative
about the substrate's REPRESENTATION -- it says the store is a worse co-occurrence record than a
counter -- and it is NOT proof the substrate cannot do its stated job of building an auditable
knowledge store. A separate cell has to test grounding against an independent gold. Do not let
this cell's verdict be quoted as the broader one.

FOUR ARMS, TWO OF THEM THE SUBSTRATE'S OWN ROUTES:
  EPISODIC   hippocampal DG code overlap after CA3 settling
  SEMANTIC   cosine to the lemma's accumulated context profile
  COOC       raw co-occurrence counting over the read split           <- FLOOR, run STANDALONE
  FREQ       the most frequent lemma; never looks at the cue          <- FLOOR, run STANDALONE
  ORTH       char-trigram overlap between cue and candidate           <- FLOOR, run STANDALONE
  SCRAMBLE   EPISODIC on a word-shuffled cue                          <- if this ties EPISODIC,
                                                                         the pipeline is not reading

PLUS FOUR ABLATIONS, one organ each, rate-matched: episodic / definitions / gap_detector /
foraging. An assembled substrate nobody can switch pieces off in cannot be told apart from an
expensive Counter, and no cell in this archive has ever run this arm.

ITEM PRIORITY -- THE FIRST QUESTION, AND IT IS FREE. *** DID THE TEST ITEMS EXIST BEFORE THE
MECHANISM DID? *** YES. The items are sentences of published prose written long before this
project; the gold is the word that is actually in the sentence. No detector of ours authored,
selected or labelled them. Item selection is a SEEDED RANDOM content lemma per sentence, not the
first one -- the smoke run selected the first known lemma, which skews frequent and INFLATED both
floors, and that bias is removed here rather than carried.

PRE-COMMITTED READINGS, written before any number from this cell exists:
  (a) a substrate route beats the strongest floor's UPPER bound, CI-separated, AND at least one
      ablation degrades it -> the assembly does work; name the organ.
  (b) a substrate route beats the floor but NO ablation moves anything -> the floor is what is
      scoring and the organs are decoration. Report it that way; do not soften it.
  (c) no substrate route beats the strongest floor -> a real negative, PROVIDED the instrument is
      alive. The exact-key arm is what establishes that: if EPISODIC cannot retrieve an episode
      it stored verbatim, the cell is broken and reports nothing.
  (d) SCRAMBLE ties the real cue -> the pipeline is not reading, and every other number in the
      cell is void.

Run:  python experiments/exp_substrate_end_to_end_readout_v1.py --mode smoke
      python experiments/exp_substrate_end_to_end_readout_v1.py --mode full
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
from hdlab.reading_grounding_loop import content_lemmas, context_vector_masked
from hdlab.substrate import CONTEXT_DIM, Substrate

CELL = "exp_substrate_end_to_end_readout_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", CELL)

CORPUS = "simplewiki"          # definition-rich, and NOT what the substrate self-test reads
SEEDS = (20260819, 7, 101)
N_BOOT = 2000
N_PERM = 2000
TOP_K = 5


# ---------------------------------------------------------------------------------------------
# SCORING ROUTES. Every one takes the SAME cue, the SAME candidate pool and the SAME gold.
# ---------------------------------------------------------------------------------------------

def _char_trigrams(w: str) -> set:
    w = f"  {w}  "
    return {w[i:i + 3] for i in range(len(w) - 2)}


class Routes:
    """Builds every arm's ranker off ONE read pass, so nothing differs but the route."""

    def __init__(self, sub: Substrate, read_split: Sequence[str]) -> None:
        self.sub = sub
        self.seen = {lem for lem, _ in sub._episode_index}
        if not self.seen:                       # the episodic ablation empties this
            self.seen = set(sub.profile())
        prof = {k: v for k, v in sub.profile().items() if k in self.seen}
        self.names = sorted(prof)
        if self.names:
            P = np.stack([prof[k] for k in self.names]).astype(np.float64)
            self.Pn = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
        else:
            self.Pn = np.zeros((0, CONTEXT_DIM))
        self.freq: collections.Counter = collections.Counter()
        self.cooc: Dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for sent in read_split:
            lems = [l for l in content_lemmas(sent) if l in self.seen]
            for l in lems:
                self.freq[l] += 1
            for a in lems:
                for b in lems:
                    if a != b:
                        self.cooc[b][a] += 1
        self.freq_rank = [w for w, _ in self.freq.most_common()]
        self.tri = {n: _char_trigrams(n) for n in self.names}

    # -- substrate routes --
    def episodic(self, sent: str, tgt: str) -> List[str]:
        return [r[0] for r in self.sub.recall_sentence(sent, target=tgt, top_k=TOP_K)]

    def semantic(self, sent: str, tgt: str) -> List[str]:
        if not self.names:
            return []
        v = context_vector_masked(sent, tgt, d=CONTEXT_DIM)
        if v is None or not np.any(v):
            return []
        v = np.asarray(v, dtype=np.float64)
        sims = self.Pn @ (v / (np.linalg.norm(v) + 1e-12))
        return [self.names[i] for i in np.argsort(-sims)[:TOP_K]]

    # -- floors, each computable from exactly what the substrate had --
    def cooc_floor(self, sent: str, tgt: str) -> List[str]:
        c: collections.Counter = collections.Counter()
        for l in content_lemmas(sent):
            if l == tgt or l not in self.seen:
                continue
            c.update(self.cooc.get(l, {}))
        return [w for w, _ in c.most_common(TOP_K)]

    def freq_floor(self, sent: str, tgt: str) -> List[str]:
        return self.freq_rank[:TOP_K]

    def orth_floor(self, sent: str, tgt: str) -> List[str]:
        cue = set()
        for l in content_lemmas(sent):
            if l != tgt:
                cue |= _char_trigrams(l)
        if not cue:
            return []
        scored = sorted(self.names, key=lambda n: -len(self.tri[n] & cue))
        return scored[:TOP_K]


# ---------------------------------------------------------------------------------------------

def _pick_target(sent: str, seen: set, rng: random.Random) -> Optional[str]:
    """A SEEDED RANDOM known content lemma -- never the first.

    The smoke run took the first known lemma of each sentence, which skews toward frequent words
    and inflated both floors. That bias is removed here rather than carried into the verdict.
    """
    cands = [l for l in content_lemmas(sent) if l in seen]
    return rng.choice(cands) if cands else None


def _donor_cue(cues: Sequence[str], i: int, rng: random.Random) -> str:
    """The scramble control: swap in an UNRELATED sentence, keeping the target.

    *** THE OBVIOUS VERSION OF THIS CONTROL IS INCAPABLE OF FAILING AND WAS CAUGHT DOING SO. ***
    Shuffling the cue's word ORDER tied the real cue EXACTLY -- hit@1 0.7 vs 0.7, permutation
    p = 1.0 -- because `context_vector_masked` builds a BAG of content words, so a shuffled
    sentence is the SAME VECTOR. That is not a weak control, it is a no-op wearing a control's
    name, and pre-committed reading (d) fired on it as designed.

    The control that BINDS destroys the cue's CONTENT rather than its order, which is the recipe
    `reading_grounding_loop`'s own `scramble_context_source` uses: the target's context window
    becomes an unrelated sentence, so coherence dies while gross corpus statistics survive.
    """
    if len(cues) < 2:
        return cues[0]
    j = i
    while j == i:
        j = rng.randrange(len(cues))
    return cues[j]


def _hit(ranked: Sequence[str], tgt: str, k: int) -> int:
    return int(tgt in list(ranked)[:k])


def _boot_ci(x: np.ndarray, rng: np.random.Generator, n: int = N_BOOT) -> Tuple[float, float, float]:
    if x.size == 0:
        return (float("nan"),) * 3
    idx = rng.integers(0, x.size, size=(n, x.size))
    means = x[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi), float((hi - lo) / 2.0)


def _paired_perm_p(a: np.ndarray, b: np.ndarray, rng: np.random.Generator,
                   n: int = N_PERM) -> float:
    """Two-sided paired permutation on the per-item difference. The null is 'the ROUTE LABEL
    carries no information', built by flipping which arm each item is credited to."""
    d = a - b
    obs = abs(d.mean())
    flips = rng.integers(0, 2, size=(n, d.size)) * 2 - 1
    null = np.abs((flips * d).mean(axis=1))
    return float((np.sum(null >= obs) + 1) / (n + 1))


def _run_one(seed: int, n_read: int, n_items: int, ablate: Sequence[str],
             batch: int, corpus: str) -> dict:
    rng = random.Random(seed)
    nprng = np.random.default_rng(seed)

    reg = CorpusRegistry()
    if corpus not in reg.handles:
        raise SystemExit(f"corpus {corpus!r} not on the shelf: {reg.readable_names()[:8]}")
    pool_sents = reg.handles[corpus].take(n_read + 4 * n_items)
    read_split = pool_sents[:n_read]
    held_out = pool_sents[n_read:]
    if len(held_out) < n_items:
        raise SystemExit(f"corpus too small: {len(held_out)} held-out sentences")

    sub = Substrate(seed=seed, ablate=list(ablate))
    t0 = time.time()
    rr = sub.read(corpus=corpus, n_sentences=n_read, batch=batch, max_patches=1)
    read_s = time.time() - t0

    routes = Routes(sub, read_split)
    seen = routes.seen
    arms = {"EPISODIC": routes.episodic, "SEMANTIC": routes.semantic,
            "COOC_floor": routes.cooc_floor, "FREQ_floor": routes.freq_floor,
            "ORTH_floor": routes.orth_floor}

    per_item: Dict[str, Dict[str, List[int]]] = {
        reg_name: {a: [] for a in list(arms) + ["SCRAMBLE"]}
        for reg_name in ("HELD_OUT", "SEEN_exact_key")}
    n_by_regime: Dict[str, int] = {}
    targets_used: List[str] = []

    for regime, cues in (("HELD_OUT", held_out), ("SEEN_exact_key", read_split)):
        n = 0
        for i, sent in enumerate(cues):
            tgt = _pick_target(sent, seen, rng)
            if tgt is None:
                continue
            for name, fn in arms.items():
                r = fn(sent, tgt)
                per_item[regime][name].append(_hit(r, tgt, 1))
            sc = routes.episodic(_donor_cue(cues, i, rng), tgt)
            per_item[regime]["SCRAMBLE"].append(_hit(sc, tgt, 1))
            if regime == "HELD_OUT":
                targets_used.append(tgt)
            n += 1
            if n >= n_items:
                break
        n_by_regime[regime] = n

    out: dict = {"seed": seed, "ablate": list(ablate), "n_read": rr.n_sentences,
                 "read_seconds": round(read_s, 1), "pool_size": len(seen),
                 "n_episodes": len(sub._episode_index),
                 "n_provenance": len(sub.state.provenance),
                 "n_refused": len(sub.state.refusals),
                 "n_by_regime": n_by_regime,
                 "chance_at_1": (1.0 / len(seen)) if seen else None,
                 "distinct_targets": len(set(targets_used)),
                 "target_freq_mean": float(np.mean([routes.freq[t] for t in targets_used]))
                 if targets_used else None}

    for regime in per_item:
        vecs = {k: np.asarray(v, dtype=np.float64) for k, v in per_item[regime].items()}
        block: dict = {}
        for name, x in vecs.items():
            lo, hi, hw = _boot_ci(x, nprng)
            block[name] = {"hit@1": float(x.mean()) if x.size else None,
                           "ci_lo": lo, "ci_hi": hi, "ci_half_width": hw, "n": int(x.size)}
        # THE STRONGEST FLOOR ACTUALLY RUN, and the bar is its UPPER bound -- a floor is an
        # ESTIMATE and carries its own error bar (STATUS discipline 18).
        floors = {k: v for k, v in block.items() if k.endswith("_floor")}
        strongest = max(floors, key=lambda k: floors[k]["hit@1"] or 0.0)
        bar = floors[strongest]["ci_hi"]
        block["_strongest_floor"] = strongest
        block["_credible_bar"] = bar
        for name in ("EPISODIC", "SEMANTIC"):
            m = (block[name]["hit@1"] or 0.0) - (floors[strongest]["hit@1"] or 0.0)
            block[name]["margin_vs_strongest_floor"] = m
            block[name]["clears_credible_bar"] = bool((block[name]["hit@1"] or 0.0) > bar)
            block[name]["perm_p_vs_floor"] = _paired_perm_p(
                vecs[name], vecs[strongest], nprng)
        block["SCRAMBLE"]["perm_p_vs_EPISODIC"] = _paired_perm_p(
            vecs["EPISODIC"], vecs["SCRAMBLE"], nprng)
        out[regime] = block
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    ap.add_argument("--corpus", default=CORPUS)
    a = ap.parse_args()
    smoke = a.mode == "smoke"
    n_read = 400 if smoke else 4000
    n_items = 60 if smoke else 300
    batch = 25 if smoke else 50
    seeds = SEEDS[:1] if smoke else SEEDS
    ablations: List[Tuple[str, ...]] = [()] if smoke else [
        (), ("episodic",), ("definitions",), ("gap_detector",), ("foraging",)]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    t0 = time.time()
    for seed in seeds:
        for ab in ablations:
            key = unit_key(a.mode, a.corpus, seed, "+".join(ab) or "NONE")
            if key in done:
                print(f"[skip] {key}", flush=True)
                continue
            print(f"[run ] {key}", flush=True)
            res = _run_one(seed, n_read, n_items, ab, batch, a.corpus)
            res["unit_key"] = key
            if smoke:
                print(json.dumps(res, indent=2, default=str))
            else:
                record_unit(OUTPUT_DIR, key, res)

    if smoke:
        print("SMOKE OK")
        return 0

    units = load_units(OUTPUT_DIR)
    metrics = {
        "cell": CELL,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full",
        "corpus": a.corpus,
        "n_units": len(units),
        "items_predate_mechanism": True,
        "items_predate_note": (
            "Items are sentences of published prose that predate this project entirely; the gold "
            "is the word actually present in the sentence. No detector of ours authored, selected "
            "or labelled them. Target is a SEEDED RANDOM known content lemma, not the first."),
        "task_favours_floors_by_construction": True,
        "task_caveat": (
            "Naming a word from its neighbours is close to cloze, where co-occurrence counting is "
            "a strong baseline BY DESIGN. A loss says the store is a worse co-occurrence record "
            "than a counter. It is NOT proof the substrate cannot build an auditable knowledge "
            "store; that needs a separate cell with an independent gold."),
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
