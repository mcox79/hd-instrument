"""PHASE 2: A WIRING DIAGNOSTIC ON THE ASSEMBLED SUBSTRATE. DEMOTED FROM A REPORT CARD 2026-08-19.

*** READ THIS BEFORE QUOTING ANY NUMBER FROM THIS CELL. ***

THE SCORE IS RETIRED. THE CONTRASTS ARE NOT. The best achievable score on this task is 0.0300 --
exact co-occurrence, cosine-ranked, which this run now carries as an explicit arm -- against the
substrate's 0.0150. So fixing every defect ever found in this cell wins a TIE WITH A FLOOR. The
headline hit@1 is therefore NOT a capability claim and must not be reported as one. What survives
re-running is the ABLATION TABLE: a within-cell paired difference does not need the task to have
headroom against an external floor, it only needs each organ to be ABLE to move the number.

WHY IT IS BEING RE-RUN AT ALL, AND THE ANSWER IS NOT "TO RESTORE THE TABLE". The first full run
(2026-08-19T03:25:48Z) recorded **n_provenance 0 on all 30 units, no exceptions**. Consolidation
fired only when the forager CHANGED CORPUS, and this cell reads one patch, so nothing was ever
promoted to a grounded fact. The `definitions` and `gap_detector` ablations returned BIT-IDENTICAL
episode counts to the control -- 8,394 in every single unit -- because those organs feed the
grounding path and the grounding path never ran. "Changes exactly nothing" was the bug restated,
not a measurement of two organs, and two slots the substrate calls FILLED were resting on it.

*** THE ONE PRE-REGISTERED QUESTION, WRITTEN BEFORE THE RE-RUN. ***
  WITH CONSOLIDATION ACTUALLY FIRING, DOES THE READ-OUT CHANGE AT ALL?
Both answers are informative, which is why it is worth the compute:
  (i)  IT DOES NOT -> the read-out never consults grounded facts. That is a WIRING DEFECT and it
       must be known BEFORE anything is built on top of the grounding path, because a channel
       that improves grounding would be INVISIBLE to any end-to-end read-out score. This outcome
       is a finding about the assembly, not a null.
  (ii) IT DOES -> the ablation table becomes interpretable for the first time, and the
       definitions / gap_detector nulls can finally be read as facts about those organs.
The contrast that decides it is the new `consolidation` ablation (B3 off) against the control,
same seed, same corpus, same text. Its binding is proven BOTH WAYS by a substrate self-test:
on -> 30 provenance rows and 91 refusals; off -> 0 and 0. An ablation asserted only by "the
ablated arm grounds nothing" would have PASSED on the broken run, because nothing grounded in
either arm.

WHY THIS CELL EXISTS AT ALL. `hdlab/substrate.py` wires nine organs into one reader. Every one of
them was validated ALONE, and wiring components that each look fine is exactly how this project
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
  COOCCOS    the SAME counts, COSINE-ranked instead of argmax-counted <- FLOOR, a CANDIDATE for
                                                                         strongest. NOT ASSUMED
                                                                         TO BE STRONGEST: see the
                                                                         note directly below.
  FREQ       the most frequent lemma; never looks at the cue          <- FLOOR, run STANDALONE
  ORTH       char-trigram overlap between cue and candidate           <- FLOOR, run STANDALONE
  SCRAMBLE   EPISODIC on a DONOR sentence, target kept                <- if this ties EPISODIC,
                                                                         the pipeline is not reading

PLUS FIVE ABLATIONS, one organ each, rate-matched: episodic / definitions / gap_detector /
foraging / consolidation. An assembled substrate nobody can switch pieces off in cannot be told
apart from an expensive Counter, and no cell in this archive has ever run this arm.

*** COOC_COS_floor IS CARRIED AS A CANDIDATE, NOT DECLARED THE STRONGEST, AND THAT WORDING IS A
CORRECTION I MADE TO MY OWN TEXT BEFORE THIS RAN. *** The 0.0300-vs-0.0125 figure that motivated
adding it was measured on a DIFFERENT setup, and discipline 2 says a floor's strength is a
property of the scorer and population, never a number you carry across. Checked on this cell's own
smoke (`scratch/check_cooccos_is_not_a_noop.py`): cosine-ranking is genuinely a DIFFERENT
computation from count-ranking -- not a no-op, which is the failure the scramble control already
had here -- but at smoke scale it is WEAKER, 0.0 vs 0.0167 held-out and 0.15 vs 0.30 at exact key.
So `_strongest_floor` is COMPUTED per regime by taking the max over the floors actually run, and
whichever wins is reported. The cell does not assert in advance which that is.

THE FORAGING TWIN IS RATE-MATCHED ON SENTENCES ACTUALLY READ, AND THE PREVIOUS TWO ATTEMPTS BOTH
FAILED IN OPPOSITE DIRECTIONS. In the first full run the twin read 4,000 sentences against the
live arm's 1,150 -- 3.5x more text -- so the arm measured "how much did you read", not "did you
choose well". The live control now runs FIRST and the twin is handed the sentence count the live
arm ACTUALLY consumed, via `Substrate.read(match_sentences=...)`. `ReadResult.rate_matched` is
recorded per unit, so an unmatched comparison can never again look matched in the metrics.

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

PRE-COMMITTED READINGS FOR THE RE-RUN'S OWN QUESTION, added 2026-08-19 BEFORE it was run:
  (e) the `consolidation` ablation moves NO substrate route, at any seed, in either regime, while
      the control's n_provenance is > 0 -> outcome (i) above. THE READ-OUT DOES NOT CONSULT
      GROUNDED FACTS. Report it as a wiring defect in the assembly and do NOT build a new channel
      on the grounding path until it is fixed, because that channel could not be measured here.
  (f) the `consolidation` ablation moves a substrate route -> outcome (ii). The table is
      interpretable; the definitions / gap_detector nulls may now be read as facts about those
      organs, and only now.
  (g) the control's n_provenance is 0 -> THE FIX DID NOT TAKE AND NOTHING ELSE IN THIS RUN IS
      INTERPRETABLE. This reading exists because the previous run's n_provenance 0 was read past;
      it is checked FIRST, before any arm is looked at.

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
SR_GAMMAS = (0.1, 0.5, 0.9)    # SWEPT, never adopted -- gamma is a parameter, not a computation
# Consolidation cadence, in sentences. MEASURED, not picked (scratch/probe_consolidation_binds.py):
# at 400 sentences and this cadence a single-patch read records 3 passes, 30 provenance rows and
# 91 refusals, where the corpus-change trigger recorded 0 at every volume tried.
CONSOLIDATE_EVERY = 200

# BUMP THIS WHENEVER THE ARM SET OR A SCORER CHANGES. It is part of every unit_key, so a resumed
# run cannot silently serve results computed under a DIFFERENT specification -- which is what
# would have happened here: v1 units were already checkpointed on disk, and adding the SR arms
# without a bump would have let `completed_units` skip every one of them.
# v1 -> v2: added the D7 successor-representation arms; excluded the cue's own words from BOTH
#           the SR and COOC rankings (M's identity term put cue words top by construction and
#           made SR read exactly 0.000 everywhere).
# v2 -> v3: PERIODIC CONSOLIDATION now fires (v2 units all recorded n_provenance 0); added the
#           `consolidation` ablation, which is the re-run's whole question; added the
#           COOC_COS_floor arm, the strongest floor available and previously absent; and
#           rate-matched the foraging twin on sentences ACTUALLY READ rather than on the budget.
#           THE BUMP IS LOAD-BEARING: 30 v2 units are checkpointed on disk and every one of them
#           was computed with a dead grounding path, so a resumed run must not serve them.
SPEC_VERSION = "v3_consolidation"


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

        # THE STRONGEST FLOOR, AND IT WAS MISSING FROM EVERY EARLIER VERDICT IN THIS CELL.
        # The SAME counts as COOC_floor, ranked by COSINE instead of by summed count. Measured
        # separately at 0.0300 against COOC_floor's 0.0125, which makes every prior "beats the
        # strongest floor" statement here void -- the strongest floor was never run. Cosine
        # divides out candidate frequency, which is exactly what the argmax-of-counts version
        # cannot do, and it is computable from precisely what the substrate had.
        self.idx = {n: i for i, n in enumerate(self.names)}
        if self.names:
            C = np.zeros((len(self.names), len(self.names)), dtype=np.float32)
            for w, row in self.cooc.items():
                i = self.idx.get(w)
                if i is None:
                    continue
                for o, c in row.items():
                    j = self.idx.get(o)
                    if j is not None:
                        C[i, j] = c
            self.C = C
            self.Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
        else:
            self.C = np.zeros((0, 0), dtype=np.float32)
            self.Cn = self.C

        # D7 SUCCESSOR REPRESENTATION, swept over gamma and never adopted at one value. M is a
        # DISCOUNTED MULTI-STEP co-occurrence statistic and COOC_floor is the 1-STEP one, so the
        # sweep IS the test: if SR only wins at small gamma it is the 1-step counter wearing a
        # matrix (M = I + gamma*P + gamma^2*P^2 + ..., so gamma -> 0 leaves the 1-step term).
        self.sr: Dict[float, object] = {}
        if self.names:
            seqs = [[l for l in content_lemmas(s) if l in self.seen] for s in read_split]
            seqs = [s for s in seqs if len(s) > 1]
            if seqs:
                from hdlab.successor_representation import SuccessorRepresentation
                for g in SR_GAMMAS:
                    try:
                        self.sr[g] = SuccessorRepresentation.from_sequences(
                            seqs, gamma=g, window=1, vocab=self.names)
                    except (ValueError, np.linalg.LinAlgError):
                        self.sr[g] = None

    def sr_rank(self, sent: str, tgt: str, gamma: float) -> List[str]:
        m = self.sr.get(gamma)
        if m is None:
            return []
        cue = [l for l in content_lemmas(sent) if l != tgt and l in self.seen]
        if not cue:
            return []
        # THE CUE'S OWN WORDS ARE EXCLUDED, AND NOT AS A FAVOUR. M = I + gamma*P + ..., so the
        # IDENTITY TERM puts every cue word at the top of its own ranking by construction. With
        # them left in, SR scored exactly 0.000 in every cell of the smoke -- a dead arm produced
        # by an artifact of the equation, not by the mechanism failing. The target is masked out
        # of the cue, so it can never be among the excluded.
        # COOC_floor gets the IDENTICAL treatment below, so the two arms still differ in ROUTE
        # and in nothing else.
        return m.rank_from_cue(cue, top_k=TOP_K, exclude=cue)

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
        cue = [l for l in content_lemmas(sent) if l != tgt and l in self.seen]
        for l in cue:
            c.update(self.cooc.get(l, {}))
        # SAME EXCLUSION AS THE SR ARM. Applied here too because the arms must differ in ROUTE and
        # nothing else -- giving one arm a cleaner candidate list than its floor would be exactly
        # the kind of unmatched comparison this cell exists to avoid.
        for w in cue:
            c.pop(w, None)
        return [w for w, _ in c.most_common(TOP_K)]

    def cooc_cos_floor(self, sent: str, tgt: str) -> List[str]:
        """The same counts as COOC_floor, cosine-ranked. THE STRONGEST FLOOR ACTUALLY AVAILABLE.

        Identical cue, identical exclusion, identical candidate pool -- the arms differ in the
        RANKING RULE and in nothing else, which is the only way the comparison means anything.
        """
        if not self.names:
            return []
        cue = [l for l in content_lemmas(sent) if l != tgt and l in self.seen]
        rows = [self.idx[l] for l in cue if l in self.idx]
        if not rows:
            return []
        v = self.C[rows].sum(axis=0)
        nv = float(np.linalg.norm(v))
        if nv <= 0.0:
            return []
        sims = self.Cn @ (v / nv)
        excl = {self.idx[l] for l in cue if l in self.idx}
        order = np.argsort(-sims)
        return [self.names[i] for i in order if i not in excl][:TOP_K]

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
             batch: int, corpus: str, match_sentences: Optional[int] = None) -> dict:
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
    # CONSOLIDATE ON A SCHEDULE. The v2 run left this at whatever the corpus change dictated and
    # every one of its 30 units recorded n_provenance 0. `consolidate_every` is passed EXPLICITLY
    # so this cell's grounding behaviour is visible here rather than inherited from a default.
    rr = sub.read(corpus=corpus, n_sentences=n_read, batch=batch, max_patches=1,
                  consolidate_every=CONSOLIDATE_EVERY, match_sentences=match_sentences)
    read_s = time.time() - t0

    routes = Routes(sub, read_split)
    seen = routes.seen
    arms = {"EPISODIC": routes.episodic, "SEMANTIC": routes.semantic,
            "COOC_floor": routes.cooc_floor, "COOC_COS_floor": routes.cooc_cos_floor,
            "FREQ_floor": routes.freq_floor, "ORTH_floor": routes.orth_floor}
    for _g in SR_GAMMAS:
        arms[f"SR_g{_g}"] = (lambda s, t, g=_g: routes.sr_rank(s, t, g))

    per_item: Dict[str, Dict[str, List[int]]] = {
        reg_name: {a: [] for a in list(arms) + ["SCRAMBLE"]}
        for reg_name in ("HELD_OUT", "SEEN_exact_key")}
    arms = dict(arms)          # bind after SR construction so the sweep is present in both blocks
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
                 "rate_matched": bool(rr.rate_matched),
                 "match_sentences_given": match_sentences,
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
        for name in ["EPISODIC", "SEMANTIC"] + [f"SR_g{g}" for g in SR_GAMMAS]:
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
    # THE CONTROL IS FIRST AND THAT ORDER IS LOAD-BEARING, not cosmetic: the foraging twin can
    # only be rate-matched once the live arm has reported how many sentences it ACTUALLY read.
    # The smoke carries the consolidation contrast so the smoke can FAIL on the question the run
    # exists to answer, rather than merely proving the plumbing executes.
    ablations: List[Tuple[str, ...]] = [(), ("consolidation",)] if smoke else [
        (), ("episodic",), ("definitions",), ("gap_detector",), ("consolidation",),
        ("foraging",)]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    done = completed_units(OUTPUT_DIR) if not smoke else set()
    prior = load_units(OUTPUT_DIR) if not smoke else {}
    t0 = time.time()
    for seed in seeds:
        live_n: Optional[int] = None       # sentences the LIVE arm consumed, for the frozen twin
        for ab in ablations:
            key = unit_key(SPEC_VERSION, a.mode, a.corpus, seed, "+".join(ab) or "NONE")
            if key in done:
                print(f"[skip] {key}", flush=True)
                if not ab:
                    rec = prior.get(key) if isinstance(prior, dict) else None
                    live_n = (rec or {}).get("n_read")
                continue
            # An unmatched foraging twin has been read as a result twice in this project, in
            # OPPOSITE directions. Refuse to run it blind rather than record another void arm.
            if "foraging" in ab and live_n is None:
                print(f"[SKIP-UNMATCHED] {key}: the live arm's sentence count is unknown, so "
                      "the frozen twin cannot be rate-matched. Run the control unit for this "
                      "seed first.", flush=True)
                continue
            print(f"[run ] {key}", flush=True)
            res = _run_one(seed, n_read, n_items, ab, batch, a.corpus,
                           match_sentences=live_n if "foraging" in ab else None)
            res["unit_key"] = key
            if not ab:
                live_n = res["n_read"]
            if smoke:
                print(json.dumps(res, indent=2, default=str))
            else:
                record_unit(OUTPUT_DIR, key, res)

    if smoke:
        print("SMOKE OK")
        return 0

    units = load_units(OUTPUT_DIR)
    all_rows = list(units.values()) if isinstance(units, dict) else list(units)
    # SPEC ISOLATION AT ASSEMBLY, NOT ONLY AT SKIP. `completed_units` keys off SPEC_VERSION so a
    # resumed run recomputes v3, but `load_units` returns EVERY unit ever written to this
    # directory -- including the 30 v2 units whose grounding path was dead. Folding those into
    # metrics.json would drag n_provenance 0 controls into the gate below and fire reading (g)
    # on a run that worked. The bump protects the COMPUTE; this line protects the REPORT.
    rows = [u for u in all_rows
            if str(u.get("unit_key", "")).startswith(SPEC_VERSION + "|")]
    n_foreign = len(all_rows) - len(rows)
    ctrl = [u for u in rows if not u.get("ablate")]
    # READING (g), CHECKED IN CODE AND FIRST. The previous run's n_provenance 0 was printed and
    # read past; a pre-committed reading that depends on a human noticing a field is not a gate.
    ctrl_prov = [int(u.get("n_provenance") or 0) for u in ctrl]
    grounding_fired = bool(ctrl_prov) and all(p > 0 for p in ctrl_prov)
    unmatched = [u.get("unit_key") for u in rows if u.get("rate_matched") is False]
    metrics = {
        "cell": CELL,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_mode": "full",
        "corpus": a.corpus,
        "n_units": len(rows),
        "spec_version": SPEC_VERSION,
        "units_from_older_specs_excluded": n_foreign,
        "spec_isolation_note": (
            "metrics.json carries ONLY units whose unit_key matches this SPEC_VERSION. The "
            "excluded count is reported rather than silently dropped: those units are real runs "
            "of a DIFFERENT specification, not noise."),
        "role": "WIRING DIAGNOSTIC, NOT A REPORT CARD",
        "headline_score_is_retired": True,
        "headline_retired_reason": (
            "The best achievable score on this task is 0.0300 (COOC_COS_floor, carried as an arm "
            "here) against the substrate's 0.0150, so fixing every defect wins a tie with a "
            "floor. The hit@1 is NOT a capability claim. What is being measured is the ABLATION "
            "CONTRASTS, which are within-cell paired differences and do not need the task to "
            "have headroom."),
        "prereg_question": (
            "With consolidation actually firing, does the read-out change at all? The deciding "
            "contrast is ablate=['consolidation'] against the control at the same seed."),
        "grounding_fired_in_control": grounding_fired,
        "control_n_provenance": ctrl_prov,
        "grounding_gate_note": (
            "READING (g): if this is False the fix did not take and NOTHING ELSE in this run is "
            "interpretable. Every unit of the v2 run recorded 0 here."),
        "unmatched_units": unmatched,
        "unmatched_note": (
            "Units whose foraging twin was NOT rate-matched on sentences actually read. Must be "
            "empty; a non-empty list voids the foraging arm and nothing else."),
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
        "units": rows,
    }
    path = os.path.join(OUTPUT_DIR, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, path)
    print(f"[done] {len(rows)} units ({n_foreign} older-spec units excluded) "
          f"in {time.time() - t0:.0f}s -> {path}")
    print(f"[gate] grounding_fired_in_control={grounding_fired} "
          f"control_n_provenance={ctrl_prov}", flush=True)
    if not grounding_fired:
        print("[gate] READING (g) FIRED: the control grounded nothing. Nothing else in this run "
              "is interpretable.", flush=True)
    if unmatched:
        print(f"[gate] UNMATCHED foraging units: {unmatched}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
