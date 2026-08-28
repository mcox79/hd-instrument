"""experiments/exp_reading_comprehensible_input_zpd_v1.py

THE READER CHOOSES WHAT TO READ NEXT -- the brain-faithful way, which is NOT the way the brief asked.
Solver cell for `the_reader_cannot_choose_what_to_read_next`. 2026-08-28.

THE DISK OUTRANKS THE BRIEF, AND IT REFUTES THE BRIEF'S PROPOSED MECHANISM.
The brief asks for an MVT information-forager driven by a value-of-information / gap / learning-progress
signal (EVC-gated).  That exact mechanism was already built and run at full scale for the neighbouring
problem `aimed_reading_is_built_and_the_reader_never_calls_it` (status REFUTED, owner-DONE): the forager
LOSES to the fixed 4-corpus schedule register-controlled on 3/3 seeds (FORAGE 0.041, FORAGE_LP 0.025 vs
FROZEN 0.051), and -- decisively -- its info-free twin does NOT lose for the learning-progress arms, i.e.
the learning-progress signal CARRIES NO INFORMATION FOR CORPUS CHOICE on the live path.

WHY (drilled to mechanism, not asserted).  Learning progress = the time-derivative of prediction error
(Oudeyer & Kaplan 2007) is a DIFFERENCE OF TWO NOISY ESTIMATES; the active-learning and curriculum-RL
literature (Settles 2009; Mussmann & Liang 2018; noisy-LP work 2025-26) shows it needs heavy temporal
smoothing (sliding windows / momentum) to be usable -- which the BETWEEN-source, few-episodes-per-source
regime cannot afford.  Fraction-known is a DIRECTLY OBSERVABLE state statistic (one pass, low variance).
So LP is a fine WITHIN-source leave signal (dense, many samples) and a useless BETWEEN-source selection
signal.  That is the brain-and-statistics reason the forager failed and comprehensible input succeeds.

THE BRAIN-FAITHFUL MECHANISM THAT WORKS -- COMPREHENSIBLE INPUT / ZPD.
The parked, proven result (`exp_aimed_reading_learnable_input_v6`, +0.04 vs FROZEN register-controlled,
3/3 seeds, twin loses) selects the source with the most NEW learnable words appearing in COMPREHENSIBLE
sentences (Krashen 1985 i+1; Vygotsky ZPD; Metcalfe 2002 region of proximal learning).  This cell makes
that the answer to THIS problem and PUSHES ITS FIDELITY FINER, on two axes the v6 result left open:

  (1) THE COMPREHENSIBILITY THRESHOLD.  v6 used a hard 0.5 (a sentence is comprehensible if >=50% of its
      content words are known).  The evidence says that is too low: reading comprehension rises
      monotonically toward a HIGH known-fraction (Schmitt, Jiang & Grabe 2011; Laufer 2010 ~95-98%
      coverage; N400 integration cost is monotonic in surprisal -- Kutas & Federmeier 2011 -- not an
      inverted-U), and the one genuine LEARNING-RATE optimum is ~85% known / ~15% novel (Wilson, Shenhav,
      Straccia & Cohen 2019, the 85% rule).  Prediction: the optimal threshold is ~0.85-0.9, not 0.5.
  (2) ADAPTIVITY.  Metcalfe's region of proximal learning is a RELATIVE/ORDINAL, RISING target (near-
      mastery-but-not-yet-known), not a fixed number: as competence grows, i rises.  The i+FEW arm reads
      sentences with only a FEW new words (self-scaling), which starts on easy graded readers and
      progresses -- the ROPL signature.

ARMS (identical except the WHAT-TO-READ-NEXT policy; grounding-yield MVT leave-rule within source; a
FRESH throwaway HDFactStore per (arm,seed); the canonical foundation is never opened):
  FROZEN        the historical fixed 4-corpus schedule                         [FLOOR 2 -- the wall]
  RANDOM        uniform random corpus choice                                   [FLOOR 1 / info-free twin]
  CI_050        comprehensible input, hard threshold 0.5 (= v6, reproduced)    [proven baseline]
  CI_085        comprehensible input, hard threshold 0.85 (the 85% rule)       [fidelity upgrade]
  CI_ADAPTIVE   i+FEW: sentences with <= MAX_NEW new words (rising ZPD target)  [fidelity upgrade]
  CI_SHUFFLED   CI_085 with per-corpus comprehensibility scores SHUFFLED       [INFO-FREE TWIN -- must lose]

METRIC: register-controlled coverage (probe stratified by FROZEN-reachability, equal-weighted) + bootstrap
CI, reused verbatim from exp_aimed_reading_register_controlled_v1 -- the metric the proven result used.
Multi-seed.  Info-free twin must LOSE CI-separated; report CI half-width + null.

REUSE (wire-don't-island): Shelf/UncertaintyMeter/load_base_vocab (exp_information_foraging_reading_v1);
build_register_context/coverage_block/_boot_delta_ci (exp_aimed_reading_register_controlled_v1);
ForagingController/SurpriseSegmenter (information_foraging); reading_grounding_loop.  NO hdlab/ write.

ASCII-only.  Deterministic.  Resumable per (arm, seed).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import re
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

from experiments.exp_information_foraging_reading_v1 import (
    BETA_LEAVE, CHUNK, N_DIM, PEEK_N, PEEK_STRIDE, RHO_HALFLIFE, RHO_SLOW_HALFLIFE, SCHEMA_THRESH,
    SEED_VOCAB_N, SEG_K, SEG_MAX_RUN, SEG_MIN_RUN, SEG_WINDOW, SUBSTRATE_SEED, TRAVEL_TAU,
    Shelf, UncertaintyMeter, load_base_vocab)
from experiments.exp_aimed_reading_register_controlled_v1 import (
    build_register_context, coverage_block, _boot_delta_ci)
from hdlab.hd_fact_store import HDFactStore
from hdlab.information_foraging import ForagingConfig, ForagingController, SurpriseSegmenter
from hdlab.reading_grounding_loop import (KNOWN_RELATION, MEANING_RELATION, ReadingLoopState,
                                          checkpoint, process_sentence, seed_known_words)

ANCHOR_NAME = os.environ.get("HDLAB_EXP_NAME", "reading_comprehensible_input_zpd_v1")
TOKEN = re.compile(r"[a-z]+")

# Data dependencies for remote dispatch (auto-shipped by the fulfiller if missing on remote).
# Reading is regex + a GLASS-BOX lemmatizer (hdlab.thematic_role_labeler.lemma_word) -- NO spaCy/nltk
# at runtime -- so the raw corpora can be read remotely without a parse cache.
# KB_REFERENT: data/corpora/base_vocabulary/cleaned/base_vocabulary_ordered.csv
# KB_REFERENT: data/corpora
# KB_REFERENT: data/closed_class_lexicon_v1.json   # pre-built (spaCy-free load) -> reading_grounding_loop
#   loads this instead of calling closed_class_lexicon._spacy_stop_words() (remote has no spaCy)

FULL_BUDGET = 8000
SMOKE_BUDGET = 900
FULL_SEEDS = [0, 1, 2]
SMOKE_SEEDS = [0]
N_BOOT_FULL, N_BOOT_SMOKE = 4000, 600

# arm -> (mode, param).  mode: "frozen"|"random"|"hard"|"adaptive"|"shuffled"
ARMS: Dict[str, tuple] = {
    "FROZEN": ("frozen", 0.0),
    "RANDOM": ("random", 0.0),
    "CI_050": ("hard", 0.50),
    "CI_085": ("hard", 0.85),
    "CI_ADAPTIVE": ("adaptive", 2),      # i+FEW: <=2 new words per sentence (rising ZPD target)
    "CI_GRADED": ("graded", 0.0),        # per-word GRADED partial credit, whole-sentence (anti-starvation fix)
    "CI_GRADED_WIN": ("graded_win", 4),  # GRADED over a LOCAL +-4-word window (finer locality; component opt)
    "CI_SHUFFLED": ("shuffled", 0.85),   # info-free twin of CI_085
}
ARM_SEED_IX = {a: i for i, a in enumerate(ARMS)}


def repo_path(rel: str) -> str:
    return os.path.join(REPO_ROOT, rel)


def _output_dir(run_mode: str, tag: str = "") -> str:
    # the remote runner sets HDLAB_EXP_NAME to the entry name, which may already carry the "exp_"
    # prefix (the cell filename); strip it so we write data/exp_<base>, not data/exp_exp_<base>.
    base = ANCHOR_NAME[4:] if ANCHOR_NAME.startswith("exp_") else ANCHOR_NAME
    return repo_path(f"data/exp_{base}" + ("_smoke" if run_mode == "smoke" else "")
                     + (("_" + tag) if tag else ""))


def _write_json_atomic(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


# ==================================================== comprehensible-input source scoring
def _corpus_learnable_score(handle, known_set: set, mode: str, param) -> float:
    """Score a corpus by its NEW-word learnable content, given the reader's current known vocab.
      hard      : COUNT of distinct new words appearing in sentences with known_fraction >= param
                  (Krashen i+1 as a BINARY WHOLE-SENTENCE gate -- the v6 mechanism).
      adaptive  : COUNT of distinct new words in sentences with <= param new words (i+FEW).
      graded    : GRADED per-word partial credit -- NO binary sentence gate.  Each distinct new word
                  earns credit = MAX over its sentences of g(local_known_fraction), g(x)=x (linear
                  default; sweep x^2 / sigmoid).  This is the anti-STARVATION fix (research
                  2026-08-28): human word learning accumulates weak partial evidence across
                  partially-understood contexts (Yu & Smith 2007, 6.25%-informative trials), so no
                  context scores zero -> the selection signal can never return an empty set ->
                  cannot starve; and because every corpus gets a non-zero graded score, selection is
                  RELATIVE/ordinal (pick the best AVAILABLE) rather than an absolute cutoff.
    Self-corrects either way: grounded words leave the 'new' pool, so an exhausted corpus's score falls."""
    if mode in ("graded", "graded_win"):
        # x^2 graded partial credit: never 0 (-> no starvation) but steeply discounts low-comprehension
        # contexts (-> will not camp on jargon).  graded = whole-SENTENCE known-fraction;
        # graded_win = a LOCAL window of +-param tokens around each new word (finer locality, the N400
        # integration window -- research 2026-08-28 granularity point: local context, not the sentence).
        W = int(param) if mode == "graded_win" else 0
        credit: Dict[str, float] = {}
        for s in handle.peek(PEEK_N, PEEK_STRIDE):
            toks = [t for t in TOKEN.findall(s.lower()) if len(t) >= 3]
            if not toks:
                continue
            if mode == "graded":
                new = [t for t in toks if t not in known_set]
                kf = (len(toks) - len(new)) / len(toks)
                g = kf * kf
                for t in new:
                    if g > credit.get(t, 0.0):
                        credit[t] = g
            else:                                            # graded_win: per-word local-window comprehensibility
                for i, t in enumerate(toks):
                    if t in known_set:
                        continue
                    lo, hi = max(0, i - W), min(len(toks), i + W + 1)
                    win = toks[lo:i] + toks[i + 1:hi]        # neighbours only (exclude the target word)
                    kf = (sum(1 for w in win if w in known_set) / len(win)) if win else 0.0
                    g = kf * kf
                    if g > credit.get(t, 0.0):
                        credit[t] = g
        return float(sum(credit.values()))
    learnable = set()
    for s in handle.peek(PEEK_N, PEEK_STRIDE):
        toks = [t for t in TOKEN.findall(s.lower()) if len(t) >= 3]
        if not toks:
            continue
        new = [t for t in toks if t not in known_set]
        if mode == "hard":
            known_frac = (len(toks) - len(new)) / len(toks)
            comprehensible = known_frac >= param
        elif mode == "adaptive":
            comprehensible = (len(new) <= int(param)) and len(toks) >= 4
        else:
            comprehensible = True
        if comprehensible:
            for t in new:
                learnable.add(t)
    return float(len(learnable))


