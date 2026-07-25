"""arc_selection_precision_coherence_subset_v1 -- MAX SELECTION PRECISION, the VET-confirmed wall.

The max-retrieval diagnostic (29543) PROVED reachability is SOLVED: the WIDE re-retrieval pool
(RR top-100) has recall@100=0.69 of the gold central facts and an ALL-REACHABLE ceiling of 1.0 --
the pool CONTAINS the gold facts. MEASURED@disk:
  wide pool recall@100 (SC)             = 0.6911
  E_wide_gate Challenge (current gate)  = 0.3306
  E_oracle  Challenge (gold->combiner)  = 0.7125
    @data/exp_arc_retrieval_max_recall_ksweep_reretrieval_v1/metrics.json
But a wide high-recall pool does NOT lift the answer (E_wide_gate 0.3306 vs narrow gate 0.3368,
statistically flat): the gate+combiner picks a surface-LURE while an oracle handed the exact gold
facts reaches 0.7125. The pool CONTAINS the gold; SELECTION cannot ISOLATE it. The wall relocated
from retrieval to SELECTION-PRECISION. The ENTIRE remaining gap 0.33 -> 0.71 on Challenge is
selection.

ONE variable = the SELECTION SIGNAL that picks K_SEL facts from the UNCHANGED wide pool; the
UNCHANGED bind+bundle combiner (agg.aggregate 'bundle', imported) reads out the answer. Selection
signals (brain-faithful VLPFC post-retrieval selection; Badre & Wagner 2007; Kintsch CI / Thagard
ECHO coherence):
  A_gate  -- current gate.gate_scores (stem-cos goal-bias + RIF suppression)  [BASELINE=E_wide_gate]
  REL     -- goal-biased relevance to the answer-SET: relu(cos f,STEM)+mean_c relu(cos f,choice_c)
  COH     -- COHERENCE-SUBSET (the KEY hypothesis): Kintsch/ECHO settle over the signed fact-fact
             coherence matrix (agg._relax, UNCHANGED settle math), seeded by relevance; select the
             facts with highest SETTLED activation = the subset that COHERES into one explanation.
             The coherent gold subset reinforces; incoherent lures lose share.
  DISC    -- discriminative: facts that most separate ONE choice from the rest (answer-agnostic
             margin max_c cos - 2nd_max_c cos); judged on the ANSWER now (not recall).
  COMB    -- relevance + coherence + discriminative (min-max normed) - MU*suppression, combined.
  RND     -- K_SEL random pool facts                                          [MUST-FAIL control]
  ORACLE  -- gold central facts -> combiner                                   [CEILING ~0.71]
ALL selection signals are ANSWER-AGNOSTIC (never see the correct index or the gold uids). Gold is
used ONLY for the ORACLE arm and for evaluation (accuracy, selection-precision-vs-gold).

PRIMARY = end-to-end ARC accuracy, Easy + Challenge, judged on the ANSWER (NOT recall), over the
WIDE pool. HARD_PASS = a selection signal closes a MATERIAL fraction of the 0.33->0.71 Challenge gap
(pre-reg margin, McNemar significance vs A_gate) AND random-select does NOT. HARD_FAIL = no selection
signal beats the current gate -> selection-precision from a contains-gold pool is itself the hard
wall -> report straight (the lever is then deeper meaning/grounding for relevance, the relocated
hypothesis). SECONDARY = selection PRECISION vs gold (does the signal pick more gold facts?) --
diagnostic; the ANSWER is primary.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT
remote-portable); NO push/remote-persist; ASCII-only; deterministic (fixed seeds, numpy default_rng,
sorted iteration, no hash()); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL RR wide pool + REAL selection
#   signals (REL/COH/DISC) + UNCHANGED combiner at tiny scale; a PLANTED coherence-subset case asserts
#   the COH discriminator FIRES (COH flips a question REL drowns => coherence load-bearing); arms-differ
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration; no hash()
# - baseline_in_band + AG-guard on A_gate challenge (headroom to the 0.71 ceiling)
# - storage = SHARDED (each fact = own vector + own graph node; no superposition)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse (UNCHANGED): the WIDE RR pool builder, the current selection gate, the bind+settle combiner,
# the PPR graph, arc helpers. The ONLY new code is the SELECTION SIGNALS (REL / COH / DISC / COMB).
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (
    SemanticHDEncoder, _load_glove, _load_wordnet)

ANCHOR_NAME = "arc_selection_precision_coherence_subset_v1"
SEED = 20260726

# ---- selection hyperparams (author-designed a priori; see pre-reg) ----
K_WIDE = mr.K_WIDE          # UNCHANGED wide re-retrieval pool the signals select FROM (=100)
RR_TOP_T = mr.RR_TOP_T      # UNCHANGED re-retrieval reformulation depth
K_SEL = gate.K_SEL          # UNCHANGED clean-fact selection width (Cowan-4; =4)
MU_SUPP = gate.MU_SUPP      # UNCHANGED suppression weight in the COMB arm
SETTLE_T = agg.SETTLE_T     # UNCHANGED Kintsch CI iteration cap (=50)
SETTLE_EPS = agg.SETTLE_EPS # UNCHANGED Kintsch convergence epsilon (=1e-3)
# pool-construction constants (reused UNCHANGED from the PPR cell)
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# ---- bands (author-designed a priori; PRIMARY = end-to-end Challenge accuracy, judged on ANSWER) ----
# gap to close = oracle-gold Challenge (~0.71) - current gate Challenge (~0.33) ~= 0.38.
HP_CHAL_LIFT = 0.05    # best selection arm - A_gate on Challenge (>= ~13% of the 0.38 gap)
MB_CHAL_LIFT = 0.02    # positive-but-sub-HP band floor
RANDOM_MAX = 0.02      # RND - A_gate on Challenge must be <= this (fewer-facts is not the driver)
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95 # A_gate challenge >= this -> vacuous (no headroom)


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
# the SELECTION SIGNALS (the ONE new piece; all ANSWER-AGNOSTIC)
# ---------------------------------------------------------------------------
def _minmax(x):
    """Per-question min-max normalize a score vector to [0,1] (flat -> zeros)."""
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return x
    lo = float(x.min())
    hi = float(x.max())
    if hi - lo <= 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def relevance_score(fh_pool, stem_vec, choice_hd):
    """Goal-biased relevance to the answer-SET: relu(cos f,STEM) + mean_c relu(cos f,choice_c).
    Rewards facts relevant to the question topic INCLUDING any answer choice (not the separating
    margin). Answer-agnostic. Returns [P]."""
    P = fh_pool.shape[0]
    if P == 0:
        return np.zeros(0, dtype=np.float64)
    stem_rel = np.maximum(fh_pool @ stem_vec, 0.0)               # [P]
    cc = np.maximum(fh_pool @ choice_hd.T, 0.0)                  # [P, C] relu cos to each choice
    ans_rel = cc.mean(axis=1) if cc.shape[1] else np.zeros(P)
    return (stem_rel + ans_rel).astype(np.float64)


def discriminative_score(fh_pool, choice_hd):
    """Choice-separating margin: max_c cos(f,choice_c) - 2nd_max_c. Facts that sharply favor ONE
    choice over the rest. Answer-agnostic (does NOT know which choice is correct). Returns [P]."""
    P = fh_pool.shape[0]
    if P == 0:
        return np.zeros(0, dtype=np.float64)
    cc = (fh_pool @ choice_hd.T).astype(np.float64)             # [P, C]
    if cc.shape[1] >= 2:
        part = np.sort(cc, axis=1)
        return (part[:, -1] - part[:, -2]).astype(np.float64)
    return cc.max(axis=1).astype(np.float64)


def coherence_score(fh_pool, af0):
    """COHERENCE-SUBSET (the key hypothesis): Kintsch/ECHO settle over the SIGNED fact-fact coherence
    matrix FF=cos(f_i,f_j) (positive=consistent/shared meaning, negative=contradiction), seeded by the
    top-down relevance af0. Reuses the UNCHANGED combiner settle math agg._relax. The subset that
    COHERES into one explanation reinforces (positive edges); incoherent/contradictory lures lose
    share. Returns the SETTLED per-fact activation [P] (caller selects top-K_SEL). Answer-agnostic."""
    P = fh_pool.shape[0]
    if P <= 1:
        return np.ones(P, dtype=np.float64)
    FF = (fh_pool @ fh_pool.T).astype(np.float64)               # signed fact-fact coherence
    np.fill_diagonal(FF, 0.0)
    a0 = np.maximum(np.asarray(af0, dtype=np.float64), 0.0)
    if a0.sum() <= 0:
        a0 = np.ones(P, dtype=np.float64)
    af, _, _, _ = agg._relax(FF, a0, SETTLE_T, SETTLE_EPS)      # UNCHANGED settle
    return af.astype(np.float64)


def _topk_idx(scores, k):
    """Indices of the top-k scores (descending, stable ties by index). Reuse gate helper semantics."""
    return gate._topk_idx(np.asarray(scores, dtype=np.float64), k)


# ---------------------------------------------------------------------------
# self-test: real code path + planted coherence-subset discriminator + arms-differ + determinism
# ---------------------------------------------------------------------------
def _planted_coherence_subset_discriminator():
    """Synthetic HD case proving COHERENCE selection is load-bearing and reachable.
    choices: c_T (correct), c_L (lure).
    Wide pool: 3 GOLD facts support c_T, MUTUALLY COHERENT (near a shared gold direction), only
      MODERATE stem-relevance; 4 LURE facts each individually HIGH stem-relevance + support c_L but
      MUTUALLY INCOHERENT (spread across contradictory directions -> negative fact-fact edges).
    Under the UNCHANGED bundle combiner:
      REL (relevance)  -> the 4 high-stem-relevance lure facts rank top -> picks c_L (WRONG)
      COH (coherence)  -> gold facts reinforce (positive edges), lures lose share -> gold selected ->
                          picks c_T (RIGHT)
    => coherence-subset is LOAD-BEARING (COH flips what REL drowns); the discriminator is reachable."""
    N = 512
    rng = np.random.default_rng(23)

    def orth(v, *against):
        for a in against:
            v = v - v.dot(a) * a
        return v / np.linalg.norm(v)

    t_dir = orth(rng.standard_normal(N))                 # correct-choice direction
    l_dir = orth(rng.standard_normal(N), t_dir)          # lure-choice direction
    s_dir = orth(rng.standard_normal(N), t_dir, l_dir)   # "stem surface" direction (relevance)
    # four independent lure-scatter directions (make lures MUTUALLY incoherent)
    d1 = orth(rng.standard_normal(N), t_dir, l_dir, s_dir)
    d2 = orth(rng.standard_normal(N), t_dir, l_dir, s_dir, d1)
    d3 = orth(rng.standard_normal(N), t_dir, l_dir, s_dir, d1, d2)
    d4 = orth(rng.standard_normal(N), t_dir, l_dir, s_dir, d1, d2, d3)
    choice_hd = np.stack([t_dir, l_dir]).astype(np.float32)   # C0 correct, C1 lure
    stem_vec = s_dir.astype(np.float32)

    def mk(vec):
        return (vec / np.linalg.norm(vec)).astype(np.float32)

    # GOLD facts: strongly aligned to a SHARED gold direction (t_dir) -> mutually coherent;
    # only moderate stem-surface relevance.
    g1 = mk(0.90 * t_dir + 0.20 * s_dir)
    g2 = mk(0.88 * t_dir + 0.22 * s_dir)
    g3 = mk(0.92 * t_dir + 0.18 * s_dir)
    # LURE facts: HIGH stem-surface relevance + support the lure, but each pulled into a DIFFERENT
    # scatter direction so they do NOT cohere with each other.
    L1 = mk(0.35 * l_dir + 0.70 * s_dir + 0.55 * d1)
    L2 = mk(0.35 * l_dir + 0.70 * s_dir + 0.55 * d2)
    L3 = mk(0.35 * l_dir + 0.70 * s_dir + 0.55 * d3)
    L4 = mk(0.35 * l_dir + 0.70 * s_dir + 0.55 * d4)
    fh_pool = np.stack([g1, g2, g3, L1, L2, L3, L4]).astype(np.float32)
    gold_idx = {0, 1, 2}
    lure_idx = {3, 4, 5, 6}

    rel = relevance_score(fh_pool, stem_vec, choice_hd)
    # relevance ranks the lures on top (they carry the stem-surface direction)
    top_rel = set(int(i) for i in _topk_idx(rel, K_SEL))
    assert top_rel & lure_idx, f"planted: relevance did not surface a lure (setup weak); top_rel={top_rel}"
    assert len(top_rel & gold_idx) < 3, f"planted: relevance already picks all gold; top_rel={top_rel}"

    coh = coherence_score(fh_pool, af0=np.maximum(rel, 0.0))
    top_coh = set(int(i) for i in _topk_idx(coh, K_SEL))
    # coherence must recover the coherent gold subset
    assert len(top_coh & gold_idx) >= 3, f"planted: coherence did not recover the gold subset; top_coh={top_coh}"

    # UNCHANGED combiner readout on the two selections
    QQ = mk(t_dir + l_dir + 3.0 * s_dir)                 # query ~ stem+choices (stem-surface heavy)

    def pick(sel_local):
        fh = fh_pool[np.array(sorted(sel_local), dtype=np.int64)]
        q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
        return agg._pick(sc, np.random.default_rng(0))

    pick_rel = pick(top_rel)
    pick_coh = pick(top_coh)
    assert pick_rel == 1, f"planted: REL should drown to the lure, got {pick_rel}"
    assert pick_coh == 0, f"planted: COH should recover the correct choice, got {pick_coh}"
    # arms differ
    assert top_rel != top_coh, "planted: REL and COH selections identical"
    # determinism of the coherence settle
    coh2 = coherence_score(fh_pool, af0=np.maximum(rel, 0.0))
    assert np.allclose(coh, coh2), "planted: coherence settle non-deterministic"
    return True


def self_test():
    print("[self-test] planted coherence-subset discriminator "
          "(COH recovers the coherent gold subset REL drowns; combiner flips) ...", flush=True)
    _planted_coherence_subset_discriminator()

    print("[self-test] REAL encoder + REAL RR wide pool + REAL selection signals + UNCHANGED combiner ...",
          flush=True)
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
    sc_words = sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
    sc_word_vecs = arc._encode_store(enc, sc_words)
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    STEM = arc._encode_store(enc, [q["stem"]])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])

    # REAL WIDE RR pool (max-recall cell path, UNCHANGED import) ------------------------------------
    seeds_sc = ppr.link_seeds([sc_words], vocab, t2i, term_vecs, [sc_word_vecs], SEED_COS)
    sm_sc = ppr.seeds_to_matrix(seeds_sc, len(vocab))
    F_SC = ppr.fact_activation(ppr.ppr_batch(sm_sc, M, HOPS, DAMP), Sft)
    seeds2 = mr.reformulate_seeds(F_SC, seeds_sc, fact_terms, t2i, RR_TOP_T)
    F_P2 = ppr.fact_activation(ppr.ppr_batch(ppr.seeds_to_matrix(seeds2, len(vocab)), M, HOPS, DAMP), Sft)
    F_RR = mr._rownorm_scores(F_SC) + mr._rownorm_scores(F_P2)
    pool_idx = ppr.topk_from_scores(F_RR[0], min(K_WIDE, len(store_sents)))
    assert pool_idx.size > 0, "real: empty RR wide pool"
    fh_pool = SV_store[pool_idx]

    # REAL selection signals ------------------------------------------------------------------------
    rel = relevance_score(fh_pool, STEM, choice_hd)
    disc = discriminative_score(fh_pool, choice_hd)
    coh = coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ, 0.0))
    assert rel.shape[0] == disc.shape[0] == coh.shape[0] == pool_idx.size, "real: signal shape mismatch"
    # A_gate baseline signal (UNCHANGED gate)
    lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])
    fw = [fact_word_sets[i] for i in pool_idx.tolist()]
    gs = gate.gate_scores(fh_pool, fw, stem_words, STEM, choice_hd, lure_set)
    assert gs["gate"].shape[0] == pool_idx.size, "real: gate score shape mismatch"
    # combined signal
    comb = _minmax(rel) + _minmax(coh) + _minmax(disc) - MU_SUPP * gs["lure_penalty"]
    assert comb.shape[0] == pool_idx.size, "real: combined shape mismatch"

    # UNCHANGED combiner over a coherence selection
    sel = pool_idx[_topk_idx(coh, K_SEL)]
    fh = SV_store[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc_scores, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc_scores.shape[0] == len(q["choices"]), "real: combiner reuse shape mismatch"

    # determinism
    coh_b = coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ, 0.0))
    assert np.allclose(coh, coh_b), "real: coherence settle non-deterministic"

    # WorldTree parse touch
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    qs = agg.load_wt_questions(limit_easy=5, limit_chal=5)
    assert len(qs) >= 5 and all("gold_central" in x for x in qs), "question parse failed"
    print("[self-test] PASS (planted coherence-subset flips REL-drowned question; real encoder+RR pool+"
          "REL/COH/DISC/COMB signals+UNCHANGED combiner; determinism; WT parse)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        # FULL graph (all ~9720 facts -> real pool at scale), question SUBSET
        return {"n_dim": 2048, "limit_easy": 150, "limit_chal": 150}
    # FULL: bounded eval slice to fit one INLINE-LOCAL foreground call (mirrors the max-recall cell
    # slice that ran in ~108s: K_WIDE=100 pool + coherence settle + 7 arms over ~1087 questions).
    return {"n_dim": 2048, "limit_easy": 500, "limit_chal": 600}


ARMS = ("A_gate", "REL", "COH", "DISC", "COMB", "RND", "ORACLE")
SEL_ARMS = ("REL", "COH", "DISC", "COMB")   # the mechanism arms compared to A_gate baseline


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

    # ---- store = FULL tablestore (gold included; closed-book-over-curriculum) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    print(f"[store] full tablestore = {nFacts} facts", flush=True)

    # ---- bipartite graph + PPR transition (UNCHANGED) ----
    _heartbeat(output_dir, "build_graph")
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    fact_word_sets = [set(t) for t in fact_terms]
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)
    print(f"[graph] terms={nTerms} incidence_nnz={A.nnz}", flush=True)

    # ---- encode store + questions + term vocab ONCE ----
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

    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]
    sc_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                      for q in questions]
    uniq_words = sorted({w for ws in sc_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}

    def wvecs(ws):
        return uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)

    # ---- WIDE RR pool (max-recall cell path, UNCHANGED): SC pass-1 UNION reformulated pass-2 ----
    _heartbeat(output_dir, "ppr_wide_pool")
    seeds_sc = ppr.link_seeds(sc_words_per_q, vocab, t2i, term_vecs, [wvecs(ws) for ws in sc_words_per_q], SEED_COS)
    sm_sc = ppr.seeds_to_matrix(seeds_sc, nTerms)
    F_SC = ppr.fact_activation(ppr.ppr_batch(sm_sc, M, HOPS, DAMP), Sft)
    seeds2 = mr.reformulate_seeds(F_SC, seeds_sc, fact_terms, t2i, RR_TOP_T)
    F_P2 = ppr.fact_activation(ppr.ppr_batch(ppr.seeds_to_matrix(seeds2, nTerms), M, HOPS, DAMP), Sft)
    F_RR = mr._rownorm_scores(F_SC) + mr._rownorm_scores(F_P2)   # the WIDE pool score (UNCHANGED)

    # ---- per-question: WIDE pool -> SELECTION SIGNAL -> UNCHANGED combiner ----
    _heartbeat(output_dir, "select_and_answer")
    picks = {name: np.full(nQ, -1, dtype=np.int64) for name in ARMS}
    lure_flags = np.zeros(nQ, dtype=bool)
    # selection-precision-vs-gold accumulators (diagnostic; gold used for EVAL only)
    sel_gold_hit = {name: [] for name in ARMS}   # per-question: (#selected that are gold)/K_SEL
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
        lure_flags[qi] = gate.is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(F_RR[qi], K_WIDE)       # the UNCHANGED wide pool
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        fw = [fact_word_sets[i] for i in pool_idx.tolist()]

        # signals (all answer-agnostic)
        rel = relevance_score(fh_pool, STEM[qi], chd)
        disc = discriminative_score(fh_pool, chd)
        coh = coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)  # A_gate baseline
        comb = _minmax(rel) + _minmax(coh) + _minmax(disc) - MU_SUPP * gs["lure_penalty"]

        # selections (local indices into pool_idx)
        sel_local = {
            "A_gate": _topk_idx(gs["gate"], K_SEL),
            "REL": _topk_idx(rel, K_SEL),
            "COH": _topk_idx(coh, K_SEL),
            "DISC": _topk_idx(disc, K_SEL),
            "COMB": _topk_idx(comb, K_SEL),
        }
        rng_r = np.random.default_rng(SEED + 7000 + qi)
        sel_local["RND"] = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]

        gold_rows = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)
        gold_set = set(int(g) for g in gold_rows.tolist())

        for name in SEL_ARMS + ("A_gate", "RND"):
            sel_glob = pool_idx[sel_local[name]]
            picks[name][qi] = combiner_pick(qi, sel_glob)
            denom = min(K_SEL, sel_glob.size) if sel_glob.size else 1
            sel_gold_hit[name].append(sum(1 for g in sel_glob.tolist() if g in gold_set) / denom)
        picks["ORACLE"][qi] = combiner_pick(qi, gold_rows)
        sel_gold_hit["ORACLE"].append(1.0 if gold_rows.size else 0.0)

        if len(glass) < 12 and lure_flags[qi]:
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"], "correct_index": ci,
                "n_gold_in_store": len(gold_set),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "COH_selected": [uid2sent.get(uids[i], "")[:70] for i in pool_idx[sel_local["COH"]].tolist()],
                "REL_selected": [uid2sent.get(uids[i], "")[:70] for i in pool_idx[sel_local["REL"]].tolist()],
                "COH_selected_gold": [int(i in gold_set) for i in pool_idx[sel_local["COH"]].tolist()],
                "REL_selected_gold": [int(i in gold_set) for i in pool_idx[sel_local["REL"]].tolist()],
            })

    correct = {name: np.array([int(picks[name][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64) for name in ARMS}

    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_chal = ~is_easy
    chal_lure = is_chal & lure_flags

    def acc(mask, name):
        m = correct[name][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    accs = {}
    for name in ARMS:
        accs[name] = {"easy": acc(is_easy, name), "challenge": acc(is_chal, name),
                      "chal_lure": acc(chal_lure, name),
                      "chal_correct": int(np.sum(correct[name][is_chal])),
                      "chal_n": int(np.sum(is_chal)),
                      "sel_gold_precision": round(float(np.mean([sel_gold_hit[name][qi]
                                                   for qi in range(nQ) if is_chal[qi]])), 4)
                      if int(np.sum(is_chal)) else None}
        print(f"[acc] {name}: easy={accs[name]['easy']} chal={accs[name]['challenge']} "
              f"lure={accs[name]['chal_lure']} sel_gold_prec={accs[name]['sel_gold_precision']}", flush=True)

    # ---- PRIMARY discriminator: best selection arm vs A_gate on CHALLENGE (judged on the ANSWER) ----
    A_chal = accs["A_gate"]["challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["challenge"] or 0.0
    gap = round(oracle_chal - A_chal, 4)
    arm_lift = {name: round((accs[name]["challenge"] or 0.0) - A_chal, 4) for name in SEL_ARMS}
    best_arm = max(SEL_ARMS, key=lambda n: arm_lift[n])
    best_lift = arm_lift[best_arm]
    gap_frac_closed = round(best_lift / gap, 4) if gap > 1e-9 else None
    rand_lift = round((accs["RND"]["challenge"] or 0.0) - A_chal, 4)

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_gate"][is_chal], correct[best_arm][is_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    random_ok = rand_lift <= RANDOM_MAX

    # ---- integrity gates ----
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in ("A_gate", "REL", "COH", "DISC", "COMB", "RND")))
    arms_differ = n_distinct >= 4

    # ---- verdict (PRIMARY = end-to-end Challenge accuracy; judged on the ANSWER) ----
    if ag_saturated:
        verdict = "SELECTION_DISCRIMINATOR_SATURATED"
        vmsg = (f"baseline A_gate Challenge {A_chal} >= {AG_BASELINE_SAT}: no headroom for selection "
                f"(report, not a mechanism failure).")
    elif not arms_differ:
        verdict = "SELECTION_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"selection arms produced < 4 distinct pick-vectors (n_distinct={n_distinct}); arm "
                f"implementation bug -- do NOT trust the accuracy comparison.")
    elif best_lift >= HP_CHAL_LIFT and sig and random_ok:
        verdict = "SELECTION_HARD_PASS"
        vmsg = (f"SELECTION SIGNAL closes a MATERIAL fraction of the selection gap ON THE ANSWER: "
                f"best arm {best_arm} Challenge {accs[best_arm]['challenge']} vs A_gate {A_chal} "
                f"(lift {best_lift:+.4f} >= {HP_CHAL_LIFT}; {gap_frac_closed} of the {gap} gap to oracle "
                f"{oracle_chal}); McNemar b={mc_b} c={mc_c} stat={mc_stat:.2f} p={mc_p:.4f} "
                f"(<{MCNEMAR_ALPHA}); RANDOM control R-A_gate={rand_lift:+.4f} (<={RANDOM_MAX}, fewer-facts "
                f"is NOT the driver). Selection-precision-vs-gold {best_arm}={accs[best_arm]['sel_gold_precision']} "
                f"vs A_gate {accs['A_gate']['sel_gold_precision']}. Per-arm lifts: {arm_lift}.")
    elif best_lift >= MB_CHAL_LIFT:
        verdict = "SELECTION_MIDDLE_BAND"
        vmsg = (f"MIDDLE: best arm {best_arm} Challenge lift {best_lift:+.4f} in [{MB_CHAL_LIFT},"
                f"{HP_CHAL_LIFT}) OR a gate unmet -- McNemar p={mc_p} (sig={sig}), random R-A_gate="
                f"{rand_lift} (ok={random_ok}). Selection helps but not decisively "
                f"({gap_frac_closed} of the {gap} gap). Per-arm lifts: {arm_lift}. "
                f"best arm Chal={accs[best_arm]['challenge']} vs A_gate {A_chal}, oracle {oracle_chal}.")
    else:
        verdict = "SELECTION_HARD_FAIL"
        vmsg = (f"HONEST WALL: NO selection signal beats the current gate on the answer (best arm "
                f"{best_arm} Challenge {accs[best_arm]['challenge']} vs A_gate {A_chal}, lift {best_lift:+.4f} "
                f"< {MB_CHAL_LIFT}). Selection-precision from a contains-gold pool (recall@100=0.69, oracle "
                f"{oracle_chal}) is ITSELF the hard wall. Per-arm lifts {arm_lift}; random R-A_gate={rand_lift}. "
                f"Redirect: the lever is DEEPER meaning/grounding for relevance (the relocated hypothesis), "
                f"NOT more retrieval or a re-tuned surface gate. sel_gold_precision best_arm="
                f"{accs[best_arm]['sel_gold_precision']} A_gate={accs['A_gate']['sel_gold_precision']} "
                f"oracle={accs['ORACLE']['sel_gold_precision']}.")

    grade = arc._grade_proxy(accs[best_arm]["easy"], accs[best_arm]["challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [Chal] A_gate={A_chal} REL={accs['REL']['challenge']} "
                    f"COH={accs['COH']['challenge']} DISC={accs['DISC']['challenge']} "
                    f"COMB={accs['COMB']['challenge']} RND={accs['RND']['challenge']} "
                    f"ORACLE={oracle_chal} | best={best_arm} lift={best_lift:+.4f} "
                    f"gap_frac={gap_frac_closed} McNemar_p={mc_p} rand_lift={rand_lift} | "
                    f"chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_chal_lure": int(np.sum(chal_lure)),
        "chance_theoretical": round(chance, 4),
        "store_facts": nFacts, "graph_terms": nTerms,
        # selection config
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "settle_t": SETTLE_T, "settle_eps": SETTLE_EPS,
        "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        # PRIMARY: end-to-end accuracy by arm (judged on the ANSWER, not recall)
        "acc_by_arm": accs,      # each arm: easy / challenge / chal_lure / sel_gold_precision
        "A_gate_challenge": A_chal,
        "oracle_gold_challenge": oracle_chal,
        "selection_gap": gap,
        "arm_lift_challenge": arm_lift,     # each SEL arm minus A_gate on Challenge
        "best_arm": best_arm, "best_lift_challenge": best_lift,
        "gap_fraction_closed": gap_frac_closed,
        "random_lift_challenge": rand_lift, "random_control_ok": bool(random_ok),
        "mcnemar_challenge": {"arm": best_arm, "b_A_right_arm_wrong": mc_b,
                              "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        # SECONDARY diagnostic: selection precision vs gold (gold for EVAL only)
        "sel_gold_precision_by_arm": {name: accs[name]["sel_gold_precision"] for name in ARMS},
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "bands": {"HP_chal_lift": HP_CHAL_LIFT, "MB_chal_lift": MB_CHAL_LIFT, "random_max": RANDOM_MAX,
                  "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: SELECTION is the ONLY variable. The WIDE re-retrieval pool (RR top-100, max-recall "
            "cell mr.reformulate_seeds/_rownorm_scores, IMPORTED UNCHANGED) and the bind+bundle combiner "
            "(agg.aggregate 'bundle', IMPORTED UNCHANGED) are held fixed; the ONE new piece is the "
            "selection signal that picks K_SEL=4 facts from the pool. Arms: A_gate (current gate "
            "gate.gate_scores baseline = E_wide_gate analog), REL (goal-biased answer-SET relevance), "
            "COH (COHERENCE-SUBSET: agg._relax Kintsch/ECHO settle over the signed fact-fact coherence "
            "matrix seeded by relevance, select highest settled activation = the coherent subset), DISC "
            "(choice-separating margin, answer-agnostic), COMB (min-max normed REL+COH+DISC - MU*RIF "
            "suppression), RND (random-select MUST-FAIL), ORACLE (gold->combiner ceiling ~0.71). ALL "
            "selection signals ANSWER-AGNOSTIC (never see correct index or gold uids). PRIMARY = "
            "end-to-end ARC Challenge accuracy judged on the ANSWER; McNemar best-arm vs A_gate; RANDOM "
            "must-fail. SECONDARY = selection-precision vs gold (diagnostic). Gold used ONLY for the "
            "ORACLE arm + evaluation. "
            "STUBBED/NOTED-NOT-BUILT: triggered/confidence-gated re-selection and learned relevance "
            "weighting (this cell tests fixed brain-faithful selection signals first); if HARD_FAIL, the "
            "redirect is deeper meaning/grounding for relevance, NOT a re-tuned surface gate."),
        "contract": "INLINE-LOCAL; no push/remote-persist; NOT remote-portable (GloVe+WorldTree git-ignored/large); VET-PENDING; FULL eval slice bounded (limit_easy=500 limit_chal=600) to fit one foreground call",
        "compute_architecture": "mixed CPU: batched GloVe encode + scipy.sparse batched PPR (2 passes, UNCHANGED) + per-question selection signals (cheap KxK coherence settle at K=100) + UNCHANGED combiner; wall target < 10min",
        "storage_strategy": "sharded (each fact = own embedding + own graph node; no superposition)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": "default_ok_for_this_regime (selection hyperparams author-set a priori; wide pool + combiner UNCHANGED; NOT tuned to force a win; random-select present as must-fail)",
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
