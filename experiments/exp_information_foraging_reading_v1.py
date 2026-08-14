"""experiments/exp_information_foraging_reading_v1.py -- CAN THE SUBSTRATE CHOOSE WHAT TO READ?
2026-08-14. Pre-reg: preregs/2026-08-14_information_foraging_reading_v1.md

THE QUESTION. Until today the reading loop could address 4 corpora out of the 36 on disk, and the
consequence is measured: 63.9% of every definitional term it has ever banked came from one biology
segment (tools/segment_skew_report.py, run against definitional_facts_v5.jsonl). This cell gives
it the whole shelf (hdlab.corpus_registry) plus a patch-leaving rule (hdlab.information_foraging)
and asks whether choosing for itself beats (1) choosing at random over the SAME shelf and (2) the
frozen 4-entry schedule that produced the skew.

FOUR ARMS, identical in every respect except the reading POLICY. Same seed lexicon, same encoder,
same n_dim, same checkpoint cadence, same total sentence budget, same fresh experiment store.

  FORAGE       MVT leave rule  +  gap-ranked corpus choice over 28 readable corpora
  RANDOM       MVT leave rule  +  UNIFORM RANDOM corpus choice over the same 28     [FLOOR 1]
  FROZEN       the historical 4-entry schedule, fixed order, equal budget per source [FLOOR 2]
  FIXED_LEAVE  gap-ranked corpus choice  +  FIXED patch length (isolates the leave rule)

CURRENCY = UNCERTAINTY REDUCTION PER UNIT EFFORT, NOT ITEMS READ. CITED@Constantino & Daw 2015
Exp 2 rejected item-count accounting at exceedance probability .999. The gain of one harvest step
(one sentence) is the SUM OVER THE SENTENCE'S CONTENT LEMMAS OF THE POSTERIOR-MEAN SHIFT the
substrate's OWN concept model undergoes:

    gain(s) = sum_L  || S_L^{new}/(n_L+1)  -  S_L^{old}/n_L ||  /  sqrt(d)

read directly off `ConceptSpace._sums` before and after `process_sentence`. For a first encounter
(n_L = 0) the shift is the whole vector, i.e. 1.0. This quantity is monotone in Bayesian surprise
for a fixed-variance Gaussian-mean model, it decays as ~1/n within a patch (which is the depletion
curve the MVT needs and gets for free from the substrate's own arithmetic), and it is emphatically
not a count: a sentence of already-well-observed words scores ~0 while still being one item.
`assert_gain_is_not_a_count` gates on the realised stream. DECLARED LIMITATION, in the pre-reg and
here: this is BAYESIAN SURPRISE, not Oudeyer LEARNING PROGRESS (the derivative of prediction
error). Surprise cannot by itself distinguish learnable novelty from unlearnable noise, so a
novelty trap is a live risk; `mean_lp` is recorded alongside so the two can be compared post hoc,
and a forager that camps on the highest-novelty corpus and grounds WORSE is a real reportable
negative rather than a bug.

PATCHES ARE NOT DOCUMENTS. CITED@Zacks 2007 / Baldassano 2017 / Kumar 2023. A corpus visit is
segmented by `SurpriseSegmenter` on the substrate's OWN gain signal, and the leave decision is
evaluated AT those event boundaries -- boundaries are decision points. So the hierarchy is
sentence-run patch inside corpus patch, each scored on its own.

REUSE (wire-don't-island; every organ below is imported and called, none reimplemented):
  hdlab.reading_grounding_loop     process_sentence / checkpoint / seed_known_words / ConceptSpace
  hdlab.gap_driven_reader          PrereqTracker / read_and_track / next_read_target / rank_material
                                   (HARD_PASS commit 7dd02833b; its ONLY prior caller fed it four
                                   synthetic f-string templates of pseudowords -- this is the first
                                   time it has ever been pointed at real corpora)
  hdlab.corpus_registry            the shelf
  hdlab.information_foraging       the leave rule
  hdlab.hd_fact_store.HDFactStore  a FRESH experiment store per arm; the canonical foundation is
                                   never opened, never written (growth is paused pending grounding
                                   quality, and this cell does not resume it)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; sha256 over each arm's read-sentence stream)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except)
# - crlb_n/a: no quantitative noise floor applies; discriminator reachability argued from
#   construction (28 sources vs 4 bounds dominant_share from below at 1/28 vs 1/4)
# - baseline_in_band at smoke (META_RULE_AG; FROZEN dominant_share must land in (0.05, 0.99))
# - discriminator survives scale: smoke runs the SAME policies at reduced budget and the smoke
#   gate asserts the mechanism FIRED (>=3 distinct corpora chosen, >=3 patches, travel updates >0)
# - cardinality_ok: EXPECTED_N_UNITS = n_arms; verdict counts len(per_unit)
# - per-unit failure-class instrumentation; no bare except
# - calibration_check: default_ok_for_this_regime (schema_thresh 0.25 = cycle-1's calibrated value)
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

ASCII-only. Deterministic: fixed integer seeds, sorted(set(...)) everywhere, never Python hash().
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    sys.stdout.reconfigure(line_buffering=True)     # SS17 progress_logging
except (AttributeError, ValueError):
    pass

from hdlab.corpus_registry import (CorpusHandle, CorpusRegistry, CorpusSpec, STATUS_READABLE)
from hdlab.gap_driven_reader import (PrereqTracker, next_read_target, rank_material, read_and_track)
from hdlab.hd_fact_store import HDFactStore
from hdlab.information_foraging import (ForagingConfig, ForagingController, SurpriseSegmenter,
                                        assert_gain_is_not_a_count, oracle_mvt_optimum)
from hdlab.reading_grounding_loop import (KNOWN_RELATION, MEANING_RELATION, ReadingLoopState,
                                          checkpoint, content_lemmas, seed_known_words,
                                          segment_skew)
from tools import exp_checkpoint

ANCHOR_NAME = "information_foraging_reading_v1"

# ------------------------------------------------------------------ pre-registered constants
N_DIM = 2048                       # matches cycle-1/2 so the reading pipeline is byte-comparable
SEED_VOCAB_N = 1000                # base_vocabulary top-1000 = the seed lexicon (cycle-1's value)
HELDOUT_PROBE_LO, HELDOUT_PROBE_HI = 1000, 4000   # ranks 1001..4000: HELD OUT of every arm
CHUNK = 150                        # sentences between consolidation checkpoints (cycle-1's value)
SCHEMA_THRESH = 0.25               # MEASURED@exp_reading_grounding_loop_cycle1_v1 SCHEMA_THRESH_FULL
SUBSTRATE_SEED = 20260814

FULL_BUDGET = 10000                # harvest steps (sentences) per arm
SMOKE_BUDGET = 900
FULL_MAX_SENT_PER_CORPUS = 4000
SMOKE_MAX_SENT_PER_CORPUS = 600
FULL_MAX_BYTES = 4_000_000
SMOKE_MAX_BYTES = 700_000
PEEK_N = 120                       # sentences sampled per corpus when RANKING candidate material
PEEK_STRIDE = 7

TRAVEL_TAU = 8.0                   # FREE; swept in the diagnostics arm below (Hayden 2011)
RHO_HALFLIFE = 72.0                # ~1.5 patch+travel cycles at an expected ~40-step patch
RHO_SLOW_HALFLIFE = 360.0
BETA_LEAVE = 4.0
PATCH_FIXED_LEN = 40               # FIXED_LEAVE arm's constant residence (pre-registered)
SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN = 24, 1.0, 6, 120

ARMS = ["FORAGE", "RANDOM", "FROZEN", "FIXED_LEAVE", "FORAGE_REFUSAL"]
# FORAGE_REFUSAL is the dated AMENDMENT arm (prereg sec 12): identical to FORAGE except that the
# blocked concept driving each choice is drawn from the REFUSAL ledger rather than from raw
# pending exposure. The superseded FORAGE rule is retained and still scored, per the amendment
# discipline in notes/ORGAN_MAP.md sec 3 correction 1.
GAP_RANKED_ARMS = {"FORAGE": "pending", "FIXED_LEAVE": "pending", "FORAGE_REFUSAL": "refusal"}
EXPECTED_N_UNITS = len(ARMS)

# The historical frozen schedule, reproduced source-for-source from
# experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137 (SEGMENT_POOL_LOADERS).
FROZEN_SPECS = [
    CorpusSpec("ele_cont", STATUS_READABLE, "txt",
               ["data/corpora/onestop/Texts-SeparatedByReadingLevel/Ele-Txt"], "news"),
    CorpusSpec("int_cont", STATUS_READABLE, "txt",
               ["data/corpora/onestop/Texts-SeparatedByReadingLevel/Int-Txt"], "news"),
    CorpusSpec("adv_new", STATUS_READABLE, "txt",
               ["data/corpora/onestop/Texts-SeparatedByReadingLevel/Adv-Txt"], "news"),
    CorpusSpec("bio_new", STATUS_READABLE, "txt",
               ["data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt"],
               "textbook_biology"),
]


# ============================================================================ small helpers
def repo_path(rel: str) -> str:
    return os.path.join(REPO_ROOT, rel)


def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _write_json_atomic(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)                    # META_RULE_AH


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    _write_json_atomic(os.path.join(output_dir, "_start_marker.json"), {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()})


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    _write_json_atomic(os.path.join(output_dir, "metrics.json"), {
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME})


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def load_base_vocab(lo: int, hi: int) -> List[str]:
    """base_vocabulary_ordered.csv rows [lo, hi). Rank order is the file's own; deterministic."""
    path = repo_path("data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv")
    words: List[str] = []
    with open(path, encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if i >= hi:
                break
            if i >= lo:
                words.append(row["word"])
    return words


def norm_entropy(counts: Dict[str, int]) -> Tuple[float, str, float]:
    tot = sum(counts.values())
    if tot <= 0:
        return 0.0, "", 0.0
    items = sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0])))
    ent = -sum((v / tot) * math.log(v / tot) for _k, v in items if v > 0)
    max_ent = math.log(len(items)) if len(items) > 1 else 1.0
    return (ent / max_ent if max_ent > 0 else 0.0), items[0][0], items[0][1] / tot


