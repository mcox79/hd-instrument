"""experiments/exp_retrieval_practice_consolidation_v1.py

PROBLEM: grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice.

THE WALL (inherited, not re-quoted as a result): the read-to-grow loop grounds a word only if a
SPLIT-HALF COSINE coherence of its context vectors clears SCHEMA_THRESH=0.25 within patience_max=3
consolidation passes (hdlab.grounding_acquisition_loop.consolidation_pass +
schema_consistency_split_half). Empirically P(ground | k encounters) PEAKS at k=4 and FALLS toward
k=20 -- MORE exposures give LESS grounding. That is backwards from the brain: repeated coherent
exposure should ACCUMULATE into durable memory.

THE BRAIN OPERATION WE REPLICATE (PINNED-BY-EVIDENCE): RETRIEVAL PRACTICE / the testing effect.
  * Karpicke & Roediger 2008 (Science 319:966): once an item is retrievable, REPEATED RETRIEVAL
    drives ~80% 1-week retention while equal REPEATED STUDY is statistically indistinguishable from
    zero. Retrieval is a memory MODIFIER, not a neutral read-out.
  * Mozer, Pashler, Cepeda, Lindsey & Vul 2009 (NIPS, Multiscale Context Model), Eq. 7 -- the
    PUBLISHED, human-data-fit update rule we COPY:
        Delta s = eps * (1 - s)
    with eps LARGE on a successful retrieval and SMALL on failure/first-exposure. The (1 - s) term
    IS Bjork & Bjork's New Theory of Disuse (biggest boost when weakest; diminishing returns -> no
    runaway). It is RETRIEVAL-GATED, not exposure-count-gated.
  * Kornell, Hays & Bjork 2009 + Marsh et al. 2007 -- the 3-way outcome rule: HIT -> large
    increment; MISS-then-CORRECTED (feedback = the new context itself) -> small positive; MISS-
    uncorrected -> do not fold noise into the estimate (risks interference).

THE OPERATION we copy exactly; the PARAMETERS (hit/near-miss thresholds, eps ratio, ground
threshold) are OURS-UNDER-TEST and SWEPT, never adopted (Mozer's eps ratio ~9 was fit to verbal
paired-associate spacing over days -- a different regime; we sweep it here).

DESIGN (exposure-matched by construction -- the whole point of the testing-effect design):
  1. CAPTURE: read real modern corpus (simplewiki + news + science, the incumbent 4-corpus shelf)
     with the incumbent consolidation live. Capture (a) the anchor pool the incumbent built
     (seeds + incumbent-grounded), (b) every ungrounded library item's FULL trace list, (c) the
     CONSOLIDATION_FAIL population = words with >= MIN_CONFIRM=4 traces, not grounded, not refused.
  2. RETRIEVAL-SIGNAL DIAGNOSTIC (the fork): for the CONSOLIDATION_FAIL words, is cos(trace,
     same-word bundle) > cos(trace, other-word bundle)? If yes, a retrievable signal EXISTS and the
     wall is encoding-bound (retrieval practice can help). If at chance, the wall is REPRESENTATION-
     bound (a full-PASS negative -> reader_meaning_channel/ATL). Answered BEFORE building the gate.
  3. ARMS on IDENTICAL trace sets (perfect exposure match):
     RESTUDY   incumbent split-half coherence gate (>= SCHEMA_THRESH), best-case (all traces at
               once). THE exposure-matched re-study control -- retrieval must beat re-study.
     RETRIEVE  Mozer Eq.7 retrieval-gated strengthening + 3-way outcome. MY MECHANISM.
     EXPOSURE  Delta s = eps_fixed*(1-s) on EVERY exposure, no retrieval gate (folds all contexts).
               Isolates "the retrieval GATE" from "more updates" (brief FLOOR: strengthen by count).
     TWIN_SHUF info-free twin: same retrieval outcomes, SHUFFLED across the word's own encounters.
     TWIN_RAND info-free twin: retrieval score replaced by a random draw. Both MUST LOSE.
  4. THE 0.45 ANCHOR GATE (canonicalize, SENSE_MATCH_THRESH) is UNCHANGED for every arm, so no arm
     can manufacture grounding by lowering the sense bar (brief: do NOT trade precision for recall).
  5. METRIC: GROUNDED-AND-CORRECT rate on the CONSOLIDATION_FAIL population -- a word grounds to an
     eligible anchor AND that (word, anchor) pair is WordNet-related (the loop's own blind quality
     check, _wordnet_scores; WordNet plays no part in any decision). Paired bootstrap CI over words;
     held-out DEV/TEST word split (params swept on DEV, headline on TEST); null p95 for the twins.

REUSE (wire-don't-island; imported and called, never reimplemented):
  hdlab.reading_grounding_loop  ReadingLoopState/seed_known_words/process_sentence/checkpoint/
                                content_lemmas/canonicalize/ConceptSpace/_cos/SENSE_MATCH_THRESH
  hdlab.grounding_acquisition_loop  schema_consistency_split_half/MIN_CONFIRM/Trace
  hdlab.closed_class_lexicon    is_eligible_meaning (the anchor eligibility predicate)
  hdlab.hd_fact_store           a fresh throwaway store (canonical foundation never touched)
  experiments.exp_reading_comprehensible_input_zpd_v1  the CI_050 read machinery + constants
  experiments.exp_information_foraging_reading_v1       Shelf/load_base_vocab/_wordnet_scores
  experiments.exp_aimed_reading_register_controlled_v1  build_register_context (the probe)

ASCII-only. Deterministic: sorted(set(...)), fixed integer seeds, np.random.default_rng(seed),
never Python hash(). NO hdlab/ write. NO external LLM. Glass-box throughout.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.exp_reading_comprehensible_input_zpd_v1 import (ARMS, CHUNK, N_DIM, SCHEMA_THRESH,
                                                                 SEED_VOCAB_N, SUBSTRATE_SEED,
                                                                 choose_source, TRAVEL_TAU,
                                                                 RHO_HALFLIFE, RHO_SLOW_HALFLIFE,
                                                                 BETA_LEAVE, SEG_WINDOW, SEG_K,
                                                                 SEG_MIN_RUN, SEG_MAX_RUN)
from experiments.exp_information_foraging_reading_v1 import Shelf, load_base_vocab, _wordnet_scores
from experiments.exp_aimed_reading_register_controlled_v1 import build_register_context
from hdlab.hd_fact_store import HDFactStore
from hdlab.information_foraging import ForagingConfig, ForagingController, SurpriseSegmenter
from hdlab.reading_grounding_loop import (KNOWN_RELATION, MEANING_RELATION, ReadingLoopState,
                                          SENSE_MATCH_THRESH, ConceptSpace, canonicalize,
                                          checkpoint, content_lemmas, process_sentence,
                                          seed_known_words, _cos)
from hdlab.grounding_acquisition_loop import MIN_CONFIRM, Trace, schema_consistency_split_half
from hdlab.closed_class_lexicon import is_eligible_meaning

# ---- REMOTE data deps (remote_cpu_queue; spaCy-free -- closed_class_lexicon degrades to its frozen
# stop-word snapshot + data/closed_class_lexicon_v1.json; the read forages hashed bags, never parses;
# --confirm-all runs encoder_diagnostic(do_structural=False) so nothing needs a live parser) --------
# KB_REFERENT: data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv
# KB_REFERENT: data/corpora
# KB_REFERENT: data/closed_class_lexicon_v1.json   # pre-built spaCy-free closed-class lexicon
# KB_REFERENT: data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
# KB_REFERENT: data/grounding_testbed/Ratings_Warriner_et_al.csv
# KB_REFERENT: data/corpora/binder/binder2016_ratings.csv   # measured Binder-535 (anti-artifact check)
# KB_REFERENT: data/exp_selpref_unseen_lowdata_v1/_ckpt_full/artifact_BINDER65_PREDICT.npz
# KB_REFERENT: data/exp_selpref_unseen_lowdata_v1/_ckpt_full/units.jsonl

ANCHOR_NAME = os.environ.get("HDLAB_EXP_NAME", "retrieval_practice_consolidation_v1")
FULL_BUDGET, SMOKE_BUDGET = 3000, 700
N_BOOT = 2000

# ---- OUR-INVENTION-UNDER-TEST parameters (swept; never adopted from a recording) ----------------
# The retrieval scorer works in the masked bag-of-content-words context space (d=256). A single
# trace vs a running bundle is a noisier probe than the summed-bundle 0.45 the sense gate uses, so
# the hit/near-miss thresholds sit BELOW 0.45 and are swept. The eps ratio starts near Mozer's
# fitted 9 (eps_hit/eps_miss) but is swept -- our regime (word-sense grounding from running text)
# is not verbal paired-associate spacing.
DEFAULT_PARAMS = {
    "hit_thresh": 0.18,      # cos(new context, running estimate) >= this  -> HIT (successful retrieval)
    "nearmiss_thresh": 0.08, # >= this and < hit_thresh                    -> MISS-then-CORRECTED
    "eps_hit": 0.45,         # Mozer Eq.7 eps on a successful retrieval
    "eps_corr": 0.10,        # eps on a corrected miss (feedback = the new context)
    "eps_miss": 0.05,        # eps on first-exposure / uncorrected restudy increment
    "ground_thresh": 0.50,   # durable strength s required to ground
}
# swept grid (kept small; DEV-tuned, TEST-reported)
SWEEP = {
    "hit_thresh": [0.14, 0.18, 0.22],
    "eps_hit": [0.35, 0.45, 0.55],
    "ground_thresh": [0.45, 0.55, 0.65],
}


def _output_dir(run_mode: str) -> str:
    base = ANCHOR_NAME[4:] if ANCHOR_NAME.startswith("exp_") else ANCHOR_NAME
    return os.path.join(REPO_ROOT, "data", f"exp_{base}" + ("_smoke" if run_mode == "smoke" else ""))


# ===================== 1. CAPTURE ================================================================

def capture(budget: int, run_mode: str, seed: int, arm: str = "CI_050",
            route_b: bool = False, encoder=None, sources=None,
            collect_ctx_words: bool = False) -> dict:
    """Read the incumbent 4-corpus shelf with the incumbent consolidation LIVE. Return the anchor
    pool the incumbent built, every ungrounded library item's full trace list, the incumbent
    grounded set, and the CONSOLIDATION_FAIL population.

    route_b (default OFF): also accumulate the SEPARABLE per-lemma co-occurrence counts (ROUTE B,
    track_all_content_lemmas) so the distributional PPMI+SVD representation can be built for the
    representation-bound probe. Costs memory; only the probe path sets it."""
    t0 = time.time()
    mode, param = ARMS[arm]
    seed_words = load_base_vocab(0, SEED_VOCAB_N)
    store = HDFactStore(n_dim=N_DIM, seed=SUBSTRATE_SEED + seed,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL", MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    if route_b:
        state.space.track_all_content_lemmas = True
    seed_known_words(state, seed_words, source="seed_base_vocabulary")
    shelf = Shelf(run_mode, frozen=False)
    if sources is not None:
        shelf.handles = {k: v for k, v in shelf.handles.items() if k in sources}
        if not shelf.handles:
            raise ValueError(f"no shelf handles match sources={sources}; have {list(Shelf(run_mode, frozen=False).handles)}")
    rng = random.Random(SUBSTRATE_SEED + seed)
    cfg = ForagingConfig(travel_step_duration=TRAVEL_TAU, rho_halflife_steps=RHO_HALFLIFE,
                         rho_slow_halflife_steps=RHO_SLOW_HALFLIFE, beta_leave=BETA_LEAVE,
                         stochastic=True, seed=SUBSTRATE_SEED + seed)
    ctrl = ForagingController(cfg)
    seg = SurpriseSegmenter(SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN)

    encounter: Counter = Counter()
    ctx_words: Dict[str, list] = defaultdict(list)   # lemma -> list of per-occurrence context-lemma lists
    n_read = pass_idx = since_ckpt = 0
    prev_banked = 0
    current: Optional[str] = None
    cdiag = {"n_chosen": 0, "n_fallback": 0, "choices": []}

    def known_set():
        return set(w.lower() for w in seed_words) | {p["subject"] for p in state.provenance}

    while n_read < budget:
        nxt = choose_source(arm, mode, param, shelf, known_set(), rng, current, cdiag, None)
        if nxt != current:
            if current is not None:
                ctrl.travel()
            current = nxt
            ctrl.enter_patch(current)
        handle = shelf.handles[current]
        while n_read < budget:
            batch = handle.take(1)
            if not batch:
                break
            sentence = batch[0]
            sent_lems = sorted(set(content_lemmas(sentence)))
            for lem in sent_lems:
                encounter[lem] += 1
            if collect_ctx_words:
                for lem in sent_lems:
                    if len(ctx_words[lem]) < 40:            # cap per-word occurrences (memory)
                        ctx_words[lem].append([c for c in sent_lems if c != lem])
            process_sentence(state, sentence, f"{arm}_s{seed}_{n_read}", pass_idx, encoder=encoder)
            banked_now = len(state.provenance)
            gy = float(banked_now - prev_banked); prev_banked = banked_now
            ctrl.harvest(gy)
            n_read += 1; since_ckpt += 1
            if since_ckpt >= CHUNK:
                checkpoint(state, pass_idx, current, schema_thresh=SCHEMA_THRESH)
                pass_idx += 1; since_ckpt = 0
            if seg.observe(gy) and ctrl.should_leave():
                break
    if since_ckpt > 0:
        checkpoint(state, pass_idx, current or "final", schema_thresh=SCHEMA_THRESH)

    grounded = {p["subject"] for p in state.provenance}
    refused = {r.get("lemma") for r in state.refusals}
    # CONSOLIDATION_FAIL population: in library, >= MIN_CONFIRM traces, not grounded, not refused.
    items = state.library.items
    consol_fail = {}
    all_ge4_ungrounded = {}
    for lem, it in items.items():
        ntr = len(it.traces or [])
        if ntr < MIN_CONFIRM:
            continue
        if it.status.startswith("GROUNDED"):
            continue
        all_ge4_ungrounded[lem] = it
        if lem not in refused:
            consol_fail[lem] = it
    return {
        "state": state, "grounded": grounded, "refused": refused, "encounter": encounter,
        "consol_fail": consol_fail, "all_ge4_ungrounded": all_ge4_ungrounded,
        "n_read": n_read, "elapsed_s": round(time.time() - t0, 2),
        "seed_words": set(w.lower() for w in seed_words),
        "ctx_words": dict(ctx_words) if collect_ctx_words else None,
    }


# ===================== 2. RETRIEVAL-SIGNAL DIAGNOSTIC (the fork) =================================

def retrieval_signal_diagnostic(pop: Dict[str, object], rng: np.random.Generator,
                                n_pairs: int = 4000) -> dict:
    """Is there a retrievable signal for the CONSOLIDATION_FAIL words? For random single traces,
    cos(trace, same-word bundle-of-the-rest) vs cos(trace, a DIFFERENT word's bundle). If self >>
    other, a retrievable signal exists (encoding-bound). If ~equal, representation-bound."""
    lemmas = sorted(pop)
    if len(lemmas) < 2:
        return {"n": 0, "self_mean": None, "other_mean": None, "auc": None}
    bundles = {l: np.sum([t.context_vec for t in pop[l].traces], axis=0) for l in lemmas}
    self_scores: List[float] = []
    other_scores: List[float] = []
    for _ in range(n_pairs):
        l = lemmas[int(rng.integers(0, len(lemmas)))]
        traces = pop[l].traces
        i = int(rng.integers(0, len(traces)))
        t = traces[i]
        rest = np.sum([x.context_vec for j, x in enumerate(traces) if j != i], axis=0)
        if np.any(rest != 0.0):
            self_scores.append(_cos(t.context_vec, rest))
        o = l
        while o == l:
            o = lemmas[int(rng.integers(0, len(lemmas)))]
        other_scores.append(_cos(t.context_vec, bundles[o]))
    # AUC: P(self > other) over independent random draws (a simple rank-discrimination readout)
    ss = np.array(self_scores); os_ = np.array(other_scores)
    m = min(len(ss), len(os_))
    auc = float(np.mean(ss[:m] > os_[:m])) if m else None
    return {"n": m, "self_mean": round(float(np.mean(ss)), 4) if len(ss) else None,
            "other_mean": round(float(np.mean(os_)), 4) if len(os_) else None,
            "self_p50": round(float(np.median(ss)), 4) if len(ss) else None,
            "auc_self_gt_other": round(auc, 4) if auc is not None else None}


# ===================== 3. CONSOLIDATION ARMS (identical trace sets) ==============================

def _eligible_anchor(raw_sum: np.ndarray, lemma: str, space: ConceptSpace) -> Tuple[str, float]:
    """The UNCHANGED 0.45 sense gate: canonicalize against the incumbent anchor pool, eligible
    anchors only. Returns (anchor_or_self, best_cos). anchor==lemma means NO eligible anchor cleared
    SENSE_MATCH_THRESH (a tautology; refused, never grounded)."""
    return canonicalize(lemma, raw_sum, space, thresh=SENSE_MATCH_THRESH, eligible=is_eligible_meaning)


def arm_restudy(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict) -> dict:
    """Incumbent split-half coherence gate, best-case (all traces at once). Grounds iff schema
    coherence >= SCHEMA_THRESH AND an eligible anchor clears 0.45."""
    schema = schema_consistency_split_half(traces, min_half_size=2)
    if schema is None or schema < SCHEMA_THRESH:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "SCHEMA_FAIL",
                "s": None, "schema": None if schema is None else round(float(schema), 4)}
    raw = np.sum([t.context_vec for t in traces], axis=0)
    anchor, best = _eligible_anchor(raw, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": None, "schema": round(float(schema), 4)}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": None, "schema": round(float(schema), 4)}


def _retrieve_core(traces: List[Trace], p: dict, score_fn: Callable[[np.ndarray, np.ndarray, int], float],
                   fold_on_miss: bool = False) -> Tuple[np.ndarray, float, dict]:
    """Sequential Mozer-Eq.7 retrieval-gated consolidation. Returns (confirmed_estimate m,
    durable strength s, telemetry). score_fn(new_context, running_estimate, encounter_index) ->
    retrieval score (cos, or an info-free surrogate for the twins)."""
    hit_th, near_th = p["hit_thresh"], p["nearmiss_thresh"]
    e_hit, e_corr, e_miss, gt = p["eps_hit"], p["eps_corr"], p["eps_miss"], p["ground_thresh"]
    m = np.array(traces[0].context_vec, dtype=np.float64, copy=True)      # fast-mapping seed
    s = e_miss * 1.0                                                       # first-exposure encoding
    n_hit = n_corr = n_miss = 0
    for idx in range(1, len(traces)):
        c = traces[idx].context_vec
        r = score_fn(c, m, idx)
        if r >= hit_th:
            eps = e_hit; n_hit += 1; m = m + c                            # HIT: strengthen + fold in
        elif r >= near_th:
            eps = e_corr; n_corr += 1; m = m + c                          # CORRECTED: elaborate
        else:
            eps = e_miss if fold_on_miss else 0.0; n_miss += 1           # MISS: no strengthen, keep m clean
            if fold_on_miss:
                m = m + c
        s = min(1.0, max(0.0, s + eps * (1.0 - s)))
    return m, s, {"n_hit": n_hit, "n_corr": n_corr, "n_miss": n_miss}


def arm_retrieve(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict) -> dict:
    """MY MECHANISM: retrieve the running estimate, test the new context, strengthen on success.
    Grounds iff durable s >= ground_thresh AND an eligible anchor clears 0.45 (gate UNCHANGED)."""
    m, s, tel = _retrieve_core(traces, p, lambda c, mm, i: _cos(c, mm))
    if s < p["ground_thresh"]:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "WEAK_TRACE",
                "s": round(s, 4), **tel}
    anchor, best = _eligible_anchor(m, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": round(s, 4), **tel}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": round(s, 4), **tel}


def arm_exposure(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict) -> dict:
    """EXPOSURE-COUNT floor: Delta s = eps_fixed*(1-s) on EVERY exposure, no retrieval gate; fold
    all contexts. Isolates 'the retrieval gate' from 'more updates'."""
    pp = dict(p); pp["eps_hit"] = pp["eps_corr"] = pp["eps_miss"] = p["eps_hit"]
    # force every encounter to count as an update regardless of score:
    m, s, tel = _retrieve_core(traces, pp, lambda c, mm, i: 1e9, fold_on_miss=True)
    if s < p["ground_thresh"]:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "WEAK_TRACE",
                "s": round(s, 4), **tel}
    anchor, best = _eligible_anchor(m, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": round(s, 4), **tel}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": round(s, 4), **tel}


def arm_retrieve_anchor(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict) -> dict:
    """MORE FAITHFUL retrieval: retrieve the MEANING (PBV-style). After each fold, canonicalize the
    running estimate to a provisional anchor; on the next encounter, RETRIEVE that anchor and test
    whether the NEW context still points at it (r = cos(new_context, anchor_bundle)). Strengthen on
    a hit. This tests the carried MEANING hypothesis, not self-coherence -- the closest analog to
    Karpicke retrieval (retrieve the answer, test it). Rules out 'we built the weak retrieval'."""
    hit_th, near_th = p["hit_thresh"], p["nearmiss_thresh"]
    e_hit, e_corr, e_miss, gt = p["eps_hit"], p["eps_corr"], p["eps_miss"], p["ground_thresh"]
    m = np.array(traces[0].context_vec, dtype=np.float64, copy=True)
    s = e_miss * 1.0
    n_hit = n_corr = n_miss = 0
    for idx in range(1, len(traces)):
        c = traces[idx].context_vec
        anchor, _ = _eligible_anchor(m, lemma, space)      # RETRIEVE the current meaning guess
        if anchor != lemma and (ab := space.bundle(anchor)) is not None:
            r = _cos(c, ab)                                 # test: does new context point at it?
        else:
            r = _cos(c, m)                                  # no meaning yet -> self-coherence fallback
        if r >= hit_th:
            eps = e_hit; n_hit += 1; m = m + c
        elif r >= near_th:
            eps = e_corr; n_corr += 1; m = m + c
        else:
            eps = 0.0; n_miss += 1
        s = min(1.0, max(0.0, s + eps * (1.0 - s)))
    if s < gt:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "WEAK_TRACE",
                "s": round(s, 4), "n_hit": n_hit, "n_corr": n_corr, "n_miss": n_miss}
    anchor, best = _eligible_anchor(m, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": round(s, 4), "n_hit": n_hit, "n_corr": n_corr, "n_miss": n_miss}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": round(s, 4), "n_hit": n_hit, "n_corr": n_corr, "n_miss": n_miss}


def arm_twin_shuffle(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict,
                     rng: np.random.Generator) -> dict:
    """INFO-FREE TWIN: same retrieval scores, SHUFFLED across the word's own encounters, so the
    strengthen decisions are decoupled from which context actually matched. Must lose."""
    scores = [_cos(traces[i].context_vec, traces[0].context_vec) for i in range(1, len(traces))]
    perm = list(range(len(scores)))
    rng.shuffle(perm)
    shuffled = [scores[perm[i]] for i in range(len(scores))]
    m, s, tel = _retrieve_core(traces, p, lambda c, mm, i: shuffled[i - 1])
    if s < p["ground_thresh"]:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "WEAK_TRACE",
                "s": round(s, 4), **tel}
    anchor, best = _eligible_anchor(m, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": round(s, 4), **tel}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": round(s, 4), **tel}


def arm_twin_random(lemma: str, traces: List[Trace], space: ConceptSpace, p: dict,
                    rng: np.random.Generator) -> dict:
    """INFO-FREE TWIN: retrieval score replaced by a random draw from the same range. Must lose."""
    draws = rng.uniform(-0.1, 0.4, size=max(0, len(traces) - 1))
    m, s, tel = _retrieve_core(traces, p, lambda c, mm, i: draws[i - 1])
    if s < p["ground_thresh"]:
        return {"grounded": False, "meaning": None, "best_cos": None, "reason": "WEAK_TRACE",
                "s": round(s, 4), **tel}
    anchor, best = _eligible_anchor(m, lemma, space)
    if anchor == lemma:
        return {"grounded": False, "meaning": None, "best_cos": round(float(best), 4),
                "reason": "NO_ANCHOR", "s": round(s, 4), **tel}
    return {"grounded": True, "meaning": anchor, "best_cos": round(float(best), 4),
            "reason": "GROUNDED", "s": round(s, 4), **tel}


# ===================== 4. SCORING ===============================================================

def _wn_related(pairs: List[Tuple[str, str]]) -> Dict[Tuple[str, str], bool]:
    """Per-pair WordNet relatedness (the loop's own blind quality check). Returns a dict so we can
    score grounded-AND-correct per WORD for the paired bootstrap."""
    out: Dict[Tuple[str, str], bool] = {}
    if not pairs:
        return out
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return {pr: False for pr in pairs}
    for subj, obj in pairs:
        ss, oo = wn.synsets(subj), wn.synsets(obj)
        rel = False
        if ss and oo:
            for a in ss[:6]:
                ac = set(a.closure(lambda x: x.hypernyms()))
                for b in oo[:6]:
                    if a == b or b in ac or a in set(b.closure(lambda x: x.hypernyms())):
                        rel = True
                    try:
                        w = a.wup_similarity(b)
                    except Exception:
                        w = None
                    if w is not None and w >= 0.5:
                        rel = True
        out[(subj, obj)] = rel
    return out


def score_arm(pop_lemmas: List[str], results: Dict[str, dict]) -> dict:
    """Given per-word arm results, compute grounded / grounded-and-correct indicators per word."""
    grounded = [l for l in pop_lemmas if results[l]["grounded"]]
    pairs = [(l, results[l]["meaning"]) for l in grounded]
    rel = _wn_related(pairs)
    correct_ind = {l: (1 if (results[l]["grounded"] and rel.get((l, results[l]["meaning"]), False)) else 0)
                   for l in pop_lemmas}
    grounded_ind = {l: (1 if results[l]["grounded"] else 0) for l in pop_lemmas}
    n = len(pop_lemmas)
    n_g = sum(grounded_ind.values())
    n_c = sum(correct_ind.values())
    return {
        "n_pop": n, "n_grounded": n_g, "n_grounded_correct": n_c,
        "grounded_rate": round(n_g / n, 6) if n else 0.0,
        "grounded_correct_rate": round(n_c / n, 6) if n else 0.0,
        "precision_wn": round(n_c / n_g, 6) if n_g else None,
        "_correct_ind": correct_ind, "_grounded_ind": grounded_ind,
    }


def paired_bootstrap(ind_a: Dict[str, int], ind_b: Dict[str, int], lemmas: List[str],
                     rng: np.random.Generator, n_boot: int = N_BOOT) -> dict:
    """Paired bootstrap over WORDS of (rate_a - rate_b). CI-separated iff lo > 0."""
    a = np.array([ind_a[l] for l in lemmas], dtype=np.float64)
    b = np.array([ind_b[l] for l in lemmas], dtype=np.float64)
    n = len(lemmas)
    if n == 0:
        return {"delta": 0.0, "lo": 0.0, "hi": 0.0, "ci_separated": False}
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        diffs[i] = a[idx].mean() - b[idx].mean()
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"delta": round(float(a.mean() - b.mean()), 6), "lo": round(float(lo), 6),
            "hi": round(float(hi), 6), "ci_separated": bool(lo > 0)}


def _auc(scores: np.ndarray, labels: np.ndarray) -> Optional[float]:
    """AUC = P(score of a positive > score of a negative), ties count 0.5."""
    pos = scores[labels == 1]; neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    gt = 0.0
    for s in pos:
        gt += np.sum(s > neg) + 0.5 * np.sum(s == neg)
    return float(gt / (len(pos) * len(neg)))


def decisive_selection_auc(pop_lemmas: List[str], pop: Dict[str, object], space: ConceptSpace,
                           params: dict, rng: np.random.Generator) -> dict:
    """THE DECISIVE, RATE-INDEPENDENT TEST. Hold the meaning representation FIXED (full-bundle m for
    every word) so (grounds-at-0.45?, WordNet-correct?) is arm-independent. Then ask: does the
    RETRIEVAL-derived confidence score rank the groundable-and-CORRECT words above chance? If AUC ~=
    0.5 (== a random score), the retrieval signal adds nothing to selection -> representation-bound.

    Compares selection scores: retrieve_s, retrieve_anchor_s, exposure_s, self_signal margin,
    random. Labels: 'correct' (grounds to a WordNet-correct anchor under the fixed full bundle)."""
    # fixed full-bundle meaning + labels
    full_pairs = []
    grounded_fixed = {}
    for l in pop_lemmas:
        raw = np.sum([t.context_vec for t in pop[l].traces], axis=0)
        anchor, best = _eligible_anchor(raw, l, space)
        grounded_fixed[l] = (anchor if anchor != l else None, float(best))
        if anchor != l:
            full_pairs.append((l, anchor))
    rel = _wn_related(full_pairs)
    correct_lbl = np.array([1 if (grounded_fixed[l][0] is not None and
                                  rel.get((l, grounded_fixed[l][0]), False)) else 0
                            for l in pop_lemmas])
    grounded_lbl = np.array([1 if grounded_fixed[l][0] is not None else 0 for l in pop_lemmas])
    # per-word selection scores
    retr = {l: arm_retrieve(l, pop[l].traces, space, params)["s"] for l in pop_lemmas}
    ranc = {l: arm_retrieve_anchor(l, pop[l].traces, space, params)["s"] for l in pop_lemmas}
    # self-signal margin: mean cos(trace, rest) - mean cos(trace, global mean of other words)
    glob = np.mean([np.sum([t.context_vec for t in pop[l].traces], axis=0) for l in pop_lemmas], axis=0)
    selfsig = {}
    for l in pop_lemmas:
        tr = pop[l].traces
        cs = []
        for i, t in enumerate(tr):
            rest = np.sum([x.context_vec for j, x in enumerate(tr) if j != i], axis=0)
            if np.any(rest != 0.0):
                cs.append(_cos(t.context_vec, rest) - _cos(t.context_vec, glob))
        selfsig[l] = float(np.mean(cs)) if cs else 0.0
    randsc = {l: float(rng.random()) for l in pop_lemmas}
    exp_s = {l: arm_exposure(l, pop[l].traces, space, params)["s"] for l in pop_lemmas}

    def sc(d):
        return np.array([d[l] if d[l] is not None else 0.0 for l in pop_lemmas], dtype=np.float64)

    def _auc_ci(scores: np.ndarray, labels: np.ndarray) -> dict:
        """Bootstrap CI on AUC over words. above_chance = 2.5th pct > 0.5."""
        base = _auc(scores, labels)
        if base is None:
            return {"auc": None, "lo": None, "hi": None, "above_chance": None}
        n = len(labels)
        vals = []
        for _ in range(800):
            idx = rng.integers(0, n, size=n)
            a = _auc(scores[idx], labels[idx])
            if a is not None:
                vals.append(a)
        lo, hi = (np.percentile(vals, [2.5, 97.5]) if vals else (base, base))
        return {"auc": round(base, 4), "lo": round(float(lo), 4), "hi": round(float(hi), 4),
                "above_chance": bool(lo > 0.5)}

    out = {"n_pop": len(pop_lemmas),
           "n_groundable_fixed_bundle": int(grounded_lbl.sum()),
           "n_correct_fixed_bundle": int(correct_lbl.sum()),
           "base_precision_if_all_grounded": round(float(correct_lbl.sum() / max(1, grounded_lbl.sum())), 4)}
    for name, d in (("retrieve_s", retr), ("retrieve_anchor_s", ranc), ("exposure_s", exp_s),
                    ("self_signal", selfsig), ("random", randsc)):
        out[f"auc_correct__{name}"] = None if _auc(sc(d), correct_lbl) is None else round(_auc(sc(d), correct_lbl), 4)
        out[f"auc_groundable__{name}"] = None if _auc(sc(d), grounded_lbl) is None else round(_auc(sc(d), grounded_lbl), 4)
    # bootstrap CI on the two mechanism scores for the CORRECT label (the decisive negative)
    out["auc_ci_correct__retrieve_s"] = _auc_ci(sc(retr), correct_lbl)
    out["auc_ci_correct__retrieve_anchor_s"] = _auc_ci(sc(ranc), correct_lbl)
    return out


def m_quality_matched(pop_lemmas: List[str], pop: Dict[str, object], space: ConceptSpace,
                      params: dict) -> dict:
    """Does RETRIEVE's hits-only estimate m canonicalize to a CORRECT anchor more often than the
    full-bundle (re-study) m, among words that ground under each? Isolates 'a cleaner m' from
    'grounds more words'. Precision compared at each arm's own natural grounding set."""
    def _prec(m_fn) -> dict:
        pairs, ng = [], 0
        for l in pop_lemmas:
            m = m_fn(l)
            anchor, best = _eligible_anchor(m, l, space)
            if anchor != l:
                ng += 1; pairs.append((l, anchor))
        rel = _wn_related(pairs)
        nc = sum(1 for pr in pairs if rel.get(pr, False))
        return {"n_grounded": ng, "n_correct": nc,
                "precision": round(nc / ng, 4) if ng else None}
    full = _prec(lambda l: np.sum([t.context_vec for t in pop[l].traces], axis=0))
    retr = _prec(lambda l: _retrieve_core(pop[l].traces, params, lambda c, mm, i: _cos(c, mm))[0])
    return {"full_bundle_restudy_m": full, "retrieve_hits_only_m": retr}


def characterize_population(pop_lemmas: List[str], pop: Dict[str, object], space: ConceptSpace,
                            encounter: Counter) -> dict:
    """WHAT are the CONSOLIDATION_FAIL words? The brief asserts '>=4 COHERENT traces'. Test it: split
    the population by (a) has a WordNet target at all, (b) polysemy, (c) split-half COHERENCE, (d) an
    eligible anchor exists. This locates the wall: durability (coherent+anchor+single-sense but
    unground) vs representation (no target / polysemous / no anchor / incoherent traces)."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        wn = None
    cat: Counter = Counter()
    schema_vals: List[float] = []
    coherent_single_anchor: List[str] = []      # the population retrieval-practice COULD help
    for l in pop_lemmas:
        tr = pop[l].traces
        sch = schema_consistency_split_half(tr, min_half_size=2)
        if sch is not None:
            schema_vals.append(float(sch))
        raw = np.sum([t.context_vec for t in tr], axis=0)
        anchor, best = _eligible_anchor(raw, l, space)
        has_anchor = anchor != l
        nsyn = len(wn.synsets(l)) if wn is not None else 0
        coherent = (sch is not None and sch >= SCHEMA_THRESH)
        if nsyn == 0:
            cat["NO_WORDNET_TARGET_propernoun_or_oov"] += 1
        elif nsyn >= 5:
            cat["POLYSEMOUS_ge5_senses"] += 1
        elif not has_anchor:
            cat["SINGLE_SENSE_but_NO_ELIGIBLE_ANCHOR"] += 1
        elif not coherent:
            cat["HAS_ANCHOR_but_INCOHERENT_traces_splithalf_lt_0.25"] += 1
        else:
            cat["COHERENT_SINGLE_SENSE_WITH_ANCHOR"] += 1
            coherent_single_anchor.append(l)
    sv = np.array(schema_vals) if schema_vals else np.array([0.0])
    return {"n": len(pop_lemmas),
            "by_category": dict(sorted(cat.items(), key=lambda kv: -kv[1])),
            "splithalf_coherence": {"mean": round(float(sv.mean()), 4),
                                    "p50": round(float(np.median(sv)), 4),
                                    "frac_ge_0.25_incumbent_gate": round(float((sv >= SCHEMA_THRESH).mean()), 4),
                                    "frac_ge_0.10": round(float((sv >= 0.10).mean()), 4)},
            "n_coherent_single_sense_with_anchor": len(coherent_single_anchor),
            "examples_coherent_single_sense": sorted(coherent_single_anchor)[:20]}


def depth_curve(pop_lemmas: List[str], results: Dict[str, dict], pop: Dict[str, object]) -> dict:
    """P(grounded-and-correct | k traces) per arm -- does it RISE with k (vs the incumbent's fall)?"""
    by_k_tot: Counter = Counter()
    by_k_c: Counter = Counter()
    for l in pop_lemmas:
        k = min(len(pop[l].traces), 20)
        by_k_tot[k] += 1
        if results[l]["grounded"] and results[l].get("_correct"):
            by_k_c[k] += 1
    return {str(k): {"n": by_k_tot.get(k, 0),
                     "p": round(by_k_c.get(k, 0) / by_k_tot[k], 4) if by_k_tot.get(k) else None}
            for k in range(4, 21)}


# ===================== 5. DRIVER ================================================================

def _dev_test_split(lemmas: List[str], seed: int) -> Tuple[List[str], List[str]]:
    """Deterministic held-out split by a stable hash of the lemma (NOT Python hash())."""
    import hashlib
    dev, test = [], []
    for l in sorted(lemmas):
        h = int(hashlib.sha1(f"{seed}:{l}".encode()).hexdigest(), 16)
        (dev if h % 2 == 0 else test).append(l)
    return dev, test


def _apply_arms(pop_lemmas: List[str], pop: Dict[str, object], space: ConceptSpace, params: dict,
                rng: np.random.Generator) -> Dict[str, Dict[str, dict]]:
    """Return {arm_name: {lemma: result}} for all arms on the given population + params."""
    out: Dict[str, Dict[str, dict]] = {a: {} for a in
                                       ("RESTUDY", "RETRIEVE", "RETRIEVE_ANCHOR", "EXPOSURE",
                                        "TWIN_SHUF", "TWIN_RAND")}
    for l in pop_lemmas:
        tr = pop[l].traces
        out["RESTUDY"][l] = arm_restudy(l, tr, space, params)
        out["RETRIEVE"][l] = arm_retrieve(l, tr, space, params)
        out["RETRIEVE_ANCHOR"][l] = arm_retrieve_anchor(l, tr, space, params)
        out["EXPOSURE"][l] = arm_exposure(l, tr, space, params)
        out["TWIN_SHUF"][l] = arm_twin_shuffle(l, tr, space, params, rng)
        out["TWIN_RAND"][l] = arm_twin_random(l, tr, space, params, rng)
    return out


def _annotate_correct(pop_lemmas: List[str], arm_res: Dict[str, dict]) -> None:
    grounded = [l for l in pop_lemmas if arm_res[l]["grounded"]]
    rel = _wn_related([(l, arm_res[l]["meaning"]) for l in grounded])
    for l in pop_lemmas:
        arm_res[l]["_correct"] = bool(arm_res[l]["grounded"] and
                                      rel.get((l, arm_res[l]["meaning"]), False))


def run(budget: int, run_mode: str, seed: int) -> dict:
    t0 = time.time()
    cap = capture(budget, run_mode, seed)
    state = cap["state"]
    space = state.space
    pop = cap["consol_fail"]
    pop_lemmas = sorted(pop)
    rng = np.random.default_rng(1000 + seed)

    diag = retrieval_signal_diagnostic(pop, rng)

    # DEV/TEST split; sweep params on DEV by grounded_correct_rate; report on TEST.
    dev, test = _dev_test_split(pop_lemmas, seed)
    best_params, best_dev = dict(DEFAULT_PARAMS), -1.0
    sweep_log = []
    for ht in SWEEP["hit_thresh"]:
        for eh in SWEEP["eps_hit"]:
            for gt in SWEEP["ground_thresh"]:
                pr = dict(DEFAULT_PARAMS); pr.update(hit_thresh=ht, eps_hit=eh, ground_thresh=gt)
                res = {l: arm_retrieve(l, pop[l].traces, space, pr) for l in dev}
                _annotate_correct(dev, res)
                rate = sum(1 for l in dev if res[l]["_correct"]) / max(1, len(dev))
                sweep_log.append({"hit_thresh": ht, "eps_hit": eh, "ground_thresh": gt,
                                  "dev_grounded_correct_rate": round(rate, 6)})
                if rate > best_dev:
                    best_dev, best_params = rate, pr

    def _full(pop_l: List[str], params: dict) -> dict:
        arms = _apply_arms(pop_l, pop, space, params, np.random.default_rng(7 + seed))
        for a in arms:
            _annotate_correct(pop_l, arms[a])
        scores = {a: score_arm(pop_l, arms[a]) for a in arms}
        brng = np.random.default_rng(99 + seed)
        cmp = {}
        for opp in ("RESTUDY", "EXPOSURE", "TWIN_SHUF", "TWIN_RAND"):
            cmp[f"RETRIEVE_vs_{opp}"] = paired_bootstrap(
                scores["RETRIEVE"]["_correct_ind"], scores[opp]["_correct_ind"], pop_l, brng)
        curves = {a: depth_curve(pop_l, arms[a], pop) for a in ("RESTUDY", "RETRIEVE")}
        clean = {a: {k: v for k, v in scores[a].items() if not k.startswith("_")} for a in scores}
        return {"scores": clean, "comparisons": cmp, "depth_curve": curves}

    test_out = _full(test, best_params)
    full_out = _full(pop_lemmas, best_params)          # whole population, DEV-tuned params
    fixed_out = _full(pop_lemmas, DEFAULT_PARAMS)      # no-tuning transparency

    # DECISIVE, RATE-INDEPENDENT tests (the real fork -- selection signal + m quality)
    sel = decisive_selection_auc(pop_lemmas, pop, space, best_params, np.random.default_rng(55 + seed))
    mq = m_quality_matched(pop_lemmas, pop, space, best_params)
    charac = characterize_population(pop_lemmas, pop, space, cap["encounter"])

    headline = (
        "CONSOLIDATION_FAIL n=%d. DECISIVE: selection-AUC for picking a WordNet-CORRECT grounding -- "
        "retrieve_s=%s, retrieve_anchor_s=%s, exposure_s=%s, self_signal=%s vs random=%s (>0.5 means "
        "the retrieval signal helps). precision at matched recall is FLAT if these ~= random. "
        "m-quality: retrieve-hits-only precision=%s vs full-bundle restudy precision=%s. "
        "Recall aside: RETRIEVE grounds %.3f vs RESTUDY %.3f but LOSES to exposure-count %.3f / "
        "random twin %.3f (threshold-relaxation, not a testing effect)." % (
            len(pop_lemmas), sel.get("auc_correct__retrieve_s"), sel.get("auc_correct__retrieve_anchor_s"),
            sel.get("auc_correct__exposure_s"), sel.get("auc_correct__self_signal"),
            sel.get("auc_correct__random"),
            mq["retrieve_hits_only_m"]["precision"], mq["full_bundle_restudy_m"]["precision"],
            full_out["scores"]["RETRIEVE"]["grounded_correct_rate"],
            full_out["scores"]["RESTUDY"]["grounded_correct_rate"],
            full_out["scores"]["EXPOSURE"]["grounded_correct_rate"],
            full_out["scores"]["TWIN_RAND"]["grounded_correct_rate"]))

    return {
        "population_characterization": charac,
        "decisive_selection_auc": sel,
        "decisive_m_quality": mq,
        "seed": seed, "run_mode": run_mode, "n_read": cap["n_read"],
        "capture_elapsed_s": cap["elapsed_s"], "elapsed_s": round(time.time() - t0, 2),
        "n_incumbent_grounded": len(cap["grounded"]),
        "n_consol_fail": len(pop_lemmas),
        "n_all_ge4_ungrounded": len(cap["all_ge4_ungrounded"]),
        "retrieval_signal_diagnostic": diag,
        "best_params_dev_tuned": best_params, "best_dev_grounded_correct_rate": round(best_dev, 6),
        "dev_test_sizes": {"dev": len(dev), "test": len(test)},
        "TEST_heldout": test_out,
        "FULL_pop_dev_tuned": full_out,
        "FIXED_pop_no_tuning": fixed_out,
        "sweep_log": sweep_log,
        "headline": headline,
    }


# ===================== SELF-TEST + MAIN =========================================================

_WN_CLOSURE_CACHE: Dict[object, frozenset] = {}


def _syn_closure(syn):
    c = _WN_CLOSURE_CACHE.get(syn)
    if c is None:
        c = frozenset(syn.closure(lambda x: x.hypernyms())) | {syn}
        _WN_CLOSURE_CACHE[syn] = c
    return c


def _correct_anchor_set(word: str, anchor_syns: Dict[str, list], wn) -> set:
    """Anchors WordNet-related to `word` (same criterion as _wn_related: subsumption or wup>=0.5)."""
    ws = wn.synsets(word)[:6]
    if not ws:
        return set()
    wclos = set()
    for a in ws:
        wclos |= _syn_closure(a)
    out = set()
    for anc, asyn in anchor_syns.items():
        if anc == word:
            continue
        hit = False
        for b in asyn:
            if b in wclos:
                hit = True; break
            if _syn_closure(b) & set(ws):
                hit = True; break
        if not hit:
            for b in asyn[:3]:
                for a in ws[:3]:
                    try:
                        if (a.wup_similarity(b) or 0) >= 0.5:
                            hit = True; break
                    except Exception:
                        pass
                if hit:
                    break
        if hit:
            out.add(anc)
    return out


def _rank_of_best_correct(word_vec: np.ndarray, anchor_names: List[str], anchor_mat: np.ndarray,
                          correct: set, self_name: str) -> Tuple[Optional[int], bool]:
    """Rank (1=best) of the highest-scoring WordNet-correct anchor under this encoder, and whether
    the argmax anchor is itself correct. anchor_mat rows L2-normalized, aligned to anchor_names."""
    q = word_vec / (np.linalg.norm(word_vec) + 1e-12)
    sims = anchor_mat @ q
    order = np.argsort(-sims)
    nearest_correct = False
    best_rank = None
    for rank, idx in enumerate(order, start=1):
        a = anchor_names[idx]
        if a == self_name:
            continue
        if rank == 1 or (best_rank is None and a == anchor_names[order[0]]):
            pass
        if a in correct:
            best_rank = rank
            break
    # nearest (argmax excluding self)
    for idx in order:
        if anchor_names[idx] != self_name:
            nearest_correct = anchor_names[idx] in correct
            break
    return best_rank, nearest_correct


def encoder_diagnostic(budget: int, run_mode: str, seed: int, do_structural: bool = True) -> dict:
    """DIG INTO THE CONTEXT ENCODER: for words where a WordNet-correct anchor EXISTS (the 78%
    representation-recoverable slice), WHY does the encoder miss it? Decompose the encoder's failure:
      - RANK of the best correct anchor under the incumbent hashed bag-of-words (near-miss vs far).
      - HEAD-TO-HEAD encoders on nearest-correct rate + correct-anchor rank, isolating each lever:
          hashed_bow_signed  (incumbent d=256, sign) ............. capacity(hash) + quantisation
          hashed_bow_graded  (incumbent d=256, graded) ........... quantisation lever
          sep_raw            (full-D separable counts) ........... removes the d=256 hash collision
          sep_ppmi           (full-D PPMI) ...................... + frequency weighting
          phi                (PPMI+SVD, k=100) .................. + dimensionality smoothing (ATL)
          structural         (dependency-relation features) ..... + SYNTAX (a second parsed read)
      If a correct anchor is FAR in EVERY encoder, distributional similarity and WordNet-relatedness
      diverge -> the READOUT/criterion is the issue, not the encoder. If a lever moves it up, that
      lever is the fix."""
    import scipy.sparse as sp
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a)
                     and space.bundle(a) is not None and counts.get(a))
    anchor_syns = {a: wn.synsets(a)[:6] for a in anchors}
    anchor_syns = {a: s for a, s in anchor_syns.items() if s}
    anchors = [a for a in anchors if a in anchor_syns]
    # representation-recoverable population: correct anchor exists AND has co-occurrence counts
    correct = {}
    recov = []
    for l in sorted(pop):
        if not counts.get(l):
            continue
        cs = _correct_anchor_set(l, anchor_syns, wn)
        if cs:
            correct[l] = cs
            recov.append(l)
    if len(recov) < 10 or len(anchors) < SVD_K + 5:
        return {"error": "insufficient recoverable population / anchors", "n_recov": len(recov),
                "n_anchors": len(anchors)}

    # ---- separable-count encoders (full-D, no hash collision) ----
    embed = sorted(set(anchors) | set(recov))
    vocab_words = sorted({c for w in embed for c in counts[w]})
    vocab = {w: i for i, w in enumerate(vocab_words)}
    M = _count_matrix(embed, counts, vocab)          # [n_embed, n_vocab] raw counts
    row = {w: i for i, w in enumerate(embed)}
    Mden = M.toarray()
    # sep_raw
    raw_mat = l2n(Mden.astype(np.float64))
    # sep_ppmi (no SVD)
    Mc = M.tocoo(); rsum = np.asarray(M.sum(1)).ravel(); csum = np.asarray(M.sum(0)).ravel()
    tot = float(M.sum()); rsum[rsum < 1e-12] = 1; csum[csum < 1e-12] = 1
    pmi = np.log(Mc.data / (rsum[Mc.row] * csum[Mc.col] / tot))
    P = sp.csr_matrix((np.maximum(pmi, 0.0), (Mc.row, Mc.col)), shape=M.shape)
    ppmi_mat = l2n(P.toarray().astype(np.float64))
    # phi (PPMI+SVD)
    phi = ppmi_svd(M, svd_k=SVD_K)

    def _eval(name, matrix, rowmap):
        anc_mat = np.stack([matrix[rowmap[a]] for a in anchors], axis=0)
        ranks, nearest = [], 0
        for w in recov:
            if w not in rowmap:
                continue
            br, nc = _rank_of_best_correct(matrix[rowmap[w]], anchors, anc_mat, correct[w], w)
            if br is not None:
                ranks.append(br)
            nearest += int(nc)
        n = sum(1 for w in recov if w in rowmap)
        ranks_arr = np.array(ranks) if ranks else np.array([len(anchors)])
        return {"encoder": name, "n": n, "nearest_correct_rate": round(nearest / n, 4) if n else None,
                "median_rank_best_correct": int(np.median(ranks_arr)),
                "frac_correct_in_top10": round(float(np.mean(ranks_arr <= 10)), 4),
                "frac_correct_in_top1": round(float(np.mean(ranks_arr <= 1)), 4)}

    results = [_eval("sep_raw", raw_mat, row), _eval("sep_ppmi", ppmi_mat, row),
               _eval("phi_ppmi_svd", phi, row)]

    # ---- READ-OUT re-ranking on phi (the wall is the READ-OUT: does a PARADIGMATIC re-ranker pick
    # ---- the correct anchor over the topical-nearest?). Uses the SAME valid `correct` sets (wup). --
    recov_in = [w for w in recov if w in row]
    phi_anc = l2n(np.stack([phi[row[a]] for a in anchors], axis=0))
    Wq = l2n(np.stack([phi[row[w]] for w in recov_in], axis=0))
    S = Wq @ phi_anc.T                                   # [n_recov, n_anchor] cosine
    bg = S.mean(axis=0)                                  # per-anchor genericity (topic/frequency backbone)

    def _ro(name, score_mat, abstain=None):
        n = grounded = corr = t3 = t10 = 0
        for i, w in enumerate(recov_in):
            order = [j for j in np.argsort(-score_mat[i]) if anchors[j] != w]
            n += 1
            if abstain is not None:
                raw = S[i][order[:2]]                    # abstain on the RAW cosine margin
                if len(raw) >= 2 and (raw[0] - raw[1]) < abstain:
                    continue
            grounded += 1
            cset = correct[w]
            if anchors[order[0]] in cset:
                corr += 1
            if any(anchors[j] in cset for j in order[:3]):
                t3 += 1
            if any(anchors[j] in cset for j in order[:10]):
                t10 += 1
        return {"readout": name, "n": n, "n_grounded": grounded,
                "rank1_correct_over_pop": round(corr / n, 4) if n else None,
                "precision_of_grounded": round(corr / grounded, 4) if grounded else None,
                "top3_correct": round(t3 / n, 4) if n else None,
                "top10_correct": round(t10 / n, 4) if n else None}

    readout_reranking = [_ro("NEAREST", S), _ro("BG_SUBTRACT", S - bg[None, :]),
                         _ro("ABSTAIN_m0.02", S, abstain=0.02), _ro("ABSTAIN_m0.05", S, abstain=0.05)]
    # DISTILLED substitutability axis (the landed 0.865 paradigmatic read-out) as a LEARNED re-ranker
    try:
        from hdlab.distributional_meaning_channel import build as dm_build
        ch = dm_build(counts)
        h1 = h3 = h10 = nd = 0
        for w in recov_in[:150]:
            sc = ch.substitutability_batch([(w, a) for a in anchors])
            rk = [anchors[i] for i in sorted(range(len(anchors)),
                  key=lambda i: -(sc[i] if sc[i] is not None else -1e9)) if anchors[i] != w]
            nd += 1; cs = correct[w]
            if rk and rk[0] in cs:
                h1 += 1
            if any(a in cs for a in rk[:3]):
                h3 += 1
            if any(a in cs for a in rk[:10]):
                h10 += 1
        readout_reranking.append({"readout": "DISTILLED_capped150", "n": nd,
                                  "rank1_correct_over_pop": round(h1 / nd, 4) if nd else None,
                                  "top3_correct": round(h3 / nd, 4) if nd else None,
                                  "top10_correct": round(h10 / nd, 4) if nd else None})
    except Exception as e:
        readout_reranking.append({"readout": "DISTILLED", "error": str(e)[:160]})

    # ---- incumbent hashed bag-of-words (d=256) signed vs graded, from the SAME space ----
    hb_anchor_signed = np.stack([np.sign(space.bundle(a)) for a in anchors], axis=0)
    hb_anchor_graded = np.stack([space.bundle(a) for a in anchors], axis=0)
    for nm, amat, qfn in (("hashed_bow_signed", hb_anchor_signed, lambda v: np.sign(v)),
                          ("hashed_bow_graded", hb_anchor_graded, lambda v: v)):
        amat_n = l2n(amat.astype(np.float64))
        ranks, nearest, n = [], 0, 0
        for w in recov:
            raw = np.sum([t.context_vec for t in pop[w].traces], axis=0)
            br, nc = _rank_of_best_correct(qfn(raw), anchors, amat_n, correct[w], w)
            n += 1
            if br is not None:
                ranks.append(br)
            nearest += int(nc)
        ra = np.array(ranks) if ranks else np.array([len(anchors)])
        results.append({"encoder": nm, "n": n, "nearest_correct_rate": round(nearest / n, 4),
                        "median_rank_best_correct": int(np.median(ra)),
                        "frac_correct_in_top10": round(float(np.mean(ra <= 10)), 4),
                        "frac_correct_in_top1": round(float(np.mean(ra <= 1)), 4)})

    # ---- structural (syntax) encoder: a SEPARATE parsed read ----
    structural = None
    if do_structural:
        try:
            from hdlab.reading_grounding_loop import StructuralEncoder
            enc = StructuralEncoder(REPO_ROOT)
            scap = capture(budget, run_mode, seed, encoder=enc)
            sspace = scap["state"].space
            spop = scap["consol_fail"]
            sanchors = sorted(a for a in sspace.anchors()
                              if a in scap["seed_words"] and is_eligible_meaning(a)
                              and sspace.bundle(a) is not None and a in anchor_syns)
            srecov = [w for w in spop if w in correct]     # reuse the WordNet correct sets
            if len(srecov) >= 10 and len(sanchors) >= 10:
                samat = l2n(np.stack([sspace.bundle(a) for a in sanchors], axis=0).astype(np.float64))
                ranks, nearest, n = [], 0, 0
                for w in srecov:
                    cset = correct[w] & set(sanchors)
                    if not cset:
                        continue
                    raw = np.sum([t.context_vec for t in spop[w].traces], axis=0)
                    br, nc = _rank_of_best_correct(raw, sanchors, samat, cset, w)
                    n += 1
                    if br is not None:
                        ranks.append(br)
                    nearest += int(nc)
                ra = np.array(ranks) if ranks else np.array([len(sanchors)])
                structural = {"encoder": "structural_syntax", "n": n, "n_anchors": len(sanchors),
                              "nearest_correct_rate": round(nearest / n, 4) if n else None,
                              "median_rank_best_correct": int(np.median(ra)),
                              "frac_correct_in_top10": round(float(np.mean(ra <= 10)), 4),
                              "frac_correct_in_top1": round(float(np.mean(ra <= 1)), 4),
                              "encoder_stats": enc.stats()}
            else:
                structural = {"error": "insufficient structural population", "n_recov": len(srecov),
                              "n_anchors": len(sanchors)}
        except Exception as e:
            structural = {"error": str(e)[:200]}

    return {"budget": budget, "seed": seed, "n_consol_fail": len(pop),
            "n_representation_recoverable": len(recov), "n_eligible_anchors": len(anchors),
            "n_vocab": len(vocab_words),
            "encoders": results, "structural": structural,
            "readout_reranking_on_phi": readout_reranking,
            "reading": ("median_rank_best_correct near 1-10 => near-miss (weighting/quantisation/capacity "
                        "fixes it); far (>>50) in EVERY encoder => distributional similarity != WordNet "
                        "relatedness, the READOUT/criterion is the wall, not the encoder."),
            "capture_elapsed_s": cap["elapsed_s"]}


def grounded_reranker_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """THE POSITIVE DEMONSTRATION (turns elimination into proof). Every DISTRIBUTIONAL read-out fails
    to SELECT the correct anchor from the retrieved top-K (~0.21-0.24 vs top-10 ceiling ~0.87). The
    brain-foundational claim is that SENSE discrimination needs GROUNDED (sensorimotor+affective)
    features, not co-occurrence (ATL hub-and-spoke; Lambon Ralph/Patterson). Test it directly: re-rank
    the same top-K by GROUNDED-HUB similarity (hdlab.distributional_meaning_channel.build_grounded_hub
    -- 11 Lancaster sensorimotor + 3 Warriner affect dims, the project's grounded teacher) and see if
    it selects the correct anchor where distributional cosine cannot.
      grounded_rank1 >> distributional 0.21 => DEMONSTRATED: grounded features are the lever; the fix is
        're-rank the retrieved top-K by grounded-hub similarity' (concrete, actionable).
      grounded_rank1 ~= 0.21 OR grounded coverage thin on these abstract words => nuanced: purely
        sensorimotor grounding does not carry these senses (abstract concepts need affective/linguistic
        grounding -- Barsalou/Vigliocco), which sharpens WHICH grounding is the lever."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n, build_grounded_hub, hub_sim
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    try:
        hub, cov = build_grounded_hub(embed)
    except Exception as e:
        return {"error": "grounded hub build failed: " + str(e)[:150]}
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))

    n_anchor_cov = int(sum(cov[ei[a]] for a in anchors))
    n = grd_hit = dist_hit = 0
    n_word_cov = 0
    for w in pop_words:
        if not cov[ei[w]]:
            continue
        n_word_cov += 1
        q = phi[ei[w]] / (np.linalg.norm(phi[ei[w]]) + 1e-12)
        order = [j for j in np.argsort(-(A @ q)) if anchors[j] != w][:topk]   # top-K by DISTRIBUTIONAL
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = [1 if _rel(w_ss, w_clos, anchors[j]) else 0 for j in order]
        if sum(labs) == 0:
            continue                       # no correct anchor in the retrieved top-K -> not scoreable
        n += 1
        if labs[0] == 1:                   # distributional nearest (rank-1 by cosine)
            dist_hit += 1
        # GROUNDED re-rank of the SAME top-K (covered candidates only; uncovered -> -inf)
        iw = np.array([ei[w]] * len(order)); ja = np.array([ei[anchors[j]] for j in order])
        gs = hub_sim(hub, iw, ja)
        gs = np.where(np.array([cov[ei[anchors[j]]] for j in order]), gs, -1e9)
        if labs[int(np.argmax(gs))] == 1:
            grd_hit += 1
    return {"budget": budget, "seed": seed, "topk": topk, "n_anchors": len(anchors),
            "grounded_coverage_anchors": round(n_anchor_cov / len(anchors), 4),
            "grounded_coverage_words": round(n_word_cov / max(1, len(pop_words)), 4),
            "n_scoreable_covered_words_with_correct_in_topK": n,
            "grounded_rerank_rank1_correct": round(grd_hit / n, 4) if n else None,
            "distributional_nearest_rank1_correct": round(dist_hit / n, 4) if n else None,
            "grounded_lift_over_distributional": round((grd_hit - dist_hit) / n, 4) if n else None,
            "reading": ("grounded_lift >> 0 => grounded (ATL hub-and-spoke) features SELECT the correct "
                        "sense where distribution cannot => the demonstrated fix. lift ~0 or low coverage "
                        "=> purely sensorimotor grounding does not carry these (abstract) senses."),
            "capture_elapsed_s": cap["elapsed_s"]}


# ================================================================================================
# THE FULL-LIFT MECHANISM (brain-foundational; unsupervised; THIS is the wire, not a diagnostic).
# Research-pinned in RESEARCH_sense_selection_mechanism.md (hdi_research drill 2026-09-01):
#   * ATL hub selects a sense by RELIABILITY-WEIGHTED cue combination (Ernst & Banks 2002 /
#     noisy-channel comprehension; == product-of-experts for Gaussian cues) of the distributional
#     (co-occurrence) spoke and the grounded (sensorimotor+affect / experiential) spoke, then argmax
#     (= the settled attractor basin, Rodd 2004). Equal-weight z-fusion is LESS brain-faithful
#     (discards the reliability the brain demonstrably uses) -- kept only as a contrast.
#   * A flat cue is auto-down-weighted; for an ABSTRACT word the grounded cue is flat -> fusion
#     leans on the distributional spoke (Andrews 2009 distributional bootstrapping) -- Q3 for free.
#   * Two-stage fast distributional shortlist -> slow grounded re-rank is LASS-pinned (Barsalou 2008).
# ================================================================================================
_BINDER65_CACHE = None


def _load_binder65_table() -> Dict[str, np.ndarray]:
    """Predicted Binder-2016 65-dim EXPERIENTIAL ratings for ~25k words -- the computational
    EXTENSION of Binder norms to a large vocabulary built OFFLINE in exp_selpref_unseen_lowdata_v1
    (held-out rho 0.69 vs measured Binder). Binder-65 adds Social/Cognition/Emotion/Space/Time/
    Causal axes the 14-dim sensorimotor+affect hub cannot represent -- the axes abstract senses
    differ on (Binder 2016; Anderson 2017). OUR-INVENTION-FOR-COVERAGE: imputed, NOT measured norms
    -> adopt only on MEASURED lift (the research's mandatory ablation). Returns {} on any failure."""
    global _BINDER65_CACHE
    if _BINDER65_CACHE is not None:
        return _BINDER65_CACHE
    base = os.path.join(REPO_ROOT, "data", "exp_selpref_unseen_lowdata_v1", "_ckpt_full")
    tab: Dict[str, np.ndarray] = {}
    try:
        mat = np.load(os.path.join(base, "artifact_BINDER65_PREDICT.npz"))["mat"]
        words = None
        with open(os.path.join(base, "units.jsonl"), encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                if str(d.get("unit_key", "")).startswith("BINDER65_PREDICT"):
                    words = d["result"]["words"]
                    break
        if words is not None and mat.shape[0] == len(words):
            tab = {w: mat[i] for i, w in enumerate(words)}
    except Exception:
        tab = {}
    _BINDER65_CACHE = tab
    return tab


def _build_binder65_hub(words):
    """z-scored + L2-normalized predicted-Binder-65 experiential hub over `words`, plus a coverage
    mask -- same (hub[n,65], cov[n]) shape as build_grounded_hub so it plugs straight into hub_sim.
    Returns (None, None) if the predictor artifact is unavailable."""
    from hdlab.distributional_meaning_channel import l2n, _zblock
    tab = _load_binder65_table()
    if not tab:
        return None, None
    raw, cov = _zblock(tab, 65, words)
    return l2n(raw), cov


_BINDER65_MEASURED_CACHE = None


def _load_binder65_measured_table() -> Dict[str, np.ndarray]:
    """The MEASURED Binder-2016 65-dim experiential norms (535 words, human ratings) -- the anti-
    imputation-artifact control for the predicted table. Columns are the 65 experiential dims
    (Vision..Arousal); metadata columns (WC/N/Mean R/LEN/FREQ/...) are excluded. Returns {} on
    failure."""
    global _BINDER65_MEASURED_CACHE
    if _BINDER65_MEASURED_CACHE is not None:
        return _BINDER65_MEASURED_CACHE
    import csv as _csv
    import io as _io
    path = os.path.join(REPO_ROOT, "data", "corpora", "binder", "binder2016_ratings.csv")
    tab: Dict[str, np.ndarray] = {}
    try:
        with _io.open(path, encoding="utf-8", errors="replace") as fh:
            rdr = _csv.reader(fh)
            hdr = next(rdr)
            cols = list(range(hdr.index("Mean R") + 1, hdr.index("Mean R") + 1 + 65))  # 65 experiential dims
            for row in rdr:
                w = row[hdr.index("Word")].strip().lower()
                try:
                    tab[w] = np.array([float(row[c]) for c in cols], float)
                except (ValueError, IndexError):
                    pass
    except Exception:
        tab = {}
    _BINDER65_MEASURED_CACHE = tab
    return tab


def _measured_binder_hub(words):
    """z-scored + L2-normalized MEASURED-Binder-65 hub over `words` + coverage mask (True only for
    the ~535 human-rated words). Returns (None, None) if the CSV is unavailable."""
    from hdlab.distributional_meaning_channel import l2n, _zblock
    tab = _load_binder65_measured_table()
    if not tab:
        return None, None
    raw, cov = _zblock(tab, 65, words)
    return l2n(raw), cov


# derivational suffixes stripped to reach a grounded stem (longest-first). MORPHOLOGY as a word-
# INTERNAL grounding spoke: readers ground a derived word by decomposing it (brightness<-bright,
# national<-nation, justice<-just). PINNED (accumulation drill Q4, highest-value miss): morphology
# is extracted without instruction and is the route for the abstract/derived tail sensorimotor
# norms miss. Single-exposure, cheap, brain-faithful.
_DERIV_SUFFIXES = ["fulness", "iness", "ation", "ption", "ically", "ness", "tion", "sion",
                   "ment", "ance", "ence", "ical", "ious", "eous", "ous", "ive", "ity", "ially",
                   "ally", "able", "ible", "hood", "ship", "less", "ful", "dom", "ery", "ism",
                   "ist", "ize", "ise", "al", "ic", "ly", "er", "or", "age"]


def _morph_stem_candidates(word: str) -> List[str]:
    """Ordered candidate grounded stems for a derived word: WordNet derivationally-related forms
    (the pinned morphological link, e.g. justice.n <-> just.a), then WordNet morphy lemmas, then a
    derivational suffix stripper with orthographic repair (happiness->happi->happy, creative->
    creat->create). Deduplicated, self excluded."""
    from nltk.corpus import wordnet as wn
    out: List[str] = []
    seen = {word}
    try:
        for s in wn.synsets(word)[:6]:
            for l in s.lemmas():
                if l.name().lower() == word:
                    for d in l.derivationally_related_forms():
                        dn = d.name().lower()
                        if dn not in seen:
                            seen.add(dn); out.append(dn)
        for pos in ("n", "v", "a", "r"):
            m = wn.morphy(word, pos)
            if m and m.lower() not in seen:
                seen.add(m.lower()); out.append(m.lower())
    except Exception:
        pass
    for suf in _DERIV_SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            stem = word[:-len(suf)]
            for cand in (stem, stem + "e", (stem[:-1] + "y" if stem.endswith("i") else None)):
                if cand and cand not in seen:
                    seen.add(cand); out.append(cand)
    return out


def _morph_lookup(word: str, covset) -> Optional[str]:
    """First grounded-covered morphological stem of `word`, or None. `covset` is any mapping/set of
    grounded-covered lemmas (a norm table)."""
    for c in _morph_stem_candidates(word):
        if c in covset:
            return c
    return None


def _build_binder65_hub_morph(words):
    """Binder-65 experiential hub EXTENDED to derived words by morphological backoff: a word not in
    the predicted-Binder table borrows its grounded-covered derivational stem's vector (brightness
    <-bright). Same (hub[n,65], cov[n]) shape; also returns (n_direct, n_morph) coverage counts.
    Returns (None, None, 0, 0) if the table is unavailable. OUR-INVENTION-FOR-COVERAGE: the stem's
    grounding is a PROXY for the derived word -- adopt on measured lift, especially on the tail."""
    from hdlab.distributional_meaning_channel import l2n, _zblock
    tab = _load_binder65_table()
    if not tab:
        return None, None, 0, 0
    ext: Dict[str, np.ndarray] = {}
    n_direct = n_morph = 0
    for w in words:
        wl = w.lower()
        if wl in tab:
            ext[wl] = tab[wl]; n_direct += 1
        else:
            stem = _morph_lookup(wl, tab)
            if stem is not None:
                ext[wl] = tab[stem]; n_morph += 1
    raw, cov = _zblock(ext, 65, words)
    return l2n(raw), cov, n_direct, n_morph


def _cand_z(s: np.ndarray) -> np.ndarray:
    s = np.asarray(s, float)
    return (s - s.mean()) / (s.std() + 1e-9)


def _cue_reliability(s: np.ndarray) -> float:
    """Peakiness of a cue's scores over the candidate set, in [0,1]: ~0 = flat/uninformative,
    ~1 = one candidate dominates. THE reliability-weighted (precision-weighted) cue-combination
    weight (Ernst & Banks 2002; noisy-channel comprehension): trust a cue that sharply separates the
    candidates, down-weight a flat one. LABEL-FREE -- uses only the cue's own score shape, never
    correctness. (softmax-max-probability, rescaled so a uniform distribution maps to 0.)"""
    s = np.asarray(s, float)
    K = len(s)
    if K < 2 or s.std() < 1e-12:
        return 0.0
    z = _cand_z(s)
    e = np.exp(z - z.max())
    p = e / e.sum()
    return float((p.max() - 1.0 / K) / (1.0 - 1.0 / K + 1e-12))


def grounded_fusion_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """THE BRAIN-FOUNDATIONAL FULL-LIFT MECHANISM (unsupervised; wireable). Selectors compared, all
    UNSUPERVISED (no gold ever touched), on the SAME scoreable population -- words whose retrieved
    distributional top-K contains a WordNet-correct anchor, so the within-set ceiling is 1.0:
      DIST      : argmax distributional cosine (the incumbent read-out; ~0.24).
      GRD14     : argmax 14-dim grounded-hub cosine (the demonstrated single-spoke re-rank; ~0.33).
      GRD65     : argmax predicted-Binder-65 experiential cosine (richer spoke alone).
      FUSE14    : reliability-weighted (dist, grd14) then argmax. THE core mechanism.
      FUSE65    : reliability-weighted (dist, grd65) then argmax.
      FUSE_BOTH : reliability-weighted (dist, grd14, grd65) then argmax. Full spoke set.
      EQUALZ14  : equal-weight z-fusion (dist, grd14) -- the LESS brain-faithful contrast the research
                  argues against; FUSE14 should be >= this.
      SHUF14    : FUSE14 with the grounded rows PERMUTED = info-free twin; MUST collapse to ~DIST.
    Reports paired-bootstrap CIs for the key lifts, and the ABSTRACT-slice (no sensorimotor coverage)
    breakdown that the research mandates before adopting Binder-65."""
    from hdlab.distributional_meaning_channel import (_count_matrix, ppmi_svd, SVD_K, l2n,
                                                      build_grounded_hub, hub_sim)
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):   # FULL WordNet criterion (subsumption OR wup>=0.5); top-K only
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    hub14, cov14 = build_grounded_hub(embed)
    hub65, cov65 = _build_binder65_hub(embed)
    have65 = hub65 is not None
    hub65m, cov65m = _measured_binder_hub(embed)     # MEASURED Binder-535 (anti-imputation-artifact)
    have65m = hub65m is not None
    hub65mo, cov65mo, n65_direct, n65_morph = _build_binder65_hub_morph(embed)  # + morphology backoff
    have65mo = hub65mo is not None
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    rng = np.random.default_rng(seed + 909)
    perm = rng.permutation(len(embed))
    hub14_shuf, cov14_shuf = hub14[perm], cov14[perm]
    perm65 = rng.permutation(len(embed))
    hub65_shuf, cov65_shuf = (hub65[perm65], cov65[perm65]) if have65 else (None, None)

    def _grd_scores(hubm, covm, wi, cand):
        """z-scored grounded cos over the candidates (uncovered candidates -> 0 = neutral), plus the
        cue reliability. Grounded ABSTAINS (returns zeros, 0.0) when the word is uncovered or <2
        candidates are covered -- so an abstract word contributes no grounded weight and fusion is
        pure distributional there."""
        if hubm is None or not covm[wi]:
            return np.zeros(len(cand)), 0.0
        covmask = np.array([bool(covm[j]) for j in cand])
        if covmask.sum() < 2:
            return np.zeros(len(cand)), 0.0
        raw = hub_sim(hubm, np.array([wi] * len(cand)), np.array(cand))
        z = np.zeros(len(cand))
        r = raw[covmask]
        z[covmask] = (r - r.mean()) / (r.std() + 1e-9)
        return z, _cue_reliability(r)

    keys = ["DIST", "GRD14", "GRD65", "GRD65_MORPH", "GRD_BOTH", "CASCADE", "CASCADE_MORPH",
            "FUSE14", "FUSE65", "FUSE_BOTH", "EQUALZ14", "SHUF14", "GRD65_SHUF"]
    per_word = {k: [] for k in keys}
    flags14 = []
    flags65mo = []
    # measured-Binder cross-check (anti-imputation-artifact): per-word correctness of DIST /
    # predicted-Binder / measured-Binder, collected ONLY on measured-Binder-covered words.
    mx = {"DIST": [], "GRD65_pred": [], "GRD65_meas": []}
    n = n_word_cov14 = n_word_cov65 = 0
    for w in pop_words:
        wi = ei[w]
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        cand = [ei[anchors[j]] for j in order]
        s_d = np.array([sims_all[j] for j in order])
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = np.array([1 if _rel(w_ss, w_clos, anchors[j]) else 0 for j in order])
        if labs.sum() == 0:
            continue                         # no correct anchor retrieved -> not scoreable
        n += 1
        if cov14[wi]: n_word_cov14 += 1
        if have65 and cov65[wi]: n_word_cov65 += 1
        flags14.append(bool(cov14[wi]))
        flags65mo.append(bool(have65mo and cov65mo[wi]))
        zd = _cand_z(s_d); rd = _cue_reliability(s_d)
        zg14, rg14 = _grd_scores(hub14, cov14, wi, cand)
        zg65, rg65 = (_grd_scores(hub65, cov65, wi, cand) if have65 else (np.zeros(len(cand)), 0.0))
        zg65mo, rg65mo = (_grd_scores(hub65mo, cov65mo, wi, cand) if have65mo else (np.zeros(len(cand)), 0.0))
        zg14s, rg14s = _grd_scores(hub14_shuf, cov14_shuf, wi, cand)
        zg65s, rg65s = (_grd_scores(hub65_shuf, cov65_shuf, wi, cand) if have65 else (np.zeros(len(cand)), 0.0))
        p_grd65 = int(np.argmax(zg65)) if rg65 > 0 else 0
        p_grd65mo = int(np.argmax(zg65mo)) if rg65mo > 0 else 0
        p_grd14 = int(np.argmax(zg14)) if rg14 > 0 else 0
        picks = {
            "DIST": 0,                       # order is sorted by s_d, so nearest == index 0
            "GRD14": p_grd14,
            "GRD65": p_grd65,                 # pure Binder-65 re-rank (dist-fallback where uncovered)
            "GRD65_MORPH": p_grd65mo,         # Binder-65 + morphology backoff (extends the tail)
            "GRD_BOTH": int(np.argmax(rg14 * zg14 + rg65 * zg65)) if (rg14 + rg65) > 0 else 0,  # grounded-only hub
            "CASCADE": p_grd65 if rg65 > 0 else (p_grd14 if rg14 > 0 else 0),  # WIRE: best grounded spoke->dist
            "CASCADE_MORPH": (p_grd65mo if rg65mo > 0 else (p_grd14 if rg14 > 0 else 0)),  # + morph tail
            "FUSE14": int(np.argmax(rd * zd + rg14 * zg14)),
            "FUSE65": int(np.argmax(rd * zd + rg65 * zg65)),
            "FUSE_BOTH": int(np.argmax(rd * zd + rg14 * zg14 + rg65 * zg65)),
            "EQUALZ14": int(np.argmax(zd + zg14)) if rg14 > 0 else 0,
            "SHUF14": int(np.argmax(rd * zd + rg14s * zg14s)),
            "GRD65_SHUF": int(np.argmax(zg65s)) if rg65s > 0 else 0,
        }
        for k, pk in picks.items():
            per_word[k].append(int(labs[pk] == 1))
        if have65m and cov65m[wi]:
            zg65m, rg65m = _grd_scores(hub65m, cov65m, wi, cand)
            if rg65m > 0:
                mx["DIST"].append(int(labs[0] == 1))
                mx["GRD65_pred"].append(int(labs[p_grd65] == 1))
                mx["GRD65_meas"].append(int(labs[int(np.argmax(zg65m))] == 1))

    if n == 0:
        return {"error": "no scoreable words", "n_anchors": len(anchors)}

    def _rate(k):
        return round(float(np.mean(per_word[k])), 4)

    def _lift_ci(a_key, b_key="DIST", nboot=N_BOOT):
        d = np.array(per_word[a_key]) - np.array(per_word[b_key])
        bs = np.random.default_rng(seed + 111)
        idx = bs.integers(0, len(d), size=(nboot, len(d)))
        means = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
        return {"lift": round(float(d.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    fa = np.array(flags14, bool)
    abstract = ~fa

    def _slice_rate(k, mask):
        if mask.sum() == 0:
            return None
        return round(float(np.array(per_word[k])[mask].mean()), 4)

    return {
        "budget": budget, "seed": seed, "topk": topk, "n_anchors": len(anchors),
        "n_scoreable_words_with_correct_in_topK": n,
        "grounded14_word_coverage": round(n_word_cov14 / n, 4),
        "binder65_word_coverage": round(n_word_cov65 / n, 4) if have65 else 0.0,
        "binder65_morph_word_coverage": round(float(np.mean(flags65mo)), 4) if have65mo else 0.0,
        "binder65_morph_backoff_counts_over_embed": {"direct": n65_direct, "via_morphology": n65_morph},
        "have_binder65": have65,
        "have_binder65_measured": have65m,
        "have_binder65_morph": have65mo,
        "rank1_correct": {k: _rate(k) for k in keys},
        "lift_over_DIST": {k: round(_rate(k) - _rate("DIST"), 4) for k in keys},
        "ci_GRD65_minus_DIST_HEADLINE": _lift_ci("GRD65"),
        "ci_CASCADE_minus_DIST_WIRE": _lift_ci("CASCADE"),
        "ci_CASCADE_MORPH_minus_DIST_WIRE_PLUS_MORPH": _lift_ci("CASCADE_MORPH"),
        "ci_GRD65_MORPH_minus_GRD65_morph_adds": _lift_ci("GRD65_MORPH", "GRD65"),
        "ci_GRD65_minus_GRD14_richer_spoke": _lift_ci("GRD65", "GRD14"),
        "ci_GRD65_SHUF_minus_DIST_MUST_INCLUDE_0": _lift_ci("GRD65_SHUF"),
        "ci_FUSE_BOTH_minus_DIST": _lift_ci("FUSE_BOTH"),
        "ci_SHUF14_minus_DIST_MUST_INCLUDE_0": _lift_ci("SHUF14"),
        "binder_measured_cross_check": {
            "n_measured_covered": len(mx["DIST"]),
            "DIST": round(float(np.mean(mx["DIST"])), 4) if mx["DIST"] else None,
            "GRD65_predicted": round(float(np.mean(mx["GRD65_pred"])), 4) if mx["GRD65_pred"] else None,
            "GRD65_measured": round(float(np.mean(mx["GRD65_meas"])), 4) if mx["GRD65_meas"] else None,
            "note": "on the human-rated-Binder slice: if MEASURED ~ PREDICTED > DIST, the predicted "
                    "table's lift is real experiential grounding, not an imputation artifact."},
        "abstract_slice_no_sensorimotor_coverage": {
            "n": int(abstract.sum()),
            "DIST": _slice_rate("DIST", abstract),
            "GRD65": _slice_rate("GRD65", abstract),
            "GRD65_MORPH": _slice_rate("GRD65_MORPH", abstract),
            "CASCADE_MORPH": _slice_rate("CASCADE_MORPH", abstract),
            "note": "the abstract (no-sensorimotor) tail. Adopt Binder-65 / morphology only if they "
                    "lift this slice over DIST. Morphology (GRD65_MORPH) is the pinned route for the "
                    "derived words here (accumulation drill Q4)."},
        "reading": ("HEADLINE: pure GROUNDED re-rank by the richest experiential spoke (GRD65 = "
                    "predicted-Binder-65, distributional-fallback where uncovered) SELECTS the correct "
                    "sense far above DIST (CI-separated) while its shuffle twin GRD65_SHUF ~= DIST. "
                    "Re-FUSING the distributional cue (FUSE*) HURTS vs grounded-alone -- the "
                    "distributional cue is confidently WRONG for sense (peaky about TOPIC not SENSE), "
                    "so the two-stage LASS cascade (dist SHORTLIST -> grounded SELECT) is the wire, "
                    "grounded-dominant. GRD65 > GRD14 => the richer experiential spoke earns its keep; "
                    "measured~predicted on the human-Binder slice => not an imputation artifact."),
        "capture_elapsed_s": cap["elapsed_s"]}


def grounded_supervised_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """CEILING YARDSTICK ONLY -- NOT a brain mechanism, NOT wired. This trains a logistic on WordNet-
    correctness labels (5-fold CV over held-out WORDS) and is therefore grade-by-what-you-ground-by;
    the brain has no WordNet teacher for sense selection. Its ONLY legitimate use (like the existing
    distributional supervised_reranker_probe) is to UPPER-BOUND how much sense-signal the GROUNDED
    features CONTAIN, against which the unsupervised brain-faithful fusion (grounded_fusion_probe) is
    judged. Features are RELATIONAL grounded (grounded-hub cos, per-dim grounded agreement, Binder-65
    cos) + weak distributional (cos, rank) -- no candidate-identity features (those would learn a
    population prior, not a w-specific selector). Includes an info-free shuffled-grounded control."""
    from hdlab.distributional_meaning_channel import (_count_matrix, ppmi_svd, SVD_K, l2n,
                                                      build_grounded_hub, hub_sim)
    from nltk.corpus import wordnet as wn
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception as e:
        return {"error": "sklearn unavailable: " + str(e)[:80]}
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    hub14, cov14 = build_grounded_hub(embed)
    hub65, cov65 = _build_binder65_hub(embed)
    have65 = hub65 is not None
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    hub14n = l2n(hub14)
    hub65n = l2n(hub65) if have65 else None

    def _feature_rows(hub14_use, hub65_use):
        """Per-word top-K candidate feature matrices + labels; RELATIONAL grounded features only
        (grounded-hub14 cos + per-dim agreement, grounded-Binder65 cos, + weak distributional cos/
        rank). hub14_use / hub65_use carry the (possibly shuffled) grounded rows so the info-free
        control shuffles BOTH grounded spokes together."""
        rows = {}
        for w in pop_words:
            wi = ei[w]
            q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
            sims_all = A @ q
            order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
            w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
            feats, labs = [], []
            wcov14 = bool(cov14[wi]); wcov65 = bool(have65 and cov65[wi] and hub65_use is not None)
            hv14 = hub14_use[wi]
            hv65 = hub65_use[wi] if wcov65 else None
            for rnk, j in enumerate(order):
                ai = ei[anchors[j]]
                dcos = float(sims_all[j])
                # grounded-hub cos + per-dim agreement (14) -- relational, 0 when either side uncovered
                if wcov14 and cov14[ai]:
                    hprod = hv14 * hub14_use[ai]                 # 14-dim elementwise agreement
                    hcos14 = float(hprod.sum())
                else:
                    hprod = np.zeros(14); hcos14 = 0.0
                if wcov65 and cov65[ai]:
                    hcos65 = float(np.dot(hv65, hub65_use[ai]))   # hub65_use rows are L2-normed
                else:
                    hcos65 = 0.0
                feats.append([dcos, float(rnk), hcos14, hcos65, *hprod.tolist()])
                labs.append(1 if _rel(w_ss, w_clos, anchors[j]) else 0)
            rows[w] = (np.array(feats, float), np.array(labs, int))
        return rows

    def _cv_rank1(rows):
        words = [w for w in pop_words if rows[w][1].sum() > 0]
        rng = np.random.default_rng(seed)
        rng.shuffle(words)
        folds = np.array_split(words, 5)
        sup = near = n = 0
        for f in range(5):
            test = set(folds[f]); train = [w for w in words if w not in test]
            Xtr = np.vstack([rows[w][0] for w in train]); ytr = np.concatenate([rows[w][1] for w in train])
            mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
            clf = LogisticRegression(max_iter=1000, class_weight="balanced")
            clf.fit((Xtr - mu) / sd, ytr)
            for w in folds[f]:
                X, y = rows[w]
                p = clf.predict_proba((X - mu) / sd)[:, 1]
                n += 1
                sup += int(y[int(np.argmax(p))] == 1)
                near += int(y[0] == 1)
        return (round(sup / n, 4) if n else None, round(near / n, 4) if n else None, n)

    real = _cv_rank1(_feature_rows(hub14n, hub65n))
    rngp = np.random.default_rng(seed + 909)
    pp = rngp.permutation(len(embed))           # ONE permutation shuffles BOTH grounded spokes
    shuf = _cv_rank1(_feature_rows(hub14n[pp], hub65n[pp] if have65 else None))
    return {
        "budget": budget, "seed": seed, "topk": topk, "have_binder65": have65,
        "CEILING_grounded_supervised_rank1": real[0],
        "nearest_rank1_same_pop": real[1],
        "extractable_ceiling_lift_over_nearest": round(real[0] - real[1], 4) if real[0] is not None else None,
        "info_free_shuffled_grounded_rank1": shuf[0],
        "shuffled_lift_over_nearest_MUST_BE_NEAR_0": round(shuf[0] - shuf[1], 4) if shuf[0] is not None else None,
        "n_words": real[2],
        "reading": ("This is the UPPER BOUND on extractable grounded sense-signal (trains on gold "
                    "labels; NOT a wire). The unsupervised fusion (grounded_fusion_probe) is the "
                    "brain-faithful mechanism; compare its lift against this ceiling. shuffled ~0 "
                    "confirms the ceiling comes from real grounding, not the supervised machinery."),
        "capture_elapsed_s": cap["elapsed_s"]}


def context_gated_probe(budget: int, run_mode: str, seed: int, topk: int = 20, ridge: float = 50.0) -> dict:
    """TOWARD THE CEILING (research-pinned, RESEARCH_toward_ceiling_sense_selection.md). The grounded
    cue so far is PER-WORD (one static norm vector = a sense-BLEND for a polysemous word). The brain
    builds an OCCURRENCE-SPECIFIC grounded representation -- context PRE-ACTIVATES the sense-
    appropriate experiential features (Barsalou situated conceptualization 2009; predictive-coding
    N400, Kuperberg 2025; controlled semantic cognition, Lambon Ralph 2017). Prototype exactly that:
    learn g: occurrence-context (the trace's d256 hashed context bag) -> Binder-65 experiential, via
    RIDGE trained on library words DISJOINT from the eval set (leak-free); then per OCCURRENCE set
    binder_ctx = g(context_vec) and SELECT the distributional-shortlist candidate whose STATIC
    grounded prototype best matches binder_ctx. THE ASYMMETRY: candidates static, TARGET context-
    specific -- stop matching to a blurry per-word average, match to what the context DEMANDS.
      CTXGATE > GRD65_static (CI-sep) AND CTXGATE_SHUF ~ chance AND reachability>0  => context-gating
        is the toward-ceiling lever (the wire upgrade).
      CTXGATE ~ GRD65_static => the d256 hashed occurrence context is too THIN to sharpen the sense
        -> a richer occurrence-context representation is the next lever, NOT a ceiling (reachability
        rules out a stuck-representation false null)."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    items = cap["state"].library.items
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    tab = _load_binder65_table()
    if not tab:
        return {"error": "predicted-Binder-65 table unavailable"}

    def _b65(lemma):
        v = tab.get(lemma.lower())
        if v is None:
            return None
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else None

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    anc_b65 = {a: _b65(a) for a in anchors}

    # ---- fit g: occurrence-context (d256) -> Binder-65, on library words DISJOINT from eval pop ----
    # Two g's: G_all (train on every disjoint word's per-word BLEND binder) and G_mono (train ONLY on
    # ~monosemous words <=2 WordNet senses, whose binder IS sense-specific). G_mono is the FAIR test:
    # it avoids the blend-target circularity (a g fit to per-word blends can only reconstruct the blend
    # noisily -> strictly below the clean static blend). If even G_mono cannot beat static, the wall is
    # intrinsic (the thin d256 occurrence context lacks sense-discriminative signal), not a weak g.
    pop_set = set(pop_words)
    Xa, Ya, Xm, Ym = [], [], [], []
    D = None
    for lem, it in items.items():
        if lem in pop_set or not it.traces:
            continue
        b = _b65(lem)
        if b is None:
            continue
        mono = len(wn.synsets(lem)) <= 2
        for t in it.traces:
            cv = getattr(t, "context_vec", None)
            if cv is None:
                continue
            cv = np.asarray(cv, float)
            if D is None:
                D = cv.shape[0]
            if cv.shape[0] != D or not np.any(cv):
                continue
            Xa.append(cv); Ya.append(b)
            if mono:
                Xm.append(cv); Ym.append(b)
    if len(Xa) < 200 or D is None:
        return {"error": "insufficient g-training occurrences", "n_train_occ": len(Xa)}
    Xa = np.stack(Xa); Ya = np.stack(Ya)
    G_all = np.linalg.solve(Xa.T @ Xa + ridge * np.eye(D), Xa.T @ Ya)
    G_mono = None
    if len(Xm) >= 200:
        Xm = np.stack(Xm); Ym = np.stack(Ym)
        G_mono = np.linalg.solve(Xm.T @ Xm + ridge * np.eye(D), Xm.T @ Ym)

    def _cb(cv, G):
        p = cv @ G
        n = np.linalg.norm(p)
        return p / n if n > 1e-9 else None

    # ---- PASS 1: collect per-word geometry + occurrence contexts (build the global context pool) ----
    rows = []          # (labs, cbmat, covered, dist_hit, grd_static_hit, cvs)
    global_cv = []
    reach = []
    for w in pop_words:
        wi = ei[w]
        bw = _b65(w)
        it = items.get(w)
        if bw is None or it is None or not it.traces:
            continue
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = np.array([1 if _rel(w_ss, w_clos, anchors[j]) else 0 for j in order])
        if labs.sum() == 0:
            continue
        cb = [anc_b65[anchors[j]] for j in order]
        covered = [k for k, v in enumerate(cb) if v is not None]
        if len(covered) < 2:
            continue
        cbmat = np.stack([cb[k] for k in covered])
        cvs = [np.asarray(t.context_vec, float) for t in it.traces
               if getattr(t, "context_vec", None) is not None and np.any(t.context_vec)]
        if not cvs:
            continue
        dist_hit = int(labs[0] == 1)
        grd_static_hit = int(labs[covered[int(np.argmax(cbmat @ bw))]] == 1)
        rows.append((labs, cbmat, covered, dist_hit, grd_static_hit, cvs))
        global_cv.extend(cvs)
        bl = [_cb(cv, G_all) for cv in cvs]; bl = [b for b in bl if b is not None]
        if len(bl) >= 2:
            BC = np.stack(bl); BCn = BC / (np.linalg.norm(BC, axis=1, keepdims=True) + 1e-12)
            iu = np.triu_indices(len(BCn), 1)
            reach.append(1.0 - float((BCn @ BCn.T)[iu].mean()))
    if not rows:
        return {"error": "no scoreable words"}
    global_cv = np.stack(global_cv)
    rng = np.random.default_rng(seed + 4242)

    # ---- PASS 2: per-occurrence selection. CTXGATE_SHUF draws a context from a DIFFERENT word (valid
    # info-free twin -- the within-word shuffle was a no-op since a word's occurrences share labels). --
    occ = {"DIST": [], "GRD65_static": [], "CTXGATE": [], "CTXGATE_MONO": [], "CTXGATE_XWORD_SHUF": []}
    word_ctx_pick_correct = []
    for (labs, cbmat, covered, dist_hit, grd_static_hit, cvs) in rows:
        ctx_picks = []
        for cv in cvs:
            occ["DIST"].append(dist_hit)
            occ["GRD65_static"].append(grd_static_hit)
            b_all = _cb(cv, G_all)
            if b_all is not None:
                p = covered[int(np.argmax(cbmat @ b_all))]
                occ["CTXGATE"].append(int(labs[p] == 1)); ctx_picks.append(p)
            if G_mono is not None:
                b_m = _cb(cv, G_mono)
                if b_m is not None:
                    occ["CTXGATE_MONO"].append(int(labs[covered[int(np.argmax(cbmat @ b_m))]] == 1))
            b_x = _cb(global_cv[rng.integers(0, len(global_cv))], G_all)   # cross-word context
            if b_x is not None:
                occ["CTXGATE_XWORD_SHUF"].append(int(labs[covered[int(np.argmax(cbmat @ b_x))]] == 1))
        if ctx_picks:
            word_ctx_pick_correct.append(int(labs[Counter(ctx_picks).most_common(1)[0][0]] == 1))

    def _m(k):
        return round(float(np.mean(occ[k])), 4) if occ[k] else None

    def _ci(a_key, b_key, nboot=N_BOOT):
        a = np.array(occ[a_key]); b = np.array(occ[b_key])
        m = min(len(a), len(b)); a, b = a[:m], b[:m]; d = a - b
        bs = np.random.default_rng(seed + 77)
        idx = bs.integers(0, len(d), size=(nboot, len(d)))
        mns = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(mns, 2.5)), float(np.percentile(mns, 97.5))
        return {"lift": round(float(d.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    return {
        "budget": budget, "seed": seed, "topk": topk, "ridge": ridge,
        "n_words_scored": len(rows), "n_occurrences_scored": len(occ["CTXGATE"]),
        "n_g_training_occ_all": int(Xa.shape[0]), "n_g_training_occ_mono": int(len(Ym)) if G_mono is not None else 0,
        "context_dim": int(D),
        "reachability_within_word_binder_ctx_distance": round(float(np.mean(reach)), 4) if reach else None,
        "per_occurrence_rank1_correct": {k: _m(k) for k in occ},
        "per_word_CTXGATE_plurality_correct": round(float(np.mean(word_ctx_pick_correct)), 4) if word_ctx_pick_correct else None,
        "ci_CTXGATE_minus_GRD65static": _ci("CTXGATE", "GRD65_static"),
        "ci_CTXGATE_MONO_minus_GRD65static_FAIR_TEST": _ci("CTXGATE_MONO", "GRD65_static") if G_mono is not None else None,
        "ci_CTXGATE_minus_XWORDSHUF_signal_test": _ci("CTXGATE", "CTXGATE_XWORD_SHUF"),
        "reading": ("INTRINSIC WALL TEST. If CTXGATE_MONO (g trained on monosemous single-sense binders, "
                    "avoiding the blend-target circularity) still does NOT beat GRD65_static, AND CTXGATE "
                    "~ CTXGATE_XWORD_SHUF (real occurrence context no better than a random other word's "
                    "context), then the thin d256 occurrence context lacks sense-discriminative signal -- "
                    "the wall is intrinsic to the occurrence-context REPRESENTATION, and sharpening senses "
                    "needs per-sense grounding (sense-splitting), not context-gating over this signal."),
        "capture_elapsed_s": cap["elapsed_s"]}


def situation_grounding_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """CROSS-THE-WALL TEST for context-gating. context_gated_probe proved the substrate's stored
    occurrence context (d256 HASHED bag) carries no sense signal (CTXGATE ~ random-other-word). This
    probe rebuilds context-gating over the ACTUAL context WORDS (rich, un-hashed): ground each
    occurrence PARAMETER-FREE by the mean predicted-Binder-65 of its context content-words (Barsalou
    situated conceptualization: the occurrence's meaning is grounded by the experiential features of
    what surrounds it), then SELECT the shortlist candidate whose static grounded prototype best
    matches that SITUATION vector.
      SITU > GRD65_static (CI-sep) AND SITU > SITU_XWORD_SHUF => richer occurrence context carries the
        sense signal the hashed d256 lost => the wall was the substrate REPRESENTATION (buildable).
      SITU ~ GRD65_static AND SITU ~ SITU_XWORD_SHUF => even real context words do not sense-
        disambiguate these hard words under the per-word any-sense metric => the wall is DEEPER than
        the representation (the hard population's contexts are genuinely uninformative for grounding-
        based sense selection, and/or per-occurrence sense gold is needed to reward it)."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True, collect_ctx_words=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    ctxw = cap.get("ctx_words") or {}
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    tab = _load_binder65_table()
    if not tab:
        return {"error": "predicted-Binder-65 table unavailable"}

    def _b65(lemma):
        v = tab.get(lemma.lower())
        if v is None:
            return None
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else None

    def _situation(ctx_lemmas):
        """mean predicted-Binder-65 of the covered context content-words (L2-normed), or None."""
        vs = [tab[c.lower()] for c in ctx_lemmas if c.lower() in tab]
        if not vs:
            return None
        m = np.mean(np.stack(vs), axis=0)
        n = np.linalg.norm(m)
        return m / n if n > 1e-9 else None

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l) and ctxw.get(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    anc_b65 = {a: _b65(a) for a in anchors}

    # PASS 1: per-word geometry + occurrence situation vectors; build global situation pool
    rows = []
    global_situ = []
    reach = []
    ctx_cov = []      # fraction of a word's context tokens that are Binder-covered
    for w in pop_words:
        wi = ei[w]
        bw = _b65(w)
        if bw is None:
            continue
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = np.array([1 if _rel(w_ss, w_clos, anchors[j]) else 0 for j in order])
        if labs.sum() == 0:
            continue
        cb = [anc_b65[anchors[j]] for j in order]
        covered = [k for k, v in enumerate(cb) if v is not None]
        if len(covered) < 2:
            continue
        cbmat = np.stack([cb[k] for k in covered])
        situ = [_situation(L) for L in ctxw[w]]
        situ = [s for s in situ if s is not None]
        if not situ:
            continue
        dist_hit = int(labs[0] == 1)
        grd_static_hit = int(labs[covered[int(np.argmax(cbmat @ bw))]] == 1)
        rows.append((labs, cbmat, covered, dist_hit, grd_static_hit, situ))
        global_situ.extend(situ)
        if len(situ) >= 2:
            S = np.stack(situ); Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
            iu = np.triu_indices(len(Sn), 1)
            reach.append(1.0 - float((Sn @ Sn.T)[iu].mean()))
    if not rows:
        return {"error": "no scoreable words with context words"}
    global_situ = np.stack(global_situ)
    rng = np.random.default_rng(seed + 5150)

    occ = {"DIST": [], "GRD65_static": [], "SITU": [], "SITU_XWORD_SHUF": []}
    word_situ_pick_correct = []
    for (labs, cbmat, covered, dist_hit, grd_static_hit, situ) in rows:
        picks = []
        for s in situ:
            occ["DIST"].append(dist_hit)
            occ["GRD65_static"].append(grd_static_hit)
            p = covered[int(np.argmax(cbmat @ s))]
            occ["SITU"].append(int(labs[p] == 1)); picks.append(p)
            sx = global_situ[rng.integers(0, len(global_situ))]
            occ["SITU_XWORD_SHUF"].append(int(labs[covered[int(np.argmax(cbmat @ sx))]] == 1))
        if picks:
            word_situ_pick_correct.append(int(labs[Counter(picks).most_common(1)[0][0]] == 1))

    def _m(k):
        return round(float(np.mean(occ[k])), 4) if occ[k] else None

    def _ci(a_key, b_key, nboot=N_BOOT):
        a = np.array(occ[a_key]); b = np.array(occ[b_key]); mn = min(len(a), len(b))
        d = a[:mn] - b[:mn]
        bs = np.random.default_rng(seed + 88)
        idx = bs.integers(0, len(d), size=(nboot, len(d)))
        mns = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(mns, 2.5)), float(np.percentile(mns, 97.5))
        return {"lift": round(float(d.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    return {
        "budget": budget, "seed": seed, "topk": topk,
        "n_words_scored": len(rows), "n_occurrences_scored": len(occ["SITU"]),
        "reachability_within_word_situation_distance": round(float(np.mean(reach)), 4) if reach else None,
        "per_occurrence_rank1_correct": {k: _m(k) for k in occ},
        "per_word_SITU_plurality_correct": round(float(np.mean(word_situ_pick_correct)), 4) if word_situ_pick_correct else None,
        "ci_SITU_minus_GRD65static_DECISIVE": _ci("SITU", "GRD65_static"),
        "ci_SITU_minus_DIST": _ci("SITU", "DIST"),
        "ci_SITU_minus_XWORDSHUF_signal_test": _ci("SITU", "SITU_XWORD_SHUF"),
        "reading": ("SITU > GRD65_static (CI-sep) AND SITU > SITU_XWORD_SHUF => real context WORDS carry "
                    "the sense signal the hashed d256 lost -> the wall was the occurrence-context "
                    "REPRESENTATION (buildable). SITU ~ static AND ~ xword-shuffle => even rich context "
                    "words do not sense-disambiguate these hard words on the per-word any-sense metric "
                    "-> the wall is DEEPER (needs per-sense grounding + per-occurrence sense gold)."),
        "capture_elapsed_s": cap["elapsed_s"]}


def relational_graph_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """BREAKTHROUGH LEVER 2 (the change IN KIND): the feature-cosine family is exhausted (blend/
    context/cluster/gloss all plateau). Sense selection is TAXONOMIC/RELATIONAL (ATL is-a graph;
    Mirman 2017 taxonomic vs thematic dissociation), so select over the GRAPH, not by averaging
    vectors. Score each shortlist candidate anchor by its TAXONOMIC coherence (shared hypernym
    ancestry = Jaccard of WordNet hypernym closures -- a graph relatedness, NOT the wup threshold in
    the metric) to the SEED set = the KNOWN grounded anchor words OBSERVED IN THIS WORD'S CONTEXTS.
    Context words only pick SEED NODES; the GRAPH disambiguates -> the context-DILUTION failure that
    killed context-gating does not transfer (relational, not feature-average).

    *** CIRCULARITY WARNING (loud, per the drill): the correctness metric IS WordNet-relatedness and
    this selector walks WordNet -> the RAW relational number is grade-by-what-you-ground-by and is NOT
    trustworthy on its own. The HONEST reads are the CONTROLS: (a) RELATIONAL(real seeds) vs
    RELATIONAL(SHUFFLED seeds from a random other word) -- a real per-context taxonomic signal only if
    real >> shuffled; (b) RELATIONAL vs GRD65_static -- does the graph beat the feature-cosine. A clean
    verdict still needs a GOLD per-occurrence sense benchmark (independent of the graph). ***"""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True, collect_ctx_words=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    ctxw = cap.get("ctx_words") or {}
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anchor_set = set(anchors)
    anc_syn = {a: wn.synsets(a)[:3] for a in anchors}
    anc_clos = {a: [_syn_closure(s) for s in anc_syn[a]] for a in anchors}
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel_any(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    def _tax(a, seed_closlist):
        """max shared-ancestry Jaccard between anchor a's synset-closures and a seed's closures."""
        best = 0.0
        for ca in anc_clos[a]:
            for cs in seed_closlist:
                u = len(ca | cs)
                if u:
                    j = len(ca & cs) / u
                    if j > best:
                        best = j
        return best

    tab = _load_binder65_table()

    def _b65(lemma):
        if not tab:
            return None
        v = tab.get(lemma.lower())
        if v is None:
            return None
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else None

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l) and ctxw.get(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    anc_b65 = {a: _b65(a) for a in anchors}

    # per-word: observed KNOWN-anchor seeds from its contexts (most frequent, cap 8)
    seedmap = {}
    for w in pop_words:
        c = Counter()
        for L in ctxw[w]:
            for x in L:
                if x in anchor_set and x != w:
                    c[x] += 1
        seedmap[w] = [a for a, _ in c.most_common(8)]
    words_with_seeds = [w for w in pop_words if len(seedmap[w]) >= 2]
    rng = np.random.default_rng(seed + 2718)

    occ = {"DIST": [], "GRD65_static": [], "RELATIONAL": [], "RELATIONAL_SHUFSEED": [], "REL_PLUS_GRD": []}
    n_scored = 0
    for w in words_with_seeds:
        wi = ei[w]
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        cand = [anchors[j] for j in order]
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = np.array([1 if _rel_any(w_ss, w_clos, a) else 0 for a in cand])
        if labs.sum() == 0:
            continue
        n_scored += 1
        # seeds (real) + shuffled seeds (from a random OTHER word)
        seeds = seedmap[w]
        wsh = words_with_seeds[int(rng.integers(0, len(words_with_seeds)))]
        seeds_sh = seedmap[wsh]
        seed_clos = [c for s in seeds for c in anc_clos.get(s, [])]
        seed_clos_sh = [c for s in seeds_sh for c in anc_clos.get(s, [])]
        rel = np.array([_tax(a, seed_clos) for a in cand]) if seed_clos else np.zeros(len(cand))
        rel_sh = np.array([_tax(a, seed_clos_sh) for a in cand]) if seed_clos_sh else np.zeros(len(cand))
        # DIST + grounded static (blend cosine)
        occ["DIST"].append(int(labs[0] == 1))
        bw = _b65(w)
        if bw is not None:
            cb = np.array([[float(np.dot(_b65(a), bw)) if _b65(a) is not None else -9 for a in cand]])[0]
            gpick = int(np.argmax(cb))
        else:
            gpick = 0
        occ["GRD65_static"].append(int(labs[gpick] == 1))
        occ["RELATIONAL"].append(int(labs[int(np.argmax(rel))] == 1))
        occ["RELATIONAL_SHUFSEED"].append(int(labs[int(np.argmax(rel_sh))] == 1))
        # reliability-weighted fuse of relational + grounded (both taxonomic signals)
        zr = (rel - rel.mean()) / (rel.std() + 1e-9)
        if bw is not None:
            zg = (cb - cb.mean()) / (cb.std() + 1e-9)
            occ["REL_PLUS_GRD"].append(int(labs[int(np.argmax(zr + zg))] == 1))
        else:
            occ["REL_PLUS_GRD"].append(int(labs[int(np.argmax(zr))] == 1))

    if n_scored == 0:
        return {"error": "no scoreable words with >=2 known-anchor seeds"}

    def _m(k):
        return round(float(np.mean(occ[k])), 4) if occ[k] else None

    def _ci(a_key, b_key, nboot=N_BOOT):
        a = np.array(occ[a_key]); b = np.array(occ[b_key]); mn = min(len(a), len(b))
        d = a[:mn] - b[:mn]
        bs = np.random.default_rng(seed + 271)
        idx = bs.integers(0, len(d), size=(nboot, len(d)))
        mns = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(mns, 2.5)), float(np.percentile(mns, 97.5))
        return {"lift": round(float(d.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    return {
        "budget": budget, "seed": seed, "topk": topk, "n_words_scored": n_scored,
        "rank1_correct": {k: _m(k) for k in occ},
        "ci_RELATIONAL_minus_SHUFSEED_THE_VALID_SIGNAL_TEST": _ci("RELATIONAL", "RELATIONAL_SHUFSEED"),
        "ci_RELATIONAL_minus_GRD65static": _ci("RELATIONAL", "GRD65_static"),
        "ci_REL_PLUS_GRD_minus_GRD65static": _ci("REL_PLUS_GRD", "GRD65_static"),
        "reading": ("CIRCULAR METRIC -- read the CONTROLS: RELATIONAL >> RELATIONAL_SHUFSEED => the "
                    "observed-context taxonomic graph carries a REAL per-context sense signal (not graph "
                    "centrality). RELATIONAL / REL_PLUS_GRD > GRD65_static => the graph beats the feature-"
                    "cosine (the change-in-kind pays). If RELATIONAL ~ SHUFSEED, the raw number is just "
                    "graph structure/frequency (circular), not context signal. A clean verdict needs a "
                    "GOLD per-occurrence sense benchmark independent of WordNet."),
        "capture_elapsed_s": cap["elapsed_s"]}


def gloss_grounding_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """BREAKTHROUGH LEVER 1 (cleaner, less-circular): the ~0.45 plateau is the ceiling of cosine over
    a per-WORD grounded BLEND (a sense-blend for polysemous words). De-blend WITHOUT the unstable
    occurrence-clustering by grounding each of the target's WordNet SENSES from its GLOSS (definition
    + synonyms + hypernyms/hyponyms) via predicted-Binder-65 -- a clean per-SENSE vector, offline,
    free (research-pinned: grounding a hard sense by relating it to the known network / its
    definition; Borman & Lupyan "a definition is worth many contexts"). Grounding is EXPERIENTIAL
    (Binder), independent of the WordNet-relatedness METRIC (less circular than a graph walk).
      Per-SENSE metric (the clean test): does the per-sense gloss vector pick the anchor CORRECT FOR
        THAT SENSE better than the blend (which picks ONE anchor for all senses)?
      GLOSS_MFS > STATIC_BLEND (single-try, no multi-try inflation) => clean de-blend is the lever.
      GLOSS_ANYSENSE >> its RANDOM-gloss control => de-blending REVEALS correct senses the blend
        missed (real per-sense structure, not multi-try inflation)."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_syn = {a: wn.synsets(a)[:6] for a in anchors}

    def _rel_to_sense(a, s, s_clos):
        """anchor a related to a SINGLE target synset s (subsumption OR wup>=0.5)."""
        for b in anc_syn[a]:
            if b == s or b in s_clos or s in _syn_closure(b):
                return True
        for b in anc_syn[a][:3]:
            try:
                if (b.wup_similarity(s) or 0) >= 0.5:
                    return True
            except Exception:
                pass
        return False

    tab = _load_binder65_table()
    if not tab:
        return {"error": "predicted-Binder-65 table unavailable"}

    def _b65(lemma):
        v = tab.get(lemma.lower())
        if v is None:
            return None
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else None

    def _gloss_vec(syn):
        """clean per-SENSE grounded vector: mean predicted-Binder-65 over the sense's gloss words +
        synonyms + hypernym/hyponym lemmas (offline definitional grounding), L2-normed, or None."""
        words = set()
        for tok in syn.definition().replace(";", " ").split():
            t = "".join(ch for ch in tok.lower() if ch.isalpha())
            if len(t) >= 3:
                words.add(t)
        for lm in syn.lemma_names():
            words.add(lm.lower().replace("_", " ").split()[0])
        for rel in (syn.hypernyms() + syn.hyponyms()[:5]):
            for lm in rel.lemma_names()[:3]:
                words.add(lm.lower().replace("_", " ").split()[0])
        vs = [tab[w] for w in words if w in tab]
        if not vs:
            return None
        m = np.mean(np.stack(vs), axis=0); n = np.linalg.norm(m)
        return m / n if n > 1e-9 else None

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    anc_b65 = {a: _b65(a) for a in anchors}
    rng = np.random.default_rng(seed + 8128)

    persense = {"STATIC_BLEND": [], "GLOSS_PERSENSE": []}      # per-(word,sense) correct-for-that-sense
    anyword = {"STATIC_BLEND": [], "GLOSS_MFS": [], "GLOSS_ANYSENSE": [], "GLOSS_ANYSENSE_RANDOM": []}
    n_words = 0
    n_senses_grounded = 0
    for w in pop_words:
        wi = ei[w]
        bw = _b65(w)
        if bw is None:
            continue
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        cand_a = [anchors[j] for j in order]
        cb = [anc_b65[a] for a in cand_a]
        covered = [k for k, v in enumerate(cb) if v is not None]
        if len(covered) < 2:
            continue
        cbmat = np.stack([cb[k] for k in covered])
        # any-sense correctness of each covered candidate (same criterion family as elsewhere)
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        def _rel_any(a):
            a_ss = set(anc_syn[a]); a_clos = set().union(*[_syn_closure(s) for s in anc_syn[a]]) if anc_syn[a] else set()
            if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
                return True
            for s in list(w_ss)[:3]:
                for b in list(a_ss)[:3]:
                    try:
                        if (s.wup_similarity(b) or 0) >= 0.5:
                            return True
                    except Exception:
                        pass
            return False
        labs_any = np.array([1 if _rel_any(cand_a[covered[m]]) else 0 for m in range(len(covered))])
        if labs_any.sum() == 0:
            continue
        n_words += 1
        # STATIC blend pick (one anchor for the whole word)
        blend_pick = int(np.argmax(cbmat @ bw))
        anyword["STATIC_BLEND"].append(int(labs_any[blend_pick] == 1))
        senses = wn.synsets(w)[:4]
        gvecs = [_gloss_vec(s) for s in senses]
        sense_data = [(s, g) for s, g in zip(senses, gvecs) if g is not None]
        if not sense_data:
            continue
        n_senses_grounded += len(sense_data)
        # GLOSS_MFS = first (most-frequent) grounded sense, single try
        gloss_any_hits = []
        for si, (s, g) in enumerate(sense_data):
            pick = int(np.argmax(cbmat @ g))
            s_clos = _syn_closure(s)
            labs_s = np.array([1 if _rel_to_sense(cand_a[covered[m]], s, s_clos) else 0 for m in range(len(covered))])
            # per-sense: gloss pick correct for THIS sense; blend pick correct for THIS sense
            if labs_s.sum() > 0:
                persense["GLOSS_PERSENSE"].append(int(labs_s[pick] == 1))
                persense["STATIC_BLEND"].append(int(labs_s[blend_pick] == 1))
            gloss_any_hits.append(int(labs_any[pick] == 1))
            if si == 0:
                anyword["GLOSS_MFS"].append(int(labs_any[pick] == 1))
        anyword["GLOSS_ANYSENSE"].append(int(any(gloss_any_hits)))
        # RANDOM-gloss control (isolate multi-try inflation): random unit vectors, same #senses
        rhits = []
        for _ in sense_data:
            rg = rng.standard_normal(cbmat.shape[1]); rg /= (np.linalg.norm(rg) + 1e-12)
            rhits.append(int(labs_any[int(np.argmax(cbmat @ rg))] == 1))
        anyword["GLOSS_ANYSENSE_RANDOM"].append(int(any(rhits)))

    if n_words == 0:
        return {"error": "no scoreable words"}

    def _m(d, k):
        return round(float(np.mean(d[k])), 4) if d[k] else None

    def _ci(d, a_key, b_key, nboot=N_BOOT):
        a = np.array(d[a_key]); b = np.array(d[b_key]); mn = min(len(a), len(b))
        x = a[:mn] - b[:mn]
        bs = np.random.default_rng(seed + 111)
        idx = bs.integers(0, len(x), size=(nboot, len(x)))
        mns = x[idx].mean(axis=1)
        lo, hi = float(np.percentile(mns, 2.5)), float(np.percentile(mns, 97.5))
        return {"lift": round(float(x.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    return {
        "budget": budget, "seed": seed, "topk": topk, "n_words_scored": n_words,
        "n_senses_grounded": n_senses_grounded, "n_persense_pairs": len(persense["GLOSS_PERSENSE"]),
        "per_sense_correct_for_that_sense": {k: _m(persense, k) for k in persense},
        "ci_GLOSS_PERSENSE_minus_STATIC_BLEND_DECISIVE": _ci(persense, "GLOSS_PERSENSE", "STATIC_BLEND"),
        "any_sense_word_level": {k: _m(anyword, k) for k in anyword},
        "ci_GLOSS_MFS_minus_STATIC_BLEND_singletry": _ci(anyword, "GLOSS_MFS", "STATIC_BLEND"),
        "ci_GLOSS_ANYSENSE_minus_RANDOM_multitry_control": _ci(anyword, "GLOSS_ANYSENSE", "GLOSS_ANYSENSE_RANDOM"),
        "reading": ("GLOSS_PERSENSE > STATIC_BLEND (per-sense, CI-sep) => clean per-sense gloss grounding "
                    "beats the blend at picking the anchor correct FOR THAT SENSE -> de-blend is the lever. "
                    "GLOSS_MFS > STATIC_BLEND => even a single (most-frequent) clean sense beats the blend "
                    "(no multi-try inflation). GLOSS_ANYSENSE >> RANDOM control => real per-sense structure. "
                    "All ~equal => de-blending via glosses does not help on this population."),
        "capture_elapsed_s": cap["elapsed_s"]}


def _spherical_2means(V, seed, iters=8):
    """Tiny glass-box spherical k=2 clustering of L2-normed rows V (cosine). Seeds = the two most
    dissimilar rows. Returns an assignment array in {0,1}. For <4 rows returns all-zeros (k=1)."""
    n = len(V)
    if n < 4:
        return np.zeros(n, int)
    G = V @ V.T
    i0 = 0
    j0 = int(np.argmin(G[i0]))
    i1 = int(np.argmin(G[j0]))       # the pair with least similarity
    cent = np.stack([V[j0], V[i1]])
    assign = np.zeros(n, int)
    for _ in range(iters):
        assign = np.argmax(V @ cent.T, axis=1)
        newc = []
        for k in (0, 1):
            rows = V[assign == k]
            if len(rows) == 0:
                newc.append(cent[k]); continue
            m = rows.mean(0); nn = np.linalg.norm(m)
            newc.append(m / nn if nn > 1e-9 else cent[k])
        newc = np.stack(newc)
        if np.allclose(newc, cent):
            cent = newc; break
        cent = newc
    return assign


def sense_cluster_grounding_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """THE SENSE-INDUCTION LEVER (the named next work toward the ~0.85 ceiling). Two failure modes were
    located: a SINGLE occurrence context is too NOISY (situation_grounding ~ chance-ish), and the per-
    WORD grounding is too BLURRY (a sense-blend). The in-between fix (per-sense prototypes; Rodd 2004
    separable attractor basins): CLUSTER a word's occurrences into senses (spherical k=2 over their
    situation vectors = mean-Binder of each occurrence's context words), ground each CLUSTER by its
    centroid (denoised AND sub-word-specific), then select per occurrence by its cluster's centroid.
      CLUSTER > GRD65_static (CI-sep) => per-sense grounding breaks past static => the sense-induction
        lever works; sequence sense-splitting BEFORE grounding. per_word_best_cluster_correct is the
        upper bound: does splitting REVEAL a correct sense the blend missed?
      CLUSTER ~ GRD65_static => even denoised per-sense grounding does not beat static on this hard
        population => the sense-induction wall is real (W9 instability is binding), not a denoising gap."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True, collect_ctx_words=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    ctxw = cap.get("ctx_words") or {}
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]])) for a in anchors}

    def _rel(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    tab = _load_binder65_table()
    if not tab:
        return {"error": "predicted-Binder-65 table unavailable"}

    def _b65(lemma):
        v = tab.get(lemma.lower())
        if v is None:
            return None
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else None

    def _situation(ctx_lemmas):
        vs = [tab[c.lower()] for c in ctx_lemmas if c.lower() in tab]
        if not vs:
            return None
        m = np.mean(np.stack(vs), axis=0); n = np.linalg.norm(m)
        return m / n if n > 1e-9 else None

    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l) and ctxw.get(l)]
    embed = sorted(set(anchors) | set(pop_words))
    ei = {w: i for i, w in enumerate(embed)}
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[ei[a]] for a in anchors], axis=0))
    anc_b65 = {a: _b65(a) for a in anchors}

    occ = {"DIST": [], "GRD65_static": [], "SITU_single": [], "CLUSTER": [], "CLUSTER_XWORD_SHUF": []}
    per_word_best_cluster = []      # per-sense UPPER bound: any cluster centroid picks a correct anchor
    per_word_best_random = []       # CONTROL: same upper bound under a RANDOM 2-split (isolates the
                                    # 2-tries inflation from genuine sense structure)
    per_word_static = []
    global_cent = []
    rows = []
    rng2 = np.random.default_rng(seed + 31337)
    for w in pop_words:
        wi = ei[w]
        bw = _b65(w)
        if bw is None:
            continue
        q = phi[wi] / (np.linalg.norm(phi[wi]) + 1e-12)
        sims_all = A @ q
        order = [j for j in np.argsort(-sims_all) if anchors[j] != w][:topk]
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        labs = np.array([1 if _rel(w_ss, w_clos, anchors[j]) else 0 for j in order])
        if labs.sum() == 0:
            continue
        cb = [anc_b65[anchors[j]] for j in order]
        covered = [k for k, v in enumerate(cb) if v is not None]
        if len(covered) < 2:
            continue
        cbmat = np.stack([cb[k] for k in covered])
        situ = [_situation(L) for L in ctxw[w]]
        keep = [s for s in situ if s is not None]
        if len(keep) < 1:
            continue
        S = np.stack(keep)
        assign = _spherical_2means(S, seed)
        cents = {}
        for k in set(assign.tolist()):
            m = S[assign == k].mean(0); nn = np.linalg.norm(m)
            cents[k] = m / nn if nn > 1e-9 else m
        dist_hit = int(labs[0] == 1)
        grd_static_hit = int(labs[covered[int(np.argmax(cbmat @ bw))]] == 1)
        per_word_static.append(grd_static_hit)
        # per-cluster picks; per-word upper bound = ANY cluster centroid picks a correct anchor
        cluster_pick_correct = {}
        for k, c in cents.items():
            cluster_pick_correct[k] = int(labs[covered[int(np.argmax(cbmat @ c))]] == 1)
        per_word_best_cluster.append(int(any(cluster_pick_correct.values())))
        # CONTROL: random 2-split of the SAME occurrences -> its best-cluster upper bound
        if len(S) >= 4:
            rasg = rng2.integers(0, 2, size=len(S))
            rhit = 0
            for k in set(rasg.tolist()):
                m = S[rasg == k].mean(0); nn = np.linalg.norm(m)
                rc = m / nn if nn > 1e-9 else m
                if labs[covered[int(np.argmax(cbmat @ rc))]] == 1:
                    rhit = 1; break
            per_word_best_random.append(rhit)
        else:
            per_word_best_random.append(int(any(cluster_pick_correct.values())))
        for k in cents:
            global_cent.append(cents[k])
        rows.append((labs, cbmat, covered, dist_hit, grd_static_hit, S, assign, cents, cluster_pick_correct))
    if not rows:
        return {"error": "no scoreable words with context words"}
    global_cent = np.stack(global_cent)
    rng = np.random.default_rng(seed + 6006)
    for (labs, cbmat, covered, dist_hit, grd_static_hit, S, assign, cents, cpc) in rows:
        for oi in range(len(S)):
            occ["DIST"].append(dist_hit)
            occ["GRD65_static"].append(grd_static_hit)
            occ["SITU_single"].append(int(labs[covered[int(np.argmax(cbmat @ S[oi]))]] == 1))
            occ["CLUSTER"].append(cpc[assign[oi]])          # this occurrence's cluster centroid pick
            cx = global_cent[rng.integers(0, len(global_cent))]
            occ["CLUSTER_XWORD_SHUF"].append(int(labs[covered[int(np.argmax(cbmat @ cx))]] == 1))

    def _m(k):
        return round(float(np.mean(occ[k])), 4) if occ[k] else None

    def _ci(a_key, b_key, nboot=N_BOOT):
        a = np.array(occ[a_key]); b = np.array(occ[b_key]); mn = min(len(a), len(b))
        d = a[:mn] - b[:mn]
        bs = np.random.default_rng(seed + 99)
        idx = bs.integers(0, len(d), size=(nboot, len(d)))
        mns = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(mns, 2.5)), float(np.percentile(mns, 97.5))
        return {"lift": round(float(d.mean()), 4), "lo": round(lo, 4), "hi": round(hi, 4),
                "ci_separated_above_0": bool(lo > 0)}

    return {
        "budget": budget, "seed": seed, "topk": topk,
        "n_words_scored": len(rows), "n_occurrences_scored": len(occ["CLUSTER"]),
        "per_occurrence_rank1_correct": {k: _m(k) for k in occ},
        "per_word_static_correct": round(float(np.mean(per_word_static)), 4) if per_word_static else None,
        "per_word_best_cluster_correct_UPPER_BOUND": round(float(np.mean(per_word_best_cluster)), 4) if per_word_best_cluster else None,
        "per_word_best_RANDOMsplit_correct_CONTROL": round(float(np.mean(per_word_best_random)), 4) if per_word_best_random else None,
        "upper_bound_real_minus_random_split": (round(float(np.mean(per_word_best_cluster)) - float(np.mean(per_word_best_random)), 4)
                                                if per_word_best_cluster and per_word_best_random else None),
        "ci_CLUSTER_minus_GRD65static_DECISIVE": _ci("CLUSTER", "GRD65_static"),
        "ci_CLUSTER_minus_SITUsingle": _ci("CLUSTER", "SITU_single"),
        "ci_CLUSTER_minus_XWORDSHUF": _ci("CLUSTER", "CLUSTER_XWORD_SHUF"),
        "reading": ("CLUSTER > GRD65_static (CI-sep) => per-sense (clustered) grounding breaks past static "
                    "-> the sense-induction lever works. per_word_best_cluster_correct >> per_word_static "
                    "=> splitting REVEALS correct senses the blend missed (the achievable headroom). "
                    "CLUSTER ~ static => the sense-induction wall is real on this population (denoising + "
                    "sub-word specificity still insufficient), consistent with the W9 splitting instability."),
        "capture_elapsed_s": cap["elapsed_s"]}


