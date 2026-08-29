"""exp_learner_safety_gate_v1 -- BAR #4 SAFETY GATE for
notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/PROBLEM.md.

QUESTION (owner's emphatic requirement, BAR #4): before the reader is ever allowed to GROW its own meaning
by reading, prove (a) growing IMPROVES a DOWNSTREAM comprehension score, (b) the gain is the REAL learned
grammatical structure and not just "more tokens processed" (an info-free growth control -- same tokens,
destroyed grammar -- must NOT help), and (c) quantify the CORRUPTION risk: does growing ever DEGRADE a
meaning the substrate had RIGHT before?

PRIOR-WORK CHECK (tools/experiment_index.py query "corruption" / "grows" / "safety" -- substrate_query.sh
returns zero bytes per the 2026-08-18 audit, so the replacement tool was used): the closest hit is
`exp_coherence_filter_foundation_growth_safety_precheck_v1` (MIDDLE_BAND) -- but that tests whether
FILTERING raw-reader EXTRACTIONS (an LCCP structural-consolidation gate) improves precision before
consolidation; it is a different mechanism (a classifier gate on triples) answering a different question. No
prior cell asks whether GROWING THE TOKEN BUDGET of the distributional SIMILARITY learner (5M -> 15M tokens)
improves a downstream comprehension score or ever corrupts a previously-correct meaning. This cell is novel,
not a rediscovery.

DOWNSTREAM TASK (reused verbatim -- same gold, same construction, same source cache -- as the landed
exp_meaning_channel_paraphrase_comprehension_v1): LitBank who-did-what verb-paraphrase retrieval. Per
document (data/litbank/who_did_what_events.json, 100 docs), the candidate set = that document's distinct
governing verbs (gov_verb per mention, alpha, len>=3, >=3 candidates). For each candidate `target`, the
QUERY is a WordNet verb-synonym of `target` that is a DIFFERENT lemma and NOT already a candidate string (a
true paraphrase probe: "pursue" queried when the story said "chased"). Prediction = argmax_c
similarity(query, candidate_c); accuracy = pred == target. Exact string match on the query is 0 by
construction (q != target), so this task STRUCTURALLY requires a semantic/associative read-out -- exactly
what the learner produces, and exactly the who-did-what comprehension axis BAR #4 names.

THE LEARNED READ-OUT (reused verbatim from experiments.exp_structured_context_learner_v1, NOT modified):
SELPREF -- the McRae verb selectional-preference PPMI-SVD vector (verb row x (argument-slot, filler)
column). SELPREF is the verb-centric arm and already beat WIN2/DEP_TYPED CI-separated on SimVerb (the
closest existing benchmark to this task's verb-verb axis; the landed 15M-token full run:
SELPREF rho=0.1481 vs WIN2 rho=0.0844 vs DEP_TYPED rho=0.1186 -- data/exp_structured_context_learner_v1/
metrics.json), so it is the correct read-out for THIS verb-paraphrase task per the brief's own guidance
("if the task is verb-centric use SELPREF for verb-verb"). similarity(cue, candidate) = cosine of the SVD
vectors; None if OOV or all-zero SELPREF row (no argument-slot edges observed for that verb).

ARMS (all scored on the SAME downstream task, SAME items -- see coverage handling below):
  BASELINE_SMALL   : SELPREF learned on the FIRST 5,000,000 simplewiki tokens (pre-growth substrate).
  GROWN_LARGE      : SELPREF learned on the FIRST 15,000,000 simplewiki tokens (grew by reading 3x more of
                     the SAME stream, SAME pipeline -- ONE variable: token budget).
  INFO_FREE_GROWTH : SELPREF-domain-MATCHED info-free twin, learned on the SAME 15,000,000 tokens, the SAME
                     verb-headed argument-slot edges as GROWN_LARGE, but the ARGUMENT-SLOT LABELS
                     (nsubj/dobj/...) are globally PERMUTED ACROSS edges before counting -- same edge
                     count (at min_count=1), same fillers, same verb rows, destroyed only the
                     role<->filler CORRESPONDENCE. This is the exact "KILLER twin" construction discipline
                     of exp_structured_context_learner_v1.build_labelshuffle_cooc (shuffle the label
                     SEQUENCE across a deterministic edge stream, 2-pass memory-light regeneration), here
                     RE-IMPLEMENTED restricted to SELPREF's own verb-argument-slot edge population instead
                     of the general all-deprel population build_labelshuffle_cooc uses -- so
                     BASELINE/GROWN/INFO_FREE differ in EXACTLY one variable (correct vs shuffled labels,
                     identical edges), matching the SAME representation family used for the real arms. Same
                     tokens read, same amount of "growth" writing -- if this arm helps as much as
                     GROWN_LARGE, the win is corpus size / more writing, not real grammar.
  CONCEPTUAL (ref) : hdlab.conceptual_meaning.ConceptualChannel.similarity(q,'V',c,'V') -- the incumbent
                     landed WordNet-grounded identity channel, for CONTEXT ONLY (not part of the safety
                     gate; this problem does not touch or re-validate that organ).
  RANDOM (floor)   : random dense vectors over the union vocab, cosine similarity (info-free; must lose).

COVERAGE (handled honestly per the assignment): CORE_COMMON = items where BASELINE_SMALL, GROWN_LARGE AND
INFO_FREE_GROWTH all produce a defined (non-None) argmax prediction -- this is the GATE population (STEP 3
deltas + STEP 4 corruption rate use ONLY this set, so all three arms are compared on literally identical
items). CONCEPTUAL and RANDOM are scored on their own achievable subset OF THAT SAME CORE_COMMON population
(reported coverage n + fraction) rather than shrinking the GATE population for two reference/floor arms that
are not part of the pass/fail decision.

GATE (BAR #4a/4b, both required for SAFE_TO_GROW):
  (a) GROWN_LARGE beats BASELINE_SMALL, CI-separated on the matched-pairs bootstrap accuracy delta (growing
      by reading DOES improve downstream comprehension).
  (b) INFO_FREE_GROWTH does NOT beat BASELINE_SMALL CI-separated (the gain in (a) is the real learned
      grammatical structure, not the act of processing/writing more tokens).
SAFETY NUMBER (BAR #4c, always reported regardless of gate outcome): among CORE_COMMON items BASELINE_SMALL
  gets RIGHT, the fraction GROWN_LARGE gets WRONG (corruption_right_to_wrong) + bootstrap CI; the reverse
  (recovery_wrong_to_right) reported for context.

A rigorous NEGATIVE (gate fails) is a valid PASS for this cell -- it means "not safe to turn growth on yet",
which is exactly the question BAR #4 asks.

EXTENSION (2026-08-28, coordinator review of the first run): the first run's INFO_FREE_LABELSHUF twin
(shuffle argument-slot LABELS, keep the true (verb,filler) edge) turned out to be a WEAK ablation -- it
preserves true selectional co-occurrence (which verb pairs with which filler in SOME role), so it is not
GENUINELY info-free, and it also beat BASELINE_SMALL CI-separated. Two additions close this gap:
  INFO_FREE_FILLERSHUF : the strict complement -- keep the TRUE argument-slot label + verb, shuffle the
                         FILLER across edges (destroys selectional structure, keeps role/grammar labels).
  INFO_FREE_FULLSHUF   : the GENUINELY info-free control -- SELPREF's own dependency structure is not
                         meaningful once co-occurrence itself is destroyed, so this arm is a WIN2
                         window-PPMI-SVD built on a GLOBALLY TOKEN-SHUFFLED 15M corpus (reusing
                         S.build_cooc(..., shuffle_seed=...), the SAME shuffle mechanism the landed
                         exp_structured_context_learner_v1 uses for its own SHUF_CORPUS control) -- ALL
                         co-occurrence is destroyed, only unigram marginals survive. Expected near RANDOM.
CLEAN GATE B (supersedes the first run's label-shuffle gate for the pass/fail call, per coordinator
instruction): FULLSHUF must NOT beat BASELINE_SMALL CI-separated, AND GROWN_LARGE must beat FULLSHUF
CI-separated (real structure adds value over the clean info-free floor, not just over a partial ablation).
CORRUPTION BY CONFIDENCE: among BASELINE_SMALL-correct items, split by the baseline arm's OWN prediction
confidence (top-vs-2nd-candidate margin) at the median; report the right->wrong corruption rate separately
for the confident half and the low-margin half -- concentration in the low-margin half would support a
confidence-gated growth mitigation; a comparable rate in the confident half means genuine knowledge loss.

DATA-INTEGRITY FINDING (verified live before the full run, see cache_path()/_cache_has_verb_tags()): of the
4 pre-existing data/exp_structured_context_learner_v1/parsed_simplewiki_*tok.jsonl caches, the 150000tok and
5000000tok caches were written BEFORE the attribute_ruler fix that module's own parse_and_cache() docstring
warns about ("disabling it leaves pos_ EMPTY, which silently broke the SELPREF verb arm") -- confirmed: 0
VERB tags in an 85k-token sample of each, vs 8418/85292 for the 300000tok and 15000000tok caches (built
after the fix). A stale cache makes build_selpref_cooc silently return ZERO columns (BASELINE_SMALL would
have 0 coverage, exactly what smoke first showed). This cell checks cache validity before trusting it and,
if stale, regenerates a POS-CORRECTED cache into ITS OWN data dir via the same (already-fixed)
S.parse_and_cache -- it never overwrites the shared stale files in data/exp_structured_context_learner_v1/.

Run:  .venv/Scripts/python.exe experiments/exp_learner_safety_gate_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_learner_safety_gate_v1.py --mode smoke   (150k/300k-tok caches)
      .venv/Scripts/python.exe experiments/exp_learner_safety_gate_v1.py --mode full    (5M/15M-tok caches; the BAR #4 run)

Reuses (READ-ONLY imports, nothing below is modified): experiments.exp_structured_context_learner_v1
(load_parsed, token_sents, build_vocab, build_selpref_cooc, build_cooc, ppmi_matrix, svd_vectors,
dense_vec_cosine_fn, random_vec_cosine_fn, ARG_SLOTS, CTX_MIN_COUNT, SVD_K, _build_from_edges -- used to
build the matched label-/filler-shuffle twins and the full-corpus-shuffle control),
experiments.exp_meaning_channel_paraphrase_comprehension_v1 (_verb_synonym, and via it H.load_cache() --
the SAME gold paraphrase-item construction), hdlab.conceptual_meaning.ConceptualChannel (reference arm
only). Does NOT modify hdlab/, data/foundation/, the baseline cell, or any other experiment cell. Does NOT
turn on foundation growth -- this is a validation-only harness (default-off by construction: it never
writes to data/foundation or hdlab/).

ASCII only. Writes ONLY to data/exp_learner_safety_gate_v1/.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
from array import array as _arr

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
if os.path.join(REPO_ROOT, "experiments") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))

import experiments.exp_structured_context_learner_v1 as S           # noqa: E402  (READ-ONLY reuse)
import experiments.exp_meaning_channel_paraphrase_comprehension_v1 as P  # noqa: E402  (READ-ONLY reuse)
from hdlab.conceptual_meaning import ConceptualChannel               # noqa: E402  (READ-ONLY reuse)

ANCHOR = "learner_safety_gate_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR)
LEARNER_CACHE_DIR = os.path.join(REPO_ROOT, "data", "exp_structured_context_learner_v1")
SEED = 20260827

MODE_CFG = {
    # smoke: small ALREADY-CACHED parses, fast correctness check of the mechanism (not the BAR #4 claim).
    # ctx_min_count is LOWERED from S.CTX_MIN_COUNT(=5) because at 150k/300k tokens almost no
    # (arg-slot, filler) column reaches 5 occurrences -- SELPREF would have 0 columns at smoke scale with
    # the full-run threshold (measured: cols=0 at min_count=5, 150k tok). This is a smoke-scale artifact,
    # not part of the BAR #4 claim (the full run uses the real S.CTX_MIN_COUNT).
    "smoke": {"small_tok": 150_000, "large_tok": 300_000, "vocab_cap": 15_000, "min_count": 3,
              "ctx_min_count": 1, "n_boot": 300},
    # full: the BAR #4 run -- the ALREADY-CACHED 5M / 15M simplewiki parses (no re-parsing needed).
    "full": {"small_tok": 5_000_000, "large_tok": 15_000_000, "vocab_cap": 60_000, "min_count": 8,
              "ctx_min_count": S.CTX_MIN_COUNT, "n_boot": 2000},
}


def _cache_has_verb_tags(path, sample_tokens=50_000):
    """DATA-INTEGRITY CHECK (found live, 2026-08-28): some of the pre-existing
    data/exp_structured_context_learner_v1/parsed_simplewiki_*tok.jsonl caches were written BEFORE the
    attribute_ruler fix noted in that module's own parse_and_cache() docstring ("disabling it leaves pos_
    EMPTY, which silently broke the SELPREF verb arm") -- confirmed on disk: the 150000tok and 5000000tok
    caches have upos=='' on EVERY token (0 VERB tags in the first 85k tokens sampled), while the 300000tok
    and 15000000tok caches have the correct tags (8418/85292 VERB in the same sample). A stale cache makes
    S.build_selpref_cooc silently return ZERO columns (the exact SCRIPT_PRECONDITION_VIOLATION failure
    mode) -- this checks BEFORE trusting a cache, not after a silent empty-arm result."""
    ntok = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            for tok in rec:
                ntok += 1
                if tok[3] == "VERB":
                    return True
            if ntok >= sample_tokens:
                break
    return False


def own_stale_fixed_cache_path(tok):
    return os.path.join(OUTPUT_DIR, "parsed_simplewiki_%dtok_posfixed.jsonl" % tok)


def cache_path(tok):
    """Prefer the SHARED pre-existing cache (read-only) if it has real POS tags; if it is stale (see
    _cache_has_verb_tags), regenerate a CORRECTED cache into THIS CELL'S OWN data dir (never touches/
    overwrites the shared stale file in data/exp_structured_context_learner_v1/) using the SAME
    (already-fixed) S.parse_and_cache pipeline, so the SELPREF read-out is built from real dependency
    parses at both corpus sizes."""
    shared = os.path.join(LEARNER_CACHE_DIR, "parsed_simplewiki_%dtok.jsonl" % tok)
    if os.path.exists(shared) and _cache_has_verb_tags(shared):
        return shared
    own = own_stale_fixed_cache_path(tok)
    if not os.path.exists(own) or not _cache_has_verb_tags(own):
        print("[fix] shared cache %s is missing or STALE (no POS tags) -- regenerating a POS-CORRECTED "
              "cache into this cell's OWN data dir: %s (shared cache left untouched)" % (shared, own),
              flush=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        S.parse_and_cache(tok, own)
    return own


# --------------------------------------------------------------------------- downstream task (reused gold)
def build_paraphrase_items(docs=None):
    """SAME construction as exp_meaning_channel_paraphrase_comprehension_v1.main(): per LitBank document,
    candidate set = distinct gov_verb strings (alpha, len>=3, >=3 candidates); for each candidate `target`,
    query = a WordNet verb-synonym of `target` that is a DIFFERENT lemma and not already a candidate string.
    Fully deterministic (no RNG): the gold item set does not depend on corpus vocabulary, so it is built
    ONCE and the SAME items are used for every arm/corpus size (no leakage, no re-derivation of the gold)."""
    recs = P.H.load_cache()
    if docs is not None:
        recs = recs[:docs]
    items = []
    for di, rec in enumerate(recs):
        verbs = sorted({m["gov_verb"] for m in rec["stream"] if m.get("gov_verb")})
        cand = [v for v in verbs if v.isalpha() and len(v) >= 3]
        if len(cand) < 3:
            continue
        for target in cand:
            q = P._verb_synonym(target)
            if q is None or q in cand:          # need a TRUE paraphrase (different lemma, not a candidate)
                continue
            items.append({"doc": di, "target": target, "query": q, "cand": cand})
    return items


# --------------------------------------------------------------------------- the matched info-free twin
def build_selpref_labelshuffle_cooc(parsed, word_index, rng, min_count=S.CTX_MIN_COUNT):
    """INFO-FREE twin matched to S.build_selpref_cooc's OWN edge population (verb-headed argument-slot
    edges only -- NOT the general all-deprel population S.build_labelshuffle_cooc uses, which would change
    TWO variables at once: the context-column family AND the label correspondence). Same construction
    DISCIPLINE as S.build_labelshuffle_cooc: collect the argument-slot LABEL of every qualifying edge in a
    deterministic stream order, shuffle that label SEQUENCE globally (preserves the label multiset, the
    edge count, the fillers, the verb rows), then re-walk the SAME deterministic edge stream a second time
    consuming the shuffled labels by position -- so edge #k keeps its (verb, filler) but may get a
    DIFFERENT argument-slot label than it truly had. Only the role<->filler CORRESPONDENCE is destroyed.
    2-pass memory-light (no python list of edges kept), matching S.build_labelshuffle_cooc's own approach."""
    def qualifying_edges():
        for sent in parsed:
            for tok, head, rel, _upos in sent:
                base = rel.split(":")[0]
                if base in S.ARG_SLOTS and 0 <= head < len(sent) and sent[head][3] == "VERB":
                    verb = sent[head][0]
                    if verb in word_index and tok in word_index:
                        yield verb, base, tok

    lab2id = {}
    ids = _arr("h")
    for _verb, base, _tok in qualifying_edges():
        j = lab2id.get(base)
        if j is None:
            j = len(lab2id); lab2id[base] = j
        ids.append(j)
    if not lab2id:
        return S._build_from_edges(iter(()), len(word_index), min_count)
    id2lab = sorted(lab2id, key=lab2id.get)
    arr = np.frombuffer(ids, dtype=np.int16).copy()
    rng.shuffle(arr)

    def it():
        k = 0
        for verb, _base, tok in qualifying_edges():
            yield word_index[verb], id2lab[arr[k]] + "\t" + tok
            k += 1

    return S._build_from_edges(it(), len(word_index), min_count)