# ==================================================== the currency: posterior-mean-shift meter
class UncertaintyMeter:
    """Reads the substrate's OWN model and reports how much one sentence MOVED it.

    TWO LOCI, because the substrate keeps what it knows and what it is still learning in different
    places, and the uncertainty that matters lives mostly in the SECOND:
      (a) `ConceptSpace._sums[lemma]`  -- the running context accumulator for words the substrate
          already KNOWS (seed lexicon) or has GROUNDED. Measuring only this was the first draft's
          bug: a sentence made entirely of not-yet-known words scored exactly 0.0, i.e. the meter
          was blind to precisely the words the loop is trying to learn.
      (b) `Library.items[lemma].traces` -- the accumulating evidence for words still PENDING. Each
          new trace is one more observation of a concept the substrate cannot yet ground, so the
          posterior-mean shift there IS the uncertainty reduction the forager should be chasing.

    Not a count. Not the loop's own objective -- the loop never sees this number, and nothing here
    writes to any substrate structure. Purely an observer."""

    def __init__(self, state) -> None:
        self.state = state
        self.space = state.space
        self.d = state.space.d
        self._seen: Dict[str, np.ndarray] = {}
        self._n: Dict[str, int] = {}
        self._lib_sum: Dict[str, np.ndarray] = {}
        self._lib_n: Dict[str, int] = {}
        self.rebaseline()

    def rebaseline(self) -> None:
        """Re-sync to the current model without scoring the difference. Called after every
        consolidation checkpoint, because `seed_from_bundle` OVERWRITES a newly-grounded lemma's
        accumulator, and because terminal items are released from the Library -- both are
        bookkeeping events, not observations, and neither is uncertainty reduction."""
        for lemma, vec in self.space._sums.items():
            self._seen[lemma] = np.array(vec, copy=True)
            self._n.setdefault(lemma, 1)
        items = getattr(self.state.library, "items", {})
        for lemma in sorted(self._lib_n):
            if lemma not in items:
                self._lib_n.pop(lemma, None)
                self._lib_sum.pop(lemma, None)

    def _shift(self, prev_sum: np.ndarray, n_prev: int, new_vecs: Sequence[np.ndarray]
               ) -> Tuple[float, np.ndarray, int, List[float]]:
        gain, errs = 0.0, []
        rd = math.sqrt(self.d)
        cur, n = prev_sum, n_prev
        for x in new_vecs:
            x = np.asarray(x, dtype=np.float64)
            if n == 0:
                gain += float(np.linalg.norm(x)) / rd
                errs.append(1.0)
                cur = x.astype(np.float64, copy=True)
                n = 1
                continue
            mean_b = cur / n
            nxt = cur + x
            mean_a = nxt / (n + 1)
            gain += float(np.linalg.norm(mean_a - mean_b)) / rd
            nb, nx = float(np.linalg.norm(mean_b)), float(np.linalg.norm(x))
            if nb > 0 and nx > 0:
                errs.append(1.0 - float(np.dot(mean_b, x)) / (nb * nx))
            cur, n = nxt, n + 1
        return gain, cur, n, errs

    def score(self, lemmas: Sequence[str]) -> Tuple[float, float]:
        """(gain, mean_prediction_error) for the observations just absorbed. `gain` is the summed
        posterior-mean shift; `mean_prediction_error` is 1 - cos(prior_mean, new_observation),
        recorded so LEARNING PROGRESS (its derivative) can be compared post hoc."""
        gain, errs = 0.0, []
        rd = math.sqrt(self.d)
        items = getattr(self.state.library, "items", {})
        for lemma in lemmas:
            # (a) known / grounded anchors
            cur = self.space._sums.get(lemma)
            if cur is not None:
                prev = self._seen.get(lemma)
                if prev is None:
                    self._seen[lemma] = np.array(cur, copy=True)
                    self._n[lemma] = 1
                    gain += float(np.linalg.norm(cur)) / rd
                    errs.append(1.0)
                elif not np.array_equal(cur, prev):
                    n = self._n.get(lemma, 1)
                    mean_b, mean_a = prev / n, cur / (n + 1)
                    gain += float(np.linalg.norm(mean_a - mean_b)) / rd
                    x = cur - prev
                    nb, nx = float(np.linalg.norm(mean_b)), float(np.linalg.norm(x))
                    if nb > 0 and nx > 0:
                        errs.append(1.0 - float(np.dot(mean_b, x)) / (nb * nx))
                    self._n[lemma] = n + 1
                    self._seen[lemma] = np.array(cur, copy=True)
            # (b) still-pending items: the words the loop is actually trying to learn
            item = items.get(lemma)
            if item is None:
                continue
            traces = getattr(item, "traces", None)
            if not traces:
                continue
            seen_n = self._lib_n.get(lemma, 0)
            if len(traces) <= seen_n:
                continue
            new_vecs = []
            for t in traces[seen_n:]:
                v = getattr(t, "context_vec", None)
                if v is not None:
                    new_vecs.append(v)
            if not new_vecs:
                self._lib_n[lemma] = len(traces)
                continue
            base = self._lib_sum.get(lemma)
            n_prev = seen_n if base is not None else 0
            base = base if base is not None else np.zeros(self.d, dtype=np.float64)
            g, cur_sum, n_new, e = self._shift(base, n_prev, new_vecs)
            gain += g
            errs.extend(e)
            self._lib_sum[lemma] = cur_sum
            self._lib_n[lemma] = len(traces)
        return gain, (sum(errs) / len(errs) if errs else 0.0)