def supervised_reranker_probe(budget: int, run_mode: str, seed: int, topk: int = 20) -> dict:
    """THE DECISIVE LAST RUNG. Unsupervised + the learned distilled read-out both fail to SELECT the
    correct anchor from the retrieved top-K (rank-1 ~0.24 vs top-10 ceiling ~0.87). Does GROUNDING-
    LABEL SUPERVISION extract a selection signal the unsupervised read-outs miss? A glass-box logistic
    over cheap per-candidate features (cosine, background-subtracted cosine, anchor frequency, anchor
    specificity/depth, cosine rank), 5-fold CROSS-VALIDATED OVER HELD-OUT WORDS (labels used offline
    only = an admissible foundation asset; no external LLM at inference). If CV rank-1 >> 0.24 the
    signal EXISTS and the fix is a learned selector; if ~0.24 it is genuinely ABSENT from distributional
    context -> needs grounded/sensorimotor input (the reader_meaning_channel/ATL problem)."""
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    try:
        from sklearn.linear_model import LogisticRegression
    except Exception as e:
        return {"error": "sklearn unavailable: " + str(e)[:80]}
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    anc_sc = {a: (set(wn.synsets(a)[:6]), set().union(*[_syn_closure(s) for s in wn.synsets(a)[:6]]))
              for a in anchors}
    anc_freq = {a: float(sum(counts[a].values())) for a in anchors}
    anc_depth = {a: (min([s.min_depth() for s in wn.synsets(a)[:6]] or [0])) for a in anchors}

    def _rel_wup(w_ss, w_clos, a):
        """FULL correctness criterion (matches _wn_related everywhere else): subsumption OR wup>=0.5.
        Called only on TOP-K candidates per word, so the wup cost is bounded."""
        a_ss, a_clos = anc_sc[a]
        if (w_ss & a_ss) or any(b in w_clos for b in a_ss) or any(s in a_clos for s in w_ss):
            return True
        for s in list(w_ss)[:3]:
            for b in list(a_ss)[:3]:
                try:
                    if (s.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    # phi over ALL pop words with counts + the anchors (recov defined AFTER, by correct-in-top-K)
    pop_words = [l for l in sorted(pop) if counts.get(l) and wn.synsets(l)]
    embed = sorted(set(anchors) | set(pop_words))
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    rowi = {w: i for i, w in enumerate(embed)}
    if len(anchors) < SVD_K + 5 or len(pop_words) < 40:
        return {"error": "insufficient", "n_pop": len(pop_words), "n_anchors": len(anchors)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[rowi[a]] for a in anchors], axis=0))
    Wq = l2n(np.stack([phi[rowi[w]] for w in pop_words], axis=0))
    S = Wq @ A.T
    bg = S.mean(axis=0)
    logf = np.log(np.array([anc_freq[a] + 1 for a in anchors]))
    dep = np.array([anc_depth[a] for a in anchors], float)

    # per-word top-K candidate rows: features + FULL-criterion (wup) labels on the top-K only
    rows_by_word = {}
    for i, w in enumerate(pop_words):
        sims = S[i]
        order = [j for j in np.argsort(-sims) if anchors[j] != w][:topk]
        w_ss = set(wn.synsets(w)[:6]); w_clos = set().union(*[_syn_closure(s) for s in wn.synsets(w)[:6]])
        feats, labs, cand = [], [], []
        for rnk, j in enumerate(order):
            feats.append([sims[j], sims[j] - bg[j], logf[j], dep[j], float(rnk)])
            labs.append(1 if _rel_wup(w_ss, w_clos, anchors[j]) else 0)
            cand.append(anchors[j])
        rows_by_word[w] = (np.array(feats, float), np.array(labs, int), cand)

    rng = np.random.default_rng(seed)
    words = [w for w in pop_words if rows_by_word[w][1].sum() > 0]   # words with a correct anchor IN top-K
    rng.shuffle(words)
    folds = np.array_split(words, 5)
    sup_hit = near_hit = n = 0
    for f in range(5):
        test = set(folds[f]); train = [w for w in words if w not in test]
        Xtr = np.vstack([rows_by_word[w][0] for w in train])
        ytr = np.concatenate([rows_by_word[w][1] for w in train])
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
        clf = LogisticRegression(max_iter=500, class_weight="balanced")
        clf.fit((Xtr - mu) / sd, ytr)
        for w in folds[f]:
            X, y, cand = rows_by_word[w]
            p = clf.predict_proba((X - mu) / sd)[:, 1]
            n += 1
            if y[int(np.argmax(p))] == 1:
                sup_hit += 1
            if y[0] == 1:                     # NEAREST = top cosine (rank 0)
                near_hit += 1
    coefs = dict(zip(["cosine", "cos_minus_bg", "log_freq", "specificity_depth", "cos_rank"],
                     [round(float(c), 3) for c in clf.coef_[0]]))
    return {"budget": budget, "seed": seed, "n_words_with_correct_in_topK": n, "topk": topk,
            "supervised_rank1_correct": round(sup_hit / n, 4) if n else None,
            "nearest_rank1_correct_same_pop": round(near_hit / n, 4) if n else None,
            "lift_over_nearest": round((sup_hit - near_hit) / n, 4) if n else None,
            "logistic_coefs_last_fold": coefs,
            "reading": ("supervised >> nearest => a selection signal EXISTS in cheap features (build a "
                        "learned re-ranker). supervised ~= nearest => the signal is genuinely ABSENT from "
                        "distributional context => needs grounded/sensorimotor input (ATL)."),
            "capture_elapsed_s": cap["elapsed_s"]}