def build_selpref_fillershuffle_cooc(parsed, word_index, rng, min_count=S.CTX_MIN_COUNT):
    """STRICT COMPLEMENT of build_selpref_labelshuffle_cooc (added 2026-08-28 per coordinator review).
    SAME SELPREF edge population (verb-headed argument-slot edges), but this time the FILLER TOKEN is
    globally shuffled across edges while the verb and the TRUE argument-slot LABEL stay attached to their
    real edge -- so grammar (which role each edge is) is intact and edge counts are preserved, but the
    SELECTIONAL correspondence (which specific filler word occupies that role for that verb) is destroyed.
    Where build_selpref_labelshuffle_cooc asks "does knowing the CORRECT ROLE matter", this asks "does
    knowing the CORRECT FILLER matter" -- together they bracket which half of SELPREF's structure is
    doing the work. Same 2-pass memory-light discipline (collect filler ids in edge order, shuffle the id
    sequence, re-walk the identical deterministic edge stream consuming shuffled ids by position)."""
    def qualifying_edges():
        for sent in parsed:
            for tok, head, rel, _upos in sent:
                base = rel.split(":")[0]
                if base in S.ARG_SLOTS and 0 <= head < len(sent) and sent[head][3] == "VERB":
                    verb = sent[head][0]
                    if verb in word_index and tok in word_index:
                        yield verb, base, tok

    id2word = [None] * len(word_index)
    for w, i in word_index.items():
        id2word[i] = w
    filler_ids = _arr("i")
    for _verb, _base, tok in qualifying_edges():
        filler_ids.append(word_index[tok])
    if not filler_ids:
        return S._build_from_edges(iter(()), len(word_index), min_count)
    arr = np.frombuffer(filler_ids, dtype=np.int32).copy()
    rng.shuffle(arr)

    def it():
        k = 0
        for verb, base, _tok in qualifying_edges():
            yield word_index[verb], base + "\t" + id2word[arr[k]]
            k += 1

    return S._build_from_edges(it(), len(word_index), min_count)