# ==================================================================== corpus-choice policies
class Shelf:
    """Wraps the registry so all four arms draw sentences through one interface."""

    def __init__(self, run_mode: str, frozen: bool) -> None:
        max_sent = SMOKE_MAX_SENT_PER_CORPUS if run_mode == "smoke" else FULL_MAX_SENT_PER_CORPUS
        max_bytes = SMOKE_MAX_BYTES if run_mode == "smoke" else FULL_MAX_BYTES
        if frozen:
            self.handles = {s.name: CorpusHandle(s, max_sent, max_bytes) for s in FROZEN_SPECS}
            self.domains = {s.name: s.domain for s in FROZEN_SPECS}
            self.registry = None
        else:
            reg = CorpusRegistry(max_sentences_per_corpus=max_sent, max_bytes=max_bytes)
            self.handles = {n: reg.handles[n] for n in reg.readable_names()}
            self.domains = {n: reg.domain_of(n) for n in self.handles}
            self.registry = reg
        self.names = sorted(self.handles)

    def live_names(self) -> List[str]:
        return sorted(n for n in self.names if self.handles[n].remaining() > 0)


def _primary_blocked_lemma(state: ReadingLoopState, source: str) -> Optional[str]:
    """Which blocked concept drives the next choice.

    `pending`  -- the most-attempted still-PENDING Library item. This is the ORIGINAL
                  pre-registered rule. The first smoke showed what it actually selects on real
                  corpora: `page`, `bbm`, `blackberry` -- high-frequency nouns that are barely
                  knowledge gaps at all, because "most traces" is very nearly a frequency ranking.
    `refusal`  -- the most-REFUSED lemma that is still not banked. A refusal means the item
                  reached the consolidation gate and FAILED there, which is a far stronger signal
                  of a genuine blocked concept than raw exposure. This is the AMENDMENT arm
                  (preregs/2026-08-14_information_foraging_reading_v1.md sec 12, filed before the
                  full run; the superseded `pending` rule is retained and still scored).
                  It also finally reads the refusal ledger for a DECISION, which is the specific
                  thing notes/gap_driven_learning_loop_audit_2026-08-13.md sec 5 found nothing on
                  disk ever does: 11,122 rows written, counted, reloaded, and never consulted."""
    if source == "refusal":
        banked = {p["subject"] for p in state.provenance}
        counts: Counter = Counter(r["lemma"] for r in state.refusals
                                  if r.get("lemma") not in banked)
        if counts:
            return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        # no refusals yet (early in a run): fall through to the pending rule
    pending = [(len(it.traces), lem) for lem, it in sorted(state.library.items.items())
               if getattr(it, "status", "") == "PENDING"]
    if not pending:
        return None
    pending.sort(key=lambda t: (-t[0], t[1]))
    return pending[0][1]


