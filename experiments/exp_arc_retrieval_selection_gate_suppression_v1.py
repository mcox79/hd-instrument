"""arc_retrieval_selection_gate_suppression_v1 -- the brain's STAGE-5 RETRIEVAL SELECTION GATE.

The bind+settle combiner reaches Challenge 0.696 on CLEAN gold facts but DROWNS on the noisy real
spreading-activation pool (Challenge ~0.28-0.31). MEASURED@disk:
  combiner-on-gold   oracle_bundle_acc_challenge = 0.6961
    @data/exp_arc_aggregation_retriever_bindsettle_v1/metrics.json
  combiner-on-noisy  retr_bundle_acc_challenge   = 0.2834 (same file);
    spreading-pool baseline end-to-end Challenge  = 0.3101
    @data/exp_arc_retrieval_multicue_ppr_discriminative_v1/metrics.json:end_to_end.A.bundle.challenge
The brain never feeds a noisy pool to reasoning: Stage-5 RETRIEVAL CONTROL first (Badre & Wagner 2007
anterior-VLPFC controlled/strategic retrieval + mid-VLPFC post-retrieval SELECTION; Anderson, Bjork &
Bjork 1994 retrieval-induced-forgetting = ACTIVELY SUPPRESS competitors). We have NO selection gate.

ONE variable = the SELECTION GATE, inserted BEFORE the UNCHANGED combiner, over the UNCHANGED
spreading pool (PPR arm B, imported). gate_score(f) = goal_score(f) - MU * lure_penalty(f):
  goal_score = relu(cos(f,STEM)) + LAMBDA_DISC*(max_c cos(f,choice_c) - 2nd_max)   [goal-bias]
  lure_penalty = Jaccard(fact_words, stem_words) * [argmax choice of f is the STANDOUT surface-lure]
                                                                                    [RIF suppression]
The standout surface-lure = UNIQUE argmax stem-word-overlap choice strictly above mean overlap
(answer-agnostic; NEVER uses gold).

ARMS (identical spreading pool; combiner = UNCHANGED agg.aggregate 'bundle'; ONLY selection differs):
  A_noisy   -- all K_POOL pool facts -> combiner              [BASELINE = current noisy pool]
  B_gate    -- top-K_SEL by gate_score -> combiner            [MECHANISM: goal-bias + suppression]
  S_nosupp  -- top-K_SEL by goal_score alone -> combiner      [ABLATION: suppression OFF]
  R_random  -- K_SEL random pool facts -> combiner            [MUST-FAIL: "fewer facts" driver]
  ref_oracle_gold -- gold central facts -> combiner           [CONTEXT ceiling ~0.696]

PRIMARY metric = END-TO-END ARC accuracy (Easy + Challenge, ESPECIALLY Challenge-LURE subset). NOT
recall (selection is SUPPOSED to lower recall -- it trades recall for precision). McNemar A vs B on
the LURE subset. Selectivity check (NON-LURE unchanged). Suppression-precision check (fires on WRONG
not CORRECT choice). Glass-box: which facts selected/suppressed per question.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT
remote-portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng,
sorted iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL PPR pool + REAL gate + UNCHANGED
#   combiner; a PLANTED surface-lure case asserts the gate FIRES (B flips a question A drowns; S fails
#   where B succeeds => suppression load-bearing; suppression fires on the WRONG choice); arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on A_noisy challenge (headroom vs the 0.696 ceiling)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import math
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse: PPR spreading pool (UNCHANGED), the bind+settle combiner (UNCHANGED), arc helpers
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_retrieval_selection_gate_suppression_v1"
SEED = 20260724

# ---- selection-gate hyperparams (author-designed a priori; see pre-reg) ----
K_POOL = 20          # spreading pool the gate selects from (the "noisy pool" baseline A feeds whole)
K_SEL = 4            # few clean facts after selection (Cowan-4 / WorldTree ~2.5 central)
LAMBDA_DISC = 1.0    # weight of the choice-separating (discriminative) term in goal_score
MU_SUPP = 1.0        # competitor-suppression penalty weight (RIF)
# pool-construction constants (reused UNCHANGED from the PPR cell)
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# ---- bands (author-designed a priori; PRIMARY = end-to-end Challenge-LURE accuracy) ----
HP_LURE_LIFT = 0.08    # B_gate - A_noisy on Challenge-LURE  (notes pre-reg strong claim)
MB_LURE_LIFT = 0.03    # positive-but-sub-HP band floor
HP_SUPP = 0.02         # B_gate - S_nosupp on LURE -> suppression load-bearing
RANDOM_MAX = 0.03      # R_random - A_noisy on LURE must be <= this (fewer-facts is not the driver)
SEL_NONLURE_EPS = 0.05 # |B_gate - A_noisy| on NON-LURE must be <= this (selective to the failure mode)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95 # A_noisy challenge >= this -> vacuous (no headroom)


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
_T0 = [0.0]


def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# surface-lure identification (answer-agnostic) + LURE-subset stratification (eval)
# ---------------------------------------------------------------------------
def _overlap_counts(stem_words, choices):
    """Stem content-word overlap count per choice (min_len=MIN_TERM_LEN)."""
    sw = set(stem_words)
    return [len(sw & set(arc._content_words(ch, MIN_TERM_LEN))) for ch in choices]


def standout_lure_choices(stem_words, choices):
    """Answer-agnostic: the UNIQUE argmax stem-word-overlap choice, strictly above mean overlap.
    Returns a set of choice indices (empty if no standout surface-dominant choice)."""
    ov = _overlap_counts(stem_words, choices)
    if not ov:
        return set(), ov
    max_ov = max(ov)
    argmax_count = sum(1 for o in ov if o == max_ov)
    mean_ov = float(np.mean(ov))
    if max_ov > 0 and argmax_count == 1 and max_ov > mean_ov:
        return {int(np.argmax(ov))}, ov
    return set(), ov


def is_lure_question(stem_words, choices, correct_index):
    """EVAL stratification (may use gold): a distractor's stem-word overlap STRICTLY exceeds the
    correct answer's overlap (the surface-trap the Challenge set is built around)."""
    ov = _overlap_counts(stem_words, choices)
    if not ov or correct_index >= len(ov):
        return False
    dist_max = max((ov[c] for c in range(len(ov)) if c != correct_index), default=0)
    return dist_max > ov[correct_index]