# --------------------------------------------------------------------------- similarity / scoring
def argmax_pred(sim_fn, query, cand):
    """argmax_c sim_fn(query, cand[c]); None candidates excluded; None overall if NONE are defined."""
    sims = [sim_fn(query, c) for c in cand]
    if all(s is None for s in sims):
        return None
    filled = [s if s is not None else -1e18 for s in sims]
    return cand[int(np.argmax(filled))]


def score_items(items, sim_fn):
    """Per item: 1/0/None (None = uncovered by this arm). Returns a python list, same order as items."""
    out = []
    for it in items:
        pred = argmax_pred(sim_fn, it["query"], it["cand"])
        out.append(None if pred is None else int(pred == it["target"]))
    return out


def boot_ci(binary_arr, seed, n_boot):
    a = np.asarray([x for x in binary_arr if x is not None], dtype=float)
    n = a.size
    if n == 0:
        return {"acc": None, "ci": [None, None], "ci_half": None, "n": 0}
    rng = np.random.default_rng(seed)
    boots = np.array([a[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"acc": round(float(a.mean()), 4), "ci": [round(lo, 4), round(hi, 4)],
            "ci_half": round((hi - lo) / 2, 4), "n": int(n)}


def paired_delta_acc(arr_a, arr_b, seed, n_boot):
    """Matched-pairs bootstrap of mean(a) - mean(b) over the SAME resampled item indices (higher power
    than comparing independent CIs for a small per-item effect; same method
    exp_structured_context_learner_v1.paired_delta uses for its own gate). a/b must be same length,
    0/1 arrays already restricted to the common-coverage population (no Nones)."""
    a = np.asarray(arr_a, dtype=float); b = np.asarray(arr_b, dtype=float)
    n = a.size
    rng = np.random.default_rng(seed)
    ds = np.array([(a[idx].mean() - b[idx].mean()) for idx in (rng.integers(0, n, n) for _ in range(n_boot))])
    lo, hi = float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))
    d0 = float(a.mean() - b.mean())
    return {"delta": round(d0, 4), "ci": [round(lo, 4), round(hi, 4)], "ci_half": round((hi - lo) / 2, 4),
            "n": int(n), "separated_above": bool(lo > 0), "separated_below": bool(hi < 0)}