def choose_gap_ranked(state: ReadingLoopState, tracker: PrereqTracker, shelf: Shelf,
                      rng: random.Random, exclude: Optional[str], diag: dict,
                      primary_source: str = "pending") -> str:
    """The substrate picks its own next corpus, using organs it already owns:

      1. the most-attempted still-unresolved word in its Library is the PRIMARY blocked concept;
      2. `gap_driven_reader.next_read_target` names the specific missing PREREQUISITE behind it
         (co-occurrence consistency x the live GapDetector signal);
      3. `gap_driven_reader.rank_material` scores every corpus's peek sample by how much material
         it holds on that target.

    When the target appears in no peek at all, every score is 0 and a ranked choice would
    degenerate into "alphabetically first". Classical MVT assumes RANDOM patch encounter, so the
    honest fallback is a random draw -- counted in `n_choice_fallback_random`, because if that
    counter is large then FORAGE is RANDOM by construction and the comparison must say so."""
    live = [n for n in shelf.live_names() if n != exclude] or shelf.live_names()
    if not live:
        return sorted(shelf.names)[0]

    primary = _primary_blocked_lemma(state, primary_source)
    if primary is None:
        diag["n_choice_fallback_random"] += 1
        return rng.choice(live)
    target, cands = next_read_target(state, tracker, primary, use_gap_signal=True)
    diag["targets"].append({"primary": primary, "target": target, "n_candidates": len(cands)})

    docs = {n: shelf.handles[n].peek(PEEK_N, PEEK_STRIDE) for n in live}
    ranked = rank_material(state, target, docs)
    if not ranked or ranked[0][1] <= 0:
        diag["n_choice_fallback_random"] += 1
        return rng.choice(live)
    diag["n_choice_ranked"] += 1
    diag["ranked_top"].append({"target": target, "corpus": ranked[0][0], "score": ranked[0][1]})
    return ranked[0][0]