def _jaccard(a_set, b_set):
    if not a_set or not b_set:
        return 0.0
    inter = len(a_set & b_set)
    union = len(a_set | b_set)
    return inter / union if union else 0.0


# ---------------------------------------------------------------------------
# the SELECTION GATE (the ONE new piece)
# ---------------------------------------------------------------------------
def gate_scores(fh_pool, fact_word_sets, stem_word_set, stem_vec, choice_hd, lure_set):
    """Compute goal_score, gate_score, and diagnostics for a pool of facts.
      fh_pool        : [P, N] L2 fact embeddings (the spreading pool)
      fact_word_sets : list length P of content-word sets per pooled fact
      stem_word_set  : content-word set of the stem
      stem_vec       : [N] L2 stem embedding
      choice_hd      : [C, N] L2 (stem+choice) embeddings
      lure_set       : set of choice indices flagged as standout surface-lures (answer-agnostic)
    Returns dict with arrays goal, gate, lure_penalty, best_choice, g_stem, g_disc, surf_pull."""
    P = fh_pool.shape[0]
    if P == 0:
        z = np.zeros(0, dtype=np.float64)
        return {"goal": z, "gate": z, "lure_penalty": z, "best_choice": np.zeros(0, np.int64),
                "g_stem": z, "g_disc": z, "surf_pull": z}
    cc = fh_pool @ choice_hd.T                                  # [P, C] cos(fact, choice)
    g_stem = np.maximum(fh_pool @ stem_vec, 0.0)                # [P] relu goal relevance
    if cc.shape[1] >= 2:
        part = np.sort(cc, axis=1)
        g_disc = part[:, -1] - part[:, -2]                     # choice-separating margin
    else:
        g_disc = cc.max(axis=1)
    goal = g_stem + LAMBDA_DISC * g_disc
    best_choice = cc.argmax(axis=1).astype(np.int64)
    lure_align = np.array([1.0 if int(bc) in lure_set else 0.0 for bc in best_choice], dtype=np.float64)
    surf_pull = np.array([_jaccard(fact_word_sets[i], stem_word_set) for i in range(P)], dtype=np.float64)
    lure_penalty = surf_pull * lure_align
    gate = goal - MU_SUPP * lure_penalty
    return {"goal": goal.astype(np.float64), "gate": gate.astype(np.float64),
            "lure_penalty": lure_penalty, "best_choice": best_choice,
            "g_stem": g_stem.astype(np.float64), "g_disc": g_disc.astype(np.float64),
            "surf_pull": surf_pull}