def _frac_ci(pool_idx, arr, want, seed, n_boot):
    """P(arr[pool_idx] == want), bootstrap CI over pool_idx (shared by corruption_rate and the
    confidence-split breakdown so both use IDENTICAL arithmetic)."""
    if pool_idx.size == 0:
        return {"rate": None, "ci": [None, None], "ci_half": None, "n": 0}
    rng = np.random.default_rng(seed)
    n = pool_idx.size
    point = float((arr[pool_idx] == want).mean())
    boots = np.array([(arr[pool_idx[rng.integers(0, n, n)]] == want).mean() for _ in range(n_boot)])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return {"rate": round(point, 4), "ci": [round(lo, 4), round(hi, 4)],
            "ci_half": round((hi - lo) / 2, 4), "n": int(n)}


def corruption_rate(base_correct, grown_correct, seed, n_boot):
    """base_correct/grown_correct: 0/1 arrays over the SAME items (common-coverage population).
    corruption_right_to_wrong = P(grown wrong | base right) -- the safety number (BAR #4c).
    recovery_wrong_to_right   = P(grown right | base wrong) -- reported for context."""
    base = np.asarray(base_correct, dtype=int); grown = np.asarray(grown_correct, dtype=int)
    right_idx = np.where(base == 1)[0]
    wrong_idx = np.where(base == 0)[0]
    return {"corruption_right_to_wrong": _frac_ci(right_idx, grown, 0, seed + 100, n_boot),
            "recovery_wrong_to_right": _frac_ci(wrong_idx, grown, 1, seed + 101, n_boot)}


def prediction_confidence(sim_fn, query, cand):
    """The predicting arm's OWN confidence in its argmax pick: margin between the top and 2nd-best
    candidate similarity. Falls back to the top similarity VALUE if only one candidate has a defined
    score (margin undefined with < 2 defined scores). None if no candidate has a defined score."""
    sims = [sim_fn(query, c) for c in cand]
    defined = [s for s in sims if s is not None]
    if not defined:
        return None
    if len(defined) == 1:
        return float(defined[0])
    top2 = sorted(defined, reverse=True)[:2]
    return float(top2[0] - top2[1])