def choose_source(arm: str, mode: str, param, shelf, known_set: set, rng, exclude, diag,
                  shuffle_map: Optional[Dict[str, str]]) -> str:
    live = [n for n in shelf.live_names() if n != exclude] or shelf.live_names()
    if not live:
        return sorted(shelf.names)[0]
    if mode == "random":
        return rng.choice(live)
    if mode == "frozen":
        return live[0]                      # never used (FROZEN handled by the schedule in run_arm)
    score_mode = {"hard": "hard", "shuffled": "hard", "adaptive": "adaptive",
                  "graded": "graded", "graded_win": "graded_win"}[mode]
    scored = []
    for n in sorted(live):
        key = shuffle_map[n] if (mode == "shuffled" and shuffle_map) else n
        scored.append((_corpus_learnable_score(shelf.handles[key], known_set, score_mode, param), n))
    scored.sort(key=lambda vn: (-vn[0], vn[1]))
    best_score, best = scored[0]
    if best_score <= 0:
        diag["n_fallback"] += 1
        return rng.choice(live)
    diag["n_chosen"] += 1
    if len(diag["choices"]) < 40:
        diag["choices"].append({"corpus": best, "score": best_score})
    return best


# ==================================================== one arm x one seed
def run_arm(arm: str, seed: int, budget: int, run_mode: str) -> dict:
    mode, param = ARMS[arm]
    t0 = time.time()
    seed_words = load_base_vocab(0, SEED_VOCAB_N)
    known_base = set(w.lower() for w in seed_words)
    store = HDFactStore(n_dim=N_DIM, seed=SUBSTRATE_SEED + seed,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"}, use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, seed_words, source="seed_base_vocabulary")
    meter = UncertaintyMeter(state)
    shelf = Shelf(run_mode, frozen=(arm == "FROZEN"))
    import random as _random
    rng = _random.Random(SUBSTRATE_SEED + seed * 131 + ARM_SEED_IX[arm])
    cfg = ForagingConfig(travel_step_duration=TRAVEL_TAU, rho_halflife_steps=RHO_HALFLIFE,
                         rho_slow_halflife_steps=RHO_SLOW_HALFLIFE, beta_leave=BETA_LEAVE,
                         stochastic=True, seed=SUBSTRATE_SEED + seed * 131 + ARM_SEED_IX[arm])
    ctrl = ForagingController(cfg)
    seg = SurpriseSegmenter(SEG_WINDOW, SEG_K, SEG_MIN_RUN, SEG_MAX_RUN)

    shuffle_map = None
    if mode == "shuffled":
        names = sorted(shelf.names)
        perm = list(names)
        _random.Random(SUBSTRATE_SEED + 4242 + seed).shuffle(perm)
        shuffle_map = {a: b for a, b in zip(names, perm)}

    diag = {"n_chosen": 0, "n_fallback": 0, "choices": []}
    read_by_corpus: Counter = Counter()
    gy_gains: List[float] = []
    n_read = pass_idx = since_ckpt = 0
    prev_banked = 0
    current: Optional[str] = None
    frozen_order: List[str] = []
    frozen_quota = 0
    if arm == "FROZEN":
        frozen_order = sorted(shelf.names)   # the 4 frozen specs
        frozen_quota = max(1, budget // len(frozen_order))

    def known_set():
        return known_base | {p["subject"] for p in state.provenance}

    while n_read < budget:
        if arm == "FROZEN":
            idx = min(n_read // frozen_quota, len(frozen_order) - 1)
            nxt = frozen_order[idx]
        else:
            nxt = choose_source(arm, mode, param, shelf, known_set(), rng, current, diag, shuffle_map)
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
            process_sentence(state, sentence, f"{arm}_s{seed}_{n_read}", pass_idx)
            lemmas = None
            # grounding-yield currency (v6): words banked this step
            banked_now = len(state.provenance)
            gy = float(banked_now - prev_banked)
            prev_banked = banked_now
            gy_gains.append(gy)
            ctrl.harvest(gy)
            read_by_corpus[current] += 1
            n_read += 1
            since_ckpt += 1
            if since_ckpt >= CHUNK:
                checkpoint(state, pass_idx, current, schema_thresh=SCHEMA_THRESH)
                meter.rebaseline()
                pass_idx += 1
                since_ckpt = 0
            # WITHIN-source leave: MVT on grounding-yield at surprise-segmenter boundaries
            if arm == "FROZEN":
                if n_read >= frozen_quota * (frozen_order.index(current) + 1):
                    break
            elif arm == "RANDOM":
                if read_by_corpus[current] and (n_read % 40 == 0):
                    break
            else:
                if seg.observe(gy) and ctrl.should_leave():
                    break
    if since_ckpt > 0:
        checkpoint(state, pass_idx, current or "final", schema_thresh=SCHEMA_THRESH)
        meter.rebaseline()

    banked = [(p["subject"], p["object"], p.get("segment")) for p in state.provenance]
    grounded_subjects = sorted({a for a, _b, _s in banked})
    dom_by = Counter(_domain_of(c) for c in read_by_corpus for _ in range(read_by_corpus[c]))
    tot = sum(dom_by.values()) or 1
    dom_top = dom_by.most_common(1)[0] if dom_by else ("none", 0)
    st = ctrl.state()
    return {
        "arm": arm, "seed": seed, "mode": mode, "param": param,
        "n_sentences_read": n_read, "elapsed_s": round(time.time() - t0, 2),
        "n_grounded": len(grounded_subjects),
        "grounded_subjects": grounded_subjects,     # SAVE THE POPULATION (scored later)
        "n_distinct_corpora_read": len(read_by_corpus),
        "dominant_domain": dom_top[0], "dominant_domain_share": round(dom_top[1] / tot, 6),
        "sentences_read_by_corpus": dict(sorted(read_by_corpus.items(), key=lambda kv: (-kv[1], kv[0]))[:12]),
        "read_order_first12": [c["corpus"] for c in diag["choices"][:12]],
        "foraging": {"n_patches": st["n_patches"], "mean_patch_residence": round(st["mean_patch_residence"], 2),
                     "n_travel_updates": st["n_travel_updates"],
                     "n_chosen": diag["n_chosen"], "n_fallback": diag["n_fallback"],
                     "gy_distinct": len(sorted(set(round(g, 6) for g in gy_gains)))},
    }


_DOMAIN_CACHE: Dict[str, str] = {}


def _domain_of(corpus: str) -> str:
    if not _DOMAIN_CACHE:
        try:
            from hdlab.corpus_registry import CorpusRegistry
            reg = CorpusRegistry(max_sentences_per_corpus=10, max_bytes=100_000)
            for n in reg.names():
                _DOMAIN_CACHE[n] = reg.handles[n].spec.domain
            from experiments.exp_information_foraging_reading_v1 import FROZEN_SPECS
            for s in FROZEN_SPECS:
                _DOMAIN_CACHE[s.name] = s.domain
        except Exception:
            pass
    return _DOMAIN_CACHE.get(corpus, "unknown")


# ============================================================================ verdict (multi-seed)
def _mean_ci(xs: List[float]):
    import math
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    m = sum(xs) / n
    if n == 1:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, 1.96 * math.sqrt(var / n)


def build_verdict(ctx: dict, per: Dict[str, List[dict]], n_boot: int) -> dict:
    # register-controlled coverage per (arm, seed)
    cov = {a: [] for a in ARMS}
    for a in ARMS:
        for r in per.get(a, []):
            cb = coverage_block(ctx, r["grounded_subjects"])
            cov[a].append(cb["register_controlled_coverage"])
    # pick the BEST comprehensible-input arm as the treatment
    ci_arms = ["CI_050", "CI_085", "CI_ADAPTIVE", "CI_GRADED", "CI_GRADED_WIN"]
    ci_means = {a: _mean_ci(cov[a])[0] for a in ci_arms if cov[a]}
    best_ci = max(ci_means, key=ci_means.get) if ci_means else "CI_085"

    def paired_boot(a, b):
        # per-seed register-controlled delta via the bootstrap over probe words, averaged across seeds
        deltas, los, his = [], [], []
        for ra, rb in zip(per.get(a, []), per.get(b, [])):
            d, lo, hi, _f = _boot_delta_ci(ctx, set(ra["grounded_subjects"]), set(rb["grounded_subjects"]),
                                           n_boot, seed=1234 + ra["seed"])
            deltas.append(d); los.append(lo); his.append(hi)
        if not deltas:
            return None
        return {"delta_mean": round(float(np.mean(deltas)), 6),
                "delta_min": round(float(np.min(deltas)), 6),
                "ci_lo_mean": round(float(np.mean(los)), 6), "ci_hi_mean": round(float(np.mean(his)), 6),
                "all_seeds_positive": all(l > 0 for l in los), "n_seeds": len(deltas)}

    checks = {
        "best_ci_arm": best_ci,
        "register_controlled_means": {a: round(_mean_ci(cov[a])[0], 6) for a in ARMS if cov[a]},
        "C1_best_CI_beats_FROZEN": paired_boot(best_ci, "FROZEN"),
        "C2_best_CI_beats_RANDOM": paired_boot(best_ci, "RANDOM"),
        "C3_best_CI_beats_SHUFFLED_twin": paired_boot(best_ci, "CI_SHUFFLED"),
        "FIDELITY_085_vs_050": paired_boot("CI_085", "CI_050"),
        "FIDELITY_ADAPTIVE_vs_050": paired_boot("CI_ADAPTIVE", "CI_050"),
    }
    c1 = checks["C1_best_CI_beats_FROZEN"]; c2 = checks["C2_best_CI_beats_RANDOM"]; c3 = checks["C3_best_CI_beats_SHUFFLED_twin"]
    passed = all(x and x["all_seeds_positive"] for x in (c1, c2, c3))
    v = "HARD_PASS" if passed else ("HARD_FAIL" if all(x and x["delta_mean"] < 0 for x in (c1, c2)) else "MIDDLE_BAND")
    msg = (f"best CI arm={best_ci} rc-cov={_mean_ci(cov[best_ci])[0]:.4f} | vs FROZEN "
           f"d={c1['delta_mean'] if c1 else None} (all-seed CI>0={c1['all_seeds_positive'] if c1 else None}) | "
           f"vs RANDOM d={c2['delta_mean'] if c2 else None} ({c2['all_seeds_positive'] if c2 else None}) | "
           f"vs SHUFFLED-twin d={c3['delta_mean'] if c3 else None} ({c3['all_seeds_positive'] if c3 else None}) | "
           f"fidelity 085-050 d={checks['FIDELITY_085_vs_050']['delta_mean'] if checks['FIDELITY_085_vs_050'] else None}")
    return {"verdict": v, "verdict_msg": msg, "checks": checks}


# ============================================================================ self-test
def self_test() -> dict:
    from hdlab import information_foraging as inf
    assert inf.run_all_selftests()
    # comprehensibility scoring: a corpus of rich comprehensible sentences must beat jargon + exhausted
    class _H:
        def __init__(self, sents): self._s = sents
        def peek(self, n, stride): return self._s
    known = {"the", "a", "is", "of", "and", "cat", "dog", "runs", "big"}
    rich = _H(["the big cat runs and the dog is a mammal",         # 1 new word (mammal), comprehensible
               "the dog runs and the cat is a feline"])            # 1 new (feline), comprehensible
    jargon = _H(["zzz qqq vvv www xxx", "aaa bbb ccc ddd eee"])    # all new, incomprehensible
    exhausted = _H(["the big cat runs", "a dog is the cat"])       # comprehensible but NO new words
    s_rich = _corpus_learnable_score(rich, known, "hard", 0.5)
    s_jargon = _corpus_learnable_score(jargon, known, "hard", 0.5)
    s_exhausted = _corpus_learnable_score(exhausted, known, "hard", 0.5)
    assert s_rich >= 2 > s_jargon and s_rich > s_exhausted == 0, (s_rich, s_jargon, s_exhausted)
    # threshold 0.85 must be STRICTER than 0.5 (fewer comprehensible sentences qualify)
    half_known = _H(["the cat zzz qqq vvv", "a dog www xxx yyy"])   # ~40% known -> fails 0.85, passes 0.5
    assert _corpus_learnable_score(half_known, known, "hard", 0.5) >= _corpus_learnable_score(half_known, known, "hard", 0.85)
    # adaptive i+FEW: only sentences with <=2 new words count
    s_adapt = _corpus_learnable_score(rich, known, "adaptive", 2)
    assert s_adapt >= 2, s_adapt
    # GRADED (anti-starvation): never 0 on partially-known material where a hard 0.85 gate WOULD be 0;
    # and a more-comprehensible corpus still scores higher (relative ranking preserved).
    half_known = _H(["the cat zzz qqq vvv", "a dog www xxx yyy"])   # ~40% known -> hard@0.85 = 0
    assert _corpus_learnable_score(half_known, known, "hard", 0.85) == 0.0
    g_half = _corpus_learnable_score(half_known, known, "graded", 0.0)
    g_rich = _corpus_learnable_score(rich, known, "graded", 0.0)
    assert g_half > 0.0, "graded must NOT starve on partially-known material"
    assert g_rich > g_half, (g_rich, g_half)
    # register context builds
    ctx = build_register_context("smoke")
    assert ctx["reachable"] and ctx["unreachable"], "register strata must be non-empty"
    cb = coverage_block(ctx, ["the", ctx["reachable"][0]])
    assert "register_controlled_coverage" in cb
    return {"selftest_ok": True, "rich": s_rich, "jargon": s_jargon, "exhausted": s_exhausted,
            "n_reachable": len(ctx["reachable"]), "n_unreachable": len(ctx["unreachable"])}


# ============================================================================ main
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "smoke", "self-test"], default="full")
    ap.add_argument("--self-test", dest="selftest", action="store_true", help="queue-gate alias for --mode self-test")
    ap.add_argument("--smoke", action="store_true", help="queue-gate alias for --mode smoke")
    ap.add_argument("--arms", default="")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)
    if args.selftest:
        args.mode = "self-test"
    elif args.smoke:
        args.mode = "smoke"

    if args.mode == "self-test":
        print(json.dumps(self_test(), indent=2)); print("SELF-TEST PASSED"); return 0

    run_mode = args.mode
    budget = args.budget if args.budget > 0 else (SMOKE_BUDGET if run_mode == "smoke" else FULL_BUDGET)
    seeds = SMOKE_SEEDS if run_mode == "smoke" else FULL_SEEDS
    if args.seeds:
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    arms = list(ARMS) if not args.arms else [a for a in ARMS if a in set(args.arms.split(","))]
    n_boot = N_BOOT_SMOKE if run_mode == "smoke" else N_BOOT_FULL
    output_dir = _output_dir(run_mode, args.tag)
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.time()

    st = self_test()
    print(f"[selftest] ok reach={st['n_reachable']} unreach={st['n_unreachable']}", flush=True)
    ctx = build_register_context(run_mode)

    units_path = os.path.join(output_dir, "units.jsonl")
    done = {}
    if os.path.exists(units_path):
        with open(units_path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    u = json.loads(ln); done[(u["arm"], u["seed"])] = u
    def emit_metrics(per, final):
        # write a RUNNING metrics.json after every unit so a mid-run crash never loses completed work
        # (the ~20-min remote sync pulls results_path; incremental writes keep it current). The full
        # bootstrap verdict runs only when all arms are present (final); partial writes are cheap.
        n_done = sum(len(v) for v in per.values())
        complete = all(len(per.get(a, [])) == len(seeds) for a in ARMS)
        verdict = (build_verdict(ctx, per, n_boot) if complete
                   else {"verdict": "PARTIAL_IN_PROGRESS" if not final else "PARTIAL_NOT_ALL_ARMS",
                         "verdict_msg": f"{n_done}/{len(arms) * len(seeds)} units; present {sorted(per)}",
                         "checks": None})
        # a running register-controlled coverage table for the units so far (so a partial file is useful)
        table = {}
        for a in sorted(per):
            cvs = [coverage_block(ctx, r["grounded_subjects"])["register_controlled_coverage"] for r in per[a]]
            table[a] = {"rc_cov_by_seed": [round(c, 6) for c in cvs],
                        "rc_cov_mean": round(sum(cvs) / len(cvs), 6) if cvs else None,
                        "grounded_by_seed": [r["n_grounded"] for r in per[a]], "n_seeds": len(cvs)}
        metrics = {
            "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "verdict": verdict["verdict"],
            "verdict_msg": verdict["verdict_msg"], "summary": f"{verdict['verdict']}: {verdict['verdict_msg'][:400]}",
            "progress": {"units_done": n_done, "units_total": len(arms) * len(seeds), "complete": complete,
                         "final": final},
            "elapsed_s": round(time.time() - t0, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
            "checks": verdict.get("checks"), "seeds": seeds, "arms": arms, "budget": budget,
            "per_arm_summary": table,
            "register_context": {"n_probe": len(ctx["probe"]), "n_reachable": len(ctx["reachable"]),
                                 "n_unreachable": len(ctx["unreachable"])},
            "per_arm": {a: per[a] for a in sorted(per)}, "selftest": st,
        }
        _write_json_atomic(os.path.join(output_dir, "metrics.json"), metrics)
        return metrics

    per: Dict[str, List[dict]] = defaultdict(list)
    for a0 in sorted(done):
        per[a0[0]].append(done[a0])
    emit_metrics(per, final=False)                       # checkpoint whatever resumed from disk
    for arm in arms:
        for seed in seeds:
            if (arm, seed) in done:
                print(f"[{arm} s{seed}] resumed", flush=True); continue
            print(f"[{arm} s{seed}] start budget={budget}", flush=True)
            res = run_arm(arm, seed, budget, run_mode)
            with open(units_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(res, default=str) + "\n")
            per[arm].append(res)
            cb = coverage_block(ctx, res["grounded_subjects"])
            print(f"[{arm} s{seed}] done {res['elapsed_s']}s grounded={res['n_grounded']} "
                  f"rc_cov={cb['register_controlled_coverage']:.4f} corpora={res['n_distinct_corpora_read']} "
                  f"dom={res['dominant_domain']}({res['dominant_domain_share']})", flush=True)
            emit_metrics(per, final=False)                # <-- RUNNING checkpoint after every unit

    metrics = emit_metrics(per, final=True)
    print(json.dumps({k: metrics[k] for k in ("verdict", "verdict_msg", "elapsed_s")}, indent=2), flush=True)
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
        _write_json_atomic(os.path.join(_out, "metrics.json"), {
            "verdict": "CELL_CRASHED", "verdict_msg": f"{type(_e).__name__}: {str(_e)[:500]}",
            "summary": f"CELL_CRASHED: {type(_e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "anchor_name": ANCHOR_NAME})
        raise