def _topk_idx(scores, k):
    """Indices of the top-k scores (descending, stable ties by index)."""
    n = scores.shape[0]
    kk = min(k, n)
    if kk <= 0:
        return np.zeros(0, dtype=np.int64)
    idx = np.argpartition(-scores, kk - 1)[:kk]
    return idx[np.argsort(-scores[idx], kind="stable")]


# ---------------------------------------------------------------------------
# McNemar
# ---------------------------------------------------------------------------
def mcnemar(a_correct, b_correct):
    """Paired McNemar test on two boolean arrays (same items). Returns (b, c, stat, p).
      b = A right & B wrong ; c = A wrong & B right. Continuity-corrected chi-square, df=1."""
    a = np.asarray(a_correct, dtype=bool)
    b = np.asarray(b_correct, dtype=bool)
    n_b = int(np.sum(a & ~b))
    n_c = int(np.sum(~a & b))
    disc = n_b + n_c
    if disc == 0:
        return n_b, n_c, 0.0, 1.0
    stat = (abs(n_b - n_c) - 1.0) ** 2 / disc
    try:
        from scipy.stats import chi2
        p = float(chi2.sf(stat, 1))
    except Exception:
        # normal-approx fallback: chi2_1 sf = erfc(sqrt(stat/2))
        p = float(math.erfc(math.sqrt(max(stat, 0.0) / 2.0)))
    return n_b, n_c, float(stat), p


# ---------------------------------------------------------------------------
# self-test: real code path + planted surface-lure discriminator + arms-differ + determinism
# ---------------------------------------------------------------------------
def _planted_selection_gate_discriminator():
    """Synthetic HD + lexical case proving the gate is load-bearing and reachable:
    choices: c_T (correct) low stem-overlap, c_L (lure) HIGH stem-overlap (unique standout).
    Pool: 2 good facts (support c_T, moderate stem-relevance, no surface overlap) + 3 lure facts
    (support c_L, HIGH stem surface overlap => HIGH goal_score too). Under the UNCHANGED bundle
    combiner:
      A_noisy (all facts)      -> the 3 stem-relevant lure facts dominate the bundle -> picks c_L (WRONG)
      S_nosupp (goal only)     -> lure facts rank HIGHEST by goal_score -> picks c_L (WRONG)
      B_gate (goal-suppress)   -> lure facts penalized, dropped -> good facts selected -> picks c_T (RIGHT)
    => suppression is LOAD-BEARING (S fails where B succeeds); gate reachability proven; and suppression
    fires on the WRONG choice (precision)."""
    N = 512
    rng = np.random.default_rng(11)

    def orth(v, *against):
        for a in against:
            v = v - v.dot(a) * a
        return v / np.linalg.norm(v)

    t_dir = orth(rng.standard_normal(N))                 # correct-choice direction
    l_dir = orth(rng.standard_normal(N), t_dir)          # lure-choice direction
    s_dir = orth(rng.standard_normal(N), t_dir, l_dir)   # "stem surface" direction
    choice_hd = np.stack([t_dir, l_dir]).astype(np.float32)   # C0 correct, C1 lure
    stem_vec = s_dir.astype(np.float32)

    def mk(vec):
        return (vec / np.linalg.norm(vec)).astype(np.float32)

    # good facts: mostly correct-direction + a little stem-relevance; NO surface-word overlap
    g1 = mk(0.75 * t_dir + 0.25 * s_dir)
    g2 = mk(0.72 * t_dir + 0.28 * s_dir)
    # lure facts: support the lure AND are strongly stem-surface-relevant (high goal_score too)
    L1 = mk(0.55 * l_dir + 0.83 * s_dir)
    L2 = mk(0.52 * l_dir + 0.85 * s_dir)
    L3 = mk(0.50 * l_dir + 0.87 * s_dir)
    fh_pool = np.stack([g1, g2, L1, L2, L3]).astype(np.float32)

    # lexical structure: stem shares words with the LURE choice only; lure facts carry those words
    stem_words = {"alpha", "beta", "gamma"}
    choices = ["delta epsilon", "alpha beta"]            # c_T overlap 0 ; c_L overlap 2 (standout)
    fact_word_sets = [{"delta"}, {"epsilon"},            # good facts: no stem overlap
                      {"alpha", "beta"}, {"alpha", "beta"}, {"alpha"}]  # lure facts: surface overlap
    lure_set, ov = standout_lure_choices(stem_words, choices)
    assert lure_set == {1}, f"planted: standout lure not choice 1; lure_set={lure_set} ov={ov}"

    gs = gate_scores(fh_pool, fact_word_sets, stem_words, stem_vec, choice_hd, lure_set)
    # goal_score alone must rank lure facts at the top (they are the most stem-relevant)
    top_goal = _topk_idx(gs["goal"], K_SEL)
    assert any(i >= 2 for i in top_goal), "planted: goal-only did not surface a lure fact (setup weak)"
    # gate must drop the lure facts (they carry a positive penalty and are demoted)
    assert np.sum(gs["lure_penalty"] > 0) >= 2, f"planted: suppression inert; pen={gs['lure_penalty']}"
    top_gate = _topk_idx(gs["gate"], K_SEL)
    # suppression precision: penalized facts' best-choice is the LURE (wrong), not the correct
    supp_idx = np.where(gs["lure_penalty"] > 0)[0]
    assert all(int(gs["best_choice"][i]) == 1 for i in supp_idx), "planted: suppression fired off-lure"

    # UNCHANGED combiner readout for the three selections
    QQ = mk(t_dir + l_dir + 3.0 * s_dir)                 # query ~ stem+choices (stem-surface heavy)

    def pick(sel_idx):
        fh = fh_pool[sel_idx]
        q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
        return agg._pick(sc, np.random.default_rng(0))

    pick_all = pick(np.arange(fh_pool.shape[0]))         # A_noisy
    pick_goal = pick(top_goal)                           # S_nosupp
    pick_gate = pick(top_gate)                           # B_gate
    assert pick_all == 1, f"planted: A_noisy should drown to the lure, got {pick_all}"
    assert pick_goal == 1, f"planted: S_nosupp (goal only) should still pick the lure, got {pick_goal}"
    assert pick_gate == 0, f"planted: B_gate (suppression) should recover correct, got {pick_gate}"
    # arms differ
    assert not (np.array_equal(top_gate, top_goal)), "planted: gate and goal selections identical"
    return True