def readout_reranker_probe(budget: int, run_mode: str, seed: int, topk_pool: int = 50) -> dict:
    """THE READ-OUT FIX TEST. The wall is that single-nearest-anchor picks a SYNTAGMATIC (topical:
    whisky->wedding) associate; the PARADIGMATIC (substitutable: whisky->brandy) WordNet-correct
    anchor sits at rank ~3. Test glass-box re-rankers over the top-`topk_pool` distributional
    candidates that de-emphasise the shared-topic backbone:
      NEAREST      : rank by raw cosine (the incumbent read-out; baseline).
      BG_SUBTRACT  : score = cos(w,a) - mean_w' cos(w',a) -- subtract each anchor's GENERICITY
                     (how similar it is to everything), i.e. remove the topical/frequency backbone.
      RECIPROCAL   : keep only anchors for which w is ALSO in a's top-`topk_pool`; rank by w's rank
                     + a's rank of w (mutual-neighbour filter kills asymmetric topical associates).
      ABSTAIN      : NEAREST, but refuse to ground when the top1-top2 cosine margin < a threshold
                     (raises PRECISION of what is grounded -- the brief's do-not-add-wrong-meanings).
    Correctness = WordNet subsumption/shared-synset (fast; the same criterion family as _wn_related,
    wup dropped for speed -> slightly STRICTER, so gains are conservative). Space = PPMI+SVD (phi)."""
    import scipy.sparse as sp
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a) and wn.synsets(a))
    # precompute synsets + closures (fast correctness)
    def _syns_clos(w):
        ss = wn.synsets(w)[:6]
        clos = set()
        for s in ss:
            clos |= _syn_closure(s)
        return set(ss), clos
    anc_sc = {a: _syns_clos(a) for a in anchors}

    def _related(w_ss, w_clos, a):
        a_ss, a_clos = anc_sc[a]
        if w_ss & a_ss:
            return True
        if any(b in w_clos for b in a_ss):
            return True
        if any(s in a_clos for s in w_ss):
            return True
        return False

    recov, w_sc = [], {}
    for l in sorted(pop):
        if not counts.get(l):
            continue
        ss, clos = _syns_clos(l)
        if not ss:
            continue
        if any(_related(ss, clos, a) for a in anchors):     # a correct anchor exists
            recov.append(l)
            w_sc[l] = (ss, clos)
    if len(recov) < 10 or len(anchors) < SVD_K + 5:
        return {"error": "insufficient", "n_recov": len(recov), "n_anchors": len(anchors)}

    embed = sorted(set(anchors) | set(recov))
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    row = {w: i for i, w in enumerate(embed)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    A = l2n(np.stack([phi[row[a]] for a in anchors], axis=0))     # [n_anchor, k], L2
    ai = {a: i for i, a in enumerate(anchors)}

    # anchor genericity backbone: mean similarity of each anchor to ALL recov words
    Wq = l2n(np.stack([phi[row[w]] for w in recov], axis=0))      # [n_recov, k]
    sim_wa = Wq @ A.T                                             # [n_recov, n_anchor]
    anchor_bg = sim_wa.mean(axis=0)                              # genericity per anchor
    # anchor->its own top pool over the anchor set (for reciprocal), computed once
    AA = A @ A.T
    np.fill_diagonal(AA, -2.0)
    anchor_top = {anchors[i]: set(np.argsort(-AA[i])[:topk_pool]) for i in range(len(anchors))}

    Ks = [1, 3, 5, 10]
    res = {}

    def _score_readout(name, rank_fn, abstain_margin=None):
        hits = {k: 0 for k in Ks}
        n = grounded = correct = 0
        for wi, w in enumerate(recov):
            sims = sim_wa[wi]
            order = list(np.argsort(-sims))
            order = [j for j in order if anchors[j] != w][:topk_pool]
            ranked = rank_fn(w, wi, order, sims)          # list of anchor indices, best first
            n += 1
            ss, clos = w_sc[w]
            if abstain_margin is not None:
                top = [sims[j] for j in order[:2]]
                if len(top) >= 2 and (top[0] - top[1]) < abstain_margin:
                    continue                               # abstain: not grounded
            if not ranked:
                continue
            grounded += 1
            top1 = anchors[ranked[0]]
            if _related(ss, clos, top1):
                correct += 1
            for k in Ks:
                if any(_related(ss, clos, anchors[j]) for j in ranked[:k]):
                    hits[k] += 1
        return {"n": n, "n_grounded": grounded,
                "grounded_correct_rate_over_pop": round(correct / n, 4) if n else None,
                "precision_of_grounded": round(correct / grounded, 4) if grounded else None,
                "topk_correct_recall": {str(k): round(hits[k] / n, 4) for k in Ks} if n else {}}

    res["NEAREST"] = _score_readout("NEAREST", lambda w, wi, order, sims: order)
    res["BG_SUBTRACT"] = _score_readout(
        "BG_SUBTRACT",
        lambda w, wi, order, sims: sorted(order, key=lambda j: -(sims[j] - anchor_bg[j])))

    def _recip(w, wi, order, sims):
        keep = [j for j in order if row.get(w) is not None and ai[anchors[j]] in anchor_top and
                _w_in_anchor_top(w, anchors[j])]
        return keep if keep else order

    def _w_in_anchor_top(w, a):
        # is w among anchor a's top pool? approximate: compare w's phi to a's neighbours set membership
        # (a's top pool is over anchors; w may not be an anchor, so test w's sim rank vs a's pool cutoff)
        av = A[ai[a]]
        wv = phi[row[w]] / (np.linalg.norm(phi[row[w]]) + 1e-12)
        s_wa = float(av @ wv)
        # a's topk_pool-th anchor similarity as the cutoff
        cutoff = np.sort(AA[ai[a]])[::-1][min(topk_pool, len(anchors)) - 1]
        return s_wa >= cutoff
    res["RECIPROCAL"] = _score_readout("RECIPROCAL", _recip)
    res["ABSTAIN_m0.02"] = _score_readout("ABSTAIN", lambda w, wi, order, sims: order,
                                          abstain_margin=0.02)
    res["ABSTAIN_m0.05"] = _score_readout("ABSTAIN", lambda w, wi, order, sims: order,
                                          abstain_margin=0.05)

    return {"budget": budget, "seed": seed, "n_consol_fail": len(pop), "n_recoverable": len(recov),
            "n_anchors": len(anchors), "topk_pool": topk_pool, "readouts": res,
            "reading": ("NEAREST precision_of_grounded is the incumbent ceiling (~0.25-0.30). If "
                        "BG_SUBTRACT / RECIPROCAL raise precision_of_grounded, the syntagmatic-topic "
                        "backbone was the wall and a paradigmatic read-out is the fix. If ABSTAIN "
                        "raises precision at reduced coverage, low-margin refusal is a cheap precision "
                        "lever. If none beat NEAREST, the paradigmatic signal is genuinely absent."),
            "capture_elapsed_s": cap["elapsed_s"]}


def walls_probe(budget: int, run_mode: str, seed: int, do_distilled: bool = False,
                distilled_cap: int = 60) -> dict:
    """DO ALL THE REMAINING WALLS. The encoder diagnostic showed the correct anchor sits at median
    rank ~3 (top-10 ~85%) under EVERY encoder incl. syntax -> the wall is the READ-OUT, not the
    encoder. This probe drills:
      #1 READ-OUT: the top-K correct-recall CURVE (the ceiling a re-ranking read-out could reach),
         and whether the TRAINED distilled substitutability direction re-ranks the top region better
         than raw-nearest.
      #2 SECOND ORACLE: recompute nearest-correct + rank under an INDEPENDENT correctness criterion
         (WordNet gloss-overlap, Lesk-style) -> is the near-miss finding scorer-robust?
      #3 ANCHOR SPECIFICITY: are the correct anchors in the top region SPECIFIC (deep synsets) or
         vague hypernyms (shallow) -> how much is a read-out fix actually worth?"""
    import scipy.sparse as sp
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K, l2n
    from nltk.corpus import wordnet as wn
    cap = capture(budget, run_mode, seed, route_b=True)
    space = cap["state"].space
    pop = cap["consol_fail"]
    counts = space.all_context_counts()
    anchors = sorted(a for a in space.anchors()
                     if a in cap["seed_words"] and is_eligible_meaning(a) and counts.get(a))
    anchor_syns = {a: wn.synsets(a)[:6] for a in anchors}
    anchor_syns = {a: s for a, s in anchor_syns.items() if s}
    anchors = [a for a in anchors if a in anchor_syns]

    def _gloss_words(word):
        s = set()
        for syn in wn.synsets(word)[:6]:
            for tok in syn.definition().lower().replace(";", " ").split():
                t = tok.strip('.,:()"\'')
                if len(t) > 2:
                    s.add(t)
        return s
    agloss = {a: _gloss_words(a) for a in anchors}

    def _gloss_correct_set(w):
        wg = _gloss_words(w)
        out = set()
        for a in anchors:
            if a in wg or w in agloss[a] or len(wg & agloss[a]) >= 2:
                out.add(a)
        return out

    correct_path, correct_gloss, recov = {}, {}, []
    for l in sorted(pop):
        if not counts.get(l):
            continue
        cp = _correct_anchor_set(l, anchor_syns, wn)
        if cp:
            correct_path[l] = cp
            correct_gloss[l] = _gloss_correct_set(l)
            recov.append(l)
    if len(recov) < 10 or len(anchors) < SVD_K + 5:
        return {"error": "insufficient", "n_recov": len(recov), "n_anchors": len(anchors)}

    embed = sorted(set(anchors) | set(recov))
    vocab = {w: i for i, w in enumerate(sorted({c for w in embed for c in counts[w]}))}
    M = _count_matrix(embed, counts, vocab)
    row = {w: i for i, w in enumerate(embed)}
    phi = ppmi_svd(M, svd_k=SVD_K)
    anc_mat = l2n(np.stack([phi[row[a]] for a in anchors], axis=0))
    Ks = [1, 3, 5, 10, 20, 50]

    def _topk_curve(correct_sets, matrix, rowmap, anc_matrix):
        hits = {k: 0 for k in Ks}
        n = 0
        depth_of_correct = []
        for w in recov:
            if w not in rowmap:
                continue
            n += 1
            q = matrix[rowmap[w]] / (np.linalg.norm(matrix[rowmap[w]]) + 1e-12)
            sims = anc_matrix @ q
            order = [anchors[i] for i in np.argsort(-sims) if anchors[i] != w]
            cset = correct_sets[w]
            for k in Ks:
                if any(a in cset for a in order[:k]):
                    hits[k] += 1
            # specificity: min_depth of the first correct anchor's synsets (deeper = more specific)
            for a in order[:20]:
                if a in cset:
                    ds = [s.min_depth() for s in anchor_syns.get(a, [])]
                    if ds:
                        depth_of_correct.append(min(ds))
                    break
        return {"n": n, "topk_correct_recall": {str(k): round(hits[k] / n, 4) for k in Ks} if n else {},
                "median_correct_anchor_min_depth": (int(np.median(depth_of_correct))
                                                    if depth_of_correct else None)}

    path_curve = _topk_curve(correct_path, phi, row, anc_mat)
    gloss_curve = _topk_curve(correct_gloss, phi, row, anc_mat)

    # #1 distilled substitutability direction as a re-ranking read-out (opt-in: dm_build is heavy)
    distilled = None
    if do_distilled:
      try:
        from hdlab.distributional_meaning_channel import build as dm_build
        ch = dm_build(counts)
        scored_words = recov[:distilled_cap]
        hits = {k: 0 for k in Ks}; n = 0
        for w in scored_words:
            pairs = [(w, a) for a in anchors]
            scores = ch.substitutability_batch(pairs)
            ranked = [a for a, s in sorted(zip(anchors, scores),
                                           key=lambda t: (-(t[1] if t[1] is not None else -1e9))) if a != w]
            cset = correct_path[w]
            n += 1
            for k in Ks:
                if any(a in cset for a in ranked[:k]):
                    hits[k] += 1
        distilled = {"n": n, "topk_correct_recall_path": {str(k): round(hits[k] / n, 4) for k in Ks} if n else {}}
      except Exception as e:
        distilled = {"error": str(e)[:200]}

    return {"budget": budget, "seed": seed, "n_consol_fail": len(pop), "n_recoverable": len(recov),
            "n_anchors": len(anchors),
            "readout_topK_phi_pathoracle": path_curve,
            "readout_topK_phi_glossoracle": gloss_curve,
            "distilled_direction_readout": distilled,
            "reading": ("topk_correct_recall rising steeply K=1->10 means the correct anchor is in the "
                        "region but not rank-1 => a re-ranking READ-OUT is the lever (not the encoder). "
                        "path vs gloss agreement => the near-miss is scorer-robust. deep median depth => "
                        "the reachable correct anchors are specific, so the read-out fix is worth it."),
            "capture_elapsed_s": cap["elapsed_s"]}


def oracle_anchor_ceiling(budget: int, run_mode: str, seed: int, sources=None) -> dict:
    """THE DECISIVE DECOMPOSITION I OWED: is the wall REPRESENTATION-bound or COVERAGE-bound?
    For each CONSOLIDATION_FAIL word, does a WordNet-CORRECT eligible anchor even EXIST anywhere in
    the learner's known vocabulary (the anchor pool)? That is the CEILING of anchor-nearest-neighbour
    grounding under a PERFECT representation. Partition the wall:
      - COVERAGE-BOUND: no correct anchor exists -> a better encoder cannot help; the meaning is not
        in the vocabulary (needs vocabulary growth / anchor-pool expansion / ATL).
      - REPRESENTATION-BOUND (recoverable): a correct anchor EXISTS but our method misses it -> a
        better encoder / sense-splitting could recover it.
      - ALREADY-CORRECT: correct anchor exists and our single-bundle method already grounds it.
    This tells us WHICH lever to pull, which no experiment so far measured."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return {"error": "wordnet unavailable"}
    cap = capture(budget, run_mode, seed, sources=sources)
    space = cap["state"].space
    pop = cap["consol_fail"]
    pop_lemmas = sorted(pop)
    anchors = [a for a in space.anchors() if is_eligible_meaning(a)]
    # precompute each anchor's synsets (capped) once
    anc_syn = {a: wn.synsets(a)[:6] for a in anchors}
    anc_syn = {a: s for a, s in anc_syn.items() if s}

    def _related(ws, wclos, anc) -> bool:
        for b in anc_syn[anc]:
            if b in wclos:                                  # anchor sense subsumed by / equal to a word sense
                return True
            bclos = set(b.closure(lambda x: x.hypernyms()))
            if any(a in bclos for a in ws):                 # word sense subsumed by anchor sense
                return True
            for a in ws:
                try:
                    if (a.wup_similarity(b) or 0) >= 0.5:
                        return True
                except Exception:
                    pass
        return False

    def _has_correct_anchor(w) -> bool:
        ws = wn.synsets(w)[:6]
        if not ws:
            return False
        wclos = set()
        for a in ws:
            wclos |= {a} | set(a.closure(lambda x: x.hypernyms()))
        for anc in anchors:
            if anc == w or anc not in anc_syn:
                continue
            if _related(ws, wclos, anc):
                return True
        return False

    # our actual single-bundle grounding correctness (the representative incumbent-style grounder)
    method_correct = {}
    for l in pop_lemmas:
        raw = np.sum([t.context_vec for t in pop[l].traces], axis=0)
        anc, _ = _eligible_anchor(raw, l, space)
        method_correct[l] = (anc != l) and bool(_wn_related([(l, anc)]).get((l, anc), False))

    cat_of = {}
    try:
        poly_set = {l for l in pop_lemmas if len(wn.synsets(l)) >= 5}
    except Exception:
        poly_set = set()
    coverage_bound = recoverable = already = 0
    by_pop = {"all": [0, 0, 0], "polysemous": [0, 0, 0], "nonpolysemous": [0, 0, 0]}  # [cov, recov, already]
    for l in pop_lemmas:
        avail = _has_correct_anchor(l)
        if not avail:
            bucket = 0; coverage_bound += 1
        elif method_correct[l]:
            bucket = 2; already += 1
        else:
            bucket = 1; recoverable += 1
        by_pop["all"][bucket] += 1
        key = "polysemous" if l in poly_set else "nonpolysemous"
        by_pop[key][bucket] += 1
    n = len(pop_lemmas)

    def _frac(d):
        tot = sum(d)
        return {"n": tot, "coverage_bound": round(d[0] / tot, 4) if tot else None,
                "representation_recoverable": round(d[1] / tot, 4) if tot else None,
                "already_correct": round(d[2] / tot, 4) if tot else None}
    return {
        "n_consol_fail": n, "n_eligible_anchors": len(anchors),
        "oracle_anchor_ceiling": round((recoverable + already) / n, 4) if n else None,
        "actual_single_bundle_correct": round(already / n, 4) if n else None,
        "partition_all": _frac(by_pop["all"]),
        "partition_polysemous": _frac(by_pop["polysemous"]),
        "partition_nonpolysemous": _frac(by_pop["nonpolysemous"]),
        "reading": ("coverage_bound HIGH => the meaning is not in the vocabulary (grow anchors/ATL); "
                    "representation_recoverable HIGH => a correct anchor EXISTS but our encoder misses "
                    "it (better encoder / sense-splitting is the lever)."),
        "capture_elapsed_s": cap["elapsed_s"],
    }


def online_sense_cluster(traces: List[Trace], tau: float) -> List[List[int]]:
    """Online DP-means / NP-MSSG sense induction (Neelakantan 2014; Kulis & Jordan 2012 DP-means as
    the small-variance limit of a Dirichlet-process mixture). Streaming, as the brain reads:
    on each context, assign to the nearest existing sense-centroid if cos >= tau, else SPAWN a new
    sense. Returns clusters as lists of trace indices (in encounter order). tau is OURS-UNDER-TEST
    (swept; the literature tunes it 0.4-0.6, dataset-specific -- never adopted)."""
    centroids: List[List[float]] = []      # running SUM vectors
    counts: List[int] = []
    clusters: List[List[int]] = []
    for i, t in enumerate(traces):
        c = t.context_vec
        if not centroids:
            centroids.append(np.array(c, dtype=np.float64)); counts.append(1); clusters.append([i]); continue
        sims = [_cos(c, cen) for cen in centroids]
        k = int(np.argmax(sims))
        if sims[k] >= tau:
            centroids[k] = centroids[k] + c; counts[k] += 1; clusters[k].append(i)
        else:
            centroids.append(np.array(c, dtype=np.float64)); counts.append(1); clusters.append([i])
    return clusters


def _inter_sense_relatedness(word: str) -> Optional[float]:
    """Mean pairwise Wu-Palmer among a word's WordNet synsets. LOW => homonymy-like (unrelated
    senses, clean attractor basins -> multi-prototype clustering should recover senses); HIGH =>
    regular polysemy (one graded basin -> clustering over-splits). The pinned split/merge predictor
    (Rodd 2004; Klein & Murphy 2001), used instead of raw synset count."""
    try:
        from nltk.corpus import wordnet as wn
    except Exception:
        return None
    ss = wn.synsets(word)[:6]
    if len(ss) < 2:
        return None
    sims = []
    for i in range(len(ss)):
        for j in range(i + 1, len(ss)):
            try:
                w = ss[i].wup_similarity(ss[j])
            except Exception:
                w = None
            if w is not None:
                sims.append(float(w))
    return float(np.mean(sims)) if sims else None


def sense_splitting_probe(budget: int, run_mode: str, seed: int,
                          taus: Sequence[float] = (0.10, 0.15, 0.20, 0.25),
                          min_count: int = 3) -> dict:
    """PUSH THROUGH THE WALL on the LARGEST slice (polysemy, ~41%). The brain learns multiple senses
    of a word from reading by CLUSTERING contexts into senses (multi-prototype); the incumbent
    single-average blurs them. Test whether online sense-clustering recovers what the average loses:
      (a) COHERENCE recovery -- do DP-means sense-clusters cohere (split-half) where the whole bundle
          does not, ABOVE a random-cluster control at the SAME cluster sizes (kills the 'small sets
          cohere by chance' artifact)?
      (b) CORRECT-GROUNDING recovery -- does per-cluster canonicalize ground a WordNet-correct sense
          the single-bundle misses, WITHOUT dropping precision (the 0.45 anchor gate is unchanged)?
      (c) the PINNED boundary -- does the win concentrate in LOW-inter-sense-relatedness (homonym-like)
          words, as Rodd 2004 / Klein & Murphy 2001 predict, and NOT in high-relatedness polysemes?"""
    from collections import defaultdict as _dd
    cap = capture(budget, run_mode, seed)
    space = cap["state"].space
    pop = cap["consol_fail"]
    try:
        from nltk.corpus import wordnet as wn
        poly = {l: it for l, it in pop.items() if len(wn.synsets(l)) >= 5}
    except Exception:
        poly = {}
    poly_lemmas = sorted(poly)
    rng = np.random.default_rng(4242 + seed)

    def _splithalf(idxs: List[int], traces: List[Trace]) -> Optional[float]:
        if len(idxs) < 4:
            return None
        sub = [traces[i] for i in idxs]
        return schema_consistency_split_half(sub, min_half_size=2)

    results_by_tau = {}
    for tau in taus:
        n_recover = n_single_correct = n_split_any_correct = 0
        n_split_grounded = n_split_correct = 0
        coh_bundle, coh_dp, coh_rand = [], [], []
        recover_by_relatedness = {"low_homonym_like": [0, 0], "high_polyseme_like": [0, 0]}  # [recovered, total]
        for l in poly_lemmas:
            tr = poly[l].traces
            clusters = online_sense_cluster(tr, tau)
            big = [cl for cl in clusters if len(cl) >= min_count]
            # single-bundle (incumbent) grounding + correctness
            raw = np.sum([t.context_vec for t in tr], axis=0)
            sa, _ = _eligible_anchor(raw, l, space)
            single_correct = (sa != l) and bool(_wn_related([(l, sa)]).get((l, sa), False))
            n_single_correct += int(single_correct)
            # sense-split grounding: each qualifying cluster -> its own anchor
            split_pairs = []
            for cl in big:
                cen = np.sum([tr[i].context_vec for i in cl], axis=0)
                ca, _ = _eligible_anchor(cen, l, space)
                if ca != l:
                    split_pairs.append((l, ca))
            rel = _wn_related(split_pairs)
            split_correct_flags = [rel.get(pr, False) for pr in split_pairs]
            n_split_grounded += len(split_pairs)
            n_split_correct += sum(1 for f in split_correct_flags if f)
            split_any_correct = any(split_correct_flags)
            n_split_any_correct += int(split_any_correct)
            recovered = split_any_correct and not single_correct     # strict recovery
            n_recover += int(recovered)
            # coherence: DP clusters vs RANDOM clusters of the SAME sizes vs the whole bundle
            b = _splithalf(list(range(len(tr))), tr)
            if b is not None:
                coh_bundle.append(b)
            perm = list(rng.permutation(len(tr)))
            pos = 0
            for cl in clusters:
                d = _splithalf(cl, tr)
                if d is not None:
                    coh_dp.append(d)
                rnd_idx = perm[pos:pos + len(cl)]; pos += len(cl)
                rc = _splithalf(list(rnd_idx), tr)
                if rc is not None:
                    coh_rand.append(rc)
            # stratify recovery by inter-sense relatedness
            r = _inter_sense_relatedness(l)
            if r is not None:
                key = "low_homonym_like" if r < 0.5 else "high_polyseme_like"
                recover_by_relatedness[key][1] += 1
                recover_by_relatedness[key][0] += int(recovered)
        n = len(poly_lemmas)
        results_by_tau[str(tau)] = {
            "n_polysemous": n,
            "single_bundle_correct_rate": round(n_single_correct / n, 4) if n else None,
            "split_any_correct_rate": round(n_split_any_correct / n, 4) if n else None,
            "recovery_rate_split_correct_where_single_wrong": round(n_recover / n, 4) if n else None,
            "split_precision": round(n_split_correct / n_split_grounded, 4) if n_split_grounded else None,
            "coherence_bundle_mean": round(float(np.mean(coh_bundle)), 4) if coh_bundle else None,
            "coherence_dpmeans_clusters_mean": round(float(np.mean(coh_dp)), 4) if coh_dp else None,
            "coherence_random_clusters_mean": round(float(np.mean(coh_rand)), 4) if coh_rand else None,
            "recovery_by_relatedness": {k: {"recovered": v[0], "total": v[1],
                                            "rate": round(v[0] / v[1], 4) if v[1] else None}
                                        for k, v in recover_by_relatedness.items()},
        }
    return {"budget": budget, "seed": seed, "n_consol_fail": len(pop),
            "n_polysemous_ge5": len(poly_lemmas), "min_count_per_sense": min_count,
            "by_tau": results_by_tau, "capture_elapsed_s": cap["elapsed_s"]}


def _nearest_eligible(query: np.ndarray, anchor_names: List[str], anchor_mat: np.ndarray,
                      self_name: str) -> Tuple[Optional[str], float]:
    """Nearest anchor by cosine, excluding self. anchor_mat rows aligned to anchor_names."""
    q = query / (np.linalg.norm(query) + 1e-12)
    sims = anchor_mat @ q
    best, bc = None, -2.0
    for i, a in enumerate(anchor_names):
        if a == self_name:
            continue
        if sims[i] > bc:
            best, bc = a, float(sims[i])
    return best, bc


def distributional_representation_probe(budget: int, run_mode: str, seed: int) -> dict:
    """PROVE-THE-POINT (constructive representation-bound test). Hold the grounding PROCEDURE fixed
    (assign each word its nearest eligible seed anchor) and vary only the REPRESENTATION:
      BOW  -- the incumbent masked bag-of-content-words bundle (what consolidation actually uses).
      PHI  -- PPMI+SVD over the SAME read's separable co-occurrence (CLS/ATL semantic manifold;
              hdlab.distributional_meaning_channel.ppmi_svd, byte-for-byte the landed math).
    If PHI's nearest-anchor WordNet precision >> BOW's on the SAME CONSOLIDATION_FAIL words, the wall
    is REPRESENTATION-bound and the lever is the meaning representation, not the consolidation scheme.
    Threshold-free (every word gets its nearest anchor) so no gate is tuned per space."""
    import scipy.sparse as sp
    from hdlab.distributional_meaning_channel import _count_matrix, ppmi_svd, SVD_K
    cap = capture(budget, run_mode, seed, route_b=True)
    state = cap["state"]
    space = state.space
    pop = cap["consol_fail"]
    pop_lemmas = sorted(pop)
    counts = space.all_context_counts()                      # lemma -> Counter(context lemma -> n)
    seed_words = cap["seed_words"]
    # eligible seed anchors present in BOTH representations
    anchors = sorted(a for a in space.anchors()
                     if a in seed_words and is_eligible_meaning(a)
                     and space.bundle(a) is not None and counts.get(a))
    embed_words = sorted(set(anchors) | {l for l in pop_lemmas if counts.get(l)})
    vocab_words = sorted({c for w in embed_words for c in counts[w]})
    if len(anchors) < 5 or len(vocab_words) < SVD_K + 5 or len(embed_words) < SVD_K + 5:
        return {"error": "insufficient co-occurrence to build PPMI+SVD at this scale",
                "n_anchors": len(anchors), "n_vocab": len(vocab_words), "n_embed": len(embed_words)}
    vocab = {w: i for i, w in enumerate(vocab_words)}
    M = _count_matrix(embed_words, counts, vocab)
    phi = ppmi_svd(M, svd_k=SVD_K)
    row = {w: i for i, w in enumerate(embed_words)}
    phi_anchor_mat = np.stack([phi[row[a]] for a in anchors], axis=0)
    # BOW anchor matrix (sign bundles, matching canonicalize's query convention)
    bow_anchor_mat = np.stack([np.sign(space.bundle(a)) for a in anchors], axis=0)
    pop_scored = [l for l in pop_lemmas if l in row]
    bow_pairs, phi_pairs = [], []
    for l in pop_scored:
        raw = np.sum([t.context_vec for t in pop[l].traces], axis=0)
        ba, _ = _nearest_eligible(np.sign(raw), anchors, bow_anchor_mat, l)
        pa, _ = _nearest_eligible(phi[row[l]], anchors, phi_anchor_mat, l)
        if ba:
            bow_pairs.append((l, ba))
        if pa:
            phi_pairs.append((l, pa))
    bow_rel = _wn_related(bow_pairs)
    phi_rel = _wn_related(phi_pairs)
    bow_correct = {l: bow_rel.get((l, dict(bow_pairs).get(l)), False) for l in pop_scored}
    phi_correct = {l: phi_rel.get((l, dict(phi_pairs).get(l)), False) for l in pop_scored}
    # paired: over the SAME words, is PHI's nearest anchor correct more often than BOW's?
    n = len(pop_scored)
    both = [(1 if phi_correct[l] else 0) - (1 if bow_correct[l] else 0) for l in pop_scored]
    brng = np.random.default_rng(321 + seed)
    diffs = np.array([np.mean([both[i] for i in brng.integers(0, n, size=n)]) for _ in range(N_BOOT)]) if n else np.array([0.0])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {
        "n_pop_scored": n, "n_anchors": len(anchors), "n_vocab": len(vocab_words), "svd_k": SVD_K,
        "bow_nearest_anchor_precision": round(sum(bow_correct.values()) / n, 4) if n else None,
        "phi_nearest_anchor_precision": round(sum(phi_correct.values()) / n, 4) if n else None,
        "phi_minus_bow": round((sum(phi_correct.values()) - sum(bow_correct.values())) / n, 4) if n else None,
        "phi_minus_bow_ci": [round(float(lo), 4), round(float(hi), 4)],
        "phi_beats_bow_ci_separated": bool(lo > 0),
        "capture_elapsed_s": cap["elapsed_s"],
    }


def self_test() -> dict:
    """Formula self-tests on synthetic traces -- no corpus read."""
    d = N_DIM
    rng = np.random.default_rng(0)
    # a COHERENT word: all traces share a fixed direction + noise -> RETRIEVE should strengthen.
    base = rng.standard_normal(d)
    coh = [Trace(episode_id=f"e{i}", pole="POS",
                 context_vec=np.sign(base + 0.6 * rng.standard_normal(d)), pass_idx=1)
           for i in range(6)]
    # an INCOHERENT word: independent random traces -> RETRIEVE should NOT strengthen.
    inc = [Trace(episode_id=f"e{i}", pole="POS",
                 context_vec=np.sign(rng.standard_normal(d)), pass_idx=1) for i in range(6)]
    m_c, s_c, _ = _retrieve_core(coh, DEFAULT_PARAMS, lambda c, mm, i: _cos(c, mm))
    m_i, s_i, _ = _retrieve_core(inc, DEFAULT_PARAMS, lambda c, mm, i: _cos(c, mm))
    assert s_c > s_i, f"coherent word must strengthen more than incoherent: {s_c} !> {s_i}"
    assert s_c >= DEFAULT_PARAMS["ground_thresh"], f"coherent word must reach ground_thresh: {s_c}"
    # (1-s) ceiling: s never exceeds 1
    assert 0.0 <= s_c <= 1.0 and 0.0 <= s_i <= 1.0
    # EXPOSURE arm folds every context -> its estimate norm >= RETRIEVE's on the incoherent word
    # (RETRIEVE quarantines misses). schema self-test:
    sch = schema_consistency_split_half(coh, min_half_size=2)
    assert sch is not None
    # dev/test split is deterministic + disjoint
    dv, ts = _dev_test_split(["alpha", "beta", "gamma", "delta", "epsilon"], 0)
    assert set(dv).isdisjoint(set(ts))
    return {"selftest_ok": True, "s_coherent": round(float(s_c), 4),
            "s_incoherent": round(float(s_i), 4), "schema_coherent": round(float(sch), 4)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    ap.add_argument("--self-test", dest="selftest", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dist-probe", dest="dist_probe", action="store_true",
                    help="run ONLY the distributional-representation probe (PPMI+SVD vs bag-of-words)")
    ap.add_argument("--sense-probe", dest="sense_probe", action="store_true",
                    help="run ONLY the sense-splitting probe (multi-prototype on the polysemous slice)")
    ap.add_argument("--oracle-probe", dest="oracle_probe", action="store_true",
                    help="run ONLY the oracle anchor-ceiling decomposition (coverage- vs representation-bound)")
    ap.add_argument("--encoder-probe", dest="encoder_probe", action="store_true",
                    help="run ONLY the encoder diagnostic (why the encoder misses anchors that exist)")
    ap.add_argument("--walls-probe", dest="walls_probe", action="store_true",
                    help="run ONLY the read-out/oracle/specificity drills (do-all remaining walls)")
    ap.add_argument("--reranker-probe", dest="reranker_probe", action="store_true",
                    help="run ONLY the read-out re-ranker fix test (nearest vs bg-subtract/reciprocal/abstain)")
    ap.add_argument("--supervised-probe", dest="supervised_probe", action="store_true",
                    help="run ONLY the supervised re-ranker test (is the selection signal extractable?)")
    ap.add_argument("--confirm-all", dest="confirm_all", action="store_true",
                    help="full-scale read-out confirmation: oracle + encoder(+re-rankers) + supervised -> one metrics.json")
    ap.add_argument("--grounded-probe", dest="grounded_probe", action="store_true",
                    help="run ONLY the grounded-hub re-ranker (does sensorimotor+affect grounding SELECT the sense?)")
    ap.add_argument("--fusion-probe", dest="fusion_probe", action="store_true",
                    help="run ONLY the brain-faithful reliability-weighted grounded<->distributional FUSION selector (the full-lift mechanism)")
    ap.add_argument("--grounded-supervised-probe", dest="grounded_supervised_probe", action="store_true",
                    help="run ONLY the grounded-supervised CEILING yardstick (upper bound on extractable grounded sense-signal; NOT a wire)")
    ap.add_argument("--context-gated-probe", dest="context_gated_probe", action="store_true",
                    help="run ONLY the context-gated grounding prototype (occurrence-specific binder_ctx=g(context); the toward-ceiling lever)")
    ap.add_argument("--situation-probe", dest="situation_probe", action="store_true",
                    help="run ONLY the situation-grounding cross-the-wall test (ground each occurrence by the mean Binder of its ACTUAL context words)")
    ap.add_argument("--sense-cluster-probe", dest="sense_cluster_probe", action="store_true",
                    help="run ONLY the per-sense (clustered) grounding prototype (the sense-induction lever toward the ceiling)")
    ap.add_argument("--gloss-probe", dest="gloss_probe", action="store_true",
                    help="run ONLY the per-sense GLOSS grounding prototype (breakthrough lever 1: de-blend via definitions)")
    ap.add_argument("--relational-probe", dest="relational_probe", action="store_true",
                    help="run ONLY the relational taxonomic-graph selector (breakthrough lever 2: change-in-kind; read the seed-shuffle control)")
    ap.add_argument("--sources", type=str, default="", help="comma-separated shelf sources (per-genre)")
    ap.add_argument("--distilled", dest="distilled", action="store_true",
                    help="in --walls-probe, also run the heavy distilled-direction read-out test")
    args = ap.parse_args(argv)
    if args.selftest:
        args.mode = "self-test"
    elif args.smoke:
        args.mode = "smoke"
    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2)); print("SELF-TEST PASSED"); return 0
    if args.dist_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = distributional_representation_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "dist_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.sense_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = sense_splitting_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "sense_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.oracle_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        srcs = [s.strip() for s in args.sources.split(",") if s.strip()] or None
        probe = oracle_anchor_ceiling(budget, run_mode, seed=args.seed, sources=srcs)
        fn = "oracle_probe.json" if not srcs else f"oracle_probe_{'_'.join(srcs)}.json"
        with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.encoder_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = encoder_diagnostic(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "encoder_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.confirm_all:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        res = {"anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": "READOUT_CONFIRM",
               "seed": args.seed, "budget": budget,
               "oracle": oracle_anchor_ceiling(budget, run_mode, seed=args.seed),
               "encoder_and_readouts": encoder_diagnostic(budget, run_mode, seed=args.seed, do_structural=False),
               "supervised": supervised_reranker_probe(budget, run_mode, seed=args.seed),
               "grounded_rerank": grounded_reranker_probe(budget, run_mode, seed=args.seed),
               "grounded_fusion": grounded_fusion_probe(budget, run_mode, seed=args.seed),
               "grounded_supervised_ceiling": grounded_supervised_probe(budget, run_mode, seed=args.seed),
               "ts_iso": datetime.now(timezone.utc).isoformat()}
        tmp = os.path.join(out, "metrics.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, default=str)
        os.replace(tmp, os.path.join(out, "confirm_all.json"))
        print(json.dumps({"oracle_partition": res["oracle"].get("partition_all"),
                          "encoders": [(e["encoder"], e.get("frac_correct_in_top10"))
                                       for e in res["encoder_and_readouts"].get("encoders", [])],
                          "readouts": [(r["readout"], r.get("rank1_correct_over_pop"))
                                       for r in res["encoder_and_readouts"].get("readout_reranking_on_phi", [])],
                          "supervised_lift": res["supervised"].get("lift_over_nearest"),
                          "grounded_lift": res["grounded_rerank"].get("grounded_lift_over_distributional"),
                          "grounded_rank1": res["grounded_rerank"].get("grounded_rerank_rank1_correct"),
                          "fusion_rank1": res["grounded_fusion"].get("rank1_correct"),
                          "fusion_lift_over_DIST": res["grounded_fusion"].get("lift_over_DIST"),
                          "fusion_ci_FUSE_BOTH_minus_DIST": res["grounded_fusion"].get("ci_FUSE_BOTH_minus_DIST"),
                          "fusion_shuffle_control": res["grounded_fusion"].get("ci_SHUF14_minus_DIST_MUST_INCLUDE_0"),
                          "grounded_supervised_ceiling": res["grounded_supervised_ceiling"].get("CEILING_grounded_supervised_rank1")},
                         indent=2, default=str))
        return 0
    if args.grounded_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = grounded_reranker_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "grounded_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.fusion_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = grounded_fusion_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "fusion_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.grounded_supervised_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = grounded_supervised_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "grounded_supervised_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.context_gated_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = context_gated_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "context_gated_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.situation_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = situation_grounding_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "situation_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.sense_cluster_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = sense_cluster_grounding_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "sense_cluster_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.gloss_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = gloss_grounding_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "gloss_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.relational_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = relational_graph_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "relational_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.supervised_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = supervised_reranker_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "supervised_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.reranker_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = readout_reranker_probe(budget, run_mode, seed=args.seed)
        with open(os.path.join(out, "reranker_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    if args.walls_probe:
        run_mode = args.mode
        budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
        out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
        probe = walls_probe(budget, run_mode, seed=args.seed, do_distilled=args.distilled)
        with open(os.path.join(out, "walls_probe.json"), "w", encoding="utf-8") as f:
            json.dump(probe, f, indent=2, default=str)
        print(json.dumps(probe, indent=2, default=str))
        return 0
    run_mode = args.mode
    budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
    out = _output_dir(run_mode); os.makedirs(out, exist_ok=True)
    st = self_test()
    res = run(budget, run_mode, seed=args.seed)
    metrics = {"anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": "MEASURED",
               "verdict_msg": res["headline"], "summary": res["headline"],
               "ts_iso": datetime.now(timezone.utc).isoformat(), "selftest": st, "result": res}
    tmp = os.path.join(out, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, os.path.join(out, "metrics.json"))
    print(json.dumps({k: v for k, v in res.items() if k not in ("sweep_log",)}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