def confidence_split_corruption(items, base_core_idx, base_core, grown_core, sim_baseline, seed, n_boot):
    """CORRUPTION BY CONFIDENCE (coordinator request 2026-08-28): among the base-right items, is the
    right->wrong flip concentrated in LOW-CONFIDENCE baseline predictions (churn near a tie -- supports a
    confidence-gated growth mitigation) or does it hit HIGH-CONFIDENCE predictions too (genuine knowledge
    loss)? Confidence = the BASELINE arm's own prediction_confidence on each base-right item. Median split
    into top-half (confident) vs bottom-half (low-margin); each half's right->wrong rate + CI computed with
    the SAME _frac_ci arithmetic as the overall corruption number.
    base_core_idx: the list mapping CORE_COMMON position -> original `items` index (so query/cand can be
    looked back up for the confidence computation). base_core/grown_core: 0/1 arrays over CORE_COMMON."""
    base = np.asarray(base_core, dtype=int); grown = np.asarray(grown_core, dtype=int)
    right_pos_all = np.where(base == 1)[0]        # positions (within CORE_COMMON) baseline got right
    pos_list, conf_list = [], []
    for pos in right_pos_all:
        it = items[base_core_idx[pos]]
        c = prediction_confidence(sim_baseline, it["query"], it["cand"])
        if c is not None:                          # guard only; a base-right item always has >=1 defined score
            pos_list.append(pos); conf_list.append(c)
    right_pos = np.asarray(pos_list, dtype=int)
    conf = np.asarray(conf_list, dtype=float)
    order = np.argsort(-conf)                      # descending: most confident first
    right_pos_sorted = right_pos[order]
    conf_sorted = conf[order]
    half = len(right_pos_sorted) // 2
    top_half, bottom_half = right_pos_sorted[:half], right_pos_sorted[half:]
    top_conf, bottom_conf = conf_sorted[:half], conf_sorted[half:]

    def _rng(a):
        return [float(a.min()), float(a.max())] if a.size else [None, None]

    return {
        "n_base_right_with_confidence": int(len(right_pos_sorted)),
        "confidence_median_split_value": float(np.median(conf)) if conf.size else None,
        "top_half_confident": dict(_frac_ci(top_half, grown, 0, seed + 200, n_boot), conf_range=_rng(top_conf)),
        "bottom_half_low_confidence": dict(_frac_ci(bottom_half, grown, 0, seed + 201, n_boot),
                                            conf_range=_rng(bottom_conf)),
    }


# --------------------------------------------------------------------------- self-test (formula, no corpus)
def self_test():
    ok = True

    # (1) corruption-rate arithmetic: hand-worked example. base-right = idx{0,1,2,4} (4 items); grown wrong
    # at idx1 only -> corruption_right_to_wrong = 1/4. base-wrong = idx{3}; grown is ALSO wrong there
    # (grown[3]=0, want=1 for recovery) -> recovery_wrong_to_right = 0/1 = 0.0.
    base = [1, 1, 1, 0, 1]
    grown = [1, 0, 1, 0, 1]
    res = corruption_rate(base, grown, seed=1, n_boot=200)
    exp_corr, exp_rec = 0.25, 0.0
    ok_c = (abs(res["corruption_right_to_wrong"]["rate"] - exp_corr) < 1e-9
            and abs(res["recovery_wrong_to_right"]["rate"] - exp_rec) < 1e-9)
    print("[self-test] corruption arithmetic: expect corr=%.4f rec=%.4f got corr=%.4f rec=%.4f -> %s"
          % (exp_corr, exp_rec, res["corruption_right_to_wrong"]["rate"],
             res["recovery_wrong_to_right"]["rate"], "OK" if ok_c else "FAIL"), flush=True)
    ok = ok and ok_c

    # (2) paired_delta_acc arithmetic: a beats b by a known margin, with n large enough that a real effect
    # is CI-separated (sanity that the sign/gate direction is right, not just that it runs).
    rng = np.random.default_rng(7)
    b_arr = rng.integers(0, 2, 400).astype(float)
    a_arr = b_arr.copy()
    flip_up = np.where(b_arr == 0)[0][:60]
    a_arr[flip_up] = 1.0   # a strictly improves on 60 of b's 0s, never regresses -> a beats b CI-sep
    d = paired_delta_acc(a_arr, b_arr, seed=2, n_boot=500)
    ok_d = d["delta"] > 0 and d["separated_above"]
    print("[self-test] paired_delta_acc: delta=%.4f ci=%s separated_above=%s -> %s"
          % (d["delta"], d["ci"], d["separated_above"], "OK" if ok_d else "FAIL"), flush=True)
    ok = ok and ok_d

    # (3) paraphrase item construction: real LitBank cache, exact-match must be excluded by construction.
    items = build_paraphrase_items(docs=20)
    ok_i = len(items) > 0 and all(it["query"] != it["target"] for it in items)
    print("[self-test] paraphrase items (20 docs): n=%d exact-match-excluded=%s -> %s"
          % (len(items), ok_i, "OK" if ok_i else "FAIL"), flush=True)
    ok = ok and ok_i

    # (4) SELPREF label-shuffle twin: matched edge population on a tiny synthetic parse. At min_count=1
    # NO columns are dropped, so total edge mass must be IDENTICAL between real and shuffled (the shuffle
    # only reassigns WHICH column an edge lands in, never drops an edge) -- the exact invariant the
    # construction claims to preserve.
    one_pair = [
        [("the", 1, "det", "DET"), ("cat", 2, "nsubj", "NOUN"), ("chased", 2, "ROOT", "VERB"),
         ("the", 4, "det", "DET"), ("mouse", 2, "dobj", "NOUN")],
        [("a", 1, "det", "DET"), ("dog", 2, "nsubj", "NOUN"), ("saw", 2, "ROOT", "VERB"),
         ("a", 4, "det", "DET"), ("bird", 2, "dobj", "NOUN")],
    ]
    parsed = one_pair * 25
    words = sorted({t for s in parsed for (t, _h, _r, _u) in s})
    index = {w: i for i, w in enumerate(words)}
    real, n_real = S.build_selpref_cooc(parsed, index, min_count=1)
    shuf, n_shuf = build_selpref_labelshuffle_cooc(parsed, index, np.random.default_rng(3), min_count=1)
    same_total = abs(float(real.sum()) - float(shuf.sum())) < 1e-9
    both_nonzero = float(real.sum()) > 0 and float(shuf.sum()) > 0
    same_shape0 = real.shape[0] == shuf.shape[0] == len(index)
    ok_s = same_total and both_nonzero and same_shape0
    print("[self-test] selpref labelshuffle: edges_real=%.0f edges_shuf=%.0f cols_real=%d cols_shuf=%d "
          "same_total=%s -> %s" % (float(real.sum()), float(shuf.sum()), n_real, n_shuf, same_total,
                                    "OK" if ok_s else "FAIL"), flush=True)
    ok = ok and ok_s

    # (5) SELPREF filler-shuffle twin (strict complement, added 2026-08-28): same tiny synthetic parse,
    # same invariant (min_count=1 -> total edge mass preserved -- fillers are reassigned, never dropped).
    fshuf, n_fshuf = build_selpref_fillershuffle_cooc(parsed, index, np.random.default_rng(5), min_count=1)
    same_total_f = abs(float(real.sum()) - float(fshuf.sum())) < 1e-9
    ok_f = same_total_f and float(fshuf.sum()) > 0 and fshuf.shape[0] == len(index)
    print("[self-test] selpref fillershuffle: edges_real=%.0f edges_fshuf=%.0f cols_fshuf=%d same_total=%s "
          "-> %s" % (float(real.sum()), float(fshuf.sum()), n_fshuf, same_total_f, "OK" if ok_f else "FAIL"),
          flush=True)
    ok = ok and ok_f

    # (6) prediction_confidence: hand-worked. 3 candidates with known sims -> margin = top - 2nd.
    # 1 candidate defined -> fallback to its raw value. 0 defined -> None.
    def fake_sim(pairs):
        d = dict(pairs)
        return lambda q, c: d.get((q, c))
    sim3 = fake_sim({("q", "a"): 0.9, ("q", "b"): 0.5, ("q", "c"): 0.2})
    c3 = prediction_confidence(sim3, "q", ["a", "b", "c"])
    sim1 = fake_sim({("q", "a"): 0.7})
    c1 = prediction_confidence(sim1, "q", ["a", "b"])
    c0 = prediction_confidence(fake_sim({}), "q", ["a", "b"])
    ok_pc = abs(c3 - 0.4) < 1e-9 and abs(c1 - 0.7) < 1e-9 and c0 is None
    print("[self-test] prediction_confidence: margin(3cand)=%.4f(expect 0.4) fallback(1cand)=%.4f(expect 0.7) "
          "none(0cand)=%s -> %s" % (c3, c1, c0, "OK" if ok_pc else "FAIL"), flush=True)
    ok = ok and ok_pc

    # (7) confidence_split_corruption: hand-worked, exercises the REAL function end-to-end. 4 base-right
    # toy items with DISTINCT queries so one shared sim_fn gives each a KNOWN, DIFFERENT confidence
    # (margin = |simA - simB|): item0=0.9, item1=0.7, item2=0.3, item3=0.1 -> median split gives
    # top_half={item0,item1} (confident), bottom_half={item2,item3} (low-margin). grown-correctness is
    # rigged so ONLY the two low-confidence items flip wrong -> top_half corruption must be 0/2=0.0,
    # bottom_half must be 2/2=1.0 (churn concentrated in low confidence, the "safe" pattern).
    toy_items = [{"query": "q%d" % i, "cand": ["a", "b"], "target": "a"} for i in range(4)]
    confs_wanted = [0.9, 0.7, 0.3, 0.1]
    toy_sim_table = {}
    for i, m in enumerate(confs_wanted):
        toy_sim_table[("q%d" % i, "a")] = 0.5 + m / 2
        toy_sim_table[("q%d" % i, "b")] = 0.5 - m / 2
    sim_toy = fake_sim(toy_sim_table)
    base_core_idx_toy = [0, 1, 2, 3]
    base_core_toy = [1, 1, 1, 1]
    grown_core_toy = [1, 1, 0, 0]
    res_cs = confidence_split_corruption(toy_items, base_core_idx_toy, base_core_toy, grown_core_toy,
                                          sim_toy, seed=11, n_boot=200)
    top_corr = res_cs["top_half_confident"]["rate"]
    bot_corr = res_cs["bottom_half_low_confidence"]["rate"]
    ok_cs = abs(top_corr - 0.0) < 1e-9 and abs(bot_corr - 1.0) < 1e-9
    print("[self-test] confidence_split_corruption (real fn): top_half_corr=%.4f(expect 0.0) "
          "bottom_half_corr=%.4f(expect 1.0) split=%s -> %s"
          % (top_corr, bot_corr, res_cs["confidence_median_split_value"], "OK" if ok_cs else "FAIL"),
          flush=True)
    ok = ok and ok_cs

    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