def self_test():
    print("[self-test] planted surface-lure selection-gate discriminator "
          "(B flips what A/S drown; suppression load-bearing + precise) ...", flush=True)
    _planted_selection_gate_discriminator()

    print("[self-test] REAL SemanticHDEncoder + REAL PPR pool + REAL gate + UNCHANGED combiner ...", flush=True)
    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "photosynthesis produces oxygen as a byproduct for animals to breathe",
        "sunlight is a source of energy for plants",
        "iron is a heavy metal used to build bridges",
        "the moon orbits the earth once each month",
    ]
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in store_sents]
    fact_word_sets = [set(t) for t in fact_terms]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)

    SV_store = arc._encode_store(enc, store_sents)
    term_vecs = arc._encode_store(enc, vocab)

    q = {"stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar and oxygen", "the moon", "loud sound"], "correct_index": 1}
    stem_words = set(arc._content_words(q["stem"], MIN_TERM_LEN))
    q_words = sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
    q_word_vecs = arc._encode_store(enc, q_words)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    STEM = arc._encode_store(enc, [q["stem"]])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])

    # REAL spreading pool (PPR arm B) -- UNCHANGED import
    seeds = ppr.link_seeds([q_words], vocab, t2i, term_vecs, [q_word_vecs], SEED_COS)
    seed_mat = ppr.seeds_to_matrix(seeds, len(vocab))
    a = ppr.ppr_batch(seed_mat, M, HOPS, DAMP)
    fscore = ppr.fact_activation(a, Sft)[0]
    pool_idx = ppr.topk_from_scores(fscore, min(K_POOL, len(store_sents)))
    assert pool_idx.size > 0, "real: empty spreading pool"

    lure_set, _ = standout_lure_choices(stem_words, q["choices"])
    fw = [fact_word_sets[i] for i in pool_idx]
    gs = gate_scores(SV_store[pool_idx], fw, stem_words, STEM, choice_hd, lure_set)
    assert gs["gate"].shape[0] == pool_idx.size, "real: gate score shape mismatch"

    # UNCHANGED combiner reuse on a gate selection
    sel = pool_idx[_topk_idx(gs["gate"], K_SEL)]
    fh = SV_store[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == len(q["choices"]), "real: combiner reuse shape mismatch"

    # determinism of the gate
    gs2 = gate_scores(SV_store[pool_idx], fw, stem_words, STEM, choice_hd, lure_set)
    assert np.allclose(gs["gate"], gs2["gate"]), "real: gate non-deterministic"

    # McNemar sanity
    b, c, stat, p = mcnemar([1, 1, 0, 0, 1], [1, 0, 1, 1, 0])
    assert 0.0 <= p <= 1.0, "mcnemar p out of range"

    # WorldTree parse touch
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print("[self-test] PASS (planted gate flips drowned question, suppression load-bearing+precise; "
          "real encoder+PPR-pool+gate+UNCHANGED combiner; determinism; McNemar; WT parse)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (all ~9720 facts -> real pool at scale), question SUBSET
        return {"n_dim": 2048, "limit_easy": 200, "limit_chal": 150}
    return {"n_dim": 2048, "limit_easy": None, "limit_chal": None}


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    nQ = len(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f}", flush=True)

    # ---- store = FULL tablestore (gold facts are general curriculum sentences, NOT answer labels) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    print(f"[store] full tablestore = {nFacts} facts (closed-book-over-curriculum)", flush=True)

    # ---- bipartite graph + PPR pool (PPR cell functions, UNCHANGED) ----
    _heartbeat(output_dir, "build_graph")
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    fact_word_sets = [set(t) for t in fact_terms]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)
    print(f"[graph] terms={nTerms} incidence_nnz={A.nnz}", flush=True)

    # ---- encode store + questions + terms ONCE ----
    _heartbeat(output_dir, "encode_store", {"n": nFacts})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, sents)
    print(f"[encode] store {nFacts} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)

    _heartbeat(output_dir, "encode_terms", {"n": nTerms})
    term_vecs = arc._encode_store(enc, vocab)

    _heartbeat(output_dir, "encode_questions")
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]

    q_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                     for q in questions]
    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]
    uniq_words = sorted({w for ws in q_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}
    q_word_vecs_per_q = [uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)
                         for ws in q_words_per_q]

    # ---- spreading pool (PPR arm B), batched, UNCHANGED ----
    _heartbeat(output_dir, "ppr_pool")
    seeds = ppr.link_seeds(q_words_per_q, vocab, t2i, term_vecs, q_word_vecs_per_q, SEED_COS)
    seed_mat = ppr.seeds_to_matrix(seeds, nTerms)
    a_real = ppr.ppr_batch(seed_mat, M, HOPS, DAMP)
    FB = ppr.fact_activation(a_real, Sft)                     # [nQ x nFacts] arm-B activation

    # ---- gold central rows (for the oracle ceiling reference) ----
    gold_uids = sorted({u for q in questions for u in q["gold_central"] if u in uid2fi})
    uid2goldrow = {u: i for i, u in enumerate(gold_uids)}
    GV = SV_store[[uid2fi[u] for u in gold_uids]] if gold_uids else np.zeros((0, nd), np.float32)

    # ---- per-question: pool -> gate -> selections -> UNCHANGED combiner ----
    _heartbeat(output_dir, "select_and_answer")
    picks = {name: np.full(nQ, -1, dtype=np.int64) for name in ("A", "B", "S", "R", "O")}
    lure_flags = np.zeros(nQ, dtype=bool)              # eval LURE-subset membership
    n_lure_facts_in_pool = np.zeros(nQ, dtype=np.int64)
    n_supp_removed = np.zeros(nQ, dtype=np.int64)      # facts S selects but B suppresses out
    supp_fire_correct = 0
    supp_fire_wrong = 0
    glass = []

    def combiner_pick(qi, sel_idx):
        if sel_idx.size == 0:
            sc, _ = agg.aggregate(np.zeros((0, nd), np.float32), np.zeros(0, np.float32),
                                  choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
            return agg._pick(sc, np.random.default_rng(SEED + qi))
        fh = SV_store[sel_idx]
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
        return agg._pick(sc, np.random.default_rng(SEED + qi))

    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        stem_words = stem_words_per_q[qi]
        lure_flags[qi] = is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(FB[qi], K_POOL)        # the noisy spreading pool (arm B)
        fw = [fact_word_sets[i] for i in pool_idx]
        gs = gate_scores(SV_store[pool_idx], fw, stem_words, STEM[qi], choice_hd_map[qi], lure_set)

        sel_goal = _topk_idx(gs["goal"], K_SEL)                # S_nosupp local indices
        sel_gate = _topk_idx(gs["gate"], K_SEL)                # B_gate local indices
        rng_r = np.random.default_rng(SEED + 5000 + qi)
        sel_rand = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]

        A_sel = pool_idx                                       # A_noisy = whole pool
        B_sel = pool_idx[sel_gate]
        S_sel = pool_idx[sel_goal]
        R_sel = pool_idx[sel_rand]

        picks["A"][qi] = combiner_pick(qi, A_sel)
        picks["B"][qi] = combiner_pick(qi, B_sel)
        picks["S"][qi] = combiner_pick(qi, S_sel)
        picks["R"][qi] = combiner_pick(qi, R_sel)
        # oracle ceiling: gold central facts -> UNCHANGED combiner
        grows = [uid2fi[u] for u in q["gold_central"] if u in uid2fi]
        picks["O"][qi] = combiner_pick(qi, np.array(grows, dtype=np.int64))

        # diagnostics
        n_lure_facts_in_pool[qi] = int(np.sum(gs["lure_penalty"] > 0))
        removed = set(sel_goal.tolist()) - set(sel_gate.tolist())
        n_supp_removed[qi] = len(removed)
        for li in np.where(gs["lure_penalty"] > 0)[0]:
            if int(gs["best_choice"][li]) == ci:
                supp_fire_correct += 1
            else:
                supp_fire_wrong += 1

        if len(glass) < 10 and lure_flags[qi]:
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120],
                "choices": q["choices"], "correct_index": ci,
                "lure_choice_flagged": sorted(lure_set),
                "picks": {"A_noisy": int(picks["A"][qi]), "B_gate": int(picks["B"][qi]),
                          "S_nosupp": int(picks["S"][qi]), "R_random": int(picks["R"][qi]),
                          "oracle": int(picks["O"][qi])},
                "selected_B_gate": [uid2sent.get(uids[i], "")[:70] for i in B_sel[:K_SEL]],
                "suppressed_facts": [uid2sent.get(uids[pool_idx[i]], "")[:70]
                                     for i in np.where(gs["lure_penalty"] > 0)[0][:6]],
            })

    correct = {name: np.array([int(picks[name][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64)
               for name in ("A", "B", "S", "R", "O")}

    # ---- accuracy by split ----
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_chal = ~is_easy
    chal_lure = is_chal & lure_flags
    chal_nonlure = is_chal & ~lure_flags

    def acc(mask, name):
        m = correct[name][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    accs = {}
    for name in ("A", "B", "S", "R", "O"):
        accs[name] = {"easy": acc(is_easy, name), "challenge": acc(is_chal, name),
                      "chal_lure": acc(chal_lure, name), "chal_nonlure": acc(chal_nonlure, name)}
        print(f"[acc] {name}: easy={accs[name]['easy']} chal={accs[name]['challenge']} "
              f"lure={accs[name]['chal_lure']} nonlure={accs[name]['chal_nonlure']}", flush=True)

    n_lure = int(np.sum(chal_lure))
    n_nonlure = int(np.sum(chal_nonlure))

    # ---- primary discriminator: B_gate vs A_noisy on Challenge-LURE (+ McNemar) ----
    lure_lift = None
    mc_b = mc_c = 0
    mc_stat = mc_p = None
    if n_lure > 0:
        lure_lift = round((accs["B"]["chal_lure"] or 0.0) - (accs["A"]["chal_lure"] or 0.0), 4)
        mc_b, mc_c, mc_stat, mc_p = mcnemar(correct["A"][chal_lure], correct["B"][chal_lure])

    nonlure_move = None
    if n_nonlure > 0:
        nonlure_move = round((accs["B"]["chal_nonlure"] or 0.0) - (accs["A"]["chal_nonlure"] or 0.0), 4)

    supp_lift = None      # B - S on LURE (suppression load-bearing)
    rand_lift = None      # R - A on LURE (must be ~0)
    if n_lure > 0:
        supp_lift = round((accs["B"]["chal_lure"] or 0.0) - (accs["S"]["chal_lure"] or 0.0), 4)
        rand_lift = round((accs["R"]["chal_lure"] or 0.0) - (accs["A"]["chal_lure"] or 0.0), 4)

    # ---- gates ----
    A_chal = accs["A"]["challenge"] or 0.0
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    # discriminator-fires: suppression actually acted on some LURE-subset facts
    supp_fired = int(np.sum(n_supp_removed[chal_lure])) > 0 if n_lure else False
    supp_precise = supp_fire_wrong >= supp_fire_correct   # per notes: fires on WRONG >= CORRECT

    import hashlib
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ("A", "B", "S", "R")}
    arms_differ = len({digests["A"], digests["B"], digests["S"], digests["R"]}) == 4

    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    selective = (nonlure_move is None) or (abs(nonlure_move) <= SEL_NONLURE_EPS)
    supp_ok = (supp_lift is not None) and (supp_lift >= HP_SUPP)
    random_ok = (rand_lift is not None) and (rand_lift <= RANDOM_MAX)

    # ---- verdict (PRIMARY = end-to-end Challenge-LURE; judged on the ANSWER) ----
    if n_lure < 5:
        verdict = "GATE_INCONCLUSIVE_SMALL_LURE_SUBSET"
        vmsg = (f"LURE subset n={n_lure} < 5 -- too small for a decisive end-to-end test "
                f"(run FULL; smoke subsets undersample the lure stratum). "
                f"chal_lure A={accs['A']['chal_lure']} B={accs['B']['chal_lure']}.")
    elif ag_saturated:
        verdict = "GATE_DISCRIMINATOR_SATURATED"
        vmsg = (f"baseline A_noisy Challenge {A_chal} >= {AG_BASELINE_SAT}: noisy pool already saturates; "
                f"no headroom for selection (report, not a mechanism failure).")
    elif not supp_precise:
        verdict = "GATE_SUPPRESSION_ANTI_PRECISION_DISQUALIFIED"
        vmsg = (f"suppression fired on the CORRECT choice ({supp_fire_correct}) MORE than the WRONG "
                f"choice ({supp_fire_wrong}) -- crude oppose-signal disqualified per notes anti-precision "
                f"guard. LURE lift {lure_lift} is not trustworthy; a precision-tested contradiction "
                f"detector is the next step (do NOT re-tune thresholds).")
    elif (lure_lift is not None and lure_lift >= HP_LURE_LIFT and sig and selective
          and supp_ok and random_ok):
        verdict = "GATE_HARD_PASS"
        vmsg = (f"SELECTION GATE beats the noisy pool ON THE ANSWER: Challenge-LURE B_gate "
                f"{accs['B']['chal_lure']} vs A_noisy {accs['A']['chal_lure']} (lift {lure_lift:+.4f} "
                f">= {HP_LURE_LIFT}); McNemar b={mc_b} c={mc_c} stat={mc_stat:.2f} p={mc_p:.4f} "
                f"(<{MCNEMAR_ALPHA}); NON-LURE move {nonlure_move:+.4f} (selective, |.|<={SEL_NONLURE_EPS}); "
                f"suppression load-bearing B-S={supp_lift:+.4f} (>={HP_SUPP}); RANDOM control R-A="
                f"{rand_lift:+.4f} (<={RANDOM_MAX}, fewer-facts is NOT the driver). suppression precision "
                f"wrong/correct={supp_fire_wrong}/{supp_fire_correct}. Ceiling oracle-gold Chal-LURE "
                f"{accs['O']['chal_lure']}.")
    elif lure_lift is not None and lure_lift >= MB_LURE_LIFT:
        verdict = "GATE_MIDDLE_BAND"
        vmsg = (f"MIDDLE: Challenge-LURE lift {lure_lift:+.4f} in [{MB_LURE_LIFT},{HP_LURE_LIFT}) OR a gate "
                f"unmet -- McNemar p={mc_p} (sig={sig}), selective={selective} (nonlure {nonlure_move}), "
                f"suppression B-S={supp_lift} (ok={supp_ok}), random R-A={rand_lift} (ok={random_ok}). "
                f"Selection helps but not decisively. B_gate Chal={accs['B']['challenge']} "
                f"vs A_noisy {accs['A']['challenge']}.")
    else:
        verdict = "GATE_HARD_FAIL"
        vmsg = (f"MECHANISM HARD_FAIL: selection gate does NOT beat the noisy pool on the answer "
                f"(Challenge-LURE B_gate {accs['B']['chal_lure']} vs A_noisy {accs['A']['chal_lure']}, "
                f"lift {lure_lift} < {MB_LURE_LIFT}). Per pre-reg -> the COMBINER itself (not the pool) is "
                f"the wall: even a clean selected pool does not lift the answer. Random R-A={rand_lift}, "
                f"suppression B-S={supp_lift}. Redirect to the combiner (contradiction/precision), not "
                f"more retrieval. oracle-gold ceiling Chal-LURE={accs['O']['chal_lure']} "
                f"(headroom exists; combiner cannot use the clean pool).")

    grade = arc._grade_proxy(accs["B"]["easy"], accs["B"]["challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [Chal-LURE n={n_lure}] A={accs['A']['chal_lure']} B={accs['B']['chal_lure']} "
                    f"S={accs['S']['chal_lure']} R={accs['R']['chal_lure']} O={accs['O']['chal_lure']} | "
                    f"lift(B-A)={lure_lift} McNemar_p={mc_p} | nonlure_move={nonlure_move} | "
                    f"supp(B-S)={supp_lift} rand(R-A)={rand_lift} | [Chal-all] A={accs['A']['challenge']} "
                    f"B={accs['B']['challenge']} | chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_chal_lure": n_lure, "n_chal_nonlure": n_nonlure,
        "chance_theoretical": round(chance, 4),
        # gate config
        "k_pool": K_POOL, "k_sel": K_SEL, "lambda_disc": LAMBDA_DISC, "mu_supp": MU_SUPP,
        "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        # PRIMARY: end-to-end accuracy by split (judged on the ANSWER, not recall)
        "acc_by_arm": accs,   # each arm: easy / challenge / chal_lure / chal_nonlure
        "lure_lift_B_minus_A": lure_lift,
        "mcnemar_lure": {"b_A_right_B_wrong": mc_b, "c_A_wrong_B_right": mc_c,
                         "stat": None if mc_stat is None else round(mc_stat, 4),
                         "p_value": None if mc_p is None else round(mc_p, 5),
                         "significant": bool(sig)},
        "nonlure_move_B_minus_A": nonlure_move,
        "selective_to_lure": bool(selective),
        "suppression_lift_B_minus_S": supp_lift,
        "suppression_load_bearing": bool(supp_ok),
        "random_lift_R_minus_A": rand_lift,
        "random_control_ok": bool(random_ok),
        # suppression firing / precision (uses gold ONLY for measurement, never in the gate)
        "suppression_fire_on_correct": supp_fire_correct,
        "suppression_fire_on_wrong": supp_fire_wrong,
        "suppression_precise": bool(supp_precise),
        "suppression_fired_on_lure_subset": bool(supp_fired),
        "n_supp_removed_total": int(np.sum(n_supp_removed)),
        "n_lure_facts_in_pool_total": int(np.sum(n_lure_facts_in_pool)),
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band),
        "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ),
        "arm_pick_digests": digests,
        "bands": {"HP_lure_lift": HP_LURE_LIFT, "MB_lure_lift": MB_LURE_LIFT, "HP_supp": HP_SUPP,
                  "random_max": RANDOM_MAX, "sel_nonlure_eps": SEL_NONLURE_EPS,
                  "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the STAGE-5 RETRIEVAL SELECTION GATE inserted BEFORE the UNCHANGED bind+settle "
            "combiner (agg.aggregate 'bundle', imported) over the UNCHANGED PPR spreading pool (arm B, "
            "imported). gate_score = goal_score (relu cos-to-STEM + choice-separating margin) - MU * "
            "lure_penalty (fact-stem Jaccard * fact-supports-the-standout-surface-lure). Arms A_noisy "
            "(whole pool), B_gate (goal-bias+suppression), S_nosupp (goal-bias only = suppression-off "
            "ablation), R_random (must-fail), oracle-gold ceiling. PRIMARY = end-to-end ARC accuracy, "
            "Easy+Challenge, ESPECIALLY the Challenge-LURE subset (distractor out-overlaps correct); "
            "McNemar A-vs-B on LURE; NON-LURE selectivity; suppression-precision (fires on WRONG not "
            "CORRECT choice). GATE IS ANSWER-AGNOSTIC (never uses gold); the LURE-subset partition and "
            "the precision counters use gold for EVALUATION only. "
            "STUBBED/NOTED-NOT-BUILT: controlled RE-RETRIEVAL (query reformulation + second PPR pass) -- "
            "this cell tests suppression+selection first, the cheaper half of the notes' two-part probe; "
            "if HARD_PASS, re-retrieval is the follow-up. Signed contradiction detector left to the "
            "combiner cell (orthogonal)."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING",
        "compute_architecture": "mixed CPU: batched GloVe encode + scipy.sparse batched PPR (imported) + cheap per-question gate + UNCHANGED combiner; wall target < 5min",
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": "default_ok_for_this_regime (gate hyperparams author-set a priori; NOT tuned to force a win)",
    }
    _write_metrics_atomic(output_dir, metrics)

    try:
        with open(os.path.join(output_dir, "glassbox_sample.json"), "w", encoding="utf-8") as f:
            json.dump(glass, f, indent=2)
    except Exception as e:
        print(f"[warn] glassbox persist failed (non-fatal): {e}", flush=True)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)
    return metrics


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)
    run(args.mode, output_dir)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