# ============================================================================== one arm
def run_arm(arm: str, budget: int, run_mode: str, output_dir: str) -> dict:
    t0 = time.time()
    seed_words = load_base_vocab(0, SEED_VOCAB_N)
    store = HDFactStore(n_dim=N_DIM, seed=SUBSTRATE_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source="seed_base_vocabulary")
    tracker = PrereqTracker()
    meter = UncertaintyMeter(state)

    shelf = Shelf(run_mode, frozen=(arm == "FROZEN"))
    rng = random.Random(SUBSTRATE_SEED + ARMS.index(arm))
    cfg = ForagingConfig(travel_step_duration=TRAVEL_TAU, rho_halflife_steps=RHO_HALFLIFE,
                         rho_slow_halflife_steps=RHO_SLOW_HALFLIFE, beta_leave=BETA_LEAVE,
                         stochastic=True, seed=SUBSTRATE_SEED + ARMS.index(arm))
    ctrl = ForagingController(cfg)
    seg = SurpriseSegmenter(SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN)

    diag = {"n_choice_ranked": 0, "n_choice_fallback_random": 0, "targets": [], "ranked_top": []}
    gains: List[float] = []
    errs: List[float] = []
    visits: List[str] = []
    read_by_corpus: Counter = Counter()
    sent_hash = hashlib.sha256()
    patch_gain_seqs: List[List[float]] = []

    frozen_order = [s.name for s in FROZEN_SPECS]
    frozen_quota = budget // len(frozen_order)

    n_read = 0
    pass_idx = 0
    since_ckpt = 0
    current: Optional[str] = None

    while n_read < budget:
        # ---- choose a corpus (this is the whole experiment)
        if arm == "FROZEN":
            idx = min(n_read // frozen_quota, len(frozen_order) - 1)
            nxt = frozen_order[idx]
        elif arm == "RANDOM":
            live = [n for n in shelf.live_names() if n != current] or shelf.live_names()
            nxt = rng.choice(live)
        else:                                     # every gap-ranked arm
            nxt = choose_gap_ranked(state, tracker, shelf, rng, current, diag,
                                    primary_source=GAP_RANKED_ARMS[arm])
        if nxt != current:
            if current is not None:
                ctrl.travel()                      # r = 0, rho STILL updates (failure mode 2)
                patch_gain_seqs.append(list(ctrl.patch_log[-1]["gains"]))
            current = nxt
            ctrl.enter_patch(current)
            visits.append(current)
        handle = shelf.handles[current]

        # ---- harvest this patch
        n_in_patch = 0
        while n_read < budget:
            batch = handle.take(1)
            if not batch:
                break                              # corpus exhausted; treat as a forced leave
            sentence = batch[0]
            sent_hash.update(sentence.encode("utf-8"))
            lemmas = read_and_track(state, tracker, sentence, f"{arm}_{n_read}", pass_idx)
            gain, err = meter.score(lemmas)
            gains.append(gain)
            errs.append(err)
            ctrl.harvest(gain)
            read_by_corpus[current] += 1
            n_read += 1
            n_in_patch += 1
            since_ckpt += 1

            if since_ckpt >= CHUNK:
                row = checkpoint(state, pass_idx, current, schema_thresh=SCHEMA_THRESH)
                meter.rebaseline()
                pass_idx += 1
                since_ckpt = 0
                if pass_idx % 4 == 0:
                    _heartbeat(output_dir, {
                        "ts_iso": datetime.now(timezone.utc).isoformat(), "arm": arm,
                        "unit_idx": n_read, "total_units": budget,
                        "elapsed_s": round(time.time() - t0, 1),
                        "extra": {"grounded": row["cumulative_grounded"], "rho": round(ctrl.rho, 6),
                                  "kappa": round(ctrl.kappa.kappa, 4), "corpus": current,
                                  "n_patches": len(ctrl.patch_log)}})
                    print(f"[{arm}] {n_read}/{budget} corpus={current} grounded="
                          f"{row['cumulative_grounded']} rho={ctrl.rho:.5f} "
                          f"kappa={ctrl.kappa.kappa:.3f} patches={len(ctrl.patch_log)} "
                          f"t={time.time()-t0:.0f}s", flush=True)

            # ---- leave?
            boundary = seg.observe(gain)
            if arm == "FROZEN":
                if n_read >= frozen_quota * (frozen_order.index(current) + 1):
                    break
            elif arm == "FIXED_LEAVE":
                if n_in_patch >= PATCH_FIXED_LEN:
                    break
            elif boundary and ctrl.should_leave():
                break

    if since_ckpt > 0:
        checkpoint(state, pass_idx, current or "final", schema_thresh=SCHEMA_THRESH)
        meter.rebaseline()
    if ctrl.patch_log is not None and ctrl.n_harvests_this_patch:
        ctrl.travel()
        patch_gain_seqs.append(list(ctrl.patch_log[-1]["gains"]))

    final_row = state.growth_curve[-1] if state.growth_curve else {}
    return _score_arm(arm, state, ctrl, shelf, gains, errs, visits, read_by_corpus, diag,
                      patch_gain_seqs, final_row, sent_hash.hexdigest(), n_read,
                      round(time.time() - t0, 2))


# ============================================================================ scoring
def _wordnet_scores(pairs: List[Tuple[str, str]]) -> dict:
    """BLIND, MECHANICAL grounding-quality check. Not hand-scored (the hand-scored MEANINGFUL
    read-out sits at 1-3% and made two cells undecidable this week), and not the substrate's own
    objective: WordNet plays no part in any arm's decision path. Disclosure: the loop's lemmatiser
    (`thematic_role_labeler.lemma_word`) normalises surface forms, but no WordNet SEMANTIC
    relation is consulted anywhere in the reading pipeline.

    A banked (subject, object) pair counts as RELATED when the two share a synset, one is in the
    other's hypernym closure, or their max Wu-Palmer similarity clears 0.5."""
    from nltk.corpus import wordnet as wn
    n_scorable = n_related = 0
    wups: List[float] = []
    for subj, obj in pairs:
        ss, os_ = wn.synsets(subj), wn.synsets(obj)
        if not ss or not os_:
            continue
        n_scorable += 1
        best = 0.0
        related = False
        for a in ss[:6]:
            ac = set(a.closure(lambda x: x.hypernyms()))
            for b in os_[:6]:
                if a == b or b in ac or a in set(b.closure(lambda x: x.hypernyms())):
                    related = True
                try:
                    w = a.wup_similarity(b)
                except Exception:                 # nltk raises on cross-POS pairs; treat as 0
                    w = None
                if w is not None and w > best:
                    best = float(w)
        wups.append(best)
        if related or best >= 0.5:
            n_related += 1
    return {"n_pairs": len(pairs), "n_scorable": n_scorable, "n_related": n_related,
            "wn_agreement": round(n_related / n_scorable, 6) if n_scorable else None,
            "wn_scorable_frac": round(n_scorable / len(pairs), 6) if pairs else None,
            "mean_wup": round(sum(wups) / len(wups), 6) if wups else None}


def _score_arm(arm, state, ctrl, shelf, gains, errs, visits, read_by_corpus, diag,
               patch_gain_seqs, final_row, sent_digest, n_read, elapsed) -> dict:
    banked = [(p["subject"], p["object"], p.get("segment")) for p in state.provenance]
    by_source = Counter(s for _a, _b, s in banked)
    bal, dom, dom_share = norm_entropy(dict(by_source))
    dom_by_domain = Counter(shelf.domains.get(s, "unknown") for _a, _b, s in banked)
    dbal, ddom, ddom_share = norm_entropy(dict(dom_by_domain))

    items = getattr(state.library, "items", {})
    trace_counts = sorted(len(getattr(it, "traces", []) or []) for it in items.values())
    n_at_min_confirm = sum(1 for c in trace_counts if c >= 4)   # MIN_CONFIRM = 4

    heldout = sorted(set(load_base_vocab(HELDOUT_PROBE_LO, HELDOUT_PROBE_HI)))
    banked_subjects = sorted({a for a, _b, _s in banked})
    hits = sorted(set(banked_subjects) & set(heldout))

    orc = oracle_mvt_optimum(patch_gain_seqs, ctrl.cfg.travel_step_duration,
                             ctrl.cfg.harvest_step_duration)
    st = ctrl.state()
    # learning-progress proxy: is prediction error FALLING across the run (Oudeyer), recorded so
    # the surprise-vs-progress question is answerable post hoc rather than assumed away
    half = max(1, len(errs) // 2)
    lp = (sum(errs[:half]) / half) - (sum(errs[half:]) / max(1, len(errs) - half))

    return {
        "arm": arm,
        "n_sentences_read": n_read,
        "elapsed_s": elapsed,
        "read_sentence_digest": sent_digest,
        # --- knowledge outcome
        "n_grounded": len(banked_subjects),
        "n_grounded_per_1k": round(1000.0 * len(banked_subjects) / max(1, n_read), 4),
        "n_refused": len(state.refusals),
        "refusal_reasons": dict(sorted(Counter(r["reason"] for r in state.refusals).items(),
                                       key=lambda kv: (-kv[1], kv[0]))),
        "n_self_grounded_tautology": sum(1 for a, b, _s in banked if a == b),
        "tautology_rate": round(sum(1 for a, b, _s in banked if a == b) / max(1, len(banked)), 6),
        # --- the blind spot
        "source_balance_entropy": round(bal, 6),
        "dominant_source": dom,
        "dominant_source_share": round(dom_share, 6),
        "domain_balance_entropy": round(dbal, 6),
        "dominant_domain": ddom,
        "dominant_domain_share": round(ddom_share, 6),
        "n_distinct_sources_banked": len(by_source),
        "banked_by_source": dict(sorted(by_source.items(), key=lambda kv: (-kv[1], kv[0]))),
        "sentences_read_by_corpus": dict(sorted(read_by_corpus.items(),
                                                key=lambda kv: (-kv[1], kv[0]))),
        "n_distinct_corpora_read": len(read_by_corpus),
        # --- held-out probe (never visible to any arm's decisions)
        "heldout_probe_n": len(heldout),
        "heldout_hits": len(hits),
        "heldout_coverage": round(len(hits) / max(1, len(heldout)), 6),
        "heldout_precision": round(len(hits) / max(1, len(banked_subjects)), 6),
        # EXPOSURE FRAGMENTATION -- the candidate mechanism behind any FORAGE grounding deficit.
        # Grounding needs MIN_CONFIRM=4 coherent encounters of the SAME lemma; a forager that
        # hops sources may never accumulate them. Measured, not assumed.
        "exposure": {
            "n_library_items": len(trace_counts),
            "mean_traces_per_item": round(sum(trace_counts) / max(1, len(trace_counts)), 4),
            "median_traces_per_item": (trace_counts[len(trace_counts) // 2] if trace_counts else 0),
            "max_traces": (trace_counts[-1] if trace_counts else 0),
            "n_items_at_min_confirm": n_at_min_confirm,
            "frac_items_at_min_confirm": round(n_at_min_confirm / max(1, len(trace_counts)), 6),
        },
        # --- blind grounding quality
        "wordnet": _wordnet_scores([(a, b) for a, b, _s in banked]),
        # --- foraging diagnostics
        "foraging": {
            "achieved_gain_rate": round(st["achieved_rate"], 8),
            "total_gain": round(st["total_gain"], 6),
            "total_time": st["total_time"],
            "rho_final": round(st["rho"], 8),
            "rho_fast_final": round(st["rho_fast"], 8),
            "rho_slow_final": round(st["rho_slow"], 8),
            "kappa_final": round(st["kappa"], 6),
            "kappa_n_observed": st["kappa_n_observed"],
            "n_patches": st["n_patches"],
            "mean_patch_residence": round(st["mean_patch_residence"], 4),
            "n_travel_updates": st["n_travel_updates"],
            "n_visits": len(visits),
            "n_distinct_visited": len(sorted(set(visits))),
            "oracle_rate": round(orc["oracle_rate"], 8),
            "oracle_ratio": round(st["achieved_rate"] / orc["oracle_rate"], 6) if orc["oracle_rate"] > 0 else None,
            "gain_distinct_values": len(sorted(set(round(g, 9) for g in gains))),
            "mean_gain": round(sum(gains) / max(1, len(gains)), 8),
            "learning_progress_first_half_minus_second": round(lp, 6),
            "n_choice_ranked": diag["n_choice_ranked"],
            "n_choice_fallback_random": diag["n_choice_fallback_random"],
            "ranked_choice_frac": round(diag["n_choice_ranked"] /
                                        max(1, diag["n_choice_ranked"] + diag["n_choice_fallback_random"]), 6),
            "example_targets": diag["targets"][:15],
            "example_ranked_choices": diag["ranked_top"][:15],
        },
        "final_growth_row_segment_skew": segment_skew(final_row),
    }


# ============================================================================ verdict
def build_verdict(per_arm: Dict[str, dict]) -> dict:
    missing = [a for a in ARMS if a not in per_arm]
    if missing:
        return {"verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "verdict_msg": f"expected {EXPECTED_N_UNITS} arms, missing {missing}"}

    digests = {a: per_arm[a]["read_sentence_digest"] for a in ARMS}
    if len(sorted(set(digests.values()))) != len(ARMS):
        return {"verdict": "HARD_FAIL_META_RULE_AF_ARMS_BIT_IDENTICAL",
                "verdict_msg": f"arms read identical sentence streams: {digests}"}

    F, R, Z, X, FR = (per_arm[a] for a in ARMS)
    checks = {}
    # D1 -- the blind spot, FORAGE vs the frozen schedule. Declared: FORAGE is advantaged here
    # partly BY CONSTRUCTION (28 sources vs 4). That is the point of the shelf, and it is stated.
    d1 = Z["dominant_source_share"] - F["dominant_source_share"]
    checks["D1_dominant_share_drop_vs_FROZEN"] = {"value": round(d1, 6), "pass_band": ">= 0.15",
                                                  "pass": d1 >= 0.15}
    # D2 -- foraging vs a coin flip over IDENTICAL options. The real test.
    rel = ((F["heldout_coverage"] - R["heldout_coverage"]) / R["heldout_coverage"]
           if R["heldout_coverage"] > 0 else None)
    checks["D2_heldout_coverage_vs_RANDOM_rel"] = {
        "value": round(rel, 6) if rel is not None else None, "pass_band": ">= +0.10",
        "pass": rel is not None and rel >= 0.10,
        "forage": F["heldout_coverage"], "random": R["heldout_coverage"],
        "frozen": Z["heldout_coverage"]}
    # D3 -- grounding quality, blind. Non-inferiority against FROZEN; superiority is the upside.
    fq, zq = F["wordnet"]["wn_agreement"], Z["wordnet"]["wn_agreement"]
    checks["D3_wn_agreement_vs_FROZEN"] = {
        "forage": fq, "random": R["wordnet"]["wn_agreement"], "frozen": zq,
        "delta": round(fq - zq, 6) if (fq is not None and zq is not None) else None,
        "pass_band": "delta >= -0.05 (non-inferiority)",
        "pass": fq is not None and zq is not None and (fq - zq) >= -0.05}
    # D4 -- mechanism (OBJECTIVE-ALIGNED: FORAGE optimises this directly, so it is a mechanism
    # check, not a capability claim). 5-15% below the post-hoc oracle is brain-matched;
    # 100% means the oracle leaked into the online policy.
    orr = F["foraging"]["oracle_ratio"]
    checks["D4_oracle_ratio"] = {"value": orr, "pass_band": "0.70 <= r < 1.00",
                                 "pass": orr is not None and 0.70 <= orr < 1.0,
                                 "note": "objective-aligned for FORAGE; mechanism check only"}
    # mechanism-fired gates (META_RULE_K) -- if these fail the discriminator never ran
    fired = {
        "gain_is_value_not_count": F["foraging"]["gain_distinct_values"] > 50,
        "travel_updates_fired": F["foraging"]["n_travel_updates"] > 0,
        "multiple_patches": F["foraging"]["n_patches"] >= 5,
        "multiple_corpora_chosen": F["n_distinct_corpora_read"] >= 3,
        "ranked_choice_not_all_fallback": F["foraging"]["ranked_choice_frac"] > 0.10,
        "baseline_in_band_META_RULE_AG": 0.05 < Z["dominant_source_share"] < 0.99,
    }
    checks["mechanism_fired"] = fired

    if not all(fired.values()):
        return {"verdict": "HARD_FAIL_DISCRIMINATOR_DID_NOT_FIRE",
                "verdict_msg": f"mechanism-fired gates failed: "
                               f"{[k for k, v in sorted(fired.items()) if not v]}",
                "checks": checks}

    core = [checks["D1_dominant_share_drop_vs_FROZEN"]["pass"],
            checks["D2_heldout_coverage_vs_RANDOM_rel"]["pass"],
            checks["D3_wn_agreement_vs_FROZEN"]["pass"]]
    n_pass = sum(1 for c in core if c)
    if n_pass == 3:
        v = "HARD_PASS"
    elif n_pass == 0:
        v = "HARD_FAIL"
    else:
        v = "MIDDLE_BAND"
    msg = (f"D1 dominant-source-share drop vs FROZEN = "
           f"{checks['D1_dominant_share_drop_vs_FROZEN']['value']} (need >=0.15); "
           f"D2 held-out coverage FORAGE {F['heldout_coverage']} vs RANDOM {R['heldout_coverage']} "
           f"rel={checks['D2_heldout_coverage_vs_RANDOM_rel']['value']} (need >=+0.10); "
           f"D3 WordNet agreement FORAGE {fq} vs FROZEN {zq} (need delta >= -0.05); "
           f"D4 oracle ratio {orr}. "
           f"FORAGE read {F['n_distinct_corpora_read']} corpora / banked from "
           f"{F['n_distinct_sources_banked']}; FROZEN read {Z['n_distinct_corpora_read']}. "
           f"AMENDMENT arm FORAGE_REFUSAL: dom_share {FR['dominant_source_share']}, "
           f"heldout {FR['heldout_coverage']}, wn {FR['wordnet']['wn_agreement']}, "
           f"grounded {FR['n_grounded']} vs FORAGE {F['n_grounded']} vs FROZEN {Z['n_grounded']}. "
           f"EXPOSURE frac-at-MIN_CONFIRM: FORAGE {F['exposure']['frac_items_at_min_confirm']} "
           f"vs FROZEN {Z['exposure']['frac_items_at_min_confirm']}.")
    return {"verdict": v, "verdict_msg": msg, "checks": checks}


# ============================================================================ self-test
def self_test() -> dict:
    """SCHEMA-VET F.1: constructs the REAL substrate objects the FULL run uses, at tiny scale."""
    exercised = set()
    from hdlab import corpus_registry as cr
    from hdlab import information_foraging as inf
    assert inf.run_all_selftests()
    exercised.add("information_foraging")
    reg = CorpusRegistry(max_sentences_per_corpus=20, max_bytes=200_000)
    assert len(reg.readable_names()) >= 20, reg.readable_names()
    exercised.add("CorpusRegistry")

    # F.2 substrate_signature: bind against the LIVE signatures with BASE kwargs only
    import inspect
    inspect.signature(HDFactStore).bind_partial(n_dim=64, seed=1)
    inspect.signature(checkpoint).bind_partial(None, 0, "t")
    inspect.signature(rank_material).bind_partial(None, "x", {})
    exercised.add("substrate_signature")

    store = HDFactStore(n_dim=512, seed=1,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, ["the", "a", "is", "of", "and", "in", "engine", "harvest"], "seed")
    exercised.add("ReadingLoopState")
    tracker = PrereqTracker()
    meter = UncertaintyMeter(state)
    gains = []
    for i, s in enumerate(["The old velmara engine was repaired before the harvest.",
                           "A velmara engine is an engine of the old kind.",
                           "The borlune manual is a manual of the river boat."]):
        lem = read_and_track(state, tracker, s, f"st{i}", 0)
        g, _e = meter.score(lem)
        gains.append(g)
    exercised.add("read_and_track")
    assert all(g > 0 for g in gains), gains
    assert len(sorted(set(round(g, 9) for g in gains))) > 1, f"gain must vary, got {gains}"
    row = checkpoint(state, 0, "selftest_segment", schema_thresh=0.10)
    assert "grounded_by_segment" in row and "refused_by_segment" in row, sorted(row)
    exercised.add("checkpoint_stage_a_detector")

    shelf = Shelf("smoke", frozen=False)
    diag = {"n_choice_ranked": 0, "n_choice_fallback_random": 0, "targets": [], "ranked_top": []}
    pick = choose_gap_ranked(state, tracker, shelf, random.Random(1), None, diag)
    assert pick in shelf.names, pick
    exercised.add("choose_gap_ranked")

    frozen = Shelf("smoke", frozen=True)
    assert sorted(frozen.names) == sorted(s.name for s in FROZEN_SPECS), frozen.names
    for n in frozen.names:
        assert len(frozen.handles[n].pool()) >= 5, n
    exercised.add("frozen_shelf")

    assert _wordnet_scores([("dog", "animal"), ("carburetor", "device")])["n_scorable"] == 2
    exercised.add("wordnet_scorer")

    # F.5: no nondeterministic seeding anywhere in this file
    # AST, not a text grep: a text scan of this file matches its own check and its own docstring,
    # which is exactly the kind of false positive that makes a gate get deleted rather than fixed.
    import ast
    tree = ast.parse(open(os.path.abspath(__file__), encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "hash", f"built-in hash() at line {node.lineno} (PROT-023/F.5)"
            if node.func.id == "list" and node.args:
                a = node.args[0]
                assert not (isinstance(a, ast.Call) and isinstance(a.func, ast.Name)
                            and a.func.id == "set"), f"nondeterministic dedupe at line {node.lineno}"
    exercised.add("deterministic_seeding_ast_scan")
    return {"selftest_ok": True, "exercised_entrypoints": sorted(exercised),
            "n_readable_corpora": len(reg.readable_names()),
            "gains": [round(g, 6) for g in gains]}


# ============================================================================ main
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    args = ap.parse_args(argv)

    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2))
        print("SELF-TEST PASSED")
        return 0

    run_mode = args.mode
    budget = SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET
    output_dir = _output_dir(run_mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, run_mode)
    t0 = time.time()

    st = self_test()
    print(f"[selftest] ok, {st['n_readable_corpora']} readable corpora", flush=True)

    done = exp_checkpoint.completed_units(output_dir)
    prior = exp_checkpoint.load_units(output_dir)
    per_arm: Dict[str, dict] = {}
    failures: Dict[str, str] = {}
    for arm in ARMS:
        key = exp_checkpoint.unit_key("arm", arm)
        if key in done:
            per_arm[arm] = prior[key]
            print(f"[{arm}] resumed from checkpoint", flush=True)
            continue
        print(f"[{arm}] start budget={budget}", flush=True)
        try:
            res = run_arm(arm, budget, run_mode, output_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except (MemoryError, OSError, ValueError, KeyError, IndexError, TypeError,
                AttributeError, RuntimeError) as e:
            failures[arm] = f"{type(e).__name__}: {e}"
            print(f"[{arm}] FAILED {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            continue
        exp_checkpoint.record_unit(output_dir, key, res)
        per_arm[arm] = res
        print(f"[{arm}] done in {res['elapsed_s']}s grounded={res['n_grounded']} "
              f"corpora={res['n_distinct_corpora_read']} "
              f"dom_share={res['dominant_source_share']} "
              f"heldout={res['heldout_coverage']} "
              f"wn={res['wordnet']['wn_agreement']}", flush=True)

    # currency gate (failure mode 6) -- run against the realised stream, not the design intent
    currency_ok, currency_msg = True, "ok"
    for arm, res in sorted(per_arm.items()):
        if res["foraging"]["gain_distinct_values"] <= 1:
            currency_ok, currency_msg = False, f"{arm} gain stream is constant (an item count)"

    verdict = build_verdict(per_arm) if not failures else {
        "verdict": "HARD_FAIL_ARM_CRASHED", "verdict_msg": json.dumps(failures)}
    if not currency_ok:
        verdict = {"verdict": "HARD_FAIL_CURRENCY_IS_A_COUNT", "verdict_msg": currency_msg}

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict["verdict"],
        "verdict_msg": verdict["verdict_msg"],
        "summary": f"{verdict['verdict']}: {verdict['verdict_msg'][:400]}",
        "elapsed_s": round(time.time() - t0, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "checks": verdict.get("checks"),
        "arms": per_arm,
        "arm_failures": failures,
        "cardinality": {"expected_n_units": EXPECTED_N_UNITS, "n_units": len(per_arm),
                        "cardinality_ok": len(per_arm) == EXPECTED_N_UNITS},
        "arms_differ_verified": len(sorted(set(a["read_sentence_digest"] for a in per_arm.values()))) == len(per_arm),
        "config": {"n_dim": N_DIM, "budget": budget, "chunk": CHUNK,
                   "schema_thresh": SCHEMA_THRESH, "seed_vocab_n": SEED_VOCAB_N,
                   "heldout_probe_range": [HELDOUT_PROBE_LO, HELDOUT_PROBE_HI],
                   "travel_tau": TRAVEL_TAU, "rho_halflife": RHO_HALFLIFE,
                   "rho_slow_halflife": RHO_SLOW_HALFLIFE, "beta_leave": BETA_LEAVE,
                   "patch_fixed_len": PATCH_FIXED_LEN, "substrate_seed": SUBSTRATE_SEED,
                   "peek_n": PEEK_N, "final_metrics_atomicity": "tmp_replace"},
        "selftest": st,
    }
    _write_json_atomic(os.path.join(output_dir, "metrics.json"), metrics)
    print(json.dumps({k: metrics[k] for k in ("verdict", "verdict_msg", "elapsed_s")}, indent=2),
          flush=True)
    return 0


if __name__ == "__main__":
    _out = _output_dir("full")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:
        _write_crash_metrics(_out, _e)
        raise