# --------------------------------------------------------------------------- main run
def run(mode):
    cfg = MODE_CFG[mode]
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("[items] building paraphrase items from data/litbank/who_did_what_events.json (all docs) ...",
          flush=True)
    items = build_paraphrase_items(docs=None)
    force_words = set()
    for it in items:
        force_words.add(it["query"]); force_words.update(it["cand"])
    print("[items] n_items=%d n_force_words=%d" % (len(items), len(force_words)), flush=True)
    if len(items) < 10:
        print("[abort] fewer than 10 paraphrase items constructed; cannot score", flush=True)
        return 1

    print("[load] parsed caches (small=%d large=%d tok; shared caches used if POS-valid, else a "
          "POS-corrected cache is (re)built into this cell's own data dir -- see cache_path()) ..."
          % (cfg["small_tok"], cfg["large_tok"]), flush=True)
    parsed_small, ntok_small = S.load_parsed(cache_path(cfg["small_tok"]), cfg["small_tok"])
    parsed_large, ntok_large = S.load_parsed(cache_path(cfg["large_tok"]), cfg["large_tok"])
    print("[load] small: %d sent / %d tok | large: %d sent / %d tok"
          % (len(parsed_small), ntok_small, len(parsed_large), ntok_large), flush=True)

    toks_small = S.token_sents(parsed_small)
    toks_large = S.token_sents(parsed_large)
    index_small = S.build_vocab(toks_small, force_words, cfg["vocab_cap"], cfg["min_count"])
    index_large = S.build_vocab(toks_large, force_words, cfg["vocab_cap"], cfg["min_count"])
    print("[vocab] small=%d words | large=%d words" % (len(index_small), len(index_large)), flush=True)

    print("[build] SELPREF cooc (baseline/grown/labelshuffle/fillershuffle) ...", flush=True)
    selpref_small, ncol_small = S.build_selpref_cooc(parsed_small, index_small, min_count=cfg["ctx_min_count"])
    selpref_large, ncol_large = S.build_selpref_cooc(parsed_large, index_large, min_count=cfg["ctx_min_count"])
    selpref_labelshuf, ncol_labelshuf = build_selpref_labelshuffle_cooc(
        parsed_large, index_large, np.random.default_rng(SEED + 3), min_count=cfg["ctx_min_count"])
    selpref_fillershuf, ncol_fillershuf = build_selpref_fillershuffle_cooc(
        parsed_large, index_large, np.random.default_rng(SEED + 4), min_count=cfg["ctx_min_count"])
    print("[build] cols: small=%d large=%d labelshuffle=%d fillershuffle=%d"
          % (ncol_small, ncol_large, ncol_labelshuf, ncol_fillershuf), flush=True)

    # FULLSHUF_GROWTH (coordinator addition 2026-08-28): a GENUINELY info-free growth control -- the
    # learner is trained on the LARGE corpus with its TOKEN STREAM GLOBALLY SHUFFLED (destroys ALL
    # co-occurrence, keeps unigram marginals), reusing the baseline's own shuffle mechanism
    # (S.build_cooc(..., shuffle_seed=...), the same construction the landed exp_structured_context_
    # learner_v1 uses for its own SHUF_CORPUS control). A plain WIN2 window-PPMI-SVD (not SELPREF -- with
    # NO real co-occurrence there is no dependency structure to restrict to argument slots either) is the
    # "cleanest" read per the coordinator's instruction; verb-verb cosine is still well-defined over it.
    # Expect this arm to sit near RANDOM.
    print("[build] FULLSHUF_GROWTH: window-PPMI-SVD on a globally token-shuffled 15M corpus ...", flush=True)
    fullshuf_cooc = S.build_cooc(toks_large, index_large, 2, shuffle_seed=SEED + 30)

    print("[svd] PPMI + SVD per arm ...", flush=True)
    vec_small = S.svd_vectors(S.ppmi_matrix(selpref_small), seed=SEED)
    vec_large = S.svd_vectors(S.ppmi_matrix(selpref_large), seed=SEED)
    vec_labelshuf = S.svd_vectors(S.ppmi_matrix(selpref_labelshuf), seed=SEED)
    vec_fillershuf = S.svd_vectors(S.ppmi_matrix(selpref_fillershuf), seed=SEED)
    vec_fullshuf = S.svd_vectors(S.ppmi_matrix(fullshuf_cooc), seed=SEED)
    sim_baseline = S.dense_vec_cosine_fn(vec_small, index_small)
    sim_grown = S.dense_vec_cosine_fn(vec_large, index_large)
    sim_labelshuf = S.dense_vec_cosine_fn(vec_labelshuf, index_large)
    sim_fillershuf = S.dense_vec_cosine_fn(vec_fillershuf, index_large)
    sim_fullshuf = S.dense_vec_cosine_fn(vec_fullshuf, index_large)

    union_words = sorted(set(index_small) | set(index_large))
    union_index = {w: i for i, w in enumerate(union_words)}
    sim_random = S.random_vec_cosine_fn(union_index, dim=S.SVD_K, seed=SEED)

    chan = ConceptualChannel()
    def sim_conceptual(w1, w2):
        return chan.similarity(w1, "V", w2, "V")

    print("[score] scoring all arms on all items ...", flush=True)
    r_baseline = score_items(items, sim_baseline)
    r_grown = score_items(items, sim_grown)
    r_labelshuf = score_items(items, sim_labelshuf)
    r_fillershuf = score_items(items, sim_fillershuf)
    r_fullshuf = score_items(items, sim_fullshuf)
    r_conceptual = score_items(items, sim_conceptual)
    r_random = score_items(items, sim_random)

    n_total = len(items)
    # CORE_COMMON now spans ALL FIVE learned-channel arms (added fullshuf + fillershuf) so every gate
    # comparison in this run (old label-shuffle gate, new clean fullshuf gate, filler-shuffle context,
    # corruption, confidence breakdown) is computed on IDENTICAL items -- no number crosses populations.
    core_idx = [i for i in range(n_total)
                if r_baseline[i] is not None and r_grown[i] is not None and r_labelshuf[i] is not None
                and r_fillershuf[i] is not None and r_fullshuf[i] is not None]
    n_core = len(core_idx)
    print("[coverage] n_total=%d baseline=%d grown=%d labelshuf=%d fillershuf=%d fullshuf=%d "
          "conceptual=%d random=%d | CORE_COMMON(all 5 learned arms)=%d"
          % (n_total, sum(x is not None for x in r_baseline), sum(x is not None for x in r_grown),
             sum(x is not None for x in r_labelshuf), sum(x is not None for x in r_fillershuf),
             sum(x is not None for x in r_fullshuf), sum(x is not None for x in r_conceptual),
             sum(x is not None for x in r_random), n_core), flush=True)

    if n_core < 10:
        print("[abort] CORE_COMMON coverage < 10 items; cannot gate", flush=True)
        metrics = {"anchor_name": ANCHOR, "mode": mode, "verdict": "ABORT_INSUFFICIENT_COVERAGE",
                   "n_total_items": n_total, "n_core_common": n_core, "elapsed_s": round(time.time() - t0, 1)}
        _write_metrics(metrics)
        return 1

    base_core = [r_baseline[i] for i in core_idx]
    grown_core = [r_grown[i] for i in core_idx]
    labelshuf_core = [r_labelshuf[i] for i in core_idx]
    fillershuf_core = [r_fillershuf[i] for i in core_idx]
    fullshuf_core = [r_fullshuf[i] for i in core_idx]
    conceptual_core = [r_conceptual[i] for i in core_idx if r_conceptual[i] is not None]
    random_core = [r_random[i] for i in core_idx if r_random[i] is not None]

    arm_acc = {
        "BASELINE_SMALL": boot_ci(base_core, SEED + 1, cfg["n_boot"]),
        "GROWN_LARGE": boot_ci(grown_core, SEED + 2, cfg["n_boot"]),
        "INFO_FREE_LABELSHUF": boot_ci(labelshuf_core, SEED + 3, cfg["n_boot"]),
        "INFO_FREE_FILLERSHUF": boot_ci(fillershuf_core, SEED + 6, cfg["n_boot"]),
        "INFO_FREE_FULLSHUF": boot_ci(fullshuf_core, SEED + 7, cfg["n_boot"]),
        "CONCEPTUAL_ref": boot_ci(conceptual_core, SEED + 4, cfg["n_boot"]),
        "RANDOM_floor": boot_ci(random_core, SEED + 5, cfg["n_boot"]),
    }
    for nm, r in arm_acc.items():
        print("  %-22s acc=%s ci=%s n=%d" % (nm, r["acc"], r["ci"], r["n"]), flush=True)

    d_grown_vs_base = paired_delta_acc(grown_core, base_core, SEED + 10, cfg["n_boot"])
    d_labelshuf_vs_base = paired_delta_acc(labelshuf_core, base_core, SEED + 11, cfg["n_boot"])
    d_fillershuf_vs_base = paired_delta_acc(fillershuf_core, base_core, SEED + 13, cfg["n_boot"])
    d_fullshuf_vs_base = paired_delta_acc(fullshuf_core, base_core, SEED + 14, cfg["n_boot"])
    d_grown_vs_labelshuf = paired_delta_acc(grown_core, labelshuf_core, SEED + 12, cfg["n_boot"])
    d_grown_vs_fullshuf = paired_delta_acc(grown_core, fullshuf_core, SEED + 15, cfg["n_boot"])
    print("  GROWN - BASELINE        : %s" % d_grown_vs_base, flush=True)
    print("  LABELSHUF - BASELINE    : %s" % d_labelshuf_vs_base, flush=True)
    print("  FILLERSHUF - BASELINE   : %s" % d_fillershuf_vs_base, flush=True)
    print("  FULLSHUF - BASELINE     : %s  (the GENUINELY info-free control)" % d_fullshuf_vs_base, flush=True)
    print("  GROWN - LABELSHUF       : %s  (role-label-specific residual)" % d_grown_vs_labelshuf, flush=True)
    print("  GROWN - FULLSHUF        : %s  (real-structure residual over the clean info-free floor)"
          % d_grown_vs_fullshuf, flush=True)

    gate_a = bool(d_grown_vs_base["separated_above"])                 # growth helps, CI-separated
    # OLD gate_b (label-shuffle twin) kept for continuity with the first run's report.
    gate_b_labelshuf = bool(not d_labelshuf_vs_base["separated_above"])
    # CLEAN gate_b (coordinator 2026-08-28): the GENUINELY info-free control (full corpus shuffle) must
    # NOT beat baseline CI-separated, AND grown must beat it CI-separated (real structure adds value on
    # top of the clean info-free floor, not just on top of a partial/weak ablation).
    gate_b_clean = bool(not d_fullshuf_vs_base["separated_above"]) and bool(d_grown_vs_fullshuf["separated_above"])
    gate_pass_clean = gate_a and gate_b_clean

    corr = corruption_rate(base_core, grown_core, SEED + 20, cfg["n_boot"])
    print("  CORRUPTION (right->wrong, base-right n=%d): %s" % (
        corr["corruption_right_to_wrong"]["n"], corr["corruption_right_to_wrong"]), flush=True)
    print("  RECOVERY   (wrong->right, base-wrong n=%d): %s" % (
        corr["recovery_wrong_to_right"]["n"], corr["recovery_wrong_to_right"]), flush=True)

    conf_break = confidence_split_corruption(items, core_idx, base_core, grown_core, sim_baseline,
                                              SEED + 40, cfg["n_boot"])
    print("  CORRUPTION BY CONFIDENCE: top_half(confident)=%s | bottom_half(low-margin)=%s | median_split=%.4f"
          % (conf_break["top_half_confident"], conf_break["bottom_half_low_confidence"],
             conf_break["confidence_median_split_value"]), flush=True)

    if gate_pass_clean:
        verdict = "SAFE_TO_GROW_GATE_A_AND_CLEAN_GATE_B_PASS_CISEP"
    elif not gate_a:
        verdict = "NOT_SAFE_GROWTH_DOES_NOT_IMPROVE_COMPREHENSION_CISEP__GATE_A_FAIL"
    elif d_fullshuf_vs_base["separated_above"]:
        verdict = "NOT_SAFE_EVEN_FULLY_SHUFFLED_GROWTH_BEATS_BASELINE__GATE_B_CLEAN_FAIL_COVERAGE_CONFOUND"
    else:
        verdict = "NOT_SAFE_GROWN_DOES_NOT_CLEAR_CLEAN_INFOFREE_FLOOR_CISEP__GATE_B_CLEAN_FAIL"

    print("[verdict] %s | gate_a=%s gate_b_clean=%s (gate_b_labelshuf_from_first_run=%s) | %.0fs"
          % (verdict, gate_a, gate_b_clean, gate_b_labelshuf, time.time() - t0), flush=True)

    metrics = {
        "anchor_name": ANCHOR, "mode": mode, "seed": SEED,
        "config": dict(cfg, svd_k=S.SVD_K, svd_p=S.SVD_P, ppmi_alpha=S.PPMI_ALPHA),
        "n_tokens": {"small": ntok_small, "large": ntok_large},
        "vocab": {"small": len(index_small), "large": len(index_large)},
        "selpref_cols": {"small": ncol_small, "large": ncol_large, "labelshuffle": ncol_labelshuf,
                          "fillershuffle": ncol_fillershuf},
        "n_total_items": n_total, "n_force_words": len(force_words),
        "coverage": {
            "baseline": sum(x is not None for x in r_baseline),
            "grown": sum(x is not None for x in r_grown),
            "labelshuf": sum(x is not None for x in r_labelshuf),
            "fillershuf": sum(x is not None for x in r_fillershuf),
            "fullshuf": sum(x is not None for x in r_fullshuf),
            "conceptual": sum(x is not None for x in r_conceptual),
            "random": sum(x is not None for x in r_random),
            "core_common": n_core,
        },
        "arm_accuracy": arm_acc,
        "gate": {
            "grown_vs_baseline": d_grown_vs_base,
            "labelshuf_vs_baseline": d_labelshuf_vs_base,
            "fillershuf_vs_baseline": d_fillershuf_vs_base,
            "fullshuf_vs_baseline": d_fullshuf_vs_base,
            "grown_vs_labelshuf_residual": d_grown_vs_labelshuf,
            "grown_vs_fullshuf_residual": d_grown_vs_fullshuf,
            "gate_a_grown_beats_baseline_cisep": gate_a,
            "gate_b_labelshuf_does_not_beat_baseline_cisep": gate_b_labelshuf,
            "gate_b_clean_fullshuf_does_not_beat_baseline_AND_grown_beats_fullshuf": gate_b_clean,
            "gate_pass_clean": gate_pass_clean,
        },
        "corruption": corr,
        "corruption_by_confidence": conf_break,
        "verdict": verdict,
        "elapsed_s": round(time.time() - t0, 1),
    }
    _write_metrics(metrics)
    return 0


def _write_metrics(metrics):
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUTPUT_DIR, "metrics.json"), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    return run(args.mode)


if __name__ == "__main__":
    sys.exit(main())
